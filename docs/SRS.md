# Tài liệu Đặc tả Yêu cầu Phần mềm (SRS) - Python  
**Tên phần mềm:** DailyClip – Công cụ tự động hóa ghi chú và lưu trữ dữ liệu cá nhân  
**Phiên bản:** 1.0 (Python)  

## 1. Giới thiệu

### 1.1 Mục đích
Tài liệu này mô tả các yêu cầu chức năng và phi chức năng của phần mềm **DailyClip** (Python version) – công cụ hỗ trợ năng suất cá nhân chạy nền trên Windows, tự động thu thập, phân loại và lưu trữ dữ liệu từ clipboard, ảnh chụp màn hình, cùng với giao diện ghi chú nhanh và tìm kiếm toàn cục.

Mục tiêu chính: Giảm thiểu thao tác thủ công khi lưu ý tưởng, code snippet, hình ảnh, giúp người dùng truy xuất thông tin cực nhanh mà không phụ thuộc vào đám mây.

### 1.2 Phạm vi sản phẩm
- **Trong phạm vi**:  
  - Tự động giám sát và lưu clipboard (text, image).  
  - Chụp màn hình nhanh bằng phím tắt hoặc tiếp nhận ảnh chụp từ clipboard hệ điều hành (Print Screen, Win+Shift+S).  
  - Ghi chú nhanh hỗ trợ Markdown với auto-save.  
  - Tìm kiếm toàn cục (global search) trên dữ liệu đã lưu.  
  - Xem trước ảnh theo ngày và preview ảnh ngay trong GUI khi chọn file/kết quả ảnh.  
  - Chạy nền với system tray icon.
  - **Tùy chỉnh & chỉnh sửa file**: Có khả năng sửa tên file (rename), chỉnh sửa nội dung notes và clips, xóa file từ GUI.
  - **Auto-start**: Tùy chọn tự động khởi động ứng dụng khi Windows khởi động.
  - **Lọc trùng lặp thông minh**: Phát hiện và xử lý exact duplicate, similar content (1–2 ký tự khác), với tùy chọn cảnh báo hoặc gộp tự động.

- **Ngoài phạm vi**:  
  - Đồng bộ đám mây (có thể mở rộng sau).  
  - Hỗ trợ đa nền tảng (chỉ Windows native v1).  
  - AI phân loại/tóm tắt nội dung (phiên bản sau).

## 2. Mô tả tổng quát

### 2.1 Quan điểm sản phẩm
DailyClip là sự kết hợp giữa clipboard manager (như Ditto), screenshot tool (như ShareX), quick note (như Notepad++ floating), và local search engine (như Everything/Obsidian local search), nhưng tự động hóa cao hơn và tập trung vào tổ chức theo ngày.

### 2.2 Chức năng sản phẩm
- Tự động tạo thư mục theo ngày khi khởi động hoặc chuyển ngày.  
- Lưu clipboard thay đổi (text → JSONL, image → PNG).  
- Chụp màn hình vùng/toàn màn hình/active window bằng hotkey nội bộ hoặc nhận ảnh screenshot từ clipboard hệ điều hành (Print Screen, Win+Shift+S) và lưu tự động.  
- Ghi chú nhanh Markdown với auto-save.  
- Tìm kiếm nhanh toàn cục (text trong clips/notes).  
- Duyệt danh sách thư mục ngày và file ngay khi mở GUI, kể cả khi chưa nhập từ khóa.  
- Xem lưới ảnh chụp trong ngày.
- Preview ảnh trực tiếp trong GUI khi người dùng chọn ảnh từ kết quả tìm kiếm, danh sách file hoặc gallery.
- **Lọc trùng lặp thông minh**: Phát hiện exact duplicate (100% giống), skip duplicate trong 10 giây, detect similar content (1–2 ký tự khác) với cảnh báo hoặc gộp tự động.
- **Chỉnh sửa & quản lý file**: Rename file trực tiếp từ GUI, chỉnh sửa nội dung notes, chỉnh sửa text của clips, xóa file, hỗ trợ bulk rename.
- **Auto-start Windows**: Tùy chọn tự động khởi động ứng dụng khi Windows khởi động, chạy nền tự động.

### 2.3 Đặc điểm người dùng
- Người dùng cá nhân, quen thuộc với phím tắt.  
- Ưu tiên tốc độ, nhẹ máy, dữ liệu local 100%.  
- Có thể tích lũy hàng nghìn file sau 1–2 năm.

### 2.4 Môi trường hoạt động
- Hệ điều hành: Windows 10/11 (64-bit).  
- Python: 3.10+ (CPython).  
- Dung lượng RAM đề xuất: ≥ 4GB (app chạy nền).  
- Không yêu cầu GPU hoặc internet (offline-first).

