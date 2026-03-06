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
DailyClip là ứng dụng desktop Windows Python + PyQt6 chạy nền, giám sát clipboard, hỗ trợ chụp màn hình nhanh, ghi chú Markdown, index & tìm kiếm local toàn cục dữ liệu theo ngày.

### 2.2 Mục tiêu thiết kế chính
- **Local-first & Lightweight**: Không phụ thuộc server, RAM < 150MB (hơi cao hơn .NET do Python overhead), disk usage tối ưu.  
- **Performance**: Search < 500ms với hàng chục nghìn file tích lũy.  
- **Reliability**: Không mất dữ liệu khi clipboard thay đổi nhanh, crash-proof.  
- **Extensibility**: Dễ thêm tag, sync, encrypt sau này.  
- **Modern UX**: Giao diện PyQt6 modern, global hotkey mượt.

## 3. Kiến trúc hệ thống (System Architecture)

### 3.1 Tổng quan kiến trúc
DailyClip sử dụng kiến trúc **Layered + Event-Driven** (Python version):
- **Presentation Layer**: PyQt6 windows (Quick Search, Quick Note, Gallery).
- **Application Layer**: Core logic (Clipboard monitor, Hotkey handler, Capture service, Indexer).
- **Domain Layer**: Entities (ClipItem, Note, Screenshot), Services (StorageService, SearchService).
- **Infrastructure Layer**: File system access, DuckDB index, PIL for images, pyperclip for clipboard.

**Deployment View**: Single Python package (.exe via PyInstaller) hoặc Python source files, chạy nền với System Tray icon.

### 3.2 Biểu đồ kiến trúc cấp cao (Context Diagram C4-Level 1)

```
┌──────────┐
│   User   │
└────┬─────┘
     │ Ctrl+C, Alt+S, Alt+N, Alt+Space
     ↓
┌─────────────────────────────────────────┐
│   DailyClip Application (Python + PyQt6) │
│    (Single process, multi-threaded)     │
└─────────────────────────────────────────┘
     ↑ Uses          ↓ Stores      ↗ Queries
┌──────────┐   ┌──────────────┐  ┌─────────┐
│ Windows  │   │ File System  │  │ DuckDB  │
│   API    │   │ [Root]/...   │  │  Index  │
└──────────┘   └──────────────┘  └─────────┘

No internet, no server, no cloud dependency (offline-first).
```

### 3.3 Các thành phần chính (Components)

| Thành phần              | Mô tả                                                                 | Công nghệ chính                          | Trách nhiệm chính (REQ liên quan) |
|-------------------------|-----------------------------------------------------------------------|------------------------------------------|-----------------------------------|
| ClipboardMonitor        | Giám sát clipboard thay đổi real-time, deduplicate, extract metadata | pyperclip + threading + queues            | REQ-101 → REQ-104                |
| ScreenCaptureService    | Chụp vùng/toàn màn/active window                                      | pyautogui / mss + PIL                    | REQ-105                          |
| HotkeyManager           | Đăng ký & xử lý global hotkeys                                        | keyboard / pynput library                | REQ-201                          |
| StorageService          | Tạo folder ngày, lưu file theo quy ước, append JSONL                  | pathlib + json + Pillow                 | REQ-001 → REQ-003                |
| NoteEditorService       | Markdown editor với auto-save                                         | markdown2 + PyQt6 QPlainTextEdit          | REQ-202                          |
| SearchService           | Index & full-text search                                              | DuckDB (duckdb package)                 | REQ-301 → REQ-303                |
| TrayIcon & Background   | Chạy nền, thông báo, menu context                                     | PyQt6 QSystemTrayIcon                   | NFR-004                          |

## 4. Thiết kế dữ liệu (Data Design)

### 4.1 Cấu trúc thư mục (Storage Structure)
```
DailyClipRoot/                  (có thể config, mặc định %AppData%/DailyClip)
├── 2026-03-06/
│   ├── images/
│   │   └── screen_[HH-mm-ss].png
│   ├── clippings/
│   │   └── clips_[HH-mm-ss].jsonl   (append nhiều record nếu cùng giây)
│   ├── notes/
│   │   └── notes_2026-03-06.md      (một file/ngày, append sections)
│   └── index/
│       └── daily_index.duckdb       (DuckDB file cho FTS index)
└── config.json                  (root config: hotkeys, root folder, cleanup rules)
```

### 4.2 Định dạng dữ liệu chính
- **Clip JSONL record** (mỗi dòng):
  ```json
  {
    "timestamp": "2026-03-06T09:30:05+07:00",
    "type": "text|image|html",
    "content": "...",               
    "format": "plain|markdown|code",
    "source_url": "https://..."     
  }
  ```
