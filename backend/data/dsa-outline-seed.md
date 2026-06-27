# dsa outline

# DSA Lab Seed Topics (Pattern-Wise, Starks Style)
* * *
## PATTERN 1: PREFIX SUM & CUMULATIVE LOGIC
**1\. Subarray Sum Equals K (LC #560) \[Medium\]**
*   Python: `collections.defaultdict(int)` for frequency map
*   Real-World: Financial transaction anomaly detection (sum of transactions in a window)
*   Remember: prefix\_sum - k lookup, not sliding window (negative numbers exist)
*   Edge: prefix\_sum map starts with {0: 1}, not empty

**2\. Product of Array Except Self (LC #238) \[Medium\]**
*   Python: list comprehension with running product, no division
*   Real-World: Recommendation scoring (multiply all feature weights except current)
*   Remember: Left pass × Right pass trick, O(1) extra space using output array
*   Edge: Zeros in array break division approach, prefix product handles it

**3\. Range Sum Query - Immutable (LC #303) \[Easy\]**
*   Python: `itertools.accumulate` for one-liner prefix sum
*   Real-World: Dashboard analytics (sum of metrics over any date range)
*   Remember: prefix\[right+1\] - prefix\[left\], off-by-one kills you
*   Edge: Single element range, full array range

**4\. Contiguous Array (LC #525) \[Medium\]**
*   Python: dict for first-seen index of running sum
*   Real-World: Network packet analysis (equal 0s and 1s = balanced traffic)
*   Remember: Treat 0 as -1, reduce to "subarray sum = 0" problem
*   Edge: Entire array is the answer, store index -1 for sum 0

* * *
## PATTERN 2: TWO POINTERS
**5\. 3Sum (LC #15) \[Medium\]**
*   Python: sort + two pointers, skip duplicates with while loops
*   Real-World: Chemistry (finding 3 reagents that balance to neutral pH)
*   Remember: Sort first, fix one element, two-pointer on rest. Dedup at BOTH levels
*   Edge: All zeros \[0,0,0,0\], all negatives, array with duplicates

**6\. Container With Most Water (LC #11) \[Medium\]**
*   Python: `max()` with two pointers from both ends
*   Real-World: Warehouse shelf placement (maximize storage between two walls)
*   Remember: Move the SHORTER pointer (greedy). Width decreases, so only height increase helps
*   Edge: Monotonically increasing/decreasing heights

**7\. Trapping Rain Water (LC #42) \[Hard\]**
*   Python: Two-pointer with left\_max, right\_max tracking
*   Real-World: Terrain flooding simulation, reservoir capacity estimation
*   Remember: Water at i = min(left\_max, right\_max) - height\[i\]. Two-pointer avoids O(n) space
*   Edge: Flat surface (no trap), single peak, valley at edges

**8\. Valid Palindrome II (LC #680) \[Easy\]**
*   Python: string slicing s\[i+1:j+1\] or s\[i:j\] for skip check
*   Real-World: Spell-checker (allow one typo tolerance)
*   Remember: On mismatch, try skipping left OR right, check both
*   Edge: Already palindrome, single char, skip first or last char

* * *
## PATTERN 3: SLIDING WINDOW
**9\. Minimum Window Substring (LC #76) \[Hard\]**
*   Python: `collections.Counter` for need/have maps, expandable window
*   Real-World: Log search (smallest time window containing all error types)
*   Remember: Expand right until valid, shrink left to minimize. Track "formed" count
*   Edge: t has duplicate chars, t longer than s, single char match

**10\. Longest Substring Without Repeating Characters (LC #3) \[Medium\]**
*   Python: dict storing last index of each char, update left = max(left, last\_seen+1)
*   Real-World: Unique session tracking (longest streak of unique page visits)
*   Remember: Don't reset left backward. Use max() to only move forward
*   Edge: All same chars "aaaa", all unique "abcdef", empty string

**11\. Sliding Window Maximum (LC #239) \[Hard\]**
*   Python: `collections.deque` as monotonic decreasing deque
*   Real-World: Stock market (max price in rolling k-day window), sensor peak detection
*   Remember: Deque stores INDICES not values. Pop from back if smaller, pop from front if out of window
*   Edge: k=1 (return array itself), k=len(nums), all equal elements

**12\. Longest Repeating Character Replacement (LC #424) \[Medium\]**
*   Python: Counter + window where len - max\_freq <= k
*   Real-World: DNA mutation analysis (longest strand achievable with k mutations)
*   Remember: Window is valid if (window\_size - count\_of\_most\_frequent) <= k. Never shrink max\_freq
*   Edge: k >= len(s) means whole string, all same chars already

* * *
## PATTERN 4: FAST & SLOW POINTERS
**13\. Linked List Cycle II (LC #142) \[Medium\]**
*   Python: Floyd's algorithm, after meet reset one pointer to head
*   Real-World: Deadlock detection in OS (resource allocation graph cycle)
*   Remember: After meeting, distance from head to cycle start = distance from meet to cycle start
*   Edge: No cycle, cycle at head, single node self-loop

**14\. Find the Duplicate Number (LC #287) \[Medium\]**
*   Python: Treat array as linked list, index → value as next pointer
*   Real-World: Database integrity check (finding duplicate primary keys)
*   Remember: Floyd's on array without modifying it. nums\[0\] is entry point (0 is never in range)
*   Edge: Duplicate appears many times, duplicate is at boundary

**15\. Happy Number (LC #202) \[Easy\]**
*   Python: Digit sum with `divmod()` in a loop, or set for cycle detection
*   Real-World: Hashing collision detection (cycle in hash chains)
*   Remember: Sum of squares either reaches 1 or enters a cycle. Fast/slow or HashSet both work
*   Edge: Single digit numbers, very large numbers converge quickly

**16\. Middle of the Linked List (LC #876) \[Easy\]**
*   Python: slow = [slow.next](http://slow.next), fast = [fast.next.next](http://fast.next.next)
*   Real-World: Load balancer (split request queue in half for two workers)
*   Remember: For even length, this gives second middle. Check fast AND [fast.next](http://fast.next)
*   Edge: Single node, two nodes, odd vs even length

* * *
## PATTERN 5: HASHMAP & FREQUENCY COUNTING
**17\. Top K Frequent Elements (LC #347) \[Medium\]**
*   Python: `Counter.most_common(k)` one-liner, or bucket sort O(n)
*   Real-World: Trending topics, top search queries, most active users
*   Remember: Bucket sort beats heap: index = frequency, value = list of elements. O(n) vs O(n log k)
*   Edge: All same frequency, k equals unique elements, single element

**18\. Group Anagrams (LC #49) \[Medium\]**
*   Python: `defaultdict(list)` with `tuple(sorted(word))` as key, or letter count tuple
*   Real-World: Plagiarism detection, search engine query clustering
*   Remember: sorted() key is O(k log k). Count-based tuple key is O(k) but 26-length fixed
*   Edge: Empty strings group together, single char words, all same word

**19\. Longest Consecutive Sequence (LC #128) \[Medium\]**
*   Python: `set()` for O(1) lookup, only start counting from sequence START
*   Real-World: Gap analysis in time-series data, finding continuous uptime stretches
*   Remember: Only process if (num - 1) NOT in set. This makes it O(n) not O(n²)
*   Edge: Duplicates (set handles), empty array, all same number

**20\. Two Sum (LC #1) \[Easy\]**
*   Python: dict for complement lookup in single pass
*   Real-World: Payment matching (find two transactions that sum to a target refund)
*   Remember: Store {value: index}. Check complement BEFORE inserting (avoids using same element twice)
*   Edge: Same element can't be used twice, negative numbers, exactly two solutions

* * *
## PATTERN 6: MONOTONIC STACK
**21\. Daily Temperatures (LC #739) \[Medium\]**
*   Python: stack stores indices, pop when current > stack top
*   Real-World: Weather forecasting (days until warmer), stock price alerts
*   Remember: Stack holds INDICES of decreasing temps. Answer\[popped\] = i - popped
*   Edge: Monotonically increasing (empty result), monotonically decreasing (all zeros)

**22\. Largest Rectangle in Histogram (LC #84) \[Hard\]**
*   Python: Stack of indices, calculate width on pop: i - stack\[-1\] - 1
*   Real-World: Maximum rectangular plot in uneven terrain, UI layout calculation
*   Remember: Push -1 as sentinel. Width = i - stack\[-1\] - 1 (not i - popped)
*   Edge: All same height, single bar, ascending order, descending order

**23\. Next Greater Element I (LC #496) \[Easy\]**
*   Python: Stack + HashMap to store next-greater mapping
*   Real-World: Stock next peak prediction, DNS resolution chain
*   Remember: Process nums2 with stack, build map. Then look up each nums1 element
*   Edge: No greater element exists (return -1), last element always -1

**24\. Online Stock Span (LC #901) \[Medium\]**
*   Python: Stack of (price, span) tuples, accumulate span on pop
*   Real-World: Literal stock span calculation, consecutive performance metrics
*   Remember: Pop all smaller/equal prices, ADD their spans to current. Stack stores cumulative info
*   Edge: Monotonically increasing prices (span always 1), all same price

* * *
## PATTERN 7: BINARY SEARCH (ON ANSWER)
**25\. Koko Eating Bananas (LC #875) \[Medium\]**
*   Python: bisect-style on answer space, `math.ceil(pile/speed)` for hours calc
*   Real-World: Resource allocation (minimum server capacity to process jobs in time)
*   Remember: Search space is \[1, max(piles)\]. Binary search on the ANSWER, not the array
*   Edge: h == len(piles) means answer is max(piles), single pile

**26\. Search in Rotated Sorted Array (LC #33) \[Medium\]**
*   Python: Identify which half is sorted, then decide direction
*   Real-World: Searching in circular buffers, log rotation search
*   Remember: One half is ALWAYS sorted. Check if target is in sorted half, else go other way
*   Edge: No rotation, single element, target not present, rotation at start/end

**27\. Find Minimum in Rotated Sorted Array (LC #153) \[Medium\]**
*   Python: Compare mid with right (not left!) to decide direction
*   Real-World: Finding reset point in circular time-series data
*   Remember: If nums\[mid\] > nums\[right\], min is in right half. Compare with RIGHT always
*   Edge: Not rotated (first element), single element, two elements

**28\. Median of Two Sorted Arrays (LC #4) \[Hard\]**
*   Python: Binary search on shorter array, partition both arrays
*   Real-World: Database merge-sort optimization, distributed percentile computation
*   Remember: Binary search on SHORTER array. Partition so left\_total = (m+n+1)//2. Check cross-boundaries
*   Edge: One empty array, arrays of very different sizes, all elements same

* * *
## PATTERN 8: BACKTRACKING
**29\. Combination Sum (LC #39) \[Medium\]**
*   Python: Recursive with start index, append/pop pattern, allow reuse (i not i+1)
*   Real-World: Budget allocation (find all ways to spend exact budget on items)
*   Remember: Pass same index i (reuse allowed). Sort to enable early termination when sum > target
*   Edge: Single element equals target, no valid combination, very deep recursion

**30\. Word Search (LC #79) \[Medium\]**
*   Python: DFS with in-place marking (board\[r\]\[c\] = '#'), restore after
*   Real-World: Pattern matching in grids (crossword solvers, OCR character path detection)
*   Remember: Mark visited IN-PLACE to save space. Restore on backtrack. Check bounds first
*   Edge: Single char word, word longer than board cells, all same chars in board

**31\. N-Queens (LC #51) \[Hard\]**
*   Python: Sets for columns, diagonals (row-col), anti-diagonals (row+col)
*   Real-World: Constraint satisfaction (scheduling, resource allocation without conflicts)
*   Remember: Diagonal identity: row-col is constant. Anti-diagonal: row+col is constant. Sets for O(1) check
*   Edge: n=1 (trivial), n=2,3 (no solution), n=4 (two solutions)

**32\. Palindrome Partitioning (LC #131) \[Medium\]**
*   Python: Backtrack with s\[start:i+1\] slicing, isPalindrome check
*   Real-World: Text segmentation (NLP word boundary detection with constraints)
*   Remember: For each position, try all possible palindrome prefixes. Memoize palindrome checks with DP table
*   Edge: All same chars (many partitions), no palindrome substring longer than 1

* * *
## PATTERN 9: BFS / DFS ON GRAPHS
**33\. Number of Islands (LC #200) \[Medium\]**
*   Python: DFS with in-place sinking (grid\[r\]\[c\] = '0'), or BFS with deque
*   Real-World: Image blob detection, connected component analysis in maps
*   Remember: Sink visited land to avoid visited set. Iterate full grid, count DFS triggers
*   Edge: All water, all land (one island), diagonal doesn't count

**34\. Course Schedule (LC #207) \[Medium\]**
*   Python: `defaultdict(list)` for adjacency, DFS with 3-state coloring (unvisited, in-progress, done)
*   Real-World: Build system dependency resolution (make, gradle), package managers
*   Remember: Cycle detection = impossible. Three states prevent revisiting done nodes. Kahn's BFS also works
*   Edge: No prerequisites (always possible), self-loop, disconnected graph

**35\. Word Ladder (LC #127) \[Hard\]**
*   Python: BFS with deque, generate neighbors by replacing each char with a-z
*   Real-World: Spell-checker suggestion chains, gene mutation paths
*   Remember: BFS guarantees shortest path. Use wildcard pattern dict (h_t → \[hot, hat\]) for O(26_L) neighbor gen
*   Edge: No transformation possible (return 0), endWord not in list, very long words

**36\. Clone Graph (LC #133) \[Medium\]**
*   Python: dict {original: clone} as visited map, DFS/BFS cloning
*   Real-World: Deep copy of object graphs, database record duplication with references
*   Remember: HashMap maps old→new node. Clone node FIRST, then recurse neighbors. Handles cycles naturally
*   Edge: Empty graph, single node with self-loop, fully connected graph

* * *
## PATTERN 10: TREE TRAVERSAL & DFS
**37\. Binary Tree Level Order Traversal (LC #102) \[Medium\]**
*   Python: deque BFS, process level\_size = len(queue) nodes per iteration
*   Real-World: Org chart level display, DOM rendering layer by layer, BFS in social networks
*   Remember: Key trick is snapshot len(queue) at start of each level. Append children during iteration
*   Edge: Empty tree, single node, skewed tree (one node per level)

**38\. Validate Binary Search Tree (LC #98) \[Medium\]**
*   Python: Recursive with (low, high) bounds, or inorder should be strictly increasing
*   Real-World: Database index validation, ensuring B-tree property holds after mutations
*   Remember: Pass bounds down: left child gets (low, node.val), right gets (node.val, high). Use float('-inf'), float('inf')
*   Edge: Equal values (strictly less, not <=), single node, Integer.MIN/MAX as values

**39\. Serialize and Deserialize Binary Tree (LC #297) \[Hard\]**
*   Python: Preorder with "null" markers, deque for deserialization (popleft)
*   Real-World: Saving tree state to disk/network (JSON tree structure, AST serialization)
*   Remember: Preorder + null markers = unique tree. Use deque.popleft() for O(1) consumption during deserialize
*   Edge: Empty tree, all left children (skewed), complete binary tree

**40\. Lowest Common Ancestor (LC #236) \[Medium\]**
*   Python: Recursive, return node if found, bubble up from both sides
*   Real-World: Version control merge-base (git merge-base), taxonomy classification
*   Remember: If left and right both return non-null, current node is LCA. If one is null, return the other
*   Edge: One node is ancestor of other, both nodes same, root is one of the nodes

* * *
## PATTERN 11: HEAP / PRIORITY QUEUE (Top-K)
**41\. Merge K Sorted Lists (LC #23) \[Hard\]**
*   Python: `heapq` with (val, index, node) tuples (index breaks ties since ListNode isn't comparable)
*   Real-World: Database merge-sort join, merging sorted log files from multiple servers
*   Remember: Push first element of each list. Pop min, push next from same list. Tie-breaker index needed
*   Edge: Empty lists in input, single list, all lists have one element

**42\. Find Median from Data Stream (LC #295) \[Hard\]**
*   Python: Two heaps: max-heap (negate for Python) for left, min-heap for right
*   Real-World: Real-time percentile monitoring, streaming analytics dashboards
*   Remember: Balance: len(left) == len(right) or len(left) == len(right)+1. Always push to left first
*   Edge: Single element, two elements, all same values, alternating large/small

**43\. Task Scheduler (LC #621) \[Medium\]**
*   Python: Counter + max-heap (negate), track cooldown with queue of (time\_available, count)
*   Real-World: CPU task scheduling, rate-limited API call batching
*   Remember: Most frequent task determines idle slots. Formula: (max\_freq-1) \* (n+1) + count\_of\_max\_freq tasks
*   Edge: n=0 (no cooldown), all same task, many tasks with same frequency

**44\. Kth Largest Element in an Array (LC #215) \[Medium\]**
*   Python: `heapq.nlargest(k, nums)[-1]`, or min-heap of size k, or quickselect
*   Real-World: Top-K leaderboard, finding percentile cutoffs in real-time
*   Remember: Min-heap of size k: push all, pop when size > k. Top of heap = kth largest. O(n log k)
*   Edge: k=1 (max), k=n (min), duplicates in array, all same elements
* * *
## PATTERN 12: DYNAMIC PROGRAMMING (1D)
**45\. House Robber (LC #198) \[Medium\]**
*   Python: dp\[i\] = max(dp\[i-1\], dp\[i-2\] + nums\[i\]), space-optimize to two vars
*   Real-World: Resource selection with exclusion constraints, ad placement with spacing rules
*   Remember: Choice at each step: skip or take+skip\_previous. Two variables (prev1, prev2) replace array
*   Edge: Single house, two houses, all same values, alternating high/low

**46\. Longest Increasing Subsequence (LC #300) \[Medium\]**
*   Python: `bisect.bisect_left` on tails array for O(n log n), or dp\[i\] = LIS ending at i
*   Real-World: Stock trend analysis (longest uptrend), version dependency resolution
*   Remember: Patience sorting: maintain smallest tail for each length. bisect\_left finds insertion point
*   Edge: Strictly increasing (LIS = n), strictly decreasing (LIS = 1), all equal

**47\. Coin Change (LC #322) \[Medium\]**
*   Python: dp = \[float('inf')\] \* (amount+1), dp\[0\] = 0, iterate coins for each amount
*   Real-World: Making change (literally), minimum resource allocation, minimum API calls
*   Remember: Bottom-up: dp\[i\] = min(dp\[i\], dp\[i-coin\]+1) for all coins. Check dp\[amount\] != inf
*   Edge: Amount 0 (return 0), impossible (return -1), single coin, amount < smallest coin

**48\. Decode Ways (LC #91) \[Medium\]**
*   Python: dp\[i\] depends on single digit (1-9) and double digit (10-26)
*   Real-World: Text encoding/decoding ambiguity, parser state machines
*   Remember: '0' alone is invalid. Leading zeros kill paths. Check both s\[i\] and s\[i-1:i+1\]
*   Edge: Leading zero "0...", "10" vs "01", consecutive zeros, "00"
* * *
## PATTERN 13: DYNAMIC PROGRAMMING (2D)
**49\. Longest Common Subsequence (LC #1143) \[Medium\]**
*   Python: 2D dp, space-optimize to two rows. dp\[i\]\[j\] = dp\[i-1\]\[j-1\]+1 if match
*   Real-World: Diff tools (git diff), DNA sequence alignment, spell-check suggestions
*   Remember: Match → diagonal+1. No match → max(left, top). Space optimization: only need previous row
*   Edge: No common chars (LCS=0), one is substring of other, identical strings

**50\. Edit Distance (LC #72) \[Hard\]**
*   Python: dp\[i\]\[j\] = operations to convert word1\[:i\] to word2\[:j\]. Three choices: insert, delete, replace
*   Real-World: Spell checker ranking, DNA mutation distance, fuzzy string matching
*   Remember: Match = dp\[i-1\]\[j-1\]. Else: 1 + min(dp\[i-1\]\[j\], dp\[i\]\[j-1\], dp\[i-1\]\[j-1\]). Base cases = indices
*   Edge: One empty string (answer = len of other), identical strings (0), completely different

**51\. Unique Paths (LC #62) \[Medium\]**
*   Python: dp\[i\]\[j\] = dp\[i-1\]\[j\] + dp\[i\]\[j-1\], or `math.comb(m+n-2, m-1)` one-liner
*   Real-World: Robot navigation, grid-based routing, network packet path counting
*   Remember: Combinatorics shortcut: C(m+n-2, m-1). DP if obstacles exist (LC #63)
*   Edge: 1xn or mx1 grid (only one path), large grids (overflow in some languages, not Python)

**52\. Burst Balloons (LC #312) \[Hard\]**
*   Python: Interval DP. dp\[l\]\[r\] = max coins from bursting all balloons between l and r
*   Real-World: Optimal job sequencing with neighbor-dependent rewards, game theory
*   Remember: Think of LAST balloon to burst in range (not first). Multiply with boundaries nums\[l-1\]\*nums\[k\]\*nums\[r+1\]
*   Edge: Single balloon, two balloons, padding with 1s at boundaries
* * *
## PATTERN 14: GREEDY
**53\. Jump Game (LC #55) \[Medium\]**
*   Python: Track farthest reachable index, iterate and update
*   Real-World: Network hop analysis (can packet reach destination?), game level feasibility
*   Remember: At each index, farthest = max(farthest, i + nums\[i\]). If i > farthest, unreachable
*   Edge: Single element (always true), first element is 0 (false unless n=1), all 1s

**54\. Partition Labels (LC #763) \[Medium\]**
*   Python: dict for last occurrence of each char, expand partition end greedily
*   Real-World: Log file splitting (ensure each log type stays in one partition), data sharding
*   Remember: Track last occurrence of every char. Expand current partition end to max(end, last\[char\])
*   Edge: All unique chars (each is own partition), single char repeated (one partition)

**55\. Gas Station (LC #134) \[Medium\]**
*   Python: If total gas >= total cost, solution exists. Track running surplus, reset start on deficit
*   Real-World: Vehicle routing with refueling, circular delivery optimization
*   Remember: If total >= 0, answer exists and is UNIQUE. Reset start when tank goes negative
*   Edge: All stations same gas/cost, only one valid start, impossible (total < 0)

**56\. Meeting Rooms II (LC #253) \[Medium\]**
*   Python: Sort starts and ends separately, two-pointer to count overlaps. Or heapq for end times
*   Real-World: Conference room scheduling, server connection pool sizing, parallel job slots
*   Remember: Sort start\[\] and end\[\] separately. If start\[i\] < end\[j\], need new room. Else reuse (j++)
*   Edge: No overlaps (1 room), all overlap (n rooms), meetings with zero duration
* * *
## PATTERN 15: INTERVALS
**57\. Merge Intervals (LC #56) \[Medium\]**
*   Python: Sort by start, compare current.start with last\_merged.end
*   Real-World: Calendar merge (free/busy), IP range consolidation, time-series compression
*   Remember: Sort by start. If overlap: merged\[-1\]\[1\] = max(merged\[-1\]\[1\], current\[1\]). Else append
*   Edge: Single interval, all overlapping (merge to one), already sorted, touching boundaries \[1,2\]\[2,3\]

**58\. Non-Overlapping Intervals (LC #435) \[Medium\]**
*   Python: Sort by END time (greedy), count conflicts
*   Real-World: Job scheduling (maximize non-conflicting jobs), TV show recording conflicts
*   Remember: Sort by END (not start!). Greedy: keep interval that ends earliest. Count removals
*   Edge: No overlaps (remove 0), all same interval (remove n-1), nested intervals

**59\. Insert Interval (LC #57) \[Medium\]**
*   Python: Three phases: before (end < new\_start), merge (overlap), after (start > new\_end)
*   Real-World: Calendar event insertion, range-based access control updates
*   Remember: Collect all non-overlapping before, merge all overlapping, collect all after. Clean 3-pass logic
*   Edge: Insert at beginning, insert at end, new interval covers all existing

**60\. Car Pooling (LC #1094) \[Medium\]**
*   Python: Difference array / sweep line. Mark +passengers at start, -passengers at end
*   Real-World: Literal carpooling, elevator capacity, bandwidth allocation over time
*   Remember: Sweep line: at each point sum active passengers. Array\[start\] += p, Array\[end\] -= p
*   Edge: All same pickup/drop, capacity exactly met, trips are sorted vs unsorted
* * *
## PATTERN 16: TRIE (PREFIX TREE)
**61\. Implement Trie (LC #208) \[Medium\]**
*   Python: Nested `defaultdict` or class TrieNode with children dict + is\_end flag
*   Real-World: Autocomplete engines, spell checkers, IP routing tables (longest prefix match)
*   Remember: Each node has children dict (char → TrieNode) and is\_end boolean. Insert/search/startsWith
*   Edge: Empty string insertion, prefix is also a word, single character words

**62\. Word Search II (LC #212) \[Hard\]**
*   Python: Build Trie from words, DFS on board with Trie pruning. Remove word from Trie after found
*   Real-World: Multi-keyword search in documents, content moderation (banned word detection)
*   Remember: Trie + backtracking on grid. Prune: delete leaf nodes after finding word (optimization). Mark visited in-place
*   Edge: Same word found multiple paths (only add once), overlapping words, board smaller than word

**63\. Design Add and Search Words (LC #211) \[Medium\]**
*   Python: Trie with DFS for '.' wildcard (try all children at that level)
*   Real-World: Regex-lite matching, wildcard DNS resolution, pattern-based log search
*   Remember: '.' means branch to ALL children at current level. Recursive DFS for each wildcard position
*   Edge: All dots "..." (match any word of that length), dot at end, no matching word

**64\. Replace Words (LC #648) \[Medium\]**
*   Python: Build Trie from roots, for each word find shortest prefix in Trie
*   Real-World: Text summarization (replace long words with abbreviations), stemming in NLP
*   Remember: Walk each word char by char through Trie. First is\_end found = shortest root. Replace and stop
*   Edge: Word has no root (keep original), multiple roots match (shortest wins), root equals full word
* * *
## PATTERN 17: UNION-FIND (DISJOINT SET)
**65\. Accounts Merge (LC #721) \[Medium\]**
*   Python: Union-Find with email → owner mapping, group by root at end
*   Real-World: User identity resolution (merge accounts across platforms), entity deduplication
*   Remember: Union emails that share an account. Group all emails by find(root). Sort each group
*   Edge: Same email in multiple accounts, single email accounts, no merging needed

**66\. Redundant Connection (LC #684) \[Medium\]**
*   Python: Union-Find, first edge where find(u) == find(v) before union is the answer
*   Real-World: Network loop detection, removing redundant connections to form spanning tree
*   Remember: Process edges in order. If u and v already connected (same root), this edge creates cycle
*   Edge: Tree with exactly one extra edge (guaranteed), edge at the beginning vs end

**67\. Number of Connected Components (LC #323) \[Medium\]**
*   Python: Union-Find with rank, count components = n - successful\_unions
*   Real-World: Social network clustering, network segmentation analysis
*   Remember: Start with n components. Each successful union reduces by 1. Or: count unique roots at end
*   Edge: Fully connected (1 component), no edges (n components), self-loops

**68\. Graph Valid Tree (LC #261) \[Medium\]**
*   Python: Valid tree = connected + no cycles = (n-1 edges + all connected via Union-Find)
*   Real-World: Validating hierarchy structures, checking acyclic dependency graphs
*   Remember: Tree conditions: exactly n-1 edges AND fully connected. Union-Find detects cycles during edge processing
*   Edge: Empty graph (n=1 is valid), disconnected components, extra edges
* * *
## PATTERN 18: BIT MANIPULATION
**69\. Single Number (LC #136) \[Easy\]**
*   Python: `functools.reduce(operator.xor, nums)` one-liner
*   Real-World: Error detection (parity bits), finding corrupted packet in duplicate stream
*   Remember: XOR properties: a^a=0, a^0=a, commutative+associative. All pairs cancel out
*   Edge: Single element array, large numbers, negative numbers (XOR still works in Python)

**70\. Counting Bits (LC #338) \[Easy\]**
*   Python: dp\[i\] = dp\[i >> 1\] + (i & 1), or dp\[i\] = dp\[i & (i-1)\] + 1
*   Real-World: Hamming weight tables in networking, population count for SIMD operations
*   Remember: Relationship: i's bit count = (i//2)'s count + last bit. Build table bottom-up O(n)
*   Edge: n=0 (just \[0\]), powers of 2 (exactly 1 bit), n=1

**71\. Reverse Bits (LC #190) \[Easy\]**
*   Python: Bit-by-bit: result = (result << 1) | (n & 1); n >>= 1 for 32 iterations
*   Real-World: Network byte order conversion (endianness), cryptographic bit permutations
*   Remember: Extract LSB with n&1, shift result left, OR it in. Do exactly 32 times (fixed width)
*   Edge: All zeros, all ones, alternating bits

**72\. Missing Number (LC #268) \[Easy\]**
*   Python: XOR all indices AND all values, or math: n\*(n+1)//2 - sum(nums)
*   Real-World: Data integrity check (detect missing packet in sequence), census gap detection
*   Remember: XOR approach: xor(0..n) ^ xor(nums) = missing. Math approach: expected\_sum - actual\_sum
*   Edge: Missing 0, missing n (last), single element \[0\] or \[1\]
* * *
## PATTERN 19: LINKED LIST MANIPULATION
**73\. Reverse Linked List (LC #206) \[Easy\]**
*   Python: Iterative with prev/curr/next trio, or recursive ([head.next.next](http://head.next.next) = head)
*   Real-World: Undo stack implementation, reversing transaction chain
*   Remember: Save next, point curr to prev, advance. Three pointers always. Don't lose reference to next
*   Edge: Empty list, single node, two nodes

**74\. LRU Cache (LC #146) \[Medium\]**
*   Python: `collections.OrderedDict` with move\_to\_end(), or HashMap + doubly linked list
*   Real-World: Browser cache, database query cache, CPU cache eviction
*   Remember: OrderedDict.move\_to\_end(key) on get, popitem(last=False) on evict. O(1) everything
*   Edge: Capacity 1, get non-existent key, put existing key (update, don't evict)

**75\. Merge Two Sorted Lists (LC #21) \[Easy\]**
*   Python: Dummy head node, compare and link smaller, attach remainder
*   Real-World: Merge sort merge step, combining sorted search results from multiple shards
*   Remember: dummy = ListNode(0), tail pointer advances. At end, attach whichever list remains
*   Edge: One empty list, both empty, all elements from one list come first

**76\. Reorder List (LC #143) \[Medium\]**
*   Python: Find middle (fast/slow) → reverse second half → merge alternating
*   Real-World: Memory-efficient interleaving, playlist shuffle (alternating new/old)
*   Remember: Three steps: (1) split at middle, (2) reverse second half, (3) interleave merge. Modify in-place
*   Edge: Single node, two nodes, odd vs even length
* * *
## PATTERN 20: MATRIX / 2D TRAVERSAL
**77\. Rotate Image (LC #48) \[Medium\]**
*   Python: Transpose (swap matrix\[i\]\[j\] with matrix\[j\]\[i\]) then reverse each row
*   Real-World: Image rotation in CV, game board rotation, screen orientation change
*   Remember: 90 clockwise = transpose + reverse rows. 90 counter-clockwise = transpose + reverse columns
*   Edge: 1x1 matrix, 2x2 matrix, non-square (can't rotate in-place)

**78\. Spiral Matrix (LC #54) \[Medium\]**
*   Python: Four boundaries (top, bottom, left, right), shrink after each direction
*   Real-World: Printer rasterization, CNC machine path, snake game board traversal
*   Remember: Go right→down→left→up, shrink boundary after each. Check boundary still valid after each shrink
*   Edge: Single row, single column, 1x1, non-square matrix

**79\. Set Matrix Zeroes (LC #73) \[Medium\]**
*   Python: Use first row/col as markers, separate flag for row0/col0
*   Real-World: Spreadsheet formula propagation (zeroing dependent cells), game of life neighbor marking
*   Remember: O(1) space: first row/col store which rows/cols to zero. Process non-first row/col first on cleanup
*   Edge: No zeros, entire matrix zeros, zeros only in first row/col

**80\. Search a 2D Matrix (LC #74) \[Medium\]**
*   Python: Treat as 1D sorted array. index → row = mid//cols, col = mid%cols
*   Real-World: Searching in paginated sorted data, matrix-stored sorted databases
*   Remember: Virtual 1D index mapping: row = mid // n, col = mid % n. Standard binary search
*   Edge: Single row, single column, target smaller/larger than all elements
* * *
**Total: 20 Patterns, 80 Questions. All pattern-wise, Python-contextualized, interview-ready.**