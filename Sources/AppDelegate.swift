import Cocoa
import SwiftUI

public class AppDelegate: NSObject, NSApplicationDelegate {
    private var statusItem: NSStatusItem!
    private var popover: NSPopover!
    private var eventMonitor: Any?

    public func applicationDidFinishLaunching(_ notification: Notification) {
        // Initialize Sound Engine
        _ = SoundEngine.shared

        // Setup Menu Bar Status Item
        setupStatusItem()

        // Setup Popover with SwiftUI MenuView
        setupPopover()

        // Start Keyboard Interceptor
        KeyTapManager.shared.start()
    }

    private func setupStatusItem() {
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)

        if let button = statusItem.button {
            // SF Symbol shotgun/flame icon with fallback
            if let image = NSImage(systemSymbolName: "flame.fill", accessibilityDescription: "ShotgunKeys") {
                let config = NSImage.SymbolConfiguration(pointSize: 13, weight: .semibold)
                button.image = image.withSymbolConfiguration(config)
            } else {
                button.title = "💥"
            }
            button.action = #selector(togglePopover(_:))
            button.target = self
        }
    }

    private func setupPopover() {
        popover = NSPopover()
        popover.contentSize = NSSize(width: 330, height: 530)
        popover.behavior = .transient
        popover.animates = true
        popover.contentViewController = NSHostingController(rootView: MenuView())
    }

    @objc private func togglePopover(_ sender: AnyObject?) {
        guard let button = statusItem.button else { return }

        if popover.isShown {
            closePopover(sender)
        } else {
            showPopover(button)
        }
    }

    private func showPopover(_ button: NSStatusBarButton) {
        _ = KeyTapManager.shared.checkAccessibilityStatus()
        popover.show(relativeTo: button.bounds, of: button, preferredEdge: .minY)
        
        // Monitor global clicks outside to dismiss
        eventMonitor = NSEvent.addGlobalMonitorForEvents(matching: [.leftMouseDown, .rightMouseDown]) { [weak self] _ in
            self?.closePopover(nil)
        }
    }

    private func closePopover(_ sender: AnyObject?) {
        if popover.isShown {
            popover.performClose(sender)
        }
        if let monitor = eventMonitor {
            NSEvent.removeMonitor(monitor)
            eventMonitor = nil
        }
    }

    public func applicationWillTerminate(_ notification: Notification) {
        KeyTapManager.shared.stop()
    }
}
