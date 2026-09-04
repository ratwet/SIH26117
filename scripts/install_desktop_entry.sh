#!/usr/bin/env bash
# =====================================================================
# Aquanex — Desktop Entry Installer (scripts/install_desktop_entry.sh)
# Registers Aquanex in Linux GNOME/KDE Application Drawer & Launcher
# =====================================================================

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="$HOME/.local/share/applications"
DESKTOP_SRC="$ROOT_DIR/aquanex.desktop"
DESKTOP_DEST="$APP_DIR/aquanex.desktop"
ICONS_DIR="$HOME/.icons"

echo "================================================================="
echo "🛡️  INSTALLING AQUANEX TO LINUX APP DRAWER"
echo "================================================================="

mkdir -p "$APP_DIR"
mkdir -p "$ICONS_DIR"

# Ensure execution rights on launchers
chmod +x "$ROOT_DIR/scripts/launch_aquanex.sh"
chmod +x "$ROOT_DIR/scripts/run_linux_desktop.py"

# Copy desktop entry and icon
cp "$DESKTOP_SRC" "$DESKTOP_DEST"
chmod +x "$DESKTOP_DEST"
cp "$ROOT_DIR/frontend/public/aquanex-logo.png" "$ICONS_DIR/aquanex.png"

# Validate desktop file
if command -v desktop-file-validate > /dev/null 2>&1; then
    desktop-file-validate "$DESKTOP_DEST"
    echo "✅ Desktop entry syntax validated successfully."
fi

# Refresh XDG desktop application database
if command -v update-desktop-database > /dev/null 2>&1; then
    update-desktop-database "$APP_DIR"
    echo "✅ System desktop database refreshed."
fi

echo "================================================================="
echo "🎉 Aquanex is now registered in your Linux App Drawer!"
echo "   - Search 'Aquanex' in GNOME / Super Key application launcher"
echo "   - Desktop file: $DESKTOP_DEST"
echo "   - Executable: $ROOT_DIR/scripts/launch_aquanex.sh"
echo "================================================================="
