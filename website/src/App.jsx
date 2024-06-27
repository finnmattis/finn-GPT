import React, { useState, useRef } from "react";
import ChatBox from "./ChatBox";
import "./App.css";
import Textbox from "./Textbox";
import Background from "./Background";
import ThemeSwitcher from "./ThemeSwitcher";
import MagicText from "./MagicText";
import FireflyEffect from "./Firefly";
import Fog from "./Fog";

const App = () => {
  const [completions, setCompletions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [theme, setTheme] = useState(0);
  const abortControllerRef = useRef(null);

  const fetchStream = async (input) => {
    setIsLoading(true);
    setCompletions((prev) => [...prev, { type: "text", content: input }]);

    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch(
        `http://127.0.0.1:5000/?context=${encodeURIComponent(input)}`,
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
        if (done) {
          break;
        }

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        lines.forEach((line) => {
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            if (data === "[DONE]") {
              setIsLoading(false);
            } else if (data === "[ERROR]") {
              setCompletions((prev) => {
                const newCompletions = [...prev];
                newCompletions[newCompletions.length - 1].type = "error";
                newCompletions[newCompletions.length - 1].content =
                  "Uh Oh. Failed to fetch response from server.";
                return newCompletions;
              });
            } else {
              setCompletions((prev) => {
                const newCompletions = [...prev];
                const lastIndex = newCompletions.length - 1;

                let filteredData;
                if (data === "<newline>") {
                  filteredData = "\n";
                } else {
                  filteredData = data.replace(/[^\x20-\x7E\u2013]/g, "");
                }

                // hacky solution cause react weird
                if (!newCompletions[lastIndex].content.endsWith(filteredData)) {
                  newCompletions[lastIndex].content += filteredData;
                }

                return newCompletions;
              });
            }
          }
        });
      }
    } catch (err) {
      if (err.name !== "AbortError") {
        console.log(err);
        setCompletions((prev) => {
          const newCompletions = [...prev];
          newCompletions[newCompletions.length - 1].type = "error";
          newCompletions[newCompletions.length - 1].content =
            "Uh Oh. Failed to fetch response from server.";
          return newCompletions;
        });
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

  const renderCompletions = (theme_of_caller) => {
    if (theme_of_caller !== theme) return;
    console.log("hi");
    return completions.map((item, index) => {
      return (
        <div key={index} className="text-wrapper">
          <p className={`text-gen ${item.type === "error" && "error"}`}>
            {item.content}
          </p>
          {index != completions.length - 1 && (
            <div key={`separator-${index}`} className="separator">
              &nbsp;
            </div>
          )}
        </div>
      );
    });
  };

  return (
    <div className={`app-container}`}>
      <div
        className={`app-container-magic theme-transition ${
          theme === 2 ? "theme-visible" : "theme-hidden"
        }`}
      ></div>
      {/* Absolutes */}
      <ThemeSwitcher theme={theme} setTheme={setTheme} />
      <div className="absolute top-0 w-full mt-5 z-10 flex justify-center">
        <h1 className={`app-title ${theme === 2 ? "app-title-magic" : ""}`}>
          {theme === 0 ? "Use" : theme === 1 ? "Explore" : "Uncover"}{" "}
          {theme === 2 ? <MagicText /> : "finnGPT"}
        </h1>
      </div>
      {/* Normal (note: w-0 h-0 to prevent the content area from going below the textbox on space and magic*/}
      <div
        className={`${theme === 0 ? "theme-visible" : "theme-hidden w-0 h-0"}`}
      >
        <div className="content-area">{renderCompletions(0)}</div>
      </div>
      {/* Space */}
      <Background currentTheme={theme} />
      <div className={`${theme === 1 ? "theme-visible" : "theme-hidden"}`}>
        <Textbox text={renderCompletions(1)} theme={1} />
      </div>
      {/* Magic */}
      <div className={`${theme === 2 ? "theme-visible" : "theme-hidden"}`}>
        <Textbox text={renderCompletions(2)} theme={2} />
        <FireflyEffect />
        <Fog />
      </div>
      <ChatBox onButton={onButton} isLoading={isLoading} theme={theme} />
    </div>
  );
};

export default App;
