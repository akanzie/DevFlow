namespace DailyClip.Core.Helpers;

using DailyClip.Core.Entities;

/// <summary>
/// Factory methods for creating ClipItem instances with common patterns.
/// </summary>
public static class ClipItemFactory
{
    /// <summary>
    /// Creates a ClipItem from text content (most common case).
    /// </summary>
    /// <param name="text">The text content.</param>
    /// <param name="sourceUrl">Optional source URL or reference.</param>
    /// <returns>A new ClipItem with type "text".</returns>
    public static ClipItem FromText(string text, string? sourceUrl = null)
    {
        ArgumentNullException.ThrowIfNull(text);
        return ClipItem.Create(
            DateTimeOffset.Now,
            "text",
            text,
            sourceUrl ?? "clipboard");
    }

    /// <summary>
    /// Creates a ClipItem from code content (with language annotation).
    /// </summary>
    /// <param name="code">The code content.</param>
    /// <param name="language">Programming language identifier (optional).</param>
    /// <returns>A new ClipItem with type "code".</returns>
    public static ClipItem FromCode(string code, string? language = null)
    {
        ArgumentNullException.ThrowIfNull(code);
        var type = string.IsNullOrWhiteSpace(language) ? "code" : $"code:{language}";
        return ClipItem.Create(
            DateTimeOffset.Now,
            type,
            code,
            $"code/{language}");
    }

    /// <summary>
    /// Creates a ClipItem from JSON content.
    /// </summary>
    /// <param name="json">The JSON content.</param>
    /// <returns>A new ClipItem with type "json".</returns>
    public static ClipItem FromJson(string json)
    {
        ArgumentNullException.ThrowIfNull(json);
        return ClipItem.Create(
            DateTimeOffset.Now,
            "json",
            json,
            "clipboard");
    }

    /// <summary>
    /// Creates a ClipItem from markdown content.
    /// </summary>
    /// <param name="markdown">The markdown content.</param>
    /// <returns>A new ClipItem with type "markdown".</returns>
    public static ClipItem FromMarkdown(string markdown)
    {
        ArgumentNullException.ThrowIfNull(markdown);
        return ClipItem.Create(
            DateTimeOffset.Now,
            "markdown",
            markdown,
            "clipboard");
    }
}
