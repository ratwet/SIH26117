#!/usr/bin/env bash
# =====================================================================
# Aquanex Senior - Level 2 Desktop Launcher (scripts/launch_senior.sh)
# Launches Aquanex pre-authenticated as Anand (Senior Reliability Lead)
# =====================================================================

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_URL="${1:-http://127.0.0.1:8000}"

echo "================================================================="
echo "📐 LAUNCHING AQUANEX SENIOR - LEVEL 2 STATUTORY APPROVAL CLIENT"
echo "   Personnel: Anand (Senior Reliability Lead • PIN 5700)"
echo "   Target Gateway: $TARGET_URL"
echo "================================================================="

cd "$ROOT_DIR"
exec python3 "$ROOT_DIR/scripts/run_linux_desktop.py" "$TARGET_URL" --persona senior "$@"
