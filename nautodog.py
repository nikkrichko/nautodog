import click
from loguru import logger
import sys
import functools # Import functools

# --- Command Group Imports ---
from src.ddsnmpconfig.commands import ddsnmpconfig
from src.ddmonitor.commands import ddmonitor
from src.ddmainconfig.commands import ddmainconfig
from src.ddagent.commands import ddagent
from src.report.commands import report

# --- Loguru Configuration ---
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# --- Logging Decorator ---
def log_command(func):
    """
    A decorator to log command execution with its arguments using Loguru.
    To be applied to Click command functions.
    """
    @functools.wraps(func) # Use functools.wraps to preserve func metadata
    def wrapper(*args, **kwargs):
        ctx = click.get_current_context(silent=True)
        command_path = "N/A"
        params_str = "N/A"

        if ctx:
            command_path = ctx.command_path
            # Filter out context from kwargs if it's there, as it's not a user parameter
            params_to_log = {k: v for k, v in ctx.params.items()}
            params_str = ", ".join(f"{k}='{v}'" for k, v in params_to_log.items())
        else:
            # Fallback if context is not available (e.g. during testing or direct invocation)
            # This part might need adjustment based on how commands are invoked outside CLI
            func_args = list(args)
            # If 'self' or 'cls' is an argument, it would be in func_args.
            # We assume typical Click command usage where options are in kwargs.
            params_str = ", ".join(f"{k}='{v}'" for k, v in kwargs.items())


        logger.info(f"Executing command: '{command_path}' with parameters: {{ {params_str} }}")
        try:
            # Call the original command function
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error during command '{command_path}': {e}")
            # It's often better to let Click handle the display of the error for CLI consistency
            raise
    return wrapper

# --- Main CLI Application ---
@click.group()
def cli():
    """
    Nautodog CLI application.
    Use --help with any command or group for more details.
    """
    logger.info("Nautodog CLI application initialized.")
    pass

# Add command groups
cli.add_command(ddsnmpconfig)
cli.add_command(ddmonitor)
cli.add_command(ddmainconfig)
cli.add_command(ddagent)
cli.add_command(report)

if __name__ == '__main__':
    cli()
