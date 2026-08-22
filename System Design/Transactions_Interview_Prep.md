# Transactions — Interview Prep (Lead/Staff Level, with Code & Sources)

> **Target level:** Lead/Staff · **Baseline:** ANSI SQL-92 isolation levels as the reference framework; PostgreSQL (current) as the reference RDBMS wherever database-specific behavior is shown; Spring Framework 6.x declarative transaction management (`@Transactional`, propagation types) · **Last verified:** 2026-08-22 · **Prerequisites:** basic SQL; [Spring Boot Internals](../Frameworks/Spring_Boot_Internals_Interview_Prep.md) helpful for the proxy-based `@Transactional` sections

How to use this: each question has **the answer the way I'd actually say it out loud** in an interview, a **code snippet** you could sketch on a whiteboard or IDE to back it up, and **where the follow-up goes if you're in a Staff-level loop** — because at this level the bar is explaining what actually breaks across service and database boundaries, not reciting ACID as a definition.

---

## 1. Explain ACID in Practical Terms

**Answer:**

"**Atomicity** — a transaction's operations happen as one indivisible unit: either every write in it takes effect, or none do. If step 3 of 5 fails, steps 1 and 2 get rolled back too, not left half-applied. **Consistency** — a transaction takes the database from one valid state to another, respecting every constraint (foreign keys, unique constraints, check constraints, and application-level invariants a transaction is designed to preserve) — this is really the *outcome* the other three properties combine to guarantee, not an independent mechanism of its own. **Isolation** — concurrent transactions behave, from each transaction's own point of view, as if they ran one at a time, sequentially, even though the database may actually be interleaving their execution for performance — the exact strength of this guarantee is tunable (question 2), and weaker isolation levels intentionally allow specific anomalies in exchange for more concurrency. **Durability** — once a transaction commits, its effects survive any subsequent crash, power loss, or restart — typically achieved via a write-ahead log flushed to durable storage before the commit is acknowledged to the caller.

The practical, staff-level framing I'd add: these four properties aren't equally 'free' — atomicity and durability are close to non-negotiable for anything a relational database claims to support, but isolation is the one with a genuine, deliberate spectrum of trade-offs (question 2), and a huge amount of real production bugs and design decisions in a system come from picking (or defaulting into) the wrong isolation level for what a specific piece of business logic actually needs."

**Code:**

```sql
BEGIN;
  UPDATE accounts SET balance = balance - 100 WHERE id = 1; -- debit
  UPDATE accounts SET balance = balance + 100 WHERE id = 2; -- credit
COMMIT;
-- ATOMICITY: if the second UPDATE fails (e.g., account 2 doesn't exist),
-- the FIRST update is also rolled back — money never just vanishes from
-- account 1 with nowhere to go
```

**Follow-up:**

I'd bring up that "consistency" in ACID is a genuinely different, narrower notion than "consistency" in the CAP theorem sense — a common point of confusion in interviews and in casual conversation alike. ACID consistency means "the database's own declared constraints are never violated by a committed transaction" (a foreign key always points at a row that exists, a unique constraint is never doubly satisfied); CAP consistency means "every read sees the most recent write, across a distributed set of replicas/nodes." A system can be perfectly ACID-consistent on a single node while being eventually (not CAP-)consistent across replicas — these are separate axes, and conflating them in a distributed-systems discussion is a real, common mistake worth explicitly avoiding.

**Source:** [Jim Gray — The Transaction Concept](https://jimgray.azurewebsites.net/papers/thetransactionconcept.pdf), [PostgreSQL Documentation — Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html)

---

## 2. What Anomalies Are Possible at Each Isolation Level?

**Answer:**

"The SQL standard defines four isolation levels, each permitting fewer anomalies than the one before it, at the cost of more locking/contention or more complex concurrency-control machinery underneath.

**Read Uncommitted** — permits dirty reads (question 3): a transaction can see another transaction's *uncommitted*, possibly-about-to-be-rolled-back changes. Rarely actually implemented as a truly distinct level in modern databases (PostgreSQL, for instance, treats it identically to Read Committed) — it's mostly a historical/standard-completeness entry at this point.

**Read Committed** — the most common real-world default (PostgreSQL, SQL Server, Oracle all default here) — prevents dirty reads, but still permits non-repeatable reads and phantom reads: each individual statement within a transaction sees a fresh snapshot as of *that statement's* start, so two `SELECT`s of the same row within one transaction can see different values if another transaction committed a change in between them.

**Repeatable Read** — prevents non-repeatable reads by taking one snapshot as of the *transaction's* start (not each statement's), so the same row read twice within one transaction is guaranteed to return the same value — but the SQL standard still permits phantom reads at this level (a *new* row matching a `WHERE` clause appearing in a second identical query), though PostgreSQL's actual implementation of Repeatable Read (built on MVCC, question 4) happens to prevent phantoms too, which is stricter than the standard requires and a genuinely common point of confusion between the *standard's* definition and a *specific database's* actual behavior at that level.

**Serializable** — the strongest level: transactions behave as if executed one at a time in some serial order, preventing all of the above anomalies including write skew (question 16), at the cost of the database needing to detect and abort transactions that *would* violate serializability if allowed to both commit — meaning application code at this level must be prepared to retry a transaction that gets aborted purely due to a detected serialization conflict, not an actual data error."

**Code:**

```sql
-- setting isolation level per-transaction, PostgreSQL syntax
BEGIN ISOLATION LEVEL REPEATABLE READ;
  SELECT balance FROM accounts WHERE id = 1; -- snapshot taken HERE, at BEGIN
  -- ... another transaction commits a change to account 1 in between ...
  SELECT balance FROM accounts WHERE id = 1; -- SAME value as above — guaranteed
COMMIT;                                        -- by Repeatable Read's snapshot semantics
```

**Follow-up:**

I'd emphasize the point that matters most in practice: **the SQL standard describes anomalies each level must *prevent*, not the exact mechanism**, so two databases both claiming "Repeatable Read" can have subtly different actual guarantees (PostgreSQL's Repeatable Read also prevents phantoms and write skew via serializable-snapshot-isolation-adjacent techniques; the SQL standard's minimal definition of Repeatable Read does not require phantom prevention) — meaning "what isolation level are we running" is necessary but not sufficient information; you have to know the *specific database's* actual documented behavior at that level, not just assume standard-textbook semantics apply verbatim. I'd also flag that most application code defaults to whatever the database's own default is (Read Committed, typically) without the team having made a deliberate choice — and that default is often the right choice for typical CRUD workloads, but any code relying on multi-statement read consistency within a transaction (a report computing an aggregate from several queries that all need to reflect the same point in time) needs to explicitly choose and justify a stronger level, not assume the default happens to provide it.

