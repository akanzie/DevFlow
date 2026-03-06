# Tài liệu Kiến trúc Hệ thống & Kiến trúc Phần mềm (Architecture Overview)  
**Tên phần mềm:** DailyClip – Công cụ tự động hóa ghi chú và lưu trữ dữ liệu cá nhân  
**Phiên bản:** 1.0  
**Ngày soạn thảo:** 06/03/2026  
**Tác giả:** Kiệt (với hỗ trợ tinh chỉnh)  

## 1. Giới thiệu & Mục đích

Tài liệu này giải thích sự khác biệt giữa **Kiến trúc Hệ thống** (System Architecture) và **Kiến trúc Phần mềm** (Software Architecture), làm rõ phạm vi, mục tiêu, và cách áp dụng chúng trong dự án DailyClip.

Mục tiêu:
- Làm rõ khái niệm để tránh nhầm lẫn trong giao tiếp team.
- Hướng dẫn thiết kế hệ thống DailyClip theo nguyên tắc kiến trúc chuẩn.
- Cung cấp Architecture Decision Records (ADRs) cho các quyết định thiết kế chính.

---

## 2. So sánh tổng quan: System Architecture vs. Software Architecture

| Tiêu chí                  | Kiến trúc Hệ thống (System Architecture)                          | Kiến trúc Phần mềm (Software Architecture)                       |
|---------------------------|-------------------------------------------------------------------|-------------------------------------------------------------------|
| **Phạm vi**               | Toàn bộ hệ thống (phần mềm + phần cứng + mạng + thiết bị ngoại vi + dịch vụ bên ngoài + con người nếu cần) | Chỉ phần mềm (components, modules, cách tổ chức và tương tác nội tại) |
| **Mức độ trừu tượng**     | Cao nhất, cấp conceptual (khung nhìn toàn cảnh)                    | Cao, nhưng thấp hơn system arch (chi tiết cấu trúc phần mềm)      |
| **Trọng tâm chính**       | Cấu trúc tổng thể, luồng dữ liệu giữa subsystem, tích hợp, deployment, scalability | Cấu trúc nội tại: layers, components, patterns, quality attributes (performance, testability, maintainability, security) |
| **Câu hỏi trả lời**       | Hệ thống gồm những phần nào? Chúng kết nối thế nào? Xử lý failure/scale/security tổng thể ra sao? | Phần mềm được chia thành module nào? Pattern gì? Code tổ chức thế nào để dễ test, bảo trì, mở rộng? |
| **Ví dụ thiết kế**        | Hệ thống e-commerce: Frontend web + Mobile app + Backend services + Database + CDN + Payment gateway + Monitoring | Backend service: Clean Architecture layers (domain, application, infrastructure), CQRS, Event Sourcing, DI container, Repository pattern |
| **Ai chịu trách nhiệm**   | System Architect, Solution Architect, Enterprise Architect        | Software Architect, Technical Lead, Principal Engineer           |
| **Tài liệu điển hình**    | Context diagram, Deployment diagram (C4 Level 1-2), Block diagram | Component diagram, Class diagram, Package diagram, ADRs (Architecture Decision Records) |

---

## 3. Mối quan hệ giữa hai loại kiến trúc

