# Blind 75 — New Question Bank Creation — 2026-08-25

Scope: creation of `Data Structures & Algorithms/Blind_75_Question_Bank.md`,
a second, separate DSA question bank at the user's explicit request,
alongside (not replacing) the existing 100-problem, pattern-organized
`DSA_Pattern_Based_Question_Bank.md`. The user was asked and explicitly
chose "add alongside as a second, separate list" over replacing the
existing bank.

## Content and provenance

75 problems, organized by data-structure category (Array, Binary,
Dynamic Programming, Graph, Interval, Linked List, Matrix, String, Tree,
Heap) — the traditional grouping this specific, well-known list has
circulated under since it was first compiled and shared publicly in
2018. Only problem titles are listed (short, functional names — not
creative expression), grouped and introduced with this guide's own
original framing text; no narrative, commentary, or descriptive prose
from any specific source's write-up was reproduced.

Two independent attempts were made to verify this reconstruction against
a live, canonical source before writing it:

- `https://www.techinterviewhandbook.org/best-practice-questions/` —
  returned HTTP 403 to an automated fetch.
- A candidate GitHub-hosted mirror — returned HTTP 404 (wrong path, no
  working alternative found in the time available).

Neither succeeded, so this list is presented as a high-confidence
reconstruction from training knowledge, not a verified-exact
reproduction — this limitation is stated explicitly and prominently in
the guide's own top-of-file note, consistent with how this repo has
handled every other unverifiable citation this session (the `leetcode.com`
domain-wide block, the DSA pattern bank's own equivalent note). The note
specifically flags that a handful of premium-locked problems are the
most likely to vary between different public reproductions of this list,
while the core, non-premium majority is consistent across essentially
every version encountered.

## Verification performed

- Counted the numbered problem entries directly (`grep -c`): confirmed
  exactly 75.
- Generated the guide's Table of Contents with `scripts/add_toc.py`.
- Re-ran `scripts/check_internal_links.py`, `scripts/check_duplicate_headings.py`,
  and `scripts/check_code_fences.py` across all 43 repository markdown
  files — clean.
- Re-ran `markdownlint-cli2` across all 43 files — 0 issues.
- Ran `lychee` against the new guide: 91 link occurrences, 76 excluded
  (the 75 `leetcode.com` problem links plus the `leetcode.com` homepage
  link, both already covered by the exclusion added in the prior DSA
  question bank pass), 15 checked and OK, 0 errors.

## Integration

- Added a second bullet to the "Data Structures & Algorithms" section of
  the top-level `README.md`'s "Guides by topic" list, and updated that
  section's intro sentence to describe both question banks.
- Updated `AUDIT.md`'s excluded-files note, repository-wide counts (39 →
  40 files, question banks 2 → 3, question total updated to mention both
  DSA banks), and added this dated audit file to the History section.
- No changes were made to `DSA_Pattern_Based_Question_Bank.md` — the two
  banks are independent, deliberately organized differently (algorithmic
  pattern vs. data-structure category), and inevitably overlap in which
  individual problems they include, which is expected and not treated as
  duplication to resolve.

## Not done in this pass

- No individual `leetcode.com` link was confirmed to resolve to its
  intended problem — same limitation as the pattern-based bank.
- The exact 75-problem composition was not cross-checked against a live
  authoritative source, for the reasons above — this is a documented,
  known limitation, not an oversight.
