import Foundation
import SwiftData

enum MoodLevel: Int, Codable, CaseIterable {
    case veryBad = 1
    case bad = 2
    case neutral = 3
    case good = 4
    case excellent = 5
    
    var emoji: String {
        switch self {
        case .veryBad: return "😢"
        case .bad: return "😟"
        case .neutral: return "😐"
        case .good: return "🙂"
        case .excellent: return "😄"
        }
    }
    
    var displayName: String {
        switch self {
        case .veryBad: return "Rất tệ"
        case .bad: return "Tệ"
        case .neutral: return "Bình thường"
        case .good: return "Tốt"
        case .excellent: return "Tuyệt vời"
        }
    }
}

enum EnergyLevel: Int, Codable, CaseIterable {
    case exhausted = 1
    case low = 2
    case medium = 3
    case high = 4
    case veryHigh = 5
    
    var displayName: String {
        switch self {
        case .exhausted: return "Kiệt sức"
        case .low: return "Thấp"
        case .medium: return "Trung bình"
        case .high: return "Cao"
        case .veryHigh: return "Rất cao"
        }
    }
}

@Model
final class BurnoutCheckIn {
    var date: Date = Date()
    var mood: MoodLevel = .neutral
    var energy: EnergyLevel = .medium
    var notes: String = ""
    var createdAt: Date = Date()
    
    init(
        date: Date = Date(),
        mood: MoodLevel = .neutral,
        energy: EnergyLevel = .medium,
        notes: String = ""
    ) {
        self.date = date
        self.mood = mood
        self.energy = energy
        self.notes = notes
    }
    
    var score: Double {
        Double(mood.rawValue + energy.rawValue) / 10.0
    }
    
    var isBurnoutRisk: Bool {
        mood.rawValue <= 2 && energy.rawValue <= 2
    }
}

@Model
final class BurnoutReport {
    var weekStartDate: Date
    var weekEndDate: Date
    var avgMood: Double = 0.0
    var avgEnergy: Double = 0.0
    var burnoutRiskDays: Int = 0
    var recommendations: [String] = []
    var createdAt: Date = Date()
    
    init(weekStartDate: Date, weekEndDate: Date) {
        self.weekStartDate = weekStartDate
        self.weekEndDate = weekEndDate
    }
}
