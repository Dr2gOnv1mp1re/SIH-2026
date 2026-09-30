/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        enterprise: {
          bg: "#07080F",            // Deep Space void background
          bgSecondary: "#0C0E1A",   // Header / Top bar (purple-black)
          card: "#12152A",          // Cards with violet undertone
          cardHover: "#181C36",     // Interactive hover state
          cardSubtle: "#0E1122",    // Inner nested panels
          border: "#1C2042",        // Subtle purple-tint border
          borderLight: "#2A2F5A",   // Active / Focused border
          textPrimary: "#F1F5F9",   // Crisp white text
          textSecondary: "#94A3B8", // Slate body text
          textMuted: "#64748B",     // Metadata / Caption text
          cyan: "#06B6D4",          // Electric Cyan (Primary Accent)
          cyanLight: "#22D3EE",     // Hover cyan
          violet: "#8B5CF6",        // Rich Violet (Secondary Accent)
          violetLight: "#A78BFA",   // Lighter violet
          rose: "#F43F5E",          // Critical Risk / Alert Rose
          roseLight: "#FB7185",     // Rose accent
          amber: "#F59E0B",         // Warning Amber
          emerald: "#10B981",       // Healthy / Verified Emerald
          emeraldLight: "#34D399",  // Green accent
          purple: "#7C3AED"         // Governance / ML Purple
        }
      },
      fontFamily: {
        sans: ['Inter', 'Outfit', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace']
      },
      boxShadow: {
        'card': '0 4px 20px -2px rgba(8, 5, 30, 0.6)',
        'card-hover': '0 8px 30px -4px rgba(8, 5, 30, 0.8)',
        'subtle': '0 1px 3px 0 rgba(0, 0, 0, 0.4)',
        'modal': '0 25px 50px -12px rgba(0, 0, 0, 0.9)',
        'glow-cyan': '0 0 20px -4px rgba(6, 182, 212, 0.25)',
        'glow-violet': '0 0 20px -4px rgba(139, 92, 246, 0.25)'
      }
    },
  },
  plugins: [],
}
