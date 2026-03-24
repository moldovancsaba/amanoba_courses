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

SOURCE_DIR = Path('/Users/moldovancsaba/Projects/amanoba_courses/ai-30-day-en-cultural-adapt-2026-02-13')
TARGET_DIR = Path('/Users/moldovancsaba/Projects/amanoba_courses/ai-30-day-es-cultural-adapt-2026-02-13')
SOURCE_PACKAGE = SOURCE_DIR / 'AI_30_DAY_EN_export_2026-02-13_recreated.json'
OUT_PACKAGE = TARGET_DIR / 'AI_30_DAY_ES_export_2026-02-13_recreated.json'

LESSON_SRC_DIR = SOURCE_DIR / 'lessons'
QUIZ_SRC_DIR = SOURCE_DIR / 'quizzes'
LESSON_OUT_DIR = TARGET_DIR / 'lessons'
QUIZ_OUT_DIR = TARGET_DIR / 'quizzes'
LOCALIZATION_DIR = TARGET_DIR / 'localization'


class Translator:
    def __init__(self):
        self.translator = GoogleTranslator(source='en', target='es')
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
                time.sleep(0.2)
                return translated
            except Exception as err:
                last_error = err
                time.sleep(1.0 + (attempt * 0.8))
        raise RuntimeError(f'Translation failed after retries: {last_error}')

    def translate(self, text: str) -> str:
        if not text:
            return text

        placeholder_map = {
            '{{courseName}}': '__PLACEHOLDER_COURSENAME__',
            '{{dayNumber}}': '__PLACEHOLDER_DAYNUMBER__',
            '{{lessonTitle}}': '__PLACEHOLDER_LESSONTITLE__',
            '{{lessonContent}}': '__PLACEHOLDER_LESSONCONTENT__',
            'http://localhost:3000/courses/AI_30_DAY_EN/day/{{dayNumber}}': '__PLACEHOLDER_COURSEURL__',
            '**Skeleton ID:**': '__PLACEHOLDER_SID__',
            '**Skeleton Family:**': '__PLACEHOLDER_SFAM__',
            '**Skeleton Level:**': '__PLACEHOLDER_SLVL__',
            '**Question:**': '__PLACEHOLDER_Q__',
            '**Correct:**': '__PLACEHOLDER_C__',
            '**Type:**': '__PLACEHOLDER_T__',
            '**Difficulty:**': '__PLACEHOLDER_D__',
            '> **Pro tip:**': '__PLACEHOLDER_PROTIP__',
            '> **Common mistake:**': '__PLACEHOLDER_COMMON__',
            '## Learning goal': '__PLACEHOLDER_H2_LG__',
            '## Who': '__PLACEHOLDER_H2_WHO__',
            '## What': '__PLACEHOLDER_H2_WHAT__',
            '## Where': '__PLACEHOLDER_H2_WHERE__',
            '## When': '__PLACEHOLDER_H2_WHEN__',
            '## Why it matters': '__PLACEHOLDER_H2_WHY__',
            '## How': '__PLACEHOLDER_H2_HOW__',
            '## Guided exercise': '__PLACEHOLDER_H2_GUIDED__',
            '## Independent exercise': '__PLACEHOLDER_H2_INDEP__',
            '## Self-check': '__PLACEHOLDER_H2_SELF__',
            '## Bibliography': '__PLACEHOLDER_H2_BIB__',
            '## Read more': '__PLACEHOLDER_H2_READMORE__',
            '### Success criteria (observable)': '__PLACEHOLDER_H3_SUCCESS__',
            '### Output you will create today': '__PLACEHOLDER_H3_OUTPUT__',
            '### What is this?': '__PLACEHOLDER_H3_WI__',
            "### What isn't this?": '__PLACEHOLDER_H3_WIN__',
            '### 2-minute theory': '__PLACEHOLDER_H3_2MIN__',
            '### Key concepts': '__PLACEHOLDER_H3_KEY__',
            '### It works fine here': '__PLACEHOLDER_H3_WORKS__',
            '### Do not use this when': '__PLACEHOLDER_H3_DONT__',
            '### Connection points': '__PLACEHOLDER_H3_CONN__',
            '### Use it when': '__PLACEHOLDER_H3_USE__',
            '### Frequency': '__PLACEHOLDER_H3_FREQ__',
            '### Late warning signs': '__PLACEHOLDER_H3_WARN__',
            '### Practical benefits': '__PLACEHOLDER_H3_BEN__',
            '### What happens if you skip it': '__PLACEHOLDER_H3_SKIP__',
            '### Realistic expectation': '__PLACEHOLDER_H3_REAL__',
            '### Step by step': '__PLACEHOLDER_H3_STEPS__',
            "### Do / Don't": '__PLACEHOLDER_H3_DODO__',
            '### Common errors and their correction': '__PLACEHOLDER_H3_ERR__',
            '### Tool recommendations': '__PLACEHOLDER_H3_TOOLS__',
            '### Source transparency': '__PLACEHOLDER_H3_SRC__',
            '### Used sources': '__PLACEHOLDER_H3_USED__',
            '### Checked but not used sources': '__PLACEHOLDER_H3_CHK__',
            '### Further materials': '__PLACEHOLDER_H3_FUR__',
        }

        work = text
        for old, token in placeholder_map.items():
            work = work.replace(old, token)

        translated_chunks = [self._translate_chunk(chunk) for chunk in self._split_chunks(work)]
        translated = '\n'.join(translated_chunks)

        for old, token in placeholder_map.items():
            translated = translated.replace(token, old)

        translated = translated.replace('__PLACEHOLDER_COURSEURL__', 'http://localhost:3000/courses/AI_30_DAY_ES/day/{{dayNumber}}')
        return translated


