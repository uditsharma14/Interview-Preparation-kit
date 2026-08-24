# Roadmap

Open, forward-looking work for InterviewSmith. Completed items are removed
from this file rather than marked done, to keep it a task list rather than
a changelog — see `AUDIT.md` and `audits/` for what has already happened.

## Code-block validation rollout

Computer Science Fundamentals, Testing, and Java Collections have had every
code block classified and every compilable/runnable block compiled and
executed (see `audits/2026-08-23-repo-metrics-and-code-validation.md` and
`audits/2026-08-23-java-collections-code-audit.md`). The remaining 14
guides have not had their code blocks classified or executed.

Recommended approach: one guide per change, in order of Java/SQL code
density — Java Concurrency, Java JVM & GC, Spring Boot Internals, Spring
Security & OAuth2, JPA & Hibernate, then the System Design guides. Each
pass should classify every code block into one of the five categories
(compilable example, partial illustrative snippet, pseudocode,
configuration, shell command), compile and execute every block classified
as compilable, and record findings in a new dated file under `audits/`.

`scripts/check_code_fences.py` currently flags 4 blocks outside the
audited guides that are tagged `text` but read as executable-looking code:
`AI Engineering/AI_Engineering_Interview_Prep.md:668`,
`System Design/Cross_Stack_Design_Scenarios_Interview_Prep.md:522`, and
`System Design/Transactions_Interview_Prep.md:116` and `:153`. These need
classification, not necessarily correction.

## Answer-length restructuring rollout

Four guides have been migrated off the original four-part
Answer/Code/Follow-up/Source shape: Java Collections and REST API Design
(five-part: Core answer/Staff-level extension/Example/Follow-up
questions/Sources), Testing (six-part, adds Failure modes), and Computer
Science Fundamentals (a lighter Basic-level four-part variant:
Answer/Example/"Go deeper"/Source, 80–150-word answers). 13 guides remain
on the original shape and have not been measured for answer length since
the original repository-wide measurement (234-word median).

Open decision: standardize the remaining guides on the five-part shape or
the six-part shape with Failure modes. `README.md`'s "How each question is
structured" section documents both variants currently in use; update it
again once the rollout is further along.

## Full six-part standardized rewrite

A more elaborate structure (Question / Short answer / Deep dive / Example
/ Failure modes / Follow-ups / Sources) was proposed early in the
repository's history as a long-term target, distinct from the five-/
six-part answer-length restructuring above. Not started. This is a large,
separate scope decision — 544 questions across 17 guides — that should be
made deliberately rather than as a side effect of an accuracy pass.

## Sample-project extraction

Extracting Java/SQL examples into standalone, CI-testable sample projects
(a Maven/Gradle module with a real test harness per example) has not been
attempted. This is a substantial project of its own, separate from the
in-guide code-block compilation checks already performed.

## Known content duplication

`Language/Java_Collections_Interview_Prep.md` Q22 ("How Would You Diagnose
a Collection That Continuously Grows in Production?") and
`Language/Java_JVM_GC_Interview_Prep.md` Q24 ("How Would You Investigate a
Memory Leak Using Heap Dumps and Dominator Trees?") both independently walk
the jmap/MAT/path-to-GC-roots workflow. Both versions are independently
accurate; consolidating them (one question cross-referencing the other) is
low priority but still open.

## Repository description

The GitHub repository's "About" sidebar text has not been kept in sync
with `README.md`'s corrected question count (540+, not 559) and does not
reflect that most guides are Staff-scoped rather than uniformly graduated
Basic → Staff. This is a repository setting, not a file in the repository,
and needs to be updated directly through GitHub.
