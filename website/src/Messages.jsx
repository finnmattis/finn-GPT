import { MessageCircle, User, AlertTriangle } from "lucide-react";
import { useState, useEffect } from "react";

const ChatMessage = ({ type, content, index, theme }) => {
  const [isVisible, setIsVisible] = useState(false);
  const isUser = type === "user";
  const isError = type === "error";

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, index * 100); // Stagger the animation

    return () => clearTimeout(timer);
  }, [index]);

  const getThemeStyles = () => {
    if (theme === 1) {
      return {
        user: "bg-blue-500 text-white",
        assistant: "bg-green-500 text-white",
        error: "bg-red-500 text-white",
      };
    } else if (theme === 2) {
      return {
        user: "bg-opacity-20 backdrop-filter backdrop-blur-md border border-white border-opacity-30",
        assistant:
          "bg-opacity-20 backdrop-filter backdrop-blur-md border border-white border-opacity-30",
        error:
          "bg-opacity-20 backdrop-filter backdrop-blur-md border border-white border-opacity-30",
      };
    } else {
      return {
        user: "bg-blue-100 text-blue-800",
        assistant: "bg-gray-100 text-gray-800",
        error: "bg-red-100 text-red-800",
      };
    }
  };

  const themeStyles = getThemeStyles();

  return (
    <div
      className={`flex ${
        isUser ? "justify-end" : "justify-start"
      } mb-4 transition-all duration-500 ease-out ${
        isVisible
          ? "opacity-100 translate-x-0"
          : `opacity-0 ${isUser ? "translate-x-full" : "-translate-x-full"}`
      }`}
    >
      <div
        className={`max-w-3/4 p-3 rounded-lg ${
          isUser
            ? themeStyles.user
            : isError
            ? themeStyles.error
            : themeStyles.assistant
        }`}
      >
        <div className="flex items-center mb-2">
          {isUser ? (
            <User className="w-5 h-5 mr-2" />
          ) : isError ? (
            <AlertTriangle className="w-5 h-5 mr-2" />
          ) : (
            <MessageCircle className="w-5 h-5 mr-2" />
          )}
          <span className="font-semibold">
            {isUser ? "User" : isError ? "Error" : "Assistant"}
          </span>
        </div>
        <p>{content}</p>
      </div>
    </div>
  );
};

const Messages = ({ content, theme = 0 }) => {
  const messages = content
    .split("<|")
    .filter(Boolean)
    .map((msg) => {
      const [type, ...contentParts] = msg.split("|>");
      return { type, content: contentParts.join("|>").trim() };
    });

  const containerStyles = () => {
    if (theme === 1 || theme === 2) {
      return {
        position: "absolute",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        width: "50vw",
        minWidth: "300px",
        height: "70vh",
        overflow: "hidden",
        zIndex: 10,
      };
    } else {
      return {};
    }
  };

  const innerStyles = () => {
    if (theme === 1) {
      return {
        position: "absolute",
        inset: 0,
        margin: "1.5rem",
        overflowY: "auto",
      };
    } else if (theme === 2) {
      return {
        position: "absolute",
        inset: 0,
        padding: "20px",
        overflowY: "auto",
        background: "rgba(0, 0, 0, 0.2)",
        backdropFilter: "blur(8px)",
        borderRadius: "10px",
        boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
        border: "1px solid rgba(255, 255, 255, 0.3)",
      };
    } else {
      return {};
    }
  };

  return (
    <div className="container mx-auto max-w-2xl p-4" style={containerStyles()}>
      {theme === 1 && (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 100 140"
          className="absolute inset-0 w-full h-full"
          preserveAspectRatio="none"
        >
          <defs>
            <style>
              {`
              .frame-border { fill: none; stroke: #149daf; stroke-width: 0.5; stroke-miterlimit: 10; }
              .frame-accent { fill: #149daf; stroke-width: 0; }
              .frame-glass { fill: #149daf; opacity: 0.2; }
              `}
            </style>
          </defs>
          <polygon
            className="frame-glass"
            points="0,0 100,0 100,126 90,140 10,140 0,126 0,0"
          />
          <polygon
            className="frame-border"
            points="0,0 100,0 100,126 90,140 10,140 0,126 0,0"
          />
          <polygon
            className="frame-accent"
            points="100,133 100,140 90,140 100,133"
          />
          <rect className="frame-accent" x="2" y="0" width="20" height="1" />
          <rect className="frame-accent" x="10" y="138" width="30" height="1" />
          <rect className="frame-accent" x="98" y="70" width="1" height="7" />
        </svg>
      )}
      <div
        className="relative overflow-auto scrollbar-hide"
        style={innerStyles()}
      >
        <div className="space-y-4">
          {messages.map((msg, index) => (
            <ChatMessage
              key={index}
              type={msg.type}
              content={msg.content}
              index={index}
              theme={theme}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default Messages;
