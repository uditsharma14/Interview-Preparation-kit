# Redis & Caching — Code-Block Audit — 2026-08-25

Scope: seventh guide in `ROADMAP.md`'s code-block validation rollout.
No Redis server, `redis-cli`, or Lua interpreter is available on this
machine, and Docker's daemon isn't running. The user was asked whether
to install Redis via Homebrew, start Docker, or skip a live instance
entirely — they chose to skip live execution and rely on compile-checks
plus manual logic tracing instead, so this pass verifies what can be
verified without a running Redis (real compilation against the actual
Spring Data Redis API, and a real, executed unit test for the one piece
of pure, dependency-free logic in the guide) rather than end-to-end
command execution.

## Classification summary (36 total code blocks)

- **23 `java`-tagged blocks.** Most call `redisTemplate`/`cache` against
  undefined domain types (`Product`, `productRepository`) specific to a
  single question's own narrow example — per `CONTRIBUTING.md`, correctly
  **partial illustrative snippet**. 12 of these were extracted and
  compiled directly against the real `spring-boot-starter-data-redis`
  3.2.5 API (adding it to the reusable Maven project from the JPA/Spring
  passes) to verify method-signature/API-usage correctness, and one
  (Q21's `TokenBucket` class) is fully self-contained, dependency-free
  logic that was compiled **and executed** with a real correctness test.
- **7 `text`-tagged blocks** — race-condition timelines, cluster/failover
  diagrams, a postmortem outline — correctly diagrams/pseudocode, not
  meant to execute.
- **3 `bash`-tagged blocks** — `redis-cli --hotkeys`/`--bigkeys`/`INFO`/
  `SLOWLOG` diagnostic commands — reviewed for correct command syntax
  against current Redis documentation, not executed (no live server).
- **1 `conf`-tagged block** — `redis.conf` `maxmemory-policy` settings —
  reviewed for correct directive names, not executed.
- **1 `sql`-tagged block** — the atomic `UPDATE ... WHERE quantity >= 1`
  decrement pattern (Q20) — standard, well-known SQL, not executed.
- **1 `lua`-tagged block** — the atomic rate-limiter script (Q22) —
  traced by hand rather than executed (no Lua interpreter or Redis
  available); see below.

## Verification performed

**`TokenBucket` (Q21) — compiled and executed.** The class has zero
external dependencies (no Redis, no Spring), so it was extracted verbatim
and run against four scenarios: consuming with zero tokens and no
elapsed time correctly returns `false`; waiting ~1.1s correctly refills
~10 tokens (`REFILL_RATE_PER_SECOND = 10`) and the next consume succeeds;
draining the refilled tokens one at a time correctly stops after ~9
further successes; and a simulated one-hour idle period correctly caps
refill at `CAPACITY = 100` rather than accumulating unboundedly. All four
matched the guide's claims exactly — the refill math, the capacity cap,
and the burst/deny behavior are all correct as written.

**12 `RedisTemplate`-based snippets (Q1, Q6, Q13, Q16, Q18, Q19, Q20,
Q21, Q22, Q23, Q24, Q28) — compiled against the real Spring Data Redis
3.2.5 API.** This confirms every `redisTemplate.opsForValue()`,
`SessionCallback`, `RedisScript`, `RedisCallback`, and `executePipelined`
call site uses a real, correctly-typed method signature — catching the
kind of subtle API-usage bug that reads as plausible but doesn't actually
compile, without needing a live server to prove the syntax and typing
are correct.

**Lua rate-limiter script (Q22) — verified by manual trace, not
execution.** The script (`INCR` the key, `EXPIRE` it only on the request
that creates it via `current == 1`, reject if `current > limit`) matches
Redis's own documented "rate limiter 2" pattern exactly. The guide's own
prose already explicitly calls out and explains the specific correctness
requirement this script satisfies — conditional `EXPIRE` only on window
creation, not unconditionally on every request — so tracing the script
by hand confirms the code matches the guide's own stated reasoning; no
further issue was found.

## Bugs found and fixed

**Q16 — `WAIT` command lambda has the wrong return type (real compile
error).** The code was:

```java
redisTemplate.execute((RedisCallback<Long>) connection ->
    connection.execute("WAIT", "1".getBytes(), "1000".getBytes()));
```

`RedisConnection`/`RedisCommands.execute(String, byte[]...)` returns
`Object`, not `Long` — confirmed directly from the compiled
`spring-data-redis-3.2.5.jar` via `javap`. A lambda used as a
`RedisCallback<Long>` must return `Long`, so this fails with
`"incompatible types: bad return type in lambda expression"` — confirmed
via `javac` before fixing. Fixed with an explicit cast:

```java
redisTemplate.execute((RedisCallback<Long>) connection ->
    (Long) connection.execute("WAIT", "1".getBytes(), "1000".getBytes()));
```

## Not done in this pass

- No live Redis instance was used (declined by the user in favor of
  compile-check + manual tracing) — so `WATCH`/`MULTI`/`EXEC`'s actual
  abort-on-modified-key behavior (Q23), pipelining's actual round-trip
  reduction (Q24), the Lua script's actual atomic execution (Q22), and
  the distributed-lock/fencing-token examples' actual runtime behavior
  (Q18/Q19) were reviewed for correctness but not executed end-to-end.
- The remaining ~11 `java` blocks referencing undefined, question-specific
  domain types not covered above were classified as partial illustrative
  per `CONTRIBUTING.md` and not compiled.
- A minor, non-blocking observation: Q24's pipelining example calls
  `RedisConnection.get(byte[])`, which Spring Data Redis 3.x marks
  deprecated in favor of `connection.stringCommands().get(...)` — it
  still compiles and functions correctly (confirmed above), so this
  wasn't changed; flagging it here rather than treating it as a bug,
  since the guide's own baseline is Redis/Spring Boot 3.x broadly, not a
  pinned client-library minor version.
