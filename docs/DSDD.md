# Tài liệu Thiết kế Chi tiết (Detailed Software Design Document) - Python  
**Tên phần mềm:** DailyClip – Công cụ tự động hóa ghi chú và lưu trữ dữ liệu cá nhân  
**Phiên bản:** 1.0 (Python Detailed Design)  
**Ngày soạn thảo:** 06/03/2026  

## 1. Giới thiệu

### 1.1 Mục đích
Tài liệu này mô tả thiết kế chi tiết (low-level design) của DailyClip (Python), bao gồm:  
- Cấu trúc package và module chính.  
- Interfaces (Protocols) và mối quan hệ giữa các class.  
- Thuật toán cốt lõi (clipboard monitor, indexing, search).  
- Thiết kế dữ liệu chi tiết và schema DuckDB.  
- Sequence & class diagram (mô tả text).  

Tài liệu phục vụ lập trình viên implement code, tester viết unit test, và maintainer hiểu cấu trúc nội bộ.

### 1.2 Phạm vi
- Chi tiết cho MVP: clipboard monitor, capture, quick note, global search, storage theo ngày.  
- Không bao gồm: settings UI chi tiết, cleanup scheduler, export module.

### 1.3 Tài liệu tham chiếu
- SRS
- SDD

## 2. Cấu trúc Package & Layered Architecture

```
dailyclip/
├── __init__.py
├── main.py                          # Entry point
├── config.py                        # Configuration, constants
│
├── core/                            # Domain Layer
│   ├── __init__.py
│   ├── entities.py                  # ClipItem, Note, Screenshot (dataclasses)
│   ├── protocols.py                 # IStorageService, ISearchService (Protocols)
│   └── values.py                    # Value objects if any
│
├── application/                     # Application Layer
│   ├── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── clipboard.py             # ClipboardMonitor service
│   │   ├── search.py                # SearchService interface
│   │   ├── storage.py               # StorageService interface
│   │   ├── hotkey.py                # HotkeyManager interface
│   │   └── capture.py               # ScreenCaptureService interface
│   └── use_cases/                   # Optional, if needed
│       ├── __init__.py
│       ├── search_use_case.py
│       └── capture_use_case.py
│
├── infrastructure/                  # Infrastructure Layer
│   ├── __init__.py
│   ├── clipboard_monitor.py         # ClipboardMonitorImpl (pyperclip based)
│   ├── duckdb_search.py             # DuckDBSearchServiceImpl
│   ├── file_storage.py              # FileStorageServiceImpl
│   ├── windows_hotkey.py            # WindowsHotkeyServiceImpl (keyboard/pynput)
│   └── screenshot_capture.py        # ScreenCaptureServiceImpl (pyautogui/mss)
│
├── presentation/                    # Presentation Layer (PyQt6)
│   ├── __init__.py
│   ├── app.py                       # QApplication main
│   ├── windows/
│   │   ├── __init__.py
│   │   ├── quick_search.py          # QuickSearchWindow (QMainWindow)
│   │   ├── quick_note.py            # QuickNoteWindow (QMainWindow)
│   │   └── gallery.py               # GalleryWindow
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── search_result_item.py    # Custom QListWidget item
│   │   └── gallery_item.py          # Custom gallery item
│   └── tray.py                      # SystemTrayIcon
│
├── common/                          # Shared utilities
│   ├── __init__.py
│   ├── logger.py                    # Logging configuration
│   ├── di_container.py              # Dependency injection setup
│   └── utils.py                     # Helper functions
│
└── tests/                           # Unit tests
    ├── __init__.py
    ├── test_clipboard.py
    ├── test_search.py
    ├── test_storage.py
    └── test_hotkey.py
```

## 3. Domain Layer - Entities (core/entities.py)

