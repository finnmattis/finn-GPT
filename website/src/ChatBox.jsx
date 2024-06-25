import React, { useState } from 'react';
import "./ChatBox.css"

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
            placeholder="Type a message..."
        />
        <button className="submit-button" onClick={handleSend} style={{backgroundColor: input.length === 0 && !isLoading ? '#676767' : 'white'}}>
            <img src="/send.png" alt="Send" className="send-icon" />
        </button>
        <p className='disclaimer-text'>FinnGPT can not make mistakes. Don't check important info.</p>
    </div>
</div>
  );
};

export default ChatBox;