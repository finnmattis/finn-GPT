import React, { useState } from 'react';
import ChatBox from './ChatBox';
import "./App.css"

const App = () => {
  const [text, setText] = useState("");

  async function query(data) {
    const response = await fetch(
      "https://qtg077olky1x1xzg.us-east-1.aws.endpoints.huggingface.cloud",
      {
        headers: { 
          "Accept" : "application/json",
          "Content-Type": "application/json" 
        },
        method: "POST",
        body: JSON.stringify(data),
      }
    );
    const result = await response.json();
    return result;
  }

  const handleSend = (input) => {
    setText(input);
    query({
        "inputs": input,
        "parameters": {}
      }).then((response) => {
        let gen = JSON.stringify(response)
        console.log(gen)
        setText(gen);
    });
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