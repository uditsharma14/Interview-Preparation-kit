# Interview Preparation Kit

A collection of deep-dive, mid-to-staff-level interview prep notes for technical interviews. Each topic is written as a set of Q&A entries with the answer phrased the way it would actually be said out loud in an interview, backed by code snippets and pointers to where staff-level follow-up questions tend to go.

Content is organized into three broad folders rather than one-per-topic subfolders:

## Programming Language

- **[Java Collections Interview Prep](Programming%20Language/Java_Collections_Interview_Prep.md)** — `HashMap`/`TreeMap`/`LinkedHashMap` internals, concurrent collections, boxed-collection costs, and production leak diagnosis.
- **[Java Concurrency Interview Prep](Programming%20Language/Java_Concurrency_Interview_Prep.md)** — Visibility/atomicity/ordering, locks, virtual threads, executors, `ForkJoinPool`, the ABA problem, and structured concurrency.
- **[Java JVM & GC Interview Prep](Programming%20Language/Java_JVM_GC_Interview_Prep.md)** — Memory areas, JIT/escape analysis, reference types, G1/ZGC/Shenandoah, container OOM-kills, and native memory.
- **[Spring Boot Internals Interview Prep](Programming%20Language/Spring_Boot_Internals_Interview_Prep.md)** — `SpringApplication.run()` internals, bean lifecycle, auto-configuration, AOP proxies and self-invocation, graceful shutdown, and execution models.
- **[Spring Security & OAuth2 Interview Prep](Programming%20Language/Spring_Security_OAuth2_Interview_Prep.md)** — Filter chain architecture, CSRF/CORS, OAuth2 flows and PKCE, JWT validation and key rotation, token storage, BOLA, and multi-tenant authorization.
- **[JPA & Hibernate Interview Prep](Programming%20Language/JPA_Hibernate_Interview_Prep.md)** — Entity lifecycle, dirty checking and flushing, N+1 diagnosis and fixes, fetch strategies, optimistic/pessimistic locking, ID generation and batching, and DTO boundaries.

## System Design

- **[Kafka Deep-Dive Interview Prep](System%20Design/Kafka_Interview_Prep.md)** — Topics, partitions, offsets, ordering guarantees, message keys, and consumer group rebalancing.
- **[REST API Design Interview Prep](System%20Design/REST_API_Design_Interview_Prep.md)** — Resource modeling, idempotency and retries, pagination strategies, versioning and backward compatibility, error formats, async workflows, and rate limiting.
- **[Transactions Interview Prep](System%20Design/Transactions_Interview_Prep.md)** — ACID and isolation levels, MVCC, Spring propagation types, deadlocks, the transactional outbox pattern, sagas vs. two-phase commit, and zero-downtime schema migration.

## Engineering Leadership

*(reserved for Lead/Staff engineering and technical leadership content)*

## How to use this

Each question follows the same structure:

1. **How I'd say it** — a conversational, interview-ready explanation.
2. **Code** — a snippet to sketch on a whiteboard or IDE to back up the explanation.
3. **Where staff-level interviews push further** — the deeper follow-up that separates a mid-level answer from a staff-level one.
