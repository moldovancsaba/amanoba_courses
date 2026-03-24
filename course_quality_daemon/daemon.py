from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import shutil
import signal
import sqlite3
import sys
import tempfile
import subprocess
import time
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .confidence import confidence_for_completion, confidence_for_validation
from .local_runtime import LocalRuntimeManager
from .validator import audit_lesson, validate_question


DEFAULT_FEED_LIMIT = 25
DONE_COLUMN_LIMIT = 10
FAILED_COLUMN_LIMIT = 10
ARCHIVED_COLUMN_LIMIT = 50


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_text(json.dumps(value, ensure_ascii=False, sort_keys=True))


def acquire_process_lock(lock_path: Path) -> int | None:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(fd)
        return None
    os.ftruncate(fd, 0)
    os.write(fd, str(os.getpid()).encode("utf-8"))
    return fd


def release_process_lock(fd: int | None) -> None:
    if fd is None:
        return
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def _normalize_lesson_payload(payload: dict[str, Any]) -> dict[str, str]:
    title = str(payload.get("title") or "").strip()
    content = str(payload.get("content") or "").strip()
    email_subject = str(payload.get("emailSubject") or title).strip()
    email_body = str(payload.get("emailBody") or "").strip()
    return {
        "title": title,
        "content": content,
        "emailSubject": email_subject,
        "emailBody": email_body,
    }


@dataclass
class Config:
    config_path: Path
    power_mode: str
    workspace_root: Path
    source_mode: str
    state_db_path: Path
    backups_dir: Path
    reports_dir: Path
    scan_interval_seconds: int
    scan_globs: list[str]
    ignore_dirs: set[str]
    apply_fixes: bool
    fix_questions: bool
    fix_lessons: bool
    max_attempts_per_task: int
    feed_limit: int
    queue_check_interval_seconds: int
    idle_sleep_seconds: int
    post_task_sleep_seconds: int
    action_feed_limit: int
    max_task_runtime_seconds: int
    quarantine_after_failures: int
    runtime_config: dict[str, Any]
    live_app_root: Path | None
    live_bridge_script: str | None
    live_actor: str
    live_batch_size: int
    live_batch_passes: int
    live_bridge_timeout_seconds: int
    dashboard_host: str
    dashboard_port: int

    @classmethod
    def from_file(cls, path: Path) -> "Config":
        raw = json.loads(path.read_text(encoding="utf-8"))
        root = path.parent.resolve()

        def resolve(value: str) -> Path:
            candidate = Path(value)
            return candidate if candidate.is_absolute() else (root / candidate).resolve()

        return cls(
            config_path=path.resolve(),
            power_mode=str(raw.get("power_mode") or "balanced"),
            workspace_root=resolve(raw["workspace_root"]),
            source_mode=str(raw.get("source_mode") or "files").strip().lower(),
            state_db_path=resolve(raw["state_db_path"]),
            backups_dir=resolve(raw["backups_dir"]),
            reports_dir=resolve(raw["reports_dir"]),
            scan_interval_seconds=int(raw.get("scan_interval_seconds", 300)),
            scan_globs=list(raw.get("scan_globs", ["**/*.json"])),
            ignore_dirs=set(raw.get("ignore_dirs", [".course-quality", "__pycache__"])),
            apply_fixes=bool(raw.get("apply_fixes", True)),
            fix_questions=bool(raw.get("fix_questions", True)),
            fix_lessons=bool(raw.get("fix_lessons", False)),
            max_attempts_per_task=int(raw.get("max_attempts_per_task", 5)),
            feed_limit=int(raw.get("feed_limit", DEFAULT_FEED_LIMIT)),
            queue_check_interval_seconds=int(raw.get("queue_check_interval_seconds", 300)),
            idle_sleep_seconds=int(raw.get("idle_sleep_seconds", 15)),
            post_task_sleep_seconds=int(raw.get("post_task_sleep_seconds", 20)),
            action_feed_limit=int(raw.get("action_feed_limit", 3)),
            max_task_runtime_seconds=int(raw.get("max_task_runtime_seconds", 900)),
            quarantine_after_failures=int((raw.get("watchdog") or {}).get("quarantine_after_failures") or 2),
            runtime_config=dict(raw.get("runtime") or {}),
            live_app_root=resolve(str(raw.get("live", {}).get("app_root"))) if raw.get("live", {}).get("app_root") else None,
            live_bridge_script=str(raw.get("live", {}).get("bridge_script") or "scripts/course-quality-live-bridge.ts"),
            live_actor=str(raw.get("live", {}).get("actor") or "course-quality-daemon"),
            live_batch_size=int(raw.get("live", {}).get("batch_size") or 25),
            live_batch_passes=int(raw.get("live", {}).get("batch_passes") or 8),
            live_bridge_timeout_seconds=int(raw.get("live", {}).get("bridge_timeout_seconds") or 120),
            dashboard_host=str(raw.get("dashboard", {}).get("host") or "127.0.0.1"),
            dashboard_port=int(raw.get("dashboard", {}).get("port") or 8765),
        )


