import React from 'react';
import { Search } from 'lucide-react';

// Actually I'll check utils first in a second, but for now I'll assume standard Shadcn-like structure or just simple class string.
// Pivot: logic to be safe.

interface SearchInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  containerClassName?: string;
}

export const SearchInput: React.FC<SearchInputProps> = ({
  className,
  containerClassName,
  ...props
}) => {
  return (
    <div className={`relative ${containerClassName || ''}`}>
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted pointer-events-none" />
      <input
        type="text"
        className={`field-surface w-full pl-9 pr-4 py-2 text-sm text-text-primary placeholder:text-text-secondary outline-none transition-all ${className || ''}`}
        aria-label="Search"
        {...props}
      />
    </div>
  );
};
