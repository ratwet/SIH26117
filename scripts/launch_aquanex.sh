#!/usr/bin/env bash
# =====================================================================
# Aquanex — Native Linux Desktop Launcher (scripts/launch_aquanex.sh)
# Launches the native Linux desktop application window for SovereignWorkbench
# =====================================================================

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_URL="${1:-http://127.0.0.1:8000}"

echo "================================================================="
echo "🛡️  LAUNCHING AQUANEX NATIVE LINUX DESKTOP CLIENT"
echo "   Target Gateway: $TARGET_URL"
echo "================================================================="

cd "$ROOT_DIR"
exec python3 "$ROOT_DIR/scripts/run_linux_desktop.py" "$TARGET_URL"
