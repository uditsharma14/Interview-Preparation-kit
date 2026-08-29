# Next.js — New Guide Creation — 2026-08-29

Scope: the user asked for a Next.js interview guide covering routing,
SSR/SSG, API routes, server components, and deployment, explicitly
pitched at an intermediate level rather than this repository's usual
Staff depth. No structural clarifying questions were asked given the
well-defined, modest scope.

## What was created

- **`Frontend & Full-Stack/NextJS_Interview_Prep.md`** (new,
  intermediate level, 12 questions) — what Next.js adds on top of
  React; file-based routing in the App Router; App Router vs. Pages
  Router; dynamic segments (`[slug]`, `[...slug]`, `[[...slug]]`);
  layouts vs. pages; SSR vs. SSG vs. ISR; Server Components vs. Client
  Components; `'use client'` and its module-boundary effect; Route
  Handlers; data fetching/caching (`fetch` options, `revalidatePath`/
  `revalidateTag`, `unstable_cache`); Middleware; and deployment options
  (Node server, Docker, static export, Vercel). Uses the simpler
  Answer/Code/Follow-up/Source structure (matching AI Engineering)
  rather than the heavier five-part Staff structure used by React/
  Angular, to match the requested intermediate depth.

## Verification performed

- Every claim checked against live nextjs.org docs via `WebFetch`
  before writing (routing/layouts-and-pages, server-and-client-
  components, Route Handlers, incremental-static-regeneration,
  deploying), plus a targeted `WebSearch` to confirm the `page.tsx`/
  `route.ts` same-segment exclusivity rule.
- The guide explicitly flags the Next.js 15 version boundary: `params`
  and `searchParams` became `Promise`s requiring `await`, versus the
  synchronous objects of Next.js 13/14 — called out in the intro
  paragraph since a lot of existing tutorials/code still show the older
  form.
- `scripts/add_toc.py` run on the new file — the manually-written TOC
  matched the script's generated anchors exactly, no diff.
- `scripts/check_internal_links.py`, `scripts/check_duplicate_headings.py`,
  and `scripts/check_code_fences.py` run repository-wide — 60 files
  checked, 0 broken links, 0 duplicate headings, 0 missing language
  tags. One block (the Pages-Router-vs-App-Router comparison, tagged
  `text`) was flagged as ambiguous/executable-looking by the fences
  script; left as `text` since it deliberately mixes prose-style
  annotations with code and isn't meant to compile on its own,
  consistent with how similar comparison blocks are already tagged
  elsewhere in the repo.
- `markdownlint-cli2` run against the new file — 0 issues.
- `lychee --config .lychee.toml` run against this file together with
  `Language/OOP_Concepts_Interview_Prep.md` (96 links total, 61
  unique) — 0 errors. A subsequent repository-wide `lychee` run (3,317
  checked, 3,116 OK, 0 errors, 201 excluded) also incidentally found
  that the previously-flagged `microservices.io` `503` (see AUDIT.md's
  prior "Open findings") has resolved on its own.

## Code-testing scope (consistent with Angular/React)

- No Node/npm/bundler toolchain is set up in this environment, so the
  TypeScript/JSX/bash code blocks were not compiled or executed. This
  matches the repository's existing, documented treatment of Angular
  and React: framework-dependent snippets checked for correct API usage
  against the primary docs, not run. See AUDIT.md's "Known limitations"
  section, now updated to include Next.js alongside Angular and React.

## Integration

- `README.md`: added a Next.js bullet to "Guides by topic" → Frontend &
  Full-Stack, a row to "Difficulty by guide" (Intermediate), and
  updated the top-of-file guide/question/glossary counts and badges.
- `AUDIT.md`: added a Next.js guide-status row, updated the Angular/
  React TS-JSX code-testing note to include Next.js, and updated
  repository-wide counts (62 files, 695 questions, refreshed `lychee`
  results).
- This pass also backfilled the OOP Concepts guide's own README/AUDIT
  integration, which had been left incomplete since its creation — see
  `audits/2026-08-27-oop-concepts-creation.md`.
