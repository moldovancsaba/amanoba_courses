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
    "képzeld el, hogy",
    "egy feladaton dolgozol, és döntened kell",
    "valós munkhelyzetben kell döntened",
    "munkhelyzetben",
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
    "konret opcio",
    "konkrét opció",
    "ez a legerősebb választás, mert javítja a döntés minőségét",
    "ez elsőre kényelmesnek tűnhet",
    "ez csak felszíni részletre reagál",
    "ez részleges javításnak látszik",
    "rovid valasz",
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
    re.compile(r"\bв\s+урока\b", re.I),
    re.compile(r"\b(w|na|z)\s+lekcji\b", re.I),
    re.compile(r"\bna\s+(liç(ão|ões)|aula)\b", re.I),
    re.compile(r"\bdalam\s+pelajaran\b", re.I),
    re.compile(r"\bderste\b", re.I),
    re.compile(r"\bفي\s+الدرس\b", re.I),
    re.compile(r"\bपाठ\s+में\b"),
    re.compile(r"\bkatika\s+somo\b", re.I),
]

COURSE_REFERENCE_PATTERNS = [
    re.compile(r"\b(this|the)\s+course\b", re.I),
    re.compile(r"\bfrom\s+this\s+course\b", re.I),
    re.compile(r"\bebben\s+a\s+kurzusban\b", re.I),
    re.compile(r"\bbu\s+kursta\b", re.I),
    re.compile(r"\bفي\s+هذه\s+الدورة\b", re.I),
    re.compile(r"\bइस\s+कोर्स\s+में\b"),
    re.compile(r"\bkatika\s+kozi\s+hii\b", re.I),
    re.compile(r"\bв\s+този\s+курс\b", re.I),
]

META_DISTRACTOR_PATTERNS = [
    re.compile(r"\b(wait|waiting)\b.*\b(someone else|others)\b", re.I),
    re.compile(r"\bjust\b.*\bread\b.*\bnot\b.*\b(apply|implement)\b", re.I),
    re.compile(r"\bmegvárom\b.*\b(valaki\s+más|más)\b", re.I),
]

LANGUAGE_MARKERS: dict[str, tuple[str, ...]] = {
    "en": (
        "learning goal",
        "why it matters",
        "explanation",
        "example",
        "guided exercise",
        "self-check",
        "today",
        "open the lesson",
    ),
    "hu": (
        "tanulási cél",
        "miért fontos",
        "magyarázat",
        "példa",
        "irányított gyakorlat",
        "önellenőrzés",
        "nyisd meg",
        "termelékenység",
    ),
    "pl": (
        "cel nauki",
        "dlaczego to ważne",
        "wyjaśnienie",
        "przykład",
        "ćwiczenie",
        "samokontrola",
        "produktywność",
        "otwórz lekcję",
    ),
    "pt": (
        "objetivo de aprendizado",
        "por que é importante",
        "explicação",
        "exemplo",
        "exercício guiado",
        "autoavaliação",
        "produtividade",
        "abra a lição",
    ),
    "vi": (
        "mục tiêu học tập",
        "tại sao điều này quan trọng",
        "giải thích",
        "ví dụ",
        "bài tập có hướng dẫn",
        "tự kiểm tra",
        "năng suất",
        "mở bài học",
    ),
    "es": (
        "objetivo de aprendizaje",
        "por qué importa",
        "explicación",
        "ejemplo",
        "ejercicio guiado",
        "autoevaluación",
        "abre la lección",
    ),
    "id": (
        "tujuan belajar",
        "mengapa ini penting",
        "penjelasan",
        "contoh",
        "latihan terpandu",
        "pemeriksaan mandiri",
        "buka pelajaran",
    ),
    "ar": (
        "هدف التعلّم",
        "لماذا هذا مهم",
        "الشرح",
        "مثال",
        "تمرين موجّه",
        "تحقق ذاتي",
        "افتح الدرس",
    ),
    "bg": (
        "учебна цел",
        "защо е важно",
        "обяснение",
        "пример",
        "насочено упражнение",
        "самопроверка",
        "отвори урока",
    ),
    "hi": (
        "सीखने का लक्ष्य",
        "यह क्यों महत्वपूर्ण है",
        "व्याख्या",
        "उदाहरण",
        "निर्देशित अभ्यास",
        "स्व-जांच",
        "पाठ खोलें",
    ),
    "ru": (
        "цель обучения",
        "почему это важно",
        "объяснение",
        "пример",
        "упражнение",
        "самопроверка",
        "открой урок",
    ),
    "sw": (
        "lengo la kujifunza",
        "kwa nini hili ni muhimu",
        "maelezo",
        "mfano",
        "zoezi la mwongozo",
        "kujihakiki",
        "fungua somo",
    ),
    "sv": (
        "lärandemål",
        "varför det är viktigt",
        "förklaring",
        "exempel",
        "guidad övning",
        "självkontroll",
        "öppna lektionen",
    ),
    "tr": (
        "öğrenme hedefi",
        "neden önemli",
        "açıklama",
        "örnek",
        "yönlendirmeli alıştırma",
        "öz kontrol",
        "dersi aç",
    ),
}

