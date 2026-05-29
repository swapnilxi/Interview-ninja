'use client';

import { createClient } from '@/lib/supabase/client';

export interface UserSettings {
  questionModel: string;
  answerModel: string;
  openaiKey: string;
  geminiKey: string;
  anthropicKey: string;
}

function isSchemaError(error: any): boolean {
  if (!error) return false;
  if (error.code && typeof error.code === 'string') {
    const errorClass = error.code.substring(0, 2);
    if (errorClass === '42' || errorClass === '08') return true;
    if (errorClass === '23') return false;
  }
  if (error.message) {
    const schemaErrorPatterns = [
      /relation.*does not exist/i,
      /column.*does not exist/i,
      /function.*does not exist/i,
      /syntax error/i,
    ];
    return schemaErrorPatterns.some((p) => p.test(error.message));
  }
  return false;
}

export const settingsService = {
  async getSettings(): Promise<UserSettings | null> {
    const supabase = createClient();
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return null;

    try {
      const { data, error } = await supabase
        .from('user_settings')
        .select('*')
        .eq('user_id', user.id)
        .maybeSingle();

      if (error) {
        if (isSchemaError(error)) throw error;
        return null;
      }

      if (!data) return null;

      return {
        questionModel: data.question_model,
        answerModel: data.answer_model,
        openaiKey: data.openai_key || '',
        geminiKey: data.gemini_key || '',
        anthropicKey: data.anthropic_key || '',
      };
    } catch (error: any) {
      if (isSchemaError(error)) throw error;
      return null;
    }
  },

  async saveSettings(settings: UserSettings): Promise<void> {
    const supabase = createClient();
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) throw new Error('Not authenticated');

    try {
      const { error } = await supabase
        .from('user_settings')
        .upsert(
          {
            user_id: user.id,
            question_model: settings.questionModel,
            answer_model: settings.answerModel,
            openai_key: settings.openaiKey,
            gemini_key: settings.geminiKey,
            anthropic_key: settings.anthropicKey,
            updated_at: new Date().toISOString(),
          },
          { onConflict: 'user_id' }
        );

      if (error) {
        if (isSchemaError(error)) throw error;
        throw new Error(error.message);
      }
    } catch (error: any) {
      if (isSchemaError(error)) throw error;
      throw error;
    }
  },
};
