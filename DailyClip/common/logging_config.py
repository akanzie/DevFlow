"""Logging helpers for DailyClip."""

from __future__ import annotations

import logging
from pathlib import Path

from DailyClip.core.config import AppConfig


def configure_logging(log_dir: Path | None = None) -> None:
    """Configure application logging once."""
    target_dir = log_dir or AppConfig.get_data_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    log_file = target_dir / 'dailyclip.log'

    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(),
        ],
    )
