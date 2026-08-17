#!/usr/bin/env bash
set -e

# ==========================================
# ShotgunKeys Android Standalone Build Script
# Builds signed release APK without Android Studio
# ==========================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_DIR="/tmp/android_tools"
BUILD_DIR="$SCRIPT_DIR/build"
RELEASE_DIR="$SCRIPT_DIR/release"
CLASSES_DIR="$BUILD_DIR/classes"

echo "=== [1/6] Preparing Build Environment ==="
mkdir -p "$BUILD_DIR" "$RELEASE_DIR" "$CLASSES_DIR" "$TOOLS_DIR"

# Ensure tools are present
if [ ! -f "$TOOLS_DIR/android.jar" ]; then
  echo "Downloading minimal android.jar..."
  curl -L -s -o "$TOOLS_DIR/android.jar" https://raw.githubusercontent.com/Sable/android-platforms/master/android-28/android.jar
fi

if [ ! -f "$TOOLS_DIR/dx.jar" ]; then
  echo "Downloading minimal dalvik-dx..."
  curl -L -s -o "$TOOLS_DIR/dx.jar" https://repo1.maven.org/maven2/com/jakewharton/android/repackaged/dalvik-dx/14.0.0_r21/dalvik-dx-14.0.0_r21.jar
fi

if [ ! -f "$TOOLS_DIR/aapt" ]; then
  if [ ! -f "$TOOLS_DIR/apktool.jar" ]; then
    echo "Downloading apktool..."
    curl -L -s -o "$TOOLS_DIR/apktool.jar" https://github.com/iBotPeaches/Apktool/releases/download/v2.9.3/apktool_2.9.3.jar
  fi
  unzip -p "$TOOLS_DIR/apktool.jar" prebuilt/macosx/aapt_64 > "$TOOLS_DIR/aapt"
  chmod +x "$TOOLS_DIR/aapt"
fi

echo "=== [2/6] Generating R.java with AAPT ==="
"$TOOLS_DIR/aapt" package -f -m \
  -J "$SCRIPT_DIR/app/src/main/java" \
  -M "$SCRIPT_DIR/app/src/main/AndroidManifest.xml" \
  -S "$SCRIPT_DIR/app/src/main/res" \
  -I "$TOOLS_DIR/android.jar"

echo "=== [3/6] Compiling Java Source Files ==="
javac -source 8 -target 8 \
  -cp "$TOOLS_DIR/android.jar" \
  -d "$CLASSES_DIR" \
  "$SCRIPT_DIR"/app/src/main/java/com/shotgunkeys/app/*.java

echo "=== [4/6] Converting Classes to Dalvik DEX ==="
java -cp "$TOOLS_DIR/dx.jar" com.android.dx.command.Main \
  --dex \
  --output="$BUILD_DIR/classes.dex" \
  "$CLASSES_DIR"

echo "=== [5/6] Packaging Resources and DEX into APK ==="
rm -f "$BUILD_DIR/unaligned.apk"
"$TOOLS_DIR/aapt" package -f \
  -M "$SCRIPT_DIR/app/src/main/AndroidManifest.xml" \
  -S "$SCRIPT_DIR/app/src/main/res" \
  -I "$TOOLS_DIR/android.jar" \
  -F "$BUILD_DIR/unaligned.apk"

cd "$BUILD_DIR"
"$TOOLS_DIR/aapt" add unaligned.apk classes.dex
cd "$SCRIPT_DIR"

echo "=== [6/6] Signing Release APK with Keystore ==="
if [ ! -f "$BUILD_DIR/release.keystore" ]; then
  keytool -genkeypair -v \
    -keystore "$BUILD_DIR/release.keystore" \
    -alias shotgunkeys \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000 \
    -storepass shotgun123 \
    -keypass shotgun123 \
    -dname "CN=ShotgunKeys, OU=Mobile, O=ShotgunKeys, L=Global, ST=Global, C=US"
fi

rm -f "$RELEASE_DIR/ShotgunKeys.apk" "$SCRIPT_DIR/ShotgunKeys.apk"

jarsigner -verbose \
  -sigalg SHA256withRSA \
  -digestalg SHA-256 \
  -keystore "$BUILD_DIR/release.keystore" \
  -storepass shotgun123 \
  -keypass shotgun123 \
  -signedjar "$RELEASE_DIR/ShotgunKeys.apk" \
  "$BUILD_DIR/unaligned.apk" \
  shotgunkeys

cp "$RELEASE_DIR/ShotgunKeys.apk" "$SCRIPT_DIR/ShotgunKeys.apk"

echo "=== Verifying APK Signature ==="
jarsigner -verify "$RELEASE_DIR/ShotgunKeys.apk"

echo ""
echo "============================================================"
echo " BUILD SUCCESSFUL!"
echo " Signed standalone APK generated at:"
echo " 1) $RELEASE_DIR/ShotgunKeys.apk"
echo " 2) $SCRIPT_DIR/ShotgunKeys.apk"
echo "============================================================"
