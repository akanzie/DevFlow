// Package.swift - SwiftUI Preview Content
// Quick stubs for preview/demo data

import SwiftUI
import SwiftData

// MARK: - Preview Helpers

struct PreviewData {
    static var sampleBlock: DailyBlock {
        let now = Date()
        let calendar = Calendar.current
        let startTime = calendar.date(byAdding: .hour, value: 1, to: now)!
        let endTime = calendar.date(byAdding: .hour, value: 2, to: startTime)!
        
        return DailyBlock(
            startTime: startTime,
            endTime: endTime,
            title: "LeetCode Practice",
            category: .learn,
            description: "Work on medium level DSA problems"
        )
    }
    
    static var sampleBlocks: [DailyBlock] {
        let service = PlannerService.shared
        return service.generateDefaultSchedule(isMorningPerson: true)
    }
    
    static var sampleHabit: Habit {
        let habit = Habit(name: "Gym 4x/tuần", frequency: .fourDaysWeek)
        // Add some mock check-ins
        let calendar = Calendar.current
        for i in 0..<7 {
            let date = calendar.date(byAdding: .day, value: -i, to: Date())!
            if i % 2 == 0 {
                let checkIn = HabitCheckIn(date: date, habitName: "Gym")
                habit.checkIns.append(checkIn)
            }
        }
        habit.updateStreak()
        return habit
    }
    
    static var sampleNote: QuickNote {
        QuickNote(
            content: "SwiftData supports relationships automatically. Remember to test on real device!",
            tags: ["learning", "swift"],
            isVoiceNote: false
        )
    }
    
    static var sampleCheckIn: BurnoutCheckIn {
        BurnoutCheckIn(
            mood: .good,
            energy: .high,
            notes: "Had a productive day, finished feature implementation"
        )
    }
    
    static func modelContainer() -> ModelContainer {
        let container = try! ModelContainer(
            for: DailyBlock.self, Habit.self, QuickNote.self,
            BurnoutCheckIn.self, FeedItem.self,
            configurations: ModelConfiguration(isStoredInMemoryOnly: true)
        )
        return container
    }
}

// MARK: - Mock Services

class MockFeedService {
    static let mockFeeds: [FeedItem] = [
        FeedItem(
            title: "State of Swift 2026",
            description: "Latest developments in Swift language and ecosystem",
            url: "https://example.com/1",
            source: "Dev.to",
            publicationDate: Date()
        ),
        FeedItem(
            title: "Burnout Recovery: A Developer's Guide",
            description: "How to recognize and recover from burnout",
            url: "https://example.com/2",
            source: "Viblo",
            publicationDate: Date().addingTimeInterval(-3600)
        ),
    ]
}

// MARK: - Preview Modifiers

extension View {
    func previewWithContainer() -> some View {
        modelContainer(PreviewData.modelContainer())
    }
}

// MARK: - Mock Extensions

extension Habit {
    mutating func updateStreak() {
        let calendar = Calendar.current
        var currentStreak = 0
        var checkDate = calendar.startOfDay(for: Date())
        
        let sortedCheckIns = checkIns.sorted { $0.date > $1.date }
        
        for checkIn in sortedCheckIns {
            if calendar.isDate(checkIn.date, inSameDayAs: checkDate) {
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
}
