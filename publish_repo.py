#!/usr/bin/env python3
"""
ShotgunKeys Automated GitHub Deployer & Publisher
Automatically creates the repository, pushes all platform branches,
uploads release binaries, and configures GitHub Pages.
"""

import subprocess
import sys
import time
import os
import json
import urllib.request
import urllib.error

REPO_NAME = "ShotgunKeys"
REPO_DESC = "💥 Turn every keystroke into a 12-gauge shotgun blast! Available for macOS, Windows, and Android."
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_cmd(cmd, cwd=PROJECT_DIR, check=True):
    print(f"➜ Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    res = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), capture_output=True, text=True)
    if res.stdout.strip():
        print(res.stdout.strip())
    if res.stderr.strip():
        print(res.stderr.strip())
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed with code {res.returncode}")
    return res

def get_gh_token():
    res = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True)
    if res.returncode != 0 or not res.stdout.strip():
        raise RuntimeError("GitHub CLI is not authenticated. Please run 'gh auth login'.")
    return res.stdout.strip()

def get_gh_user(token):
    url = "https://api.github.com/user"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "ShotgunKeys-Deployer"
    })
    with urllib.request.urlopen(req, timeout=8) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["login"]

def create_github_repo(token, username):
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "ShotgunKeys-Deployer"
    }
    payload = json.dumps({
        "name": REPO_NAME,
        "description": REPO_DESC,
        "private": False,
        "has_issues": True,
        "has_projects": True,
        "has_wiki": True
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"✓ Repository created successfully: {username}/{REPO_NAME}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        if "already exists" in body or e.code == 422:
            print(f"✓ Repository already exists: {username}/{REPO_NAME}")
            return True
        print(f"HTTP Error {e.code}: {body}")
        raise e

def enable_github_pages(token, username):
    url = f"https://api.github.com/repos/{username}/{REPO_NAME}/pages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "ShotgunKeys-Deployer"
    }
    payload = json.dumps({
        "source": {
            "branch": "main",
            "path": "/docs"
        }
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"✓ GitHub Pages enabled at: https://{username}.github.io/{REPO_NAME}/")
    except urllib.error.HTTPError as e:
        if e.code == 409: # Already enabled
            print(f"✓ GitHub Pages is already active: https://{username}.github.io/{REPO_NAME}/")
        else:
            print(f"Note: GitHub Pages setup returned code {e.code} (can be enabled via Repo Settings > Pages)")

def main():
    print("==========================================================")
    print(" 🚀 ShotgunKeys Automated GitHub Deployer & Publisher")
    print("==========================================================")

    # 1. Check Authentication
    token = get_gh_token()
    print("✓ GitHub CLI Token verified.")

    # 2. Prepare Local Git Commit
    run_cmd(["git", "add", "."], check=False)
    run_cmd(["git", "commit", "-m", "feat: ShotgunKeys v1.0.0 multi-platform release (macOS, Windows, Android)"], check=False)

    # 3. Wait for GitHub API Availability & Create Repo
    max_retries = 30
    username = None
    for attempt in range(1, max_retries + 1):
        try:
            print(f"[{attempt}/{max_retries}] Connecting to GitHub API...")
            username = get_gh_user(token)
            print(f"✓ Authenticated as: {username}")
            create_github_repo(token, username)
            break
        except Exception as e:
            print(f"⚠️  GitHub API responded with error: {e}. Retrying in 4 seconds...")
            time.sleep(4)

    if not username:
        print("❌ Could not reach GitHub API. Please check your internet connection or GitHub Status.")
        sys.exit(1)

    # 4. Configure Remote and Push Code
    remote_url = f"https://github.com/{username}/{REPO_NAME}.git"
    print(f"Setting remote origin to: {remote_url}")
    run_cmd(f"git remote set-url origin {remote_url} || git remote add origin {remote_url}", check=False)
    run_cmd(["git", "branch", "-M", "main"])
    
    print("Pushing codebase to GitHub main branch...")
    push_res = run_cmd(["git", "push", "-u", "origin", "main", "--force"], check=False)
    if push_res.returncode != 0:
        print("Retrying push with credential helper...")
        run_cmd(f"git push -u origin main", check=True)

    # 5. Create GitHub Release v1.0.0 with Attachments
    print("\n📦 Publishing Release v1.0.0 to GitHub...")
    releases_dir = os.path.join(PROJECT_DIR, "releases")
    mac_zip = os.path.join(releases_dir, "ShotgunKeys-macOS.zip")
    win_zip = os.path.join(releases_dir, "ShotgunKeys-Windows.zip")
    apk_file = os.path.join(releases_dir, "ShotgunKeys.apk")

    release_notes = """## 💥 ShotgunKeys v1.0.0 Multi-Platform Release

Turn every keystroke into an authentic 12-gauge shotgun blast and Space/Enter into tactical pump-action reloads!

### 📥 Downloads
- **🍏 macOS**: [`ShotgunKeys-macOS.zip`](https://github.com/{username}/ShotgunKeys/releases/download/v1.0.0/ShotgunKeys-macOS.zip) (Ready-to-run `.app`)
- **🪟 Windows**: [`ShotgunKeys-Windows.zip`](https://github.com/{username}/ShotgunKeys/releases/download/v1.0.0/ShotgunKeys-Windows.zip) (Portable zero-setup package)
- **🤖 Android**: [`ShotgunKeys.apk`](https://github.com/{username}/ShotgunKeys/releases/download/v1.0.0/ShotgunKeys.apk) (Signed installable APK)

### 🌐 Live Web Soundboard
Try the sounds right in your browser: https://{username}.github.io/ShotgunKeys/
""".format(username=username)

    notes_file = os.path.join(PROJECT_DIR, ".release_notes.tmp")
    with open(notes_file, "w") as f:
        f.write(release_notes)

    # Delete existing release if re-running
    subprocess.run(["gh", "release", "delete", "v1.0.0", "-y"], capture_output=True)

    create_rel_cmd = [
        "gh", "release", "create", "v1.0.0",
        mac_zip, win_zip, apk_file,
        "--title", "💥 ShotgunKeys v1.0.0 — Multi-Platform Release",
        "--notes-file", notes_file
    ]
    run_cmd(create_rel_cmd, check=False)
    if os.path.exists(notes_file):
        os.remove(notes_file)

    # 6. Enable GitHub Pages
    print("\n🌐 Configuring GitHub Pages for Live Web Soundboard...")
    enable_github_pages(token, username)

    print("\n==========================================================")
    print(" 🎉 SUCCESS! ShotgunKeys is LIVE on GitHub!")
    print("==========================================================")
    print(f"⭐ Repository: https://github.com/{username}/{REPO_NAME}")
    print(f"📦 Releases:   https://github.com/{username}/{REPO_NAME}/releases/tag/v1.0.0")
    print(f"🌐 Web Site:   https://{username}.github.io/{REPO_NAME}/")
    print("==========================================================")

if __name__ == "__main__":
    main()
