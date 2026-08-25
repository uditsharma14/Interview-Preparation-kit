# Microservices & Architecture Patterns — Restructure to the Java Collections Shape — 2026-08-24

Scope: restructured `Microservices & Architecture Patterns/Microservices_Architecture_Patterns_Interview_Prep.md`
from its original flat, single-level "Lead/Staff" shape into the graduated
Basic → Intermediate → Staff, five-part shape used by Java Collections and
REST API Design, at the user's request to make it "similar to the Java
interview questions."

## What changed

- **Shape**: the original four-part **Answer** / **Code** / **Follow-up**
  (one paragraph) / **Source** structure became the five-part **Core
  answer** (100–180 words) / **Staff-level extension** / **Example** /
  **Follow-up questions** (two bulleted Q&A pairs) / **Sources** structure.
  Each original dense Answer was split — the essential explanation stayed
  in the Core answer, the deeper trade-off/nuance content moved into the
  Staff-level extension, and each single discursive Follow-up paragraph
  was split into two distinct, bulleted follow-up Q&As. No technical
  content was dropped in this split; it was reorganized.
- **Grading**: all 25 questions were re-leveled into Basic (6 questions —
  monolith-vs-microservices, database-per-service, sync-vs-async
  communication, API Gateway, service discovery, CAP theorem),
  Intermediate (9 questions — DDD decomposition, bounded contexts,
  anti-corruption layer, strangler fig, BFF, sidecar/service mesh basics,
  ambassador/adapter, resilience trio, monorepo/polyrepo), and Staff (10
  questions — API composition vs. CQRS, service mesh trade-offs, CQRS,
  event sourcing, CQRS/ES relationship, read models,
  layered/hexagonal/clean architecture, orchestration vs. choreography,
  consumer-driven contracts, distributed monolith). The header's `Target
  level` changed from `Lead/Staff` to `Basic → Staff (graduated)`, and the
  guide's own prerequisites line was reworded to say the
  Transactions/REST API Design/Redis/Kafka prerequisites apply from the
  Intermediate section onward, not to the guide as a whole.
- **Numbering**: questions were renumbered 1–25 to match their new
  Basic/Intermediate/Staff grouping (the mapping from old to new number is
  not 1:1 with the original order — see the git history for the prior
  version if the old numbering is needed for any reason).
- **Cross-references**: every in-guide reference to another question by
  number ("question 7," "question 2/6") was rewritten as a short
  descriptive phrase ("covered in the Distributed Monolith question," "the
  decomposition-by-capability question") instead — this matches the
  convention already used in Java Collections and the newer frontend
  guides, and makes the guide's internal references immune to any future
  renumbering, rather than needing to be manually tracked and updated
  again.

## Bug found and fixed: one broken cross-file anchor link

The Testing guide linked directly into this guide's old Q23 anchor
(`#23-what-is-consumer-driven-contract-testing...`) for its
consumer-driven-contract-testing cross-reference. Since that question is
now Q24 after re-leveling, the anchor no longer resolved.
`scripts/check_internal_links.py` caught this immediately after the
restructure. Fixed by updating the link in
`Testing/Software_Testing_Interview_Prep.md` to the new anchor. A
repo-wide search confirmed this was the only anchor-specific cross-file
reference into this guide — the other three files that reference it
(`README.md`, the Computer Science Glossary, and two other places in the
Testing guide) all link to the file itself, not a specific anchor, so
they were unaffected by the renumbering.

## Verification performed

- Regenerated the guide's Table of Contents with `scripts/add_toc.py`
  rather than hand-writing anchors for 25 renumbered/regrouped headings.
- Re-ran `scripts/check_internal_links.py` across all 35 (now 36)
  repository markdown files — confirms the fixed Testing-guide link and
  no other regressions.
- Re-ran `scripts/check_duplicate_headings.py` and
  `scripts/check_code_fences.py` against the restructured guide — clean;
  no new ambiguous or under-tagged code fences introduced by the
  reformatting.
- Re-ran `markdownlint-cli2` across all repository files — 0 issues.
- Re-ran `lychee` against the restructured guide (116 links, 0 errors) —
  confirms none of the original citations were broken by the reformatting
  (the underlying URLs were carried over unchanged from the original
  guide, not re-verified as newly-fetched in this pass).
- Measured every one of the 25 new Core answers' word counts — all fall
  within the guide's own 100–180 word target (144–180 words), matching
  the same standard applied to Java Collections and the frontend guides.
- Counted follow-up-question bullets: exactly 50 (2 per question × 25),
  confirming the reformatting was applied uniformly across every question.

## Not done in this pass

- This was a **structural reformatting pass, not a new fact-check** — the
  technical claims and citation URLs are the same ones from the original
  guide's most recent fact-audit (`audits/2026-08-22-initial-accuracy-audit.md`),
  carried over into the new shape rather than independently re-verified
  against primary sources in this pass. `AUDIT.md`'s "Fact-audited: Yes"
  for this guide still reflects that original pass, not a new one.
- Code-block classification/execution was not attempted — this guide's
  examples are almost entirely `text`-tagged architecture diagrams (by
  design, not runnable), consistent with its "Code-tested: No" status
  before and after this restructure.
