#!/usr/bin/env python3
import json
import re
from pathlib import Path

BASE = Path('/Users/moldovancsaba/Projects/amanoba_courses/ai-30-day-en-cultural-adapt-2026-02-13')
LESSONS = BASE / 'lessons'
QUIZZES = BASE / 'quizzes'
PACKAGE = BASE / 'AI_30_DAY_EN_export_2026-02-13_recreated.json'


def replace_all(text: str, pairs: list[tuple[str, str]]) -> str:
    out = text
    for old, new in pairs:
        out = out.replace(old, new)
    return out


def phrase_fixes(text: str) -> str:
    pairs = [
        ('pricing bases', 'pricing fundamentals'),
        ('service deployment with different packages, ignoring its context.', 'service-package tasks while ignoring context.'),
        ('without measurements.', 'without measurement.'),
        ('I would like a long answer right away', 'I ask for a long answer immediately'),
        ('without format or limit.', 'without specifying format or constraints.'),
        ('Rephrase the task more nicely, but', 'I rewrite the task to sound nicer, but'),
        ('I take the limits and just go for speed, even if the chance of', 'I remove constraints and optimize only for speed, even if the risk of'),
        ('I count the number of times the request was executed, even if', 'I only count how many times the prompt ran, even if'),
        ('I count the number of times the request has been executed, even if', 'I only count how many times the prompt ran, even if'),
        ('choice for sentiment,', 'choose by gut feel,'),
        ('choice for feeling,', 'choose by gut feel,'),
        ("It's not a general AI demonstration, and it's not a task worth doing just for the sake of demonstration.", 'This is not a generic AI demo, and it is not busywork.'),
        ('### Signs detected late', '### Late warning signs'),
        ('### A realistic expectation', '### Realistic expectations'),
        ('### 2 minute theory', '### 2-minute theory'),
        ('At least once per working day, every time for recurring tasks.', 'At least once per workday, and every time for recurring tasks.'),
        ('Do not use this here', 'Do not use this when'),
        ('A short note with 3 blocks: situation, request samples, quality gate.', 'A short note with three blocks: situation, prompt variants, and quality gate.'),
        ('The quality here is that ', 'Quality comes from ensuring that '),
        ('can be checked and repeated.', 'is verifiable and repeatable.'),
        ('follow-up work is reduced', 'rework is reduced'),
    ]
    out = replace_all(text, pairs)

    out = re.sub(
        r'Long (?:general|generic) request -> (?:multiple|several) random (?:re-runs|reruns|replays) -> (?:choose by gut feel|choice for sentiment|choice for feel),',
        'Generic long prompt -> random reruns -> choose by gut feel,',
        out,
    )
    out = re.sub(
        r'I only give the style, because the details of (.+?) will be (?:figured out|guessed) by the model\.',
        r'I only specify tone and assume the model will infer the rest about \1.',
        out,
    )
    out = re.sub(
        r'I only give the style, because the model will figure out the details of (.+?)\.',
        r'I only specify tone and assume the model will infer the rest about \1.',
        out,
    )
    out = re.sub(
        r'I will hand it over without changes, and I will not record the measurement point \((.+?)\) separately\.',
        r'I hand it over unchanged and do not record the measurement point (\1).',
        out,
    )
    out = re.sub(
        r"I(?:'m| am) looking to see if the text has become longer than before, regardless of whether the (.+?)\.",
        r'I only check whether the output is longer than before, not whether the \1 is usable.',
        out,
    )
    out = re.sub(
        r'I look to see if the text has become longer than before, regardless of whether the (.+?) is usable\.',
        r'I only check whether the output is longer than before, not whether the \1 is usable.',
        out,
    )
    out = re.sub(
        r'I only check whether the output is longer than before, regardless of whether the (.+?)\.',
        r'I only check whether the output is longer than before, not whether the \1 is usable.',
        out,
    )
    out = re.sub(
        r'I am only asking for an impression from the team, but I am evaluating the results of (.+?) without data\.',
        r'I only collect team impressions and evaluate \1 without data.',
        out,
    )
    out = out.replace('all tasks are responsible and without date measurement.', 'all tasks have owners and dates, but without measurement.')
    out = out.replace('is responsible for each task and a date measurement point is recorded.', 'each task has a recorded owner and due date metric.')
    out = out.replace("By the end of today\\'s practical task", "By the end of today's practical task")
    return out


