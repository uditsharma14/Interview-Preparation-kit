# Microservices & Architecture Patterns — Interview Prep (Lead/Staff Level, with Code & Sources)

How to use this: each question has **the answer the way I'd actually say it out loud** in an interview, a **diagram/sketch** you could draw on a whiteboard to back it up, and **where the follow-up goes if you're in a Staff-level loop** — because at this level the bar is explaining trade-offs and failure modes, not naming patterns. This file assumes familiarity with the Transactions category (sagas, two-phase commit), the REST API Design file (BFF, idempotency, versioning), and the Redis/Kafka files (circuit breakers, message keys) — it cross-references them rather than repeating them, and focuses on the structural, whole-system architecture questions those files don't cover.

---

## 1. How Do You Decide Microservices Versus a Monolith for a New System?

**How I'd say it:**

"I'd start from the position that a monolith is the right **default** for a new system, not a stepping-stone to be embarrassed about — Martin Fowler's 'MonolithFirst' argument holds up well in practice: you rarely know your actual service boundaries correctly on day one, and a premature microservices split locks in boundary guesses before the domain is well understood, which is far more expensive to undo than refactoring module boundaries inside a single deployable.

The case for splitting into microservices becomes real once specific, concrete pressures show up: **independent scaling needs** (one part of the system has a genuinely different load/resource profile than the rest — a video-transcoding workload versus a lightweight CRUD API); **independent deployability requirements** driven by team structure (multiple teams need to ship on their own cadence without coordinating releases, and a monolith's single deployment unit is genuinely blocking that); or a **genuine need for technology/language diversity** for a specific workload (a component that's a much better fit for a different language/runtime than the rest of the system). I'd be explicit that 'the codebase feels big' or 'microservices are the modern way to build things' are *not* on this list — those are the reasons organizations regret a split, not reasons that justify one."

**Code:**

```text
Monolith (the default, until a concrete pressure says otherwise):

  ┌─────────────────────────────────┐
  │         Single Deployable        │
  │  Orders | Inventory | Payments   │  <- modules, clear internal
  │         (one process,             boundaries, ONE deploy
  │          one database)            pipeline, ONE team can
  └─────────────────────────────────┘   ship the whole thing

Split justified ONLY once a concrete pressure appears:

  Independent scaling:  Inventory has 50x the read traffic of Payments
                          -> Inventory becomes its own service, scaled
                             independently, WITHOUT dragging Payments
                             along for capacity it doesn't need

  Independent teams:     3 teams, each wanting to deploy on their own
                          cadence, currently blocked by one shared
                          release train -> service boundaries drawn
                          along TEAM boundaries (Conway's Law, applied
                          deliberately rather than accidentally)
```

**Where staff-level interviews push further:**

I'd bring up Conway's Law explicitly and its "inverse" (sometimes called the Reverse Conway Maneuver) — an organization's system architecture tends to mirror its communication structure whether or not that's deliberate, so a Staff-level decision here often isn't purely technical: if the actual goal is enabling independent team ownership, it can be more effective to *first* restructure teams around the desired service boundaries and let the architecture follow, rather than drawing service boundaries first and hoping team structure adapts to match. I'd also flag that "the monolith has gotten hard to work in" is frequently a *modularity* problem, not a *deployment-unit* problem — and the fix for bad internal module boundaries is better internal module boundaries, not necessarily a network hop between them; splitting into microservices without first achieving good modularity just produces a distributed system with the same tangled coupling, now paying network/serialization/operational costs on top of the same unsolved boundary problem.

**Source:** [Martin Fowler — MonolithFirst](https://martinfowler.com/bliki/MonolithFirst.html), [Sam Newman — Building Microservices](https://samnewman.io/books/building_microservices_2nd_edition/)

---

## 2. How Do You Decompose a System Into Microservices — By Business Capability or by Subdomain (DDD)?

**How I'd say it:**

"These are two related but distinct lenses, and I'd actually use both, cross-checking one against the other rather than picking a single method mechanically.

**Decompose by business capability** starts from 'what does the business actually *do*' — capabilities like Order Management, Inventory Management, Customer Support — largely independent of current org structure, and maps each capability (or a cohesive cluster of them) onto a service. This tends to produce stable boundaries, since business capabilities change far less often than either team structure or specific technical implementations.

**Decompose by DDD subdomain** (question 3 covers bounded contexts directly) starts from the domain model itself — identifying **core** subdomains (the genuinely differentiating, competitive part of the business — where the org should invest its best engineering effort and want full control), **supporting** subdomains (necessary, but not differentiating — e.g., a fairly generic notification system), and **generic** subdomains (truly commodity, often better bought/outsourced than built — authentication, payment processing via a third party). This lens adds something capability-decomposition alone doesn't: it tells you *where to invest* and where a service boundary should exist specifically to isolate a subdomain's own, different pace of change and different domain language from its neighbors.

In practice I'd draw candidate boundaries from business capability, then validate/adjust them against DDD subdomain analysis — a capability that turns out to span both a core and a generic subdomain internally is often a signal the capability-level boundary is too coarse and should split further, specifically at the seam between the differentiating and commodity parts of it."

**Code:**

```text
Business capability lens (WHAT the business does):
  Order Management | Inventory Management | Customer Support | Billing

DDD subdomain lens (WHERE to invest, and what kind of thing this is):
  CORE:       Order Management's pricing/promotion engine — the actual
              competitive differentiator, deserves the best engineers
              and full in-house control
  SUPPORTING: Inventory Management — necessary, not differentiating,
              built in-house but without heavy specialized investment
  GENERIC:    Payment processing, authentication — commodity, often
              better to BUY (Stripe, an identity provider) than build

Cross-checking the two lenses together often reveals a capability
boundary is too coarse:

  "Order Management" capability, on closer DDD analysis, actually
  CONTAINS both a CORE subdomain (dynamic pricing/promotions — build,
  invest heavily) and a GENERIC one (basic order-status notifications —
  candidate to extract or even buy) — suggesting the service boundary
  should split HERE, at that internal seam, not treat "Order
  Management" as one atomic service
```

**Where staff-level interviews push further:**

I'd bring up that this decomposition exercise is exactly the kind of design artifact worth reviewing explicitly before committing to service boundaries (tying to the Cross-Stack Design Scenarios file's boundary-evaluation question) — and I'd add the transactional-coupling and change-coupling tests from that file as the actual validation step: if a proposed capability/subdomain-derived boundary requires nearly every common operation to become a saga, or if git history shows the "two" proposed services almost always change together, that's evidence the DDD/capability analysis missed something, and the boundary should be redrawn before committing, not patched around afterward with more distributed-transaction machinery.

**Source:** [Eric Evans — Domain-Driven Design](https://www.domainlanguage.com/ddd/), [Chris Richardson — Decompose by Business Capability](https://microservices.io/patterns/decomposition/decompose-by-business-capability.html), [Vaughn Vernon — Implementing Domain-Driven Design](https://vaughnvernon.com/)

---

## 3. What Is a Bounded Context, and Why Does It Matter for Service Boundaries?

**How I'd say it:**

"A bounded context is the boundary within which a specific domain model — its terminology, its rules, its meaning for a given concept — is internally consistent and unambiguous. The same word can (and often should) mean genuinely different things in different bounded contexts: a 'Customer' in the Billing context is fundamentally a billing account with payment methods and invoices; a 'Customer' in the Support context is a person with a history of tickets, preferences, and communication channels. Trying to force one single, universal 'Customer' model to serve both contexts equally well produces a bloated, over-general model that serves neither context cleanly — a very common, very costly modeling mistake in systems that haven't recognized their bounded contexts explicitly.

This matters directly for service boundaries because a bounded context is a strong, principled candidate for a service boundary specifically *because* it's already a place where the domain model itself changes meaning — putting the boundary there means each service's internal model can stay simple, coherent, and free to evolve independently, without needing to negotiate a shared, lowest-common-denominator model with a neighboring context that has genuinely different needs for the 'same' concept."

**Code:**

```text
"Customer" means something DIFFERENT in each bounded context —
this is NORMAL and CORRECT, not a modeling inconsistency to "fix":

  Billing Context:                    Support Context:
    Customer {                          Customer {
      billingAccountId                    ticketHistory
      paymentMethods                      preferredContactChannel
      invoices                            supportTier
      taxJurisdiction                     satisfactionScore
    }                                    }

  Each context's OWN model stays simple and serves ITS OWN needs well.
  A single universal "Customer" trying to satisfy BOTH contexts
  becomes bloated and serves neither cleanly — this divergence is
  exactly where a service boundary belongs
```

**Where staff-level interviews push further:**

I'd bring up the **context map** as the tool that makes bounded contexts actionable at a system level, not just a modeling insight within one context — explicitly documenting the *relationship* between contexts (a Shared Kernel, a Customer/Supplier relationship, a Conformist relationship where one side just accepts the other's model as-is, or an Anti-Corruption Layer, question 4) is what turns "we've identified our bounded contexts" into an actual integration architecture, and I'd treat skipping this step — identifying contexts but never explicitly designing how they relate and translate at their boundaries — as a common, incomplete application of DDD that leaves exactly the integration questions (how do these two services actually talk, and who translates between their different models) unanswered.

