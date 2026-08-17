package com.shotgunkeys.app;

public enum SoundPreset {
    REALISTIC(
        "REALISTIC",
        "Realistic 12-Gauge",
        "Authentic heavy 12-gauge pump shotgun blast with brass eject",
        new int[]{R.raw.shotgun_blast_1, R.raw.shotgun_blast_2, R.raw.shotgun_blast_3, R.raw.shotgun_blast_4},
        new int[]{R.raw.shotgun_reload_1, R.raw.shotgun_reload_2, R.raw.real_shotgun_reload}
    ),
    TACTICAL(
        "TACTICAL",
        "Tactical Shotgun",
        "Crisp military breach sound with swift mechanical pump slide",
        new int[]{R.raw.tactical_blast_1, R.raw.tactical_blast_2, R.raw.tactical_blast_3},
        new int[]{R.raw.tactical_reload_1, R.raw.tactical_reload_2}
    ),
    DOOM(
        "DOOM",
        "Doom Super Shotgun",
        "Devastating heavy double-barrel blast with industrial reload",
        new int[]{R.raw.doom_blast_1, R.raw.doom_blast_2},
        new int[]{R.raw.doom_reload_1, R.raw.doom_reload_2}
    ),
    SILENCED(
        "SILENCED",
        "Silenced Shotgun",
        "Subdued tactical suppressed blast with discreet chambering",
        new int[]{R.raw.silenced_blast_1, R.raw.silenced_blast_2},
        new int[]{R.raw.silenced_reload_1, R.raw.silenced_reload_2}
    ),
    CYBERPUNK(
        "CYBERPUNK",
        "Cyberpunk Railgun",
        "Futuristic energy plasma discharge with capacitor recharge cycle",
        new int[]{R.raw.cyber_blast_1, R.raw.cyber_blast_2},
        new int[]{R.raw.cyber_reload_1, R.raw.cyber_reload_2}
    ),
    ARCADE(
        "ARCADE",
        "8-Bit Arcade",
        "Classic retro arcade blip fire & crunchy chiptune pump action",
        new int[]{R.raw.arcade_blast},
        new int[]{R.raw.arcade_reload}
    );

    private final String id;
    private final String displayName;
    private final String description;
    private final int[] blastResIds;
    private final int[] reloadResIds;

    SoundPreset(String id, String displayName, String description, int[] blastResIds, int[] reloadResIds) {
        this.id = id;
        this.displayName = displayName;
        this.description = description;
        this.blastResIds = blastResIds;
        this.reloadResIds = reloadResIds;
    }

    public String getId() {
        return id;
    }

    public String getDisplayName() {
        return displayName;
    }

    public String getDescription() {
        return description;
    }

    public int[] getBlastResIds() {
        return blastResIds;
    }

    public int[] getReloadResIds() {
        return reloadResIds;
    }

    public static SoundPreset fromId(String id) {
        for (SoundPreset preset : values()) {
            if (preset.id.equalsIgnoreCase(id)) {
                return preset;
            }
        }
        return REALISTIC;
    }
}
