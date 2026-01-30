from typing import TYPE_CHECKING, Any, Protocol
from rich.console import Console
from .enums import LogLevel

if TYPE_CHECKING:
    from .core import _PwnLogger


class HasConsole(Protocol):
    console: Console


class DisplayProtocol(Protocol):
    logger: "_PwnLogger"
    progress_display: HasConsole


class LoggableMixin:
    """Mixin that injects standard logging methods into active display contexts."""

    def _sub_log(self: Any, level: LogLevel, *objects: Any) -> None:
        """Internal helper to print a indented log line associated with the active task."""
        # We assume 'self' has 'logger' and 'progress_display' via usage in Status/Progress
        if self.logger._should_log(level):
            style = self.logger.styles.get(level, "")
            self.progress_display.console.print(" ", *objects, style=style)

    def success(self, *objects: Any) -> None:
        self._sub_log(LogLevel.SUCCESS, *objects)

    def info(self, *objects: Any) -> None:
        self._sub_log(LogLevel.INFO, *objects)

    def warn(self, *objects: Any) -> None:
        self._sub_log(LogLevel.WARN, *objects)

    def error(self, *objects: Any) -> None:
        self._sub_log(LogLevel.ERROR, *objects)

    def debug(self, *objects: Any) -> None:
        self._sub_log(LogLevel.DEBUG, *objects)
