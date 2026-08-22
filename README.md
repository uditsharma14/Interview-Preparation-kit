# Interview Preparation Kit

A collection of deep-dive, mid-to-staff-level interview prep notes for technical interviews. Each topic is written as a set of Q&A entries with the answer phrased the way it would actually be said out loud in an interview, backed by code snippets and pointers to where staff-level follow-up questions tend to go.

This repository optimizes for **accuracy over question count**. Every guide has been through an audit pass against primary sources (Oracle/OpenJDK specs, Spring/Hibernate/Kafka/Redis/Kubernetes documentation, IETF RFCs) — see [`AUDIT.md`](AUDIT.md) for the verification status of each guide and [`CONTRIBUTING.md`](CONTRIBUTING.md) for the citation/accuracy policy new material has to meet. If you're prepping for an interview, that means you can trust a claim here enough to repeat it in the room — and if you find one that's wrong or stale, that's exactly what `AUDIT.md` and the contribution policy exist to fix.

## Who This Is For

Current interview loops for **Full Stack**, **Forward Deployed**, and **Staff** engineering roles overlap a lot but weight things differently. Here's what's actually covered today versus still a gap, per role, so you know where to spend time:

| Role | What their loop usually leans on | Covered here | Still a gap |
|---|---|---|---|
| **Full Stack Engineer** | Frontend fundamentals (React/TS, browser/perf), backend API design, databases, light system design, testing | [Frameworks](Frameworks/), [System Design](System%20Design/) (esp. [REST API Design](System%20Design/REST_API_Design_Interview_Prep.md)), [Language](Language/) | [Frontend & Full-Stack](Frontend%20%26%20Full-Stack/) *(reserved — see that folder's README)* |
| **Forward Deployed Engineer** | Rapid prototyping across the stack, scripting/data wrangling, working with ambiguous client requirements and messy environments, stakeholder communication, deploying into a customer's own (often locked-down) infrastructure, increasingly LLM/agent integration on top of client data | [System Design](System%20Design/) (esp. [Cross-Stack Scenarios](System%20Design/Cross_Stack_Design_Scenarios_Interview_Prep.md)), [Tech Leadership](Tech%20Leadership/) (ambiguity, influence, communication), [AI Engineering](AI%20Engineering/), [Kubernetes, Docker & Cloud](Kubernetes%2C%20Docker%20%26%20Cloud/) | [Forward-Deployed & Customer-Facing Engineering](Forward-Deployed%20%26%20Customer-Facing%20Engineering/) *(reserved — see that folder's README)* |
| **Staff Engineer** | Deep fundamentals across the stack, system design and trade-offs, architecture/design judgment, organizational leverage and leadership | Nearly everything — [Language](Language/), [Frameworks](Frameworks/), [System Design](System%20Design/), [Tech Leadership](Tech%20Leadership/), [Microservices & Architecture Patterns](Microservices%20%26%20Architecture%20Patterns/), [Kubernetes, Docker & Cloud](Kubernetes%2C%20Docker%20%26%20Cloud/) | [Design Patterns](Design%20Patterns/) *(reserved — see that folder's README)* |

AI/LLM-application questions have become common across all three loops in the last year or two — even a straightforward backend or full-stack interview now often includes "how would you design a RAG pipeline" or "how do you evaluate an LLM feature" — which is why **AI Engineering** is reserved as its own section rather than folded into System Design.

## Recommended study order

The guides build on each other — each one's header states its own prerequisites, but if you're going through the whole kit rather than a single topic, this order minimizes backtracking:

1. **[Java Collections](Language/Java_Collections_Interview_Prep.md) → [Java Concurrency](Language/Java_Concurrency_Interview_Prep.md) → [Java JVM & GC](Language/Java_JVM_GC_Interview_Prep.md)** — language fundamentals everything else assumes.
2. **[Spring Boot Internals](Frameworks/Spring_Boot_Internals_Interview_Prep.md) → [Spring Security & OAuth2](Frameworks/Spring_Security_OAuth2_Interview_Prep.md) → [JPA & Hibernate](Frameworks/JPA_Hibernate_Interview_Prep.md)** — the framework layer most of the code examples elsewhere in the kit use.
3. **[Transactions](System%20Design/Transactions_Interview_Prep.md) → [Kafka](System%20Design/Kafka_Interview_Prep.md) → [Redis & Caching](System%20Design/Redis_Caching_Interview_Prep.md) → [REST API Design](System%20Design/REST_API_Design_Interview_Prep.md)** — Transactions first: its dual-write-problem and outbox-pattern framing gets reused directly by the Kafka and Redis guides.
4. **[Microservices & Architecture Patterns](Microservices%20%26%20Architecture%20Patterns/Microservices_Architecture_Patterns_Interview_Prep.md)** — assumes the Transactions (sagas, 2PC), REST API Design, and Redis/Kafka guides above.
5. **[Cross-Stack Design Scenarios](System%20Design/Cross_Stack_Design_Scenarios_Interview_Prep.md)** — deliberately last among the technical guides; every scenario draws on several of the guides above at once, the way a real Staff-level system-design round actually does.
6. **[Kubernetes, Docker & Cloud](Kubernetes%2C%20Docker%20%26%20Cloud/Kubernetes_Docker_Interview_Prep.md)** — mostly independent of the above; can be read any time, and is itself graduated Basic → Staff internally.
7. **[AI Engineering](AI%20Engineering/AI_Engineering_Interview_Prep.md)** — assumes general backend engineering (steps 1–4); cross-references the REST API Design, Redis, and Transactions guides for patterns (retries, idempotency, caching) that apply directly to LLM-backed systems.
8. **[Tech Leadership](Tech%20Leadership/Engineering_Leadership_Interview_Prep.md)** — not technology-specific, but most useful last: the judgment questions here often draw on the technical material above for concrete grounding.

## Difficulty by guide

| Guide | Level | Notes |
|---|---|---|
| [Java Collections](Language/Java_Collections_Interview_Prep.md) | Senior → Staff | Starts at core-Java fundamentals, escalates to production leak diagnosis. |
| [Java Concurrency](Language/Java_Concurrency_Interview_Prep.md) | Staff | Assumes Collections. |
| [Java JVM & GC](Language/Java_JVM_GC_Interview_Prep.md) | Staff | Assumes Collections and Concurrency for some sections. |
| [Spring Boot Internals](Frameworks/Spring_Boot_Internals_Interview_Prep.md) | Staff | Assumes basic Spring (`@Component`/`@Autowired`). |
| [Spring Security & OAuth2](Frameworks/Spring_Security_OAuth2_Interview_Prep.md) | Staff | Assumes Spring Boot Internals. |
| [JPA & Hibernate](Frameworks/JPA_Hibernate_Interview_Prep.md) | Staff | Assumes Spring Boot Internals, basic SQL. |
| [Transactions](System%20Design/Transactions_Interview_Prep.md) | Staff | Assumes basic SQL. |
| [Kafka](System%20Design/Kafka_Interview_Prep.md) | Staff | Assumes basic messaging/pub-sub concepts. |
| [Redis & Caching](System%20Design/Redis_Caching_Interview_Prep.md) | Staff | Assumes basic Redis commands. |
| [REST API Design](System%20Design/REST_API_Design_Interview_Prep.md) | Staff | Assumes basic HTTP. |
| [Microservices & Architecture Patterns](Microservices%20%26%20Architecture%20Patterns/Microservices_Architecture_Patterns_Interview_Prep.md) | Staff | Assumes Transactions, REST API Design, Redis, Kafka. |
| [Cross-Stack Design Scenarios](System%20Design/Cross_Stack_Design_Scenarios_Interview_Prep.md) | Staff | Assumes the rest of the technical guides — deliberately cross-cutting. |
| [Kubernetes, Docker & Cloud](Kubernetes%2C%20Docker%20%26%20Cloud/Kubernetes_Docker_Interview_Prep.md) | **Beginner → Staff** | Explicitly graduated internally: Docker Basic → Staff, then Kubernetes Basic → Staff. |
| [AI Engineering](AI%20Engineering/AI_Engineering_Interview_Prep.md) | Staff | Assumes general backend engineering; fastest-moving guide in the repo — check its "last verified" date. |
| [Tech Leadership](Tech%20Leadership/Engineering_Leadership_Interview_Prep.md) | Staff | Not technology-specific; no technical prerequisite, but most useful after the technical guides. |

Most of this kit is genuinely Staff-scoped by design — see "Who This Is For" above for where the *entry points* (Java Collections, Kubernetes' Basic tier) are more accessible.

## Quick-revision path

Interview tomorrow, not weeks from now? Don't read every guide front to back — for each guide you need, read only the **bolded Answer paragraph** of each question (skip Code and Follow-up on a first pass), then come back for **Follow-up** sections specifically on the questions closest to what you expect to be asked. That's the "can I say this out loud correctly" layer; Follow-up is the "can I go one level deeper when probed" layer, worth targeted review rather than exhaustive re-reading under time pressure.

Highest-yield guides for a generalist Staff/Lead loop, in priority order if you have to cut scope: [Java Concurrency](Language/Java_Concurrency_Interview_Prep.md), [Transactions](System%20Design/Transactions_Interview_Prep.md), [Kafka](System%20Design/Kafka_Interview_Prep.md), [Redis & Caching](System%20Design/Redis_Caching_Interview_Prep.md), [Spring Boot Internals](Frameworks/Spring_Boot_Internals_Interview_Prep.md), [Cross-Stack Design Scenarios](System%20Design/Cross_Stack_Design_Scenarios_Interview_Prep.md) — these are the topics that show up across the widest range of loop types.

## Deep-dive path

Weeks of runway, not days? Go in the [recommended study order](#recommended-study-order) above, guide by guide, and for each question: read the Answer, work through the Code example by hand (actually run it where it's real compilable code, not pseudocode), then read the cited primary source rather than trusting the guide's paraphrase of it — the source is there precisely so you don't have to take the paraphrase on faith. The Follow-up section on each question is a good self-check: cover it, answer the question yourself, then compare.

## Contents

Content is organized by kind of content, not by role — use the tables above to figure out which folders and difficulty levels matter most for the loop you're prepping for.

### Language

Pure Java runtime/language topics — no framework involved.

- **[Java Collections Interview Prep](Language/Java_Collections_Interview_Prep.md)** — `HashMap`/`TreeMap`/`LinkedHashMap` internals, concurrent collections, boxed-collection costs, and production leak diagnosis.
- **[Java Concurrency Interview Prep](Language/Java_Concurrency_Interview_Prep.md)** — Visibility/atomicity/ordering, locks, virtual threads, executors, `ForkJoinPool`, the ABA problem, and structured concurrency.
- **[Java JVM & GC Interview Prep](Language/Java_JVM_GC_Interview_Prep.md)** — Memory areas, JIT/escape analysis, reference types, G1/ZGC/Shenandoah, container OOM-kills, and native memory.

### Frameworks

Spring and JPA/Hibernate — how the framework itself works under the hood.

- **[Spring Boot Internals Interview Prep](Frameworks/Spring_Boot_Internals_Interview_Prep.md)** — `SpringApplication.run()` internals, bean lifecycle, auto-configuration, AOP proxies and self-invocation, graceful shutdown, and execution models.
- **[Spring Security & OAuth2 Interview Prep](Frameworks/Spring_Security_OAuth2_Interview_Prep.md)** — Filter chain architecture, CSRF/CORS, OAuth2 flows and PKCE, JWT validation and key rotation, token storage, BOLA, and multi-tenant authorization.
- **[JPA & Hibernate Interview Prep](Frameworks/JPA_Hibernate_Interview_Prep.md)** — Entity lifecycle, dirty checking and flushing, N+1 diagnosis and fixes, fetch strategies, optimistic/pessimistic locking, ID generation and batching, and DTO boundaries.

### System Design

Architecture, distributed-systems trade-offs, and cross-service concerns.

- **[Kafka Deep-Dive Interview Prep](System%20Design/Kafka_Interview_Prep.md)** — Topics, partitions, offsets, ordering guarantees, message keys, and consumer group rebalancing.
- **[REST API Design Interview Prep](System%20Design/REST_API_Design_Interview_Prep.md)** — Resource modeling, idempotency and retries, pagination strategies, versioning and backward compatibility, error formats, async workflows, and rate limiting.
- **[Transactions Interview Prep](System%20Design/Transactions_Interview_Prep.md)** — ACID and isolation levels, MVCC, Spring propagation types, deadlocks, the transactional outbox pattern, sagas vs. two-phase commit, and zero-downtime schema migration.
- **[Redis & Caching Interview Prep](System%20Design/Redis_Caching_Interview_Prep.md)** — Caching strategies, stampedes/penetration/pollution, eviction policies, hot keys, replication/Sentinel/Cluster, distributed locks and fencing tokens, rate limiting, and cache-deployment versioning.
- **[Cross-Stack Design Scenarios Interview Prep](System%20Design/Cross_Stack_Design_Scenarios_Interview_Prep.md)** — 20 end-to-end scenarios spanning Spring Boot, PostgreSQL, Redis, and Kafka: order platforms, multi-region trade-offs, zero-downtime deployments, incident diagnosis, service-boundary evaluation, and SLOs.

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

## How each question is structured

Every question in every guide follows the same shape:

1. **Answer** — a conversational, interview-ready explanation, phrased the way it would actually be said out loud, roughly 30–90 seconds if spoken.
2. **Code** — a snippet, config, SQL, sketch, or decision framework/template to back the explanation up (compilable code where practical; clearly labeled pseudocode/conceptual where not).
3. **Follow-up** — the deeper probe that separates a mid-level answer from a Staff-level one: failure modes, trade-offs, what breaks at scale.
4. **Source** — the authoritative reference(s) for the important claims made in that question.

## Accuracy and contribution policy

This kit is deliberately not optimizing for question count. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full policy — in short: primary sources over memory, version-scoped claims, no unscoped "always"/"never"/"guaranteed"/"exactly once," no fabricated production experience, and no AI-conversation artifacts. [`AUDIT.md`](AUDIT.md) tracks the verification status of every guide and every known issue found so far, fixed or still open.

## License

[CC BY-NC-SA 4.0](LICENSE) — you can share and adapt this material with attribution, for non-commercial purposes, under the same license. See the [`LICENSE`](LICENSE) file for the full terms.
