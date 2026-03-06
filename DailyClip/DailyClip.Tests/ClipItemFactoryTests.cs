namespace DailyClip.Tests;

using DailyClip.Core.Helpers;
using FluentAssertions;
using Xunit;

/// <summary>
/// Unit tests for ClipItemFactory helper methods.
/// </summary>
public class ClipItemFactoryTests
{
    [Fact]
    public void FromText_WithValidText_CreatesClipItem()
    {
        // Arrange
        var text = "Hello, World!";

        // Act
        var clip = ClipItemFactory.FromText(text);

        // Assert
        clip.Should().NotBeNull();
        clip.Type.Should().Be("text");
        clip.Content.Should().Be(text);
        clip.SourceUrl.Should().Be("clipboard");
        clip.Timestamp.Should().BeCloseTo(DateTimeOffset.Now, TimeSpan.FromSeconds(1));
    }

    [Fact]
    public void FromText_WithSourceUrl_IncludesSourceUrl()
    {
        // Arrange
        var text = "From a website";
        var url = "https://example.com";

        // Act
        var clip = ClipItemFactory.FromText(text, url);

        // Assert
        clip.SourceUrl.Should().Be(url);
    }

    [Fact]
    public void FromText_WithNull_ThrowsArgumentNullException()
    {
        // Act & Assert
        Assert.Throws<ArgumentNullException>(() => ClipItemFactory.FromText(null!));
    }

    [Fact]
    public void FromCode_WithLanguage_CreatesCodeClip()
    {
        // Arrange
        var code = "public void HelloWorld() { }";
        var language = "csharp";

        // Act
        var clip = ClipItemFactory.FromCode(code, language);

        // Assert
        clip.Type.Should().Be("code:csharp");
        clip.Content.Should().Be(code);
    }

    [Fact]
    public void FromCode_WithoutLanguage_CreatesGenericCodeClip()
    {
        // Arrange
        var code = "cout << 'Hello' << endl;";

        // Act
        var clip = ClipItemFactory.FromCode(code);

        // Assert
        clip.Type.Should().Be("code");
        clip.Content.Should().Be(code);
    }

    [Fact]
    public void FromCode_WithNull_ThrowsArgumentNullException()
    {
        // Act & Assert
        Assert.Throws<ArgumentNullException>(() => ClipItemFactory.FromCode(null!));
    }

    [Fact]
    public void FromJson_WithValidJson_CreatesJsonClip()
    {
        // Arrange
        var json = @"{ ""name"": ""test"", ""value"": 123 }";

        // Act
        var clip = ClipItemFactory.FromJson(json);

        // Assert
        clip.Type.Should().Be("json");
        clip.Content.Should().Be(json);
    }

    [Fact]
    public void FromJson_WithNull_ThrowsArgumentNullException()
    {
        // Act & Assert
        Assert.Throws<ArgumentNullException>(() => ClipItemFactory.FromJson(null!));
    }

    [Fact]
    public void FromMarkdown_WithValidMarkdown_CreatesMarkdownClip()
    {
        // Arrange
        var markdown = "# Heading\n- Bullet 1\n- Bullet 2";

        // Act
        var clip = ClipItemFactory.FromMarkdown(markdown);

        // Assert
        clip.Type.Should().Be("markdown");
        clip.Content.Should().Be(markdown);
    }

    [Fact]
    public void FromMarkdown_WithNull_ThrowsArgumentNullException()
    {
        // Act & Assert
        Assert.Throws<ArgumentNullException>(() => ClipItemFactory.FromMarkdown(null!));
    }

    [Fact]
    public void AllFactoryMethods_ProduceValidClips()
    {
        // Arrange & Act
        var clips = new[]
        {
            ClipItemFactory.FromText("text"),
            ClipItemFactory.FromCode("code"),
            ClipItemFactory.FromJson("{}"),
            ClipItemFactory.FromMarkdown("# md"),
        };

        // Assert
        clips.Should().AllSatisfy(c =>
        {
            c.Should().NotBeNull();
            c.SourceUrl.Should().NotBeNullOrWhiteSpace();
            c.Content.Should().NotBeNullOrEmpty();
        });
    }
}
