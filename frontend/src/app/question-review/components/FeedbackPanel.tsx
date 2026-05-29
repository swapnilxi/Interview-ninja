import Icon from '@/components/ui/AppIcon';

interface FeedbackItem {
  category: string;
  icon: string;
  items: string[];
}

interface FeedbackPanelProps {
  feedback: {
    strengths: string[];
    improvements: string[];
    starGuidance?: {
      situation: string;
      task: string;
      action: string;
      result: string;
    };
    technicalDepth?: string[];
    bestPractices?: string[];
  };
  questionType: string;
}

export default function FeedbackPanel({ feedback, questionType }: FeedbackPanelProps) {
  const feedbackSections: FeedbackItem[] = [
    {
      category: 'Strengths',
      icon: 'CheckCircleIcon',
      items: feedback.strengths,
    },
    {
      category: 'Areas for Improvement',
      icon: 'LightBulbIcon',
      items: feedback.improvements,
    },
  ];

  if (feedback.technicalDepth && feedback.technicalDepth.length > 0) {
    feedbackSections.push({
      category: 'Technical Depth Recommendations',
      icon: 'BeakerIcon',
      items: feedback.technicalDepth,
    });
  }

  if (feedback.bestPractices && feedback.bestPractices.length > 0) {
    feedbackSections.push({
      category: 'Best Practices',
      icon: 'SparklesIcon',
      items: feedback.bestPractices,
    });
  }

  return (
    <div className="bg-card rounded-lg p-24 shadow-md border border-border">
      <div className="flex items-center gap-12 mb-24">
        <div className="w-36 h-36 rounded-md bg-secondary/20 flex items-center justify-center">
          <Icon
            name="ChatBubbleLeftRightIcon"
            size={20}
            variant="outline"
            className="text-secondary"
          />
        </div>
        <h3 className="font-heading text-lg font-medium text-foreground">
          Detailed Feedback & Recommendations
        </h3>
      </div>

      <div className="space-y-24">
        {feedbackSections.map((section) => (
          <div key={section.category}>
            <div className="flex items-center gap-12 mb-12">
              <Icon
                name={section.icon as any}
                size={18}
                variant="outline"
                className="text-primary"
              />
              <h4 className="font-heading text-base font-medium text-foreground">
                {section.category}
              </h4>
            </div>
            <ul className="space-y-12 pl-30">
              {section.items.map((item, index) => (
                <li
                  key={index}
                  className="text-sm text-foreground leading-relaxed flex gap-12"
                >
                  <span className="text-primary mt-6">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}

        {feedback.starGuidance && (
          <div className="pt-24 border-t border-border">
            <div className="flex items-center gap-12 mb-18">
              <Icon
                name="StarIcon"
                size={18}
                variant="solid"
                className="text-accent"
              />
              <h4 className="font-heading text-base font-medium text-foreground">
                STAR Method Guidance
              </h4>
            </div>
            <div className="space-y-12 bg-muted/50 rounded-md p-18">
              <div>
                <span className="text-xs font-caption text-accent font-semibold">
                  SITUATION:
                </span>
                <p className="text-sm text-foreground mt-4">
                  {feedback.starGuidance.situation}
                </p>
              </div>
              <div>
                <span className="text-xs font-caption text-accent font-semibold">
                  TASK:
                </span>
                <p className="text-sm text-foreground mt-4">
                  {feedback.starGuidance.task}
                </p>
              </div>
              <div>
                <span className="text-xs font-caption text-accent font-semibold">
                  ACTION:
                </span>
                <p className="text-sm text-foreground mt-4">
                  {feedback.starGuidance.action}
                </p>
              </div>
              <div>
                <span className="text-xs font-caption text-accent font-semibold">
                  RESULT:
                </span>
                <p className="text-sm text-foreground mt-4">
                  {feedback.starGuidance.result}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}