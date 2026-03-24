# System Versioning

## Current state

This workspace is currently not attached to a Git repository, so `git status`, `git log`, and commit-based provenance are not available here.

That means:

- there is no trustworthy local branch name to report
- there is no commit SHA to anchor documentation claims
- runtime behavior must be verified from code, config, and live reports

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
- the active config defaults
- the actual launch-agent behavior

It should not claim Git-backed provenance unless this workspace is reattached to a real repository.
