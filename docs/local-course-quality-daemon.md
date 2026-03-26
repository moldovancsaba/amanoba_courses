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

## Status and SSOT

- **Status:** current operational runtime doc
- **Document owner:** Amanoba course/QC maintainers
- **Runtime SSOT:** `docs/current-ssot.md`
- **Conflict rule:** if the live daemon/dashboard/watchdog behavior differs, update this document before using it as an operational reference

## Fresh machine bootstrap

If you are installing the QC app on a new Mac or restoring a machine from scratch, bootstrap the local env file from the linked Vercel project before you start the daemon.

Required local env file:

- `.env.local`

Minimum required values for the QC runtime:

- `MONGODB_URI`
- `DB_NAME=amanoba`
- optional: `OPENAI_API_KEY` if you want the OpenAI fallback path enabled

Supported bootstrap flow:

```bash
vercel login
vercel link
vercel env ls
vercel env pull .env.local
```

Notes:

- `vercel link` ties the local workspace to the correct Vercel project.
- `vercel env pull .env.local` pulls the project environment variables that the local scripts need into the `.env.local` file that the QC runtime already reads.
- If the machine is missing `.env.local`, this is the supported way to recreate it from the project’s Vercel environment.
- After pulling env vars, verify that `MONGODB_URI` and `DB_NAME` are present before starting the launch agents.

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

1. `mlx`
2. `ollama`

That means:

- local MLX/Apertus is the primary unattended writer path,
- lesson/question QC now first tries a specialist local micro-pipeline:
  - `drafter` = Gemma 3 270M
  - `writer` = Granite 4.0 H 350M
  - `judge` = Qwen 2.5 0.5B
- specialist QC output is still accepted only if the normal validator gates pass,
- Ollama is used only as fallback when MLX is unavailable or temporarily cooled down after repeated runtime failures,
- MLX runs through the dedicated [`.venv-mlx/bin/python`](/Users/moldovancsaba/Projects/amanoba_courses/.venv-mlx/bin/python) interpreter,
- the resident creator roles stay online as separate MLX servers and are shown in the dashboard as a single compact model roster:
  - drafter on `127.0.0.1:8080`
  - writer on `127.0.0.1:8081`
  - judge on `127.0.0.1:8082`
- the watchdog enforces MLX as the primary writer and treats fallback mode as a repairable incident,
- Ollama model-level timeout fallback is still used when the Ollama primary/fallback chain is active,
- Ollama runs with a low-power profile by default when it is used as fallback (`temperature 0.1`, `num_predict 384`, `num_ctx 2048`, `num_thread 2`),
- the dashboard power summary now also shows the effective lesson rewrite token budget,
- rewrite calls fail over across configured providers instead of waiting forever on the first healthy provider,
- if there is no internet or no API key, queueing and dashboard still work,
- auto-rewrite falls back only if a real provider is actually available.

The code still keeps an internal null provider as a guard rail, but it is not part of the documented runtime stack and is not surfaced in the UI.

## Feedback feed

The job feed is split into four buckets:

- `queued` — work that is coming next
- `running` — the item currently being processed
- `completed` — most recently finished jobs
- `failed/quarantined review` — visible problem cases that still need inspection or human action

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

- switch between `Course Creator` and `Quality Control` from the left rail,
- create sovereign course-creator runs from `topic`, `target language`, and `research mode`,
- generate and edit stage artifacts inside the creator modal,
- watch queued, running, completed, failed, and archived jobs in kanban columns,
- inspect provider health and the compact model roster,
- switch power mode between `gentle`, `balanced`, and `fast`,
- trigger a new scan,
- watch the single long-lived QC worker progress,
- open a card in a modal to inspect before/after content,
- challenge a completed result with one comment so it goes back to `Coming Up`,
- search archived completed jobs directly from the local SQLite state.

Creator UX behavior:

