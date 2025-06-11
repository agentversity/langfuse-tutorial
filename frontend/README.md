# Q&A Agent Frontend

The frontend component of the Q&A Agent is built with React. It provides a simple chat interface for interacting with the Q&A agent.

## Overview

The frontend is a single-page React application with a minimalist black and white design. It allows users to ask questions and displays the answers from the Q&A agent, including information about the search results used to generate the answers.

## Project Structure

```
frontend/
├── public/              # Public assets
├── src/                 # Source code
│   ├── App.js           # Main React component
│   ├── App.css          # Styling
│   ├── index.js         # Entry point
│   └── ...              # Other React files
└── package.json         # Dependencies and scripts
```

## Key Components

### App Component

The main component of the application is the `App` component in `App.js`. It handles:

- User input
- API requests to the backend
- Displaying messages
- Loading states

### Chat Interface

The chat interface consists of:

- A header with the application title
- A main area for displaying messages
- A footer with an input field and send button

### Message Display

Messages are displayed in a chat-like interface with:

- User messages aligned to the right
- Assistant messages aligned to the left
- System messages (like loading indicators) centered

For assistant messages that include search information, the sources are displayed as links below the message.

## API Integration

The frontend communicates with the backend using a simple fetch API. When a user submits a question:

1. The question is sent to the backend API
2. The backend processes the question and returns an answer
3. The frontend displays the answer to the user

Example of API integration:

```javascript
// Send request to backend
const response = await fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ message: input }),
});

// Process response
const data = await response.json();

// Display answer
const assistantMessage = { 
  role: 'assistant', 
  content: data.response,
  searchInfo: data.search_info
};
setMessages(prevMessages => [...prevMessages, assistantMessage]);
```

## Styling

The application uses a clean, minimalist black and white design defined in `App.css`. Key styling features include:

- CSS variables for consistent colors and spacing
- Responsive design that works on different screen sizes
- Different styling for user, assistant, and system messages
- Subtle animations for loading states

The design focuses on readability and usability, with clear visual distinction between different types of messages.

## User Experience

The user experience is designed to be simple and intuitive:

1. User enters a question in the input field
2. User clicks the send button or presses Enter
3. A loading indicator shows that the question is being processed
4. The answer appears in the chat interface
5. If the answer is based on search results, the sources are displayed as links

## Running the Frontend

To run the frontend:

1. Make sure you have Node.js and npm installed
2. Navigate to the frontend directory
3. Install dependencies with `npm install`
4. Start the development server with `npm start`
5. Open your browser to http://localhost:3000

## Building for Production

To build the frontend for production:

1. Navigate to the frontend directory
2. Run `npm run build`
3. The build files will be created in the `build` directory
4. These files can be served by any static file server

## Next Steps

For more information about the backend implementation, see the [Backend Documentation](../backend/README.md).
