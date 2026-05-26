import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        slatePanel: "#111827",
        slateInk: "#e5e7eb",
        citation: "#38bdf8"
      }
    }
  },
  plugins: []
};

export default config;