- `Course Creator` and `Quality Control` are separate left-rail pages
- the `Course Creator` page uses a kanban-style pipeline so the user can see where each run currently sits
- creator stages now publish structured handoff data for `blueprint`, `lesson_generation`, and `quiz_generation`
- QC handoff reads that structured data instead of depending only on reparsing the visible stage markdown
- the UI can show `QC handoff ready` or `QC handoff blocked` from that contract directly
- creator columns are:
  - `Research`
  - `Blueprint`
  - `Lessons`
  - `Quizzes`
  - `QC Review`
  - `Draft To Live`
  - `Done`
- creator run cards expose readiness badges before the user opens a run:
  - stage state
  - QC state
  - release state
- creator cards are intentionally simple:
  - current stage
  - last action
  - updated time
- the creator modal is decision-point driven:
  - show only the current stage content that needs review
  - show only the valid actions for that stage
  - hide internal run metadata and duplicate pipeline/status noise
- the user action model is simple across the pipeline:
  - `Accept`
  - `Modify`
  - `Delete`
- `Accept` moves to the next stage and starts the next AI step automatically
- `Modify` moves back one stage and starts rework automatically using the user note
- `Delete` moves the run to trash
- the creator modal is stage-focused by default:
  - `Research` shows the research brief and source pack only
  - `Blueprint` shows one outline day at a time
  - `Lesson Generation` shows one lesson at a time
  - `Quiz Generation` shows one question at a time
  - `QC Review` starts as `QC Setup` until creator QC tasks exist, then switches into live QC progress
  - `Draft To Live` shows the release decision only
- the modal does not repeat the full stage list, because the kanban column already provides the run position
- raw artifact editing is hidden by default and appears only after the user selects `Show Edit Panel`
- setup and release states hide invalid controls until they become relevant
- buttons are state-aware and disabled when a stage or lifecycle precondition is not satisfied
- destructive recovery actions are visually separated from publish actions

The QC system now runs as a single long-lived daemon process under launchd.
The dashboard does not own a second in-process worker thread, and the queue is guarded by `.course-quality/process.lock`, so only one QC worker process can own execution at a time.

Kanban column behavior:

- `Coming Up`: pending tasks that have not been processed yet
- `Active Now`: currently running task
- `Done`: last 10 completed tasks
- `Failed`: last 10 visible problem tasks, including quarantined and terminal failure cases
- `Archived`: older completed tasks, plus searchable completed history

Creator stage behavior:

- `Research`: source-aware research brief with visible source pack
- the source pack is user-managed inside the local creator modal:
  - add source
  - edit source
  - delete source
  - refresh source pack from research
- each source can also be marked as:
  - `preferred`
  - `neutral`
  - `rejected`
- source preference and rejection survive source refresh
- `Blueprint`: 30-day architecture derived from the approved research artifact
- `Lesson Generation`: 30-day lesson draft batch derived from the approved blueprint
- `Quiz Generation`: quiz draft batch derived from the approved lesson batch
- `QC Review`: injects approved creator lesson/question drafts into the local QC queue at top priority
- `Draft To Live`: final human gate with a QC-readiness summary, exportable draft package, explicit Amanoba draft import, explicit live publish control, and downstream rollback/delete controls

Checkpoint gates are enforced inside the local workflow:

- blueprint generation requires approved research
- lesson generation requires approved blueprint
- quiz generation requires approved lesson generation
- QC Review generation requires approved quiz generation
- QC Review acceptance requires all injected creator QC tasks to be completed with no failed/quarantined creator QC tasks remaining
- Draft To Live acceptance requires:
  - an exported draft package
  - an explicit draft import into Amanoba
  - an explicit live publish action in Amanoba
- if the user rolls back or deletes the downstream Amanoba course, the local creator run reopens at `Draft To Live`

UX rule:

- the UI must only present actions that match the current lifecycle state
- the user keeps explicit control over every irreversible step:
  - stage acceptance
  - draft export
  - Amanoba draft import
  - live publish
  - rollback
  - delete import

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
- `worker` uses `RunAtLoad` and `KeepAlive`
- `watchdog` uses `RunAtLoad` and `StartInterval`

