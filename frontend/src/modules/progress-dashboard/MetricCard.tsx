import Icon from '@/components/ui/AppIcon';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle: string;
  icon: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color: 'primary' | 'secondary' | 'success' | 'accent';
}

const colorClasses = {
  primary: 'bg-primary/20 text-primary',
  secondary: 'bg-secondary/20 text-secondary',
  success: 'bg-success/20 text-success',
  accent: 'bg-accent/20 text-accent',
};

export default function MetricCard({
  title,
  value,
  subtitle,
  icon,
  trend,
  color,
}: MetricCardProps) {
  return (
    <div className="bg-card rounded-lg p-24 shadow-md border border-border hover:shadow-lg transition-smooth">
      <div className="flex items-start justify-between mb-18">
        <div className={`w-48 h-48 rounded-md ${colorClasses[color]} flex items-center justify-center`}>
          <Icon name={icon as any} size={24} variant="outline" />
        </div>
        {trend && (
          <div className={`flex items-center gap-4 text-sm font-medium ${trend.isPositive ? 'text-success' : 'text-error'}`}>
            <Icon
              name={trend.isPositive ? 'ArrowTrendingUpIcon' : 'ArrowTrendingDownIcon'}
              size={16}
              variant="outline"
            />
            <span>{Math.abs(trend.value)}%</span>
          </div>
        )}
      </div>
      <div>
        <h3 className="text-3xl font-heading font-semibold text-foreground mb-6">
          {value}
        </h3>
        <p className="text-sm font-medium text-muted-foreground mb-4">
          {title}
        </p>
        <p className="text-xs text-muted-foreground font-caption">
          {subtitle}
        </p>
      </div>
    </div>
  );
}