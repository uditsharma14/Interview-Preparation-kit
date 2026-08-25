# Data Structures & Algorithms — Pattern-Based Question Bank (Top 100)

> **Format:** A curated practice list, not worked solutions — 100 problems grouped into 20 recognizable patterns, the same style of preparation popularized by "Grokking the Coding Interview" and NeetCode: learn the pattern once, then recognize it across many differently-worded problems, instead of memorizing 100 unrelated solutions. Pair this with [Computer Science Fundamentals](../Computer%20Science%20Fundamentals/Computer_Science_Fundamentals_Interview_Prep.md) for the underlying Big-O/data-structure concepts these patterns assume. **Target level:** Basic (pattern recognition) → Staff (choosing and justifying the right pattern under novel constraints). **Last verified:** 2026-08-25.

**A note on the links below:** LeetCode blocks automated link-checking tools (confirmed via multiple independent, deliberately-attempted fetches — every request returned HTTP 403, the standard signature of bot-blocking rather than a removed page), so the individual problem links here could not be mechanically verified the way every other citation in this repo is. Each link is generated directly and mechanically from the problem's well-established, stable, public title using LeetCode's own standard URL format — if a specific link ever seems to land on the wrong problem, search the title directly on leetcode.com rather than trusting the link blindly.

How to use this: for each pattern, **Recognize it when** names the phrasing/constraints in a problem statement that signal this is the pattern to reach for — that recognition skill, not the specific 100 problems, is the actual thing being practiced. Work through a pattern's problems together, back to back, before moving to the next pattern — solving them in the scrambled order they'd appear on a random problem list defeats the entire point of pattern-based practice.

<!-- toc -->
## Table of Contents

