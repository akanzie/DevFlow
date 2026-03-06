# Tài liệu Kế hoạch Code Chi tiết (Detailed Coding Plan)  
**Dự án:** DailyClip – MVP (Minimum Viable Product)  
**Phiên bản:** 1.0  
**Thời gian ước tính:** 6–9 tuần (1 người, 20–30h/tuần)  
**Ngày bắt đầu:** 06/03/2026  
**Tác giả:** Kiệt (với hỗ trợ tinh chỉnh)  

---

## 1. Nguyên tắc thứ tự Code (Coding Priority Principles)

**"Inside-out" approach**: Viết code từ trong ra ngoài, core trước, UI sau.

1. **Core domain & storage trước**  
   - Phần không phụ thuộc UI, dễ test unit riêng lẻ.
   - Là foundation cho các tính năng khác.

2. **Automation & background logic**  
   - Clipboard monitor, auto-folder creation, capture service.
   - Không cần UI để test.

3. **Infrastructure critical**  
   - DuckDB index & search (phần khó nhất về performance).
   - Hoàn thành sớm để có time optimize nếu chậm.

4. **Hotkey & global interaction**  
   - Cần sớm để trải nghiệm thực tế (user feel app chạy).
   - Global hotkey (Alt+S, Alt+N, Alt+Space) là "wow factor".

5. **UI & presentation layer**  
   - Làm sau khi backend đã ổn.
   - Ghép ViewModels vào WinUI Windows.

6. **Polish, test, config, release**  
   - Error handling, logging, cleanup scheduler.
   - Single-file publish, packaging.

---

## 2. Timeline Ước tính (1 người, part-time 20–30h/tuần)

| Giai đoạn | Thời gian | Thứ tự prioritized (1=cao nhất) | Deliverable có thể chạy được | Test Strategy |
|-----------|-----------|--------------------------------|------------------------------|----------------|
| **1. Foundation & Setup** | 2–4 ngày | 1-3: Setup, Config, Domain | .sln build success, folder tạo PASS | Manual |
| **2. Storage & File I/O** | 5–7 ngày | 4-6: FileStorage, ClipItem, unit tests | Lưu clipboard thủ công được | Unit test |
| **3. Clipboard Monitor** | 4–6 ngày | 7-8: ClipboardMonitor, test | Auto-save khi copy | Unit + manual (100 copies test) |
| **4. Capture & Hotkey** | 5–7 ngày | 9-11: Capture, Hotkey, HotkeyService | Alt+S chụp, lưu file | Manual hotkey + screenshot verify |
| **5. Quick Note UI** | 3–5 ngày | 12-13: QuickNoteWindow, ViewModel | Alt+N → note window, auto-save | ViewModel unit test + manual |
| **6. DuckDB Index** | 7–10 ngày | 14-16: SearchService, index, FTS query | Index 1000 clips, search < 500ms | Integration test in-memory DB |
| **7. Quick Search UI** | 5–7 ngày | 17-19: SearchWindow, binding results | Alt+Space search, show 50 results | ViewModel test + manual |
| **8. Gallery & Tray** | 4–6 ngày | 20-21: Gallery images, tray icon | View ngày hôm nay ảnh, tray menu | Manual |
| **9. Polish & Release** | 5–7 ngày | 22-24: Error handling, config, cleanup | Config.json works, auto-start OK | Full manual test + coverage >70% |

**Tổng ước tính MVP:** **6–9 tuần** (tùy tốc độ debug Windows API & DuckDB optimization)

---

## 3. Thứ tự Code Chi tiết (24 Priority Steps)

### Phase 1: Foundation & Setup (Days 1–4)

#### STEP 1: Create Project Structure
**Thời gian:** 1 ngày  
**Output:** `.sln` file, 5 projects ready, all packages added

```
DailyClip/
├── DailyClip.sln
├── DailyClip/                      (WinUI 3 main app)
├── DailyClip.Core/                 (Domain + Application layer)
├── DailyClip.Infrastructure/       (Infrastructure layer)
├── DailyClip.Tests/                (xUnit tests)
└── docs/                           (SRS, SDD, etc.)
```

