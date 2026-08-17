"""
Global Low-Level Keyboard Hook for ShotgunKeys Windows.
Features:
- Windows Native `SetWindowsHookExW` (`WH_KEYBOARD_LL`) for ultra-low latency & anti-cheat safe background capture
- Automatic fallback to `pynput.keyboard` for cross-platform and non-admin scenarios
- Space / Enter reload handling with configurable toggles
- Key event callbacks for live UI counter updates
"""

import sys
import os
import threading
import time
from typing import Callable, List, Optional

from config import config
from sound_engine import sound_engine

# Virtual key codes on Windows
VK_SPACE = 0x20
VK_RETURN = 0x0D
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12  # Alt
VK_CAPITAL = 0x14
VK_ESCAPE = 0x1B

class KeyListener:
    """Manages global keyboard interception across all Windows apps and games."""

    def __init__(self):
        self.is_running = False
        self.hook_thread: Optional[threading.Thread] = None
        self.hook_id = None
        self.callbacks: List[Callable[[str], None]] = []
        
        # Debounce / repeat control
        self.last_key_time = 0.0
        self.min_key_interval = 0.025  # 25ms debounce to prevent mechanical chatter

    def register_callback(self, callback: Callable[[str], None]):
        """Register a callback for UI updates: callback('blast') or callback('reload')"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def unregister_callback(self, callback: Callable[[str], None]):
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def _notify_callbacks(self, action: str):
        for cb in self.callbacks:
            try:
                cb(action)
            except Exception:
                pass

    def start(self):
        """Starts the global keyboard hook in a background daemon thread."""
        if self.is_running:
            return
        self.is_running = True
        self.hook_thread = threading.Thread(target=self._run_hook, daemon=True, name="ShotgunKeysHookThread")
        self.hook_thread.start()
        print("[KeyListener] Global keyboard listener started.")

    def stop(self):
        """Stops the global keyboard hook."""
        self.is_running = False
        # If Windows native hook is active, post quit message
        if os.name == 'nt' and hasattr(self, '_win_thread_id'):
            try:
                import ctypes
                ctypes.windll.user32.PostThreadMessageW(self._win_thread_id, 0x0012, 0, 0) # WM_QUIT
            except Exception:
                pass
        print("[KeyListener] Global keyboard listener stopped.")

    def _handle_key_event(self, vk_code: int):
        """Processes a detected keydown event."""
        if not config.get("enabled", True):
            return

        now = time.time()
        if now - self.last_key_time < self.min_key_interval:
            return
        self.last_key_time = now

        reload_on_space = config.get("reload_on_space", True)
        reload_on_enter = config.get("reload_on_enter", True)

        # Space key
        if vk_code == VK_SPACE and reload_on_space:
            sound_engine.play_reload()
            self._notify_callbacks("reload")
            return

        # Enter / Return key
        if vk_code == VK_RETURN and reload_on_enter:
            sound_engine.play_reload()
            self._notify_callbacks("reload")
            return

        # Regular key -> Shotgun Blast
        sound_engine.play_blast()
        self._notify_callbacks("blast")

    def _run_hook(self):
        """Dispatches to native Windows WH_KEYBOARD_LL hook or pynput fallback."""
        if os.name == 'nt':
            try:
                self._run_windows_native_hook()
                return
            except Exception as e:
                print(f"[KeyListener] Native Windows hook failed: {e}. Falling back to pynput.")

        # Fallback to pynput
        self._run_pynput_hook()

    def _run_windows_native_hook(self):
        """High-performance Windows SetWindowsHookExW implementation."""
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        WH_KEYBOARD_LL = 13
        WM_KEYDOWN = 0x0100
        WM_SYSKEYDOWN = 0x0104

        # KBDLLHOOKSTRUCT definition
        class KBDLLHOOKSTRUCT(ctypes.Structure):
            _fields_ = [
                ("vkCode", wintypes.DWORD),
                ("scanCode", wintypes.DWORD),
                ("flags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.c_void_p)
            ]

        HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

        def low_level_keyboard_proc(nCode, wParam, lParam):
            if nCode >= 0:
                if wParam in (WM_KEYDOWN, WM_SYSKEYDOWN):
                    kbd = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                    vk = kbd.vkCode
                    self._handle_key_event(vk)
            return user32.CallNextHookEx(None, nCode, wParam, lParam)

        self._hook_callback = HOOKPROC(low_level_keyboard_proc)
        self._win_thread_id = kernel32.GetCurrentThreadId()

        h_instance = kernel32.GetModuleHandleW(None)
        self.hook_id = user32.SetWindowsHookExW(
            WH_KEYBOARD_LL,
            self._hook_callback,
            h_instance,
            0
        )

        if not self.hook_id:
            raise RuntimeError(f"SetWindowsHookExW failed with error code: {kernel32.GetLastError()}")

        print("[KeyListener] Native Windows WH_KEYBOARD_LL hook active.")

        # Windows Message pump
        msg = wintypes.MSG()
        while self.is_running:
            res = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if res <= 0:
                break
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        if self.hook_id:
            user32.UnhookWindowsHookEx(self.hook_id)
            self.hook_id = None
        print("[KeyListener] Native hook unhooked.")

    def _run_pynput_hook(self):
        """Cross-platform pynput keyboard hook fallback."""
        try:
            from pynput import keyboard

            def on_press(key):
                if not self.is_running:
                    return False

                vk = 0
                if key == keyboard.Key.space:
                    vk = VK_SPACE
                elif key == keyboard.Key.enter:
                    vk = VK_RETURN
                else:
                    vk = 0xFF # Generic key

                self._handle_key_event(vk)

            with keyboard.Listener(on_press=on_press) as listener:
                self._pynput_listener = listener
                while self.is_running:
                    time.sleep(0.1)
                listener.stop()
        except ImportError:
            print("[KeyListener] Warning: Neither Windows native hook nor pynput is available. Keyboard interception disabled.")
            while self.is_running:
                time.sleep(0.5)

# Global listener instance
key_listener = KeyListener()
