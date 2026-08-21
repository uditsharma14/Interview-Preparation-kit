# Redis & Caching — Interview Prep (Lead/Staff Level, with Code & Sources)

How to use this: each question has **the answer the way I'd actually say it out loud** in an interview, a **code snippet** you could sketch on a whiteboard or IDE to back it up, and **where the follow-up goes if you're in a Staff-level loop** — because at this level the bar is explaining what breaks under real production traffic (stampedes, hot keys, failover), not reciting Redis command syntax.

---

## 1. When Should Redis Be Used as a Cache Versus a System of Record?

**Answer:**

"As a **cache**, Redis holds data that's derivable/reconstructible from an authoritative source of truth (typically a relational database) — if the cached data is lost entirely (a Redis restart, a cluster failure, an eviction), the application can always fall back to the source of truth and rebuild it; correctness never depends on Redis retaining anything. This is Redis's overwhelmingly most common role, and it's what its default configuration and operational model are optimized for.

As a **system of record**, Redis itself becomes the sole, authoritative store for some piece of data — nothing else can reconstruct it if it's lost. This is a fundamentally different reliability bar: it requires deliberately configuring persistence (RDB snapshots and/or AOF, question relevant to durability), replication with appropriate `WAIT`/acknowledgment semantics, and accepting that Redis's consistency and durability guarantees, even when carefully configured, are generally weaker than a mature relational database's ACID guarantees — Redis was designed and optimized primarily as a fast, in-memory data structure server, and its persistence/durability story, while genuinely usable for some system-of-record use cases (rate-limiter counters, session data, leaderboards, ephemeral queues), is not a drop-in replacement for a relational database's transactional guarantees for data where correctness is paramount (financial ledgers, order records). I'd draw this line explicitly in any design review: for anything where losing or corrupting the data would be a genuine business incident and there's no other system that has a copy of the truth, I'd want a much stronger case made before treating Redis as that system's authoritative store rather than its cache."

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

**Where staff-level interviews push further:**

I'd bring up that the actual decision often isn't binary — a system can legitimately use Redis as a system of record for specific, deliberately-scoped, low-consequence-of-loss data (rate limiters, ephemeral session tokens, real-time leaderboards where a rare reset is tolerable) while using it purely as a cache for everything else, and the key discipline is being explicit and deliberate about *which* category each specific Redis-backed feature falls into, documented clearly, rather than letting a feature drift into "we're relying on Redis never losing this" territory informally, without anyone having consciously decided to accept that risk. I'd also mention Redis's own persistence options (RDB, AOF, or both) genuinely can make it durable enough for many system-of-record use cases — but even with full AOF persistence (`appendfsync always`), the durability/performance trade-off and operational complexity involved are real costs that should be a deliberate choice, made with full awareness of what's being traded away, not a default.

**Source:** [Redis Documentation — Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)

---

## 2. Explain Cache-Aside, Read-Through, Write-Through, and Write-Behind Strategies

**Answer:**

"**Cache-aside** (lazy loading) puts the application in explicit control: on a read, check the cache first; on a miss, read from the database, then populate the cache for next time; on a write, write to the database and either update or invalidate the corresponding cache entry. This is the most common pattern in practice, specifically because it's simple, and the cache only ever holds data that's actually been requested (no wasted population of never-read data).

**Read-through** moves the 'check cache, fall back to database, populate cache' logic *into the caching layer itself* (via a configured loader function) rather than the application explicitly orchestrating it — functionally similar to cache-aside from the application's perspective (a single `get()` call handles the whole fallback transparently), but the responsibility for the fallback logic lives in the cache abstraction, not scattered across call sites.

**Write-through** writes go to the cache first, and the cache itself synchronously writes through to the underlying database as part of the same operation — the cache and database are always kept in sync as a single logical write, at the cost of every write now paying the latency of both the cache write and the database write together.

**Write-behind** (write-back) writes go to the cache immediately and return to the caller right away, with the actual database write happening **asynchronously**, batched, sometime after — dramatically reducing write latency (the caller never waits on the database), at real cost: a window exists where the cache has data the database doesn't yet have, and a cache failure during that window means genuine, permanent data loss, since the write never made it to the durable source of truth at all."

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

**Where staff-level interviews push further:**

I'd give the practical decision framework: cache-aside is the right default for the overwhelming majority of read-heavy workloads, since it's simple, resilient (a cache outage just means slower reads via database fallback, not incorrect behavior), and doesn't risk data loss on writes. Write-through is worth it specifically when read-after-write consistency matters and the added write latency is acceptable. Write-behind is a genuinely risky pattern I'd reserve for data where the consequence of losing a brief window of writes is truly acceptable (analytics counters, non-critical activity logs) — I'd be very cautious about applying write-behind to anything with real business consequences, given how easy it is for that data-loss window to be forgotten about until an actual cache failure incident makes it painfully concrete.

