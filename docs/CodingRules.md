# Tài liệu Quy tắc Code (Coding Rules & Style Guidelines)  
**Dự án:** DailyClip  
**Phiên bản:** 1.0  
**Áp dụng cho:** Toàn bộ codebase C# / XAML (WinUI 3 + .NET 9)  
**Mục tiêu:** Code sạch, nhất quán, dễ đọc, dễ test, dễ mở rộng. Tuân thủ nguyên tắc **"Code is read much more often than written"**.

---

## 1. Nguyên tắc chung (General Principles)

- **Clean Code & SOLID** → Áp dụng nghiêm ngặt (Single Responsibility, Open-Closed, Dependency Inversion…).
- **Clean Architecture** → Tách rõ Domain → Application → Infrastructure → Presentation.
- **MVVM** → Sử dụng CommunityToolkit.Mvvm cho ViewModel (ObservableProperty, RelayCommand…).
- **Performance & Lightweight** → Tránh allocation không cần thiết, dùng struct khi phù hợp, ưu tiên async I/O.
- **Error Handling** → Không catch Exception chung chung. Sử dụng specific exception + logging (Serilog).
- **Async/Await** → Luôn dùng async cho I/O (file, clipboard, DB). ConfigureAwait(false) ở nơi không cần context.
- **Null Safety** → Sử dụng nullable reference types (enable `<Nullable>enable</Nullable>` trong .csproj).
- **Modern C#** → Sử dụng C# 12+ features: primary constructors, collection expressions, default lambda params…

---

## 2. Naming Conventions (theo Microsoft official)

| Loại                  | Quy tắc                  | Ví dụ                              |
|-----------------------|--------------------------|------------------------------------|
| Class / Struct / Interface / Enum | **PascalCase**           | `ClipboardMonitorService`, `ClipItem` |
| Method / Property     | **PascalCase**           | `AppendClipAsync`, `IsDuplicate`   |
| Field (private)       | **_camelCase**           | `_storageService`, `_lastHash`     |
| Local variable / Parameter | **camelCase**       | `clipItem`, `queryText`            |
| Constant              | **PascalCase** hoặc **UPPER_CASE** (tùy ngữ cảnh) | `MaxCacheAgeSeconds`               |
| Interface             | Bắt đầu bằng **I**       | `IStorageService`, `ISearchService` |
| Event                 | **PascalCase** + **EventHandler** suffix nếu cần | `ClipboardChanged`                 |
| XAML Control / Binding | **camelCase** hoặc **PascalCase** nhất quán | `searchBox`, `ResultsListView`     |

**Quy tắc chi tiết:**
- Không dùng Hungarian notation (strName, iCount…).
- Không dùng underscore ở đầu public member.
- Tên phải **rõ nghĩa**, tránh viết tắt trừ khi phổ biến (e.g. `url` thay vì `uniformResourceLocator`).
- Enum member: PascalCase (e.g. `TextFormat.Markdown`, `ClipType.Image`).
- Sử dụng suffix/prefix khi cần: `...Service`, `...Repository`, `...ViewModel`, `...View`.

---

## 3. Formatting & Layout

### 3.1 Chung
- **Indentation**: 4 spaces (không dùng tab).
- **Line length**: Tối đa 120 ký tự (nên <100 cho dễ đọc trên màn hình nhỏ).
- **Braces**: Luôn dùng braces `{}` cho if/else/for/while (ngay cả single-line).
- **Encoding**: UTF-8 without BOM.
- **Line endings**: CRLF (Windows environment).

### 3.2 Spacing
- Một khoảng trắng quanh operator: `a + b`, `if (condition)`.
- Không khoảng trắng trước `(` trong method call: `Method(arg)`.
- Khoảng trắng sau keyword: `if (`, `for (`, `while (`.
- Một dòng trống giữa các method, hai dòng giữa các class/region.
- Không trailing whitespace.

### 3.3 Using Directives
```csharp
// Sắp xếp theo alphabet, nhóm: System → Microsoft → Third-party → Project
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

using DuckDB.NET.Data;
using SixLabors.ImageSharp;

using DailyClip.Core.Entities;
using DailyClip.Infrastructure.Services;
```

- Chỉ `using static` khi thực sự cần (e.g. `using static System.Math;`).
- Xóa unused using (Visual Studio Code Cleanup).

