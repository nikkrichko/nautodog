import functools
import yaml
from loguru import logger

class CustomLogger:
    def __init__(self, config_path='config.yaml'):
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found at {config_path}. Using default logging settings.")
            config = {}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file {config_path}: {e}. Using default logging settings.")
            config = {}

        logging_config = config.get('logging', {})
        log_level = logging_config.get('log_level', 'INFO')
        log_file = logging_config.get('log_file', 'nautodog.log')

        logger.remove()  # Remove default handler
        logger.add(
            log_file,
            level=log_level.upper(),
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}",
            colorize=False  # Colorize is for console, not file
        )

        # Adding console logger with colorization
        logger.add(
            lambda msg: print(msg, end=''), # Use a lambda to print directly to console
            level=log_level.upper(),
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            colorize=True,
            enqueue=True # Important for thread-safety if used in multi-threaded apps
        )

        logger.level("INFO", color="<green>")
        logger.level("DEBUG", color="<yellow>") # Changed to yellow for better visibility than orange
        logger.level("TRACE", color="<cyan>") # Changed to cyan for better visibility than orange
        logger.level("ERROR", color="<red>")
        logger.level("WARNING", color="<magenta>") # Added warning level color

    def log_function_call(self, info=True):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if info:
                    logger.info(f"Calling function: {func.__name__}")
                else:
                    # Be careful with logging sensitive data in args/kwargs
                    # For simplicity, logging them as is. Consider filtering or summarizing in production.
                    args_repr = [repr(a) for a in args]
                    kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                    # Limiting the length of logged arguments to avoid excessively long log messages
                    max_arg_length = 100
                    logged_args = []
                    for arg_str in args_repr:
                        if len(arg_str) > max_arg_length:
                            logged_args.append(arg_str[:max_arg_length] + "...")
                        else:
                            logged_args.append(arg_str)

                    logged_kwargs = []
                    for kwarg_str in kwargs_repr:
                        if len(kwarg_str) > max_arg_length:
                            logged_kwargs.append(kwarg_str[:max_arg_length] + "...")
                        else:
                            logged_kwargs.append(kwarg_str)

                    details = f"with arguments: {', '.join(logged_args)}" if logged_args else ""
                    if logged_kwargs:
                        details += f"{' and ' if details else 'with '}keyword arguments: {', '.join(logged_kwargs)}"

                    if not details: # If no args or kwargs
                        logger.debug(f"Calling function: {func.__name__}")
                    else:
                         logger.debug(f"Calling function: {func.__name__} {details}")
                return func(*args, **kwargs)
            return wrapper
        return decorator

# Example usage (optional, can be removed or kept for testing)
if __name__ == '__main__':
    # Create a dummy config.yaml for testing if it doesn't exist
    try:
        with open('config.yaml', 'r') as f:
            pass
    except FileNotFoundError:
        with open('config.yaml', 'w') as f:
            yaml.dump({'logging': {'log_level': 'DEBUG', 'log_file': 'test_app.log'}}, f)

    custom_logger = CustomLogger(config_path='config.yaml')

    @custom_logger.log_function_call(info=True)
    def example_function_info(message):
        logger.info(f"Inside example_function_info: {message}")

    @custom_logger.log_function_call(info=False)
    def example_function_debug(a, b, c="default"):
        logger.debug(f"Inside example_function_debug with a={a}, b={b}, c={c}")
        return a + b

    example_function_info("Hello from info logger!")
    example_function_debug(1, 2, c="test")
    example_function_debug(1,2, c="This is a very long string that should be truncated if it exceeds the max_arg_length which is currently set to 100 characters in the logger configuration to prevent overly verbose log messages.")

    # Test with no args/kwargs
    @custom_logger.log_function_call(info=False)
    def no_args_kwargs_func():
        logger.debug("Inside no_args_kwargs_func")

    no_args_kwargs_func()

    logger.trace("This is a TRACE message.")
    logger.debug("This is a DEBUG message.")
    logger.info("This is an INFO message.")
    logger.warning("This is a WARNING message.")
    logger.error("This is an ERROR message.")

    # Test config file not found
    # custom_logger_no_config = CustomLogger(config_path='non_existent_config.yaml')
    # @custom_logger_no_config.log_function_call()
    # def test_no_config_func():
    #    logger.info("Testing with no config file")
    # test_no_config_func()

    # Test malformed config file
    # with open('malformed_config.yaml', 'w') as f:
    #    f.write("logging: {log_level: INFO, log_file: 'app.log'") # Malformed YAML
    # custom_logger_malformed_config = CustomLogger(config_path='malformed_config.yaml')
    # @custom_logger_malformed_config.log_function_call()
    # def test_malformed_config_func():
    #    logger.info("Testing with malformed config file")
    # test_malformed_config_func()
