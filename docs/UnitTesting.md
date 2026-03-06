# Tài liệu Hướng dẫn Unit Test (Unit Testing Guidelines)  
**Dự án:** DailyClip  
**Phiên bản:** 1.0  
**Áp dụng cho:** Toàn bộ codebase testable (Domain, Application, Infrastructure layers)  
**Mục tiêu:** Đảm bảo chất lượng code, dễ refactor, phát hiện bug sớm. Ưu tiên **unit test nhanh, độc lập, dễ đọc**.

---

## 1. Chiến lược Test theo Clean Architecture

Clean Architecture → test từ trong ra ngoài (inside-out testing):

| Layer              | Loại test chính          | Mocks cần thiết? | Công cụ khuyến nghị          | Coverage mục tiêu |
|--------------------|--------------------------|------------------|------------------------------|-------------------|
| **Domain**         | Pure unit tests          | Không            | xUnit                        | >95%              |
| **Application**    | Unit tests (use cases)   | Có (interfaces)  | xUnit + Moq                  | >85%              |
| **Infrastructure** | Unit + nhẹ integration   | Có (nếu có thể)  | xUnit + Moq + InMemory DuckDB | >70% (ưu tiên critical paths) |
| **Presentation**   | ViewModel tests          | Có (services)    | xUnit + Moq + CommunityToolkit | >80% cho ViewModel logic |
| **UI (WinUI Views)** | Không unit test          | -                | -                            | Manual / UI test nếu cần |

**Thứ tự ưu tiên viết test**:
1. Domain logic (entities, value objects, business rules).
2. Application services / use cases.
3. ViewModels (MVVM).
4. Infrastructure (storage, search) – dùng in-memory hoặc mock.

**Không test**:
- Framework code (WinUI binding, Windows API trực tiếp).
- UI rendering (dùng UI testing nếu cần, ví dụ Appium hoặc WinAppDriver sau này).

---

## 2. Công cụ & Setup

Thêm vào solution (tạo project riêng: `DailyClip.Tests` – Class Library .NET 9):

### 2.1 NuGet Packages

```xml
<ItemGroup>
  <!-- Test framework -->
  <PackageReference Include="xunit" Version="2.9.2" />
  <PackageReference Include="xunit.runner.visualstudio" Version="2.8.2" PrivateAssets="all" />
  <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.11.1" />
  
  <!-- Mocking & Assertions -->
  <PackageReference Include="Moq" Version="4.20.72" />
  <PackageReference Include="FluentAssertions" Version="7.0.0" />
  
  <!-- Tools -->
  <PackageReference Include="CommunityToolkit.Mvvm" Version="8.3.2" />
  <PackageReference Include="DuckDB.NET.Data" Version="1.0.0" />
  
  <!-- Coverage (optional) -->
  <PackageReference Include="coverlet.collector" Version="6.0.0" PrivateAssets="all" />
</ItemGroup>
```

### 2.2 Project Structure
```
DailyClip/
├── DailyClip.Core/                (Domain + Application layer)
├── DailyClip.Infrastructure/      (Infrastructure layer)
├── DailyClip.Presentation/        (Presentation layer - WinUI 3)
├── DailyClip.Tests/               (Unit tests - NEW)
│   ├── Domain/
│   │   └── Entities/
│   │       └── ClipItemTests.cs
│   ├── Application/
│   │   └── Services/
│   │       └── ClipboardMonitorServiceTests.cs
│   ├── Infrastructure/
│   │   └── Services/
│   │       └── DuckDBSearchServiceTests.cs
│   └── Presentation/
│       └── ViewModels/
│           └── QuickSearchViewModelTests.cs
└── DailyClip.sln
```

### 2.3 Test Runner
```bash
# Run all tests
dotnet test

# Run with coverage
dotnet test /p:CollectCoverage=true /p:CoverageFormat=opencover

# Run specific test file
dotnet test --filter "FullyQualifiedName=DailyClip.Tests.Domain.Entities.ClipItemTests"

# Watch mode (VS extension: Test Explorer Live Unit Testing)
```

---

## 3. Best Practices chung

