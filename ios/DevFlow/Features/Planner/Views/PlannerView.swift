import SwiftUI

struct PlannerView: View {
    @Environment(\.modelContext) private var context
    @Query(sort: \DailyBlock.startTime) private var blocks: [DailyBlock]
    @State private var viewModel = PlannerViewModel()
    @State private var showAddBlock = false
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color(UIColor.systemBackground)
                    .ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Header with current block
                    currentBlockWidget
                        .padding()
                        .background(Color(UIColor.secondarySystemBackground))
                    
                    // Timeline
                    ScrollView {
                        VStack(spacing: 12) {
                            ForEach(viewModel.todayBlocks, id: \.self) { block in
                                TimelineBlockView(block: block) {
                                    toggleBlockCompletion(block)
                                }
                            }
                        }
                        .padding()
                    }
                }
                
                // Floating action button
                VStack {
                    HStack {
                        Spacer()
                        Button(action: { showAddBlock = true }) {
                            Image(systemName: "plus.circle.fill")
                                .font(.system(size: 56))
                                .foregroundColor(.accentColor)
                        }
                        .padding()
                    }
                    Spacer()
                }
            }
            .navigationTitle("Planner")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    DatePicker(
                        "Select date",
                        selection: $viewModel.currentDate,
                        displayedComponents: .date
                    )
                    .onChange(of: viewModel.currentDate) { oldValue, newValue in
                        viewModel.generateScheduleForDate(newValue)
                    }
                }
            }
            .sheet(isPresented: $showAddBlock) {
                AddBlockSheet(isPresented: $showAddBlock) { block in
                    context.insert(block)
                }
            }
        }
        .onAppear {
            viewModel.blocks = blocks as [DailyBlock]
            viewModel.updateCurrentBlock()
        }
        .onChange(of: blocks) { oldValue, newValue in
            viewModel.blocks = newValue as [DailyBlock]
        }
    }
    
    private var currentBlockWidget: some View {
        VStack(alignment: .leading, spacing: 8) {
            if let current = viewModel.currentBlock {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Đang thực hiện")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            Text(current.title)
                                .font(.headline)
                                .foregroundColor(.white)
                            
                            Text("Còn \(current.timeRemainingMinutes) phút")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        
                        Spacer()
                        
                        CircularProgressView(
                            progress: (current.duration - current.timeRemaining) / current.duration,
                            size: 60,
                            color: Color(hex: current.category.color)
                        )
                    }
                    
                    HStack(spacing: 8) {
                        Button(action: { toggleBlockCompletion(current) }) {
                            Label("Hoàn thành", systemImage: "checkmark.circle")
                                .font(.caption)
                        }
                        .buttonStyle(.bordered)
                        
                        Button(action: {}) {
                            Label("Focus Mode", systemImage: "focus.viewfinder")
                                .font(.caption)
                        }
                        .buttonStyle(.bordered)
                    }
                }
                .padding()
                .background(Color(hex: current.category.color).opacity(0.2))
                .cornerRadius(12)
            } else {
                Text("Không có lịch nào được thực hiện")
                    .foregroundColor(.secondary)
            }
        }
    }
    
    private func toggleBlockCompletion(_ block: DailyBlock) {
        if let index = viewModel.blocks.firstIndex(of: block) {
            viewModel.blocks[index].isCompleted.toggle()
        }
    }
}

struct TimelineBlockView: View {
    let block: DailyBlock
    let onToggleCompletion: () -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 12) {
                VStack(alignment: .leading, spacing: 4) {
                    HStack(spacing: 6) {
                        Text(block.title)
                            .font(.headline)
                            .lineLimit(1)
                        
                        Image(systemName: "clock")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    
                    Text("\(formattedTime(block.startTime)) - \(formattedTime(block.endTime))")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                Button(action: onToggleCompletion) {
                    Image(systemName: block.isCompleted ? "checkmark.circle.fill" : "circle")
                        .font(.title2)
                        .foregroundColor(.accentColor)
                }
            }
            .padding()
            .background(Color(UIColor.secondarySystemBackground))
            .cornerRadius(8)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(Color(hex: block.category.color), lineWidth: 2)
            )
            
            if block.isCurrentBlock {
                HStack(spacing: 4) {
                    Image(systemName: "play.circle.fill")
                        .font(.caption)
                        .foregroundColor(.green)
                    Text("Đang diễn ra")
                        .font(.caption)
                        .foregroundColor(.green)
                }
                .padding(.leading)
            }
        }
    }
    
    private func formattedTime(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm"
        return formatter.string(from: date)
    }
}

struct AddBlockSheet: View {
    @Binding var isPresented: Bool
    var onAdd: (DailyBlock) -> Void
    
    @State private var title = ""
    @State private var startTime = Date()
    @State private var endTime = Date().addingTimeInterval(3600)
    @State private var selectedCategory: BlockCategory = .other
    
    var body: some View {
        NavigationStack {
            Form {
                Section("Chi tiết Block") {
                    TextField("Tiêu đề", text: $title)
                    
                    Picker("Danh mục", selection: $selectedCategory) {
                        ForEach(BlockCategory.allCases, id: \.self) { category in
                            Text(category.displayName).tag(category)
                        }
                    }
                }
                
                Section("Thời gian") {
                    DatePicker("Bắt đầu", selection: $startTime, displayedComponents: [.hourAndMinute])
                    DatePicker("Kết thúc", selection: $endTime, displayedComponents: [.hourAndMinute])
                }
                
                Button(action: addBlock) {
                    Text("Thêm Block")
                }
                .disabled(title.trimmingCharacters(in: .whitespaces).isEmpty)
            }
            .navigationTitle("Thêm Block mới")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Hủy") { isPresented = false }
                }
            }
        }
    }
    
    private func addBlock() {
        let block = DailyBlock(
            startTime: startTime,
            endTime: endTime,
            title: title,
            category: selectedCategory
        )
        onAdd(block)
        isPresented = false
    }
}

struct CircularProgressView: View {
    let progress: Double
    let size: CGFloat
    let color: Color
    
    var body: some View {
        ZStack {
            Circle()
                .stroke(Color.gray.opacity(0.3), lineWidth: 4)
            
            Circle()
                .trim(from: 0, to: progress)
                .stroke(color, style: StrokeStyle(lineWidth: 4, lineCap: .round))
                .rotationEffect(.degrees(-90))
            
            Text("\(Int(progress * 100))%")
                .font(.caption)
                .fontWeight(.semibold)
        }
        .frame(width: size, height: size)
    }
}

#Preview {
    PlannerView()
        .modelContainer(for: DailyBlock.self)
}
