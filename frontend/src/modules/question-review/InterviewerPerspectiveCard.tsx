import Icon from '@/components/ui/AppIcon';

interface InterviewerPerspectiveCardProps {
  perspective: {
    whatInterviewersLookFor: string[];
    commonMistakes: string[];
    realWorldApplication: string;
  };
}

export default function InterviewerPerspectiveCard({
  perspective,
}: InterviewerPerspectiveCardProps) {
  return (
    <div className="bg-card rounded-lg p-24 shadow-md border border-border">
      <div className="flex items-center gap-12 mb-24">
        <div className="w-36 h-36 rounded-md bg-accent/20 flex items-center justify-center">
          <Icon
            name="UserGroupIcon"
            size={20}
            variant="outline"
            className="text-accent"
          />
        </div>
        <h3 className="font-heading text-lg font-medium text-foreground">
          Interviewer Perspective
        </h3>
      </div>

      <div className="space-y-24">
        <div>
          <div className="flex items-center gap-12 mb-12">
            <Icon
              name="EyeIcon"
              size={18}
              variant="outline"
              className="text-success"
            />
            <h4 className="font-heading text-base font-medium text-foreground">
              What Interviewers Look For
            </h4>
          </div>
          <ul className="space-y-12 pl-30">
            {perspective.whatInterviewersLookFor.map((item, index) => (
              <li
                key={index}
                className="text-sm text-foreground leading-relaxed flex gap-12"
              >
                <span className="text-success mt-6">✓</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <div className="flex items-center gap-12 mb-12">
            <Icon
              name="ExclamationTriangleIcon"
              size={18}
              variant="outline"
              className="text-warning"
            />
            <h4 className="font-heading text-base font-medium text-foreground">
              Common Mistakes to Avoid
            </h4>
          </div>
          <ul className="space-y-12 pl-30">
            {perspective.commonMistakes.map((item, index) => (
              <li
                key={index}
                className="text-sm text-foreground leading-relaxed flex gap-12"
              >
                <span className="text-warning mt-6">⚠</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="pt-18 border-t border-border">
          <div className="flex items-center gap-12 mb-12">
            <Icon
              name="BriefcaseIcon"
              size={18}
              variant="outline"
              className="text-primary"
            />
            <h4 className="font-heading text-base font-medium text-foreground">
              Real-World Application
            </h4>
          </div>
          <p className="text-sm text-foreground leading-relaxed pl-30">
            {perspective.realWorldApplication}
          </p>
        </div>
      </div>
    </div>
  );
}