# TÀI LIỆU YÊU CẦU SẢN PHẨM (PRODUCT REQUIREMENTS DOCUMENT - PRD)

**Tên sản phẩm:** DevFlow - Companion App cho Developer IT  
**Phiên bản:** 1.0 (MVP)  
**Ngày soạn thảo:** Tháng 3/2026  
**Tác giả:** Kiệt (dựa trên ý tưởng phát triển bản thân cho dev IT)  
**Mô tả ngắn:** Ứng dụng iOS hỗ trợ developer IT (lập trình viên, tester, devops...) duy trì lịch trình phát triển bản thân, tránh burnout, tăng năng suất khi làm việc 8h/ngày (office/remote).

---

## 1. Giới thiệu

### 1.1 Mục đích của tài liệu
Tài liệu này mô tả chi tiết các yêu cầu chức năng, phi chức năng, giao diện và kinh doanh để phát triển ứng dụng DevFlow. Nó làm cơ sở cho developer (SwiftUI), designer, tester và product owner để build, test và launch app.

### 1.2 Phạm vi sản phẩm

**In scope (MVP):**
- Planner theo lịch dev hàng ngày (dựa lịch mẫu đã đề xuất).
- Habit tracker (gym, học code, ngủ đủ, commit GitHub).
- Quick note & idea capture (voice-to-text).
- Tech feed nhẹ (RSS curated).
- Burnout check-in & weekly report.
- Widget, notification, integration cơ bản với Health/Focus mode.

**Out of scope (các phase sau):**
- Sync với GitHub/Notion/Obsidian API đầy đủ.
- AI advanced (generate code snippet).
- Version cho iPad/macOS.
- Multi-user/family sharing.
- In-app purchase/subscription (có thể thêm sau).

### 1.3 Đối tượng người dùng chính (Target users)
- Developer IT Việt Nam (20-35 tuổi): junior → mid/senior, làm office/remote.
- Người bận rộn, cần tool đơn giản, privacy-first, không phức tạp như Notion/Todoist.
- Người quan tâm self-improvement: gym, học skill, work-life balance.

### 1.4 Giả định & ràng buộc
- Người dùng dùng iPhone/iOS 17+ (2026).
- App native SwiftUI (không cross-platform).
- Dữ liệu lưu local + iCloud sync (không cần backend server MVP).
- Ngôn ngữ chính: Tiếng Việt (UI), hỗ trợ tiếng Anh.

---

## 2. Yêu cầu kinh doanh & mục tiêu sản phẩm

- **Vấn đề giải quyết:** Dev IT thường burnout do ngồi lâu, học không đều, thiếu theo dõi progress → app giúp duy trì streak, nhắc nhở, báo cáo tiến độ.

- **Mục tiêu MVP:**
  - 500+ download trong 3 tháng đầu (TestFlight + App Store).
  - Retention day 7: >40%.
  - Rating ≥4.5/5.

- **Unique Value Proposition (UVP):** "Companion dành riêng cho dev IT – không phải todo list chung chung, mà theo lịch dev thực tế + burnout guard."

---

## 3. Yêu cầu chức năng (Functional Requirements)

Sử dụng **User Story** format: As a [user], I want [feature] so that [benefit].

### 3.1 Onboarding & Authentication
- As a new user, I want onboarding 3-4 screen (giới thiệu app, chọn lịch mẫu: morning person / night owl) so that tôi setup nhanh.
- Local auth (Face ID/Touch ID/Passcode) – không cần email/login MVP.

### 3.2 Daily Planner
- Hiển thị lịch ngày theo timeline (block thời gian: 5:30 thức dậy → 23:00 ngủ).
- Cho phép customize block (thêm/sửa/xóa, ví dụ: thay workout bằng chạy bộ).
- Widget home/lock screen: current block + time left.
- Notification: remind 5 phút trước block (e.g. "Bắt đầu LeetCode nhé!").
- Integration: toggle Focus mode "Dev Learning" khi bắt đầu học.

### 3.3 Habit Tracker
- Danh sách habit mặc định: Gym 4x/tuần, Học code 1h/ngày, Ngủ ≥7h, Commit GitHub.
- Check-in hàng ngày (ring progress, streak counter).
- Calendar view: thấy streak dài nhất.
- Widget: daily progress ring.

### 3.4 Quick Note & Idea Capture
- Floating button hoặc Siri Shortcut: ghi note nhanh (text/voice).
- Voice-to-text (dùng Apple Speech framework).
- Tag: #bug #idea #learning #meeting.
- List note searchable, export text.

### 3.5 Tech Feed
- Curated RSS: dev.to, Viblo, Medium (tag "programming"), Hacker News top 5.
- Read later + offline mode.
- Notification daily top 3 bài mới (optional).

### 3.6 Burnout Guard & Report
- Daily check-in: mood (emoji 1-5) + energy level.
- Nếu thấp 2 ngày liên tiếp → suggest "Nghỉ 1 ngày code-free" hoặc "Đi bộ 15 phút".
- Weekly report: % hoàn thành habit, thời gian học vs nghỉ, chart đơn giản.

---

## 4. Yêu cầu phi chức năng (Non-Functional Requirements)

- **Performance:** Load <2s, smooth animation (60fps).
- **Privacy:** All data local/iCloud, không track analytics MVP.
- **Accessibility:** Support VoiceOver, Dynamic Type, Dark Mode auto.
- **Offline:** 100% functions work offline (sync khi online).
- **Battery:** Background fetch nhẹ (≤5% pin/ngày).
- **Size:** App <50MB.
- **Security:** Encrypt local data (SwiftData/Core Data).

---

## 5. Giao diện & UX (High-level UI/UX)

- **Design system:** Native iOS Human Interface Guidelines (HIG) 2026.
- Màu sắc: Dark theme chính (xanh dương tech + xám), accent: xanh lá (progress).
- Navigation: Tab bar dưới (Home, Habits, Notes, Feed).
- Widget: 3 size (small/medium/large).
- Live Activities: khi đang trong block học (timer countdown trên Dynamic Island nếu iPhone 14+).

---

## 6. Technical Requirements

- **Platform:** iOS 17+ (target iOS 18/19 năm 2026).
- **Ngôn ngữ:** Swift 6+, SwiftUI.
- **Storage:** SwiftData (hoặc Core Data).
- **Framework:** WidgetKit, UserNotifications, HealthKit (workout/sleep), Speech (voice), Charts (report).
- **Sync:** CloudKit (free, private).
- **AI lite (optional):** Apple Intelligence nếu public API (summarize note).
- **Testing:** Unit test ≥70% coverage core logic.

---

## 7. Roadmap & Milestones (MVP)

- **Phase 1 (2-4 tuần):** Setup project, onboarding, planner + widget.
- **Phase 2 (3-4 tuần):** Habit tracker + notification.
- **Phase 3 (2-3 tuần):** Note + feed + burnout guard.
- **Phase 4 (2 tuần):** Polish UI, TestFlight beta, App Store submit.

---

## 8. Phụ lục

- **Lịch mẫu dev (reference):** (copy từ lịch trước: 5:30 dậy → 23:00 ngủ).
- **Wireframe gợi ý:** (bạn có thể vẽ nhanh bằng Figma hoặc dùng AI như Uizard).
- **Tài liệu tham khảo:** Apple HIG, SwiftUI Tutorials, IEEE SRS template.

---

**Tài liệu này có thể mở rộng thành SRS chi tiết hơn nếu cần (thêm use case diagram, flow chi tiết từng screen).**
