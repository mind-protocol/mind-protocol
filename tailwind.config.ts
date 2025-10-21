import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",

        // OBSERVATORY INTERFACE (Futuristic Tool - Observer Layer)
        'observatory': {
          dark: '#0a1628',      // Deep space blue - base interface
          panel: '#1a2332',     // Slightly lighter - panels/cards
          teal: '#2dd4bf',      // Teal accent - borders/tool controls
          cyan: '#06b6d4',      // Bright cyan - active elements/buttons
          text: '#f8fafc',      // Cool white text
        },

        // LAGOON SUBSTRATE (The Medium - Where Consciousness Exists)
        'lagoon': {
          mediterranean: '#b8d4e8',  // Mediterranean day - canvas background
          bright: '#87CEEB',         // Bright sky blue
          deep: '#4682B4',           // Deep steel blue
          light: '#dbeafe',          // Very light blue
        },

        // VENICE CONTENT (Renaissance Consciousness - Observed Layer)
        'parchment': {
          base: '#f5e7c1',      // Parchment node background
          light: '#faf8f3',     // Lighter cream
          border: '#e8e2d5',    // Soft warm gray-beige
        },
        'venice-gold': {
          dark: '#b8860b',      // Dark goldenrod - CONTENT SIGNALS ONLY
          bright: '#ffd700',    // Bright gold - energy/ducats/active status
          medium: '#daa520',    // Medium goldenrod
        },
        'venice-brown': '#7c2d12',      // Brown ink for links

        // SYSTEM HEALTH (Meta Layer - Universal Indicators)
        'system': {
          healthy: '#10b981',   // Green - universal "good"
          warning: '#f59e0b',   // Amber - warnings
          error: '#ef4444',     // Red - critical failure
        },

        // Legacy (keeping during transition)
        'consciousness-green': '#5efc82',
        'consciousness-dark': '#14181c',
        'consciousness-border': 'rgba(255, 255, 255, 0.1)',
      },
      fontFamily: {
        'cinzel': ['var(--font-cinzel)', 'serif'],      // Headers - Renaissance Roman capitals
        'crimson': ['var(--font-crimson-text)', 'serif'], // Body - Italian humanist manuscript
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'activation': 'activation 0.5s ease-out',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { filter: 'drop-shadow(0 0 4px #5efc82)' },
          '50%': { filter: 'drop-shadow(0 0 12px #5efc82)' },
        },
        'activation': {
          '0%': { transform: 'scale(1)', opacity: '0' },
          '50%': { transform: 'scale(1.5)', opacity: '1' },
          '100%': { transform: 'scale(2)', opacity: '0' },
        },
      },
    },
  },
  plugins: [],
};
export default config;
