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

interface Question {
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

const mockQuestions: Question[] = [
  {
    id: 'q-001',
    title: 'Implement a LRU Cache with O(1) Operations',
    category: 'Data Structures',
    subCategory: 'Hash Maps & Linked Lists',
    difficulty: 'Hard',
    dateEncountered: '01/28/2026',
    content: `Design and implement a data structure for Least Recently Used (LRU) cache. It should support the following operations: get and put.\n\nget(key) - Get the value (will always be positive) of the key if the key exists in the cache, otherwise return -1.\nput(key, value) - Set or insert the value if the key is not already present. When the cache reached its capacity, it should invalidate the least recently used item before inserting a new item.\n\nThe cache is initialized with a positive capacity.\n\nFollow up:\nCould you do both operations in O(1) time complexity?`,
    tags: ['hash-map', 'doubly-linked-list', 'design', 'cache'],
    userResponse: `I would use a combination of a hash map and a doubly linked list to achieve O(1) time complexity for both operations.\n\nThe hash map stores key-value pairs where the value is a pointer to a node in the doubly linked list. The doubly linked list maintains the order of usage, with the most recently used item at the head and the least recently used at the tail.\n\nFor get(key):\n1. Check if key exists in hash map\n2. If yes, move the corresponding node to the head of the list\n3. Return the value\n4. If no, return -1\n\nFor put(key, value):\n1. If key exists, update value and move to head\n2. If key doesn't exist:\n   - Create new node\n   - Add to hash map\n   - Add to head of list\n   - If capacity exceeded, remove tail node and its hash map entry`,
    feedback: {
      strengths: [
        'Correctly identified the need for both hash map and doubly linked list',
        'Understood the O(1) time complexity requirement',
        'Clear explanation of the data structure choice',
        'Covered both get and put operations systematically',
      ],
      improvements: [
        'Missing implementation details for moving nodes in the doubly linked list',
        'Did not mention sentinel nodes (dummy head/tail) for easier edge case handling',
        'Could elaborate on why doubly linked list is preferred over singly linked list',
        'No discussion of thread safety or concurrent access considerations',
      ],
      technicalDepth: [
        'Explain the pointer manipulation required when moving a node to the head',
        'Discuss the trade-off between space complexity (O(n)) and time complexity (O(1))',
        'Mention how to handle the case when capacity is 0 or 1',
        'Consider discussing alternative implementations like OrderedDict in Python',
      ],
      bestPractices: [
        'Always validate input parameters (null checks, capacity validation)',
        'Use sentinel nodes to simplify edge case handling',
        'Consider implementing a separate Node class for better encapsulation',
        'Add comprehensive unit tests covering edge cases',
      ],
    },
    relatedQuestions: [
      {
        id: 'q-002',
        title: 'Design LFU Cache',
        category: 'Data Structures',
        difficulty: 'Hard',
        similarity: 85,
      },
      {
        id: 'q-003',
        title: 'Implement a Time-based Key-Value Store',
        category: 'Data Structures',
        difficulty: 'Medium',
        similarity: 72,
      },
      {
        id: 'q-004',
        title: 'Design In-Memory File System',
        category: 'System Design',
        difficulty: 'Hard',
        similarity: 68,
      },
    ],
    performanceMetrics: {
      attempts: [
        { date: '01/28/2026', score: 65, timeSpent: '45 min' },
        { date: '01/30/2026', score: 78, timeSpent: '38 min' },
        { date: '02/02/2026', score: 85, timeSpent: '32 min' },
      ],
      improvementAreas: [
        'Edge case handling',
        'Code optimization',
        'Time complexity analysis',
      ],
    },
    interviewerPerspective: {
      whatInterviewersLookFor: [
        'Understanding of hash map and linked list data structures',
        'Ability to achieve O(1) time complexity for both operations',
        'Clear explanation of design choices and trade-offs',
        'Consideration of edge cases and boundary conditions',
        'Clean, maintainable code with proper encapsulation',
      ],
      commonMistakes: [
        'Using only a hash map without maintaining access order',
        'Implementing with O(n) time complexity for one or both operations',
        'Forgetting to update the linked list when accessing existing keys',
        'Not handling the capacity limit correctly',
        'Poor variable naming and code organization',
      ],
      realWorldApplication: `LRU caches are fundamental to many production systems:\n\n• Web browsers use LRU caching for recently visited pages and resources\n• Database systems implement LRU for buffer pool management\n• Operating systems use LRU for page replacement in virtual memory\n• CDNs employ LRU strategies for content caching\n• Redis and Memcached use variations of LRU for memory management\n\nUnderstanding LRU cache implementation demonstrates your ability to optimize for both time and space complexity, a critical skill for building scalable systems.`,
    },
    isMastered: false,
    isInReviewList: true,
  },
  {
    id: 'q-005',
    title: 'Describe a Time You Led a Cross-Functional Team',
    category: 'Behavioral',
    subCategory: 'Leadership',
    difficulty: 'Medium',
    dateEncountered: '01/25/2026',
    content: `Tell me about a time when you had to lead a cross-functional team to deliver a critical project. How did you handle conflicting priorities and ensure successful delivery?`,
    tags: ['leadership', 'teamwork', 'communication', 'project-management'],
    userResponse: `In my previous role, I led a team of 8 people from engineering, design, and product to launch a new feature within a tight 6-week deadline. We had conflicting priorities initially, with engineering wanting more time for testing and product pushing for faster delivery.\n\nI organized daily standups and weekly alignment meetings to ensure everyone was on the same page. We created a shared roadmap and prioritized features based on user impact. When conflicts arose, I facilitated discussions to find compromises that satisfied all stakeholders.\n\nThe project was delivered on time with 95% test coverage and received positive user feedback.`,
    feedback: {
      strengths: [
        'Provided specific context with team size and timeline',
        'Mentioned concrete actions taken (standups, alignment meetings)',
        'Included measurable outcomes (95% test coverage, on-time delivery)',
        'Addressed the conflict resolution aspect of the question',
      ],
      improvements: [
        'Could provide more detail about the specific conflict and how it was resolved',
        'Missing personal leadership qualities demonstrated',
        'No mention of challenges faced or lessons learned',
        'Could elaborate on how you measured success beyond delivery',
      ],
      starGuidance: {
        situation: 'Set the context more vividly: "At Company X, we were launching a critical payment feature that required coordination between 3 engineering teams, 2 designers, and product management. The feature was essential for Q4 revenue targets, but we had only 6 weeks before the holiday freeze."',
        task: 'Clarify your specific responsibility: "As the technical lead, I was responsible for coordinating all technical decisions, resolving conflicts between teams, and ensuring we met both quality standards and the aggressive timeline."',
        action: 'Provide more specific actions: "I implemented a three-pronged approach: (1) Created a shared Slack channel for real-time communication, (2) Established a decision-making framework where engineering had final say on technical debt but product owned feature prioritization, (3) Set up bi-weekly demos to stakeholders to maintain transparency and gather early feedback."',
        result: 'Quantify impact more comprehensively: "We delivered the feature 2 days ahead of schedule with 95% test coverage. The feature processed $2M in transactions in the first month with zero critical bugs. The cross-functional collaboration model I established became the template for future projects, reducing average project delivery time by 20%."',
      },
    },
    relatedQuestions: [
      {
        id: 'q-006',
        title: 'Tell Me About a Time You Had to Make a Difficult Decision',
        category: 'Behavioral',
        difficulty: 'Medium',
        similarity: 78,
      },
      {
        id: 'q-007',
        title: 'Describe a Situation Where You Had to Influence Without Authority',
        category: 'Behavioral',
        difficulty: 'Hard',
        similarity: 82,
      },
      {
        id: 'q-008',
        title: 'How Do You Handle Disagreements with Team Members?',
        category: 'Behavioral',
        difficulty: 'Easy',
        similarity: 65,
      },
    ],
    performanceMetrics: {
      attempts: [
        { date: '01/25/2026', score: 70, timeSpent: '12 min' },
        { date: '01/29/2026', score: 82, timeSpent: '10 min' },
      ],
      improvementAreas: [
        'STAR structure',
        'Quantifiable results',
        'Leadership qualities',
      ],
    },
    interviewerPerspective: {
      whatInterviewersLookFor: [
        'Clear demonstration of leadership skills and initiative',
        'Ability to navigate complex interpersonal dynamics',
        'Evidence of strategic thinking and prioritization',
        'Measurable impact and outcomes',
        'Self-awareness and learning from experiences',
        'Communication and stakeholder management skills',
      ],
      commonMistakes: [
        'Providing vague or generic examples without specific details',
        'Focusing too much on the team and not enough on personal contributions',
        'Not following the STAR format (Situation, Task, Action, Result)',
        'Failing to quantify results or demonstrate impact',
        'Not addressing the conflict resolution aspect of the question',
        'Speaking negatively about team members or stakeholders',
      ],
      realWorldApplication: `Leadership and cross-functional collaboration are essential in modern software engineering:\n\n• Senior engineers regularly lead initiatives spanning multiple teams\n• Technical decisions often require buy-in from product, design, and business stakeholders\n• Successful projects depend on effective communication and conflict resolution\n• Engineering leaders must balance technical excellence with business priorities\n• Career advancement beyond senior IC roles requires demonstrated leadership\n\nThis question assesses your readiness for senior technical roles where leadership and influence are as important as technical skills.`,
    },
    isMastered: false,
    isInReviewList: false,
  },
];

function QuestionReviewContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isHydrated, setIsHydrated] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState<Question>(mockQuestions[0]);

  useEffect(() => {
    setIsHydrated(true);
    const questionId = searchParams.get('id');
    if (questionId) {
      const question = mockQuestions.find((q) => q.id === questionId);
      if (question) {
        setCurrentQuestion(question);
      }
    }
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

  const handleToggleMastered = () => {
    setCurrentQuestion((prev) => ({
      ...prev,
      isMastered: !prev.isMastered,
    }));
  };

  if (!isHydrated) {
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