"""
System Tray Integration for ShotgunKeys Windows using pystray.
Allows background execution with quick-access popup menu.
"""

import os
import sys
import threading
from typing import Callable, Optional
from PIL import Image

PYSTRAY_AVAILABLE = False
try:
    import pystray
    from pystray import MenuItem as item, Menu
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False

from config import config, get_assets_dir, get_custom_sounds_dir, PRESETS
from sound_engine import sound_engine

class TrayIcon:
    """Manages the Windows taskbar notification area (System Tray) icon."""

    def __init__(self, on_show_window: Optional[Callable[[], None]] = None, on_exit: Optional[Callable[[], None]] = None):
        self.on_show_window = on_show_window
        self.on_exit = on_exit
        self.icon: Optional[Any] = None
        self.tray_thread: Optional[threading.Thread] = None

    def _get_icon_image(self) -> Image.Image:
        """Loads app icon PNG or creates a dynamic fallback icon."""
        png_path = os.path.join(get_assets_dir(), "app_icon.png")
        if os.path.exists(png_path):
            try:
                return Image.open(png_path)
            except Exception:
                pass

        # Fallback colored square
        img = Image.new('RGBA', (64, 64), (255, 140, 20, 255))
        return img

    def _toggle_enabled(self, icon, item):
        is_enabled = not config.get("enabled", True)
        config.set("enabled", is_enabled)
        if hasattr(self, 'on_state_change') and self.on_state_change:
            self.on_state_change()

    def _set_preset(self, preset_name: str):
        def handler(icon, item):
            sound_engine.load_preset(preset_name, preview=True)
            if hasattr(self, 'on_state_change') and self.on_state_change:
                self.on_state_change()
        return handler

    def _is_preset_active(self, preset_name: str):
        def handler(item):
            return config.get("preset", "Realistic 12-Gauge") == preset_name
        return handler

    def _open_custom_folder(self, icon, item):
        custom_dir = get_custom_sounds_dir()
        if os.name == 'nt':
            os.startfile(custom_dir)
        elif sys.platform == 'darwin':
            import subprocess
            subprocess.Popen(['open', custom_dir])
        else:
            import subprocess
            subprocess.Popen(['xdg-open', custom_dir])

    def _reload_audio(self, icon, item):
        sound_engine.load_preset(config.get("preset", "Realistic 12-Gauge"), preview=True)

    def _show_gui(self, icon, item):
        if self.on_show_window:
            self.on_show_window()

    def _exit_app(self, icon, item):
        if self.icon:
            self.icon.stop()
        if self.on_exit:
            self.on_exit()
        else:
            os._exit(0)

    def start(self, on_state_change: Optional[Callable[[], None]] = None):
        """Starts the system tray icon in a separate thread."""
        self.on_state_change = on_state_change
        if not PYSTRAY_AVAILABLE:
            print("[TrayIcon] pystray is not installed. System tray icon disabled.")
            return

        image = self._get_icon_image()

        # Build Presets Submenu
        preset_items = []
        for p in PRESETS:
            p_name = p["name"]
            p_icon = p["icon"]
            preset_items.append(
                item(
                    f"{p_icon} {p_name}",
                    self._set_preset(p_name),
                    checked=self._is_preset_active(p_name),
                    radio=True
                )
            )

        menu = Menu(
            item("🎚 Open ShotgunKeys", self._show_gui, default=True),
            item(
                "🔊 Sound Enabled",
                self._toggle_enabled,
                checked=lambda item: config.get("enabled", True)
            ),
            Menu.SEPARATOR,
            item("🎛 Sound Profiles", Menu(*preset_items)),
            item("📁 Custom Sounds Folder", self._open_custom_folder),
            item("🔄 Reload Audio Files", self._reload_audio),
            Menu.SEPARATOR,
            item("🚪 Exit", self._exit_app)
        )

        self.icon = pystray.Icon("ShotgunKeys", image, "ShotgunKeys - Typing Sound Engine", menu)

        def run_tray():
            try:
                self.icon.run()
            except Exception as e:
                print(f"[TrayIcon] Tray loop error: {e}")

        self.tray_thread = threading.Thread(target=run_tray, daemon=True, name="ShotgunKeysTrayThread")
        self.tray_thread.start()
        print("[TrayIcon] System tray initialized.")

    def stop(self):
        if self.icon:
            try:
                self.icon.stop()
            except Exception:
                pass
            self.icon = None

    def notify(self, title: str, message: str):
        """Sends a desktop balloon notification via tray icon."""
        if self.icon and hasattr(self.icon, 'notify'):
            try:
                self.icon.notify(message, title)
            except Exception:
                pass
