from typing import Optional
from rich.console import Console
from rich.theme import Theme
from rich.progress import (
    Progress,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
)
from .enums import LogLevel


class _Progress:
    """Handles persistent progress bars."""

    def __init__(self, logger, message: str, total: int, level: LogLevel):
        self.logger = logger
        self.level = level
        self.visible = self.logger._should_log(self.level)
        self.message = message
        self.total = total

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
        self.task_id = None

    def __enter__(self):
        if self.visible:
            self.progress_display.start()
            self.task_id = self.progress_display.add_task(
                self.message, total=self.total
            )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.visible:
            return False

        try:
            if exc_type is KeyboardInterrupt:
                self.finish("Execution aborted by user", level=LogLevel.ERROR)
                return True
            elif exc_type is not None:
                self.finish(exc_val, level=LogLevel.ERROR)
                return True
            else:
                if self.task_id is not None:
                    self.finish()
        finally:
            if self.progress_display.live.is_started:
                self.progress_display.stop()

    def update(
        self,
        advance: int = 0,
        completed: Optional[int] = None,
        description: Optional[str] = None,
    ) -> None:
        if description is not None:
            self.message = description
        if self.visible and self.task_id is not None:
            self.progress_display.update(
                self.task_id,
                advance=advance,
                completed=completed,
                description=description,
            )

    def finish(
        self, message: Optional[str] = None, level: Optional[LogLevel] = None
    ) -> None:
        if not self.visible or self.task_id is None:
            return

        f_message = message if message is not None else self.message
        f_level = level if level else self.level
        style = self.logger.STYLES.get(f_level, "")

        for column in self.progress_display.columns:
            if isinstance(column, BarColumn):
                column.complete_style = style
                column.finished_style = style
            elif type(column) is TextColumn:
                column.text_format = "{task.description}"
            elif hasattr(column, "style"):
                column.style = style

        self.progress_display.console.push_theme(
            Theme({"progress.remaining": style, "progress.percentage": style})
        )

        update_kwargs = {"description": f"[{style}]{f_message}[/]", "refresh": True}
        if f_level != LogLevel.ERROR:
            update_kwargs["completed"] = self.total

        self.progress_display.update(self.task_id, **update_kwargs)

        if self.progress_display.live.is_started:
            self.progress_display.stop()

        self.task_id = None

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