**Commands:**
```bash
dotnet new winui -n DailyClip
dotnet new classlib -n DailyClip.Core
dotnet new classlib -n DailyClip.Infrastructure
dotnet new xunit -n DailyClip.Tests
dotnet new sln -n DailyClip
# Add projects to solution
dotnet sln add DailyClip DailyClip.Core DailyClip.Infrastructure DailyClip.Tests
```

**NuGet Packages to add:**
```bash
# Main app & infrastructure
dotnet add DailyClip package CommunityToolkit.Mvvm
dotnet add DailyClip package Serilog
dotnet add DailyClip package Microsoft.Extensions.DependencyInjection

dotnet add DailyClip.Core package System.Text.Json
dotnet add DailyClip.Infrastructure package DuckDB.NET.Data
dotnet add DailyClip.Infrastructure package SixLabors.ImageSharp
dotnet add DailyClip.Infrastructure package Serilog

# Tests
dotnet add DailyClip.Tests package xunit.runner.visualstudio
dotnet add DailyClip.Tests package Microsoft.NET.Test.Sdk
dotnet add DailyClip.Tests package Moq
dotnet add DailyClip.Tests package FluentAssertions
```

**Checklist:**
- [ ] All projects build without errors
- [ ] NuGet restore successful
- [ ] Create .editorconfig (from CodingRules.md)
- [ ] First git commit: "Initial solution setup"

---

#### STEP 2: AppConfig & Constants
**Thời gian:** 0.5 ngày  
**Location:** `DailyClip.Core/Config/AppConfig.cs`

```csharp
namespace DailyClip.Core.Config;

public class AppConfig
{
    public static class Paths
    {
        public static string RootFolder =>
            Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                "DailyClip");
    }

    public static class Hotkeys
    {
        public const int SearchHotkey = (int)ModifierKeys.Alt | ((int)'S');
        public const int NoteHotkey = (int)ModifierKeys.Alt | ((int)'N');
        public const int SearchWindowHotkey = (int)ModifierKeys.Alt | ((int)'L');
    }

    public static class Timing
    {
        public const int DuplicateCacheWindowSeconds = 10;
        public const int AutoSaveIntervalMs = 5000;
        public const int SearchDebounceMs = 300;
    }

    public static class Cleanup
    {
        public const int RetentionDays = 30;
    }
}
```

**Config.json template (user-editable):**
```json
{
  "rootFolder": "C:\\Users\\user\\AppData\\Roaming\\DailyClip",
  "hotkeyCapture": "Alt+S",
  "hotkeyNote": "Alt+N",
  "hotkeySearch": "Alt+Apostrophe",
  "retentionDays": 30,
  "autoStartWithWindows": false,
  "enableEncryption": false
}
```

**Checklist:**
- [ ] AppConfig.Paths.RootFolder returns valid path
- [ ] Config.json can be loaded (implement later)

---

#### STEP 3: Domain Entities
**Thời gian:** 1 ngày  
**Location:** `DailyClip.Core/Entities/`

```csharp
// ClipItem.cs
namespace DailyClip.Core.Entities;

public record ClipItem(
    DateTimeOffset Timestamp,
    string Type,        // "text" | "image" | "html"
    string Content,     // text hoặc path tới image
    string? SourceUrl = null,
    string? Format = null
)
{
    public ClipItem
    {
        if (Timestamp == default) throw new ArgumentException("Invalid timestamp", nameof(Timestamp));
        if (string.IsNullOrEmpty(Type)) throw new ArgumentNullException(nameof(Type));
        if (string.IsNullOrEmpty(Content)) throw new ArgumentNullException(nameof(Content));
    }

    public bool IsDuplicate(ClipItem other)
    {
        const int windowSeconds = 10;
        return type == other.Type
            && Content == other.Content
            && (Timestamp - other.Timestamp).TotalSeconds <= windowSeconds;
    }
}

// SearchResult.cs
public record SearchResult(
    DateTimeOffset Timestamp,
    string Snippet,      // Preview text
    string FilePath,
    string Type,         // "text" | "image"
    float RelevanceScore
);

// DailyNote.cs
public record DailyNote(
    DateOnly Date,
    string Content       // Markdown content
);
```

