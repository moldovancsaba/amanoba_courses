#!/bin/bash
set -euo pipefail

if [[ ! -x /usr/bin/caffeinate ]]; then
  echo "caffeinate binary not found"
  exit 1
fi

exec /usr/bin/caffeinate -dimsu /bin/bash -lc 'while true; do sleep 3600; done'
