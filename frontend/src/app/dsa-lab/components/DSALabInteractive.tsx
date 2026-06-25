'use client';

import { useState } from 'react';
import Icon from '@/components/ui/AppIcon';
import LabCopilot from '@/components/common/LabCopilot';
import OnDemandSection from '@/components/lab/OnDemandSection';
import QuizCarousel from '@/components/lab/QuizCarousel';

// ─── Types ───────────────────────────────────────────────────────────────────
interface DSAProblem {
  id: string;
  name: string;
  lcNumber: number | null;
  brief: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  pattern: string;
  tags: string[];
}
interface TopicGroup {
  id: string; label: string; icon: string;
  problems: DSAProblem[];
  references: { id: string; label: string }[];
}
interface SectionState { generated: boolean; generating: boolean; content: string }

// ─── Problem Data ─────────────────────────────────────────────────────────────
const TOPICS: TopicGroup[] = [
  {
    id: 'arrays', label: 'Arrays & Hashing', icon: 'TableCellsIcon',
    references: [
      { id: 'ref-hash', label: '📚 Hash Map Internals & Collision Resolution' },
      { id: 'ref-prefix', label: '📚 Prefix Sum Patterns' },
    ],
    problems: [
      { id: 'two-sum', name: 'Two Sum', lcNumber: 1, brief: 'Find two indices summing to target using hash map.', difficulty: 'Easy', pattern: 'Hash Map', tags: ['hash-map', 'complement'] },
      { id: 'top-k', name: 'Top K Frequent Elements', lcNumber: 347, brief: 'Return k most frequent elements via bucket sort.', difficulty: 'Medium', pattern: 'Bucket Sort / Heap', tags: ['hash-map', 'heap', 'bucket-sort'] },
      { id: 'product-except', name: 'Product of Array Except Self', lcNumber: 238, brief: 'Prefix+postfix product without division, O(n).', difficulty: 'Medium', pattern: 'Prefix/Postfix', tags: ['prefix-sum', 'arrays'] },
      { id: 'longest-consec', name: 'Longest Consecutive Sequence', lcNumber: 128, brief: 'O(n) solution using hash set streak detection.', difficulty: 'Hard', pattern: 'Hash Set', tags: ['hash-set', 'greedy'] },
    ],
  },
  {
    id: 'two-pointers', label: 'Two Pointers / Sliding Window', icon: 'ArrowsRightLeftIcon',
    references: [{ id: 'ref-sw', label: '📚 Sliding Window Patterns Catalog' }],
    problems: [
      { id: 'min-window', name: 'Minimum Window Substring', lcNumber: 76, brief: 'Smallest window containing all chars of t.', difficulty: 'Hard', pattern: 'Sliding Window', tags: ['sliding-window', 'hash-map'] },
      { id: 'longest-no-repeat', name: 'Longest Substring Without Repeating', lcNumber: 3, brief: 'Max length substring with no duplicates.', difficulty: 'Medium', pattern: 'Sliding Window', tags: ['sliding-window'] },
      { id: 'three-sum', name: '3Sum', lcNumber: 15, brief: 'Find all triplets summing to zero.', difficulty: 'Medium', pattern: 'Two Pointers', tags: ['two-pointers', 'sorting'] },
    ],
  },
  {
    id: 'binary-search', label: 'Binary Search', icon: 'MagnifyingGlassIcon',
    references: [{ id: 'ref-bs', label: '📚 Binary Search on Answer Pattern' }],
    problems: [
      { id: 'search-rotated', name: 'Search in Rotated Sorted Array', lcNumber: 33, brief: 'Binary search with rotated pivot detection.', difficulty: 'Medium', pattern: 'Binary Search', tags: ['binary-search'] },
      { id: 'median-two', name: 'Median of Two Sorted Arrays', lcNumber: 4, brief: 'O(log(m+n)) median via binary search partitioning.', difficulty: 'Hard', pattern: 'Binary Search', tags: ['binary-search', 'divide-conquer'] },
      { id: 'koko', name: 'Koko Eating Bananas', lcNumber: 875, brief: 'Binary search on answer for minimum eating speed.', difficulty: 'Medium', pattern: 'Binary Search on Answer', tags: ['binary-search-on-answer'] },
    ],
  },
  {
    id: 'trees', label: 'Trees & Graphs', icon: 'ShareIcon',
    references: [
      { id: 'ref-bfs-dfs', label: '📚 BFS vs DFS Decision Framework' },
      { id: 'ref-uf', label: '📚 Union-Find & Disjoint Sets' },
    ],
    problems: [
      { id: 'num-islands', name: 'Number of Islands', lcNumber: 200, brief: 'Count connected components via BFS/DFS.', difficulty: 'Medium', pattern: 'DFS / BFS', tags: ['graph', 'dfs', 'bfs'] },
      { id: 'course-schedule', name: 'Course Schedule', lcNumber: 207, brief: 'Cycle detection via topological sort.', difficulty: 'Medium', pattern: 'Topological Sort', tags: ['graph', 'topological-sort', 'cycle-detection'] },
      { id: 'lca', name: 'Lowest Common Ancestor of BST', lcNumber: 235, brief: 'Use BST property for efficient LCA.', difficulty: 'Medium', pattern: 'Tree DFS', tags: ['bst', 'dfs', 'tree'] },
      { id: 'word-ladder', name: 'Word Ladder', lcNumber: 127, brief: 'Shortest transformation sequence via BFS.', difficulty: 'Hard', pattern: 'BFS', tags: ['bfs', 'graph', 'string'] },
    ],
  },
  {
    id: 'dp', label: 'Dynamic Programming', icon: 'ChartBarIcon',
    references: [
      { id: 'ref-dp-patterns', label: '📚 DP Pattern Recognition Guide' },
      { id: 'ref-dp-opt', label: '📚 Space Optimization in DP' },
    ],
    problems: [
      { id: 'coin-change', name: 'Coin Change', lcNumber: 322, brief: 'Minimum coins via unbounded knapsack DP.', difficulty: 'Medium', pattern: 'Unbounded Knapsack DP', tags: ['dp', 'bfs'] },
      { id: 'lcs', name: 'Longest Common Subsequence', lcNumber: 1143, brief: '2D DP table for LCS length.', difficulty: 'Medium', pattern: '2D DP', tags: ['dp', 'string'] },
      { id: 'burst-balloons', name: 'Burst Balloons', lcNumber: 312, brief: 'Interval DP with reverse thinking.', difficulty: 'Hard', pattern: 'Interval DP', tags: ['dp', 'interval'] },
      { id: 'edit-distance', name: 'Edit Distance', lcNumber: 72, brief: 'Levenshtein distance via 2D DP.', difficulty: 'Hard', pattern: '2D DP', tags: ['dp', 'string'] },
    ],
  },
  {
    id: 'heap', label: 'Heaps & Priority Queues', icon: 'FunnelIcon',
    references: [{ id: 'ref-heap', label: '📚 Heap Internals & heapq in Python' }],
    problems: [
      { id: 'find-median', name: 'Find Median from Data Stream', lcNumber: 295, brief: 'Two heaps (max-heap + min-heap) for O(log n) median.', difficulty: 'Hard', pattern: 'Two Heaps', tags: ['heap', 'design'] },
      { id: 'task-scheduler', name: 'Task Scheduler', lcNumber: 621, brief: 'Greedy scheduling using max-heap + cooldown.', difficulty: 'Medium', pattern: 'Greedy + Heap', tags: ['heap', 'greedy'] },
    ],
  },
];

