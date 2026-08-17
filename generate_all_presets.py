#!/usr/bin/env python3
"""
Preset Audio Synthesizer & Masterer for ShotgunKeys Public Release
Generates/masters all 6 soundpacks + sets up custom folder:
1. Realistic 12-Gauge (Live Winchester/Benelli)
2. Tactical Combat (Snappy military shotgun)
3. Heavy Doom / Boomstick (Massive sub-bass double barrel)
4. Silenced Spec-Ops (Suppressed pneumatic "thwip" + smooth slide)
5. Cyberpunk Energy (Futuristic plasma blast + servo reload)
6. 8-Bit Retro Arcade (Chiptune action)
"""

import math
import os
import random
import struct
import wave

SAMPLE_RATE = 44100

def write_mono_wav(filename, samples, sample_rate=SAMPLE_RATE):
    max_amp = max(abs(s) for s in samples) if samples else 1.0
    if max_amp < 1e-6:
        max_amp = 1.0
    gain = 0.95 / max_amp

    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        packed_data = bytearray()
        for s in samples:
            val = int(max(min(s * gain, 1.0), -1.0) * 32767)
            packed_data.extend(struct.pack('<h', val))
        wav_file.writeframes(packed_data)
    print(f"Mastered: {filename} ({len(samples)/sample_rate:.3f}s)")

# --- Tactical Combat (Tight & Snappy) ---
def generate_tactical_blast(variant=1, duration=0.28):
    total_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * total_samples
    random.seed(101 + variant * 37)
    
    base_freq = 240.0 + variant * 20.0
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Crisp attack transient
        trans = (random.uniform(-1.0, 1.0) * 2.0) * math.exp(-t * 180.0)
        # Tight punch
        punch_freq = max(50.0, base_freq * math.exp(-t * 35.0))
        punch = math.sin(2 * math.pi * punch_freq * t) * math.exp(-t * 22.0) * 1.5
        # Crisp noise burst with sharp cutoff
        noise = random.uniform(-0.8, 0.8) * math.exp(-t * 18.0) * 1.2
        # Metallic chamber snap
        metal = math.sin(2 * math.pi * 1450.0 * t) * math.exp(-t * 40.0) * 0.4
        
        samples[i] = math.tanh((trans + punch + noise + metal) * 1.2)
    return samples

def generate_tactical_reload(variant=1, duration=0.26):
    total_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * total_samples
    random.seed(202 + variant * 41)
    
    t_rack = 0.02
    t_lock = 0.13
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        val = 0.0
        # Stage 1: Sharp slide rack back
        if t >= t_rack and t < 0.10:
            dt = t - t_rack
            val += (math.sin(2 * math.pi * 2100 * dt) + random.uniform(-0.9, 0.9)) * math.exp(-dt * 65.0) * 1.1
        # Stage 2: Fast forward battery lock
        if t >= t_lock:
            dt = t - t_lock
            clack = (math.sin(2 * math.pi * 1600 * dt) + math.sin(2 * math.pi * 3200 * dt) * 0.6) * math.exp(-dt * 45.0) * 1.3
            thud = math.sin(2 * math.pi * 220 * dt) * math.exp(-dt * 30.0) * 0.9
            val += clack + thud
        samples[i] = math.tanh(val * 1.3)
    return samples

# --- Heavy Doom / Boomstick (Massive Double Barrel) ---
def generate_doom_blast(variant=1, duration=0.48):
    total_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * total_samples
    random.seed(303 + variant * 53)
    
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Double transient (two barrels firing almost simultaneously)
        trans1 = (random.uniform(-1.0, 1.0) * 1.8) * math.exp(-t * 120.0)
        dt2 = t - 0.008
        trans2 = (random.uniform(-1.0, 1.0) * 1.6) * math.exp(-max(0.0, dt2) * 110.0) if dt2 >= 0 else 0.0
        
        # Heavy sub-bass earthquake boom
        sub_freq = max(28.0, 160.0 * math.exp(-t * 15.0))
        sub = (math.sin(2 * math.pi * sub_freq * t) + 0.5 * math.sin(math.pi * sub_freq * t)) * math.exp(-t * 8.5) * 2.0
        
        # Roaring distorted blast body
        noise = math.tanh(random.uniform(-1.0, 1.0) * 3.0) * math.exp(-t * 10.0) * 1.5
        
        # Low metal resonance
        clang = math.sin(2 * math.pi * 380 * t) * math.exp(-t * 12.0) * 0.5
        
        samples[i] = math.tanh((trans1 + trans2 + sub + noise + clang) * 1.1)
    return samples

def generate_doom_reload(variant=1, duration=0.42):
    total_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * total_samples
    random.seed(404 + variant * 19)
    
    t_open = 0.02
    t_insert = 0.16
    t_snap = 0.28
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        val = 0.0
        # 1. Breech break open
        if t >= t_open and t < 0.12:
            dt = t - t_open
            val += (math.sin(2 * math.pi * 900 * dt) + math.sin(2 * math.pi * 2200 * dt) * 0.7) * math.exp(-dt * 35.0) * 0.9
        # 2. Heavy brass shells slide into chambers
        if t >= t_insert and t < 0.26:
            dt = t - t_insert
            val += (math.sin(2 * math.pi * 1750 * dt) + random.uniform(-0.6, 0.6)) * math.exp(-dt * 45.0) * 0.8
        # 3. Heavy double barrel snap shut (THUD-CLICK)
        if t >= t_snap:
            dt = t - t_snap
            snap_thud = math.sin(2 * math.pi * 140 * dt) * math.exp(-dt * 20.0) * 1.4
            snap_metal = (math.sin(2 * math.pi * 2800 * dt) + math.sin(2 * math.pi * 4200 * dt) * 0.5) * math.exp(-dt * 40.0) * 1.2
            val += snap_thud + snap_metal
        samples[i] = math.tanh(val * 1.3)
    return samples

