#!/usr/bin/env python3
"""
Procedural Shotgun & Reload Sound Synthesizer
Generates 16-bit 44.1kHz PCM WAV audio files for ShotgunKeys macOS app.
"""

import math
import os
import random
import struct
import wave

SAMPLE_RATE = 44100

def write_wav(filename, samples, sample_rate=SAMPLE_RATE):
    """Write normalized float samples (-1.0 to 1.0) to a 16-bit mono WAV file."""
    # Peak normalization with headroom
    max_amp = max(abs(s) for s in samples) if samples else 1.0
    if max_amp < 1e-6:
        max_amp = 1.0
    gain = 0.92 / max_amp

    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)

        packed_data = bytearray()
        for s in samples:
            val = int(max(min(s * gain, 1.0), -1.0) * 32767)
            packed_data.extend(struct.pack('<h', val))
        wav_file.writeframes(packed_data)
    print(f"Generated: {filename} ({len(samples)/sample_rate:.3f}s)")

def generate_shotgun_blast(variation=1, duration=0.38):
    """
    Synthesize a heavy 12-gauge shotgun blast:
    1. Initial supersonic shockwave transient (0-8ms)
    2. Deep explosive sub-bass pitch drop (10-150ms)
    3. Multi-layer filtered turbulent explosion noise
    4. Metal barrel ringing resonance
    5. Diffuse acoustic decay tail
    """
    total_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * total_samples
    random.seed(42 + variation * 101)

    # Pitch/tone slight variation
    base_sub_freq = 190.0 + (variation - 1) * 18.0
    metal_freq1 = 520.0 + (variation * 40.0)
    metal_freq2 = 1180.0 + (variation * 60.0)

    # IIR Lowpass filter state
    lp_out = 0.0
    lp_alpha = 0.28 + (variation * 0.02)

    for i in range(total_samples):
        t = i / SAMPLE_RATE

        # 1. Transient Attack Spike (0 - 0.012s)
        transient = 0.0
        if t < 0.012:
            transient_env = (1.0 - t / 0.012) ** 1.8
            transient = (random.uniform(-1.0, 1.0) * 1.5 + math.sin(2 * math.pi * 3200 * t)) * transient_env

        # 2. Sub-Bass Punch (Explosive kick: frequency drops exponentially from ~200Hz to 38Hz)
        sub_freq = max(35.0, base_sub_freq * math.exp(-t * 24.0))
        sub_phase = 2 * math.pi * sub_freq * t
        sub_env = math.exp(-t * 14.0) * (1.0 if t > 0.002 else t / 0.002)
        sub_boom = (math.sin(sub_phase) + 0.4 * math.sin(sub_phase * 0.5) + 0.25 * math.sin(sub_phase * 2.0)) * sub_env

        # 3. Explosive Body (Filtered high-energy noise with non-linear distortion)
        raw_noise = random.uniform(-1.0, 1.0)
        dynamic_alpha = lp_alpha * math.exp(-t * 8.0) + 0.015
        lp_out += dynamic_alpha * (raw_noise - lp_out)
        body_env = math.exp(-t * 11.5) * (1.0 if t > 0.001 else t / 0.001)
        distorted_noise = math.tanh(lp_out * 3.2) * body_env

        # 4. Metal Barrel Resonant Clang / Ring
        ring_env = math.exp(-t * 18.0) * 0.25
        metal_ring = (math.sin(2 * math.pi * metal_freq1 * t) * 0.6 +
                      math.sin(2 * math.pi * metal_freq2 * t) * 0.4) * ring_env

        # 5. Tail Reverb / Scatter
        tail_env = math.exp(-t * 7.5) * 0.35
        tail = raw_noise * tail_env

        # Composite sample
        sample = (transient * 1.3) + (sub_boom * 1.4) + (distorted_noise * 1.6) + (metal_ring * 0.6) + (tail * 0.4)
        samples[i] = math.tanh(sample * 1.1)

    return samples

