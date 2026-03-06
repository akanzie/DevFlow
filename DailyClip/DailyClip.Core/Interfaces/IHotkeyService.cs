namespace DailyClip.Core.Interfaces;

/// <summary>
/// Service interface for system-wide global hotkey registration and handling.
/// </summary>
public interface IHotkeyService
{
    /// <summary>
    /// Registers a global hotkey.
    /// </summary>
    /// <param name="hotkeyId">Unique identifier for this hotkey.</param>
    /// <param name="modifiers">Modifier keys (Ctrl, Alt, Shift, Win).</param>
    /// <param name="key">Virtual key code.</param>
    /// <param name="callback">Action to invoke when hotkey is pressed.</param>
    /// <exception cref="InvalidOperationException">Thrown if hotkey registration fails.</exception>
    void RegisterHotkey(int hotkeyId, ModifierKeys modifiers, int key, Action callback);

    /// <summary>
    /// Unregisters all hotkeys.
    /// </summary>
    void UnregisterAll();
}

/// <summary>
/// Hotkey modifier keys enumeration.
/// </summary>
[Flags]
public enum ModifierKeys
{
    None = 0,
    Alt = 1,
    Control = 2,
    Shift = 4,
    Win = 8,
}