### 3.1 AAA Pattern (Arrange – Act – Assert)
```csharp
[Fact]
public void ExampleTest()
{
    // Arrange: Set up test data & mocks
    var service = new ExampleService();
    var input = new ExampleInput { Value = 42 };

    // Act: Execute the method under test
    var result = service.Process(input);

    // Assert: Verify the result
    result.Should().Be(42);
}
```

### 3.2 Test Naming Convention
Format: `[MethodUnderTest]_[Scenario]_[ExpectedResult]`

```csharp
// ✓ Good (clear intent)
public void AppendClipAsync_DuplicateContentWithin10s_SkipsSave()
public void Search_EmptyQuery_ReturnsEmpty()
public void ClipItem_InvalidTimestamp_ThrowsArgumentException()

// ✗ Bad (unclear)
public void Test1()
public void AppendClipAsyncTest()
public void TestSearch()
```

### 3.3 One Assertion Per Concept
```csharp
// ✓ Better: Test one behavior
[Fact]
public void SaveClip_Success_ReturnsClipId()
{
    var result = _service.Save(clip);
    result.Should().NotBeEmpty(); // Assert ID generated
}

[Fact]
public void SaveClip_Success_UpdatesLastSavedTime()
{
    var before = DateTimeOffset.Now;
    _service.Save(clip);
    var after = DateTimeOffset.Now;
    
    _service.LastSaved.Should().BeOnOrAfter(before).And.BeOnOrBefore(after);
}

// ✗ Bad: Multiple behaviors in one test
[Fact]
public void SaveClipTest()
{
    var result = _service.Save(clip);
    result.Should().NotBeEmpty();
    _service.LastSaved.Should().NotBe(default);
    // ...many more asserts
}
```

### 3.4 Async Tests
```csharp
// ✓ Always use async/await (never .Result or .Wait())
[Fact]
public async Task AppendClipAsync_WithValidClip_SavesSuccessfully()
{
    var clip = new ClipItem(DateTimeOffset.Now, "text", "content");
    
    await _service.AppendClipAsync(clip);
    
    _storageMock.Verify(s => s.AppendAsync(It.IsAny<ClipItem>()), Times.Once);
}

// ✗ Never do this
var result = _service.AppendClipAsync(clip).Result; // Deadlock risk!
```

### 3.5 Test Parameterization
```csharp
// ✓ Use [Theory] + [InlineData] for multiple scenarios
[Theory]
[InlineData("")]
[InlineData(null)]
[InlineData("   ")]
public void AppendClipAsync_EmptyOrWhitespace_ThrowsArgumentException(string content)
{
    FluentActions.Invoking(() => new ClipItem(DateTimeOffset.Now, "text", content))
        .Should().Throw<ArgumentException>();
}

// ✓ Or [MemberData] for complex data
[Theory]
[MemberData(nameof(GetInvalidClips))]
public void IsValid_InvalidClip_ReturnsFalse(ClipItem clip)
{
    clip.IsValid().Should().BeFalse();
}

public static IEnumerable<object[]> GetInvalidClips => new List<object[]>
{
    new object[] { new ClipItem(default, "text", "content") }, // Invalid timestamp
    new object[] { new ClipItem(DateTimeOffset.Now, "text", "") }, // Empty content
};
```

### 3.6 Mock Best Practices
```csharp
// ✓ Mock only interfaces
var storageMock = new Mock<IStorageService>();

// ✓ Setup return values
storageMock
    .Setup(s => s.GetClipsAsync(It.IsAny<DateOnly>()))
    .ReturnsAsync(new List<ClipItem> { new(DateTimeOffset.Now, "text", "code") });

// ✓ Verify method calls
storageMock.Verify(s => s.SaveAsync(It.IsAny<ClipItem>()), Times.Once);
storageMock.Verify(s => s.SaveAsync(It.Is<ClipItem>(c => c.Content == "specific")), Times.Once);

// ✗ Don't mock concrete classes (unless absolutely necessary)
var fakeService = new Mock<ConcreteClipboardService>(); // Bad!

// ✗ Don't over-verify (brittle tests)
storageMock.Verify(s => s.InternalMethodA(), Times.Once); // Bad
```

