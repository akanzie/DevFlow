# Implementation Notes – STEP 1–3

**Date:** 06/03/2026  
**Author:** Team DailyClip

---

## Design Decisions Made

### 1. Domain Entities: Records vs Classes
**Decision:** Use **immutable `record` types** for `ClipItem`, `SearchResult`, `DailyNote`

**Rationale:**
- ✅ Immutable → thread-safe, easier to reason about
- ✅ Fluent structural equality → good for testing snapshots
- ✅ Concise syntax (C# 12+)
- ✅ Most appropriate for domain entities that rarely change after creation

**Alternative Rejected:** `class` with properties
- More verbose, requires manual equality override
- Mutable by default (opens for bugs)

---

### 2. Validation Strategy: Constructor Validation
**Decision:** Throw exceptions **inside record primary constructors** (via init-only property)

```csharp
public record ClipItem(...) 
{
    public ClipItem // Property validator
    {
        if (Timestamp == default) throw new ArgumentException(...);
    }
}
```

**Rationale:**
- ✅ Fail-fast: prevents invalid objects from ever existing
- ✅ Clear semantics: constructor contract
- ✅ Consistent with Domain-Driven Design

**Alternative Rejected:** Factory methods
- More boilerplate, less discoverable

---

### 3. Duplicate Detection Logic: Where to Implement?
**Decision:** Place in **ClipItem domain entity** (`IsDuplicate` method)

```csharp
public bool IsDuplicate(ClipItem other) { ... }
```

**Rationale:**
- ✅ Business rule lives in domain (not scattered across services)
- ✅ Testable independently (unit test just the entity)
- ✅ Easier to reuse in application layer

**Alternative Rejected:** Put in ClipboardMonitorService
- Service becomes focused on IO + logic mixing (violates SRP)

---

### 4. Configuration: Static Class vs. IOptions
**Decision:** Use **static `AppConfig` class** for MVP, plan migration to `IOptions<T>` later

**Rationale:**
- ✅ No DI overhead for constants
- ✅ Easy access from anywhere (`AppConfig.Timing.DuplicateCacheWindowSeconds`)
- ✅ Fast: resolved at compile time for constants

**Migration Path for v1.1:**
```csharp
// Later: Replace with IOptions<AppSettings> from config.json
services.Configure<AppSettings>(configuration.GetSection("DailyClip"));
```

**Alternative:** IOptions from the start
- Adds complexity too early; static is fine for MVP

---

### 5. Interfaces: Core Layer (not Infrastructure)
**Decision:** Place **all service interfaces** in `DailyClip.Core.Interfaces`

**Rationale:**
- ✅ Clean Architecture: core layer depends on abstractions, not implementations
- ✅ DailyClip.Infrastructure implements these contracts
- ✅ DailyClip.Tests mocks these interfaces
- ✅ Dependency direction: Infrastructure → Core (onion principle)

**Structure:**
```
Core (independ ent)
├── Entities (pure domain)
├── Interfaces (contracts only)
└── Config

Infrastructure (depends on Core)
├── Services (implements Core.Interfaces)
└── DuckDB/IO implementations

Tests (depends on Core)
├── Mocks of Core.Interfaces
└── DailyClip.Tests
```

---

### 6. Nullable Reference Types: Enabled Globally
**Decision:** `<Nullable>enable</Nullable>` in all .csproj files

**Rationale:**
- ✅ Prevents NullReferenceException bugs
- ✅ Compiler warnings guide safe coding
- ✅ Project-wide consistency (no opt-in per file)

**Consequence:**
- Every parameter/return that can be null must be annotated with `?`
- Example: `string? SourceUrl` means can be null, `string Content` means never null

---

### 7. Async-First Design
**Decision:** All I/O and long-running operations are **async methods**

```csharp
Task CreateDailyFolderIfNotExistsAsync();
Task AppendClipAsync(ClipItem clip);
Task<byte[]> CaptureRegionAsync(Rectangle bounds);
```

**Rationale:**
- ✅ No thread blocking (critical for UI responsiveness)
- ✅ Scalable: can handle many concurrent operations
- ✅ Pattern: `Async` suffix signals async (CodingRules compliant)

**Consequence:**
- Implementations must use `async/await`, not `Task.Run` hacks
- Tests must use `async Task` and `await`

---

### 8. Hotkey Service: ModifierKeys Enum
**Decision:** Define **custom `ModifierKeys` enum** in `IHotkeyService.cs`

```csharp
[Flags]
public enum ModifierKeys
{
    None = 0,
    Alt = 1,
    Control = 2,
    Shift = 4,
    Win = 8,
}
```

**Rationale:**
- ✅ Type-safe: prevents invalid combinations
- ✅ Flags attribute: bitwise operations for multiple modifiers
- ✅ Clear semantics vs Windows `Keys` enum (which is for virtual keys)

**Usage:**
```csharp
hotkeyService.RegisterHotkey(1, ModifierKeys.Alt | ModifierKeys.Shift, VirtualKey.S);
```

---

## Code Quality Decisions

### CodingRules Applied
- ✅ **Naming**: PascalCase for classes/methods (e.g., `ClipItem`, `AppendClipAsync`)
- ✅ **Naming**: _camelCase for private fields (will apply in infrastructure implementations)
- ✅ **XML Docs**: All public members documented (`/// <summary>`)
- ✅ **Formatting**: 4-space indentation via .editorconfig
- ✅ **Braces**: Always use `{}` (checked by editorconfig)
- ✅ **Modern C#**: Using C# 12+ features (records, implicit usings, etc.)

### Documentation Strategy
- Each public class/method has `<summary>` explaining **why** and **what**
- Parameters documented with `<param>`
- Exceptions documented with `<exception>`
- Example in README shows how to navigate the structure

---

## Package Decisions

### DailyClip.Core.csproj
```xml
<PackageReference Include="System.Text.Json" />  <!-- For JSONL serialization -->
<PackageReference Include="Microsoft.Extensions.DependencyInjection.Abstractions" />
```

### DailyClip.Infrastructure.csproj
```xml
<PackageReference Include="DuckDB.NET.Data" />
<PackageReference Include="SixLabors.ImageSharp" />  <!-- PNG encoding -->
<PackageReference Include="Serilog" />              <!-- Structured logging -->
```

### DailyClip.Tests.csproj
```xml
<PackageReference Include="xunit" />
<PackageReference Include="Moq" />
<PackageReference Include="FluentAssertions" />
<PackageReference Include="coverlet.collector" />  <!-- Code coverage -->
```

### DailyClip (Main App).csproj
```xml
<PackageReference Include="CommunityToolkit.Mvvm" />  <!-- MVVM helpers -->
<PackageReference Include="Microsoft.WindowsAppSDK" />  <!-- WinUI 3 -->
```

---

## File Organization Rationale

```
DailyClip.Core/
├── Config/
│   └── AppConfig.cs         (Static constants, no dependencies)
├── Entities/
│   ├── ClipItem.cs          (Domain entity, pure business logic)
│   ├── SearchResult.cs
│   └── DailyNote.cs
├── Interfaces/
│   ├── IStorageService.cs   (Service contracts, no implementation)
│   ├── ISearchService.cs
│   ├── IClipboardMonitor.cs
│   ├── IHotkeyService.cs
│   └── IScreenCaptureService.cs
```

**Rationale:**
- **Config/** first → used by everything
- **Entities/** → domain objects
- **Interfaces/** → service contracts (implementations go to Infrastructure)

---

## Next Steps & Migration Points

### STEP 4: FileStorageService Implementation
- **Goal:** Implement `IStorageService` in Infrastructure
- **Key method:** `AppendClipAsync()` → write JSONL line to file
- **Challenge:** Ensure thread-safety for concurrent appends
- **Test:** Unit test with temp folder

### Future: From AppConfig to config.json
```json
{
  "hotkeyCapture": "Alt+S",
  "hotkeyNote": "Alt+N",
  "hotkeySearch": "Alt+Apostrophe",
  "retentionDays": 30
}
```

Migrate from static constants to `IOptions<AppSettings>` in:
- App.xaml.cs (setup)
- Services (inject via constructor)

---

## Known Limitations (By Design)

1. **No encryption** (v1.0): Data stored plaintext locally
   - Mitigation: User has full OS-level file permissions
   - v2.0: Add optional AES encryption per-clip

2. **Static AppConfig** (current): No runtime changes
   - Mitigation: Restart app to pick up new config
   - v1.1: Migrate to IOptions for hot reload

3. **Single-user only** (v1.0): No multi-user support
   - Rationale: Desktop app on personal machine
   - v2.0: Multi-device sync when cloud integration comes

---

## Testing Strategy (Detailed in UnitTesting.md)

- **Domain Entities**: Pure unit tests (no mock, no async)
  - Test: `IsDuplicate()` logic, validation throwing
  
- **Services (Infrastructure)**: Unit + integration tests
  - Mock: File I/O (using temp folder)
  - Integration: In-memory DuckDB for SearchService
  
- **ViewModel**: Unit tests with mock services
  - Mock: ISearchService, IStorageService
  - Test: Binding, command execution

- **UI (WinUI Views)**: Manual testing only
  - Reason: WinUI binding hard to unit test
  - Focus: ViewModel logic well-tested

---

## Build & Deployment Decisions (STEP 1–3)

### Framework Deferral: WinUI3 → STEP 12+
**Decision:** Use `Microsoft.NET.Sdk` (console app) instead of WindowsDesktop + WinUI3 SDK

**Why This Decision:**
- WindowsAppSDK 1.5.240227000 requires PRI (Package Resource Index) compilation
- PRI tasks depend on `Microsoft.Build.Packaging.Pri.Tasks.dll` (not in standard .NET 9 SDK)
- System cannot locate: `C:\Program Files\dotnet\sdk\9.0.311\Microsoft\VisualStudio\v17.0\AppxPackage\Microsoft.Build.Packaging.Pri.Tasks.dll`
- **Better approach:** Stabilize core services (clipboard, storage, search) first without UI framework baggage

**Implementation Timeline:**
- **STEP 1–11:** Headless/CLI validation of all core functionality
- **STEP 12–15:** Migrate to separate `DailyClip.UI` project with WinUI3
- **STEP 16+:** Advanced UI features (tray, drag/drop, notifications)

**What This Means:**
- ✅ Core services can be tested independently
- ✅ Infrastructure layer fully stable before UI complexity
- ✅ Reduces cryptic build errors that block development
- ✅ MVP can launch as CLI tool, UI is v1.1 feature

### Entity Validation: Factory Pattern (Not Property Initializers)
**Issue Found:** Initial code attempted to use property initializers for validation:
```csharp
// INVALID - Doesn't compile in C#
public record ClipItem { 
    validation ...  
}
```

**Resolution:** Changed to static `Create()` factory method
```csharp
// CORRECT - Idiomatic C# for record validation
public sealed record ClipItem(...) {
    public static ClipItem Create(DateTimeOffset timestamp, string type, string content, ...) {
        ArgumentException.ThrowIfNullOrWhiteSpace(content);
        return new ClipItem(timestamp, type, content, ...);
    }
}
```

**Why:** C# records cannot use property validators. Factory methods are the idiomatic pattern for immutable validation.

### System.Drawing.Rectangle Import
**Issue:** `IScreenCaptureService.cs` referenced `Rectangle` type without import
```csharp
Task<byte[]> CaptureRegionAsync(Rectangle bounds);  // Rectangle not found!
```

**Resolution:** Added `using System.Drawing;`

**Future Migration:** Plan to migrate to SharpDX or SkiaSharp for cleaner graphics API in v1.2+

---

## Checklist for STEP 1–3 Completion

- ✅ Solution builds without errors
- ✅ All .csproj files have correct target frameworks
- ✅ NuGet packages restore successfully
- ✅ Domain entities immutable and validated
- ✅ All interfaces well-documented with XML
- ✅ .editorconfig applied consistently
- ✅ Naming follows CodingRules
- ✅ No circular dependencies
- ✅ README documents what's done
- ✅ Ready for STEP 4: FileStorageService

---

## Questions for Future PRs

When implementing services, ask:
1. **Does this class have a single responsibility?**
2. **Are all I/O operations async?**
3. **Is error handling specific (not catch-all)?**
4. **Are domain rules in Core, not Infrastructure?**
5. **Do I need 3+ unit tests for this logic?**

---

**Status:** Foundation Ready 🎯  
**Next Milestone:** FileStorageService + unit tests (STEP 4–6)
