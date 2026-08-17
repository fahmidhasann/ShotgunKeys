package com.shotgunkeys.app;

import android.accessibilityservice.AccessibilityService;
import android.content.Intent;
import android.os.SystemClock;
import android.util.Log;
import android.view.KeyEvent;
import android.view.accessibility.AccessibilityEvent;

import java.util.List;

public class ShotgunAccessibilityService extends AccessibilityService {
    private static final String TAG = "ShotgunAccessibility";
    
    private static boolean isServiceRunning = false;
    private SoundEngine soundEngine;
    private SettingsManager settings;
    private long lastTriggerTime = 0;
    private static final long DEBOUNCE_MS = 25; // Prevent duplicate rapid events

    public static boolean isRunning() {
        return isServiceRunning;
    }

    @Override
    public void onCreate() {
        super.onCreate();
        this.soundEngine = SoundEngine.getInstance(this);
        this.settings = SettingsManager.getInstance(this);
        isServiceRunning = true;
        Log.i(TAG, "ShotgunAccessibilityService created and active.");
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        if (event == null) return;

        int eventType = event.getEventType();
        if (eventType == AccessibilityEvent.TYPE_VIEW_TEXT_CHANGED) {
            long now = SystemClock.uptimeMillis();
            if (now - lastTriggerTime < DEBOUNCE_MS) {
                return;
            }
            lastTriggerTime = now;

            int addedCount = event.getAddedCount();
            int removedCount = event.getRemovedCount();

            if (addedCount > 0) {
                List<CharSequence> textList = event.getText();
                boolean isSpaceOrEnter = false;

                if (textList != null && !textList.isEmpty()) {
                    CharSequence fullText = textList.get(0);
                    int fromIndex = event.getFromIndex();
                    if (fullText != null && fromIndex >= 0 && fromIndex + addedCount <= fullText.length()) {
                        CharSequence addedSub = fullText.subSequence(fromIndex, fromIndex + addedCount);
                        for (int i = 0; i < addedSub.length(); i++) {
                            char c = addedSub.charAt(i);
                            if (c == ' ' || c == '\n' || c == '\r' || c == '\t') {
                                isSpaceOrEnter = true;
                                break;
                            }
                        }
                    }
                }

                if (isSpaceOrEnter && settings.isSpaceReloadEnabled()) {
                    soundEngine.playReload();
                } else {
                    soundEngine.playBlast();
                }
            } else if (removedCount > 0) {
                // Backspace / character deletion - subtle tactical response
                soundEngine.playBlast();
            }
        }
    }

    @Override
    protected boolean onKeyEvent(KeyEvent event) {
        if (event != null && event.getAction() == KeyEvent.ACTION_DOWN) {
            int keyCode = event.getKeyCode();
            if ((keyCode == KeyEvent.KEYCODE_SPACE || keyCode == KeyEvent.KEYCODE_ENTER || keyCode == KeyEvent.KEYCODE_NUMPAD_ENTER) 
                    && settings.isSpaceReloadEnabled()) {
                soundEngine.playReload();
            } else {
                soundEngine.playBlast();
            }
        }
        return super.onKeyEvent(event);
    }

    @Override
    public void onInterrupt() {
        Log.w(TAG, "ShotgunAccessibilityService interrupted.");
    }

    @Override
    public void onDestroy() {
        isServiceRunning = false;
        super.onDestroy();
        Log.i(TAG, "ShotgunAccessibilityService destroyed.");
    }
}
