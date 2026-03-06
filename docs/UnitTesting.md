# Tài liệu Hướng dẫn Unit Test (Unit Testing Guidelines) - Python  
**Dự án:** DailyClip (Python version)  
**Phiên bản:** 1.0  
**Áp dụng cho:** Toàn bộ codebase testable (Domain, Application, Infrastructure layers)  
**Mục tiêu:** Đảm bảo chất lượng code, dễ refactor, phát hiện bug sớm. Ưu tiên **unit test nhanh, độc lập, dễ đọc**.

---

## 1. Testing Strategy: Layered Architecture

Theo Clean Architecture, test từ trong ra ngoài (inside-out):

| Layer              | Loại test chính          | Mocks cần thiết? | Công cụ khuyến nghị          | Coverage mục tiêu |
|--------------------|--------------------------|------------------|------------------------------|-------------------|
| **Domain**         | Pure unit tests          | Không            | pytest                       | >95%              |
| **Application**    | Unit tests (services)    | Có (interfaces)  | pytest + pytest-mock         | >85%              |
| **Infrastructure** | Unit + nhẹ integration   | Có (nếu có thể)  | pytest + pytest-mock         | >70% (critical path) |
| **Presentation**   | Widget/Signal tests      | Có (services)    | pytest + pytest-mock (PyQt6 hard to test) | >60% |
| **UI (PyQt6 Views)** | Manual / Integration test | -                | pytest-qt (optional)         | Manual testing    |

**Thứ tự ưu tiên viết test**:
1. Domain logic (entities, value objects, business rules).
2. Application services / use cases.
3. Infrastructure (storage, search).
4. Presentation (ViewModels/Signal handlers).
5. UI Views (skip unit test, do integration test if needed).

---

## 2. Setup & Tools

### 2.1 Project Structure
```
dailyclip/
├── dailyclip/              # Source code
│   ├── core/
│   ├── application/
│   ├── infrastructure/
│   ├── presentation/
│   └── common/
│
├── tests/                  # Test directory (parallel structure)
│   ├── __init__.py
│   ├── conftest.py         # Pytest fixtures & config
│   ├── test_entities.py    # Domain layer tests
│   ├── core/
│   │   ├── __init__.py
│   │   └── test_entities.py
│   ├── application/
│   │   └── test_services.py
│   ├── infrastructure/
│   │   ├── test_clipboard.py
│   │   ├── test_search.py
│   │   └── test_storage.py
│   └── presentation/
│       └── test_viewmodels.py
│
└── setup.py / pyproject.toml
```

### 2.2 Install Dependencies
```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock
```

Add to `pyproject.toml` or `setup.cfg`:
```ini
[tool:pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --cov=dailyclip --cov-report=html
```

### 2.3 Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=dailyclip --cov-report=html

# Run specific test file
pytest tests/test_entities.py

# Run specific test
pytest tests/test_entities.py::TestClipItem::test_creation

# Watch mode (requires pytest-watch)
pip install pytest-watch
ptw

# Parallel execution (requires pytest-xdist)
pip install pytest-xdist
pytest -n auto
```

---

## 3. Test Basics & Best Practices

### 3.1 Test Structure (AAA Pattern)
```python
import pytest
from dailyclip.core.entities import ClipItem, ClipType
from datetime import datetime

class TestClipItem:
    """Test ClipItem entity."""
    
    def test_creation_success(self):
        """Test creating a ClipItem successfully."""
        # Arrange: Set up test data
        timestamp = datetime.now()
        content = "test content"
        
        # Act: Execute the function/method under test
        clip = ClipItem(
            timestamp=timestamp,
            content=content,
            clip_type=ClipType.TEXT
        )
        
        # Assert: Verify the result
        assert clip.timestamp == timestamp
        assert clip.content == content
        assert clip.clip_type == ClipType.TEXT
    
    def test_immutability(self):
        """Test that ClipItem is immutable."""
        clip = ClipItem(
            timestamp=datetime.now(),
            content="test",
            clip_type=ClipType.TEXT
        )
        
        with pytest.raises(AttributeError):
            clip.content = "modified"  # Should fail (frozen dataclass)
