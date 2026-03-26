#!/bin/bash
set -euo pipefail
for label in com.amanoba.coursequality.worker com.amanoba.coursequality.dashboard com.amanoba.coursequality.watchdog com.amanoba.coursequality.ollama com.amanoba.coursequality.caffeinate com.amanoba.coursequality.role.drafter com.amanoba.coursequality.role.writer com.amanoba.coursequality.role.judge; do
  echo "== $label =="
  launchctl print "gui/$UID/$label" 2>/dev/null | sed -n '1,40p' || echo "not loaded"
  echo
 done
