# AI/LLM Content Expansion — New Guides and Extensions — 2026-08-27

Scope: the user provided a large (150+ item, ~10-category) checklist of
AI/LLM interview topics — LLM fundamentals/Transformer internals, RAG,
agents/agentic AI, evaluation, prompt engineering, LLM system design,
vector databases, production/architecture, AI security, classic ML/DL
fundamentals, and project deep-dive questions — and asked for interview
questions covering it. Given the scope, the user was asked upfront to
resolve three structural decisions before writing began: depth (full
Answer/Code/Follow-up/Sources treatment for everything except ML/DL
fundamentals and project deep-dive, which got a lighter treatment),
organization (new guides for genuinely new categories, extending
AI Engineering for topics that overlap its existing questions), and
whether to include classic ML/DL fundamentals and project deep-dive
questions at all (included, both lighter-treatment).

## What was created

- **`AI Engineering/LLM_Fundamentals_Interview_Prep.md`** (new, 14
  questions) — Transformer architecture, self-attention, Query/Key/Value
  and the attention formula, multi-head attention, positional embeddings,
  tokenization, temperature, top-k/top-p sampling, embeddings, cosine
  similarity, instruction tuning, RLHF, LoRA/PEFT, and quantization.
  Every mathematical/architectural claim (the scaled dot-product
  attention formula, the sinusoidal positional-encoding formula, LoRA's
  `h = W₀x + BAx` decomposition and its 10,000x/3x reduction figures for
  GPT-3 175B, InstructGPT's exact three-step RLHF pipeline, nucleus
  sampling's cumulative-probability-mass definition) was verified
  directly against the cited primary paper (via `ar5iv.labs.arxiv.org`
  HTML mirrors, since raw arXiv PDFs don't render as extractable text)
  before being written, not stated from memory.
- **`AI Engineering/Vector_Databases_and_RAG_Interview_Prep.md`** (new,
  12 questions) — how a vector database differs from a relational one,
  ANN search and HNSW's layered-graph mechanism, embedding dimensionality
  trade-offs, choosing and migrating embedding models, metadata
  filtering, duplicate-document handling, updating/deleting embeddings,
  retrieval recall as a metric, implementing citations, multi-tenant RAG
  isolation, and comparing Qdrant/Pinecone/FAISS/pgvector. HNSW's
  layer-search mechanism and pgvector's actual supported index
  types/distance operators (confirmed via its own GitHub README, not
  assumed) were verified before writing.
- **11 new questions appended to `AI_Engineering_Interview_Prep.md`**
  (Q28-Q38, appended after the existing Q27 rather than inserted
  mid-file, since the existing 27 questions cross-reference each other
  by number 71 times — inserting mid-file would have required
  renumbering and fixing every one of those references, a much higher-risk
  edit than appending): LangGraph and graph-vs-chain orchestration, agent
  memory (short/long-term), tool-execution-failure handling, offline vs.
  online evaluation, building a golden evaluation dataset, measuring
  answer relevance and faithfulness as distinct metrics (Ragas' exact
  claim-verification and question-reconstruction methodologies verified
  against its own docs before writing), guardrails (input vs. output),
  canary rollout for a new model version, detecting production
  model-quality degradation, provider-outage handling and model fallback,
  and a "how to structure a project deep-dive" question that explicitly
  provides a framework rather than a fabricated project narrative, per
  `CONTRIBUTING.md`'s prohibition on inventing production experience —
  it ends with the standard `> Personal example to add:` placeholder.
- **`System Design/LLM_System_Design_Interview_Prep.md`** (new, 8
  scenarios, mirroring Cross-Stack Design Scenarios' format) — an
  enterprise RAG platform for multiple internal teams, an AI
  incident-response copilot, a customer-support chatbot, a scalable
  document-ingestion pipeline, supporting 1 million LLM requests/day,
  semantic caching, multi-region LLM infrastructure, and LLM application
  observability. Deliberately excludes scenarios already covered in
  depth elsewhere (PII/privacy, provider fallback, RBAC/cross-user
  isolation in RAG) — each of those cross-references the specific
  question that already owns it instead of duplicating.
- **A new "Machine Learning Fundamentals" section in
  `Computer_Science_Glossary.md`** (22 terms, lighter/glossary-style
  treatment per the user's explicit choice) — supervised/unsupervised
  learning, train/validation/test sets, overfitting/underfitting,
  bias-variance trade-off, precision/recall/F1/ROC-AUC, gradient descent,
  learning rate, backpropagation, activation functions, CNN, RNN/LSTM
  (with a `See:` pointer to LLM Fundamentals Q2 for exactly why
  Transformers superseded them), cross-entropy loss, regularization,
  batch normalization, and dropout.

## Verification performed

- Primary-source checks (via `WebFetch`/`WebSearch`, mostly against
  `ar5iv.labs.arxiv.org` HTML mirrors since raw arXiv PDF fetches don't
  extract cleanly) for: Vaswani et al. (Attention Is All You Need),
  Hu et al. (LoRA), Ouyang et al. (InstructGPT/RLHF), Holtzman et al.
  (nucleus sampling), Malkov & Yashunin (HNSW), the pgvector GitHub
  README, Ragas' faithfulness and answer-relevance metric docs, and
  LangChain's LangGraph positioning/persistence docs — before writing
  any claim attributed to them, not after.
- Every Python code block across the new/extended files was extracted
  and syntax-checked with `ast.parse`. This caught two real bugs
  introduced during writing: two code blocks (Q30 and Q37 in
  `AI_Engineering_Interview_Prep.md`, and the semantic-cache function in
  `LLM_System_Design_Interview_Prep.md`) were genuine, executable-looking
  Python mistakenly tagged `text` — reclassified to `python` per
  `CONTRIBUTING.md`'s code-classification policy — and one of them
  (Q37) had an actual syntax error (a multi-line comment missing its
  `#` continuation, plus a stray `wait_exponential(...)` literal
  ellipsis) that `ast.parse` caught directly; both were fixed and
  re-verified.
- `scripts/add_toc.py` run on all four touched/created guide files.
- `scripts/check_internal_links.py`, `scripts/check_duplicate_headings.py`,
  and `scripts/check_code_fences.py` run repository-wide after every
  significant edit; the code-fences script's remaining 5
  ambiguous-block flags are all pre-existing or already-reviewed
  narrative/comparison diagrams (see each guide's own code audit),
  not real bugs.
- `markdownlint-cli2` run repository-wide: 0 issues.
- `lychee --config .lychee.toml` run against every new/touched file
  individually (388/391 links OK; the one transient failure resolved on
  retry) and then repository-wide (3,221 checked, 3,014 OK, 6 errors —
  all the same pre-existing `microservices.io` citation, confirmed via a
  direct `curl` to be a genuine, currently-live `503` from the site
  itself, not a stale link, and unrelated to this session's additions).

## Integration

- `README.md`: added the three new guides to "Guides by topic" (System
  Design and AI Engineering sections), updated the "Four weeks" study
  path's AI Engineering step to include the new prerequisite chain,
  added three new rows to the "Difficulty by guide" table, updated the
  Computer Science Glossary's description (200 → 222 terms, mentions the
  new ML section), and updated the top-of-file summary line (21 → 24
  guides, 600+ → 650+ questions, 200-term → 222-term glossary).
- `AUDIT.md`: added guide-status rows for LLM Fundamentals, Vector
  Databases & RAG, and LLM System Design; updated AI Engineering's row
  (code-tested still `Yes`, last-reviewed date bumped); updated the
  Computer Science Glossary row's audited-term count and last-reviewed
  date; updated repository-wide counts (57 files, 666 questions, current
  lychee results); added this file to the History section.

## Not done in this pass

- The classic ML/DL fundamentals glossary entries were written from
  well-established, standard textbook definitions rather than
  individually re-verified against a primary source each — these are
  uncontested, standard facts (the F1/precision/recall formulas,
  gradient descent's definition), and the user explicitly asked for a
  lighter treatment for this specific section; flagged honestly in
  `AUDIT.md`'s guide-status row rather than claimed as fully
  source-verified.
- The project-deep-dive question deliberately does not fabricate a
  project narrative, per `CONTRIBUTING.md`'s policy — it provides a
  structuring framework and an explicit `> Personal example to add:`
  placeholder instead, consistent with how the Tech Leadership guide
  already handles this same constraint.
- No live LLM API calls, vector database, or LangGraph runtime were used
  to verify behavior — verification for this content was primary-source
  fact-checking (for claims) and syntax-checking (for code), the
  appropriate rigor level for content that's almost entirely
  conceptual/architectural rather than compilable application code (only
  3 of the ~45 new questions' code blocks are real, executable-shaped
  Python at all; the rest are diagrams, formulas, or comparison
  sketches).
