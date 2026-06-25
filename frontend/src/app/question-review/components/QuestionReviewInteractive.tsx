'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Suspense } from 'react';
import QuestionDetailCard from './QuestionDetailCard';
import ResponseEditor from './ResponseEditor';
import FeedbackPanel from './FeedbackPanel';
import RelatedQuestionsCard from './RelatedQuestionsCard';
import PerformanceMetricsCard from './PerformanceMetricsCard';
import ActionButtonsPanel from './ActionButtonsPanel';
import InterviewerPerspectiveCard from './InterviewerPerspectiveCard';
import { questionsService, Question as ServiceQuestion } from '@/lib/services/questionsService';

interface ReviewQuestion {
  id: string;
  title: string;
  category: string;
  subCategory: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  dateEncountered: string;
  content: string;
  tags: string[];
  userResponse: string;
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
  relatedQuestions: Array<{
    id: string;
    title: string;
    category: string;
    difficulty: 'Easy' | 'Medium' | 'Hard';
    similarity: number;
  }>;
  performanceMetrics: {
    attempts: Array<{
      date: string;
      score: number;
      timeSpent: string;
    }>;
    improvementAreas: string[];
  };
  interviewerPerspective: {
    whatInterviewersLookFor: string[];
    commonMistakes: string[];
    realWorldApplication: string;
  };
  isMastered: boolean;
  isInReviewList: boolean;
}

function mapBackendQuestionToReview(q: ServiceQuestion): ReviewQuestion {
  const tags = q.subType.split(' ').map((s) => s.toLowerCase()).filter(Boolean);

  return {
    id: q.id,
    title: `${q.subType} Core Practice`,
    category: q.category,
    subCategory: q.subType,
    difficulty: q.difficulty,
    dateEncountered: q.dateEncountered,
    content: q.questionText,
    tags: tags.length > 0 ? tags : ['interview'],
    userResponse: '',
    feedback: {
      strengths: ['Demonstrated initial structured reasoning', 'Identified primary design parameters'],
      improvements: ['Consider space optimization trade-offs under heavy throughput constraints'],
      starGuidance: {
        situation: 'Asked to analyze, design, or solve this engineering task.',
        task: 'Provide a robust, scale-aware solution covering standard edge cases.',
        action: 'Formulate structural blocks, compare choices, and implement cleanly.',
        result: 'Optimal complexity, minimized latency overhead, and robust correctness.',
      },
    },
    relatedQuestions: [],
    performanceMetrics: {
      attempts: [
        {
          date: q.dateEncountered,
          score: q.userPerformance !== undefined ? q.userPerformance * 20 : 80,
          timeSpent: '15 mins',
        },
      ],
      improvementAreas: ['Time complexity optimization', 'Production readiness design details'],
    },
    interviewerPerspective: {
      whatInterviewersLookFor: [
        'Problem-solving clarity',
        'Trade-off decisions rationale',
        'System constraints realization',
      ],
      commonMistakes: [
        'Skipping critical validation constraints',
        'Over-engineering the core solution baseline',
      ],
      realWorldApplication: 'Directly impacts application code reliability, performance limits, and resource efficiency.',
    },
    isMastered: q.userPerformance === 5,
    isInReviewList: false,
  };
}

function QuestionReviewContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isHydrated, setIsHydrated] = useState(false);
  const [questions, setQuestions] = useState<ReviewQuestion[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState<ReviewQuestion | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setIsHydrated(true);
    async function load() {
      try {
        const backendQs = await questionsService.getAll();
        const reviewQs = backendQs.map(mapBackendQuestionToReview);
        setQuestions(reviewQs);
        
        const questionId = searchParams.get('id');
        if (questionId) {
          const found = reviewQs.find((q) => q.id === questionId);
          if (found) {
            setCurrentQuestion(found);
          } else if (reviewQs.length > 0) {
            setCurrentQuestion(reviewQs[0]);
          }
        } else if (reviewQs.length > 0) {
          setCurrentQuestion(reviewQs[0]);
        }
      } catch (err) {
        console.error('Failed to load questions in review:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [searchParams]);

  const handleResponseUpdate = (response: string) => {
    setCurrentQuestion((prev) => ({
      ...prev,
      userResponse: response,
    }));
  };

  const handleQuestionSelect = (questionId: string) => {
    router.push(`/question-review?id=${questionId}`);
  };

  const handlePracticeSimilar = () => {
    router.push('/daily-session');
  };

  const handleToggleReviewList = () => {
    setCurrentQuestion((prev) => ({
      ...prev,
      isInReviewList: !prev.isInReviewList,
    }));
  };

  const handleToggleMastered = async () => {
    if (!currentQuestion) return;
    const newMastered = !currentQuestion.isMastered;
    const newPerformance = newMastered ? 5 : 3;
    try {
      await questionsService.updatePerformance(currentQuestion.id, newPerformance);
      setCurrentQuestion((prev) => {
        if (!prev) return null;
        return {
          ...prev,
          isMastered: newMastered,
          performanceMetrics: {
            ...prev.performanceMetrics,
            attempts: [
              ...prev.performanceMetrics.attempts,
              { date: new Date().toISOString().split('T')[0], score: newPerformance * 20, timeSpent: '5 mins' }
            ]
          }
        };
      });
    } catch (err) {
      console.error('Failed to update mastered state:', err);
    }
  };

  if (!isHydrated || loading || !currentQuestion) {
    return (
      <div className="min-h-screen bg-background pt-[60px]">
        <div className="max-w-[1400px] mx-auto px-24 py-36">
          <div className="flex items-center justify-center h-[400px]">
            <div className="w-48 h-48 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background pt-[60px]">
      <div className="max-w-[1400px] mx-auto px-24 py-36">
        <div className="mb-24">
          <button
            onClick={() => router.push('/question-bank')}
            className="
              flex items-center gap-6 text-sm text-muted-foreground
              hover:text-foreground transition-smooth
            "
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M10 12L6 8L10 4"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            Back to Question Bank
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-24">
          <div className="lg:col-span-2 space-y-24">
            <QuestionDetailCard question={currentQuestion} />
            <ResponseEditor
              initialResponse={currentQuestion.userResponse}
              onResponseUpdate={handleResponseUpdate}
              questionId={currentQuestion.id}
            />
            <FeedbackPanel
              feedback={currentQuestion.feedback}
              questionType={currentQuestion.category}
            />
            <InterviewerPerspectiveCard
              perspective={currentQuestion.interviewerPerspective}
            />
          </div>

          <div className="space-y-24">
            <ActionButtonsPanel
              questionId={currentQuestion.id}
              isMastered={currentQuestion.isMastered}
              isInReviewList={currentQuestion.isInReviewList}
              onPracticeSimilar={handlePracticeSimilar}
              onToggleReviewList={handleToggleReviewList}
              onToggleMastered={handleToggleMastered}
            />
            <PerformanceMetricsCard
              attempts={currentQuestion.performanceMetrics.attempts}
              improvementAreas={currentQuestion.performanceMetrics.improvementAreas}
            />
            <RelatedQuestionsCard
              questions={currentQuestion.relatedQuestions}
              onQuestionSelect={handleQuestionSelect}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="min-h-screen bg-background pt-[60px]">
      <div className="max-w-[1400px] mx-auto px-24 py-36">
        <div className="flex items-center justify-center h-[400px]">
          <div className="w-48 h-48 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
        </div>
      </div>
    </div>
  );
}

export default function QuestionReviewInteractive() {
  return (
    <Suspense fallback={<LoadingSkeleton />}>
      <QuestionReviewContent />
    </Suspense>
  );
}