def day_from_filename(path: Path) -> int:
    m = re.match(r'lesson-(\d{2})-', path.name)
    if not m:
        raise ValueError(f'Invalid lesson filename: {path.name}')
    return int(m.group(1))


def translate_lesson_content(translator: Translator, text: str, day: int) -> tuple[str, str]:
    lines = text.splitlines()
    out = []
    lesson_title = None
    for i, line in enumerate(lines):
        if i == 0 and line.startswith('# Lesson '):
            m = re.match(r'^# Lesson (\d+):\s*(.+)$', line)
            if m:
                translated_title = translator.translate(m.group(2)).strip()
                translated_title = translated_title.rstrip('.')
                line = f'# Lesson {int(m.group(1))}: {translated_title}'
                lesson_title = translated_title
        elif line.startswith('**In one sentence:**'):
            p = line.split(':', 1)
            tail = translator.translate(p[1].strip()) if len(p) > 1 else ''
            line = f'**In one sentence:** {tail}'
        elif line.startswith('**Time:**'):
            tail = line.split(':', 1)[1].strip() if ':' in line else ''
            line = f'**Time:** {tail}'
        elif line.startswith('**Tangible output:**'):
            p = line.split(':', 1)
            tail = translator.translate(p[1].strip()) if len(p) > 1 else ''
            line = f'**Tangible output:** {tail}'
        elif line.startswith('- **Name:**'):
            p = line.split(':', 1)
            tail = translator.translate(p[1].strip()) if len(p) > 1 else ''
            line = f'- **Name:** {tail}'
        elif line.startswith('- **Format:**'):
            p = line.split(':', 1)
            tail = translator.translate(p[1].strip()) if len(p) > 1 else ''
            line = f'- **Format:** {tail}'
        elif line.startswith('- **Where saved:**'):
            line = line
        elif line.startswith('|'):
            if re.match(r'^\|\s*[-: ]+\|', line):
                line = line
            else:
                parts = line.split('|')
                new_parts = [parts[0]]
                for part in parts[1:-1]:
                    cell = part.strip()
                    new_parts.append(' ' + (translator.translate(cell) if cell else '') + ' ')
                new_parts.append(parts[-1])
                line = '|'.join(new_parts)
        elif line.startswith('A) ') or line.startswith('B) ') or line.startswith('C) ') or line.startswith('D) '):
            pref = line[:3]
            line = pref + translator.translate(line[3:].strip())
        elif re.match(r'^\*\*(Question|Correct|Type|Difficulty):\*\*', line):
            key, val = line.split(':', 1)
            if key == '**Question**':
                line = f'{key}: {translator.translate(val.strip())}'
            else:
                line = line
        elif line.startswith('- [ ]'):
            line = '- [ ] ' + translator.translate(line[5:].strip())
        elif line.startswith('- '):
            line = '- ' + translator.translate(line[2:].strip())
        elif line.startswith('1. ') or line.startswith('2. ') or line.startswith('3. ') or line.startswith('4. ') or line.startswith('5. '):
            pref, tail = line.split(' ', 1)
            line = f'{pref} {translator.translate(tail.strip())}'
        elif line.strip() and not line.startswith('#') and not line.startswith('> **Pro tip:**') and not line.startswith('> **Common mistake:**'):
            line = translator.translate(line)
        elif line.startswith('> **Pro tip:**'):
            tail = line[len('> **Pro tip:**'):].strip()
            line = '> **Pro tip:** ' + translator.translate(tail)
        elif line.startswith('> **Common mistake:**'):
            tail = line[len('> **Common mistake:**'):].strip()
            line = '> **Common mistake:** ' + translator.translate(tail)

        out.append(line)

    text_out = '\n'.join(out).strip() + '\n'
    if lesson_title is None:
        lesson_title = f'Lección {day}'
    return text_out, lesson_title


