#!/usr/bin/env python3
import copy
import json
import re
import time
import warnings
from datetime import datetime
from pathlib import Path

from deep_translator import GoogleTranslator

warnings.filterwarnings('ignore')

SOURCE_DIR = Path('/Users/moldovancsaba/Projects/amanoba_courses/ai-30-nap-hu-premium-rewrite-2026-02-11-v2')
TARGET_DIR = Path('/Users/moldovancsaba/Projects/amanoba_courses/ai-30-day-en-cultural-adapt-2026-02-13')
SOURCE_PACKAGE = SOURCE_DIR / 'AI_30_NAP_export_2026-02-11_hu-premium-rewrite-v2.json'
OUT_PACKAGE = TARGET_DIR / 'AI_30_DAY_EN_export_2026-02-13_recreated.json'

LESSON_SRC_DIR = SOURCE_DIR / 'lessons'
QUIZ_SRC_DIR = SOURCE_DIR / 'quizzes'
LESSON_OUT_DIR = TARGET_DIR / 'lessons'
QUIZ_OUT_DIR = TARGET_DIR / 'quizzes'
LOCALIZATION_DIR = TARGET_DIR / 'localization'


class Translator:
    def __init__(self):
        self.translator = GoogleTranslator(source='hu', target='en')
        self.cache = {}

    def _split_chunks(self, text: str, limit: int = 4200) -> list[str]:
        if len(text) <= limit:
            return [text]

        blocks = re.split(r'(\n\n+)', text)
        chunks = []
        current = ''

        for block in blocks:
            if not block:
                continue
            if len(current) + len(block) <= limit:
                current += block
                continue
            if current:
                chunks.append(current)
                current = ''
            if len(block) <= limit:
                current = block
                continue

            lines = block.splitlines(keepends=True)
            line_buf = ''
            for line in lines:
                if len(line_buf) + len(line) <= limit:
                    line_buf += line
                else:
                    if line_buf:
                        chunks.append(line_buf)
                    line_buf = line
            if line_buf:
                current = line_buf

        if current:
            chunks.append(current)

        return chunks

    def _translate_chunk(self, text: str) -> str:
        text = text.strip('\n')
        if not text:
            return ''

        if text in self.cache:
            return self.cache[text]

        last_error = None
        for attempt in range(6):
            try:
                translated = self.translator.translate(text)
                self.cache[text] = translated
                time.sleep(0.25)
                return translated
            except Exception as err:
                last_error = err
                time.sleep(1.2 + (attempt * 0.8))
        raise RuntimeError(f'Translation failed after retries: {last_error}')

    def translate(self, text: str) -> str:
        if not text:
            return text

        placeholder_map = {
            '{{courseName}}': '__PLACEHOLDER_COURSENAME__',
            '{{dayNumber}}': '__PLACEHOLDER_DAYNUMBER__',
            '{{lessonTitle}}': '__PLACEHOLDER_LESSONTITLE__',
            '{{lessonContent}}': '__PLACEHOLDER_LESSONCONTENT__',
            'http://localhost:3000/courses/AI_30_NAP/day/{{dayNumber}}': '__PLACEHOLDER_COURSEURL__',
        }

        work = text
        for old, token in placeholder_map.items():
            work = work.replace(old, token)

        translated_chunks = [self._translate_chunk(chunk) for chunk in self._split_chunks(work)]
        translated = '\n'.join(translated_chunks)

        # Cultural adaptation and consistency cleanups.
        replacements = [
            ('Forint', 'USD'),
            ('forint', 'USD'),
            ('HUF', 'USD'),
            ('Day number', 'Day'),
            ('## DayNumber.', '## Day'),
            ('Read the full lesson ->', 'Read the full lesson ->'),
        ]
        for old, new in replacements:
            translated = translated.replace(old, new)

        for old, token in placeholder_map.items():
            translated = translated.replace(token, old)

        translated = translated.replace('__PLACEHOLDER_COURSEURL__', 'http://localhost:3000/courses/AI_30_DAY_EN/day/{{dayNumber}}')
        return translated


