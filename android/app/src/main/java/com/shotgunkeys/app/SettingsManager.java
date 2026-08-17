package com.shotgunkeys.app;

import android.content.Context;
import android.content.SharedPreferences;

public class SettingsManager {
    private static final String PREF_NAME = "shotgunkeys_prefs";
    
    private static final String KEY_PRESET = "selected_preset";
    private static final String KEY_VOLUME = "master_volume";
    private static final String KEY_MICRO_DYNAMICS = "micro_dynamics_enabled";
    private static final String KEY_SPACE_RELOAD = "space_reload_enabled";
    private static final String KEY_HAPTICS = "haptics_enabled";
    private static final String KEY_FLOATING_WIDGET = "floating_widget_enabled";
    private static final String KEY_SHOTS_COUNT = "stat_shots_count";
    private static final String KEY_RELOADS_COUNT = "stat_reloads_count";

    private static SettingsManager instance;
    private final SharedPreferences prefs;

    public interface OnSettingsChangeListener {
        void onSettingChanged(String key);
    }

    private SettingsManager(Context context) {
        this.prefs = context.getApplicationContext().getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
    }

    public static synchronized SettingsManager getInstance(Context context) {
        if (instance == null) {
            instance = new SettingsManager(context);
        }
        return instance;
    }

    public SoundPreset getPreset() {
        String presetId = prefs.getString(KEY_PRESET, SoundPreset.REALISTIC.getId());
        return SoundPreset.fromId(presetId);
    }

    public void setPreset(SoundPreset preset) {
        prefs.edit().putString(KEY_PRESET, preset.getId()).apply();
    }

    public float getVolume() {
        return prefs.getFloat(KEY_VOLUME, 0.85f);
    }

    public void setVolume(float volume) {
        prefs.edit().putFloat(KEY_VOLUME, Math.max(0.0f, Math.min(1.0f, volume))).apply();
    }

    public boolean isMicroDynamicsEnabled() {
        return prefs.getBoolean(KEY_MICRO_DYNAMICS, true);
    }

    public void setMicroDynamicsEnabled(boolean enabled) {
        prefs.edit().putBoolean(KEY_MICRO_DYNAMICS, enabled).apply();
    }

    public boolean isSpaceReloadEnabled() {
        return prefs.getBoolean(KEY_SPACE_RELOAD, true);
    }

    public void setSpaceReloadEnabled(boolean enabled) {
        prefs.edit().putBoolean(KEY_SPACE_RELOAD, enabled).apply();
    }

    public boolean isHapticsEnabled() {
        return prefs.getBoolean(KEY_HAPTICS, true);
    }

    public void setHapticsEnabled(boolean enabled) {
        prefs.edit().putBoolean(KEY_HAPTICS, enabled).apply();
    }

    public boolean isFloatingWidgetEnabled() {
        return prefs.getBoolean(KEY_FLOATING_WIDGET, false);
    }

    public void setFloatingWidgetEnabled(boolean enabled) {
        prefs.edit().putBoolean(KEY_FLOATING_WIDGET, enabled).apply();
    }

    public long getShotsFiredCount() {
        return prefs.getLong(KEY_SHOTS_COUNT, 0L);
    }

    public synchronized void incrementShotsFired() {
        long current = getShotsFiredCount();
        prefs.edit().putLong(KEY_SHOTS_COUNT, current + 1).apply();
    }

    public long getReloadsCount() {
        return prefs.getLong(KEY_RELOADS_COUNT, 0L);
    }

    public synchronized void incrementReloads() {
        long current = getReloadsCount();
        prefs.edit().putLong(KEY_RELOADS_COUNT, current + 1).apply();
    }

    public void resetStats() {
        prefs.edit().putLong(KEY_SHOTS_COUNT, 0L).putLong(KEY_RELOADS_COUNT, 0L).apply();
    }
}
