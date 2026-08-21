# Kafka Deep-Dive Interview Prep

---

## 1. Core Concepts: Topics, Partitions, Offsets, Brokers, Producers, Consumers, Consumer Groups

- **Topic**: A named stream of records, logically split into **partitions**. Topics are the unit of organization (like a table).
- **Partition**: An ordered, immutable, append-only log. Each partition is the unit of parallelism and ordering — Kafka only guarantees order *within* a partition, not across a topic.
- **Offset**: A monotonically increasing integer identifying a record's position within a partition. Offsets are per-partition, not global to the topic.
- **Broker**: A single Kafka server that stores partitions and serves produce/fetch requests. A cluster is a set of brokers; each partition has one broker acting as **leader** and others as **followers** (replicas).
- **Producer**: A client that publishes records to a topic, choosing (or letting Kafka choose) which partition each record lands in.
- **Consumer**: A client that reads records from partitions, tracking its position via offsets.
- **Consumer Group**: A set of consumers that cooperatively consume a topic, where each partition is assigned to exactly one consumer *within* the group at a time. This is how Kafka achieves horizontal scaling of consumption while preserving per-partition order.

---

## 2. What Ordering Does Kafka Guarantee?

Kafka guarantees **strict ordering only within a single partition**. There is no ordering guarantee across partitions of the same topic. This is why partitioning strategy (i.e., your choice of message key) is the single biggest lever for correctness in ordering-sensitive systems.

---

## 3. How Message Keys Influence Correctness and Scalability

- If a key is provided, Kafka's default partitioner hashes the key to consistently route all records with that key to the **same partition**, preserving order for that key (e.g., all events for `orderId=123` land in one partition and are processed in order).
- If no key is provided, records are distributed round-robin (or via sticky partitioning in newer versions) for load balancing, but ordering across records is not guaranteed.
- **Trade-off**: keys give you ordering guarantees per entity but also create a scalability ceiling — a single hot key means a single partition absorbs all that load, and you can't parallelize consumption of that key beyond one consumer. Choosing a key is really choosing your unit of ordering vs. your unit of parallelism.

---

## 4. What Happens During a Consumer-Group Rebalance?

A rebalance is the process of reassigning partitions among the consumers in a group. It's triggered by:
- A consumer joining or leaving the group (including crashes or exceeding `max.poll.interval.ms`)
- A change in topic partition count
- A group coordinator failover

During a rebalance (in the classic **eager** protocol), all consumers in the group **stop consuming**, revoke all their assigned partitions, and the group coordinator reassigns partitions from scratch. This causes a "stop-the-world" pause across the entire group, even for consumers whose assignment doesn't change.

---

## 5. Eager vs. Cooperative Rebalancing

| | Eager Rebalancing | Cooperative (Incremental) Rebalancing |
|---|---|---|
| Behavior | All consumers revoke **all** partitions, then reassignment happens from scratch | Only partitions that actually need to move are revoked; unaffected consumers keep processing |
| Pause | Full stop-the-world for the whole group | Minimal disruption — only affected partitions pause |
| Protocol | `RangeAssignor`, `RoundRobinAssignor` (legacy default) | `CooperativeStickyAssignor` (recommended default since Kafka 2.4+) |
| Use case | Simpler, but costly at scale | Preferred for large consumer groups or latency-sensitive pipelines |

