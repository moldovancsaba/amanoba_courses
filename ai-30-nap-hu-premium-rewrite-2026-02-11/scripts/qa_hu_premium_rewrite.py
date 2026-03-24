#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

BASE_DIR = Path('/Users/moldovancsaba/Projects/amanoba_courses/ai-30-nap-hu-premium-rewrite-2026-02-11')
PACKAGE = BASE_DIR / 'AI_30_NAP_export_2026-02-11_hu-premium-rewrite.json'
REPORT = BASE_DIR / 'localization-qa-report.md'

if len(sys.argv) > 1:
    PACKAGE = Path(sys.argv[1])

REQUIRED_HU_SECTIONS = [
    '## Tanulási cél',
    '## Kinek szól',
    '## Miről szól',
    '## Hol használod',
    '## Mikor használd',
    '## Miért számít',
    '## Hogyan csináld',
    '## Vezetett gyakorlat (10-15 perc)',
    '## Önálló gyakorlat (5-10 perc)',
    '## Gyors önellenőrzés (igen/nem)',
    '## Források',
    '## Továbbolvasás',
]

BANNED_QUIZ_FRAGMENTS = [
    'Egy új gyakorlatot vezetsz be',
    'Gyakorlat (vezetett)',
    'Gyakorlat (önálló)',
    'in this lesson',
    'this lesson',
    'today',
    'Day ',
]

BANNED_CONTEXT_REFERENCES = [
    'ebben a leckében',
    'a mai leckében',
    'a kurzusban',
    'ebben a modulban',
    'tegnapi',
    'holnapi leckében',
]

ENGLISH_HEADING_LEAK = [
    '## Learning goal',
    '## Who',
    '## What',
    '## Where',
    '## When',
    '## Why it matters',
    '## How',
    '### Guided exercise',
    '### Independent exercise',
    '### Self-check',
]

APP_LIKE_TYPES = {'application', 'critical-thinking', 'diagnostic', 'best_practice', 'metric'}


def md_table_count(text: str) -> int:
    return len(re.findall(r'\n\|[^\n]+\|\n\|\s*[-:| ]+\|', text))


def balanced_punctuation(text: str) -> tuple[bool, str]:
    if text.count('(') != text.count(')'):
        return False, 'zárójelpár-hiba'
    if text.count('"') % 2 != 0:
        return False, 'idézőjelpár-hiba'
    return True, ''


