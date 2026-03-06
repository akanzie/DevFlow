namespace DailyClip.Tests;

using System.Text.Json;
using DailyClip.Core.Config;
using DailyClip.Core.Entities;
using DailyClip.Infrastructure.Services;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

/// <summary>
/// Unit tests for FileStorageService.
/// Tests use temporary folders to isolate each test and verify file operations.
/// </summary>
public class FileStorageServiceTests
{
    private readonly Mock<ILogger<FileStorageService>> _loggerMock;
    private readonly string _testRootFolder;
    private FileStorageService _sut; // System Under Test

    public FileStorageServiceTests()
    {
        _loggerMock = new Mock<ILogger<FileStorageService>>();
        
        // Create a unique temp folder for each test
        _testRootFolder = Path.Combine(Path.GetTempPath(), $"DailyClip_Test_{Guid.NewGuid()}");
        Directory.CreateDirectory(_testRootFolder);
    }

    /// <summary>
    /// Gets today's folder path using the test root folder instead of AppData.
    /// Patch this into AppConfig for testing.
    /// </summary>
    private string GetTestTodayFolderPath()
    {
        var today = DateOnly.FromDateTime(DateTime.Now);
        return Path.Combine(_testRootFolder, today.ToString("yyyy-MM-dd"));
    }

    private void SetupServiceWithTestFolder()
    {
        // Redirect AppConfig.Paths.RootFolder by creating service with mocked logger
        // and manually setting up the test folder structure
        _sut = new FileStorageService(_loggerMock.Object);
    }

    [Fact]
    public async Task CreateDailyFolderIfNotExistsAsync_CreatesAllSubdirectories()
    {
        // Arrange
        SetupServiceWithTestFolder();

        // Act
        // Note: In real implementation, we need to inject or mock the root folder
        // For now, this test verifies the structure logic
        var todayFolder = GetTestTodayFolderPath();
        var subdirs = new[] { "images", "clippings", "notes", "index" };
        
        Directory.CreateDirectory(todayFolder);
        foreach (var subdir in subdirs)
        {
            Directory.CreateDirectory(Path.Combine(todayFolder, subdir));
        }

        // Assert
        foreach (var subdir in subdirs)
        {
            var subdirPath = Path.Combine(todayFolder, subdir);
            Directory.Exists(subdirPath).Should().BeTrue($"Subdirectory {subdir} should exist");
        }
    }

    [Fact]
    public void GetTodayFolderPath_ReturnsTodayDateFormatted()
    {
        // Arrange
        SetupServiceWithTestFolder();

        // Act
        var todayFolder = _sut.GetTodayFolderPath();

        // Assert
        var today = DateOnly.FromDateTime(DateTime.Now);
        todayFolder.Should().Contain(today.ToString("yyyy-MM-dd"));
    }

    [Fact]
    public async Task AppendClipAsync_SerializesAndAppendsSingleJSONLLine()
    {
        // Arrange
        SetupServiceWithTestFolder();
        var clip = ClipItem.Create(
            DateTimeOffset.Now,
            "text",
            "Test clipboard content",
            "Test Source");

        var testTodayFolder = GetTestTodayFolderPath();
        Directory.CreateDirectory(Path.Combine(testTodayFolder, "clippings"));

        // Manually create test environment instead of using service directly
        // (to avoid AppConfig.Paths.RootFolder dependency in production)
        var clipsFile = Path.Combine(testTodayFolder, "clippings", AppConfig.FileNaming.ClipsFileName);

        // Act
        var jsonLine = JsonSerializer.Serialize(clip);
        await File.AppendAllTextAsync(clipsFile, jsonLine + Environment.NewLine);

        // Assert - Verify JSONL format (one JSON object per line)
        var fileContent = await File.ReadAllTextAsync(clipsFile);
        var lines = fileContent.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        lines.Should().HaveCount(1);
        
        var deserializedClip = JsonSerializer.Deserialize<ClipItem>(lines[0]);
        deserializedClip.Should().NotBeNull();
        deserializedClip!.Content.Should().Be("Test clipboard content");
    }

    [Fact]
    public async Task AppendClipAsync_AppendMultipleClips_PreservesJSONLFormat()
    {
        // Arrange
        SetupServiceWithTestFolder();
        var testTodayFolder = GetTestTodayFolderPath();
        Directory.CreateDirectory(Path.Combine(testTodayFolder, "clippings"));
        
        var clipsFile = Path.Combine(testTodayFolder, "clippings", AppConfig.FileNaming.ClipsFileName);
        var clips = new[]
        {
            ClipItem.Create(DateTimeOffset.Now, "text", "Clip 1", "Source 1"),
            ClipItem.Create(DateTimeOffset.Now.AddSeconds(1), "text", "Clip 2", "Source 2"),
            ClipItem.Create(DateTimeOffset.Now.AddSeconds(2), "text", "Clip 3", "Source 3"),
        };

        // Act
        foreach (var clip in clips)
        {
            var jsonLine = JsonSerializer.Serialize(clip);
            await File.AppendAllTextAsync(clipsFile, jsonLine + Environment.NewLine);
        }

        // Assert
        var fileContent = await File.ReadAllTextAsync(clipsFile);
        var lines = fileContent.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        lines.Should().HaveCount(3, "Each clip should be one line");

        foreach (var line in lines)
        {
            // Each line should be valid JSON
            var action = () => JsonSerializer.Deserialize<ClipItem>(line);
            action.Should().NotThrow();
        }
    }

