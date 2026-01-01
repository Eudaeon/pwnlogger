from rich.console import Console
from .enums import LogLevel
from .status import _Status
from .progress import _Progress


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
        self.console = Console(highlight=False)
        self.min_level = level

    def set_level(self, level: LogLevel) -> None:
        if not isinstance(level, LogLevel):
            raise TypeError(
                f"Level must be a LogLevel enum, not {type(level).__name__}"
            )
        self.min_level = level

    def _should_log(self, level: LogLevel) -> bool:
        return level >= self.min_level

    def _print(self, level: LogLevel, message: str) -> None:
        if self._should_log(level):
            style = self.STYLES.get(level, "")
            self.console.print(message, style=style)

    def success(self, message: str) -> None:
        self._print(LogLevel.SUCCESS, message)

    def info(self, message: str) -> None:
        self._print(LogLevel.INFO, message)

    def warn(self, message: str) -> None:
        self._print(LogLevel.WARN, message)

    def debug(self, message: str) -> None:
        self._print(LogLevel.DEBUG, message)

    def error(self, message: str) -> None:
        self._print(LogLevel.ERROR, message)

    def raw(self, message: str) -> None:
        self.console.print(message)

    def status(self, message: str, level: LogLevel = LogLevel.INFO):
        return _Status(self, message, level)

    def progress(self, message: str, total: int = 100, level: LogLevel = LogLevel.INFO):
        return _Progress(self, message, total, level)
