# Design Patterns — New Guide Creation — 2026-08-24

Scope: creation of `Design Patterns/Design_Patterns_Interview_Prep.md`,
replacing the placeholder stub that previously occupied this folder,
covering 15 of the Gang of Four's 23 original patterns at the user's
explicit request. Two scoping decisions were confirmed with the user
before writing: organize by GoF category (Creational → Structural →
Behavioral) rather than the graduated Basic → Intermediate → Staff shape
used elsewhere in the repo, and cover exactly the 15 named patterns with
no added comparison questions.

## Patterns covered

**Creational** (3): Singleton, Factory Method, Builder.
**Structural** (5): Adapter, Decorator, Facade, Proxy, Composite.
**Behavioral** (7): Observer, Strategy, Command, Iterator, State,
Template Method, Chain of Responsibility.

Each question uses the same five-part shape as Java Collections and the
Microservices restructure (Core answer / Staff-level extension / Example
/ Follow-up questions / Sources), with the Staff-level extension in every
question specifically covering the pattern's real-world JDK/Spring
instance (where one exists) and when reaching for the pattern is overkill
for a simpler design — directly matching the planned scope already
written into the folder's placeholder stub before this guide existed.

## Code-block audit

All 15 `java`-tagged code blocks were extracted and compiled/executed
with JDK 21 (`javac`/`java`), not just visually reviewed. All 15 compiled
without error and produced output; every observed output was checked
line-by-line against the block's own inline comments — all matched
exactly. No bugs were found. Status: **Code-tested: Yes**.

Each example is a single self-contained `public class ...Demo` file with
a `main` method, deliberately structured so the same file that appears in
the guide is the exact file that was compiled — not a hand-copied or
lightly-adapted version — to eliminate transcription risk between what's
published and what was actually verified.

## Citations

Two source types are used consistently across all 15 patterns:

- The canonical Gang-of-Four book (Gamma, Helm, Johnson, Vlissides —
  *Design Patterns: Elements of Reusable Object-Oriented Software*, 1994)
  as the primary definitional source, linked via its Wikipedia page
  (confirmed 200) since the O'Reilly library page for the book returns
  403 to automated requests and has no other stable, freely-accessible
  canonical URL.
- refactoring.guru's per-pattern page (all 15 confirmed 200 before
  citing) as a secondary, widely-used practical reference with diagrams
  and multi-language examples.

Four patterns additionally cite the specific JDK class that is their
real-world instance, each confirmed live: `Iterator`, `Comparator`,
`InputStream` (for `java.io`'s decorator hierarchy), and
`java.lang.reflect.Proxy`.

## Structural validation

- Generated the guide's Table of Contents with `scripts/add_toc.py`
  rather than hand-writing anchors for 15 headings nested under three
  category sections.
- `scripts/check_internal_links.py`, `scripts/check_duplicate_headings.py`,
  `scripts/check_code_fences.py` — all clean across all 36 repository
  markdown files including the new guide.
- `markdownlint-cli2` — 0 issues across all 36 files.
- `lychee` — 73 links checked against the new guide specifically, 0
  errors; a full repository run (2,789 links) also came back with 0
  errors.
- Measured all 15 Core answers' word counts against the 100–180 word
  target — all in range (147–172 words).
- Counted follow-up-question bullets: exactly 30 (2 per pattern × 15).

## Integration

- Removed `Design Patterns/README.md` (the placeholder stub), consistent
  with the repo's convention that a populated topic folder doesn't carry
  its own README.
- Added a new "Design Patterns" section to the top-level `README.md`'s
  "Guides by topic" list (placed after Java JVM & GC, before Frameworks,
  since it's core-Java-OOP content rather than framework-specific),
  removed it from the "Reserved — not yet written" section, added a row
  to the "Difficulty by guide" table, and updated the Staff Engineer row
  in "Who this is for" to list it under covered topics instead of a gap.
- Updated the repository-wide guide/question counts (20 → 21 guides,
  606 → 621 questions, badge and prose both updated) and `AUDIT.md`'s
  guide status table, repository-wide counts, and open-findings
  denominators.

## Not done in this pass

- Only 15 of the Gang of Four's 23 original patterns are covered, by the
  user's explicit scope decision — Abstract Factory, Prototype, Bridge,
  Flyweight, Interpreter, Mediator, Memento, Visitor, and Null Object are
  not included and are not tracked as a gap against this guide's own
  stated scope, since the guide never claims full GoF coverage.
- No comparison/"often confused" questions (Strategy vs. State, Decorator
  vs. Proxy vs. Adapter) were added as separate questions, per the user's
  explicit choice — each pattern's own Staff-level extension or follow-up
  questions address the most relevant comparison inline instead (e.g.,
  Strategy's and State's entries each name the other and state the
  distinction directly).
