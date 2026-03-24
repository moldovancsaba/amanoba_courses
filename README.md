# Amanoba Course Quality Control Center

Local-first control center for the live Amanoba system. It reads the live MongoDB-backed Amanoba app through a bridge, queues weak lessons and quiz questions, fixes one item at a time, and keeps running in the background with a local web control center.

## Launch Like `{hatori}` or `{reply}`

Primary one-click launcher:

- [`start_amanoba.command`](start_amanoba.command)

Also available with the `{hatori}`-style name:

- [`Launch Amanoba.command`](Launch%20Amanoba.command)

Both launchers:

- refresh the background services,
- make sure the local dashboard is reachable,
- open the control center in your browser.

The dashboard bootstraps with a live server-side snapshot, so the board renders current jobs immediately even before the first browser refresh call completes.

After launch, open:

- `http://127.0.0.1:8765`

## macOS Menubar App

Install:

```bash
cd /Users/moldovancsaba/Projects/amanoba_courses
bash tools/macos/AmanobaMenubar/install_AmanobaMenubar.sh
```

Run:

```bash
open ~/Applications/AmanobaMenubar.app
```

Install and run in one step:

```bash
bash tools/macos/AmanobaMenubar/run_AmanobaMenubar.sh
```

Menu app guide:

- [`docs/menubar-user-guide.md`](docs/menubar-user-guide.md)

## Quick Start

```bash
cd /Users/moldovancsaba/Projects/amanoba_courses
./start_amanoba.command
```

## Background Service Mode

Install or refresh restart-proof macOS launch agents:

```bash
cd /Users/moldovancsaba/Projects/amanoba_courses
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
- `com.amanoba.coursequality.ollama`

Service behavior:

- `dashboard`: `RunAtLoad` + `KeepAlive`
- `ollama`: `RunAtLoad` + `KeepAlive`
- `worker`: `RunAtLoad` + `StartInterval`
- `watchdog`: `RunAtLoad` + `StartInterval`

So the UI/runtime stay resident, while the worker and watchdog relaunch on schedule and at login.
Manual `Process One Job` runs also use a separate one-shot subprocess now, so the browser action returns immediately and does not depend on a long-running in-process Python thread.
The queue is guarded by a shared process lock, so only one worker process can own job execution at a time.

The watchdog is a separate supervisor, not the worker itself. It runs from launchd at login and on a repeating schedule, repairs stale locks and stuck tasks, kills frozen worker runs, and kickstarts the worker/dashboard/Ollama when health checks fail.
Timeouts now create a task-level RCA record, trigger an immediate watchdog incident cycle, and quarantine a card after repeated bounce-backs so it stays visible for human review instead of looping forever.

The Failed lane is broader than terminal failure. It includes retry-failed cards, quarantined cards, and terminally failed cards so humans can review all active problem cases in one place.

## Power Modes

The dashboard supports:

- `gentle` for always-on low-capacity background work
- `balanced` for normal continuous operation
- `fast` for higher-throughput local rewriting

Current persisted mode lives in:

- [`course_quality_daemon.json`](course_quality_daemon.json)

## Control Center

The dashboard shows:

- queued jobs
- running job
- completed jobs
- failed jobs
- provider health
- current power mode

Useful URLs:

- dashboard: `http://127.0.0.1:8765`
- health: `http://127.0.0.1:8765/api/health`
- feed: `http://127.0.0.1:8765/api/feed?limit=10`

## Canonical format

Amanoba lesson storage is `Markdown-first`, not `HTML-first`.

- lesson `content`: Markdown
- lesson `emailBody`: Markdown
- legacy HTML is tolerated by the app renderer, but it is not the canonical write format

Source of truth:

- [`docs/amanoba-course-content-standard-v1-0.md`](docs/amanoba-course-content-standard-v1-0.md)
- [`docs/course-package-format.md`](docs/course-package-format.md)
- [`/Users/moldovancsaba/Projects/amanoba/app/lib/lesson-content.ts`](/Users/moldovancsaba/Projects/amanoba/app/lib/lesson-content.ts)

## More Documentation

- [`docs/current-ssot.md`](docs/current-ssot.md)
- [`docs/local-course-quality-daemon.md`](docs/local-course-quality-daemon.md)
- [`docs/local-runtime-evaluation.md`](docs/local-runtime-evaluation.md)
- [`docs/system-versioning.md`](docs/system-versioning.md)
- [`docs/create-a-course-handover.md`](docs/create-a-course-handover.md)

## GitHub SSOT For Issues

This repository is the product codebase, but GitHub issue planning and management do **not** live here.

Use these as the operational issue SSOT:

- issue repository: [`moldovancsaba/mvp-factory-control`](https://github.com/moldovancsaba/mvp-factory-control)
- project board: [`MVP Factory Board`](https://github.com/users/moldovancsaba/projects/1)

Rules:

- search, create, update, and close product issues in `mvp-factory-control`
- use the project board as the shared product planning surface
- treat issue cards there as the authoritative backlog for `amanoba_courses`
- do not create parallel planning issues in `moldovancsaba/amanoba_courses` unless explicitly requested
