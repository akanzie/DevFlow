import Foundation
import SwiftData

enum HabitFrequency: Int, Codable, CaseIterable {
    case daily = 1
    case threeDaysWeek = 3
    case fourDaysWeek = 4
    case fiveDaysWeek = 5
    case weekly = 7
    
    var displayName: String {
        switch self {
        case .daily: return "Hàng ngày"
        case .threeDaysWeek: return "3 ngày/tuần"
        case .fourDaysWeek: return "4 ngày/tuần"
        case .fiveDaysWeek: return "5 ngày/tuần"
        case .weekly: return "1 lần/tuần"
        }
    }
}

@Model
final class Habit {
    var name: String
    var description: String = ""
    var frequency: HabitFrequency = .daily
    var streak: Int = 0
    var longestStreak: Int = 0
    var lastCheckedDate: Date?
    var createdAt: Date = Date()
    var updatedAt: Date = Date()
    var isActive: Bool = true
    @Relationship(deleteRule: .cascade) var checkIns: [HabitCheckIn] = []
    
    init(
        name: String,
        description: String = "",
        frequency: HabitFrequency = .daily
    ) {
        self.name = name
        self.description = description
        self.frequency = frequency
    }
    
    func checkIn(date: Date = Date()) {
        let calendar = Calendar.current
        let today = calendar.startOfDay(for: date)
        
        // Prevent duplicate check-ins on the same day
        if let lastChecked = lastCheckedDate {
            if calendar.isDateInToday(lastChecked) {
                return
            }
        }
        
        let checkIn = HabitCheckIn(date: today, habitName: name)
        checkIns.append(checkIn)
        lastCheckedDate = date
        updateStreak()
        updatedAt = Date()
    }
    
    private func updateStreak() {
        let calendar = Calendar.current
        var currentStreak = 0
        var checkDate = calendar.startOfDay(for: Date())
        
        let sortedCheckIns = checkIns.sorted { $0.date > $1.date }
        
        for checkIn in sortedCheckIns {
            if calendar.isDate(checkIn.date, inSameDayAs: checkDate) {
                currentStreak += 1
                checkDate = calendar.date(byAdding: .day, value: -1, to: checkDate) ?? checkDate
            } else if calendar.isDate(checkIn.date, inSameDayAs: calendar.date(byAdding: .day, value: -1, to: checkDate) ?? Date()) {
                currentStreak += 1
                checkDate = calendar.date(byAdding: .day, value: -1, to: checkDate) ?? checkDate
            } else {
                break
            }
        }
        
        self.streak = currentStreak
        if currentStreak > longestStreak {
            longestStreak = currentStreak
        }
    }
    
    func isCheckedInToday() -> Bool {
        let calendar = Calendar.current
        return checkIns.contains { calendar.isDateInToday($0.date) }
    }
    
    func completionPercentage(forDays days: Int) -> Double {
        let calendar = Calendar.current
        let checkInDates = Set(checkIns.map { calendar.startOfDay(for: $0.date) })
        
        var completedDays = 0
        for i in 0..<days {
            let date = calendar.date(byAdding: .day, value: -i, to: Date()) ?? Date()
            if checkInDates.contains(calendar.startOfDay(for: date)) {
                completedDays += 1
            }
        }
        
        return Double(completedDays) / Double(days)
    }
}

@Model
final class HabitCheckIn {
    var date: Date
    var habitName: String
    var createdAt: Date = Date()
    
    init(date: Date, habitName: String) {
        self.date = date
        self.habitName = habitName
    }
}
