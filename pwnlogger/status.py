from typing import Optional
from rich.progress import Progress, SpinnerColumn, TextColumn
from .enums import LogLevel


class _Status:
    """Handles single-line animated indicators."""

    def __init__(self, logger, message: str, level: LogLevel):
        self.logger = logger
        self.message = message
        self.level = level
        self.visible = self.logger._should_log(self.level)

        style = self.logger.STYLES.get(self.level, "bold blue")
        self.progress_display = Progress(
            SpinnerColumn(style=style),
            TextColumn(f"[{style}]{{task.description}}"),
            console=self.logger.console,
            transient=True,
        )
        self.task_id = None

    def __enter__(self):
        if self.visible:
            self.progress_display.start()
            self.task_id = self.progress_display.add_task(self.message)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.visible:
            return None

        try:
            if exc_type is KeyboardInterrupt:
                self.finish("Execution aborted by user", level=LogLevel.ERROR)
                return True
            elif exc_type is not None:
                self.finish(exc_val, level=LogLevel.ERROR)
                return True
            else:
                self.finish(level=self.level)
        finally:
            if self.progress_display.live.is_started:
                self.progress_display.stop()
        return None

    def _sub_log(self, level: LogLevel, message: str):
        if self.logger._should_log(level):
            style = self.logger.STYLES.get(level, "")
            self.progress_display.console.print(f"  {message}", style=style)

    def info(self, m):
        self._sub_log(LogLevel.INFO, m)

    def success(self, m):
        self._sub_log(LogLevel.SUCCESS, m)

    def error(self, m):
        self._sub_log(LogLevel.ERROR, m)

    def debug(self, m):
        self._sub_log(LogLevel.DEBUG, m)

    def update(self, message: str) -> None:
        if self.visible and self.task_id is not None:
            self.message = message
            self.progress_display.update(self.task_id, description=message)

    def finish(
        self, message: Optional[str] = None, level: Optional[LogLevel] = None
    ) -> None:
        if not self.visible or self.task_id is None:
            return
        f_message = message if message is not None else self.message
        f_level = level if level else self.level
        style = self.logger.STYLES.get(f_level, "")
        self.progress_display.stop()
        self.logger.console.print(f_message, style=style)
        self.task_id = None