// ─── Realistic Content Templates ─────────────────────────────────────────────
function getContent(sectionId: string, problem: DSAProblem): string {
  const name = problem.name;
  const lc = problem.lcNumber ? `LC #${problem.lcNumber}` : '';
  const pattern = problem.pattern;

  const templates: Record<string, string> = {
    'problem-name': `# ${name} ${lc}\n\n**Category:** ${problem.tags.join(', ')}\n**Difficulty:** ${problem.difficulty}\n**Core Pattern:** ${pattern}\n\n${problem.brief}`,

    'pattern': `**Core DSA Pattern: ${pattern}**\n\nThis problem is a canonical example of the **${pattern}** technique.\n\n**When to recognize this pattern:**\n- The problem asks for pairs/groups with a specific relationship\n- You need O(n) time but naive approach is O(n²)\n- You want to trade space for time\n\n**Why this pattern works here:**\nInstead of checking every pair (O(n²)), we store what we've seen and look up the complement in O(1). This converts a search problem into a lookup problem.\n\n**Pattern Fingerprint — look for these signals:**\n1. "Two elements that satisfy condition X"\n2. "Find if X exists in the array"\n3. "Count occurrences of something"\n4. Fixed-size window with a maintained property`,

    'intuition': `**Problem Intuition — Interview-Friendly Explanation**\n\n**The hidden insight:**\nThe naive approach is to check every pair — O(n²). The insight is: for each element, we only need to know if its "complement" has appeared before.\n\n**Why we reject the brute force:**\nFor n=10⁵, O(n²) = 10¹⁰ operations — this would take minutes. The interviewer won't accept it.\n\n**The mental model:**\nImagine walking through a party and putting name tags on people. When you meet someone, you don't scan the whole room — you check your list. Same idea: build a lookup table as you go.\n\n**The "aha" moment:**\nFor ${name}, as you process each element, ask: "Have I already seen what I need?" Instead of looking forward, look backward using your hash map.\n\n**How to explain this to an interviewer:**\n"I noticed that for each element, the search for its partner can be done in O(1) if we pre-store elements. So I trade O(n) space for O(n) time improvement from O(n²)."`,

    'brute-force': `**Brute Force Approach**\n\n**Idea:** Check every possible pair/combination.\n\n\`\`\`python\ndef brute_force_solution(nums, target):\n    # Check every pair — O(n²) time, O(1) space\n    n = len(nums)\n    for i in range(n):\n        for j in range(i + 1, n):\n            if nums[i] + nums[j] == target:\n                return [i, j]\n    return []  # No solution found\n\n# Time:  O(n²) — nested loops over all pairs\n# Space: O(1) — no extra data structures\n\`\`\`\n\n**Why it fails:**\n- n = 10⁵ → 10¹⁰ operations → TLE guaranteed\n- Interviewer expects you to identify this and move on quickly\n- Say: "This works but is O(n²). Let me optimize."`,

    'optimal': `**Optimal Approach — Interview-Ready Solution**\n\n**Algorithm:**\n1. Initialize a hash map {value: index}\n2. For each element, compute complement = target - element\n3. If complement is in map → found! Return indices\n4. Otherwise, store current element in map\n\n\`\`\`python\ndef ${name.toLowerCase().replace(/\s+/g, '_')}(nums: list[int], target: int) -> list[int]:\n    """\n    Hash map for O(1) complement lookup.\n    Time: O(n) | Space: O(n)\n    """\n    seen = {}  # {value: index}\n    \n    for i, num in enumerate(nums):\n        complement = target - num\n        \n        if complement in seen:\n            return [seen[complement], i]  # Return earlier index first\n        \n        seen[num] = i  # Store current for future lookups\n    \n    return []  # Guaranteed solution exists per problem statement\n\n\n# Dry Run with [2, 7, 11, 15], target=9:\n# i=0: num=2, complement=7, seen={} → not found, seen={2:0}\n# i=1: num=7, complement=2, seen={2:0} → FOUND! return [0, 1]\n\`\`\`\n\n**Why this is optimal:**\n- Time: O(n) — single pass through array\n- Space: O(n) — hash map stores at most n elements\n- This cannot be done in O(1) space (need to store history)\n- This cannot be done in O(1) time (must read all elements at least once)`,

    'python-concepts': `**Key Python Concepts Used**\n\n**1. Dictionary (Hash Map) — dict{}**\n\`\`\`python\nseen = {}          # Create empty dict\nseen[key] = val   # O(1) amortized write\nval = seen[key]   # O(1) average read\nkey in seen       # O(1) membership check ← crucial here\n\`\`\`\nWhy it matters: Python dicts use hash tables internally. Average O(1) operations make our algorithm O(n) overall.\n\n**2. enumerate() — get index + value together**\n\`\`\`python\nfor i, num in enumerate(nums):  # Pythonic, avoids nums[i]\n    pass\n\`\`\`\n\n**3. Tuple unpacking for clean returns**\n\`\`\`python\nreturn [seen[complement], i]  # List of two indices\n\`\`\`\n\n**4. defaultdict (alternative approach)**\n\`\`\`python\nfrom collections import defaultdict\nd = defaultdict(list)  # Never raises KeyError\nd[key].append(value)   # Useful for grouping\n\`\`\``,

    'interview-insights': `**Key Interview Insights**\n\n**Common mistakes candidates make:**\n1. Returning [j, i] instead of [i, j] — always return earlier index first\n2. Storing the index AFTER checking — this causes self-pairing bugs when target = 2*num\n3. Forgetting that indices must be different (but values can repeat)\n4. Overthinking the edge cases — the problem guarantees exactly one solution\n\n**Follow-up questions interviewers ask:**\n- "What if there are multiple valid answers?" → Return all pairs using a set\n- "What if the array is sorted?" → Use two pointers, O(1) space (LC #167)\n- "What if you can't use extra space?" → Sort + two pointers, O(n log n) time\n- "3Sum version?" → Fix one element, use two pointers for the rest (LC #15)\n- "Count pairs, don't return them?" → Adjust to count instead of return\n\n**What Microsoft/Apple/Google interviewers want to see:**\n1. You quickly identify brute force and explain WHY it's slow\n2. You derive the optimization (don't just memorize it)\n3. You handle the dry run cleanly on a small example\n4. You discuss edge cases proactively (empty array, single element, duplicates)\n5. Clean, readable code — use meaningful variable names`,

    'pattern-notes': `**Pattern Recognition Notes**\n\n**How to identify the Hash Map Complement pattern:**\n✅ Problem involves finding pairs/groups with a specific relationship\n✅ Brute force is O(n²) nested loops\n✅ You need to "remember" what you've seen\n✅ Order of elements matters (or their frequencies)\n\n**Template for this pattern:**\n\`\`\`python\nseen = {}\nfor i, x in enumerate(arr):\n    complement = needed_value(x, target)\n    if complement in seen:\n        # FOUND: use seen[complement] and i\n        pass\n    seen[x] = i  # Store AFTER checking to avoid self-pairing\n\`\`\`\n\n**Similar problems to practice (escalating difficulty):**\n- LC #1 Two Sum (this problem)\n- LC #167 Two Sum II (sorted array, two pointers)\n- LC #15 3Sum (fix + two pointers)\n- LC #18 4Sum (nested fix + two pointers)\n- LC #560 Subarray Sum Equals K (prefix sum + hash map)\n- LC #1010 Pairs of Songs (modular arithmetic + hash map)`,

    'real-interview-tips': `**Real Interview Tips**\n\n**Opening (first 2 minutes):**\n"Let me make sure I understand the problem. We have an array of integers and a target. We need to return the indices of the two numbers that add up to the target. I'll assume there's exactly one solution and I can't use the same element twice. Is that correct?"\n\n**During coding:**\nNarrate your thinking: "I'll use a hash map to store each number and its index as I iterate. For each new number, I check if its complement is already in the map."\n\n**Complexity discussion:**\n"The time complexity is O(n) because we iterate through the array once, and each hash map operation is O(1) amortized. Space is O(n) in the worst case where no pair exists until the last element."\n\n**Proactive edge cases:**\n"Edge cases I'd consider: empty array returns [], single element returns [], duplicate values work because we store the most recent index, but let me verify..."\n\n**What separates L4 from L5 at FAANG:**\nL4 gets the solution. L5 discusses: "In a distributed system, if this array was sharded across machines, how would I coordinate the lookup? We'd need a shared hash map or a two-phase approach."`,

    'references': `**References & Resources**\n\n📹 **Video Explanations:**\n- NeetCode YouTube: "${name}" — excellent whiteboard walkthrough\n- Abdul Bari Algorithm Course (for foundational understanding)\n\n📄 **Problem Links:**\n- LeetCode #${problem.lcNumber}: Official problem + editorial\n- NeetCode.io roadmap — categorized by pattern\n- Striver's DSA Sheet — A-Z DSA problems with difficulty progression\n\n📚 **Books:**\n- *Introduction to Algorithms* (CLRS) — Chapter 11: Hash Tables\n- *Cracking the Coding Interview* — Arrays & Strings chapter\n- *Elements of Programming Interviews* — Hash tables chapter\n\n🌐 **Online Resources:**\n- CP-Algorithms.com — Mathematical foundations\n- MIT 6.006 OpenCourseWare — Hash tables lecture\n- Competitive Programmer's Handbook (free PDF) — Data structures`,
  };

  return templates[sectionId] ?? `**${name} — ${sectionId}**\n\nDetailed content for this section of the ${name} problem analysis. This covers the ${sectionId} aspect with full technical depth appropriate for senior engineering interviews.`;
}

