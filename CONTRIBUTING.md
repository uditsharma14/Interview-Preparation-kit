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
7. **Classify every code block, and verify it accordingly.** Before adding
   or reviewing a fenced code block, decide which of these five kinds it
   is — the fence's language tag and the surrounding prose should make the
   choice unambiguous to a reader, not just to you:
   - **Compilable example** — a self-contained unit (every type it uses is
     either standard library or defined in the same block) that actually
     compiles/runs as shown. Verify this for real before submitting —
     `javac`/`java`, `python3`, or the equivalent for the language — don't
     assert it compiles from memory. If you touch an existing block in this
     category, re-verify it; don't assume it still compiles unchanged.
   - **Partial illustrative snippet** — a fragment that assumes context
     not shown (a domain type like `OrderService` or `PaymentGateway`, a
     surrounding test class, framework imports) and isn't meant to compile
     standalone. This is the right, honest category for most Example
     blocks in an interview-prep guide — it's not a lesser tier, it's the
     accurate one for a snippet that's teaching a pattern rather than
     shipping a file. **Do not invent a domain class purely to make the
     snippet compile** — a fabricated `OrderService` with a fake `process()`
     method that exists only to satisfy a compiler doesn't make the example
     more correct, it just adds invented behavior nobody asked for. If a
     block in this category couldn't practically be made self-contained,
     say so directly — a short comment or a sentence in the prose noting
     what it assumes — rather than presenting it as if it were complete.
     Even a partial snippet must still get its actual API calls,
     annotations, and method signatures right against a primary source;
     "it's just illustrative" is not an excuse for a wrong API.
   - **Pseudocode** — a diagram, flowchart, or comparison sketch (ASCII art,
     a labeled sequence, a before/after table) that isn't in any real
     programming language at all. Tag it `text` (or the closest fit) rather
     than a real language tag, since it was never meant to run.
   - **Configuration** — YAML/JSON/properties/`.feature` files and similar:
     valid as configuration syntax, not executed as a program. Verify the
     syntax and keys are real for the tool/version referenced, not
     invented-sounding.
   - **Shell command** — an actual command line (`git`, `docker`, `kubectl`,
     `curl`, a build tool invocation). Verify the flags and command shape
     are real for the tool's current version, and that it would do what the
     surrounding prose says it does.

   A block that reads like it should compile but can't be verified to
   (undefined types aside, an incorrect API, a missing import) isn't
   automatically "partial illustrative" — check whether it's actually a bug
   (fix it: correct the import, annotation, or API call) versus genuinely
   assuming external context (leave it partial, but label it as such).
   `scripts/check_code_fences.py`, wired into `docs-check.yml`, catches two
   mechanical symptoms of this policy not being followed — a fenced block
   with no language tag at all, and a block tagged `text` whose content
   nonetheless reads like real, executable syntax — but it can't tell a
   diagram that merely resembles code from an under-tagged real snippet;
   that classification call is yours.
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
  the answer up, classified per the code-example policy above.
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

InterviewSmith is dual-licensed — see [`LICENSE.md`](LICENSE.md) for the
full split. In short: the guides, glossary, and other written/educational
content are under CC BY-NC-SA 4.0 ([`LICENSE-CONTENT`](LICENSE-CONTENT));
the tooling in `scripts/` is under MIT ([`LICENSE-CODE`](LICENSE-CODE)).
**By submitting a contribution, you agree it's licensed under whichever of
those two applies to the file(s) you changed** — a new or edited guide
question under CC BY-NC-SA 4.0, a new or edited script under MIT — the same
terms every other file in that category already carries. You keep copyright
in your own contribution; you're not assigning it to the repository owner,
only licensing it under the applicable terms above, consistent with how the
rest of the repository is licensed.

If you're contributing a file that doesn't clearly fall into either
category, say so in your PR description rather than assuming — see
[`LICENSE.md`](LICENSE.md)'s note on exactly this.
