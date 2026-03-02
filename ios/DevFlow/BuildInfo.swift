// BuildInfo.swift
// Contains build configuration and version management

import Foundation

struct BuildInfo {
    // Version
    static let appVersion = "1.0"
    static let buildNumber = 1
    static let bundleIdentifier = "com.devflow.app"
    
    // Release Configuration
    static let isProduction = false
    static let isTestFlight = false
    static let isSimulator = ProcessInfo.processInfo.environment["SIMULATOR_DEVICE_NAME"] != nil
    
    // Build Metadata
    static let buildDate: Date = {
        // Update this when creating release build
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd HH:mm:ss"
        return formatter.date(from: "2026-03-02 00:00:00") ?? Date()
    }()
    
    static let minimumOSVersion = "17.0"
    static let targetOSVersion = "19.0" // Target iOS 18/19
    
    // Feature Flags
    static let featuresEnabled: [String: Bool] = [
        "widgetKit": false,       // Phase 2
        "healthKit": false,       // Phase 2
        "deeplinks": false,       // Phase 2
        "appleIntelligence": false, // Phase 3
        "subscription": false,    // Phase 3
        "cloudBackup": false,     // Future
    ]
    
    // Debug Flags
    #if DEBUG
    static let isDebug = true
    static let logLevel = "verbose"
    static let mockNetwork = true
    #else
    static let isDebug = false
    static let logLevel = "warning"
    static let mockNetwork = false
    #endif
    
    static func description() -> String {
        return """
        ╔═══════════════════════════════════════════════╗
        ║           DevFlow Build Information           ║
        ╠═══════════════════════════════════════════════╣
        ║ Version:           \(appVersion) (Build \(buildNumber))
        ║ Bundle ID:         \(bundleIdentifier)
        ║ Min OS:            iOS \(minimumOSVersion)
        ║ Target OS:         iOS \(targetOSVersion)
        ║ Build Date:        \(DateFormatter().string(from: buildDate))
        ║ Simulator:         \(isSimulator ? "Yes" : "No")
        ║ Debug Build:       \(isDebug ? "Yes" : "No")
        ║ Production:        \(isProduction ? "Yes" : "No")
        ╚═══════════════════════════════════════════════╝
        """
    }
}

// Singleton Logger
class Logger {
    static let shared = Logger()
    
    enum Level: String {
        case verbose = "🔵 VERBOSE"
        case debug = "🟢 DEBUG"
        case info = "🔵 INFO"
        case warning = "🟡 WARNING"
        case error = "🔴 ERROR"
        case critical = "⛔️ CRITICAL"
    }
    
    private init() {}
    
    func log(_ message: String, level: Level = .info, file: String = #file, line: Int = #line) {
        #if DEBUG
        let filename = URL(fileURLWithPath: file).lastPathComponent
        let timestamp = DateFormatter().string(from: Date())
        print("[\(timestamp)] [\(level.rawValue)] [\(filename):\(line)] \(message)")
        #endif
    }
    
    func verbose(_ message: String, file: String = #file, line: Int = #line) {
        log(message, level: .verbose, file: file, line: line)
    }
    
    func debug(_ message: String, file: String = #file, line: Int = #line) {
        log(message, level: .debug, file: file, line: line)
    }
    
    func info(_ message: String, file: String = #file, line: Int = #line) {
        log(message, level: .info, file: file, line: line)
    }
    
    func warning(_ message: String, file: String = #file, line: Int = #line) {
        log(message, level: .warning, file: file, line: line)
    }
    
    func error(_ message: String, file: String = #file, line: Int = #line) {
        log(message, level: .error, file: file, line: line)
    }
    
    func critical(_ message: String, file: String = #file, line: Int = #line) {
        log(message, level: .critical, file: file, line: line)
    }
}

// Convenience shorthand
let logger = Logger.shared
