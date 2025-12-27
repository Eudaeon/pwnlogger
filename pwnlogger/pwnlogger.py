import sys
from enum import IntEnum
from typing import Optional

from rich.console import Console
from rich.theme import Theme
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
)


class LogLevel(IntEnum):
    """Available logging levels for pwnlogger."""

    DEBUG = 10
    INFO = 20
    ERROR = 30
    SUCCESS = 40


class _PwnLogger:
    """Core logger class providing styled output and progress tracking."""

    STYLES = {
        LogLevel.SUCCESS: "bold green",
        LogLevel.ERROR: "bold red",
        LogLevel.INFO: "bold blue",
        LogLevel.DEBUG: "dim",
    }

    def __init__(self, level: LogLevel = LogLevel.DEBUG):
        self.console = Console(highlight=False)
        self.min_level = level

    def set_level(self, level: LogLevel) -> None:
        """Sets the minimum threshold for displayed logs."""
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

    def debug(self, message: str) -> None:
        self._print(LogLevel.DEBUG, message)

    def error(self, message: str) -> None:
        self._print(LogLevel.ERROR, message)

    def raw(self, message: str) -> None:
        self.console.print(message)

    def status(self, message: str, level: LogLevel = LogLevel.INFO):
        """Context manager for an animated spinner."""
        return self._Status(self, message, level)

    def progress(self, message: str, total: int = 100, level: LogLevel = LogLevel.INFO):
        """Context manager for a single-task progress bar."""
        return self._Progress(self, message, total, level)

    class _Status:
        """Handles single-line animated indicators."""

        def __init__(self, logger: "_PwnLogger", message: str, level: LogLevel):
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
            if self.visible:
                if exc_type:
                    if exc_type is KeyboardInterrupt:
                        self.finish("User aborted execution", level=LogLevel.ERROR)
                        sys.exit(1)
                    else:
                        self.finish(f"Exception: {exc_val}", level=LogLevel.ERROR)
                else:
                    self.finish(level=self.level)

                if self.progress_display.live.is_started:
                    self.progress_display.stop()

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
            """Updates current status text."""
            if self.visible and self.task_id is not None:
                self.message = message
                self.progress_display.update(self.task_id, description=message)

        def finish(
            self, message: Optional[str] = None, level: Optional[LogLevel] = None
        ) -> None:
            """Finishes the status and prints the final message."""
            if not self.visible or self.task_id is None:
                return

            f_message = message if message is not None else self.message
            f_level = level if level else self.level
            style = self.logger.STYLES.get(f_level, "")

            self.progress_display.stop()
            self.logger.console.print(f_message, style=style)
            self.task_id = None

    class _Progress:
        """Handles persistent progress bars."""

        def __init__(
            self, logger: "_PwnLogger", message: str, total: int, level: LogLevel
        ):
            self.logger = logger
            self.level = level
            self.visible = self.logger._should_log(self.level)
            style = self.logger.STYLES.get(self.level, "bold blue")

            local_theme = Theme(
                {"progress.remaining": style, "progress.percentage": style}
            )
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

            self.task_id = (
                self.progress_display.add_task(message, total=total)
                if self.visible
                else None
            )

        def __enter__(self):
            if self.visible:
                self.progress_display.start()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.visible:
                self.progress_display.stop()

        def update(
            self,
            advance: int = 0,
            completed: Optional[int] = None,
            description: Optional[str] = None,
        ) -> None:
            if self.visible and self.task_id is not None:
                self.progress_display.update(
                    self.task_id,
                    advance=advance,
                    completed=completed,
                    description=description,
                )

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


logger = _PwnLogger()
