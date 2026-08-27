# REST API Design — Code-Block Audit — 2026-08-25

Scope: ninth guide in `ROADMAP.md`'s code-block validation rollout.

## Classification summary (40 total code blocks)

- **9 `java`-tagged blocks.** 6 of the 9 (Q5, Q10, Q13, Q20, Q21, Q25)
  were extracted and compiled directly against real Spring Web 6.1.8,
  Spring Retry, and Resilience4j 2.2.0 APIs (added to the reusable Maven
  project from the earlier Java/Spring passes) — this surfaced two real
  bugs (below). The remaining 3 (Q15's enum-handling switch statement,
  Q22's per-tenant rate limiter, Q24's tracing example) reference
  undefined domain types (`quotaRepository`, `tokenBucketScript`,
  `inventoryClient`) specific to their own narrow example — correctly
  **partial illustrative snippet** per `CONTRIBUTING.md`; Q15's switch
  statement was reviewed by inspection (standard Java 14+ arrow-switch
  syntax, already compiled successfully elsewhere in this repository).
- **12 `http`-tagged, 8 `json`-tagged blocks** — request/response
  examples (status codes, headers, pagination cursors, error shapes) —
  reviewed for correct header names and JSON structure against RFC 9110/
  9457/7396/6902/8594 and the IETF drafts cited, not executed (would
  require a live HTTP server to round-trip meaningfully).
- **5 `text`-tagged blocks** — RPC-vs-REST comparison, idempotency
  tables, state-diagram, business-health distinctions — correctly
  diagrams/comparisons, not meant to execute.
- **3 `sql`-tagged blocks** — offset/keyset pagination queries, a unique
  constraint — reviewed for syntactic correctness, not executed.
- **3 `yaml`-tagged blocks** — a compatibility-policy example, an
  OpenAPI spec fragment, a Spectral lint ruleset — reviewed for
  structural correctness, not executed (would require the Spectral CLI).

## Bugs found and fixed

**Q5 — stale, guaranteed-empty `Optional.get()` in the concurrent-retry
catch block (real `NoSuchElementException`).** The idempotent
payment-creation handler's `catch (DuplicateKeyException e)` block
called `existing.get()`:

```java
} catch (DuplicateKeyException e) {
    return ResponseEntity.status(existing.get().getStatusCode())
        .body(idempotencyRepository.findByKey(idempotencyKey).get().getStoredResponse());
}
```

`existing` is the `Optional` captured *before* the `try` block, and the
`catch` block is only reached when that earlier `if (existing.isPresent())`
check was false — so `existing` is guaranteed empty at this point, and
`existing.get()` throws `NoSuchElementException`. Reproduced the exact
exception with a minimal standalone repro before fixing. Fixed by
re-querying once and using the fresh result for both the status code and
the body:

```java
} catch (DuplicateKeyException e) {
    IdempotencyRecord winner = idempotencyRepository.findByKey(idempotencyKey)
        .orElseThrow();
    return ResponseEntity.status(winner.getStatusCode()).body(winner.getStoredResponse());
}
```

**Q25 — undeclared `response` symbol (real compile error).** The
usage-instrumentation example called `response.setHeader(...)` twice,
but `response` was never declared as a method parameter, field, or local
variable — unlike the guide's usual convention of implying
repository/service fields on an unshown enclosing class,
`HttpServletResponse` specifically isn't something Spring injects as a
field; it must be a method parameter. Confirmed as a real compile error
(`cannot find symbol: variable response`) before fixing. Fixed by adding
it to the method signature:

```java
Order getOrderV1(@PathVariable String id, @RequestHeader("X-Api-Key") String apiKey,
        HttpServletResponse response) { ... }
```

## Not done in this pass

- Q15's switch statement and Q22/Q24's illustrative snippets referencing
  undefined domain types were not independently compiled — Q15 is
  low-risk standard syntax already exercised elsewhere in this
  repository; Q22/Q24 would require fabricating substantial domain logic,
  which `CONTRIBUTING.md` discourages.
- No live HTTP server, OpenAPI validator, or Spectral CLI was used —
  `http`/`json`/`yaml` blocks were reviewed for correctness against their
  cited RFCs/drafts and current OpenAPI/Spectral documentation, not
  executed or schema-validated.
- SQL pagination examples (offset vs. keyset) were reviewed for
  syntactic correctness, not run against a live database — the same
  keyset-pagination technique was already implicitly covered by this
  session's general SQL review in the Transactions pass.
