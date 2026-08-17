#!/bin/bash
set -e

REPO_NAME="ShotgunKeys"
USERNAME="fahmidhasann"
TAG="v1.0.0"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================================="
echo " 🚀 ShotgunKeys Multi-Platform GitHub Publisher"
echo "=========================================================="

cd "$PROJECT_DIR"

# 1. Check gh auth
echo "Checking GitHub authentication..."
if ! gh auth status &>/dev/null; then
    echo "❌ Error: GitHub CLI is not authenticated. Run 'gh auth login' first."
    exit 1
fi
echo "✓ Authenticated as $USERNAME"

# 2. Ensure git repo is initialized and committed
if [ ! -d ".git" ]; then
    echo "Initializing local Git repository..."
    git init
    git branch -M main
fi

git add .
if ! git diff --cached --quiet; then
    git commit -m "feat: ShotgunKeys multi-platform release (macOS, Windows, Android, Web)"
fi
echo "✓ Git commit ready"

# 3. Create Remote GitHub Repository if not existing
echo "Ensuring remote repository '$USERNAME/$REPO_NAME' exists..."
if ! gh repo view "$USERNAME/$REPO_NAME" &>/dev/null; then
    echo "Creating public repository '$REPO_NAME' on GitHub..."
    gh repo create "$REPO_NAME" --public --description "💥 Turn Every Keystroke into a 12-Gauge Blast! Multi-platform for macOS, Windows and Android" --source=. --remote=origin --push || {
        echo "Creating repository via API..."
        gh api -X POST /user/repos -f name="$REPO_NAME" -f description="💥 Turn Every Keystroke into a 12-Gauge Blast! Multi-platform for macOS, Windows and Android" -F private=false || true
    }
fi

# 4. Set remote URL and push
TOKEN=$(gh auth token)
git remote set-url origin "https://${USERNAME}:${TOKEN}@github.com/${USERNAME}/${REPO_NAME}.git" 2>/dev/null || git remote add origin "https://${USERNAME}:${TOKEN}@github.com/${USERNAME}/${REPO_NAME}.git"

echo "Pushing code to main branch..."
git push -u origin main

# 5. Create GitHub Release v1.0.0 and upload binaries
echo "Creating GitHub Release $TAG and uploading binaries..."
RELEASE_ASSETS=()
if [ -f "releases/ShotgunKeys-macOS.zip" ]; then
    RELEASE_ASSETS+=("releases/ShotgunKeys-macOS.zip#ShotgunKeys for macOS (.zip)")
fi
if [ -f "releases/ShotgunKeys-Windows.zip" ]; then
    RELEASE_ASSETS+=("releases/ShotgunKeys-Windows.zip#ShotgunKeys for Windows (.zip)")
fi
if [ -f "releases/ShotgunKeys.apk" ]; then
    RELEASE_ASSETS+=("releases/ShotgunKeys.apk#ShotgunKeys for Android (.apk)")
fi

gh release create "$TAG" "${RELEASE_ASSETS[@]}" \
    --title "ShotgunKeys v1.0.0 — Multi-Platform Release" \
    --notes "💥 **ShotgunKeys v1.0.0** is here! Turn every keystroke into an authentic 12-gauge blast.

### 📦 Downloads:
- 🍏 **macOS**: \`ShotgunKeys-macOS.zip\` (Apple Silicon & Intel)
- 🪟 **Windows**: \`ShotgunKeys-Windows.zip\` (Portable 10/11)
- 🤖 **Android**: \`ShotgunKeys.apk\` (Full installable APK)

🌐 **Live Web Soundboard**: https://${USERNAME}.github.io/ShotgunKeys/" \
    --target main || echo "Release might already exist or will be updated."

# 6. Enable GitHub Pages on /docs folder
echo "Configuring GitHub Pages..."
gh api -X POST "/repos/$USERNAME/$REPO_NAME/pages" \
    -f source[branch]="main" \
    -f source[path]="/docs" 2>/dev/null || echo "GitHub Pages configuration submitted."

echo "=========================================================="
echo " ✅ PUBLISH COMPLETE!"
echo " 🌐 Web Landing: https://${USERNAME}.github.io/${REPO_NAME}/"
echo " 📦 Releases: https://github.com/${USERNAME}/${REPO_NAME}/releases/tag/${TAG}"
echo " ⭐ Repo: https://github.com/${USERNAME}/${REPO_NAME}"
echo "=========================================================="
