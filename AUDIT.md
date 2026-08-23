# Audit Log

This file tracks the accuracy audit of every guide in this repository, per
the repository's accuracy policy (see `CONTRIBUTING.md`). Each row is one
finding. A guide is not considered "reviewed" until every Critical/Major
row for that guide has `Status = Fixed` or `Status = Won't fix (documented)`.

Severity legend:

- **Critical** — factually wrong, would mislead a candidate or embarrass
  them in an interview.
- **Major** — imprecise or missing an important qualifier/version boundary.
- **Minor** — technically defensible but sloppy wording, weak example, or
  missing citation.
- **Editorial** — artifacts, filler, formatting, structure, duplication.

## Findings

### Computer Science Fundamentals/Computer_Science_Fundamentals_Interview_Prep.md

New guide, added 2026-08-23 — not a rewrite/graduation of existing content like the entries below, so there's no "before" state to diff against. 15 Basic-only questions (no Staff tier, by design) covering networking (TCP/UDP, DNS, IP/ports, URI/URL/URN), HTTP (statelessness, HTTP/1.1 vs. 2 vs. 3, status code categories, headers vs. body), encryption/security (symmetric vs. asymmetric, encryption vs. hashing, the TLS handshake, certificates/CAs), and general terminology (Big-O, SQL vs. NoSQL, API vs. web service). Every citation (mostly IETF RFCs — 9293, 768, 1035, 3986, 9110, 9113, 9114, 8446, 5280 — plus IANA, NIST, MIT OCW, PostgreSQL/MongoDB docs, W3C) was checked live before being included; 0 broken links. Cross-references into six other guides (Java Collections, REST API Design, Spring Security & OAuth2, Docker & Kubernetes, Transactions, Redis & Caching) were written descriptively (by guide name, not question number) specifically so they won't go stale if those guides are renumbered again in the future — a deliberate choice after the numbered-cross-reference maintenance burden encountered graduating the other six guides.

**Expanded (2026-08-23, same day):** 13 more questions added, covering classic computer-science-degree curriculum terminology not otherwise in this kit — **Data Structures & Algorithms** (stack/queue, tree vs. graph, recursion/base case), **Programming Languages & OOP** (the four OOP pillars, compiled vs. interpreted, static vs. dynamic typing), **Operating Systems** (kernel/OS role, virtual memory/paging, CPU caching), **Databases** (normalization/1NF-2NF-3NF, indexes), and **Software Engineering Practices** (version control/Git, unit vs. integration vs. E2E tests). Appended after the existing 15 (numbered 16–28) rather than interleaved, so no renumbering of the original 15 was needed and no cross-references anywhere in the repo needed updating. New citations included Oracle Java Tutorials, the JLS, *Operating Systems: Three Easy Pieces* (a free, widely-used OS textbook), an MIT OCW database-normalization lecture, PostgreSQL's indexes documentation, the official Git book, and Martin Fowler's test-pyramid article — all checked live before inclusion; 0 broken links. Same descriptive (not numbered) cross-reference convention as the original 15 was continued.

**Guide status: Reviewed. 28/28 questions reviewed, TOC added, version-baseline header present. Basic-only by design — see `README.md`'s "Difficulty by guide" table.**

### Language/Java_Collections_Interview_Prep.md

