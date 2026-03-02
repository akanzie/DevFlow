# DevFlow iOS App - Code Architecture & Setup Guide

## 📱 Project Structure

```
DevFlow/
├── App/
│   └── DevFlowApp.swift           # Main app entry point, setup, onboarding
├── Features/
│   ├── Planner/                   # Daily planner & timeline
│   │   ├── Views/
│   │   │   └── PlannerView.swift
│   │   └── ViewModels/
│   │       └── PlannerViewModel.swift
│   ├── Habits/                    # Habit tracking
│   │   └── Views/
│   │       └── HabitsView.swift
│   ├── Notes/                     # Quick notes & ideas
│   │   └── Views/
│   │       └── NotesView.swift
│   ├── Feed/                      # Tech feed (RSS)
│   │   └── Views/
│   │       └── FeedView.swift
│   └── Burnout/                   # Burnout guard & reporting
│       └── Views/
│           └── BurnoutView.swift
├── Core/
│   ├── Models/
│   │   ├── DailyBlock.swift
│   │   ├── Habit.swift
│   │   ├── QuickNote.swift
│   │   └── BurnoutCheckIn.swift
│   ├── Services/
│   │   ├── PlannerService.swift
│   │   ├── BurnoutService.swift
│   │   ├── FeedService.swift
│   │   └── NotificationService.swift
│   ├── Extensions/
│   │   └── ColorExtension.swift
│   ├── AppConstants.swift         # App-wide constants
│   └── ViewModels/
├── Resources/                     # Assets, colors, strings
└── Widgets/                       # WidgetKit Extension (future)
```

## 🏗️ Architecture Principles

### 1. **Offline-First + Local Sync**
- All data stored locally using **SwiftData** (replacing Core Data)
- **CloudKit** handles automatic device sync (iCloud)
- No backend server needed for MVP

### 2. **View Layer (SwiftUI)**
- Declarative UI using latest SwiftUI features (iOS 17+)
- Uses `@Query` from SwiftData for reactive data binding
- Dark theme preferred (tech vibe)

### 3. **Data Layer (SwiftData)**
```swift
@Model class DailyBlock { ... }  // Marked with @Model macro
@Model class Habit { ... }
@Model class QuickNote { ... }
```

### 4. **State Management**
- Use `@Observable` for ViewModels when needed
- Prefer `@Query` directly in Views for simple cases
- Keep logic close to Models (service methods)

### 5. **Service Layer**
- `PlannerService`: Schedule generation & block management
- `BurnoutService`: Weekly report calculatino & risk assessment
- `FeedService`: RSS feed fetching (mock for MVP)

## 🚀 Getting Started

### Prerequisites
- Xcode 15.1+
- iOS 17.0+
- Swift 5.9+

### Setup Steps

1. **Clone/Open in Xcode**
   ```bash
   open DevFlow.xcodeproj
   ```

2. **Enable iCloud (CloudKit)**
   - Select `DevFlow` target → Signing & Capabilities
   - Add iCloud capability
   - Enable CloudKit
   - Set container ID: `iCloud.com.devflow.app`

3. **Build & Run**
   - Select iOS 17+ simulator or device
   - Cmd+R to build and run

4. **First Launch**
   - Onboarding: Choose schedule (morning person / night owl)
   - Default habits auto-created
   - Start adding blocks and habits!

## 📋 Key Models & Relationships

### DailyBlock
- Represents a time block in daily schedule
- Properties: startTime, endTime, title, category, isCompleted
- Methods: duration, isCurrentBlock, timeRemaining

### Habit
- Tracks habits with streaks
- Properties: name, frequency, streak, checkIns (relationship)
- Methods: checkIn(), updateStreak(), completionPercentage()

### QuickNote
- Quick ideas/notes with tags and voice support
- Properties: content, tags, isVoiceNote, isFavorite, isArchived
- Methods: addTag(), removeTag()

