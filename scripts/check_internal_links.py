#!/usr/bin/env python3
"""Validate internal markdown links (relative file paths and same-file anchors).

Checks every `[text](target)` link in every .md file in the repo:
  - relative file links resolve to a real file on disk
  - `#anchor` fragments (on a relative link or a same-file link) resolve to
    a heading in the target file, using GitHub's heading-to-anchor slug rules

External links (http/https) and mailto: links are skipped — see
check_external_links workflow step (lychee) for those.

Exit code is non-zero if any link is broken, so this is CI-friendly.
"""
import re
import sys
import os
import urllib.parse

LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
FENCE_RE = re.compile(r"^```")


def strip_code_fences(content: str) -> str:
    """Blank out fenced code-block bodies so example markdown/URLs inside
    them aren't mistaken for real links."""
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


def slugify(heading: str) -> str:
    """GitHub's markdown heading-to-anchor algorithm (github-slugger): strip
    emphasis, lowercase, drop non-word/space/hyphen chars, then convert each
    remaining space to a hyphen INDIVIDUALLY (no collapsing) — a punctuation
    character stripped from between two spaces (e.g. "A & B" -> "A  B")
    must become a double hyphen ("a--b"), not a single one."""
    text = re.sub(r"`([^`]*)`", r"\1", heading)  # strip inline code backticks
    text = re.sub(r"[*_]", "", text)  # strip bold/italic markers
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)  # drop punctuation
    text = text.replace(" ", "-")
    return text


def anchors_for(path: str) -> set:
    if not os.path.isfile(path):
        return set()
    with open(path, encoding="utf-8") as f:
        content = strip_code_fences(f.read())
    slugs = set()
    seen = {}
    for match in HEADING_RE.finditer(content):
        base = slugify(match.group(2))
        n = seen.get(base, 0)
        slug = base if n == 0 else f"{base}-{n}"
        seen[base] = n + 1
        slugs.add(slug)
    return slugs


def main() -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    md_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirpath.split(os.sep):
            continue
        for name in filenames:
            if name.endswith(".md"):
                md_files.append(os.path.join(dirpath, name))

    broken = []
    for md_file in md_files:
        with open(md_file, encoding="utf-8") as f:
            content = strip_code_fences(f.read())
        base_dir = os.path.dirname(md_file)
        for match in LINK_RE.finditer(content):
            target = match.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            file_part, _, anchor = target.partition("#")
            file_part = urllib.parse.unquote(file_part)
            if file_part == "":
                resolved = md_file  # same-file anchor
            else:
                resolved = os.path.normpath(os.path.join(base_dir, file_part))
            if not os.path.exists(resolved):
                broken.append((md_file, target, "target path does not exist"))
                continue
            if anchor and os.path.isfile(resolved):
                anchor_slug = urllib.parse.unquote(anchor).lower()
                if anchor_slug not in anchors_for(resolved):
                    broken.append(
                        (md_file, target, f"no heading resolves to anchor #{anchor}")
                    )

    if broken:
        print(f"Found {len(broken)} broken internal link(s):\n")
        for source, target, reason in broken:
            rel = os.path.relpath(source, root)
            print(f"  {rel}: [{target}] — {reason}")
        return 1

    print(f"Checked {len(md_files)} markdown files — all internal links resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
