# Current SSOT

This document defines the current source-of-truth model for `amanoba_courses`.

If an older document, historical handover, or stale note conflicts with this file, treat that older material as supporting context only until it is updated.

## Status and SSOT

- **Status:** primary runtime SSOT
- **Document owner:** Amanoba maintainers
- **Supporting SSOTs:** `docs/system-versioning.md`, `docs/reference/sovereign-course-creator-compatibility-contract.md`, `docs/reference/quiz-quality-pipeline-handover.md`, `docs/reference/quiz-quality-pipeline-playbook.md`
- **Conflict rule:** if a code path or runtime surface disagrees with a supporting document, update the supporting document to match the current code and runtime before using it for delivery decisions

## Ownership and precedence

- **Document owner:** Amanoba maintainers
- **Primary runtime SSOT:** this file
- **Supporting SSOTs:** `docs/system-versioning.md`, `docs/reference/sovereign-course-creator-compatibility-contract.md`, `docs/reference/quiz-quality-pipeline-handover.md`, `docs/reference/quiz-quality-pipeline-playbook.md`
- **Conflict rule:** if a code path or runtime surface disagrees with a supporting document, update the supporting document to match the current code and runtime before using it for delivery decisions

## Code and runtime

The active product workspace is:

- `/Users/moldovancsaba/Projects/amanoba_courses`

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

Portable machine bootstrap:

- the local QC runtime expects `.env.local` to exist on each machine
- the supported way to recreate `.env.local` on a fresh machine is to link the repo to the correct Vercel project and run `vercel env pull .env.local`
- minimum local env values: `MONGODB_URI`, `DB_NAME=amanoba`
- optional fallback env value: `OPENAI_API_KEY`
- if the machine is missing `.env.local`, do not guess the secrets; pull them from the linked Vercel project instead

The active local product surface is the browserview control center at:

- `http://127.0.0.1:8765`

Current local pages:

- `Course Creator`
- `Quality Control`

Current runtime note:

- the QC runtime uses resident creator roles on `8080`, `8081`, and `8082`
- the menubar is intentionally minimal and uses short role labels only
- the dashboard shows one compact `Model Roster` row instead of the older split residency/runtime panels
- `Open Health JSON` is no longer part of the menubar surface

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
- creator-to-QC handoff is now backed by structured stage payloads
- QC repair now tries the local specialist stack before normal fallback
- the creator modal is decision-point driven:
  - research review shows the research brief and curated sources only
  - blueprint review shows one outline day at a time
  - lesson review shows one lesson at a time
  - quiz review shows one question at a time
  - QC review starts as `QC Setup` until the handoff exists, then shows QC progress state
  - draft-to-live review shows only the downstream release decision
- internal run ids, duplicate stage lists, and non-decision noise must stay out of the modal
- the modal does not repeat the full pipeline stage list once the run is opened
- the modal shows only the current stage content and the current valid actions
- the user action model is:
  - `Accept`
  - `Modify`
  - `Delete`
- `Accept` moves forward and starts the next AI step automatically
- `Modify` moves back one stage and starts rework automatically using the user note
- `Delete` moves the run to trash
- raw artifact editing is hidden by default and is exposed only by explicit user action
- setup and release states hide irrelevant controls until they are valid

Current operator-facing build version:

- `Amanoba v0.2.0`

Current delivered creator handoff:

- approved creator drafts enter the local QC queue during `QC Review`
- creator QC tasks are top-priority local draft tasks, not live Amanoba DB mutations
- completed creator QC results are written back into the creator run payload
- creator-to-QC handoff is now defined by structured artifact payloads, not only by parsing human-readable stage text
- `Draft To Live` now includes the full downstream gate:
  - export local v2 draft package
  - import package into Amanoba as draft/inactive
  - publish the imported draft on explicit user action
  - rollback the published course back to draft/inactive if needed
  - delete the imported Amanoba draft if the downstream handoff must be removed
  - only then allow final local acceptance
  - show creator run readiness badges on the run cards before the user opens a run
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
- if a doc describes an old workflow, it must not be used as the delivery source without first reconciling it to the current system

## Course content and publishing

For lesson and quiz content:

- live system compatibility is defined by `/Users/moldovancsaba/Projects/amanoba`
- canonical content/course standards remain in this repo under `docs/`
- sovereign course-creator compatibility is defined in `docs/reference/sovereign-course-creator-compatibility-contract.md`
- when there is a conflict, the current application behavior plus the explicitly designated SSOT docs win

## Working rule

When planning or executing future work:

1. confirm the current code/runtime behavior
2. check whether the relevant doc is current or stale
3. update obsolete documentation as part of the change
4. search and manage product issues in `mvp-factory-control`
