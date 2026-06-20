/** Official A2Z Tools brand assets (see docs/UI_DESIGN_SYSTEM.md §1.3) */

export const brand = {
  name: "A2Z Tools",
  legalName: "A2Z Tools Pty Ltd",
  logo: {
    /** Full lockup — icon + A2ZTOOLS + PTY LTD */
    full: {
      src: "/brand/a2z-tools-logo.png",
      width: 1024,
      height: 682,
      alt: "A2Z Tools Pty Ltd",
    },
    /** Compact mark for mobile header (crops icon from full lockup) */
    mark: {
      src: "/brand/a2z-tools-logo.png",
      width: 1024,
      height: 682,
      alt: "A2Z Tools",
    },
  },
} as const;

/** Max logo width on desktop header (design system: 140px) */
export const LOGO_MAX_WIDTH_PX = 140;

/** Minimum logomark size (design system: 32px) */
export const LOGOMARK_SIZE_PX = 32;
