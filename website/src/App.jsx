import { useState, useRef, useEffect } from "react";
import ChatBox from "./ChatBox";
import "./App.css";
import Textbox from "./Textbox";
import Background from "./Background";
import Switcher from "./Switcher";
import MagicText from "./MagicText";
import FireflyEffect from "./Firefly";
import Fog from "./Fog";
import Messages from "./Messages";

const App = () => {
  const [mode, setMode] = useState(0);
  const [conv, setConv] = useState("");
  const [completions, setCompletions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [theme, setTheme] = useState(0);
  const abortControllerRef = useRef(null);

  const fetchStream = async (input) => {
    setIsLoading(true);
    if (mode === 0) {
      input = "<|user|>" + input + "<|assistant|>";
      setConv((prev) => prev + input);
    } else {
      setCompletions((prev) => [...prev, { type: "text", content: input }]);
    }

    abortControllerRef.current = new AbortController();

    try {
      const url = new URL("http://127.0.0.1:5000/");
      url.searchParams.append("context", input);
      url.searchParams.append("isChat", mode === 0);

      const response = await fetch(url.toString(), {
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let isDone = false;
      while (!isDone) {
        const { done, value } = await reader.read();
        if (done) {
          isDone = true;
          continue;
        }

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        lines.forEach((line) => {
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            if (data === "[DONE]") {
              setIsLoading(false);
            } else if (data === "[ERROR]") {
              if (mode === 0) {
                setConv(
                  (prev) =>
                    (prev +=
                      "<|error|>" +
                      "Uh Oh. Failed to fetch response from server.")
                );
              } else {
                setCompletions((prev) => {
                  const newCompletions = [...prev];
                  newCompletions[newCompletions.length - 1].type = "error";
                  newCompletions[newCompletions.length - 1].content =
                    "Uh Oh. Failed to fetch response from server.";
                  return newCompletions;
                });
              }
            } else {
              let filteredData;
              if (data === "<newline>") {
                filteredData = "\n";
              } else {
                filteredData = data.replace(/[^\x20-\x7E\u2013]/g, "");
              }
              if (mode === 0) {
                setConv((prev) => {
                  if (prev.endsWith("<|user|")) {
                    return prev.slice(0, -8);
                  }
                  return prev + filteredData;
                });
              } else {
                setCompletions((prev) => {
                  const newCompletions = [...prev];
                  const lastIndex = newCompletions.length - 1;

                  // hacky solution cause react weird
                  if (
                    !newCompletions[lastIndex].content.endsWith(filteredData)
                  ) {
                    newCompletions[lastIndex].content += filteredData;
                  }

                  return newCompletions;
                });
              }
            }
          }
        });
      }
    } catch (err) {
      if (err.name !== "AbortError") {
        console.log(err);
        if (mode === 0) {
          setConv(
            (prev) =>
              (prev +=
                "<|error|>" + "Uh Oh. Failed to fetch response from server.")
          );
        } else {
          setCompletions((prev) => {
            const newCompletions = [...prev];
            newCompletions[newCompletions.length - 1].type = "error";
            newCompletions[newCompletions.length - 1].content =
              "Uh Oh. Failed to fetch response from server.";
            return newCompletions;
          });
        }
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
      <Switcher
        theme={theme}
        setTheme={setTheme}
        mode={mode}
        setMode={setMode}
      />
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
        <div className="content-area">
          {mode === 0 ? <Messages content={conv} /> : renderCompletions(0)}
        </div>
      </div>
      {/* Space */}
      <Background currentTheme={theme} />
      <div className={`${theme === 1 ? "theme-visible" : "theme-hidden"}`}>
        <Textbox text={mode === 0 ? conv : renderCompletions(1)} theme={1} />
      </div>
      {/* Magic */}
      <div className={`${theme === 2 ? "theme-visible" : "theme-hidden"}`}>
        <Textbox text={mode === 0 ? conv : renderCompletions(2)} theme={2} />
        <FireflyEffect count={30} />
        <Fog />
      </div>
      <ChatBox onButton={onButton} isLoading={isLoading} theme={theme} />
    </div>
  );
};

export default App;
