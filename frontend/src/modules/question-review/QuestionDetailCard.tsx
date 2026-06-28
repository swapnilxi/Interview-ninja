import Icon from '@/components/ui/AppIcon';

interface QuestionDetailCardProps {
  question: {
    id: string;
    title: string;
    category: string;
    subCategory: string;
    difficulty: 'Easy' | 'Medium' | 'Hard';
    dateEncountered: string;
    content: string;
    tags: string[];
  };
}

export default function QuestionDetailCard({ question }: QuestionDetailCardProps) {
  const difficultyColors = {
    Easy: 'bg-success/20 text-success border-success/30',
    Medium: 'bg-warning/20 text-warning border-warning/30',
    Hard: 'bg-error/20 text-error border-error/30',
  };

  const categoryIcons: Record<string, string> = {
    'Data Structures': 'CubeIcon',
    'Algorithms': 'BeakerIcon',
    'System Design': 'ServerIcon',
    'Computer Vision': 'EyeIcon',
    'Behavioral': 'ChatBubbleLeftRightIcon',
    'Machine Learning': 'CpuChipIcon',
  };

  return (
    <div className="bg-card rounded-lg p-24 shadow-md border border-border">
      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-18 mb-24">
        <div className="flex-1">
          <div className="flex items-center gap-12 mb-12">
            <div className="w-36 h-36 rounded-md bg-primary/20 flex items-center justify-center">
              <Icon
                name={(categoryIcons[question.category] || 'QuestionMarkCircleIcon') as any}
                size={20}
                variant="outline"
                className="text-primary"
              />
            </div>
            <div>
              <span className="text-xs font-caption text-muted-foreground">
                {question.category} • {question.subCategory}
              </span>
            </div>
          </div>
          <h2 className="font-heading text-2xl font-semibold text-foreground mb-12">
            {question.title}
          </h2>
        </div>

        <div className="flex items-center gap-12">
          <span
            className={`
              px-18 py-6 rounded-md text-xs font-medium border
              ${difficultyColors[question.difficulty]}
            `}
          >
            {question.difficulty}
          </span>
          <div className="flex items-center gap-6 text-sm text-muted-foreground">
            <Icon name="CalendarIcon" size={16} variant="outline" />
            <span className="font-caption">{question.dateEncountered}</span>
          </div>
        </div>
      </div>

      <div className="prose prose-invert max-w-none mb-24">
        <p className="text-foreground leading-relaxed whitespace-pre-wrap">
          {question.content}
        </p>
      </div>

      <div className="flex flex-wrap gap-6">
        {question.tags.map((tag) => (
          <span
            key={tag}
            className="px-12 py-4 rounded-md bg-muted text-muted-foreground text-xs font-caption"
          >
            #{tag}
          </span>
        ))}
      </div>
    </div>
  );
}