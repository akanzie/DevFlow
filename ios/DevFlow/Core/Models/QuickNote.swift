import Foundation
import SwiftData

@Model
final class QuickNote {
    var content: String
    var createdAt: Date = Date()
    var updatedAt: Date = Date()
    var tags: [String] = []
    var isVoiceNote: Bool = false
    var voiceNotePath: String?
    var isFavorite: Bool = false
    var isArchived: Bool = false
    
    init(
        content: String,
        tags: [String] = [],
        isVoiceNote: Bool = false
    ) {
        self.content = content
        self.tags = tags
        self.isVoiceNote = isVoiceNote
    }
    
    var tagsString: String {
        tags.map { "#\($0)" }.joined(separator: " ")
    }
    
    func addTag(_ tag: String) {
        let cleanTag = tag.lowercased().trimmingCharacters(in: .whitespaces)
        if !tags.contains(cleanTag) && !cleanTag.isEmpty {
            tags.append(cleanTag)
        }
    }
    
    func removeTag(_ tag: String) {
        tags.removeAll { $0 == tag.lowercased() }
    }
}

@Model
final class FeedItem {
    var title: String
    var description: String
    var url: String
    var source: String
    var imageUrl: String?
    var publicationDate: Date
    var isRead: Bool = false
    var isSavedForLater: Bool = false
    var createdAt: Date = Date()
    
    init(
        title: String,
        description: String,
        url: String,
        source: String,
        imageUrl: String? = nil,
        publicationDate: Date
    ) {
        self.title = title
        self.description = description
        self.url = url
        self.source = source
        self.imageUrl = imageUrl
        self.publicationDate = publicationDate
    }
}