```python
from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum
from typing import Optional
from pathlib import Path

class ClipType(Enum):
    TEXT = "text"
    IMAGE = "image"
    HTML = "html"

@dataclass(frozen=True)
class ClipItem:
    """Đại diện một item clipboard"""
    timestamp: datetime
    clip_type: ClipType
    content: str
    format: str = "plain"  # plain, markdown, code
    source_url: Optional[str] = None

@dataclass(frozen=True)
class Screenshot:
    """Metadata của ảnh chụp màn hình"""
    timestamp: datetime
    file_path: Path
    width: int
    height: int

@dataclass(frozen=True)
class DailyNote:
    """Ghi chú Markdown ngày"""
    date_str: str  # YYYY-MM-DD
    content: str

@dataclass(frozen=True)
class SearchResult:
    """Kết quả tìm kiếm"""
    timestamp: datetime
    snippet: str
    file_path: Path
    item_type: str  # "clip", "note", "screenshot"
    relevance_score: float
```

## 4. Application Layer - Protocols (core/protocols.py)

```python
from typing import Protocol, List
from pathlib import Path
from .entities import ClipItem, Screenshot, DailyNote, SearchResult

class IStorageService(Protocol):
    """Interface lưu trữ"""
    def create_daily_folder(self, date_str: str) -> Path: ...
    async def append_clip(self, clip: ClipItem) -> None: ...
    async def save_screenshot(self, image_bytes: bytes, timestamp: datetime) -> Path: ...
    async def append_note(self, note: DailyNote) -> None: ...

class ISearchService(Protocol):
    """Interface tìm kiếm"""
    async def index_daily_data(self, date_str: str) -> None: ...
    async def search(self, query: str, limit: int = 50) -> List[SearchResult]: ...

class IClipboardMonitor(Protocol):
    """Interface giám sát clipboard"""
    async def start_monitoring(self) -> None: ...
    async def stop_monitoring(self) -> None: ...

class IHotkeyService(Protocol):
    """Interface hotkey"""
    def register_hotkey(self, combo: str, callback: Callable) -> None: ...
    def unregister_all(self) -> None: ...

class IScreenCaptureService(Protocol):
    """Interface chụp màn hình"""
    def capture_region(self, x: int, y: int, w: int, h: int) -> bytes: ...
    def capture_fullscreen(self) -> bytes: ...
    def capture_active_window(self) -> bytes: ...
```

## 5. Infrastructure Layer - Key Implementations

### 5.1 ClipboardMonitor (infrastructure/clipboard_monitor.py)

```python
import asyncio
import pyperclip
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Callable, Optional
from pathlib import Path
from core.entities import ClipItem, ClipType
from core.protocols import IStorageService, ISearchService

class ClipboardMonitorService:
    def __init__(self, storage: IStorageService, search: ISearchService):
        self._storage = storage
        self._search = search
        self._last_hash: Optional[str] = None
        self._last_hash_time: Optional[datetime] = None
        self._monitoring = False
        self._logger = logging.getLogger(__name__)

    async def start_monitoring(self):
        """Bắt đầu giám sát clipboard"""
        self._monitoring = True
        self._logger.info("Clipboard monitor started")
        
        while self._monitoring:
            try:
                content = pyperclip.paste()
                await self._process_clipboard(content)
            except Exception as e:
                self._logger.error(f"Clipboard error: {e}")
            
            await asyncio.sleep(0.5)  # Poll every 500ms

    async def stop_monitoring(self):
        """Dừng giám sát clipboard"""
        self._monitoring = False
        self._logger.info("Clipboard monitor stopped")

    async def _process_clipboard(self, content: str):
        """Xử lý clipboard content"""
        if not content:
            return
        
        # Deduplicate check
        if self._is_duplicate(content):
            return
        
        # Create ClipItem
        clip = ClipItem(
            timestamp=datetime.now(),
            clip_type=ClipType.TEXT,
            content=content,
            source_url=self._extract_url(content)
        )
        
        # Save and index
        await self._storage.append_clip(clip)
        await self._search.index_daily_data(datetime.now().strftime("%Y-%m-%d"))

    def _is_duplicate(self, content: str) -> bool:
        """Check nếu content trùng lặp trong 10s"""
        current_hash = hashlib.sha256(content.encode()).hexdigest()
        now = datetime.now()
        
        if self._last_hash == current_hash:
            if self._last_hash_time and (now - self._last_hash_time) < timedelta(seconds=10):
                return True
        
        self._last_hash = current_hash
        self._last_hash_time = now
        return False

    def _extract_url(self, content: str) -> Optional[str]:
        """Extract URL từ content nếu có"""
        import re
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
        return urls[0] if urls else None
```