That means the UI/runtime services stay resident, the worker stays up continuously, and the watchdog is relaunched on schedule and at login.
The worker is also started with `nice -n 10` so it runs continuously at lower scheduler priority.

## Watchdog

The system now has a separate OS-level watchdog module.

It is intentionally not the main worker. Its only job is orchestration and repair:

- runs as `com.amanoba.coursequality.watchdog`
- starts at login / OS launch
- runs as a fresh launchd cycle every `watchdog.check_interval_seconds`
- performs a full service kickstart every `watchdog.full_restart_interval_seconds`
- kills stale `run-once` worker processes
- kills stuck `course_quality_daemon.mlx_worker` subprocesses when MLX has fallen into a bad state
- clears stale `.course-quality/process.lock`
- recovers tasks left in `running`
- restarts dashboard if `/api/healthz` is not reachable
- restarts Ollama if the local endpoint is down
- kickstarts the worker when queue execution is not progressing
- checks both the watchdog runtime snapshot and the dashboard runtime snapshot
- treats `selected provider != mlx` as an incident when MLX is available
- restarts the worker/dashboard so MLX becomes the selected provider again
- writes its own report to `.course-quality/reports/watchdog.json`

Timeout and repeated-bounce policy:

- every timeout is classified into a structured RCA record on the task
- timeout incidents immediately trigger a watchdog cycle
- that watchdog cycle checks worker/dashboard/Ollama health, clears stale locks, kills stale worker runs, repairs MLX runtime issues, and kickstarts recovery
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
cd /Users/moldovancsaba/Projects/amanoba_courses
./start_amanoba.command
```

or double-click:

- `start_amanoba.command`
- `Launch Amanoba.command`

These launchers refresh the background services, wait for dashboard health, and open `http://127.0.0.1:8765`.

## Quick start

```bash
cd /Users/moldovancsaba/Projects/amanoba_courses
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
- timed-out lesson/question runs are recorded with RCA and moved out of `running`
- repeated timeout/retry bounce-backs are quarantined after `watchdog.quarantine_after_failures`
- obviously poor lessons now skip the wasteful normal-rewrite-first path and go straight to reconstruction
- task detail can include provider timing traces so slow providers are visible in the UI

## Local versioning

This workspace is Git-backed at:

- `moldovancsaba/amanoba_courses`
- `https://github.com/moldovancsaba/amanoba_courses.git`

For this project, the operational runtime source of truth is:

- the live code under `course_quality_daemon/`
- the active config in `course_quality_daemon.json`
- the launch-agent definitions in `scripts/install-course-quality-launchagents.sh`
- the runtime reports under `.course-quality/reports/`

Menubar build version:

- `Amanoba v0.2.0`

## Current dashboard surface

- a single `Model Roster` row replaces the older split residency/runtime panels
- the roster shows:
  - `DRAFTER`
  - `WRITER`
  - `JUDGE`
  - `mlx`
  - `ollama`
- each model entry uses short human-readable labels only, not filesystem paths

GitHub issue planning source of truth is separate:

- issue repository: `moldovancsaba/mvp-factory-control`
- project board: `https://github.com/users/moldovancsaba/projects/1`

## Recommended rollout

- Make sure MLX/Apertus is installed in [`.venv-mlx`](/Users/moldovancsaba/Projects/amanoba_courses/.venv-mlx) and `ollama` has its fallback models pulled.
- Run the dashboard and inspect a few real rewritten outputs while MLX is selected as the writer.
- When the outputs are stable, install the launch agents and leave the system running in the background.
- Keep `idle_sleep_seconds` and `post_task_sleep_seconds` non-zero so the worker remains gentle on the machine.
- If you want a gentler or more aggressive scan cadence, tune `queue_check_interval_seconds`, `idle_sleep_seconds`, and the watchdog intervals in `course_quality_daemon.json`.

Current known hard failure mode to watch:

- if a lesson rewrite provider returns article/blog/webpage/schema.org JSON instead of Amanoba lesson JSON, the daemon rejects it and the card stays visible for review or quarantine instead of silently looping
