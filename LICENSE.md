# License

InterviewSmith is dual-licensed — different parts of this repository are
licensed differently, on purpose. **The repository is not entirely
MIT-licensed.** Read this file before reusing anything from here.

## What's licensed how

| Content | License | Full text |
|---|---|---|
| Interview-preparation prose, the Markdown guides (every `*_Interview_Prep.md` file), the glossary, diagrams, and other educational/written content in this repository | **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)** | [`LICENSE-CONTENT`](LICENSE-CONTENT) |
| Repository tooling and original scripts under [`scripts/`](scripts/) (`check_internal_links.py`, `check_duplicate_headings.py`, `check_code_fences.py`, `add_toc.py`, and any other script added there) | **MIT License** | [`LICENSE-CODE`](LICENSE-CODE) |

SPDX identifiers, for tooling that reads them: `CC-BY-NC-SA-4.0` for the
content described above, `MIT` for `scripts/`.

If a future file doesn't obviously fall into either category above, ask the
repository owner rather than assuming — don't infer a license from a file's
location alone.

## What CC BY-NC-SA 4.0 means for the guides, in short

This is a summary for convenience, not a substitute for the full text in
[`LICENSE-CONTENT`](LICENSE-CONTENT) (or the official deed at
[creativecommons.org/licenses/by-nc-sa/4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)),
which governs if this summary and the license disagree:

- **Attribution** — if you share or adapt the guides, credit InterviewSmith
  and link back to this repository.
- **NonCommercial** — you may not use the guides for commercial purposes
  (for example, repackaging them into a paid course or bootcamp) without the
  copyright holder's separate permission.
- **ShareAlike** — if you remix, transform, or build on the guides, you must
  distribute your contribution under the same CC BY-NC-SA 4.0 license.

## What MIT means for `scripts/`, in short

The scripts exist to check the guides' own structure (internal links,
duplicate headings, code-fence hygiene, table-of-contents generation) and
are licensed permissively so they're straightforwardly reusable in other
projects with attribution, per the terms in [`LICENSE-CODE`](LICENSE-CODE).

## Copyright

Copyright (c) 2026 uditsharma14, the original author and current maintainer
of InterviewSmith. This licensing decision does not change or reassign
copyright already held by any other contributor to this repository — a
contributor retains copyright in their own contribution; see
[`CONTRIBUTING.md`](CONTRIBUTING.md) for the terms new contributions are
accepted under.

## Why two licenses instead of one

The content (interview answers, explanations, the actual educational value
of this repository) and the tooling (link/heading/code-fence checkers) are
different kinds of work with different reuse expectations. CC BY-NC-SA 4.0
keeps the guides attributed, non-commercial, and share-alike — reusable for
personal study and derivative study guides, not resellable as-is or
folded into paid material without permission. MIT keeps the scripts
freely reusable, including commercially, the way small utility scripts
conventionally are, since gatekeeping reuse of a link checker doesn't serve
any purpose the content license is protecting.