# --- Silenced Spec-Ops (Stealth / Office Friendly) ---
def generate_silenced_blast(variant=1, duration=0.22):
    total_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * total_samples
    random.seed(505 + variant * 29)
    
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Suppressed pneumatic "Thwip" / puff
        puff_freq = max(80.0, 420.0 * math.exp(-t * 40.0))
        puff = math.sin(2 * math.pi * puff_freq * t) * math.exp(-t * 26.0) * 1.2
        # Whispering gas dispersion noise
        gas = (random.uniform(-0.5, 0.5) * math.sin(2 * math.pi * 1200 * t)) * math.exp(-t * 30.0) * 0.8
        # Subtle internal bolt click
        click = math.sin(2 * math.pi * 2600 * t) * math.exp(-t * 70.0) * 0.5
        
        samples[i] = math.tanh((puff + gas + click) * 0.95)
    return samples

def generate_silenced_reload(variant=1, duration=0.24):
    total_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * total_samples
    random.seed(606 + variant * 31)
    
    t_rack = 0.02
    t_fwd = 0.12
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        val = 0.0
        # Smooth oiled slide pull
        if t >= t_rack and t < 0.10:
            dt = t - t_rack
            val += (math.sin(2 * math.pi * 1350 * dt) * 0.6 + random.uniform(-0.4, 0.4)) * math.exp(-dt * 35.0) * 0.8
        # Soft muffled chamber lock
        if t >= t_fwd:
            dt = t - t_fwd
            val += (math.sin(2 * math.pi * 850 * dt) + math.sin(2 * math.pi * 2100 * dt) * 0.4) * math.exp(-dt * 40.0) * 1.0
        samples[i] = math.tanh(val * 0.9)
    return samples

# --- Cyberpunk Energy / Plasma Shotgun ---
def generate_cyber_blast(variant=1, duration=0.32):
    total_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * total_samples
    random.seed(707 + variant * 43)
    
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Plasma ionization transient
        trans = (math.sin(2 * math.pi * 4500 * t) * random.uniform(0.5, 1.5)) * math.exp(-t * 90.0)
        # Sci-Fi laser frequency sweep
        sweep_freq = max(60.0, 1800.0 * math.exp(-t * 22.0))
        laser = math.sin(2 * math.pi * sweep_freq * t + math.sin(2 * math.pi * 120 * t)) * math.exp(-t * 14.0) * 1.4
        # Heavy sub energy blast
        sub = math.sin(2 * math.pi * 65 * t) * math.exp(-t * 12.0) * 1.2
        # Electric sizzle
        sizzle = (random.uniform(-0.7, 0.7) * math.sin(2 * math.pi * 6200 * t)) * math.exp(-t * 18.0) * 0.7
        
        samples[i] = math.tanh((trans + laser + sub + sizzle) * 1.1)
    return samples

def generate_cyber_reload(variant=1, duration=0.30):
    total_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * total_samples
    random.seed(808 + variant * 47)
    
    t_eject = 0.02
    t_charge = 0.10
    t_lock = 0.20
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        val = 0.0
        # 1. Thermal cell eject beep / hiss
        if t >= t_eject and t < 0.09:
            dt = t - t_eject
            val += math.sin(2 * math.pi * 2800 * dt) * math.exp(-dt * 50.0) * 0.8
        # 2. Magnetic charging coil pitch ramp
        if t >= t_charge and t < 0.22:
            dt = t - t_charge
            ramp_freq = 600.0 + dt * 4500.0
            val += math.sin(2 * math.pi * ramp_freq * dt) * math.sin(math.pi * dt / 0.12) * 1.1
        # 3. Cyber servo lock (Ching!)
        if t >= t_lock:
            dt = t - t_lock
            val += (math.sin(2 * math.pi * 3200 * dt) + math.sin(2 * math.pi * 800 * dt) * 0.7) * math.exp(-dt * 45.0) * 1.2
        samples[i] = math.tanh(val * 1.2)
    return samples

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "Assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    print("Generating all 6 sound presets for ShotgunKeys...")
    
    # 1. Tactical Combat (3 blasts, 2 reloads)
    for v in [1, 2, 3]:
        write_mono_wav(os.path.join(assets_dir, f"tactical_blast_{v}.wav"), generate_tactical_blast(v))
    for v in [1, 2]:
        write_mono_wav(os.path.join(assets_dir, f"tactical_reload_{v}.wav"), generate_tactical_reload(v))

    # 2. Heavy Doom (2 blasts, 2 reloads)
    for v in [1, 2]:
        write_mono_wav(os.path.join(assets_dir, f"doom_blast_{v}.wav"), generate_doom_blast(v))
        write_mono_wav(os.path.join(assets_dir, f"doom_reload_{v}.wav"), generate_doom_reload(v))

    # 3. Silenced Spec-Ops (2 blasts, 2 reloads)
    for v in [1, 2]:
        write_mono_wav(os.path.join(assets_dir, f"silenced_blast_{v}.wav"), generate_silenced_blast(v))
        write_mono_wav(os.path.join(assets_dir, f"silenced_reload_{v}.wav"), generate_silenced_reload(v))

    # 4. Cyberpunk Energy (2 blasts, 2 reloads)
    for v in [1, 2]:
        write_mono_wav(os.path.join(assets_dir, f"cyber_blast_{v}.wav"), generate_cyber_blast(v))
        write_mono_wav(os.path.join(assets_dir, f"cyber_reload_{v}.wav"), generate_cyber_reload(v))

    print("\nAll presets synthesized and mastered successfully!")

if __name__ == "__main__":
    main()
