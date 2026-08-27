# Transactions — Code-Block Audit — 2026-08-25

Scope: eighth guide in `ROADMAP.md`'s code-block validation rollout.
This guide reuses several mechanisms already behaviorally verified in
earlier passes (proxy-based `@Transactional` self-invocation and
private-method ineffectiveness — Spring Boot Internals; optimistic/
pessimistic locking via `@Version`/`LockModeType` — JPA & Hibernate) —
those weren't re-derived here, since the underlying mechanism is
identical and already confirmed with real execution. This pass focused
verification on the claims genuinely specific to this guide: transaction
propagation semantics and the checked-vs-unchecked rollback rule.

## Classification summary (37 total code blocks)

- **20 `java`-tagged blocks.** Most reference undefined domain types
  (`Order`, `OrderService`, `accountRepository`) specific to a single
  question's own example — correctly **partial illustrative snippet**
  per `CONTRIBUTING.md`. 5 of these (Q5, Q6, Q10's propagation and
  rollback-rule examples) were independently re-implemented and executed
  against a real Spring transaction manager rather than left as
  unverified prose (see below), and the `@Retryable`/`@Backoff` usage in
  Q13/Q26/Q27 and `@TransactionalEventListener(phase = AFTER_COMMIT)` in
  Q12 were compiled directly against the real Spring Retry / Spring
  Framework 6.1 APIs to confirm correct attribute names and types.
- **10 `sql`-tagged blocks** — ACID/isolation-level demonstrations, lost-
  update/write-skew races, constraint definitions, deadlock error output,
  and expand/contract schema-migration statements — reviewed for correct
  SQL/PostgreSQL syntax, not executed against a live database.
- **6 `text`-tagged blocks** — MVCC/2PC/saga timelines and postmortem-
  style diagrams — correctly pseudocode/diagrams, not meant to execute.
- **1 `properties`-tagged block** — `idle_in_transaction_session_timeout`
  — reviewed for correct PostgreSQL directive naming.

## Behavioral verification (real Spring transaction management + H2)

Built a real Spring context (`@EnableTransactionManagement`, a
`DataSourceTransactionManager` over an H2 in-memory database, plain
`JdbcTemplate`) to independently exercise five claims — deliberately
using plain JDBC rather than JPA, since these questions are about
Spring's transaction-propagation mechanics themselves, not persistence-
context behavior already covered by the JPA pass:

- **`REQUIRED` join + shared rollback (Q5).** An outer `@Transactional`
  method inserted a row, then called an inner `@Transactional`
  (`REQUIRED`, the default) method that inserted a second row and threw.
  Result: **both** rows were rolled back — confirming the claim that a
  `REQUIRED` child joining an existing transaction shares its entire
  rollback outcome with the caller, not just its own portion.
- **`REQUIRES_NEW` independence (Q6).** An outer method called an inner
  `REQUIRES_NEW` method (which committed its own row), then inserted its
  own row and threw. Result: the outer row was rolled back, but the
  inner `REQUIRES_NEW` row **remained committed** — confirming
  `REQUIRES_NEW`'s claimed independence from the outer transaction's
  eventual outcome.
- **`NESTED` savepoint-scoped rollback (Q6).** An outer method inserted a
  row, called an inner `NESTED`-propagation method that inserted a row
  and threw, caught the exception, and continued normally. Result: the
  outer row committed, but only the nested savepoint's row was rolled
  back — confirming `NESTED`'s claimed partial-rollback-and-continue
  semantics, distinct from both `REQUIRED` and `REQUIRES_NEW`.
- **Checked exceptions do not trigger rollback by default (Q10).** A
  `@Transactional` method that inserted a row and then threw a *checked*
  `Exception` **committed** the insert anyway — confirming Spring's
  default rollback rule applies only to unchecked exceptions, exactly as
  the guide states (and flags as a common, dangerous surprise).
- **Unchecked exceptions do trigger rollback by default (Q10).** The
  same method throwing a `RuntimeException` instead correctly rolled
  back its insert.

All five results matched the guide's claims exactly, with no
discrepancies.

## Additional compile-only verification

- `@Retryable(retryFor = ..., noRetryFor = ..., maxAttempts = ...,
  backoff = @Backoff(delay = ..., multiplier = ..., maxDelay = ...))`
  (Q13, Q26, Q27) compiled cleanly against the real `spring-retry`
  dependency — confirmed `retryFor`/`noRetryFor` (not the older `value`/
  `exclude`) are valid attribute names on the version this repo's
  baseline implies.
- `@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)`
  (Q12) compiled cleanly against Spring Framework 6.1.

## Bugs found

None. Unlike the JPA/Hibernate and Redis/Caching passes, no compile
errors or factually incorrect claims were found in this guide's code.

## Minor observation (not a bug, not fixed)

Q13's `@Retryable(retryFor = DeadlockLoserDataAccessException.class, ...)`
compiles and works correctly, but `DeadlockLoserDataAccessException` was
marked `@Deprecated(since = "6.0.3")` in Spring Framework — confirmed via
`javap` against the real `spring-tx-6.1.6.jar`. It still exists, still
compiles, and still triggers correctly on a deadlock (the class wasn't
removed, only deprecated), so this wasn't changed — noted here for the
same reason as the Redis pass's `RedisConnection.get(byte[])`
observation: a currency note, not a functional defect.

## Not done in this pass

- The remaining ~13 `java` blocks referencing undefined, question-
  specific domain types were classified as partial illustrative per
  `CONTRIBUTING.md` and not compiled.
- No live PostgreSQL instance was used — the `sql`-tagged blocks
  (isolation levels, `pg_stat_activity`, deadlock error text, schema
  migration statements) were reviewed for syntactic correctness against
  PostgreSQL documentation, not executed. `BEGIN ISOLATION LEVEL
  REPEATABLE READ` was confirmed as valid PostgreSQL `BEGIN` syntax
  against the docs rather than executed.
- Self-invocation (Q8) and private-method (Q9) `@Transactional`
  ineffectiveness were not re-verified with a new test — both are the
  identical proxy mechanism already confirmed with real execution in
  `audits/2026-08-25-spring-boot-internals-code-audit.md`.
- Distributed-systems concepts with no meaningfully executable form in
  this environment (2PC's blocking coordinator failure mode, saga
  choreography/orchestration, MVCC/VACUUM internals) were reviewed for
  factual accuracy against their cited sources but not executed —
  they aren't code in the classifiable sense to begin with.
