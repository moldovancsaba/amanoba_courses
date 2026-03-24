from __future__ import annotations

import json
import os
import re
import signal
import shutil
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from .validator import audit_lesson, validate_question


def _language_name(code: str | None) -> str:
    mapping = {
        "hu": "Hungarian",
        "en": "English",
        "es": "Spanish",
        "pt": "Portuguese",
        "id": "Indonesian",
        "pl": "Polish",
        "ru": "Russian",
        "sv": "Swedish",
    }
    return mapping.get(str(code or "").strip().lower(), str(code or "the target"))


def _language_tone_guide(code: str | None) -> str:
    guides = {
        "hu": "Write natural modern Hungarian. Avoid translated-sounding filler, corporate stiffness, and repeated stock phrases. Prefer clear, direct, idiomatic wording.",
        "en": "Write natural modern English. Avoid translationese, generic training jargon, and repetitive phrasing. Prefer concrete, fluent wording.",
        "es": "Write natural modern Spanish. Avoid literal translation patterns and stiff instructional prose. Prefer idiomatic, specific wording.",
        "pt": "Write natural modern Portuguese. Avoid literal translation patterns and stiff instructional prose. Prefer idiomatic, specific wording.",
        "id": "Write natural modern Indonesian. Avoid translated-sounding phrasing and generic filler. Prefer direct, clear, idiomatic wording.",
        "pl": "Write natural modern Polish. Avoid translated-sounding phrasing and generic filler. Prefer direct, clear, idiomatic wording.",
        "ru": "Write natural modern Russian. Avoid translated-sounding phrasing and generic filler. Prefer direct, clear, idiomatic wording.",
        "sv": "Write natural modern Swedish. Avoid translated-sounding phrasing and generic filler. Prefer direct, clear, idiomatic wording.",
    }
    return guides.get(str(code or "").strip().lower(), "Write in the target language with fluent, native-sounding wording.")