```

### 3.2 Test Naming Convention
Format: `test_[unit_under_test]_[scenario]_[expected_result]`

```python
# ✓ Clear, describes what's being tested
def test_is_duplicate_same_content_10_seconds_returns_true():
    pass

def test_search_empty_query_raises_value_error():
    pass

def test_append_clip_valid_data_saves_successfully():
    pass

# ✗ Unclear
def test1():
    pass

def test_create():
    pass

def test_search_test():
    pass
```

### 3.3 One Concept Per Test
```python
# ✓ Good: Test one behavior/assertion
def test_append_clip_success_calls_storage_once():
    """Test that valid clip appends once."""
    storage_mock = Mock(spec=IStorageService)
    service = ClipboardMonitorService(storage_mock)
    
    clip = create_test_clip()
    service.append_clip(clip)
    
    storage_mock.append_clip.assert_called_once_with(clip)

def test_append_clip_success_logs_info():
    """Test that append clips logs info message."""
    logger_mock = Mock()
    storage_mock = Mock()
    service = ClipboardMonitorService(storage_mock, logger_mock)
    
    service.append_clip(create_test_clip())
    
    logger_mock.info.assert_called()

# ✗ Bad: Testing multiple behaviors
def test_append_clip_everything():
    """Test everything about append."""
    storage_mock = Mock()
    logger_mock = Mock()
    service = ClipboardMonitorService(storage_mock, logger_mock)
    
    clip = create_test_clip()
    service.append_clip(clip)
    
    # Todo many assertions...
    storage_mock.append_clip.assert_called_once()
    logger_mock.info.assert_called()
    # ... more asserts
    # Hard to diagnose which failed!
```

### 3.4 Use Fixtures for Reusable Setup
```python
import pytest
from dailyclip.core.entities import ClipItem, ClipType
from datetime import datetime

@pytest.fixture
def sample_clip():
    """Provide sample ClipItem for tests."""
    return ClipItem(
        timestamp=datetime(2026, 3, 6, 10, 30, 0),
        content="test content",
        clip_type=ClipType.TEXT
    )

@pytest.fixture
def storage_mock():
    """Provide mock storage service."""
    from unittest.mock import Mock
    return Mock(spec=IStorageService)

@pytest.fixture
def clipboard_monitor(storage_mock):
    """Provide ClipboardMonitorService with mocked storage."""
    return ClipboardMonitorService(storage_mock)

# Usage in tests
class TestClipboardMonitor:
    def test_append_saves(self, clipboard_monitor, storage_mock, sample_clip):
        clipboard_monitor.append_clip(sample_clip)
        storage_mock.append_clip.assert_called_once_with(sample_clip)
```

### 3.5 conftest.py for Global Fixtures
```python
# tests/conftest.py
import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime
from dailyclip.core.entities import ClipItem, ClipType
from dailyclip.core.protocols import IStorageService, ISearchService

@pytest.fixture
def sample_clip():
    """Test clip."""
    return ClipItem(
        timestamp=datetime(2026, 3, 6, 10, 0, 0),
        content="test",
        clip_type=ClipType.TEXT
    )

@pytest.fixture
def storage_mock():
    """Mock storage service."""
    mock = AsyncMock(spec=IStorageService)
    mock.append_clip = AsyncMock()
    mock.create_daily_folder = Mock(return_value=Path("/mock/path"))
    return mock

@pytest.fixture
def search_mock():
    """Mock search service."""
    mock = AsyncMock(spec=ISearchService)
    mock.search = AsyncMock(return_value=[])
    return mock

@pytest.fixture
def logger_mock():
    """Mock logger."""
    return Mock()
```

---

## 4. Testing Different Layers

### 4.1 Domain Layer Tests (No Mocks)
```python
# tests/core/test_entities.py
import pytest
from datetime import datetime
from dailyclip.core.entities import ClipItem, ClipType