// ─── Quiz Data ────────────────────────────────────────────────────────────────
const QUIZ_BANK: Record<string, { q: string; options: string[]; answer: number; explanation: string }[]> = {
  'two-sum': [
    { q: 'What is the time complexity of the optimal Two Sum solution?', options: ['O(n²)', 'O(n log n)', 'O(n)', 'O(log n)'], answer: 2, explanation: 'We iterate once through the array with O(1) hash map lookups, giving overall O(n).' },
    { q: 'What data structure enables the O(n) solution?', options: ['Stack', 'Hash Map (dict)', 'Binary Search Tree', 'Priority Queue'], answer: 1, explanation: 'A hash map provides O(1) average-case lookup for the complement of each element.' },
    { q: 'What is stored as the VALUE in the hash map?', options: ['The element value', 'The element\'s index', 'The complement value', 'Boolean True'], answer: 1, explanation: 'We store {value: index} so we can return the index when the complement is found.' },
    { q: 'Why do we check BEFORE storing the current element?', options: ['Order matters for output', 'To avoid using the same element twice', 'Python requires this order', 'To handle negative numbers'], answer: 1, explanation: 'Checking before storing prevents using an element as its own pair (self-pairing bug when target = 2*num).' },
  ],
  'default': [
    { q: 'What is the primary advantage of hash maps in algorithm design?', options: ['O(1) space complexity', 'O(1) average time lookup', 'Sorted order maintenance', 'Guaranteed collision-free storage'], answer: 1, explanation: 'Hash maps provide O(1) average-case time for insertion, deletion, and lookup operations.' },
    { q: 'When should you prefer BFS over DFS for graph problems?', options: ['When finding any path', 'When finding the shortest path', 'When the graph is deep', 'When using recursion'], answer: 1, explanation: 'BFS explores level by level, guaranteeing shortest path in unweighted graphs. DFS finds any path, not necessarily shortest.' },
    { q: 'What is the time complexity of building a heap from n elements?', options: ['O(n log n)', 'O(n)', 'O(log n)', 'O(n²)'], answer: 1, explanation: 'Heapify (build_heap) runs in O(n) due to the amortized analysis, not O(n log n) as naive insertion would suggest.' },
    { q: 'In dynamic programming, what two conditions must a problem satisfy?', options: ['Greedy choice + optimal substructure', 'Overlapping subproblems + optimal substructure', 'Divide & conquer + memoization', 'Recursion + base case'], answer: 1, explanation: 'DP applies when: (1) optimal solution can be built from optimal sub-solutions, and (2) same subproblems appear multiple times.' },
  ],
};

