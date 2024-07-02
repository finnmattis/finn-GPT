import { MessageCircle, User, AlertTriangle } from "lucide-react";
import { useState, useEffect } from "react";

const ChatMessage = ({ type, content, index }) => {
  const [isVisible, setIsVisible] = useState(false);
  const isUser = type === "user";
  const isError = type === "error";

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, index * 100); // Stagger the animation

    return () => clearTimeout(timer);
  }, [index]);

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
            ? "bg-blue-100 text-blue-800"
            : isError
            ? "bg-red-100 text-red-800"
            : "bg-gray-100 text-gray-800"
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

const Messages = ({ content }) => {
  const messages = content
    .split("<|")
    .filter(Boolean)
    .map((msg) => {
      const [type, ...contentParts] = msg.split("|>");
      return { type, content: contentParts.join("|>").trim() };
    });

  return (
    <div className="container mx-auto max-w-2xl p-4">
      <div className="space-y-4">
        {messages.map((msg, index) => (
          <ChatMessage
            key={index}
            type={msg.type}
            content={msg.content}
            index={index}
          />
        ))}
      </div>
    </div>
  );
};

export default Messages;
