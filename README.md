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
- `worker`: `RunAtLoad` + `KeepAlive`
- `watchdog`: `RunAtLoad` + `StartInterval`

So the UI/runtime stay resident, the worker stays up as one continuous daemon, and the watchdog relaunches on schedule and at login.
The queue is guarded by a shared process lock, so only one QC worker process can own job execution at a time.

The watchdog is a separate supervisor, not the worker itself. It runs from launchd at login and on a repeating schedule, repairs stale locks and stuck tasks, kills frozen worker runs, enforces MLX/Apertus as the primary writer provider, and kickstarts the worker/dashboard/Ollama when health checks fail.
Timeouts now create a task-level RCA record, trigger an immediate watchdog incident cycle, and quarantine a card after repeated bounce-backs so it stays visible for human review instead of looping forever.

The Failed review surface is broader than terminal failure. It includes active failed/problem cases, and quarantined cards remain explicitly visible for human review instead of silently re-entering the queue.

## Power Modes

The dashboard supports:

- `gentle` for always-on low-capacity background work
- `balanced` for normal continuous operation
- `fast` for higher-throughput local rewriting

The rail summary now also shows the effective lesson rewrite token budget, because the lesson-repair path can differ from the base provider profile shown in older builds.

## Local Runtime Order

The worker now supports provider selection in this order by default:

1. `mlx`
2. `ollama`

That means:

- MLX/Apertus is the primary writer for unattended QC,
- Ollama is fallback only when MLX is unavailable or temporarily cooled down after repeated runtime failures,
- the watchdog treats `selected provider != mlx` as a repairable incident and tries to restore MLX automatically,
- the MLX path runs through the dedicated [`.venv-mlx/bin/python`](/Users/moldovancsaba/Projects/amanoba_courses/.venv-mlx/bin/python) interpreter so health checks and generation use the same runtime.

Current persisted mode lives in:

- [`course_quality_daemon.json`](course_quality_daemon.json)

## Control Center

The dashboard shows:

- `Course Creator` page for sovereign course creation runs
- `Quality Control` page for live lesson/question QC
- queued jobs
- running job
- completed jobs
- failed jobs
- quarantined jobs
- provider health
- current power mode
- provider timings on task detail when a rewrite attempt ran

Useful URLs:

- dashboard: `http://127.0.0.1:8765`
- health: `http://127.0.0.1:8765/api/health`
- feed: `http://127.0.0.1:8765/api/feed?limit=10`

## Sovereign Course Creator

The local browserview now includes a separate `Course Creator` surface in the left rail.

Implemented creator stages:

1. `Topic Intake`
2. `Research`
3. `Blueprint`
4. `Lesson Generation`
5. `Quiz Generation`
6. `QC Review`
7. `Draft To Live`

Current delivered behavior:

- create a run from `topic`, `target language`, and `research mode`
- collect and show a source pack for research-enabled runs
- CRUD the source pack directly in the local creator modal:
  - create sources
  - review sources
  - update sources
  - delete sources
  - refresh the source pack from research
- mark sources as:
  - `preferred`
  - `neutral`
  - `rejected`
- carry those source decisions through refresh so user curation persists
- show a `Grounding Basis` summary in the creator artifact view
- generate a true 30-day blueprint from the approved research artifact
- generate a 30-day lesson batch draft from the approved blueprint
- generate a quiz batch draft from the approved lesson batch
- inject the approved creator draft into the local QC queue at top priority during `QC Review`
- create `30` creator lesson QC tasks and `210` creator question QC tasks for a full 30-day run
- write completed creator QC results back into the creator run payload instead of publishing them directly to the live DB
- block `QC Review` acceptance until every injected creator QC task is completed and there are no failed or quarantined creator QC tasks left
- generate a `Draft To Live` readiness summary from the current QC completion state
- export a real draft course package (`packageVersion 2.0`) from the reviewed creator payload during `Draft To Live`
- import the exported package into Amanoba as a draft/inactive course on explicit user action
- publish the imported draft into Amanoba on a second explicit user action
- rollback a published Amanoba course back to draft/inactive from the same local creator run
- delete the imported Amanoba draft from the same local creator run when the downstream handoff should be removed entirely
- require package export, draft import, and explicit live publish before `Draft To Live` can be accepted
- enforce checkpoint gates before downstream generation
- show artifact summaries in the creator modal so coverage is visible without reading only raw stage markdown

Current creator UX behavior:

- left rail separates `Course Creator` from `Quality Control`
- the `Course Creator` page now uses a kanban-style pipeline like QC
- runs are shown in stage columns:
  - `Research`
  - `Blueprint`
  - `Lessons`
  - `Quizzes`
  - `QC Review`
  - `Draft To Live`
  - `Done`
- creator run cards now show readiness badges before opening:
  - stage state
  - QC state
  - release state
- the creator modal shows a `Lifecycle Checklist` so the user can see readiness state at a glance
- the modal shows `What Happens Next` to explain the next valid action and downstream consequence
- the modal shows a stage-specific warning so approval risk is explicit
- the artifact summary now highlights:
  - `Decision Risk`
  - `QC Readiness`
  - `Release Readiness`
- actions are grouped by intent:
  - `Stage Workflow`
  - `Downstream Release`
  - `Recovery Controls`
- actions enable only when the current stage and lifecycle state allow them
- rollback and delete-import are isolated from publish actions so release and recovery cannot be confused
- the creator modal is stage-focused by default:
  - `Research` shows the research brief and curated source pack only
  - `Blueprint` shows one outline day at a time with next/previous day navigation
  - `Lesson Generation` shows one lesson at a time with next/previous lesson navigation
  - `Quiz Generation` shows one quiz question at a time with next/previous question navigation
  - `QC Review` starts as `QC Setup` until the handoff is created, then switches into QC progress state
  - `Draft To Live` shows only release state, package, import, and publish readiness
- the modal does not repeat the full stage list, because the kanban column already tells the user where the run currently sits
- raw stage editing is hidden by default and opens only when the user explicitly chooses `Show Edit Panel`
- setup and release states hide irrelevant controls until those controls are actually valid

The creator workflow lives in the local `amanoba_courses` control center, not in `amanoba.com`.
`amanoba.com` remains the downstream final editing/publishing surface for small modifications after draft creation and QC.

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
