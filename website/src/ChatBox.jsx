import React, { useState } from 'react';
import "./ChatBox.css"

const ChatBox = ({ onSendMessage }) => {
  const [text, setText] = useState('');

  const handleSend = () => {
    if (text.trim()) {
      onSendMessage(text);
      setText('');
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
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Type a message..."
        />
        <button className="submit-button" onClick={handleSend} style={{backgroundColor: text.length === 0 ? '#676767' : 'white'}}>
            <img src="/send.png" alt="Send" className="send-icon" />
        </button>
        <p className='disclaimer-text'>FinnGPT can not make mistakes. Don't check important info.</p>
    </div>
</div>
  );
};

export default ChatBox;