class TestClipItem:
    """Test ClipItem domain entity."""
    
    def test_creation_with_all_fields(self):
        """Test creating clip with all fields."""
        timestamp = datetime(2026, 3, 6, 10, 0, 0)
        clip = ClipItem(
            timestamp=timestamp,
            content="code snippet",
            clip_type=ClipType.TEXT,
            format="code"
        )
        
        assert clip.timestamp == timestamp
        assert clip.content == "code snippet"
        assert clip.clip_type == ClipType.TEXT
        assert clip.format == "code"
    
    def test_creation_with_minimal_fields(self):
        """Test creating clip with minimal required fields."""
        clip = ClipItem(
            timestamp=datetime.now(),
            content="text",
            clip_type=ClipType.TEXT
        )
        
        assert clip.format == "plain"  # Default value
    
    def test_immutability(self):
        """Test clip is immutable (frozen dataclass)."""
        clip = ClipItem(
            timestamp=datetime.now(),
            content="text",
            clip_type=ClipType.TEXT
        )
        
        with pytest.raises(AttributeError):
            clip.content = "changed"
    
    @pytest.mark.parametrize("clip_type", [ClipType.TEXT, ClipType.IMAGE, ClipType.HTML])
    def test_all_clip_types(self, clip_type):
        """Test all ClipType values are valid."""
        clip = ClipItem(
            timestamp=datetime.now(),
            content="data",
            clip_type=clip_type
        )
        
        assert clip.clip_type == clip_type
```

### 4.2 Application Layer Tests (With Mocks)
```python
# tests/application/test_services.py
import pytest
from unittest.mock import AsyncMock, Mock, call
from datetime import datetime
from dailyclip.application.services.clipboard import ClipboardMonitorService
from dailyclip.core.entities import ClipItem, ClipType
from dailyclip.core.protocols import IStorageService, ISearchService

class TestClipboardMonitor:
    """Test ClipboardMonitorService application layer."""
    
    @pytest.mark.asyncio
    async def test_process_clipboard_saves_clip(self, storage_mock, sample_clip):
        """Test processing clipboard saves clip to storage."""
        search_mock = AsyncMock(spec=ISearchService)
        monitor = ClipboardMonitorService(storage_mock, search_mock)
        
        await monitor._process_clipboard(sample_clip.content)
        
        storage_mock.append_clip.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_duplicate_within_10s_skipped(self, storage_mock, search_mock):
        """Test duplicate clips within 10s are skipped."""
        monitor = ClipboardMonitorService(storage_mock, search_mock)
        content = "duplicate test"
        
        await monitor._process_clipboard(content)
        await monitor._process_clipboard(content)  # Same content
        
        # Check called only once
        storage_mock.append_clip.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_different_content_not_skipped(self, storage_mock, search_mock):
        """Test different content is NOT skipped."""
        monitor = ClipboardMonitorService(storage_mock, search_mock)
        
        await monitor._process_clipboard("content1")
        await monitor._process_clipboard("content2")
        
        # Check called twice
        assert storage_mock.append_clip.call_count == 2
    
    @pytest.mark.asyncio
    async def test_storage_error_logged(self, storage_mock, search_mock, logger_mock):
        """Test storage errors are logged."""
        storage_mock.append_clip.side_effect = IOError("Storage failed")
        monitor = ClipboardMonitorService(storage_mock, search_mock)
        
        # Should not raise, just log
        await monitor._process_clipboard("content")
        
        # Verify it tried to log error
        # (depends on your logging implementation)
```

### 4.3 Infrastructure Layer Tests
```python
# tests/infrastructure/test_search.py
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from dailyclip.infrastructure.duckdb_search import DuckDBSearchService
from dailyclip.core.entities import SearchResult

