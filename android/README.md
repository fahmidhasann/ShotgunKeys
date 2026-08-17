# 💥 ShotgunKeys for Android 📱
> **Turn every tap on your Android keyboard into a thunderous 12-gauge shotgun blast!**  
> *আপনার অ্যান্ড্রয়েড কীবোর্ডে টাইপ করার সাথে সাথেই রিয়েল শটগান ব্লাস্ট ও রিলোড সাউন্ড শুনুন!*

[![Platform](https://img.shields.io/badge/Platform-Android_5.0+_(API_21+)-green.svg)](https://android.com)
[![Build](https://img.shields.io/badge/Build-Standalone_APK-orange.svg)](#-how-to-install--ব্যবহারের-নিয়ম)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Audio](https://img.shields.io/badge/Engine-SoundPool_Multi--Stream-red.svg)](#-features--বৈশিষ্ট্যসমূহ)

---

## 📥 Standalone APK Download (সরাসরি এপিকে ডাউনলোড)

The standalone, fully signed, ready-to-install `.apk` file is located right in this repository:

- 📦 **Direct APK File:** [`ShotgunKeys.apk`](./ShotgunKeys.apk) *(1.2 MB)*
- 📦 **Release Directory:** [`release/ShotgunKeys.apk`](./release/ShotgunKeys.apk)

---

## 🇧🇩 বাংলা নির্দেশিকা (Bengali Guide)

### 🌟 ShotgunKeys কী?
**ShotgunKeys** হলো একটি ট্যাকটিক্যাল অ্যান্ড্রয়েড অ্যাপ যা ব্যাকগ্রাউন্ডে চলে এবং যেকোনো অ্যাপে (GBoard, WhatsApp, Messenger, Chrome, SMS, Facebook, ইত্যাদি) টাইপ করার সাথে সাথে রিয়েল শটগানের ফায়ার ব্লাস্ট এবং স্পেস/এন্টারে পাম্প রিলোড সাউন্ড প্লে করে!

### 🚀 যেভাবে ইনস্টল ও চালু করবেন:
1. **APK ডাউনলোড ও ইনস্টল করুন:**
   - [`ShotgunKeys.apk`](./ShotgunKeys.apk) ফাইলটি আপনার ফোনে ট্রান্সফার করে ওপেন করুন এবং **Install** দিন। (প্রয়োজনে *Install unknown apps* পারমিশন অন করুন)।
2. **অ্যাপ ওপেন করুন:**
   - অ্যাপ ওপেন করার পর হোম স্ক্রিনে থাকা **"ENABLE ACCESSIBILITY"** বাটনে ট্যাপ করুন।
3. **অ্যাক্সেসিবিলিটি পারমিশন দিন:**
   - ফোনের Accessibility সেটিংস খুলে যাবে। সেখানে **ShotgunKeys** খুঁজে বের করে **ON** করে দিন।
4. **মজা নিন:**
   - এবার যেকোনো অ্যাপে গিয়ে যেকোনো মেসেজ টাইপ করুন — প্রতিটা লেটারে শুনবেন পাওয়ারফুল শটগান ব্লাস্ট এবং স্পেস বা নতুন লাইনে চাপলে শুনবেন মেকানিক্যাল পাম্প রিলোড!

---

## ⚡ Key Features (প্রধান সুবিধাসমূহ)

| Feature | Description |
| :--- | :--- |
| 💥 **Zero-Latency SoundPool Engine** | Instant multi-channel audio playback with zero audio lag, even during ultra-fast typing. |
| 🎛️ **6 Premium Sound Presets** | **Realistic 12-Gauge**, **Tactical Shotgun**, **Doom Super Shotgun**, **Silenced Shotgun**, **Cyberpunk Railgun**, and **8-Bit Arcade**. |
| 🌐 **Global Accessibility Typing Detection** | Works seamlessly system-wide across all virtual keyboards (GBoard, SwiftKey, Samsung Keyboard, etc.) and hardware keyboards. |
| 🔄 **Space & Enter Auto-Reload** | Automatically cycles shotgun pump chamber sound whenever Space, Enter, or Return is pressed. |
| 🎲 **Natural Micro-Dynamics** | Organic pitch (±3%) and volume variations so consecutive keystrokes never sound robotic. |
| 📳 **Tactical Haptic Feedback** | Crisp haptic vibration pulses matched to gunshot blast recoil and double pump action. |
| 📊 **Live Combat Metrics** | Real-time counters for **Shots Fired** and **Pumps & Reloads** with instant reset. |
| 🪟 **Floating Draggable Widget** | Optional overlay trigger badge that floats over games and apps for quick manual firing. |
| 🎚️ **Master Volume Control** | Precise 0% to 100% volume slider right inside the main tactical dashboard. |

---

## 🔊 Sound Presets (সাউন্ড প্রিসেটসমূহ)

1. **Realistic 12-Gauge (রিয়েল ১২-গেজ)**: Authentic heavy 12-gauge pump shotgun blast with metallic brass ejection.
2. **Tactical Shotgun (ট্যাকটিক্যাল শটগান)**: Crisp military breach gunshot with swift mechanical pump slide.
3. **Doom Super Shotgun (ডুম সুপার শটগান)**: Devastating double-barrel blast with industrial mechanical reload.
4. **Silenced Shotgun (সাইলেন্সড শটগান)**: Subdued tactical suppressed blast for quiet stealth typing.
5. **Cyberpunk Railgun (সাইবারপাঙ্ক রেইলগান)**: Futuristic plasma discharge with high-voltage capacitor recharge.
6. **8-Bit Arcade (৮-বিট আর্কেড)**: Retro arcade sound effects and crunchy 80s chiptune pump action.

---

## 🛠️ Project Structure (প্রজেক্ট স্ট্রাকচার)

```
ShotgunKeys-Android/
├── ShotgunKeys.apk                 # 🚀 Standalone signed installable APK (1.2 MB)
├── release/
│   └── ShotgunKeys.apk             # Release package directory
├── build_apk.sh                    # ⚡ Instant standalone build script (no heavy Android Studio UI required)
├── gradlew / gradlew.bat           # Standard Gradle wrapper
├── build.gradle / settings.gradle  # Gradle build scripts
├── app/
│   ├── build.gradle                # App module configuration
│   └── src/main/
│       ├── AndroidManifest.xml     # App manifest & permissions
│       ├── java/com/shotgunkeys/app/
│       │   ├── MainActivity.java                # Dark Tactical Dashboard & Soundboard
│       │   ├── SoundEngine.java                 # Multi-stream SoundPool audio engine
│       │   ├── ShotgunAccessibilityService.java # Global typing listener
│       │   ├── FloatingWidgetService.java       # Floating trigger overlay
│       │   ├── SettingsManager.java             # SharedPreferences manager
│       │   └── SoundPreset.java                 # 6 preset definitions & resources
│       └── res/
│           ├── layout/              # Tactical dark UI layouts
│           ├── raw/                 # All 26 optimized WAV audio samples
│           ├── mipmap-*/            # HD app launcher icons (MDPI to XXXHDPI)
│           ├── drawable/            # Tactical neon buttons & cards
│           ├── values/              # Strings, colors, and dark theme
│           └── xml/                 # Accessibility service config
```

---

## 🏗️ How to Build Standalone APK (কীভাবে নিজে বিল্ড করবেন)

You can build the complete signed release APK in **2 seconds** without installing gigabytes of Android Studio UI:

```bash
# 1. Clone or open the repository:
cd /Users/fahmidhasantaohid/Desktop/ShotgunKeys-Android

# 2. Run the standalone build script:
./build_apk.sh
```

Or using Gradle:
```bash
./gradlew assembleRelease
```

The compiled and signed APK will be output to:
- `ShotgunKeys.apk`
- `release/ShotgunKeys.apk`

---

## 🔒 Permissions & Privacy (পারমিশন ও গোপনীয়তা)

- **Accessibility Service (`BIND_ACCESSIBILITY_SERVICE`)**: Used solely for detecting key taps to trigger local sound playback in real-time. **No text or personal data is ever recorded, stored, or transmitted.**
- **Vibrate (`android.permission.VIBRATE`)**: Used to provide haptic feedback when firing.
- **Overlay (`SYSTEM_ALERT_WINDOW`)**: Optional permission for displaying the draggable floating trigger badge.
- **100% Offline & Private**: ShotgunKeys contains no ads, no trackers, and requires no internet access.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
Created with ❤️ by Fahmid Hasan Taohid.
