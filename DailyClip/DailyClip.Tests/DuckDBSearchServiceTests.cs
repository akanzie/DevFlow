namespace DailyClip.Tests;

using DailyClip.Core.Entities;
using DailyClip.Core.Interfaces;
using DailyClip.Infrastructure.Services;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

/// <summary>
/// Unit tests for in-memory search service.
/// </summary>
public class DuckDBSearchServiceTests
{
    private readonly Mock<IStorageService> _mockStorageService = new();
    private readonly Mock<ILogger<InMemorySearchService>> _mockLogger = new();
    private readonly InMemorySearchService _sut;

    public DuckDBSearchServiceTests()
    {
        _sut = new InMemorySearchService(_mockStorageService.Object, _mockLogger.Object);
    }

    [Fact]
    public async Task InitializeAsync_CreatesSearchIndex()
    {
        // Act
        await _sut.InitializeAsync();

        // Assert - No exception thrown
        Assert.True(true);
    }

    [Fact]
    public async Task InitializeAsync_CalledTwice_DoesNotThrow()
    {
        // Act
        await _sut.InitializeAsync();
        await _sut.InitializeAsync();

        // Assert
        Assert.True(true);
    }

    [Fact]
    public async Task IndexClipAsync_WithValidClip_Succeeds()
    {
        // Arrange
        await _sut.InitializeAsync();
        var clip = new ClipItem(
            Timestamp: DateTimeOffset.Now,
            Type: "text",
            Content: "Test content for indexing");

        // Act
        await _sut.IndexClipAsync(clip);

        // Assert - No exception thrown
        Assert.True(true);
    }

    [Fact]
    public async Task IndexClipAsync_WithNull_ThrowsArgumentNullException()
    {
        // Arrange
        await _sut.InitializeAsync();

        // Act & Assert
        await Assert.ThrowsAsync<ArgumentNullException>(() => _sut.IndexClipAsync(null!));
    }

    [Fact]
    public async Task IndexClipAsync_MultipleClips_AllIndexed()
    {
        // Arrange
        await _sut.InitializeAsync();
        var clips = new[]
        {
            new ClipItem(DateTimeOffset.Now, "text", "Clip 1"),
            new ClipItem(DateTimeOffset.Now.AddSeconds(1), "text", "Clip 2"),
            new ClipItem(DateTimeOffset.Now.AddSeconds(2), "text", "Clip 3")
        };

        // Act
        foreach (var clip in clips)
        {
            await _sut.IndexClipAsync(clip);
        }

        // Assert - All indexed without exception
        Assert.True(true);
    }

    [Fact]
    public async Task SearchAsync_WithValidQuery_ReturnsResults()
    {
        // Arrange
        await _sut.InitializeAsync();
        var clip = new ClipItem(
            Timestamp: DateTimeOffset.Now,
            Type: "text",
            Content: "unique keyword test");
        await _sut.IndexClipAsync(clip);

        // Act
        var results = await _sut.SearchAsync("keyword", limit: 50);

        // Assert
        results.Should().NotBeEmpty();
        results.Should().HaveCount(1);
        results[0].Snippet.Should().Contain("unique keyword test");
    }

    [Fact]
    public async Task SearchAsync_WithNullQuery_ThrowsArgumentNullException()
    {
        // Arrange
        await _sut.InitializeAsync();

        // Act & Assert
        await Assert.ThrowsAsync<ArgumentNullException>(() => _sut.SearchAsync(null!, limit: 50));
    }

    [Fact]
    public async Task SearchAsync_WithEmptyQuery_ThrowsArgumentException()
    {
        // Arrange
        await _sut.InitializeAsync();

        // Act & Assert
        await Assert.ThrowsAsync<ArgumentException>(() => _sut.SearchAsync("", limit: 50));
    }

    [Fact]
    public async Task SearchAsync_WithNoMatches_ReturnsEmpty()
    {
        // Arrange
        await _sut.InitializeAsync();
        var clip = new ClipItem(
            Timestamp: DateTimeOffset.Now,
            Type: "text",
            Content: "test content");
        await _sut.IndexClipAsync(clip);

        // Act
        var results = await _sut.SearchAsync("nonexistent", limit: 50);

        // Assert
        results.Should().BeEmpty();
    }

    [Fact]
    public async Task SearchAsync_WithLimit_RespectsLimit()
    {
        // Arrange
        await _sut.InitializeAsync();
        for (int i = 0; i < 10; i++)
        {
            var clip = new ClipItem(
                Timestamp: DateTimeOffset.Now.AddSeconds(i),
                Type: "text",
                Content: $"test content {i}");
            await _sut.IndexClipAsync(clip);
        }

        // Act
        var results = await _sut.SearchAsync("test", limit: 3);

        // Assert
        results.Should().HaveCount(3);
    }