**Source:** [Eric Evans — Domain-Driven Design](https://www.domainlanguage.com/ddd/), [Martin Fowler — BoundedContext](https://martinfowler.com/bliki/BoundedContext.html)

---

## 4. What Is an Anti-Corruption Layer, and When Do You Need One?

**How I'd say it:**

"An anti-corruption layer (ACL) is a translation layer placed at the boundary between two bounded contexts (or between your system and an external/legacy system) specifically to prevent one side's domain model, terminology, or quirks from leaking into and 'corrupting' the other side's clean internal model. Instead of your new service directly consuming a legacy system's awkward data shapes and inconsistent semantics throughout its own codebase, the ACL absorbs that awkwardness in one place, translating it into your own service's clean, well-designed internal model — so the ugliness is contained and isolated, not smeared across every part of your code that happens to touch that external dependency.

I'd reach for one specifically when integrating with a legacy system whose model doesn't map cleanly onto your new service's domain (a common, almost inevitable situation during a strangler-fig-style migration, question 5), or when integrating with a third-party/external system whose API shape is dictated by their own concerns, not yours, and adapting your own domain model to match theirs directly would make your own code awkward and tightly coupled to their specific representation."

**Code:**

```text
WITHOUT an anti-corruption layer — legacy quirks leak everywhere:

  New Order Service ---(direct calls)---> Legacy Inventory System
  (every place in the new service that touches inventory has to know
   the legacy system's weird status codes, its "0 means available,
   1 means reserved, 2 means... it's complicated" semantics, directly)

WITH an anti-corruption layer — translation happens ONCE, in one place:

  New Order Service ---> [Anti-Corruption Layer] ---> Legacy Inventory System
       |                        |
       |  clean, well-designed  |  translates legacy's awkward
       |  InventoryStatus enum  |  status codes/semantics into the
       |  (AVAILABLE/RESERVED/  |  NEW service's own clean model,
       |   OUT_OF_STOCK)        |  ONCE, isolated in this one layer
       v
  the REST of the new service never sees the legacy system's
  actual representation at all
```

```java
// The ACL, concretely — a translation boundary, not just a thin proxy
class LegacyInventoryAntiCorruptionLayer {
    InventoryStatus checkStatus(String sku) {
        LegacyInventoryResponse raw = legacyInventoryClient.query(sku); // awkward
        return switch (raw.getStatusCode()) {                             // legacy shape
            case 0 -> InventoryStatus.AVAILABLE;   // translated ONCE, here,
            case 1 -> InventoryStatus.RESERVED;      // into the NEW service's
            case 2 -> InventoryStatus.OUT_OF_STOCK;   // own clean domain model
            default -> throw new UnknownLegacyStatusException(raw.getStatusCode());
        };
    }
}
```

**Where staff-level interviews push further:**

I'd bring up that an ACL is a deliberate, ongoing maintenance cost, not a one-time adapter you write and forget — every change to the legacy/external system's behavior needs to be absorbed and re-translated at this boundary, and I'd treat "who owns and maintains the ACL, and how do we find out when the upstream system's behavior changes underneath it" as a real operational question, not an afterthought — an untested, unmonitored ACL that silently starts mistranslating after an upstream change is a genuinely dangerous failure mode, since it corrupts data quietly rather than failing loudly. I'd also mention that an ACL is often the right, deliberate place to introduce contract tests (question 23) specifically, precisely because it's the one place in the codebase where the external system's actual behavior is meant to be fully characterized and pinned down.

**Source:** [Eric Evans — Domain-Driven Design](https://www.domainlanguage.com/ddd/), [Martin Fowler — Anti-Corruption Layer](https://microservices.io/patterns/refactoring/anti-corruption-layer.html)

---

## 5. Explain the Strangler Fig Pattern for Migrating a Monolith to Microservices

**How I'd say it:**

"Named after the strangler fig vine, which grows around a host tree and gradually replaces it entirely without the host ever being cut down all at once — the pattern migrates a monolith incrementally, by routing specific, individual pieces of functionality to new services one at a time, while the monolith continues serving everything that hasn't been migrated yet, until eventually there's nothing left in the monolith and it can be decommissioned. This avoids the high-risk 'big bang rewrite' — building an entirely new system in parallel and cutting over all at once, which has a long track record of failure (Netscape's famous, multi-year, ultimately-abandoned rewrite is the canonical cautionary tale) — in favor of continuous, incremental, individually-low-risk steps, each independently valuable and independently reversible.

Mechanically, this typically requires a **routing layer** (an API gateway or reverse proxy) sitting in front of both the monolith and the new services, directing each incoming request to whichever one currently owns that specific piece of functionality — as functionality migrates, the routing rules change, but from the outside, clients see one continuous, stable-looking system throughout the entire migration, never an abrupt cutover."

**Code:**

```text
Migration progression over time:

  Phase 1 (start):
    Client -> [Routing Layer] -> Monolith (owns EVERYTHING)

  Phase 2 (Inventory extracted first, chosen for a concrete reason —
  e.g., independent scaling need, question 1):
    Client -> [Routing Layer] -> Monolith (Orders, Payments, ...)
                              -> Inventory Service (NEW)
    (routing rule: /inventory/** -> new service, everything else -> monolith)

  Phase 3 (Orders extracted next):
    Client -> [Routing Layer] -> Monolith (Payments, ... — shrinking)
                              -> Inventory Service
                              -> Order Service (NEW)

  Phase N (monolith fully "strangled"):
    Client -> [Routing Layer] -> Inventory Service
                              -> Order Service
                              -> Payment Service
                              -> ... (monolith DECOMMISSIONED entirely)
```

**Where staff-level interviews push further:**

I'd bring up that the actual hard part of a strangler-fig migration is rarely the routing-layer mechanics — it's the **data** migration happening underneath, specifically when a piece of functionality being extracted still needs data that remains, for a while, authoritatively owned by the monolith's database. This is exactly where an anti-corruption layer (question 4) and often a temporary dual-write/data-sync strategy (mirroring the Transactions file's expand/contract discipline) become necessary, and I'd flag that picking the *order* in which to extract functionality deliberately — starting with pieces that have the fewest, cleanest data dependencies on the rest of the monolith — is a meaningfully important sequencing decision that determines how painful the whole migration turns out to be, not an arbitrary choice of "whatever seems easiest to unplug first."

**Source:** [Martin Fowler — StranglerFigApplication](https://martinfowler.com/bliki/StranglerFigApplication.html), [Sam Newman — Building Microservices](https://samnewman.io/books/building_microservices_2nd_edition/)

---

## 6. What Problems Does a Shared Database Between Microservices Cause, and How Does Database-Per-Service Address Them?

**How I'd say it:**

"A shared database between services — even if each service's *code* is nominally separate — reintroduces exactly the tight coupling microservices are meant to eliminate, just moved into the schema instead of the codebase. Concretely: any service can read (and often write) any table, so there's no real encapsulation of another service's internal data representation — a schema change in one service's tables can silently break another service that happened to query them directly, with no compile-time or even obvious runtime signal that a contract was violated. It also means services can't be scaled or evolved independently at the storage layer — one service's heavy read load competes for the same database resources as another's, and choosing a different, better-fitting storage technology for one service's specific access pattern (e.g., a document store for one service, a relational database for another) becomes impossible if everything has to share one database.

**Database-per-service** fixes this by giving each service exclusive ownership of its own data store — no other service ever queries it directly, only through that service's own API (or published events). This restores real encapsulation (a service's internal schema is genuinely private and free to evolve, since nothing outside can depend on its specific shape) and independent technology choice (each service picks the storage technology that actually fits its own access pattern), at the direct cost of the cross-service query and transaction problems the rest of this file (and the Transactions category) exists to address — question 7's API composition/CQRS, and sagas instead of cross-database ACID transactions."

**Code:**

```text
SHARED DATABASE (anti-pattern) — services LOOK separate, but the
schema is a hidden, uncontrolled integration point:

  Order Service -----\
  Inventory Service ---> [ONE shared database, all tables]
  Payment Service -----/

  Inventory changes a column's meaning -> Order Service, which
  happened to query that table directly, silently breaks — with NO
  compile-time signal, since the coupling lives in the schema, invisible
  to either service's own code review

DATABASE-PER-SERVICE — real encapsulation, each schema genuinely private:

  Order Service -----> Order DB (owned EXCLUSIVELY by Order Service)
  Inventory Service --> Inventory DB (owned EXCLUSIVELY by Inventory Service)
  Payment Service ----> Payment DB (owned EXCLUSIVELY by Payment Service)

  The ONLY way Order Service gets inventory data is through Inventory
  Service's own API/events — never a direct query against its database
```

**Where staff-level interviews push further:**

I'd bring up that database-per-service is often the decision that most concretely reveals whether a proposed service boundary was actually correct (tying back to question 2's cross-checking discipline) — a boundary that turns out to need frequent, ad hoc cross-database joins or transactions to do anything useful is a strong signal the split happened along the wrong seam, and I'd treat "can this service's data genuinely be private, with all external access going through its API" as a concrete, checkable test for a proposed boundary, not just an implementation detail to be worked out after the boundary is already decided.

