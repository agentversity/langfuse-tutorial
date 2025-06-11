"""
FastAPI server for the Q&A Agent
"""
import os
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
from functools import wraps

from agent import run_agent as agent_run_agent
from langfuse import observe, get_client

# Load environment variables
load_dotenv()

# Check if API keys are set
if not os.getenv("OPENROUTER_API_KEY"):
    print("Warning: OPENROUTER_API_KEY environment variable not set")

# Create a decorator that only applies observe if Langfuse is available
#def observe_if_available(name=None):
#    def decorator(func):
#        @wraps(func)
#        async def wrapper(*args, **kwargs):
#            # If Langfuse is not available, just call the function
#            if not os.getenv("LANGFUSE_PUBLIC_KEY") or not os.getenv("LANGFUSE_SECRET_KEY"):
#                return await func(*args, **kwargs)
#            # Otherwise, use the observe decorator
#            return await observe(name=name)(func)(*args, **kwargs)
#        return wrapper
#    return decorator

# Create FastAPI app
app = FastAPI(title="Q&A Agent API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Define request and response models
class QuestionRequest(BaseModel):
    message: str
    session_id: Optional[str] = None  # Optional session ID for tracking conversations

class AnswerResponse(BaseModel):
    response: str
    search_info: Dict[str, Any] = None
    confidence: float = 0.0
    trace_id: Optional[str] = None  # Langfuse trace ID for debugging

@app.get("/")
async def root():
    """Root endpoint to check if the API is running."""
    return {"status": "ok", "message": "Q&A Agent API is running"}

@observe(name="api_chat_request")
@app.post("/api/chat", response_model=AnswerResponse)
async def chat(request: QuestionRequest, fastapi_request: Request):
    """
    Chat endpoint to interact with the Q&A agent.
    
    Args:
        request: The question request containing:
            - message: The user's question
            - session_id: Optional session ID for tracking conversations
        
    Returns:
        The answer response containing:
            - response: The agent's answer
            - search_info: Information about the search results
            - confidence: The confidence level of the answer
            - trace_id: Langfuse trace ID for debugging
    """
    try:
        # Get the question from the request
        question = request.message
        
        # Get or create session ID
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get client IP and user agent for tracing
        client_host = fastapi_request.client.host if fastapi_request.client else "unknown"
        user_agent = fastapi_request.headers.get("user-agent", "unknown")
        
        # No need to create explicit trace - using @observe decorator instead
        trace_id = None  # We'll still pass None to maintain compatibility
        
        # Run the agent using the imported function
        result = agent_run_agent(
            question, 
            trace_id=trace_id,
            session_id=session_id
        )
        
        # Prepare search info
        search_info = {
            "num_results": len(result["search_results"]),
            "sources": [item["link"] for item in result["search_results"] if "link" in item]
        }
        
        # Ensure all events are sent to Langfuse if it's available
        if os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
            langfuse_client = get_client()
            if langfuse_client is not None:
                langfuse_client.flush()
        
        # Return the answer with search information, confidence, and trace ID
        return AnswerResponse(
            response=result["answer"],
            search_info=search_info,
            confidence=result["confidence"],
            trace_id=trace_id
        )
    except Exception as e:
        # Log the error
        print(f"Error: {str(e)}")
        
        # Raise an HTTP exception
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
