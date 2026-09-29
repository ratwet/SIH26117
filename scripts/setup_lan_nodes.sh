#!/usr/bin/env bash
# SovereignWorkbench - Minimalist Air-Gap Netplan Setup
set -euo pipefail

[ "${EUID:-$(id -u)}" -eq 0 ] || { echo "error: root privileges required (run with sudo)" >&2; exit 1; }
command -v netplan >/dev/null 2>&1 || { echo "error: netplan utility not found" >&2; exit 1; }

CHOICE="${1:-}"
if [ -z "$CHOICE" ]; then
  echo "Sovereign LAN Node Configurator:"
  echo "  1) Server Node (192.168.1.100)"
  echo "  2) Admin Node  (192.168.1.101)"
  echo "  3) User Client (192.168.1.102)"
  read -rp "Select node [1-3]: " CHOICE
fi

case "$CHOICE" in
  1) NAME="Server Node"; IP="192.168.1.100" ;;
  2) NAME="Admin Node";  IP="192.168.1.101" ;;
  3) NAME="User Client"; IP="192.168.1.102" ;;
  *) echo "Aborted."; exit 0 ;;
esac

IFACE="${2:-$(ip -o link show 2>/dev/null | awk -F': ' '$2 ~ /^(eth|en|enp|eno)/ {print $2; exit}')}"
IFACE="${IFACE:-eth0}"

CONFIG="/etc/netplan/01-sih-lan.yaml"
cat <<EOF > "$CONFIG"
network:
  version: 2
  renderer: networkd
  ethernets:
    ${IFACE}:
      addresses: [${IP}/24]
      routes: []
      nameservers:
        addresses: []
EOF
chmod 600 "$CONFIG"
netplan apply

echo "Configured: $NAME ($IP/24 on $IFACE) [Air-gap active: zero gateway]"
