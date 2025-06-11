# Q&A AI Agent with Internet Search

A Q&A AI agent built with Langgraph and React that can search the internet for real-time information. This application allows users to ask questions and receive answers from an AI assistant with access to the latest information from the web.

## Overview

This project consists of two main components:

1. **Backend**: A Python-based FastAPI server with a Langgraph agent that can search the web and generate answers.
2. **Frontend**: A React-based web interface for interacting with the Q&A agent.

The application allows users to ask questions through a simple chat interface. The backend processes these questions, searches the web for relevant information using the Serper.dev API, and generates answers using OpenAI via OpenRouter.

## Key Features

- **Internet Search**: Automatically searches the web for real-time information
- **AI-Powered Answers**: Generates concise, accurate answers based on search results
- **Performance Monitoring**: Optional integration with Langfuse for monitoring and tracing

## Project Structure

```
qa_agent/
├── backend/             # Python backend with Langgraph and FastAPI
│   ├── agent/           # Langgraph agent implementation
│   │   ├── __init__.py
│   │   └── graph.py     # Agent graph definition
│   ├── app.py           # FastAPI server
│   ├── .env.example     # Example environment variables
│   └── requirements.txt # Python dependencies
└── frontend/            # React frontend
    ├── public/
    ├── src/
    │   ├── App.js       # Main React component
    │   ├── App.css      # Styling
    │   └── ...
    └── package.json
```

## Prerequisites

- Python 3.9+
- Node.js 14+
- npm 6+
- OpenRouter API key (get one at https://openrouter.ai/)
- Serper.dev API key (get one at https://serper.dev/)
- Langfuse API keys (get them at https://langfuse.com/)

## Setup and Installation

### Backend

1. Navigate to the backend directory:
   ```
   cd qa_agent/backend
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file from the example:
   ```
   copy .env.example .env
   ```

6. Edit the `.env` file and add your OpenRouter API key and Serper.dev API key.

### Frontend

1. Navigate to the frontend directory:
   ```
   cd qa_agent/frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

## Running the Application

### Backend

1. Make sure your virtual environment is activated.

2. Start the FastAPI server:
   ```
   cd qa_agent/backend
   python app.py
   ```

   The backend will be available at http://localhost:8000.

### Frontend

1. Start the React development server:
   ```
   cd qa_agent/frontend
   npm start
   ```

   The frontend will be available at http://localhost:3000.

## Documentation

- [Backend Documentation](backend/README.md): Details about the FastAPI server and API endpoints
- [Agent Documentation](backend/agent/README.md): Information about the Langgraph agent implementation
- [Frontend Documentation](frontend/README.md): Details about the React frontend

## Usage

1. Open your browser and navigate to http://localhost:3000.
2. Type a question in the input field and press Enter or click the Send button.
3. The AI agent will process your question, search the web and provide an answer.
4. The answer will include links to the sources used to generate the response.

## Notes

- This is a demo application without memory but with internet search capabilities.
- The application uses OpenRouter to access various LLM providers.
- The application uses Serper.dev to search the internet for real-time information.
