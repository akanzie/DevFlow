using System.Threading.Tasks;

namespace DailyClip.Core.Interfaces;

/// <summary>
/// Service for managing quick notes.
/// </summary>
public interface INoteService
{
    /// <summary>
    /// Saves a quick note to today's note file.
    /// </summary>
    /// <param name="content">The note content to save.</param>
    /// <returns>A task representing the asynchronous operation.</returns>
    Task SaveNoteAsync(string content);
}
