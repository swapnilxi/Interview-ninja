'use client';

import React, { useState, useEffect } from 'react';
import Icon from '@/components/ui/AppIcon';
import { settingsService, UserSettings } from '@/lib/services/settingsService';

const AVAILABLE_MODELS = [
  { id: 'gemini-2.5-flash', name: 'Gemini 2.5 Flash (Fast, Recommended)', provider: 'Google' },
  { id: 'gemini-2.5-pro', name: 'Gemini 2.5 Pro (High Quality)', provider: 'Google' },
  { id: 'gpt-4o', name: 'GPT-4o (Premium)', provider: 'OpenAI' },
  { id: 'gpt-4o-mini', name: 'GPT-4o Mini (Cost Effective)', provider: 'OpenAI' },
  { id: 'claude-3-5-sonnet-latest', name: 'Claude 3.5 Sonnet (State-of-the-Art)', provider: 'Anthropic' },
  { id: 'claude-3-5-haiku-latest', name: 'Claude 3.5 Haiku (Fast)', provider: 'Anthropic' },
];

export default function ConfigInteractive() {
  const [settings, setSettings] = useState<UserSettings>({
    questionModel: 'gemini-2.5-flash',
    answerModel: 'gemini-2.5-pro',
    openaiKey: '',
    geminiKey: '',
    anthropicKey: '',
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Security visibility states for keys
  const [showOpenaiKey, setShowOpenaiKey] = useState(false);
  const [showGeminiKey, setShowGeminiKey] = useState(false);
  const [showAnthropicKey, setShowAnthropicKey] = useState(false);

  useEffect(() => {
    async function loadSettings() {
      try {
        const data = await settingsService.getSettings();
        if (data) {
          setSettings(data);
        }
      } catch (err) {
        console.error('Failed to load settings:', err);
      } finally {
        setLoading(false);
      }
    }
    loadSettings();
  }, []);

  const handleChange = (key: keyof UserSettings, value: string) => {
    setSettings((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setToast(null);

    try {
      await settingsService.saveSettings(settings);
      setToast({
        type: 'success',
        message: 'Settings and API keys saved successfully to SQLite!',
      });
      // Clear toast after 4 seconds
      setTimeout(() => setToast(null), 4000);
    } catch (err) {
      console.error(err);
      setToast({
        type: 'error',
        message: 'Failed to update user settings. Please check backend connection.',
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-60">
        <div className="w-48 h-48 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-24">
      {/* Toast Alert */}
      {toast && (
        <div
          className={`p-18 rounded-lg border flex items-center gap-12 animate-fade-in shadow-lg ${
            toast.type === 'success'
              ? 'bg-success/15 border-success text-success-foreground'
              : 'bg-error/15 border-error text-error-foreground'
          }`}
        >
          <Icon
            name={toast.type === 'success' ? 'CheckCircleIcon' : 'ExclamationTriangleIcon'}
            size={20}
            variant="solid"
            className={toast.type === 'success' ? 'text-success' : 'text-error'}
          />
          <span className="text-sm font-medium">{toast.message}</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-24">
        {/* Model Configurations */}
        <div className="bg-card border border-border rounded-lg p-24 shadow-md space-y-18">
          <div className="flex items-center gap-12 pb-12 border-b border-border">
            <Icon name="CpuChipIcon" size={24} className="text-primary" />
            <div>
              <h3 className="font-heading text-lg font-semibold text-foreground">Model Configuration</h3>
              <p className="text-xs text-muted-foreground">Select LLM architectures for running daily prompts and evaluation</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-18">
            <div className="space-y-6">
              <label htmlFor="questionModel" className="block text-sm font-medium text-foreground">
                Question Generation Model
              </label>
              <select
                id="questionModel"
                value={settings.questionModel}
                onChange={(e) => handleChange('questionModel', e.target.value)}
                className="w-full rounded-md border border-border bg-input px-12 py-9 text-sm text-foreground focus-ring transition-smooth"
              >
                {AVAILABLE_MODELS.map((model) => (
                  <option key={`q-${model.id}`} value={model.id}>
                    {model.name}
                  </option>
                ))}
              </select>
              <span className="text-[11px] text-muted-foreground">Used for daily topic expansion and parsing CV details.</span>
            </div>

            <div className="space-y-6">
              <label htmlFor="answerModel" className="block text-sm font-medium text-foreground">
                Answer Evaluation Model
              </label>
              <select
                id="answerModel"
                value={settings.answerModel}
                onChange={(e) => handleChange('answerModel', e.target.value)}
                className="w-full rounded-md border border-border bg-input px-12 py-9 text-sm text-foreground focus-ring transition-smooth"
              >
                {AVAILABLE_MODELS.map((model) => (
                  <option key={`a-${model.id}`} value={model.id}>
                    {model.name}
                  </option>
                ))}
              </select>
              <span className="text-[11px] text-muted-foreground">Used to score, provide STAR guidelines, and highlight improvements.</span>
            </div>
          </div>
        </div>

        {/* API Credentials */}
        <div className="bg-card border border-border rounded-lg p-24 shadow-md space-y-18">
          <div className="flex items-center gap-12 pb-12 border-b border-border">
            <Icon name="KeyIcon" size={24} className="text-secondary" />
            <div>
              <h3 className="font-heading text-lg font-semibold text-foreground">API Keys Management</h3>
              <p className="text-xs text-muted-foreground">Stored securely in your local SQLite credentials table</p>
            </div>
          </div>

          <div className="space-y-18">
            {/* Google Gemini API Key */}
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <label htmlFor="geminiKey" className="block text-sm font-medium text-foreground">
                  Google Gemini API Key
                </label>
                <span className="text-xs text-muted-foreground">Required for Gemini models</span>
              </div>
              <div className="relative">
                <input
                  id="geminiKey"
                  type={showGeminiKey ? 'text' : 'password'}
                  value={settings.geminiKey}
                  onChange={(e) => handleChange('geminiKey', e.target.value)}
                  placeholder="AIzaSy..."
                  className="w-full rounded-md border border-border bg-input pl-12 pr-48 py-9 text-sm text-foreground focus-ring font-code"
                />
                <button
                  type="button"
                  onClick={() => setShowGeminiKey(!showGeminiKey)}
                  className="absolute right-12 top-1/2 -translate-y-1/2 p-6 text-muted-foreground hover:text-foreground transition-smooth"
                  aria-label={showGeminiKey ? "Hide key" : "Show key"}
                >
                  <Icon name={showGeminiKey ? 'EyeSlashIcon' : 'EyeIcon'} size={18} />
                </button>
              </div>
            </div>

            {/* OpenAI API Key */}
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <label htmlFor="openaiKey" className="block text-sm font-medium text-foreground">
                  OpenAI API Key
                </label>
                <span className="text-xs text-muted-foreground">Required for GPT models</span>
              </div>
              <div className="relative">
                <input
                  id="openaiKey"
                  type={showOpenaiKey ? 'text' : 'password'}
                  value={settings.openaiKey}
                  onChange={(e) => handleChange('openaiKey', e.target.value)}
                  placeholder="sk-proj-..."
                  className="w-full rounded-md border border-border bg-input pl-12 pr-48 py-9 text-sm text-foreground focus-ring font-code"
                />
                <button
                  type="button"
                  onClick={() => setShowOpenaiKey(!showOpenaiKey)}
                  className="absolute right-12 top-1/2 -translate-y-1/2 p-6 text-muted-foreground hover:text-foreground transition-smooth"
                  aria-label={showOpenaiKey ? "Hide key" : "Show key"}
                >
                  <Icon name={showOpenaiKey ? 'EyeSlashIcon' : 'EyeIcon'} size={18} />
                </button>
              </div>
            </div>

            {/* Anthropic API Key */}
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <label htmlFor="anthropicKey" className="block text-sm font-medium text-foreground">
                  Anthropic Claude API Key
                </label>
                <span className="text-xs text-muted-foreground">Required for Claude models</span>
              </div>
              <div className="relative">
                <input
                  id="anthropicKey"
                  type={showAnthropicKey ? 'text' : 'password'}
                  value={settings.anthropicKey}
                  onChange={(e) => handleChange('anthropicKey', e.target.value)}
                  placeholder="sk-ant-..."
                  className="w-full rounded-md border border-border bg-input pl-12 pr-48 py-9 text-sm text-foreground focus-ring font-code"
                />
                <button
                  type="button"
                  onClick={() => setShowAnthropicKey(!showAnthropicKey)}
                  className="absolute right-12 top-1/2 -translate-y-1/2 p-6 text-muted-foreground hover:text-foreground transition-smooth"
                  aria-label={showAnthropicKey ? "Hide key" : "Show key"}
                >
                  <Icon name={showAnthropicKey ? 'EyeSlashIcon' : 'EyeIcon'} size={18} />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Submit Actions */}
        <div className="flex justify-end gap-12">
          <button
            type="submit"
            disabled={saving}
            className="py-12 px-24 rounded-md bg-primary hover:bg-primary/90 text-primary-foreground font-medium transition-smooth flex items-center gap-12 focus-ring disabled:opacity-50"
          >
            {saving ? (
              <span className="w-18 h-18 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
            ) : (
              <Icon name="CheckIcon" size={18} />
            )}
            Save Configuration
          </button>
        </div>
      </form>
    </div>
  );
}

