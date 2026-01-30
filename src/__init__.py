from .core import _PwnLogger
from .enums import LogLevel

logger = _PwnLogger()

__all__ = ["logger", "LogLevel"]
