namespace DailyClip.Core.Interfaces;

using DailyClip.Core.Entities;

/// <summary>
/// Service interface for monitoring Windows clipboard changes in real-time.
/// </summary>
public interface IClipboardMonitor
{
    /// <summary>
    /// Starts monitoring clipboard for changes.
    /// </summary>
    /// <returns>A task representing the asynchronous operation.</returns>
    Task StartMonitoringAsync();

    /// <summary>
    /// Stops monitoring clipboard.
    /// </summary>
    /// <returns>A task representing the asynchronous operation.</returns>
    Task StopMonitoringAsync();

    /// <summary>
    /// Event fired when clipboard content changes (and passes duplicate check).
    /// </summary>
    event EventHandler<ClipboardChangedEventArgs>? ClipboardChanged;
}

/// <summary>
/// Event arguments for clipboard changes.
/// </summary>
public class ClipboardChangedEventArgs : EventArgs
{
    /// <summary>
    /// Gets or sets the clip item that was copied (null if error occurred).
    /// </summary>
    public ClipItem? Clip { get; set; }

    /// <summary>
    /// Gets or sets the error if clipboard read failed (null if successful).
    /// </summary>
    public Exception? Error { get; set; }
}
