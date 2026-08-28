# LLM System Design — Interview Prep (Staff Level, with Code & Sources)

> **Target level:** Staff · **Baseline:** general hosted-LLM-API production patterns; inherits the baseline of [AI Engineering](../AI%20Engineering/AI_Engineering_Interview_Prep.md), [LLM Fundamentals](../AI%20Engineering/LLM_Fundamentals_Interview_Prep.md), and [Vector Databases & RAG](../AI%20Engineering/Vector_Databases_and_RAG_Interview_Prep.md), which this file assumes and doesn't re-explain · **Last verified:** 2026-08-27 · **Prerequisites:** the three AI Engineering files above, plus general system-design fundamentals (the rest of InterviewSmith, especially [Redis & Caching](Redis_Caching_Interview_Prep.md), [REST API Design](REST_API_Design_Interview_Prep.md), and [Cross-Stack Design Scenarios](Cross_Stack_Design_Scenarios_Interview_Prep.md))

How to use this: each question is an **end-to-end design scenario**, answered **the way I'd actually say it out loud** in an interview, with a **sketch/diagram** you could draw on a whiteboard and **where the follow-up goes if you're in a Staff-level loop** — these scenarios deliberately assume you've already read the AI Engineering, LLM Fundamentals, and Vector Databases & RAG files, and cross-reference their specific questions by number rather than re-explaining RAG pipelines, agent loops, evaluation, or cost/latency management from scratch. What's genuinely new here is the **system design** layer: how these pieces actually compose into a production architecture, and what breaks at real scale. Some scenarios in your list — PII/data privacy, provider fallback, RBAC in RAG, preventing cross-user document leakage — already have dedicated, deep treatment in those companion files; rather than duplicate them, each relevant scenario below cross-references the specific question that already covers it.

<!-- toc -->
## Table of Contents

