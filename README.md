# Amanoba Course Quality Control Center

Local-first control center for the live Amanoba system. It reads the live MongoDB-backed Amanoba app through a bridge, queues weak lessons and quiz questions, fixes one item at a time, and keeps running in the background with a local web control center.

Current operating shape:

- resident MLX creator roles:
  - drafter on `8080`
  - writer on `8081`
  - judge on `8082`
- Ollama fallback kept warm with `keep_alive`
- launch agents wrapped with `caffeinate -dimsu`
- menubar app trimmed to the real operator actions only
- current QC queue is English-only
- the dashboard shows one compact `Model Roster` row with the three resident roles plus `mlx` and `ollama`

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
cd "$HOME/Projects/amanoba_courses"
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
- resource check: `bash tools/macos/AmanobaMenubar/check_AmanobaMenubar_resources.sh`

User manual:

- [`docs/user-manual.md`](docs/user-manual.md)

Mac mini handoff:

- [`docs/mac-mini-install-handoff.md`](docs/mac-mini-install-handoff.md)

## Quick Start

```bash
cd "$HOME/Projects/amanoba_courses"
./start_amanoba.command
```

## Background Service Mode

Install or refresh restart-proof macOS launch agents:

```bash
cd "$HOME/Projects/amanoba_courses"
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
- `com.amanoba.coursequality.caffeinate`
- `com.amanoba.coursequality.ollama`
- `com.amanoba.coursequality.role.drafter`
- `com.amanoba.coursequality.role.writer`
- `com.amanoba.coursequality.role.judge`

Service behavior:

- `dashboard`: `RunAtLoad` + `KeepAlive`
- `ollama`: `RunAtLoad` + `KeepAlive`
- `worker`: `RunAtLoad` + `KeepAlive`
- `watchdog`: `RunAtLoad` + `StartInterval`
- `caffeinate`: `RunAtLoad` + `KeepAlive`

So the UI/runtime stay resident, the worker stays up as one continuous daemon, the watchdog relaunches on schedule and at login, and the Mac stays awake while the stack is active.
The current continuous daemon cadence is `60` seconds for scan, queue check, idle sleep, and post-task sleep, so the worker keeps advancing without five-minute idle gaps.
The queue is guarded by a shared process lock, so only one QC worker process can own job execution at a time.

The watchdog is a separate supervisor, not the worker itself. It runs from launchd at login and on a repeating schedule, repairs stale locks and stuck tasks, kills frozen worker runs, enforces MLX/Apertus as the primary writer provider, and kickstarts the worker/dashboard/Ollama when health checks fail.
Timeouts now create a task-level RCA record, trigger an immediate watchdog incident cycle, and quarantine a card after repeated bounce-backs so it stays visible for human review instead of looping forever.
The watchdog also rewarms resident creator roles when memory pressure rises, instead of leaving the runtime in a degraded but silent state.

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
- lesson/question QC now first tries a local specialist micro-pipeline:
  - `drafter` = Gemma 3 270M
  - `writer` = Granite 4.0 H 350M
  - `judge` = Qwen 2.5 0.5B
- if the specialist path rejects or fails, QC falls back to the existing rewrite/failover path
- Ollama is fallback only when MLX is unavailable or temporarily cooled down after repeated runtime failures,
- the watchdog treats `selected provider != mlx` as a repairable incident and tries to restore MLX automatically,
- the MLX path runs through the dedicated [`.venv-mlx/bin/python`](.venv-mlx/bin/python) interpreter so health checks and generation use the same runtime.

Current persisted mode lives in:

- [`course_quality_daemon.json`](course_quality_daemon.json)

## Control Center

The dashboard shows:

- `Course Creator` page for sovereign course creation runs
- `Quality Control` page for live lesson/question QC
- one compact `Model Roster`
- queued jobs
- running job
- completed jobs
- failed jobs
- quarantined jobs
- provider health
- current power mode
- provider timings on task detail when a rewrite attempt ran
- the resident-server banner for drafter/writer/judge

Useful URLs:

- dashboard: `http://127.0.0.1:8765`
- health: `http://127.0.0.1:8765/api/health`
- feed: `http://127.0.0.1:8765/api/feed?limit=10`

Resident creator roles that should stay warm:

- `DRAFTER` on `127.0.0.1:8080` using `Gemma 3 270M`
- `WRITER` on `127.0.0.1:8081` using `Granite 4.0 350M (H)`
- `JUDGE` on `127.0.0.1:8082` using `Qwen 2.5 0.5B`

Live bridge dependency:

- the worker bridge lives in the live Amanoba app workspace under the current user home directory
- fresh-machine live app bootstrap uses:
  - `cd "$HOME/Projects/amanoba"`
  - `vercel login`
  - `vercel link --yes --scope narimato --project amanoba`
  - `vercel env ls`
  - `vercel env pull .env.local --yes`
  - `npm install`
- live queue advancement still requires a real `MONGODB_URI` and `DB_NAME="amanoba"` in `"$HOME/Projects/amanoba/.env.local"`
- when that secret is missing, the worker correctly reports `waiting-dependency`

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
- generate a true 30-day blueprint from the approved research artifact
- generate a 30-day lesson batch draft from the approved blueprint
- generate a quiz batch draft from the approved lesson batch
- inject the approved creator draft into the local QC queue at top priority during `QC Review`
- create `30` creator lesson QC tasks and `210` creator question QC tasks for a full 30-day run
- write completed creator QC results back into the creator run payload instead of publishing them directly to the live DB
- block `QC Review` acceptance until every injected creator QC task is completed and there are no failed or quarantined creator QC tasks left
- generate a `Draft To Live` readiness summary from the current QC completion state
- export a real draft course package (`packageVersion 2.0`) from the reviewed creator payload during `Draft To Live`
- store structured stage artifacts for `blueprint`, `lesson_generation`, and `quiz_generation` so QC handoff uses validated machine-readable rows instead of reparsing only the human-readable stage text
- expose QC handoff readiness in the creator payload and UI as `ready / missing stages / draft counts`
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
- creator run cards now stay minimal:
  - current state
  - language and research mode
  - last action
  - updated time
- the creator modal is decision-point driven:
  - show only the current stage content that needs review
  - show only the actions valid for that stage
  - keep the user action model simple:
    - `Accept`
    - `Modify`
    - `Delete`
- `Accept` moves the run to the next stage and starts the next AI step automatically
- `Modify` moves the run back one stage and starts rework automatically using the user note
- `Delete` moves the run to trash
- setup stages show one clear primary action, not a review UI
- release and recovery actions are shown only in `Draft To Live`
- the creator modal is stage-focused by default:
  - `Research` shows the research brief and curated source pack only
  - `Blueprint` shows one outline day at a time with next/previous day navigation
  - `Lesson Generation` shows one lesson at a time with next/previous lesson navigation
  - `Quiz Generation` shows one quiz question at a time with next/previous question navigation
  - `QC Review` starts as `QC Setup` until the handoff is created, then switches into QC progress state
  - `Draft To Live` shows only the downstream release decision
- the modal does not repeat the full stage list, because the kanban column already tells the user where the run currently sits
- setup stages hide irrelevant controls and show only the next required step

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
- the Amanoba app workspace `app/lib/lesson-content.ts` source referenced by the compatibility contract

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
