"""
Colored Logging Utility for Doc Ingestion Pipeline

Provides colored, structured logging with visual hierarchy for better readability.

Author: Felix (Consciousness Engineer)
Date: 2025-10-29
"""

import logging
import sys
from typing import Optional


# ANSI color codes
class Colors:
    """ANSI color codes for terminal output"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright foreground colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


class ColoredFormatter(logging.Formatter):
    """Colored log formatter with visual hierarchy"""

    # Level-specific colors and symbols
    LEVEL_COLORS = {
        logging.DEBUG: Colors.BRIGHT_BLACK,
        logging.INFO: Colors.BRIGHT_CYAN,
        logging.WARNING: Colors.BRIGHT_YELLOW,
        logging.ERROR: Colors.BRIGHT_RED,
        logging.CRITICAL: Colors.BOLD + Colors.BRIGHT_RED,
    }

    LEVEL_SYMBOLS = {
        logging.DEBUG: "🔍",
        logging.INFO: "✓",
        logging.WARNING: "⚠",
        logging.ERROR: "✗",
        logging.CRITICAL: "🔥",
    }

    # Component-specific colors (for logger names)
    COMPONENT_COLORS = {
        "graph": Colors.BLUE,
        "SchemaRegistry": Colors.MAGENTA,
        "LLMClusterCreator": Colors.GREEN,
        "embedding": Colors.CYAN,
        "chunker": Colors.YELLOW,
        "lint": Colors.BRIGHT_MAGENTA,
        "orchestrator": Colors.BRIGHT_BLUE,
        "state": Colors.BRIGHT_GREEN,
    }

    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        if not self.use_colors:
            return self._format_plain(record)

        # Extract component name from logger name or record
        component = self._extract_component(record)

        # Get colors
        level_color = self.LEVEL_COLORS.get(record.levelno, Colors.WHITE)
        component_color = self._get_component_color(component)
        symbol = self.LEVEL_SYMBOLS.get(record.levelno, "·")

        # Format timestamp
        timestamp = f"{Colors.DIM}{self.formatTime(record, '%H:%M:%S')}{Colors.RESET}"

        # Format level with symbol
        level_str = f"{level_color}{symbol} {record.levelname:8s}{Colors.RESET}"

        # Format component
        component_str = f"{component_color}[{component}]{Colors.RESET}"

        # Format message
        message = record.getMessage()

        # Highlight important patterns in message
        message = self._highlight_message(message)

        # Build final format
        return f"{timestamp} {level_str} {component_str} {message}"

    def _format_plain(self, record: logging.LogRecord) -> str:
        """Plain format without colors (for file output or non-TTY)"""
        component = self._extract_component(record)
        timestamp = self.formatTime(record, '%H:%M:%S')
        return f"{timestamp} {record.levelname:8s} [{component}] {record.getMessage()}"

    def _extract_component(self, record: logging.LogRecord) -> str:
        """Extract component name from logger name or message"""
        # Check if message has component prefix (e.g., "[SchemaRegistry]")
        message = record.getMessage()
        if message.startswith("[") and "]" in message:
            return message[1:message.index("]")]

        # Otherwise use logger name
        name = record.name
        if "." in name:
            # Use last part of dotted name (e.g., "doc_ingestion.graph" -> "graph")
            return name.split(".")[-1]
        return name

    def _get_component_color(self, component: str) -> str:
        """Get color for component"""
        # Check exact match first
        if component in self.COMPONENT_COLORS:
            return self.COMPONENT_COLORS[component]

        # Check partial match
        for key, color in self.COMPONENT_COLORS.items():
            if key.lower() in component.lower():
                return color

        # Default color
        return Colors.WHITE

    def _highlight_message(self, message: str) -> str:
        """Highlight important patterns in message"""
        # Remove component prefix if present (already in component_str)
        if message.startswith("[") and "]" in message:
            message = message[message.index("]") + 1:].strip()

        # Highlight numbers
        import re
        message = re.sub(
            r'\b(\d+)\b',
            f'{Colors.BOLD}\\1{Colors.RESET}',
            message
        )

        # Highlight success indicators
        message = message.replace("✓", f"{Colors.BRIGHT_GREEN}✓{Colors.RESET}")
        message = message.replace("✅", f"{Colors.BRIGHT_GREEN}✅{Colors.RESET}")

        # Highlight file paths
        message = re.sub(
            r'([a-zA-Z0-9_\-./]+\.(py|json|md|txt))',
            f'{Colors.DIM}\\1{Colors.RESET}',
            message
        )

        return message


def setup_logger(
    name: str,
    level: int = logging.INFO,
    use_colors: bool = True
) -> logging.Logger:
    """
    Setup colored logger for doc ingestion components

    Args:
        name: Logger name (typically __name__)
        level: Logging level (default: INFO)
        use_colors: Whether to use colored output (auto-detect if TTY)

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)

    # Avoid adding multiple handlers
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Auto-detect TTY if not explicitly specified
    is_tty = sys.stdout.isatty() if use_colors else False

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Set formatter
    formatter = ColoredFormatter(use_colors=is_tty)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


def log_section(logger: logging.Logger, title: str, level: int = logging.INFO):
    """
    Log a visual section separator

    Args:
        logger: Logger instance
        title: Section title
        level: Log level
    """
    separator = "─" * 60

    if level == logging.INFO:
        logger.info(f"\n{Colors.BRIGHT_BLUE}{separator}{Colors.RESET}")
        logger.info(f"{Colors.BRIGHT_BLUE}{Colors.BOLD}{title}{Colors.RESET}")
        logger.info(f"{Colors.BRIGHT_BLUE}{separator}{Colors.RESET}\n")
    else:
        logger.log(level, f"\n{separator}")
        logger.log(level, title)
        logger.log(level, f"{separator}\n")


def log_table(logger: logging.Logger, headers: list, rows: list, level: int = logging.INFO):
    """
    Log data in table format

    Args:
        logger: Logger instance
        headers: Column headers
        rows: List of row data (each row is a list matching headers)
        level: Log level
    """
    if not rows:
        logger.log(level, "(empty)")
        return

    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    # Format header
    header_str = " │ ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    separator = "─┼─".join("─" * w for w in widths)

    logger.log(level, f"{Colors.BOLD}{header_str}{Colors.RESET}")
    logger.log(level, separator)

    # Format rows
    for row in rows:
        row_str = " │ ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row))
        logger.log(level, row_str)


def log_progress(logger: logging.Logger, current: int, total: int, item: str = "items"):
    """
    Log progress indicator

    Args:
        logger: Logger instance
        current: Current progress
        total: Total items
        item: Item description
    """
    percent = (current / total * 100) if total > 0 else 0
    bar_length = 30
    filled = int(bar_length * current / total) if total > 0 else 0
    bar = "█" * filled + "░" * (bar_length - filled)

    logger.info(
        f"{Colors.BRIGHT_CYAN}Progress:{Colors.RESET} "
        f"[{bar}] {current}/{total} {item} ({percent:.1f}%)"
    )
