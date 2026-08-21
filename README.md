# Interview Preparation Kit

A collection of deep-dive, mid-to-staff-level interview prep notes for technical interviews. Each topic is written as a set of Q&A entries with the answer phrased the way it would actually be said out loud in an interview, backed by code snippets and pointers to where staff-level follow-up questions tend to go.

## Who This Is For

Current interview loops for **Full Stack**, **Forward Deployed**, and **Staff** engineering roles overlap a lot but weight things differently. Here's what's actually covered today versus still a gap, per role, so you know where to spend time:

| Role | What their loop usually leans on | Covered here | Still a gap |
|---|---|---|---|
| **Full Stack Engineer** | Frontend fundamentals (React/TS, browser/perf), backend API design, databases, light system design, testing | [Frameworks](Frameworks/), [System Design](System%20Design/) (esp. [REST API Design](System%20Design/REST_API_Design_Interview_Prep.md)), [Language](Language/) | [Frontend & Full-Stack](Frontend%20%26%20Full-Stack/) *(reserved)* |
| **Forward Deployed Engineer** | Rapid prototyping across the stack, scripting/data wrangling, working with ambiguous client requirements and messy environments, stakeholder communication, deploying into a customer's own (often locked-down) infrastructure, increasingly LLM/agent integration on top of client data | [System Design](System%20Design/) (esp. [Cross-Stack Scenarios](System%20Design/Cross_Stack_Design_Scenarios_Interview_Prep.md)), [Tech Leadership](Tech%20Leadership/) (ambiguity, influence, communication), [AI Engineering](AI%20Engineering/), [Kubernetes, Docker & Cloud](Kubernetes%2C%20Docker%20%26%20Cloud/) *(reserved)* | [Forward-Deployed & Customer-Facing Engineering](Forward-Deployed%20%26%20Customer-Facing%20Engineering/) *(reserved)* |
| **Staff Engineer** | Deep fundamentals across the stack, system design and trade-offs, architecture/design judgment, organizational leverage and leadership | Nearly everything — [Language](Language/), [Frameworks](Frameworks/), [System Design](System%20Design/), [Tech Leadership](Tech%20Leadership/), [Microservices & Architecture Patterns](Microservices%20%26%20Architecture%20Patterns/) | [Design Patterns](Design%20Patterns/) *(reserved)*, [Kubernetes, Docker & Cloud](Kubernetes%2C%20Docker%20%26%20Cloud/) *(reserved)* |

AI/LLM-application questions have become common across all three loops in the last year or two — even a straightforward backend or full-stack interview now often includes "how would you design a RAG pipeline" or "how do you evaluate an LLM feature" — which is why **AI Engineering** is reserved as its own section rather than folded into System Design.

## Contents

Content is organized by kind of content, not by role — use the table above to figure out which folders matter most for the loop you're prepping for.

## Language

Pure Java runtime/language topics — no framework involved.

- **[Java Collections Interview Prep](Language/Java_Collections_Interview_Prep.md)** — `HashMap`/`TreeMap`/`LinkedHashMap` internals, concurrent collections, boxed-collection costs, and production leak diagnosis.
- **[Java Concurrency Interview Prep](Language/Java_Concurrency_Interview_Prep.md)** — Visibility/atomicity/ordering, locks, virtual threads, executors, `ForkJoinPool`, the ABA problem, and structured concurrency.
- **[Java JVM & GC Interview Prep](Language/Java_JVM_GC_Interview_Prep.md)** — Memory areas, JIT/escape analysis, reference types, G1/ZGC/Shenandoah, container OOM-kills, and native memory.

## Frameworks

Spring and JPA/Hibernate — how the framework itself works under the hood.

- **[Spring Boot Internals Interview Prep](Frameworks/Spring_Boot_Internals_Interview_Prep.md)** — `SpringApplication.run()` internals, bean lifecycle, auto-configuration, AOP proxies and self-invocation, graceful shutdown, and execution models.
- **[Spring Security & OAuth2 Interview Prep](Frameworks/Spring_Security_OAuth2_Interview_Prep.md)** — Filter chain architecture, CSRF/CORS, OAuth2 flows and PKCE, JWT validation and key rotation, token storage, BOLA, and multi-tenant authorization.
- **[JPA & Hibernate Interview Prep](Frameworks/JPA_Hibernate_Interview_Prep.md)** — Entity lifecycle, dirty checking and flushing, N+1 diagnosis and fixes, fetch strategies, optimistic/pessimistic locking, ID generation and batching, and DTO boundaries.