### 3.7 FluentAssertions
```csharp
// ✓ Readable assertions
result.Should().NotBeNull()
    .And.BeOfType<ClipItem>()
    .Which.Content.Should().StartWith("async");

results.Should()
    .HaveCount(5)
    .And.ContainSingle(r => r.Type == "text");

// ✓ Exception testing
FluentActions.Invoking(() => service.Process(null))
    .Should().Throw<ArgumentNullException>()
    .WithMessage("*clip*");
```

### 3.8 IDisposable for Resource Cleanup
```csharp
public class DuckDBSearchServiceTests : IDisposable
{
    private readonly DuckDBSearchService _sut;

    public DuckDBSearchServiceTests()
    {
        _sut = new DuckDBSearchService(":memory:");
    }

    [Fact]
    public async Task IndexAsync_ValidClip_Indexed()
    {
        // Test
    }

    public void Dispose()
    {
        _sut?.Dispose();
    }
}
```

---

## 4. Unit Test Examples cụ thể cho DailyClip

### 4.1 Domain Layer: Entity Tests (Pure, no mock)

```csharp
// DailyClip.Tests/Domain/Entities/ClipItemTests.cs
using Xunit;
using FluentAssertions;
using DailyClip.Core.Entities;

namespace DailyClip.Tests.Domain.Entities;

public class ClipItemTests
{
    [Fact]
    public void Constructor_ValidArguments_CreatesSuccessfully()
    {
        // Arrange & Act
        var clip = new ClipItem(DateTimeOffset.Now, "text", "some code");

        // Assert
        clip.Content.Should().Be("some code");
        clip.Type.Should().Be("text");
    }

    [Fact]
    public void Constructor_NullContent_ThrowsArgumentNullException()
    {
        // Act & Assert
        FluentActions.Invoking(() => 
            new ClipItem(DateTimeOffset.Now, "text", null!))
            .Should().Throw<ArgumentNullException>()
            .WithParameterName("content");
    }

    [Fact]
    public void Constructor_DefaultTimestamp_ThrowsArgumentException()
    {
        // Act & Assert
        FluentActions.Invoking(() => 
            new ClipItem(default, "text", "content"))
            .Should().Throw<ArgumentException>()
            .WithMessage("*timestamp*");
    }

    [Fact]
    public void IsDuplicate_SameContentWithin10Seconds_ReturnsTrue()
    {
        // Arrange
        var now = DateTimeOffset.Now;
        var clip1 = new ClipItem(now, "text", "const API_KEY = '...'");
        var clip2 = new ClipItem(now.AddSeconds(5), "text", "const API_KEY = '...'");

        // Act & Assert
        clip1.IsDuplicate(clip2).Should().BeTrue();
    }

    [Fact]
    public void IsDuplicate_DifferentContent_ReturnsFalse()
    {
        // Arrange
        var now = DateTimeOffset.Now;
        var clip1 = new ClipItem(now, "text", "content A");
        var clip2 = new ClipItem(now.AddSeconds(5), "text", "content B");

        // Act & Assert
        clip1.IsDuplicate(clip2).Should().BeFalse();
    }

    [Fact]
    public void IsDuplicate_SameContentAfter10Seconds_ReturnsFalse()
    {
        // Arrange (deduplicate window is 10s)
        var now = DateTimeOffset.Now;
        var clip1 = new ClipItem(now, "text", "content");
        var clip2 = new ClipItem(now.AddSeconds(11), "text", "content");

        // Act & Assert
        clip1.IsDuplicate(clip2).Should().BeFalse();
    }
}
```

### 4.2 Application Layer: Service Tests (with Mocks)

