from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


QUESTION_PATTERNS = [
    "what is a key concept from",
    "mi a kulcsfontosságú koncepció",
    "mit jelent a \"",
    "what does \"",
    "a leckében leírt",
    "a leckében szereplő",
    "as described in the lesson",
    "described in the lesson",
    "follow the method described in the lesson",
]

ANSWER_PATTERNS = [
    "a fundamental principle related to this topic",
    "an advanced technique not covered here",
    "a completely unrelated concept",
    "a basic misunderstanding",
    "no significant impact",
    "only matters theoretically",
    "not mentioned in the lesson",
    "as described in the lesson",
]

LESSON_REFERENCE_PATTERNS = [
    re.compile(r"\b(in|from|as)\s+(described\s+in\s+)?the\s+lesson\b", re.I),
    re.compile(r"\b(described|discussed)\s+in\s+the\s+lesson\b", re.I),
    re.compile(r"\b(a|az)\s+leck(ében|e)\b", re.I),
    re.compile(r"\bleckében\b", re.I),
    re.compile(r"\bв\s+уроке\b", re.I),
    re.compile(r"\b(w|na|z)\s+lekcji\b", re.I),
    re.compile(r"\bna\s+(liç(ão|ões)|aula)\b", re.I),
    re.compile(r"\bdalam\s+pelajaran\b", re.I),
]

COURSE_REFERENCE_PATTERNS = [
    re.compile(r"\b(this|the)\s+course\b", re.I),
    re.compile(r"\bfrom\s+this\s+course\b", re.I),
    re.compile(r"\bebben\s+a\s+kurzusban\b", re.I),
]

META_DISTRACTOR_PATTERNS = [
    re.compile(r"\b(wait|waiting)\b.*\b(someone else|others)\b", re.I),
    re.compile(r"\bjust\b.*\bread\b.*\bnot\b.*\b(apply|implement)\b", re.I),
    re.compile(r"\bmegvárom\b.*\b(valaki\s+más|más)\b", re.I),
]


def _contains_any(text: str, patterns: list[str]) -> str | None:
    lowered = text.lower()
    for pattern in patterns:
        if pattern in lowered:
            return pattern
    return None


def validate_question(question: dict[str, Any]) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    stem = str(question.get("question", "")).strip()
    options = question.get("options") or []
    correct_index = question.get("correctIndex")
    question_type = str(question.get("questionType", "")).strip().lower()

    if len(stem) < 40:
        errors.append("Question stem must be at least 40 characters.")

    if not isinstance(options, list) or len(options) < 2:
        errors.append("Question must have at least 2 options.")
        options = []

    for idx, option in enumerate(options):
        option_text = str(option).strip()
        if len(option_text) < 25:
            errors.append(f"Option {idx} must be at least 25 characters.")
        match = _contains_any(option_text, ANSWER_PATTERNS)
        if match:
            errors.append(f"Option {idx} contains a banned generic answer pattern: {match!r}.")
        for regex in LESSON_REFERENCE_PATTERNS:
            if regex.search(option_text):
                errors.append(f"Option {idx} references the lesson directly.")
                break
        for regex in COURSE_REFERENCE_PATTERNS:
            if regex.search(option_text):
                errors.append(f"Option {idx} references the course directly.")
                break
        for regex in META_DISTRACTOR_PATTERNS:
            if regex.search(option_text):
                errors.append(f"Option {idx} is a meta distractor instead of a domain mistake.")
                break

    if not isinstance(correct_index, int) or correct_index < 0 or correct_index >= len(options):
        errors.append("correctIndex must point to an existing option.")

    match = _contains_any(stem, QUESTION_PATTERNS)
    if match:
        errors.append(f"Question contains a banned template pattern: {match!r}.")

    for regex in LESSON_REFERENCE_PATTERNS:
        if regex.search(stem):
            errors.append("Question references the lesson directly.")
            break

    for regex in COURSE_REFERENCE_PATTERNS:
        if regex.search(stem):
            errors.append("Question references the course directly.")
            break

    if question_type == "recall":
        errors.append("Recall questions are not allowed.")

    if isinstance(correct_index, int) and 0 <= correct_index < len(options):
        if len(str(options[correct_index]).strip()) < 35:
            warnings.append("Correct answer is short; quality may still be weak.")

    return ValidationResult(is_valid=not errors, errors=errors, warnings=warnings)


def audit_lesson(lesson: dict[str, Any]) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    title = str(lesson.get("title", "")).strip()
    content = str(lesson.get("content", "")).strip()
    email_subject = str(lesson.get("emailSubject", "")).strip()
    email_body = str(lesson.get("emailBody", "")).strip()

    if len(title) < 10:
        errors.append("Lesson title is too short.")
    if len(content) < 800:
        errors.append("Lesson content is too short to support high-quality quiz generation.")
    if content.count("\n") < 8:
        warnings.append("Lesson content is very compact; examples or structure may be missing.")
    if "##" not in content and "-" not in content and "1." not in content:
        warnings.append("Lesson has little visible structure.")
    if len(email_subject) < 8:
        warnings.append("Email subject is short.")
    if len(email_body) < 120:
        warnings.append("Email body is short.")

    return ValidationResult(is_valid=not errors, errors=errors, warnings=warnings)
