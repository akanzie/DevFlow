import SwiftUI
import SwiftData

struct HabitsView: View {
    @Environment(\.modelContext) private var context
    @Query(sort: \Habit.createdAt) private var habits: [Habit]
    @State private var showAddHabit = false
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color(UIColor.systemBackground)
                    .ignoresSafeArea()
                
                VStack {
                    if habits.isEmpty {
                        emptyState
                    } else {
                        habitsList
                    }
                }
                
                VStack {
                    HStack {
                        Spacer()
                        Button(action: { showAddHabit = true }) {
                            Image(systemName: "plus.circle.fill")
                                .font(.system(size: 56))
                                .foregroundColor(.accentColor)
                        }
                        .padding()
                    }
                    Spacer()
                }
            }
            .navigationTitle("Habits")
            .navigationBarTitleDisplayMode(.inline)
            .sheet(isPresented: $showAddHabit) {
                AddHabitSheet(isPresented: $showAddHabit) { habit in
                    context.insert(habit)
                }
            }
        }
    }
    
    private var emptyState: some View {
        VStack(spacing: 16) {
            Image(systemName: "target")
                .font(.system(size: 48))
                .foregroundColor(.gray)
            
            Text("Chưa có thói quen nào")
                .font(.headline)
            
            Text("Tạo thói quen đầu tiên để bắt đầu theo dõi")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(UIColor.systemBackground))
    }
    
    private var habitsList: some View {
        ScrollView {
            VStack(spacing: 12) {
                ForEach(habits, id: \.self) { habit in
                    NavigationLink(destination: HabitDetailView(habit: habit)) {
                        HabitRowView(habit: habit) {
                            habit.checkIn()
                        }
                    }
                }
            }
            .padding()
        }
    }
}

struct HabitRowView: View {
    let habit: Habit
    let onCheckIn: () -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(habit.name)
                        .font(.headline)
                        .foregroundColor(.primary)
                    
                    Text(habit.frequency.displayName)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                VStack(alignment: .center, spacing: 4) {
                    Text("\(habit.streak)")
                        .font(.title3)
                        .fontWeight(.bold)
                        .foregroundColor(.green)
                    
                    Text("streak")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }
            
            // Progress ring
            ProgressRingView(
                progress: habit.completionPercentage(forDays: 30),
                label: "30-ngày"
            )
            
            HStack(spacing: 8) {
                if habit.isCheckedInToday() {
                    HStack(spacing: 4) {
                        Image(systemName: "checkmark.circle.fill")
                            .font(.caption)
                        Text("Đã hoàn thành hôm nay")
                            .font(.caption)
                    }
                    .foregroundColor(.green)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.green.opacity(0.2))
                    .cornerRadius(6)
                } else {
                    Button(action: onCheckIn) {
                        HStack(spacing: 4) {
                            Image(systemName: "plus.circle")
                                .font(.caption)
                            Text("Check-in")
                                .font(.caption)
                        }
                        .foregroundColor(.blue)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.blue.opacity(0.2))
                        .cornerRadius(6)
                    }
                }
                
                Spacer()
            }
        }
        .padding()
        .background(Color(UIColor.secondarySystemBackground))
        .cornerRadius(12)
    }
}

struct ProgressRingView: View {
    let progress: Double
    let label: String
    
    var body: some View {
        HStack(spacing: 12) {
            ZStack {
                Circle()
                    .stroke(Color.gray.opacity(0.3), lineWidth: 3)
                
                Circle()
                    .trim(from: 0, to: progress)
                    .stroke(Color.green, style: StrokeStyle(lineWidth: 3, lineCap: .round))
                    .rotationEffect(.degrees(-90))
                
                Text("\(Int(progress * 100))%")
                    .font(.caption2)
                    .fontWeight(.semibold)
            }
            .frame(width: 40, height: 40)
            
            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
            
            Spacer()
        }
    }
}

struct HabitDetailView: View {
    @Environment(\.modelContext) private var context
    let habit: Habit
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 16) {
                // Stats
                HStack(spacing: 16) {
                    StatCard(
                        title: "Streak",
                        value: "\(habit.streak)",
                        icon: "🔥"
                    )
                    
                    StatCard(
                        title: "Longest",
                        value: "\(habit.longestStreak)",
                        icon: "⭐️"
                    )
                    
                    StatCard(
                        title: "Total",
                        value: "\(habit.checkIns.count)",
                        icon: "✅"
                    )
                }
                .padding()
                
                // Calendar view (simplified)
                Text("Lịch sử check-in: \(habit.checkIns.count) lần")
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .padding()
                
                Spacer()
            }
            .navigationTitle(habit.name)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Menu {
                        Button("Sửa", action: {})
                        Button("Xóa", role: .destructive) {
                            context.delete(habit)
                        }
                    } label: {
                        Image(systemName: "ellipsis.circle")
                    }
                }
            }
        }
    }
}

struct StatCard: View {
    let title: String
    let value: String
    let icon: String
    
    var body: some View {
        VStack(spacing: 8) {
            Text(icon)
                .font(.title)
            
            Text(value)
                .font(.headline)
            
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color(UIColor.secondarySystemBackground))
        .cornerRadius(8)
    }
}

struct AddHabitSheet: View {
    @Binding var isPresented: Bool
    var onAdd: (Habit) -> Void
    
    @State private var name = ""
    @State private var selectedFrequency: HabitFrequency = .daily
    
    var body: some View {
        NavigationStack {
            Form {
                Section("Thông tin thói quen") {
                    TextField("Tên thói quen", text: $name)
                    
                    Picker("Tần suất", selection: $selectedFrequency) {
                        ForEach(HabitFrequency.allCases, id: \.self) { frequency in
                            Text(frequency.displayName).tag(frequency)
                        }
                    }
                }
                
                Button(action: addHabit) {
                    Text("Tạo Habit")
                }
                .disabled(name.trimmingCharacters(in: .whitespaces).isEmpty)
            }
            .navigationTitle("Thêm Habit mới")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Hủy") { isPresented = false }
                }
            }
        }
    }
    
    private func addHabit() {
        let habit = Habit(
            name: name,
            frequency: selectedFrequency
        )
        onAdd(habit)
        isPresented = false
    }
}

#Preview {
    HabitsView()
        .modelContainer(for: Habit.self)
}