GENERIC_LANGUAGE_MARKERS: dict[str, tuple[str, ...]] = {
    "en": ("what", "which", "should", "because", "situation", "decision", "best", "most"),
    "hu": ("miért", "melyik", "hogyan", "helyzet", "döntés", "mert", "érdemes", "legjobb"),
    "pl": ("dlaczego", "który", "jak", "sytuacja", "decyzja", "ponieważ", "najlepszy"),
    "pt": ("por que", "qual", "como", "situação", "decisão", "melhor", "porque"),
    "vi": ("tại sao", "điều gì", "tình huống", "quyết định", "nên", "phù hợp"),
    "es": ("por qué", "cuál", "cómo", "situación", "decisión", "mejor", "debería"),
    "id": ("mengapa", "mana", "bagaimana", "situasi", "keputusan", "sebaiknya"),
    "ar": ("لماذا", "ما", "أي", "موقف", "قرار", "أفضل", "ينبغي"),
    "bg": ("защо", "кой", "как", "ситуация", "решение", "най", "трябва"),
    "hi": ("क्यों", "कौन", "कैसे", "स्थिति", "निर्णय", "सही", "चाहिए"),
    "ru": ("почему", "какой", "как", "ситуация", "решение", "лучше"),
    "sw": ("kwa nini", "ipi", "jinsi", "hali", "uamuzi", "bora", "inapaswa"),
    "sv": ("varför", "vilket", "hur", "situation", "beslut", "bäst"),
    "tr": ("neden", "hangi", "nasıl", "durum", "karar", "doğru", "gerekir"),
}


def _language_scores(text: str) -> dict[str, int]:
    lowered = text.lower()
    scores: dict[str, int] = {}
    for code, markers in LANGUAGE_MARKERS.items():
        scores[code] = sum(1 for marker in markers if marker in lowered)
    return scores


def _generic_language_scores(text: str) -> dict[str, int]:
    lowered = text.lower()
    scores: dict[str, int] = {}
    for code, markers in GENERIC_LANGUAGE_MARKERS.items():
        total = 0
        for marker in markers:
            pattern = r"\b" + re.escape(marker) + r"\b"
            if re.search(pattern, lowered):
                total += 1
        scores[code] = total
    return scores


