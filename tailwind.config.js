/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./pages/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        safe: "#16a34a",
        malicious: "#dc2626",
        risk: "#f59e0b",
      },
    },
  },
  plugins: [],
};
