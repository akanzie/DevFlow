namespace DailyClip.Infrastructure;

using DailyClip.Core.Interfaces;
using DailyClip.Infrastructure.Services;
using Microsoft.Extensions.DependencyInjection;

/// <summary>
/// Extension methods for registering infrastructure services in dependency injection container.
/// </summary>
public static class ServiceCollectionExtensions
{
    /// <summary>
    /// Adds infrastructure layer services to the dependency injection container.
    /// </summary>
    /// <param name="services">The service collection to add to.</param>
    /// <returns>The service collection for chaining.</returns>
    public static IServiceCollection AddInfrastructureServices(this IServiceCollection services)
    {
        ArgumentNullException.ThrowIfNull(services);

        // Register file storage service
        services.AddSingleton<IStorageService, FileStorageService>();

        // Register duplicate detector for clipboard monitoring
        services.AddSingleton(new DuplicateDetector(windowSeconds: 10));

        // Register clipboard monitor service
        services.AddSingleton<IClipboardMonitor, ClipboardMonitorService>();

        // Register search service (In-memory for MVP) - STEP 11
        services.AddSingleton<ISearchService, InMemorySearchService>();

        // Register hotkey service - STEP 12
        services.AddSingleton<IHotkeyService, HotkeyService>();

        // Register screen capture service - STEP 13
        services.AddSingleton<IScreenCaptureService, ScreenCaptureService>();

        // Register note service - STEP 14
        services.AddSingleton<INoteService, NoteService>();

        return services;
    }
}
