import inspect

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
            print(f"[INFO] Executing command function: {caller_function_name}")
        except IndexError:
            print("[INFO] Could not determine caller name (IndexError in inspect.stack).")
        except Exception as e:
            print(f"[ERROR] Error in PrintInfo while getting caller name: {e}")

if __name__ == '__main__':
    # Example usage:
    def example_function_one():
        pi = PrintInfo()
        pi.print_caller_name()

    def example_function_two():
        PrintInfo().print_caller_name()

    class MyClass:
        def my_method(self):
            PrintInfo().print_caller_name()

    example_function_one()
    example_function_two()

    instance = MyClass()
    instance.my_method()
