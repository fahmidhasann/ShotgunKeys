#!/usr/bin/env python3
"""
Generates an App Icon for ShotgunKeys using pure python / zlib PNG generation,
then creates a macOS .icns file using iconutil.
"""

import os
import struct
import zlib
import subprocess

def create_png(width, height, filename):
    """Generate a high-res RGBA PNG with a fiery shotgun / crosshair theme"""
    raw_data = bytearray()
    cx, cy = width / 2.0, height / 2.0
    r_outer = width * 0.45

    for y in range(height):
        raw_data.append(0) # Filter type 0 (None)
        for x in range(width):
            dx = x - cx
            dy = y - cy
            dist = (dx*dx + dy*dy) ** 0.5
            norm_dist = dist / r_outer

            if norm_dist > 1.0:
                # Outside circle - transparent
                raw_data.extend([0, 0, 0, 0])
                continue

            # Dark tactical carbon base background
            bg_r = int(25 + 15 * (1.0 - norm_dist))
            bg_g = int(28 + 15 * (1.0 - norm_dist))
            bg_b = int(32 + 15 * (1.0 - norm_dist))
            alpha = 255

            # Outer ring gradient
            if norm_dist > 0.88:
                ring_t = (norm_dist - 0.88) / 0.12
                # Golden / Orange metallic ring
                bg_r = int(240 * (1.0 - ring_t) + 180 * ring_t)
                bg_g = int(140 * (1.0 - ring_t) + 90 * ring_t)
                bg_b = int(20 * (1.0 - ring_t) + 10 * ring_t)

            # Center Crosshairs / Target Rings
            ring1 = abs(dist - width * 0.28) < (width * 0.02)
            ring2 = abs(dist - width * 0.15) < (width * 0.015)
            cross_x = abs(dx) < (width * 0.018) and abs(dy) > (width * 0.08) and dist < (width * 0.38)
            cross_y = abs(dy) < (width * 0.018) and abs(dx) > (width * 0.08) and dist < (width * 0.38)

            if ring1 or ring2 or cross_x or cross_y:
                bg_r = 255
                bg_g = 180
                bg_b = 40

            # Central Muzzle Flash Burst (explosive core)
            if dist < (width * 0.12):
                core_t = dist / (width * 0.12)
                bg_r = 255
                bg_g = int(240 - core_t * 120)
                bg_b = int(200 - core_t * 180)

            raw_data.extend([bg_r, bg_g, bg_b, alpha])

    # Build PNG chunk structure
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    png_bytes = (
        b'\x89PNG\r\n\x1a\n' +
        chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)) +
        chunk(b'IDAT', zlib.compress(bytes(raw_data), 9)) +
        chunk(b'IEND', b'')
    )

    with open(filename, 'wb') as f:
        f.write(png_bytes)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    iconset_dir = os.path.join(base_dir, "AppIcon.iconset")
    os.makedirs(iconset_dir, exist_ok=True)

    sizes = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png"),
    ]

    print("Generating icon layers...")
    for sz, name in sizes:
        create_png(sz, sz, os.path.join(iconset_dir, name))

    print("Compiling AppIcon.icns via iconutil...")
    assets_dir = os.path.join(base_dir, "Assets")
    os.makedirs(assets_dir, exist_ok=True)
    icns_path = os.path.join(assets_dir, "AppIcon.icns")
    subprocess.run(["iconutil", "-c", "icns", iconset_dir, "-o", icns_path], check=True)
    print("AppIcon.icns created successfully at:", icns_path)

if __name__ == "__main__":
    main()
