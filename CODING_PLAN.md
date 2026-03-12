# Kế hoạch Coding cho các tính năng còn lại của DailyClip

Dựa trên phân tích các chức năng đã và chưa hoàn thiện, đây là kế hoạch triển khai chi tiết cho các tính năng còn lại, được chia thành các "Sprint" (chặng) hợp lý.

Mỗi task trong kế hoạch đều bao gồm:
*   **Mô tả**: Tính năng hoạt động như thế nào từ góc nhìn người dùng.
*   **Yêu cầu kỹ thuật**: Cần làm gì trong code, thư viện nào cần dùng.
*   **Chiến lược Test**: Cách để đảm bảo tính năng hoạt động đúng.
*   **Prompt cho AI**: Câu lệnh bạn có thể copy-paste để yêu cầu AI viết code.

---

### **Sprint 1: Nâng cấp Lõi & Hoàn thiện UI Cơ bản**

**Mục tiêu:** Cải thiện các tính năng đã có và bổ sung các phần còn thiếu quan trọng nhất để sản phẩm trở nên hữu dụng hơn.

#### **Task 1.1: Chụp ảnh màn hình theo vùng chọn (Region Capture)**

*   **Mô tả**: Người dùng nhấn phím tắt (ví dụ: `Alt+S`), màn hình sẽ mờ đi, cho phép họ kéo chuột để vẽ một hình chữ nhật. Vùng bên trong hình chữ nhật sẽ được chụp lại, lưu thành file PNG và được index.
*   **Yêu cầu kỹ thuật**:
    1.  Tạo một cửa sổ PyQt6 mới: `ScreenCaptureOverlay`, trong suốt, không viền, toàn màn hình.
    2.  Sử dụng `QRubberBand` để vẽ vùng chọn dựa trên các sự kiện `mousePressEvent`, `mouseMoveEvent`, `mouseReleaseEvent`.
    3.  Khi người dùng nhả chuột, lấy tọa độ của vùng đã chọn.
    4.  Dùng thư viện `mss` để chụp lại màn hình theo tọa độ đó.
    5.  Dữ liệu ảnh (bytes) được gửi đến `IStorageService.save_screenshot` đã có sẵn.
    6.  Cập nhật `ScreenCaptureServiceImpl` để hiển thị overlay này.
*   **Chiến lược Test**:
    *   **Test tay (Manual)**: Nhấn hotkey, màn hình mờ đi. Kéo chuột vẽ vùng chọn. Kiểm tra file PNG mới được tạo trong thư mục ngày hiện tại và nội dung ảnh khớp với vùng đã chọn.
    *   **Unit Test**: Mock các thành phần của `mss` và `PyQt6`. Test logic tính toán tọa độ trong `ScreenCaptureOverlay`. Test rằng `save_screenshot` được gọi với dữ liệu ảnh (đã mock).
*   **Prompt cho AI**:
    ```text
    Hãy implement tính năng chụp ảnh màn hình theo vùng chọn cho DailyClip.

    **File cần tạo/sửa:** `presentation/windows/screen_capture_overlay.py` và `infrastructure/screenshot_capture.py`.

    **Yêu cầu:**
    1.  Tạo class `ScreenCaptureOverlay` kế thừa từ `QMainWindow` (PyQt6).
    2.  Window phải trong suốt (`Qt.WA_TranslucentBackground`), không viền, và toàn màn hình.
    3.  Sử dụng `QRubberBand` để cho phép người dùng kéo chuột chọn một vùng.
    4.  Khi chuột được nhả ra, lấy tọa độ của vùng chọn.
    5.  Dùng thư viện `mss` để chụp lại nội dung màn hình trong vùng tọa độ đó.
    6.  Phát ra một signal `region_captured(image_bytes)` chứa dữ liệu ảnh đã chụp.
    7.  Cập nhật `ScreenCaptureServiceImpl` để khởi tạo và hiển thị overlay này, sau đó kết nối signal `region_captured` để gọi service lưu trữ.
    ```