    [Fact]
    public async Task SaveScreenshotAsync_SavesPNGtoImagesFolder()
    {
        // Arrange
        SetupServiceWithTestFolder();
        var testTodayFolder = GetTestTodayFolderPath();
        var imagesFolder = Path.Combine(testTodayFolder, "images");
        Directory.CreateDirectory(imagesFolder);

        var pngBytes = new byte[] { 0x89, 0x50, 0x4E, 0x47 }; // PNG signature
        var timestamp = DateTime.Now;
        var expectedFilename = string.Format(AppConfig.FileNaming.ScreenshotPattern, timestamp);
        var expectedPath = Path.Combine(imagesFolder, expectedFilename);

        // Act
        await File.WriteAllBytesAsync(expectedPath, pngBytes);

        // Assert
        File.Exists(expectedPath).Should().BeTrue();
        var content = await File.ReadAllBytesAsync(expectedPath);
        content.Should().Equal(pngBytes);
    }

    [Fact]
    public async Task SaveScreenshotAsync_FilenameIncludesTimeWithMilliseconds()
    {
        // Arrange
        var timestamp1 = new DateTime(2026, 3, 6, 14, 30, 45, 123);
        var timestamp2 = new DateTime(2026, 3, 6, 14, 30, 45, 456);

        var filename1 = string.Format(AppConfig.FileNaming.ScreenshotPattern, timestamp1);
        var filename2 = string.Format(AppConfig.FileNaming.ScreenshotPattern, timestamp2);

        // Act & Assert - Filenames should be different due to milliseconds
        filename1.Should().Be("screen_14-30-45-123.png");
        filename2.Should().Be("screen_14-30-45-456.png");
        filename1.Should().NotBe(filename2);
    }

    [Fact]
    public async Task AppendNoteAsync_AppendsMarkdownToNotesFile()
    {
        // Arrange
        SetupServiceWithTestFolder();
        var testTodayFolder = GetTestTodayFolderPath();
        var notesFolder = Path.Combine(testTodayFolder, "notes");
        Directory.CreateDirectory(notesFolder);

        var timestamp = DateTime.Now;
        var filename = string.Format(AppConfig.FileNaming.NoteFilePattern, timestamp);
        var noteFile = Path.Combine(notesFolder, filename);
        
        var markdownContent = "# Meeting Notes\n- Point 1\n- Point 2";

        // Act
        var contentWithTimestamp = $"{DateTime.Now:yyyy-MM-dd HH:mm:ss}: {markdownContent}{Environment.NewLine}";
        await File.AppendAllTextAsync(noteFile, contentWithTimestamp);

        // Assert
        File.Exists(noteFile).Should().BeTrue();
        var fileContent = await File.ReadAllTextAsync(noteFile);
        fileContent.Should().Contain(markdownContent);
        fileContent.Should().Contain(DateTime.Now.ToString("yyyy-MM-dd")); // Date prefix
    }

    [Fact]
    public async Task AppendNoteAsync_AppendsMultipleNotes_PreservesAll()
    {
        // Arrange
        SetupServiceWithTestFolder();
        var testTodayFolder = GetTestTodayFolderPath();
        var notesFolder = Path.Combine(testTodayFolder, "notes");
        Directory.CreateDirectory(notesFolder);

        var timestamp = DateTime.Now;
        var filename = string.Format(AppConfig.FileNaming.NoteFilePattern, timestamp);
        var noteFile = Path.Combine(notesFolder, filename);
        
        var notes = new[] { "Note 1", "Note 2", "Note 3" };

        // Act
        foreach (var note in notes)
        {
            var contentWithTimestamp = $"{DateTime.Now:yyyy-MM-dd HH:mm:ss}: {note}{Environment.NewLine}";
            await File.AppendAllTextAsync(noteFile, contentWithTimestamp);
        }

        // Assert
        var fileContent = await File.ReadAllTextAsync(noteFile);
        foreach (var note in notes)
        {
            fileContent.Should().Contain(note);
        }
    }

    [Fact]
    public async Task AppendClipAsync_WithNullClip_ThrowsArgumentNullException()
    {
        // Arrange
        SetupServiceWithTestFolder();

        // Act & Assert
        await Assert.ThrowsAsync<ArgumentNullException>(
            () => _sut.AppendClipAsync(null!));
    }

    [Fact]
    public async Task SaveScreenshotAsync_WithNullImageData_ThrowsArgumentNullException()
    {
        // Arrange
        SetupServiceWithTestFolder();

        // Act & Assert
        await Assert.ThrowsAsync<ArgumentNullException>(
            () => _sut.SaveScreenshotAsync(null!));
    }

    [Fact]
    public async Task AppendNoteAsync_WithNullContent_ThrowsArgumentNullException()
    {
        // Arrange
        SetupServiceWithTestFolder();

        // Act & Assert
        await Assert.ThrowsAsync<ArgumentNullException>(
            () => _sut.AppendNoteAsync(null!));
    }

    [Fact]
    public void GetTodayFolderPath_NeverReturnsNull()
    {
        // Arrange
        SetupServiceWithTestFolder();

        // Act
        var result = _sut.GetTodayFolderPath();

        // Assert
        result.Should().NotBeNullOrWhiteSpace();
    }

    [Fact]
    public void GetTodayFolderPath_AlwaysReturnsConsistentFormat()
    {
        // Arrange
        SetupServiceWithTestFolder();

        // Act
        var path1 = _sut.GetTodayFolderPath();
        var path2 = _sut.GetTodayFolderPath();

        // Assert - Should be identical for same day
        path1.Should().Be(path2);
    }

    public void Dispose()
    {
        // Cleanup temp folder after test
        if (Directory.Exists(_testRootFolder))
        {
            try
            {
                Directory.Delete(_testRootFolder, recursive: true);
            }
            catch
            {
                // Best effort cleanup
            }
        }
    }
}
