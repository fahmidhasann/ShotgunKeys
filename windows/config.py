"""
Configuration management for ShotgunKeys Windows.
Handles JSON persistence of user settings and statistics.
"""

import os
import json
import sys
from typing import Dict, Any

DEFAULT_CONFIG: Dict[str, Any] = {
    "enabled": True,
    "volume": 0.85,
    "preset": "Realistic 12-Gauge",
    "pitch_randomization": True,
    "reload_on_space": True,
    "reload_on_enter": True,
    "start_minimized": False,
    "minimize_to_tray": True,
    "total_shots_fired": 0,
    "total_reloads": 0,
}

PRESETS = [
    {
        "id": "realistic",
        "name": "Realistic 12-Gauge",
        "icon": "💥",
        "description": "Authentic live-recorded 12-gauge field blasts and heavy pump action",
        "blast_files": ["shotgun_blast_1.wav", "shotgun_blast_2.wav", "shotgun_blast_3.wav", "shotgun_blast_4.wav"],
        "reload_files": ["shotgun_reload_1.wav", "shotgun_reload_2.wav", "real_shotgun_reload.wav"]
    },
    {
        "id": "tactical",
        "name": "Tactical Combat",
        "icon": "🎯",
        "description": "Crisp & snappy military combat shotgun firing and tactical breach reload",
        "blast_files": ["tactical_blast_1.wav", "tactical_blast_2.wav", "tactical_blast_3.wav"],
        "reload_files": ["tactical_reload_1.wav", "tactical_reload_2.wav"]
    },
    {
        "id": "doom",
        "name": "Heavy Doom (Boomstick)",
        "icon": "⚡",
        "description": "Massive sub-bass double-barrel super shotgun thunder with metallic rack",
        "blast_files": ["doom_blast_1.wav", "doom_blast_2.wav"],
        "reload_files": ["doom_reload_1.wav", "doom_reload_2.wav"]
    },
    {
        "id": "silenced",
        "name": "Silenced Spec-Ops",
        "icon": "🤫",
        "description": "Suppressed covert tactical puff and lubricated smooth slide",
        "blast_files": ["silenced_blast_1.wav", "silenced_blast_2.wav"],
        "reload_files": ["silenced_reload_1.wav", "silenced_reload_2.wav"]
    },
    {
        "id": "cyberpunk",
        "name": "Cyberpunk Energy",
        "icon": "🔮",
        "description": "High-energy futuristic plasma shotgun discharge with servo cycle",
        "blast_files": ["cyber_blast_1.wav", "cyber_blast_2.wav"],
        "reload_files": ["cyber_reload_1.wav", "cyber_reload_2.wav"]
    },
    {
        "id": "arcade",
        "name": "8-Bit Retro Arcade",
        "icon": "🕹️",
        "description": "Punchy 8-bit retro arcade synth blast and chiptune power-reload",
        "blast_files": ["arcade_blast.wav"],
        "reload_files": ["arcade_reload.wav"]
    },
    {
        "id": "custom",
        "name": "Custom (User Folder)",
        "icon": "📁",
        "description": "Load your own WAV/MP3 sound effects dropped in the custom_sounds/ folder",
        "blast_files": [],
        "reload_files": []
    }
]

def get_base_dir() -> str:
    """Get root directory whether running as script or PyInstaller frozen bundle."""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS  # type: ignore
    return os.path.dirname(os.path.abspath(__file__))

def get_app_data_dir() -> str:
    """Get persistent AppData directory on Windows or fallback on other OS."""
    if os.name == 'nt':
        app_data = os.environ.get('APPDATA')
        if app_data:
            target_dir = os.path.join(app_data, 'ShotgunKeys')
            os.makedirs(target_dir, exist_ok=True)
            return target_dir
    # Fallback to user home directory or local directory
    target_dir = os.path.join(os.path.expanduser('~'), '.shotgunkeys')
    os.makedirs(target_dir, exist_ok=True)
    return target_dir

def get_custom_sounds_dir() -> str:
    """Get custom sounds directory next to executable or script."""
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        custom_dir = os.path.join(exe_dir, "custom_sounds")
    else:
        custom_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "custom_sounds")
    os.makedirs(custom_dir, exist_ok=True)
    return custom_dir

def get_assets_dir() -> str:
    """Get assets directory containing WAV audio files and icons."""
    base = get_base_dir()
    assets_dir = os.path.join(base, "assets")
    if not os.path.exists(assets_dir):
        # Fallback to script folder
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    return assets_dir

class ConfigManager:
    """Manages application state and JSON configuration file."""
    def __init__(self):
        self.config_path = os.path.join(get_app_data_dir(), "config.json")
        self.data: Dict[str, Any] = dict(DEFAULT_CONFIG)
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.data.update(saved)
            except Exception as e:
                print(f"[Config] Error loading config: {e}")

    def save(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"[Config] Error saving config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any, auto_save: bool = True):
        self.data[key] = value
        if auto_save:
            self.save()

    def increment(self, key: str, amount: int = 1):
        self.data[key] = self.data.get(key, 0) + amount
        # Periodic or explicit save

# Global config instance
config = ConfigManager()
