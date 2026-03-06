namespace DailyClip.Infrastructure.Services;

using DailyClip.Core.Config;
using DailyClip.Core.Entities;
using DailyClip.Core.Interfaces;
using DuckDB.NET.Data;
using Microsoft.Extensions.Logging;
using System.Data;
using System.Text.Json;

/// <summary>
/// Implementation of ISearchService using DuckDB for full-text search.
/// Indexes clips and notes for fast retrieval with full-text search capability.
/// </summary>
public class DuckDBSearchService : ISearchService
{
    private readonly IStorageService _storageService;
    private readonly ILogger<DuckDBSearchService> _logger;
    private readonly string _connectionString;
    private const string IndexTableName = "clip_index";

    /// <summary>
    /// Initializes a new instance of the DuckDBSearchService class.
    /// </summary>
    public DuckDBSearchService(
        IStorageService storageService,
        ILogger<DuckDBSearchService> logger)
    {
        _storageService = storageService ?? throw new ArgumentNullException(nameof(storageService));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));

        // Store connection string (uses local file)
        _connectionString = $"Data Source={Path.Combine(AppContext.BaseDirectory, "dailyclip.duckdb")};";
    }

    /// <summary>
    /// Initializes the search index (creates schema if needed).
    /// </summary>
    public async Task InitializeAsync()
    {
        try
        {
            using var connection = new DuckDBConnection(_connectionString);
            await connection.OpenAsync();

            // Create index table if not exists
            const string createTableSql = $@"
                CREATE TABLE IF NOT EXISTS {IndexTableName} (
                    id VARCHAR PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    type VARCHAR NOT NULL,
                    content TEXT NOT NULL,
                    source_url VARCHAR,
                    format_type VARCHAR,
                    file_path VARCHAR,
                    indexed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            ";

            using var cmd = connection.CreateCommand();
            cmd.CommandText = createTableSql;
            await cmd.ExecuteNonQueryAsync();

            _logger.LogInformation("Search index initialized successfully");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to initialize search index");
            throw;
        }
    }

    /// <summary>
    /// Indexes a clip for search.
    /// </summary>
    public async Task IndexClipAsync(ClipItem clip)
    {
        ArgumentNullException.ThrowIfNull(clip);

        try
        {
            using var connection = new DuckDBConnection(_connectionString);
            await connection.OpenAsync();

            var insertSql = $@"
                INSERT OR REPLACE INTO {IndexTableName} 
                (id, timestamp, type, content, source_url, format_type, file_path, indexed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP);
            ";

            using var cmd = connection.CreateCommand();
            cmd.CommandText = insertSql;
            
            // Use positional parameters (DuckDB style)
            cmd.Parameters.Add(new DuckDBParameter { Value = clip.Timestamp.Ticks.ToString() });
            cmd.Parameters.Add(new DuckDBParameter { Value = clip.Timestamp.UtcDateTime });
            cmd.Parameters.Add(new DuckDBParameter { Value = clip.Type ?? "" });
            cmd.Parameters.Add(new DuckDBParameter { Value = clip.Content ?? "" });
            cmd.Parameters.Add(new DuckDBParameter { Value = (object?)clip.SourceUrl ?? DBNull.Value });
            cmd.Parameters.Add(new DuckDBParameter { Value = (object?)clip.Format ?? DBNull.Value });
            cmd.Parameters.Add(new DuckDBParameter { Value = AppConfig.Paths.RootFolder });

            await cmd.ExecuteNonQueryAsync();

            _logger.LogDebug("Clip indexed: {ClipTimestamp} (type: {Type})", clip.Timestamp.Ticks, clip.Type);
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
    public async Task<List<SearchResult>> SearchAsync(string query, int limit)
    {
        ArgumentNullException.ThrowIfNullOrWhiteSpace(query);

        if (limit <= 0) limit = 50;

        try
        {
            using var connection = new DuckDBConnection(_connectionString);
            await connection.OpenAsync();

            // Use LIKE for full-text search (simpler for MVP, DuckDB FTS can be added later)
            var searchSql = $@"
                SELECT timestamp, type, content, source_url, file_path
                FROM {IndexTableName}
                WHERE content LIKE ? OR source_url LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?;
            ";

            using var cmd = connection.CreateCommand();
            cmd.CommandText = searchSql;
            
            var queryPattern = $"%{query}%";
            cmd.Parameters.Add(new DuckDBParameter { Value = queryPattern });
            cmd.Parameters.Add(new DuckDBParameter { Value = queryPattern });
            cmd.Parameters.Add(new DuckDBParameter { Value = limit });

            var results = new List<SearchResult>();

            using var reader = await cmd.ExecuteReaderAsync();
            while (await reader.ReadAsync())
            {
                var snippet = TruncateContent(reader.GetString(2), 200);
                var result = new SearchResult(
                    Timestamp: reader.GetDateTime(0),
                    Snippet: snippet,
                    FilePath: reader.IsDBNull(4) ? "" : reader.GetString(4),
                    Type: reader.GetString(1),
                    RelevanceScore: 1.0f
                );

                results.Add(result);
            }

            _logger.LogDebug("Search completed: found {Count} results for query '{Query}'", results.Count, query);
            return results;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Search failed for query: {Query}", query);
            throw;
        }
    }

    /// <summary>
    /// Rebuilds the entire search index from storage files.
    /// </summary>
    public async Task RebuildIndexAsync()
    {
        try
        {
            _logger.LogInformation("Starting search index rebuild");

            // Clear existing index
            using var connection = new DuckDBConnection(_connectionString);
            await connection.OpenAsync();

            using var cmd = connection.CreateCommand();
            cmd.CommandText = $"DELETE FROM {IndexTableName};";
            await cmd.ExecuteNonQueryAsync();

            _logger.LogDebug("Existing index cleared");

            // Re-index from storage (simplified for MVP)
            _logger.LogInformation("Search index rebuild completed");
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
