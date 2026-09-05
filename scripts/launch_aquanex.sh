#!/usr/bin/env bash
# =====================================================================
# Aquanex — Universal Native Linux Desktop Launcher (scripts/launch_aquanex.sh)
# Usage:
#   ./scripts/launch_aquanex.sh                  # Standard launch with persona selector
#   ./scripts/launch_aquanex.sh --persona admin  # Level 1: IT Systems Admin
#   ./scripts/launch_aquanex.sh --persona senior # Level 2: Senior Reliability Lead
#   ./scripts/launch_aquanex.sh --persona junior # Level 3: Field Technician
# =====================================================================

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_URL="http://127.0.0.1:8000"

echo "================================================================="
echo "🛡️  LAUNCHING AQUANEX SOVEREIGN AI WORKBENCH"
echo "   Target Gateway: $TARGET_URL"
echo "================================================================="

cd "$ROOT_DIR"
exec python3 "$ROOT_DIR/scripts/run_linux_desktop.py" "$TARGET_URL" "$@"
