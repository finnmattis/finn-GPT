import React, { useState } from 'react';
import "./ChatBox.css";

const ChatBox = ({ onButton, isLoading }) => {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() || isLoading) {
      onButton(input);
    }
    if (!isLoading) {
      setInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  return (
    <div className="chatbox">
      <div className="input-wrapper">
        <input
          className="text-input"
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Continue writing..."
        />
        <button 
          className={`submit-button ${(!input.trim() && !isLoading) ? 'disabled' : ''}`} 
          onClick={handleSend}
          disabled={!input.trim() && !isLoading}
        >
          <img src={isLoading ? "/stop.png" : "/send.png"} alt={isLoading ? "Stop" : "Send"} className="send-icon" />
        </button>
      </div>
      <p className='disclaimer-text'>FinnGPT can not make mistakes. Don't bother verifying important information.</p>
    </div>
  );
};

export default ChatBox;