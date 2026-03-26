# System Versioning

## Current state

Current runtime release:

- `Amanoba v0.2.0`

This workspace is attached to a Git repository:

- repository: `moldovancsaba/amanoba_courses`
- remote: `https://github.com/moldovancsaba/amanoba_courses.git`

That means local provenance is available through normal Git commands such as:

- `git status`
- `git log`
- `git rev-parse HEAD`

## Status and SSOT

- **Status:** current version registry
- **Document owner:** Amanoba maintainers
- **Runtime SSOT:** `docs/current-ssot.md`
- **Conflict rule:** if the menubar, dashboard, or launch-agent behavior changes, update both this file and `docs/current-ssot.md` together so the version note and runtime surface stay aligned

## Ownership and SSOT

- **Document owner:** Amanoba maintainers
- **Versioning SSOT:** this file for current operator-facing version notes
- **Runtime SSOT:** `docs/current-ssot.md`
- **Conflict rule:** if the menubar, dashboard, or launch-agent behavior changes, update both this file and `docs/current-ssot.md` together so the version note and runtime surface stay aligned

## GitHub issue and planning source of truth

Code lives in `moldovancsaba/amanoba_courses`, but issue planning does not.

Use these as the authoritative planning sources:

- issue repository: `moldovancsaba/mvp-factory-control`
- project board: `https://github.com/users/moldovancsaba/projects/1`

Operational rule:

- do not assume the product repo issue tracker is the backlog
- search, create, update, and manage `amanoba_courses` issues in `mvp-factory-control`
- use the project board there as the planning SSOT
- when documentation refers to backlog items, dependencies, ideabank cards, or delivery tracking, it refers to `mvp-factory-control`

## Operational source of truth

Use these as the authoritative sources for the current system state:

- `course_quality_daemon/` for behavior
- `course_quality_daemon.json` for active configuration
- `scripts/install-course-quality-launchagents.sh` for launch-agent behavior
- `.course-quality/reports/health.json` for live runtime/provider state
- `.course-quality/reports/feed.json` for queue state
- `.course-quality/reports/watchdog.json` for watchdog actions

Current operator-facing surface:

- menubar build version: `Amanoba v0.2.0`
- menubar labels are short and role-based only
- the dashboard runtime section shows one compact `Model Roster` row
- the resident creator roles are served on ports `8080`, `8081`, and `8082`

## Normalization rule

Documentation in this project should describe:

- the current code path
- the current Git-backed workspace reality
- the active config defaults
- the actual launch-agent behavior
- the external planning SSOT in `mvp-factory-control`

Current operator-facing build versions should be documented explicitly when they affect the user surface. For example, the menubar app version is controlled by `tools/macos/AmanobaMenubar/install_AmanobaMenubar.sh` and is currently `0.2.0`.
