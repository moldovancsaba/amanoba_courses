from __future__ import annotations

import importlib.metadata
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
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
        self.daemon = CourseQualityDaemon(config, manage_worker_heartbeat=False)
        self.watchdog_config = dict((json.loads(config.config_path.read_text(encoding="utf-8"))).get("watchdog") or {})
        self.worker_process_timeout_seconds = int(self.watchdog_config.get("worker_process_timeout_seconds") or 600)
        self.worker_progress_timeout_seconds = int(self.watchdog_config.get("worker_progress_timeout_seconds") or max(300, self.worker_process_timeout_seconds))
        self.worker_backlog_timeout_seconds = int(
            self.watchdog_config.get("worker_backlog_timeout_seconds")
            or max(600, int(self.config.queue_check_interval_seconds) * 2)
        )
        self.dashboard_request_timeout_seconds = int(self.watchdog_config.get("dashboard_request_timeout_seconds") or 8)
        self.ollama_request_timeout_seconds = int(self.watchdog_config.get("ollama_request_timeout_seconds") or 5)
        self.full_restart_interval_seconds = int(self.watchdog_config.get("full_restart_interval_seconds") or 10800)
        self.provider_repair_timeout_seconds = int(self.watchdog_config.get("provider_repair_timeout_seconds") or 600)
        self.primary_writer_provider = str(self.watchdog_config.get("primary_writer_provider") or "mlx").strip().lower()
        mlx_cfg = dict(self.config.runtime_config.get("mlx") or {})
        self.mlx_timeout_seconds = int(mlx_cfg.get("timeout") or 120)
        self.mlx_process_timeout_seconds = int(
            self.watchdog_config.get("mlx_process_timeout_seconds") or max(self.mlx_timeout_seconds + 45, 600)
        )
        self.memory_pressure_swap_mb = int(self.watchdog_config.get("memory_pressure_swap_mb") or 512)
        self.memory_pressure_free_pages = int(self.watchdog_config.get("memory_pressure_free_pages") or 15000)

    def run_once(self, incident: dict[str, Any] | None = None) -> dict[str, Any]:
        actions: list[dict[str, Any]] = []
        state = self._load_state()

        killed = self._kill_stale_worker_processes()
        if killed:
            actions.append({"type": "kill-stale-workers", "pids": killed})

        duplicate_kills = self._kill_duplicate_qc_processes()
        if duplicate_kills:
            actions.append({"type": "kill-duplicate-workers", "pids": duplicate_kills})

        stale_mlx = self._kill_stale_mlx_worker_processes()
        if stale_mlx:
            actions.append({"type": "kill-stale-mlx-workers", "pids": stale_mlx})
            self._kickstart_label("com.amanoba.coursequality.worker")
            actions.append({"type": "restart-worker-after-stale-mlx"})

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

        stalled = self._worker_stalled()
        if stalled is not None:
            pid = int(stalled.get("pid") or 0)
            if pid > 0:
                try:
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(1)
                    try:
                        os.kill(pid, 0)
                    except OSError:
                        pass
                    else:
                        os.kill(pid, signal.SIGKILL)
                except OSError:
                    pass
            actions.append({"type": "restart-stalled-worker", "worker": stalled})

        backlog_stalled = self._worker_backlog_stalled()
        if backlog_stalled is not None:
            self._kickstart_label("com.amanoba.coursequality.worker")
            actions.append({"type": "restart-backlog-stalled-worker", "worker": backlog_stalled})

        dashboard_ok = self._dashboard_healthy()
        if not dashboard_ok:
            self._kickstart_label("com.amanoba.coursequality.dashboard")
            actions.append({"type": "restart-dashboard"})

        ollama_ok = self._ollama_healthy()
        if not ollama_ok:
            self._kickstart_label("com.amanoba.coursequality.ollama")
            actions.append({"type": "restart-ollama"})

        resident_repairs = self._repair_resident_roles()
        if resident_repairs:
            actions.extend(resident_repairs)

        runtime_before = self.daemon.runtime.health_snapshot()
        dashboard_runtime = self._dashboard_runtime_snapshot()
        actions.extend(self._repair_runtime_providers(runtime_before, dashboard_runtime))
        memory_pressure = self._memory_pressure_status()
        if memory_pressure.get("degraded"):
            actions.append({"type": "memory-pressure-detected", **memory_pressure})
            warmed = self._warm_creator_roles_after_pressure(memory_pressure)
            if warmed:
                actions.append({"type": "warm-creator-roles-after-pressure", "roles": warmed})
        runtime_after = self.daemon.runtime.health_snapshot()
        creator_pipeline = self.daemon._creator_pipeline_manifest()

        if incident:
            actions.extend(self._handle_incident(incident, dashboard_ok=dashboard_ok, ollama_ok=ollama_ok))

        if self._needs_full_restart(state):
            self._kickstart_label("com.amanoba.coursequality.dashboard")
            self._kickstart_label("com.amanoba.coursequality.ollama")
            self._kickstart_label("com.amanoba.coursequality.worker")
            state["lastFullRestartAt"] = utc_now()
            actions.append({"type": "full-restart"})
        summary = {
            "generatedAt": utc_now(),
            "incident": incident,
            "counts": self.daemon.state.counts(),
            "dashboardHealthy": self._dashboard_healthy(),
            "ollamaHealthy": self._ollama_healthy(),
            "runtime": runtime_after,
            "dashboardRuntime": dashboard_runtime,
            "creatorPipeline": creator_pipeline,
            "providerIssues": self._provider_issues(runtime_after),
            "creatorPipelineIssues": self._creator_pipeline_issues(creator_pipeline),
            "activeWorkerProcesses": self._active_qc_processes(),
            "activeMlxWorkerProcesses": self._active_mlx_worker_processes(),
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

    def _active_qc_processes(self) -> list[dict[str, Any]]:
        result = subprocess.run(
            ["ps", "-axo", "pid=,etime=,command="],
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
            command_text = f" {line} "
            if " daemon " not in command_text and " run-once " not in command_text:
                continue
            parts = line.split(None, 2)
            if len(parts) < 3:
                continue
            try:
                pid = int(parts[0])
                etimes = self._parse_etime(parts[1])
            except ValueError:
                continue
            rows.append({"pid": pid, "etimes": etimes, "command": parts[2]})
        return rows

    def _parse_etime(self, raw: str) -> int:
        text = str(raw or "").strip()
        if not text:
            raise ValueError("missing etime")
        days = 0
        clock = text
        if "-" in text:
            day_part, clock = text.split("-", 1)
            days = int(day_part)
        fields = [int(part) for part in clock.split(":")]
        if len(fields) == 3:
            hours, minutes, seconds = fields
        elif len(fields) == 2:
            hours = 0
            minutes, seconds = fields
        elif len(fields) == 1:
            hours = 0
            minutes = 0
            seconds = fields[0]
        else:
            raise ValueError(f"invalid etime: {raw}")
        return days * 86400 + hours * 3600 + minutes * 60 + seconds

    def _worker_processes(self) -> list[dict[str, Any]]:
        return [
            proc
            for proc in self._active_qc_processes()
            if " run-once " in f" {proc['command']} " or str(proc["command"]).endswith(" run-once")
        ]

    def _daemon_processes(self) -> list[dict[str, Any]]:
        return [
            proc
            for proc in self._active_qc_processes()
            if " daemon " in f" {proc['command']} " or str(proc["command"]).endswith(" daemon")
        ]

    def _kill_duplicate_qc_processes(self) -> list[int]:
        processes = sorted(self._active_qc_processes(), key=lambda item: (int(item.get("etimes") or 0), int(item.get("pid") or 0)), reverse=True)
        if len(processes) <= 1:
            return []
        keep = processes[0]
        killed: list[int] = []
        for proc in processes[1:]:
            pid = int(proc.get("pid") or 0)
            if pid <= 0 or pid == int(keep.get("pid") or 0):
                continue
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

    def _kill_stale_mlx_worker_processes(self) -> list[int]:
        killed: list[int] = []
        for proc in self._active_mlx_worker_processes():
            if int(proc.get("etimes") or 0) < self.mlx_process_timeout_seconds:
                continue
            pid = int(proc.get("pid") or 0)
            if pid <= 0:
                continue
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
        if self._active_qc_processes():
            return False
        try:
            self.process_lock_path.unlink()
            return True
        except OSError:
            return False

    def _repair_resident_roles(self) -> list[dict[str, Any]]:
        actions: list[dict[str, Any]] = []
        for role in self.daemon.resident_role_snapshot():
            if bool(role.get("reachable")):
                continue
            label = str(role.get("launchLabel") or "").strip()
            if not label:
                continue
            self._kickstart_label(label)
            actions.append(
                {
                    "type": "restart-resident-role",
                    "role": str(role.get("name") or "ROLE"),
                    "label": label,
                    "endpoint": f"{role.get('host') or '127.0.0.1'}:{role.get('port') or '-'}",
                }
            )
        return actions

    def _worker_stalled(self) -> dict[str, Any] | None:
        daemons = self._daemon_processes()
        if len(daemons) != 1:
            return None
        worker = daemons[0]
        heartbeat = self.daemon.worker_status_snapshot()
        progress_at = str(heartbeat.get("progressAt") or "").strip()
        phase = str(heartbeat.get("phase") or "").strip().lower()
        if not progress_at or phase in {"idle", "sleeping", "stopped"}:
            return None
        try:
            then = datetime.fromisoformat(progress_at).astimezone(timezone.utc)
        except ValueError:
            return None
        age = int((datetime.now(timezone.utc) - then).total_seconds())
        if age < self.worker_progress_timeout_seconds:
            return None
        return {
            "pid": worker.get("pid"),
            "phase": heartbeat.get("phase"),
            "taskKey": heartbeat.get("taskKey"),
            "progressAt": progress_at,
            "stalledSeconds": age,
        }

    def _worker_backlog_stalled(self) -> dict[str, Any] | None:
        counts = self.daemon.state.counts()
        pending = int(counts.get("pending") or 0)
        running = int(counts.get("running") or 0)
        if pending <= 0 or running > 0:
            return None
        daemons = self._daemon_processes()
        if len(daemons) != 1:
            if pending > 0:
                return {
                    "pid": None,
                    "phase": "missing-worker",
                    "pending": pending,
                    "running": running,
                    "stalledSeconds": None,
                }
            return None
        worker = daemons[0]
        heartbeat = self.daemon.worker_status_snapshot()
        phase = str(heartbeat.get("phase") or "").strip().lower()
        if phase == "processing":
            return None
        progress_at = str(heartbeat.get("progressAt") or "").strip()
        if not progress_at:
            return {
                "pid": worker.get("pid"),
                "phase": phase or "unknown",
                "pending": pending,
                "running": running,
                "stalledSeconds": None,
            }
        try:
            then = datetime.fromisoformat(progress_at).astimezone(timezone.utc)
        except ValueError:
            return None
        age = int((datetime.now(timezone.utc) - then).total_seconds())
        if age < self.worker_backlog_timeout_seconds:
            return None
        return {
            "pid": worker.get("pid"),
            "phase": heartbeat.get("phase"),
            "taskKey": heartbeat.get("taskKey"),
            "progressAt": progress_at,
            "pending": pending,
            "running": running,
            "stalledSeconds": age,
        }

    def _dashboard_healthy(self) -> bool:
        try:
            with urllib.request.urlopen(
                f"http://{self.config.dashboard_host}:{self.config.dashboard_port}/api/healthz",
                timeout=self.dashboard_request_timeout_seconds,
            ) as response:
                if int(getattr(response, "status", 200)) >= 400:
                    return False
                json.loads(response.read().decode("utf-8"))
                return True
        except Exception:
            return False

    def _dashboard_runtime_snapshot(self) -> dict[str, Any] | None:
        try:
            with urllib.request.urlopen(
                f"http://{self.config.dashboard_host}:{self.config.dashboard_port}/api/health",
                timeout=self.dashboard_request_timeout_seconds,
            ) as response:
                if int(getattr(response, "status", 200)) >= 400:
                    return None
                payload = json.loads(response.read().decode("utf-8"))
                runtime = payload.get("runtime")
                if isinstance(runtime, dict):
                    return runtime
        except Exception:
            return None
        return None

    def _ollama_healthy(self) -> bool:
        endpoint = str((self.config.runtime_config.get("ollama") or {}).get("endpoint") or "http://127.0.0.1:11434").rstrip("/")
        try:
            with urllib.request.urlopen(f"{endpoint}/api/tags", timeout=self.ollama_request_timeout_seconds) as response:
                if int(getattr(response, "status", 200)) >= 400:
                    return False
                return True
        except Exception:
            return False

    def _memory_pressure_status(self) -> dict[str, Any]:
        swap_used_mb = 0
        swap_free_mb = 0
        swap_total_mb = 0
        free_pages = None
        degraded = False
        details: list[str] = []
        try:
            swap = subprocess.run(["sysctl", "-n", "vm.swapusage"], capture_output=True, text=True, check=False)
            text = (swap.stdout or swap.stderr or "").strip()
            # Example: total = 16384.00M  used = 1024.00M  free = 15360.00M  (encrypted)
            for token in text.replace("(", " ").replace(")", " ").replace(",", " ").split():
                if token == "total" or token == "used" or token == "free":
                    continue
            match = re.findall(r"(total|used|free)\s*=\s*([0-9.]+)M", text)
            for kind, value in match:
                mb = int(float(value))
                if kind == "total":
                    swap_total_mb = mb
                elif kind == "used":
                    swap_used_mb = mb
                elif kind == "free":
                    swap_free_mb = mb
            if swap_used_mb >= self.memory_pressure_swap_mb:
                degraded = True
                details.append(f"swap used {swap_used_mb}MB")
        except Exception:
            pass
        try:
            vm = subprocess.run(["vm_stat"], capture_output=True, text=True, check=False)
            pages = self._parse_vm_stat(vm.stdout or "")
            free_pages = int(pages.get("Pages free") or 0)
            if free_pages and free_pages <= self.memory_pressure_free_pages:
                degraded = True
                details.append(f"free pages {free_pages}")
        except Exception:
            pass
        return {
            "degraded": degraded,
            "swapUsedMb": swap_used_mb,
            "swapFreeMb": swap_free_mb,
            "swapTotalMb": swap_total_mb,
            "freePages": free_pages,
            "detail": "; ".join(details) if details else "memory pressure not detected",
        }

    def _parse_vm_stat(self, text: str) -> dict[str, int]:
        pages: dict[str, int] = {}
        for line in text.splitlines():
            line = line.strip()
            if not line or ":" not in line:
                continue
            key, raw_value = line.split(":", 1)
            digits = "".join(ch for ch in raw_value if ch.isdigit())
            if not digits:
                continue
            pages[key.strip()] = int(digits)
        return pages

    def _warm_creator_roles_after_pressure(self, memory_pressure: dict[str, Any]) -> dict[str, bool]:
        warmed: dict[str, bool] = {}
        try:
            warmed = self.daemon.runtime.warm_creator_roles()
        except Exception:
            warmed = {}
        if not warmed:
            # Fall back to a direct health pass if warm hooks are unavailable.
            warmed = {
                role: bool(self.daemon.runtime.creator_role_health(role).get("available"))
                for role in ("drafter", "writer", "judge")
            }
        return warmed

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
            if int(incident.get("attempt") or 0) >= 2:
                self._kickstart_label("com.amanoba.coursequality.dashboard")
                self._kickstart_label("com.amanoba.coursequality.ollama")
                self._kickstart_label("com.amanoba.coursequality.worker")
                actions.append({"type": "incident-full-stack-restart", "incidentType": incident_type})
        return actions

    def _provider_issues(self, runtime_snapshot: dict[str, Any]) -> list[dict[str, Any]]:
        issues: list[dict[str, Any]] = []
        for item in runtime_snapshot.get("providers") or []:
            status = str(item.get("status") or "").strip().upper()
            if status == "HEALTHY":
                continue
            issues.append(
                {
                    "provider": item.get("provider"),
                    "status": status,
                    "detail": item.get("detail"),
                    "configuredModel": item.get("configuredModel"),
                    "resolvedModel": item.get("resolvedModel"),
                    "endpoint": item.get("endpoint"),
                }
            )
        selected = runtime_snapshot.get("selected") or {}
        if (
            self.primary_writer_provider
            and str(selected.get("provider") or "").strip().lower() != self.primary_writer_provider
        ):
            issues.append(
                {
                    "provider": self.primary_writer_provider,
                    "status": "FALLBACK",
                    "detail": f"Selected provider is {selected.get('provider') or '-'} instead of primary {self.primary_writer_provider}.",
                    "configuredModel": None,
                    "resolvedModel": None,
                    "endpoint": None,
                }
            )
        return issues

    def _creator_pipeline_issues(self, creator_pipeline: dict[str, Any]) -> list[dict[str, Any]]:
        issues: list[dict[str, Any]] = []
        for role, item in creator_pipeline.items():
            if not isinstance(item, dict):
                continue
            if not bool(item.get("installed")):
                issues.append(
                    {
                        "role": role,
                        "status": "MISSING",
                        "detail": f"{item.get('model') or '-'} is not installed.",
                        "tool": item.get("tool"),
                        "model": item.get("model"),
                        "location": item.get("location"),
                    }
                )
            elif str(item.get("state") or "").strip().lower() == "degraded":
                issues.append(
                    {
                        "role": role,
                        "status": "DEGRADED",
                        "detail": str(item.get("description") or "Role is degraded."),
                        "tool": item.get("tool"),
                        "model": item.get("model"),
                        "location": item.get("location"),
                    }
                )
        return issues

    def _repair_runtime_providers(self, runtime_snapshot: dict[str, Any], dashboard_runtime: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        actions: list[dict[str, Any]] = []
        actions.extend(self._enforce_primary_writer_provider(runtime_snapshot, dashboard_runtime))
        for item in runtime_snapshot.get("providers") or []:
            provider = str(item.get("provider") or "").strip().lower()
            if provider != "mlx" or bool(item.get("available")):
                continue
            actions.extend(self._repair_mlx_provider(item))
        return actions

    def _enforce_primary_writer_provider(self, runtime_snapshot: dict[str, Any], dashboard_runtime: dict[str, Any] | None) -> list[dict[str, Any]]:
        actions: list[dict[str, Any]] = []
        primary = self.primary_writer_provider
        if primary != "mlx":
            return actions
        runtime_selected = str((runtime_snapshot.get("selected") or {}).get("provider") or "").strip().lower()
        dashboard_selected = str(((dashboard_runtime or {}).get("selected") or {}).get("provider") or "").strip().lower()
        mlx_health = next(
            (item for item in (runtime_snapshot.get("providers") or []) if str(item.get("provider") or "").strip().lower() == "mlx"),
            None,
        )
        mlx_available = bool((mlx_health or {}).get("available"))
        needs_repair = False
        if dashboard_selected and dashboard_selected != primary:
            needs_repair = True
        elif runtime_selected and runtime_selected != primary and mlx_available:
            needs_repair = True
        if not needs_repair:
            return actions

        killed_mlx = self._kill_active_mlx_worker_processes()
        if killed_mlx:
            actions.append({"type": "kill-stuck-mlx-workers", "pids": killed_mlx})
        self._kickstart_label("com.amanoba.coursequality.worker")
        self._kickstart_label("com.amanoba.coursequality.dashboard")
        actions.append(
            {
                "type": "restore-primary-writer-provider",
                "expectedProvider": primary,
                "runtimeSelected": runtime_selected or None,
                "dashboardSelected": dashboard_selected or None,
                "mlxAvailable": mlx_available,
            }
        )
        time.sleep(2)
        repaired_runtime = self._dashboard_runtime_snapshot() or {}
        repaired_selected = str(((repaired_runtime or {}).get("selected") or {}).get("provider") or "").strip().lower()
        actions.append(
            {
                "type": "primary-writer-provider-check",
                "expectedProvider": primary,
                "selectedProvider": repaired_selected or None,
                "ok": repaired_selected == primary,
            }
        )
        return actions

    def _repair_mlx_provider(self, provider_health: dict[str, Any]) -> list[dict[str, Any]]:
        detail = str(provider_health.get("detail") or "").strip()
        lowered = detail.lower()
        if "gpu timeout" in lowered or "metal runtime" in lowered or "command buffer execution failed" in lowered:
            killed = self._kill_active_mlx_worker_processes()
            self._kickstart_label("com.amanoba.coursequality.worker")
            self._kickstart_label("com.amanoba.coursequality.dashboard")
            actions = [{"type": "provider-unavailable", "provider": "mlx", "detail": detail}]
            if killed:
                actions.append({"type": "kill-stuck-mlx-workers", "provider": "mlx", "pids": killed})
            actions.append({"type": "restart-after-mlx-runtime-failure", "provider": "mlx"})
            return actions
        if "runtime missing" not in lowered and "no module named 'mlx_lm'" not in lowered:
            return [{"type": "provider-unavailable", "provider": "mlx", "detail": detail}]

        repair = self._ensure_mlx_runtime()
        actions = [
            {
                "type": "repair-mlx-runtime",
                "provider": "mlx",
                "ok": repair.get("ok"),
                "detail": repair.get("detail"),
                "python": repair.get("python"),
                "venv": repair.get("venv"),
            }
        ]
        if repair.get("ok"):
            self._kickstart_label("com.amanoba.coursequality.dashboard")
            self._kickstart_label("com.amanoba.coursequality.worker")
            actions.append({"type": "restart-dashboard-after-mlx-repair", "provider": "mlx"})
            actions.append({"type": "kickstart-worker-after-mlx-repair", "provider": "mlx"})
        return actions

    def _ensure_mlx_runtime(self) -> dict[str, Any]:
        venv_dir = self.root / ".venv-mlx"
        venv_python = venv_dir / "bin" / "python"
        bootstrap_python = self._bootstrap_python()
        if bootstrap_python is None:
            return {
                "ok": False,
                "detail": "No usable Python interpreter found to build the MLX runtime environment.",
                "venv": str(venv_dir),
                "python": None,
            }

        if not venv_python.exists():
            created = self._run_command(
                [bootstrap_python, "-m", "venv", str(venv_dir)],
                timeout=self.provider_repair_timeout_seconds,
            )
            if not created["ok"]:
                return {
                    "ok": False,
                    "detail": f"Failed to create MLX venv: {created['detail']}",
                    "venv": str(venv_dir),
                    "python": bootstrap_python,
                }

        upgraded = self._run_command(
            [str(venv_python), "-m", "pip", "install", "-U", "pip", "setuptools", "wheel"],
            timeout=self.provider_repair_timeout_seconds,
        )
        if not upgraded["ok"]:
            return {
                "ok": False,
                "detail": f"Failed to prepare MLX venv: {upgraded['detail']}",
                "venv": str(venv_dir),
                "python": str(venv_python),
            }

        installed = self._run_command(
            [str(venv_python), "-m", "pip", "install", *self._desired_mlx_packages()],
            timeout=self.provider_repair_timeout_seconds,
        )
        if not installed["ok"]:
            return {
                "ok": False,
                "detail": f"Failed to install MLX runtime packages: {installed['detail']}",
                "venv": str(venv_dir),
                "python": str(venv_python),
            }

        verified = self._run_command(
            [str(venv_python), "-c", "import mlx_lm; print('ok')"],
            timeout=30,
        )
        if not verified["ok"]:
            return {
                "ok": False,
                "detail": f"MLX runtime install finished but import still failed: {verified['detail']}",
                "venv": str(venv_dir),
                "python": str(venv_python),
            }

        return {
            "ok": True,
            "detail": "MLX runtime repaired in the dedicated venv.",
            "venv": str(venv_dir),
            "python": str(venv_python),
        }

    def _desired_mlx_packages(self) -> list[str]:
        mlx_version = self._distribution_version("mlx")
        mlx_lm_version = self._distribution_version("mlx-lm")
        return [
            f"mlx=={mlx_version}" if mlx_version else "mlx",
            f"mlx-lm=={mlx_lm_version}" if mlx_lm_version else "mlx-lm",
        ]

    def _distribution_version(self, name: str) -> str | None:
        try:
            return importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            return None

    def _bootstrap_python(self) -> str | None:
        candidates = [
            os.environ.get("AMANOBA_BOOTSTRAP_PYTHON"),
            shutil.which("python3"),
            sys.executable,
            "/opt/homebrew/bin/python3",
            "/usr/bin/python3",
        ]
        seen: set[str] = set()
        for candidate in candidates:
            if not candidate:
                continue
            if not os.path.exists(candidate) or not os.access(candidate, os.X_OK):
                continue
            resolved = os.path.realpath(candidate)
            if resolved in seen:
                continue
            seen.add(resolved)
            return candidate
        return None

    def _run_command(self, args: list[str], timeout: int) -> dict[str, Any]:
        try:
            result = subprocess.run(
                args,
                cwd=self.root,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return {"ok": False, "detail": f"timed out after {timeout} seconds: {' '.join(args)}"}
        if result.returncode == 0:
            return {"ok": True, "detail": (result.stdout or "").strip()}
        stderr = (result.stderr or "").strip()
        stdout = (result.stdout or "").strip()
        return {"ok": False, "detail": (stderr or stdout or f"exit code {result.returncode}")[:1200]}

    def _kickstart_label(self, label: str) -> None:
        uid = str(os.getuid())
        subprocess.run(["launchctl", "kickstart", "-k", f"gui/{uid}/{label}"], check=False, capture_output=True, text=True)

    def _active_mlx_worker_processes(self) -> list[dict[str, Any]]:
        result = subprocess.run(
            ["ps", "-axo", "pid=,etime=,command="],
            capture_output=True,
            text=True,
            check=False,
        )
        rows: list[dict[str, Any]] = []
        for line in (result.stdout or "").splitlines():
            line = line.strip()
            if not line or "course_quality_daemon.mlx_worker" not in line:
                continue
            parts = line.split(None, 2)
            if len(parts) < 3:
                continue
            try:
                pid = int(parts[0])
                etimes = self._parse_etime(parts[1])
            except ValueError:
                continue
            rows.append({"pid": pid, "etimes": etimes, "command": parts[2]})
        return rows

    def _kill_active_mlx_worker_processes(self) -> list[int]:
        killed: list[int] = []
        for proc in self._active_mlx_worker_processes():
            pid = int(proc.get("pid") or 0)
            if pid <= 0:
                continue
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


def run_watchdog(config_path: Path) -> None:
    config = Config.from_file(config_path.resolve())
    summary = CourseQualityWatchdog(config).run_once()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