```
┌─────────────────────────────────────────────────┐
│    SYSTEM ARCHITECTURE (Ngoài cùng)             │
│  - Toàn bộ hệ thống: app + OS + storage + user  │
│  - Quyết định: Offline vs. Cloud? Desktop/Web?  │
│  - Tầm nhìn: Deployment model, Infrastructure   │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │  SOFTWARE ARCHITECTURE (Bên trong)          │ │
│  │  - Chỉ DailyClip app (.NET)                │ │
│  │  - Quyết định: Layers, patterns, structure  │ │
│  │  - Tầm nhìn: Code organization, modules     │ │
│  │                                             │ │
│  │  ┌──────────────────────────────────────┐  │ │
│  │  │ DETAILED DESIGN (Chi tiết nhất)       │  │ │
│  │  │ - Classes, interfaces, algorithms     │  │ │
│  │  │ - Database schema, sequences          │  │ │
│  │  └──────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

**Mối quan hệ:**
- System Architecture **bao quát và định hướng** Software Architecture.
  - System Arch: "Chúng ta build monolith desktop app offline-first" → Software Arch: "Dùng Clean Architecture + MVVM".
- Software Architecture **chi tiết hóa** System Architecture.
  - System Arch: "Dùng DuckDB cho search" → Software Arch: "Inject DuckDBSearchService qua DI container, FTS query performance optimization".
- Trong dự án **nhỏ** (desktop tool, app cá nhân): System Arch rất đơn giản, Software Arch chiếm ưu thế.
- Trong dự án **lớn** (enterprise, microservices): System Arch phức tạp, định hướng rõ ràng cho từng Software Arch của mỗi service.

---

## 4. Áp dụng vào DailyClip

### 4.1 Kiến trúc Hệ thống (System Architecture) cho DailyClip

**Phạm vi:**
- User (người dùng desktop Windows)
- DailyClip App (.NET 9 desktop application)
- Windows Operating System (API: Clipboard, Hotkey, Graphics Capture)
- File System (local storage)
- DuckDB (embedded database)

**Context Diagram (C4 Level 1):**
```
┌──────────┐
│   User   │
└────┬─────┘
     │ Ctrl+C, Alt+S, Alt+N, Alt+Space
     ↓
┌─────────────────────────────────────────┐
│       DailyClip Application              │
│  (Single .NET 9 WinUI 3 Desktop App)     │
└─────────────────────────────────────────┘
     ↑ Uses          ↓ Stores      ↗ Queries
┌──────────┐   ┌──────────────┐  ┌─────────┐
│ Windows  │   │ File System  │  │ DuckDB  │
│   API    │   │ [Root]/...   │  │  Index  │
└──────────┘   └──────────────┘  └─────────┘

No internet, no server, no cloud dependency (offline-first).
```

**Deployment Model:**
- Single executable (DailyClip.exe) + runtime (.NET 9).
- Config folder: `%AppData%/DailyClip/` (portable).
- Data folder: `%AppData%/DailyClip/data/[YYYY-MM-DD]/` (user-configurable).
- Single instance running (mutex lock).

**Key Design Decisions:**
- **Offline-first**: Không phụ thuộc server, dữ liệu 100% local.
- **Single executable**: Không microservices, không background services (nhờ .NET single-file publish).
- **Embedded DB**: DuckDB embedded, không cần database server.
- **Process model**: Main window + background monitor thread (clipboard & hotkey).

**Quality Attributes (System Level):**
- Reliability: Không mất dữ liệu khi crash, auto-save ngay khi clipboard thay đổi.
- Performance: App start < 2s, search < 500ms.
- Availability: Chạy nền 24/7, auto-start with Windows (optional).
- Portability: Dữ liệu có thể backup/restore dễ dàng (structure đơn giản).
- Security: Dữ liệu local (bảo mật mặc định), tùy chọn encrypt sau.

---

### 4.2 Kiến trúc Phần mềm (Software Architecture) cho DailyClip

**Pattern chính: Clean Architecture + MVVM**

```
┌─────────────────────────────────────────────────────────┐
│           PRESENTATION LAYER (WinUI 3)                  │
│  ┌────────────────┐  ┌────────────────┐                 │
│  │ Quick Search   │  │ Quick Note     │  TrayIcon       │
│  │    View        │  │    View        │  Gallery View   │
│  │ + ViewModel    │  │ + ViewModel    │                 │
│  └────────────────┘  └────────────────┘                 │
└────────────┬───────────────────────────────────────────┘
             │ INotifyPropertyChanged, Command
             ↓
┌─────────────────────────────────────────────────────────┐
│       APPLICATION LAYER (Services & Use Cases)          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  SearchUseCase, CaptureUseCase, NoteUseCase     │   │
│  │  · Orchestrate business logic                    │   │
│  │  · Call domain & infrastructure services         │   │
│  └──────────────────────────────────────────────────┘   │
│  [ISearchService, IStorageService, IHotkeyService...]   │
└────────────┬───────────────────────────────────────────┘
             │ Dependency Injection
             ↓
