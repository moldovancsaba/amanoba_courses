# Local Course Quality Daemon

This tool gives you a local, continuous worker that:

- reads the live Amanoba MongoDB-backed app through the bridge in `/Users/moldovancsaba/Projects/amanoba/scripts/course-quality-live-bridge.ts`,
- detects weak lessons and invalid quiz questions,
- queues each fix as a separate task,
- processes exactly one task at a time,
- keeps running so new course packages or new language variants are picked up automatically,
- stays in low-capacity background mode between jobs,
- prefers local rewrite providers so it can continue working offline,
- writes a live feed of queued, running, completed, and failed jobs,
- exposes a local web dashboard as a control center.

## Files

- `course_quality_daemon/` — Python package
- `course_quality_daemon.example.json` — starter config
- `.course-quality/state.sqlite3` — local queue/state database created at runtime
- `.course-quality/backups/` — original live payload backups before any write
- `.course-quality/reports/status.json` — latest count summary
- `.course-quality/reports/feed.json` — machine-readable job feed
- `.course-quality/reports/feed.md` — human-readable job feed
- `.course-quality/reports/health.json` — local runtime/provider health
- `scripts/install-course-quality-launchagents.sh` — installs restart-proof background services

## Local runtime order

The worker now supports provider selection in this order by default:

1. `ollama`
2. `mlx`

That means:

- local `ollama` is used first for stable unattended queue work,
- local MLX Apertus stays available as a secondary installed runtime,
- Ollama runs with a low-power profile by default (`temperature 0.1`, `num_predict 384`, `num_ctx 2048`, `num_thread 2`),
- if there is no internet or no API key, queueing and dashboard still work,
- auto-rewrite falls back only if a real provider is actually available.

The code still keeps an internal null provider as a guard rail, but it is not part of the documented runtime stack and is not surfaced in the UI.

## Feedback feed

The job feed is split into four buckets:

- `queued` — work that is coming next
- `running` — the item currently being processed
- `completed` — most recently finished jobs
- `failed` — the Failed lane, which includes retry-failed, quarantined, and terminally failed jobs

Each entry contains the course, lesson, question or lesson target, timestamps, attempts, last error, and a Sovereign-style confidence/trust-tier judgement.

## Canonical content format

The live Amanoba app is **Markdown-first** for lessons.

- Lesson `content` is stored canonically as Markdown.
- Lesson `emailBody` is stored canonically as Markdown.
- Legacy HTML may exist in old records, but the app renders both through `contentToHtml`.
- The quality daemon must therefore write lessons back in Markdown form, not HTML-first form.

Canonical references:

- `docs/amanoba-course-content-standard-v1-0.md`
- `docs/course-package-format.md`
- `/Users/moldovancsaba/Projects/amanoba/app/lib/lesson-content.ts`
- `/Users/moldovancsaba/Projects/amanoba/app/lib/models/lesson.ts`

## Dashboard

Run the local control center:

```bash
python3 -m course_quality_daemon --config course_quality_daemon.json dashboard
```

Then open:

```text
http://127.0.0.1:8765
```

The dashboard lets you:

- watch queued, running, completed, failed, and archived jobs in kanban columns,
- inspect provider health,
- switch power mode between `gentle`, `balanced`, and `fast`,
- trigger a new scan,
- process one job manually,
- open a card in a modal to inspect before/after content,
- challenge a completed result with one comment so it goes back to `Coming Up`,
- search archived completed jobs directly from the local SQLite state.

The manual `run-once` action now returns immediately and only sends a compact summary payload back to the browser. The actual rewrite continues in the background.
The dashboard starts manual work by spawning a separate one-shot Python process, not an in-process thread, so long lesson rewrites cannot block the web request or freeze the control center.
All worker entrypoints also share a filesystem lock at `.course-quality/process.lock`, so only one `run-once` or daemon process can own the queue at a time.

Kanban column behavior:

- `Coming Up`: pending tasks that have not been processed yet
- `Active Now`: currently running task
- `Done`: last 10 completed tasks
- `Failed`: last 10 visible problem tasks, including retry-failed, quarantined, and terminal failures
- `Archived`: older completed tasks, plus searchable completed history

## Background services

Install restart-proof macOS launch agents:

```bash
bash scripts/install-course-quality-launchagents.sh
```

Check status:

```bash
bash scripts/status-course-quality-launchagents.sh
```

Installed services:

- `com.amanoba.coursequality.worker`
- `com.amanoba.coursequality.dashboard`
- `com.amanoba.coursequality.watchdog`
- `com.amanoba.coursequality.ollama` if `ollama` exists locally

Service behavior:

- `dashboard` uses `RunAtLoad` and `KeepAlive`
- `ollama` uses `RunAtLoad` and `KeepAlive`
- `worker` uses `RunAtLoad` and `StartInterval`
- `watchdog` uses `RunAtLoad` and `StartInterval`

