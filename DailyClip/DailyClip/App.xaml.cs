using Microsoft.UI.Xaml;
using Microsoft.Extensions.DependencyInjection;
using DailyClip.Core.Config;
using DailyClip.Core.Interfaces;
using DailyClip.Infrastructure;
using Serilog;
using System;
using DailyClip.Views;

namespace DailyClip;

/// <summary>
/// Provides application-specific behavior to supplement the default Application class.
/// </summary>
public partial class App : Application
{
    private Window? m_window;
    private IServiceProvider? _serviceProvider;

    /// <summary>
    /// Initializes the singleton application object. This is the first line of authored code
    /// executed, and as such is the logical equivalent of main() or WinMain().
    /// </summary>
    public App()
    {
        this.InitializeComponent();
    }

    /// <summary>
    /// Invoked when the application is launched.
    /// </summary>
    /// <param name="args">Details about the launch request and process.</param>
    protected override void OnLaunched(Microsoft.UI.Xaml.LaunchActivatedEventArgs args)
    {
        // Configure Serilog
        Log.Logger = new LoggerConfiguration()
            .WriteTo.Debug()
            .WriteTo.File(Path.Combine(AppConfig.Paths.RootFolder, "logs", "dailyclip-.log"),
                rollingInterval: RollingInterval.Day)
            .CreateLogger();

        // Configure DI
        var services = new ServiceCollection();
        services.AddInfrastructureServices();
        _serviceProvider = services.BuildServiceProvider();

        // Start background services
        var clipboardMonitor = _serviceProvider.GetRequiredService<IClipboardMonitorService>();
        var hotkeyService = _serviceProvider.GetRequiredService<IHotkeyService>();

        // Register hotkeys
        hotkeyService.RegisterHotkey(AppConfig.Hotkeys.SearchHotkey, () => ShowQuickSearch());
        hotkeyService.RegisterHotkey(AppConfig.Hotkeys.NoteHotkey, () => ShowQuickNote());
        hotkeyService.RegisterHotkey(AppConfig.Hotkeys.CaptureHotkey, () => CaptureScreen());

        // The app runs in the background, no main window
        Log.Information("DailyClip started successfully");
    }

    private void ShowQuickSearch()
    {
        var searchService = _serviceProvider?.GetRequiredService<ISearchService>();

        if (searchService != null)
        {
            var window = new Views.QuickSearchWindow(searchService);
            window.Activate();
        }
    }

    private void ShowQuickNote()
    {
        var noteService = _serviceProvider?.GetRequiredService<INoteService>();

        if (noteService != null)
        {
            var window = new Views.QuickNoteWindow(noteService);
            window.Activate();
        }
    }

    private async void CaptureScreen()
    {
        var screenCaptureService = _serviceProvider?.GetRequiredService<IScreenCaptureService>();
        var clipboardService = _serviceProvider?.GetRequiredService<IClipboardService>();

        if (screenCaptureService != null && clipboardService != null)
        {
            try
            {
                var screenshot = await screenCaptureService.CaptureFullscreenAsync();
                // TODO: Save screenshot and copy to clipboard
                Log.Information("Screenshot captured, {Bytes} bytes", screenshot.Length);
            }
            catch (Exception ex)
            {
                Log.Error(ex, "Failed to capture screen");
            }
        }
    }
}
