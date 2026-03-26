#!/bin/bash
set -euo pipefail
ROOT="${AMANOBA_COURSES_ROOT:-/Users/chappie/Projects/amanoba_courses}"
CONFIG="${AMANOBA_CONFIG_PATH:-$ROOT/course_quality_daemon.json}"
PYTHON_BIN="${AMANOBA_PYTHON_BIN:-$ROOT/.venv-mlx/bin/python}"
ROLE="${AMANOBA_RESIDENT_ROLE:-}"
if [[ -z "$ROLE" ]]; then
  echo "AMANOBA_RESIDENT_ROLE is required" >&2
  exit 1
fi
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3 || true)"
fi
if [[ -z "$PYTHON_BIN" || ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="/usr/bin/python3"
fi
PYTHON_USER_SITE="$("$PYTHON_BIN" - <<'PY'
import site
print(site.getusersitepackages())
PY
)"
export PYTHONPATH="${PYTHON_USER_SITE}${PYTHONPATH:+:$PYTHONPATH}"
cd "$ROOT"
exec "$PYTHON_BIN" -m course_quality_daemon.resident_roles --config "$CONFIG" --role "$ROLE"
