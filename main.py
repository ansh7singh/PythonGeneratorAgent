import os
from dotenv import load_dotenv
from google import genai
import sys
from google.genai import types
from functions1.get_file_info import schema_get_files_info
from functions1.get_file_content import schema_get_file_content
from functions1.get_write_file_content import schema_write_file
from functions1.run_python_file import schema_run_python_file
from call_function import call_function
def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    system_prompt = """
        You are a helpful AI coding agent.

        When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

        - List files and directories
        - read content of the file
        - write to a file
        - run a python file with optional arguements
        

        All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
        """

    if len(sys.argv) < 2:
        print("I need a prompt")
        sys.exit()

    verbose_flag = False
    if len(sys.argv) == 3 and sys.argv[2] == "--verbose":
        verbose_flag = True

    prompt = sys.argv[1]
    messages = [
    types.Content(
        role="user",
        parts=[types.Part(text=prompt)]
    )
] 
    available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file
    ]
)
    config=types.GenerateContentConfig(
    tools=[available_functions], system_instruction=system_prompt
)
    

    response = client.models.generate_content(
        model="gemini-2.0-flash-001", contents=messages,config=config
    )
    if response is None or response.usage_metadata is None:
        print("Response is malformed")
        return
    if verbose_flag:
        print(f"user_prompt: {prompt}")
        print(f"prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"response tokens: {response.usage_metadata.candidates_token_count}")
    if response.function_calls:
        for function_call in response.function_calls:
            # Get the current working directory
            working_dir = os.getcwd()
            # Call the function with the function call object and working directory
            tool_response = call_function(function_call, working_dir, verbose=verbose_flag)
            # You might want to append the tool response to the messages for the next API call
            # messages.append(tool_response)
    else:
        print(response.text)

    
    

    

    # Make sure to print the file info for the calculator directory at the project root

if __name__ == "__main__":
    main()
