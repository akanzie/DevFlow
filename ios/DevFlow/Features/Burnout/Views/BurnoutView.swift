import SwiftUI
import SwiftData

struct BurnoutView: View {
    @Environment(\.modelContext) private var context
    @Query(sort: \BurnoutCheckIn.date, order: .reverse) private var checkIns: [BurnoutCheckIn]
    @State private var showCheckIn = false
    @State private var weeklyReport: BurnoutReport?
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color(UIColor.systemBackground)
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 16) {
                        // Check-in button
                        Button(action: { showCheckIn = true }) {
                            HStack {
                                Image(systemName: "heart.circle.fill")
                                    .font(.title2)
                                
                                VStack(alignment: .leading) {
                                    Text("Burnout Check-in")
                                        .font(.headline)
                                    Text("Cập nhật tâm trạng và năng lượng")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                }
                                
                                Spacer()
                                
                                Image(systemName: "chevron.right")
                                    .foregroundColor(.secondary)
                            }
                            .padding()
                            .background(Color(UIColor.secondarySystemBackground))
                            .cornerRadius(12)
                        }
                        .foregroundColor(.primary)
                        
                        // Weekly report
                        if let report = weeklyReport {
                            BurnoutReportCard(report: report)
                        }
                        
                        // Recent check-ins
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Lịch sử gần đây")
                                .font(.headline)
                                .padding(.horizontal)
                            
                            ForEach(checkIns.prefix(7), id: \.self) { checkIn in
                                BurnoutCheckInRow(checkIn: checkIn)
                            }
                        }
                    }
                    .padding()
                }
            }
            .navigationTitle("Burnout Guard")
            .navigationBarTitleDisplayMode(.inline)
            .sheet(isPresented: $showCheckIn) {
                BurnoutCheckInSheet(isPresented: $showCheckIn) { newCheckIn in
                    context.insert(newCheckIn)
                    updateWeeklyReport()
                }
            }
            .onAppear {
                updateWeeklyReport()
            }
        }
    }
    
    private func updateWeeklyReport() {
        weeklyReport = BurnoutService.shared.calculateWeeklyReport(from: checkIns)
    }
}

struct BurnoutReportCard: View {
    let report: BurnoutReport
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Báo cáo tuần này")
                .font(.headline)
            
            HStack(spacing: 16) {
                StatCell(label: "Tâm trạng", value: String(format: "%.1f", report.avgMood), maxValue: "5.0")
                StatCell(label: "Năng lượng", value: String(format: "%.1f", report.avgEnergy), maxValue: "5.0")
                StatCell(label: "Ngày nguy hiểm", value: "\(report.burnoutRiskDays)", maxValue: "7")
            }
            
            Divider()
            
            VStack(alignment: .leading, spacing: 4) {
                Text("Gợi ý")
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                ForEach(report.recommendations, id: \.self) { rec in
                    Text(rec)
                        .font(.caption)
                        .lineLimit(2)
                }
            }
        }
        .padding()
        .background(Color(UIColor.secondarySystemBackground))
        .cornerRadius(12)
    }
}

struct StatCell: View {
    let label: String
    let value: String
    let maxValue: String
    
    var body: some View {
        VStack(alignment: .center, spacing: 4) {
            Text(value)
                .font(.title3)
                .fontWeight(.bold)
            
            Text(label)
                .font(.caption2)
                .foregroundColor(.secondary)
            
            Text("/ \(maxValue)")
                .font(.caption2)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color(UIColor.tertiarySystemBackground))
        .cornerRadius(8)
    }
}

struct BurnoutCheckInRow: View {
    let checkIn: BurnoutCheckIn
    
    var body: some View {
        HStack(spacing: 12) {
            VStack(alignment: .center, spacing: 4) {
                Text(checkIn.mood.emoji)
                    .font(.title)
                Text("Tâm trạng")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
            
            VStack(alignment: .center, spacing: 4) {
                Image(systemName: "bolt.fill")
                    .foregroundColor(.yellow)
                Text(checkIn.energy.displayName)
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            Text(checkIn.date.formatted(date: .abbreviated, time: .omitted))
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .background(Color(UIColor.secondarySystemBackground))
        .cornerRadius(8)
    }
}

struct BurnoutCheckInSheet: View {
    @Binding var isPresented: Bool
    var onAdd: (BurnoutCheckIn) -> Void
    
    @State private var selectedMood: MoodLevel = .neutral
    @State private var selectedEnergy: EnergyLevel = .medium
    @State private var notes = ""
    
    var body: some View {
        NavigationStack {
            Form {
                Section("Tâm trạng") {
                    HStack(spacing: 16) {
                        ForEach(MoodLevel.allCases, id: \.self) { mood in
                            Button(action: { selectedMood = mood }) {
                                VStack {
                                    Text(mood.emoji)
                                        .font(.title)
                                    Text(mood.displayName)
                                        .font(.caption2)
                                }
                                .frame(maxWidth: .infinity)
                                .padding(8)
                                .background(selectedMood == mood ? Color.blue.opacity(0.2) : Color.gray.opacity(0.1))
                                .cornerRadius(8)
                            }
                        }
                    }
                }
                
                Section("Năng lượng") {
                    Picker("Năng lượng", selection: $selectedEnergy) {
                        ForEach(EnergyLevel.allCases, id: \.self) { energy in
                            Text(energy.displayName).tag(energy)
                        }
                    }
                }
                
                Section("Ghi chú") {
                    TextEditor(text: $notes)
                        .frame(height: 100)
                }
                
                Button(action: submitCheckIn) {
                    Text("Lưu Check-in")
                }
            }
            .navigationTitle("Burnout Check-in")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Hủy") { isPresented = false }
                }
            }
        }
    }
    
    private func submitCheckIn() {
        let checkIn = BurnoutCheckIn(
            mood: selectedMood,
            energy: selectedEnergy,
            notes: notes
        )
        onAdd(checkIn)
        isPresented = false
    }
}

#Preview {
    BurnoutView()
        .modelContainer(for: BurnoutCheckIn.self)
}
