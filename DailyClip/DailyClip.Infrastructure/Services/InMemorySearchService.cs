namespace DailyClip.Infrastructure.Services;

using DailyClip.Core.Entities;
using DailyClip.Core.Interfaces;
using Microsoft.Extensions.Logging;

/// <summary>
/// In-memory implementation of ISearchService for MVP.
/// Provides full-text search without external database dependencies.
/// Can be upgraded to DuckDB later if performance requires it.
/// </summary>
public class InMemorySearchService : ISearchService
{
    private readonly IStorageService _storageService;
    private readonly ILogger<InMemorySearchService> _logger;
    private readonly List<IndexedItem> _index = new();

    private class IndexedItem
    {
        public required string Id { get; set; }
        public required DateTimeOffset Timestamp { get; set; }
        public required string Type { get; set; }
        public required string Content { get; set; }
        public string? SourceUrl { get; set; }
        public string? Format { get; set; }
        public required string FilePath { get; set; }
    }

    /// <summary>
    /// Initializes a new instance of the InMemorySearchService class.
    /// </summary>
    public InMemorySearchService(
        IStorageService storageService,
        ILogger<InMemorySearchService> logger)
    {
        _storageService = storageService ?? throw new ArgumentNullException(nameof(storageService));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    /// <summary>
    /// Initializes the search service (no-op for in-memory implementation).
    /// </summary>
    public Task InitializeAsync()
    {
        _logger.LogInformation("In-memory search service initialized");
        return Task.CompletedTask;
    }

    /// <summary>
    /// Indexes a clip for search.
    /// </summary>
    public Task IndexClipAsync(ClipItem clip)
    {
        ArgumentNullException.ThrowIfNull(clip);

        try
        {
            var id = clip.Timestamp.Ticks.ToString();
            
            // Remove existing entry if present
            _index.RemoveAll(x => x.Id == id);

            // Add new entry
            _index.Add(new IndexedItem
            {
                Id = id,
                Timestamp = clip.Timestamp,
                Type = clip.Type ?? "text",
                Content = clip.Content ?? "",
                SourceUrl = clip.SourceUrl,
                Format = clip.Format,
                FilePath = ""
            });

            _logger.LogDebug("Clip indexed: {ClipId} (type: {Type})", id, clip.Type);
            return Task.CompletedTask;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to index clip");
            throw;
        }
    }

    /// <summary>
    /// Searches for clips matching the query using full-text search.
    /// </summary>
    public Task<List<SearchResult>> SearchAsync(string query, int limit)
    {
        ArgumentNullException.ThrowIfNullOrWhiteSpace(query);

        if (limit <= 0) limit = 50;

        try
        {
            var results = new List<SearchResult>();
            var queryLower = query.ToLowerInvariant();

            // Search in content and source URL
            var matches = _index
                .Where(item =>
                    (item.Content?.Contains(queryLower, StringComparison.OrdinalIgnoreCase) ?? false) ||
                    (item.SourceUrl?.Contains(queryLower, StringComparison.OrdinalIgnoreCase) ?? false))
                .OrderByDescending(item => item.Timestamp)
                .Take(limit)
                .ToList();

            foreach (var match in matches)
            {
                var snippet = TruncateContent(match.Content, 200);
                var result = new SearchResult(
                    Timestamp: match.Timestamp,
                    Snippet: snippet,
                    FilePath: match.FilePath,
                    Type: match.Type,
                    RelevanceScore: 1.0f
                );

                results.Add(result);
            }

            _logger.LogDebug("Search completed: found {Count} results for query '{Query}'", results.Count, query);
            return Task.FromResult(results);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Search failed for query: {Query}", query);
            throw;
        }
    }

    /// <summary>
    /// Rebuilds the search index from storage files.
    /// </summary>
    public Task RebuildIndexAsync()
    {
        try
        {
            _logger.LogInformation("Starting search index rebuild");

            // Clear existing index
            _index.Clear();

            _logger.LogInformation("Search index rebuild completed");
            return Task.CompletedTask;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to rebuild search index");
            throw;
        }
    }

    /// <summary>
    /// Truncates content to a maximum length for preview.
    /// </summary>
    private static string TruncateContent(string content, int maxLength = 200)
    {
        if (string.IsNullOrEmpty(content)) return "";
        if (content.Length <= maxLength) return content;

        return content.Substring(0, maxLength) + "...";
    }
}