// ─── Section Definitions ──────────────────────────────────────────────────────
const SECTION_DEFS = [
  { id: 'problem-name', label: 'Problem Statement', icon: 'DocumentTextIcon', subtitle: 'Name, LC#, topic, pattern' },
  { id: 'pattern', label: 'Core DSA Pattern', icon: 'PuzzlePieceIcon', subtitle: 'Pattern used + recognition signals' },
  { id: 'intuition', label: 'Problem Intuition', icon: 'LightBulbIcon', subtitle: 'Interview-friendly reasoning process' },
  { id: 'brute-force', label: 'Brute Force Approach', icon: 'BoltSlashIcon', subtitle: 'Code + why it\'s rejected' },
  { id: 'optimal', label: 'Optimal Approach', icon: 'BoltIcon', subtitle: 'Clean code + dry run + complexity' },
  { id: 'python-concepts', label: 'Python Concepts Used', icon: 'CodeBracketIcon', subtitle: 'defaultdict, heapq, enumerate, etc.' },
  { id: 'interview-insights', label: 'Key Interview Insights', icon: 'ChatBubbleLeftRightIcon', subtitle: 'Common mistakes + follow-ups' },
  { id: 'pattern-notes', label: 'Pattern Recognition Notes', icon: 'MagnifyingGlassIcon', subtitle: 'How to spot this in future problems' },
  { id: 'real-interview-tips', label: 'Real Interview Tips', icon: 'AcademicCapIcon', subtitle: 'What to say, how FAANG evaluates' },
  { id: 'quiz', label: 'Quiz', icon: 'TrophyIcon', subtitle: '4 questions with explanations' },
  { id: 'references', label: 'References & Resources', icon: 'BookOpenIcon', subtitle: 'NeetCode, Striver, CLRS, MIT OCW' },
];