**Checklist:**
- [ ] Entity records compile
- [ ] No circular dependencies
- [ ] Snapshot values in test for snapshot testing (later)

---

### Phase 2: Storage & File I/O (Days 5–12)

#### STEP 4: IStorageService Interface (Core)
**Thời gian:** 0.5 ngày

```csharp
namespace DailyClip.Core.Interfaces;

public interface IStorageService
{
    /// <summary>
    /// Ensure daily folder structure exists: [Root]/[YYYY-MM-DD]/{images,clippings,notes}/
    /// </summary>
    Task CreateDailyFolderIfNotExistsAsync();

    /// <summary>
    /// Get today's folder path: [Root]/[YYYY-MM-DD]/
    /// </summary>
    string GetTodayFolderPath();

    /// <summary>
    /// Append a clip to clippings/clips_[HH-mm-ss].jsonl
    /// </summary>
    Task AppendClipAsync(ClipItem clip);

    /// <summary>
    /// Save screenshot to images/screen_[HH-mm-ss].png
    /// </summary>
    Task<string> SaveScreenshotAsync(byte[] imageData);

    /// <summary>
    /// Append markdown line to notes/notes_[YYYY-MM-DD].md
    /// </summary>
    Task AppendNoteAsync(string markdownContent);
}
```

---

#### STEP 5: FileStorageService Implementation (Infrastructure)
**Thời gian:** 2 ngày  
**Location:** `DailyClip.Infrastructure/Services/FileStorageService.cs`

```csharp
namespace DailyClip.Infrastructure.Services;

public class FileStorageService : IStorageService
{
    private readonly ILogger<FileStorageService> _logger;
    private readonly string _rootFolder;

    public FileStorageService(ILogger<FileStorageService> logger)
    {
        _logger = logger;
        _rootFolder = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
            "DailyClip");
    }

    public async Task CreateDailyFolderIfNotExistsAsync()
    {
        var today = DateOnly.FromDateTime(DateTime.Now);
        var todayFolder = Path.Combine(_rootFolder, today.ToString("yyyy-MM-dd"));
        var subfolders = new[] { "images", "clippings", "notes", "index" };

        foreach (var subfolder in subfolders)
        {
            var folderPath = Path.Combine(todayFolder, subfolder);
            if (!Directory.Exists(folderPath))
            {
                Directory.CreateDirectory(folderPath);
                _logger.Information("Created folder: {FolderPath}", folderPath);
            }
        }
    }

    public string GetTodayFolderPath()
    {
        var today = DateOnly.FromDateTime(DateTime.Now);
        return Path.Combine(_rootFolder, today.ToString("yyyy-MM-dd"));
    }

    public async Task AppendClipAsync(ClipItem clip)
    {
        ArgumentNullException.ThrowIfNull(clip);

        var todayFolder = GetTodayFolderPath();
        var clipsFile = Path.Combine(todayFolder, "clippings", "clips_current.jsonl");

        var json = JsonSerializer.Serialize(clip);
        await File.AppendAllTextAsync(clipsFile, json + Environment.NewLine);

        _logger.Information("Clip appended: {FilePath}", clipsFile);
    }

    public async Task<string> SaveScreenshotAsync(byte[] imageData)
    {
        ArgumentNullException.ThrowIfNull(imageData);

        var todayFolder = GetTodayFolderPath();
        var timestamp = DateTime.Now.ToString("HH-mm-ss-fff");
        var filePath = Path.Combine(todayFolder, "images", $"screen_{timestamp}.png");

        await File.WriteAllBytesAsync(filePath, imageData);
        _logger.Information("Screenshot saved: {FilePath}", filePath);

        return filePath;
    }

    public async Task AppendNoteAsync(string markdownContent)
    {
        ArgumentNullException.ThrowIfNull(markdownContent);

        var today = DateOnly.FromDateTime(DateTime.Now);
        var todayFolder = GetTodayFolderPath();
        var noteFile = Path.Combine(todayFolder, "notes", $"notes_{today:yyyy-MM-dd}.md");

        await File.AppendAllTextAsync(noteFile, markdownContent + Environment.NewLine);
        _logger.Information("Note appended: {FilePath}", noteFile);
    }
}
```

