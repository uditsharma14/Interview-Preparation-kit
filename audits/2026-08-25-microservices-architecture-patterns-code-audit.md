# Microservices & Architecture Patterns — Code-Block Audit — 2026-08-25

Scope: eleventh guide in `ROADMAP.md`'s code-block validation rollout.
This guide is overwhelmingly conceptual/architectural — it was already
restructured for level/format in `audits/2026-08-24-microservices-restructure.md`
— and turned out to contain almost no compilable code at all.

## Classification summary (26 total code blocks)

- **25 `text`-tagged blocks** — architecture diagrams, migration-phase
  progressions (strangler fig), before/after boundary illustrations —
  correctly diagrams/pseudocode, not meant to execute.
- **1 `java`-tagged block** (Q9, the anti-corruption-layer example) —
  a self-contained `switch` expression translating a legacy integer
  status code into a clean domain enum. Extracted and compiled directly
  (with minimal stub types for the legacy client/response/exception
  classes it references) — compiled cleanly on the first attempt, no
  issues found.

## Bugs found

None.

## Not done in this pass

- No further code execution was needed or possible — this guide's single
  code block is a pure, dependency-free `switch` expression already
  verified by direct compilation, and its 25 `text` blocks are diagrams,
  not classifiable/executable code under `CONTRIBUTING.md`'s policy.
