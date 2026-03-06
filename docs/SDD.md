# Tài liệu Thiết kế Hệ thống (System Design Document - SDD)  
**Tên phần mềm:** DailyClip – Công cụ tự động hóa ghi chú và lưu trữ dữ liệu cá nhân  
**Phiên bản:** 1.0 (Sơ bộ – High-Level Design)  
**Ngày soạn thảo:** 06/03/2026  
**Tác giả:** Kiệt (với hỗ trợ tinh chỉnh)  

## 1. Giới thiệu

### 1.1 Mục đích
Tài liệu này mô tả thiết kế cấp cao (High-Level Design) và một số thiết kế chi tiết (Low-Level Design) cần thiết để triển khai phần mềm **DailyClip** theo đúng SRS. Nó định nghĩa kiến trúc hệ thống, các thành phần chính, giao tiếp giữa chúng, luồng dữ liệu, và các quyết định kỹ thuật quan trọng.

### 1.2 Phạm vi
- Thiết kế cho phiên bản Windows native đầu tiên (offline-first, local storage).  
- Không bao gồm: đồng bộ đám mây, multi-platform, AI tagging (các tính năng mở rộng sau).

### 1.3 Tài liệu tham chiếu
- SRS.md 
- Các REQ-ID từ SRS dùng để trace ngược.

## 2. Tổng quan hệ thống & Mục tiêu thiết kế

### 2.1 Mô tả hệ thống
DailyClip là ứng dụng desktop Windows chạy nền, giám sát clipboard, hỗ trợ chụp màn hình nhanh, ghi chú Markdown, index & tìm kiếm local toàn cục dữ liệu theo ngày.

### 2.2 Mục tiêu thiết kế chính
- **Local-first & Lightweight**: Không phụ thuộc server, RAM < 100MB khi idle, disk usage tối ưu.  
- **Performance**: Search < 500ms với hàng chục nghìn file tích lũy.  
- **Reliability**: Không mất dữ liệu khi clipboard thay đổi nhanh, crash-proof.  
- **Extensibility**: Dễ thêm tag, sync, encrypt sau này.  
- **Modern UX**: Giao diện Mica/Acrylic, global hotkey mượt.

## 3. Kiến trúc hệ thống (System Architecture)

### 3.1 Tổng quan kiến trúc
DailyClip sử dụng kiến trúc **Layered + Event-Driven**:
- **Presentation Layer**: WinUI 3 windows (Quick Search, Quick Note, Gallery).
- **Application Layer**: Core logic (Clipboard monitor, Hotkey handler, Capture service, Indexer).
- **Domain Layer**: Entities (ClipItem, Note, Screenshot), Services (StorageService, SearchService).
- **Infrastructure Layer**: File system access, DuckDB index, ImageSharp, Windows API P/Invoke.

**Deployment View**: Single .exe + .dlls, chạy nền với System Tray icon.

### 3.2 Biểu đồ kiến trúc cấp cao (High-Level Architecture Diagram)
(Mô tả text – bạn có thể vẽ bằng Draw.io / Excalidraw)

```
[User] 
   ↓ Global Hotkeys (Alt+Space, Alt+N, Alt+S)
   ↓ System Tray Icon
[DailyClip App (WinUI 3 + .NET 9)]
   ├── Quick Search Window ──► SearchService (DuckDB FTS)
   ├── Quick Note Window ───► NoteService + Markdown Editor
   ├── Capture Service ─────► Windows.Graphics.Capture / BitBlt
   ├── Clipboard Monitor ───► Clipboard.ContentChanged event
   └── Storage Service ─────► File System ([Root]/[YYYY-MM-DD]/...)
                              └── Indexer → DuckDB daily_index.db
```

### 3.3 Các thành phần chính (Components)

