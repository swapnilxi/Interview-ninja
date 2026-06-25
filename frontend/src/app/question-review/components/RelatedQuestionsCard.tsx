import Icon from '@/components/ui/AppIcon';

interface RelatedQuestion {
  id: string;
  title: string;
  category: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  similarity: number;
}

interface RelatedQuestionsCardProps {
  questions: RelatedQuestion[];
  onQuestionSelect: (questionId: string) => void;
}

export default function RelatedQuestionsCard({
  questions,
  onQuestionSelect,
}: RelatedQuestionsCardProps) {
  const difficultyColors = {
    Easy: 'text-success',
    Medium: 'text-warning',
    Hard: 'text-error',
  };

  return (
    <div className="bg-card rounded-lg p-24 shadow-md border border-border">
      <div className="flex items-center gap-12 mb-18">
        <Icon name="LinkIcon" size={20} variant="outline" className="text-primary" />
        <h3 className="font-heading text-lg font-medium text-foreground">
          Related Questions
        </h3>
      </div>

      <p className="text-sm text-muted-foreground mb-18 font-caption">
        Practice similar questions to reinforce learning patterns
      </p>

      <div className="space-y-12">
        {questions.map((question) => (
          <button
            key={question.id}
            onClick={() => onQuestionSelect(question.id)}
            className="
              w-full p-18 rounded-md bg-muted/50 border border-border
              hover:bg-muted hover:border-primary/50
              transition-smooth focus-ring text-left
              group
            "
          >
            <div className="flex items-start justify-between gap-12 mb-6">
              <h4 className="font-heading text-sm font-medium text-foreground group-hover:text-primary transition-smooth flex-1">
                {question.title}
              </h4>
              <Icon
                name="ArrowRightIcon"
                size={16}
                variant="outline"
                className="text-muted-foreground group-hover:text-primary transition-smooth flex-shrink-0 mt-2"
              />
            </div>
            <div className="flex items-center gap-12 text-xs">
              <span className="text-muted-foreground font-caption">
                {question.category}
              </span>
              <span className="text-muted-foreground">•</span>
              <span className={`font-medium ${difficultyColors[question.difficulty]}`}>
                {question.difficulty}
              </span>
              <span className="text-muted-foreground">•</span>
              <span className="text-muted-foreground font-caption">
                {question.similarity}% similar
              </span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}