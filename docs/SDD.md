# Tài liệu Thiết kế Hệ thống (System Design Document - SDD) - Python  
**Tên phần mềm:** DailyClip – Công cụ tự động hóa ghi chú và lưu trữ dữ liệu cá nhân  
**Phiên bản:** 1.0 (Python)  

## 1. Giới thiệu

### 1.1 Mục đích
Tài liệu này mô tả thiết kế cấp cao (High-Level Design) và một số thiết kế chi tiết (Low-Level Design) cần thiết để triển khai phần mềm **DailyClip** (Python version) theo đúng SRS. Nó định nghĩa kiến trúc hệ thống, các thành phần chính, giao tiếp giữa chúng, luồng dữ liệu, và các quyết định kỹ thuật quan trọng.

### 1.2 Phạm vi
- Thiết kế cho phiên bản Windows standalone đầu tiên (offline-first, local storage).  
- Không bao gồm: đồng bộ đám mây, multi-platform, AI tagging (các tính năng mở rộng sau).

### 1.3 Tài liệu tham chiếu
- SRS.md  
- Các REQ-ID từ SRS dùng để trace ngược.

## 2. Tổng quan hệ thống & Mục tiêu thiết kế

### 2.1 Mô tả hệ thống
DailyClip là ứng dụng desktop Windows Python + PyQt6 chạy nền, giám sát clipboard, tiếp nhận ảnh screenshot từ clipboard hệ điều hành (Print Screen, Snipping Tool, Win+Shift+S), hỗ trợ chụp màn hình nội bộ bằng hotkey cấu hình được, ghi chú Markdown, index & tìm kiếm local toàn cục, đồng thời cho phép duyệt thư mục ngày và preview ảnh trực tiếp trong GUI.

### 2.2 Mục tiêu thiết kế chính
- **Local-first & Lightweight**: Không phụ thuộc server, RAM < 150MB (hơi cao hơn .NET do Python overhead), disk usage tối ưu.  
- **Performance**: Search < 500ms với hàng chục nghìn file tích lũy; mở danh sách duyệt ban đầu nhanh khi query rỗng.  
- **Reliability**: Không mất dữ liệu khi clipboard thay đổi nhanh, không bỏ sót ảnh screenshot từ clipboard hệ điều hành.  
- **Extensibility**: Dễ thêm tag, sync, encrypt sau này.  
- **Modern UX**: Giao diện PyQt6 hiện đại, global hotkey mượt, có browse mode và preview pane.

## 3. Kiến trúc hệ thống (System Architecture)

### 3.1 Tổng quan kiến trúc
DailyClip sử dụng kiến trúc **Layered + Event-Driven + Hybrid UI/Data Browser**:
- **Presentation Layer**: PyQt6 windows cho Quick Search/Explorer, Quick Note, Gallery và System Tray. Quick Search gồm ô tìm kiếm, danh sách duyệt/kết quả và preview pane.
- **Application Layer**: `AppController`, async runtime nền, điều phối startup/shutdown, đăng ký hotkey, routing sự kiện clipboard/capture/search.
- **Domain Layer**: Entities (`ClipItem`, `DailyNote`, `SearchResult`) và các contract cho storage, search, hotkey, clipboard monitor.
- **Infrastructure Layer**: File system access, DuckDB unified index, clipboard intake, screenshot capture, image preview loading, pyperclip/keyboard/Pillow.

**Deployment View**: Gói Python executable qua PyInstaller hoặc chạy từ source. Bản phân phối ổn định ưu tiên `onedir` để gom đủ dependency động; app chạy nền với System Tray icon.

### 3.2 Biểu đồ kiến trúc cấp cao (Context Diagram C4-Level 1)

```
┌──────────┐
│   User   │
└────┬─────┘
     │ Ctrl+C, Print Screen, Win+Shift+S,
     │ Alt+S, Alt+N, Alt+Space
     ↓
┌──────────────────────────────────────────┐
│   DailyClip Application (Python + PyQt6)│
│     (Single process, multi-threaded)    │
└──────────────────────────────────────────┘
     ↑ Uses            ↓ Stores          ↗ Queries
┌──────────┐     ┌──────────────┐     ┌──────────────┐
│ Windows  │     │ File System  │     │ DuckDB Index │
│   API    │     │ [Root]/...   │     │ search_index │
└──────────┘     └──────────────┘     └──────────────┘

No internet, no server, no cloud dependency (offline-first).
```

### 3.3 Các thành phần chính (Components)

