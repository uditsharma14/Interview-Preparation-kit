# Java Collections — Interview Prep, Basic to Staff Level (with Code & Sources)

> **Target level:** Basic → Staff (graduated — see below) · **Baseline:** Java/JDK 21 (LTS) · **Last verified:** 2026-08-23 · **Prerequisites:** core Java syntax and generics for the Basic section; `equals()`/`hashCode()` basics helpful from the Intermediate section onward

How to use this: each question has a **core answer** (100–180 words — roughly what you'd actually say out loud in 40–70 seconds), a **staff-level extension** with the deeper trade-offs pushed out of the core response rather than dropped, a **code example** you could sketch on a whiteboard or IDE, **follow-up questions** an interviewer is likely to probe with next, and **sources**. Questions are grouped by level (Basic → Intermediate → Staff) so you can calibrate depth to the interview you're prepping for; the later sections assume the earlier ones as background and don't re-explain them.

<!-- toc -->
## Table of Contents

- [Basic](#basic)
  - [1. What Is the Java Collections Framework, and What Are Its Core Interfaces?](#1-what-is-the-java-collections-framework-and-what-are-its-core-interfaces)
  - [2. `List` vs. `Set` vs. `Map` — What's the Core Difference?](#2-list-vs-set-vs-map--whats-the-core-difference)
  - [3. What Is the `equals()`/`hashCode()` Contract, and Why Does It Matter for Collections?](#3-what-is-the-equalshashcode-contract-and-why-does-it-matter-for-collections)
  - [4. `HashSet` vs. `LinkedHashSet` vs. `TreeSet` — What's the Difference?](#4-hashset-vs-linkedhashset-vs-treeset--whats-the-difference)
  - [5. What Is an `Iterator`, and How Do You Remove Elements Safely While Iterating?](#5-what-is-an-iterator-and-how-do-you-remove-elements-safely-while-iterating)
  - [6. How Do You Iterate Over a `Map`'s Entries?](#6-how-do-you-iterate-over-a-maps-entries)
  - [7. `Comparable` vs. `Comparator` — What's the Difference?](#7-comparable-vs-comparator--whats-the-difference)
- [Intermediate](#intermediate)
  - [8. `ArrayList` vs. `LinkedList` — the Basic Trade-Off](#8-arraylist-vs-linkedlist--the-basic-trade-off)
  - [9. `Iterator` vs. `ListIterator` — What's the Difference?](#9-iterator-vs-listiterator--whats-the-difference)
  - [10. `Queue` vs. `Deque` — What's the Difference, and When Would You Use Each?](#10-queue-vs-deque--whats-the-difference-and-when-would-you-use-each)
  - [11. How Do You Choose Between `HashMap`, `LinkedHashMap`, and `TreeMap`?](#11-how-do-you-choose-between-hashmap-linkedhashmap-and-treemap)
  - [12. `Collection` vs. `Collections` — What's the Difference?](#12-collection-vs-collections--whats-the-difference)
- [Staff Level](#staff-level)
  - [13. How Does `HashMap` Work Internally — Collisions, Resizing, Treeification, Equality?](#13-how-does-hashmap-work-internally--collisions-resizing-treeification-equality)
  - [14. What Can Go Wrong If a Mutable Object Is Used as a `HashMap` Key?](#14-what-can-go-wrong-if-a-mutable-object-is-used-as-a-hashmap-key)
  - [15. When Would You Use `ConcurrentHashMap` Instead of a Synchronized Map?](#15-when-would-you-use-concurrenthashmap-instead-of-a-synchronized-map)
  - [16. Are Compound Operations on `ConcurrentHashMap` Thread-Safe? `get`-then-`put` vs. `computeIfAbsent`](#16-are-compound-operations-on-concurrenthashmap-thread-safe-get-then-put-vs-computeifabsent)
  - [17. How Would You Design an In-Memory Structure Supporting High Write Concurrency and Snapshot Reads?](#17-how-would-you-design-an-in-memory-structure-supporting-high-write-concurrency-and-snapshot-reads)
  - [18. Compare `ArrayList`, `LinkedList`, `ArrayDeque`, and `CopyOnWriteArrayList`](#18-compare-arraylist-linkedlist-arraydeque-and-copyonwritearraylist)
  - [19. When Is `CopyOnWriteArrayList` a Good Choice, and When Is It Disastrous?](#19-when-is-copyonwritearraylist-a-good-choice-and-when-is-it-disastrous)
  - [20. How Do Weakly Consistent Iterators Differ From Fail-Fast Iterators?](#20-how-do-weakly-consistent-iterators-differ-from-fail-fast-iterators)
  - [21. What Are the Memory and Performance Costs of Boxed Collections?](#21-what-are-the-memory-and-performance-costs-of-boxed-collections)
  - [22. How Would You Diagnose a Collection That Continuously Grows in Production?](#22-how-would-you-diagnose-a-collection-that-continuously-grows-in-production)
  - [23. How Would You Build an LRU Cache Using `LinkedHashMap`?](#23-how-would-you-build-an-lru-cache-using-linkedhashmap)
  - [24. `TreeMap`/`TreeSet` — How Does Ordering Work, and What Breaks If `compareTo` Is Inconsistent With `equals`?](#24-treemaptreeset--how-does-ordering-work-and-what-breaks-if-compareto-is-inconsistent-with-equals)
  - [25. What Is `WeakHashMap`, and When Would You Actually Reach for It?](#25-what-is-weakhashmap-and-when-would-you-actually-reach-for-it)
  - [26. `Arrays.asList()`, `List.of()`, and `Collections.unmodifiableList()` — What Are the Actual Mutability Differences?](#26-arraysaslist-listof-and-collectionsunmodifiablelist--what-are-the-actual-mutability-differences)
  - [27. How Does `PriorityQueue` Work Internally, and What Are Its Complexity Trade-Offs?](#27-how-does-priorityqueue-work-internally-and-what-are-its-complexity-trade-offs)
- [Sources & Further Reading — Consolidated](#sources--further-reading--consolidated)

<!-- /toc -->

---

## Basic

### 1. What Is the Java Collections Framework, and What Are Its Core Interfaces?

**Core answer:**

"The Java Collections Framework is the standard library's unified set of interfaces and implementations for storing and manipulating groups of objects — before it existed, every library had its own incompatible ad hoc container types. The core interfaces form a hierarchy: `Collection` is the root, extended by `List` (ordered, allows duplicates, indexed access — `ArrayList`, `LinkedList`), `Set` (no duplicates, membership-focused — `HashSet`, `TreeSet`, `LinkedHashSet`), and `Queue`/`Deque` (ordered for processing, head/tail access — `ArrayDeque`, `PriorityQueue`). `Map` is a genuinely separate hierarchy — not a `Collection` at all, since it stores key-value pairs rather than single elements, though `keySet()`, `values()`, and `entrySet()` each return a `Collection` view over it.

Every concrete class implements one of these interfaces, which is why code should almost always be written against the interface (`List<String> list = new ArrayList<>();`), not the concrete type — it keeps the implementation swappable without touching every call site."

**Staff-level extension:**

This interface-over-implementation discipline pays off the first time a performance problem forces a swap — discovering `ArrayList`'s O(n) middle-insertion cost is a bottleneck and switching from one `List` implementation to another (`ArrayList` to `LinkedList`, say) is a one-line change if the rest of the code only ever referenced `List`, and a much bigger refactor if it referenced `ArrayList` directly everywhere. Switching to `ArrayDeque` for queue-like access is a different case worth being precise about: `ArrayDeque` doesn't implement `List` at all — it implements `Deque`/`Queue` — so that swap is only a one-line change if the call sites were already typed as `Queue`/`Deque`; a `List`-typed call site using indexed access (`get(i)`, `set(i, v)`) has no equivalent on `ArrayDeque` and needs real code changes, not just a new `List` implementation. The same reasoning applies to testing: substituting a different in-memory implementation is trivial against an interface, awkward against a concrete class.

**Example:**

```java
// Program to the interface, not the implementation
List<String> names = new ArrayList<>();       // could swap implementations later, no call-site changes
Set<String> uniqueIds = new HashSet<>();       // no duplicates, no guaranteed order
Map<String, Integer> scores = new HashMap<>(); // key-value pairs — NOT a Collection itself

// Map's "collection views" — live windows onto the same underlying data
for (Map.Entry<String, Integer> entry : scores.entrySet()) {
    System.out.println(entry.getKey() + " -> " + entry.getValue());
}
```

**Follow-up questions:**

- *"Why isn't `Map` a `Collection`?"* — It stores key-value pairs, not single elements — a fundamentally different shape, though its `keySet()`/`values()`/`entrySet()` views are each a `Collection`.
- *"What's the practical cost of programming to the concrete type instead of the interface?"* — Every later implementation swap becomes a multi-call-site refactor instead of a one-line change.

**Sources:** [Collections Framework Overview, Oracle Java Tutorials](https://docs.oracle.com/javase/tutorial/collections/intro/index.html), [`Collection` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Collection.html), [`ArrayDeque` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayDeque.html) (confirms `ArrayDeque`'s implemented interfaces don't include `List`)

---

### 2. `List` vs. `Set` vs. `Map` — What's the Core Difference?

**Core answer:**

"`List` is an ordered collection that allows duplicates and gives indexed access — you can ask for 'the element at position 3,' and the same value can appear multiple times. `Set` is the mathematical-set abstraction: no duplicates — adding an element already present is a no-op — though how 'already present' gets decided depends on the implementation: `HashSet`/`LinkedHashSet` decide it via `equals()`/`hashCode()`, while `TreeSet` instead decides it via natural ordering or a supplied `Comparator`, treating two elements as the same whenever `compareTo()` (or `compare()`) returns zero, independent of `equals()`. Most implementations don't guarantee any particular iteration order (`HashSet`), though `LinkedHashSet` preserves insertion order and `TreeSet` keeps everything sorted. `Map` associates unique keys with values — a lookup structure, not a sequence: you retrieve by key, not by position.

The practical decision is about the *access pattern* the code actually needs: reaching for a `List` when the real requirement is 'no duplicates, fast membership check' means writing manual duplicate-checking code a `Set` already gives for free; using parallel `List`s of keys and values when the requirement is 'look this up by identifier' means writing manual linear search a `HashMap` already solves in expected average O(1) — that's an average-case, hash-based guarantee specific to `HashMap`/`HashSet`, not something every `Map`/`Set` implementation gives; `TreeMap`, for instance, is O(log n) per operation, covered later in this guide."

**Staff-level extension:**

The "wrong container for the access pattern" mistake shows up constantly in real code review: a `List<User>` searched linearly by `id` on every request is a `Map<Long, User>` nobody built, and it's an O(n) cost hiding in what looks like simple code. The fix is almost always mechanical once spotted — the deeper skill is recognizing the pattern (repeated linear scans keyed by some field) as a container-choice smell in the first place, not a performance problem to solve later.

**Example:**

```java
List<String> tags = new ArrayList<>(List.of("java", "java", "spring")); // duplicates allowed
Set<String> uniqueTags = new HashSet<>(tags);                           // duplicates collapsed
Map<String, Integer> tagCounts = new HashMap<>();                       // lookup by key, not position
tagCounts.merge("java", 1, Integer::sum);
```

**Follow-up questions:**

- *"Does `Set` guarantee any iteration order?"* — No — `HashSet` doesn't; `LinkedHashSet` preserves insertion order; `TreeSet` keeps sorted order.
- *"What's the tell that a `List` should actually be a `Map`?"* — Any code doing a linear scan/search over a `List` keyed by some field — that's an O(n) lookup a `HashMap` makes expected average O(1).

**Sources:** [`List`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/List.html), [`Set`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Set.html), [`Map`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Map.html), [`HashMap`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashMap.html) Javadoc, JDK 21, [`TreeSet` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/TreeSet.html) ("a `TreeSet` instance performs all element comparisons using its `compareTo` (or `compare`) method")

---

### 3. What Is the `equals()`/`hashCode()` Contract, and Why Does It Matter for Collections?

**Core answer:**

"The contract, from `Object`'s Javadoc: if two objects are equal according to `equals()`, they **must** return the same `hashCode()`; the reverse isn't required — two unequal objects can share a hash code, which is a collision, not a bug. Every hash-based collection (`HashMap`, `HashSet`) relies on this contract structurally: it uses `hashCode()` to pick a bucket and `equals()` to confirm an exact match within that bucket.

If you override `equals()` but forget `hashCode()` (or vice versa), the default `Object` identity-based `hashCode()` is still in effect, which almost certainly disagrees with your custom `equals()` — two objects your code considers equal can land in different buckets, so a `HashSet` silently accepts both as 'distinct,' and `map.get(key)` fails to find an entry that a logically-equal key was used to insert, because the lookup hash doesn't match the bucket the entry actually lives in."

**Staff-level extension:**

This is exactly why IDEs and `record` types generate `equals()` and `hashCode()` together, never one without the other — it's protecting against a contract violation that produces genuinely confusing bugs. The other half of the contract worth knowing: `hashCode()` must be *consistent* — calling it multiple times on the same object, with no mutation of the equals-relevant fields in between, must return the same value every time, exactly the property broken by the mutable-key `HashMap` bug covered later in this guide.

**Example:**

```java
class Point {
    int x, y;
    Point(int x, int y) { this.x = x; this.y = y; }

    @Override
    public boolean equals(Object o) {
        return o instanceof Point p && p.x == x && p.y == y;
    }
    // BUG: no hashCode() override — inherits Object's identity-based hash
}

Set<Point> points = new HashSet<>();
points.add(new Point(1, 2));
System.out.println(points.contains(new Point(1, 2))); // false, without hashCode() override —
                                                          // despite equals() saying they're equal!
```

**Follow-up questions:**

- *"If two objects have the same `hashCode()`, are they necessarily equal?"* — No — that direction isn't required by the contract; a shared hash code is just a collision, resolved by `equals()`.
- *"What's the practical symptom of overriding `equals()` without `hashCode()`?"* — `contains()`/`get()` silently return false/null for an object `equals()` says should match — the hash-based lookup goes to the wrong bucket.

**Sources:** [`Object#hashCode()` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Object.html#hashCode())

---

### 4. `HashSet` vs. `LinkedHashSet` vs. `TreeSet` — What's the Difference?

**Core answer:**

"All three implement `Set` — no duplicates — but differ in how a duplicate is decided, ordering, and performance. `HashSet` is backed by a `HashMap` internally, decides duplicates via `hashCode()`/`equals()`, gives expected average O(1) add/remove/contains, and makes zero ordering guarantee — iteration order can look arbitrary and can change across JDK versions or resizes. `LinkedHashSet` extends `HashSet`, so it decides duplicates the same `hashCode()`/`equals()` way, but additionally threads every entry through a doubly-linked list (the same mechanism `LinkedHashMap` uses), so iteration order is predictable — insertion order — at a small memory and performance cost over plain `HashSet`. `TreeSet` is different in kind, not just performance: it's backed by a red-black tree (the same structure `TreeMap` uses), decides duplicates via natural ordering or a supplied `Comparator` — two elements are the same whenever `compareTo()`/`compare()` returns zero, regardless of what `equals()` would say — keeps elements sorted at all times, and pays O(log n) for add/remove/contains instead of `HashSet`'s average O(1), in exchange for that ordering and range operations (`headSet`, `tailSet`, `ceiling`, `floor`) the other two can't offer at all."

**Staff-level extension:**

The decision is almost entirely about what the *iteration order* actually needs to be, since correctness is identical across all three. Default to `HashSet` unless something specifically needs order — reaching for `LinkedHashSet` or `TreeSet` "just in case" pays a real, permanent cost for an ordering guarantee the code never uses. `TreeSet` requires elements to be mutually comparable, and if `compareTo()`/`equals()` are inconsistent, it silently drops what `equals()` would consider distinct elements — exactly the pitfall the `TreeMap` question later in this guide covers in depth.

**Example:**

```java
Set<String> hashSet = new HashSet<>(List.of("banana", "apple", "cherry"));
Set<String> linkedHashSet = new LinkedHashSet<>(List.of("banana", "apple", "cherry"));
Set<String> treeSet = new TreeSet<>(List.of("banana", "apple", "cherry"));

System.out.println(hashSet);       // arbitrary-looking order, e.g. [banana, cherry, apple]
System.out.println(linkedHashSet); // insertion order: [banana, apple, cherry]
System.out.println(treeSet);       // sorted order: [apple, banana, cherry]
```

**Follow-up questions:**

- *"Which is fastest for a simple 'have I seen this before' check?"* — `HashSet` — O(1) average, and the default unless ordering is actually needed.
- *"What does `TreeSet` require of its elements?"* — Mutual comparability, via `Comparable` or a supplied `Comparator` — otherwise `add()` throws `ClassCastException` at runtime.

**Sources:** [`HashSet`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashSet.html), [`LinkedHashSet`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/LinkedHashSet.html), [`TreeSet`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/TreeSet.html) Javadoc, JDK 21

---

### 5. What Is an `Iterator`, and How Do You Remove Elements Safely While Iterating?

**Core answer:**

"`Iterator` is the standard interface for walking through a collection one element at a time without exposing its internal structure — `hasNext()` checks if there's another element, `next()` returns it and advances, and `remove()` removes the *last element returned by `next()`* from the underlying collection. It's the only safe way to remove elements from most collections while iterating: calling `list.remove(item)` directly inside a for-each loop over that same list throws `ConcurrentModificationException`, because the enhanced for-loop uses an `Iterator` internally, and structurally modifying the collection through any path other than that same iterator's own `remove()` invalidates it.

Going through `iterator.remove()` instead works because the iterator updates its own internal bookkeeping as part of the removal, so it never gets out of sync with the collection it's walking."

**Staff-level extension:**

The alternative that avoids the whole issue: collect the items to remove into a separate list during iteration, then call `removeAll()` — or the collection's own `removeIf()`, added in Java 8, which does exactly this internally and is usually the cleanest option — after the loop finishes. That's useful when the removal decision needs information gathered across multiple elements, not just the current one, where a single-pass `iterator.remove()` isn't expressive enough.

**Example:**

```java
List<Integer> numbers = new ArrayList<>(List.of(1, 2, 3, 4, 5));

// WRONG — throws ConcurrentModificationException
for (Integer n : numbers) {
    if (n % 2 == 0) numbers.remove(n); // modifying the list mid-iteration, NOT via the iterator
}

// RIGHT — via the iterator's own remove()
Iterator<Integer> it = numbers.iterator();
while (it.hasNext()) {
    if (it.next() % 2 == 0) it.remove(); // safe — the iterator stays in sync with itself
}

// RIGHT — Java 8+, cleanest for a simple predicate
numbers.removeIf(n -> n % 2 == 0);
```

**Follow-up questions:**

- *"Why does `for (Integer n : numbers) numbers.remove(n)` throw?"* — The enhanced for-loop uses an `Iterator` internally, and modifying the list through any other path invalidates it — `ConcurrentModificationException` is the iterator's own detection of that.
- *"What's the simplest fix for a straightforward predicate-based removal?"* — `Collection#removeIf()`, added in Java 8 — it does the safe iterate-and-remove internally.

**Sources:** [`Iterator` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Iterator.html), [`Collection#removeIf` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Collection.html#removeIf(java.util.function.Predicate))

---

### 6. How Do You Iterate Over a `Map`'s Entries?

**Core answer:**

"Three main ways, in order of how commonly they're actually the right choice. `entrySet()` iteration is the standard, most efficient approach when you need both key and value — it returns a `Set<Map.Entry<K,V>>` view over the map, giving you both in a single pass with no repeated lookups. `keySet()` iteration, followed by `map.get(key)` inside the loop, is a common but strictly worse pattern when you need the value too — it does a second hash lookup per entry that `entrySet()` avoids entirely, since the entry set already carries the value alongside the key. `forEach((key, value) -> ...)`, added in Java 8, is the most concise for a simple per-entry action, and is functionally equivalent to iterating `entrySet()` under the hood."

**Staff-level extension:**

The `keySet()` + `get()` anti-pattern is worth calling out explicitly because it's genuinely common in code that started as "just iterate the keys" and later grew a need for the value too, without anyone going back to switch to `entrySet()` — on a small map the extra lookups are invisible, but on a hot path over a large map, doubling the number of hash computations and bucket walks is a real, measurable, and completely avoidable cost.

**Example:**

```java
Map<String, Integer> scores = Map.of("alice", 90, "bob", 85);

// BEST for key+value: entrySet() — one pass, no extra lookups
for (Map.Entry<String, Integer> entry : scores.entrySet()) {
    System.out.println(entry.getKey() + " -> " + entry.getValue());
}

// WORSE: keySet() + get() — a redundant second lookup per entry
for (String key : scores.keySet()) {
    System.out.println(key + " -> " + scores.get(key)); // extra hash lookup, avoidable
}

// CONCISE: forEach, Java 8+
scores.forEach((key, value) -> System.out.println(key + " -> " + value));
```

**Follow-up questions:**

- *"When is `keySet()` iteration actually fine?"* — When you genuinely only need the keys, not the values — no redundant lookup happens in that case.
- *"Is `forEach` faster than `entrySet()` iteration?"* — No — it's implemented via `entrySet()` internally in the standard `Map` implementations; it's a conciseness win, not a performance one.

**Sources:** [`Map#entrySet`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Map.html#entrySet()), [`Map#forEach`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Map.html#forEach(java.util.function.BiConsumer)) Javadoc, JDK 21

---

### 7. `Comparable` vs. `Comparator` — What's the Difference?

**Core answer:**

"`Comparable<T>` is implemented *by the class itself* — it defines a single 'natural ordering' via `compareTo()`, baked into the class, used by default whenever the class is sorted (`Collections.sort()`, `TreeSet`, `TreeMap`) without an explicit ordering supplied. `Comparator<T>` is a *separate* object that defines an ordering externally to the class, passed in wherever a specific order is needed — useful when a class has no single obvious natural order, when you don't own the class's source to add `Comparable` to it, or when you need multiple different orderings of the same type in different contexts.

A class can implement `Comparable` for its one natural default order and still be sorted by an entirely different `Comparator` whenever a specific call site needs something else."

**Staff-level extension:**

`Comparator` composition (Java 8+) is the practical reason `Comparator` usually wins over hand-writing a multi-field `compareTo()` for anything beyond a single field: `Comparator.comparing(Employee::getSalary).thenComparing(Employee::getName)` reads as a direct description of the sort priority, whereas the equivalent hand-written `compareTo()` is a chain of manual `if (result != 0) return result;` checks that's easy to get subtly wrong — especially the tie-breaking order — and harder to review at a glance.

**Example:**

```java
class Employee implements Comparable<Employee> {
    String name; double salary;
    Employee(String name, double salary) { this.name = name; this.salary = salary; }

    @Override // natural ordering: by name
    public int compareTo(Employee other) { return this.name.compareTo(other.name); }
}

List<Employee> employees = new ArrayList<>(/* ... */);
Collections.sort(employees); // uses compareTo() — sorts by name (the natural order)

// A DIFFERENT order, via Comparator, without touching the class at all:
employees.sort(Comparator.comparingDouble((Employee e) -> e.salary).reversed()
                          .thenComparing(e -> e.name));
```

**Follow-up questions:**

- *"Can a class be sorted by more than one field without multiple `Comparable` implementations?"* — Yes — implement `Comparable` for the one natural default, and pass a `Comparator` for any other ordering a specific call site needs.
- *"Why does `Comparator` composition tend to beat a hand-written multi-field `compareTo()`?"* — It reads as a direct priority list instead of a manual chain of `if` checks that's easy to get subtly wrong.

**Sources:** [`Comparable`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Comparable.html), [`Comparator`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Comparator.html) Javadoc, JDK 21

---

## Intermediate

### 8. `ArrayList` vs. `LinkedList` — the Basic Trade-Off

**Core answer:**

"`ArrayList` is backed by a resizable array: O(1) indexed access — `get(i)` jumps straight to the memory offset — but inserting or removing from the middle is O(n), since every following element has to shift. `LinkedList` is a doubly-linked list of individually allocated nodes: inserting or removing is O(1) *once you're already at the right node* via an iterator, but `get(i)` is O(n) — there's no direct indexing, so it has to walk from the head or tail, whichever is closer.

The naive takeaway — 'LinkedList for lots of insertions, ArrayList for lots of lookups' — is directionally right but incomplete: in practice, getting to the right position in a `LinkedList` in the first place is usually the dominant cost, and `ArrayList`'s contiguous memory layout gives it much better CPU cache behavior than `LinkedList`'s scattered nodes, which the fuller comparison later in this guide covers in real depth."

**Staff-level extension:**

This is deliberately the basic version — the Staff-level comparison later in this guide covers `ArrayDeque` and `CopyOnWriteArrayList` alongside these two, and specifically explains *why* `LinkedList`'s theoretical O(1) insertion advantage rarely wins in practice on modern hardware: cache-miss cost dominates for anything but very large N, a detail worth knowing at Staff level but not essential to get this basic comparison right first.

**Example:**

```java
List<Integer> arrayList = new ArrayList<>();
// get(500_000) is O(1) — direct array index
// add(0, x) — inserting at the front — is O(n), shifts every element right

List<Integer> linkedList = new LinkedList<>();
// get(500_000) is O(n) — must walk from head or tail
// addFirst(x) is O(1) — no shifting, just relinks a node
```

**Follow-up questions:**

- *"Is `LinkedList` usually faster for frequent insertions in practice?"* — Not as often as the Big-O alone suggests — see the fuller Staff-level comparison later in this guide for why.
- *"What's `ArrayList`'s worst case?"* — Inserting or removing near the front of a large list — O(n) per operation, since everything after has to shift.

**Sources:** [`ArrayList`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayList.html), [`LinkedList`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/LinkedList.html) Javadoc, JDK 21

---

### 9. `Iterator` vs. `ListIterator` — What's the Difference?

**Core answer:**

"`Iterator` is the general-purpose interface every `Collection` supports: forward-only traversal, with `hasNext()`/`next()`/`remove()`. `ListIterator` is a `List`-specific extension of `Iterator` that adds real capabilities plain `Iterator` doesn't have: it can traverse **backward** as well as forward (`hasPrevious()`/`previous()`), it exposes the current index (`nextIndex()`/`previousIndex()`), and — critically — it can **modify** the list during iteration, not just remove from it: `set()` replaces the last element returned by `next()`/`previous()` in place, and `add()` inserts a new element at the iterator's current position.

Plain `Iterator` only supports `remove()`; if the loop needs to replace or insert elements while walking the list, `ListIterator` is the only safe way to do it without triggering `ConcurrentModificationException`."

**Staff-level extension:**

The practical trigger for reaching for `ListIterator` over plain `Iterator` is almost always "I need to modify the list, not just remove from it, while I'm walking it" — replacing every element matching a condition, or inserting a new element relative to the current position. Outside a `List`-specific need like that, plain `Iterator` (or the `Collection` default methods like `removeIf()`) is simpler and should stay the default.

**Example:**

```java
List<String> names = new ArrayList<>(List.of("alice", "bob", "carol"));

ListIterator<String> it = names.listIterator();
while (it.hasNext()) {
    String name = it.next();
    if (name.equals("bob")) {
        it.set("BOB");           // replace in place — plain Iterator can't do this
        it.add("dave");          // insert right after — plain Iterator can't do this either
    }
}
System.out.println(names); // [alice, BOB, dave, carol]
```

**Follow-up questions:**

- *"Can `ListIterator` traverse backward?"* — Yes — `hasPrevious()`/`previous()`, which plain `Iterator` doesn't offer at all.
- *"What can `ListIterator` do that plain `Iterator` can't?"* — Replace the current element (`set()`) and insert a new one (`add()`) during iteration — plain `Iterator` only supports `remove()`.

**Sources:** [`ListIterator` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ListIterator.html)

---

### 10. `Queue` vs. `Deque` — What's the Difference, and When Would You Use Each?

**Core answer:**

"`Queue` models FIFO (first-in-first-out) access: elements go in at the tail (`offer()`/`add()`) and come out at the head (`poll()`/`remove()`) — the right shape for task queues, breadth-first traversal, or any producer/consumer scenario where processing order should match arrival order. `Deque` ('double-ended queue') generalizes this: it supports insertion and removal at **both** ends (`addFirst()`/`addLast()`, `pollFirst()`/`pollLast()`), so it can act as a `Queue` (FIFO), a stack (LIFO, via `push()`/`pop()`, which operate on the head), or both at once.

`ArrayDeque` is the standard general-purpose implementation of both interfaces — the Javadoc itself notes it's likely faster than `LinkedList` when used as a queue and faster than the legacy `Stack` class when used as a stack, since it's backed by a resizable circular array rather than individually-allocated nodes."

**Staff-level extension:**

In modern code, `ArrayDeque` has largely replaced both the old `java.util.Stack` (a synchronized, `Vector`-based class from Java 1.0, functionally obsolete) and `LinkedList` for pure queue/stack use — there's rarely a reason to reach for either of those two anymore. The one thing worth knowing explicitly: `ArrayDeque` doesn't accept `null` elements, unlike `LinkedList`, which does — a real migration gotcha if existing code relied on `null` as a sentinel value in a queue or stack.

**Example:**

```java
Queue<Task> taskQueue = new ArrayDeque<>();
taskQueue.offer(task1); // added to the tail
taskQueue.offer(task2);
Task next = taskQueue.poll(); // task1 — removed from the head, FIFO order

Deque<Integer> stack = new ArrayDeque<>();
stack.push(1); // added to the head
stack.push(2);
int top = stack.pop(); // 2 — removed from the head, LIFO order
```

**Follow-up questions:**

- *"Can the same `ArrayDeque` instance be used as both a queue and a stack?"* — Yes — `Deque` supports both access patterns simultaneously; which one you get depends on which methods you call.
- *"What's the `ArrayDeque` gotcha to watch for when migrating from `LinkedList`?"* — It explicitly prohibits `null` elements, unlike `LinkedList`.

**Sources:** [`Queue`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Queue.html), [`Deque`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Deque.html), [`ArrayDeque`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayDeque.html) Javadoc, JDK 21

---

### 11. How Do You Choose Between `HashMap`, `LinkedHashMap`, and `TreeMap`?

**Core answer:**

"All three implement `Map`, and correctness — key-value lookup — is identical across them; the decision is entirely about what ordering guarantee, if any, is actually needed, since each guarantee costs something. `HashMap` makes no ordering promise at all and gives O(1) average get/put — the right default unless a specific reason says otherwise. `LinkedHashMap` adds predictable iteration order (insertion order by default, or access order with a constructor flag) at a modest extra memory cost, and is the right choice specifically when *predictable iteration* matters — logging output that should read in insertion order, or an LRU cache built on its access-order mode, covered in depth later in this guide.

`TreeMap` keeps keys sorted at all times, backed by a red-black tree, at O(log n) instead of O(1) per operation, and is the right choice when the code needs *sorted* iteration or range queries (`firstKey()`, `ceilingKey()`, `subMap()`) that neither of the other two can offer at all."

**Staff-level extension:**

The mistake worth avoiding is reaching for `LinkedHashMap` or `TreeMap` defensively "in case ordering matters later" — that pays a real, permanent cost (memory or O(log n)) for a guarantee the code may never use. The right sequencing is: default to `HashMap`, and only step up to `LinkedHashMap` or `TreeMap` once a concrete requirement (a UI needing insertion order, a report needing sorted output) actually demands it.

**Example:**

```java
Map<String, Integer> hashMap = new HashMap<>();             // no order guarantee, O(1) — default
Map<String, Integer> linkedHashMap = new LinkedHashMap<>(); // insertion order preserved
Map<String, Integer> treeMap = new TreeMap<>();              // always sorted by key, O(log n)

for (String key : List.of("banana", "apple", "cherry")) {
    hashMap.put(key, 1); linkedHashMap.put(key, 1); treeMap.put(key, 1);
}
System.out.println(hashMap.keySet());       // arbitrary-looking order
System.out.println(linkedHashMap.keySet()); // [banana, apple, cherry] — insertion order
System.out.println(treeMap.keySet());       // [apple, banana, cherry] — sorted order
```

**Follow-up questions:**

- *"What's the performance cost of `TreeMap` versus `HashMap`?"* — O(log n) per operation instead of O(1) average — the price paid for always-sorted iteration and range queries.
- *"When is `LinkedHashMap` the right default over `HashMap`?"* — Specifically when predictable iteration order is a real requirement, not a hypothetical one — e.g., an LRU cache using its access-order mode.

**Sources:** [`HashMap`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashMap.html), [`LinkedHashMap`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/LinkedHashMap.html), [`TreeMap`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/TreeMap.html) Javadoc, JDK 21

---

### 12. `Collection` vs. `Collections` — What's the Difference?

**Core answer:**

"`Collection` (singular) is the root *interface* of the framework — `List`, `Set`, and `Queue` all extend it, and it defines the common operations every collection supports (`add()`, `remove()`, `size()`, `iterator()`, and so on). `Collections` (plural) is an entirely different thing: a **utility class**, full of `static` methods that operate *on* collections rather than being one — `Collections.sort()`, `Collections.reverse()`, `Collections.max()`/`min()`, `Collections.synchronizedList()` (wraps a collection with synchronized access), and `Collections.unmodifiableList()` (wraps a collection in a read-only view, covered in depth later in this guide, including its sharp edges).

The naming is a genuinely common source of confusion for exactly this reason — one is an interface you implement or extend, the other is a helper class you call static methods on, and they're related only in that `Collections`'s methods take `Collection`s as arguments."

**Staff-level extension:**

`Collections` is effectively the same design pattern as `Arrays` (static helper methods operating on array instances) or `Objects` (static helper methods operating on any object) — a common Java standard-library idiom of pairing a core type or interface with a `static`-method utility class of the same name, pluralized or not, that provides operations which don't naturally belong as instance methods on the type itself.

**Example:**

```java
// Collection: the INTERFACE
Collection<String> items = new ArrayList<>(List.of("banana", "apple"));

// Collections: the UTILITY CLASS — static methods that operate ON a Collection
List<String> itemList = new ArrayList<>(items);
Collections.sort(itemList);
Collections.reverse(itemList);
String max = Collections.max(items); // "banana" — works on any Collection
List<String> readOnly = Collections.unmodifiableList(itemList);
```

**Follow-up questions:**

- *"Is `Collections` a subtype of `Collection`?"* — No — they're unrelated types; `Collections` is a `static`-method utility class, not part of the interface hierarchy at all.
- *"What's a similar naming pattern elsewhere in the standard library?"* — `Arrays` (static helpers for arrays) and `Objects` (static helpers for any object) follow the same idiom.

**Sources:** [`Collections` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Collections.html)

---

## Staff Level

### 13. How Does `HashMap` Work Internally — Collisions, Resizing, Treeification, Equality?

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

### 14. What Can Go Wrong If a Mutable Object Is Used as a `HashMap` Key?

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

### 15. When Would You Use `ConcurrentHashMap` Instead of a Synchronized Map?

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

### 16. Are Compound Operations on `ConcurrentHashMap` Thread-Safe? `get`-then-`put` vs. `computeIfAbsent`

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

### 17. How Would You Design an In-Memory Structure Supporting High Write Concurrency and Snapshot Reads?

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

### 18. Compare `ArrayList`, `LinkedList`, `ArrayDeque`, and `CopyOnWriteArrayList`

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

### 19. When Is `CopyOnWriteArrayList` a Good Choice, and When Is It Disastrous?

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

### 20. How Do Weakly Consistent Iterators Differ From Fail-Fast Iterators?

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

### 21. What Are the Memory and Performance Costs of Boxed Collections?

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

### 22. How Would You Diagnose a Collection That Continuously Grows in Production?

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

### 23. How Would You Build an LRU Cache Using `LinkedHashMap`?

**Core answer:**

"`LinkedHashMap` is a `HashMap` that also threads every entry through a doubly-linked list, so iteration order is predictable instead of the hash-bucket chaos you get from plain `HashMap`. By default that order is insertion order, but there's a constructor flag — `accessOrder = true` — that switches it to *access* order instead: every `get()` (and every `put()` on an existing key) moves that entry to the end of the list as 'most recently used.'

Once you have access-order tracking, an LRU cache is almost free: the least-recently-used entry is always sitting right at the front of the iteration order, which is exactly what `removeEldestEntry()` is a hook for. Override it to return `true` once the map exceeds your capacity, and `LinkedHashMap` evicts the oldest entry for you on the very next `put()` — no manual bookkeeping, no separate linked list to maintain yourself."

**Staff-level extension:**

This is a fine single-threaded or low-contention LRU implementation, but it is not thread-safe out of the box — every `get()` mutates the internal linked list (even reads are writes here, structurally), so concurrent access needs external synchronization, e.g. wrapping the whole thing and synchronizing `get`/`put` together, which reintroduces the single-lock bottleneck from question 15. For a genuinely concurrent LRU at scale, I'd point at `Caffeine` (or Guava's `CacheBuilder` before it) — it implements approximate LRU/LFU eviction (via a Window TinyLFU policy in Caffeine's case) with striped, low-contention internals rather than one global lock, which is what production caching layers actually reach for instead of hand-rolling `LinkedHashMap`.

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

### 24. `TreeMap`/`TreeSet` — How Does Ordering Work, and What Breaks If `compareTo` Is Inconsistent With `equals`?

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

### 25. What Is `WeakHashMap`, and When Would You Actually Reach for It?

**Core answer:**

"A normal `HashMap` holds a strong reference to every key, which means a key can never be garbage collected as long as it's sitting in the map — even if nothing else in the program references it anymore. `WeakHashMap` holds its keys through `WeakReference`s instead, so once a key becomes otherwise unreachable, the garbage collector is free to reclaim it, and `WeakHashMap` will lazily clear out that now-dead entry itself, typically the next time you touch the map.

The practical use case is a cache keyed by an object's *identity/lifecycle*, where you want the cache entry to disappear automatically the moment nothing else cares about that key anymore — metadata tied to a class, listener bookkeeping tied to some external object — without explicitly removing entries yourself and risking the same kind of leak from question 22."

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

### 26. `Arrays.asList()`, `List.of()`, and `Collections.unmodifiableList()` — What Are the Actual Mutability Differences?

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

### 27. How Does `PriorityQueue` Work Internally, and What Are Its Complexity Trade-Offs?

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
