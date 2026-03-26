from __future__ import annotations

import argparse
import json
import signal
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from mlx_lm import generate, load
from .portable_paths import resolve_mlx_model_path, resolve_portable_path


DEFAULT_ROLE_MODELS = {
    "DRAFTER": {
        "label": "Gemma 3 270M",
        "family": "MLX quantized local model",
        "path": "/Users/chappie/.cache/huggingface/hub/models--mlx-community--gemma-3-270m-it-4bit/snapshots/ff1143e3a10547c9f2129e94ca37059b096b23f4",
        "port": 8080,
    },
    "WRITER": {
        "label": "Granite 4.0 350M (H)",
        "family": "MLX quantized local model",
        "path": "/Users/chappie/.cache/huggingface/hub/models--mlx-community--granite-4.0-h-350m-8bit/snapshots/754e5ae403ffa03922e36332ca5e528f14464a1b",
        "port": 8081,
    },
    "JUDGE": {
        "label": "Qwen 2.5 0.5B",
        "family": "MLX quantized local model",
        "path": "/Users/chappie/.cache/huggingface/hub/models--mlx-community--Qwen2.5-0.5B-Instruct-4bit/snapshots/a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3",
        "port": 8082,
    },
}


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _flatten_messages(messages: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for item in messages:
        role = str(item.get("role") or "user").strip().upper()
        content = item.get("content")
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict) and str(block.get("type") or "") == "text":
                    parts.append(str(block.get("text") or ""))
            text = "\n".join(part for part in parts if part).strip()
        else:
            text = str(content or "").strip()
        if text:
            lines.append(f"{role}: {text}")
    return "\n\n".join(lines).strip()


@dataclass
class ResidentRoleConfig:
    role: str
    host: str
    port: int
    model_label: str
    model_family: str
    model_path: Path
    warm_prompt: str
    max_tokens: int


class ResidentRoleRuntime:
    def __init__(self, config: ResidentRoleConfig) -> None:
        self.config = config
        self._lock = threading.Lock()
        self._model = None
        self._tokenizer = None
        self._started_at = utc_now()
        self._last_request_at: str | None = None
        self._last_error: str | None = None
        self._warm = False

    def start(self) -> None:
        self._model, self._tokenizer = load(str(self.config.model_path))
        self._warmup()

    def _warmup(self) -> None:
        try:
            self.generate_text(self.config.warm_prompt, max_tokens=12)
            self._warm = True
            self._last_error = None
        except Exception as exc:
            self._warm = False
            self._last_error = str(exc)

    def health(self) -> dict[str, Any]:
        return {
            "ok": self._model is not None and self._tokenizer is not None,
            "status": "WARM" if self._warm else "DEGRADED",
            "role": self.config.role,
            "endpoint": f"http://{self.config.host}:{self.config.port}",
            "host": self.config.host,
            "port": self.config.port,
            "modelLabel": self.config.model_label,
            "modelFamily": self.config.model_family,
            "modelPath": str(self.config.model_path),
            "startedAt": self._started_at,
            "lastRequestAt": self._last_request_at,
            "lastError": self._last_error,
            "generatedAt": utc_now(),
        }

    def generate_text(self, prompt: str, max_tokens: int | None = None) -> str:
        if self._model is None or self._tokenizer is None:
            raise RuntimeError(f"{self.config.role} model is not loaded.")
        with self._lock:
            text = generate(
                self._model,
                self._tokenizer,
                prompt,
                max_tokens=int(max_tokens or self.config.max_tokens),
                verbose=False,
            )
            self._last_request_at = utc_now()
            self._warm = True
            self._last_error = None
            return str(text or "").strip()


