#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec /bin/zsh "$ROOT_DIR/start_amanoba.command"
