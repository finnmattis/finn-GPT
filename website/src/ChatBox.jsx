import React, { useState } from 'react';
import "./ChatBox.css";

const ChatBox = ({ onButton, isLoading, theme = "standard" }) => {
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

  const isSpaceTheme = theme === "space";
  const chatboxClass = isSpaceTheme ? "chatbox chatbox-space" : "chatbox";
  const inputClass = isSpaceTheme ? "text-input text-input-space" : "text-input";
  const buttonClass = `submit-button ${(!input.trim() && !isLoading) ? 'disabled' : ''} ${isSpaceTheme ? 'submit-button-space' : ''}`;

  return (
    <div className={chatboxClass}>
      <div className="input-wrapper">
        <input
          className={inputClass}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Continue writing..."
        />
        <button 
          className={buttonClass}
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