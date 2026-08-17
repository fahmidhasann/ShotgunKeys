// --- ShotgunKeys Interactive Web Engine --- //

document.addEventListener('DOMContentLoaded', () => {
    // 1. Detect User OS
    detectUserOS();

    // 2. Setup Audio Soundboard
    setupSoundboard();

    // 3. Setup Global Web Keyboard Listener (Type anywhere on page to test!)
    setupWebKeyboardListener();
});

// Sound Definitions
const SOUND_PRESETS = {
    realistic: {
        title: "Realistic 12-Gauge (Default)",
        desc: "Winchester Model 12 & Benelli Nova ১২-গেজ শর্টগানের আসল লাইভ রেকর্ডিং ব্লাস্ট।",
        blasts: ["assets/shotgun_blast_1.wav", "assets/shotgun_blast_2.wav", "assets/shotgun_blast_3.wav", "assets/shotgun_blast_4.wav"],
        reloads: ["assets/shotgun_reload_1.wav", "assets/shotgun_reload_2.wav"]
    },
    tactical: {
        title: "Tactical Combat (Military)",
        desc: "শার্প ও স্ন্যাপি মিলিটারি ট্যাকটিক্যাল শর্টগান ফায়ার এবং দ্রুত স্লাইড র্যাক।",
        blasts: ["assets/tactical_blast_1.wav", "assets/tactical_blast_2.wav", "assets/tactical_blast_3.wav"],
        reloads: ["assets/tactical_reload_1.wav", "assets/tactical_reload_2.wav"]
    },
    doom: {
        title: "Heavy Doom (Boomstick)",
        desc: "ডিপ সাব-বাস যুক্ত থান্ডার্স ডাবল-ব্যারেল ব্লাস্ট এবং ভারী চেম্বার স্ন্যাপ।",
        blasts: ["assets/doom_blast_1.wav", "assets/doom_blast_2.wav"],
        reloads: ["assets/doom_reload_1.wav", "assets/doom_reload_2.wav"]
    },
    silenced: {
        title: "Silenced Spec-Ops (Stealth)",
        desc: "সাপ্রেসড নিউমেটিক 'থুইপ' পাফ এবং সফট অয়েলড স্লাইড ককিং।",
        blasts: ["assets/silenced_blast_1.wav", "assets/silenced_blast_2.wav"],
        reloads: ["assets/silenced_reload_1.wav", "assets/silenced_reload_2.wav"]
    },
    cyberpunk: {
        title: "Cyberpunk Plasma (Sci-Fi)",
        desc: "হাই-এনার্জি প্লাজমা শক ডিসচার্জ এবং ম্যাগনেটিক চার্জিং সারভো রিলোড।",
        blasts: ["assets/cyber_blast_1.wav", "assets/cyber_blast_2.wav"],
        reloads: ["assets/cyber_reload_1.wav", "assets/cyber_reload_2.wav"]
    },
    arcade: {
        title: "8-Bit Retro Arcade",
        desc: "রেট্রো আর্কেড সিন্থ ব্লাস্ট এবং চিপটিউন স্লাইড পাম্প সাউন্ড।",
        blasts: ["assets/arcade_blast.wav"],
        reloads: ["assets/arcade_reload.wav"]
    }
};

let currentPresetKey = 'realistic';
let blastCount = 0;
let reloadCount = 0;

// Audio Cache
const audioPool = {};

function getCachedAudio(src) {
    if (!audioPool[src]) {
        audioPool[src] = [];
    }
    // Find an idle audio element or create a new one
    let audio = audioPool[src].find(a => a.paused || a.ended);
    if (!audio) {
        audio = new Audio(src);
        audioPool[src].push(audio);
    }
    return audio;
}

