import React from "react";
import { Settings, Rocket, Wand2 } from "lucide-react";

const ThemeSwitcher = ({ theme, setTheme }) => {
  const themes = [
    { icon: Settings, label: "Standard" },
    { icon: Rocket, label: "Space" },
    { icon: Wand2, label: "Magic" },
  ];

  const handleThemeChange = (index) => {
    setTheme(index);
  };

  return (
    <div className="fixed top-0 left-0 z-50 m-4">
      <div className="relative bg-gray-200 w-72 h-16 rounded-full p-1 flex items-center">
        {themes.map((theme, index) => (
          <button
            key={index}
            onClick={() => handleThemeChange(index)}
            className={`flex-1 h-14 flex items-center justify-center rounded-full transition-all duration-300 z-10 ${
              theme === index ? "text-blue-500" : "text-gray-500"
            }`}
          >
            <theme.icon size={24} />
          </button>
        ))}
        <div
          className="absolute bg-white w-1/3 h-14 rounded-full shadow-md transition-all duration-300"
          style={{
            left: `${theme * 33.33}%`,
          }}
        />
      </div>
    </div>
  );
};

export default ThemeSwitcher;
