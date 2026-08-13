"""Logging configuration helpers."""

import logging

from config.settings import settings


def configure_logging() -> None:
    """Configure application-wide console logging once."""

    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )