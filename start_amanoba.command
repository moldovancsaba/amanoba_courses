#!/bin/zsh
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "Starting Amanoba Course Quality from: $ROOT_DIR"

if [ ! -f "course_quality_daemon.json" ] || [ ! -d "course_quality_daemon" ]; then
  echo "This launcher must run from the Amanoba project folder."
  echo "Expected course_quality_daemon.json and course_quality_daemon/ were not found in: $ROOT_DIR"
  echo "Run this file instead:"
  echo "  /Users/chappie/Projects/amanoba_courses/start_amanoba.command"
  exit 1
fi

PY_CMD=""
if command -v python3 >/dev/null 2>&1; then
  PY_CMD="python3"
elif command -v python >/dev/null 2>&1; then
  PY_CMD="python"
else
  echo "Python 3 is required."
  exit 1
fi

echo "Using $($PY_CMD --version 2>&1)"

if ! command -v ollama >/dev/null 2>&1; then
  echo "Ollama is not installed."
  echo "Install it from: https://ollama.com/download"
  exit 1
fi

echo "Installing or refreshing Amanoba background services..."
bash "$ROOT_DIR/scripts/install-course-quality-launchagents.sh"

echo "Waiting for dashboard to become ready..."
READY=0
for i in {1..40}; do
  if curl -sSf http://127.0.0.1:8765/api/health >/dev/null 2>&1; then
    READY=1
    break
  fi
  sleep 1
done

if [ "$READY" != "1" ]; then
  echo "Dashboard did not become ready in time."
  echo "Check:"
  echo "  $ROOT_DIR/.course-quality/launchd/dashboard.err.log"
  echo "  $ROOT_DIR/.course-quality/launchd/worker.err.log"
  exit 1
fi

echo ""
echo "Amanoba Control Center is ready."
echo "Dashboard: http://127.0.0.1:8765"
echo ""

(open "http://127.0.0.1:8765" >/dev/null 2>&1 &) || true

echo "Press Enter to close this launcher window."
read -r _
