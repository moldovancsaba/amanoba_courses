# Sovereign Course Creator Compatibility Contract

This document defines the compatibility contract between the future sovereign course-creation workflow in `amanoba_courses` and the live Amanoba application in `/Users/moldovancsaba/Projects/amanoba`.

It is the implementation artifact for:

- `mvp-factory-control` issue [#504](https://github.com/moldovancsaba/mvp-factory-control/issues/504)

If a later course-creation stage contradicts this contract, this contract wins until it is explicitly updated.

Applies to: **Amanoba v0.2.0**.

## Status and SSOT

- **Status:** current compatibility contract
- **Document owner:** Amanoba course-creator maintainers
- **Runtime SSOT:** `docs/current-ssot.md`
- **Conflict rule:** when the code and this document disagree, update this contract to match the live application before relying on it for delivery

## Ownership and SSOT

- **Compatibility SSOT:** this contract plus the live Amanoba application behavior in `/Users/moldovancsaba/Projects/amanoba`
- **Runtime version:** `Amanoba v0.2.0`

## Purpose

The sovereign course creator must produce artifacts that are:

- structurally valid for the live Amanoba models
- operationally safe for admin/editor flows
- compatible with current import, render, and QC behavior
- strict enough to fail closed on invalid or mixed-language content

This contract exists so later stages do not reinterpret the live application independently.

## Canonical live entities

The sovereign course creator must align with these live entities:

1. `CCS`
- model: `/Users/moldovancsaba/Projects/amanoba/app/lib/models/ccs.ts`
- purpose: course-family record
- canonical fields:
  - `ccsId`
  - `name`
  - `idea`
  - `outline`
  - `relatedDocuments`

2. `Course`
- model: `/Users/moldovancsaba/Projects/amanoba/app/lib/models/course.ts`
- purpose: a language-variant course or child/short course
- canonical fields for the sovereign creator:
  - `courseId`
  - `name`
  - `description`
  - `language`
  - `durationDays`
  - `isActive`
  - `requiresPremium`
  - `price`
  - `translations`
  - `pointsConfig`
  - `xpConfig`
  - `metadata`
  - `ccsId`
  - `isDraft`
  - `certification`
  - `defaultLessonQuizQuestionCount`
  - `quizMaxWrongAllowed`
  - `lessonQuizPolicy`

3. `Lesson`
- model: `/Users/moldovancsaba/Projects/amanoba/app/lib/models/lesson.ts`
- purpose: one day lesson within a course
- canonical fields:
  - `lessonId`
  - `courseId`
  - `dayNumber`
  - `language`
  - `title`
  - `content`
  - `emailSubject`
  - `emailBody`
  - `translations`
  - `quizConfig`
  - `unlockConditions`
  - `pointsReward`
  - `xpReward`
  - `isActive`
  - `displayOrder`
  - `metadata`

4. `QuizQuestion`
- model: `/Users/moldovancsaba/Projects/amanoba/app/lib/models/quiz-question.ts`
- purpose: course-specific or reusable question storage
- canonical fields for sovereign course creation:
  - `question`
  - `options` plus `correctIndex`
  - or `correctAnswer` plus `wrongAnswers`
  - `difficulty`
  - `category`
  - `isActive`
  - `lessonId`
  - `courseId`
  - `isCourseSpecific`
  - `uuid`
  - `hashtags`
  - `questionType`
  - `metadata.createdAt`
  - `metadata.updatedAt`
  - `metadata.createdBy`
  - `metadata.updatedBy`
  - `metadata.auditedAt`
  - `metadata.auditedBy`

## Live application seams

The compatibility contract must stay aligned with these behaviors:

1. Lesson content format
- source: `/Users/moldovancsaba/Projects/amanoba/app/lib/lesson-content.ts`
- canonical storage is Markdown
- legacy HTML may exist
- rendering uses `contentToHtml`
- import/export normalization uses `contentToMarkdown`

2. Course creation and editing
- source: `/Users/moldovancsaba/Projects/amanoba/app/api/admin/courses/route.ts`
- `courseId` must match `^[A-Z0-9_]+$`
- `language` is stored lowercase
- `ccsId` must be uppercase/underscore-safe if present

3. Question creation and filtering
- source: `/Users/moldovancsaba/Projects/amanoba/app/api/admin/questions/route.ts`
- language is currently inferred operationally through hashtags
- admin creation path validates question/options/correctIndex structure

4. Package import path
- source: `/Users/moldovancsaba/Projects/amanoba/app/api/admin/courses/import/route.ts`
- import accepts course plus lessons package data
- lesson content is accepted as stored content and later rendered via lesson-content helpers
- import merges into existing records when overwrite is enabled

## Entity responsibilities by stage

### Stage 1: Topic / run creation

Live DB writes are not required yet.

Allowed artifacts:

- sovereign run record
- topic input
- optional local draft artifacts

Forbidden:

- direct creation of live `Course`, `Lesson`, or `QuizQuestion`

### Stage 2: Research

Live DB writes are still optional and should remain draft-only.

Allowed artifacts:

- research source pack
- findings summary
- research approval decision

Forbidden:

- direct publish or lesson/question writes to live entities

### Stage 3: Blueprint / CCS planning

Allowed live entity:

- `CCS`

Allowed fields to create or update:

- `ccsId`
- `name`
- `idea`
- `outline`
- `relatedDocuments`

Notes:

- this is the first live-family artifact that may be created
- it defines course-family semantics but does not yet publish a course variant

### Stage 4: Draft course variant creation

Allowed live entity:

- `Course`

Required fields:

- `courseId`
- `name`
- `description`
- `language`
- `durationDays`
- `ccsId`
- `brandId`
- `pointsConfig`
- `xpConfig`

Required draft semantics:

- `isDraft = true`
- `isActive` must not be used as a shortcut for live publish

### Stage 5: Lesson draft generation

Allowed live entity:

- `Lesson`

Required fields:

- `lessonId`
- `courseId`
- `dayNumber`
- `language`
- `title`
- `content`
- `emailSubject`
- `emailBody`

Required invariants:

- `content` is stored in Markdown form
- `emailBody` is stored in Markdown form
- `title`, `content`, `emailSubject`, and `emailBody` must match the lesson language
- lesson content must be checkpoint-approved before QC injection

### Stage 6: Quiz draft generation

Allowed live entity:

- `QuizQuestion`

Required invariants:

- question must be tied to the lesson/course context
- language must match the target course language
- final accepted question pool must satisfy the current quiz SSOT gates
- questions must be standalone and random-order safe
- weak recall-style questions are not allowed where the current SSOT disallows them

### Stage 7: QC injection

The sovereign creator must hand draft lessons/questions into the existing QC system rather than bypassing it.

Allowed side effects:

- queue injection
- QC status tracking
- QC feedback linked back to the sovereign run
- structured handoff payloads derived from approved blueprint/lesson/question stage artifacts

Forbidden:

- direct live promotion without QC completion
- QC injection that depends only on reparsing human-readable markdown without a validated structured handoff payload

### Stage 8: Draft-to-live promotion

Allowed live entity updates:

- `Course.isDraft`
- `Course.isActive`
- any final approved lesson/question payload updates already validated by QC

Required invariants:

- final human approval is mandatory
- QC must be complete enough to satisfy the agreed publish gate
- promotion must be auditable and reversible

## Field mapping matrix

| Sovereign artifact | Live entity | Required mapping |
|---|---|---|
| Course family id | `CCS.ccsId`, `Course.ccsId` | Uppercase underscore-safe family id |
| Course variant id | `Course.courseId` | Uppercase underscore-safe variant id |
| Language variant | `Course.language`, `Lesson.language` | Lowercase locale code |
| Day plan | `Lesson.dayNumber` | Stable day-to-lesson mapping |
| Lesson title | `Lesson.title` | Human-readable lesson name |
| Lesson body | `Lesson.content` | Markdown-first lesson content |
| Lesson email subject | `Lesson.emailSubject` | Language-pure, day-compatible subject |
| Lesson email body | `Lesson.emailBody` | Markdown-first email content |
| Question lesson link | `QuizQuestion.lessonId` | Stable lesson identifier |
| Question course link | `QuizQuestion.courseId` | Owning course reference |
| Question audit identity | `QuizQuestion.uuid` | Stable unique identifier |
| Question language hint | `QuizQuestion.hashtags` | Include language tag strategy used by Amanoba |

## Hard invariants

These are fail-closed rules.

1. `courseId` and `ccsId`
- `courseId` must remain uppercase letters, numbers, and underscores only
- `ccsId` must remain uppercase letters, numbers, and underscores only
- locale tokens like `pt-br` cannot be written directly into `courseId`; use `PT_BR`

2. Markdown-first lessons
- `Lesson.content` must be written in Markdown form
- `Lesson.emailBody` must be written in Markdown form
- rendering to HTML happens through the application, not as the stored canonical form

3. Language integrity
- non-target-language leakage is prohibited in final accepted lessons and quizzes
- English fallback is only allowed when explicitly triggered by the future research/source policy
- fallback must be explicit, never silent

4. Draft before live
- sovereign-created course variants must remain draft until the explicit publish gate is satisfied
- `isActive` is not enough to represent publish approval by itself

5. QC is mandatory for final package improvement
- sovereign-created lessons/questions must pass through the existing QC system before final promotion

## Validation before live apply

Before any sovereign stage writes or promotes live content, validate:

1. `CCS`
- `ccsId` format
- `idea` and `outline` presence for approved planning stages

2. `Course`
- `courseId` format
- `language` format
- `ccsId` format
- draft flag semantics
- points and XP config presence

3. `Lesson`
- required fields present
- markdown-first storage
- language integrity across title/content/email fields
- dayNumber and course linkage consistent with the approved blueprint

4. `QuizQuestion`
- structural validity of answer model
- language integrity across question and options
- lesson/course linkage present
- question type and minimum quality aligned to current SSOT

## Rollback expectations

Every future implementation stage must support rollback at the artifact level.

Minimum rollback expectations:

1. Draft artifacts
- sovereign draft artifacts must be versioned or restorable without corrupting the run

2. Live content updates
- lesson/question replacements must preserve backups before overwrite
- draft-to-live promotion must record enough metadata to undo or supersede the promotion safely

3. QC outcomes
- QC failures, quarantines, and manual challenges must remain visible and attributable

## Open decisions for later issues

These are intentionally left to later implementation cards, not guessed here:

1. Where the sovereign run record itself lives
- local repo artifact
- Amanoba DB collection
- hybrid run log plus DB entity

2. Exact draft storage strategy
- fully live draft entities in Amanoba
- hybrid local artifacts plus staged live writes

3. Final publish gate minimums
- exact QC completion thresholds
- exact human approval UX

4. Source-pack persistence
- whether approved source packs live only in sovereign-run state or also in live Amanoba entities

## Later issues that depend on this contract

- [#505](https://github.com/moldovancsaba/mvp-factory-control/issues/505)
- [#506](https://github.com/moldovancsaba/mvp-factory-control/issues/506)
- [#507](https://github.com/moldovancsaba/mvp-factory-control/issues/507)
- [#508](https://github.com/moldovancsaba/mvp-factory-control/issues/508)
- [#509](https://github.com/moldovancsaba/mvp-factory-control/issues/509)
- [#510](https://github.com/moldovancsaba/mvp-factory-control/issues/510)
- [#511](https://github.com/moldovancsaba/mvp-factory-control/issues/511)
- [#512](https://github.com/moldovancsaba/mvp-factory-control/issues/512)
- [#513](https://github.com/moldovancsaba/mvp-factory-control/issues/513)
