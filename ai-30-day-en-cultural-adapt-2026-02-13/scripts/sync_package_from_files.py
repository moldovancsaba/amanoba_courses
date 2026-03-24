#!/usr/bin/env python3
import json
import re
from pathlib import Path
from typing import Optional

BASE = Path('/Users/moldovancsaba/Projects/amanoba_courses/ai-30-day-en-cultural-adapt-2026-02-13')
PACKAGE = BASE / 'AI_30_DAY_EN_export_2026-02-13_recreated.json'
LESSONS = BASE / 'lessons'
QUIZZES = BASE / 'quizzes'


def parse_quiz_file(path: Path):
    text = path.read_text(encoding='utf-8')
    blocks = [b.strip() for b in text.split('\n---\n') if '**Question:**' in b]
    rows = []
    for b in blocks:
        qm = re.search(r'\*\*Question:\*\*\s*(.*)', b)
        opts = re.findall(r'^[A-D]\)\s+(.*)$', b, flags=re.M)
        cm = re.search(r'\*\*Correct:\*\*\s*([A-D])', b)
        dm = re.search(r'\*\*Difficulty:\*\*\s*(\w+)', b)
        tm = re.search(r'\*\*Type:\*\*\s*([\w-]+)', b)
        if not qm or len(opts) != 4 or not cm:
            continue
        rows.append(
            {
                'question': qm.group(1).strip(),
                'options': [o.strip() for o in opts],
                'correctIndex': ord(cm.group(1)) - ord('A'),
                'difficulty': (dm.group(1).strip().lower() if dm else 'medium'),
                'category': (tm.group(1).strip().lower() if tm else 'application'),
            }
        )
    return rows


def lesson_title_from_content(content: str) -> Optional[str]:
    first = content.splitlines()[0] if content else ''
    m = re.match(r'^#\s*Lesson\s+\d+:\s*(.+)$', first)
    return m.group(1).strip() if m else None


def main() -> None:
    obj = json.loads(PACKAGE.read_text(encoding='utf-8'))

    by_day_lesson_file = {}
    for p in sorted(LESSONS.glob('lesson-*.md')):
        m = re.match(r'^lesson-(\d{2})-.*\.md$', p.name)
        if m and not p.name.endswith('-quiz.md'):
            by_day_lesson_file[int(m.group(1))] = p

    by_day_quiz_file = {}
    for p in sorted(QUIZZES.glob('lesson-*-quiz.md')):
        m = re.match(r'^lesson-(\d{2})-.*-quiz\.md$', p.name)
        if m:
            by_day_quiz_file[int(m.group(1))] = p

    for lesson in obj.get('lessons', []):
        day = int(lesson.get('dayNumber'))
        lp = by_day_lesson_file.get(day)
        qp = by_day_quiz_file.get(day)
        if lp:
            content = lp.read_text(encoding='utf-8').rstrip('\n')
            lesson['content'] = content
            title = lesson_title_from_content(content)
            if title:
                lesson['title'] = title
                lesson['emailSubject'] = f'AI 30 Day - Day {day}: {title}'
        if qp:
            parsed = parse_quiz_file(qp)
            existing = lesson.get('quizQuestions') or []
            out = []
            for i, pq in enumerate(parsed):
                row = existing[i] if i < len(existing) else {}
                out.append(
                    {
                        'hashtags': row.get('hashtags', []),
                        'question': pq['question'],
                        'options': pq['options'],
                        'correctIndex': pq['correctIndex'],
                        'difficulty': pq['difficulty'],
                        'category': pq['category'],
                        'questionType': row.get('questionType', 'multiple_choice'),
                        'isActive': row.get('isActive', True),
                    }
                )
            lesson['quizQuestions'] = out

    PACKAGE.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
