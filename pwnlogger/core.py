import sys
from rich.console import Console
from .enums import LogLevel
from .progress import _Progress
from .status import _Status


class _PwnLogger:
    """Core logger class providing styled output and progress tracking."""

    STYLES = {
        LogLevel.SUCCESS: "bold green",
        LogLevel.ERROR: "bold red",
        LogLevel.WARN: "bold yellow",
        LogLevel.INFO: "bold blue",
        LogLevel.DEBUG: "dim",
    }

    def __init__(self, level: LogLevel = LogLevel.DEBUG):
        self.console = Console(file=sys.stdout, highlight=False)
        self.error_console = Console(file=sys.stderr, highlight=False)
        self.min_level = level

    def set_level(self, level: LogLevel) -> None:
        """Sets the minimum logging level."""
        if not isinstance(level, LogLevel):
            raise TypeError(
                f"Level must be a LogLevel enum, not {type(level).__name__}"
            )
        self.min_level = level

    def _should_log(self, level: LogLevel) -> bool:
        """Checks if the given level meets the minimum threshold."""
        return level >= self.min_level

    def _print(self, level: LogLevel, message: str) -> None:
        """Prints styled messages to the appropriate stream."""
        if self._should_log(level):
            style = self.STYLES.get(level, "")
            if level == LogLevel.ERROR:
                self.error_console.print(message, style=style)
            else:
                self.console.print(message, style=style)

    def success(self, message: str) -> None:
        """Logs a success message."""
        self._print(LogLevel.SUCCESS, message)

    def info(self, message: str) -> None:
        """Logs an info message."""
        self._print(LogLevel.INFO, message)

    def warn(self, message: str) -> None:
        """Logs a warning message."""
        self._print(LogLevel.WARN, message)

    def debug(self, message: str) -> None:
        """Logs a debug message."""
        self._print(LogLevel.DEBUG, message)

    def error(self, message: str) -> None:
        """Logs an error message (prints to stderr)."""
        self._print(LogLevel.ERROR, message)

    def raw(self, message: str) -> None:
        """Prints a raw message to stdout without styling."""
        self.console.print(message)

    def status(self, message: str, level: LogLevel = LogLevel.INFO) -> "_Status":
        """Creates a spinner status context manager."""
        return _Status(self, message, level)

    def progress(
        self, message: str, total: int = 100, level: LogLevel = LogLevel.INFO
    ) -> "_Progress":
        """Creates a progress bar context manager."""
        return _Progress(self, message, total, level)