class StateStore:
    def __init__(self, db_path: Path) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
        self.reset_running_tasks()

    def _init_schema(self) -> None:
        with self._lock:
            self.conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS packages (
                    path TEXT PRIMARY KEY,
                    fingerprint TEXT NOT NULL,
                    course_id TEXT,
                    language TEXT,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS tasks (
                    task_key TEXT PRIMARY KEY,
                    kind TEXT NOT NULL,
                    package_path TEXT NOT NULL,
                    course_id TEXT,
                    language TEXT,
                    lesson_id TEXT,
                    question_uuid TEXT,
                    question_index INTEGER,
                    source_hash TEXT NOT NULL,
                    status TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    last_error TEXT,
                    details_json TEXT,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    finished_at TEXT,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS task_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_key TEXT NOT NULL,
                    comment TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            pragma_rows = self.conn.execute("PRAGMA table_info(tasks)").fetchall()
            columns = {str(row["name"] if isinstance(row, sqlite3.Row) else row[1]) for row in pragma_rows}
            for name in ["created_at", "started_at", "finished_at"]:
                if name not in columns:
                    self.conn.execute(f"ALTER TABLE tasks ADD COLUMN {name} TEXT")
            self.conn.execute("UPDATE tasks SET created_at = COALESCE(created_at, updated_at) WHERE created_at IS NULL")
            self.conn.commit()

    def reset_running_tasks(self) -> None:
        with self._lock:
            self.conn.execute(
                "UPDATE tasks SET status='pending', started_at=NULL, updated_at=? WHERE status='running'",
                (utc_now(),),
            )
            self.conn.commit()

    def recover_stale_running_tasks(self, max_runtime_seconds: int, max_attempts: int) -> int:
        if max_runtime_seconds <= 0:
            return 0
        with self._lock:
            rows = self.conn.execute(
                "SELECT task_key, attempts, started_at, details_json FROM tasks WHERE status='running' AND started_at IS NOT NULL"
            ).fetchall()
            now_dt = datetime.now(timezone.utc)
            recovered = 0
            for row in rows:
                started_at = str(row["started_at"] or "").strip()
                if not started_at:
                    continue
                try:
                    started_dt = datetime.fromisoformat(started_at)
                except ValueError:
                    continue
                runtime_seconds = int((now_dt - started_dt).total_seconds())
                if runtime_seconds < max_runtime_seconds:
                    continue
                attempts = int(row["attempts"] or 0) + 1
                next_status = "failed" if attempts >= max_attempts else "pending"
                details: dict[str, Any] = {}
                if row["details_json"]:
                    try:
                        details = json.loads(row["details_json"])
                    except json.JSONDecodeError:
                        details = {"raw": row["details_json"]}
                recoveries = list(details.get("recoveries") or [])
                recoveries.append(
                    {
                        "type": "stale-running-timeout",
                        "runtimeSeconds": runtime_seconds,
                        "recoveredAt": utc_now(),
                    }
                )
                details["recoveries"] = recoveries[-20:]
                now = utc_now()
                self.conn.execute(
                    """
                    UPDATE tasks
                    SET status=?,
                        attempts=?,
                        last_error=?,
                        details_json=?,
                        started_at=NULL,
                        finished_at=?,
                        updated_at=?
                    WHERE task_key=?
                    """,
                    (
                        next_status,
                        attempts,
                        f"Recovered stale running task after {runtime_seconds} seconds.",
                        json.dumps(details, ensure_ascii=False),
                        now if next_status == "failed" else None,
                        now,
                        row["task_key"],
                    ),
                )
                recovered += 1
            self.conn.commit()
            return recovered

    def save_package(self, path: str, fingerprint: str, course_id: str, language: str) -> None:
        with self._lock:
            self.conn.execute(
                """
                INSERT INTO packages(path, fingerprint, course_id, language, updated_at)
                VALUES(?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    fingerprint=excluded.fingerprint,
                    course_id=excluded.course_id,
                    language=excluded.language,
                    updated_at=excluded.updated_at
                """,
                (path, fingerprint, course_id, language, utc_now()),
            )
            self.conn.commit()

    def upsert_task(
        self,
        task_key: str,
        kind: str,
        package_path: str,
        course_id: str,
        language: str,
        lesson_id: str,
        question_uuid: str | None,
        question_index: int | None,
        source_hash: str,
        details: dict[str, Any],
    ) -> None:
        with self._lock:
            existing = self.conn.execute(
                "SELECT source_hash, status, created_at, attempts, started_at, finished_at, last_error, updated_at FROM tasks WHERE task_key=?",
                (task_key,),
            ).fetchone()
            created_at = existing["created_at"] if existing and existing["created_at"] else utc_now()
            unchanged = bool(existing and existing["source_hash"] == source_hash)
            if unchanged and existing["status"] in {"completed", "failed", "running", "pending"}:
                next_status = str(existing["status"])
            elif existing and existing["status"] == "running":
                next_status = "running"
            else:
                next_status = "pending"
            attempts = int(existing["attempts"]) if existing and unchanged else 0
            started_at = existing["started_at"] if existing and next_status == "running" else None
            finished_at = existing["finished_at"] if existing and next_status in {"completed", "failed"} else None
            last_error = existing["last_error"] if existing and unchanged and existing["last_error"] else None
            updated_at = existing["updated_at"] if existing and unchanged and existing["updated_at"] else utc_now()
            self.conn.execute(
                """
                INSERT INTO tasks(
                    task_key, kind, package_path, course_id, language, lesson_id, question_uuid,
                    question_index, source_hash, status, attempts, last_error, details_json,
                    created_at, started_at, finished_at, updated_at
                ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(task_key) DO UPDATE SET
                    package_path=excluded.package_path,
                    course_id=excluded.course_id,
                    language=excluded.language,
                    lesson_id=excluded.lesson_id,
                    question_uuid=excluded.question_uuid,
                    question_index=excluded.question_index,
                    source_hash=excluded.source_hash,
                    status=CASE
                        WHEN tasks.source_hash = excluded.source_hash AND tasks.status IN ('completed', 'failed', 'running', 'pending') THEN tasks.status
                        WHEN tasks.status = 'running' THEN 'running'
                        ELSE 'pending'
                    END,
                    attempts=CASE
                        WHEN tasks.source_hash = excluded.source_hash THEN tasks.attempts
                        WHEN tasks.status = 'running' THEN tasks.attempts
                        ELSE 0
                    END,
                    last_error=CASE
                        WHEN tasks.source_hash = excluded.source_hash THEN tasks.last_error
                        ELSE NULL
                    END,
                    details_json=excluded.details_json,
                    created_at=COALESCE(tasks.created_at, excluded.created_at),
                    started_at=CASE
                        WHEN tasks.source_hash = excluded.source_hash AND tasks.status = 'running' THEN tasks.started_at
                        WHEN tasks.status = 'running' THEN tasks.started_at
                        ELSE NULL
                    END,
                    finished_at=CASE
                        WHEN tasks.source_hash = excluded.source_hash AND tasks.status IN ('completed', 'failed') THEN tasks.finished_at
                        ELSE NULL
                    END,
                    updated_at=CASE
                        WHEN tasks.source_hash = excluded.source_hash THEN tasks.updated_at
                        ELSE excluded.updated_at
                    END
                """,
                (
                    task_key,
                    kind,
                    package_path,
                    course_id,
                    language,
                    lesson_id,
                    question_uuid,
                    question_index,
                    source_hash,
                    next_status,
                    attempts,
                    last_error,
                    json.dumps(details, ensure_ascii=False),
                    created_at,
                    started_at,
                    finished_at,
                    updated_at,
                ),
            )
            self.conn.commit()

    def claim_next_task(self, max_attempts: int) -> sqlite3.Row | None:
        with self._lock:
            now = utc_now()
            self.conn.execute("BEGIN IMMEDIATE")
            try:
                running = self.conn.execute("SELECT 1 FROM tasks WHERE status='running' LIMIT 1").fetchone()
                if running is not None:
                    self.conn.commit()
                    return None
                task = self.conn.execute(
                    "SELECT task_key FROM tasks WHERE status='pending' AND attempts < ? ORDER BY attempts ASC, updated_at ASC, created_at ASC LIMIT 1",
                    (max_attempts,),
                ).fetchone()
                if task is None:
                    self.conn.commit()
                    return None
                cursor = self.conn.execute(
                    "UPDATE tasks SET status='running', started_at=?, updated_at=? WHERE task_key=? AND status='pending'",
                    (now, now, task["task_key"]),
                )
                if cursor.rowcount <= 0:
                    self.conn.commit()
                    return None
                row = self.conn.execute("SELECT * FROM tasks WHERE task_key=?", (task["task_key"],)).fetchone()
                self.conn.commit()
                return row
            except Exception:
                self.conn.rollback()
                raise

    def mark_running(self, task_key: str) -> sqlite3.Row | None:
        with self._lock:
            now = utc_now()
            self.conn.execute(
                "UPDATE tasks SET status='running', started_at=?, updated_at=? WHERE task_key=?",
                (now, now, task_key),
            )
            self.conn.commit()
            return self.conn.execute("SELECT * FROM tasks WHERE task_key=?", (task_key,)).fetchone()

    def mark_completed(self, task_key: str, details: dict[str, Any]) -> None:
        with self._lock:
            now = utc_now()
            self.conn.execute(
                "UPDATE tasks SET status='completed', details_json=?, finished_at=?, last_error=NULL, updated_at=? WHERE task_key=?",
                (json.dumps(details, ensure_ascii=False), now, now, task_key),
            )
            self.conn.commit()

    def mark_failed(self, task_key: str, attempts: int, max_attempts: int, error: str, details: dict[str, Any]) -> None:
        with self._lock:
            now = utc_now()
            status = "failed" if attempts >= max_attempts else "pending"
            existing = self.conn.execute("SELECT details_json FROM tasks WHERE task_key=?", (task_key,)).fetchone()
            merged_details: dict[str, Any] = {}
            if existing and existing["details_json"]:
                try:
                    loaded = json.loads(existing["details_json"])
                    if isinstance(loaded, dict):
                        merged_details.update(loaded)
                except json.JSONDecodeError:
                    pass
            merged_details.update(details)
            self.conn.execute(
                "UPDATE tasks SET status=?, attempts=?, last_error=?, details_json=?, started_at=NULL, finished_at=?, updated_at=? WHERE task_key=?",
                (status, attempts, error, json.dumps(merged_details, ensure_ascii=False), now if status == "failed" else None, now, task_key),
            )
            self.conn.commit()

    def mark_failed_with_policy(
        self,
        task_key: str,
        attempts: int,
        max_attempts: int,
        error: str,
        details: dict[str, Any],
        quarantine_after_failures: int,
    ) -> str:
        with self._lock:
            now = utc_now()
            if attempts >= max_attempts:
                status = "failed"
            elif quarantine_after_failures > 0 and attempts >= quarantine_after_failures:
                status = "quarantined"
            else:
                status = "pending"
            existing = self.conn.execute("SELECT details_json FROM tasks WHERE task_key=?", (task_key,)).fetchone()
            merged_details: dict[str, Any] = {}
            if existing and existing["details_json"]:
                try:
                    loaded = json.loads(existing["details_json"])
                    if isinstance(loaded, dict):
                        merged_details.update(loaded)
                except json.JSONDecodeError:
                    pass
            merged_details.update(details)
            if status == "quarantined":
                merged_details["humanActionRequired"] = True
                merged_details["quarantine"] = {
                    "status": "active",
                    "reason": error,
                    "quarantinedAt": now,
                    "attempts": attempts,
                }
            self.conn.execute(
                "UPDATE tasks SET status=?, attempts=?, last_error=?, details_json=?, started_at=NULL, finished_at=?, updated_at=? WHERE task_key=?",
                (status, attempts, error, json.dumps(merged_details, ensure_ascii=False), now if status in {"failed", "quarantined"} else None, now, task_key),
            )
            self.conn.commit()
            return status

    def clear_pending_tasks(self, package_path: str | None = None) -> int:
        with self._lock:
            if package_path:
                cursor = self.conn.execute(
                    """
                    DELETE FROM tasks
                    WHERE status='pending'
                      AND package_path=?
                      AND COALESCE(attempts, 0) = 0
                      AND last_error IS NULL
                    """,
                    (package_path,),
                )
            else:
                cursor = self.conn.execute(
                    """
                    DELETE FROM tasks
                    WHERE status='pending'
                      AND COALESCE(attempts, 0) = 0
                      AND last_error IS NULL
                    """
                )
            self.conn.commit()
            return int(cursor.rowcount or 0)

    def counts(self) -> dict[str, int]:
        with self._lock:
            rows = self.conn.execute("SELECT status, COUNT(*) AS count FROM tasks GROUP BY status").fetchall()
            return {row["status"]: int(row["count"]) for row in rows}

    def feed_snapshot(self, limit: int) -> dict[str, Any]:
        completed_count = self.count_by_status("completed")
        failed_rows = self._query_failed_column_rows(FAILED_COLUMN_LIMIT)
        return {
            "generatedAt": utc_now(),
            "counts": self.counts(),
            "queued": [self._row_to_summary(row) for row in self._query_tasks("pending", "updated_at ASC", limit)],
            "running": [self._row_to_summary(row) for row in self._query_tasks("running", "started_at ASC", limit)],
            "completed": [self._row_to_summary(row) for row in self._query_tasks("completed", "finished_at DESC", DONE_COLUMN_LIMIT)],
            "failed": [self._row_to_summary(row) for row in failed_rows],
            "failedCount": len(failed_rows),
            "archived": [self._row_to_summary(row) for row in self._query_tasks_offset("completed", "finished_at DESC", ARCHIVED_COLUMN_LIMIT, DONE_COLUMN_LIMIT)],
            "archivedCount": max(0, completed_count - DONE_COLUMN_LIMIT),
        }

    def count_by_status(self, status: str) -> int:
        with self._lock:
            row = self.conn.execute("SELECT COUNT(*) AS count FROM tasks WHERE status=?", (status,)).fetchone()
            return int(row["count"]) if row else 0

    def _query_tasks(self, status: str, order_by: str, limit: int) -> list[sqlite3.Row]:
        query = f"SELECT * FROM tasks WHERE status=? ORDER BY {order_by} LIMIT ?"
        with self._lock:
            return self.conn.execute(query, (status, limit)).fetchall()

    def _query_failed_column_rows(self, limit: int) -> list[sqlite3.Row]:
        with self._lock:
            return self.conn.execute(
                """
                SELECT *
                FROM tasks
                WHERE status='failed'
                   OR status='quarantined'
                   OR (status='pending' AND last_error IS NOT NULL)
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

    def _query_tasks_offset(self, status: str, order_by: str, limit: int, offset: int) -> list[sqlite3.Row]:
        query = f"SELECT * FROM tasks WHERE status=? ORDER BY {order_by} LIMIT ? OFFSET ?"
        with self._lock:
            return self.conn.execute(query, (status, limit, offset)).fetchall()

    def _row_to_summary(self, row: sqlite3.Row) -> dict[str, Any]:
        details: dict[str, Any] = {}
        if row["details_json"]:
            try:
                details = json.loads(row["details_json"])
            except json.JSONDecodeError:
                details = {"raw": row["details_json"]}
        return {
            "taskKey": row["task_key"],
            "kind": row["kind"],
            "courseId": row["course_id"],
            "language": row["language"],
            "lessonId": row["lesson_id"],
            "questionUuid": row["question_uuid"],
            "questionIndex": row["question_index"],
            "packagePath": row["package_path"],
            "status": row["status"],
            "displayStatus": (
                "retry-failed"
                if row["status"] == "pending" and row["last_error"]
                else ("quarantined" if row["status"] == "quarantined" else row["status"])
            ),
            "attempts": row["attempts"],
            "lastError": row["last_error"],
            "createdAt": row["created_at"],
            "startedAt": row["started_at"],
            "finishedAt": row["finished_at"],
            "updatedAt": row["updated_at"],
            "details": details,
        }

    def task_detail(self, task_key: str) -> dict[str, Any] | None:
        with self._lock:
            row = self.conn.execute("SELECT * FROM tasks WHERE task_key=?", (task_key,)).fetchone()
            if row is None:
                return None
            feedback_rows = self.conn.execute(
                "SELECT comment, created_at FROM task_feedback WHERE task_key=? ORDER BY created_at DESC",
                (task_key,),
            ).fetchall()
        summary = self._row_to_summary(row)
        summary["feedback"] = [{"comment": item["comment"], "createdAt": item["created_at"]} for item in feedback_rows]
        return summary

    def feedback_comments(self, task_key: str) -> list[str]:
        with self._lock:
            rows = self.conn.execute(
                "SELECT comment FROM task_feedback WHERE task_key=? ORDER BY created_at ASC",
                (task_key,),
            ).fetchall()
        return [str(row["comment"]) for row in rows]

    def add_feedback_comment(self, task_key: str, comment: str) -> None:
        clean = comment.strip()
        if not clean:
            return
        with self._lock:
            self.conn.execute(
                "INSERT INTO task_feedback(task_key, comment, created_at) VALUES(?, ?, ?)",
                (task_key, clean, utc_now()),
            )
            self.conn.commit()

    def quarantine_repeated_failures(self, threshold: int) -> list[str]:
        if threshold <= 0:
            return []
        with self._lock:
            rows = self.conn.execute(
                """
                SELECT task_key, attempts, last_error, details_json
                FROM tasks
                WHERE status='pending'
                  AND last_error IS NOT NULL
                  AND attempts >= ?
                """,
                (threshold,),
            ).fetchall()
            now = utc_now()
            updated: list[str] = []
            for row in rows:
                details: dict[str, Any] = {}
                if row["details_json"]:
                    try:
                        loaded = json.loads(row["details_json"])
                        if isinstance(loaded, dict):
                            details = loaded
                    except json.JSONDecodeError:
                        details = {}
                details["humanActionRequired"] = True
                details["quarantine"] = {
                    "status": "active",
                    "reason": str(row["last_error"] or ""),
                    "quarantinedAt": now,
                    "attempts": int(row["attempts"] or 0),
                }
                self.conn.execute(
                    """
                    UPDATE tasks
                    SET status='quarantined',
                        details_json=?,
                        finished_at=COALESCE(finished_at, ?),
                        updated_at=?
                    WHERE task_key=?
                    """,
                    (json.dumps(details, ensure_ascii=False), now, now, row["task_key"]),
                )
                updated.append(str(row["task_key"]))
            self.conn.commit()
            return updated

    def search_completed(self, query: str, limit: int = ARCHIVED_COLUMN_LIMIT) -> list[dict[str, Any]]:
        q = f"%{query.strip()}%"
        with self._lock:
            rows = self.conn.execute(
                """
                SELECT * FROM tasks
                WHERE status='completed'
                  AND (
                    task_key LIKE ?
                    OR course_id LIKE ?
                    OR language LIKE ?
                    OR lesson_id LIKE ?
                    OR question_uuid LIKE ?
                    OR package_path LIKE ?
                    OR details_json LIKE ?
                  )
                ORDER BY finished_at DESC
                LIMIT ?
                """,
                (q, q, q, q, q, q, q, limit),
            ).fetchall()
        return [self._row_to_summary(row) for row in rows]

    def challenge_task(self, task_key: str, comment: str) -> dict[str, Any] | None:
        clean = comment.strip()
        if not clean:
            raise ValueError("Challenge comment is required.")
        with self._lock:
            row = self.conn.execute("SELECT * FROM tasks WHERE task_key=?", (task_key,)).fetchone()
            if row is None:
                return None
            now = utc_now()
            self.conn.execute(
                "INSERT INTO task_feedback(task_key, comment, created_at) VALUES(?, ?, ?)",
                (task_key, clean, now),
            )
            details = {}
            if row["details_json"]:
                try:
                    details = json.loads(row["details_json"])
                except json.JSONDecodeError:
                    details = {"raw": row["details_json"]}
            history = list(details.get("challengeHistory") or [])
            history.append({"comment": clean, "createdAt": now})
            details["challengeHistory"] = history[-20:]
            self.conn.execute(
                """
                UPDATE tasks
                SET status='pending',
                    attempts=0,
                    last_error=NULL,
                    started_at=NULL,
                    finished_at=NULL,
                    details_json=?,
                    updated_at=?
                WHERE task_key=?
                """,
                (json.dumps(details, ensure_ascii=False), now, task_key),
            )
            self.conn.commit()
        return self.task_detail(task_key)


class AmanobaLiveBridge:
    def __init__(self, app_root: Path, script_path: str, actor: str, timeout_seconds: int) -> None:
        self.app_root = app_root
        self.script_path = script_path
        self.actor = actor
        self.timeout_seconds = max(1, int(timeout_seconds))

    def scan(self) -> dict[str, Any]:
        return self._run(["scan"])

    def next_batch(self, limit: int) -> dict[str, Any]:
        return self._run(["next-batch", "--limit", str(limit)])

    def fetch(self, task_key: str) -> dict[str, Any]:
        return self._run(["fetch", "--task-key", task_key])

    def apply(self, task_key: str, payload: dict[str, Any]) -> dict[str, Any]:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            temp_path = handle.name
        try:
            return self._run(["apply", "--task-key", task_key, "--payload-file", temp_path, "--actor", self.actor])
        finally:
            try:
                os.unlink(temp_path)
            except OSError:
                pass

    def mark_reviewed(self, task_key: str, result: str = "valid") -> dict[str, Any]:
        return self._run(["mark-reviewed", "--task-key", task_key, "--actor", self.actor, "--result", result])

    def _run(self, args: list[str]) -> dict[str, Any]:
        tsx_path = self.app_root / "node_modules" / ".bin" / "tsx"
        if not tsx_path.exists():
            raise RuntimeError(f"tsx not found in app workspace: {tsx_path}")
        script = self.app_root / self.script_path
        if not script.exists():
            raise RuntimeError(f"Live bridge script not found: {script}")
        try:
            result = subprocess.run(
                [str(tsx_path), "--env-file=.env.local", str(script), *args],
                cwd=str(self.app_root),
                capture_output=True,
                text=True,
                check=False,
                timeout=self.timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                f"Live bridge command timed out after {self.timeout_seconds} seconds: {' '.join(args)}"
            ) from exc
        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            stdout = (result.stdout or "").strip()
            detail = stderr or stdout or f"exit code {result.returncode}"
            raise RuntimeError(f"Live bridge command failed: {detail}")
        output = (result.stdout or "").strip()
        if not output:
            return {}
        return json.loads(output)


class CourseQualityDaemon:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.state = StateStore(config.state_db_path)
        self.runtime = LocalRuntimeManager(config.runtime_config)
        self.live_bridge = (
            AmanobaLiveBridge(
                config.live_app_root,
                config.live_bridge_script or "scripts/course-quality-live-bridge.ts",
                config.live_actor,
                config.live_bridge_timeout_seconds,
            )
            if config.source_mode == "amanoba_live_db" and config.live_app_root is not None
            else None
        )
        self._process_lock = threading.Lock()
        self.config.backups_dir.mkdir(parents=True, exist_ok=True)
        self.config.reports_dir.mkdir(parents=True, exist_ok=True)

    def scan(self) -> dict[str, int]:
        if self.config.source_mode == "amanoba_live_db":
            return self._scan_live()
        package_count = 0
        task_count = 0
        for path in self._iter_candidate_files():
            package = self._load_package(path)
            if package is None:
                continue
            package_count += 1
            task_count += self._enqueue_tasks(path, package)
        self._write_reports()
        return {"packages": package_count, "tasks": task_count}

    def _scan_live(self) -> dict[str, int]:
        if self.live_bridge is None:
            raise RuntimeError("Live DB mode is enabled but the live bridge is not configured.")
        pending_path = str(self.config.live_app_root or self.config.workspace_root)
        self.state.clear_pending_tasks(pending_path)
        payload = self.live_bridge.next_batch(self.config.live_batch_size)
        candidates = payload.get("candidates") or []
        created = 0
        reviewed_valid = 0
        for candidate in candidates:
            kind = str(candidate.get("kind") or "").strip().lower()
            if kind == "lesson":
                lesson = candidate.get("lesson") or {}
                lesson_payload = {
                    "title": lesson.get("title"),
                    "content": lesson.get("content"),
                    "emailSubject": lesson.get("emailSubject"),
                    "emailBody": lesson.get("emailBody"),
                }
                audit = audit_lesson(lesson_payload)
                task_key = f"lesson::{lesson['objectId']}"
                if audit.is_valid:
                    self.live_bridge.mark_reviewed(task_key, result="already-valid")
                    reviewed_valid += 1
                    continue
                created += 1
                human_course = str(lesson.get("courseName") or lesson.get("courseId") or "Unknown course")
                human_day = f"Day {lesson.get('dayNumber')}" if lesson.get("dayNumber") not in (None, "") else str(lesson.get("lessonId") or "-")
                self.state.upsert_task(
                    task_key=task_key,
                    kind="lesson",
                    package_path=pending_path,
                    course_id=str(lesson.get("courseId") or ""),
                    language=str(lesson.get("language") or ""),
                    lesson_id=str(lesson.get("lessonId") or ""),
                    question_uuid=None,
                    question_index=None,
                    source_hash=sha256_json({"lesson": lesson_payload}),
                    details={
                        "errors": audit.errors,
                        "warnings": audit.warnings,
                        "before": lesson_payload,
                        "displayTitle": str(lesson.get("title") or lesson.get("lessonId") or task_key),
                        "humanCourseName": human_course,
                        "humanDayLabel": human_day,
                        "humanLessonTitle": str(lesson.get("title") or lesson.get("lessonId") or "-"),
                        "judgement": confidence_for_validation("lesson", audit.errors, audit.warnings),
                    },
                )
                continue

            question = candidate.get("question") or {}
            question_payload = {
                "uuid": question.get("uuid"),
                "question": question.get("question"),
                "options": question.get("options") or [],
                "correctIndex": question.get("correctIndex"),
                "questionType": question.get("questionType"),
                "difficulty": question.get("difficulty"),
                "category": question.get("category"),
                "hashtags": question.get("hashtags") or [],
                "isActive": True,
            }
            validation = validate_question(question_payload)
            task_key = f"question::{question['objectId']}"
            if validation.is_valid:
                self.live_bridge.mark_reviewed(task_key, result="already-valid")
                reviewed_valid += 1
                continue
            created += 1
            human_course = str(question.get("courseName") or question.get("courseId") or "Unknown course")
            human_day = f"Day {question.get('dayNumber')}" if question.get("dayNumber") not in (None, "") else str(question.get("lessonId") or "-")
            self.state.upsert_task(
                task_key=task_key,
                kind="question",
                package_path=pending_path,
                course_id=str(question.get("courseId") or ""),
                language=str(question.get("language") or ""),
                lesson_id=str(question.get("lessonId") or ""),
                question_uuid=str(question.get("uuid") or question.get("objectId") or ""),
                question_index=None,
                source_hash=sha256_json({"question": question_payload}),
                details={
                    "errors": validation.errors,
                    "warnings": validation.warnings,
                    "before": question_payload,
                    "displayTitle": str(question.get("question") or question.get("uuid") or task_key),
                    "humanCourseName": human_course,
                    "humanDayLabel": human_day,
                    "humanLessonTitle": str(question.get("lessonTitle") or question.get("lessonId") or "-"),
                    "judgement": confidence_for_validation("question", validation.errors, validation.warnings),
                },
            )
        self._write_reports()
        return {
            "packages": int((payload.get("counts") or {}).get("courses") or 0),
            "tasks": created,
            "reviewedValid": reviewed_valid,
            "batchSize": len(candidates),
        }

    def process_one(self) -> str:
        with self._process_lock:
            task = self.state.claim_next_task(self.config.max_attempts_per_task)
            if task is None and self.config.source_mode == "amanoba_live_db":
                for _ in range(max(1, self.config.live_batch_passes)):
                    scan_result = self._scan_live()
                    task = self.state.claim_next_task(self.config.max_attempts_per_task)
                    if task is not None:
                        break
                    if int(scan_result.get("batchSize") or 0) <= 0:
                        break
            if task is None:
                self._write_reports()
                return "idle"
            self._write_reports()
            try:
                result = self._process_task_with_timeout(task)
                self.state.mark_completed(task["task_key"], result)
                self._write_reports()
                return task["task_key"]
            except Exception as exc:
                attempts = int(task["attempts"]) + 1
                existing_details: dict[str, Any] = {}
                if task["details_json"]:
                    try:
                        loaded = json.loads(task["details_json"])
                        if isinstance(loaded, dict):
                            existing_details = loaded
                    except json.JSONDecodeError:
                        existing_details = {}
                incident = self._build_failure_incident(task, exc, attempts, existing_details)
                next_status = self.state.mark_failed_with_policy(
                    task["task_key"],
                    attempts=attempts,
                    max_attempts=self.config.max_attempts_per_task,
                    error=str(exc),
                    quarantine_after_failures=self.config.quarantine_after_failures,
                    details=incident,
                )
                self._record_system_feedback(task["task_key"], incident, next_status)
                self._write_reports()
                return f"failed:{task['task_key']}"

    def _build_failure_incident(
        self,
        task: sqlite3.Row,
        exc: Exception,
        attempts: int,
        existing_details: dict[str, Any],
    ) -> dict[str, Any]:
        error = str(exc).strip()
        classification = self._classify_failure(error)
        history = list(existing_details.get("failureHistory") or [])
        event = {
            "at": utc_now(),
            "error": error,
            "attempt": attempts,
            "type": classification["type"],
            "component": classification["component"],
            "playbook": classification["playbook"],
        }
        watchdog_report = None
        if classification["type"] in {"timeout", "live-bridge-timeout"}:
            watchdog_report = self._run_watchdog_incident(
                {
                    "type": classification["type"],
                    "taskKey": str(task["task_key"]),
                    "kind": str(task["kind"]),
                    "attempt": attempts,
                    "error": error,
                    "component": classification["component"],
                }
            )
            if watchdog_report:
                event["watchdog"] = {
                    "generatedAt": watchdog_report.get("generatedAt"),
                    "actions": watchdog_report.get("actions") or [],
                    "dashboardHealthy": watchdog_report.get("dashboardHealthy"),
                    "ollamaHealthy": watchdog_report.get("ollamaHealthy"),
                }
        history.append(event)
        details = dict(existing_details)
        details.update(
            {
                "error": error,
                "attempts": attempts,
                "failureHistory": history[-20:],
                "rca": {
                    "type": classification["type"],
                    "component": classification["component"],
                    "summary": classification["summary"],
                    "playbook": classification["playbook"],
                    "lastUpdatedAt": utc_now(),
                },
            }
        )
        if watchdog_report:
            details["lastWatchdogIncident"] = watchdog_report
        return details

    def _classify_failure(self, error: str) -> dict[str, Any]:
        message = error.strip()
        lower = message.lower()
        if "timed out" in lower and "live bridge" in lower:
            return {
                "type": "live-bridge-timeout",
                "component": "live-bridge",
                "summary": "The live Amanoba bridge exceeded its response window.",
                "playbook": [
                    "Run the watchdog incident cycle immediately.",
                    "Check dashboard, worker, and Ollama health.",
                    "Restart the affected component if unhealthy.",
                    "Kick the worker again only after the queue is healthy.",
                ],
            }
        if "timed out" in lower:
            return {
                "type": "timeout",
                "component": "worker",
                "summary": "The task exceeded the allowed processing time.",
                "playbook": [
                    "Run the watchdog incident cycle immediately.",
                    "Kill stale worker processes and clear stale locks.",
                    "Verify dashboard and provider health.",
                    "Restart only the unhealthy service, or the full stack if recovery fails.",
                ],
            }
        if "did not return json" in lower:
            return {
                "type": "provider-json",
                "component": "runtime-provider",
                "summary": "The rewrite provider returned an invalid payload shape.",
                "playbook": [
                    "Preserve the card in Failed for review.",
                    "Retry once through the normal queue.",
                    "Quarantine after repeated bounces for human review.",
                ],
            }
        if "still failed validation" in lower:
            return {
                "type": "validation-regression",
                "component": "validator",
                "summary": "The rewritten content still failed Amanoba validation rules.",
                "playbook": [
                    "Keep the card visible in Failed.",
                    "Retry once with the accumulated history and human feedback.",
                    "Quarantine after repeated bounces for human review.",
                ],
            }
        return {
            "type": "unknown",
            "component": "worker",
            "summary": "The task failed with an uncategorized worker error.",
            "playbook": [
                "Record the error and keep the card visible.",
                "Retry once through the queue.",
                "Quarantine after repeated bounces for human review.",
            ],
        }

    def _run_watchdog_incident(self, incident: dict[str, Any]) -> dict[str, Any] | None:
        try:
            from .watchdog import CourseQualityWatchdog

            return CourseQualityWatchdog(self.config).run_once(incident=incident)
        except Exception as exc:
            return {
                "generatedAt": utc_now(),
                "incident": incident,
                "actions": [],
                "error": f"Watchdog incident handling failed: {exc}",
            }

    def _record_system_feedback(self, task_key: str, incident: dict[str, Any], next_status: str) -> None:
        rca = dict(incident.get("rca") or {})
        summary = str(rca.get("summary") or "Task failure recorded.").strip()
        playbook = ", ".join(str(item) for item in (rca.get("playbook") or []))
        if next_status == "quarantined":
            self.state.add_feedback_comment(
                task_key,
                f"[system] Quarantined after repeated bounce-backs. RCA: {summary} Proven recovery: {playbook}",
            )
            return
        if rca.get("type") in {"timeout", "live-bridge-timeout"}:
            self.state.add_feedback_comment(
                task_key,
                f"[system] Timeout RCA captured. Watchdog incident run triggered. Proven recovery: {playbook}",
            )

    def _process_task_with_timeout(self, task: sqlite3.Row) -> dict[str, Any]:
        timeout_seconds = max(1, int(self.config.max_task_runtime_seconds))
        try:
            is_main_thread = threading.current_thread() is threading.main_thread()
        except Exception:
            is_main_thread = False
        if not is_main_thread or not hasattr(signal, "SIGALRM"):
            return self._process_task(task)

        class _TaskTimeout(Exception):
            pass

        def _handler(signum: int, frame: Any) -> None:
            raise _TaskTimeout()

        previous = signal.getsignal(signal.SIGALRM)
        signal.signal(signal.SIGALRM, _handler)
        signal.alarm(timeout_seconds)
        try:
            return self._process_task(task)
        except _TaskTimeout as exc:
            raise RuntimeError(f"Task timed out after {timeout_seconds} seconds.") from exc
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, previous)

    def trigger_processing(self, max_items: int = 1) -> dict[str, Any]:
        target = max(1, int(max_items))
        if self.state.counts().get("running", 0) > 0:
            return {
                "accepted": False,
                "reason": "system-busy",
                "summary": self.action_snapshot(),
            }
        cmd = [
            sys.executable,
            "-m",
            "course_quality_daemon",
            "--config",
            str(self.config.config_path),
            "run-once",
            "--max-items",
            str(target),
        ]
        with open(os.devnull, "wb") as sink:
            subprocess.Popen(
                cmd,
                cwd=str(self.config.workspace_root),
                stdout=sink,
                stderr=sink,
                start_new_session=True,
            )
        return {
            "accepted": True,
            "scheduledItems": target,
            "summary": self.action_snapshot(),
        }

    def action_snapshot(self) -> dict[str, Any]:
        feed = self.feed_snapshot(limit=self.config.action_feed_limit)
        return {
            "generatedAt": feed["generatedAt"],
            "counts": feed["counts"],
            "queued": feed["queued"],
            "running": feed["running"],
            "completed": feed["completed"],
            "failed": feed["failed"],
        }

    def power_profiles(self) -> dict[str, dict[str, int | float]]:
        return {
            "gentle": {"temperature": 0.1, "num_predict": 256, "num_ctx": 1536, "num_thread": 1},
            "balanced": {"temperature": 0.1, "num_predict": 384, "num_ctx": 2048, "num_thread": 2},
            "fast": {"temperature": 0.15, "num_predict": 512, "num_ctx": 3072, "num_thread": 4},
        }

    def current_power_mode(self) -> str:
        if self.config.power_mode in self.power_profiles():
            return self.config.power_mode
        ollama = dict(self.config.runtime_config.get("ollama") or {})
        active = {
            "temperature": float(ollama.get("temperature") or 0.1),
            "num_predict": int(ollama.get("num_predict") or 384),
            "num_ctx": int(ollama.get("num_ctx") or 2048),
            "num_thread": int(ollama.get("num_thread") or 2),
        }
        for name, profile in self.power_profiles().items():
            if active == profile:
                return name
        return "custom"

    def set_power_mode(self, mode: str) -> dict[str, Any]:
        profiles = self.power_profiles()
        if mode not in profiles:
            raise ValueError(f"Unsupported power mode: {mode}")
        raw = json.loads(self.config.config_path.read_text(encoding="utf-8"))
        runtime = dict(raw.get("runtime") or {})
        ollama = dict(runtime.get("ollama") or {})
        ollama.update(profiles[mode])
        runtime["ollama"] = ollama
        raw["runtime"] = runtime
        raw["power_mode"] = mode
        temp_path = self.config.config_path.with_suffix(self.config.config_path.suffix + ".tmp")
        temp_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temp_path.replace(self.config.config_path)
        self.config.power_mode = mode
        self.config.runtime_config = runtime
        self.runtime = LocalRuntimeManager(self.config.runtime_config)
        self._restart_launch_agent("com.amanoba.coursequality.worker")
        return {
            "mode": mode,
            "profile": profiles[mode],
            "summary": self.action_snapshot(),
        }

    def _restart_launch_agent(self, label: str) -> None:
        uid = str(os.getuid())
        try:
            subprocess.run(["launchctl", "kickstart", "-k", f"gui/{uid}/{label}"], check=False, capture_output=True)
        except Exception:
            return

    def run_daemon(self) -> None:
        next_scan_at = 0.0
        while True:
            now = time.time()
            if now >= next_scan_at:
                self.scan()
                next_scan_at = now + self.config.scan_interval_seconds
            self.state.recover_stale_running_tasks(
                max_runtime_seconds=self.config.max_task_runtime_seconds,
                max_attempts=self.config.max_attempts_per_task,
            )
            if self.state.counts().get("running", 0) <= 0:
                self.process_one()
            time.sleep(self.config.queue_check_interval_seconds)

    def feed_snapshot(self, limit: int | None = None) -> dict[str, Any]:
        feed = self.state.feed_snapshot(limit or self.config.feed_limit)
        for key in ["queued", "running", "completed", "failed", "archived"]:
            feed[key] = [self._enrich_task_summary(item) for item in feed.get(key, [])]
        return feed

    def task_detail(self, task_key: str) -> dict[str, Any] | None:
        task = self.state.task_detail(task_key)
        if task is None:
            return None
        return self._enrich_task_summary(task)

    def health_snapshot(self) -> dict[str, Any]:
        return {
            "generatedAt": utc_now(),
            "runtime": self.runtime.health_snapshot(),
            "power": {
                "mode": self.current_power_mode(),
                "profiles": self.power_profiles(),
            },
            "counts": self.state.counts(),
            "workspaceRoot": str(self.config.workspace_root),
            "dashboard": {
                "host": self.config.dashboard_host,
                "port": self.config.dashboard_port,
                "url": f"http://{self.config.dashboard_host}:{self.config.dashboard_port}",
            },
        }

    def reported_health_snapshot(self) -> dict[str, Any]:
        report_path = self.config.reports_dir / "health.json"
        if report_path.exists():
            try:
                return json.loads(report_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
        snapshot = self.health_snapshot()
        report_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return snapshot

    def _iter_candidate_files(self) -> list[Path]:
        results: list[Path] = []
        for pattern in self.config.scan_globs:
            for path in self.config.workspace_root.glob(pattern):
                if not path.is_file():
                    continue
                if any(part in self.config.ignore_dirs for part in path.parts):
                    continue
                results.append(path.resolve())
        return sorted(set(results))

    def _load_package(self, path: Path) -> dict[str, Any] | None:
        if not path.exists() or not path.is_file():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None
        if not isinstance(payload, dict):
            return None
        if not isinstance(payload.get("course"), dict):
            return None
        if not isinstance(payload.get("lessons"), list):
            return None
        return payload

    def _enrich_task_summary(self, summary: dict[str, Any]) -> dict[str, Any]:
        details = dict(summary.get("details") or {})
        if self.config.source_mode == "amanoba_live_db":
            course_name = str(details.get("humanCourseName") or summary.get("courseId") or "Unknown course")
            day_label = str(details.get("humanDayLabel") or summary.get("lessonId") or "-")
            lesson_title = str(details.get("humanLessonTitle") or summary.get("lessonId") or "-")
            human_title = str(
                details.get("displayTitle")
                or (details.get("after") or {}).get("question")
                or (details.get("before") or {}).get("question")
                or (details.get("after") or {}).get("title")
                or (details.get("before") or {}).get("title")
                or summary.get("taskKey")
            )
            summary["details"] = details
            summary["humanTitle"] = human_title
            summary["humanCourseName"] = course_name
            summary["humanDayLabel"] = day_label
            summary["humanLessonTitle"] = lesson_title
            summary["humanContext"] = f"{course_name} • {day_label}"
            summary["humanUpdatedAt"] = summary.get("finishedAt") or summary.get("updatedAt") or summary.get("startedAt") or summary.get("createdAt")
            return summary
        package = self._load_package(Path(summary["packagePath"]))
        course = package.get("course") if package is not None else None
        lesson = None
        question = None
        if package is not None:
            lesson = next((item for item in package.get("lessons") or [] if str(item.get("lessonId")) == str(summary.get("lessonId") or "")), None)
            if lesson is not None and summary.get("kind") == "question":
                index = summary.get("questionIndex")
                questions = lesson.get("quizQuestions") or []
                if isinstance(index, int) and 0 <= index < len(questions):
                    question = questions[index]
        if summary.get("kind") == "question":
            if "before" not in details and isinstance(question, dict):
                details["before"] = json.loads(json.dumps(question, ensure_ascii=False))
            if "displayTitle" not in details:
                details["displayTitle"] = (
                    str((details.get("after") or {}).get("question") or (details.get("before") or {}).get("question") or "")
                    or str((question or {}).get("question") or "")
                )
        else:
            if "before" not in details and isinstance(lesson, dict):
                details["before"] = {
                    "title": lesson.get("title"),
                    "content": lesson.get("content"),
                    "emailSubject": lesson.get("emailSubject"),
                    "emailBody": lesson.get("emailBody"),
                }
            if "displayTitle" not in details:
                details["displayTitle"] = (
                    str((details.get("after") or {}).get("title") or (details.get("before") or {}).get("title") or "")
                    or str((lesson or {}).get("title") or "")
                )
        human_title = details.get("displayTitle") or summary.get("questionUuid") or summary.get("lessonId") or summary.get("taskKey")
        course_name = str((course or {}).get("name") or summary.get("courseId") or "Unknown course")
        day_number = (lesson or {}).get("dayNumber")
        day_label = f"Day {day_number}" if day_number not in (None, "") else str(summary.get("lessonId") or "-")
        lesson_title = str((lesson or {}).get("title") or summary.get("lessonId") or "-")
        summary["details"] = details
        summary["humanTitle"] = str(human_title)
        summary["humanCourseName"] = course_name
        summary["humanDayLabel"] = day_label
        summary["humanLessonTitle"] = lesson_title
        summary["humanContext"] = f"{course_name} • {day_label}"
        summary["humanUpdatedAt"] = summary.get("finishedAt") or summary.get("updatedAt") or summary.get("startedAt") or summary.get("createdAt")
        return summary

    def _enqueue_tasks(self, path: Path, package: dict[str, Any]) -> int:
        raw_text = path.read_text(encoding="utf-8")
        fingerprint = sha256_text(raw_text)
        course = package.get("course") or {}
        lessons = package.get("lessons") or []
        course_id = str(course.get("courseId", ""))
        language = str(course.get("language", ""))
        self.state.save_package(str(path), fingerprint, course_id, language)

        created = 0
        for lesson_index, lesson in enumerate(lessons):
            lesson_id = str(lesson.get("lessonId", f"lesson-{lesson_index + 1}"))
            lesson_audit = audit_lesson(lesson)
            if not lesson_audit.is_valid:
                self.state.upsert_task(
                    task_key=f"lesson::{path}::{lesson_id}",
                    kind="lesson",
                    package_path=str(path),
                    course_id=course_id,
                    language=language,
                    lesson_id=lesson_id,
                    question_uuid=None,
                    question_index=None,
                    source_hash=sha256_json({"lesson": lesson}),
                    details={
                        "errors": lesson_audit.errors,
                        "warnings": lesson_audit.warnings,
                        "displayTitle": str(lesson.get("title") or lesson_id),
                        "judgement": confidence_for_validation("lesson", lesson_audit.errors, lesson_audit.warnings),
                    },
                )
                created += 1
            for question_index, question in enumerate(lesson.get("quizQuestions") or []):
                validation = validate_question(question)
                if validation.is_valid:
                    continue
                question_uuid = str(question.get("uuid") or f"idx-{question_index}")
                self.state.upsert_task(
                    task_key=f"question::{path}::{lesson_id}::{question_uuid}",
                    kind="question",
                    package_path=str(path),
                    course_id=course_id,
                    language=language,
                    lesson_id=lesson_id,
                    question_uuid=question_uuid,
                    question_index=question_index,
                    source_hash=sha256_json({"question": question}),
                    details={
                        "errors": validation.errors,
                        "warnings": validation.warnings,
                        "displayTitle": str(question.get("question") or question_uuid),
                        "judgement": confidence_for_validation("question", validation.errors, validation.warnings),
                    },
                )
                created += 1
        return created

    def _process_task(self, task: sqlite3.Row) -> dict[str, Any]:
        if self.config.source_mode == "amanoba_live_db":
            return self._process_live_task(task)
        package_path = Path(task["package_path"])
        package = self._load_package(package_path)
        if package is None:
            raise RuntimeError(f"Package could not be loaded: {package_path}")
        course = package["course"]
        lessons = package["lessons"]
        lesson = next((item for item in lessons if str(item.get("lessonId")) == task["lesson_id"]), None)
        if lesson is None:
            raise RuntimeError(f"Lesson not found: {task['lesson_id']}")
        human_feedback = self.state.feedback_comments(task["task_key"])
        if task["kind"] == "lesson":
            return self._process_lesson_task(package_path, package, course, lesson, human_feedback)
        return self._process_question_task(package_path, package, course, lesson, int(task["question_index"]), human_feedback)

    def _process_live_task(self, task: sqlite3.Row) -> dict[str, Any]:
        if self.live_bridge is None:
            raise RuntimeError("Live DB mode is enabled but the live bridge is not configured.")
        live_task = self.live_bridge.fetch(str(task["task_key"]))
        human_feedback = self.state.feedback_comments(task["task_key"])
        course = live_task.get("course") or {}
        lesson = live_task.get("lesson") or {}
        if task["kind"] == "lesson":
            return self._process_live_lesson_task(str(task["task_key"]), course, lesson, human_feedback)
        question = live_task.get("question") or {}
        return self._process_live_question_task(str(task["task_key"]), course, lesson, question, human_feedback)

    def _process_live_lesson_task(
        self,
        task_key: str,
        course: dict[str, Any],
        lesson: dict[str, Any],
        human_feedback: list[str],
    ) -> dict[str, Any]:
        human_course = str(course.get("name") or lesson.get("courseName") or lesson.get("courseId") or "Unknown course")
        human_day = f"Day {lesson.get('dayNumber')}" if lesson.get("dayNumber") not in (None, "") else str(lesson.get("lessonId") or "-")
        human_lesson = str(lesson.get("title") or lesson.get("lessonId") or "-")
        before = {
            "title": lesson.get("title"),
            "content": lesson.get("content"),
            "emailSubject": lesson.get("emailSubject"),
            "emailBody": lesson.get("emailBody"),
        }
        audit = audit_lesson(before)
        if audit.is_valid:
            self.live_bridge.mark_reviewed(task_key, result="already-valid")
            judgement = confidence_for_completion("none", audit.warnings)
            return {
                "status": "already-valid",
                "warnings": audit.warnings,
                "judgement": judgement,
                "before": before,
                "after": before,
                "displayTitle": human_lesson,
                "humanCourseName": human_course,
                "humanDayLabel": human_day,
                "humanLessonTitle": human_lesson,
            }
        if not self.config.fix_lessons or not self.config.apply_fixes:
            raise RuntimeError(f"Lesson needs improvement but lesson fixing is disabled: {audit.errors}")
        provider = self.runtime.selected_provider()
        rewrite_input = list(audit.errors)
        rewrite_input.extend(f"Human challenge: {comment}" for comment in human_feedback)
        rewritten = _normalize_lesson_payload(provider.rewrite_lesson(course, lesson, rewrite_input))
        post_audit = audit_lesson(rewritten)
        if not post_audit.is_valid:
            raise RuntimeError(f"Rewritten lesson still failed validation: {post_audit.errors}")
        backup = self._backup_live_snapshot(task_key, before)
        self.live_bridge.apply(task_key, rewritten)
        after = _normalize_lesson_payload(rewritten)
        judgement = confidence_for_completion(provider.name, post_audit.warnings)
        return {
            "status": "rewritten",
            "provider": provider.name,
            "backup": str(backup),
            "warnings": post_audit.warnings,
            "judgement": judgement,
            "before": before,
            "after": after,
            "displayTitle": human_lesson,
            "humanCourseName": human_course,
            "humanDayLabel": human_day,
            "humanLessonTitle": human_lesson,
            "feedbackUsed": human_feedback,
            "changedFields": [key for key in before if before.get(key) != after.get(key)],
        }

    def _process_live_question_task(
        self,
        task_key: str,
        course: dict[str, Any],
        lesson: dict[str, Any],
        question: dict[str, Any],
        human_feedback: list[str],
    ) -> dict[str, Any]:
        human_course = str(course.get("name") or lesson.get("courseName") or lesson.get("courseId") or question.get("courseId") or "Unknown course")
        human_day = f"Day {lesson.get('dayNumber')}" if lesson.get("dayNumber") not in (None, "") else str(question.get("lessonId") or lesson.get("lessonId") or "-")
        human_lesson = str(lesson.get("title") or question.get("lessonTitle") or question.get("lessonId") or "-")
        human_question = str(question.get("question") or question.get("uuid") or task_key)
        before = json.loads(json.dumps(question, ensure_ascii=False))
        validation = validate_question(before)
        if validation.is_valid:
            self.live_bridge.mark_reviewed(task_key, result="already-valid")
            judgement = confidence_for_completion("none", validation.warnings)
            return {
                "status": "already-valid",
                "warnings": validation.warnings,
                "judgement": judgement,
                "before": before,
                "after": before,
                "displayTitle": human_question,
                "humanCourseName": human_course,
                "humanDayLabel": human_day,
                "humanLessonTitle": human_lesson,
            }
        if not self.config.fix_questions or not self.config.apply_fixes:
            raise RuntimeError(f"Question needs improvement but question fixing is disabled: {validation.errors}")
        provider = self.runtime.selected_provider()
        rewrite_input = list(validation.errors)
        rewrite_input.extend(f"Human challenge: {comment}" for comment in human_feedback)
        rewritten = provider.rewrite_question(course, lesson, question, rewrite_input)
        post_validation = validate_question(rewritten)
        if not post_validation.is_valid:
            raise RuntimeError(f"Rewritten question still failed validation: {post_validation.errors}")
        backup = self._backup_live_snapshot(task_key, before)
        self.live_bridge.apply(task_key, rewritten)
        after = json.loads(json.dumps(rewritten, ensure_ascii=False))
        judgement = confidence_for_completion(provider.name, post_validation.warnings)
        return {
            "status": "rewritten",
            "provider": provider.name,
            "backup": str(backup),
            "warnings": post_validation.warnings,
            "judgement": judgement,
            "before": before,
            "after": after,
            "displayTitle": str(after.get("question") or human_question),
            "humanCourseName": human_course,
            "humanDayLabel": human_day,
            "humanLessonTitle": human_lesson,
            "feedbackUsed": human_feedback,
            "changedFields": [key for key in after if before.get(key) != after.get(key)],
        }

    def _process_lesson_task(
        self,
        package_path: Path,
        package: dict[str, Any],
        course: dict[str, Any],
        lesson: dict[str, Any],
        human_feedback: list[str],
    ) -> dict[str, Any]:
        audit = audit_lesson(lesson)
        if audit.is_valid:
            judgement = confidence_for_completion("none", audit.warnings)
            return {"status": "already-valid", "warnings": audit.warnings, "judgement": judgement}
        if not self.config.fix_lessons or not self.config.apply_fixes:
            raise RuntimeError(f"Lesson needs improvement but lesson fixing is disabled: {audit.errors}")
        before = {
            "title": lesson.get("title"),
            "content": lesson.get("content"),
            "emailSubject": lesson.get("emailSubject"),
            "emailBody": lesson.get("emailBody"),
        }
        provider = self.runtime.selected_provider()
        rewrite_input = list(audit.errors)
        rewrite_input.extend(f"Human challenge: {comment}" for comment in human_feedback)
        rewritten = _normalize_lesson_payload(provider.rewrite_lesson(course, lesson, rewrite_input))
        lesson["title"] = rewritten["title"]
        lesson["content"] = rewritten["content"]
        lesson["emailSubject"] = rewritten["emailSubject"]
        lesson["emailBody"] = rewritten["emailBody"]
        post_audit = audit_lesson(lesson)
        if not post_audit.is_valid:
            raise RuntimeError(f"Rewritten lesson still failed validation: {post_audit.errors}")
        backup = self._backup_file(package_path)
        self._save_package(package_path, package)
        judgement = confidence_for_completion(provider.name, post_audit.warnings)
        after = _normalize_lesson_payload(
            {
                "title": lesson.get("title"),
                "content": lesson.get("content"),
                "emailSubject": lesson.get("emailSubject"),
                "emailBody": lesson.get("emailBody"),
            }
        )
        return {
            "status": "rewritten",
            "provider": provider.name,
            "backup": str(backup),
            "warnings": post_audit.warnings,
            "judgement": judgement,
            "before": before,
            "after": after,
            "feedbackUsed": human_feedback,
            "changedFields": [key for key in before if before.get(key) != after.get(key)],
        }

    def _process_question_task(
        self,
        package_path: Path,
        package: dict[str, Any],
        course: dict[str, Any],
        lesson: dict[str, Any],
        question_index: int,
        human_feedback: list[str],
    ) -> dict[str, Any]:
        questions = lesson.get("quizQuestions") or []
        if question_index >= len(questions):
            raise RuntimeError(f"Question index is out of range: {question_index}")
        question = questions[question_index]
        validation = validate_question(question)
        if validation.is_valid:
            judgement = confidence_for_completion("none", validation.warnings)
            return {"status": "already-valid", "warnings": validation.warnings, "judgement": judgement}
        if not self.config.fix_questions or not self.config.apply_fixes:
            raise RuntimeError(f"Question needs improvement but question fixing is disabled: {validation.errors}")
        before = json.loads(json.dumps(question, ensure_ascii=False))
        provider = self.runtime.selected_provider()
        rewrite_input = list(validation.errors)
        rewrite_input.extend(f"Human challenge: {comment}" for comment in human_feedback)
        rewritten = provider.rewrite_question(course, lesson, question, rewrite_input)
        for key in ["question", "options", "correctIndex", "questionType", "difficulty", "category", "hashtags"]:
            if key in rewritten:
                question[key] = rewritten[key]
        post_validation = validate_question(question)
        if not post_validation.is_valid:
            raise RuntimeError(f"Rewritten question still failed validation: {post_validation.errors}")
        backup = self._backup_file(package_path)
        self._save_package(package_path, package)
        judgement = confidence_for_completion(provider.name, post_validation.warnings)
        after = json.loads(json.dumps(question, ensure_ascii=False))
        return {
            "status": "rewritten",
            "provider": provider.name,
            "backup": str(backup),
            "warnings": post_validation.warnings,
            "judgement": judgement,
            "before": before,
            "after": after,
            "feedbackUsed": human_feedback,
            "changedFields": [key for key in after if before.get(key) != after.get(key)],
        }

    def _save_package(self, path: Path, package: dict[str, Any]) -> None:
        path.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def _backup_file(self, path: Path) -> Path:
        stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        relative = path.relative_to(self.config.workspace_root)
        backup_dir = self.config.backups_dir / relative.parent
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / f"{path.stem}__{stamp}{path.suffix}"
        shutil.copy2(path, backup_path)
        return backup_path

    def _backup_live_snapshot(self, task_key: str, payload: dict[str, Any]) -> Path:
        stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        safe_name = task_key.replace("::", "__").replace("/", "_")
        backup_dir = self.config.backups_dir / "live-db"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / f"{safe_name}__{stamp}.json"
        backup_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return backup_path

    def _write_reports(self) -> None:
        feed = self.feed_snapshot()
        health = self.reported_health_snapshot()
        (self.config.reports_dir / "status.json").write_text(
            json.dumps({"generatedAt": feed["generatedAt"], "counts": feed["counts"]}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (self.config.reports_dir / "feed.json").write_text(json.dumps(feed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (self.config.reports_dir / "health.json").write_text(json.dumps(health, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (self.config.reports_dir / "feed.md").write_text(self._feed_markdown(feed, health), encoding="utf-8")

    def _feed_markdown(self, feed: dict[str, Any], health: dict[str, Any]) -> str:
        lines = [
            "# Course Quality Control Center",
            "",
            f"Generated at: {feed['generatedAt']}",
            "",
            "## Runtime",
            "",
            f"- selected provider: {health['runtime']['selected'].get('provider')} ({health['runtime']['selected'].get('status')})",
            f"- detail: {health['runtime']['selected'].get('detail')}",
            f"- dashboard: {health['dashboard']['url']}",
            "",
            "## Counts",
            "",
        ]
        counts = feed.get("counts", {})
        if counts:
            for key in sorted(counts):
                lines.append(f"- {key}: {counts[key]}")
        else:
            lines.append("- no jobs yet")
        lines.extend(["", "## Coming Up", ""])
        lines.extend(self._section_lines(feed.get("queued", []), "No queued jobs."))
        lines.extend(["", "## Active Now", ""])
        lines.extend(self._section_lines(feed.get("running", []), "No running jobs."))
        lines.extend(["", "## Done Recently", ""])
        lines.extend(self._section_lines(feed.get("completed", []), "No completed jobs yet."))
        lines.extend(["", "## Failed", ""])
        lines.extend(self._section_lines(feed.get("failed", []), "No failed jobs."))
        lines.append("")
        return "\n".join(lines)

    def _section_lines(self, rows: list[dict[str, Any]], empty_message: str) -> list[str]:
        if not rows:
            return [f"- {empty_message}"]
        lines: list[str] = []
        for row in rows:
            target = row.get("questionUuid") or row.get("lessonId") or row.get("taskKey")
            prefix = f"- [{row.get('status')}] {row.get('courseId') or 'unknown-course'} / {row.get('lessonId') or '-'} / {target}"
            lines.append(prefix)
            judgement = row.get("details", {}).get("judgement") or {}
            if judgement:
                lines.append(f"  confidence: {judgement.get('confidence')} ({judgement.get('trustTier')})")
            if row.get("lastError"):
                lines.append(f"  error: {row['lastError']}")
            lines.append(f"  attempts: {row.get('attempts', 0)} | updated: {row.get('updatedAt')}")
        return lines


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Continuous quality worker for Amanoba course packages.")
    parser.add_argument("--config", required=True, help="Path to the daemon config JSON file.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("scan", help="Scan the workspace and refresh the task queue.")
    run_once = subparsers.add_parser("run-once", help="Scan, then process up to N items.")
    run_once.add_argument("--max-items", type=int, default=1)
    subparsers.add_parser("status", help="Print task counts.")
    feed = subparsers.add_parser("feed", help="Print the live job feed.")
    feed.add_argument("--limit", type=int, default=DEFAULT_FEED_LIMIT)
    subparsers.add_parser("health", help="Print runtime health.")
    subparsers.add_parser("watchdog", help="Run one watchdog supervision cycle.")
    dash = subparsers.add_parser("dashboard", help="Run the local web dashboard.")
    dash.add_argument("--host", default=None)
    dash.add_argument("--port", type=int, default=None)
    subparsers.add_parser("daemon", help="Run the scanner/worker loop continuously.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    config = Config.from_file(Path(args.config).resolve())
    daemon = CourseQualityDaemon(config)

    if args.command == "scan":
        print(json.dumps(daemon.scan(), ensure_ascii=False, indent=2))
        return
    if args.command == "run-once":
        lock_fd = acquire_process_lock(config.state_db_path.parent / "process.lock")
        if lock_fd is None:
            print(json.dumps({"busy": True, "reason": "another worker process is already active"}, ensure_ascii=False, indent=2))
            return
        try:
            scan_result = daemon.scan()
            processed: list[str] = []
            for _ in range(max(1, int(args.max_items))):
                outcome = daemon.process_one()
                if outcome == "idle":
                    break
                processed.append(outcome)
            print(json.dumps({"scan": scan_result, "processed": processed}, ensure_ascii=False, indent=2))
            return
        finally:
            release_process_lock(lock_fd)
    if args.command == "status":
        print(json.dumps(daemon.state.counts(), ensure_ascii=False, indent=2))
        return
    if args.command == "feed":
        print(json.dumps(daemon.feed_snapshot(limit=args.limit), ensure_ascii=False, indent=2))
        return
    if args.command == "health":
        print(json.dumps(daemon.health_snapshot(), ensure_ascii=False, indent=2))
        return
    if args.command == "watchdog":
        from .watchdog import run_watchdog

        run_watchdog(config.config_path)
        return
    if args.command == "dashboard":
        from .dashboard import run_dashboard

        run_dashboard(daemon, host=args.host or config.dashboard_host, port=args.port or config.dashboard_port)
        return
    lock_fd = acquire_process_lock(config.state_db_path.parent / "process.lock")
    if lock_fd is None:
        print(json.dumps({"busy": True, "reason": "another worker process is already active"}, ensure_ascii=False, indent=2))
        return
    try:
        daemon.run_daemon()
    finally:
        release_process_lock(lock_fd)
