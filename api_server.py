import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions1.get_file_info import schema_get_files_info
from functions1.get_file_content import schema_get_file_content
from functions1.get_write_file_content import schema_write_file
from functions1.run_python_file import schema_run_python_file
from call_function import call_function
from typing import List, Optional

load_dotenv()

app = FastAPI(title="AI Coding Agent API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini client
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

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

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file
    ]
)

config = types.GenerateContentConfig(
    tools=[available_functions], 
    system_instruction=system_prompt
)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = []


class FunctionCallInfo(BaseModel):
    name: str
    args: dict
    result: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    function_calls: List[FunctionCallInfo] = []
    usage_metadata: Optional[dict] = None


@app.get("/")
def read_root():
    return {"message": "AI Coding Agent API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Build messages from conversation history
        messages = []
        
        # Add conversation history
        for msg in request.conversation_history:
            messages.append(
                types.Content(
                    role=msg.role,
                    parts=[types.Part(text=msg.content)]
                )
            )
        
        # Add current user message
        messages.append(
            types.Content(
                role="user",
                parts=[types.Part(text=request.message)]
            )
        )
        
        # Generate response
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=messages,
            config=config
        )
        
        if response is None:
            raise HTTPException(status_code=500, detail="Failed to get response from AI")
        
        # Process function calls (handle multi-turn function calling)
        function_calls_info = []
        response_text = ""
        current_response = response
        max_iterations = 5  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            if current_response.function_calls:
                # Process all function calls
                for function_call in current_response.function_calls:
                    working_dir = os.getcwd()
                    tool_response = call_function(function_call, working_dir, verbose=False)
                    
                    # Store function call info
                    func_args = {}
                    if hasattr(function_call, 'args'):
                        func_args = function_call.args
                    elif hasattr(function_call, 'function_call') and hasattr(function_call.function_call, 'args'):
                        func_args = function_call.function_call.args
                    
                    func_info = FunctionCallInfo(
                        name=function_call.name if hasattr(function_call, 'name') else getattr(function_call.function_call, 'name', 'unknown'),
                        args=func_args,
                        result=None
                    )
                    
                    # Extract result from tool response
                    if tool_response and hasattr(tool_response, 'parts'):
                        for part in tool_response.parts:
                            if hasattr(part, 'function_response'):
                                func_resp = part.function_response
                                if isinstance(func_resp, dict):
                                    result = func_resp.get('result', '')
                                    if not result:
                                        result = func_resp.get('error', '')
                                else:
                                    result = str(func_resp) if func_resp else ''
                                if result:
                                    func_info.result = result
                    
                    function_calls_info.append(func_info)
                    
                    # Add tool response to messages for follow-up
                    messages.append(tool_response)
                
                # Get next response after function calls
                current_response = client.models.generate_content(
                    model="gemini-2.0-flash-001",
                    contents=messages,
                    config=config
                )
                
                if current_response is None:
                    response_text = "Function calls executed successfully, but no final response was generated."
                    break
                    
                # Continue loop if there are more function calls
                if current_response.function_calls:
                    continue
            else:
                # No more function calls, get the text response
                break
        
        # Extract the final response text
        if current_response and current_response.text:
            response_text = current_response.text
        elif function_calls_info:
            # If we had function calls but no text, provide a summary
            response_text = f"Executed {len(function_calls_info)} function call(s) successfully."
        else:
            response_text = "No response generated."
        
        # Extract usage metadata from the final response
        usage_metadata = None
        if current_response and current_response.usage_metadata:
            usage_metadata = {
                "prompt_token_count": current_response.usage_metadata.prompt_token_count,
                "candidates_token_count": current_response.usage_metadata.candidates_token_count,
                "total_token_count": current_response.usage_metadata.total_token_count
            }
        elif response.usage_metadata:
            # Fallback to initial response metadata
            usage_metadata = {
                "prompt_token_count": response.usage_metadata.prompt_token_count,
                "candidates_token_count": response.usage_metadata.candidates_token_count,
                "total_token_count": response.usage_metadata.total_token_count
            }
        
        return ChatResponse(
            response=response_text,
            function_calls=function_calls_info,
            usage_metadata=usage_metadata
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

