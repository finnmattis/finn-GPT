import PropTypes from "prop-types";
import { useState, useEffect } from "react";
import { Settings, Rocket, Wand2, Menu } from "lucide-react";

const ThemeSwitcher = ({ theme, setTheme }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  const themes = [
    { icon: Settings, label: "Standard" },
    { icon: Rocket, label: "Space" },
    { icon: Wand2, label: "Magic" },
  ];

  useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkScreenSize();
    window.addEventListener("resize", checkScreenSize);

    return () => window.removeEventListener("resize", checkScreenSize);
  }, []);

  const handleThemeChange = (index) => {
    setTheme(index);
    setIsMenuOpen(false);
  };

  if (!isMobile) {
    return (
      <div className="fixed top-0 left-0 z-40 m-4">
        <div className="relative bg-gray-200 w-72 h-16 rounded-full p-1 flex items-center">
          {themes.map((themeItem, index) => (
            <button
              key={index}
              onClick={() => handleThemeChange(index)}
              className={`flex-1 h-14 flex items-center justify-center rounded-full transition-all duration-300 z-10 ${
                theme === index ? "text-blue-500" : "text-gray-500"
              }`}
            >
              <themeItem.icon size={24} />
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
  }

  return (
    <>
      <button
        onClick={() => setIsMenuOpen(!isMenuOpen)}
        className="fixed top-4 left-4 z-50 p-2 bg-gray-200 rounded-full shadow-md"
      >
        <Menu size={24} />
      </button>

      <div
        className={`fixed top-0 left-0 z-40 h-full w-64 bg-gray-200 shadow-lg transform transition-transform duration-300 ease-in-out ${
          isMenuOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex flex-col h-full pt-16 px-4">
          {themes.map((themeItem, index) => (
            <button
              key={index}
              onClick={() => handleThemeChange(index)}
              className={`flex items-center space-x-4 py-4 ${
                theme === index ? "text-blue-500" : "text-gray-500"
              }`}
            >
              <themeItem.icon size={24} />
              <span>{themeItem.label}</span>
            </button>
          ))}
        </div>
      </div>
    </>
  );
};

ThemeSwitcher.propTypes = {
  theme: PropTypes.number.isRequired,
  setTheme: PropTypes.func.isRequired,
};

export default ThemeSwitcher;
