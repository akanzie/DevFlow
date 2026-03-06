# Tài liệu Thiết kế Phần mềm Chi tiết (Detailed Software Design Document)  
**Tên phần mềm:** DailyClip – Công cụ tự động hóa ghi chú và lưu trữ dữ liệu cá nhân  
**Phiên bản:** 1.0 (Detailed Design – Low-Level)  
**Ngày soạn thảo:** 06/03/2026  
**Tác giả:** Kiệt (với hỗ trợ tinh chỉnh)  

## 1. Giới thiệu

### 1.1 Mục đích
Tài liệu này mô tả thiết kế chi tiết (low-level design) của DailyClip, bao gồm:  
- Thiết kế lớp và module chính.  
- Giao diện (interfaces) và mối quan hệ giữa các lớp.  
- Thuật toán cốt lõi (clipboard monitor, indexing, search).  
- Thiết kế dữ liệu chi tiết và schema DuckDB.  
- Sequence & class diagram (mô tả text).  

Tài liệu phục vụ lập trình viên implement code, tester viết unit test, và maintainer hiểu cấu trúc nội bộ.

### 1.2 Phạm vi
- Chi tiết cho MVP (Minimum Viable Product): clipboard monitor, capture, quick note, global search, storage theo ngày.  
- Không bao gồm: settings UI chi tiết, cleanup scheduler, export module (có thể thêm sau).

### 1.3 Tài liệu tham chiếu
- SRS DailyClip v1.0  
- System Design Document (High-Level) v1.0  

## 2. Thiết kế tổng thể (Refined Architecture)

DailyClip sử dụng **Clean Architecture** + **MVVM** (Model-View-ViewModel) cho phần UI:  
- **Core (Domain)**: Entities, Use Cases, Interfaces.  
- **Application**: Services, DTOs.  
- **Infrastructure**: File system, DuckDB, Windows API wrappers.  
- **Presentation**: WinUI 3 Views + ViewModels.

## 3. Thiết kế lớp & Module chính (Class & Module Design)

### 3.1 Entities (Domain Layer)

| Lớp/Entity              | Mô tả                                                                 | Thuộc tính chính |
|-------------------------|-----------------------------------------------------------------------|------------------|
| ClipItem                | Đại diện một clip từ clipboard (text/image)                           | Timestamp (DateTimeOffset), Type (enum: Text/Image/Html), Content (string), SourceUrl (string?), Format (string) |
| Screenshot              | Metadata của ảnh chụp màn hình                                        | Timestamp, FilePath (string), Dimensions (Width/Height) |
| DailyNote               | Nội dung ghi chú ngày (Markdown)                                      | Date (DateOnly), Content (string) |
| SearchResult            | Kết quả tìm kiếm                                                      | Timestamp, Snippet (string), FilePath, Type, RelevanceScore |

### 3.2 Interfaces (Application Layer)

| Interface               | Phương thức chính | Mục đích (liên quan REQ) |
|-------------------------|-------------------|--------------------------|
| IClipboardMonitor       | StartMonitoring(), StopMonitoring() | REQ-101 |
| IStorageService         | CreateDailyFolder(), AppendClip(ClipItem), SaveScreenshot(byte[]), AppendNote(string) | REQ-001 → REQ-003 |
| ISearchService          | IndexDailyData(), Search(string query, int limit) → List<SearchResult> | REQ-301 → REQ-303 |
| IHotkeyService          | RegisterHotkey(Hotkey combo, Action callback), UnregisterAll() | REQ-201 |
| IScreenCaptureService   | CaptureRegion(Rect), CaptureActiveWindow(), CaptureFullscreen() → byte[] | REQ-105 |

### 3.3 Main Services (Implementation)

- **ClipboardMonitorService** (implement IClipboardMonitor)  
  - Sử dụng `Windows.ApplicationModel.DataTransfer.Clipboard.ContentChanged` event.  
  - Deduplicate: lưu hash (SHA256) của content + timestamp last clip trong MemoryCache (expire 10s).  
  - Extract source_url: nếu clipboard có HTML format → parse <a href> hoặc meta.

- **DuckDBSearchService** (implement ISearchService)  
  - Khởi tạo DB: `DuckDBConnection` với file `[Root]/[YYYY-MM-DD]/index/daily_index.duckdb`.  
  - Table schema:
    ```sql
    CREATE TABLE clips_index (
        id UUID PRIMARY KEY DEFAULT uuid(),
        timestamp TIMESTAMPTZ NOT NULL,
        file_path VARCHAR NOT NULL,
        type VARCHAR NOT NULL,
        content TEXT NOT NULL,
        full_text TSVECTOR  -- cho FTS
    );
    CREATE INDEX idx_fts ON clips_index USING GIN(full_text);
    ```
  - Index incremental: mỗi clip mới → `INSERT INTO ... VALUES (...) ON CONFLICT DO NOTHING;`

