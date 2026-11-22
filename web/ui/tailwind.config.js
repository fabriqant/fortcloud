/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontSize: {
        "4xs": ["var(--text-4xs)", { lineHeight: "var(--leading-4xs)" }],
        "3xs": ["var(--text-3xs)", { lineHeight: "var(--leading-3xs)" }],
        "2xs": ["var(--text-2xs)", { lineHeight: "var(--leading-2xs)" }],
        xs: ["var(--text-xs)", { lineHeight: "var(--leading-xs)" }],
        sm: ["var(--text-sm)", { lineHeight: "var(--leading-sm)" }],
        base: ["var(--text-base)", { lineHeight: "var(--leading-base)" }],
        lg: ["var(--text-lg)", { lineHeight: "var(--leading-lg)" }],
        xl: ["var(--text-xl)", { lineHeight: "var(--leading-xl)" }],
        "2xl": ["var(--text-2xl)", { lineHeight: "var(--leading-2xl)" }],
        "3xl": ["var(--text-3xl)", { lineHeight: "var(--leading-3xl)" }],
        "4xl": ["var(--text-4xl)", { lineHeight: "var(--leading-4xl)" }],
        "sidebar-desc": ["var(--text-sidebar-desc)", { lineHeight: "var(--leading-sidebar-desc)" }],
        "accordion-title": ["var(--text-accordion-title)", { lineHeight: "var(--leading-accordion-title)" }],
        control: ["var(--text-control)", { lineHeight: "var(--leading-control)" }],
        footer: ["var(--text-footer)", { lineHeight: "var(--leading-footer)" }],
      },
      lineHeight: {
        none: "1",
        tight: "1.25",
        snug: "1.4",
        normal: "1.5",
        relaxed: "1.6",
        loose: "2",
        3: "0.85",
        4: "1.1",
        5: "1.3",
        6: "1.8",
        7: "2",
        8: "2.2",
        9: "2.4",
        10: "2.6",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "SFMono-Regular", "Consolas", "monospace"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(15,23,42,.04), 0 8px 24px rgba(15,23,42,.05)",
      },
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(4px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "tool-in": {
          "0%": { opacity: "0", transform: "translateY(8px) scale(0.995)" },
          "100%": { opacity: "1", transform: "translateY(0) scale(1)" },
        },
      },
      animation: {
        "fade-in": "fade-in .22s ease-out both",
        "tool-in": "tool-in .32s cubic-bezier(0.22, 1, 0.36, 1) both",
      },
    },
  },
  plugins: [],
};
