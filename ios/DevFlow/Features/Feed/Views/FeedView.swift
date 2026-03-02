import SwiftUI
import SwiftData

struct FeedView: View {
    @State private var feedItems: [FeedItem] = []
    @State private var isLoading = true
    @Environment(\.modelContext) private var context
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color(UIColor.systemBackground)
                    .ignoresSafeArea()
                
                if isLoading {
                    ProgressView()
                } else if feedItems.isEmpty {
                    emptyState
                } else {
                    feedList
                }
            }
            .navigationTitle("Feed")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button(action: refreshFeed) {
                        Image(systemName: "arrow.clockwise")
                    }
                }
            }
            .onAppear {
                loadFeed()
            }
        }
    }
    
    private var emptyState: some View {
        VStack(spacing: 16) {
            Image(systemName: "newspaper")
                .font(.system(size: 48))
                .foregroundColor(.gray)
            
            Text("Không có bài viết nào")
                .font(.headline)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
    
    private var feedList: some View {
        ScrollView {
            VStack(spacing: 12) {
                ForEach(feedItems, id: \.self) { item in
                    FeedItemView(item: item) {
                        saveForLater(item)
                    }
                }
            }
            .padding()
        }
    }
    
    private func loadFeed() {
        isLoading = true
        Task {
            let items = await FeedService.shared.fetchFeeds()
            DispatchQueue.main.async {
                feedItems = items
                isLoading = false
            }
        }
    }
    
    private func refreshFeed() {
        loadFeed()
    }
    
    private func saveForLater(_ item: FeedItem) {
        if let index = feedItems.firstIndex(of: item) {
            feedItems[index].isSavedForLater.toggle()
            FeedService.shared.cacheFeedItem(feedItems[index])
        }
    }
}

struct FeedItemView: View {
    let item: FeedItem
    let onSave: () -> Void
    @State private var isExpanded = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .top, spacing: 12) {
                VStack(alignment: .leading, spacing: 8) {
                    Text(item.title)
                        .font(.headline)
                        .lineLimit(2)
                    
                    Text(item.source)
                        .font(.caption)
                        .foregroundColor(.secondary)
                    
                    Text(item.publicationDate.formatted(date: .abbreviated, time: .shortened))
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                Button(action: onSave) {
                    Image(systemName: item.isSavedForLater ? "bookmark.fill" : "bookmark")
                        .foregroundColor(.blue)
                }
            }
            
            if isExpanded {
                Divider()
                
                Text(item.description)
                    .font(.caption)
                    .lineLimit(nil)
                
                Link(destination: URL(string: item.url) ?? URL(fileURLWithPath: "")) {
                    HStack {
                        Text("Đọc tiếp")
                            .font(.caption)
                        Image(systemName: "arrow.up.right")
                            .font(.caption2)
                    }
                    .foregroundColor(.blue)
                }
            }
            
            Button(action: { withAnimation { isExpanded.toggle() } }) {
                Text(isExpanded ? "Thu gọn" : "Xem thêm")
                    .font(.caption)
                    .foregroundColor(.blue)
            }
        }
        .padding()
        .background(Color(UIColor.secondarySystemBackground))
        .cornerRadius(8)
    }
}

#Preview {
    FeedView()
}
