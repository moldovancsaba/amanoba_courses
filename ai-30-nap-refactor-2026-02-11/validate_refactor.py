import json
from pathlib import Path

p = Path('/Users/moldovancsaba/Projects/amanoba_courses/ai-30-nap-refactor-2026-02-11/AI_30_NAP_export_2026-02-11_refactored.json')
with p.open('r', encoding='utf-8') as f:
    data = json.load(f)

issues = []
lessons = data.get('lessons', [])
if len(lessons) != 30:
    issues.append(f'lesson_count={len(lessons)}')

required_tokens = [
    '## Learning goal', '## Who', '## What', '### What it is', '### What it is not',
    '### 2-minute theory', '## Where', '## When', '## Why it matters', '## How',
    '### Guided exercise', '### Independent exercise', '### Self-check',
    '## Bibliography', '## Read more'
]

all_questions = []
for i, lesson in enumerate(lessons, start=1):
    content = lesson.get('content', '')
    for tok in required_tokens:
        if tok not in content:
            issues.append(f'day_{i:02d}_missing_{tok}')
    if content.count('| --- | --- | --- |') != 1:
        issues.append(f'day_{i:02d}_table_count={content.count("| --- | --- | --- |")}')
    callouts = content.count('> **Pro tip:**') + content.count('> **Common mistake:**')
    if callouts != 1:
        issues.append(f'day_{i:02d}_callout_count={callouts}')

    qq = lesson.get('quizQuestions', [])
    if len(qq) < 7:
        issues.append(f'day_{i:02d}_quiz_count={len(qq)}')
    app_like = sum(1 for q in qq if q.get('questionType') in {'application', 'critical-thinking', 'diagnostic', 'best_practice', 'metric'})
    if app_like < 5:
        issues.append(f'day_{i:02d}_app_like={app_like}')
    recall = sum(1 for q in qq if q.get('questionType') == 'recall')
    if recall != 0:
        issues.append(f'day_{i:02d}_recall={recall}')

    for q in qq:
        all_questions.append(q.get('question', '').strip())

unique_questions = len(set(all_questions))
if unique_questions != len(all_questions):
    issues.append(f'duplicate_questions={len(all_questions)-unique_questions}')

print('PASS' if not issues else 'FAIL')
if issues:
    for issue in issues[:100]:
        print(issue)
