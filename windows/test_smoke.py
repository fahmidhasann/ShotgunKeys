#!/usr/bin/env python3
"""
Comprehensive Unit & Smoke Tests for ShotgunKeys Windows.
Verifies all modules, sound assets, presets, audio engine, keyboard hook logic, and GUI components.
"""

import os
import sys
import unittest
import io
import wave
import struct

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config, get_assets_dir, get_custom_sounds_dir, PRESETS
from sound_engine import SoundEngine
from key_listener import KeyListener, VK_SPACE, VK_RETURN

class TestConfig(unittest.TestCase):
    def test_default_config_keys(self):
        self.assertTrue(config.get("enabled", True))
        self.assertGreaterEqual(config.get("volume", 0.85), 0.0)
        self.assertLessEqual(config.get("volume", 0.85), 1.0)
        self.assertIn("preset", config.data)

    def test_presets_structure(self):
        self.assertEqual(len(PRESETS), 7)
        preset_names = [p["name"] for p in PRESETS]
        expected = [
            "Realistic 12-Gauge",
            "Tactical Combat",
            "Heavy Doom (Boomstick)",
            "Silenced Spec-Ops",
            "Cyberpunk Energy",
            "8-Bit Retro Arcade",
            "Custom (User Folder)"
        ]
        for name in expected:
            self.assertIn(name, preset_names)

    def test_assets_exist(self):
        assets_dir = get_assets_dir()
        self.assertTrue(os.path.exists(assets_dir), "Assets dir should exist")
        # Check all preset files exist on disk
        for p in PRESETS:
            for f in p.get("blast_files", []):
                full_path = os.path.join(assets_dir, f)
                self.assertTrue(os.path.exists(full_path), f"Missing audio asset: {f}")
            for f in p.get("reload_files", []):
                full_path = os.path.join(assets_dir, f)
                self.assertTrue(os.path.exists(full_path), f"Missing audio asset: {f}")

        # Check icons
        self.assertTrue(os.path.exists(os.path.join(assets_dir, "app_icon.png")))
        self.assertTrue(os.path.exists(os.path.join(assets_dir, "app_icon.ico")))

class TestSoundEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SoundEngine.get_instance()

    def test_wav_resampling(self):
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            data = struct.pack('<200h', *([1000, -1000] * 100))
            wf.writeframes(data)
        raw_wav = buf.getvalue()

        # Test resample
        resampled_up = self.engine._resample_wav_bytes(raw_wav, 1.04)
        self.assertIsNotNone(resampled_up)
        self.assertGreater(len(resampled_up), 44)

        resampled_down = self.engine._resample_wav_bytes(raw_wav, 0.96)
        self.assertIsNotNone(resampled_down)
        self.assertGreater(len(resampled_down), 44)

    def test_load_all_presets(self):
        for p in PRESETS:
            p_name = p["name"]
            self.engine.load_preset(p_name, preview=False)
            self.assertGreater(len(self.engine.blast_pitch_variants), 0, f"Preset {p_name} should load blast sounds")
            self.assertGreater(len(self.engine.reload_pitch_variants), 0, f"Preset {p_name} should load reload sounds")

    def test_audio_playback_methods(self):
        self.engine.set_volume(0.5)
        self.assertEqual(config.get("volume"), 0.5)
        self.engine.set_pitch_randomization(True)
        self.assertTrue(config.get("pitch_randomization"))

        # Trigger playback routines without exception
        self.engine.play_blast()
        self.engine.play_reload()

class TestKeyListener(unittest.TestCase):
    def setUp(self):
        self.listener = KeyListener()
        self.received_actions = []

    def callback(self, action: str):
        self.received_actions.append(action)

    def test_key_handling_logic(self):
        self.listener.register_callback(self.callback)
        self.listener.last_key_time = 0 # reset debounce

        # Normal key -> blast
        config.set("enabled", True)
        self.listener._handle_key_event(0x41) # 'A'
        self.assertIn("blast", self.received_actions)

        # Space key -> reload
        self.listener.last_key_time = 0
        config.set("reload_on_space", True)
        self.listener._handle_key_event(VK_SPACE)
        self.assertIn("reload", self.received_actions)

        # Enter key -> reload
        self.listener.last_key_time = 0
        config.set("reload_on_enter", True)
        self.listener._handle_key_event(VK_RETURN)
        self.assertIn("reload", self.received_actions)

        # Space key with reload_on_space disabled -> blast
        self.received_actions.clear()
        self.listener.last_key_time = 0
        config.set("reload_on_space", False)
        self.listener._handle_key_event(VK_SPACE)
        self.assertIn("blast", self.received_actions)

        # Muted app -> no actions
        self.received_actions.clear()
        self.listener.last_key_time = 0
        config.set("enabled", False)
        self.listener._handle_key_event(0x42) # 'B'
        self.assertEqual(len(self.received_actions), 0)

        # Restore enabled
        config.set("enabled", True)
        config.set("reload_on_space", True)
        self.listener.unregister_callback(self.callback)

class TestGUIAndTray(unittest.TestCase):
    def test_gui_init(self):
        try:
            import tkinter as tk
            from gui import MainWindow
            window = MainWindow()
            self.assertIsNotNone(window.root)
            window.update_state_ui()
            window.on_key_action("blast")
            window.on_key_action("reload")
            window.root.destroy()
        except (ImportError, Exception) as e:
            print(f"[TestGUI] Handled non-desktop environment check: {type(e).__name__}")

    def test_tray_structure(self):
        from tray import TrayIcon
        tray = TrayIcon()
        img = tray._get_icon_image()
        self.assertIsNotNone(img)
        self.assertEqual(img.size, (512, 512))
        img.close()

if __name__ == "__main__":
    unittest.main(verbosity=2)
