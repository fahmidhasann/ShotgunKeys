import Foundation
import AppKit
import ApplicationServices

public class KeyTapManager {
    public static let shared = KeyTapManager()

    private var eventTap: CFMachPort?
    private var runLoopSource: CFRunLoopSource?
    private var globalMonitor: Any?
    private var localMonitor: Any?
    private var permissionTimer: Timer?

    // Common macOS Keycodes
    public static let kVK_Space: Int64 = 49
    public static let kVK_Return: Int64 = 36
    public static let kVK_ANSI_KeypadEnter: Int64 = 76

    private init() {}

    public func start() {
        checkAndRequestAccessibility()
        startPermissionMonitoring()
        setupEventTap()
        setupLocalMonitor()
    }

    public func stop() {
        if let tap = eventTap {
            CGEvent.tapEnable(tap: tap, enable: false)
            if let src = runLoopSource {
                CFRunLoopRemoveSource(CFRunLoopGetMain(), src, .commonModes)
            }
            eventTap = nil
            runLoopSource = nil
        }
        if let gm = globalMonitor {
            NSEvent.removeMonitor(gm)
            globalMonitor = nil
        }
        if let lm = localMonitor {
            NSEvent.removeMonitor(lm)
            localMonitor = nil
        }
        permissionTimer?.invalidate()
        permissionTimer = nil
    }

    public func checkAccessibilityStatus() -> Bool {
        let trusted = AXIsProcessTrusted()
        DispatchQueue.main.async {
            AppState.shared.isAccessibilityGranted = trusted
        }
        return trusted
    }

    public func checkAndRequestAccessibility() {
        let options: NSDictionary = [kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String: true]
        let trusted = AXIsProcessTrustedWithOptions(options)
        DispatchQueue.main.async {
            AppState.shared.isAccessibilityGranted = trusted
        }
    }

    public func openAccessibilitySettings() {
        if let url = URL(string: "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility") {
            NSWorkspace.shared.open(url)
        }
    }

    private func startPermissionMonitoring() {
        permissionTimer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            guard let self = self else { return }
            let isTrusted = self.checkAccessibilityStatus()
            if isTrusted && self.eventTap == nil {
                self.setupEventTap()
            }
        }
    }

    private func setupEventTap() {
        guard eventTap == nil else { return }
        
        let mask = (1 << CGEventType.keyDown.rawValue)
        
        let callback: CGEventTapCallBack = { (proxy, type, event, refcon) -> Unmanaged<CGEvent>? in
            if type == .tapDisabledByTimeout || type == .tapDisabledByUserInput {
                if let tap = KeyTapManager.shared.eventTap {
                    CGEvent.tapEnable(tap: tap, enable: true)
                }
                return Unmanaged.passUnretained(event)
            }

            if type == .keyDown {
                let keyCode = event.getIntegerValueField(.keyboardEventKeycode)
                KeyTapManager.shared.handleKeyDown(keyCode: keyCode)
            }

            return Unmanaged.passUnretained(event)
        }

        guard let tap = CGEvent.tapCreate(
            tap: .cgSessionEventTap,
            place: .headInsertEventTap,
            options: .listenOnly,
            eventsOfInterest: CGEventMask(mask),
            callback: callback,
            userInfo: nil
        ) else {
            // If CGEventTap fails (e.g. before accessibility permission), fallback to global monitor
            setupGlobalMonitorFallback()
            return
        }

        self.eventTap = tap
        let source = CFMachPortCreateRunLoopSource(kCFAllocatorDefault, tap, 0)
        self.runLoopSource = source
        CFRunLoopAddSource(CFRunLoopGetMain(), source, .commonModes)
        CGEvent.tapEnable(tap: tap, enable: true)
    }

    private func setupGlobalMonitorFallback() {
        guard globalMonitor == nil else { return }
        globalMonitor = NSEvent.addGlobalMonitorForEvents(matching: .keyDown) { [weak self] event in
            self?.handleKeyDown(keyCode: Int64(event.keyCode))
        }
    }

    private func setupLocalMonitor() {
        guard localMonitor == nil else { return }
        localMonitor = NSEvent.addLocalMonitorForEvents(matching: .keyDown) { [weak self] event in
            self?.handleKeyDown(keyCode: Int64(event.keyCode))
            return event
        }
    }

    public func handleKeyDown(keyCode: Int64) {
        guard AppState.shared.isEnabled else { return }

        let isSpace = (keyCode == KeyTapManager.kVK_Space)
        let isEnter = (keyCode == KeyTapManager.kVK_Return || keyCode == KeyTapManager.kVK_ANSI_KeypadEnter)

        if (isSpace && AppState.shared.reloadOnSpace) || (isEnter && AppState.shared.reloadOnEnter) {
            // Space or Enter -> Shotgun Reload
            SoundEngine.shared.playReload()
        } else {
            // Any other key -> Shotgun Blast
            SoundEngine.shared.playShotgunBlast()
        }
    }
}
