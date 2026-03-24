# System Versioning

## Current state

This workspace is attached to a Git repository:

- repository: `moldovancsaba/amanoba_courses`
- remote: `https://github.com/moldovancsaba/amanoba_courses.git`

That means local provenance is available through normal Git commands such as:

- `git status`
- `git log`
- `git rev-parse HEAD`

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

## Normalization rule

Documentation in this project should describe:

- the current code path
- the current Git-backed workspace reality
- the active config defaults
- the actual launch-agent behavior
- the external planning SSOT in `mvp-factory-control`
