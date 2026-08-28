# Redis & Caching — Interview Prep (Lead/Staff Level, with Code & Sources)

> **Target level:** Lead/Staff · **Baseline:** Redis 7.x (OSS) — Lua scripting via `EVAL`, Cluster hash-slot model, Sentinel-based failover · **Last verified:** 2026-08-22 · **Prerequisites:** basic Redis commands (`GET`/`SET`/`EXPIRE`); [Transactions](Transactions_Interview_Prep.md) helpful for the dual-write/outbox framing reused here

How to use this: each question has **the answer the way I'd actually say it out loud** in an interview, a **code snippet** you could sketch on a whiteboard or IDE to back it up, and **where the follow-up goes if you're in a Staff-level loop** — because at this level the bar is explaining what breaks under real production traffic (stampedes, hot keys, failover), not reciting Redis command syntax.

<!-- toc -->
## Table of Contents

- [1. When Should Redis Be Used as a Cache Versus a System of Record?](#1-when-should-redis-be-used-as-a-cache-versus-a-system-of-record)
- [2. Explain Cache-Aside, Read-Through, Write-Through, and Write-Behind Strategies](#2-explain-cache-aside-read-through-write-through-and-write-behind-strategies)
- [3. How Do You Maintain Consistency Between a Database and a Cache?](#3-how-do-you-maintain-consistency-between-a-database-and-a-cache)
- [4. What Can Go Wrong With "Update Database, Then Delete Cache"?](#4-what-can-go-wrong-with-update-database-then-delete-cache)
- [5. How Would You Handle Failure Between the Database Update and Cache Invalidation?](#5-how-would-you-handle-failure-between-the-database-update-and-cache-invalidation)
- [6. What Is a Cache Stampede, and How Do You Prevent It?](#6-what-is-a-cache-stampede-and-how-do-you-prevent-it)
- [7. What Are Cache Penetration and Cache Pollution?](#7-what-are-cache-penetration-and-cache-pollution)
- [8. Why Should Cache TTLs Include Jitter?](#8-why-should-cache-ttls-include-jitter)
- [9. How Would You Cache Negative Results Safely?](#9-how-would-you-cache-negative-results-safely)
- [10. How Do You Select a TTL?](#10-how-do-you-select-a-ttl)
- [11. Compare Redis Eviction Policies](#11-compare-redis-eviction-policies)
- [12. How Do Hot Keys Affect Redis?](#12-how-do-hot-keys-affect-redis)
- [13. How Would You Detect and Mitigate Hot Keys?](#13-how-would-you-detect-and-mitigate-hot-keys)
- [14. How Do Large Keys Affect Latency and Cluster Behavior?](#14-how-do-large-keys-affect-latency-and-cluster-behavior)
- [15. What Is the Difference Between Redis Replication, Sentinel, and Cluster?](#15-what-is-the-difference-between-redis-replication-sentinel-and-cluster)
- [16. What Consistency Guarantees Does Redis Replication Provide?](#16-what-consistency-guarantees-does-redis-replication-provide)
- [17. What Happens During Redis Failover?](#17-what-happens-during-redis-failover)
- [18. Why Can a Distributed Lock Be Unsafe?](#18-why-can-a-distributed-lock-be-unsafe)
- [19. Explain Token-Based Lock Ownership](#19-explain-token-based-lock-ownership)
- [20. When Should You Avoid Distributed Locks Entirely?](#20-when-should-you-avoid-distributed-locks-entirely)
- [21. Compare Fixed-Window, Sliding-Window, and Token-Bucket Rate Limiting](#21-compare-fixed-window-sliding-window-and-token-bucket-rate-limiting)
- [22. How Would You Build an Atomic Rate Limiter Using Lua?](#22-how-would-you-build-an-atomic-rate-limiter-using-lua)
- [23. How Do Redis Transactions Differ From Relational Transactions?](#23-how-do-redis-transactions-differ-from-relational-transactions)
- [24. What Do Pipelines Improve, and What Do They Not Guarantee?](#24-what-do-pipelines-improve-and-what-do-they-not-guarantee)
- [25. How Would You Version Cache Keys During a Deployment?](#25-how-would-you-version-cache-keys-during-a-deployment)
- [26. How Would Blue and Green Versions Share a Cache Safely?](#26-how-would-blue-and-green-versions-share-a-cache-safely)
- [27. How Do You Prevent Stale Cached Authorization Decisions?](#27-how-do-you-prevent-stale-cached-authorization-decisions)
- [28. How Should an Application Behave When Redis Is Unavailable?](#28-how-should-an-application-behave-when-redis-is-unavailable)
- [29. What Redis Metrics Would You Monitor?](#29-what-redis-metrics-would-you-monitor)
- [30. Describe a Cache Incident That Increased Rather Than Reduced Database Load](#30-describe-a-cache-incident-that-increased-rather-than-reduced-database-load)
- [Sources & Further Reading — Consolidated](#sources--further-reading--consolidated)

<!-- /toc -->

---

## 1. When Should Redis Be Used as a Cache Versus a System of Record?

**Answer:**

"As a **cache**, Redis holds data that's derivable from an authoritative source of truth — usually a relational database. If the cached data is lost entirely (a restart, a cluster failure, an eviction), the application falls back to the source of truth and rebuilds it. Correctness never depends on Redis retaining anything. This is Redis's most common role by far, and it's what its default configuration is built for.

As a **system of record**, Redis becomes the sole, authoritative store for some piece of data — nothing else can reconstruct it if it's lost. That's a much higher reliability bar. It means configuring persistence deliberately (RDB snapshots and/or AOF), setting up replication with real `WAIT`/acknowledgment semantics, and accepting that even a carefully-configured Redis is generally weaker on consistency and durability than a mature relational database's ACID guarantees. Redis was built primarily as a fast, in-memory data structure server. Its persistence story works fine for some system-of-record use cases — rate-limiter counters, session data, leaderboards, ephemeral queues — but it's not a drop-in replacement for a database's transactional guarantees where correctness really matters, like financial ledgers or order records. I'd draw this line explicitly in any design review: if losing or corrupting the data would be a real business incident, and no other system holds a copy of the truth, I'd want a much stronger case made before treating Redis as the authoritative store rather than the cache."

**Code:**

```java
// Cache role — Redis holds a DERIVED copy; the database remains authoritative,
// and losing this data is a performance problem, never a correctness one
@Cacheable(value = "products", key = "#id")
Product getProduct(String id) {
    return productRepository.findById(id).orElseThrow(); // ALWAYS reconstructible
}                                                            // from the real source of truth

// System-of-record role — Redis IS the authoritative store; losing it means
// the data is GONE, with no fallback reconstruction possible
redisTemplate.opsForValue().increment("rate-limit:tenant-42:minute-" + currentMinute);
// a rate-limiter counter genuinely lives ONLY in Redis — there's no
// "reconstruct this from the database" fallback if it's lost, which is an
// ACCEPTABLE risk for THIS specific, low-stakes use case (worst case: a
// brief rate-limit reset), but would NOT be acceptable for, say, an
// account balance
```

**Follow-up:**

The decision isn't always binary. A system can legitimately use Redis as a system of record for specific, low-consequence-of-loss data — rate limiters, ephemeral session tokens, leaderboards where a rare reset is tolerable — while treating it purely as a cache everywhere else. The discipline is being deliberate about which category each Redis-backed feature falls into, and documenting that choice, rather than drifting into "we're relying on Redis never losing this" without anyone actually deciding to accept that risk. Redis's own persistence options — RDB, AOF, or both — can make it durable enough for a lot of system-of-record use cases. But even with full AOF persistence (`appendfsync always`), you're trading performance and operational complexity for that durability, and that should be a conscious choice, not a default.

**Source:** [Redis Documentation — Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)

---

## 2. Explain Cache-Aside, Read-Through, Write-Through, and Write-Behind Strategies

**Answer:**

"**Cache-aside** (lazy loading) puts the application in explicit control: on a read, check the cache first; on a miss, read from the database and populate the cache for next time; on a write, write to the database and either update or invalidate the corresponding cache entry. It's the most common pattern in practice — simple, and the cache only ever holds data that's actually been requested.

**Read-through** moves that same 'check cache, fall back to database, populate cache' logic into the caching layer itself, via a configured loader function, instead of the application orchestrating it explicitly. It looks similar to cache-aside from the application's side — one `get()` call handles the whole fallback — but the fallback logic now lives in the cache abstraction rather than scattered across call sites.

**Write-through** sends writes to the cache first, and the cache synchronously writes through to the database as part of the same operation. Cache and database stay in sync as one logical write, at the cost of every write paying both the cache and the database latency together.

**Write-behind** (write-back) writes to the cache immediately and returns to the caller right away, with the actual database write happening asynchronously, batched, sometime later. That cuts write latency dramatically, but it opens a real window where the cache has data the database doesn't yet have — and a cache failure during that window means permanent data loss, since the write never reached the durable source of truth."

**Code:**

```java
// CACHE-ASIDE — application explicitly orchestrates the fallback
Product getProduct(String id) {
    Product cached = cache.get(id);
    if (cached != null) return cached; // hit

    Product fromDb = productRepository.findById(id).orElseThrow(); // miss -> DB
    cache.set(id, fromDb, Duration.ofMinutes(10)); // populate for next time
    return fromDb;
}

void updateProduct(Product product) {
    productRepository.save(product);   // write DATABASE first
    cache.delete(product.getId());      // then INVALIDATE (question 4 covers
}                                          // why delete, not update, is usually safer

// WRITE-BEHIND — fast write, DEFERRED, batched persistence — real data-loss
// risk if the cache fails before the deferred write actually happens
void recordPageView(String pageId) {
    cache.increment("views:" + pageId); // returns IMMEDIATELY — fast
    // a background process periodically flushes accumulated view counts
    // to the database, batched — but a cache crash BEFORE that flush
    // means those increments are GONE, permanently, never reaching the DB
}
```

**Follow-up:**

The practical decision: cache-aside is the right default for most read-heavy workloads — it's simple, resilient (a cache outage just means slower reads via the database, not wrong behavior), and doesn't risk losing data on writes. Write-through earns its cost specifically when read-after-write consistency matters enough to justify the added write latency. Write-behind is genuinely risky, and I'd only reach for it where losing a brief window of writes is truly acceptable — analytics counters, non-critical activity logs. I'd be very cautious applying it to anything with real business consequences, since that data-loss window is easy to forget about until an actual failure makes it painfully concrete.

**Source:** [AWS — Caching Strategies](https://aws.amazon.com/caching/best-practices/), [Redis Documentation — Client-Side Caching Patterns](https://redis.io/docs/latest/develop/reference/client-side-caching/)

---

## 3. How Do You Maintain Consistency Between a Database and a Cache?

**Answer:**

"Perfect, always-consistent synchronization between a database and a cache isn't really achievable without paying a cost that defeats the point of caching — a genuinely synchronous, transactional write to both would reintroduce the same distributed-transaction problems the Transactions category covers for a database-and-Kafka pair, just here between a database and a cache. So the realistic goal is **bounded, well-understood staleness**: the cache might briefly diverge from the database after a write, but that window stays short, predictable, and appropriate for how staleness-tolerant the data actually is — not a pretense that the cache mirrors the database in real time.

Cache-aside with invalidation-on-write (question 2) gets you most of the way there for typical workloads: writes invalidate or update the relevant entry as part of the write path, and a reader hitting a cache miss right after invalidation reads fresh data and repopulates the cache correctly. The genuinely hard part — the next question covers it directly — is the ordering between 'update the database' and 'invalidate the cache,' and the race conditions that ordering creates. That's where most real consistency bugs in cache-aside implementations actually come from."

**Code:**

```java
@Transactional
void updateProductPrice(String productId, BigDecimal newPrice) {
    productRepository.updatePrice(productId, newPrice); // DATABASE first,
    // within the transaction — the invalidation below should happen AFTER
    // the transaction commits, not interleaved with it (question 4 covers
    // exactly why interleaving here is dangerous)
}

@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
void onProductUpdated(ProductUpdatedEvent event) {
    cache.delete(event.getProductId()); // invalidation happens ONLY after the
}                                          // database transaction has DEFINITELY
                                             // committed — never before, never
                                             // interleaved with an in-flight transaction
```

**Follow-up:**

"Maintain consistency" for a cache should always come with an explicit staleness tolerance for the specific data in question. A product catalog description can tolerate several minutes of staleness with zero business impact; a user's current account balance can't. Treating both with the same caching strategy is a common mistake. The actual staff-level skill is stating, for each cached data type, what the maximum acceptable staleness window is and what mechanism actually bounds it to that window — TTL alone (question 10), invalidation-on-write, or a combination — rather than treating "add caching" as one uniform decision applied everywhere.

**Source:** [Redis Documentation — Cache Invalidation Strategies](https://redis.io/docs/latest/develop/reference/client-side-caching/)

---

## 4. What Can Go Wrong With "Update Database, Then Delete Cache"?

**Answer:**

"This is the generally recommended ordering — update the database, then delete the cache entry, rather than updating it directly, since recomputing the new cached value can itself go stale if another write is happening concurrently, while deletion just forces the next reader to recompute fresh. Even so, it has a real, if narrow, race condition worth knowing precisely.

The classic sequence: Thread A reads the cache, gets a miss, and is about to read the database and repopulate the cache. Before Thread A's repopulation write lands, Thread B updates the database with a newer value and deletes the cache entry — which is already empty, so the delete is a no-op. Thread A then finishes its stale read (of the pre-update value, since it read before Thread B's update landed) and writes that stale value into the cache, where it now sits until its TTL expires or another write triggers invalidation. It's a genuine race, if a narrow one, and worth naming explicitly rather than assuming 'update DB, delete cache' is bulletproof."

**Code:**

```text
Timeline illustrating the race:

  Thread A: cache.get(id) -> MISS
  Thread A: db.read(id) -> reads value V1 (the CURRENT value, at this instant)
                                    |
                                    |    Thread B: db.update(id, V2)   <- newer write
                                    |    Thread B: cache.delete(id)     <- no-op, already empty
                                    |
  Thread A: cache.set(id, V1)   <- writes the NOW-STALE V1 into the cache,
                                     AFTER Thread B's newer V2 was already
                                     committed and its (no-op) invalidation ran

  Result: cache now holds STALE V1, while the database correctly holds V2 —
  this persists until the cache entry's TTL eventually expires
```

**Follow-up:**

This is exactly why every cached entry should carry a TTL, even ones that are also explicitly invalidated on write. The TTL is a self-healing backstop, bounding how long a rare race-condition-induced stale entry can survive, even though invalidation-on-write handles the overwhelming majority of updates correctly and immediately. For data where consistency really matters, a **delayed double-delete** — delete the cache entry, wait a short interval long enough for an in-flight stale repopulation like Thread A's to finish, then delete again — narrows this race further. It adds real complexity, though, and I'd only reach for it when a plain TTL backstop genuinely isn't good enough, given how rare this exact race is in most workloads.

**Source:** [Facebook — Scaling Memcache at Facebook (the delete-on-write pattern's origin)](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf)

---

## 5. How Would You Handle Failure Between the Database Update and Cache Invalidation?

**Answer:**

"This is a 'two things need to happen but can't be made atomic across two systems' problem — structurally the same issue the Transactions category's outbox pattern addresses for a database-and-Kafka pair, just here between a database and a cache. If the process crashes, or the cache is briefly unreachable, after the database commits but before the invalidation call succeeds, the cache is left holding a stale entry indefinitely. That's worse than question 4's narrow race, since there's no TTL-triggering event coming — the entry just serves stale data until its TTL naturally expires, if one was even set.

The mitigations, roughly in order of infrastructure cost: **always set a TTL**, even on entries that are also invalidation-driven, so a missed invalidation self-heals within a bounded window instead of persisting forever. That's the cheap baseline, and it's always worth doing. For a stronger guarantee, a **CDC-based invalidation pipeline** — reading the database's write-ahead log with a Debezium-style change-data-capture mechanism, the same idea behind the Transactions category's outbox discussion — invalidates the cache as a reaction to the committed change itself, rather than depending on application code remembering to call invalidate. That decouples 'did the database change actually happen' from 'did the invalidation code path run and succeed,' closing the exact gap a crashed invalidation call leaves open."

**Code:**

```java
// The baseline, cheap mitigation — ALWAYS set a TTL, even for invalidation-
// driven entries, so a missed invalidation self-heals within a bounded window
cache.set(productId, product, Duration.ofMinutes(15)); // even if the
// invalidation call below crashes/fails, this entry expires naturally
// within 15 minutes regardless — bounded staleness, not indefinite staleness

@Transactional
void updateProduct(Product product) {
    productRepository.save(product); // commits successfully
    // PROCESS CRASHES HERE, before the next line ever runs —
    cache.delete(product.getId());     // never executes — cache is now STALE,
}                                         // but bounded by the TTL set above,
                                            // not stale FOREVER
```

```text
CDC-based invalidation (stronger guarantee, more infrastructure):

  Postgres WAL --> Debezium --> Kafka topic (product-changes)
                                       |
                                       v
                        Cache Invalidation Consumer
                        (reacts to the COMMITTED change itself,
                         completely independent of whether the
                         ORIGINAL application code's invalidation
                         call succeeded, failed, or never ran at all)
```

**Follow-up:**

CDC-based invalidation is the more robust answer, structurally closing the same gap the transactional outbox pattern closes for database-to-Kafka publication — the database's own committed write-ahead log becomes the source of truth for "did this change actually happen," and invalidation reacts to that signal instead of depending on the original request's code running a follow-up call successfully. Worth being honest about the trade-off, though: it's real infrastructure investment — a CDC pipeline with its own operational monitoring — and it's only worth it once a TTL backstop's staleness window is genuinely unacceptable for the data in question. For most caching use cases, "always set a TTL as a backstop" is sufficient and much cheaper. I'd save the CDC approach for data where even a brief, TTL-bounded staleness window is a real business problem.

**Source:** [Debezium documentation](https://debezium.io/documentation/reference/stable/index.html), [Facebook — Scaling Memcache at Facebook](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf)

---

## 6. What Is a Cache Stampede, and How Do You Prevent It?

**Answer:**

"A cache stampede — also called a 'thundering herd' against the cache — happens when a popular cache entry expires or gets invalidated, and a large number of concurrent requests for that key all miss at once, and all of them independently hit the database (or recompute an expensive value) at the same moment to repopulate it. What should be one cache-miss-triggered query turns into potentially hundreds or thousands of simultaneous, identical, redundant queries hitting the database at once — enough to overload it, sometimes badly enough to cascade into a broader outage from what started as one cache entry expiring.

The standard prevention mechanisms: **request coalescing/single-flight** — the first request that misses acquires a lock (or otherwise signals 'I'm already fetching this'), and every other concurrent request for the same key waits for that result instead of independently querying the database, then everyone shares the one fetched result. **Probabilistic early expiration** — instead of a hard cutoff exactly at TTL, each read has a small, growing chance of proactively refreshing the entry before it actually expires, as it approaches its TTL — spreading refresh load over time instead of concentrating it at one instant. **Stale-while-revalidate** — serve the slightly stale cached value immediately to any request that arrives right as an entry expires, while kicking off exactly one background refresh, rather than making every concurrent requester wait on a fresh fetch."

**Code:**

```java
// Request coalescing / single-flight — via a distributed lock, so only
// ONE of many concurrent requests for the same key actually hits the database
Product getProduct(String id) {
    Product cached = cache.get(id);
    if (cached != null) return cached;

    String lockKey = "lock:product:" + id;
    boolean acquired = redisTemplate.opsForValue()
        .setIfAbsent(lockKey, "1", Duration.ofSeconds(5)); // SET NX with a short TTL

    if (acquired) {
        try {
            Product fresh = productRepository.findById(id).orElseThrow(); // ONLY
            cache.set(id, fresh, Duration.ofMinutes(10));                    // this ONE
            return fresh;                                                       // request
        } finally { redisTemplate.delete(lockKey); }                            // hits the DB
    } else {
        // did NOT get the lock — someone else is already fetching;
        // wait briefly and retry the cache read, rather than ALSO hitting the DB
        Thread.sleep(50);
        return getProduct(id); // recursive retry — will likely hit the now-populated cache
    }
}
```

**Follow-up:**

Stampedes are specifically dangerous for hot keys. A rarely-accessed key expiring and triggering a handful of redundant queries is a non-event, but a genuinely popular key — a homepage's featured-products list, a widely-referenced config value — expiring under high concurrent traffic is exactly the scenario that turns a routine cache refresh into a database-overload incident. I'd identify the specific hot keys proactively, via cache-hit-rate and access-frequency monitoring (questions 12/13), and apply stampede protection deliberately to those, rather than assume every cached entry needs the same protection. For most low-traffic entries, an occasional handful of redundant queries on expiration is genuinely fine and not worth the added complexity of coalescing or locking.

**Source:** [Vikram Rangnekar — Cache Stampede](https://en.wikipedia.org/wiki/Cache_stampede), [XFetch / Probabilistic Early Expiration (Vattani, Chierichetti, Lowenstein)](https://cseweb.ucsd.edu/~avattani/papers/cache_stampede.pdf)

---

## 7. What Are Cache Penetration and Cache Pollution?

**Answer:**

"**Cache penetration** happens when requests repeatedly ask for keys that don't exist in the database at all. Since there's no valid value to cache — a cache-aside pattern typically only caches values it actually found — every one of those requests misses the cache and hits the database every time, with no cache benefit ever accruing. It can become a real attack vector or accidental-load problem: a malicious actor, or a buggy client, probing many non-existent IDs forces sustained, uncached database load that a normal cache does nothing to absorb, since it structurally can never have a hit for a key with no corresponding data.

**Cache pollution** is a different problem: the cache fills up with entries that are rarely or never accessed again — either from an unusual traffic pattern, like a scraper touching a huge number of distinct, individually-rare keys once each, or a caching policy that's too broad or eager. That crowds out the genuinely hot, frequently-accessed entries under the eviction policy (question 11), degrading the overall hit rate for the traffic that actually matters — even though nothing about the cache looks obviously broken. It's just full of the wrong things."

**Code:**

```java
// Cache penetration mitigation — cache the NEGATIVE result too (question 9),
// so repeated lookups of a non-existent ID stop hitting the database
Optional<Product> getProduct(String id) {
    String cached = cache.get(id);
    if (cached != null) {
        return cached.equals("__NOT_FOUND__")
            ? Optional.empty()       // a cached NEGATIVE result — no DB hit needed
            : Optional.of(deserialize(cached));
    }

    Optional<Product> fromDb = productRepository.findById(id);
    cache.set(id, fromDb.map(this::serialize).orElse("__NOT_FOUND__"),
        fromDb.isPresent() ? Duration.ofMinutes(10) : Duration.ofMinutes(1)); // SHORTER
    return fromDb;                                                              // TTL for
}                                                                                   // negatives
```

**Follow-up:**

**Bloom filters** are the more sophisticated defense against cache penetration, especially for very high-cardinality ID spaces where caching every individual negative result would itself use significant memory. A Bloom filter can answer "does this ID definitely not exist" with zero false negatives — and a small, tunable false-positive rate — using a tiny memory footprint compared to caching every miss individually, letting the application skip the database entirely for IDs the filter confirms don't exist. For cache pollution, it's exactly the kind of problem an eviction-policy choice (question 11) has to account for: a plain LRU policy is vulnerable to exactly this scrape-and-pollute pattern, since a single pass through many rarely-reused keys can evict an entire working set of hot data. That's part of why more sophisticated policies like LFU, or TinyLFU-based admission policies (used by Caffeine, referenced in the JPA/Hibernate file's second-level-cache discussion), exist — they resist this failure mode better than plain recency-based eviction.

**Source:** [Redis Documentation — Bloom Filter (RedisBloom)](https://redis.io/docs/latest/develop/data-types/probabilistic/bloom-filter/), [Caffeine — Window TinyLFU](https://github.com/ben-manes/caffeine/wiki/Efficiency)

---

## 8. Why Should Cache TTLs Include Jitter?

**Answer:**

"If a large number of cache entries all get the exact same TTL, and they were all populated around the same time — a deployment or cold-cache event that populates many entries at once, or a batch job that refreshes a large set of keys together — they'll all expire at roughly the same instant. That recreates the cache-stampede problem from question 6, except now across many keys at once instead of one hot key: a synchronized mass expiration that hits the database with a burst of simultaneous queries, instead of a smooth trickle of individual expirations over time.

Adding **jitter** — a small, randomized adjustment to each entry's actual TTL, say a base TTL of 10 minutes plus or minus a random 0-2 minutes, computed independently per entry — spreads out what would otherwise be a synchronized batch of expirations. It converts a single sharp spike in cache-miss/database load into a smoother trickle across the jitter window, without meaningfully changing the average staleness any one entry experiences."

**Code:**

```java
// WITHOUT jitter — every entry populated in this batch expires at the
// EXACT SAME MOMENT, recreating a synchronized mass-expiration stampede
Duration baseTtl = Duration.ofMinutes(10);
for (Product product : allProducts) {
    cache.set(product.getId(), product, baseTtl); // ALL expire simultaneously,
}                                                     // 10 minutes from now, together

// WITH jitter — spreads expiration across a window, avoiding a synchronized spike
Duration baseTtl = Duration.ofMinutes(10);
for (Product product : allProducts) {
    Duration jitteredTtl = baseTtl.plusSeconds(
        ThreadLocalRandom.current().nextLong(-60, 60)); // +/- 1 minute, PER ENTRY,
    cache.set(product.getId(), product, jitteredTtl);      // computed independently —
}                                                             // expirations now spread
                                                                // smoothly across a 2-minute
                                                                 // window instead of hitting
                                                                  // all at once
```

**Follow-up:**

This exact failure mode is a common, easy-to-overlook root cause of a specific incident shape worth naming directly: "database load spikes every N minutes, in a suspiciously regular, clock-aligned pattern." That's a strong signal pointing at synchronized TTL expiration somewhere upstream, and once it's correctly diagnosed, adding jitter is usually a fast, low-risk fix. Jitter should be applied at TTL-*setting* time, per entry, as shown above — not as some kind of randomized delay in the read path. The goal is desynchronizing when entries expire, not adding latency to reads, and conflating the two is a common mistake when someone reaches for "add some randomness" without pinning down exactly where it needs to live.

**Source:** [AWS — Caching Best Practices, TTL jitter](https://aws.amazon.com/caching/best-practices/)

---

## 9. How Would You Cache Negative Results Safely?

**Answer:**

"Caching a 'not found' result — question 7's penetration mitigation — is genuinely valuable, since without it, repeated lookups for a non-existent key hit the database forever. But it needs care, because a negative result is different from a positive one in a couple of important ways.

First, the negative-result marker needs to be unambiguous — distinguishable from any legitimate cached value, including a legitimately empty or null-ish real value if the data model allows one. A sentinel value or a distinct wrapper is safer than caching a plain `null` and hoping the client's null-handling happens to distinguish 'not found' from 'not yet cached at all,' which is easy to get wrong. Second, negative results should generally get a shorter TTL than positive ones — the data might not exist yet at read time but get created moments later, and a long negative-cache TTL would mask that new data's existence for longer than necessary. A short negative TTL bounds how long a 'not found' answer can stay wrong after the real data starts existing."

**Code:**

```java
private static final String NOT_FOUND_MARKER = "__NOT_FOUND__"; // unambiguous
// sentinel — cannot collide with any legitimate serialized product value

Optional<Product> getProduct(String id) {
    String cached = cache.get(id);
    if (NOT_FOUND_MARKER.equals(cached)) {
        return Optional.empty(); // cached NEGATIVE result — no DB call needed
    }
    if (cached != null) {
        return Optional.of(deserialize(cached)); // cached POSITIVE result
    }

    Optional<Product> fromDb = productRepository.findById(id);
    if (fromDb.isPresent()) {
        cache.set(id, serialize(fromDb.get()), Duration.ofMinutes(30)); // LONGER TTL
    } else {
        cache.set(id, NOT_FOUND_MARKER, Duration.ofSeconds(30)); // SHORTER TTL —
    }                                                                // bounds how long
    return fromDb;                                                     // a "not found"
}                                                                         // answer can mask
                                                                            // newly-created data
```

**Follow-up:**

Negative-result caching interacts directly with the invalidation discipline from questions 3-5. If a resource with a previously-cached "not found" entry gets created afterward, the creation path needs to explicitly invalidate that specific negative entry — not just rely on the short TTL to eventually expire it — or newly-created data can appear not to exist for up to the negative TTL's duration. That's a genuinely confusing bug if the "invalidate on write" logic was only ever designed with updates to existing records in mind, not the create-after-a-cached-miss case. And for a resource type where "not found" lookups are rare in normal operation, negative caching might not be worth the extra complexity at all — it's specifically valuable when penetration-style repeated-miss traffic (question 7) is a genuine, measured problem, not a default to apply regardless of actual access patterns.

**Source:** [AWS — Caching Best Practices](https://aws.amazon.com/caching/best-practices/)

---

## 10. How Do You Select a TTL?

**Answer:**

"TTL selection is a trade-off between **staleness tolerance** — how fast this data changes, and how much it matters if a reader sees a slightly outdated value — and **cache effectiveness** — a longer TTL means a higher hit rate and less database load, but also a longer staleness window. There's no universal correct TTL; it has to come from the specific data's actual characteristics, not from convention or a copy-pasted value from an unrelated use case.

My approach: start from the data's actual update frequency and business staleness tolerance. A product's list price, which might change a few times a month and where a few minutes of staleness has zero real impact, can reasonably use a TTL of many minutes to hours. A real-time inventory count during a flash sale, where staleness directly causes overselling, needs a TTL of seconds at most — or arguably shouldn't lean on TTL-based staleness at all, and should use invalidation-on-write as the primary consistency mechanism (question 3), with TTL as a pure backstop (questions 4/5). I'd also weigh the cost of a cache miss: data that's expensive to recompute — a heavy aggregation query, an expensive external API call — deserves a longer TTL even when it's moderately staleness-sensitive, since the cost of occasional staleness is often cheaper than frequent expensive recomputation."

**Code:**

```java
// Different TTLs, deliberately chosen per data characteristic — NOT a single
// blanket TTL applied uniformly across the whole application
cache.set("product:price:" + id, price, Duration.ofHours(1));       // low
// change frequency, low staleness sensitivity -> long TTL is fine

cache.set("inventory:count:" + sku, count, Duration.ofSeconds(5));  // high
// change frequency during a sale, HIGH staleness sensitivity (overselling
// risk) -> short TTL, AND ideally invalidation-on-write as the PRIMARY
// consistency mechanism, with this TTL purely as a self-healing backstop

cache.set("analytics:daily-summary:" + date, summary, Duration.ofHours(24)); // EXPENSIVE
// to recompute (a heavy aggregation query), and staleness within a day is
// genuinely irrelevant for a "daily summary" -> long TTL clearly justified
```

**Follow-up:**

TTL selection shouldn't be a one-time decision made at implementation time and never revisited. It's worth checking periodically against actual observed hit rates and staleness complaints — if users or downstream systems report staleness for a specific value, the TTL might be too long for that data's real sensitivity; if hit rates are surprisingly low for a value that should be stable, the TTL might be shorter than it needs to be, generating unnecessary database load. Treat TTL as a tuned, monitored parameter rather than a fixed, permanent choice. And for data whose staleness tolerance genuinely varies by context — the same product data might tolerate more staleness on a low-traffic browse page than on a checkout page double-checking current price — it's legitimate to use different TTLs, or bypass the cache entirely, depending on which use case is actually reading it.

**Source:** [AWS — Caching Best Practices](https://aws.amazon.com/caching/best-practices/)

---

## 11. Compare Redis Eviction Policies

**Answer:**

"Once Redis reaches its configured `maxmemory` limit, its eviction policy decides what happens next: reject new writes outright, or evict existing keys to make room, and if evicting, which keys to choose.

`noeviction` — the default — simply returns an error on any write once memory is full, though reads still work. This is the right choice for a system-of-record use case (question 1), where losing data via silent eviction would be a correctness bug, not just degraded performance. You'd rather get a loud write failure than silently lose data.

`allkeys-lru` evicts the least-recently-used key across the whole keyspace, regardless of whether it has a TTL. It's the most common choice for a pure-cache setup, since 'keep what's actually being used, discard what isn't' is a reasonable approximation with low overhead.

`volatile-lru` uses the same LRU logic but restricts it to keys that have a TTL — keys with no expiration are never evicted. That's useful when a single Redis instance mixes cache-role keys (with TTLs) and system-of-record-role keys (deliberately without), letting eviction pressure fall only on the cache-role subset.

`allkeys-lfu` and `volatile-lfu` evict based on frequency of access rather than recency — a key accessed constantly but not in the last few seconds is kept over one accessed once, very recently. This resists the pollution pattern from question 7 better than pure LRU, since it weights actual access frequency over mere recency.

`volatile-ttl` evicts the key with the nearest expiration first, among keys with a TTL. It's a narrower, less commonly used policy for cases where 'evict what was going to expire soonest anyway' is a more meaningful signal than recency or frequency."

**Code:**

```conf
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru   # typical PURE CACHE deployment — evict least-
                                  # recently-used, regardless of TTL presence

# For a MIXED deployment (cache-role keys with TTLs, system-of-record keys
# WITHOUT TTLs, coexisting) — restrict eviction pressure to the cache-role subset
maxmemory-policy volatile-lru

# For a genuine system-of-record deployment — NEVER silently evict; fail
# loudly on writes instead, since losing this data would be a real bug
maxmemory-policy noeviction
```

**Follow-up:**

Mixing system-of-record and pure-cache keys in the same Redis instance is itself a bit of a design smell when it's practical to avoid. It forces a compromise policy like `volatile-lru`, which has to distinguish the two roles by TTL presence alone — fragile if any code path accidentally sets, or forgets to set, a TTL on the wrong kind of key. I'd generally separate these into different logical databases, or better, entirely separate Redis instances or clusters, so each gets an eviction policy and `maxmemory` sizing genuinely matched to its actual role, rather than relying on a subtle TTL-presence convention to keep the two from interfering under memory pressure.

**Source:** [Redis Documentation — Eviction Policies](https://redis.io/docs/latest/develop/reference/eviction/)

---

## 12. How Do Hot Keys Affect Redis?

**Answer:**

"Redis's command execution is single-threaded — even in cluster mode, each key is served by exactly one node, and that node processes commands for that key one at a time. So a single, extremely popular key — a 'hot key' — can become a genuine bottleneck regardless of how much total capacity the broader cluster has, since scaling out by adding more nodes does nothing to help if that key's requests all land on the same shard.

That's a fundamentally different scaling problem than general capacity. A cluster with plenty of aggregate throughput headroom can still see one hot key's node pegged at high CPU or network utilization, causing elevated latency for every key co-located on that same node — not just the hot key itself — while every other node sits comfortably underutilized. This is exactly the kind of thing that shows up as 'our cluster has plenty of spare capacity overall, but we're still seeing latency spikes' — a symptom that looks like a capacity problem but is actually a data-distribution problem no amount of horizontal scaling fixes on its own."

**Code:**

```text
Redis Cluster with 3 shards, hash-slot-based key distribution:

  Shard 1: keys hashing to slots 0-5460      <- "featured-products" lands here
  Shard 2: keys hashing to slots 5461-10922
  Shard 3: keys hashing to slots 10923-16383

  If "featured-products" receives 80% of the ENTIRE workload's read traffic
  (a genuinely common pattern — a homepage's most-viewed content), Shard 1
  absorbs almost all of that load, becoming saturated, WHILE Shards 2 and 3
  sit nearly idle — adding a 4th shard does NOTHING to help, since
  "featured-products" is still just ONE key, served by exactly ONE shard,
  no matter how many total shards the cluster has
```

**Follow-up:**

This is exactly why Redis Cluster's horizontal scaling helps a lot with aggregate load across many distinct keys but gives zero relief for one genuinely hot key. The fix has to happen at the data-access-pattern level (question 13's mitigations), not the infrastructure level, and recognizing "this is a hot-key problem, not a capacity problem" early is the actual diagnostic skill here — throwing more nodes at a hot-key-caused latency spike is wasted effort. It's also worth recognizing this as an instance of a more general distributed-systems pattern: sharding distributes aggregate load well, but any single logical unit of data — a key, a database row, a Kafka partition — still has a ceiling set by whatever single node ultimately serves it. That's not unique to Redis.

**Source:** [Redis Documentation — Cluster Specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)

---

## 13. How Would You Detect and Mitigate Hot Keys?

**Answer:**

"**Detection**: Redis has a built-in `--hotkeys` mode for `redis-cli`, using the approximate LFU-based sampling already present internally for the `allkeys-lfu` policy, that surfaces the most-frequently-accessed keys directly with no extra tooling needed. Beyond that, per-shard CPU and network monitoring, combined with request-level logging that captures the specific key accessed, lets you correlate 'this node is saturated' with 'these keys are responsible for most of its traffic.'

**Mitigation**, once you've found a hot key, depends on the access pattern. **Local, in-process caching** of the hot key's value inside each application instance — an in-memory cache with a short TTL sitting in front of Redis — can absorb most read traffic before it ever reaches Redis at all, since a lot of that traffic is just redundant reads of the same, barely-changing value. **Key splitting**, for a counter or aggregatable value specifically, splits the single hot key into N sharded sub-keys (`counter:0` through `counter:N-1`, chosen by a random or round-robin distribution per write), spreading writes across multiple keys and, in cluster mode, potentially multiple shards — then you sum across all N sub-keys when a read needs the total. **Read replicas** work for a hot key that's read-heavy: routing reads across multiple replicas distributes read load, though writes still funnel through the primary."

**Code:**

```bash
# Detecting hot keys directly, no external tooling needed
redis-cli --hotkeys
```

```java
// Local, in-process cache in FRONT of Redis, specifically for a known hot key —
// absorbs the vast majority of traffic before it ever reaches Redis at all
private final Cache<String, String> localHotKeyCache = Caffeine.newBuilder()
    .expireAfterWrite(Duration.ofSeconds(2)) // short — bounded staleness,
    .maximumSize(100)                            // but massively reduces Redis load
    .build();

String getFeaturedProducts() {
    return localHotKeyCache.get("featured-products",
        key -> redisTemplate.opsForValue().get(key)); // Redis only hit once
}                                                          // per 2-second window,
                                                             // PER APPLICATION INSTANCE,
                                                              // regardless of how many
                                                               // actual requests arrive

// Key splitting — spreads a hot COUNTER across multiple sub-keys
void incrementViewCount(String contentId) {
    int shard = ThreadLocalRandom.current().nextInt(10);
    redisTemplate.opsForValue().increment(contentId + ":shard:" + shard);
}

long getTotalViewCount(String contentId) {
    long total = 0;
    for (int i = 0; i < 10; i++) {
        String value = redisTemplate.opsForValue().get(contentId + ":shard:" + i);
        total += value != null ? Long.parseLong(value) : 0;
    }
    return total; // aggregated across all 10 sub-keys, spread across shards
}
```

**Follow-up:**

Local in-process caching can feel like a slightly cheap fix, but for a read-heavy hot key it's often the most effective mitigation, because it eliminates network round-trips to Redis entirely for that key rather than just spreading load across more capacity. For content that's read constantly and changes rarely — a featured-products list, a global config value — even a very short local TTL absorbs most of the traffic, and I'd generally reach for it before something more complex like key splitting. Key splitting is better saved for write-heavy hot keys, like a genuinely high-frequency counter, where local caching doesn't help at all, since a write actually needs to reach the authoritative store. It also adds real complexity on the read side — fanning out and summing across sub-keys — which is worth weighing against the specific write-throughput problem it solves.

**Source:** [Redis Documentation — redis-cli --hotkeys](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/), [Caffeine cache library](https://github.com/ben-manes/caffeine)

---

## 14. How Do Large Keys Affect Latency and Cluster Behavior?

**Answer:**

"Because Redis's command execution is single-threaded per node, a single command that has to process a large value — a huge `List`, `Hash`, `Set`, or one very large string — blocks that node's entire event loop for the duration of that operation. Every other client's command against that same node, even for completely unrelated small keys, has to wait behind it. `LRANGE bigkey 0 -1` on a multi-million-element list, or `SMEMBERS` on a huge set, can stall a node for a noticeable duration, and everything else hitting that node during that window sees elevated latency, purely because of one oversized key.

This also affects cluster resharding: when Redis Cluster moves a key from one shard to another during rebalancing or scale-out, it has to migrate that key's entire value atomically. A very large key takes proportionally longer to migrate, and during that window, operations against it can be delayed or, in some cases, briefly blocked — making cluster rebalancing slower and riskier compared to a cluster where keys are more uniformly, modestly sized."

**Code:**

```bash
# Finding large keys proactively, before they become an incident
redis-cli --bigkeys

# A dangerous pattern — a single key holding an unbounded, ever-growing
# collection, with no size limit ever enforced
LPUSH activity-log:user-12345 "event data..." # if this list is NEVER trimmed,
# it can grow to millions of elements over a user's lifetime, and any
# LRANGE against it becomes an increasingly expensive, blocking operation
```

```java
// FIX — bound the collection's size explicitly, at write time, rather than
// letting it grow unboundedly
redisTemplate.opsForList().leftPush(key, eventData);
redisTemplate.opsForList().trim(key, 0, 999); // cap at 1000 most-recent
// entries, EVERY write — the key's size is now BOUNDED by construction,
// never growing large enough to become a blocking-operation problem
```

**Follow-up:**

Unbounded collections stored in a single Redis key — a list, set, or hash with no size cap enforced — are worth catching in design review, before they become a latency incident. `redis-cli --bigkeys` is a useful reactive diagnostic, but the actual fix is architectural discipline: any collection-type key that can grow unboundedly over time — per-user activity logs, accumulating event streams — needs an explicit size cap at write time, via `LTRIM`, capped `ZADD` with score-based eviction, or splitting into time-bucketed keys that naturally age out. Catching this early is much cheaper than fixing an already-oversized key in production.

**Source:** [Redis Documentation — redis-cli --bigkeys](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/), [Redis Documentation — Cluster Specification, resharding](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)

---

## 15. What Is the Difference Between Redis Replication, Sentinel, and Cluster?

**Answer:**

"**Replication** is the foundational primitive: one or more replicas asynchronously copy a primary's data, giving you read scalability and a basic durability foundation, but no automatic failover. If the primary fails, a human or a script has to manually promote a replica and reconfigure clients to point at it.

**Sentinel** adds automatic failover on top of plain replication. A small quorum of Sentinel processes continuously monitors the primary's health, and once a quorum of them independently agrees the primary is genuinely down — not just unreachable from one Sentinel's own perspective, which could just be a network partition on that Sentinel's side — they elect and promote a replica automatically, and notify clients of the new topology through Sentinel's own pub/sub mechanism. That solves the manual-intervention problem, but Sentinel still manages a single logical dataset — it doesn't shard data at all.

**Cluster** provides both automatic failover, built directly into Cluster itself without needing separate Sentinel processes, and horizontal sharding: data is partitioned across multiple primary nodes, each owning a subset of the 16384 hash slots, and each can have its own replicas for failover. That lets both data volume and throughput scale horizontally, which neither plain replication nor Sentinel alone provides."

**Code:**

```text
Replication only:
  Primary --(async replication)--> Replica
  Failover: MANUAL — a human/script must promote the replica and
  reconfigure every client to point at the new primary

Sentinel:
  Sentinel-1, Sentinel-2, Sentinel-3 (quorum) monitor: Primary --> Replica
  Failover: AUTOMATIC — Sentinels detect primary failure via quorum
  agreement, promote a replica, and notify clients of the new topology
  Still ONE logical dataset — no data sharding

Cluster:
  Shard A (Primary A + Replica A) — owns hash slots 0-5460
  Shard B (Primary B + Replica B) — owns hash slots 5461-10922
  Shard C (Primary C + Replica C) — owns hash slots 10923-16383
  Failover: AUTOMATIC, per-shard, built into Cluster itself
  Data IS sharded — horizontal scaling of BOTH capacity and throughput
```

**Follow-up:**

Plain replication with manual failover is rarely a good production default, given how cheap Sentinel is to add — Sentinel, or a managed cloud provider's equivalent, should be the baseline for any production Redis deployment that can't tolerate a manual-intervention window during a primary failure. Cluster's added complexity — data sharding, client-side redirect and topology awareness, harder multi-key operations since keys can now live on different shards, per question 23's Redis-transaction discussion — is worth taking on once a single node's capacity or throughput genuinely isn't enough. I'd avoid reaching for Cluster prematurely "for scalability" if a well-sized primary-plus-replicas-plus-Sentinel setup is still comfortably within capacity, since Cluster's operational and application-level complexity is a real cost that shouldn't be paid before it's actually needed.

**Source:** [Redis Documentation — Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/), [Redis Documentation — Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/), [Redis Documentation — Cluster Tutorial](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/)

---

## 16. What Consistency Guarantees Does Redis Replication Provide?

**Answer:**

"Redis replication is asynchronous by default: the primary applies a write and acknowledges it to the client immediately, then streams the change to its replicas — with no guarantee a replica has received, let alone applied, it by the time the client gets its acknowledgment. That means replication gives you only eventual consistency by default: a read against a replica can, and routinely will, briefly return stale data relative to what the primary already acknowledged. There's no built-in guarantee on how large that lag gets under normal operation — typically it's small, sub-millisecond to low-milliseconds under healthy conditions, but it can grow significantly under replica load, network issues, or a backlog of pending replication data.

For cases where that staleness is unacceptable, Redis offers `WAIT` — a command that blocks until a specified number of replicas have acknowledged the write, or a timeout elapses — letting a client trade write latency for a stronger, more synchronous-feeling guarantee on a per-write basis. Even `WAIT` doesn't make replication itself synchronous by default; it's an opt-in check layered on top of the underlying async mechanism."

**Code:**

```java
// Default — asynchronous, eventually consistent; a read against a replica
// immediately after this write MIGHT still see the OLD value
redisTemplate.opsForValue().set("key", "new-value"); // acknowledged as soon
// as the PRIMARY applies it — replicas may not have it yet at all

// Using WAIT explicitly, for writes that need a stronger guarantee before
// proceeding — trades latency for confidence that at least N replicas have it
redisTemplate.execute((RedisCallback<Long>) connection ->
    (Long) connection.execute("WAIT", "1".getBytes(), "1000".getBytes())); // wait for
    // at least 1 replica to acknowledge, up to 1000ms, before considering
    // this write "safe enough" to proceed on
```

**Follow-up:**

This asynchronous default has a real, sometimes-overlooked failover implication: because replication is async, a primary can acknowledge a write to a client and then fail before that write ever reaches any replica. If Sentinel or Cluster then promotes a replica that never received it, the write is permanently lost — even though the client got a successful acknowledgment. That's a genuine, if narrow-window, data-loss risk built into Redis's default replication model, and it's exactly the trade-off that should inform the question-1 decision about whether Redis is a pure cache (where this loss window is a non-issue, since the database stays authoritative) or a system of record (where this failure mode needs to be explicitly accepted, mitigated with `WAIT`-based stronger acknowledgment, or avoided by choosing a different store for that data).

**Source:** [Redis Documentation — Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/), [Redis Documentation — WAIT command](https://redis.io/docs/latest/commands/wait/)

---

## 17. What Happens During Redis Failover?

**Answer:**

"With Sentinel, or Cluster's built-in failover, managing the process: Sentinels continuously monitor the primary with periodic health checks. Once a quorum of them independently agrees the primary is genuinely unreachable — quorum specifically to avoid one Sentinel's own network partition triggering an unnecessary failover — the Sentinels elect one of themselves to drive the failover, pick the best-positioned replica (typically the one with the most up-to-date replication offset) to promote, promote it, reconfigure the remaining replicas to follow the new primary, and update Sentinel's published configuration so clients asking 'who is the current primary' get the new address.

The practical consequence: there's a real gap between the original primary failing and a new one being fully promoted and ready to accept writes. During that gap, write availability is lost entirely — reads against surviving replicas might still work, depending on client configuration, but writes have nowhere to go until promotion finishes. And any writes the old primary acknowledged but hadn't yet replicated to the promoted replica (question 16's async-replication data-loss risk) are permanently lost as part of this transition, not just delayed."

**Code:**

```text
Failover timeline:

  t=0s:  Primary fails (crash, network partition, hardware failure)
  t=0-5s: Sentinels' health checks begin failing against the primary
  t=5-10s: Quorum of Sentinels agrees primary is DOWN (requires multiple
           INDEPENDENT Sentinels to agree, not just one — avoiding a false
           positive from one Sentinel's own isolated network issue)
  t=10-15s: Elected Sentinel selects the best replica (least replication lag)
            and promotes it to primary
  t=15s+:  New primary accepts writes; remaining replicas reconfigured to
           replicate from it; Sentinel's published config updated

  DURING this ~10-15 second window: writes are UNAVAILABLE. Any write the
  OLD primary acknowledged to a client between its last successful
  replication to the NOW-PROMOTED replica and its actual failure is
  PERMANENTLY LOST — it never reached the replica that became the new primary
```

**Follow-up:**

Applications relying on Redis need to be explicitly designed to tolerate this write-unavailability window gracefully. A request that tries to write during a failover should fail fast with a clear error, or degrade gracefully (question 28), rather than hanging or retrying indefinitely against an endpoint that genuinely can't accept writes for those 10-15 seconds. Failover timing is also tunable — Sentinel's `down-after-milliseconds`, quorum size, and related settings — and it's a real trade-off: a faster failure-detection configuration shrinks the write-unavailability window but raises the risk of a false-positive failover from a transient blip, while a more conservative one is slower to fail over but more resistant to unnecessary, disruptive failovers from brief, self-resolving network issues.

**Source:** [Redis Documentation — Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/)

---

## 18. Why Can a Distributed Lock Be Unsafe?

**Answer:**

"A naive distributed lock built on `SET lock-key unique-value NX PX 30000` — set if not already present, with a 30-second expiry — has a real, non-obvious safety gap: the lock's expiry is a time-based guess about how long the holder needs, not a guarantee tied to whether that holder is actually still alive and making progress. If the process holding the lock hits a long pause — a GC pause, tying back to the JVM/GC file's stop-the-world discussion, a network delay, or just legitimately taking longer than the assumed 30 seconds — the lock can expire and get acquired by a second process while the first one is still running, still believes it holds the lock, and is still actively doing the work the lock was meant to protect. Now two processes both believe they hold exclusive access, which is exactly the safety violation a mutual-exclusion lock exists to prevent.

This isn't a Redis-specific bug you can fix with a longer TTL — it's a structural property of any lock whose validity depends purely on a timer rather than verifiable, ongoing proof the holder is still alive and hasn't been superseded. That's why naive TTL-based distributed locking is a well-documented unsafe pattern for genuinely correctness-critical mutual exclusion."

**Code:**

```java
// UNSAFE — TTL expiry has NO relationship to whether the holder is actually
// still alive/making progress; a long GC pause or network delay can cause
// the lock to expire while this process still believes it holds it
boolean acquired = redisTemplate.opsForValue()
    .setIfAbsent("lock:inventory:sku-100", "holder-A", Duration.ofSeconds(30));
if (acquired) {
    doSomeWorkThatMightTakeLongerThan30Seconds(); // if a GC pause delays this
    // past 30s, the lock EXPIRES and another process can acquire it — TWO
    // processes now believe they hold exclusive access simultaneously
    redisTemplate.delete("lock:inventory:sku-100"); // and THIS delete might now
}                                                       // incorrectly release the
                                                          // OTHER process's lock, since
                                                          // it just deletes by key,
                                                          // with no ownership check at all
```

**Follow-up:**

Worth bringing up Martin Kleppmann's well-known critique of Redlock — Redis's own proposed multi-instance locking algorithm. His argument is precisely this TTL-versus-actual-liveness gap, applied specifically to Redlock's claimed stronger guarantees, and the broader point is that no purely timer-based distributed lock, no matter how many Redis instances it coordinates across, can guarantee true fencing/safety against an arbitrarily-paused process. The fix comes from either accepting the lock as a best-effort optimization — fine if the protected operation is itself idempotent or tolerant of rare double-execution — or from a genuinely different mechanism, like fencing tokens (question 19), that provides safety even when the timer's assumption is violated. The practical takeaway: know what a given distributed lock is actually protecting, and whether that operation can tolerate an occasional double-execution. If it truly can't, a naive TTL-based Redis lock alone isn't a sufficient safety mechanism.

**Source:** [Martin Kleppmann — How to do distributed locking](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html), [Redis Documentation — Distributed Locks with Redis](https://redis.io/docs/latest/develop/use/patterns/distributed-locks/)

---

## 19. Explain Token-Based Lock Ownership

**Answer:**

"The mitigation for question 18's core problem — a lock's TTL expiring while the holder is still, unknowingly, active — is a fencing token. Instead of the lock just being held or not held, every successful acquisition returns a monotonically increasing token, and every operation the lock protects must present that token to whatever resource it's actually modifying. That resource must reject any operation presenting a token lower than the highest it has already seen.

This doesn't prevent two processes from both believing they hold the lock at the same time — the underlying TTL-expiry race from question 18 can still happen. What it ensures is that if it does happen, only the process with the higher, more recent token can actually succeed at the protected operation. The stale holder, even if it still believes it holds the lock and tries to act, gets rejected by the resource itself, because its token is now lower than one already presented by the newer holder. This shifts the actual safety guarantee away from 'the lock's timer is trustworthy' — which question 18 shows it isn't — to 'the protected resource enforces monotonic ordering,' which is a genuinely stronger guarantee."

**Code:**

```java
// Fencing-token-based acquisition — every acquisition gets a MONOTONICALLY
// INCREASING token, via Redis's atomic INCR
long acquireLockWithFencingToken(String lockKey) {
    boolean acquired = redisTemplate.opsForValue()
        .setIfAbsent(lockKey, "holder", Duration.ofSeconds(30));
    if (!acquired) throw new LockNotAcquiredException();
    return redisTemplate.opsForValue().increment("fencing-token-counter"); // e.g. returns 34
}

// The PROTECTED RESOURCE (a database row, in this example) enforces the
// ordering itself — this is where the ACTUAL safety guarantee lives,
// NOT in the Redis lock's own timer
@Transactional
void updateInventory(String sku, int newQuantity, long fencingToken) {
    int updated = jdbcTemplate.update(
        "UPDATE inventory SET quantity = ?, last_fencing_token = ? " +
        "WHERE sku = ? AND last_fencing_token < ?", // REJECTS a stale token —
        newQuantity, fencingToken, sku, fencingToken); // even if the CALLER
    if (updated == 0) {                                    // still believes it
        throw new StaleLockException("a newer holder has already acted");
    }                                                        // holds the lock
}
```

**Follow-up:**

Fencing tokens require the protected resource itself to cooperate — it has to store and check the last-seen token, as in the SQL example above — which is a real implementation cost. That's why they're the right answer specifically for correctness-critical operations, while for lower-stakes work where an occasional rare double-execution is genuinely tolerable, a plain TTL-based lock combined with idempotent operation design is often a perfectly pragmatic choice. The decision comes down to one question: is the operation this lock protects idempotent, or otherwise safely tolerant of rare double-execution? If yes, a simple lock is fine. If no — a genuinely non-idempotent, correctness-critical mutation — fencing tokens, or a different mechanism entirely like the pessimistic database-row-locking from the Transactions category (which doesn't have this liveness problem, since it's tied to an actual database session rather than an independent timer), are the more defensible choice.

**Source:** [Martin Kleppmann — How to do distributed locking](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)

---

## 20. When Should You Avoid Distributed Locks Entirely?

**Answer:**

"I'd avoid a distributed lock whenever the problem can instead be solved with an atomic operation on the data store itself — which, for a large fraction of real 'we need mutual exclusion' scenarios, it actually can. A single atomic `UPDATE inventory SET quantity = quantity - ? WHERE sku = ? AND quantity >= ?` — checking sufficiency and decrementing in one statement — achieves the actual business requirement, 'don't oversell inventory,' without any lock at all, and without question 18's TTL-based liveness problems, because the database's own atomicity guarantee is doing the work, not an external, timer-based coordination mechanism.

More broadly, I'd avoid distributed locks whenever the operation can be made idempotent instead — if running it twice concurrently produces the same correct result either way, there's no need to prevent concurrent execution at all. A database's own transactional guarantees, optimistic or pessimistic locking, already solve this for data that lives in that database — bolting on a separate external Redis lock on top of a database that already handles concurrency well is usually unnecessary complexity. I'd reserve genuine distributed locks for coordination problems that don't map onto a single atomic operation or an idempotency-based design — like making sure only one instance in a fleet runs a scheduled job, where there's no natural database statement that expresses that requirement directly."

**Code:**

```sql
-- NO LOCK NEEDED — a single atomic statement expresses the actual business
-- requirement directly, with the database's own atomicity as the guarantee
UPDATE inventory SET quantity = quantity - 1
WHERE sku = 'WIDGET-100' AND quantity >= 1;
-- 0 rows affected means "insufficient stock" — correctly, safely, atomically,
-- under ANY level of concurrency, with ZERO distributed locking involved
```

```java
// A GENUINE distributed-lock use case — coordinating "only one instance
// across a fleet should run this scheduled job" has no natural mapping
// onto a single atomic database statement; a lock is the RIGHT tool here
@Scheduled(cron = "0 0 * * * *")
void runHourlyReconciliationJob() {
    boolean acquired = redisTemplate.opsForValue()
        .setIfAbsent("lock:hourly-reconciliation", instanceId, Duration.ofMinutes(50));
    if (!acquired) return; // another instance already running this hour's job
    doReconciliation();
}
```

**Follow-up:**

The general principle worth stating explicitly in an architecture review: reach for atomicity at the data layer first, idempotency second, and a distributed lock only as a last resort for coordination problems that don't map onto either of the first two. Teams that default to "add a Redis lock" as the reflexive answer to any concurrency concern often end up with unnecessary complexity and the real safety gaps from question 18, when a simpler, more robust, lock-free solution was already sitting in the database they were already using. Even the legitimate "run this job on exactly one instance" case is often better served by dedicated tooling — a Kubernetes `CronJob` with the right concurrency policy, or Quartz's clustered-scheduler mode with database-backed coordination — rather than a hand-rolled Redis lock, since those tools have already worked through edge cases like a job that runs long or a node that dies mid-execution.

**Source:** [Martin Kleppmann — How to do distributed locking](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)

---

## 21. Compare Fixed-Window, Sliding-Window, and Token-Bucket Rate Limiting

**Answer:**

"**Fixed window** counts requests within a fixed, aligned time window — say, 'requests this calendar minute' — and resets to zero at each boundary. It's simple to implement, just a counter key with a TTL matching the window, but it has a real correctness gap at the boundaries: a client can send its full quota right at the end of one window and its full quota again right at the start of the next, getting up to double the intended rate in a short span straddling the boundary, even though neither individual window technically exceeded its limit.

**Sliding window** — either a true log of individual request timestamps, or the cheaper, more common approximation: a weighted average between the current and previous fixed windows, proportional to how far into the current window you are — fixes the boundary-burst problem by evaluating rate over a continuously moving window instead of discrete, resettable buckets. That costs somewhat more computation and storage than a single counter.

**Token bucket** models a bucket holding up to a maximum number of tokens, refilling at a steady rate over time. Each request consumes one token, and gets rejected only if the bucket is empty. This naturally supports bursts — a client that's been idle has a full bucket and can burst up to capacity all at once — while still enforcing a steady long-run average via the refill rate. That's often a better match for real, naturally bursty traffic than a strict, unforgiving fixed rate."

**Code:**

```java
// Fixed window — simple, but has the boundary-burst gap
String key = "ratelimit:" + userId + ":" + currentMinute();
Long count = redisTemplate.opsForValue().increment(key);
redisTemplate.expire(key, Duration.ofMinutes(1));
boolean allowed = count <= 100; // up to 200 requests possible across a
                                   // boundary (100 at 11:59:59, 100 at 12:00:00)

// Token bucket — naturally supports bursts, smooths long-run rate
class TokenBucket {
    long tokens;
    long lastRefillTimestamp;
    static final long CAPACITY = 100, REFILL_RATE_PER_SECOND = 10;

    boolean tryConsume() {
        long now = System.currentTimeMillis();
        long elapsed = now - lastRefillTimestamp;
        tokens = Math.min(CAPACITY, tokens + (elapsed / 1000) * REFILL_RATE_PER_SECOND);
        lastRefillTimestamp = now;
        if (tokens > 0) { tokens--; return true; }
        return false;
    }
}
```

**Follow-up:**

My practical default for rate-limiting real client traffic is token bucket, mainly because real traffic is naturally bursty — a user opening several tabs at once, a batch of retries — and a token bucket accommodates that gracefully while still enforcing a meaningful long-run average. A strict fixed-window limit can feel unnecessarily punishing for legitimate, momentarily-bursty usage that never actually exceeds a reasonable average rate. I'd reach for fixed-window when implementation simplicity matters more than precision and the boundary-burst gap's consequence is acceptable, and for a true sliding-window log specifically when precise, gap-free enforcement is a hard requirement — a security-sensitive limit like login-attempt throttling, where the boundary gap could actually be exploited.

**Source:** [Cloudflare — Counting Things: Rate Limiting](https://blog.cloudflare.com/counting-things-a-lot-of-different-things/), [Redis Documentation — Rate Limiting Patterns](https://redis.io/docs/latest/develop/use-cases/rate-limiter/)

---

## 22. How Would You Build an Atomic Rate Limiter Using Lua?

**Answer:**

"A rate limiter built from separate Redis commands — a `GET` to check the current count, then an `INCR` if under the limit — has the same check-then-act race condition problem that runs through this whole category: two concurrent requests can both read the same 'under limit' count before either one's increment lands, both proceed, and the limit gets silently exceeded. Redis's Lua scripting (`EVAL`) solves this cleanly, because a Lua script executes atomically on the server — no other client's command can run in between any of its internal operations. So a check-and-increment expressed entirely within one Lua script becomes genuinely atomic as a whole, with no possibility of a race between the check and the increment, no matter how many clients are hitting the same key at once."

**Code:**

```lua
-- rate_limiter.lua — executed ATOMICALLY on the Redis server; no other
-- command from ANY client can interleave with this script's execution
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])

local current = redis.call('INCR', key)
if current == 1 then
    -- Set the TTL ONLY on the request that creates this window (the first
    -- increment). Calling EXPIRE unconditionally on every allowed request
    -- would push the key's expiry forward each time — the window would
    -- never actually roll over as long as requests keep arriving, so a
    -- client sending one request every few seconds could stay rate-limited
    -- indefinitely instead of getting a fresh window every `window` seconds.
    redis.call('EXPIRE', key, window)
end

if current > limit then
    return 0 -- rejected — over limit
end
return 1 -- allowed
```

```java
private static final RedisScript<Long> RATE_LIMIT_SCRIPT =
    RedisScript.of(new ClassPathResource("rate_limiter.lua"), Long.class);

boolean isAllowed(String userId) {
    Long result = redisTemplate.execute(RATE_LIMIT_SCRIPT,
        List.of("ratelimit:" + userId), "100", "60"); // limit=100, window=60s
    return result != null && result == 1;
}
```

**Follow-up:**

Lua's atomicity guarantee is really the same underlying mechanism — single-threaded command execution — that makes plain individual Redis commands atomic in the first place. A Lua script is just a way to compose multiple operations into one larger atomic unit, not a fundamentally different mechanism, which is a useful way to think about when Lua is (and isn't) the right tool: any time an operation needs multiple related steps to happen as one atomic unit — a check-and-increment, a read-modify-write across multiple keys — Lua fits naturally, whereas a single already-atomic command like a plain `INCR` doesn't need it. Worth flagging the operational trade-off too: because a Lua script blocks Redis's single-threaded execution for its whole duration, a slow or unbounded script has exactly the same "blocks the node for everyone" risk as the large-key problem from question 14. Lua is fine for small, bounded operations like rate limiting, but it's not a place to put heavy or unbounded computation.

Also worth flagging a correctness pitfall that's easy to introduce by accident: calling `EXPIRE` unconditionally on every allowed request, instead of only on the request that creates the key (`current == 1`), quietly changes the rate limiter's semantics. A true fixed window is supposed to reset at a fixed boundary regardless of traffic; if every accepted request pushes the TTL forward, the key's expiry keeps sliding as long as requests keep arriving, so the window effectively never rolls over for a client that keeps sending occasional traffic — it only resets once the client goes quiet for a full `window` seconds. That's a meaningfully stricter behavior than the "N requests per calendar-aligned window" semantics the pattern is supposed to provide, so the conditional `EXPIRE` isn't a style nicety — it's what makes the implementation match the stated algorithm.

**Source:** [Redis Documentation — Scripting with Lua](https://redis.io/docs/latest/develop/interact/programmability/eval-intro/), [Redis Documentation — INCR command, "Pattern: rate limiter"](https://redis.io/docs/latest/commands/incr/) (this file's script is the documented "rate limiter 2" pattern, including its conditional-`EXPIRE`-on-`current==1` fix for the race/TTL-reset issue)

---

## 23. How Do Redis Transactions Differ From Relational Transactions?

**Answer:**

"Redis's `MULTI`/`EXEC` mechanism queues a batch of commands on the client's connection and executes them all together, atomically, with no other client's commands interleaving. That part is genuinely similar in spirit to a relational transaction's isolation guarantee. But the differences from a full relational transaction are significant and worth stating precisely, since 'Redis transaction' invites an assumption of stronger semantics than it actually provides.

There's no rollback on a command-level failure within the queued batch. If one command in a `MULTI`/`EXEC` block fails at execution time — as opposed to a syntax error caught when queuing, which does abort the whole thing before execution starts — Redis just keeps executing the remaining commands anyway. There's no ACID-style 'undo everything already applied' behavior for a runtime failure partway through, which is fundamentally different from a relational database rolling back on a constraint violation. There's also no real isolation in the sense of hiding one transaction's in-progress state from concurrent readers until commit — Redis's atomicity is about no interleaving of other clients' commands during execution, not about hiding partial state, which doesn't really apply the same way given the whole batch executes almost instantaneously anyway under Redis's single-threaded model. And there's no equivalent of a `WHERE`-clause-based conditional check spanning the whole transaction — Redis's `WATCH` command gives you a narrower, optimistic-concurrency mechanism instead: abort the whole transaction if a watched key changed before `EXEC`, which is closer in spirit to optimistic locking than to a relational transaction's general isolation model."

**Code:**

```text
MULTI
  INCR counter
  LPUSH bad-command-usage-here  -- a RUNTIME error (wrong arity/type), NOT
                                    -- caught until this command actually executes
  INCR another-counter
EXEC
-- Result: the INCR on "counter" SUCCEEDS, the malformed LPUSH command FAILS
-- (returns an error for that one command), and the SECOND INCR still
-- EXECUTES anyway — there is NO automatic rollback of "counter"'s increment
-- just because a LATER command in the same MULTI/EXEC batch failed
```

```java
// WATCH — Redis's OPTIMISTIC-concurrency mechanism, the closest analog to
// a relational transaction's conditional/isolation behavior, but narrower
redisTemplate.execute(new SessionCallback<Object>() {
    public Object execute(RedisOperations operations) {
        operations.watch("balance"); // start watching this key
        Object currentBalance = operations.opsForValue().get("balance");
        operations.multi();
        operations.opsForValue().set("balance", newComputedValue(currentBalance));
        return operations.exec(); // returns null/empty if "balance" was
        // modified by ANY OTHER client between the WATCH and this EXEC —
        // the whole batch is aborted, and the application must retry,
        // exactly mirroring optimistic locking's version-check-and-retry pattern
    }
});
```

**Follow-up:**

The lack of real rollback is exactly why Lua scripting (question 22) is often the better tool than `MULTI`/`EXEC` when you need genuine conditional logic or multi-step correctness. A Lua script gives you actual programmatic control — checking a value and deciding whether to proceed with subsequent operations before they're issued, all within the same atomic execution — whereas `MULTI`/`EXEC` just queues and runs a fixed, pre-determined batch with no way for one command's behavior to depend on the previous command's actual runtime result. The practical guidance: `WATCH`/`MULTI`/`EXEC` is fine for simple optimistic-concurrency cases — check a value hasn't changed, then apply a fixed set of writes — but Lua is the more powerful, correct tool whenever the operation needs actual conditional logic based on values read during the atomic operation itself.

**Source:** [Redis Documentation — Transactions](https://redis.io/docs/latest/develop/interact/transactions/)

---

## 24. What Do Pipelines Improve, and What Do They Not Guarantee?

**Answer:**

"Pipelining lets a client send multiple commands to Redis without waiting for each individual response before sending the next one. All the commands go out in a batch over the network, and Redis processes and returns all the responses together, dramatically cutting the round-trip overhead compared to sending each command and waiting one at a time. For a client fetching, say, 100 different keys, pipelining can turn 100 round trips into effectively one — a substantial latency win purely from eliminating repeated round-trip cost. This is a network and latency optimization, not a correctness or atomicity feature.

Critically, pipelining gives you no atomicity guarantee at all. Unlike `MULTI`/`EXEC`, other clients' commands can interleave with a pipelined batch's individual commands as Redis processes them one at a time internally — pipelining just changes how commands are transmitted, not how they're executed on the server. Each command in the pipeline is still its own independent, individually-interleavable operation from the server's point of view. If a client needs both the network efficiency of pipelining and a guarantee that no other client's commands interleave with the batch, `MULTI`/`EXEC` — which client libraries typically pipeline under the hood anyway — is the tool that provides that, not plain pipelining alone."

**Code:**

```java
// Pipelining — network efficiency ONLY; commands are STILL individually
// interleavable with other clients' commands on the server side
List<Object> results = redisTemplate.executePipelined(
    (RedisCallback<Object>) connection -> {
        for (String key : hundredKeys) {
            connection.get(key.getBytes()); // all 100 GETs sent in ONE
        }                                       // network round trip, but each
        return null;                              // is STILL its own independent,
    });                                              // individually-interleavable
                                                        // operation on the server
```

**Follow-up:**

The common, real mistake this distinction guards against is assuming pipelining gives you the same atomicity as `MULTI`/`EXEC` because they're both "batching multiple commands together." It's an easy confusion, and code that pipelines a read-then-conditional-write sequence, expecting no other client to interleave in between, is silently vulnerable to exactly the race conditions this whole category has been building toward — pipelining offers zero protection against that. The clean distinction: reach for pipelining purely to cut network round trips for a batch of otherwise-independent commands; reach for `MULTI`/`EXEC`, or Lua for anything needing real conditional logic, when atomicity or no-interleaving is the actual requirement. Never assume one gives you the other's guarantee.

**Source:** [Redis Documentation — Pipelining](https://redis.io/docs/latest/develop/use/pipelining/)

---

## 25. How Would You Version Cache Keys During a Deployment?

**Answer:**

"The core problem a deployment introduces: if a new application version changes the shape of what's cached — a different serialization format, a different set of fields in a cached DTO, a changed computation that produces a different value under the same key — and the old version is still running during a rolling deployment, both versions reading and writing the same key can produce genuinely broken behavior. The new version might read data the old version wrote in the old shape and fail to deserialize it, or misinterpret it silently, or vice versa.

The standard fix is embedding a version identifier directly into the cache key itself, so old and new versions running simultaneously during a rollout are structurally reading and writing entirely different, non-overlapping keys — eliminating any possibility of cross-version interference. The old version's cache entries become orphaned once the deployment completes, and they just age out via their normal TTL rather than needing explicit cleanup. That's a clean, low-effort trade-off, since the storage cost of some temporarily-orphaned entries is trivial compared to the risk of cross-version corruption."

**Code:**

```java
// Cache key includes an explicit SCHEMA VERSION, not just the entity's own ID —
// old and new app versions, running SIMULTANEOUSLY during a rolling deploy,
// structurally never touch each other's cache entries
private static final int CACHE_SCHEMA_VERSION = 2; // bumped whenever the
                                                       // cached SHAPE changes

String buildCacheKey(String productId) {
    return "product:v" + CACHE_SCHEMA_VERSION + ":" + productId;
    // OLD app instances (still running during the rollout) use "product:v1:*"
    // NEW app instances use "product:v2:*" — ZERO overlap, ZERO cross-version
    // corruption risk, even though both versions are live simultaneously
}
```

**Follow-up:**

The version number should only get bumped when the cached value's shape or computation logic actually changes — not on every deployment. Bumping it indiscriminately would mean every rolling deployment causes a full, unnecessary cache-cold-start, with the database absorbing a cache-miss burst it didn't need to. I'd treat "does this deployment change what gets cached, or how" as an explicit question during code review or release planning, and only bump the version when the answer is genuinely yes. This connects directly to the REST API Design file's backward-compatibility discussion — "does this change break existing readers of this data" is fundamentally the same question, just applied to a cache entry's shape instead of an API response's.

**Source:** [AWS — Caching Best Practices](https://aws.amazon.com/caching/best-practices/)

---

## 26. How Would Blue and Green Versions Share a Cache Safely?

**Answer:**

"Building on question 25's versioned-key mechanism, blue/green deployment adds a wrinkle: unlike a typical rolling deployment, where the old version scales down as the new version scales up over a short window, blue/green often runs both environments fully in parallel for a longer, more deliberate cutover — verification, gradual traffic shifting, an easy instant rollback. So the 'old and new coexisting' window that motivates cache-key versioning can last considerably longer for blue/green than for a fast rolling deploy.

The same versioned-key mechanism from question 25 is still the right foundation, but blue/green's explicit cutover model raises an additional question: should blue and green share the same underlying Redis instance at all, or use separate cache infrastructure per environment? Sharing one instance, with versioned keys keeping the environments' entries apart, is operationally simpler and avoids paying for duplicate infrastructure — but it means a genuinely severe problem in one environment, like a runaway key-generation bug or a memory-exhaustion event, could in principle degrade the shared instance enough to affect the other, otherwise-healthy environment too. Fully separate infrastructure per environment removes that cross-environment blast radius entirely, at the cost of running and keeping warm duplicate caching infrastructure during the cutover."

**Code:**

```java
// Versioned keys, applied to the blue/green case specifically — both
// environments can safely share ONE Redis instance without collision
String buildCacheKey(String productId, String deploymentColor) {
    return "product:" + deploymentColor + ":v" + CACHE_SCHEMA_VERSION + ":" + productId;
    // blue:  "product:blue:v2:12345"
    // green: "product:green:v3:12345"  <- even a DIFFERENT schema version,
    // for whatever green is about to introduce, coexists safely alongside blue
}
```

**Follow-up:**

This decision should be driven by the actual blast-radius tolerance for the specific deployment. For a routine, low-risk blue/green cutover, a shared instance with versioned keys is usually a reasonable, cost-efficient default. For a genuinely high-stakes migration — a major schema change, or a change to something with a history of cache-related incidents — I'd lean toward the extra cost of fully separate infrastructure, specifically to guarantee that a problem discovered in green during the cutover can't degrade blue's cache performance while it's still serving production traffic, preserving a genuinely clean rollback path.

**Source:** [Martin Fowler — BlueGreenDeployment](https://martinfowler.com/bliki/BlueGreenDeployment.html)

---

## 27. How Do You Prevent Stale Cached Authorization Decisions?

**Answer:**

"Caching authorization decisions — a user's roles or permissions, a computed 'can this user access this resource' result — is a tempting performance optimization, since authorization checks can be expensive and happen on nearly every request. But it introduces a staleness risk that's more severe than typical data staleness: if a user's access gets revoked — a role removed, an account suspended, a permission denied after a detected security issue — but a cached 'authorized' decision for them is still being served, the revocation has no actual effect until the cache entry expires. A user who should be locked out immediately can keep performing authorized actions for however long the cache TTL allows. That's a genuinely dangerous gap for a security control, in a way that a stale product price or a stale view count just isn't.

My approach: use a much shorter TTL for authorization-decision caching than you'd use for general data — seconds, not minutes — since the cost of over-caching here is a security exposure window, not a minor staleness inconvenience. For genuinely security-critical revocation events — an account suspension, a detected compromise — I'd trigger explicit, immediate invalidation of that user's cached authorization entries as part of the revocation action itself, rather than relying purely on a short TTL to eventually catch up. The short TTL is a backstop for whatever the explicit invalidation might miss, not the primary mechanism for something this sensitive."

**Code:**

```java
// Short TTL specifically because staleness here IS a security exposure,
// not just a minor UX inconvenience — much shorter than typical data caching
cache.set("authz:" + userId, permissions, Duration.ofSeconds(15));

// EXPLICIT invalidation as part of the revocation action itself — don't
// rely purely on the short TTL to eventually catch up
@Transactional
void suspendUserAccount(String userId) {
    userRepository.suspend(userId);
    cache.delete("authz:" + userId); // IMMEDIATE — the revocation takes effect
}                                       // on the VERY NEXT request, not up to
                                          // 15 seconds later
```

**Follow-up:**

This exact risk — a cached authorization decision not reflecting a recent revocation — is directly analogous to the JWT-revocation-difficulty discussion in the Spring Security file: a self-contained, cached credential or decision that's hard to invalidate early once it's issued. The same trade-off applies: shorter cache lifetime means a smaller exposure window, but more frequent authorization checks cost more performance. I'd treat authorization-decision caching as needing its own, security-conscious review, distinct from the general TTL discipline in question 10, precisely because getting the staleness window wrong here means a genuine security incident — a suspended user retaining access — not just a minor data-freshness annoyance. That distinction should push toward meaningfully more conservative choices: shorter TTLs, mandatory explicit invalidation on revocation events.

**Source:** [OWASP — Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)

---

## 28. How Should an Application Behave When Redis Is Unavailable?

**Answer:**

"This is fundamentally the same question as any dependency-availability question from the REST API Design and Spring Boot Internals categories — the right answer depends entirely on whether Redis is being used as a cache or a system of record (question 1), which is exactly why that distinction matters architecturally, not just conceptually.

If Redis is purely a cache — data reconstructible from the database — the application should treat an outage as degraded, not broken: fall back to reading directly from the database on every cache-layer failure, accepting higher database load and latency for the duration, but continuing to correctly serve requests. That requires explicitly wrapping cache access with fallback logic, or using a circuit breaker around the cache client, rather than letting a Redis exception propagate up and fail the whole request. I've seen real incidents caused by exactly this mistake — a 'just a cache' dependency going down and taking the whole application with it, because the calling code had no fallback path and just let the exception become a request failure.

If Redis is being used as a system of record for some specific data — question 1's narrower, deliberate use case — an outage genuinely means that functionality is unavailable. A rate limiter backed only by Redis, with no fallback, either has to fail open (allow all requests, accepting a temporary loss of rate-limiting protection) or fail closed (reject all requests, prioritizing safety over availability), and which is correct depends entirely on which failure mode is less bad for that specific feature."

**Code:**

```java
// Cache role — GRACEFUL DEGRADATION on Redis failure, never let it break the request
Product getProduct(String id) {
    try {
        Product cached = cache.get(id);
        if (cached != null) return cached;
    } catch (RedisConnectionFailureException e) {
        log.warn("Redis unavailable, falling back to direct database read", e);
        // FALL THROUGH to the database read below — degraded, not broken
    }
    return productRepository.findById(id).orElseThrow(); // database is the
}                                                            // ACTUAL source of truth;
                                                                // Redis being down never
                                                                 // prevents a correct response

// Rate limiter (system-of-record-ish role) — an explicit FAIL-OPEN decision,
// deliberately chosen because "briefly allow more traffic than intended"
// is judged LESS BAD than "reject all traffic because Redis happens to be down"
boolean isAllowed(String userId) {
    try {
        return rateLimiterViaRedis.check(userId);
    } catch (RedisConnectionFailureException e) {
        log.warn("Redis unavailable, FAILING OPEN for rate limiting", e);
        return true; // deliberate choice — documented, reviewed, not accidental
    }
}
```

**Follow-up:**

The "fall back to the database on cache failure" pattern has a real danger of its own worth naming: if Redis goes down during significant traffic, and every request that would normally hit the cache instead falls through to the database at once, that sudden full-traffic shift can overwhelm the database — effectively a cache-outage version of the stampede problem from question 6, triggered by total unavailability instead of one key expiring. I'd combine the fallback with a circuit breaker or load-shedding specifically on the database-fallback path, rather than assume the database can simply absorb 100% of what the cache was handling. And I'd treat "what happens to database load if the cache disappears entirely" as a required capacity-planning question to answer explicitly — ideally via a game-day exercise actually simulating a full Redis outage under realistic load — rather than an assumption left untested until an incident reveals whether the database can actually handle it.

**Source:** [Google SRE Workbook — Handling Overload](https://sre.google/sre-book/handling-overload/), [Resilience4j — Circuit Breaker](https://resilience4j.readme.io/docs/circuitbreaker)

---

## 29. What Redis Metrics Would You Monitor?

**Answer:**

"I'd group monitoring into a few categories, each catching a different class of problem covered throughout this file.

**Memory**: `used_memory` versus `maxmemory` — approaching the limit signals imminent eviction or, with `noeviction`, write failures — and eviction rate (`evicted_keys`). A rising eviction rate on a policy meant to be a rare safety valve, not the primary memory-management mechanism, often signals the instance is undersized for its working set.

**Hit rate**: `keyspace_hits` versus `keyspace_misses`. A declining hit rate is the clearest signal of a caching-effectiveness regression — a bad TTL choice, question 7's penetration or pollution problems, or a working set that's outgrown what's practical to cache — and it directly correlates with increased load pushed back onto the database.

**Latency**: command-level latency, watching especially for occasional slow outliers rather than just averages. `SLOWLOG` surfaces individual slow commands — a large-key operation from question 14, an unexpectedly expensive Lua script — that averages alone would hide if slow commands are rare but severe.

**Replication health**: replication lag, `master_repl_offset` versus each replica's own offset. Rising lag is an early warning that question 16's staleness risk is widening beyond its normal, small window, and that question 17's failover-related data-loss risk is growing.

**Connection/client metrics**: connected client count versus `maxclients`, and blocked or rejected connections. A rising client count can signal a connection leak in an application — not properly returning connections to a pool — well before it becomes an outright connection-exhaustion outage."

**Code:**

```bash
# The single most useful command for a quick, comprehensive health snapshot
redis-cli INFO

# Specific sections worth watching closely, individually
redis-cli INFO memory       # used_memory, maxmemory, evicted_keys
redis-cli INFO stats        # keyspace_hits, keyspace_misses, expired_keys
redis-cli INFO replication  # master_repl_offset, connected_slaves, and each
                              # replica's own offset lag
redis-cli SLOWLOG GET 10    # the 10 most recent slow commands, with their
                              # actual execution time — catches the outliers
                              # averages alone would hide
```

**Follow-up:**

Hit-rate monitoring specifically needs to be segmented per key-pattern or use case, not tracked as one aggregate number across the whole instance. An aggregate hit rate can look perfectly healthy while one important cache use case has silently degraded, simply because it's averaged out by many other, unrelated, still-healthy usages sharing the same instance. I'd build per-prefix or per-feature hit-rate dashboards — tagging metrics by cache key namespace, not just one instance-wide number — so a regression in a specific use case is visible and alertable on its own, rather than hidden inside an average that still looks fine.

**Source:** [Redis Documentation — INFO command](https://redis.io/docs/latest/commands/info/), [Redis Documentation — Slow Log](https://redis.io/docs/latest/commands/slowlog/)

---

## 30. Describe a Cache Incident That Increased Rather Than Reduced Database Load

**Answer:**

"I'll walk through a representative, composite shape rather than claim one specific universal incident, since this pattern and its root causes recur across a lot of real systems in a genuinely predictable way — which is exactly what makes it worth having ready as a story. A service's cache-hit rate was healthy and stable for months. Then a routine deployment — one that happened to change the serialization format of a widely-cached DTO, without anyone realizing that had cache implications — shipped without a corresponding cache-key version bump (question 25's mitigation, skipped because nobody flagged the change as cache-relevant during review).

Every subsequently-cached read using the new format either failed deserialization against old-format entries still sitting in the cache, or, depending on the deserialization library's error tolerance, silently misinterpreted them. Either way, the effective hit rate collapsed to near-zero — every cache read was now either an outright failure that triggered a database fallback, or worse, an incorrect value that triggered additional corrective reads once the bad data was noticed downstream. The database, which had comfortably handled only cache-miss traffic for months, suddenly got close to 100% of the read volume it had been architecturally relying on the cache to absorb. Because its capacity had been sized around the assumption that the cache would keep absorbing most read traffic (question 28's exact capacity-planning gap), it had never been tested against, or provisioned for, this full-traffic-fallback scenario. It began timing out under the sudden load, cascading into broader request failures well beyond just the endpoint that used the changed DTO."

**Code:**

```text
Postmortem structure I'd actually use for this:

1. TIMELINE — deployment time, first elevated-database-load alert, time to
   correctly diagnose "this is a cache-format mismatch, not a database
   problem," time to mitigate (rolling back, or forward-fixing with a
   version bump) and fully recover

2. ROOT CAUSE — the specific serialization-format change, and the missing
   cache-key version bump that should have accompanied it (question 25)

3. CONTRIBUTING FACTORS —
   - no code-review checklist item prompting "does this change the shape
     of anything currently cached" for changes to widely-cached DTOs
   - no hit-rate monitoring granular enough (question 29's per-feature
     segmentation) to immediately, precisely pinpoint WHICH cache
     use case's hit rate had collapsed — initial diagnosis time was spent
     ruling out other causes before the actual one was identified
   - database capacity had never been explicitly load-tested against a
     "cache provides zero benefit" scenario (question 28), so nobody
     knew in advance whether it could survive full fallback traffic —
     it turned out it couldn't, at least not without degrading

4. WHAT WENT WELL — the graceful-degradation fallback logic (question 28)
   DID correctly kick in and serve correct data throughout, once the
   deserialization failures were happening — the INCIDENT was a load/
   capacity problem, not a correctness/data-integrity problem, specifically
   BECAUSE that fallback discipline was already in place

5. ACTION ITEMS:
   - immediate: forward-fix via an emergency cache-key version bump,
     restoring cache effectiveness immediately
   - systemic: add "does this change anything currently cached" as an
     explicit code-review prompt for changes touching widely-cached types
   - systemic: segment hit-rate monitoring per cache-use-case (question 29)
   - systemic: run an actual load test / game-day exercise simulating full
     cache unavailability, to know AHEAD OF TIME whether the database can
     survive it, rather than discovering the answer during a real incident
```

**Follow-up:**

The generalizable insight here: a cache that's been present and effective for a long time creates an easy-to-miss implicit dependency. A database's actual, tested capacity can quietly become "capacity assuming the cache is working," rather than "capacity for the application's real, full traffic," and that assumption only gets tested for real the moment the cache stops being effective — whether from an outage (question 28) or, as here, a subtler effectiveness collapse from a mismatched deployment. The durable fix is making that implicit assumption explicit and periodically verified: treat "can our database actually survive the cache disappearing or becoming ineffective" as a standing question answered through deliberate testing, not something only validated involuntarily during a real incident — which is a much more expensive and disruptive way to find out the answer was no.

**Source:** [Google SRE Book — Postmortem Culture](https://sre.google/sre-book/postmortem-culture/), [AWS — Caching Best Practices](https://aws.amazon.com/caching/best-practices/)

---

## Sources & Further Reading — Consolidated

| Topic | Link |
|---|---|
| Redis Documentation — Persistence | https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/ |
| AWS — Caching Best Practices | https://aws.amazon.com/caching/best-practices/ |
| Redis Documentation — Client-Side Caching Patterns | https://redis.io/docs/latest/develop/reference/client-side-caching/ |
| Facebook — Scaling Memcache at Facebook | https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf |
| Debezium documentation | https://debezium.io/documentation/reference/stable/index.html |
| Redis Documentation — Bloom Filter (RedisBloom) | https://redis.io/docs/latest/develop/data-types/probabilistic/bloom-filter/ |
| Caffeine — Window TinyLFU | https://github.com/ben-manes/caffeine/wiki/Efficiency |
| Redis Documentation — Eviction Policies | https://redis.io/docs/latest/develop/reference/eviction/ |
| Redis Documentation — Cluster Specification | https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/ |
| Redis Documentation — Optimization / bigkeys / hotkeys | https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/ |
| Redis Documentation — Replication | https://redis.io/docs/latest/operate/oss_and_stack/management/replication/ |
| Redis Documentation — Sentinel | https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/ |
| Redis Documentation — Cluster Tutorial | https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/ |
| Redis Documentation — WAIT command | https://redis.io/docs/latest/commands/wait/ |
| Martin Kleppmann — How to do distributed locking | https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html |
| Redis Documentation — Distributed Locks with Redis | https://redis.io/docs/latest/develop/use/patterns/distributed-locks/ |
| Cloudflare — Counting Things: Rate Limiting | https://blog.cloudflare.com/counting-things-a-lot-of-different-things/ |
| Redis Documentation — Rate Limiting Patterns | https://redis.io/docs/latest/develop/use-cases/rate-limiter/ |
| Redis Documentation — Scripting with Lua | https://redis.io/docs/latest/develop/interact/programmability/eval-intro/ |
| Redis Documentation — Transactions | https://redis.io/docs/latest/develop/interact/transactions/ |
| Redis Documentation — Pipelining | https://redis.io/docs/latest/develop/use/pipelining/ |
| Martin Fowler — BlueGreenDeployment | https://martinfowler.com/bliki/BlueGreenDeployment.html |
| OWASP — Session Management Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html |
| Google SRE Workbook — Handling Overload | https://sre.google/sre-book/handling-overload/ |
| Resilience4j — Circuit Breaker | https://resilience4j.readme.io/docs/circuitbreaker |
| Redis Documentation — INFO command | https://redis.io/docs/latest/commands/info/ |
| Redis Documentation — Slow Log | https://redis.io/docs/latest/commands/slowlog/ |
| Google SRE Book — Postmortem Culture | https://sre.google/sre-book/postmortem-culture/ |
