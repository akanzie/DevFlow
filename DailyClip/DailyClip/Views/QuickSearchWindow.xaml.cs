using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using DailyClip.Core.Interfaces;
using DailyClip.Core.Models;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading.Tasks;
using System;
using Windows.ApplicationModel.DataTransfer;
using Microsoft.UI;

namespace DailyClip.Views;

/// <summary>
/// Quick Search window for searching clipboard history.
/// </summary>
public sealed partial class QuickSearchWindow : Window
{
    private readonly ISearchService _searchService;
    private ObservableCollection<ClipSearchResult> _searchResults = new();

public QuickSearchWindow(ISearchService searchService)
    {
        this.InitializeComponent();
        _searchService = searchService;
        ResultsListView.ItemsSource = _searchResults;

        // Position window in center of screen
        var hwnd = Win32Interop.GetWindowFromWindowId(this.WindowId);
        var displayArea = DisplayArea.GetFromWindowId(this.WindowId, DisplayAreaFallback.Primary);
        this.WindowStartupLocation = WindowStartupLocation.Manual;
        this.Left = displayArea.WorkArea.Width / 2 - this.Width / 2;
        this.Top = displayArea.WorkArea.Height / 2 - this.Height / 2;

        // Focus search box
        SearchTextBox.Focus(FocusState.Programmatic);
    }

    private async void SearchTextBox_TextChanged(object sender, TextChangedEventArgs e)
    {
        var query = SearchTextBox.Text;
        if (string.IsNullOrWhiteSpace(query))
        {
            _searchResults.Clear();
            return;
        }

        try
        {
            var results = await _searchService.SearchAsync(query);
            _searchResults.Clear();
            foreach (var result in results.Take(10)) // Limit to 10 results
            {
                _searchResults.Add(result);
            }
        }
        catch (Exception ex)
        {
            // Log error, but don't crash
            System.Diagnostics.Debug.WriteLine($"Search error: {ex.Message}");
        }
    }

    private void SearchTextBox_KeyDown(object sender, KeyRoutedEventArgs e)
    {
        if (e.Key == Windows.System.VirtualKey.Escape)
        {
            this.Close();
        }
        else if (e.Key == Windows.System.VirtualKey.Enter && ResultsListView.SelectedItem != null)
        {
            SelectResult(ResultsListView.SelectedItem as ClipSearchResult);
        }
        else if (e.Key == Windows.System.VirtualKey.Down && _searchResults.Any())
        {
            ResultsListView.SelectedIndex = 0;
            ResultsListView.Focus(FocusState.Programmatic);
        }
    }

    private void ResultsListView_ItemClick(object sender, ItemClickEventArgs e)
    {
        if (e.ClickedItem is ClipSearchResult result)
        {
            SelectResult(result);
        }
    }

    private void SelectResult(ClipSearchResult? result)
    {
        if (result == null) return;

        // Copy to clipboard
        var dataPackage = new DataPackage();
        dataPackage.SetText(result.Content);
        Clipboard.SetContent(dataPackage);

        this.Close();
    }

    private void SearchTextBox_GotFocus(object sender, RoutedEventArgs e)
    {
        SearchTextBox.SelectAll();
    }
}
