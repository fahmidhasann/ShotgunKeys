package com.shotgunkeys.app;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.text.TextUtils;
import android.view.LayoutInflater;
import android.view.View;
import android.view.animation.Animation;
import android.view.animation.ScaleAnimation;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.LinearLayout;
import android.widget.SeekBar;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.List;

public class MainActivity extends Activity {
    private SoundEngine soundEngine;
    private SettingsManager settings;

    private TextView tvHeaderStatusBadge;
    private TextView tvServiceIndicator;
    private TextView tvServiceStatusText;
    private Button btnToggleAccessibility;

    private Button btnFireBlast;
    private Button btnPumpReload;

    private TextView tvStatShotsFired;
    private TextView tvStatReloads;
    private TextView tvBtnResetStats;

    private LinearLayout layoutPresetsContainer;
    private final List<View> presetCardViews = new ArrayList<>();

    private SeekBar seekbarVolume;
    private TextView tvVolumeValue;
    private Switch switchMicroDynamics;
    private Switch switchSpaceReload;
    private Switch switchHaptics;
    private Switch switchFloatingWidget;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        soundEngine = SoundEngine.getInstance(this);
        settings = SettingsManager.getInstance(this);

        initViews();
        setupListeners();
        setupPresets();
        updateStats();
    }

    @Override
    protected void onResume() {
        super.onResume();
        updateAccessibilityStatus();
        updateStats();
        updatePresetSelection();
    }

    private void initViews() {
        tvHeaderStatusBadge = findViewById(R.id.tv_header_status_badge);
        tvServiceIndicator = findViewById(R.id.tv_service_indicator);
        tvServiceStatusText = findViewById(R.id.tv_service_status_text);
        btnToggleAccessibility = findViewById(R.id.btn_toggle_accessibility);

        btnFireBlast = findViewById(R.id.btn_fire_blast);
        btnPumpReload = findViewById(R.id.btn_pump_reload);

        tvStatShotsFired = findViewById(R.id.tv_stat_shots_fired);
        tvStatReloads = findViewById(R.id.tv_stat_reloads);
        tvBtnResetStats = findViewById(R.id.tv_btn_reset_stats);

        layoutPresetsContainer = findViewById(R.id.layout_presets_container);

        seekbarVolume = findViewById(R.id.seekbar_volume);
        tvVolumeValue = findViewById(R.id.tv_volume_value);
        switchMicroDynamics = findViewById(R.id.switch_micro_dynamics);
        switchSpaceReload = findViewById(R.id.switch_space_reload);
        switchHaptics = findViewById(R.id.switch_haptics);
        switchFloatingWidget = findViewById(R.id.switch_floating_widget);

        // Load saved state into controls
        int volProgress = (int) (settings.getVolume() * 100);
        seekbarVolume.setProgress(volProgress);
        tvVolumeValue.setText(volProgress + "%");

        switchMicroDynamics.setChecked(settings.isMicroDynamicsEnabled());
        switchSpaceReload.setChecked(settings.isSpaceReloadEnabled());
        switchHaptics.setChecked(settings.isHapticsEnabled());
        switchFloatingWidget.setChecked(settings.isFloatingWidgetEnabled());
    }

    private void setupListeners() {
        btnToggleAccessibility.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS);
                startActivity(intent);
                Toast.makeText(MainActivity.this, "Find 'ShotgunKeys' and enable it", Toast.LENGTH_LONG).show();
            }
        });

        btnFireBlast.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                animateButton(v);
                soundEngine.playBlast();
                updateStats();
            }
        });

        btnPumpReload.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                animateButton(v);
                soundEngine.playReload();
                updateStats();
            }
        });

        tvBtnResetStats.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                settings.resetStats();
                updateStats();
                Toast.makeText(MainActivity.this, "Combat stats reset", Toast.LENGTH_SHORT).show();
            }
        });

        seekbarVolume.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                tvVolumeValue.setText(progress + "%");
                settings.setVolume(progress / 100.0f);
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {}
        });

        switchMicroDynamics.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                settings.setMicroDynamicsEnabled(isChecked);
            }
        });

        switchSpaceReload.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                settings.setSpaceReloadEnabled(isChecked);
            }
        });

        switchHaptics.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                settings.setHapticsEnabled(isChecked);
            }
        });

        switchFloatingWidget.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if (isChecked) {
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M && !Settings.canDrawOverlays(MainActivity.this)) {
                        Intent intent = new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                                Uri.parse("package:" + getPackageName()));
                        startActivity(intent);
                        buttonView.setChecked(false);
                        Toast.makeText(MainActivity.this, "Grant overlay permission for floating trigger", Toast.LENGTH_LONG).show();
                        return;
                    }
                    settings.setFloatingWidgetEnabled(true);
                    startService(new Intent(MainActivity.this, FloatingWidgetService.class));
                } else {
                    settings.setFloatingWidgetEnabled(false);
                    stopService(new Intent(MainActivity.this, FloatingWidgetService.class));
                }
            }
        });

        soundEngine.setSoundEventListener(new SoundEngine.SoundEventListener() {
            @Override
            public void onSoundPlayed(final boolean isBlast) {
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        updateStats();
                    }
                });
            }
        });
    }

    private void setupPresets() {
        layoutPresetsContainer.removeAllViews();
        presetCardViews.clear();

        LayoutInflater inflater = LayoutInflater.from(this);
        SoundPreset[] presets = SoundPreset.values();

        for (final SoundPreset preset : presets) {
            View card = inflater.inflate(R.layout.item_preset, layoutPresetsContainer, false);

            TextView tvIcon = card.findViewById(R.id.tv_preset_icon);
            TextView tvName = card.findViewById(R.id.tv_preset_name);
            TextView tvDesc = card.findViewById(R.id.tv_preset_desc);
            Button btnTest = card.findViewById(R.id.btn_preset_test);

            tvName.setText(preset.getDisplayName());
            tvDesc.setText(preset.getDescription());

            // Preset icon customization
            switch (preset) {
                case REALISTIC: tvIcon.setText("💥"); break;
                case TACTICAL: tvIcon.setText("🎯"); break;
                case DOOM: tvIcon.setText("⚡"); break;
                case SILENCED: tvIcon.setText("🤫"); break;
                case CYBERPUNK: tvIcon.setText("🤖"); break;
                case ARCADE: tvIcon.setText("🕹️"); break;
            }

            card.setTag(preset);

            card.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    settings.setPreset(preset);
                    updatePresetSelection();
                    soundEngine.playBlast();
                }
            });

            btnTest.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    settings.setPreset(preset);
                    updatePresetSelection();
                    soundEngine.playBlast();
                }
            });

            presetCardViews.add(card);
            layoutPresetsContainer.addView(card);
        }

        updatePresetSelection();
    }

    private void updatePresetSelection() {
        SoundPreset current = settings.getPreset();
        for (View card : presetCardViews) {
            SoundPreset preset = (SoundPreset) card.getTag();
            TextView tvBadge = card.findViewById(R.id.tv_preset_selected_badge);
            if (preset == current) {
                card.setBackgroundResource(R.drawable.card_tactical_active_bg);
                if (tvBadge != null) tvBadge.setVisibility(View.VISIBLE);
            } else {
                card.setBackgroundResource(R.drawable.card_tactical_bg);
                if (tvBadge != null) tvBadge.setVisibility(View.GONE);
            }
        }
    }

    private void updateStats() {
        tvStatShotsFired.setText(String.valueOf(settings.getShotsFiredCount()));
        tvStatReloads.setText(String.valueOf(settings.getReloadsCount()));
    }

    private void updateAccessibilityStatus() {
        boolean isServiceEnabled = isAccessibilityServiceEnabled(this, ShotgunAccessibilityService.class);

        if (isServiceEnabled || ShotgunAccessibilityService.isRunning()) {
            tvHeaderStatusBadge.setText("ACTIVE");
            tvHeaderStatusBadge.setTextColor(0xFF10B981);
            tvServiceIndicator.setText("● ");
            tvServiceIndicator.setTextColor(0xFF10B981);
            tvServiceStatusText.setText("ENABLED");
            tvServiceStatusText.setTextColor(0xFF10B981);
            btnToggleAccessibility.setText(R.string.btn_service_active);
            btnToggleAccessibility.setBackgroundResource(R.drawable.btn_secondary);
        } else {
            tvHeaderStatusBadge.setText("STANDBY");
            tvHeaderStatusBadge.setTextColor(0xFFF59E0B);
            tvServiceIndicator.setText("● ");
            tvServiceIndicator.setTextColor(0xFFEF4444);
            tvServiceStatusText.setText("DISABLED");
            tvServiceStatusText.setTextColor(0xFFEF4444);
            btnToggleAccessibility.setText(R.string.btn_enable_service);
            btnToggleAccessibility.setBackgroundResource(R.drawable.btn_action_green);
        }
    }

    private boolean isAccessibilityServiceEnabled(Context context, Class<?> service) {
        String expectedServiceName = context.getPackageName() + "/" + service.getName();
        try {
            int accessibilityEnabled = Settings.Secure.getInt(
                    context.getContentResolver(),
                    Settings.Secure.ACCESSIBILITY_ENABLED
            );
            if (accessibilityEnabled == 1) {
                String settingValue = Settings.Secure.getString(
                        context.getContentResolver(),
                        Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES
                );
                if (settingValue != null) {
                    TextUtils.SimpleStringSplitter colonSplitter = new TextUtils.SimpleStringSplitter(':');
                    colonSplitter.setString(settingValue);
                    while (colonSplitter.hasNext()) {
                        String componentName = colonSplitter.next();
                        if (componentName.equalsIgnoreCase(expectedServiceName)) {
                            return true;
                        }
                    }
                }
            }
        } catch (Exception e) {
            // ignore
        }
        return false;
    }

    private void animateButton(View view) {
        ScaleAnimation anim = new ScaleAnimation(
                1.0f, 0.93f, 1.0f, 0.93f,
                Animation.RELATIVE_TO_SELF, 0.5f,
                Animation.RELATIVE_TO_SELF, 0.5f
        );
        anim.setDuration(80);
        anim.setRepeatCount(1);
        anim.setRepeatMode(Animation.REVERSE);
        view.startAnimation(anim);
    }
}
