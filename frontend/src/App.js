import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [plan, setPlan] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [useAgenticMode, setUseAgenticMode] = useState(true);

  const sendMessage = async () => {
    if (!message.trim()) return;

    setIsLoading(true);
    try {
      const endpoint = useAgenticMode ? '/api/agent' : '/api/chat';
      const result = await axios.post(endpoint, { message });
      
      setResponse(result.data.response);
      if (result.data.plan) {
        setPlan(result.data.plan);
      }
    } catch (error) {
      setResponse('Error: ' + (error.response?.data?.error || error.message));
    }
    setIsLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🤖 Agentic AI App</h1>
        <p>Hackathon Project with Google Gemini Integration</p>
      </header>
      
      <main className="App-main">
        <div className="chat-container">
          <div className="mode-selector">
            <label>
              <input
                type="checkbox"
                checked={useAgenticMode}
                onChange={(e) => setUseAgenticMode(e.target.checked)}
              />
              Use Agentic Mode (Planning + Memory + Tools)
            </label>
          </div>

          <div className="input-section">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything... I'll plan, execute, and remember!"
              rows={3}
              disabled={isLoading}
            />
            <button onClick={sendMessage} disabled={isLoading || !message.trim()}>
              {isLoading ? 'Processing...' : 'Send'}
            </button>
          </div>

          {response && (
            <div className="response-section">
              <h3>🤖 Agent Response:</h3>
              <div className="response-text">{response}</div>
            </div>
          )}

          {plan && (
            <div className="plan-section">
              <h3>📋 Execution Plan:</h3>
              <div className="plan-list">
                {plan.map((task, index) => (
                  <div key={index} className="plan-item">
                    <strong>Task {index + 1}:</strong> {task.description}
                    <br />
                    <small>Tool: {task.tool} | Priority: {task.priority}</small>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>

      <footer className="App-footer">
        <p>Built for the Agentic AI Hackathon with 💚 and Google Gemini</p>
      </footer>
    </div>
  );
}

export default App;