┌─────────────────────────────────────────────────────────┐
│       DOMAIN LAYER (Core Business Logic)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  ClipItem    │  │  DailyNote   │  │  Screenshot  │  │
│  │  (Entity)    │  │  (Entity)    │  │  (Entity)    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  [Domain Interfaces: IRepository, IRepository, ...]    │
└────────────┬───────────────────────────────────────────┘
             │ Implement
             ↓
┌─────────────────────────────────────────────────────────┐
│    INFRASTRUCTURE LAYER (External Systems & Impl)       │
│  ┌──────────────────┐  ┌──────────────────────────────┐ │
│  │ DuckDBSearch     │  │ FileSystemStorage            │ │
│  │ Service          │  │ Service                      │ │
│  └──────────────────┘  └──────────────────────────────┘ │
│  ┌──────────────────┐  ┌──────────────────────────────┐ │
│  │ WindowsHotkey    │  │ ClipboardMonitor             │ │
│  │ Service          │  │ (P/Invoke wrapper)           │ │
│  └──────────────────┘  └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Lý do chọn Clean Architecture:**
- Domain không phụ thuộc UI (testable).
- Dễ thay đổi infrastructure (DuckDB → SQLite là 1 line config).
- Dễ mock cho unit testing.
- Clear separation of concerns.

**Lý do chọn MVVM:**
- WinUI 3 native hỗ trợ MVVM/binding tốt.
- ViewModel không biết View (testable).
- Dễ integrate CommunityToolkit.Mvvm.

**Bổ sung Pattern:**
- **Repository Pattern**: ClipRepository, NoteRepository → abstract IO.
- **Service Locator / DI Container**: Microsoft.Extensions.DependencyInjection.
- **Event-Driven**: ClipboardMonitor fire event → SearchService incremental update.
- **Singleton Services**: HotkeyService, ClipboardMonitor (global, single instance).

---

## 5. Architecture Decision Records (ADRs)

### ADR-001: Chọn DuckDB thay vì SQLite cho Full-Text Search

**Status:** ACCEPTED  
**Context:** DailyClip cần tìm kiếm nhanh trên hàng chục nghìn clips/notes.  
**Decision:** Sử dụng DuckDB (embedded).  
**Rationale:**
- DuckDB columnar → FTS ~3-5x nhanh hơn SQLite FTS5 trên workload text-heavy.
- Hỗ trợ FTS native (Full-Text Search extension).
- Single-file database → dễ backup.
- OLAP/analytics quicker → future feature (statistics, trends).

**Alternatives considered:**
- SQLite + FTS5 (simpler, but slower for large text queries).
- Elasticsearch (overkill, need external service, more complex).

**Consequences:**
- +: Fast search, native FTS.
- -: Slight learning curve for DuckDB API, one more dependency.

---

### ADR-002: Monolith Desktop App (không Microservices)

**Status:** ACCEPTED  
**Context:** DailyClip là tool desktop cá nhân, offline-first, single-user.  
**Decision:** Single executable (.NET 9 WinUI 3) monolith, không chia microservices.  
**Rationale:**
- Không có server, không network complexity.
- User trên single machine → không cần distributed system.
- Monolith dễ deploy, debug, maintain cho small team / solo dev.
- Future sync có thể thêm via API layer (không cần refactor).

**Alternatives:**
- Docker + microservices (completely overkill và add complexity).
- Backend + Frontend separate (phức tạp hơn cần, không benefit).

**Consequences:**
- +: Simple, fast to develop, single deployment unit.
- -: Monolith có giới hạn scalability (nhưng không cần scale cho single-user app).

---

### ADR-003: JSONL for Clips (JSONL format)

**Status:** ACCEPTED  
**Context:** Cần lưu clipboard data, có thể hàng trăm items/ngày.  
**Decision:** Sử dụng JSONL (JSON Lines) format, append-only file.  
**Rationale:**
- Append-only → không cần rewrite toàn file mỗi lần có clip mới.
- Dễ parse từng dòng (mỗi dòng = 1 JSON object độc lập).
- Human-readable (debug dễ).
- Supports streaming (xử lý file lớn không phải load hết vào RAM).

