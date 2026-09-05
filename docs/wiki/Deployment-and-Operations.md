# 🚀 Deployment & Operations Guide

This guide provides step-by-step instructions for deploying Aquanex in a production refinery environment, configuring the offline 3-node physical LAN topology, and launching the native Linux desktop client.

---

## 🛠️ System Prerequisites

| Component | Minimum Specification | Recommended Production |
| :--- | :--- | :--- |
| **Operating System** | Linux (Ubuntu 22.04 LTS, Fedora 39+, RHEL 9+) | Ubuntu 24.04 LTS / RHEL 9.3 |
| **Python** | Python 3.10+ | Python 3.11 or 3.12 |
| **Node.js** | Node.js v18 LTS with npm | Node.js v20 LTS |
| **Linux Sandboxing** | `bubblewrap` package installed (`/usr/bin/bwrap`) | `bubblewrap` v0.8.0+ |
| **Desktop Shell** | `gir1.2-webkit2-4.1` and `gir1.2-gtk-3.0` | GNOME 45+ or KDE Plasma 6 |
| **Hardware Node 1 (Server)**| 8-Core CPU, 32GB RAM, RTX 3090 / 4090 (24GB VRAM) | Dual A100 / RTX 6000 Ada (48GB) |
| **Hardware Node 2 (Admin)** | 4-Core CPU, 8GB RAM | Any standard Linux laptop |
| **Hardware Node 3 (Client)**| 4-Core CPU, 8GB RAM | Any standard Linux workstation |

---

## 📦 Step-by-Step Installation

### 1. Clone Repository & Setup Virtual Environment
```bash
# Clone the repository
git clone https://github.com/ratwet/SIH26117.git
cd SIH26117

# Create and activate Python virtual environment
python3 -m venv myenv
source myenv/bin/activate

# Install all pinned backend requirements
pip install -r backend/requirements.txt
```

### 2. Build the Desktop Frontend
```bash
cd frontend
npm install
npm run build
cd ..
```

---

## 🖥️ Launching the Native Linux Desktop Client

Aquanex provides a native, hardware-accelerated Linux desktop client powered by GTK 3.0 and WebKit2:

```bash
# Option 1: Install to Linux App Drawer (GNOME / KDE)
bash scripts/install_desktop_entry.sh

# Option 2: Launch directly via automated script
bash scripts/launch_aquanex.sh

# Option 3: Run standalone GTK WebKit2 runner
python3 scripts/run_linux_desktop.py
```

---

## 🏛️ Physical 3-Node Offline LAN Network Configuration

To configure the isolated, air-gapped 3-node LAN subnet (`192.168.1.0/24`) without an external Internet gateway, run [`scripts/setup_lan_nodes.sh`](scripts/setup_lan_nodes.sh):

```bash
# On Server Node (192.168.1.100)
sudo bash scripts/setup_lan_nodes.sh server

# On Admin Node (192.168.1.101)
sudo bash scripts/setup_lan_nodes.sh admin

# On User Workbench Node (192.168.1.102)
sudo bash scripts/setup_lan_nodes.sh user
```

### Netplan Configuration Sample (`/etc/netplan/01-sih-lan.yaml`):
```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      addresses:
        - 192.168.1.100/24
      routes: []     # Strictly empty = No default route / No WAN
      nameservers:
        addresses: [] # Strictly empty = No public DNS
```

---

## 🛡️ Sovereignty Verification: Zero-Egress Proof

To provide undeniable proof to evaluators and cyber auditors that zero packets escape the air-gapped workstation:

```bash
# Launch the live network packet sniffer
sudo bash scripts/verify_sovereignty.sh
```

The script monitors all interfaces via `tcpdump` and verifies that **0 bytes of WAN traffic** occur during end-to-end model inference, document parsing, and file generation.
