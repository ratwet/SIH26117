#!/usr/bin/env bash
# =====================================================================
# Aquanex — macOS Desktop Build Helper (scripts/build_macos.sh)
# Used by Anand on MacBook to compile the native Apple Silicon macOS app
# =====================================================================

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/frontend"

echo "================================================================="
echo "🍎  COMPILING AQUANEX NATIVE MACOS DESKTOP APP (.dmg / .app)"
echo "================================================================="

# 1. Install frontend dependencies
echo "📦 [1/2] Installing frontend dependencies..."
npm install

# 2. Build Tauri release bundle
echo "🔨 [2/2] Running Tauri release build..."
npm run tauri:build

echo "================================================================="
echo "🎉 Build Complete!"
echo "   Output DMG: frontend/src-tauri/target/release/bundle/dmg/"
echo "   Output App: frontend/src-tauri/target/release/bundle/macos/"
echo "================================================================="
