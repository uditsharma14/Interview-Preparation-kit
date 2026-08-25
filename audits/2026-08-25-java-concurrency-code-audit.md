# Java Concurrency — Full Code-Block Audit — 2026-08-25

Scope: the first guide in `ROADMAP.md`'s code-block validation rollout.
Every one of the guide's 34 fenced code blocks (33 `java`, 1 `bash`) across
its 33 questions was classified per `CONTRIBUTING.md`'s five-way policy,
and every block classified as compilable was actually compiled with
`javac`/`java` (JDK 21) and executed, with output checked against the
block's own inline comments.

## Classification summary

- **16 compilable examples** (Q1, Q2, Q3, Q4, Q5, Q6, Q9, Q10, Q14, Q15,
  Q22, Q24, Q26, Q28, Q30, Q31) — all compiled and executed. Two real
  bugs found (below); every other output matched its inline comments
  exactly.
- **17 partial illustrative snippets** (Q7, Q8, Q11, Q12, Q13, Q16, Q17,
  Q18's `transfer()` method, Q19, Q20, Q21, Q23, Q25, Q27, Q29, Q32, Q33)
  — each assumes a domain type or helper method not shown (`lock`,
  `doWork()`, `restTemplate`, `Account`, `EventBus`, Spring's
  `TaskDecorator`/`MDC`/`SecurityContextHolder`, or JUnit's `@Test`), or
  (Q33) is an explicitly-flagged preview API (`StructuredTaskScope`
  targeting JEP 505/JDK 25) not compilable on this guide's JDK 21
  baseline — already honestly caveated in the guide's own prose, not a
  finding.
- **1 shell command** (Q18's `jstack`/`jcmd` invocation) — verified as
  real, current tool syntax; not executed against a live hung process,
  since that would require deliberately constructing one.

Several "partial illustrative" blocks (Q16's `StampedLock` optimistic
read, Q29's `CountDownLatch`/`CyclicBarrier` test logic) were additionally
verified with a separate, self-contained test harness reproducing their
core mechanism, even though the blocks as literally shown in the guide
aren't standalone-compilable (bare fields/methods with no class wrapper,
or JUnit's `@Test` annotation). Both confirmed correct.

## Bugs found and fixed

### Q31 — `AtomicStampedReference<Integer>` example silently failed due to Integer autoboxing

The example illustrating the ABA problem used the literal `200` at two
separate call sites: `ref.compareAndSet(100, 200, 0, 1)` and later
`ref.compareAndSet(200, 100, 1, 2)`. Running it exactly as shown, the
second call **silently failed** — the guide's comments confidently assert
"value is 100 again, but stamp is now 2," but the actual final state
stayed at `(200, 1)`.

Root cause, confirmed with a targeted diagnostic: `AtomicStampedReference.compareAndSet()`
compares the expected reference by `==`, not `.equals()`. Java's `Integer`
autoboxing only guarantees a shared, cached instance for values `-128`
through `127` (`Integer.valueOf`'s documented caching range); `200` falls
outside that range, so the literal `200` at the first call site and the
literal `200` at the second call site autobox to two genuinely different
`Integer` objects. The CAS's reference check fails silently — no
exception, just a `false` return the original snippet didn't even check.

Fixed by declaring `Integer initialValue = 100, midValue = 200;` once and
reusing those same references at every call site, and added a note in the
Staff-level extension naming this exact gotcha explicitly — it's a
genuinely non-obvious, real pitfall for anyone using `AtomicReference`/
`AtomicStampedReference` over a boxed numeric type outside the cached
range, not just a bug in this one example. Re-verified the fixed version
produces the exact output the guide's comments claim.

### Q28 — `BoundedCache` settled at capacity + 1, not the stated capacity

The bounded-cache sketch checked `if (map.size() > capacity)` inside the
`computeIfAbsent` mapping function to decide whether to evict. Verified
by running it directly: inserting 5 entries into a `BoundedCache(3)` left
**4** entries in the map, not 3.

Root cause: `ConcurrentHashMap.computeIfAbsent()`'s mapping function runs
*before* the key is actually committed into the map — `map.size()`
read from inside that function does not yet count the key currently being
computed. Checking `> capacity` therefore only evicts once the map
already holds `capacity + 1` *other* entries, so the map settles at
`capacity + 1` in steady state, not `capacity` as the constructor's name
and parameter imply.

Fixed by changing the check to `>= capacity`, which accounts for the
about-to-be-added entry. Re-verified: `BoundedCache(3)` now correctly
settles at exactly 3 entries after 5 inserts. This is a real, findable
correctness bug distinct from the guide's own already-disclosed hedge
about the eviction being "approximate FIFO... not for production
correctness" (that hedge is about LRU-vs-FIFO ordering fidelity; the
off-by-one is a different, previously-undisclosed defect in the bound
itself).

## Claims independently verified accurate (no bug, cited for completeness)

- **Q4** — the naive `Counter` race: run across 3 trials, 2 threads ×
  100,000 increments each reliably finished well below the expected
  200,000 (106,482–107,927 observed), confirming the guide's "reliably
  LESS than 200,000" claim.
- **Q15** — `BrokenCounter` (`volatile` alone, no atomicity) reliably lost
  updates across 3 trials (144,686–154,605 observed, never 200,000);
  `CorrectCounter` (`AtomicInteger`) hit exactly 200,000 on all 3 trials.
  Confirms the guide's central claim that `volatile` provides visibility
  without atomicity.
- **Q24** — `SumTask`'s `ForkJoinPool`/work-stealing sum and the
  equivalent parallel-stream sum both matched the mathematically correct
  total for a 1,000,000-element array exactly.
- **Q29** — the `CountDownLatch`-based deterministic-wait pattern and the
  `CyclicBarrier`-forced-concurrency pattern (with the JUnit `@Test`
  annotations stripped and `assertEquals` replaced with a plain
  comparison, since JUnit wasn't available in this ad hoc compile
  environment) both produced the exact counts the guide's assertions
  claim, across 3 trials each.
- **Q16** — the `StampedLock` optimistic-read-with-validation-fallback
  pattern was stress-tested with a concurrent writer running 100,000
  updates while a reader called `distanceFromOrigin()` 100,000 times
  concurrently; completed without error or an impossible (negative)
  result.

## Not done in this pass

- The 4 code fences flagged by `scripts/check_code_fences.py` outside
  this guide (AI Engineering, Cross-Stack Design Scenarios, Transactions)
  are unrelated to Java Concurrency and remain open, tracked in
  `ROADMAP.md`.
- Q33's `StructuredTaskScope` preview API was not compiled — it targets
  JEP 505 (JDK 25, fifth preview), and this environment's JDK is 21,
  which has an earlier, structurally different preview shape of the same
  API (the constructor-based `ShutdownOnFailure`, not the
  `open(Joiner)` factory shown). The guide's own prose already discloses
  this precisely; installing a JDK 25 early-access build to compile a
  preview API was judged out of scope for this pass.
