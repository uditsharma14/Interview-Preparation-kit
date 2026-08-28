# LLM Fundamentals — Interview Prep (Lead/Staff Level, with Code & Sources)

> **Target level:** Lead/Staff · **Baseline:** the Transformer architecture as introduced in Vaswani et al. 2017 and the training pipeline (pretraining → instruction tuning → RLHF) as popularized by InstructGPT; version-agnostic — these are architectural/training-methodology facts, not tied to one model release · **Last verified:** 2026-08-26 · **Prerequisites:** none beyond general software engineering; complements [AI Engineering](AI_Engineering_Interview_Prep.md), which assumes this file's mechanics and focuses on production application-building instead

How to use this: each question has **the answer the way I'd actually say it out loud** in an interview, a **code/formula snippet** you could sketch on a whiteboard to back it up, and **where the follow-up goes if you're in a Staff-level loop** — because at this level the bar is explaining *why* a mechanism exists and what breaks without it, not reciting "Transformers use attention." This file covers the model-internals and training-methodology layer; [AI Engineering](AI_Engineering_Interview_Prep.md) picks up from there and covers building production systems on top of these models (RAG, agents, evaluation, cost/latency, security) — questions on prompting vs. fine-tuning vs. RAG, context windows, and reducing latency/cost live there, not here, since they're application decisions rather than model-internals questions.

<!-- toc -->
## Table of Contents

