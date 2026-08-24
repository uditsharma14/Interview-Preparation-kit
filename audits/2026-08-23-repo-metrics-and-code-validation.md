# Repository Metrics Correction and Code Validation — 2026-08-23

Scope: repository-wide count reconciliation (markdown files, guides,
questions, link-check statistics), plus a full code-block classification
and validation pass on Computer Science Fundamentals and Testing.

## Corrected repo-wide counts

Every count below was re-measured directly against the repository as it
existed on 2026-08-23 — file counts via `find`, question counts via heading
regex (cross-checked for gaps/duplicates), and live runs of every
repository check (internal links, duplicate headings, markdown lint,
`lychee`, and the newly added `scripts/check_code_fences.py`).

| Metric | Value before this pass | Corrected, measured value |
|---|---|---|
| Markdown files in the repository | 21 files (per the repo-wide checks table), inconsistent with "17 guides" used elsewhere | 26 markdown files total (17 Q&A guides + 1 glossary + 3 reserved-placeholder READMEs + 1 Further Reading list + 1 System Design Question Bank + README.md/AUDIT.md/CONTRIBUTING.md) |
| Q&A guides | 15 guides in one place, 17 in another — internally inconsistent | 17 — confirmed by counting distinct guide files with numbered question headings |
| Total numbered questions | 559, arrived at by summing per-guide deltas across several same-day edits | 544 — counted directly from every guide's numbered headings, cross-checked per guide for gaps or duplicates (none found) |
| Guides with a TOC | 12 of 15 | 14 of 17 (Kafka, Redis, and Transactions still missing at the time; added later the same day) |
| Internal link check | 21 files, 0 broken | 26 files, 0 broken |
| Duplicate-heading check | 21 files, 0 found | 26 files, 0 found |
| Markdown lint | 21 files, 0 issues | 26 files, 0 issues |
| External link check | 1,476 links checked, 1,476 OK, 0 errors, 19 correctly excluded | 2,245 total link occurrences, 1,245 unique URLs, 2,221 OK, 0 errors, 24 excluded, 117 redirects (`lychee` 0.24.2) |
| Version-baseline header present | "Added to all 15 guides" | All 17 Q&A guides have one |
| Code fence check | not previously tracked | New check added: 0 fenced code blocks anywhere in the repository are missing a language tag; 4 blocks outside the two guides audited this pass (AI Engineering, Cross-Stack Design Scenarios, Transactions) are tagged `text` but read as executable-looking code, flagged for future classification |

## Code block audit: Computer Science Fundamentals and Testing

Every fenced code block in Computer Science Fundamentals (29 blocks) and
Testing (48 blocks — 77 total) was classified into one of five kinds
(self-contained runnable/compilable example, partial illustrative snippet,
pseudocode, configuration, shell command), and every block that could
plausibly be a compilable or runnable example was actually run.

| Classification | CS Fundamentals | Testing |
|---|---|---|
| Compilable example (verified) | 3 (`Factorial`, `ShapeDemo`, a Python typing demo) | 0 |
| Partial illustrative snippet | 2 (Big-O fragments; a deliberate compile-error demo) | 40 |
| Pseudocode (diagrams/tables, no real syntax) | 20 | 15 |
| Configuration | 0 | 2 (a Gherkin `.feature` file, a CI YAML sketch) |
| Shell command | 1 (`git` walkthrough) | 3 (`gradlew` loop; a `bash` block split out of an ambiguous fence) |
| SQL (partial — assumes an existing `users` table, syntax verified with `sqlite3`) | 1 | — |
| Groovy (Gatling DSL, partial illustrative) | — | 1 |

### Bugs found and fixed

- **Testing Q32** — `new MockProducer<>(true, new StringSerializer(), new OrderEventSerializer())` called a constructor that doesn't exist; Kafka's actual 4-argument constructor requires a `Partitioner` argument. Fixed to `new MockProducer<>(true, null, new StringSerializer(), new OrderEventSerializer())`, confirmed against the Kafka 4.0 `MockProducer` Javadoc.
- **Testing Q34** — two top-level classes both named `SessionValidator` declared in the same fence. Renamed the "before" version to `SessionValidatorBeforeFix` and clarified in the comment that the second is the same class, refactored.
- **Testing Q38** — a `text`-tagged block mixed an ASCII diagram with two real, executable `./gradlew` lines. Split into a `text` block (the diagram) and a `bash` block (the commands).

APIs spot-verified against primary sources: jqwik's `@BigRange` annotation (confirmed it applies to both `BigInteger` and `BigDecimal`, with string-valued `min`/`max`), Spring's `DynamicPropertyRegistry.add()` signature, and Selenium 4.x's `WebDriverWait(driver, Duration)` constructor — all matched the guides' existing usage with no changes needed.

No domain classes were invented to make a snippet "look complete" — the large majority of Testing's Java blocks (40 of 48) assume representative types like `Order`, `PaymentGateway`, or `Calculator` that aren't defined in the snippet, and are correctly classified as partial illustrative snippets rather than forced into a fake compilable shape. Both guides' intro paragraphs state this convention explicitly.

## Status tier definitions used from this point forward

1. **Added** — content exists; no independent verification pass has been run against it yet.
2. **Structurally reviewed** — TOC, heading structure, internal links, and duplicate-heading checks pass, but claims/citations have not been independently checked against primary sources.
3. **Fact-checked** — an independent pass verified claims and citations against primary sources for all or substantially all questions in the guide. Code examples were not executed as part of this.
4. **Code-validated** — every code block was classified, and every block presented as compilable/runnable was actually compiled or run, with bugs found fixed. Independent of whether prose claims elsewhere were fact-checked.
5. **Fully verified** — both Fact-checked and Code-validated, for every question in the guide, with current evidence — not partial coverage.

Two guides qualified for tier 5 at the end of this pass: Computer Science
Fundamentals and Testing. See `AUDIT.md` for the current, up-to-date
per-guide table.
