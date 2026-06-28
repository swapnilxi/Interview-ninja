'use client';

import { useState } from 'react';
import Icon from '@/components/ui/AppIcon';

interface ExportOptions {
  includeAnswers: boolean;
  includeNotes: boolean;
  includeTimestamps: boolean;
  format: 'markdown' | 'pdf';
}

interface ExportActionPanelProps {
  sessionData: {
    sessionId: string;
    date: string;
    questionsCompleted: number;
    totalQuestions: number;
  };
  onExport: (options: ExportOptions) => Promise<void>;
  onClose?: () => void;
}

export default function ExportActionPanel({
  sessionData,
  onExport,
  onClose,
}: ExportActionPanelProps) {
  const [options, setOptions] = useState<ExportOptions>({
    includeAnswers: true,
    includeNotes: true,
    includeTimestamps: true,
    format: 'markdown',
  });

  const [isExporting, setIsExporting] = useState(false);
  const [exportComplete, setExportComplete] = useState(false);

  const handleOptionToggle = (key: keyof ExportOptions) => {
    if (key === 'format') return;
    setOptions((prev) => ({
      ...prev,
      [key]: !prev[key as keyof typeof prev],
    }));
  };

  const handleFormatChange = (format: 'markdown' | 'pdf') => {
    setOptions((prev) => ({ ...prev, format }));
  };

  const handleExport = async () => {
    setIsExporting(true);
    try {
      await onExport(options);
      setExportComplete(true);
      setTimeout(() => {
        setExportComplete(false);
        onClose?.();
      }, 2000);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="bg-card rounded-lg p-36 shadow-xl border border-border max-w-md w-full">
      <div className="flex items-center justify-between mb-24">
        <div className="flex items-center gap-12">
          <div className="w-36 h-36 rounded-md bg-success/20 flex items-center justify-center">
            <Icon
              name="CheckCircleIcon"
              size={20}
              variant="solid"
              className="text-success"
            />
          </div>
          <div>
            <h3 className="font-heading text-lg font-semibold text-foreground">
              Session Complete!
            </h3>
            <p className="text-sm text-muted-foreground font-caption">
              {sessionData.questionsCompleted}/{sessionData.totalQuestions}{' '}
              questions completed
            </p>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-6 rounded-md hover:bg-muted transition-smooth focus-ring"
            aria-label="Close export panel"
          >
            <Icon name="XMarkIcon" size={20} variant="outline" />
          </button>
        )}
      </div>

      <div className="space-y-18 mb-24">
        <div>
          <h4 className="text-sm font-medium text-foreground mb-12 font-heading">
            Export Format
          </h4>
          <div className="grid grid-cols-2 gap-12">
            <button
              onClick={() => handleFormatChange('markdown')}
              className={`
                h-48 px-18 rounded-md flex items-center justify-center gap-6
                transition-smooth font-medium text-sm focus-ring
                ${
                  options.format === 'markdown'
                    ? 'bg-primary text-primary-foreground shadow-glow' :'bg-muted text-muted-foreground hover:bg-muted/80'
                }
              `}
            >
              <Icon name="DocumentTextIcon" size={18} variant="outline" />
              Markdown
            </button>
            <button
              onClick={() => handleFormatChange('pdf')}
              className={`
                h-48 px-18 rounded-md flex items-center justify-center gap-6
                transition-smooth font-medium text-sm focus-ring
                ${
                  options.format === 'pdf' ?'bg-primary text-primary-foreground shadow-glow' :'bg-muted text-muted-foreground hover:bg-muted/80'
                }
              `}
            >
              <Icon name="DocumentArrowDownIcon" size={18} variant="outline" />
              PDF
            </button>
          </div>
        </div>

        <div>
          <h4 className="text-sm font-medium text-foreground mb-12 font-heading">
            Include in Export
          </h4>
          <div className="space-y-12">
            <label className="flex items-center gap-12 cursor-pointer group">
              <input
                type="checkbox"
                checked={options.includeAnswers}
                onChange={() => handleOptionToggle('includeAnswers')}
                className="
                  w-18 h-18 rounded border-2 border-border
                  bg-input checked:bg-primary checked:border-primary
                  transition-smooth cursor-pointer focus-ring
                "
              />
              <span className="text-sm text-foreground group-hover:text-primary transition-smooth">
                Your Answers
              </span>
            </label>

            <label className="flex items-center gap-12 cursor-pointer group">
              <input
                type="checkbox"
                checked={options.includeNotes}
                onChange={() => handleOptionToggle('includeNotes')}
                className="
                  w-18 h-18 rounded border-2 border-border
                  bg-input checked:bg-primary checked:border-primary
                  transition-smooth cursor-pointer focus-ring
                "
              />
              <span className="text-sm text-foreground group-hover:text-primary transition-smooth">
                Personal Notes
              </span>
            </label>

            <label className="flex items-center gap-12 cursor-pointer group">
              <input
                type="checkbox"
                checked={options.includeTimestamps}
                onChange={() => handleOptionToggle('includeTimestamps')}
                className="
                  w-18 h-18 rounded border-2 border-border
                  bg-input checked:bg-primary checked:border-primary
                  transition-smooth cursor-pointer focus-ring
                "
              />
              <span className="text-sm text-foreground group-hover:text-primary transition-smooth">
                Timestamps
              </span>
            </label>
          </div>
        </div>
      </div>

      <div className="flex gap-12">
        {onClose && (
          <button
            onClick={onClose}
            disabled={isExporting}
            className="
              flex-1 h-48 px-36 rounded-md
              bg-muted text-foreground
              font-medium text-sm
              hover:bg-muted/80 active:scale-[0.97]
              transition-smooth focus-ring
              disabled:opacity-50 disabled:cursor-not-allowed
            "
          >
            Cancel
          </button>
        )}
        <button
          onClick={handleExport}
          disabled={isExporting || exportComplete}
          className="
            flex-1 h-48 px-36 rounded-md
            bg-primary text-primary-foreground
            font-medium text-sm
            hover:shadow-glow active:scale-[0.97]
            transition-smooth focus-ring
            disabled:opacity-50 disabled:cursor-not-allowed
            flex items-center justify-center gap-6
          "
        >
          {isExporting ? (
            <>
              <div className="w-18 h-18 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
              Exporting...
            </>
          ) : exportComplete ? (
            <>
              <Icon
                name="CheckIcon"
                size={18}
                variant="outline"
                className="text-primary-foreground"
              />
              Complete!
            </>
          ) : (
            <>
              <Icon
                name="ArrowDownTrayIcon"
                size={18}
                variant="outline"
                className="text-primary-foreground"
              />
              Export Session
            </>
          )}
        </button>
      </div>

      <div className="mt-18 pt-18 border-t border-border">
        <p className="text-xs text-muted-foreground text-center font-caption">
          Session ID: {sessionData.sessionId} • {sessionData.date}
        </p>
      </div>
    </div>
  );
}