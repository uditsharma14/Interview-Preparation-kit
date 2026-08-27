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
| Computer Science Glossary | Partial (17/222 terms individually source-verified; the 22-term Machine Learning Fundamentals section added 2026-08-27 is standard, uncontested ML terminology, cross-checked against the same primary sources as the LLM Fundamentals guide where they overlap, but not independently re-verified term-by-term) | N/A | Yes | 2026-08-27 |
| Java Collections | Yes | Yes | Yes | 2026-08-23 |
| Java Concurrency | Yes | Yes | Yes | 2026-08-25 |
| Java JVM & GC | Yes | Yes | Yes | 2026-08-25 |
| Spring Boot Internals | Yes | Yes | Yes | 2026-08-25 |
| Spring Security & OAuth2 | Yes | Yes | Yes | 2026-08-25 |
| JPA & Hibernate | Yes | Yes | Yes | 2026-08-25 |
| Testing | Yes | Yes | Yes | 2026-08-23 |
| REST API Design | Yes | Yes | Yes | 2026-08-25 |
| Cross-Stack Design Scenarios | Yes | Yes | Yes | 2026-08-25 |
| Microservices & Architecture Patterns | Yes | Yes | Yes | 2026-08-25 |
| Kubernetes, Docker & Cloud | Yes | Yes | Yes | 2026-08-25 |
| AI Engineering | Yes (content changes fast — re-verify figures before relying on them) | Yes | Yes | 2026-08-27 |
| LLM Fundamentals | Yes | N/A | Yes | 2026-08-27 |
| Vector Databases & RAG | Yes | N/A | Yes | 2026-08-27 |
| LLM System Design | Yes | Partial (one Python block, syntax-checked only, not executed — see its scope note) | Yes | 2026-08-27 |
| Tech Leadership | Yes (behavioral content — checked for fabricated experience, not spec citations) | N/A | Yes | 2026-08-22 |
| Kafka | Yes | N/A | Yes | 2026-08-25 |
| Redis & Caching | Yes | Yes | Yes | 2026-08-25 |
| Transactions | Partial (spot-checked on major topics, not every question individually) | Yes | Yes | 2026-08-25 |
| JavaScript | Yes | Yes | Yes | 2026-08-24 |
| Angular | Yes | No | Yes | 2026-08-24 |
| React | Yes | No | Yes | 2026-08-24 |
| Design Patterns | Yes | Yes | Yes | 2026-08-24 |

`Forward-Deployed & Customer-Facing Engineering/README.md` is a
placeholder stub with no content. `Further Reading/System_Design_and_AI_Reading_List.md`
is an external link list, exempt from this policy by its own header.
`System Design/System_Design_Interview_Question_Bank.md`,
`Data Structures & Algorithms/DSA_Pattern_Based_Question_Bank.md`, and
`Data Structures & Algorithms/Blind_75_Question_Bank.md` are
practice-prompt/problem lists, not worked answers. None of these five
files are tracked in the table above. Both DSA question banks' combined
~175 individual `leetcode.com` problem links could not be
automated-link-checked at all (the site returns HTTP 403 to every
automated fetch attempt) — see each file's own top-of-file note and the
domain-specific exclusion added to `.lychee.toml`. The Blind 75 list's
provenance could also not be cross-checked against a single authoritative
source (both attempted verification pages also refused automated
fetches) — see that file's own note on this.

## Repository-wide counts (measured 2026-08-27)

- 57 markdown files (24 Q&A guides, 1 glossary, 1 placeholder stub, 1
  Further Reading list, 3 question banks, 22 dated files under `audits/`,
  plus README/AUDIT/CONTRIBUTING/ROADMAP/LICENSE)
- 666 numbered questions across 24 guides, plus a 222-term glossary, a
  100-problem pattern-organized DSA question bank, and a 75-problem
  Blind 75 question bank
- 0 broken internal links, 0 duplicate headings, 0 missing code-fence
  language tags (`scripts/check_internal_links.py`,
  `scripts/check_duplicate_headings.py`, `scripts/check_code_fences.py`)
- 3,221 external link occurrences checked repository-wide, 3,014 OK, 6
  errors, 201 excluded (`lychee`, most recent full run 2026-08-27). All 6
  errors are the same pre-existing citation
  (`microservices.io/patterns/communication-style/idempotent-consumer.html`,
  cited in Kafka, Transactions, and Cross-Stack Design Scenarios) —
  confirmed via a direct `curl` that the site itself is currently
  returning a live `503`, not a stale/dead link; unrelated to this
  session's additions and left as-is pending the site's own recovery.
- 24 of 24 Q&A guides have a table of contents

## Open findings

- `Language/Java_Collections_Interview_Prep.md` Q22 and
  `Language/Java_JVM_GC_Interview_Prep.md` Q24 cover overlapping ground
  (heap-dump/memory-leak diagnosis) — not consolidated, low priority.
- All 4 code fences originally flagged by `scripts/check_code_fences.py`
  as ambiguous (`text`-tagged but executable-looking) have now been
  reviewed as part of their respective guides' 2026-08-25 code audits —
  Transactions' two, Cross-Stack Design Scenarios' one, and AI
  Engineering's one — and confirmed correctly tagged (narrative/
  architecture pseudocode, or a JSON-schema comparison with one small
  embedded, independently syntax-checked Python function), not real bugs.
