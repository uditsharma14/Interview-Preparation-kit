# Frontend & Full-Stack — New Guides (JavaScript, Angular, React) — 2026-08-24

Scope: creation and verification of three new guides — `Frontend &
Full-Stack/JavaScript_Interview_Prep.md`, `Angular_Interview_Prep.md`, and
`React_Interview_Prep.md` — 20 questions each (60 total), five-part shape
(Core answer / Staff-level extension / Example / Follow-up questions /
Sources), graduated Basic → Intermediate → Staff, matching the shape
already used by Java Collections and REST API Design.

## Version-baseline research

Before drafting, current version facts were verified against primary
sources rather than assumed from training-time knowledge, since Angular
and React are fast-moving:

- **JavaScript/ECMAScript**: confirmed ES2026 is the current finalized
  edition via a live fetch of the TC39 ECMA-262 spec page (titled for the
  next, not-yet-finalized edition, per TC39's own convention).
- **Angular**: v22 is current stable (released 2026-06-03). Signals
  (`signal()`/`computed()`/`effect()`) stable since v20. Standalone
  components became the compiler default in v19. Zoneless change
  detection stable since v20.2, default for new apps since v21. The new
  `@if`/`@for`/`@switch` control-flow syntax shipped in v17. Verified via
  a background research pass against angular.dev.
- **React**: React 19 (Dec 2024, latest minor 19.2, Oct 2025) is current;
  no React 20 announced. `useActionState` (renamed from `useFormState`),
  Actions, and `ref` as a plain prop are React 19 features. The React
  Compiler is confirmed to be a **separate, independently-versioned**
  project (not part of React's own release), reaching stable v1.0 on
  2025-10-07 — verified directly against react.dev, including its own
  blog announcement.

13 `angular.dev` URLs and all `react.dev`/MDN/other citation URLs were
checked for HTTP 200 before being cited.

## Code-block audit

**JavaScript** (19 `javascript`-tagged blocks): every block was extracted
and run with Node.js 25. All ran without unexpected errors, and every
block that produces console output was checked line-by-line against its
own inline comments — all matched. Two blocks are honestly partial rather
than self-contained: the CommonJS-vs-ESM comparison block shows two
separate files (`math.cjs`/`math.mjs`) side by side for comparison, not
one runnable script; the XSS-defense and event-delegation blocks use a
`DOMPurify` import and the `document` global respectively, both of which
require a browser/bundler context Node.js alone doesn't provide — neither
is a bug, both are appropriately illustrative for their topic. No bugs
were found or fixed. Status: **Code-tested: Yes**.

**Angular** (23 code blocks, TypeScript with `@Component`/`@Injectable`
decorators and templates) and **React** (23 code blocks, JSX): every
example was checked for correct API usage against the verified version
facts above (signal syntax, `input()`/`model()`, `@defer` syntax, Hook
signatures, `useActionState`, and similar) but **not compiled or
executed** — doing so would require a full Angular CLI project or a
React+JSX build (Babel/bundler), not a bare interpreter, which was out of
scope for this pass. These are honestly partial illustrative snippets by
the nature of component-framework code, not compilable-example claims.
Status: **Code-tested: No** for both, consistent with how other
framework-heavy guides (Spring Boot Internals, Spring Security & OAuth2,
JPA & Hibernate) are marked in `AUDIT.md`.

## Structural validation

- `scripts/check_internal_links.py`, `scripts/check_duplicate_headings.py`,
  `scripts/check_code_fences.py` — all clean across all 34 repo markdown
  files including the three new guides.
- `markdownlint-cli2` — 0 issues across all 34 files.
- `lychee` — 2 broken links found and fixed (see below); re-run confirmed
  0 errors on the three new guides (313 links checked) and 0 errors
  repo-wide (2,696 links checked).
- Each guide's Core-answer word count was measured against the five-part
  shape's 100–180 word target; 3 of 60 were initially 1–8 words over and
  were trimmed for concision without cutting content (Angular Q9, React
  Q10, React Q14). All 60 are now in range.

### Bug found and fixed: `scripts/add_toc.py` self-referential TOC entry

Running `scripts/add_toc.py` on a file that **already has** a `<!-- toc
-->` block (a TOC *refresh*, as opposed to a first-time insertion) caused
it to add a spurious self-referential "Table of Contents" TOC entry to
the regenerated TOC. Root cause: `insert_or_replace_toc()` called
`build_toc()` on the full file content *before* stripping out the
existing TOC block, so the old block's own `## Table of Contents` heading
got scanned and included as a new entry. This had never surfaced before
because every prior use of the script (Kafka, Redis, Transactions) was a
first-time insertion, not a refresh — there was no pre-existing TOC block
to be re-scanned. Fixed by stripping any existing TOC block from the
content before building the new one. Verified the fix is a true no-op
against Kafka's already-published TOC (byte-identical output) and
confirmed the three new guides' hand-written TOCs already had
byte-correct anchors once the fix was applied.

### External links: 2 broken, both fixed

- `Frontend & Full-Stack/JavaScript_Interview_Prep.md`: an MDN URL
  (`.../Guide/Object_prototypes`) 404'd; it was redundant with an
  adjacent, already-correct MDN citation
  (`.../Guide/Inheritance_and_the_prototype_chain`) covering the same
  claim, so the broken duplicate was removed rather than replaced.
- `Frontend & Full-Stack/React_Interview_Prep.md`: the React Compiler
  v1.0 announcement URL was wrong
  (`/blog/2025/10/07/introducing-react-compiler`, 404). Corrected to the
  actual URL (`/blog/2025/10/07/react-compiler-1`), confirmed 200.

## Integration

- Top-level `README.md`: added a "Frontend & Full-Stack" section to
  "Guides by topic" (previously listed as "Reserved — not yet written"),
  and updated the "Who this is for" table's Full Stack Engineer row to
  point at the new guides instead of the reserved placeholder. Updated
  the guide/question counts (17 → 20 guides, 540+ → 600+ questions,
  matching the badge and the "17 guides" prose line).
- `Frontend & Full-Stack/README.md` (a no-content placeholder stub) was
  deleted, consistent with the repo's existing convention that a
  populated topic folder (`Language/`, `Frameworks/`) has no README of
  its own — guides sit directly in the folder.
- `AUDIT.md`: added rows for JavaScript/Angular/React to the guide status
  table, updated repository-wide counts (31 → 34 files, 544 → 604
  questions, 2,245 → 2,696 external links checked), corrected the
  placeholder-stub count (three → two), and updated the "Known
  limitations" and "Open findings" sections to reflect the new guides'
  actual verification status.

## Not done in this pass

- Angular and React code blocks were not compiled/executed (see above) —
  tracked as a gap, not a defect, the same way it's tracked for the other
  framework-heavy guides.
- No independent second-pass fact-check of the Angular/React prose beyond
  the version-baseline research described above — a full line-by-line
  fact audit (the depth applied to Java Collections) has not yet been
  done for these three guides.
