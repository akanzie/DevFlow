import SwiftUI
import SwiftData

@main
struct DevFlowApp: App {
    @State private var modelContainer: ModelContainer?
    @State private var isOnboarded = false
    
    var body: some Scene {
        WindowGroup {
            if let modelContainer = modelContainer {
                if isOnboarded {
                    TabBarView()
                        .modelContainer(modelContainer)
                } else {
                    OnboardingView(isOnboarded: $isOnboarded)
                        .modelContainer(modelContainer)
                }
            } else {
                ProgressView()
                    .onAppear {
                        setupModelContainer()
                    }
            }
        }
    }
    
    private func setupModelContainer() {
        do {
            let container = try ModelContainer(
                for: DailyBlock.self, Habit.self, HabitCheckIn.self,
                QuickNote.self, FeedItem.self, BurnoutCheckIn.self,
                BurnoutReport.self,
                configurations: ModelConfiguration(
                    isStoredInMemoryOnly: false,
                    cloudKitDatabase: .private("iCloud.com.devflow.app")
                )
            )
            self.modelContainer = container
            
            // Load onboarding state from UserDefaults
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                isOnboarded = UserDefaults.standard.bool(forKey: "isOnboarded")
            }
        } catch {
            print("Failed to setup ModelContainer: \(error)")
        }
    }
}

struct TabBarView: View {
    var body: some View {
        TabView {
            PlannerView()
                .tabItem {
                    Label("Planner", systemImage: "calendar")
                }
            
            HabitsView()
                .tabItem {
                    Label("Habits", systemImage: "target")
                }
            
            NotesView()
                .tabItem {
                    Label("Notes", systemImage: "note.text")
                }
            
            FeedView()
                .tabItem {
                    Label("Feed", systemImage: "newspaper")
                }
            
            BurnoutView()
                .tabItem {
                    Label("Burnout", systemImage: "heart")
                }
        }
        .preferredColorScheme(.dark)
    }
}

struct OnboardingView: View {
    @Binding var isOnboarded: Bool
    @State private var currentStep = 0
    @State private var selectedSchedule: String = "morning"
    @State private var isMorningPerson = true
    
    var body: some View {
        ZStack {
            Color(UIColor.systemBackground)
                .ignoresSafeArea()
            
            VStack(spacing: 20) {
                if currentStep == 0 {
                    welcomeStep
                } else if currentStep == 1 {
                    scheduleStep
                } else if currentStep == 2 {
                    habitsStep
                } else {
                    finalStep
                }
                
                Spacer()
                
                HStack(spacing: 16) {
                    if currentStep > 0 {
                        Button(action: { currentStep -= 1 }) {
                            Text("Quay lại")
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.gray.opacity(0.2))
                                .cornerRadius(8)
                        }
                    }
                    
                    Button(action: nextStep) {
                        Text(currentStep == 3 ? "Hoàn thành" : "Tiếp tục")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                }
                .padding()
            }
            .padding()
        }
    }
    
    private var welcomeStep: some View {
        VStack(spacing: 20) {
            Image(systemName: "wave.3")
                .font(.system(size: 60))
                .foregroundColor(.blue)
            
            Text("Chào mừng đến DevFlow")
                .font(.title)
                .fontWeight(.bold)
            
            Text("Companion dành riêng cho Developer IT – duy trì lịch phát triển bản thân, tránh burnout, tăng năng suất")
                .font(.body)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
    }
    
    private var scheduleStep: some View {
        VStack(spacing: 20) {
            Text("Chọn lịch hợp với bạn")
                .font(.headline)
            
            Button(action: { isMorningPerson = true }) {
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Image(systemName: "sunrise.fill")
                            .font(.title2)
                            .foregroundColor(.orange)
                        
                        Text("Morning Person")
                            .font(.headline)
                        
                        Spacer()
                        
                        Image(systemName: isMorningPerson ? "checkmark.circle.fill" : "circle")
                            .foregroundColor(isMorningPerson ? .blue : .gray)
                    }
                    
                    Text("Thức dậy 5:30, học tập buổi tối")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding()
                .background(Color(UIColor.secondarySystemBackground))
                .cornerRadius(8)
            }
            
            Button(action: { isMorningPerson = false }) {
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Image(systemName: "moon.stars.fill")
                            .font(.title2)
                            .foregroundColor(.indigo)
                        
                        Text("Night Owl")
                            .font(.headline)
                        
                        Spacer()
                        
                        Image(systemName: !isMorningPerson ? "checkmark.circle.fill" : "circle")
                            .foregroundColor(!isMorningPerson ? .blue : .gray)
                    }
                    
                    Text("Thức dậy 7:00, học tập tối")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding()
                .background(Color(UIColor.secondarySystemBackground))
                .cornerRadius(8)
            }
        }
    }
    
    private var habitsStep: some View {
        VStack(spacing: 20) {
            Text("Thói quen mặc định")
                .font(.headline)
            
            VStack(spacing: 8) {
                HabitBadge(name: "Gym", frequency: "4x/tuần", icon: "💪")
                HabitBadge(name: "Học code", frequency: "1h/ngày", icon: "💻")
                HabitBadge(name: "Ngủ đủ", frequency: "≥7h", icon: "😴")
                HabitBadge(name: "Commit GitHub", frequency: "Hàng ngày", icon: "🚀")
            }
            
            Text("Bạn có thể chỉnh sửa hoặc thêm thói quen khác sau")
                .font(.caption)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
    }
    
    private var finalStep: some View {
        VStack(spacing: 20) {
            Image(systemName: "checkmark.circle.fill")
                .font(.system(size: 60))
                .foregroundColor(.green)
            
            Text("Sẵn sàng!")
                .font(.title)
                .fontWeight(.bold)
            
            Text("DevFlow đã sẵn sàng để giúp bạn duy trì tiến độ phát triển bản thân")
                .font(.body)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
    }
    
    private func nextStep() {
        if currentStep == 3 {
            UserDefaults.standard.setValue(true, forKey: "isOnboarded")
            UserDefaults.standard.setValue(isMorningPerson, forKey: "isMorningPerson")
            isOnboarded = true
        } else {
            currentStep += 1
        }
    }
}

struct HabitBadge: View {
    let name: String
    let frequency: String
    let icon: String
    
    var body: some View {
        HStack(spacing: 12) {
            Text(icon)
                .font(.title2)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(name)
                    .font(.headline)
                Text(frequency)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
        }
        .padding()
        .background(Color(UIColor.secondarySystemBackground))
        .cornerRadius(8)
    }
}

#Preview {
    DevFlowApp()
}