### 2.5 Giả định và ràng buộc
**Giả định**:  
- Người dùng chạy Windows và có quyền để đăng ký global hotkey.  
- Clipboard không bị chặn bởi phần mềm bảo mật bên thứ ba.

**Ràng buộc**:  
- Chỉ hỗ trợ Windows (v1).  
- Dữ liệu lưu local, không encrypt mặc định (có thể thêm sau).  
- Tối đa 1 instance chạy cùng lúc.

## 3. Yêu cầu cụ thể

### 3.1 Yêu cầu chức năng

#### 3.1.1 Quản lý lưu trữ (Storage Management)
- REQ-001: Tự động tạo thư mục gốc theo ngày **[Root]/[YYYY-MM-DD]** khi khởi động app hoặc lúc 00:00.  
- REQ-002: Trong mỗi ngày có các sub-folder:  
  - `images/` → ảnh chụp màn hình (.png).  
  - `clippings/` → dữ liệu clipboard (.jsonl cho text, .png cho image).  
  - `notes/` → file ghi chú thủ công (.md).  
- REQ-003: Tên file theo quy ước:  
  - Clips: `clips_[HH-mm-ss].jsonl` (append nếu cùng giây).  
  - Ảnh: `screen_[HH-mm-ss].png`.  
  - Notes: `notes_[YYYY-MM-DD].md` (một file/ngày).

#### 3.1.2 Tự động hóa Clipboard & Capture
- REQ-101: Giám sát sự kiện clipboard thay đổi (real-time via pyperclip/threading).  
- REQ-102: Khi clipboard có text → append object JSONL: `{ "timestamp": "...", "content": "...", "format": "text", "source_url": "..." }`.  
- REQ-103: Khi clipboard có image (bao gồm ảnh chụp từ Print Screen, Snipping Tool hoặc Win+Shift+S) → lưu .png vào images/ 
- REQ-103a: **Điều kiện tạo file khi copy (File Creation Conditions)**: Ứng dụng chỉ tạo file clip/image mới khi nội dung clipboard thay đổi và thỏa mãn: (1) Nội dung có độ dài tối thiểu (text ≥ 3 ký tự), (2) Là ảnh có độ phân giải hợp lệ (width × height ≥ 64×64 pixels), hoặc (3) Là dữ liệu có cấu trúc nhận diện được (URL, code, mã định dạng). Bỏ qua clipboard trống hoặc chứa dữ liệu không hợp lệ.
- REQ-104: **Deduplicate Strategy** (Chính sách loại bỏ trùng lặp):
  - **REQ-104a**: Bỏ qua nếu nội dung **giống đúc** (exact match 100%) với 1 clip đã copy trước đó trong **cùng 1 ngày** hoặc tìm thấy nội dung đó trong clippings/ → không tạo file mới.
  - **REQ-104b**: Bỏ qua nếu nội dung **giống hoàn toàn** với clip copy trước đó trong vòng **10 giây gần nhất** → không tạo file mới.
  - **REQ-104c**: Nếu nội dung **gần giống** (khác 1–2 ký tự hoặc có edit nhỏ, hoặc độ tương đồng > 95%) so với clip gần nhất:
    - **Option 1 (Cảnh báo)**: Hiển thị dialog hỏi user: *"Nội dung tương tự clip vừa copy (XX% giống). Lưu clip mới hay bỏ qua?"*
    - **Option 2 (Gộp tự động)**: Nếu đã có clip tương tự trong 5 phút gần nhất → tự động cập nhật metadata clip cũ (thêm timestamp mới) thay vì tạo file mới.
    - **Config tùy chọn**: User có thể cấu hình mode gộp tự động mà không cần cảnh báo.
- REQ-105: Ứng dụng hỗ trợ phím tắt chụp màn hình nội bộ (mặc định Alt+S, có thể cấu hình): hỗ trợ region / active window / fullscreen, lưu tự động vào images/.
- REQ-106: Nếu ảnh chụp được tạo bởi Print Screen, Snipping Tool hoặc Win+Shift+S và xuất hiện trên clipboard, ứng dụng phải tự nhận diện và lưu ảnh đó vào images/ như screenshot hợp lệ.

#### 3.1.3 Giao diện & Tương tác người dùng
- REQ-201: Global hotkey (system-wide):  
  - Alt+Space → mở Quick Search bar (floating, topmost).  
  - Alt+N → mở cửa sổ ghi chú nhanh (Markdown editor).  
  - Alt+S (mặc định, có thể cấu hình) → chụp màn hình.  
