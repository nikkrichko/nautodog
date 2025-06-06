# Logging System

This document details the logging system implemented in the Nautodog project.

## Overview

The project utilizes a custom logging setup built around the [Loguru](https://loguru.readthedocs.io/en/stable/) library. A dedicated class, `CustomLogger`, located in `src/helper/custom_logger.py`, is responsible for configuring and managing the logging behavior across the application.

## Initialization

The logger is initialized at the very beginning of the application's execution in the main `nautodog.py` script. An instance of `CustomLogger` is created, which reads its configuration from the `config.yaml` file located in the root directory of the project.

```python
# In nautodog.py
from src.helper.custom_logger import CustomLogger
from loguru import logger # Import after CustomLogger initializes it

# Initialize the custom logger
custom_logger_instance = CustomLogger(config_path='config.yaml')
# This configures the global loguru.logger

logger.info("Nautodog application started.")
# Now logger is ready for use.
```

## Configuration (`config.yaml`)

The logging behavior is controlled by the `logging` section within the `config.yaml` file.

### Default Configuration

Here is the default structure of the logging configuration:

```yaml
logging:
  log_level: INFO
  log_file: nautodog.log
```

### Configuration Options

*   **`log_level`**:
    *   **Description**: Defines the minimum severity level for messages to be recorded.
    *   **Possible Values**:
        *   `TRACE`: Highly detailed diagnostic information, typically for intense debugging.
        *   `DEBUG`: Detailed information, typically of interest only when diagnosing problems.
        *   `INFO`: Confirmation that things are working as expected. (Default)
        *   `WARNING`: An indication that something unexpected happened, or indicative of some problem in the near future (e.g., ‘disk space low’). The software is still working as expected.
        *   `ERROR`: Due to a more serious problem, the software has not been able to perform some function.
        *   `CRITICAL`: A very serious error, indicating that the program itself may be unable to continue running.
    *   **Default**: `INFO`

*   **`log_file`**:
    *   **Description**: The path (relative to the project root or absolute) to the file where logs will be written.
    *   **Default**: `nautodog.log`

If `config.yaml` is not found or if the `logging` section or its keys are missing or malformed, the system will default to `log_level: INFO` and `log_file: nautodog.log`.

## Log Output Format

### File Output

Logs written to the `log_file` follow this format:

```
YYYY-MM-DD HH:mm:ss.SSS | {level} | {message}
```
Example:
```
2023-10-27 10:30:05.123 | INFO | This is an informational message.
```

### Console Output

Logs displayed on the console are colorized for better readability and include more detailed context:

**Format**:
`<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>`

**Colorization Scheme**:
*   `TRACE`: Cyan
*   `DEBUG`: Yellow
*   `INFO`: Green
*   `WARNING`: Magenta
*   `ERROR`: Red
*   `CRITICAL`: Red (similar to ERROR, but typically for more severe issues)

The level name in console output is padded to 8 characters for alignment (e.g., `INFO    `, `DEBUG   `).

## `@log_function_call` Decorator

The `CustomLogger` class provides a convenient decorator, `log_function_call`, to automatically log the calling of functions or methods.

### Importing the Decorator

The decorator itself is a method of the `CustomLogger` instance. However, for ease of use, if you are in a module where you don't have direct access to the `custom_logger_instance` created in `nautodog.py`, you would typically access it via the configured `loguru.logger` or, if you specifically need the decorator, you might need to pass the instance or re-instantiate CustomLogger (though the latter is not recommended for general logging).

For typical usage where `nautodog.py` has already initialized `CustomLogger`:
If you need the decorator instance, it's best to get it from the initialized `custom_logger_instance`.
Let's assume `custom_logger_instance` is made available globally or passed around. For simplicity in modules other than `nautodog.py`, if you need this specific decorator, you might consider how to access `custom_logger_instance`.
However, the decorator is part of the instance, so it's not directly importable like `from src.helper.custom_logger import log_function_call`. You would use it via an instance of `CustomLogger`.

If you have an instance, say `cl = CustomLogger()`:
```python
# Assuming 'cl' is an instance of CustomLogger
# from src.helper.custom_logger import CustomLogger
# cl = CustomLogger() # If you need to create a local instance (less common for this decorator)

@cl.log_function_call
def my_function():
    pass
```
Given the current structure, the `custom_logger` instance is in `nautodog.py`. To use its decorator in other modules, you'd ideally pass this instance or make it accessible. A simpler way for general function call logging without direct instance dependency is not available with the current `log_function_call` which is a method of `CustomLogger`.

Let's refine this: The prompt for `log_function_call` import might be slightly misleading. The decorator is a *method* of the `CustomLogger` instance. If `nautodog.py` creates `custom_logger = CustomLogger()`, then other modules would need access to this `custom_logger` instance to use its `log_function_call` method.

For the purpose of this documentation, let's assume `custom_logger` is the instance created in `nautodog.py`.

### Using the Decorator

```python
# In a module where 'custom_logger' instance from nautodog.py is accessible
# For example, if custom_logger was made a global or passed:
# from nautodog import custom_logger

# This is a conceptual example if custom_logger instance is accessible
# @custom_logger.log_function_call
# def my_function_with_default_log(param1, param2):
#     logger.info(f"Executing my_function_with_default_log with {param1}, {param2}")

# @custom_logger.log_function_call(info=False)
# def my_function_with_detailed_log(name, age=30):
#     logger.debug(f"Executing my_function_with_detailed_log with {name}, {age}")
```

**Correction for decorator usage based on current implementation:**
The decorator is part of the `CustomLogger` instance. If you create an instance of `CustomLogger`, you can use its decorator:

```python
from src.helper.custom_logger import CustomLogger
from loguru import logger # Ensure logger is imported after CustomLogger might have run

# Example: If you have a CustomLogger instance
my_local_logger_instance = CustomLogger() # This will also configure global logger

@my_local_logger_instance.log_function_call
def my_function_with_default_log(param1, param2):
    logger.info(f"Inside my_function_with_default_log: {param1}, {param2}")
    pass

@my_local_logger_instance.log_function_call(info=False)
def my_function_with_detailed_log(name, age=30, **kwargs):
    logger.debug(f"Inside my_function_with_detailed_log: {name}, {age}, {kwargs}")
    pass

my_function_with_default_log("test1", "test2")
my_function_with_detailed_log("Alice", age=31, city="Wonderland")
```

### Decorator Parameters

*   **`info`** (boolean):
    *   **`True`** (default): Logs a message at `INFO` level when the function is called. The message format is:
        `INFO: Calling function: <function_name>`
    *   **`False`**: Logs a message at `DEBUG` level, including the function's arguments and keyword arguments. The message format is:
        `DEBUG: Calling function: <function_name> with arguments: <args> and keyword arguments: <kwargs>`
        *(Note: Argument values are converted to their string representation and may be truncated if excessively long.)*

## Using the Logger Directly

Once `CustomLogger` is initialized in `nautodog.py`, the Loguru `logger` object is configured globally. You can import and use it in any module:

```python
from loguru import logger

def some_module_function():
    logger.info("This is an informational message from another module.")
    logger.debug("This is a debug message.")

    try:
        # Some operation that might fail
        x = 1 / 0
    except ZeroDivisionError:
        logger.error("An error occurred: Division by zero.")

some_module_function()
```

This allows for consistent logging throughout the application using the same configuration (file output, console output, levels, and format).