- [Array & String Patterns](#array--string-patterns)
  - [Two Pointers](#two-pointers)
  - [Sliding Window](#sliding-window)
  - [Cyclic Sort](#cyclic-sort)
- [Linked List Patterns](#linked-list-patterns)
  - [Fast & Slow Pointers](#fast--slow-pointers)
  - [In-place Reversal of a Linked List](#in-place-reversal-of-a-linked-list)
  - [Linked List Manipulation](#linked-list-manipulation)
- [Interval Patterns](#interval-patterns)
  - [Merge Intervals](#merge-intervals)
- [Tree & Graph Patterns](#tree--graph-patterns)
  - [Tree BFS](#tree-bfs)
  - [Tree DFS](#tree-dfs)
  - [Graphs (BFS / DFS / Topological Sort / Union-Find)](#graphs-bfs--dfs--topological-sort--union-find)
  - [Trie](#trie)
- [Searching & Heap Patterns](#searching--heap-patterns)
  - [Modified Binary Search](#modified-binary-search)
  - [Top K Elements (Heap)](#top-k-elements-heap)
  - [K-way Merge](#k-way-merge)
- [Combinatorial Patterns](#combinatorial-patterns)
  - [Subsets & Backtracking](#subsets--backtracking)
- [Dynamic Programming Patterns](#dynamic-programming-patterns)
  - [1D Dynamic Programming](#1d-dynamic-programming)
  - [2D Dynamic Programming](#2d-dynamic-programming)
- [Greedy & Bit Manipulation](#greedy--bit-manipulation)
  - [Greedy](#greedy)
  - [Bit Manipulation](#bit-manipulation)
- [Stack Patterns](#stack-patterns)
  - [Monotonic Stack / Stack-Based](#monotonic-stack--stack-based)
- [Recommended practice order](#recommended-practice-order)
- [Sources & Further Reading](#sources--further-reading)

<!-- /toc -->

---

## Array & String Patterns

### Two Pointers

Two indices move through a sorted (or sortable) array or string, from either end or in the same direction, to avoid a nested loop's O(n²) cost. **Recognize it when:** the input is sorted, or can be sorted without losing what the problem asks; the problem asks for a pair, triplet, or subrange satisfying a sum/comparison condition. Typical complexity: O(n) or O(n log n) after an initial sort, versus O(n²) for the brute-force nested-loop version.

1. [Two Sum II - Input Array Is Sorted](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/)
2. [3Sum](https://leetcode.com/problems/3sum/)
3. [Container With Most Water](https://leetcode.com/problems/container-with-most-water/)
4. [Trapping Rain Water](https://leetcode.com/problems/trapping-rain-water/)
5. [Valid Palindrome](https://leetcode.com/problems/valid-palindrome/)
6. [Remove Duplicates from Sorted Array](https://leetcode.com/problems/remove-duplicates-from-sorted-array/)

### Sliding Window

A window of elements expands and contracts over a contiguous run of an array or string, tracking a running property (sum, character count, distinct-element count) incrementally instead of recomputing it from scratch for every possible window. **Recognize it when:** the problem asks for the longest/shortest/best contiguous subarray or substring satisfying some condition. Typical complexity: O(n) — each element enters and leaves the window at most once, versus O(n²) or worse for recomputing each window's property independently.

1. [Best Time to Buy and Sell Stock](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/)
2. [Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/)
3. [Longest Repeating Character Replacement](https://leetcode.com/problems/longest-repeating-character-replacement/)
4. [Minimum Window Substring](https://leetcode.com/problems/minimum-window-substring/)
5. [Permutation in String](https://leetcode.com/problems/permutation-in-string/)
6. [Sliding Window Maximum](https://leetcode.com/problems/sliding-window-maximum/)

### Cyclic Sort

Exploits an array known to contain numbers from a specific, bounded range (commonly `1` to `n`) by placing each number directly at its "correct" index in one pass, then scanning once more to spot whatever's out of place — missing, duplicated. **Recognize it when:** the problem guarantees the input contains numbers in a known range like `[1, n]` and asks for a missing or duplicate value. Typical complexity: O(n) time, O(1) extra space — the array itself is reused as the lookup structure, avoiding a separate hash set.

1. [Missing Number](https://leetcode.com/problems/missing-number/)
2. [Find All Numbers Disappeared in an Array](https://leetcode.com/problems/find-all-numbers-disappeared-in-an-array/)
3. [First Missing Positive](https://leetcode.com/problems/first-missing-positive/)
4. [Find All Duplicates in an Array](https://leetcode.com/problems/find-all-duplicates-in-an-array/)

---

## Linked List Patterns

### Fast & Slow Pointers

Two pointers traverse a linked list (or an implicit sequence, like repeated digit-sum operations) at different speeds — commonly one step and two steps at a time — so that if the sequence loops, the faster pointer eventually laps the slower one, detecting a cycle without any extra memory. **Recognize it when:** the problem involves a linked list and asks about a cycle, the middle element, or "does this sequence eventually repeat." Typical complexity: O(n) time, O(1) space — the alternative, storing every visited node in a hash set, works but costs O(n) space this pattern avoids entirely.

1. [Linked List Cycle](https://leetcode.com/problems/linked-list-cycle/)
2. [Linked List Cycle II](https://leetcode.com/problems/linked-list-cycle-ii/)
3. [Middle of the Linked List](https://leetcode.com/problems/middle-of-the-linked-list/)
4. [Happy Number](https://leetcode.com/problems/happy-number/)
5. [Find the Duplicate Number](https://leetcode.com/problems/find-the-duplicate-number/)

### In-place Reversal of a Linked List

Reverses a linked list, or a specific portion of one, by walking it once and re-pointing each node's `next` reference as you go, rather than allocating a new list or using extra storage. **Recognize it when:** the problem explicitly asks to reverse a list, or a sublist between two positions, in place. Typical complexity: O(n) time, O(1) extra space — the classic trap is losing the reference to the rest of the list before re-pointing a node's `next`, which silently truncates it.

1. [Reverse Linked List](https://leetcode.com/problems/reverse-linked-list/)
2. [Reverse Linked List II](https://leetcode.com/problems/reverse-linked-list-ii/)
3. [Reverse Nodes in k-Group](https://leetcode.com/problems/reverse-nodes-in-k-group/)
4. [Swap Nodes in Pairs](https://leetcode.com/problems/swap-nodes-in-pairs/)

### Linked List Manipulation

The broader set of linked-list problems that aren't purely about reversal or cycle detection — merging, arithmetic performed digit-by-digit across nodes, or copying a list whose nodes carry extra pointers. **Recognize it when:** the problem involves combining, restructuring, or deep-copying a linked list, often with a dummy head node to simplify edge cases at the list's start. Typical complexity: O(n) or O(n + m) for merging two lists of length n and m.

1. [Merge Two Sorted Lists](https://leetcode.com/problems/merge-two-sorted-lists/)
2. [Remove Nth Node From End of List](https://leetcode.com/problems/remove-nth-node-from-end-of-list/)
3. [Add Two Numbers](https://leetcode.com/problems/add-two-numbers/)
4. [Copy List with Random Pointer](https://leetcode.com/problems/copy-list-with-random-pointer/)

---

## Interval Patterns

### Merge Intervals

Sorting a collection of intervals by start time turns "do these overlap" into a simple, single left-to-right scan comparing each interval only against the one immediately before it, rather than checking every pair. **Recognize it when:** the problem gives a list of ranges/intervals and asks to merge overlapping ones, insert a new one, count overlaps, or schedule against them. Typical complexity: O(n log n), dominated by the initial sort — the scan itself after sorting is O(n).

1. [Merge Intervals](https://leetcode.com/problems/merge-intervals/)
2. [Insert Interval](https://leetcode.com/problems/insert-interval/)
3. [Non-overlapping Intervals](https://leetcode.com/problems/non-overlapping-intervals/)
4. [Meeting Rooms II](https://leetcode.com/problems/meeting-rooms-ii/)
5. [Interval List Intersections](https://leetcode.com/problems/interval-list-intersections/)

---

## Tree & Graph Patterns

### Tree BFS

Visits a tree level by level using a queue — process every node currently in the queue (one full level), then enqueue their children as the next level, repeating until the queue empties. **Recognize it when:** the problem specifically needs level-by-level information — the value at each depth, the level order itself, or "the last node visible looking from one side." Typical complexity: O(n) time and O(w) space, where w is the tree's maximum width (the widest level).

1. [Binary Tree Level Order Traversal](https://leetcode.com/problems/binary-tree-level-order-traversal/)
2. [Binary Tree Zigzag Level Order Traversal](https://leetcode.com/problems/binary-tree-zigzag-level-order-traversal/)
3. [Minimum Depth of Binary Tree](https://leetcode.com/problems/minimum-depth-of-binary-tree/)
4. [Binary Tree Right Side View](https://leetcode.com/problems/binary-tree-right-side-view/)

### Tree DFS

Recursively (or with an explicit stack) descends into a tree, typically all the way to a leaf, before backtracking — natural for problems that need to accumulate or check something along a root-to-leaf path, or compare a whole subtree's shape against a rule. **Recognize it when:** the problem talks about paths, subtrees, or a property that has to hold recursively (a valid BST, a common ancestor, matching structure). Typical complexity: O(n) time, O(h) space for the recursion stack, where h is the tree's height (O(log n) balanced, O(n) worst case for a degenerate tree).

1. [Maximum Depth of Binary Tree](https://leetcode.com/problems/maximum-depth-of-binary-tree/)
2. [Path Sum](https://leetcode.com/problems/path-sum/)
3. [Diameter of Binary Tree](https://leetcode.com/problems/diameter-of-binary-tree/)
4. [Validate Binary Search Tree](https://leetcode.com/problems/validate-binary-search-tree/)
5. [Lowest Common Ancestor of a Binary Tree](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/)
6. [Serialize and Deserialize Binary Tree](https://leetcode.com/problems/serialize-and-deserialize-binary-tree/)

### Graphs (BFS / DFS / Topological Sort / Union-Find)

The same BFS/DFS traversal ideas generalized from trees to arbitrary graphs, which can have cycles and more than one path between two nodes — plus two graph-specific techniques: topological sort (ordering nodes so every directed edge points forward, only possible if the graph has no cycle) and Union-Find (efficiently tracking which nodes are already connected as edges are added one at a time). **Recognize it when:** the problem involves a grid, an adjacency list, or an explicit dependency/prerequisite relationship, and asks about connectivity, reachability, a valid ordering, or the number of separate groups. Typical complexity: O(V + E) for BFS/DFS and topological sort; near O(α(n)) per operation for Union-Find with path compression, effectively constant in practice.

1. [Number of Islands](https://leetcode.com/problems/number-of-islands/)
2. [Clone Graph](https://leetcode.com/problems/clone-graph/)
3. [Course Schedule](https://leetcode.com/problems/course-schedule/)
4. [Course Schedule II](https://leetcode.com/problems/course-schedule-ii/)
5. [Pacific Atlantic Water Flow](https://leetcode.com/problems/pacific-atlantic-water-flow/)
6. [Rotting Oranges](https://leetcode.com/problems/rotting-oranges/)
7. [Redundant Connection](https://leetcode.com/problems/redundant-connection/)

### Trie

A tree in which each node represents one character, and every path from the root spells out a prefix — built specifically so that checking whether a word or prefix exists takes time proportional only to the word's length, not the number of words stored. **Recognize it when:** the problem is fundamentally about prefixes — autocomplete, a dictionary of valid words, or searching a grid for multiple words at once. Typical complexity: O(L) per insert/search, where L is the word's length, independent of how many other words are stored.

1. [Implement Trie (Prefix Tree)](https://leetcode.com/problems/implement-trie-prefix-tree/)
2. [Word Search II](https://leetcode.com/problems/word-search-ii/)
3. [Design Add and Search Words Data Structure](https://leetcode.com/problems/design-add-and-search-words-data-structure/)

---

## Searching & Heap Patterns

### Modified Binary Search

The classic halve-the-search-space binary search, adapted to conditions beyond "find this exact value in a plain sorted array" — a sorted array that's been rotated, a 2D matrix sorted row-by-row and column-by-column, or searching for a boundary (the first/last position satisfying a condition) rather than one exact value. **Recognize it when:** the input is sorted, or "sorted with a twist" (rotated, row/column-sorted), and a brute-force scan would be O(n) when the problem's constraints strongly suggest a faster answer is expected. Typical complexity: O(log n), or O(log(min(m, n))) for a 2D variant.

1. [Binary Search](https://leetcode.com/problems/binary-search/)
2. [Search in Rotated Sorted Array](https://leetcode.com/problems/search-in-rotated-sorted-array/)
3. [Find Minimum in Rotated Sorted Array](https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/)
4. [Search a 2D Matrix](https://leetcode.com/problems/search-a-2d-matrix/)
5. [Find First and Last Position of Element in Sorted Array](https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/)
6. [Median of Two Sorted Arrays](https://leetcode.com/problems/median-of-two-sorted-arrays/)

### Top K Elements (Heap)

A heap (priority queue) of bounded size k keeps track of the k largest, smallest, or most-frequent elements seen so far, without ever sorting or storing the entire dataset. **Recognize it when:** the problem specifically asks for "the k-th," "the top k," or a running statistic (a live median) over a stream of values. Typical complexity: O(n log k) — cheaper than the O(n log n) a full sort would cost when k is much smaller than n.

1. [Kth Largest Element in an Array](https://leetcode.com/problems/kth-largest-element-in-an-array/)
2. [Top K Frequent Elements](https://leetcode.com/problems/top-k-frequent-elements/)
3. [Find Median from Data Stream](https://leetcode.com/problems/find-median-from-data-stream/)
4. [K Closest Points to Origin](https://leetcode.com/problems/k-closest-points-to-origin/)
5. [Task Scheduler](https://leetcode.com/problems/task-scheduler/)

### K-way Merge

Generalizes merging two sorted lists (the core step of merge sort) to merging k sorted lists at once, using a heap to always pick the smallest next element across all k lists in O(log k) instead of scanning all k candidates in O(k) every time. **Recognize it when:** the problem gives multiple already-sorted lists, arrays, or a matrix sorted along both axes, and asks for a combined ordering or a specific rank within it. Typical complexity: O(n log k), where n is the total number of elements across all k lists.

1. [Merge k Sorted Lists](https://leetcode.com/problems/merge-k-sorted-lists/)
2. [Kth Smallest Element in a Sorted Matrix](https://leetcode.com/problems/kth-smallest-element-in-a-sorted-matrix/)
3. [Smallest Range Covering Elements from K Lists](https://leetcode.com/problems/smallest-range-covering-elements-from-k-lists/)

---

## Combinatorial Patterns

### Subsets & Backtracking

Explores every valid way to build up a combination, permutation, or arrangement by making a choice, recursing into the consequences of that choice, and undoing it ("backtracking") to try the next option — pruning a branch early the moment it's clear it can't lead to a valid answer. **Recognize it when:** the problem asks to enumerate *all* subsets, permutations, combinations, or valid arrangements satisfying some constraint, not just count or find one. Typical complexity: exponential (O(2ⁿ) for subsets, O(n!) for permutations) — inherent to enumerating every possibility, not a sign the approach is wrong; the skill being tested is pruning invalid branches as early as possible, not avoiding exponential time altogether.

1. [Subsets](https://leetcode.com/problems/subsets/)
2. [Permutations](https://leetcode.com/problems/permutations/)
3. [Combination Sum](https://leetcode.com/problems/combination-sum/)
4. [Word Search](https://leetcode.com/problems/word-search/)
5. [Letter Combinations of a Phone Number](https://leetcode.com/problems/letter-combinations-of-a-phone-number/)
6. [N-Queens](https://leetcode.com/problems/n-queens/)
7. [Palindrome Partitioning](https://leetcode.com/problems/palindrome-partitioning/)

---

## Dynamic Programming Patterns

### 1D Dynamic Programming

Breaks a problem down into overlapping subproblems indexed by a single value (typically a position or a target amount), where each subproblem's answer is computed once from smaller subproblems' already-computed answers and reused, rather than recomputed every time it comes up. **Recognize it when:** a brute-force recursive solution would revisit the exact same subproblem repeatedly (visible as exponential time with heavy redundant recursive calls), and the problem asks for an optimal count, a way, or a minimum/maximum over a 1D sequence. Typical complexity: O(n) or O(n × target) time, down from exponential for the naive recursive version.

1. [Climbing Stairs](https://leetcode.com/problems/climbing-stairs/)
2. [House Robber](https://leetcode.com/problems/house-robber/)
3. [Coin Change](https://leetcode.com/problems/coin-change/)
4. [Longest Increasing Subsequence](https://leetcode.com/problems/longest-increasing-subsequence/)
5. [Word Break](https://leetcode.com/problems/word-break/)
6. [Decode Ways](https://leetcode.com/problems/decode-ways/)
7. [Maximum Subarray](https://leetcode.com/problems/maximum-subarray/)

### 2D Dynamic Programming

The same overlapping-subproblems idea, but each subproblem is indexed by two values instead of one — commonly a position in each of two strings, or a position plus a remaining budget/capacity. **Recognize it when:** the problem compares or combines two sequences (two strings, a grid of cells) and asks for an optimal alignment, transformation cost, or count of ways, and a 1D state clearly isn't enough to capture the problem. Typical complexity: O(m × n) time and space for two sequences of length m and n, sometimes reducible to O(min(m, n)) space by keeping only the previous row.

1. [Unique Paths](https://leetcode.com/problems/unique-paths/)
2. [Longest Common Subsequence](https://leetcode.com/problems/longest-common-subsequence/)
3. [Edit Distance](https://leetcode.com/problems/edit-distance/)
4. [Partition Equal Subset Sum](https://leetcode.com/problems/partition-equal-subset-sum/)
5. [Longest Palindromic Substring](https://leetcode.com/problems/longest-palindromic-substring/)
6. [Best Time to Buy and Sell Stock with Cooldown](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-cooldown/)

---

## Greedy & Bit Manipulation

### Greedy

Makes the locally-best choice at each step, without reconsidering it later, and relies on a problem-specific proof (not a general guarantee) that the accumulated local choices actually produce a global optimum. **Recognize it when:** an optimal-substructure argument can be made informally ("it's never worse to do X now"), the problem is about reachability, scheduling, or partitioning under a simple rule, and a full dynamic-programming table feels like overkill for how the problem actually behaves. Typical complexity: O(n) or O(n log n), usually just the cost of an initial sort plus one linear pass — but a greedy approach that seems intuitively right without an actual proof is a common, genuine source of subtly wrong solutions.

1. [Jump Game](https://leetcode.com/problems/jump-game/)
2. [Jump Game II](https://leetcode.com/problems/jump-game-ii/)
3. [Gas Station](https://leetcode.com/problems/gas-station/)
4. [Partition Labels](https://leetcode.com/problems/partition-labels/)

### Bit Manipulation

Uses bitwise operators (`XOR`, `AND`, `OR`, shifts) directly on a number's binary representation, exploiting properties like XOR canceling out a value paired with itself, to solve a problem in O(1) extra space that would otherwise need a hash set or array. **Recognize it when:** the problem involves finding a single unpaired element among duplicates, counting set bits, or otherwise asks for something achievable through raw binary representation rather than arithmetic. Typical complexity: O(n) time, O(1) space — the space savings over a hash-set-based approach is usually the entire point.

1. [Single Number](https://leetcode.com/problems/single-number/)
2. [Number of 1 Bits](https://leetcode.com/problems/number-of-1-bits/)
3. [Counting Bits](https://leetcode.com/problems/counting-bits/)
4. [Sum of Two Integers](https://leetcode.com/problems/sum-of-two-integers/)

---

## Stack Patterns

### Monotonic Stack / Stack-Based

A stack that's kept strictly increasing or decreasing as elements are pushed — popping off elements that violate that order before pushing the new one — used to answer "what's the nearest bigger/smaller element" for every position in a single linear pass, instead of scanning outward from each position independently. **Recognize it when:** the problem asks for the next/previous greater or smaller element, needs matched pairs (parentheses, brackets), or asks for a maximal rectangle/area computed from a sequence of heights. Typical complexity: O(n) — each element is pushed and popped from the stack at most once, versus O(n²) for checking every pair of positions directly.

1. [Valid Parentheses](https://leetcode.com/problems/valid-parentheses/)
2. [Daily Temperatures](https://leetcode.com/problems/daily-temperatures/)
3. [Largest Rectangle in Histogram](https://leetcode.com/problems/largest-rectangle-in-histogram/)
4. [Min Stack](https://leetcode.com/problems/min-stack/)

---

## Recommended practice order

1. **Array & String, Linked List, and Stack patterns first** — they build the pointer/index manipulation instincts every later pattern assumes.
2. **Tree & Graph patterns next** — BFS/DFS on a tree generalizes directly into BFS/DFS on a graph, so the tree patterns are the on-ramp, not a separate topic to learn from scratch.
3. **Searching & Heap patterns alongside Tree & Graph** — Top K and K-way Merge both lean on the same heap mechanics.
4. **Combinatorial (Subsets & Backtracking) before Dynamic Programming** — many DP problems are a brute-force backtracking solution's exponential redundancy, made tractable; recognizing that redundancy is easier once backtracking itself is comfortable.
5. **Dynamic Programming last, and expect it to take the longest** — it's the pattern with the least visually obvious "tell" in a problem statement, and the one most worth spaced repetition on rather than a single pass.
6. **Greedy and Bit Manipulation throughout, opportunistically** — they're narrower, faster to internalize, and don't need to wait for the rest of the sequence.

For each problem: identify the pattern *before* looking at it as an individual puzzle, state the target time/space complexity out loud before writing any code, and only check a reference solution after a genuine attempt — pattern recognition is a recall skill, and skipping straight to a solution trains recognizing the *solution*, not the *pattern*.

## Sources & Further Reading

| Topic | Link |
|---|---|
| NeetCode — pattern-organized problem lists and video explanations | https://neetcode.io/ |
| Educative — Grokking the Coding Interview (origin of much of this pattern taxonomy) | https://www.educative.io/courses/grokking-coding-interview |
| Tech Interview Handbook — Grind 75 (a widely-used curated problem list this bank draws on for problem selection) | https://www.techinterviewhandbook.org/grind75/ |
| LeetCode — problem platform (individual links above; see the note at the top of this guide on why they couldn't be automated-link-checked) | https://leetcode.com/ |
