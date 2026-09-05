#!/usr/bin/env bash
# =====================================================================
# Aquanex Field / Junior — Level 3 Desktop Launcher (scripts/launch_junior.sh)
# Launches Aquanex pre-authenticated as Naveen (Field Technician)
# Zero-configuration locked model interface for high-speed field operations
# =====================================================================

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_URL="${1:-http://127.0.0.1:8000}"

echo "================================================================="
echo "👷 LAUNCHING AQUANEX FIELD — LEVEL 3 INSPECTION OPERATOR CLIENT"
echo "   Personnel: Naveen (Field Technician • PIN 2026)"
echo "   Interface: Pre-configured Locked Inspection Model (Edge-8B)"
echo "   Target Gateway: $TARGET_URL"
echo "================================================================="

cd "$ROOT_DIR"
exec python3 "$ROOT_DIR/scripts/run_linux_desktop.py" "$TARGET_URL" --persona junior "$@"
