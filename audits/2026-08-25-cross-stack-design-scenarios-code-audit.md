# Cross-Stack Design Scenarios — Code-Block Audit — 2026-08-25

Scope: tenth guide in `ROADMAP.md`'s code-block validation rollout. This
guide is deliberately synthesis-oriented — every scenario explicitly
cross-references mechanisms already verified in depth in their own home
guides (the Redis stampede/degradation incident, the JPA/Hibernate N+1
postmortem, the Transactions outbox pattern, the REST API idempotency-key
mechanism, the Spring Security JWKS rotation sequencing) rather than
introducing large amounts of new code to check.

## Classification summary (20 total code blocks)

- **4 `java`-tagged blocks.** Q7's `@CircuitBreaker` usage is the
  identical annotation already compiled against the real Resilience4j
  API in the REST API Design pass. Q8's before/after outbox-pattern
  snippet is the same mechanism already verified in the Transactions
  pass (same-transaction atomicity between a business write and an
  outbox row). Q18's synchronous-boundary example uses only
  `java.util.concurrent.Semaphore` — a plain JDK class needing no
  verification. Q9's `KafkaListenerEndpointRegistry`/
  `MessageListenerContainer.pause()`/`.resume()` usage was genuinely new
  (the Kafka guide itself has zero code blocks) — extracted and compiled
  directly against the real `spring-kafka` API to confirm the method
  signatures are real and correctly used.
- **15 `text`-tagged blocks** — architecture/sequence diagrams,
  investigation checklists, before/after narrative pseudocode (including
  the one flagged by `scripts/check_code_fences.py` as
  "general-purpose-code-like" — Q14's monolith-split before/after
  example, reviewed and confirmed to be genuine annotated narrative
  pseudocode, not intended to compile, consistent with how the
  Transactions pass resolved its own two flagged blocks). Correctly
  classified.
- **1 `bash`-tagged block** — GC/safepoint log flags and a
  `pg_stat_activity` diagnostic query (Q13) — reviewed for correct flag
  syntax against JDK documentation, not executed.

## Verification performed

`KafkaListenerEndpointRegistry.getListenerContainers()` returning a
`Collection<MessageListenerContainer>` with `.pause()`/`.resume()`
methods (Q9) was compiled directly against the real `spring-kafka`
dependency — confirmed real, correctly-typed API, not a plausible-looking
invention.

## Bugs found

None. No new bugs were introduced in this guide's own code (Q7/Q8's
patterns were already confirmed correct in their home guides; Q9's new
API usage compiled cleanly).

## Not done in this pass

- Q7's `@CircuitBreaker` and Q8's outbox pattern were not re-verified
  independently — they're the identical mechanisms already confirmed
  with real compilation/execution in
  `audits/2026-08-25-rest-api-design-code-audit.md` and
  `audits/2026-08-25-transactions-code-audit.md` respectively.
- No live multi-region, Kafka, or database infrastructure was used to
  verify the architectural claims in this guide (active-active/
  active-passive replication trade-offs, JWKS rotation sequencing,
  tenant-isolation-via-RLS) — these are design/diagnostic reasoning
  questions describing established patterns already cited to their
  primary sources, not executable code to classify or compile.
