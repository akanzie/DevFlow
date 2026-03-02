# 🚀 DevFlow iOS - Quick Reference Card

## ⚡ 5-Minute Setup

```bash
1. cd c:\DevFlow\ios
2. open DevFlow.xcodeproj
3. Target → Signing & Capabilities
4. Click "+" → iCloud → Enable CloudKit
5. Container: iCloud.com.devflow.app
6. Cmd+R (Build & Run)
```

---

## 📱 Features at a Glance

| Feature | What it does | File |
|---------|------------|------|
| **Planner** | Daily schedule with 14 blocks | `PlannerView.swift` |
| **Habits** | Streak tracking with check-ins | `HabitsView.swift` |
| **Notes** | Quick ideas with tags | `NotesView.swift` |
| **Feed** | Developer articles | `FeedView.swift` |
| **Burnout** | Mood tracking & weekly reports | `BurnoutView.swift` |

---

## 🎯 Key Data Models

```swift
@Model
DailyBlock        // Time slots (work/learn/rest/etc)
Habit             // Habits with streaks
QuickNote         // Notes with tags
BurnoutCheckIn    // Mood + energy tracking
FeedItem          // RSS items
```

---

## 📁 Important Files

**Start here:**
```
00_START_HERE.md       ← Overview
GETTING_STARTED.md     ← Setup + testing
```

**Understanding architecture:**
```
ARCHITECTURE.swift     ← Tips & guidelines
FILE_STRUCTURE.md      ← Every file explained
README.md              ← Deep dive
```

**Main app code:**
```
App/DevFlowApp.swift   ← Entry point, tabs
Features/*/Views/*.swift ← Feature code
Core/Models/*.swift    ← Data models
Core/Services/*.swift  ← Business logic
```

---

## 🧪 Testing Basics

```bash
Feature: Planner
✓ See today's schedule
✓ Tap block → mark complete
✓ Tap "+" → add new block
✓ Change date → see other days

Feature: Habits
✓ See 4 default habits
✓ Tap check-in → streak increases
✓ Next day: can check-in again
✓ Same day: only 1 check-in allowed

Feature: Notes
✓ Tap "+" → add note
✓ Add tags (e.g., #swift)
✓ Search by content or tags
✓ Delete with context menu

Feature: Burnout
✓ Tap check-in
✓ Select mood + energy
✓ See weekly report
✓ View recommendations
```

---

## 🔧 Common Tasks

### Add a new habit (default)
Edit `AppConstants.swift`:
```swift
static let defaultHabits = [
    ("New Habit Name", HabitFrequency.daily),
]
```

### Change schedule times
Edit in `PlannerService.swift`:
```swift
static let morningPersonSchedule: [...] = [
    ("Thức dậy", 5, 30, .health),  // Hour, Minute
    ...
]
```

### Add new feature
1. Create `Features/NewFeature/Views/NewFeatureView.swift`
2. Add model in `Core/Models/NewModel.swift`
3. Add tab in `TabBarView` in `DevFlowApp.swift`

### Debug data
```swift
logger.debug("Message here")  // Logs to console
```

---

## 🌐 Technology Stack

| Component | Technology |
|-----------|-----------|
| UI | SwiftUI |
| Data | SwiftData (@Model) |
| Sync | CloudKit |
| Database | SQLite |
| Language | Swift 5.9+ |
| OS | iOS 17+ |

---

## 📊 Project Structure

```
Models      → Data (@Model classes)
Services    → Logic (PlannerService, etc)
Views       → UI (PlannerView, etc)
Extensions  → Utilities (Color, Date)
Utilities   → Config (AppConstants, Logger)
```

---

## ✅ Checklist

- [ ] Xcode 15.1+ installed
- [ ] Read `GETTING_STARTED.md`
- [ ] iCloud capability added
- [ ] CloudKit enabled
- [ ] App builds (Cmd+B)
- [ ] App runs (Cmd+R)
- [ ] Onboarding completes
- [ ] Can add block, habit, note
- [ ] Data persists after restart

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| App crashes | Check Xcode console, verify iOS 17+ |
| Data not syncing | Verify container ID: `iCloud.com.devflow.app` |
| iCloud not working | Test on real device (simulator limited) |
| Build fails | Cmd+Shift+K (clean), retry Cmd+B |
| Can't check-in twice | By design! Only 1 per day |

---

## 📞 Documentation

- **Setup?** → `GETTING_STARTED.md`
- **Architecture?** → `ARCHITECTURE.swift`
- **File guide?** → `FILE_STRUCTURE.md`
- **Everything?** → `README.md`

---

## 🎯 Success Criteria

- ✅ App launches in <2 seconds
- ✅ All 5 features work
- ✅ Data persists offline
- ✅ CloudKit syncs when online
- ✅ No crashes
- ✅ Ready for TestFlight

---

## 🚀 Next Steps

1. **Now:** Follow 5-minute setup above
2. **5 min:** App should be running
3. **Test:** Follow testing checklist
4. **Today:** Submit to TestFlight
5. **Week:** Ship to App Store

---

**Ready? Let's go! 💻**

```bash
cd c:\DevFlow\ios && open DevFlow.xcodeproj
```

---

*Last updated: March 2, 2026*  
*Status: Production Ready ✅*
