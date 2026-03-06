# Tài liệu Quy tắc Code (Coding Rules & Style Guidelines) - Python  
**Dự án:** DailyClip (Python version)  
**Phiên bản:** 1.0  
**Áp dụng cho:** Toàn bộ codebase Python (PyQt6 + Core logic)  
**Mục tiêu:** Code sạch, nhất quán, dễ đọc, dễ test, dễ mở rộng. Tuân thủ **PEP 8** và nguyên tắc **Clean Code**.

---

## 1. Nguyên tắc General (General Principles)

- **Clean Code & SOLID** → Áp dụng nghiêm ngặt (Single Responsibility, Open-Closed, Dependency Inversion…).
- **Type Hints** → Luôn dùng type hints (Python 3.10+ support từ `from __future__ import annotations`).
- **Async First** → Sử dụng `async`/`await` cho I/O operations (file, clipboard, DB).
- **Error Handling** → Không catch generic `Exception`. Catch specific exceptions + logging.
- **Dataclasses & Protocols** → Sử dụng `dataclasses` cho entities, `Protocol` cho interfaces.
- **Dependency Injection** → Dùng `dependency-injector` package.
- **Logging** → Sử dụng `logging` module, không `print()`.
- **PEP 8 Compliance** → Tuân thủ PEP 8 hoàn toàn, dùng tools như `black`, `flake8`, `isort`.

---

## 2. Naming Conventions (PEP 8 Official)

| Loại                  | Quy tắc                  | Ví dụ                              | Lưu ý |
|-----------------------|--------------------------|------------------------------------|-------|
| Module / File         | **snake_case**           | `clipboard_monitor.py`, `search_service.py` | Toàn bộ chữ cái thường, dấu gạch dưới |
| Class / Exception     | **PascalCase**           | `ClipboardMonitorService`, `ClipboardError` | Bắt đầu hoa, không dấu gạch |
| Function / Method     | **snake_case**           | `append_clip()`, `is_duplicate()` | Toàn bộ chữ cái thường, dấu gạch dưới |
| Constant              | **UPPER_CASE**           | `MAX_CACHE_SIZE`, `DEFAULT_TIMEOUT_SECONDS` | Toàn bộ chữ hoa, dấu gạch dưới |
| Variable (local)      | **snake_case**           | `clip_item`, `search_results` | Toàn bộ chữ cái thường, dấu gạch dưới |
| Private Method/Field  | **_snake_case** (leading underscore) | `_process_clipboard()`, `_last_hash` | Một dấu gạch dưới đầu |
| Magic Method          | **__method__** (dunder)  | `__init__()`, `__str__()` | Hai dấu gạch dưới đầu và cuối |
| Interface (Protocol)  | **I + PascalCase**       | `IStorageService`, `ISearchService` | Theo convention, dùng Protocols |
| Dict Keys             | **snake_case**           | `config["max_items"]` | Nhất quán, tránh CamelCase |

**Quy tắc bổ sung:**
- Tên phải **rõ ràng, tự biểu đạt**, tránh viết tắt trừ khi phổ biến (e.g., `url`, `db`, `config`).
- Sử dụng suffix/prefix khi cần: `...Service`, `...Repository`, `...Manager`, `...Error`.
- Không dùng Hungarian notation (`strName`, `iCount` – lỗi thời).
- Enum member: **UPPER_CASE** (e.g., `ClipType.TEXT`, `ClipType.IMAGE`).

---

## 3. File Structure & Organization

### 3.1 File Header
```python
"""
Module description: Giải thích module làm gì.

Example:
    Cách sử dụng module:
    
    >>> from my_module import MyClass
    >>> obj = MyClass()
    >>> obj.do_something()
"""

import logging
from typing import Protocol, List
from pathlib import Path

logger = logging.getLogger(__name__)
```

### 3.2 Import Organization (PEP 8 & isort)
```python
# 1. Standard Library (sorted alphabetically)
import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Protocol

# 2. Third-party libraries (sorted alphabetically)
import pyperclip
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QMainWindow, QLineEdit
from dependency_injector import containers, providers

# 3. Local/application imports (sorted alphabetically)
from core.entities import ClipItem, ClipType
from core.protocols import IStorageService
from common.logger import get_logger

# Avoid: from module import *
```

Tools: Sử dụng `isort` để auto-format imports.
```bash
isort .  # Sort all imports in current directory
```

