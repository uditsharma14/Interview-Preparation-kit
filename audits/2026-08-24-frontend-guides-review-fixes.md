# Frontend Guides — Independent Review and Fixes — 2026-08-24

Scope: an independent, read-only strict audit of the three frontend guides
(`JavaScript_Interview_Prep.md`, `Angular_Interview_Prep.md`,
`React_Interview_Prep.md`) created earlier the same day (see
`audits/2026-08-24-frontend-guides-creation.md`), followed by fixes for
every finding the review surfaced. The review checked spoken-form
delivery, graduated structure, citation accuracy against primary sources,
version-baseline consistency, code-block classification, follow-up
quality, AI-editor artifacts, and internal-link/anchor correctness.

## Findings and fixes

| # | Severity | Location | Problem | Fix |
|---|---|---|---|---|
| 1 | Major | Angular Q1 | Stated Angular ships a new major version "roughly every six months" as a current fact. Verified directly against `angular.dev/reference/releases`: this changed to a 12-month cadence starting with **v22** — the guide's own stated baseline — so the six-month claim was already stale the moment the guide's "Last verified" date was set. | Corrected to state the current 12-month cadence, with an explicit note on the prior six-month cadence and exactly when it changed. |
| 2 | Major | JavaScript Q15 | Sources line cited an MDN anchor (`setTimeout#throttling_and_debouncing`) that does not exist on the live page (confirmed via direct fetch — no such heading id is present), with a garbled label that named "css-tricks" inside an "MDN —" prefixed link pointing only at MDN. | Split into two real, separately-linked citations: a plain MDN `setTimeout()` link (no fake anchor) and a live CSS-Tricks URL for the debounce/throttle explainer, labeled as the secondary source it actually is (debounce/throttle has no spec, so a secondary source is the correct category per `CONTRIBUTING.md`, not a workaround). |
| 3 | Major | Angular guide-wide | No question on the Angular `Router` — route configuration, guards, or resolvers — despite the guide claiming Basic→Staff coverage and Routing being one of the most commonly asked Angular interview topics. | Added a new question ("What Does the Angular Router Provide, and How Do Route Guards Work?") as Intermediate Q13, covering `provideRouter`, functional guards (`CanActivateFn`) vs. the older class-based `CanActivate`, `UrlTree` redirects, and functional resolvers (`ResolveFn`) vs. guards. Verified `CanActivateFn`'s and `ResolveFn`'s exact signatures and a working example against `angular.dev`'s own API reference pages before writing. Staff Level renumbered 13→21 to 14→21. |
| 4 | Major | React guide-wide | No question on Error Boundaries, despite it being a standard React interview topic and a genuinely interesting "hooks still have no equivalent" nuance for a Staff-level candidate. | Added a new question ("What Are Error Boundaries, and How Do You Implement One?") as Intermediate Q13, covering `getDerivedStateFromError`/`componentDidCatch`, the specific error categories boundaries do *not* catch (event handlers, async code, SSR, the boundary's own errors), the `startTransition` exception, and the `react-error-boundary` package. Verified directly against react.dev's own Error Boundary reference section, including the example code, before writing. Staff Level renumbered 13→20 to 14→21. |
| 5 | Minor | Angular Q7 Sources | Cited `https://angular.dev/guide/components/importing`, which now redirects (Angular folded the standalone-components page into the general components guide). Not a broken link — `lychee` correctly didn't flag it, since redirects aren't treated as failures — but a stale citation worth pointing at the canonical URL. | Updated both the inline Q7 citation and the consolidated sources table to `https://angular.dev/guide/components#using-components`, confirmed via `curl` to return a plain 200 with no redirect. |
| 6 | Minor | JavaScript Q14 | The memory-leak question never mentioned `WeakMap`/`WeakSet`, despite them being the standard, direct answer to "how would you cache by object identity without causing this leak" — directly adjacent to the question's own topic. | Added a sentence to the Staff-level extension plus a new follow-up question and an MDN `WeakMap` citation. |
| 7 | Minor | React guide-wide | Inconsistent import convention across examples — 19 of 20 examples used an implicit `React.X` namespace with no import statement shown, while one (`useActionState`, Q17 pre-fix) explicitly wrote `import { useActionState } from 'react';` and then called it unqualified. | Aligned the one outlier to the dominant `React.X` convention used everywhere else in the guide (`React.useActionState`), removing the stray import. |
| 8 | Minor (fold-in, not a separate question) | React Q4 | `useReducer` was named only once, in passing, inside Q19's answer, with no explanation of when to reach for it over `useState` — a commonly asked comparison. | Folded a concise `useState`-vs-`useReducer` comparison into Q4's Staff-level extension, plus a new follow-up question and a `useReducer` citation, per the original review's own suggested minimal fix (rather than adding a fourteenth-question's worth of new content for a comparison question). |

## Verification performed

- Re-ran `scripts/check_internal_links.py`, `scripts/check_duplicate_headings.py`,
  and `scripts/check_code_fences.py` across all 34 repository markdown
  files after every structural edit — clean throughout, no regressions.
- Regenerated both edited guides' Tables of Contents with
  `scripts/add_toc.py` after the renumbering, rather than hand-editing
  anchors, to guarantee GitHub-slugger-correct links for the two new
  questions and every renumbered heading.
- Re-ran `markdownlint-cli2` across all 34 files — 0 issues.
- Re-ran `lychee` against all three frontend guides (331 links, 0 errors)
  and the full repository (2,713 links, 0 errors) — confirms both fixed
  citations (Angular Q7, JavaScript Q15) and all newly added citations
  (Router/guards/resolver API references, the React Error Boundary
  reference, `react-error-boundary`, `WeakMap`, `useReducer`, CSS-Tricks)
  actually resolve.
- Re-measured every Core answer's word count across all 62 questions
  (20 JavaScript + 21 Angular + 21 React, up from 60 before this pass) —
  all fall within the guide's own 100–180 word target, including both
  new questions (148 and 159 words respectively).
- Verified the two new code examples (the Angular guard/resolver example,
  the React Error Boundary example) against the same primary-source pages
  used to write them, rather than from memory.

## Not done in this pass

- The remaining coverage gaps noted in the original review as Minor
  (Angular Pipes, JavaScript generators/iterators, React Portals) were
  intentionally left out — the review's own actionable summary prioritized
  the Major findings and did not ask for every Minor coverage note to be
  closed in the same pass.
- No new full line-by-line fact-check of the two new questions' prose
  beyond the specific API calls verified above (guard/resolver signatures,
  Error Boundary lifecycle methods) — consistent with the depth applied to
  the rest of Angular/React content in the creation pass, not a new,
  deeper standard introduced only for these two questions.
