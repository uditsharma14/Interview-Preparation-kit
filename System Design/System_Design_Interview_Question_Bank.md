# System Design Interview Question Bank

> **Format:** Practice prompts, not full worked answers — pair this with [Transactions](Transactions_Interview_Prep.md), [Kafka](Kafka_Interview_Prep.md), [Redis & Caching](Redis_Caching_Interview_Prep.md), [REST API Design](REST_API_Design_Interview_Prep.md), and [Cross-Stack Design Scenarios](Cross_Stack_Design_Scenarios_Interview_Prep.md) for the underlying technical depth each prompt draws on. **Target level:** Senior → Staff → Principal, plus a Forward Deployed Engineer track. **Last verified:** 2026-08-22.

Strong system-design prompts to rehearse for Senior, Staff, Principal, or Forward Deployed Engineer interviews — organized by theme, with a recommended answer structure and the follow-up questions a Principal-level interviewer is likely to press on.

## Core system-design questions

1. Design a URL-shortening service.
2. Design a distributed rate limiter.
3. Design a notification platform supporting email, SMS, and push.
4. Design a real-time chat system.
5. Design a large-scale file-storage service.
6. Design an API gateway.
7. Design a distributed job scheduler.
8. Design a feature-flag platform.
9. Design a metrics and alerting system.
10. Design a multi-tenant SaaS platform.

## Distributed transactions and payments

1. Design an order-processing system using Saga.
2. Design a payment-processing platform.
3. Design a wallet and ledger system.
4. Design an idempotent payment API.
5. Design a refund and chargeback workflow.
6. Design a settlement and reconciliation platform.
7. Design a double-entry accounting ledger.
8. Design cross-service consistency without 2PC.
9. Design a transactional-outbox platform using Debezium and Kafka.
10. Handle a permanently failed Saga compensation.
11. Prevent duplicate charges during retries.
12. Reconcile internal transactions with an external payment provider.
13. Design a multi-region, high-availability payment system.

## Event-driven architecture

1. Design an event-streaming platform using Kafka.
2. Guarantee ordering for events belonging to one account.
3. Handle duplicate, missing, and out-of-order events.
4. Design retry topics and dead-letter processing.
5. Evolve event schemas without breaking consumers.
6. Recover after a Kafka consumer partially processes a message.
7. Design event replay and backfill.
8. Scale consumers with highly uneven partition traffic.
9. Design an event-driven audit trail.
10. Migrate from synchronous APIs to event-driven services.

## Data-intensive systems

1. Design a search autocomplete service.
2. Design a semantic-search platform.
3. Design a change-data-capture pipeline.
4. Design a multi-tenant analytics platform.
5. Design a distributed cache.
6. Design an append-only event store.
7. Select SQL versus NoSQL for a high-volume workload.
8. Shard a database while preserving aggregate consistency.
9. Handle a hot tenant or hot partition.
10. Perform a zero-downtime database migration.

## AI and Forward Deployed Engineering

See also [AI Engineering Interview Prep](../AI%20Engineering/AI_Engineering_Interview_Prep.md) for the underlying technical depth (RAG, evals, agent/tool-calling design, prompt injection) these prompts assume.

1. Design an enterprise RAG platform.
2. Design a customer-support AI assistant.
3. Design an incident-investigation copilot.
4. Ingest data from SharePoint, Google Drive, wikis, and APIs.
5. Design document-level access control for RAG.
6. Evaluate retrieval and answer quality.
7. Prevent hallucinations in a regulated workflow.
8. Design prompt and model versioning.
9. Support multiple LLM providers with failover.
10. Control latency and token cost.
11. Add human approval for high-risk actions.
12. Monitor an agentic workflow in production.
13. Handle prompt injection from retrieved documents.
14. Deploy an AI solution inside a customer-controlled environment.
15. Convert one customer's solution into a reusable platform capability.

## Forward-deployed scenarios

These test customer delivery and judgment, not merely architecture — see also the reserved [Forward-Deployed & Customer-Facing Engineering](../Forward-Deployed%20%26%20Customer-Facing%20Engineering/README.md) section.

1. A customer wants production deployment in four weeks, but requirements are unclear. How do you proceed?
2. A prototype performs well in demos but fails on real customer data. What do you do?
3. Customer security blocks your preferred architecture. How do you redesign it?
4. Product requirements conflict with the customer's operational workflow. How do you resolve the conflict?
5. Customer data cannot leave its private network. Design the deployment.
6. The customer requests a one-off feature that could fragment the product. How do you decide?
7. Adoption is low even though the system is technically successful. How do you investigate?
8. A production launch is approaching, but evaluation quality remains below target. Do you delay?
9. Several customer deployments need similar customizations. What should become platform functionality?
10. Explain a complex tradeoff to customer leadership without hiding technical risk.

## Principal-level follow-ups

Expect the interviewer to challenge your first design:

- What are the critical business invariants?
- What consistency model is required?
- What is the system of record?
- Where are the transaction boundaries?
- What happens during a partial failure?
- How are retries made idempotent?
- How is data reconciled after an outage?
- What breaks at 10× or 100× traffic?
- How do you migrate without downtime?
- How do you prevent one tenant from affecting others?
- How do you meet disaster-recovery objectives?
- How do you control operational cost?
- How do you audit sensitive actions?
- What should be built now versus deferred?
- How would a five-person team deliver this incrementally?

## Recommended answer structure

Use this sequence during an interview:

1. Clarify users, use cases, scale, and constraints.
2. Establish functional and nonfunctional requirements.
3. Identify business invariants.
4. Define APIs and core data models.
5. Present the high-level architecture.
6. Walk through the primary request flow.
7. Explain consistency and transaction boundaries.
8. Cover failures, retries, idempotency, and reconciliation.
9. Address scaling, partitioning, caching, and hot spots.
10. Cover security, observability, deployment, and disaster recovery.
11. State tradeoffs and an incremental delivery plan.

## Priority prompts for a payments / event-driven / AI-platform background

If your background leans payments, event-driven systems, and AI platform work, prioritize these five:

1. Design a payment authorization and settlement platform.
2. Design an order workflow using Saga, outbox, Debezium, and Kafka.
3. Design a multi-region wallet-provisioning platform.
4. Design an enterprise RAG and incident-intelligence system.
5. Design a customer deployment that must run inside a regulated private environment.
