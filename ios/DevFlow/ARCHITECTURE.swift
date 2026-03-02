// DevFlow.swift
// 
// This file contains the main app configuration and entry point
// for the DevFlow iOS app.
//
// Architecture:
// - Offline-first with CloudKit sync
// - SwiftData for local persistence
// - SwiftUI for all UI
// - Modular feature-based structure
//
// Entry Point: DevFlowApp (main struct with @main macro)

import SwiftUI
import SwiftData

/// Configuration for the app
struct DevFlowConfiguration {
    /// App version from Info.plist or hardcoded
    static let version = "1.0"
    
    /// Minimum iOS version required
    static let minimumOSVersion = "17.0"
}

// MARK: - Tips

/// Tips for developing with this codebase:
///
/// 1. **Adding New Features**
///    - Create folder under Features/ with Views/ subfolder
///    - Define models in Core/Models/
///    - Create service in Core/Services/ if complex logic needed
///    - Add new tab in TabBarView
///
/// 2. **SwiftData Best Practices**
///    - Always mark models with @Model macro
///    - Use @Query(sort:) in Views for reactive data
///    - Never use @Attribute(.unique) to avoid sync conflicts
///    - Test on real device for iCloud sync
///
/// 3. **Performance**
///    - Use .limit() in @Query for long lists
///    - Avoid heavy computation in body{}
///    - Use @State for temporary UI state only
///    - Test on iPhone SE for baseline performance
///
/// 4. **Naming Conventions**
///    - Services: PlannerService, BurnoutService
///    - Views: PlannerView, HabitsView (end with "View")
///    - ViewModels: PlannerViewModel (end with "ViewModel")
///    - Models: Use clear nouns (Habit, DailyBlock, BurnoutCheckIn)
///
/// 5. **Debugging**
///    - Use print() + logs view in Xcode Console
///    - Test notifications with 5-second delay
///    - Verify iCloud sync with Settings > [Apple ID] > iCloud
///    - Check user permissions: prefs for notifications
///
/// 6. **Code Organization**
///    - Keep files <500 lines (split if needed)
///    - Separate UI logic from business logic
///    - Use extensions for code organization
///    - Comment complex algorithms
///
/// 7. **Testing**
///    - Unit test service methods
///    - UI test critical user flows
///    - Use preview #Preview { } for UI iteration
///    - Test on iOS 17 minimum (requirement)

// MARK: - Feature Flags (for future use)

struct FeatureFlags {
    static let enableWidgetKit = false // Phase 2
    static let enableHealthKit = false // Phase 2
    static let enableAI = false        // Phase 3
}
