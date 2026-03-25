#!/bin/bash
set -euo pipefail
ROOT="${AMANOBA_COURSES_ROOT:-/Users/moldovancsaba/Projects/amanoba_courses}"
CONFIG="${AMANOBA_CONFIG_PATH:-$ROOT/course_quality_daemon.json}"
PYTHON_BIN="${AMANOBA_PYTHON_BIN:-$ROOT/.venv-mlx/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3 || true)"
fi
if [[ -z "$PYTHON_BIN" || ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="/usr/bin/python3"
fi
cd "$ROOT"

# Extract MLX config for Fast Worker
MODEL=$(/usr/bin/python3 -c "import json, os; cfg=json.load(open('$CONFIG')); print(cfg.get('runtime', {}).get('mlx', {}).get('model', ''))")
PORT=$(/usr/bin/python3 -c "import json, os; cfg=json.load(open('$CONFIG')); print(cfg.get('runtime', {}).get('mlx', {}).get('fast_mlx_port', 8501))")

if [[ -n "$MODEL" && -d "$MODEL" ]]; then
  echo "Starting Fast MLX worker (port $PORT, model $(basename "$MODEL"))..."
  "$PYTHON_BIN" -m course_quality_daemon.fast_mlx_worker --model "$MODEL" --port "$PORT" > .course-quality/fast-mlx-worker.log 2>&1 &
  FAST_MLX_PID=$!
  echo $FAST_MLX_PID > .course-quality/fast_mlx_worker.pid
  
  # Ensure cleanup on exit
  trap 'kill $FAST_MLX_PID 2>/dev/null || true; rm -f .course-quality/fast_mlx_worker.pid' EXIT
fi

exec /usr/bin/nice -n 10 "$PYTHON_BIN" -m course_quality_daemon --config "$CONFIG" daemon
