#!/usr/bin/env python3
"""
SovereignWorkbench — Native Linux Desktop Client (scripts/run_linux_desktop.py)
Owned by Naveen (Dev 4: Frontend & Desktop Lead).

Launches the native Linux desktop application window for Aquanex using 
Linux GTK 3.0 and WebKit2 runtime, directly connected to the tested backend gateway.
Supports on-demand screenshot capture and headless validation.
"""

import sys
import os
import time
import urllib.request
import subprocess
import argparse
from pathlib import Path

# Ensure GTK 3.0 and WebKit2 4.1 introspection
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.1')
from gi.repository import Gtk, WebKit2, GdkPixbuf, GLib

BACKEND_DEFAULT = "http://127.0.0.1:8000"
ROOT_DIR = Path(__file__).resolve().parent.parent


def is_backend_alive(url: str) -> bool:
    try:
        with urllib.request.urlopen(f"{url}/api/health", timeout=1.5) as res:
            return res.status == 200
    except Exception:
        return False


def ensure_backend_running(url: str):
    """If backend is not running, launches it in the background."""
    if is_backend_alive(url):
        print(f"✅ Live backend gateway detected at: {url}")
        return

    print(f"⚠️  Backend not responding at {url}. Starting background FastAPI server...")
    backend_script = ROOT_DIR / "scripts" / "start_workbench.sh"
    if backend_script.exists():
        subprocess.Popen(["bash", str(backend_script)], cwd=str(ROOT_DIR))
    else:
        python_bin = sys.executable
        subprocess.Popen(
            [python_bin, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd=str(ROOT_DIR / "backend"),
            env={**os.environ, "PYTHONPATH": "backend"}
        )

    for _ in range(12):
        time.sleep(0.5)
        if is_backend_alive(url):
            print(f"✅ Backend gateway successfully booted and verified.")
            return

    print("⚠️  Continuing desktop launch in offline standalone mode.")


class AquanexDesktopWindow(Gtk.Window):
    def __init__(self, target_url: str, snapshot_path: str = None, quit_after_snapshot: bool = False, action: str = None):
        super().__init__(title="Aquanex — SovereignWorkbench (MRPL PS 117)")
        
        self.snapshot_path = snapshot_path
        self.quit_after_snapshot = quit_after_snapshot
        self.action = action

        # Window configuration matching tauri.conf.json
        self.set_default_size(1320, 860)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_wmclass("aquanex", "Aquanex")

        # Set Window Icon
        icon_path = ROOT_DIR / "frontend" / "public" / "aquanex-logo.png"
        if not icon_path.exists():
            icon_path = ROOT_DIR / "frontend" / "src-tauri" / "icons" / "128x128.png"
            
        if icon_path.exists():
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(icon_path))
                self.set_icon(pixbuf)
            except Exception as e:
                print(f"Could not load icon: {e}")

        # WebKit2 Web View Configuration
        self.settings = WebKit2.Settings()
        self.settings.set_enable_javascript(True)
        self.settings.set_enable_developer_extras(True)
        self.settings.set_enable_webgl(True)
        self.settings.set_hardware_acceleration_policy(WebKit2.HardwareAccelerationPolicy.ALWAYS)

        # Create WebKit2 Web View
        self.webview = WebKit2.WebView.new_with_settings(self.settings)
        self.webview.connect("load-changed", self.on_load_changed)

        # Scroll window container
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(self.webview)
        self.add(scrolled_window)

        # Load target URL
        print(f"🚀 Loading Aquanex native desktop UI from: {target_url}")
        self.webview.load_uri(target_url)

        self.connect("destroy", Gtk.main_quit)

    def on_load_changed(self, webview, event):
        if event == WebKit2.LoadEvent.FINISHED:
            print("✨ Aquanex Linux desktop client loaded successfully.")
            if self.action == "settings":
                GLib.timeout_add(500, self.trigger_settings_action)
            elif self.action == "audit":
                GLib.timeout_add(500, self.trigger_audit_action)
            elif self.snapshot_path:
                GLib.timeout_add(1000, self.capture_snapshot)

    def trigger_settings_action(self):
        js = """
        document.getElementById('btnCustomize').click();
        setTimeout(() => {
            const btn = document.getElementById('btnTestBackendConn');
            if (btn) btn.click();
        }, 300);
        """
        self.webview.run_javascript(js, None, None, None)
        if self.snapshot_path:
            GLib.timeout_add(1200, self.capture_snapshot)
        return False

    def trigger_audit_action(self):
        js = "document.getElementById('pillAudit').click();"
        self.webview.run_javascript(js, None, None, None)
        if self.snapshot_path:
            GLib.timeout_add(6200, self.capture_snapshot)
        return False

    def capture_snapshot(self):
        def snapshot_callback(view, result):
            try:
                surface = view.get_snapshot_finish(result)
                surface.write_to_png(self.snapshot_path)
                print(f"📸 Native Linux App Screenshot saved to: {self.snapshot_path}")
            except Exception as e:
                print(f"Snapshot error: {e}")
            
            if self.quit_after_snapshot:
                Gtk.main_quit()

        self.webview.get_snapshot(
            WebKit2.SnapshotRegion.FULL_DOCUMENT,
            WebKit2.SnapshotOptions.NONE,
            None,
            snapshot_callback
        )
        return False  # Don't repeat timer


def main():
    parser = argparse.ArgumentParser(description="Aquanex Linux Desktop App Launcher")
    parser.add_argument("url", nargs="?", default=BACKEND_DEFAULT, help="Backend URL to connect to")
    parser.add_argument("--snapshot", dest="snapshot", default=None, help="Save screenshot to file path")
    parser.add_argument("--quit-after-snapshot", action="store_true", help="Close app after taking screenshot")
    parser.add_argument("--action", choices=["settings", "audit"], default=None, help="Trigger UI action before capture")
    args = parser.parse_args()

    print("=" * 65)
    print("🛡️  AQUANEX SOVEREIGNWORKBENCH — NATIVE LINUX DESKTOP CLIENT")
    print("   Platform: Linux (GTK 3.0 + WebKit2 Engine)")
    print(f"   Target Gateway: {args.url}")
    print("=" * 65)

    GLib.set_prgname("aquanex")
    GLib.set_application_name("Aquanex")

    ensure_backend_running(args.url)

    app = AquanexDesktopWindow(
        target_url=args.url,
        snapshot_path=args.snapshot,
        quit_after_snapshot=args.quit_after_snapshot,
        action=args.action
    )
    app.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
