#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
bash "$REPO_ROOT/tools/macos/AmanobaMenubar/install_AmanobaMenubar.sh"
open "$HOME/Applications/AmanobaMenubar.app"
