# Audit Status

Current verification status for every guide in InterviewSmith. Detailed
findings live in dated files under `audits/`; forward-looking work lives
in `ROADMAP.md`. This file is a summary, not a log — it should stay short
enough to read in one sitting.

## What the columns mean

- **Fact-audited** — technical claims and citations checked against
  primary sources (Oracle/OpenJDK, Spring, Kafka, Redis, Kubernetes,
  RFCs, and similar). `Yes` means all or substantially all questions;
  `Partial` means a bounded subset — see the guide's linked audit file
  for the exact scope.
- **Code-tested** — every fenced code block classified (compilable
  example, partial illustrative snippet, pseudocode, configuration, shell
  command), and every block classified as compilable actually compiled
  and executed. `N/A` where a guide has no real code to test.
- **Structure-validated** — table of contents present, internal links
  resolve, no duplicate headings. Mechanical, script-verified
  (`scripts/check_internal_links.py`, `scripts/check_duplicate_headings.py`).

A guide is never marked fully audited across all three columns unless
every question, citation, and executable example in it was actually
checked — a `Partial` or `No` in any column is not a defect, it states
what hasn't been done yet.

## Guide status

| Guide | Fact-audited | Code-tested | Structure-validated | Last reviewed |
|---|---|---|---|---|
| Computer Science Fundamentals | Yes | Yes | Yes | 2026-08-23 |
| Computer Science Glossary | Partial (17/200 terms) | N/A | Yes | 2026-08-23 |
| Java Collections | Yes | Yes | Yes | 2026-08-23 |
| Java Concurrency | Yes | Yes | Yes | 2026-08-25 |
| Java JVM & GC | Yes | Yes | Yes | 2026-08-25 |
| Spring Boot Internals | Yes | No | Yes | 2026-08-23 |
| Spring Security & OAuth2 | Yes | No | Yes | 2026-08-23 |
| JPA & Hibernate | Yes | No | Yes | 2026-08-23 |
| Testing | Yes | Yes | Yes | 2026-08-23 |
| REST API Design | Yes | No | Yes | 2026-08-22 |
| Cross-Stack Design Scenarios | Yes | No | Yes | 2026-08-22 |
| Microservices & Architecture Patterns | Yes | No | Yes | 2026-08-24 |
| Kubernetes, Docker & Cloud | Yes | No | Yes | 2026-08-22 |
| AI Engineering | Yes (content changes fast — re-verify figures before relying on them) | No | Yes | 2026-08-22 |
| Tech Leadership | Yes (behavioral content — checked for fabricated experience, not spec citations) | N/A | Yes | 2026-08-22 |
| Kafka | Yes | No | Yes | 2026-08-23 |
| Redis & Caching | Yes | No | Yes | 2026-08-23 |
| Transactions | Partial (spot-checked on major topics, not every question individually) | No | Yes | 2026-08-23 |
| JavaScript | Yes | Yes | Yes | 2026-08-24 |
| Angular | Yes | No | Yes | 2026-08-24 |
| React | Yes | No | Yes | 2026-08-24 |
| Design Patterns | Yes | Yes | Yes | 2026-08-24 |

`Forward-Deployed & Customer-Facing Engineering/README.md` is a
placeholder stub with no content. `Further Reading/System_Design_and_AI_Reading_List.md`
is an external link list, exempt from this policy by its own header.
`System Design/System_Design_Interview_Question_Bank.md` and
`Data Structures & Algorithms/DSA_Pattern_Based_Question_Bank.md` are
practice-prompt/problem lists, not worked answers. None of these four
files are tracked in the table above. The DSA question bank's ~100
individual `leetcode.com` problem links could not be automated-link-checked
at all (the site returns HTTP 403 to every automated fetch attempt) — see
that file's own top-of-file note and the domain-specific exclusion added
to `.lychee.toml`.

## Repository-wide counts (measured 2026-08-25)

- 39 markdown files (21 Q&A guides, 1 glossary, 1 placeholder stub, 1
  Further Reading list, 2 question banks, 7 dated files under `audits/`,
  plus README/AUDIT/CONTRIBUTING/ROADMAP/LICENSE)
- 621 numbered questions across 21 guides, plus a 200-term glossary and a
  100-problem, pattern-organized DSA question bank
- 0 broken internal links, 0 duplicate headings, 0 missing code-fence
  language tags (`scripts/check_internal_links.py`,
  `scripts/check_duplicate_headings.py`, `scripts/check_code_fences.py`)
- 2,789 external link occurrences checked (Q&A guides only; the DSA
  question bank's ~100 `leetcode.com` links are excluded from `lychee`
  entirely, see above), 2,765 OK, 0 errors, 24 excluded
  (`lychee`, most recent full run 2026-08-24)
