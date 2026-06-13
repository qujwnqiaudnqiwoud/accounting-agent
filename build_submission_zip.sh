#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

LEADER_NAME="${1:-徐北辰}"
PYTHON_BIN="${PYTHON:-python3}"

"$PYTHON_BIN" scripts_build_zip.py "$LEADER_NAME"
