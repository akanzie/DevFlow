# Tài liệu Đặc tả Yêu cầu Phần mềm (SRS)  
**Tên phần mềm:** DailyClip – Công cụ tự động hóa ghi chú và lưu trữ dữ liệu cá nhân  
**Phiên bản:** 1.0 (Sơ bộ)  
**Ngày soạn thảo:** 06/03/2026  
**Tác giả:** Kiệt (với hỗ trợ tinh chỉnh)  

## 1. Giới thiệu

### 1.1 Mục đích
Tài liệu này mô tả các yêu cầu chức năng và phi chức năng của phần mềm **DailyClip** – một công cụ hỗ trợ năng suất cá nhân (productivity tool) chạy nền trên Windows, tự động thu thập, phân loại và lưu trữ dữ liệu từ clipboard, ảnh chụp màn hình, cùng với giao diện ghi chú nhanh và tìm kiếm toàn cục.

Mục tiêu chính: Giảm thiểu thao tác thủ công khi lưu ý tưởng, code snippet, hình ảnh, giúp người dùng truy xuất thông tin cực nhanh mà không phụ thuộc vào đám mây hoặc công cụ nặng.

### 1.2 Phạm vi sản phẩm
- **Trong phạm vi**:  
  - Tự động giám sát và lưu clipboard (text, image).  
  - Chụp màn hình nhanh bằng phím tắt.  
  - Ghi chú nhanh hỗ trợ Markdown với auto-save.  
  - Tìm kiếm toàn cục (global search) trên dữ liệu đã lưu.  
  - Xem trước ảnh theo ngày (gallery view).  
  - Chạy nền với system tray icon.

- **Ngoài phạm vi**:  
  - Đồng bộ đám mây (có thể mở rộng sau).  
  - Hỗ trợ đa nền tảng (chỉ Windows native).  
  - AI phân loại/tóm tắt nội dung (phiên bản sau).

### 1.3 Đối tượng và mức độ đọc hiểu
- Người dùng cuối (end-user): Cá nhân cần tăng năng suất (developer, designer, researcher).  
- Nhà phát triển: Đội ngũ implement và bảo trì.  
- Tester/QA: Kiểm tra tính năng và hiệu suất.

### 1.4 Định nghĩa, viết tắt và thuật ngữ
- **Clipboard**: Bộ nhớ tạm thời của Windows khi copy (Ctrl+C).  
- **JSONL**: JSON Lines – mỗi dòng là một object JSON độc lập.  
- **Global hotkey**: Phím tắt hoạt động toàn hệ thống.  
- **DuckDB**: Database columnar nhẹ, tối ưu full-text search.

## 2. Mô tả tổng quát

### 2.1 Quan điểm sản phẩm
DailyClip là sự kết hợp giữa clipboard manager (như Ditto), screenshot tool (như ShareX), quick note (như Notepad++ floating), và local search engine (như Everything/Obsidian local search), nhưng tự động hóa cao hơn và tập trung vào tổ chức theo ngày.

### 2.2 Chức năng sản phẩm
- Tự động tạo thư mục theo ngày khi khởi động hoặc chuyển ngày.  
- Lưu clipboard thay đổi (text → JSONL, image → PNG).  
- Chụp màn hình vùng/toàn màn hình/active window.  
- Ghi chú nhanh Markdown với auto-save.  
- Tìm kiếm nhanh toàn cục (text trong clips/notes).  
- Xem lưới ảnh chụp trong ngày.

### 2.3 Đặc điểm người dùng
- Người dùng cá nhân, quen thuộc với phím tắt (Ctrl+C, Alt+Tab).  
- Ưu tiên tốc độ, nhẹ máy, dữ liệu local 100%.  
- Có thể tích lũy hàng nghìn file sau 1–2 năm.

### 2.4 Môi trường hoạt động
- Hệ điều hành: Windows 10/11 (64-bit).  
- .NET runtime: .NET 8 hoặc 9.  
- Dung lượng RAM đề xuất: ≥ 4GB (app chạy nền).  
- Không yêu cầu GPU hoặc internet (offline-first).

### 2.5 Giả định và ràng buộc
**Giả định**:  
- Người dùng chạy Windows và có quyền admin để đăng ký global hotkey.  
- Clipboard không bị chặn bởi phần mềm bảo mật bên thứ ba.

