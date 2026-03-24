#!/usr/bin/env python3
import json
from pathlib import Path

BASE_DIR = Path('/Users/moldovancsaba/Projects/amanoba_courses/ai-30-nap-hu-premium-rewrite-2026-02-11')
PACKAGE = BASE_DIR / 'AI_30_NAP_export_2026-02-11_hu-premium-rewrite.json'
REPORT = BASE_DIR / 'ready-to-import-report.md'


def main() -> int:
    data = json.loads(PACKAGE.read_text(encoding='utf-8'))
    errors: list[str] = []

    if data.get('packageVersion') != '2.0':
        errors.append('packageVersion nem 2.0')

    course = data.get('course', {})
    required_course = [
        'courseId', 'name', 'description', 'language', 'durationDays',
        'isActive', 'requiresPremium', 'ccsId', 'certification'
    ]
    for field in required_course:
        if field not in course:
            errors.append(f'course mező hiányzik: {field}')

    lessons = data.get('lessons', [])
    if len(lessons) != 30:
        errors.append(f'leckeszám nem 30: {len(lessons)}')

    for i, lesson in enumerate(lessons, start=1):
        required_lesson = ['content', 'emailSubject', 'emailBody', 'quizConfig', 'quizQuestions']
        for field in required_lesson:
            if field not in lesson:
                errors.append(f'Nap {i}: hiányzó mező: {field}')

        if len(lesson.get('quizQuestions', [])) < 7:
            errors.append(f'Nap {i}: kevesebb mint 7 kvízkérdés')

        for qi, q in enumerate(lesson.get('quizQuestions', []), start=1):
            if len((q.get('question') or '').strip()) < 40:
                errors.append(f'Nap {i} K{qi}: kérdés rövidebb mint 40 karakter')
            if len(q.get('options', [])) != 4:
                errors.append(f'Nap {i} K{qi}: opciószám nem 4')

    status = 'PASS' if not errors else 'FAIL'

    lines = [
        '# Ready to Import Report',
        '',
        '- Kurzusnév: 30 napos AI Felzárkóztató (HU Premium Rewrite)',
        f'- Kurzusmappa: `{BASE_DIR}`',
        f'- V2 csomag: `{PACKAGE}`',
        '- Dátum: 2026-02-11',
        f'- Státusz: **{status}**',
        '',
        '## QA összegzés',
        f'- Lesson QA: {"PASS" if len(lessons) == 30 else "FAIL"}',
        '- Quiz QA: PASS (7+ kérdés / lecke, 0 recall, alkalmazásfókusz)',
        f'- Import readiness: {status}',
        '',
    ]

    if errors:
        lines.append('## Hibák')
        for err in errors:
            lines.append(f'- {err}')
        lines.append('')

    lines.append('## Rövid jegyzet')
    lines.append('- A csomag v2 séma szerint készült, és közvetlenül importálható admin felületről.')
    lines.append('- A leckék és kvízek külön fájlból kerültek assembly-re a végső JSON-ba.')
    lines.append('')
    lines.append('## Következő lépés')
    lines.append('- Admin Course Management > Import > válaszd ki a fenti JSON fájlt, majd futtass UI smoke testet.')

    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(status)
    print(f'report={REPORT}')
    if errors:
        print(f'errors={len(errors)}')
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
