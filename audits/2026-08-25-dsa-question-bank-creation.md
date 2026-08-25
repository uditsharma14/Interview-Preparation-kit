# Data Structures & Algorithms — New Question Bank Creation — 2026-08-25

Scope: creation of a new `Data Structures & Algorithms` folder and
`DSA_Pattern_Based_Question_Bank.md`, at the user's request for a "top 100
problems" DSA section organized by category and pattern-based
preparation. Two scoping decisions were confirmed with the user before
writing: a curated list (pattern description + problem titles/links, no
worked solutions or per-problem hints) rather than full worked answers,
and a new top-level folder rather than folding into Computer Science
Fundamentals.

## Content

100 problems across 20 patterns, grouped into 9 category sections (Array
& String, Linked List, Interval, Tree & Graph, Searching & Heap,
Combinatorial, Dynamic Programming, Greedy & Bit Manipulation, Stack).
Each pattern has a short description of the underlying technique, a
**Recognize it when** line naming the problem-statement signal that
should trigger reaching for that pattern, a typical complexity class, and
a numbered list of representative problems. This matches the existing
`System Design/System_Design_Interview_Question_Bank.md`'s "practice
prompts, not worked answers" format and target-level framing, adapted for
DSA content specifically (pattern recognition as the explicit unit of
practice, per "Grokking the Coding Interview"'s and NeetCode's
established teaching model, not this repo inventing a new taxonomy).

## Citation limitation: leetcode.com blocks all automated verification

Every citation in this repo up to this point has been verified live
before being included, via `curl` and/or an independent fetch tool. That
was not possible here: `leetcode.com` returned HTTP 403 to every
attempted automated fetch (curl with a browser user agent, and a second,
independent fetch tool) across a representative sample of problem-page
URLs, and there is no reason to expect the remaining ~90 to behave
differently — this is the identical bot-blocking signature already
documented for several other domains in `.lychee.toml` (oreilly.com,
netflixtechblog.com, and others), not evidence any specific page is gone.

Given this, the 100 individual problem links could not be verified
one-by-one the way, for example, every Angular/React citation was earlier
this session. Instead:

- Each link was generated mechanically from the problem's well-known,
  stable, public title using LeetCode's own standard URL slug format
  (lowercase, hyphenated, punctuation stripped) — the same deterministic
  transformation LeetCode itself applies, not a guess.
- The 100 problems themselves are drawn from extremely well-established,
  long-standing public curricula (the pattern taxonomy popularized by
  "Grokking the Coding Interview," NeetCode's pattern-organized lists,
  and the "Grind 75" curated list), not invented or uncertain selections
  — the risk here is a possible slug-formatting mismatch on an individual
  link, not the problem's existence or title being wrong.
- `leetcode.com` was added to `.lychee.toml`'s `exclude` list, following
  the exact same pattern already established there for other confirmed-live,
  bot-blocking domains, with a comment explaining why this entry is
  different (no per-URL confirmation was possible, only domain-level).
- An explicit, honest note was added at the top of the guide itself
  telling the reader these links weren't mechanically verified and to
  search by title on leetcode.com if a specific link seems wrong.

This is a deliberate, documented departure from this session's usual
"verify before citing" standard, made necessary by the citation target
itself being unverifiable by any tool available in this environment —
not a relaxation of the standard for future work.

## Bug found and fixed: `scripts/check_duplicate_headings.py`

Running the duplicate-heading check against the new guide immediately
flagged a false positive: `### 1D Dynamic Programming` and `### 2D
Dynamic Programming` were reported as duplicates. Root cause:
`LEADING_NUMBER_RE` (`^(?:q?\.?\s*)?\d+[.):]?\s*`) is meant to strip a
numbered-list prefix like `"13. "` before comparing heading text, so that
renumbered questions with identical text aren't flagged as new
duplicates — but both the punctuation group and the trailing whitespace
group are optional, so a bare leading digit immediately followed by a
letter (no separator at all, as in `"1D"`) was still being stripped,
leaving `"D Dynamic Programming"` for both headings and producing a
collision neither heading actually has.

Fixed by requiring the digit to be followed by either punctuation-plus-
optional-whitespace or at least one whitespace character before it's
treated as list numbering: `^(?:q?\.?\s*)?\d+(?:[.):]\s*|\s+)`. Verified
the fix resolves the false positive and re-ran the check across all 39
repository markdown files — zero duplicates found, confirming the fix
didn't introduce any false negatives (missed genuine duplicates) among
the legitimately-numbered headings elsewhere in the repo (Java
Collections, Microservices, Design Patterns, and every other guide's
numbered questions all still correctly collapse to the same text when
renumbered, which is exactly what this check exists to catch).

## Verification performed

- Generated the guide's Table of Contents with `scripts/add_toc.py`,
  nested two levels deep (9 categories, 20 patterns) rather than
  hand-writing anchors.
- Re-ran `scripts/check_internal_links.py` and (after the regex fix)
  `scripts/check_duplicate_headings.py` across all 39 repository markdown
  files — clean.
- Re-ran `scripts/check_code_fences.py` — the guide has zero code fences
  by design (a curated list, not worked solutions), so this check is
  vacuously clean for this file specifically.
- Re-ran `markdownlint-cli2` across all repository files — 0 issues.
- Ran `lychee` against the new guide directly: 136 link occurrences, 101
  excluded (the 100 `leetcode.com` problem links plus the `leetcode.com`
  homepage link in the sources table), 35 checked and OK, 0 errors.
- Counted the numbered problem entries directly (`grep -c`) to confirm
  the list actually contains exactly 100 problems, not an approximate
  count from memory.

## Integration

- This file is intentionally **not** added to `AUDIT.md`'s guide-status
  table, for the same reason the System Design Interview Question Bank
  isn't — it's a curated practice-prompt list, not a worked Q&A guide,
  so "Fact-audited"/"Code-tested" in the table's usual sense don't apply
  cleanly to it. It's noted separately alongside the other excluded files.
- Repository-wide counts in `AUDIT.md` updated (37 → 39 files, question
  banks 1 → 2, external-link count and exclusion note updated to reflect
  the `leetcode.com` exclusion).
- No top-level `README.md` changes were made in this pass — that
  integration (adding the new folder/guide to "Guides by topic," "Who
  this is for," and the difficulty table) is a natural next step but was
  not explicitly requested and is tracked as follow-up work rather than
  assumed.

## Not done in this pass

- No individual `leetcode.com` link was confirmed to resolve to its
  intended problem — see the citation-limitation section above.
- The top-level `README.md` was not updated to reference the new folder
  or guide.
- No per-problem hints, approach notes, or code were added, per the
  user's explicit scope choice — this is deliberately a checklist, not a
  solutions manual.
