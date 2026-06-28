'use client';

import Icon from '@/components/ui/AppIcon';

interface SortControlsProps {
  sortBy: string;
  sortOrder: 'asc' | 'desc';
  onSortChange: (sortBy: string) => void;
  onOrderChange: () => void;
}

const sortOptions = [
  { value: 'dateEncountered', label: 'Date Encountered' },
  { value: 'lastReviewed', label: 'Last Reviewed' },
  { value: 'difficulty', label: 'Difficulty' },
  { value: 'category', label: 'Category' },
  { value: 'performance', label: 'Performance' },
];

export default function SortControls({
  sortBy,
  sortOrder,
  onSortChange,
  onOrderChange,
}: SortControlsProps) {
  return (
    <div className="flex items-center gap-12">
      <div className="flex items-center gap-6">
        <Icon
          name="ArrowsUpDownIcon"
          size={18}
          variant="outline"
          className="text-muted-foreground"
        />
        <span className="text-sm text-muted-foreground font-caption">
          Sort by:
        </span>
      </div>

      <select
        value={sortBy}
        onChange={(e) => onSortChange(e.target.value)}
        className="h-36 px-12 rounded-md bg-input border border-border text-foreground text-sm transition-smooth focus-ring cursor-pointer"
      >
        {sortOptions.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>

      <button
        onClick={onOrderChange}
        className="p-9 rounded-md hover:bg-muted transition-smooth focus-ring"
        aria-label={`Sort ${sortOrder === 'asc' ? 'descending' : 'ascending'}`}
        title={`Sort ${sortOrder === 'asc' ? 'descending' : 'ascending'}`}
      >
        <Icon
          name={sortOrder === 'asc' ? 'ArrowUpIcon' : 'ArrowDownIcon'}
          size={18}
          variant="outline"
        />
      </button>
    </div>
  );
}