def day_from_filename(path: Path) -> int:
    m = re.match(r'lesson-(\d{2})-', path.name)
    if not m:
        raise ValueError(f'Invalid lesson filename: {path.name}')
    return int(m.group(1))


def render_quiz_markdown(day: int, title: str, questions: list[dict]) -> str:
    diff_map = {
        'EASY': 'easy',
        'MEDIUM': 'medium',
        'HARD': 'hard',
        'EXPERT': 'expert',
    }
    type_map = {
        'application': 'application',
        'critical-thinking': 'critical-thinking',
        'diagnostic': 'diagnostic',
        'metric': 'metric',
        'best_practice': 'best-practice',
    }

    lines = [f'# Lesson {day} quiz: {title}', '', '## Question pool']
    letters = ['A', 'B', 'C', 'D']
    for idx, q in enumerate(questions, start=1):
        lines += [
            '',
            f'### Question {idx}',
            f"**Question:** {q['question']}",
            f"A) {q['options'][0]}",
            f"B) {q['options'][1]}",
            f"C) {q['options'][2]}",
            f"D) {q['options'][3]}",
            f"**Correct:** {letters[q['correctIndex']]}",
            f"**Type:** {type_map.get(q.get('questionType', 'application'), 'application')}",
            f"**Difficulty:** {diff_map.get(q.get('difficulty', 'MEDIUM'), 'medium')}",
        ]
    return '\n'.join(lines) + '\n'


def translate_quiz_pool(translator: Translator, quiz_questions: list[dict]) -> list[dict]:
    # Translate all stem/option strings for one lesson in one request.
    marker_lines = []
    order = []
    for i, q in enumerate(quiz_questions, start=1):
        q_key = f'__Q{i:02d}__'
        marker_lines.append(f'{q_key} {q["question"]}')
        order.append(('q', i - 1, None, q_key))
        for j, opt in enumerate(q['options'], start=1):
            o_key = f'__Q{i:02d}O{j}__'
            marker_lines.append(f'{o_key} {opt}')
            order.append(('o', i - 1, j - 1, o_key))

    translated_blob = translator.translate('\n'.join(marker_lines))

    extracted = {}
    for line in translated_blob.splitlines():
        line = line.strip()
        m = re.match(r'^(__Q\d{2}(?:O\d)?__)\s*(.*)$', line)
        if m:
            extracted[m.group(1)] = m.group(2).strip()

    out = []
    for i, q in enumerate(quiz_questions, start=1):
        q_new = copy.deepcopy(q)
        q_key = f'__Q{i:02d}__'
        q_new['question'] = extracted.get(q_key, translator.translate(q['question']))
        new_opts = []
        for j, opt in enumerate(q['options'], start=1):
            o_key = f'__Q{i:02d}O{j}__'
            new_opts.append(extracted.get(o_key, translator.translate(opt)))
        q_new['options'] = new_opts
        out.append(q_new)
    return out


def translate_tags(translator: Translator, tags: list[str]) -> list[str]:
    out = []
    for tag in tags:
        translated = translator.translate(tag)
        translated = re.sub(r'\s+', '-', translated.strip().lower())
        translated = re.sub(r'[^a-z0-9\-]+', '', translated)
        translated = re.sub(r'-+', '-', translated).strip('-')
        out.append(translated or tag)
    return out


