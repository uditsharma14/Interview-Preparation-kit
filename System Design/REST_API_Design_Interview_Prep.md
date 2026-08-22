# REST API Design — Interview Prep (Lead/Staff Level, with Code & Sources)

How to use this: each question has **the answer the way I'd actually say it out loud** in an interview, a **code/example snippet** you could sketch on a whiteboard or IDE to back it up, and **where the follow-up goes if you're in a Staff-level loop** — because at this level the bar is explaining trade-offs and failure modes across client evolution, retries, and multi-team consumption, not reciting HTTP verb definitions.

---

## 1. What Makes an API Resource-Oriented Rather Than RPC-Oriented?

**Answer:**

"An RPC-style API exposes *actions* as the primary unit — endpoints named like verbs or procedures (`/getUser`, `/createOrderAndCharge`, `/cancelSubscription`) that map roughly one-to-one onto function calls, and the HTTP method used to reach them is often just an implementation detail (many RPC-style APIs use POST for everything). A resource-oriented (REST) API instead exposes *nouns* — resources, identified by URIs (`/users/{id}`, `/orders/{id}`) — and expresses actions through a small, standard set of HTTP methods applied to those nouns (`GET /orders/{id}` to read, `POST /orders` to create, `DELETE /orders/{id}` to remove).

The practical benefit isn't stylistic purity — it's that a resource-oriented design gets a lot of behavior 'for free' from HTTP's own semantics and the broader ecosystem built around them: caching (`GET` is cacheable by intermediaries by default, an RPC `POST /getUser` typically isn't), idempotency guarantees tied to specific methods (question 4), standard status codes that convey meaning without needing custom documentation for every endpoint, and tooling (API gateways, proxies, browsers) that already understands HTTP semantics without needing to understand your specific action vocabulary. Not every operation maps cleanly onto CRUD-over-a-noun, though — question 17/18 covers how I handle genuinely action-oriented operations (like 'approve this refund') within an otherwise resource-oriented design, rather than pretending everything is naturally a resource."

**Code:**

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

**Follow-up:**

I'd be upfront that pure REST-by-the-book (HATEOAS, Roy Fielding's original dissertation-level constraints) is rarely what teams actually mean by "RESTful API" in practice — most production APIs are "pragmatic REST": resource-oriented URLs and standard HTTP semantics, without full hypermedia-driven discoverability. I'd frame the actual decision as: resource orientation is the right default because it leverages HTTP's existing semantics and tooling, but a handful of genuinely action-oriented operations (a workflow trigger, a bulk operation, a computation with no natural resource identity) are fine to model explicitly as their own thing (question 17) rather than forcing an awkward resource abstraction onto something that isn't naturally one — dogmatic REST-purism that produces worse APIs than a pragmatic hybrid is a real anti-pattern I'd push back on in a design review.

