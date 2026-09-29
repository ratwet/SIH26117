#!/usr/bin/env python3
"""
Aquanex — Native Linux Desktop Client & Universal Launcher (scripts/run_linux_desktop.py)
Supports:
1. Native GTK 3.0 + WebKit2 Desktop Window
2. Three Persona Levels: Admin (Level 1), Senior (Level 2), Junior/Field (Level 3)
3. Zero-Crash Resilient Bootloader with Automatic Splash & Health Retry
4. Cross-Distro Fallback (Chromium/Chrome/Brave/Edge App Mode or System Browser)
"""

import sys
import os
import time
import urllib.request
import subprocess
import argparse
import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DEFAULT = "http://127.0.0.1:8000"

BOOTLOADER_SPLASH_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Aquanex Sovereign AI Workbench</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: #000000;
      color: #e2e8f0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      overflow: hidden;
      user-select: none;
    }
    .splash-card {
      background: #080808;
      border: 1px solid #1a1a1a;
      border-radius: 14px;
      padding: 40px 48px;
      max-width: 480px;
      width: 90%;
      text-align: center;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.9);
    }
    .logo-pulse {
      width: 72px;
      height: 72px;
      margin: 0 auto 20px;
      background: radial-gradient(circle, rgba(59, 130, 246, 0.2) 0%, rgba(15, 20, 32, 0) 70%);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 34px;
      animation: pulse 2s ease-in-out infinite;
    }
    @keyframes pulse {
      0%, 100% { transform: scale(1); filter: drop-shadow(0 0 8px rgba(59, 130, 246, 0.4)); }
      50% { transform: scale(1.08); filter: drop-shadow(0 0 20px rgba(59, 130, 246, 0.8)); }
    }
    h1 {
      font-size: 1.35rem;
      font-weight: 700;
      color: #f8fafc;
      letter-spacing: -0.02em;
      margin-bottom: 6px;
    }
    .badge {
      display: inline-block;
      font-size: 0.68rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      padding: 3px 10px;
      border-radius: 9999px;
      background: rgba(16, 185, 129, 0.12);
      border: 1px solid rgba(16, 185, 129, 0.3);
      color: #34d399;
      margin-bottom: 18px;
    }
    p {
      color: #94a3b8;
      font-size: 0.85rem;
      line-height: 1.5;
      margin-bottom: 24px;
    }
    .spinner-bar {
      width: 100%;
      height: 4px;
      background: #1e293b;
      border-radius: 9999px;
      overflow: hidden;
      margin-bottom: 20px;
      position: relative;
    }
    .spinner-bar::after {
      content: "";
      position: absolute;
      left: -40%;
      width: 40%;
      height: 100%;
      background: linear-gradient(90deg, #3b82f6, #60a5fa, #38bdf8);
      border-radius: 9999px;
      animation: loading 1.5s ease-in-out infinite;
    }
    @keyframes loading {
      0% { left: -40%; width: 30%; }
      50% { left: 30%; width: 50%; }
      100% { left: 100%; width: 30%; }
    }
    .status-text {
      font-size: 0.75rem;
      color: #64748b;
      font-family: monospace;
      margin-bottom: 16px;
    }
    .btn-retry {
      background: #1e293b;
      border: 1px solid #334155;
      color: #e2e8f0;
      padding: 8px 18px;
      font-size: 0.8rem;
      font-weight: 500;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    .btn-retry:hover {
      background: #3b82f6;
      border-color: #3b82f6;
      color: #ffffff;
    }
  </style>
  <script>
    const TARGET_URL = "%%TARGET_URL%%";
    let attempts = 0;

    async function checkBackend() {
      attempts++;
      const statusEl = document.getElementById("statusMsg");
      if (statusEl) {
        statusEl.textContent = "Connecting to air-gapped node (Attempt " + attempts + ")...";
      }

      try {
        const res = await fetch("http://127.0.0.1:8000/api/health", { method: "GET" });
        if (res.ok) {
          if (statusEl) statusEl.textContent = "Gateway connected! Loading workbench...";
          window.location.href = TARGET_URL;
          return;
        }
      } catch (err) {}

      setTimeout(checkBackend, 600);
    }

    window.addEventListener("DOMContentLoaded", () => {
      setTimeout(checkBackend, 400);
    });
  </script>
</head>
<body>
  <div class="splash-card">
    <div class="logo-pulse">🛡️</div>
    <h1>Aquanex Sovereign AI</h1>
    <div class="badge">Air-Gapped Sovereign Node</div>
    <p>Initializing local FastAPI gateway &amp; LangGraph state engine on 127.0.0.1:8000...</p>
    <div class="spinner-bar"></div>
    <div class="status-text" id="statusMsg">Booting backend runtime...</div>
    <button class="btn-retry" onclick="window.location.href=TARGET_URL">Connect Now</button>
  </div>
</body>
</html>
"""


def is_backend_alive(url: str = BACKEND_DEFAULT) -> bool:
    """Checks if the FastAPI backend gateway is responding."""
    try:
        base_url = url.split("?")[0].rstrip("/")
        with urllib.request.urlopen(f"{base_url}/api/health", timeout=1.2) as res:
            return res.status == 200
    except Exception:
        return False


def locate_uvicorn() -> str:
    """Locates uvicorn binary across virtualenvs and system paths."""
    candidates = [
        ROOT_DIR / ".venv" / "bin" / "uvicorn",
        Path.home() / "myenv" / "bin" / "uvicorn",
        Path.home() / ".local" / "bin" / "uvicorn",
        ROOT_DIR / "venv" / "bin" / "uvicorn",
    ]
    for c in candidates:
        if c.exists() and os.access(c, os.X_OK):
            return str(c)

    which_u = shutil.which("uvicorn")
    if which_u:
        return which_u

    return ""


def ensure_backend_running(url: str = BACKEND_DEFAULT):
    """If backend is not running, boots it via uvicorn/start_workbench.sh and waits."""
    if is_backend_alive(url):
        print(f"✅ Live backend gateway detected at: {url}")
        return

    print(f"⚠️  Backend not responding at {url}. Starting Sovereign FastAPI server...")
    backend_script = ROOT_DIR / "scripts" / "start_workbench.sh"

    uvicorn_bin = locate_uvicorn()
    env = {**os.environ, "PYTHONPATH": str(ROOT_DIR / "backend")}

    if backend_script.exists():
        subprocess.Popen(["bash", str(backend_script)], cwd=str(ROOT_DIR), env=env)
    elif uvicorn_bin:
        subprocess.Popen(
            [uvicorn_bin, "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd=str(ROOT_DIR / "backend"),
            env=env,
        )
    else:
        # Fallback to system python module
        subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd=str(ROOT_DIR / "backend"),
            env=env,
        )

    # Wait up to 20 seconds (40 iterations * 0.5s) for backend to become ready
    print("⏳ Waiting for backend gateway on 127.0.0.1:8000...", end="", flush=True)
    for _ in range(40):
        time.sleep(0.5)
        print(".", end="", flush=True)
        if is_backend_alive(url):
            print("\n✅ Backend gateway successfully booted and verified!")
            return

    print("\n⚠️  Continuing desktop launch in resilient bootloader mode.")


def open_in_standalone_browser(url: str, title: str):
    """
    Fallback for Linux distributions where GTK 3.0 / WebKit2 is not pre-installed.
    Uses Chromium, Google Chrome, Brave, Edge, or Firefox in standalone app-window mode.
    """
    print(f"🌐 Launching {title} via universal Linux browser app mode: {url}")

    browsers = [
        ["google-chrome", f"--app={url}", "--new-window"],
        ["chromium", f"--app={url}", "--new-window"],
        ["chromium-browser", f"--app={url}", "--new-window"],
        ["brave-browser", f"--app={url}", "--new-window"],
        ["microsoft-edge", f"--app={url}", "--new-window"],
        ["firefox", "--new-window", url],
    ]

    for b in browsers:
        if shutil.which(b[0]):
            try:
                subprocess.Popen(b)
                print(f"✅ Launched using {b[0]}")
                return
            except Exception as e:
                print(f"Could not launch {b[0]}: {e}")

    # Ultimate fallback
    import webbrowser
    webbrowser.open(url)


def run_gtk_webkit_app(target_url: str, title: str, wm_class: str, snapshot_path: str = None, quit_after_snapshot: bool = False, action: str = None):
    """Runs native GTK 3.0 + WebKit2 application window."""
    import gi
    gi.require_version('Gtk', '3.0')
    gi.require_version('WebKit2', '4.1')
    from gi.repository import Gtk, WebKit2, GdkPixbuf, GLib

    GLib.set_prgname(wm_class)
    GLib.set_application_name(title)

    class AquanexDesktopWindow(Gtk.Window):
        def __init__(self):
            super().__init__(title=title)
            self.snapshot_path = snapshot_path
            self.quit_after_snapshot = quit_after_snapshot
            self.action = action
            self.target_url = target_url

            self.set_default_size(1320, 860)
            self.set_position(Gtk.WindowPosition.CENTER)
            self.set_wmclass(wm_class, title)

            # Icon configuration
            icon_path = ROOT_DIR / "frontend" / "public" / "aquanex-logo.png"
            if not icon_path.exists():
                icon_path = ROOT_DIR / "frontend" / "src-tauri" / "icons" / "128x128.png"

            if icon_path.exists():
                try:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(icon_path))
                    self.set_icon(pixbuf)
                except Exception as e:
                    print(f"Could not load icon: {e}")

            # WebKit2 Settings
            self.settings = WebKit2.Settings()
            self.settings.set_enable_javascript(True)
            self.settings.set_enable_developer_extras(True)
            self.settings.set_enable_webgl(True)
            self.settings.set_hardware_acceleration_policy(WebKit2.HardwareAccelerationPolicy.ALWAYS)

            # Web View
            self.webview = WebKit2.WebView.new_with_settings(self.settings)
            self.webview.connect("load-changed", self.on_load_changed)
            self.webview.connect("load-failed", self.on_load_failed)

            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.add(self.webview)
            self.add(scrolled_window)

            print(f"🚀 Loading Aquanex native desktop UI: {self.target_url}")
            self.webview.load_uri(self.target_url)

            self.connect("destroy", Gtk.main_quit)

        def on_load_failed(self, webview, load_event, failing_uri, error):
            """Gracefully catches connection refused and shows bootloader splash screen."""
            print(f"ℹ️  Gateway initializing ({error.message}). Displaying splash screen...")
            splash_rendered = BOOTLOADER_SPLASH_HTML.replace("%%TARGET_URL%%", self.target_url)
            webview.load_html(splash_rendered, failing_uri)
            return True  # Suppress default WebKit error screen

        def on_load_changed(self, webview, event):
            if event == WebKit2.LoadEvent.FINISHED:
                uri = webview.get_uri() or ""
                if "127.0.0.1:8000" in uri:
                    print("✨ Aquanex Linux desktop client loaded successfully.")
                if self.action == "settings":
                    GLib.timeout_add(500, self.trigger_settings_action)
                elif self.action == "audit":
                    GLib.timeout_add(500, self.trigger_audit_action)
                elif self.action == "offline-chat":
                    GLib.timeout_add(800, self.trigger_offline_chat_action)
                elif self.action == "new-chat":
                    GLib.timeout_add(500, self.trigger_new_chat_action)
                elif self.snapshot_path:
                    GLib.timeout_add(1000, self.capture_snapshot)

        def trigger_new_chat_action(self):
            js = """
            const btn = document.getElementById('btnNewChat');
            if (btn) btn.click();
            """
            self.webview.run_javascript(js, None, None, None)
            if self.snapshot_path:
                GLib.timeout_add(1000, self.capture_snapshot)
            return False

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
            js = """
            const adm = document.getElementById('adminDashboardCanvas');
            if (adm) {
                adm.scrollTop = 550;
            } else {
                const p = document.getElementById('pillAudit');
                if (p) p.click();
            }
            """
            self.webview.run_javascript(js, None, None, None)
            if self.snapshot_path:
                GLib.timeout_add(1000, self.capture_snapshot)
            return False

        def trigger_offline_chat_action(self):
            js = """
            const ta = document.getElementById('chatTextarea');
            const btn = document.getElementById('btnChatSend');
            if (ta && btn) {
                ta.value = 'Check corrosion rate on line CDU-01';
                btn.disabled = false;
                btn.click();
            }
            """
            self.webview.run_javascript(js, None, None, None)
            if self.snapshot_path:
                GLib.timeout_add(3000, self.capture_snapshot)
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
            return False

    app = AquanexDesktopWindow()
    app.show_all()
    Gtk.main()


def main():
    parser = argparse.ArgumentParser(description="Aquanex Linux Desktop App Launcher")
    parser.add_argument("url", nargs="?", default=BACKEND_DEFAULT, help="Backend URL to connect to")
    parser.add_argument("--persona", choices=["admin", "senior", "junior", "field"], default=None, help="Refinery Persona / Access Level")
    parser.add_argument("--snapshot", dest="snapshot", default=None, help="Save screenshot to file path")
    parser.add_argument("--quit-after-snapshot", action="store_true", help="Close app after taking screenshot")
    parser.add_argument("--action", choices=["settings", "audit", "offline-chat", "new-chat"], default=None, help="Trigger UI action before capture")
    parser.add_argument("--browser", action="store_true", help="Force launch in standalone browser app mode")
    parser.add_argument("--demo", action="store_true", help="Launch in demo exhibition mode (bypass WAN lockdown)")
    args = parser.parse_args()

    # Determine persona configuration
    target_persona = args.persona.lower() if args.persona else None
    if target_persona == "field":
        target_persona = "junior"

    if target_persona == "admin":
        window_title = "Aquanex Admin — Sovereign Cluster Control Center"
        wm_class = "aquanex-admin"
    elif target_persona == "senior":
        window_title = "Aquanex Senior — Reliability Engineering Lead"
        wm_class = "aquanex-senior"
    elif target_persona == "junior":
        window_title = "Aquanex Field — Ultrasonic Inspection Assistant"
        wm_class = "aquanex-field"
    else:
        window_title = "Aquanex — Sovereign AI Workbench (MRPL PS 117)"
        wm_class = "aquanex"

    # Construct final target URL with persona and standalone query parameters
    target_url = args.url
    if target_persona:
        delim = "&" if "?" in target_url else "?"
        if f"persona={target_persona}" not in target_url:
            target_url = f"{target_url}{delim}persona={target_persona}&standalone=1"
        elif "standalone=" not in target_url:
            target_url = f"{target_url}&standalone=1"

    if args.demo or args.snapshot:
        delim = "&" if "?" in target_url else "?"
        target_url = f"{target_url}{delim}demo=1"

    print("=" * 68)
    print(f"🛡️  {window_title.upper()}")
    print("   Platform: Linux Universal Desktop Client")
    print(f"   Target Gateway: {target_url}")
    print("=" * 68)

    # Ensure backend is running before presenting window
    ensure_backend_running(target_url)

    # Check GTK / WebKit2 availability
    has_gtk_webkit = False
    if not args.browser:
        try:
            import gi
            gi.require_version('Gtk', '3.0')
            gi.require_version('WebKit2', '4.1')
            has_gtk_webkit = True
        except Exception:
            has_gtk_webkit = False

    if has_gtk_webkit and not args.browser:
        try:
            run_gtk_webkit_app(
                target_url=target_url,
                title=window_title,
                wm_class=wm_class,
                snapshot_path=args.snapshot,
                quit_after_snapshot=args.quit_after_snapshot,
                action=args.action
            )
            return
        except Exception as e:
            print(f"⚠️ Native WebKit error: {e}. Falling back to browser app mode.")

    # Cross-distro fallback
    open_in_standalone_browser(target_url, window_title)


if __name__ == "__main__":
    main()
