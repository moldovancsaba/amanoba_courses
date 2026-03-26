#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CONFIG_PATH="$REPO_ROOT/course_quality_daemon.json"
DASHBOARD_URL="http://127.0.0.1:8765"

echo "AmanobaMenubar resource check"
echo "repo: $REPO_ROOT"
echo

for cmd in swiftc curl launchctl caffeinate; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "command:$cmd OK $(command -v "$cmd")"
  else
    echo "command:$cmd MISSING"
  fi
done

echo
python3 - <<'PY' "$CONFIG_PATH"
import json
import sys
from pathlib import Path

cfg = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
runtime = dict(cfg.get("runtime") or {})
print("configured models:")
print(f"  provider_order: {runtime.get('provider_order')}")
print(f"  writer_provider_order: {runtime.get('writer_provider_order')}")
mlx = dict(runtime.get("mlx") or {})
ollama = dict(runtime.get("ollama") or {})
openai = dict(runtime.get("openai") or {})
print(f"  mlx_model: {mlx.get('model')}")
print(f"  mlx_python_bin: {mlx.get('python_bin')}")
print(f"  ollama_model: {ollama.get('model')}")
print(f"  ollama_fallback_models: {ollama.get('fallback_models')}")
print(f"  openai_model: {openai.get('model')}")
print("resident creator roles:")
for item in runtime.get("resident_creator_roles") or []:
    print(f"  {item.get('name')}: {item.get('host')}:{item.get('port')} {item.get('model_label')}")
PY

echo
if curl -fsS "$DASHBOARD_URL/api/health" >/tmp/amanoba-menubar-health.json 2>/dev/null; then
  echo "dashboard: OK $DASHBOARD_URL"
  python3 - <<'PY'
import json
from pathlib import Path
obj = json.loads(Path("/tmp/amanoba-menubar-health.json").read_text(encoding="utf-8"))
selected = ((obj.get("runtime") or {}).get("selected") or {})
print(f"selected_provider: {selected.get('provider')} ({selected.get('status')})")
for item in ((obj.get("runtime") or {}).get("providers") or []):
    print(f"provider:{item.get('provider')} {item.get('status')} {item.get('detail')}")
for item in ((obj.get("system") or {}).get("residentRoles") or []):
    print(f"resident:{item.get('name')} {item.get('status')} {item.get('modelLabel') or '-'} {item.get('detail')}")
PY
else
  echo "dashboard: DOWN $DASHBOARD_URL"
fi

echo
for port in 8080 8081 8082 8765 11434; do
  if nc -z 127.0.0.1 "$port" >/dev/null 2>&1; then
    echo "port:$port OPEN"
  else
    echo "port:$port CLOSED"
  fi
done