**Source:** [Chris Richardson — Database per Service](https://microservices.io/patterns/data/database-per-service.html)

---

## 7. How Do You Handle Queries That Need Data From Multiple Services — API Composition Versus CQRS?

**How I'd say it:**

"With database-per-service (question 6), a query that naturally spans multiple services' data — 'show me an order with its current shipping status and the customer's loyalty tier' — has no single database to run a join against anymore, and there are two standard answers.

**API composition**: a composer (an API gateway, a BFF, or a dedicated composing service) calls each relevant service's own API, gets back each piece independently, and joins/aggregates the results in application code, on the fly, at query time. This is simple to reason about and requires no additional infrastructure, but it has real limits: the composer's own performance is bounded by the slowest of the services it calls (question 8's synchronous-call latency stacking), and it's genuinely difficult to do efficient filtering/sorting/pagination across the composed result set if the underlying services don't already support exactly the filter/sort the composed query needs.

**CQRS** (question 16) sidesteps the live-composition cost entirely by maintaining a separate, pre-built, denormalized **read model** — populated ahead of time by consuming events published by each of the owning services, and kept in eventual sync with them — that already has exactly the shape a specific query needs, in one place, queryable directly without any cross-service calls at query time at all. This trades query-time cost for write-time/build-time complexity (maintaining the event consumers that keep the read model in sync) and, critically, for **staleness** — the read model reflects the state as of whenever it last processed the relevant events, not the absolute current state, exactly mirroring the eventual-consistency trade-off from the Redis file's caching discussion, just applied to a purpose-built query-serving store instead of a generic cache."

**Code:**

```text
API COMPOSITION — live, on-demand joining across services:

  Client -> [Composer] -+-> Order Service    (GET /orders/123)
                         +-> Shipping Service (GET /shipments?orderId=123)
                         +-> Customer Service (GET /customers/456/loyalty-tier)
                         |
                         v
                  merge results, return ONE composed response
  -- simple, no extra infra, but latency = SLOWEST of the 3 calls,
  -- and cross-service filter/sort/pagination is genuinely hard

CQRS READ MODEL — pre-built, denormalized, queryable directly:

  Order Service ----(OrderPlaced event)-----\
  Shipping Service --(ShipmentUpdated event)--> [Read Model Builder]
  Customer Service --(LoyaltyTierChanged)----/         |
                                                          v
                                            OrderSummaryReadModel
                                            (already has EVERYTHING
                                             this specific query needs,
                                             in ONE place, pre-joined)

  Client -> GET /order-summaries/123 -> reads DIRECTLY from the
  read model, NO live cross-service calls at query time at all
  -- fast, supports rich filter/sort/pagination, but the read model
  -- is EVENTUALLY consistent, not live-current
```

**Where staff-level interviews push further:**

I'd give the practical decision rule: API composition is the right default for genuinely infrequent, low-latency-tolerant, or simple queries where the added infrastructure of a maintained read model isn't justified; CQRS read models earn their complexity specifically for high-frequency, performance-critical, or richly-filterable queries where live composition's latency stacking and limited query flexibility are actual, measured problems — and I'd be honest that reaching for CQRS by default, for every cross-service query, is a common over-engineering trap, since it means building and operating an event-consuming, read-model-maintaining pipeline for queries that a straightforward composed call would have served perfectly well.

**Source:** [Chris Richardson — API Composition](https://microservices.io/patterns/data/api-composition.html), [Chris Richardson — CQRS](https://microservices.io/patterns/data/cqrs.html)

---

## 8. Compare Synchronous (REST/gRPC) and Asynchronous (Event-Driven) Communication Between Services

**How I'd say it:**

"**Synchronous** communication (a REST call, a gRPC call) has the caller block, waiting for the callee's response, before proceeding — simple to reason about (the code reads top-to-bottom, matching the actual call flow) and gives an immediate result/error, but it directly couples the caller's availability to the callee's: if the callee is slow or down, the caller is affected immediately, and a chain of several synchronous calls stacks up latency additively (and stacks up availability risk multiplicatively — if each of 3 services in a chain is 99.9% available, the *chain's* effective availability is meaningfully lower than any single service's, tying directly to the concurrency/REST API files' discussion of holding resources across slow calls).

**Asynchronous** communication (publishing an event to Kafka, a message queue) decouples the producer's and consumer's availability entirely — the producer publishes and moves on, regardless of whether any consumer is currently up, healthy, or fast; a consumer that's temporarily down simply catches up on its backlog once it recovers, rather than the producer being blocked or failing. This buys resilience and independent scaling at a real cost: the caller doesn't get an immediate result (any response has to come back asynchronously, if at all, complicating request/response-shaped interactions), and the system as a whole now has to reason about eventual consistency and message-ordering/delivery guarantees (the entire Kafka file's concerns) rather than a synchronous call's simpler, if more fragile, immediate-consistency model."

**Code:**

```text
SYNCHRONOUS chain — latency ADDS, availability MULTIPLIES (degrades):

  Client -> Order Service -> Inventory Service -> Pricing Service
            (each call BLOCKS waiting for the next)

  Total latency ≈ sum of all three services' latencies
  Effective availability ≈ 0.999 × 0.999 × 0.999 ≈ 99.7%, NOT 99.9% —
  a chain is only as available as the PRODUCT of its links

ASYNCHRONOUS — producer and consumer availability DECOUPLED:

  Order Service --publishes--> OrderPlaced event --> Kafka topic
                                                          |
                          (Inventory Service consumes WHENEVER it's
                           ready/healthy — a brief Inventory outage
                           does NOT block Order Service AT ALL; it
                           just means a growing, but RECOVERABLE, backlog)
```

**Where staff-level interviews push further:**

I'd bring up that this isn't a system-wide, all-or-nothing choice — a mature architecture typically uses **both**, deliberately, per interaction: synchronous for interactions that are genuinely request/response in nature and where the caller needs an immediate answer to proceed (checking current inventory availability before showing a "add to cart" button), asynchronous for interactions that are fundamentally about "something happened, and other parts of the system should eventually react" (an order being placed triggering fulfillment, notification, and analytics workflows) — and I'd flag that a common architectural mistake is defaulting to synchronous calls even for interactions that are conceptually asynchronous ("fire an event and move on"), purely because synchronous code is easier to write initially, which is exactly how a system ends up with the fragile, availability-multiplying call chains this question describes as the failure mode to avoid.

**Source:** [Chris Richardson — Communication Style](https://microservices.io/patterns/), [Sam Newman — Building Microservices](https://samnewman.io/books/building_microservices_2nd_edition/)

---

## 9. What Is the API Gateway Pattern, and What Problems Does It Solve/Introduce?

**How I'd say it:**

"An API Gateway is a single entry point sitting between external clients and the internal set of microservices, handling cross-cutting concerns centrally so individual services don't each need to reimplement them: request routing to the correct backend service, authentication/token validation (tying to the Spring Security file), rate limiting (tying to the REST API Design/Redis files), request/response transformation, and often API composition (question 7) for endpoints that need to aggregate data from multiple services.

It solves a real problem: without it, every client needs to know the network location of every individual service (or a client-side load-balancing/discovery mechanism), and every cross-cutting concern (auth, rate limiting) has to be correctly reimplemented consistently across every service independently, which is both duplicated effort and a real correctness risk (one service's auth-check implementation subtly differing from another's). It introduces a real cost of its own: it becomes a **central, shared dependency** that every request passes through — meaning it's a single point of failure if not built and operated with real redundancy, and it can become an organizational bottleneck if every service team has to coordinate changes through one gateway team/configuration, rather like the general shared-services-ownership risk discussed in the Tech Leadership file."

**Code:**

```text
WITHOUT a gateway — every client must know every service's location,
and every service reimplements auth/rate-limiting independently:

  Mobile Client  -----\
  Web Client     ------> Order Service (own auth check, own rate limit)
  Partner API    -----/  Inventory Service (own auth check, own rate limit)
                          Payment Service (own auth check, own rate limit)
  -- duplicated, INCONSISTENTLY-implemented cross-cutting logic across
  -- every service, and clients need to know every internal address

WITH a gateway — cross-cutting concerns centralized, ONE entry point:

  Mobile Client  -----\
  Web Client     ------> [API Gateway] --routes to--> Order Service
  Partner API    -----/   - auth validated ONCE                Inventory Service
                           - rate limiting ONCE                Payment Service
                           - request routing/composition
  -- BUT: the gateway is now a SHARED, CRITICAL dependency —
  -- needs its OWN redundancy/scaling, and can become an
  -- organizational bottleneck if every team must route changes
  -- through one gateway-owning team
```

**Where staff-level interviews push further:**

I'd bring up that the API Gateway pattern is distinct from, and often confused with, an API Gateway *product* (Kong, Amazon API Gateway, Spring Cloud Gateway) — the pattern is the architectural role, and I'd walk through the trade-off between a single, shared gateway serving everyone (simpler operationally, but a bigger shared-dependency/bottleneck risk) versus the BFF pattern (REST API Design file's discussion, and question 10 here) giving each distinct client type its own tailored gateway — the right choice depends on how different each client's actual needs are and how much organizational friction a single shared gateway is causing in practice, not a universal best answer.

**Source:** [Chris Richardson — API Gateway](https://microservices.io/patterns/apigateway.html)

---

## 10. Explain the Backend-for-Frontend (BFF) Pattern

**How I'd say it:**

"A BFF is a dedicated backend service built specifically for **one** particular client type or team (a mobile app's BFF, a web app's BFF, a partner-integration's BFF), rather than one shared, general-purpose API gateway trying to serve every client's needs equally well. Each BFF is owned by (or built in close collaboration with) the team building that specific client, and it's shaped exactly around that client's actual needs — a mobile BFF might aggressively compose and flatten data to minimize round trips and payload size for a bandwidth/battery-constrained client; a web BFF might expose richer, more granular data since the web client can afford more, different round trips.

This solves a real problem a single shared gateway/API runs into: different clients genuinely have different needs (a mobile app wants a different data shape and aggregation than an internal admin tool), and forcing one shared API to serve all of them well tends to produce an API that's either overly generic (forcing every client to do its own composition/filtering client-side) or bloated with client-specific special cases (a shared API accumulating `if (client == 'mobile')` branches internally). Giving each client its own BFF, owned by the team that actually understands that client's needs, avoids both failure modes — at the cost of some genuine duplication across BFFs (similar composition logic reimplemented per BFF) that has to be weighed against the benefit of each one being cleanly tailored."

**Code:**

```text
ONE SHARED API trying to serve every client — tends toward either
over-generic OR bloated-with-special-cases:

  Mobile Client  -----\
  Web Client     ------> [ONE Shared API] -> backend services
  Admin Tool     -----/
  -- mobile wants minimal payload, web wants richer data, admin wants
  -- yet different fields — the shared API either forces every
  -- client to do its OWN filtering/composition, or grows internal
  -- "if client == mobile" branches

BFF PER CLIENT TYPE — each tailored, owned by the team that builds
the corresponding client:

  Mobile Client -> [Mobile BFF]  -> aggressively composed, minimal payload
  Web Client    -> [Web BFF]     -> richer, more granular data
  Admin Tool    -> [Admin BFF]   -> different shape entirely, admin-specific

  Each BFF calls the SAME underlying backend services, just composes
  and shapes the response DIFFERENTLY, tailored to its ONE client
```

**Where staff-level interviews push further:**

I'd bring up that the actual decision to introduce per-client BFFs versus a single shared gateway should follow the same team-ownership logic as the Tech Leadership file's shared-service discussion — a BFF makes the most sense when a client's owning team wants (and is capable of) independently evolving their own composition/aggregation logic without waiting on a separate, shared-gateway-owning team, and I'd flag that introducing BFFs purely for architectural tidiness, without a team actually wanting or needing that independence, just multiplies the number of things to operate and keep in sync with backend service changes, for no real organizational benefit.

**Source:** [Sam Newman — Backend for Frontend pattern](https://samnewman.io/patterns/architectural/bff/)

---

## 11. What Is the Sidecar Pattern, and How Does It Relate to a Service Mesh?

**How I'd say it:**

"The sidecar pattern deploys a **helper process alongside** each service instance (typically in the same pod, in a Kubernetes context) to handle cross-cutting infrastructure concerns — network communication (retries, timeouts, mTLS, load balancing), logging/metrics collection, configuration — **without** that logic living inside the service's own application code or requiring every service to link a shared library implementing it consistently across every language/framework the organization happens to use. The service's own code just talks to `localhost`, and the sidecar intercepts and handles the actual cross-cutting behavior transparently.

A **service mesh** (Istio, Linkerd) is the sidecar pattern applied systematically across an entire fleet of services, with a centralized control plane managing and configuring every sidecar (often called a 'data plane' in this context) consistently — giving uniform mTLS, retries, circuit breaking, and observability across every service in the mesh, regardless of what language or framework each individual service happens to be written in, since the sidecar handles it outside the application entirely. This is a genuinely powerful way to get consistent infrastructure behavior across a polyglot fleet of services without needing a shared library reimplemented correctly in every language — at the real operational cost of running and understanding an entirely new, fairly complex piece of infrastructure (the mesh's control plane) that every request now passes through."

**Code:**

```text
Sidecar pattern, per service instance (e.g., one Kubernetes pod):

  ┌─────────────────────────────────┐
  │             Pod                  │
  │  ┌───────────┐   ┌────────────┐ │
  │  │  Service   │   │  Sidecar    │ │
  │  │  (app code)│<->│ (proxy —    │ │
  │  │            │   │  Envoy)     │ │
  │  └───────────┘   └─────┬──────┘ │
  └─────────────────────────┼────────┘
                             |  (mTLS, retries, metrics — handled HERE,
                             v   NOT in the service's own code at all)
                    Other services' sidecars

Service mesh = this pattern applied UNIFORMLY, fleet-wide, with a
CENTRAL control plane configuring every sidecar consistently:

  [Control Plane — Istio/Linkerd] --configures--> every sidecar,
  across every service, regardless of language (Java, Go, Python —
  the SIDECAR handles cross-cutting concerns identically for all of them)
```

**Where staff-level interviews push further:**

I'd bring up the genuine, often-underestimated operational cost of adopting a service mesh — every request now traverses at least one additional network hop (through the local sidecar proxy), the mesh's control plane itself becomes a new, critical piece of infrastructure that needs its own operational expertise and on-call ownership, and debugging a request's actual path through the system now requires understanding the mesh's own behavior (retries/circuit-breaking configured *at the mesh layer*, potentially interacting confusingly with retry logic also present in application code) on top of the application logic itself. I'd frame the decision explicitly: a service mesh earns its complexity for a genuinely large, polyglot fleet where consistent cross-cutting behavior (mTLS everywhere, uniform observability) is a real, otherwise-hard-to-achieve organizational need — I'd be skeptical of adopting one for a modest number of services in a single language, where a well-built shared library or the framework's own built-in resilience features (Resilience4j, per the Redis/Cross-Stack files) achieve the same practical outcome with far less new infrastructure.

**Source:** [Istio documentation](https://istio.io/latest/docs/concepts/what-is-istio/), [Chris Richardson — Sidecar pattern](https://microservices.io/patterns/deployment/service-mesh.html)

---

## 12. What Is a Service Mesh, and What Does It Solve Versus What's Often Oversold?

**How I'd say it:**

"Building directly on question 11's mechanism, what a service mesh genuinely solves well: uniform mutual TLS between every service pair without each service implementing its own certificate handling; consistent, centrally-configured retry/timeout/circuit-breaking policy across a polyglot fleet, without reimplementing it per-language; and rich, automatic, uniform observability (every request's latency/error rate, automatically, for every service, without each one needing its own instrumentation) — genuinely valuable, hard-to-achieve-otherwise capabilities for a large, heterogeneous fleet.

What I'd push back on as often oversold: a service mesh is **not** a substitute for good service boundaries or application-level resilience thinking — retries configured at the mesh layer can mask (or worse, interact confusingly with) retry logic also present in application code, and a team that adopts a mesh assuming it 'handles reliability for us' without still applying the idempotency, timeout, and bulkhead thinking from the Transactions/Redis/Cross-Stack files ends up with a false sense of safety. I'd also push back on 'we need a service mesh' as a reflexive answer to any microservices reliability conversation — for a small-to-moderate number of services, especially in a single language/framework, the same resilience properties are often achievable more simply via a shared library or the framework's built-in features, without taking on an entirely new infrastructure layer and its own operational burden."

**Code:**

```text
GENUINELY solved well by a mesh, hard to achieve otherwise at scale:
  - uniform mTLS across every service pair, zero per-service code
  - consistent retry/circuit-breaker POLICY across a POLYGLOT fleet
  - automatic, uniform per-service observability

OFTEN OVERSOLD / needs care:
  - "the mesh handles reliability" -> still need APPLICATION-level
    idempotency (Transactions file) — a mesh retry of a non-idempotent
    call is just as dangerous as an application-level retry of one
  - mesh-level retries + application-level retries, BOTH configured,
    can COMPOUND unexpectedly (a mesh retrying 3x, each of which the
    application ALSO retries 3x, = 9x actual attempts, not 3x) —
    this needs to be DELIBERATELY reconciled, not assumed to "just work"
```

**Where staff-level interviews push further:**

I'd bring up the specific, easy-to-miss failure mode of retry policies compounding across layers — mesh-level retry configuration and application-level retry configuration (via Resilience4j or similar) operating independently, each unaware of the other, can multiply the actual number of attempts (and, worse, actual downstream side effects if the retried operation isn't genuinely idempotent) far beyond what either layer's configuration alone suggests — and I'd treat "who owns retry policy, at which layer, and how do we make sure they're not silently compounding" as a required design conversation before adopting a mesh alongside existing application-level resilience code, not something to discover during an incident.

**Source:** [Istio documentation](https://istio.io/latest/docs/concepts/what-is-istio/), [Google SRE Workbook — Handling Overload](https://sre.google/sre-book/handling-overload/)

---

## 13. Explain the Ambassador and Adapter Patterns

**How I'd say it:**

"Both are sidecar-adjacent patterns for handling a specific cross-cutting concern outside a service's own application code, but they solve different, more targeted problems than the general sidecar/mesh pattern.

The **ambassador pattern** places a small proxy alongside a service specifically to handle **outbound** connections to external/remote services on the service's behalf — retry logic, circuit breaking, TLS termination, or protocol translation for calls the service makes *out* to something else, without the service's own code needing to implement that logic itself. It's essentially a narrower, single-purpose sidecar focused specifically on the outbound-call concern, sometimes used even without adopting a full service mesh.

The **adapter pattern** (in this deployment-pattern sense, distinct from the classic GoF structural pattern) standardizes a service's own **monitoring/logging/observability** interface — a sidecar that takes whatever native metrics/logs format a specific service or legacy component emits and translates it into the organization's standard observability format, so the rest of the observability tooling doesn't need per-service, per-legacy-format special-casing to understand it."

**Code:**

```text
Ambassador — handles OUTBOUND calls on the service's behalf:

  Service --(localhost call)--> [Ambassador] --(retry/circuit-break/
                                                  TLS/protocol translate)-->
                                                External/Remote Service
  -- the service's OWN code just makes a simple local call; the
  -- ambassador handles all the outbound-call complexity

Adapter — standardizes a service's OWN observability output:

  Legacy Service (emits metrics in its OWN native, non-standard format)
       |
       v
  [Adapter sidecar] -- translates into the ORG'S standard format --
       |
       v
  Standard observability pipeline (Prometheus, etc.) — sees ONE
  consistent format, regardless of what each individual service
  natively emits
```

**Where staff-level interviews push further:**

I'd bring up that both patterns are specific, narrower instances of the same general principle behind the sidecar pattern and service mesh (question 11) — pulling a cross-cutting concern out of application code and into a co-located helper process — and I'd frame recognizing "is this cross-cutting concern narrow enough to solve with a single-purpose ambassador/adapter, or broad enough that we actually need a full service mesh" as the real, practical judgment call, rather than treating these as entirely separate, unrelated patterns to memorize independently.

**Source:** [Chris Richardson — Microservices Patterns (Deployment)](https://microservices.io/patterns/), [Kubernetes Patterns (Ibryam & Huß) — O'Reilly](https://www.oreilly.com/library/view/kubernetes-patterns/9781492050278/)

---

## 14. How Does Service Discovery Work — Client-Side Versus Server-Side?

**How I'd say it:**

"Service discovery solves the problem of a caller needing to find a **current, healthy** network address for a service instance in an environment where instances are constantly being created, destroyed, scaled, and rescheduled (a container orchestrator routinely moves things around) — hardcoding IP addresses simply doesn't work.

**Client-side discovery**: the calling service itself queries a service registry (which tracks currently-healthy instances and their addresses) directly, and does its own load balancing across the returned set of healthy instances — giving the client full control over load-balancing strategy, but requiring every client to implement (or link a library implementing) registry lookup and load balancing consistently.

**Server-side discovery**: the caller makes a request to a well-known, stable address (a load balancer, or in Kubernetes, a Service resource with a stable virtual IP), and that intermediary handles querying the registry and routing to a healthy instance — the caller doesn't need to know anything about discovery at all, which is simpler for clients, at the cost of that routing intermediary now being a required, shared piece of infrastructure every request passes through.

Modern Kubernetes-based deployments overwhelmingly use server-side discovery via Kubernetes' own built-in Service abstraction — client-side discovery (via tools like Netflix's now-legacy Eureka) was more common in the pre-Kubernetes era, where the orchestration platform itself didn't provide this natively."

**Code:**

```text
Client-side discovery — the CALLER queries the registry and load-balances:

  Order Service -> [Service Registry] -> "Inventory instances at:
                                            10.0.1.5, 10.0.1.9, 10.0.1.12"
              -> Order Service picks ONE (round-robin/etc.) and calls it directly

Server-side discovery — a stable address handles it FOR the caller:

  Order Service -> http://inventory-service (stable virtual address)
                        |
                        v
              [Kubernetes Service / Load Balancer]
              -- queries registry, routes to a healthy instance,
              -- INVISIBLY to the calling Order Service
```

**Where staff-level interviews push further:**

I'd bring up that the practical reason server-side discovery dominates today isn't that client-side discovery is inherently worse — it's that Kubernetes made server-side discovery essentially free and built-in (every Service resource provides it automatically), removing the historical reason (needing a separately-operated registry like Eureka or Consul, and a client library in every language) that made client-side discovery attractive in the first place. I'd mention that client-side discovery still has a real niche where finer-grained, client-controlled load-balancing logic genuinely matters (a service mesh's data plane, question 11/12, is actually a sophisticated form of this, just implemented at the sidecar layer rather than in application code directly), rather than being simply obsolete.

**Source:** [Chris Richardson — Client-side Discovery](https://microservices.io/patterns/client-side-discovery.html), [Kubernetes Documentation — Service](https://kubernetes.io/docs/concepts/services-networking/service/)

---

## 15. Explain Circuit Breaker, Bulkhead, and Retry as a Combined Resilience Strategy

**How I'd say it:**

"These three are frequently discussed individually, but their real value is in how they compose together to prevent a failure in one downstream dependency from cascading into a much bigger outage — and I'd walk through them as a system, not three isolated tricks.

**Retry** handles transient, brief failures (a momentary network blip) by trying again, ideally with backoff and jitter (REST API Design file's discussion) — but retrying blindly against a *genuinely* struggling, not just transiently-blipping, dependency just adds more load to something already failing, making things worse, not better.

**Circuit breaker** addresses exactly that gap — it tracks the failure rate of calls to a specific dependency, and once failures cross a threshold, it 'opens,' failing fast (without even attempting the call) for a cooldown period, rather than letting every caller keep retrying against something that's clearly not recovering — this is what actually stops retry logic from turning a struggling dependency into an overwhelmed one.

**Bulkhead** isolates resource pools (thread pools, connection pools) *per dependency*, so a circuit-broken or slow dependency can only ever exhaust the resources allocated to calls against *it specifically* — without a bulkhead, one slow dependency can exhaust a shared thread/connection pool, and that exhaustion then blocks calls to every *other*, unrelated, perfectly healthy dependency sharing the same pool, which is exactly how a single degraded dependency turns into a total, unrelated-feature-affecting outage."

**Code:**

```text
Without bulkheading — ONE slow dependency exhausts a SHARED pool,
taking down calls to OTHER, unrelated, healthy dependencies too:

  [Shared Thread Pool] -- serves calls to BOTH Inventory AND Pricing
     Inventory (SLOW/struggling) -> threads pile up waiting on it
     Pricing (perfectly healthy) -> BLOCKED anyway — no threads left,
                                      even though Pricing itself is fine

With bulkheading — isolated pools, one dependency's problem STAYS contained:

  [Inventory Thread Pool] -- Inventory struggles -> ONLY this pool exhausts
  [Pricing Thread Pool]   -- Pricing calls proceed NORMALLY, unaffected

All three combined, per dependency:
  Retry (handle brief blips) -> Circuit Breaker (stop retrying once
  genuinely struggling, fail fast) -> Bulkhead (contain the blast
  radius to just this ONE dependency's own resource pool)
```

**Where staff-level interviews push further:**

I'd bring up that these three need to be configured to work **together** deliberately, not layered on independently without coordination — a retry policy that keeps retrying even after the circuit breaker has opened defeats the circuit breaker's whole purpose, and a bulkhead sized too small for a dependency's normal healthy load will trigger rejections even when that dependency is perfectly fine, indistinguishable from a genuine problem. I'd frame the actual Staff-level skill as designing these three as one coherent resilience policy per dependency — informed by that dependency's actual normal latency/failure characteristics — rather than applying generic, uniform defaults to every dependency regardless of its real behavior.

**Source:** [Resilience4j documentation](https://resilience4j.readme.io/docs/getting-started), [Michael Nygard — Release It!](https://pragprog.com/titles/mnee2/release-it-second-edition/)

---

## 16. Explain CQRS and When It's Worth the Added Complexity

**How I'd say it:**

"CQRS (Command Query Responsibility Segregation) separates the **write** model (commands — the operations that change state, validated against business rules and invariants) from the **read** model (queries — optimized purely for how data is actually consumed, often denormalized and shaped exactly for specific query needs) — rather than using one single model for both, which is what a typical CRUD/entity-based design does by default.

The case for it: write models need to enforce invariants and business rules correctly, which often favors a normalized, rule-encoding structure; read models need to be fast and shaped for actual query/display needs, which often favors denormalization, precomputed aggregates, and multiple different shapes for the same underlying data depending on which screen/use case is asking. A single shared model trying to serve both well tends to compromise on both fronts — over-normalized for reads (forcing expensive joins/aggregation at query time), or over-denormalized for writes (making invariant enforcement awkward). CQRS is genuinely worth it when read and write patterns are meaningfully different (question 7's read-model use case is a direct example) and when that divergence is causing real, measured pain in the single-model approach — I'd be honest that for a large fraction of typical CRUD applications, read and write needs aren't actually different enough to justify the added complexity of maintaining two separate models and keeping them in sync, and CQRS applied there is pure, unnecessary overhead."

**Code:**

```text
Single shared model (typical CRUD) — one model must serve BOTH:

  Order Entity {id, status, items, customerId, total, ...}
  -- WRITES: validate business rules against this shape (fine)
  -- READS: a dashboard needing "orders per customer per month,
     with customer name and loyalty tier" must JOIN/aggregate
     across this normalized shape EVERY TIME, expensively

CQRS — separate models, each optimized for its OWN purpose:

  WRITE side:  Order Entity (normalized, enforces invariants,
               validated business rules on every command)
                    |
             (OrderPlaced, OrderShipped events published)
                    v
  READ side:   OrderDashboardReadModel {customerId, customerName,
               loyaltyTier, monthlyOrderCount, monthlyTotal, ...}
               -- ALREADY shaped exactly for the dashboard query,
               -- no expensive join/aggregation needed AT QUERY TIME
```

**Where staff-level interviews push further:**

I'd bring up that CQRS doesn't require event sourcing (question 18) — they're frequently paired together but are genuinely separate decisions; you can apply CQRS with a perfectly ordinary CRUD write model, simply also maintaining a separate, denormalized read model kept in sync via change-data-capture or explicit events, without ever adopting the write side's persistence-as-a-sequence-of-events model at all. I'd flag conflating the two as a common, real confusion, and I'd advocate for evaluating each decision on its own separate merits — "do we need a separate read model" and "should our write-side persistence be event-sourced" are two different questions with two different justifications.

**Source:** [Martin Fowler — CQRS](https://martinfowler.com/bliki/CQRS.html), [Chris Richardson — CQRS](https://microservices.io/patterns/data/cqrs.html)

---

## 17. Explain Event Sourcing and Its Trade-Offs Versus Traditional CRUD Persistence

**How I'd say it:**

"Traditional CRUD persistence stores an entity's **current state** — an `UPDATE` overwrites the previous value, and once it commits, the prior state is simply gone unless separately captured in an audit log. Event sourcing inverts this: instead of storing current state, it stores the **complete, ordered sequence of events** that led to the current state (`OrderPlaced`, `ItemAdded`, `OrderShipped`), and current state is derived, on demand, by replaying that event sequence from the beginning (or from the last snapshot, question below) — the events themselves are the actual, immutable source of truth, never overwritten or deleted.

The genuine benefits: a complete, inherent audit trail for free (every state change is a permanently-recorded event, not something you have to separately, deliberately log); the ability to reconstruct state as of *any* point in history by replaying events up to that point; and the ability to build entirely new read models/projections later, from the same historical event stream, for a query need that wasn't anticipated when the events were originally recorded. The real costs: replaying a long event history to reconstruct current state can become slow as the stream grows (mitigated by periodic snapshots — a cached, precomputed current-state checkpoint, so replay only needs to process events since the last snapshot); querying 'current state' at all requires either replaying or maintaining a projection, rather than a simple `SELECT`; and it's a genuinely unfamiliar mental model for a team used to CRUD, with real learning-curve and tooling-maturity costs."

**Code:**

```text
Traditional CRUD — stores CURRENT STATE, overwrites on update:

  orders table: {id: 123, status: "shipped", total: 99.99}
  -- the fact that it was EVER "pending" or "paid" before "shipped"
  -- is GONE, unless separately logged elsewhere

Event Sourcing — stores the SEQUENCE OF EVENTS, current state is DERIVED:

  event_stream (order-123):
    1. OrderPlaced    {items: [...], total: 99.99}
    2. PaymentReceived {amount: 99.99}
    3. OrderShipped    {carrier: "UPS", trackingNumber: "1Z..."}

  Current state = replay ALL events, in order, applying each one's
  effect -> arrives at {status: "shipped", total: 99.99, ...}
  -- but the FULL HISTORY is inherently, permanently preserved too

Snapshot optimization — avoid replaying the ENTIRE history every time:

  Snapshot @ event #500: {status: "shipped", total: 99.99, ...}
  -- to get current state, replay only events AFTER #500, not
  -- from event #1 — bounds replay cost as the stream grows unboundedly
```

**Where staff-level interviews push further:**

I'd bring up that event sourcing is a genuinely significant architectural commitment, not a lightweight technique to sprinkle in — schema evolution for events themselves needs the same rigor as the Kafka file's schema-compatibility discussion (an old event format needs to remain replayable forever, since the entire history must stay reconstructable), and I'd advocate reserving it specifically for domains where the audit trail and point-in-time-reconstruction capabilities are genuinely, directly valuable to the business (financial ledgers, regulated industries with real audit requirements) rather than adopting it broadly across a whole system "because it's a good pattern" — for most ordinary business entities, a traditional CRUD model plus a separate, deliberate audit-log table gets most of the practical benefit at a fraction of the architectural complexity and team-learning-curve cost.

**Source:** [Martin Fowler — Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html), [Greg Young — CQRS and Event Sourcing](https://cqrs.files.wordpress.com/2010/11/cqrs_documents.pdf)

---

## 18. How Do CQRS and Event Sourcing Relate (and Why Are They Often Conflated)?

**How I'd say it:**

"They're frequently discussed and implemented together, which is exactly why they get conflated as one single pattern, but they answer genuinely different questions and can each be adopted independently of the other. CQRS (question 16) answers 'should reads and writes use the same model, or separate ones' — a data-access-shape question. Event sourcing (question 17) answers 'should we persist current state directly, or persist the sequence of events that produced it' — a persistence-strategy question.

They pair naturally because event sourcing's write side *already* naturally produces a stream of events (that's the whole point of the persistence model), which is exactly the input a CQRS read-model builder needs to construct its denormalized projections — so if you've adopted event sourcing, you get a very natural, low-friction path to also building CQRS read models from those same events, which is why the two are so often implemented together in practice. But you can do CQRS with a plain CRUD write side (publishing explicit domain events alongside ordinary state updates, or using change-data-capture, rather than events being the *actual* source of truth), and you can do event sourcing without CQRS at all (a system that only ever replays events to answer queries directly, with no separate, precomputed read model) — I'd make sure to state clearly in an interview that adopting one doesn't require adopting the other, since assuming they're a package deal is a common, avoidable source of over-engineering."

**Code:**

```text
FOUR genuinely independent combinations, not one single "pattern":

  CRUD write + single shared model (no CQRS, no event sourcing):
    the ordinary default — fine for most systems

  CRUD write + CQRS (separate read model, no event sourcing):
    write side is ordinary CRUD; read model built via explicit
    domain events published alongside writes, or via CDC

  Event-sourced write + NO separate read model (event sourcing,
  no CQRS): current state is derived by replay/projection directly,
  with no SEPARATE, precomputed read-model store

  Event-sourced write + CQRS read model (BOTH together — the
  common pairing, since it's low-friction given the write side
  ALREADY produces the exact event stream a read-model builder needs)
```

**Where staff-level interviews push further:**

I'd bring up that explicitly separating these two decisions in a design conversation is itself a useful discipline — I'd want to hear a team justify "why event sourcing" and "why CQRS" as two distinct cost-benefit arguments, not one bundled "let's do the event-sourcing-CQRS thing" decision, since I've seen teams adopt both together, by default, having only really needed one (usually just a CQRS read model, without the much bigger commitment of making events the actual system of record).

**Source:** [Greg Young — CQRS and Event Sourcing](https://cqrs.files.wordpress.com/2010/11/cqrs_documents.pdf), [Martin Fowler — CQRS](https://martinfowler.com/bliki/CQRS.html)

---

## 19. What Is a Read Model / Materialized View, and How Do You Keep It in Sync?

**How I'd say it:**

"A read model (or materialized view, in the CQRS sense rather than the narrower SQL-specific one) is a precomputed, denormalized data structure built and maintained specifically to serve a particular query pattern efficiently — rather than computing that query's result live, on demand, from a normalized source every time it's requested.

Keeping it in sync is the actual crux of implementing this pattern correctly: the read model is built and updated by a **projection** — a component that consumes the events (or change-data-capture stream) representing changes to the source-of-truth data, and applies each one's effect to the read model incrementally, as those changes happen. This means the read model is inherently **eventually consistent** with the source of truth — there's a real, if typically small, lag between a write happening and the read model reflecting it, exactly mirroring the Redis file's cache-consistency discussion, just for a purpose-built query store rather than a generic cache. Handling **projection failures/replay** matters concretely: since the read model is fully derivable from the event stream, if a bug in the projection logic corrupts it, or a new query need requires a differently-shaped read model, the standard recovery is to simply **rebuild it from scratch** by replaying the entire relevant event history from the beginning — a genuinely powerful recovery mechanism traditional CRUD-only systems don't have, since there's no equivalent 'replay the full history' option once an `UPDATE` has overwritten the only copy of a piece of data."

**Code:**

```text
Projection — consumes events, incrementally updates the read model:

  OrderPlaced event ---\
  ItemAdded event -------> [Projection] --> updates OrderSummaryReadModel
  OrderShipped event ---/                    (denormalized, query-optimized)

  Read model reflects state as of "whenever the projection last
  processed relevant events" — EVENTUALLY consistent, bounded staleness,
  same trade-off as Redis cache invalidation lag, just a different layer

Rebuild-from-scratch recovery — a genuine advantage over plain CRUD:

  Projection logic had a bug for the last 3 weeks, corrupting the
  read model -> DELETE the corrupted read model entirely, REPLAY
  every event from the beginning of the stream through the FIXED
  projection logic -> read model is now CORRECTLY rebuilt, from the
  authoritative event history — a recovery option plain CRUD, where
  the "before" state was already overwritten and gone, simply doesn't have
```

**Where staff-level interviews push further:**

I'd bring up that "rebuild from scratch by replaying the full event history" is a genuinely powerful capability, but it has a real, practical limit worth naming — replaying a very large, long-lived event stream from the beginning can be slow, which is exactly why the same snapshot-based optimization from question 17 (or, for a read model specifically, versioned/blue-green rebuild strategies that build the new read model in the background while the old one keeps serving traffic, then atomically cut over) matters here too, not just for the write side's own state-reconstruction — and I'd treat "how long would a full read-model rebuild actually take, and have we tested it" as a concrete, important operational question for any system relying on this recovery mechanism, not an assumed-safe fallback that's never actually been exercised.

**Source:** [Chris Richardson — CQRS](https://microservices.io/patterns/data/cqrs.html), [Martin Fowler — Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html)

---

## 20. Explain the CAP Theorem in Practical Microservices Terms

**How I'd say it:**

"CAP theorem states that a distributed system, in the presence of a **network partition** (P — nodes can't reliably communicate with each other), must choose between **consistency** (C — every node sees the same, most-recent data) and **availability** (A — every request gets a response, even if it might not reflect the absolute latest write). Since partitions are a real, unavoidable possibility in any genuinely distributed system (network failures happen), the practical framing is really 'when a partition occurs, does this specific piece of the system choose C or A' — not a permanent, system-wide label, since different parts of the same overall system legitimately make different choices for different data.

In a microservices architecture specifically, this shows up constantly and concretely: a payment/inventory-count system typically favors **consistency** (better to briefly reject a request than risk overselling/double-charging during a partition — directly mirroring the Cross-Stack Design Scenarios file's multi-region trade-off discussion for exactly this kind of data). A product-catalog or user-profile read typically favors **availability** (better to serve a possibly-slightly-stale product description than fail the request entirely during a brief partition — nobody's business is meaningfully harmed by a few seconds of catalog staleness). The Staff-level skill here is making this choice **explicitly, per data type**, rather than picking one label for an entire system and applying it uniformly, which is almost always the wrong granularity for this decision."

**Code:**

```text
CAP theorem, applied per-data-type (NOT as one system-wide label):

  Payment/Inventory data during a partition:
    choose CONSISTENCY — reject/delay rather than risk overselling
    or double-charging; a temporarily unavailable checkout is better
    than a checkout that's available but WRONG

  Product catalog / user profile data during a partition:
    choose AVAILABILITY — serve possibly-stale data rather than fail
    the request entirely; staleness here has near-zero real business cost

  The SAME overall e-commerce platform makes BOTH choices,
  simultaneously, for DIFFERENT data — there's no single correct
  "are we CP or AP" answer for the whole system
```

**Where staff-level interviews push further:**

I'd bring up PACELC as the more complete, practically useful extension of CAP worth mentioning explicitly — it points out that CAP only describes behavior *during* a partition, but even in the normal, no-partition case, a system still has to choose between latency and consistency (do you wait for a stronger consistency guarantee across replicas, accepting higher latency, or return faster with a potentially slightly-stale read) — and I'd frame this as the more common, everyday trade-off a system actually navigates, since network partitions are relatively rare compared to the routine latency-versus-consistency choice made on every single request in a replicated system.

**Source:** [Eric Brewer — CAP Twelve Years Later](https://www.infoq.com/articles/cap-twelve-years-later-how-the-rules-have-changed/), [Daniel Abadi — PACELC](https://www.cs.umd.edu/~abadi/papers/abadi-pacelc.pdf)

---

## 21. Compare Layered, Hexagonal (Ports & Adapters), and Clean Architecture

**How I'd say it:**

"**Layered architecture** organizes code into horizontal layers (presentation, business logic, data access), with each layer depending only on the layer below it — simple and familiar, but it has a real, common failure mode: business logic ends up depending directly on data-access-layer types (an entity class, a repository interface tightly coupled to a specific ORM), making the business logic harder to test in isolation and harder to change independently of the persistence technology underneath it.

**Hexagonal architecture** (ports and adapters) inverts this dependency: the business/domain logic sits at the center, depending on nothing external — it defines **ports** (interfaces expressing what it needs, like `OrderRepository`), and **adapters** (concrete implementations of those interfaces — a JPA-based adapter, a REST-client-based adapter for an external service) plug in from the outside, implementing the ports the domain defined. The domain never depends on any specific technology; technology depends on the domain's own defined interfaces.

**Clean architecture** (Robert Martin's formulation) is essentially the same core inversion-of-dependency principle as hexagonal, expressed as concentric rings (entities at the very center, use cases around them, then interface adapters, then frameworks/drivers at the outermost ring), with an explicit, named 'Dependency Rule': source code dependencies can only point inward, never outward — the innermost, most stable business rules never depend on anything in an outer, more volatile ring (a specific database, a specific web framework). In practice, hexagonal and clean architecture are different visual framings of the same underlying idea — dependencies point toward the stable business logic, not toward volatile technology choices — and I wouldn't draw a hard technical distinction between them in a design discussion."

**Code:**

```text
Layered (naive) — business logic depends DOWNWARD on data-access types:

  Presentation Layer
        |
        v
  Business Logic Layer  --- depends directly on --->
        |                                              JpaOrderRepository
        v                                              (a SPECIFIC ORM type)
  Data Access Layer
  -- business logic is now coupled to JPA specifics, hard to test
  -- in isolation, hard to swap persistence technology later

Hexagonal / Clean — dependencies point INWARD, toward the domain:

           ┌─────────────────────────────┐
           │      Domain / Use Cases       │  <- defines PORTS
           │  (depends on NOTHING external) │     (interfaces it needs)
           └──────────────┬────────────────┘
                           │ port: OrderRepository (interface)
              ┌────────────┴────────────┐
              v                          v
      JpaOrderRepositoryAdapter   InMemoryOrderRepositoryAdapter
      (implements the port,       (implements the SAME port —
       plugs in from OUTSIDE)      trivial to swap for testing)
```

**Where staff-level interviews push further:**

I'd bring up that the actual, concrete benefit teams get from adopting hexagonal/clean architecture isn't philosophical purity — it's **testability**: business logic that depends only on interfaces it defines itself can be unit-tested with simple in-memory fakes, with zero database, zero HTTP mocking framework, zero test-container infrastructure needed at all, which is a genuinely large, measurable productivity and confidence win for a codebase's core logic. I'd also flag the real cost honestly: this pattern adds genuine indirection (more interfaces, more explicit wiring) that's not worth it for a small, simple CRUD service with thin business logic — I'd reserve it specifically for the parts of a system with genuinely complex, valuable business rules worth protecting and testing in isolation, not apply it uniformly to every service regardless of how much actual domain logic it contains.

**Source:** [Alistair Cockburn — Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/), [Robert C. Martin — Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

---

## 22. Compare Orchestration-Based and Choreography-Based Integration Across a Whole System

**How I'd say it:**

"This is the same orchestration-versus-choreography distinction the Transactions category covers in depth for sagas specifically, but I'd broaden it here to the whole-system integration-style question, since it applies beyond just multi-step transactional workflows.

**Orchestration-style integration**: a central coordinating component (an orchestrator service, or a BFF/gateway acting as one) explicitly directs interactions between other services — calling one, then based on its result, deciding to call another, and so on. This keeps the overall business process visible and reasoned-about in one place, at the cost of the orchestrator becoming a real, central dependency every one of those flows relies on.

**Choreography-style integration**: services react to each other's published events independently, with no central coordinator — each service knows what event to listen for and what to do in response, and the overall system behavior emerges from this decentralized web of event-driven reactions. This keeps individual services more loosely coupled (no service needs to know about a central orchestrator, or even that it's part of a larger, multi-service flow at all), but — exactly as the Transactions category's saga comparison found — the overall system-level behavior becomes much harder to see, reason about, monitor, and debug as a whole, since there's no single place that describes 'here's what happens end-to-end.'

At a whole-system level (not just one saga), I'd generally favor a hybrid: choreography for genuinely independent, fire-and-forget reactions (an order being placed triggering independent, unrelated analytics/notification consumers that don't need to be part of any explicit flow), and orchestration for anything that's a genuine, multi-step business process with real compensation/failure-handling needs, where visibility and debuggability of the whole flow matters more than the marginal coupling reduction choreography would offer."

**Code:**

```text
Choreography — decentralized, services react independently:

  Order Service --publishes--> OrderPlaced
                                     |
             ┌───────────────────────┼───────────────────────┐
             v                       v                       v
   Analytics Service      Notification Service      Inventory Service
   (reacts independently)  (reacts independently)   (reacts independently)
  -- no ONE place shows the full picture; each service's OWN
  -- subscription logic, scattered across the codebase, IS the flow

Orchestration — one place explicitly drives and can be reasoned about:

  OrderPlacementOrchestrator:
    1. call Inventory.reserve()
    2. call Payment.charge()
    3. call Order.confirm()
    4. (on failure at any step: invoke compensations, in reverse)
  -- the ENTIRE flow, and every failure path, is visible in ONE place
```

**Where staff-level interviews push further:**

I'd bring up that this is genuinely the same decision, at a larger scale, as the Transactions file's saga-orchestration-vs-choreography question — and I'd make the connection explicit in an interview to show I recognize it's one underlying trade-off (visibility/centralization vs. decoupling/independence) showing up at multiple scales, from a single multi-step transaction up to an entire system's integration style, rather than treating them as unrelated concepts that happen to share similar names.

**Source:** [Chris Richardson — Saga Pattern (Choreography vs Orchestration)](https://microservices.io/patterns/data/saga.html), [Gregor Hohpe — Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/)

---

## 23. What Is Consumer-Driven Contract Testing, and Why Does It Matter for Independently-Deployed Services?

**How I'd say it:**

"Once services are deployed independently (the whole point of microservices), integration bugs between them can't be reliably caught by end-to-end tests alone — those are slow, flaky, and typically only run against a shared staging environment that doesn't reflect every possible combination of service versions in production. Consumer-driven contract testing solves this differently: each **consumer** of a service's API writes down its actual expectations of that API (a 'contract' — specific requests it makes and the specific response shape it expects back), and that contract is verified independently against the **provider**'s actual implementation, in the provider's own CI pipeline, *before* the provider is ever deployed.

This gives each side fast, independent feedback without needing a slow, shared, full end-to-end test environment: the provider's CI can say 'does my current implementation still satisfy every consumer's stated contract' on every single change, catching a breaking change *before* it's ever deployed and actually breaks a real consumer in production — directly operationalizing the REST API Design file's backward-compatibility discipline as an automated, enforced check rather than a manual review guideline."

**Code:**

```text
1. CONSUMER (Order Service) writes a contract expressing its OWN
   actual expectations of the Inventory Service's API:

   Contract: "when I GET /inventory/WIDGET-100, I expect a response
              shaped like {sku: string, available: number}"

2. Contract is published to a shared broker (Pact Broker or similar)

3. PROVIDER (Inventory Service)'s CI pipeline, on EVERY change,
   verifies its ACTUAL current implementation against EVERY
   consumer's published contract:

   Inventory Service CI: "does my code, RIGHT NOW, actually satisfy
   Order Service's contract? Satisfy every OTHER consumer's contract too?"

   -> if a proposed change would break ANY consumer's contract,
      CI FAILS immediately, on THIS change, BEFORE deployment —
      not discovered later via a shared, slow end-to-end environment,
      and not discovered even LATER, in production, after a real break
```

**Where staff-level interviews push further:**

I'd bring up that this pattern directly operationalizes the "unknown consumers" problem from the REST API Design and Cross-Stack Design Scenarios files — a contract broker inherently creates a registry of which consumers actually depend on a given provider's API, converting "we don't know who might break" into "here's the exact, enumerated list of contracts we need to keep satisfying," which is a genuinely valuable organizational artifact independent of the testing benefit itself. I'd also flag that this pattern requires real cultural buy-in across teams — consumer teams have to actually write and maintain their contracts, and provider teams have to actually treat contract-test failures as blocking, not advisory — and a contract-testing setup that exists but isn't actually enforced as a deployment gate provides much less real protection than it appears to on paper.

**Source:** [Pact — Contract Testing](https://docs.pact.io/), [Martin Fowler — Consumer-Driven Contracts](https://martinfowler.com/articles/consumerDrivenContracts.html)

---

## 24. What Is a Distributed Monolith, and How Does an Architecture End Up There by Accident?

**How I'd say it:**

"A distributed monolith is a system that's been split into multiple independently-deployable services, but which still behaves, in practice, like a single monolith from a coupling and deployment-coordination standpoint — services can't actually be deployed independently without coordinating releases across several of them simultaneously, because they're so tightly coupled (via a shared database, question 6; via synchronous call chains with no independent versioning, question 8; via a shared library whose every change requires every consuming service to redeploy in lockstep) that the *network boundary* between them exists without any of the actual *independence* benefits microservices are meant to provide. It's arguably worse than a plain monolith, since it now also carries every operational cost of a distributed system (network latency, partial failure, more complex debugging) without gaining the independent-deployability, independent-scaling benefits that were the entire justification for taking on those costs in the first place.

This happens by accident most commonly when services are split along boundaries that weren't validated against the tests from question 2/6 (transactional coupling, change coupling, genuine data independence) — teams draw service lines based on a superficial sense of 'this feels like a separate concern' without checking whether the actual data and transactional dependencies support that split, and end up with services that are network-separated in name but tightly, synchronously coupled in every practical sense that matters."

**Code:**

```text
Symptoms of a distributed monolith (checkable, concrete signals):

  - Deploying Service A requires ALSO deploying Service B and C in
    the SAME release, coordinated — "independent" deployability is
    fictional in practice
  - A single request chain synchronously calls through 4+ services,
    each blocking on the next (question 8's availability-multiplying
    chain), with NO async decoupling anywhere in the flow
  - Services share a database, or a tightly-coupled shared library
    whose EVERY change forces every consumer to redeploy together
  - Git history shows these "separate" services' code changing
    together, in the SAME commits, almost every time (the change-
    coupling test from the Cross-Stack Design Scenarios file,
    FAILING here specifically)

  Net result: ALL the operational cost of a distributed system
  (network latency, partial failure modes, harder debugging),
  NONE of the independent-deployability/scaling benefit that was
  the entire justification for the split
```

**Where staff-level interviews push further:**

I'd bring up that recognizing a distributed monolith after the fact, and deciding what to do about it, is itself a real, non-trivial architectural decision — sometimes the right fix is re-merging services back together (accepting that the split was premature or along the wrong seam, and a monolith with good internal module boundaries genuinely serves the organization better right now), and sometimes it's investing in properly decoupling the existing split (introducing async communication where synchronous chains exist, splitting a shared database properly, per question 6) — and I'd frame choosing between "un-split" and "properly decouple" as depending on the same underlying analysis from question 2: does re-evaluating the actual bounded contexts and business capabilities suggest these should genuinely be separate services done right, or does it suggest they were never really separate to begin with.

**Source:** [Sam Newman — Building Microservices](https://samnewman.io/books/building_microservices_2nd_edition/), [Martin Fowler — MonolithFirst](https://martinfowler.com/bliki/MonolithFirst.html)

---

## 25. How Would You Decide Between a Monorepo and Polyrepo for Microservices?

**How I'd say it:**

"I'd treat this primarily as a trade-off between **cross-service change coordination** and **team autonomy/independent tooling**, rather than a purely technical decision with one universally correct answer.

**Monorepo** (all services' code in one repository): makes cross-service, atomic changes genuinely easier — a change to a shared library and every consumer of it can be made and reviewed in one single commit/PR, with CI able to verify the whole set of affected services together, rather than needing a coordinated, multi-repository, multi-PR rollout. It also gives trivial, uniform tooling and dependency-version consistency across every service by default. The costs: build/CI tooling has to scale to a very large, shared codebase (requiring investment in tooling like Bazel/Nx for selective, affected-only builds, rather than naively rebuilding everything on every change), and access-control/ownership boundaries have to be enforced through convention or tooling (CODEOWNERS files) rather than the repository boundary itself providing it for free.

**Polyrepo** (each service in its own repository): gives each team clean, independent ownership, independent CI/CD pipelines, and independent tooling/dependency-version choices by default, at the cost of cross-service changes becoming genuinely harder to coordinate — a shared-library change now requires separate PRs across multiple repositories, sequenced carefully (often via the same versioned, backward-compatible-first discipline from the REST API Design file), and there's no single place to see 'what does the whole system currently look like' the way a monorepo naturally provides."

**Code:**

```text
Monorepo — atomic cross-service changes, shared tooling by default:

  /repo
    /order-service
    /inventory-service
    /shared-lib
  -- change shared-lib AND update every consumer, in ONE commit/PR,
  -- CI verifies the WHOLE affected set together
  -- REQUIRES investment in selective/incremental build tooling
     (Bazel, Nx) as the repo grows, or CI becomes prohibitively slow

Polyrepo — independent ownership/tooling, harder cross-service coordination:

  order-service (own repo, own CI/CD, own team)
  inventory-service (own repo, own CI/CD, own team)
  shared-lib (own repo, own versioned releases)
  -- shared-lib change requires: release a new VERSION, then separate
  -- PRs in EACH consuming repo to bump to it, sequenced carefully —
  -- much more coordination overhead for cross-cutting changes
```

**Where staff-level interviews push further:**

I'd bring up that this decision correlates strongly with organizational scale and team autonomy needs (tying to the Tech Leadership file's shared-platform discussion) — very large organizations with genuinely independent teams (Google, and famously a monorepo at truly enormous scale, being a notable counter-example that only works because of massive, dedicated investment in custom tooling) often lean polyrepo specifically for team autonomy, while other equally large organizations successfully run monorepos specifically because they value atomic cross-cutting changes enough to invest heavily in the tooling that makes a monorepo scale. I'd frame the honest answer as: there's no universally correct choice, and I'd want to know the organization's actual priorities (autonomy vs. cross-service coordination ease) and its willingness to invest in the tooling either choice requires at scale, before recommending one over the other.

**Source:** [Google — Why Google Stores Billions of Lines of Code in a Single Repository](https://cacm.acm.org/magazines/2016/7/204032-why-google-stores-billions-of-lines-of-code-in-a-single-repository/), [Sam Newman — Building Microservices](https://samnewman.io/books/building_microservices_2nd_edition/)

---

## Sources & Further Reading — Consolidated

| Topic | Link |
|---|---|
| Martin Fowler — MonolithFirst | https://martinfowler.com/bliki/MonolithFirst.html |
| Sam Newman — Building Microservices | https://samnewman.io/books/building_microservices_2nd_edition/ |
| Eric Evans — Domain-Driven Design | https://www.domainlanguage.com/ddd/ |
| Chris Richardson — Decompose by Business Capability | https://microservices.io/patterns/decomposition/decompose-by-business-capability.html |
| Vaughn Vernon — Implementing Domain-Driven Design | https://vaughnvernon.com/ |
| Martin Fowler — BoundedContext | https://martinfowler.com/bliki/BoundedContext.html |
| Martin Fowler — Anti-Corruption Layer | https://microservices.io/patterns/refactoring/anti-corruption-layer.html |
| Martin Fowler — StranglerFigApplication | https://martinfowler.com/bliki/StranglerFigApplication.html |
| Chris Richardson — Database per Service | https://microservices.io/patterns/data/database-per-service.html |
| Chris Richardson — API Composition | https://microservices.io/patterns/data/api-composition.html |
| Chris Richardson — CQRS | https://microservices.io/patterns/data/cqrs.html |
| Chris Richardson — Communication Style | https://microservices.io/patterns/ |
| Chris Richardson — API Gateway | https://microservices.io/patterns/apigateway.html |
| Sam Newman — Backend for Frontend pattern | https://samnewman.io/patterns/architectural/bff/ |
| Istio documentation | https://istio.io/latest/docs/concepts/what-is-istio/ |
| Chris Richardson — Service Mesh | https://microservices.io/patterns/deployment/service-mesh.html |
| Google SRE Workbook — Handling Overload | https://sre.google/sre-book/handling-overload/ |
| Chris Richardson — Microservices Patterns (Deployment) | https://microservices.io/patterns/ |
| Kubernetes Patterns | https://k8spatterns.io/ |
| Chris Richardson — Client-side Discovery | https://microservices.io/patterns/client-side-discovery.html |
| Kubernetes Documentation — Service | https://kubernetes.io/docs/concepts/services-networking/service/ |
| Resilience4j documentation | https://resilience4j.readme.io/docs/getting-started |
| Michael Nygard — Release It! | https://pragprog.com/titles/mnee2/release-it-second-edition/ |
| Martin Fowler — CQRS | https://martinfowler.com/bliki/CQRS.html |
| Greg Young — CQRS and Event Sourcing | https://cqrs.files.wordpress.com/2010/11/cqrs_documents.pdf |
| Martin Fowler — Event Sourcing | https://martinfowler.com/eaaDev/EventSourcing.html |
| Eric Brewer — CAP Twelve Years Later | https://www.infoq.com/articles/cap-twelve-years-later-how-the-rules-have-changed/ |
| Daniel Abadi — PACELC | https://www.cs.umd.edu/~abadi/papers/abadi-pacelc.pdf |
| Alistair Cockburn — Hexagonal Architecture | https://alistair.cockburn.us/hexagonal-architecture/ |
| Robert C. Martin — Clean Architecture | https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html |
| Chris Richardson — Saga Pattern | https://microservices.io/patterns/data/saga.html |
| Gregor Hohpe — Enterprise Integration Patterns | https://www.enterpriseintegrationpatterns.com/ |
| Pact — Contract Testing | https://docs.pact.io/ |
| Martin Fowler — Consumer-Driven Contracts | https://martinfowler.com/articles/consumerDrivenContracts.html |
| Google — Why Google Stores Billions of Lines of Code in a Single Repository | https://cacm.acm.org/magazines/2016/7/204032-why-google-stores-billions-of-lines-of-code-in-a-single-repository/ |