- 21 of 21 Q&A guides have a table of contents

## Open findings

- `Language/Java_Collections_Interview_Prep.md` Q22 and
  `Language/Java_JVM_GC_Interview_Prep.md` Q24 cover overlapping ground
  (heap-dump/memory-leak diagnosis) — not consolidated, low priority.
- 4 code fences outside the audited guides (AI Engineering, Cross-Stack
  Design Scenarios, Transactions) are tagged `text` but read as
  executable-looking code — flagged by `scripts/check_code_fences.py`,
  not yet classified.
- 14 of 21 guides have never had their code blocks classified or executed
  (see `ROADMAP.md`). Angular and React's blocks have been classified
  (framework-dependent partial illustrative snippets, API-checked against
  primary docs) but not compiled or executed.
- 13 of 21 guides have not been measured or restructured for answer
  length since the original repository-wide measurement.

## Known limitations

- Citation liveness reflects the date of the most recent `lychee` run, not
  continuous monitoring — a monthly scheduled run catches drift between
  edits.
- "Fact-audited: Yes" reflects independent verification that occurred at
  some point, not necessarily on the date in the "Last reviewed" column —
  see the linked audit file under `audits/` for exactly what was checked
  and when.
- AI Engineering's content is explicitly the fastest-moving in the
  repository; a "Yes" there is weaker evidence of current accuracy than
  the same mark on a spec-driven guide.
- No guide's code has been mechanically tested beyond Computer Science
  Fundamentals, Testing, Java Collections, JavaScript, and Design
  Patterns. Angular and React's code blocks are TypeScript/JSX examples
  that assume a full framework build (Angular CLI, or a bundler with a
  JSX transform) — they were checked for correct API usage against
  angular.dev/react.dev, not compiled or executed.

## History

Detailed findings, one file per audit pass:

- `audits/2026-08-22-initial-accuracy-audit.md` — the original
  repository-wide accuracy pass, per-guide finding tables, and the
  repo-wide checks as they stood at the time.
- `audits/2026-08-23-repo-metrics-and-code-validation.md` — repository
  count corrections, and the Computer Science Fundamentals / Testing
  code-block audit.
- `audits/2026-08-23-java-collections-code-audit.md` — a targeted
  Javadoc correction pass and a full code-block audit for Java
  Collections specifically.
- `audits/2026-08-24-frontend-guides-creation.md` — creation and
  verification of three new guides (JavaScript, Angular, React):
  version-baseline research, a full JavaScript code-block execution
  audit, two broken external links found and fixed, a bug found and
  fixed in `scripts/add_toc.py`, and README/AUDIT integration.
- `audits/2026-08-24-frontend-guides-review-fixes.md` — an independent
  review of the three frontend guides surfaced a wrong version-sensitive
  claim (Angular's release cadence), a broken/garbled citation (JS
  debounce/throttle), a stale citation URL, and two coverage gaps
  (Angular Router/guards, React Error Boundaries) — all fixed, plus two
  smaller consistency fixes (a `WeakMap` mention, a mixed import-style
  example).
- `audits/2026-08-24-microservices-restructure.md` — restructured
  Microservices & Architecture Patterns from a flat, Lead/Staff-only,
  four-part shape into the graduated Basic → Intermediate → Staff,
  five-part shape used by Java Collections; all 25 questions
  re-leveled, reformatted, and re-numbered, with one broken cross-file
  anchor link (from the Testing guide) found and fixed as a result.
- `audits/2026-08-24-design-patterns-creation.md` — creation of a new
  guide covering 15 Gang-of-Four patterns, organized by category
  (Creational → Structural → Behavioral) rather than graduated
  difficulty; every one of the guide's 15 Java code examples was
  compiled and executed, with output checked against inline comments,
  and the placeholder stub replaced with real content.
- `audits/2026-08-25-dsa-question-bank-creation.md` — creation of a new
  Data Structures & Algorithms folder and a 100-problem, pattern-based
  question bank (20 patterns, curated list style, no worked solutions,
  matching the System Design Interview Question Bank's format); a bug
  found and fixed in `scripts/check_duplicate_headings.py` (a
  leading-digit heading like "1D Dynamic Programming" was incorrectly
  treated as numbered-list text and collided with "2D Dynamic
  Programming"); `leetcode.com` added to `.lychee.toml`'s exclusion list
  since the site blocks all automated link-checking.

See `CONTRIBUTING.md` for the accuracy and citation policy new material
is expected to meet, and `ROADMAP.md` for planned work.