- **HotkeyService**  
  - P/Invoke `RegisterHotKey` từ user32.dll.  
  - Window message loop (WndProc) xử lý WM_HOTKEY.  
  - Singleton lifetime, inject vào App.xaml.cs.

## 4. Thuật toán chính (Key Algorithms)

### 4.1 Clipboard Processing (Pseudo-code)
```csharp
void OnClipboardChanged()
{
    var content = Clipboard.GetContent();
    if (content.Contains(StandardDataFormats.Text))
    {
        string text = await content.GetTextAsync();
        if (IsDuplicate(text)) return;

        var clip = new ClipItem { Timestamp = DateTimeOffset.Now, Type = "text", Content = text };
        clip.SourceUrl = ExtractUrlFromHtml(content);
        
        await _storage.AppendClipAsync(clip);
        await _search.IndexClipAsync(clip);
    }
    else if (content.Contains(StandardDataFormats.Bitmap))
    {
        // Lưu PNG + metadata
    }
}

bool IsDuplicate(string text)
{
    string hash = ComputeSha256(text);
    return _cache.TryGetValue(hash, out _) && (DateTimeOffset.Now - lastTime < 10s);
}
```

### 4.2 Full-Text Search
```sql
-- Query mẫu trong DuckDB
SELECT 
    timestamp, 
    file_path, 
    snippet(content, 100) AS preview,
    ts_rank_cd(full_text, websearch_to_tsquery(?)) AS rank
FROM clips_index
WHERE full_text @@ websearch_to_tsquery(?)
ORDER BY rank DESC, timestamp DESC
LIMIT 50;
```

## 5. Sequence Diagrams (Mô tả text)

### 5.1 Sequence: Copy text → Lưu & Index
```
User -> Clipboard : Ctrl+C
Clipboard -> ClipboardMonitorService : ContentChanged event
ClipboardMonitorService -> StorageService : AppendClip(ClipItem)
StorageService -> FileSystem : Append JSONL line to clips_xx.jsonl
ClipboardMonitorService -> SearchService : IndexClip(ClipItem)
SearchService -> DuckDB : INSERT INTO clips_index ...
```

### 5.2 Sequence: Quick Search
```
User -> System : Alt+Space
HotkeyService -> QuickSearchView : Show()
QuickSearchViewModel -> SearchService : Search(query)
SearchService -> DuckDB : Execute query
SearchService -> QuickSearchViewModel : List<SearchResult>
QuickSearchViewModel -> View : Bind to ListView
```

## 6. Thiết kế giao diện chi tiết (UI Components)

- **QuickSearchWindow**: WinUI Window (Extends MicaBackdrop), SearchBox + ListView (ItemTemplate với Timestamp + Snippet + Icon).  
- **QuickNoteWindow**: TextBox với Markdown rendering (sử dụng CommunityToolkit.Markdown hoặc Markdig). Auto-save DispatcherTimer 5s.  
- **TrayIcon**: NotifyIcon với ContextMenuFlyout (Open Search, Open Note, Open Today Folder, Exit).

## 7. Thiết kế dữ liệu chi tiết

- **JSONL Clip example**:
  ```json
  {"timestamp":"2026-03-06T09:30:05+07:00","type":"text","content":"async Task Main()","source_url":"https://github.com/...","format":"code"}
  ```

- **DuckDB Indexing Strategy**:  
  - Daily rebuild nếu >500 clips mới (để tránh fragmentation).  
  - Incremental insert cho hầu hết trường hợp.

## 8. Quyết định chi tiết & Trade-off bổ sung

- Sử dụng **DuckDB** thay SQLite vì tốc độ FTS cao hơn trên workload text-heavy (benchmark ~3-5x nhanh hơn cho query 10k+ records).  
- **MVVM** với CommunityToolkit.Mvvm để binding dễ dàng, testable.  
- Error handling: Wrap tất cả IO/DuckDB calls trong try-catch + logging (Serilog to file).

## 9. Phụ lục
- **Class Diagram** (text UML-like):  
  ```
  ClipboardMonitorService --> IStorageService
  ClipboardMonitorService --> ISearchService
  QuickSearchViewModel --> ISearchService
  App --> HotkeyService (singleton)
  ```
- **Unit Test Coverage gợi ý**: Clipboard deduplicate, JSONL append, DuckDB query ranking.  
- **Next steps**: Implement prototype ClipboardMonitor + Storage trước (2-3 ngày).
