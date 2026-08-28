# REST API Design — Interview Prep (Lead/Staff Level, with Code & Sources)

> **Target level:** Lead/Staff · **Baseline:** HTTP semantics per RFC 9110/9111 (framework-agnostic; code examples use Spring Boot 3.x) · **Last verified:** 2026-08-22 · **Prerequisites:** basic HTTP; [Spring Boot Internals](../Frameworks/Spring_Boot_Internals_Interview_Prep.md) helpful for the code examples

How to use this: each question has a **core answer** (100–180 words — roughly what you'd actually say out loud in 40–70 seconds), a **staff-level extension** with the deeper trade-offs pushed out of the core response rather than dropped, an **example** snippet you could sketch on a whiteboard or IDE, **follow-up questions** an interviewer is likely to probe with next, and **sources** — because at this level the bar is explaining trade-offs and failure modes across client evolution, retries, and multi-team consumption, not reciting HTTP verb definitions.

<!-- toc -->
## Table of Contents

- [1. What Makes an API Resource-Oriented Rather Than RPC-Oriented?](#1-what-makes-an-api-resource-oriented-rather-than-rpc-oriented)
- [2. How Do You Choose Resource Names and URI Structures?](#2-how-do-you-choose-resource-names-and-uri-structures)
- [3. Explain the Semantics of `GET`, `POST`, `PUT`, `PATCH`, and `DELETE`](#3-explain-the-semantics-of-get-post-put-patch-and-delete)
- [4. Which HTTP Methods Should Be Idempotent?](#4-which-http-methods-should-be-idempotent)
- [5. How Would You Make a Payment-Creation Endpoint Safely Retryable?](#5-how-would-you-make-a-payment-creation-endpoint-safely-retryable)
- [6. Compare Offset, Cursor, and Keyset Pagination](#6-compare-offset-cursor-and-keyset-pagination)
- [7. How Do You Guarantee Stable Pagination While Data Changes?](#7-how-do-you-guarantee-stable-pagination-while-data-changes)
- [8. How Would You Design Filtering, Sorting, and Field Selection?](#8-how-would-you-design-filtering-sorting-and-field-selection)
- [9. Compare JSON Merge Patch and JSON Patch](#9-compare-json-merge-patch-and-json-patch)
- [10. How Do You Prevent Lost Updates Using ETags or Version Fields?](#10-how-do-you-prevent-lost-updates-using-etags-or-version-fields)
- [11. When Should an API Return `200`, `201`, `202`, `204`, `400`, `409`, `422`, or `429`?](#11-when-should-an-api-return-200-201-202-204-400-409-422-or-429)
- [12. What Should a Consistent Error Response Contain?](#12-what-should-a-consistent-error-response-contain)
- [13. How Should Validation Errors Be Represented?](#13-how-should-validation-errors-be-represented)
- [14. Compare URI, Header, and Media-Type API Versioning](#14-compare-uri-header-and-media-type-api-versioning)
- [15. How Would You Evolve an API Without Breaking Existing Clients?](#15-how-would-you-evolve-an-api-without-breaking-existing-clients)
- [16. How Do You Define Backward Compatibility?](#16-how-do-you-define-backward-compatibility)
- [17. How Should Long-Running Operations Be Modeled?](#17-how-should-long-running-operations-be-modeled)
- [18. How Do You Design Asynchronous REST Workflows?](#18-how-do-you-design-asynchronous-rest-workflows)
- [19. How Would You Expose Bulk Operations With Partial Success?](#19-how-would-you-expose-bulk-operations-with-partial-success)
- [20. How Do Retries Interact With Timeouts and Duplicate Requests?](#20-how-do-retries-interact-with-timeouts-and-duplicate-requests)
- [21. How Do You Protect an API From Retry Storms?](#21-how-do-you-protect-an-api-from-retry-storms)
- [22. How Would You Implement Rate Limiting for Tenants With Different Quotas?](#22-how-would-you-implement-rate-limiting-for-tenants-with-different-quotas)
- [23. What Is the Difference Between Readiness, Liveness, and Business Health?](#23-what-is-the-difference-between-readiness-liveness-and-business-health)
- [24. How Should Distributed Tracing Context Propagate?](#24-how-should-distributed-tracing-context-propagate)
- [25. How Would You Safely Deprecate an Endpoint Used by Unknown Consumers?](#25-how-would-you-safely-deprecate-an-endpoint-used-by-unknown-consumers)
- [26. How Do You Balance Fine-Grained APIs Against Chatty Network Behavior?](#26-how-do-you-balance-fine-grained-apis-against-chatty-network-behavior)
- [27. Design an API for Creating an Order, Reserving Inventory, and Taking Payment](#27-design-an-api-for-creating-an-order-reserving-inventory-and-taking-payment)
- [28. How Would You Review an API Specification Across Multiple Teams?](#28-how-would-you-review-an-api-specification-across-multiple-teams)
- [Sources & Further Reading — Consolidated](#sources--further-reading--consolidated)

<!-- /toc -->

---

## 1. What Makes an API Resource-Oriented Rather Than RPC-Oriented?

**Core answer:**

"An RPC-style API exposes *actions* as the main unit. Endpoints read like verbs or procedures — `/getUser`, `/createOrderAndCharge`, `/cancelSubscription` — mapping roughly one-to-one onto function calls, and the HTTP method is often incidental (a lot of RPC-style APIs use POST for everything). A resource-oriented (REST) API exposes *nouns* instead: resources identified by URIs (`/users/{id}`, `/orders/{id}`), with actions expressed through a small, standard set of HTTP methods applied to those nouns — `GET /orders/{id}` to read, `POST /orders` to create, `DELETE /orders/{id}` to remove.

The benefit isn't stylistic purity. A resource-oriented design gets a lot of behavior for free from HTTP's own semantics: caching (`GET` is cacheable by intermediaries by default; an RPC `POST /getUser` usually isn't), idempotency guarantees tied to specific methods (question 4), standard status codes, and tooling that already understands HTTP without needing to learn your specific action vocabulary."

**Staff-level extension:**

Not every operation maps cleanly onto CRUD-over-a-noun. Questions 17 and 18 cover how I'd handle genuinely action-oriented operations — "approve this refund," say — within an otherwise resource-oriented design, rather than pretending everything is naturally a resource. I'd also be upfront that pure REST-by-the-book (HATEOAS, Roy Fielding's original dissertation-level constraints) is rarely what teams actually mean by "RESTful API" in practice. Most production APIs are "pragmatic REST": resource-oriented URLs and standard HTTP semantics, without full hypermedia-driven discoverability. Resource orientation is the right default because it leverages HTTP's existing semantics and tooling — but a handful of genuinely action-oriented operations are fine to model explicitly as their own thing, rather than forcing an awkward resource abstraction onto something that isn't naturally one. Dogmatic REST-purism that produces worse APIs than a pragmatic hybrid is worth pushing back on in a design review.

**Example:**

```text
# RPC-style — action-centric, HTTP method is incidental (often always POST)
POST /getUserOrders      { "userId": "123" }
POST /cancelOrder        { "orderId": "456" }
POST /createOrderAndCharge  { "userId": "123", "items": [...] }

# Resource-oriented — noun-centric, HTTP method carries real, standard meaning
GET    /users/123/orders
DELETE /orders/456                      # cancellation modeled as resource deletion,
                                          # or as a state transition (question 17)
POST   /orders                          # creates a new Order resource
```

**Follow-up questions:**

- *"What kinds of operations don't map cleanly onto a resource?"* — A workflow trigger, a bulk operation, a computation with no natural resource identity. Model these explicitly as their own thing (question 17) rather than forcing an awkward abstraction.
- *"Does REST require HATEOAS to count as REST?"* — In the purist sense, yes. But that's rarely what teams mean in practice — "pragmatic REST" (resource-oriented URLs, standard HTTP semantics) is the real-world norm.

**Sources:** [Roy Fielding's dissertation — REST architectural style](https://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm), [RFC 9110 — HTTP Semantics](https://datatracker.ietf.org/doc/html/rfc9110)

---

## 2. How Do You Choose Resource Names and URI Structures?

**Core answer:**

"A few conventions I'd apply consistently — consistency across an API surface matters more than any single rule on its own. Plural nouns for collections (`/orders`, not `/order`). Lowercase with hyphens rather than underscores or camelCase in the URL path (`/order-items`, not `/orderItems` or `/order_items`). And nesting to express genuine ownership or containment, but only one level deep in practice: `/users/{userId}/orders` is fine, but `/users/{userId}/orders/{orderId}/items/{itemId}/reviews/{reviewId}` gets unwieldy. That usually means the deeper resources deserve their own top-level, independently addressable collection (`/order-items/{itemId}`) instead of being buried behind a long parent chain.

I'd also keep URIs about *identity*, not query or filter logic. Filtering, sorting, and pagination parameters belong in the query string (question 8), not the path — `/orders/status/shipped` implies status is a fixed part of the hierarchy rather than a filter dimension."

**Staff-level extension:**

The highest-leverage practice here isn't any individual naming rule — it's a **written, enforced API style guide** shared across every team building services in the org, linted automatically (an OpenAPI-spec linter like Spectral, run in CI) rather than relying on manual review to catch inconsistency. The real cost of inconsistent naming isn't aesthetic. Client developers integrating with many internal APIs have to context-switch conventions per service, and that compounds the cognitive load of working across a growing microservices landscape. A shared, automatically-enforced style guide is the actual staff-level fix — not "everyone please try to follow the same conventions."

**Example:**

```text
# GOOD — plural nouns, hyphenated, shallow nesting for genuine containment
GET  /orders
GET  /orders/{orderId}
GET  /users/{userId}/orders          # genuine containment: these orders BELONG to this user
GET  /order-items/{itemId}           # deep resources get their OWN top-level collection,
                                        # rather than /users/{u}/orders/{o}/items/{i}

# AVOID
GET  /Order                          # inconsistent casing/singular
GET  /orders/status/shipped          # filter logic baked into the PATH instead
GET  /orders?status=shipped          # ...use a query parameter instead, see question 8
GET  /users/{u}/orders/{o}/items/{i}/reviews/{r}   # too deep, hard to address independently
```

**Follow-up questions:**

- *"Why hyphens over camelCase or underscores?"* — Hyphens are the more broadly recommended convention for URL readability and SEO-adjacent tooling. It's a stylistic choice, but one worth picking once and enforcing.
- *"How do you actually enforce naming consistency across teams?"* — An OpenAPI-spec linter (Spectral) run in CI, not manual review. That catches deviation automatically at the point it's introduced.

**Sources:** [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines), [Google API Design Guide](https://cloud.google.com/apis/design)

---

## 3. Explain the Semantics of `GET`, `POST`, `PUT`, `PATCH`, and `DELETE`

**Core answer:**

"`GET` retrieves a representation of a resource. It must be safe (no side effects the client should be held responsible for) and cacheable by default. `POST` creates a new subordinate resource under a collection, or triggers a non-idempotent action — it's the 'catch-all' verb precisely because it doesn't carry the safety or idempotency guarantees the others do. `PUT` replaces a resource *entirely* at a known URI: the request body represents the complete desired state, and any field left out is implicitly cleared, not left untouched. That's what makes `PUT` naturally idempotent. `PATCH` applies a *partial* modification — only the fields present change, everything else stays as-is. Because there are multiple competing formats for expressing a partial update (question 9), its idempotency depends entirely on the patch content itself: an 'increment by 1' patch isn't idempotent, a 'set this field to X' patch is. `DELETE` removes a resource and should be idempotent — deleting an already-deleted resource should be a no-op returning success, not an error."

**Staff-level extension:**

The common real-world mistake is using `PUT` for what's actually a partial update: a team implements `PUT /orders/123` but only updates the fields present in the request body, silently leaving the rest untouched when they're omitted. This violates `PUT`'s actual replace-semantics contract, and any HTTP-aware intermediary, cache, or client library that assumes correct `PUT` behavior can misbehave against it. The fix is simple: if an endpoint only ever updates a subset of fields, it should be `PATCH`, not a `PUT` that lies about its own semantics. Getting this right isn't pedantry — it's what lets HTTP-level tooling and client libraries reason correctly about the API's actual behavior without reading custom documentation for every endpoint.

**Example:**

```http
GET /orders/123               # safe, cacheable — retrieves current state, no side effect

POST /orders                  # creates a NEW resource; NOT idempotent — calling
{ "items": [...] }             # this twice creates TWO orders

PUT /orders/123                # REPLACES the entire resource — omitted fields are
{ "status": "shipped", "items": [...] }  # cleared/reset, not left untouched;
                                            # calling this twice with the same body
                                            # produces the SAME end state both times

PATCH /orders/123              # PARTIAL update — only "status" changes, everything
{ "status": "shipped" }         # else on the order is left exactly as it was

DELETE /orders/123             # idempotent — calling this repeatedly should be safe;
                                 # the SECOND call finding nothing to delete is a
                                 # normal, expected outcome, not an error condition
```

**Follow-up questions:**

- *"Is `PATCH` always idempotent?"* — No, it depends entirely on the patch content. "Increment by 1" isn't; "set to X" is.
- *"Why does it matter if a team implements `PUT` as a partial update?"* — Any HTTP-aware intermediary, cache, or client library assuming correct `PUT` semantics (full replacement) can misbehave against an endpoint that quietly does partial updates instead.

**Sources:** [RFC 9110 §9 — HTTP Methods](https://datatracker.ietf.org/doc/html/rfc9110#section-9), [RFC 5789 — PATCH Method](https://datatracker.ietf.org/doc/html/rfc5789)

---

## 4. Which HTTP Methods Should Be Idempotent?

**Core answer:**

"By the HTTP spec, `GET`, `HEAD`, `PUT`, `DELETE`, `OPTIONS`, and `TRACE` are all idempotent — making the identical request multiple times has the same effect on server state as making it once. `POST` and `PATCH` are explicitly **not** guaranteed idempotent by the spec. A specific `PATCH` payload can happen to be idempotent depending on what it expresses (question 3), but the method itself carries no such guarantee.

Idempotency is about the *effect on server state* being the same across repeated calls — a different, weaker property than **safety**. `GET` is both safe (no intended side effect at all) and idempotent; `PUT`/`DELETE` are idempotent but not safe. This matters for retry logic: a client can safely retry any idempotent method after a timeout without risking a duplicated effect. But retrying a plain `POST` after a timeout is genuinely dangerous, since the original request might have already succeeded server-side — a naive retry could create a duplicate resource, which is exactly the problem the next question addresses."

**Staff-level extension:**

Idempotency being a spec-level guarantee doesn't mean every real implementation honors it. A `PUT` handler with a buggy side effect — incrementing a counter as a side channel of an otherwise-replace-style update, say — technically violates the idempotency contract the method name promises. This is a real, if less common, source of retry-related bugs: infrastructure like load balancers, HTTP clients, and service meshes that automatically retries idempotent methods on failure is trusting the *implementation* to actually be idempotent, not just the method choice. Idempotency has to be engineered into the handler's actual behavior — usually via an upsert or set-to-exact-value operation, not an increment or append — not just assumed because the HTTP method is conventionally idempotent. And for `POST`, where the spec offers no help at all, idempotency has to be added deliberately, via a client-supplied idempotency key (question 5).

**Example:**

```text
Idempotent (safe to retry blindly after a timeout/network failure):
  GET     — safe AND idempotent
  HEAD    — safe AND idempotent
  PUT     — idempotent, not safe (has an effect, but repeating doesn't compound it)
  DELETE  — idempotent, not safe
  OPTIONS — safe AND idempotent
  TRACE   — safe AND idempotent

NOT guaranteed idempotent (retrying blindly risks a DUPLICATE effect):
  POST    — e.g., retrying a payment-creation POST after a timeout could create
             TWO charges if the original request actually succeeded server-side
  PATCH   — idempotency depends entirely on what the specific patch body expresses
```

**Follow-up questions:**

- *"Is idempotency guaranteed just by choosing an idempotent HTTP method?"* — No. The spec guarantees the contract, not the implementation — a buggy `PUT` handler with a side-channel effect can violate it silently.
- *"What's the difference between idempotent and safe?"* — Safe means no intended side effect at all (`GET`). Idempotent means repeating the effect doesn't compound it (`PUT`/`DELETE` are idempotent but not safe).

**Sources:** [RFC 9110 §9.2 — Idempotent Methods](https://datatracker.ietf.org/doc/html/rfc9110#section-9.2.2)

---

## 5. How Would You Make a Payment-Creation Endpoint Safely Retryable?

**Core answer:**

"Since payment creation is inherently a `POST` with no natural idempotent semantics, safety under retry has to be added explicitly via an **idempotency key**. The client generates a unique key — typically a UUID — once per logical payment attempt, and sends it as an `Idempotency-Key` header. Before processing, the server checks whether it has already seen this exact key. If not, it processes the payment normally and stores the key alongside the *result* for some retention window. If the key has been seen before, the server returns the **stored result from the original request** without processing the payment again — even if the client retries because it never received the original response, the server recognizes this as a retry it already fully handled, and responds consistently without a second charge."

**Staff-level extension:**

The detail that actually matters for correctness: the idempotency-key check and the payment-processing-plus-key-storage need to happen atomically — typically via a unique constraint on the key in the same database transaction as the payment record, or a distributed lock around the check-then-process sequence. A naive "check if key exists, if not process" implementation has the same check-then-act race a concurrent map warns about: two near-simultaneous retries with the same key could both pass the "not seen yet" check and both create a payment. The retention window is a real design trade-off, not an afterthought — idempotency records need to be kept long enough to cover any realistic client retry window (commonly 24 hours), but keeping them forever is unnecessary storage growth. A scheduled cleanup job or TTL should expire them after that window.

**Example:**

```java
@PostMapping("/payments")
ResponseEntity<PaymentResult> createPayment(
        @RequestHeader("Idempotency-Key") String idempotencyKey,
        @RequestBody PaymentRequest request) {

    // Atomic check-and-reserve — a unique DB constraint on idempotency_key
    // makes this genuinely race-safe, not just "probably fine"
    Optional<IdempotencyRecord> existing = idempotencyRepository.findByKey(idempotencyKey);
    if (existing.isPresent()) {
        // this is a RETRY of a request already fully processed — return the
        // ORIGINAL stored result, do NOT process the payment again
        return ResponseEntity.status(existing.get().getStatusCode())
            .body(existing.get().getStoredResponse());
    }

    try {
        PaymentResult result = paymentProcessor.charge(request); // the actual side effect
        idempotencyRepository.save(new IdempotencyRecord(idempotencyKey, 200, result));
        return ResponseEntity.ok(result);
    } catch (DuplicateKeyException e) {
        // a concurrent request with the SAME key won the race to insert first —
        // re-query (the earlier `existing` is still the EMPTY lookup from
        // before this attempt, not the winner's row) and return ITS result
        // rather than double-processing
        IdempotencyRecord winner = idempotencyRepository.findByKey(idempotencyKey)
            .orElseThrow();
        return ResponseEntity.status(winner.getStatusCode()).body(winner.getStoredResponse());
    }
}
```

```sql
-- The unique constraint that makes the check-and-reserve step genuinely atomic
ALTER TABLE idempotency_records ADD CONSTRAINT uq_idempotency_key UNIQUE (idempotency_key);
```

**Follow-up questions:**

- *"What if the same key arrives with a genuinely different payment amount?"* — Reject it as a client error (`422`, "idempotency key reused with different parameters"). Never silently process the new amount or silently return the old result.
- *"What makes the check-and-store step actually safe under concurrent retries?"* — A unique DB constraint on the key in the same transaction as the payment write, not a separate "check, then process" pair of steps.

**Sources:** [Stripe API — Idempotent Requests](https://stripe.com/docs/api/idempotent_requests), [IETF Draft — The Idempotency-Key HTTP Header Field](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/)

---

## 6. Compare Offset, Cursor, and Keyset Pagination

**Core answer:**

"**Offset pagination** (`?page=3&size=20`) is the simplest to implement — the database skips N rows and returns the next M. It has real problems at scale: the database still has to *scan* the skipped rows, so performance degrades as the offset grows, and if rows are inserted or deleted between requests, the client can see duplicate or skipped items, since 'offset 20' now points to a different logical row.

**Cursor pagination** replaces the offset with an opaque token representing 'where I left off,' encoding the last-seen item's sort key. The next request says 'give me the next N items after this cursor.' It avoids the scan-cost problem — a direct indexed seek — and is far more resilient to concurrent inserts and deletes, since the cursor refers to a fixed logical position instead of a shifting offset.

**Keyset pagination** is the actual database technique behind cursor pagination — an indexed seek condition in the `WHERE` clause rather than `OFFSET`. I'd expose an opaque cursor at the API surface, backed by a keyset query underneath."

**Staff-level extension:**

The cursor should be genuinely opaque to the client — base64-encoded, or even encrypted/signed — rather than a plain, readable value. That lets the server change its internal pagination implementation later (add a tiebreaker column, change the sort key entirely) without breaking the API contract, since clients only ever pass the cursor back verbatim. Offset pagination isn't wrong everywhere, though — for a small, admin-facing UI with modest data volume and infrequent concurrent writes, its simplicity (jump straight to page 5, show a total page count) is a real UX advantage cursor pagination can't offer. The actual trade-off is "arbitrary page jump plus total count" against "scale and consistency under concurrent writes," not "cursor is always better."

**Example:**

```sql
-- Offset pagination — simple, but the database still scans through
-- (and discards) all 100,000 skipped rows to get to this page
SELECT * FROM orders ORDER BY created_at DESC LIMIT 20 OFFSET 100000;

-- Keyset pagination — seeks directly via an indexed condition, no scan-and-discard
SELECT * FROM orders
WHERE created_at < :last_seen_created_at
   OR (created_at = :last_seen_created_at AND id < :last_seen_id) -- tiebreaker
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

```json
// Cursor pagination — the API-facing contract: an OPAQUE token, not a raw offset
{
  "items": [ /* ... 20 orders ... */ ],
  "next_cursor": "eyJjcmVhdGVkX2F0IjoiMjAyNi0wMS0wMVQwMDowMDowMFoiLCJpZCI6IjQ1NiJ9"
  // base64-encoded {"created_at": "...", "id": "456"} — the client treats this
  // as an OPAQUE string, never parses or constructs it itself
}
```

**Follow-up questions:**

- *"Can a cursor-based API jump to an arbitrary page?"* — No, and that's the trade-off. Offset pagination keeps that ability at the cost of scan performance and consistency under concurrent writes.
- *"Why not expose the raw sort key as the cursor?"* — Opacity lets the server change its internal pagination implementation later without breaking the API contract.

**Sources:** [Use the Index, Luke — pagination done right](https://use-the-index-luke.com/no-offset), [Slack API — Pagination](https://api.slack.com/apis/pagination)

---

## 7. How Do You Guarantee Stable Pagination While Data Changes?

**Core answer:**

"Stability needs two things working together. First, a **deterministic, total ordering** — the sort key must uniquely determine row order, with no ties. A sort purely on `created_at`, where rows can share a timestamp, is a real bug source: ties can come back in a different relative order across requests, skipping or duplicating a row across pages. The fix is to always include a unique column — the primary key — as an explicit final tiebreaker in the `ORDER BY`.

Second, keyset/cursor pagination (question 6) handles inserts and deletes elsewhere in the data much better than offset pagination, since each request seeks from a fixed position — a new row inserted elsewhere doesn't shift what 'this cursor' means. What it doesn't solve is a previously-returned row being modified in a way that changes its sort position mid-pagination; that row could legitimately reappear later. Usually that's an acceptable, documented trade-off rather than something fully solvable without snapshot isolation."

**Staff-level extension:**

Snapshot-based pagination — a database transaction or snapshot held open for the pagination session, or a point-in-time export the client paginates over — is the only way to get fully consistent pagination against actively-changing data. It's genuinely useful for something like a data export or an audit trail, where "the exact state as of the moment I started paginating" matters, but it comes with real cost: an open long-running transaction has its own resource and locking implications, and it isn't appropriate for a typical high-traffic, ever-changing API. For most APIs, deterministic ordering plus keyset-based cursor pagination is the right trade-off. I'd only reach for snapshot-based pagination for export/audit-style use cases where perfect point-in-time consistency is an explicit, documented requirement.

**Example:**

```sql
-- WITHOUT a tiebreaker — ties on created_at can be returned inconsistently
-- across separate requests, causing skipped or duplicated rows at page boundaries
SELECT * FROM orders ORDER BY created_at DESC LIMIT 20;

-- WITH an explicit, unique tiebreaker — deterministic total ordering,
-- guaranteed stable and consistent across repeated/paginated requests
SELECT * FROM orders ORDER BY created_at DESC, id DESC LIMIT 20;
```

**Follow-up questions:**

- *"Can a row reappear on a later page during pagination?"* — Yes, if it's updated in a way that moves its sort position while the client is still paginating. That's a documented, generally acceptable trade-off.
- *"When would you actually pay for snapshot-based pagination?"* — Export/audit-style use cases where perfect point-in-time consistency is an explicit requirement, not a typical high-traffic API.

**Sources:** [Use the Index, Luke — pagination done right](https://use-the-index-luke.com/no-offset)

---

## 8. How Would You Design Filtering, Sorting, and Field Selection?

**Core answer:**

"All three belong in the query string, not the path (question 2), since they're modifying *how* a collection is queried or rendered, not identifying a different resource.

**Filtering**: a consistent, predictable convention — `?status=shipped&createdAfter=2026-01-01` for simple equality and range filters. For more complex needs, I'd pick one consistent syntax rather than inventing per-endpoint conventions — either a structured query-parameter convention (`?status=shipped,cancelled` for 'in' semantics, `?amount[gte]=100` for range operators) or, for genuinely complex query needs, a dedicated filter DSL applied consistently across the whole API.

**Sorting**: a single, consistent parameter (`?sort=createdAt,-amount` — comma-separated, leading `-` for descending) rather than separate `sortBy`/`sortDirection` parameters that only support one field.

**Field selection** (sparse fieldsets): `?fields=id,status,total` lets a client request only the fields it needs, reducing payload size for high-volume or mobile clients. It's valuable for large resources with many optional or expensive fields, but I'd be selective about offering it — it adds real server-side complexity for a benefit that's often better solved by a leaner default response or a separate 'summary' representation."

**Staff-level extension:**

Unconstrained, free-form filtering — allowing arbitrary fields and operators without validation — is a real performance and security risk, not just a design nicety. A filter parameter that maps directly onto an unindexed column, or that allows arbitrarily complex boolean combinations, can let a client trigger expensive queries that degrade the whole service, accidentally or deliberately. I'd validate allowed filter fields and operators against a known allowlist rather than passing client input straight through to a query builder unchecked. A query language or DSL — OData's `$filter`, or GraphQL entirely — is worth considering once filtering needs grow complex enough that a bespoke query-parameter convention starts accumulating special cases. That's usually the signal the ad hoc approach has outgrown itself.

**Example:**

```http
GET /orders?status=shipped,cancelled&createdAfter=2026-01-01T00:00:00Z
GET /orders?amount[gte]=100&amount[lte]=500
GET /orders?sort=createdAt,-amount        # ascending createdAt, THEN descending amount
GET /orders?fields=id,status,total          # sparse fieldset — only these fields returned
```

**Follow-up questions:**

- *"What's the risk of unconstrained filtering?"* — A client can trigger expensive queries against unindexed columns or arbitrarily complex boolean combinations. Validate allowed fields and operators against an allowlist.
- *"When do you reach for a real query DSL instead of ad hoc query params?"* — Once filtering needs grow complex enough that the bespoke convention starts accumulating special cases. That's the signal it's outgrown itself.

**Sources:** [JSON:API Specification — Filtering, Sorting, Sparse Fieldsets](https://jsonapi.org/format/#fetching), [Google API Design Guide — Standard Fields](https://cloud.google.com/apis/design/design_patterns)

---

## 9. Compare JSON Merge Patch and JSON Patch

**Core answer:**

"Both are standardized formats for expressing a partial update via `PATCH` (question 3), and they represent genuinely different trade-offs, not just stylistic variants.

**JSON Merge Patch** (RFC 7396) is the simpler of the two. The patch body is a JSON object shaped like the target resource — a field present overwrites the corresponding field, and a field set to `null` means 'delete this field.' It's intuitive and easy to construct, but has a real limitation: because `null` means 'delete,' there's no way to express 'set this field to `null`' as distinct from 'remove it,' and any array field replaces the *entire* array rather than specific elements.

**JSON Patch** (RFC 6902) is more expressive and more complex. The patch body is an *array of operations* — `add`, `remove`, `replace`, `move`, `copy`, `test` — each targeting a location via a JSON Pointer. It can express precise per-element array operations, distinguish 'set to null' from 'remove entirely,' and include a `test` precondition that aborts the patch if not met. The cost is that it's harder for clients to hand-construct and more complex for the server to apply correctly."

**Staff-level extension:**

The practical recommendation: JSON Merge Patch is the right default for most real APIs, since most partial-update needs really are just 'change these top-level fields,' and the null-means-delete ambiguity rarely matters in practice — most domains don't have a meaningful distinction between 'field is null' and 'field is absent.' I'd reach for full JSON Patch specifically when array-element-level operations or the `test`-based precondition mechanism are genuinely needed, or when working with a client ecosystem that already expects it. Neither format substitutes for proper optimistic-concurrency control (question 10). JSON Patch's `test` operation can be used for a lightweight version check, but I'd generally prefer the explicit `ETag`/`If-Match` mechanism as the primary tool, since it's visible at the HTTP layer rather than buried inside a patch body.

**Example:**

```json
// JSON Merge Patch (RFC 7396) — simple, but ambiguous about null vs delete,
// and replaces WHOLE arrays rather than patching individual elements
// PATCH /orders/123, Content-Type: application/merge-patch+json
{
  "status": "shipped",
  "internalNotes": null,        // means "DELETE this field" — cannot express
                                   // "set internalNotes to the literal value null"
  "tags": ["urgent", "gift"]     // REPLACES the entire tags array, cannot add/remove
}                                    // just ONE tag without resending the whole array

// JSON Patch (RFC 6902) — precise, operation-based, more expressive
// PATCH /orders/123, Content-Type: application/json-patch+json
[
  { "op": "replace", "path": "/status", "value": "shipped" },
  { "op": "remove",  "path": "/internalNotes" },
  { "op": "add",     "path": "/tags/-", "value": "gift" },     // append ONE tag
  { "op": "test",    "path": "/version", "value": 5 }           // precondition —
]                                                                  // aborts the WHOLE
                                                                     // patch if version != 5
```

**Follow-up questions:**

- *"What's the actual default you'd reach for?"* — JSON Merge Patch, for most real APIs. The null-means-delete ambiguity rarely matters in practice.
- *"Can JSON Patch's `test` operation replace ETag-based concurrency control?"* — It could for a lightweight check, but `ETag`/`If-Match` is preferable as the primary mechanism, since it's visible and inspectable at the HTTP layer.

**Sources:** [RFC 7396 — JSON Merge Patch](https://datatracker.ietf.org/doc/html/rfc7396), [RFC 6902 — JSON Patch](https://datatracker.ietf.org/doc/html/rfc6902)

---

## 10. How Do You Prevent Lost Updates Using ETags or Version Fields?

**Core answer:**

"A lost update happens when two clients read the same resource, both make changes based on that now-stale read, and the second client's write silently overwrites the first client's changes without either client being told a conflict occurred — classic last-write-wins data loss.

The standard HTTP-native mechanism is `ETag` combined with conditional requests. The server includes an `ETag` header — an opaque version identifier — on every `GET` response. When the client updates the resource, it includes that same value in an `If-Match` header on the write. The server compares `If-Match` against the resource's current `ETag`; if they don't match, someone else modified the resource in between, and the server rejects the write with `412 Precondition Failed` instead of silently applying it over the intervening change. That's optimistic concurrency control at the HTTP layer, giving the client an explicit signal instead of silently losing data.

An application-level `version` field achieves the same thing in the request/response body instead of HTTP headers."

**Staff-level extension:**

This is the same optimistic-locking mechanism JPA/Hibernate implements via `@Version` — the HTTP-level `ETag`/`If-Match` pattern and the database-level `@Version` column are the same idea applied at two different layers, and in a well-designed system they're often wired together directly, with the entity's `@Version` value becoming the `ETag` so a database-level optimistic-lock failure surfaces cleanly as a `412` at the API layer. This pattern needs client cooperation to actually work: a client that ignores the `ETag`/`If-Match` contract and just sends unconditional `PUT`s defeats the whole mechanism. For genuinely critical resources, I'd consider making `If-Match` a required header — rejecting writes that omit it with `428 Precondition Required` — rather than optional, to stop well-meaning clients from silently bypassing the protection.

**Example:**

```http
GET /orders/123
200 OK
ETag: "a1b2c3d4"
{ "id": "123", "status": "pending", "total": 99.99 }

# Client makes a change based on the read above, includes If-Match with the
# EXACT ETag value it originally received
PATCH /orders/123
If-Match: "a1b2c3d4"
{ "status": "shipped" }

# If nobody else modified the resource since: succeeds, returns a NEW ETag
200 OK
ETag: "e5f6g7h8"

# If somebody else modified it in between: the server detects the mismatch
# and REJECTS the write instead of silently overwriting the intervening change
412 Precondition Failed
```

```java
@PatchMapping("/orders/{id}")
ResponseEntity<Order> updateOrder(@PathVariable String id,
        @RequestHeader("If-Match") String ifMatch, @RequestBody OrderPatch patch) {
    Order current = orderRepository.findById(id).orElseThrow();
    String currentEtag = computeEtag(current);
    if (!currentEtag.equals(ifMatch)) {
        return ResponseEntity.status(HttpStatus.PRECONDITION_FAILED).build(); // 412
    }
    Order updated = applyPatch(current, patch);
    orderRepository.save(updated);
    return ResponseEntity.ok().eTag(computeEtag(updated)).body(updated);
}
```

**Follow-up questions:**

- *"What happens if a client just ignores `If-Match` entirely?"* — It defeats the mechanism. For genuinely critical resources, make `If-Match` required and reject writes that omit it with `428 Precondition Required`.
- *"How does this relate to JPA's `@Version`?"* — Same pattern at two layers, often wired together so the entity's `@Version` value becomes the `ETag`.

**Sources:** [RFC 9110 §8.8 — ETag and Conditional Requests](https://datatracker.ietf.org/doc/html/rfc9110#section-8.8), [RFC 6585 — 428 Precondition Required](https://datatracker.ietf.org/doc/html/rfc6585)

---

## 11. When Should an API Return `200`, `201`, `202`, `204`, `400`, `409`, `422`, or `429`?

**Core answer:**

"`200 OK` is a successful request with a response body — the general-purpose success code for `GET`/`PUT`/`PATCH` and any non-creation `POST`. `201 Created` is a successful `POST` (or occasionally `PUT`) that created a new resource; it should include a `Location` header. `202 Accepted` means the request was validly received but is processed asynchronously (question 17/18). `204 No Content` is success with nothing to return — common for `DELETE`, or a write where the updated representation isn't echoed back.

`400 Bad Request` means the request is structurally malformed — invalid JSON, a missing required field — and couldn't even be validated against business rules. `409 Conflict` means the request is well-formed but conflicts with the resource's current state, like cancelling an order that's already shipped. `422 Unprocessable Entity` means the request is well-formed but fails business-rule validation, like a discount code that doesn't exist — it separates 'your request wasn't syntactically valid' from 'it was, but doesn't satisfy the rules.' `429 Too Many Requests` means the rate limit was exceeded, with a `Retry-After` header."

**Staff-level extension:**

`400` vs. `422` is one of the most inconsistently applied distinctions across real-world APIs. Plenty of production APIs use `400` for everything, which isn't strictly wrong but throws away a useful signal for clients trying to distinguish 'fix your request format' from 'your format is fine, but this business rule failed.' I'd pick a clear, documented convention up front — 422 for anything a client would reasonably want to handle differently, 400 for genuinely malformed requests that indicate a client bug — and enforce it via a shared exception-handling layer (`@ControllerAdvice` in Spring, mapping exception types to status codes centrally) rather than leaving each endpoint to decide ad hoc.

**Example:**

```http
POST /orders                          201 Created
Location: /orders/456                 { "id": "456", ... }

POST /orders/456/refund-requests      202 Accepted
{ "statusUrl": "/refund-requests/789" } # processing continues asynchronously

DELETE /orders/456                    204 No Content   # success, nothing to return

POST /orders                          400 Bad Request
{ "error": "malformed JSON at line 3" }  # structurally invalid, not even parseable
                                            # against the expected shape

POST /orders                          409 Conflict
{ "error": "an order with this external reference already exists" }

POST /orders                          422 Unprocessable Entity
{ "error": "discount code 'XYZ' does not exist" }  # WELL-FORMED request,
                                                       # fails a business rule

POST /orders                          429 Too Many Requests
Retry-After: 30
```

**Follow-up questions:**

- *"Is using `400` for everything wrong?"* — Not strictly, but it throws away a signal clients could otherwise react to programmatically.
- *"How do you enforce a consistent status-code convention across an API?"* — A shared exception-handling layer (`@ControllerAdvice` in Spring) mapping exception types to status codes centrally, not per-endpoint judgment calls.

**Sources:** [RFC 9110 §15 — Status Codes](https://datatracker.ietf.org/doc/html/rfc9110#section-15), [RFC 4918 §11.2 — 422 Unprocessable Entity](https://datatracker.ietf.org/doc/html/rfc4918#section-11.2)

---

## 12. What Should a Consistent Error Response Contain?

**Core answer:**

"I'd standardize on a single, consistent error response shape across the entire API, ideally following an established standard rather than inventing a bespoke one — a standard format lets generic client-side error-handling tooling work across many APIs without custom parsing per service. **RFC 9457 (Problem Details for HTTP APIs)** is the current, well-adopted standard: a `type` (a URI identifying the error category, ideally dereferenceable to documentation), a `title` (a short, human-readable summary), a `status` (the HTTP status code, repeated in the body), a `detail` (a human-readable explanation specific to this occurrence), and an `instance` (a URI identifying this occurrence, useful for correlating with server-side logs).

Beyond the RFC 9457 baseline, I'd include a `traceId`/`requestId` correlating the response to server-side logs and traces, and, for validation errors specifically, a structured list of field-level errors (question 13) rather than cramming everything into one prose `detail` string."

**Staff-level extension:**

Adopting a real standard rather than a bespoke `{error: "..."}` shape has an underappreciated benefit: client libraries, API gateways, and observability tooling increasingly understand `application/problem+json` natively, and a `type` URI that dereferences to real documentation gives both humans and tooling a stable, linkable identity for a specific error category — rather than an error message string that might get reworded and silently break any client pattern-matching on it. Error responses are also a common, easy-to-miss security leak point. Stack traces, internal exception messages, or SQL error text surfacing in a `detail` field in production is a real information-disclosure risk, so error-handling middleware needs a deliberate mapping from internal exceptions to safe, external-facing `detail` messages — never a blanket "just serialize the exception."

**Example:**

```json
// RFC 9457 Problem Details — the standardized baseline shape
{
  "type": "https://api.example.com/errors/insufficient-inventory",
  "title": "Insufficient inventory",
  "status": 422,
  "detail": "Only 2 units of SKU 'WIDGET-100' are available, but 5 were requested.",
  "instance": "/orders/456",
  "traceId": "4bf92f3577b34da6a3ce929d0e0e4736"   // custom extension field —
}                                                    // RFC 9457 explicitly allows
                                                       // additional members beyond the base set
```

```json
// Content-Type for RFC 9457 responses — a REAL, standardized media type,
// not just "application/json" with a conventionally-shaped body
// Content-Type: application/problem+json
```

**Follow-up questions:**

- *"What's the risk of a bespoke error format vs. a standard one?"* — Generic tooling (gateways, observability, client libraries) can't understand it natively, and a reworded message string can silently break clients pattern-matching on it.
- *"What's a common security mistake in error responses?"* — Letting stack traces or internal exception/SQL text leak into a production `detail` field. It needs a deliberate mapping to safe external messages.

**Sources:** [RFC 9457 — Problem Details for HTTP APIs](https://datatracker.ietf.org/doc/html/rfc9457)

---

## 13. How Should Validation Errors Be Represented?

**Core answer:**

"For a single overall request failure, I'd use the RFC 9457 shape from the previous question, but extend it with a structured, **per-field** list of validation errors — not one flattened `detail` string trying to describe multiple field problems in prose. Each entry should identify the specific field or path that failed (ideally via a JSON Pointer, matching the addressing convention JSON Patch uses, question 9), a machine-readable error code so a client can react programmatically without string-matching human-readable text, and a human-readable message as a fallback display default.

This matters for the actual client-side experience: a form needs to map 'the `email` field is invalid' to that specific input box, and an i18n layer needs a stable error code to look up a localized message from, rather than parsing an English sentence that might change wording between API versions."

**Staff-level extension:**

Machine-readable error **codes**, not just field names, are the detail most APIs get wrong or skip entirely, and they're what actually enables good client-side UX at scale. Without a stable code, a frontend either has to fragile-string-match the message — which breaks the moment the wording changes, even for a harmless copy edit — or just show the raw server message untranslated, a poor experience for any multi-locale product. I'd define and version the error-code vocabulary as a first-class part of the API contract, the same way status codes and response schemas are. Treating error codes as an afterthought is a common gap that shows up painfully once a client team tries to build good, localized error UX against the API.

**Example:**

```json
{
  "type": "https://api.example.com/errors/validation-failed",
  "title": "Validation failed",
  "status": 422,
  "detail": "The request contains 2 validation errors.",
  "errors": [
    {
      "field": "/email",                 // JSON Pointer — same convention as JSON Patch
      "code": "INVALID_FORMAT",           // machine-readable — client reacts on THIS,
      "message": "must be a valid email address"  // not on the prose message
    },
    {
      "field": "/shippingAddress/postalCode",
      "code": "REQUIRED_FIELD_MISSING",
      "message": "postal code is required"
    }
  ]
}
```

```java
@ExceptionHandler(MethodArgumentNotValidException.class)
ResponseEntity<ProblemDetail> handleValidation(MethodArgumentNotValidException ex) {
    List<FieldError> fieldErrors = ex.getBindingResult().getFieldErrors().stream()
        .map(fe -> new FieldError("/" + fe.getField(), mapToErrorCode(fe), fe.getDefaultMessage()))
        .toList();
    ProblemDetail problem = ProblemDetail.forStatus(HttpStatus.UNPROCESSABLE_ENTITY);
    problem.setProperty("errors", fieldErrors); // structured, not a single prose string
    return ResponseEntity.status(422).body(problem);
}
```

**Follow-up questions:**

- *"Why use a JSON Pointer for the field path instead of a plain field name?"* — Consistency with JSON Patch's addressing convention (question 9): one path syntax across the API.
- *"Should the error-code vocabulary be documented like the rest of the API contract?"* — Yes, versioned and documented per code, the same way status codes and response schemas are.

**Sources:** [RFC 9457 — Problem Details for HTTP APIs](https://datatracker.ietf.org/doc/html/rfc9457), [RFC 6901 — JSON Pointer](https://datatracker.ietf.org/doc/html/rfc6901)

---

## 14. Compare URI, Header, and Media-Type API Versioning

**Core answer:**

"**URI versioning** (`/v1/orders`, `/v2/orders`) embeds the version directly in the path. It's the most visible and simplest option for clients and API-gateway routing and caching to reason about, but it means a resource's URI technically changes across versions — a real, if often-tolerated, violation of the REST principle that a URI identifies a resource independent of representation.

**Header versioning** (a custom header like `Api-Version: 2`) keeps the URI stable, with the same resource identity and the version negotiated separately. It's more architecturally 'correct,' but less visible and harder for some caching or gateway layers to route on cleanly, since caching keyed purely by URL now needs to also vary by header.

**Media-type versioning** (content negotiation via `Accept: application/vnd.example.v2+json`) folds the version into the standard HTTP content-negotiation mechanism. It's arguably the most 'correct' option from a pure HTTP-semantics standpoint, but it's the least commonly understood pattern among typical API consumers, with generally weaker tooling support than the other two."

**Staff-level extension:**

The pragmatic recommendation: for most public-facing APIs, URI versioning wins in practice because of its simplicity and visibility. It's what most widely-used public APIs actually do — Stripe, GitHub, and most major providers use version-in-the-path or a simple header, rarely pure media-type negotiation — and fighting that ecosystem convention has a real developer-experience cost for consumers who expect the common pattern. I'd reserve header or media-type versioning for internal APIs where the consuming teams are known and the stronger architectural correctness is worth the reduced visibility. Regardless of mechanism, the harder problem is the actual **versioning policy** (question 15/16): how long old versions stay supported, and how breaking changes get communicated.

**Example:**

```http
# URI versioning — simplest, most visible, but the resource "URI" changes per version
GET /v1/orders/123
GET /v2/orders/123

# Header versioning — stable URI, version negotiated separately
GET /orders/123
Api-Version: 2

# Media-type versioning — version folded into standard HTTP content negotiation
GET /orders/123
Accept: application/vnd.example.order.v2+json
```

**Follow-up questions:**

- *"What do most major public APIs actually use?"* — URI versioning — Stripe, GitHub, and most major providers, rarely pure media-type negotiation.
- *"Does the versioning mechanism matter more than the policy?"* — No — how long old versions are supported and how breaking changes are communicated matters far more than which mechanism was chosen.

**Sources:** [RFC 9110 §12 — Content Negotiation](https://datatracker.ietf.org/doc/html/rfc9110#section-12), [Stripe API Versioning](https://stripe.com/docs/api/versioning)

---

## 15. How Would You Evolve an API Without Breaking Existing Clients?

**Core answer:**

"The core discipline is distinguishing changes that are genuinely backward-compatible (question 16) from those that aren't, and defaulting to the compatible kind whenever the actual requirement allows it. Safe, non-breaking changes: adding a new, optional field to a response; adding a new, optional request parameter with a sensible default; adding an entirely new endpoint; adding a new enum value **if and only if** clients are contractually expected to handle unknown values gracefully; relaxing a validation constraint.

Breaking changes: removing or renaming any existing field; changing a field's type or semantic meaning; adding a new *required* field or parameter; tightening validation to reject previously-accepted input; changing a status code for an existing scenario. For genuinely breaking changes that are unavoidable, I'd reach for versioning (question 14) combined with a real deprecation policy (question 25) — running old and new versions in parallel for a defined support window."

**Staff-level extension:**

The enum-value caveat is worth stating explicitly, since it's a common source of accidental breakage: adding a new enum value is only safe if the API's documented contract *already* told clients to treat unknown values as a graceful fallback (a `default` case in a switch, not a hard failure) — if that expectation was never established, adding a new value can break clients that reasonably assumed the enum was closed and exhaustive, and I'd treat this as effectively a breaking change unless the forward-compatibility contract was explicit from the start. Contract testing (Pact, or an OpenAPI-spec-diff tool run in CI) is the actual mechanism for *enforcing* backward compatibility rather than relying on developer discipline and code review alone — a CI check that diffs the current spec against the previous release and fails the build on a breaking-change pattern catches the mistake at the moment it's introduced, far cheaper than catching it after a client breaks in production.

**Example:**

```json
// SAFE — new OPTIONAL field added to a response; existing clients that don't
// know about "estimatedDeliveryDate" simply ignore it, nothing breaks
{
  "id": "123",
  "status": "shipped",
  "estimatedDeliveryDate": "2026-01-15"   // NEW field — additive, non-breaking
}
```

```java
// SAFE client-side pattern that MAKES new enum values non-breaking —
// but only if this defensive handling was part of the documented contract
// from the start, not something every client happened to do by luck
switch (order.getStatus()) {
    case "pending" -> handlePending(order);
    case "shipped" -> handleShipped(order);
    default -> handleUnknownStatus(order); // gracefully handles a FUTURE new value,
}                                             // rather than crashing/misbehaving on it
```

**Follow-up questions:**

- *"Is adding a new enum value always safe?"* — Only if the documented contract already told clients to treat unknown values gracefully — otherwise treat it as a breaking change.
- *"Does 'additive changes are safe' hold for every client?"* — Only if clients are actually built to ignore unknown fields and tolerate new enum values — a strict/schema-validating client can still break on an additive change.

**Sources:** [Stripe — API Versioning and backward compatibility](https://stripe.com/docs/upgrades), [Pact — Contract Testing](https://docs.pact.io/)

---

## 16. How Do You Define Backward Compatibility?

**Core answer:**

"I'd define it precisely, since 'backward compatible' is often used loosely: a change is backward-compatible if **every existing, correctly-written client, calling the API exactly as it did before the change, continues to function correctly without any modification** — same requests succeed the same way, same response shapes are still valid to whatever the client's existing parsing/handling logic expects.

The precision that matters: 'continues to function correctly' has to be evaluated against what clients are *contractually entitled to assume*, not just what happens to technically still parse. A client using a JSON library that silently ignores unknown fields will 'still work' if a new field is added, but a client using strict schema validation that rejects unknown properties will break on the exact same change — whether that counts as 'backward compatible' depends on what the API's documented contract actually promised clients. I'd always pair the technical definition with an explicit, published compatibility contract — without a stated contract, 'is this change backward compatible' is genuinely ambiguous, since it depends on assumptions about client behavior the API team doesn't actually control."

**Staff-level extension:**

This published-contract approach is exactly how major API providers (Stripe is a commonly cited example) manage to add fields and even new enum values within a stable major version without it counting as a breaking change — the contract with clients was established up front, clients are expected (and, in Stripe's case, their official client libraries are actually built) to honor it, and the API provider can then evolve additively with confidence. "Backward compatible" isn't a property you can assess purely by inspecting the diff between two API versions in isolation — it's a property that depends on an explicit, agreed contract between API provider and consumers about what each side is allowed to assume, and defining that contract clearly up front is a prerequisite for being able to reason about compatibility at all, not an optional nicety.

**Example:**

```yaml
# A concrete, PUBLISHED compatibility contract — this is what actually makes
# "backward compatible" an evaluable, non-ambiguous claim, rather than a vibe
compatibility_policy:
  clients_must:
    - ignore unrecognized fields in JSON responses
    - tolerate unrecognized values in enum-like string fields (treat as a default/fallback case)
    - not rely on the ORDER of fields in a JSON object
    - not rely on undocumented fields or behavior
  api_guarantees_within_a_major_version:
    - existing fields will not be removed or repurposed to mean something different
    - existing required request parameters will not become MORE restrictive
    - existing status codes for documented scenarios will not change
    - new fields may be added to responses at any time
    - new optional request parameters may be added at any time
```

**Follow-up questions:**

- *"Can you assess 'backward compatible' just by diffing two API versions?"* — No — it depends on the agreed contract about what clients are entitled to assume, which isn't visible in a diff alone.
- *"How does Stripe manage to add enum values without it being a breaking change?"* — The compatibility contract was established up front, and their official client libraries are built to honor it.

**Sources:** [Stripe — API Versioning](https://stripe.com/docs/upgrades), [Google API Improvement Proposals — Compatibility](https://google.aip.dev/180)

---

## 17. How Should Long-Running Operations Be Modeled?

**Core answer:**

"An operation that can't complete within a normal synchronous request/response cycle (a report generation, a bulk data export) shouldn't be forced into a blocking `POST` that holds the connection open until it finishes — that's fragile (client/proxy timeouts, a dropped connection losing the result entirely) and doesn't give the client any way to check progress or recover if its own process restarts mid-wait.

The standard pattern: the initiating request returns immediately with `202 Accepted` and a representation of the **operation itself** as a resource (not the eventual result) — including a URL the client can poll to check status, and a `Location` header pointing at it. The operation resource's status field progresses through well-defined states (`pending` → `in_progress` → `completed`/`failed`), and once complete, either includes the result directly or links to where it can be fetched. This turns a long-running process into an ordinary resource lifecycle the client can poll, be interrupted and resume checking on, and reason about using the same tools as any other resource."

**Staff-level extension:**

Webhooks are the complementary alternative to polling, worth offering alongside (or instead of) it for operations that can take a genuinely long time — rather than repeatedly polling, the client registers a callback URL up front and the server calls it once the operation completes; more efficient and near-immediate, at the cost of requiring the client to expose a reachable HTTP endpoint of its own, which not every client (especially browser-based/mobile) can do — this is exactly why many APIs offer both. The operation resource's status transitions should themselves be well-documented and exhaustive (including failure states with actionable error detail, per question 12) — a client polling an operation needs to know definitively when to stop and how to distinguish "still working" from "failed, here's why" from "succeeded, here's the result."

**Example:**

```http
POST /reports
{ "type": "quarterly-revenue", "quarter": "2026-Q1" }

202 Accepted
Location: /operations/op-789
{ "id": "op-789", "status": "pending", "createdAt": "2026-01-15T10:00:00Z" }

# Client polls the operation resource to check progress
GET /operations/op-789
200 OK
{ "id": "op-789", "status": "in_progress", "progressPercent": 40 }

# Once complete, the operation resource links to (or includes) the actual result
GET /operations/op-789
200 OK
{
  "id": "op-789",
  "status": "completed",
  "result": { "reportUrl": "/reports/rep-456" }
}
```

**Follow-up questions:**

- *"Why not just use webhooks instead of polling?"* — Not every client can expose a reachable HTTP endpoint (browser-based/mobile clients especially) — polling is the universally-available baseline, webhooks an optional efficiency add-on.
- *"How does a client know when to stop polling?"* — The operation resource's states must be exhaustive and documented, distinguishing "still working" from "failed" from "succeeded" unambiguously.

**Sources:** [Google AIP — Long-running operations](https://google.aip.dev/151), [Microsoft REST API Guidelines — Long running operations](https://github.com/microsoft/api-guidelines/blob/vNext/azure/Guidelines.md#long-running-operations)

---

## 18. How Do You Design Asynchronous REST Workflows?

**Core answer:**

"Building on the previous question's operation-resource pattern, a genuinely asynchronous *workflow* (as opposed to a single long-running operation) often involves multiple steps, some of which might themselves be async, and I'd model the overall thing as its own resource with an explicit state machine, rather than trying to force it into a single request/response exchange.

Concretely: the workflow resource (`/order-fulfillments/{id}`) exposes its current state (`reserved` → `paid` → `shipped` → `delivered`, or with explicit failure branches like `payment_failed`, `inventory_unavailable`) and, ideally, a history/timeline of state transitions for observability. State transitions are triggered either by client action or by events from other systems (a payment webhook arriving, an inventory system confirming reservation) — and I'd design the resource so a client can always `GET` the current state to reconcile, rather than *only* relying on push notifications/webhooks that could be missed."

**Staff-level extension:**

For any given workflow, I'd draw out the actual state diagram explicitly as part of the design — nailing down every valid transition and every terminal/failure state up front avoids the common failure mode of an ad hoc, undocumented, and inconsistent set of status values accumulating organically as edge cases get discovered in production. The actual, recurring staff-level failure mode here isn't picking the wrong HTTP mechanics — it's under-designing the state machine itself: teams that don't draw out every valid transition and terminal state explicitly up front tend to accumulate ad hoc status values and undocumented edge-case transitions organically as production incidents reveal gaps. I'd advocate for treating the state diagram as a genuine design artifact reviewed before implementation (the same rigor a database schema migration would get), and for building in an explicit "unknown/unexpected transition" guard in the implementation itself — an attempted transition that isn't valid from the current state should be rejected with a clear `409 Conflict` and a specific error code, not silently allowed or ignored.

**Example:**

```json
// The workflow itself is a first-class, pollable/observable resource
GET /order-fulfillments/456
{
  "id": "456",
  "orderId": "123",
  "state": "payment_processing",
  "history": [
    { "state": "reserved", "at": "2026-01-15T10:00:00Z" },
    { "state": "payment_processing", "at": "2026-01-15T10:00:05Z" }
  ],
  "_links": {
    "cancel": { "href": "/order-fulfillments/456/cancellation", "method": "POST" }
  }
}
```

```text
State diagram, explicitly designed BEFORE implementation, not discovered ad hoc:

  reserved --> payment_processing --> paid --> shipped --> delivered
     |               |
     v               v
  cancelled     payment_failed --> reserved (retry) or cancelled (give up)
```

**Follow-up questions:**

- *"What should happen on an invalid state transition attempt?"* — Reject it with a clear `409 Conflict` and a specific error code — never silently allow or ignore it.
- *"When should the state diagram itself be reviewed?"* — Before implementation, with the same rigor a database schema migration would get — not discovered ad hoc as incidents reveal gaps.

**Sources:** [Google AIP — Long-running operations](https://google.aip.dev/151), [AWS Step Functions — State machine design](https://docs.aws.amazon.com/step-functions/latest/dg/concepts-states.html)

---

## 19. How Would You Expose Bulk Operations With Partial Success?

**Core answer:**

"A bulk endpoint (`POST /orders/batch` accepting an array of order-creation requests) genuinely can't be all-or-nothing in most realistic designs — if item 47 out of 100 fails validation, forcing the entire batch to fail (and requiring the client to resubmit all 100, including the 46 that would have succeeded) is usually worse UX and worse efficiency than processing each item independently and reporting per-item results.

The pattern I'd use: the response is itself an array with one entry per submitted item, explicitly correlated via a client-supplied ID per item, each carrying its own success/failure status and, for failures, the same structured validation-error detail from question 13 — scoped to that specific item. I'd generally use `207 Multi-Status` (borrowed from WebDAV) to signal 'the request itself was processed, but individual items had mixed outcomes' — distinct from a clean `200`/`201` or a `4xx` implying the whole request failed."

**Staff-level extension:**

Partial-success batch semantics need to be paired with a clear **idempotency** story for the batch as a whole, not just individual items (tying back to question 5) — if a client retries an entire failed/partially-failed batch, it needs a way to avoid re-processing the items that *already* succeeded, which usually means either per-item idempotency keys within the batch, or the client being expected to resubmit only the failed subset. Very large batches deserve an explicit size limit and, beyond a certain size, should be redirected to the async-operation pattern (question 17) entirely — a bulk endpoint processing 10,000 items synchronously within one HTTP request/response cycle is fragile regardless of how well the partial-success reporting is designed.

**Example:**

```json
// POST /orders/batch
// Request: an array of order-creation payloads, each with a client-supplied
// correlation ID so the client can match results back to its own inputs
{
  "items": [
    { "clientRef": "req-1", "sku": "WIDGET-1", "quantity": 2 },
    { "clientRef": "req-2", "sku": "WIDGET-2", "quantity": 999999 }
  ]
}

// 207 Multi-Status — the batch request itself was processed; individual
// items had MIXED outcomes, each reported independently
{
  "results": [
    { "clientRef": "req-1", "status": 201, "order": { "id": "order-501" } },
    {
      "clientRef": "req-2", "status": 422,
      "error": { "code": "INSUFFICIENT_INVENTORY", "message": "only 10 units available" }
    }
  ]
}
```

**Follow-up questions:**

- *"What happens if a client retries a partially-failed batch?"* — It needs per-item idempotency keys, or should resubmit only the failed subset (via `clientRef`) rather than the whole original batch.
- *"What about a batch of 10,000 items?"* — Redirect it to the async-operation pattern (question 17) — a synchronous batch that large is fragile regardless of how good the partial-success reporting is.

**Sources:** [RFC 4918 §11.1 — 207 Multi-Status](https://datatracker.ietf.org/doc/html/rfc4918#section-11.1), [Google AIP — Batch methods](https://google.aip.dev/231)

---

## 20. How Do Retries Interact With Timeouts and Duplicate Requests?

**Core answer:**

"The core danger is that a **timeout is fundamentally ambiguous** — the client doesn't know whether the server never received the request, received it but hasn't finished, or actually completed successfully and only the *response* was lost in transit. A naive retry policy that resends on any timeout risks duplicating the effect of a request that already succeeded server-side, which is exactly why idempotency (question 5) has to be designed in *before* any retry logic, not as an afterthought.

The safe retry discipline: only automatically retry requests that are either inherently idempotent (`GET`/`PUT`/`DELETE`) or explicitly made idempotent via an idempotency key (`POST`); use **exponential backoff with jitter** between attempts, both to give a struggling downstream service room to recover and to avoid many clients retrying in lockstep (the 'thundering herd' pattern); and set a **retry budget/ceiling** rather than retrying indefinitely, since an indefinitely-retrying client during a real outage just adds sustained load to an already-struggling system."

**Staff-level extension:**

The thundering-herd/retry-storm dynamic connects to a real production failure pattern: a downstream dependency has a brief blip, many clients simultaneously time out and retry, and if those retries are synchronized (no jitter) or unbounded (no ceiling), the retry traffic itself can be *larger* than the original load that caused the blip, turning a brief, recoverable degradation into a much longer, self-sustaining outage — a system's own well-intentioned reliability mechanism becoming the actual cause of prolonged unavailability. Retry policy has to be designed with the *aggregate, system-wide* effect in mind, not just "will this individual client's request eventually succeed" — jitter, backoff, retry budgets, and ideally client-side circuit breakers all exist specifically to prevent a client-side reliability feature from becoming a server-side reliability liability.

**Example:**

```java
// Exponential backoff with jitter — the standard, safe retry shape
RetryTemplate retryTemplate = RetryTemplate.builder()
    .maxAttempts(4)
    .exponentialBackoff(200, 2.0, 5000) // 200ms initial, doubling, 5s cap
    .retryOn(TimeoutException.class, HttpServerErrorException.class) // NOT on
    .build();                                                          // 4xx client errors —
                                                                          // those won't succeed
                                                                          // on retry anyway

// Applying jitter explicitly — WITHOUT it, many clients that all started
// retrying at the same moment (e.g., all timed out from the same brief
// outage) would retry in lockstep, re-creating the overload they're
// trying to recover from
long baseDelayMs = 200 * (long) Math.pow(2, attemptNumber);
long jitteredDelayMs = baseDelayMs / 2 + ThreadLocalRandom.current().nextLong(baseDelayMs / 2);
```

**Follow-up questions:**

- *"Why is jitter necessary, not just backoff?"* — Without it, many clients that timed out from the same brief blip retry in lockstep, re-creating the overload they're trying to recover from.
- *"What stops a client from retrying forever during a real outage?"* — A retry budget/ceiling, and ideally a client-side circuit breaker that stops retrying once failure rate crosses a threshold.

**Sources:** [AWS Architecture Blog — Exponential Backoff and Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/), [Google SRE Workbook — Retries](https://sre.google/sre-book/handling-overload/)

---

## 21. How Do You Protect an API From Retry Storms?

**Core answer:**

"Building directly on the previous question, protection needs to happen on both the client side (well-behaved retry policies — backoff, jitter, budgets, circuit breakers) *and* the server side, since I wouldn't want to rely purely on every client implementing good retry hygiene correctly — some won't, whether due to a bug, a third-party client library with poor defaults, or a client team that just didn't think about it.

Server-side defenses: rate limiting (question 22) to cap how much load any single client/tenant can generate regardless of why; the `Retry-After` header on `429`/`503` responses, giving well-behaved clients an explicit, authoritative signal for how long to wait rather than guessing; load-shedding (deliberately rejecting some requests fast, with a clear `503`, rather than accepting every request and having *all* of them time out slowly); and, at the API-gateway or service-mesh layer, a circuit breaker that can detect a downstream dependency is unhealthy and start failing fast rather than letting every request queue up waiting on a dependency that's clearly not going to respond in time."

**Staff-level extension:**

Load-shedding is the counterintuitive-but-correct move during a genuine overload event: deliberately rejecting a *fraction* of incoming requests immediately and cheaply preserves the system's ability to serve at least *some* requests successfully, which is strictly better than accepting everything and serving nothing successfully — a trade-off many teams are hesitant to build deliberately (it feels wrong to reject a request you could theoretically serve), but a well-established resilience pattern precisely because the alternative is worse for every caller. I'd also connect this to bulkheading — isolating resource pools (connection pools, thread pools) per downstream dependency, so a retry storm or overload hitting *one* dependency doesn't exhaust resources shared with calls to *other*, unrelated dependencies.

**Example:**

```java
// Server-side circuit breaker — fails FAST once a downstream dependency is
// clearly unhealthy, rather than letting every request queue up and time out
// slowly, which would waste this service's own resources during an incident
@CircuitBreaker(name = "inventoryService", fallbackMethod = "fallbackInventoryCheck")
InventoryStatus checkInventory(String sku) {
    return inventoryClient.check(sku);
}

InventoryStatus fallbackInventoryCheck(String sku, Exception ex) {
    // return a cheap, immediate degraded response instead of hanging —
    // protects THIS service's own thread pool from being exhausted by
    // requests waiting on a downstream dependency that's already unhealthy
    return InventoryStatus.unknown();
}
```

```http
# Explicit, authoritative signal for well-behaved clients — removes the
# guesswork from client-side backoff timing entirely
503 Service Unavailable
Retry-After: 60
```

**Follow-up questions:**

- *"Isn't rejecting requests you could theoretically serve a bad idea?"* — No — accepting everything and having all of them time out slowly is strictly worse for every caller than shedding a fraction fast.
- *"What's bulkheading, and why does it matter here?"* — Isolating resource pools per downstream dependency, so one misbehaving dependency's overload can't exhaust resources shared with calls to unrelated dependencies.

**Sources:** [Google SRE Workbook — Handling Overload](https://sre.google/sre-book/handling-overload/), [Resilience4j — Circuit Breaker](https://resilience4j.readme.io/docs/circuitbreaker)

---

## 22. How Would You Implement Rate Limiting for Tenants With Different Quotas?

**Core answer:**

"I'd model rate limits as a per-tenant (or per-API-key, per-client) configuration rather than a single global limit, since different tenants legitimately have different contracted throughput needs (a free tier, a standard paid tier, an enterprise tier with a negotiated higher quota) — the rate-limiting mechanism itself (token bucket, sliding window) stays the same, but the *limit value and window* it enforces is looked up per-tenant at request time, from the tenant's identity (extracted from the authenticated token/API key) rather than anything client-suppliable.

Beyond the mechanism, I'd expose the current rate-limit state transparently to clients via standard headers (`RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`) on *every* response, not just the one that finally exceeds the limit — this lets well-behaved clients self-throttle proactively rather than only discovering the limit reactively after being rejected. And I'd design tiered limits with **burst allowance** in mind (a token-bucket-style limiter naturally supports this), since real traffic is rarely perfectly smooth."

**Staff-level extension:**

Rate limits should be enforced consistently at the edge (an API gateway) for coarse, tenant-level throughput protection, but sometimes *also* need finer-grained, endpoint-specific limits underneath (a tenant's overall quota might be generous, but one specific expensive endpoint — a bulk export, a heavy search query — might need its own tighter, independent limit regardless of the tenant's general headroom). Rate-limit configuration itself needs to be dynamically adjustable without a deployment (a tenant upgrading their plan, or a temporary limit increase during a negotiated traffic spike, shouldn't require a code change and redeploy) — backing tenant quotas with a configuration store that can be updated live, rather than hardcoding tier limits into application code, is the actual staff-level operational requirement here, not just picking the right algorithm.

**Example:**

```java
@Component
class TenantRateLimiter {
    private final RedisTemplate<String, String> redis;

    boolean allowRequest(String tenantId) {
        TenantQuota quota = quotaRepository.findByTenantId(tenantId); // per-tenant,
        // looked up from the AUTHENTICATED principal's tenant, never client-suppliable
        String key = "ratelimit:" + tenantId;
        // token-bucket check via a Lua script for atomicity (Redis/Caching category
        // covers this exact pattern in depth)
        return tokenBucketScript.evaluate(redis, key, quota.getCapacity(), quota.getRefillRate());
    }
}
```

```http
# Exposed on EVERY response, not just the one that finally gets rejected —
# lets well-behaved clients self-throttle proactively
200 OK
RateLimit-Limit: 1000
RateLimit-Remaining: 42
RateLimit-Reset: 30

429 Too Many Requests
Retry-After: 30
```

**Follow-up questions:**

- *"Is a single per-tenant limit always enough?"* — No — one specific expensive endpoint (a bulk export, a heavy search) may need its own tighter limit regardless of the tenant's general headroom.
- *"Should tier limits be hardcoded into application code?"* — No — back tenant quotas with a live-updatable configuration store, so a plan upgrade doesn't require a deployment.

**Sources:** [IETF Draft — RateLimit header fields](https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/), [Stripe — Rate Limits](https://stripe.com/docs/rate-limits)

---

## 23. What Is the Difference Between Readiness, Liveness, and Business Health?

**Core answer:**

"Readiness and liveness are covered in depth in the Spring Boot Internals file — readiness answers 'can this instance currently accept and correctly handle traffic,' liveness answers 'is this instance in a broken internal state that only a restart fixes' — and both are infrastructure-facing signals meant for an orchestrator (Kubernetes) to make routing/restart decisions, deliberately narrow and mechanical in what they check.

**Business health** is a distinct, broader concept: not 'is this specific process alive and accepting connections,' but 'is the *system as a whole* actually functioning correctly from a business-outcome perspective' — are orders actually completing end-to-end, is the payment success rate within a normal range, is the checkout conversion funnel behaving as expected. This is monitored differently (business-metric dashboards and alerting, not a Kubernetes probe), aimed at a different audience, and it can be degraded even when every individual service reports itself perfectly ready and alive."

**Staff-level extension:**

The specific incident pattern this distinction is meant to catch: every service reporting green (ready, alive) while the *actual business outcome* customers care about is broken — a classic real-world example is a payment gateway integration where the gateway itself is technically reachable and responding (so any naive health check treats it as "up"), but is silently returning valid-shaped decline responses for every single transaction due to a misconfiguration on either side. No service-level health check catches this, since nothing crashed or became unreachable, but the business is fully down from a revenue perspective. Business-health dashboards and alerts are a genuinely necessary, separate layer of observability a mature platform needs *in addition to* readiness/liveness — treating "all my services report healthy" as equivalent to "the product is working" is a real, common, and dangerous conflation.

**Example:**

```text
Readiness (per-instance, infrastructure-facing):
  GET /actuator/health/readiness -> "can THIS instance serve traffic right now?"

Liveness (per-instance, infrastructure-facing):
  GET /actuator/health/liveness -> "is THIS instance in a broken state needing a restart?"

Business health (system-wide, outcome-facing) — NOT a simple HTTP probe at all,
typically a dashboard/alerting system built on business metrics:
  - order completion rate over the last 15 minutes, vs. historical baseline
  - payment success rate, vs. historical baseline
  - checkout funnel conversion, vs. historical baseline
  - "are orders ACTUALLY going through end-to-end", not "is every service's
    /health endpoint returning 200"
```

**Follow-up questions:**

- *"Would a readiness probe catch a payment gateway silently declining every transaction?"* — No — the gateway is technically reachable and responding, so the probe reports "up" while the business is fully down.
- *"Who's the audience for business-health signals vs. readiness/liveness?"* — On-call engineers and business stakeholders investigating "is the product working for customers," not an orchestrator deciding whether to restart a pod.

**Sources:** [Spring Boot Reference — Kubernetes Probes](https://docs.spring.io/spring-boot/reference/actuator/endpoints.html#actuator.endpoints.kubernetes-probes), [Google SRE Book — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)

---

## 24. How Should Distributed Tracing Context Propagate?

**Core answer:**

"A single logical request in a microservices architecture typically fans out across many service calls, and distributed tracing exists to reconstruct that whole causal chain as one coherent trace, rather than a pile of disconnected per-service logs someone has to manually correlate after the fact.

The mechanism: a **trace ID** (identifying the entire end-to-end request) and a **span ID** (identifying this specific hop) are generated at the very first entry point (or extracted from an incoming request if this service isn't the true origin), and every *outgoing* call this service makes needs to propagate that same trace ID (with a new span ID, referencing the calling span as its parent) forward via standard, interoperable headers — the current standard being the **W3C Trace Context** spec (`traceparent`/`tracestate`), which most modern tracing libraries (OpenTelemetry being dominant now) implement natively rather than requiring custom propagation code."

**Staff-level extension:**

The practical failure mode when this isn't done correctly: any hop that doesn't propagate the incoming trace context forward (a service that generates a *new*, unrelated trace ID for its downstream calls instead of continuing the one it received) breaks the trace into disconnected fragments at exactly that point — the trace suddenly 'ends' at that service from the perspective of anyone trying to follow the full request through the system, which is exactly the kind of gap that turns a 10-minute root-cause investigation into a multi-hour one during an actual incident. Async/messaging boundaries (Kafka in particular) are the most common place trace propagation silently breaks, since it requires the trace context to be explicitly embedded in the message's headers at *publish* time and explicitly extracted and continued at *consume* time — this doesn't happen automatically the way a synchronous HTTP call's context propagation often does via auto-instrumentation. Ensuring end-to-end trace continuity across every hop — including async boundaries specifically — is a genuine platform-engineering investment worth prioritizing deliberately, since its absence doesn't show up as a bug in normal operation, only as dramatically slower incident investigation exactly when speed matters most.

**Example:**

```http
# Incoming request already carries trace context from an upstream caller
GET /orders/123
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
             ^^ version  ^^ trace-id (32 hex)      ^^ parent span-id  ^^ flags
```

```java
// The service MUST propagate the SAME trace-id forward on every outgoing call,
// with a NEW span-id representing this hop, parented to the incoming span
@GetMapping("/orders/{id}")
Order getOrder(@PathVariable String id) {
    // OpenTelemetry instrumentation handles this automatically for
    // supported HTTP clients/database drivers/Kafka producers — but it's
    // worth understanding WHY it matters, not just enabling the auto-instrumentation:
    InventoryStatus inventory = inventoryClient.check(id); // trace context propagated
    // automatically via the instrumented HTTP client, continuing the SAME trace-id
    return orderRepository.findById(id);
}
```

**Follow-up questions:**

- *"Does trace context propagate automatically across a Kafka publish/consume boundary?"* — No — it must be explicitly embedded in message headers at publish time and extracted at consume time; auto-instrumentation usually only covers synchronous HTTP.
- *"What does a broken trace look like in practice?"* — It 'ends' abruptly at the hop that didn't propagate context, with no visible connection to whatever happened downstream.

**Sources:** [W3C Trace Context specification](https://www.w3.org/TR/trace-context/), [OpenTelemetry documentation](https://opentelemetry.io/docs/)

---

## 25. How Would You Safely Deprecate an Endpoint Used by Unknown Consumers?

**Core answer:**

"'Unknown consumers' is the crux of the difficulty — for an internal API where every caller is a known, cooperating team, deprecation is mostly a communication and coordination problem. For a public API (or an internal API that's been around long enough that nobody's fully sure who's still calling an old endpoint), the discipline has to be more conservative and evidence-based, since you genuinely can't just ask everyone to confirm they've migrated.

My approach: first, **instrument the endpoint to measure actual usage** before assuming anything about who's still calling it — logging caller identity and volume over a long enough window to catch infrequent-but-real usage. Second, **communicate the deprecation explicitly and with real lead time** — via the `Deprecation` and `Sunset` HTTP headers (RFC 8594) on every response, so even automated clients get a machine-readable signal, plus direct outreach to any *identified* caller. Third, **only actually remove it once usage has genuinely dropped to zero** for a sustained period — not on a fixed calendar date chosen without regard to actual measured migration progress."

**Staff-level extension:**

The actual hard part of deprecating a public-facing or long-lived internal endpoint isn't the mechanism (headers, documentation) — it's the organizational discipline of genuinely measuring usage before committing to a removal date, and being willing to *delay* the removal if the data shows meaningful residual usage, rather than treating a previously-announced sunset date as immovable regardless of what the actual telemetry says. Teams that pick a sunset date up front, communicate it once, and then remove the endpoint on schedule regardless of measured usage risk a real, avoidable outage for whatever caller didn't get the message (a legacy internal batch job nobody remembered, a small partner integration that was never in the direct communication loop) — the safer, more mature practice treats the sunset date as a target informed by ongoing measurement, not a fixed commitment made in the absence of real usage data.

**Example:**

```http
# Every response from a deprecated endpoint carries machine-readable signals —
# useful even for automated clients that nobody manually reads documentation for
GET /v1/orders/123
Deprecation: true
Sunset: Sat, 30 Jun 2026 00:00:00 GMT
Link: <https://api.example.com/docs/migration/v1-to-v2-orders>; rel="deprecation"

200 OK
{ "id": "123", ... }   # still fully functional — deprecation headers are a
                          # WARNING, not a functional degradation, until sunset
```

```java
// Instrumenting ACTUAL usage before assuming anything about who's still calling it
@GetMapping("/v1/orders/{id}")
Order getOrderV1(@PathVariable String id, @RequestHeader("X-Api-Key") String apiKey,
        HttpServletResponse response) { // injected as a PARAMETER, not a field —
    deprecationMetrics.recordUsage("v1-orders-get", apiKey); // WHO, not just how many —
    response.setHeader("Deprecation", "true");                 // lets you actually
    response.setHeader("Sunset", "Sat, 30 Jun 2026 00:00:00 GMT"); // reach out to
    return legacyOrderService.getOrder(id);                        // identified stragglers
}
```

**Follow-up questions:**

- *"Should a sunset date be treated as fixed once announced?"* — No — as a target informed by ongoing measurement, delayed if telemetry shows meaningful residual usage.
- *"What's the risk of removing on schedule regardless of usage data?"* — A real, avoidable outage for a caller who didn't get the message — a forgotten legacy batch job, an untracked partner integration.

**Sources:** [RFC 8594 — The Sunset HTTP Header Field](https://datatracker.ietf.org/doc/html/rfc8594), [IETF Draft — The Deprecation HTTP Header Field](https://datatracker.ietf.org/doc/draft-ietf-httpapi-deprecation-header/)

---

## 26. How Do You Balance Fine-Grained APIs Against Chatty Network Behavior?

**Core answer:**

"A very fine-grained, purist resource model (a separate endpoint for every individual piece of data, requiring a client to make many sequential or parallel requests to assemble one screen's worth of information) is architecturally clean but can produce genuinely chatty client behavior — for a mobile client on a high-latency connection especially, ten small sequential requests to render one page can be dramatically slower than one larger request, purely due to accumulated round-trip latency.

I'd address this with a layered approach rather than picking one extreme: keep the underlying resource model reasonably fine-grained and well-factored, but offer **composite/aggregate endpoints** for common client access patterns that would otherwise require many round trips (`GET /orders/{id}/summary` returning the order plus its items plus shipping status in one call) — a deliberate, purpose-built denormalization for a specific client need, not a wholesale abandonment of resource-oriented design. For genuinely variable, client-driven data-shaping needs, I'd consider a **BFF (Backend-for-Frontend)** layer per major client type, or GraphQL specifically for that aggregation problem."

**Staff-level extension:**

This tension is exactly what GraphQL was purpose-built to address at the protocol level — letting a client specify exactly the shape of data it needs in a single request, rather than the API provider guessing which composite shapes are worth pre-building. But GraphQL trades away a lot of what makes REST operationally simple (HTTP-level caching by URL, straightforward rate limiting per endpoint, simpler per-endpoint authorization modeling) — the actual choice is workload-dependent, and for many APIs, a well-chosen handful of composite REST endpoints covering the genuinely common access patterns gets most of GraphQL's practical benefit without taking on its added operational complexity (query cost analysis to prevent expensive arbitrary queries, N+1 problems at the resolver level, but now client-triggerable).

**Example:**

```http
# Fine-grained (clean resource model, but chatty for a common access pattern)
GET /orders/123          # 1st round trip
GET /orders/123/items     # 2nd round trip
GET /orders/123/shipment  # 3rd round trip — 3 sequential/parallel round trips
                            # just to render ONE order-detail screen

# Composite endpoint — deliberate denormalization for a KNOWN, common access
# pattern, offered ALONGSIDE the fine-grained resources, not instead of them
GET /orders/123/summary
{
  "order": { "id": "123", "status": "shipped" },
  "items": [ { "sku": "WIDGET-1", "quantity": 2 } ],
  "shipment": { "carrier": "UPS", "trackingNumber": "1Z999..." }
}
```

**Follow-up questions:**

- *"Is GraphQL a strictly better replacement for REST?"* — No — it solves over-fetching elegantly but trades away HTTP-level caching by URL and simple per-endpoint rate limiting/authorization.
- *"What's the N+1 risk GraphQL introduces?"* — The same resolver-level N+1 problem as an ORM, but now client-triggerable via an arbitrary query shape — needs query cost analysis to bound it.

**Sources:** [Sam Newman — Backend for Frontend pattern](https://samnewman.io/patterns/architectural/bff/), [GraphQL specification](https://spec.graphql.org/)

---

## 27. Design an API for Creating an Order, Reserving Inventory, and Taking Payment

**Core answer:**

"I'd model this as a single `POST /orders` that kicks off a multi-step workflow, rather than exposing 'reserve inventory' and 'take payment' as separate client-orchestrated calls — the client shouldn't be responsible for calling three separate endpoints in the right order and handling partial failure between them; that orchestration responsibility belongs on the server side, tying directly into the transactional-outbox/saga patterns from the Transactions category.

Concretely: `POST /orders` accepts the order request and, synchronously, does only what's genuinely fast and safe to do synchronously — validate the request and create the order resource in a `pending` state, returning `201 Created` immediately. The actual multi-step workflow (reserve inventory, charge payment) proceeds *asynchronously* as a saga — the client polls `GET /orders/{id}` (or receives a webhook) to observe the order progressing through `inventory_reserved` → `payment_processing` → `confirmed`, or landing in an explicit failure state with a clear reason. This directly reuses the long-running-operation/workflow patterns from questions 17/18, rather than a single synchronous transaction spanning three different systems, which would be fragile."

**Staff-level extension:**

I wouldn't model this as three separate client-callable endpoints (`POST /reservations`, `POST /charges`, `POST /orders`) that the client itself calls in sequence: that pushes the hardest part of the problem — what happens if step 2 fails after step 1 already succeeded, who's responsible for compensating/rolling back the inventory reservation if the payment fails — onto every client integrating with the API, and different client teams would inevitably get this partial-failure handling subtly wrong in different ways. Centralizing the orchestration server-side, as a saga the order resource's own state machine represents, means the hard distributed-systems problem is solved exactly once, correctly, in the place that owns it — and I'd explicitly connect this design to the transactional outbox pattern (ensuring the order's initial `pending` state and the "start the saga" trigger are committed atomically) and to idempotency (question 5) for the payment-charging step specifically, since that's the step where a duplicate/retried execution has real financial consequences.

**Example:**

```http
POST /orders
{ "items": [{"sku": "WIDGET-1", "quantity": 2}], "paymentMethodId": "pm_123" }

201 Created
Location: /orders/456
{ "id": "456", "status": "pending", "items": [...] }

# Client polls (or receives a webhook) to observe progress through the saga
GET /orders/456
{ "id": "456", "status": "inventory_reserved" }
GET /orders/456
{ "id": "456", "status": "payment_processing" }
GET /orders/456
{ "id": "456", "status": "confirmed", "confirmationNumber": "ORD-2026-0456" }

# Or, an explicit, actionable failure state instead of a generic error
GET /orders/456
{
  "id": "456", "status": "payment_failed",
  "failureReason": { "code": "CARD_DECLINED", "message": "the payment method was declined" }
}
```

**Follow-up questions:**

- *"Why not let the client call reserve-inventory and charge-payment as separate endpoints?"* — That pushes partial-failure handling (compensating a reservation if payment fails) onto every client, and different teams would get it subtly wrong differently.
- *"Where does idempotency matter most in this flow?"* — The payment-charging step specifically — a duplicate/retried execution there has real financial consequences.

**Sources:** [Chris Richardson — Saga Pattern](https://microservices.io/patterns/data/saga.html), [Google AIP — Long-running operations](https://google.aip.dev/151)

---

## 28. How Would You Review an API Specification Across Multiple Teams?

**Core answer:**

"I'd treat API review as a genuine cross-functional gate, not a rubber-stamp, structured around a few concrete dimensions rather than an unstructured 'does this look okay' pass. **Consistency**: does it follow the org's naming, versioning, error-format, and pagination conventions (question 2) — deviation compounds across every future consumer. **Consumer impact**: who's calling this, what does their access pattern look like (question 26), and has the design been validated against a real use case. **Evolution**: is there an explicit versioning/compatibility story (questions 14-16) from day one. **Security**: correct auth, no sensitive leakage in responses or errors. **Operability**: observability hooks (tracing, question 24; health signals, question 23) from the start.

Mechanically, I'd push for review against a **written OpenAPI specification**, before implementation begins — a formal spec surfaces inconsistencies and gaps far more effectively than reviewing running code or a wiki page, and gives every reviewing team a concrete artifact to comment on."

**Staff-level extension:**

Reviewing against a formal, machine-readable specification enables genuinely valuable automation that manual review alone can't match — a linter (Spectral or similar) enforcing the org's style guide automatically on every spec change in CI, contract-testing tools (Pact) that can verify a *future* implementation actually matches the reviewed spec, and API-diff tools that flag breaking changes against a previous version automatically. The actual staff-level contribution to this process is designing the *review process itself* to scale — a single senior engineer manually reviewing every API design across a growing organization becomes a bottleneck and a single point of failure; building a lightweight, mostly-automated review pipeline (linting, breaking-change detection, a lightweight cross-team design-review checklist) that catches the majority of common issues automatically, reserving human review time for genuinely novel design trade-offs, is what actually lets API quality scale across many teams without the review process itself becoming the constraint.

**Example:**

```yaml
# The reviewable ARTIFACT — an OpenAPI spec, reviewed BEFORE implementation begins
openapi: 3.1.0
paths:
  /orders/{id}:
    get:
      summary: Retrieve an order
      responses:
        '200':
          description: Order found
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Order' }
        '404':
          description: Order not found          # every meaningful failure MUST be
        '403':                                    # documented explicitly, not left
          description: Not authorized for this order  # implicit or discovered later
```

```yaml
# A CI-enforced linting/style check — catching consistency issues automatically,
# rather than relying purely on manual cross-team review to notice every deviation
# .spectral.yaml (Spectral OpenAPI linter ruleset)
rules:
  path-casing: { given: "$.paths[*]~", then: { function: pattern, functionOptions: { match: "^(/[a-z0-9-]+)+$" } } }
  require-error-responses: { given: "$.paths[*][*].responses", then: { field: "4XX", function: truthy } }
```

**Follow-up questions:**

- *"Why review a spec instead of the implementation?"* — A formal, machine-readable spec surfaces gaps (missing error responses, ambiguous types) more effectively than reviewing running code, and enables automation manual review can't match.
- *"What's the staff-level contribution beyond doing reviews well?"* — Designing the review process itself to scale — a single senior engineer manually reviewing every API is a bottleneck; automate the mechanical checks, reserve human time for genuine trade-offs.

**Sources:** [Spectral — OpenAPI Linter](https://github.com/stoplightio/spectral), [Google API Improvement Proposals (AIPs)](https://google.aip.dev/)

---

## Sources & Further Reading — Consolidated

| Topic | Link |
|---|---|
| Roy Fielding's dissertation — REST architectural style | https://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm |
| RFC 9110 — HTTP Semantics | https://datatracker.ietf.org/doc/html/rfc9110 |
| RFC 5789 — PATCH Method | https://datatracker.ietf.org/doc/html/rfc5789 |
| Microsoft REST API Guidelines | https://github.com/microsoft/api-guidelines |
| Google API Design Guide | https://cloud.google.com/apis/design |
| Stripe API — Idempotent Requests | https://stripe.com/docs/api/idempotent_requests |
| IETF Draft — Idempotency-Key Header | https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/ |
| Use the Index, Luke — pagination done right | https://use-the-index-luke.com/no-offset |
| Slack API — Pagination | https://api.slack.com/apis/pagination |
| JSON:API Specification | https://jsonapi.org/format/ |
| RFC 7396 — JSON Merge Patch | https://datatracker.ietf.org/doc/html/rfc7396 |
| RFC 6902 — JSON Patch | https://datatracker.ietf.org/doc/html/rfc6902 |
| RFC 6901 — JSON Pointer | https://datatracker.ietf.org/doc/html/rfc6901 |
| RFC 6585 — 428 Precondition Required | https://datatracker.ietf.org/doc/html/rfc6585 |
| RFC 4918 — WebDAV (422, 207 status codes) | https://datatracker.ietf.org/doc/html/rfc4918 |
| RFC 9457 — Problem Details for HTTP APIs | https://datatracker.ietf.org/doc/html/rfc9457 |
| Stripe API Versioning | https://stripe.com/docs/api/versioning |
| Stripe — Upgrades and backward compatibility | https://stripe.com/docs/upgrades |
| Pact — Contract Testing | https://docs.pact.io/ |
| Google API Improvement Proposals (AIPs) | https://google.aip.dev/ |
| AWS Architecture Blog — Exponential Backoff and Jitter | https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/ |
| Google SRE Workbook — Handling Overload | https://sre.google/sre-book/handling-overload/ |
| Resilience4j — Circuit Breaker | https://resilience4j.readme.io/docs/circuitbreaker |
| IETF Draft — RateLimit header fields | https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/ |
| Stripe — Rate Limits | https://stripe.com/docs/rate-limits |
| Spring Boot Reference — Kubernetes Probes | https://docs.spring.io/spring-boot/reference/actuator/endpoints.html#actuator.endpoints.kubernetes-probes |
| Google SRE Book — Monitoring Distributed Systems | https://sre.google/sre-book/monitoring-distributed-systems/ |
| W3C Trace Context specification | https://www.w3.org/TR/trace-context/ |
| OpenTelemetry documentation | https://opentelemetry.io/docs/ |
| RFC 8594 — The Sunset HTTP Header Field | https://datatracker.ietf.org/doc/html/rfc8594 |
| IETF Draft — Deprecation HTTP Header Field | https://datatracker.ietf.org/doc/draft-ietf-httpapi-deprecation-header/ |
| Sam Newman — Backend for Frontend pattern | https://samnewman.io/patterns/architectural/bff/ |
| GraphQL specification | https://spec.graphql.org/ |
| Chris Richardson — Saga Pattern | https://microservices.io/patterns/data/saga.html |
| Spectral — OpenAPI Linter | https://github.com/stoplightio/spectral |