**Source:** [PostgreSQL Documentation — Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html), [ANSI SQL-92 Isolation Levels (as analyzed in Berenson et al., "A Critique of ANSI SQL Isolation Levels")](https://www.microsoft.com/en-us/research/publication/a-critique-of-ansi-sql-isolation-levels/)

---

## 3. Compare Dirty Reads, Non-Repeatable Reads, Phantom Reads, and Lost Updates

**Answer:**

"**Dirty read**: reading data that another, still-in-progress (uncommitted) transaction has written — if that other transaction subsequently rolls back, you've based a decision on data that, from the database's perspective, never actually happened at all.

**Non-repeatable read**: reading the *same row* twice within one transaction and getting two *different* values, because another transaction committed an update to that row in between your two reads — the row itself didn't disappear or appear, its value just changed underneath you mid-transaction.

**Phantom read**: running the *same query* (a range/filter condition, not a single-row lookup) twice within one transaction and getting a *different set of rows*, because another transaction inserted or deleted a row that newly matches (or stops matching) your query's condition in between the two executions — new 'phantom' rows appearing (or previously-matching rows disappearing) that weren't a factor in your first read.

**Lost update**: two transactions both read the same row, both compute a new value based on what they read, and both write back — the second write silently overwrites the first's change entirely, with neither transaction ever being told a conflict happened; this is specifically a *write-write* problem (unlike the first three, which are about reads seeing something inconsistent), and it's the concrete failure mode optimistic/pessimistic locking (questions 15/covered further below) exist to prevent."

**Code:**

```sql
-- LOST UPDATE — the classic race, regardless of isolation level unless
-- explicit locking or optimistic version checking is used
-- Transaction A                          Transaction B
BEGIN;                                    BEGIN;
SELECT balance FROM accounts WHERE id=1;  SELECT balance FROM accounts WHERE id=1;
-- reads 100                              -- ALSO reads 100
UPDATE accounts SET balance = 100 - 30    UPDATE accounts SET balance = 100 - 50
  WHERE id = 1;                            WHERE id = 1;
COMMIT;                                    COMMIT;
-- Final balance: 50 (B's write wins) — A's $30 debit is SILENTLY LOST,
-- neither transaction was ever told a conflict occurred
```

**Follow-up:**

I'd point out that lost updates are the anomaly that's easiest to accidentally reproduce in *application* code even when the database's own isolation level would otherwise prevent a pure SQL-level version — specifically, the common "read a row in one statement, compute in application code, write it back in a separate statement" pattern (`SELECT` then, in Java, `balance - amount`, then a separate `UPDATE ... SET balance = ?`) reintroduces exactly this race regardless of the database's isolation level, because the check-then-act sequence spans two separate round trips with application logic in between, not one atomic SQL statement — the fix is either a single atomic `UPDATE accounts SET balance = balance - ? WHERE id = ?` (letting the database do the arithmetic in one statement) or explicit optimistic/pessimistic locking around the read-modify-write sequence. I'd frame this as the direct bridge to the JPA/Hibernate file's optimistic-locking discussion — the exact same lost-update problem, just expressed at the ORM/entity level instead of raw SQL.

**Source:** [Berenson et al. — A Critique of ANSI SQL Isolation Levels](https://www.microsoft.com/en-us/research/publication/a-critique-of-ansi-sql-isolation-levels/)

---

## 4. How Does MVCC Work?

**Answer:**

"Multi-Version Concurrency Control is the mechanism most modern relational databases (PostgreSQL, MySQL/InnoDB, Oracle) use to provide strong isolation *without* readers and writers blocking each other for ordinary reads. Instead of a reader taking a lock to prevent a writer from changing a row it's currently reading, the database keeps **multiple versions** of a row simultaneously — when a transaction updates a row, it doesn't overwrite the old version in place; it creates a *new* version of the row (tagged with the transaction ID that created it) while the old version remains, still visible to any transaction whose snapshot predates the update.

Each transaction, depending on its isolation level, operates against a consistent **snapshot** — effectively 'the set of row versions that were committed as of some point in time' — and reads simply select the correct version to look at from that transaction's perspective, entirely without needing to acquire a read lock or block on a concurrent writer at all. This is exactly what gives 'readers don't block writers, and writers don't block readers' behavior (though writers still block *other writers* modifying the same row, since two concurrent writes to the same row genuinely can't both apply without conflict resolution) — a substantial concurrency win over purely lock-based isolation schemes, at the cost of needing a background process (PostgreSQL's `VACUUM`) to eventually clean up old row versions that no active transaction's snapshot needs anymore."

**Code:**

```text
Row id=1, initial state: balance=100, created by txn 5

Transaction 10 (long-running, snapshot taken early):
  sees balance=100 (the version visible as of its snapshot)

Transaction 11 (concurrent, updates the row):
  UPDATE accounts SET balance=150 WHERE id=1;
  -- creates a NEW version of the row: balance=150, created by txn 11
  COMMIT;

Transaction 10 (still running, same snapshot as before):
  SELECT balance FROM accounts WHERE id=1;
  -- STILL sees balance=100 — its snapshot predates txn 11's commit,
  -- and MVCC serves it the OLD version without blocking on txn 11 at all,
  -- and without txn 11 having had to block waiting for txn 10 to finish reading
```

**Follow-up:**

I'd bring up `VACUUM` (PostgreSQL specifically) as the operationally important consequence of MVCC that's easy to overlook until it becomes an incident: old row versions ("dead tuples") accumulate as updates/deletes happen, and if `VACUUM` falls behind (heavy write load, long-running transactions holding old snapshots open and preventing cleanup of versions they might still need), table bloat grows, index efficiency degrades, and in an extreme, genuinely dangerous case, PostgreSQL's transaction ID (`xid`) counter can approach wraparound, which the database proactively guards against by refusing new writes entirely until an aggressive forced vacuum completes — a real, production-halting failure mode that traces directly back to MVCC's version-accumulation mechanism, not a mysterious unrelated database bug. I'd mention this specifically because "why is my database suddenly refusing writes" or "why did performance degrade gradually over months" investigations in a PostgreSQL system very often trace back to exactly this — long-running transactions (an idle-in-transaction connection left open, a batch job holding a transaction open far longer than intended) preventing vacuum from reclaiming old versions.

**Source:** [PostgreSQL Documentation — MVCC](https://www.postgresql.org/docs/current/mvcc-intro.html), [PostgreSQL Documentation — Routine Vacuuming](https://www.postgresql.org/docs/current/routine-vacuuming.html)

---

## 5. What Is the Default Spring Transaction Propagation Behavior?

**Answer:**

"`REQUIRED` is the default propagation for `@Transactional` — if a transaction is already active when a `@Transactional` method is called, the method joins that existing transaction (participates in it, sharing its commit/rollback outcome); if no transaction is currently active, a new one is started. This default is deliberately the 'just make sure there's *a* transaction, reusing one if it already exists' behavior, which is the right default for the overwhelming majority of service-layer methods — most business operations should participate in whatever transactional context their caller established, rather than each method insisting on its own independent transaction.

The practical implication worth being precise about: because `REQUIRED` joins the *existing* transaction rather than starting an independent one, if a `REQUIRED` method throws an exception that triggers a rollback, it marks the **entire, shared** transaction for rollback — including whatever work the *calling* method (or any other method further up the call chain, also participating in the same shared transaction) had already done, even if that calling code doesn't itself throw or otherwise seem to fail. This is often exactly the desired behavior (the whole logical operation should be all-or-nothing), but it's a common source of confusion when a seemingly-unrelated failure deep in a call chain unexpectedly rolls back work that looked, from the outer method's code, like it had already succeeded."

**Code:**

```java
@Service
class OrderService {
    @Transactional // REQUIRED (default) — starts a NEW transaction, since
    void placeOrder(Order order) { // nothing was already active when this was called
        orderRepository.save(order);
        inventoryService.reserve(order); // joins THIS SAME transaction
    }
}

@Service
class InventoryService {
    @Transactional // REQUIRED (default) — JOINS the caller's already-active
    void reserve(Order order) { // transaction, does NOT start an independent one
        inventoryRepository.decrement(order.getSku(), order.getQuantity());
        if (insufficientStock()) {
            throw new InsufficientInventoryException(); // marks the ENTIRE shared
            // transaction (including orderRepository.save() above, from the
        }                                                   // CALLING method) for rollback —
    }                                                          // the order save is undone too,
}                                                                // even though placeOrder()'s
                                                                   // own code never itself failed
```

**Follow-up:**

I'd bring up that this default is precisely why business operations that span multiple service-layer methods should be thought of as one atomic unit from a transactional-boundary perspective, even though they're implemented as separate Java method calls across separate classes — the `@Transactional` boundary that actually matters for a given business operation is typically the outermost, entry-point method (`placeOrder()` in the example), and inner `@Transactional` annotations on methods that are only ever called from within an already-transactional context are, practically speaking, mostly documentation/safety-net annotations (ensuring the method still behaves correctly if it's ever called standalone) rather than the methods that actually determine transaction boundaries in the common call path. I'd also connect this forward to question 12 — transaction boundaries should align with business operations, and `REQUIRED`'s join-the-existing-transaction default is exactly the mechanism that makes a multi-method, multi-class business operation cohere into one correct atomic unit without every individual method needing to reason about where the actual transaction started.

**Source:** [Spring Framework Reference — Transaction Propagation](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/tx-propagation.html)

---

## 6. Explain `REQUIRED`, `REQUIRES_NEW`, `NESTED`, and `NOT_SUPPORTED`

**Answer:**

"`REQUIRED` (question 5): join an existing transaction if one is active, otherwise start a new one — one shared, all-or-nothing outcome across the whole call chain that participates in it.

`REQUIRES_NEW`: always start a **brand-new, independent** transaction, suspending any currently-active one for the duration of the call — the new transaction commits or rolls back entirely on its own, completely independent of whatever happens to the outer (suspended, then resumed) transaction afterward. This is the right tool specifically when you need a piece of work to **survive** even if the outer operation later fails — the canonical example is audit logging: you want the audit record to persist regardless of whether the broader business operation it's logging ultimately succeeds or rolls back, so the audit-write needs its own independent, already-committed transaction, not one that would be rolled back along with everything else if the outer operation fails afterward.

`NESTED`: starts a true database **savepoint** within the existing transaction (not a fully independent transaction) — if the nested portion fails and rolls back, only the work done since that savepoint is undone, while the outer transaction can catch the failure and continue, still within the *same* overall transaction and connection, ultimately committing or rolling back everything together as one unit. This requires the underlying JDBC driver/database to actually support savepoints (most do, but it's a real prerequisite, and some environments/drivers don't).

`NOT_SUPPORTED`: suspends any currently-active transaction and runs the method with **no transaction at all** — useful for an operation that's read-only, doesn't need transactional guarantees, and specifically shouldn't hold a database connection/transaction resource open for its duration (a long-running external call, or a read that's fine being non-transactional and shouldn't tie up connection-pool capacity for longer than necessary)."

**Code:**

```java
@Transactional // REQUIRES_NEW — commits INDEPENDENTLY, survives even if the
public void logAuditEvent(String action, String userId) { // caller's transaction
    auditRepository.save(new AuditEntry(action, userId, Instant.now())); // later rolls back
}

@Transactional
public void placeOrder(Order order) {
    orderRepository.save(order);
    auditService.logAuditEvent("order_placed", order.getUserId()); // commits ON ITS OWN,
    // even if something below throws and rolls back placeOrder()'s own transaction

    if (fraudCheckFails(order)) {
        throw new FraudSuspectedException(); // rolls back the order save —
    }                                          // but the audit log entry ALREADY
}                                                 // committed independently, and stays

@Transactional(propagation = Propagation.NESTED) // true SAVEPOINT within the
public void attemptRiskyStep(Order order) {         // SAME outer transaction/connection
    riskyRepository.doSomethingThatMightFail(order);
    // if this throws, ONLY this nested portion rolls back to its savepoint —
    // the outer transaction can catch it and continue, still one shared commit/rollback
}
```

**Follow-up:**

I'd emphasize `REQUIRES_NEW`'s real cost, which directly sets up the next question: it acquires a genuinely **separate** database connection from the pool for the duration of the inner transaction (the outer connection is suspended, not reused), so a call chain that nests several `REQUIRES_NEW` calls (or calls one repeatedly in a loop) can exhaust the connection pool far faster than the `REQUIRED` default would, since each `REQUIRES_NEW` invocation checks out its own connection on top of whatever the outer, suspended transaction is already holding. I'd also mention `NESTED` as the generally underused middle ground worth considering more often than it typically gets reached for — it gives partial-rollback-and-continue semantics without the connection-pool cost of a fully independent transaction, though its savepoint-based implementation means it's still tied to the outer transaction's ultimate fate (if the *outer* transaction itself rolls back entirely, the nested savepoint's work is rolled back too, regardless of whether the nested portion itself "succeeded" earlier).

**Source:** [Spring Framework Reference — Transaction Propagation](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/tx-propagation.html)

---

## 7. Why Might `REQUIRES_NEW` Exhaust a Connection Pool?

**Answer:**

"Because `REQUIRES_NEW` suspends the caller's current transaction and connection, then checks out a **separate, additional** connection from the pool for the new, independent transaction — meaning at the moment a `REQUIRES_NEW` method is executing, at least two connections are simultaneously checked out for what is, from the outside, a single logical call chain: the outer, suspended transaction's connection (held, though idle, waiting for the inner call to return) and the inner transaction's own freshly-checked-out connection.

This compounds badly in a few realistic scenarios: a `REQUIRES_NEW` call made from *within a loop* (audit-logging each item of a large batch individually, say) checks out and returns a connection *per iteration*, and under high concurrency, many threads each doing this simultaneously can rapidly exhaust a fixed-size pool, especially if the inner transaction's work is even slightly slow; or a call chain with several nested layers, each independently using `REQUIRES_NEW` for its own reasons, stacks up multiple simultaneously-held connections per single external request. The failure mode in production is exactly the classic connection-pool-exhaustion symptom — requests start blocking waiting for a connection to become available, and under sustained load this can cascade into widespread timeouts across completely unrelated request paths sharing the same pool, not just the specific operation using `REQUIRES_NEW`."

**Code:**

```java
// DANGEROUS — REQUIRES_NEW called inside a loop; each iteration holds the
// OUTER transaction's connection suspended WHILE ALSO checking out a
// separate connection for the inner call — connection demand roughly
// DOUBLES for the duration of this loop, per concurrent request
@Transactional
void processBatch(List<Item> items) {
    for (Item item : items) {
        auditService.logAuditEvent("processed", item.getId()); // REQUIRES_NEW,
    }                                                              // called N times —
}                                                                    // N connection
                                                                       // check-outs, on TOP
                                                                        // of this method's
                                                                         // own already-held
                                                                          // connection

// BETTER — batch the audit writes into ONE independent transaction,
// rather than one REQUIRES_NEW call per loop iteration
@Transactional(propagation = Propagation.REQUIRES_NEW)
void logAuditEventsBatch(List<AuditEntry> entries) {
    auditRepository.saveAll(entries); // ONE additional connection check-out,
}                                        // regardless of batch size
```

**Follow-up:**

I'd bring up that this is exactly the kind of production incident that's genuinely hard to spot in code review, since `REQUIRES_NEW` on an individual method looks completely reasonable in isolation — the danger only manifests from the *calling pattern* (inside a loop, or nested several layers deep under load), which requires tracing actual call chains and connection-pool metrics under realistic concurrency to catch, not reading the annotation on one method at a time. I'd recommend connection-pool monitoring (active/idle connection counts, wait-time-for-a-connection metrics) as the concrete early-warning signal for this class of problem, and I'd advocate for treating `REQUIRES_NEW` as something used deliberately and sparingly for specific, justified needs (genuinely independent-of-outer-outcome writes like audit logs) rather than a default reached for whenever "I want this to definitely commit" seems appealing — the far more common, safer default remains `REQUIRED`, precisely because it doesn't have this connection-multiplication cost.

**Source:** [Spring Framework Reference — Transaction Propagation](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/tx-propagation.html), [HikariCP — Pool Sizing](https://github.com/brettwooldridge/HikariCP/wiki/About-Pool-Sizing)

---

## 8. Why Does `@Transactional` Self-Invocation Fail?

**Answer:**

"This is the exact same proxy-based AOP mechanism and exact same failure mode covered in depth in the Spring Boot Internals file's self-invocation question, and in the Spring Security file's method-security version of it — `@Transactional` is implemented via a dynamic proxy (or CGLIB subclass) wrapping the bean, and the transaction-management logic (begin, commit, rollback) only runs when a call arrives **through that proxy** from *outside* the bean. A method calling another `@Transactional` method on `this` — via a plain, unqualified call, which always resolves to the raw, unproxied target object from inside the bean's own code — bypasses the proxy entirely, meaning the second method's `@Transactional` annotation has **zero effect**: no new transaction starts, no independent commit/rollback boundary is created, and it simply executes as part of whatever transactional context (or lack thereof) the *calling* method already established."

**Code:**

```java
@Service
class OrderService {

    public void placeOrder(Order order) {
        validate(order);
        saveWithNewTransaction(order); // SELF-INVOCATION — bypasses the proxy
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW) // NEVER actually gets
    public void saveWithNewTransaction(Order order) {         // its own independent
        orderRepository.save(order);                            // transaction when
    }                                                              // called this way —
}                                                                    // it just runs as
                                                                       // part of whatever
                                                                        // transaction (or none)
                                                                         // placeOrder() has

// FIX — same pattern as the other files: split into a separate bean, so the
// call genuinely crosses a proxy boundary from the outside
@Service
class OrderServiceFixed {
    private final TransactionalOrderWriter writer; // separate bean/collaborator

    public void placeOrder(Order order) {
        validate(order);
        writer.saveWithNewTransaction(order); // cross-bean call — proxy correctly applies
    }
}
```

**Follow-up:**

I'd flag that this is a particularly dangerous instance of the general self-invocation problem specifically because a `REQUIRES_NEW` self-invocation failure doesn't just silently skip an *optimization* (unlike a missed `@Cacheable`) — it silently changes the actual **atomicity and durability guarantees** of the code: a developer who wrote `saveWithNewTransaction` specifically to guarantee it commits independently of the caller's outcome (e.g., an audit log meant to survive the caller's later rollback) gets no such guarantee at all when reached via self-invocation, and the bug is invisible until the exact scenario the independent-commit guarantee was meant to protect against actually occurs in production — at which point the "guaranteed to survive" data is unexpectedly missing. I'd recommend the same ArchUnit-style static-analysis safeguard mentioned in the Spring Security file, specifically flagging any `@Transactional`-annotated method (especially non-`REQUIRED` propagation types) called from within its own class, given how severe and silent the resulting bug can be.

**Source:** [Spring Framework Reference — Understanding AOP Proxies](https://docs.spring.io/spring-framework/reference/core/aop/proxying.html#aop-understanding-aop-proxies)

---

## 9. What Happens When `@Transactional` Is Used on Private Methods?

**Answer:**

"By default, Spring's proxy-based AOP (both JDK dynamic proxies and CGLIB subclass proxies) can only intercept calls to **public** methods reachable through the proxy's exposed interface/subclass — a `private` method can never be called from outside the class at all (that's what `private` means at the language level), so there's no possible external call path for a proxy to intercept in the first place; the proxy mechanism structurally cannot wrap something that's only ever invoked via internal, same-class, `this`-based calls, which is itself just a specific case of the self-invocation problem from the previous question, except here it's not even possible to fix by calling from *outside* the class, since the method isn't accessible from outside at all.

The practical result: `@Transactional` on a `private` method is silently, completely ineffective — no exception is thrown, no warning is logged by default, the annotation simply does nothing at all, ever, for that method, since there is no call path into it that could ever go through the proxy."

**Code:**

```java
@Service
class OrderService {

    public void placeOrder(Order order) {
        saveInternal(order); // the ONLY possible call path to this method —
    }                          // a same-class, private-method call, which can
                                  // NEVER go through the proxy, structurally,
                                  // regardless of self-invocation avoidance tricks

    @Transactional // COMPLETELY INEFFECTIVE — there is no external call path
    private void saveInternal(Order order) { // to a private method AT ALL,
        orderRepository.save(order);            // so the proxy can never intercept it
    }
}

// FIX — the method must be public (or at minimum package-private/protected,
// depending on the proxy type, but public is the safe, universal choice) AND
// called from a DIFFERENT bean, not self-invoked, for @Transactional to apply
@Service
class OrderServiceFixed {
    public void placeOrder(Order order) {
        saveInternal(order);
    }

    @Transactional // now genuinely intercepted — public, AND called correctly
    public void saveInternal(Order order) { // (this specific example still has
        orderRepository.save(order);          // the self-invocation problem too —
    }                                            // BOTH issues need fixing together)
}
```

**Follow-up:**

I'd bring up that this is a genuinely good candidate for a compile-time or build-time lint check, since it's completely invisible at runtime (no exception, no log line by default) and only discoverable by noticing the *absence* of expected transactional behavior — a much harder bug to trace than one that throws. I'd also mention that AspectJ compile-time/load-time weaving (unlike Spring's default proxy-based AOP) *can* correctly intercept private methods, since it rewrites bytecode directly rather than relying on an external wrapping object — this is a legitimate, if heavier, mitigation worth knowing about for a codebase where this class of mistake keeps recurring, though I'd generally prefer fixing the actual method visibility and call pattern over reaching for a different, more complex AOP weaving strategy just to route around a fixable design issue.

**Source:** [Spring Framework Reference — Method Visibility and @Transactional](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html#transaction-declarative-annotations)

---

## 10. Which Exceptions Cause Rollback by Default?

**Answer:**

"Spring's default rollback rule is specifically: **unchecked exceptions** (any subclass of `RuntimeException`, plus `Error`) trigger a rollback automatically; **checked exceptions** (any subclass of `Exception` that isn't a `RuntimeException`) do **not** trigger a rollback by default — the transaction commits normally even if a checked exception propagates out of a `@Transactional` method, unless explicitly configured otherwise.

This default is inherited directly from the EJB specification's historical convention, and it genuinely surprises a lot of developers coming from a mental model of 'any exception should obviously roll back the transaction' — a checked exception representing a real business failure (an `InsufficientFundsException` declared as `extends Exception`, say) will, by Spring's default, still let the transaction commit, silently persisting whatever partial state existed at the point the exception was thrown, unless the method explicitly overrides the rollback rule via `@Transactional(rollbackFor = InsufficientFundsException.class)`. This is exactly why the practical convention in most Spring codebases is to make business/domain exceptions extend `RuntimeException` rather than checked `Exception` — sidestepping this default entirely by working with the grain of the framework's rollback behavior, rather than needing an explicit `rollbackFor` override scattered across every checked-exception-throwing transactional method."

**Code:**

```java
@Transactional
public void placeOrder(Order order) {
    orderRepository.save(order);
    if (insufficientInventory()) {
        throw new InsufficientInventoryException(); // if this is a CHECKED exception,
    }                                                    // the order save ABOVE still
}                                                           // COMMITS by Spring's default —
                                                              // a genuinely dangerous surprise

// Explicit override — makes a CHECKED exception trigger rollback anyway
@Transactional(rollbackFor = InsufficientInventoryException.class)
public void placeOrderExplicit(Order order) throws InsufficientInventoryException {
    orderRepository.save(order);
    if (insufficientInventory()) {
        throw new InsufficientInventoryException(); // NOW correctly rolls back
    }
}

// The generally-preferred convention — avoid the whole issue by making
// business exceptions unchecked, matching Spring's default rollback behavior
class InsufficientInventoryException extends RuntimeException { } // extends
// RuntimeException, not Exception — triggers rollback by DEFAULT, no
// rollbackFor override needed anywhere it's thrown
```

**Follow-up:**

I'd bring up that this default rollback rule's real danger is amplified by how *easy* it is to accidentally trigger, especially at an API/service boundary translating a lower-level exception into a domain-specific checked exception — a developer wrapping a caught exception into a custom checked exception for a "cleaner" method signature can unknowingly disable rollback for exactly the failure case they were trying to represent, with no error, warning, or test failure signaling the gap unless a test specifically asserts on database state after a failure path. I'd recommend, as a team-wide convention rather than a case-by-case decision, that all business/domain exceptions extend `RuntimeException`, and that any genuinely-needed checked exception crossing a `@Transactional` boundary be explicitly reviewed for its rollback implications — treating "does this exception correctly roll back the transaction" as a required part of code review for any new exception type introduced in transactional code, given how silent and easy-to-miss getting this wrong is.

**Source:** [Spring Framework Reference — Rollback Rules](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html#transaction-declarative-rolling-back)

---

## 11. Why Is Holding a Database Transaction Open During a Remote Call Dangerous?

**Answer:**

"This is the database-transaction-specific version of the exact same lock-scope discipline from the concurrency file's 'risks of calling external services while holding a lock' question, and it's arguably an even more severe version of it — a database transaction typically holds a checked-out connection from a finite pool *and* whatever row/table locks its writes have taken for the transaction's entire duration, both of which are now tied to the latency of a network call the application has zero control over.

If the remote call is slow (a downstream service degrading, a network blip, an unresponsive third party), the transaction — and its held connection and locks — stays open for however long that call takes, which can be far longer than any normal database operation would ever take on its own. This has compounding effects: the connection is unavailable to every other request needing one from the same pool for that entire duration, directly risking pool exhaustion under load (tying to question 7's dynamic, but here the trigger is external latency rather than nested transaction calls); and any row locks the transaction is holding block every *other* transaction that needs to touch those same rows, meaning a slow external call can effectively serialize otherwise-unrelated concurrent requests that happen to touch the same data, turning one slow downstream dependency into a much broader, harder-to-diagnose application-wide slowdown."

**Code:**

```java
// DANGEROUS — the transaction (and its connection, and any row locks) stays
// open for the ENTIRE duration of the external HTTP call
@Transactional
public void placeOrder(Order order) {
    Inventory inventory = inventoryRepository.findByIdForUpdate(order.getSku()); // ROW LOCK taken
    inventory.decrement(order.getQuantity());
    inventoryRepository.save(inventory);

    paymentGatewayClient.charge(order.getPaymentMethod(), order.getTotal()); // NETWORK CALL —
    // the row lock on `inventory` is held for however long THIS takes, blocking
    // every other transaction wanting to touch the same inventory row, and the
    // database connection is checked out from the pool the whole time too

    orderRepository.save(order);
}

// FIXED — do the DATABASE work under the transaction, commit it, THEN make
// the external call outside any transaction/lock scope
public void placeOrderFixed(Order order) {
    reserveInventory(order); // @Transactional — commits and releases the lock/connection
    PaymentResult result = paymentGatewayClient.charge(order.getPaymentMethod(), order.getTotal());
    finalizeOrder(order, result); // separate, SHORT @Transactional method
}
```

**Follow-up:**

I'd bring up that this is precisely why the "reserve inventory, then charge payment, then confirm" flow needs to be modeled as a saga (question 19/20) rather than one long-held database transaction spanning multiple external calls — the whole architectural point of a saga is to break a multi-step, multi-system operation into a sequence of independently-committing local transactions with compensating actions for failure, specifically *because* holding one database transaction open across multiple network calls (to a payment gateway, in this example) is both a severe reliability/scalability risk and, in a genuinely distributed system, often impossible in the first place (the payment gateway isn't part of your database and can't participate in the same ACID transaction anyway). I'd frame this as the direct, concrete motivation for why sagas exist as a pattern, not an abstract distributed-systems theory — this exact anti-pattern is the thing they're designed to replace.

**Source:** [Vlad Mihalcea — Why you should avoid transactions spanning multiple requests/calls](https://vladmihalcea.com/spring-transaction-best-practices/), [Chris Richardson — Saga Pattern](https://microservices.io/patterns/data/saga.html)

---

## 12. How Should Transaction Boundaries Align With Business Operations?

**Answer:**

"A transaction boundary should correspond to one complete, logically-atomic **business operation** — the smallest unit of work that genuinely needs 'all or nothing' semantics from the caller's/business's point of view, not an arbitrary technical or code-organizational boundary. 'Place an order' (validate, reserve inventory, record the order) is typically one business operation and should typically be one transaction; 'place an order' and 'send a confirmation email' are *not* the same business operation — the email send shouldn't be inside the same transaction (it's an external side effect with its own separate failure mode, tying to question 11, and a failed email send shouldn't roll back an otherwise-successful order).

The practical discipline I'd apply: transactions should be as **short** as correctness allows (long-held transactions cost connection-pool capacity and lock duration, tying to questions 7/11/4's vacuum discussion) but as **complete** as the business operation genuinely requires (a transaction that's too narrowly scoped risks leaving the business operation's own invariants only partially enforced — e.g., committing the inventory decrement in one transaction and the order record in a separate one invites exactly the kind of inconsistency atomicity exists to prevent, if the second transaction fails after the first already committed)."

**Code:**

```java
// TOO NARROW — the actual business operation "place an order" is split across
// two separate transactions, reintroducing exactly the atomicity gap ACID
// transactions exist to prevent WITHIN a single business operation
@Transactional
public void reserveInventoryOnly(Order order) { inventoryRepository.decrement(...); }
@Transactional
public void saveOrderOnly(Order order) { orderRepository.save(order); }
// if saveOrderOnly() fails after reserveInventoryOnly() already committed,
// inventory is decremented for an order that was NEVER actually recorded —
// a genuine, avoidable data-consistency bug from over-narrow transaction scoping

// CORRECTLY SCOPED — the actual atomic business operation, as ONE transaction
@Transactional
public void placeOrder(Order order) {
    inventoryRepository.decrement(order.getSku(), order.getQuantity());
    orderRepository.save(order); // both succeed or both roll back TOGETHER —
}                                    // exactly matching the real business invariant

// CORRECTLY EXCLUDED — the email send is a SEPARATE concern, not part of
// this transaction's atomicity requirement at all
@Transactional
public void placeOrderThenNotify(Order order) {
    placeOrder(order); // the atomic DB operation, as its own transaction
    // email sending happens AFTER commit, outside any transaction — e.g. via
    // an ApplicationEventPublisher + @TransactionalEventListener(phase = AFTER_COMMIT)
}
```

**Follow-up:**

I'd bring up `@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)` as the concrete Spring mechanism for correctly expressing "this side effect should happen only if, and only after, the business transaction actually commits" — decoupling the side effect (sending an email, publishing an event) from the transaction's own atomicity boundary while still guaranteeing it doesn't fire on a rolled-back operation. I'd also connect this question directly to the transactional outbox pattern (question 19) as the more rigorous version of the same underlying principle applied specifically to Kafka publication — "the side effect and the database change need to be atomic with each other, but the side effect itself (a network call, a message publish) can't safely be *inside* the same database transaction," and the outbox pattern is exactly how that tension gets resolved correctly rather than either accepting an inconsistency window or dangerously holding a transaction open across an external call.

**Source:** [Spring Framework Reference — Transactional Events](https://docs.spring.io/spring-framework/reference/data-access/transaction/event.html)

---

## 13. How Do Deadlocks Occur, and How Should an Application Respond?

**Answer:**

"A database deadlock occurs the same way an in-process lock deadlock does (covered at length in the concurrency file) — two or more transactions each hold a row/table lock the other needs, and each is blocked waiting for the other to release theirs, with no possible resolution without external intervention. The classic case: transaction A locks row 1 then wants row 2; transaction B locks row 2 then wants row 1 — neither can proceed.

Databases detect this automatically (via a wait-for graph, periodically checked for cycles) and resolve it themselves by choosing one transaction as the 'victim' — aborting it and rolling it back (typically the one that's done the least work, or by some other database-specific heuristic), throwing a specific, recognizable error (`deadlock detected` in PostgreSQL, a specific SQLState/error code in other databases) back to that transaction's caller, while letting the other transaction proceed normally. The correct application-level response is **not** to treat this as a generic failure — it's a specific, expected, and typically transient condition that the application should catch explicitly and **retry** the entire transaction from the beginning (not just the failed statement), since the transaction was aborted specifically to break the deadlock, and simply retrying it (usually against a database state that's no longer deadlocked, since the other transaction has since released its locks by committing or rolling back) very often succeeds the second time."

**Code:**

```java
@Retryable(
    retryFor = DeadlockLoserDataAccessException.class, // Spring's specific
    maxAttempts = 3,                                       // exception type for
    backoff = @Backoff(delay = 100, multiplier = 2)          // exactly this scenario
)
@Transactional
public void transferFunds(String fromAccount, String toAccount, BigDecimal amount) {
    // if THIS specific transaction is chosen as the deadlock "victim" by the
    // database, Spring translates the database's native deadlock error into
    // DeadlockLoserDataAccessException, and @Retryable retries the WHOLE
    // method (a fresh transaction attempt), not just one failed statement
    Account from = accountRepository.findByIdForUpdate(fromAccount);
    Account to = accountRepository.findByIdForUpdate(toAccount);
    from.debit(amount);
    to.credit(amount);
}
```

```sql
-- The database-level detection, PostgreSQL example: one of the two
-- transactions above gets THIS error, the OTHER proceeds normally:
ERROR: deadlock detected
DETAIL: Process 1234 waits for ShareLock on transaction 5678; blocked by process 5678.
        Process 5678 waits for ShareLock on transaction 1234; blocked by process 1234.
```

**Follow-up:**

I'd bring up that the actual, durable fix — same principle as the concurrency file's advice on in-process lock ordering — is enforcing a **consistent lock acquisition order** across every code path that takes multiple row locks in the same transaction (e.g., always locking accounts in ascending ID order, regardless of which account is logically "from" or "to" in a given call), which structurally prevents the circular-wait condition that causes deadlocks in the first place, rather than relying on retry-after-the-fact as the only mitigation. I'd frame retry as the correct *safety net* for deadlocks that do occur despite good lock-ordering discipline (some deadlocks are hard to fully eliminate in complex schemas with many interacting foreign keys/indexes), not as a substitute for actually designing lock acquisition order carefully in the first place — a system relying purely on retry-and-hope without any lock-ordering discipline will see deadlock rates scale badly with concurrency and schema complexity.

**Source:** [PostgreSQL Documentation — Deadlocks](https://www.postgresql.org/docs/current/explicit-locking.html#LOCKING-DEADLOCKS), [Spring Retry documentation](https://github.com/spring-projects/spring-retry)

---

## 14. How Would You Prevent Lost Updates?

**Answer:**

"Building directly on question 3's definition, prevention comes down to one of three approaches, each with a different trade-off, mirroring the exact same choice covered in the JPA/Hibernate file's optimistic-vs-pessimistic-locking questions and the REST API Design file's ETag mechanism — this is genuinely the same underlying problem showing up at three different layers of the stack.

**Atomic single-statement updates**: whenever the update is expressible as one SQL statement that reads and writes in the same atomic operation (`UPDATE accounts SET balance = balance - 100 WHERE id = 1`), there's no read-then-write gap at all for another transaction to race into — this is the simplest and, when applicable, the best fix, since it sidesteps the whole problem rather than detecting/preventing a race in a read-modify-write sequence.

**Optimistic concurrency control**: for updates that genuinely can't be expressed as one atomic statement (the new value depends on complex application logic, not just simple arithmetic on the current value), track a version/timestamp column and include it in the `WHERE` clause of the eventual update, failing loudly (zero rows affected) if another transaction changed the row first — exactly the `@Version` mechanism from JPA/Hibernate.

**Pessimistic locking**: take an explicit row lock (`SELECT ... FOR UPDATE`) at read time, preventing any other transaction from reading (for update) or writing that row until this transaction finishes — preventing the race outright rather than detecting it after the fact, at the cost of blocking concurrent access to that row for the transaction's duration."

**Code:**

```sql
-- Atomic single-statement update — no read-modify-write gap exists at all
UPDATE accounts SET balance = balance - 100 WHERE id = 1;

-- Optimistic concurrency — detects a conflict, doesn't prevent it outright
UPDATE accounts SET balance = 150, version = version + 1
  WHERE id = 1 AND version = 3; -- 0 rows affected if version has already
                                    -- moved on -> application must detect and react

-- Pessimistic locking — prevents the race by blocking concurrent access
BEGIN;
  SELECT balance FROM accounts WHERE id = 1 FOR UPDATE; -- other transactions
  -- wanting THIS row now BLOCK until this transaction commits/rolls back
  UPDATE accounts SET balance = 150 WHERE id = 1;
COMMIT;
```

**Follow-up:**

I'd give the practical decision rule directly: prefer the atomic single-statement update whenever the update logic is genuinely simple arithmetic/set-operations on the current value, since it's the cheapest and most foolproof option and requires no additional concurrency-control machinery at all; reach for optimistic locking when the update logic is more complex (multi-field, business-rule-driven) but conflicts are expected to be rare, accepting the cost of retry logic on the (uncommon) conflict case; reach for pessimistic locking specifically when conflicts are frequent enough that optimistic retries would themselves become a meaningful source of wasted work and latency, or when the cost of a failed/retried attempt is high enough that preventing the race outright is worth the reduced concurrency — this is the exact same decision framework from the JPA/Hibernate file's pessimistic-locking question, just stated at the raw-SQL level here rather than the ORM level.

**Source:** [PostgreSQL Documentation — Explicit Locking](https://www.postgresql.org/docs/current/explicit-locking.html)

---

## 15. Compare Optimistic and Pessimistic Concurrency Control

**Answer:**

"Optimistic concurrency control assumes conflicts are the exception, not the rule — it does no locking at read time at all, and instead detects a conflict at write time by checking whether the underlying data changed since it was read (a version number, timestamp, or full-row comparison), failing the write and requiring the application to reload and retry if a conflict is detected. This maximizes concurrency for the common (no-conflict) case, since reads never block anything, at the cost of wasted work and added complexity whenever a conflict genuinely does occur — the application has to handle the failure case explicitly (retry, or surface to a user).

Pessimistic concurrency control assumes conflicts are frequent enough to be worth actively preventing, taking a lock at read time that blocks any other transaction from concurrently reading (for a write lock) or writing the same data until the lock is released — this eliminates the possibility of a conflict occurring at all for the locked data, at the direct cost of reduced concurrency (other transactions genuinely wait) and the deadlock-risk considerations from question 13.

The decision, stated plainly: it's a trade-off between *optimizing for the common case being conflict-free* (optimistic) versus *guaranteeing no conflict can occur, at the cost of serializing contended access* (pessimistic) — and the right choice depends entirely on the actual, measured contention rate for the specific data/operation in question, not a general preference for one approach over the other."

**Code:**

```java
// Optimistic — no lock, detect-and-retry on conflict
@Entity
class Account {
    @Version Integer version; // JPA/Hibernate's built-in optimistic mechanism
}
// low contention scenario: reads never block, occasional retry on conflict
// is cheap relative to how rarely it actually happens

// Pessimistic — lock at read time, preventing conflicts outright
Account account = entityManager.find(Account.class, id, LockModeType.PESSIMISTIC_WRITE);
// high contention scenario (e.g., flash-sale inventory): every concurrent
// request to the SAME row queues up and waits its turn, rather than racing
// and retrying repeatedly under contention that would make retries themselves costly
```

**Follow-up:**

I'd bring up that this decision shouldn't be made once, globally, for an entire application — it's legitimately a **per-hot-path** decision, and a mature system often uses both simultaneously for different tables/operations based on each one's actual measured contention profile: optimistic locking as the default for most entities (low contention, typical CRUD), pessimistic locking specifically for the small number of genuinely hot, high-contention rows (a popular flash-sale item's inventory count, a shared counter/sequence). I'd also mention that under genuinely extreme contention, even pessimistic locking on a single row becomes a serialization bottleneck no locking strategy alone can fix — at that point the actual fix is usually architectural (sharding the hot counter across multiple rows and summing them, or moving the operation to a purpose-built high-throughput primitive like a Redis atomic counter, tying to the Redis/Caching category) rather than tuning the locking strategy further on a single, inherently-contended row.

**Source:** [PostgreSQL Documentation — Explicit Locking](https://www.postgresql.org/docs/current/explicit-locking.html), [Jakarta Persistence Specification §3.4 — Locking](https://jakarta.ee/specifications/persistence/3.1/jakarta-persistence-spec-3.1.html)

---

## 16. What Is Write Skew?

**Answer:**

"Write skew is a subtler anomaly than a simple lost update — it happens when two transactions each read some **overlapping but not identical** set of data, each independently makes a decision and writes to **different** rows based on what they read, and each individual write is perfectly valid *given what that transaction saw* — but the *combination* of both writes together violates an invariant that spans both rows, an invariant neither transaction's own write, in isolation, actually broke.

The textbook example: a hospital rule requires at least one doctor on call at all times; two doctors, A and B, are both on call; each independently checks 'am I allowed to go off call' by verifying at least one *other* doctor is still on call — both check, both see the other one is still on call (true, at the moment each checked), and both simultaneously go off call, since each transaction's own read and write are individually consistent with what it saw. The result: zero doctors on call, violating the invariant, even though neither individual transaction's write was 'wrong' given its own snapshot — this is fundamentally different from a lost update (which is about two writes to the *same* row), and it's specifically why write skew requires the **Serializable** isolation level (or explicit application-level locking of the *read set*, not just the rows being written) to prevent — weaker isolation levels, including Repeatable Read in the SQL-standard sense, don't protect against it, since each individual transaction's read and write, viewed in isolation, look perfectly consistent."

**Code:**

```sql
-- Write skew: TWO doctors, invariant "at least one on-call doctor exists"
-- Transaction A (Doctor 1 going off call)  Transaction B (Doctor 2 going off call)
BEGIN;                                       BEGIN;
SELECT COUNT(*) FROM doctors                 SELECT COUNT(*) FROM doctors
  WHERE on_call = true;                        WHERE on_call = true;
-- sees 2 (both still on call)               -- ALSO sees 2 (both still on call)
UPDATE doctors SET on_call = false            UPDATE doctors SET on_call = false
  WHERE id = 1;                                 WHERE id = 2;
COMMIT;                                       COMMIT;
-- BOTH commits succeed under Read Committed OR standard-Repeatable-Read —
-- each transaction's OWN write is individually consistent with what IT saw.
-- Final state: ZERO doctors on call — the invariant is violated, even though
-- neither transaction touched the SAME row the other one wrote to
```

**Follow-up:**

I'd bring up that this is exactly why PostgreSQL's actual Serializable implementation (Serializable Snapshot Isolation, SSI) exists as a distinct, additional mechanism beyond plain MVCC snapshotting — it specifically tracks read-write dependencies *between* concurrent transactions (not just conflicting writes to the same row) and aborts one of them if it detects a pattern that could produce a non-serializable outcome like write skew, even though no single row was written by both transactions. I'd also mention the practical application-level alternative when Serializable isolation isn't used or available: explicitly locking (or re-checking, within the same transaction, immediately before the write) the *entire read set* the invariant depends on, not just the specific row being written — in the doctors example, that would mean each transaction taking a lock on (or re-verifying, right before its own update, inside the same transaction) the *count* of on-call doctors, not just locking its own row, which is a subtler and easier-to-miss requirement than typical single-row locking intuition would suggest.

**Source:** [Martin Kleppmann — Designing Data-Intensive Applications, Ch. 7 (Write Skew)](https://dataintensive.net/), [PostgreSQL Documentation — Serializable Isolation Level](https://www.postgresql.org/docs/current/transaction-iso.html#XACT-SERIALIZABLE)

---

## 17. How Do Database Constraints Complement Application Validation?

**Answer:**

"Application-level validation is necessary but not sufficient as the *only* correctness guard, because it can be bypassed or made inconsistent in ways a database constraint structurally cannot: a second application instance with slightly different (or buggy, or not-yet-deployed) validation logic, a direct database access path (an ad hoc admin script, a data migration, another service sharing the same database), or a genuine race condition between two concurrent requests each individually passing application-level validation before either one's write actually lands (a classic check-then-act gap, similar in shape to write skew) — none of these are protected by application code alone, since application-level validation only runs within the specific code path that happens to execute it.

Database constraints (`NOT NULL`, `UNIQUE`, `FOREIGN KEY`, `CHECK`) act as the **last line of defense**, enforced by the database itself regardless of which application, code path, or concurrent race produced the write — they can't be bypassed by a code path that forgot to call the validation logic, and they're evaluated atomically as part of the same transaction attempting the write, closing exactly the kind of race-condition gap that pure application-level 'check first, then write' validation logic is structurally vulnerable to. The right mental model: application-level validation exists for **fast, specific, user-facing feedback** (a friendly 'that email is already taken' message before even attempting a write), while database constraints exist for **absolute, unbypassable correctness** — you want both, for different reasons, not one instead of the other."

**Code:**

```java
// Application-level validation — fast, good UX, but NOT sufficient alone
if (userRepository.existsByEmail(email)) {
    throw new EmailAlreadyExistsException(email); // nice, immediate feedback —
}                                                     // but a CONCURRENT request
userRepository.save(new User(email, ...));          // checking at the SAME moment
                                                        // could ALSO pass this check
                                                        // before either one's INSERT
                                                        // actually lands — a genuine race
```

```sql
-- The database constraint that ACTUALLY prevents the race, regardless of
-- what any application code did or didn't check beforehand
ALTER TABLE users ADD CONSTRAINT uq_users_email UNIQUE (email);
-- the SECOND concurrent INSERT, even if its application-level check passed,
-- gets a DataIntegrityViolationException from the database itself — the
-- constraint is the thing that ACTUALLY guarantees uniqueness, unconditionally
```

**Follow-up:**

I'd bring up the practical pattern this implies for handling the constraint-violation case gracefully rather than letting it surface as a raw, ugly database exception: catching the specific `DataIntegrityViolationException` (or its more specific subtype) at the application layer and translating it into the same friendly, user-facing error the application-level check was already producing for the common case — meaning both checks coexist deliberately: the application-level check for the fast, common-case UX, and the database constraint (with graceful exception handling wrapping it) as the actual, unbypassable correctness guarantee for the rare race-condition case the application check alone can't catch. I'd frame this as a general principle worth stating explicitly in any data-modeling discussion: any invariant that's genuinely required for correctness (not just a nice-to-have UX check) should have a database-level constraint enforcing it, full stop — relying purely on application code discipline for a true correctness invariant is a bet that every current and future code path touching that table will always get the check right, which is a bet that eventually loses as a system and its number of write paths grow.

**Source:** [PostgreSQL Documentation — Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)

---

## 18. How Do You Coordinate a Database Update and Kafka Publication?

**Answer:**

"This is the core distributed-consistency problem that motivates the entire rest of this category: a database and a Kafka broker are two entirely separate systems with no shared transaction coordinator by default, so there is no way to make 'commit this database row' and 'publish this Kafka message' happen as one truly atomic operation using ordinary means — whichever one you do second is always at risk of failing *after* the first one already succeeded, leaving the two systems inconsistent with each other (the database committed but no message was published, or a message was published but the database transaction that was supposed to precede it then rolled back).

The naive, broken approaches both fail in a specific, predictable way: publishing the Kafka message *before* committing the database transaction risks a message being published for a database change that then rolls back (consumers act on an event describing something that, from the database's perspective, never actually happened); committing the database transaction *first*, then publishing to Kafka, risks the application crashing (or the Kafka broker being briefly unreachable) in the gap between the two, silently losing the event entirely even though the database change is real and already committed. The correct, standard solution to this exact problem is the **transactional outbox pattern** (question 19) — writing the event to an outbox table as part of the *same* database transaction as the actual business data change (which the database genuinely can do atomically, since it's one transaction on one system), and having a separate, asynchronous process relay outbox rows to Kafka afterward, decoupling 'is the event durably and atomically recorded' (solved by the single-database-transaction) from 'has the event actually reached Kafka yet' (solved by the relay process retrying until it succeeds)."

**Code:**

```java
// BROKEN — publish before commit: message can describe a change that
// then ROLLS BACK, and consumers have no way to know that happened
@Transactional
public void placeOrder(Order order) {
    kafkaTemplate.send("order-events", new OrderPlacedEvent(order)); // published NOW
    orderRepository.save(order);
    if (someValidationFails()) {
        throw new ValidationException(); // rolls back the SAVE — but the Kafka
    }                                       // message ALREADY WENT OUT, describing
}                                             // an order that never actually persisted

// ALSO BROKEN — commit then publish: a crash/broker-unreachable gap between
// the two silently LOSES the event entirely, even though the DB change is real
@Transactional
public void placeOrderCommitFirst(Order order) {
    orderRepository.save(order);
} // transaction commits HERE — if the process crashes on the very next line,
  // below, the order is durably saved but NO event is EVER published
// kafkaTemplate.send("order-events", new OrderPlacedEvent(order)); // never runs
```

**Follow-up:**

I'd walk through exactly why "just retry the Kafka send if it fails" doesn't fully close the gap in the commit-first approach: retrying handles a *transient* publish failure, but it does nothing for the case where the *process itself* crashes (or is killed, or the pod is rescheduled) in the exact gap between the database commit and the retry logic even getting a chance to run — no in-memory retry mechanism survives a process crash, which is precisely why the outbox pattern's durability comes from writing the pending event to the *same database*, in the *same transaction*, rather than trying to make the Kafka publish itself more reliable through retries alone. I'd frame the outbox pattern as the answer specifically because it converts "atomically do two things across two different systems" (genuinely hard) into "atomically do one thing in one system" (a normal database transaction) plus "reliably, eventually relay already-durably-recorded data to a second system" (a much more tractable, retry-until-success problem, covered in question 19's implementation).

**Source:** [Chris Richardson — Transactional Outbox Pattern](https://microservices.io/patterns/data/transactional-outbox.html), [Debezium documentation — Outbox Event Router](https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html)

---

## 19. Explain the Transactional Outbox Pattern

**Answer:**

"The pattern solves question 18's problem by never trying to make a database write and a Kafka publish atomic with each other directly — instead, the application writes the event **to an outbox table in the same database**, as part of the *same* database transaction as the actual business data change. Since both writes (the business row and the outbox row) are ordinary rows in the same database, the database's own ACID guarantees make them atomic with each other for free — either both are committed together, or neither is, with no possibility of one succeeding without the other.

A **separate relay process** — either a polling job that periodically queries the outbox table for new, unpublished rows, or (the more common, more efficient modern approach) a **Change Data Capture** (CDC) tool like Debezium reading the database's own write-ahead log/replication stream directly — picks up newly-committed outbox rows and publishes them to Kafka, marking them as published (or deleting them) once the publish succeeds. Because the outbox row is already durably committed in the database *before* the relay ever attempts to publish it, a crash or failure at any point in the relay process is fully recoverable: the relay simply resumes from wherever it left off (the last successfully-published outbox row, or the CDC tool's own log-position checkpoint) and continues publishing whatever's left, with no possibility of silently losing an event the way the naive commit-then-publish approach could."

**Code:**

```java
@Transactional
public void placeOrder(Order order) {
    orderRepository.save(order); // business data change
    outboxRepository.save(new OutboxEvent(          // SAME transaction, SAME database —
        "OrderPlaced", order.getId(), serializeToJson(order))); // atomic with the save
} // BOTH commit together or NEITHER does — no possibility of one without the other
```

```sql
CREATE TABLE outbox_events (
    id UUID PRIMARY KEY,
    aggregate_type VARCHAR(255) NOT NULL,
    aggregate_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now()
    -- NOTE: no "published" flag needed at all with a CDC-based relay (Debezium) —
    -- the CDC tool reads the WAL directly and the row can simply be deleted
    -- after the INSERT is captured, rather than needing a polling/marking scheme
);
```

```text
Debezium CDC-based relay (the modern, generally-preferred approach over polling):

  Postgres WAL --> Debezium connector --> Kafka Connect --> Kafka topic

  - Debezium reads the database's write-ahead log DIRECTLY, capturing every
    INSERT into outbox_events as it's committed — no polling delay, no
    additional load on the outbox table from repeated SELECT polling
  - Debezium's "Outbox Event Router" SMT (single message transform) can
    unwrap the outbox row's own schema directly into the actual Kafka
    message shape, so consumers see a clean domain event, not a raw
    "outbox_events row" shape
```

**Follow-up:**

I'd bring up the polling-vs-CDC trade-off explicitly: a polling relay is simpler to build and reason about but adds latency (bounded by the poll interval) and repeated query load on the outbox table; a CDC-based relay (Debezium) has near-zero latency (reading the WAL as changes happen) and doesn't add polling load, but introduces a genuinely more complex piece of infrastructure (a Kafka Connect cluster, Debezium connector configuration, its own operational monitoring needs) that has to be built, deployed, and kept healthy as a first-class production dependency in its own right. I'd also mention that the outbox table needs its own cleanup/retention strategy regardless of relay mechanism (old, already-published rows shouldn't accumulate forever, tying to the general table-bloat/vacuum concerns from question 4), and that this pattern is precisely how the cross-stack design scenario "a service sometimes publishes events without committing its database update" gets fixed architecturally — the outbox table's atomicity with the business write is the structural guarantee that makes that failure mode impossible by construction, rather than something handled by more careful error-handling code around a direct publish call.

**Source:** [Chris Richardson — Transactional Outbox Pattern](https://microservices.io/patterns/data/transactional-outbox.html), [Debezium documentation](https://debezium.io/documentation/reference/stable/index.html)

---

## 20. How Do Outbox Relays Handle Duplicate Publication?

**Answer:**

**"They don't fully prevent it — and they're not designed to; instead, the outbox pattern (and the systems built on top of it) accept 'at-least-once' delivery as the realistic guarantee and push the responsibility for handling duplicates onto consumers, rather than trying to achieve true exactly-once delivery at the relay/publish layer itself.** Concretely: if the relay process crashes or fails *after* successfully publishing a message to Kafka but *before* it manages to mark that outbox row as published (or delete it), the relay will, upon recovery, see that row as still 'unpublished' and publish it again — a genuine duplicate, arriving on the Kafka topic a second time. This gap is fundamentally unavoidable without a true, distributed two-phase-commit-style protocol between the outbox database and Kafka (which the pattern deliberately avoids, precisely because 2PC has its own severe availability costs, question 22), so the pattern instead treats duplicate delivery as an accepted, expected possibility.

The actual mitigation is downstream: consumers of events produced via an outbox relay must be **idempotent** (question 25 covers consumer idempotency directly) — capable of safely processing the exact same event twice without a duplicated side effect, typically by tracking processed event IDs (the outbox event's own UUID, generated once and included as part of the event payload, is exactly the natural idempotency key for this) and skipping/no-op'ing an already-processed event ID on a second delivery."

**Code:**

```java
// The event's OWN id, generated ONCE when the outbox row is created, becomes
// the natural idempotency key for consumers — regardless of how many times
// the relay might redeliver this specific event due to a crash-before-ack
@Transactional
public void placeOrder(Order order) {
    orderRepository.save(order);
    UUID eventId = UUID.randomUUID(); // generated ONCE, here — stable across
    outboxRepository.save(new OutboxEvent(eventId, "OrderPlaced", ...)); // any redelivery
}

// Consumer-side idempotency, using that same stable event id
@KafkaListener(topics = "order-events")
void handleOrderPlaced(OrderPlacedEvent event) {
    if (processedEventRepository.existsById(event.getEventId())) {
        return; // ALREADY processed this exact event id — safe no-op on a duplicate
    }
    // process normally, then record this event id as processed —
    // atomically, in the SAME transaction as the actual processing work,
    // for the same reason the outbox pattern itself needs same-transaction atomicity
    processOrder(event);
    processedEventRepository.save(new ProcessedEvent(event.getEventId()));
}
```

**Follow-up:**

I'd bring up that this is exactly the concrete instance of Kafka's broader "why must consumers remain idempotent even when Kafka transactions are used" principle from the Kafka/Messaging category — the outbox pattern's relay-side duplicate risk is just one specific *source* of duplicate delivery among several (producer retries, consumer rebalances re-processing uncommitted offsets), and the fix is the same regardless of the specific source: idempotent consumers, not trying to eliminate every possible duplicate-delivery cause at the producing/relaying side, since that's an unbounded and ultimately unwinnable game across a genuinely distributed system. I'd also mention that "mark as published, then delete/flag the outbox row" itself needs to happen as its own transaction distinct from the original business-write transaction (it happens later, in the relay process, not atomically with the original save) — and getting the ordering right here (publish first, then mark-as-published, accepting the crash-after-publish-before-mark gap as the acceptable at-least-once risk, rather than mark-as-published-first-then-publish, which would risk the opposite, worse failure of marking something published that never actually made it to Kafka at all) is a subtle but important implementation detail.

**Source:** [Chris Richardson — Transactional Outbox Pattern](https://microservices.io/patterns/data/transactional-outbox.html), [Confluent — Idempotent Consumer Pattern](https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/)

---

## 21. Why Does Kafka Exactly-Once Processing Not Automatically Include a Relational Database?

**Answer:**

"Kafka's exactly-once semantics (transactional producers, idempotent producers, transactional consumers reading only committed offsets) are scoped **entirely within Kafka's own ecosystem** — they guarantee that a producer's writes across multiple Kafka partitions/topics, combined with a consumer's offset commits, behave atomically *with respect to Kafka itself*. This says nothing at all about, and provides no coordination mechanism for, any *external* system a consumer might also write to while processing a message — a relational database write performed inside a Kafka consumer's message-handling logic is entirely outside the scope of Kafka's own transactional coordinator, since that coordinator has no visibility into or control over the database at all.

Concretely: a consumer that reads a message, writes to a database, and commits its Kafka offset is doing three logically-related operations across two entirely separate systems (Kafka's offset-commit mechanism, and the database's own transaction), and there's no built-in, automatic way to make 'commit the database write' and 'commit the Kafka offset' atomic with each other — the consumer could crash after the database write commits but before the offset commit succeeds (resulting in that message being re-delivered and re-processed on restart, a duplicate from the database's perspective unless the consumer is idempotent), or, less commonly depending on commit ordering, the reverse gap. This is exactly why the general principle 'consumers must be idempotent regardless of Kafka's own delivery guarantees' (question 8 in the Kafka category, and question 20 here) holds even when a system is using Kafka's transactional/exactly-once features to their fullest — those features solve the Kafka-internal half of the problem, not the Kafka-to-external-system half."

**Code:**

```java
@KafkaListener(topics = "order-events")
@Transactional // this transaction covers the DATABASE write ONLY —
void handleOrderPlaced(OrderPlacedEvent event) { // it has NO relationship to,
    orderProcessedRepository.save(new ProcessedOrder(event)); // and cannot
} // coordinate with, Kafka's OWN internal offset-commit mechanism at all —

// even with Kafka's "exactly-once" consumer configuration enabled:
// isolation.level=read_committed
// enable.auto.commit=false  (manual, offset committed AFTER processing)

// there is STILL a gap: crash between the @Transactional database commit
// above and the SUBSEQUENT Kafka offset commit means this message gets
// RE-DELIVERED on restart — a duplicate, from the DATABASE's perspective,
// regardless of how "exactly-once" Kafka's own internal machinery is
```

**Follow-up:**

I'd bring up that genuinely atomic "Kafka offset commit + external database write" coordination *is* theoretically achievable via distributed transactions (XA/2PC, question 22) spanning both systems, but this is rarely done in practice — it requires both the database and the Kafka client to support and correctly implement the two-phase commit protocol together, adds significant latency and availability cost (2PC's coordinator becomes a single point of blocking failure for both systems), and is exactly the kind of heavyweight distributed-transaction machinery that sagas and idempotent-consumer patterns exist specifically to avoid needing. I'd frame the practical, almost-universally-adopted industry answer as: don't try to make the database write and the Kafka offset commit atomic with each other at all — instead, make the database write **idempotent** (track processed event IDs, as in question 20), and accept that a message might be redelivered and reprocessed after a crash, relying on idempotency rather than cross-system atomicity to achieve the correct end result.

**Source:** [Confluent — Exactly-Once Semantics in Apache Kafka](https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/), [Kafka Documentation — Transactions](https://kafka.apache.org/documentation/#semantics)

---

## 22. What Is a Distributed Transaction, and Why Is Two-Phase Commit Often Avoided?

**Answer:**

"A distributed transaction is a single logical transaction whose operations span **multiple, independent systems** (two different databases, a database and a message broker, two different microservices each with their own database) — all of which need to either all commit together or all roll back together, exactly like a single-database ACID transaction, but now coordinated across systems that don't share a single transaction log or lock manager.

**Two-phase commit (2PC)** is the classical protocol for this: a coordinator asks every participant to 'prepare' (do all the work, acquire all necessary locks, and durably record 'ready to commit' — but not actually commit yet); once *every* participant confirms it's prepared, the coordinator tells all of them to actually commit; if any participant fails to prepare, the coordinator tells everyone to roll back instead.

It's avoided in most modern distributed-systems designs for a few serious, practical reasons: **it's blocking** — every participant holds its locks/resources from the 'prepare' phase all the way until it receives the coordinator's final commit/rollback instruction, and if the coordinator itself crashes or becomes unreachable in between those two phases, every participant is stuck holding its locks indefinitely, unable to safely proceed in either direction on its own (this is the 'in-doubt transaction' problem, and it can genuinely freeze resources across multiple systems for as long as the coordinator remains unavailable). It also **requires every participant to support the 2PC protocol** (XA-compliant drivers/systems), which many modern systems — Kafka included — either don't support at all or support only awkwardly. And it fundamentally **couples the availability of every participating system together** — the whole point of independent services with independent databases is that one system's outage shouldn't block another's ability to make progress, and 2PC directly reintroduces exactly that coupling, undermining a core benefit of a distributed architecture in the first place."

**Code:**

```text
2PC, illustrating the blocking failure mode:

  Coordinator -> Database A: PREPARE   -> A: "ready" (locks held, waiting)
  Coordinator -> Database B: PREPARE   -> B: "ready" (locks held, waiting)

  Coordinator CRASHES here, before sending the final COMMIT to either participant

  Database A: still holding its locks, waiting INDEFINITELY for a commit/
              rollback instruction that may never come until the coordinator
              recovers — this is the "in-doubt transaction" problem
  Database B: same situation — BOTH systems are now stuck, blocking whatever
              else needed those locked resources, for as long as the
              coordinator remains down
```

**Follow-up:**

I'd bring up that 2PC isn't *never* used — it genuinely exists and is supported in specific enterprise contexts (some legacy JMS/JTA-based Java EE systems, certain financial systems with strict, non-negotiable cross-system atomicity requirements and a controlled, reliable coordinator infrastructure) — but the modern consensus, especially for cloud-native/microservices architectures, strongly favors avoiding it in favor of the saga pattern (question 23) specifically because sagas trade strict atomicity for availability and loose coupling, accepting eventual consistency and explicit compensation logic instead of a blocking, tightly-coupled cross-system commit protocol. I'd frame the actual decision as a real instance of the broader CP-vs-AP trade-off from distributed systems theory (CAP-theorem-adjacent, though not identical) — 2PC prioritizes strict consistency at the cost of availability during coordinator/participant failure; sagas prioritize availability and independent service operation, accepting a temporary inconsistency window that compensating actions are designed to resolve.

**Source:** [Pat Helland — Life Beyond Distributed Transactions](https://cidrdb.org/cidr2007/papers/cidr07p15.pdf), [Chris Richardson — Saga Pattern](https://microservices.io/patterns/data/saga.html)

---

## 23. Explain the Saga Pattern and Compensating Transactions

**Answer:**

"A saga is a sequence of **local transactions**, each in a single service/database, where each step's success triggers the next step, and — critically — each step that has a real-world effect worth undoing has an associated **compensating transaction**: a separate, explicit operation that semantically reverses that step's effect, used if a *later* step in the sequence fails and the whole saga needs to be unwound.

This is fundamentally different from a rollback in the ACID sense — a compensating transaction doesn't undo the original step at the database-transaction level (that original transaction already committed, independently, and is done); it performs a **new, forward-moving transaction** that achieves the equivalent of 'undo,' semantically (refunding a payment that was already charged, releasing inventory that was already reserved, cancelling a shipment that was already scheduled) — precisely because each step in a saga commits independently and there's no single, spanning transaction left open across the whole sequence to roll back in the traditional sense once several steps have already committed.

This trades strict, database-style atomicity (2PC's guarantee) for availability and loose coupling between services — each service only ever needs its own local database transaction, never a cross-service lock or blocking coordinator — at the cost of the system passing through genuinely inconsistent intermediate states during a saga's execution (inventory reserved but payment not yet confirmed, for instance) that the rest of the system needs to be explicitly designed to tolerate or hide from users until the saga fully completes."

**Code:**

```text
Order Placement Saga:

  Step 1: Reserve Inventory     (local txn, service: Inventory)
  Step 2: Charge Payment        (local txn, service: Payment)
  Step 3: Confirm Order         (local txn, service: Order)

  If Step 2 (Charge Payment) FAILS:
    Compensating action: Release Inventory  <-- a NEW, forward transaction,
    -- NOT a rollback of Step 1's already-committed transaction — Step 1
    -- genuinely happened and committed; this compensates for it afterward

  If Step 3 (Confirm Order) FAILS, after Steps 1 and 2 already succeeded:
    Compensating actions, in REVERSE order:
      - Refund Payment       (compensates Step 2)
      - Release Inventory    (compensates Step 1)
```

```java
@Saga
class OrderPlacementSaga {
    void reserveInventory(Order order) { inventoryClient.reserve(order); }
    void compensateReserveInventory(Order order) { inventoryClient.release(order); }

    void chargePayment(Order order) { paymentClient.charge(order); }
    void compensateChargePayment(Order order) { paymentClient.refund(order); }
    // a saga ORCHESTRATOR (question 24) tracks which steps have completed
    // and invokes compensations, in REVERSE order, if a later step fails
}
```

**Follow-up:**

I'd bring up that not every step is compensable, and that's a genuine design constraint sagas have to be built around explicitly, not an edge case to handle later — an email that's already been sent can't be un-sent (question 30 in this category covers exactly this "compensation impossible" case), so a saga's design has to either order genuinely irreversible steps **last** (after every reversible step has already succeeded, minimizing the chance a later failure would need to "un-send" something un-sendable) or accept and explicitly design for the residual risk that an irreversible action might occasionally need a different kind of remediation (a follow-up corrective email, a manual customer-service intervention) rather than a clean, automatic compensating transaction. I'd also mention idempotency as a requirement for compensating transactions themselves, not just the forward steps — a compensation that gets triggered twice (due to a retry, or an orchestrator restarting after a crash mid-saga) needs to be safe to execute twice without, say, double-refunding a payment.

**Source:** [Chris Richardson — Saga Pattern](https://microservices.io/patterns/data/saga.html), [Hector Garcia-Molina & Kenneth Salem — Sagas (original 1987 paper)](https://www.cs.cornell.edu/andru/cs711/2002fa/reading/sagas.pdf)

---

## 24. Compare Choreography and Orchestration Sagas

**Answer:**

"**Choreography** has no central coordinator at all — each service, upon completing its own local transaction, publishes an event, and the *next* service(s) in the logical sequence independently subscribe to and react to that event, triggering their own local transaction and publishing their own resulting event in turn. The saga's overall flow emerges from this decentralized chain of event publication and reaction, with no single place that 'knows' the whole sequence.

**Orchestration** has an explicit, central orchestrator component that directly knows the entire saga's sequence of steps and compensations, explicitly invoking each participating service in turn (via direct calls or commands) and explicitly deciding, based on each step's outcome, whether to proceed to the next step or begin invoking compensations in reverse order.

The trade-off: choreography keeps services more loosely coupled (no service needs to know about the orchestrator, or even that it's participating in a larger saga at all — it just reacts to events it's already subscribed to) and avoids a potential single point of failure/bottleneck in an orchestrator, but the overall saga's logic becomes genuinely hard to see, reason about, monitor, or debug as a whole — there's no single place to look to understand 'what does this business process actually do end-to-end,' and adding a new step means adding new event subscriptions scattered across multiple services rather than one centralized change. Orchestration keeps the saga's logic centralized, explicit, and easy to reason about, test, and modify as one cohesive unit, at the cost of the orchestrator becoming a genuine dependency every participating step now has (tighter coupling to the orchestrator specifically, and a component whose own availability/correctness the whole saga now depends on)."

**Code:**

```text
CHOREOGRAPHY — no central coordinator, services react to each other's events:

  Order Service --publishes--> OrderCreated
                                    |
                                    v
  Inventory Service (subscribes to OrderCreated) --publishes--> InventoryReserved
                                                                     |
                                                                     v
  Payment Service (subscribes to InventoryReserved) --publishes--> PaymentCharged
  -- no single place shows this ENTIRE flow; it's implicit in each
  -- service's own event subscriptions, scattered across the codebase

ORCHESTRATION — one component explicitly drives the whole sequence:

  OrderSagaOrchestrator:
    1. call Inventory.reserve()   -> on failure: done, nothing to compensate yet
    2. call Payment.charge()      -> on failure: call Inventory.release() [compensate]
    3. call Order.confirm()       -> on failure: call Payment.refund(),
                                                     Inventory.release() [compensate, reverse order]
  -- the ENTIRE flow, including every compensation, is visible in ONE place
```

**Follow-up:**

I'd give a practical recommendation rather than presenting these as equally good in all cases: for sagas with more than a small handful of steps, or with non-trivial compensation logic, I'd generally favor orchestration specifically *because* of its debuggability and the ability to actually see and test the whole business process as one unit — choreography's decentralization sounds appealing architecturally but tends to become genuinely difficult to operate in practice once a saga has more than 2-3 steps, since understanding "why did this order get stuck in a weird state" requires tracing event flows across several services' independent subscription logic rather than reading one orchestrator's code. I'd reserve choreography for genuinely simple, small sagas (2 steps, minimal/no compensation needed) where the loose-coupling benefit clearly outweighs the lost visibility, and I'd note that a dedicated orchestration framework (Temporal, Camunda, AWS Step Functions, or a simpler in-house state-machine-based orchestrator) is usually worth adopting for orchestration-based sagas rather than hand-rolling the state-tracking and compensation-invocation logic from scratch, given how easy it is to get the failure/retry/compensation-ordering logic subtly wrong by hand.

**Source:** [Chris Richardson — Saga Pattern (Choreography vs Orchestration)](https://microservices.io/patterns/data/saga.html), [Temporal documentation](https://docs.temporal.io/)

---

## 25. How Would You Design Idempotency for a Transactional Consumer?

**Answer:**

"The core mechanism, as touched on in question 20, is tracking which specific messages have already been fully processed, keyed by a stable identifier that's the same across any redelivery of the *same* logical message — and critically, that tracking has to happen **atomically with the actual processing side effect itself**, in the same local database transaction, or you reintroduce exactly the same 'two things need to happen together but might not' gap the outbox pattern exists to solve, just one layer further down the pipeline.

Concretely: the consumer, upon receiving a message, checks (within the same transaction as the processing work it's about to do) whether this message's ID has already been recorded as processed; if so, it's a duplicate delivery and the consumer should no-op (or, depending on the operation, safely re-return whatever result it produced the first time, mirroring the idempotency-key pattern from the REST API Design file's payment-retry question — this is genuinely the same underlying pattern, applied to message consumption instead of HTTP requests); if not, it performs the actual business logic **and** records the message ID as processed, both within that same single database transaction, so either both happen (processed exactly once, from the database's point of view) or neither does (a crash mid-processing rolls back both the business effect and the "processed" marker together, correctly leaving the message eligible for a legitimate retry)."

**Code:**

```java
@KafkaListener(topics = "payment-requests")
@Transactional // covers BOTH the idempotency check/record AND the actual
void handlePaymentRequest(PaymentRequestEvent event) { // business effect, atomically
    if (processedMessageRepository.existsById(event.getMessageId())) {
        return; // duplicate delivery — safe no-op, message already fully handled
    }

    paymentService.charge(event.getAccountId(), event.getAmount()); // the actual
    // side effect — happens EXACTLY ONCE across any number of redeliveries,
    // because it's atomic (same DB transaction) with the marker below

    processedMessageRepository.save(new ProcessedMessage(event.getMessageId()));
    // BOTH the charge above AND this marker commit together, or NEITHER does —
    // a crash between them is impossible by construction (same transaction);
    // a crash BEFORE either commits just means a legitimate, safe-to-retry redelivery
}
```

**Follow-up:**

I'd bring up that the message ID used for this check has to be genuinely stable and unique across redeliveries specifically — if the message ID is generated fresh by the producer on every send (rather than once, at the point the underlying business event was first created, as in the outbox pattern's approach from question 20), a producer-side retry that resends the "same" logical message with a *new* ID would defeat the whole idempotency mechanism, since the consumer would see it as a genuinely new, never-before-seen message. I'd also mention that for very high-throughput consumers, the processed-message-tracking table itself needs its own retention/cleanup strategy (old entries can eventually be purged once they're old enough that no realistic redelivery window could still produce a duplicate for them) — an unbounded, ever-growing "processed messages" table is a real, if slow-building, operational cost worth planning for from the start rather than discovering as a table-bloat problem months into production.

**Source:** [Confluent — Idempotent Consumer Pattern](https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/), [Chris Richardson — Idempotent Consumer](https://microservices.io/patterns/communication-style/idempotent-consumer.html)

---

## 26. How Do You Safely Retry a Failed Transaction?

**Answer:**

"Safe retry requires first classifying *why* the transaction failed, since the correct response differs completely depending on the failure category — retrying blindly regardless of cause is itself a common source of bugs. **Transient infrastructure failures** (a deadlock victim, question 13; a brief connection-pool exhaustion; a momentary network blip to the database) are the genuinely safe-to-retry category — the transaction's own logic wasn't wrong, an external, temporary condition prevented it from completing, and retrying the *entire* transaction from the beginning (not just a partial resumption) against a now-hopefully-recovered environment is the correct response. **Business-rule/validation failures** (insufficient inventory, a failed fraud check, a genuinely invalid request) are **not** safe to blindly retry — retrying the exact same operation against the exact same invalid input will simply fail again, identically, and blind retry logic here just wastes resources and potentially confuses monitoring/alerting with repeated, predictable failures that were never going to succeed.

For the safe-to-retry category, the discipline mirrors the REST API Design file's retry guidance directly: retry with **exponential backoff and jitter**, bounded by a maximum attempt count or total time budget, and critically, ensure the retried operation is itself **idempotent** or safely re-attemptable from scratch — a transaction that's partially, silently non-idempotent (e.g., it sends a non-transactional side effect like an email partway through, before the point of failure) can't simply be re-run wholesale without risking that side effect happening twice, which is exactly why question 27's 'when might a retry repeat an external side effect' is such an important companion consideration to this one."

**Code:**

```java
@Retryable(
    retryFor = { DeadlockLoserDataAccessException.class, TransientDataAccessException.class },
    noRetryFor = { ValidationException.class, InsufficientInventoryException.class }, // NEVER
    maxAttempts = 3,                                                                     // retry
    backoff = @Backoff(delay = 100, multiplier = 2, maxDelay = 2000)                     // these —
)
@Transactional
public void processPayment(PaymentRequest request) {
    validateRequest(request); // throws ValidationException on bad input —
    // explicitly excluded from retry above, since retrying identical bad
    // input will just fail identically every time, wasting attempts

    Account account = accountRepository.findByIdForUpdate(request.getAccountId());
    account.debit(request.getAmount()); // if THIS specifically fails due to a
    // transient deadlock (question 13), the WHOLE method retries from the top —
    accountRepository.save(account);       // safe here because nothing in this
}                                             // specific method has a non-idempotent
                                                // external side effect
```

**Follow-up:**

I'd bring up that the safest transactions to retry are ones designed with retry in mind from the start — no external, non-idempotent side effects inside the transactional method itself (question 12's guidance on keeping side effects outside transaction boundaries directly supports this), and any writes performed being naturally idempotent or protected by the same idempotency-key mechanism covered in questions 20/25, so that even an *accidental* double-execution (a retry that fires when the original attempt actually had succeeded, but the success signal was lost) doesn't cause a duplicated real-world effect. I'd frame this as the practical reason "design for retry from the start" is a better principle than "add retry logic to existing code as an afterthought" — retrofitting safe retry onto a transaction that wasn't designed with idempotency/side-effect-isolation in mind often requires restructuring the operation anyway, so it's cheaper to get right the first time than to bolt on carefully later.

**Source:** [Spring Retry documentation](https://github.com/spring-projects/spring-retry), [AWS Architecture Blog — Exponential Backoff and Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)

---

## 27. When Might a Retry Repeat an External Side Effect?

**Answer:**

"Any time a transaction includes a call to something **outside the local database transaction's own rollback scope** — an external HTTP call, a Kafka publish (unless it's specifically going through an outbox, question 19, which is exactly designed to bring it *inside* the local transaction's atomicity), a file write, an email send — that external effect does **not** automatically roll back if the surrounding database transaction later fails or is retried, because it was never actually part of that transaction's atomic scope in the database sense at all; it's a real-world action that already happened, independent of what the database later decides to do.

This creates a specific, dangerous window: if a transaction performs an external side effect, and *then* fails for some unrelated reason further down in the same method (triggering a retry of the *whole* transaction), the retry re-executes everything from the top **including the external side effect**, which already genuinely happened once and is now happening again — a duplicate charge, a duplicate email, a duplicate downstream API call — even though the *database* portion of the original attempt was correctly rolled back and is being correctly retried from a clean state."

**Code:**

```java
// DANGEROUS — external call happens INSIDE the retried transaction; a retry
// re-executes the external call too, even though only the DATABASE portion
// actually needed to be redone
@Retryable(retryFor = TransientDataAccessException.class, maxAttempts = 3)
@Transactional
public void placeOrder(Order order) {
    paymentGatewayClient.charge(order.getPaymentMethod(), order.getTotal()); // EXTERNAL —
    // does NOT roll back if the line below throws, and WILL be repeated if
    // this whole method retries due to a transient database issue

    orderRepository.save(order); // if THIS specifically throws a transient
    // DB exception, the @Retryable annotation retries the ENTIRE method —
    // including the payment charge above, which will be charged a SECOND TIME
}

// FIXED — separate the external call from the retried database transaction
// entirely, using an idempotency key (question 5 in REST API Design; question
// 25 here) so even an intentional retry of the EXTERNAL call itself is safe
public void placeOrderFixed(Order order) {
    String idempotencyKey = order.getIdempotencyKey(); // generated ONCE, stable
    PaymentResult result = paymentGatewayClient.charge( // across any retry of
        order.getPaymentMethod(), order.getTotal(), idempotencyKey); // THIS call

    saveOrderWithRetry(order, result); // ONLY the database portion is
}                                          // wrapped in @Retryable/@Transactional —
                                             // retrying it never re-triggers the
                                             // external charge, which already
                                             // completed (and is itself idempotent
                                             // if IT needs to be retried independently)
```

**Follow-up:**

I'd frame the general architectural rule this motivates explicitly: external, non-idempotent side effects should be **structurally separated** from the database transaction they're logically associated with — either performed and confirmed *before* the transaction that records the result (as in the fixed example, where the payment is confirmed first, and only the database recording is subject to retry), or deferred entirely via the outbox pattern so the side effect is itself made idempotent-safe and decoupled from any retry of the local transaction. I'd also connect this back to question 11's "never hold a transaction open across a remote call" guidance — that's about the transaction's *lock duration*, this question is about the transaction's *retry safety*, but they're both symptoms of the same root design smell: an external call embedded inside a database-transactional method, which is dangerous for at least two independent reasons (lock/connection duration, AND retry-duplication risk), reinforcing why "external calls don't belong inside a `@Transactional`/`@Retryable` boundary" is a strong, broadly-applicable design principle rather than a narrow fix for one specific symptom.

**Source:** [Spring Retry documentation](https://github.com/spring-projects/spring-retry), [Stripe API — Idempotent Requests](https://stripe.com/docs/api/idempotent_requests)

---

## 28. How Would You Investigate Transactions That Remain Open for Several Minutes?

**Answer:**

"First step is identifying the actual long-running transactions and what they're doing/waiting on, using the database's own introspection tools rather than guessing from application logs alone — PostgreSQL's `pg_stat_activity` view, filtered by `state` and `xact_start`, shows exactly which sessions have transactions open, for how long, and what query (if any) they're currently executing (or whether they're `idle in transaction`, which is its own specific and very common culprit, covered below).

The most common real-world root causes, roughly in likelihood order: **`idle in transaction`** — a transaction that began, ran some queries, and is now sitting open with the application doing something else entirely (waiting on a slow external call held inside a transaction, exactly question 11's anti-pattern; a bug where a transaction is opened but a code path forgets to commit/rollback and return the connection; a debugger breakpoint hit mid-transaction during a manual investigation, accidentally left paused) — this is the single most damaging case, since it holds locks and a connection while doing *zero* actual database work, for however long the surrounding code takes. **A genuinely long-running query** — a missing index, a full table scan, or a poorly-optimized query that's actually still executing, tying back to the JPA/Hibernate file's query-diagnosis question. **Batch processing without periodic commits** — a job processing millions of rows within a single, unbroken transaction (tying to the JPA/Hibernate file's batch-processing question) rather than committing in bounded chunks."

**Code:**

```sql
-- PostgreSQL: find long-running transactions and WHAT they're currently doing
SELECT pid, state, xact_start, now() - xact_start AS transaction_duration,
       query, wait_event_type, wait_event
FROM pg_stat_activity
WHERE state != 'idle' OR state = 'idle in transaction'
ORDER BY xact_start ASC;

-- "idle in transaction" specifically is the most dangerous pattern —
-- a transaction holding locks/a connection while doing ABSOLUTELY NOTHING,
-- because the APPLICATION is off doing something else (a slow external
-- call, a bug, a forgotten commit) with the transaction still open
```

```properties
# A real, practical safeguard — kills sessions idle-in-transaction past a
# threshold, since a legitimate transaction almost never NEEDS to sit idle
# for this long; this is a safety net catching bugs/anti-patterns, not
# something well-designed transactional code should ever actually trigger
idle_in_transaction_session_timeout = 30s  # postgresql.conf
```

**Follow-up:**

I'd bring up `idle_in_transaction_session_timeout` as a genuinely valuable, defensive production safeguard worth setting proactively (not just reaching for during an active incident) — it won't fix the underlying application bug that left a transaction idle (an external call inside a transaction boundary, a forgotten commit), but it bounds the *damage* any single occurrence of that bug can do, automatically terminating the offending session after a threshold rather than letting it hold locks/a connection indefinitely until someone manually notices and intervenes. I'd also mention that this exact investigation — `pg_stat_activity`, sorted by transaction duration, cross-referenced against application logs/traces for whatever request/job correlates with the offending PID's start time — is precisely the diagnostic path for the cross-stack design scenario "a low-latency service has periodic pauses" when the root cause turns out to be database-side lock contention from a long-held transaction elsewhere in the system, rather than anything wrong with the specific slow-looking request itself.

**Source:** [PostgreSQL Documentation — pg_stat_activity](https://www.postgresql.org/docs/current/monitoring-stats.html#MONITORING-PG-STAT-ACTIVITY-VIEW), [PostgreSQL Documentation — idle_in_transaction_session_timeout](https://www.postgresql.org/docs/current/runtime-config-client.html)

---

## 29. How Would You Perform a Destructive Schema Migration Without Downtime?

**Answer:**

"I'd apply the general **expand/contract** pattern, the same discipline referenced in the JPA/Hibernate file's entity-relationship-migration question, but stated here at the schema level directly. **Expand**: add the new schema element (a new column, a new table, a new constraint) alongside the existing one, without removing or altering anything the currently-deployed application version depends on — this deploy is purely additive and safe to release independently. **Migrate**: backfill the new structure from the old (in bounded batches, per the JPA/Hibernate batch-processing discipline, not one giant transaction), and deploy an application version that writes to *both* old and new structures simultaneously (dual-write) while reading from whichever is authoritative for the current rollout stage — this is the phase where actual application code changes happen, and it can proceed gradually, verified against production traffic, with the old structure still fully intact as a safety net. **Contract**: once every consumer/application instance is confirmed migrated to use the new structure exclusively (verified, not assumed) and a safe rollback window has passed, remove the old structure entirely.

The reason this pattern specifically avoids downtime for a *destructive* change (a column rename, a type change, a column removal) is that a truly destructive, single-step migration (`ALTER TABLE ... RENAME COLUMN`, run once) requires the *old* and *new* application versions to never simultaneously depend on incompatible schema shapes during a rolling deployment — and since a rolling deploy inherently means old and new application code run *simultaneously* for some window, any single-step destructive change is incompatible with zero-downtime rolling deployment by construction, regardless of how fast the migration itself executes."

**Code:**

```sql
-- EXPAND — additive only, safe to deploy alongside the CURRENT app version
ALTER TABLE orders ADD COLUMN customer_email_normalized VARCHAR(255); -- NEW column,
-- old app version doesn't know about it and isn't affected by its presence

-- MIGRATE — backfill in BOUNDED BATCHES, not one giant transaction
UPDATE orders SET customer_email_normalized = LOWER(TRIM(customer_email))
WHERE id BETWEEN 1 AND 10000 AND customer_email_normalized IS NULL;
-- repeated in batches; NEW app version writes to BOTH columns during this phase

-- CONTRACT — only after EVERY consumer is confirmed on the new column,
-- and a safe rollback window has passed
ALTER TABLE orders DROP COLUMN customer_email; -- the OLD column, now truly unused
```

```java
// MIGRATE phase application code — dual-write, so the OLD column stays
// correct as a safety net for as long as any old app instance might still
// be running during a rolling deployment
@Transactional
void saveOrder(Order order) {
    order.setCustomerEmail(order.getEmail());                     // OLD — still written
    order.setCustomerEmailNormalized(order.getEmail().trim().toLowerCase()); // NEW
    orderRepository.save(order);
}
```

**Follow-up:**

I'd bring up that the "migrate" phase's verification step — confirming every consumer has genuinely stopped relying on the old structure before contracting — deserves the exact same rigor as the REST API Design file's endpoint-deprecation discussion: measure actual usage (query logs, application metrics on which code path/column is being read) rather than assuming a deploy completed successfully means every instance is running the new code, since a stuck deployment, a long-lived batch job on an old version, or an unexpected rollback mid-migration could all mean the old structure is still genuinely load-bearing longer than expected. I'd also mention that for genuinely large tables, even the "expand" phase's `ALTER TABLE ADD COLUMN` needs care — modern PostgreSQL versions handle a nullable column addition without a full table rewrite (fast, metadata-only), but adding a column with a non-null default, or certain other schema changes, can still trigger a full table rewrite that locks the table for the operation's duration on some database versions — this is exactly the kind of database-version-specific detail worth verifying explicitly (via `EXPLAIN`/documentation for the specific database version in use) rather than assuming based on general schema-migration folklore, before running it against a large, heavily-used production table.

**Source:** [Martin Fowler & Pramod Sadalage — Evolutionary Database Design](https://martinfowler.com/articles/evodb.html), [PostgreSQL Documentation — ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html)

---

## 30. When Is Compensation Impossible, and How Should the Workflow Be Designed?

**Answer:**

"Compensation is impossible whenever a step's real-world effect genuinely cannot be reversed or semantically undone — an email or SMS that's already been sent and read, a physical shipment that's already left a warehouse and can't be recalled before delivery, funds that have been irrevocably transferred to a system outside your control (a wire transfer to an external bank, once it clears), or any action with an observable, external, human-facing effect that a 'compensating' follow-up action can mitigate but never truly erase (you can send a follow-up 'please disregard our previous email' message, but you can't make the original message un-read).

The design response, given that reality, has two parts. First, **sequencing**: order a saga's steps so that genuinely irreversible actions happen **last**, after every reversible step has already succeeded — minimizing the window in which a later failure would require attempting to compensate for something that can't actually be compensated. Second, and more fundamentally, for steps that remain irreversible no matter how they're sequenced (they're inherently the *final*, externally-visible outcome of the whole workflow), the design has to shift from 'automatically compensate' to **'make the irreversible step maximally reliable and minimally likely to need undoing in the first place'** — meaning every precondition that could cause it to need reversing should be fully validated and confirmed *before* that step executes, treating the irreversible action as a one-way door that the system does everything possible to walk through correctly the first time, rather than planning to walk back through it afterward."

**Code:**

```text
Order Fulfillment Saga — DELIBERATE ordering, irreversible steps LAST:

  1. Reserve Inventory        <- reversible (release)
  2. Charge Payment           <- reversible (refund)
  3. Generate Invoice/Receipt <- reversible (void/cancel, in most jurisdictions)
  4. Ship Physical Package    <- IRREVERSIBLE once truck departs — placed LAST,
                                  deliberately, so every reversible precondition
                                  (payment confirmed, inventory genuinely available,
                                  address validated) is FULLY confirmed BEFORE
                                  this step ever executes

  If step 4 somehow still needs to be "undone" after the fact (a shipping
  error discovered post-departure): this is NOT a compensating transaction
  in the saga sense anymore — it becomes a genuinely separate, often manual
  or partially-manual remediation process (a return/refund workflow, customer
  service intervention), explicitly outside the automatic saga machinery
```

**Follow-up:**

I'd bring up that this reality — some workflows genuinely have a true point of no return — is exactly why a mature saga implementation includes an explicit **"irreversible step" boundary** in its design, clearly documented and reviewed, rather than treating every step as uniformly compensable and discovering the gap only when a real incident requires "undoing" something that can't be undone. I'd also mention that this is a legitimate place where extra validation, confirmation, or even a deliberate, brief human-in-the-loop delay before the irreversible step (a "review before final shipment" gate for high-value orders, for instance) is a reasonable, deliberate design trade-off — accepting slightly slower throughput specifically at the one-way-door step, in exchange for meaningfully reducing the rate at which the system ever needs a remediation process that doesn't cleanly fit the automated-compensation model at all. I'd frame the broader staff-level takeaway as: not every distributed-workflow problem has a fully automatable solution, and recognizing exactly where that boundary is — and designing the system to minimize how often it's actually reached — is itself the correct engineering answer, rather than forcing every step into a compensating-transaction shape that doesn't genuinely apply to it.

**Source:** [Chris Richardson — Saga Pattern](https://microservices.io/patterns/data/saga.html), [Hector Garcia-Molina & Kenneth Salem — Sagas (original 1987 paper)](https://www.cs.cornell.edu/andru/cs711/2002fa/reading/sagas.pdf)

---

## Sources & Further Reading — Consolidated

| Topic | Link |
|---|---|
| Jim Gray — The Transaction Concept | https://jimgray.azurewebsites.net/papers/thetransactionconcept.pdf |
| PostgreSQL Documentation — Transaction Isolation | https://www.postgresql.org/docs/current/transaction-iso.html |
| Berenson et al. — A Critique of ANSI SQL Isolation Levels | https://www.microsoft.com/en-us/research/publication/a-critique-of-ansi-sql-isolation-levels/ |
| PostgreSQL Documentation — MVCC | https://www.postgresql.org/docs/current/mvcc-intro.html |
| PostgreSQL Documentation — Routine Vacuuming | https://www.postgresql.org/docs/current/routine-vacuuming.html |
| Spring Framework Reference — Transaction Propagation | https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/tx-propagation.html |
| HikariCP — Pool Sizing | https://github.com/brettwooldridge/HikariCP/wiki/About-Pool-Sizing |
| Spring Framework Reference — Understanding AOP Proxies | https://docs.spring.io/spring-framework/reference/core/aop/proxying.html |
| Spring Framework Reference — Rollback Rules | https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html |
| Vlad Mihalcea — Spring Transaction Propagation | https://vladmihalcea.com/spring-transaction-best-practices/ |
| Spring Framework Reference — Transactional Events | https://docs.spring.io/spring-framework/reference/data-access/transaction/event.html |
| PostgreSQL Documentation — Explicit Locking / Deadlocks | https://www.postgresql.org/docs/current/explicit-locking.html |
| Spring Retry documentation | https://github.com/spring-projects/spring-retry |
| Martin Kleppmann — Designing Data-Intensive Applications | https://dataintensive.net/ |
| PostgreSQL Documentation — Constraints | https://www.postgresql.org/docs/current/ddl-constraints.html |
| Chris Richardson — Transactional Outbox Pattern | https://microservices.io/patterns/data/transactional-outbox.html |
| Debezium documentation | https://debezium.io/documentation/reference/stable/index.html |
| Confluent — Exactly-Once Semantics in Apache Kafka | https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/ |
| Kafka Documentation — Transactions | https://kafka.apache.org/documentation/#semantics |
| Pat Helland — Life Beyond Distributed Transactions | https://cidrdb.org/cidr2007/papers/cidr07p15.pdf |
| Chris Richardson — Saga Pattern | https://microservices.io/patterns/data/saga.html |
| Hector Garcia-Molina & Kenneth Salem — Sagas (1987) | https://www.cs.cornell.edu/andru/cs711/2002fa/reading/sagas.pdf |
| Chris Richardson — Idempotent Consumer | https://microservices.io/patterns/communication-style/idempotent-consumer.html |
| Temporal documentation | https://docs.temporal.io/ |
| AWS Architecture Blog — Exponential Backoff and Jitter | https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/ |
| Stripe API — Idempotent Requests | https://stripe.com/docs/api/idempotent_requests |
| PostgreSQL Documentation — pg_stat_activity | https://www.postgresql.org/docs/current/monitoring-stats.html#MONITORING-PG-STAT-ACTIVITY-VIEW |
| Martin Fowler & Pramod Sadalage — Evolutionary Database Design | https://martinfowler.com/articles/evodb.html |
| PostgreSQL Documentation — ALTER TABLE | https://www.postgresql.org/docs/current/sql-altertable.html |