---

#### STEP 6: Unit Tests for Storage
**Thời g時間:** 1.5 ngày  
**Location:** `DailyClip.Tests/Infrastructure/FileStorageServiceTests.cs`

```csharp
public class FileStorageServiceTests : IDisposable
{
    private readonly string _tempFolder;
    private readonly FileStorageService _sut;
    private readonly Mock<ILogger<FileStorageService>> _loggerMock;

    public FileStorageServiceTests()
    {
        _tempFolder = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
        _loggerMock = new Mock<ILogger<FileStorageService>>();

        // Inject temp folder (need to adjust implementation to accept root path)
        _sut = new FileStorageService(_loggerMock.Object, _tempFolder);
    }

    [Fact]
    public async Task CreateDailyFolderIfNotExists_CreatesStructure()
    {
        // Act
        await _sut.CreateDailyFolderIfNotExistsAsync();

        // Assert
        var todayPath = _sut.GetTodayFolderPath();
        Directory.Exists(Path.Combine(todayPath, "images")).Should().BeTrue();
        Directory.Exists(Path.Combine(todayPath, "clippings")).Should().BeTrue();
        Directory.Exists(Path.Combine(todayPath, "notes")).Should().BeTrue();
    }

    [Fact]
    public async Task AppendClipAsync_ValidClip_WritesJsonl()
    {
        // Arrange
        await _sut.CreateDailyFolderIfNotExistsAsync();
        var clip = new ClipItem(DateTimeOffset.Now, "text", "test content");

        // Act
        await _sut.AppendClipAsync(clip);

        // Assert
        var clipsFile = Path.Combine(_sut.GetTodayFolderPath(), "clippings", "clips_current.jsonl");
        var content = await File.ReadAllTextAsync(clipsFile);
        content.Should().Contain("test content");
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempFolder))
            Directory.Delete(_tempFolder, recursive: true);
    }
}
```

**Checklist:**
- [ ] Unit tests pass: `dotnet test --filter "FileStorageServiceTests"`
- [ ] Can append JSONL lines sequentially
- [ ] Folder structure created correctly

---

#### STEP 7: ClipItem Factory & Helpers
**Thời gian:** 1 ngày  
**Location:** `DailyClip.Core/Services/ClipItemFactory.cs`

```csharp
public static class ClipItemFactory
{
    public static ClipItem FromText(string text, string? sourceUrl = null)
    {
        ArgumentNullException.ThrowIfNull(text);
        return new(DateTimeOffset.Now, "text", text, sourceUrl, "plain");
    }

    public static ClipItem FromMarkdownCode(string code, string? language = null)
    {
        return new(DateTimeOffset.Now, "text", code, null, $"code:{language}");
    }
}

public class DuplicateDetector
{
    private readonly MemoryCache _cache = new(new MemoryCacheOptions());

    public bool IsDuplicate(string content)
    {
        var hash = ComputeSha256(content);
        var isCached = _cache.TryGetValue(hash, out _);

        if (!isCached)
        {
            _cache.Set(hash, true, new MemoryCacheEntryOptions
            {
                AbsoluteExpirationRelativeToNow = TimeSpan.FromSeconds(10)
            });
        }

        return isCached;
    }

    private static string ComputeSha256(string text)
    {
        using var sha = new System.Security.Cryptography.SHA256Managed();
        var hash = sha.ComputeHash(System.Text.Encoding.UTF8.GetBytes(text));
        return Convert.ToHexString(hash);
    }
}
```

---

### Phase 3: Clipboard Monitor (Days 13–19)

#### STEP 8: IClipboardMonitor Interface
**Thời gian:** 0.5 ngày

