import Foundation
import SwiftData

class PlannerService {
    static let shared = PlannerService()
    
    private init() {}
    
    // Predefined schedules
    static let morningPersonSchedule: [(String, Int, Int, BlockCategory)] = [
        ("Thức dậy", 5, 30, .health),
        ("Tập thể dục", 5, 45, .health),
        ("Tắm", 6, 15, .health),
        ("Ăn sáng", 6, 30, .meal),
        ("Chuẩn bị đi làm", 7, 0, .work),
        ("Làm việc (ca 1)", 8, 0, .work),
        ("Nghỉ trưa", 12, 0, .meal),
        ("Làm việc (ca 2)", 13, 0, .work),
        ("Café/Xả stress", 17, 0, .rest),
        ("Học code/Skill", 18, 0, .learn),
        ("Ăn tối", 19, 30, .meal),
        ("Giải trí", 20, 30, .rest),
        ("Chuẩn bị ngủ", 22, 30, .rest),
        ("Ngủ", 23, 0, .rest)
    ]
    
    static let nightOwlSchedule: [(String, Int, Int, BlockCategory)] = [
        ("Thức dậy", 7, 0, .health),
        ("Ăn sáng", 7, 30, .meal),
        ("Chuẩn bị đi làm", 8, 0, .work),
        ("Làm việc (ca 1)", 9, 0, .work),
        ("Nghỉ trưa", 12, 30, .meal),
        ("Làm việc (ca 2)", 13, 30, .work),
        ("Tập thể dục", 17, 0, .health),
        ("Tắm", 18, 0, .health),
        ("Ăn tối", 18, 30, .meal),
        ("Giải trí", 19, 30, .rest),
        ("Học code/Skill", 21, 0, .learn),
        ("Cafe/Xả stress", 22, 30, .rest),
        ("Chuẩn bị ngủ", 23, 30, .rest),
        ("Ngủ", 0, 30, .rest)
    ]
    
    func generateDefaultSchedule(isMorningPerson: Bool, for date: Date = Date()) -> [DailyBlock] {
        let schedule = isMorningPerson ? Self.morningPersonSchedule : Self.nightOwlSchedule
        let calendar = Calendar.current
        let tomorrow = calendar.date(byAdding: .day, value: 1, to: date) ?? date
        
        var blocks: [DailyBlock] = []
        
        for (index, (title, hour, minute, category)) in schedule.enumerated() {
            var startComponents = calendar.dateComponents([.year, .month, .day], from: date)
            startComponents.hour = hour
            startComponents.minute = minute
            
            let nextItem = index + 1
            var endComponents = calendar.dateComponents([.year, .month, .day], from: date)
            
            if nextItem < schedule.count {
                let (_, nextHour, nextMinute, _) = schedule[nextItem]
                endComponents.hour = nextHour
                endComponents.minute = nextMinute
            } else {
                // Last block goes to tomorrow
                endComponents = calendar.dateComponents([.year, .month, .day], from: tomorrow)
                endComponents.hour = schedule[0].1
                endComponents.minute = schedule[0].2
            }
            
            let startTime = calendar.date(from: startComponents) ?? date
            let endTime = calendar.date(from: endComponents) ?? date
            
            let block = DailyBlock(
                startTime: startTime,
                endTime: endTime,
                title: title,
                category: category
            )
            blocks.append(block)
        }
        
        return blocks
    }
    
    func getCurrentBlock(from blocks: [DailyBlock]) -> DailyBlock? {
        blocks.first { $0.isCurrentBlock }
    }
    
    func getUpcomingBlock(from blocks: [DailyBlock]) -> DailyBlock? {
        let now = Date()
        return blocks.first { $0.startTime > now }
    }
    
    func getBlocksForDate(_ date: Date, from blocks: [DailyBlock]) -> [DailyBlock] {
        let calendar = Calendar.current
        return blocks.filter { calendar.isDate($0.startTime, inSameDayAs: date) }
    }
}
