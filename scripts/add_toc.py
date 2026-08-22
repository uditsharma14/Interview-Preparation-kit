#!/usr/bin/env python3
"""Insert (or refresh) a Table of Contents in a guide, listing its H2
headings (each question) as links using GitHub's anchor-slug rules.

Usage: python3 scripts/add_toc.py <file.md> [<file.md> ...]

Idempotent: if a TOC block (marked by <!-- toc --> ... <!-- /toc -->) already
exists, it's replaced in place rather than duplicated, so this is safe to
re-run after editing a guide's headings.
"""
import re
import sys

HEADING_RE = re.compile(r"^(#{2,3})\s+(.*)$", re.MULTILINE)
FENCE_RE = re.compile(r"^```")
TOC_BLOCK_RE = re.compile(r"<!-- toc -->.*?<!-- /toc -->\n?", re.DOTALL)


def slugify(heading: str) -> str:
    """Match GitHub's actual heading-anchor algorithm (github-slugger):
    strip markdown emphasis, lowercase, drop anything that isn't a word
    char/space/hyphen, then convert each remaining space to a hyphen
    INDIVIDUALLY — do not collapse repeats. A punctuation character with a
    space on each side (e.g. "A & B", "A — B") leaves two adjacent spaces
    once the punctuation is stripped, which GitHub renders as a DOUBLE
    hyphen ("a--b"), not a single one."""
    text = re.sub(r"`([^`]*)`", r"\1", heading)
    text = re.sub(r"[*_]", "", text)
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = text.replace(" ", "-")
    return text


def strip_code_fences(content: str) -> str:
    lines = content.split("\n")
    out, in_fence = [], False
    for line in lines:
        if FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else line)
    return "\n".join(out)


def build_toc(content: str) -> str:
    scan_content = strip_code_fences(content)
    seen = {}
    lines = ["<!-- toc -->", "## Table of Contents", ""]
    for match in HEADING_RE.finditer(scan_content):
        level, text = len(match.group(1)), match.group(2).strip()
        base = slugify(text)
        n = seen.get(base, 0)
        slug = base if n == 0 else f"{base}-{n}"
        seen[base] = n + 1
        indent = "  " * (level - 2)
        lines.append(f"{indent}- [{text}](#{slug})")
    lines.append("")
    lines.append("<!-- /toc -->")
    return "\n".join(lines) + "\n"


def insert_or_replace_toc(content: str) -> str:
    toc = build_toc(content)
    if TOC_BLOCK_RE.search(content):
        return TOC_BLOCK_RE.sub(toc, content, count=1)
    # Insert after the intro paragraph, i.e. before the first "---" line,
    # or before the first H2 if there's no "---" separator.
    lines = content.split("\n")
    insert_at = None
    for i, line in enumerate(lines):
        if line.strip() == "---":
            insert_at = i
            break
        if line.startswith("## "):
            insert_at = i
            break
    if insert_at is None:
        insert_at = len(lines)
    new_lines = lines[:insert_at] + [toc.rstrip("\n"), ""] + lines[insert_at:]
    return "\n".join(new_lines)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: add_toc.py <file.md> [<file.md> ...]", file=sys.stderr)
        return 2
    for path in sys.argv[1:]:
        with open(path, encoding="utf-8") as f:
            content = f.read()
        updated = insert_or_replace_toc(content)
        with open(path, "w", encoding="utf-8") as f:
            f.write(updated)
        print(f"updated {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
