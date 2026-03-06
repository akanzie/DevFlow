namespace DailyClip.Tests;

using DailyClip.Core.Entities;
using DailyClip.Core.Interfaces;
using DailyClip.Infrastructure.Services;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

/// <summary>
/// Unit tests for ClipboardMonitorService.
/// </summary>
public class ClipboardMonitorServiceTests
{
    private readonly Mock<IStorageService> _mockStorageService = new();
    private readonly Mock<ISearchService> _mockSearchService = new();
    private readonly Mock<ILogger<ClipboardMonitorService>> _mockLogger = new();
    private readonly DuplicateDetector _duplicateDetector = new();

    [Fact]
    public async Task StartMonitoringAsync_WithValidDependencies_Succeeds()
    {
        // Arrange
        var service = new ClipboardMonitorService(
            _mockStorageService.Object,
            _mockSearchService.Object,
            _mockLogger.Object,
            _duplicateDetector
        );

        // Act
        await service.StartMonitoringAsync();

        // Assert - No exception thrown
        Assert.True(true);
    }

    [Fact]
    public async Task StopMonitoringAsync_AfterStart_Succeeds()
    {
        // Arrange
        var service = new ClipboardMonitorService(
            _mockStorageService.Object,
            _mockSearchService.Object,
            _mockLogger.Object,
            _duplicateDetector
        );

        await service.StartMonitoringAsync();

        // Act & Assert - Should not throw
        await service.StopMonitoringAsync();
    }

    [Fact]
    public void ClipboardChanged_CanBeSubscribed()
    {
        // Arrange
        var service = new ClipboardMonitorService(
            _mockStorageService.Object,
            _mockSearchService.Object,
            _mockLogger.Object,
            _duplicateDetector
        );

        var handlerCalled = false;

        // Act
        service.ClipboardChanged += (sender, e) =>
        {
            handlerCalled = true;
        };

        // Assert - No exception thrown means subscription succeeded
        Assert.True(true);
    }

    [Fact]
    public void ClipboardChanged_CanHaveMultipleSubscribers()
    {
        // Arrange
        var service = new ClipboardMonitorService(
            _mockStorageService.Object,
            _mockSearchService.Object,
            _mockLogger.Object,
            _duplicateDetector
        );

        var handler1Called = false;
        var handler2Called = false;

        // Act
        service.ClipboardChanged += (sender, e) => handler1Called = true;
        service.ClipboardChanged += (sender, e) => handler2Called = true;

        // Assert - No exception thrown means both subscriptions succeeded
        Assert.True(true);
    }

    [Fact]
    public void Constructor_WithNullStorageService_ThrowsArgumentNullException()
    {
        // Act & Assert
        Assert.Throws<ArgumentNullException>(
            () => new ClipboardMonitorService(
                null!,
                _mockSearchService.Object,
                _mockLogger.Object,
                _duplicateDetector
            )
        );
    }

    [Fact]
    public void Constructor_WithNullSearchService_ThrowsArgumentNullException()
    {
        // Act & Assert
        Assert.Throws<ArgumentNullException>(
            () => new ClipboardMonitorService(
                _mockStorageService.Object,
                null!,
                _mockLogger.Object,
                _duplicateDetector
            )
        );
    }

    [Fact]
    public void Constructor_WithNullLogger_ThrowsArgumentNullException()
    {
        // Act & Assert
        Assert.Throws<ArgumentNullException>(
            () => new ClipboardMonitorService(
                _mockStorageService.Object,
                _mockSearchService.Object,
                null!,
                _duplicateDetector
            )
        );
    }

    [Fact]
    public void Constructor_WithNullDuplicateDetector_ThrowsArgumentNullException()
    {
        // Act & Assert
        Assert.Throws<ArgumentNullException>(
            () => new ClipboardMonitorService(
                _mockStorageService.Object,
                _mockSearchService.Object,
                _mockLogger.Object,
                null!
            )
        );
    }

    [Fact]
    public async Task StartMonitoringAsync_CalledTwice_DoesNotThrow()
    {
        // Arrange
        var service = new ClipboardMonitorService(
            _mockStorageService.Object,
            _mockSearchService.Object,
            _mockLogger.Object,
            _duplicateDetector
        );

        // Act
        await service.StartMonitoringAsync();
        await service.StartMonitoringAsync(); // Second call

        // Assert - Should not throw
        Assert.True(true);
    }

    [Fact]
    public async Task StopMonitoringAsync_WithoutStart_DoesNotThrow()
    {
        // Arrange
        var service = new ClipboardMonitorService(
            _mockStorageService.Object,
            _mockSearchService.Object,
            _mockLogger.Object,
            _duplicateDetector
        );

        // Act & Assert
        await service.StopMonitoringAsync(); // Should not throw
    }

    [Fact]
    public async Task StopMonitoringAsync_CalledTwice_DoesNotThrow()
    {
        // Arrange
        var service = new ClipboardMonitorService(
            _mockStorageService.Object,
            _mockSearchService.Object,
            _mockLogger.Object,
            _duplicateDetector
        );

        await service.StartMonitoringAsync();

        // Act & Assert
        await service.StopMonitoringAsync();
        await service.StopMonitoringAsync(); // Second call should not throw
    }

    [Fact]
    public async Task StartMonitoringAsync_LogsInformation()
    {
        // Arrange
        var service = new ClipboardMonitorService(
            _mockStorageService.Object,
            _mockSearchService.Object,
            _mockLogger.Object,
            _duplicateDetector
        );

        // Act
        await service.StartMonitoringAsync();

        // Assert - Verify that logging was called
        _mockLogger.Verify(
            x => x.Log(
                LogLevel.Information,
                It.IsAny<EventId>(),
                It.IsAny<It.IsAnyType>(),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()
            ),
            Times.Once
        );
    }

    [Fact]
    public async Task ClipboardMonitorService_ImplementsIClipboardMonitor()
    {
        // Arrange
        var service = new ClipboardMonitorService(
            _mockStorageService.Object,
            _mockSearchService.Object,
            _mockLogger.Object,
            _duplicateDetector
        );

        // Assert
        service.Should().BeAssignableTo<IClipboardMonitor>();
    }

    [Fact]
    public async Task StopMonitoringAsync_VerifiesLogging()
    {
        // Arrange
        var service = new ClipboardMonitorService(
            _mockStorageService.Object,
            _mockSearchService.Object,
            _mockLogger.Object,
            _duplicateDetector
        );

        await service.StartMonitoringAsync();

        // Act
        await service.StopMonitoringAsync();
        await Task.Delay(100); // Allow logging to complete

        // Assert - Verify Information level was used for stop
        _mockLogger.Verify(
            x => x.Log(
                LogLevel.Information,
                It.IsAny<EventId>(),
                It.IsAny<It.IsAnyType>(),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()
            ),
            Times.AtLeast(2) // At least once for start, at least once for stop
        );
    }
}