def parse_quiz_blocks(text: str) -> list[str]:
    return [b.strip() for b in text.split('\n---\n') if '**Question:**' in b]


def translate_quiz_markdown(translator: Translator, text: str) -> tuple[str, list[dict], str]:
    m_header = re.search(r'^# Lesson\s+(\d+)\s+quiz:\s*(.+)$', text, re.M)
    day = int(m_header.group(1)) if m_header else 0
    title_src = m_header.group(2).strip() if m_header else 'Quiz'
    title_out = translator.translate(title_src)

    lines = [f'# Lesson {day} quiz: {title_out}', '', '## Question pool']
    out_questions = []

    blocks = parse_quiz_blocks(text)
    for idx, b in enumerate(blocks, start=1):
        sid = re.search(r'\*\*Skeleton ID:\*\*\s*(.+)', b)
        sfam = re.search(r'\*\*Skeleton Family:\*\*\s*(.+)', b)
        slvl = re.search(r'\*\*Skeleton Level:\*\*\s*(.+)', b)
        q = re.search(r'\*\*Question:\*\*\s*(.+)', b)
        opts = re.findall(r'^[A-D]\)\s+(.+)$', b, re.M)
        cor = re.search(r'\*\*Correct:\*\*\s*([A-D])', b)
        typ = re.search(r'\*\*Type:\*\*\s*(.+)', b)
        dif = re.search(r'\*\*Difficulty:\*\*\s*(.+)', b)

        q_text = translator.translate(q.group(1).strip()) if q else ''
        opt_out = [translator.translate(o.strip()) for o in opts]
        while len(opt_out) < 4:
            opt_out.append('')

        lines += [
            '',
            f'### Question {idx}',
            f'**Skeleton ID:** {(sid.group(1).strip() if sid else "S00_PLACEHOLDER")}',
            f'**Skeleton Family:** {(sfam.group(1).strip() if sfam else "placeholder_family")}',
            f'**Skeleton Level:** {(slvl.group(1).strip().lower() if slvl else "foundation")}',
            f'**Question:** {q_text}',
            f'A) {opt_out[0]}',
            f'B) {opt_out[1]}',
            f'C) {opt_out[2]}',
            f'D) {opt_out[3]}',
            f'**Correct:** {(cor.group(1).strip() if cor else "A")}',
            f'**Type:** {(typ.group(1).strip() if typ else "application")}',
            f'**Difficulty:** {(dif.group(1).strip().lower() if dif else "medium")}',
            '',
            '---',
        ]

        correct_letter = (cor.group(1).strip() if cor else 'A')
        correct_index = ord(correct_letter) - ord('A')
        question_type = (typ.group(1).strip() if typ else 'application')
        difficulty = (dif.group(1).strip().lower() if dif else 'medium')

        out_questions.append(
            {
                'question': q_text,
                'options': opt_out,
                'correctIndex': max(0, min(3, correct_index)),
                'questionType': question_type,
                'category': question_type,
                'difficulty': difficulty,
            }
        )

    quiz_text = '\n'.join(lines).rstrip() + '\n'
    return quiz_text, out_questions, title_out


