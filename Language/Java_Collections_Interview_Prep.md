# Java Collections — Interview Prep (Mid → Staff Level, with Code & Sources)

> **Target level:** Mid → Staff · **Baseline:** Java/JDK 21 (LTS) · **Last verified:** 2026-08-22 · **Prerequisites:** core Java syntax, generics, `equals()`/`hashCode()` basics

How to use this: each question has a **core answer** (100–180 words — roughly what you'd actually say out loud in 40–70 seconds), a **staff-level extension** with the deeper trade-offs pushed out of the core response rather than dropped, a **code example** you could sketch on a whiteboard or IDE, **follow-up questions** an interviewer is likely to probe with next, and **sources**. Read just the core answer for a fast pass; read the extension and follow-ups when you want the staff-level depth on that specific topic — because the mid-level and staff-level bar for the *same* question isn't the depth of vocabulary, it's whether you can talk about what happens when it breaks in production.

<!-- toc -->
## Table of Contents

- [1. How Does `HashMap` Work Internally — Collisions, Resizing, Treeification, Equality?](#1-how-does-hashmap-work-internally--collisions-resizing-treeification-equality)
- [2. What Can Go Wrong If a Mutable Object Is Used as a `HashMap` Key?](#2-what-can-go-wrong-if-a-mutable-object-is-used-as-a-hashmap-key)
- [3. When Would You Use `ConcurrentHashMap` Instead of a Synchronized Map?](#3-when-would-you-use-concurrenthashmap-instead-of-a-synchronized-map)
- [4. Are Compound Operations on `ConcurrentHashMap` Thread-Safe? `get`-then-`put` vs. `computeIfAbsent`](#4-are-compound-operations-on-concurrenthashmap-thread-safe-get-then-put-vs-computeifabsent)
- [5. How Would You Design an In-Memory Structure Supporting High Write Concurrency and Snapshot Reads?](#5-how-would-you-design-an-in-memory-structure-supporting-high-write-concurrency-and-snapshot-reads)
- [6. Compare `ArrayList`, `LinkedList`, `ArrayDeque`, and `CopyOnWriteArrayList`](#6-compare-arraylist-linkedlist-arraydeque-and-copyonwritearraylist)
- [7. When Is `CopyOnWriteArrayList` a Good Choice, and When Is It Disastrous?](#7-when-is-copyonwritearraylist-a-good-choice-and-when-is-it-disastrous)
- [8. How Do Weakly Consistent Iterators Differ From Fail-Fast Iterators?](#8-how-do-weakly-consistent-iterators-differ-from-fail-fast-iterators)
- [9. What Are the Memory and Performance Costs of Boxed Collections?](#9-what-are-the-memory-and-performance-costs-of-boxed-collections)
- [10. How Would You Diagnose a Collection That Continuously Grows in Production?](#10-how-would-you-diagnose-a-collection-that-continuously-grows-in-production)
- [11. How Would You Build an LRU Cache Using `LinkedHashMap`?](#11-how-would-you-build-an-lru-cache-using-linkedhashmap)
- [12. `TreeMap`/`TreeSet` — How Does Ordering Work, and What Breaks If `compareTo` Is Inconsistent With `equals`?](#12-treemaptreeset--how-does-ordering-work-and-what-breaks-if-compareto-is-inconsistent-with-equals)
- [13. What Is `WeakHashMap`, and When Would You Actually Reach for It?](#13-what-is-weakhashmap-and-when-would-you-actually-reach-for-it)
- [14. `Arrays.asList()`, `List.of()`, and `Collections.unmodifiableList()` — What Are the Actual Mutability Differences?](#14-arraysaslist-listof-and-collectionsunmodifiablelist--what-are-the-actual-mutability-differences)
- [15. How Does `PriorityQueue` Work Internally, and What Are Its Complexity Trade-Offs?](#15-how-does-priorityqueue-work-internally-and-what-are-its-complexity-trade-offs)
- [Sources & Further Reading — Consolidated](#sources--further-reading--consolidated)

<!-- /toc -->

---

## 1. How Does `HashMap` Work Internally — Collisions, Resizing, Treeification, Equality?

**Core answer:**

"A `HashMap` is an array of buckets under the hood — `Node<K,V>[] table`, 16 slots by default. On `put(key, value)`, Java takes `key.hashCode()`, runs it through a spreading function to mix the high bits into the low bits, and uses `(n - 1) & hash` to pick a bucket index. If nothing's there, the entry just drops in. If something's already there — a collision — it either walks a linked list comparing each existing key with `.equals()`, or, if that bucket's gotten long enough, walks a small red-black tree instead.

Resizing happens once size crosses `capacity × loadFactor` — 12 entries in a 16-bucket map by default, since load factor is 0.75. The table then doubles and every entry gets rehashed into its new spot.

Treeification is the Java 8 addition: if a single bucket's chain grows past 8 entries, *and* the table has at least 64 buckets total, that bucket converts to a tree, turning worst-case lookup from O(n) to O(log n)."

**Staff-level extension:**

The 0.75 load factor and doubling-capacity strategy is itself a space/time trade-off: a higher load factor packs entries denser (less wasted array space) at the cost of longer collision chains before treeification kicks in; a lower load factor spreads entries thinner for faster average lookups at the cost of more allocated-but-empty bucket slots. Pre-sizing a `HashMap`'s initial capacity when the eventual size is roughly known avoids paying for several incremental doubles-and-rehashes during warmup — a real, measurable cost on hot startup paths that create many entries. Treeification itself is a safety net for pathological collision cases (a bad or adversarial `hashCode()`), not the everyday path — most buckets never get anywhere close to 8 entries.

**Example:**

```java
// Demonstrating a deliberate collision — two keys, same hash, same bucket
class BadKey {
    final int id;
    BadKey(int id) { this.id = id; }

    @Override
    public int hashCode() {
        return 42; // terrible on purpose — forces every BadKey into the same bucket
    }

    @Override
    public boolean equals(Object o) {
        return o instanceof BadKey bk && bk.id == this.id;
    }
}

Map<BadKey, String> map = new HashMap<>();
for (int i = 0; i < 20; i++) {
    map.put(new BadKey(i), "value-" + i); // all 20 collide into one bucket
}
// Below the treeify threshold this bucket is just a linked list Java walks
// with .equals() on every lookup — O(n) instead of O(1).
```

**Follow-up questions:**

- *"Why is the Java 8 resize cheaper than a full rehash?"* — Because capacity is always a power of two and exactly doubles, each existing entry either stays at its current index or moves to `index + oldCapacity` — nothing else is possible. Resize just splits each bucket's chain into a "stays" list and a "moves" list using one extra bit of the already-computed hash, rather than recomputing every hash from scratch.
- *"Can a `HashMap` have a `null` key?"* — Exactly one; it lives in bucket 0, since there's no hash to compute for it.
- *"Is iteration order guaranteed?"* — No. It's explicitly unspecified and can change across JDK versions or even across resizes — never write code that depends on `HashMap` iteration order.

**Sources:** [`HashMap` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashMap.html)

---

## 2. What Can Go Wrong If a Mutable Object Is Used as a `HashMap` Key?

**Core answer:**

"The map decides which bucket a key belongs in at insertion time, based on `hashCode()` at that exact moment. If you mutate the key afterward in a way that changes its hash code, the map has no way of knowing — the entry is still sitting in its *original* bucket, but a fresh `get()` or `remove()` call now computes a *different* hash from the mutated key and looks in the wrong bucket entirely, so the lookup fails. That doesn't make the entry unreachable in general, though: iterating the map (`keySet()`, `entrySet()`, `forEach()`) walks every bucket regardless of hash, so the entry turns up there with no trouble. What's genuinely broken is *hash-based single-key lookup and removal* while the mutation is in effect — not the entry's reachability through the API as a whole. It's still a nasty, silent bug class, because nothing throws and `size()` looks completely normal."

**Staff-level extension:**

If the key's hash-relevant state is later restored to what it was at insertion time, `get()`/`remove()` start working again too, since the recomputed hash now matches the bucket the entry actually lives in once more. That has a practical consequence for anyone trying to fix this after the fact: a naive fix that calls `map.remove(key)` after noticing a lookup failure will itself silently no-op (it's using the same broken hash-based lookup), while a fix that iterates to find and remove the stale entry will actually work. I'd talk about this as a design principle, not just a gotcha: value objects used as map/set keys should be immutable by construction. Java 16+ `record` types are a good fit *if you're careful* — but records are only **shallowly** immutable: the component references can't be reassigned, but if a component's own type is mutable (a `List`, a `Date`, another mutable class), the record's `hashCode()` still changes when that referenced object is mutated in place, reproducing exactly this bug. Records work well as map keys when all record components are themselves immutable (other records, boxed primitives, `String`, `List.of(...)`), or when a mutable input is defensively copied in the compact constructor before being stored. This is especially dangerous in caching layers, where keys are often composite objects (e.g., a request-parameters object) that some other part of the codebase might mutate in place without realizing it's also a live cache key elsewhere.

**Example:**

```java
class MutableKey {
    List<String> tags;
    MutableKey(List<String> tags) { this.tags = tags; }

    @Override
    public int hashCode() { return tags.hashCode(); } // derived from mutable contents
    @Override
    public boolean equals(Object o) {
        return o instanceof MutableKey mk && mk.tags.equals(this.tags);
    }
}

Map<MutableKey, String> map = new HashMap<>();
MutableKey key = new MutableKey(new ArrayList<>(List.of("a", "b")));
map.put(key, "original value");

System.out.println(map.get(key)); // "original value" — works fine

key.tags.add("c"); // mutate the key AFTER insertion — hashCode now changes

System.out.println(map.get(key));    // null — hash-based lookup goes to the wrong bucket
System.out.println(map.remove(key)); // null — same problem, can't remove via hash lookup
System.out.println(map.size());      // 1 — the entry is still there

for (MutableKey k : map.keySet()) {  // iteration doesn't hash — it walks every
    System.out.println(k.tags);      // bucket, so the entry IS found: prints [a, b, c]
}

key.tags.remove("c"); // restore the key to its original hash-relevant state
System.out.println(map.get(key)); // "original value" — get() works again, because
                                    // the recomputed hash now matches the bucket
                                    // the entry has been sitting in the whole time
```

**Follow-up questions:**

- *"Is the entry ever truly unreachable?"* — Not through iteration, no — only hash-based `get()`/`remove()` are affected while the mutation is in effect.
- *"How would you fix a map that already has a stale-hash entry?"* — Iterate to find and remove it directly; `map.remove(key)` alone won't work, since it relies on the same broken hash-based lookup.
- *"Are records always safe as map keys?"* — Only if every component is itself immutable, or mutable inputs are defensively copied — records are shallowly immutable, not deeply.

**Sources:** [`Object.hashCode()` contract, Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Object.html#hashCode()), [`java.lang.Record` Javadoc — "a shallowly immutable, transparent carrier"](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Record.html)

---

## 3. When Would You Use `ConcurrentHashMap` Instead of a Synchronized Map?

**Core answer:**

"`Collections.synchronizedMap()` wraps every method in one shared lock — so even two threads reading completely different keys have to take turns. It works, but it turns the map into a single-lane road no matter how many threads want in.

`ConcurrentHashMap` doesn't use one big lock. It locks at a much finer grain — individual bins, essentially — and reads are lock-free entirely. Multiple threads can read concurrently without blocking each other, and writes to different bins can proceed in parallel too. Any time I've got genuine concurrent read/write traffic — a shared cache, counters hit by multiple request threads — I reach for `ConcurrentHashMap`. `synchronizedMap` I'd only use for low-contention or legacy situations where I'm not trying to optimize throughput."

**Staff-level extension:**

Thread safety here is per-operation, not per-invariant. `get`/`put`/`remove` are atomic, and so are the documented compound methods (`putIfAbsent`, `computeIfAbsent`, `merge`, `replace`, etc.) — each one is guaranteed atomic on its own. But an invariant that spans *multiple* keys, or spans the map plus some other resource (e.g., "this map and that counter must always agree"), is not automatically protected just because the underlying map is a `ConcurrentHashMap` — that kind of compound, cross-key invariant still needs its own coordination (a lock, a single-key redesign, or an atomic compound method that captures the whole invariant in one call). One sharp edge worth knowing: unlike `HashMap`, `ConcurrentHashMap` **does not allow `null` keys or values**, deliberately — in a concurrent map, `map.get(key) == null` is ambiguous ("not present" vs. "present with a null value"), and the usual `containsKey()` disambiguation isn't safe here since another thread could remove the entry between the two calls. Disallowing `null` outright closes off the ambiguity.

**Example:**

```java
// synchronizedMap: one lock for everything, including iteration —
// and iteration isn't even automatically protected, you have to do it yourself:
Map<String, Integer> syncMap = Collections.synchronizedMap(new HashMap<>());
synchronized (syncMap) {           // required manually — easy to forget
    for (String key : syncMap.keySet()) {
        System.out.println(key);
    }
}

// ConcurrentHashMap: individual operations (get/put/remove, and the
// documented compound methods below) are thread-safe without external
// locking — no need to wrap this in synchronized(), unlike synchronizedMap:
Map<String, Integer> chm = new ConcurrentHashMap<>();
chm.put("a", 1);
for (String key : chm.keySet()) {  // safe to iterate while other threads mutate
    System.out.println(key);
}
```

**Follow-up questions:**

- *"How did this work before Java 8?"* — Java 7 used segment-based locking: the map was split into a fixed number of `Segment`s, each independently lockable, so writes to different segments could proceed in parallel while writes to the *same* segment still serialized. 16 was just the **default** `concurrencyLevel`; the actual count scaled with whatever was passed to the constructor.
- *"What changed in Java 8?"* — Segments were replaced entirely with per-bin locking — `synchronized` blocks on individual bin head nodes plus CAS for inserting into empty bins — finer granularity that scales with bin count, plus the same treeification behavior as `HashMap` for badly-collided bins.
- *"Can `ConcurrentHashMap` guarantee a multi-key invariant?"* — No — only individual operations and the documented compound methods are atomic; anything spanning multiple keys or an external resource needs its own coordination.

**Sources:** [`ConcurrentHashMap` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html)

---

## 4. Are Compound Operations on `ConcurrentHashMap` Thread-Safe? `get`-then-`put` vs. `computeIfAbsent`

**Core answer:**

"Individual calls are atomic — one `get()`, one `put()`, each safe on its own. But *chaining* two calls together is not automatically atomic as a unit, and this trips people up constantly. If you do `if (map.get(key) == null) map.put(key, expensiveCompute())`, two threads can both see `null` at the same instant and both proceed — one just overwrites the other, or you've done expensive work twice for nothing. That's a textbook check-then-act race, and it doesn't matter that each individual line is thread-safe, because the *gap between* the lines is where the bug lives.

`computeIfAbsent()` fixes this because it's genuinely atomic as one operation — Java locks the specific bin for the duration of the check-and-insert, so only one thread ever actually computes and inserts for a given key."

**Staff-level extension:**

`merge()` is the sibling method worth knowing for accumulate-style updates, like a concurrent counter or histogram: `counts.merge("event-type-a", 1, Integer::sum)` atomically initializes-or-increments in one call. The general rule that separates "knows the API" from "has actually been burned by this": any lambda passed to `compute`, `computeIfAbsent`, `computeIfPresent`, or `merge` should be fast, side-effect-free, and must never try to modify the same map — it's running under a per-bin lock, and violating that can produce genuinely confusing deadlocks in production that are painful to reproduce.

**Example:**

```java
Map<String, Integer> map = new ConcurrentHashMap<>();

// BROKEN under concurrency — classic check-then-act race
if (map.get("counter") == null) {
    map.put("counter", expensiveInit()); // two threads can both get here
}

// CORRECT — atomic as a single operation
map.computeIfAbsent("counter", k -> expensiveInit());

// Sharp edge: never mutate the SAME map inside the mapping function —
// the bin is locked during this call, so this can deadlock or throw:
map.computeIfAbsent("a", k -> {
    map.put("b", 1); // DON'T DO THIS — modifying the same map mid-computation
    return 1;
});
```

**Follow-up questions:**

- *"What's the atomic way to do an increment-or-initialize counter?"* — `counts.merge("event-type-a", 1, Integer::sum)` — atomic "increment or initialize," common in rate limiters and histograms.
- *"What happens if the `computeIfAbsent` lambda modifies the same map?"* — It's running under a per-bin lock; modifying the same map from inside it can deadlock or throw, since the lock may already be held for the key being touched.

**Sources:** [`ConcurrentHashMap#computeIfAbsent` Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html#computeIfAbsent(K,java.util.function.Function))

---

## 5. How Would You Design an In-Memory Structure Supporting High Write Concurrency and Snapshot Reads?

**Core answer:**

"This is a genuinely interesting tension because the two requirements pull in opposite directions — high write concurrency wants writes to be cheap and unblocked by anything, and snapshot reads want a frozen, consistent point-in-time view, which usually means *something* gets copied or locked. My starting answer is double-buffering: writers hit a live `ConcurrentHashMap` directly with no snapshot overhead per write, and a separate, periodically-published `AtomicReference<Map<K,V>>` gives readers a lock-free, always internally-consistent point-in-time view. The trade-off I'd name explicitly: this gives readers a slightly-stale-but-internally-consistent view, not the absolute latest state — and that's usually the right trade, because true 'latest state + zero write cost + zero read cost' isn't achievable simultaneously without giving something up."

**Staff-level extension:**

I wouldn't reach for one silver-bullet answer without weighing alternatives, since a staff interviewer usually wants to see that rather than the first idea landed on:

- **Naive copy-on-write** — technically gives snapshots, but every single write pays the O(n) copy cost, which falls apart under high write volume. Wrong tool for *this* specific requirement, even though it's the "obvious" thread-safe-list answer people reach for.
- **Persistent (immutable) data structures with structural sharing** — like Clojure's persistent maps, or libraries like Vavr in Java. Each "update" produces a new immutable version that shares most of its internal tree structure with the previous version instead of copying everything, so snapshots are genuinely cheap and every version is frozen forever by construction. More complex internals, generally slower single-threaded raw throughput than a plain `HashMap`, but a legitimately elegant middle ground.
- **Event-sourcing / append-only log with periodic materialized views** — keep the log of writes as the source of truth (like a Kafka topic), and have readers work off periodically-materialized snapshots built from replaying that log — same "writers don't wait on readers" idea, just at a different architectural layer.

**Example — the double-buffering pattern:**

```java
public class SnapshotableStore<K, V> {
    // Writers hit this directly — fast, no snapshot overhead per write
    private final ConcurrentHashMap<K, V> live = new ConcurrentHashMap<>();

    // Readers needing a true point-in-time view get this instead
    private final AtomicReference<Map<K, V>> snapshot =
        new AtomicReference<>(Map.of());

    public void put(K key, V value) {
        live.put(key, value); // writers never touch the snapshot at all
    }

    // Called periodically (e.g., every N ms, or on-demand) — NOT on every write
    public void publishSnapshot() {
        snapshot.set(Map.copyOf(live)); // one O(n) copy, not one per write
    }

    public Map<K, V> readSnapshot() {
        return snapshot.get(); // lock-free, always internally consistent
    }
}
```

**Follow-up questions:**

- *"How fresh is the snapshot readers see?"* — As fresh as the last `publishSnapshot()` call, not the live map — bounded staleness, not eventual consistency in the general sense.
- *"When would naive copy-on-write actually be fine?"* — When writes are rare relative to reads (e.g., a listener registry) — see Q7 for exactly that trade-off worked through in more depth.
- *"How would this look built on Kafka instead of an in-process map?"* — Same shape at a different layer: the write log is the source of truth, and readers work off periodically-materialized views built by replaying it.

**Sources:** [`AtomicReference` Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/atomic/AtomicReference.html), [`Map.copyOf` Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Map.html#copyOf(java.util.Map))

---

## 6. Compare `ArrayList`, `LinkedList`, `ArrayDeque`, and `CopyOnWriteArrayList`

**Core answer:**

"`ArrayList` is a resizable array — O(1) random access, cache-friendly since everything's contiguous in memory, and O(n) if you're inserting or removing from the middle because it has to shift elements. It's my default unless I have a specific reason not to use it.

`LinkedList` is a doubly-linked list of individually allocated nodes. In theory, insert/remove is O(1) — but only if you're already sitting at that position via an iterator. Getting there in the first place, via `get(index)`, is O(n) anyway, and it's usually *slower* in practice than people expect, since each element is a separate heap object with pointers, meaning scattered memory and poor cache behavior.

`ArrayDeque` is a resizable circular array built for stack/queue use — no per-node overhead, much better cache locality than `LinkedList`. This is genuinely almost always my answer over `LinkedList` for queue/stack needs.

`CopyOnWriteArrayList` copies the entire backing array on every mutation. Reads are lock-free and iteration is always safe and consistent. Great when reads vastly outnumber writes; bad the moment writes get frequent or the list gets large."

**Staff-level extension:**

This question is often a trap for candidates who memorized "LinkedList is good for insertions" without understanding *why that's usually wrong in practice* on modern hardware: Big-O analysis ignores cache behavior, and cache misses dominate real-world performance far more than people expect for anything but very large N. Worth naming explicitly since it's the deeper point behind the whole comparison, not just an `ArrayDeque` trivia fact.

**Example:**

```java
// Why LinkedList's O(1) insert doesn't save you if you don't already have position:
LinkedList<Integer> list = new LinkedList<>();
// list.get(500_000) is O(n) — has to walk from head or tail, whichever's closer
// ArrayList.get(500_000) is O(1) — direct array index

// ArrayDeque as a stack — no boxing overhead, no node allocation per element
Deque<Integer> stack = new ArrayDeque<>();
stack.push(1);
stack.push(2);
stack.pop(); // 2 — LIFO, and noticeably faster than java.util.Stack or LinkedList here
```

**Follow-up questions:**

- *"Does the Javadoc back up the ArrayDeque claim?"* — Yes: *"This class is likely to be faster than Stack when used as a stack, and faster than LinkedList when used as a queue."*
- *"Any gotchas migrating to ArrayDeque?"* — It explicitly prohibits `null` elements (unlike `ArrayList`) — a real trap if existing code relied on nulls as sentinel values.

**Sources:** [`ArrayDeque` Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayDeque.html)

---

## 7. When Is `CopyOnWriteArrayList` a Good Choice, and When Is It Disastrous?

**Core answer:**

"Good fit: small-to-moderate lists where reads/iteration vastly outnumber writes. The textbook case is a list of event listeners — you register a handful rarely, but fire/iterate over them constantly. Since writes are rare, the copy-on-write cost basically never gets paid, and in exchange every reader gets a lock-free, guaranteed-consistent snapshot with zero risk of a `ConcurrentModificationException`, even if a listener gets added mid-iteration.

Disastrous fit: frequent writes, or a large list. Every `add()`, `remove()`, or `set()` copies the *entire* underlying array — so a write to a 100,000-element list means allocating and copying 100,000 references regardless of how small the actual change is. Under write-heavy load that tanks throughput and creates real GC pressure from constantly discarding full-size arrays."

**Staff-level extension:**

This pattern shows up in real frameworks constantly — listener/callback registries in various parts of the JDK and common libraries use exactly this shape, because "register rarely, fire often" is an extremely common access pattern. The iterator-snapshot subtlety is worth flagging deliberately: the iterator is frozen from the moment it was created, so it will *never* see items added during that specific iteration — usually exactly what you want (stable, predictable iteration) but a real surprise for anyone who assumes an iterator reflects "live" state.

**Example:**

```java
List<Runnable> listeners = new CopyOnWriteArrayList<>();
listeners.add(() -> System.out.println("listener 1"));

for (Runnable r : listeners) {
    listeners.add(() -> System.out.println("added during iteration")); // fine!
    r.run();
}
// No ConcurrentModificationException — but note the newly-added listener
// does NOT run in THIS iteration, because the iterator is a frozen snapshot
// taken when the for-loop started.

// The disaster case, for contrast:
List<Integer> hotList = new CopyOnWriteArrayList<>();
for (int i = 0; i < 1_000_000; i++) {
    hotList.add(i); // EVERY call here copies the entire array so far — O(n^2) total
}
```

**Follow-up questions:**

- *"Would a listener added mid-iteration ever fire in that same loop?"* — No — the iterator is a frozen snapshot from creation time, so it never sees concurrent additions, by design.
- *"What's the actual cost of a write on a 100K-element list?"* — A full copy of all 100,000 references, regardless of how small the logical change is — O(n) per write, not O(1).

**Sources:** [`CopyOnWriteArrayList` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/CopyOnWriteArrayList.html)

---

## 8. How Do Weakly Consistent Iterators Differ From Fail-Fast Iterators?

**Core answer:**

"Fail-fast iterators — `ArrayList`, `HashMap`, most of the classic collections — track a hidden modification counter and check it on every step. If the collection was structurally changed by anyone since the iterator was created, the next `next()` call throws `ConcurrentModificationException`. Important nuance: this is explicitly documented as a *best-effort* detection mechanism, not a hard guarantee — you're not supposed to rely on it for actual thread-safety, only treat it as a debugging aid that catches *some* bugs.

Weakly consistent iterators — `ConcurrentHashMap`, `CopyOnWriteArrayList`, `ConcurrentLinkedQueue` — are built to tolerate concurrent modification instead of blowing up. They never throw `ConcurrentModificationException`. They guarantee to reflect the state at some point at or after iterator creation, but make no promise about whether later concurrent modifications will or won't show up mid-iteration. That relaxed guarantee is exactly what lets them avoid locking during iteration."

**Staff-level extension:**

"Best-effort" is doing real work in that sentence — the `modCount` check can miss genuine concurrent modification bugs in certain interleavings, so "my code didn't throw `CME` in testing" is never proof of thread-safety. The practical guidance: if you need to modify a collection during iteration, either use `Iterator.remove()` on a fail-fast collection, collect items to remove into a separate list and remove them after the loop, or reach for a genuinely concurrent collection (`ConcurrentHashMap.newKeySet()`, `CopyOnWriteArrayList`) if actual concurrent access is the real requirement.

**Example:**

```java
// Fail-fast in action — this throws, even single-threaded:
List<Integer> list = new ArrayList<>(List.of(1, 2, 3));
for (Integer i : list) {
    if (i == 2) list.remove(i); // throws ConcurrentModificationException
}

// The correct way to remove during iteration on a fail-fast collection:
Iterator<Integer> it = list.iterator();
while (it.hasNext()) {
    if (it.next() == 2) it.remove(); // safe — goes through the iterator itself
}

// Weakly consistent — this does NOT throw, by design:
Map<String, Integer> chm = new ConcurrentHashMap<>(Map.of("a", 1, "b", 2));
for (String key : chm.keySet()) {
    chm.put("c", 3); // no exception — might or might not show up in this iteration
}
```

**Follow-up questions:**

- *"Is passing tests without a CME proof of thread-safety?"* — No — the `modCount` check is explicitly best-effort and can miss real concurrent-modification bugs in certain interleavings.
- *"What's the safe way to remove elements while iterating a fail-fast collection?"* — `Iterator.remove()`, or collect items to remove into a separate list and remove them after the loop.

**Sources:** [`ArrayList` Javadoc — see "fail-fast" section](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayList.html), [`ConcurrentHashMap` Javadoc — see "weakly consistent" iterator description](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html)

---

## 9. What Are the Memory and Performance Costs of Boxed Collections?

**Core answer:**

"Generic collections can't hold primitives directly — `List<int>` isn't legal, only `List<Integer>`. So every `int` you put into a `List<Integer>` gets autoboxed into an `Integer` object behind the scenes. That costs you in a few ways: a raw `int` is 4 bytes, but a boxed `Integer` costs a lot more once you account for the object header — you can easily be paying 4-5x the memory for the same data. It also means pointer indirection — a primitive array is contiguous in memory and cache-friendly; a `List<Integer>` is a list of *references* to separately-allocated objects scattered around the heap, so iterating it means chasing pointers and eating cache misses. And every one of those small boxed objects is something the garbage collector eventually has to deal with — a hot loop boxing and discarding millions of values creates real GC churn a primitive array would never generate."

**Staff-level extension:**

The JLS explicitly requires the `Integer` caching behavior for values `-128` to `127` (§5.1.7, Boxing Conversion), so it's not implementation-specific trivia, it's a language guarantee that engineers routinely get bitten by anyway because `==` *looks* like it should just work. The cache's upper bound can actually be raised via `-XX:AutoBoxCacheMax` (or the `java.lang.Integer.IntegerCache.high` system property) — a fun fact but also a trap, since code that "happens to work" with `==` because the cache was tuned larger in one environment can silently break in another. For genuinely hot paths — financial calculations, large in-memory datasets, tight loops — primitive-specialized collection libraries (Eclipse Collections, fastutil) or plain arrays are the real fix; for small collections or infrequent operations, none of this matters and optimizing for it prematurely isn't worth the complexity.

**Example:**

```java
// The classic interview gotcha — Integer caching
Integer a = 100;
Integer b = 100;
System.out.println(a == b); // true — both in the cached range (-128 to 127)

Integer c = 200;
Integer d = 200;
System.out.println(c == d); // false! — outside the cache, two distinct objects

// This is exactly why you always compare boxed types with .equals(), not ==:
System.out.println(c.equals(d)); // true — correct, regardless of caching

// The memory difference, made concrete:
int[] primitives = new int[1_000_000];      // ~4MB, contiguous
Integer[] boxed = new Integer[1_000_000];   // ~4MB just for the references,
                                              // PLUS ~16-20 bytes per actual
                                              // Integer object once populated —
                                              // roughly 20MB+ total
```

**Follow-up questions:**

- *"Is Integer caching a JVM implementation detail or a language guarantee?"* — A guarantee: JLS §5.1.7 requires it for `-128` to `127`, quoting *"It is always the case that r1 == r2"* for boxed values in that range.
- *"When does boxing overhead actually matter?"* — Genuinely hot paths — large in-memory datasets, tight loops, financial calculations — not small collections or infrequent operations, where it's not worth the added complexity.

**Sources:** [JLS §5.1.7, Boxing Conversion](https://docs.oracle.com/javase/specs/jls/se21/html/jls-5.html)

---

## 10. How Would You Diagnose a Collection That Continuously Grows in Production?

**Core answer:**

"This is really a memory-leak investigation where the growing collection is just the visible symptom. First step is capturing evidence — heap dumps at intervals, either manually via `jmap` or automatically on OOM with `-XX:+HeapDumpOnOutOfMemoryError` so I've got the actual moment it broke. Then I'd load those into a profiler — Eclipse MAT or VisualVM — and compare retained size across snapshots to see what's actually growing. From there, 'path to GC roots' on the offending collection tells you exactly what's holding the reference alive — that usually points straight at the responsible code. Then I'd walk the usual suspects in roughly likelihood order: an unbounded cache with no eviction policy is probably the single most common real cause, listener registration without unregistration is a close second, `ThreadLocal` leaks in a thread-pool environment third, and plain old `static` collections, which live for the entire classloader lifetime by definition."

**Staff-level extension:**

I'd push past "how do you diagnose it once it's already a problem" into "how do you catch it before it becomes an incident" — Java Flight Recorder (JFR) running continuously with low overhead, or a scheduled `jcmd GC.class_histogram` comparison, gives you a live trend line of which classes are growing over time, so this becomes something caught by a dashboard rather than discovered via a customer complaint or an OOM crash. Also worth naming as a candidate incident story: staff-level interviews often want the *narrative* of how you traced a real one (what tool, what you saw, what the fix was, what monitoring got added afterward) more than the abstract checklist.

**Example:**

```bash
# Capture a heap dump on demand (doesn't require an OOM to happen)
jmap -dump:live,format=b,file=heap.hprof <pid>

# Or configure the JVM to auto-dump right when it actually runs out of memory:
# -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/var/dumps/

# Lightweight, ongoing monitoring — no full heap dump needed —
# shows live object counts per class, cheap enough to run periodically:
jcmd <pid> GC.class_histogram | head -30
```

```java
// The classic ThreadLocal leak pattern in a pooled-thread environment:
private static final ThreadLocal<ExpensiveContext> CONTEXT = new ThreadLocal<>();

void handleRequest() {
    CONTEXT.set(new ExpensiveContext());
    // ... do work ...
    // MISSING: CONTEXT.remove();
    // On a thread pool, this thread gets reused for the NEXT unrelated request,
    // and the old ExpensiveContext just sits there, unreachable except through
    // the ThreadLocal itself — a genuinely sneaky leak because nothing about
    // this code looks wrong on casual read.
}

void handleRequestCorrectly() {
    try {
        CONTEXT.set(new ExpensiveContext());
        // ... do work ...
    } finally {
        CONTEXT.remove(); // always clean up, especially in pooled-thread code
    }
}
```

**Follow-up questions:**

- *"How would you catch this before it pages someone?"* — Continuous low-overhead JFR, or a scheduled `jcmd GC.class_histogram` comparison, gives a live trend line so growth is caught on a dashboard, not via an OOM crash.
- *"What's the single most common real cause?"* — An unbounded cache with no eviction policy, ahead of listener leaks, `ThreadLocal` leaks, and stale static collections.

**Sources:** [`jcmd` documentation](https://docs.oracle.com/en/java/javase/21/docs/specs/man/jcmd.html), [`java` launcher options, incl. `HeapDumpOnOutOfMemoryError`](https://docs.oracle.com/en/java/javase/21/docs/specs/man/java.html)

---

## 11. How Would You Build an LRU Cache Using `LinkedHashMap`?

**Core answer:**

"`LinkedHashMap` is a `HashMap` that also threads every entry through a doubly-linked list, so iteration order is predictable instead of the hash-bucket chaos you get from plain `HashMap`. By default that order is insertion order, but there's a constructor flag — `accessOrder = true` — that switches it to *access* order instead: every `get()` (and every `put()` on an existing key) moves that entry to the end of the list as 'most recently used.'

Once you have access-order tracking, an LRU cache is almost free: the least-recently-used entry is always sitting right at the front of the iteration order, which is exactly what `removeEldestEntry()` is a hook for. Override it to return `true` once the map exceeds your capacity, and `LinkedHashMap` evicts the oldest entry for you on the very next `put()` — no manual bookkeeping, no separate linked list to maintain yourself."

**Staff-level extension:**

This is a fine single-threaded or low-contention LRU implementation, but it is not thread-safe out of the box — every `get()` mutates the internal linked list (even reads are writes here, structurally), so concurrent access needs external synchronization, e.g. wrapping the whole thing and synchronizing `get`/`put` together, which reintroduces the single-lock bottleneck from question 3. For a genuinely concurrent LRU at scale, I'd point at `Caffeine` (or Guava's `CacheBuilder` before it) — it implements approximate LRU/LFU eviction (via a Window TinyLFU policy in Caffeine's case) with striped, low-contention internals rather than one global lock, which is what production caching layers actually reach for instead of hand-rolling `LinkedHashMap`.

**Example:**

```java
class LRUCache<K, V> extends LinkedHashMap<K, V> {
    private final int capacity;

    LRUCache(int capacity) {
        // initialCapacity, loadFactor, accessOrder=true — the last flag is the whole trick
        super(16, 0.75f, true);
        this.capacity = capacity;
    }

    @Override
    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        return size() > capacity; // called automatically after every put()
    }
}

LRUCache<Integer, String> cache = new LRUCache<>(3);
cache.put(1, "a");
cache.put(2, "b");
cache.put(3, "c");
cache.get(1);           // touching 1 marks it most-recently-used
cache.put(4, "d");       // capacity exceeded — evicts 2, the true LRU entry, not 1
System.out.println(cache.keySet()); // [3, 1, 4]
```

**Follow-up questions:**

- *"Is this LRU cache thread-safe?"* — No — every `get()` mutates the internal linked list, so concurrent access needs external synchronization, which reintroduces a single-lock bottleneck (Q3).
- *"What would you actually reach for in production?"* — Caffeine (or Guava's `CacheBuilder` before it) — striped, low-contention internals via a Window TinyLFU policy, rather than hand-rolling `LinkedHashMap`.

**Sources:** [`LinkedHashMap` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/LinkedHashMap.html) — see `removeEldestEntry` and the access-order constructor.

---

## 12. `TreeMap`/`TreeSet` — How Does Ordering Work, and What Breaks If `compareTo` Is Inconsistent With `equals`?

**Core answer:**

"`TreeMap` and `TreeSet` keep their entries sorted at all times, backed by a red-black tree — so `get`, `put`, `contains`, and `remove` are all O(log n), not O(1) like a hash-based map, in exchange for always-sorted iteration and range operations like `headMap`, `tailMap`, `ceilingKey`, and `floorKey` that a `HashMap` simply can't offer.

The critical thing is that a `TreeMap` never calls `equals()` or `hashCode()` at all — it determines whether two keys are 'the same' purely through `compareTo()` (or a supplied `Comparator`) returning zero. Most of the time that lines up with `equals()` returning `true` for the same pair, but if you write a `compareTo()` that isn't consistent with `equals()`, the map silently violates the general `Map` contract: two keys that `equals()` says are different objects get treated as the same slot, and only one is ever retrievable. Nothing throws — it just silently behaves differently than a `HashMap` would for the same objects."

**Staff-level extension:**

The Javadoc is explicit about this exact subtlety: *"the ordering maintained by a sorted set (or map) must be consistent with equals if it is to correctly implement the Set (or Map) interface"* — and it goes further, noting a sorted set can technically be used *without* that consistency, but every operation elsewhere that relies on `equals()` (like passing the set to another collection's `addAll`) will misbehave. `NavigableMap`/`NavigableSet` (the interfaces `TreeMap`/`TreeSet` implement) are the real reason to reach for a tree structure at all — `floorEntry`, `ceilingEntry`, `subMap` come up constantly in scheduling, range-query, and interval-overlap problems where a hash-based structure genuinely can't help.

**Example:**

```java
class Employee implements Comparable<Employee> {
    String name;
    double salary;
    Employee(String name, double salary) { this.name = name; this.salary = salary; }

    // Sorted by salary only — but equals() (inherited from Object) is identity-based
    @Override
    public int compareTo(Employee other) {
        return Double.compare(this.salary, other.salary);
    }
}

Set<Employee> byName = new TreeSet<>(); // ordering, not equals(), decides membership
byName.add(new Employee("Alice", 90_000));
byName.add(new Employee("Bob", 90_000)); // same salary as Alice — compareTo() returns 0

System.out.println(byName.size()); // 1 — Bob was silently treated as a duplicate of Alice,
                                     // even though .equals() would say they're different people

// The fix: make compareTo() a genuine total order that agrees with equals(),
// e.g. break ties on a unique field:
@Override
public int compareTo(Employee other) {
    int bySalary = Double.compare(this.salary, other.salary);
    return bySalary != 0 ? bySalary : this.name.compareTo(other.name);
}
```

**Follow-up questions:**

- *"Does an inconsistent `compareTo()` throw an exception?"* — No — nothing throws, it just silently drops what `equals()` would consider distinct entries.
- *"What's the actual reason to reach for a tree over a hash-based map?"* — `NavigableMap`/`NavigableSet` operations — `floorEntry`, `ceilingEntry`, `subMap` — for scheduling, range-query, and interval-overlap problems.

**Sources:** [`TreeMap` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/TreeMap.html), [`Comparable` Javadoc — consistency with equals](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Comparable.html)

---

## 13. What Is `WeakHashMap`, and When Would You Actually Reach for It?

**Core answer:**

"A normal `HashMap` holds a strong reference to every key, which means a key can never be garbage collected as long as it's sitting in the map — even if nothing else in the program references it anymore. `WeakHashMap` holds its keys through `WeakReference`s instead, so once a key becomes otherwise unreachable, the garbage collector is free to reclaim it, and `WeakHashMap` will lazily clear out that now-dead entry itself, typically the next time you touch the map.

The practical use case is a cache keyed by an object's *identity/lifecycle*, where you want the cache entry to disappear automatically the moment nothing else cares about that key anymore — metadata tied to a class, listener bookkeeping tied to some external object — without explicitly removing entries yourself and risking the same kind of leak from question 10."

**Staff-level extension:**

Two things trip people up in practice. First: it's only the *keys* that are weakly referenced — the values are held strongly, so if a value indirectly holds a strong reference back to its own key (a common accident with inner classes or listener objects capturing an outer `this`), the key never actually becomes unreachable and you get no cleanup at all, silently defeating the whole point. Second: entry removal happens lazily, tied to GC activity and to when you next interact with the map — it's explicitly not deterministic or immediate, so `WeakHashMap` is the wrong tool if you need predictable eviction timing (that's a job for size- or time-based eviction in something like Caffeine, not automatic GC-driven cleanup). It's worth contrasting with `WeakReference`/`SoftReference` used directly in a manual cache, and with `ThreadLocal`'s own internal use of weak references for its keys — the same underlying idea applied to a different leak.

**Example:**

```java
Map<Object, String> cache = new WeakHashMap<>();

Object key = new Object();
cache.put(key, "metadata for this object");
System.out.println(cache.size()); // 1

key = null;         // no other strong reference to the original key exists anymore
System.gc();        // in real code you'd never force this — for demonstration only

// After a GC cycle, the entry may already be gone — not guaranteed to be immediate,
// but the point is: nobody had to call cache.remove() for it to happen.
System.out.println(cache.size()); // likely 0, though timing depends on the GC
```

**Follow-up questions:**

- *"Are values also weakly referenced?"* — No, only keys — a value that indirectly holds a strong reference back to its own key defeats the cleanup entirely.
- *"Can you rely on immediate eviction?"* — No — removal is lazy, tied to GC activity; use Caffeine-style size/time eviction if predictable timing matters.

**Sources:** [`WeakHashMap` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/WeakHashMap.html), [`java.lang.ref.WeakReference` Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/ref/WeakReference.html)

---

## 14. `Arrays.asList()`, `List.of()`, and `Collections.unmodifiableList()` — What Are the Actual Mutability Differences?

**Core answer:**

"These three get lumped together as 'ways to make a list' but they have genuinely different mutability semantics, and mixing them up is a real production bug source, not just trivia.

`Arrays.asList()` returns a fixed-size list backed *directly* by the array you passed in — `set()` works and writes through to the underlying array, but `add()` and `remove()` throw `UnsupportedOperationException` because the list can't resize an array. The 'backed by the array' part is the sharp edge: mutating the list through `set()` mutates the original array too, and vice versa.

`List.of()` (Java 9+) is genuinely, fully immutable — `set()`, `add()`, and `remove()` all throw. It also rejects `null` elements outright at construction time, which `Arrays.asList()` does not.

`Collections.unmodifiableList()` wraps an existing list in a read-only *view* — you can't mutate through the wrapper, but if you keep a reference to the original underlying list and mutate that directly, the 'immutable' view changes right along with it, because it's not a copy, just a facade."

**Staff-level extension:**

This is an API-design lesson worth internalizing: if you're handing a collection out of a method as something the caller shouldn't mutate, `Collections.unmodifiableList()` around a mutable list you still hold onto is a leaky abstraction — the caller can't mutate it directly, but you can still change it out from under them, which is confusing for anyone reading only the caller's code. `List.of()` (or `List.copyOf()` if you need to defensively snapshot an incoming list) gives a much stronger, harder-to-misuse guarantee. `List.copyOf()` specifically is the right tool when you're handed a mutable list from a caller and want a genuinely independent, immutable snapshot rather than another view over their list.

**Example:**

```java
// Arrays.asList: fixed-size, but writes through to the backing array
Integer[] arr = {1, 2, 3};
List<Integer> backed = Arrays.asList(arr);
backed.set(0, 99);
System.out.println(arr[0]); // 99 — the "list" and the array are the same memory
backed.add(4); // throws UnsupportedOperationException — can't resize an array

// List.of: truly immutable, and rejects null up front
List<Integer> immutable = List.of(1, 2, 3);
immutable.set(0, 99); // throws UnsupportedOperationException
// List.of(1, null, 3); // throws NullPointerException immediately at creation

// Collections.unmodifiableList: a view, not a copy — the underlying list can still change
List<Integer> mutable = new ArrayList<>(List.of(1, 2, 3));
List<Integer> view = Collections.unmodifiableList(mutable);
mutable.add(4);
System.out.println(view); // [1, 2, 3, 4] — the "unmodifiable" view just showed a new element
```

**Follow-up questions:**

- *"What's the leaky-abstraction risk with `unmodifiableList()`?"* — The wrapper blocks the caller, but you still hold the original mutable list and can change it out from under them — confusing for anyone reading only the caller's code.
- *"How do you get a genuinely independent, immutable snapshot of a caller's list?"* — `List.copyOf()` — a real copy, not another view.

**Sources:** [`Arrays#asList` Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Arrays.html#asList(T...)), [`List#of` Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/List.html#of()), [`Collections#unmodifiableList` Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Collections.html#unmodifiableList(java.util.List))

---

## 15. How Does `PriorityQueue` Work Internally, and What Are Its Complexity Trade-Offs?

**Core answer:**

"`PriorityQueue` is a binary heap stored in a plain array — not a linked structure, no per-node object overhead. It maintains the heap property: every parent is less-than-or-equal to (for a min-heap, the default) both its children, according to natural ordering or a supplied `Comparator`. That property guarantees the smallest element is always at index 0, so `peek()` is O(1).

`offer()`/`add()` puts the new element at the end of the array and 'sifts it up' — swapping with its parent repeatedly while it's smaller than that parent — which is O(log n). `poll()` removes the root, moves the *last* element into its place, and 'sifts it down' into the correct position, also O(log n). What it's explicitly not good for: it only guarantees the *root* is the minimum — the rest of the array is not fully sorted, so full ordering requires draining it with repeated `poll()` calls, not iterating the backing array directly."

**Staff-level extension:**

`PriorityQueue` is unbounded and grows dynamically like `ArrayList`, but it's explicitly *not* thread-safe — for a concurrent producer/consumer priority queue, the answer is `PriorityBlockingQueue`, which wraps the same heap logic with locking and blocking semantics for `take()`/`put()`. `remove(Object)` is a trap worth flagging: removing an arbitrary (non-root) element is O(n), not O(log n), because the heap has no efficient way to locate an arbitrary value — only the root is known in O(1). That asymmetry matters for problems like "top-K streaming" or Dijkstra's algorithm with decrease-key semantics, where naive implementations that repeatedly remove-and-reinsert arbitrary entries can quietly degrade a solution from O(n log n) to O(n²) without the interviewee noticing.

**Example:**

```java
// Min-heap by default — smallest offered is always polled first
PriorityQueue<Integer> minHeap = new PriorityQueue<>();
minHeap.offer(5);
minHeap.offer(1);
minHeap.offer(3);
System.out.println(minHeap.poll()); // 1
System.out.println(minHeap.poll()); // 3

// Max-heap: supply a reversed comparator — there's no separate "MaxPriorityQueue" type
PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Comparator.reverseOrder());
maxHeap.offer(5);
maxHeap.offer(1);
maxHeap.offer(3);
System.out.println(maxHeap.poll()); // 5

// The classic gotcha: iteration order is NOT sorted order
PriorityQueue<Integer> pq = new PriorityQueue<>(List.of(5, 1, 3, 2, 4));
System.out.println(pq); // some heap-internal array order, NOT [1, 2, 3, 4, 5]
// To get sorted output, you must drain it:
List<Integer> sorted = new ArrayList<>();
while (!pq.isEmpty()) sorted.add(pq.poll());
System.out.println(sorted); // [1, 2, 3, 4, 5] — correct, via repeated poll()
```

**Follow-up questions:**

- *"Is `PriorityQueue` thread-safe?"* — No — for a concurrent producer/consumer priority queue, use `PriorityBlockingQueue` instead.
- *"What's the cost of removing an arbitrary element?"* — O(n), not O(log n) — only the root is known in O(1); naive repeated remove-and-reinsert can quietly degrade an algorithm from O(n log n) to O(n²).

**Sources:** [`PriorityQueue` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/PriorityQueue.html), [`PriorityBlockingQueue` Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/PriorityBlockingQueue.html)

---

## Sources & Further Reading — Consolidated

| Topic | Link |
|---|---|
| `HashMap` (JDK 21 Javadoc) | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashMap.html |
| `ConcurrentHashMap` (JDK 21 Javadoc) | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html |
| `CopyOnWriteArrayList` (JDK 21 Javadoc) | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/CopyOnWriteArrayList.html |
| `ArrayDeque` (JDK 21 Javadoc) | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayDeque.html |
| `ArrayList` (JDK 21 Javadoc, fail-fast iterator notes) | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayList.html |
| `Object.hashCode()` contract | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Object.html#hashCode() |
| `Map` interface overview | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Map.html |
| JLS §5.1.7 — Boxing Conversion (Integer cache rule) | https://docs.oracle.com/javase/specs/jls/se21/html/jls-5.html |
| `jcmd` diagnostic tool | https://docs.oracle.com/en/java/javase/21/docs/specs/man/jcmd.html |
| `java` launcher options (incl. `HeapDumpOnOutOfMemoryError`) | https://docs.oracle.com/en/java/javase/21/docs/specs/man/java.html |
| `LinkedHashMap` (JDK 21 Javadoc, incl. `removeEldestEntry`) | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/LinkedHashMap.html |
| `TreeMap` (JDK 21 Javadoc) | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/TreeMap.html |
| `Comparable` Javadoc (consistency with equals) | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Comparable.html |
| `WeakHashMap` (JDK 21 Javadoc) | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/WeakHashMap.html |
| `java.lang.ref.WeakReference` Javadoc | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/ref/WeakReference.html |
| `Arrays#asList` Javadoc | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Arrays.html#asList(T...) |
| `List#of` Javadoc | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/List.html#of() |
| `Collections#unmodifiableList` Javadoc | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Collections.html#unmodifiableList(java.util.List) |
| `PriorityQueue` (JDK 21 Javadoc) | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/PriorityQueue.html |
| `PriorityBlockingQueue` (JDK 21 Javadoc) | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/PriorityBlockingQueue.html |