| Thành phần              | Mô tả                                                                      | Công nghệ chính                         | Trách nhiệm chính (REQ liên quan) |
|-------------------------|----------------------------------------------------------------------------|-----------------------------------------|-----------------------------------|
| AppController           | Bootstrap app, wiring services, tray, hotkey routing, shutdown sạch        | PyQt6 + asyncio runtime                 | REQ-201 → REQ-206                 |
| ClipboardMonitor        | Giám sát clipboard text/image, deduplicate, nhận diện screenshot OS        | pyperclip + threading + queues          | REQ-101 → REQ-104, REQ-106        |
| ScreenCaptureService    | Chụp vùng/toàn màn/active window và đưa ảnh vào pipeline lưu trữ chuẩn hóa | PyQt6 / PIL / mss hoặc API tương đương  | REQ-105                           |
| HotkeyManager           | Đăng ký & xử lý global hotkeys                                             | keyboard / pynput library               | REQ-201                           |
| StorageService          | Tạo folder ngày, lưu file theo quy ước, append JSONL, liệt kê folder/file  | pathlib + json + Pillow                 | REQ-001 → REQ-003, REQ-204        |
| SearchService           | Index & search unified cho clips/notes, incremental rebuild                | DuckDB                                  | REQ-203, REQ-301 → REQ-303        |
| ExplorerPreviewAdapter  | Chuyển folder/file/result thành item GUI, nạp preview text/ảnh và metadata | PyQt6 + Pillow/QImage                   | REQ-203 → REQ-206                 |
| NoteEditorService       | Markdown editor với auto-save                                              | PyQt6 QPlainTextEdit                    | REQ-202                           |
| TrayIcon & Background   | Chạy nền, thông báo, menu context                                          | PyQt6 QSystemTrayIcon                   | NFR-004                           |

## 4. Thiết kế dữ liệu (Data Design)

### 4.1 Cấu trúc thư mục (Storage Structure)
```
DailyClipRoot/                  (có thể config, mặc định %AppData%/DailyClip)
├── 2026-03-06/
│   ├── images/
│   │   └── screen_[HH-mm-ss].png
│   ├── clippings/
│   │   └── clips_[HH-mm-ss].jsonl   (append nhiều record nếu cùng giây)
│   └── notes/
│       └── notes_2026-03-06.md      (một file/ngày, append sections)
├── search_index.duckdb              (global DuckDB index cho clips/notes)
└── config.json                      (root config: hotkeys, root folder, cleanup rules)
```

### 4.2 Định dạng dữ liệu chính
- **Clip JSONL record** (mỗi dòng):
  ```json
  {
    "timestamp": "2026-03-06T09:30:05+07:00",
    "type": "text|image",
    "content": "...",
    "format": "plain|markdown|code",
    "source_url": "https://...",
    "file_path": "..."
  }
  ```
- **Search index record** (logical model cho `SearchResult`):
  - Columns: `entry_id`, `entry_type`, `timestamp`, `content`, `preview`, `file_path`, `source_url`, `score`.
- **Preview metadata**:
  - Tối thiểu gồm: tên file, thời gian lưu, loại entry, đường dẫn file; với ảnh có thêm width/height nếu đọc được.

## 5. Luồng dữ liệu chính (Key Data Flows)

### 5.1 Luồng Clipboard / OS Screenshot → Lưu trữ
1. `ClipboardMonitor` polling khoảng 500ms hoặc nhận event thay đổi clipboard.
2. Đọc clipboard content dạng text hoặc image.
3. Nếu image đến từ Print Screen, Snipping Tool hoặc Win+Shift+S, pipeline xử lý vẫn giống image clipboard thông thường.
4. Thực hiện deduplicate trong cửa sổ 10 giây cho nội dung lặp.
5. Persist text vào `clips_[HH-mm-ss].jsonl`; persist image thành `.png` và metadata tương ứng.
6. Gửi tác vụ incremental update cho search index nếu entry có dữ liệu searchable.

### 5.2 Luồng Internal Capture Hotkey → Lưu trữ
1. User nhấn hotkey capture nội bộ (mặc định Alt+S, có thể cấu hình).
2. `ScreenCaptureService` chụp region / active window / fullscreen.
3. Ảnh được chuẩn hóa về cùng pipeline lưu trữ screenshot.
4. `StorageService` lưu `screen_[HH-mm-ss].png` vào `images/` và trả metadata cho UI/tray notification.

### 5.3 Luồng Quick Search / Browse / Preview
1. User mở Quick Search (Alt+Space).
2. Nếu query rỗng, `StorageService` liệt kê thư mục ngày và file theo thứ tự mới nhất trước.
3. Nếu query có nội dung, UI debounce 300ms rồi `SearchService` query DuckDB unified index, sort theo thời gian giảm dần, limit 50.
4. UI hiển thị cùng một danh sách cho cả browse mode và search mode.
5. Khi item được chọn:
   - nếu là image/screenshot: nạp preview ảnh scale phù hợp và metadata cơ bản.
   - nếu là text/note: hiển thị excerpt/preview text và metadata.
6. User có thể mở file, mở thư mục chứa hoặc copy nội dung phù hợp với loại entry.

## 6. Thiết kế giao diện & Tương tác (UI/UX Design)

