import Foundation
import AVFoundation

public class SoundEngine {
    public static let shared = SoundEngine()

    private let audioQueue = DispatchQueue(label: "com.shotgunkeys.audioqueue", qos: .userInteractive)
    
    // Polyphonic pools
    private var blastPlayers: [AVAudioPlayer] = []
    private var reloadPlayers: [AVAudioPlayer] = []
    private var blastPoolIndex: Int = 0
    private var reloadPoolIndex: Int = 0
    
    private var blastSoundDataList: [Data] = []
    private var reloadSoundDataList: [Data] = []
    
    private let poolSize = 32
    private var volume: Float = 0.85

    /// Dynamic custom sounds directory located in Application Support
    public static var customSoundsDirectory: URL {
        let fileManager = FileManager.default
        let appSupportDir: URL
        if let userAppSupport = fileManager.urls(for: .applicationSupportDirectory, in: .userDomainMask).first {
            appSupportDir = userAppSupport.appendingPathComponent("ShotgunKeys/CustomSounds", isDirectory: true)
        } else {
            appSupportDir = fileManager.homeDirectoryForCurrentUser.appendingPathComponent("Library/Application Support/ShotgunKeys/CustomSounds", isDirectory: true)
        }

        if !fileManager.fileExists(atPath: appSupportDir.path) {
            try? fileManager.createDirectory(at: appSupportDir, withIntermediateDirectories: true, attributes: nil)
            
            // Create a helpful README in the custom sounds folder
            let readmeURL = appSupportDir.appendingPathComponent("README.txt")
            if !fileManager.fileExists(atPath: readmeURL.path) {
                let instructions = """
                ShotgunKeys - Custom Audio Folder
                =================================
                Drop your own audio files (.wav, .mp3, .m4a, .aif) into this folder!

                Naming Conventions:
                - For Blast sounds (regular keys):
                  Name files containing "blast", "shot", or "fire" (e.g. blast1.wav, my_shot.mp3).
                - For Reload sounds (Space / Enter keys):
                  Name files containing "reload", "pump", or "cock" (e.g. reload1.wav, pump.wav).

                After adding or updating files:
                Click "Reload Files" in the ShotgunKeys menu bar dropdown to load your sounds.
                """
                try? instructions.write(to: readmeURL, atomically: true, encoding: .utf8)
            }
        }
        return appSupportDir
    }

    /// List of potential custom sounds directory search paths
    private static var customSoundsSearchDirectories: [URL] {
        var dirs: [URL] = [customSoundsDirectory]

        // 1. Next to the app bundle (portable mode)
        let bundleFolder = Bundle.main.bundleURL.deletingLastPathComponent().appendingPathComponent("CustomSounds", isDirectory: true)
        dirs.append(bundleFolder)

        // 2. Inside Resources
        if let resURL = Bundle.main.resourceURL?.appendingPathComponent("CustomSounds", isDirectory: true) {
            dirs.append(resURL)
        }

        // 3. Current working directory
        let cwdDir = URL(fileURLWithPath: FileManager.default.currentDirectoryPath, isDirectory: true).appendingPathComponent("CustomSounds", isDirectory: true)
        dirs.append(cwdDir)

        return dirs
    }

    private init() {
        self.volume = Float(AppState.shared.volume)
        loadSounds(profile: AppState.shared.soundProfile, preview: false)
    }

    public func setVolume(_ vol: Float) {
        self.volume = max(0.0, min(1.0, vol))
        audioQueue.async {
            for player in self.blastPlayers {
                player.volume = self.volume
            }
            for player in self.reloadPlayers {
                player.volume = self.volume
            }
        }
    }

    public func reloadSounds() {
        loadSounds(profile: AppState.shared.soundProfile, preview: true)
    }

