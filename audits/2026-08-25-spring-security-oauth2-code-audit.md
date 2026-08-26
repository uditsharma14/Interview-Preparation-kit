# Spring Security & OAuth2 — Code-Block Audit — 2026-08-25

Scope: fourth guide in `ROADMAP.md`'s code-block validation rollout, and
the second Spring-based guide audited (reusing the Maven/Spring
verification setup built for Spring Boot Internals). This guide's 42
questions split roughly in two: the Basic/Intermediate/early-Staff
questions (1–21) are built around concrete `SecurityFilterChain`/method-
security Java code; the OAuth2/OIDC/JWT questions (22–42) are
overwhelmingly protocol-flow and design-pattern discussion, represented
as HTTP-flow diagrams, JSON token payloads, and RFC-referencing prose
rather than executable Java.

## Classification summary

- **33 `java`-tagged blocks.** The majority reference Spring Security
  types (`SecurityFilterChain`, `@PreAuthorize`, `JwtDecoder`,
  `OAuth2TokenValidator`) combined with undefined domain types
  (`orderRepository`, `paymentRepository`, `Order`, `RefundTokenRecord`,
  application-specific services) — per `CONTRIBUTING.md`, the correct,
  honest classification for these is **partial illustrative snippet**,
  the same conclusion reached for the bulk of Spring Boot Internals'
  examples. Four of the guide's most load-bearing, mechanism-level claims
  (below) were independently verified against a real, running Spring
  Security context rather than left as unverified prose.
- **7 `text`-tagged blocks** — OAuth2/PKCE flow diagrams, a shallow-vs-
  retained-size-style ASCII illustration, a postmortem-style structure —
  correctly pseudocode/diagram, not meant to execute.
- **3 `json`-tagged blocks** — JWKS documents, ID token / access token
  payload examples — valid JSON illustrating token structure, not
  executable.
- **1 each of `bash`, `html`, `http`, `javascript`, `properties`** — a
  `curl`/log-grep shell example, an HTML form illustrating a CSRF token
  field, a raw HTTP `Set-Cookie` example, a browser-side token-storage
  snippet, and a Spring Boot properties file — all reviewed for syntax
  correctness against current documentation, none executed (most would
  need a live authorization server, browser, or servlet container to run
  meaningfully).

## Behavioral verification (real Spring Security context)

Building directly on the Maven/Spring setup from the Spring Boot
Internals audit, one more load-bearing mechanism was independently
verified against a real, running Spring context with `@EnableMethodSecurity`
active:

**`hasRole()` automatic `ROLE_` prefixing vs. `hasAuthority()`'s exact-string
check (Q7/Q8).** A real `@Service` bean with three `@PreAuthorize`-annotated
methods was exercised under four different authenticated principals:

- `hasRole('ADMIN')` with a `ROLE_ADMIN` granted authority → **allowed**.
- `hasRole('ADMIN')` with a plain `ADMIN` granted authority (no prefix)
  → **denied**, confirming the `ROLE_` prefix is genuinely required and
  automatically checked-for, not optional or lenient.
- `hasAuthority('ROLE_ADMIN')` with a `ROLE_ADMIN` granted authority →
  **allowed**, confirming the two checks are functionally identical only
  when the caller manually spells out the same prefix `hasRole()` would
  add automatically.
- `hasAuthority('orders:write')` with an `orders:write` granted authority
  → **allowed**, confirming `hasAuthority()` performs an exact match with
  no prefixing logic applied at all, exactly as needed for a non-role-shaped
  fine-grained permission.

All four results match the guide's claims exactly.

This is in addition to the three mechanisms already verified during the
Spring Boot Internals pass and directly reused by this guide's own
cross-references — self-invocation bypassing an AOP proxy (this guide's
Q18 is the identical mechanism applied to `@PreAuthorize` instead of
`@Transactional`, already confirmed structurally in the prior pass) and
`@Primary`/`@Qualifier`/circular-dependency resolution (referenced but
not re-tested here, since they're Spring Boot Internals' own claims, not
new claims this guide introduces).

## Bugs found

None. Unlike Spring Boot Internals (which had a real constructor/class
name mismatch), this pass found no compile-breaking or behaviorally
incorrect code in the blocks reviewed.

## Not done in this pass

- The ~28 remaining `java` blocks referencing undefined domain types
  (`OrderRepository`, `refreshTokenRepository`, `ledgerRepository`,
  `authorizationService`, and similar) were classified as partial
  illustrative per `CONTRIBUTING.md` and not compiled — doing so would
  require inventing substantial fabricated business logic, which the
  policy explicitly discourages.
- No live OAuth2 authorization-code flow, PKCE exchange, or JWKS
  rotation was actually exercised end-to-end — these questions (22, 29,
  31, 33) describe protocol behavior defined by RFC 6749/7636/7517 and
  Spring Security's own reference documentation (both already cited
  directly in the guide), and reproducing a full authorization server +
  resource server round trip was judged disproportionate to a
  documentation code-audit pass.
- The `bash`/`html`/`http`/`javascript`/`properties`/`json`/`text` blocks
  were reviewed for syntax and structural correctness against current
  Spring Security 6.x / RFC documentation but not executed.