### 3.3 File Layout (Recommend order)
```python
"""Module docstring."""

# Imports
import logging
from typing import Protocol

# Constants
DEFAULT_TIMEOUT_SECONDS = 30
MAX_CLIPBOARD_SIZE = 1_000_000

# Logging
logger = logging.getLogger(__name__)

# Protocols / Interfaces
class IStorageService(Protocol):
    """Interface for storage."""
    def save(self) -> None: ...

# Dataclasses / Value Objects
from dataclasses import dataclass

@dataclass(frozen=True)
class ClipItem:
    """Immutable clip item."""
    timestamp: datetime
    content: str

# Main Classes
class ClipboardMonitorService:
    """Main service implementation."""
    
    def __init__(self, storage: IStorageService):
        self._storage = storage
    
    def start(self) -> None:
        """Start monitoring."""
        pass

# Helper functions
def extract_url(content: str) -> Optional[str]:
    """Extract URL from content."""
    pass

# If __name__ == "__main__"
if __name__ == "__main__":
    pass
```

---

## 4. Formatting & Layout

### 4.1 General Formatting
- **Indentation**: 4 spaces (PEP 8 standard).
- **Line length**: 88 characters (Black default, reasonable trade-off).
- **Encoding**: UTF-8 (default for Python 3).
- **Line endings**: LF (`\n` – Unix style, recommended for cross-platform).

### 4.2 Blank Lines
- 2 blank lines between top-level definitions (classes, functions).
- 1 blank line between method definitions inside a class.
- 1 blank line between logical sections inside a function (optional, use for clarity).
- No trailing whitespace.

```python
class MyClass:
    """First class."""
    
    def __init__(self):
        pass
    
    def method_one(self):
        return 1
    
    def method_two(self):
        return 2


class AnotherClass:
    """Second class."""
    pass


def top_level_function():
    """Top-level function."""
    pass
```

### 4.3 Spacing Rules
```python
# ✓ Around operators
a = b + c
x == y
if condition:

# ✗ Not around operators inside brackets
my_list[1:5]  # No spaces
function_call(arg1, arg2)  # No space before (

# ✗ Not after keyword
if condition:  # Not if  (condition)
for x in items:  # Not for  x  in  items

# ✓ After comma
items = [1, 2, 3]
function(arg1, arg2, arg3)

# ✓ Dictionary
config = {"key": "value", "another": "value"}
```

### 4.4 String Quotes
```python
# Prefer single quotes (Python convention)
name = 'John'
message = "It's a message"  # Use double when contains single quote

# f-strings for formatting
value = 42
message = f"Value is {value}"  # Better than .format() or %s

# Triple quotes for docstrings
def my_function():
    """
    Multi-line docstring.
    
    Args:
        arg1: Description.
    
    Returns:
        Description of return.
    """
    pass
```

---

## 5. Type Hints & Documentation

### 5.1 Type Hints (Required)
```python
from typing import Optional, List, Dict, Callable, Union
from pathlib import Path
import asyncio

# ✓ Always use type hints
def process_clip(content: str, max_length: int = 1024) -> bool:
    """Process a clipboard clip."""
    return len(content) <= max_length

# ✓ With async
async def fetch_data(url: str) -> Dict[str, any]:
    """Fetch data from URL."""
    pass

# ✓ With Optional and List
def find_items(items: List[str], query: Optional[str] = None) -> List[str]:
    """Find items matching query."""
    if query is None:
        return items
    return [item for item in items if query in item]

# ✓ Union types (or use `|` in Python 3.10+)
def handle_data(data: Union[str, int, float]) -> None:
    pass

# Python 3.10+ alternative
def handle_data_modern(data: str | int | float) -> None:
    pass
```

### 5.2 Docstrings (Google Style)
```python
def search_clips(query: str, limit: int = 50) -> List[Dict]:
    """
    Search clips using full-text search.
    
    Args:
        query: Search query string.
        limit: Maximum number of results to return. Defaults to 50.
    
    Returns:
        List of matching clip dictionaries, each containing:
        - timestamp: ISO datetime string
        - snippet: Preview of content
        - file_path: Path to clip file
    
    Raises:
        ValueError: If query is empty.
        IOError: If database connection fails.
    
    Example:
        >>> results = search_clips("python async", limit=10)
        >>> len(results)
        5
    
    Note:
        Results are sorted by timestamp descending.
    """
    if not query:
        raise ValueError("Query cannot be empty")
    
    # Implementation...
    pass
```

