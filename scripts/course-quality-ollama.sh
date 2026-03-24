#!/bin/bash
set -euo pipefail
OLLAMA_BIN="${OLLAMA_BIN:-$(command -v ollama || true)}"
if [[ -z "$OLLAMA_BIN" || ! -x "$OLLAMA_BIN" ]]; then
  echo "ollama binary not found"
  exit 1
fi
if /usr/bin/curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  while true; do sleep 60; done
fi
exec "$OLLAMA_BIN" serve
