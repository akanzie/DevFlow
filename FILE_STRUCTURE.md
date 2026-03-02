# DevFlow iOS Project - File Structure & Quick Reference

## 📁 Complete Project Structure

```
c:\DevFlow/
│
├── docs/
│   ├── PRD.md                          # Product Requirements Document
│   └── IMPLEMENTATION_SUMMARY.md       # This implementation summary
│
├── ios/
│   ├── Info.plist                      # App configuration (permissions, version)
│   ├── README.md                       # Setup guide & architecture docs
│   ├── setup.sh                        # Quick setup script (Mac/Linux)
│   │
│   └── DevFlow/                        # Main app source code
│       │
│       ├── App/
│       │   └── DevFlowApp.swift        # Main app entry point, TabView, Onboarding
│       │
│       ├── Features/
│       │   ├── Planner/
│       │   │   ├── Views/
│       │   │   │   └── PlannerView.swift        # Timeline, add blocks, current block widget
│       │   │   └── ViewModels/
│       │   │       └── PlannerViewModel.swift   # Schedule logic, block management
│       │   │
│       │   ├── Habits/
│       │   │   └── Views/
│       │   │       └── HabitsView.swift         # Habit list, check-in, details, add sheet
│       │   │
│       │   ├── Notes/
│       │   │   └── Views/
│       │   │       └── NotesView.swift          # Note list, search, add note sheet
│       │   │
│       │   ├── Feed/
│       │   │   └── Views/
│       │   │       └── FeedView.swift           # Feed items display, save for later
│       │   │
│       │   └── Burnout/
│       │       └── Views/
│       │           └── BurnoutView.swift        # Check-in, weekly report, recommendations
│       │
│       ├── Core/
│       │   ├── Models/
│       │   │   ├── DailyBlock.swift             # @Model: Time block with category & completion
│       │   │   ├── Habit.swift                  # @Model: Habit with streak & check-ins
│       │   │   ├── QuickNote.swift              # @Model: Note with tags & voice support
│       │   │   └── BurnoutCheckIn.swift         # @Model: Mood/energy check-in & report
│       │   │
│       │   ├── Services/
│       │   │   ├── PlannerService.swift         # Schedule generation, block utilities
│       │   │   ├── BurnoutService.swift         # Weekly reports, risk assessment
│       │   │   └── FeedService.swift            # RSS feeds (mock for MVP)
│       │   │
│       │   ├── Extensions/
│       │   │   └── ColorExtension.swift         # Color hex parsing + Date formatting
│       │   │
│       │   ├── AppConstants.swift               # App-wide config (notifications, habits, etc)
│       │   └── PreviewContent.swift             # Mock data for SwiftUI previews
│       │
│       ├── BuildInfo.swift                      # Version, build metadata, feature flags, Logger
│       ├── ARCHITECTURE.swift                   # Architecture guide, best practices, tips
│       └── Resources/                           # (Placeholder for future assets/colors)
│
└── setup.sh                            # Quick setup script

```

---

## 📄 File Quick Reference

### **App Entry Point**
| File | Purpose | Key Functions |
|------|---------|---|
| `DevFlowApp.swift` | Main app entry with @main | Setup ModelContainer, onboarding, tab navigation |
| `OnboardingView` | 4-step onboarding flow | Welcome → Schedule → Habits → Complete |

### **Core Models (SwiftData)**
| File | Model | Properties | Methods |
|------|-------|-----------|---------|
| `DailyBlock.swift` | `DailyBlock` | startTime, endTime, title, category, isCompleted | duration, isCurrentBlock, timeRemaining |
| `Habit.swift` | `Habit` + `HabitCheckIn` | name, frequency, streak, checkIns[] | checkIn(), updateStreak(), completionPercentage() |
| `QuickNote.swift` | `QuickNote` | content, tags, isVoiceNote, isFavorite | addTag(), removeTag() |
| `BurnoutCheckIn.swift` | `BurnoutCheckIn` + `BurnoutReport` | date, mood, energy, notes | score (double), isBurnoutRisk (bool) |

### **Services**
| File | Service | Key Methods |
|------|---------|-------------|
| `PlannerService.swift` | `PlannerService` | generateDefaultSchedule(), getCurrentBlock(), getUpcomingBlock() |
| `BurnoutService.swift` | `BurnoutService` | calculateWeeklyReport(), checkConsecutiveLowMood() |
| `FeedService.swift` | `FeedService` | fetchFeeds() async, cacheFeedItem() |

### **Feature Views**
| File | View | Subviews | Features |
|------|------|----------|----------|
| `PlannerView.swift` | `PlannerView` | TimelineBlockView, AddBlockSheet, CircularProgressView | Daily timeline, block completion, add/edit blocks |
| `HabitsView.swift` | `HabitsView` | HabitRowView, HabitDetailView, AddHabitSheet, ProgressRingView | Habit list, streaks, 30-day percentage |
| `NotesView.swift` | `NotesView` | NoteRowView, SearchBar, AddNoteSheet | Search, tags, favorites, context menu |
| `FeedView.swift` | `FeedView` | FeedItemView | Mock RSS items, save for later, expand/collapse |
| `BurnoutView.swift` | `BurnoutView` | BurnoutCheckInSheet, BurnoutReportCard, StatCell, BurnoutCheckInRow | Daily check-in, weekly stats, recommendations |

### **Utilities & Config**
| File | Purpose |
|------|---------|
| `appConstants.swift` | Notifications timing, default habits, UI constants |
| `ColorExtension.swift` | Hex to Color parsing, Date formatting helpers |
| `PreviewContent.swift` | Mock data for SwiftUI previews |
| `BuildInfo.swift` | Version, build metadata, feature flags, Logger |
| `ARCHITECTURE.swift` | Development guide, best practices, naming conventions |
| `Info.plist` | App permissions, minimum OS, iCloud config |