### 5.2 DuckDBSearchService (infrastructure/duckdb_search.py)

```python
import duckdb
import logging
from pathlib import Path
from typing import List
from datetime import datetime
from core.protocols import ISearchService
from core.entities import SearchResult, ClipType
import json

class DuckDBSearchService(ISearchService):
    def __init__(self, db_path: Path):
        self._db_path = db_path
        self._logger = logging.getLogger(__name__)
        self._init_db()

    def _init_db(self):
        """Initialize DuckDB database"""
        conn = duckdb.connect(str(self._db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clips_index (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                timestamp TIMESTAMP,
                file_path VARCHAR,
                content_type VARCHAR,
                content TEXT,
                full_text TEXT
            )
        """)
        
        # Create FTS index
        conn.execute("""
            CREATE OR REPLACE INDEX IF NOT EXISTS idx_fts 
            ON clips_index (full_text)
        """)
        conn.close()

    async def index_daily_data(self, date_str: str) -> None:
        """Index dữ liệu ngày"""
        clips_dir = Path(f"%APPDATA%/DailyClip/data/{date_str}/clippings")
        
        if not clips_dir.exists():
            return
        
        conn = duckdb.connect(str(self._db_path))
        
        for jsonl_file in clips_dir.glob("*.jsonl"):
            with open(jsonl_file) as f:
                for line in f:
                    try:
                        record = json.loads(line)
                        conn.execute("""
                            INSERT OR IGNORE INTO clips_index 
                            (timestamp, file_path, content_type, content, full_text)
                            VALUES (?, ?, ?, ?, ?)
                        """, [
                            record.get("timestamp"),
                            str(jsonl_file),
                            record.get("type", "text"),
                            record.get("content"),
                            record.get("content")  # Full-text indexed
                        ])
                    except Exception as e:
                        self._logger.error(f"Index error: {e}")
        
        conn.close()

    async def search(self, query: str, limit: int = 50) -> List[SearchResult]:
        """Full-text search"""
        conn = duckdb.connect(str(self._db_path))
        
        sql = f"""
            SELECT id, timestamp, file_path, content_type, 
                   SUBSTR(content, 1, 100) as snippet
            FROM clips_index
            WHERE full_text LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """
        
        try:
            results = conn.execute(sql, [f"%{query}%", limit]).fetchall()
            return [
                SearchResult(
                    timestamp=r[1],
                    snippet=r[4],
                    file_path=Path(r[2]),
                    item_type=r[3],
                    relevance_score=1.0
                )
                for r in results
            ]
        finally:
            conn.close()
```

## 6. Presentation Layer - PyQt6 Examples

### 6.1 QuickSearchWindow (presentation/windows/quick_search.py)

```python
import sys
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QLineEdit, QListWidget, QWidget
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from core.protocols import ISearchService

class QuickSearchWindow(QMainWindow):
    def __init__(self, search_service: ISearchService):
        super().__init__()
        self._search_service = search_service
        self._init_ui()
        self._search_timer = QTimer()
        self._search_timer.timeout.connect(self._do_search)

    def _init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("DailyClip Search")
        self.setGeometry(100, 100, 600, 400)
        
        # Main widget
        main_widget = QWidget()
        layout = QVBoxLayout()
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search clips, notes...")
        self.search_box.textChanged.connect(self._on_search_text_changed)
        layout.addWidget(self.search_box)
        
        # Results list
        self.results_list = QListWidget()
        layout.addWidget(self.results_list)
        
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def _on_search_text_changed(self, text: str):
        """Debounce search input"""
        self._search_timer.stop()
        if text:
            self._search_timer.start(300)  # 300ms debounce

    async def _do_search(self):
        """Execute search"""
        query = self.search_box.text()
        results = await self._search_service.search(query)
        
        self.results_list.clear()
        for result in results:
            self.results_list.addItem(f"{result.timestamp}: {result.snippet}")
```

