from typing import Optional
from rich.console import Console
from rich.theme import Theme
from rich.progress import (
    Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
)
from .enums import LogLevel

class _Progress:
    """Handles persistent progress bars."""
    def __init__(self, logger, message: str, total: int, level: LogLevel):
        self.logger = logger
        self.level = level
        self.visible = self.logger._should_log(self.level)
        style = self.logger.STYLES.get(self.level, "bold blue")

        local_theme = Theme({"progress.remaining": style, "progress.percentage": style})
        local_console = Console(
            theme=local_theme,
            highlight=False,
            force_terminal=self.logger.console.is_terminal,
        )

        self.progress_display = Progress(
            TextColumn(f"[{style}]{{task.description}}"),
            BarColumn(complete_style=style, finished_style=style),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=local_console,
            transient=False,
        )
        self.task_id = self.progress_display.add_task(message, total=total) if self.visible else None

    def __enter__(self):
        if self.visible:
            self.progress_display.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.visible:
            self.progress_display.stop()

    def update(self, advance: int = 0, completed: Optional[int] = None, description: Optional[str] = None) -> None:
        if self.visible and self.task_id is not None:
            self.progress_display.update(self.task_id, advance=advance, completed=completed, description=description)

    def _sub_log(self, level: LogLevel, message: str):
        if self.logger._should_log(level):
            style = self.logger.STYLES.get(level, "")
            self.progress_display.console.print(f"  {message}", style=style)

    def info(self, m): self._sub_log(LogLevel.INFO, m)
    def success(self, m): self._sub_log(LogLevel.SUCCESS, m)
    def error(self, m): self._sub_log(LogLevel.ERROR, m)
    def debug(self, m): self._sub_log(LogLevel.DEBUG, m)