- **Quick Search / Explorer**: PyQt6 floating window, topmost, gồm `QLineEdit` tìm kiếm, danh sách item duyệt/kết quả và preview pane bên phải hoặc phía dưới tùy layout.
- **Browse Mode mặc định**: Khi ô tìm kiếm trống, hiển thị danh sách thư mục ngày và file có sẵn thay vì empty state.
- **Preview Pane**: Nếu item là ảnh thì hiển thị preview scale vừa khung + metadata; nếu item là text/note thì hiển thị excerpt, timestamp và đường dẫn.
- **Quick Note**: Floating PyQt6 window, `QPlainTextEdit`, auto-save qua `QTimer` mỗi 5 giây và khi đóng/Esc.
- **Gallery**: `QGridLayout` hoặc model/view cho thumbnail; chọn ảnh sẽ đồng bộ sang preview pane hoặc dialog full-size.
- **Tray Menu**: PyQt6 `QSystemTrayIcon` → `QMenu` (Open Search, New Note, Open Today Folder, Exit).

## 7. Rủi ro & Giải pháp giảm thiểu

- Rủi ro: Python startup time / kích thước package lớn → Giải pháp: lazy initialization, tránh load preview asset trước khi cần.
- Rủi ro: Global hotkey conflict với app khác → Giải pháp: cho phép cấu hình phím tắt + fallback qua tray.
- Rủi ro: Clipboard monitor miss event hoặc không phân biệt được screenshot OS với image clipboard khác → Giải pháp: fallback polling thread, xử lý image clipboard theo pipeline screenshot hợp lệ.
- Rủi ro: Preview ảnh lớn gây lag UI → Giải pháp: lazy load, scale theo viewport, đọc metadata ngoài UI thread nếu cần.
- Rủi ro: DuckDB corruption hoặc packaging thiếu dependency động → Giải pháp: retry/rebuild index, ưu tiên build `onedir` cho release ổn định.

## 8. Performance Considerations

- **Memory**: PyQt6 GUI overhead ~80-100MB, DuckDB ~20-30MB, tổng < 150MB idle.
- **Startup**: ~1-2s tùy máy và mode đóng gói.
- **Search**: Query text < 500ms cho ~10k records.
- **Browse Mode**: Chỉ nạp danh sách thư mục/file và metadata nhẹ lúc mở; preview ảnh nạp lazy khi user chọn item.
- **Clipboard monitoring**: Background thread/polling, tác động thấp tới CPU.
- **Threading**: ClipboardMonitor + HotkeyListener trên thread riêng, UI trên main thread, preview/search có thể chuyển sang worker khi tải nặng.

## 9. Phụ lục
- **Technology stack chi tiết** như trong SRS.
- **Ước lượng effort sơ bộ**: ~3-5 tuần cho MVP (1 dev, tùy kinh nghiệm Python/PyQt6).
- **Roadmap**: v1.1 – cleanup old data, export zip; v2 – cloud sync option.

## 10. Ghi chép Quyết định Kiến trúc (Architecture Decision Records - ADRs)

### ADR-001: Chọn DuckDB thay vì SQLite cho Search Index

**Status:** ACCEPTED  
**Context:** DailyClip cần tìm kiếm nhanh trên hàng chục nghìn clips/notes và duy trì một global index đơn giản để query xuyên ngày.  
**Decision:** Sử dụng DuckDB (embedded) cho unified search index.  
**Rationale:**
- DuckDB phù hợp cho truy vấn text/search và rebuild index cục bộ.
- Một file index chung ở root giúp query xuyên ngày đơn giản hơn index theo từng ngày.
- Dễ backup và rebuild khi cần.

**Alternatives considered:**
- SQLite + FTS5 (đơn giản hơn nhưng không được chọn cho thiết kế hiện tại).

---

### ADR-002: Chọn PyQt6 thay vì alternative GUI framework

**Status:** ACCEPTED  
**Context:** Cần GUI modern, native Windows feel, responsive, hỗ trợ browse list + preview pane.  
**Decision:** Sử dụng PyQt6.  
**Rationale:**
- Widget system đủ linh hoạt cho floating search window, preview pane, tray và note editor.
- Signal/Slot mechanism phù hợp cho event-driven UI.
- Native integration tốt trên Windows.
- Mature ecosystem cho packaging desktop app.

**Alternatives considered:**
- Tkinter (built-in, nhưng hạn chế về UI/UX).
- PySimpleGUI (đơn giản hơn, nhưng khó tùy biến cho browse/preview flow).
- Electron + Python backend (quá nặng cho mục tiêu local-first lightweight).

---

### ADR-003: Chọn PyInstaller onedir mode làm bản phân phối mặc định

**Status:** ACCEPTED  
**Context:** Ứng dụng dùng PyQt6, DuckDB, dependency injection và một số import động; bản `onefile` khó ổn định hơn trong đóng gói thực tế.  
**Decision:** Dùng PyInstaller `--onedir` làm bản phát hành mặc định; `--onefile` chỉ giữ như target thử nghiệm hoặc debug packaging.  
**Rationale:**
- `onedir` gom dependency động ổn định hơn cho PyQt6, DuckDB và `dependency_injector`.
- Dễ smoke-test, debug log và xử lý hidden import.
- Startup nhất quán hơn do không cần self-extract mỗi lần chạy.

**Alternatives considered:**
- PyInstaller `--onefile` (gọn hơn nhưng fragile hơn với dependency động).
- MSI installer (phức tạp hơn, không cần thiết cho MVP).
- Chạy từ source + venv (phù hợp dev, không phù hợp end-user).

