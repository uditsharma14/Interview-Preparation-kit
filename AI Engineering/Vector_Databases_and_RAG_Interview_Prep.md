# Vector Databases & RAG Internals — Interview Prep (Lead/Staff Level, with Code & Sources)

> **Target level:** Lead/Staff · **Baseline:** general vector-database and ANN-search concepts (pgvector, Pinecone, Qdrant, FAISS referenced by name where their specific behavior is discussed; no single product version pinned) · **Last verified:** 2026-08-26 · **Prerequisites:** [LLM Fundamentals](LLM_Fundamentals_Interview_Prep.md) questions 9-10 (embeddings, cosine similarity); [AI Engineering](AI_Engineering_Interview_Prep.md) questions 7-12 cover the RAG pipeline's overall shape, chunking strategy, hybrid search, retrieval-quality diagnosis, re-ranking, and handling frequently-updating data — this file goes one layer deeper, into the vector database and embedding-model mechanics those questions build on, and doesn't re-cover ground they already own

How to use this: each question has **the answer the way I'd actually say it out loud** in an interview, a **code/diagram snippet** you could sketch on a whiteboard, and **where the follow-up goes if you're in a Staff-level loop** — because at this level the bar is understanding what a vector database is actually doing under the hood (and where that leaks into real production decisions: recall trade-offs, embedding-model migrations, multi-tenant isolation), not reciting "it stores vectors and finds similar ones." This file assumes you've already read [AI Engineering](AI_Engineering_Interview_Prep.md)'s RAG questions — chunking strategy (its question 8), hybrid search (its question 9), and retrieval-quality diagnosis (its question 10) are covered there and referenced here, not repeated.

<!-- toc -->
## Table of Contents

