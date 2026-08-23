# Contributing

InterviewSmith's value is its accuracy. A wrong answer memorized before a
Staff-level interview is worse than no answer — it gets confidently repeated
in the room. Everything below exists to keep that from happening.

## Before you submit anything

Read `AUDIT.md` first. It tracks the verification status of every guide and
the known-issues list InterviewSmith has already been through one full pass to
fix. If you're proposing a change to a guide marked "Verified" there, say
which finding you're addressing (or that you found a new one) so the audit
log stays accurate.

## Accuracy policy

1. **Never state a technical claim from memory when it can be verified.**
   Before adding or changing a claim about a framework, language feature, or
   protocol, check it against a primary source (see the list below) — don't
   rely on how you remember a library behaving, especially for
   version-sensitive behavior.
2. **Cite the source next to the claim it supports**, not just once at the
   bottom of the file in a way that could apply to anything. Every question
   ends with a `**Source:**` line; if you add a claim that needs one, add or
   extend that line.
3. **Prefer primary sources.** In order of preference for InterviewSmith's usual
   topics:
   - Oracle/OpenJDK specifications, Javadocs, and JEPs
   - Spring, Spring Boot, Spring Security, and Hibernate/Jakarta Persistence
     reference documentation
   - Apache Kafka documentation and KIPs
   - Redis documentation
   - Kubernetes and Docker documentation
   - IETF RFCs (HTTP semantics, OAuth2/OIDC, JWT, etc.)
   - PostgreSQL documentation
   Use credible secondary sources (Martin Fowler, microservices.io, named
   engineering blog posts, the Google SRE books) only for architectural
   opinions, named patterns, or trade-off framing that doesn't have a spec —
   never as a substitute for a primary source when one exists.
4. **State version boundaries explicitly.** If a behavior changed between
   versions (an API shape, a default, a deprecation), say which version
   introduced or changed it rather than describing it as a timeless fact.
   Every guide has a baseline declared at the top (target level / technology
   version / last-verified date / prerequisites) — keep claims consistent
   with that baseline, and update the baseline if you're documenting a newer
   version's behavior.
5. **Avoid unscoped absolutes.** "Always," "never," "guaranteed," and
   "exactly once" are almost never true without a stated scope. If you write
   one of these words, the sentence should also say under what conditions it
   holds (e.g. "within a single partition," "as long as the JVM's default
   `hashCode()` is used," "assuming `min.insync.replicas` is met").
6. **Don't invent production experience.** No fabricated incidents, metrics,
   or "I've seen this happen" stories — including in the Tech Leadership
   guide, where the temptation is strongest. If a question genuinely calls
   for a personal example, leave an explicit placeholder:
   `> Personal example to add: describe a real incident involving this
   trade-off, including context, decision, outcome, and lesson.`
   A real contributor fills it in with something that actually happened to
   them, or leaves it as a visible placeholder rather than a fabricated
   story.
7. **Verify code examples.** A code block should be one of: compilable code
   (and ideally actually compiled/run before submitting), clearly marked
   pseudocode, valid configuration, valid SQL, a decision framework, or an
   incident-investigation sequence. Don't present incomplete pseudocode as
   if it were production-ready. If you can't verify a snippet compiles,
   label it as conceptual rather than asserting it works.
8. **No AI-conversation artifacts.** This includes meta-commentary directed
   at whoever is editing the file rather than at an interview candidate —
   "let me know if you'd like me to restructure this," "happy to expand on
   X," and similar phrasing. If you're using an LLM to help draft content,
   read the output as if you were the candidate about to say it out loud,
   and remove anything addressed to an editor instead of an interviewer.

## Formatting

Follow the structure already used throughout the repo — every question
should stay internally consistent with the same shape:

- A clear question heading.
- **Answer** — the response phrased the way you'd actually say it out loud
  in an interview; long enough to be complete, short enough to say in
  roughly 30–90 seconds.
- **Code** — a snippet, config, SQL, sketch, or decision framework backing
  the answer up.
- **Follow-up** — what a Staff-level interviewer probes next: failure modes,
  trade-offs, scale, what breaks and how the design would change.
- **Source** — the authoritative reference(s) for the important claims made
  above.

Keep the **Deep dive** material inside Follow-up focused on what's
genuinely non-obvious — don't restate the Answer in more words.

## Duplicate and low-value content

Before adding a new question, check whether an existing question in this
guide (or a closely related one — Cross-Stack Design Scenarios especially
overlaps with the topic-specific guides) already covers it. Prefer
cross-referencing an existing question over re-explaining the same
mechanism twice. If you find a duplicate while reviewing, consolidate it and
note the consolidation in your commit message.

InterviewSmith is not trying to have the largest possible number of
questions. A question that doesn't help evaluate Staff-level judgment —
pure trivia, a rephrasing of an existing question, or something that
doesn't come up in real loops — is a candidate for removal, not padding.

## Commit style

Small, topic-scoped commits with a message that says what was wrong, what's
correct now, and (for a factual fix) what source verified it — see the git
log for the pattern InterviewSmith already follows, e.g.:

```text
fix(kafka): clarify idempotent-producer scope (per-partition, not single-partition-only)

Q9 previously summarized idempotence scope as 'single producer session,
single partition,' which reads as if a producer using idempotence could
only safely write to one partition. Corrected: the PID + sequence-number
dedup/ordering guarantee is tracked independently per partition...

Verified against Confluent's 'Exactly-once Semantics Is Possible'...
```

Don't bundle an unrelated content fix with a formatting/structure change —
they should be reviewable (and revertable) independently.

## Updating `AUDIT.md`

If you fix a finding that's tracked in `AUDIT.md`, mark it `**Fixed**` in
that file in the same change. If you find a new issue you're not fixing
immediately, add a row for it with `Status: Open` rather than leaving it
undocumented — an unfixed known issue is far less costly than an unknown
one.

## Licensing

InterviewSmith does not yet have a license file. Until the owner chooses
one, treat all content as "all rights reserved" by default — don't
redistribute it elsewhere or assume permissive reuse. See the README's
License section for the options recommended to the owner.