```csharp
// DailyClip.Tests/Application/Services/ClipboardMonitorServiceTests.cs
using Xunit;
using Moq;
using FluentAssertions;
using DailyClip.Core.Entities;
using DailyClip.Core.Interfaces;
using DailyClip.Application.Services;

namespace DailyClip.Tests.Application.Services;

public class ClipboardMonitorServiceTests
{
    private readonly Mock<IStorageService> _storageMock;
    private readonly Mock<ISearchService> _searchMock;
    private readonly Mock<ILogger<ClipboardMonitorService>> _loggerMock;
    private readonly ClipboardMonitorService _sut;

    public ClipboardMonitorServiceTests()
    {
        _storageMock = new Mock<IStorageService>();
        _searchMock = new Mock<ISearchService>();
        _loggerMock = new Mock<ILogger<ClipboardMonitorService>>();

        _sut = new ClipboardMonitorService(
            _storageMock.Object,
            _searchMock.Object,
            _loggerMock.Object);
    }

    [Fact]
    public async Task ProcessClipboardTextAsync_NewContent_SavesAndIndex()
    {
        // Arrange
        string content = "async Task Main() { }";
        string? sourceUrl = "https://github.com/example";
        
        _storageMock
            .Setup(s => s.AppendClipAsync(It.IsAny<ClipItem>()))
            .Returns(Task.CompletedTask);
        
        _searchMock
            .Setup(s => s.IndexClipAsync(It.IsAny<ClipItem>()))
            .Returns(Task.CompletedTask);

        // Act
        await _sut.ProcessClipboardTextAsync(content, sourceUrl);

        // Assert: Verify both storage and search were called
        _storageMock.Verify(
            s => s.AppendClipAsync(It.Is<ClipItem>(c => 
                c.Content == content && c.SourceUrl == sourceUrl && c.Type == "text")),
            Times.Once);

        _searchMock.Verify(
            s => s.IndexClipAsync(It.IsAny<ClipItem>()),
            Times.Once);
    }

    [Fact]
    public async Task ProcessClipboardTextAsync_DuplicateWithin10Seconds_SkipsSave()
    {
        // Arrange
        var content = "duplicate code";
        var clip = new ClipItem(DateTimeOffset.Now, "text", content);
        
        _sut.LastProcessedClip = clip; // Simulate previous clip

        _storageMock.Reset(); // Should not be called

        // Act
        await _sut.ProcessClipboardTextAsync(content, null);

        // Assert: Storage should NOT be called for duplicate
        _storageMock.Verify(
            s => s.AppendClipAsync(It.IsAny<ClipItem>()),
            Times.Never);
    }

    [Fact]
    public async Task ProcessClipboardTextAsync_NullContent_ThrowsArgumentNullException()
    {
        // Act & Assert
        await FluentActions.Invoking(() => 
            _sut.ProcessClipboardTextAsync(null!, null))
            .Should().ThrowAsync<ArgumentNullException>();
    }
}
```

### 4.3 Infrastructure Layer: DuckDB Search Tests (In-memory)

```csharp
// DailyClip.Tests/Infrastructure/Services/DuckDBSearchServiceTests.cs
using Xunit;
using FluentAssertions;
using DailyClip.Core.Entities;
using DailyClip.Infrastructure.Services;

namespace DailyClip.Tests.Infrastructure.Services;

public class DuckDBSearchServiceTests : IDisposable
{
    private readonly DuckDBSearchService _sut;
    private readonly string _dbPath = ":memory:"; // In-memory for fast tests

    public DuckDBSearchServiceTests()
    {
        _sut = new DuckDBSearchService(_dbPath);
        _sut.InitializeAsync().GetAwaiter().GetResult();
    }

    [Fact]
    public async Task IndexClipAsync_ValidClip_IndexedSuccessfully()
    {
        // Arrange
        var clip = new ClipItem(
            DateTimeOffset.Now,
            "text",
            "async await pattern in C#");

        // Act
        await _sut.IndexClipAsync(clip);
        var results = await _sut.SearchAsync("async", 10);

        // Assert
        results.Should().HaveCount(1);
        results[0].Snippet.Should().Contain("async");
    }

    [Theory]
    [InlineData("async await")]
    [InlineData("pattern")]
    [InlineData("C#")]
    public async Task SearchAsync_WithMatchingKeyword_ReturnsResults(string query)
    {
        // Arrange
        var clip = new ClipItem(
            DateTimeOffset.Now,
            "text",
            "async await pattern in C#");
        
        await _sut.IndexClipAsync(clip);

        // Act
        var results = await _sut.SearchAsync(query, 10);

        // Assert
        results.Should().NotBeEmpty().And.ContainSingle();
    }

    [Fact]
    public async Task SearchAsync_NoMatches_ReturnsEmpty()
    {
        // Arrange
        var clip = new ClipItem(DateTimeOffset.Now, "text", "C# code");
        await _sut.IndexClipAsync(clip);

        // Act
        var results = await _sut.SearchAsync("Python", 10);

        // Assert
        results.Should().BeEmpty();
    }

    [Fact]
    public async Task SearchAsync_MultipleClips_RanksByRelevance()
    {
        // Arrange: Index multiple clips with varying relevance
        var clips = new[]
        {
            new ClipItem(DateTimeOffset.Now.AddSeconds(-1), "text", "async async async"),
            new ClipItem(DateTimeOffset.Now.AddSeconds(-2), "text", "async pattern"),
            new ClipItem(DateTimeOffset.Now.AddSeconds(-3), "text", "pattern matching"),
        };

        foreach (var clip in clips)
            await _sut.IndexClipAsync(clip);

        // Act
        var results = await _sut.SearchAsync("async", 10);

        // Assert: First result should match "async" best (higher score)
        results.Should().HaveCountGreaterThan(1);
        results[0].RelevanceScore.Should().BeGreaterThanOrEqualTo(results[1].RelevanceScore);
    }

    public void Dispose() => _sut?.Dispose();
}
```

