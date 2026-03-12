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
- Chụp màn hình bằng hotkey nội bộ hoặc nhận ảnh từ clipboard hệ điều hành (Print Screen, Win+Shift+S).
- **Giao diện hợp nhất (Unified Window)**: Cung cấp một cửa sổ chính duy nhất, được gọi bằng phím tắt, tích hợp các chức năng:
  - **Tìm kiếm nổi (Spotlight-style)**: Tìm kiếm toàn cục trên tất cả dữ liệu.
  - **Duyệt file và xem trước**: Duyệt dữ liệu theo ngày, xem trước nội dung (text, ảnh) và chỉnh sửa trực tiếp ngay trong cửa sổ.
  - **Ghi chú nhanh**: Soạn thảo ghi chú Markdown tích hợp.
  - **Xem ảnh dạng lưới (Gallery)**.
- **Xử lý trùng lặp thông minh (Zero-interruption)**: Thực hiện cập nhật im lặng (silent update) cho nội dung trùng lặp hoàn toàn và quản lý phiên bản cho nội dung gần giống.
- **Tự động nhóm các clip trong ngày** dựa trên ứng dụng nguồn (ví dụ: các clip từ VSCode, Chrome).
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
- REQ-103a: **Điều kiện tạo file khi copy (File Creation Conditions)**: Ứng dụng chỉ tạo file clip/image mới khi nội dung clipboard thay đổi và thỏa mãn: (1) Nội dung có độ dài tối thiểu (text ≥ 3 ký tự), (2) Là ảnh có độ phân giải hợp lệ (width × height ≥ 64×64 pixels), hoặc (3) Là dữ liệu có cấu trúc nhận diện được (URL, code, mã định dạng). Bỏ qua clipboard trống hoặc chứa dữ liệu không hợp lệ. (4) Nếu copy liên tục từ cùng một ứng dụng trong vài giây → có thể bỏ qua hoặc gộp.
- REQ-104: **Xử lý trùng lặp và phiên bản (Zero-interruption)**:
  - **REQ-104a (Cập nhật - Silent Update)**: Khi người dùng copy nội dung **trùng khớp 100%** (exact match) với một clip đã tồn tại, hệ thống phải thực hiện **Cập nhật im lặng (Silent Update)**: tự động cập nhật timestamp của clip cũ đó và đưa nó lên đầu danh sách. Tuyệt đối không hiển thị hộp thoại xác nhận hay tạo bản sao mới.
  - **REQ-104b**: Bỏ qua nếu nội dung **giống hoàn toàn** với clip copy trước đó trong vòng **10 giây gần nhất** để tránh lưu các thao tác copy lặp lại nhanh.
  - **REQ-104c (Cập nhật - Version History)**: Nếu nội dung **gần giống** (ví dụ: sửa một vài dòng code rồi copy lại), hệ thống sẽ lưu thành một clip mới nhưng tự động liên kết nó như một **"phiên bản mới"** của clip gốc.
    - **Giới hạn**: Lưu tối đa 10 phiên bản gần nhất cho một nhóm nội dung để tối ưu lưu trữ. Các phiên bản cũ hơn sẽ tự động bị loại bỏ hoặc gộp.
    - **Thao tác**: Người dùng có thể xem lịch sử, so sánh sự khác biệt ("View Diff") và thực hiện **"Revert" (Khôi phục)** để đưa một phiên bản cũ lên làm phiên bản hiện hành (main clip).
- REQ-105: Ứng dụng hỗ trợ phím tắt chụp màn hình nội bộ (mặc định Alt+S, có thể cấu hình): hỗ trợ region / fullscreen, lưu tự động vào images/.
- REQ-106: Nếu ảnh chụp được tạo bởi Print Screen, Snipping Tool hoặc Win+Shift+S và xuất hiện trên clipboard, ứng dụng phải tự nhận diện và lưu ảnh đó vào images/ như screenshot hợp lệ.

#### 3.1.3 Giao diện & Tương tác người dùng
- REQ-201 (Cập nhật - Unified Hotkeys): Global hotkey (system-wide):
  - `Alt+Space` → Mở/đóng cửa sổ chính (Unified Main Window) ở chế độ tìm kiếm nổi (Spotlight-style).
  - Alt+S (mặc định, có thể cấu hình) → chụp màn hình.  
  (Chức năng ghi chú nhanh được tích hợp vào cửa sổ chính, không cần hotkey riêng).
