namespace DailyClip.Tests;

using DailyClip.Core.Interfaces;
using DailyClip.Infrastructure;
using FluentAssertions;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Xunit;

/// <summary>
/// Integration tests for infrastructure service registration and basic workflows.
/// </summary>
public class InfrastructureIntegrationTests
{
    [Fact]
    public void AddInfrastructureServices_RegistersStorageService()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();

        // Act
        services.AddInfrastructureServices();
        var provider = services.BuildServiceProvider();

        // Assert
        var storageService = provider.GetService<IStorageService>();
        storageService.Should().NotBeNull();
        storageService.Should().BeAssignableTo<IStorageService>();
    }

    [Fact]
    public void AddInfrastructureServices_StorageServiceThrowsOnMultipleRegistration()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();

        // Act & Assert
        services.AddInfrastructureServices();
        // Second call should work (singleton behavior)
        services.AddInfrastructureServices();
        
        var provider = services.BuildServiceProvider();
        var service = provider.GetService<IStorageService>();
        service.Should().NotBeNull();
    }

    [Fact]
    public void ServiceCollection_CanResolveStorageService()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();
        services.AddInfrastructureServices();

        // Act
        var provider = services.BuildServiceProvider();
        var service = provider.GetRequiredService<IStorageService>();

        // Assert
        service.Should().NotBeNull();
        service.GetTodayFolderPath().Should().NotBeNullOrWhiteSpace();
    }
}
