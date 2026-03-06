namespace DailyClip.Core.Interfaces;

using DailyClip.Core.Entities;

/// <summary>
/// Service interface for indexing and full-text searching over clips and notes.
/// </summary>
public interface ISearchService
{
    /// <summary>
    /// Indexes a single clip item for full-text search.
    /// Performs incremental update if database exists, creates if needed.
    /// </summary>
    /// <param name="clip">The clip item to index.</param>
    /// <returns>A task representing the asynchronous operation.</returns>
    Task IndexClipAsync(ClipItem clip);

    /// <summary>
    /// Rebuilds the full index from scratch (use when migrating or fixing corruption).
    /// </summary>
    /// <returns>A task representing the asynchronous operation.</returns>
    Task RebuildIndexAsync();

    /// <summary>
    /// Performs a full-text search on indexed clips and notes.
    /// </summary>
    /// <param name="query">Search query (space-separated keywords).</param>
    /// <param name="limit">Maximum number of results to return.</param>
    /// <returns>List of search results ranked by relevance, most recent first.</returns>
    /// <exception cref="ArgumentNullException">Thrown when query is null.</exception>
    Task<List<SearchResult>> SearchAsync(string query, int limit);
}
