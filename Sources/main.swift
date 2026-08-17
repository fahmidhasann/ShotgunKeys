import Cocoa

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.setActivationPolicy(.accessory) // Menu bar app
_ = NSApplicationMain(CommandLine.argc, CommandLine.unsafeArgv)
