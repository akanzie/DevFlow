# DevFlow iOS - Getting Started Guide

## ⚡ Quick Start (5 minutes)

### Step 1: Clone/Open Project
```bash
cd c:\DevFlow\ios
open DevFlow.xcodeproj
```

### Step 2: Configure iCloud (IMPORTANT)
1. **Select Target**
   - Click "DevFlow" in Xcode navigator
   - Select "DevFlow" target

2. **Add Capabilities**
   - Go to "Signing & Capabilities" tab
   - Click "+ Capability"
   - Search for "iCloud"
   - Click "iCloud"

3. **Configure CloudKit**
   - Check ☐ "CloudKit"
   - Container ID should auto-fill: `iCloud.com.devflow.app`
   - If not, set manually to: `iCloud.com.devflow.app`

### Step 3: Build & Run
```
Cmd+R (or click ▶️ Play button)
```

### Step 4: First Launch Experience
- **Onboarding:** Choose "Morning Person" or "Night Owl"
- **See:** 4 default habits, today's schedule blocks
- **Try:** Add a new block, check-in a habit, create a note

---

## 🧪 Testing Checklist

### ✅ PLANNER Feature
- [ ] App launches to Planner tab with today's schedule
- [ ] See 14 blocks for full day (5:30 AM → 23:00 PM)
- [ ] Blocks have correct colors (by category)
- [ ] Can tap a block to mark as complete ✓
- [ ] Completed blocks show checkmark
- [ ] Current block is highlighted (if time matches)
- [ ] Can tap "+" to add new block
- [ ] Can select date to see different day's schedule
- [ ] New blocks appear immediately
- [ ] Data persists after restart ✅

### ✅ HABITS Feature
- [ ] See 4 default habits listed
- [ ] Each habit shows streak count (0 initially)
- [ ] Can tap "Check-in" button
- [ ] After check-in: streak updates to 1
- [ ] Next day: can check-in again (streak = 2)
- [ ] Same day: can't check-in twice
- [ ] Tap habit row → see details (stats)
- [ ] 30-day completion ring shows %
- [ ] Can add new habit with "+" button
- [ ] New habit appears with 0 streak
- [ ] Data persists after restart ✅

