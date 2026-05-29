import Icon from '@/components/ui/AppIcon';

interface EmptyStateProps {
  hasFilters: boolean;
  onClearFilters?: () => void;
}

export default function EmptyState({ hasFilters, onClearFilters }: EmptyStateProps) {
  return (
    <div className="bg-card rounded-lg p-48 shadow-md border border-border text-center">
      <div className="w-72 h-72 rounded-full bg-muted/50 flex items-center justify-center mx-auto mb-24">
        <Icon
          name={hasFilters ? 'FunnelIcon' : 'BookOpenIcon'}
          size={36}
          variant="outline"
          className="text-muted-foreground"
        />
      </div>

      <h3 className="font-heading text-xl font-semibold text-foreground mb-12">
        {hasFilters ? 'No Questions Found' : 'No Questions Yet'}
      </h3>

      <p className="text-sm text-muted-foreground max-w-md mx-auto mb-24 font-body">
        {hasFilters
          ? 'No questions match your current filters. Try adjusting your search criteria or clearing filters to see all questions.' :'Start your daily practice sessions to build your question bank. Questions from completed sessions will appear here for review and practice.'}
      </p>

      {hasFilters && onClearFilters && (
        <button
          onClick={onClearFilters}
          className="inline-flex items-center gap-6 px-24 py-12 rounded-md bg-primary text-primary-foreground hover:shadow-glow transition-smooth focus-ring"
        >
          <Icon name="XMarkIcon" size={18} variant="outline" />
          <span className="font-medium">Clear Filters</span>
        </button>
      )}
    </div>
  );
}