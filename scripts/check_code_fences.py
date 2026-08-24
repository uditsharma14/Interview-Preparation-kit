#!/usr/bin/env python3
"""Lint fenced code blocks across every markdown guide.

Flags two things CONTRIBUTING.md's code-example policy depends on being
caught automatically, since neither is visible in a normal markdown preview:

1. A fenced code block with NO language tag at all (```` ``` ```` with nothing
   after it). Markdown renders these as plain, unhighlighted text, which
   often hides that a block is actually a real (or real-looking) shell
   command, SQL statement, or program.

2. An "ambiguous executable-looking" block: one tagged as `text`/`plain`/
   `none` (or untagged) whose content nonetheless looks like real,
   executable syntax — a shell command, SQL, or a general-purpose
   language's statements/keywords. These should either get a real language
   tag, or, if they're intentionally a diagram/table/pseudocode sketch that
   merely resembles code, are left alone — this script can't tell those
   two apart on its own, so it reports them for a human to classify per
   the five-way policy in CONTRIBUTING.md ("Verify code examples"), it
   does not fail the build on them.

Exit status: non-zero only for finding #1 (missing language), since that's
an unambiguous, mechanically-fixable defect. Finding #2 is printed as a
warning list for human triage and never fails CI on its own.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Fences that explicitly mean "not a specific executable language" —
# not flagged as "missing a language" (they're an intentional choice),
# but still eligible for the ambiguous-content heuristic below.
NON_LANGUAGE_TAGS = {"text", "plain", "plaintext", "none", ""}

# Heuristics for "this looks like real, executable code," grouped so a
# report can say *why* a block was flagged, not just that it was.
SHELL_PATTERNS = [
    r"^\s*#!/",
    r"^\s*\$\s+\S",
    r"^\s*(git|docker|kubectl|curl|npm|gradlew|mvn|python3?|java|javac)\b",
    r"&&\s*\\?$",
    r"^\s*export\s+\w+=",
]
SQL_PATTERNS = [
    r"\bSELECT\b.+\bFROM\b",
    r"\bCREATE\s+(TABLE|INDEX)\b",
    r"\bINSERT\s+INTO\b",
    r"\bUPDATE\b.+\bSET\b",
]
GENERAL_CODE_PATTERNS = [
    r"^\s*(public|private|protected|static)\s+\w",
    r"^\s*(class|interface|enum)\s+\w+\s*[{(]",
    r"^\s*def\s+\w+\(",
    r"^\s*function\s+\w+\(",
    r"^\s*import\s+[\w.]+;?\s*$",
    r"^\s*@\w+(\(.*\))?\s*$",  # a bare annotation line, e.g. @Test
    r";\s*$",  # a real statement terminator, repeated across lines is the strongest signal
]

FENCE_RE = re.compile(r"^(```+)(\S*)\s*$")


def find_markdown_files():
    return sorted(p for p in REPO_ROOT.rglob("*.md") if ".git" not in p.parts)


def extract_fences(path: Path):
    """Yield (start_line, lang, content_lines) for every fenced block."""
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        m = FENCE_RE.match(lines[i])
        if m:
            fence, lang = m.group(1), m.group(2)
            start = i + 1
            content = []
            i += 1
            while i < len(lines) and not lines[i].startswith(fence):
                content.append(lines[i])
                i += 1
            yield start, lang, content
        i += 1


def looks_executable(content_lines):
    """Return a list of reasons a block resembles real, executable code."""
    text = "\n".join(content_lines)
    reasons = []
    statement_terminators = sum(1 for l in content_lines if re.search(r";\s*(//.*)?$", l))
    for pat in SHELL_PATTERNS:
        if re.search(pat, text, re.MULTILINE):
            reasons.append("shell-command-like")
            break
    for pat in SQL_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            reasons.append("SQL-like")
            break
    for pat in GENERAL_CODE_PATTERNS:
        if pat == r";\s*$":
            continue  # handled via statement_terminators below, needs a repetition threshold
        if re.search(pat, text, re.MULTILINE):
            reasons.append("general-purpose-code-like")
            break
    if statement_terminators >= 3:
        reasons.append(f"{statement_terminators} lines end in ';' like real statements")
    return reasons


def main():
    missing_lang = []
    ambiguous = []

    for path in find_markdown_files():
        rel = path.relative_to(REPO_ROOT)
        for start, lang, content in extract_fences(path):
            if not any(l.strip() for l in content):
                continue  # empty fence, nothing to classify
            if lang == "":
                missing_lang.append((rel, start))
                continue
            if lang.lower() in NON_LANGUAGE_TAGS:
                reasons = looks_executable(content)
                if reasons:
                    ambiguous.append((rel, start, lang or "(untagged)", reasons))

    print(f"Scanned {len(find_markdown_files())} markdown files.\n")

    if missing_lang:
        print(f"MISSING LANGUAGE TAG ({len(missing_lang)}) — add one (or `text` if genuinely not code):")
        for rel, start in missing_lang:
            print(f"  {rel}:{start}")
        print()
    else:
        print("No fenced code blocks are missing a language tag.\n")

    if ambiguous:
        print(f"AMBIGUOUS EXECUTABLE-LOOKING BLOCKS ({len(ambiguous)}) — tagged `{{lang}}` but reads like real code.")
        print("Not a failure on its own: classify per CONTRIBUTING.md's code-example policy")
        print("(compilable example / partial illustrative snippet / pseudocode / configuration / shell command).")
        print("If it's genuinely a diagram or table that merely resembles code, leave it — otherwise, retag it.\n")
        for rel, start, lang, reasons in ambiguous:
            print(f"  {rel}:{start}  (tagged '{lang}') — {', '.join(reasons)}")
        print()
    else:
        print("No ambiguous executable-looking blocks found among non-language-tagged fences.\n")

    # Only a missing language tag is treated as a hard failure — it's
    # unambiguous and mechanically fixable. Ambiguous content needs a
    # human classification call and is reported, not enforced.
    return 1 if missing_lang else 0


if __name__ == "__main__":
    sys.exit(main())
