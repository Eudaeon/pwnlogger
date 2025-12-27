# PwnLogger

A lightweight logging utility for debugging, built on `rich`.

## Installation

```bash
pip install git+https://github.com/Eudaeon/pwnlogger.git
```

## Usage

### Basic Logging

Import `logger` and `LogLevel` to set verbosity and print colored lines.

```python
from pwnlogger import logger, LogLevel

# Set the minimum threshold (default is DEBUG)
logger.set_level(LogLevel.INFO)

logger.success("Build completed in 4.2s")
logger.info("Connecting to database...")
logger.error("Connection failed: timeout")
logger.debug("Stack trace: ...") # Hidden because min_level is INFO
```

### Status Spinners

Use the `status` manager for tasks where the final duration is unknown. You can update the message and print indented logs within the block.

```python
import time
from pwnlogger import logger, LogLevel

with logger.status("Provisioning server...", level=LogLevel.INFO) as s:
    time.sleep(1)
    s.info("Instance 'web-01' created.")
    
    time.sleep(1)
    s.update("Configuring firewall rules...")
    s.info("Port 80/443 opened.")
    
    # Finish with a custom status message and log level
    time.sleep(1)
    s.finish("Infrastructure ready.", level=LogLevel.SUCCESS)
```

### Progress Bars

Use `progress` for iterative tasks with a known total. These bars persist on the screen after completion.

```python
import time
from pwnlogger import logger

files = ["data1.json", "data2.json", "config.yaml", "logs.txt"]

with logger.progress("Processing files...", total=len(files)) as p:
    for filename in files:
        # Update progress and description
        p.update(advance=1, description=f"Processing {filename}")
        
        # Log events without breaking the bar
        if filename.endswith(".yaml"):
            p.debug(f"Parsing YAML headers for {filename}")
            
        time.sleep(0.5)
```