- REQ-202 (Cập nhật - Unified Main Window & Spotlight UI):
  - Hệ thống phải cung cấp một **cửa sổ chính hợp nhất (Unified Main Window)**, thay thế cho các cửa sổ riêng lẻ.
  - Khi được gọi bằng hotkey, cửa sổ ban đầu xuất hiện dưới dạng một **thanh tìm kiếm nổi tối giản (Spotlight-style)** ở giữa màn hình, hiển thị kết quả tìm kiếm realtime bên dưới.
  - Khi chọn một item, cửa sổ sẽ mở rộng để hiển thị giao diện đầy đủ, bao gồm danh sách kết quả và một **panel preview/chỉnh sửa** bên cạnh.
  - Cửa sổ phải hỗ trợ chế độ "luôn ở trên" (always on top) có thể bật/tắt.
  - **Cơ chế đóng (UX Dismissal)**: Nhấn `Esc` sẽ đóng cửa sổ hoặc quay lại trạng thái thanh tìm kiếm nhỏ (nếu đang ở chế độ xem chi tiết) để tối ưu hóa thao tác.
  - **Luồng tương tác (Flow Diagram)**:
    ```mermaid
    graph TD
        Start((Alt+Space)) --> SearchBar{Floating Bar}
        SearchBar -- User types query --> ResultsList[Live Results]
        SearchBar -- Empty query --> BrowseMode[Browse by Date]
        
        ResultsList -- Select Item --> DetailView[Unified Window Expanded]
        BrowseMode -- Select Item --> DetailView
        
        DetailView --> PreviewPane[Preview & Inline Edit]
        
        PreviewPane -- Ctrl+S --> Save[Save & Update Index]
        PreviewPane -- Esc --> SearchBar
        
        SearchBar -- Esc --> Close((Hidden/Tray))
    ```

- REQ-203 (Cập nhật - Chế độ xem linh hoạt):
  - Cửa sổ chính phải cho phép chuyển đổi linh hoạt giữa các chế độ xem:
    - **Search Mode**: Tìm kiếm toàn cục.
    - **Browse Mode**: Khi ô tìm kiếm trống, tự động hiển thị danh sách duyệt file/thư mục theo ngày.
    - **Gallery Mode**: Hiển thị các mục hình ảnh dưới dạng lưới (grid view).
    - **Note Mode**: Cung cấp giao diện soạn thảo Markdown tích hợp, auto-save khi thay đổi.
- REQ-204 (Cập nhật - Tích hợp Preview và Chỉnh sửa nội tuyến):
  - Panel preview/chỉnh sửa phải hiển thị nội dung chi tiết của item đang được chọn.
  - **Đối với clip/note (text)**: Cho phép **chỉnh sửa trực tiếp (inline edit)** ngay trong panel. Hỗ trợ các tính năng soạn thảo cơ bản như Undo/Redo, và lưu bằng `Ctrl+S`. Khi lưu, hệ thống có thể đề xuất tạo phiên bản mới hoặc ghi đè.
  - **Xử lý xung đột khi chỉnh sửa (Edit Conflict)**: Trong trường hợp người dùng đang chỉnh sửa một Clip, nếu hệ thống phát hiện trùng lặp mới (Silent Update) cho Clip đó, hệ thống phải **ưu tiên nội dung người dùng đang soạn thảo**. Quá trình cập nhật ngầm không được làm mới giao diện editor gây mất dữ liệu chưa lưu.
  - **Đối với ảnh**: Hiển thị ảnh preview và metadata (kích thước, thời gian).
- REQ-205 (Cập nhật - Hành động nhanh từ Preview):
  - Panel preview phải tích hợp các nút hành động nhanh, bao gồm: Copy lại nội dung, Mở file bằng ứng dụng mặc định, Đánh dấu sao (Favorite), Xóa file, Chỉnh sửa tên file.
- REQ-206: **Nhóm clip thông minh (Smart Grouping)**: Hệ thống hỗ trợ nhóm các clip trong danh sách duyệt dựa trên:
  - **Nguồn ứng dụng**: (Mặc định) Group theo Window Title/Process Name (VD: "Visual Studio Code", "Chrome").
  - **Chủ đề/Tags**: (Tùy chọn) Group theo các thẻ (tags) người dùng tự gán hoặc tự động phát hiện (VD: "Code Snippets", "Images", "Links").

