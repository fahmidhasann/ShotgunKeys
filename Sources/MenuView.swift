import SwiftUI
import AppKit

public struct MenuView: View {
    @ObservedObject var state = AppState.shared
    @State private var showReloadToast = false

    public init() {}

    public var body: some View {
        VStack(spacing: 0) {
            // Header Bar
            headerSection
            
            Divider()
                .background(Color.white.opacity(0.1))

            ScrollView(.vertical, showsIndicators: false) {
                VStack(spacing: 14) {
                    // Accessibility Permission Warning Banner (if not granted)
                    if !state.isAccessibilityGranted {
                        permissionBanner
                    }

                    // Main Power / Activation Card
                    powerControlCard

                    // Sound Profile Dropdown Card
                    soundProfileDropdownCard

                    // Custom Sounds Folder & Import Card (if custom or general)
                    if state.soundProfile == .custom {
                        customSoundsCard
                    }

                    // Volume & Pitch Controls
                    audioSettingsCard

                    // Key Binding Options Card
                    keyBindingsCard

                    // Live Stats & Action Monitor
                    liveStatsCard

                    // Quick Audio Test Actions
                    testButtonsSection
                }
                .padding(16)
            }

            Divider()
                .background(Color.white.opacity(0.1))

            // Footer Bar
            footerSection
        }
        .frame(width: 340, height: 580)
        .background(
            ZStack {
                Color(nsColor: .windowBackgroundColor)
                LinearGradient(
                    gradient: Gradient(colors: [
                        Color(red: 0.12, green: 0.13, blue: 0.15),
                        Color(red: 0.08, green: 0.09, blue: 0.10)
                    ]),
                    startPoint: .top,
                    endPoint: .bottom
                )
            }
        )
    }

    // MARK: - Sections

    private var headerSection: some View {
        HStack(spacing: 10) {
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [Color.orange, Color.red],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 32, height: 32)
                    .shadow(color: Color.orange.opacity(0.4), radius: 6, x: 0, y: 2)

                Image(systemName: state.soundProfile.icon)
                    .font(.system(size: 15, weight: .bold))
                    .foregroundColor(.white)
            }

            VStack(alignment: .leading, spacing: 2) {
                Text("ShotgunKeys")
                    .font(.system(size: 15, weight: .bold, design: .rounded))
                    .foregroundColor(.white)
                Text(state.soundProfile.rawValue)
                    .font(.system(size: 11, weight: .medium))
                    .foregroundColor(.orange.opacity(0.9))
            }

            Spacer()

