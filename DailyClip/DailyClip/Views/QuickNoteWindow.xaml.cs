using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using DailyClip.Core.Interfaces;
using System;
using System.Threading.Tasks;

namespace DailyClip.Views;

/// <summary>
/// Quick Note window for creating quick notes.
/// </summary>
public sealed partial class QuickNoteWindow : Window
{
    private readonly INoteService _noteService;

    public QuickNoteWindow(INoteService noteService)
    {
        this.InitializeComponent();
        _noteService = noteService;

        // Position window in center of screen
        var displayArea = DisplayArea.GetFromWindowId(Win32Interop.GetWindowIdFromWindow(this.WindowHandle), DisplayAreaFallback.Primary);
        this.WindowStartupLocation = WindowStartupLocation.Manual;
        this.Left = displayArea.WorkArea.Width / 2 - this.Width / 2;
        this.Top = displayArea.WorkArea.Height / 2 - this.Height / 2;

        // Focus note box
        NoteTextBox.Focus(FocusState.Programmatic);
    }

    private async void SaveButton_Click(object sender, RoutedEventArgs e)
    {
        await SaveNoteAsync();
    }

    private void CancelButton_Click(object sender, RoutedEventArgs e)
    {
        this.Close();
    }

    private void NoteTextBox_KeyDown(object sender, KeyRoutedEventArgs e)
    {
        if (e.Key == Windows.System.VirtualKey.Escape)
        {
            this.Close();
        }
        else if (e.Key == Windows.System.VirtualKey.S && (e.KeyModifiers & Windows.System.VirtualKeyModifiers.Control) == Windows.System.VirtualKeyModifiers.Control)
        {
            e.Handled = true;
            _ = SaveNoteAsync();
        }
    }

    private async Task SaveNoteAsync()
    {
        var content = NoteTextBox.Text?.Trim();
        if (string.IsNullOrWhiteSpace(content))
        {
            return;
        }

        try
        {
            await _noteService.SaveNoteAsync(content);
            this.Close();
        }
        catch (Exception ex)
        {
            // Show error message
            var dialog = new ContentDialog
            {
                Title = "Error",
                Content = $"Failed to save note: {ex.Message}",
                CloseButtonText = "OK",
                XamlRoot = this.Content.XamlRoot
            };
            _ = dialog.ShowAsync();
        }
    }

    private void NoteTextBox_GotFocus(object sender, RoutedEventArgs e)
    {
        NoteTextBox.SelectAll();
    }
}