def generate_pump_reload(variation=1, duration=0.32):
    """
    Synthesize a tactical pump-action rack sound:
    Stage 1 (0ms - 80ms): Slide racking back (metallic friction + click + shell eject clink)
    Stage 2 (80ms - 140ms): Mechanical spring sliding
    Stage 3 (140ms - 290ms): Slide slamming forward into battery (heavy solid metal CHAK-CLACK)
    """
    total_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * total_samples
    random.seed(88 + variation * 77)

    t_rack_back = 0.015
    t_eject = 0.065
    t_rack_forward = 0.155
    t_lock = 0.185

    for i in range(total_samples):
        t = i / SAMPLE_RATE
        val = 0.0

        # --- Stage 1: Slide Back (Click-Slide) ---
        if 0 <= t < 0.09:
            dt1 = t - t_rack_back
            if dt1 >= 0:
                env1 = math.exp(-dt1 * 60.0)
                click1 = (math.sin(2 * math.pi * 1850 * dt1) + random.uniform(-0.8, 0.8)) * env1
                val += click1 * 0.9

            # Shell ejection ping/clink
            dt_eject = t - t_eject
            if dt_eject >= 0:
                env_eject = math.exp(-dt_eject * 45.0)
                clink = math.sin(2 * math.pi * 2900 * dt_eject) * env_eject * 0.5
                val += clink

            val += (random.uniform(-0.5, 0.5) * math.sin(2 * math.pi * 950 * t)) * math.exp(-t * 25.0) * 0.4

        # --- Stage 2: Slide Forward + Chambering ---
        if 0.10 <= t < 0.32:
            dt_fwd = t - t_rack_forward
            if dt_fwd >= 0:
                env_fwd = math.exp(-dt_fwd * 55.0)
                click_fwd = (math.sin(2 * math.pi * 1400 * dt_fwd) + random.uniform(-0.9, 0.9)) * env_fwd
                val += click_fwd * 1.1

            dt_lock = t - t_lock
            if dt_lock >= 0:
                env_lock = math.exp(-dt_lock * 35.0)
                thud = math.sin(2 * math.pi * 180 * dt_lock) * math.exp(-dt_lock * 25.0) * 1.2
                snap = (math.sin(2 * math.pi * 2400 * dt_lock) + math.sin(2 * math.pi * 3800 * dt_lock) * 0.5) * env_lock * 0.9
                lock_noise = random.uniform(-0.9, 0.9) * env_lock * 0.8
                val += (thud + snap + lock_noise) * 1.2

        samples[i] = math.tanh(val * 1.3)

    return samples

def generate_arcade_blast(duration=0.25):
    """Retro 8-bit/16-bit arcade punchy blast"""
    total_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * total_samples
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        freq = max(40.0, 600.0 * math.exp(-t * 22.0))
        square = 1.0 if (math.sin(2 * math.pi * freq * t) > 0) else -1.0
        noise = random.uniform(-1.0, 1.0)
        env = math.exp(-t * 14.0)
        samples[i] = (square * 0.45 + noise * 0.75) * env
    return samples

def generate_arcade_reload(duration=0.22):
    """Retro arcade pump sound"""
    total_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * total_samples
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        val = 0.0
        if t < 0.08:
            freq = 400.0 + t * 4000.0
            val = (1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0) * math.exp(-t * 20.0)
        elif t > 0.10:
            dt = t - 0.10
            freq = 1200.0 - dt * 5000.0
            if freq > 100:
                val = (1.0 if math.sin(2 * math.pi * freq * dt) > 0 else -1.0) * math.exp(-dt * 25.0)
        samples[i] = val * 0.7
    return samples

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "Assets")
    os.makedirs(assets_dir, exist_ok=True)

    print("Synthesizing ShotgunKeys audio assets...")
    
    # 1. Realistic 12-Gauge Blasts
    for v in [1, 2, 3]:
        samples = generate_shotgun_blast(variation=v, duration=0.38)
        write_wav(os.path.join(assets_dir, f"shotgun_blast_{v}.wav"), samples)

    # 2. Realistic Pump-Action Reloads
    for v in [1, 2]:
        samples = generate_pump_reload(variation=v, duration=0.32)
        write_wav(os.path.join(assets_dir, f"shotgun_reload_{v}.wav"), samples)

    # 3. Arcade Retro Soundpack
    write_wav(os.path.join(assets_dir, "arcade_blast.wav"), generate_arcade_blast())
    write_wav(os.path.join(assets_dir, "arcade_reload.wav"), generate_arcade_reload())

    print("\nAll sound assets synthesized successfully!")

if __name__ == "__main__":
    main()
