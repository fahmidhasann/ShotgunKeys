#!/usr/bin/env bash
set -e

# ==============================================================================
# ShotgunKeys Android Standalone Build Script
# Builds fully compliant, signed & zipaligned release APK (v1 + v2 + v3 schemes)
# Tested on Android 5.0 to Android 15 & Windows Subsystem for Android (WSA)
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TOOLS_DIR="/tmp/android_tools"
BUILD_DIR="$SCRIPT_DIR/build"
RELEASE_DIR="$SCRIPT_DIR/release"
CLASSES_DIR="$BUILD_DIR/classes"

echo "============================================================"
echo " 💥 Building ShotgunKeys Android Release APK"
echo " Working Directory: $SCRIPT_DIR"
echo "============================================================"

# 1. Prepare directories
echo "=== [1/6] Preparing Build Environment & Dependencies ==="
mkdir -p "$BUILD_DIR" "$RELEASE_DIR" "$CLASSES_DIR" "$TOOLS_DIR"

if [ ! -f "$TOOLS_DIR/android.jar" ]; then
  echo "Downloading Android SDK platform library (API 30)..."
  curl -L -s -o "$TOOLS_DIR/android.jar" https://raw.githubusercontent.com/Sable/android-platforms/master/android-30/android.jar
fi

if [ ! -f "$TOOLS_DIR/dx.jar" ]; then
  echo "Downloading Dalvik DX compiler..."
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

if [ ! -f "$TOOLS_DIR/uber-apk-signer.jar" ]; then
  echo "Downloading Uber-APK-Signer (v2/v3 Signing & ZipAlign engine)..."
  curl -L -s -o "$TOOLS_DIR/uber-apk-signer.jar" https://github.com/patrickfav/uber-apk-signer/releases/download/v1.3.0/uber-apk-signer-1.3.0.jar
fi

# 2. AAPT R.java generation
echo "=== [2/6] Generating R.java with AAPT ==="
"$TOOLS_DIR/aapt" package -f -m \
  -J "$SCRIPT_DIR/app/src/main/java" \
  -M "$SCRIPT_DIR/app/src/main/AndroidManifest.xml" \
  -S "$SCRIPT_DIR/app/src/main/res" \
  -I "$TOOLS_DIR/android.jar"

# 3. Compile Java Source Files
echo "=== [3/6] Compiling Java Source Files ==="
rm -rf "$CLASSES_DIR"/*
javac -source 8 -target 8 \
  -cp "$TOOLS_DIR/android.jar" \
  -d "$CLASSES_DIR" \
  "$SCRIPT_DIR"/app/src/main/java/com/shotgunkeys/app/*.java

# 4. Dalvik DEX generation
echo "=== [4/6] Converting Classes to Dalvik DEX ==="
java -cp "$TOOLS_DIR/dx.jar" com.android.dx.command.Main \
  --dex \
  --output="$BUILD_DIR/classes.dex" \
  "$CLASSES_DIR"

# 5. Packaging APK
echo "=== [5/6] Packaging Resources and DEX into APK ==="
rm -f "$BUILD_DIR/ShotgunKeys-unsigned.apk"
"$TOOLS_DIR/aapt" package -f \
  -M "$SCRIPT_DIR/app/src/main/AndroidManifest.xml" \
  -S "$SCRIPT_DIR/app/src/main/res" \
  -I "$TOOLS_DIR/android.jar" \
  -F "$BUILD_DIR/ShotgunKeys-unsigned.apk"

cd "$BUILD_DIR"
"$TOOLS_DIR/aapt" add ShotgunKeys-unsigned.apk classes.dex
cd "$SCRIPT_DIR"

# 6. Signing & 4-Byte ZipAligning
echo "=== [6/6] Signing & 4-Byte Zipaligning with Keystore ==="
if [ ! -f "$BUILD_DIR/release.keystore" ]; then
  echo "Generating release keystore..."
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

rm -f "$RELEASE_DIR"/*

java -jar "$TOOLS_DIR/uber-apk-signer.jar" \
  -a "$BUILD_DIR/ShotgunKeys-unsigned.apk" \
  --ks "$BUILD_DIR/release.keystore" \
  --ksAlias shotgunkeys \
  --ksPass shotgun123 \
  --ksKeyPass shotgun123 \
  -o "$RELEASE_DIR" \
  --verbose

# Standardize output file name
FINAL_SIGNED_APK="$(ls -1 "$RELEASE_DIR"/*-aligned-signed.apk 2>/dev/null | head -n 1 || true)"

if [ -n "$FINAL_SIGNED_APK" ] && [ -f "$FINAL_SIGNED_APK" ]; then
  cp "$FINAL_SIGNED_APK" "$RELEASE_DIR/ShotgunKeys.apk"
  cp "$FINAL_SIGNED_APK" "$SCRIPT_DIR/ShotgunKeys.apk"
  if [ -d "$ROOT_DIR/releases" ]; then
    cp "$FINAL_SIGNED_APK" "$ROOT_DIR/releases/ShotgunKeys.apk"
  fi
  # Clean intermediate files
  rm -f "$RELEASE_DIR"/*-aligned-signed.apk*
fi

echo "=== Verifying Final APK Signatures & Alignment ==="
java -jar "$TOOLS_DIR/uber-apk-signer.jar" \
  --onlyVerify \
  --verbose \
  -a "$SCRIPT_DIR/ShotgunKeys.apk"

echo ""
echo "============================================================"
echo " 🎉 ANDROID APK BUILD SUCCESSFUL!"
echo " Signed and zipaligned APK (v1, v2, v3) is ready at:"
echo " 1) $RELEASE_DIR/ShotgunKeys.apk"
echo " 2) $SCRIPT_DIR/ShotgunKeys.apk"
echo " 3) $ROOT_DIR/releases/ShotgunKeys.apk"
echo "============================================================"
