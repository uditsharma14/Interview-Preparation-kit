<p align="center">
  <img src="assets/logo.png" alt="InterviewSmith" width="440">
</p>

<h1 align="center">InterviewSmith</h1>
<p align="center"><em>The deep-dive, mid-to-staff-level interview prep kit — written to be said out loud, not skimmed.</em></p>
<p align="center">
  <a href="https://github.com/uditsharma14/InterviewSmith/actions/workflows/docs-check.yml"><img src="https://github.com/uditsharma14/InterviewSmith/actions/workflows/docs-check.yml/badge.svg" alt="Docs check"></a>
  <img alt="Guides" src="https://img.shields.io/badge/guides-26-orange">
  <img alt="Q&A entries" src="https://img.shields.io/badge/Q%26A%20entries-690%2B-orange">
  <img alt="Glossary terms" src="https://img.shields.io/badge/glossary%20terms-222-orange">
  <a href="LICENSE.md"><img alt="License" src="https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0%20(content)%20%2F%20MIT%20(scripts)-blue"></a>
</p>

Every push and PR runs markdown linting, internal-link/anchor validation, and external-citation link-checking automatically ([`.github/workflows/docs-check.yml`](.github/workflows/docs-check.yml)); a monthly scheduled run catches link rot that happens independent of any edit.

You don't walk into a Staff-level loop and get asked to define a `HashMap`. You get asked why it breaks under concurrent writes, what happens when the load factor tips, and what you'd actually do about it at 2 a.m. InterviewSmith is built to survive that follow-up: **26 guides, 690+ interview questions, and a 222-term glossary** — each question answered the way you'd actually say it out loud, supported by code, configuration, SQL, pseudocode, or design examples as fits the question, and closed out with exactly where a Staff-level interviewer pushes next. Several guides are explicitly graduated Basic → Staff, so the same guide works whether you're building the fundamentals for the first time or forging the deep end the night before a loop.

InterviewSmith optimizes for **accuracy over question count**. Every guide has undergone at least one audit pass against primary sources — Oracle/OpenJDK specs, Spring/Hibernate/Kafka/Redis/Kubernetes documentation, IETF RFCs, OWASP. See [`AUDIT.md`](AUDIT.md) for the review status of each guide and every finding, fixed or still open, and [`CONTRIBUTING.md`](CONTRIBUTING.md) for the citation/accuracy policy new material has to meet. An audit pass reduces errors; it doesn't guarantee none remain — version-sensitive claims should still be checked against the linked documentation before you repeat them somewhere it counts, and if you find one that's wrong or stale, `AUDIT.md` and the contribution policy exist to fix it.

## Contents

