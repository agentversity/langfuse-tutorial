import React, { useState } from 'react';
import './App.css';

function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!input.trim()) return;
    
    // Add user message to chat
    const userMessage = { role: 'user', content: input };
    setMessages([...messages, userMessage]);
    
    // Clear input field
    setInput('');
    
    // Set loading state
    setIsLoading(true);
    
    // Add a temporary "thinking" message
    const thinkingMessage = { role: 'system', content: 'Thinking...' };
    setMessages(prevMessages => [...prevMessages, thinkingMessage]);
    
    try {
      // Send request to backend
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: input }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to get response from server');
      }
      
      const data = await response.json();
      
      // Remove the thinking message
      setMessages(prevMessages => prevMessages.filter(msg => msg.content !== 'Thinking...'));
      
      // Add assistant message to chat
      const assistantMessage = { 
        role: 'assistant', 
        content: data.response,
        searchInfo: data.search_info
      };
      setMessages(prevMessages => [...prevMessages, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
      
      // Remove the thinking message
      setMessages(prevMessages => prevMessages.filter(msg => msg.content !== 'Thinking...'));
      
      // Add error message to chat
      const errorMessage = { 
        role: 'system', 
        content: 'Sorry, there was an error processing your request. Please try again.' 
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      // Reset loading state
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Q&A Agent</h1>
      </header>
      
      <main className="App-main">
        <div className="chat-container">
          {messages.length === 0 ? (
            <div className="empty-state">
              <p>Ask a question to get started</p>
            </div>
          ) : (
            <div className="messages">
              {messages.map((message, index) => (
                <div key={index} className={`message ${message.role}`}>
                  <div className="message-content">
                    {message.content}
                    {message.searchInfo && (
                      <div className="search-indicator">
                        <small>Answer based on {message.searchInfo.num_results} search results</small>
                        {message.searchInfo.sources && message.searchInfo.sources.length > 0 && (
                          <div className="sources">
                            <small>Sources:</small>
                            <ul>
                              {message.searchInfo.sources.map((source, i) => (
                                <li key={i}>
                                  <a href={source} target="_blank" rel="noopener noreferrer">
                                    {source}
                                  </a>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
      
      <footer className="App-footer">
        <form onSubmit={handleSubmit} className="input-form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            disabled={isLoading}
            className="input-field"
          />
          <button 
            type="submit" 
            disabled={isLoading || !input.trim()} 
            className="submit-button"
          >
            {isLoading ? 'Processing...' : 'Send'}
          </button>
        </form>
      </footer>
    </div>
  );
}

export default App;
