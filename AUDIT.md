# Audit Log

This file tracks the accuracy audit of every guide in this repository, per
the repository's accuracy policy (see `CONTRIBUTING.md`). Each row is one
finding. A guide is not considered "verified" until every Critical/Major
row for that guide has `Status = Fixed` or `Status = Won't fix (documented)`.

Severity legend:

- **Critical** — factually wrong, would mislead a candidate or embarrass
  them in an interview.
- **Major** — imprecise or missing an important qualifier/version boundary.
- **Minor** — technically defensible but sloppy wording, weak example, or
  missing citation.
- **Editorial** — artifacts, filler, formatting, structure, duplication.

## Findings

### Language/Java_Collections_Interview_Prep.md

| Question | Severity | Problem | Correct interpretation | Authoritative source | Status |
|---|---|---|---|---|---|
| Q2 — Mutable HashMap key | Critical | Stated a mutated-key entry becomes "permanently unreachable through the API." | `get()`/`remove()` via a freshly computed hash fail, but the entry is still findable via iteration, and becomes `get()`-reachable again if the key's hash-relevant state is restored. | [`HashMap` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashMap.html) | **Fixed** |
| Q3 — Java 7 `ConcurrentHashMap` segments | Major | Claimed "16 fixed segments" unconditionally. | 16 was only the default `concurrencyLevel` for the no-arg constructor; actual segment count depended on the configured `concurrencyLevel`. | JDK 7 `ConcurrentHashMap` Javadoc | **Fixed** |
| Q3 — synchronization claim | Major | Code comment: "no external synchronization needed, ever." | Individual operations and documented compound methods are atomic; multi-key/cross-resource invariants still need external coordination. | [`ConcurrentHashMap` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html) | **Fixed** |
| End of file | Editorial | Leftover conversational artifact addressed to the repo author. | Remove. | — | **Fixed** |
| Q10 vs JVM_GC heap-dump question | Editorial | Real redundancy: both fully explain the MAT/`jmap`/path-to-GC-roots workflow. | Worth consolidating in a future pass; not done here (small enough overlap, both versions are independently accurate). | — | Open (low priority) |

**Guide status: Verified. 15/15 questions reviewed, TOC added, version-baseline header present.**

### Language/Java_Concurrency_Interview_Prep.md