## 7. Dependency Injection Setup (common/di_container.py)

```python
from dependency_injector import containers, providers
from pathlib import Path
from infrastructure.clipboard_monitor import ClipboardMonitorService
from infrastructure.duckdb_search import DuckDBSearchService
from infrastructure.file_storage import FileStorageService
from infrastructure.windows_hotkey import WindowsHotkeyService

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    # Infrastructure services
    storage_service = providers.Singleton(
        FileStorageService,
        root_path=Path("%APPDATA%/DailyClip/data")
    )
    
    search_service = providers.Singleton(
        DuckDBSearchService,
        db_path=Path("%APPDATA%/DailyClip/data/search.duckdb")
    )
    
    clipboard_monitor = providers.Singleton(
        ClipboardMonitorService,
        storage=storage_service,
        search=search_service
    )
    
    hotkey_service = providers.Singleton(
        WindowsHotkeyService
    )
```

## 8. Thuật toán Chính (Key Algorithms)

### 8.1 Clipboard Processing Flow (Pseudo-code)
```python
async def on_clipboard_change():
    content = pyperclip.paste()
    
    # Check duplicate
    if is_duplicate(content, last_10_seconds):
        return
    
    # Create object
    clip = ClipItem(
        timestamp=now(),
        type="text",
        content=content
    )
    
    # Extract metadata
    clip.source_url = extract_url(content)
    
    # Persist
    await storage.append_clip(clip)
    
    # Index
    await search.index_clip(clip)
```

### 8.2 Full-Text Search Query (SQL)
```sql
SELECT timestamp, file_path, snippet(content, 100) AS preview
FROM clips_index
WHERE full_text LIKE ?
ORDER BY timestamp DESC
LIMIT 50;
```

## 9. Sequence Diagrams (Text)

### 9.1 Copy text → Lưu & Index
```
User -> System : Ctrl+C
ClipboardMonitor -> Storage : append_clip(ClipItem)
Storage -> FileSystem : Append JSONL
ClipboardMonitor -> SearchService : index_daily_data()
SearchService -> DuckDB : INSERT INTO clips_index
```

### 9.2 Quick Search
```
User -> System : Alt+Space
HotkeyService -> QuickSearchWindow : show()
User -> SearchBox : Type query
SearchBox -> SearchService : search(query)
SearchService -> DuckDB : Execute FTS query
SearchService -> Window : Display results
```

## 10. Error Handling & Logging

```python
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path.home() / "AppData/Local/DailyClip/app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Usage
try:
    await storage.append_clip(clip)
except IOError as e:
    logger.error(f"Storage error: {e}", exc_info=True)
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
```

## 11. Unit Testing Strategy

- **pytest** + **pytest-asyncio** for async tests
- **pytest-mock** cho mocking
- **unittest.mock** for Protocol mocking

Example:
```python
@pytest.mark.asyncio
async def test_clipboard_duplicate():
    storage_mock = Mock(spec=IStorageService)
    search_mock = Mock(spec=ISearchService)
    
    monitor = ClipboardMonitorService(storage_mock, search_mock)
    
    # First call should save
    await monitor._process_clipboard("test")
    storage_mock.append_clip.assert_called_once()
    
    # Duplicate within 10s should not save
    await monitor._process_clipboard("test")
    storage_mock.append_clip.assert_called_once()  # Still once
```

## 12. Performance Considerations

- **Clipboard polling**: 500ms interval (acceptable trade-off).
- **Search indexing**: Incremental via append, daily rebuild if >1000 new items.
- **Memory**: ClipboardMonitor keep last 10s hashes in memory (~minimal).
- **Threading**: Clipboard monitor runs in background thread, GUI on main QThread.

---

Tài liệu chi tiết này cung cấp blueprint implement DailyClip Python version.
