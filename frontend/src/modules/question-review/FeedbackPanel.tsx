'use client';

import { useState } from 'react';
import Icon from '@/components/ui/AppIcon';

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
  hasAnswer: boolean;
}

export default function FeedbackPanel({ feedback, questionType, hasAnswer }: FeedbackPanelProps) {
  const [unlocked, setUnlocked] = useState(false);
  const [generating, setGenerating] = useState(false);

  const handleGenerate = () => {
    if (!hasAnswer) return;
    setGenerating(true);
    setTimeout(() => {
      setGenerating(false);
      setUnlocked(true);
    }, 1800);
  };

  // Locked state — no answer yet
  if (!hasAnswer) {
    return (
      <div className="bg-card rounded-lg p-24 shadow-md border border-border">
        <div className="flex items-center gap-12 mb-18">
          <div className="w-36 h-36 rounded-md bg-muted flex items-center justify-center">
            <Icon name="LockClosedIcon" size={20} variant="outline" className="text-muted-foreground" />
          </div>
          <h3 className="font-heading text-lg font-medium text-foreground">Feedback & Analysis</h3>
        </div>
        <div className="text-center py-24 border border-dashed border-border rounded-lg">
          <Icon name="PencilSquareIcon" size={36} variant="outline" className="text-muted-foreground/50 mx-auto mb-12" />
          <p className="text-sm text-muted-foreground font-body">
            Write your answer first, then generate AI feedback.
          </p>
        </div>
      </div>
    );
  }

  // Has answer but not yet generated
  if (!unlocked) {
    return (
      <div className="bg-card rounded-lg p-24 shadow-md border border-border">
        <div className="flex items-center gap-12 mb-18">
          <div className="w-36 h-36 rounded-md bg-secondary/20 flex items-center justify-center">
            <Icon name="SparklesIcon" size={20} variant="outline" className="text-secondary" />
          </div>
          <h3 className="font-heading text-lg font-medium text-foreground">Feedback & Analysis</h3>
        </div>
        <div className="text-center py-24 space-y-18">
          <Icon name="SparklesIcon" size={40} variant="outline" className="text-secondary/60 mx-auto" />
          <div>
            <p className="text-sm text-foreground font-medium mb-6">Ready to analyse your answer</p>
            <p className="text-xs text-muted-foreground font-body">
              Click the button below to generate AI-powered feedback, strengths, and improvement areas based on your response.
            </p>
          </div>
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="inline-flex items-center gap-9 px-24 py-12 bg-secondary text-secondary-foreground rounded-md font-medium text-sm hover:bg-secondary/90 transition-smooth disabled:opacity-60"
          >
            {generating ? (
              <>
                <span className="w-16 h-16 border-2 border-secondary-foreground/30 border-t-secondary-foreground rounded-full animate-spin" />
                Generating Feedback...
              </>
            ) : (
              <>
                <Icon name="SparklesIcon" size={16} variant="solid" />
                Generate Feedback
              </>
            )}
          </button>
        </div>
      </div>
    );
  }

  // Fully unlocked — show feedback
  const feedbackSections = [
    { category: 'Strengths', icon: 'CheckCircleIcon', items: feedback.strengths },
    { category: 'Areas for Improvement', icon: 'LightBulbIcon', items: feedback.improvements },
    ...(feedback.technicalDepth?.length ? [{ category: 'Technical Depth', icon: 'BeakerIcon', items: feedback.technicalDepth }] : []),
    ...(feedback.bestPractices?.length ? [{ category: 'Best Practices', icon: 'SparklesIcon', items: feedback.bestPractices }] : []),
  ];

  return (
    <div className="bg-card rounded-lg p-24 shadow-md border border-border animate-fade-in">
      <div className="flex items-center gap-12 mb-24">
        <div className="w-36 h-36 rounded-md bg-success/20 flex items-center justify-center">
          <Icon name="ChatBubbleLeftRightIcon" size={20} variant="outline" className="text-success" />
        </div>
        <h3 className="font-heading text-lg font-medium text-foreground">Detailed Feedback & Recommendations</h3>
      </div>

      <div className="space-y-24">
        {feedbackSections.map((section) => (
          <div key={section.category}>
            <div className="flex items-center gap-12 mb-12">
              <Icon name={section.icon as any} size={18} variant="outline" className="text-primary" />
              <h4 className="font-heading text-base font-medium text-foreground">{section.category}</h4>
            </div>
            <ul className="space-y-12 pl-30">
              {section.items.map((item, index) => (
                <li key={index} className="text-sm text-foreground leading-relaxed flex gap-12">
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
              <Icon name="StarIcon" size={18} variant="solid" className="text-accent" />
              <h4 className="font-heading text-base font-medium text-foreground">STAR Method Guidance</h4>
            </div>
            <div className="space-y-12 bg-muted/50 rounded-md p-18">
              {(['situation', 'task', 'action', 'result'] as const).map((key) => (
                <div key={key}>
                  <span className="text-xs font-caption text-accent font-semibold uppercase">{key}:</span>
                  <p className="text-sm text-foreground mt-4">{feedback.starGuidance![key]}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}