"""JSON logging configuration for the assistant service."""

import json
import logging
import sys
from typing import Any


class JsonFormatter(logging.Formatter):
    """Format log records as one JSON object per line."""

    _FIELDS = ("intent", "latency_ms", "session", "degraded")

    def format(self, record: logging.LogRecord) -> str:
        data: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for key in self._FIELDS:
            if hasattr(record, key):
                data[key] = getattr(record, key)
        return json.dumps(data, ensure_ascii=False)


def setup_logging(level: str = "INFO") -> None:
    """Send structured logs to stderr at the requested severity level."""
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level.upper())
