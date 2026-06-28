'use client';

import { useState, useEffect } from 'react';
import Icon from '@/components/ui/AppIcon';

interface ActionButtonsPanelProps {
  questionId: string;
  isMastered: boolean;
  isInReviewList: boolean;
  onPracticeSimilar: () => void;
  onToggleReviewList: () => void;
  onToggleMastered: () => void;
}

export default function ActionButtonsPanel({
  questionId,
  isMastered,
  isInReviewList,
  onPracticeSimilar,
  onToggleReviewList,
  onToggleMastered,
}: ActionButtonsPanelProps) {
  const [isHydrated, setIsHydrated] = useState(false);

  useEffect(() => {
    setIsHydrated(true);
  }, []);

  if (!isHydrated) {
    return (
      <div className="bg-card rounded-lg p-24 shadow-md border border-border">
        <div className="h-[120px]" />
      </div>
    );
  }

  return (
    <div className="bg-card rounded-lg p-24 shadow-md border border-border">
      <h3 className="font-heading text-lg font-medium text-foreground mb-18">
        Quick Actions
      </h3>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-12">
        <button
          onClick={onPracticeSimilar}
          className="
            h-48 px-18 rounded-md
            bg-primary text-primary-foreground
            font-medium text-sm
            hover:shadow-glow active:scale-[0.97]
            transition-smooth focus-ring
            flex items-center justify-center gap-6
          "
        >
          <Icon name="AcademicCapIcon" size={18} variant="outline" />
          Practice Similar
        </button>

        <button
          onClick={onToggleReviewList}
          className={`
            h-48 px-18 rounded-md
            font-medium text-sm
            active:scale-[0.97]
            transition-smooth focus-ring
            flex items-center justify-center gap-6
            ${
              isInReviewList
                ? 'bg-success text-success-foreground hover:bg-success/90'
                : 'bg-muted text-foreground hover:bg-muted/80'
            }
          `}
        >
          <Icon
            name={isInReviewList ? 'CheckIcon' : 'BookmarkIcon'}
            size={18}
            variant={isInReviewList ? 'solid' : 'outline'}
          />
          {isInReviewList ? 'In Review List' : 'Add to Review'}
        </button>

        <button
          onClick={onToggleMastered}
          className={`
            h-48 px-18 rounded-md
            font-medium text-sm
            active:scale-[0.97]
            transition-smooth focus-ring
            flex items-center justify-center gap-6
            ${
              isMastered
                ? 'bg-accent text-accent-foreground hover:bg-accent/90'
                : 'bg-muted text-foreground hover:bg-muted/80'
            }
          `}
        >
          <Icon
            name={isMastered ? 'CheckBadgeIcon' : 'TrophyIcon'}
            size={18}
            variant={isMastered ? 'solid' : 'outline'}
          />
          {isMastered ? 'Mastered' : 'Mark as Mastered'}
        </button>
      </div>

      <div className="mt-18 pt-18 border-t border-border">
        <p className="text-xs text-muted-foreground text-center font-caption">
          Question ID: {questionId}
        </p>
      </div>
    </div>
  );
}