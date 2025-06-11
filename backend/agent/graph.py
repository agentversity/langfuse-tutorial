"""
Q&A Agent using Langgraph with internet search capabilities
"""
import os
import json
import requests
from typing import Dict, List, TypedDict, Any, Optional
from functools import wraps


from langgraph.graph import StateGraph, END

import openai
from openai import OpenAI

# Import Langfuse
from langfuse import observe, get_client
from langfuse import Langfuse

# Initialize Langfuse client
#langfuse = Langfuse()

def get_langfuse_client():
    """Get the Langfuse client if API keys are available."""
    try:
        # Check if Langfuse API keys are set
        if not os.getenv("LANGFUSE_PUBLIC_KEY") or not os.getenv("LANGFUSE_SECRET_KEY"):
            return None
        # Use the get_client function from langfuse
        return get_client()
    except Exception as e:
        print(f"Warning: Failed to initialize Langfuse client: {str(e)}")
        return None

# Create a decorator that only applies observe if Langfuse is available
#def observe_if_available(name=None, capture_input=None, capture_output=None):
#    def decorator(func):
#        @wraps(func)
#        def wrapper(*args, **kwargs):
#            # If Langfuse is not available, just call the function
#            if get_langfuse_client() is None:
#                return func(*args, **kwargs)
#            # Otherwise, use the observe decorator
#            return observe(name=name, capture_input=capture_input, capture_output=capture_output)(func)(*args, **kwargs)
#        return wrapper
#    return decorator

# Define the state schema (simplified)
class AgentState(TypedDict):
    """State for the Q&A agent."""
    question: str
    search_results: List[Dict[str, str]]
    answer: str
    confidence: float
    
# Initialize the OpenAI client
def get_openai_client():
    """Get the OpenAI client with Openrouter configuration."""
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY", ""),
        default_headers={
            "HTTP-Referer": "http://localhost:3000",  # Required for OpenRouter
            "X-Title": "Q&A Agent Demo"  # Optional, but helps OpenRouter understand your app
        }
    )
    return client

# Search the web
@observe(
    name="search_web"
)
def search_web(state: AgentState) -> AgentState:
    """Search the web using Serper.dev API."""
    query = state["question"]
    
    # Call Serper.dev API
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': os.getenv("SERPER_API_KEY", ""),
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, headers=headers, data=payload)
    search_results = response.json()
    
    # Extract and format relevant information
    formatted_results = []
    
    # Process organic results
    if "organic" in search_results:
        for result in search_results["organic"][:2]:  # Limit to top 3 results
            formatted_results.append({
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", "")
            })
    
    # Update state with search results
    state["search_results"] = formatted_results
    
    # Return the updated state
    return state

@observe(
    name="answer_question"
)
def answer_question(state: AgentState) -> AgentState:
    """Generate an answer using the question and search results."""
    client = get_openai_client()
    
    # Prepare search results context
    search_context = ""
    if state["search_results"]:
        search_context = "Here are some search results that might help:\n\n"
        for i, result in enumerate(state["search_results"], 1):
            search_context += f"{i}. {result['title']}\n"
            search_context += f"   Link: {result['link']}\n"
            search_context += f"   {result['snippet']}\n\n"
    
    # Prepare the prompt
    prompt = f"""
    You are a helpful Q&A assistant with access to real-time information. Answer the following question concisely and accurately:
    
    Question: {state["question"]}
    
    {search_context}
    
    Answer:
    """

    
    # Call the LLM
    response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[
            {"role": "system", "content": "You are a helpful Q&A assistant that provides accurate and concise answers based on the latest information available."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500
    )
    #system_prompt = "You are a helpful Q&A assistant that provides accurate and concise answers based on the latest information available."
    
    #langfuse.create_prompt(
    #    name = "answer_question",
    #    input = system_prompt + "\n\n" + prompt,
    #    output = response.choices[0].message.content,
    #    metadata = {
    #        "question": state["question"],
    #        "search_results": state["search_results"]
    #    },
    #    tags = ["initial"]
    #)
    # Extract the answer
    answer = response.choices[0].message.content
    
    # Set confidence to a high value since we're using search
    confidence = 0.95
    
    # Update the state with both answer and confidence
    state["answer"] = answer
    state["confidence"] = confidence
    
    # Return the updated state
    return state

# Create the graph for search-based answer
def create_agent():
    """Create and return a Q&A agent graph that uses search."""
    
    # Define the graph
    builder = StateGraph(AgentState)
    
    # Add nodes
    builder.add_node("search_web", search_web)
    builder.add_node("answer_question", answer_question)
    
    # Add edge for linear flow
    builder.add_edge("search_web", "answer_question")
    
    # Set the entry point
    builder.set_entry_point("search_web")
    
    # Set the exit point
    builder.add_edge("answer_question", END)
    
    # Compile the graph with callbacks
    graph = builder.compile()
    
    return graph

# Function to run the agent
@observe(name="run_agent")
def run_agent(question: str, trace_id: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Run the agent with a question and return the full result.
    
    Args:
        question: The question to answer
        trace_id: Optional trace ID for Langfuse tracing
        session_id: Optional session ID for Langfuse tracing
        
    Returns:
        The full result including the answer and metadata
    """
    # Create the agent
    agent = create_agent()
    
    # Initialize the state
    initial_state = {
        "question": question,
        "search_results": [],
        "answer": "",
        "confidence": 0.0
    }
    
    # Run the agent
    result = agent.invoke(initial_state)
    
    # Ensure all events are sent to Langfuse if it's available
    langfuse_client = get_langfuse_client()
    if langfuse_client is not None:
        langfuse_client.flush()
    
    # Return the full result
    return result
