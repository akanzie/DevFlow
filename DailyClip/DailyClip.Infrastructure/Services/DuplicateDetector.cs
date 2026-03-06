namespace DailyClip.Infrastructure.Services;

using System.Collections.Concurrent;
using System.Security.Cryptography;
using System.Text;

/// <summary>
/// Detects duplicate clipboard content within a 10-second sliding window.
/// Uses SHA256 hash of content for fast comparison and minimal memory usage.
/// </summary>
public class DuplicateDetector
{
    private readonly ConcurrentDictionary<string, long> _hashCache = new();
    private readonly int _windowSeconds;

    /// <summary>
    /// Initializes a new instance of the DuplicateDetector class.
    /// </summary>
    /// <param name="windowSeconds">Time window in seconds for duplicate detection (default: 10).</param>
    public DuplicateDetector(int windowSeconds = 10)
    {
        if (windowSeconds <= 0)
            throw new ArgumentException("Window must be positive", nameof(windowSeconds));

        _windowSeconds = windowSeconds;
    }

    /// <summary>
    /// Checks if content was seen recently (within window).
    /// If new, adds it to cache for future checks.
    /// </summary>
    /// <param name="content">Content to check.</param>
    /// <returns>True if content seen recently (duplicate), false if new.</returns>
    /// <exception cref="ArgumentNullException">Thrown when content is null.</exception>
    public bool IsDuplicate(string content)
    {
        ArgumentNullException.ThrowIfNull(content);

        var hash = ComputeHash(content);
        var now = DateTimeOffset.UtcNow.ToUnixTimeSeconds();

        // Try to get existing entry
        if (_hashCache.TryGetValue(hash, out var timestamp))
        {
            var elapsed = now - timestamp;
            if (elapsed < _windowSeconds)
            {
                // Within window → duplicate
                return true;
            }

            // Outside window → treat as new, update timestamp
            _hashCache[hash] = now;
            return false;
        }

        // First time seeing this content → add to cache
        _hashCache.TryAdd(hash, now);
        return false;
    }

    /// <summary>
    /// Clears the duplicate cache.
    /// </summary>
    public void Clear()
    {
        _hashCache.Clear();
    }

    /// <summary>
    /// Gets the number of cached hashes.
    /// </summary>
    public int CacheCount => _hashCache.Count;

    /// <summary>
    /// Computes SHA256 hash of content.
    /// </summary>
    private static string ComputeHash(string content)
    {
        using var sha = SHA256.Create();
        var bytes = Encoding.UTF8.GetBytes(content);
        var hash = sha.ComputeHash(bytes);
        return Convert.ToHexString(hash);
    }
}