            // Status Indicator Pill
            HStack(spacing: 5) {
                Circle()
                    .fill(state.isEnabled ? Color.green : Color.red.opacity(0.8))
                    .frame(width: 8, height: 8)
                Text(state.isEnabled ? "ACTIVE" : "MUTED")
                    .font(.system(size: 10, weight: .heavy, design: .monospaced))
                    .foregroundColor(state.isEnabled ? Color.green : Color.red.opacity(0.8))
            }
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(Color.black.opacity(0.35))
            .cornerRadius(12)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 14)
    }

    private var permissionBanner: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 8) {
                Image(systemName: "exclamationmark.triangle.fill")
                    .foregroundColor(.yellow)
                    .font(.system(size: 14, weight: .bold))
                Text("Accessibility Needed")
                    .font(.system(size: 12, weight: .bold))
                    .foregroundColor(.white)
            }

            Text("macOS requires Accessibility permission to detect keystrokes in other apps.")
                .font(.system(size: 11))
                .foregroundColor(.white.opacity(0.8))
                .fixedSize(horizontal: false, vertical: true)

            Button(action: {
                KeyTapManager.shared.openAccessibilitySettings()
            }) {
                HStack {
                    Image(systemName: "lock.open.fill")
                    Text("Grant Permission in Settings")
                        .fontWeight(.semibold)
                }
                .font(.system(size: 11))
                .frame(maxWidth: .infinity)
                .padding(.vertical, 6)
                .background(Color.yellow.opacity(0.25))
                .foregroundColor(.yellow)
                .cornerRadius(6)
                .overlay(
                    RoundedRectangle(cornerRadius: 6)
                        .stroke(Color.yellow.opacity(0.5), lineWidth: 1)
                )
            }
            .buttonStyle(.plain)
        }
        .padding(12)
        .background(Color.yellow.opacity(0.12))
        .cornerRadius(10)
        .overlay(
            RoundedRectangle(cornerRadius: 10)
                .stroke(Color.yellow.opacity(0.3), lineWidth: 1)
        )
    }

    private var powerControlCard: some View {
        HStack {
            VStack(alignment: .leading, spacing: 2) {
                Text("Sound Effects")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(.white)
                Text(state.isEnabled ? "Gunshot audio enabled" : "Sounds currently muted")
                    .font(.system(size: 11))
                    .foregroundColor(.gray)
            }

            Spacer()

            Toggle("", isOn: $state.isEnabled)
                .toggleStyle(SwitchToggleStyle(tint: .orange))
                .labelsHidden()
        }
        .padding(12)
        .background(Color.white.opacity(0.06))
        .cornerRadius(10)
    }

    private var soundProfileDropdownCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text("SOUND PRESET")
                    .font(.system(size: 10, weight: .bold, design: .rounded))
                    .foregroundColor(.gray)
                Spacer()
                Text("Instant Preview ON")
                    .font(.system(size: 9, weight: .semibold))
                    .foregroundColor(.orange.opacity(0.8))
            }

            // Styled Custom Dropdown / Menu
            Menu {
                ForEach(SoundProfile.allCases) { profile in
                    Button(action: {
                        state.soundProfile = profile
                    }) {
                        HStack {
                            Image(systemName: profile.icon)
                            Text(profile.rawValue)
                        }
                    }
                }
            } label: {
                HStack(spacing: 10) {
                    Image(systemName: state.soundProfile.icon)
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(.orange)
                        .frame(width: 20)

                    VStack(alignment: .leading, spacing: 2) {
                        Text(state.soundProfile.rawValue)
                            .font(.system(size: 13, weight: .semibold))
                            .foregroundColor(.white)
                        Text(state.soundProfile.subtitle)
                            .font(.system(size: 10))
                            .foregroundColor(.gray)
                    }

                    Spacer()

                    Image(systemName: "chevron.up.chevron.down")
                        .font(.system(size: 11, weight: .semibold))
                        .foregroundColor(.orange.opacity(0.8))
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
                .background(Color.white.opacity(0.08))
                .cornerRadius(8)
                .overlay(
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(Color.orange.opacity(0.3), lineWidth: 1)
                )
            }
            .menuStyle(.borderlessButton)
        }
        .padding(12)
        .background(Color.white.opacity(0.06))
        .cornerRadius(10)
    }

    private var customSoundsCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text("CUSTOM AUDIO FOLDER")
                    .font(.system(size: 10, weight: .bold, design: .rounded))
                    .foregroundColor(.gray)
                Spacer()
                if showReloadToast {
                    Text("✓ Reloaded")
                        .font(.system(size: 10, weight: .semibold))
                        .foregroundColor(.green)
                }
            }

            Text("Drop your own WAV/MP3 files into the CustomSounds folder.")
                .font(.system(size: 11))
                .foregroundColor(.white.opacity(0.7))

            HStack(spacing: 8) {
                Button(action: {
                    let url = SoundEngine.customSoundsDirectory
                    NSWorkspace.shared.open(url)
                }) {
                    HStack(spacing: 4) {
                        Image(systemName: "folder.fill")
                        Text("Open Folder")
                    }
                    .font(.system(size: 11, weight: .medium))
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 6)
                    .background(Color.white.opacity(0.1))
                    .foregroundColor(.white)
                    .cornerRadius(6)
                }
                .buttonStyle(.plain)

                Button(action: {
                    SoundEngine.shared.reloadSounds()
                    showReloadToast = true
                    DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
                        showReloadToast = false
                    }
                }) {
                    HStack(spacing: 4) {
                        Image(systemName: "arrow.clockwise")
                        Text("Reload Files")
                    }
                    .font(.system(size: 11, weight: .medium))
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 6)
                    .background(Color.orange.opacity(0.2))
                    .foregroundColor(.orange)
                    .cornerRadius(6)
                }
                .buttonStyle(.plain)
            }
        }
        .padding(12)
        .background(Color.white.opacity(0.06))
        .cornerRadius(10)
    }

    private var audioSettingsCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("AUDIO CONTROLS")
                .font(.system(size: 10, weight: .bold, design: .rounded))
                .foregroundColor(.gray)

            // Volume Slider
            VStack(alignment: .leading, spacing: 6) {
                HStack {
                    Image(systemName: state.volume > 0.5 ? "speaker.wave.3.fill" : (state.volume > 0.05 ? "speaker.wave.1.fill" : "speaker.slash.fill"))
                        .foregroundColor(.orange)
                        .font(.system(size: 12))
                    Text("Master Volume")
                        .font(.system(size: 12, weight: .medium))
                        .foregroundColor(.white)
                    Spacer()
                    Text("\(Int(state.volume * 100))%")
                        .font(.system(size: 11, weight: .bold, design: .monospaced))
                        .foregroundColor(.orange)
                }

                Slider(value: $state.volume, in: 0.0...1.0)
                    .accentColor(.orange)
            }

            Divider()
                .background(Color.white.opacity(0.08))

            // Pitch & Dynamics Randomization Toggle
            Toggle(isOn: $state.pitchRandomization) {
                VStack(alignment: .leading, spacing: 1) {
                    Text("Natural Micro-Dynamics")
                        .font(.system(size: 12, weight: .medium))
                        .foregroundColor(.white)
                    Text("Adds organic pitch & volume dynamics during typing")
                        .font(.system(size: 10))
                        .foregroundColor(.gray)
                }
            }
            .toggleStyle(SwitchToggleStyle(tint: .orange))
        }
        .padding(12)
        .background(Color.white.opacity(0.06))
        .cornerRadius(10)
    }

    private var keyBindingsCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("KEY BEHAVIOR")
                .font(.system(size: 10, weight: .bold, design: .rounded))
                .foregroundColor(.gray)

            HStack {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Space Key Reload")
                        .font(.system(size: 12, weight: .medium))
                        .foregroundColor(.white)
                    Text("Pump-action sound on Spacebar")
                        .font(.system(size: 10))
                        .foregroundColor(.gray)
                }
                Spacer()
                Toggle("", isOn: $state.reloadOnSpace)
                    .toggleStyle(SwitchToggleStyle(tint: .orange))
                    .labelsHidden()
            }

            Divider()
                .background(Color.white.opacity(0.08))

            HStack {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Enter Key Reload")
                        .font(.system(size: 12, weight: .medium))
                        .foregroundColor(.white)
                    Text("Pump-action sound on Return / Enter")
                        .font(.system(size: 10))
                        .foregroundColor(.gray)
                }
                Spacer()
                Toggle("", isOn: $state.reloadOnEnter)
                    .toggleStyle(SwitchToggleStyle(tint: .orange))
                    .labelsHidden()
            }
        }
        .padding(12)
        .background(Color.white.opacity(0.06))
        .cornerRadius(10)
    }

    private var liveStatsCard: some View {
        HStack(spacing: 12) {
            // Blast Count
            VStack(alignment: .leading, spacing: 2) {
                Text("SHOTS FIRED")
                    .font(.system(size: 9, weight: .heavy, design: .rounded))
                    .foregroundColor(.orange)
                Text("\(state.totalShotsFired)")
                    .font(.system(size: 18, weight: .black, design: .monospaced))
                    .foregroundColor(.white)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(10)
            .background(Color.black.opacity(0.3))
            .cornerRadius(8)

            // Reload Count
            VStack(alignment: .leading, spacing: 2) {
                Text("RELOADS")
                    .font(.system(size: 9, weight: .heavy, design: .rounded))
                    .foregroundColor(.yellow)
                Text("\(state.totalReloads)")
                    .font(.system(size: 18, weight: .black, design: .monospaced))
                    .foregroundColor(.white)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(10)
            .background(Color.black.opacity(0.3))
            .cornerRadius(8)
        }
    }

    private var testButtonsSection: some View {
        HStack(spacing: 10) {
            Button(action: {
                SoundEngine.shared.playShotgunBlast()
            }) {
                HStack(spacing: 6) {
                    Image(systemName: "burst.fill")
                    Text("Test Blast")
                        .fontWeight(.bold)
                }
                .font(.system(size: 12))
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 8)
                .background(
                    LinearGradient(
                        colors: [Color.orange, Color.red],
                        startPoint: .top,
                        endPoint: .bottom
                    )
                )
                .cornerRadius(8)
                .shadow(color: Color.orange.opacity(0.3), radius: 4, x: 0, y: 2)
            }
            .buttonStyle(.plain)

            Button(action: {
                SoundEngine.shared.playReload()
            }) {
                HStack(spacing: 6) {
                    Image(systemName: "arrow.triangle.2.circlepath")
                    Text("Test Reload")
                        .fontWeight(.bold)
                }
                .font(.system(size: 12))
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 8)
                .background(Color.white.opacity(0.12))
                .cornerRadius(8)
                .overlay(
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(Color.white.opacity(0.2), lineWidth: 1)
                )
            }
            .buttonStyle(.plain)
        }
    }

    private var footerSection: some View {
        HStack {
            Button(action: {
                let url = SoundEngine.customSoundsDirectory
                NSWorkspace.shared.open(url)
            }) {
                HStack(spacing: 4) {
                    Image(systemName: "folder")
                    Text("Sounds Folder")
                }
                .font(.system(size: 11))
                .foregroundColor(.gray)
            }
            .buttonStyle(.plain)

            Spacer()

            Button(action: {
                NSApplication.shared.terminate(nil)
            }) {
                HStack(spacing: 4) {
                    Image(systemName: "power")
                    Text("Quit")
                }
                .font(.system(size: 11, weight: .semibold))
                .foregroundColor(.red.opacity(0.85))
            }
            .buttonStyle(.plain)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(Color.black.opacity(0.2))
    }
}
