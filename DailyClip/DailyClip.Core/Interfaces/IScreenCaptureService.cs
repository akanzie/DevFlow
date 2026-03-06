using System.Drawing;

namespace DailyClip.Core.Interfaces;

/// <summary>
/// Service interface for screen capture functionality.
/// Supports region selection, active window, and fullscreen captures.
/// </summary>
public interface IScreenCaptureService
{
    /// <summary>
    /// Captures a specific region of the screen.
    /// </summary>
    /// <param name="bounds">Screen region bounds (x, y, width, height) in pixels.</param>
    /// <returns>Raw PNG image bytes.</returns>
    /// <exception cref="InvalidOperationException">Thrown if capture fails.</exception>
    Task<byte[]> CaptureRegionAsync(Rectangle bounds);

    /// <summary>
    /// Captures the currently active window.
    /// </summary>
    /// <returns>Raw PNG image bytes.</returns>
    /// <exception cref="InvalidOperationException">Thrown if capture fails.</exception>
    Task<byte[]> CaptureActiveWindowAsync();

    /// <summary>
    /// Captures the entire screen (all monitors).
    /// </summary>
    /// <returns>Raw PNG image bytes.</returns>
    /// <exception cref="InvalidOperationException">Thrown if capture fails.</exception>
    Task<byte[]> CaptureFullscreenAsync();
}
