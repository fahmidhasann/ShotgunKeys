#!/usr/bin/env python3
"""
PyInstaller packaging script for ShotgunKeys Windows.
Builds a standalone, zero-dependency executable 'ShotgunKeys.exe' with embedded assets and icon.
"""

import os
import sys
import subprocess
import shutil

def build():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "assets")
    custom_sounds_dir = os.path.join(base_dir, "custom_sounds")
    icon_path = os.path.join(assets_dir, "app_icon.ico")
    main_script = os.path.join(base_dir, "main.py")

    sep = ";" if os.name == 'nt' else ":"

    print("==================================================")
    print("   🔨 BUILDING STANDALONE SHOTGUNKEYS.EXE         ")
    print("==================================================")

    # Ensure icon exists
    if not os.path.exists(icon_path):
        print("[Build] Generating app icon...")
        subprocess.run([sys.executable, os.path.join(base_dir, "make_icon.py")], check=True)

    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--name=ShotgunKeys",
        "--onefile",
        "--noconsole",
        f"--icon={icon_path}",
        f"--add-data={assets_dir}{sep}assets",
        f"--add-data={custom_sounds_dir}{sep}custom_sounds",
        "--hidden-import=pygame",
        "--hidden-import=pygame.mixer",
        "--hidden-import=pynput",
        "--hidden-import=pynput.keyboard",
        "--hidden-import=pystray",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--clean",
        "-y",
        main_script
    ]

    print("[Build] Running command:")
    print(" ".join(cmd))
    print("--------------------------------------------------")

    result = subprocess.run(cmd, cwd=base_dir)

    if result.returncode == 0:
        dist_dir = os.path.join(base_dir, "dist")
        exe_path = os.path.join(dist_dir, "ShotgunKeys.exe" if os.name == 'nt' else "ShotgunKeys")
        
        # Ensure a copy of custom_sounds is next to dist for user convenience
        dist_custom = os.path.join(dist_dir, "custom_sounds")
        os.makedirs(dist_custom, exist_ok=True)
        readme_src = os.path.join(custom_sounds_dir, "README.txt")
        if os.path.exists(readme_src):
            shutil.copy(readme_src, os.path.join(dist_custom, "README.txt"))

        print("==================================================")
        print("   ✅ BUILD SUCCESSFUL!                           ")
        print(f"   Output: {exe_path}")
        print("==================================================")
    else:
        print("[Build] ❌ Build failed with exit code:", result.returncode)
        sys.exit(result.returncode)

if __name__ == "__main__":
    build()
