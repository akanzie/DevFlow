import Foundation

class BurnoutService {
    static let shared = BurnoutService()
    
    private init() {}
    
    func calculateWeeklyReport(from checkIns: [BurnoutCheckIn]) -> BurnoutReport? {
        guard !checkIns.isEmpty else { return nil }
        
        let calendar = Calendar.current
        let today = Date()
        let weekAgo = calendar.date(byAdding: .day, value: -7, to: today) ?? today
        
        let weekCheckIns = checkIns.filter { $0.date >= weekAgo && $0.date <= today }
        guard !weekCheckIns.isEmpty else { return nil }
        
        let weekStart = calendar.startOfDay(for: weekAgo)
        let weekEnd = calendar.startOfDay(for: today)
        
        let report = BurnoutReport(weekStartDate: weekStart, weekEndDate: weekEnd)
        
        let avgMood = Double(weekCheckIns.map { $0.mood.rawValue }.reduce(0, +)) / Double(weekCheckIns.count)
        let avgEnergy = Double(weekCheckIns.map { $0.energy.rawValue }.reduce(0, +)) / Double(weekCheckIns.count)
        let burnoutRiskDays = weekCheckIns.filter { $0.isBurnoutRisk }.count
        
        report.avgMood = avgMood
        report.avgEnergy = avgEnergy
        report.burnoutRiskDays = burnoutRiskDays
        
        report.recommendations = generateRecommendations(
            avgMood: avgMood,
            avgEnergy: avgEnergy,
            burnoutRiskDays: burnoutRiskDays
        )
        
        return report
    }
    
    private func generateRecommendations(avgMood: Double, avgEnergy: Double, burnoutRiskDays: Int) -> [String] {
        var recommendations: [String] = []
        
        if avgMood < 2.5 {
            recommendations.append("😟 Tâm trạng không tốt - hãy dành thời gian nghỉ ngơi và hoạt động yêu thích")
        }
        
        if avgEnergy < 2.5 {
            recommendations.append("⚡️ Năng lượng thấp - hãy tập luyện thể dục và ngủ đủ giấc")
        }
        
        if burnoutRiskDays >= 2 {
            recommendations.append("🚨 Nguy hiểm burnout - hãy nghỉ 1 ngày code-free hoặc tập yoga thả lỏng")
        }
        
        if avgMood >= 4 && avgEnergy >= 4 {
            recommendations.append("💪 Tuyệt vời! Hãy giữ vững tinh thần này và tiếp tục phát triển kỹ năng")
        }
        
        if recommendations.isEmpty {
            recommendations.append("✅ Tình trạng bình thường - hãy duy trì thói quen tốt của bạn")
        }
        
        return recommendations
    }
    
    func checkConsecutiveLowMood(from checkIns: [BurnoutCheckIn]) -> Bool {
        let sortedCheckIns = checkIns.sorted { $0.date > $1.date }
        
        if sortedCheckIns.count >= 2 {
            let today = sortedCheckIns[0]
            let yesterday = sortedCheckIns[1]
            
            return today.mood.rawValue <= 2 && yesterday.mood.rawValue <= 2
        }
        
        return false
    }
}
