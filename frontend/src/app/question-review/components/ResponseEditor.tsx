'use client';

import { useState, useEffect } from 'react';
import Icon from '@/components/ui/AppIcon';

interface ResponseEditorProps {
  initialResponse: string;
  onResponseUpdate: (response: string) => void;
  questionId: string;
}

export default function ResponseEditor({
  initialResponse,
  onResponseUpdate,
  questionId,
}: ResponseEditorProps) {
  const [isHydrated, setIsHydrated] = useState(false);
  const [response, setResponse] = useState(initialResponse);
  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<string>('');
  const [wordCount, setWordCount] = useState(0);

  useEffect(() => {
    setIsHydrated(true);
  }, []);

  useEffect(() => {
    if (isHydrated) {
      const words = response.trim().split(/\s+/).filter(Boolean).length;
      setWordCount(words);
    }
  }, [response, isHydrated]);

  const handleResponseChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setResponse(e.target.value);
  };

  const handleSave = async () => {
    setIsSaving(true);
    await new Promise((resolve) => setTimeout(resolve, 800));
    onResponseUpdate(response);
    if (isHydrated) {
      const now = new Date();
      setLastSaved(
        now.toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit',
        })
      );
    }
    setIsSaving(false);
  };

  const handleReset = () => {
    setResponse(initialResponse);
  };

  if (!isHydrated) {
    return (
      <div className="bg-card rounded-lg p-24 shadow-md border border-border">
        <div className="flex items-center justify-between mb-18">
          <h3 className="font-heading text-lg font-medium text-foreground">
            Your Response
          </h3>
        </div>
        <div className="h-[300px] bg-input rounded-md border border-border" />
      </div>
    );
  }

  return (
    <div className="bg-card rounded-lg p-24 shadow-md border border-border">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-12 mb-18">
        <div className="flex items-center gap-12">
          <Icon name="PencilSquareIcon" size={20} variant="outline" />
          <h3 className="font-heading text-lg font-medium text-foreground">
            Your Response
          </h3>
        </div>
        <div className="flex items-center gap-12">
          <span className="text-sm text-muted-foreground font-caption">
            {wordCount} words
          </span>
          {lastSaved && (
            <span className="text-xs text-muted-foreground font-caption">
              Last saved: {lastSaved}
            </span>
          )}
        </div>
      </div>

      <textarea
        value={response}
        onChange={handleResponseChange}
        placeholder="Type your response here..."
        className="
          w-full h-[300px] p-18 rounded-md
          bg-input border border-border
          text-foreground placeholder:text-muted-foreground
          resize-none transition-smooth focus-ring
          font-body text-sm leading-relaxed
        "
      />

      <div className="flex flex-col sm:flex-row gap-12 mt-18">
        <button
          onClick={handleSave}
          disabled={isSaving || response === initialResponse}
          className="
            flex-1 h-48 px-24 rounded-md
            bg-primary text-primary-foreground
            font-medium text-sm
            hover:shadow-glow active:scale-[0.97]
            transition-smooth focus-ring
            disabled:opacity-50 disabled:cursor-not-allowed
            flex items-center justify-center gap-6
          "
        >
          {isSaving ? (
            <>
              <div className="w-18 h-18 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Icon name="CheckIcon" size={18} variant="outline" />
              Save Changes
            </>
          )}
        </button>
        <button
          onClick={handleReset}
          disabled={response === initialResponse}
          className="
            flex-1 h-48 px-24 rounded-md
            bg-muted text-foreground
            font-medium text-sm
            hover:bg-muted/80 active:scale-[0.97]
            transition-smooth focus-ring
            disabled:opacity-50 disabled:cursor-not-allowed
            flex items-center justify-center gap-6
          "
        >
          <Icon name="ArrowPathIcon" size={18} variant="outline" />
          Reset to Original
        </button>
      </div>
    </div>
  );
}