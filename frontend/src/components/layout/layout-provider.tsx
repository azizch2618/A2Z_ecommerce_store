"use client";

import * as React from "react";

interface LayoutContextValue {
  mobileNavOpen: boolean;
  setMobileNavOpen: (open: boolean) => void;
  searchOpen: boolean;
  setSearchOpen: (open: boolean) => void;
  headerScrolled: boolean;
}

const LayoutContext = React.createContext<LayoutContextValue | null>(null);

function LayoutProvider({ children }: { children: React.ReactNode }) {
  const [mobileNavOpen, setMobileNavOpen] = React.useState(false);
  const [searchOpen, setSearchOpen] = React.useState(false);
  const [headerScrolled, setHeaderScrolled] = React.useState(false);

  React.useEffect(() => {
    const onScroll = () => {
      setHeaderScrolled(window.scrollY > 10);
    };

    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  React.useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (
        event.key === "/" &&
        !searchOpen &&
        !(event.target instanceof HTMLInputElement) &&
        !(event.target instanceof HTMLTextAreaElement)
      ) {
        event.preventDefault();
        setSearchOpen(true);
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [searchOpen]);

  const value = React.useMemo(
    () => ({
      mobileNavOpen,
      setMobileNavOpen,
      searchOpen,
      setSearchOpen,
      headerScrolled,
    }),
    [mobileNavOpen, searchOpen, headerScrolled]
  );

  return (
    <LayoutContext.Provider value={value}>{children}</LayoutContext.Provider>
  );
}

function useLayout() {
  const context = React.useContext(LayoutContext);
  if (!context) {
    throw new Error("useLayout must be used within LayoutProvider");
  }
  return context;
}

export { LayoutProvider, useLayout };