function playSound(soundArray) {
    if (!soundArray || soundArray.length === 0) return;
    const randomSrc = soundArray[Math.floor(Math.random() * soundArray.length)];
    try {
        const audio = getCachedAudio(randomSrc);
        audio.currentTime = 0;
        audio.volume = 0.85;
        // Pitch variation (micro-dynamics)
        audio.playbackRate = 0.96 + Math.random() * 0.08;
        audio.play().catch(e => {
            console.log("Audio autoplay prevented - user must interact first");
        });
    } catch (e) {
        console.error(e);
    }
}

function playBlast() {
    const preset = SOUND_PRESETS[currentPresetKey];
    if (preset) {
        playSound(preset.blasts);
        blastCount++;
        const el = document.getElementById('webBlastCount');
        if (el) el.textContent = blastCount;
    }
}

function playReload() {
    const preset = SOUND_PRESETS[currentPresetKey];
    if (preset) {
        playSound(preset.reloads);
        reloadCount++;
        const el = document.getElementById('webReloadCount');
        if (el) el.textContent = reloadCount;
    }
}

// Setup Soundboard UI
function setupSoundboard() {
    const tabs = document.querySelectorAll('.preset-tab');
    const titleEl = document.getElementById('activePresetTitle');
    const descEl = document.getElementById('activePresetDesc');
    const btnBlast = document.getElementById('btnWebBlast');
    const btnReload = document.getElementById('btnWebReload');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            const presetKey = tab.getAttribute('data-preset');
            currentPresetKey = presetKey;

            const preset = SOUND_PRESETS[presetKey];
            if (preset) {
                if (titleEl) titleEl.textContent = preset.title;
                if (descEl) descEl.textContent = preset.desc;
                // Preview sound on click
                playBlast();
            }
        });
    });

    if (btnBlast) {
        btnBlast.addEventListener('click', () => {
            playBlast();
            animateButton(btnBlast);
        });
    }

    if (btnReload) {
        btnReload.addEventListener('click', () => {
            playReload();
            animateButton(btnReload);
        });
    }
}

function animateButton(btn) {
    btn.style.transform = 'scale(0.95)';
    setTimeout(() => {
        btn.style.transform = '';
    }, 120);
}

// Global Web Keyboard Listener
function setupWebKeyboardListener() {
    window.addEventListener('keydown', (e) => {
        // Prevent typing if inside an input field
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

        if (e.code === 'Space' || e.code === 'Enter') {
            e.preventDefault();
            playReload();
            const btn = document.getElementById('btnWebReload');
            if (btn) animateButton(btn);
        } else {
            playBlast();
            const btn = document.getElementById('btnWebBlast');
            if (btn) animateButton(btn);
        }
    });
}

// OS Detection Logic
function detectUserOS() {
    const userAgent = window.navigator.userAgent || window.navigator.vendor || window.opera;
    const platform = window.navigator.platform || '';

    const detectedEl = document.getElementById('detectedOsName');
    const cardMac = document.getElementById('cardMac');
    const cardWindows = document.getElementById('cardWindows');
    const cardAndroid = document.getElementById('cardAndroid');

    let osName = "Universal";
    let targetCard = null;

    if (/android/i.test(userAgent)) {
        osName = "Android Mobile (APK)";
        targetCard = cardAndroid;
    } else if (/Mac|MacIntel|MacPPC|Mac68K/i.test(platform) || /Macintosh/i.test(userAgent)) {
        // Check if iOS
        if (/iPhone|iPad|iPod/i.test(userAgent)) {
            osName = "iOS (iPhone/iPad)";
        } else {
            osName = "macOS (Apple Silicon & Intel)";
            targetCard = cardMac;
        }
    } else if (/Win32|Win64|Windows|WinCE/i.test(platform) || /Windows/i.test(userAgent)) {
        osName = "Windows 10 / 11";
        targetCard = cardWindows;
    } else if (/Linux/i.test(platform)) {
        osName = "Linux (Python / Android)";
    }

    if (detectedEl) {
        detectedEl.textContent = osName;
    }

    if (targetCard) {
        targetCard.classList.add('highlighted-os');
    }
}