- [1. How Does a Vector Database Actually Work, and How Is It Different From a Relational Database?](#1-how-does-a-vector-database-actually-work-and-how-is-it-different-from-a-relational-database)
- [2. What Is ANN Search, and How Does HNSW Achieve It?](#2-what-is-ann-search-and-how-does-hnsw-achieve-it)
- [3. What Is Embedding Dimensionality, and How Does It Affect Storage, Performance, and Accuracy?](#3-what-is-embedding-dimensionality-and-how-does-it-affect-storage-performance-and-accuracy)
- [4. How Do You Choose an Embedding Model?](#4-how-do-you-choose-an-embedding-model)
- [5. What Happens When You Change Embedding Models, and How Would You Migrate Millions of Embeddings?](#5-what-happens-when-you-change-embedding-models-and-how-would-you-migrate-millions-of-embeddings)
- [6. What Is Metadata Filtering, and When Do You Need It?](#6-what-is-metadata-filtering-and-when-do-you-need-it)
- [7. How Do You Handle Duplicate Documents in a RAG Index?](#7-how-do-you-handle-duplicate-documents-in-a-rag-index)
- [8. How Do You Update or Delete Embeddings When Source Documents Change?](#8-how-do-you-update-or-delete-embeddings-when-source-documents-change)
- [9. What Is Retrieval Recall, and How Do You Measure It?](#9-what-is-retrieval-recall-and-how-do-you-measure-it)
- [10. How Would You Implement Citations/Sources in a RAG Response?](#10-how-would-you-implement-citationssources-in-a-rag-response)
- [11. How Would You Prevent One User From Retrieving Another User's Documents in Multi-Tenant RAG?](#11-how-would-you-prevent-one-user-from-retrieving-another-users-documents-in-multi-tenant-rag)
- [12. Compare Qdrant, Pinecone, FAISS, and pgvector — When Would You Use pgvector Instead of a Dedicated Vector Database?](#12-compare-qdrant-pinecone-faiss-and-pgvector--when-would-you-use-pgvector-instead-of-a-dedicated-vector-database)
- [Sources & Further Reading — Consolidated](#sources--further-reading--consolidated)

<!-- /toc -->

---

## 1. How Does a Vector Database Actually Work, and How Is It Different From a Relational Database?

**Answer:**

"A vector database stores each record as a high-dimensional numeric vector (an embedding, LLM Fundamentals file question 9) plus, typically, the original content and structured metadata alongside it, and its core operation is fundamentally different from a relational database's: instead of an *exact-match* or *range* query against indexed columns (`WHERE status = 'shipped'`), the primary operation is 'find the K vectors nearest to this query vector' — a **similarity search**, not an equality/range lookup, using a distance metric like cosine similarity (LLM Fundamentals file question 10) to define 'nearest.'

This changes what indexing even means: a relational database's B-tree index works because equality and range comparisons on a single value are cheap and exact; there's no equivalent 'sort the vectors and binary-search' structure for high-dimensional similarity, since 'nearest neighbor' in high-dimensional space doesn't have the same clean ordering a single scalar column does. Computing exact nearest neighbors means comparing the query against *every* stored vector — fine for a few thousand vectors, but it stops scaling well well before a real production corpus's size, which is exactly why vector databases build specialized **approximate** nearest-neighbor indexes (question 2) instead of brute-forcing an exact answer on every query."

**Code:**

```text
Relational database — EXACT/RANGE match on structured columns:

  SELECT * FROM orders WHERE status = 'shipped' AND total > 100;
  -- a B-tree index makes this a fast, EXACT lookup

Vector database — SIMILARITY search against a query vector:

  vector_db.similarity_search(query_vector, k=5)
  -- "give me the 5 stored vectors CLOSEST to this one" --
  -- no exact-match semantics at all; the "closest" answer set
  -- can genuinely change slightly between two runs with an
  -- APPROXIMATE index (question 2), which has no relational-DB
  -- equivalent -- a B-tree index never gives an "approximate" answer
```

**Follow-up:**

I'd bring up that this distinction is exactly why "just add a vector column to our existing relational database" (pgvector, question 12) and "stand up a dedicated vector database" are both legitimate, competing answers rather than one being obviously correct — the actual decision hinges on whether the team's existing operational investment in the relational database (backups, replication, access control already built around it) outweighs a dedicated vector database's typically more mature ANN-specific tooling and horizontal scaling story for very large vector counts. I'd also flag that many production systems genuinely need *both* kinds of query in the same request — "find the 10 most semantically relevant support tickets, but only ones with `status = 'open'` and `team = 'billing'`" — which is precisely what metadata filtering (question 6) exists to combine, rather than treating vector similarity and structured filtering as mutually exclusive query styles.

**Source:** [Pinecone — What Is a Vector Database?](https://www.pinecone.io/learn/vector-database/)

---

## 2. What Is ANN Search, and How Does HNSW Achieve It?

**Answer:**

"Approximate Nearest Neighbor (ANN) search trades a small, usually acceptable amount of accuracy (the returned 'nearest' vectors are very likely, but not *guaranteed*, to be the true K nearest) for a dramatic speed improvement over exact search — exact nearest-neighbor search requires comparing the query against every stored vector (linear in the number of vectors), which becomes impractical at real production scale (millions to billions of vectors), while a well-tuned ANN index can answer the same query in a small fraction of that time by not exhaustively checking everything.

**HNSW** (Hierarchical Navigable Small World) is the most widely deployed ANN algorithm today, and its core idea is a **multi-layer graph**: the bottom layer contains every vector, connected to its nearest neighbors; each layer above it contains a shrinking subset of vectors with progressively longer-range connections, so the very top layer has few nodes and very long links. A search starts at an entry point in the *top* layer and greedily moves toward whichever neighbor is closest to the query, descending a layer each time it can't find a closer neighbor at the current one — using the sparse top layers for fast, coarse, long-distance navigation, then refining within the dense bottom layer for a precise local answer, similar in spirit to how a highway system lets you cover long distances quickly before dropping to local roads for the final approach."

**Code:**

```text
HNSW's layered graph structure:

  Layer 2 (few nodes, LONG links):    A -------------- F
                                        \              /
  Layer 1 (more nodes, medium links):   A --- C ---- F --- H
                                          \   /  \    /
  Layer 0 (ALL nodes, SHORT links):    A-B-C-D-E-F-G-H-I-J-K

  Search: start at an entry point in the TOP layer -> greedily move
  to the neighbor CLOSEST to the query vector -> when no closer
  neighbor exists at this layer, DROP DOWN a layer -> repeat,
  refining with progressively shorter/denser links -> at layer 0,
  do a final, precise local search among the remaining candidates
```

**Follow-up:**

I'd bring up the practical tuning knobs this exposes, since "just enable HNSW" isn't the end of the decision — parameters like `M` (how many connections each node maintains) and `ef_search`/`ef_construction` (how wide a candidate list the search/build process explores) directly trade index size and build time against query speed and recall, and the right values are workload-specific, not universal defaults — a team should measure actual recall against a labeled query set (this file's question 9) at a few different parameter settings rather than accepting whatever a library ships as its default. I'd also mention that ANN's core trade-off — accepting occasional missed true-nearest-neighbors in exchange for speed — is exactly why retrieval-quality monitoring (AI Engineering file, question 10) can't assume perfect recall even when the pipeline is working entirely as designed; some fraction of "the truly best-matching chunk wasn't retrieved" is an accepted, structural cost of using ANN at all, not necessarily a bug to chase down every time.

**Source:** [Malkov & Yashunin — Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs](https://arxiv.org/abs/1603.09320), [Pinecone — HNSW](https://www.pinecone.io/learn/series/faiss/hnsw/)

---

## 3. What Is Embedding Dimensionality, and How Does It Affect Storage, Performance, and Accuracy?

**Answer:**

"Dimensionality is simply how many numbers make up each embedding vector — a model producing 384-dimensional embeddings outputs a list of 384 floats per piece of text; another might produce 1536 or 3072. Higher dimensionality generally lets a model encode more nuanced semantic distinctions (more 'room' to represent different aspects of meaning as separate directions in the vector space), which can improve retrieval accuracy for genuinely subtle distinctions — but it's not free: storage scales linearly with dimension count (a 3072-dimensional embedding takes 8x the storage of a 384-dimensional one, at the same numeric precision), and both the memory footprint and the per-comparison compute cost of an ANN index (question 2) scale with dimensionality too, since every similarity computation touches every dimension.

The practical trade-off: a smaller-dimension embedding model is cheaper to store and query at scale and often *fast enough* to be indistinguishable in practice for many retrieval tasks, while a larger-dimension model's accuracy edge matters most for genuinely fine-grained semantic distinctions a smaller model's more compressed representation can't capture as well. This is a real, measurable trade-off worth testing against a specific corpus and query set (question 4), not something to assume 'bigger is always better' about — a needlessly large embedding dimension for a task that doesn't need that much representational capacity is pure, avoidable storage and latency cost."

**Code:**

```text
Storage cost scales LINEARLY with dimension (at fixed numeric precision,
e.g. float32 = 4 bytes per dimension):

  384-dim embedding:  384 x 4 bytes = 1,536 bytes per vector
  1536-dim embedding: 1536 x 4 bytes = 6,144 bytes per vector  (4x)
  3072-dim embedding: 3072 x 4 bytes = 12,288 bytes per vector (8x)

  -- for 10 million document chunks, that's the difference between
  -- ~15GB and ~123GB of raw vector storage, BEFORE any ANN index
  -- overhead on top -- a real infrastructure cost difference, not
  -- a rounding error at production scale
```

**Follow-up:**

I'd bring up **Matryoshka Representation Learning** (MRL) as a genuinely useful, increasingly common technique worth knowing by name — some modern embedding models are explicitly trained so that a *truncated* prefix of the full embedding (say, the first 256 of 1536 dimensions) still functions as a usable, if less precise, embedding on its own, letting a team dynamically trade dimensionality for storage/speed on the same model without needing to train or serve a genuinely separate smaller model. I'd also mention that dimensionality reduction techniques (PCA, or simple truncation for a non-MRL-trained model) exist for shrinking an existing embedding set after the fact, but I'd be honest that this is a lossy compromise with real, measurable recall cost, and I'd validate it against the same retrieval-quality evaluation (question 9) as any other pipeline change rather than assuming a specific reduction ratio is "close enough."

**Source:** [Kusupati et al. — Matryoshka Representation Learning](https://arxiv.org/abs/2205.13147), [OpenAI — Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)

---

## 4. How Do You Choose an Embedding Model?

**Answer:**

"I'd evaluate against the specific corpus and query patterns the system will actually see, not pick based on a generic leaderboard ranking alone — a model that tops a broad benchmark can still underperform a smaller, more specialized model on a specific domain's actual vocabulary and query style (legal contract language, internal product terminology, code search), since a general-purpose benchmark's average performance doesn't guarantee it reflects any *specific* domain well.

Concretely, I'd weigh: **retrieval quality on real, representative queries** — build a small labeled evaluation set (question 9) of real or realistic queries paired with the chunks that should be retrieved for them, and measure actual recall/precision for each embedding model candidate against it, rather than trusting a benchmark score. **Dimensionality and cost** (question 3) — a model's embedding size directly drives storage and query cost at scale, and a marginal quality gain from a much larger model may not be worth a proportionally much larger infrastructure cost. **Domain fit** — some embedding models are specifically trained or fine-tuned for code, multilingual content, or a particular retrieval style (asymmetric query-to-document versus symmetric text-to-text similarity), and picking a model whose training objective actually matches the task's shape matters more than raw parameter count. **Licensing and hosting** — whether the model is available via a hosted API (simple, no infrastructure, ongoing per-call cost) or must be self-hosted (more operational overhead, but no per-call cost and full data control, echoing the AI Engineering file's question 1 hosted-vs-self-hosted framing applied specifically to embeddings)."

**Code:**

```text
Evaluation-driven embedding model selection, NOT leaderboard-driven:

  1. Build a labeled eval set: real/realistic queries, each paired
     with the chunk(s) that SHOULD be retrieved for it (question 9)

  2. For each embedding model candidate:
     - embed the full corpus with it
     - run every eval query through it
     - measure recall@k / precision@k against the labeled answers

  3. Compare: does a general-purpose leaderboard-topping model
     actually win on THIS specific corpus/query distribution, or
     does a smaller, domain-fit model perform comparably or better
     at a fraction of the dimensionality/cost?

  -- the LEADERBOARD tells you what performs well on ITS benchmark
  -- distribution; the EVAL SET tells you what performs well on
  -- YOURS -- these are not guaranteed to agree
```

**Follow-up:**

I'd bring up the MTEB (Massive Text Embedding Benchmark) leaderboard as a legitimate, useful *starting point* for narrowing candidates worth actually evaluating — it's genuinely valuable for surfacing which models are broadly strong, and I wouldn't dismiss it — but I'd be explicit that it's a starting shortlist, not a final decision, precisely because MTEB's aggregate score averages across many different task types and domains that may not resemble the specific system's actual retrieval task at all. I'd also mention that this decision needs periodic revisiting, not a one-time choice made at launch and never reconsidered — newer embedding models are released frequently, and a system that never re-evaluates its embedding model choice against current alternatives risks leaving a real retrieval-quality (or cost) improvement on the table indefinitely, though any actual switch has to go through question 5's migration discipline, not a casual swap.

**Source:** [Hugging Face — MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard), [OpenAI — Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)

---

## 5. What Happens When You Change Embedding Models, and How Would You Migrate Millions of Embeddings?

**Answer:**

"The critical fact that makes this a real migration, not a config change: embeddings from two different models live in **entirely different, incompatible vector spaces** (LLM Fundamentals file, question 9's follow-up) — there's no meaningful way to compare a query embedded with the new model against documents still embedded with the old one; the distances and directions simply don't correspond to anything, so 'similarity' scores computed across the two would be essentially meaningless. This means a change of embedding model can't be applied incrementally to individual documents as they happen to be touched — every single existing embedding has to be regenerated with the new model before the new model can be used for retrieval at all, or you end up silently mixing incompatible embeddings in the same index.

My approach mirrors the same expand/contract discipline used for a zero-downtime schema migration elsewhere in this repository: **re-embed the entire corpus with the new model into a genuinely separate index** (a new collection/namespace, not overwriting the old one in place) — this can run as a background batch job, taking however long it takes, without disrupting the currently-serving old index at all. **Validate the new index's retrieval quality** against the same labeled evaluation set (question 9) used to pick the new model in the first place, confirming it performs at least as well in practice, on the actual corpus, not just on the model-selection benchmark. **Cut over reads** to the new index only once validated — ideally via a gradual rollout (a percentage of traffic, monitored, before 100%) rather than an instant, all-at-once switch. Only after the cutover is confirmed healthy would I decommission the old index — keeping it available as a fast rollback path during the transition."

**Code:**

```text
Embedding-model migration, expand/contract style:

  1. EXPAND: re-embed the ENTIRE corpus with the NEW model into a
     SEPARATE index/collection -- old index keeps serving, untouched,
     for the full duration of this (potentially long) batch job

  2. VALIDATE: run the SAME labeled eval set (question 9) against
     the new index -- confirm real, measured retrieval quality
     before trusting it with live traffic

  3. GRADUAL CUTOVER: route a small percentage of read traffic to
     the new index, monitor real quality/latency signals, expand
     gradually -- NOT an instant all-at-once switch

  4. CONTRACT: only decommission the OLD index once the new one has
     been fully live and healthy for a defined bake period -- the
     old index is the fast, safe ROLLBACK path until then

  -- NEVER mix embeddings from BOTH models in the SAME index/query --
  -- they are NOT comparable, and doing so silently corrupts every
  -- similarity score computed across the mismatched pair
```

**Follow-up:**

I'd bring up that the re-embedding batch job itself needs the same operational care as any large data-migration job elsewhere in this repository — bounded batching (not one giant unbroken operation), retry/resume-from-checkpoint capability for a job that might realistically take hours or days over millions of documents, and explicit cost estimation up front, since re-embedding an entire corpus through a hosted embedding API is a real, sometimes substantial one-time cost worth knowing in advance rather than discovering via a surprising bill. I'd also flag that this exact migration cost is a legitimate, concrete factor in the embedding-model-selection decision (question 4) itself — a model choice made too casually, without confidence it'll hold up well for a reasonable amount of time, invites paying this full re-embedding cost again sooner than a more careful initial evaluation would have required.

**Source:** [Pinecone — Vector Database Migration Considerations](https://www.pinecone.io/learn/vector-database/)

---

## 6. What Is Metadata Filtering, and When Do You Need It?

**Answer:**

**"Metadata filtering** combines a vector similarity search with a structured, exact-match/range filter on fields stored alongside each vector — 'find the 5 most semantically similar chunks, but *only* among those where `department = 'legal'` and `document_date > 2025-01-01`' — rather than a pure similarity search across the entire index regardless of any other constraint. Every practical vector database supports this natively, since a pure, unfiltered similarity search is rarely what a real application actually needs: almost every production RAG system has *some* dimension along which retrieval genuinely needs to be scoped, not just ranked by semantic relevance.

I'd reach for it any time there's a real, non-semantic constraint on what should even be eligible for retrieval — access control (a user should only ever retrieve documents they're authorized to see, question 11), recency (only search documents from the last quarter), document type (only search FAQs, not internal engineering notes, for a customer-facing assistant), or explicit user-selected scope (a user filtering search results to a specific project or folder in the product UI). The key implementation detail worth being precise about: metadata filtering should be applied as a genuine **pre-filter or integrated filter** within the ANN search itself wherever the database supports it, not as a post-hoc filter applied to the top-K results *after* retrieval — filtering after the fact means the K results the ANN index returned might all get filtered out, leaving too few (or zero) actually-eligible results, even though plenty of eligible, relevant documents exist further down the unfiltered ranking that a pre-filtered search would have found."

**Code:**

```text
WRONG — filtering AFTER retrieval (post-filter):

  top_10 = vector_db.similarity_search(query_vector, k=10)
  filtered = [r for r in top_10 if r.metadata["department"] == "legal"]
  -- if NONE of the unfiltered top 10 happen to be "legal" docs,
  -- filtered is EMPTY, even though relevant legal documents exist
  -- further down the FULL ranking, outside the top 10 -- WRONG results

CORRECT — filtering INTEGRATED into the search itself (pre-filter):

  results = vector_db.similarity_search(
      query_vector, k=10,
      filter={"department": "legal", "document_date": {"$gt": "2025-01-01"}}
  )
  -- the ANN search itself only considers ELIGIBLE vectors when
  -- finding the top K -- guaranteed up to 10 eligible results,
  -- not "up to 10 minus whatever got filtered out afterward"
```

**Follow-up:**

I'd bring up that pre-filtering has a real performance cost worth being aware of, not just a correctness benefit — depending on the specific ANN index and how selective the filter is, a highly restrictive filter (only 0.1% of the corpus matches) can force the search to do meaningfully more work to find enough eligible candidates than an unfiltered search would, and different vector databases handle this trade-off differently (some maintain separate, filter-aware index structures; others apply the filter during graph traversal, question 2, with varying efficiency depending on filter selectivity) — this is a genuine, product-specific detail worth benchmarking directly against the actual filter patterns a system will use, rather than assuming filtering is "free" just because the API makes it easy to express. I'd also connect metadata filtering directly to question 11's access-control discussion — using it as the *mechanism* for enforcing per-user/per-tenant document isolation is exactly the pattern, but it has to be applied server-side, from a trusted identity, never from a client-suppliable filter value, for the same reason the Spring Security file insists on deriving a tenant ID from a validated JWT claim rather than a request parameter.

**Source:** [Pinecone — Metadata Filtering](https://docs.pinecone.io/guides/data/filter-with-metadata), [Qdrant — Filtering](https://qdrant.tech/documentation/concepts/filtering/)

---

## 7. How Do You Handle Duplicate Documents in a RAG Index?

**Answer:**

"Duplicates degrade a RAG system in a specific, easy-to-miss way: if the same (or near-identical) content exists as multiple chunks in the index, several of a query's top-K retrieved results can end up being redundant copies of the same information — wasting context-window budget on repetition rather than genuinely diverse, useful context, and in the worst case crowding out a *different*, actually-relevant chunk that would have made the top-K if the duplicates weren't occupying multiple slots.

My approach: **detect duplicates before indexing**, not after — exact duplicates are cheap to catch with a content hash (identical text, hash-and-compare before ever generating an embedding for it); near-duplicates (the same underlying content with minor formatting differences, or the same document ingested from two different source systems) need a similarity-based check instead — comparing a new chunk's embedding against existing ones and treating anything above a high similarity threshold as a likely duplicate worth deduplicating or flagging for review, rather than blindly indexing it as new. For content that's *legitimately* similar but not truly duplicate (two product FAQ entries that happen to be worded very similarly but answer genuinely different questions), I'd be conservative about auto-deduplication and prefer surfacing likely-duplicate pairs for a human to confirm, rather than silently dropping content that might not actually be redundant."

**Code:**

```text
Ingestion-time deduplication, layered:

  1. EXACT duplicates -- cheap, deterministic:
     content_hash = sha256(chunk.text.strip().lower())
     if content_hash in seen_hashes:
         skip_indexing(chunk)  # or increment a reference count instead
                                  # of creating a redundant vector entry

  2. NEAR duplicates -- similarity-based, needs a threshold decision:
     candidate_embedding = embedding_model.embed(chunk.text)
     similar_existing = vector_db.similarity_search(
         candidate_embedding, k=1)
     if similar_existing and similar_existing[0].score > 0.98:
         flag_as_likely_duplicate(chunk, similar_existing[0])
         # conservative default: FLAG for review, don't auto-drop --
         # a high similarity score isn't PROOF of true redundancy
```

**Follow-up:**

I'd bring up that near-duplicate detection's similarity threshold is itself a real tuning decision with a genuine precision/recall trade-off, not an arbitrary constant — too low a threshold (too aggressive) risks discarding genuinely distinct content that merely happens to be phrased similarly; too high a threshold (too conservative) lets meaningful redundancy through — and I'd validate whatever threshold is chosen against a labeled sample of known duplicate/non-duplicate pairs from the actual corpus, the same evaluation discipline this file and the AI Engineering file apply to every other retrieval-quality decision, rather than picking a round number and trusting it blindly. I'd also mention that duplicate documents are a common, specific symptom of a broader **data pipeline hygiene** problem worth investigating at the source — if the same content keeps entering the ingestion pipeline from multiple upstream systems (a CMS and a wiki both containing the same policy document, say), the durable fix is often establishing a single source of truth for that content upstream, rather than indefinitely relying on ingestion-time deduplication logic to paper over an architectural duplication problem.

**Source:** [Pinecone — Deduplication in RAG](https://www.pinecone.io/learn/retrieval-augmented-generation/)

---

## 8. How Do You Update or Delete Embeddings When Source Documents Change?

**Answer:**

"This is the vector-database-specific version of the AI Engineering file's question 12 (handling RAG over frequently-updating data) — I'd apply the same staleness-management discipline there, focused here on the actual mechanics of the vector store itself. The core requirement: every indexed chunk needs a stable, traceable link back to its **source document and version**, so that when a source document changes, the system can identify and act on exactly the chunks that came from it, rather than needing to rediscover that mapping after the fact.

Concretely: on a document **update**, I'd re-chunk and re-embed the changed document, then **delete the old chunks and insert the new ones as a single logical operation** (most vector databases support an upsert primitive, but the actual old-chunk-count and new-chunk-count can differ if the update changed the document's length enough to shift chunk boundaries — a naive upsert keyed only by document ID, without also cleaning up now-orphaned old chunk IDs, can leave stale chunks behind). On a document **deletion**, every chunk that traces back to it needs to be deleted from the vector index too — an application that deletes a document from its primary content store but forgets to also purge the corresponding vector-index entries leaves a real, if often invisible, staleness bug: the RAG system continues confidently citing content the source system no longer considers valid or even present at all."

**Code:**

```text
Every indexed chunk stores its provenance explicitly, not just its
embedding and text:

  {
    "id": "doc-42-chunk-3",
    "embedding": [...],
    "text": "...",
    "metadata": {
      "source_document_id": "doc-42",
      "source_document_version": "v7",
      "chunk_index": 3
    }
  }

On document UPDATE (doc-42 changes from v7 to v8):
  old_chunk_ids = vector_db.find_by_metadata(source_document_id="doc-42")
  new_chunks = chunk_and_embed(updated_document)  # v8's chunks --
                                                     # count may DIFFER
                                                     # from v7's chunk count
  vector_db.delete(old_chunk_ids)   # remove ALL v7 chunks explicitly,
  vector_db.insert(new_chunks)       # not just "the same number of IDs"

On document DELETION:
  chunk_ids = vector_db.find_by_metadata(source_document_id="doc-42")
  vector_db.delete(chunk_ids)  # MUST happen -- a deleted source
  # document with orphaned vector-index entries means the RAG system
  # keeps confidently citing content that no longer exists
```

**Follow-up:**

I'd bring up that this update/delete discipline needs to be **triggered automatically by the same event that changed the source document**, not left as a manual or best-effort follow-up step — exactly the same architectural principle as the Transactions file's transactional outbox pattern, just applied to keeping a vector index consistent with its source of truth instead of keeping Kafka consistent with a database: if a content-management system's own save/delete action doesn't reliably and atomically trigger the corresponding vector-index update, staleness will accumulate silently over time, discovered only when a user notices outdated or nonexistent content being confidently cited — precisely the failure mode the AI Engineering file's own production-incident question (its question 27) walks through in detail. I'd also mention that a periodic reconciliation job — comparing the source-of-truth document set against what's actually indexed and flagging any mismatch — is a valuable defense-in-depth safety net worth having regardless of how well-designed the event-driven update path is, since it catches whatever the event-driven path misses (a missed webhook, a failed re-indexing job that nobody's monitoring for, echoing the Redis file's own cache-invalidation discipline).

**Source:** [LangChain — Indexing API](https://python.langchain.com/docs/how_to/indexing/), [Pinecone — Managing Data Freshness](https://www.pinecone.io/learn/retrieval-augmented-generation/)

---

## 9. What Is Retrieval Recall, and How Do You Measure It?

**Answer:**

"Retrieval recall (formally, recall@K) measures, out of all the chunks that are *genuinely relevant* to a given query, what fraction actually appear somewhere in the top-K results the retrieval step returns — a recall@5 of 0.8 for a query means 80% of the truly relevant chunks for it made it into the top 5 returned, and 20% didn't, regardless of how many *irrelevant* chunks might also be in that top 5 (which is what **precision** measures instead — the fraction of the top-K results that are actually relevant, a related but distinct question).

Measuring it for real requires a **labeled evaluation set**: a representative sample of realistic queries, each paired with the specific chunk(s) in the corpus that a human (or a careful process) has confirmed are genuinely the right answer for that query — without this ground truth, there's no way to compute recall at all, only to eyeball whether retrieved results look plausible. I'd build this set the same way the AI Engineering file's question 19 recommends building any evaluation set — sourced from real usage patterns or domain-expert judgment, not just examples the engineer building the pipeline happened to think of, since self-authored eval queries tend to be biased toward cases the current implementation already handles well."

**Code:**

```text
Recall@K = (relevant chunks that appear in the top-K results)
           / (total relevant chunks that exist for this query)

Example: for query "what is the refund policy for expedited orders",
the labeled ground truth says chunks {C7, C12, C15} are ALL genuinely
relevant (the answer is split across three source chunks).

Retrieval returns top-5: [C7, C3, C12, C9, C20]
  -- relevant chunks FOUND: C7, C12 (2 out of 3 relevant chunks)
  -- Recall@5 = 2/3 = 0.67  (C15 was missed entirely)
  -- Precision@5 = 2/5 = 0.40 (2 of the 5 returned results were relevant)

Aggregate across the FULL labeled eval set (not just one query):
  mean_recall_at_5 = average(recall@5 across every eval query)
  -- THIS number is what you compare before/after a chunking,
  -- embedding-model, or retrieval-parameter change (question 5,
  -- AI Engineering file question 8)
```

**Follow-up:**

I'd bring up that recall and precision genuinely trade off against each other as K changes, and neither one alone tells the whole story — increasing K (returning more results) mechanically increases recall (more chances to include every relevant chunk) while generally decreasing precision (more irrelevant results mixed in), so the actual, useful question isn't "what's our recall" in isolation, but "at the K we actually use in production, what's both our recall and precision, and does that combination reflect real user-facing quality" — a system with excellent recall@50 but that only ever sends the top-3 chunks to the LLM hasn't actually benefited from that high recall number at all. I'd also mention that building the labeled ground-truth set is genuinely the expensive, hard part of this whole exercise, not the metric computation itself — I'd advocate for growing it incrementally from real production query logs and real user feedback signals (AI Engineering file question 19's after-shipping discipline) rather than trying to construct a large, comprehensive one entirely up front before any real usage data exists.

**Source:** [Pinecone — RAG Evaluation](https://www.pinecone.io/learn/series/vector-databases-in-production-for-busy-engineers/rag-evaluation/), [Ragas — RAG Evaluation Framework](https://docs.ragas.io/)

---

## 10. How Would You Implement Citations/Sources in a RAG Response?

**Answer:**

"Citations serve two distinct purposes worth being explicit about: they let a user independently **verify** a claim rather than trusting the model's confident tone alone, and they give the system itself a concrete, checkable link between 'what the response said' and 'what it was actually grounded in' — directly supporting hallucination detection (AI Engineering file, question 21), since a claim that can't be traced back to a specific retrieved source is exactly the kind of thing worth flagging as unverified or fabricated.

Mechanically, the most reliable approach: tag each retrieved chunk with a stable identifier and its source metadata (document title, URL, section) *before* it's inserted into the prompt, instruct the model explicitly to reference that identifier inline when it uses information from a specific chunk, and then, in the application layer, map those inline identifiers back to the actual source metadata to render real, clickable citations in the response — rather than asking the model to freely generate citation text itself (a model asked to 'cite your sources' without a structured mechanism can fabricate a plausible-looking but incorrect citation just as readily as it can fabricate any other claim, which defeats the entire point of citations as a verification mechanism)."

**Code:**

```text
Prompt construction — each chunk tagged with a STABLE identifier
the model is instructed to reference, not asked to invent freely:

  Context:
  [1] (source: refund-policy.pdf, section 2) "Refunds are processed
      within 5-7 business days for standard orders."
  [2] (source: expedited-shipping-faq.md) "Expedited orders may
      take up to 3 additional business days for refund processing."

  Instruction: "Answer using ONLY the context above. After each
  claim, cite the source number in brackets, e.g. [1]. Do not
  state anything you cannot attribute to a specific numbered source."

  Model's response: "Standard refunds take 5-7 business days [1],
  while expedited orders may take up to 3 additional days [2]."

  Application layer: map [1] -> {title: "Refund Policy", url: "..."},
  [2] -> {title: "Expedited Shipping FAQ", url: "..."} -- rendered
  as REAL, clickable citations, built from TRUSTED metadata, not
  from anything the model generated freely
```

**Follow-up:**

I'd bring up that citation *presence* alone isn't the same as citation *correctness*, and I'd treat verifying the correspondence as its own, explicit check — a model can cite source [1] for a claim that's actually only supported by source [2], or blend information from two sources into one claim attributed to only one of them, and this specific failure mode (a plausible-looking but mismatched citation) is arguably worse than no citation at all, since it actively misleads a user who trusts the citation without independently checking it. I'd recommend the LLM-as-judge pattern (AI Engineering file, question 20) specifically adapted to check citation-claim correspondence as part of the regular evaluation suite (its question 19/22) — prompting a judge model with the claim, the cited source, and asking directly "does this specific source actually support this specific claim" — rather than assuming a model instructed to cite sources does so reliably just because the instruction was given.

**Source:** [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents), [Ragas — RAG Evaluation Framework](https://docs.ragas.io/)

---

## 11. How Would You Prevent One User From Retrieving Another User's Documents in Multi-Tenant RAG?

**Answer:**

"This is the RAG-specific instance of the Cross-Stack Design Scenarios file's tenant-isolation discipline (its question 17), applied specifically to the vector index: the tenant/user identifier has to come from a validated, server-trusted source (an authenticated JWT claim, never a client-suppliable parameter) and be embedded as **metadata on every single indexed chunk** at ingestion time, so that every retrieval query can be scoped to it via metadata filtering (question 6) — never relying on the LLM itself, or any purely application-logic check performed *after* retrieval, as the actual security boundary.

The critical discipline: the tenant filter must be applied as a genuine, mandatory pre-filter integrated into the similarity search itself (question 6), not as a check the application code merely *should* remember to add on every query path — a single code path that forgets to add the tenant filter is a genuine cross-tenant data leak, not a degraded-quality bug, so I'd treat this the same way the Spring Security file treats a missing authorization check: as something that needs a structural backstop, not just developer discipline. Where the underlying vector database or the surrounding data layer supports it, I'd add a database-level enforcement mechanism as that backstop — a dedicated collection/namespace per tenant (physical separation, the strongest guarantee, at the cost of more operational overhead managing many indexes) or row-level-security-equivalent enforcement tied to an authenticated session context, so that even a query that forgot to apply an explicit tenant filter still can't cross tenant boundaries, mirroring exactly the PostgreSQL row-level-security backstop the Cross-Stack file recommends at the database layer generally."

**Code:**

```text
Every chunk indexed with an authoritative tenant identifier:

  {
    "id": "doc-42-chunk-3",
    "embedding": [...],
    "metadata": { "tenant_id": "tenant-A", ... }
  }

Every retrieval query scoped by the AUTHENTICATED tenant, never a
client-suppliable value:

  tenant_id = get_tenant_from_validated_jwt(request)  # NEVER from
                                                          # a query param
  results = vector_db.similarity_search(
      query_vector, k=5,
      filter={"tenant_id": tenant_id}  # MANDATORY, applied to
  )                                       # EVERY query, structurally

Stronger backstop -- PHYSICAL separation, when tenant count/scale
and isolation requirements justify the operational overhead:

  vector_db.get_collection(f"tenant_{tenant_id}_documents")
  -- a query issued against the WRONG collection structurally
  -- cannot return another tenant's vectors AT ALL, regardless of
  -- whether the metadata filter was correctly applied
```

**Follow-up:**

I'd bring up that this exact isolation discipline needs to extend to the RAG pipeline's **caching layer** too, if one exists — a cached retrieval result or a cached final LLM response keyed only by query text, without also including the tenant ID in the cache key, can serve one tenant's cached answer (potentially containing or reflecting their private document content) to a different tenant who happens to ask a similarly-worded question, which is exactly the same class of bug the Redis file warns about generally but with materially worse consequences here, since the leaked content is another tenant's actual private data rather than just stale public information. I'd also mention that for genuinely high-stakes multi-tenant isolation requirements (regulated industries, enterprise contracts with explicit data-segregation clauses), I'd push for physical separation (dedicated collections, or even dedicated vector-database instances per tenant) as the default rather than the exception, specifically because a single shared index's isolation depends entirely on every single query path correctly applying a filter, forever, across every future engineer who touches that code — a guarantee that's structurally harder to violate is worth its added operational cost when the consequence of a leak is severe enough.

**Source:** [OWASP — LLM Top 10 (Sensitive Information Disclosure)](https://genai.owasp.org/llm-top-10/), [Qdrant — Multitenancy](https://qdrant.tech/documentation/guides/multiple-partitions/)

---

## 12. Compare Qdrant, Pinecone, FAISS, and pgvector — When Would You Use pgvector Instead of a Dedicated Vector Database?

**Answer:**

"These sit at genuinely different points on the build-vs-buy and operational-complexity spectrum, not just as interchangeable options with different names. **Pinecone** is a fully-managed, hosted vector database — zero infrastructure to operate, built specifically and only for vector search, with strong out-of-the-box ANN performance and metadata filtering; the trade-off is it's a proprietary hosted service (cost scales with usage, and you're dependent on their infrastructure/API). **Qdrant** is an open-source vector database, available both self-hosted and as a managed cloud offering — gives more deployment flexibility than a pure hosted-only product, with a similar feature set (HNSW-based ANN, metadata filtering, multi-tenancy support). **FAISS** (Facebook AI Similarity Search) is a *library*, not a database — it provides highly optimized ANN index implementations (including HNSW and several others) that a team embeds directly into their own application/service, with no built-in persistence, replication, metadata filtering, or multi-tenancy — genuinely fast and flexible for research or for a team willing to build the surrounding database-like infrastructure themselves, but it is not a drop-in production database.

**pgvector** is a PostgreSQL extension adding vector storage and similarity search (including both IVFFlat and HNSW indexing, question 2) directly inside an ordinary PostgreSQL database — the vectors, metadata, and any other relational data live in the *same* database, queryable together in the same SQL, with the exact same backup/replication/access-control infrastructure a team's existing PostgreSQL deployment already has. I'd reach for pgvector specifically when a team already runs PostgreSQL for its primary application data, the vector-search scale is moderate (pgvector's ANN performance is real but generally doesn't match a purpose-built vector database at very large scale or very high query throughput), and the operational simplicity of *not* standing up and operating an entirely separate database system is worth more than a dedicated vector database's typically stronger performance ceiling — a very common, pragmatic choice for a team's first RAG system, with room to migrate (question 5) to a dedicated vector database later if scale genuinely demands it."

**Code:**

```text
                Managed?   Self-host?  Metadata     Primary
                                        filtering?   use case

Pinecone        Yes only   No          Yes          Dedicated hosted
                                                     vector search
Qdrant          Yes or     Yes         Yes          Dedicated vector
                self-host                            search, flexible
                                                     deployment
FAISS           N/A        Yes         No (library  Embeddable ANN
                (library)               only, no      LIBRARY, not a
                                        DB features)  database
pgvector        Yes        Yes         Yes (via     Vector search
                (via a     (it's a      normal SQL)  ADDED TO an
                managed     Postgres                  EXISTING
                Postgres)   extension)                Postgres deployment

  -- pgvector's real advantage: vectors + relational data + metadata
  -- all live in ONE database, queryable together in ONE SQL statement,
  -- reusing infra a team likely already operates and understands
```

**Follow-up:**

I'd bring up that "pgvector doesn't scale" is often stated as a blanket fact when it's really a specific, measurable claim worth verifying against an actual workload before assuming it applies — pgvector's HNSW support (a relatively more recent addition to the extension) closed much of the raw ANN-performance gap against dedicated vector databases for many realistic workloads, and I'd benchmark pgvector directly against the actual expected query volume and corpus size before concluding a dedicated vector database is genuinely necessary, rather than reaching for one preemptively on reputation alone. I'd frame the actual decision framework as: start with pgvector if PostgreSQL is already the team's operational home and the scale is moderate-to-large-but-not-extreme; migrate to a dedicated vector database (Qdrant, Pinecone, or a similar product) once a team has *measured*, concrete evidence — a specific latency SLO pgvector can't meet at the required query volume, or a genuinely massive vector count — rather than migrating preemptively based on an assumption about where the limits are.

**Source:** [pgvector — GitHub](https://github.com/pgvector/pgvector), [Qdrant Documentation](https://qdrant.tech/documentation/), [FAISS — GitHub](https://github.com/facebookresearch/faiss)

---

## Sources & Further Reading — Consolidated

| Topic | Link |
|---|---|
| Pinecone — What Is a Vector Database? | https://www.pinecone.io/learn/vector-database/ |
| Malkov & Yashunin — HNSW | https://arxiv.org/abs/1603.09320 |
| Pinecone — HNSW | https://www.pinecone.io/learn/series/faiss/hnsw/ |
| Kusupati et al. — Matryoshka Representation Learning | https://arxiv.org/abs/2205.13147 |
| OpenAI — Embeddings Guide | https://platform.openai.com/docs/guides/embeddings |
| Hugging Face — MTEB Leaderboard | https://huggingface.co/spaces/mteb/leaderboard |
| Pinecone — RAG Evaluation | https://www.pinecone.io/learn/series/vector-databases-in-production-for-busy-engineers/rag-evaluation/ |
| Ragas — RAG Evaluation Framework | https://docs.ragas.io/ |
| LangChain — Indexing API | https://python.langchain.com/docs/how_to/indexing/ |
| Pinecone — Metadata Filtering | https://docs.pinecone.io/guides/data/filter-with-metadata |
| Qdrant — Filtering | https://qdrant.tech/documentation/concepts/filtering/ |
| Qdrant — Multitenancy | https://qdrant.tech/documentation/guides/multiple-partitions/ |
| OWASP — LLM Top 10 | https://genai.owasp.org/llm-top-10/ |
| Anthropic — Building Effective Agents | https://www.anthropic.com/research/building-effective-agents |
| pgvector — GitHub | https://github.com/pgvector/pgvector |
| Qdrant Documentation | https://qdrant.tech/documentation/ |
| FAISS — GitHub | https://github.com/facebookresearch/faiss |