**Ràng buộc**:  
- Chỉ hỗ trợ Windows (không macOS/Linux ở phiên bản đầu).  
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
- REQ-101: Giám sát sự kiện clipboard thay đổi (real-time, không chỉ hook Ctrl+C).  
- REQ-102: Khi clipboard có text → append object JSONL: `{ "timestamp": "...", "content": "...", "format": "text", "source_url": "..." (nếu detect được) }`.  
- REQ-103: Khi clipboard có image → lưu .png vào images/ và metadata JSONL.  
- REQ-104: Deduplicate: Bỏ qua nếu nội dung giống lần copy trước trong 10 giây.  
- REQ-105: Phím tắt chụp màn hình (mặc định Alt+S): hỗ trợ region / active window / fullscreen, lưu tự động vào images/.

#### 3.1.3 Giao diện & Tương tác người dùng
- REQ-201: Global hotkey (system-wide):  
  - Alt+Space → mở Quick Search bar (floating, topmost).  
  - Alt+N → mở cửa sổ ghi chú nhanh (Markdown editor).  
  - Alt+S → chụp màn hình.  
- REQ-202: Quick Note window: Editor Markdown, auto-save mỗi 5s hoặc khi Esc/đóng.  
- REQ-203: Quick Search: Thanh tìm kiếm realtime, hiển thị kết quả từ clips/notes/images (tên file + snippet).  
- REQ-204: Gallery view: Grid ảnh trong ngày, click để mở full-size.

#### 3.1.4 Tìm kiếm & Index
- REQ-301: Index dữ liệu text (clips/*.jsonl, notes/*.md) bằng DuckDB hoặc SQLite+FTS5.  
- REQ-302: Tìm kiếm full-text, fuzzy, sắp xếp theo thời gian giảm dần.  
- REQ-303: Rebuild/incremental index khi có dữ liệu mới hoặc ngày mới.

### 3.2 Yêu cầu phi chức năng (Non-Functional Requirements)

| ID       | Yêu cầu                              | Mô tả / Tiêu chí đo lường                              |
|----------|--------------------------------------|-----------------------------------------------------------------|
| NFR-001  | Hiệu suất – Thời gian phản hồi       | Quick Search < 500ms (với <10.000 file tích lũy).               |
| NFR-002  | Hiệu suất – Dung lượng               | App chạy nền < 100MB RAM.                                       |
| NFR-003  | Độ tin cậy                           | Không crash khi clipboard thay đổi liên tục (>100 lần/phút).   |
| NFR-004  | Khả dụng                             | Chạy nền 24/7, tự khởi động cùng Windows (tùy chọn).            |
| NFR-005  | Bảo mật                              | Dữ liệu local, tùy chọn xóa tự động sau 30/90 ngày.             |
| NFR-006  | Khả dụng & Bảo trì                   | Dễ backup (zip folder), dễ migrate (cấu trúc thư mục đơn giản).|
| NFR-007  | Giao diện                            | Modern UI (Mica/Acrylic), hỗ trợ dark/light mode.               |

### 3.3 Yêu cầu giao diện bên ngoài
- Windows API: Clipboard events, RegisterHotKey, Graphics Capture.  
- Không tích hợp API bên thứ ba (offline-first).

## 4. Kịch bản sử dụng mẫu (Use Cases)

1. **Khởi động ngày mới**: App tự tạo thư mục 2026-03-06 → thông báo tray icon.  
2. **Copy code từ web**: Ctrl+C → lưu clips_09-30-05.jsonl với content + URL (nếu có).  
3. **Chụp màn hình ý tưởng**: Alt+S → chọn vùng → lưu screen_10-15-22.png.  
4. **Ghi chú nhanh**: Alt+N → viết Markdown → Esc → auto-save vào notes_2026-03-06.md.  
5. **Tìm lại nội dung cũ**: Alt+Space → gõ "async await" → hiển thị kết quả từ 3 ngày trước.

## 5. Công nghệ đề xuất (Technology Stack)

- Ngôn ngữ: C# .NET 9 (hoặc .NET 8 LTS).  
- UI: WinUI 3 (hiện đại, Mica/Acrylic, tốt hơn WPF).  
- Search/Index: DuckDB (ưu tiên) hoặc SQLite + FTS5.  
- Image: SixLabors.ImageSharp.  
- Hotkey/Clipboard: P/Invoke Windows API + Clipboard.ContentChanged.  
- Markdown: Markdig + custom control.

## 6. Phụ lục
- Cấu trúc thư mục mẫu.  
- Danh sách phím tắt mặc định (có thể tùy chỉnh).  
- Roadmap mở rộng (sync, AI tag, encrypt...).
