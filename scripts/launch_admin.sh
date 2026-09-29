#!/usr/bin/env bash
# =====================================================================
# Aquanex Admin - Level 1 Desktop Launcher (scripts/launch_admin.sh)
# Launches Aquanex pre-authenticated as Rajat (IT Systems Administrator)
# =====================================================================

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_URL="${1:-http://127.0.0.1:8000}"

echo "================================================================="
echo "👑 LAUNCHING AQUANEX ADMIN - LEVEL 1 GOVERNANCE CLIENT"
echo "   Personnel: Rajat (IT Systems Administrator • PIN 1170)"
echo "   Target Gateway: $TARGET_URL"
echo "================================================================="

cd "$ROOT_DIR"
exec python3 "$ROOT_DIR/scripts/run_linux_desktop.py" "$TARGET_URL" --persona admin "$@"
