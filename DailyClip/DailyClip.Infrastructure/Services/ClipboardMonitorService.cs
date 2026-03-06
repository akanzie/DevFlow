namespace DailyClip.Infrastructure.Services;

using DailyClip.Core.Entities;
using DailyClip.Core.Helpers;
using DailyClip.Core.Interfaces;
using Microsoft.Extensions.Logging;

/// <summary>
/// Implementation of IClipboardMonitor for monitoring Windows clipboard changes.
/// 
/// Current Implementation (STEP 7-10): Stub with manual text processing capability.
/// Real clipboard event monitoring will be integrated in STEP 12+ with WinUI3.
/// 
/// This allows testing of the factory and duplicate detection logic in isolation,
/// with clipboard polling to be added when the UI framework is available.
/// </summary>
public class ClipboardMonitorService : IClipboardMonitor
{
    private readonly IStorageService _storageService;
    private readonly ISearchService _searchService;
    private readonly ILogger<ClipboardMonitorService> _logger;
    private readonly DuplicateDetector _duplicateDetector;
    private bool _isMonitoring;

    /// <summary>
    /// Event fired when clipboard content is detected and saved (excludes duplicates).
    /// </summary>
    public event EventHandler<ClipboardChangedEventArgs>? ClipboardChanged;

    /// <summary>
    /// Initializes a new instance of the ClipboardMonitorService class.
    /// </summary>
    public ClipboardMonitorService(
        IStorageService storageService,
        ISearchService searchService,
        ILogger<ClipboardMonitorService> logger,
        DuplicateDetector duplicateDetector)
    {
        _storageService = storageService ?? throw new ArgumentNullException(nameof(storageService));
        _searchService = searchService ?? throw new ArgumentNullException(nameof(searchService));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        _duplicateDetector = duplicateDetector ?? throw new ArgumentNullException(nameof(duplicateDetector));
        _isMonitoring = false;
    }

    /// <summary>
    /// Starts monitoring clipboard for changes.
    /// Placeholder for STEP 7-10. Real clipboard monitoring will be integrated in STEP 12+ with WinUI3.
    /// </summary>
    public async Task StartMonitoringAsync()
    {
        if (_isMonitoring)
        {
            _logger.LogDebug("Clipboard monitoring already active, skipping start");
            return;
        }

        try
        {
            // Ensure daily folder exists before monitoring
            await _storageService.CreateDailyFolderIfNotExistsAsync();

            _isMonitoring = true;
            _logger.LogInformation("Clipboard monitoring started (STEP 7-10: placeholder - real monitoring in STEP 12+ with WinUI3)");
        }
        catch (Exception ex)
        {
            _isMonitoring = false;
            _logger.LogError(ex, "Failed to start clipboard monitoring");
            throw;
        }
    }

    /// <summary>
    /// Stops monitoring clipboard for changes.
    /// </summary>
    public async Task StopMonitoringAsync()
    {
        if (!_isMonitoring)
        {
            _logger.LogDebug("Clipboard monitoring not active, skipping stop");
            return;
        }

        try
        {
            _isMonitoring = false;
            _logger.LogInformation("Clipboard monitoring stopped");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error stopping clipboard monitoring");
            throw;
        }

        await Task.CompletedTask;
    }

    /// <summary>
    /// Processes text content from the clipboard manually.
    /// For testing and integration purposes. Real clipboard monitoring added in STEP 12+.
    /// </summary>
    /// <param name="text">Text content to process.</param>
    public async Task ProcessTextManuallyAsync(string text)
    {
        if (!_isMonitoring)
        {
            _logger.LogWarning("Clipboard monitoring not active, cannot process text");
            return;
        }

        if (string.IsNullOrWhiteSpace(text))
        {
            _logger.LogDebug("Ignoring empty or whitespace-only clipboard text");
            return;
        }

        try
        {
            // Check for duplicate
            if (_duplicateDetector.IsDuplicate(text))
            {
                _logger.LogDebug("Duplicate content detected, skipping save");
                return;
            }

            // Create clip item
            var clip = ClipItemFactory.FromText(text);

            // Save to storage
            await _storageService.AppendClipAsync(clip);
            _logger.LogDebug("Clip saved to storage: {ClipTimestamp}", clip.Timestamp);

            // Index for search (continue on error)
            try
            {
                await _searchService.IndexClipAsync(clip);
                _logger.LogDebug("Clip indexed for search: {ClipTimestamp}", clip.Timestamp);
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Failed to index clip {ClipTimestamp}, continuing", clip.Timestamp);
            }

            // Publish event
            ClipboardChanged?.Invoke(this, new ClipboardChangedEventArgs { Clip = clip });
            _logger.LogInformation("New clip processed and saved: {ClipTimestamp} (length: {Length})", clip.Timestamp, text.Length);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing clipboard text");
            ClipboardChanged?.Invoke(this, new ClipboardChangedEventArgs { Error = ex });
        }
    }
}