---

## 6. Language Specific Best Practices

### 6.1 Classes & Dataclasses
```python
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

# ✓ Use dataclass for immutable entities (Domain layer)
@dataclass(frozen=True)
class ClipItem:
    """Immutable clip item."""
    timestamp: datetime
    content: str
    source_url: Optional[str] = None

# ✓ Use regular class for mutable services
class ClipboardMonitorService:
    """Mutable service that maintains state."""
    
    def __init__(self, storage_service):
        self._storage = storage_service
        self._running = False
    
    async def start(self):
        self._running = True

# ✓ Avoid inheritance, prefer composition
class BadExample:
    """Don't extend service classes."""
    pass

class GoodExample:
    """Compose services instead."""
    
    def __init__(self, monitor: IClipboardMonitor, storage: IStorageService):
        self._monitor = monitor
        self._storage = storage
```

### 6.2 Functions (Keep Small)
```python
# ✓ Good: < ~30 lines, single responsibility
async def append_clip_to_storage(clip: ClipItem, storage: IStorageService) -> None:
    """Append a clip to storage."""
    try:
        await storage.append_clip(clip)
        logger.info(f"Clip appended: {clip.timestamp}")
    except IOError as e:
        logger.error(f"Failed to append clip: {e}")
        raise

# ✗ Bad: Does too much, too long
async def process_clipboard_event():
    # Read clipboard, deduplicate, format, save, index, notify... all here!
    pass

# ✓ Extract helpers
def is_duplicate(content: str, cache: Dict[str, datetime]) -> bool:
    """Check if content is duplicate within 10s."""
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    if content_hash in cache:
        if datetime.now() - cache[content_hash] < timedelta(seconds=10):
            return True
    return False
```

### 6.3 Async Code (Prioritize async/await)
```python
# ✓ Always async for I/O
async def read_file_async(path: Path) -> str:
    """Read file asynchronously."""
    return path.read_text()  # In production, use aiofiles
    # import aiofiles
    # async with aiofiles.open(path) as f:
    #     return await f.read()

# ✗ Never block
data = asyncio.run(read_file_async(path))  # ✗ If you're already in async context

# ✓ Use asyncio.gather for parallel operations
results = await asyncio.gather(
    fetch_data(url1),
    fetch_data(url2),
    fetch_data(url3)
)

# ✓ Proper async unit test
import pytest

@pytest.mark.asyncio
async def test_append_clip():
    storage_mock = AsyncMock(spec=IStorageService)
    service = ClipboardMonitorService(storage_mock)
    
    clip = ClipItem(timestamp=datetime.now(), content="test")
    await service.append_clipboard(clip)
    
    storage_mock.append_clip.assert_called_once_with(clip)
```

### 6.4 Exception Handling
```python
# ✓ Catch specific exceptions
try:
    result = await search_service.search(query)
except ValueError as e:
    logger.error(f"Invalid search query: {e}")
    # Handle or reraise
except IOError as e:
    logger.error(f"Search service I/O error: {e}")
except Exception as e:  # ✗ Only if absolutely necessary to catch all
    logger.critical(f"Unexpected error in search: {e}", exc_info=True)
    raise

# ✓ Create custom exceptions
class DailyClipError(Exception):
    """Base exception for DailyClip."""
    pass

class ClipboardMonitorError(DailyClipError):
    """Raised when clipboard monitor fails."""
    pass

class SearchError(DailyClipError):
    """Raised when search fails."""
    pass

# ✓ Use context managers
from contextlib import contextmanager

@contextmanager
def managed_connection(db_path: Path):
    """Context manager for database connection."""
    import duckdb
    conn = duckdb.connect(str(db_path))
    try:
        yield conn
    finally:
        conn.close()

# Usage
with managed_connection(db_path) as conn:
    results = conn.execute("SELECT * FROM clips").fetchall()
```

### 6.5 Collections & List Comprehensions
```python
# ✓ List comprehensions (concise, readable)
results = [item for item in items if item.timestamp > cutoff_date]

# ✓ Dict comprehensions
mappings = {key: value for key, value in pairs if key is not None}

# ✓ Generator expressions (for large datasets, memory efficient)
large_results = (item for item in items if check(item))

# ✗ Avoid nested comprehensions if not obvious
# ✗ big_list = [[item for item in sublist] for sublist in list_of_lists]  # Hard to read

# ✓ Better: Use loop for complex logic
result = []
for sublist in list_of_lists:
    for item in sublist:
        if item.is_valid():
            result.append(process(item))
```

