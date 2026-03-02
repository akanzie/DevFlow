import Foundation

class FeedService {
    static let shared = FeedService()
    
    private init() {}
    
    let rssFeeds: [(name: String, url: String)] = [
        ("Dev.to", "https://dev.to/feed"),
        ("Viblo", "https://viblo.asia/rss"),
        ("Hacker News", "https://news.ycombinator.com/rss"),
        ("Medium - Programming", "https://medium.com/tag/programming/latest?format=rss"),
    ]
    
    func fetchFeeds() async -> [FeedItem] {
        var items: [FeedItem] = []
        
        // Mock data for MVP - in production, parse RSS feeds
        let mockItems: [FeedItem] = [
            FeedItem(
                title: "SwiftUI Performance Tips 2026",
                description: "Learn advanced techniques to optimize your SwiftUI apps",
                url: "https://dev.to/example",
                source: "Dev.to",
                publicationDate: Date()
            ),
            FeedItem(
                title: "Burnout Prevention for Developers",
                description: "Strategies to maintain work-life balance",
                url: "https://viblo.asia/example",
                source: "Viblo",
                publicationDate: Date().addingTimeInterval(-3600)
            ),
            FeedItem(
                title: "iOS 18 Features for Developers",
                description: "New APIs and capabilities in iOS 18",
                url: "https://news.ycombinator.com/example",
                source: "Hacker News",
                publicationDate: Date().addingTimeInterval(-7200)
            ),
        ]
        
        items.append(contentsOf: mockItems)
        return items.sorted { $0.publicationDate > $1.publicationDate }
    }
    
    func cacheFeedItem(_ item: FeedItem) {
        // Used by the app to cache items locally
    }
}
