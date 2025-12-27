from .core import _PwnLogger
from .enums import LogLevel

logger = _PwnLogger()

__version__ = "0.1.0"
__author__ = "Eudaeon"
__all__ = ["logger", "LogLevel"]