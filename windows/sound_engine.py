"""
High-Performance Audio Engine for ShotgunKeys Windows.
Features:
- Multi-voice polyphonic playback (32 channels)
- Pre-initialized low-latency buffer (512 samples @ 44.1kHz 16-bit)
- Pitch and volume micro-randomization for dynamic realism
- Support for all built-in sound presets + user custom audio folder
- Thread-safe non-blocking audio dispatch
- Graceful mock audio mode if audio hardware or pygame is unavailable
"""

import os
import glob
import random
import threading
import io
import wave
import struct
from typing import List, Dict, Optional, Any

# Attempt pygame mixer import with fallback
PYGAME_AVAILABLE = False
try:
    import pygame
    import pygame.mixer
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

from config import config, get_assets_dir, get_custom_sounds_dir, PRESETS

class MockSound:
    """Mock sound object for headless or non-pygame environments."""
    def __init__(self, source: Any = None):
        self.source = source
        self.volume = 1.0

    def set_volume(self, vol: float):
        self.volume = vol

    def play(self):
        pass

class MockChannel:
    def play(self, sound: Any):
        pass

class SoundEngine:
    """Manages audio playback, polyphonic mixing, and sound preset loading."""

    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def __init__(self):
        self.initialized = False
        self.volume: float = float(config.get("volume", 0.85))
        self.pitch_randomization: bool = bool(config.get("pitch_randomization", True))
        self.current_preset: str = str(config.get("preset", "Realistic 12-Gauge"))
        
        # Pitch variant pools: List of lists containing Sound/MockSound objects
        self.blast_pitch_variants: List[List[Any]] = []
        self.reload_pitch_variants: List[List[Any]] = []

        self.last_played_blast_idx = -1
        self.last_played_reload_idx = -1

        self.audio_thread_lock = threading.Lock()
        self._init_audio_subsystem()
        self.load_preset(self.current_preset, preview=False)

    def _init_audio_subsystem(self):
        """Pre-initializes the mixer with low latency settings."""
        if not PYGAME_AVAILABLE:
            print("[SoundEngine] Pygame is not installed. Running in mock audio mode.")
            self.initialized = True  # Allow mock loading
            return

        try:
            # Low latency configuration: 44.1kHz, 16-bit signed stereo, 512 buffer
            if not pygame.mixer.get_init():
                pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
                pygame.mixer.init()
            pygame.mixer.set_num_channels(32)
            self.initialized = True
            print("[SoundEngine] Pygame mixer initialized successfully with 32 channels.")
        except Exception as e:
            print(f"[SoundEngine] Error initializing pygame.mixer: {e}. Trying fallback buffer.")
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
                pygame.mixer.set_num_channels(32)
                self.initialized = True
            except Exception as e2:
                print(f"[SoundEngine] Audio init warning: {e2}. Falling back to mock sound mode.")
                self.initialized = True

    def _resample_wav_bytes(self, wav_bytes: bytes, pitch_ratio: float) -> Optional[bytes]:
        """
        Resamples a 16-bit PCM WAV in memory to simulate pitch/rate shift.
        pitch_ratio: >1.0 = higher pitch (faster), <1.0 = lower pitch (slower)
        """
        try:
            with wave.open(io.BytesIO(wav_bytes), 'rb') as wf:
                params = wf.getparams()
                nchannels, sampwidth, framerate, nframes = params[:4]
                if sampwidth != 2:
                    return wav_bytes
                frames = wf.readframes(nframes)

            total_samples = nframes * nchannels
            fmt = f"<{total_samples}h"
            samples = struct.unpack(fmt, frames)

            new_nframes = int(nframes / pitch_ratio)
            new_samples = []
            
            for i in range(new_nframes):
                orig_pos = i * pitch_ratio
                idx = int(orig_pos)
                frac = orig_pos - idx
                
                for ch in range(nchannels):
                    sample_idx = idx * nchannels + ch
                    if sample_idx + nchannels < len(samples):
                        s1 = samples[sample_idx]
                        s2 = samples[sample_idx + nchannels]
                        interpolated = int(s1 + frac * (s2 - s1))
                        interpolated = max(-32768, min(32767, interpolated))
                        new_samples.append(interpolated)
                    elif sample_idx < len(samples):
                        new_samples.append(samples[sample_idx])
                    else:
                        new_samples.append(0)

            out_fmt = f"<{len(new_samples)}h"
            out_raw = struct.pack(out_fmt, *new_samples)

            out_buf = io.BytesIO()
            with wave.open(out_buf, 'wb') as out_wf:
                out_wf.setnchannels(nchannels)
                out_wf.setsampwidth(sampwidth)
                out_wf.setframerate(framerate)
                out_wf.writeframes(out_raw)
            return out_buf.getvalue()
        except Exception:
            return wav_bytes

    def _load_sound_file_with_variants(self, filepath: str) -> List[Any]:
        """Loads a WAV file and pre-generates micro-pitch variants for instant zero-latency playback."""
        variants = []
        if not os.path.exists(filepath):
            return variants

        # If pygame is not available or mixer not initialized, create mock sounds
        if not PYGAME_AVAILABLE or not pygame.mixer.get_init():
            base_sound = MockSound(filepath)
            base_sound.set_volume(self.volume)
            variants.append(base_sound)
            # Add mock variants
            for _ in range(4):
                var = MockSound(filepath)
                var.set_volume(self.volume)
                variants.append(var)
            return variants

        try:
            base_sound = pygame.mixer.Sound(filepath)
            base_sound.set_volume(self.volume)
            variants.append(base_sound)

            if filepath.lower().endswith('.wav'):
                with open(filepath, 'rb') as f:
                    wav_data = f.read()

                pitch_ratios = [0.96, 0.98, 1.02, 1.04]
                for ratio in pitch_ratios:
                    mod_bytes = self._resample_wav_bytes(wav_data, ratio)
                    if mod_bytes:
                        try:
                            mod_sound = pygame.mixer.Sound(io.BytesIO(mod_bytes))
                            mod_sound.set_volume(self.volume)
                            variants.append(mod_sound)
                        except Exception:
                            pass
        except Exception as e:
            print(f"[SoundEngine] Failed to load audio file {filepath}: {e}")
            variants.append(MockSound(filepath))

        return variants if variants else [MockSound(filepath)]

    def set_volume(self, vol: float):
        """Sets master playback volume (0.0 - 1.0)."""
        self.volume = max(0.0, min(1.0, float(vol)))
        config.set("volume", self.volume)

        with self.audio_thread_lock:
            for variant_group in self.blast_pitch_variants:
                for sound in variant_group:
                    try:
                        sound.set_volume(self.volume)
                    except Exception:
                        pass
            for variant_group in self.reload_pitch_variants:
                for sound in variant_group:
                    try:
                        sound.set_volume(self.volume)
                    except Exception:
                        pass

    def set_pitch_randomization(self, enabled: bool):
        """Toggle dynamic pitch randomization."""
        self.pitch_randomization = bool(enabled)
        config.set("pitch_randomization", self.pitch_randomization)

    def load_preset(self, preset_name: str, preview: bool = False):
        """Loads sound effects for the given preset name."""
        self.current_preset = preset_name
        config.set("preset", preset_name)
        assets_dir = get_assets_dir()
        custom_dir = get_custom_sounds_dir()

        with self.audio_thread_lock:
            self.blast_pitch_variants.clear()
            self.reload_pitch_variants.clear()

            if preset_name == "Custom (User Folder)":
                self._load_custom_folder(custom_dir, assets_dir)
            else:
                preset_info = next((p for p in PRESETS if p["name"] == preset_name), None)
                if not preset_info:
                    preset_info = PRESETS[0]

                blast_files = preset_info.get("blast_files", [])
                reload_files = preset_info.get("reload_files", [])

                for fname in blast_files:
                    path = os.path.join(assets_dir, fname)
                    if os.path.exists(path):
                        vars = self._load_sound_file_with_variants(path)
                        if vars:
                            self.blast_pitch_variants.append(vars)

                for fname in reload_files:
                    path = os.path.join(assets_dir, fname)
                    if os.path.exists(path):
                        vars = self._load_sound_file_with_variants(path)
                        if vars:
                            self.reload_pitch_variants.append(vars)

        print(f"[SoundEngine] Loaded preset '{preset_name}' ({len(self.blast_pitch_variants)} blast types, {len(self.reload_pitch_variants)} reload types)")

        if preview and config.get("enabled", True):
            threading.Timer(0.05, self.play_blast).start()

    def _load_custom_folder(self, custom_dir: str, fallback_assets_dir: str):
        """Scans custom_sounds/ directory for blast and reload audio files."""
        supported_exts = ("*.wav", "*.mp3", "*.ogg", "*.flac")
        all_files = []
        for ext in supported_exts:
            all_files.extend(glob.glob(os.path.join(custom_dir, ext)))
            all_files.extend(glob.glob(os.path.join(custom_dir, ext.upper())))

        blast_found = []
        reload_found = []

        for fpath in all_files:
            fname = os.path.basename(fpath).lower()
            if any(k in fname for k in ["blast", "shot", "fire", "gun", "boom", "bang"]):
                blast_found.append(fpath)
            elif any(k in fname for k in ["reload", "pump", "cock", "action", "rack", "slide"]):
                reload_found.append(fpath)
            else:
                blast_found.append(fpath)

        for path in blast_found:
            vars = self._load_sound_file_with_variants(path)
            if vars:
                self.blast_pitch_variants.append(vars)

        for path in reload_found:
            vars = self._load_sound_file_with_variants(path)
            if vars:
                self.reload_pitch_variants.append(vars)

        # If custom folder is empty, fallback to Realistic 12-Gauge
        if not self.blast_pitch_variants:
            for fname in ["shotgun_blast_1.wav", "shotgun_blast_2.wav", "shotgun_blast_3.wav", "shotgun_blast_4.wav"]:
                path = os.path.join(fallback_assets_dir, fname)
                if os.path.exists(path):
                    vars = self._load_sound_file_with_variants(path)
                    if vars:
                        self.blast_pitch_variants.append(vars)

        if not self.reload_pitch_variants:
            for fname in ["shotgun_reload_1.wav", "shotgun_reload_2.wav"]:
                path = os.path.join(fallback_assets_dir, fname)
                if os.path.exists(path):
                    vars = self._load_sound_file_with_variants(path)
                    if vars:
                        self.reload_pitch_variants.append(vars)

    def play_blast(self):
        """Plays a shotgun blast sound effect instantly with polyphonic voice allocation."""
        if not config.get("enabled", True):
            return

        config.increment("total_shots_fired")
        if not self.blast_pitch_variants:
            return

        with self.audio_thread_lock:
            if len(self.blast_pitch_variants) > 1:
                choices = [i for i in range(len(self.blast_pitch_variants)) if i != self.last_played_blast_idx]
                idx = random.choice(choices) if choices else 0
                self.last_played_blast_idx = idx
            else:
                idx = 0

            variant_group = self.blast_pitch_variants[idx]
            if not variant_group:
                return

            if self.pitch_randomization and len(variant_group) > 1:
                sound_to_play = random.choice(variant_group)
            else:
                sound_to_play = variant_group[0]

            vol_factor = random.uniform(0.93, 1.0) if self.pitch_randomization else 1.0
            try:
                sound_to_play.set_volume(self.volume * vol_factor)
            except Exception:
                pass

            if PYGAME_AVAILABLE and pygame.mixer.get_init():
                channel = pygame.mixer.find_channel(True)
                if channel:
                    channel.play(sound_to_play)
            else:
                sound_to_play.play()

    def play_reload(self):
        """Plays a shotgun reload sound effect instantly."""
        if not config.get("enabled", True):
            return

        config.increment("total_reloads")
        if not self.reload_pitch_variants:
            return

        with self.audio_thread_lock:
            if len(self.reload_pitch_variants) > 1:
                choices = [i for i in range(len(self.reload_pitch_variants)) if i != self.last_played_reload_idx]
                idx = random.choice(choices) if choices else 0
                self.last_played_reload_idx = idx
            else:
                idx = 0

            variant_group = self.reload_pitch_variants[idx]
            if not variant_group:
                return

            if self.pitch_randomization and len(variant_group) > 1:
                sound_to_play = random.choice(variant_group)
            else:
                sound_to_play = variant_group[0]

            vol_factor = random.uniform(0.95, 1.0) if self.pitch_randomization else 1.0
            try:
                sound_to_play.set_volume(self.volume * vol_factor)
            except Exception:
                pass

            if PYGAME_AVAILABLE and pygame.mixer.get_init():
                channel = pygame.mixer.find_channel(True)
                if channel:
                    channel.play(sound_to_play)
            else:
                sound_to_play.play()

# Global engine instance
sound_engine = SoundEngine.get_instance()