def _htmlish_to_text(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    text = re.sub(r"<\s*br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<\s*/p\s*>", "\n\n", text, flags=re.I)
    text = re.sub(r"<\s*/h[1-6]\s*>", "\n\n", text, flags=re.I)
    text = re.sub(r"<\s*li[^>]*>", "\n- ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = (
        text.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
    )
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _question_prompt(course: dict[str, Any], lesson: dict[str, Any], question: dict[str, Any], validation_errors: list[str]) -> str:
    language_code = str(lesson.get("language") or course.get("language") or "").strip().lower()
    language_name = _language_name(language_code)
    lesson_excerpt = str(lesson.get("content") or "").strip()[:4500]
    metadata = {
        "questionType": question.get("questionType") or "application",
        "difficulty": question.get("difficulty") or "medium",
        "category": question.get("category") or "course_quality",
        "hashtags": question.get("hashtags") or [],
    }
    return f"""
You are Amanoba's senior assessment writer.
Write one improved multiple-choice question in {language_name}.
Return strict JSON only.

Required JSON keys:
- question
- options
- correctIndex
- questionType
- difficulty
- category
- hashtags

Quality bar:
- {_language_tone_guide(language_code)}
- Sound like a strong local educator, not a translated template.
- Make the question concrete, specific, and useful in real work.
- The stem must describe a realistic decision, action, or judgement moment.
- Keep it standalone: no references to "the lesson", "the course", or other meta framing.
- Do not test recall. Test application, diagnosis, prioritization, or good judgement.
- Keep 4 answer options.
- Exactly 1 clearly best answer.
- Wrong answers must be plausible mistakes a learner could realistically make.
- Avoid repeating the same key phrase from the lesson across the stem and every option.
- Avoid generic filler like "something related", "not covered here", or "as described in the lesson".
- Keep the existing intent, topic, and language variant.

Length rules:
- question: at least 40 characters
- each option: at least 25 characters

Preserve or improve these metadata values unless there is a strong reason to change them:
{json.dumps(metadata, ensure_ascii=False)}

Course context:
{json.dumps({'courseId': course.get('courseId'), 'name': course.get('name'), 'language': course.get('language')}, ensure_ascii=False)}

Lesson context:
{json.dumps({'lessonId': lesson.get('lessonId'), 'title': lesson.get('title'), 'language': lesson.get('language')}, ensure_ascii=False)}

Lesson excerpt:
{lesson_excerpt}

Original question:
{json.dumps(question, ensure_ascii=False)}

Issues to fix:
{json.dumps(validation_errors, ensure_ascii=False)}
""".strip()


def _lesson_prompt(course: dict[str, Any], lesson: dict[str, Any], validation_errors: list[str]) -> str:
    language_code = str(lesson.get("language") or course.get("language") or "").strip().lower()
    language_name = _language_name(language_code)
    lesson_excerpt = _htmlish_to_text(str(lesson.get("content") or ""))[:4500]
    email_excerpt = _htmlish_to_text(str(lesson.get("emailBody") or ""))[:1200]
    return f"""
You are Amanoba's senior instructional writer.
Rewrite this lesson in {language_name}.
Return strict JSON only.

Required JSON keys:
- title
- content
- emailSubject
- emailBody

Forbidden keys and formats:
- do not return article/blog/webpage metadata
- do not return keys like text, date, author, image, description, publisher, @context, @type, url, datePublished, dateModified
- do not return schema.org JSON-LD
- do not return a web article object
- do not wrap the lesson in another object

Quality bar:
- {_language_tone_guide(language_code)}
- Keep the same topic and learning intent.
- Improve narrative flow, structure, clarity, and usefulness.
- Be specific and practical instead of generic.
- Keep Markdown lesson formatting. Do not return HTML as the preferred final lesson body.
- Do not invent unsupported claims or sources.
- Expand weak lessons into a complete teaching asset, not a short summary.
- Start with `{{` and end with `}}`.
- Output exactly one JSON object and nothing else.

Length and structure rules:
- content must be between 900 and 2200 characters
- content must include clear section headings
- content must include: learning goal, why it matters, explanation, examples, guided exercise, and self-check
- content must be valid Markdown using headings, lists, emphasis, and links where appropriate
- emailBody must be more informative than a one-line reminder
- emailBody should be between 120 and 500 characters
- emailBody should be Markdown, not HTML, unless preserving unavoidable legacy structure

Use this exact shape:
{{
  "title": "Localized lesson title",
  "content": "## Learning goal\\n...\\n\\n## Why it matters\\n...\\n\\n## Explanation\\n...\\n\\n## Example\\n...\\n\\n## Guided exercise\\n...\\n\\n## Self-check\\n...",
  "emailSubject": "Localized subject line",
  "emailBody": "## Today\\nShort localized summary with one clear call to open the lesson."
}}

Course:
{json.dumps({'courseId': course.get('courseId'), 'name': course.get('name'), 'language': course.get('language')}, ensure_ascii=False)}

Lesson:
{json.dumps({'lessonId': lesson.get('lessonId'), 'title': lesson.get('title'), 'language': lesson.get('language')}, ensure_ascii=False)}

Current lesson draft excerpt:
{lesson_excerpt}

Current email draft excerpt:
{email_excerpt}

Issues to fix:
{json.dumps(validation_errors, ensure_ascii=False)}
""".strip()


def _foreign_lesson_shape(candidate: dict[str, Any]) -> bool:
    forbidden = {
        "text",
        "date",
        "author",
        "image",
        "description",
        "publisher",
        "url",
        "datePublished",
        "dateModified",
        "@context",
        "@type",
        "headline",
        "mainEntityOfPage",
    }
    keys = {str(key) for key in candidate.keys()}
    return bool(keys & forbidden)


@dataclass
class RuntimeHealth:
    provider: str
    status: str
    detail: str
    available: bool
    configured_model: str | None = None
    resolved_model: str | None = None
    endpoint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "status": self.status,
            "detail": self.detail,
            "available": self.available,
            "configuredModel": self.configured_model,
            "resolvedModel": self.resolved_model,
            "endpoint": self.endpoint,
        }