#### **Task 1.2: Nâng cấp Giao diện Ghi chú nhanh (Quick Note)**

*   **Mô tả**: Hoàn thiện cửa sổ ghi chú nhanh để hỗ trợ đầy đủ Markdown với tính năng xem trước (preview) theo thời gian thực.
*   **Yêu cầu kỹ thuật**:
    1.  Sửa `QuickNoteWindow` để có layout chia đôi: bên trái là `QTextEdit` để gõ Markdown, bên phải là `QTextBrowser` để hiển thị preview.
    2.  Sử dụng thư viện `markdown` để chuyển đổi text từ `QTextEdit` sang HTML.
    3.  Sự kiện `textChanged` của `QTextEdit` sẽ trigger việc cập nhật preview (có thể dùng debounce để tối ưu).
    4.  HTML được tạo ra sẽ được set cho `QTextBrowser`.
    5.  Thêm thanh công cụ (toolbar) với các nút cơ bản: Bold, Italic, Link... để chèn cú pháp Markdown vào `QTextEdit`.
*   **Chiến lược Test**:
    *   **Test tay**: Mở cửa sổ Quick Note. Gõ cú pháp Markdown (vd: `# Header`, `**bold**`) và kiểm tra xem preview bên phải có hiển thị đúng không. Dùng các nút trên toolbar và kiểm tra.
    *   **Unit Test**: Test hàm chuyển đổi Markdown sang HTML. Test logic của các nút trên toolbar (ví dụ: khi chọn text và nhấn "Bold", text có được bao bởi `**` hay không).
*   **Prompt cho AI**:
    ```text
    Hãy nâng cấp `QuickNoteWindow` trong `presentation/windows/quick_note.py` để hỗ trợ soạn thảo Markdown với live preview.

    **Yêu cầu:**
    1.  Sử dụng `QSplitter` để chia cửa sổ thành 2 phần: `QTextEdit` (bên trái) và `QTextBrowser` (bên phải).
    2.  Sử dụng thư viện `markdown` của Python.
    3.  Khi người dùng gõ vào `QTextEdit`, nội dung sẽ được chuyển sang HTML và hiển thị ở `QTextBrowser`. Áp dụng debounce 300ms cho việc cập nhật.
    4.  Thêm một `QToolBar` với các action: Bold (Ctrl+B), Italic (Ctrl+I), và Chèn Link. Các action này sẽ chèn cú pháp Markdown tương ứng vào `QTextEdit`.
    5.  Áp dụng CSS cơ bản cho `QTextBrowser` để có giao diện dark mode đẹp hơn.
    ```

#### **Task 1.3: Xây dựng Giao diện Cài đặt (Settings UI)**

*   **Mô tả**: Tạo một cửa sổ cài đặt nơi người dùng có thể tùy chỉnh các thiết lập của ứng dụng, bắt đầu với việc tùy chỉnh phím tắt.
*   **Yêu cầu kỹ thuật**:
    1.  Tạo `SettingsWindow` trong `presentation/windows/`.
    2.  Sử dụng `QTabWidget` để phân loại cài đặt (ví dụ: "Hotkeys", "Storage").
    3.  **Tab Hotkeys**: Hiển thị các phím tắt hiện tại. Sử dụng widget `QKeySequenceEdit` để người dùng có thể ghi lại tổ hợp phím mới.
    4.  Mở rộng `AppConfig` để lưu và tải các cài đặt này từ file `config.ini` hoặc `settings.json`.
    5.  Khi người dùng lưu, ghi giá trị mới vào file config và thông báo cho các service liên quan (ví dụ: `HotkeyService` cần đăng ký lại phím tắt mới).
*   **Chiến lược Test**:
    *   **Test tay**: Mở cửa sổ cài đặt. Thay đổi một phím tắt, lưu lại, và kiểm tra xem phím tắt mới có hoạt động không.
    *   **Unit Test**: Test logic lưu/tải của `AppConfig`. Test `SettingsWindow` đọc và ghi chính xác vào một object `AppConfig` đã được mock.
