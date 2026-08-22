# Cross-Stack Staff-Level Design Scenarios — Interview Prep (with Code & Sources)

> **Target level:** Staff · **Baseline:** inherits the baseline of whichever guide each scenario draws on (Java, Spring Boot, Spring Security, JPA, Transactions, Redis, Kafka, REST API Design — see each file's own header) · **Last verified:** 2026-08-22 · **Prerequisites:** the rest of this kit — these scenarios deliberately assume it

How to use this: each question has **the answer the way I'd actually say it out loud** in an interview, a **sketch/diagram or checklist** you could draw on a whiteboard to back it up, and **where the follow-up goes if you're in a Staff-level loop** — these scenarios deliberately span the other files in this kit (Java, Spring, Security, JPA, Transactions, Redis, Kafka, REST API Design), because that's exactly how they show up in a real Staff-level interview: as one messy, cross-cutting problem, not a single-topic question.

---

## 1. Design an Order-Processing Platform Using Spring Boot, PostgreSQL, Redis, and Kafka

**Answer:**

"I'd start from the business operation, not the technology list: 'place an order' needs to (1) validate and record the order durably, (2) reserve inventory, (3) charge payment, (4) notify downstream systems (shipping, analytics, notifications) — and I'd map each of those onto the right tool rather than assuming every piece of infrastructure listed needs to be involved in every step.

**PostgreSQL** owns the durable, transactional state — the order record itself, inventory counts, payment records — anything where ACID guarantees (Transactions category) genuinely matter. **Redis** sits in front of PostgreSQL purely as a cache for read-heavy, latency-sensitive paths (product catalog lookups, a user's order history summary) — never as the source of truth for anything transactional, per the Redis file's question 1 distinction. **Kafka** decouples the order-placement flow from everything that doesn't need to happen synchronously within the request — inventory reservation and payment can be orchestrated as a saga (Transactions category, question 23) with each step's completion published as an event, and shipping/notifications/analytics are pure downstream consumers of those events, entirely decoupled from the request path and from each other.

The order write path itself uses the transactional outbox pattern (Transactions category, question 19) to atomically commit the order record and the 'start the saga' event in one PostgreSQL transaction, avoiding the classic 'committed to the database but never published to Kafka' gap."

**Code:**

```text
                         ┌─────────────┐
   Client -- POST /orders --> Spring Boot API --> PostgreSQL (order + outbox row,
                         └─────────────┘             ONE atomic transaction)
                                                            |
                                                   Debezium/relay reads outbox
                                                            |
                                                            v
                                                    Kafka: order-events
                                                    /          |          \
                                          Inventory Svc   Payment Svc   Notification Svc
                                          (saga step)      (saga step)   (pure consumer,
                                                                          decoupled)

   Redis: sits in FRONT of PostgreSQL for reads only (product catalog,
   order-history summaries) — never the authoritative store for order/
   payment/inventory state
```

**Follow-up:**

I'd walk through the failure modes deliberately, since that's what actually distinguishes a Staff-level answer here: what happens if payment fails after inventory is reserved (saga compensation, Transactions category question 23); what happens if a customer retries a timed-out order-creation request (idempotency key, REST API Design file question 5); what happens if Redis is completely unavailable (graceful degradation to PostgreSQL directly, Redis file question 28, with the corresponding database-capacity-under-full-load question the Redis file's question 30 incident illustrates); and how a downstream consumer (notifications) being slow or down doesn't block the order-placement request path at all, since it's a pure async consumer of already-committed events, not a synchronous dependency.

**Source:** [Chris Richardson — Saga Pattern](https://microservices.io/patterns/data/saga.html), [Chris Richardson — Transactional Outbox Pattern](https://microservices.io/patterns/data/transactional-outbox.html)

---

## 2. How Would You Guarantee That an Accepted REST Request Eventually Produces Exactly One Business Outcome?

**Answer:**

"'Exactly one business outcome' is a stronger, more precise framing than 'exactly-once delivery' — it's really about idempotency at every layer the request's effect passes through, not about achieving some impossible distributed-systems guarantee of literal single delivery everywhere.

I'd apply idempotency at each hop independently: at the **API layer**, an idempotency key (REST API Design file, question 5) lets the client safely retry an ambiguous (timed-out) request without risking a duplicate order/charge — the server recognizes a repeated key and returns the original result rather than reprocessing. At the **database layer**, the actual business operation is wrapped in a single local transaction with appropriate constraints (a unique constraint on the idempotency key itself, or on a natural business key) so even a race between two near-simultaneous 'duplicate' requests resolves correctly (Transactions category, question 17's constraints-as-last-line-of-defense). At the **messaging layer**, if the outcome triggers downstream event processing, every consumer is built to be idempotent against redelivery (Transactions category, question 25 and Kafka category's consumer-idempotency principle), tracking processed event IDs rather than assuming Kafka's own delivery guarantees are sufficient on their own.

The overall design principle: don't chase 'exactly-once' as a transport-level guarantee anywhere in the chain (it's either unavailable or prohibitively expensive at several of these hops) — instead, make every hop idempotent, so that however many times a message or request is actually delivered/retried, the *net business effect* is the same as exactly once."

**Code:**

```text
Client --(Idempotency-Key: abc-123)--> API
  -> DB: INSERT with UNIQUE constraint on idempotency_key
     -> if duplicate: return the ORIGINAL stored result, no reprocessing
  -> Outbox event published, ONCE, atomically with the DB write
     -> Consumer: checks processed_event_id before acting
        -> if already processed: no-op
        -> if not: process AND record the event_id, atomically, together

Net effect: regardless of how many times the client retries, or how many
times Kafka redelivers, the actual business outcome (one order, one charge,
one shipment) happens EXACTLY ONCE, even though NO individual hop in the
chain provides a true "exactly-once" guarantee on its own
```

**Follow-up:**

I'd bring up that this is exactly the "idempotency all the way down" principle, and that it's a more robust, more achievable design goal than trying to eliminate duplicates at the source — trying to prevent every possible retry/redelivery from ever happening is fighting the fundamental nature of unreliable networks and distributed systems, whereas making every hop tolerant of duplicates is a tractable, well-understood engineering problem with established patterns at each layer, which is exactly why this whole interview bank keeps returning to idempotency as the unifying answer across REST, Transactions, and Kafka categories independently.

**Source:** [Stripe API — Idempotent Requests](https://stripe.com/docs/api/idempotent_requests), [Chris Richardson — Idempotent Consumer](https://microservices.io/patterns/communication-style/idempotent-consumer.html)

---

## 3. Design a Multi-Region Service and State the Consistency Trade-Offs Explicitly

**Answer:**

"I'd start by rejecting the premise that there's one universally-correct multi-region architecture — the right design depends entirely on the actual consistency requirements of the *specific data* involved, which usually varies within the same system, so I'd design per-data-type rather than picking one global strategy.

For data that can tolerate eventual consistency (product catalogs, user profile data, most read-heavy content) — **active-active** with asynchronous cross-region replication: every region can read and write locally, with changes propagating to other regions asynchronously. This gives the best latency (no cross-region round trip on the write path) at the cost of a real, explicit inconsistency window between regions, and the corresponding need to handle conflicting concurrent writes to the same record from two different regions (last-write-wins based on a timestamp, or a more sophisticated CRDT-based merge for data that supports it).

For data requiring strong consistency (financial transactions, inventory counts where overselling is a real business risk) — **active-passive** with a single authoritative region for writes (all writes route to one region, synchronously or near-synchronously replicated to others for read scaling/disaster recovery, but never accepting a conflicting concurrent write from a different region) — trading multi-region write latency and availability-during-a-region-outage for genuine consistency.

I'd state the trade-off explicitly, in CAP-theorem terms but grounded in the actual business consequence: active-active/eventually-consistent data means the business is accepting that a network partition between regions can produce genuinely conflicting writes that need reconciliation; active-passive/strongly-consistent data means the business is accepting that a regional outage of the single write-authoritative region makes writes for that data entirely unavailable everywhere, not just in the affected region, until failover completes."

**Code:**

```text
Active-Active (eventual consistency) — e.g., product catalog:
  Region US <--async replication--> Region EU <--async replication--> Region APAC
  - writes accepted LOCALLY in each region, low latency
  - conflicting writes to the SAME record in two regions: resolved via
    last-write-wins (timestamp) or CRDT merge
  - trade-off: a real inconsistency window exists between regions

Active-Passive (strong consistency) — e.g., account balance / inventory:
  Region US (WRITE-AUTHORITATIVE) --sync/near-sync replication--> Region EU (READ ONLY)
  - ALL writes route to US, regardless of which region the request originated in
  - trade-off: a US region outage means writes are UNAVAILABLE EVERYWHERE,
    not just in US, until failover promotes a new write-authoritative region
```

**Follow-up:**

I'd bring up that this decision genuinely needs to be made **per data type**, not once for the whole system — a real multi-region e-commerce platform might run its product catalog active-active (eventual consistency is fine — a customer seeing a slightly stale description for a few seconds across regions is a non-issue) while running its payment/inventory subsystem active-passive (a customer in one region overselling the same physical inventory unit as a customer in another region, due to eventually-consistent replication, is a genuine business problem) — and I'd walk through exactly why a single, uniform "we're active-active" or "we're strongly consistent" answer for an entire platform is usually the wrong level of granularity for this decision.

**Source:** [Martin Kleppmann — Designing Data-Intensive Applications, Ch. 5 (Replication)](https://dataintensive.net/), [AWS — Multi-Region Application Architecture](https://aws.amazon.com/blogs/architecture/tag/multi-region/)

---

## 4. Design a Zero-Downtime Deployment Involving Database, Cache, API, and Event-Schema Changes

**Answer:**

"I'd apply the expand/contract pattern independently at each of the four layers, sequenced so that at every point during the rollout, old and new application versions can coexist and both function correctly against whatever state each layer is currently in — since a rolling deployment inherently means both versions run simultaneously for some window.

**Database** (Transactions category, question 29): expand — add new columns/tables alongside old, dual-write from the new app version; migrate reads gradually; contract — remove old structures only once fully migrated and verified. **Cache** (Redis file, question 25): version cache keys so old and new app versions never read/write each other's cached shapes. **API** (REST API Design file, questions 14-16): add new fields/endpoints additively; never remove or change the meaning of anything the currently-deployed old version's clients depend on until they're confirmed migrated. **Event schema** (Kafka category): apply the same additive-first discipline — new optional fields, never repurposing or removing an existing field until every consumer is confirmed to have migrated off it, using the specific compatibility mode (backward/forward/full) the schema registry enforces.

The unifying principle across all four: **never make a single-step destructive change to anything a currently-running old version depends on**, because a rolling deployment guarantees old and new code run simultaneously for some real window — treat that window as a first-class design constraint at every layer, not an inconvenient detail to route around."

**Code:**

```text
Sequencing across a single deployment, ALL FOUR layers additive-first:

  1. DB migration (expand): new column added, nullable, old app version unaffected
  2. Event schema (expand): new optional field added to the event schema
  3. Deploy NEW app version:
       - writes to BOTH old and new DB columns (dual-write)
       - writes cache entries under a NEW versioned key
       - publishes events with the new optional field populated
       - OLD app version instances, still running during rollout, are
         UNAFFECTED by any of the above — they don't know these new
         elements exist, and don't need to
  4. Old app version instances fully scaled down / rollout complete
  5. Verify: confirm (via metrics/usage) NOTHING still depends on old
     column / old cache key version / absent event field
  6. Contract: remove old DB column, allow old cache keys to age out via
     TTL, mark the event schema field as no-longer-optional if appropriate
```

**Follow-up:**

I'd emphasize that the actual hard part isn't designing each layer's expand/contract sequence in isolation — it's correctly **sequencing across layers**, since a mistake in ordering (e.g., publishing an event with a new required field before every consumer's schema-registry-enforced compatibility check has been updated to accept it) can break things even if each individual layer's own migration was internally correct. I'd advocate for a written, reviewed rollout plan explicitly listing the order of operations across all four layers for any deployment non-trivial enough to touch more than one of them simultaneously, treating this sequencing as a genuine design artifact worth reviewing before executing, not something improvised during the deployment itself.

**Source:** [Martin Fowler & Pramod Sadalage — Evolutionary Database Design](https://martinfowler.com/articles/evodb.html), [Confluent — Schema Evolution and Compatibility](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html)

---

## 5. A Deployment Doubles Database Traffic Without Changing Request Volume. How Do You Investigate?

**Answer:**

"Since request volume is unchanged but database traffic doubled, the cause is almost certainly something in the deployed code generating more queries **per request** than before, or a cache-effectiveness regression pushing traffic that used to be absorbed elsewhere onto the database — not a capacity/scaling issue. I'd start by diffing the deployment: what actually changed in this specific release, and does the change touch anything data-access-related (a new JPA entity relationship, a fetch-strategy change, a modified query, a cache-key or TTL change).

My concrete investigation sequence: check the **query count per request** (via Hibernate statistics, JPA/Hibernate file question 25, or APM tooling) for the specific endpoints seeing the traffic increase, comparing before/after the deployment — this immediately tells me if it's an N+1 regression (JPA/Hibernate file question 7) freshly introduced by this deploy. In parallel, check **cache hit rate** (Redis file question 29) for a sudden drop correlating with the deployment — a cache-key-versioning miss (Redis file question 25, and the exact incident in Redis file question 30) where a serialization-format or cache-key change silently broke cache effectiveness is a very common, specific match for exactly this symptom shape."

**Code:**

```text
Investigation checklist, in the order I'd actually run it:

  1. What changed in THIS deployment? (git diff / release notes) — does it
     touch entity relationships, fetch strategies, cache keys/TTLs, or
     query logic AT ALL?
  2. Query-count-per-request, BEFORE vs AFTER this deploy, for the specific
     endpoints showing increased DB load (Hibernate statistics / APM)
       -> if N per request went from ~2 to ~2+N(collection size): N+1 regression
  3. Cache hit rate, BEFORE vs AFTER this deploy, segmented per feature/key-prefix
       -> if it collapsed near this deploy's timestamp: cache-key-version /
          serialization-format mismatch (exactly the Redis file's incident shape)
  4. If neither of the above: check for a NEW scheduled job / batch process
     introduced in this deploy that wasn't present before, running independently
     of the request path but adding to overall DB load
```

**Follow-up:**

I'd bring up that the fastest way to actually distinguish "N+1 regression" from "cache-effectiveness regression" is precisely the segmented, per-feature monitoring both the JPA/Hibernate and Redis files independently recommend as a *standing* practice, not something built ad hoc during an incident — if that instrumentation already exists, this investigation takes minutes; if it doesn't, the incident itself becomes the forcing function to add it, and I'd treat "add this instrumentation" as a mandatory action item coming out of the postmortem regardless of which specific root cause this particular incident turns out to have.

**Source:** [Hibernate ORM User Guide — Statistics](https://docs.jboss.org/hibernate/orm/current/userguide/html_single/Hibernate_User_Guide.html#statistics), [Redis Documentation — INFO command](https://redis.io/docs/latest/commands/info/)

---

## 6. Kafka Lag Grows While CPU and Database Usage Remain Low. What Hypotheses Would You Test?

**Answer:**

"Growing lag with low CPU and low database load is a strong signal that the consumer isn't *compute-bound* or *database-bound* — it's most likely **blocked/waiting** on something, or structurally under-provisioned in a way that has nothing to do with raw processing capacity. I'd test hypotheses in order of likelihood.

First: **consumer count versus partition count** — if there are fewer active consumer instances than partitions, some partitions simply have no consumer assigned and their lag grows by definition, regardless of how idle the ones that *are* consuming are; this is a trivially checkable, very common root cause. Second: **an external, non-database dependency call inside the message-processing loop** that's slow or occasionally hanging (a downstream HTTP call, an external API) — this would show low CPU (the consumer thread is blocked waiting, not computing) and low database load (the bottleneck isn't the database at all), exactly matching the symptom. Third: **frequent, unnecessary rebalances** (Kafka category) — if consumers are being kicked out of the group and rejoining repeatedly (a `max.poll.interval.ms` violation from occasionally-slow processing, or unstable consumer health), the group spends meaningful time paused during each rebalance, accumulating lag even though no single message is actually slow to process. Fourth: **a single poison message or a few disproportionately expensive messages** stalling one partition's consumer specifically, while the metrics I'm looking at are aggregated across all partitions and hiding a per-partition problem."

**Code:**

```text
Hypothesis-testing checklist, in order:

  1. Consumer instance count vs partition count — any UNASSIGNED partitions?
     (kafka-consumer-groups.sh --describe)
  2. Thread dump / profiling on a consumer instance DURING the lag window —
     is the processing thread BLOCKED (on I/O, a lock, an external call)
     rather than busy computing? (low CPU + blocked thread = waiting, not working)
  3. Rebalance frequency — check consumer group logs for repeated
     "Attempt to heartbeat failed" / rebalance events correlating with the
     lag growth window
  4. PER-PARTITION lag, not just aggregate group lag — is ONE specific
     partition disproportionately behind (pointing at a poison message or
     a hot-partition-specific slow dependency), while others are fine?
```

**Follow-up:**

I'd bring up that "low CPU, low DB usage, growing lag" is almost a textbook signature for a blocked-on-I/O consumer thread specifically, and a thread dump taken *during* the lag window (not after the fact) is the single highest-value diagnostic step — it directly shows whether the processing thread is stuck waiting on something, and what, rather than requiring me to guess from aggregate metrics alone. I'd also connect this to the concurrency file's ForkJoinPool-blocking discussion as a reminder that "low CPU" specifically rules out compute-bound causes but says nothing about I/O-bound blocking, which is exactly the category this symptom shape points toward.

**Source:** [Kafka Documentation — Consumer Configs](https://kafka.apache.org/documentation/#consumerconfigs), [Confluent Documentation — Monitor Consumer Lag](https://docs.confluent.io/platform/current/monitor/monitor-consumer-lag.html)

---

## 7. Redis Fails During Peak Traffic. How Do You Prevent a Database Collapse?

**Answer:**

"This is precisely the failure mode from the Redis file's question 30 incident, and the prevention has to be designed and tested **before** it happens, not improvised during the outage. The core risk: if every request that would normally hit the cache instead falls through to the database simultaneously (the graceful-degradation fallback from Redis file question 28, applied at full traffic volume), the database can be hit with far more load than it was ever sized or tested for, since it had been architecturally relying on the cache absorbing the bulk of read traffic.

My prevention approach, layered: first, **load-shed at the application layer** rather than letting every request fall through unconditionally — a circuit breaker around the cache-fallback path that, once database latency/error rate crosses a threshold, starts rejecting a portion of requests fast (REST API Design file, question 21) rather than letting all of them queue up against an increasingly overwhelmed database. Second, **request coalescing** for the fallback path specifically (Redis file question 6's stampede-prevention pattern, applied here to 'the entire cache is gone' rather than just one hot key expiring) — if many concurrent requests for the same data all miss the cache simultaneously during the outage, coalesce them into one database query rather than each hitting the database independently. Third, and most important as a *preventive* rather than reactive measure: **actually load-test the 'cache is completely gone' scenario ahead of time** (a deliberate game-day exercise) to know, in advance, whether the database can survive full fallback traffic at all — if it can't, the real fix is either provisioning additional database read capacity specifically sized for this scenario, or accepting and designing for a deliberate, controlled degraded-service mode (serving stale/cached-at-the-edge data, or shedding non-critical read traffic) rather than discovering the database's actual limit during a real incident."

**Code:**

```java
@CircuitBreaker(name = "database-fallback", fallbackMethod = "serveDegraded")
Product getProduct(String id) {
    try {
        return cache.get(id); // normal path
    } catch (RedisConnectionFailureException e) {
        return productRepository.findById(id).orElseThrow(); // fallback —
    }                                                            // but PROTECTED
}                                                                    // by the circuit
                                                                       // breaker wrapping
                                                                        // this whole method,
                                                                         // not unconditional

Product serveDegraded(String id, Exception ex) {
    return staleLocalFallbackCache.getIfPresent(id); // once the circuit OPENS
}                                                        // (database itself now
                                                           // struggling), serve
                                                            // whatever LAST-KNOWN-GOOD
                                                             // data is available locally,
                                                              // rather than adding to
                                                               // database load further
```

**Follow-up:**

I'd bring up that the single most valuable thing a team can do here isn't a specific code pattern — it's actually running the game-day exercise (deliberately taking Redis offline in a staging/canary environment under realistic load and observing what genuinely happens) before it's forced on them by a real production incident, since that's the only way to know with confidence whether the fallback-plus-circuit-breaker design actually holds under real traffic, rather than looking correct in code review but failing in ways nobody anticipated once actually exercised at scale.

**Source:** [Google SRE Workbook — Handling Overload](https://sre.google/sre-book/handling-overload/), [Resilience4j — Circuit Breaker](https://resilience4j.readme.io/docs/circuitbreaker)

---

## 8. A Service Sometimes Publishes Events Without Committing Its Database Update. Fix the Architecture.

**Answer:**

"This is the exact anomaly the transactional outbox pattern exists to eliminate structurally (Transactions category, questions 18-19), and 'sometimes' publishes without committing tells me the current implementation is almost certainly doing a direct Kafka publish either before the database commit, or immediately after it but outside any atomicity guarantee with it — both of the broken patterns described in that category's question 18.

The fix: introduce an outbox table in the same database as the business data, and rewrite the write path so the business-data change and the 'publish this event' intent are written **in the same local database transaction** — atomic with each other by construction, since they're now just two ordinary rows in one ACID transaction, rather than two operations spanning two entirely separate systems. Replace the direct Kafka publish call with a separate relay process (a polling job, or better, a CDC tool like Debezium reading the database's write-ahead log) that picks up committed outbox rows and publishes them to Kafka asynchronously, entirely decoupled from the original request's transaction."

**Code:**

```java
// BEFORE — the broken pattern causing the reported symptom
@Transactional
public void placeOrder(Order order) {
    kafkaTemplate.send("order-events", new OrderPlacedEvent(order)); // published
    orderRepository.save(order); // if THIS fails/rolls back, the event
}                                    // was ALREADY published — exactly the
                                       // reported "sometimes publishes without
                                       // committing" symptom

// AFTER — outbox pattern, atomic by construction
@Transactional
public void placeOrder(Order order) {
    orderRepository.save(order);
    outboxRepository.save(new OutboxEvent("OrderPlaced", order.getId(),
        serializeToJson(order))); // SAME transaction — both commit together,
}                                     // or NEITHER does; the relay process
                                        // publishes to Kafka SEPARATELY, later,
                                        // reading only ALREADY-COMMITTED rows
```

**Follow-up:**

I'd bring up that fixing this requires more than just moving the publish call — it requires making the relay process itself idempotent-tolerant on the consumer side (Transactions category questions 20/25), since the outbox pattern shifts the reliability problem from "avoid duplicates entirely" (impossible to guarantee) to "consumers must tolerate at-least-once delivery," and I'd walk through confirming every existing consumer of this event stream is actually built to handle a redelivered event correctly before considering this fix complete — the outbox pattern alone fixes the "published without committing" symptom, but doesn't automatically fix a consumer that assumed exactly-once delivery and never needed to handle duplicates before.

**Source:** [Chris Richardson — Transactional Outbox Pattern](https://microservices.io/patterns/data/transactional-outbox.html), [Debezium documentation](https://debezium.io/documentation/reference/stable/index.html)

---

## 9. Green Application Instances Must Serve HTTP Traffic but Cannot Consume Kafka Messages. Design the Deployment.

**Answer:**

"This is a genuine, common requirement during a blue/green cutover — you want to verify green can correctly *serve* traffic before letting it also start *consuming and processing* messages, since a bug in green's consumer logic processing real production messages (potentially with side effects, like charging payments or sending notifications) is much harder to safely undo than a bug in green's HTTP response handling, which is comparatively low-risk to verify and roll back.

The mechanism: green's Kafka consumers should be deployed in a **disabled/paused** state initially — either by not starting the `@KafkaListener` consumers at all in green's initial configuration (a feature flag or Spring profile controlling whether consumer beans are even created), or by starting them but keeping them **paused** (Kafka's own consumer `pause()`/`resume()` API) so they're connected to the cluster (verifiable health-wise) but not actively polling/processing messages. HTTP traffic routing (via the load balancer/service mesh) is controlled entirely independently of this — green can receive and serve HTTP requests fully while its Kafka consumption remains paused, letting you verify green's HTTP-serving correctness in isolation before making the separate decision to also enable its message consumption."

**Code:**

```java
@Component
class GreenConsumerGate {
    @Autowired
    private KafkaListenerEndpointRegistry registry;

    @EventListener(ApplicationReadyEvent.class)
    void pauseConsumersUntilCutoverApproved() {
        if (!deploymentConfig.isConsumingEnabled()) { // explicit flag, separate
            registry.getListenerContainers()              // from HTTP-traffic routing
                .forEach(MessageListenerContainer::pause); // connected, but NOT
        }                                                     // actively polling
    }

    // Called explicitly, as a SEPARATE cutover step, once green's HTTP-serving
    // behavior has already been independently verified
    void enableConsumptionAfterVerification() {
        registry.getListenerContainers().forEach(MessageListenerContainer::resume);
    }
}
```

**Follow-up:**

I'd bring up that this deliberately splits one cutover into **two independent, sequenced decisions** — "is green safe to serve HTTP traffic" and "is green safe to process Kafka messages" — rather than treating the whole cutover as one atomic switch, and I'd argue this staged approach is strictly safer for any deployment where the consumer side has real, harder-to-reverse side effects: verify the lower-risk surface first, gain confidence, then deliberately and separately flip on the higher-risk surface, rather than betting both simultaneously on the same single cutover moment.

**Source:** [Spring Kafka Documentation — Pausing and Resuming Listener Containers](https://docs.spring.io/spring-kafka/reference/kafka/pause-resume.html)

---

## 10. A JWT Signing Key Is Rotated and Some Services Begin Rejecting Valid Requests. Diagnose and Redesign.

**Answer:**

"This is exactly the key-rotation sequencing failure described in the Spring Security file (question 17) — the most likely root cause is that the old signing key was removed from the published JWKS document (or a resource server's JWKS cache hadn't yet refreshed to pick up the new key) before every token signed with the old key had actually expired, so tokens that were still validly within their lifetime suddenly fail signature verification once the resource server can no longer find the key that signed them.

Diagnosis: check the `kid` on the rejected tokens against what's currently published in the JWKS document — if the `kid` isn't present at all, that's the smoking gun (the old key was removed too early). Check each affected resource server's JWKS cache refresh interval and whether it had actually re-fetched since the new key was published — a resource server with a long cache TTL that hadn't refreshed yet would reject brand-new tokens signed with the new key it doesn't know about yet, which is the mirror-image version of the same underlying sequencing problem.

Redesign: enforce a strict, explicit key-rotation runbook — publish the new key in the JWKS document (alongside the old one, not replacing it) well before the authorization server starts signing with it; only start signing with the new key once resource servers have had time (based on their known cache refresh intervals, with margin) to pick it up; keep the old key published for at least the maximum token lifetime after the authorization server stops signing with it; only remove the old key from the JWKS document once that full window has passed."

**Code:**

```text
Corrected rotation runbook — explicit stages, explicit minimum wait times:

  T+0:    publish NEW key in JWKS, alongside OLD key (still signing with OLD)
  T+X:    (X >= longest resource server's JWKS cache refresh interval, with margin)
          switch authorization server to sign NEW tokens with NEW key
  T+X+Y:  (Y >= maximum token lifetime, e.g. 1 hour)
          every token signed with OLD key has now naturally expired
  T+X+Y:  ONLY NOW remove OLD key from the published JWKS document

  Rule of thumb violated in the incident: OLD key was removed at some T
  where T < X+Y — either before resource servers had the NEW key cached
  (rejecting NEW tokens) or before OLD tokens had expired (rejecting
  still-valid OLD tokens once the OLD key disappeared from JWKS)
```

**Follow-up:**

I'd bring up that this incident is a good candidate for an automated safeguard beyond just a better runbook — a pre-rotation check that queries every known resource server's actual current JWKS cache state (or, more practically, a centrally-enforced minimum key-overlap-duration policy that the rotation tooling itself refuses to violate) is more reliable than a documented process that depends on a human correctly calculating and waiting out the right intervals under time pressure during a security-sensitive rotation.

**Source:** [RFC 7517 — JSON Web Key](https://datatracker.ietf.org/doc/html/rfc7517), [Spring Security Reference — JWKS-based JWT Decoding](https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html)

---

## 11. A Customer Retries a Timed-Out Payment Request. How Do You Prevent Double Charging?

**Answer:**

"This is the canonical idempotency-key scenario — see REST API Design question 5 for the full mechanism (unique idempotency key per logical attempt, an atomic check-and-reserve against a unique DB constraint, returning the original stored result on replay) and the working code for it; I won't re-derive that here. What this framing — a customer reporting a suspected double charge — actually tests is the two things around that mechanism that a pure design question doesn't: whether the *client* half of the contract held, and how you'd investigate after the fact rather than just describe the design.

The mechanism only works if the client reuses the *same* idempotency key across retries of the same logical attempt. If a mobile client or a flaky client library regenerates a fresh UUID on every retry — a genuinely common implementation bug — the server-side mechanism is powerless: each retry looks like a brand-new request to a server that's doing everything right. So this is a client/server contract, not a purely server-side implementation detail, and it needs to be documented and tested against actual client behavior, not just assumed because the server-side code looks correct."

**Example (incident-investigation sequence):**

```text
Customer reports what looks like a double charge on a timed-out payment.

  1. Pull the idempotency_records row(s) for that customer/order around the
     report time. One row with one key → the server-side mechanism worked;
     look elsewhere (a genuinely separate payment, a refund/re-attempt the
     customer initiated themselves, a display bug double-counting one charge).
  2. Two DIFFERENT idempotency keys for what the customer describes as one
     attempt → the server did its job correctly on each request it received;
     the bug is upstream, on the client — check whether the client
     regenerates the key per retry instead of reusing it.
  3. Payment processor shows two actual charges against ONE idempotency key
     → the server-side atomicity is broken (e.g., the unique constraint is
     missing, or the check-and-reserve isn't in the same transaction as the
     charge) — this is the REST Q5 atomicity requirement not actually being
     met in production.
  4. Confirm the fix category (client key-reuse discipline vs. server-side
     atomicity) before proposing a change — the two failure modes above have
     completely different fixes, and "add more retries" fixes neither.
```

**Source:** [Stripe API — Idempotent Requests](https://stripe.com/docs/api/idempotent_requests)

---

## 12. A JPA Query Causes Production Memory Spikes but Works Correctly in Testing. How Do You Investigate?

**Answer:**

"'Correct in testing, memory spike in production' almost always points at a **data-volume difference** between the two environments, not a logic bug — the query is functionally correct, but something about its result-set size or fetch strategy scales badly with production's actual data volume in a way test data (typically much smaller) never exercises.

My investigation: check whether the query loads a full collection into memory that scales with a customer/tenant's own data size (JPA/Hibernate file's N+1 and eager-loading discussions) — a query that works fine for a test customer with 10 orders but loads all associated entities for a production customer with 500,000 orders is exactly this shape of bug, and it's precisely the pattern described in the JPA/Hibernate file's own postmortem question (question 30) — a latent issue that was always present, just never large enough to matter until a specific customer's data volume grew past a threshold. I'd check for a join-fetch across multiple large collections (question 9 in that file — the cross-product multiplication problem, which can produce genuinely enormous, duplicated result sets for a customer with large collections on both sides of the join) as a specific, common variant."

**Code:**

```text
Investigation checklist:

  1. Which specific query/entity is implicated? (heap dump + dominator tree,
     JVM/GC file question 12, sorted by retained size — what's actually
     holding the memory)
  2. Does the query's result size scale with a SPECIFIC customer/tenant's
     own data volume, rather than being bounded/paginated?
  3. Is this a JOIN FETCH across MULTIPLE collections (cross-product
     multiplication, JPA/Hibernate file question 9)?
  4. Reproduce against a COPY of the actual large customer's data volume
     (not test fixtures) — does the memory spike reproduce immediately
     once tested against REALISTIC data volume?
```

**Follow-up:**

I'd bring up that the actual, durable fix here is rarely "optimize this one query" — it's recognizing that **test data volume needs to represent realistic production data-volume distributions**, not just correctness-focused small fixtures, and I'd advocate for adding a small number of "large tenant" scenarios to the test/staging environment specifically to catch this entire class of bug before production, rather than relying on production incidents as the only place data-volume-scaling issues ever get discovered — directly mirroring the systemic action item from the JPA/Hibernate file's own postmortem question.

**Source:** [Hibernate ORM User Guide — Fetching Strategies](https://docs.jboss.org/hibernate/orm/current/userguide/html_single/Hibernate_User_Guide.html#fetching), [Eclipse Memory Analyzer (MAT) documentation](https://eclipse.dev/mat/)

---

## 13. A Low-Latency Service Has Periodic 10-Second Pauses. Describe Your Diagnostic Process.

**Answer:**

"A periodic, roughly-regular pause pattern is a strong initial signal pointing toward something cyclical — GC, a scheduled job, or a database-side periodic event — rather than a request-pattern-driven cause, so I'd start there rather than assuming it's application-request-load-related.

First: **GC logs** (JVM/GC file, questions 7-10) — is there a full GC (or a mixed/young collection taking unusually long) correlating exactly with the pause timing? If pauses are genuinely periodic (every N minutes, say), that's consistent with a GC cycle triggered by consistent allocation/promotion pressure reaching a threshold on a predictable cadence. Second, if GC logs don't show a correlating pause: check **safepoint logs** specifically (JVM/GC file question 8) — a long 'time to safepoint' with a short actual GC pause points at an application thread delaying entry into a safepoint, not GC itself being slow. Third: check the **database** for periodically-long-running transactions or lock contention (Transactions category question 28's `pg_stat_activity` investigation) — a scheduled batch job or a periodic long-held transaction elsewhere in the system could be causing lock contention that manifests as a pause in this unrelated low-latency service. Fourth: check for a **periodic scheduled task** (a cron job, a `@Scheduled` method) running on the same JVM or same database, at a cadence matching the pause pattern."

**Code:**

```bash
# Correlate pause timestamps against GC log entries FIRST
java -Xlog:gc*:file=gc.log:time,uptime,level,tags -jar app.jar

# If GC doesn't correlate, check safepoint-specific timing
java -Xlog:safepoint:file=safepoint.log:time,uptime -jar app.jar

# Check for periodic long-running transactions/lock contention on the DB side
SELECT pid, state, xact_start, now() - xact_start AS duration, query
FROM pg_stat_activity WHERE state != 'idle' ORDER BY xact_start ASC;

# Check for scheduled jobs with a cadence matching the pause pattern
grep -i "scheduled\|cron" application.log | grep -oP '\d{2}:\d{2}:\d{2}'
```

**Follow-up:**

I'd emphasize that the very first, cheapest diagnostic step is simply plotting the pause timestamps and checking whether they're genuinely periodic (a fixed interval) versus merely frequent-but-irregular — a truly periodic pattern narrows the search dramatically toward cyclical causes (GC, scheduled jobs, periodic batch processes) and away from request-load-driven causes almost immediately, which is a cheap, high-leverage triage step worth doing before diving into any of the deeper GC/safepoint/database investigation.

**Source:** [JDK Flight Recorder documentation](https://docs.oracle.com/en/java/javase/21/docs/specs/man/jfr.html), [PostgreSQL Documentation — pg_stat_activity](https://www.postgresql.org/docs/current/monitoring-stats.html#MONITORING-PG-STAT-ACTIVITY-VIEW)

---

## 14. How Would You Split a Large Spring Boot Monolith While Preserving Transaction Correctness?

**Answer:**

"The core risk in splitting a monolith is that existing code very likely relies on a single, shared ACID database transaction to enforce cross-entity invariants that span what will become **different services** after the split — once those entities live in different services with different databases, that single-transaction guarantee is gone, and the invariant needs a new mechanism.

My approach: first, identify the **transactional boundaries** in the current monolith that actually span what's being split apart — every `@Transactional` method that touches entities destined for different future services is a place where the split will introduce a genuine consistency gap that needs to be explicitly addressed, not just split mechanically along class/package boundaries. For each such boundary, replace the single local transaction with either an explicit saga (Transactions category questions 23-24) if the operation genuinely needs multi-step, compensable coordination across the new service boundary, or, if the actual invariant can tolerate it, redesign the operation to only require strong consistency **within** one new service's boundary, accepting eventual consistency for anything that must cross into another. I'd do this analysis **before** choosing where to actually draw the service boundaries, not after — a proposed split that turns out to require sagas for nearly every common operation is a signal the boundary itself may be drawn in the wrong place (directly feeding into question 15)."

**Code:**

```text
Before split (monolith, single DB transaction):
  @Transactional
  void placeOrder(Order order) {
      orderRepository.save(order);       // -> will become "Order Service"
      inventoryRepository.decrement(...); // -> will become "Inventory Service"
      paymentRepository.charge(...);      // -> will become "Payment Service"
  }
  -- ONE local transaction currently guarantees all-or-nothing atomicity
  -- across what are about to become THREE separate services/databases

After split — MUST become an explicit saga, not a "hope it's still atomic":
  OrderService.placeOrder()
    -> publishes OrderCreated
       -> InventoryService (saga step, local txn, compensable: release)
       -> PaymentService (saga step, local txn, compensable: refund)
  -- the FORMER single-transaction guarantee is now explicit saga
  -- orchestration/choreography with real compensation logic —
  -- this must be DESIGNED, not assumed to "just still work"
```

**Follow-up:**

I'd bring up that the actual staff-level judgment here is recognizing which former single-transaction operations are **cheap and natural** to convert to a saga (genuinely independent steps with clear compensations) versus which ones reveal that the proposed service boundary itself cuts across a **cohesive unit that shouldn't have been split apart in the first place** — if an operation's invariants are so tightly coupled that no reasonable saga design feels natural, that's often a signal to reconsider the boundary (merge those two "services" back into one, at least for now) rather than force an awkward, fragile distributed-transaction workaround onto a boundary that doesn't reflect the domain's actual seams.

**Source:** [Chris Richardson — Microservices Patterns (decomposition strategies)](https://microservices.io/patterns/), [Chris Richardson — Saga Pattern](https://microservices.io/patterns/data/saga.html)

---

## 15. How Would You Determine Whether a Proposed Microservice Boundary Is Appropriate?

**Answer:**

"I'd evaluate a proposed boundary against a few concrete tests, rather than relying on intuition about 'this feels like a separate concern.' First, the **transactional-coupling test** from the previous question — does splitting along this boundary force nearly every common operation into a saga with real compensation logic? If so, that's evidence the boundary cuts across something that's actually one cohesive transactional unit in the business domain, not two independent ones.

Second, the **change-coupling test** — do these two proposed services, historically, tend to change together, in the same commits/pull requests, for the same business reasons? If two 'separate' services are almost always modified together whenever a business requirement changes, that's a strong signal they're not actually independently-evolvable units yet, regardless of how cleanly separable their code looks structurally. Third, the **team-ownership test** (tying directly into the Engineering Leadership category) — can one team genuinely own, deploy, and operate this service independently, without needing coordinated releases with the team owning the other side of the boundary? A boundary that still requires two teams to coordinate every deployment hasn't actually achieved the independent-deployability benefit microservices are meant to provide, even if the code is technically split into separate repositories/services."

**Code:**

```text
Boundary evaluation checklist:

  1. TRANSACTIONAL: does a typical, common business operation require
     coordinating writes across BOTH proposed services? If EVERY common
     operation needs a saga, question the boundary itself.

  2. CHANGE COUPLING: pull up git history — do commits touching one
     proposed service's code ALSO, historically, touch the other's, for
     the SAME business reason, most of the time? (a real, measurable signal,
     not a guess)

  3. TEAM OWNERSHIP: can ONE team deploy, operate, and evolve this proposed
     service WITHOUT needing a coordinated release with another team?

  4. DATA OWNERSHIP: does each proposed service have a genuinely distinct,
     independently-evolvable data model, or are they really just two views
     over what's fundamentally the same underlying entity/aggregate?
```

**Follow-up:**

I'd bring up that the change-coupling test specifically is underused and genuinely valuable because it's **measurable from actual history** rather than a subjective architectural opinion — pulling git log data on which files/modules change together in the same commits over the past year gives real, concrete evidence about where a codebase's actual seams are, versus where an org chart or an idealized domain diagram *suggests* they should be, and I'd treat a mismatch between those two (the org chart says "two services," the commit history says "these always change together") as a serious, evidence-based reason to reconsider a proposed split before committing to it.

**Source:** [Chris Richardson — Microservices Patterns (Decompose by Business Capability / Subdomain)](https://microservices.io/patterns/decomposition/decompose-by-business-capability.html), [Martin Fowler — MonolithFirst](https://martinfowler.com/bliki/MonolithFirst.html)

---

## 16. How Do You Evolve an Event Contract Used by Dozens of Unknown Consumers?

**Answer:**

"This is the Kafka-category version of the REST API Design file's endpoint-deprecation discipline (question 25 there), applied to an event schema instead of an HTTP endpoint — with the added wrinkle that Kafka consumers are often genuinely harder to enumerate than HTTP API callers (no equivalent of an API-key-per-caller convention necessarily existing for every consumer group), so 'unknown consumers' is a more common, more serious constraint here.

My approach: enforce schema compatibility rules explicitly via a schema registry (Avro/Protobuf/JSON Schema with backward/forward/full compatibility checking, Kafka category) so any schema change that would break an existing consumer is **rejected at publish time**, before it ever reaches the topic — this converts 'a consumer might break' from a runtime discovery into a compile-time/CI-time guarantee. For genuinely additive changes (new optional fields), the schema registry's backward-compatibility check passes automatically and no coordination is needed. For a genuinely breaking change (removing a field, changing a type), I'd treat it exactly like an API version bump — publish to a **new** topic (or a new, explicitly versioned event type on the same topic) rather than mutating the existing contract in place, let both the old and new event versions coexist for a measured migration period, monitor actual consumer-group lag/activity on the old topic to identify which consumer groups are still actively reading it, and only retire the old topic once usage has genuinely dropped to zero."

**Code:**

```text
Schema registry enforcement, at PUBLISH time (before reaching the topic):

  Producer attempts to publish with a MODIFIED schema
    -> Schema Registry checks compatibility mode (e.g., BACKWARD)
    -> if the new schema is NOT backward-compatible with what existing
       consumers expect: REJECTED at publish time, build/deploy FAILS
    -> if it IS compatible (additive field, etc.): allowed through

For a genuinely BREAKING change:
  order-events        (OLD schema, still active)
  order-events-v2      (NEW schema, new topic)
  -> monitor consumer-group lag/activity on order-events specifically
  -> only retire order-events once ALL identified consumer groups have
     confirmed migration to order-events-v2
```

**Follow-up:**

I'd bring up that "unknown consumers" is itself a problem worth fixing at the platform level, not just worked around — requiring every consumer group to register itself (even informally, via a lightweight internal catalog/registry of "which team owns which consumer group, reading which topics") turns "we don't know who's still consuming this" into an answerable question, and I'd advocate for that kind of consumer-registry discipline as a genuine platform investment specifically because "we have no idea who might break" is a much worse position to operate a shared event contract from than having an explicit, even if imperfect, map of known consumers to check against before any breaking change is even considered.

**Source:** [Confluent — Schema Evolution and Compatibility](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html), [Confluent Documentation — Monitor Consumer Lag](https://docs.confluent.io/platform/current/monitor/monitor-consumer-lag.html)

---

## 17. How Would You Design Tenant Isolation Across API, Database, Cache, and Kafka?

**Answer:**

"I'd apply a consistent principle at every layer: the tenant identifier is established once, at authentication, from a source the tenant/caller cannot forge or override, and every subsequent layer scopes its behavior by that same trusted identifier — never re-deriving or re-trusting a tenant ID from anything client-suppliable at a lower layer.

**API**: the tenant ID comes from a validated JWT claim (Spring Security file, question 30), never a request header or query parameter a client could simply set to a different tenant's ID. **Database**: every query scoped by tenant at the data-access layer as a structural default — either via repository method signatures that require a tenant parameter (JPA/Hibernate-adjacent discipline), or more robustly, via database-level row-level security tied to the current session's tenant context, so even a query that forgot to add an explicit tenant filter still can't leak across tenants (Spring Security file, question 30's PostgreSQL RLS recommendation). **Cache**: tenant ID embedded in every cache key (`product:tenant-42:12345`, not just `product:12345`), preventing any possibility of one tenant's cached data being served to another, and enabling per-tenant cache eviction if ever needed (e.g., offboarding a tenant). **Kafka**: tenant ID embedded in every event payload (and, where the access pattern justifies it, potentially used as part of the partitioning key, if per-tenant ordering matters — Kafka category's message-key discussion), with every consumer's processing logic explicitly scoped by that embedded tenant ID, never assuming a topic is inherently single-tenant just because it happens to be used that way today."

**Code:**

```text
Consistent tenant-scoping across every layer, all deriving from ONE
authenticated, trusted source (the JWT's tenant_id claim):

  API:      GET /orders/{id}  ->  tenant_id from VALIDATED JWT claim
  Database: findByIdAndTenantId(id, tenantId)  +  PostgreSQL RLS as a
            structural backstop, independent of application code discipline
  Cache:    cache key = "order:" + tenantId + ":" + id  (never JUST the id)
  Kafka:    event payload includes tenant_id explicitly; consumers filter/
            scope processing by it, never assume single-tenant topic usage
```

**Follow-up:**

I'd bring up that the database-level row-level-security backstop is the single highest-leverage piece of this design, precisely because it's the one layer that protects against a mistake at **every other** layer simultaneously — an application bug that forgets to scope a query by tenant, a cache key that's accidentally built without the tenant prefix, or a Kafka consumer that processes an event without checking its tenant field are all still caught if the database itself refuses to return cross-tenant rows regardless of what the application asked for — and I'd argue that for a genuinely multi-tenant platform, this database-level enforcement is worth the setup investment specifically because it's the layer most resistant to being accidentally bypassed by a future engineer who doesn't know or remember the full tenant-isolation discipline the rest of the stack depends on.

**Source:** [PostgreSQL — Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html), [OWASP API Security Top 10](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)

---

## 18. How Do You Introduce Backpressure Across Synchronous and Asynchronous Boundaries?

**Answer:**

"Backpressure means a slow or overwhelmed downstream consumer can signal 'slow down' back to whatever is producing work for it, rather than the producer blindly continuing to push work faster than the consumer can handle — and the mechanism for expressing that signal is fundamentally different depending on whether the boundary is synchronous or asynchronous.

At a **synchronous** boundary (an HTTP call, a direct method call to a downstream service): backpressure is expressed via bounded concurrency limits (a semaphore, a bounded connection pool, or a bounded thread pool — concurrency file discussion) and explicit rejection (`429`/`503`, REST API Design file question 21) once that bound is reached — the caller gets an immediate, fast signal to back off, rather than queuing indefinitely.

At an **asynchronous, messaging-based** boundary (a Kafka consumer): backpressure is more naturally built-in — a consumer that's processing slowly simply doesn't call `poll()` again until it's ready, and messages accumulate in the topic (visible as growing consumer lag) rather than being force-fed to an overwhelmed consumer; the 'signal' here is lag itself, and the corresponding response is scaling out consumers (more partitions, more consumer instances) or optimizing per-message processing time, not a synchronous rejection response.

The genuinely hard part is the **boundary between the two** — a synchronous HTTP request that triggers work eventually processed asynchronously (or vice versa) needs an explicit translation: an HTTP endpoint accepting a request that will be processed via a Kafka-backed async pipeline should apply its own bounded-queue/rejection logic at the HTTP layer (not let unlimited HTTP requests pile up unboundedly waiting on a slow async pipeline downstream), rather than assuming the async side's natural backpressure (lag) automatically protects the synchronous side too."

**Code:**

```java
// Synchronous boundary — explicit, bounded rejection
Semaphore concurrencyLimit = new Semaphore(50); // matches downstream capacity

ResponseEntity<?> callDownstream(Request request) {
    if (!concurrencyLimit.tryAcquire()) {
        return ResponseEntity.status(503).header("Retry-After", "5").build(); // FAST,
    }                                                                            // explicit
    try { return ResponseEntity.ok(downstreamClient.call(request)); }             // rejection
    finally { concurrencyLimit.release(); }
}

// Async boundary — backpressure is IMPLICIT via lag, not an explicit rejection
@KafkaListener(topics = "work-items", concurrency = "5") // bounded consumer
void processWorkItem(WorkItem item) { // parallelism, matching actual capacity
    doExpensiveProcessing(item); // if this is slow, lag grows — the SIGNAL —
}                                    // rather than the consumer being force-fed
                                       // faster than it can actually keep up

// The BOUNDARY between them — an HTTP endpoint accepting work for later
// ASYNC processing needs its OWN explicit bound, not inherited from the
// async side's lag-based backpressure
ResponseEntity<?> submitForAsyncProcessing(WorkRequest request) {
    if (pendingQueueDepth() > MAX_QUEUE_DEPTH) {
        return ResponseEntity.status(503).build(); // explicit HTTP-layer bound,
    }                                                  // independent of Kafka's
    kafkaTemplate.send("work-items", request);           // OWN lag-based signal
    return ResponseEntity.accepted().build();
}
```

**Follow-up:**

I'd bring up that the most common mistake at exactly this synchronous-to-asynchronous boundary is assuming the async side's natural backpressure (growing Kafka lag) automatically protects the synchronous side from being overwhelmed — it doesn't, since an HTTP endpoint that unconditionally accepts and publishes to Kafka has no inherent limit of its own, and will happily accept far more requests than the async pipeline can ever catch up on, silently growing an unbounded backlog (and potentially an unbounded number of concurrently-open HTTP connections/threads waiting on a synchronous 'accepted' response) even while Kafka's own lag metric is dutifully, correctly reporting the growing problem — the HTTP layer needs its own, independent, explicit bound, not a borrowed sense of safety from the async side's different backpressure mechanism.

**Source:** [Google SRE Workbook — Handling Overload](https://sre.google/sre-book/handling-overload/), [Reactive Streams specification (backpressure model reference)](https://www.reactive-streams.org/)

---

## 19. How Do You Define and Measure an End-to-End Reliability SLO?

**Answer:**

"An SLO needs to be defined in terms of what actually matters to the **user/business outcome**, not an internal component's own health — 'the database is up 99.99% of the time' is an internal metric, not an SLO; 'a customer can successfully place an order within 2 seconds, 99.9% of the time' is an SLO, because it's stated in terms of the actual end-to-end user-facing outcome, and it can be violated even when every individual internal component reports itself as healthy (exactly the business-health-versus-infrastructure-health distinction from the REST API Design file, question 23).

Measurement has to be **end-to-end**, from the client's actual perspective, not an average of each internal service's own individually-reported health — this typically means synthetic monitoring (a script that actually performs the real user journey — place a test order — end to end, on a schedule, from outside the system) combined with real-user-monitoring aggregated across the full request path (using distributed tracing, REST API Design file question 24, to actually measure the complete latency/success of the whole journey, not just one hop). I'd define the SLO with an explicit **error budget** (Google SRE's framing) — if the SLO is 99.9% successful order placement over a rolling 30-day window, that budget (0.1% of requests) is a deliberate, spendable allowance, and I'd track how much of it is being consumed in real time, treating a budget nearing exhaustion as a trigger to prioritize reliability work over new features (directly connecting to the Engineering Leadership category's reliability-versus-feature-commitment trade-off)."

**Code:**

```text
NOT an SLO (internal, component-level):
  "Database uptime: 99.99%"
  "API service uptime: 99.95%"
  -- both can be true SIMULTANEOUSLY while the actual end-to-end user
  -- journey fails, e.g., due to a Redis outage causing degraded checkout,
  -- or a Kafka consumer backlog delaying order confirmation

AN ACTUAL SLO (end-to-end, user-outcome-focused):
  "95% of order-placement attempts complete successfully within 2 seconds,
   measured end-to-end via distributed tracing across the FULL request
   path (API -> DB -> Kafka saga completion -> confirmation), over a
   rolling 30-day window"

  Error budget: 5% of order attempts, over 30 days, can fail/be slow
  before the SLO is violated — tracked in REAL TIME, not just reviewed
  retroactively at month-end
```

**Follow-up:**

I'd bring up that the error-budget framing's real value is turning "how reliable should we be" from an abstract, endless debate into a concrete, quantified, and genuinely actionable operating model — once a team has a real-time view of how much budget remains, "should we ship this risky feature this week, or focus on reliability" stops being a subjective argument and becomes a data-driven decision based on whether the budget is currently healthy or already nearly exhausted, which is exactly the kind of objective, evidence-based prioritization tool a Staff engineer should be advocating for and helping build, rather than relying on ad hoc, contentious debates every time the trade-off comes up.

**Source:** [Google SRE Book — Service Level Objectives](https://sre.google/sre-book/service-level-objectives/), [Google SRE Workbook — Implementing SLOs](https://sre.google/workbook/implementing-slos/)

---

## 20. How Would You Run a Production Migration With a Tested Rollback and Recovery Plan?

**Answer:**

"I'd treat 'tested rollback plan' literally — a rollback plan that's never actually been executed in a realistic environment isn't a real plan, it's a hope, and I've seen migrations where the forward path was carefully tested but the rollback path, assumed to be 'just run the reverse migration script,' had never actually been exercised and turned out to have its own bugs precisely when it was needed under real incident pressure.

My approach: apply the expand/contract discipline (Transactions category question 29) so that at every intermediate stage, both the current and the previous application version can run correctly against the current schema state — this is what makes rollback *possible* at all without data loss, since a genuinely destructive, single-step migration has no safe rollback by construction. Explicitly **test the rollback path** in a staging environment that mirrors production data volume — run the forward migration, verify, then actually execute the rollback and verify the system is genuinely healthy and correct afterward, not just assumed to be. Define explicit **go/no-go checkpoints** during the actual production migration (specific metrics/checks that must pass before proceeding to the next irreversible step), and a clear **decision owner** authorized to trigger rollback without needing to escalate through additional approval under time pressure — ambiguity about who can pull the rollback trigger, and how quickly, is a real, common failure mode during an actual migration incident."

**Code:**

```text
Migration runbook structure:

  1. EXPAND phase deployed — verify BOTH old and new app versions function
     correctly against the new schema state (this is the actual "rollback
     safety" property being tested, not just assumed)

  2. TESTED ROLLBACK — in staging, with PRODUCTION-representative data
     volume: run the expand migration, verify, THEN actually execute the
     rollback script and verify the system is genuinely correct afterward —
     not "the rollback script exists," but "the rollback script was RUN
     and VERIFIED to work"

  3. Explicit GO/NO-GO checkpoints during the real production migration:
     - after backfill: verify data correctness via a sampling/checksum query
     - after dual-write deployment: verify write-path parity between
       old and new structures for a monitoring window
     - CLEAR, PRE-AGREED decision owner authorized to trigger rollback,
       WITHOUT needing further approval, if any checkpoint fails

  4. CONTRACT phase — only after a defined, sufficient bake period with
     no issues, and explicit confirmation nothing still depends on the
     old structure
```

**Follow-up:**

I'd bring up that the single most valuable, and most commonly skipped, step is actually **executing** the rollback in a realistic environment before the real migration — teams very often write a rollback script, review it, and consider it "tested" purely by reading it, without ever actually running it end-to-end against realistic data volume; the failure mode this misses is exactly the kind of thing that only surfaces under real execution (a rollback script with a subtle bug, a step that takes far longer against real data volume than anyone estimated, an assumption about intermediate state that doesn't actually hold) — and I'd treat "have we ever actually run this rollback, for real, and confirmed the system came back correctly" as a hard gate before approving any non-trivial production migration, not a nice-to-have.

**Source:** [Martin Fowler & Pramod Sadalage — Evolutionary Database Design](https://martinfowler.com/articles/evodb.html), [Google SRE Book — Managing Incidents](https://sre.google/sre-book/managing-incidents/)

---

## Sources & Further Reading — Consolidated

| Topic | Link |
|---|---|
| Chris Richardson — Saga Pattern | https://microservices.io/patterns/data/saga.html |
| Chris Richardson — Transactional Outbox Pattern | https://microservices.io/patterns/data/transactional-outbox.html |
| Chris Richardson — Idempotent Consumer | https://microservices.io/patterns/communication-style/idempotent-consumer.html |
| Chris Richardson — Microservices Patterns (Decomposition) | https://microservices.io/patterns/ |
| Martin Fowler — MonolithFirst | https://martinfowler.com/bliki/MonolithFirst.html |
| Stripe API — Idempotent Requests | https://stripe.com/docs/api/idempotent_requests |
| Martin Kleppmann — Designing Data-Intensive Applications | https://dataintensive.net/ |
| AWS — Multi-Region Application Architecture | https://aws.amazon.com/blogs/architecture/tag/multi-region/ |
| Martin Fowler & Pramod Sadalage — Evolutionary Database Design | https://martinfowler.com/articles/evodb.html |
| Confluent — Schema Evolution and Compatibility | https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html |
| Confluent Documentation — Monitor Consumer Lag | https://docs.confluent.io/platform/current/monitor/monitor-consumer-lag.html |
| Kafka Documentation — Consumer Configs | https://kafka.apache.org/documentation/#consumerconfigs |
| Google SRE Workbook — Handling Overload | https://sre.google/sre-book/handling-overload/ |
| Resilience4j — Circuit Breaker | https://resilience4j.readme.io/docs/circuitbreaker |
| Hibernate ORM User Guide — Statistics | https://docs.jboss.org/hibernate/orm/current/userguide/html_single/Hibernate_User_Guide.html#statistics |
| Eclipse Memory Analyzer (MAT) | https://eclipse.dev/mat/ |
| JDK Flight Recorder documentation | https://docs.oracle.com/en/java/javase/21/docs/specs/man/jfr.html |
| PostgreSQL Documentation — pg_stat_activity | https://www.postgresql.org/docs/current/monitoring-stats.html#MONITORING-PG-STAT-ACTIVITY-VIEW |
| Spring Kafka Documentation — Pausing/Resuming Listener Containers | https://docs.spring.io/spring-kafka/reference/kafka/pause-resume.html |
| RFC 7517 — JSON Web Key | https://datatracker.ietf.org/doc/html/rfc7517 |
| Spring Security Reference — JWT | https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html |
| PostgreSQL — Row Security Policies | https://www.postgresql.org/docs/current/ddl-rowsecurity.html |
| OWASP API Security Top 10 | https://owasp.org/API-Security/editions/2023/en/0x11-t10/ |
| Reactive Streams specification | https://www.reactive-streams.org/ |
| Google SRE Book — Service Level Objectives | https://sre.google/sre-book/service-level-objectives/ |
| Google SRE Workbook — Implementing SLOs | https://sre.google/workbook/implementing-slos/ |
| Google SRE Book — Managing Incidents | https://sre.google/sre-book/managing-incidents/ |