def main() -> int:
    data = json.loads(PACKAGE.read_text(encoding='utf-8'))
    errors: list[str] = []
    warnings: list[str] = []

    if data.get('packageVersion') != '2.0':
        errors.append(f"Top-level: packageVersion nem 2.0 ({data.get('packageVersion')})")

    course = data.get('course', {})
    if course.get('language') != 'hu':
        errors.append(f"Course language nem hu ({course.get('language')})")

    lessons = data.get('lessons', [])
    if len(lessons) != 30:
        errors.append(f"Leckeszám hiba: {len(lessons)} (elvárt: 30)")

    seen_questions = {}
    total_questions = 0

    for idx, lesson in enumerate(lessons, start=1):
        day = lesson.get('dayNumber', idx)
        title = lesson.get('title', f'nap-{idx}')
        content = lesson.get('content', '')

        if not content.startswith(f'# Lecke {day}:'):
            errors.append(f'Nap {day}: fejléc nem a várt formátum')

        for sec in REQUIRED_HU_SECTIONS:
            if sec not in content:
                errors.append(f'Nap {day}: hiányzó szekció: {sec}')

        for sec in ENGLISH_HEADING_LEAK:
            if sec in content:
                errors.append(f'Nap {day}: angol heading szivárgás: {sec}')

        tcount = md_table_count(content)
        if tcount != 1:
            errors.append(f'Nap {day}: táblaszám {tcount} (elvárt: 1)')

        callouts = content.count('> **Pro tipp:**') + content.count('> **Gyakori hiba:**')
        if callouts != 1:
            errors.append(f'Nap {day}: callout darabszám {callouts} (elvárt: 1)')

        qq = lesson.get('quizQuestions', [])
        if len(qq) < 7:
            errors.append(f'Nap {day}: kérdésszám {len(qq)} (elvárt: legalább 7)')

        app_like = sum(1 for q in qq if q.get('questionType') in APP_LIKE_TYPES)
        if app_like < 5:
            errors.append(f'Nap {day}: alkalmazás jellegű kérdés {app_like} (elvárt: legalább 5)')

        recall_count = sum(1 for q in qq if q.get('questionType') == 'recall')
        if recall_count != 0:
            errors.append(f'Nap {day}: recall kérdés {recall_count} (elvárt: 0)')

        for qi, q in enumerate(qq, start=1):
            total_questions += 1
            question = (q.get('question') or '').strip()
            options = q.get('options') or []

            if len(question) < 40:
                errors.append(f'Nap {day} K{qi}: kérdés túl rövid')

            for bad in BANNED_QUIZ_FRAGMENTS + BANNED_CONTEXT_REFERENCES:
                if bad.lower() in question.lower():
                    errors.append(f'Nap {day} K{qi}: tiltott minta: {bad}')

            ok_punc, punc_reason = balanced_punctuation(question)
            if not ok_punc:
                errors.append(f'Nap {day} K{qi}: írásjel hiba ({punc_reason})')

            if len(options) != 4:
                errors.append(f'Nap {day} K{qi}: opciószám {len(options)} (elvárt: 4)')
            else:
                if len(set(o.strip().lower() for o in options)) != 4:
                    errors.append(f'Nap {day} K{qi}: duplikált opciók')
                for oi, opt in enumerate(options, start=1):
                    if len(opt.strip()) < 25:
                        errors.append(f'Nap {day} K{qi} O{oi}: opció túl rövid')

            correct = q.get('correctIndex')
            if correct not in [0, 1, 2, 3]:
                errors.append(f'Nap {day} K{qi}: hibás correctIndex ({correct})')

            key = re.sub(r'\s+', ' ', question.lower()).strip()
            if key in seen_questions:
                other_day, other_q = seen_questions[key]
                errors.append(f'Nap {day} K{qi}: duplikált kérdés (egyezik Nap {other_day} K{other_q})')
            else:
                seen_questions[key] = (day, qi)

        # import readiness fields lesson level
        required_lesson_fields = ['content', 'emailSubject', 'emailBody', 'quizConfig', 'quizQuestions']
        for f in required_lesson_fields:
            if f not in lesson:
                errors.append(f'Nap {day}: hiányzó kötelező mező: {f}')

        if lesson.get('language') != 'hu':
            warnings.append(f'Nap {day}: lesson.language != hu')

    status = 'PASS' if not errors else 'FAIL'

    lines = [
        '# Localization QA Report',
        '',
        f'- Dátum: 2026-02-11',
        f'- Csomag: `{PACKAGE}`',
        f'- Státusz: **{status}**',
        f'- Leckék: {len(lessons)}',
        f'- Kérdések: {total_questions}',
        '',
        '## Lefuttatott gate-ek',
        '- Kötelező HU szekciók megléte 30/30 leckén',
        '- Pontosan 1 tábla és 1 callout leckénként',
        '- Tiltott töredékek és kontextus-utalások tiltása kérdésekben',
        '- Duplikált kérdésszöveg tiltás a teljes 210-es kérdésbankban',
        '- Kérdés/opció hossz és szerkezeti minimumok',
        '- 7+ kérdés / lecke, 5+ alkalmazás jellegű, 0 recall',
        '- Import-ready mezők ellenőrzése',
        '',
    ]

    if errors:
        lines.append('## Hibák')
        for e in errors:
            lines.append(f'- {e}')
        lines.append('')

    if warnings:
        lines.append('## Figyelmeztetések')
        for w in warnings:
            lines.append(f'- {w}')
        lines.append('')

    if not errors:
        lines.append('## Összegzés')
        lines.append('- Minden kötelező minőségi és lokalizációs kapu átment.')
        lines.append('- A kurzus kérdésbankja duplikációmentes és import-kompatibilis.')

    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(status)
    print(f'report={REPORT}')
    if errors:
        print(f'errors={len(errors)}')
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
