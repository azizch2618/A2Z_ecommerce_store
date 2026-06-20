export interface SearchHighlightProps {
  text: string;
  query: string;
  className?: string;
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function SearchHighlight({ text, query, className }: SearchHighlightProps) {
  const trimmed = query.trim();
  if (!trimmed) {
    return <span className={className}>{text}</span>;
  }

  const tokens = trimmed
    .split(/\s+/)
    .filter(Boolean)
    .sort((a, b) => b.length - a.length);

  if (tokens.length === 0) {
    return <span className={className}>{text}</span>;
  }

  const pattern = new RegExp(`(${tokens.map(escapeRegExp).join("|")})`, "gi");
  const parts = text.split(pattern);

  return (
    <span className={className}>
      {parts.map((part, index) => {
        const isMatch = tokens.some(
          (token) => part.toLowerCase() === token.toLowerCase()
        );
        if (!isMatch) {
          return <span key={`${part}-${index}`}>{part}</span>;
        }
        return (
          <mark
            key={`${part}-${index}`}
            className="rounded-sm bg-brand-amber/35 px-0.5 font-semibold text-foreground"
          >
            {part}
          </mark>
        );
      })}
    </span>
  );
}

export { SearchHighlight };
