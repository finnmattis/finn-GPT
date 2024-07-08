import { useState, useRef } from "react";
import ChatBox from "./ChatBox";
import "./App.css";
import StarsBackground from "./StarsBackground";
import Switcher from "./Switcher";
import MagicText from "./MagicText";
import FireflyEffect from "./Firefly";
import Fog from "./Fog";
import Content from "./Content";

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
      let url;
      if (mode === 0) {
        url = new URL("http://127.0.0.1:5000/");
      } else {
        url = new URL("https://base-finn-gpt-enoprmj2xa-uc.a.run.app/");
      }
      url.searchParams.append("context", conv + input);

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
                    return prev.slice(0, -7);
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

  return (
    <div className={`app-container`}>
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
      <Content
        content={mode === 0 ? conv : completions}
        theme={theme}
        mode={mode}
      />
      <ChatBox onButton={onButton} isLoading={isLoading} theme={theme} />
      {/* Space Background */}
      <StarsBackground currentTheme={theme} />
      {/* Magic Background */}
      <div
        className={`app-container-magic theme-transition ${
          theme === 2 ? "theme-visible" : "theme-hidden"
        }`}
      ></div>
      <div
        className={`${theme === 2 ? "theme-visible" : "theme-hidden w-0 h-0"}`}
      >
        <FireflyEffect count={50} />
        <Fog />
      </div>
    </div>
  );
};

export default App;
