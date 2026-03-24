import json
import re
import sys
from pathlib import Path

default_pkg = '/Users/moldovancsaba/Projects/amanoba_courses/ai-30-nap-refactor-2026-02-11/AI_30_NAP_export_2026-02-11_refactored.json'
pkg = Path(sys.argv[1] if len(sys.argv) > 1 else default_pkg)
data = json.loads(pkg.read_text(encoding='utf-8'))

banned_in_quiz = [
    'Egy új gyakorlatot vezetsz be',
    'Gyakorlat (vezetett)',
    'Gyakorlat (önálló)',
    'Írj le 3 feladat',
    'in this lesson',
    'today',
    'Day '
]

issues = []
question_texts = []

for lesson in data.get('lessons', []):
    d = lesson.get('dayNumber')
    content = lesson.get('content', '')

    # Lesson-level basic quality gates
    if '### Guided exercise' not in content or '### Independent exercise' not in content:
        issues.append(f'Day {d}: missing exercise sections')
    if content.count('| --- | --- | --- |') != 1:
        issues.append(f'Day {d}: table count != 1')
    if content.count('> **Pro tip:**') + content.count('> **Common mistake:**') != 1:
        issues.append(f'Day {d}: callout count != 1')

    for i, q in enumerate(lesson.get('quizQuestions', []), start=1):
        text = (q.get('question') or '').strip()
        question_texts.append((d, i, text))

        if len(text) < 40:
            issues.append(f'Day {d} Q{i}: question too short')

        for bad in banned_in_quiz:
            if bad.lower() in text.lower():
                issues.append(f'Day {d} Q{i}: banned fragment: {bad}')

        if '[' in text or ']' in text:
            issues.append(f'Day {d} Q{i}: placeholder-like brackets in question')

        # Balanced punctuation heuristics
        for a, b, label in [('(', ')', 'parentheses'), ('"', '"', 'double-quote')]:
            if label == 'double-quote':
                if text.count('"') % 2 != 0:
                    issues.append(f'Day {d} Q{i}: unbalanced quotes')
            else:
                if text.count(a) != text.count(b):
                    issues.append(f'Day {d} Q{i}: unbalanced parentheses')

# Duplicate exact questions
seen = {}
for d, i, t in question_texts:
    key = re.sub(r'\s+', ' ', t.lower()).strip()
    if key in seen:
        issues.append(f'Day {d} Q{i}: duplicate of Day {seen[key][0]} Q{seen[key][1]}')
    else:
        seen[key] = (d, i)

if issues:
    print('FAIL')
    for x in issues:
        print(x)
else:
    print('PASS')
    print(f"Lessons: {len(data.get('lessons', []))}")
    print(f"Questions: {len(question_texts)}")
