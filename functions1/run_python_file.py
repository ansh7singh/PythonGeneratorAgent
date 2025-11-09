import os
import subprocess
from google.genai import types

def run_python_file(working_directory:str , file_path:str,args=[]):
    abs_working_dirct_path = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))
    
    if not abs_file_path.startswith(abs_working_dirct_path):
        return f"Error: {file_path} is not inside {working_directory}"
    
    if not os.path.exists(abs_file_path):
        parent_dir = os.path.dirname(abs_file_path)
        try:
            os.makedirs(parent_dir, exist_ok=True)
        except Exception as e:
            return f"Could not create directory {parent_dir}: {e}"
    if not file_path.endswith(".py"):
        return f"file with path{file_path} is not a python file."
    final_args = ["python3", file_path]
    final_args.extend(args)
    output =  subprocess.run(final_args,cwd=working_directory,timeout=30,capture_output=True)
    final_return_string =  f"""
STDOUT:{output.stdout}
STDERR:{output.stderr}

"""    
   
    if output.stdout == "" and output.stderr == "":
           return f"process returned with no response error:{output.stderr} , output:{output.stdout}"
    if output.returncode != 0:
           final_return_string += f"process existed with error code{output.returncode}"
    return final_return_string

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python script with the given arguments and returns its output and errors.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file to execute, relative to the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="Command line arguments to pass to the Python script.",
                default=[],
            ),
        },
        required=["file_path"],
    ),
)
    
