'use client';

import Icon from '@/components/ui/AppIcon';

interface BulkActionsBarProps {
  selectedCount: number;
  onExport: () => void;
  onMarkForReview: () => void;
  onClearSelection: () => void;
}

export default function BulkActionsBar({
  selectedCount,
  onExport,
  onMarkForReview,
  onClearSelection,
}: BulkActionsBarProps) {
  if (selectedCount === 0) return null;

  return (
    <div className="fixed bottom-24 left-1/2 -translate-x-1/2 z-50 animate-in slide-in-from-bottom-5 duration-300">
      <div className="bg-card rounded-lg shadow-xl border border-border p-18 flex items-center gap-18">
        <div className="flex items-center gap-12">
          <div className="w-36 h-36 rounded-md bg-primary/20 flex items-center justify-center">
            <Icon
              name="CheckCircleIcon"
              size={18}
              variant="solid"
              className="text-primary"
            />
          </div>
          <div>
            <p className="text-sm font-medium text-foreground">
              {selectedCount} {selectedCount === 1 ? 'question' : 'questions'} selected
            </p>
            <p className="text-xs text-muted-foreground font-caption">
              Choose an action below
            </p>
          </div>
        </div>

        <div className="h-36 w-px bg-border" />

        <div className="flex items-center gap-6">
          <button
            onClick={onExport}
            className="flex items-center gap-6 px-18 py-9 rounded-md bg-primary text-primary-foreground hover:shadow-glow transition-smooth focus-ring"
          >
            <Icon name="ArrowDownTrayIcon" size={16} variant="outline" />
            <span className="text-sm font-medium">Export</span>
          </button>

          <button
            onClick={onMarkForReview}
            className="flex items-center gap-6 px-18 py-9 rounded-md bg-secondary text-secondary-foreground hover:shadow-glow transition-smooth focus-ring"
          >
            <Icon name="BookmarkIcon" size={16} variant="outline" />
            <span className="text-sm font-medium">Mark for Review</span>
          </button>

          <button
            onClick={onClearSelection}
            className="p-9 rounded-md hover:bg-muted transition-smooth focus-ring"
            aria-label="Clear selection"
          >
            <Icon name="XMarkIcon" size={18} variant="outline" />
          </button>
        </div>
      </div>
    </div>
  );
}