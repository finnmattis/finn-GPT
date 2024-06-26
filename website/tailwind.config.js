/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",

    // Or if using `src` directory:
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    screens: {
      sm: { min: "0px", max: "767px" },
      md: { min: "768px", max: "991px" },
      lg: { min: "992px", max: "1199px" },
      xl: { min: "1200px" },
    },
    extend: {
      colors: {
        primary: "#0A092B",
        secondary: "#303854",
        highlight: "#AAB1F9",
        text: "#F9F7FB",
      },
      gridTemplateColumns: {
        responsive: "repeat(auto-fit, minmax(20rem, 1fr))",
      },
      keyframes: {
        pan: {
          "0%": { backgroundPosition: " 0% center" },
          "100%": { backgroundPosition: "-200% center" },
        },
        twinkle: {
          "0%": { transform: "scale(0) rotate(0deg)" },
          "50%": { transform: "scale(1) rotate(180deg)" },
          "100%": { transform: "scale(0) rotate(360deg)" },
        },
      },
      animation: {
        "bg-pan": "pan 3s linear infinite",
        twinkle: "twinkle 1000ms ease infinite",
      },
    },
  },
  plugins: [require("tailwind-scrollbar-hide")],
};
