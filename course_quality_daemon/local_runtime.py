from __future__ import annotations

import atexit
import json
import os
import re
import socket
import shutil
import subprocess
import sys
import time
import threading
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
        "ar": "Write natural modern Arabic. Avoid literal translation patterns, stiff instructional prose, and repeated stock phrases. Prefer clear, fluent, idiomatic wording.",
        "bg": "Write natural modern Bulgarian. Avoid translated-sounding filler and rigid instructional prose. Prefer direct, idiomatic, specific wording.",
        "hu": "Write natural modern Hungarian. Avoid translated-sounding filler, corporate stiffness, and repeated stock phrases. Prefer clear, direct, idiomatic wording.",
        "en": "Write natural modern English. Avoid translationese, generic training jargon, and repetitive phrasing. Prefer concrete, fluent wording.",
        "es": "Write natural modern Spanish. Avoid literal translation patterns and stiff instructional prose. Prefer idiomatic, specific wording.",
        "hi": "Write natural modern Hindi. Avoid translationese, stiff textbook wording, and repeated filler. Prefer clear, idiomatic, specific wording.",
        "pt": "Write natural modern Portuguese. Avoid literal translation patterns and stiff instructional prose. Prefer idiomatic, specific wording.",
        "id": "Write natural modern Indonesian. Avoid translated-sounding phrasing and generic filler. Prefer direct, clear, idiomatic wording.",
        "pl": "Write natural modern Polish. Avoid translated-sounding phrasing and generic filler. Prefer direct, clear, idiomatic wording.",
        "ru": "Write natural modern Russian. Avoid translated-sounding phrasing and generic filler. Prefer direct, clear, idiomatic wording.",
        "sw": "Write natural modern Swahili. Avoid literal translation patterns and generic training filler. Prefer clear, idiomatic, specific wording.",
        "sv": "Write natural modern Swedish. Avoid translated-sounding phrasing and generic filler. Prefer direct, clear, idiomatic wording.",
        "tr": "Write natural modern Turkish. Avoid literal translation patterns, stiff instructional prose, and repeated filler. Prefer clear, idiomatic, specific wording.",
        "vi": "Write natural modern Vietnamese. Avoid translated-sounding phrasing, stiff instructional prose, and repeated filler. Prefer clear, idiomatic, specific wording.",
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
    language_code = str(course.get("language") or lesson.get("language") or "").strip().lower()
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
- Use only {language_name}. Do not mix in any other language.
- Do not use headings, stock phrases, or labels copied from another language.
- Make the question concrete, specific, and useful in real work.
- The stem must describe a realistic decision, action, or judgement moment.
- Keep it standalone: no references to "the lesson", "the course", or other meta framing.
- Do not test recall. Test application, diagnosis, prioritization, or good judgement.
- Keep 4 answer options.
- Exactly 1 clearly best answer.
- Wrong answers must be plausible mistakes a learner could realistically make.
- Avoid repeating the same key phrase from the lesson across the stem and every option.
- Avoid generic filler like "something related", "not covered here", or "as described in the lesson".
- **NEVER** include the AI's reasoning, justification, or explaining why an answer is correct within the options themselves (e.g., do not say "this is the strongest choice", "this improves quality", etc.).
- **NEVER** use the word "only" or "csak" as a lazy distractor marker.
- Keep the existing intent, topic, and language variant.

Negative constraints (STRICT):
- Do not repeat the same sentence structure for all wrong answers.
- Do not use phrases like "ez a legerősebb választás", "ez csak felszíni", "ez részleges javítás".
- Do not add "REASONING:" or "EXPLANATION:" fields to the JSON.

Length rules (STRICT):
- The question stem MUST be between 80 and 250 characters. Do NOT make it short.
- Each option MUST be between 45 and 180 characters. Explain the option clearly.
- If the generated text is too short, the task will be REJECTED. Expand your thoughts.
- Start with `{{` and end with `}}`.

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
    language_code = str(course.get("language") or lesson.get("language") or "").strip().lower()
    language_name = _language_name(language_code)
    canonical_sections = [
        "Learning goal",
        "Who",
        "What",
        "Where",
        "When",
        "Why it matters",
        "How",
        "Guided exercise",
        "Independent exercise",
        "Self-check",
        "Bibliography (sources used)",
        "Read more (optional)",
    ]
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
- Use only {language_name}. Do not mix in English or any other language.
- All headings, labels, bullets, calls to action, and email copy must stay in {language_name}.
- Keep the same topic and learning intent.
- Improve narrative flow, structure, clarity, and usefulness.
- Be specific and practical instead of generic.
- Keep Markdown lesson formatting and follow the canonical lesson grammar exactly.
- The lesson content MUST include the canonical blocks in order.
- Do not invent unsupported claims or sources.
- Expand weak lessons into a complete teaching asset, not a short summary.
- **CRITICAL**: Do NOT mix languages. If you are writing in {language_name}, every single word must be in {language_name}.
- Do NOT use technical markers or boilerplate from other languages (e.g., do not use Bulgarian markers in Russian content, do not use English headings in Hungarian content).
- Start with `{{` and end with `}}`.
- Output exactly one JSON object and nothing else.

Length rules (STRICT):
- Content MUST be between 1200 and 2500 characters.
- If the input is a placeholder or outline, you MUST expand it into a full, detailed professional lesson.
- DO NOT be brief. Be thorough, detailed, and professional.
- If the output is shorter than 1200 characters, it will be REJECTED.
- content must include these canonical blocks in order:
{chr(10).join(f"- {section}" for section in canonical_sections)}
- content must be valid Markdown using headings, lists, emphasis, and links where appropriate
- emailBody must be more informative than a one-line reminder
- emailBody should be between 120 and 500 characters
- emailBody should be Markdown, not HTML, unless preserving unavoidable legacy structure

