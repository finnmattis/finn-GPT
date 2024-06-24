import React, { useState } from 'react';
import ChatBox from './ChatBox';
import "./App.css"

const App = () => {
  const [text, setText] = useState("");

  const handleSend = (input) => {
    console.log(input)
  };

  return (
    <div>
      <div className="text-wrapper">
      <p className="text-gen">
        {text}
      </p>
      </div>
      <ChatBox onSend={handleSend} />
    </div>
  );
};

export default App;