| Question | Severity | Problem | Correct interpretation | Authoritative source | Status |
|---|---|---|---|---|---|
| Q14 (was Q2 before the 2026-08-23 renumbering below) — Mutable HashMap key | Critical | Stated a mutated-key entry becomes "permanently unreachable through the API." | `get()`/`remove()` via a freshly computed hash fail, but the entry is still findable via iteration, and becomes `get()`-reachable again if the key's hash-relevant state is restored. | [`HashMap` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashMap.html) | **Fixed** |
| Q14 follow-up — records as map keys (2026-08-22 pass) | Major | Claimed `record` types are a good fit as map/set keys "because they're immutable," without noting records are only shallowly immutable. | A record's component *references* can't be reassigned, but a mutable component's own state can still change, changing `hashCode()` — reproducing the exact bug the question demonstrates. Records work well as keys when all components are themselves immutable, or mutable inputs are defensively copied. | [`java.lang.Record` Javadoc — "a shallowly immutable, transparent carrier"](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Record.html) | **Fixed** |
| Q15 (was Q3 before the 2026-08-23 renumbering below) — Java 7 `ConcurrentHashMap` segments | Major | Claimed "16 fixed segments" unconditionally. | 16 was only the default `concurrencyLevel` for the no-arg constructor; actual segment count depended on the configured `concurrencyLevel`. | JDK 7 `ConcurrentHashMap` Javadoc | **Fixed** |
| Q15 — synchronization claim | Major | Code comment: "no external synchronization needed, ever." | Individual operations and documented compound methods are atomic; multi-key/cross-resource invariants still need external coordination. | [`ConcurrentHashMap` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html) | **Fixed** |
| End of file | Editorial | Leftover conversational artifact addressed to the repo author. | Remove. | — | **Fixed** |
| Q22 (was Q10 before the 2026-08-23 renumbering below) vs JVM_GC heap-dump question | Editorial | Real redundancy: both fully explain the MAT/`jmap`/path-to-GC-roots workflow. | Worth consolidating in a future pass; not done here (small enough overlap, both versions are independently accurate). | — | Open (low priority) |
| Guide graduated Basic → Staff (2026-08-23) | — | Guide was the answer-length-restructuring pilot but had no true entry-level on-ramp — all 15 questions already assumed familiarity with the collection types being compared. | Added 12 new questions — 7 Basic (framework/interface overview, `List`/`Set`/`Map` basics, the `equals()`/`hashCode()` contract, `HashSet`/`LinkedHashSet`/`TreeSet`, `Iterator` basics, iterating a `Map`, `Comparable` vs. `Comparator`) and 5 Intermediate (`ArrayList` vs. `LinkedList` basics, `Iterator` vs. `ListIterator`, `Queue` vs. `Deque`, choosing among `HashMap`/`LinkedHashMap`/`TreeMap`, `Collection` vs. `Collections`) — as new `## Basic`/`## Intermediate` sections before the existing 15 questions, now wrapped in `## Staff Level`, using the same five-part (Core answer/Staff-level extension/Example/Follow-up questions/Sources) structure already established by the pilot. The original 15 questions were renumbered 1–15 → 13–27; the two internal self-references ("from question 3," "from question 10") and one cross-file reference (Java_Concurrency's "question 11 in the collections file") were updated to the new numbers. No existing question content was altered beyond the number/heading-level change. All 12 new Core answers measure 109–158 words (within the established 100–180 range); all citations verified live before writing. | — | **Added** |

**Guide status: Reviewed. 27/27 questions reviewed (15 original Staff-level + 12 new Basic/Intermediate, 2026-08-23), TOC added, version-baseline header present. Graduated Basic → Staff, matching Java Concurrency and Kubernetes/Docker. Uses the five-part (Core answer/Staff-level extension/Example/Follow-up questions/Sources) structure throughout — no longer just the pilot, this is now the second guide fully on that structure (see the answer-length restructuring rollout note in the backlog).**

**Answer-length restructuring pilot (2026-08-22):** The README promised ~30–90-second spoken answers, but a repo-wide measurement of 358 labeled Answer sections found a 234-word median (≈94 seconds at 150 wpm), 206 answers over 225 words, and none under 75 — this guide's own Q5 was the worst offender at 649 words. Rather than trim depth outright, this guide was restructured question-by-question into **Core answer** (100–180 words, the actual spoken-out-loud answer) / **Staff-level extension** (the deeper trade-off material moved out of the core response, not deleted) / **Example** (renamed from Code) / **Follow-up questions** (interviewer-style Q&A pairs, renamed from Follow-up) / **Sources** (renamed from Source). All 15 Core answers now measure 116–176 words (verified programmatically). This was done as a pilot on one guide only, per the repository owner's explicit choice, to be reviewed before deciding whether to roll the same treatment out to the other 14 guides — see backlog.

### Language/Java_Concurrency_Interview_Prep.md

| Question | Severity | Problem | Correct interpretation | Authoritative source | Status |
|---|---|---|---|---|---|
| Q14 (was Q1 before the 2026-08-23 renumbering below) — JMM / happens-before | Critical | Racy code called "actually undefined" / "genuinely undefined behavior." | Without happens-before, visibility/ordering aren't guaranteed, but the JMM (JLS Ch. 17) still constrains execution — not UB in the C/C++ sense. | [JLS §17.4](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html#jls-17.4) | **Fixed** |
| Q33 (was Q20 before the 2026-08-23 renumbering below) — Structured concurrency | Critical | Cited JEP 505 but used the removed constructor-based `new StructuredTaskScope.ShutdownOnFailure()` API. | JEP 505 replaced constructors with `StructuredTaskScope.open(Joiner)`. Rewrote example to that API; flagged that JEP 525/533 have continued changing it (JEP 533 changes the thrown exception to `ExecutionException`). | [JEP 505](https://openjdk.org/jeps/505), [JEP 525](https://openjdk.org/jeps/525), [JEP 533](https://openjdk.org/jeps/533), [`Joiner` Javadoc, JDK 25](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/StructuredTaskScope.Joiner.html) | **Fixed** |
| Guide graduated Basic → Staff (2026-08-23) | — | Guide previously started at Lead/Staff depth with no on-ramp, unlike the graduated Java Collections (Senior → Staff) and Kubernetes/Docker (Basic → Staff) guides. | Added 13 new questions — 8 Basic (thread vs. process, creating threads, thread lifecycle, race conditions, `synchronized` basics, deadlock basics, `wait`/`notify` vs. `sleep`, daemon threads) and 5 Intermediate (`ExecutorService`, `Runnable`/`Callable`/`Future`, `CountDownLatch`/`CyclicBarrier`/`Semaphore`, producer-consumer via `BlockingQueue`, `synchronized` vs. `ReentrantLock` basics) — as new `## Basic`/`## Intermediate` sections before the existing 20 questions, now wrapped in `## Staff Level`. The original 20 questions were renumbered 1–20 → 14–33 (heading level `##` → `###` to nest under the new level sections); the one internal self-reference ("from question 6") was updated to the new number ("from question 19"). No existing question content was altered beyond the number/heading-level change. All 13 new questions cite Oracle Javadoc/JLS/Java Tutorials sources, verified live. | — | **Added** |

**Guide status: Reviewed. 33/33 questions reviewed (20 original Staff-level + 13 new Basic/Intermediate, 2026-08-23), TOC added, version-baseline header present. Graduated Basic → Staff, matching the Java Collections and Kubernetes/Docker guides.**

### Language/Java_JVM_GC_Interview_Prep.md

No factual errors found against JVMS §2.5, G1/ZGC/Shenandoah docs, JEP 439, or container-awareness documentation.

| Question | Severity | Problem | Correct interpretation | Authoritative source | Status |
|---|---|---|---|---|---|
| Q13 (was Q1) follow-up — wrong internal cross-reference (found and fixed 2026-08-23) | Minor | Pre-existing bug, found incidentally while renumbering: the follow-up said "covered in more depth in question 8," but Q8 (now Q20) is about stop-the-world pauses/safepointing, unrelated to the container-OOM-kill topic actually being referenced. | The intended target was the container-kill question (old Q14, now Q26, "Why Can the Container Kill a Java Process Even When Heap Usage Is Below `-Xmx`?"). | — | **Fixed** |
| Guide graduated Basic → Staff (2026-08-23) | — | Guide started directly at Lead/Staff depth (memory areas, JIT internals, GC collector selection) with no on-ramp, unlike the graduated Collections/Concurrency/Kubernetes guides. | Added 12 new questions — 7 Basic (JVM/JDK/JRE, stack vs. heap, what GC is and why, `ClassLoader` basics, bytecode interpretation vs. JIT, why the heap has young/old generations, `==` vs. `.equals()`) and 5 Intermediate (collector types overview before the G1/ZGC/Shenandoah comparison, minor vs. major/full GC, what a Java "memory leak" actually means given GC, basic JVM memory flags, metaspace vs. the old PermGen) — as new `## Basic`/`## Intermediate` sections before the existing 18 questions, now wrapped in `## Staff Level`. The original 18 questions were renumbered 1–18 → 13–30; three internal self-references were updated to the new numbers (including the pre-existing wrong reference above). All citations verified live before writing, including two corrected Oracle GC-tuning-guide URLs (the guide's actual page slugs differ from the intuitive ones — e.g. `garbage-collector-implementation1.html`, not `garbage-collector-implementation.html`). | — | **Added** |

**Guide status: Reviewed. 30/30 questions reviewed (18 original Staff-level + 12 new Basic/Intermediate, 2026-08-23), TOC added, version-baseline header present. Graduated Basic → Staff, matching Java Collections, Java Concurrency, and Kubernetes/Docker.**

### Frameworks/Spring_Boot_Internals_Interview_Prep.md

| Question | Severity | Problem | Correct interpretation | Authoritative source | Status |
|---|---|---|---|---|---|
| Q13 (was Q1) — early events | Critical | Showed `@Component` + `@EventListener` handling `ApplicationStartingEvent`/`ApplicationEnvironmentPreparedEvent`, which fire before the `ApplicationContext` exists. | Must register via `SpringApplication.addListeners(...)` or a `spring.factories` `ApplicationListener` entry; `@Component`/`@EventListener` only works from `ContextRefreshedEvent` onward. | [Spring Boot Reference — Application Events and Listeners](https://docs.spring.io/spring-boot/reference/features/spring-application.html) | **Fixed** |
| Q16 (was Q4) — `@Primary` vs `@Qualifier` | Critical | Prose stated Spring checks `@Primary` before `@Qualifier`, contradicting the question's own code example, which showed an injection-point `@Qualifier` overriding `@Primary`. | An explicit `@Qualifier` at the injection point is resolved first (a specific, per-injection-point instruction); `@Primary` is the tie-breaker only when no qualifier is given and multiple type-matching candidates remain. | [`@Primary` Javadoc](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/context/annotation/Primary.html), [Qualifiers reference](https://docs.spring.io/spring-framework/reference/core/beans/annotation-config/autowired-qualifiers.html) | **Fixed** |
| Q24/26 (was Q12/14) follow-ups — proxy method visibility | Critical | Blanket "advised methods must be public" framing. | Interface-based (JDK) proxies: public-only. Class-based (CGLIB) proxies: as of **Spring Framework 6.0**, protected/package-visible methods can also be made transactional by default. Private/effectively-private methods never advisable. | [Spring Framework Reference — `@Transactional` method visibility](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html), [Proxying Mechanisms](https://docs.spring.io/spring-framework/reference/core/aop/proxying.html) | **Fixed** |
| Q29 (was Q17) follow-up | Major | Claimed `SpringApplicationRunListener` registers via the same `.imports` mechanism as `@AutoConfiguration`. | It uses the older `META-INF/spring.factories` mechanism, distinct from `AutoConfiguration.imports`. | Spring Boot Reference docs | **Fixed** |
| Q13 follow-up / Q29 (was Q1 follow-up / Q17) — `ApplicationFailedEvent` (2026-08-22 pass) | Critical | Implied `ApplicationFailedEvent` is safe to handle with an ordinary `@Component`/`@EventListener`, grouping it with the post-`ContextRefreshedEvent` "safe" events; Q29's code example demonstrated exactly this pattern as the recommended one. | Spring documents it simply as the event sent when an exception occurs during startup, with no guaranteed minimum stage — a failure can happen before the context has created that bean at all. Reliable handling requires a listener registered directly with `SpringApplication.addListeners(...)` (or `spring.factories`), not a regular managed bean. | [Spring Boot Reference — Application Events and Listeners](https://docs.spring.io/spring-boot/reference/features/spring-application.html#features.spring-application.application-events-and-listeners) | **Fixed** |
| Q15 (was Q3) — `AutowiredAnnotationBeanPostProcessor` phase (2026-08-22 pass) | Major | Cited `AutowiredAnnotationBeanPostProcessor` as an example of the before-initialization `BeanPostProcessor` callback phase. | Its injection work runs through `postProcessProperties()` during dependency/property population — a distinct, earlier stage than `postProcessBeforeInitialization`. Separated the lifecycle explicitly into instantiation → property population → `postProcessBeforeInitialization` → initialization → `postProcessAfterInitialization`/proxying. | [`AutowiredAnnotationBeanPostProcessor` Javadoc](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/beans/factory/annotation/AutowiredAnnotationBeanPostProcessor.html) | **Fixed** |
| Fenced code block | Editorial | `spring.factories`-style snippet's code fence had no language tag (markdownlint MD040). | Tagged `text`. | — | **Fixed** |
| Guide graduated Basic → Staff (2026-08-23) | — | Guide started directly at Lead/Staff depth with no on-ramp, despite the README describing it as assuming only "basic Spring." | Added 12 new questions — 7 Basic (what Spring/DI solve, bean/`ApplicationContext` basics, `@Component` family, injection styles, Spring Boot vs. Framework, `@SpringBootApplication`, properties vs. YAML) and 5 Intermediate (bean scopes, `@Bean` vs. `@Component`, profiles, `@RestController` vs. `@Controller`, `@Value` vs. `@ConfigurationProperties`) — as new `## Basic`/`## Intermediate` sections before the existing 25 questions, now wrapped in `## Staff Level`. The original 25 questions were renumbered 1–25 → 13–37; all 15 internal cross-references (verified individually against their actual targets before renumbering — none were wrong) were updated to the new numbers. The one cross-file reference from `AUDIT.md`'s Transactions entry ("Spring Boot Internals guide's Q12/14 fix") was also updated. All 12 new citations verified live before writing. | — | **Added** |

**Guide status: Reviewed. 37/37 questions reviewed (25 original Staff-level + 12 new Basic/Intermediate, 2026-08-23), TOC added, version-baseline header present. Graduated Basic → Staff, matching Collections, Concurrency, JVM & GC, and Kubernetes/Docker.**

### Frameworks/Spring_Security_OAuth2_Interview_Prep.md

No Critical/Major findings after a full read, including targeted verification of filter-chain ordering (Q16, was Q4), CSRF/CORS (Q19–20, was Q7–8), OAuth2 authorization-code flow with PKCE against RFC 7636 (Q22, was Q10), and JWT/JWKS validation and key rotation against RFC 7519/7517 (Q28–29, was Q16–17) — the `aud`-validation-not-checked-by-default callout in Q28 (was Q16) in particular is a real, correctly-flagged Spring Security gap, not an error. No duplicates, no conversational artifacts, no broken links.

| Question | Severity | Problem | Correct interpretation | Authoritative source | Status |
|---|---|---|---|---|---|
| Guide graduated Basic → Staff (2026-08-23) | — | Guide started directly at Lead/Staff depth (filter chain internals, OAuth2 flows, JWT validation) with no on-ramp, despite the README describing it as assuming only Spring Boot Internals. | Added 12 new questions — 7 Basic (what Spring Security/`@EnableWebSecurity` does, `UserDetailsService`, Basic Auth vs. form login, password hashing/`BCryptPasswordEncoder`, cookies vs. sessions, HTTPS/TLS basics, RBAC/`@PreAuthorize` basics) and 5 Intermediate (`hasRole()` vs. `hasAuthority()`, JWT structure before validation, `permitAll()`/`authenticated()`/`denyAll()`, CSRF basics before the enable/disable decision, `AuthenticationEntryPoint`) — as new `## Basic`/`## Intermediate` sections before the existing 30 questions, now wrapped in `## Staff Level`. The original 30 questions were renumbered 1–30 → 13–42; all internal cross-references were updated to the new numbers, including two multi-number references ("question 7/8," "question 25/26") a first automated pass initially handled incorrectly and required a manual fix. Two cross-file numbered references from Cross-Stack Design Scenarios (old Q17 and Q30) and this guide's own AUDIT.md finding-row labels (Q4, Q7–8, Q10, Q16–17) were also updated. One citation URL 404'd during verification (`.../authorization/expression-based.html`, removed from the current docs) and was corrected to the live `.../authorization/method-security.html` page before being included. | — | **Added** |

**Guide status: Reviewed — no correctness findings. 42/42 questions reviewed (30 original Staff-level + 12 new Basic/Intermediate, 2026-08-23), TOC added, version-baseline header present. Graduated Basic → Staff, matching Spring Boot Internals and the other graduated guides.**

### Frameworks/JPA_Hibernate_Interview_Prep.md

| Question | Severity | Problem | Correct interpretation | Authoritative source | Status |
|---|---|---|---|---|---|
| Q33 (was Q21) follow-up — pessimistic lock timeout | Minor | Cited `javax.persistence.lock.timeout` while the rest of the guide targets Jakarta Persistence 3.1 (`jakarta.persistence.*`). | Corrected to `jakarta.persistence.lock.timeout`. | [Jakarta Persistence Specification 3.1](https://jakarta.ee/specifications/persistence/3.1/jakarta-persistence-spec-3.1.html) | **Fixed** |
| Guide graduated Basic → Staff (2026-08-23) | — | Guide started directly at Lead/Staff depth (entity lifecycle, dirty checking, N+1, locking) with no on-ramp, despite the README describing it as assuming only Spring Boot Internals + basic SQL. | Added 12 new questions — 7 Basic (what an ORM/JPA/Hibernate is, `@Entity` requirements, Spring Data JPA/repositories, `@Id`/`@GeneratedValue`, relationship-annotation cardinality, DTOs) and 5 Intermediate (`save`/`findById`/`deleteById`, JPQL vs. native SQL, `@Transactional` at service vs. repository layer, composite keys, `CascadeType.ALL` vs. individual types) — as new `## Basic`/`## Intermediate` sections before the existing 30 questions, now wrapped in `## Staff Level`. The original 30 questions were renumbered 1–30 → 13–42; this was the densest guide for internal cross-references (~55 occurrences, including four compound "question N/M" references — `22/23`, `4/5`, `15/16`, `8/29` — that needed both numbers offset, handled as a distinct regex pass to avoid the partial-fix bug encountered on the Spring Security guide's compound references). Five cross-file numbered references from Cross-Stack Design Scenarios (old Q7, Q9 ×2, Q25, Q30) were also updated. All 12 new citations verified live before writing. | — | **Added** |

Dependency-resolution question (known issue #9) was independently re-checked in this guide's own scope and found already accurate. Entity lifecycle, dirty checking/flush timing, N+1 causes/fixes, LAZY/EAGER defaults per association type, and `GenerationType.IDENTITY` disabling JDBC batching were all verified correct.

**Guide status: Reviewed. 42/42 questions reviewed (30 original Staff-level + 12 new Basic/Intermediate, 2026-08-23), TOC added, version-baseline header present. Graduated Basic → Staff — the fifth and final guide in this rollout, matching Collections, Concurrency, JVM & GC, Spring Boot Internals, and Spring Security & OAuth2.**

### System Design/REST_API_Design_Interview_Prep.md

| Question | Severity | Problem | Correct interpretation | Authoritative source | Status |
|---|---|---|---|---|---|
| Q10 — ETag | Editorial | Malformed markdown span: `` `ETag** `` (mismatched backtick/bold). | Fixed to `` `ETag` ``. | — | **Fixed** |
| Q4 — idempotent methods | Editorial | Code block omitted `TRACE`, though prose correctly includes it. | Added `TRACE` to the code block. | [RFC 9110 §9.2.2](https://datatracker.ietf.org/doc/html/rfc9110#section-9.2.2) | **Fixed** |
| Q5 vs Cross-Stack Q11 | Minor | ~90% duplicated idempotency-key mechanism and code with Cross-Stack Design Scenarios Q11. | Trimmed Cross-Stack Q11 to cross-reference this question and focus on the client-contract + incident-investigation angle instead of re-explaining the mechanism. | — | **Fixed** |

HTTP semantics (RFC 9110/9111/9457/7396/6902/4918) and CAP theorem framing checked out.

**Guide status: Reviewed. 28/28 questions reviewed, TOC added, version-baseline header present. Restructured (2026-08-22) into the five-part shape — the second guide, after Java Collections, to receive this treatment.**

**Answer-length restructuring rollout, guide 2 of 15 (2026-08-22):** Following the Java Collections pilot (see that guide's own "Guide status" note), this guide's 28 questions were restructured into **Core answer** (100–180 words) / **Staff-level extension** / **Example** (renamed from Code) / **Follow-up questions** (renamed from Follow-up) / **Sources** (renamed from Source). Pre-restructuring, answers ranged 160–324 words (average 235, five over 250); all 28 Core answers now measure 132–180 words (verified programmatically). No content was deleted — material trimmed from the Answer paragraphs, and the prose from the original Follow-up sections, was redistributed into Staff-level extension and Follow-up questions rather than cut.

### System Design/Cross_Stack_Design_Scenarios_Interview_Prep.md

| Question | Severity | Problem | Correct interpretation | Authoritative source | Status |
|---|---|---|---|---|---|
| Q11 vs REST API Q5 | Minor | Duplicate — see REST API Design entry above. | Consolidated. | — | **Fixed** |
| Q7 — circuit-breaker fallback | Major | `@CircuitBreaker(fallbackMethod = "servedegraded")` didn't match the actual method name `serveDegraded` — Resilience4j resolves fallback methods by exact, case-sensitive name via reflection, so this would fail to wire up at runtime rather than degrade gracefully as claimed. | Fixed the string to `"serveDegraded"`. | [Resilience4j docs](https://resilience4j.readme.io/docs/circuitbreaker) | **Fixed** |

Cross-checked against the now-reviewed Kafka, Redis, and Transactions guides for consistency on partition ordering, eviction/rate-limiting, and isolation-level claims — no contradictions found.

**Guide status: Reviewed. 20/20 questions reviewed, TOC added, version-baseline header present.**

### Microservices & Architecture Patterns/Microservices_Architecture_Patterns_Interview_Prep.md

CAP theorem (Q20) is correctly scoped to "during a network partition," not oversimplified as a blanket pick-2-of-3, and cites both Brewer's own retrospective and PACELC as a refinement. Service mesh (Q12) and ambassador/adapter (Q13) sections were checked for the "what's genuinely solved vs. often oversold" framing the task asked for and found substantively accurate, with real failure-mode content (retry-policy compounding across mesh + application layers) rather than trivia. No Critical/Major findings.

**Guide status: Reviewed — no blocking findings. 25/25 questions reviewed, TOC added, version-baseline header present.**

### Kubernetes, Docker & Cloud/Kubernetes_Docker_Interview_Prep.md

| Question | Severity | Problem | Correct interpretation | Authoritative source | Status |
|---|---|---|---|---|---|
| Q17 — ConfigMap vs Secret | Major | Implied `kubectl get`/`describe` both hide Secret values by default. | Only `kubectl describe secret` redacts (byte counts only); `kubectl get secret -o yaml/json` prints the full base64-encoded data — real protection is RBAC, not `describe`'s redaction. | [Kubernetes — Secrets](https://kubernetes.io/docs/concepts/configuration/secret/) | **Fixed** |
| Q20 — dockershim | Editorial | "was removed" with no version. | Deprecated v1.20, removed v1.24. | [Kubernetes — Dockershim Removal FAQ](https://kubernetes.io/blog/2022/02/17/dockershim-faq/) | **Fixed** |
| Q32 — PodSecurityPolicy | Editorial | "now-removed" with no version. | Deprecated v1.21, removed v1.25. | [Kubernetes — Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/) | **Fixed** |

**Guide status: Reviewed. 35/35 questions reviewed, TOC added, version-baseline header present.**

### AI Engineering/AI_Engineering_Interview_Prep.md

| Question | Severity | Problem | Correct interpretation | Authoritative source | Status |
|---|---|---|---|---|---|
| Q24 — resilience code | Major | Code block mixed Java/Spring annotations (`@CircuitBreaker`, `@Retryable`, `@Backoff`) onto a Python function — doesn't compile in either language. | Rewrote using real Python libraries (`tenacity`, `pybreaker`) with a working call pattern. | [tenacity docs](https://tenacity.readthedocs.io/), [pybreaker](https://github.com/danielfm/pybreaker) | **Fixed** |

This is the fastest-moving guide in the repo (model capabilities/pricing/context windows). The version-baseline header explicitly flags specific numbers as approximate and to be re-verified before an interview, rather than stating them as permanent fact — see the header's own "last verified" caveat.

**Guide status: Reviewed. 27/27 questions reviewed, TOC added, version-baseline header present (with the fast-moving-content caveat above).**

### Tech Leadership/Engineering_Leadership_Interview_Prep.md

| Question | Severity | Problem | Correct interpretation | Authoritative source | Status |
|---|---|---|---|---|---|
| Q2, Q20 follow-ups | Editorial | First-person "I've seen..." phrasing implying personal production experience (task rules prohibit inventing this). | Reworded to observational framing; added an explicit "personal example to add" placeholder at the Q20 spot per repo policy. | — | **Fixed** |

No fabricated metrics or incidents found beyond the two reworded phrasings above.

**Guide status: Reviewed. 25/25 questions reviewed, TOC added, version-baseline header present.**

### System Design/Kafka_Interview_Prep.md

| Question | Severity | Problem | Correct interpretation | Authoritative source | Status |
|---|---|---|---|---|---|
| Q9 — idempotent producer scope (known issue #3) | Major | Summarized idempotence scope as "single producer session, single partition," readable as if a producer using idempotence could only safely write to one partition total. | Sequencing/dedup is tracked independently **per partition** within a session (a producer can write to many partitions); idempotence alone gives no atomicity across partitions/topics — that's what transactions add. | [Confluent — Exactly-once Semantics Is Possible](https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/) (quote verified: "For a single partition, Idempotent producer sends remove the possibility of duplicate messages") | **Fixed** |
| Version-baseline header (2026-08-22 pass) | Major | Header said "Baseline: Apache Kafka 3.x" while "Last verified" was dated 2026; Kafka 4.0 (KRaft-only, ZooKeeper removed) GA'd March 2025, so the stated baseline was stale relative to the verification date. | Updated the baseline to Kafka 4.x and added an explicit note that this guide's rebalancing content describes the classic consumer-group protocol (still the client default in 4.x), distinct from the new KIP-848 protocol that's broker-default-but-client-opt-in as of 4.0. | [Apache Kafka 4.0.0 Release Announcement](https://kafka.apache.org/blog/2025/03/18/apache-kafka-4.0.0-release-announcement/) | **Fixed** |
| Q2 — "strict FIFO" ordering (2026-08-22 pass) | Major | Stated partition-scoped ordering as unconditional "strict FIFO," without noting it depends on producer configuration. | Ordering within a partition holds when idempotence is enabled (default since Kafka 3.0.1/3.2.0) or `max.in.flight.requests.per.connection=1`; without idempotence and with more than one in-flight request, a retry can reorder records even within one partition (Q12). | [Apache Kafka Documentation — Producer Configs](https://kafka.apache.org/documentation/#producerconfigs) | **Fixed** |
| Q3 — same key → same partition (2026-08-22 pass) | Major | "Every record with the same key always lands in the same partition" was qualified only for partition-count changes. | Also depends on a fixed partitioner implementation and a key serializer that's deterministic for logically-equal keys; either changing breaks the mapping. | [Apache Kafka Documentation — Producer Configs](https://kafka.apache.org/documentation/#producerconfigs) | **Fixed** |
| Q6 — static membership "reduces rebalances to zero" (2026-08-22 pass) | Major | Claimed static membership could reduce rolling-deploy rebalances "to zero" without qualification. | It eliminates the rebalance for a same-instance restart returning within `session.timeout.ms`; genuine scale-up/down or a late-returning consumer still triggers one. | [KIP-345](https://cwiki.apache.org/confluence/display/KAFKA/KIP-345%3A+Introduce+static+membership+protocol+to+reduce+consumer+rebalances) | **Fixed** |
| Q7 — at-least-once "never silently dropped" (2026-08-22 pass) | Major | Implied at-least-once guarantees the business outcome is never lost, when the guarantee is scoped to Kafka's own redelivery, not to the consumer's processing logic. | Auto-commit misconfiguration or a consumer that swallows a processing failure can still lose the effective outcome even though Kafka redelivered the message correctly. | [Apache Kafka Documentation — Message Delivery Semantics](https://kafka.apache.org/documentation/#semantics) | **Fixed** |
| Q10 — RF=3/`min.insync.replicas=2`/`acks=all` "no write unavailability" (2026-08-22 pass) | Major | Stated this configuration tolerates any single-broker loss "without data loss or write unavailability," unconditionally. | Holds only if the lost broker was already fully in sync; a leader loss still has a brief election window, and an ISR already degraded before the loss can drop write availability entirely. | [Apache Kafka Documentation — Broker Configs](https://kafka.apache.org/documentation/#brokerconfigs) | **Fixed** |
| Q11 — "classic CAP-style tension" (2026-08-22 pass) | Minor | Called the `acks=all`/`min.insync.replicas` trade-off a "classic CAP" trade-off; CAP formally describes behavior during a network partition, while this trade-off applies to any replica unavailability, partition or not. | Reworded to "structurally similar to, but not a literal instance of, CAP." | — | **Fixed** |

Full read of all 40 conceptual questions + 15 scenario questions. Ordering guarantees (Q2), rebalancing (Q4–6), delivery semantics (Q7), `acks`/ISR/replication (Q10–11), retention/compaction (Q29–30), and all 15 scenario questions checked against Kafka documentation and cited KIPs (429, 345, 98) — no other Critical/Major findings from the original pass. A second pass (this round) found the seven overly-absolute-language issues above, all now fixed; two scenario answers (S5, S38-adjacent payments-pipeline design) carried the same RF/ISR overstatement by restating Q10's claim and were softened to cross-reference the corrected version instead of re-asserting it independently.

**Guide status: Reviewed. 55/55 questions reviewed (40 conceptual + 15 scenario), version-baseline header present. TOC not yet added — see Phase 3/4 backlog.**

### System Design/Redis_Caching_Interview_Prep.md

| Question | Severity | Problem | Correct interpretation | Authoritative source | Status |
|---|---|---|---|---|---|
| Q22 — rate-limiter EXPIRE bug (known issue #4) | Critical | Lua rate limiter called `EXPIRE` unconditionally on every allowed request and described this as "harmless." Resetting the TTL on every request means the window's expiry keeps getting pushed forward as long as traffic continues, so it never actually rolls over on schedule — a materially different (much stricter) behavior than the stated fixed-window semantics. | Set `EXPIRE` only when `INCR` returns `1` (the request that creates the window). | [Redis Documentation — INCR command, "Pattern: rate limiter"](https://redis.io/docs/latest/commands/incr/) (this file's fix is exactly the documented "rate limiter 2" pattern) | **Fixed** |

Full read of all 30 questions. Cache-aside/write-through/write-behind (Q2), the update-then-delete-cache race (Q4–5), stampede prevention (Q6), eviction policies (Q11), hot keys (Q12–13), replication/Sentinel/Cluster consistency (Q15–17), distributed locks (Q18–19), and Redis transaction/pipeline semantics (Q23–24) checked against Redis documentation — no other Critical/Major findings.

**Guide status: Reviewed. 30/30 questions reviewed, version-baseline header present. TOC not yet added — see Phase 3/4 backlog.**

### System Design/Transactions_Interview_Prep.md

Isolation levels and their PostgreSQL-specific behavior (Q2–3), MVCC (Q4), Spring propagation defaults and the shared-rollback implication of `REQUIRED` (Q5–6), proxy-based self-invocation and private-method limitations (Q8–9, consistent with the Spring Boot Internals guide's Q24/26 fix, formerly Q12/14 before its 2026-08-23 Basic/Intermediate renumbering), default rollback-on-unchecked-only behavior (Q10), deadlocks (Q13), optimistic/pessimistic concurrency (Q14–15), the outbox pattern (Q19), and 2PC-vs-saga trade-offs (Q22–23, correctly hedged — "2PC isn't *never* used," not an absolute) were all checked against PostgreSQL documentation, the Spring Framework reference, and the cited papers/pattern sources. No Critical/Major findings in this pass.

**Guide status: Reviewed. Spot-checked in depth (isolation levels, propagation, self-invocation/private-method proxy behavior, rollback rules, 2PC/saga) with no findings; not every one of the 30 questions was individually re-verified line-by-line in this pass the way the other 14 guides were — treat as a strong but slightly lighter pass than the rest of the repo. Version-baseline header present. TOC not yet added — see Phase 3/4 backlog.**

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

## Guide review status

| Guide | Status |
|---|---|
| Computer Science Fundamentals/Computer_Science_Fundamentals_Interview_Prep.md | Reviewed |
| Language/Java_Collections_Interview_Prep.md | Reviewed |
| Language/Java_Concurrency_Interview_Prep.md | Reviewed |
| Language/Java_JVM_GC_Interview_Prep.md | Reviewed |
| Frameworks/Spring_Boot_Internals_Interview_Prep.md | Reviewed |
| Frameworks/Spring_Security_OAuth2_Interview_Prep.md | Reviewed — no correctness findings |
| Frameworks/JPA_Hibernate_Interview_Prep.md | Reviewed |
| System Design/REST_API_Design_Interview_Prep.md | Reviewed |
| System Design/Cross_Stack_Design_Scenarios_Interview_Prep.md | Reviewed |
| Microservices & Architecture Patterns/Microservices_Architecture_Patterns_Interview_Prep.md | Reviewed — no blocking findings |
| Kubernetes, Docker & Cloud/Kubernetes_Docker_Interview_Prep.md | Reviewed |
| AI Engineering/AI_Engineering_Interview_Prep.md | Reviewed |
| Tech Leadership/Engineering_Leadership_Interview_Prep.md | Reviewed |
| System Design/Kafka_Interview_Prep.md | Reviewed |
| System Design/Redis_Caching_Interview_Prep.md | Reviewed |
| System Design/Transactions_Interview_Prep.md | Reviewed (spot-checked in depth; see note above) |

"Reviewed" means: audited against the Phase 1 checklist and this repository's known-issues list, with all Critical/Major findings from that pass fixed. It does **not** mean every question has been rewritten into the full Phase 2 six-part standardized structure (Question / Short answer / Deep dive / Example / Failure modes / Follow-ups / Sources) — the existing Answer/Code/Follow-up/Source structure was judged accurate and well-organized enough that a wholesale rewrite risked introducing errors for uncertain benefit, and was deliberately not attempted in this pass (see backlog).

## Phase 3/4 backlog (not yet done)

- Table of contents on the Kafka, Redis, and Transactions guides (the other 12 have one).
- **Answer-length restructuring rollout.** Java_Collections (2026-08-22, pilot) and System Design/REST_API_Design (2026-08-22) have been migrated to a five-part Core answer / Staff-level extension / Example / Follow-up questions / Sources structure, fixing the repo-wide answer-length problem (original median 234 words against a 30–90-second/~100-180-word target) for those two guides — see each guide's own "Guide status" note above. 13 guides remain — roughly 370 more questions — still on the original Answer/Code/Follow-up/Source shape and still running long. Continuing the rollout guide-by-guide is fine to proceed with incrementally; the README's "How each question is structured" section still describes the old four-part shape, since it's accurate for 13 of 15 guides — update it once rollout covers all (or the repository owner decides to stop partway), to avoid the same overstatement-of-uniformity problem this pass was fixing elsewhere.
- Full Phase 2 rewrite of every question into the six-part standardized structure (Question / Short answer / Deep dive / Example / Failure modes / Follow-ups / Sources) — a different, more elaborate structure than the five-part answer-length restructuring above. This repository contains 514 numbered questions across 16 guides as of 2026-08-23 (413 across the original 15 guides at the original audit, +13 from Java Concurrency's, +12 each from Java Collections', Java JVM & GC's, Spring Boot Internals', Spring Security & OAuth2's, and JPA & Hibernate's Basic/Intermediate graduations, +28 from the new Computer Science Fundamentals guide (15 at creation, +13 same-day expansion) — counted programmatically; see the per-guide counts in each guide's own "Guide status" line above). All six graduated guides now span Basic → Staff internally, matching the Kubernetes/Docker guide's original graduated design; Computer Science Fundamentals is Basic-only by design and doesn't graduate to Staff. This was not attempted; Phase 1 (accuracy) and the explicitly listed known issues were prioritized per the task's own instruction not to proceed to content restructuring before the audit is complete. This is a genuinely large, separate scope decision the repository owner should make deliberately rather than have it happen as a side effect of an accuracy pass.
- Extracting Java/SQL examples into standalone, CI-testable sample projects (Phase 3, "where practical"). Not attempted — would need per-example scaffolding (Maven/Gradle module, test harness) and is a substantial project of its own.
- Licensing — deliberately not chosen; needs the repository owner's decision (see `CONTRIBUTING.md`).
- Java_Collections Q22 (was Q10) vs. Java_JVM_GC Q24 (was Q12) heap-dump question redundancy — flagged, not consolidated (both are independently accurate; low priority).