- [1. Design an Enterprise RAG Platform Serving Multiple Internal Teams](#1-design-an-enterprise-rag-platform-serving-multiple-internal-teams)
- [2. Design an AI Incident-Response Copilot](#2-design-an-ai-incident-response-copilot)
- [3. Design a Customer-Support Chatbot Using LLMs](#3-design-a-customer-support-chatbot-using-llms)
- [4. Design a Scalable Document-Ingestion Pipeline for RAG](#4-design-a-scalable-document-ingestion-pipeline-for-rag)
- [5. How Would You Support 1 Million LLM Requests Per Day?](#5-how-would-you-support-1-million-llm-requests-per-day)
- [6. How Would You Implement Semantic Caching for LLM Responses?](#6-how-would-you-implement-semantic-caching-for-llm-responses)
- [7. How Would You Design Multi-Region LLM Infrastructure?](#7-how-would-you-design-multi-region-llm-infrastructure)
- [8. How Would You Implement Observability for an LLM Application, and What Metrics Would You Monitor?](#8-how-would-you-implement-observability-for-an-llm-application-and-what-metrics-would-you-monitor)
- [Sources & Further Reading — Consolidated](#sources--further-reading--consolidated)

<!-- /toc -->

---

## 1. Design an Enterprise RAG Platform Serving Multiple Internal Teams

**Answer:**

"I'd design this as a **shared platform with per-team boundaries**, not either one monolithic shared index or fully independent systems per team. The platform-level value — shared ingestion tooling, shared evaluation infrastructure, one place to fix a cross-cutting bug — only pays off if teams don't each have to rebuild it. But the isolation requirements (a team's documents shouldn't leak to another team's users, question 11 in the Vector Databases & RAG file) are non-negotiable regardless of how much infrastructure is shared.

Concretely, I'd build a shared **ingestion service** (question 4) that any team can register a document source with, producing consistently-chunked, consistently-embedded content — but every chunk tagged with an authoritative team/tenant identifier at ingestion time, exactly the Vector Databases & RAG file's question 11 pattern. A shared **retrieval and generation API** that every team's application calls, but every request scoped by the caller's validated identity, never a client-suppliable team parameter. A shared **evaluation framework** (AI Engineering file, question 19) that any team can plug their own golden dataset (question 32 there) into, rather than each team building bespoke eval tooling from scratch. And **per-team configuration** where it genuinely needs to differ. A legal team's RAG assistant needs a much more conservative grounding instruction and lower hallucination tolerance than an internal engineering-docs assistant, so system prompts (AI Engineering file, question 6) and acceptable-quality thresholds should be configurable per team, not forced into one global default."

**Code:**

```text
                     +-------------------------+
  Team A's app ----> |  Shared Retrieval + Gen  | <---- Team B's app
  Team C's app ----> |         API              | <---- Team D's app
                     |  (scoped by VALIDATED    |
                     |   team identity, ALWAYS) |
                     +-------------------------+
                              |
              +---------------+---------------+
              v                               v
     +----------------+              +------------------+
     | Shared Vector   |              | Shared Evaluation |
     | DB, tenant-     |              | Framework (each   |
     | scoped metadata  |              | team plugs their  |
     | (Vector DB Q11) |              | own golden set)   |
     +----------------+              +------------------+
              ^
              |
     +------------------+
     | Shared Ingestion   |  <- any team registers a document
     | Service (Q4)       |     source; consistent chunking/
     +------------------+     embedding, tenant-tagged at
                                ingestion time
```

**Follow-up:**

I'd bring up that the hardest part of a genuinely multi-team platform isn't the technical isolation — Vector Databases & RAG file's question 11 already covers that mechanism directly. It's the **governance** question of who owns quality when something goes wrong. If the shared platform's chunking strategy or embedding model choice is wrong for one specific team's document style, is that team empowered to override it locally, or does every change go through a slow, centralized platform team? I'd advocate for a small number of genuinely overridable settings (system prompt, quality thresholds, chunking parameters) exposed per-team, with the platform team owning the shared, harder-to-safely-override infrastructure — the ingestion pipeline's core mechanics, the vector database itself, tenant isolation enforcement. That gives teams real autonomy where it's safe to, without letting every team reinvent the isolation and evaluation infrastructure that's genuinely safer built once, correctly, and shared.

**Source:** [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents), [Qdrant — Multitenancy](https://qdrant.tech/documentation/guides/multiple-partitions/)

---

## 2. Design an AI Incident-Response Copilot

**Answer:**

"This is fundamentally an **agentic**, tool-calling design (AI Engineering file, questions 13-14), not a RAG-over-static-documents design. An incident-response copilot's most valuable information — current error rates, which service is degraded right now, recent deploys, live log output — is inherently real-time and can't be pre-indexed into a vector database the way stable documentation can. The system needs to actively **query** live observability systems as tools, not just retrieve pre-embedded chunks.

Concretely, I'd give it tools for querying the actual observability stack directly — `get_service_health(service_name)`, `get_recent_deploys(service_name, hours)`, `search_logs(service_name, query, time_range)`, `get_error_rate(service_name, time_range)` — each designed per the AI Engineering file's question 15 discipline (narrow, validated, read-only by default). I'd deliberately keep this copilot **read-only** for its actual tool access. It can query and correlate live signals and *suggest* a remediation (a rollback, a scale-up, a specific runbook step), but I would not give it tools that directly execute infrastructure changes without an explicit human-approval gate (AI Engineering file, question 16). An incident-response tool that can autonomously take destructive or state-changing action during a live incident, based on a probabilistic model's read of ambiguous signals, is exactly the kind of high-blast-radius, hard-to-reverse action that question 16's approval-gate discipline exists for. A static knowledge base of past incident postmortems and runbooks (RAG, question 7 in AI Engineering) complements this — useful for 'has something like this happened before, and what fixed it' — layered underneath the live-tool-querying capability, not a replacement for it."

**Code:**

```text
Incident-Response Copilot -- AGENTIC, tool-calling, mostly READ-ONLY:

  On-call engineer: "checkout service p99 latency just spiked, what's
  going on?"

  [Copilot, agent loop, AI Engineering Q13/Q16]:
    Thought: check checkout service's current health first
    Action: get_service_health("checkout-service")
    Observation: {status: "degraded", error_rate: 0.12}

    Thought: check for a recent deploy that might correlate
    Action: get_recent_deploys("checkout-service", hours=2)
    Observation: {deploy_at: "14:32", version: "v2.4.1"}

    Thought: correlate deploy time with the latency spike onset
    Action: search_logs("checkout-service", "error", time_range="14:30-14:45")
    Observation: {matching_logs: [...connection pool exhausted...]}

    -- SUGGESTS: "v2.4.1, deployed at 14:32, correlates with the
       spike. Logs show connection pool exhaustion. Recommend
       rolling back v2.4.1." -- does NOT autonomously execute the
       rollback; surfaces it for HUMAN approval (Q16's gate)
```

**Follow-up:**

I'd bring up that this design's actual value proposition is **speed of correlation across many systems**, not replacing human judgment. An experienced on-call engineer can perform each of these individual lookups manually, but doing so sequentially, across several different tools/dashboards, under the time pressure of a live incident, is exactly where a tool-calling agent that can query several systems and correlate results in seconds provides real, measurable value. I'd frame the copilot's job as *compressing investigation time*, with the human still making and executing the actual remediation decision. I'd also flag that this system needs the exact same evaluation discipline (AI Engineering file, question 19/32) as any other production LLM system: a golden dataset of past real incidents, with known root causes, that the copilot's diagnostic suggestions can be measured against. An incident-response tool that's subtly wrong with confidence is actively dangerous during a real incident, arguably more so than a similarly-wrong customer-support chatbot (question 3).

**Source:** [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents), [Google SRE Book — Managing Incidents](https://sre.google/sre-book/managing-incidents/)

---

## 3. Design a Customer-Support Chatbot Using LLMs

**Answer:**

"The core design tension for a customer-facing support chatbot: it needs to be genuinely helpful and handle the large majority of common questions autonomously (the actual cost/scale justification for building it at all), while having a **reliable, low-friction escalation path to a human** for anything it can't handle well or confidently. Deciding *when* to escalate is a real design problem, not an afterthought.

Concretely, I'd build **RAG grounded in the actual support knowledge base** (AI Engineering file, question 7), with an explicit grounding instruction (its question 6) instructing the model to say so directly when the knowledge base doesn't contain an answer, rather than guessing. This is the primary hallucination-mitigation lever (question 21) for exactly this use case. I'd add **explicit confidence/scope signals** driving escalation: a query the retrieval step returns low-relevance results for (Vector Databases & RAG file, question 9's recall discussion), a query the model itself flags as outside its intended scope (its own system-prompt-defined boundaries, question 6), or an explicit user request to speak to a human. All of these should route to a human agent smoothly, with the full conversation context handed off — not silently making the user repeat themselves. **Tone and brand-voice consistency** comes from a carefully designed, tested system prompt (question 6), since a customer-facing chatbot's phrasing is a genuine brand-representation concern, not just a functional correctness one. And I'd use **tightly scoped tools** (question 15) for anything action-oriented (checking an order status, initiating a return) — narrow, validated, idempotent, with human approval gates (question 16) for anything with real financial consequence like an unprompted refund."

**Code:**

```text
Customer support chatbot -- RAG-grounded, with EXPLICIT escalation paths:

  User query -> [Retrieval against support KB] -> relevance score

  IF relevance score is LOW (retrieval genuinely found nothing
  good, Vector DB file Q9):
     -> escalate to human, WITH the query and a note:
        "no confident match found in knowledge base"

  IF the model's own response indicates it's out of scope
  (system prompt Q6's explicit boundary, e.g. "I don't have
  information about that" triggered by the grounding instruction):
     -> escalate to human, WITH the full conversation transcript

  IF the user explicitly asks for a human:
     -> escalate IMMEDIATELY, no further bot attempts

  OTHERWISE: bot answers directly, grounded in retrieved KB content,
  citing sources (Vector DB file Q10) so the user can verify
```

**Follow-up:**

I'd bring up that escalation-rate and post-escalation-resolution-quality are the two metrics I'd actually watch most closely in production for this system, more than raw "did the bot answer" rate. A bot with a very low escalation rate that's actually failing to recognize when it's wrong is a worse outcome than a bot that escalates more often but does so accurately, since a confidently wrong autonomous answer damages trust far more than a smooth handoff to a human does. I'd treat "is the *decision* to escalate or not itself well-calibrated" as its own thing to evaluate (AI Engineering file, question 19/33), not just "is the bot's autonomous answer quality good when it does answer." I'd also mention that handoff context-transfer quality is a real, easy-to-underestimate UX detail. A human agent receiving an escalation with the full prior conversation and the bot's own reasoning/retrieved-context trace can resolve the issue far faster than one receiving only "user needs help." I'd design the handoff payload deliberately rather than treating it as an afterthought bolted onto the "main" bot-answering flow.

**Source:** [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents), [Google SRE Workbook — Handling Overload](https://sre.google/sre-book/handling-overload/)

---

## 4. Design a Scalable Document-Ingestion Pipeline for RAG

**Answer:**

"I'd separate this into distinct, independently-scalable stages, since each has genuinely different bottlenecks and failure modes. I'd design it as an **asynchronous, event-driven pipeline** rather than a single synchronous batch job — a source-document change event should trigger the pipeline, not a fixed nightly cron regardless of how frequently or infrequently documents actually change.

**Stage 1 — extraction**: pull raw content from heterogeneous sources (a CMS, a wiki, uploaded PDFs, a ticketing system), normalizing formats into plain text/structured content. This stage's bottleneck is typically source-system API rate limits and format diversity, not compute. **Stage 2 — chunking** (AI Engineering file, question 8): split into semantically coherent chunks, respecting document structure. This is CPU-bound and easily parallelized across documents. **Stage 3 — embedding**: the most expensive stage at real scale, since it's either a paid, rate-limited hosted API call per chunk or real GPU compute if self-hosting the embedding model. I'd batch chunks into the largest requests the embedding API/model efficiently supports, rather than one API call per chunk, and apply the same bounded-concurrency/backoff discipline as any other external-dependency call (REST API Design file's retry guidance). **Stage 4 — indexing**: writing to the vector database, including the deduplication (Vector Databases & RAG file, question 7) and provenance-tracking (its question 8) discipline needed to support future updates/deletes cleanly. Each stage should be its own queue-decoupled step (a message per document flowing through stages, Kafka-style), so a slow or temporarily-failing embedding-API stage doesn't block extraction from continuing to make progress on other documents."

**Code:**

```text
Event-driven, stage-decoupled ingestion pipeline:

  Source change event (webhook, CDC, or scheduled poll for
  sources without push notifications)
       |
       v
  [Extraction queue] -> normalize to plain text/structured content
       |
       v
  [Chunking queue] -> semantically-aware chunks (AI Eng file Q8),
       |               tagged with source_document_id + version
       v               (Vector DB file Q8's provenance requirement)
  [Embedding queue] -> BATCHED calls to the embedding model/API,
       |               bounded concurrency + backoff (REST API
       |               Design file's retry discipline)
       v
  [Indexing queue] -> dedup check (Vector DB file Q7) -> write to
                       vector DB, atomically replacing any prior
                       chunks for this document version (Vector
                       DB file Q8)

  -- each stage is INDEPENDENTLY scalable and independently
  -- failure-isolated -- a slow embedding API doesn't block
  -- extraction from processing OTHER documents concurrently
```

**Follow-up:**

I'd bring up that **reconciliation** — a periodic job comparing the source-of-truth document set against what's actually indexed and flagging any drift — is a required safety net for this pipeline, not optional, exactly per the Vector Databases & RAG file's question 8 discussion. An event-driven pipeline is only as reliable as its weakest event-delivery guarantee, and a missed webhook or a silently-failed stage will otherwise accumulate undetected staleness indefinitely, discovered only when a user notices outdated content (the AI Engineering file's own question 27 postmortem is exactly this failure mode). I'd also flag cost estimation as something to build into the pipeline's own design from day one. Logging the actual embedding-API cost per document/batch means a sudden, unexpected spike in ingestion volume (a large new document source being onboarded) is visible as a cost signal immediately, rather than discovered via a surprising bill weeks later — echoing the AI Engineering file's own cost-management discipline (its question 24) applied specifically to the ingestion side rather than the query side.

**Source:** [LangChain — Indexing API](https://python.langchain.com/docs/how_to/indexing/), [Confluent — Schema Evolution and Compatibility](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html)

---

## 5. How Would You Support 1 Million LLM Requests Per Day?

**Answer:**

"1 million requests/day averages to roughly 12 requests/second sustained, but the actual design has to account for real traffic being far peakier than that average. A design that only handles the average rate will fail during a legitimate peak, so I'd size for a realistic peak-to-average ratio, not the daily average directly.

Concretely, I'd use **rate limiting and quota management per caller** (REST API Design file, question 22, applied here), both to protect the system from any single caller's traffic spike and to manage the real, direct cost implication of every additional request against a paid, per-token API. I'd add **request queuing with backpressure** (Cross-Stack Design Scenarios file, question 18) at the boundary between synchronous request-acceptance and the actual LLM call — accepting more concurrent requests than the downstream LLM provider's own rate limits and the system's configured concurrency budget can handle just produces a pile of timing-out requests, not more actual throughput. **Model routing/tiering** (AI Engineering file, question 24) works as a genuine capacity lever, not just a cost lever: routing simple, high-volume request types to a smaller, faster, higher-throughput model frees up whatever rate-limit/capacity budget the slower frontier model has for the requests that genuinely need it. And I'd rely on **horizontal scaling of the application layer itself** — the service issuing LLM calls, not the LLM provider, which the team doesn't control the scaling of. This part is ordinary, well-understood horizontal scaling (more stateless service instances behind a load balancer), and I'd make sure it's not accidentally the actual bottleneck while attention is focused on the LLM-provider-specific concerns."

**Code:**

```text
1,000,000 requests/day ~= 12 req/s AVERAGE -- but real traffic is
PEAKY, not uniform; design for the realistic PEAK, not the average

Layered capacity strategy:

  [Load Balancer] -> [Stateless App Instances, horizontally scaled --
                       ordinary scaling, NOT the LLM-specific bottleneck]
        |
        v
  [Rate limiter / quota manager, per-caller (REST API Q22)]
        |
        v
  [Request queue with BOUNDED depth + explicit backpressure
   (Cross-Stack Q18) -- reject fast (503) rather than accept
   unboundedly and have everything time out slowly]
        |
        v
  [Model router (AI Eng Q24): simple/high-volume request TYPES ->
   smaller/faster model; genuinely complex requests -> frontier
   model -- frees up frontier-model rate-limit budget for what
   actually needs it]
        |
        v
  [LLM Provider -- the ACTUAL, hard external rate-limit ceiling
   this whole design is working within]
```

**Follow-up:**

I'd bring up that the LLM provider's own rate limits (requests-per-minute, tokens-per-minute, often tiered by account/spend level) are frequently the actual hard ceiling this whole design is working against, not the application's own infrastructure. I'd check and explicitly model the provider's specific rate-limit tier against the required peak throughput *before* assuming any application-level scaling work alone solves the problem, and I'd have a concrete plan (a higher-tier account, multiple API keys/accounts load-balanced across, or a secondary provider per question 37 in the AI Engineering file) for when the required throughput genuinely exceeds what a single account's rate limit allows. I'd also mention that prompt caching (AI Engineering file, question 24) becomes disproportionately valuable at this scale specifically. If a meaningful fraction of the 1 million daily requests share a large, stable prompt prefix (a common system prompt, shared RAG context for a popular query pattern), caching that prefix doesn't just save cost — it also reduces the actual token-throughput consumed against the provider's rate limit, directly increasing effective request capacity within the same limit.

**Source:** [Anthropic — Rate Limits](https://docs.anthropic.com/en/api/rate-limits), [Google SRE Workbook — Handling Overload](https://sre.google/sre-book/handling-overload/)

---

## 6. How Would You Implement Semantic Caching for LLM Responses?

**Answer:**

"Prompt caching (AI Engineering file, question 24) caches an exact, stable prompt *prefix* on the provider's side. It's genuinely valuable, but it only helps when the same prefix repeats byte-for-byte. **Semantic caching** solves a different, complementary problem: caching a *full response* keyed not by exact prompt-text match, but by semantic similarity. If a new query is semantically close enough to a previously-answered one (measured via embedding similarity, LLM Fundamentals file question 10), it serves the cached response directly rather than making a fresh, full LLM call at all, even though the new query's literal wording differs from the original.

The implementation: embed each incoming query, then check it against a cache of (query embedding, response) pairs via a similarity search (the same ANN mechanics as retrieval itself, Vector Databases & RAG file, question 2). If a sufficiently similar past query exists above a chosen similarity threshold, return its cached response; otherwise, call the LLM normally and cache the new (query, response) pair for future hits. This is genuinely valuable specifically for **high-repetition query patterns worded differently**. A customer-support bot fielding many different phrasings of 'what's your return policy' benefits enormously, since exact-text caching would never hit on paraphrased duplicates, while semantic caching correctly recognizes them as effectively the same question."

**Code:**

```python
# Semantic cache lookup, BEFORE making an LLM call:

def get_response_with_semantic_cache(query, similarity_threshold=0.95):
    query_embedding = embedding_model.embed(query)
    cached_match = semantic_cache.similarity_search(
        query_embedding, k=1)

    if cached_match and cached_match[0].score >= similarity_threshold:
        return cached_match[0].cached_response  # SKIP the LLM call
                                                    # entirely -- both
                                                    # cost AND latency
                                                    # win

    response = call_llm(query)  # genuine cache miss
    semantic_cache.insert(query_embedding, response)  # cache for
    return response                                       # NEXT time
```

```text
Threshold trade-off:
  TOO LOW (e.g. 0.80): "what's your refund policy" and "how do I
  cancel my subscription" might be treated as similar enough to
  share a cached answer -- WRONG answer served confidently
  TOO HIGH (e.g. 0.999): almost nothing counts as similar enough
  -> cache hit rate collapses toward zero, little practical benefit
```

**Follow-up:**

I'd bring up that the similarity threshold is the single highest-stakes tuning parameter in this whole design, and I'd validate it empirically — against a labeled set of genuinely-equivalent and genuinely-different query pairs, the same evaluation discipline this repository applies everywhere — rather than picking a round number. A threshold that's even slightly too permissive risks serving a **confidently wrong cached answer** to a query that's *almost* but not *quite* the same as the cached one, which is a uniquely dangerous failure mode since it looks exactly like a normal, successful response with no visible signal anything went wrong. I'd also flag **cache invalidation** as the same hard problem it always is (Redis file, questions 3-5). If the underlying information a cached response depends on changes (the actual return policy is updated), every semantically-similar cached entry needs to be invalidated too. I'd bound cached-entry lifetime with a TTL as the same self-healing backstop the Redis file recommends generally, rather than assuming semantic cache entries need no expiration at all just because they were "correct" when cached.

**Source:** [Redis — Semantic Caching for LLMs](https://redis.io/blog/what-is-semantic-caching/), [Pinecone — Vector Similarity Explained](https://www.pinecone.io/learn/vector-similarity/)

---

## 7. How Would You Design Multi-Region LLM Infrastructure?

**Answer:**

"This is the LLM-specific instance of the Cross-Stack Design Scenarios file's general multi-region trade-off framework (its question 3), applied to a system whose core dependency — the LLM provider itself — the team doesn't control the regional deployment of. That's a real, distinguishing constraint versus a typical multi-region database/API design.

Concretely, I'd use **application-layer active-active**: the stateless request-handling layer (rate limiting, RAG retrieval, prompt construction) deploys genuinely active-active across regions, each region serving local traffic with low latency, exactly the Cross-Stack file's eventual-consistency-tolerant pattern, since this layer typically has no cross-region consistency requirement at all. **The LLM API call itself** should route to whichever of the provider's available regional endpoints is geographically closest to minimize round-trip latency, if the provider offers regional endpoints at all. Many hosted providers don't expose full regional choice the way a team's own infrastructure would, so I'd verify this concretely rather than assuming it's available. **The vector database and any long-term memory/state** (AI Engineering file, question 29) needs its own explicit consistency decision, following the Cross-Stack file's question 3 framework directly. If RAG content is read-heavy and tolerant of a brief cross-region staleness window, active-active replication of the vector index across regions is reasonable. If any region-specific data-residency requirement exists — a real, current regulatory constraint, per the LLM Fundamentals file's hosted-vs-self-hosted framing — that specific data needs to stay within its required region, which can mean **not** replicating it globally at all, and instead routing that specific tenant/data's requests to a single region."

**Code:**

```text
Multi-region LLM architecture, per-layer consistency decisions:

  Region US:  [App Layer] --local low-latency--> [LLM Provider's
  Region EU:  [App Layer] --local low-latency-->  nearest regional
  Region APAC:[App Layer] --local low-latency-->  endpoint, if offered]

  App layer: ACTIVE-ACTIVE, eventually consistent, per Cross-Stack
             file Q3 -- typically no real cross-region consistency
             need for stateless request handling

  Vector DB: DEPENDS on data-residency requirements --
    - no residency constraint: active-active replication OK,
      tolerating a brief staleness window
    - REAL residency constraint (regulated data): that SPECIFIC
      tenant's data stays in ONE region; requests for it route
      there specifically, NOT globally replicated

  LLM provider: the team does NOT control this dependency's own
  regional deployment -- verify what regional endpoints (if any)
  are actually offered, rather than assuming full control
```

**Follow-up:**

I'd bring up that the LLM-provider dependency being outside the team's own infrastructure control is the genuinely distinguishing constraint here compared to a typical multi-region system design. A team can't simply "deploy the LLM closer" the way it could with its own database, so the actual latency-optimization levers are narrower: routing to whichever regional endpoint the provider does offer, and otherwise accepting the provider's own baseline latency as a fixed cost. I'd be explicit about this limitation in a design discussion rather than implying more control exists than actually does. I'd also connect this directly to question 37 in the AI Engineering file. A genuinely resilient multi-region design should already have a provider-outage fallback plan, and a regional outage at the *provider's* infrastructure (not the team's own regional deployment) is a real, distinct failure mode worth explicitly covering in that same fallback design, not assumed away because the team's own regions are healthy.

**Source:** [AWS — Multi-Region Application Architecture](https://aws.amazon.com/blogs/architecture/tag/multi-region/), [Anthropic — Model Overview](https://docs.anthropic.com/en/docs/about-claude/models)

---

## 8. How Would You Implement Observability for an LLM Application, and What Metrics Would You Monitor?

**Answer:**

"I'd build observability across the same layers the AI Engineering file's question 36 (detecting production quality degradation) identifies as independent sources of failure. An LLM application's observability can't be just 'is the API responding,' since that tells you nothing about whether the *content* it's producing is actually good, or whether an upstream dependency has silently degraded.

Concretely, I'd track **operational metrics**: latency (broken down by model/tier, since a model-routing design, question 5, has genuinely different latency profiles per tier), error rate, and cost per request (AI Engineering file, question 24), tracked per model version (its question 26/35's versioning discipline) so a regression can be precisely attributed. **Quality metrics**: the same faithfulness/relevance scores (AI Engineering file, question 33) computed continuously against a sample of real production traffic (its question 31's online-evaluation discipline), tracked as a time series specifically to catch gradual decline. **Pipeline health metrics**: retrieval recall proxies, embedding-pipeline success rate, re-indexing job freshness (Vector Databases & RAG file, question 8), since a healthy-looking LLM output metric can mask a degraded input the model is faithfully working from. And **distributed tracing** end-to-end (REST API Design file, question 24), extended specifically to capture which retrieved chunks fed a given response and which tool calls an agent made, so a single confusing production interaction can be fully reconstructed after the fact, not just its final latency and status code."

**Code:**

```text
LLM observability, layered (mirrors AI Engineering file Q36's
degradation-diagnosis categories):

  OPERATIONAL (standard, but per-model-version tagged):
    latency_by_model_tier, error_rate, cost_per_request,
    tokens_in / tokens_out

  QUALITY (continuous online eval, AI Eng file Q31/Q33):
    faithfulness_score_7day_trend, relevance_score_7day_trend,
    escalation_rate (for a support-chatbot-shaped system, Q3)

  PIPELINE HEALTH (Vector DB file Q8):
    time_since_last_successful_reindex, embedding_pipeline_success_rate,
    retrieval_recall_proxy (sampled, labeled)

  TRACE-LEVEL (REST API Design file Q24, extended for LLM specifics):
    trace = {
      request_id, model_version, prompt_version (AI Eng Q26),
      retrieved_chunk_ids (Vector DB file),   <- WHICH chunks fed this
      tool_calls_made,                           <- for agentic systems
      final_response, latency_breakdown_by_stage
    }
    -- lets a SPECIFIC confusing production interaction be fully
    -- reconstructed after the fact, not just its final status code
```

**Follow-up:**

I'd bring up that the trace-level data specifically — capturing which retrieved chunks and tool calls actually fed a given response — is the piece teams most often skip initially and most acutely regret not having during an actual incident investigation. Standard operational tracing (REST API Design file, question 24) captures the request's path through services, but an LLM-specific trace needs to capture the *content* that shaped the response, not just the services it passed through. 'Why did the model say this' is almost always answered by 'because it was given this specific context,' and reconstructing that after the fact without having captured it at request time is often impossible. I'd also mention that alerting thresholds for the quality-metric time series need to be tuned for **gradual drift**, not just sudden step-changes. A threshold-crossing alert configured only for a sharp drop will miss the slow, weeks-long decline the AI Engineering file's own postmortem question (its question 27) describes, which is exactly the shape most real-world quality-degradation incidents actually take.

**Source:** [Google SRE Book — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/), [OpenTelemetry documentation](https://opentelemetry.io/docs/)

---

## Sources & Further Reading — Consolidated

| Topic | Link |
|---|---|
| Anthropic — Building Effective Agents | https://www.anthropic.com/research/building-effective-agents |
| Qdrant — Multitenancy | https://qdrant.tech/documentation/guides/multiple-partitions/ |
| Google SRE Book — Managing Incidents | https://sre.google/sre-book/managing-incidents/ |
| Google SRE Workbook — Handling Overload | https://sre.google/sre-book/handling-overload/ |
| LangChain — Indexing API | https://python.langchain.com/docs/how_to/indexing/ |
| Confluent — Schema Evolution and Compatibility | https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html |
| Anthropic — Rate Limits | https://docs.anthropic.com/en/api/rate-limits |
| Redis — Semantic Caching for LLMs | https://redis.io/blog/what-is-semantic-caching/ |
| Pinecone — Vector Similarity Explained | https://www.pinecone.io/learn/vector-similarity/ |
| AWS — Multi-Region Application Architecture | https://aws.amazon.com/blogs/architecture/tag/multi-region/ |
| Anthropic — Model Overview | https://docs.anthropic.com/en/docs/about-claude/models |
| Google SRE Book — Monitoring Distributed Systems | https://sre.google/sre-book/monitoring-distributed-systems/ |
| OpenTelemetry documentation | https://opentelemetry.io/docs/ |