### BurnoutCheckIn
- Daily mood + energy check-in
- Properties: date, mood (enum), energy (enum), notes
- Methods: isBurnoutRisk (bool)

## 🔌 Extensions & Integrations

### WidgetKit (Phase 2)
- Small widget: Current block + time remaining
- Medium widget: Daily progress rings
- Large widget: Habit streaks + notes

### Notifications
- Block reminders: 5 mins before start
- Daily check-in prompt: 9 PM
- Burnout alert: If risky mood 2+ days

### Health Integration (Phase 2)
- Query steps/workout from HealthKit
- Auto-mark "gym" habit if detected
- Sync sleep data

### Voice Input
- Quick note voice-to-text using Speech framework
- Save as VoiceNote in QuickNote model

## 🎨 Design System

### Colors (Dark Theme)
- Primary: Blue (#007AFF)
- Accent: Green (#34C759) for progress
- Category colors:
  - Work: #FF6B6B (red)
  - Learn: #4ECDC4 (cyan)
  - Health: #45B7D1 (blue)
  - Rest: #96CEB4 (green)
  - Meal: #FFEAA7 (yellow)

### Typography
- Headlines: .headline (bold)
- Body: .body (regular)
- Small text: .caption, .caption2

### Spacing
- Padding: 8pt, 12pt, 16pt (standard)
- Corner radius: 8-12pt
- Shadow: Light, subtle

## 🧪 Testing

### Unit Tests (Core Logic)
```swift
// Test Habit streak calculation
func testHabitStreakUpdate() {
    let habit = Habit(name: "Gym")
    habit.checkIn()
    habit.checkIn()
    XCTAssertEqual(habit.streak, 2)
}

// Test Block current state
func testBlockIsCurrentBlock() {
    let block = DailyBlock(...)
    XCTAssertTrue(block.isCurrentBlock)
}
```

### UI Tests
- Test onboarding flow
- Test tab navigation
- Test add/edit operations

## 📦 Dependencies

**Built-in (No external pods needed)**
- SwiftUI
- SwiftData (iOS 17+)
- Combine
- WidgetKit
- UserNotifications
- HealthKit (optional)
- Speech
- CloudKit

**Why no external packages for MVP?**
- SwiftData replaces Core Data + Realm
- Native SwiftUI handles all UI
- CloudKit is free + private
- Lightweight = better battery life

## 📱 Deployment

### TestFlight (Beta)
1. Create provisioning profile in Apple Developer
2. Archive app: Cmd+Shift+K
3. Upload to App Store Connect
4. Add testers (emails)
5. Send TestFlight link

### App Store (Production)
1. Complete app information:
   - Name, icon, screenshots
   - Description (use PRD copy)
   - Category: Productivity
   - Keywords: habit, planner, developer, burnout
2. Submit for review (24-48 hours)
3. Monitor crashes + ratings

## 🐛 Debugging

### Common Issues

**SwiftData not syncing to iCloud?**
- Verify container ID matches in code + capabilities
- Check iCloud sign-in on device
- Test with real device (simulator has limitations)

**Notifications not firing?**
- Check user notifications permission
- Verify notification is scheduled for future time
- Test with .now() + 5 seconds

**Widget not updating?**
- Ensure shared container ID in WidgetKit extension
- Test small timeline update first

## 📚 Resources

- [Apple SwiftData Docs](https://developer.apple.com/documentation/swiftdata)
- [SwiftUI Tutorials](https://developer.apple.com/tutorials/swiftui)
- [CloudKit Guide](https://developer.apple.com/icloud/cloudkit/)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)

## 🎯 Next Steps (Phase 2+)

- [ ] WidgetKit extension
- [ ] HealthKit integration
- [ ] AI summarization (Apple Intelligence)
- [ ] iPad/macOS version
- [ ] Sync with GitHub API
- [ ] Premium features (in-app purchase)

---

**Version:** 1.0 (MVP)  
**Last Updated:** March 2, 2026  
**Maintainer:** DevFlow Team
