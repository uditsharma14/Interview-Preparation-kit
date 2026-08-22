#!/usr/bin/env python3
"""Detect duplicate headings within each markdown file.

Two headings in the same file that normalize to the same text (ignoring
question numbering, case, and punctuation) usually mean either a genuine
duplicate question that should be consolidated, or a copy-paste leftover.
This does NOT catch near-duplicates with different wording — that needs a
human read (see AUDIT.md's editorial-severity findings for examples already
found and fixed/tracked that way).

Exit code is non-zero if any duplicate is found, so this is CI-friendly.
"""
import re
import sys
import os

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
LEADING_NUMBER_RE = re.compile(r"^(?:q?\.?\s*)?\d+[.):]?\s*", re.IGNORECASE)
FENCE_RE = re.compile(r"^```")


def strip_code_fences(content: str) -> str:
    """Blank out fenced code-block bodies so '#'-prefixed lines inside them
    (shell comments, thread dumps, etc.) aren't mistaken for headings."""
    lines = content.split("\n")
    out = []
    in_fence = False
    for line in lines:
        if FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else line)
    return "\n".join(out)


def normalize(heading: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", heading)
    text = re.sub(r"[*_]", "", text)
    text = LEADING_NUMBER_RE.sub("", text.strip())
    text = re.sub(r"[^\w\s]", "", text).lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def main() -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    md_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirpath.split(os.sep):
            continue
        for name in filenames:
            if name.endswith(".md"):
                md_files.append(os.path.join(dirpath, name))

    any_dupes = False
    for md_file in sorted(md_files):
        with open(md_file, encoding="utf-8") as f:
            content = strip_code_fences(f.read())
        seen = {}
        dupes = []
        for match in HEADING_RE.finditer(content):
            level, text = match.group(1), match.group(2)
            key = (len(level), normalize(text))
            if not key[1]:
                continue
            if key in seen:
                dupes.append((seen[key], text))
            else:
                seen[key] = text
        if dupes:
            any_dupes = True
            rel = os.path.relpath(md_file, root)
            print(f"{rel}:")
            for original, dup in dupes:
                print(f"  duplicate heading: {dup!r} (matches {original!r})")

    if any_dupes:
        return 1
    print(f"Checked {len(md_files)} markdown files — no duplicate headings found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