| Question | Severity | Problem | Correct interpretation | Authoritative source | Status |
|---|---|---|---|---|---|
| Q1 — JMM / happens-before | Critical | Racy code called "actually undefined" / "genuinely undefined behavior." | Without happens-before, visibility/ordering aren't guaranteed, but the JMM (JLS Ch. 17) still constrains execution — not UB in the C/C++ sense. | [JLS §17.4](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html#jls-17.4) | **Fixed** |
| Q20 — Structured concurrency | Critical | Cited JEP 505 but used the removed constructor-based `new StructuredTaskScope.ShutdownOnFailure()` API. | JEP 505 replaced constructors with `StructuredTaskScope.open(Joiner)`. Rewrote example to that API; flagged that JEP 525/533 have continued changing it (JEP 533 changes the thrown exception to `ExecutionException`). | [JEP 505](https://openjdk.org/jeps/505), [JEP 525](https://openjdk.org/jeps/525), [JEP 533](https://openjdk.org/jeps/533), [`Joiner` Javadoc, JDK 25](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/StructuredTaskScope.Joiner.html) | **Fixed** |

**Guide status: Verified. 20/20 questions reviewed, TOC added, version-baseline header present.**

### Language/Java_JVM_GC_Interview_Prep.md

No factual errors found against JVMS §2.5, G1/ZGC/Shenandoah docs, JEP 439, or container-awareness documentation.

**Guide status: Verified — no findings. 18/18 questions reviewed, TOC added, version-baseline header present.**

### Frameworks/Spring_Boot_Internals_Interview_Prep.md

| Question | Severity | Problem | Correct interpretation | Authoritative source | Status |
|---|---|---|---|---|---|
| Q1 — early events | Critical | Showed `@Component` + `@EventListener` handling `ApplicationStartingEvent`/`ApplicationEnvironmentPreparedEvent`, which fire before the `ApplicationContext` exists. | Must register via `SpringApplication.addListeners(...)` or a `spring.factories` `ApplicationListener` entry; `@Component`/`@EventListener` only works from `ContextRefreshedEvent` onward. | [Spring Boot Reference — Application Events and Listeners](https://docs.spring.io/spring-boot/reference/features/spring-application.html) | **Fixed** |
| Q4 — `@Primary` vs `@Qualifier` | Critical | Prose stated Spring checks `@Primary` before `@Qualifier`, contradicting the question's own code example, which showed an injection-point `@Qualifier` overriding `@Primary`. | An explicit `@Qualifier` at the injection point is resolved first (a specific, per-injection-point instruction); `@Primary` is the tie-breaker only when no qualifier is given and multiple type-matching candidates remain. | [`@Primary` Javadoc](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/context/annotation/Primary.html), [Qualifiers reference](https://docs.spring.io/spring-framework/reference/core/beans/annotation-config/autowired-qualifiers.html) | **Fixed** |
| Q12/14 follow-ups — proxy method visibility | Critical | Blanket "advised methods must be public" framing. | Interface-based (JDK) proxies: public-only. Class-based (CGLIB) proxies: as of **Spring Framework 6.0**, protected/package-visible methods can also be made transactional by default. Private/effectively-private methods never advisable. | [Spring Framework Reference — `@Transactional` method visibility](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html), [Proxying Mechanisms](https://docs.spring.io/spring-framework/reference/core/aop/proxying.html) | **Fixed** |
| Q17 follow-up | Major | Claimed `SpringApplicationRunListener` registers via the same `.imports` mechanism as `@AutoConfiguration`. | It uses the older `META-INF/spring.factories` mechanism, distinct from `AutoConfiguration.imports`. | Spring Boot Reference docs | **Fixed** |
| Fenced code block | Editorial | `spring.factories`-style snippet's code fence had no language tag (markdownlint MD040). | Tagged `text`. | — | **Fixed** |

**Guide status: Verified. 25/25 questions reviewed, TOC added, version-baseline header present.**

### Frameworks/Spring_Security_OAuth2_Interview_Prep.md

No Critical/Major findings after a full read, including targeted verification of filter-chain ordering (Q4), CSRF/CORS (Q7–8), OAuth2 authorization-code flow with PKCE against RFC 7636 (Q10), and JWT/JWKS validation and key rotation against RFC 7519/7517 (Q16–17) — the `aud`-validation-not-checked-by-default callout in Q16 in particular is a real, correctly-flagged Spring Security gap, not an error. No duplicates, no conversational artifacts, no broken links.

**Guide status: Verified — no correctness findings. 30/30 questions reviewed, TOC added, version-baseline header present.**

### Frameworks/JPA_Hibernate_Interview_Prep.md

| Question | Severity | Problem | Correct interpretation | Authoritative source | Status |
|---|---|---|---|---|---|
| Q21 follow-up — pessimistic lock timeout | Minor | Cited `javax.persistence.lock.timeout` while the rest of the guide targets Jakarta Persistence 3.1 (`jakarta.persistence.*`). | Corrected to `jakarta.persistence.lock.timeout`. | [Jakarta Persistence Specification 3.1](https://jakarta.ee/specifications/persistence/3.1/jakarta-persistence-spec-3.1.html) | **Fixed** |

Dependency-resolution question (known issue #9) was independently re-checked in this guide's own scope and found already accurate. Entity lifecycle, dirty checking/flush timing, N+1 causes/fixes, LAZY/EAGER defaults per association type, and `GenerationType.IDENTITY` disabling JDBC batching were all verified correct.

**Guide status: Verified. 30/30 questions reviewed, TOC added, version-baseline header present.**

### System Design/REST_API_Design_Interview_Prep.md

| Question | Severity | Problem | Correct interpretation | Authoritative source | Status |
|---|---|---|---|---|---|
| Q10 — ETag | Editorial | Malformed markdown span: `` `ETag** `` (mismatched backtick/bold). | Fixed to `` `ETag` ``. | — | **Fixed** |
| Q4 — idempotent methods | Editorial | Code block omitted `TRACE`, though prose correctly includes it. | Added `TRACE` to the code block. | [RFC 9110 §9.2.2](https://datatracker.ietf.org/doc/html/rfc9110#section-9.2.2) | **Fixed** |
| Q5 vs Cross-Stack Q11 | Minor | ~90% duplicated idempotency-key mechanism and code with Cross-Stack Design Scenarios Q11. | Trimmed Cross-Stack Q11 to cross-reference this question and focus on the client-contract + incident-investigation angle instead of re-explaining the mechanism. | — | **Fixed** |

HTTP semantics (RFC 9110/9111/9457/7396/6902/4918) and CAP theorem framing checked out.

**Guide status: Verified. 28/28 questions reviewed, TOC added, version-baseline header present.**

### System Design/Cross_Stack_Design_Scenarios_Interview_Prep.md

| Question | Severity | Problem | Correct interpretation | Authoritative source | Status |
|---|---|---|---|---|---|
| Q11 vs REST API Q5 | Minor | Duplicate — see REST API Design entry above. | Consolidated. | — | **Fixed** |
| Q7 — circuit-breaker fallback | Major | `@CircuitBreaker(fallbackMethod = "servedegraded")` didn't match the actual method name `serveDegraded` — Resilience4j resolves fallback methods by exact, case-sensitive name via reflection, so this would fail to wire up at runtime rather than degrade gracefully as claimed. | Fixed the string to `"serveDegraded"`. | [Resilience4j docs](https://resilience4j.readme.io/docs/circuitbreaker) | **Fixed** |

Cross-checked against the now-verified Kafka, Redis, and Transactions guides for consistency on partition ordering, eviction/rate-limiting, and isolation-level claims — no contradictions found.

**Guide status: Verified. 20/20 questions reviewed, TOC added, version-baseline header present.**

### Microservices & Architecture Patterns/Microservices_Architecture_Patterns_Interview_Prep.md

CAP theorem (Q20) is correctly scoped to "during a network partition," not oversimplified as a blanket pick-2-of-3, and cites both Brewer's own retrospective and PACELC as a refinement. Service mesh (Q12) and ambassador/adapter (Q13) sections were checked for the "what's genuinely solved vs. often oversold" framing the task asked for and found substantively accurate, with real failure-mode content (retry-policy compounding across mesh + application layers) rather than trivia. No Critical/Major findings.

**Guide status: Verified — no blocking findings. 25/25 questions reviewed, TOC added, version-baseline header present.**

### Kubernetes, Docker & Cloud/Kubernetes_Docker_Interview_Prep.md

| Question | Severity | Problem | Correct interpretation | Authoritative source | Status |
|---|---|---|---|---|---|
| Q17 — ConfigMap vs Secret | Major | Implied `kubectl get`/`describe` both hide Secret values by default. | Only `kubectl describe secret` redacts (byte counts only); `kubectl get secret -o yaml/json` prints the full base64-encoded data — real protection is RBAC, not `describe`'s redaction. | [Kubernetes — Secrets](https://kubernetes.io/docs/concepts/configuration/secret/) | **Fixed** |
| Q20 — dockershim | Editorial | "was removed" with no version. | Deprecated v1.20, removed v1.24. | [Kubernetes — Dockershim Removal FAQ](https://kubernetes.io/blog/2022/02/17/dockershim-faq/) | **Fixed** |
| Q32 — PodSecurityPolicy | Editorial | "now-removed" with no version. | Deprecated v1.21, removed v1.25. | [Kubernetes — Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/) | **Fixed** |

**Guide status: Verified. 35/35 questions reviewed, TOC added, version-baseline header present.**

### AI Engineering/AI_Engineering_Interview_Prep.md

| Question | Severity | Problem | Correct interpretation | Authoritative source | Status |
|---|---|---|---|---|---|
| Q24 — resilience code | Major | Code block mixed Java/Spring annotations (`@CircuitBreaker`, `@Retryable`, `@Backoff`) onto a Python function — doesn't compile in either language. | Rewrote using real Python libraries (`tenacity`, `pybreaker`) with a working call pattern. | [tenacity docs](https://tenacity.readthedocs.io/), [pybreaker](https://github.com/danielfm/pybreaker) | **Fixed** |

This is the fastest-moving guide in the repo (model capabilities/pricing/context windows). The version-baseline header explicitly flags specific numbers as approximate and to be re-verified before an interview, rather than stating them as permanent fact — see the header's own "last verified" caveat.

**Guide status: Verified. 27/27 questions reviewed, TOC added, version-baseline header present (with the fast-moving-content caveat above).**

### Tech Leadership/Engineering_Leadership_Interview_Prep.md

| Question | Severity | Problem | Correct interpretation | Authoritative source | Status |
|---|---|---|---|---|---|
| Q2, Q20 follow-ups | Editorial | First-person "I've seen..." phrasing implying personal production experience (task rules prohibit inventing this). | Reworded to observational framing; added an explicit "personal example to add" placeholder at the Q20 spot per repo policy. | — | **Fixed** |

No fabricated metrics or incidents found beyond the two reworded phrasings above.

**Guide status: Verified. 25/25 questions reviewed, TOC added, version-baseline header present.**

### System Design/Kafka_Interview_Prep.md

| Question | Severity | Problem | Correct interpretation | Authoritative source | Status |
|---|---|---|---|---|---|
| Q9 — idempotent producer scope (known issue #3) | Major | Summarized idempotence scope as "single producer session, single partition," readable as if a producer using idempotence could only safely write to one partition total. | Sequencing/dedup is tracked independently **per partition** within a session (a producer can write to many partitions); idempotence alone gives no atomicity across partitions/topics — that's what transactions add. | [Confluent — Exactly-once Semantics Is Possible](https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/) (quote verified: "For a single partition, Idempotent producer sends remove the possibility of duplicate messages") | **Fixed** |

Full read of all 40 conceptual questions + 15 scenario questions. Ordering guarantees (Q2), rebalancing (Q4–6), delivery semantics (Q7), `acks`/ISR/replication (Q10–11), retention/compaction (Q29–30), and all 15 scenario questions checked against Kafka documentation and cited KIPs (429, 345, 98) — no other Critical/Major findings.

**Guide status: Verified. 55/55 questions reviewed (40 conceptual + 15 scenario), version-baseline header present. TOC not yet added — see Phase 3/4 backlog.**

### System Design/Redis_Caching_Interview_Prep.md

| Question | Severity | Problem | Correct interpretation | Authoritative source | Status |
|---|---|---|---|---|---|
| Q22 — rate-limiter EXPIRE bug (known issue #4) | Critical | Lua rate limiter called `EXPIRE` unconditionally on every allowed request and described this as "harmless." Resetting the TTL on every request means the window's expiry keeps getting pushed forward as long as traffic continues, so it never actually rolls over on schedule — a materially different (much stricter) behavior than the stated fixed-window semantics. | Set `EXPIRE` only when `INCR` returns `1` (the request that creates the window). | [Redis Documentation — INCR command, "Pattern: rate limiter"](https://redis.io/docs/latest/commands/incr/) (this file's fix is exactly the documented "rate limiter 2" pattern) | **Fixed** |

Full read of all 30 questions. Cache-aside/write-through/write-behind (Q2), the update-then-delete-cache race (Q4–5), stampede prevention (Q6), eviction policies (Q11), hot keys (Q12–13), replication/Sentinel/Cluster consistency (Q15–17), distributed locks (Q18–19), and Redis transaction/pipeline semantics (Q23–24) checked against Redis documentation — no other Critical/Major findings.

**Guide status: Verified. 30/30 questions reviewed, version-baseline header present. TOC not yet added — see Phase 3/4 backlog.**

### System Design/Transactions_Interview_Prep.md

Isolation levels and their PostgreSQL-specific behavior (Q2–3), MVCC (Q4), Spring propagation defaults and the shared-rollback implication of `REQUIRED` (Q5–6), proxy-based self-invocation and private-method limitations (Q8–9, consistent with the Spring Boot Internals guide's Q12/14 fix), default rollback-on-unchecked-only behavior (Q10), deadlocks (Q13), optimistic/pessimistic concurrency (Q14–15), the outbox pattern (Q19), and 2PC-vs-saga trade-offs (Q22–23, correctly hedged — "2PC isn't *never* used," not an absolute) were all checked against PostgreSQL documentation, the Spring Framework reference, and the cited papers/pattern sources. No Critical/Major findings in this pass.

**Guide status: Verified. Spot-checked in depth (isolation levels, propagation, self-invocation/private-method proxy behavior, rollback rules, 2PC/saga) with no findings; not every one of the 30 questions was individually re-verified line-by-line in this pass the way the other 14 guides were — treat as a strong but slightly lighter pass than the rest of the repo. Version-baseline header present. TOC not yet added — see Phase 3/4 backlog.**

## Repo-wide checks

| Check | Result | Status |
|---|---|---|
| Internal markdown links (relative paths + `#anchor` fragments) resolve | `scripts/check_internal_links.py`, verified against `github-slugger` (the library GitHub's renderer actually uses) for anchor correctness — 21 files, 0 broken | **Pass** — wired into CI |
| Duplicate headings within a file | `scripts/check_duplicate_headings.py` (skips fenced code blocks after an early false positive on an identical thread-dump line in a deadlock example) — 21 files, 0 found | **Pass** — wired into CI |
| Markdown lint | `markdownlint-cli2` with `.markdownlint.yaml` tuned to this repo's house style — 21 files, 0 issues (2 missing code-fence language tags found and fixed along the way) | **Pass** — wired into CI |
| External link liveness | `lychee` with `.lychee.toml` (retries, realistic user agent, justified allowlist for confirmed-live-but-bot-blocking domains and the illustrative `*.example.com` code-example hostnames) — 1476 links checked, 1476 OK, 0 errors, 19 correctly excluded | **Pass** — wired into CI, plus a monthly scheduled run since link rot happens independent of edits |
| README links to reserved directories (`Design Patterns`, `Frontend & Full-Stack`, `Forward-Deployed & Customer-Facing Engineering`) | Directories did not exist; created a placeholder `README.md` in each, clearly marked "reserved — not yet written" | **Fixed** |
| "let me know and I'll restructure it" / similar chat-meta-commentary | Found once (Java_Collections, end of file) — repo-wide grep confirms no other instances anywhere in the repo | **Fixed** |
| Version-baseline / target-level / last-verified / prerequisites header on every guide | Added to all 15 guides | **Fixed** |
| Table of Contents on every guide | Added to 12 of 15 guides (all except Kafka, Redis, Transactions) | Open — see backlog |

## Guide verification status

| Guide | Status |
|---|---|
| Language/Java_Collections_Interview_Prep.md | Verified |
| Language/Java_Concurrency_Interview_Prep.md | Verified |
| Language/Java_JVM_GC_Interview_Prep.md | Verified — no findings |
| Frameworks/Spring_Boot_Internals_Interview_Prep.md | Verified |
| Frameworks/Spring_Security_OAuth2_Interview_Prep.md | Verified — no correctness findings |
| Frameworks/JPA_Hibernate_Interview_Prep.md | Verified |
| System Design/REST_API_Design_Interview_Prep.md | Verified |
| System Design/Cross_Stack_Design_Scenarios_Interview_Prep.md | Verified |
| Microservices & Architecture Patterns/Microservices_Architecture_Patterns_Interview_Prep.md | Verified — no blocking findings |
| Kubernetes, Docker & Cloud/Kubernetes_Docker_Interview_Prep.md | Verified |
| AI Engineering/AI_Engineering_Interview_Prep.md | Verified |
| Tech Leadership/Engineering_Leadership_Interview_Prep.md | Verified |
| System Design/Kafka_Interview_Prep.md | Verified |
| System Design/Redis_Caching_Interview_Prep.md | Verified |
| System Design/Transactions_Interview_Prep.md | Verified (spot-checked in depth; see note above) |

"Verified" means: audited against the Phase 1 checklist and this repository's known-issues list, with all Critical/Major findings from that pass fixed. It does **not** mean every question has been rewritten into the full Phase 2 six-part standardized structure (Question / Short answer / Deep dive / Example / Failure modes / Follow-ups / Sources) — the existing Answer/Code/Follow-up/Source structure was judged accurate and well-organized enough that a wholesale rewrite risked introducing errors for uncertain benefit, and was deliberately not attempted in this pass (see backlog).

## Phase 3/4 backlog (not yet done)

- Table of contents on the Kafka, Redis, and Transactions guides (the other 12 have one).
- Full Phase 2 rewrite of every question into the six-part standardized structure. This repository contains exactly 413 numbered questions across the 15 guides (counted programmatically, matching the task's original estimate — see the per-guide counts in each guide's own "Guide status" line above). This was not attempted; Phase 1 (accuracy) and the explicitly listed known issues were prioritized per the task's own instruction not to proceed to content restructuring before the audit is complete. This is a genuinely large, separate scope decision the repository owner should make deliberately rather than have it happen as a side effect of an accuracy pass.
- Extracting Java/SQL examples into standalone, CI-testable sample projects (Phase 3, "where practical"). Not attempted — would need per-example scaffolding (Maven/Gradle module, test harness) and is a substantial project of its own.
- Licensing — deliberately not chosen; needs the repository owner's decision (see `CONTRIBUTING.md`).
- Java_Collections Q10 vs. Java_JVM_GC's heap-dump question redundancy — flagged, not consolidated (both are independently accurate; low priority).
