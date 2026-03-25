#!/bin/bash
set -euo pipefail
ROOT="${AMANOBA_COURSES_ROOT:-/Users/moldovancsaba/Projects/amanoba_courses}"
CONFIG_PATH="${AMANOBA_CONFIG_PATH:-$ROOT/course_quality_daemon.json}"
LAUNCH_DIR="$HOME/Library/LaunchAgents"
LOG_DIR="$ROOT/.course-quality/launchd"
mkdir -p "$LAUNCH_DIR" "$LOG_DIR"
WORKER_INTERVAL="$(CONFIG_PATH_ENV="$CONFIG_PATH" python3 - <<'PY'
import json
import os
from pathlib import Path
path = Path(os.environ["CONFIG_PATH_ENV"])
raw = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
print(int(raw.get('queue_check_interval_seconds') or 300))
PY
)"
WATCHDOG_INTERVAL="$(CONFIG_PATH_ENV="$CONFIG_PATH" python3 - <<'PY'
import json
import os
from pathlib import Path
path = Path(os.environ["CONFIG_PATH_ENV"])
raw = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
watchdog = raw.get('watchdog') or {}
print(int(watchdog.get('check_interval_seconds') or 600))
PY
)"
WORKER_PLIST="$LAUNCH_DIR/com.amanoba.coursequality.worker.plist"
DASHBOARD_PLIST="$LAUNCH_DIR/com.amanoba.coursequality.dashboard.plist"
OLLAMA_PLIST="$LAUNCH_DIR/com.amanoba.coursequality.ollama.plist"
WATCHDOG_PLIST="$LAUNCH_DIR/com.amanoba.coursequality.watchdog.plist"
cat > "$WORKER_PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>com.amanoba.coursequality.worker</string>
<key>ProgramArguments</key><array><string>$ROOT/scripts/course-quality-worker.sh</string></array>
<key>WorkingDirectory</key><string>$ROOT</string>
<key>EnvironmentVariables</key><dict>
<key>AMANOBA_COURSES_ROOT</key><string>$ROOT</string>
<key>AMANOBA_PYTHON_BIN</key><string>$ROOT/.venv-mlx/bin/python</string>
<key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
</dict>
<key>RunAtLoad</key><true/>
<key>KeepAlive</key><true/>
<key>StandardOutPath</key><string>$LOG_DIR/worker.out.log</string>
<key>StandardErrorPath</key><string>$LOG_DIR/worker.err.log</string>
</dict></plist>
PLIST
cat > "$DASHBOARD_PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>com.amanoba.coursequality.dashboard</string>
<key>ProgramArguments</key><array><string>$ROOT/scripts/course-quality-dashboard.sh</string></array>
<key>WorkingDirectory</key><string>$ROOT</string>
<key>EnvironmentVariables</key><dict>
<key>AMANOBA_COURSES_ROOT</key><string>$ROOT</string>
<key>AMANOBA_PYTHON_BIN</key><string>$ROOT/.venv-mlx/bin/python</string>
<key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
</dict>
<key>RunAtLoad</key><true/>
<key>KeepAlive</key><true/>
<key>StandardOutPath</key><string>$LOG_DIR/dashboard.out.log</string>
<key>StandardErrorPath</key><string>$LOG_DIR/dashboard.err.log</string>
</dict></plist>
PLIST
cat > "$WATCHDOG_PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>com.amanoba.coursequality.watchdog</string>
<key>ProgramArguments</key><array><string>$ROOT/scripts/course-quality-watchdog.sh</string></array>
<key>WorkingDirectory</key><string>$ROOT</string>
<key>EnvironmentVariables</key><dict>
<key>AMANOBA_COURSES_ROOT</key><string>$ROOT</string>
<key>AMANOBA_PYTHON_BIN</key><string>$ROOT/.venv-mlx/bin/python</string>
<key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
</dict>
<key>RunAtLoad</key><true/>
<key>StartInterval</key><integer>$WATCHDOG_INTERVAL</integer>
<key>StandardOutPath</key><string>$LOG_DIR/watchdog.out.log</string>
<key>StandardErrorPath</key><string>$LOG_DIR/watchdog.err.log</string>
</dict></plist>
PLIST
if command -v ollama >/dev/null 2>&1; then
cat > "$OLLAMA_PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>com.amanoba.coursequality.ollama</string>
<key>ProgramArguments</key><array><string>$ROOT/scripts/course-quality-ollama.sh</string></array>
<key>EnvironmentVariables</key><dict>
<key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
</dict>
<key>RunAtLoad</key><true/>
<key>KeepAlive</key><true/>
<key>StandardOutPath</key><string>$LOG_DIR/ollama.out.log</string>
<key>StandardErrorPath</key><string>$LOG_DIR/ollama.err.log</string>
</dict></plist>
PLIST
fi
for label in com.amanoba.coursequality.worker com.amanoba.coursequality.dashboard com.amanoba.coursequality.watchdog com.amanoba.coursequality.ollama; do
  launchctl bootout "gui/$UID/$label" >/dev/null 2>&1 || true
done
[[ -f "$OLLAMA_PLIST" ]] && launchctl bootstrap "gui/$UID" "$OLLAMA_PLIST" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$UID" "$WORKER_PLIST"
launchctl bootstrap "gui/$UID" "$DASHBOARD_PLIST"
launchctl bootstrap "gui/$UID" "$WATCHDOG_PLIST"
launchctl kickstart -k "gui/$UID/com.amanoba.coursequality.worker"
launchctl kickstart -k "gui/$UID/com.amanoba.coursequality.dashboard"
launchctl kickstart -k "gui/$UID/com.amanoba.coursequality.watchdog"
[[ -f "$OLLAMA_PLIST" ]] && launchctl kickstart -k "gui/$UID/com.amanoba.coursequality.ollama" || true
echo "Installed launch agents. Dashboard: http://127.0.0.1:8765"
