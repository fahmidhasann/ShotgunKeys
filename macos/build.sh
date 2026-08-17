#!/bin/bash
set -e

# ==============================================================================
# ShotgunKeys - macOS Build & Release Packaging Script
# ==============================================================================

APP_NAME="ShotgunKeys"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$PROJECT_DIR/build"
DIST_DIR="$PROJECT_DIR/dist"
APP_BUNDLE="$PROJECT_DIR/$APP_NAME.app"
MACOS_DIR="$APP_BUNDLE/Contents/MacOS"
RESOURCES_DIR="$APP_BUNDLE/Contents/Resources"

echo "================================================================="
echo " 💥 Building $APP_NAME for macOS"
echo " Project Directory: $PROJECT_DIR"
echo "================================================================="

# 1. Clean previous build artifacts
echo "🧹 Cleaning previous build and release artifacts..."
rm -rf "$APP_BUNDLE" "$BUILD_DIR" "$DIST_DIR"
mkdir -p "$MACOS_DIR" "$RESOURCES_DIR" "$BUILD_DIR" "$DIST_DIR"

# 2. Ensure sound assets and icon exist
if [ ! -f "$PROJECT_DIR/Assets/shotgun_blast_1.wav" ]; then
    echo "🔊 Generating and mastering sound presets..."
    python3 "$PROJECT_DIR/process_sounds.py" || true
    python3 "$PROJECT_DIR/generate_all_presets.py" || true
fi

if [ ! -f "$PROJECT_DIR/Assets/AppIcon.icns" ]; then
    echo "🎨 Generating AppIcon.icns..."
    python3 "$PROJECT_DIR/generate_icon.py" || true
fi

# 3. Detect Architecture and SDK
ARCH="$(uname -m)"
SDK_PATH="$(xcrun --show-sdk-path)"
echo "⚙️  Host Architecture: $ARCH"
echo "⚙️  macOS SDK: $SDK_PATH"

# 4. Compile Swift sources with optimizations
echo "🔨 Compiling Swift source files with -O optimization..."
swiftc -O \
    -target "${ARCH}-apple-macos13.0" \
    -sdk "$SDK_PATH" \
    -framework Cocoa \
    -framework SwiftUI \
    -framework AVFoundation \
    -framework ApplicationServices \
    "$PROJECT_DIR"/Sources/*.swift \
    -o "$MACOS_DIR/$APP_NAME"

# 5. Copy Info.plist
echo "📋 Packaging Info.plist..."
cp "$PROJECT_DIR/Info.plist" "$APP_BUNDLE/Contents/Info.plist"

# 6. Copy Resources (Sounds, Icons, etc.)
echo "📦 Bundling assets into application bundle..."
if [ -d "$PROJECT_DIR/Assets" ]; then
    # Copy all WAV audio files
    find "$PROJECT_DIR/Assets" -maxdepth 1 -name "*.wav" -exec cp {} "$RESOURCES_DIR/" \;
    # Copy AppIcon.icns
    if [ -f "$PROJECT_DIR/Assets/AppIcon.icns" ]; then
        cp "$PROJECT_DIR/Assets/AppIcon.icns" "$RESOURCES_DIR/"
    fi
fi

# 7. Copy App bundle to build directory for archiving
cp -R "$APP_BUNDLE" "$BUILD_DIR/"

# 8. Ad-hoc Code Signing
echo "🔏 Signing application bundle (Ad-Hoc)..."
codesign --force --deep --sign - "$APP_BUNDLE"
codesign --force --deep --sign - "$BUILD_DIR/$APP_NAME.app"

# 9. Create Distribution Archive (ZIP)
echo "🗜️  Creating release ZIP in dist/..."
(
    cd "$PROJECT_DIR"
    zip -r -q -y "$DIST_DIR/ShotgunKeys-macOS.zip" "$APP_NAME.app"
)

# 10. Verify Bundle & Codesign
echo "🔍 Verifying application integrity..."
codesign --verify --verbose "$APP_BUNDLE"

echo "================================================================="
echo " ✅ Build & Packaging Completed Successfully!"
echo " App Bundle:  $APP_BUNDLE"
echo " Release ZIP: $DIST_DIR/ShotgunKeys-macOS.zip"
echo "================================================================="
