"""
Modern Dark-Themed Desktop GUI for ShotgunKeys Windows using Tkinter.
Features:
- Tactical dark UI layout with real-time statistics counters
- Sound preset selection with live descriptions and audio test buttons
- Master volume slider and mechanics toggles (pitch variance, space/enter reload)
- System tray minimization and DPI-aware scaling
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional

from config import config, get_assets_dir, get_custom_sounds_dir, PRESETS
from sound_engine import sound_engine

# High DPI Awareness on Windows
if os.name == 'nt':
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            import ctypes
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

# Color Palette Constants
COLOR_BG = "#101114"
COLOR_CARD_BG = "#191a21"
COLOR_CARD_BORDER = "#282a36"
COLOR_ACCENT = "#ff9800"
COLOR_ACCENT_HOVER = "#ffa726"
COLOR_ACCENT_ACTIVE = "#e65100"
COLOR_SUCCESS = "#00e676"
COLOR_SUCCESS_BG = "#0c281e"
COLOR_MUTED = "#6c757d"
COLOR_MUTED_BG = "#22252c"
COLOR_TEXT = "#f0f2f5"
COLOR_TEXT_SECONDARY = "#9ea3b5"
COLOR_TEXT_MUTED = "#5a6072"
COLOR_INPUT_BG = "#232631"

class MainWindow:
    """The primary GUI control center for ShotgunKeys."""

    def __init__(self, on_minimize_to_tray: Optional[Callable[[], None]] = None, on_exit: Optional[Callable[[], None]] = None):
        self.on_minimize_to_tray = on_minimize_to_tray
        self.on_exit = on_exit

        self.root = tk.Tk()
        self.root.title("ShotgunKeys")
        self.root.geometry("490x670")
        self.root.minsize(470, 620)
        self.root.configure(bg=COLOR_BG)

        # Set Window Icon
        self._set_app_icon()

        # State Variables
        self.var_enabled = tk.BooleanVar(value=bool(config.get("enabled", True)))
        self.var_volume = tk.DoubleVar(value=float(config.get("volume", 0.85)) * 100.0)
        self.var_pitch = tk.BooleanVar(value=bool(config.get("pitch_randomization", True)))
        self.var_reload_space = tk.BooleanVar(value=bool(config.get("reload_on_space", True)))
        self.var_reload_enter = tk.BooleanVar(value=bool(config.get("reload_on_enter", True)))
        self.var_preset = tk.StringVar(value=str(config.get("preset", "Realistic 12-Gauge")))

        self.var_shots = tk.StringVar(value=f"{config.get('total_shots_fired', 0):,}")
        self.var_reloads = tk.StringVar(value=f"{config.get('total_reloads', 0):,}")
        self.var_status_feed = tk.StringVar(value="Status: Ready")

        self._configure_styles()
        self._build_ui()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close_window)

    def _set_app_icon(self):
        assets_dir = get_assets_dir()
        ico_path = os.path.join(assets_dir, "app_icon.ico")
        png_path = os.path.join(assets_dir, "app_icon.png")

        if os.path.exists(ico_path) and os.name == 'nt':
            try:
                self.root.iconbitmap(ico_path)
                return
            except Exception:
                pass

        if os.path.exists(png_path):
            try:
                img = tk.PhotoImage(file=png_path)
                self.root.iconphoto(True, img)
            except Exception:
                pass

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure(".", background=COLOR_BG, foreground=COLOR_TEXT)
        style.configure("TFrame", background=COLOR_BG)
        style.configure("Card.TFrame", background=COLOR_CARD_BG)

        # Labels
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground=COLOR_TEXT, background=COLOR_BG)
        style.configure("SubHeader.TLabel", font=("Segoe UI", 9), foreground=COLOR_TEXT_SECONDARY, background=COLOR_BG)
        style.configure("CardTitle.TLabel", font=("Segoe UI", 10, "bold"), foreground=COLOR_ACCENT, background=COLOR_CARD_BG)
        style.configure("StatNum.TLabel", font=("Segoe UI", 18, "bold"), foreground=COLOR_TEXT, background=COLOR_CARD_BG)
        style.configure("StatLabel.TLabel", font=("Segoe UI", 8, "bold"), foreground=COLOR_TEXT_SECONDARY, background=COLOR_CARD_BG)
        style.configure("Desc.TLabel", font=("Segoe UI", 9), foreground=COLOR_TEXT_SECONDARY, background=COLOR_CARD_BG)

        # Combobox
        style.configure(
            "TCombobox",
            fieldbackground=COLOR_INPUT_BG,
            background=COLOR_INPUT_BG,
            foreground=COLOR_TEXT,
            arrowcolor=COLOR_ACCENT,
            darkcolor=COLOR_CARD_BORDER,
            lightcolor=COLOR_CARD_BORDER,
            bordercolor=COLOR_CARD_BORDER,
            padding=6
        )
        style.map('TCombobox',
                  fieldbackground=[('readonly', COLOR_INPUT_BG)],
                  selectbackground=[('readonly', COLOR_ACCENT)],
                  selectforeground=[('readonly', '#000000')])

        # Scale / Slider
        style.configure("Horizontal.TScale",
                        background=COLOR_CARD_BG,
                        troughcolor=COLOR_INPUT_BG,
                        bordercolor=COLOR_CARD_BORDER,
                        lightcolor=COLOR_ACCENT,
                        darkcolor=COLOR_ACCENT)

        # Checkbutton
        style.configure("TCheckbutton",
                        background=COLOR_CARD_BG,
                        foreground=COLOR_TEXT,
                        font=("Segoe UI", 9))
        style.map("TCheckbutton",
                  background=[("active", COLOR_CARD_BG)],
                  foreground=[("active", COLOR_TEXT)])

    def _build_ui(self):
        main_container = tk.Frame(self.root, bg=COLOR_BG, padx=16, pady=14)
        main_container.pack(fill=tk.BOTH, expand=True)

        # 1. HEADER SECTION
        header_frame = tk.Frame(main_container, bg=COLOR_BG)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # Title & Subtitle left
        title_box = tk.Frame(header_frame, bg=COLOR_BG)
        title_box.pack(side=tk.LEFT)

        title_label = tk.Label(
            title_box,
            text="💥 SHOTGUNKEYS",
            font=("Segoe UI", 15, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_BG
        )
        title_label.pack(anchor="w")

        sub_label = tk.Label(
            title_box,
            text="Tactical Typing & Mechanical Sound Engine",
            font=("Segoe UI", 8),
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_BG
        )
        sub_label.pack(anchor="w")

        # Status badge right
        self.btn_master_toggle = tk.Button(
            header_frame,
            text="● ACTIVE" if self.var_enabled.get() else "○ MUTED",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_SUCCESS_BG if self.var_enabled.get() else COLOR_MUTED_BG,
            fg=COLOR_SUCCESS if self.var_enabled.get() else COLOR_MUTED,
            activebackground=COLOR_INPUT_BG,
            activeforeground=COLOR_TEXT,
            bd=1,
            relief=tk.FLAT,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self._toggle_master_enabled
        )
        self.btn_master_toggle.pack(side=tk.RIGHT, pady=4)

        # 2. STATS DASHBOARD CARD
        stats_card = tk.Frame(main_container, bg=COLOR_CARD_BG, bd=1, relief=tk.SOLID, highlightbackground=COLOR_CARD_BORDER, highlightthickness=1)
        stats_card.pack(fill=tk.X, pady=(0, 10), ipady=6, ipadx=8)

        stats_grid = tk.Frame(stats_card, bg=COLOR_CARD_BG)
        stats_grid.pack(fill=tk.X, padx=10, pady=4)
        stats_grid.columnconfigure(0, weight=1)
        stats_grid.columnconfigure(1, weight=1)

        # Left Stat: Shots
        shot_box = tk.Frame(stats_grid, bg=COLOR_CARD_BG)
        shot_box.grid(row=0, column=0, sticky="ew", padx=4)

        tk.Label(shot_box, text="TOTAL BLASTS", font=("Segoe UI", 8, "bold"), fg=COLOR_TEXT_SECONDARY, bg=COLOR_CARD_BG).pack(anchor="center")
        self.lbl_shots = tk.Label(shot_box, textvariable=self.var_shots, font=("Segoe UI", 16, "bold"), fg=COLOR_ACCENT, bg=COLOR_CARD_BG)
        self.lbl_shots.pack(anchor="center")

        # Right Stat: Reloads
        reload_box = tk.Frame(stats_grid, bg=COLOR_CARD_BG)
        reload_box.grid(row=0, column=1, sticky="ew", padx=4)

        tk.Label(reload_box, text="TOTAL RELOADS", font=("Segoe UI", 8, "bold"), fg=COLOR_TEXT_SECONDARY, bg=COLOR_CARD_BG).pack(anchor="center")
        self.lbl_reloads = tk.Label(reload_box, textvariable=self.var_reloads, font=("Segoe UI", 16, "bold"), fg="#40c4ff", bg=COLOR_CARD_BG)
        self.lbl_reloads.pack(anchor="center")

        # Activity feed pill
        feed_box = tk.Frame(stats_card, bg=COLOR_INPUT_BG, padx=8, pady=3)
        feed_box.pack(fill=tk.X, padx=12, pady=(4, 2))
        self.lbl_feed = tk.Label(feed_box, textvariable=self.var_status_feed, font=("Segoe UI", 8, "bold"), fg=COLOR_TEXT_SECONDARY, bg=COLOR_INPUT_BG)
        self.lbl_feed.pack(anchor="center")

        # 3. PRESETS SELECTION CARD
        preset_card = tk.Frame(main_container, bg=COLOR_CARD_BG, bd=1, relief=tk.SOLID, highlightbackground=COLOR_CARD_BORDER, highlightthickness=1)
        preset_card.pack(fill=tk.X, pady=(0, 10), ipady=6, ipadx=10)

        tk.Label(preset_card, text="SOUND PROFILE", font=("Segoe UI", 9, "bold"), fg=COLOR_ACCENT, bg=COLOR_CARD_BG).pack(anchor="w", padx=10, pady=(6, 4))

        # Dropdown
        preset_names = [f"{p['icon']} {p['name']}" for p in PRESETS]
        self.preset_combo = ttk.Combobox(
            preset_card,
            values=preset_names,
            state="readonly",
            font=("Segoe UI", 9)
        )
        # Match current preset
        curr_p = self.var_preset.get()
        curr_idx = 0
        for i, p in enumerate(PRESETS):
            if p["name"] == curr_p:
                curr_idx = i
                break
        self.preset_combo.current(curr_idx)
        self.preset_combo.pack(fill=tk.X, padx=10, pady=(0, 6))
        self.preset_combo.bind("<<ComboboxSelected>>", self._on_preset_changed)

        # Preset description label
        self.lbl_preset_desc = tk.Label(
            preset_card,
            text=self._get_preset_desc(curr_p),
            font=("Segoe UI", 8),
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_CARD_BG,
            wraplength=420,
            justify=tk.LEFT
        )
        self.lbl_preset_desc.pack(anchor="w", padx=10, pady=(0, 8))

        # Test Sound Buttons row
        test_row = tk.Frame(preset_card, bg=COLOR_CARD_BG)
        test_row.pack(fill=tk.X, padx=10, pady=(0, 4))

        btn_test_blast = tk.Button(
            test_row,
            text="💥 Test Blast",
            font=("Segoe UI", 8, "bold"),
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT,
            activebackground=COLOR_ACCENT,
            activeforeground="#000000",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._test_blast
        )
        btn_test_blast.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))

        btn_test_reload = tk.Button(
            test_row,
            text="🔄 Test Reload",
            font=("Segoe UI", 8, "bold"),
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT,
            activebackground="#40c4ff",
            activeforeground="#000000",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._test_reload
        )
        btn_test_reload.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(4, 0))

        # 4. AUDIO CONTROLS CARD
        ctrl_card = tk.Frame(main_container, bg=COLOR_CARD_BG, bd=1, relief=tk.SOLID, highlightbackground=COLOR_CARD_BORDER, highlightthickness=1)
        ctrl_card.pack(fill=tk.X, pady=(0, 10), ipady=6, ipadx=10)

        # Volume Header + Value
        vol_header = tk.Frame(ctrl_card, bg=COLOR_CARD_BG)
        vol_header.pack(fill=tk.X, padx=10, pady=(6, 2))

        tk.Label(vol_header, text="MASTER VOLUME", font=("Segoe UI", 9, "bold"), fg=COLOR_ACCENT, bg=COLOR_CARD_BG).pack(side=tk.LEFT)
        self.lbl_vol_val = tk.Label(
            vol_header,
            text=f"{int(self.var_volume.get())}%",
            font=("Segoe UI", 9, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_CARD_BG
        )
        self.lbl_vol_val.pack(side=tk.RIGHT)

        # Volume Slider
        self.scale_vol = ttk.Scale(
            ctrl_card,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.var_volume,
            command=self._on_volume_changed
        )
        self.scale_vol.pack(fill=tk.X, padx=10, pady=(2, 8))

        # Checkboxes for mechanics
        cb_pitch = ttk.Checkbutton(
            ctrl_card,
            text="Dynamic Pitch Micro-Randomization (Anti-Robotic)",
            variable=self.var_pitch,
            command=self._on_pitch_toggle
        )
        cb_pitch.pack(anchor="w", padx=10, pady=2)

        cb_space = ttk.Checkbutton(
            ctrl_card,
            text="Trigger Reload Sound on Spacebar",
            variable=self.var_reload_space,
            command=self._on_space_toggle
        )
        cb_space.pack(anchor="w", padx=10, pady=2)

        cb_enter = ttk.Checkbutton(
            ctrl_card,
            text="Trigger Reload Sound on Enter Key",
            variable=self.var_reload_enter,
            command=self._on_enter_toggle
        )
        cb_enter.pack(anchor="w", padx=10, pady=2)

        # 5. BOTTOM ACTIONS
        actions_frame = tk.Frame(main_container, bg=COLOR_BG)
        actions_frame.pack(fill=tk.X, pady=(2, 0))

        btn_folder = tk.Button(
            actions_frame,
            text="📁 Custom Sounds",
            font=("Segoe UI", 8),
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT_SECONDARY,
            activebackground=COLOR_CARD_BORDER,
            activeforeground=COLOR_TEXT,
            bd=0,
            padx=8,
            pady=5,
            cursor="hand2",
            command=self._open_custom_folder
        )
        btn_folder.pack(side=tk.LEFT, padx=(0, 4))

        btn_reload_audio = tk.Button(
            actions_frame,
            text="🔄 Refresh Sounds",
            font=("Segoe UI", 8),
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT_SECONDARY,
            activebackground=COLOR_CARD_BORDER,
            activeforeground=COLOR_TEXT,
            bd=0,
            padx=8,
            pady=5,
            cursor="hand2",
            command=self._reload_sounds
        )
        btn_reload_audio.pack(side=tk.LEFT, padx=4)

        btn_tray = tk.Button(
            actions_frame,
            text="🔽 Minimize to Tray",
            font=("Segoe UI", 8, "bold"),
            bg=COLOR_CARD_BORDER,
            fg=COLOR_TEXT,
            activebackground=COLOR_ACCENT,
            activeforeground="#000000",
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            command=self.hide_to_tray
        )
        btn_tray.pack(side=tk.RIGHT, padx=(4, 0))

    def _get_preset_desc(self, name: str) -> str:
        for p in PRESETS:
            if p["name"] == name:
                return p["description"]
        return ""

    def _toggle_master_enabled(self):
        new_val = not self.var_enabled.get()
        self.var_enabled.set(new_val)
        config.set("enabled", new_val)
        self.update_state_ui()

    def update_state_ui(self):
        """Refreshes UI state from config."""
        is_enabled = config.get("enabled", True)
        self.var_enabled.set(is_enabled)
        if is_enabled:
            self.btn_master_toggle.config(
                text="● ACTIVE",
                bg=COLOR_SUCCESS_BG,
                fg=COLOR_SUCCESS
            )
        else:
            self.btn_master_toggle.config(
                text="○ MUTED",
                bg=COLOR_MUTED_BG,
                fg=COLOR_MUTED
            )

        # Preset
        curr_p = config.get("preset", "Realistic 12-Gauge")
        self.var_preset.set(curr_p)
        for i, p in enumerate(PRESETS):
            if p["name"] == curr_p:
                self.preset_combo.current(i)
                break
        self.lbl_preset_desc.config(text=self._get_preset_desc(curr_p))

    def _on_preset_changed(self, event=None):
        selected_idx = self.preset_combo.current()
        if 0 <= selected_idx < len(PRESETS):
            selected_preset = PRESETS[selected_idx]["name"]
            self.var_preset.set(selected_preset)
            self.lbl_preset_desc.config(text=self._get_preset_desc(selected_preset))
            sound_engine.load_preset(selected_preset, preview=True)

    def _test_blast(self):
        sound_engine.play_blast()
        self.on_key_action("blast")

    def _test_reload(self):
        sound_engine.play_reload()
        self.on_key_action("reload")

    def _on_volume_changed(self, val):
        vol_pct = float(val)
        self.lbl_vol_val.config(text=f"{int(vol_pct)}%")
        sound_engine.set_volume(vol_pct / 100.0)

    def _on_pitch_toggle(self):
        sound_engine.set_pitch_randomization(self.var_pitch.get())

    def _on_space_toggle(self):
        config.set("reload_on_space", self.var_reload_space.get())

    def _on_enter_toggle(self):
        config.set("reload_on_enter", self.var_reload_enter.get())

    def _open_custom_folder(self):
        custom_dir = get_custom_sounds_dir()
        if os.name == 'nt':
            os.startfile(custom_dir)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', custom_dir])
        else:
            subprocess.Popen(['xdg-open', custom_dir])

    def _reload_sounds(self):
        curr_p = self.var_preset.get()
        sound_engine.load_preset(curr_p, preview=True)
        self.var_status_feed.set("Status: Audio Refreshed 🔄")

    def on_key_action(self, action: str):
        """Thread-safe dispatch for live UI stats updates."""
        def update():
            shots = config.get("total_shots_fired", 0)
            reloads = config.get("total_reloads", 0)
            self.var_shots.set(f"{shots:,}")
            self.var_reloads.set(f"{reloads:,}")
            if action == "blast":
                self.var_status_feed.set(f"💥 BLAST (#{shots:,})")
            elif action == "reload":
                self.var_status_feed.set(f"🔄 RELOAD (#{reloads:,})")

        try:
            self.root.after(0, update)
        except Exception:
            pass

    def show(self):
        """Restores and brings the window to the foreground."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide_to_tray(self):
        """Hides the window to system tray."""
        self.root.withdraw()
        if self.on_minimize_to_tray:
            self.on_minimize_to_tray()

    def on_close_window(self):
        """Window close button behavior."""
        if config.get("minimize_to_tray", True):
            self.hide_to_tray()
        else:
            self.quit_app()

    def quit_app(self):
        """Complete application shutdown."""
        if self.on_exit:
            self.on_exit()
        else:
            self.root.destroy()
            os._exit(0)

    def run_loop(self):
        """Starts Tkinter main event loop."""
        self.root.mainloop()