- REQ-202: Quick Note window: Editor Markdown, auto-save mỗi 5s hoặc khi Esc/đóng.  
- REQ-203: Quick Search: Thanh tìm kiếm realtime, hiển thị kết quả từ clips/notes/images, cho phép mở file hoặc thư mục chứa, và hiển thị preview nếu item đang chọn là ảnh.  
- REQ-204: Khi Quick Search mở với ô tìm kiếm trống, GUI phải hiển thị danh sách thư mục ngày và file hiện có để người dùng duyệt/chọn, thay vì chỉ có ô tìm kiếm rỗng.  
- REQ-205: Gallery view: Grid ảnh trong ngày, hỗ trợ preview ảnh đang chọn và click để mở full-size.
- REQ-206: Khi người dùng chọn file ảnh hoặc screenshot trong danh sách duyệt hoặc kết quả tìm kiếm, GUI phải hiển thị preview ảnh ngay trong cửa sổ hiện tại kèm metadata cơ bản (tên file, thời gian lưu).
- REQ-207: **Chỉnh sửa tên file và nội dung**: Người dùng có khả năng sửa tên file clips, notes hoặc images trực tiếp từ GUI (double-click tên file để rename, hoặc right-click → rename). Người dùng có thể mở và chỉnh sửa nội dung file .md (notes) trực tiếp từ Quick Note window hoặc text editor tích hợp, sau đó auto-save hoặc save manually. Hỗ trợ batch rename (multiple files) với preview thay đổi trước khi confirm.
- REQ-208: **Chỉnh sửa nội dung clips**: Người dùng có thể mở file `.jsonl` (clips) và chỉnh sửa nội dung text hoặc metadata trực tiếp (ví dụ: sửa lỗi chính tả, thêm source URL, cập nhật tags). Thay đổi sẽ được lưu vào file tương ứng. Thêm tùy chọn "Edit Content" (right-click trên clip item hay double-click text) → mở editor Markdown với nội dung text → save/cancel.