---

## 🎯 Feature Map

### **Planner Module**
```
PlannerView
├─ Uses: PlannerService, PlannerViewModel, DailyBlock
├─ Displays: TimelineBlockView (each block)
├─ Actions: Toggle completion, add/edit block
└─ States: currentBlock, upcomingBlock, selectedDate
```

### **Habits Module**
```
HabitsView
├─ Uses: Habit model with HabitCheckIn relationship
├─ Displays: HabitRowView (each habit card)
├─ Actions: Check-in, view detail, add habit
└─ Shows: Streak, 30-day %, check-in status
```

### **Notes Module**
```
NotesView
├─ Uses: QuickNote model
├─ Displays: NoteRowView (each note)
├─ Search: By content or tags
├─ Actions: Add, delete, favorite, archive
└─ Features: Tags, voice note support
```

### **Feed Module**
```
FeedView
├─ Uses: FeedService, FeedItem model
├─ Displays: FeedItemView (article cards)
├─ Mock Data: 3 sample articles
├─ Actions: Save for later, expand, open link
└─ Future: Real RSS parsing, background fetch
```

### **Burnout Module**
```
BurnoutView
├─ Uses: BurnoutCheckIn, BurnoutService
├─ Check-in: Mood (emoji) + Energy (level)
├─ Report: Weekly stats + recommendations
├─ Display: 7-day history, risk assessment
└─ Logic: Auto-detect burnout risk, suggest actions
```

---

## 🔑 Key Swift Concepts Used

| Concept | File | Example |
|---------|------|---------|
| **@Model** (SwiftData) | All Models/ files | `@Model final class DailyBlock { ... }` |
| **@Query** | Feature Views | `@Query(sort: \DailyBlock.startTime) var blocks` |
| **@Observable** | ViewModels | `@Observable class PlannerViewModel { ... }` |
| **@Environment** | All Views | `@Environment(\.modelContext) var context` |
| **@State, @Binding** | All Views | Local UI state management |
| **NavigationStack** | Feature Views | For modal/push navigation |
| **TabView** | DevFlowApp | 5-tab bottom navigation |
| **Enum + CaseIterable** | Models | BlockCategory, HabitFrequency, MoodLevel |
| **@Relationship** | Models | `@Relationship(deleteRule: .cascade)` |
| **async/await** | FeedService | `func fetchFeeds() async -> [FeedItem]` |

---

## 🚀 How to Use Each File

### **When Adding a New Feature**
1. Create folder: `Features/[FeatureName]/Views/`
2. Define model in `Core/Models/[NewModel].swift`
3. Add service in `Core/Services/[NewService].swift` if needed
4. Create view in `Features/[Feature]/Views/[Feature]View.swift`
5. Add tab to `TabBarView` in `DevFlowApp.swift`

### **When Modifying Existing Features**
1. Find feature folder under `Features/`
2. Edit view in `Views/[Name]View.swift`
3. Update model in `Core/Models/[Model].swift`
4. Adjust logic in `Core/Services/[Service].swift`

### **When Debugging**
1. Use `Logger.shared.debug("message")` in `BuildInfo.swift`
2. Check model relationships in `Core/Models/`
3. Trace data flow through @Query in views
4. Test with `.modelContainer(for: ...)` in preview

### **When Adding Constants**
1. Edit `Core/AppConstants.swift`
2. Use as `AppConstants.appName`, etc.
3. Avoid hardcoding strings in views

---

## 💾 Data Flow

```
User Action (tap button)
    ↓
View State Updated (@State)
    ↓
Model Updated (modelContext.insert/update)
    ↓
SwiftData persists locally
    ↓
CloudKit syncs automatically
    ↓
@Query refreshes views
    ↓
UI Re-renders
```

---

## 🔗 File Dependencies Map

```
DevFlowApp.swift
├── TabBarView
│   ├── PlannerView → PlannerViewModel → PlannerService → DailyBlock
│   ├── HabitsView → Habit → HabitCheckIn
│   ├── NotesView → QuickNote
│   ├── FeedView → FeedService → FeedItem
│   └── BurnoutView → BurnoutCheckIn → BurnoutService

Core/
├── Models/ (all data structures)
├── Services/ (business logic)
├── Extensions/ (utilities)
└── BuildInfo.swift (config + logging)
```

---

## 🧪 Testing Each Module

### **Test Planner**
```swift
let service = PlannerService.shared
let blocks = service.generateDefaultSchedule(isMorningPerson: true)
// Check: 14 blocks for full day, proper times
```

### **Test Habits**
```swift
let habit = Habit(name: "Gym")
habit.checkIn()
habit.checkIn() // Should not create new (same day)
print(habit.streak) // Should be 1
```

### **Test Notes**
```swift
var note = QuickNote(content: "Test", tags: ["swift"])
note.addTag("ios")
print(note.tags) // ["swift", "ios"]
```

### **Test Burnout**
```swift
let service = BurnoutService.shared
let report = service.calculateWeeklyReport(from: checkIns)
print(report.avgMood) // Double 1-5
```

---

## ✅ Completion Checklist for Developers

- [ ] Understand architecture (read ARCHITECTURE.swift)
- [ ] Build on real device (iOS 17+)
- [ ] Verify iCloud sync is working
- [ ] Test each feature (5-6 user stories per feature)
- [ ] Check data persistence after restart
- [ ] Test onboarding flow completely
- [ ] Verify notifications (if enabled)
- [ ] Performance test on iPhone SE (baseline)
- [ ] UI review in dark mode
- [ ] Accessibility check (VoiceOver, Dynamic Type)

---

**Last Updated:** March 2, 2026  
**Status:** Ready for development ✅
