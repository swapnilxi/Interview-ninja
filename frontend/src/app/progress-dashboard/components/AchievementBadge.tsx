import Icon from '@/components/ui/AppIcon';

interface AchievementBadgeProps {
  title: string;
  description: string;
  icon: string;
  isUnlocked: boolean;
  unlockedDate?: string;
}

export default function AchievementBadge({
  title,
  description,
  icon,
  isUnlocked,
  unlockedDate,
}: AchievementBadgeProps) {
  return (
    <div
      className={`
        bg-card rounded-lg p-18 border transition-smooth
        ${isUnlocked ? 'border-success shadow-md' : 'border-border opacity-60'}
      `}
    >
      <div className="flex items-start gap-12">
        <div
          className={`
            w-48 h-48 rounded-md flex items-center justify-center flex-shrink-0
            ${isUnlocked ? 'bg-success/20' : 'bg-muted'}
          `}
        >
          <Icon
            name={icon as any}
            size={24}
            variant={isUnlocked ? 'solid' : 'outline'}
            className={isUnlocked ? 'text-success' : 'text-muted-foreground'}
          />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-medium text-foreground mb-4 truncate">
            {title}
          </h4>
          <p className="text-xs text-muted-foreground font-caption line-clamp-2">
            {description}
          </p>
          {isUnlocked && unlockedDate && (
            <p className="text-xs text-success font-caption mt-6">
              Unlocked {unlockedDate}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}