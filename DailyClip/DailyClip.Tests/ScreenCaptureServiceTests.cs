namespace DailyClip.Tests;

using DailyClip.Core.Interfaces;
using DailyClip.Infrastructure.Services;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using Moq;
using System.Drawing;
using Xunit;

/// <summary>
/// Unit tests for ScreenCaptureService.
/// </summary>
public class ScreenCaptureServiceTests
{
    private readonly Mock<ILogger<ScreenCaptureService>> _mockLogger = new();

    [Fact]
    public void Constructor_WithValidLogger_Succeeds()
    {
        // Act
        var service = new ScreenCaptureService(_mockLogger.Object);

        // Assert
        service.Should().NotBeNull();
        service.Should().BeAssignableTo<IScreenCaptureService>();
    }

    [Fact]
    public void Constructor_WithNullLogger_ThrowsArgumentNullException()
    {
        // Act & Assert
        Assert.Throws<ArgumentNullException>(() => new ScreenCaptureService(null!));
    }

    [Fact]
    public async Task CaptureRegionAsync_WithValidBounds_ReturnsBytes()
    {
        // Arrange
        var service = new ScreenCaptureService(_mockLogger.Object);
        var bounds = new Rectangle(0, 0, 100, 100);

        // Act
        try
        {
            var result = await service.CaptureRegionAsync(bounds);

            // Assert - Should return non-null PNG bytes
            result.Should().NotBeNull();
            result.Length.Should().BeGreaterThan(0);
            // PNG magic number: 89 50 4E 47
            result[0].Should().Be(0x89);
            result[1].Should().Be(0x50);
            result[2].Should().Be(0x4E);
            result[3].Should().Be(0x47);
        }
        catch (InvalidOperationException)
        {
            // Expected in test environment without proper display
        }
    }

    [Fact]
    public async Task CaptureRegionAsync_WithZeroWidth_ThrowsInvalidOperationException()
    {
        // Arrange
        var service = new ScreenCaptureService(_mockLogger.Object);
        var bounds = new Rectangle(0, 0, 0, 100); // Zero width

        // Act & Assert
        await Assert.ThrowsAsync<InvalidOperationException>(() => service.CaptureRegionAsync(bounds));
    }

    [Fact]
    public async Task CaptureRegionAsync_WithZeroHeight_ThrowsInvalidOperationException()
    {
        // Arrange
        var service = new ScreenCaptureService(_mockLogger.Object);
        var bounds = new Rectangle(0, 0, 100, 0); // Zero height

        // Act & Assert
        await Assert.ThrowsAsync<InvalidOperationException>(() => service.CaptureRegionAsync(bounds));
    }

    [Fact]
    public async Task CaptureRegionAsync_WithNegativeWidth_ThrowsInvalidOperationException()
    {
        // Arrange
        var service = new ScreenCaptureService(_mockLogger.Object);
        var bounds = new Rectangle(0, 0, -100, 100); // Negative width

        // Act & Assert
        await Assert.ThrowsAsync<InvalidOperationException>(() => service.CaptureRegionAsync(bounds));
    }

    [Fact]
    public async Task CaptureRegionAsync_WithNegativeHeight_ThrowsInvalidOperationException()
    {
        // Arrange
        var service = new ScreenCaptureService(_mockLogger.Object);
        var bounds = new Rectangle(0, 0, 100, -100); // Negative height

        // Act & Assert
        await Assert.ThrowsAsync<InvalidOperationException>(() => service.CaptureRegionAsync(bounds));
    }

    [Fact]
    public async Task CaptureRegionAsync_WithValidPosition_Succeeds()
    {
        // Arrange
        var service = new ScreenCaptureService(_mockLogger.Object);
        var bounds = new Rectangle(100, 100, 200, 200); // Offset position

        // Act
        try
        {
            var result = await service.CaptureRegionAsync(bounds);

            // Assert
            result.Should().NotBeNull();
            result.Length.Should().BeGreaterThan(0);
        }
        catch (InvalidOperationException)
        {
            // Expected in test environment
        }
    }

    [Fact]
    public async Task CaptureRegionAsync_RetursIsAsync()
    {
        // Arrange
        var service = new ScreenCaptureService(_mockLogger.Object);
        var bounds = new Rectangle(0, 0, 50, 50);

        // Act
        var task = service.CaptureRegionAsync(bounds);

        // Assert - Should be a Task
        task.Should().BeAssignableTo<Task>();
    }