- [How to use this repository](#how-to-use-this-repository)
- [Who this is for](#who-this-is-for)
- [Study paths](#study-paths)
- [Difficulty by guide](#difficulty-by-guide)
- [Guides by topic](#guides-by-topic)
- [How each question is structured](#how-each-question-is-structured)
- [Accuracy and contribution policy](#accuracy-and-contribution-policy)
- [License](#license)

## How to use this repository

- **This is a reference, not a substitute** for coding practice, mock interviews, or your own behavioral stories. It exists to help you *speak accurately* about a topic you already understand well enough to be asked about — it won't teach you to code under time pressure, simulate the back-and-forth of a real interview loop, or hand you a STAR story about a decision you didn't actually make. Pair it with real practice (LeetCode/system-design mocks, a friend or peer running you through questions cold) rather than treating reading alone as preparation.
- Start with a guide's own header — target level, technology baseline, and prerequisites are stated up front, so you know whether it's the right entry point before reading a word further.
- Pick a [study path](#study-paths) that matches the time you actually have, rather than defaulting to reading every guide front to back.
- Every interview question includes a **Source** section linking to references supporting its important technical claims — treat a guide's prose as a fast, spoken-out-loud paraphrase, and the linked source as the actual authority, especially for anything version-sensitive.
- Found something wrong or stale? [`AUDIT.md`](AUDIT.md) tracks known issues and [`CONTRIBUTING.md`](CONTRIBUTING.md) has the fix policy.

## Who this is for

Current interview loops for **Full Stack**, **Forward Deployed**, and **Staff** engineering roles overlap a lot but weight things differently — these three are the loops InterviewSmith was actually built against, chosen because they cover the widest realistic spread (a Full Stack loop leans toward breadth and applied fundamentals, a Forward Deployed loop leans toward ambiguity and delivery under real-world constraints, and a Staff loop leans toward depth and architectural judgment). Here's what's covered today versus still a gap, per role, so you know where to spend time:

| Role | What their loop leans on | Covered here | Still a gap |
|---|---|---|---|
| **Full Stack Engineer** | Frontend fundamentals (React/TS, browser/perf) • Backend API design • Databases • Light system design • Testing | [Frontend & Full-Stack](Frontend%20%26%20Full-Stack/) • [Frameworks](Frameworks/) • [System Design](System%20Design/) (esp. [REST API Design](System%20Design/REST_API_Design_Interview_Prep.md)) • [Testing](Testing/) • [Language](Language/) | Browser/rendering performance deep dives beyond what's in the frontend guides |
| **Forward Deployed Engineer** | Rapid prototyping across the stack • Scripting/data wrangling • Ambiguous requirements, messy environments • Stakeholder communication • Deploying into a customer's locked-down infrastructure • Increasingly, LLM/agent integration on client data | [System Design](System%20Design/) (esp. [Cross-Stack Scenarios](System%20Design/Cross_Stack_Design_Scenarios_Interview_Prep.md)) • [Tech Leadership](Tech%20Leadership/) (ambiguity, influence) • [AI Engineering](AI%20Engineering/) • [Kubernetes, Docker & Cloud](Kubernetes%2C%20Docker%20%26%20Cloud/) | [Forward-Deployed & Customer-Facing Engineering](Forward-Deployed%20%26%20Customer-Facing%20Engineering/) *(reserved)* |
| **Staff Engineer** | Deep fundamentals across the stack • System design and trade-offs • Architecture/design judgment • Organizational leverage and leadership | Nearly everything — [Language](Language/) • [Design Patterns](Design%20Patterns/) • [Frameworks](Frameworks/) • [Testing](Testing/) • [System Design](System%20Design/) • [Tech Leadership](Tech%20Leadership/) • [Microservices & Architecture Patterns](Microservices%20%26%20Architecture%20Patterns/) • [Kubernetes, Docker & Cloud](Kubernetes%2C%20Docker%20%26%20Cloud/) | — |

*(reserved = no content yet — see [Guides by topic](#guides-by-topic) for what's planned)*

AI/LLM-application questions have become common across all three loops in the last year or two — even a straightforward backend or full-stack interview now often includes "how would you design a RAG pipeline" or "how do you evaluate an LLM feature." That's why **AI Engineering** is its own section rather than folded into System Design.

## Study paths

Pick based on how much time you actually have — not "read everything front to back."

### One day

Interview tomorrow. For each guide you need, read only the bolded **Answer** paragraph per question first — skip Code and Follow-up on this pass; that's the "can I say this out loud correctly" layer. Then go back for **Follow-up** sections only on the questions closest to what you actually expect to be asked.

Highest-yield guides for a generalist Staff/Lead loop, in priority order if you have to cut scope: [Java Concurrency](Language/Java_Concurrency_Interview_Prep.md), [Transactions](System%20Design/Transactions_Interview_Prep.md), [Kafka](System%20Design/Kafka_Interview_Prep.md), [Redis & Caching](System%20Design/Redis_Caching_Interview_Prep.md), [Spring Boot Internals](Frameworks/Spring_Boot_Internals_Interview_Prep.md), [Cross-Stack Design Scenarios](System%20Design/Cross_Stack_Design_Scenarios_Interview_Prep.md) — these show up across the widest range of loop types.

### One week

Enough time for the core stack your specific loop leans on, not the whole kit — use [Who this is for](#who-this-is-for) to pick the guides. Read each question's full Answer, Code, and Follow-up; the cited Source is optional unless a claim is version-sensitive or looks off. For a generalist backend/Staff loop, that's roughly: Language → Frameworks → Testing → Transactions/Kafka/Redis/REST API Design → Microservices & Architecture Patterns — the same dependency order as the four-week path below, just stopping once your loop's actual scope is covered.

### Four weeks

Enough time to go deep, guide by guide, in the order below — it minimizes backtracking, since later guides assume earlier ones' vocabulary without re-explaining it. For each question: read the Answer, work through the Code example by hand (actually run it where it's real compilable code, not pseudocode), read the cited primary source rather than trusting the paraphrase, then use Follow-up as a self-check — cover it, answer it yourself, compare.

0. **[Computer Science Fundamentals](Computer%20Science%20Fundamentals/Computer_Science_Fundamentals_Interview_Prep.md)** — genuinely optional if HTTP, TCP/UDP, DNS, encryption, and Big-O are already second nature; every other guide assumes this vocabulary without re-explaining it.
1. **[Java Collections](Language/Java_Collections_Interview_Prep.md) → [Java Concurrency](Language/Java_Concurrency_Interview_Prep.md) → [Java JVM & GC](Language/Java_JVM_GC_Interview_Prep.md)** — language fundamentals everything else assumes.
2. **[Spring Boot Internals](Frameworks/Spring_Boot_Internals_Interview_Prep.md) → [Spring Security & OAuth2](Frameworks/Spring_Security_OAuth2_Interview_Prep.md) → [JPA & Hibernate](Frameworks/JPA_Hibernate_Interview_Prep.md)** — the framework layer most code examples elsewhere use.
3. **[Software Testing](Testing/Software_Testing_Interview_Prep.md)** — its Basic section needs no prerequisite and can be read anytime; from the JUnit/Mockito content onward it assumes Spring Boot Internals (and JPA & Hibernate for the `@DataJpaTest`/Testcontainers questions), so it's placed here while that context is fresh.
4. **[Transactions](System%20Design/Transactions_Interview_Prep.md) → [Kafka](System%20Design/Kafka_Interview_Prep.md) → [Redis & Caching](System%20Design/Redis_Caching_Interview_Prep.md) → [REST API Design](System%20Design/REST_API_Design_Interview_Prep.md)** — Transactions first: its dual-write-problem and outbox-pattern framing gets reused directly by Kafka and Redis.
5. **[Microservices & Architecture Patterns](Microservices%20%26%20Architecture%20Patterns/Microservices_Architecture_Patterns_Interview_Prep.md)** — assumes Transactions (sagas, 2PC), REST API Design, and Redis/Kafka above.
6. **[Cross-Stack Design Scenarios](System%20Design/Cross_Stack_Design_Scenarios_Interview_Prep.md)** — deliberately last among the technical guides; every scenario draws on several guides above at once, the way a real Staff-level system-design round actually does.
7. **[Kubernetes, Docker & Cloud](Kubernetes%2C%20Docker%20%26%20Cloud/Kubernetes_Docker_Interview_Prep.md)** — mostly independent of the above; can be read any time, and is itself graduated Basic → Staff internally.
8. **[LLM Fundamentals](AI%20Engineering/LLM_Fundamentals_Interview_Prep.md) → [AI Engineering](AI%20Engineering/AI_Engineering_Interview_Prep.md) → [Vector Databases & RAG](AI%20Engineering/Vector_Databases_and_RAG_Interview_Prep.md) → [LLM System Design](System%20Design/LLM_System_Design_Interview_Prep.md)** — LLM Fundamentals needs no prerequisite beyond general software engineering; AI Engineering and Vector Databases & RAG assume it and each other; LLM System Design assumes all three plus general backend engineering (steps 1–5), and cross-references REST API Design, Redis, and Transactions for patterns (retries, idempotency, caching) that apply directly to LLM-backed systems.
9. **[Tech Leadership](Tech%20Leadership/Engineering_Leadership_Interview_Prep.md)** — not technology-specific, but most useful last: the judgment questions here often draw on the technical material above for concrete grounding.

## Difficulty by guide

| Guide | Level | Notes |
|---|---|---|
| [Computer Science Fundamentals](Computer%20Science%20Fundamentals/Computer_Science_Fundamentals_Interview_Prep.md) | **Basic (only)** | No Staff tier — this guide deliberately stays foundational (HTTP, TCP/UDP, DNS, encryption, Big-O) and points into the other guides for depth on each topic. |
| [Java Collections](Language/Java_Collections_Interview_Prep.md) | **Basic → Staff** | Explicitly graduated internally: Basic → Intermediate → Staff. The Intermediate section onward assumes `equals()`/`hashCode()` basics; escalates to production leak diagnosis. |
| [Java Concurrency](Language/Java_Concurrency_Interview_Prep.md) | **Basic → Staff** | Explicitly graduated internally: Basic → Intermediate → Staff. The Intermediate section onward assumes Collections. |
| [Java JVM & GC](Language/Java_JVM_GC_Interview_Prep.md) | **Basic → Staff** | Explicitly graduated internally: Basic → Intermediate → Staff. The Staff-level section assumes Collections and Concurrency for some parts. |
| [OOP Concepts](Language/OOP_Concepts_Interview_Prep.md) | **Basic → Staff** | Explicitly graduated internally: Basic → Intermediate → Staff. Core Java syntax is the only prerequisite for the Basic section; Design Patterns builds on top of this guide's vocabulary rather than re-explaining it. |
| [Design Patterns](Design%20Patterns/Design_Patterns_Interview_Prep.md) | Basic → Staff | Organized by GoF category (Creational → Structural → Behavioral), not graduated by difficulty — core Java OOP is the only prerequisite. |
| [Spring Boot Internals](Frameworks/Spring_Boot_Internals_Interview_Prep.md) | **Basic → Staff** | Explicitly graduated internally: Basic → Intermediate → Staff. The Intermediate section onward assumes the Basic section's `@Component`/`@Autowired` familiarity. |
| [Spring Security & OAuth2](Frameworks/Spring_Security_OAuth2_Interview_Prep.md) | **Basic → Staff** | Explicitly graduated internally: Basic → Intermediate → Staff. Assumes Spring Boot Internals for the Basic section. |
| [JPA & Hibernate](Frameworks/JPA_Hibernate_Interview_Prep.md) | **Basic → Staff** | Explicitly graduated internally: Basic → Intermediate → Staff. Assumes Spring Boot Internals and basic SQL for the Basic section. |
| [Software Testing](Testing/Software_Testing_Interview_Prep.md) | **Basic → Staff** | Explicitly graduated internally: Basic → Intermediate → Staff (scenario-based). The Basic section opens with testing fundamentals/types of testing (no prerequisite) before moving into JUnit/Mockito, which assumes Spring Boot Internals; the Intermediate section also covers SDET automation tooling (Selenium, API testing, BDD/Cucumber), and the Staff section leans on JPA & Hibernate for the `@DataJpaTest`/Testcontainers questions. |
| [Transactions](System%20Design/Transactions_Interview_Prep.md) | Staff | Assumes basic SQL. |
| [Kafka](System%20Design/Kafka_Interview_Prep.md) | Staff | Assumes basic messaging/pub-sub concepts. |
| [Redis & Caching](System%20Design/Redis_Caching_Interview_Prep.md) | Staff | Assumes basic Redis commands. |
| [REST API Design](System%20Design/REST_API_Design_Interview_Prep.md) | Staff | Assumes basic HTTP. |
| [Microservices & Architecture Patterns](Microservices%20%26%20Architecture%20Patterns/Microservices_Architecture_Patterns_Interview_Prep.md) | **Basic → Staff** | Explicitly graduated internally: Basic → Intermediate → Staff. Transactions, REST API Design, Redis, and Kafka are helpful from the Intermediate section onward, not required for Basic. |
| [Cross-Stack Design Scenarios](System%20Design/Cross_Stack_Design_Scenarios_Interview_Prep.md) | Staff | Assumes the rest of the technical guides — deliberately cross-cutting. |
| [LLM System Design](System%20Design/LLM_System_Design_Interview_Prep.md) | Staff | Assumes AI Engineering, LLM Fundamentals, and Vector Databases & RAG — deliberately cross-cutting, the AI-application analog of Cross-Stack Design Scenarios. |
| [Kubernetes, Docker & Cloud](Kubernetes%2C%20Docker%20%26%20Cloud/Kubernetes_Docker_Interview_Prep.md) | **Beginner → Staff** | Explicitly graduated internally: Docker Basic → Staff, then Kubernetes Basic → Staff. |
| [LLM Fundamentals](AI%20Engineering/LLM_Fundamentals_Interview_Prep.md) | Lead/Staff | No prerequisite beyond general software engineering; model-internals/training-methodology layer beneath AI Engineering. |
| [AI Engineering](AI%20Engineering/AI_Engineering_Interview_Prep.md) | Staff | Assumes general backend engineering; fastest-moving guide in the repo — check its "last verified" date. |
| [Vector Databases & RAG](AI%20Engineering/Vector_Databases_and_RAG_Interview_Prep.md) | Lead/Staff | Assumes LLM Fundamentals (embeddings, cosine similarity) and AI Engineering's RAG questions — goes one layer deeper into vector-database/embedding-model mechanics. |
| [Tech Leadership](Tech%20Leadership/Engineering_Leadership_Interview_Prep.md) | Staff | Not technology-specific; no technical prerequisite, but most useful after the technical guides. |
| [Next.js](Frontend%20%26%20Full-Stack/NextJS_Interview_Prep.md) | Intermediate | Deliberately lighter than this repo's usual Staff depth — assumes React (components, hooks, the virtual DOM) and focuses on what Next.js adds on top. |

Most of InterviewSmith is genuinely Staff-scoped by design — see [Who this is for](#who-this-is-for) above for where the *entry points* (Computer Science Fundamentals in full; the Basic tiers of Java Collections, Java Concurrency, Java JVM & GC, Spring Boot Internals, Spring Security & OAuth2, JPA & Hibernate, and Software Testing; Kubernetes' Basic tier) are more accessible.

## Guides by topic

Organized by kind of content, not by role — use [Who this is for](#who-this-is-for) or the table above to figure out what actually matters for your loop. 13 topic areas have content today; 1 is reserved for future material, grouped at the end of this section rather than mixed in among the completed ones.

### Computer Science Fundamentals

Networking, HTTP, encryption, and general CS/software terminology — Basic-only, no framework or language involved. The foundational layer every other guide assumes without re-explaining it.

- **[Computer Science Fundamentals Interview Prep](Computer%20Science%20Fundamentals/Computer_Science_Fundamentals_Interview_Prep.md)** — Networking (TCP vs. UDP, DNS, IP/ports, URI/URL/URN), HTTP (statelessness, HTTP/1.1 vs. 2 vs. 3, status codes, headers vs. body), encryption/security (symmetric vs. asymmetric, hashing, TLS handshake, certificates/CAs), data structures & algorithms (stack/queue, tree vs. graph, recursion, Big-O), programming languages & OOP (the four pillars, compiled vs. interpreted, static vs. dynamic typing), operating systems (kernel, virtual memory/paging, CPU caching), databases (SQL vs. NoSQL, normalization, indexes), and software engineering practices (version control, unit/integration/E2E testing).
- **[Computer Science Glossary](Computer%20Science%20Fundamentals/Computer_Science_Glossary.md)** — a fast, 2–3-line-per-term reference covering 222 core CS/software-engineering/ML terms, grouped by theme rather than alphabetically, including a Machine Learning Fundamentals section (supervised/unsupervised learning, precision/recall/F1, gradient descent, backpropagation, CNN/RNN/LSTM, regularization, dropout). Not a substitute for the interview-answer guides — it's the "what does this word mean" layer beneath them, with pointers into the guides that cover any given term in real depth.

### Language

Pure Java runtime/language topics — no framework involved.

- **[Java Collections Interview Prep](Language/Java_Collections_Interview_Prep.md)** — Graduated Basic → Staff: core interfaces, `equals()`/`hashCode()`, and `Comparable`/`Comparator` basics through `HashMap`/`TreeMap`/`LinkedHashMap` internals, concurrent collections, boxed-collection costs, and production leak diagnosis.
- **[Java Concurrency Interview Prep](Language/Java_Concurrency_Interview_Prep.md)** — Graduated Basic → Staff: threads, `synchronized`, and deadlock basics through `ExecutorService`/coordination primitives to visibility/atomicity/ordering, lock comparisons, virtual threads, `ForkJoinPool`, the ABA problem, and structured concurrency.
- **[Java JVM & GC Interview Prep](Language/Java_JVM_GC_Interview_Prep.md)** — Graduated Basic → Staff: JVM/JDK/JRE, stack vs. heap, GC basics, and generational-heap fundamentals through memory areas, JIT/escape analysis, reference types, G1/ZGC/Shenandoah, container OOM-kills, and native memory.
- **[OOP Concepts Interview Prep](Language/OOP_Concepts_Interview_Prep.md)** — Graduated Basic → Staff: the four pillars (encapsulation, inheritance, polymorphism, abstraction) through interfaces vs. abstract classes, composition over inheritance, and immutability, to the Liskov Substitution Principle, the diamond problem, and OOP anti-patterns at Staff scale.

### Design Patterns

Classic Gang-of-Four patterns and how they show up in real Java/Spring codebases — organized by GoF category, not difficulty.

- **[Design Patterns Interview Prep](Design%20Patterns/Design_Patterns_Interview_Prep.md)** — 15 GoF patterns with compilable Java examples: Creational (Singleton, Factory Method, Builder), Structural (Adapter, Decorator, Facade, Proxy, Composite), and Behavioral (Observer, Strategy, Command, Iterator, State, Template Method, Chain of Responsibility) — each tied to its real JDK/Spring instance and to when the pattern is overkill for a simpler design.

### Frameworks

Spring and JPA/Hibernate — how the framework itself works under the hood.

- **[Spring Boot Internals Interview Prep](Frameworks/Spring_Boot_Internals_Interview_Prep.md)** — Graduated Basic → Staff: DI/IoC and bean basics, stereotype annotations, and Spring Boot vs. Framework through `SpringApplication.run()` internals, bean lifecycle, auto-configuration, AOP proxies and self-invocation, graceful shutdown, and execution models.
- **[Spring Security & OAuth2 Interview Prep](Frameworks/Spring_Security_OAuth2_Interview_Prep.md)** — Graduated Basic → Staff: `UserDetailsService`, password hashing, RBAC, and JWT structure basics through filter chain architecture, CSRF/CORS, OAuth2 flows and PKCE, JWT validation and key rotation, token storage, BOLA, and multi-tenant authorization.
- **[JPA & Hibernate Interview Prep](Frameworks/JPA_Hibernate_Interview_Prep.md)** — Graduated Basic → Staff: ORM/JPA/Hibernate basics, entity/repository fundamentals, and relationship annotations through entity lifecycle, dirty checking and flushing, N+1 diagnosis and fixes, fetch strategies, optimistic/pessimistic locking, ID generation and batching, and DTO boundaries.

### Testing

Testing-framework mechanics and scenario-based testing strategy, organized as its own graduated guide rather than folded into the Frameworks section.

- **[Software Testing Interview Prep](Testing/Software_Testing_Interview_Prep.md)** — Graduated Basic → Staff, written for SDET and QA roles as much as backend engineers: testing fundamentals and terminology (verification vs. validation, STLC, test plan/strategy/case, functional vs. non-functional, black/white/gray-box, smoke/sanity/regression, manual vs. automation, the defect life cycle and severity vs. priority) and JUnit/Mockito basics, through `@ParameterizedTest`, Spring Boot test slices, `MockMvc`, Testcontainers, and SDET automation tooling — API testing, Selenium WebDriver, the Page Object Model, BDD/Cucumber, data- vs. keyword-driven testing, and the test automation pyramid — to Staff-level scenario-based questions covering an external payment gateway, `@Async`/scheduled tasks, Kafka producers/consumers, flaky tests (both unit and UI/Selenium), time-dependent code, designing an automation framework from scratch, performance/load/stress/spike/soak testing, structuring test suites in CI, property-based testing, mutation testing, security testing (SAST/DAST/SCA/pentest), and testing distributed, eventually-consistent workflows like sagas.

### System Design

Architecture, distributed-systems trade-offs, and cross-service concerns.

- **[Kafka Deep-Dive Interview Prep](System%20Design/Kafka_Interview_Prep.md)** — Topics, partitions, offsets, ordering guarantees, message keys, and consumer group rebalancing.
- **[REST API Design Interview Prep](System%20Design/REST_API_Design_Interview_Prep.md)** — Resource modeling, idempotency and retries, pagination strategies, versioning and backward compatibility, error formats, async workflows, and rate limiting.
- **[Transactions Interview Prep](System%20Design/Transactions_Interview_Prep.md)** — ACID and isolation levels, MVCC, Spring propagation types, deadlocks, the transactional outbox pattern, sagas vs. two-phase commit, and zero-downtime schema migration.
- **[Redis & Caching Interview Prep](System%20Design/Redis_Caching_Interview_Prep.md)** — Caching strategies, stampedes/penetration/pollution, eviction policies, hot keys, replication/Sentinel/Cluster, distributed locks and fencing tokens, rate limiting, and cache-deployment versioning.
- **[Cross-Stack Design Scenarios Interview Prep](System%20Design/Cross_Stack_Design_Scenarios_Interview_Prep.md)** — 20 end-to-end scenarios spanning Spring Boot, PostgreSQL, Redis, and Kafka: order platforms, multi-region trade-offs, zero-downtime deployments, incident diagnosis, service-boundary evaluation, and SLOs.
- **[LLM System Design Interview Prep](System%20Design/LLM_System_Design_Interview_Prep.md)** — end-to-end LLM-application scenarios: an enterprise RAG platform, an AI incident-response copilot, a customer-support chatbot, a scalable ingestion pipeline, supporting a million requests/day, semantic caching, multi-region LLM infrastructure, and observability.
- **[System Design Interview Question Bank](System%20Design/System_Design_Interview_Question_Bank.md)** — a practice-prompt list (not full worked answers) spanning core system design, distributed transactions/payments, event-driven architecture, data-intensive systems, AI/Forward-Deployed scenarios, and the follow-up questions a Principal-level interviewer presses on.

### Tech Leadership

Lead/Staff-level judgment, influence, and organizational impact — not technology-specific.

- **[Lead/Staff Engineering & Technical Leadership Interview Prep](Tech%20Leadership/Engineering_Leadership_Interview_Prep.md)** — Architectural decision-making, influence without authority, platform standards, incident leadership, technical strategy, and what Staff-level impact looks like beyond code.

### AI Engineering

- **[LLM Fundamentals Interview Prep](AI%20Engineering/LLM_Fundamentals_Interview_Prep.md)** — Transformer architecture, self-attention and QKV, multi-head attention, positional embeddings, tokenization, temperature and top-k/top-p sampling, embeddings and cosine similarity, instruction tuning, RLHF, LoRA/PEFT, and quantization.
- **[AI Engineering Interview Prep](AI%20Engineering/AI_Engineering_Interview_Prep.md)** — Hosted vs. self-hosted models, prompting vs. fine-tuning vs. RAG, chunking and hybrid search, agent/tool-calling design (including LangGraph and agent memory) and guardrails, evaluation (golden datasets, faithfulness, offline/online), hallucination mitigation, prompt injection, cost/latency management, canary rollouts, and provider-outage fallback in production.
- **[Vector Databases & RAG Interview Prep](AI%20Engineering/Vector_Databases_and_RAG_Interview_Prep.md)** — ANN search and HNSW, embedding-model selection and migration, metadata filtering, duplicate/stale-document handling, retrieval recall, citations, multi-tenant RAG isolation, and comparing Qdrant, Pinecone, FAISS, and pgvector.

### Microservices & Architecture Patterns

- **[Microservices & Architecture Patterns Interview Prep](Microservices%20%26%20Architecture%20Patterns/Microservices_Architecture_Patterns_Interview_Prep.md)** — Service decomposition and bounded contexts, strangler fig migration, API Gateway/BFF/sidecar/service mesh, CQRS and event sourcing, CAP theorem, hexagonal/clean architecture, contract testing, and the distributed monolith.

### Kubernetes, Docker & Cloud

- **[Docker & Kubernetes Interview Prep](Kubernetes%2C%20Docker%20%26%20Cloud/Kubernetes_Docker_Interview_Prep.md)** — Basic through Staff level: containers vs. VMs, image layers and multi-stage builds, namespaces/cgroups, Pods/Deployments/Services/Ingress, probes, scheduling, StatefulSets, multi-tenancy, etcd, zero-downtime rollouts, cluster security, and service mesh vs. native Kubernetes.

### Frontend & Full-Stack

Client-side fundamentals — the JavaScript language and runtime, plus the frameworks most commonly asked about in Full Stack loops.

- **[JavaScript Interview Prep](Frontend%20%26%20Full-Stack/JavaScript_Interview_Prep.md)** — `var`/`let`/`const` and hoisting, closures, the event loop and microtask/macrotask queues, Promises and `async`/`await`, prototypal inheritance, memory leaks, debounce vs. throttle, the V8 garbage collector, and XSS defense.
- **[Angular Interview Prep](Frontend%20%26%20Full-Stack/Angular_Interview_Prep.md)** — Components and data binding, standalone components vs. NgModules, Signals, change detection and zoneless Angular, dependency injection, forms, RxJS interop, SSR/hydration, and state-management trade-offs.
- **[React Interview Prep](Frontend%20%26%20Full-Stack/React_Interview_Prep.md)** — JSX and the virtual DOM, Hooks, reconciliation and Fiber, concurrent rendering, the React Compiler, Server Components, Actions, and state-management and testing trade-offs.
- **[Next.js Interview Prep](Frontend%20%26%20Full-Stack/NextJS_Interview_Prep.md)** — Intermediate level. File-based routing in the App Router, the App Router vs. the Pages Router, dynamic routes, layouts, SSR vs. SSG vs. ISR, Server Components vs. Client Components, Route Handlers, data fetching/caching, Middleware, and deployment options.

### Data Structures & Algorithms

Curated practice lists, not worked-answer guides — one organized by 20 recognizable algorithmic patterns (Two Pointers, Sliding Window, Tree BFS/DFS, Dynamic Programming, and more), the same approach popularized by "Grokking the Coding Interview" and NeetCode; the other the well-known, minimal "Blind 75" selection, organized by data-structure category instead.

- **[DSA Pattern-Based Question Bank](Data%20Structures%20%26%20Algorithms/DSA_Pattern_Based_Question_Bank.md)** — 100 problems across 20 patterns, each with a "recognize it when" signal and typical complexity, grouped into Array/String, Linked List, Interval, Tree/Graph, Searching/Heap, Combinatorial, Dynamic Programming, Greedy/Bit Manipulation, and Stack patterns.
- **[Blind 75 Question Bank](Data%20Structures%20%26%20Algorithms/Blind_75_Question_Bank.md)** — the well-known, minimal 75-problem list, organized by data-structure category (Array, Binary, Dynamic Programming, Graph, Interval, Linked List, Matrix, String, Tree, Heap) the way it's traditionally presented.

### Further Reading

External articles, videos, and engineering-blog write-ups — not InterviewSmith's own Q&A guides, and not held to the same primary-source citation bar (see the note at the top of the list itself).

- **[System Design & AI Engineering Reading List](Further%20Reading/System_Design_and_AI_Reading_List.md)** — System design deep-dive articles, 26 classic system-design write-ups by category (rate limiters, key-value stores, chat systems, payments, and more), AI agent video courses, AI engineering core concepts, real-world system design case studies from 16 companies' engineering blogs, and 20 foundational system design concepts.

### Reserved — not yet written

This folder exists today only as a placeholder README stating its planned scope — there is no guide content in it yet.

- **[Forward-Deployed & Customer-Facing Engineering](Forward-Deployed%20%26%20Customer-Facing%20Engineering/)** — rapid prototyping under ambiguity, scripting and data wrangling against messy client data/systems, integrating with a customer's existing infrastructure, and the specific communication/expectation-setting skills these roles are actually screened on.

## How each question is structured

Most guides follow the same four-part shape below, deliberately, so once you're used to the pattern in one guide, most other guides read the same way — the exceptions are the guides already migrated to the newer structures described after the list:

1. **Answer** — a conversational, interview-ready explanation, phrased the way it would actually be said out loud, roughly 30–90 seconds if spoken. This is the part you should be able to recite cold.
2. **Code** — a snippet, config, SQL, sketch, or decision framework/template to back the explanation up (compilable code where practical; clearly labeled pseudocode/conceptual where not).
3. **Follow-up** — the deeper probe that separates a mid-level answer from a Staff-level one: failure modes, trade-offs, what breaks at scale.
4. **Source** — the authoritative reference(s) for the important claims made above.

A rollout to a more granular five-part structure (Core answer / Staff-level extension / Example / Follow-up questions / Sources — same underlying content, with the deeper trade-off material explicitly pulled out of the core spoken answer) is in progress guide by guide — see [`AUDIT.md`](AUDIT.md) for which guides have migrated so far. Every question in the Software Testing guide uses a related six-part variant that adds an explicit **Failure modes** section, and Computer Science Fundamentals uses its own lighter Basic-level four-part variant (Answer / Example / "Go deeper" / Source, 80–150-word answers) — see each guide's `AUDIT.md` entry for why.

## Accuracy and contribution policy

InterviewSmith is deliberately not optimizing for question count. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full policy — in short: primary sources over memory, version-scoped claims, no unscoped "always"/"never"/"guaranteed"/"exactly once," no fabricated production experience, and no AI-conversation artifacts. [`AUDIT.md`](AUDIT.md) tracks the review status of every guide and every known issue found so far, fixed or still open.

## License

InterviewSmith is **dual-licensed** — this repository is not entirely
MIT-licensed. See [`LICENSE.md`](LICENSE.md) for the full explanation of
what's covered by which license and why.

| Content | License |
|---|---|
| The guides, glossary, diagrams, and other educational/written content | [CC BY-NC-SA 4.0](LICENSE-CONTENT) — attribution required, non-commercial only, share-alike |
| Repository tooling in [`scripts/`](scripts/) | [MIT](LICENSE-CODE) — permissive, minimal restriction |