*   **Prompt cho AI**:
    ```text
    Hãy tạo một cửa sổ Cài đặt (Settings) cho DailyClip bằng PyQt6.

    **File cần tạo:** `presentation/windows/settings_window.py`.

    **Yêu cầu:**
    1.  Tạo class `SettingsWindow` kế thừa từ `QDialog`.
    2.  Sử dụng `QFormLayout` để hiển thị các cài đặt.
    3.  Mục cài đặt đầu tiên là "Hotkeys". Với mỗi hotkey (Quick Search, New Note), tạo một `QLabel` và một `QKeySequenceEdit`.
    4.  Load giá trị hotkey hiện tại từ `AppConfig` và hiển thị lên `QKeySequenceEdit`.
    5.  Thêm nút "Save" và "Cancel". Khi "Save" được nhấn, cập nhật `AppConfig` với giá trị mới và đóng dialog.
    6.  Thêm một mục "Settings" trong menu của System Tray để mở cửa sổ này.
    ```

---

### **Sprint 2: Tính năng Thông minh & Giao diện Hợp nhất**

**Mục tiêu:** Tích hợp các cửa sổ rời rạc thành một trải nghiệm thống nhất và bổ sung các tính năng thông minh để tăng giá trị cho người dùng.

#### **Task 2.1: Hợp nhất Giao diện (Unified Window)**

*   **Mô tả**: Thay vì có nhiều cửa sổ riêng lẻ (Search, Note), tạo một cửa sổ chính duy nhất có thể chuyển đổi giữa các chế độ khác nhau, tương tự như Raycast hay Alfred.
*   **Yêu cầu kỹ thuật**:
    1.  Thiết kế lại `QuickSearchWindow` thành `UnifiedMainWindow`.
    2.  Thanh tìm kiếm sẽ là trung tâm. Khi người dùng gõ, nó sẽ tìm kiếm clips như hiện tại.
    3.  Thêm các "lệnh" (commands). Ví dụ, gõ "new note" + Enter sẽ chuyển view sang giao diện ghi chú ngay trong cửa sổ đó, thay vì mở cửa sổ mới.
    4.  Sử dụng `QStackedWidget` để quản lý các view khác nhau (view tìm kiếm, view ghi chú, view cài đặt...).
    5.  Logic xử lý lệnh sẽ phân tích input của người dùng để quyết định hiển thị view nào trong `QStackedWidget`.
*   **Chiến lược Test**:
    *   **Test tay**: Mở cửa sổ. Gõ tìm kiếm và xem kết quả. Gõ "new note" và xem giao diện có chuyển sang chế độ ghi chú không.
    *   **Unit Test**: Test bộ phân tích lệnh (command parser). Ví dụ: `parse("new note")` trả về `Command.NEW_NOTE`. Test logic chuyển đổi view của `QStackedWidget`.
*   **Prompt cho AI**:
    ```text
    Hãy tái cấu trúc `QuickSearchWindow` thành một `UnifiedMainWindow` có thể chuyển đổi chế độ.

    **File cần sửa:** `presentation/windows/quick_search.py` (đổi tên thành `unified_window.py`).

    **Yêu cầu:**
    1.  Sử dụng `QStackedWidget` làm widget trung tâm.
    2.  Tầng đầu tiên của `QStackedWidget` là layout tìm kiếm hiện tại (thanh search + danh sách kết quả).
    3.  Tạo một `NoteWidget` mới để chứa giao diện soạn thảo note. Thêm widget này vào tầng thứ hai của `QStackedWidget`.
    4.  Trong `UnifiedMainWindow`, khi người dùng gõ "new note" vào thanh tìm kiếm và nhấn Enter, hãy chuyển `QStackedWidget` sang `NoteWidget`.
    5.  Thêm một nút "Back" hoặc xử lý phím `Esc` để quay lại view tìm kiếm từ view ghi chú.
    ```

