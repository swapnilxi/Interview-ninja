'use client';

import { createClient } from '@/lib/supabase/client';

export interface Question {
  id: string;
  questionText: string;
  category: string;
  subType: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  questionType: string;
  dateEncountered: string;
  lastReviewed: string | null;
  userPerformance?: number;
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

function mapRow(row: any): Question {
  return {
    id: row.id,
    questionText: row.question_text,
    category: row.category,
    subType: row.sub_type,
    difficulty: row.difficulty as 'Easy' | 'Medium' | 'Hard',
    questionType: row.question_type,
    dateEncountered: row.date_encountered,
    lastReviewed: row.last_reviewed,
    userPerformance: row.user_performance,
  };
}

export const questionsService = {
  async getAll(): Promise<Question[]> {
    const supabase = createClient();
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return [];

    try {
      const { data, error } = await supabase
        .from('questions')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false });

      if (error) {
        if (isSchemaError(error)) throw error;
        return [];
      }

      return data?.map(mapRow) || [];
    } catch (error: any) {
      if (isSchemaError(error)) throw error;
      return [];
    }
  },

  async upsertMany(questions: Omit<Question, 'id'>[]): Promise<void> {
    const supabase = createClient();
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return;

    try {
      const rows = questions.map((q) => ({
        user_id: user.id,
        question_text: q.questionText,
        category: q.category,
        sub_type: q.subType,
        difficulty: q.difficulty,
        question_type: q.questionType,
        date_encountered: q.dateEncountered,
        last_reviewed: q.lastReviewed,
        user_performance: q.userPerformance,
      }));

      const { error } = await supabase.from('questions').insert(rows);

      if (error) {
        if (isSchemaError(error)) throw error;
      }
    } catch (error: any) {
      if (isSchemaError(error)) throw error;
    }
  },

  async updatePerformance(id: string, performance: number): Promise<void> {
    const supabase = createClient();
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return;

    try {
      const { error } = await supabase
        .from('questions')
        .update({ user_performance: performance, last_reviewed: new Date().toISOString().split('T')[0] })
        .eq('id', id)
        .eq('user_id', user.id);

      if (error) {
        if (isSchemaError(error)) throw error;
      }
    } catch (error: any) {
      if (isSchemaError(error)) throw error;
    }
  },
};