## System Design

Architecture, distributed-systems trade-offs, and cross-service concerns.

- **[Kafka Deep-Dive Interview Prep](System%20Design/Kafka_Interview_Prep.md)** — Topics, partitions, offsets, ordering guarantees, message keys, and consumer group rebalancing.
- **[REST API Design Interview Prep](System%20Design/REST_API_Design_Interview_Prep.md)** — Resource modeling, idempotency and retries, pagination strategies, versioning and backward compatibility, error formats, async workflows, and rate limiting.
- **[Transactions Interview Prep](System%20Design/Transactions_Interview_Prep.md)** — ACID and isolation levels, MVCC, Spring propagation types, deadlocks, the transactional outbox pattern, sagas vs. two-phase commit, and zero-downtime schema migration.
- **[Redis & Caching Interview Prep](System%20Design/Redis_Caching_Interview_Prep.md)** — Caching strategies, stampedes/penetration/pollution, eviction policies, hot keys, replication/Sentinel/Cluster, distributed locks and fencing tokens, rate limiting, and cache-deployment versioning.
- **[Cross-Stack Design Scenarios Interview Prep](System%20Design/Cross_Stack_Design_Scenarios_Interview_Prep.md)** — 20 end-to-end scenarios spanning Spring Boot, PostgreSQL, Redis, and Kafka: order platforms, multi-region trade-offs, zero-downtime deployments, incident diagnosis, service-boundary evaluation, and SLOs.

## Tech Leadership

Lead/Staff-level judgment, influence, and organizational impact — not technology-specific.

- **[Lead/Staff Engineering & Technical Leadership Interview Prep](Tech%20Leadership/Engineering_Leadership_Interview_Prep.md)** — Architectural decision-making, influence without authority, platform standards, incident leadership, technical strategy, and what Staff-level impact looks like beyond code.

## AI Engineering

- **[AI Engineering Interview Prep](AI%20Engineering/AI_Engineering_Interview_Prep.md)** — Hosted vs. self-hosted models, prompting vs. fine-tuning vs. RAG, chunking and hybrid search, agent/tool-calling design and guardrails, LLM-as-judge, hallucination mitigation, prompt injection, and cost/latency management in production.

## Microservices & Architecture Patterns

- **[Microservices & Architecture Patterns Interview Prep](Microservices%20%26%20Architecture%20Patterns/Microservices_Architecture_Patterns_Interview_Prep.md)** — Service decomposition and bounded contexts, strangler fig migration, API Gateway/BFF/sidecar/service mesh, CQRS and event sourcing, CAP theorem, hexagonal/clean architecture, contract testing, and the distributed monolith.

## Design Patterns

*(reserved — classic GoF patterns and modern applications of them in real codebases)*

## Kubernetes, Docker & Cloud

*(reserved — containerization fundamentals, Kubernetes objects/scheduling/networking, cloud infrastructure trade-offs (AWS/GCP/Azure), CI/CD, and the deployment/operations concerns Forward Deployed and Staff loops both lean on heavily)*

## Frontend & Full-Stack

*(reserved — React/TypeScript fundamentals, browser/rendering performance, state management, and full-stack API integration concerns — the main gap for Full Stack Engineer loops)*

## Forward-Deployed & Customer-Facing Engineering

*(reserved — rapid prototyping under ambiguity, scripting and data wrangling against messy client data/systems, integrating with a customer's existing infrastructure, and the specific communication/expectation-setting skills these roles are actually screened on)*

## How to use this

Each question follows the same structure:

1. **How I'd say it** — a conversational, interview-ready explanation.
2. **Code / Framework** — a snippet or a decision framework/template to sketch on a whiteboard to back up the explanation.
3. **Where staff-level interviews push further** — the deeper follow-up that separates a mid-level answer from a staff-level one.
