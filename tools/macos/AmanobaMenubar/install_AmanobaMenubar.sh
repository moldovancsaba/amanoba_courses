#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
APP_NAME="AmanobaMenubar"
APP_DIR="$HOME/Applications/${APP_NAME}.app"
BIN_DIR="$APP_DIR/Contents/MacOS"
RES_DIR="$APP_DIR/Contents/Resources"
TMP_SWIFT="/tmp/${APP_NAME}.swift"
APP_VERSION="0.2.0"

if pgrep -f "${APP_DIR}/Contents/MacOS/${APP_NAME}" >/dev/null 2>&1; then
  pkill -f "${APP_DIR}/Contents/MacOS/${APP_NAME}" >/dev/null 2>&1 || true
fi
pkill -x "${APP_NAME}" >/dev/null 2>&1 || true
osascript -e "tell application \"${APP_NAME}\" to quit" >/dev/null 2>&1 || true
rm -rf "$APP_DIR"

# Keep only the current Amanoba menubar bundle; remove known legacy copies.
for legacy in \
  "$HOME/Applications/HatoriMenubar.app" \
  "$HOME/Applications/OpenClawMenubar.app" \
  "$HOME/Applications/ReplyMenubar.app" \
  "/Applications/HatoriMenubar.app" \
  "/Applications/OpenClawMenubar.app" \
  "/Applications/ReplyMenubar.app" \
  "/Applications/AmanobaMenubar.app"; do
  rm -rf "$legacy"
done

mkdir -p "$BIN_DIR" "$RES_DIR"

sed \
  -e "s#__REPO_ROOT__#${REPO_ROOT}#g" \
  -e "s#__APP_VERSION__#${APP_VERSION}#g" \
  "$REPO_ROOT/tools/macos/AmanobaMenubar/main.swift.template" > "$TMP_SWIFT"

swiftc "$TMP_SWIFT" -o "$BIN_DIR/${APP_NAME}" -framework AppKit

REPO_ROOT_ENV="$REPO_ROOT" RES_DIR_ENV="$RES_DIR" APP_VERSION_ENV="$APP_VERSION" python3 - <<'PY'
import json
import os
from pathlib import Path

repo_root = Path(os.environ["REPO_ROOT_ENV"])
res_dir = Path(os.environ["RES_DIR_ENV"])
app_version = os.environ["APP_VERSION_ENV"]
config_path = repo_root / "course_quality_daemon.json"
cfg = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
runtime = dict(cfg.get("runtime") or {})
manifest = {
    "app": "AmanobaMenubar",
    "version": app_version,
    "dashboardUrl": "http://127.0.0.1:8765",
    "workspaceRoot": str(repo_root),
    "requiredCommands": ["swiftc", "curl", "launchctl", "caffeinate"],
    "runtimeModels": {
        "providerOrder": list(runtime.get("provider_order") or []),
        "writerProviderOrder": list(runtime.get("writer_provider_order") or []),
        "mlx": dict(runtime.get("mlx") or {}),
        "ollama": dict(runtime.get("ollama") or {}),
        "openai": dict(runtime.get("openai") or {}),
    },
    "residentCreatorRoles": list(runtime.get("resident_creator_roles") or []),
}
(res_dir / "runtime-resources.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

cat > "$APP_DIR/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key>
  <string>${APP_NAME}</string>
  <key>CFBundleExecutable</key>
  <string>${APP_NAME}</string>
  <key>CFBundleIdentifier</key>
  <string>com.amanoba.menubar</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleShortVersionString</key>
  <string>${APP_VERSION}</string>
  <key>LSUIElement</key>
  <true/>
  <key>NSHighResolutionCapable</key>
  <true/>
</dict>
</plist>
PLIST

chmod +x "$BIN_DIR/${APP_NAME}"

echo "Installed: $APP_DIR (version ${APP_VERSION})"
echo "Bundled resource manifest: $RES_DIR/runtime-resources.json"

osascript -e "tell application \"System Events\"
  if exists login item \"${APP_NAME}\" then
    delete login item \"${APP_NAME}\"
  end if
  make login item at end with properties {path:\"${APP_DIR}\", hidden:false}
end tell" >/dev/null 2>&1 || true

echo "Auto-launch enabled."
echo "Run: open \"$APP_DIR\""
