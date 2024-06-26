import React from "react";

const Textbox = ({ text, theme = 2 }) => {
  const getThemeStyles = () => {
    if (theme === 2) {
      return {
        background: "rgba(0, 0, 0, 0.2)",
        backdropFilter: "blur(8px)",
        borderRadius: "10px",
        padding: "20px",
        boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
        border: "1px solid rgba(255, 255, 255, 0.3)",
      };
    }
    return {};
  };

  return (
    <div
      className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-1/2 overflow-hidden"
      style={{ maxWidth: "50vw", height: "70vh", ...getThemeStyles() }}
    >
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
        className={`relative z-10 overflow-auto scrollbar-hide ${
          theme === 1 ? "absolute inset-0 m-6" : ""
        }`}
        style={{
          maxHeight: theme === 1 ? "calc(100% - 5rem)" : "100%",
        }}
      >
        <div
          className={`text-center text-white}`}
          style={{
            fontSize: "22px",
            lineHeight: "1.5",
          }}
        >
          {text}
        </div>
      </div>
    </div>
  );
};

export default Textbox;
