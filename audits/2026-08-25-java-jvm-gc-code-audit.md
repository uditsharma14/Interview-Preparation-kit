# Java JVM & GC — Full Code-Block Audit — 2026-08-25

Scope: second guide in `ROADMAP.md`'s code-block validation rollout.
Every one of the guide's 31 fenced code blocks (9 `java`, 17 `bash`, 1
`yaml`, 4 `text`) across its 30 questions was classified per
`CONTRIBUTING.md`'s five-way policy. Every block classified as compilable
was compiled with `javac`/`java` (JDK 21) and executed, with output
checked against the block's own inline comments.

## Classification summary

- **7 compilable examples** (Q2, Q3, Q4, Q5, Q7, Q10, Q16) — all compiled
  and executed. Every observed output matched its inline comments
  exactly. No bugs found.
- **2 partial illustrative snippets** (Q17, Q29) — each assumes a
  domain-specific helper method not shown (`loadExpensiveData()`,
  `session`, `loadEntireFileIntoMemory()`, `processData()`). The
  self-containable *mechanisms* within Q17 specifically (the
  `WeakReference` collection-timing claim and the `Cleaner`-based
  resource-cleanup pattern) were independently verified with stubbed
  test harnesses — both correct (below).
- **17 shell commands** (`bash`-tagged — `jstack`/`jcmd`/`java` flag
  invocations, `grep`/`dmesg` pipelines) — spot-checked for correct,
  current flag syntax against JDK 21 documentation; not executed against
  a live JVM incident, since most require a real hung/leaking process to
  observe meaningful output from.
- **1 configuration block** (Q28's Kubernetes `resources` YAML) — valid
  Kubernetes resource-spec syntax.
- **4 pseudocode/diagram blocks** (Q1, Q6, Q25, Q30, all tagged `text`) —
  conceptual diagrams (heap layout, shallow-vs-retained-size illustration,
  a postmortem-structure outline), correctly not tagged as a real
  language since none are meant to run.

## Claims independently verified accurate (no bug, cited for completeness)

- **Q4** — `String.class.getClassLoader()` printed `null` (bootstrap
  loader), and the application/platform class loader printouts matched
  the guide's claimed identities exactly.
- **Q7** — the string-interning example (`a == b` true, `a == c` false,
  `a.equals(c)` true) reproduced exactly as claimed.
- **Q16** — `computeDistance(0, 0, 3, 4)` correctly returned `5.0` (a
  3-4-5 triangle), and `sumWithRedundantLock(3, 4)` correctly returned
  `7` — confirming the scalar-replacement and lock-elimination example
  code is functionally correct (the JIT optimization claims themselves
  are about *how* this runs, not observable from output alone, and the
  guide's own prose already correctly frames them as compiler
  opportunities rather than guarantees).
- **Q17 (WeakReference)** — stubbed out `session`/`loadExpensiveData()`
  and confirmed, across 3 trials, that `weakSession.get()` returned `null`
  after `session = null; System.gc();` — matching the guide's "very
  likely null already" claim.
- **Q17 (Cleaner)** — stubbed `releaseNativeHandle()` and confirmed the
  `NativeResourceHolder`/`Cleaner.Cleanable` pattern correctly invokes
  cleanup deterministically via `close()` inside a try-with-resources
  block, exactly as the pattern is meant to work.

## Bugs found and fixed

None. Every compilable block ran correctly on the first attempt, and
every independently-verified claim held. This is a genuinely clean
result, not a shortened audit — the same extraction, compilation, and
verification rigor was applied as for Java Concurrency (which did surface
two real bugs the same day).

## Not done in this pass

- The `bash`-tagged shell commands (JVM flags, `jcmd`/`jstack`
  invocations, GC log greps) were checked for correct syntax against
  current JDK 21 documentation but not executed — most require a real,
  running JVM under representative load or a deliberately-constructed
  failure condition (a live OOM, an actual deadlock, a genuine memory
  leak) to produce meaningful output, which was judged out of scope for
  a documentation code-audit pass.
- The 4 code fences flagged by `scripts/check_code_fences.py` outside
  this guide (AI Engineering, Cross-Stack Design Scenarios, Transactions)
  remain open, tracked in `ROADMAP.md`.