#### 3.1.4 Tìm kiếm & Index
- REQ-301: Index dữ liệu text (clips/*.jsonl, notes/*.md) bằng DuckDB.  
- REQ-302: Tìm kiếm full-text, fuzzy, sắp xếp theo thời gian giảm dần.  
- REQ-303: Rebuild/incremental index khi có dữ liệu mới hoặc ngày mới.

#### 3.1.5 Bảo mật & An toàn dữ liệu
- REQ-401: **Khóa ứng dụng (App Lock)**: Hỗ trợ khóa truy cập giao diện chính bằng mật khẩu hoặc Windows Hello (nếu phần cứng hỗ trợ). Khi bị khóa, ứng dụng vẫn chạy ngầm để thu thập clipboard nhưng yêu cầu xác thực khi nhấn `Alt+Space` để xem dữ liệu.
- REQ-402: **Mã hóa dữ liệu (Encryption - Optional)**: Cung cấp tùy chọn mã hóa file nội dung (AES-256) trên đĩa. Lưu ý: Tính năng này có thể làm giảm nhẹ hiệu suất tìm kiếm và preview.

### 3.2 Yêu cầu phi chức năng (Non-Functional Requirements)

| ID       | Yêu cầu                              | Mô tả / Tiêu chí đo lường                              |
|----------|--------------------------------------|-----------------------------------------------------------------|
| NFR-001  | Hiệu suất – Thời gian phản hồi       | Quick Search < 500ms (với <10.000 file). Đảm bảo < 1000ms ngay cả khi dữ liệu đạt **100.000 clips**. |
| NFR-002  | Hiệu suất – Dung lượng               | App chạy nền < 150MB RAM (Python overhead).                    |
| NFR-003  | Độ tin cậy                           | Không crash khi clipboard thay đổi liên tục (>100 lần/phút).   |
| NFR-003a | Deduplicate Performance              | Kiểm tra trùng lặp nội dung (exact/similar match) < 100ms, hỗ trợ tối thiểu 10.000 clips trong memory index. |
| NFR-004  | Khả dụng & Auto-start                | Chạy nền 24/7, tự khởi động cùng Windows (tùy chọn). Ứng dụng phải hỗ trợ tùy chọn "Auto-start on Windows Startup" trong settings, khi bật sẽ tự động chạy khi user login vào Windows. |
| NFR-005  | Bảo mật                              | Dữ liệu local, tùy chọn xóa tự động sau 30/90 ngày.             |
| NFR-006  | Khả dụng & Bảo trì                   | Dễ backup (zip folder), dễ migrate (cấu trúc thư mục đơn giản).|
| NFR-007  | Giao diện - Desktop-like             | Modern UI giống phần mềm desktop chuyên nghiệp (PyQt6 dark theme, hỗ trợ light mode). Cửa sổ phải có title bar, minimize/maximize/close buttons, resizable frame, context menu chuẩn Windows. Không sử dụng web view hoặc Electron-based framework. Ngoài ra, hỗ trợ native Windows window style với icon trên taskbar, tray icon ở system tray, và tích hợp context menu (right-click) trên desktop/explorer. |
| NFR-008  | Khả năng phục hồi (Resiliency)       | Cơ chế **Crash Recovery**: Dữ liệu clipboard queue và index chưa kịp ghi đĩa phải được khôi phục hoặc rebuild tự động lần khởi động kế tiếp. Ghi chú (Notes) phải có cơ chế temp file để không mất dữ liệu đang gõ dở nếu mất điện/crash. |

### 3.3 Yêu cầu giao diện bên ngoài
- Windows API: Clipboard (via pyperclip), Hotkey (via keyboard/pynput), Screenshot (via pyautogui/mss), clipboard image intake tương thích Print Screen và Win+Shift+S.  
- Không tích hợp API bên thứ ba (offline-first).

## 4. Kịch bản sử dụng mẫu (Use Cases)

1. **Khởi động ngày mới**: App tự tạo thư mục 2026-03-06 → thông báo tray icon.  
2. **Copy code từ web**: Ctrl+C → lưu clips_09-30-05.jsonl với content + URL (nếu có).  
3. **Chụp màn hình ý tưởng**: Alt+S hoặc Print Screen/Win+Shift+S → ảnh được tạo → app lưu screen_10-15-22.png.  
4. **Tìm kiếm và xem chi tiết (Unified Flow)**: User nhấn `Alt+Space`, thanh tìm kiếm nổi hiện ra. User gõ "async await". Danh sách kết quả hiện ngay bên dưới. User dùng phím mũi tên để chọn một clip code. Cửa sổ tự động mở rộng, hiển thị danh sách kết quả bên trái và nội dung đầy đủ của clip code trong panel preview bên phải.
5. **Chỉnh sửa nhanh (Inline Edit)**: Trong panel preview, user phát hiện một lỗi chính tả trong clip. User click trực tiếp vào vùng văn bản, sửa lỗi, rồi nhấn `Ctrl+S` để lưu lại. Thao tác hoàn tất mà không cần rời khỏi cửa sổ chính.
6. **Ghi chú nhanh (Integrated)**: User nhấn `Alt+Space`, sau đó chuyển sang chế độ "Note". Giao diện soạn thảo Markdown hiện ra ngay trong cửa sổ chính. User viết ghi chú, và nó sẽ được tự động lưu.
7. **Hành động nhanh với ảnh**: User tìm thấy một ảnh chụp màn hình. Trong panel preview, user bấm nút "Copy" để sao chép lại ảnh vào clipboard, hoặc bấm "Xóa" để loại bỏ file.
8. **Xử lý copy trùng lặp (Im lặng)**: User đang viết code và ấn Ctrl+C một đoạn hàm hai lần liên tiếp theo thói quen. Ứng dụng phát hiện trùng lặp hoàn toàn. Hệ thống chỉ cập nhật thời gian của clip đó thành hiện tại và đưa nó lên đầu danh sách. User không hề bị làm phiền. Khi mở cửa sổ chính, đoạn code đó vẫn nằm ngay trên cùng.
9. **Quản lý phiên bản cho nội dung gần giống**: User copy "async await in JavaScript" → lưu clip. 30 giây sau copy "async await in Typescript" (sửa đổi nhỏ) → ứng dụng lưu clip mới nhưng hiển thị nó như một "phiên bản 2" của clip gốc. User có thể bấm "View Diff" để xem sự khác biệt.
10. **Gộp clip tự động theo nguồn**: User dành 30 phút đọc tài liệu trên Chrome và copy 5 đoạn text khác nhau. Khi mở ứng dụng, tại mục hôm nay, có một nhóm tên là "Google Chrome (5 clips)". User bấm mở rộng để xem nhanh cả 5 đoạn text này mà không bị lẫn lộn với các clip copy từ Slack hay Word.
11. **Auto-start app**: User mở Settings → bật tùy chọn "Auto-start on Windows Startup" → app tự động khởi động khi Windows khởi động, chạy nền với tray icon.
12. **Xử lý xung đột khi đang sửa**: User đang mở một đoạn code cũ để thêm ghi chú. Trong lúc đó, User vô tình copy lại chính đoạn code đó từ IDE. Hệ thống thực hiện "Silent Update" (cập nhật timestamp) cho clip trong database, nhưng giao diện chỉnh sửa của User vẫn giữ nguyên trạng thái đang gõ, không bị refresh hay mất dữ liệu. User lưu xong mới cập nhật lại danh sách.

## 5. Công nghệ đề xuất (Technology Stack)

| Thành phần              | Công nghệ Python                    |
|------------------------|------------------------------------|
| **Language**            | Python 3.10+                       |
| **GUI Framework**       | PyQt6 (native desktop, không Electron/web). Hỗ trợ tùy chỉnh UI (frameless, topmost) cho trải nghiệm giống Spotlight. |
| **Windows Integration** | `winreg` (Registry) cho Auto-start, `pygetwindow` hoặc `psutil` để lấy metadata ứng dụng nguồn. |
| **Search/Index**        | duckdb (duckdb-python)             |
| **Similarity & Diff**   | `difflib` (built-in) để phát hiện nội dung gần giống và hiển thị khác biệt (diff view). |
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
