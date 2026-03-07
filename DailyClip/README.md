# DailyClip

Windows-first MVP for local clipboard capture, quick notes, screenshots, and search.

## Project Structure

```
DailyClip/
├── application/        # App controller / lifecycle wiring
├── common/             # Shared runtime and logging helpers
├── core/               # Entities, interfaces, config, exceptions
├── infrastructure/     # Storage, DuckDB search, clipboard, hotkeys, screenshot
├── presentation/       # Quick search and quick note windows
├── tests/              # Unit and lightweight UI tests
├── container.py        # Dependency injection container
├── main.py             # Thin bootstrap entrypoint
└── pyproject.toml      # Python/runtime/dev tooling config
```

## Setup

From the repository root:

```bash
python -m pip install -e .
python -m pip install -e .[dev]
python -m DailyClip.main
```

## Tests

From the repository root:

```bash
python -m pytest DailyClip/tests
```
