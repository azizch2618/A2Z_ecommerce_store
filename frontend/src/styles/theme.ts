/**
 * A2Z Tools theme constants for programmatic use (charts, meta tags, etc.)
 * CSS variables in src/styles/tokens.css are the source of truth for styling.
 */

export const theme = {
  colors: {
    brand: {
      navy: "#0F172A",
      navyLight: "#1E293B",
      blue: "#0066CC",
      blueHover: "#0052A3",
      blueLight: "#EFF6FF",
      amber: "#D97706",
      amberLight: "#FFFBEB",
    },
    semantic: {
      success: "#059669",
      warning: "#D97706",
      error: "#DC2626",
      info: "#0066CC",
    },
  },
  breakpoints: {
    sm: 640,
    md: 768,
    lg: 1024,
    xl: 1280,
    "2xl": 1536,
  },
  container: {
    maxWidth: 1440,
    padding: {
      mobile: 16,
      tablet: 24,
      desktop: 32,
    },
  },
  touchTarget: 44,
  gstRate: 0.1,
  currency: "AUD",
} as const;

export type Theme = typeof theme;