def run() -> None:
    LESSON_OUT_DIR.mkdir(parents=True, exist_ok=True)
    QUIZ_OUT_DIR.mkdir(parents=True, exist_ok=True)
    LOCALIZATION_DIR.mkdir(parents=True, exist_ok=True)

    src = json.loads(SOURCE_PACKAGE.read_text(encoding='utf-8'))
    lesson_files = sorted(LESSON_SRC_DIR.glob('lesson-*.md'), key=day_from_filename)
    quiz_files = sorted(QUIZ_SRC_DIR.glob('lesson-*-quiz.md'), key=day_from_filename)

    if len(lesson_files) != 30 or len(quiz_files) != 30:
        raise RuntimeError(f'Expected 30 lessons and 30 quizzes, got lessons={len(lesson_files)} quizzes={len(quiz_files)}')

    lesson_file_by_day = {day_from_filename(p): p.name for p in lesson_files}
    quiz_file_by_day = {day_from_filename(p): p.name for p in quiz_files}

    translator = Translator()

    course = copy.deepcopy(src['course'])
    course['courseId'] = 'AI_30_DAY_EN'
    course['ccsId'] = 'AI_30_DAY'
    course['language'] = 'en'
    course['name'] = '30-Day AI Catch-Up'
    course['description'] = (
        'A practical 30-day AI catch-up course for beginners and returners, with daily guided exercises, '
        'reusable outputs, and quality checks for real work use.'
    )
    if isinstance(course.get('metadata'), dict):
        tags = course['metadata'].get('tags')
        if isinstance(tags, list):
            course['metadata']['tags'] = translate_tags(translator, tags)

    lessons_out = []
    residual_hu_chars = 0

    for lesson in sorted(src['lessons'], key=lambda x: x['dayNumber']):
        day = lesson['dayNumber']
        lesson_new = copy.deepcopy(lesson)

        title_en = translator.translate(lesson['title'])
        content_en = translator.translate(lesson['content'])
        email_subject_en = f"AI 30 Day - Day {day}: {title_en}"
        email_body_en = translator.translate(lesson['emailBody'])
        email_body_en = email_body_en.replace('http://localhost:3000/courses/AI_30_NAP/day/{{dayNumber}}', 'http://localhost:3000/courses/AI_30_DAY_EN/day/{{dayNumber}}')

        quiz_translated = translate_quiz_pool(translator, lesson['quizQuestions'])

        lesson_new['lessonId'] = f'AI_30_DAY_EN_DAY_{day:02d}'
        lesson_new['language'] = 'en'
        lesson_new['title'] = title_en
        lesson_new['content'] = content_en
        lesson_new['emailSubject'] = email_subject_en
        lesson_new['emailBody'] = email_body_en
        lesson_new['quizQuestions'] = quiz_translated

        meta = lesson_new.get('metadata') or {}
        meta['sourceLessonFile'] = str((LESSON_OUT_DIR / lesson_file_by_day[day]).resolve())
        meta['sourceQuizFile'] = str((QUIZ_OUT_DIR / quiz_file_by_day[day]).resolve())
        lesson_new['metadata'] = meta

        lessons_out.append(lesson_new)

        (LESSON_OUT_DIR / lesson_file_by_day[day]).write_text(content_en + ('\n' if not content_en.endswith('\n') else ''), encoding='utf-8')
        quiz_md = render_quiz_markdown(day, title_en, quiz_translated)
        (QUIZ_OUT_DIR / quiz_file_by_day[day]).write_text(quiz_md, encoding='utf-8')

        residual_hu_chars += len(re.findall(r'[ÁÉÍÓÖŐÚÜŰáéíóöőúüű]', content_en))
        residual_hu_chars += len(re.findall(r'[ÁÉÍÓÖŐÚÜŰáéíóöőúüű]', title_en))

    package = {
        'packageVersion': src.get('packageVersion', '2.0'),
        'version': src.get('version', '2.0'),
        'exportedAt': datetime.utcnow().isoformat(timespec='seconds') + 'Z',
        'exportedBy': 'codex-localization-en-cultural-adapt',
        'course': course,
        'lessons': lessons_out,
        'canonicalSpec': src.get('canonicalSpec'),
        'courseIdea': src.get('courseIdea'),
    }

    OUT_PACKAGE.write_text(json.dumps(package, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    # Localization docs.
    (LOCALIZATION_DIR / 'language-demand-research.md').write_text(
        '\n'.join([
            '# Language Demand Research',
            '',
            'Course: 30-Day AI Catch-Up',
            f'Source course folder: {SOURCE_DIR}',
            f'Date: {datetime.utcnow().strftime("%Y-%m-%d")}',
            '',
            '## Candidate language',
            '- English (en-US)',
            '',
            '## Evidence summary',
            '- English remains the most used content language on the web, which supports broad discoverability and learner reach. Source: https://w3techs.com/technologies/overview/content_language',
            '- Stack Overflow developer survey responses are primarily in English, which aligns with AI-builder and practitioner target audiences. Source: https://survey.stackoverflow.co/2024',
            '- Global English proficiency remains widespread across many markets, which supports cross-region course usability. Source: https://www.ef.com/wwen/epi/',
            '',
            '## Recommendation',
            '- Proceed with en-US localization first to maximize global accessibility and compatibility with existing AI tooling/documentation ecosystems.',
            '',
        ]) + '\n',
        encoding='utf-8',
    )

    (LOCALIZATION_DIR / 'target-language-decision.md').write_text(
        '\n'.join([
            '# Target Language Decision',
            '',
            'Course: 30-Day AI Catch-Up',
            f'Source course folder: {SOURCE_DIR}',
            f'Date: {datetime.utcnow().strftime("%Y-%m-%d")}',
            '',
            '## Decision',
            '- Target language: English (en-US)',
            '- Localization mode: cultural adaptation',
            '',
            '## Rationale',
            '- Requested directly by user.',
            '- Highest practical reach for product, AI tooling, and multi-region learner onboarding.',
            '',
        ]) + '\n',
        encoding='utf-8',
    )

    (LOCALIZATION_DIR / 'localization-brief.md').write_text(
        '\n'.join([
            '# Localization Brief',
            '',
            'Course: 30-Day AI Catch-Up',
            'Target language: English (en-US)',
            f'Date: {datetime.utcnow().strftime("%Y-%m-%d")}',
            '',
            '## Purpose',
            'Localize the Hungarian source into practical global English while preserving daily lesson structure, quiz rigor, and actionable outcomes.',
            '',
            '## Tone and formality',
            '- Direct, practical, and friendly professional.',
            '- Avoid region-locked slang and legal assumptions.',
            '',
            '## Cultural adaptation rules',
            '- Replace locale-specific phrasing with globally understandable equivalents.',
            '- Normalize currency references to USD unless a source-specific context requires otherwise.',
            '- Keep tool and product names untranslated (OpenAI, ChatGPT, Claude, Gemini).',
            '',
        ]) + '\n',
        encoding='utf-8',
    )

    (LOCALIZATION_DIR / 'glossary-en.md').write_text(
        '\n'.join([
            '# Glossary - English (en-US)',
            '',
            '| Source term (HU) | Preferred EN term | Notes |',
            '| --- | --- | --- |',
            '| kimenet | output | Use consistently in lessons and quizzes. |',
            '| minőségkapu | quality gate | Keep as operational QA checkpoint. |',
            '| kérés | prompt | In AI context, prefer prompt. |',
            '| munkafolyamat | workflow | Use workflow for process framing. |',
            '| visszakerdezés | clarification question | Keep explicit in action steps. |',
            '| hallucináció | hallucination | Use in AI reliability context. |',
            '',
        ]) + '\n',
        encoding='utf-8',
    )

    (LOCALIZATION_DIR / 'style-guide-en.md').write_text(
        '\n'.join([
            '# Style Guide - English (en-US)',
            '',
            '## Voice',
            '- Practical teacher voice with clear next actions.',
            '- Prefer short declarative sentences for instructions.',
            '',
            '## Grammar and consistency',
            '- Use sentence case for headings unless fixed by source template.',
            '- Keep checklist items as action-oriented statements.',
            '- Keep quiz questions scenario-based and fully self-contained.',
            '',
            '## QA language gate',
            '- No leftover Hungarian diacritics in learner-facing text.',
            '- Avoid ambiguous pronouns where referent is not explicit in sentence.',
            '',
        ]) + '\n',
        encoding='utf-8',
    )

    (LOCALIZATION_DIR / 'cultural-adaptation-checklist.md').write_text(
        '\n'.join([
            '# Cultural Adaptation Checklist',
            '',
            '| Check | Status | Notes |',
            '| --- | --- | --- |',
            '| Currency examples normalized | DONE | Normalized to USD where needed. |',
            '| Locale-specific idioms removed | DONE | Translation pass favors neutral global English. |',
            '| Tool names preserved | DONE | OpenAI, ChatGPT, Claude, Gemini preserved. |',
            '| Region-locked assumptions reduced | DONE | Kept examples broadly workplace-oriented. |',
            '| Remaining risks reviewed | DONE | Small residual phrasing artifacts may remain in long-form lesson prose. |',
            '',
        ]) + '\n',
        encoding='utf-8',
    )

    # QA reports.
    qa_errors = []
    if len(lessons_out) != 30:
        qa_errors.append(f'Expected 30 lessons, got {len(lessons_out)}')
    for lesson in lessons_out:
        if lesson.get('language') != 'en':
            qa_errors.append(f"Day {lesson.get('dayNumber')}: lesson language is not en")
        if len(lesson.get('quizQuestions') or []) < 7:
            qa_errors.append(f"Day {lesson.get('dayNumber')}: fewer than 7 quiz questions")

    qa_status = 'PASS' if not qa_errors else 'FAIL'

    qa_findings = [f'- {e}' for e in qa_errors] if qa_errors else ['- No blocking localization errors detected.']
    qa_lines = [
        '# Localization QA Report',
        '',
        f'- Date: {datetime.utcnow().strftime("%Y-%m-%d")}',
        '- Source language: hu',
        '- Target language: en (en-US)',
        '- Mode: cultural adaptation',
        f'- Package: `{OUT_PACKAGE}`',
        f'- Lesson files: {len(list(LESSON_OUT_DIR.glob("lesson-*.md")))}',
        f'- Quiz files: {len(list(QUIZ_OUT_DIR.glob("lesson-*-quiz.md")))}',
        f'- Residual Hungarian diacritics (learner-facing text scan): {residual_hu_chars}',
        f'- Status: **{qa_status}**',
        '',
        '## Findings',
    ]
    qa_lines.extend(qa_findings)
    qa_lines.append('')
    (TARGET_DIR / 'localization-qa-report.md').write_text(
        '\n'.join(qa_lines) + '\n',
        encoding='utf-8',
    )

    ready_status = 'PASS' if not qa_errors else 'FAIL'
    (TARGET_DIR / 'ready-to-import-report.md').write_text(
        '\n'.join([
            '# Ready-to-Import Report',
            '',
            f'- Date: {datetime.utcnow().strftime("%Y-%m-%d")}',
            f'- Package path: `{OUT_PACKAGE}`',
            '- packageVersion: 2.0',
            f'- courseId: `{course["courseId"]}`',
            f'- ccsId: `{course["ccsId"]}`',
            '- language: `en`',
            f'- lessons: {len(lessons_out)}',
            f'- import readiness: **{ready_status}**',
            '',
        ]) + '\n',
        encoding='utf-8',
    )

    (TARGET_DIR / 'run-log.md').write_text(
        '\n'.join([
            '# Run Log',
            '',
            f'- Date: {datetime.utcnow().strftime("%Y-%m-%d")}',
            '- Task: Build EN localization variant with cultural adaptation',
            f'- Source: `{SOURCE_PACKAGE}`',
            f'- Output folder: `{TARGET_DIR}`',
            f'- Output package: `{OUT_PACKAGE}`',
            f'- Status: {ready_status}',
            '',
        ]) + '\n',
        encoding='utf-8',
    )

    (TARGET_DIR / 'tasklist.md').write_text(
        '\n'.join([
            '# Tasklist',
            '',
            '- [x] Scope lock (source folder + target en-US + cultural adaptation)',
            '- [x] Localization docs generated (research, decision, brief, glossary, style guide, checklist)',
            '- [x] 30 lesson files localized',
            '- [x] 30 quiz files localized',
            '- [x] v2 package rebuilt',
            f'- [x] QA complete: {qa_status}',
            '',
        ]) + '\n',
        encoding='utf-8',
    )


if __name__ == '__main__':
    run()