- Every guide's code blocks are now classified — the code-block
  validation rollout finished 2026-08-25 (see the 13 dated audit files
  in the History section below). Angular and React's blocks have been
  classified (framework-dependent partial illustrative snippets,
  API-checked against primary docs) but still not compiled or executed
  — the one remaining gap, since they need a Node/npm toolchain with
  JSX/TS support, not just a JVM/Python environment; see `ROADMAP.md`.
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
- Every guide's code has now been classified and, where compilable,
  mechanically tested except Angular and React — see each guide's own
  dated audit file under `audits/` for the exact scope and rigor of what
  was checked (several guides without a live dependency available, e.g.
  Redis & Caching without a live Redis instance and Kubernetes/Docker
  without a live cluster, used compile-checks and schema/lint validators
  instead of full execution — documented per guide, not a gap unique to
  this list). Angular and React's code blocks are TypeScript/JSX examples
  that assume a full framework build (Angular CLI, or a bundler with a
  JSX transform) — they were checked for correct API usage against
  angular.dev/react.dev, not compiled or executed; see `ROADMAP.md`.

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
- `audits/2026-08-25-blind-75-creation.md` — added a second, separate
  DSA question bank containing the well-known "Blind 75" selection (75
  problems, organized by data-structure category rather than pattern);
  provenance could not be cross-checked against a live authoritative
  source, documented honestly in the file itself rather than presented
  as a guaranteed-exact reproduction.

- `audits/2026-08-25-jpa-hibernate-code-audit.md` — fifth guide in the
  code-block validation rollout; classified all 50 code blocks, verified
  six load-bearing Hibernate mechanisms (persistence-context identity and
  dirty checking, auto-flush before a JPQL query, the N+1 query problem,
  owning-vs-inverse-side FK persistence, `persist()`/`merge()` reference
  semantics, and optimistic-locking conflict detection) against a real
  Hibernate 6.4 + H2 persistence unit; found and fixed a real compile
  error (two stacked, non-repeatable `@ManyToOne` annotations on the same
  field in Q22).

- `audits/2026-08-25-kafka-code-audit.md` — sixth guide in the code-block
  validation rollout; the guide contains zero fenced code blocks (pure
  prose/tables), so its code-tested status is N/A rather than a gap.

- `audits/2026-08-25-redis-caching-code-audit.md` — seventh guide in the
  code-block validation rollout; no live Redis available, so verification
  used compile-checks against the real Spring Data Redis API (12
  snippets) plus an executed unit test for the guide's one dependency-free
  class (`TokenBucket`, Q21); found and fixed a real compile error (Q16's
  `WAIT`-command lambda returning `Object` where `RedisCallback<Long>`
  requires `Long`).

- `audits/2026-08-25-transactions-code-audit.md` — eighth guide in the
  code-block validation rollout; classified all 37 code blocks; verified
  five transaction-propagation/rollback claims (`REQUIRED` join-and-share-
  rollback, `REQUIRES_NEW` independence, `NESTED` savepoint-scoped
  partial rollback, and the checked-vs-unchecked default rollback rule)
  against a real Spring `DataSourceTransactionManager` + H2; no bugs
  found; resolved the two previously-flagged ambiguous code fences in
  this guide as correctly-tagged diagrams, not real code.

- `audits/2026-08-25-rest-api-design-code-audit.md` — ninth guide in the
  code-block validation rollout; classified all 40 code blocks; compiled
  6 of 9 java blocks against real Spring Web/Retry/Resilience4j APIs;
  found and fixed two real bugs (Q5's stale-`Optional.get()` in a
  concurrent-retry catch block, and Q25's undeclared `response` symbol).

- `audits/2026-08-25-cross-stack-design-scenarios-code-audit.md` — tenth
  guide in the code-block validation rollout; classified all 20 code
  blocks; verified the one genuinely new API claim (Q9's
  `KafkaListenerEndpointRegistry` pause/resume) against the real
  `spring-kafka` API; no bugs found; resolved its one previously-flagged
  ambiguous code fence as correctly-tagged narrative pseudocode.

- `audits/2026-08-25-microservices-architecture-patterns-code-audit.md`
  — eleventh guide in the code-block validation rollout; classified all
  26 code blocks (25 diagrams, 1 compilable); the guide's single Java
  block (an anti-corruption-layer `switch` expression) compiled cleanly;
  no bugs found.

- `audits/2026-08-25-kubernetes-docker-cloud-code-audit.md` — twelfth
  guide in the code-block validation rollout, and the first with no
  Java/application code; classified all 52 blocks; schema-validated 9
  Kubernetes manifests with `kubeconform` and linted all 7 Dockerfiles
  with `hadolint` (both installed for this pass); no bugs found.

- `audits/2026-08-25-ai-engineering-code-audit.md` — thirteenth guide in
  the code-block validation rollout, and the first with Python code;
  classified all 30 blocks; verified 6 code paths against real,
  installed third-party libraries (the `anthropic` SDK's actual type
  definitions, real Pydantic validation, and real `pybreaker`/`tenacity`
  circuit-breaker/retry behavior); no bugs found; resolved the guide's
  one previously-flagged ambiguous code fence.

- `audits/2026-08-27-ai-llm-content-expansion.md` — added three new
  guides (LLM Fundamentals, Vector Databases & RAG, LLM System Design),
  11 new questions appended to AI Engineering (Q28-38, covering
  LangGraph/agent memory/tool-failure handling, offline/online
  evaluation, faithfulness/relevance metrics, guardrails, canary
  rollout, degradation detection, provider fallback, and a project-
  deep-dive structuring question), and a 22-term Machine Learning
  Fundamentals section in the Computer Science Glossary, in response to
  a user-provided AI/LLM interview-question checklist; every
  architectural/mathematical claim in the new LLM Fundamentals guide was
  checked against its primary paper before writing; found and fixed two
  real bugs introduced during writing (Python code mistagged as `text`,
  one with an actual syntax error caught by `ast.parse`).

See `CONTRIBUTING.md` for the accuracy and citation policy new material
is expected to meet, and `ROADMAP.md` for planned work.
