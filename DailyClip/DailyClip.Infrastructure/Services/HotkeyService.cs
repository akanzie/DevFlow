namespace DailyClip.Infrastructure.Services;

using DailyClip.Core.Interfaces;
using Microsoft.Extensions.Logging;
using System.ComponentModel;
using System.Runtime.InteropServices;

/// <summary>
/// Implementation of IHotkeyService using Windows API for global hotkey registration.
/// Registers system-wide hotkeys that trigger even when the application is not in focus.
/// </summary>
public class HotkeyService : IHotkeyService
{
    private readonly ILogger<HotkeyService> _logger;
    private readonly Dictionary<int, Action> _hotkeyCallbacks = new();
    private IntPtr _windowHandle;
    private readonly object _lockObject = new();

    // Windows API constants
    private const int WM_HOTKEY = 0x0312;
    private const int WS_EX_TOOLWINDOW = 0x00000080;
    private const int WS_OVERLAPPED = 0x00000000;

    // P/Invoke declarations
    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool RegisterHotKey(IntPtr hWnd, int id, int fsModifiers, int vk);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool UnregisterHotKey(IntPtr hWnd, int id);

    [DllImport("user32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern IntPtr CreateWindowEx(
        int dwExStyle,
        string lpClassName,
        string lpWindowName,
        int dwStyle,
        int x,
        int y,
        int nWidth,
        int nHeight,
        IntPtr hWndParent,
        IntPtr hMenu,
        IntPtr hInstance,
        IntPtr lpParam);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool DestroyWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    private static extern bool GetMessage(out MSG lpMsg, IntPtr hWnd, uint wMsgFilterMin, uint wMsgFilterMax);

    [DllImport("user32.dll")]
    private static extern bool TranslateMessage(ref MSG lpMsg);

    [DllImport("user32.dll")]
    private static extern IntPtr DispatchMessage(ref MSG lpMsg);

    [DllImport("kernel32.dll")]
    private static extern IntPtr GetModuleHandle(string lpModuleName);

    [StructLayout(LayoutKind.Sequential)]
    private struct MSG
    {
        public IntPtr hwnd;
        public int message;
        public IntPtr wParam;
        public IntPtr lParam;
        public uint time;
        public int pt_x;
        public int pt_y;
    }

    /// <summary>
    /// Initializes a new instance of the HotkeyService class.
    /// </summary>
    public HotkeyService(ILogger<HotkeyService> logger)
    {
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        InitializeWindow();
    }

    /// <summary>
    /// Creates a hidden window to receive hotkey messages.
    /// </summary>
    private void InitializeWindow()
    {
        try
        {
            // Register window class
            const string windowClassName = "DailyClipHotkeyWindow";
            var hInstance = GetModuleHandle(null);

            _windowHandle = CreateWindowEx(
                WS_EX_TOOLWINDOW,
                "STATIC",
                windowClassName,
                WS_OVERLAPPED,
                0, 0, 0, 0,
                IntPtr.Zero,
                IntPtr.Zero,
                hInstance,
                IntPtr.Zero
            );

            if (_windowHandle == IntPtr.Zero)
            {
                _logger.LogWarning("Failed to create hidden window for hotkey capture");
            }
            else
            {
                _logger.LogInformation("Hotkey window initialized (handle: {WindowHandle})", _windowHandle);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to initialize hotkey window");
        }
    }

    /// <summary>
    /// Registers a global hotkey.
    /// </summary>
    public void RegisterHotkey(int hotkeyId, ModifierKeys modifiers, int key, Action callback)
    {
        ArgumentNullException.ThrowIfNull(callback);

        lock (_lockObject)
        {
            try
            {
                // Convert ModifierKeys enum to Windows API format
                int fsModifiers = 0;
                if ((modifiers & ModifierKeys.Alt) != 0)
                    fsModifiers |= 0x0001; // MOD_ALT
                if ((modifiers & ModifierKeys.Control) != 0)
                    fsModifiers |= 0x0002; // MOD_CONTROL
                if ((modifiers & ModifierKeys.Shift) != 0)
                    fsModifiers |= 0x0004; // MOD_SHIFT
                if ((modifiers & ModifierKeys.Win) != 0)
                    fsModifiers |= 0x0008; // MOD_WIN

                // Register the hotkey
                if (_windowHandle == IntPtr.Zero)
                {
                    _logger.LogError("Cannot register hotkey: window handle is null");
                    throw new InvalidOperationException("Hotkey window not initialized");
                }

                if (!RegisterHotKey(_windowHandle, hotkeyId, fsModifiers, key))
                {
                    int errorCode = Marshal.GetLastWin32Error();
                    _logger.LogError("Failed to register hotkey (ID: {HotkeyId}, error: {ErrorCode})", hotkeyId, errorCode);
                    throw new InvalidOperationException($"Failed to register hotkey: error {errorCode}");
                }

                // Store the callback
                _hotkeyCallbacks[hotkeyId] = callback;
                _logger.LogInformation("Hotkey registered (ID: {HotkeyId}, modifiers: {Modifiers}, key: {Key})", 
                    hotkeyId, modifiers, key);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error registering hotkey");
                throw;
            }
        }
    }

    /// <summary>
    /// Unregisters all hotkeys.
    /// </summary>
    public void UnregisterAll()
    {
        lock (_lockObject)
        {
            try
            {
                if (_windowHandle == IntPtr.Zero)
                {
                    _logger.LogWarning("Cannot unregister hotkeys: window handle is null");
                    return;
                }

                foreach (var hotkeyId in _hotkeyCallbacks.Keys.ToList())
                {
                    if (UnregisterHotKey(_windowHandle, hotkeyId))
                    {
                        _logger.LogInformation("Hotkey unregistered (ID: {HotkeyId})", hotkeyId);
                    }
                    else
                    {
                        int errorCode = Marshal.GetLastWin32Error();
                        _logger.LogWarning("Failed to unregister hotkey (ID: {HotkeyId}, error: {ErrorCode})", 
                            hotkeyId, errorCode);
                    }
                }

                _hotkeyCallbacks.Clear();

                // Destroy the window
                if (!DestroyWindow(_windowHandle))
                {
                    _logger.LogWarning("Failed to destroy hotkey window");
                }
                else
                {
                    _logger.LogInformation("Hotkey window destroyed");
                }

                _windowHandle = IntPtr.Zero;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error unregistering hotkeys");
            }
        }
    }

    /// <summary>
    /// Destructor to ensure hotkeys are unregistered.
    /// </summary>
    ~HotkeyService()
    {
        try
        {
            UnregisterAll();
        }
        catch (Exception ex)
        {
            _logger?.LogError(ex, "Error in HotkeyService destructor");
        }
    }

    /// <summary>
    /// Handles hotkey press events (called from window message loop).
    /// </summary>
    internal void OnHotkeyPressed(int hotkeyId)
    {
        lock (_lockObject)
        {
            if (_hotkeyCallbacks.TryGetValue(hotkeyId, out var callback))
            {
                try
                {
                    _logger.LogDebug("Hotkey pressed (ID: {HotkeyId})", hotkeyId);
                    callback?.Invoke();
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error executing hotkey callback (ID: {HotkeyId})", hotkeyId);
                }
            }
            else
            {
                _logger.LogWarning("Received hotkey press for unknown ID: {HotkeyId}", hotkeyId);
            }
        }
    }
}
