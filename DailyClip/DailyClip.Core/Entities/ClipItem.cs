namespace DailyClip.Core.Entities;

/// <summary>
/// Represents a single clipboard item (text, image, or HTML content).
/// Immutable record type for domain entity.
/// </summary>
/// <param name="Timestamp">When the clip was captured.</param>
/// <param name="Type">Content type: "text" | "image" | "html"</param>
/// <param name="Content">Text content or path to image file.</param>
/// <param name="SourceUrl">Optional source URL extracted from HTML format.</param>
/// <param name="Format">Optional content format: "plain" | "markdown" | "code" etc.</param>
public sealed record ClipItem(
    DateTimeOffset Timestamp,
    string Type,
    string Content,
    string? SourceUrl = null,
    string? Format = null)
{
    /// <summary>
    /// Creates a new ClipItem with validation.
    /// </summary>
    /// <param name="timestamp">The timestamp of the clip.</param>
    /// <param name="type">The content type.</param>
    /// <param name="content">The clip content.</param>
    /// <param name="sourceUrl">Optional source URL.</param>
    /// <param name="format">Optional content format.</param>
    /// <returns>A validated ClipItem instance.</returns>
    /// <exception cref="ArgumentException">When timestamp is default.</exception>
    /// <exception cref="ArgumentNullException">When required fields are null/empty.</exception>
    public static ClipItem Create(
        DateTimeOffset timestamp,
        string type,
        string content,
        string? sourceUrl = null,
        string? format = null)
    {
        if (timestamp == default)
        {
            throw new ArgumentException("Timestamp cannot be default", nameof(timestamp));
        }

        if (string.IsNullOrWhiteSpace(type))
        {
            throw new ArgumentNullException(nameof(type), "Type cannot be null or empty");
        }

        if (string.IsNullOrWhiteSpace(content))
        {
            throw new ArgumentNullException(nameof(content), "Content cannot be null or empty");
        }

        return new ClipItem(timestamp, type, content, sourceUrl, format);
    }

    /// <summary>
    /// Checks if this clip is a duplicate of another clip within the configured time window.
    /// </summary>
    /// <param name="other">The other clip to compare against.</param>
    /// <returns>true if same type and content within 10-second window; otherwise false.</returns>
    public bool IsDuplicate(ClipItem other)
    {
        ArgumentNullException.ThrowIfNull(other);

        const int windowSeconds = 10;

        return Type == other.Type
            && Content == other.Content
            && Math.Abs((Timestamp - other.Timestamp).TotalSeconds) <= windowSeconds;
    }
}