- [1. How Does a Transformer Architecture Work, at a High Level?](#1-how-does-a-transformer-architecture-work-at-a-high-level)
- [2. What Is Self-Attention, and What Problem Does It Solve?](#2-what-is-self-attention-and-what-problem-does-it-solve)
- [3. What Are Query, Key, and Value Vectors, and How Do They Combine Into the Attention Formula?](#3-what-are-query-key-and-value-vectors-and-how-do-they-combine-into-the-attention-formula)
- [4. Why Does the Transformer Use Multi-Head Attention Instead of a Single Attention Computation?](#4-why-does-the-transformer-use-multi-head-attention-instead-of-a-single-attention-computation)
- [5. Why Are Positional Embeddings Needed, and How Do They Work?](#5-why-are-positional-embeddings-needed-and-how-do-they-work)
- [6. What Is Tokenization, and Why Don't LLMs Process Raw Characters or Words?](#6-what-is-tokenization-and-why-dont-llms-process-raw-characters-or-words)
- [7. What Is Temperature, and How Does It Affect Generation?](#7-what-is-temperature-and-how-does-it-affect-generation)
- [8. Compare Top-k and Top-p (Nucleus) Sampling](#8-compare-top-k-and-top-p-nucleus-sampling)
- [9. What Are Embeddings, and How Do They Capture Meaning?](#9-what-are-embeddings-and-how-do-they-capture-meaning)
- [10. What Is Cosine Similarity, and Why Is It the Standard Metric for Comparing Embeddings?](#10-what-is-cosine-similarity-and-why-is-it-the-standard-metric-for-comparing-embeddings)
- [11. What Is Instruction Tuning, and How Does It Differ From the Pretraining Objective?](#11-what-is-instruction-tuning-and-how-does-it-differ-from-the-pretraining-objective)
- [12. What Is RLHF, and What Problem Does It Solve That Instruction Tuning Alone Doesn't?](#12-what-is-rlhf-and-what-problem-does-it-solve-that-instruction-tuning-alone-doesnt)
- [13. What Are LoRA and PEFT, and Why Does the Industry Favor Them Over Full Fine-Tuning?](#13-what-are-lora-and-peft-and-why-does-the-industry-favor-them-over-full-fine-tuning)
- [14. What Is Quantization, and What Are the Real Trade-Offs?](#14-what-is-quantization-and-what-are-the-real-trade-offs)
- [Sources & Further Reading — Consolidated](#sources--further-reading--consolidated)

<!-- /toc -->

---

## 1. How Does a Transformer Architecture Work, at a High Level?

**Answer:**

"The Transformer (Vaswani et al., 2017) processes a sequence by stacking N repeats of two kinds of layers. A **self-attention** sub-layer lets every position directly pull in information from every other position (question 2). A **position-wise feed-forward** sub-layer then transforms each position's representation independently. Each sub-layer sits inside a residual connection followed by layer normalization — the output is `LayerNorm(x + Sublayer(x))`, not the sublayer's raw output. That's what makes it practical to stack many layers without training becoming unstable — the same residual-connection trick used in deep CNNs, just applied here.

The original paper describes an **encoder-decoder** architecture: an encoder stack processes the full input, and a decoder stack generates output autoregressively while attending back to the encoder's output. That's the shape the paper used for translation. Most of today's large language models (GPT-family, Claude, Llama) are **decoder-only** instead — one stack of decoder blocks, trained to predict the next token given everything before it. They use **masked** self-attention so a position can only attend to earlier positions, never later ones. That masking is what makes autoregressive generation — produce one token, then condition on it to produce the next — coherent at all."

**Code:**

```text
Decoder-only Transformer block (repeated N times), the shape used by
most modern LLMs:

  input embeddings + positional encoding (question 5)
         |
         v
  +-------------------------+
  | Masked Self-Attention   |  <- each position attends ONLY to itself
  | (question 2)            |     and earlier positions, never later ones
  +-------------------------+
         |
     residual add + LayerNorm
         |
         v
  +-------------------------+
  | Feed-Forward Network    |  <- applied to each position independently
  +-------------------------+
         |
     residual add + LayerNorm
         |
         v
     (repeat this block N times, then a final linear + softmax
      over the vocabulary to predict the next token)
```

**Follow-up:**

I'd point out that the residual connections are load-bearing, not a minor implementation detail. Without them, gradients have to flow back through every attention and feed-forward transformation at every one of N stacked layers, and in practice that makes very deep stacks — dozens of layers in a modern LLM — untrainable. The residual path gives gradients a direct route back to earlier layers, the same fix ResNet uses for deep CNNs, just applied to a different layer type. I'd also flag **encoder-decoder vs. decoder-only** as a common point of confusion: a decoder-only model isn't "missing" the encoder for some capability reason. It's a deliberate simplification that works because next-token prediction over a single sequence doesn't need the sequence-to-sequence structure translation originally required.

**Source:** [Vaswani et al. — Attention Is All You Need](https://arxiv.org/abs/1706.03762)

---

## 2. What Is Self-Attention, and What Problem Does It Solve?

**Answer:**

"Self-attention lets every token in a sequence directly compute a weighted combination of *every other token's* representation, with the weights set by how relevant each other token is to the current one. In 'the dog that chased the cat was tired,' this lets 'was tired' attend strongly back to 'dog,' not 'cat,' no matter how many words separate them. That's fundamentally different from how RNNs/LSTMs handled sequences. An RNN passes information forward one step at a time through a hidden state, so information from early in the sequence has to survive being compressed through every intermediate step to still be usable later. In practice, that makes long-range dependencies hard for RNNs to learn. Processing is also inherently **sequential** — step *t* can't start until step *t-1* finishes — which is slow to train since it can't be parallelized across the sequence length.

Self-attention solves both problems at once. Any two positions, no matter how far apart, connect through a single direct computation — a constant number of steps, not one that grows with sequence length. And because every position's attention computation is independent of the others, the whole thing parallelizes across the full sequence on a GPU. That parallelizability is a big part of why Transformers scale to the sizes and datasets they do, not just their capability per parameter."

**Code:**

```text
RNN — sequential, information must survive being compressed through
EVERY intermediate hidden state to reach a later position:

  token1 -> h1 -> token2 -> h2 -> token3 -> h3 -> ... -> h_n
  (step t can't start until step t-1 finishes; long-range info
   degrades the more intermediate steps it has to survive)

Self-attention — every position connects to every other position
directly, in ONE step, and all positions compute in PARALLEL:

  token1 --\
  token2 ---+--> attention(all pairs, simultaneously) --> output
  token3 --/       for EVERY position at once, not sequentially
  ...
```

**Follow-up:**

I'd point out the real cost this trades in. Self-attention's direct-connection benefit comes from computing a score between *every pair* of positions, which is O(n²) in sequence length. That's exactly why very long context windows get expensive (question 2 in the AI Engineering file covers the cost/latency consequence directly), and it's the bottleneck a whole line of research — sparse attention, linear attention, sliding-window attention — targets, trading away some of self-attention's "every position sees every other position directly" property for better scaling on long sequences. I'd frame this honestly as an active trade-off space, not a solved problem: different production models make different calls here depending on how much they prioritize long context versus raw throughput.

**Source:** [Vaswani et al. — Attention Is All You Need](https://arxiv.org/abs/1706.03762)

---

## 3. What Are Query, Key, and Value Vectors, and How Do They Combine Into the Attention Formula?

**Answer:**

"Every token's embedding gets projected, through three separate learned weight matrices, into three vectors: a **Query** (what this position is 'looking for'), a **Key** (what this position 'offers' to other positions looking for something), and a **Value** (the actual content passed along if this position gets attended to). The attention score between two positions is the dot product of one position's Query with another's Key — a high dot product means 'this Key matches what that Query is looking for.' Those scores get softmax-normalized into weights that sum to 1, then used to compute a weighted sum of every position's Value vectors.

The exact formula, from the original paper: `Attention(Q, K, V) = softmax(QKᵀ / √d_k) V`, where Q, K, and V are matrices with one row per position. The `√d_k` scaling — dividing by the square root of the Key vectors' dimension — exists because, as the paper puts it, 'for large values of d_k, the dot products grow large in magnitude, pushing the softmax function into regions where it has extremely small gradients.' Without that scaling, softmax would saturate (produce near-one-hot outputs) for high-dimensional Keys, and the resulting vanishing-gradient problem would make training unstable."

**Code:**

```text
For each token, three learned linear projections of its embedding x:
  Q = x @ W_Q       K = x @ W_K       V = x @ W_V

Attention(Q, K, V) = softmax( (Q @ Kᵀ) / sqrt(d_k) ) @ V

  Q @ Kᵀ            -- similarity score between every Query and every
                        Key (how relevant is EVERY other position to
                        THIS one)
  / sqrt(d_k)       -- scaling factor preventing the dot products from
                        growing too large and saturating softmax
  softmax( ... )    -- normalizes each row into attention WEIGHTS
                        summing to 1
  @ V               -- weighted sum of VALUE vectors, using those
                        weights -- the actual output for this position
```

**Follow-up:**

I'd point out why the Query/Key/Value split matters, instead of just comparing raw embeddings directly: it lets the model learn *different* projections for 'what I'm looking for' versus 'what I have to offer' versus 'what I'd actually contribute if attended to.' These don't have to be the same vector, and giving the model three independently-learned projections is strictly more expressive than forcing one representation to serve all three roles. I'd also mention that this same QKV mechanism, when Q comes from one sequence and K/V come from a *different* one, is called **cross-attention**. That's what the original encoder-decoder Transformer used to let the decoder attend back to the encoder's output, and it's still the mechanism behind things like an image-captioning model's text decoder attending to an image encoder's visual features.

**Source:** [Vaswani et al. — Attention Is All You Need](https://arxiv.org/abs/1706.03762)

---

## 4. Why Does the Transformer Use Multi-Head Attention Instead of a Single Attention Computation?

**Answer:**

"Rather than computing one attention pass over the full-dimensional Query/Key/Value vectors, the Transformer splits Q, K, and V into several smaller 'heads.' Each head gets its own independently-learned projections, computes attention separately, and the results get concatenated back together. The paper's own reasoning: 'multi-head attention allows the model to jointly attend to information from different representation subspaces at different positions. With a single attention head, averaging inhibits this.'

Concretely: a single attention head produces one weighted average per position. So if two different kinds of relationships matter at once — say one head's job is tracking subject-verb agreement, another's is tracking coreference to an earlier noun — a single head has to blend both signals into one averaged result. Multiple heads let the model represent several distinct relationships at once, each in its own subspace, instead of collapsing them into one averaged view."

**Code:**

```text
Single head: ONE attention computation over the full d_model dimension
  -> ONE weighted average per position -- different relevant
     relationships get blended/averaged together, losing distinction

Multi-head (h heads, each of dimension d_model/h):
  head_1 = Attention(Q@W_Q1, K@W_K1, V@W_V1)   <- may learn to track
  head_2 = Attention(Q@W_Q2, K@W_K2, V@W_V2)   <- a DIFFERENT kind of
  ...                                              relationship
  head_h = Attention(Q@W_Qh, K@W_Kh, V@W_Vh)

  MultiHead(Q,K,V) = Concat(head_1, ..., head_h) @ W_O
  -- each head's output is concatenated, then linearly projected
  -- back to d_model -- the model can represent SEVERAL distinct
  -- relationship types at once, instead of one averaged view
```

**Follow-up:**

This is a good illustration of a broader theme in deep learning architecture design: giving a model several narrower, independent 'views' of the same input, then combining them, often produces representations a single computation of the same total size can't match. That's because averaging — which is what a single head trying to serve every purpose amounts to — destroys distinctions a network could otherwise keep separate. I'd also mention that in practice, different heads in a trained Transformer are observed to specialize in different patterns — some attend mostly to the immediately preceding token, others track longer-range syntactic relationships. That's an empirical finding from interpretability research, not something explicitly designed into the architecture, but it's a useful intuition for why the mechanism helps.

**Source:** [Vaswani et al. — Attention Is All You Need](https://arxiv.org/abs/1706.03762)

---

## 5. Why Are Positional Embeddings Needed, and How Do They Work?

**Answer:**

"Self-attention, as described in question 3, is fundamentally **permutation-invariant**. The formula computes a score between every pair of positions based purely on their Query/Key/Value content — nothing in the computation encodes *where* a token sits in the sequence. Shuffling the input tokens would shuffle the output identically, with no way for the model to tell 'the cat sat on the mat' from 'the mat sat on the cat' based on attention alone. Positional information has to be injected explicitly, since nothing else in the architecture provides it — unlike an RNN, which processes tokens in order and implicitly encodes position through that sequential structure.

The original paper's approach: a fixed, deterministic **sinusoidal** positional encoding gets added directly to each token's embedding before the first layer — `PE(pos, 2i) = sin(pos / 10000^(2i/d_model))` and `PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))`, where `pos` is the token's position and `i` indexes the embedding dimension. Each dimension oscillates at a different frequency, so combining all of them gives every position a unique, fixed pattern the model can learn to use as a positional signal. Modern models have mostly moved to alternative schemes: **learned** positional embeddings (a trainable lookup table indexed by position, instead of a fixed formula), or, in many current LLMs, **rotary positional embeddings (RoPE)**, which encode relative position by rotating Query/Key vectors as a function of their distance apart rather than adding an absolute positional signal. But the underlying problem all of these solve is the same — self-attention has no inherent sense of order, and something has to supply one."

**Code:**

```text
Sinusoidal positional encoding (original paper):
  PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
  PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))

  final_input_embedding = token_embedding + PE(pos)
  -- added ONCE, before the first Transformer layer; every later
  -- layer's self-attention sees position implicitly baked into
  -- the token representations it operates on

Without ANY positional signal:
  Attention("cat", "mat", "sat") produces the SAME result regardless
  of token ORDER -- self-attention itself has no notion of sequence
  position at all, unlike an RNN's inherently sequential processing
```

**Follow-up:**

I'd point out that the choice between fixed sinusoidal, learned, and rotary (RoPE) positional schemes has real consequences for how well a model generalizes past the sequence lengths it was trained on. A fixed sinusoidal encoding is deterministic for any position, so in principle it extends to arbitrary lengths, but empirically models still degrade past their trained context length. A learned embedding table is strictly bounded to whatever maximum position it was trained with — there's simply no learned vector for a position beyond that. RoPE's relative-position framing — encoding *distance between* tokens rather than each token's absolute position — is part of why it's become the dominant choice in modern LLMs: relative position generalizes more naturally to longer sequences than an absolute signal does, which matters directly for how a model's stated context window behaves near and past its trained length.

**Source:** [Vaswani et al. — Attention Is All You Need](https://arxiv.org/abs/1706.03762)

---

## 6. What Is Tokenization, and Why Don't LLMs Process Raw Characters or Words?

**Answer:**

"Tokenization splits text into the discrete units (tokens) a model actually operates on. What counts as a 'unit' — a character, a whole word, or something in between — is a real design trade-off, not an arbitrary detail. Character-level tokenization keeps the vocabulary tiny (one entry per character) but makes every sequence very long, since a word becomes many tokens — that costs more compute per unit of actual content, per question 2's context-window/cost discussion. Whole-word tokenization keeps sequences short, but it needs an enormous vocabulary to cover every word form in every language, and it has no graceful way to represent a word it's never seen before — an unfamiliar name, a typo, a made-up term. It either needs a bloated vocabulary trying to anticipate everything, or falls back to an 'unknown token' that discards information.

**Subword tokenization** — Byte-Pair Encoding (BPE) is the most common family — is the practical middle ground almost every modern LLM uses. Common whole words get their own token, while rarer or unfamiliar words break into smaller, reusable subword pieces: 'tokenization' might become `token` + `ization`. Even a genuinely novel string is representable letter-by-letter in the worst case, since the vocabulary includes individual bytes/characters as a fallback. That gives a bounded vocabulary size, reasonably short sequences for common text, and graceful handling of anything the tokenizer hasn't seen as a whole unit."

**Code:**

```text
Character-level:  "tokenization" -> 12 tokens (t,o,k,e,n,i,z,a,t,i,o,n)
                  tiny vocabulary, but VERY long sequences

Word-level:       "tokenization" -> 1 token, IF it's in the vocabulary
                  at all -- an unseen word has NO representation
                  without a bloated vocabulary or an <UNK> fallback

Subword (BPE):    "tokenization" -> ["token", "ization"] (2 tokens)
                  -- common pieces get their own token; rare/novel
                  -- text still decomposes into SOMETHING representable,
                  -- down to individual bytes in the worst case
```

**Follow-up:**

I'd point out that tokenization efficiency varies a lot by language and content type, with real practical consequences. A BPE vocabulary trained mostly on English text tokenizes English prose efficiently — close to one token per word — but tokenizes non-English text, code, or structured data like JSON considerably less efficiently, using more tokens per unit of actual content. That inflates cost and effectively shrinks the usable context window for that content type, tying back to question 2's cost-modeling point in the AI Engineering file. I'd also mention that tokenization is an underappreciated source of surprising model behavior: a model's well-documented trouble with character-level tasks — counting letters in a word, reversing a string — traces back to the fact that it never sees individual characters once a word tokenizes into a single opaque token. The model has to work with a compressed representation that doesn't preserve character-level structure at all.

**Source:** [Sennrich et al. — Neural Machine Translation of Rare Words with Subword Units (BPE)](https://arxiv.org/abs/1508.07909), [Hugging Face — Tokenizer Summary](https://huggingface.co/docs/transformers/en/tokenizer_summary)

---

## 7. What Is Temperature, and How Does It Affect Generation?

**Answer:**

"After the model's final layer produces a raw score (a 'logit') for every possible next token, softmax converts those logits into a probability distribution. Temperature is a scaling factor applied to the logits *before* that softmax — it divides each logit by the temperature value before normalizing. At temperature 1.0, you get the model's raw, unmodified distribution. A **lower** temperature (below 1.0) sharpens the distribution: it exaggerates the gap between high- and low-probability tokens, making the model's already-preferred choices even more dominant, which gives you more deterministic, repeatable output. A temperature approaching 0 approximates always picking the single highest-probability token (greedy decoding). A **higher** temperature (above 1.0) flattens the distribution, giving lower-probability tokens a comparatively better shot at being sampled — that produces more varied, sometimes more creative, but also less reliable output.

In practice: low temperature (often 0-0.3) for tasks that need consistency and correctness — structured data extraction, code generation, factual Q&A. Higher temperature (often 0.7-1.0+) for tasks where variety is actually desirable — creative writing, brainstorming, generating diverse options. It's a task-specific tuning decision, not a universal default, and it's the same lever the AI Engineering file's hallucination-mitigation discussion (question 21 there) points to when it recommends lower temperature for factual tasks."

**Code:**

```text
softmax_with_temperature(logits, T) = softmax(logits / T)

T < 1.0  (e.g. 0.2):  sharpens the distribution -- the model's top
                        choice becomes even MORE dominant -> more
                        deterministic, focused, repeatable output

T = 1.0:               the model's raw, unmodified distribution

T > 1.0  (e.g. 1.5):  flattens the distribution -- lower-probability
                        tokens become comparatively MORE likely to be
                        sampled -> more varied, less predictable output

T -> 0:                approaches GREEDY decoding -- always pick the
                        single highest-probability token, deterministically
```

**Follow-up:**

I'd point out that temperature alone doesn't fully control output diversity in practice. It's almost always combined with top-k or top-p (question 8) as a *filtering* step applied before or alongside the temperature-scaled distribution — a high temperature on its own still leaves the full vocabulary technically samplable, including extremely unlikely, potentially incoherent tokens that just got a slightly better chance. Top-k/top-p bounds *which* tokens are eligible, while temperature reshapes *how sharply* probability is spread among the eligible ones — they're complementary controls, not alternatives. I'd also mention that temperature 0 is sometimes handled as a special case by a provider's API, since dividing by 0 is undefined — most APIs implement "temperature 0" as greedy decoding directly, rather than literally computing `logits / 0`.

**Source:** [Hugging Face — Text Generation Strategies](https://huggingface.co/docs/transformers/en/generation_strategies), [Anthropic — Messages API Reference (temperature)](https://docs.anthropic.com/en/api/messages)

---

## 8. Compare Top-k and Top-p (Nucleus) Sampling

**Answer:**

"Both are filtering strategies that restrict which tokens are eligible to be sampled *before* you actually draw from the (temperature-scaled) probability distribution. Neither replaces temperature — they answer 'which tokens are even in consideration,' while temperature answers 'how sharply is probability distributed among them.'

**Top-k** sampling restricts eligibility to a *fixed number* — the k highest-probability tokens, regardless of what the distribution actually looks like. Its weakness, as the original nucleus-sampling paper argues: a fixed k is wrong for some distributions almost by construction. For a 'peaked' distribution where the model is genuinely confident (most probability mass sits on a couple of tokens), a large k needlessly includes many low-probability, inappropriate tokens. For a 'flat' distribution where many tokens are similarly plausible, a small k can needlessly exclude reasonable options.

**Top-p (nucleus)** sampling restricts eligibility to the *smallest set of tokens whose cumulative probability reaches a threshold p* (commonly 0.9-0.95). The eligible set's *size* adapts automatically to how peaked or flat the distribution is at each step, instead of using one fixed count regardless of context. That adaptivity is exactly what makes it the generally preferred default in modern generation setups, and it's the mechanism the original paper's own framing built to fix top-k's fixed-count weakness."

**Code:**

```text
Distribution A (PEAKED — model is confident):
  token_1: 0.70   token_2: 0.15   token_3: 0.05   ... (long tail)

  top-k=5:  includes tokens 1-5, several with near-zero probability
            -- needlessly includes low-quality options
  top-p=0.9: includes ONLY tokens 1-2 (0.70+0.15=0.85, +token_3 to
             reach 0.90) -- adapts to the ACTUAL confident shape

Distribution B (FLAT — model is genuinely uncertain):
  token_1: 0.12   token_2: 0.11   token_3: 0.10   ... (many similar)

  top-k=5:  arbitrarily excludes token_6 even though it's nearly as
            plausible as token_5 -- fixed count doesn't match the shape
  top-p=0.9: includes as many tokens as ACTUALLY needed to reach 90%
             cumulative probability -- naturally wider set here
```

**Follow-up:**

I'd mention that most production APIs let you set both top-k and top-p at once, applied as sequential filters, combined with temperature as a third separate control. That's not redundant — a team might set a generous top-p as the primary adaptive filter while also capping top-k as a hard ceiling against a pathological edge case where a very flat distribution includes too many tokens. For tasks that need genuinely deterministic, repeatable output — structured extraction, evaluation-suite regression testing per the AI Engineering file's question 19/22 — the practical answer is usually temperature 0 / greedy decoding, not tuning top-k/top-p at all. These sampling strategies exist to introduce *controlled* randomness, so a task that doesn't want randomness shouldn't reach for them in the first place.

**Source:** [Holtzman et al. — The Curious Case of Neural Text Degeneration (nucleus sampling)](https://arxiv.org/abs/1904.09751), [Hugging Face — Text Generation Strategies](https://huggingface.co/docs/transformers/en/generation_strategies)

---

## 9. What Are Embeddings, and How Do They Capture Meaning?

**Answer:**

"An embedding is a fixed-length vector of real numbers that represents a piece of content — a token, a word, a sentence, a document, an image — in a way meant to capture its meaning. The property that makes embeddings useful: semantically similar content ends up with similar embeddings (nearby in vector space), while unrelated content ends up far apart, even though nothing about the raw text ('dog' vs. 'puppy') looks similar as a string.

This works because embedding models are trained specifically to place related content near each other, often through a **contrastive** training objective. The model is shown pairs of genuinely related text — a question and its correct answer, two paraphrases of the same sentence — alongside unrelated pairs, and trained to push related pairs' embeddings closer together while pushing unrelated pairs apart. The resulting embedding space isn't hand-designed — its dimensions don't map to human-interpretable concepts individually — but the *distances and directions* between embeddings end up encoding real semantic relationships. That's exactly the property RAG's retrieval step (AI Engineering file, question 7) relies on: embedding a user's query and finding the nearest document chunks by vector distance works because 'nearest in embedding space' correlates with 'semantically relevant to this query,' not because of any explicit keyword overlap."

**Code:**

```text
Token embeddings (question 1's input to the Transformer) and RAG's
document/query embeddings are the SAME underlying idea, applied at
different granularity:

  "king" - "man" + "woman" ≈ "queen"   -- the classic illustration:
  -- vector ARITHMETIC on embeddings can capture real semantic
  -- relationships, because the training objective pushed related
  -- concepts into a consistent geometric relationship, not because
  -- anyone hand-designed a "royalty" or "gender" dimension

Nearby in embedding space:            Far apart in embedding space:
  "dog"  <-->  "puppy"                  "dog"  <-->  "spreadsheet"
  "refund policy" <--> "return policy"  "refund policy" <--> "login page"
```

**Follow-up:**

I'd point out that embedding quality is task- and domain-dependent, not a universal, interchangeable property. A general-purpose embedding model trained mostly on web text can perform noticeably worse at capturing similarity within a specialized domain — legal contracts, medical terminology, a company's internal jargon — than a model fine-tuned or specifically chosen for it. That's exactly why "how do you choose an embedding model" is its own real evaluation question, not an assumption that any model works equally well for any content — the Vector Databases & RAG file covers this in depth. I'd also mention that embeddings from different models are **not directly comparable**: two different models produce vectors in entirely different, incompatible spaces, so mixing embeddings from two models in the same vector index — or comparing a query embedded with model A against documents embedded with model B — produces meaningless results, not just slightly worse ones.

**Source:** [OpenAI — Embeddings Guide](https://platform.openai.com/docs/guides/embeddings), [Reimers & Gurevych — Sentence-BERT](https://arxiv.org/abs/1908.10084)

---

## 10. What Is Cosine Similarity, and Why Is It the Standard Metric for Comparing Embeddings?

**Answer:**

"Cosine similarity measures the cosine of the angle between two vectors: `cos(θ) = (A · B) / (|A| × |B|)`, the dot product divided by the product of their magnitudes. It produces a value from -1 (exactly opposite directions) to 1 (exactly the same direction), with 0 meaning the vectors are orthogonal. Critically, it measures *direction* only — it completely ignores each vector's magnitude.

That magnitude-independence is exactly why it's the standard choice for comparing embeddings. An embedding model can produce vectors of varying magnitude for reasons that have nothing to do with semantic content — a longer piece of text accumulating more 'signal' during encoding, for instance — and a magnitude-sensitive metric like plain Euclidean distance would let that irrelevant variation distort the similarity score. Two embeddings pointing in nearly the same direction but with different lengths would get scored as less similar than they really are, purely from that length difference. Cosine similarity sidesteps this by construction, comparing only the *direction* each vector points in — which is where an embedding model's semantic training objective (question 9) actually places its meaningful signal."

**Code:**

```text
cosine_similarity(A, B) = (A · B) / (|A| × |B|)

  A · B     -- dot product: sum of element-wise products
  |A|, |B|  -- each vector's own magnitude (Euclidean length)
  dividing BY the magnitudes is what makes the result depend ONLY
  on the ANGLE between the vectors, not their length

  cos(θ) = 1   -> vectors point in the SAME direction (max similarity)
  cos(θ) = 0   -> vectors are ORTHOGONAL (unrelated)
  cos(θ) = -1  -> vectors point in OPPOSITE directions

Two embeddings with the SAME direction but DIFFERENT magnitude:
  A = [2, 2]   B = [1, 1]
  Euclidean distance: NOT zero -- looks "different"
  Cosine similarity: 1.0 -- correctly recognized as pointing the
  SAME direction, i.e. equally semantically similar
```

**Follow-up:**

I'd mention that many modern embedding models are trained (or explicitly documented) to produce **normalized** vectors — every embedding scaled to unit magnitude. For normalized vectors, cosine similarity and the dot product become mathematically equivalent, since the magnitude terms in the denominator are both 1 and drop out. That's exactly why some vector databases default to plain dot-product similarity as an optimization instead of computing the full cosine formula every time: it's cheaper (no division, no magnitude calculation), and it produces an identical ranking as long as every vector in the index is actually normalized. I'd flag this as something worth verifying explicitly for a specific embedding model and vector database pairing — assuming dot product and cosine similarity are interchangeable without confirming the vectors are normalized is a subtle correctness bug that silently produces wrong rankings for non-normalized embeddings.

**Source:** [Pinecone — Vector Similarity Explained](https://www.pinecone.io/learn/vector-similarity/)

---

## 11. What Is Instruction Tuning, and How Does It Differ From the Pretraining Objective?

**Answer:**

"A base, pretrained LLM is trained purely on **next-token prediction** over a massive corpus of raw text. Its objective is 'given this text so far, predict the most statistically likely next token,' with no explicit notion of 'follow this instruction' or 'be helpful' baked in at all. That produces a model that's good at continuing text in a way that's statistically plausible given its training data. But a base model prompted with 'Write a poem about the ocean' is just as likely to continue with *more instructions in the same style* as it is to actually write a poem — that pattern is statistically common in its training data, since instructions are often followed by more instructions in a list, not necessarily by the thing being requested.

**Instruction tuning** is a further training phase (supervised fine-tuning, or SFT) on a curated dataset of (instruction, desired-response) pairs. It specifically teaches the model the pattern 'given an instruction, produce a helpful response to it,' rather than merely 'continue this text plausibly.' This is exactly step one of the InstructGPT/RLHF pipeline (question 12). Instruction tuning alone, without the further RLHF steps, already produces a model that behaves much more like a helpful assistant than the raw base model — though it doesn't yet incorporate the more nuanced preference signal (which of several valid-looking responses humans actually prefer) that RLHF adds on top."

**Code:**

```text
Base (pretrained) model objective:
  "predict the most statistically likely next token, given
   everything before it" -- trained on raw internet-scale text,
   with NO explicit "helpfulness" or "follow instructions" signal

  Prompt: "Write a poem about the ocean."
  Base model might continue: "Write a short story about a dragon.
  Write an essay about..." -- statistically plausible CONTINUATION
  of "a list of instructions," not necessarily instruction-FOLLOWING

Instruction-tuned model:
  Trained further on curated (instruction, ideal_response) pairs:
    {"instruction": "Write a poem about the ocean.",
     "response": "Waves crash upon the sandy shore..."}
  -- explicitly teaches the PATTERN "instruction -> helpful response,"
  -- not left to emerge accidentally from raw-text continuation
```

**Follow-up:**

I'd bring up that instruction tuning's data quality matters enormously and is labor-intensive to produce well. The InstructGPT paper's own pipeline used human labelers writing high-quality demonstration responses specifically for this phase. A model instruction-tuned on a small, narrow, or low-quality dataset can pick up brittle, overly-specific patterns — always starting responses with a particular phrase, being unhelpfully verbose — rather than genuinely general instruction-following ability. The quality and diversity of this dataset is a first-order driver of how well the resulting model generalizes to instructions unlike anything in its tuning set. I'd also mention that instruction tuning and RLHF (question 12) are complementary, sequential phases, not competing techniques. A production-grade assistant model virtually always goes through both, in that order, since instruction tuning establishes the basic 'follow instructions helpfully' behavior that RLHF then further refines using human preference signal.

**Source:** [Ouyang et al. — Training Language Models to Follow Instructions with Human Feedback (InstructGPT)](https://arxiv.org/abs/2203.02155)

---

## 12. What Is RLHF, and What Problem Does It Solve That Instruction Tuning Alone Doesn't?

**Answer:**

"Reinforcement Learning from Human Feedback trains a model to prefer the *kind* of response humans actually prefer, not just to produce *a* plausible response to an instruction. Instruction tuning (question 11) teaches 'respond to this instruction helpfully,' but for any given instruction there are often many different valid-looking responses. Instruction tuning alone doesn't have a mechanism for learning *which* of several reasonable responses is actually better along dimensions like helpfulness, honesty, or harmlessness that are hard to specify as an explicit rule.

The InstructGPT paper's three-step pipeline established this approach. **Step 1 (SFT)** instruction-tunes a pretrained model on human-written demonstrations — exactly question 11. **Step 2 (reward modeling)** shows human labelers multiple model outputs for the same prompt and has them rank them by preference; a separate reward model is trained to predict which output humans would prefer, turning subjective human preference into a differentiable, learnable signal. **Step 3 (RL optimization)** further optimizes the instruction-tuned model using **PPO** (Proximal Policy Optimization), treating the reward model's score as the reward signal to maximize. A KL-divergence penalty keeps the model from drifting too far from the original instruction-tuned model, preventing it from over-optimizing against the reward model's specific quirks — a failure mode called reward hacking."

**Code:**

```text
The three-step RLHF pipeline (InstructGPT):

  STEP 1 (SFT): pretrained model + human-written demonstrations
                -> instruction-tuned model  (question 11)

  STEP 2 (Reward Model): for the same prompt, humans RANK several
                model outputs by preference (e.g. K=4 to K=9 outputs
                ranked at once) -> train a separate model to PREDICT
                that human preference as a scalar reward score

  STEP 3 (PPO): instruction-tuned model generates outputs -> reward
                model SCORES them -> PPO updates the model's weights
                to increase expected reward, with a KL PENALTY
                keeping it from drifting too far from the Step 1
                model (prevents "reward hacking" the Step 2 model's
                specific blind spots)
```

**Follow-up:**

I'd bring up **reward hacking** as the concrete failure mode that makes the KL penalty in Step 3 load-bearing, not a minor regularization detail. A reward model is itself an imperfect proxy for genuine human preference. A policy optimized aggressively enough against it, with no constraint, can learn to exploit specific quirks the reward model happens to score highly — excessive verbosity, a particular phrasing style, sycophantic agreement — without those things actually reflecting genuine human preference. The KL penalty bounds how far the policy can drift from the SFT model specifically to limit how much of this exploitation is possible. I'd also mention that RLHF is an active, evolving area. Direct preference optimization (DPO) and related methods have emerged specifically to get a similar preference-alignment effect without needing the full separate reward-model-plus-PPO machinery, trading some of RLHF's flexibility for a simpler, more stable training pipeline. It's worth knowing the name exists, even without claiming deep expertise in the trade-offs versus classic RLHF.

**Source:** [Ouyang et al. — Training Language Models to Follow Instructions with Human Feedback (InstructGPT)](https://arxiv.org/abs/2203.02155), [Schulman et al. — Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347)

---

## 13. What Are LoRA and PEFT, and Why Does the Industry Favor Them Over Full Fine-Tuning?

**Answer:**

"PEFT (Parameter-Efficient Fine-Tuning) is the general category: a family of techniques that adapt a pretrained model to a new task or dataset while updating only a small fraction of its total parameters, rather than the full model. Full fine-tuning of a modern LLM means updating every one of its often tens or hundreds of billions of parameters, which is expensive in compute, and it requires storing a full separate copy of the entire model's weights per fine-tuned variant, which is expensive in storage.

**LoRA** (Low-Rank Adaptation) is the most widely used PEFT technique. Instead of updating a pretrained weight matrix `W₀` directly, LoRA freezes `W₀` entirely and learns a much smaller update expressed as the product of two low-rank matrices, `B` and `A`, so the effective forward pass becomes `h = W₀x + BAx`. The rank `r` of these matrices is chosen to be far smaller than the original matrix's dimensions, so `B` and `A` together have vastly fewer trainable parameters than `W₀` itself. The LoRA paper reports reducing GPT-3 175B's trainable parameter count by roughly 10,000× and GPU memory requirements by 3× versus full fine-tuning, while matching or exceeding full fine-tuning's task performance in their experiments. Critically, LoRA adds **zero inference latency** compared to a fully fine-tuned model. Because `BA` can be explicitly computed and merged directly into `W₀` at deployment time, the model runs with the exact same architecture and computation as if it had been fully fine-tuned — unlike adapter-layer approaches, which add extra sequential computation at inference time."

**Code:**

```text
Full fine-tuning:
  EVERY parameter in W0 gets updated during training
  -> requires storing a FULL separate copy of the model per variant
  -> expensive compute (gradients for the whole model) and storage

LoRA:
  W0 stays FROZEN entirely -- zero gradient updates to it
  h = W0 @ x + (B @ A) @ x
       ^frozen      ^^^^^ TRAINABLE, low-rank (rank r << d, k)

  GPT-3 175B example (LoRA paper, r=4, applied to attention
  query/value projections only):
    full fine-tune checkpoint: ~350GB
    LoRA checkpoint:           ~35MB   (~10,000x smaller)

  AT DEPLOYMENT: merge B@A directly into W0 -> IDENTICAL inference
  computation to a fully fine-tuned model -- ZERO added latency,
  unlike adapter-layer approaches that add extra sequential compute
```

**Follow-up:**

I'd bring up the practical operational benefit this unlocks, which is often the actual reason a team reaches for LoRA over full fine-tuning. Because a LoRA checkpoint is tiny (megabytes, not gigabytes) and the frozen base model is shared, a single deployed base model can serve *many* different LoRA adapters simultaneously. That means swapping in a different, small adapter per customer or per task, rather than needing to load and serve a completely separate full-size model checkpoint for each variant — a meaningfully different operational and cost profile than one full fine-tune per use case. I'd also mention **QLoRA** as the natural combination worth knowing by name: applying LoRA on top of a 4-bit **quantized** (question 14) frozen base model, further reducing the memory needed to even load the base model for fine-tuning. That's what makes fine-tuning a genuinely large model feasible on a single consumer or prosumer GPU rather than requiring a multi-GPU cluster.

**Source:** [Hu et al. — LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685), [Dettmers et al. — QLoRA](https://arxiv.org/abs/2305.14314)

---

## 14. What Is Quantization, and What Are the Real Trade-Offs?

**Answer:**

"Quantization reduces the numerical precision used to store a model's weights, and sometimes its activations. A model's weights are typically stored and trained in 32-bit or 16-bit floating point (FP32, or increasingly FP16/BF16 given the scale of modern models). Quantization converts them to a lower-precision representation, commonly 8-bit or 4-bit integers (INT8, INT4), trading some numerical precision for a smaller memory footprint and, often, faster inference.

The trade-off is real, not free. Fewer bits per weight means less precision to represent the model's learned values, which can measurably degrade output quality. How much depends heavily on the specific quantization technique, how aggressively it quantizes (INT8 typically degrades less than INT4), and whether the technique is 'post-training quantization' (PTQ — quantize an already-fully-trained model, simpler but can lose more quality) or 'quantization-aware training' (QAT — the model is trained or fine-tuned with quantization effects simulated during training, generally preserving more quality at a given bit-width, at the cost of needing an actual training/fine-tuning run rather than a one-shot conversion). The benefit side is substantial and concrete: a model quantized from FP16 to INT4 needs roughly a quarter of the memory to load, which can be the difference between a model fitting on a single GPU versus requiring several. Reduced memory bandwidth requirements often translate directly into faster inference too, since moving data — not just computing on it — is a real bottleneck at these model sizes."

**Code:**

```text
Typical precision levels, in DECREASING memory footprint per weight:

  FP32 (32-bit float)  -- full precision, largest footprint, rare
                            for a model this size trained/served today
  FP16 / BF16 (16-bit) -- the common TRAINING precision for modern LLMs
  INT8  (8-bit int)    -- ~half the memory of FP16, MODEST quality loss
                            for most models with a decent quantization
                            method
  INT4  (4-bit int)    -- ~quarter the memory of FP16, MORE quality
                            loss, more sensitive to WHICH quantization
                            technique/calibration data is used

  Example: a 70B-parameter model
    FP16:  ~140GB  -- needs multiple high-end GPUs
    INT8:  ~70GB   -- may fit on fewer/smaller GPUs
    INT4:  ~35GB   -- may fit on a SINGLE consumer/prosumer GPU
```

**Follow-up:**

I'd bring up that "how much does quantization actually hurt quality" is not a question to answer from general intuition — it's workload- and technique-specific. I'd insist on running the exact same evaluation suite (AI Engineering file, question 19) against the quantized model that's used for any other model-version change, comparing scores directly against the unquantized baseline, before shipping a quantized model to production. A quantization scheme that preserves quality well on one task or domain can degrade a different task noticeably more, and "it felt fine in a few manual tries" is exactly the kind of unverified claim this entire repository pushes back on. I'd also connect this directly to the cost/latency discussion in the AI Engineering file (question 24). Quantization is one of several concrete levers for that trade-off, alongside model routing/tiering and prompt caching — specifically relevant when self-hosting (question 1 there) makes the memory/compute footprint a cost the team is directly paying for, rather than an abstraction a hosted API absorbs.

**Source:** [Hugging Face — Quantization Overview](https://huggingface.co/docs/transformers/en/quantization/overview), [Dettmers et al. — QLoRA](https://arxiv.org/abs/2305.14314)

---

## Sources & Further Reading — Consolidated

| Topic | Link |
|---|---|
| Vaswani et al. — Attention Is All You Need | https://arxiv.org/abs/1706.03762 |
| Sennrich et al. — Byte-Pair Encoding for NMT | https://arxiv.org/abs/1508.07909 |
| Hugging Face — Tokenizer Summary | https://huggingface.co/docs/transformers/en/tokenizer_summary |
| Hugging Face — Text Generation Strategies | https://huggingface.co/docs/transformers/en/generation_strategies |
| Anthropic — Messages API Reference | https://docs.anthropic.com/en/api/messages |
| Holtzman et al. — Nucleus Sampling | https://arxiv.org/abs/1904.09751 |
| OpenAI — Embeddings Guide | https://platform.openai.com/docs/guides/embeddings |
| Reimers & Gurevych — Sentence-BERT | https://arxiv.org/abs/1908.10084 |
| Pinecone — Vector Similarity Explained | https://www.pinecone.io/learn/vector-similarity/ |
| Ouyang et al. — InstructGPT (RLHF) | https://arxiv.org/abs/2203.02155 |
| Schulman et al. — Proximal Policy Optimization | https://arxiv.org/abs/1707.06347 |
| Hu et al. — LoRA | https://arxiv.org/abs/2106.09685 |
| Dettmers et al. — QLoRA | https://arxiv.org/abs/2305.14314 |
| Hugging Face — Quantization Overview | https://huggingface.co/docs/transformers/en/quantization/overview |
