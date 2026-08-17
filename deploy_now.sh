#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "=========================================================="
echo " 🚀 ShotgunKeys One-Click GitHub Deployer"
echo "=========================================================="

echo "1. Checking GitHub Authentication..."
USER_NAME=$(gh api user --jq .login 2>/dev/null || echo "")

if [ -z "$USER_NAME" ]; then
    echo "❌ GitHub API is currently unavailable (HTTP 503) or not logged in."
    echo "Please wait a few moments for GitHub servers to recover and run this script again."
    exit 1
fi

echo "✓ Authenticated as: $USER_NAME"

echo "2. Preparing Git Commits..."
git add .
git commit -m "feat: ShotgunKeys v1.0.0 multi-platform release (macOS, Windows, Android)" || true
git branch -M main

echo "3. Creating GitHub Repository 'ShotgunKeys'..."
gh repo create "$USER_NAME/ShotgunKeys" --public --description "💥 Turn every keystroke into a 12-gauge shotgun blast! Available for macOS, Windows, and Android." --source=. --remote=origin 2>/dev/null || true

git remote set-url origin "https://github.com/$USER_NAME/ShotgunKeys.git" 2>/dev/null || git remote add origin "https://github.com/$USER_NAME/ShotgunKeys.git"

echo "4. Pushing code to GitHub main branch..."
git push -u origin main --force

echo "5. Creating GitHub Release v1.0.0 with all 3 OS packages..."
gh release delete v1.0.0 -y 2>/dev/null || true
gh release create v1.0.0 \
    releases/ShotgunKeys-macOS.zip \
    releases/ShotgunKeys-Windows.zip \
    releases/ShotgunKeys.apk \
    --title "💥 ShotgunKeys v1.0.0 — Multi-Platform Release" \
    --notes "Turn every keystroke into an authentic 12-gauge shotgun blast and Space/Enter into tactical pump-action reloads! Available for macOS, Windows, and Android. Live Web Soundboard: https://$USER_NAME.github.io/ShotgunKeys/"

echo "6. Activating GitHub Pages..."
gh api -X POST "/repos/$USER_NAME/ShotgunKeys/pages" -F "source[branch]=main" -F "source[path]=/docs" 2>/dev/null || true

echo ""
echo "=========================================================="
echo " 🎉 SUCCESS! ShotgunKeys is LIVE on GitHub!"
echo "=========================================================="
echo "⭐ Repository: https://github.com/$USER_NAME/ShotgunKeys"
echo "📦 Releases:   https://github.com/$USER_NAME/ShotgunKeys/releases/tag/v1.0.0"
echo "🌐 Web Site:   https://$USER_NAME.github.io/ShotgunKeys/"
echo "=========================================================="
