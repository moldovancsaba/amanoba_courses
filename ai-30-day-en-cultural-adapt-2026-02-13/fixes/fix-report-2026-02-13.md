# Fix Report - 2026-02-13

## Root cause
- Previous localization polish left format mismatches against current QA scripts:
  - Lesson section headers did not match required labels for `qa_lessons.py`.
  - Quiz files were missing `---` question block separators expected by `qa_quizzes.py`.
  - Quiz blocks had no required skeleton metadata fields.
  - A few quiz options were weakly balanced and one stem pair was near-duplicate by similarity gate.

## Files changed
- Lessons: all files under `/Users/moldovancsaba/Projects/amanoba_courses/ai-30-day-en-cultural-adapt-2026-02-13/lessons/`
  - Section label normalization
  - Do/Don't formatting normalization for paragraph-length gate
  - Callout label normalization where needed
- Quizzes: all files under `/Users/moldovancsaba/Projects/amanoba_courses/ai-30-day-en-cultural-adapt-2026-02-13/quizzes/`
  - Inserted per-question separators (`---`)
  - Inserted skeleton metadata per question from plan
  - Targeted quality rewrites for failing options/stems
- Package synced from files:
  - `/Users/moldovancsaba/Projects/amanoba_courses/ai-30-day-en-cultural-adapt-2026-02-13/AI_30_DAY_EN_export_2026-02-13_recreated.json`
- Automation/helper scripts added:
  - `/Users/moldovancsaba/Projects/amanoba_courses/ai-30-day-en-cultural-adapt-2026-02-13/scripts/align_course_to_qa.py`
  - `/Users/moldovancsaba/Projects/amanoba_courses/ai-30-day-en-cultural-adapt-2026-02-13/scripts/sync_package_from_files.py`

## QA results
- Lesson QA (`qa_lessons.py`): PASS
- Quiz QA (`qa_quizzes.py` + DB checks + recommendations): PASS
- Skeleton-fit promotion recommendations: generated, no promotable candidates (`after_support=0`)
- Day-by-day strict runner (`ai30_en_rebuild_runner.py`): PASS through day 30
- Import readiness check (v2 package validation): PASS

## Remaining risks
- Language quality is now QA-compliant and structurally consistent, but some wording may still benefit from optional native-copy polishing in a future editorial pass.

## Next step
- Import `/Users/moldovancsaba/Projects/amanoba_courses/ai-30-day-en-cultural-adapt-2026-02-13/AI_30_DAY_EN_export_2026-02-13_recreated.json` into the Amanoba UI.
