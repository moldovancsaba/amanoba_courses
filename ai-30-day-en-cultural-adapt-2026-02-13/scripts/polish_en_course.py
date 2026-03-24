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


def polish_lesson_text(text: str) -> str:
    pairs = [
        ('### 2 minute theory', '### 2-minute theory'),
        ("It's not a general AI demonstration, and it's not a task worth doing just for the sake of demonstration.", 'This is not a generic AI demo, and it is not busywork.'),
        ('### Signs detected late', '### Late warning signs'),
        ('### A realistic expectation', '### Realistic expectations'),
        ('At least once per working day, every time for recurring tasks.', 'At least once per workday, and every time for recurring tasks.'),
        ('Do not use this here', 'Do not use this when'),
        ('A short note with 3 blocks: situation, request samples, quality gate.', 'A short note with three blocks: situation, prompt variants, and quality gate.'),
        ('in hand, which you can use again tomorrow.', 'ready to reuse tomorrow.'),
        ('The quality here is that ', 'Quality comes from ensuring that '),
        ('can be checked and repeated.', 'is verifiable and repeatable.'),
        ('follow-up work is reduced', 'rework is reduced'),
        ('pricing bases', 'pricing fundamentals'),
    ]
    out = replace_all(text, pairs)

    # Light grammar normalization patterns.
    out = re.sub(r'\bChoose a task of your own, tomorrow, where\b', 'Choose one of your own tasks for tomorrow where', out)
    out = re.sub(r"\bBy the end of today's practical task, you will have (.+?) ready to reuse tomorrow\.", r"By the end of today's practical task, you will have \1.", out)
    out = re.sub(r'\s{2,}', ' ', out)
    out = out.replace('  \n', '  \n')
    return out


def polish_quiz_text(text: str) -> str:
    pairs = [
        ('I would like a long answer right away', 'I ask for a long answer immediately'),
        ('without format or limit.', 'without specifying format or constraints.'),
        ('Rephrase the task more nicely, but', 'I rewrite the task to sound nicer, but'),
        ('I take the limits and just go for speed, even if the chance of', 'I remove constraints and optimize only for speed, even if the risk of'),
        ('I count the number of times the request was executed, even if', 'I only count how many times the prompt ran, even if'),
        ('I count the number of times the request has been executed, even if', 'I only count how many times the prompt ran, even if'),
        ('choice for feeling,', 'choose by gut feel,'),
        ('choice for sentiment,', 'choose by gut feel,'),
        ('pricing bases', 'pricing fundamentals'),
        ('service deployment with different packages, ignoring its context.', 'service-package tasks while ignoring context.'),
        ('without measurements.', 'without measurement.'),
        ('I only read about pricing for a week, but I do not test a real 3-option pricing table on an actual task.', 'I only read about pricing for a week, but I do not test a real 3-option pricing table in a real task.'),
    ]
    out = replace_all(text, pairs)

    # Structural phrasing cleanup for arrow-style options.
    out = re.sub(
        r'Introduction of quick request (.+?) for tasks -> immediate sending -> subsequent rewriting if there is a problem\.',
        r'Quick prompt for \1 tasks -> send immediately -> rewrite later only if issues appear.',
        out,
    )
    out = re.sub(
        r'Quick request (.+?) for task -> immediate sending -> subsequent rewriting if there is a problem\.',
        r'Quick prompt for \1 -> send immediately -> rewrite later only if issues appear.',
        out,
    )

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
        r'I only check whether the output is longer than before, regardless of whether the (.+?)\.',
        r'I only check whether the output is longer than before, not whether the \1 is usable.',
        out,
    )

    out = re.sub(
        r'I am only asking for an impression from the team, but I am evaluating the results of (.+?) without data\.',
        r'I only collect team impressions and evaluate \1 without data.',
        out,
    )

    out = re.sub(
        r'\bis responsible for each task and a date measurement point is recorded\.',
        'each task has a recorded owner and due date metric.',
        out,
    )
    out = out.replace('all tasks are responsible and without date measurement.', 'all tasks have owners and dates, but without measurement.')

    out = re.sub(r'\s{2,}', ' ', out)
    return out


def polish_package(obj: dict) -> dict:
    for lesson in obj.get('lessons', []):
        content = lesson.get('content') or ''
        lesson['content'] = polish_lesson_text(content)

        first = lesson['content'].splitlines()[0] if lesson['content'] else ''
        m = re.match(r'^#\s*Lesson\s+(\d+):\s*(.+)$', first)
        if m:
            day = int(lesson.get('dayNumber', m.group(1)))
            title = m.group(2).strip()
            lesson['title'] = title
            lesson['emailSubject'] = f'AI 30 Day - Day {day}: {title}'

        qq = lesson.get('quizQuestions') or []
        for q in qq:
            q['question'] = polish_quiz_text(q.get('question') or '')
            q['options'] = [polish_quiz_text(opt) for opt in (q.get('options') or [])]
    return obj


def main() -> None:
    for p in sorted(LESSONS.glob('lesson-*.md')):
        p.write_text(polish_lesson_text(p.read_text(encoding='utf-8')), encoding='utf-8')

    for p in sorted(QUIZZES.glob('lesson-*-quiz.md')):
        p.write_text(polish_quiz_text(p.read_text(encoding='utf-8')), encoding='utf-8')

    obj = json.loads(PACKAGE.read_text(encoding='utf-8'))
    obj = polish_package(obj)
    PACKAGE.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
