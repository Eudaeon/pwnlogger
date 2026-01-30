import sys
from typing import TYPE_CHECKING, Dict, Optional
from rich.console import Console
from .enums import LogLevel
from .theme import DEFAULT_STYLES

if TYPE_CHECKING:
    from .progress import _Progress
    from .status import _Status


class _PwnLogger:
    """Core logger class."""

    def __init__(
        self,
        level: LogLevel = LogLevel.DEBUG,
        styles: Optional[Dict[LogLevel, str]] = None,
    ):
        # highlight=False prevents rich from auto-highlighting numbers/paths
        self.console = Console(file=sys.stdout, highlight=False)
        self.error_console = Console(file=sys.stderr, highlight=False)
        self.min_level = level
        self.styles = DEFAULT_STYLES.copy()
        if styles:
            self.styles.update(styles)

    def set_level(self, level: LogLevel) -> None:
        if not isinstance(level, LogLevel):
            raise TypeError(
                f"Level must be a LogLevel enum, not {type(level).__name__}"
            )
        self.min_level = level

    def _should_log(self, level: LogLevel) -> bool:
        return level >= self.min_level

    def log(self, level: LogLevel, *objects) -> None:
        """Dispatches the message to the correct console based on severity."""
        if self._should_log(level):
            style = self.styles.get(level, "")
            console = self.error_console if level == LogLevel.ERROR else self.console
            console.print(*objects, style=style)

    def success(self, *objects) -> None:
        self.log(LogLevel.SUCCESS, *objects)

    def info(self, *objects) -> None:
        self.log(LogLevel.INFO, *objects)

    def warn(self, *objects) -> None:
        self.log(LogLevel.WARN, *objects)

    def debug(self, *objects) -> None:
        self.log(LogLevel.DEBUG, *objects)

    def error(self, *objects) -> None:
        self.log(LogLevel.ERROR, *objects)

    def raw(self, *objects) -> None:
        """Bypasses styling to print raw text directly to stdout."""
        self.console.print(*objects)

    def status(self, message: str, level: LogLevel = LogLevel.INFO) -> "_Status":
        from .status import _Status

        return _Status(self, message, level)

    def progress(
        self, message: str, total: int = 100, level: LogLevel = LogLevel.INFO
    ) -> "_Progress":
        from .progress import _Progress

        return _Progress(self, message, total, level)