### 4.4 Presentation Layer: ViewModel Tests

```csharp
// DailyClip.Tests/Presentation/ViewModels/QuickSearchViewModelTests.cs
using Xunit;
using Moq;
using FluentAssertions;
using CommunityToolkit.Mvvm.ComponentModel;
using DailyClip.Core.Entities;
using DailyClip.Core.Interfaces;
using DailyClip.Presentation.ViewModels;

namespace DailyClip.Tests.Presentation.ViewModels;

public class QuickSearchViewModelTests
{
    private readonly Mock<ISearchService> _searchMock;
    private QuickSearchViewModel _sut;

    public QuickSearchViewModelTests()
    {
        _searchMock = new Mock<ISearchService>();
        _sut = new QuickSearchViewModel(_searchMock.Object);
    }

    [Fact]
    public async Task SearchCommand_WithValidQuery_CallsSearchServiceAndUpdatesResults()
    {
        // Arrange
        var expectedResults = new List<SearchResult>
        {
            new(DateTimeOffset.Now, "async await", "/path/clip1.jsonl", "text", 0.95f),
            new(DateTimeOffset.Now, "await pattern", "/path/clip2.jsonl", "text", 0.85f),
        };

        _searchMock
            .Setup(s => s.SearchAsync("async", 50))
            .ReturnsAsync(expectedResults);

        // Act
        _sut.Query = "async";
        await _sut.SearchCommand.ExecuteAsync(null);

        // Assert
        _searchMock.Verify(s => s.SearchAsync("async", 50), Times.Once);
        _sut.Results.Should().HaveCount(2);
        _sut.Results[0].Snippet.Should().Be("async await");
    }

    [Fact]
    public async Task SearchCommand_EmptyQuery_DoesNotCallSearchService()
    {
        // Arrange
        _sut.Query = "";

        // Act
        await _sut.SearchCommand.ExecuteAsync(null);

        // Assert
        _searchMock.Verify(s => s.SearchAsync(It.IsAny<string>(), It.IsAny<int>()), Times.Never);
    }

    [Fact]
    public void Query_OnPropertyChanged_NotifiesObservers()
    {
        // Arrange
        bool notified = false;
        _sut.PropertyChanged += (sender, args) =>
        {
            if (args.PropertyName == nameof(QuickSearchViewModel.Query))
                notified = true;
        };

        // Act
        _sut.Query = "test query";

        // Assert
        notified.Should().BeTrue();
    }
}
```

---

## 5. Test Review Checklist (PR / Self-check)

Trước khi commit hoặc submit PR test, verify:

