# Current SSOT

This document defines the current source-of-truth model for `amanoba_courses`.

If an older document, historical handover, or stale note conflicts with this file, treat that older material as supporting context only until it is updated.

## Code and runtime

The active product workspace is:

- `/Users/chappie/Projects/amanoba_courses`

The active Git repository is:

- `moldovancsaba/amanoba_courses`
- `https://github.com/moldovancsaba/amanoba_courses.git`

The active runtime truth for the local quality system is:

- `course_quality_daemon/`
- `course_quality_daemon.json`
- `scripts/install-course-quality-launchagents.sh`
- `.course-quality/reports/health.json`
- `.course-quality/reports/feed.json`
- `.course-quality/reports/watchdog.json`

The active local product surface is the browserview control center at:

- `http://127.0.0.1:8765`

Current local pages:

- `Course Creator`
- `Quality Control`

Current runtime version:

- `Amanoba v0.2.0`

Current model roster and residency surface:

- compact `Model Roster` in the dashboard
- local QC writer providers:
  - `mlx` as primary
  - `ollama` as warm fallback
- resident creator roles:
  - `DRAFTER` on `127.0.0.1:8080` using `Gemma 3 270M`
  - `WRITER` on `127.0.0.1:8081` using `Granite 4.0 350M (H)`
  - `JUDGE` on `127.0.0.1:8082` using `Qwen 2.5 0.5B`

Current live bridge dependency truth:

- the live bridge script is `/Users/chappie/Projects/amanoba/scripts/course-quality-live-bridge.ts`
- the live Amanoba app is linked to Vercel project `narimato/amanoba`
- the fresh-machine bootstrap path for the live app is:
  - `vercel login`
  - `vercel link --yes --scope narimato --project amanoba`
  - `vercel env ls`
  - `vercel env pull .env.local --yes`
- `/Users/chappie/Projects/amanoba/.env.local` must contain a real `MONGODB_URI` and `DB_NAME="amanoba"`
- if `MONGODB_URI` is missing, the worker must report `waiting-dependency` instead of pretending the queue is healthy
- current continuous daemon cadence is `60` seconds for scan, queue check, idle sleep, and post-task sleep

Current creator page model:

- the local `Course Creator` page is a kanban-style stage pipeline
- runs are displayed in stage columns instead of only a flat list
- the stage columns are:
  - `Research`
  - `Blueprint`
  - `Lessons`
  - `Quizzes`
  - `QC Review`
  - `Draft To Live`
  - `Done`
- the research source pack is CRUD-capable inside the local creator modal
- the source pack also supports user review states:
  - `preferred`
  - `neutral`
  - `rejected`
- source review state persists across source refresh
- the creator modal is stage-focused:
  - research review shows the research brief and curated sources only
  - blueprint review shows one outline day at a time
  - lesson review shows one lesson at a time
  - quiz review shows one question at a time
  - QC review starts as `QC Setup` until the handoff exists, then shows QC progress state
  - draft-to-live review shows only release/package/import/publish state
- the modal does not repeat the full pipeline stage list once the run is opened
- raw artifact editing is hidden by default and is exposed only by explicit user action
- setup and release states hide irrelevant controls until they are valid

Current delivered creator handoff:

- approved creator drafts enter the local QC queue during `QC Review`
- creator QC tasks are top-priority local draft tasks, not live Amanoba DB mutations
- completed creator QC results are written back into the creator run payload
- `Draft To Live` now includes the full downstream gate:
  - export local v2 draft package
  - import package into Amanoba as draft/inactive
  - publish the imported draft on explicit user action
  - rollback the published course back to draft/inactive if needed
  - delete the imported Amanoba draft if the downstream handoff must be removed
  - only then allow final local acceptance
  - present creator controls in lifecycle-aware UX groups:
    - `Stage Workflow`
    - `Downstream Release`
    - `Recovery Controls`
  - show creator run readiness badges on the run cards before the user opens a run
  - show a `Lifecycle Checklist` and `What Happens Next` banner in the local creator modal
  - show explicit stage-risk messaging and readiness summaries for:
    - decision risk
    - QC readiness
    - release readiness
  - disable actions until their stage or lifecycle prerequisites are satisfied

## GitHub planning and backlog

GitHub issue planning for `amanoba_courses` does **not** live in the product repository.

Use these as the planning SSOT:

- issue repository: `moldovancsaba/mvp-factory-control`
- project board: `https://github.com/users/moldovancsaba/projects/1`

Operational rule:

- search for existing ideabank, roadmap, dependency, and delivery issues in `mvp-factory-control`
- create new planning issues for `amanoba_courses` in `mvp-factory-control`
- manage issue status, dependencies, and board placement there
- do not create a second planning backlog inside `moldovancsaba/amanoba_courses` unless explicitly requested

## Documentation governance

Documentation is only useful if it reflects the system that exists now.

Therefore:

- current-behavior docs are authoritative only when they match the code and live runtime
- stale docs should be updated, superseded, or treated as historical/supporting
- if a doc references the old hyphenated workspace path, update it to the Git-backed underscore path
- if a doc references `/Users/moldovancsaba/Projects/amanoba_courses`, update it to `/Users/chappie/Projects/amanoba_courses`
- if a doc describes an old workflow, it must not be used as the delivery source without first reconciling it to the current system

## Course content and publishing

For lesson and quiz content:

- live system compatibility is defined by `/Users/chappie/Projects/amanoba`
- canonical content/course standards remain in this repo under `docs/`
- sovereign course-creator compatibility is defined in `docs/reference/sovereign-course-creator-compatibility-contract.md`
- when there is a conflict, the current application behavior plus the explicitly designated SSOT docs win

## Working rule

When planning or executing future work:

1. confirm the current code/runtime behavior
2. check whether the relevant doc is current or stale
3. update obsolete documentation as part of the change
4. search and manage product issues in `mvp-factory-control`
