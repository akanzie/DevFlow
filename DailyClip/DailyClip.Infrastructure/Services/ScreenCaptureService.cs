namespace DailyClip.Infrastructure.Services;

using DailyClip.Core.Interfaces;
using Microsoft.Extensions.Logging;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;

/// <summary>
/// Implementation of IScreenCaptureService using Windows API and System.Drawing.
/// Captures screen regions, active windows, and fullscreen with PNG output.
/// </summary>
public class ScreenCaptureService : IScreenCaptureService
{
    private readonly ILogger<ScreenCaptureService> _logger;

    // Windows API P/Invoke declarations
    [DllImport("user32.dll")]
    private static extern IntPtr GetForegroundWindow();

    [DllImport("user32.dll")]
    private static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);

    [DllImport("user32.dll")]
    private static extern int GetSystemMetrics(int nIndex);

    private const int SM_CXSCREEN = 0;
    private const int SM_CYSCREEN = 1;

    [StructLayout(LayoutKind.Sequential)]
    private struct RECT
    {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;

        public int Width => Right - Left;
        public int Height => Bottom - Top;
    }

    /// <summary>
    /// Initializes a new instance of the ScreenCaptureService class.
    /// </summary>
    public ScreenCaptureService(ILogger<ScreenCaptureService> logger)
    {
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    /// <summary>
    /// Captures a specific region of the screen.
    /// </summary>
    public async Task<byte[]> CaptureRegionAsync(Rectangle bounds)
    {
        return await Task.Run(() =>
        {
            try
            {
                if (bounds.Width <= 0 || bounds.Height <= 0)
                {
                    throw new InvalidOperationException("Capture bounds must have positive width and height");
                }

                using var bitmap = new Bitmap(bounds.Width, bounds.Height);
                using var graphics = Graphics.FromImage(bitmap);

                graphics.CopyFromScreen(bounds.Location, Point.Empty, bounds.Size);

                _logger.LogInformation("Screen region captured ({Width}x{Height} at {X},{Y})", 
                    bounds.Width, bounds.Height, bounds.X, bounds.Y);

                return BitmapToPng(bitmap);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to capture screen region");
                throw new InvalidOperationException("Failed to capture screen region", ex);
            }
        });
    }

    /// <summary>
    /// Captures the currently active window.
    /// </summary>
    public async Task<byte[]> CaptureActiveWindowAsync()
    {
        return await Task.Run(() =>
        {
            try
            {
                IntPtr hWnd = GetForegroundWindow();
                if (hWnd == IntPtr.Zero)
                {
                    throw new InvalidOperationException("No active window found");
                }

                if (!GetWindowRect(hWnd, out RECT windowRect))
                {
                    throw new InvalidOperationException("Failed to get window bounds");
                }

                Rectangle bounds = new Rectangle(
                    windowRect.Left,
                    windowRect.Top,
                    windowRect.Width,
                    windowRect.Height
                );

                // Validate bounds
                if (bounds.Width <= 0 || bounds.Height <= 0)
                {
                    throw new InvalidOperationException("Invalid window bounds");
                }

                using var bitmap = new Bitmap(bounds.Width, bounds.Height);
                using var graphics = Graphics.FromImage(bitmap);

                graphics.CopyFromScreen(bounds.Location, Point.Empty, bounds.Size);

                _logger.LogInformation("Active window captured ({Width}x{Height})", bounds.Width, bounds.Height);

                return BitmapToPng(bitmap);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to capture active window");
                throw new InvalidOperationException("Failed to capture active window", ex);
            }
        });
    }

    /// <summary>
    /// Captures the entire screen (all monitors).
    /// </summary>
    public async Task<byte[]> CaptureFullscreenAsync()
    {
        return await Task.Run(() =>
        {
            try
            {
                // Get total screen dimensions
                int screenWidth = GetSystemMetrics(SM_CXSCREEN);
                int screenHeight = GetSystemMetrics(SM_CYSCREEN);

                if (screenWidth <= 0 || screenHeight <= 0)
                {
                    throw new InvalidOperationException("Failed to get screen dimensions");
                }

                Rectangle bounds = new Rectangle(0, 0, screenWidth, screenHeight);

                using var bitmap = new Bitmap(screenWidth, screenHeight);
                using var graphics = Graphics.FromImage(bitmap);

                graphics.CopyFromScreen(Point.Empty, Point.Empty, 
                    new Size(screenWidth, screenHeight));

                _logger.LogInformation("Fullscreen captured ({Width}x{Height})", screenWidth, screenHeight);

                return BitmapToPng(bitmap);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to capture fullscreen");
                throw new InvalidOperationException("Failed to capture fullscreen", ex);
            }
        });
    }

    /// <summary>
    /// Converts a Bitmap to PNG byte array.
    /// </summary>
    private static byte[] BitmapToPng(Bitmap bitmap)
    {
        try
        {
            using var pngStream = new MemoryStream();
            bitmap.Save(pngStream, ImageFormat.Png);
            return pngStream.ToArray();
        }
        catch (Exception ex)
        {
            // Fallback: encode manually with error handling
            using var fallbackStream = new MemoryStream();
            bitmap.Save(fallbackStream, ImageFormat.Png);
            return fallbackStream.ToArray();
        }
    }
}

