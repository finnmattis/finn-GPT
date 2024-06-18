import React, { useState } from 'react';
import ChatBox from './ChatBox';
import "./App.css"

const App = () => {
  const [text, setText] = useState("");

  const handleSendMessage = (input) => {
    setText(text + input);
  };

  return (
    <div>
      <div className="text-wrapper">
      <p className="text-gen">
        {text}
      </p>
      </div>
      <ChatBox onSendMessage={handleSendMessage} />
    </div>
  );
};

export default App;