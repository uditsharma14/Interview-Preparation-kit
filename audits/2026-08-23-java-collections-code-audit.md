# Java Collections — Targeted Correction and Code Audit — 2026-08-23

Scope: Java Collections code examples and a targeted subset of prose claims
(Set/Map duplicate-detection and complexity generalizations, the
ArrayDeque/List relationship), verified against Java 21 primary
documentation.

## Targeted correction pass (Q1, Q2, Q4)

A narrow re-check of five specific claims against the Java 21 Javadoc — not
a full re-read of all 27 questions. The other 22 questions in the guide
were not re-verified as part of this pass.

| Question | Severity | Problem | Correct interpretation | Authoritative source | Status |
|---|---|---|---|---|---|
| Q2 — `Set` duplicate-detection stated as a blanket `equals()`/`hashCode()` mechanism | Major | "`Set` is the mathematical-set abstraction: no duplicates (adding an element already present is a no-op, determined via `equals()`/`hashCode()`)" — true for `HashSet`/`LinkedHashSet`, false for `TreeSet`. | `TreeSet` performs all element comparisons via `compareTo()` (or a supplied `Comparator`); two elements are treated as the same whenever that returns zero, independent of `equals()`. Reworded Q2's Core answer to state the mechanism per-implementation instead of as one blanket rule. | [`TreeSet` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/TreeSet.html): "a `TreeSet` instance performs all element comparisons using its `compareTo` (or `compare`) method" | **Fixed** |
| Q4 — `HashSet`/`LinkedHashSet`/`TreeSet` comparison never named the duplicate-detection mechanism at all | Major | Core answer compared the three purely on ordering/performance, leaving "how is a duplicate decided" unstated — the same gap as the Q2 finding, in the question most likely to be asked this directly. | Added the `hashCode()`/`equals()` (`HashSet`/`LinkedHashSet`) vs. natural-ordering/`Comparator` (`TreeSet`) distinction directly into Q4's Core answer, not just its Staff-level extension. | [`TreeSet` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/TreeSet.html) | **Fixed** |
| Q2 — `HashMap`'s expected-average-O(1) lookup stated as a blanket `Map` guarantee | Major | "using parallel `List`s of keys and values... a `Map` already solves in O(1)" and a matching follow-up — reads as if every `Map` implementation is O(1), when `TreeMap` is O(log n) (already correctly stated elsewhere in this same guide). | Reworded both instances in Q2 to say `HashMap` specifically, "expected average O(1)," matching the `HashMap` Javadoc's own hedge ("assuming the hash function disperses the elements properly among the buckets"). | [`HashMap` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashMap.html) | **Fixed** |
| `TreeMap` O(log n) — verified, no change needed | — | Checked whether the guide states `TreeMap`'s lookup/insertion/removal cost anywhere, given the `Map`-blanket-O(1) issue above. | Already correctly stated in at least two places, each explicit that `TreeMap` is O(log n), not O(1). No change made. | [`TreeMap` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/TreeMap.html) | Verified — no change |
| Q1 — `ArrayList` → `ArrayDeque` described as a one-line swap alongside `List`/`Queue` | Major | "switching to `ArrayDeque` for queue-like access is a one-line change if the rest of the code only ever referenced `List`/`Queue`" — `ArrayDeque` does not implement `List`, so a `List`-typed call site cannot simply be reassigned an `ArrayDeque`. | Reworded to separate the two cases: swapping between `List` implementations is the one-line case; swapping to `ArrayDeque` is only one line if the call site was already typed as `Queue`/`Deque`. | [`ArrayDeque` Javadoc, JDK 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayDeque.html) — confirmed "All Implemented Interfaces" is `Collection`, `Deque`, `Queue`, `SequencedCollection`, `Cloneable`, `Serializable` — `List` is not among them | **Fixed** |

This did not change the guide's Fact-checked status in `AUDIT.md` — code
blocks had not yet been executed at the time of this pass, and the bulk of
the guide's claims were last independently checked at the original pass
and the Basic/Intermediate graduation, not in this narrower re-check.

## Code-block audit (full guide scope)

Every one of the guide's 28 fenced code blocks (27 `java`, 1 `bash`) was
classified: 24 self-contained runnable/compilable examples, 3 partial
illustrative snippets (Q10, Q16, Q22's `java` block — each references an
undefined placeholder type or method that was deliberately not invented to
force a compile), and 1 shell command (Q22's `bash` block, `jmap`/`jcmd`).
No pseudocode or configuration blocks exist in this guide. All 24 blocks
classified as self-contained were compiled with `javac` (JDK 21) and
executed with `java`; all 24 compiled and ran successfully, and every
observed output was checked against the block's own inline comments.

### Bug found and fixed

**Q20** ("How Do Weakly Consistent Iterators Differ From Fail-Fast
Iterators?"): the fail-fast demo used `new ArrayList<>(List.of(1, 2, 3))`,
removing the value `2` mid-iteration, with the comment "this throws, even
single-threaded." It does not: `ArrayList`'s iterator only checks for
comodification inside `next()`, and removing the second-to-last element of
a 3-element list leaves `cursor == size` after the removal, so
`hasNext()` returns `false` and the loop exits before `next()` is ever
called again — no exception is thrown. Verified deterministic (reproduced
3/3 runs) and verified the general rule empirically: removing value `n-1`
from a fresh `1..n` list never throws, for `n` from 3 to 6; every other
position does. Fixed by changing the list to `List.of(1, 2, 3, 4)` — same
removed value, no longer the second-to-last element — and confirmed it now
throws `ConcurrentModificationException` as documented. `ConcurrentModificationException`'s
own Javadoc notes the fail-fast behavior "should be used only to detect
bugs," not relied on for correctness — worth knowing independent of this
specific fix.

### Verified correct, no changes needed

Several claims were genuinely at risk of being wrong and are worth naming
individually since they were confirmed rather than assumed: Q3's
missing-`hashCode()` bug (`contains()` returns `false` as documented),
Q14's full mutate-then-restore `HashMap` key sequence (all six documented
outputs matched exactly), Q19's `CopyOnWriteArrayList` frozen-snapshot
iterator claim and its O(n²) "disaster case" (near-quadratic scaling
confirmed at reduced scale — 2,000/4,000/8,000 elements took ~0/2/9ms; the
literal 1,000,000-element case in the guide did not finish in 180 seconds,
consistent with the claim, though not run to completion), Q23's
`LinkedHashMap`-based LRU cache eviction order, Q24's `TreeSet`
natural-ordering-not-`equals()` duplicate collapse, and Q26's four separate
`Arrays.asList`/`List.of`/`Collections.unmodifiableList` behavioral claims
(all four confirmed, including the exact exception type for each).

The two `jmap`/`jcmd` commands in Q22's shell block were checked against
the JDK 21 `jmap`(1) and `jcmd`(1) man pages — both correct as written.
Noted for the record, not a guide defect: Oracle's own `jmap`
documentation currently describes the tool itself as "experimental and
unsupported."

Q10's `Task`/`task1`/`task2` placeholder was labeled directly in its code
comment, since the bare name gave no signal it wasn't a real `java.util`
type. `expensiveInit()` (Q16) and `ExpensiveContext` (Q22) were left
unlabeled, since their names and surrounding prose already make the
placeholder intent obvious.

This guide's code blocks are code-tested in the narrow sense: every block
presented as self-contained/runnable was actually compiled and executed
successfully, and the one that wasn't behaving as documented is fixed.
This does not make the guide fully verified — the 3 partial snippets were
correctly left unexecuted, and this pass did not re-check the guide's
prose/citations outside Q1/Q2/Q4.
