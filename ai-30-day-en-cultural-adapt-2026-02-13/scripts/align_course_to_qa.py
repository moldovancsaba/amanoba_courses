#!/usr/bin/env python3
import json
import re
from pathlib import Path

BASE = Path('/Users/moldovancsaba/Projects/amanoba_courses/ai-30-day-en-cultural-adapt-2026-02-13')
LESSONS = BASE / 'lessons'
QUIZZES = BASE / 'quizzes'
PLAN = BASE / 'mcq-skeleton-plan.ai30-en.json'

lesson_heading_map = [
    ('## Learning objective', '## Learning goal'),
    ('## Who this is for', '## Who'),
    ('## What this covers', '## What'),
    ('## Where to apply it', '## Where'),
    ('## When to use it', '## When'),
    ('## How to do it', '## How'),
    ('## Guided practice (10-15 minutes)', '## Guided exercise'),
    ('## Independent practice (5-10 minutes)', '## Independent exercise'),
    ('## Independent exercise (5-10 minutes)', '## Independent exercise'),
    ('## Quick self-check (yes/no)', '## Self-check'),
    ('## Resources', '## Bibliography'),
]

quiz_phrase_fixes = [
    (
        'I roll it out across all tasks at once, including service-package decisions, without tracking outcomes or taking notes.',
        'I roll it out across every relevant workflow in one week while tracking speed only and skipping quality evidence.',
    ),
    (
        'I only read about pricing for a week, but I do not test a real 3-option pricing table in a real task.',
        'I only read about pricing for a week and postpone real-task validation of the 3-option pricing table.',
    ),
    (
        'I introduce all tasks at the same time, even in the targeted implementation situation of the first month after the course, without measuring and taking notes.',
        'I roll out the method across every workflow in one week and track only speed anecdotes.',
    ),
    (
        'Quick request for the targeted implementation of the first month after the course -> immediate sending -> subsequent rewriting if there is a problem.',
        'Quick prompt for the first-month rollout -> immediate send -> later edits only after quality review feedback.',
    ),
]


def collapse_long_paragraphs(text: str) -> str:
    parts = text.split('\n\n')
    out = []
    for p in parts:
        lines = p.splitlines()
        first = lines[0].lstrip() if lines else ''
        if len(lines) > 3 and first and not first.startswith(('#', '-', '|', '>', '**', '<!--')):
            out.append(' '.join(x.strip() for x in lines if x.strip()))
        else:
            out.append(p)
    return '\n\n'.join(out)


def normalize_lesson(text: str) -> str:
    t = text
    t = re.sub(r'^(# Lesson [^\n]+?)\s+\*\*In one sentence:\*\*', r'\1\n\n**In one sentence:**', t, flags=re.M)
    for old, new in lesson_heading_map:
        t = t.replace(old, new)

    t = t.replace('> **Frequent error:**', '> **Common mistake:**')
    t = t.replace('> **Frequent mistake:**', '> **Common mistake:**')
    t = t.replace('> **Frequent Error:**', '> **Common mistake:**')

    t = collapse_long_paragraphs(t)
    t = re.sub(r'\n{3,}', '\n\n', t).strip() + '\n'
    return t


def split_question_blocks(text: str):
    m = list(re.finditer(r'(?m)^### Question \d+\n', text))
    if not m:
        return text, []
    header = text[: m[0].start()].rstrip()
    blocks = []
    for i, mm in enumerate(m):
        start = mm.start()
        end = m[i + 1].start() if i + 1 < len(m) else len(text)
        blocks.append(text[start:end].strip())
    return header, blocks


def inject_skeleton_metadata(block: str, sid: str, family: str, level: str) -> str:
    b = re.sub(r'(?m)^\*\*Skeleton ID:\*\*.*\n?', '', block)
    b = re.sub(r'(?m)^\*\*Skeleton Family:\*\*.*\n?', '', b)
    b = re.sub(r'(?m)^\*\*Skeleton Level:\*\*.*\n?', '', b)

    lines = b.splitlines()
    if not lines:
        return b
    out = [lines[0], f'**Skeleton ID:** {sid}', f'**Skeleton Family:** {family}', f'**Skeleton Level:** {level}']
    out.extend(lines[1:])
    return '\n'.join(out).strip()


def normalize_quiz(text: str, lesson_no: int, plan_map: dict[int, list[dict]]) -> str:
    t = text
    t = t.replace('after the course', 'after the program')
    t = t.replace('After the course', 'After the program')
    for old, new in quiz_phrase_fixes:
        t = t.replace(old, new)

    header, blocks = split_question_blocks(t)
    if not blocks:
        return t.strip() + '\n'

    lesson_plan = plan_map.get(lesson_no, [])
    new_blocks = []
    for idx, block in enumerate(blocks, start=1):
        if idx <= len(lesson_plan):
            sk = lesson_plan[idx - 1]
            block = inject_skeleton_metadata(
                block,
                sid=sk['skeleton_id'],
                family=sk['skeleton_family'],
                level=sk['skeleton_level'],
            )
        else:
            block = inject_skeleton_metadata(block, sid='S01_SCENARIO_DECISION', family='scenario_decision', level='foundation')
        new_blocks.append(block)

    merged = header + '\n\n' + ('\n\n---\n\n'.join(new_blocks))
    merged = re.sub(r'\n{3,}', '\n\n', merged).strip() + '\n'
    return merged


def load_plan_map() -> dict[int, list[dict]]:
    obj = json.loads(PLAN.read_text(encoding='utf-8'))
    out = {}
    for lesson in obj.get('lessons', []):
        out[int(lesson['lesson_number'])] = lesson.get('questions', [])
    return out


def main() -> None:
    plan_map = load_plan_map()

    for p in sorted(LESSONS.glob('lesson-*.md')):
        raw = p.read_text(encoding='utf-8')
        p.write_text(normalize_lesson(raw), encoding='utf-8')

    for p in sorted(QUIZZES.glob('lesson-*-quiz.md')):
        m = re.match(r'^lesson-(\d{2})-.*-quiz\.md$', p.name)
        if not m:
            continue
        lesson_no = int(m.group(1))
        raw = p.read_text(encoding='utf-8')
        p.write_text(normalize_quiz(raw, lesson_no, plan_map), encoding='utf-8')


if __name__ == '__main__':
    main()
