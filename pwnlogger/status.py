from typing import Optional
from rich.progress import Progress, SpinnerColumn, TextColumn
from .enums import LogLevel


class _Status:
    """Handles single-line animated indicators."""

    def __init__(self, logger, message: str, level: LogLevel = LogLevel.INFO):
        self.logger = logger
        self.message = message
        self.level = level
        self.visible = self.logger._should_log(self.level)

        style = self.logger.STYLES[self.level]

        self.progress_display = Progress(
            SpinnerColumn(style=style),
            TextColumn(f"[{style}]{{task.description}}"),
            console=self.logger.console,
            transient=True,
        )
        self.task_id = None

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
                return True
            elif exc_type is not None:
                self.finish(str(exc_val), level=LogLevel.ERROR)
                return True
            else:
                self.finish(level=self.level)
        finally:
            if self.progress_display.live.is_started:
                self.progress_display.stop()
        return None

    def _sub_log(self, level: LogLevel, message: str) -> None:
        """Prints a log line above the active spinner."""
        if self.logger._should_log(level):
            style = self.logger.STYLES[level]
            self.progress_display.console.print(f"  {message}", style=style)

    def info(self, m: str) -> None:
        """Prints an info line above the active spinner."""
        self._sub_log(LogLevel.INFO, m)

    def warn(self, m: str) -> None:
        """Prints a warning line above the active spinner."""
        self._sub_log(LogLevel.WARN, m)

    def success(self, m: str) -> None:
        """Prints a success line above the active spinner."""
        self._sub_log(LogLevel.SUCCESS, m)

    def error(self, m: str) -> None:
        """Prints an error line above the active spinner."""
        self._sub_log(LogLevel.ERROR, m)

    def debug(self, m: str) -> None:
        """Prints a debug line above the active spinner."""
        self._sub_log(LogLevel.DEBUG, m)

    def update(self, message: str) -> None:
        """Updates the status message."""
        if self.visible and self.task_id is not None:
            self.message = message
            self.progress_display.update(self.task_id, description=message)

    def finish(
        self, message: Optional[str] = None, level: Optional[LogLevel] = None
    ) -> None:
        """Stops the spinner and print a final message."""
        if not self.visible or self.task_id is None:
            return

        f_message = message if message is not None else self.message
        f_level = level if level else self.level
        style = self.logger.STYLES[f_level]

        self.progress_display.stop()
        self.task_id = None

        if f_level == LogLevel.ERROR:
            self.logger.error_console.print(f_message, style=style)
        else:
            self.logger.console.print(f_message, style=style)