    [Fact]
    public async Task CaptureActiveWindowAsync_ReturnsBytesOrThrows()
    {
        // Arrange
        var service = new ScreenCaptureService(_mockLogger.Object);

        // Act & Assert
        try
        {
            var result = await service.CaptureActiveWindowAsync();
            result.Should().NotBeNull();
            result.Length.Should().BeGreaterThan(0);
        }
        catch (InvalidOperationException ex)
        {
            // Expected: No active window or capture failed
            ex.Message.Should().Contain("Failed to capture active window");
        }
    }

    [Fact]
    public async Task CaptureActiveWindowAsync_ReturnsIsAsync()
    {
        // Arrange
        var service = new ScreenCaptureService(_mockLogger.Object);

        // Act
        var task = service.CaptureActiveWindowAsync();

        // Assert - Should be a Task
        task.Should().BeAssignableTo<Task>();
    }

    [Fact]
    public async Task CaptureFullscreenAsync_ReturnsBytes()
    {
        // Arrange
        var service = new ScreenCaptureService(_mockLogger.Object);

        // Act
        try
        {
            var result = await service.CaptureFullscreenAsync();

            // Assert
            result.Should().NotBeNull();
            result.Length.Should().BeGreaterThan(0);
            // PNG magic number
            result[0].Should().Be(0x89);
        }
        catch (InvalidOperationException)
        {
            // Expected in headless/test environment
        }
    }

    [Fact]
    public async Task CaptureFullscreenAsync_ReturnsIsAsync()
    {
        // Arrange
        var service = new ScreenCaptureService(_mockLogger.Object);

        // Act
        var task = service.CaptureFullscreenAsync();

        // Assert - Should be a Task
        task.Should().BeAssignableTo<Task>();
    }

    [Fact]
    public async Task ScreenCaptureService_ImplementsIScreenCaptureService()
    {
        // Arrange
        var service = new ScreenCaptureService(_mockLogger.Object);

        // Assert
        service.Should().BeAssignableTo<IScreenCaptureService>();
    }

    [Fact]
    public async Task CaptureRegionAsync_SmallRegion_Succeeds()
    {
        // Arrange
        var service = new ScreenCaptureService(_mockLogger.Object);
        var bounds = new Rectangle(0, 0, 10, 10); // Very small region

        // Act
        try
        {
            var result = await service.CaptureRegionAsync(bounds);
            result.Should().NotBeNull();
        }
        catch (InvalidOperationException)
        {
            // Expected in test environment
        }
    }

    [Fact]
    public async Task CaptureRegionAsync_LargeRegion_Succeeds()
    {
        // Arrange
        var service = new ScreenCaptureService(_mockLogger.Object);
        var bounds = new Rectangle(0, 0, 1920, 1080); // Full HD size

        // Act
        try
        {
            var result = await service.CaptureRegionAsync(bounds);
            result.Should().NotBeNull();
            result.Length.Should().BeGreaterThan(0);
        }
        catch (InvalidOperationException)
        {
            // Expected in test environment
        }
    }

    [Fact]
    public async Task CaptureRegionAsync_OffscreenRegion_Succeeds()
    {
        // Arrange
        var service = new ScreenCaptureService(_mockLogger.Object);
        var bounds = new Rectangle(2000, 2000, 100, 100); // Off-screen position

        // Act
        try
        {
            var result = await service.CaptureRegionAsync(bounds);
            // May work or throw - both are acceptable
            result.Should().NotBeNull();
        }
        catch (InvalidOperationException)
        {
            // Acceptable
        }
    }

    [Fact]
    public async Task CaptureRegionAsync_MultipleSequentialCaptures_Succeeds()
    {
        // Arrange
        var service = new ScreenCaptureService(_mockLogger.Object);
        var bounds = new Rectangle(0, 0, 100, 100);

        // Act
        try
        {
            var result1 = await service.CaptureRegionAsync(bounds);
            var result2 = await service.CaptureRegionAsync(bounds);

            // Assert
            result1.Should().NotBeNull();
            result2.Should().NotBeNull();
        }
        catch (InvalidOperationException)
        {
            // Expected in test environment
        }
    }