### 6.6 Context Managers
```python
# ✓ Always use context managers for resource management
with open(file_path) as f:
    content = f.read()

# ✓ Custom context manager
from contextlib import asynccontextmanager

@asynccontextmanager
async def managed_clipboard_monitor(storage: IStorageService):
    monitor = ClipboardMonitorService(storage)
    await monitor.start()
    try:
        yield monitor
    finally:
        await monitor.stop()

# Usage
async with managed_clipboard_monitor(storage) as monitor:
    # monitor is running
    pass
# monitor automatically stopped
```

---

## 7. Linting & Code Quality Tools

### 7.1 Setup
```bash
# Install dev dependencies
pip install black flake8 isort mypy pytest pytest-asyncio

# Config file: pyproject.toml or .flake8
```

### 7.2 Pre-commit Hook (Optional)
Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
black .
flake8 .
mypy .
pytest
```

### 7.3 Running Tools
```bash
# Format code
black dailyclip/

# Check style
flake8 dailyclip/

# Sort imports
isort dailyclip/

# Type checking
mypy dailyclip/

# Run tests
pytest
```

---

## 8. Common Mistakes to Avoid

| Mistake | ❌ Bad | ✓ Good |
|---------|--------|--------|
| Missing type hints | `def func(x):` | `def func(x: int) -> str:` |
| Bare except | `except:` | `except ValueError as e:` |
| Mutable default | `def f(items=[]):` | `def f(items: Optional[List] = None):` |
| Global state | `GLOBAL_VAR = []` in module | Pass via dependency injection |
| Magic numbers | `if len(x) > 1000:` | `if len(x) > MAX_SIZE:` |
| Long functions | Function >50 lines | Split into smaller functions |
| print() instead of logging | `print("Debug")` | `logger.debug("Debug")` |
| Catching generic Exception | `except Exception:` | `except SpecificError:` |

---

## 9. Tóm tắt Quy tắc

1. **PEP 8 + Black**: Tuân thủ hoàn toàn.
2. **Type hints**: Bắt buộc cho tất cả function/method.
3. **Async/await**: Cho mọi I/O operation.
4. **Exception handling**: Specific exceptions, logging.
5. **Dataclass + Protocol**: Domain layer entities + service interfaces.
6. **Dependency Injection**: dependency-injector package.
7. **Docstrings**: Google style, mandatory cho public functions.
8. **Tests**: Pytest, async support.
9. **Tools**: black, flake8, isort, mypy.

---

## 10. Example: Complete Module

```python
"""
example_service.py

Example service module demonstrating all coding rules.
"""

import asyncio
import logging
from typing import Protocol, Optional, List
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Constants
DEFAULT_TIMEOUT_SECONDS = 30
MAX_BATCH_SIZE = 100


# Protocols (Interfaces)
class IDataStore(Protocol):
    """Interface for data storage."""
    
    async def save(self, data: str) -> None:
        """Save data."""
        ...


# Dataclass (Entity)
@dataclass(frozen=True)
class DataItem:
    """Immutable data item."""
    
    timestamp: datetime
    content: str
    metadata: Optional[str] = None


# Service Implementation
class ExampleService:
    """Example service demonstrating coding rules."""
    
    def __init__(self, store: IDataStore):
        """Initialize service.
        
        Args:
            store: Data storage implementation.
        """
        self._store = store
        self._timer: Optional[asyncio.Task] = None
        logger.debug("ExampleService initialized")
    
    async def process_items(self, items: List[DataItem]) -> None:
        """Process items and store them.
        
        Args:
            items: List of items to process.
        
        Raises:
            ValueError: If items list is empty.
        """
        if not items:
            raise ValueError("Items list cannot be empty")
        
        for item in items:
            try:
                await self._store.save(item.content)
                logger.info(f"Item saved: {item.timestamp}")
            except Exception as e:
                logger.error(f"Failed to save item: {e}")
                continue  # Continue with next item
    
    def _validate_content(self, content: str) -> bool:
        """Validate content format.
        
        Args:
            content: Content to validate.
        
        Returns:
            True if valid, False otherwise.
        """
        return len(content) > 0 and len(content) <= 10000


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Example service module")
```

---

Tuân thủ các quy tắc này sẽ giúp code clean, consistent, testable, và dễ bảo trì!