```csharp
namespace DailyClip.Core.Interfaces;

public interface IClipboardMonitor
{
    Task StartMonitoringAsync();
    Task StopMonitoringAsync();
    event EventHandler<ClipboardChangedEventArgs>? ClipboardChanged;
}

public class ClipboardChangedEventArgs : EventArgs
{
    public ClipItem? Clip { get; set; }
    public Exception? Error { get; set; }
}
```

---

#### STEP 9: ClipboardMonitorService Implementation
**Thời g간:** 3 ngày  
**Location:** `DailyClip.Infrastructure/Services/ClipboardMonitorService.cs`

```csharp
namespace DailyClip.Infrastructure.Services;

public class ClipboardMonitorService : IClipboardMonitor
{
    private readonly IStorageService _storage;
    private readonly ISearchService _search;
    private readonly ILogger<ClipboardMonitorService> _logger;
    private readonly DuplicateDetector _duplicateDetector = new();

    public event EventHandler<ClipboardChangedEventArgs>? ClipboardChanged;

    public ClipboardMonitorService(
        IStorageService storage,
        ISearchService search,
        ILogger<ClipboardMonitorService> logger)
    {
        _storage = storage;
        _search = search;
        _logger = logger;
    }

    public async Task StartMonitoringAsync()
    {
        // Subscribe to UWP Clipboard events
        Clipboard.ContentChanged += OnClipboardChanged;
        _logger.Information("Clipboard monitoring started");
    }

    public async Task StopMonitoringAsync()
    {
        Clipboard.ContentChanged -= OnClipboardChanged;
        _logger.Information("Clipboard monitoring stopped");
    }

    private async void OnClipboardChanged(object? sender, EventArgs e)
    {
        try
        {
            var dataPackage = Clipboard.GetContent();

            if (dataPackage.Contains(StandardDataFormats.Text))
            {
                var text = await dataPackage.GetTextAsync();
                await ProcessTextAsync(text);
            }
            else if (dataPackage.Contains(StandardDataFormats.Bitmap))
            {
                await ProcessBitmapAsync(dataPackage);
            }
        }
        catch (Exception ex)
        {
            _logger.Error(ex, "Error processing clipboard event");
            ClipboardChanged?.Invoke(this, new ClipboardChangedEventArgs { Error = ex });
        }
    }

    private async Task ProcessTextAsync(string text)
    {
        if (_duplicateDetector.IsDuplicate(text))
        {
            _logger.Debug("Duplicate content ignored");
            return;
        }

        var sourceUrl = ExtractUrlFromClipboard();
        var clip = ClipItemFactory.FromText(text, sourceUrl);

        await _storage.AppendClipAsync(clip);
        await _search.IndexClipAsync(clip);

        _logger.Information("Text clip processed: {Length} chars", text.Length);
        ClipboardChanged?.Invoke(this, new ClipboardChangedEventArgs { Clip = clip });
    }

    private async Task ProcessBitmapAsync(DataPackage dataPackage)
    {
        // TODO: Implement bitmap handling
    }

    private string? ExtractUrlFromClipboard()
    {
        // TODO: Extract URL if HTML format available
        return null;
    }
}
```

---

#### STEP 10: Unit Tests for ClipboardMonitor
**Thời gian:** 2 ngày

```csharp
public class ClipboardMonitorServiceTests
{
    private readonly Mock<IStorageService> _storageMock = new();
    private readonly Mock<ISearchService> _searchMock = new();
    private readonly Mock<ILogger<ClipboardMonitorService>> _loggerMock = new();
    private readonly ClipboardMonitorService _sut;

    public ClipboardMonitorServiceTests()
    {
        _sut = new ClipboardMonitorService(_storageMock.Object, _searchMock.Object, _loggerMock.Object);
    }

    [Fact]
    public async Task ProcessTextAsync_NewContent_CallsStorageAndSearch()
    {
        // Arrange & Act
        await _sut.ProcessTextAsync("new code");

        // Assert
        _storageMock.Verify(s => s.AppendClipAsync(It.IsAny<ClipItem>()), Times.Once);
        _searchMock.Verify(s => s.IndexClipAsync(It.IsAny<ClipItem>()), Times.Once);
    }

    [Fact]
    public async Task ProcessTextAsync_DuplicateWithin10s_SkipsProcessing()
    {
        // Arrange: Set duplicate
        var detector = new DuplicateDetector();
        detector.IsDuplicate("content"); // Mark as seen

        // Act: Call again immediately
        var result = detector.IsDuplicate("content");

        // Assert
        result.Should().BeTrue();
    }
}
```