- [ ] **Naming**: Test name mô tả rõ ràng hành vi (MethodUnderTest_Scenario_Expected).
- [ ] **AAA Pattern**: Arrange-Act-Assert rõ ràng, tách biệt.
- [ ] **Single Concept**: Mỗi test chỉ kiểm tra một hành vi.
- [ ] **Async**: Không dùng `.Result` / `.Wait()`, luôn async/await.
- [ ] **Mocks**: Mock chỉ interfaces, verify số lần gọi đúng.
- [ ] **FluentAssertions**: Assertions rõ ràng, readable (`.Should().*`).
- [ ] **Independence**: Test không phụ thuộc thứ tự chạy, không shared state.
- [ ] **Coverage**: Branch & exception path được test.
- [ ] **Performance**: Test chạy < 100ms (trừ integration tests).
- [ ] **No Brittleness**: Không over-mock, không verify implementation details.

---

## 6. Running Tests & Coverage

### 6.1 Command Line
```bash
# Run all tests
dotnet test

# Run with verbose output
dotnet test --verbosity detailed

# Run specific test class
dotnet test --filter "FullyQualifiedName~ClipItemTests"

# Run and collect coverage
dotnet test /p:CollectCoverage=true /p:CoverageFormat=opencover /p:CoverageDirectory=./coverage

# Watch mode (requires extension)
dotnet watch test
```

### 6.2 Visual Studio
- **Test Explorer**: View → Test Explorer (Ctrl+E, T).
- **Run All**: Run All Tests button.
- **Debug**: Right-click test → Debug.
- **Coverage**: Help → Generate Code Coverage Results.

### 6.3 Coverage Report
```bash
# Install ReportGenerator (optional)
dotnet tool install -g dotnet-reportgenerator-globaltool

# Generate HTML report
reportgenerator -reports:./coverage/coverage.opencover.xml -targetdir:./coverage/report

# Open report
./coverage/report/index.html
```

---

## 7. Advanced Topics (Optional)

### 7.1 Test Fixtures (Reusable Setup)
```csharp
public abstract class DatabaseTestFixture : IAsyncLifetime
{
    private readonly DuckDBSearchService _db;

    public async Task InitializeAsync()
    {
        _db = new DuckDBSearchService(":memory:");
        await _db.InitializeAsync();
    }

    public async Task DisposeAsync() => await _db.DisposeAsync();
}

public class SearchServiceTests : DatabaseTestFixture
{
    [Fact]
    public async Task Test1() { /* ... */ }
}
```

### 7.2 Custom Assertions
```csharp
public static class AssertionExtensions
{
    public static void ShouldBeValidClip(this ClipItem clip)
    {
        clip.Should().NotBeNull();
        clip.Timestamp.Should().NotBe(default);
        clip.Content.Should().NotBeNullOrEmpty();
    }
}

// Usage
clip.ShouldBeValidClip();
```

### 7.3 Snapshot Testing (for complex objects)
```bash
# Nuget: Verify package
dotnet add package Verify
```

```csharp
[Fact]
public async Task SearchResults_Match_KnownSnapshot()
{
    var results = await _service.SearchAsync("query", 10);
    await Verify(results);
}
```

---

## 8. References & Further Reading

- **xUnit best practices**: https://xunit.net/docs/getting-started
- **Moq documentation**: https://github.com/devlooped/moq
- **FluentAssertions**: https://fluentassertions.com/
- **Unit Testing in C#** by Roy Osherove (book).
- **Clean Architecture by Robert C. Martin** (chapter on testing).
- Microsoft docs: https://learn.microsoft.com/en-us/dotnet/core/testing/

---

## 9. Kết luận

Unit testing cho DailyClip giúp:
- ✅ Phát hiện bug sớm (trong dev, không ở user).
- ✅ Dễ refactor an toàn (test xác nhân không break logic).
- ✅ Code được tài liệu hóa (test là ví dụ của cách dùng).
- ✅ Design tốt hơn (testable code = loosely coupled code).
- ✅ Confidence cao khi ship feature mới.

**Mục tiêu**: >85% coverage cho Domain + Application, >70% cho Infrastructure. Chúc bạn viết test hiệu quả! 🎯