- **DuckDB Table** (cho index):
  - Columns: id, timestamp, file_path, content_snippet, type, full_text (indexed FTS).

## 5. Luồng dữ liệu chính (Key Data Flows)

### 5.1 Luồng Clipboard → Lưu trữ
1. ClipboardMonitor polling/event fire (threading handler).
2. Đọc clipboard content via pyperclip (text/image).
3. Deduplicate check (hash last 10s - MemoryCache hoặc simple dict).
4. Tạo record JSON → append vào clips_[current].jsonl.
5. Nếu image → lưu PNG via PIL + metadata.
6. Indexer incremental update DuckDB.

### 5.2 Luồng Search
1. User mở Quick Search (Alt+Space).
2. Gõ query → debounce 300ms (QTimer).
3. SearchService query DuckDB: `SELECT * FROM clips WHERE full_text MATCH ? ORDER BY timestamp DESC LIMIT 50`.
4. Hiển thị results (snippet + link mở file/folder).

## 6. Thiết kế giao diện & Tương tác (UI/UX Design)

- **Quick Search**: PyQt6 QMainWindow (frameless possible), mica-like dark palette, QLineEdit + QListWidget results.
- **Quick Note**: Floating PyQt6 QMainWindow, QPlainTextEdit, auto-save QTimer (5s).
- **Gallery**: QGridLayout với QLabel thumbnails, virtualization via QAbstractItemModel.
- **Tray Menu**: PyQt6 QSystemTrayIcon → QMenu (Open search/note, Today folder, Settings, Exit).

## 7. Rủi ro & Giải pháp giảm thiểu

- Rủi ro: Python startup time / PyInstaller size → Giải pháp: Load on demand, lazy initialization.
- Rủi ro: Global hotkey conflict với app khác → Giải pháp: Tùy chỉnh phím tắt + fallback.
- Rủi ro: Clipboard monitor miss event (threading race) → Giải pháp: Fallback polling thread.
- Rủi ro: DuckDB corruption → Giải pháp: Backup index hàng ngày + retry mechanism.

## 8. Performance Considerations

- **Memory**: PyQt6 GUI overhead ~80-100MB, duckdb ~20-30MB, total < 150MB idle.
- **Startup**: ~1-2s (PyInstaller, depends on machine).
- **Search**: DuckDB FTS < 500ms for 10k records.
- **Clipboard monitoring**: Background thread, minimal impact.
- **Threading**: ClipboardMonitor + HotkeyListener on separate threads, UI on main QThread.

## 9. Phụ lục
- **Technology stack chi tiết** như trong SRS_Python.
- **Ước lượng effort sơ bộ**: ~3-5 tuần cho MVP (1 dev, tùy kinh nghiệm Python/PyQt6).
- **Roadmap**: v1.1 – cleanup old data, export zip; v2 – cloud sync option.

## 10. Ghi chép Quyết định Kiến trúc (Architecture Decision Records - ADRs)

### ADR-001: Chọn DuckDB thay vì SQLite cho Full-Text Search

**Status:** ACCEPTED  
**Context:** DailyClip cần tìm kiếm nhanh trên hàng chục nghìn clips/notes.  
**Decision:** Sử dụng DuckDB (embedded).  
**Rationale:**
- DuckDB columnar → FTS ~3-5x nhanh hơn SQLite FTS5 trên workload text-heavy.
- Hỗ trợ FTS native.
- Single-file database → dễ backup.
- OLAP/analytics quicker → future feature (statistics, trends).

**Alternatives considered:**
- SQLite + FTS5 (simpler, nhưng chậm hơn cho large text queries).

---

### ADR-002: Chọn PyQt6 thay vì alternative GUI framework

**Status:** ACCEPTED  
**Context:** Cần GUI modern, native Windows feel, responsive.  
**Decision:** Sử dụng PyQt6.  
**Rationale:**
- Signal/Slot mechanism → clean event handling.
- Modern widgets, theming support.
- Excellent Windows native integration.
- Mature community, good documentation.

**Alternatives considered:**
- Tkinter (built-in, but limited UI).
- PySimpleGUI (simpler, but less customizable).
- Electron + Python backend (overkill for desktop app).

---

### ADR-003: Chọn PyInstaller one-file mode cho distribution

**Status:** ACCEPTED  
**Context:** Người dùng mong muốn single executable, không cần setup.  
**Decision:** Dùng PyInstaller với `--onefile`, hook DuckDB.  
**Rationale:**
- Users thích download 1 file duy nhất.
- Dễ distribute, update.
- Portable, no installer complexity.

**Alternatives considered:**
- MSI installer (more complex, doesn't match user expectation).
- exe + separate Python runtime (messy).
