"use client";

import * as React from "react";
import { Search, X } from "lucide-react";

import { searchPlaceholder } from "@/config/navigation";
import { SearchDropdown } from "@/components/search/search-dropdown";
import { usePredictiveSearch } from "@/components/search/use-predictive-search";
import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export interface SearchBarProps {
  className?: string;
  onFocus?: () => void;
  showDropdown?: boolean;
  autoFocus?: boolean;
  id?: string;
  onClose?: () => void;
  dropdownClassName?: string;
}

function SearchBar({
  className,
  onFocus,
  showDropdown = true,
  autoFocus,
  id = "site-search",
  onClose,
  dropdownClassName,
}: SearchBarProps) {
  const inputRef = React.useRef<HTMLInputElement>(null);
  const {
    query,
    setQuery,
    isOpen,
    setIsOpen,
    isLoading,
    results,
    recentSearches,
    popularSearches,
    flatItems,
    activeIndex,
    hasQuery,
    showNoResults,
    handleKeyDown,
    submitSearch,
    selectItem,
    clearRecent,
  } = usePredictiveSearch({ onClose });

  const listboxId = `${id}-suggestions`;
  const showPanel = showDropdown && isOpen;

  return (
    <div className={cn("relative w-full", className)}>
      <form
        role="search"
        onSubmit={(event) => {
          event.preventDefault();
          submitSearch();
        }}
      >
        <div className="relative">
          <Search
            className="pointer-events-none absolute left-3 top-1/2 size-5 -translate-y-1/2 text-muted-foreground"
            aria-hidden
          />
          <Input
            ref={inputRef}
            id={id}
            type="search"
            role="combobox"
            aria-expanded={showPanel}
            aria-controls={listboxId}
            aria-autocomplete="list"
            aria-activedescendant={
              activeIndex >= 0 ? `${listboxId}-option-${activeIndex}` : undefined
            }
            placeholder={searchPlaceholder}
            autoFocus={autoFocus}
            autoComplete="off"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            onFocus={() => {
              setIsOpen(true);
              onFocus?.();
            }}
            onBlur={() => {
              window.setTimeout(() => setIsOpen(false), 150);
            }}
            onKeyDown={handleKeyDown}
            className="h-11 border-neutral-200 bg-neutral-50 pl-10 pr-10 text-base dark:border-border dark:bg-muted/40 lg:h-12"
          />
          {query ? (
            <Button
              type="button"
              variant="ghost"
              size="icon-sm"
              className="absolute right-1 top-1/2 -translate-y-1/2"
              aria-label="Clear search"
              onMouseDown={(event) => event.preventDefault()}
              onClick={() => {
                setQuery("");
                inputRef.current?.focus();
              }}
            >
              <X className="size-4" />
            </Button>
          ) : null}
        </div>
      </form>

      {showPanel ? (
        <SearchDropdown
          id={listboxId}
          query={query}
          isLoading={isLoading}
          results={results}
          recentSearches={recentSearches}
          popularSearches={popularSearches}
          flatItems={flatItems}
          activeIndex={activeIndex}
          hasQuery={hasQuery}
          showNoResults={showNoResults}
          onSelectItem={selectItem}
          onSelectQuery={(value) => {
            setQuery(value);
            submitSearch(value);
          }}
          onClearRecent={clearRecent}
          className={dropdownClassName}
        />
      ) : null}
    </div>
  );
}

export { SearchBar };