#### 3.1.4 Tìm kiếm & Index
- REQ-301: Index dữ liệu text (clips/*.jsonl, notes/*.md) bằng DuckDB.  
- REQ-302: Tìm kiếm full-text, fuzzy, sắp xếp theo thời gian giảm dần.  
- REQ-303: Rebuild/incremental index khi có dữ liệu mới hoặc ngày mới.

### 3.2 Yêu cầu phi chức năng (Non-Functional Requirements)

| ID       | Yêu cầu                              | Mô tả / Tiêu chí đo lường                              |
|----------|--------------------------------------|-----------------------------------------------------------------|
| NFR-001  | Hiệu suất – Thời gian phản hồi       | Quick Search < 500ms (với <10.000 file tích lũy).               |
| NFR-002  | Hiệu suất – Dung lượng               | App chạy nền < 150MB RAM (Python overhead).                    |
| NFR-003  | Độ tin cậy                           | Không crash khi clipboard thay đổi liên tục (>100 lần/phút).   |
| NFR-003a | Deduplicate Performance              | Kiểm tra trùng lặp nội dung (exact/similar match) < 100ms, hỗ trợ tối thiểu 10.000 clips trong memory index. |
| NFR-004  | Khả dụng & Auto-start                | Chạy nền 24/7, tự khởi động cùng Windows (tùy chọn). Ứng dụng phải hỗ trợ tùy chọn "Auto-start on Windows Startup" trong settings, khi bật sẽ tự động chạy khi user login vào Windows. |
| NFR-005  | Bảo mật                              | Dữ liệu local, tùy chọn xóa tự động sau 30/90 ngày.             |
| NFR-006  | Khả dụng & Bảo trì                   | Dễ backup (zip folder), dễ migrate (cấu trúc thư mục đơn giản).|
| NFR-007  | Giao diện - Desktop-like             | Modern UI giống phần mềm desktop chuyên nghiệp (PyQt6 dark theme, hỗ trợ light mode). Cửa sổ phải có title bar, minimize/maximize/close buttons, resizable frame, context menu chuẩn Windows. Không sử dụng web view hoặc Electron-based framework. Ngoài ra, hỗ trợ native Windows window style với icon trên taskbar, tray icon ở system tray, và tích hợp context menu (right-click) trên desktop/explorer. |

### 3.3 Yêu cầu giao diện bên ngoài
- Windows API: Clipboard (via pyperclip), Hotkey (via keyboard/pynput), Screenshot (via pyautogui/mss), clipboard image intake tương thích Print Screen và Win+Shift+S.  
- Không tích hợp API bên thứ ba (offline-first).

## 4. Kịch bản sử dụng mẫu (Use Cases)

1. **Khởi động ngày mới**: App tự tạo thư mục 2026-03-06 → thông báo tray icon.  
2. **Copy code từ web**: Ctrl+C → lưu clips_09-30-05.jsonl với content + URL (nếu có).  
3. **Chụp màn hình ý tưởng**: Alt+S hoặc Print Screen/Win+Shift+S → ảnh được tạo → app lưu screen_10-15-22.png.  
4. **Ghi chú nhanh**: Alt+N → viết Markdown → Esc → auto-save vào notes_2026-03-06.md.  
5. **Tìm lại nội dung cũ**: Alt+Space → gõ "async await" → hiển thị kết quả từ 3 ngày trước.
6. **Mở GUI để duyệt dữ liệu**: Alt+Space → chưa nhập gì → thấy danh sách thư mục ngày và file để chọn trực tiếp.
7. **Preview ảnh đã lưu**: Chọn một screenshot hoặc file ảnh trong danh sách/kết quả tìm kiếm → GUI hiển thị preview ảnh và metadata cơ bản ngay trong cửa sổ.
8. **Chỉnh sửa tên file**: Double-click trên file trong danh sách → nhập tên mới → file rename (hoặc right-click → rename). Hỗ trợ rename hàng loạt (bulk rename) với preview trước confirm.
9. **Auto-start app**: User mở Settings → bật tùy chọn "Auto-start on Windows Startup" → app tự khởi động khi Windows khởi động, chạy nền với tray icon.
10. **Lọc trùng lặp nội dung**: User copy đoạn code → lưu clips_10-00-00.jsonl. Sau 2 phút, copy lại cùng đoạn code → app nhận diện "exact duplicate cùng ngày" → bỏ qua, không tạo file mới.
11. **Cảnh báo nội dung gần giống**: User copy "async await in JavaScript" → lưu clip. 30 giây sau copy "async await in Typescript" (khác 3 ký tự) → dialog cảnh báo *"95% giống clip vừa copy. Lưu hay bỏ qua?"* → user chọn "Lưu" → tạo clip mới hoặc "Bỏ qua" → không lưu.
12. **Gộp tự động nội dung tương tự**: Nếu bật mode auto-merge → copy "Python tips" → copy "Python tip" (sai 1 ký tự) trong 5 phút → app tự động gộp, cập nhật timestamp clip cũ, không tạo file mới.
13. **Chỉnh sửa nội dung clip**: User right-click trên clip item → chọn "Edit Content" → text editor mở → user sửa typo hoặc cập nhật thông tin → save → nội dung clip được cập nhật trong file .jsonl.

## 5. Công nghệ đề xuất (Technology Stack)

| Thành phần              | Công nghệ Python                    |
|------------------------|------------------------------------|
| **Language**            | Python 3.10+                       |
| **GUI Framework**       | PyQt6 (native desktop, không Electron/web) |
| **Windows Integration** | winreg (Registry) cho Auto-start, win32com cho OS integration |
| **Search/Index**        | duckdb (duckdb-python)             |
| **Similarity Detection** | difflib (built-in), fuzzywuzzy hoặc rapidfuzz cho similarity matching |
| **Image Processing**    | Pillow (PIL)                       |
| **Hotkey/Clipboard**    | keyboard / pynput / pyperclip      |
| **Screenshot**          | pyautogui hoặc mss + PIL           |
| **Markdown**            | markdown2 hoặc python-markdown     |
| **Dependency Injection**| dependency-injector                |
| **Testing**             | pytest + pytest-mock               |
| **Logging**             | logging (built-in) + colorlog      |
| **Distribution**        | PyInstaller (onedir mode) + NSIS installer (Windows native) |
| **Configuration**       | JSON hoặc configparser             |
| **Data Serialization**  | json (built-in), dataclasses       |

---

## 6. Định nghĩa Từ (Glossary)

- **Clip**: Đơn vị dữ liệu clipboard (text/image) được lưu trữ.
- **Screenshot**: Ảnh chụp màn hình được lưu trữ.
- **Note**: Ghi chú thủ công Markdown.
- **Index**: DuckDB database chứa full-text search data.
- **Global Hotkey**: Phím tắt hệ thống (không cần focus app).
- **Deduplicate**: Loại bỏ dữ liệu trùng lặp trong cửa sổ thời gian hoặc trong cùng ngày.
- **Exact Duplicate**: Nội dung copy giống 100% (byte-by-byte match) với clip trước đó.
- **Similar Match**: Nội dung gần giống (độ tương đồng > 95%, khác 1–2 ký tự hoặc whitespace/formatting).
- **JSONL**: JSON Lines format (một JSON object per line).
- **FTS**: Full-Text Search (tìm kiếm văn bản đầy đủ).
