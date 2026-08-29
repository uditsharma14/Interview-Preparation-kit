# OOP Concepts — New Guide Creation — 2026-08-27

Scope: the user asked for an OOP concepts guide alongside a request for
Java coding interview questions. This guide, `Language/
OOP_Concepts_Interview_Prep.md`, was written and verified at the time;
its README.md and AUDIT.md integration was not — this file documents
the original creation work, and the integration gap it left behind was
closed out 2026-08-29 alongside the Next.js guide's own integration
(see `audits/2026-08-29-nextjs-guide-creation.md` and the corresponding
AUDIT.md/README.md diffs).

## What was created

- **`Language/OOP_Concepts_Interview_Prep.md`** (new, 17 questions,
  graduated Basic → Staff) — encapsulation, inheritance, polymorphism,
  and abstraction (Basic); interfaces vs. abstract classes, composition
  over inheritance, method overloading vs. overriding, `this`/`super`,
  and immutability (Intermediate); the Liskov Substitution Principle,
  the diamond problem and how default methods resolve it, favoring
  interfaces for API design, and object-oriented anti-patterns at Staff
  scale (Staff). Deliberately scoped to avoid overlap with `Design
  Patterns` (the GoF catalog built on top of these concepts) and `Java
  Collections` (which owns the `equals()`/`hashCode()` contract in
  depth) — both are cross-referenced rather than duplicated.

## Verification performed

- All 16 Java code blocks extracted into isolated temp directories,
  wrapped in a `main()` harness where the source was a bare snippet,
  and compiled/run with real `javac`/`java` — not just read for
  plausibility.
- This caught one real bug: the interface-vs-abstract-class example's
  `Employee.totalPay()` was package-private, which cannot satisfy
  `Payable.totalPay()`'s implicitly-`public` contract — a genuine
  `javac` error ("attempting to assign weaker access privileges").
  Fixed by adding `public` plus a clarifying comment; recompiled and
  reran to confirm `Manager.totalPay() == 1200.0` and
  `Contractor.totalPay() == 1000.0`.
- One quoted compiler error in the diamond-problem example was missing
  a word ("...inherits unrelated defaults... from Flyer and Swimmer"
  should read "...from types Flyer and Swimmer") — corrected after
  confirming the exact real `javac` wording against a live compile.
- `scripts/add_toc.py` run on the new file; `scripts/
  check_internal_links.py`, `scripts/check_duplicate_headings.py`, and
  `scripts/check_code_fences.py` run repository-wide — clean.
- `markdownlint-cli2` run against the new file — 0 issues.

## Not done in this pass (closed out later)

- README.md's "Guides by topic" (Language section) and "Difficulty by
  guide" table did not get an OOP Concepts entry at creation time.
- AUDIT.md's guide-status table did not get an OOP Concepts row, and
  the repository-wide counts were not updated to include it.
- `lychee` was not run against this file's citations individually at
  creation time.

All three gaps were closed 2026-08-29: see the OOP Concepts row added
to AUDIT.md's guide-status table and repository-wide counts, the
Language-section bullet and Difficulty-table row added to README.md,
and a combined `lychee` run against this file (alongside the new
Next.js guide) confirming all 96 external links across both files
resolve cleanly with 0 errors.
