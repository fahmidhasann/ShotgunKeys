"""
ShotgunKeys for Windows - Main Entry Point.
Orchestrates audio engine, global keyboard interceptor, dark-mode GUI, and system tray.
"""

import sys
import os
import argparse
import atexit

from config import config, get_custom_sounds_dir
from sound_engine import sound_engine
from key_listener import key_listener
from gui import MainWindow
from tray import TrayIcon

# Windows single-instance mutex
_mutex_handle = None

def acquire_single_instance_lock():
    """Ensures only a single instance of ShotgunKeys runs simultaneously on Windows."""
    global _mutex_handle
    if os.name == 'nt':
        try:
            import ctypes
            from ctypes import wintypes
            kernel32 = ctypes.windll.kernel32
            mutex_name = "Global\\ShotgunKeys_Windows_SingleInstance_Mutex"
            _mutex_handle = kernel32.CreateMutexW(None, True, mutex_name)
            ERROR_ALREADY_EXISTS = 183
            if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
                print("[Main] ShotgunKeys is already running in background.")
                sys.exit(0)
        except Exception as e:
            print(f"[Main] Mutex creation warning: {e}")

def main():
    parser = argparse.ArgumentParser(description="ShotgunKeys - Tactical Keyboard Sound Engine")
    parser.add_argument("--minimized", action="store_true", help="Start directly minimized to system tray")
    parser.add_argument("--mute", action="store_true", help="Start with audio muted")
    args = parser.parse_args()

    # Prevent multiple instances
    acquire_single_instance_lock()

    if args.mute:
        config.set("enabled", False)

    # Ensure custom_sounds directory exists with README
    get_custom_sounds_dir()

    print("==================================================")
    print("       💥 SHOTGUNKEYS FOR WINDOWS 💥             ")
    print("   Tactical Typing Sound & Mechanical Engine      ")
    print("==================================================")

    # 1. Initialize MainWindow and TrayIcon
    gui_window = None
    tray_icon = None

    def on_show_window():
        if gui_window:
            gui_window.root.after(0, gui_window.show)

    def on_tray_state_change():
        if gui_window:
            gui_window.root.after(0, gui_window.update_state_ui)

    def on_exit_app():
        print("[Main] Shutting down ShotgunKeys...")
        key_listener.stop()
        if tray_icon:
            tray_icon.stop()
        if gui_window:
            try:
                gui_window.root.destroy()
            except Exception:
                pass
        config.save()
        os._exit(0)

    # 2. Setup GUI
    gui_window = MainWindow(
        on_minimize_to_tray=lambda: None,
        on_exit=on_exit_app
    )

    # 3. Setup Tray Icon
    tray_icon = TrayIcon(
        on_show_window=on_show_window,
        on_exit=on_exit_app
    )
    tray_icon.start(on_state_change=on_tray_state_change)

    # 4. Connect key listener callback to GUI stats
    key_listener.register_callback(gui_window.on_key_action)
    key_listener.start()

    # Register clean shutdown
    atexit.register(key_listener.stop)
    atexit.register(config.save)

    # Initial window state
    if args.minimized or config.get("start_minimized", False):
        gui_window.hide_to_tray()
    else:
        gui_window.show()

    # 5. Run Tkinter main event loop
    try:
        gui_window.run_loop()
    except KeyboardInterrupt:
        on_exit_app()

if __name__ == "__main__":
    main()
