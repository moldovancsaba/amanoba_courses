from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from .daemon import Config, CourseQualityDaemon


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class CourseQualityWatchdog:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.root = config.workspace_root
        self.runtime_dir = self.root / ".course-quality"
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        self.state_path = self.runtime_dir / "watchdog-state.json"
        self.process_lock_path = self.runtime_dir / "process.lock"
        self.daemon = CourseQualityDaemon(config)
        self.watchdog_config = dict((json.loads(config.config_path.read_text(encoding="utf-8"))).get("watchdog") or {})
        self.worker_process_timeout_seconds = int(self.watchdog_config.get("worker_process_timeout_seconds") or 180)
        self.dashboard_request_timeout_seconds = int(self.watchdog_config.get("dashboard_request_timeout_seconds") or 8)
        self.ollama_request_timeout_seconds = int(self.watchdog_config.get("ollama_request_timeout_seconds") or 5)
        self.full_restart_interval_seconds = int(self.watchdog_config.get("full_restart_interval_seconds") or 10800)

    def run_once(self, incident: dict[str, Any] | None = None) -> dict[str, Any]:
        actions: list[dict[str, Any]] = []
        state = self._load_state()

        killed = self._kill_stale_worker_processes()
        if killed:
            actions.append({"type": "kill-stale-workers", "pids": killed})

        if self._clear_stale_process_lock():
            actions.append({"type": "clear-stale-lock", "path": str(self.process_lock_path)})

        recovered = self.daemon.state.recover_stale_running_tasks(
            max_runtime_seconds=self.config.max_task_runtime_seconds,
            max_attempts=self.config.max_attempts_per_task,
        )
        if recovered:
            actions.append({"type": "recover-stale-running", "count": recovered})

        quarantined = self.daemon.state.quarantine_repeated_failures(self.config.quarantine_after_failures)
        if quarantined:
            for task_key in quarantined:
                self.daemon.state.add_feedback_comment(
                    task_key,
                    "[system] Quarantined by watchdog after repeated bounce-backs. Human review is required before requeue.",
                )
            actions.append({"type": "quarantine-repeat-offenders", "count": len(quarantined), "taskKeys": quarantined[:10]})

        dashboard_ok = self._dashboard_healthy()
        if not dashboard_ok:
            self._kickstart_label("com.amanoba.coursequality.dashboard")
            actions.append({"type": "restart-dashboard"})

        ollama_ok = self._ollama_healthy()
        if not ollama_ok:
            self._kickstart_label("com.amanoba.coursequality.ollama")
            actions.append({"type": "restart-ollama"})

        if incident:
            actions.extend(self._handle_incident(incident, dashboard_ok=dashboard_ok, ollama_ok=ollama_ok))

        if self._needs_full_restart(state):
            self._kickstart_label("com.amanoba.coursequality.dashboard")
            self._kickstart_label("com.amanoba.coursequality.ollama")
            self._kickstart_label("com.amanoba.coursequality.worker")
            state["lastFullRestartAt"] = utc_now()
            actions.append({"type": "full-restart"})
        else:
            if self._should_start_worker():
                self._kickstart_label("com.amanoba.coursequality.worker")
                actions.append({"type": "kickstart-worker"})

        summary = {
            "generatedAt": utc_now(),
            "incident": incident,
            "counts": self.daemon.state.counts(),
            "dashboardHealthy": self._dashboard_healthy(),
            "ollamaHealthy": self._ollama_healthy(),
            "activeWorkerProcesses": self._worker_processes(),
            "actions": actions,
        }
        self._save_state(state)
        report_path = self.config.reports_dir / "watchdog.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return summary

    def _load_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {}
        try:
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save_state(self, state: dict[str, Any]) -> None:
        self.state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def _worker_processes(self) -> list[dict[str, Any]]:
        result = subprocess.run(
            ["ps", "-axo", "pid=,etimes=,command="],
            capture_output=True,
            text=True,
            check=False,
        )
        rows: list[dict[str, Any]] = []
        for line in (result.stdout or "").splitlines():
            line = line.strip()
            if not line or "course_quality_daemon" not in line:
                continue
            if f"--config {self.config.config_path}" not in line and str(self.config.config_path) not in line:
                continue
            if " run-once " not in f" {line} " and not line.endswith(" run-once"):
                continue
            parts = line.split(None, 2)
            if len(parts) < 3:
                continue
            try:
                pid = int(parts[0])
                etimes = int(parts[1])
            except ValueError:
                continue
            rows.append({"pid": pid, "etimes": etimes, "command": parts[2]})
        return rows

    def _kill_stale_worker_processes(self) -> list[int]:
        killed: list[int] = []
        for proc in self._worker_processes():
            if proc["etimes"] < self.worker_process_timeout_seconds:
                continue
            pid = int(proc["pid"])
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)
                try:
                    os.kill(pid, 0)
                except OSError:
                    killed.append(pid)
                    continue
                os.kill(pid, signal.SIGKILL)
                killed.append(pid)
            except OSError:
                continue
        return killed

    def _clear_stale_process_lock(self) -> bool:
        if not self.process_lock_path.exists():
            return False
        if self._worker_processes():
            return False
        try:
            self.process_lock_path.unlink()
            return True
        except OSError:
            return False

    def _dashboard_healthy(self) -> bool:
        try:
            with urllib.request.urlopen(
                f"http://{self.config.dashboard_host}:{self.config.dashboard_port}/api/health",
                timeout=self.dashboard_request_timeout_seconds,
            ) as response:
                if int(getattr(response, "status", 200)) >= 400:
                    return False
                json.loads(response.read().decode("utf-8"))
                return True
        except Exception:
            return False

    def _ollama_healthy(self) -> bool:
        endpoint = str((self.config.runtime_config.get("ollama") or {}).get("endpoint") or "http://127.0.0.1:11434").rstrip("/")
        try:
            with urllib.request.urlopen(f"{endpoint}/api/tags", timeout=self.ollama_request_timeout_seconds) as response:
                if int(getattr(response, "status", 200)) >= 400:
                    return False
                return True
        except Exception:
            return False

    def _needs_full_restart(self, state: dict[str, Any]) -> bool:
        raw = str(state.get("lastFullRestartAt") or "").strip()
        if not raw:
            return True
        try:
            then = time.mktime(time.strptime(raw, "%Y-%m-%dT%H:%M:%SZ"))
        except ValueError:
            return True
        return (time.time() - then) >= self.full_restart_interval_seconds

    def _handle_incident(self, incident: dict[str, Any], dashboard_ok: bool, ollama_ok: bool) -> list[dict[str, Any]]:
        actions: list[dict[str, Any]] = []
        incident_type = str(incident.get("type") or "").strip().lower()
        if incident_type in {"timeout", "live-bridge-timeout"}:
            if not dashboard_ok:
                self._kickstart_label("com.amanoba.coursequality.dashboard")
                actions.append({"type": "incident-restart-dashboard", "incidentType": incident_type})
            if not ollama_ok:
                self._kickstart_label("com.amanoba.coursequality.ollama")
                actions.append({"type": "incident-restart-ollama", "incidentType": incident_type})
            self._kickstart_label("com.amanoba.coursequality.worker")
            actions.append({"type": "incident-kickstart-worker", "incidentType": incident_type})
            if int(incident.get("attempt") or 0) >= 2:
                self._kickstart_label("com.amanoba.coursequality.dashboard")
                self._kickstart_label("com.amanoba.coursequality.ollama")
                self._kickstart_label("com.amanoba.coursequality.worker")
                actions.append({"type": "incident-full-stack-restart", "incidentType": incident_type})
        return actions

    def _should_start_worker(self) -> bool:
        counts = self.daemon.state.counts()
        if counts.get("running", 0) > 0:
            return False
        if self._worker_processes():
            return False
        return (
            counts.get("pending", 0) > 0
            or counts.get("failed", 0) > 0
            or counts.get("quarantined", 0) > 0
        )

    def _kickstart_label(self, label: str) -> None:
        uid = str(os.getuid())
        subprocess.run(["launchctl", "kickstart", "-k", f"gui/{uid}/{label}"], check=False, capture_output=True, text=True)


def run_watchdog(config_path: Path) -> None:
    config = Config.from_file(config_path.resolve())
    summary = CourseQualityWatchdog(config).run_once()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
