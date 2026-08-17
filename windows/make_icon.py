#!/usr/bin/env python3
"""
High quality icon generation for ShotgunKeys Windows (.ico and .png).
"""
import os
from PIL import Image, ImageDraw

def render_master_icon(size=512):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size / 2.0, size / 2.0
    r_outer = size * 0.46

    # 1. Outer golden / amber metallic rim
    draw.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer],
                 fill=(235, 140, 20, 255))

    # 2. Dark gunmetal inner base
    r_inner = r_outer * 0.92
    draw.ellipse([cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner],
                 fill=(28, 30, 36, 255))

    # Tactical inner ring 1
    r_t1 = size * 0.32
    draw.ellipse([cx - r_t1, cy - r_t1, cx + r_t1, cy + r_t1],
                 outline=(255, 180, 45, 230), width=max(2, int(size * 0.02)))

    # Tactical inner ring 2
    r_t2 = size * 0.20
    draw.ellipse([cx - r_t2, cy - r_t2, cx + r_t2, cy + r_t2],
                 outline=(255, 200, 60, 240), width=max(2, int(size * 0.018)))

    # Crosshairs
    tick_len = size * 0.12
    tick_gap = size * 0.07
    tick_w = max(3, int(size * 0.03))
    # Top, Bottom, Left, Right
    draw.line([(cx, cy - tick_gap - tick_len), (cx, cy - tick_gap)], fill=(255, 195, 50, 255), width=tick_w)
    draw.line([(cx, cy + tick_gap), (cx, cy + tick_gap + tick_len)], fill=(255, 195, 50, 255), width=tick_w)
    draw.line([(cx - tick_gap - tick_len, cy), (cx - tick_gap, cy)], fill=(255, 195, 50, 255), width=tick_w)
    draw.line([(cx + tick_gap, cy), (cx + tick_gap + tick_len, cy)], fill=(255, 195, 50, 255), width=tick_w)

    # Core flash glow
    draw.ellipse([cx - size * 0.09, cy - size * 0.09, cx + size * 0.09, cy + size * 0.09],
                 fill=(255, 140, 20, 255))
    draw.ellipse([cx - size * 0.06, cy - size * 0.06, cx + size * 0.06, cy + size * 0.06],
                 fill=(255, 220, 80, 255))
    draw.ellipse([cx - size * 0.03, cy - size * 0.03, cx + size * 0.03, cy + size * 0.03],
                 fill=(255, 255, 255, 255))

    return img

def main():
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    os.makedirs(assets_dir, exist_ok=True)

    master = render_master_icon(512)
    png_path = os.path.join(assets_dir, "app_icon.png")
    master.save(png_path, "PNG")
    print("Master PNG generated:", png_path)

    ico_path = os.path.join(assets_dir, "app_icon.ico")
    master.save(ico_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print("Windows ICO generated:", ico_path, "Size:", os.path.getsize(ico_path), "bytes")

if __name__ == "__main__":
    main()