Cooperative rebalancing does this in two phases (revoke only what's needed, then reassign), reducing the "stop the world" blast radius significantly.

---

## 6. Static Consumer Memberships

Normally, a consumer that restarts (e.g., during a deploy) is treated as leaving and rejoining the group, triggering a rebalance. **Static membership** (via `group.instance.id`) lets a consumer register a persistent identity, so a brief restart within `session.timeout.ms` is treated as the *same* member returning — no rebalance is triggered. This is critical for reducing rebalance churn during rolling deployments of stateful consumers (e.g., Kafka Streams apps with local state stores).

---

## 7. At-Most-Once, At-Least-Once, and Exactly-Once Delivery

- **At-most-once**: Offset is committed *before* processing completes. If a crash occurs mid-processing, the message is lost — but never reprocessed. Lowest overhead, highest data-loss risk.
- **At-least-once**: Offset is committed *after* processing completes successfully. If a crash occurs after processing but before the commit, the message will be redelivered and reprocessed — duplicates are possible, but no data is lost. This is the most common default for production systems.
- **Exactly-once**: Achieved via Kafka transactions (idempotent producer + transactional writes) so that a "read-process-write" cycle either fully commits (data write + offset commit) or fully rolls back, atomically. True exactly-once only holds within the Kafka ecosystem (producer→topic→consumer); it doesn't automatically extend to external side effects like a database write or an API call unless you design for it explicitly (see Q8, Q15).

---

## 8. Why Must Consumers Remain Idempotent Even With Kafka Transactions?

Kafka transactions guarantee exactly-once **within Kafka** — atomic writes to topics plus atomic offset commits. But most real systems have consumers that produce **external side effects**: writing to a database, calling an API, sending an email. Kafka's transactional guarantee cannot make an external system's write atomic with the Kafka offset commit. If a crash happens after the external write but before the offset commit, the message will be redelivered, and the external side effect will fire again. So the consumer's business logic itself must be idempotent (e.g., upserts keyed by a unique event ID, deduplication tables) to be safe against redelivery, regardless of Kafka's internal guarantees.

---

## 9. Idempotent Producers vs. Transactional Producers

- **Idempotent producer** (`enable.idempotence=true`): Prevents **duplicate writes caused by producer retries** to a single partition. Kafka assigns each producer a unique ID (PID) and sequence numbers per partition; the broker deduplicates retried sends. Scope: single partition, single producer session.
- **Transactional producer**: Builds on idempotence to provide **atomicity across multiple partitions/topics** in one logical unit, including atomically committing consumer offsets alongside produced records (the "read-process-write" pattern). Requires a `transactional.id` and explicit `beginTransaction()`/`commitTransaction()` calls. Scope: multi-partition atomic writes, and is what actually enables the "exactly-once" processing pattern.

---

## 10. `acks`, Retries, `min.insync.replicas`, and Replication Factor

- **`acks`**: Controls how many broker acknowledgments a producer waits for before considering a send successful.
  - `acks=0`: Fire-and-forget, no acknowledgment — fastest, least durable.
  - `acks=1`: Leader acknowledges after writing locally — durable against most failures, but a leader crash before replication can lose data.
  - `acks=all` (or `-1`): Leader waits for all in-sync replicas to acknowledge — strongest durability.
- **`retries`**: Number of times the producer will resend a message on retriable errors (e.g., leader not available) before giving up.
- **`min.insync.replicas`**: The minimum number of replicas that must acknowledge a write for it to be considered successful when `acks=all`. If fewer than this are in sync, produces fail with `NotEnoughReplicasException`.
- **Replication factor**: The total number of copies of each partition maintained across brokers (leader + followers), set at topic creation. Determines fault tolerance — e.g., replication factor 3 can survive 2 broker failures without data loss.

---

## 11. Trade-Offs of `acks=all`

- **Pros**: Strongest durability guarantee — a write is only acknowledged once all in-sync replicas have it, so it survives leader failure.
- **Cons**: Higher latency (waiting on multiple replicas), lower throughput, and it introduces availability risk — if `min.insync.replicas` can't be met (e.g., too many replicas down), writes will fail rather than silently degrade. It's a deliberate trade of availability and latency for durability, and typically paired with `min.insync.replicas=2` and replication factor 3 as a standard durable configuration.

---

## 12. What Happens When a Producer Retry Changes Event Ordering?

Without idempotence, if `max.in.flight.requests.per.connection > 1` and a batch fails and is retried, a later batch might succeed and land on the broker *before* the retried earlier batch — reordering records within a partition. This is a classic ordering bug: retries alone don't guarantee order is preserved unless idempotence is enabled, which tracks sequence numbers per partition and lets the broker reject/reorder-correct out-of-sequence retries.

---

## 13. `max.in.flight.requests.per.connection` and Idempotence

- With idempotence **disabled**, setting `max.in.flight.requests.per.connection > 1` risks reordering on retry (Q12).
- With idempotence **enabled**, Kafka safely supports up to **5** in-flight requests per connection while still preserving ordering — the broker uses per-partition sequence numbers to detect and correctly order/reject out-of-order retries, so you get both throughput (pipelining multiple in-flight batches) and correctness. Above 5 in-flight requests, idempotence is not supported.

---

## 14. When Should an Offset Be Committed?

Only **after** the message has been fully and successfully processed (including any external side effects) — never before. Committing early risks message loss if a crash occurs mid-processing (moves you toward at-most-once); committing only after processing keeps you at at-least-once, which is the safer default absent full exactly-once design.

---

## 15. Crash After DB Commit But Before Offset Commit

This is the classic **dual-write problem**. The database now reflects the processed record, but Kafka doesn't know the offset was consumed, so on restart the consumer will re-fetch and reprocess the same message. Since the offset commit didn't happen, this is at-least-once behavior — the fix is **not** to try to make this atomic across two different systems naively, but to design the DB write to be idempotent (e.g., upsert by event ID, unique constraint on a dedup key) so reprocessing is safe. Some teams instead store the offset *inside* the same database transaction as the business write (transactional outbox pattern) to make the two atomic at the DB level.

---

## 16. Automatic vs. Synchronous vs. Asynchronous Offset Commits

- **Automatic** (`enable.auto.commit=true`): Offsets are committed periodically in the background by the client library, regardless of whether processing actually completed. Simplest, but risks committing offsets for messages that haven't finished processing (data loss on crash) or committing too late (duplicate processing) — not recommended when correctness matters.
- **Synchronous** (`commitSync()`): Explicit, blocking commit after processing. Guarantees the commit succeeded before continuing, but adds latency since the consumer blocks until the broker acknowledges.
- **Asynchronous** (`commitAsync()`): Explicit, non-blocking commit with a callback. Higher throughput, but requires careful handling of commit failures and out-of-order completions (typically combined with a final `commitSync()` on shutdown to guarantee the last commit lands).

---

## 17. What Happens When Processing Exceeds `max.poll.interval.ms`?

If the time between successive `poll()` calls exceeds this setting, the consumer is presumed dead/stuck by the group coordinator, and it is **forcibly removed from the group**, triggering a rebalance — even though the process itself may still be alive and working. This is a common production bug source with slow processing (e.g., long-running DB calls) — the fix is either to reduce work per poll batch (`max.poll.records`), offload processing to a separate thread while still polling for heartbeats, or increase the interval deliberately for known-slow workloads.

---

## 18. Handling Poison Messages

A poison message is one that consistently fails processing no matter how many times it's retried (e.g., malformed payload, unhandled edge case). Left unhandled, it blocks the partition indefinitely since the consumer can't advance past it. Standard approach:
1. Retry a bounded number of times (with backoff) to rule out transient failures.
2. After exhausting retries, route the message to a **dead-letter queue (DLQ)** rather than blocking the partition.
3. Commit the offset for the poison message so the consumer can move on, while preserving the message (and failure context) in the DLQ for investigation/replay.

---

## 19. Retry Topics vs. Delayed Retry vs. Blocking Retry vs. DLQs

- **Blocking retry**: Retry immediately, in-line, within the same consumer poll loop. Simple, but blocks the partition and delays all subsequent messages behind the failing one — poor for throughput.
- **Retry topic**: Failed messages are published to a separate `topic-retry` topic and reprocessed by a dedicated retry consumer, unblocking the main partition immediately.
- **Delayed retry**: A variant of the retry topic pattern where retries are intentionally delayed (e.g., `retry-5s`, `retry-30s`, `retry-5m` topics, or using scheduling/timestamp-based delay) to allow transient issues (a downstream service being briefly down) to resolve before reattempting, rather than hammering it immediately.
- **DLQ (Dead Letter Queue)**: The final destination after retries are exhausted — a place to preserve failed messages for manual inspection, alerting, and potential replay, without blocking the live pipeline.

In practice these are combined: blocking retry for a couple of quick attempts → retry topic with delay for a few more attempts → DLQ as the final fallback.

---

## 20. What Metadata Must a DLQ Record Preserve?

To make a DLQ actually useful for debugging and safe replay, each record should carry:
- **Original topic, partition, and offset** (to trace back to source)
- **Original key and value/payload** (unmodified, for exact replay)
- **Original headers** (any tracing IDs, correlation IDs)
- **Failure reason/exception** (stack trace or error message)
- **Retry count / attempt history**
- **Timestamp of original production and of failure**
- **Consumer group / service that failed to process it** (useful when multiple services share a DLQ)

Without this, a DLQ becomes an unusable graveyard — you can see *that* something failed but not *why* or *how to safely reprocess it*.

---

## 21. Designing Replay to Avoid Repeating Irreversible Side Effects

The core risk: replaying a DLQ or reprocessing from an earlier offset can re-trigger actions that shouldn't happen twice (e.g., charging a card, sending an email, decrementing inventory). Design principles:
- Make every side-effecting operation **idempotent** using a unique, stable identifier (event ID, idempotency key) so replays are safe by construction, not by luck.
- Track **processed-event state** (e.g., a dedup table keyed by event ID with a TTL) so the consumer can check "have I already done this?" before acting.
- For genuinely irreversible actions (payment capture, external API calls without idempotency support), use an **outbox/two-phase pattern**: write intent to a local transactional store first, and only perform the external call once, gated by that stored intent, so replay re-reads the stored decision rather than re-executing the action.
- Where the downstream system supports idempotency keys natively (e.g., Stripe), pass the Kafka event ID through as that key.

---

## 22. Schema Compatibility: Avro, Protobuf, JSON Schema

All three integrate with a **schema registry** to govern how producer and consumer schemas can evolve independently without breaking each other.
- **Avro**: Most mature Kafka ecosystem integration; schema evolution rules are well defined (see Q23); requires the writer's schema to be available for readers to resolve differences; compact binary format.
- **Protobuf**: Strong typing, cross-language codegen, good field-number-based evolution (fields identified by number, not position), increasingly common alongside Avro in the registry.
- **JSON Schema**: Human-readable, easier to debug and hand-author, but larger payloads and generally weaker enforced evolution tooling compared to Avro/Protobuf in most schema registries.

The choice usually comes down to ecosystem fit (existing services), payload size sensitivity, and whether cross-team schema governance tooling is more mature for one format in your registry.

---

## 23. Backward, Forward, and Full Compatibility

- **Backward compatible**: A **new schema** can read data written with the **old schema**. Enables upgrading consumers before producers (new consumer code can still read old messages). Typically achieved by only adding optional fields with defaults, or removing fields with defaults.
- **Forward compatible**: **Old schema** can read data written with the **new schema**. Enables upgrading producers before consumers (old consumer code can tolerate new messages). Achieved similarly but from the opposite direction of change.
- **Full compatible**: Both backward and forward compatible simultaneously — safest, most restrictive, allows producers and consumers to be upgraded in any order without coordination. Generally the recommended default for shared, high-fan-out topics where you don't control every consumer's deploy schedule.

---

## 24. How to Remove a Field From an Event Schema

Removing a field safely (without breaking compatibility) generally requires it to have had a **default value** in the schema. The safe sequence:
1. Stop relying on the field in producer logic first, if possible, while still emitting it (or emitting the default).
2. Confirm no consumers still require the field (audit consumer code/contracts).
3. Remove the field from the schema — this is backward compatible only if the field had a default (old readers using the new schema will just fall back to the default they already expect).
4. Deploy the schema change, then clean up any leftover default-handling logic once you've confirmed all consumers have moved on.

Removing a required field with no default is a breaking change and requires a coordinated migration (new topic/version, dual-write period, or full compatibility mode enforcement) rather than an in-place schema edit.

---

## 25. How to Migrate to a New Partitioning Key

Changing the partition key changes which partition entities land in, which breaks ordering guarantees for any in-flight or historical data keyed the old way. Safe migration pattern:
1. Create a **new topic** with the new key/partitioning scheme (you generally can't safely re-key an existing topic in place, since ordering history depends on the old key-to-partition mapping).
2. Dual-write to both old and new topics from the producer during a transition window.
3. Migrate consumers to the new topic incrementally, validating correctness (especially per-key ordering) against the new topic.
4. Backfill historical data into the new topic with the new keying if downstream systems need history under the new scheme.
5. Deprecate/retire the old topic once all consumers have cut over.

---

## 26. What Happens When the Number of Partitions Increases?

- Existing messages are **not redistributed** — Kafka only adds new empty partitions; it doesn't rebalance existing data across the new total.
- The **key-to-partition mapping changes** for all keys going forward (since the default partitioner hashes key mod partition count), which means a given key's *future* messages may land in a different partition than its *past* messages — breaking the "same key always same partition, thus ordering" guarantee across the increase.
- This is why partition count is usually treated as a decision to get right upfront, or one requiring careful, deliberate migration (similar to Q25) rather than a routine operational change for ordering-sensitive topics.

---

## 27. How to Diagnose Consumer Lag

Consumer lag is the delta between the latest produced offset and the consumer group's committed offset per partition. Diagnosis approach:
1. Check `kafka-consumer-groups.sh --describe` (or equivalent monitoring, e.g., Burrow, Datadog Kafka integration) to see per-partition lag, not just an aggregate — a single hot/stuck partition can hide behind a healthy-looking average.
2. Determine if lag is **growing** (consumer can't keep up — throughput problem) vs. **flat but nonzero** (consumer stalled entirely — check for rebalance loops, crashed consumer, or a stuck `poll()`).
3. Check consumer-side metrics: processing time per record, GC pauses, downstream call latency (DB, external API) — often the bottleneck is external, not Kafka itself.
4. Check for uneven partition assignment (some consumers idle, others overloaded) as a rebalancing/assignment strategy issue.
5. Check broker-side health (under-replicated partitions, ISR shrink) in case the bottleneck is actually on the produce side rather than consumption.

---

## 28. Why Is Consumer Lag Alone an Incomplete Health Metric?

- Lag measured in **message count** doesn't reflect actual time-to-process impact — 10,000 lagging tiny messages might be seconds behind, while 100 lagging huge/slow messages might represent an hour of backlog.
- A consumer can have **zero lag** and still be unhealthy — e.g., silently dropping/mishandling messages without erroring, or committing offsets prematurely, masking real failures.
- Lag doesn't tell you **why** — could be a slow downstream dependency, a stuck thread, an under-provisioned consumer group, or a broker-side issue; it's a symptom indicator, not a diagnosis.
- For latency-sensitive systems, lag should be paired with **time-based lag** (estimated by timestamp of last consumed record vs. now) and downstream SLA/error-rate metrics for a real health picture.

---

## 29. Retention vs. Compaction

- **Retention**: Deletes records after a configured time (`retention.ms`) or size threshold, regardless of key — appropriate for event streams where old data simply becomes irrelevant (e.g., clickstream events).
- **Compaction** (`cleanup.policy=compact`): Retains only the **latest record per key**, deleting older records with the same key over time (via a background compaction process), regardless of age — appropriate for representing current-state data (e.g., "latest known value for entity X") rather than a full event history.
- A topic can also use both (`compact,delete`) — compacting per key while still enforcing a maximum retention window.

---

## 30. What Guarantees Does a Compacted Topic Provide?

- For any given key, consumers reading from the start of the topic (or beginning of the log) are guaranteed to eventually see the **most recent value** for that key.
- Kafka guarantees it won't delete the **most recent** record for any key (until a tombstone — a record with a `null` value — marks that key for full deletion after `delete.retention.ms`).
- Kafka does **not** guarantee all intermediate historical updates for a key are preserved — compaction may collapse several updates into just the latest one, so compacted topics aren't reliable as a full audit log/event history, only as a "current state" store.
- Ordering within a partition is still preserved for whatever records remain post-compaction.

---

## 31. Reliable Database-to-Kafka Publication

This is the classic **dual-write problem** in reverse (writing to DB and Kafka as two separate systems). The standard reliable pattern is the **Transactional Outbox**:
1. Within the same database transaction as the business write, insert a row into an `outbox` table representing the event to be published.
2. A separate process (Change Data Capture tool like Debezium, or a polling publisher) reads the outbox table/CDC log and publishes to Kafka asynchronously.
3. Because the business write and the outbox write are in the same DB transaction, they're atomic — either both happen or neither does, eliminating the risk of updating the DB but failing to publish (or vice versa).
4. The publisher marks/deletes outbox rows once successfully published (or relies on CDC's own offset tracking), and downstream consumers should still be idempotent as a defense-in-depth measure.

---

## 32. Blue-Green Deployment of Kafka Consumers

Blue-green for consumers means running the new ("green") consumer version alongside the existing ("blue") version, validating it before cutting traffic over, then decommissioning blue. Unlike stateless HTTP services, this is trickier because you generally don't want *both* blue and green actively committing offsets and processing the same partitions simultaneously (double-processing). Common approach:
1. Deploy green as a **separate consumer group** (or shadow group) reading the same topic, so it doesn't affect blue's partition assignment or offsets.
2. Validate green's behavior/output against expectations without it driving real side effects (or with side effects to a sandboxed downstream system).
3. Once validated, cut over by stopping blue and letting green either take over the original consumer group ID (to inherit committed offsets) or start green as the primary group and decommission blue.

---

## 33. Preventing Green From Processing Production Messages Before Cutover

- Run green under a **distinct consumer group ID** so it doesn't compete for the same partition assignments as blue — this alone prevents accidental double-consumption of the primary group's work, but green will still independently read all messages.
- If green shouldn't have *any* real-world side effects yet, point its output/side-effecting integrations at **sandboxed or no-op endpoints** during validation (e.g., a test database, a mocked payment gateway) rather than relying on Kafka-level gating alone.
- Alternatively, use a **shadow-group** pattern where green reads and processes but explicitly suppresses/mocks external writes until a feature flag or config switch flips it to "live" — keeping the read path exercised for validation while gating only the side-effect path.

---

## 34. Same-Group vs. Shadow-Group vs. Separate-Topic Deployment Strategies

| Strategy | How it works | Risk/Trade-off |
|---|---|---|
| **Same-group** | Green joins the *same* consumer group as blue during rollout (e.g., rolling pod replacement) | Simplest, standard rolling deploy; but no real "compare old vs new" validation window — you're trusting the new version directly |
| **Shadow-group** | Green runs as a separate consumer group reading the same topic in parallel, purely for validation, side effects suppressed/mocked | Great for validating new logic against real traffic without risk; requires care that shadow doesn't accidentally trigger real side effects |
| **Separate-topic** | Producer dual-writes to both old and new topics (potentially different schema/partitioning); green consumes only the new topic | Useful when the change involves schema or partitioning changes too, not just consumer logic; more operational overhead (dual-write, sync issues) |

Choice depends on what's changing — pure consumer-logic changes fit same-group or shadow-group; changes involving schema/partitioning typically need separate-topic.

---

## 35. Migrating Between Kafka Clusters

1. **Set up cross-cluster replication** using a tool like MirrorMaker 2 (or Confluent Replicator) to continuously replicate topics, and importantly, consumer group offsets, from source to target cluster.
2. **Validate** data parity (message counts, checksums, lag) between clusters before cutover.
3. **Migrate producers first or consumers first**, depending on risk tolerance — commonly consumers are moved first (reading from the replicated target cluster) while producers still write to source, with replication bridging the gap, then producers are cut over once consumers are confirmed healthy on the target.
4. Handle **offset translation** carefully — offsets are not guaranteed identical across clusters after replication, so MirrorMaker 2's offset-sync mechanism (or manual translation) is needed so consumers resume from the correct logical position rather than an arbitrary one.
5. Run both clusters in parallel for a validation window, then decommission the source cluster once fully cut over.

---

## 36. How Backpressure and Overload Propagate Through an Event-Driven System

If a downstream consumer or dependency slows down, Kafka's durable log naturally **absorbs** the backpressure — messages simply accumulate as lag rather than the producer being blocked, unlike a synchronous system where a slow downstream directly stalls the caller. This is one of Kafka's biggest advantages (temporal decoupling), but it means overload doesn't fail loudly — it fails as *silently growing lag*, which can go unnoticed without proper lag alerting until it becomes a major backlog. In multi-hop pipelines, one stage's overload can cascade: consumer A lags → topic B (which A publishes to) sees delayed/bursty input → consumer of B experiences its own downstream pressure, and so on. Because Kafka doesn't push data to consumers (consumers pull at their own pace), producers rarely get direct backpressure signals from a slow consumer — that's both the resilience benefit and the observability risk of the model.

---

## 37. When Is Kafka the Wrong Messaging Technology?

- **Low-latency point-to-point RPC needs** — Kafka is built for durable streaming/pub-sub, not synchronous request/response; gRPC/REST fits better.
- **Complex routing logic** (e.g., content-based routing, priority queues, per-message TTL, task queues with fine-grained ack/nack semantics) — a broker like RabbitMQ is often a better fit than shoehorning this into topics/partitions.
- **Very small-scale or simple use cases** — Kafka's operational overhead (ZooKeeper/KRaft, partition management, rebalancing complexity) may not be justified for a low-throughput, simple queue need; SQS or a simpler queue may suffice.
- **Strict global ordering across an entire high-throughput topic** — Kafka only orders within a partition; if you truly need a single global order at high volume, that's a single-partition bottleneck, which defeats Kafka's scalability model.
- **Large payloads/blobs** — Kafka isn't designed for large binary payloads (videos, large files); better to publish a reference/pointer and store the blob elsewhere (S3, etc.).

---

## 38. Design: Ordering-Sensitive Payment Workflow Using Kafka

**Requirements**: strict per-account/per-transaction ordering, durability, exactly-once-ish processing, auditability.

- **Partitioning**: Key by `accountId` (or `paymentId` if cross-account ordering isn't required) so all events for a given account land in the same partition, preserving order for that account's transaction sequence.
- **Producer config**: `acks=all`, `enable.idempotence=true`, `min.insync.replicas=2`, replication factor 3 — durability and dedup on the write path.
- **Topic design**: Separate topics per event type (e.g., `payment-initiated`, `payment-authorized`, `payment-settled`) or a single `payment-events` topic with an event-type field, depending on how many distinct consumer groups need different subsets of the lifecycle.
- **Consumer**: Idempotent processing keyed by a unique `paymentEventId`, using a transactional outbox for any DB writes triggered by processing, and Kafka transactions if writing to multiple output topics (e.g., emitting a downstream `ledger-updated` event atomically with consuming the input).
- **Failure handling**: Bounded retries → delayed retry topic → DLQ with full metadata (Q19/Q20), since payment failures need investigation, not silent drops.
- **Reconciliation**: A periodic batch reconciliation job comparing Kafka-driven state against the source-of-truth ledger, since financial correctness typically warrants defense-in-depth beyond streaming guarantees alone.

---

## 39. Design: Replay Strategy for Correcting a Faulty Consumer Deployment

**Scenario**: A buggy consumer deployment processed messages incorrectly for some window of time, and you need to reprocess that window correctly after fixing the bug.

1. **Identify the blast radius**: Determine the exact time range / offset range affected using deployment timestamps correlated against offsets (or a monitoring system tracking offsets-over-time).
2. **Fix and deploy the corrected consumer** first, validated against a shadow group or staging environment before touching production replay.
3. **Reset offsets** for the affected consumer group back to the start of the affected range (`kafka-consumer-groups.sh --reset-offsets`), or better, replay via a separate temporary consumer group reading that same range, to avoid disrupting the live group's current position.
4. **Ensure idempotency** of all downstream writes (Q21) so reprocessing the window doesn't double-apply already-correct side effects from records that were actually fine.
5. **Validate output** against expected state (row counts, checksums, spot checks) before considering the replay complete.
6. **Document and alert** on the incident window so downstream consumers of *your* output (if any) are aware data in that range was corrected.

---

## 40. Metrics and Alerts for a Critical Kafka Pipeline

**Broker-level**
- Under-replicated partitions (should be 0 — indicates replication risk)
- Active controller count (should always be exactly 1)
- Request handler / network thread idle ratio (saturation indicator)
- Disk usage / log size growth rate

**Producer-level**
- Request latency (p50/p95/p99)
- Error rate / retry rate
- Batch size and compression ratio (efficiency)

**Consumer-level**
- **Consumer lag** (both message-count and time-based, per partition — Q28)
- Rebalance frequency/duration (frequent rebalances indicate instability)
- Processing time per record / per batch
- Commit failure rate

**Topic-level**
- Message production rate vs. consumption rate (delta trend)
- Partition count vs. leader distribution (skew detection)

**Alerting priorities for a critical/financial pipeline**: under-replicated partitions > 0, consumer lag exceeding a time-based SLA threshold (not just count), DLQ record rate spike, consumer group rebalance loops, and any drop in production rate to near-zero (silent producer failure) — each tied to a runbook, not just a dashboard.
