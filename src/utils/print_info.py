import inspect
from src.utils.logger import logger

class PrintInfo:
    """
    A utility class to print information about the calling function.
    """
    def print_caller_name(self):
        """
        Prints the name of the method/function that called this method.
        """
        try:
            # inspect.stack()[0] is the current frame (print_caller_name itself)
            # inspect.stack()[1] is the frame of the caller of print_caller_name
            caller_frame_record = inspect.stack()[1]
            caller_function_name = caller_frame_record.function
            logger.info(f"Executing command function: {caller_function_name}")
        except IndexError:
            logger.warning("Could not determine caller name (IndexError in inspect.stack).")
        except Exception as e:
            logger.error(f"Error in PrintInfo while getting caller name: {e}")
