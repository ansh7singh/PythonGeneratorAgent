import os
from google.genai import types

def get_file_info(working_directory , directory="."):
    abs_working_dirct_path = os.path.abspath(working_directory)
    abs_dirct_path = os.path.abspath(os.path.join(working_directory,directory))
    if not abs_dirct_path.startswith(abs_working_dirct_path):
        return f"Error: {directory} is not a directory"
    final_response = ""
    files = os.listdir(abs_dirct_path)
    for file in files:
        file_path = os.path.join(abs_dirct_path,file)
        is_dir = os.path.isdir(file_path)
        size = os.path.getsize(file_path)
        final_response += f"- {file}: file_size={size}, is_dir = {is_dir}"
    return final_response

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)