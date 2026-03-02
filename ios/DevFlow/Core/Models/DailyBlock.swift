import Foundation
import SwiftData

enum BlockCategory: String, Codable, CaseIterable {
    case work = "work"
    case learn = "learn"
    case health = "health"
    case rest = "rest"
    case meal = "meal"
    case other = "other"
    
    var displayName: String {
        switch self {
        case .work: return "Công việc"
        case .learn: return "Học tập"
        case .health: return "Sức khỏe"
        case .rest: return "Nghỉ ngơi"
        case .meal: return "Ăn uống"
        case .other: return "Khác"
        }
    }
    
    var color: String {
        switch self {
        case .work: return "FF6B6B"
        case .learn: return "4ECDC4"
        case .health: return "45B7D1"
        case .rest: return "96CEB4"
        case .meal: return "FFEAA7"
        case .other: return "A29BFE"
        }
    }
}

@Model
final class DailyBlock {
    var startTime: Date
    var endTime: Date
    var title: String
    var category: BlockCategory = .other
    var description: String = ""
    var isCompleted: Bool = false
    var createdAt: Date = Date()
    var updatedAt: Date = Date()
    var notificationEnabled: Bool = true
    var focusModeIntegration: Bool = false
    
    init(
        startTime: Date,
        endTime: Date,
        title: String,
        category: BlockCategory = .other,
        description: String = "",
        isCompleted: Bool = false
    ) {
        self.startTime = startTime
        self.endTime = endTime
        self.title = title
        self.category = category
        self.description = description
        self.isCompleted = isCompleted
    }
    
    var duration: TimeInterval {
        endTime.timeIntervalSince(startTime)
    }
    
    var durationInMinutes: Int {
        Int(duration / 60)
    }
    
    var isCurrentBlock: Bool {
        let now = Date()
        return now >= startTime && now < endTime
    }
    
    var timeRemaining: TimeInterval {
        max(0, endTime.timeIntervalSinceNow)
    }
    
    var timeRemainingMinutes: Int {
        Int(timeRemaining / 60)
    }
}
