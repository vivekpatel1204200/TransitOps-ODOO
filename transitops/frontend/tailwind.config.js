/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["'Space Grotesk'", "sans-serif"],
      },
      colors: {
        brand: {
          50: "#eff6ff", 100: "#dbeafe", 500: "#2563eb",
          600: "#1d4ed8", 700: "#1e40af", 900: "#1e3a8a",
        },
      },
    },
  },
  plugins: [],
};
