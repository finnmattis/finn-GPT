import React, { useState } from "react";
import "./ChatBox.css";
import { SendHorizonal, Square } from "lucide-react";

const MagicalGlyphs = () => {
  const glyphs = [
    "M0,25 Q25,0 50,25 T100,25",
    "M0,50 Q50,0 100,50 T200,50",
    "M0,75 Q75,0 150,75 T300,75",
    "M25,0 Q0,25 25,50 T25,100",
    "M50,0 Q0,50 50,100 T50,200",
    "M75,0 Q0,75 75,150 T75,300",
  ];

  return (
    <svg
      className="glyph-container"
      viewBox="0 0 300 100"
      preserveAspectRatio="none"
    >
      {glyphs.map((d, i) => (
        <path
          key={i}
          className="glyph glyph-animate"
          d={d}
          style={{ animationDelay: `${i * 0.2}s` }}
        />
      ))}
    </svg>
  );
};

const ChatBox = ({ onButton, isLoading, theme = 0 }) => {
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (input.trim() || isLoading) {
      onButton(input);
    }
    if (!isLoading) {
      setInput("");
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSend();
    }
  };

  const getThemeClass = (baseClass) => {
    const themeClasses = ["", "-space", "-magic"];
    return `${baseClass}${themeClasses[theme] || ""}`;
  };

  const chatboxClass = `chatbox ${getThemeClass("chatbox")}`;
  const inputClass = `text-input ${getThemeClass("text-input")}`;
  const buttonClass = `submit-button ${
    !input.trim() && !isLoading ? "disabled" : ""
  } ${getThemeClass("submit-button")}`;

  const getPlaceholderText = () => {
    switch (theme) {
      case 1:
        return "Transmit your cosmic message...";
      case 2:
        return "Cast your spell...";
      default:
        return "Continue writing...";
    }
  };

  const buttonContent = isLoading ? (
    <Square color="#070846" fill="#070846" />
  ) : (
    <SendHorizonal color="#070846" fill="#070846" />
  );

  return (
    <div className={chatboxClass}>
      <div className="input-wrapper">
        <input
          className={inputClass}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder={getPlaceholderText()}
        />
        {theme === 2 && <MagicalGlyphs />}
        <button
          className={`${buttonClass} ${
            theme === 2
              ? "animate-bg-pan bg-gradient-to-r from-purple-500 via-violet-500 to-pink-500 bg-[length:200%]"
              : ""
          }`}
          onClick={handleSend}
          disabled={!input.trim() && !isLoading}
        >
          {buttonContent}
        </button>
      </div>
      <p className={`disclaimer-text ${theme === 2 ? "text-transparent" : ""}`}>
        FinnGPT can not make mistakes. Don't bother verifying important
        information.
      </p>
    </div>
  );
};

export default ChatBox;