class ResidentRoleHandler(BaseHTTPRequestHandler):
    runtime: ResidentRoleRuntime

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length") or "0")
        raw = self.rfile.read(length) if length > 0 else b"{}"
        if not raw:
            return {}
        loaded = json.loads(raw.decode("utf-8"))
        return loaded if isinstance(loaded, dict) else {}

    def _write_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        if self.path in {"/", "/health"}:
            self._write_json(200, self.runtime.health())
            return
        if self.path == "/v1/models":
            self._write_json(
                200,
                {
                    "object": "list",
                    "data": [
                        {
                            "id": self.runtime.config.model_label,
                            "object": "model",
                            "owned_by": "amanoba",
                        }
                    ],
                },
            )
            return
        self._write_json(404, {"ok": False, "error": "Not found"})

    def do_POST(self) -> None:
        try:
            if self.path in {"/generate", "/api/generate"}:
                payload = self._read_json()
                prompt = str(payload.get("prompt") or "").strip()
                if not prompt:
                    self._write_json(400, {"ok": False, "error": "prompt is required"})
                    return
                max_tokens = int(payload.get("max_tokens") or payload.get("maxTokens") or self.runtime.config.max_tokens)
                text = self.runtime.generate_text(prompt, max_tokens=max_tokens)
                self._write_json(
                    200,
                    {
                        "ok": True,
                        "role": self.runtime.config.role,
                        "model": self.runtime.config.model_label,
                        "text": text,
                    },
                )
                return
            if self.path == "/v1/chat/completions":
                payload = self._read_json()
                messages = payload.get("messages") or []
                prompt = _flatten_messages(messages if isinstance(messages, list) else [])
                if not prompt:
                    self._write_json(400, {"error": {"message": "messages are required"}})
                    return
                max_tokens = int(payload.get("max_tokens") or payload.get("max_completion_tokens") or self.runtime.config.max_tokens)
                text = self.runtime.generate_text(prompt, max_tokens=max_tokens)
                now = int(time.time())
                self._write_json(
                    200,
                    {
                        "id": f"{self.runtime.config.role.lower()}-{now}",
                        "object": "chat.completion",
                        "created": now,
                        "model": self.runtime.config.model_label,
                        "choices": [
                            {
                                "index": 0,
                                "message": {"role": "assistant", "content": text},
                                "finish_reason": "stop",
                            }
                        ],
                    },
                )
                return
        except Exception as exc:
            self.runtime._last_error = str(exc)
            self._write_json(500, {"ok": False, "error": str(exc), "role": self.runtime.config.role})
            return
        self._write_json(404, {"ok": False, "error": "Not found"})


def _load_config(config_path: Path, role: str) -> ResidentRoleConfig:
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    runtime_cfg = dict(raw.get("runtime") or {})
    resident_roles = list(runtime_cfg.get("resident_creator_roles") or [])
    role_upper = role.strip().upper()
    selected = next((dict(item or {}) for item in resident_roles if str((item or {}).get("name") or "").strip().upper() == role_upper), {})
    defaults = dict(DEFAULT_ROLE_MODELS.get(role_upper) or {})
    host = str(selected.get("host") or "127.0.0.1").strip()
    port = int(selected.get("port") or defaults.get("port") or 0)
    model_path = resolve_mlx_model_path(
        str(selected.get("model") or defaults.get("path") or ""),
        base_dir=config_path.parent,
        label=str(selected.get("model_label") or defaults.get("label") or role_upper),
    )
    return ResidentRoleConfig(
        role=role_upper,
        host=host,
        port=port,
        model_label=str(selected.get("model_label") or defaults.get("label") or role_upper).strip(),
        model_family=str(selected.get("family") or defaults.get("family") or "MLX quantized local model").strip(),
        model_path=model_path,
        warm_prompt=str(selected.get("warm_prompt") or "Reply with exactly: READY").strip(),
        max_tokens=int(selected.get("max_tokens") or 192),
    )


def serve_role(config_path: Path, role: str) -> None:
    config = _load_config(config_path, role)
    if not config.model_path.exists():
        raise FileNotFoundError(f"Resident role model path not found for {config.role}: {config.model_path}")
    runtime = ResidentRoleRuntime(config)
    runtime.start()
    handler = type(f"{config.role}Handler", (ResidentRoleHandler,), {})
    handler.runtime = runtime
    server = ThreadingHTTPServer((config.host, config.port), handler)

    def _shutdown(signum: int, _frame: Any) -> None:
        del signum
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve a resident Amanoba creator role on a local MLX endpoint.")
    parser.add_argument("--config", required=True, help="Path to course_quality_daemon.json")
    parser.add_argument("--role", required=True, choices=sorted(DEFAULT_ROLE_MODELS))
    args = parser.parse_args()
    serve_role(Path(args.config).expanduser(), str(args.role))


if __name__ == "__main__":
    main()
