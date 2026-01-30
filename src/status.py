from typing import TYPE_CHECKING, Optional
from rich.progress import Progress, SpinnerColumn, TextColumn
from .enums import LogLevel
from .mixins import LoggableMixin

if TYPE_CHECKING:
    from .core import _PwnLogger


class _Status(LoggableMixin):
    """Manages a single-line animated spinner."""

    def __init__(
        self, logger: "_PwnLogger", message: str, level: LogLevel = LogLevel.INFO
    ):
        self.logger = logger
        self.message = message
        self.level = level
        self.visible = self.logger._should_log(self.level)
        self.task_id = None

        style = self.logger.styles.get(self.level, "")

        # Transient=True means this entire component disappears from the console
        # when .stop() is called, allowing us to print a clean final message.
        self.progress_display = Progress(
            SpinnerColumn(style=style),
            TextColumn(f"[{style}]{{task.description}}"),
            console=self.logger.console,
            transient=True,
        )

    def __enter__(self) -> "_Status":
        if self.visible:
            self.progress_display.start()
            self.task_id = self.progress_display.add_task(self.message)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> Optional[bool]:
        if not self.visible:
            return None

        try:
            if exc_type is KeyboardInterrupt:
                self.finish("Execution aborted by user", level=LogLevel.ERROR)
            elif exc_type is not None:
                self.finish(str(exc_val), level=LogLevel.ERROR)
            else:
                self.finish(level=self.level)
        finally:
            self.stop()
        return False

    async def __aenter__(self) -> "_Status":
        return self.__enter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> Optional[bool]:
        return self.__exit__(exc_type, exc_val, exc_tb)

    def stop(self) -> None:
        if self.progress_display.live.is_started:
            self.progress_display.stop()

    def update(self, message: str) -> None:
        if self.visible and self.task_id is not None:
            self.message = message
            self.progress_display.update(self.task_id, description=message)

    def finish(
        self, message: Optional[str] = None, level: Optional[LogLevel] = None
    ) -> None:
        """Halts the spinner and prints the final status message."""
        if not self.visible or self.task_id is None:
            return

        f_message = message if message is not None else self.message
        f_level = level if level else self.level
        style = self.logger.styles.get(f_level, "")

        self.stop()
        self.task_id = None

        if f_level == LogLevel.ERROR:
            self.logger.error_console.print(f_message, style=style)
        else:
            self.logger.console.print(f_message, style=style)
