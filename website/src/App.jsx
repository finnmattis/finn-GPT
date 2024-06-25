import React, { useState } from 'react';
import ChatBox from './ChatBox';
import "./App.css"

const App = () => {
  const [text, setText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchStream = async (input) => {
    setIsLoading(true);
    setText(input);
    setError(null);

    try {
      const response = await fetch(`http://127.0.0.1:5000/?context=${encodeURIComponent(input)}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        lines.forEach(line => {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              setIsLoading(false);
            } else if (data === '[ERROR]') {
              setError('An error occurred during generation');
              setIsLoading(false);
            } else {
              setText(prev => prev + data);
            }
          }
        });
      }
    } catch (err) {
      setError(`Failed to fetch: ${err.message}`);
      setIsLoading(false);
    }
  };

  return (
    <div>
      {!error && <div className="text-wrapper"><p className="text-gen">{text}</p></div>}
      {error && <div className="text-wrapper"><p className="text-gen" style={{color: "red"}}>{error}</p></div>}
      <ChatBox onSend={fetchStream} />
    </div>
  );
};

export default App;