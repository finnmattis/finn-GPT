import React, { useState, useRef } from 'react';
import ChatBox from './ChatBox';
import "./App.css";
import Textbox from './Textbox';
import Background from "./Background"

const App = () => {
  const [text, setText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const abortControllerRef = useRef(null);

  const fetchStream = async (input) => {
    setIsLoading(true);
    setText(input);
    setError(null);

    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch(`http://127.0.0.1:5000/?context=${encodeURIComponent(input)}`, {
        signal: abortControllerRef.current.signal
      });
      
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
      if (err.name !== 'AbortError') {
        setError(`Uh Oh. Failed to fetch response from server`);
      }
      setIsLoading(false);
    }
  };

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsLoading(false);
    }
  };

  const onButton = (input) => {
    if (isLoading) {
      handleStop();
    } else {
      fetchStream(input);
    }
  };

  // return (
  //   <div className="app-container">
  //     <div className="content-area">
  //       {!error && <div className="text-wrapper"><p className="text-gen">{text}</p></div>}
  //       {error && <div className="text-wrapper"><p className="text-gen error">{error}</p></div>}
  //     </div>
  //     <ChatBox onButton={onButton} isLoading={isLoading} theme="standard"/>
  //   </div>
  // );
  // need error for space theme
  return (
    <div>
      <Background />
      <Textbox text={text}/>
      <ChatBox onButton={onButton} isLoading={isLoading} theme="space"/>
    </div>
  )
};

export default App;