    public func loadSounds(profile: SoundProfile, preview: Bool = false) {
        audioQueue.async { [weak self] in
            guard let self = self else { return }
            self.blastPlayers.removeAll()
            self.reloadPlayers.removeAll()
            self.blastSoundDataList.removeAll()
            self.reloadSoundDataList.removeAll()

            if profile == .custom {
                // Load Custom User Sounds from dynamic directories
                let validExtensions = ["wav", "mp3", "m4a", "aif", "aiff"]
                var loadedFiles = Set<String>()

                for dirURL in SoundEngine.customSoundsSearchDirectories {
                    guard FileManager.default.fileExists(atPath: dirURL.path),
                          let files = try? FileManager.default.contentsOfDirectory(atPath: dirURL.path) else {
                        continue
                    }

                    for file in files {
                        let lower = file.lowercased()
                        guard !loadedFiles.contains(lower),
                              validExtensions.contains(where: { lower.hasSuffix("." + $0) }) else {
                            continue
                        }

                        let fileURL = dirURL.appendingPathComponent(file)
                        if let data = try? Data(contentsOf: fileURL) {
                            loadedFiles.insert(lower)
                            if lower.contains("blast") || lower.contains("shot") || lower.contains("fire") {
                                self.blastSoundDataList.append(data)
                            } else if lower.contains("reload") || lower.contains("pump") || lower.contains("cock") {
                                self.reloadSoundDataList.append(data)
                            } else {
                                // Generic fallback sound goes to blast
                                self.blastSoundDataList.append(data)
                            }
                        }
                    }
                }

                // Fallback to realistic if custom folder is empty
                if self.blastSoundDataList.isEmpty {
                    self.loadPresetFiles(blastNames: ["shotgun_blast_1", "shotgun_blast_2", "shotgun_blast_3", "shotgun_blast_4"],
                                         reloadNames: ["shotgun_reload_1", "shotgun_reload_2"])
                }
            } else {
                // Load Built-in Presets
                let blastNames: [String]
                let reloadNames: [String]

                switch profile {
                case .realistic:
                    blastNames = ["shotgun_blast_1", "shotgun_blast_2", "shotgun_blast_3", "shotgun_blast_4"]
                    reloadNames = ["shotgun_reload_1", "shotgun_reload_2"]
                case .tactical:
                    blastNames = ["tactical_blast_1", "tactical_blast_2", "tactical_blast_3"]
                    reloadNames = ["tactical_reload_1", "tactical_reload_2"]
                case .heavyDoom:
                    blastNames = ["doom_blast_1", "doom_blast_2"]
                    reloadNames = ["doom_reload_1", "doom_reload_2"]
                case .silenced:
                    blastNames = ["silenced_blast_1", "silenced_blast_2"]
                    reloadNames = ["silenced_reload_1", "silenced_reload_2"]
                case .cyberpunk:
                    blastNames = ["cyber_blast_1", "cyber_blast_2"]
                    reloadNames = ["cyber_reload_1", "cyber_reload_2"]
                case .arcade:
                    blastNames = ["arcade_blast"]
                    reloadNames = ["arcade_reload"]
                case .custom:
                    blastNames = ["shotgun_blast_1"]
                    reloadNames = ["shotgun_reload_1"]
                }

                self.loadPresetFiles(blastNames: blastNames, reloadNames: reloadNames)
            }

            // Build blast polyphonic pool
            if !self.blastSoundDataList.isEmpty {
                for i in 0..<self.poolSize {
                    let data = self.blastSoundDataList[i % self.blastSoundDataList.count]
                    if let player = try? AVAudioPlayer(data: data) {
                        player.enableRate = true
                        player.volume = self.volume
                        player.prepareToPlay()
                        self.blastPlayers.append(player)
                    }
                }
            }

            // Build reload polyphonic pool
            if !self.reloadSoundDataList.isEmpty {
                for i in 0..<12 {
                    let data = self.reloadSoundDataList[i % self.reloadSoundDataList.count]
                    if let player = try? AVAudioPlayer(data: data) {
                        player.enableRate = true
                        player.volume = self.volume
                        player.prepareToPlay()
                        self.reloadPlayers.append(player)
                    }
                }
            }

            if preview && AppState.shared.isEnabled {
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.05) {
                    self.playShotgunBlast()
                }
            }
        }
    }

    private func loadPresetFiles(blastNames: [String], reloadNames: [String]) {
        for name in blastNames {
            if let url = self.findSoundURL(named: name, ext: "wav"),
               let data = try? Data(contentsOf: url) {
                self.blastSoundDataList.append(data)
            }
        }
        for name in reloadNames {
            if let url = self.findSoundURL(named: name, ext: "wav"),
               let data = try? Data(contentsOf: url) {
                self.reloadSoundDataList.append(data)
            }
        }
    }

    private func findSoundURL(named: String, ext: String) -> URL? {
        if let url = Bundle.main.url(forResource: named, withExtension: ext) {
            return url
        }
        if let url = Bundle.main.url(forResource: named, withExtension: ext, subdirectory: "Assets") {
            return url
        }
        if let resURL = Bundle.main.resourceURL {
            let direct = resURL.appendingPathComponent("\(named).\(ext)")
            if FileManager.default.fileExists(atPath: direct.path) {
                return direct
            }
            let sub = resURL.appendingPathComponent("Assets/\(named).\(ext)")
            if FileManager.default.fileExists(atPath: sub.path) {
                return sub
            }
        }

        // Relative to bundle or current directory (development / standalone execution)
        let candidatePaths = [
            Bundle.main.bundleURL.deletingLastPathComponent().appendingPathComponent("Assets/\(named).\(ext)").path,
            FileManager.default.currentDirectoryPath + "/Assets/" + named + "." + ext,
            FileManager.default.currentDirectoryPath + "/" + named + "." + ext
        ]

        for path in candidatePaths {
            if FileManager.default.fileExists(atPath: path) {
                return URL(fileURLWithPath: path)
            }
        }

        return nil
    }

    public func playShotgunBlast() {
        guard AppState.shared.isEnabled else { return }
        
        audioQueue.async { [weak self] in
            guard let self = self, !self.blastPlayers.isEmpty else { return }

            let player = self.blastPlayers[self.blastPoolIndex]
            self.blastPoolIndex = (self.blastPoolIndex + 1) % self.blastPlayers.count

            if AppState.shared.pitchRandomization {
                player.rate = Float.random(in: 0.97...1.03)
                let volVariation = Float.random(in: 0.95...1.0)
                player.volume = self.volume * volVariation
            } else {
                player.rate = 1.0
                player.volume = self.volume
            }
            player.currentTime = 0
            player.play()
        }

        AppState.shared.recordShot()
    }

    public func playReload() {
        guard AppState.shared.isEnabled else { return }

        audioQueue.async { [weak self] in
            guard let self = self, !self.reloadPlayers.isEmpty else { return }

            let player = self.reloadPlayers[self.reloadPoolIndex]
            self.reloadPoolIndex = (self.reloadPoolIndex + 1) % self.reloadPlayers.count

            if AppState.shared.pitchRandomization {
                player.rate = Float.random(in: 0.98...1.02)
                let volVariation = Float.random(in: 0.96...1.0)
                player.volume = self.volume * volVariation
            } else {
                player.rate = 1.0
                player.volume = self.volume
            }
            player.currentTime = 0
            player.play()
        }

        AppState.shared.recordReload()
    }
}