That means the UI/runtime services stay resident, while the worker and watchdog are relaunched on schedule and at login.
The worker is also started with `nice -n 10` so it runs continuously at lower scheduler priority.

## Watchdog

The system now has a separate OS-level watchdog module.

It is intentionally not the main worker. Its only job is orchestration and repair:

- runs as `com.amanoba.coursequality.watchdog`
- starts at login / OS launch
- runs as a fresh launchd cycle every `watchdog.check_interval_seconds`
- performs a full service kickstart every `watchdog.full_restart_interval_seconds`
- kills stale `run-once` worker processes
- clears stale `.course-quality/process.lock`
- recovers tasks left in `running`
- restarts dashboard if `/api/health` is not reachable
- restarts Ollama if the local endpoint is down
- kickstarts the worker when queue execution is not progressing
- writes its own report to `.course-quality/reports/watchdog.json`

Timeout and repeated-bounce policy:

- every timeout is classified into a structured RCA record on the task
- timeout incidents immediately trigger a watchdog cycle
- that watchdog cycle checks worker/dashboard/Ollama health, clears stale locks, kills stale worker runs, and kickstarts recovery
- if the same card bounces back twice, it is moved to `quarantined`
- quarantined cards stay visible in the `Failed` lane with human review required
- the modal feedback history receives a system note so a human can challenge or inspect it directly

Manual watchdog run:

```bash
python3 -m course_quality_daemon --config course_quality_daemon.json watchdog
```

Watchdog logs:

- `.course-quality/launchd/watchdog.out.log`
- `.course-quality/launchd/watchdog.err.log`

## One-Click Launchers

To launch the app the same way as `{hatori}` or `{reply}`, use either root-level launcher:

```bash
cd /Users/moldovancsaba/Projects/amanoba-courses
./start_amanoba.command
```

or double-click:

- `start_amanoba.command`
- `Launch Amanoba.command`

These launchers refresh the background services, wait for dashboard health, and open `http://127.0.0.1:8765`.

## Quick start

```bash
cd /Users/moldovancsaba/Projects/amanoba-courses
cp course_quality_daemon.example.json course_quality_daemon.json
python3 -m course_quality_daemon --config course_quality_daemon.json scan
python3 -m course_quality_daemon --config course_quality_daemon.json health
python3 -m course_quality_daemon --config course_quality_daemon.json feed --limit 20
python3 -m course_quality_daemon --config course_quality_daemon.json dashboard
```

## Live DB mode

The default config in this repo is now live-DB mode:

- `source_mode: amanoba_live_db`
- `live.app_root: /Users/moldovancsaba/Projects/amanoba`
- `live.bridge_script: scripts/course-quality-live-bridge.ts`
- `live.bridge_timeout_seconds: 120`

The daemon does **not** download the whole DB into memory at once.

Instead it:

- asks the live bridge for a small next batch,
- audits only that batch,
- marks already-valid items as reviewed in the live DB,
- queues only invalid items locally,
- processes one queued item at a time,
- writes approved fixes back to the live DB immediately.

The live bridge calls are hard-timed:

- scan/fetch/apply/mark-reviewed fail fast after `live.bridge_timeout_seconds`
- timed-out bridge calls return an explicit task error instead of hanging the queue forever
- each task execution is also hard-capped by `max_task_runtime_seconds`
- timed-out lesson/question runs become failed or retry-failed tasks instead of staying `running`
- repeated timeout/retry bounce-backs are quarantined after `watchdog.quarantine_after_failures`

## Local versioning

This workspace currently does not have Git metadata available, so local version provenance cannot be inferred from `git status` or `git log`.

For this project, the operational source of truth is:

- the live code under `course_quality_daemon/`
- the active config in `course_quality_daemon.json`
- the launch-agent definitions in `scripts/install-course-quality-launchagents.sh`
- the runtime reports under `.course-quality/reports/`

Do not assume commit-based provenance unless this workspace is reattached to a Git repository.

## Recommended rollout

- Make sure `ollama` has a local model pulled.
- Run a few `run-once --max-items 1` cycles and inspect the rewritten output.
- When the outputs are stable, install the launch agents and leave the system running in the background.
- Keep `idle_sleep_seconds` and `post_task_sleep_seconds` non-zero so the worker remains gentle on the machine.
- If you want strict 5-minute cadence, set `queue_check_interval_seconds` to `300`. The daemon will check every 5 minutes whether any task is already `running`; if none is active, it starts exactly one next queued task.

Current known hard failure mode to watch:

- if a lesson rewrite provider returns article/blog/webpage/schema.org JSON instead of Amanoba lesson JSON, the daemon rejects it and the card returns to `Failed` / `retry-failed`
