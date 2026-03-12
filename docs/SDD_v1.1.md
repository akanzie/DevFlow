# Tài liệu Thiết kế Hệ thống (System Design Document - SDD) - Python  
**Tên phần mềm:** DailyClip – Công cụ tự động hóa ghi chú và lưu trữ dữ liệu cá nhân  
**Phiên bản:** 1.1 (Python)  

## 1. Giới thiệu

### 1.1 Mục đích
Tài liệu này mô tả thiết kế cấp cao (High-Level Design) và một số thiết kế chi tiết (Low-Level Design) cần thiết để triển khai phần mềm **DailyClip** (Python version) theo đúng SRS v1.1. Nó định nghĩa kiến trúc hệ thống, các thành phần chính, giao tiếp giữa chúng, luồng dữ liệu, và các quyết định kỹ thuật quan trọng, đặc biệt tập trung vào **giao diện hợp nhất (Unified Window)** và trải nghiệm người dùng **không gián đoạn (Zero-interruption)**.

### 1.2 Phạm vi
- Thiết kế cho phiên bản Windows standalone, tập trung vào trải nghiệm người dùng liền mạch và hiệu suất cao.
- Bao gồm các tính năng mới: Unified Window, Silent Update, Version History, Smart Grouping, và các yêu cầu bảo mật cơ bản.
- Không bao gồm: đồng bộ đám mây, AI tagging (các tính năng mở rộng sau).

### 1.3 Tài liệu tham chiếu
- SRS.md (v1.1)
- Các REQ-ID và NFR-ID từ SRS dùng để trace ngược.

## 2. Tổng quan hệ thống & Mục tiêu thiết kế

### 2.1 Mô tả hệ thống
DailyClip là ứng dụng desktop Windows (Python + PyQt6) chạy nền, có kiến trúc hướng sự kiện. Ứng dụng cung cấp một **cửa sổ chính hợp nhất** theo phong cách Spotlight, được kích hoạt bằng phím tắt toàn cục. Nó tự động giám sát và lưu trữ clipboard, ảnh chụp màn hình, đồng thời xử lý thông minh các nội dung trùng lặp thông qua "cập nhật im lặng" và "quản lý phiên bản". Người dùng có thể tìm kiếm, duyệt, xem trước và chỉnh sửa nội dung ngay trong một giao diện duy nhất.

### 2.2 Mục tiêu thiết kế chính
- **Local-first & Lightweight**: Không phụ thuộc server, RAM < 150MB, tối ưu hóa việc sử dụng đĩa.
- **Performance & Scalability**: Tìm kiếm < 1s với 100.000 clips; khởi động nhanh.
- **Zero-interruption UX**: Mọi hoạt động nền (lưu, kiểm tra trùng lặp) phải diễn ra âm thầm, không làm phiền người dùng.
- **Reliability & Resiliency**: Không mất dữ liệu khi clipboard thay đổi nhanh, có cơ chế phục hồi sau sự cố (crash recovery).
- **Extensibility**: Dễ dàng thêm các module mới như đồng bộ, mã hóa nâng cao.
- **Security**: Cung cấp các tùy chọn bảo mật cơ bản như khóa ứng dụng và mã hóa dữ liệu.

## 3. Kiến trúc hệ thống (System Architecture)

### 3.1 Tổng quan kiến trúc
DailyClip tiếp tục sử dụng kiến trúc **Layered + Event-Driven**, nhưng với giao diện được hợp nhất:
- **Presentation Layer**: Một cửa sổ duy nhất `UnifiedMainWindow` (PyQt6) quản lý tất cả các tương tác người dùng. Cửa sổ này có nhiều trạng thái (thanh tìm kiếm nhỏ, cửa sổ mở rộng) và chế độ (Tìm kiếm, Duyệt, Ghi chú, Gallery).
- **Application Layer**: `AppController` điều phối các dịch vụ, xử lý sự kiện từ các lớp dưới và định tuyến chúng đến UI.
- **Domain Layer**: Các thực thể dữ liệu (`ClipItem`, `SearchResult`) và các giao ước (Protocols) cho các dịch vụ.
- **Infrastructure Layer**: Các triển khai cụ thể cho việc truy cập hệ thống file, index DuckDB, giám sát clipboard, chụp ảnh màn hình, và mã hóa.

