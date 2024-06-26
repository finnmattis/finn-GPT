import React, { useState, useRef } from "react";
import ChatBox from "./ChatBox";
import "./App.css";
import Textbox from "./Textbox";
import Background from "./Background";
import ThemeSwitcher from "./ThemeSwitcher";
import MagicText from "./MagicText";

const App = () => {
  const [text, setText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [theme, setTheme] = useState(0);
  const abortControllerRef = useRef(null);

  const fetchStream = async (input) => {
    setIsLoading(true);
    setText(input);
    setError(null);

    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch(
        `https://finn-gpt-enoprmj2xa-uc.a.run.app//?context=${encodeURIComponent(
          input
        )}`,
        {
          signal: abortControllerRef.current.signal,
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        lines.forEach((line) => {
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            if (data === "[DONE]") {
              setIsLoading(false);
            } else if (data === "[ERROR]") {
              setError("An error occurred during generation");
              setIsLoading(false);
            } else {
              setText((prev) => prev + data);
            }
          }
        });
      }
    } catch (err) {
      if (err.name !== "AbortError") {
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

  return (
    <div
      className={`app-container ${theme === 2 ? "app-container-magic" : ""}`}
    >
      <ThemeSwitcher theme={theme} setTheme={setTheme} />
      <div className="absolute top-0 w-full mt-5 z-10 flex justify-center">
        <h1 className={`app-title ${theme === 2 ? "app-title-magic" : ""}`}>
          {theme === 0 ? "Use" : theme === 1 ? "Explore" : "Uncover"}{" "}
          {theme === 2 ? <MagicText /> : "finnGPT"}
        </h1>
      </div>
      {theme === 0 ? (
        <>
          <div className="content-area">
            {!error && (
              <div className="text-wrapper">
                <p className="text-gen">{text}</p>
              </div>
            )}
            {error && (
              <div className="text-wrapper">
                <p className="text-gen error">{error}</p>
              </div>
            )}
          </div>
        </>
      ) : theme === 1 ? (
        <>
          <Background />
          <Textbox text={text} theme={1} />
        </>
      ) : (
        <>
          <Textbox text={text} theme={2} />
        </>
      )}
      <ChatBox onButton={onButton} isLoading={isLoading} theme={theme} />
    </div>
  );
};

export default App;
