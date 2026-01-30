from typing import TYPE_CHECKING, ClassVar, Dict, Optional, Tuple
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
from .mixins import LoggableMixin

if TYPE_CHECKING:
    from .core import _PwnLogger


class _Progress(LoggableMixin):
    """Manages a persistent progress bar."""

    _console_cache: ClassVar[Dict[Tuple[str, bool, int], Console]] = {}

    def __init__(
        self,
        logger: "_PwnLogger",
        message: str,
        total: int,
        level: LogLevel = LogLevel.INFO,
    ):
        self.logger = logger
        self.level = level
        self.visible = self.logger._should_log(self.level)
        self.message = message
        self.total = total
        self.task_id: Optional[TaskID] = None

        style = self.logger.styles.get(self.level, "")

        # Use cached console to avoid repeated instantiation
        cache_key = (
            style,
            self.logger.console.is_terminal,
            id(self.logger.console.file),
        )
        if cache_key in self._console_cache:
            local_console = self._console_cache[cache_key]
        else:
            local_theme = Theme(
                {"progress.remaining": style, "progress.percentage": style}
            )
            local_console = Console(
                theme=local_theme,
                highlight=False,
                force_terminal=self.logger.console.is_terminal,
                file=self.logger.console.file,
            )
            self._console_cache[cache_key] = local_console

        self.progress_display = Progress(
            TextColumn(f"[{style}]{{task.description}}"),
            BarColumn(complete_style=style, finished_style=style),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=local_console,
            transient=False,
        )

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
            elif exc_type is not None:
                self.finish(str(exc_val), level=LogLevel.ERROR)
            else:
                if self.task_id is not None:
                    self.finish()
        finally:
            self.stop()
        return False

    async def __aenter__(self) -> "_Progress":
        return self.__enter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> Optional[bool]:
        return self.__exit__(exc_type, exc_val, exc_tb)

    def stop(self) -> None:
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
        """Completes the progress bar and prints the final message."""
        if not self.visible or self.task_id is None:
            return

        f_message = message if message is not None else self.message
        f_level = level if level else self.level

        if f_level == LogLevel.ERROR:
            style = self.logger.styles.get(f_level, "")

            # Override theme to ensure all default columns (percentage, remaining) use the error style
            self.progress_display.console.push_theme(
                Theme({"progress.percentage": style, "progress.remaining": style})
            )

            # Update columns to use error style
            for column in self.progress_display.columns:
                if isinstance(column, BarColumn):
                    column.complete_style = style
                    column.finished_style = style

            self.progress_display.update(
                self.task_id,
                description=f"[{style}]{f_message}[/{style}]",
                refresh=True,
            )
            self.stop()
            self.task_id = None
            return

        self.progress_display.update(
            self.task_id, completed=self.total, refresh=True
        )

        self.stop()
        self.task_id = None

        # Log the final message independently to avoid tight coupling with Rich internals
        self.logger.log(f_level, f_message)