Use this exact shape:
{{
  "title": "Localized lesson title",
  "content": "## Learning goal\\n...\\n\\n## Who\\n...\\n\\n## What\\n...\\n\\n## Where\\n...\\n\\n## When\\n...\\n\\n## Why it matters\\n...\\n\\n## How\\n...\\n\\n## Guided exercise\\n...\\n\\n## Independent exercise\\n...\\n\\n## Self-check\\n...\\n\\n## Bibliography (sources used)\\n...\\n\\n## Read more (optional)\\n...",
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

    def warm(self) -> bool:
        return self.health().available

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

    def generate_markdown(self, prompt: str, max_tokens: int | None = None) -> str:
        raise NotImplementedError


class OllamaProvider(BaseProvider):
    name = "ollama"

    def __init__(
        self,
        endpoint: str,
        model: str,
        fallback_models: list[str] | None = None,
        timeout: int = 180,
        temperature: float = 0.1,
        num_predict: int = 384,
        lesson_num_predict: int | None = None,
        question_num_predict: int | None = None,
        num_ctx: int = 2048,
        num_thread: int = 2,
        keep_alive: str = "24h",
    ) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.model = model
        self.fallback_models = [str(item).strip() for item in (fallback_models or []) if str(item).strip()]
        self.timeout = timeout
        self.temperature = temperature
        self.num_predict = num_predict
        self.lesson_num_predict = int(lesson_num_predict or num_predict)
        self.question_num_predict = int(question_num_predict or num_predict)
        self.num_ctx = num_ctx
        self.num_thread = num_thread
        self.keep_alive = str(keep_alive or "24h").strip() or "24h"

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

    def warm(self) -> bool:
        try:
            health = self.health()
            if not health.available or not health.resolved_model:
                return False
            payload = {
                "model": str(health.resolved_model),
                "messages": [
                    {
                        "role": "user",
                        "content": "Warm this model and keep it loaded. Reply with a short acknowledgement.",
                    }
                ],
                "stream": False,
                "keep_alive": self.keep_alive,
                "options": {
                    "temperature": 0,
                    "num_predict": 8,
                    "num_ctx": self.num_ctx,
                    "num_thread": self.num_thread,
                },
            }
            body = self._request_json("/api/chat", payload)
            return bool(body)
        except Exception:
            return False

    def rewrite_question(self, course: dict[str, Any], lesson: dict[str, Any], question: dict[str, Any], validation_errors: list[str]) -> dict[str, Any]:
        prompt = self._question_prompt(course, lesson, question, validation_errors)
        candidate = self._generate_json(prompt, num_predict_override=self.question_num_predict)
        if self._question_needs_repair(candidate):
            repair_prompt = (
                "Return strict JSON only. Repair this quiz question object so it fully matches the required schema. "
                "The current draft has broken structure or failed validation. "
                "Keep the language, topic, and strongest wording, but fix missing keys, malformed arrays, and weak distractors.\n\n"
                f"Original rewrite brief:\n{prompt}\n\n"
                f"Broken draft:\n{json.dumps(candidate, ensure_ascii=False)}"
            )
            candidate = self._generate_json(repair_prompt, num_predict_override=max(self.question_num_predict, 768))
        return candidate

    def rewrite_lesson(self, course: dict[str, Any], lesson: dict[str, Any], validation_errors: list[str]) -> dict[str, Any]:
        prompt = self._lesson_prompt(course, lesson, validation_errors)
        return self._generate_json(prompt, num_predict_override=self.lesson_num_predict)

    def rewrite_question_timeout_fallback(self, course: dict[str, Any], lesson: dict[str, Any], question: dict[str, Any], validation_errors: list[str]) -> dict[str, Any]:
        prompt = self._question_prompt(course, lesson, question, validation_errors)
        return self._generate_json(prompt, num_predict_override=self.question_num_predict, models=self.fallback_models)

    def rewrite_lesson_timeout_fallback(self, course: dict[str, Any], lesson: dict[str, Any], validation_errors: list[str]) -> dict[str, Any]:
        prompt = self._lesson_prompt(course, lesson, validation_errors)
        return self._generate_json(prompt, num_predict_override=self.lesson_num_predict, models=self.fallback_models)

    def generate_markdown(self, prompt: str, max_tokens: int | None = None) -> str:
        last_error: Exception | None = None
        for model_name in self._candidate_models():
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": int(max_tokens or max(self.num_predict, 1200)),
                    "num_ctx": self.num_ctx,
                    "num_thread": self.num_thread,
                },
                "keep_alive": self.keep_alive,
            }
            try:
                body = self._request_json("/api/generate", payload)
                text = str(body.get("response") or "").strip()
                if not text:
                    raise RuntimeError(f"Ollama model {model_name} returned empty markdown response.")
                return text
            except RuntimeError as exc:
                last_error = exc
                if "timed out" not in str(exc).lower():
                    raise
        raise RuntimeError(str(last_error) if last_error else "Ollama markdown generation failed.")

    def _generate_json(
        self,
        prompt: str,
        num_predict_override: int | None = None,
        models: list[str] | None = None,
    ) -> dict[str, Any]:
        health = self.health()
        if not health.available or not health.resolved_model:
            raise RuntimeError(f"Ollama not available: {health.detail}")
        num_predict = int(num_predict_override or self.num_predict)
        last_error: Exception | None = None
        candidate_models = [str(item).strip() for item in (models or self._candidate_models()) if str(item).strip()]
        if not candidate_models:
            raise RuntimeError("No Ollama candidate models are configured.")
        for model_name in candidate_models:
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": self.temperature,
                    "num_predict": num_predict,
                    "num_ctx": self.num_ctx,
                    "num_thread": self.num_thread,
                },
                "keep_alive": self.keep_alive,
            }
            try:
                body = self._request_json("/api/generate", payload)
                text = str(body.get("response") or "").strip()
                if not text:
                    raise RuntimeError(f"Ollama model {model_name} returned empty response.")
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
                            "model": model_name,
                            "prompt": repair_prompt,
                            "stream": False,
                            "format": "json",
                        "options": {
                            "temperature": 0,
                            "num_predict": max(num_predict, 768),
                            "num_ctx": self.num_ctx,
                            "num_thread": self.num_thread,
                        },
                        "keep_alive": self.keep_alive,
                    },
                    )
                    repaired = str(repair_body.get("response") or "").strip()
                    if not repaired:
                        raise RuntimeError(f"Ollama model {model_name} JSON repair returned empty response.")
                    try:
                        return json.loads(repaired)
                    except json.JSONDecodeError:
                        return json.loads(self._extract_json(repaired))
            except RuntimeError as exc:
                last_error = exc
                if "timed out" in str(exc).lower():
                    # Stop immediately on timeout to prevent watchdog collision
                    raise
                # For other errors (unavailable, model load failing), we might try next model
                continue
        raise RuntimeError(str(last_error) if last_error else "Ollama JSON generation failed.")

    def _candidate_models(self) -> list[str]:
        health = self.health()
        if not health.available or not health.resolved_model:
            raise RuntimeError(f"Ollama not available: {health.detail}")
        models = [str(health.resolved_model).strip()]
        for model_name in self.fallback_models:
            if model_name not in models:
                models.append(model_name)
        return models

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
        except (TimeoutError, socket.timeout) as exc:
            raise RuntimeError(f"Ollama request timed out after {self.timeout} seconds.") from exc
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
        temperature: float = 0.1,
        lesson_max_tokens: int | None = None,
        question_max_tokens: int | None = None,
        normalizer_endpoint: str = "http://127.0.0.1:11434",
        normalizer_model: str = "llama3.2:3b",
        python_bin: str | None = None,
        health_timeout: int = 15,
        cooldown_seconds: int = 600,
        max_consecutive_failures: int = 2,
        resident_server: bool = False,
        server_host: str = "127.0.0.1",
        server_port: int = 0,
        server_startup_timeout: int = 180,
    ) -> None:
        self.model = model
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.temperature = float(temperature)
        self.lesson_max_tokens = int(lesson_max_tokens or max_tokens)
        self.question_max_tokens = int(question_max_tokens or max_tokens)
        self.python_bin = self._resolve_python_bin(python_bin)
        self.health_timeout = max(5, int(health_timeout or 15))
        self.cooldown_seconds = max(60, int(cooldown_seconds or 600))
        self.max_consecutive_failures = max(1, int(max_consecutive_failures or 2))
        self.resident_server = bool(resident_server)
        self.server_host = str(server_host or "127.0.0.1").strip() or "127.0.0.1"
        self.server_port = int(server_port or 0)
        self.server_startup_timeout = max(30, int(server_startup_timeout or 180))
        self._cooldown_until = 0.0
        self._consecutive_failures = 0
        self._last_failure_detail = ""
        self._health_cache: RuntimeHealth | None = None
        self._health_cache_at = 0.0
        self._health_cache_ttl = 60.0
        self._resident_server_proc: subprocess.Popen[str] | None = None
        self._resident_server_lock = threading.RLock()
        self._resident_server_ready_at = 0.0
        self.normalizer = OllamaProvider(normalizer_endpoint, normalizer_model)
        atexit.register(self.close)

    def close(self) -> None:
        with self._resident_server_lock:
            proc = self._resident_server_proc
            self._resident_server_proc = None
            if proc is None:
                return
            if proc.poll() is None:
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                except Exception:
                    try:
                        proc.kill()
                    except Exception:
                        pass

    def warm(self) -> bool:
        if not self.resident_server:
            return self.health().available
        self._ensure_resident_server(warm=True)
        return self.health().available

    def _resolved_model_path(self) -> str:
        candidate = os.path.expanduser(self.model)
        if os.path.isdir(candidate):
            return candidate
        return self.model

    def _server_base_url(self) -> str:
        if not self.server_port:
            raise RuntimeError("MLX resident server port is not configured.")
        return f"http://{self.server_host}:{self.server_port}"

    def _server_command(self) -> list[str]:
        return [
            self.python_bin,
            "-m",
            "mlx_lm",
            "server",
            "--model",
            self._resolved_model_path(),
            "--host",
            self.server_host,
            "--port",
            str(self.server_port),
            "--log-level",
            "ERROR",
        ]

    def _server_process_alive(self) -> bool:
        proc = self._resident_server_proc
        return bool(proc and proc.poll() is None)

    def _server_ready(self) -> bool:
        if not self._server_process_alive():
            return False
        if not self.server_port:
            return False
        try:
            body = self._server_request_json("/v1/models", timeout=min(10, self.health_timeout))
            models = body.get("data") or body.get("models") or []
            if isinstance(models, list):
                resolved = self._resolved_model_path()
                for item in models:
                    name = str((item or {}).get("id") or (item or {}).get("name") or "").strip()
                    if not name:
                        continue
                    if name == resolved or name == self.model or os.path.basename(name) == os.path.basename(resolved):
                        return True
                return bool(models)
            return True
        except Exception:
            return False

    def _ensure_resident_server(self, warm: bool = False) -> None:
        if not self.resident_server:
            return
        with self._resident_server_lock:
            if self._server_ready():
                self._resident_server_ready_at = time.time()
                return
            proc = self._resident_server_proc
            if proc is None or proc.poll() is not None:
                if not self.server_port:
                    raise RuntimeError("MLX resident server port is not configured.")
                command = self._server_command()
                env = os.environ.copy()
                env.setdefault("PYTHONUNBUFFERED", "1")
                env.setdefault("TOKENIZERS_PARALLELISM", "false")
                try:
                    proc = subprocess.Popen(
                        command,
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        env=env,
                    )
                except Exception as exc:
                    raise RuntimeError(f"Failed to start MLX resident server on port {self.server_port}: {exc}") from exc
                self._resident_server_proc = proc
            deadline = time.time() + (self.server_startup_timeout if warm else self.health_timeout)
            last_error: Exception | None = None
            while time.time() < deadline:
                if self._server_ready():
                    self._resident_server_ready_at = time.time()
                    self._record_success()
                    return
                if proc.poll() is not None:
                    last_error = RuntimeError(f"MLX resident server exited with code {proc.returncode}.")
                    break
                time.sleep(1.0)
            detail = f"MLX resident server failed to become ready on port {self.server_port}."
            if last_error is not None:
                detail = f"{detail} {last_error}"
            self._record_failure(detail)
            raise RuntimeError(detail)

    def _server_request_json(self, path: str, payload: dict[str, Any] | None = None, timeout: int | None = None) -> dict[str, Any]:
        data = None
        headers = {"Accept": "application/json"}
        method = "GET"
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
            method = "POST"
        req = urllib.request.Request(f"{self._server_base_url()}{path}", data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout or self.health_timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (TimeoutError, socket.timeout) as exc:
            raise RuntimeError(f"MLX resident server request timed out after {timeout or self.health_timeout} seconds.") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"MLX resident server request failed: {exc}") from exc

    def _server_generate_text(self, prompt: str, max_tokens_override: int | None = None) -> str:
        self._ensure_resident_server(warm=True)
        payload = {
            "model": self._resolved_model_path(),
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "temperature": self.temperature,
            "max_tokens": int(max_tokens_override or self.max_tokens),
        }
        body = self._server_request_json("/v1/chat/completions", payload=payload, timeout=self.timeout)
        choices = body.get("choices") or []
        if not isinstance(choices, list) or not choices:
            raise RuntimeError("MLX resident server returned no choices.")
        first = choices[0] or {}
        message = first.get("message") or {}
        text = str(message.get("content") or "").strip()
        if not text:
            raise RuntimeError("MLX resident server returned empty response.")
        return text

    def _resolve_python_bin(self, configured: str | None) -> str:
        candidates = [
            str(configured or "").strip(),
            os.environ.get("AMANOBA_PYTHON_BIN", "").strip(),
            os.path.join(os.getcwd(), ".venv-mlx", "bin", "python"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), ".venv-mlx", "bin", "python"),
            sys.executable,
        ]
        for candidate in candidates:
            if candidate and os.path.exists(candidate):
                return candidate
        return sys.executable

    def _cooldown_active(self) -> bool:
        return self._cooldown_until > time.time()

    def _cooldown_detail(self) -> str:
        remaining = max(0, int(self._cooldown_until - time.time()))
        base = self._last_failure_detail or "MLX is temporarily cooling down after repeated runtime failures."
        if remaining:
            return f"{base} Retrying MLX in about {remaining} seconds."
        return base

    def _record_success(self) -> None:
        self._consecutive_failures = 0
        self._cooldown_until = 0.0
        self._last_failure_detail = ""

    def _record_failure(self, detail: str) -> None:
        self._consecutive_failures += 1
        self._last_failure_detail = detail
        if self._consecutive_failures >= self.max_consecutive_failures:
            self._cooldown_until = time.time() + self.cooldown_seconds

    def _classify_failure(self, detail: str) -> str:
        lowered = str(detail or "").lower()
        if "gpu timeout" in lowered or "command buffer execution failed" in lowered or "[metal]" in lowered:
            return "MLX Metal runtime hit a GPU timeout."
        if "no module named 'mlx_lm'" in lowered or 'no module named "mlx_lm"' in lowered:
            return "MLX runtime is not installed in the configured interpreter."
        if "timed out after" in lowered:
            return str(detail).strip()
        return str(detail).strip() or "MLX generation failed."

    def health(self) -> RuntimeHealth:
        model_path = self._resolved_model_path()
        now = time.time()
        if self._health_cache is not None and (now - self._health_cache_at) < self._health_cache_ttl:
            cached = self._health_cache
            if cached.available and self._cooldown_active():
                return RuntimeHealth(self.name, "DEGRADED", self._cooldown_detail(), False, configured_model=self.model, resolved_model=model_path)
            return RuntimeHealth(
                cached.provider,
                cached.status,
                cached.detail,
                cached.available,
                configured_model=cached.configured_model,
                resolved_model=model_path,
                endpoint=cached.endpoint,
            )
        if self.resident_server:
            try:
                self._ensure_resident_server(warm=False)
            except Exception as exc:
                detail = self._classify_failure(str(exc))
                health = RuntimeHealth(self.name, "UNAVAILABLE", detail, False, configured_model=self.model, resolved_model=model_path)
                self._health_cache = health
                self._health_cache_at = now
                return health
            if not os.path.isdir(model_path):
                health = RuntimeHealth(self.name, "UNAVAILABLE", f"MLX model path not found: {model_path}", False, configured_model=self.model)
                self._health_cache = health
                self._health_cache_at = now
                return health
            health = RuntimeHealth(
                self.name,
                "HEALTHY",
                f"MLX resident server is running on {self.server_host}:{self.server_port}.",
                True,
                configured_model=self.model,
                resolved_model=model_path,
                endpoint=f"http://{self.server_host}:{self.server_port}",
            )
            self._record_success()
            self._health_cache = health
            self._health_cache_at = now
            return health
        if self._cooldown_active():
            health = RuntimeHealth(self.name, "DEGRADED", self._cooldown_detail(), False, configured_model=self.model, resolved_model=model_path)
            self._health_cache = health
            self._health_cache_at = now
            return health
        try:
            completed = subprocess.run(
                [self.python_bin, "-c", "import mlx_lm"],
                text=True,
                capture_output=True,
                timeout=self.health_timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            detail = f"MLX runtime health probe timed out after {self.health_timeout} seconds."
            self._record_failure(detail)
            health = RuntimeHealth(self.name, "UNAVAILABLE", detail, False, configured_model=self.model, resolved_model=model_path)
            self._health_cache = health
            self._health_cache_at = now
            return health
        except Exception as exc:
            detail = self._classify_failure(f"MLX runtime health probe failed: {exc}")
            self._record_failure(detail)
            health = RuntimeHealth(self.name, "UNAVAILABLE", detail, False, configured_model=self.model, resolved_model=model_path)
            self._health_cache = health
            self._health_cache_at = now
            return health
        if completed.returncode != 0:
            detail = self._classify_failure(completed.stderr or completed.stdout or f"MLX health probe exited with code {completed.returncode}.")
            self._record_failure(detail)
            health = RuntimeHealth(self.name, "UNAVAILABLE", detail, False, configured_model=self.model, resolved_model=model_path)
            self._health_cache = health
            self._health_cache_at = now
            return health
        if os.path.isdir(model_path):
            health = RuntimeHealth(
                self.name,
                "HEALTHY",
                f"MLX runtime available in {self.python_bin} and local model path found.",
                True,
                configured_model=self.model,
                resolved_model=model_path,
            )
            self._record_success()
            self._health_cache = health
            self._health_cache_at = now
            return health
        health = RuntimeHealth(self.name, "UNAVAILABLE", f"MLX model path not found: {model_path}", False, configured_model=self.model)
        self._health_cache = health
        self._health_cache_at = now
        return health

    def rewrite_question(self, course: dict[str, Any], lesson: dict[str, Any], question: dict[str, Any], validation_errors: list[str]) -> dict[str, Any]:
        prompt = _question_prompt(course, lesson, question, validation_errors)
        candidate = self._generate_json(prompt, max_tokens_override=self.question_max_tokens)
        if self._question_needs_retry(question, candidate):
            retry_prompt = (
                f"{prompt}\n\n"
                "Your previous draft stayed too close to the weak original or kept invalid structure. "
                "Rewrite it again from scratch. Make it more concrete, more native-sounding, and more scenario-based. "
                "Do not keep the original wording if it was weak."
            )
            candidate = self._generate_json(retry_prompt, max_tokens_override=self.question_max_tokens)
        if self._question_needs_retry(question, candidate):
            return self._normalize_question_with_ollama(prompt, question, candidate)
        return candidate

    def rewrite_lesson(self, course: dict[str, Any], lesson: dict[str, Any], validation_errors: list[str]) -> dict[str, Any]:
        prompt = _lesson_prompt(course, lesson, validation_errors)
        return self._generate_json(prompt, max_tokens_override=self.lesson_max_tokens)

    def generate_markdown(self, prompt: str, max_tokens: int | None = None) -> str:
        health = self.health()
        if not health.available:
            raise RuntimeError(f"MLX not available: {health.detail}")
        if self.resident_server:
            return self._server_generate_text(prompt, max_tokens_override=max_tokens or max(self.max_tokens, 1400))
        return self._generate_text(prompt, max_tokens or max(self.max_tokens, 1400))

    def _generate_json(self, prompt: str, max_tokens_override: int | None = None) -> dict[str, Any]:
        health = self.health()
        if not health.available:
            raise RuntimeError(f"MLX not available: {health.detail}")
        text = self._server_generate_text(prompt, max_tokens_override) if self.resident_server else self._generate_text(prompt, max_tokens_override)
        try:
            cleaned = self._extract_json(text)
            return json.loads(cleaned)
        except Exception:
            # Initial generation was successful but returned malformed JSON
            pass

        repair_prompt = (
            "Convert the following draft into strict JSON only. "
            "Do not explain. Do not add markdown. Start with {{ and end with }}.\n\n"
            f"Original task prompt:\n{prompt}\n\n"
            f"Draft to convert:\n{text}"
        )
        try:
            repaired = self._generate_text(repair_prompt, max_tokens_override)
        except RuntimeError as exc:
            if "timed out" in str(exc).lower():
                raise
            # If repair itself fails (crash, etc.), we give up on MLX
            raise

        try:
            cleaned = self._extract_json(repaired)
            return json.loads(cleaned)
        except Exception:
            return self._normalize_with_ollama(prompt, repaired, max_tokens_override)

    def _generate_text(self, prompt: str, max_tokens_override: int | None = None) -> str:
        max_tokens = int(max_tokens_override or self.max_tokens)

        # Fallback: Isolated Subprocess Worker
        command = [
            self.python_bin,
            "-m",
            "course_quality_daemon.mlx_worker",
            "--model",
            self._resolved_model_path(),
            "--max-tokens",
            str(max_tokens),
        ]
        env = os.environ.copy()
        env.setdefault("PYTHONUNBUFFERED", "1")
        try:
            completed = subprocess.run(
                command,
                input=prompt,
                text=True,
                capture_output=True,
                timeout=self.timeout if self.timeout > 0 else None,
                check=False,
                env=env,
            )
        except subprocess.TimeoutExpired as exc:
            detail = f"MLX generation timed out after {self.timeout} seconds."
            self._record_failure(detail)
            raise RuntimeError(detail) from exc
        if completed.returncode != 0:
            detail = self._classify_failure(completed.stderr or completed.stdout or f"exit code {completed.returncode}")
            self._record_failure(detail)
            raise RuntimeError(detail)
        text = str(completed.stdout or "").strip()
        if not text:
            detail = "MLX generation failed: empty response."
            self._record_failure(detail)
            raise RuntimeError(detail)
        self._record_success()
        return text

    def _extract_json(self, text: str) -> str:
        text = text.strip()
        if text.startswith("{") and text.endswith("}"):
            return text
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if match:
            return match.group(0)
        raise RuntimeError(f"MLX did not return JSON: {text[:400]}")

    def _normalize_with_ollama(self, prompt: str, draft: str, max_tokens_override: int | None = None) -> dict[str, Any]:
        normalize_prompt = (
            "Return strict JSON only. Preserve the writer's meaning, language, and tone while converting it into valid JSON. "
            "Do not weaken the writing into generic training copy. Keep the best concrete details and realistic distractors.\n\n"
            f"Original task prompt:\n{prompt}\n\n"
            f"Writer draft:\n{draft}"
        )
        return self.normalizer._generate_json(normalize_prompt, num_predict_override=max(int(max_tokens_override or self.max_tokens), 768))

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

    def generate_markdown(self, prompt: str, max_tokens: int | None = None) -> str:
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
        text = "\n".join(chunks).strip()
        if not text:
            raise RuntimeError("OpenAI returned no markdown text.")
        return text

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

    def generate_markdown(self, prompt: str, max_tokens: int | None = None) -> str:
        raise RuntimeError("No rewrite provider is available.")


class LocalRuntimeManager:
    def __init__(self, config: dict[str, Any]) -> None:
        self.provider_order = list(config.get("provider_order") or ["ollama", "mlx", "openai", "none"])
        self.writer_provider_order = list(config.get("writer_provider_order") or ["mlx", "ollama", "none"])
        self.creator_pipeline = dict(config.get("creator_pipeline") or {})
        self.providers: dict[str, BaseProvider] = {
            "ollama": OllamaProvider(
                endpoint=str(config.get("ollama", {}).get("endpoint") or "http://127.0.0.1:11434"),
                model=str(config.get("ollama", {}).get("model") or "llama3.2:3b"),
                fallback_models=list(config.get("ollama", {}).get("fallback_models") or []),
                timeout=int(config.get("ollama", {}).get("timeout") or 60),
                temperature=float(config.get("ollama", {}).get("temperature") or 0.1),
                num_predict=int(config.get("ollama", {}).get("num_predict") or 384),
                lesson_num_predict=int(config.get("ollama", {}).get("lesson_num_predict") or config.get("ollama", {}).get("num_predict") or 384),
                question_num_predict=int(config.get("ollama", {}).get("question_num_predict") or config.get("ollama", {}).get("num_predict") or 384),
                num_ctx=int(config.get("ollama", {}).get("num_ctx") or 2048),
                num_thread=int(config.get("ollama", {}).get("num_thread") or 2),
                keep_alive=str(config.get("ollama", {}).get("keep_alive") or "24h"),
            ),
            "mlx": MLXProvider(
                model=str(
                    config.get("mlx", {}).get("model")
                    or "/Users/moldovancsaba/.cache/huggingface/hub/models--mlx-community--Apertus-8B-Instruct-2509-4bit/snapshots/c5e6ae2e52c4149f36cb8e47b7ab1489ef885fed"
                ),
                timeout=int(config.get("mlx", {}).get("timeout") or 180),
                max_tokens=int(config.get("mlx", {}).get("max_tokens") or 768),
                temperature=float(config.get("mlx", {}).get("temperature") or 0.1),
                lesson_max_tokens=int(config.get("mlx", {}).get("lesson_max_tokens") or config.get("mlx", {}).get("max_tokens") or 768),
                question_max_tokens=int(config.get("mlx", {}).get("question_max_tokens") or config.get("mlx", {}).get("max_tokens") or 768),
                normalizer_endpoint=str(config.get("mlx", {}).get("normalizer_endpoint") or "http://127.0.0.1:11434"),
                normalizer_model=str(config.get("mlx", {}).get("normalizer_model") or str(config.get("ollama", {}).get("model") or "llama3.2:3b")),
                python_bin=str(config.get("mlx", {}).get("python_bin") or ""),
                health_timeout=int(config.get("mlx", {}).get("health_timeout") or 15),
                cooldown_seconds=int(config.get("mlx", {}).get("cooldown_seconds") or 600),
                max_consecutive_failures=int(config.get("mlx", {}).get("max_consecutive_failures") or 2),
            ),
            "openai": OpenAIProvider(
                api_key_env=str(config.get("openai", {}).get("api_key_env") or "OPENAI_API_KEY"),
                model=str(config.get("openai", {}).get("model") or "gpt-5.2"),
            ),
            "none": NullProvider(),
        }
        self.creator_role_providers: dict[str, BaseProvider] = {}
        self._init_creator_role_providers()
        self.warm_creator_roles()

    def _specialist_role_available(self, role: str) -> bool:
        provider = self.creator_provider(role)
        return provider is not None and provider.name != "none" and provider.health().available

    def specialist_qc_available(self) -> bool:
        return all(self._specialist_role_available(role) for role in ("drafter", "writer", "judge"))

    def _json_from_markdown_provider(self, provider: BaseProvider, prompt: str, *, max_tokens: int) -> dict[str, Any]:
        text = provider.generate_markdown(prompt, max_tokens=max_tokens)
        cleaned = text.strip()
        if cleaned.startswith("{") and cleaned.endswith("}"):
            return json.loads(cleaned)
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise RuntimeError(f"{provider.name} did not return JSON: {cleaned[:400]}")

    def _clamp_score(self, value: Any, default: float = 0.5) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            numeric = float(default)
        return max(0.0, min(1.0, numeric))

    def specialist_rewrite_question(
        self,
        course: dict[str, Any],
        lesson: dict[str, Any],
        question: dict[str, Any],
        validation_errors: list[str],
        human_feedback: list[str] | None = None,
    ) -> dict[str, Any]:
        if not self.specialist_qc_available():
            raise RuntimeError("Specialist QC pipeline is not available.")
        feedback_rows = [str(item).strip() for item in (human_feedback or []) if str(item).strip()]
        drafter = self.creator_provider("drafter")
        writer = self.creator_provider("writer")
        judge = self.creator_provider("judge")
        timings: list[dict[str, Any]] = []

        drafter_prompt = f"""
You are the Drafter in Amanoba QC.
Break this quiz question into atomic rewrite guidance.
Return strict JSON only:
{{
  "rewriteBrief": "one paragraph",
  "atomicFocuses": ["...", "..."],
  "risks": ["...", "..."],
  "d_conf": 0.0,
  "d_impact": 0.0
}}

Target language only: {_language_name(course.get("language") or lesson.get("language"))}
Current question:
{json.dumps(question, ensure_ascii=False)}
Validation errors:
{json.dumps(validation_errors, ensure_ascii=False)}
Human feedback:
{json.dumps(feedback_rows, ensure_ascii=False)}
""".strip()
        started = time.perf_counter()
        draft_breakdown = self._json_from_markdown_provider(drafter, drafter_prompt, max_tokens=600)
        timings.append({"provider": f"{drafter.name}:drafter", "status": "success", "durationMs": int((time.perf_counter() - started) * 1000)})

        writer_prompt = f"""
You are the Writer in Amanoba QC.
Write one final improved quiz question.
Return strict JSON only:
{{
  "question": "...",
  "options": ["...", "...", "...", "..."],
  "correctIndex": 0,
  "questionType": "...",
  "difficulty": "...",
  "category": "...",
  "hashtags": ["..."],
  "w_conf": 0.0,
  "w_impact": 0.0
}}

Rules:
- Use only {_language_name(course.get("language") or lesson.get("language"))}
- No mixed language
- Application-first, never recall-first
- Strong realistic distractors

Question:
{json.dumps(question, ensure_ascii=False)}
Rewrite brief:
{json.dumps(draft_breakdown, ensure_ascii=False)}
""".strip()
        started = time.perf_counter()
        writer_result = self._json_from_markdown_provider(writer, writer_prompt, max_tokens=900)
        timings.append({"provider": f"{writer.name}:writer", "status": "success", "durationMs": int((time.perf_counter() - started) * 1000)})

        candidate = {
            "question": writer_result.get("question"),
            "options": writer_result.get("options"),
            "correctIndex": writer_result.get("correctIndex"),
            "questionType": writer_result.get("questionType"),
            "difficulty": writer_result.get("difficulty"),
            "category": writer_result.get("category"),
            "hashtags": writer_result.get("hashtags"),
        }

        judge_prompt = f"""
You are the Judge in Amanoba QC.
Return strict JSON only:
{{
  "accept": true,
  "reason": "...",
  "revisionNote": "...",
  "j_conf": 0.0,
  "j_impact": 0.0
}}

Accept only if:
- target language is pure
- question is structurally valid
- scenario is concrete
- distractors are plausible
- output is clearly better than original

Original:
{json.dumps(question, ensure_ascii=False)}
Candidate:
{json.dumps(candidate, ensure_ascii=False)}
Validation errors to fix:
{json.dumps(validation_errors, ensure_ascii=False)}
""".strip()
        started = time.perf_counter()
        judge_result = self._json_from_markdown_provider(judge, judge_prompt, max_tokens=400)
        timings.append({"provider": f"{judge.name}:judge", "status": "success", "durationMs": int((time.perf_counter() - started) * 1000)})

        d_conf = self._clamp_score(draft_breakdown.get("d_conf"), 0.65)
        d_impact = self._clamp_score(draft_breakdown.get("d_impact"), 0.65)
        w_conf = self._clamp_score(writer_result.get("w_conf"), 0.7)
        w_impact = self._clamp_score(writer_result.get("w_impact"), 0.7)
        j_conf = self._clamp_score(judge_result.get("j_conf"), 0.75)
        j_impact = self._clamp_score(judge_result.get("j_impact"), 0.75)
        trust_score = round(d_conf * w_conf * j_conf, 4)
        impact_score = round(d_impact * w_impact * j_impact, 4)
        validation = validate_question(candidate, str(course.get("language") or lesson.get("language") or ""))
        accepted = bool(judge_result.get("accept")) and validation.is_valid and trust_score >= 0.35
        return {
            "provider": "specialist-pipeline",
            "payload": candidate,
            "validation": validation,
            "accepted": accepted,
            "trustScore": trust_score,
            "impactScore": impact_score,
            "judgeReason": str(judge_result.get("reason") or ""),
            "revisionNote": str(judge_result.get("revisionNote") or ""),
            "timings": timings,
            "roles": {
                "drafter": draft_breakdown,
                "writer": writer_result,
                "judge": judge_result,
            },
        }

    def specialist_rewrite_lesson(
        self,
        course: dict[str, Any],
        lesson: dict[str, Any],
        validation_errors: list[str],
        human_feedback: list[str] | None = None,
    ) -> dict[str, Any]:
        if not self.specialist_qc_available():
            raise RuntimeError("Specialist QC pipeline is not available.")
        feedback_rows = [str(item).strip() for item in (human_feedback or []) if str(item).strip()]
        drafter = self.creator_provider("drafter")
        writer = self.creator_provider("writer")
        judge = self.creator_provider("judge")
        timings: list[dict[str, Any]] = []

        drafter_prompt = f"""
You are the Drafter in Amanoba QC.
Break this lesson into atomic rewrite guidance.
Return strict JSON only:
{{
  "rewriteBrief": "one paragraph",
  "atomicFocuses": ["...", "..."],
  "risks": ["...", "..."],
  "d_conf": 0.0,
  "d_impact": 0.0
}}

Target language only: {_language_name(course.get("language") or lesson.get("language"))}
Lesson:
{json.dumps({'title': lesson.get('title'), 'content': lesson.get('content'), 'emailSubject': lesson.get('emailSubject'), 'emailBody': lesson.get('emailBody')}, ensure_ascii=False)}
Validation errors:
{json.dumps(validation_errors, ensure_ascii=False)}
Human feedback:
{json.dumps(feedback_rows, ensure_ascii=False)}
""".strip()
        started = time.perf_counter()
        draft_breakdown = self._json_from_markdown_provider(drafter, drafter_prompt, max_tokens=700)
        timings.append({"provider": f"{drafter.name}:drafter", "status": "success", "durationMs": int((time.perf_counter() - started) * 1000)})

        writer_prompt = f"""
You are the Writer in Amanoba QC.
Return strict JSON only:
{{
  "title": "...",
  "content": "...",
  "emailSubject": "...",
  "emailBody": "...",
  "w_conf": 0.0,
  "w_impact": 0.0
}}

Rules:
- Use only {_language_name(course.get("language") or lesson.get("language"))}
- Keep Markdown lesson structure
- No mixed language
- Improve clarity, usefulness, and flow

Lesson:
{json.dumps({'title': lesson.get('title'), 'content': lesson.get('content'), 'emailSubject': lesson.get('emailSubject'), 'emailBody': lesson.get('emailBody')}, ensure_ascii=False)}
Rewrite brief:
{json.dumps(draft_breakdown, ensure_ascii=False)}
""".strip()
        started = time.perf_counter()
        writer_result = self._json_from_markdown_provider(writer, writer_prompt, max_tokens=1800)
        timings.append({"provider": f"{writer.name}:writer", "status": "success", "durationMs": int((time.perf_counter() - started) * 1000)})

        candidate = {
            "title": writer_result.get("title"),
            "content": writer_result.get("content"),
            "emailSubject": writer_result.get("emailSubject"),
            "emailBody": writer_result.get("emailBody"),
        }

        judge_prompt = f"""
You are the Judge in Amanoba QC.
Return strict JSON only:
{{
  "accept": true,
  "reason": "...",
  "revisionNote": "...",
  "j_conf": 0.0,
  "j_impact": 0.0
}}

Accept only if:
- target language is pure
- lesson structure is complete
- lesson is clearly better than original
- email copy is usable

Original:
{json.dumps({'title': lesson.get('title'), 'content': lesson.get('content'), 'emailSubject': lesson.get('emailSubject'), 'emailBody': lesson.get('emailBody')}, ensure_ascii=False)}
Candidate:
{json.dumps(candidate, ensure_ascii=False)}
Validation errors to fix:
{json.dumps(validation_errors, ensure_ascii=False)}
""".strip()
        started = time.perf_counter()
        judge_result = self._json_from_markdown_provider(judge, judge_prompt, max_tokens=400)
        timings.append({"provider": f"{judge.name}:judge", "status": "success", "durationMs": int((time.perf_counter() - started) * 1000)})

        d_conf = self._clamp_score(draft_breakdown.get("d_conf"), 0.65)
        d_impact = self._clamp_score(draft_breakdown.get("d_impact"), 0.65)
        w_conf = self._clamp_score(writer_result.get("w_conf"), 0.7)
        w_impact = self._clamp_score(writer_result.get("w_impact"), 0.7)
        j_conf = self._clamp_score(judge_result.get("j_conf"), 0.75)
        j_impact = self._clamp_score(judge_result.get("j_impact"), 0.75)
        trust_score = round(d_conf * w_conf * j_conf, 4)
        impact_score = round(d_impact * w_impact * j_impact, 4)
        validation = audit_lesson(candidate, str(course.get("language") or lesson.get("language") or ""))
        accepted = bool(judge_result.get("accept")) and validation.is_valid and trust_score >= 0.35
        return {
            "provider": "specialist-pipeline",
            "payload": candidate,
            "validation": validation,
            "accepted": accepted,
            "trustScore": trust_score,
            "impactScore": impact_score,
            "judgeReason": str(judge_result.get("reason") or ""),
            "revisionNote": str(judge_result.get("revisionNote") or ""),
            "timings": timings,
            "roles": {
                "drafter": draft_breakdown,
                "writer": writer_result,
                "judge": judge_result,
            },
        }

    def _provider_names(self, preferred_order: list[str] | None = None) -> list[str]:
        ordered = list(preferred_order or self.provider_order)
        names: list[str] = []
        for item in ordered:
            name = str(item or "").strip()
            if not name or name in names:
                continue
            names.append(name)
        return names

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

    def creator_provider(self, role: str) -> BaseProvider:
        role_key = str(role or "").strip().lower()
        provider = self.creator_role_providers.get(role_key)
        if provider is not None:
            return provider
        if role_key == "judge":
            return self.providers.get("none") or NullProvider()
        return self.selected_provider()

    def creator_role_health(self, role: str) -> dict[str, Any]:
        provider = self.creator_provider(role)
        health = provider.health().to_dict()
        health["creatorRole"] = role
        if isinstance(provider, MLXProvider):
            health["residentServer"] = bool(provider.resident_server)
            health["serverHost"] = provider.server_host
            health["serverPort"] = provider.server_port
            health["residentReadyAt"] = provider._resident_server_ready_at
        return health

    def _init_creator_role_providers(self) -> None:
        creator_port_base = int(self.creator_pipeline.get("server_port_base") or 18101)
        for index, role in enumerate(("drafter", "writer", "judge")):
            role_config = dict(self.creator_pipeline.get(role) or {})
            model = str(role_config.get("model") or "").strip()
            provider_name = str(role_config.get("provider") or "").strip().lower()
            if not provider_name and model:
                provider_name = "mlx"
            installed = bool(role_config.get("installed"))
            if not installed and provider_name == "mlx" and os.path.exists(os.path.expanduser(model)):
                installed = True
            if provider_name == "validator":
                self.creator_role_providers[role] = NullProvider()
                continue
            if installed and model:
                server_port = int(role_config.get("server_port") or (creator_port_base + index))
                self.creator_role_providers[role] = MLXProvider(
                    model=model,
                    timeout=int(role_config.get("timeout") or self.providers["mlx"].timeout),
                    max_tokens=int(role_config.get("max_tokens") or self.providers["mlx"].max_tokens),
                    temperature=float(role_config.get("temperature") or getattr(self.providers["mlx"], "temperature", 0.1)),
                    lesson_max_tokens=int(role_config.get("lesson_max_tokens") or self.providers["mlx"].lesson_max_tokens),
                    question_max_tokens=int(role_config.get("question_max_tokens") or self.providers["mlx"].question_max_tokens),
                    normalizer_endpoint=str(role_config.get("normalizer_endpoint") or self.providers["mlx"].normalizer.endpoint),
                    normalizer_model=str(role_config.get("normalizer_model") or self.providers["mlx"].normalizer.model),
                    python_bin=str(role_config.get("python_bin") or self.providers["mlx"].python_bin),
                    health_timeout=int(role_config.get("health_timeout") or self.providers["mlx"].health_timeout),
                    cooldown_seconds=int(role_config.get("cooldown_seconds") or self.providers["mlx"].cooldown_seconds),
                    max_consecutive_failures=int(role_config.get("max_consecutive_failures") or self.providers["mlx"].max_consecutive_failures),
                    resident_server=bool(role_config.get("resident_server", True)),
                    server_host=str(role_config.get("server_host") or "127.0.0.1"),
                    server_port=server_port,
                    server_startup_timeout=int(role_config.get("server_startup_timeout") or 240),
                )
            else:
                self.creator_role_providers[role] = self.providers["none"]

    def warm_creator_roles(self) -> dict[str, bool]:
        results: dict[str, bool] = {}
        for role, provider in self.creator_role_providers.items():
            if isinstance(provider, MLXProvider) and provider.resident_server:
                try:
                    results[role] = provider.warm()
                except Exception:
                    results[role] = False
            else:
                results[role] = provider.health().available
        return results

    def selected_provider(self) -> BaseProvider:
        for name in self.provider_order:
            provider = self.providers.get(name)
            if not provider:
                continue
            if provider.health().available:
                return provider
        return self.providers["none"]

    def rewrite_lesson_with_failover(
        self,
        course: dict[str, Any],
        lesson: dict[str, Any],
        validation_errors: list[str],
        preferred_order: list[str] | None = None,
    ) -> dict[str, Any]:
        failures: list[str] = []
        timings: list[dict[str, Any]] = []
        target_language = str(course.get("language") or lesson.get("language") or "").strip()
        for name in self._provider_names(preferred_order):
            provider = self.providers.get(name)
            if not provider or provider.name == "none":
                continue
            health = provider.health()
            if not health.available:
                failures.append(f"{provider.name}: unavailable ({health.detail})")
                timings.append({"provider": provider.name, "status": "unavailable", "detail": health.detail, "durationMs": 0})
                continue
            started = time.perf_counter()
            try:
                payload = provider.rewrite_lesson(course, lesson, validation_errors)
                validation = audit_lesson(payload, target_language)
                if not validation.is_valid:
                    detail = "; ".join(validation.errors)
                    failures.append(f"{provider.name}: rejected invalid lesson draft ({detail})")
                    timings.append(
                        {
                            "provider": provider.name,
                            "status": "rejected",
                            "detail": detail,
                            "durationMs": int((time.perf_counter() - started) * 1000),
                        }
                    )
                    continue
                timings.append(
                    {
                        "provider": provider.name,
                        "status": "success",
                        "durationMs": int((time.perf_counter() - started) * 1000),
                    }
                )
                return {"provider": provider.name, "payload": payload, "timings": timings}
            except Exception as exc:
                failures.append(f"{provider.name}: {exc}")
                timings.append(
                    {
                        "provider": provider.name,
                        "status": "failed",
                        "detail": str(exc),
                        "durationMs": int((time.perf_counter() - started) * 1000),
                    }
                )
                if provider.name == "mlx" and "timed out" in str(exc).lower():
                    retried = self._retry_ollama_timeout_fallback_for_lesson(course, lesson, validation_errors, target_language)
                    if retried is not None:
                        retried["timings"] = timings + list(retried.get("timings") or [])
                        return retried
        raise RuntimeError("All lesson rewrite providers failed: " + " | ".join(failures))

    def rewrite_question_with_failover(
        self,
        course: dict[str, Any],
        lesson: dict[str, Any],
        question: dict[str, Any],
        validation_errors: list[str],
        preferred_order: list[str] | None = None,
    ) -> dict[str, Any]:
        failures: list[str] = []
        timings: list[dict[str, Any]] = []
        target_language = str(course.get("language") or lesson.get("language") or question.get("language") or "").strip()
        for name in self._provider_names(preferred_order):
            provider = self.providers.get(name)
            if not provider or provider.name == "none":
                continue
            health = provider.health()
            if not health.available:
                failures.append(f"{provider.name}: unavailable ({health.detail})")
                timings.append({"provider": provider.name, "status": "unavailable", "detail": health.detail, "durationMs": 0})
                continue
            started = time.perf_counter()
            try:
                payload = provider.rewrite_question(course, lesson, question, validation_errors)
                validation = validate_question(payload, target_language)
                if not validation.is_valid:
                    detail = "; ".join(validation.errors)
                    failures.append(f"{provider.name}: rejected invalid question draft ({detail})")
                    timings.append(
                        {
                            "provider": provider.name,
                            "status": "rejected",
                            "detail": detail,
                            "durationMs": int((time.perf_counter() - started) * 1000),
                        }
                    )
                    continue
                timings.append(
                    {
                        "provider": provider.name,
                        "status": "success",
                        "durationMs": int((time.perf_counter() - started) * 1000),
                    }
                )
                return {"provider": provider.name, "payload": payload, "timings": timings}
            except Exception as exc:
                failures.append(f"{provider.name}: {exc}")
                timings.append(
                    {
                        "provider": provider.name,
                        "status": "failed",
                        "detail": str(exc),
                        "durationMs": int((time.perf_counter() - started) * 1000),
                    }
                )
                if provider.name == "mlx" and "timed out" in str(exc).lower():
                    retried = self._retry_ollama_timeout_fallback_for_question(course, lesson, question, validation_errors, target_language)
                    if retried is not None:
                        retried["timings"] = timings + list(retried.get("timings") or [])
                        return retried
        raise RuntimeError("All question rewrite providers failed: " + " | ".join(failures))

    def _retry_ollama_timeout_fallback_for_lesson(
        self,
        course: dict[str, Any],
        lesson: dict[str, Any],
        validation_errors: list[str],
        target_language: str,
    ) -> dict[str, Any] | None:
        provider = self.providers.get("ollama")
        if not isinstance(provider, OllamaProvider) or not provider.fallback_models:
            return None
        started = time.perf_counter()
        try:
            payload = provider.rewrite_lesson_timeout_fallback(course, lesson, validation_errors)
            validation = audit_lesson(payload, target_language)
            if not validation.is_valid:
                detail = "; ".join(validation.errors)
                raise RuntimeError(f"Ollama timeout fallback returned invalid lesson draft: {detail}")
            return {
                "provider": "ollama-timeout-fallback",
                "payload": payload,
                "timings": [
                    {
                        "provider": "ollama-timeout-fallback",
                        "status": "success",
                        "detail": ", ".join(provider.fallback_models),
                        "durationMs": int((time.perf_counter() - started) * 1000),
                    }
                ],
            }
        except Exception:
            return None

    def _retry_ollama_timeout_fallback_for_question(
        self,
        course: dict[str, Any],
        lesson: dict[str, Any],
        question: dict[str, Any],
        validation_errors: list[str],
        target_language: str,
    ) -> dict[str, Any] | None:
        provider = self.providers.get("ollama")
        if not isinstance(provider, OllamaProvider) or not provider.fallback_models:
            return None
        started = time.perf_counter()
        try:
            payload = provider.rewrite_question_timeout_fallback(course, lesson, question, validation_errors)
            validation = validate_question(payload, target_language)
            if not validation.is_valid:
                detail = "; ".join(validation.errors)
                raise RuntimeError(f"Ollama timeout fallback returned invalid question draft: {detail}")
            return {
                "provider": "ollama-timeout-fallback",
                "payload": payload,
                "timings": [
                    {
                        "provider": "ollama-timeout-fallback",
                        "status": "success",
                        "detail": ", ".join(provider.fallback_models),
                        "durationMs": int((time.perf_counter() - started) * 1000),
                    }
                ],
            }
        except Exception:
            return None

    def generate_creator_stage(
        self,
        stage_key: str,
        topic: str,
        target_language: str,
        research_mode: str,
        current_artifact: str,
        context_artifacts: dict[str, str] | None = None,
        source_pack: list[dict[str, str]] | None = None,
        revision_request: str = "",
    ) -> dict[str, Any]:
        context_artifacts = context_artifacts or {}
        source_pack = source_pack or []
        role = self._creator_stage_role(stage_key)
        provider = self.creator_provider(role)
        provider_health = provider.health()
        prompt = _creator_stage_prompt(
            stage_key=stage_key,
            topic=topic,
            target_language=target_language,
            research_mode=research_mode,
            current_artifact=current_artifact,
            context_artifacts=context_artifacts,
            source_pack=source_pack,
            revision_request=revision_request,
        )
        max_tokens_by_stage = {
            "research": 1800,
            "blueprint": 3200,
            "lesson_generation": 5200,
            "quiz_generation": 4200,
        }
        try:
            content = provider.generate_markdown(prompt, max_tokens=max_tokens_by_stage.get(stage_key, 1800)).strip()
            if not content:
                raise RuntimeError("Provider returned empty content.")
            return {
                "provider": provider.name,
                "role": role,
                "model": str(provider_health.resolved_model or provider_health.configured_model or ""),
                "status": provider_health.status,
                "content": content,
            }
        except Exception as exc:
            return {
                "provider": "fallback",
                "role": role,
                "model": str(provider_health.resolved_model or provider_health.configured_model or ""),
                "status": provider_health.status,
                "content": _fallback_creator_stage_markdown(
                    stage_key=stage_key,
                    topic=topic,
                    target_language=target_language,
                    research_mode=research_mode,
                current_artifact=current_artifact,
                context_artifacts=context_artifacts,
                source_pack=source_pack,
                revision_request=revision_request,
            ),
                "warning": str(exc),
            }

    def _creator_stage_role(self, stage_key: str) -> str:
        stage = str(stage_key or "").strip().lower()
        if stage in {"research", "blueprint"}:
            return "drafter"
        if stage in {"lesson_generation", "quiz_generation"}:
            return "writer"
        if stage in {"qc_review", "draft_to_live"}:
            return "judge"
        return "writer"


def _creator_stage_prompt(
    stage_key: str,
    topic: str,
    target_language: str,
    research_mode: str,
    current_artifact: str,
    context_artifacts: dict[str, str],
    source_pack: list[dict[str, str]],
    revision_request: str,
) -> str:
    context_chunks = []
    for key in ("research", "blueprint", "lesson_generation", "quiz_generation"):
        value = str(context_artifacts.get(key) or "").strip()
        if value:
            context_chunks.append(f"## {key}\n{value}")
    context_block = "\n\n".join(context_chunks) if context_chunks else "No prior stage artifacts yet."
    source_lines = []
    for item in source_pack[:8]:
        source_lines.append(
            f"- {item.get('title') or 'Untitled source'} | domain={item.get('domain') or '-'} | score={item.get('score') or '-'} | {item.get('url') or '-'} | {item.get('snippet') or ''}"
        )
    source_block = "\n".join(source_lines) if source_lines else "No external source pack collected."
    revision_block = str(revision_request or "").strip()
    stage_contracts = {
        "research": (
            "Research artifact contract:\n"
            "- Use markdown.\n"
            "- Include clear sections for learner problem, audience, outcomes, scope boundaries, evidence needs, and source pack insights.\n"
            "- Distinguish timeless knowledge from current knowledge.\n"
            "- Keep it operational, not essay-like."
        ),
        "blueprint": (
            "Blueprint artifact contract:\n"
            "- Build a true 30-day architecture.\n"
            "- For every day, use this exact pattern:\n"
            "### Day 01 — Title\n"
            "- Module: ...\n"
            "- Goal: ...\n"
            "- Deliverable: ...\n"
            "- Quiz focus: ...\n"
            "- The 30-day structure must be clearly derived from the approved research brief.\n"
            "- Include audience signals, outcome signals, scope boundaries, quality risks, and source signals used."
        ),
        "lesson_generation": (
            "Lesson batch artifact contract:\n"
            "- Generate a full 30-day lesson draft batch from the approved blueprint only.\n"
            "- For every day, use this exact pattern:\n"
            "### Day 01 Lesson Draft\n"
            "- Lesson title: ...\n"
            "- Learning goal: ...\n"
            "- Deliverable: ...\n"
            "- Email subject: ...\n"
            "- Guided exercise focus: ...\n"
            "- Independent exercise focus: ...\n"
            "- Self-check focus: ...\n"
            "- Quiz focus: ...\n"
            "#### Lesson Body Draft\n"
            "## ...\n"
            "#### Email Body Draft\n"
            "## ...\n"
            "- Keep the target language pure and application-first."
        ),
        "quiz_generation": (
            "Quiz batch artifact contract:\n"
            "- Generate a full 30-day quiz draft batch from the approved lesson batch only.\n"
            "- For every day, use this exact pattern:\n"
            "### Day 01 Quiz Draft\n"
            "- Lesson title: ...\n"
            "- Quiz focus: ...\n"
            "- Batch target: 7 application-first questions\n"
            "#### Question 1\n"
            "- Stem focus: ...\n"
            "- Correct answer intent: ...\n"
            "- Distractor themes: ...\n"
            "- Question type: application\n"
            "- Keep all 7 question drafts aligned to the lesson deliverable and the target language only."
        ),
    }
    stage_contract = stage_contracts.get(stage_key, "Stage artifact contract:\n- Return a practical markdown artifact for this stage.")
    return (
        "Return markdown only. Do not return JSON. Do not explain outside the artifact.\n\n"
        "You are drafting a sovereign course-creation stage artifact for Amanoba.\n"
        "Follow these constraints exactly:\n"
        "- Target language only. No mixed-language output.\n"
        "- Be concrete, structured, and operational.\n"
        "- Align to Amanoba's markdown-first lesson and quiz standards.\n"
        "- Avoid filler, generic platitudes, and unsupported claims.\n"
        "- Use the external source pack when it contains relevant current knowledge.\n"
        "- Do not invent citations, dates, or claims that are not supported by the source pack.\n"
        "- Treat amanoba.com as downstream final editing only; this artifact belongs to the local amanoba_courses workflow.\n\n"
        f"{stage_contract}\n\n"
        f"Stage: {stage_key}\n"
        f"Topic: {topic}\n"
        f"Target language: {target_language}\n"
        f"Research mode: {research_mode}\n\n"
        f"Human feedback for this next draft:\n{revision_block or '- No new human feedback.'}\n\n"
        f"Current stage artifact draft:\n{current_artifact.strip() or '-'}\n\n"
        f"Prior approved context:\n{context_block}\n\n"
        f"External source pack:\n{source_block}\n\n"
        "If human feedback exists, treat it as mandatory. Produce a materially improved markdown artifact for the current stage."
    )


def _fallback_creator_stage_markdown(
    stage_key: str,
    topic: str,
    target_language: str,
    research_mode: str,
    current_artifact: str,
    context_artifacts: dict[str, str],
    source_pack: list[dict[str, str]],
    revision_request: str,
) -> str:
    if current_artifact.strip():
        return current_artifact.strip()
    if stage_key == "research":
        sources_md = "\n".join(
            f"- [{item.get('title') or item.get('url')}]({item.get('url')}) — {item.get('snippet') or ''}"
            for item in source_pack[:6]
            if item.get("url")
        ) or "- No external sources collected."
        return (
            f"# Research Brief\n\n"
            f"## Topic\n{topic}\n\n"
            f"## Target Language\n{target_language}\n\n"
            f"## Research Mode\n{research_mode}\n\n"
            f"## Learner Problem\n"
            f"Define the main practical problem a learner wants to solve through {topic}.\n\n"
            f"## Audience\n"
            f"- Primary audience\n"
            f"- Skill level\n"
            f"- Operating context\n\n"
            f"## Desired Outcomes\n"
            f"- Observable capability 1\n"
            f"- Observable capability 2\n"
            f"- Observable capability 3\n\n"
            f"## Scope Boundaries\n"
            f"- In scope\n"
            f"- Out of scope\n"
            f"- Follow-up opportunities\n\n"
            f"## Evidence Needs\n"
            f"- Timeless knowledge\n"
            f"- Time-sensitive knowledge\n"
            f"- Source freshness checkpoints\n"
            f"\n## Source Pack\n"
            f"{sources_md}\n"
        )
    return current_artifact.strip() or f"# {stage_key.replace('_', ' ').title()}\n"
