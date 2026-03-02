import Foundation

struct AppConstants {
    static let appName = "DevFlow"
    static let appVersion = "1.0.0"
    static let miniumOSVersion = "17.0"
    
    // CloudKit Configuration
    static let cloudKitContainerId = "iCloud.com.devflow.app"
    static let cloudKitPrivateDatabase = "private"
    
    // Notifications
    static let blockReminderMinutesBefore = 5
    static let dailyCheckInTime: (hour: Int, minute: Int) = (21, 0)
    
    // Widget
    static let widgetRefreshInterval: TimeInterval = 15 * 60 // 15 minutes
    
    // Habits
    static let defaultHabits = [
        ("Tập thể dục", HabitFrequency.fourDaysWeek),
        ("Học code", HabitFrequency.daily),
        ("Ngủ đủ 7h+", HabitFrequency.daily),
        ("Commit GitHub", HabitFrequency.daily),
    ]
    
    // UI
    static let cornerRadius: CGFloat = 12
    static let shadowRadius: CGFloat = 8
    static let animationDuration: TimeInterval = 0.3
}
