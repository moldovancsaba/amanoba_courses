#!/bin/bash
set -euo pipefail
ROOT="${AMANOBA_COURSES_ROOT:-/Users/chappie/Projects/amanoba_courses}"
CONFIG="${AMANOBA_CONFIG_PATH:-$ROOT/course_quality_daemon.json}"
PYTHON_BIN="${AMANOBA_PYTHON_BIN:-$ROOT/.venv-mlx/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3 || true)"
fi
if [[ -z "$PYTHON_BIN" || ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="/usr/bin/python3"
fi
cd "$ROOT"
exec "$PYTHON_BIN" -m course_quality_daemon --config "$CONFIG" dashboard