---

### Phase 4 onwards: Continue with Steps 11–24

(Similar level of detail for Capture, Hotkey, QuickNote, DuckDB, Search UI, Gallery, Tray, Polish)

---

## 4. Thứ tự ưu tiên từng module (Quick Reference)

| Priority | Module | Dependencies | MVP Essential | Estimated Days |
|----------|--------|--------------|----------------|-----------------|
| 1 | Setup + NuGet | - | Yes | 1 |
| 2 | AppConfig | - | Yes | 0.5 |
| 3 | Domain Entities | - | Yes | 1 |
| 4 | IStorageService | Core | Yes | 0.5 |
| 5 | FileStorageService | IStorageService | Yes | 2 |
| 6 | Storage Unit Tests | FileStorageService | Yes | 1.5 |
| 7 | ClipItem Factories | Domain | Yes | 1 |
| 8 | IClipboardMonitor | Core | Yes | 0.5 |
| 9 | ClipboardMonitorService | IStorage, ISearch | Yes | 3 |
| 10 | Clipboard Tests | ClipboardMonitor | Yes | 2 |
| 11 | IScreenCaptureService | Core | Yes | 0.5 |
| 12 | ScreenCaptureService | IScreenCapture | Yes | 2 |
| 13 | IHotkeyService | Core | Yes | 0.5 |
| 14 | HotkeyService (P/Invoke) | App | Yes | 2 |
| 15 | App Startup & DI | All above | Yes | 1 |
| 16 | QuickNoteWindow | MVVM | Yes | 2 |
| 17 | QuickNoteViewModel | IStorage | Yes | 1 |
| 18 | ISearchService | Core | Yes | 0.5 |
| 19 | DuckDBSearchService | ISearch, DuckDB | Yes | 4 |
| 20 | Search Integration Tests | DuckDB | Yes | 2 |
| 21 | QuickSearchWindow | MVVM | Yes | 2 |
| 22 | QuickSearchViewModel | ISearch | Yes | 1 |
| 23 | Gallery Image Grid | MVVM | No | 2 |
| 24 | System Tray Icon | App | No | 1.5 |
| 25 | Error Handling & Logging | All | Yes | 1 |
| 26 | Config.json & Cleanup | Utility | No | 1 |
| 27 | Polish & Single-file Publish | All | No | 2 |

---

## 5. Được khuyến nghị bắt đầu ngay (Immediate Action Plan)

### Week 1: Core Foundation + Storage
**Target:** Friday EOD có clipboard auto-save chạy được

**Ngày 1 (Monday 06/03):**
- [ ] Create solution + 5 projects (STEP 1)
- [ ] Add all NuGet packages
- [ ] Create AppConfig (STEP 2)
- [ ] Create Domain Entities (STEP 3)
- [ ] Commit: "Initial project + domain setup"

**Ngày 2-3 (Tuesday-Wednesday):**
- [ ] Implement IStorageService interface (STEP 4)
- [ ] Implement FileStorageService (STEP 5)
- [ ] Write unit tests (STEP 6)
- [ ] All tests pass locally
- [ ] Commit: "Storage service + unit tests"

**Ngày 4 (Thursday):**
- [ ] Implement ClipboardMonitorService (STEP 9)
- [ ] Wire up to App startup
- [ ] Manual test: Open app → copy text multiple times → verify `.jsonl` file written
- [ ] Commit: "Clipboard monitoring MVP"