**Source:** [AWS — Caching Strategies](https://aws.amazon.com/caching/best-practices/), [Redis Documentation — Client-Side Caching Patterns](https://redis.io/docs/latest/develop/reference/client-side-caching/)

---

## 3. How Do You Maintain Consistency Between a Database and a Cache?

**Answer:**

"Perfect, always-consistent synchronization between a database and a cache is not actually achievable without paying a cost that usually defeats the point of caching in the first place (e.g., a genuinely synchronous, transactional write to both, which reintroduces exactly the distributed-transaction problems from the Transactions category, just between a database and a cache instead of a database and Kafka). So the realistic goal is **bounded, well-understood staleness** — the cache might briefly diverge from the database after a write, but that divergence window is kept short, predictable, and appropriate for the specific data's actual staleness tolerance, rather than pretending the cache is a real-time mirror of the database.

The standard mechanism, cache-aside with invalidation-on-write (question 2), gets you most of the way there for typical workloads: writes invalidate (or update) the relevant cache entry as part of the write path, and any reader that hits a cache miss immediately after invalidation reads fresh data from the database and repopulates the cache correctly. The genuinely hard part — covered directly in the next question — is the specific ordering of 'update database' versus 'invalidate cache' and the race conditions that ordering choice creates, which is where most real consistency bugs in cache-aside implementations actually live."

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

**Where staff-level interviews push further:**

I'd emphasize that "maintain consistency" for a cache should always be scoped with an explicit staleness tolerance stated up front for the specific data in question — a product catalog description can tolerate several minutes of staleness with zero business impact, while a user's current account balance genuinely cannot, and treating both with the same caching/invalidation strategy is a common design mistake. I'd frame the actual staff-level skill here as: for each cached data type, explicitly stating "what's the maximum acceptable staleness window, and what's the actual mechanism that bounds staleness to within that window" — TTL alone (question 10), invalidation-on-write, or a combination — rather than treating "add caching" as a single, uniform decision applied identically everywhere in a system.

**Source:** [Redis Documentation — Cache Invalidation Strategies](https://redis.io/docs/latest/develop/reference/client-side-caching/)

---

## 4. What Can Go Wrong With "Update Database, Then Delete Cache"?

**Answer:**

"This is the generally-recommended ordering (update the database, *then* delete the corresponding cache entry — deliberately delete rather than update the cache directly, since recomputing and writing the correct new cached value can itself be stale/wrong if another concurrent write is happening, whereas deletion just forces the next reader to recompute fresh from the database), but it still has a real, if narrower, race condition window worth knowing precisely.

The classic failure sequence: Thread A reads the cache, gets a miss, and is about to read from the database and repopulate the cache with what it finds. **Before Thread A's repopulation write actually lands**, Thread B updates the database with a *newer* value and deletes the cache entry (which was already empty/missing, so the delete is a no-op). Thread A then completes its stale read (of the *pre-update* database value, since it read the database *before* Thread B's update landed) and writes that **stale** value into the cache — where it now sits, incorrectly, until its TTL eventually expires or another write happens to trigger invalidation again. This is a genuine, if relatively narrow-window, race, and it's worth naming explicitly rather than assuming 'update DB, delete cache' is a fully bulletproof pattern."

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

**Where staff-level interviews push further:**

I'd bring up that this specific race is exactly why a **TTL should always be set on cached entries, even ones that are also explicitly invalidated on write** — the TTL acts as a self-healing backstop, bounding how long a rare race-condition-induced stale entry can persist, even though the invalidation-on-write mechanism handles the overwhelming majority of updates correctly and immediately. I'd also mention that for genuinely high-consistency-sensitivity data, a **delayed double-delete** pattern (delete the cache entry, wait a short interval — long enough for any in-flight stale repopulation like Thread A's to have completed — then delete it again) is a known mitigation that narrows this race further, though it adds real complexity and I'd only reach for it when the staleness window from a plain TTL-backstop approach genuinely isn't acceptable for the specific data involved, given how rare this exact race actually is for most typical workloads.

**Source:** [Facebook — Scaling Memcache at Facebook (the delete-on-write pattern's origin)](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf)

---

## 5. How Would You Handle Failure Between the Database Update and Cache Invalidation?

**Answer:**

"This is a genuine 'two things need to happen, but can't be made atomic across two different systems' problem — the exact same structural issue the Transactions category's outbox pattern addresses for a database-and-Kafka pair, just here between a database and a cache. If the process crashes (or the cache is briefly unreachable) after the database commit but before the invalidation call succeeds, the cache is left holding a **stale** entry indefinitely — worse than question 4's narrow race, since there's no TTL-backstop-triggering event coming; the entry will happily serve stale data until its TTL naturally expires (if one was set at all) or something else happens to invalidate it.

The mitigations, in order of how much additional infrastructure they require: **always set a TTL**, even on entries that are also invalidation-driven, so any missed invalidation is self-healing within a bounded window rather than persisting indefinitely — this is the cheap, always-worth-doing baseline. For genuinely stronger guarantees, a **CDC-based invalidation pipeline** (using the same Debezium-style change-data-capture mechanism from the Transactions category's outbox discussion, but here reading the database's write-ahead log and invalidating the cache as a downstream reaction to the committed change itself, rather than relying on application code to remember to call invalidate) decouples 'the database change definitely happened' from 'did the application code path that was supposed to invalidate the cache actually run and succeed' — closing the exact gap a crashed/failed invalidation call leaves open."

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

**Where staff-level interviews push further:**

I'd bring up that CDC-based invalidation is genuinely the more robust answer, structurally closing the exact same class of gap the transactional outbox pattern closes for database-to-Kafka publication — the database's own committed write-ahead log becomes the single source of truth for "did this change actually happen," and the invalidation reacts to that authoritative signal rather than depending on the original request's application code successfully executing a follow-up call. I'd also be honest about the trade-off: this requires real infrastructure investment (a CDC pipeline, its own operational monitoring) that's only worth it once the TTL-backstop's staleness window is genuinely unacceptable for the specific data — for most caching use cases, "always set a TTL as a self-healing backstop" is a perfectly sufficient, much cheaper mitigation, and I'd reserve the CDC approach for data where even a brief, TTL-bounded staleness window is a real business problem.

**Source:** [Debezium documentation](https://debezium.io/documentation/reference/stable/index.html), [Facebook — Scaling Memcache at Facebook](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf)

---

## 6. What Is a Cache Stampede, and How Do You Prevent It?

**Answer:**

"A cache stampede (also called a 'thundering herd' against the cache) happens when a **popular** cache entry expires (or is invalidated) and a large number of concurrent requests for that same key all miss the cache simultaneously, and **all of them** independently proceed to hit the database (or recompute an expensive value) at the exact same moment to repopulate it — turning what should be one cache-miss-triggered database query into potentially hundreds or thousands of simultaneous, identical, redundant queries hitting the database all at once, which can genuinely overload it, sometimes badly enough to cause a cascading outage from what was originally just one cache entry expiring.

The standard prevention mechanisms: **request coalescing/single-flight** — the first request that misses acquires a lock (or otherwise signals 'I'm already fetching this'), and every other concurrent request for the *same* key waits for that first request's result rather than independently querying the database itself, then all of them share the one fetched result. **Probabilistic early expiration** — instead of a hard expiration at exactly TTL, each read has a small, increasing probability of proactively refreshing the cache entry *before* it actually expires, as the entry approaches its TTL — spreading refresh load out over time rather than concentrating it all at the exact expiration instant. **Stale-while-revalidate** — serve the (slightly) stale cached value immediately to any request that arrives right as an entry expires, while asynchronously kicking off exactly one background refresh, rather than making every concurrent requester block waiting on a fresh fetch at all."

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

**Where staff-level interviews push further:**

I'd bring up that stampedes are specifically dangerous for **hot** keys — a rarely-accessed key expiring and triggering a handful of redundant queries is a non-event, but a genuinely popular key (a homepage's featured-products list, a widely-referenced configuration value) expiring under high concurrent traffic is exactly the scenario that turns a routine cache-refresh into a database-overload incident. I'd advocate for identifying the specific hot keys in a system proactively (via cache-hit-rate/access-frequency monitoring, question 12/13's hot-key detection) and applying stampede protection deliberately to those specific keys, rather than assuming every cached entry needs the same, potentially over-engineered protection — for most low-traffic cache entries, an occasional handful of redundant concurrent database queries on expiration is genuinely fine and not worth the added complexity of coalescing/locking logic.

**Source:** [Vikram Rangnekar — Cache Stampede](https://en.wikipedia.org/wiki/Cache_stampede), [XFetch / Probabilistic Early Expiration (Vattani, Chierichetti, Lowenstein)](https://cseweb.ucsd.edu/~avattani/papers/cache_stampede.pdf)

---

## 7. What Are Cache Penetration and Cache Pollution?

**Answer:**

"**Cache penetration** happens when requests repeatedly ask for keys that **don't exist in the database at all** — since there's no valid value to cache (a cache-aside pattern typically only caches values that were successfully found), every one of these requests misses the cache and hits the database, every single time, with no possible cache benefit ever accruing for them. This becomes a genuine attack vector or accidental-load problem: a malicious actor (or a buggy client) probing many non-existent IDs can force sustained, uncached database load that a normal caching layer does nothing to absorb, since the cache is structurally incapable of ever having a hit for a key with no corresponding real data.

**Cache pollution** is a different problem: the cache fills up with entries that are rarely, if ever, accessed again — either because of an unusual, one-off traffic pattern (a scraper or crawler touching a huge number of distinct, individually-rare keys once each), or a poorly-chosen caching policy that caches things too broadly/eagerly — and this crowds out genuinely hot, frequently-accessed entries under the cache's eviction policy (question 11), degrading the cache's overall hit rate for the traffic that actually matters, even though the cache itself isn't 'failing' in any obvious way — it's just full of the wrong things."

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

**Where staff-level interviews push further:**

I'd bring up **Bloom filters** as the more sophisticated, memory-efficient defense against cache penetration specifically for very high-cardinality ID spaces where caching every individual negative result would itself consume significant memory — a Bloom filter can answer "does this ID definitely NOT exist" with zero false negatives (though a small, tunable false-positive rate) using a tiny memory footprint compared to caching every individual miss, letting the application skip the database entirely for IDs the filter confirms don't exist, without needing a per-ID cache entry for every possible non-existent value. For cache pollution, I'd mention that this is exactly the kind of problem an eviction-policy choice (question 11) needs to account for explicitly — a plain LRU policy is vulnerable to exactly this scrape-and-pollute pattern (a single pass through many rarely-reused keys can evict an entire working set of genuinely hot data), which is part of why more sophisticated policies like LFU or the TinyLFU-based admission policies (used by Caffeine, referenced in the JPA/Hibernate file's second-level-cache discussion) exist specifically to resist this failure mode better than naive recency-based eviction alone.

**Source:** [Redis Documentation — Bloom Filter (RedisBloom)](https://redis.io/docs/latest/develop/data-types/probabilistic/bloom-filter/), [Caffeine — Window TinyLFU](https://github.com/ben-manes/caffeine/wiki/Efficiency)

---

## 8. Why Should Cache TTLs Include Jitter?

**Answer:**

"If a large number of cache entries are all set with the **exact same TTL**, and they were all populated at roughly the same time (a common pattern: a deployment or a cold-cache event that populates many entries simultaneously, or a batch job that refreshes a large set of keys all at once), they will all **expire at roughly the same instant**, which recreates exactly the cache-stampede problem from question 6, except now across potentially many different keys simultaneously rather than one hot key — a synchronized, mass expiration event that hits the database with a burst of simultaneous cache-miss-triggered queries all at once, rather than a smooth, spread-out trickle of individual expirations over time.

Adding **jitter** — a small, randomized adjustment to each entry's actual TTL (e.g., a base TTL of 10 minutes, plus or minus a random 0-2 minutes, computed independently per entry) — spreads out the expiration times of what would otherwise be a synchronized batch, converting a single sharp spike in cache-miss/database load into a smoother, more manageable trickle spread across the jitter window, without meaningfully changing the *average* staleness any individual entry experiences."

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

**Where staff-level interviews push further:**

I'd bring up that this exact synchronized-expiration failure mode is a genuinely common, easy-to-overlook root cause of a specific incident pattern worth naming explicitly: "the database load spikes every N minutes, in a suspiciously regular, clock-aligned pattern" — a strong signal pointing directly at synchronized TTL expiration somewhere upstream, and adding jitter is usually a fast, low-risk, high-value fix once that pattern is correctly diagnosed. I'd also mention that jitter should be applied at TTL-*setting* time (per-entry, as shown above), not as some kind of randomized delay in the read path — the goal is desynchronizing *when entries actually expire*, not adding artificial latency to reads, and conflating the two is a common implementation mistake when someone reaches for "add some randomness" without being precise about exactly where in the flow the randomness needs to live.

**Source:** [AWS — Caching Best Practices, TTL jitter](https://aws.amazon.com/caching/best-practices/)

---

## 9. How Would You Cache Negative Results Safely?

**Answer:**

"Caching a 'not found' result (question 7's penetration-mitigation technique) is genuinely valuable — without it, repeated lookups for a non-existent key hit the database every single time, forever — but it needs to be done carefully, since a negative result is fundamentally different from a positive one in a few important ways.

First, the negative-result marker needs to be **unambiguous** — distinguishable from any legitimate cached value, including a legitimately empty/null-ish real value if the data model allows one — a sentinel value or a distinct wrapper/envelope (rather than, say, caching a plain `null` and hoping the cache client's `null`-handling semantics happen to distinguish 'not found' from 'not yet cached at all,' which is a real, easy-to-get-wrong ambiguity). Second, negative results should generally use a **shorter TTL** than positive results — the data might genuinely not exist yet at read time but be created moments later (a new resource being created concurrently with an earlier lookup for it), and a long negative-cache TTL would incorrectly mask that new data's existence for an unnecessarily long window; a short negative TTL bounds how long a 'not found' answer can remain wrong after the underlying data actually starts existing."

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

**Where staff-level interviews push further:**

I'd bring up that negative-result caching interacts directly with the cache-invalidation discipline from questions 3-5 — if a resource with a previously-cached "not found" entry is subsequently created, the creation code path needs to explicitly invalidate that specific negative cache entry (not just rely on the short TTL eventually expiring it), or legitimate newly-created data can appear to not exist for up to the negative TTL's full duration after creation, which is a genuinely confusing, easy-to-miss bug if the "invalidate on write" logic was only ever designed with updates to *existing* records in mind, not the create-after-a-cached-miss case. I'd also mention that for a resource type where "not found" lookups are expected to be rare/low-volume in normal operation, negative caching might not be worth the added complexity at all — it's specifically valuable when penetration-style repeated-miss traffic (question 7) is a genuine, measured problem, not a default to apply everywhere regardless of actual access patterns.

**Source:** [AWS — Caching Best Practices](https://aws.amazon.com/caching/best-practices/)

---

## 10. How Do You Select a TTL?

**Answer:**

"TTL selection is fundamentally a trade-off between **staleness tolerance** (how quickly does this specific data change, and how much does it actually matter if a reader sees a slightly outdated value) and **cache effectiveness** (a longer TTL means a higher hit rate and less database load, but also a longer window of potential staleness) — there's no universal 'correct' TTL; it has to be derived from the specific data's actual characteristics, not chosen by convention or copy-pasted from an unrelated use case.

My practical approach: start from the data's **actual update frequency and business staleness tolerance** — a product's list price, which might change a few times a month and where a few minutes of staleness has zero real business impact, can reasonably have a TTL of many minutes to hours; a real-time inventory count during a flash sale, where staleness directly causes overselling, needs a TTL of seconds at most, or arguably shouldn't rely on TTL-based staleness tolerance at all and should instead use invalidation-on-write as the primary consistency mechanism (question 3), with TTL purely as a self-healing backstop (question 4/5), not the primary freshness mechanism. I'd also factor in **cost of a cache miss** — data that's very expensive to recompute/refetch (a complex aggregation query, an expensive external API call) deserves a longer TTL bias even for moderately staleness-sensitive data, since the cost asymmetry (occasional staleness vs. frequent expensive recomputation) often favors erring toward longer TTLs there specifically."

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

**Where staff-level interviews push further:**

I'd bring up that TTL selection shouldn't be a one-time, set-and-forget decision made at implementation time — it's worth periodically revisiting based on actual observed cache-hit-rate and staleness-complaint data (if users/downstream systems are reporting staleness issues for a specific cached value, the TTL might genuinely be too long for that data's real sensitivity; if hit rates are unexpectedly low for a value that should be stable, the TTL might be shorter than necessary, needlessly generating database load) — treating TTL as a tuned, monitored parameter rather than a static, permanent configuration choice. I'd also mention that for data with genuinely variable staleness tolerance depending on *context* (the same product data might tolerate more staleness on a low-traffic browse page than on a checkout-confirmation page double-checking current price/availability), it's legitimate to use different TTLs — or bypass the cache entirely — for the same underlying data depending on which specific code path/use case is reading it, rather than assuming one TTL must serve every consumer of that data uniformly.

**Source:** [AWS — Caching Best Practices](https://aws.amazon.com/caching/best-practices/)

---

## 11. Compare Redis Eviction Policies

**Answer:**

"Once Redis reaches its configured `maxmemory` limit, its eviction policy determines what happens next — either reject new writes outright, or evict existing keys to make room, and if evicting, *which* keys to choose.

`noeviction` — the default — simply returns an error on any write once memory is full; reads still work normally. This is the right choice specifically for a system-of-record use case (question 1) where losing data via silent eviction would be a correctness bug, not just a performance degradation — you'd rather get a loud write failure than silently lose data.

`allkeys-lru` — evicts the least-recently-used key across the entire keyspace, regardless of whether it has a TTL set at all. This is the most common choice for a pure-cache use case, since it approximates 'keep what's actually being used, discard what isn't' reasonably well with low overhead.

`volatile-lru` — same LRU logic, but restricted to only keys that have a TTL set (keys with no expiration are never considered for eviction) — useful when a Redis instance mixes cache-role keys (which have TTLs) with system-of-record-role keys (which deliberately have none) in the same instance, letting eviction pressure fall only on the cache-role subset.

`allkeys-lfu`/`volatile-lfu` — evicts based on **frequency** of access rather than recency — a key accessed constantly but not in the last few seconds is preserved over a key accessed once, very recently; this resists the pollution pattern from question 7 (a single scan through many rarely-reused keys) better than pure LRU, since LFU specifically weights actual access frequency over mere recency.

`volatile-ttl` — evicts the key with the **nearest expiration** first among keys that have a TTL — a narrower, less commonly used policy for specific cases where 'evict what was going to expire soonest anyway' is a more meaningful signal than access recency/frequency."

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

**Where staff-level interviews push further:**

I'd bring up that mixing system-of-record and pure-cache keys in the **same** Redis instance/database is itself a design smell worth avoiding when practical — it forces a compromise eviction policy (like `volatile-lru`) that has to carefully distinguish the two roles by TTL presence alone, which is fragile if any code path accidentally sets (or forgets to set) a TTL on the wrong kind of key. I'd generally recommend separating these into different logical databases (Redis's numbered DBs, though those share the same eviction/memory pool) or, better, entirely separate Redis instances/clusters, so each can have an eviction policy and `maxmemory` sizing genuinely matched to its actual role, without depending on a subtle TTL-presence convention to keep the two use cases from interfering with each other under memory pressure.

**Source:** [Redis Documentation — Eviction Policies](https://redis.io/docs/latest/develop/reference/eviction/)

---

## 12. How Do Hot Keys Affect Redis?

**Answer:**

"Redis's core execution model is fundamentally **single-threaded** for command execution (even in cluster mode, each individual key is served by exactly one node, and that node processes commands for that key one at a time) — this means a single, extremely popular key ('hot key') that receives a disproportionate share of a workload's total traffic can become a genuine bottleneck **regardless of how much total capacity the broader cluster has**, since scaling out a Redis Cluster by adding more nodes/shards does nothing to help a single key's traffic if that key's requests all land on the same one node/shard.

This is a fundamentally different scaling problem than general capacity — a cluster with plenty of aggregate throughput headroom can still see one hot key's node pegged at high CPU/network utilization, causing elevated latency for *every* key that happens to be co-located on that same node (not just the hot key itself), while every other node in the cluster sits comfortably underutilized. This is exactly the kind of problem that shows up as 'our Redis cluster has plenty of spare capacity overall, but we're still seeing latency spikes' — a symptom that looks like a capacity/sizing problem but is actually a data-distribution/access-pattern problem no amount of horizontal scaling fixes on its own."

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

**Where staff-level interviews push further:**

I'd bring up that this is precisely why Redis Cluster's horizontal scaling model, while excellent for distributing *aggregate* load across many distinct keys, provides zero relief for a genuinely hot individual key — the fix has to happen at the *data-access-pattern* level (question 13's mitigation techniques), not the infrastructure level, and recognizing "this is a hot-key problem, not a capacity problem" early is the actual diagnostic skill that matters here; throwing more nodes at a hot-key-caused latency spike is a wasted, ineffective response that a staff engineer should be able to identify and redirect quickly. I'd also mention that this exact single-key-single-node constraint is a specific instance of a much more general distributed-systems principle — sharding/partitioning schemes distribute aggregate load well, but any single logical unit of data (a key, a database row, a Kafka partition) still fundamentally has a ceiling determined by whatever single node ultimately serves it, which is worth recognizing as a recurring pattern across many different systems, not something unique to Redis specifically.

**Source:** [Redis Documentation — Cluster Specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)

---

## 13. How Would You Detect and Mitigate Hot Keys?

**Answer:**

"**Detection**: Redis has a built-in `--hotkeys` mode for `redis-cli` (using an approximate LFU-based sampling mechanism already present internally for the `allkeys-lfu` eviction policy) that surfaces the most-frequently-accessed keys directly, without needing external tooling — a genuinely useful, low-effort first step. Beyond that, per-shard/per-node CPU and network utilization monitoring, combined with request-level tracing/logging that captures the specific key being accessed, lets you correlate 'this specific node is saturated' with 'these specific keys are responsible for the disproportionate share of its traffic.'

**Mitigation**, once a hot key is identified, has a few real options depending on the specific access pattern: **local, in-process caching** of the hot key's value **inside each application instance** (an in-memory cache with a short TTL, sitting in front of Redis) — for a value that's genuinely hot enough to be a Redis-level problem, even a very short local cache (seconds) can absorb the vast majority of read traffic before it ever reaches Redis at all, since most of that traffic is redundant reads of the same, barely-changing value. **Key splitting** — for a counter or aggregatable value specifically, split the single hot key into N sharded sub-keys (`counter:0` through `counter:N-1`, chosen by a random or round-robin distribution per write), spreading writes across multiple keys (and, in cluster mode, potentially multiple shards), then sum across all N sub-keys when a read needs the aggregate total. **Read replicas** — for a hot key that's read-heavy (not write-heavy), routing reads for that specific key across multiple Redis replicas can distribute read load, though writes still ultimately funnel through the primary."

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

**Where staff-level interviews push further:**

I'd bring up that local in-process caching, despite feeling like a slightly "cheap" or unsophisticated fix, is genuinely often the *most* effective mitigation for a read-heavy hot key specifically because it eliminates network round-trips to Redis entirely for that key, not just spreading load across more Redis capacity — for content that's read constantly and changes rarely (a featured-products list, a global configuration value), even a very short local TTL can absorb the overwhelming majority of traffic, and I'd generally reach for this before more complex options like key splitting. I'd reserve key splitting specifically for write-heavy hot keys (a genuinely high-frequency counter) where local caching doesn't help at all, since a write needs to actually reach the authoritative store to be recorded correctly, and I'd note that key splitting adds real complexity to reads (needing to fan out and sum across sub-keys), which is a cost worth weighing against the specific write-throughput problem it solves.

**Source:** [Redis Documentation — redis-cli --hotkeys](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/), [Caffeine cache library](https://github.com/ben-manes/caffeine)

---

## 14. How Do Large Keys Affect Latency and Cluster Behavior?

**Answer:**

"Because Redis's command execution is single-threaded per node, any single command that has to process a large value — a huge `List`, `Hash`, `Set`, or a single very large string — **blocks that node's entire event loop for the duration of that one operation**, meaning every *other* client's command against that same node, even for completely unrelated, small keys, has to wait behind it. A command like `LRANGE bigkey 0 -1` (fetching an entire multi-million-element list) or `SMEMBERS` on a huge set can genuinely stall a node for a noticeable, measurable duration, and every other request hitting that node during that window experiences elevated latency, purely because of one oversized key's operation.

This also affects cluster behavior specifically around **resharding/migration** — when Redis Cluster needs to move a key from one shard to another (rebalancing, or during a scale-out operation), it has to migrate that key's entire value atomically; a very large key takes proportionally longer to migrate, and during that migration window, operations against that specific key can be delayed or, in some scenarios, briefly blocked, making cluster rebalancing operations slower and riskier specifically because of the presence of oversized keys, compared to a cluster where keys are more uniformly, modestly sized."

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

**Where staff-level interviews push further:**

I'd bring up that this is exactly why unbounded collections stored as single Redis keys (an ever-growing list, set, or hash with no size cap ever enforced) are a genuine anti-pattern worth catching in design review, proactively, before they become a latency incident — `redis-cli --bigkeys` is a useful reactive diagnostic tool, but the actual fix is architectural discipline: any collection-type key that can grow unboundedly over time (per-user activity logs, accumulating event streams) needs an explicit size cap enforced at write time (via `LTRIM`, capped `ZADD` with a score-based eviction, or splitting into time-bucketed keys that naturally age out), rather than being allowed to grow indefinitely and eventually become a large-key problem that's much more disruptive to fix once already in production with a genuinely oversized value.

**Source:** [Redis Documentation — redis-cli --bigkeys](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/), [Redis Documentation — Cluster Specification, resharding](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)

---

## 15. What Is the Difference Between Redis Replication, Sentinel, and Cluster?

**Answer:**

"**Replication** is the foundational primitive — one or more replica nodes asynchronously copy a primary node's data, providing read scalability (routing reads to replicas) and a basic durability/failover foundation, but replication alone provides **no automatic failover** — if the primary fails, a human (or an external script) has to manually promote a replica to primary and reconfigure clients to point at it.

**Sentinel** adds **automatic failover** on top of plain replication — a small, separate quorum of Sentinel processes continuously monitors the primary's health, and if a quorum of Sentinels agrees the primary is genuinely down (not just unreachable from one Sentinel's perspective, which could be a network partition on that one Sentinel's side rather than a real primary failure), they automatically elect and promote a replica to be the new primary, and notify clients (via Sentinel's own pub/sub notification mechanism) of the new topology — solving the 'someone has to manually intervene' problem, but Sentinel still operates on a single logical dataset (one primary, its replicas) — it doesn't provide horizontal *data* partitioning/sharding at all.

**Cluster** provides both automatic failover (built into Cluster itself, without needing separate Sentinel processes) **and** horizontal **sharding** — data is automatically partitioned across multiple primary nodes (each owning a subset of the total 16384 hash slots), each of which can have its own replicas for failover, letting both data volume and throughput scale horizontally across many nodes, which neither plain replication nor Sentinel-managed replication alone provides."

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

**Where staff-level interviews push further:**

I'd bring up the practical decision guidance: plain replication with manual failover is rarely a good production default given how cheap Sentinel is to add — Sentinel (or a managed cloud provider's equivalent automatic-failover offering) should be the baseline for any production Redis deployment that can't tolerate a manual-intervention window during a primary failure. Cluster's added complexity (data sharding, its own client-side redirect/topology-awareness requirements, harder multi-key operations since keys can now live on different shards — see question 23's Redis-transaction-limitations discussion) is worth taking on specifically once a single node's capacity or throughput genuinely isn't sufficient — I'd avoid reaching for Cluster prematurely "for scalability" if a single well-sized primary-plus-replicas-plus-Sentinel setup is still comfortably within capacity, since Cluster's operational and application-level complexity (particularly around multi-key commands and hash-tag-based co-location) is a real cost that shouldn't be paid before it's actually needed.

**Source:** [Redis Documentation — Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/), [Redis Documentation — Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/), [Redis Documentation — Cluster Tutorial](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/)

---

## 16. What Consistency Guarantees Does Redis Replication Provide?

**Answer:**

"Redis replication is, by default, **asynchronous** — the primary applies a write, acknowledges it to the client immediately, and *then* streams the change to its replicas, with no guarantee the replica has received (let alone applied) it by the time the primary's acknowledgment reaches the client. This means Redis replication provides only **eventual consistency** by default: a read against a replica can, and routinely will, briefly return **stale** data relative to what the primary has already acknowledged as written, and there's no built-in guarantee of how large that lag window is under normal operation (though it's typically small, sub-millisecond to low-milliseconds, under healthy conditions — but can grow significantly under replica load, network issues, or a large backlog of pending replication data).

For scenarios where this staleness is unacceptable, Redis offers `WAIT` — a command that blocks until a specified number of replicas have acknowledged receiving the write (or a timeout elapses) — letting the client trade write latency for a stronger, more synchronous-like consistency guarantee on a per-write basis, though even `WAIT` doesn't make the replication protocol itself synchronous by default; it's an opt-in, explicit check layered on top of the underlying asynchronous mechanism."

**Code:**

```java
// Default — asynchronous, eventually consistent; a read against a replica
// immediately after this write MIGHT still see the OLD value
redisTemplate.opsForValue().set("key", "new-value"); // acknowledged as soon
// as the PRIMARY applies it — replicas may not have it yet at all

// Using WAIT explicitly, for writes that need a stronger guarantee before
// proceeding — trades latency for confidence that at least N replicas have it
redisTemplate.execute((RedisCallback<Long>) connection ->
    connection.execute("WAIT", "1".getBytes(), "1000".getBytes())); // wait for
    // at least 1 replica to acknowledge, up to 1000ms, before considering
    // this write "safe enough" to proceed on
```

**Where staff-level interviews push further:**

I'd bring up that this asynchronous-by-default replication has a real, sometimes-overlooked implication for failover specifically: because replication is async, a primary can acknowledge a write to a client and then **fail before that write ever reaches any replica** — if Sentinel/Cluster then promotes a replica that never received that specific write, the write is **permanently lost**, even though the client received a successful acknowledgment for it. This is a genuine, if narrow-window, data-loss risk inherent to Redis's default replication model, and it's exactly the kind of trade-off that should inform the question-1 decision about whether Redis is being used purely as a cache (where this loss window is a non-issue, since the database remains authoritative) or as a system of record (where this specific failure mode needs to be explicitly accepted, mitigated via `WAIT`-based stronger acknowledgment, or avoided by choosing a different storage system for that specific data).

**Source:** [Redis Documentation — Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/), [Redis Documentation — WAIT command](https://redis.io/docs/latest/commands/wait/)

---

## 17. What Happens During Redis Failover?

**Answer:**

"With Sentinel (or Cluster's built-in failover) managing the process: Sentinels continuously monitor the primary via periodic health checks; once a **quorum** of Sentinels independently agree the primary is genuinely unreachable/down (requiring quorum specifically to avoid a single Sentinel's own network issue — a partition isolating just that one Sentinel from the primary — from triggering an unnecessary, incorrect failover), the Sentinels elect one among themselves to actually drive the failover, select the best-positioned replica (typically the one with the most up-to-date replication offset, i.e., the least data lag from the failed primary) to promote, promote it to primary, reconfigure the remaining replicas to replicate from the new primary instead, and update Sentinel's own published configuration so clients querying Sentinel for 'who is the current primary' get the new address.

The practical consequence during this window: there's a genuine **gap** between the original primary failing and a new primary being fully promoted and ready to accept writes — during that gap, write availability is lost entirely (reads against surviving replicas may still work, depending on client configuration, but writes have nowhere to go until promotion completes) — and any writes that were acknowledged by the old primary but hadn't yet replicated to the promoted replica (question 16's async-replication data-loss risk) are permanently lost as part of this transition, not just delayed."

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

**Where staff-level interviews push further:**

I'd bring up that applications relying on Redis need to be explicitly designed to **tolerate this write-unavailability window** gracefully — a request that tries to write to Redis during a failover should fail fast with a clear error (or degrade gracefully, per question 28's broader "how should an application behave when Redis is unavailable" discussion) rather than hanging or retrying indefinitely against a Redis endpoint that's genuinely unable to accept writes for those 10-15 seconds. I'd also mention that failover timing is tunable (Sentinel's `down-after-milliseconds`, quorum size, and related settings) and represents a real trade-off: a more aggressive (faster) failure-detection configuration reduces the write-unavailability window but increases the risk of a false-positive failover triggered by a transient blip rather than a genuine failure, while a more conservative configuration is slower to fail over but more resistant to unnecessary, disruptive failovers caused by brief, self-resolving network issues.

**Source:** [Redis Documentation — Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/)

---

## 18. Why Can a Distributed Lock Be Unsafe?

**Answer:**

"A naive distributed lock built on `SET lock-key unique-value NX PX 30000` (set if not already present, with a 30-second expiry) has a genuine, non-obvious safety gap: the lock's expiry is a **time-based guess** about how long the lock holder needs, not a guarantee tied to whether that holder is actually still alive and making progress. If the process holding the lock experiences a long pause — a GC pause (tying directly back to the JVM/GC file's stop-the-world-pause discussion), a network partition that delays it, or simply legitimately taking longer than the assumed 30 seconds — the lock can **expire and be acquired by a second process** while the *first* process is still running, still believes it holds the lock, and is still actively performing the operation the lock was meant to protect exclusively. Now two processes are both operating under the belief that they exclusively hold the lock, which is exactly the safety violation a mutual-exclusion lock exists to prevent in the first place.

This isn't a Redis-specific bug or a configuration mistake to simply 'fix' with a longer TTL — it's an inherent structural property of any lock whose validity is determined purely by a timer rather than by verifiable, ongoing proof that the holder is still alive and hasn't been superseded, and it's exactly why naive distributed locking based purely on TTL expiry is a known, well-documented unsafe pattern for genuinely correctness-critical mutual exclusion."

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

**Where staff-level interviews push further:**

I'd bring up Martin Kleppmann's well-known critique of Redlock (Redis's own proposed multi-instance distributed-locking algorithm) as directly relevant background here — Kleppmann's argument is precisely this TTL-vs-actual-liveness gap, applied specifically to Redlock's claimed stronger guarantees, and the broader point his analysis makes is that **no purely timer-based distributed lock, regardless of how many Redis instances it coordinates across, can provide a true fencing/safety guarantee against an arbitrarily-paused process** — the fix has to come from either accepting the lock as a best-effort optimization (safe to use if the protected operation is itself idempotent/tolerant of rare double-execution) or from a genuinely different mechanism (fencing tokens, question 19) that provides safety even when the lock's timer-based assumption is violated. I'd frame the practical staff-level takeaway as: know explicitly what a specific distributed lock in your system is actually protecting, and whether that protected operation can tolerate an occasional, rare double-execution — if it truly cannot, a naive TTL-based Redis lock alone is not a sufficient safety mechanism, full stop.

**Source:** [Martin Kleppmann — How to do distributed locking](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html), [Redis Documentation — Distributed Locks with Redis](https://redis.io/docs/latest/develop/use/patterns/distributed-locks/)

---

## 19. Explain Token-Based Lock Ownership

**Answer:**

"The mitigation for question 18's core problem — a lock holder's TTL expiring while it's still (unknowingly) active — is a **fencing token**: instead of the lock merely being 'held or not held,' every successful lock acquisition returns a **monotonically increasing** token/number, and every operation the lock protects must present that specific token to whatever resource it's actually modifying (a database, a downstream service) — and that resource must itself **reject any operation presenting a token lower than the highest token it has already seen**.

This doesn't prevent two processes from *both* believing they hold the lock simultaneously (the underlying TTL-expiry race from question 18 can still occur) — instead, it ensures that if it does happen, only the process with the **higher** (i.e., more recent) token can actually succeed in performing the protected operation; the 'stale' holder, even if it still believes it holds the lock and attempts the operation, gets rejected by the resource itself, because its token is now lower than one already presented by the newer, legitimate holder. This shifts the actual safety guarantee from 'the lock's timer is trustworthy' (which question 18 shows it fundamentally isn't) to 'the protected resource itself enforces monotonic ordering,' which is a genuinely stronger and more defensible guarantee."

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

**Where staff-level interviews push further:**

I'd bring up that fencing tokens require the **protected resource itself** to cooperate with the scheme (it has to store and check the last-seen token, as in the SQL example above) — this is a real, meaningful implementation cost, and it's exactly why fencing tokens are the correct, robust answer specifically for genuinely correctness-critical operations, while for lower-stakes operations where an occasional rare double-execution is truly tolerable, a plain TTL-based lock (question 18's simpler, if theoretically unsafe, mechanism) combined with idempotent operation design is often a perfectly pragmatic, sufficient choice. I'd frame the decision explicitly: is the operation this lock protects idempotent or otherwise safely tolerant of rare double-execution? If yes, a simple lock is fine. If no — a genuinely non-idempotent, correctness-critical mutation — fencing tokens (or an entirely different mechanism, like the pessimistic database-row-locking from the Transactions category, which doesn't have this TTL-based-liveness problem at all since it's tied to an actual database session/transaction rather than an independent timer) are the more defensible choice.

**Source:** [Martin Kleppmann — How to do distributed locking](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)

---

## 20. When Should You Avoid Distributed Locks Entirely?

**Answer:**

"I'd avoid reaching for a distributed lock whenever the underlying problem can instead be solved by an **atomic operation on the data store itself** — which, for a huge fraction of real 'we need mutual exclusion' scenarios, it actually can. A single atomic `UPDATE inventory SET quantity = quantity - ? WHERE sku = ? AND quantity >= ?` (checking sufficiency and decrementing in one atomic statement) achieves the actual business requirement ('don't oversell inventory') without any lock at all, and without any of the TTL-based liveness problems from question 18, because the database's own atomicity guarantee — not an external, timer-based coordination mechanism — is what's actually enforcing correctness.

More broadly, I'd avoid distributed locks whenever: the operation can be made **idempotent** instead (question 25 in the Transactions category, and question 5 in the REST API Design file) — if running the operation twice concurrently produces the same correct end result either way, there's no need to prevent concurrent execution via a lock at all; a database's own transactional guarantees (optimistic or pessimistic locking, both covered extensively in the Transactions category) already solve the exact problem for data that lives in that database — reaching for a *separate*, external Redis lock on top of a database that already has its own perfectly adequate concurrency-control mechanisms is usually unnecessary, added complexity solving a problem the database already solves natively. I'd reserve genuine distributed locks specifically for coordination problems that **don't** map onto a single atomic data-store operation or an idempotency-based design — e.g., ensuring only one instance of a scheduled job runs across a fleet of application instances, where there's no natural 'atomic database operation' expressing that coordination requirement directly."

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

**Where staff-level interviews push further:**

I'd frame this as a general design principle worth stating explicitly in any architecture review: **reach for atomicity at the data layer first, idempotency second, and a distributed lock only as a last resort** for coordination problems that genuinely don't map onto either of the first two — teams that default to "add a Redis lock" as the reflexive answer to any concurrency concern often end up with unnecessary complexity and the genuine safety gaps from question 18, when the actual underlying problem had a much simpler, more robust, lock-free solution already available in the database they were already using. I'd also mention that even the legitimate "run this job on exactly one instance" use case is often better served by dedicated tooling built for that exact purpose (Kubernetes `CronJob` with appropriate concurrency policy settings, Quartz's own clustered-scheduler mode with database-backed coordination) rather than a hand-rolled Redis lock, since those tools have already worked through the edge cases (a job that runs long, a node that dies mid-execution) that a simple hand-rolled lock implementation is likely to get subtly wrong.

**Source:** [Martin Kleppmann — How to do distributed locking](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)

---

## 21. Compare Fixed-Window, Sliding-Window, and Token-Bucket Rate Limiting

**Answer:**

"**Fixed window**: count requests within a fixed, aligned time window (e.g., 'requests this calendar minute'), reset the counter to zero at each window boundary. Simple to implement (a single counter key with a TTL matching the window), but has a real correctness gap at window boundaries: a client can send its full quota right at the very end of one window, and its full quota again right at the very start of the next, achieving up to **double** the intended rate within a short span straddling the boundary, even though each individual window's count never technically exceeded its limit.

**Sliding window** (either a true sliding log of individual request timestamps, or the more common, cheaper approximation — a weighted average between the current and previous fixed windows, proportional to how far into the current window you are) fixes the boundary-burst problem by evaluating the rate over a continuously-moving window rather than discrete, resettable buckets — at the cost of somewhat more computation/storage (a true sliding log needs to store individual timestamps, or at least enough state to compute the weighted approximation) than a single fixed counter.

**Token bucket** models a bucket that holds up to a maximum number of tokens, refilling at a steady rate over time; each request consumes one token, and a request is rejected only if the bucket is empty. This naturally supports **bursts** — a client that hasn't made requests in a while has a full bucket and can burst up to the bucket's capacity all at once — while still enforcing a steady long-run average rate via the refill rate, which is often a better match for real, naturally bursty traffic patterns than a strict, unforgiving fixed-rate limit."

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

**Where staff-level interviews push further:**

I'd give a practical recommendation: token bucket is generally my default choice for rate-limiting real client traffic, specifically because real traffic patterns are naturally bursty (a user opening several tabs at once, a batch of retries), and a token bucket accommodates that burstiness gracefully while still enforcing a meaningful long-run average, whereas a strict fixed-window limit can feel unnecessarily punishing for legitimate, momentarily-bursty usage that never actually exceeds a reasonable *average* rate. I'd reserve fixed-window for cases where implementation simplicity genuinely matters more than precision (a low-stakes, coarse-grained limit) and where the boundary-burst gap's consequence is acceptable, and I'd reach for a true sliding-window-log approach specifically when precise, gap-free rate enforcement is a hard requirement (a security-sensitive limit, like login-attempt throttling, where the boundary-burst gap could be meaningfully exploited).

**Source:** [Cloudflare — Counting Things: Rate Limiting](https://blog.cloudflare.com/counting-things-a-lot-of-different-things/), [Redis Documentation — Rate Limiting Patterns](https://redis.io/docs/latest/develop/use-cases/rate-limiter/)

---

## 22. How Would You Build an Atomic Rate Limiter Using Lua?

**Answer:**

"A rate limiter implemented as multiple separate Redis commands (a `GET` to check the current count, then an `INCR` if under the limit) has exactly the check-then-act race condition problem covered throughout this category — two concurrent requests can both read the same 'under limit' count before either one's increment lands, both proceed, and the limit is silently exceeded. Redis's **Lua scripting** (`EVAL`) solves this cleanly: a Lua script executes **atomically** on the Redis server — no other command, from any other client, can execute in between any of the Lua script's own internal operations — so a rate-limiting check-and-increment, expressed entirely within one Lua script, becomes genuinely atomic as a whole, with no possibility of a race between the check and the increment, regardless of how many concurrent clients are hitting the same key simultaneously."

**Code:**

```lua
-- rate_limiter.lua — executed ATOMICALLY on the Redis server; no other
-- command from ANY client can interleave with this script's execution
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])

local current = redis.call('GET', key)
if current and tonumber(current) >= limit then
    return 0 -- rejected — over limit
end

redis.call('INCR', key)
redis.call('EXPIRE', key, window) -- only meaningfully sets TTL on first increment,
                                     -- but harmless to reset on every call here
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

**Where staff-level interviews push further:**

I'd bring up that Lua scripting's atomicity guarantee is genuinely the same underlying mechanism (single-threaded command execution) that makes plain individual Redis commands atomic in the first place — a Lua script is just a way of composing multiple operations into one larger atomic unit, rather than a fundamentally different mechanism, which is a useful mental model for recognizing when Lua is (and isn't) the right tool: any time a Redis-based operation needs multiple logically-related steps to happen as one atomic unit (a check-and-increment, a read-modify-write across multiple keys), Lua is the natural fit, whereas a single, already-atomic Redis command (a plain `INCR`, a single `SET NX`) doesn't need it at all. I'd also mention the operational trade-off worth being aware of: because a Lua script blocks Redis's single-threaded execution for its entire duration, a genuinely slow or unbounded Lua script (one that loops over a huge dataset, say) has exactly the same "blocks the whole node for everyone" risk as the large-key problem from question 14 — Lua scripts used for rate limiting or similar small, bounded operations are fine, but Lua isn't a place to put unbounded or heavy computation.

**Source:** [Redis Documentation — Scripting with Lua](https://redis.io/docs/latest/develop/interact/programmability/eval-intro/), [Redis Documentation — Rate Limiting Patterns](https://redis.io/docs/latest/develop/use-cases/rate-limiter/)

---

## 23. How Do Redis Transactions Differ From Relational Transactions?

**Answer:**

"Redis's `MULTI`/`EXEC` mechanism queues a batch of commands on the client's connection and executes them all together, atomically, with no other client's commands able to interleave in between them — that part is genuinely similar in spirit to a relational transaction's isolation guarantee. But the differences from a full relational transaction are significant and worth stating precisely, since 'Redis transaction' invites an assumption of much stronger semantics than it actually provides.

There is **no rollback** on a command-level failure within the queued batch — if one command in a `MULTI`/`EXEC` block fails at *execution* time (as opposed to a syntax error caught at queue time, which does abort the whole transaction before execution even starts), Redis simply continues executing the *remaining* commands in the batch anyway; there's no ACID-style 'undo everything already applied' behavior for a runtime failure partway through, which is fundamentally different from a relational database rolling back an entire transaction on any constraint violation or error. There's also no genuine **isolation** in the sense of one transaction's in-progress state being invisible to concurrent readers until commit — Redis's atomicity guarantee is about *no interleaving of other clients' commands during execution*, not about hiding partial, in-progress state (which doesn't really apply the same way, since the whole batch executes essentially instantaneously from other clients' perspective anyway, given Redis's single-threaded execution model). And Redis transactions have **no equivalent of a `WHERE`-clause-based conditional check spanning the whole transaction** the way a relational transaction naturally supports — Redis's `WATCH` command provides a narrower, optimistic-concurrency-style mechanism (abort the whole transaction if a watched key changed before `EXEC`), which is closer in spirit to optimistic locking than to a relational transaction's general isolation model."

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

**Where staff-level interviews push further:**

I'd bring up that this lack of true rollback is exactly why Lua scripting (question 22) is often the better tool than `MULTI`/`EXEC` when genuine conditional logic or multi-step correctness is needed — a Lua script gives you actual programmatic control (checking a value and deciding whether to proceed with subsequent operations *before* they're ever issued, all within the same atomic execution), whereas `MULTI`/`EXEC` just blindly queues and executes a fixed, pre-determined batch of commands with no ability to make command N's behavior depend on command N-1's actual runtime result within the same transaction. I'd frame the practical guidance as: `WATCH`/`MULTI`/`EXEC` is reasonable for simple optimistic-concurrency scenarios (check a value hasn't changed, then apply a fixed set of writes), but Lua scripting is the more powerful, more correct tool whenever the operation needs actual conditional logic based on values read *during* the atomic operation itself.

**Source:** [Redis Documentation — Transactions](https://redis.io/docs/latest/develop/interact/transactions/)

---

## 24. What Do Pipelines Improve, and What Do They Not Guarantee?

**Answer:**

"Pipelining lets a client send **multiple commands to Redis without waiting for each individual response** before sending the next one — all the commands are sent in a batch over the network, and Redis processes and returns all their responses together, dramatically reducing the total network round-trip overhead compared to sending each command and waiting for its individual reply one at a time. For a client issuing many independent commands (e.g., fetching 100 different keys), pipelining can turn 100 round trips into effectively one, which is a substantial latency win purely from eliminating repeated network round-trip cost — this is fundamentally a **network/latency optimization**, not a correctness or atomicity feature.

Critically, pipelining provides **no atomicity guarantee at all** — unlike `MULTI`/`EXEC`, other clients' commands *can* interleave with a pipelined batch's individual commands as Redis processes them one at a time internally (pipelining just changes how commands are *transmitted* over the network, not how they're *executed* on the server — each command in the pipeline is still executed as its own independent, individually-interleavable operation from the server's point of view). If a client needs both the network-efficiency of pipelining *and* an atomicity guarantee that no other client's commands interleave with the batch, `MULTI`/`EXEC` (which is itself typically pipelined under the hood by client libraries) is the tool that provides that, not plain pipelining alone."

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

**Where staff-level interviews push further:**

I'd bring up the common, real mistake this distinction guards against: assuming pipelining provides the same atomicity as `MULTI`/`EXEC` because they're both "batching multiple commands together" — this is a genuine, easy-to-make confusion, and code that pipelines a read-then-conditional-write sequence expecting no other client to interleave in between is silently vulnerable to exactly the race conditions this whole category has been building toward, since pipelining offers zero protection against that. I'd frame the clear distinction as: reach for pipelining purely to reduce network round-trip overhead for a batch of otherwise-independent commands; reach for `MULTI`/`EXEC` (or Lua, for anything needing actual conditional logic) specifically when atomicity/no-interleaving is the actual requirement — and never assume one gives you the other's guarantee.

**Source:** [Redis Documentation — Pipelining](https://redis.io/docs/latest/develop/use/pipelining/)

---

## 25. How Would You Version Cache Keys During a Deployment?

**Answer:**

"The core problem a deployment introduces: if a new application version changes the **shape** of what's cached (a different serialization format, a different set of fields in a cached DTO, a changed computation that produces a different-but-same-key value), and the old version is still running simultaneously during a rolling deployment, both versions reading/writing the **same cache key** can produce genuinely broken behavior — the new version might read data the old version wrote in the old shape and fail to deserialize it correctly (or silently misinterpret it), or vice versa.

The standard fix is embedding a **version identifier directly into the cache key itself** — so the old and new application versions, even though they're running simultaneously during a rolling deployment, are structurally reading and writing to **entirely different, non-overlapping keys**, eliminating any possibility of cross-version interference. This does mean the *old* version's cache entries become 'orphaned' (nothing reads them anymore once the deployment completes) and simply age out via their normal TTL, rather than needing any explicit cleanup — a clean, low-effort trade-off, since the storage cost of some temporarily-orphaned old-format entries is trivial compared to the risk of cross-version cache corruption."

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

**Where staff-level interviews push further:**

I'd bring up that the version number should be bumped specifically whenever the **cached value's shape or computation logic changes** — not on every deployment indiscriminately, since bumping it unnecessarily on every deploy would mean every rolling deployment causes a full, unnecessary cache-cold-start (every key effectively becomes new, and the database absorbs a full cache-miss burst it didn't actually need to). I'd advocate for treating "does this deployment change what gets cached or how" as an explicit, deliberate question during code review/release planning, with the version bump applied only when the answer is genuinely yes — connecting this discipline directly to the REST API Design file's backward-compatibility discussion, since "does this change break existing readers of this data" is fundamentally the same question, just applied to a cache entry's shape instead of an API response's shape.

**Source:** [AWS — Caching Best Practices](https://aws.amazon.com/caching/best-practices/)

---

## 26. How Would Blue and Green Versions Share a Cache Safely?

**Answer:**

"Building directly on question 25's versioned-key mechanism, blue/green deployment adds a specific wrinkle: unlike a typical rolling deployment (where the old version gradually scales down as the new version scales up, both briefly coexisting), blue/green often has **both environments fully running simultaneously** for a longer, more deliberate cutover window (verification, gradual traffic shifting, an easy instant-rollback option) — meaning the 'old and new versions coexisting' window that motivates cache-key versioning can be considerably longer and more deliberate for blue/green than for a typical fast rolling deploy.

The same versioned-cache-key mechanism from question 25 applies directly and is the right foundation, but blue/green's explicit, controlled cutover model opens up an additional consideration: whether blue and green should share the **same underlying Redis instance/cluster at all**, versus using entirely separate cache infrastructure per environment. Sharing one Redis instance (with versioned keys keeping the two environments' entries from colliding) is simpler operationally and avoids provisioning/paying for duplicate cache infrastructure, but it does mean a genuinely severe problem in one environment (a runaway key-generation bug, a memory-exhaustion event) could, in principle, degrade the *shared* Redis instance enough to also affect the other, otherwise-healthy environment. Fully separate cache infrastructure per environment eliminates that specific cross-environment blast-radius risk entirely, at the cost of running (and keeping warm/populated) duplicate caching infrastructure during the cutover window."

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

**Where staff-level interviews push further:**

I'd bring up that this decision (shared vs. separate cache infrastructure) should be driven by the actual blast-radius tolerance for the specific deployment — for a routine, low-risk blue/green cutover, a shared Redis instance with versioned keys is usually a perfectly reasonable, cost-efficient default; for a genuinely high-stakes migration (a major schema change, a change to a component with a history of causing cache-related incidents), I'd lean toward the extra cost of fully separate cache infrastructure specifically to guarantee that a problem discovered in the new (green) environment during the cutover window can't possibly degrade the still-serving-production-traffic old (blue) environment's cache performance, preserving a genuinely clean, safe rollback path if green turns out to have a problem.

**Source:** [Martin Fowler — BlueGreenDeployment](https://martinfowler.com/bliki/BlueGreenDeployment.html)

---

## 27. How Do You Prevent Stale Cached Authorization Decisions?

**Answer:**

"Caching authorization decisions (a user's roles/permissions, a computed 'can this user access this resource' result) is a genuinely tempting performance optimization — authorization checks can be expensive, and they happen on nearly every request — but it introduces a specific, security-relevant staleness risk that's more severe than typical data staleness: if a user's access is **revoked** (a role removed, an account suspended, a permission explicitly denied due to a detected security issue) but a cached 'authorized' decision for that user is still being served, the revocation has **no actual effect** until the cache entry expires, meaning a user who should be immediately locked out can continue performing authorized actions for however long the cache TTL allows — a genuinely dangerous gap for a security control specifically, in a way that a stale product price or a stale view count simply isn't.

My approach: use a **much shorter TTL** for authorization-decision caching than would typically be chosen for general data caching (seconds, not minutes), specifically because the cost of over-caching here is a security exposure window, not just a minor staleness inconvenience — and for genuinely security-critical revocation events (an account suspension, a detected compromise), I'd trigger **explicit, immediate invalidation** of that specific user's cached authorization entries as part of the revocation action itself, rather than relying purely on a short TTL to eventually catch up — treating the short TTL as a backstop for cases the explicit invalidation might miss, not as the primary mechanism for something this security-sensitive."

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

**Where staff-level interviews push further:**

I'd bring up that this exact risk — cached authorization decisions not reflecting a recent revocation — is directly analogous to the JWT-revocation-difficulty discussion in the Spring Security file (a self-contained, cached credential/decision that's hard to invalidate early once issued/cached), and the same fundamental trade-off applies: the shorter the cache lifetime, the smaller the exposure window, but the higher the performance cost of re-checking authorization more frequently. I'd advocate for treating authorization-decision caching as needing its own explicit, security-conscious review — distinct from the general data-caching TTL discipline in question 10 — precisely because the consequence of getting the staleness window wrong here is a genuine security incident (a suspended/revoked user retaining access), not merely a minor data-freshness inconvenience, and that distinction should drive meaningfully more conservative choices (shorter TTLs, mandatory explicit invalidation on revocation events) than would be applied to typical business data.

**Source:** [OWASP — Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)

---

## 28. How Should an Application Behave When Redis Is Unavailable?

**Answer:**

"This is fundamentally the same question as any dependency-availability question from the REST API Design and Spring Boot Internals categories — the correct answer depends entirely on **whether Redis is being used as a cache or a system of record** (question 1), and this is exactly why that distinction matters so much architecturally, not just conceptually.

If Redis is purely a cache (data reconstructible from the database), the application should treat a Redis outage as **degraded, not broken** — fall back to reading directly from the database on every cache-layer failure (a connection timeout, an exception from the Redis client), accepting higher database load and higher latency for the duration of the outage, but continuing to correctly serve requests. This requires the application code to explicitly wrap cache access with fallback logic (or use a resilience library's circuit breaker specifically around the cache client) rather than letting a Redis exception propagate up and fail the entire request — a design mistake I've seen cause real incidents, where a 'just a cache' dependency being down took down the whole application, because the calling code had no fallback path and simply let the cache exception become a request failure.

If Redis is being used as a system of record for some specific data (question 1's narrower, deliberate use case), an outage genuinely means that specific functionality is unavailable — a rate limiter backed only by Redis, with no fallback, either has to fail open (allow all requests, accepting a temporary loss of rate-limiting protection) or fail closed (reject all requests, prioritizing safety over availability) during the outage, and which choice is correct depends entirely on which failure mode is less bad for that specific feature."

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

**Where staff-level interviews push further:**

I'd bring up that the "fall back to the database on cache failure" pattern has a real, important danger of its own worth naming explicitly: if Redis goes down during a period of significant traffic, and every request that would normally hit the cache instead falls through to the database simultaneously, the sudden, full-traffic load shift can itself overwhelm the database — effectively a cache-outage-triggered version of the cache-stampede problem from question 6, just triggered by total cache unavailability rather than one key's expiration. I'd recommend combining the fallback with a circuit breaker and/or load-shedding on the database-fallback path specifically (rather than assuming the database can simply absorb 100% of what the cache was previously handling), and I'd treat "what happens to database load if the cache disappears entirely" as a required capacity-planning question to answer explicitly (ideally via a game-day/chaos-engineering exercise actually simulating a full Redis outage under realistic load) rather than an assumption left untested until an actual incident reveals whether the database can genuinely handle it.

**Source:** [Google SRE Workbook — Handling Overload](https://sre.google/sre-book/handling-overload/), [Resilience4j — Circuit Breaker](https://resilience4j.readme.io/docs/circuitbreaker)

---

## 29. What Redis Metrics Would You Monitor?

**Answer:**

"I'd group monitoring into a few categories, each catching a different class of problem this whole file has covered.

**Memory**: `used_memory` versus `maxmemory` (approaching the limit signals imminent eviction or, with `noeviction`, write failures), and eviction count/rate (`evicted_keys`) — a rising eviction rate on a policy meant to be a rare safety valve, rather than the primary memory-management mechanism, often signals the instance is undersized for its actual working set.

**Hit rate**: `keyspace_hits` versus `keyspace_misses` — a declining hit rate is the clearest signal of a caching-effectiveness regression (a bad TTL choice, question 7's penetration/pollution problems, or simply a working set that's outgrown what's practical to cache) and directly correlates with increased load pushed back onto the database.

**Latency**: command-level latency, especially watching for occasional slow outliers rather than just averages — `SLOWLOG` specifically surfaces individual slow commands (a large-key operation from question 14, an unexpectedly expensive Lua script), which averages alone can hide entirely if slow commands are rare but severe.

**Replication health**: replication lag (`master_repl_offset` versus each replica's own offset) — rising lag is an early warning for question 16's staleness risk widening beyond its normal, small window, and for question 17's failover-related data-loss risk growing larger than usual.

**Connection/client metrics**: connected client count versus `maxclients`, and blocked/rejected connection counts — a rising client count can signal a connection leak in an application (not properly returning connections to a pool) well before it becomes an outright connection-exhaustion outage."

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

**Where staff-level interviews push further:**

I'd bring up that hit-rate monitoring specifically needs to be **segmented per key-pattern/cache-use-case**, not tracked as one single aggregate number across the entire Redis instance — an aggregate hit rate can look perfectly healthy overall while one specific, important cache use case has silently degraded (a regression in one feature's caching logic), simply because it's averaged out by many other, unrelated, still-healthy cache usages sharing the same instance. I'd advocate for per-prefix or per-feature hit-rate dashboards (tagging metrics by cache key namespace, not just a single instance-wide number) specifically so a regression in one specific caching use case is visible and alertable on its own, rather than hidden inside an instance-wide average that happens to still look fine.

**Source:** [Redis Documentation — INFO command](https://redis.io/docs/latest/commands/info/), [Redis Documentation — Slow Log](https://redis.io/docs/latest/commands/slowlog/)

---

## 30. Describe a Cache Incident That Increased Rather Than Reduced Database Load

**Answer:**

"I'd walk through a representative, composite shape rather than claim one specific universal incident, since the pattern (and its root causes) recur across many real systems in a genuinely predictable way, which is exactly what makes it worth having ready as a story: a service's cache-hit rate was healthy and stable for months, and then a routine deployment — one that happened to change the serialization format of a widely-cached DTO, without anyone realizing that change had cache implications — went out without a corresponding cache-key version bump (question 25's exact mitigation, skipped because nobody flagged the change as cache-relevant during review). Every subsequently-cached read using the new format either failed deserialization against old-format entries still sitting in the cache, or (depending on the specific deserialization library's error tolerance) silently misinterpreted them — either way, the *effective* hit rate collapsed to near-zero, since virtually every cache read was now either an outright failure (triggering a fallback to the database) or, worse, an incorrect value that then triggered additional corrective reads once the bad data was noticed downstream. The database, which had been comfortably handling only cache-miss traffic for months, suddenly received close to 100% of the read volume it had been architecturally relying on the cache to absorb — and because the database's own capacity had been sized around the assumption that the cache would keep absorbing the bulk of read traffic (question 28's exact capacity-planning gap), it was never tested against, or provisioned for, this full-traffic-fallback scenario, and it began timing out under the sudden load, cascading into broader request failures well beyond just the specific endpoint that used the changed DTO."

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

**Where staff-level interviews push further:**

I'd emphasize the specific, generalizable insight this incident illustrates: a cache being present and effective for a long time creates an easy-to-miss, implicit architectural dependency — the database's actual, tested capacity may have quietly become "capacity assuming the cache is working," rather than "capacity for the application's real, full traffic," and that assumption is only ever tested for real the moment the cache stops being effective, whether from an outage (question 28) or, as in this incident, a subtler effectiveness collapse from a mismatched deployment. I'd frame the durable, systemic fix as making that implicit assumption explicit and periodically *verified* — treating "can our database actually survive the cache disappearing or becoming ineffective" as a standing question answered via deliberate testing, not an assumption that's only ever validated involuntarily, during an actual production incident, which is a much more expensive and disruptive way to find out the answer was no.

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
