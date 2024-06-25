import React, { useState } from 'react';

const App = () => {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchStream = async () => {
    setIsLoading(true);
    setResponse('');
    setError(null);

    try {
      const response = await fetch(`http://127.0.0.1:5000/?context=${encodeURIComponent(prompt)}`);
      
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
              setResponse(prev => prev + data);
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
    <div className="p-4">
      <input
        type="text"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Enter your prompt"
        className="w-full p-2 mb-4 border rounded"
      />
      <button
        onClick={fetchStream}
        disabled={isLoading || !prompt}
        className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
      >
        {isLoading ? 'Generating...' : 'Generate'}
      </button>
      {error && <p className="text-red-500 mt-4">{error}</p>}
      <div className="mt-4 p-2 border rounded">
        <h3 className="font-bold">Response:</h3>
        <p>{response}</p>
      </div>
    </div>
  );
};

export default App;