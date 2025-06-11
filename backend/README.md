# Q&A Agent Backend

The backend component of the Q&A Agent is built with FastAPI and Langgraph. It provides an API for the frontend to interact with the Q&A agent.

## Architecture

The backend consists of two main components:

1. **FastAPI Server (backend/app.py)**: Handles HTTP requests from the frontend and passes them to the Langgraph agent.
2. **Langgraph Agent (backend/agent/graph.py)**: Processes questions, searches the web, and generates answers.

## Dependencies

The backend requires the following dependencies:

```
fastapi==0.104.1
uvicorn==0.23.2
langgraph>=0.0.25
openai==1.3.5
python-dotenv==1.0.0
pydantic==2.4.2
httpx==0.25.1
requests==2.31.0
langfuse==3.0.0
```

## Environment Variables

The backend requires the following environment variables:

- `OPENROUTER_API_KEY`: API key for OpenRouter (required)
- `SERPER_API_KEY`: API key for Serper.dev (required)
- `LANGFUSE_PUBLIC_KEY`: Public key for Langfuse (optional)
- `LANGFUSE_SECRET_KEY`: Secret key for Langfuse (optional)
- `LANGFUSE_HOST`: Host for Langfuse (defaults to Langfuse Cloud)

You can set these variables in a `.env` file in the backend directory. An example `.env` file is provided in `.env.example`.

## API Endpoints

### POST /api/chat

Send a question to the Q&A agent and receive an answer.

**Request:**
```json
{
  "message": "What is the capital of France?",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "response": "The capital of France is Paris.",
  "search_info": {
    "num_results": 2,
    "sources": [
      "https://en.wikipedia.org/wiki/Paris",
      "https://www.britannica.com/place/Paris"
    ]
  },
  "confidence": 0.95,
  "trace_id": null
}
```

### GET /

Check if the API is running.

**Response:**
```json
{
  "status": "ok",
  "message": "Q&A Agent API is running"
}
```

## Server Implementation

The FastAPI server is implemented in `app.py`. It defines the API endpoints and handles requests from the frontend.

Key components:

1. **Request and Response Models**: Defined using Pydantic for type validation.
2. **API Endpoints**: Defined using FastAPI decorators.
3. **CORS Middleware**: Configured to allow requests from any origin.
4. **Error Handling**: Implemented to catch and report errors.

Example of the chat endpoint:

```python
@observe(name="api_chat_request")
@app.post("/api/chat", response_model=AnswerResponse)
async def chat(request: QuestionRequest, fastapi_request: Request):
    """
    Chat endpoint to interact with the Q&A agent.
    """
    try:
        # Get the question from the request
        question = request.message
        
        # Get or create session ID
        session_id = request.session_id or str(uuid.uuid4())
        
        # Run the agent
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
        
        # Return the answer
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
```

## Running the Server

To run the server:

1. Make sure you have set up the environment variables in a `.env` file.
2. Activate your virtual environment (if you're using one).
3. Run the following command:

```bash
python app.py
```

This will start the server on `http://localhost:8000`.

## Monitoring with Langfuse

The backend includes optional integration with Langfuse for monitoring and tracing. To enable Langfuse:

1. Set the `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` environment variables in your `.env` file.
2.  set the `LANGFUSE_HOST` environment variable if you're not using Langfuse Cloud.

The backend uses the `@observe` decorator from Langfuse to trace the execution of the agent and API endpoints.

## Next Steps

For more information about the Langgraph agent implementation, see the [Agent Documentation](agent/README.md).

For more information about frontend to backend integration, see the [Frontend Documentation](../frontend/README.md)
