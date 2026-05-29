'use client';

import { useState, useEffect, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import QuestionFilterToolbar from '@/components/common/QuestionFilterToolbar';
import QuestionTableRow from './QuestionTableRow';
import QuestionTableMobile from './QuestionTableMobile';
import QuestionStatsPanel from './QuestionStatsPanel';
import BulkActionsBar from './BulkActionsBar';
import SortControls from './SortControls';
import EmptyState from './EmptyState';


interface Question {
  id: string;
  questionText: string;
  category: 'Interview' | 'CV Skill';
  subType: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  dateEncountered: string;
  lastReviewed: string | null;
  userPerformance?: number;
}

interface FilterOptions {
  category: string;
  difficulty: string;
  dateRange: string;
  searchQuery: string;
}

const mockQuestions: Question[] = [
  {
    id: 'q1',
    questionText: 'Design a distributed rate limiter system that can handle 100,000 requests per second across multiple data centers with eventual consistency guarantees.',
    category: 'Interview',
    subType: 'System Design',
    difficulty: 'Hard',
    dateEncountered: '2026-01-28',
    lastReviewed: '2026-02-01',
    userPerformance: 4,
  },
  {
    id: 'q2',
    questionText: 'Implement a binary search tree with insert, delete, and search operations. Analyze the time complexity for each operation.',
    category: 'Interview',
    subType: 'Data Structures',
    difficulty: 'Medium',
    dateEncountered: '2026-01-27',
    lastReviewed: '2026-01-30',
    userPerformance: 5,
  },
  {
    id: 'q3',
    questionText: 'Explain the architecture and training process for YOLO (You Only Look Once) object detection model. How does it differ from R-CNN family of models?',
    category: 'CV Skill',
    subType: 'Deep Learning Vision',
    difficulty: 'Hard',
    dateEncountered: '2026-01-26',
    lastReviewed: null,
    userPerformance: 3,
  },
  {
    id: 'q4',
    questionText: 'Describe a situation where you had to make a difficult technical decision with limited information. What was your approach and outcome?',
    category: 'Interview',
    subType: 'Behavioral',
    difficulty: 'Medium',
    dateEncountered: '2026-01-25',
    lastReviewed: '2026-01-29',
    userPerformance: 4,
  },
  {
    id: 'q5',
    questionText: 'Implement the Canny edge detection algorithm from scratch. Explain each step and its mathematical foundation.',
    category: 'CV Skill',
    subType: 'Classical CV',
    difficulty: 'Hard',
    dateEncountered: '2026-01-24',
    lastReviewed: '2026-01-31',
    userPerformance: 3,
  },
  {
    id: 'q6',
    questionText: 'Write a function to find the longest palindromic substring in a given string. Optimize for both time and space complexity.',
    category: 'Interview',
    subType: 'Algorithms',
    difficulty: 'Medium',
    dateEncountered: '2026-01-23',
    lastReviewed: '2026-01-28',
    userPerformance: 5,
  },
  {
    id: 'q7',
    questionText: 'Design a real-time video analytics pipeline for detecting and tracking multiple objects in surveillance footage. Consider scalability and latency requirements.',
    category: 'CV Skill',
    subType: 'CV Deployment',
    difficulty: 'Hard',
    dateEncountered: '2026-01-22',
    lastReviewed: null,
    userPerformance: 4,
  },
  {
    id: 'q8',
    questionText: 'Explain how you would design a URL shortening service like bit.ly. Include database schema, API design, and scaling considerations.',
    category: 'Interview',
    subType: 'System Design',
    difficulty: 'Medium',
    dateEncountered: '2026-01-21',
    lastReviewed: '2026-01-27',
    userPerformance: 4,
  },
  {
    id: 'q9',
    questionText: 'Implement a custom training loop for a semantic segmentation model using PyTorch. Include data augmentation, loss calculation, and metrics tracking.',
    category: 'CV Skill',
    subType: 'CV Training Strategy',
    difficulty: 'Hard',
    dateEncountered: '2026-01-20',
    lastReviewed: '2026-01-26',
    userPerformance: 5,
  },
  {
    id: 'q10',
    questionText: 'Tell me about a time when you had to lead a team through a challenging project. How did you handle conflicts and ensure successful delivery?',
    category: 'Interview',
    subType: 'Leadership',
    difficulty: 'Medium',
    dateEncountered: '2026-01-19',
    lastReviewed: '2026-01-25',
    userPerformance: 4,
  },
  {
    id: 'q11',
    questionText: 'Design and implement a LRU (Least Recently Used) cache with O(1) time complexity for both get and put operations.',
    category: 'Interview',
    subType: 'Data Structures',
    difficulty: 'Hard',
    dateEncountered: '2026-01-18',
    lastReviewed: null,
    userPerformance: 3,
  },
  {
    id: 'q12',
    questionText: 'Explain the concept of transfer learning in computer vision. Provide examples of when to use fine-tuning vs feature extraction.',
    category: 'CV Skill',
    subType: 'Deep Learning Vision',
    difficulty: 'Medium',
    dateEncountered: '2026-01-17',
    lastReviewed: '2026-01-24',
    userPerformance: 5,
  },
  {
    id: 'q13',
    questionText: 'Implement Dijkstra\'s shortest path algorithm and analyze its time complexity. How would you optimize it for sparse graphs?',
    category: 'Interview',
    subType: 'Algorithms',
    difficulty: 'Medium',
    dateEncountered: '2026-01-16',
    lastReviewed: '2026-01-23',
    userPerformance: 4,
  },
  {
    id: 'q14',
    questionText: 'Design a model optimization strategy to reduce inference time by 50% while maintaining 95% of original accuracy for a mobile deployment.',
    category: 'CV Skill',
    subType: 'CV Optimization',
    difficulty: 'Hard',
    dateEncountered: '2026-01-15',
    lastReviewed: '2026-01-22',
    userPerformance: 4,
  },
  {
    id: 'q15',
    questionText: 'Describe your approach to mentoring junior engineers. How do you balance guidance with allowing them to learn from mistakes?',
    category: 'Interview',
    subType: 'Leadership',
    difficulty: 'Easy',
    dateEncountered: '2026-01-14',
    lastReviewed: '2026-01-21',
    userPerformance: 5,
  },
];

export default function QuestionBankInteractive() {
  const router = useRouter();
  const [isHydrated, setIsHydrated] = useState(false);
  const [filters, setFilters] = useState<FilterOptions>({
    category: 'All Categories',
    difficulty: 'All Levels',
    dateRange: 'All Time',
    searchQuery: '',
  });
  const [sortBy, setSortBy] = useState('dateEncountered');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [selectedQuestions, setSelectedQuestions] = useState<string[]>([]);
  const [selectAll, setSelectAll] = useState(false);

  useEffect(() => {
    setIsHydrated(true);
  }, []);

  const filteredQuestions = useMemo(() => {
    let filtered = [...mockQuestions];

    if (filters.category !== 'All Categories') {
      filtered = filtered.filter((q) => q.category === filters.category);
    }

    if (filters.difficulty !== 'All Levels') {
      filtered = filtered.filter((q) => q.difficulty === filters.difficulty);
    }

    if (filters.searchQuery) {
      const query = filters.searchQuery.toLowerCase();
      filtered = filtered.filter(
        (q) =>
          q.questionText.toLowerCase().includes(query) ||
          q.subType.toLowerCase().includes(query)
      );
    }

    if (filters.dateRange !== 'All Time') {
      const now = new Date();
      const cutoffDate = new Date();

      switch (filters.dateRange) {
        case 'Last 7 Days':
          cutoffDate.setDate(now.getDate() - 7);
          break;
        case 'Last 30 Days':
          cutoffDate.setDate(now.getDate() - 30);
          break;
        case 'Last 90 Days':
          cutoffDate.setDate(now.getDate() - 90);
          break;
        case 'This Year':
          cutoffDate.setMonth(0, 1);
          break;
      }

      filtered = filtered.filter(
        (q) => new Date(q.dateEncountered) >= cutoffDate
      );
    }

    filtered.sort((a, b) => {
      let aValue: any = a[sortBy as keyof Question];
      let bValue: any = b[sortBy as keyof Question];

      if (sortBy === 'difficulty') {
        const difficultyOrder = { Easy: 1, Medium: 2, Hard: 3 };
        aValue = difficultyOrder[a.difficulty];
        bValue = difficultyOrder[b.difficulty];
      }

      if (sortBy === 'performance') {
        aValue = a.userPerformance || 0;
        bValue = b.userPerformance || 0;
      }

      if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });

    return filtered;
  }, [filters, sortBy, sortOrder]);

  const stats = useMemo(() => {
    const total = mockQuestions.length;
    const interview = mockQuestions.filter((q) => q.category === 'Interview').length;
    const cvSkill = mockQuestions.filter((q) => q.category === 'CV Skill').length;
    const easy = mockQuestions.filter((q) => q.difficulty === 'Easy').length;
    const medium = mockQuestions.filter((q) => q.difficulty === 'Medium').length;
    const hard = mockQuestions.filter((q) => q.difficulty === 'Hard').length;

    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    const reviewedThisWeek = mockQuestions.filter(
      (q) => q.lastReviewed && new Date(q.lastReviewed) >= weekAgo
    ).length;

    const performanceScores = mockQuestions
      .filter((q) => q.userPerformance !== undefined)
      .map((q) => q.userPerformance!);
    const avgPerformance =
      performanceScores.length > 0
        ? performanceScores.reduce((a, b) => a + b, 0) / performanceScores.length
        : 0;

    return {
      totalQuestions: total,
      interviewQuestions: interview,
      cvSkillQuestions: cvSkill,
      easyQuestions: easy,
      mediumQuestions: medium,
      hardQuestions: hard,
      reviewedThisWeek,
      averagePerformance: avgPerformance,
    };
  }, []);

  const handleFilterChange = (newFilters: FilterOptions) => {
    setFilters(newFilters);
    setSelectedQuestions([]);
    setSelectAll(false);
  };

  const handleSortChange = (newSortBy: string) => {
    setSortBy(newSortBy);
  };

  const handleOrderChange = () => {
    setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
  };

  const handleSelectQuestion = (questionId: string) => {
    setSelectedQuestions((prev) =>
      prev.includes(questionId)
        ? prev.filter((id) => id !== questionId)
        : [...prev, questionId]
    );
  };

  const handleSelectAll = () => {
    if (selectAll) {
      setSelectedQuestions([]);
    } else {
      setSelectedQuestions(filteredQuestions.map((q) => q.id));
    }
    setSelectAll(!selectAll);
  };

  const handleReview = (questionId: string) => {
    router.push(`/question-review?id=${questionId}`);
  };

  const handlePractice = (questionId: string) => {
    router.push(`/daily-session?practice=${questionId}`);
  };

  const handleExport = () => {
    const selectedQuestionsData = mockQuestions.filter((q) =>
      selectedQuestions.includes(q.id)
    );

    const markdown = `# Question Bank Export\n\nExported on: ${new Date().toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    })}\n\nTotal Questions: ${selectedQuestionsData.length}\n\n---\n\n${selectedQuestionsData
      .map(
        (q, index) =>
          `## Question ${index + 1}\n\n**Category:** ${q.category}\n**Sub-Type:** ${q.subType}\n**Difficulty:** ${q.difficulty}\n**Date Encountered:** ${q.dateEncountered}\n\n${q.questionText}\n\n---\n`
      )
      .join('\n')}`;

    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `question-bank-export-${new Date().toISOString().split('T')[0]}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleMarkForReview = () => {
    console.log('Marking questions for review:', selectedQuestions);
    setSelectedQuestions([]);
    setSelectAll(false);
  };

  const handleClearSelection = () => {
    setSelectedQuestions([]);
    setSelectAll(false);
  };

  const handleClearFilters = () => {
    setFilters({
      category: 'All Categories',
      difficulty: 'All Levels',
      dateRange: 'All Time',
      searchQuery: '',
    });
  };

  const hasActiveFilters =
    filters.category !== 'All Categories' ||
    filters.difficulty !== 'All Levels' ||
    filters.dateRange !== 'All Time' ||
    filters.searchQuery !== '';

  if (!isHydrated) {
    return (
      <div className="min-h-screen bg-background pt-[60px]">
        <div className="max-w-[1400px] mx-auto px-24 py-36">
          <div className="animate-pulse space-y-24">
            <div className="h-48 bg-muted rounded-lg w-1/3" />
            <div className="h-96 bg-muted rounded-lg" />
            <div className="h-[600px] bg-muted rounded-lg" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background pt-[60px]">
      <div className="max-w-[1400px] mx-auto px-24 py-36">
        <div className="mb-36">
          <h1 className="font-heading text-4xl font-semibold text-foreground mb-12">
            Question Bank
          </h1>
          <p className="text-muted-foreground font-body">
            Review and practice previously encountered questions to reinforce your skills
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-24">
          <div className="lg:col-span-3 space-y-24">
            <QuestionFilterToolbar
              onFilterChange={handleFilterChange}
              categories={['All Categories', 'Interview', 'CV Skill']}
              difficulties={['All Levels', 'Easy', 'Medium', 'Hard']}
            />

            {filteredQuestions.length > 0 ? (
              <>
                <div className="bg-card rounded-lg shadow-md border border-border overflow-hidden">
                  <div className="p-24 border-b border-border">
                    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-18">
                      <div className="flex items-center gap-12">
                        <h2 className="font-heading text-lg font-medium text-foreground">
                          Questions
                        </h2>
                        <span className="px-12 py-6 rounded-md bg-primary/10 text-primary text-sm font-medium font-code">
                          {filteredQuestions.length}
                        </span>
                      </div>
                      <SortControls
                        sortBy={sortBy}
                        sortOrder={sortOrder}
                        onSortChange={handleSortChange}
                        onOrderChange={handleOrderChange}
                      />
                    </div>
                  </div>

                  <div className="hidden lg:block overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-muted/50 border-b border-border">
                        <tr>
                          <th className="px-18 py-12 text-left">
                            <input
                              type="checkbox"
                              checked={selectAll}
                              onChange={handleSelectAll}
                              className="w-18 h-18 rounded border-2 border-border bg-input checked:bg-primary checked:border-primary transition-smooth cursor-pointer focus-ring"
                              aria-label="Select all questions"
                            />
                          </th>
                          <th className="px-18 py-12 text-left text-sm font-medium text-muted-foreground font-heading">
                            Question
                          </th>
                          <th className="px-18 py-12 text-left text-sm font-medium text-muted-foreground font-heading">
                            Category
                          </th>
                          <th className="px-18 py-12 text-left text-sm font-medium text-muted-foreground font-heading">
                            Sub-Type
                          </th>
                          <th className="px-18 py-12 text-left text-sm font-medium text-muted-foreground font-heading">
                            Difficulty
                          </th>
                          <th className="px-18 py-12 text-left text-sm font-medium text-muted-foreground font-heading">
                            Date
                          </th>
                          <th className="px-18 py-12 text-left text-sm font-medium text-muted-foreground font-heading">
                            Last Reviewed
                          </th>
                          <th className="px-18 py-12 text-left text-sm font-medium text-muted-foreground font-heading">
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredQuestions.map((question) => (
                          <QuestionTableRow
                            key={question.id}
                            question={question}
                            onReview={handleReview}
                            onPractice={handlePractice}
                            isSelected={selectedQuestions.includes(question.id)}
                            onSelect={handleSelectQuestion}
                          />
                        ))}
                      </tbody>
                    </table>
                  </div>

                  <div className="lg:hidden p-18">
                    <QuestionTableMobile
                      questions={filteredQuestions}
                      onReview={handleReview}
                      onPractice={handlePractice}
                      selectedQuestions={selectedQuestions}
                      onSelect={handleSelectQuestion}
                    />
                  </div>
                </div>
              </>
            ) : (
              <EmptyState
                hasFilters={hasActiveFilters}
                onClearFilters={handleClearFilters}
              />
            )}
          </div>

          <div className="lg:col-span-1">
            <QuestionStatsPanel stats={stats} activeFilters={filters} />
          </div>
        </div>

        <BulkActionsBar
          selectedCount={selectedQuestions.length}
          onExport={handleExport}
          onMarkForReview={handleMarkForReview}
          onClearSelection={handleClearSelection}
        />
      </div>
    </div>
  );
}