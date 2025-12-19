/** @type {import('tailwindcss').Config} */
export default {
    content: [
      "./index.html",
      "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
      extend: {
        colors: {
            // Custom dark trading theme
            trade: {
                bg: "#0a0a0a",
                surface: "#1a1a1a",
                border: "#333333",
                primary: "#2563eb", // Blue
                danger: "#ef4444", // Red (Loss)
                success: "#22c55e", // Green (Win)
                warning: "#facc15", // Yellow
            }
        }
      },
    },
    plugins: [],
  }
