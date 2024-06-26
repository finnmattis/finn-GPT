import React, { useState } from "react";
import { Settings, Rocket, Wand2 } from "lucide-react";

const ThemeSwitcher = () => {
  const [activeTheme, setActiveTheme] = useState(0);

  const themes = [
    { icon: Settings, label: "Standard" },
    { icon: Rocket, label: "Space" },
    { icon: Wand2, label: "Magic" },
  ];

  const handleThemeChange = (index) => {
    setActiveTheme(index);
  };

  return (
    <div className="fixed top-0 left-0 z-50 m-4">
      <div className="relative bg-gray-200 w-72 h-16 rounded-full p-1 flex items-center">
        {themes.map((theme, index) => (
          <button
            key={index}
            onClick={() => handleThemeChange(index)}
            className={`flex-1 h-14 flex items-center justify-center rounded-full transition-all duration-300 z-10 ${
              activeTheme === index ? "text-blue-500" : "text-gray-500"
            }`}
          >
            <theme.icon size={24} />
          </button>
        ))}
        <div
          className="absolute bg-white w-1/3 h-14 rounded-full shadow-md transition-all duration-300"
          style={{
            left: `${activeTheme * 33.33}%`,
          }}
        />
      </div>
    </div>
  );
};

export default ThemeSwitcher;