class TestDuckDBSearchService:
    """Test DuckDB search service."""
    
    @pytest.fixture
    def search_service(self, tmp_path):
        """Create search service with temporary database."""
        db_path = tmp_path / "test.duckdb"
        return DuckDBSearchService(db_path)
    
    @pytest.mark.asyncio
    async def test_search_returns_results(self, search_service):
        """Test search returns results."""
        # Arrange: Insert test data
        # (Simplified - real test would use actual DuckDB)
        
        # Act
        results = await search_service.search("test", limit=10)
        
        # Assert
        assert isinstance(results, list)
        
    @pytest.mark.asyncio
    async def test_search_empty_query_raises_error(self, search_service):
        """Test empty query raises ValueError."""
        with pytest.raises(ValueError):
            await search_service.search("", limit=10)
    
    @pytest.mark.asyncio
    async def test_search_limit_respected(self, search_service):
        """Test search respects limit parameter."""
        # Would need actual data inserted
        results = await search_service.search("test", limit=5)
        assert len(results) <= 5
```

### 4.4 Async Tests
```python
# Example of testing async code
import pytest
from unittest.mock import AsyncMock

class TestAsyncOperations:
    """Test async operations."""
    
    @pytest.mark.asyncio
    async def test_async_operation_success(self):
        """Test successful async operation."""
        mock_service = AsyncMock()
        mock_service.fetch.return_value = {"status": "ok"}
        
        result = await mock_service.fetch()
        
        assert result["status"] == "ok"
        mock_service.fetch.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_async_operation_with_exception(self):
        """Test async operation that raises exception."""
        mock_service = AsyncMock()
        mock_service.fetch.side_effect = IOError("Connection failed")
        
        with pytest.raises(IOError):
            await mock_service.fetch()
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test multiple async operations run concurrently."""
        import asyncio
        
        mock1 = AsyncMock(return_value=1)
        mock2 = AsyncMock(return_value=2)
        
        results = await asyncio.gather(mock1(), mock2())
        
        assert results == [1, 2]
```

---

## 5. Mocking & Test Doubles

### 5.1 Using unittest.mock
```python
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from dailyclip.core.protocols import IStorageService

# ✓ Mock for synchronous function
storage_mock = Mock(spec=IStorageService)
storage_mock.append_clip.return_value = None

# ✓ AsyncMock for async function
search_mock = AsyncMock()
search_mock.search.return_value = []

# ✓ side_effect for multiple calls / exceptions
storage_mock.append_clip.side_effect = [None, IOError("Fail")]

# First call succeeds, second raises IOError
storage_mock.append_clip()  # Ok
storage_mock.append_clip()  # Raises IOError

# ✓ Verify calls
storage_mock.append_clip.assert_called_once()
storage_mock.append_clip.assert_called_with(expected_arg)
storage_mock.append_clip.assert_not_called()

# ✓ Check call count
assert storage_mock.append_clip.call_count == 3
```

### 5.2 Patch Decorator for External Dependencies
```python
from unittest.mock import patch
import pytest

class TestClipboardMonitor:
    @patch('dailyclip.infrastructure.clipboard_monitor.pyperclip.paste')
    def test_monitor_reads_clipboard(self, mock_paste):
        """Test clipboard is read."""
        mock_paste.return_value = "clipboard content"
        
        # Test code that calls pyperclip.paste()
        # ...
        
        mock_paste.assert_called()
```

---

## 6. Test Parameterization

### 6.1 Using @pytest.mark.parametrize
```python
import pytest
from dailyclip.core.entities import ClipType

class TestClipTypes:
    @pytest.mark.parametrize("clip_type", [
        ClipType.TEXT,
        ClipType.IMAGE,
        ClipType.HTML
    ])
    def test_all_clip_types_valid(self, clip_type):
        """Test all clip types."""
        assert clip_type in [ClipType.TEXT, ClipType.IMAGE, ClipType.HTML]
    
    @pytest.mark.parametrize("query,expected_count", [
        ("python", 5),
        ("async", 3),
        ("test", 10),
    ])
    @pytest.mark.asyncio
    async def test_search_various_queries(self, search_service, query, expected_count):
        """Test search with various queries."""
        # (Simplified - would need actual data)
        results = await search_service.search(query)
        # Check expected_count...
```

### 6.2 Using @pytest.mark.parametrize with Multiple Parameters
```python
@pytest.mark.parametrize("input,expected", [
    ("", False),  # Empty string
    (None, False),  # None value
    ("valid", True),  # Valid input
])
def test_is_valid_input(input, expected):
    assert is_valid(input) == expected
```

---

## 7. Coverage Analysis

### 7.1 Generate Coverage Report
```bash
# Generate coverage HTML report
pytest --cov=dailyclip --cov-report=html

# View coverage
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
# or
start htmlcov/index.html  # Windows
```

### 7.2 Coverage Configuration (pyproject.toml)
```ini
[tool:pytest]
addopts = 
    --cov=dailyclip
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=80  # Fail if coverage < 80%

[coverage:run]
omit =
    */tests/*
    */site-packages/*

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
```

---

## 8. Best Practices Checklist

- ✓ Write tests BEFORE or ALONGSIDE code (TDD mindset).
- ✓ Keep tests simple and focused (single concept per test).
- ✓ Use fixtures for reusable setup.
- ✓ Mock external dependencies (storage, search, clipboard).
- ✓ Test edge cases (empty input, None, exceptions).
- ✓ Use `@pytest.mark.asyncio` for async tests.
- ✓ Aim for >85% coverage (>95% for critical path).
- ✓ Name tests clearly (describe what you're testing).
- ✓ Use parametrize for multiple similar tests.
- ✓ Verify calls to mocks (assert_called_once, assert_called_with).

---

## 9. Example: Complete Test Module

```python
# tests/test_complete_example.py
import pytest
from unittest.mock import AsyncMock, patch
from pathlib import Path
from datetime import datetime
from dailyclip.core.entities import ClipItem, ClipType
from dailyclip.infrastructure.clipboard_monitor import ClipboardMonitorService

@pytest.fixture
def sample_clip():
    return ClipItem(
        timestamp=datetime.now(),
        content="test content",
        clip_type=ClipType.TEXT
    )

@pytest.fixture
def storage_mock():
    mock = AsyncMock()
    mock.append_clip = AsyncMock()
    return mock

@pytest.fixture
def search_mock():
    mock = AsyncMock()
    mock.index_daily_data = AsyncMock()
    return mock

class TestClipboardMonitorIntegration:
    """Integration tests for clipboard monitor."""
    
    @pytest.mark.asyncio
    async def test_monitor_full_flow(self, storage_mock, search_mock, sample_clip):
        """Test full clipboard monitoring flow."""
        monitor = ClipboardMonitorService(storage_mock, search_mock)
        
        # Process clipboard
        await monitor._process_clipboard(sample_clip.content)
        
        # Verify storage was called
        storage_mock.append_clip.assert_called_once()
        
        # Verify search was updated
        search_mock.index_daily_data.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_duplicate_skipped(self, storage_mock, search_mock):
        """Test duplicates are skipped."""
        monitor = ClipboardMonitorService(storage_mock, search_mock)
        
        await monitor._process_clipboard("duplicate")
        await monitor._process_clipboard("duplicate")
        
        # Verify only called once (duplicate skipped)
        storage_mock.append_clip.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling(self, storage_mock, search_mock):
        """Test error is handled gracefully."""
        storage_mock.append_clip.side_effect = IOError("Storage failed")
        monitor = ClipboardMonitorService(storage_mock, search_mock)
        
        # Should not raise
        try:
            await monitor._process_clipboard("content")
        except IOError:
            pytest.fail("Should not raise IOError")
```

---

## 10. Running Tests in CI/CD

Example GitHub Actions workflow:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest  # DailyClip is Windows-only
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        pytest --cov=dailyclip --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

---

Tuân thủ các nguyên tắc này sẽ giúp code bạn testable, maintainable, và reliable!