def _language_purity_errors(
    texts: list[str],
    target_language: str | None,
    *,
    allow_english_fallback: bool = False,
) -> list[str]:
    target = str(target_language or "").strip().lower()
    if target not in LANGUAGE_MARKERS:
        return []
    combined = "\n".join(str(text or "") for text in texts if str(text or "").strip())
    if not combined.strip():
        return []
    scores = _language_scores(combined)
    generic_scores = _generic_language_scores(combined)
    target_score = int(scores.get(target, 0)) + int(generic_scores.get(target, 0))
    english_score = int(scores.get("en", 0)) + int(generic_scores.get("en", 0))
    foreign_hits = {}
    for code in set(scores) | set(generic_scores):
        if code in {target, "en"}:
            continue
        score = int(scores.get(code, 0)) + int(generic_scores.get(code, 0))
        if score > 0:
            foreign_hits[code] = score
    if target == "en":
        foreign_hits = {code: score for code, score in foreign_hits.items() if int(scores.get(code, 0)) > 0}
    if foreign_hits:
        top_code, top_score = max(foreign_hits.items(), key=lambda item: item[1])
        if top_score > 0:
            return [f"Content mixes languages. Detected {top_code} markers inside {target} content."]
    if english_score > 0 and target != "en":
        if allow_english_fallback and target_score == 0:
            return []
        return [f"Content mixes English into {target} content, which is not allowed."]
    if target_score == 0 and target != "en":
        return [f"Content does not show clear {target} language markers."]
    return []


def _contains_any(text: str, patterns: list[str]) -> str | None:
    lowered = text.lower()
    for pattern in patterns:
        if pattern in lowered:
            return pattern
    return None


def _option_shape(option: str) -> str:
    text = str(option or "").strip()
    lowered = text.lower()
    comma_count = text.count(",")
    if comma_count >= 2:
        return "list"
    if lowered.startswith(("csak ", "only ")):
        return "only"
    if len(text.split()) <= 4:
        return "short-fragment"
    return "sentence"


def _structural_option_errors(options: list[str], correct_index: int | None) -> list[str]:
    errors: list[str] = []
    clean = [str(option or "").strip() for option in options]
    if len(clean) < 4:
        return errors

    shapes = [_option_shape(option) for option in clean]
    non_correct_shapes = [shape for index, shape in enumerate(shapes) if index != correct_index]

    if isinstance(correct_index, int) and 0 <= correct_index < len(clean):
        correct_shape = shapes[correct_index]
        if correct_shape == "list" and any(shape != "list" for shape in non_correct_shapes):
            errors.append("Options use inconsistent structures: the correct answer is a list while distractors are not parallel lists.")
        if correct_shape != "list" and all(shape == "list" for shape in non_correct_shapes):
            errors.append("Options use inconsistent structures: distractors are list-shaped while the correct answer is not.")

    only_count = sum(1 for shape in shapes if shape == "only")
    if only_count >= 2:
        errors.append("Distractors overuse 'only/csak' phrasing, which makes the correct answer too obvious.")

    short_count = sum(1 for shape in shapes if shape == "short-fragment")
    if short_count >= 2:
        errors.append("Too many options are trivial short fragments instead of plausible domain answers.")

    comma_counts = [option.count(",") for option in clean]
    if max(comma_counts, default=0) >= 3 and min(comma_counts, default=0) == 0:
        errors.append("Option set is structurally unbalanced: one answer is a detailed field list while others are simplistic single items.")

    return errors


def validate_question(question: dict[str, Any], target_language: str | None = None) -> ValidationResult:
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
    else:
        errors.extend(_structural_option_errors([str(option) for option in options], correct_index))

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

    errors.extend(_language_purity_errors([stem, *[str(option) for option in options]], target_language))

    if isinstance(correct_index, int) and 0 <= correct_index < len(options):
        if len(str(options[correct_index]).strip()) < 35:
            warnings.append("Correct answer is short; quality may still be weak.")

    return ValidationResult(is_valid=not errors, errors=errors, warnings=warnings)


def audit_lesson(lesson: dict[str, Any], target_language: str | None = None) -> ValidationResult:
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

    errors.extend(_language_purity_errors([title, content, email_subject, email_body], target_language))

    return ValidationResult(is_valid=not errors, errors=errors, warnings=warnings)
