from google.genai import types
from functions1.get_file_info import get_file_info
from functions1.get_file_content import get_file_content
from functions1.get_write_file_content import write_file
from functions1.run_python_file import run_python_file

def call_function(function_call, working_directory, verbose=False):
    """
    Call the appropriate function based on the function call object.
    
    Args:
        function_call: The function call object containing name and args
        working_directory: The working directory for file operations
        verbose: Whether to print verbose output
    
    Returns:
        The result of the function call
    """
    if verbose:
        print(f"Calling function: {function_call.name}({function_call.args})")
    else:
        print(f" - Calling function: {function_call.name}")
    
    try:
        if function_call.name == "get_files_info":
            result = get_file_info(working_directory, **function_call.args)
        elif function_call.name == "get_file_content":
            result = get_file_content(working_directory, **function_call.args)
        elif function_call.name == "write_file":
            result = write_file(working_directory, **function_call.args)
        elif function_call.name == "run_python_file":
            result = run_python_file(working_directory, **function_call.args)
        else:
            return types.Content(
                role="tool",
                parts=[
                    types.Part.from_function_response(
                        name=function_call.name,
                        response={"error": f"Unknown function: {function_call.name}"},
                    )
                ],
            )
        
        # Return the result as a tool response
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call.name,
                    response={"result": str(result)},
                )
            ],
        )
    except Exception as e:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call.name,
                    response={"error": f"Error executing {function_call.name}: {str(e)}"},
                )
            ],
        )