function initSections(): Record<string, SectionState> {
  return Object.fromEntries(SECTION_DEFS.map(s => [s.id, { generated: false, generating: false, content: '' }]));
}

function diffColor(d: string) {
  return d === 'Easy' ? 'text-success bg-success/10' : d === 'Hard' ? 'text-error bg-error/10' : 'text-warning bg-warning/10';
}

// ─── Main Component ───────────────────────────────────────────────────────────
export default function DSALabInteractive() {
  const [topics] = useState<TopicGroup[]>(TOPICS);
  const [selectedTopicId, setSelectedTopicId] = useState('arrays');
  const [selectedProblemId, setSelectedProblemId] = useState<string | null>(null);
  const [selectedRefId, setSelectedRefId] = useState<string | null>(null);
  const [expandedTopics, setExpandedTopics] = useState<Set<string>>(new Set(['arrays']));
  const [sections, setSections] = useState<Record<string, SectionState>>({});
  const [customInput, setCustomInput] = useState('');
  const [addingCustom, setAddingCustom] = useState(false);
  const [customProblems, setCustomProblems] = useState<DSAProblem[]>([]);
  const [quizBatch, setQuizBatch] = useState(0);
  const [quizBank, setQuizBank] = useState<any[]>([]);

  const currentTopic = topics.find(t => t.id === selectedTopicId);
  const allProblems = [...(currentTopic?.problems ?? []), ...customProblems.filter(p => p.tags.includes(selectedTopicId))];
  const selectedProblem = allProblems.find(p => p.id === selectedProblemId) ?? null;
  const selectedRef = currentTopic?.references.find(r => r.id === selectedRefId) ?? null;
  const contextLabel = selectedProblem?.name ?? selectedRef?.label ?? currentTopic?.label ?? 'DSA';

  const flatTopics = topics.flatMap(t => [
    { id: t.id, type: 'topic', label: t.label, topicId: t.id },
    ...t.problems.map(p => ({ id: p.id, type: 'problem', label: p.name, topicId: t.id })),
  ]);
  const currentIdx = selectedProblem ? flatTopics.findIndex(x => x.id === selectedProblemId) : -1;
  const prevItem = currentIdx > 0 ? flatTopics[currentIdx - 1] : null;
  const nextItem = currentIdx >= 0 && currentIdx < flatTopics.length - 1 ? flatTopics[currentIdx + 1] : null;

  const navigateTo = (item: typeof flatTopics[0]) => {
    setSelectedTopicId(item.topicId);
    if (item.type === 'problem') { setSelectedProblemId(item.id); setSelectedRefId(null); setSections(initSections()); setQuizBatch(0); setQuizBank([]); }
    else { setSelectedProblemId(null); setSelectedRefId(null); setSections({}); }
  };

  const selectProblem = (topicId: string, problemId: string) => {
    setSelectedTopicId(topicId);
    setSelectedProblemId(problemId);
    setSelectedRefId(null);
    setSections(initSections());
    setQuizBatch(0);
    setQuizBank(QUIZ_BANK[problemId] ?? QUIZ_BANK.default);
    setExpandedTopics(prev => new Set([...prev, topicId]));
  };

  const selectRef = (topicId: string, refId: string) => {
    setSelectedTopicId(topicId);
    setSelectedRefId(refId);
    setSelectedProblemId(null);
    setSections(initSections());
    setExpandedTopics(prev => new Set([...prev, topicId]));
  };

  const generateSection = (sectionId: string) => {
    if (!selectedProblem) return;
    setSections(prev => ({ ...prev, [sectionId]: { ...prev[sectionId], generating: true } }));
    setTimeout(() => {
      const content = getContent(sectionId, selectedProblem);
      setSections(prev => ({ ...prev, [sectionId]: { generated: true, generating: false, content } }));
    }, 1500);
  };

  const handleAddCustom = () => {
    if (!customInput.trim()) return;
    setAddingCustom(true);
    setTimeout(() => {
      const p: DSAProblem = { id: `custom-${Date.now()}`, name: customInput.trim(), lcNumber: null, brief: 'Custom problem.', difficulty: 'Medium', pattern: 'Custom', tags: [selectedTopicId] };
      setCustomProblems(prev => [...prev, p]);
      setCustomInput('');
      setAddingCustom(false);
    }, 800);
  };

  return (
    <div className="min-h-screen bg-background pt-[60px] flex flex-col">
      <div className="flex-1 flex overflow-hidden" style={{ height: 'calc(100vh - 60px)' }}>

        {/* ── LEFT: Problem Tree ─────────────────────────────────────────── */}
        <aside className="w-[260px] flex-shrink-0 border-r border-border bg-card flex flex-col">
          <div className="p-14 border-b border-border flex-shrink-0">
            <h2 className="font-heading text-sm font-semibold text-foreground flex items-center gap-9">
              <Icon name="CpuChipIcon" size={15} className="text-primary" />DSA Lab
            </h2>
            <p className="text-xs text-muted-foreground mt-3">Click to load → Generate sections</p>
          </div>

          <div className="flex-1 overflow-y-auto py-6">
            {topics.map(topic => (
              <div key={topic.id}>
                <button
                  onClick={() => { setExpandedTopics(prev => { const n = new Set(prev); n.has(topic.id) ? n.delete(topic.id) : n.add(topic.id); return n; }); setSelectedTopicId(topic.id); setSelectedProblemId(null); setSelectedRefId(null); setSections({}); }}
                  className={`w-full text-left flex items-center gap-8 px-14 py-9 text-xs font-semibold transition-smooth hover:bg-muted ${selectedTopicId === topic.id && !selectedProblemId && !selectedRefId ? 'bg-primary/10 text-primary border-r-2 border-primary' : 'text-foreground'}`}
                >
                  <Icon name={topic.icon as any} size={13} />
                  <span className="flex-1 truncate">{topic.label}</span>
                  <Icon name={expandedTopics.has(topic.id) ? 'ChevronDownIcon' : 'ChevronRightIcon'} size={11} className="text-muted-foreground flex-shrink-0" />
                </button>
                {expandedTopics.has(topic.id) && (
                  <div>
                    {topic.problems.map(p => (
                      <button key={p.id} onClick={() => selectProblem(topic.id, p.id)}
                        className={`w-full text-left flex items-center gap-8 pl-22 pr-10 py-7 text-xs transition-smooth hover:bg-muted ${selectedProblemId === p.id ? 'bg-secondary/10 text-secondary border-r-2 border-secondary' : 'text-muted-foreground'}`}>
                        <span className="text-muted-foreground/40">↳</span>
                        <span className="flex-1 truncate">{p.name}</span>
                        {p.lcNumber && <span className="text-muted-foreground/50 font-code text-[10px]">#{p.lcNumber}</span>}
                      </button>
                    ))}
                    {customProblems.filter(cp => cp.tags.includes(topic.id)).map(p => (
                      <button key={p.id} onClick={() => selectProblem(topic.id, p.id)}
                        className={`w-full text-left flex items-center gap-8 pl-22 pr-10 py-7 text-xs transition-smooth hover:bg-muted ${selectedProblemId === p.id ? 'bg-secondary/10 text-secondary border-r-2 border-secondary' : 'text-muted-foreground'}`}>
                        <span className="text-muted-foreground/40">↳</span>
                        <span className="flex-1 truncate">{p.name}</span>
                        <span className="text-xs text-accent">custom</span>
                      </button>
                    ))}
                    {topic.references.map(ref => (
                      <button key={ref.id} onClick={() => selectRef(topic.id, ref.id)}
                        className={`w-full text-left flex items-center gap-8 pl-22 pr-10 py-7 text-xs transition-smooth hover:bg-muted ${selectedRefId === ref.id ? 'bg-accent/10 text-accent border-r-2 border-accent' : 'text-muted-foreground/60'}`}>
                        <span className="text-muted-foreground/40">↳</span>
                        <span className="flex-1 truncate">{ref.label}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Add custom */}
          <div className="p-12 border-t border-border flex-shrink-0">
            <div className="flex gap-6">
              <input value={customInput} onChange={e => setCustomInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleAddCustom()}
                placeholder="Add problem / topic..."
                className="flex-1 min-w-0 bg-input border border-border rounded-md px-9 py-6 text-xs focus-ring placeholder:text-muted-foreground" />
              <button onClick={handleAddCustom} disabled={addingCustom || !customInput.trim()}
                className="p-6 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-smooth disabled:opacity-50 flex-shrink-0">
                {addingCustom ? <span className="w-12 h-12 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin block" /> : <Icon name="PlusIcon" size={14} />}
              </button>
            </div>
          </div>
        </aside>

        {/* ── CENTER: Content ────────────────────────────────────────────── */}
        <main className="flex-1 overflow-y-auto">
          {!selectedProblem && !selectedRef ? (
            <div className="flex flex-col items-center justify-center h-full text-center px-24">
              <div className="w-64 h-64 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-18">
                <Icon name="CpuChipIcon" size={32} variant="outline" className="text-primary" />
              </div>
              <h2 className="font-heading text-xl font-semibold text-foreground mb-9">Select a Problem</h2>
              <p className="text-sm text-muted-foreground max-w-sm">Choose a problem from the left sidebar. Each section generates on-demand to save tokens.</p>
            </div>
          ) : (
            <div className="p-20 space-y-14">
              {/* Problem header */}
              {selectedProblem && (
                <div className="bg-card border border-border rounded-lg p-20 shadow-sm">
                  <div className="flex items-start justify-between gap-18 flex-wrap">
                    <div className="flex-1 min-w-0">
                      <div className="flex flex-wrap items-center gap-9 mb-9">
                        {selectedProblem.lcNumber && <span className="font-code text-xs text-muted-foreground bg-muted px-9 py-4 rounded-md">LC #{selectedProblem.lcNumber}</span>}
                        <span className={`text-xs font-semibold px-9 py-4 rounded-md ${diffColor(selectedProblem.difficulty)}`}>{selectedProblem.difficulty}</span>
                        <span className="text-xs px-9 py-4 rounded-md bg-secondary/10 text-secondary">{selectedProblem.pattern}</span>
                        {selectedProblem.tags.map(tag => <span key={tag} className="text-xs px-7 py-3 rounded bg-muted text-muted-foreground font-code">{tag}</span>)}
                      </div>
                      <h1 className="font-heading text-2xl font-bold text-foreground mb-6">{selectedProblem.name}</h1>
                      <p className="text-sm text-muted-foreground">{selectedProblem.brief}</p>
                    </div>
                    {selectedProblem.lcNumber && (
                      <a href={`https://leetcode.com/problems/${selectedProblem.name.toLowerCase().replace(/[^a-z0-9]+/g, '-')}/`} target="_blank" rel="noopener noreferrer"
                        className="flex-shrink-0 flex items-center gap-6 px-12 py-7 border border-border rounded-md text-xs text-foreground hover:bg-muted transition-smooth">
                        <Icon name="ArrowTopRightOnSquareIcon" size={13} /> Open on LeetCode
                      </a>
                    )}
                  </div>
                </div>
              )}

              {selectedRef && (
                <div className="bg-card border border-border rounded-lg p-20 shadow-sm">
                  <h1 className="font-heading text-xl font-bold text-foreground mb-6">{selectedRef.label}</h1>
                  <p className="text-sm text-muted-foreground">Reference learning material. Generate sections below to explore the theory.</p>
                </div>
              )}

              {/* Sections */}
              {SECTION_DEFS.map((def, idx) => {
                const s = sections[def.id] ?? { generated: false, generating: false, content: '' };
                return (
                  <OnDemandSection
                    key={def.id}
                    sectionIndex={idx + 1}
                    icon={def.icon}
                    title={def.label}
                    subtitle={def.subtitle}
                    content={s.content}
                    isGenerated={s.generated}
                    isGenerating={s.generating}
                    onGenerate={() => generateSection(def.id)}
                  >
                    {def.id === 'quiz' && s.generated ? (
                      <QuizCarousel
                        questions={quizBank.slice(quizBatch * 4, quizBatch * 4 + 4)}
                        hasMore={(quizBatch + 1) * 4 < 16}
                        onGenerateMore={() => {
                          const more = (QUIZ_BANK.default ?? []).map(q => ({ ...q, q: `[Batch ${quizBatch + 2}] ` + q.q }));
                          setQuizBank(prev => [...prev, ...more]);
                          setQuizBatch(b => b + 1);
                        }}
                      />
                    ) : undefined}
                  </OnDemandSection>
                );
              })}

              {/* Prev / Next navigation */}
              {selectedProblem && (
                <div className="flex items-center justify-between py-18 border-t border-border mt-24">
                  <button disabled={!prevItem} onClick={() => prevItem && navigateTo(prevItem)}
                    className="flex items-center gap-9 px-16 py-10 rounded-md border border-border text-sm text-foreground hover:bg-muted transition-smooth disabled:opacity-30 disabled:pointer-events-none">
                    <Icon name="ArrowLeftIcon" size={14} />
                    <span>{prevItem ? prevItem.label : 'No previous'}</span>
                  </button>
                  <button disabled={!nextItem} onClick={() => nextItem && navigateTo(nextItem)}
                    className="flex items-center gap-9 px-16 py-10 rounded-md border border-border text-sm text-foreground hover:bg-muted transition-smooth disabled:opacity-30 disabled:pointer-events-none">
                    <span>{nextItem ? nextItem.label : 'No next'}</span>
                    <Icon name="ArrowRightIcon" size={14} />
                  </button>
                </div>
              )}
            </div>
          )}
        </main>

        {/* ── RIGHT: Copilot ─────────────────────────────────────────────── */}
        <aside className="w-[280px] flex-shrink-0 border-l border-border flex flex-col">
          <LabCopilot context={contextLabel} labType="dsa" />
        </aside>
      </div>
    </div>
  );
}
