from enum import IntEnum


class LogLevel(IntEnum):
    """Available logging levels for pwnlogger."""

    DEBUG = 10
    INFO = 20
    WARN = 30
    SUCCESS = 40
    ERROR = 50