**Source:** [Roy Fielding's dissertation — REST architectural style](https://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm), [RFC 9110 — HTTP Semantics](https://datatracker.ietf.org/doc/html/rfc9110)

---

## 2. How Do You Choose Resource Names and URI Structures?

**Answer:**

"A few concrete conventions I'd apply consistently, since consistency across an API surface matters more than any single rule in isolation: plural nouns for collections (`/orders`, not `/order`), lowercase with hyphens rather than underscores or camelCase in the URL path (`/order-items`, not `/orderItems` or `/order_items` — hyphens are the more broadly recommended convention for URL readability and SEO-adjacent tooling, though this is a stylistic choice teams should just pick once and enforce), and nesting to express genuine ownership/containment relationships, but only one level deep in practice — `/users/{userId}/orders` is fine and expresses a real containment relationship, but `/users/{userId}/orders/{orderId}/items/{itemId}/reviews/{reviewId}` becomes unwieldy and usually signals the deeper resources deserve their own top-level, independently addressable collection (`/order-items/{itemId}`) rather than being buried behind a long parent chain.

I'd also keep URIs representing *identity*, not query/filter logic — filtering, sorting, and pagination parameters belong in the query string (question 8), not encoded into the path itself (`/orders/status/shipped` is a worse design than `/orders?status=shipped`, since the former implies `status` values are a fixed, enumerable part of the resource hierarchy rather than a filter dimension)."

**Code:**

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

**Follow-up:**

I'd bring up that the actual highest-leverage practice here isn't any individual naming rule — it's having a **written, enforced API style guide** shared across every team building services in the same organization, plus linting it automatically (via an OpenAPI-spec linter like Spectral, run in CI) rather than relying on manual review to catch inconsistency. The real cost of inconsistent naming isn't aesthetic — it's that client developers integrating with many internal APIs have to context-switch conventions per service, and inconsistency compounds the cognitive load of working across a growing microservices landscape; a shared, automatically-enforced style guide is the actual staff-level fix, not "everyone please try to follow the same conventions."

**Source:** [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines), [Google API Design Guide](https://cloud.google.com/apis/design)

---

## 3. Explain the Semantics of `GET`, `POST`, `PUT`, `PATCH`, and `DELETE`

**Answer:**

"`GET` retrieves a representation of a resource, must be safe (no side effects the client should be held responsible for — see question 4's distinction from idempotency) and cacheable by default. `POST` creates a new subordinate resource under a collection, or triggers a non-idempotent action that doesn't map cleanly onto the other verbs — it's the 'catch-all' verb precisely because it doesn't carry the safety or idempotency guarantees the others do. `PUT` replaces a resource *entirely* at a known URI — the request body represents the complete desired state of that resource, and any field omitted from the body is implicitly meant to be cleared/reset to default, not left untouched; this is what makes `PUT` naturally idempotent (sending the identical `PUT` twice produces the identical end state both times). `PATCH` applies a *partial* modification to a resource — only the fields present in the request body change, everything else is left as-is; because there are multiple competing formats for expressing a partial update (question 9), `PATCH` semantics are less universally standardized than the others, and its idempotency depends entirely on the patch format/content itself (a `PATCH` that says 'increment by 1' is not idempotent; one that says 'set this field to X' is). `DELETE` removes a resource, and should be idempotent — deleting an already-deleted resource should be a no-op returning success (or an appropriate 'already gone' status), not an error."

**Code:**

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

**Follow-up:**

I'd bring up the common real-world mistake of using `PUT` for what's actually a partial update — a team implements `PUT /orders/123` but only updates the fields present in the request body, silently leaving other fields untouched when they're omitted; this violates `PUT`'s actual replace-semantics contract, and any HTTP-aware intermediary, cache, or client library that assumes correct `PUT` semantics (full replacement, implying it's safe to treat two different partial bodies to the same `PUT` as producing different independent outcomes rather than sequential state merges) can behave unexpectedly. I'd say the fix is simple and important: if an endpoint only ever updates a subset of fields, it should be `PATCH`, not a `PUT` that lies about its own semantics — getting this right isn't pedantry, it's what lets HTTP-level tooling and client libraries reason correctly about the API's actual behavior without reading custom documentation for every single endpoint.

**Source:** [RFC 9110 §9 — HTTP Methods](https://datatracker.ietf.org/doc/html/rfc9110#section-9), [RFC 5789 — PATCH Method](https://datatracker.ietf.org/doc/html/rfc5789)

---

## 4. Which HTTP Methods Should Be Idempotent?

**Answer:**

"By the HTTP spec: `GET`, `HEAD`, `PUT`, `DELETE`, `OPTIONS`, and `TRACE` are all specified as idempotent — meaning making the identical request multiple times has the same effect on server state as making it once. `POST` and `PATCH` are explicitly **not** guaranteed idempotent by the spec — though a specific `PATCH` payload *can happen* to be idempotent depending on what it expresses (question 3), the method itself carries no such guarantee.

The distinction worth being precise about: idempotency is about the *effect on server state* being the same across repeated identical calls, which is a different (weaker) property than **safety** — `GET` is both safe (no intended side effect at all) and idempotent; `PUT`/`DELETE` are idempotent but not safe (they do have an intended effect, it's just that repeating the effect doesn't change the outcome further). This distinction matters enormously in practice for retry logic: a client (or an intermediary, or an HTTP library's automatic retry behavior) can safely retry any idempotent method after a network failure or ambiguous response (a timeout where you don't know if the server actually processed the request) without risking a duplicated effect — but retrying a plain `POST` after a timeout is genuinely dangerous, since the original request might have already succeeded server-side, and a naive retry could create a duplicate resource (a duplicate order, a duplicate charge), which is exactly the problem the next question addresses directly."

**Code:**

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

**Follow-up:**

I'd bring up that idempotency being a *spec-level guarantee* doesn't mean every real implementation actually honors it — a `PUT` handler with a buggy side effect (e.g., incrementing a counter as a side channel of an otherwise-replace-style update) technically violates the idempotency contract the method name promises, and this is a real, if less common, source of retry-related bugs: infrastructure (load balancers, HTTP clients, service meshes) that automatically retries idempotent methods on failure is trusting the *implementation* to actually be idempotent, not just the method choice. I'd frame the staff-level discipline as: idempotency needs to be genuinely engineered into the handler's actual behavior (which usually means it's driven by the data in the request, applied via an upsert/set-to-exact-value operation, not an increment/append), not just assumed because the HTTP method is conventionally idempotent — and for `POST`, where the spec offers no help at all, idempotency has to be deliberately added via a client-supplied idempotency key, which is exactly the next question.

**Source:** [RFC 9110 §9.2 — Idempotent Methods](https://datatracker.ietf.org/doc/html/rfc9110#section-9.2.2)

---

## 5. How Would You Make a Payment-Creation Endpoint Safely Retryable?

**Answer:**

"Since payment creation is inherently a `POST` (creating a new resource — a charge/transaction — with no natural idempotent semantics from the HTTP method itself), safety under retry has to be added explicitly via an **idempotency key**: the client generates a unique key (typically a UUID) once, per logical payment attempt, and sends it as a header (`Idempotency-Key`) on the request. The server, before processing, checks whether it has already seen this exact key: if not, it processes the payment normally and stores the key alongside the *result* (success or failure, including the actual response body) for some retention window; if the key has been seen before, the server returns the **stored result from the original request** without processing the payment again at all — even if the client retries because it never received the original response (a network timeout, a dropped connection), the server can recognize 'this is a retry of a request I already fully handled' and respond consistently without a second charge ever occurring.

The implementation detail that actually matters for correctness: the idempotency-key check and the payment-processing-plus-key-storage need to happen atomically (typically via a unique constraint on the key in the same database transaction as the payment record creation, or a distributed lock around the check-then-process sequence) — a naive 'check if key exists, if not process' implementation has exactly the same check-then-act race the concurrency file warns about, where two near-simultaneous retries with the same key could both pass the 'not seen yet' check and both create a payment."

**Code:**

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
        // fetch and return ITS result rather than double-processing
        return ResponseEntity.status(existing.get().getStatusCode())
            .body(idempotencyRepository.findByKey(idempotencyKey).get().getStoredResponse());
    }
}
```

```sql
-- The unique constraint that makes the check-and-reserve step genuinely atomic
ALTER TABLE idempotency_records ADD CONSTRAINT uq_idempotency_key UNIQUE (idempotency_key);
```

**Follow-up:**

I'd bring up the retention-window decision explicitly as a real design trade-off, not an afterthought: idempotency records need to be kept long enough to cover any realistic client retry window (commonly 24 hours), but keeping them forever is unnecessary storage growth — a scheduled cleanup job (or a TTL, if the store supports one, e.g. Redis) should expire them after that window. I'd also flag a subtlety worth naming: the idempotency key must be scoped to *what actually needs to be identical* to count as a retry — if the client sends the same key but a genuinely *different* payment amount, the server should reject that as a client error (`422`, or a specific "idempotency key reused with different parameters" error) rather than either silently processing the new amount or silently returning the old result for different-looking input, since either behavior would be surprising and dangerous.

**Source:** [Stripe API — Idempotent Requests](https://stripe.com/docs/api/idempotent_requests), [IETF Draft — The Idempotency-Key HTTP Header Field](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/)

---

## 6. Compare Offset, Cursor, and Keyset Pagination

**Answer:**

"**Offset pagination** (`?page=3&size=20`, or `?offset=40&limit=20`) is the simplest to implement and understand — the database is asked to skip N rows and return the next M. Its problems compound at scale and under concurrent writes: the database still has to *scan* through all the skipped rows internally even though it doesn't return them, so performance degrades as the offset grows (a `LIMIT 20 OFFSET 100000` is genuinely expensive on most databases); and if rows are inserted or deleted between page requests, the client can see duplicate or skipped items across pages, since 'offset 20' refers to a different logical row after the underlying data has shifted.

**Cursor pagination** replaces the offset with an opaque token representing 'where I left off,' typically encoding the last-seen item's sort key(s) — the next request says 'give me the next N items after this cursor' rather than 'skip N items.' This avoids the scan-cost problem (the database can seek directly using an indexed condition like `WHERE id > :cursor_id`, rather than counting through skipped rows) and is far more resilient to concurrent inserts/deletes, since the cursor refers to a specific logical position (a specific row's key), not a shifting numeric offset.

**Keyset pagination** is essentially the concrete database-query technique that implements cursor pagination correctly — using an indexed column (or a composite of columns, for ties) as the seek condition directly in the `WHERE` clause and `ORDER BY`, rather than `OFFSET`. In practice 'cursor pagination' (the API-facing contract: an opaque token) and 'keyset pagination' (the underlying implementation: a seek-based query) are two sides of the same design, and I'd use them together — an opaque cursor for the API surface, backed by a keyset query underneath."

**Code:**

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

**Follow-up:**

I'd bring up why the cursor should be genuinely opaque to the client (base64-encoded, or even encrypted/signed) rather than a plain, readable value — this lets the server change its internal pagination implementation (add a tiebreaker column, change the sort key entirely) without breaking the API contract, since clients only ever pass the cursor back verbatim, never construct or interpret it themselves. I'd also mention that offset pagination isn't strictly wrong to use everywhere — for a small, admin-facing UI with modest data volume and infrequent concurrent writes, its simplicity (jump directly to page 5, show a total page count) is a genuine UX advantage cursor pagination structurally can't offer (a cursor-based API can't jump to an arbitrary page or show "page 5 of 20" without doing the expensive count/scan work anyway) — so the actual decision is trading "arbitrary page jump + total count" against "scale and consistency under concurrent writes," not simply "cursor is always better."

**Source:** [Use the Index, Luke — pagination done right](https://use-the-index-luke.com/no-offset), [Slack API — Pagination](https://api.slack.com/apis/pagination)

---

## 7. How Do You Guarantee Stable Pagination While Data Changes?

**Answer:**

"Stability requires two things working together. First, a **deterministic, total ordering** — the sort key(s) used for pagination must uniquely determine row order, with no ties; a sort purely on `created_at` where multiple rows can share the exact same timestamp is a real bug source, since ties can be returned in a different relative order across requests (most databases don't guarantee stable ordering for tied sort keys unless a tiebreaker is explicit), causing a row to be skipped or duplicated across pages. The fix is always including a unique column (typically the primary key) as an explicit final tiebreaker in the `ORDER BY`.

Second, keyset/cursor pagination (question 6) inherently handles *inserts and deletes that happen elsewhere in the data* much better than offset pagination does — since each page request seeks from a specific, fixed position (the last-seen key), a new row inserted somewhere else in the result set doesn't shift what 'this cursor' means, unlike an offset which is purely positional and shifts meaning as rows are added/removed anywhere before it. What keyset pagination does *not* automatically solve is a row that was already returned being subsequently modified in a way that changes its sort position — if a client is paginating by `updated_at` and a previously-returned row gets updated (moving it to the 'front' of the sort order) *while the client is still paginating*, that row could legitimately reappear on a later page; this is usually an acceptable, documented trade-off (real-time data that's actively being modified during pagination has this trade-off regardless of pagination strategy) rather than something fully solvable without snapshot isolation."

**Code:**

```sql
-- WITHOUT a tiebreaker — ties on created_at can be returned inconsistently
-- across separate requests, causing skipped or duplicated rows at page boundaries
SELECT * FROM orders ORDER BY created_at DESC LIMIT 20;

-- WITH an explicit, unique tiebreaker — deterministic total ordering,
-- guaranteed stable and consistent across repeated/paginated requests
SELECT * FROM orders ORDER BY created_at DESC, id DESC LIMIT 20;
```

**Follow-up:**

I'd bring up snapshot-based pagination (a database transaction/snapshot held open for the pagination session, or a point-in-time export the client paginates over) as the only way to get *fully* consistent pagination against actively-changing data — genuinely useful for something like a data export or an audit trail where "the exact state as of the moment I started paginating" matters, but it comes with real cost (an open long-running transaction/snapshot has its own resource and locking implications, tying back to the transactions category) and isn't appropriate for a typical high-traffic, ever-changing API. I'd frame the practical staff-level answer as: for most APIs, deterministic ordering (tiebreaker included) plus keyset-based cursor pagination is sufficient and the right trade-off, and I'd only reach for snapshot-based pagination for genuinely export/audit-style use cases where perfect point-in-time consistency across the whole paginated result set is an explicit requirement, documented and communicated as such.

**Source:** [Use the Index, Luke — pagination done right](https://use-the-index-luke.com/no-offset)

---

## 8. How Would You Design Filtering, Sorting, and Field Selection?

**Answer:**

"All three belong in the query string, not the path (question 2), since they're modifying *how* a collection is queried/rendered, not identifying a different resource.

**Filtering**: a consistent, predictable convention — `?status=shipped&createdAfter=2026-01-01` for simple equality/range filters on well-known fields. For more complex filtering needs (multiple values, operators beyond equality), I'd pick one consistent syntax rather than inventing per-endpoint conventions — either a structured query-parameter convention (`?status=shipped,cancelled` for 'in' semantics, `?amount[gte]=100` for range operators) or, for genuinely complex query needs, a dedicated filter query language/DSL, but consistently applied across the whole API rather than each endpoint growing its own bespoke filter syntax organically.

**Sorting**: a single, consistent parameter (`?sort=createdAt,-amount` — a comma-separated list, with a leading `-` for descending) rather than separate `sortBy`/`sortDirection` parameters that only support one sort field, which becomes limiting the moment a client needs a genuine multi-field sort (matching the tiebreaker requirement from the pagination questions, incidentally).

**Field selection** (sparse fieldsets): `?fields=id,status,total` to let a client request only the fields it actually needs, reducing payload size for high-volume/mobile clients — genuinely valuable for large resources with many optional/expensive-to-compute fields, but I'd be selective about offering it, since it adds real server-side complexity (every field needs to be independently, correctly omittable) for a benefit that's often better solved by simply designing a leaner default response or offering a separate, smaller resource representation (a 'summary' vs 'detail' representation) instead."

**Code:**

```http
GET /orders?status=shipped,cancelled&createdAfter=2026-01-01T00:00:00Z
GET /orders?amount[gte]=100&amount[lte]=500
GET /orders?sort=createdAt,-amount        # ascending createdAt, THEN descending amount
GET /orders?fields=id,status,total          # sparse fieldset — only these fields returned
```

**Follow-up:**

I'd bring up that unconstrained, free-form filtering (allowing arbitrary fields and operators without validation) is a real performance and security risk, not just a design nicety — a filter parameter that maps directly onto an unindexed database column, or that allows arbitrarily complex boolean combinations, can let a client trigger accidentally (or deliberately) expensive queries that degrade the whole service; I'd explicitly validate allowed filter fields/operators against a known allowlist rather than passing client input straight through to a query builder unchecked. I'd also mention that a query language/DSL (like OData's `$filter`, or GraphQL entirely, for APIs where flexible querying is a first-class requirement rather than an occasional need) is worth considering explicitly when filtering needs grow complex enough that a bespoke query-parameter convention starts accumulating special cases — that's usually the signal the ad-hoc approach has outgrown itself.

**Source:** [JSON:API Specification — Filtering, Sorting, Sparse Fieldsets](https://jsonapi.org/format/#fetching), [Google API Design Guide — Standard Fields](https://cloud.google.com/apis/design/design_patterns)

---

## 9. Compare JSON Merge Patch and JSON Patch

**Answer:**

"Both are standardized formats for expressing a partial update via `PATCH` (question 3), and they represent genuinely different trade-offs, not just stylistic variants.

**JSON Merge Patch** (RFC 7396) is the simpler of the two: the patch body is itself a JSON object shaped like the target resource, and applying it means 'merge these fields into the existing resource' — a field present in the patch overwrites the corresponding field on the resource, and a field explicitly set to `null` in the patch means 'delete this field.' It's intuitive and easy for clients to construct (just send the fields you want to change), but it has a real, sometimes-surprising limitation: because `null` means 'delete,' there's no way to express 'set this field's actual value to `null`' as distinct from 'remove this field' — and it also can't express operations on array elements individually (any array field in the patch replaces the *entire* array, not specific elements within it).

**JSON Patch** (RFC 6902) is more expressive and more complex: the patch body is an *array of explicit operations* (`add`, `remove`, `replace`, `move`, `copy`, `test`), each targeting a specific location in the document via a JSON Pointer path — this can express precise operations on individual array elements, distinguish 'set to null' from 'remove entirely,' and even include a `test` operation that aborts the whole patch if a precondition isn't met (a lightweight, patch-embedded optimistic-concurrency check). The cost is that it's harder for clients to hand-construct (usually needs a library to compute the diff/patch operations) and more complex for the server to apply and validate correctly."

**Code:**

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

**Follow-up:**

I'd give the practical recommendation: JSON Merge Patch is the right default for the overwhelming majority of real APIs, since most partial-update needs really are just 'change these top-level fields' and the null-means-delete ambiguity rarely matters in practice (most domains don't have a meaningful distinction between 'field is null' and 'field is absent'); I'd reach for full JSON Patch specifically when array-element-level operations or the `test`-based precondition mechanism are genuinely needed, or when working with a client ecosystem (some enterprise/B2B integration standards) that already expects it. I'd also mention that neither format is a substitute for proper optimistic-concurrency control (question 10) — JSON Patch's `test` operation *can* be used for a lightweight version check, but I'd generally prefer the explicit `ETag`/`If-Match` mechanism as the primary optimistic-concurrency tool, since it's visible at the HTTP layer (cacheable, inspectable by intermediaries) rather than buried inside a patch body.

**Source:** [RFC 7396 — JSON Merge Patch](https://datatracker.ietf.org/doc/html/rfc7396), [RFC 6902 — JSON Patch](https://datatracker.ietf.org/doc/html/rfc6902)

---

## 10. How Do You Prevent Lost Updates Using ETags or Version Fields?

**Answer:**

"A lost update happens when two clients read the same resource, both make changes based on that (now-stale) read, and the second client's write silently overwrites the first client's changes without either client ever being told a conflict occurred — classic last-write-wins data loss.

The standard HTTP-native mechanism is `ETag` combined with conditional requests: the server includes an `ETag` header (an opaque version identifier — a hash of the content, or a version number) on every `GET` response. When the client later wants to update the resource, it includes that same value in an `If-Match` header on the `PUT`/`PATCH` request. The server compares the `If-Match` value against the resource's **current** `ETag` at the moment the write is about to be applied — if they don't match, someone else modified the resource in between, and the server rejects the write with `412 Precondition Failed` rather than silently applying it over the intervening change. This is optimistic concurrency control (question 15 in the transactions category covers the broader pattern) expressed at the HTTP layer, giving the client an explicit, actionable signal ('someone else changed this — reload and reconcile') instead of silently losing data.

An application-level `version` field in the resource body (incrementing on every update, checked and required on every write) achieves the identical semantic, just expressed in the request/response body rather than HTTP headers — functionally equivalent, and the choice between the two is mostly about whether the team wants the concurrency-control mechanism to be visible/enforced at the HTTP layer (where caches, proxies, and generic HTTP tooling can participate) or purely within the application's own data model."

**Code:**

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

**Follow-up:**

I'd bring up that this is precisely the same optimistic-locking mechanism JPA/Hibernate implements internally via `@Version` (covered in depth in the JPA/Hibernate category) — the HTTP-level `ETag`/`If-Match` pattern and the database-level `@Version` column are the same conceptual pattern applied at two different layers, and in a well-designed system they're often directly wired together (the entity's `@Version` value *becomes* the `ETag`, so a database-level optimistic-lock failure surfaces cleanly as a `412` at the API layer, rather than the API needing a separate, redundant versioning mechanism). I'd also mention that this pattern requires client cooperation to actually work — a client that ignores the `ETag`/`If-Match` contract and just sends unconditional `PUT`s defeats the whole mechanism, so for genuinely critical resources, I'd consider making `If-Match` a required header (rejecting writes that omit it with `428 Precondition Required`) rather than optional, to prevent well-meaning clients from silently bypassing the protection.

**Source:** [RFC 9110 §8.8 — ETag and Conditional Requests](https://datatracker.ietf.org/doc/html/rfc9110#section-8.8), [RFC 6585 — 428 Precondition Required](https://datatracker.ietf.org/doc/html/rfc6585)

---

## 11. When Should an API Return `200`, `201`, `202`, `204`, `400`, `409`, `422`, or `429`?

**Answer:**

"`200 OK` — a successful request with a response body, the general-purpose success code for `GET`/`PUT`/`PATCH` and any `POST` that isn't specifically a creation. `201 Created` — specifically for a successful `POST` (or occasionally `PUT`) that created a new resource; should include a `Location` header pointing at the new resource's URI, and typically the created representation in the body. `202 Accepted` — the request was validly received and will be processed, but processing is asynchronous and not complete by the time the response is sent (question 17/18) — the response body typically includes a way to check status later, not the final result. `204 No Content` — success, but there's genuinely nothing to return in the body (a common choice for `DELETE`, or a `PUT`/`PATCH` where the client doesn't need the updated representation echoed back).

`400 Bad Request` — the request itself is malformed at a structural level (invalid JSON, a required field entirely missing, a type mismatch) — the request couldn't even be meaningfully validated against business rules because it's not well-formed to begin with. `409 Conflict` — the request is well-formed and understood, but conflicts with the resource's current state (attempting to create a resource that already exists with a unique constraint, or a state-transition request that's invalid given the resource's current status — e.g., trying to cancel an order that's already shipped). `422 Unprocessable Entity` — the request is well-formed (valid JSON, right types) but fails semantic/business-rule validation (a required business constraint is violated — e.g., a discount code that doesn't exist, an end date before a start date) — this is the specific code that separates 'your request wasn't syntactically valid' (400) from 'your request was syntactically fine but doesn't satisfy the rules' (422), a genuinely useful distinction for clients trying to react programmatically to different failure categories. `429 Too Many Requests` — rate limit exceeded, and should include a `Retry-After` header telling the client how long to back off."

**Code:**

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

**Follow-up:**

I'd bring up that `400` vs `422` is genuinely one of the most commonly *inconsistently applied* distinctions across real-world APIs — plenty of production APIs use `400` for everything (structural and semantic validation alike), which isn't strictly wrong (400 is a broad enough category to cover it) but does throw away a useful signal for clients trying to distinguish 'fix your request format' from 'your request format is fine, but this specific business rule failed' programmatically. I'd advocate for picking a clear, documented convention for the whole API up front (I'd generally use 422 for anything a client would reasonably want to handle differently — a specific validation error to surface to an end user — versus 400 for genuinely malformed requests that indicate a client bug) and enforcing it consistently via a shared exception-handling layer (a `@ControllerAdvice` in Spring, mapping specific exception types to specific status codes centrally) rather than leaving each endpoint to decide ad hoc.

**Source:** [RFC 9110 §15 — Status Codes](https://datatracker.ietf.org/doc/html/rfc9110#section-15), [RFC 4918 §11.2 — 422 Unprocessable Entity](https://datatracker.ietf.org/doc/html/rfc4918#section-11.2)

---

## 12. What Should a Consistent Error Response Contain?

**Answer:**

"I'd standardize on a single, consistent error response shape across the entire API — ideally following an established standard rather than inventing a bespoke one, since a standard format lets generic client-side error-handling tooling work across many APIs without custom parsing per service. **RFC 9457 (Problem Details for HTTP APIs)** is the current, well-adopted standard for exactly this: a `type` (a URI identifying the specific error category, ideally dereferenceable to human documentation), a `title` (a short, human-readable summary of the error type, generally the same across all instances of this error type), a `status` (the HTTP status code, redundantly included in the body for clients that inspect the body directly), a `detail` (a human-readable explanation specific to *this* occurrence), and an `instance` (a URI identifying this specific occurrence, useful for correlating with server-side logs).

Beyond the RFC 9457 baseline fields, I'd include: a `traceId`/`requestId` correlating the response to server-side logs/traces (critical for support and debugging — without this, 'a customer says they got an error' is very hard to root-cause); and, for validation errors specifically, a structured list of field-level errors (question 13) rather than cramming everything into one prose `detail` string that's hard for a client UI to map back onto specific form fields."

**Code:**

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

**Follow-up:**

I'd bring up that adopting a real standard (RFC 9457) rather than a bespoke `{error: "..."}` shape has a genuinely underappreciated benefit: client libraries, API gateways, and observability tooling increasingly understand `application/problem+json` natively, and a `type` URI that dereferences to real documentation gives both humans and automated tooling a stable, linkable identity for a specific error category across every version of the API, rather than an error message string that might get reworded and silently break any client that was pattern-matching on it. I'd also flag that error responses are a common, easy-to-miss security leak point — stack traces, internal exception messages, or SQL error text accidentally surfacing in a `detail` field in a production environment is a real information-disclosure risk (tying to the security-logging discussion in the Spring Security file), so error-handling middleware needs an explicit, deliberate mapping from internal exceptions to safe, external-facing `detail` messages, never a blanket "just serialize the exception."

**Source:** [RFC 9457 — Problem Details for HTTP APIs](https://datatracker.ietf.org/doc/html/rfc9457)

---

## 13. How Should Validation Errors Be Represented?

**Answer:**

"For a single overall request failure, I'd use the RFC 9457 shape from the previous question, but extend it with a structured, **per-field** list of validation errors — not one flattened `detail` string trying to describe multiple field problems in prose. Each entry should identify the specific field/path that failed (ideally via a JSON Pointer, matching the same addressing convention as JSON Patch, question 9, for consistency), a machine-readable error code (so a client can react programmatically — highlight the right form field, choose a localized message — without string-matching human-readable text), and a human-readable message as a fallback/display default.

This structure matters practically for the actual client-side experience: a client-side form needs to map 'the `email` field is invalid' to *that specific input box*, and a client-side i18n layer needs a stable error *code* to look up a localized message from, rather than needing to parse or pattern-match against an English-language sentence that might change wording between API versions."

**Code:**

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

**Follow-up:**

I'd bring up that machine-readable error **codes** (not just field names) are the detail most APIs get wrong or skip entirely, and it's the thing that actually enables good client-side UX at scale — without a stable code, a frontend either has to fragile-string-match the message (breaks the moment the message wording changes, even for a harmless copy-editing fix) or just show the raw server message untranslated, which is a poor experience for any genuinely multi-locale product. I'd advocate for defining and versioning the error-code vocabulary itself as a first-class part of the API contract (documented, with each code's meaning and which fields/endpoints can produce it), the same way status codes and response schemas are part of the contract — treating error codes as an afterthought is a common gap that shows up painfully once a client team tries to build good, localized error UX against the API.

**Source:** [RFC 9457 — Problem Details for HTTP APIs](https://datatracker.ietf.org/doc/html/rfc9457), [RFC 6901 — JSON Pointer](https://datatracker.ietf.org/doc/html/rfc6901)

---

## 14. Compare URI, Header, and Media-Type API Versioning

**Answer:**

"**URI versioning** (`/v1/orders`, `/v2/orders`) embeds the version directly in the path. It's the most visible and simplest for clients and API-gateway routing/caching to reason about (a cache or router can dispatch purely on path, no need to inspect headers), but it means a resource's identity/URI technically changes across versions, which is a real, if often-tolerated, violation of the REST principle that a URI identifies a resource independent of representation — and it means every version needs its own explicit set of route definitions.

**Header versioning** (a custom header like `Api-Version: 2`, or via `Accept-Version`) keeps the URI stable across versions — the same resource identity, with the version negotiated separately — which is more architecturally 'correct' in a REST-purist sense, but it's less visible/discoverable (a developer poking at the API in a browser or with a simple `curl` won't see the version unless they know to look for the header) and can be harder for some caching/gateway layers to route on cleanly, since caching keyed purely by URL now needs to also vary by header (`Vary: Api-Version`).

**Media-type versioning** (content negotiation via `Accept: application/vnd.example.v2+json`) folds the version into the standard HTTP content-negotiation mechanism itself — arguably the most 'correct' from a pure HTTP-semantics standpoint (the client is asking for a specific *representation* of the resource, which is exactly what `Accept` is for), but it's the least commonly understood/used pattern among typical API consumers, and tooling support (API gateways, testing tools, casual exploration) is generally weaker for it than for the other two."

**Code:**

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

**Follow-up:**

I'd give the pragmatic recommendation: for most public/external-facing APIs, URI versioning wins in practice specifically because of its simplicity and visibility — it's what the overwhelming majority of widely-used public APIs actually do (Stripe, GitHub, and most major API providers use some form of version-in-the-path or version-in-a-simple-header, rarely pure media-type negotiation), and fighting that ecosystem convention has a real cost in developer-experience friction for API consumers who expect the common pattern. I'd reserve header/media-type versioning for internal APIs where the consuming teams are known, tooling is controlled, and the stronger architectural correctness (stable resource identity across versions) is worth the reduced visibility — and regardless of *mechanism* chosen, I'd emphasize that the harder, more important problem is the actual **versioning policy** (question 15/16) — how long old versions are supported, how breaking changes get communicated — which matters far more to real-world API consumers than which specific versioning mechanism was chosen.

**Source:** [RFC 9110 §12 — Content Negotiation](https://datatracker.ietf.org/doc/html/rfc9110#section-12), [Stripe API Versioning](https://stripe.com/docs/api/versioning)

---

## 15. How Would You Evolve an API Without Breaking Existing Clients?

**Answer:**

"The core discipline is distinguishing changes that are genuinely backward-compatible (question 16) from those that aren't, and defaulting to the compatible kind whenever the actual requirement allows it. Safe, non-breaking changes: adding a new, optional field to a response (existing clients that don't know about it simply ignore it); adding a new, optional request parameter with a sensible default; adding an entirely new endpoint; adding a new possible value to an enum-like field **if and only if** clients are contractually expected to handle unknown values gracefully (this is a real caveat — see below); relaxing a validation constraint (accepting input that used to be rejected).

Breaking changes: removing or renaming any existing field; changing a field's type or semantic meaning; adding a new *required* field or parameter; tightening validation to reject previously-accepted input; changing a status code an endpoint returns for an existing scenario. For genuinely breaking changes that are unavoidable, I'd reach for versioning (question 14) as the mechanism, combined with a real deprecation policy (question 25) — running old and new versions in parallel for a defined support window, with clear communication and monitoring of which clients are still on the old version before it's actually retired.

The enum-value caveat is worth stating explicitly, since it's a common source of accidental breakage: adding a new enum value is only safe if the API's documented contract *already* told clients to treat unknown values as a graceful fallback (a `default` case in a switch, not a hard failure) — if that expectation was never established, adding a new value can break clients that (reasonably, from their perspective) assumed the enum was closed and exhaustive, and I'd treat this as effectively a breaking change unless the forward-compatibility contract was explicit from the start."

**Code:**

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

**Follow-up:**

I'd bring up contract testing (Pact, or an OpenAPI-spec-diff tool run in CI) as the actual mechanism for *enforcing* backward compatibility rather than relying on developer discipline and code review alone to catch every accidental breaking change — a CI check that diffs the current OpenAPI spec against the previous released version and fails the build on any breaking-change pattern (a field removed, a type changed, a new required field added) catches the mistake at the moment it's introduced, which is far cheaper than catching it after a client breaks in production. I'd also mention that "additive changes are safe" has a real cultural prerequisite: the API's documentation and client-generation tooling need to actively encourage clients to ignore unknown fields and tolerate new enum values by default (most JSON deserialization libraries do this by default, but strict/schema-validating clients might not) — an API surface can only rely on additive-change-safety if its consumers are actually built to be forward-compatible, which is worth stating as an explicit expectation in API documentation, not assumed silently.

**Source:** [Stripe — API Versioning and backward compatibility](https://stripe.com/docs/upgrades), [Pact — Contract Testing](https://docs.pact.io/)

---

## 16. How Do You Define Backward Compatibility?

**Answer:**

"I'd define it precisely, since 'backward compatible' is often used loosely: a change is backward-compatible if **every existing, correctly-written client, calling the API exactly as it did before the change, continues to function correctly without any modification** — same requests succeed the same way, same response shapes are still valid to whatever the client's existing parsing/handling logic expects.

The precision that matters: 'continues to function correctly' has to be evaluated against what clients are *contractually entitled to assume*, not just what happens to technically still parse. A client parsing a response with a JSON library that silently ignores unknown fields will 'still work' if a new field is added, but a client using strict schema validation that rejects unknown properties will break on the exact same change — whether that counts as 'backward compatible' depends on what the API's documented contract actually promised clients about handling unknown fields. This is why I'd always pair the technical definition with an explicit, published compatibility contract (e.g., 'clients must ignore unrecognized fields and enum values; the API guarantees not to remove or repurpose an existing field within a major version') — without a stated contract, 'is this change backward compatible' is genuinely ambiguous, since it depends on assumptions about client behavior the API team doesn't actually control."

**Code:**

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

**Follow-up:**

I'd bring up that this published-contract approach is exactly how major API providers (Stripe is a commonly cited example) manage to add fields and even new enum values within a stable major version without it counting as a breaking change — the contract with clients was established up front, clients are expected (and, in Stripe's case, their official client libraries are actually built) to honor it, and the API provider can then evolve additively with confidence. I'd frame the staff-level takeaway as: "backward compatible" isn't a property you can assess purely by inspecting the diff between two API versions in isolation — it's a property that depends on an explicit, agreed contract between API provider and consumers about what each side is allowed to assume, and defining that contract clearly up front is a prerequisite for being able to reason about compatibility at all, not an optional nicety.

**Source:** [Stripe — API Versioning](https://stripe.com/docs/upgrades), [Google API Improvement Proposals — Compatibility](https://google.aip.dev/180)

---

## 17. How Should Long-Running Operations Be Modeled?

**Answer:**

"An operation that can't complete within a normal synchronous request/response cycle (a report generation, a bulk data export, an operation that depends on a slow external process) shouldn't be forced into a blocking `POST` that holds the connection open until it finishes — that's fragile (client/proxy timeouts, a dropped connection losing the result entirely) and doesn't give the client any way to check progress or recover if their own process restarts mid-wait.

The standard pattern: the initiating request returns immediately with `202 Accepted` and a representation of the **operation itself** as a resource (not the eventual result) — including a URL the client can poll to check status (`GET /operations/{id}`), and a `Location` header pointing at it. The operation resource's status field progresses through well-defined states (`pending` → `in_progress` → `completed`/`failed`), and once complete, either includes the result directly or links to where the result can be fetched (`GET /reports/{id}` once the operation's status is `completed`). This turns a long-running process into an ordinary resource lifecycle the client can poll, be interrupted and resume checking on, and reason about using the same tools (caching, standard status codes) as any other resource."

**Code:**

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

**Follow-up:**

I'd bring up webhooks as the complementary alternative to polling, worth offering alongside (or instead of) polling for operations that can take a genuinely long time — rather than the client repeatedly polling `GET /operations/{id}`, the client registers a callback URL up front, and the server calls it once the operation completes; this is more efficient (no wasted polling requests) and gives near-immediate notification, at the cost of requiring the client to expose a reachable HTTP endpoint of its own, which not every client (especially browser-based/mobile clients) can do — this is exactly why many APIs offer both: polling as the universally-available baseline, webhooks as an optional efficiency improvement for clients that can support them. I'd also mention that the operation resource's status transitions should themselves be well-documented and exhaustive (including failure states with actionable error detail, per question 12) — a client polling an operation needs to know definitively when to stop polling and how to distinguish "still working" from "failed, here's why" from "succeeded, here's the result."

**Source:** [Google AIP — Long-running operations](https://google.aip.dev/151), [Microsoft REST API Guidelines — Long running operations](https://github.com/microsoft/api-guidelines/blob/vNext/azure/Guidelines.md#long-running-operations)

---

## 18. How Do You Design Asynchronous REST Workflows?

**Answer:**

"Building on the previous question's operation-resource pattern, a genuinely asynchronous *workflow* (as opposed to a single long-running operation) often involves multiple steps, some of which might themselves be async, and I'd model the overall thing as its own resource with an explicit state machine, rather than trying to force it into a single request/response exchange.

Concretely: the workflow resource (`/order-fulfillments/{id}`) exposes its current state (`reserved` → `paid` → `shipped` → `delivered`, or with explicit failure branches like `payment_failed`, `inventory_unavailable`) and, ideally, a history/timeline of state transitions for observability. State transitions are triggered either by client action (a `POST` to a transition-specific sub-resource, question 27's `PATCH`/action-endpoint pattern) or by events from other systems (a payment webhook arriving, an inventory system confirming reservation) — and I'd design the resource so a client can always `GET` the current state to reconcile, rather than *only* relying on push notifications/webhooks that could be missed. For any given workflow, I'd draw out the actual state diagram explicitly as part of the design — nailing down every valid transition and every terminal/failure state up front avoids the common failure mode of an ad hoc, undocumented, and inconsistent set of status values accumulating organically as edge cases get discovered in production."

**Code:**

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

**Follow-up:**

I'd bring up that the actual, recurring staff-level failure mode here isn't picking the wrong HTTP mechanics — it's under-designing the state machine itself: teams that don't draw out every valid transition and terminal state explicitly up front tend to accumulate ad hoc status values and undocumented edge-case transitions organically as production incidents reveal gaps, ending up with a workflow that's difficult to reason about, test exhaustively, or safely extend. I'd advocate for treating the state diagram as a genuine design artifact reviewed before implementation (the same rigor a database schema migration would get), and for building in an explicit "unknown/unexpected transition" guard in the implementation itself — an attempted transition that isn't valid from the current state should be rejected with a clear `409 Conflict` and a specific error code, not silently allowed or silently ignored, since a workflow that can silently enter an invalid state is a genuinely hard thing to debug after the fact.

**Source:** [Google AIP — Long-running operations](https://google.aip.dev/151), [AWS Step Functions — State machine design](https://docs.aws.amazon.com/step-functions/latest/dg/concepts-states.html)

---

## 19. How Would You Expose Bulk Operations With Partial Success?

**Answer:**

"A bulk endpoint (`POST /orders/batch` accepting an array of order-creation requests) genuinely can't be all-or-nothing in most realistic designs — if item 47 out of 100 fails validation, forcing the entire batch to fail (and requiring the client to resubmit all 100, including the 46 that would have succeeded) is usually worse UX and worse efficiency than processing each item independently and reporting per-item results.

The pattern I'd use: the response is itself an array (or a structured object) with one entry per submitted item, in the same order (or explicitly correlated via a client-supplied ID per item), each carrying its own success/failure status and, for failures, the same structured validation-error detail from question 13 — scoped to that specific item. The overall HTTP status code for a partial-success batch is itself a judgment call worth being explicit about: I'd generally use `207 Multi-Status` (borrowed from WebDAV, but increasingly used more broadly for exactly this shape) to signal 'the request itself was processed, but individual items had mixed outcomes' — distinct from a clean `200`/`201` (implying uniform success) or a `4xx` (implying the whole request failed)."

**Code:**

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

**Follow-up:**

I'd bring up that partial-success batch semantics need to be paired with a clear **idempotency** story for the batch as a whole, not just individual items (tying back to question 5) — if a client retries an entire failed/partially-failed batch, it needs a way to avoid re-processing the items that *already* succeeded the first time, which usually means either per-item idempotency keys within the batch, or the client being expected to resubmit only the failed subset (identified via their `clientRef`) rather than the whole original batch. I'd also mention that very large batches deserve an explicit size limit and, beyond a certain size, should be redirected to the async-operation pattern (question 17) entirely — a bulk endpoint processing 10,000 items synchronously within one HTTP request/response cycle is fragile regardless of how well the partial-success reporting is designed, and a batch-as-async-operation (accepting the batch, returning `202` with a pollable operation resource, per question 17) is the more robust design once volume grows past what a single synchronous call can reasonably handle.

**Source:** [RFC 4918 §11.1 — 207 Multi-Status](https://datatracker.ietf.org/doc/html/rfc4918#section-11.1), [Google AIP — Batch methods](https://google.aip.dev/231)

---

## 20. How Do Retries Interact With Timeouts and Duplicate Requests?

**Answer:**

"The core danger is that a **timeout is fundamentally ambiguous** from the client's perspective — the client doesn't know whether the server never received the request, received it but hasn't finished processing, or actually completed processing successfully and only the *response* was lost in transit. A naive client retry policy that just resends the identical request on any timeout risks duplicating the effect of a request that actually did succeed server-side, which is exactly why idempotency (question 5) has to be designed in *before* any retry logic is layered on top, not as an afterthought.

Given that, the safe retry discipline is: only automatically retry requests that are either inherently idempotent (question 4's `GET`/`PUT`/`DELETE`) or explicitly made idempotent via an idempotency key (question 5's pattern, for `POST`); use **exponential backoff with jitter** between retry attempts rather than immediate or fixed-interval retries, both to give a struggling downstream service room to recover rather than piling on more load at a fixed cadence, and to avoid many clients retrying in lockstep (the 'thundering herd' pattern, where synchronized retries from many clients all hit the recovering service at the same instant and re-trigger the same overload); and set a **retry budget/ceiling** (a maximum number of attempts, and/or a maximum total time spent retrying) rather than retrying indefinitely, since an indefinitely-retrying client during a real outage just adds sustained load to an already-struggling system, worsening the outage rather than helping it recover."

**Code:**

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

**Follow-up:**

I'd bring up the thundering-herd/retry-storm dynamic explicitly and connect it to a real production failure pattern (also covered in the cross-stack design category): a downstream dependency has a brief blip, many clients simultaneously time out and retry, and if those retries are synchronized (no jitter) or unbounded (no ceiling), the retry traffic itself can be *larger* than the original load that caused the blip, turning a brief, recoverable degradation into a much longer, self-sustaining outage — a system's own well-intentioned reliability mechanism (retries) becoming the actual cause of prolonged unavailability. I'd frame the staff-level discipline as: retry policy has to be designed with the *aggregate, system-wide* effect in mind, not just "will this individual client's request eventually succeed" — jitter, backoff, retry budgets, and ideally client-side circuit breakers (stop retrying entirely once failure rate crosses a threshold, rather than continuing to hammer a clearly-struggling dependency) all exist specifically to prevent a client-side reliability feature from becoming a server-side reliability liability.

**Source:** [AWS Architecture Blog — Exponential Backoff and Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/), [Google SRE Workbook — Retries](https://sre.google/sre-book/handling-overload/)

---

## 21. How Do You Protect an API From Retry Storms?

**Answer:**

"Building directly on the previous question, protection needs to happen on both the client side (well-behaved retry policies — backoff, jitter, budgets, circuit breakers) *and* the server side, since I wouldn't want to rely purely on every client implementing good retry hygiene correctly — some won't, whether due to a bug, a third-party client library with poor defaults, or a client team that just didn't think about it.

Server-side defenses: rate limiting (question 22) to cap how much load any single client/tenant can generate regardless of why; the `Retry-After` header on `429`/`503` responses, giving well-behaved clients an explicit, authoritative signal for how long to actually wait rather than guessing; load-shedding (deliberately rejecting some requests fast, with a clear `503`, rather than accepting every request and having *all* of them time out slowly, which is worse for both the server, which spends resources on requests it can't actually complete in time, and the client, which waits the full timeout duration before learning the request failed); and, at the API-gateway or service-mesh layer, a circuit breaker that can detect a downstream dependency is unhealthy and start failing fast (returning an immediate, cheap `503`) rather than letting every request queue up waiting on a dependency that's clearly not going to respond in time — protecting the caller's own resources (threads, connections) from being exhausted waiting on calls that are very unlikely to succeed anyway."

**Code:**

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

**Follow-up:**

I'd bring up load-shedding as the counterintuitive-but-correct move during a genuine overload event: deliberately rejecting a *fraction* of incoming requests immediately and cheaply (rather than accepting all of them and having the system degrade so badly that *every* request eventually times out) preserves the system's ability to serve at least *some* requests successfully, which is a strictly better outcome than accepting everything and serving nothing successfully — this is a real trade-off many teams are hesitant to build deliberately (it feels wrong to reject a request you could theoretically serve), but it's a well-established resilience pattern precisely because the alternative (accept everything, serve nothing) is worse for every caller. I'd also connect this to bulkheading — isolating resource pools (connection pools, thread pools) per downstream dependency, so a retry storm or overload hitting *one* dependency doesn't exhaust resources shared with calls to *other*, unrelated dependencies — a single misbehaving downstream shouldn't be able to take down a service's ability to serve requests that don't even touch it.

**Source:** [Google SRE Workbook — Handling Overload](https://sre.google/sre-book/handling-overload/), [Resilience4j — Circuit Breaker](https://resilience4j.readme.io/docs/circuitbreaker)

---

## 22. How Would You Implement Rate Limiting for Tenants With Different Quotas?

**Answer:**

"I'd model rate limits as a per-tenant (or per-API-key, per-client) configuration rather than a single global limit, since different tenants legitimately have different contracted throughput needs (a free tier, a standard paid tier, an enterprise tier with a negotiated higher quota) — the rate-limiting mechanism itself (token bucket, sliding window, covered in depth in the Redis/Caching category) stays the same, but the *limit value and window* it enforces is looked up per-tenant at request time, typically from the tenant's identity (extracted from the authenticated token/API key) rather than anything client-suppliable.

Beyond the mechanism, I'd expose the current rate-limit state transparently to clients via standard headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, or the newer standardized `RateLimit` header) on *every* response, not just the one that finally exceeds the limit — this lets well-behaved clients self-throttle proactively (slow down before they actually hit `429`) rather than only discovering the limit reactively after being rejected. And I'd design tiered limits with **burst allowance** in mind (a token-bucket-style limiter naturally supports this — question 21 in the Redis/Caching category covers the algorithm choice in depth) since real traffic is rarely perfectly smooth, and a limiter that only tolerates a hard, unchanging steady-state rate tends to reject legitimate, bursty-but-reasonable traffic patterns unnecessarily."

**Code:**

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

**Follow-up:**

I'd bring up that rate limits should be enforced consistently at the edge (an API gateway) for coarse, tenant-level throughput protection, but sometimes *also* need finer-grained, endpoint-specific limits underneath (a tenant's overall quota might be generous, but one specific expensive endpoint — a bulk export, a heavy search query — might need its own tighter, independent limit regardless of the tenant's general headroom) — a single flat per-tenant number doesn't always capture the actual cost-to-serve variance across different endpoints. I'd also mention that rate-limit configuration itself needs to be dynamically adjustable without a deployment (a tenant upgrading their plan, or a temporary limit increase during a negotiated traffic spike, shouldn't require a code change and redeploy) — backing tenant quotas with a configuration store that can be updated live, rather than hardcoding tier limits into application code, is the actual staff-level operational requirement here, not just picking the right algorithm.

**Source:** [IETF Draft — RateLimit header fields](https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/), [Stripe — Rate Limits](https://stripe.com/docs/rate-limits)

---

## 23. What Is the Difference Between Readiness, Liveness, and Business Health?

**Answer:**

"Readiness and liveness are covered in depth in the Spring Boot Internals file (question 21 there) — readiness answers 'can this instance currently accept and correctly handle traffic,' liveness answers 'is this instance in a broken internal state that only a restart fixes' — and both are infrastructure-facing signals meant for an orchestrator (Kubernetes) to make routing/restart decisions, deliberately narrow and mechanical in what they check.

**Business health** is a distinct, broader concept: not 'is this specific process alive and accepting connections,' but 'is the *system as a whole* (potentially spanning many services, queues, and dependencies) actually functioning correctly from a business-outcome perspective' — are orders actually completing end-to-end, is the payment success rate within a normal range, is the checkout conversion funnel behaving as expected. This is fundamentally a different signal, monitored differently (business-metric dashboards and alerting, not a Kubernetes probe), aimed at a different audience (on-call engineers and business stakeholders investigating 'is the product actually working for customers right now,' not an orchestrator deciding whether to restart one pod), and it can be degraded even when every individual service reports itself perfectly ready and alive — a payment provider's API being technically 'up' but returning valid-looking failure responses for every transaction is a business-health incident that readiness/liveness probes would never catch, since every individual service is honestly reporting itself as healthy the whole time."

**Code:**

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

**Follow-up:**

I'd bring up the specific incident pattern this distinction is meant to catch: every service reporting green (ready, alive) while the *actual business outcome* customers care about is broken — a classic real-world example is a payment gateway integration where the gateway itself is technically reachable and responding (so any naive health check treats it as "up"), but is silently returning valid-shaped decline responses for every single transaction due to a misconfiguration on either side — no service-level health check catches this, since nothing crashed or became unreachable, but the business is fully down from a revenue perspective. I'd advocate for business-health dashboards and alerts (built on business metrics, not infrastructure metrics) as a genuinely necessary, separate layer of observability that a mature platform needs *in addition to* readiness/liveness — treating "all my services report healthy" as equivalent to "the product is working" is a real, common, and dangerous conflation.

**Source:** [Spring Boot Reference — Kubernetes Probes](https://docs.spring.io/spring-boot/reference/actuator/endpoints.html#actuator.endpoints.kubernetes-probes), [Google SRE Book — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)

---

## 24. How Should Distributed Tracing Context Propagate?

**Answer:**

"A single logical request in a microservices architecture typically fans out across many service calls, and distributed tracing exists to reconstruct that whole causal chain as one coherent trace, rather than a pile of disconnected per-service logs someone has to manually correlate after the fact by timestamp-guessing.

The mechanism: a **trace ID** (identifying the entire end-to-end request) and a **span ID** (identifying this specific hop/operation within it) are generated at the very first entry point (or extracted from an incoming request if this service isn't the true origin — an upstream caller that's already tracing should pass its context along), and every *outgoing* call this service makes — to a downstream HTTP service, to a database, publishing to Kafka — needs to propagate that same trace ID (with a new span ID representing the new hop, referencing the calling span as its parent) forward via standard, interoperable headers, the current standard being the **W3C Trace Context** spec (`traceparent`/`tracestate` headers), which most modern tracing libraries and vendors (OpenTelemetry being the dominant one now) implement natively rather than requiring custom propagation code.

The practical failure mode when this isn't done correctly: any hop that doesn't propagate the incoming trace context forward (a service that generates a *new*, unrelated trace ID for its downstream calls instead of continuing the one it received) breaks the trace into disconnected fragments at exactly that point — the trace suddenly 'ends' at that service from the perspective of anyone trying to follow the full request through the system, which is exactly the kind of gap that turns a 10-minute root-cause investigation into a multi-hour one during an actual incident."

**Code:**

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

**Follow-up:**

I'd bring up that async/messaging boundaries (Kafka, in particular, tying to the Kafka category) are the most common place trace propagation silently breaks, since it requires the trace context to be explicitly embedded in the message's headers at *publish* time and explicitly extracted and continued at *consume* time — this doesn't happen automatically the way a synchronous HTTP call's context propagation often does via auto-instrumentation, and a lot of teams discover this gap only when trying to debug an actual production incident and finding the trace mysteriously "ends" at the point a message was published, with no visible connection to whatever eventually consumed and processed it. I'd frame ensuring end-to-end trace continuity across every hop — including async/messaging boundaries specifically — as a genuine platform-engineering investment worth prioritizing deliberately, since its absence doesn't show up as a bug in normal operation, only as dramatically slower incident investigation exactly when speed matters most.

**Source:** [W3C Trace Context specification](https://www.w3.org/TR/trace-context/), [OpenTelemetry documentation](https://opentelemetry.io/docs/)

---

## 25. How Would You Safely Deprecate an Endpoint Used by Unknown Consumers?

**Answer:**

"'Unknown consumers' is the crux of the difficulty — for an internal API where every caller is a known, cooperating team, deprecation is mostly a communication and coordination problem. For a public API (or an internal API that's been around long enough that nobody's fully sure who's still calling an old endpoint), the discipline has to be more conservative and evidence-based, since you genuinely can't just ask everyone to confirm they've migrated.

My approach: first, **instrument the endpoint to measure actual usage** before assuming anything about who's still calling it — logging caller identity (API key/client ID, at minimum) and volume for the specific endpoint/version being considered for deprecation, over a long enough window to catch infrequent-but-real usage (a monthly batch job calling it, for instance, wouldn't show up in a one-week usage sample). Second, **communicate the deprecation explicitly and with real lead time** — via the `Deprecation` and `Sunset` HTTP headers (both now standardized, RFC 8594 for `Sunset`) on every response from the deprecated endpoint, so even automated/unattended clients get a machine-readable signal, plus direct outreach to any *identified* caller from the usage data, plus prominent documentation updates. Third, **only actually remove it once usage has genuinely dropped to zero (or an acceptable, explicitly accepted residual)** for a sustained period — not on a fixed calendar date chosen without regard to actual measured migration progress — and I'd keep monitoring the deprecated endpoint's usage numbers right up until removal, ready to delay if usage hasn't actually dropped as expected."

**Code:**

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
Order getOrderV1(@PathVariable String id, @RequestHeader("X-Api-Key") String apiKey) {
    deprecationMetrics.recordUsage("v1-orders-get", apiKey); // WHO, not just how many —
    response.setHeader("Deprecation", "true");                 // lets you actually
    response.setHeader("Sunset", "Sat, 30 Jun 2026 00:00:00 GMT"); // reach out to
    return legacyOrderService.getOrder(id);                        // identified stragglers
}
```

**Follow-up:**

I'd bring up that the actual hard part of deprecating a public-facing or long-lived internal endpoint isn't the mechanism (headers, documentation) — it's the organizational discipline of genuinely measuring usage before committing to a removal date, and being willing to *delay* the removal if the data shows meaningful residual usage, rather than treating a previously-announced sunset date as immovable regardless of what the actual telemetry says. I'd share the failure mode this guards against explicitly: teams that pick a sunset date up front, communicate it once, and then remove the endpoint on schedule regardless of measured usage risk a real, avoidable outage for whatever caller didn't get the message (a legacy internal batch job nobody remembered, a small partner integration that was never in the direct communication loop) — the safer, more mature practice treats the sunset date as a target informed by ongoing measurement, not a fixed commitment made in the absence of real usage data.

**Source:** [RFC 8594 — The Sunset HTTP Header Field](https://datatracker.ietf.org/doc/html/rfc8594), [IETF Draft — The Deprecation HTTP Header Field](https://datatracker.ietf.org/doc/draft-ietf-httpapi-deprecation-header/)

---

## 26. How Do You Balance Fine-Grained APIs Against Chatty Network Behavior?

**Answer:**

"A very fine-grained, purist resource model (a separate endpoint for every individual piece of data, requiring a client to make many sequential or parallel requests to assemble one screen's worth of information) is architecturally clean but can produce genuinely chatty client behavior — for a mobile client on a high-latency connection especially, ten small sequential requests to render one page can be dramatically slower than one larger request, purely due to accumulated round-trip latency, even if each individual request is fast on the server side.

I'd address this with a layered approach rather than picking one extreme: keep the underlying resource model reasonably fine-grained and well-factored (since that's good for cacheability, independent evolution, and clarity of ownership), but offer **composite/aggregate endpoints** for common client access patterns that would otherwise require many round trips (`GET /orders/{id}/summary` returning the order plus its items plus shipping status in one call, specifically because that's a known, common 'render this screen' access pattern) — this is a deliberate, purpose-built denormalization for a specific client need, not a wholesale abandonment of resource-oriented design. For genuinely variable, client-driven data-shaping needs (different clients needing meaningfully different combinations of nested data, unpredictable in advance), I'd consider a **BFF (Backend-for-Frontend)** layer per major client type, or GraphQL specifically for that aggregation problem, rather than trying to anticipate every possible client's needs with an ever-growing set of bespoke REST composite endpoints."

**Code:**

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

**Follow-up:**

I'd bring up that this tension is exactly what GraphQL was purpose-built to address at the protocol level — letting a client specify exactly the shape of data it needs in a single request, rather than the API provider guessing which composite shapes are worth pre-building — and I'd give an honest, balanced take rather than presenting it as a strictly-better replacement for REST: GraphQL solves the chattiness/over-fetching problem elegantly, but it trades away a lot of what makes REST operationally simple (HTTP-level caching by URL, straightforward rate limiting per endpoint, simpler authorization modeling per-endpoint rather than per-field) — the actual choice is workload-dependent, and for many APIs, a well-chosen handful of composite REST endpoints covering the genuinely common access patterns gets most of GraphQL's practical benefit without taking on its added operational complexity (query cost analysis to prevent expensive arbitrary queries, N+1 query problems at the resolver level mirroring the exact issue from the JPA/Hibernate category, but now client-triggerable).

**Source:** [Sam Newman — Backend for Frontend pattern](https://samnewman.io/patterns/architectural/bff/), [GraphQL specification](https://spec.graphql.org/)

---

## 27. Design an API for Creating an Order, Reserving Inventory, and Taking Payment

**Answer:**

"I'd model this as a single `POST /orders` that kicks off a multi-step workflow, rather than exposing 'reserve inventory' and 'take payment' as separate client-orchestrated calls — the client shouldn't be responsible for calling three separate endpoints in the right order and handling partial failure between them; that orchestration responsibility belongs on the server side, tying directly into the transactional-outbox/saga patterns from the Transactions category.

Concretely: `POST /orders` accepts the order request and, synchronously within the request, does only what's genuinely fast and safe to do synchronously — validate the request and create the order resource in a `pending` state, returning `201 Created` immediately with the order resource showing `status: pending`. The actual multi-step workflow (reserve inventory, charge payment) proceeds *asynchronously* as a saga (Transactions category covers the orchestration-vs-choreography choice in depth) — the client polls `GET /orders/{id}` (or receives a webhook) to observe the order progressing through `inventory_reserved` → `payment_processing` → `confirmed`, or landing in an explicit failure state (`inventory_unavailable`, `payment_failed`) with a clear reason. This directly reuses the long-running-operation/workflow patterns from questions 17/18 — 'create an order with a complex, multi-step fulfillment process behind it' is exactly that shape of problem, not a single synchronous transaction spanning three different systems (inventory, payment, order storage), which would be fragile and exactly the kind of cross-system atomicity the Transactions category explains is hard to achieve safely via a naive distributed transaction."

**Code:**

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

**Follow-up:**

I'd walk through why I wouldn't model this as three separate client-callable endpoints (`POST /reservations`, `POST /charges`, `POST /orders`) that the client itself calls in sequence: that pushes the hardest part of the problem — what happens if step 2 fails after step 1 already succeeded, who's responsible for compensating/rolling back the inventory reservation if the payment fails — onto every client integrating with the API, and different client teams would inevitably get this partial-failure handling subtly wrong in different ways. Centralizing the orchestration server-side, as a saga the order resource's own state machine represents, means the hard distributed-systems problem is solved exactly once, correctly, in the place that owns it — and I'd explicitly connect this design to the transactional outbox pattern (ensuring the order's initial `pending` state and the "start the saga" trigger are committed atomically) and to idempotency (question 5) for the payment-charging step specifically, since that's the step where a duplicate/retried execution has real financial consequences.

**Source:** [Chris Richardson — Saga Pattern](https://microservices.io/patterns/data/saga.html), [Google AIP — Long-running operations](https://google.aip.dev/151)

---

## 28. How Would You Review an API Specification Across Multiple Teams?

**Answer:**

"I'd treat API review as a genuine cross-functional gate, not a rubber-stamp, and I'd structure it around a few concrete dimensions rather than an unstructured 'does this look okay' pass. **Consistency**: does the proposed API follow the org's established naming, versioning, error-format, and pagination conventions (question 2's style-guide point) — deviation here has compounding cost across every future consumer, not just this one API. **Consumer impact**: who's actually going to call this, what does their access pattern look like (tying to question 26's chattiness concern), and has anyone actually validated the design against a real, concrete consumer use case rather than designing in the abstract. **Evolution**: is there an explicit versioning/compatibility story (questions 14-16) for this API from day one, not bolted on after the first breaking change is needed. **Security**: does it correctly apply authentication/authorization (tying to the entire Spring Security category, especially object-level authorization, question 24 there) and does it avoid leaking anything sensitive in responses or errors. **Operability**: does it have the observability hooks (tracing, question 24 here; health signals, question 23) a production API needs from the start, not added reactively after the first incident.

Mechanically, I'd push for review to happen against a **written OpenAPI specification**, before implementation begins, not against a already-built implementation or informal prose description — reviewing a formal spec surfaces inconsistencies and gaps (missing error responses, ambiguous types, undocumented required fields) far more effectively than reviewing running code or a wiki page, and it gives every reviewing team a concrete, precise artifact to comment on."

**Code:**

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

**Follow-up:**

I'd bring up that reviewing against a formal, machine-readable specification (rather than prose or an already-built implementation) enables genuinely valuable automation that manual review alone can't match — a linter (Spectral or similar) enforcing the org's style guide automatically on every spec change in CI, contract-testing tools (Pact) that can verify a *future* implementation actually matches the reviewed spec, and API-diff tools that flag breaking changes against a previous version automatically. I'd frame the actual staff-level contribution to this process as designing the *review process itself* to scale — a single senior engineer manually reviewing every API design across a growing organization becomes a bottleneck and a single point of failure; building a lightweight, mostly-automated review pipeline (linting, breaking-change detection, a lightweight cross-team design-review template/checklist) that catches the majority of common issues automatically, reserving human review time for genuinely novel design trade-offs rather than mechanical style/consistency checks, is what actually lets API quality scale across many teams without the review process itself becoming the constraint.

**Source:** [Spectral — OpenAPI Linter](https://github.com/stoplightio/spectral), [Google API Improvement Proposals (AIPs)](https://google.aip.dev/)

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