#### **Task 2.2: Nhận diện Loại Nội dung & Nhóm Thông minh**

*   **Mô tả**: Khi một clip được lưu, ứng dụng tự động nhận diện loại nội dung (URL, code snippet, file path) và lấy thông tin về ứng dụng nguồn (VSCode, Chrome...).
*   **Yêu cầu kỹ thuật**:
    1.  **Nhận diện nội dung**: Trong `ClipboardMonitorService`, sau khi lấy nội dung, dùng regex để kiểm tra:
        *   Nếu khớp `http(s)://...`, gán `content_type = 'url'`.
        *   Nếu chứa các ký tự `{`, `}`, `;`, `def`, `class`, gán `content_type = 'code'`.
        *   Thêm trường `content_type` vào `ClipItem` và schema DuckDB.
    2.  **Lấy ứng dụng nguồn**:
        *   Sử dụng thư viện `pywin32` (trên Windows) để lấy `HWND` của cửa sổ đang active tại thời điểm copy.
        *   Từ `HWND`, lấy tên tiến trình (process name, ví dụ: `chrome.exe`, `Code.exe`).
        *   Thêm trường `source_app` vào `ClipItem` và schema DuckDB.
*   **Chiến lược Test**:
    *   **Unit Test**:
        *   Test hàm nhận diện nội dung với các chuỗi đầu vào khác nhau (URL, code, text thường) và assert `content_type` đúng.
        *   Mock hàm lấy cửa sổ active của `pywin32` và test rằng `source_app` được gán đúng.
*   **Prompt cho AI**:
    ```text
    Hãy nâng cấp `ClipboardMonitorService` để tự động nhận diện loại nội dung và ứng dụng nguồn.

    **File cần sửa:** `infrastructure/clipboard_monitor.py` và `core/entities.py`.

    **Yêu cầu:**
    1.  Thêm các trường `content_type: str` và `source_app: str` vào dataclass `ClipItem`.
    2.  Trong `ClipboardMonitorService`, khi xử lý một clip mới:
        a. Dùng regex để xác định `content_type` là 'url', 'code', hay 'text'.
        b. **Trên Windows**, dùng thư viện `win32gui` và `win32process` để lấy tên tiến trình của cửa sổ đang active (`GetForegroundWindow`). Gán tên tiến trình (vd: "chrome.exe") cho `source_app`.
    3.  Bọc phần lấy ứng dụng nguồn trong `try-except` để không làm crash ứng dụng nếu có lỗi.
    4.  Cập nhật logic lưu trữ và indexing để xử lý các trường mới này.
    ```

---

### **Sprint 3: Tính năng Chuyên sâu & Độ tin cậy**

**Mục tiêu:** Bổ sung các tính năng cho người dùng chuyên nghiệp, tăng cường bảo mật và độ tin cậy của ứng dụng.

#### **Task 3.1: Mã hóa Dữ liệu & Khóa Ứng dụng**

*   **Mô tả**: Cung cấp tùy chọn mã hóa toàn bộ dữ liệu người dùng trên đĩa và yêu cầu mật khẩu (hoặc Windows Hello) để mở khóa ứng dụng.
*   **Yêu cầu kỹ thuật**:
    1.  **Mã hóa file**: Tích hợp thư viện `cryptography`.
    2.  Khi lưu file (JSONL, PNG), mã hóa nội dung bằng Fernet (AES-128) trước khi ghi xuống đĩa.
    3.  Khi đọc file, giải mã nội dung.
    4.  **Quản lý khóa**: Tạo một khóa mã hóa chính cho người dùng, lưu nó an toàn bằng `Windows Credential Manager`.
    5.  **Khóa ứng dụng**: Trước khi cửa sổ chính hiện ra, hiển thị một dialog yêu cầu mật khẩu. Mật khẩu này được dùng để truy cập khóa mã hóa trong Credential Manager.
