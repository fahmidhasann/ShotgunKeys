# 💥 ShotgunKeys — Multi-Platform Release

<div align="center">

![ShotgunKeys Logo](docs/assets/app_icon.png)

### Turn Every Keystroke into a 12-Gauge Shotgun Blast!
**প্রতিটি কি-ক্লিকে শর্টগান ব্লাস্ট এবং Space/Enter-এ পাম্প-অ্যাকশন রিলোড সাউন্ড!**

[![Platform macOS](https://img.shields.io/badge/Platform-macOS%2013%2B-blue?logo=apple)](https://github.com/fahmidhasann/ShotgunKeys/releases/download/v1.0.0/ShotgunKeys-macOS.zip)
[![Platform Windows](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6?logo=windows)](https://github.com/fahmidhasann/ShotgunKeys/releases/download/v1.0.0/ShotgunKeys-Windows.zip)
[![Platform Android](https://img.shields.io/badge/Platform-Android%20APK-3DDC84?logo=android)](https://github.com/fahmidhasann/ShotgunKeys/releases/download/v1.0.0/ShotgunKeys.apk)
[![License MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Pages](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-orange?logo=github)](https://fahmidhasann.github.io/ShotgunKeys/)

---

### 🌐 [Live Web Soundboard & Download Center](https://fahmidhasann.github.io/ShotgunKeys/)

</div>

---

## ⚡ ডিরেক্ট ডাউনলোড লিংকস (Direct Download Links)

নন-টেকনিক্যাল ইউজারদের জন্য প্রি-বিল্ড ইনস্টলেবল প্যাকেজ:

| অপারেটিং সিস্টেম | ডাউনলোড ফাইল | সাইজ | চালানোর নিয়ম |
| :--- | :--- | :--- | :--- |
| 🍏 **macOS** | [**Download for Mac (.zip)**](https://github.com/fahmidhasann/ShotgunKeys/releases/download/v1.0.0/ShotgunKeys-macOS.zip) | ~১.২ MB | আনজিপ করে `ShotgunKeys.app` ওপেন করুন এবং Accessibility অন করুন। |
| 🪟 **Windows** | [**Download for Windows (.zip)**](https://github.com/fahmidhasann/ShotgunKeys/releases/download/v1.0.0/ShotgunKeys-Windows.zip) | ~৯০০ KB | এক্সট্রাক্ট করে `run.bat` ফাইলে ডাবল ক্লিক করুন। |
| 🤖 **Android** | [**Download APK (.apk)**](https://github.com/fahmidhasann/ShotgunKeys/releases/download/v1.0.0/ShotgunKeys.apk) | ~১.২ MB | ফোনে ইনস্টল করে Accessibility সার্ভিস চালু করুন। |

---

## 🎯 ৭টি অডিও প্রিসেট (Sound Profiles)

1. **🔥 Realistic 12-Gauge (Default)**: Winchester Model 12 & Benelli Nova ১২-গেজ শর্টগানের আসল লাইভ ফিল্ড রেকর্ডিং ব্লাস্ট।
2. **🎯 Tactical Combat (CS / Military)**: স্ন্যাপি, শার্প ও ফাস্ট মিলিটারি শর্টগান ফায়ার এবং দ্রুত স্লাইড র্যাক।
3. **⚡ Heavy Doom (Boomstick)**: ডিপ সাব-বাস যুক্ত থান্ডার্স ডাবল-ব্যারেল ব্লাস্ট এবং ভারী ডুয়াল চেম্বার স্ন্যাপ।
4. **🤫 Silenced Spec-Ops (Stealth / Office)**: সাপ্রেসড নিউমেটিক "থুইপ" পাফ এবং সফট অয়েলড স্লাইড ককিং।
5. **⚛️ Cyberpunk Energy (Plasma / Sci-Fi)**: হাই-এনার্জি প্লাজমা শক ডিসচার্জ এবং ম্যাগনেটিক চার্জিং কয়েল / সারভো রিলোড।
6. **🕹️ 8-Bit Retro Arcade**: রেট্রো আর্কেড সিন্থ ব্লাস্ট এবং চিপটিউন স্লাইড পাম্প সাউন্ড।
7. **📁 Custom Soundpack (User Folder)**: আপনার নিজের যেকোনো পছন্দের `.wav` বা `.mp3` সাউন্ড ড্রপ করে ব্যবহার করার সুবিধা।

---

## 🗂️ মনোরিপো স্ট্রাকচার (Repository Architecture)

```
ShotgunKeys/
├── 🍏 macos/               # macOS Native App (Swift 5.9, SwiftUI, AVFoundation)
│   ├── Sources/            # Native EventTap & Polyphonic Audio Engine
│   └── build.sh            # Production Build & CodeSign Script
│
├── 🪟 windows/             # Windows Portable App (Python, Win32 Hook, System Tray)
│   ├── key_listener.py     # Low-level WH_KEYBOARD_LL hook (Zero-latency)
│   ├── sound_engine.py     # 32-channel polyphonic sound engine with pitch dynamics
│   ├── gui.py              # Modern dark tactical desktop UI
│   ├── run.bat             # 1-Click launcher
│   └── build_exe.bat       # Standalone PyInstaller builder
│
├── 🤖 android/             # Android Native App (Java, SoundPool, Accessibility)
│   ├── app/src/main/       # AccessibilityService, SoundEngine, FloatingWidget
│   ├── build_apk.sh        # Fast standalone APK compiler
│   └── ShotgunKeys.apk     # Standalone signed release APK
│
├── 🌐 docs/                # GitHub Pages Web Landing & Live Soundboard
│   ├── index.html          # Responsive landing page with OS detection
│   ├── style.css           # Cyber-tactical dark design system
│   └── app.js              # In-browser audio tester & keyboard listener
│
├── 📦 releases/            # Pre-packaged binaries ready for GitHub Releases
│   ├── ShotgunKeys-macOS.zip
│   ├── ShotgunKeys-Windows.zip
│   └── ShotgunKeys.apk
│
└── 📱 SOCIAL_POST_TEMPLATE.md  # Facebook/Social Media viral copy-paste captions
```

---

## 🚀 সেটআপ ও ইনস্টলেশন গাইড (Setup Guides)

### 🍏 macOS
1. `ShotgunKeys-macOS.zip` ডাউনলোড করে আনজিপ করুন।
2. `ShotgunKeys.app` কে Applications ফোল্ডারে নিয়ে ওপেন করুন।
3. মেনু বারের 🔥 আইকনে ক্লিক করে **"Grant Permission"** দিয়ে Accessibility পারমিশন অন করুন।

### 🪟 Windows
1. `ShotgunKeys-Windows.zip` ডাউনলোড করে আনজিপ করুন।
2. `run.bat` ফাইলে ডাবল ক্লিক করুন (প্রয়োজনীয় ডিপেনডেন্সি স্বয়ংক্রিয়ভাবে চেক করে অ্যাপ ওপেন হবে)।
3. সিস্টেম ট্রে থেকে মিনিমাইজ, সাউন্ড মিউট বা প্রিসেট বদলানো যাবে।

### 🤖 Android
1. `ShotgunKeys.apk` ডাউনলোড করে আপনার অ্যান্ড্রয়েড ফোনে ইনস্টল করুন।
2. অ্যাপ ওপেন করে **"Enable Accessibility"** বাটনে ট্যাপ করে `ShotgunKeys Typing Sound Service` অন করে দিন।
3. এখন যেকোনো কীবোর্ডে (GBoard, SwiftKey, Samsung Keyboard, WhatsApp, ইত্যাদি) টাইপ করলেই শর্টগান সাউন্ড বাজবে!

---

## 📱 সোশ্যাল মিডিয়ায় শেয়ার করার ক্যাপশন
ফেসবুক বা অন্যান্য সোশ্যাল মিডিয়ায় পোস্ট করার জন্য সম্পূর্ণ তৈরি ক্যাপশন ও টেক্সট পাওয়া যাবে [`SOCIAL_POST_TEMPLATE.md`](SOCIAL_POST_TEMPLATE.md) ফাইলে।

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
