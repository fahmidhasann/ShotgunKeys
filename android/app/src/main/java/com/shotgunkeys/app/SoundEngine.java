package com.shotgunkeys.app;

import android.content.Context;
import android.media.AudioAttributes;
import android.media.AudioManager;
import android.media.SoundPool;
import android.os.Build;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.util.Log;

import java.util.HashMap;
import java.util.Map;
import java.util.Random;

public class SoundEngine {
    private static final String TAG = "SoundEngine";
    private static final int MAX_STREAMS = 16;

    private static SoundEngine instance;
    private final Context context;
    private final SettingsManager settings;
    private final SoundPool soundPool;
    private final Vibrator vibrator;
    private final Random random = new Random();

    // Map from raw resource ID -> loaded SoundPool sound ID
    private final Map<Integer, Integer> soundIdMap = new HashMap<>();
    private final Map<Integer, Boolean> soundLoadedMap = new HashMap<>();

    private int lastBlastIndex = -1;
    private int lastReloadIndex = -1;

    public interface SoundEventListener {
        void onSoundPlayed(boolean isBlast);
    }

    private SoundEventListener soundEventListener;

    private SoundEngine(Context context) {
        this.context = context.getApplicationContext();
        this.settings = SettingsManager.getInstance(this.context);
        this.vibrator = (Vibrator) this.context.getSystemService(Context.VIBRATOR_SERVICE);

        AudioAttributes audioAttributes = new AudioAttributes.Builder()
                .setUsage(AudioAttributes.USAGE_GAME)
                .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                .setFlags(AudioAttributes.FLAG_AUDIBILITY_ENFORCED)
                .build();

        this.soundPool = new SoundPool.Builder()
                .setMaxStreams(MAX_STREAMS)
                .setAudioAttributes(audioAttributes)
                .build();

        this.soundPool.setOnLoadCompleteListener(new SoundPool.OnLoadCompleteListener() {
            @Override
            public void onLoadComplete(SoundPool soundPool, int sampleId, int status) {
                if (status == 0) {
                    soundLoadedMap.put(sampleId, true);
                } else {
                    Log.e(TAG, "Failed to load sample ID: " + sampleId);
                }
            }
        });

        preloadAllSounds();
    }

    public static synchronized SoundEngine getInstance(Context context) {
        if (instance == null) {
            instance = new SoundEngine(context);
        }
        return instance;
    }

    public void setSoundEventListener(SoundEventListener listener) {
        this.soundEventListener = listener;
    }

    private void preloadAllSounds() {
        for (SoundPreset preset : SoundPreset.values()) {
            for (int resId : preset.getBlastResIds()) {
                loadResource(resId);
            }
            for (int resId : preset.getReloadResIds()) {
                loadResource(resId);
            }
        }
    }

    private int loadResource(int resId) {
        if (!soundIdMap.containsKey(resId)) {
            int soundId = soundPool.load(context, resId, 1);
            soundIdMap.put(resId, soundId);
            soundLoadedMap.put(soundId, false);
            return soundId;
        }
        return soundIdMap.get(resId);
    }

    public void playBlast() {
        SoundPreset preset = settings.getPreset();
        int[] blastIds = preset.getBlastResIds();
        if (blastIds == null || blastIds.length == 0) return;

        // Choose next variation
        int index = 0;
        if (blastIds.length > 1) {
            do {
                index = random.nextInt(blastIds.length);
            } while (index == lastBlastIndex && blastIds.length > 2);
        }
        lastBlastIndex = index;

        int resId = blastIds[index];
        playSound(resId, true);

        // Stats & Notification
        settings.incrementShotsFired();
        if (soundEventListener != null) {
            soundEventListener.onSoundPlayed(true);
        }
    }

    public void playReload() {
        SoundPreset preset = settings.getPreset();
        int[] reloadIds = preset.getReloadResIds();
        if (reloadIds == null || reloadIds.length == 0) return;

        int index = 0;
        if (reloadIds.length > 1) {
            do {
                index = random.nextInt(reloadIds.length);
            } while (index == lastReloadIndex && reloadIds.length > 2);
        }
        lastReloadIndex = index;

        int resId = reloadIds[index];
        playSound(resId, false);

        // Stats & Notification
        settings.incrementReloads();
        if (soundEventListener != null) {
            soundEventListener.onSoundPlayed(false);
        }
    }

    private void playSound(int resId, boolean isBlast) {
        Integer soundId = soundIdMap.get(resId);
        if (soundId == null) {
            soundId = loadResource(resId);
        }

        float baseVolume = settings.getVolume();
        float leftVol = baseVolume;
        float rightVol = baseVolume;
        float rate = 1.0f;

        if (settings.isMicroDynamicsEnabled()) {
            // Subtle pitch modulation (0.97 - 1.03)
            float pitchOffset = (random.nextFloat() - 0.5f) * 0.06f;
            rate = Math.max(0.85f, Math.min(1.15f, 1.0f + pitchOffset));

            // Subtle gain modulation (±3%)
            float volOffset = (random.nextFloat() - 0.5f) * 0.06f;
            float variedVol = Math.max(0.1f, Math.min(1.0f, baseVolume + volOffset));
            leftVol = variedVol;
            rightVol = variedVol;
        }

        soundPool.play(soundId, leftVol, rightVol, 1, 0, rate);

        // Haptic feedback
        if (settings.isHapticsEnabled() && vibrator != null && vibrator.hasVibrator()) {
            try {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    if (isBlast) {
                        vibrator.vibrate(VibrationEffect.createOneShot(35, VibrationEffect.DEFAULT_AMPLITUDE));
                    } else {
                        // Tactical double pump vibration
                        long[] timings = {0, 25, 40, 30};
                        int[] amplitudes = {0, 180, 0, 220};
                        vibrator.vibrate(VibrationEffect.createWaveform(timings, amplitudes, -1));
                    }
                } else {
                    vibrator.vibrate(isBlast ? 35 : 70);
                }
            } catch (Exception e) {
                Log.w(TAG, "Haptics error: " + e.getMessage());
            }
        }
    }

    public void release() {
        soundPool.release();
    }
}
