'use client';

import { createClient } from '@/lib/supabase/client';

export interface SessionAnswer {
  questionId?: string;
  questionText: string;
  answerText: string;
  category: string;
  difficulty: string;
  questionType: string;
  isCompleted: boolean;
  sessionDate: string;
}

export interface SessionProgressRow {
  id: string;
  sessionDate: string;
  questionText: string;
  answerText: string;
  category: string;
  difficulty: string;
  questionType: string;
  isCompleted: boolean;
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
      /syntax error/i,
    ];
    return schemaErrorPatterns.some((p) => p.test(error.message));
  }
  return false;
}

export const sessionService = {
  async saveSessionAnswers(answers: SessionAnswer[]): Promise<void> {
    const supabase = createClient();
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return;

    try {
      const rows = answers.map((a) => ({
        user_id: user.id,
        session_date: a.sessionDate,
        question_id: a.questionId || null,
        question_text: a.questionText,
        answer_text: a.answerText,
        category: a.category,
        difficulty: a.difficulty,
        question_type: a.questionType,
        is_completed: a.isCompleted,
      }));

      const { error } = await supabase.from('session_progress').upsert(rows, {
        onConflict: 'id',
      });

      if (error) {
        if (isSchemaError(error)) throw error;
      }
    } catch (error: any) {
      if (isSchemaError(error)) throw error;
    }
  },

  async getSessionByDate(date: string): Promise<SessionProgressRow[]> {
    const supabase = createClient();
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return [];

    try {
      const { data, error } = await supabase
        .from('session_progress')
        .select('*')
        .eq('user_id', user.id)
        .eq('session_date', date)
        .order('created_at', { ascending: true });

      if (error) {
        if (isSchemaError(error)) throw error;
        return [];
      }

      return (
        data?.map((row) => ({
          id: row.id,
          sessionDate: row.session_date,
          questionText: row.question_text,
          answerText: row.answer_text,
          category: row.category,
          difficulty: row.difficulty,
          questionType: row.question_type,
          isCompleted: row.is_completed,
        })) || []
      );
    } catch (error: any) {
      if (isSchemaError(error)) throw error;
      return [];
    }
  },

  async getProgressStats(userId?: string): Promise<{
    totalSessions: number;
    totalAnswered: number;
    completedAnswers: number;
    recentDates: string[];
  }> {
    const supabase = createClient();
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return { totalSessions: 0, totalAnswered: 0, completedAnswers: 0, recentDates: [] };

    try {
      const { data, error } = await supabase
        .from('session_progress')
        .select('session_date, is_completed')
        .eq('user_id', user.id)
        .order('session_date', { ascending: false });

      if (error) {
        if (isSchemaError(error)) throw error;
        return { totalSessions: 0, totalAnswered: 0, completedAnswers: 0, recentDates: [] };
      }

      const uniqueDates = [...new Set(data?.map((r) => r.session_date) || [])];
      const completed = data?.filter((r) => r.is_completed).length || 0;

      return {
        totalSessions: uniqueDates.length,
        totalAnswered: data?.length || 0,
        completedAnswers: completed,
        recentDates: uniqueDates.slice(0, 7),
      };
    } catch (error: any) {
      if (isSchemaError(error)) throw error;
      return { totalSessions: 0, totalAnswered: 0, completedAnswers: 0, recentDates: [] };
    }
  },
};
