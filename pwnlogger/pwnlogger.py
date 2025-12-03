import sys
import time
import threading
import itertools
from enum import IntEnum


class _PwnLogger:
    class Colors:
        RESET = "\033[0m"
        BOLD = "\033[1m"
        RED = "\033[91m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        BLUE = "\033[94m"
        PURPLE = "\033[95m"
        CYAN = "\033[96m"
        GRAY = "\033[90m"

    class LogLevel(IntEnum):
        DEBUG = 10
        INFO = 20
        ERROR = 30
        SUCCESS = 40

    STYLES = {
        LogLevel.SUCCESS: ("✔", Colors.GREEN),
        LogLevel.ERROR: ("✖", Colors.RED),
        LogLevel.INFO: ("i", Colors.BLUE),
        LogLevel.DEBUG: ("d", Colors.GRAY),
    }

    def __init__(self, level="debug"):
        self.min_level = self._normalize_level(level)

    def _normalize_level(self, level):
        if isinstance(level, self.LogLevel):
            return level
        try:
            return self.LogLevel[level.upper()]
        except (KeyError, AttributeError):
            return self.LogLevel.INFO

    def set_level(self, level):
        self.min_level = self._normalize_level(level)

    def _should_log(self, level):
        return level >= self.min_level

    def _format_line(self, level, message, indent=""):
        symbol, color = self.STYLES.get(level, ("?", self.Colors.RESET))
        return (
            f"{indent}{self.Colors.BOLD}{color}[{symbol}]{self.Colors.RESET} {message}"
        )

    def _print(self, level, message):
        if self._should_log(level):
            sys.stdout.write(self._format_line(level, message) + "\n")
            sys.stdout.flush()

    def success(self, message):
        self._print(self.LogLevel.SUCCESS, message)

    def info(self, message):
        self._print(self.LogLevel.INFO, message)

    def debug(self, message):
        self._print(self.LogLevel.DEBUG, message)

    def error(self, message):
        self._print(self.LogLevel.ERROR, message)

    def raw(self, message):
        sys.stdout.write(message + "\n")
        sys.stdout.flush()

    def progress(self, message, level="info"):
        enum_level = self._normalize_level(level)
        return self._Progress(self, message, enum_level)

    class _Progress:
        def __init__(self, logger, message, level):
            self.logger = logger
            self.message = message
            self.level = level
            _, self.anim_color = self.logger.STYLES.get(
                self.level, ("*", self.logger.Colors.BLUE)
            )
            self.spinner = itertools.cycle(
                ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            )
            self.visible = self.logger._should_log(self.level)
            self.stop_event = threading.Event()
            self.lock = threading.Lock()

            if self.visible:
                sys.stdout.write(
                    f"\r{self.anim_color}[{next(self.spinner)}]{self.logger.Colors.RESET} {self.message}\033[K"
                )
                sys.stdout.flush()
                self.thread = threading.Thread(target=self._animate, daemon=True)
                self.thread.start()

        def _draw(self):
            sys.stdout.write(
                f"\r{self.anim_color}[{next(self.spinner)}]{self.logger.Colors.RESET} {self.message}\033[K"
            )
            sys.stdout.flush()

        def _animate(self):
            while not self.stop_event.is_set():
                with self.lock:
                    self._draw()
                time.sleep(0.1)

        def _sub_print(self, level, message):
            if self.logger._should_log(level):
                with self.lock:
                    if self.visible:
                        sys.stdout.write("\r\033[K")

                    line = self.logger._format_line(level, message, indent="    ")
                    sys.stdout.write(f"{line}\n")

                    if self.visible:
                        self._draw()

        def info(self, message):
            self._sub_print(self.logger.LogLevel.INFO, message)

        def success(self, message):
            self._sub_print(self.logger.LogLevel.SUCCESS, message)

        def error(self, message):
            self._sub_print(self.logger.LogLevel.ERROR, message)

        def debug(self, message):
            self._sub_print(self.logger.LogLevel.DEBUG, message)

        def status(self, message):
            if self.visible:
                with self.lock:
                    self.message = message

        def finish(self, message, level=None):
            finish_level = self.logger._normalize_level(level) if level else self.level
            if self.visible:
                self.stop_event.set()
                self.thread.join()
                symbol, color = self.logger.STYLES.get(finish_level)
                with self.lock:
                    sys.stdout.write("\r\033[K")
                    sys.stdout.write(
                        f"{self.logger.Colors.BOLD}{color}[{symbol}]{self.logger.Colors.RESET} {message}\n"
                    )
                    sys.stdout.flush()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.visible and not self.stop_event.is_set():
                if exc_type:
                    if exc_type is KeyboardInterrupt:
                        self.finish("User aborted execution", level="error")
                        sys.exit(1)
                    else:
                        self.finish("Exception occurred", level="error")
                else:
                    self.finish("Done", level=self.level)


logger = _PwnLogger()
LogLevel = _PwnLogger.LogLevel
