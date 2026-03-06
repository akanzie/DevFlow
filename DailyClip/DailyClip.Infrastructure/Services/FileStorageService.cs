namespace DailyClip.Infrastructure.Services;

using System.Text.Json;
using DailyClip.Core.Config;
using DailyClip.Core.Entities;
using DailyClip.Core.Interfaces;
using Microsoft.Extensions.Logging;

/// <summary>
/// Implementation of IStorageService for persistent file system storage.
/// Manages daily folder structure, JSONL clips, PNG screenshots, and markdown notes.
/// </summary>
public class FileStorageService : IStorageService
{
    private readonly ILogger<FileStorageService> _logger;
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = false,
        WriteIndented = false,
    };

    /// <summary>
    /// Initializes a new instance of the FileStorageService class.
    /// </summary>
    /// <param name="logger">Logger for diagnostic output.</param>
    public FileStorageService(ILogger<FileStorageService> logger)
    {
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    /// <summary>
    /// Creates today's daily folder structure: RootFolder/YYYY-MM-DD/{images,clippings,notes,index}
    /// </summary>
    public async Task CreateDailyFolderIfNotExistsAsync()
    {
        try
        {
            var todayFolder = GetTodayFolderPath();
            var subdirs = new[] { "images", "clippings", "notes", "index" };

            // Create root folder if needed
            if (!Directory.Exists(todayFolder))
            {
                Directory.CreateDirectory(todayFolder);
                _logger.LogInformation("Created daily folder: {FolderPath}", todayFolder);
            }

            // Create all subdirectories
            foreach (var subdir in subdirs)
            {
                var subdirPath = Path.Combine(todayFolder, subdir);
                if (!Directory.Exists(subdirPath))
                {
                    Directory.CreateDirectory(subdirPath);
                    _logger.LogInformation("Created subdirectory: {SubdirPath}", subdirPath);
                }
            }

            await Task.CompletedTask;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create daily folder structure");
            throw;
        }
    }

    /// <summary>
    /// Gets today's folder path in format [RootFolder]/[YYYY-MM-DD]
    /// </summary>
    public string GetTodayFolderPath() => AppConfig.Paths.GetTodayFolderPath();

    /// <summary>
    /// Appends a clip item to clippings/clips_current.jsonl as a single JSON line.
    /// Each clip is serialized and written as one line (JSONL format).
    /// </summary>
    public async Task AppendClipAsync(ClipItem clip)
    {
        ArgumentNullException.ThrowIfNull(clip);

        try
        {
            await CreateDailyFolderIfNotExistsAsync();

            var clippingsFolder = Path.Combine(GetTodayFolderPath(), "clippings");
            var clipsFile = Path.Combine(clippingsFolder, AppConfig.FileNaming.ClipsFileName);

            // Serialize clip to JSON string (single line)
            var jsonLine = JsonSerializer.Serialize(clip, JsonOptions);

            // Append to file with newline
            await File.AppendAllTextAsync(clipsFile, jsonLine + Environment.NewLine);

            _logger.LogInformation(
                "Appended clip to {ClipsFile}: {Timestamp} ({Type})",
                clipsFile,
                clip.Timestamp,
                clip.Type);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to append clip");
            throw new IOException("Failed to append clip to storage", ex);
        }
    }

    /// <summary>
    /// Saves a screenshot to images/screen_[HH-mm-ss-fff].png
    /// </summary>
    public async Task<string> SaveScreenshotAsync(byte[] imageData)
    {
        ArgumentNullException.ThrowIfNull(imageData);

        try
        {
            await CreateDailyFolderIfNotExistsAsync();

            var imagesFolder = Path.Combine(GetTodayFolderPath(), "images");
            var timestamp = DateTime.Now;
            var filename = string.Format(
                AppConfig.FileNaming.ScreenshotPattern,
                timestamp);
            var imageFile = Path.Combine(imagesFolder, filename);

            await File.WriteAllBytesAsync(imageFile, imageData);

            _logger.LogInformation("Saved screenshot: {ImageFile}", imageFile);
            return imageFile;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to save screenshot");
            throw new IOException("Failed to save screenshot", ex);
        }
    }

    /// <summary>
    /// Appends markdown content to notes/notes_[YYYY-MM-dd].md
    /// </summary>
    public async Task AppendNoteAsync(string markdownContent)
    {
        ArgumentNullException.ThrowIfNull(markdownContent);

        try
        {
            await CreateDailyFolderIfNotExistsAsync();

            var notesFolder = Path.Combine(GetTodayFolderPath(), "notes");
            var timestamp = DateTime.Now;
            var filename = string.Format(
                AppConfig.FileNaming.NoteFilePattern,
                timestamp);
            var noteFile = Path.Combine(notesFolder, filename);

            // Append content with timestamp and separator
            var contentWithTimestamp = $"{DateTime.Now:yyyy-MM-dd HH:mm:ss}: {markdownContent}{Environment.NewLine}";

            await File.AppendAllTextAsync(noteFile, contentWithTimestamp);

            _logger.LogInformation("Appended note to {NoteFile}", noteFile);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to append note");
            throw new IOException("Failed to append note", ex);
        }
    }
}
