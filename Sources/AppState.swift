import Foundation
import Combine
import SwiftUI

public enum SoundProfile: String, CaseIterable, Identifiable {
    case realistic = "Realistic 12-Gauge"
    case tactical = "Tactical Combat"
    case heavyDoom = "Heavy Doom (Boomstick)"
    case silenced = "Silenced Spec-Ops"
    case cyberpunk = "Cyberpunk Energy"
    case arcade = "8-Bit Retro Arcade"
    case custom = "Custom (User Folder)"

    public var id: String { rawValue }

    public var icon: String {
        switch self {
        case .realistic: return "flame.fill"
        case .tactical: return "scope"
        case .heavyDoom: return "bolt.shield.fill"
        case .silenced: return "waveform.badge.magnifyingglass"
        case .cyberpunk: return "atom"
        case .arcade: return "gamecontroller.fill"
        case .custom: return "folder.fill"
        }
    }

    public var subtitle: String {
        switch self {
        case .realistic: return "Authentic live-recorded field blasts"
        case .tactical: return "Crisp & snappy military gunshot"
        case .heavyDoom: return "Massive bass double-barrel thunder"
        case .silenced: return "Suppressed puff & smooth slide"
        case .cyberpunk: return "High-energy plasma & servo reload"
        case .arcade: return "Punchy 8-bit retro chiptune"
        case .custom: return "Your custom audio files from folder"
        }
    }
}

public class AppState: ObservableObject {
    public static let shared = AppState()

    @Published public var isEnabled: Bool {
        didSet {
            UserDefaults.standard.set(isEnabled, forKey: "ShotgunKeys_isEnabled")
        }
    }

    @Published public var volume: Double {
        didSet {
            UserDefaults.standard.set(volume, forKey: "ShotgunKeys_volume")
            SoundEngine.shared.setVolume(Float(volume))
        }
    }

    @Published public var pitchRandomization: Bool {
        didSet {
            UserDefaults.standard.set(pitchRandomization, forKey: "ShotgunKeys_pitchRandomization")
        }
    }

    @Published public var soundProfile: SoundProfile {
        didSet {
            UserDefaults.standard.set(soundProfile.rawValue, forKey: "ShotgunKeys_soundProfile")
            SoundEngine.shared.loadSounds(profile: soundProfile, preview: true)
        }
    }

    @Published public var reloadOnSpace: Bool {
        didSet {
            UserDefaults.standard.set(reloadOnSpace, forKey: "ShotgunKeys_reloadOnSpace")
        }
    }

    @Published public var reloadOnEnter: Bool {
        didSet {
            UserDefaults.standard.set(reloadOnEnter, forKey: "ShotgunKeys_reloadOnEnter")
        }
    }

    @Published public var isAccessibilityGranted: Bool = false
    @Published public var totalShotsFired: Int = 0
    @Published public var totalReloads: Int = 0
    @Published public var lastActionText: String = "Ready"

    private init() {
        self.isEnabled = UserDefaults.standard.object(forKey: "ShotgunKeys_isEnabled") as? Bool ?? true
        self.volume = UserDefaults.standard.object(forKey: "ShotgunKeys_volume") as? Double ?? 0.85
        self.pitchRandomization = UserDefaults.standard.object(forKey: "ShotgunKeys_pitchRandomization") as? Bool ?? true
        self.reloadOnSpace = UserDefaults.standard.object(forKey: "ShotgunKeys_reloadOnSpace") as? Bool ?? true
        self.reloadOnEnter = UserDefaults.standard.object(forKey: "ShotgunKeys_reloadOnEnter") as? Bool ?? true

        let savedProfileStr = UserDefaults.standard.string(forKey: "ShotgunKeys_soundProfile") ?? SoundProfile.realistic.rawValue
        self.soundProfile = SoundProfile(rawValue: savedProfileStr) ?? .realistic
    }

    public func recordShot() {
        DispatchQueue.main.async {
            self.totalShotsFired += 1
            self.lastActionText = "💥 BLAST (#\(self.totalShotsFired))"
        }
    }

    public func recordReload() {
        DispatchQueue.main.async {
            self.totalReloads += 1
            self.lastActionText = "🔄 RELOAD (#\(self.totalReloads))"
        }
    }
}