def reflow_lesson(text: str) -> str:
    t = text
    t = re.sub(r'\s+(##\s)', r'\n\n\1', t)
    t = re.sub(r'\s+(###\s)', r'\n\n\1', t)
    t = re.sub(r'\s+(\*\*In one sentence:\*\*)', r'\n\n\1', t)
    t = re.sub(r'\s+(\*\*Time:\*\*)', r'\n\1', t)
    t = re.sub(r'\s+(\*\*Tangible output:\*\*)', r'\n\1', t)
    t = re.sub(r'\s+(\*\*Primary[^\n]*\*\*)', r'\n\n\1', t)
    t = re.sub(r'\s+(\*\*Secondary[^\n]*\*\*)', r'\n\1', t)
    t = re.sub(r'\s+(\*\*Involved[^\n]*\*\*)', r'\n\1', t)
    t = re.sub(r'\s+(\*\*Affected[^\n]*\*\*)', r'\n\1', t)
    t = re.sub(r'\s+(- \[ \])', r'\n\1', t)
    t = re.sub(r'\s+(- \*\*)', r'\n\1', t)
    t = re.sub(r'\s+(> \*\*)', r'\n\n\1', t)
    t = re.sub(r'\s+(\|[^\n]*\|)', r'\n\1', t)
    t = t.replace('| |', '|\n|')
    t = re.sub(r'\s+(\d+\.\s+\*\*)', r'\n\1', t)
    t = re.sub(r'\s+(<!--\s+source-lesson-file:)', r'\n\n\1', t)

    # Ensure section headings are not glued to paragraph text.
    lesson_h2 = [
        'Learning objective',
        'Who this is for',
        'What this covers',
        'Where to apply it',
        'When to use it',
        'Why it matters',
        'How to do it',
        'Guided practice (10-15 minutes)',
        'Independent exercise (5-10 minutes)',
        'Quick self-check (yes/no)',
        'Resources',
        'Further reading',
    ]
    lesson_h3 = [
        'What is this?',
        "What isn't this?",
        '2-minute theory',
        'Key concepts',
        'It works fine here',
        'Do not use this when',
        'Connection points',
        'Use it when',
        'Frequency',
        'Late warning signs',
        'Practical benefits',
        'What happens if you skip it',
        'Realistic expectations',
        'Step by step',
        'Do / Don\'t',
        'Common errors and their correction',
        "It's ready if",
        'Inputs',
        'Steps',
        'Expected output format',
        'Task',
        'Output',
        'Starting metric',
    ]
    for h in lesson_h2:
        t = re.sub(rf'(## {re.escape(h)})\s+', rf'\1\n\n', t)
    for h in lesson_h3:
        t = re.sub(rf'(### {re.escape(h)})\s+', rf'\1\n\n', t)

    # keep line endings tidy
    t = re.sub(r'\n{3,}', '\n\n', t)
    return t.strip() + '\n'


def reflow_quiz(text: str) -> str:
    t = text
    t = re.sub(r'\s+(##\s+Question\s+pool)', r'\n\n\1', t)
    t = re.sub(r'\s+(###\s+Question\s+\d+)', r'\n\n\1', t)
    t = re.sub(r'\s+(\*\*Question:\*\*)', r'\n\1', t)
    t = re.sub(r'\s+([A-D]\)\s)', r'\n\1', t)
    t = re.sub(r'\s+(\*\*Correct:\*\*)', r'\n\1', t)
    t = re.sub(r'\s+(\*\*Type:\*\*)', r'\n\1', t)
    t = re.sub(r'\s+(\*\*Difficulty:\*\*)', r'\n\1', t)
    t = re.sub(r'\n{3,}', '\n\n', t)
    return t.strip() + '\n'


def main() -> None:
    for p in sorted(LESSONS.glob('lesson-*.md')):
        txt = p.read_text(encoding='utf-8')
        txt = phrase_fixes(txt)
        txt = reflow_lesson(txt)
        p.write_text(txt, encoding='utf-8')

    for p in sorted(QUIZZES.glob('lesson-*-quiz.md')):
        txt = p.read_text(encoding='utf-8')
        txt = phrase_fixes(txt)
        txt = reflow_quiz(txt)
        p.write_text(txt, encoding='utf-8')

    obj = json.loads(PACKAGE.read_text(encoding='utf-8'))
    for lesson in obj.get('lessons', []):
        lesson['content'] = reflow_lesson(phrase_fixes(lesson.get('content') or '')).rstrip('\n')

        first = lesson['content'].splitlines()[0] if lesson['content'] else ''
        m = re.match(r'^#\s*Lesson\s+(\d+):\s*(.+)$', first)
        if m:
            day = int(lesson.get('dayNumber', m.group(1)))
            lesson['title'] = m.group(2).strip()
            lesson['emailSubject'] = f"AI 30 Day - Day {day}: {lesson['title']}"

        for q in (lesson.get('quizQuestions') or []):
            q['question'] = phrase_fixes(q.get('question') or '')
            q['options'] = [phrase_fixes(opt) for opt in (q.get('options') or [])]

    PACKAGE.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
