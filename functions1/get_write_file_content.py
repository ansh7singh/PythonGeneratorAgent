import os
from google.genai import types

def write_file(working_directory, file_path, content):
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
    
    try:
        with open(abs_file_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        return f"Could not write to file: {file_path}, {e}"
    
    # ✅ Return a success message
    return f'Success: wrote {len(content)} characters to "{abs_file_path}"'

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a file, creating the file and any necessary directories if they don't exist.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to write to, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file.",
            ),
        },
        required=["file_path", "content"],
    ),
)
