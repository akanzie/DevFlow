import SwiftUI
import SwiftData

struct NotesView: View {
    @Environment(\.modelContext) private var context
    @Query(sort: \QuickNote.createdAt, order: .reverse) private var notes: [QuickNote]
    @State private var showAddNote = false
    @State private var searchText = ""
    
    var filteredNotes: [QuickNote] {
        if searchText.isEmpty {
            return notes
        }
        return notes.filter { note in
            note.content.localizedCaseInsensitiveContains(searchText) ||
            note.tags.contains { $0.localizedCaseInsensitiveContains(searchText) }
        }
    }
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color(UIColor.systemBackground)
                    .ignoresSafeArea()
                
                VStack {
                    SearchBar(text: $searchText)
                        .padding()
                    
                    if filteredNotes.isEmpty {
                        emptyState
                    } else {
                        notesList
                    }
                }
                
                VStack {
                    HStack {
                        Spacer()
                        Button(action: { showAddNote = true }) {
                            Image(systemName: "plus.circle.fill")
                                .font(.system(size: 56))
                                .foregroundColor(.accentColor)
                        }
                        .padding()
                    }
                    Spacer()
                }
            }
            .navigationTitle("Notes")
            .navigationBarTitleDisplayMode(.inline)
            .sheet(isPresented: $showAddNote) {
                AddNoteSheet(isPresented: $showAddNote) { note in
                    context.insert(note)
                }
            }
        }
    }
    
    private var emptyState: some View {
        VStack(spacing: 16) {
            Image(systemName: "note.text")
                .font(.system(size: 48))
                .foregroundColor(.gray)
            
            Text("Chưa có note nào")
                .font(.headline)
            
            Text("Ghi lại ý tưởng và học hỏi của bạn")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(UIColor.systemBackground))
    }
    
    private var notesList: some View {
        ScrollView {
            VStack(spacing: 12) {
                ForEach(filteredNotes, id: \.self) { note in
                    NoteRowView(note: note)
                        .contextMenu {
                            Button("Yêu thích", systemImage: "heart") {
                                note.isFavorite.toggle()
                            }
                            
                            Button("Lưu lại", systemImage: "bookmark") {}
                            
                            Button("Xóa", systemImage: "trash", role: .destructive) {
                                context.delete(note)
                            }
                        }
                }
            }
            .padding()
        }
    }
}

struct NoteRowView: View {
    let note: QuickNote
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(note.content)
                    .lineLimit(2)
                    .font(.headline)
                
                Spacer()
                
                if note.isFavorite {
                    Image(systemName: "heart.fill")
                        .foregroundColor(.red)
                }
                
                if note.isVoiceNote {
                    Image(systemName: "mic.fill")
                        .foregroundColor(.blue)
                }
            }
            
            if !note.tags.isEmpty {
                HStack(spacing: 6) {
                    ForEach(note.tags, id: \.self) { tag in
                        Text("#\(tag)")
                            .font(.caption)
                            .foregroundColor(.blue)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(Color.blue.opacity(0.2))
                            .cornerRadius(4)
                    }
                }
            }
            
            Text(note.createdAt.formatted(date: .abbreviated, time: .shortened))
                .font(.caption2)
                .foregroundColor(.secondary)
        }
        .padding()
        .background(Color(UIColor.secondarySystemBackground))
        .cornerRadius(8)
    }
}

struct SearchBar: View {
    @Binding var text: String
    
    var body: some View {
        HStack {
            Image(systemName: "magnifyingglass")
                .foregroundColor(.gray)
            
            TextField("Tìm note...", text: $text)
            
            if !text.isEmpty {
                Button(action: { text = "" }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.gray)
                }
            }
        }
        .padding(8)
        .background(Color(UIColor.secondarySystemBackground))
        .cornerRadius(8)
    }
}

struct AddNoteSheet: View {
    @Binding var isPresented: Bool
    var onAdd: (QuickNote) -> Void
    
    @State private var content = ""
    @State private var tags = ""
    @State private var isVoiceNote = false
    
    var body: some View {
        NavigationStack {
            Form {
                Section("Note") {
                    TextEditor(text: $content)
                        .frame(height: 150)
                    
                    HStack {
                        TextField("Tags (cách nhau bằng dấu phẩy)", text: $tags)
                        
                        Button(action: { isVoiceNote.toggle() }) {
                            Image(systemName: isVoiceNote ? "mic.fill" : "mic")
                                .foregroundColor(isVoiceNote ? .blue : .gray)
                        }
                    }
                }
                
                Button(action: addNote) {
                    Text("Lưu Note")
                }
                .disabled(content.trimmingCharacters(in: .whitespaces).isEmpty)
            }
            .navigationTitle("Thêm Note mới")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Hủy") { isPresented = false }
                }
            }
        }
    }
    
    private func addNote() {
        let parsedTags = tags
            .split(separator: ",")
            .map { $0.trimmingCharacters(in: .whitespaces).lowercased() }
            .filter { !$0.isEmpty }
        
        let note = QuickNote(
            content: content,
            tags: parsedTags,
            isVoiceNote: isVoiceNote
        )
        onAdd(note)
        isPresented = false
    }
}

#Preview {
    NotesView()
        .modelContainer(for: QuickNote.self)
}