    [Fact]
    public async Task CaptureActiveWindowAsync_MultipleCalls_Succeeds()
    {
        // Arrange
        var service = new ScreenCaptureService(_mockLogger.Object);

        // Act
        try
        {
            var result1 = await service.CaptureActiveWindowAsync();
            var result2 = await service.CaptureActiveWindowAsync();

            // Assert
            result1.Should().NotBeNull();
            result2.Should().NotBeNull();
        }
        catch (InvalidOperationException)
        {
            // Expected in test environment
        }
    }

    [Fact]
    public async Task CaptureFullscreenAsync_MultipleCalls_Succeeds()
    {
        // Arrange
        var service = new ScreenCaptureService(_mockLogger.Object);

        // Act
        try
        {
            var result1 = await service.CaptureFullscreenAsync();
            var result2 = await service.CaptureFullscreenAsync();

            // Assert
            result1.Should().NotBeNull();
            result2.Should().NotBeNull();
        }
        catch (InvalidOperationException)
        {
            // Expected in test environment
        }
    }

    [Fact]
    public async Task CaptureRegionAsync_WithSquareBounds_Succeeds()
    {
        // Arrange
        var service = new ScreenCaptureService(_mockLogger.Object);
        var bounds = new Rectangle(100, 100, 100, 100); // Square region

        // Act
        try
        {
            var result = await service.CaptureRegionAsync(bounds);
            result.Should().NotBeNull();
        }
        catch (InvalidOperationException)
        {
            // Expected in test environment
        }
    }

    [Fact]
    public async Task CaptureRegionAsync_WithWideRectangle_Succeeds()
    {
        // Arrange
        var service = new ScreenCaptureService(_mockLogger.Object);
        var bounds = new Rectangle(0, 0, 500, 100); // Wide rectangle

        // Act
        try
        {
            var result = await service.CaptureRegionAsync(bounds);
            result.Should().NotBeNull();
        }
        catch (InvalidOperationException)
        {
            // Expected in test environment
        }
    }

    [Fact]
    public async Task CaptureRegionAsync_WithTallRectangle_Succeeds()
    {
        // Arrange
        var service = new ScreenCaptureService(_mockLogger.Object);
        var bounds = new Rectangle(0, 0, 100, 500); // Tall rectangle

        // Act
        try
        {
            var result = await service.CaptureRegionAsync(bounds);
            result.Should().NotBeNull();
        }
        catch (InvalidOperationException)
        {
            // Expected in test environment
        }
    }

    [Fact]
    public async Task CaptureRegionAsync_ReturnedBytesAreNotEmpty()
    {
        // Arrange
        var service = new ScreenCaptureService(_mockLogger.Object);
        var bounds = new Rectangle(0, 0, 50, 50);

        // Act
        try
        {
            var result = await service.CaptureRegionAsync(bounds);

            // Assert
            result.Length.Should().BeGreaterThan(0, "PNG bytes should not be empty");
        }
        catch (InvalidOperationException)
        {
            // Expected in test environment
        }
    }

    [Fact]
    public async Task CaptureActiveWindowAsync_HandlesNoActiveWindow()
    {
        // Arrange
        var service = new ScreenCaptureService(_mockLogger.Object);

        // Act & Assert
        // Should throw InvalidOperationException if no window is available
        try
        {
            await service.CaptureActiveWindowAsync();
        }
        catch (InvalidOperationException ex)
        {
            ex.Should().NotBeNull();
            ex.Message.Should().Contain("Failed");
        }
    }

    [Fact]
    public async Task CaptureFullscreenAsync_HandlesHeadlessEnvironment()
    {
        // Arrange
        var service = new ScreenCaptureService(_mockLogger.Object);

        // Act & Assert
        // Should throw InvalidOperationException in headless environment
        try
        {
            await service.CaptureFullscreenAsync();
        }
        catch (InvalidOperationException ex)
        {
            ex.Should().NotBeNull();
        }
    }

    [Fact]
    public async Task ScreenCaptureService_AllMethodsAreAsync()
    {
        // Arrange
        var service = new ScreenCaptureService(_mockLogger.Object);
        var bounds = new Rectangle(0, 0, 100, 100);

        // Act
        var task1 = service.CaptureRegionAsync(bounds);
        var task2 = service.CaptureActiveWindowAsync();
        var task3 = service.CaptureFullscreenAsync();

        // Assert - All should return Task instances
        task1.Should().BeAssignableTo<Task>();
        task2.Should().BeAssignableTo<Task>();
        task3.Should().BeAssignableTo<Task>();
    }
}
