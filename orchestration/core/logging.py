"""
Structured logging configuration for Mind Protocol.

All services use this to configure consistent JSON logging
with service name, version, and structured fields.

Author: Ada (Architect)
Created: 2025-10-22
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict


class StructuredFormatter(logging.Formatter):
    """Format log records as structured JSON."""

    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": self.service_name,
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add any extra fields from record
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # Add frame_id, citizen_id if present
        for field in ["frame_id", "citizen_id", "event_type", "duration_ms"]:
            if hasattr(record, field):
                log_data[field] = getattr(record, field)

        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Format log records as human-readable text (for dev)."""

    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as text."""
        timestamp = datetime.utcnow().strftime("%H:%M:%S")
        base = f"[{timestamp}] [{self.service_name}] {record.levelname}: {record.getMessage()}"

        if record.exc_info:
            base += "\n" + self.formatException(record.exc_info)

        return base


def configure_logging(
    service_name: str,
    level: str = "INFO",
    format_type: str = "json"
) -> logging.Logger:
    """
    Configure structured logging for a service.

    Args:
        service_name: Name of the service (e.g., "websocket", "api")
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        format_type: "json" for structured logs, "text" for human-readable

    Returns:
        Logger instance for the service
    """
    # Create logger
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Create handler
    handler = logging.StreamHandler(sys.stdout)

    # Set formatter
    if format_type == "json":
        formatter = StructuredFormatter(service_name)
    else:
        formatter = TextFormatter(service_name)

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def log_with_fields(logger: logging.Logger, level: str, message: str, **fields: Any) -> None:
    """
    Log a message with additional structured fields.

    Args:
        logger: Logger instance
        level: Log level (info, warning, error, debug)
        message: Log message
        **fields: Additional structured fields to include
    """
    log_func = getattr(logger, level.lower())

    # Create a custom LogRecord with extra fields
    extra = {"extra_fields": fields}
    log_func(message, extra=extra)
