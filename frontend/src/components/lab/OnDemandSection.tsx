'use client';

import { useState } from 'react';
import Icon from '@/components/ui/AppIcon';

interface OnDemandSectionProps {
  sectionIndex: number;
  icon: string;
  title: string;
  subtitle?: string;
  content: string | null;
  isGenerating: boolean;
  isGenerated: boolean;
  onGenerate: () => void;
  children?: React.ReactNode; // for custom render (e.g. quiz)
}

export default function OnDemandSection({
  sectionIndex,
  icon,
  title,
  subtitle,
  content,
  isGenerating,
  isGenerated,
  onGenerate,
  children,
}: OnDemandSectionProps) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="bg-card border border-border rounded-lg overflow-hidden shadow-sm transition-smooth">
      {/* Header */}
      <div className="flex items-center justify-between p-16 border-b border-border">
        <div className="flex items-center gap-12">
          <div className="w-32 h-32 rounded-md bg-primary/10 flex items-center justify-center flex-shrink-0">
            <Icon name={icon as any} size={16} className="text-primary" />
          </div>
          <div>
            <div className="flex items-center gap-9">
              <span className="text-xs text-muted-foreground font-code">{String(sectionIndex).padStart(2, '0')}</span>
              <h3 className="font-heading text-sm font-semibold text-foreground">{title}</h3>
            </div>
            {subtitle && <p className="text-xs text-muted-foreground mt-2">{subtitle}</p>}
          </div>
        </div>

        <div className="flex items-center gap-9">
          {!isGenerated ? (
            <button
              onClick={onGenerate}
              disabled={isGenerating}
              className="flex items-center gap-6 px-14 py-7 bg-secondary/10 border border-secondary/30 text-secondary text-xs font-semibold rounded-md hover:bg-secondary/20 transition-smooth disabled:opacity-50"
            >
              {isGenerating ? (
                <><span className="w-10 h-10 border-2 border-secondary/30 border-t-secondary rounded-full animate-spin" />Generating...</>
              ) : (
                <><Icon name="SparklesIcon" size={12} />Generate</>
              )}
            </button>
          ) : (
            <div className="flex items-center gap-6">
              <span className="text-xs text-success flex items-center gap-4">
                <Icon name="CheckCircleIcon" size={12} />Done
              </span>
              {!children && (
                <button
                  onClick={() => setCollapsed(c => !c)}
                  className="p-5 rounded-md hover:bg-muted transition-smooth"
                >
                  <Icon name={collapsed ? 'ChevronDownIcon' : 'ChevronUpIcon'} size={14} className="text-muted-foreground" />
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Content */}
      {isGenerated && !collapsed && (
        <div className="p-18 animate-fade-in">
          {children ?? (
            <div className="text-sm leading-relaxed text-foreground space-y-12">
              {(content ?? '').split('\n').map((line, i) => {
                if (line.startsWith('```')) return null;
                if (line.startsWith('**') && line.endsWith('**')) {
                  return <h4 key={i} className="font-heading font-semibold text-foreground mt-18 mb-6">{line.replace(/\*\*/g, '')}</h4>;
                }
                if (line.startsWith('- ') || line.startsWith('• ')) {
                  return (
                    <div key={i} className="flex gap-9 items-start">
                      <span className="text-primary mt-4 flex-shrink-0">•</span>
                      <span className="font-body">{line.replace(/^[-•]\s/, '')}</span>
                    </div>
                  );
                }
                if (/^\d+\.\s/.test(line)) {
                  const num = line.match(/^(\d+)\./)?.[1];
                  return (
                    <div key={i} className="flex gap-9 items-start">
                      <span className="text-primary font-semibold flex-shrink-0 w-18">{num}.</span>
                      <span>{line.replace(/^\d+\.\s/, '')}</span>
                    </div>
                  );
                }
                if (line.trim() === '' ) return <div key={i} className="h-6" />;
                return <p key={i} className="font-body">{line}</p>;
              })}
            </div>
          )}
        </div>
      )}

      {/* Code blocks (extracted separately) */}
      {isGenerated && !collapsed && content && content.includes('```') && (
        <div className="px-18 pb-18">
          {content.split('```').filter((_, i) => i % 2 === 1).map((code, i) => {
            const lines = code.split('\n');
            const lang = lines[0].trim();
            const codeContent = lines.slice(1).join('\n');
            return (
              <div key={i} className="mt-12 rounded-lg overflow-hidden border border-border">
                <div className="flex items-center justify-between px-14 py-7 bg-muted border-b border-border">
                  <span className="text-xs font-code text-muted-foreground">{lang || 'python'}</span>
                  <Icon name="CodeBracketIcon" size={14} className="text-muted-foreground" />
                </div>
                <pre className="p-14 bg-[#1a1a2e] overflow-x-auto">
                  <code className="text-xs font-code text-[#e2e8f0] leading-relaxed whitespace-pre">{codeContent}</code>
                </pre>
              </div>
            );
          })}
        </div>
      )}

      {/* Locked state */}
      {!isGenerated && !isGenerating && (
        <div className="px-18 py-12 flex items-center gap-9 text-muted-foreground border-t border-border">
          <Icon name="LockClosedIcon" size={12} />
          <p className="text-xs">Click Generate ✨ to load this section</p>
        </div>
      )}
    </div>
  );
}