### 3.4 Regions
- Không lạm dụng regions.
- Chỉ dùng nếu file > 300 dòng và có lý do rõ ràng (e.g. Event handlers, Properties).
- Format: `#region Region Name` ... `#endregion`.

---

## 4. Language & Pattern Specific Rules

### 4.1 Class / Struct
```csharp
// Ưu tiên primary constructor (C# 12+) nếu có dependency injection
public class ClipboardMonitorService(IStorageService storageService, ILogger<ClipboardMonitorService> logger) 
    : IClipboardMonitor
{
    private const int DuplicateCacheDurationSeconds = 10;
    
    public async Task StartMonitoringAsync()
    {
        // Implementation
    }
}

// Sử dụng record cho immutable data
public record ClipItem(
    DateTimeOffset Timestamp,
    string Content,
    string Type,
    string? SourceUrl = null
);

// File layout:
// 1. Constants
// 2. Fields
// 3. Constructor(s)
// 4. Properties / Events
// 5. Public methods
// 6. Internal methods
// 7. Private methods
```

### 4.2 Method Best Practices
```csharp
// ✓ Good: < 40 dòng, rõ ràng
public async Task AppendClipAsync(ClipItem clip)
{
    if (clip == null) throw new ArgumentNullException(nameof(clip));
    
    var json = JsonSerializer.Serialize(clip);
    await _fileWriter.AppendLineAsync(json).ConfigureAwait(false);
    _logger.Information("Clip appended: {Content}", clip.Content);
}

// ✗ Bad: > 100 dòng, làm quá nhiều thứ
public async Task ProcessClipboardEvent()
{
    // logic phức tạp, error handling, cả indexing...
}

// ✓ Good: Extract helper methods
private bool IsDuplicate(string content) 
    => _cache.TryGetValue(ComputeHash(content), out _);

private string ComputeHash(string text)
{
    using var sha = System.Security.Cryptography.SHA256.Create();
    var hash = sha.ComputeHash(System.Text.Encoding.UTF8.GetBytes(text));
    return Convert.ToHexString(hash);
}
```

### 4.3 Async Code
```csharp
// ✓ Always async for I/O
public async Task SaveScreenshotAsync(byte[] imageData)
{
    await _fileService.WriteAsync(imageData).ConfigureAwait(false);
}

// ✓ Use ConfigureAwait(false) in library code (non-UI)
await Task.Delay(100).ConfigureAwait(false);

// ✗ Never block on async
var result = SomeAsyncMethod().Result; // ✗ Deadlock risk!

// ✓ Use Task.Run for CPU-bound work off main thread if needed
var result = await Task.Run(() => HeavyComputation()).ConfigureAwait(false);

// ✓ Proper async Unit Test
[Fact]
public async Task AppendClipAsync_ShouldSaveToFile()
{
    // Arrange, Act, Assert
    await _service.AppendClipAsync(clip);
}
```

### 4.4 Exception Handling
```csharp
// ✓ Good: Catch specific exceptions
try
{
    await _db.QueryAsync(sql);
}
catch (DuckDBException ex) when (ex.Message.Contains("syntax"))
{
    _logger.Error(ex, "Invalid SQL query: {Query}", sql);
    throw new InvalidOperationException("Search query invalid", ex);
}
catch (IOException ex)
{
    _logger.Error(ex, "File I/O error");
    // Handle gracefully or rethrow
}

// ✗ Bad: Catch generic Exception
catch (Exception ex) // ✗ Never do this
{
    // Can't determine what went wrong
}

// ✓ Rethrow only when needed
catch (SomeException ex)
{
    _logger.Error(ex, "Context about error");
    throw; // or throw new CustomException("...", ex);
}
```

### 4.5 Null Safety & Nullable Reference Types
```csharp
// Enable in .csproj: <Nullable>enable</Nullable>

// ✓ Good: Use null-conditional operators
string? sourceUrl = GetSourceUrl(clip);
int length = sourceUrl?.Length ?? 0;

// ✓ Use null-coalescing assignment
_cache ??= new Dictionary<string, object>();

// ✓ Range & null check
public IEnumerable<ClipItem> GetClips(int skip, int take)
{
    ArgumentOutOfRangeException.ThrowIfNegative(skip);
    ArgumentOutOfRangeException.ThrowIfNegative(take);
    
    return _clips.Skip(skip).Take(take);
}
```

