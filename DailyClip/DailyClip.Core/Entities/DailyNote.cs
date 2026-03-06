namespace DailyClip.Core.Entities;

/// <summary>
/// Represents a daily note with Markdown content.
/// </summary>
/// <param name="Date">The date this note belongs to.</param>
/// <param name="Content">Markdown content of the note.</param>
public sealed record DailyNote(
    DateOnly Date,
    string Content)
{
    /// <summary>
    /// Creates a new DailyNote with validation.
    /// </summary>
    /// <param name="date">The date for this note.</param>
    /// <param name="content">The markdown content.</param>
    /// <returns>A validated DailyNote instance.</returns>
    /// <exception cref="ArgumentNullException">When content is null or empty.</exception>
    public static DailyNote Create(DateOnly date, string content)
    {
        if (string.IsNullOrEmpty(content))
        {
            throw new ArgumentNullException(nameof(content), "Note content cannot be null or empty");
        }

        return new DailyNote(date, content);
    }
}