### 3.2 Biểu đồ kiến trúc cấp cao (Context Diagram C4-Level 1)

```
┌──────────┐
│   User   │
└────┬─────┘
     │ Ctrl+C, Print Screen, Alt+S, Alt+Space
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
| AppController           | Khởi tạo ứng dụng, kết nối các dịch vụ, quản lý tray icon, định tuyến hotkey. | PyQt6 + asyncio                         | REQ-201, NFR-004                  |
| **UnifiedMainWindow**   | **(Mới)** Cửa sổ chính duy nhất, quản lý các trạng thái (nhỏ/mở rộng) và chế độ (tìm kiếm/duyệt/ghi chú). Tích hợp panel preview và chỉnh sửa. | PyQt6 (QMainWindow, QLineEdit, etc.)    | REQ-202, REQ-203, REQ-204, REQ-205 |
| ClipboardMonitor        | Giám sát clipboard, phát hiện trùng lặp (exact/similar), lấy metadata nguồn ứng dụng, tạo `ClipItem`. | `pyperclip`, `difflib`, `pygetwindow`   | REQ-101 → REQ-104, REQ-106, REQ-206 |
| ScreenCaptureService    | Chụp ảnh màn hình và đưa vào luồng xử lý.                                  | PyQt6 / PIL / mss                       | REQ-105                           |
| HotkeyManager           | Đăng ký và xử lý các phím tắt toàn cục.                                     | `keyboard` / `pynput`                   | REQ-201                           |
| StorageService          | Quản lý file/thư mục, lưu/đọc `ClipItem`, quản lý phiên bản, xử lý mã hóa file. | `pathlib`, `json`, `cryptography`       | REQ-001 → REQ-003, REQ-104c, REQ-402 |
| SearchService           | Index và tìm kiếm dữ liệu text từ clips/notes.                             | DuckDB                                  | REQ-301 → REQ-303                 |
| **SecurityService**     | **(Mới)** Quản lý khóa ứng dụng (mật khẩu/Windows Hello) và vòng đời của khóa mã hóa. | `local-auth` (cho Win Hello), `cryptography` | REQ-401, REQ-402                  |
| TrayIcon & Background   | Chạy nền, hiển thị thông báo, cung cấp menu ngữ cảnh.                       | PyQt6 QSystemTrayIcon                   | NFR-004                           |

## 4. Thiết kế dữ liệu (Data Design)

### 4.1 Cấu trúc thư mục (Storage Structure)
```
DailyClipRoot/
├── 2026-03-06/
│   ├── images/
│   │   └── screen_[HH-mm-ss].png
│   ├── clippings/
│   │   └── clips_2026-03-06.jsonl   (Một file/ngày, append-only)
│   └── notes/
│       └── notes_2026-03-06.md
├── search_index.duckdb
├── config.json
└── .encryption_key              (Tùy chọn, nếu mã hóa được bật)
```

### 4.2 Định dạng dữ liệu chính
- **Clip JSONL record** (mỗi dòng trong `clips_YYYY-MM-DD.jsonl`):
  ```json
  {
    "clip_id": "uuid-v4-string",
    "timestamp": "2026-03-06T09:30:05+07:00",
    "type": "text|image",
    "content": "...",
    "format": "plain|markdown|code",
    "source_app_name": "vscode.exe",
    "source_window_title": "main.py - MyProject",
    "version_of": "parent-clip-id-or-null",
    "hash": "sha256-of-content"
  }
  ```
- **Search index record** (Bảng trong DuckDB):
  - Columns: `clip_id`, `timestamp`, `content`, `source_app_name`, `file_path`.

## 5. Luồng dữ liệu chính (Key Data Flows)

### 5.1 Luồng Clipboard → Lưu trữ (Zero-interruption)
1.  `ClipboardMonitor` đọc nội dung clipboard (text/image).
2.  Tạo hash (SHA256) cho nội dung.
3.  **Kiểm tra trùng lặp 100% (Silent Update)**:
    -   Query `SearchService` bằng hash.
    -   Nếu tìm thấy `clip_id` đã tồn tại -> Gửi sự kiện "update timestamp" cho `clip_id` đó -> Kết thúc.
4.  **Kiểm tra nội dung gần giống (Version History)**:
    -   Lấy clip gần nhất từ cùng `source_app_name`.
    -   Dùng `difflib.SequenceMatcher` để so sánh độ tương đồng.
    -   Nếu > 90% giống -> Tạo `ClipItem` mới với `version_of` trỏ đến `clip_id` của clip gốc.
5.  **Lưu clip mới**:
    -   Nếu không thuộc các trường hợp trên, tạo `ClipItem` mới (với `version_of` là null).
    -   Lấy metadata nguồn (`pygetwindow`).
6.  `StorageService` mã hóa (nếu bật) và ghi `ClipItem` vào file `.jsonl` của ngày hiện tại.
7.  `SearchService` thực hiện index tăng dần cho `ClipItem` mới.

### 5.2 Luồng Tương tác Cửa sổ chính (Unified Window Flow)
1.  Người dùng nhấn `Alt+Space`.
2.  `UnifiedMainWindow` hiển thị ở trạng thái **thanh tìm kiếm nổi**.
3.  **Kịch bản 1: Người dùng gõ tìm kiếm**:
    -   Sau 300ms (debounce), `SearchService` được gọi.
    -   Kết quả được hiển thị trực tiếp bên dưới thanh tìm kiếm.
4.  **Kịch bản 2: Ô tìm kiếm trống**:
    -   Cửa sổ hiển thị chế độ **Duyệt theo ngày**, nhóm các clip theo nguồn ứng dụng.
5.  **Hành động**:
    -   Khi người dùng chọn một item -> Cửa sổ **mở rộng**, hiển thị danh sách bên trái và **panel preview/chỉnh sửa** bên phải.
    -   Người dùng có thể chỉnh sửa nội dung trực tiếp và lưu bằng `Ctrl+S`.
    -   Nhấn `Esc` sẽ đưa cửa sổ về trạng thái thanh tìm kiếm nhỏ, hoặc đóng nếu đang ở trạng thái nhỏ.

## 6. Thiết kế giao diện & Tương tác (UI/UX Design)

- **Unified Main Window**: Một cửa sổ `QMainWindow` không viền (`FramelessWindowHint`) và luôn ở trên (`WindowStaysOnTopHint`).
  - **Trạng thái thu gọn (Compact State)**: Chỉ hiển thị một `QLineEdit` để tìm kiếm.
  - **Trạng thái mở rộng (Expanded State)**: Sử dụng `QSplitter` để chia khu vực danh sách (trái) và khu vực preview/chỉnh sửa (phải).
- **Chế độ xem (Modes)**: Sử dụng `QStackedWidget` hoặc các view có thể ẩn/hiện để chuyển đổi giữa:
  - **Search/Browse View**: Dùng `QTreeView` để hỗ trợ nhóm (Smart Grouping).
  - **Gallery View**: Dùng `QListView` với custom delegate để hiển thị thumbnail ảnh.
  - **Note View**: Dùng `QTextEdit` hỗ trợ Markdown.
- **Panel Preview/Chỉnh sửa**:
  - Hiển thị nội dung text với syntax highlighting (nếu là code).
  - Cho phép chỉnh sửa trực tiếp. Khi người dùng bắt đầu gõ, một "lock" tạm thời được đặt lên item để giải quyết xung đột (REQ-204).
  - Hiển thị ảnh với các nút hành động nhanh (Copy, Xóa, ...).
- **Luồng đóng**: Nhấn `Esc` sẽ gọi một hàm `dismiss()` trên cửa sổ, hàm này sẽ kiểm tra trạng thái hiện tại để quyết định thu nhỏ hay đóng hoàn toàn.

## 7. Rủi ro & Giải pháp giảm thiểu

- **Rủi ro**: `difflib` có thể chậm khi so sánh các đoạn text lớn, gây trễ khi copy.
  - **Giải pháp**: Chỉ chạy so sánh cho các clip text có độ dài hợp lý (< 10KB) và chỉ so với clip gần nhất từ cùng một nguồn.
- **Rủi ro**: Quản lý khóa mã hóa phức tạp, người dùng có thể làm mất khóa.
  - **Giải pháp**: Cảnh báo rõ ràng cho người dùng về trách nhiệm sao lưu khóa. Tích hợp với Windows Credential Manager để lưu khóa an toàn hơn.
- **Rủi ro**: Cửa sổ hợp nhất trở nên quá tải và phức tạp.
  - **Giải pháp**: Giữ cho thiết kế tối giản, chỉ hiển thị các điều khiển cần thiết theo ngữ cảnh.
- **Rủi ro**: Xung đột hotkey toàn cục.
  - **Giải pháp**: Cho phép người dùng tùy chỉnh hotkey trong `config.json`.

## 8. Performance Considerations

- **Memory**: Giữ mức sử dụng RAM dưới 150MB khi chạy nền.
- **Search**: Tối ưu hóa schema và query DuckDB để đạt được thời gian phản hồi < 1s với 100.000 clips.
- **UI Responsiveness**: Tải ảnh và nội dung lớn trong panel preview trên một thread riêng (worker thread) để không làm đóng băng UI.
- **Crash Recovery**: `StorageService` cần ghi vào một file tạm trước khi ghi vào file `.jsonl` chính thức. `SearchService` có thể rebuild index từ file nguồn nếu file index bị hỏng.

## 9. Phụ lục
- **Technology stack chi tiết** như trong SRS v1.1.
- **Roadmap**: v1.2 – Cải tiến Smart Grouping, hỗ trợ nhiều loại dữ liệu hơn; v2.0 – Tùy chọn đồng bộ đám mây (end-to-end encrypted).

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

---

### ADR-004: Thiết kế Giao diện Hợp nhất (Unified Window)

**Status:** ACCEPTED  
**Context:** SRS yêu cầu một trải nghiệm người dùng liền mạch, giảm thiểu số lượng cửa sổ và phím tắt cần nhớ.
**Decision:** Hợp nhất tất cả các chức năng (Tìm kiếm, Duyệt, Ghi chú, Gallery) vào một cửa sổ chính duy nhất có thể thay đổi trạng thái.
**Rationale:**
- **Giảm tải nhận thức**: Người dùng chỉ cần học một cửa sổ và một phím tắt chính (`Alt+Space`).
- **Tăng tốc quy trình làm việc**: Chuyển đổi giữa tìm kiếm, xem trước và chỉnh sửa diễn ra ngay lập tức mà không cần mở cửa sổ mới.
- **Thiết kế hiện đại**: Phù hợp với xu hướng của các công cụ năng suất hiện đại như Spotlight, Raycast, Alfred.

**Alternatives considered:**
- Giữ lại nhiều cửa sổ riêng biệt: Gây phân mảnh trải nghiệm, khó quản lý.

---

### ADR-005: Xử lý Trùng lặp bằng "Silent Update"

**Status:** ACCEPTED  
**Context:** Việc copy lặp lại một nội dung là hành vi phổ biến. Hiển thị hộp thoại xác nhận mỗi lần như vậy sẽ làm gián đoạn luồng làm việc của người dùng.
**Decision:** Khi phát hiện nội dung trùng lặp 100%, hệ thống sẽ tự động cập nhật timestamp của clip cũ và đưa nó lên đầu danh sách mà không có bất kỳ thông báo nào.
**Rationale:**
- **Zero-interruption**: Tôn trọng sự tập trung của người dùng. Ứng dụng hoạt động như một trợ lý thầm lặng.
- **Giữ dữ liệu gọn gàng**: Tránh tạo ra vô số bản sao của cùng một nội dung.
- **Hành vi có thể đoán trước**: Người dùng luôn tìm thấy nội dung họ vừa copy ở vị trí trên cùng.

**Alternatives considered:**
- Hiển thị hộp thoại "Lưu/Bỏ qua": Gây phiền nhiễu, làm chậm người dùng.
- Tự động bỏ qua mà không cập nhật timestamp: Khiến người dùng bối rối vì không thấy nội dung vừa copy ở đầu danh sách.