### 4.6 LINQ & Collections
```csharp
// ✓ Use query syntax for readability (when complex)
var recentClips = from clip in _clips
                  where clip.Timestamp > DateTime.Now.AddHours(-1)
                  orderby clip.Timestamp descending
                  select clip;

// ✓ Use method syntax for simple queries
var count = _clips.Count(c => c.Type == "text");

// ✓ Use collection expressions (C# 12+)
var list = [item1, item2, ..._otherItems];

// ✓ Avoid LINQ on large collections without filtering
var allClips = _clips.ToList(); // OK if needed
var filtered = _clips.Where(c => c.Timestamp > cutoff).ToList(); // Better
```

---

## 5. XAML & WinUI 3 Rules

### 5.1 XAML Style Guide
```xml
<!-- ✓ Good: Compiled binding (faster) -->
<TextBlock Text="{x:Bind ViewModel.Title, Mode=OneWay}" />

<!-- ✗ Avoid: Runtime binding (slower, less type-safe) -->
<TextBlock Text="{Binding Title}" />

<!-- ✓ Use style/resource for consistency -->
<TextBlock Style="{StaticResource BodyTextBlockStyle}" Text="..."/>

<!-- ✓ Localization with x:Uid (future-proof) -->
<TextBlock x:Uid="SearchResults_Title" />

<!-- ✓ Use RelayCommand from CommunityToolkit.Mvvm -->
<Button Command="{x:Bind ViewModel.SearchCommand}" Content="Search" />
```

### 5.2 ViewModel Pattern (MVVM)
```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

public partial class QuickSearchViewModel : ObservableObject
{
    private readonly ISearchService _searchService;
    
    [ObservableProperty]
    private string searchQuery = string.Empty;
    
    [ObservableProperty]
    private ObservableCollection<SearchResult> results = [];
    
    [RelayCommand]
    private async Task SearchAsync()
    {
        if (string.IsNullOrWhiteSpace(SearchQuery))
            return;
            
        var results = await _searchService.SearchAsync(SearchQuery);
        Results = new ObservableCollection<SearchResult>(results);
    }
    
    public QuickSearchViewModel(ISearchService searchService)
    {
        _searchService = searchService;
    }
}
```

### 5.3 Code-Behind Minimalism (WinUI 3 View)
```csharp
// ✓ Minimal code-behind: mostly wiring ViewModel
public sealed partial class QuickSearchWindow : Window
{
    public QuickSearchWindow()
    {
        this.InitializeComponent();
        this.DataContext = new QuickSearchViewModel(App.GetService<ISearchService>());
    }
}

// ✗ Avoid: Heavy logic in code-behind
private void SearchButton_Click(object sender, RoutedEventArgs e)
{
    // Don't put complex logic here!
}
```

---

## 6. Comments & Documentation

### 6.1 When to Comment
```csharp
// ✓ Comment "why", not "what"
// We use SHA256 because it's resistant to timing attacks (vs simple hash)
var hash = ComputeSha256(content);

// ✗ Comment "what" (obvious from code)
// Increment i
i++;

// ✓ Complex algorithm: explain approach
// Deduplicate clips: maintain a 10-second sliding window of hashes
// to avoid recording the same content twice if clipboard fires multiple events
private bool IsDuplicate(string content)
{
    // ...
}
```

### 6.2 XML Documentation (public API)
```csharp
/// <summary>
/// Appends a clip item to the daily storage and updates the search index.
/// </summary>
/// <param name="clip">The clip item to append. Must not be null.</param>
/// <returns>A task representing the asynchronous operation.</returns>
/// <exception cref="ArgumentNullException">Thrown when <paramref name="clip"/> is null.</exception>
/// <exception cref="IOException">Thrown when file write fails.</exception>
public async Task AppendClipAsync(ClipItem clip)
{
    // Implementation
}
```

---

## 7. Enforce Rules (Tools & Configuration)

### 7.1 .editorconfig (Root of Project)
```ini
root = true

[*]
indent_style = space
indent_size = 4
end_of_line = crlf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.cs]
# Indentation
csharp_indent_case_contents = true
csharp_indent_switch_labels = true
csharp_indent_labels = no_change

# Spacing
csharp_space_after_colon_in_inheritance_clause = true
csharp_space_after_comma = true
csharp_space_around_binary_operators = before_and_after

# New line preferences
csharp_new_line_before_open_brace = all
csharp_new_line_before_else = true
csharp_new_line_before_catch = true
csharp_new_line_before_finally = true

# Code block preferences
csharp_prefer_braces = true:silent
csharp_prefer_simple_using_statement = true:suggestion

[*.xaml]
indent_size = 4
```