class BaseProvider:
    name = "base"

    def health(self) -> RuntimeHealth:
        raise NotImplementedError

    def rewrite_question(
        self,
        course: dict[str, Any],
        lesson: dict[str, Any],
        question: dict[str, Any],
        validation_errors: list[str],
    ) -> dict[str, Any]:
        raise NotImplementedError

    def rewrite_lesson(
        self,
        course: dict[str, Any],
        lesson: dict[str, Any],
        validation_errors: list[str],
    ) -> dict[str, Any]:
        raise NotImplementedError


class OllamaProvider(BaseProvider):
    name = "ollama"

    def __init__(
        self,
        endpoint: str,
        model: str,
        timeout: int = 180,
        temperature: float = 0.1,
        num_predict: int = 384,
        num_ctx: int = 2048,
        num_thread: int = 2,
    ) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.temperature = temperature
        self.num_predict = num_predict
        self.num_ctx = num_ctx
        self.num_thread = num_thread

    def health(self) -> RuntimeHealth:
        try:
            body = self._request_json("/api/tags")
            models = [str(item.get("name") or item.get("model") or "").strip() for item in body.get("models", [])]
            models = [model for model in models if model]
            resolved = self.model if self.model in models else (models[0] if models else None)
            return RuntimeHealth(
                provider=self.name,
                status="HEALTHY" if resolved else "DEGRADED",
                detail="Ollama reachable." if resolved else "Ollama reachable but no suitable model found.",
                available=bool(resolved),
                configured_model=self.model,
                resolved_model=resolved,
                endpoint=self.endpoint,
            )
        except Exception as exc:
            return RuntimeHealth(
                provider=self.name,
                status="UNAVAILABLE",
                detail=str(exc),
                available=False,
                configured_model=self.model,
                endpoint=self.endpoint,
            )

    def rewrite_question(self, course: dict[str, Any], lesson: dict[str, Any], question: dict[str, Any], validation_errors: list[str]) -> dict[str, Any]:
        prompt = self._question_prompt(course, lesson, question, validation_errors)
        candidate = self._generate_json(prompt)
        if self._question_needs_repair(candidate):
            repair_prompt = (
                "Return strict JSON only. Repair this quiz question object so it fully matches the required schema. "
                "The current draft has broken structure or failed validation. "
                "Keep the language, topic, and strongest wording, but fix missing keys, malformed arrays, and weak distractors.\n\n"
                f"Original rewrite brief:\n{prompt}\n\n"
                f"Broken draft:\n{json.dumps(candidate, ensure_ascii=False)}"
            )
            candidate = self._generate_json(repair_prompt)
        return candidate

    def rewrite_lesson(self, course: dict[str, Any], lesson: dict[str, Any], validation_errors: list[str]) -> dict[str, Any]:
        prompt = self._lesson_prompt(course, lesson, validation_errors)
        candidate = self._generate_json(prompt, num_predict_override=max(self.num_predict, 1400))
        if self._lesson_needs_repair(candidate):
            repair_prompt = (
                "Return strict JSON only. Repair this lesson object so it fully matches the required schema. "
                "Output exactly one object with only these keys: title, content, emailSubject, emailBody. "
                "Do not output article metadata, schema.org, blog fields, author, image, description, text, date, publisher, or url.\n\n"
                f"Original rewrite brief:\n{prompt}\n\n"
                f"Broken draft:\n{json.dumps(candidate, ensure_ascii=False)}"
            )
            candidate = self._generate_json(repair_prompt, num_predict_override=max(self.num_predict, 1400))
        return candidate

    def _generate_json(self, prompt: str, num_predict_override: int | None = None) -> dict[str, Any]:
        health = self.health()
        if not health.available or not health.resolved_model:
            raise RuntimeError(f"Ollama not available: {health.detail}")
        num_predict = int(num_predict_override or self.num_predict)
        payload = {
            "model": health.resolved_model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": self.temperature,
                "num_predict": num_predict,
                "num_ctx": self.num_ctx,
                "num_thread": self.num_thread,
            },
        }
        body = self._request_json("/api/generate", payload)
        text = str(body.get("response") or "").strip()
        if not text:
            raise RuntimeError("Ollama returned empty response.")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        try:
            return json.loads(self._extract_json(text))
        except Exception:
            repair_prompt = (
                "Return strict JSON only. Do not explain. Do not add markdown. "
                "Repair this malformed JSON draft into one valid JSON object that matches the original task.\n\n"
                f"Original task prompt:\n{prompt}\n\n"
                f"Malformed draft:\n{text}"
            )
            repair_body = self._request_json(
                "/api/generate",
                {
                    "model": health.resolved_model,
                    "prompt": repair_prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0,
                        "num_predict": max(num_predict, 768),
                        "num_ctx": self.num_ctx,
                        "num_thread": self.num_thread,
                    },
                },
            )
            repaired = str(repair_body.get("response") or "").strip()
            if not repaired:
                raise RuntimeError("Ollama JSON repair returned empty response.")
            try:
                return json.loads(repaired)
            except json.JSONDecodeError:
                return json.loads(self._extract_json(repaired))

    def _request_json(self, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        data = None
        headers = {"Accept": "application/json"}
        method = "GET"
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
            method = "POST"
        req = urllib.request.Request(f"{self.endpoint}{path}", data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Ollama request failed: {exc}") from exc

    def _question_prompt(self, course: dict[str, Any], lesson: dict[str, Any], question: dict[str, Any], validation_errors: list[str]) -> str:
        return _question_prompt(course, lesson, question, validation_errors)

    def _lesson_prompt(self, course: dict[str, Any], lesson: dict[str, Any], validation_errors: list[str]) -> str:
        return _lesson_prompt(course, lesson, validation_errors)

    def _question_needs_repair(self, candidate: dict[str, Any]) -> bool:
        required = {"question", "options", "correctIndex", "questionType", "difficulty", "category", "hashtags"}
        if not required.issubset(candidate):
            return True
        return not validate_question(candidate).is_valid

    def _lesson_needs_repair(self, candidate: dict[str, Any]) -> bool:
        required = {"title", "content", "emailSubject", "emailBody"}
        if not required.issubset(candidate):
            return True
        if _foreign_lesson_shape(candidate):
            return True
        return not audit_lesson(candidate).is_valid

    def _extract_json(self, text: str) -> str:
        text = text.strip()
        if text.startswith("{") and text.endswith("}"):
            return text
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if match:
            return match.group(0)
        raise RuntimeError(f"Ollama did not return JSON: {text[:400]}")


class MLXProvider(BaseProvider):
    name = "mlx"

    def __init__(
        self,
        model: str,
        timeout: int = 180,
        max_tokens: int = 768,
        normalizer_endpoint: str = "http://127.0.0.1:11434",
        normalizer_model: str = "llama3.2:3b",
    ) -> None:
        self.model = model
        self.timeout = timeout
        self.max_tokens = max_tokens
        self._loaded: tuple[Any, Any] | None = None
        self.normalizer = OllamaProvider(normalizer_endpoint, normalizer_model)

    def _resolved_model_path(self) -> str:
        candidate = os.path.expanduser(self.model)
        if os.path.isdir(candidate):
            return candidate
        return self.model

    def health(self) -> RuntimeHealth:
        model_path = self._resolved_model_path()
        try:
            __import__("mlx_lm")
        except Exception as exc:
            return RuntimeHealth(self.name, "UNAVAILABLE", f"MLX generation runtime missing: {exc}", False, configured_model=self.model)
        if os.path.isdir(model_path):
            return RuntimeHealth(self.name, "HEALTHY", "MLX runtime available and local model path found.", True, configured_model=self.model, resolved_model=model_path)
        return RuntimeHealth(self.name, "UNAVAILABLE", f"MLX model path not found: {model_path}", False, configured_model=self.model)

    def rewrite_question(self, course: dict[str, Any], lesson: dict[str, Any], question: dict[str, Any], validation_errors: list[str]) -> dict[str, Any]:
        prompt = _question_prompt(course, lesson, question, validation_errors)
        candidate = self._generate_json(prompt)
        if self._question_needs_retry(question, candidate):
            retry_prompt = (
                f"{prompt}\n\n"
                "Your previous draft stayed too close to the weak original or kept invalid structure. "
                "Rewrite it again from scratch. Make it more concrete, more native-sounding, and more scenario-based. "
                "Do not keep the original wording if it was weak."
            )
            candidate = self._generate_json(retry_prompt)
        if self._question_needs_retry(question, candidate):
            return self._normalize_question_with_ollama(prompt, question, candidate)
        return candidate

    def rewrite_lesson(self, course: dict[str, Any], lesson: dict[str, Any], validation_errors: list[str]) -> dict[str, Any]:
        prompt = _lesson_prompt(course, lesson, validation_errors)
        candidate = self._generate_json(prompt, max_tokens_override=max(self.max_tokens, 1600))
        if self._lesson_needs_retry(lesson, candidate):
            retry_prompt = (
                f"{prompt}\n\n"
                "Your previous draft stayed too close to the weak original or did not materially improve the lesson. "
                "Rewrite it again with stronger structure, more useful flow, and more native-sounding wording."
            )
            candidate = self._generate_json(retry_prompt, max_tokens_override=max(self.max_tokens, 1600))
        if self._lesson_needs_retry(lesson, candidate):
            return self._normalize_lesson_with_ollama(prompt, lesson, candidate)
        return candidate

    def _load_once(self) -> tuple[Any, Any]:
        if self._loaded is None:
            from mlx_lm import load

            self._loaded = load(self._resolved_model_path())
        return self._loaded

    def _generate_json(self, prompt: str, max_tokens_override: int | None = None) -> dict[str, Any]:
        health = self.health()
        if not health.available:
            raise RuntimeError(f"MLX not available: {health.detail}")
        text = self._call_with_timeout(self._generate_text, prompt, max_tokens_override)
        try:
            cleaned = self._extract_json(text)
            return json.loads(cleaned)
        except Exception:
            repair_prompt = (
                "Convert the following draft into strict JSON only. "
                "Do not explain. Do not add markdown. Start with { and end with }.\n\n"
                f"Original task prompt:\n{prompt}\n\n"
                f"Draft to convert:\n{text}"
            )
            repaired = self._call_with_timeout(self._generate_text, repair_prompt, max_tokens_override)
            try:
                cleaned = self._extract_json(repaired)
                return json.loads(cleaned)
            except Exception:
                return self._normalize_with_ollama(prompt, repaired)

    def _call_with_timeout(self, fn: Any, *args: Any) -> Any:
        if self.timeout <= 0:
            return fn(*args)
        try:
            is_main_thread = __import__("threading").current_thread() is __import__("threading").main_thread()
        except Exception:
            is_main_thread = False
        if not is_main_thread or not hasattr(signal, "SIGALRM"):
            return fn(*args)

        class _MLXTimeout(Exception):
            pass

        def _handler(signum: int, frame: Any) -> None:
            raise _MLXTimeout()

        previous = signal.getsignal(signal.SIGALRM)
        signal.signal(signal.SIGALRM, _handler)
        signal.alarm(int(self.timeout))
        try:
            return fn(*args)
        except _MLXTimeout as exc:
            raise RuntimeError(f"MLX generation timed out after {self.timeout} seconds.") from exc
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, previous)

    def _generate_text(self, prompt: str, max_tokens_override: int | None = None) -> str:
        from mlx_lm import generate

        model, tokenizer = self._load_once()
        messages = [{"role": "user", "content": prompt}]
        if hasattr(tokenizer, "apply_chat_template"):
            rendered_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        else:
            rendered_prompt = prompt
        max_tokens = int(max_tokens_override or self.max_tokens)
        return generate(model, tokenizer, prompt=rendered_prompt, max_tokens=max_tokens, verbose=False)

    def _extract_json(self, text: str) -> str:
        text = text.strip()
        if text.startswith("{") and text.endswith("}"):
            return text
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if match:
            return match.group(0)
        raise RuntimeError(f"MLX did not return JSON: {text[:400]}")

    def _normalize_with_ollama(self, prompt: str, draft: str) -> dict[str, Any]:
        normalize_prompt = (
            "Return strict JSON only. Preserve the writer's meaning, language, and tone while converting it into valid JSON. "
            "Do not weaken the writing into generic training copy. Keep the best concrete details and realistic distractors.\n\n"
            f"Original task prompt:\n{prompt}\n\n"
            f"Writer draft:\n{draft}"
        )
        return self.normalizer._generate_json(normalize_prompt)

    def _normalize_question_with_ollama(self, prompt: str, original: dict[str, Any], draft: dict[str, Any]) -> dict[str, Any]:
        rewrite_prompt = (
            "Return strict JSON only. Rewrite this quiz question into a materially better version. "
            "The current draft is still too close to the weak original or still fails the expected quality bar. "
            "Keep the topic and language, but write a stronger scenario, more plausible distractors, and more native wording.\n\n"
            f"Original task prompt:\n{prompt}\n\n"
            f"Weak original:\n{json.dumps(original, ensure_ascii=False)}\n\n"
            f"Rejected draft:\n{json.dumps(draft, ensure_ascii=False)}"
        )
        return self.normalizer._generate_json(rewrite_prompt)

    def _normalize_lesson_with_ollama(self, prompt: str, original: dict[str, Any], draft: dict[str, Any]) -> dict[str, Any]:
        rewrite_prompt = (
            "Return strict JSON only. Rewrite this lesson into a materially better version. "
            "The current draft stayed too close to the weak original or did not improve structure enough. "
            "Keep the topic and language, but improve clarity, narrative flow, and usefulness. "
            "Output exactly one object with only these keys: title, content, emailSubject, emailBody. "
            "Never output article/webpage metadata, schema.org keys, author, image, description, text, date, publisher, or url.\n\n"
            f"Original task prompt:\n{prompt}\n\n"
            f"Weak original:\n{json.dumps(original, ensure_ascii=False)}\n\n"
            f"Rejected draft:\n{json.dumps(draft, ensure_ascii=False)}"
        )
        return self.normalizer._generate_json(rewrite_prompt)

    def _question_needs_retry(self, original: dict[str, Any], rewritten: dict[str, Any]) -> bool:
        original_question = str(original.get("question") or "").strip()
        rewritten_question = str(rewritten.get("question") or "").strip()
        original_options = [str(item).strip() for item in (original.get("options") or [])]
        rewritten_options = [str(item).strip() for item in (rewritten.get("options") or [])]
        if not rewritten_question:
            return True
        if rewritten_question == original_question and rewritten_options == original_options:
            return True
        if str(rewritten.get("questionType") or "").strip().lower() == "recall":
            return True
        validation = validate_question(rewritten)
        return not validation.is_valid

    def _lesson_needs_retry(self, original: dict[str, Any], rewritten: dict[str, Any]) -> bool:
        before = {
            "title": str(original.get("title") or "").strip(),
            "content": str(original.get("content") or "").strip(),
            "emailSubject": str(original.get("emailSubject") or "").strip(),
            "emailBody": str(original.get("emailBody") or "").strip(),
        }
        after = {
            "title": str(rewritten.get("title") or "").strip(),
            "content": str(rewritten.get("content") or "").strip(),
            "emailSubject": str(rewritten.get("emailSubject") or "").strip(),
            "emailBody": str(rewritten.get("emailBody") or "").strip(),
        }
        if before == after:
            return True
        if _foreign_lesson_shape(rewritten):
            return True
        validation = audit_lesson(after)
        return not validation.is_valid


class OpenAIProvider(BaseProvider):
    name = "openai"

    def __init__(self, api_key_env: str, model: str) -> None:
        self.api_key_env = api_key_env
        self.api_key = os.environ.get(api_key_env, "").strip()
        self.model = model

    def health(self) -> RuntimeHealth:
        if self.api_key:
            return RuntimeHealth(self.name, "HEALTHY", f"API key present in {self.api_key_env}.", True, configured_model=self.model, resolved_model=self.model)
        return RuntimeHealth(self.name, "UNAVAILABLE", f"Environment variable {self.api_key_env} is missing.", False, configured_model=self.model)

    def rewrite_question(self, course: dict[str, Any], lesson: dict[str, Any], question: dict[str, Any], validation_errors: list[str]) -> dict[str, Any]:
        prompt = _question_prompt(course, lesson, question, validation_errors)
        return self._request_json(prompt)

    def rewrite_lesson(self, course: dict[str, Any], lesson: dict[str, Any], validation_errors: list[str]) -> dict[str, Any]:
        prompt = _lesson_prompt(course, lesson, validation_errors)
        return self._request_json(prompt)

    def _request_json(self, prompt: str) -> dict[str, Any]:
        health = self.health()
        if not health.available:
            raise RuntimeError(health.detail)
        payload = {
            "model": self.model,
            "input": [{"role": "user", "content": [{"type": "input_text", "text": prompt}]}],
        }
        req = urllib.request.Request(
            url="https://api.openai.com/v1/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI request failed: {details}") from exc
        chunks: list[str] = []
        for item in body.get("output") or []:
            if item.get("type") != "message":
                continue
            for content in item.get("content") or []:
                if isinstance(content.get("text"), str):
                    chunks.append(content["text"])
        if not chunks:
            raise RuntimeError("OpenAI returned no text.")
        return json.loads("\n".join(chunks).strip())


class NullProvider(BaseProvider):
    name = "none"

    def health(self) -> RuntimeHealth:
        return RuntimeHealth(self.name, "STANDBY", "Fallback placeholder. Used only when no active rewrite provider is available.", False)

    def rewrite_question(self, course: dict[str, Any], lesson: dict[str, Any], question: dict[str, Any], validation_errors: list[str]) -> dict[str, Any]:
        raise RuntimeError("No rewrite provider is available.")

    def rewrite_lesson(self, course: dict[str, Any], lesson: dict[str, Any], validation_errors: list[str]) -> dict[str, Any]:
        raise RuntimeError("No rewrite provider is available.")


class LocalRuntimeManager:
    def __init__(self, config: dict[str, Any]) -> None:
        self.provider_order = list(config.get("provider_order") or ["ollama", "mlx", "openai", "none"])
        self.providers: dict[str, BaseProvider] = {
            "ollama": OllamaProvider(
                endpoint=str(config.get("ollama", {}).get("endpoint") or "http://127.0.0.1:11434"),
                model=str(config.get("ollama", {}).get("model") or "llama3.2:3b"),
                temperature=float(config.get("ollama", {}).get("temperature") or 0.1),
                num_predict=int(config.get("ollama", {}).get("num_predict") or 384),
                num_ctx=int(config.get("ollama", {}).get("num_ctx") or 2048),
                num_thread=int(config.get("ollama", {}).get("num_thread") or 2),
            ),
            "mlx": MLXProvider(
                model=str(
                    config.get("mlx", {}).get("model")
                    or "/Users/moldovancsaba/.cache/huggingface/hub/models--mlx-community--Apertus-8B-Instruct-2509-4bit/snapshots/c5e6ae2e52c4149f36cb8e47b7ab1489ef885fed"
                ),
                timeout=int(config.get("mlx", {}).get("timeout") or 180),
                max_tokens=int(config.get("mlx", {}).get("max_tokens") or 768),
                normalizer_endpoint=str(config.get("mlx", {}).get("normalizer_endpoint") or "http://127.0.0.1:11434"),
                normalizer_model=str(config.get("mlx", {}).get("normalizer_model") or str(config.get("ollama", {}).get("model") or "llama3.2:3b")),
            ),
            "openai": OpenAIProvider(
                api_key_env=str(config.get("openai", {}).get("api_key_env") or "OPENAI_API_KEY"),
                model=str(config.get("openai", {}).get("model") or "gpt-5.2"),
            ),
            "none": NullProvider(),
        }

    def health_snapshot(self) -> dict[str, Any]:
        healths = [
            self.providers[name].health().to_dict()
            for name in self.provider_order
            if name in self.providers and name != "none"
        ]
        selected = self.selected_provider().health().to_dict()
        return {"selected": selected, "providers": healths}

    def provider(self, name: str) -> BaseProvider | None:
        return self.providers.get(name)

    def selected_provider(self) -> BaseProvider:
        for name in self.provider_order:
            provider = self.providers.get(name)
            if not provider:
                continue
            if provider.health().available:
                return provider
        return self.providers["none"]