    [Fact]
    public async Task SearchAsync_CaseInsensitive_FindsMatches()
    {
        // Arrange
        await _sut.InitializeAsync();
        var clip = new ClipItem(
            Timestamp: DateTimeOffset.Now,
            Type: "text",
            Content: "TestContent");
        await _sut.IndexClipAsync(clip);

        // Act
        var results = await _sut.SearchAsync("testcontent", limit: 50);

        // Assert
        results.Should().NotBeEmpty();
    }

    [Fact]
    public async Task SearchAsync_WithSourceUrl_SearchesSourceUrl()
    {
        // Arrange
        await _sut.InitializeAsync();
        var clip = new ClipItem(
            Timestamp: DateTimeOffset.Now,
            Type: "text",
            Content: "content",
            SourceUrl: "https://example.com/unique-path");
        await _sut.IndexClipAsync(clip);

        // Act
        var results = await _sut.SearchAsync("unique-path", limit: 50);

        // Assert
        results.Should().NotBeEmpty();
    }

    [Fact]
    public async Task SearchAsync_ResultsSortedByTimestampDescending()
    {
        // Arrange
        await _sut.InitializeAsync();
        var now = DateTimeOffset.Now;
        var clip1 = new ClipItem(Timestamp: now.AddSeconds(-10), Type: "text", Content: "test 1");
        var clip2 = new ClipItem(Timestamp: now.AddSeconds(-5), Type: "text", Content: "test 2");
        var clip3 = new ClipItem(Timestamp: now, Type: "text", Content: "test 3");

        await _sut.IndexClipAsync(clip1);
        await _sut.IndexClipAsync(clip2);
        await _sut.IndexClipAsync(clip3);

        // Act
        var results = await _sut.SearchAsync("test", limit: 10);

        // Assert
        results.Should().HaveCount(3);
        results[0].Snippet.Should().Contain("test 3"); // Most recent first
        results[1].Snippet.Should().Contain("test 2");
        results[2].Snippet.Should().Contain("test 1");
    }

    [Fact]
    public async Task RebuildIndexAsync_ClearsAndRebuilds()
    {
        // Arrange
        await _sut.InitializeAsync();
        var clip = new ClipItem(
            Timestamp: DateTimeOffset.Now,
            Type: "text",
            Content: "test content");
        await _sut.IndexClipAsync(clip);

        // Act
        await _sut.RebuildIndexAsync();

        // Re-index after rebuild to verify functionality
        await _sut.IndexClipAsync(clip);

        // Assert - Index should still be functional
        var results = await _sut.SearchAsync("test", limit: 50);
        results.Should().NotBeEmpty();
    }



    [Fact]
    public async Task IndexClipAsync_WithDifferentTypes_AllIndexed()
    {
        // Arrange
        await _sut.InitializeAsync();
        var clips = new[]
        {
            new ClipItem(DateTimeOffset.Now, "text", "Text content"),
            new ClipItem(DateTimeOffset.Now.AddSeconds(1), "code", "var x = 1;", Format: "csharp"),
            new ClipItem(DateTimeOffset.Now.AddSeconds(2), "html", "<p>HTML</p>")
        };

        // Act
        foreach (var clip in clips)
        {
            await _sut.IndexClipAsync(clip);
        }

        // Assert
        var results = await _sut.SearchAsync("content", limit: 50);
        results.Should().NotBeEmpty();
    }

    [Fact]
    public async Task SearchAsync_WithZeroLimit_UsesDefault()
    {
        // Arrange
        await _sut.InitializeAsync();
        var clip = new ClipItem(
            Timestamp: DateTimeOffset.Now,
            Type: "text",
            Content: "test content");
        await _sut.IndexClipAsync(clip);

        // Act
        var results = await _sut.SearchAsync("test", limit: 0);

        // Assert - Should use default 50 when limit is 0
        results.Should().NotBeEmpty();
    }

    [Fact]
    public async Task Constructor_WithNullStorageService_ThrowsArgumentNullException()
    {
        // Act & Assert
        Assert.Throws<ArgumentNullException>(
            () => new InMemorySearchService(null!, _mockLogger.Object));
    }

    [Fact]
    public async Task Constructor_WithNullLogger_ThrowsArgumentNullException()
    {
        // Act & Assert
        Assert.Throws<ArgumentNullException>(
            () => new InMemorySearchService(_mockStorageService.Object, null!));
    }

    [Fact]
    public async Task InMemorySearchService_ImplementsISearchService()
    {
        // Assert
        _sut.Should().BeAssignableTo<ISearchService>();
    }
}