### 7.2 .csproj Analyzer Configuration
```xml
<PropertyGroup>
    <LangVersion>latest</LangVersion>
    <Nullable>enable</Nullable>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
    <AnalysisLevel>latest</AnalysisLevel>
</PropertyGroup>

<ItemGroup>
    <!-- Static code analyzers -->
    <PackageReference Include="Microsoft.CodeAnalysis.NetAnalyzers" 
                      Version="8.0.0" PrivateAssets="all" />
    <PackageReference Include="StyleCop.Analyzers" 
                      Version="1.2.0-beta.556" PrivateAssets="all" />
    
    <!-- Required packages -->
    <PackageReference Include="CommunityToolkit.Mvvm" Version="8.3.0" />
    <PackageReference Include="Serilog" Version="3.1.0" />
    <PackageReference Include="Microsoft.Extensions.DependencyInjection" Version="8.0.0" />
</ItemGroup>
```

### 7.3 stylecop.json (if using StyleCop.Analyzers)
```json
{
  "$schema": "https://raw.githubusercontent.com/DotNetAnalyzers/StyleCopAnalyzers/master/StyleCop.Analyzers/StyleCop.Analyzers.ruleset",
  "settings": {
    "orderingRules": {
      "SA1600": { "enabled": false },
      "SA1602": { "enabled": false }
    },
    "namingRules": {
      "SA1309": { "enabled": false }
    }
  }
}
```

### 7.4 Code Cleanup in Visual Studio
- Use: **Edit** → **Code Cleanup** → **Configure Code Cleanup**.
- Include: Format document + Apply naming styles + Remove unused directives.
- Keyboard shortcut: `Ctrl+K, Ctrl+E`.

---

## 8. Review Checklist (PR / Self-review)

Trước khi commit hoặc submit PR, verify:

- [ ] **Naming**: Biến/method/class có tên rõ ràng, tuân thủ PascalCase/camelCase/UPPER_CASE.
- [ ] **Formatting**: Indentation 4 spaces, line < 120 chars, consistent spacing.
- [ ] **Method size**: < 40 dòng (nếu lớn hơn → extract helper methods).
- [ ] **Class size**: < 400 dòng (nếu lớn hơn → split responsibilities).
- [ ] **Error handling**: Catch specific exceptions, log, handle gracefully.
- [ ] **Async**: Dùng async cho I/O, không block (.Result), ConfigureAwait(false) nếu không UI context.
- [ ] **Null safety**: Nullable checks đầy đủ, sử dụng null-conditional operators.
- [ ] **Comments**: Chỉ comment "why", không "what". XML doc cho public API.
- [ ] **XAML**: Compiled binding (x:Bind), no code-behind logic, consistent naming.
- [ ] **Unit tests**: Domain/service core covered by tests (xUnit + Moq recommended).
- [ ] **No magic numbers**: Hằng số có const name rõ ràng.
- [ ] **Performance**: Không unnecessary allocation, dùng struct/ValueTask khi phù hợp.
- [ ] **SOLID**: S.O.L.I.D principles tuân thủ (especially Single Responsibility).

---

## 9. Tài liệu tham khảo chính thức

- **Microsoft .NET Coding Conventions**: https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions
- **.NET Runtime Coding Guidelines**: https://github.com/dotnet/runtime/blob/main/docs/coding-guidelines/coding-style.md
- **Framework Design Guidelines** (Naming): https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/
- **WinUI 3 Best Practices**: https://learn.microsoft.com/en-us/windows/apps/winui/winui3/
- **MVVM Toolkit**: https://learn.microsoft.com/en-us/dotnet/communitytoolkit/mvvm/
- **Clean Code by Robert C. Martin**
- **SOLID Principles**: https://en.wikipedia.org/wiki/SOLID

---

## 10. Kết luận

Tuân thủ tài liệu này, codebase DailyClip sẽ:
- ✅ **Dễ đọc & bảo trì**: Naming/formatting nhất quán.
- ✅ **Dễ test**: Clean Architecture tách biệt concerns.
- ✅ **Dễ mở rộng**: SOLID principles hỗ trợ thêm feature không break.
- ✅ **Performance**: Async/await & efficient memory usage.
- ✅ **Professional**: Meet industry standards.

Chúc bạn code clean! 🚀
