# AI Engineering — Code-Block Audit — 2026-08-25

Scope: thirteenth guide in `ROADMAP.md`'s code-block validation rollout,
and the first with Python code. This guide is explicitly the
fastest-moving in the repository (per its own header) — this pass
verifies the code's correctness and real-library API usage, not the
currency of specific model/pricing claims, which is out of scope for a
code-block audit.

## Classification summary (30 total code blocks)

- **10 `python`-tagged blocks.** All 10 pass Python syntax validation
  (`ast.parse`). Most reference undefined helper objects specific to
  their own narrow example (`vector_db`, `payment_service`,
  `pii_detector`) — correctly **partial illustrative snippet** per
  `CONTRIBUTING.md`. However, unlike most illustrative Java snippets in
  this repository, several of these are genuinely self-contained or use
  real, installable third-party libraries, and were independently
  verified against them (see below) rather than left as unverified
  prose — a first for this repository's Python content.
- **19 `text`-tagged blocks** — decision trees, pipeline/ReAct-loop
  diagrams, tool-design before/after comparisons, postmortem structure —
  correctly diagrams/checklists, not meant to execute (one, Q15's
  tool-design example, embeds a small real Python function inside an
  otherwise-illustrative JSON-schema comparison; the embedded function
  was extracted and syntax-checked independently — clean).
- **1 `yaml`-tagged block** (Q22, a GitHub Actions workflow snippet) —
  its unquoted `on:` key parses as the YAML 1.1 boolean `true` under a
  strict parser (confirmed with PyYAML) — the well-known "Norway
  problem" quirk. This is not a bug: GitHub's own Actions workflow
  parser special-cases unquoted `on:` as the literal trigger key
  regardless of generic YAML 1.1 boolean coercion, and this exact
  unquoted form is the universal, correct convention used in virtually
  every real `.github/workflows/*.yml` file. Left unchanged.

## Verification performed

- **Q2's `estimate_cost` function** — fully self-contained, executed
  directly; confirmed the exact expected cost (`$0.1575` for the
  guide's own 50K input / 500 output token example).
- **Q7's `rag_query` function** — takes its dependencies (`vector_db`,
  `embedding_model`, `llm`) as parameters rather than referencing
  undefined globals, making it genuinely testable; executed against
  mock objects and confirmed it correctly assembles retrieved context
  into the prompt and returns the LLM's response.
- **Q5's native structured-output call** — verified `model`, `tools`,
  `tool_choice`, and `messages` are all real parameters of
  `anthropic.resources.messages.Messages.create()` by inspecting the
  installed `anthropic` SDK (v1.0.0) directly.
- **Q5's fallback validation-and-retry function** — executed against a
  real Pydantic v2 model and a fake LLM that returns invalid JSON on the
  first call and valid JSON on the second; confirmed the function
  correctly catches `pydantic.ValidationError`, retries with the error
  fed back into the prompt, and returns the correctly-parsed result.
- **Q14's tool-calling response handling** — verified `stop_reason` and
  `content` are real fields on `anthropic.types.Message`, and that the
  `tool_result` content block's field names (`type`, `tool_use_id`,
  `content`) exactly match `anthropic.types.ToolResultBlockParam`.
- **Q24's prompt-caching and resilience code** — verified the
  `cache_control: {"type": "ephemeral"}` shape matches
  `anthropic.types.CacheControlEphemeralParam` exactly. Independently
  verified the `pybreaker`/`tenacity` composition by installing both
  real libraries and running two scenarios: (1) a transient failure
  followed by success — confirmed `tenacity`'s retry decorator recovers
  correctly; (2) persistent failures — confirmed `pybreaker`'s
  `CircuitBreaker` opens after `fail_max` failures and raises
  `CircuitBreakerError`, which the guide's `except` clause correctly
  catches to serve the degraded fallback response.

All verified behavior matched the guide's claims exactly.

## Bugs found

None.

## Not done in this pass

- Q15, Q16, Q19, Q20, Q22's Python blocks were syntax-checked but not
  executed — each references undefined globals specific to its own
  narrow example (`is_repeating`, `score_response`,
  `compute_correlation`, `execute_tool`) that would require fabricating
  substantial surrounding logic to run, which `CONTRIBUTING.md`
  discourages.
- No live LLM API calls were made (no API key/network use for this
  pass) — verification of the `anthropic` SDK usage was done by
  inspecting the installed SDK's real type definitions and method
  signatures directly, which confirms the code would type-check and
  send a well-formed request, not that a live API call succeeds.
- This guide's fast-moving, non-code content (specific model names,
  context-window sizes, pricing figures) was not re-verified — the
  guide's own header already flags this as the fastest-moving content in
  the repository and out of scope for a code-block-classification pass.
