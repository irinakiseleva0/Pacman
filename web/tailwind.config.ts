import type { Config } from "tailwindcss";
import animate from "tailwindcss-animate";

const config = {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        neon: {
          yellow: "#ffe66d",
          cyan: "#33f6ff",
          purple: "#b565ff",
          pink: "#ff3df2",
          ink: "#080912",
        },
      },
      fontFamily: {
        display: ["Orbitron", "Inter", "system-ui", "sans-serif"],
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        glow: "0 0 18px rgba(51, 246, 255, 0.28)",
        "glow-yellow": "0 0 22px rgba(255, 230, 109, 0.32)",
        "glow-purple": "0 0 24px rgba(181, 101, 255, 0.3)",
      },
      backgroundImage: {
        "grid-neon":
          "linear-gradient(rgba(51,246,255,0.09) 1px, transparent 1px), linear-gradient(90deg, rgba(181,101,255,0.08) 1px, transparent 1px)",
        "radial-signal":
          "radial-gradient(circle at top left, rgba(255,230,109,0.2), transparent 34%), radial-gradient(circle at 85% 15%, rgba(51,246,255,0.18), transparent 30%), radial-gradient(circle at 50% 85%, rgba(181,101,255,0.2), transparent 38%)",
      },
    },
  },
  plugins: [animate],
} satisfies Config;

export default config;
