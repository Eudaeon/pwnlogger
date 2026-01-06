from typing import Optional
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.theme import Theme
from .enums import LogLevel


class _Progress:
    """Handles persistent progress bars."""

    def __init__(
        self, logger, message: str, total: int, level: LogLevel = LogLevel.INFO
    ):
        self.logger = logger
        self.level = level
        self.visible = self.logger._should_log(self.level)
        self.message = message
        self.total = total

        style = self.logger.STYLES[self.level]
        self.local_theme = Theme(
            {"progress.remaining": style, "progress.percentage": style}
        )

        local_console = Console(
            theme=self.local_theme,
            highlight=False,
            force_terminal=self.logger.console.is_terminal,
            file=self.logger.console.file,
        )

        self.progress_display = Progress(
            TextColumn(f"[{style}]{{task.description}}"),
            BarColumn(complete_style=style, finished_style=style),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=local_console,
            transient=False,
        )
        self.task_id: Optional[TaskID] = None

    def __enter__(self) -> "_Progress":
        if self.visible:
            self.progress_display.start()
            self.task_id = self.progress_display.add_task(
                self.message, total=self.total
            )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> Optional[bool]:
        if not self.visible:
            return False

        try:
            if exc_type is KeyboardInterrupt:
                self.finish("Execution aborted by user", level=LogLevel.ERROR)
                return True
            elif exc_type is not None:
                self.finish(str(exc_val), level=LogLevel.ERROR)
                return True
            else:
                if self.task_id is not None:
                    self.finish()
        finally:
            if self.progress_display.live.is_started:
                self.progress_display.stop()
        return None

    def update(
        self,
        advance: int = 0,
        completed: Optional[int] = None,
        description: Optional[str] = None,
    ) -> None:
        """Updates the progress bar state."""
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
        """Marks the progress bar as finished and update its style."""
        if not self.visible or self.task_id is None:
            return

        f_message = message if message is not None else self.message
        f_level = level if level else self.level
        style = self.logger.STYLES[f_level]

        for column in self.progress_display.columns:
            if isinstance(column, BarColumn):
                column.complete_style = style
                column.finished_style = style
            elif type(column) is TextColumn:
                column.text_format = "{task.description}"
            elif hasattr(column, "style"):
                column.style = style

        final_theme = Theme({"progress.remaining": style, "progress.percentage": style})
        self.progress_display.console.push_theme(final_theme)

        update_kwargs = {"description": f"[{style}]{f_message}[/]", "refresh": True}

        if f_level == LogLevel.ERROR:
            self.progress_display.update(self.task_id, **update_kwargs)

            self.progress_display.live.transient = True
            if self.progress_display.live.is_started:
                self.progress_display.stop()

            err_console = Console(
                theme=final_theme,
                file=self.logger.error_console.file,
                force_terminal=self.logger.error_console.is_terminal,
                highlight=False,
            )

            renderable = self.progress_display.make_tasks_table(
                self.progress_display.tasks
            )
            err_console.print(renderable)
        else:
            update_kwargs["completed"] = self.total
            self.progress_display.update(self.task_id, **update_kwargs)

            if self.progress_display.live.is_started:
                self.progress_display.stop()

        self.task_id = None

    def _sub_log(self, level: LogLevel, message: str) -> None:
        """Prints a log line above the active progress bar."""
        if self.logger._should_log(level):
            style = self.logger.STYLES[level]
            self.progress_display.console.print(f"  {message}", style=style)

    def info(self, m: str) -> None:
        """Prints an info line above the active progress bar."""
        self._sub_log(LogLevel.INFO, m)

    def success(self, m: str) -> None:
        """Prints a success line above the active progress bar."""
        self._sub_log(LogLevel.SUCCESS, m)

    def warn(self, m: str) -> None:
        """Prints a warning line above the active progress bar."""
        self._sub_log(LogLevel.WARN, m)

    def error(self, m: str) -> None:
        """Prints an error line above the active progress bar."""
        self._sub_log(LogLevel.ERROR, m)

    def debug(self, m: str) -> None:
        """Prints a debug line above the active progress bar."""
        self._sub_log(LogLevel.DEBUG, m)
