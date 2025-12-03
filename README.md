# PwnLogger

A lightweight logging utility for debugging.

## Features

-   Color-coded output with symbols (`✔`, `✖`, `i`, `d`)
-   Support for success, error, info, and debug log levels
-   Animated progress spinners/bars with nested logging
-   Configurable log levels

## Installation

```bash
pip install git+https://github.com/Eudaeon/pwnlogger.git
```

## Usage

### Basic Logging

```python
from pwnlogger import logger

# Log messages
logger.success("Operation completed")
logger.error("An error occurred")
logger.info("Information message")
logger.debug("Debug information")
```

### Progress Spinners

You can use the `progress` context manager to display an animated spinner while performing long-running tasks. You can also log messages nested within the progress step.

```python
import time
from pwnlogger import logger

with logger.progress("Starting long task...") as progress:
    time.sleep(1)

    # Log nested messages without breaking the spinner
    progress.info("Processing step 1")

    # Update the status text next to the spinner
    progress.status("Moving to step 2...")
    time.sleep(1)

    # Finish with a custom success message
    progress.finish("Task 3 successfully!", level="success")
```

### Log Levels

You can set the minimum log level to control verbosity. The default level is `debug`.

```python
from pwnlogger import logger

# Hide debug messages
logger.set_level("info")
logger.debug("This will not be printed")
logger.info("This will be printed")
```
