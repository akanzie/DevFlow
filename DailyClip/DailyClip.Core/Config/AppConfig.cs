namespace DailyClip.Core.Config;

/// <summary>
/// Application-wide configuration constants and settings.
/// </summary>
public static class AppConfig
{
    /// <summary>
    /// File system paths configuration.
    /// </summary>
    public static class Paths
    {
        /// <summary>
        /// Gets the root folder for DailyClip data storage.
        /// Defaults to %AppData%\DailyClip
        /// </summary>
        public static string RootFolder =>
            Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                "DailyClip");

        /// <summary>
        /// Gets today's folder path in format [RootFolder]/[YYYY-MM-DD]
        /// </summary>
        public static string GetTodayFolderPath()
        {
            var today = DateOnly.FromDateTime(DateTime.Now);
            return Path.Combine(RootFolder, today.ToString("yyyy-MM-dd"));
        }
    }

    /// <summary>
    /// Global hotkey key combinations (can be read from config later).
    /// </summary>
    public static class Hotkeys
    {
        /// <summary>
        /// Hotkey for screen capture (default: Alt+S)
        /// </summary>
        public const string CaptureHotkey = "Alt+S";

        /// <summary>
        /// Hotkey for quick note (default: Alt+N)
        /// </summary>
        public const string NoteHotkey = "Alt+N";

        /// <summary>
        /// Hotkey for quick search (default: Alt+Space)
        /// </summary>
        public const string SearchHotkey = "Alt+Space";
    }

    /// <summary>
    /// Timing and performance thresholds.
    /// </summary>
    public static class Timing
    {
        /// <summary>
        /// Duplicate detection window in seconds (skip if same content within this window).
        /// </summary>
        public const int DuplicateCacheWindowSeconds = 10;

        /// <summary>
        /// Auto-save interval for quick note (milliseconds).
        /// </summary>
        public const int AutoSaveIntervalMs = 5000;

        /// <summary>
        /// Search input debounce delay (milliseconds).
        /// </summary>
        public const int SearchDebounceMs = 300;

        /// <summary>
        /// Maximum time for search query to complete (milliseconds).
        /// </summary>
        public const int SearchTimeoutMs = 500;
    }

    /// <summary>
    /// Data retention and cleanup policies.
    /// </summary>
    public static class Cleanup
    {
        /// <summary>
        /// Default retention period for clips in days.
        /// </summary>
        public const int RetentionDays = 30;

        /// <summary>
        /// Frequency of cleanup check (milliseconds).
        /// </summary>
        public const int CleanupCheckIntervalMs = 3600000; // 1 hour
    }

    /// <summary>
    /// File naming conventions.
    /// </summary>
    public static class FileNaming
    {
        /// <summary>
        /// Appendable clipboard clips file: clippings/clips_current.jsonl
        /// </summary>
        public const string ClipsFileName = "clips_current.jsonl";

        /// <summary>
        /// Screenshot file name pattern: screen_[HH-mm-ss-fff].png
        /// </summary>
        public const string ScreenshotPattern = "screen_{0:HH-mm-ss-fff}.png";

        /// <summary>
        /// Daily note file pattern: notes_[YYYY-MM-dd].md
        /// </summary>
        public const string NoteFilePattern = "notes_{0:yyyy-MM-dd}.md";

        /// <summary>
        /// DuckDB index file name.
        /// </summary>
        public const string IndexDatabaseFileName = "daily_index.duckdb";
    }

    /// <summary>
    /// Database configuration.
    /// </summary>
    public static class Database
    {
        /// <summary>
        /// Maximum number of search results to return.
        /// </summary>
        public const int MaxSearchResults = 50;

        /// <summary>
        /// Threshold for rebuilding index vs incremental update.
        /// </summary>
        public const int RebuildIndexClipsThreshold = 500;
    }
}
