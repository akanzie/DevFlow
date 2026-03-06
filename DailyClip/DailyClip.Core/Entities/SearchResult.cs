namespace DailyClip.Core.Entities;

/// <summary>
/// Represents a search result from the index.
/// </summary>
/// <param name="Timestamp">When the original clip was created.</param>
/// <param name="Snippet">Preview text from the matched content.</param>
/// <param name="FilePath">Full path to the source file (JSONL, PNG, or MD).</param>
/// <param name="Type">Content type: "text" | "image"</param>
/// <param name="RelevanceScore">FTS rank score (0-1, higher = more relevant).</param>
public record SearchResult(
    DateTimeOffset Timestamp,
    string Snippet,
    string FilePath,
    string Type,
    float RelevanceScore);
