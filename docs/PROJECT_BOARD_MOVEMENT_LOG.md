# Project board review and manual movement / Scrum journal

Reviewed: 2026-11-15 UTC. Repository: `moldovancsaba/amanoba_courses`.

Repository-associated board: [Project 20](https://github.com/users/moldovancsaba/projects/20). Existing creator delivery work is also tracked by [Project 1](https://github.com/users/moldovancsaba/projects/1), under [the canonical creator program #513](https://github.com/moldovancsaba/mvp-factory-control/issues/513). **Boards are read-only. Never add, remove, reorder or move cards or edit project fields.** Do not move the central delivery program into the empty repository board.

## Verified scope and limits

- The repository issue collection and Project 20 both returned zero entries. This does not mean the product has no work: the central creator program and its child issues remain the known delivery records.
- Project 20 read access succeeded. The central Project 1 was read separately for the creator cards; its relevant observations are listed below.
- Source reviewed: [README](../README.md), [current SSOT](current-ssot.md), [creator daemon](../course_quality_daemon/daemon.py), [dashboard](../course_quality_daemon/dashboard.py). Existing source has stage generation, source review, QC handoff, explicit export/import/publish, provenance helpers and rollback controls.
- These are implementation surfaces, not repeated acceptance evidence. No course, learner record, model, background process, MongoDB bridge, deployment or board state was changed or exercised.
- An empty repository board is not permission to duplicate or relocate the program. Preserve the canonical issue history, including earlier migration reversals.
- Documentation links and register coverage were checked. No runtime, macOS launch-agent, model-quality or live publishing test is claimed.

## Evidence-based work clusters

| Existing issues in mvp-factory-control | Disposition / next evidence |
| --- | --- |
| [#504](https://github.com/moldovancsaba/mvp-factory-control/issues/504) compatibility | Verify current Amanoba schema/bridge contract against the existing creator; do not replace it with an isolated offline draft format. |
| [#505](https://github.com/moldovancsaba/mvp-factory-control/issues/505) run model | Rebaseline on current stage/checkpoint state and prove restart, stale approval and retry behavior. |
| [#506](https://github.com/moldovancsaba/mvp-factory-control/issues/506) research | Existing source-pack CRUD and preferred/neutral/rejected review need acceptance and rejected-source reuse checks, not a new basic source registry. |
| [#507](https://github.com/moldovancsaba/mvp-factory-control/issues/507), [#508](https://github.com/moldovancsaba/mvp-factory-control/issues/508), [#509](https://github.com/moldovancsaba/mvp-factory-control/issues/509) generation | Preserve canonical blueprint, language purity and quiz standards. Verify actual stage artifacts and quality before choosing another framework or model. |
| [#510](https://github.com/moldovancsaba/mvp-factory-control/issues/510), [#511](https://github.com/moldovancsaba/mvp-factory-control/issues/511) approval / QC | Existing lifecycle controls and QC handoff need permission, failure and repeat-publish acceptance; source presence does not close the issues. |
| [#512](https://github.com/moldovancsaba/mvp-factory-control/issues/512) audit / recovery | Retain as a safety requirement: provenance helpers and rollback do not prove a complete immutable attributable audit chain. |
| [#513](https://github.com/moldovancsaba/mvp-factory-control/issues/513) program | Keep the existing program as the sequencing anchor. Derive remaining scope from child acceptance, not old statements that the creator does not yet exist. |

Technology choice: keep the existing local-first implementation as baseline. Durable checkpoint tooling is only an evaluated option for a demonstrated recovery gap; it does not replace course policy, QC or human approval. No new dependency, provider or hosted service is selected by this review.

## Central card observations

| Canonical issue | Observed Project 1 Status | Proposed destination | Condition / execution |
| --- | --- | --- | --- |
| [#504](https://github.com/moldovancsaba/mvp-factory-control/issues/504) | Review (ALMOST) | Remain | Criterion-level evidence required; no move executed |
| [#505](https://github.com/moldovancsaba/mvp-factory-control/issues/505) | In Progress (NOW) | Remain | Criterion-level evidence required; no move executed |
| [#506](https://github.com/moldovancsaba/mvp-factory-control/issues/506) | In Progress (NOW) | Remain | Criterion-level evidence required; no move executed |
| [#507](https://github.com/moldovancsaba/mvp-factory-control/issues/507) | In Progress (NOW) | Remain | Criterion-level evidence required; no move executed |
| [#508](https://github.com/moldovancsaba/mvp-factory-control/issues/508) | In Progress (NOW) | Remain | Criterion-level evidence required; no move executed |
| [#509](https://github.com/moldovancsaba/mvp-factory-control/issues/509) | In Progress (NOW) | Remain | Criterion-level evidence required; no move executed |
| [#510](https://github.com/moldovancsaba/mvp-factory-control/issues/510) | In Progress (NOW) | Remain | Criterion-level evidence required; no move executed |
| [#511](https://github.com/moldovancsaba/mvp-factory-control/issues/511) | In Progress (NOW) | Remain | Criterion-level evidence required; no move executed |
| [#512](https://github.com/moldovancsaba/mvp-factory-control/issues/512) | IDEABANK (SOMEDAY) | Remain | Criterion-level evidence required; no move executed |
| [#513](https://github.com/moldovancsaba/mvp-factory-control/issues/513) | In Progress (NOW) | Remain | Criterion-level evidence required; no move executed |

## Append-only Scrum / manual movement journal

| Date / Scrum reference | Board and issue | Observed column | Proposed destination | Acceptance evidence | Dependency / blocker | Owner decision | Manual execution / person | Verified new column | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-15 review | Project 20 | Empty | No move | Direct board read | Central issue history remains authoritative for its work | No move proposed | Not executed | Empty observed | No card created |
| YYYY-MM-DD / meeting link | Board URL + issue URL | Exact observed value | Exact proposed value or remain | Evidence link | Specific condition | Pending | Not executed | Not verified | — |

Read the actual board and issue before each proposal; retain prior observations when a decision changes. Only mark a move executed after the owner performs it and the result is read back. Documentation rollback requires no product or board rollback.