### Week 2: Hotkey + Capture + Quick Note
**Target:** Alt+S chụp, Alt+N ghi chú, Alt+Space tìm kiếm dialog (mock results)

**Ngày 5-6:**
- [ ] Implement HotkeyService (P/Invoke) (STEP 14)
- [ ] Test Alt+S, Alt+N, Alt+Space hotkeys work
- [ ] Commit: "Global hotkey support"

**Ngày 7-8:**
- [ ] Implement ScreenCaptureService (STEP 12)
- [ ] Wire up Alt+S → capture region → save
- [ ] Test: Take screenshot, verify file exists
- [ ] Commit: "Screenshot capture"

**Ngày 9-10:**
- [ ] Create QuickNoteWindow + ViewModel (STEP 16-17)
- [ ] Implement auto-save on timer
- [ ] Test: Alt+N, type text, Esc, verify file created
- [ ] Commit: "Quick note window with auto-save"

### Week 3: DuckDB Index & Search
**Target:** Search functionality working (most complex part)

**Ngày 11-14:**
- [ ] Implement ISearchService interface
- [ ] Implement DuckDBSearchService with FTS (STEP 19)
- [ ] Write integration tests with in-memory DB
- [ ] Ensure search < 500ms for 1000 clips
- [ ] Commit: "DuckDB search + benchmarks"

**Ngày 15-17:**
- [ ] Create QuickSearchWindow + ViewModel (STEP 21-22)
- [ ] Bind search results to ListView
- [ ] Test: Alt+Space → search keyword → see results
- [ ] Commit: "Quick search UI + binding"

### Week 4+: Polish + Release
- [ ] Gallery view for images (optional for MVP)
- [ ] Tray icon + context menu
- [ ] Error handling + logging (Serilog to file)
- [ ] Config.json, cleanup scheduler
- [ ] Code coverage > 70%
- [ ] Single-file publish
- [ ] Release v0.1.0 MVP

---

## 6. Key Milestones & Success Criteria

| Milestone | Target Date | Success Criteria |
|-----------|------------|-----------------|
| **M1: Clipboard saving** | Week 1 EOD | Copy text → auto-saved to JSONL file |
| **M2: Hotkey + Capture + Note** | Week 2 EOD | Alt+S/N works, files created |
| **M3: Search + UI** | Week 3 EOD | Alt+Space search, < 500ms query time |
| **M4: MVP Release** | Week 4 EOD | All 8 giai đoạn hoàn thành, testable, shippable |

---

## 7. Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Windows API P/Invoke compatibility | Medium | High | Test early on Windows 10/11; use Windows.ApplicationModel if possible |
| DuckDB performance not meeting target | Medium | High | Benchmark frequently; consider SQLite FTS5 fallback |
| XAML/WinUI binding complexity | Low | Medium | Use CommunityToolkit.Mvvm; test ViewModel logic in unit tests first |
| Clipboard monitor missing events | Low | High | Implement fallback poll timer (every 1-2 sec) alongside event hook |
| File system permission issues | Low | Medium | Handle IOException gracefully; log with actionable messages |

---

## 8. Git Workflow & Commits

Commit frequently (every completed STEP):

```bash
git commit -m "STEP 1: Initial solution setup"
git commit -m "STEP 2-3: AppConfig + Domain entities"
git commit -m "STEP 4-6: FileStorage service + unit tests"
git commit -m "STEP 9-10: Clipboard monitor service"
# ... và cứ tiếp tục
```

Push to `main` (hoặc `dev`) khi milestone đạt.

---

## 9. Kết luận

Bằng cách follow roadmap này, bạn sẽ:
- ✅ Có sản phẩm chạy được sớm (MVP by week 4).
- ✅ Tránh rework vì code từ core ra, inside-out.
- ✅ Phát hiện vấn đề Windows API sớm (hotkey/clipboard).
- ✅ Có coverage test cao từ đầu (domain/application /80%+).
- ✅ Có thể demo & get feedback sớm.

**Start STEP 1 ngay hôm nay!** Good luck 🚀
