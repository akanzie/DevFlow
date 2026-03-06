using DailyClip.Core.Interfaces;
using DailyClip.Core.Config;
using Microsoft.Extensions.Logging;
using System;
using System.IO;
using System.Threading.Tasks;

namespace DailyClip.Infrastructure.Services;

/// <summary>
/// Service for managing quick notes.
/// </summary>
public class NoteService : INoteService
{
    private readonly ILogger<NoteService> _logger;

    public NoteService(ILogger<NoteService> logger)
    {
        _logger = logger;
    }

    /// <inheritdoc/>
    public async Task SaveNoteAsync(string content)
    {
        if (string.IsNullOrWhiteSpace(content))
        {
            throw new ArgumentException("Note content cannot be null or empty.", nameof(content));
        }

        try
        {
            var todayFolder = AppConfig.Paths.GetTodayFolderPath();
            Directory.CreateDirectory(todayFolder);

            var noteFileName = string.Format(AppConfig.FileNaming.NoteFilePattern, DateTime.Now);
            var noteFilePath = Path.Combine(todayFolder, noteFileName);

            var timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
            var noteEntry = $"[{timestamp}]\n{content}\n\n";

            await File.AppendAllTextAsync(noteFilePath, noteEntry);

            _logger.LogInformation("Note saved to {FilePath}", noteFilePath);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to save note");
            throw;
        }
    }
}