*   **Chiến lược Test**:
    *   **Unit Test**: Test các hàm mã hóa và giải mã. Mock Credential Manager để test logic lưu/lấy khóa.
    *   **Test tay**: Bật tính năng mã hóa. Thoát và mở lại ứng dụng, kiểm tra xem có dialog yêu cầu mật khẩu không. Sau khi nhập đúng, kiểm tra xem có tìm kiếm được dữ liệu cũ không. Kiểm tra các file trên đĩa và xác nhận chúng không thể đọc được bằng text editor thường.
*   **Prompt cho AI**:
    ```text
    Hãy implement tính năng mã hóa file cho DailyClip.

    **File cần sửa:** `infrastructure/file_storage.py` và tạo `infrastructure/security.py`.

    **Yêu cầu:**
    1.  Tạo một `EncryptionService` sử dụng thư viện `cryptography.fernet`.
    2.  Service này có phương thức `encrypt(data: bytes)` và `decrypt(token: bytes)`.
    3.  Khóa Fernet phải được quản lý an toàn (ví dụ: lưu trong Windows Credential Manager, hoặc đơn giản là một file được bảo vệ).
    4.  Trong `FileStorageService`, trước khi ghi dữ liệu vào file (`aiofiles.f.write`), hãy gọi `encryption_service.encrypt()`.
    5.  Khi đọc dữ liệu, hãy gọi `encryption_service.decrypt()`.
    6.  Thêm một tùy chọn trong Settings UI để bật/tắt mã hóa. Khi bật, cần có quy trình mã hóa toàn bộ dữ liệu hiện có.
    ```

#### **Task 3.2: Sao lưu & Phục hồi (Backup & Restore)**

*   **Mô tả**: Cung cấp chức năng cho phép người dùng xuất toàn bộ dữ liệu ra một file zip duy nhất và nhập lại từ file zip đó.
*   **Yêu cầu kỹ thuật**:
    1.  **Backup**:
        *   Tạo một hàm `backup_data(output_path: str)`.
        *   Hàm này sẽ dùng thư viện `zipfile` để nén toàn bộ thư mục data (`%APPDATA%/DailyClip/data`) vào file zip tại `output_path`.
    2.  **Restore**:
        *   Tạo một hàm `restore_data(zip_path: str)`.
        *   Hàm này cảnh báo người dùng rằng dữ liệu hiện tại sẽ bị ghi đè.
        *   Sau khi xác nhận, xóa thư mục data hiện tại và giải nén file zip vào vị trí đó.
        *   Sau khi restore, trigger việc rebuild lại toàn bộ index tìm kiếm.
    3.  Thêm các nút "Backup..." và "Restore..." vào Settings UI.
*   **Chiến lược Test**:
    *   **Test tay**: Tạo một số dữ liệu. Dùng tính năng Backup. Xóa thư mục data. Dùng tính năng Restore. Kiểm tra xem dữ liệu có quay trở lại và tìm kiếm được không.
*   **Prompt cho AI**:
    ```text
    Hãy thêm chức năng Backup và Restore dữ liệu cho DailyClip.

    **File cần tạo/sửa:** `infrastructure/backup_service.py` và `presentation/windows/settings_window.py`.

    **Yêu cầu:**
    1.  Tạo `BackupService` với hai phương thức async: `create_backup(target_zip_path: Path)` và `restore_from_backup(source_zip_path: Path)`.
    2.  `create_backup` sẽ nén toàn bộ thư mục dữ liệu của ứng dụng vào một file zip.
    3.  `restore_from_backup` sẽ xóa thư mục dữ liệu hiện tại và giải nén file zip vào. Cần có cảnh báo cho người dùng.
    4.  Thêm một tab "Backup/Restore" vào `SettingsWindow`.
    5.  Tab này có hai nút: "Backup to..." (mở `QFileDialog` để chọn nơi lưu file zip) và "Restore from..." (mở `QFileDialog` để chọn file zip).
    6.  Hiển thị thanh tiến trình trong quá trình backup/restore.
    ```