| Thành phần              | Mô tả                                                                 | Công nghệ chính                          | Trách nhiệm chính (REQ liên quan) |
|-------------------------|-----------------------------------------------------------------------|------------------------------------------|-----------------------------------|
| ClipboardMonitor        | Giám sát clipboard thay đổi real-time, deduplicate, extract metadata | Clipboard.ContentChanged + P/Invoke     | REQ-101 → REQ-104                |
| ScreenCaptureService    | Chụp vùng/toàn màn/active window                                      | Windows.Graphics.Capture API (.NET 8+)  | REQ-105                          |
| HotkeyManager           | Đăng ký & xử lý global hotkeys                                        | RegisterHotKey (user32.dll) + WndProc   | REQ-201                          |
| StorageService          | Tạo folder ngày, lưu file theo quy ước, append JSONL                  | System.IO + SixLabors.ImageSharp        | REQ-001 → REQ-003                |
| NoteEditorService       | Markdown editor với auto-save                                         | Markdig + WinUI RichEdit / TextBox      | REQ-202                          |
| SearchService           | Index & full-text search                                              | DuckDB.NET (FTS extension)              | REQ-301 → REQ-303                |
| TrayIcon & Background   | Chạy nền, thông báo, menu context                                     | WinUI 3 NotifyIcon                      | NFR-004                          |

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
    "content": "...",               // text hoặc path đến image
    "format": "plain|markdown|code",
    "source_url": "https://..."     // nếu detect được từ HTML format
  }
  ```
- **DuckDB Table** (cho index):
  - Columns: id, timestamp, file_path, content_snippet, type, full_text (indexed FTS).

## 5. Luồng dữ liệu chính (Key Data Flows)

### 5.1 Luồng Clipboard → Lưu trữ
1. Clipboard change event fire.
2. ClipboardMonitor đọc content (text/image).
3. Deduplicate check (hash last 10s).
4. Tạo record JSON → append vào clips_[current].jsonl.
5. Nếu image → lưu PNG + metadata.
6. Indexer incremental update DuckDB.

### 5.2 Luồng Search
1. User mở Quick Search (Alt+Space).
2. Gõ query → debounce 300ms.
3. SearchService query DuckDB: `SELECT * FROM clips WHERE full_text MATCH ? ORDER BY timestamp DESC LIMIT 50`.
4. Hiển thị results (snippet + link mở file/folder).

## 6. Thiết kế giao diện & Tương tác (UI/UX Design)

- **Quick Search**: Borderless, topmost window, Acrylic background, SearchBox + ListView results.
- **Quick Note**: Floating window, Markdown editor (syntax highlight), auto-save timer.
- **Gallery**: GridView với virtualization (load on-demand), click → full preview.
- **Tray Menu**: Open search/note, Today folder, Settings, Exit.

## 7. Quyết định thiết kế & Trade-off

| Quyết định                  | Lý do chọn                                                                 | Alternative & tại sao bỏ |
|-----------------------------|-----------------------------------------------------------------------------|---------------------------|
| DuckDB thay vì SQLite       | Columnar + FTS native nhanh hơn nhiều cho text search trên file lớn        | SQLite FTS5 (dễ hơn nhưng chậm hơn ~2-5x) |
| WinUI 3 thay vì WPF         | Modern look (Mica), performance tốt hơn, native Windows 11 feel            | WPF (ổn định hơn nhưng UI cũ) |
| JSONL cho clips             | Append-only, dễ parse, không cần đọc toàn file                             | Single JSON (phải rewrite), Markdown (khó structured) |
| Global hotkey via P/Invoke  | Hỗ trợ system-wide, chuẩn Windows                                          | Thư viện third-party (thêm dependency) |

## 8. Rủi ro & Giải pháp giảm thiểu

- Rủi ro: Global hotkey conflict với app khác → Giải pháp: Cho phép tùy chỉnh phím tắt + fallback.
- Rủi ro: Clipboard monitor miss event → Giải pháp: Poll fallback mỗi 1-2s nếu cần.
- Rủi ro: DuckDB corruption → Giải pháp: Backup index hàng ngày + retry mechanism.

## 9. Phụ lục
- **Công nghệ stack chi tiết** (như trong SRS).
- **Ước lượng effort sơ bộ**: ~4-6 tuần cho MVP (1 dev full-time).
- **Roadmap**: v1.1 – cleanup old data, export zip; v2 – cloud sync option.