### ✅ NOTES Feature
- [ ] Switch to Notes tab
- [ ] See empty state initially
- [ ] Tap "+" to add new note
- [ ] Type text + add tags (e.g., #swift #ios)
- [ ] Note appears in list
- [ ] Can search by content → filters
- [ ] Can search by tag → filters
- [ ] Tap heart icon → favorites note
- [ ] Can delete with context menu
- [ ] Voice note option appears (mic icon)
- [ ] Data persists after restart ✅

### ✅ FEED Feature
- [ ] Switch to Feed tab
- [ ] See 3 mock developer articles
- [ ] Tap article → expands to show more
- [ ] Tap "Đọc tiếp" → should open URL (may fail in simulator)
- [ ] Can tap bookmark → "Save for later" toggles
- [ ] Tap refresh icon → reloads feed
- [ ] Bookmarked articles persist

### ✅ BURNOUT Feature
- [ ] Switch to Burnout tab
- [ ] Tap check-in button
- [ ] Select mood emoji (😢 😟 😐 🙂 😄)
- [ ] Select energy level (dropdown)
- [ ] Add notes (optional)
- [ ] Tap "Lưu Check-in"
- [ ] Check-in appears in list
- [ ] See weekly report card with stats
- [ ] See recommendations based on mood
- [ ] If low mood 2+ days: high burnout alert shows
- [ ] Data persists after restart ✅

### ✅ NAVIGATION
- [ ] All 5 tabs accessible from bottom tab bar
- [ ] Each tab maintains its state when switching
- [ ] Can navigate back with back button if sheet open
- [ ] Modal sheets have "Hủy" (Cancel) button
- [ ] NavigationStack works for detail views

### ✅ ONBOARDING
- [ ] Fresh install → onboarding shows
- [ ] Complete onboarding → app main screen
- [ ] Choose "Morning Person" → see morning schedule
- [ ] Choose "Night Owl" → see night schedule
- [ ] Skip onboarding flag stored (doesn't show again)

### ✅ DATA PERSISTENCE
- [ ] Kill app (Cmd+K or swipe close)
- [ ] Reopen app
- [ ] All data still there (blocks, habits, notes, check-ins)
- [ ] Streaks preserved
- [ ] Completed blocks marked as complete

### ✅ iCLOUD SYNC (2 devices)
- [ ] Add habit on iPhone 1
- [ ] Wait 10-15 seconds
- [ ] Check iPhone 2 → habit appears
- [ ] Edit block on iPhone 1
- [ ] Changes sync to iPhone 2
- [ ] Delete note on iPhone 2
- [ ] Deleted on iPhone 1 too
- [ ] Works with no internet (syncs when reconnected)

---

## 🔧 Troubleshooting

### **App crashes on launch**
- Check Xcode console for errors
- Ensure iOS 17+ simulator/device
- Delete app + reinstall (Cmd+Shift+K then build)

### **CloudKit not syncing**
- Go to Settings > [Apple ID] > iCloud
- Toggle iCloud off/on
- Verify container ID matches: `iCloud.com.devflow.app`
- Test on real device (simulator has limitations)

### **Notifications not firing**
- Settings > DevFlow > Notifications: "Allow"
- Test with 5-second reminder (not immediate)

### **Habits check-in same day shows error**
- This is EXPECTED! Only 1 check-in per calendar day
- Next day: use new check-in button

### **Onboarding appears every launch**
- Check UserDefaults in Xcode console
- `defaults read com.apple.CoreData` (may need adjustment)

---

## 📊 Test Data to Create

### **Create Good Test Scenario**

1. **Planner:**
   - Complete 3 blocks today (gym, code, rest)
   - Add 1 custom block (e.g., "Coffee break")

2. **Habits:**
   - Check-in "Gym" (streak = 1)
   - Check-in "Học code" (streak = 1)
   - Skip "Ngủ" (incomplete)

3. **Notes:**
   - Add 3-4 notes with different tags
   - #bug, #idea, #learning
   - Test search by tag

4. **Burnout:**
   - Check-in mood: "Good" (4)
   - Energy: "High" (4)
   - Notes: "Had productive day"
   - Should see positive recommendations

5. **Feed:**
   - "Save for later" 1-2 articles
   - Expand articles to see full text

---

## 🎯 Performance Benchmarks

| Task | Target | Notes |
|------|--------|-------|
| App launch | <2 seconds | First launch includes setup |
| Load planner | <1 second | 14 blocks |
| Add note | <500ms | Immediate feedback |
| Check-in habit | <300ms | UI updates instantly |
| Search notes | <200ms | Real-time search |
| Weekly report calc | <500ms | Background compute |
| iCloud sync | 5-15 sec | Network dependent |

---

## 🐛 Debugging Tips

### **Enable Verbose Logging**
```swift
// In DevFlowApp.swift, before rendering views:
Logger.shared.verbose("App launched in \(Date())")

// Elsewhere:
logger.debug("Habit checked-in: \(habit.name), streak: \(habit.streak)")
```

### **Check SwiftData State**
```swift
// In Preview:
#Preview {
    PlannerView()
        .modelContainer(for: DailyBlock.self, inMemoryOnly: true)
}
```

### **Monitor iCloud Sync**
Settings → [Your Name] → iCloud → Show all → DevFlow → Check storage size

### **Test Offline Mode**
Xcode → Debug → Network Link Conditioner → Offline

---

## 📱 Device Testing

### **Minimum Device**
- iPhone SE (3rd gen) with iOS 17.0+

### **Recommended Devices**
- iPhone 14 Pro (current standard)
- iPhone 15 Pro (latest)
- iPad (future)

### **Simulator Testing**
- iPhone 15 simulator (iOS 17.x)
- Works but iCloud sync limited
- Test real iCloud on actual device

---

## 📦 Build & Archive

### **For TestFlight Beta**
```
1. Select Generic iOS Device
2. Product → Archive
3. Wait for build to complete
4. Manage Version & Build Number (increment)
5. Upload to App Store Connect
```

### **For App Store Release**
```
1. Ensure version bumped (1.0 → 1.1)
2. Update CHANGELOG
3. Archive for production
4. Set minimum iOS: 17.0
5. Optimize for app store
6. Submit for review (wait 24-48h)
```

---

## 🎯 Acceptance Criteria (MVP Complete)

- ✅ All 5 features implemented
- ✅ Onboarding complete & intuitive
- ✅ Data syncs via iCloud CloudKit
- ✅ Works offline (100% offline-first)
- ✅ No crashes on test scenarios
- ✅ Performance <2s load time
- ✅ Retained on day 7: >40% target
- ✅ UI dark theme, responsive
- ✅ Accessibility: VoiceOver friendly
- ✅ Ready for TestFlight

---

## 📞 Support

- **Architecture?** → Read `ARCHITECTURE.swift`
- **File structure?** → Check `FILE_STRUCTURE.md`
- **Features?** → See `IMPLEMENTATION_SUMMARY.md`
- **Requirements?** → Review `PRD.md`

---

**Happy coding! 🚀**

Now go build something amazing with DevFlow! 💻
