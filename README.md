# Interview Preparation Kit

*Deep-dive, mid-to-staff-level interview prep — written to be said out loud, not skimmed.*

[![Docs check](https://github.com/uditsharma14/Interview-Preparation-kit/actions/workflows/docs-check.yml/badge.svg)](https://github.com/uditsharma14/Interview-Preparation-kit/actions/workflows/docs-check.yml) — every push and PR runs markdown linting, internal-link/anchor validation, and external-citation link-checking automatically ([`.github/workflows/docs-check.yml`](.github/workflows/docs-check.yml)); a monthly scheduled run catches link rot that happens independent of any edit.

Most interview prep falls into one of two failure modes: too shallow (a one-line flashcard answer that falls apart the moment an interviewer asks "why," or "what breaks at scale"), or too scattered (a folder of half-finished notes, bookmarked blog posts, and old Stack Overflow tabs with no coherent throughline). This kit tries to be neither — **17 in-depth guides, 530+ Q&A entries, and a 200-term glossary**, each guide written as a set of Q&A pairs: the answer phrased the way it would actually be said out loud in an interview, backed by a code snippet, and a pointer to where staff-level follow-up questions tend to go. Several of the language/framework guides are explicitly graduated from Basic through Staff, so the same guide works whether you're building the fundamentals for the first time or refreshing the deep end the night before a Staff-level loop.

This repository optimizes for **accuracy over question count**. Every guide has undergone an initial audit against primary sources — Oracle/OpenJDK specs, Spring/Hibernate/Kafka/Redis/Kubernetes documentation, IETF RFCs. See [`AUDIT.md`](AUDIT.md) for the review status of each guide and every finding (fixed or still open), and [`CONTRIBUTING.md`](CONTRIBUTING.md) for the citation/accuracy policy new material has to meet. Version-sensitive and production-specific claims should still be verified against the linked documentation before you repeat them in an interview — and if you find one that's wrong or stale, that's exactly what `AUDIT.md` and the contribution policy exist to fix.

## Contents

- [Who this is for](#who-this-is-for)
- [Recommended study order](#recommended-study-order)
- [Difficulty by guide](#difficulty-by-guide)
- [Quick-revision path](#quick-revision-path)
- [Deep-dive path](#deep-dive-path)
- [Guides by topic](#guides-by-topic)
- [How each question is structured](#how-each-question-is-structured)
- [Accuracy and contribution policy](#accuracy-and-contribution-policy)
- [License](#license)

## Who this is for

Current interview loops for **Full Stack**, **Forward Deployed**, and **Staff** engineering roles overlap a lot but weight things differently — these three are the loops this kit was actually built against, chosen because they cover the widest realistic spread (a Full Stack loop leans toward breadth and applied fundamentals, a Forward Deployed loop leans toward ambiguity and delivery under real-world constraints, and a Staff loop leans toward depth and architectural judgment). Here's what's covered today versus still a gap, per role, so you know where to spend time:

| Role | What their loop leans on | Covered here | Still a gap |
|---|---|---|---|
| **Full Stack Engineer** | Frontend fundamentals (React/TS, browser/perf) • Backend API design • Databases • Light system design • Testing | [Frameworks](Frameworks/) • [System Design](System%20Design/) (esp. [REST API Design](System%20Design/REST_API_Design_Interview_Prep.md)) • [Language](Language/) | [Frontend & Full-Stack](Frontend%20%26%20Full-Stack/) *(reserved)* |
| **Forward Deployed Engineer** | Rapid prototyping across the stack • Scripting/data wrangling • Ambiguous requirements, messy environments • Stakeholder communication • Deploying into a customer's locked-down infrastructure • Increasingly, LLM/agent integration on client data | [System Design](System%20Design/) (esp. [Cross-Stack Scenarios](System%20Design/Cross_Stack_Design_Scenarios_Interview_Prep.md)) • [Tech Leadership](Tech%20Leadership/) (ambiguity, influence) • [AI Engineering](AI%20Engineering/) • [Kubernetes, Docker & Cloud](Kubernetes%2C%20Docker%20%26%20Cloud/) | [Forward-Deployed & Customer-Facing Engineering](Forward-Deployed%20%26%20Customer-Facing%20Engineering/) *(reserved)* |
| **Staff Engineer** | Deep fundamentals across the stack • System design and trade-offs • Architecture/design judgment • Organizational leverage and leadership | Nearly everything — [Language](Language/) • [Frameworks](Frameworks/) • [System Design](System%20Design/) • [Tech Leadership](Tech%20Leadership/) • [Microservices & Architecture Patterns](Microservices%20%26%20Architecture%20Patterns/) • [Kubernetes, Docker & Cloud](Kubernetes%2C%20Docker%20%26%20Cloud/) | [Design Patterns](Design%20Patterns/) *(reserved)* |

*(reserved = see that folder's own README)*

AI/LLM-application questions have become common across all three loops in the last year or two — even a straightforward backend or full-stack interview now often includes "how would you design a RAG pipeline" or "how do you evaluate an LLM feature." That's why **AI Engineering** is reserved as its own section rather than folded into System Design.

## Recommended study order

The guides build on each other — each one's header states its own prerequisites, but if you're going through the whole kit rather than a single topic, this order minimizes backtracking:

0. **[Computer Science Fundamentals](Computer%20Science%20Fundamentals/Computer_Science_Fundamentals_Interview_Prep.md)** — genuinely optional if HTTP, TCP/UDP, DNS, encryption, and Big-O are already second nature; every other guide assumes this vocabulary without re-explaining it, so it's the right place to start if any of those terms aren't fully solid.
1. **[Java Collections](Language/Java_Collections_Interview_Prep.md) → [Java Concurrency](Language/Java_Concurrency_Interview_Prep.md) → [Java JVM & GC](Language/Java_JVM_GC_Interview_Prep.md)** — language fundamentals everything else assumes.
2. **[Spring Boot Internals](Frameworks/Spring_Boot_Internals_Interview_Prep.md) → [Spring Security & OAuth2](Frameworks/Spring_Security_OAuth2_Interview_Prep.md) → [JPA & Hibernate](Frameworks/JPA_Hibernate_Interview_Prep.md)** — the framework layer most of the code examples elsewhere in the kit use.
3. **[Software Testing](Testing/Software_Testing_Interview_Prep.md)** — assumes Spring Boot Internals (and JPA & Hibernate for the `@DataJpaTest`/Testcontainers questions); read right after the Frameworks guides while `@SpringBootTest`/`@WebMvcTest` context is fresh.
4. **[Transactions](System%20Design/Transactions_Interview_Prep.md) → [Kafka](System%20Design/Kafka_Interview_Prep.md) → [Redis & Caching](System%20Design/Redis_Caching_Interview_Prep.md) → [REST API Design](System%20Design/REST_API_Design_Interview_Prep.md)** — Transactions first: its dual-write-problem and outbox-pattern framing gets reused directly by the Kafka and Redis guides.
5. **[Microservices & Architecture Patterns](Microservices%20%26%20Architecture%20Patterns/Microservices_Architecture_Patterns_Interview_Prep.md)** — assumes the Transactions (sagas, 2PC), REST API Design, and Redis/Kafka guides above.
6. **[Cross-Stack Design Scenarios](System%20Design/Cross_Stack_Design_Scenarios_Interview_Prep.md)** — deliberately last among the technical guides; every scenario draws on several of the guides above at once, the way a real Staff-level system-design round actually does.
7. **[Kubernetes, Docker & Cloud](Kubernetes%2C%20Docker%20%26%20Cloud/Kubernetes_Docker_Interview_Prep.md)** — mostly independent of the above; can be read any time, and is itself graduated Basic → Staff internally.
8. **[AI Engineering](AI%20Engineering/AI_Engineering_Interview_Prep.md)** — assumes general backend engineering (steps 1–5); cross-references the REST API Design, Redis, and Transactions guides for patterns (retries, idempotency, caching) that apply directly to LLM-backed systems.
9. **[Tech Leadership](Tech%20Leadership/Engineering_Leadership_Interview_Prep.md)** — not technology-specific, but most useful last: the judgment questions here often draw on the technical material above for concrete grounding.

## Difficulty by guide

| Guide | Level | Notes |
|---|---|---|
| [Computer Science Fundamentals](Computer%20Science%20Fundamentals/Computer_Science_Fundamentals_Interview_Prep.md) | **Basic (only)** | No Staff tier — this guide deliberately stays foundational (HTTP, TCP/UDP, DNS, encryption, Big-O) and points into the other guides for depth on each topic. |
| [Java Collections](Language/Java_Collections_Interview_Prep.md) | **Basic → Staff** | Explicitly graduated internally: Basic → Intermediate → Staff. The Intermediate section onward assumes `equals()`/`hashCode()` basics; escalates to production leak diagnosis. |
| [Java Concurrency](Language/Java_Concurrency_Interview_Prep.md) | **Basic → Staff** | Explicitly graduated internally: Basic → Intermediate → Staff. The Intermediate section onward assumes Collections. |
| [Java JVM & GC](Language/Java_JVM_GC_Interview_Prep.md) | **Basic → Staff** | Explicitly graduated internally: Basic → Intermediate → Staff. The Staff-level section assumes Collections and Concurrency for some parts. |
| [Spring Boot Internals](Frameworks/Spring_Boot_Internals_Interview_Prep.md) | **Basic → Staff** | Explicitly graduated internally: Basic → Intermediate → Staff. The Intermediate section onward assumes the Basic section's `@Component`/`@Autowired` familiarity. |
| [Spring Security & OAuth2](Frameworks/Spring_Security_OAuth2_Interview_Prep.md) | **Basic → Staff** | Explicitly graduated internally: Basic → Intermediate → Staff. Assumes Spring Boot Internals for the Basic section. |
| [JPA & Hibernate](Frameworks/JPA_Hibernate_Interview_Prep.md) | **Basic → Staff** | Explicitly graduated internally: Basic → Intermediate → Staff. Assumes Spring Boot Internals and basic SQL for the Basic section. |
| [Software Testing](Testing/Software_Testing_Interview_Prep.md) | **Basic → Staff** | Explicitly graduated internally: Basic → Intermediate → Staff (scenario-based). Assumes Spring Boot Internals; the Intermediate/Staff sections lean on JPA & Hibernate for the `@DataJpaTest`/Testcontainers questions. |
| [Transactions](System%20Design/Transactions_Interview_Prep.md) | Staff | Assumes basic SQL. |
| [Kafka](System%20Design/Kafka_Interview_Prep.md) | Staff | Assumes basic messaging/pub-sub concepts. |
| [Redis & Caching](System%20Design/Redis_Caching_Interview_Prep.md) | Staff | Assumes basic Redis commands. |
| [REST API Design](System%20Design/REST_API_Design_Interview_Prep.md) | Staff | Assumes basic HTTP. |
| [Microservices & Architecture Patterns](Microservices%20%26%20Architecture%20Patterns/Microservices_Architecture_Patterns_Interview_Prep.md) | Staff | Assumes Transactions, REST API Design, Redis, Kafka. |
| [Cross-Stack Design Scenarios](System%20Design/Cross_Stack_Design_Scenarios_Interview_Prep.md) | Staff | Assumes the rest of the technical guides — deliberately cross-cutting. |
| [Kubernetes, Docker & Cloud](Kubernetes%2C%20Docker%20%26%20Cloud/Kubernetes_Docker_Interview_Prep.md) | **Beginner → Staff** | Explicitly graduated internally: Docker Basic → Staff, then Kubernetes Basic → Staff. |
| [AI Engineering](AI%20Engineering/AI_Engineering_Interview_Prep.md) | Staff | Assumes general backend engineering; fastest-moving guide in the repo — check its "last verified" date. |
| [Tech Leadership](Tech%20Leadership/Engineering_Leadership_Interview_Prep.md) | Staff | Not technology-specific; no technical prerequisite, but most useful after the technical guides. |

Most of this kit is genuinely Staff-scoped by design — see [Who this is for](#who-this-is-for) above for where the *entry points* (Computer Science Fundamentals in full; the Basic tiers of Java Collections, Java Concurrency, Java JVM & GC, Spring Boot Internals, Spring Security & OAuth2, JPA & Hibernate, and Software Testing; Kubernetes' Basic tier) are more accessible.

## Quick-revision path

Interview tomorrow, not weeks from now? Don't read every guide front to back:

1. For each guide you need, read only the **bolded Answer paragraph** of each question — skip Code and Follow-up on a first pass. That's the "can I say this out loud correctly" layer.
2. Come back for **Follow-up** sections specifically on the questions closest to what you expect to be asked. That's the "can I go one level deeper when probed" layer — worth targeted review rather than exhaustive re-reading under time pressure.

Highest-yield guides for a generalist Staff/Lead loop, in priority order if you have to cut scope: [Java Concurrency](Language/Java_Concurrency_Interview_Prep.md), [Transactions](System%20Design/Transactions_Interview_Prep.md), [Kafka](System%20Design/Kafka_Interview_Prep.md), [Redis & Caching](System%20Design/Redis_Caching_Interview_Prep.md), [Spring Boot Internals](Frameworks/Spring_Boot_Internals_Interview_Prep.md), [Cross-Stack Design Scenarios](System%20Design/Cross_Stack_Design_Scenarios_Interview_Prep.md) — these show up across the widest range of loop types.

## Deep-dive path

Weeks of runway, not days? Go in the [recommended study order](#recommended-study-order) above, guide by guide, and for each question:

1. Read the Answer.
2. Work through the Code example by hand — actually run it where it's real compilable code, not pseudocode.
3. Read the cited primary source rather than trusting the guide's paraphrase of it. The source is there precisely so you don't have to take the paraphrase on faith.
4. Use the Follow-up section as a self-check: cover it, answer the question yourself, then compare.

## Guides by topic

Organized by kind of content, not by role — use the tables above to figure out which folders and difficulty levels matter most for the loop you're prepping for.

### Computer Science Fundamentals

Networking, HTTP, encryption, and general CS/software terminology — Basic-only, no framework or language involved. The foundational layer every other guide assumes without re-explaining it.

- **[Computer Science Fundamentals Interview Prep](Computer%20Science%20Fundamentals/Computer_Science_Fundamentals_Interview_Prep.md)** — Networking (TCP vs. UDP, DNS, IP/ports, URI/URL/URN), HTTP (statelessness, HTTP/1.1 vs. 2 vs. 3, status codes, headers vs. body), encryption/security (symmetric vs. asymmetric, hashing, TLS handshake, certificates/CAs), data structures & algorithms (stack/queue, tree vs. graph, recursion, Big-O), programming languages & OOP (the four pillars, compiled vs. interpreted, static vs. dynamic typing), operating systems (kernel, virtual memory/paging, CPU caching), databases (SQL vs. NoSQL, normalization, indexes), and software engineering practices (version control, unit/integration/E2E testing).
- **[Computer Science Glossary](Computer%20Science%20Fundamentals/Computer_Science_Glossary.md)** — a fast, 2–3-line-per-term reference covering 200 core CS/software-engineering terms (a full CS-degree-style vocabulary sweep), grouped by theme rather than alphabetically. Not a substitute for the interview-answer guides — it's the "what does this word mean" layer beneath them, with pointers into the guides that cover any given term in real depth.

### Language

Pure Java runtime/language topics — no framework involved.

- **[Java Collections Interview Prep](Language/Java_Collections_Interview_Prep.md)** — Graduated Basic → Staff: core interfaces, `equals()`/`hashCode()`, and `Comparable`/`Comparator` basics through `HashMap`/`TreeMap`/`LinkedHashMap` internals, concurrent collections, boxed-collection costs, and production leak diagnosis.
- **[Java Concurrency Interview Prep](Language/Java_Concurrency_Interview_Prep.md)** — Graduated Basic → Staff: threads, `synchronized`, and deadlock basics through `ExecutorService`/coordination primitives to visibility/atomicity/ordering, lock comparisons, virtual threads, `ForkJoinPool`, the ABA problem, and structured concurrency.
- **[Java JVM & GC Interview Prep](Language/Java_JVM_GC_Interview_Prep.md)** — Graduated Basic → Staff: JVM/JDK/JRE, stack vs. heap, GC basics, and generational-heap fundamentals through memory areas, JIT/escape analysis, reference types, G1/ZGC/Shenandoah, container OOM-kills, and native memory.

### Frameworks

Spring and JPA/Hibernate — how the framework itself works under the hood.

- **[Spring Boot Internals Interview Prep](Frameworks/Spring_Boot_Internals_Interview_Prep.md)** — Graduated Basic → Staff: DI/IoC and bean basics, stereotype annotations, and Spring Boot vs. Framework through `SpringApplication.run()` internals, bean lifecycle, auto-configuration, AOP proxies and self-invocation, graceful shutdown, and execution models.
- **[Spring Security & OAuth2 Interview Prep](Frameworks/Spring_Security_OAuth2_Interview_Prep.md)** — Graduated Basic → Staff: `UserDetailsService`, password hashing, RBAC, and JWT structure basics through filter chain architecture, CSRF/CORS, OAuth2 flows and PKCE, JWT validation and key rotation, token storage, BOLA, and multi-tenant authorization.
- **[JPA & Hibernate Interview Prep](Frameworks/JPA_Hibernate_Interview_Prep.md)** — Graduated Basic → Staff: ORM/JPA/Hibernate basics, entity/repository fundamentals, and relationship annotations through entity lifecycle, dirty checking and flushing, N+1 diagnosis and fixes, fetch strategies, optimistic/pessimistic locking, ID generation and batching, and DTO boundaries.

### Testing

Testing-framework mechanics and scenario-based testing strategy, organized as its own graduated guide rather than folded into the Frameworks section.

- **[Software Testing Interview Prep](Testing/Software_Testing_Interview_Prep.md)** — Graduated Basic → Staff: JUnit annotations, assertions, the AAA pattern, and mock/stub/spy basics through `@ParameterizedTest`, `@SpringBootTest`/`@WebMvcTest`/`@DataJpaTest`, `MockMvc`, and Testcontainers, to Staff-level scenario-based questions — testing an external payment gateway, `@Async`/scheduled tasks, Kafka producers/consumers, diagnosing flaky tests, time-dependent code, and structuring test suites in CI.

### System Design

Architecture, distributed-systems trade-offs, and cross-service concerns.

- **[Kafka Deep-Dive Interview Prep](System%20Design/Kafka_Interview_Prep.md)** — Topics, partitions, offsets, ordering guarantees, message keys, and consumer group rebalancing.
- **[REST API Design Interview Prep](System%20Design/REST_API_Design_Interview_Prep.md)** — Resource modeling, idempotency and retries, pagination strategies, versioning and backward compatibility, error formats, async workflows, and rate limiting.
- **[Transactions Interview Prep](System%20Design/Transactions_Interview_Prep.md)** — ACID and isolation levels, MVCC, Spring propagation types, deadlocks, the transactional outbox pattern, sagas vs. two-phase commit, and zero-downtime schema migration.
- **[Redis & Caching Interview Prep](System%20Design/Redis_Caching_Interview_Prep.md)** — Caching strategies, stampedes/penetration/pollution, eviction policies, hot keys, replication/Sentinel/Cluster, distributed locks and fencing tokens, rate limiting, and cache-deployment versioning.
- **[Cross-Stack Design Scenarios Interview Prep](System%20Design/Cross_Stack_Design_Scenarios_Interview_Prep.md)** — 20 end-to-end scenarios spanning Spring Boot, PostgreSQL, Redis, and Kafka: order platforms, multi-region trade-offs, zero-downtime deployments, incident diagnosis, service-boundary evaluation, and SLOs.
- **[System Design Interview Question Bank](System%20Design/System_Design_Interview_Question_Bank.md)** — a practice-prompt list (not full worked answers) spanning core system design, distributed transactions/payments, event-driven architecture, data-intensive systems, AI/Forward-Deployed scenarios, and the follow-up questions a Principal-level interviewer presses on.

### Tech Leadership

Lead/Staff-level judgment, influence, and organizational impact — not technology-specific.

- **[Lead/Staff Engineering & Technical Leadership Interview Prep](Tech%20Leadership/Engineering_Leadership_Interview_Prep.md)** — Architectural decision-making, influence without authority, platform standards, incident leadership, technical strategy, and what Staff-level impact looks like beyond code.

### AI Engineering

- **[AI Engineering Interview Prep](AI%20Engineering/AI_Engineering_Interview_Prep.md)** — Hosted vs. self-hosted models, prompting vs. fine-tuning vs. RAG, chunking and hybrid search, agent/tool-calling design and guardrails, LLM-as-judge, hallucination mitigation, prompt injection, and cost/latency management in production.

### Microservices & Architecture Patterns

- **[Microservices & Architecture Patterns Interview Prep](Microservices%20%26%20Architecture%20Patterns/Microservices_Architecture_Patterns_Interview_Prep.md)** — Service decomposition and bounded contexts, strangler fig migration, API Gateway/BFF/sidecar/service mesh, CQRS and event sourcing, CAP theorem, hexagonal/clean architecture, contract testing, and the distributed monolith.

### Design Patterns

*(reserved — classic GoF patterns and modern applications of them in real codebases. See [that folder's README](Design%20Patterns/README.md).)*

### Kubernetes, Docker & Cloud

- **[Docker & Kubernetes Interview Prep](Kubernetes%2C%20Docker%20%26%20Cloud/Kubernetes_Docker_Interview_Prep.md)** — Basic through Staff level: containers vs. VMs, image layers and multi-stage builds, namespaces/cgroups, Pods/Deployments/Services/Ingress, probes, scheduling, StatefulSets, multi-tenancy, etcd, zero-downtime rollouts, cluster security, and service mesh vs. native Kubernetes.

### Frontend & Full-Stack

*(reserved — React/TypeScript fundamentals, browser/rendering performance, state management, and full-stack API integration concerns — the main gap for Full Stack Engineer loops. See [that folder's README](Frontend%20%26%20Full-Stack/README.md).)*

### Forward-Deployed & Customer-Facing Engineering

*(reserved — rapid prototyping under ambiguity, scripting and data wrangling against messy client data/systems, integrating with a customer's existing infrastructure, and the specific communication/expectation-setting skills these roles are actually screened on. See [that folder's README](Forward-Deployed%20%26%20Customer-Facing%20Engineering/README.md).)*

### Further Reading

External articles, videos, and engineering-blog write-ups — not this repo's own Q&A guides, and not held to the same primary-source citation bar (see the note at the top of the list itself).

- **[System Design & AI Engineering Reading List](Further%20Reading/System_Design_and_AI_Reading_List.md)** — System design deep-dive articles, 26 classic system-design write-ups by category (rate limiters, key-value stores, chat systems, payments, and more), AI agent video courses, AI engineering core concepts, real-world system design case studies from 16 companies' engineering blogs, and 20 foundational system design concepts.

## How each question is structured

Every question in every guide follows the same shape — deliberately, so once you're used to the pattern in one guide, every other guide reads the same way:

1. **Answer** — a conversational, interview-ready explanation, phrased the way it would actually be said out loud, roughly 30–90 seconds if spoken. This is the part you should be able to recite cold.
2. **Code** — a snippet, config, SQL, sketch, or decision framework/template to back the explanation up (compilable code where practical; clearly labeled pseudocode/conceptual where not). Useful both as a whiteboard prop and as a way to sanity-check that the Answer's claims actually hold up in real code.
3. **Follow-up** — the deeper probe that separates a mid-level answer from a Staff-level one: failure modes, trade-offs, what breaks at scale. This is where an interviewer's "okay, but what if..." actually goes, so it's worth reading even for questions you already feel solid on.
4. **Source** — the authoritative reference(s) for the important claims made in that question, so you're never just trusting this kit's paraphrase.

A rollout to a more granular five-part structure (Core answer / Staff-level extension / Example / Follow-up questions / Sources — same underlying content, but with the deeper trade-off material explicitly pulled out of the core spoken answer rather than folded into one long paragraph) is in progress guide by guide — see [`AUDIT.md`](AUDIT.md) for which guides have migrated so far and which still use the four-part shape above.

## Accuracy and contribution policy

This kit is deliberately not optimizing for question count. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full policy — in short: primary sources over memory, version-scoped claims, no unscoped "always"/"never"/"guaranteed"/"exactly once," no fabricated production experience, and no AI-conversation artifacts. [`AUDIT.md`](AUDIT.md) tracks the review status of every guide and every known issue found so far, fixed or still open.

## License

Not yet chosen — see the note in `CONTRIBUTING.md`. Treat all content here as all-rights-reserved until the repository owner adds a license file.

Recommended options for the owner to choose from (not chosen on the owner's behalf):

| Option | Terms | Fits if |
|---|---|---|
| **CC BY-NC-SA 4.0** | Share/adapt with attribution, non-commercial only, share-alike | A personal study resource the owner wants circulated but not resold or repackaged commercially |
| **CC BY-SA 4.0** | Same, minus the non-commercial restriction | The owner is fine with commercial reuse (e.g. a bootcamp using it in paid material) as long as it stays attributed and share-alike |
| **MIT / Apache-2.0** | Permissive, no share-alike requirement, minimal restriction | The owner wants maximum reuse with no obligation on downstream users beyond attribution (Apache-2.0 also adds an explicit patent grant, irrelevant for prose/docs but standard for code-heavy repos) |
| **All-rights-reserved** (no license file) | The current default | The owner doesn't want redistribution at all right now |
