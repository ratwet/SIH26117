#!/usr/bin/env bash
# =====================================================================
# Aquanex - Universal Linux Desktop Integrator (scripts/install_linux_apps.sh)
# Installs Native Desktop Launchers for All 3 Levels:
#   1. Aquanex Admin (Level 1 - IT Systems Administrator)
#   2. Aquanex Senior (Level 2 - Senior Reliability Lead)
#   3. Aquanex Field (Level 3 - Field Inspection Operator)
# Compatible with all Linux distros (Ubuntu, Debian, Fedora, Arch, RHEL, openSUSE, etc.)
# =====================================================================

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APPS_DIR="$HOME/.local/share/applications"
ICONS_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"

echo "================================================================="
echo "🛡️  INSTALLING AQUANEX SOVEREIGN AI APPS FOR LINUX"
echo "   Target Root: $ROOT_DIR"
echo "   App Menu:    $APPS_DIR"
echo "================================================================="

mkdir -p "$APPS_DIR"

# 1. Application icon path
ICON_SRC="$ROOT_DIR/frontend/public/aquanex-logo.png"
if mkdir -p "$ICONS_DIR" 2>/dev/null; then
  if [ -f "$ICON_SRC" ]; then
    cp "$ICON_SRC" "$ICONS_DIR/aquanex.png" 2>/dev/null || true
  fi
fi

# Function to generate and install desktop entry with dynamic absolute paths
install_entry() {
  local filename="$1"
  local name="$2"
  local generic_name="$3"
  local comment="$4"
  local exec_script="$5"
  local wm_class="$6"
  local categories="$7"

  local target_path="$APPS_DIR/$filename"

  cat > "$target_path" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=$name
GenericName=$generic_name
Comment=$comment
Exec=$ROOT_DIR/scripts/$exec_script
Icon=$ICON_SRC
Terminal=false
Categories=$categories
Keywords=aquanex;sovereign;ai;mrpl;refinery;inspection;
StartupWMClass=$wm_class
StartupNotify=true
EOF

  chmod +x "$target_path"
  echo "✅ Installed: $name ($filename)"
}

# 2. Install Desktop Entries for all 3 Levels + Unified Portal
install_entry "aquanex-admin.desktop" \
  "Aquanex Admin" \
  "IT Systems & Model Governance (Level 1)" \
  "Aquanex Sovereign AI - IT Systems Administrator & Model Gatekeeper" \
  "launch_admin.sh" \
  "aquanex-admin" \
  "System;Development;Engineering;"

install_entry "aquanex-senior.desktop" \
  "Aquanex Senior" \
  "Reliability Engineering Lead (Level 2)" \
  "Aquanex Sovereign AI - Senior Reliability Lead with Model Switcher" \
  "launch_senior.sh" \
  "aquanex-senior" \
  "Development;Engineering;"

install_entry "aquanex-field.desktop" \
  "Aquanex Field" \
  "Ultrasonic Inspection Operator (Level 3)" \
  "Aquanex Sovereign AI - Pre-configured Field Inspection Operator" \
  "launch_junior.sh" \
  "aquanex-field" \
  "Development;Engineering;"

install_entry "aquanex.desktop" \
  "Aquanex Sovereign AI" \
  "Sovereign AI Inspection Workbench" \
  "Aquanex Sovereign On-Premise Agentic AI Workbench (MRPL PS 117)" \
  "launch_aquanex.sh" \
  "aquanex" \
  "Development;Engineering;"

# 3. Update XDG Desktop Database
if command -v update-desktop-database > /dev/null 2>&1; then
  update-desktop-database "$APPS_DIR" > /dev/null 2>&1 || true
  echo "✅ Updated XDG desktop database."
fi

# Ensure all scripts have executable permissions
chmod +x "$ROOT_DIR"/scripts/*.sh "$ROOT_DIR"/scripts/*.py

echo "================================================================="
echo "🎉 ALL 3 AQUANEX APPS ARE READY & INSTALLED IN YOUR LINUX APP MENU:"
echo "   1. 👑 Aquanex Admin   -> launch_admin.sh"
echo "   2. 📐 Aquanex Senior  -> launch_senior.sh"
echo "   3. 👷 Aquanex Field   -> launch_junior.sh"
echo "================================================================="
