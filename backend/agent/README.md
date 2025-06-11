# Q&A Agent Implementation

This directory contains the implementation of the Q&A agent using Langgraph. The agent is designed to answer questions by searching the web and generating answers based on the search results.

## Overview

The Q&A agent is implemented as a Langgraph state graph with two main nodes:

1. **Search Web**: Searches the web using the Serper.dev API to find relevant information.
2. **Answer Question**: Generates an answer using the search results and the OpenAI API via OpenRouter.

## Agent State

The agent state contains the following key information:

- `question`: The user's question
- `search_results`: The results from the web search
- `answer`: The generated answer
- `confidence`: The confidence level of the answer

## Agent Workflow

The agent follows a simple linear workflow:

1. The agent receives a question from the user.
2. The `search_web` node searches the web using the Serper.dev API.
3. The `answer_question` node generates an answer using the search results and the OpenAI API.
4. The agent returns the answer to the user.

## Web Search Implementation

The `search_web` node is responsible for searching the web using the Serper.dev API. It takes the user's question, sends a request to the Serper.dev API, and extracts the relevant information from the response.

Key aspects of the implementation:

- Uses the Serper.dev API to search Google
- Extracts the title, link, and snippet from the search results
- Limits the results to the top 2 organic results
- Updates the agent state with the search results

## Answer Generation

The `answer_question` node is responsible for generating an answer using the search results and the OpenAI API via OpenRouter. It takes the search results, formats them into a prompt, and sends a request to the OpenAI API.

Key aspects of the implementation:

- Uses the OpenAI API via OpenRouter
- Formats the search results into a prompt
- Sets a high confidence level since we're using search
- Updates the agent state with the answer and confidence

## Agent Creation and Monitoring

The agent is created using Langgraph's StateGraph. The graph is defined with two nodes (`search_web` and `answer_question`) and a linear flow between them. Langfuse is used for monitoring and tracing.

Here's a small snippet showing how the agent is created and how monitoring is implemented:

```python
# Import Langfuse
from langfuse import observe, get_client

# Monitoring with Langfuse
@observe(name="search_web")
def search_web(state: AgentState) -> AgentState:
    """Search the web using Serper.dev API."""
    # Implementation details...
    return state

@observe(name="answer_question")
def answer_question(state: AgentState) -> AgentState:
    """Generate an answer using the question and search results."""
    # Implementation details...
    return state

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
    
    # Compile the graph
    graph = builder.compile()
    
    return graph

# Running the agent with monitoring
@observe(name="run_agent")
def run_agent(question: str, trace_id: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
    """Run the agent with a question and return the full result."""
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
```

The `@observe` decorator from Langfuse is used to trace the execution of:
- The `search_web` function
- The `answer_question` function
- The `run_agent` function

This allows for comprehensive monitoring of the agent's performance, including:
- Tracking execution time
- Monitoring input and output data
- Identifying bottlenecks
- Debugging issues in the agent workflow

## Next Steps

For more information about the FastAPI server implementation, see the [Backend Documentation](../README.md).
