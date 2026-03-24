from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


class OpenAIFixer:
    def __init__(self, api_key_env: str, model: str) -> None:
        self.api_key = os.environ.get(api_key_env, "").strip()
        self.model = model

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def rewrite_question(
        self,
        course: dict[str, Any],
        lesson: dict[str, Any],
        question: dict[str, Any],
        validation_errors: list[str],
    ) -> dict[str, Any]:
        prompt = f"""
Rewrite exactly one quiz question as strict JSON only.

Return an object with these keys:
- question
- options
- correctIndex
- questionType
- difficulty
- category
- hashtags

Rules:
- Keep the same lesson topic and language.
- Standalone only. No references to "the lesson" or "the course".
- Scenario-based and concrete.
- No recall questions.
- 4 options.
- Each option must be at least 25 characters.
- The stem must be at least 40 characters.
- Wrong answers must be plausible domain mistakes.

Course:
{json.dumps({'courseId': course.get('courseId'), 'name': course.get('name'), 'language': course.get('language')}, ensure_ascii=False, indent=2)}

Lesson:
{json.dumps({'lessonId': lesson.get('lessonId'), 'title': lesson.get('title'), 'language': lesson.get('language')}, ensure_ascii=False, indent=2)}

Lesson content excerpt:
{lesson.get('content', '')[:4000]}

Original question:
{json.dumps(question, ensure_ascii=False, indent=2)}

Validation errors:
{json.dumps(validation_errors, ensure_ascii=False, indent=2)}
""".strip()
        return self._request_json(prompt)

    def rewrite_lesson(
        self,
        course: dict[str, Any],
        lesson: dict[str, Any],
        validation_errors: list[str],
    ) -> dict[str, Any]:
        prompt = f"""
Rewrite exactly one lesson as strict JSON only.

Return an object with these keys:
- title
- content
- emailSubject
- emailBody

Rules:
- Keep the same lesson topic and language.
- Improve clarity, structure, and specificity without inventing new claims.
- Keep Markdown formatting.
- The lesson must be strong enough to support scenario-based quiz generation.

Course:
{json.dumps({'courseId': course.get('courseId'), 'name': course.get('name'), 'language': course.get('language')}, ensure_ascii=False, indent=2)}

Original lesson:
{json.dumps({'lessonId': lesson.get('lessonId'), 'title': lesson.get('title')}, ensure_ascii=False, indent=2)}

Lesson content:
{lesson.get('content', '')[:12000]}

Validation errors:
{json.dumps(validation_errors, ensure_ascii=False, indent=2)}
""".strip()
        return self._request_json(prompt)

    def _request_json(self, prompt: str) -> dict[str, Any]:
        if not self.enabled:
            raise RuntimeError("OpenAI fixer is not enabled. Set the configured API key environment variable.")

        payload = {
            "model": self.model,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt,
                        }
                    ],
                }
            ],
        }
        request = urllib.request.Request(
            url="https://api.openai.com/v1/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI request failed with HTTP {exc.code}: {details}") from exc

        text = self._extract_text(body)
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Model did not return valid JSON: {text[:500]}") from exc

    @staticmethod
    def _extract_text(body: dict[str, Any]) -> str:
        output = body.get("output") or []
        chunks: list[str] = []
        for item in output:
            if item.get("type") != "message":
                continue
            for content in item.get("content") or []:
                text = content.get("text")
                if isinstance(text, str):
                    chunks.append(text)
        if not chunks:
            raise RuntimeError("OpenAI response did not contain message text.")
        return "\n".join(chunks).strip()
