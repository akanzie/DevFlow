import Foundation
import SwiftUI
import SwiftData

@Observable
class PlannerViewModel {
    var blocks: [DailyBlock] = []
    var currentDate: Date = Date()
    var isMorningPerson: Bool = true
    var selectedDate: Date = Date()
    
    private(set) var currentBlock: DailyBlock?
    private(set) var upcomingBlock: DailyBlock?
    
    init(isMorningPerson: Bool = true) {
        self.isMorningPerson = isMorningPerson
        generateTodaySchedule()
    }
    
    func generateTodaySchedule() {
        let service = PlannerService.shared
        blocks = service.generateDefaultSchedule(isMorningPerson: isMorningPerson, for: currentDate)
        updateCurrentBlock()
    }
    
    func generateScheduleForDate(_ date: Date) {
        let service = PlannerService.shared
        blocks = service.generateDefaultSchedule(isMorningPerson: isMorningPerson, for: date)
    }
    
    func updateCurrentBlock() {
        let service = PlannerService.shared
        currentBlock = service.getCurrentBlock(from: blocks)
        upcomingBlock = service.getUpcomingBlock(from: blocks)
    }
    
    func toggleBlockCompletion(_ block: DailyBlock) {
        if let index = blocks.firstIndex(of: block) {
            blocks[index].isCompleted.toggle()
        }
    }
    
    func deleteBlock(_ indexSet: IndexSet) {
        blocks.remove(atOffsets: indexSet)
    }
    
    func moveBlocks(from source: IndexSet, to destination: Int) {
        blocks.move(fromOffsets: source, toOffset: destination)
    }
    
    var completionPercentage: Double {
        guard !blocks.isEmpty else { return 0 }
        let completedCount = blocks.filter { $0.isCompleted }.count
        return Double(completedCount) / Double(blocks.count)
    }
    
    var todayBlocks: [DailyBlock] {
        PlannerService.shared.getBlocksForDate(currentDate, from: blocks)
    }
}
