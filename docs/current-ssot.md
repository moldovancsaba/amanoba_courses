# Current SSOT

This document defines the current source-of-truth model for `amanoba_courses`.

If an older document, historical handover, or stale note conflicts with this file, treat that older material as supporting context only until it is updated.

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
- when there is a conflict, the current application behavior plus the explicitly designated SSOT docs win

## Working rule

When planning or executing future work:

1. confirm the current code/runtime behavior
2. check whether the relevant doc is current or stale
3. update obsolete documentation as part of the change
4. search and manage product issues in `mvp-factory-control`
