namespace DailyClip.Core.Interfaces;

using DailyClip.Core.Entities;

/// <summary>
/// Service interface for persistent storage operations (file system).
/// Handles daily folder creation, clip appending, screenshot saving, and note management.
/// </summary>
public interface IStorageService
{
    /// <summary>
    /// Ensures the daily folder structure exists for today:
    /// [RootFolder]/[YYYY-MM-DD]/{images, clippings, notes, index}/
    /// </summary>
    /// <returns>A task representing the asynchronous operation.</returns>
    Task CreateDailyFolderIfNotExistsAsync();

    /// <summary>
    /// Gets today's folder path in format [RootFolder]/[YYYY-MM-DD]/
    /// </summary>
    /// <returns>Full path to today's folder.</returns>
    string GetTodayFolderPath();

    /// <summary>
    /// Appends a clip item to clippings/clips_current.jsonl (JSONL format, one object per line).
    /// </summary>
    /// <param name="clip">The clip item to append.</param>
    /// <exception cref="ArgumentNullException">Thrown when clip is null.</exception>
    /// <exception cref="IOException">Thrown when file write fails.</exception>
    /// <returns>A task representing the asynchronous operation.</returns>
    Task AppendClipAsync(ClipItem clip);

    /// <summary>
    /// Saves a screenshot to images/screen_[HH-mm-ss-fff].png
    /// </summary>
    /// <param name="imageData">Raw PNG image bytes.</param>
    /// <returns>Full path to the saved screenshot file.</returns>
    /// <exception cref="ArgumentNullException">Thrown when imageData is null.</exception>
    /// <exception cref="IOException">Thrown when file write fails.</exception>
    Task<string> SaveScreenshotAsync(byte[] imageData);

    /// <summary>
    /// Appends markdown content to notes/notes_[YYYY-MM-DD].md
    /// </summary>
    /// <param name="markdownContent">Markdown text to append.</param>
    /// <exception cref="ArgumentNullException">Thrown when markdownContent is null.</exception>
    /// <exception cref="IOException">Thrown when file write fails.</exception>
    /// <returns>A task representing the asynchronous operation.</returns>
    Task AppendNoteAsync(string markdownContent);
}
