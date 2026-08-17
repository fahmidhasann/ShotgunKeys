#!/usr/bin/env python3
"""
Audio Mastering and Processing for ShotgunKeys
Trims lead silence, normalizes volume, applies transient punch and smooth fade-outs.
"""

import math
import os
import struct
import wave

def read_wav_samples(filename):
    with wave.open(filename, 'rb') as w:
        nchannels = w.getnchannels()
        sampwidth = w.getsampwidth()
        framerate = w.getframerate()
        nframes = w.getnframes()
        raw_bytes = w.readframes(nframes)

    samples = []
    if sampwidth == 2:  # 16-bit PCM
        fmt = f"<{nframes * nchannels}h"
        int_samples = struct.unpack(fmt, raw_bytes)
        for i in range(0, len(int_samples), nchannels):
            # Downmix to mono if stereo
            mono_val = sum(int_samples[i:i+nchannels]) / (nchannels * 32768.0)
            samples.append(mono_val)
    elif sampwidth == 3:  # 24-bit PCM
        for i in range(0, len(raw_bytes), 3 * nchannels):
            ch_vals = []
            for ch in range(nchannels):
                offset = i + ch * 3
                b = raw_bytes[offset:offset+3]
                val = int.from_bytes(b, byteorder='little', signed=True) / (8388608.0)
                ch_vals.append(val)
            samples.append(sum(ch_vals) / len(ch_vals))
    elif sampwidth == 4:  # 32-bit float or int
        fmt = f"<{nframes * nchannels}i"
        int_samples = struct.unpack(fmt, raw_bytes)
        for i in range(0, len(int_samples), nchannels):
            mono_val = sum(int_samples[i:i+nchannels]) / (nchannels * 2147483648.0)
            samples.append(mono_val)
    else:
        raise ValueError(f"Unsupported sample width: {sampwidth}")

    return samples, framerate

def write_mono_wav(filename, samples, framerate=44100):
    # Peak normalize
    max_amp = max(abs(s) for s in samples) if samples else 1.0
    if max_amp < 1e-6:
        max_amp = 1.0
    gain = 0.95 / max_amp

    with wave.open(filename, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(framerate)
        packed = bytearray()
        for s in samples:
            val = int(max(min(s * gain, 1.0), -1.0) * 32767)
            packed.extend(struct.pack('<h', val))
        w.writeframes(packed)
    print(f"Mastered & Saved: {filename} ({len(samples)/framerate:.3f}s)")

def process_audio(input_file, output_file, max_duration=0.42, threshold=0.03, fade_out_sec=0.08):
    if not os.path.exists(input_file):
        print(f"Warning: {input_file} not found")
        return

    samples, framerate = read_wav_samples(input_file)

    # 1. Detect transient start (find first sample exceeding threshold)
    start_idx = 0
    for idx, s in enumerate(samples):
        if abs(s) > threshold:
            # Back up slightly (5ms) to catch the micro-transient
            start_idx = max(0, idx - int(framerate * 0.005))
            break

    # 2. Trim to max_duration
    max_len = int(framerate * max_duration)
    trimmed = samples[start_idx : start_idx + max_len]

    # 3. Apply smooth exponential/cosine fade-out at the end
    fade_len = int(framerate * fade_out_sec)
    if len(trimmed) > fade_len:
        fade_start = len(trimmed) - fade_len
        for i in range(fade_len):
            t = i / fade_len
            # Smooth cosine curve
            mult = 0.5 * (1.0 + math.cos(math.pi * t))
            trimmed[fade_start + i] *= mult

    write_mono_wav(output_file, trimmed, framerate)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_dir = os.path.join(base_dir, "Assets", "raw")
    assets_dir = os.path.join(base_dir, "Assets")

    print("Mastering live-recorded 12-gauge shotgun blasts...")
    process_audio(os.path.join(raw_dir, "winchester_blast1.wav"), os.path.join(assets_dir, "shotgun_blast_1.wav"), max_duration=0.45, threshold=0.02, fade_out_sec=0.10)
    process_audio(os.path.join(raw_dir, "winchester_blast2.wav"), os.path.join(assets_dir, "shotgun_blast_2.wav"), max_duration=0.42, threshold=0.02, fade_out_sec=0.10)
    process_audio(os.path.join(raw_dir, "benelli_blast1.wav"), os.path.join(assets_dir, "shotgun_blast_3.wav"), max_duration=0.45, threshold=0.02, fade_out_sec=0.10)
    process_audio(os.path.join(raw_dir, "charles_daly_blast.wav"), os.path.join(assets_dir, "shotgun_blast_4.wav"), max_duration=0.48, threshold=0.02, fade_out_sec=0.10)

    print("\nMastering authentic pump-action reload sounds...")
    process_audio(os.path.join(assets_dir, "real_shotgun_reload.wav"), os.path.join(assets_dir, "shotgun_reload_1.wav"), max_duration=0.65, threshold=0.015, fade_out_sec=0.08)
    process_audio(os.path.join(raw_dir, "gunreload1.wav"), os.path.join(assets_dir, "shotgun_reload_2.wav"), max_duration=0.55, threshold=0.015, fade_out_sec=0.08)

    print("\nAudio mastering complete!")

if __name__ == "__main__":
    main()
