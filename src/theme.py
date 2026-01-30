from .enums import LogLevel

DEFAULT_STYLES = {
    LogLevel.SUCCESS: "bold green",
    LogLevel.ERROR: "bold red",
    LogLevel.WARN: "bold yellow",
    LogLevel.INFO: "bold blue",
    LogLevel.DEBUG: "dim",
}