**Alternatives:**
- Single JSON file (phải rewrite, khó append).
- Protobuf (binary, performance tốt hơn nhưng không human-readable).
- CSV (khó handle nested data).

**Consequences:**
- +: Efficient append, human-readable, streaming.
- -: Không có built-in validation schema (need manual check).

---

### ADR-004: WinUI 3 thay vì WPF

**Status:** ACCEPTED  
**Context:** Desktop app cần modern UI, native Windows 11 look-and-feel.  
**Decision:** Sử dụng WinUI 3 (Windows UI Library 3).  
**Rationale:**
- Modern design (Mica, Acrylic backdrops) → better UX.
- Native Windows 11 integration (fluent design).
- Better performance (GPU-accelerated graphics).
- Active development by Microsoft (vs. WPF which is stable but legacy).

**Alternatives:**
- WPF (more mature, ecosystem larger, but older look).
- MAUI (.NET Multi-platform, nhưng overkill cho desktop-only).
- Electron/Vue (cross-platform, but heavier, not native feel).

**Consequences:**
- +: Modern look, better performance, Windows 11 native feel.
- -: Younger ecosystem (less StackOverflow answers), may have bugs vs. WPF stability.

---

## 6. Lời khuyên thực tế

### Khi thiết kế hệ thống:
1. **Bắt đầu với System Architecture** (dù đơn giản):
   - Vẽ Context Diagram (C4 Level 1): "Cái gì là hệ thống? Cái gì ngoài hệ thống?"
   - Vẽ Container Diagram (C4 Level 2): "Hệ thống gồm những containers / services nào?"
   - Ví dụ DailyClip: Chỉ cần 1 container (app), nên diagram rất đơn giản.

2. **Sau đó đi sâu vào Software Architecture:**
   - Chọn pattern (Clean, Onion, Hexagonal, Vertical Slice).
   - Vẽ Component Diagram: modules chính, cách tương tác.
   - Viết ADRs cho quyết định lớn.

3. **Tránh over-engineering:**
   - Với DailyClip: Clean Arch + MVVM là đủ mạnh.
   - Không cần DDD (Domain-Driven Design) full nếu domain không phức tạp.
   - Không cần Microservices, MQ, CQRS… (cảnh báo anti-pattern: "Microservices for MVP").

### Khi implement:
- Follow Clean Architecture từ đầu (dễ refactor sau hơn add structure lúc sau).
- Test driver development (TDD) cho domain layer → code quality cao hơn.
- Use DI container từ đầu (Microsoft.Extensions.DependencyInjection) → dễ test, mock.
- Tuân thủ ADRs → maintain decision log → khi refactor biết "tại sao" quyết định xưa.

---

## 7. Tham chiếu & Liên kết

- **SRS.md**: Yêu cầu chức năng & phi chức năng (What).
- **SDD.md**: Kiến trúc cấp cao (How - High-level).
- **DSDD.md**: Thiết kế chi tiết (How - Low-level).
- **C4 Model**: https://c4model.com/ (context, container, component, code).
- **Clean Architecture**: Robert C. Martin "Clean Architecture: A Craftsman's Guide to Software Structure and Design".
- **IEEE 1471-2000 / ISO/IEC/IEEE 42010**: Standards cho Software & System Architecture.

---

## 8. Kết luận

- **Kiến trúc Hệ thống** (System Architecture) = tầm nhìn toàn cảnh hệ thống (phần mềm + hardware + external).
- **Kiến trúc Phần mềm** (Software Architecture) = tổ chức nội bộ của phần mềm (layers, components, patterns).
- Cho **DailyClip**: System Architecture rất đơn giản (desktop app + local storage), Software Architecture đùa dùng **Clean Arch + MVVM** để dễ test, bảo trì, mở rộng.
- **ADRs** giúp document quyết định design → team hiểu "tại sao" → quyết định sau lần refactor.

Chúc bạn thiết kế DailyClip thành công! 🚀