def run() -> None:
    LESSON_OUT_DIR.mkdir(parents=True, exist_ok=True)
    QUIZ_OUT_DIR.mkdir(parents=True, exist_ok=True)
    LOCALIZATION_DIR.mkdir(parents=True, exist_ok=True)

    src = json.loads(SOURCE_PACKAGE.read_text(encoding='utf-8'))
    lesson_files = sorted(LESSON_SRC_DIR.glob('lesson-*.md'), key=day_from_filename)
    quiz_files = sorted(QUIZ_SRC_DIR.glob('lesson-*-quiz.md'), key=day_from_filename)

    if len(lesson_files) != 30 or len(quiz_files) != 30:
        raise RuntimeError(f'Expected 30 lessons and 30 quizzes, got lessons={len(lesson_files)} quizzes={len(quiz_files)}')

    lesson_file_by_day = {day_from_filename(p): p for p in lesson_files}
    quiz_file_by_day = {day_from_filename(p): p for p in quiz_files}

    translator = Translator()

    course = copy.deepcopy(src['course'])
    course['courseId'] = 'AI_30_DAY_ES'
    course['ccsId'] = 'AI_30_DAY'
    course['language'] = 'es'
    course['name'] = translator.translate(src['course'].get('name', '30-Day AI Catch-Up'))
    course['description'] = translator.translate(src['course'].get('description', ''))

    lessons_out = []

    for lesson in sorted(src['lessons'], key=lambda x: x['dayNumber']):
        day = int(lesson['dayNumber'])
        lesson_new = copy.deepcopy(lesson)

        lesson_src_path = lesson_file_by_day[day]
        quiz_src_path = quiz_file_by_day[day]

        lesson_text_src = lesson_src_path.read_text(encoding='utf-8')
        lesson_text_out, lesson_title = translate_lesson_content(translator, lesson_text_src, day)
        (LESSON_OUT_DIR / lesson_src_path.name).write_text(lesson_text_out, encoding='utf-8')

        quiz_text_src = quiz_src_path.read_text(encoding='utf-8')
        quiz_text_out, quiz_questions_out, quiz_title = translate_quiz_markdown(translator, quiz_text_src)
        (QUIZ_OUT_DIR / quiz_src_path.name).write_text(quiz_text_out, encoding='utf-8')

        email_body = translator.translate(lesson.get('emailBody') or '')
        email_body = email_body.replace(
            'http://localhost:3000/courses/AI_30_DAY_EN/day/{{dayNumber}}',
            'http://localhost:3000/courses/AI_30_DAY_ES/day/{{dayNumber}}',
        )

        lesson_new['lessonId'] = f'AI_30_DAY_ES_DAY_{day:02d}'
        lesson_new['language'] = 'es'
        lesson_new['title'] = lesson_title
        lesson_new['content'] = lesson_text_out.rstrip('\n')
        lesson_new['emailSubject'] = f'IA 30 dias - Dia {day}: {lesson_title}'
        lesson_new['emailBody'] = email_body

        existing_questions = lesson.get('quizQuestions') or []
        merged_questions = []
        for i, q_new in enumerate(quiz_questions_out):
            base = copy.deepcopy(existing_questions[i]) if i < len(existing_questions) else {}
            base['question'] = q_new['question']
            base['options'] = q_new['options']
            base['correctIndex'] = q_new['correctIndex']
            base['questionType'] = q_new['questionType']
            base['category'] = q_new['category']
            base['difficulty'] = q_new['difficulty']
            merged_questions.append(base)
        lesson_new['quizQuestions'] = merged_questions

        meta = lesson_new.get('metadata') or {}
        meta['sourceLessonFile'] = str((LESSON_OUT_DIR / lesson_src_path.name).resolve())
        meta['sourceQuizFile'] = str((QUIZ_OUT_DIR / quiz_src_path.name).resolve())
        lesson_new['metadata'] = meta

        lessons_out.append(lesson_new)

    package = {
        'packageVersion': src.get('packageVersion', '2.0'),
        'version': src.get('version', '2.0'),
        'exportedAt': datetime.utcnow().isoformat(timespec='seconds') + 'Z',
        'exportedBy': 'codex-localization-es-cultural-adapt',
        'course': course,
        'lessons': lessons_out,
        'canonicalSpec': src.get('canonicalSpec'),
        'courseIdea': src.get('courseIdea'),
    }

    OUT_PACKAGE.write_text(json.dumps(package, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    run()
