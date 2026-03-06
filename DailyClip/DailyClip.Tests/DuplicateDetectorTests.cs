namespace DailyClip.Tests;

using DailyClip.Infrastructure.Services;
using FluentAssertions;
using Xunit;

/// <summary>
/// Unit tests for DuplicateDetector.
/// </summary>
public class DuplicateDetectorTests
{
    [Fact]
    public void IsDuplicate_FirstContent_ReturnsFalse()
    {
        // Arrange
        var detector = new DuplicateDetector();

        // Act
        var result = detector.IsDuplicate("new content");

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public void IsDuplicate_SameContentImmediately_ReturnsTrue()
    {
        // Arrange
        var detector = new DuplicateDetector();
        var content = "duplicate me";

        // Act
        detector.IsDuplicate(content); // First call
        var result = detector.IsDuplicate(content); // Second call

        // Assert
        result.Should().BeTrue();
    }

    [Fact]
    public void IsDuplicate_DifferentContent_ReturnsFalse()
    {
        // Arrange
        var detector = new DuplicateDetector();

        // Act
        detector.IsDuplicate("content A");
        var result = detector.IsDuplicate("content B");

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public void IsDuplicate_AfterWindow_ReturnsFalse()
    {
        // Arrange
        var detector = new DuplicateDetector(windowSeconds: 1);
        var content = "content";

        // Act
        detector.IsDuplicate(content);
        System.Threading.Thread.Sleep(1100); // Wait > 1 second
        var result = detector.IsDuplicate(content);

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public void IsDuplicate_WithinWindow_ReturnsTrue()
    {
        // Arrange
        var detector = new DuplicateDetector(windowSeconds: 5);
        var content = "content";

        // Act
        detector.IsDuplicate(content);
        System.Threading.Thread.Sleep(100); // Wait < 5 seconds
        var result = detector.IsDuplicate(content);

        // Assert
        result.Should().BeTrue();
    }

    [Fact]
    public void IsDuplicate_MultipleContents_TracksIndependently()
    {
        // Arrange
        var detector = new DuplicateDetector();

        // Act
        detector.IsDuplicate("content A");
        detector.IsDuplicate("content B");
        detector.IsDuplicate("content C");

        var resultA = detector.IsDuplicate("content A");
        var resultB = detector.IsDuplicate("content B");
        var resultD = detector.IsDuplicate("content D");

        // Assert
        resultA.Should().BeTrue("A was seen before");
        resultB.Should().BeTrue("B was seen before");
        resultD.Should().BeFalse("D is new");
    }

    [Fact]
    public void IsDuplicate_WithNull_ThrowsArgumentNullException()
    {
        // Arrange
        var detector = new DuplicateDetector();

        // Act & Assert
        Assert.Throws<ArgumentNullException>(() => detector.IsDuplicate(null!));
    }

    [Fact]
    public void IsDuplicate_WithEmptyString_ReturnsFalse()
    {
        // Arrange
        var detector = new DuplicateDetector();

        // Act
        var result1 = detector.IsDuplicate(string.Empty);
        var result2 = detector.IsDuplicate(string.Empty);

        // Assert
        result1.Should().BeFalse();
        result2.Should().BeTrue("Same empty string is duplicate");
    }

    [Fact]
    public void IsDuplicate_LargeContent_WorksCorrectly()
    {
        // Arrange
        var detector = new DuplicateDetector();
        var largeContent = new string('x', 10_000_000); // 10MB string

        // Act
        var result1 = detector.IsDuplicate(largeContent);
        var result2 = detector.IsDuplicate(largeContent);

        // Assert
        result1.Should().BeFalse();
        result2.Should().BeTrue();
    }

    [Fact]
    public void Clear_EmptiesCache()
    {
        // Arrange
        var detector = new DuplicateDetector();
        detector.IsDuplicate("content A");
        detector.IsDuplicate("content B");

        // Act
        detector.Clear();

        // Assert
        detector.CacheCount.Should().Be(0);
        detector.IsDuplicate("content A").Should().BeFalse("Cache was cleared");
    }

    [Fact]
    public void CacheCount_TracksSize()
    {
        // Arrange
        var detector = new DuplicateDetector();

        // Act & Assert
        detector.CacheCount.Should().Be(0);
        
        detector.IsDuplicate("A");
        detector.CacheCount.Should().Be(1);
        
        detector.IsDuplicate("B");
        detector.CacheCount.Should().Be(2);
        
        detector.IsDuplicate("C");
        detector.CacheCount.Should().Be(3);
    }

    [Fact]
    public void Constructor_WithInvalidWindow_ThrowsArgumentException()
    {
        // Act & Assert
        Assert.Throws<ArgumentException>(() => new DuplicateDetector(windowSeconds: 0));
        Assert.Throws<ArgumentException>(() => new DuplicateDetector(windowSeconds: -1));
    }

    [Fact]
    public void IsDuplicate_SimilarButDifferentContent_BothTracked()
    {
        // Arrange
        var detector = new DuplicateDetector();
        var content1 = "Hello World";
        var content2 = "Hello World ";  // Trailing space

        // Act
        var result1 = detector.IsDuplicate(content1);
        var result2 = detector.IsDuplicate(content1);
        var result3 = detector.IsDuplicate(content2);
        var result4 = detector.IsDuplicate(content2);

        // Assert
        result1.Should().BeFalse();
        result2.Should().BeTrue();
        result3.Should().BeFalse("Different from content1");
        result4.Should().BeTrue("Same as content2");
    }
}
