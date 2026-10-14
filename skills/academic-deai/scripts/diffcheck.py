#!/usr/bin/env python3
"""diffcheck.py — verify that a rewrite did not alter protected content.

Usage:
  python diffcheck.py before.tex after.tex [--format md|text]

Protected content checked:
  - Numbers (integers and floats, including percentages and times)
  - LaTeX citation/reference/label keys: \\cite{…} \\ref{…} \\label{…}
  - LaTeX equations (inline $…$ and display $$…$$, equation/align envs)
  - New facts added (numbers or citation keys present in after but not before)

Exit codes:
  0 — no protected content changed
  1 — differences found (changes reported to stdout)
  2 — usage error
"""

from __future__ import annotations
import re
import sys
from collections import Counter

# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

_NUM   = re.compile(r"(?<!\w)(-?\d+(?:[.,]\d+)*(?:\s*%)?(?:\s*[smhkMGT])?)\b")
_KEY   = re.compile(r"\\(?:cite|ref|label)\{([^}]*)\}")
_MATH_INLINE  = re.compile(r"\$[^$\n]+?\$")
_MATH_DISPLAY = re.compile(r"\$\$[\s\S]+?\$\$")
_ENV   = re.compile(r"\\begin\{(equation|align\*?|math)\}[\s\S]*?\\end\{\1\}", re.M)
_COMMENT = re.compile(r"(?m)(?<!\\)%.*$")


def _strip_protected(text: str) -> str:
    """Remove content we do NOT want to diff (comments, normal prose)."""
    return _COMMENT.sub("", text)


def extract_numbers(text: str) -> Counter[str]:
    t = _strip_protected(text)
    return Counter(_NUM.findall(t))


def extract_keys(text: str) -> Counter[str]:
    return Counter(k.strip() for k in _KEY.findall(text) for k in k.split(","))


def extract_equations(text: str) -> list[str]:
    eqs: list[str] = []
    eqs += _ENV.findall(text)
    eqs += _MATH_DISPLAY.findall(text)
    eqs += _MATH_INLINE.findall(text)
    return [e.strip() for e in eqs]


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

def compare(before: str, after: str) -> list[dict]:
    issues: list[dict] = []

    # Numbers
    nb = extract_numbers(before)
    na = extract_numbers(after)
    for n, cnt in nb.items():
        if na[n] < cnt:
            issues.append({"type": "number_removed", "value": n,
                           "before": cnt, "after": na[n]})
    for n, cnt in na.items():
        if nb[n] < cnt:
            issues.append({"type": "number_added", "value": n,
                           "before": nb[n], "after": cnt})

    # Citation/reference keys
    kb = extract_keys(before)
    ka = extract_keys(after)
    for k, cnt in kb.items():
        if ka[k] < cnt:
            issues.append({"type": "key_removed", "value": k,
                           "before": cnt, "after": ka[k]})
    for k, cnt in ka.items():
        if kb[k] < cnt:
            issues.append({"type": "key_added", "value": k,
                           "before": kb[k], "after": cnt})

    # Equations: simple set membership (order-independent)
    eb = set(extract_equations(before))
    ea = set(extract_equations(after))
    for eq in eb - ea:
        issues.append({"type": "equation_removed", "value": eq[:80]})
    for eq in ea - eb:
        issues.append({"type": "equation_added", "value": eq[:80]})

    return issues


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

_SEVERITY = {
    "number_removed": "[REMOVED]",
    "number_added":   "[ADDED]",
    "key_removed":    "[REMOVED]",
    "key_added":      "[ADDED]",
    "equation_removed": "[REMOVED]",
    "equation_added":   "[ADDED]",
}

_OK     = "[OK]"
_WARN   = "[WARNING]"
_NOTE   = "[NOTE]"

_CATEGORY = {
    "number_removed": "number",
    "number_added":   "number",
    "key_removed":    "citation/ref key",
    "key_added":      "citation/ref key",
    "equation_removed": "equation",
    "equation_added":   "equation",
}


def _fmt_issue_text(issue: dict) -> str:
    t   = issue["type"]
    sev = _SEVERITY[t]
    cat = _CATEGORY[t]
    val = issue["value"]
    if "before" in issue:
        return f"  {sev} {cat}: {val!r}  (before={issue['before']}, after={issue['after']})"
    return f"  {sev} {cat}: {val!r}"


def _fmt_issue_md(issue: dict) -> str:
    t   = issue["type"]
    sev = _SEVERITY[t]
    cat = _CATEGORY[t]
    val = issue["value"]
    if "before" in issue:
        return f"| {sev} | {cat} | `{val}` | {issue['before']} → {issue['after']} |"
    return f"| {sev} | {cat} | `{val}` | — |"


def report_text(issues: list[dict], before_path: str, after_path: str) -> str:
    lines = [f"diffcheck: {before_path} -> {after_path}"]
    if not issues:
        lines.append(f"  {_OK} No protected content changed.")
        return "\n".join(lines)
    removed = [i for i in issues if "removed" in i["type"]]
    added   = [i for i in issues if "added"   in i["type"]]
    if removed:
        lines.append(f"\n  Removed from original ({len(removed)} item(s)):")
        lines += [_fmt_issue_text(i) for i in removed]
    if added:
        lines.append(f"\n  Added in rewrite ({len(added)} item(s)):")
        lines += [_fmt_issue_text(i) for i in added]
    lines.append(f"\n  {_WARN + ' Hard constraints may be violated.' if removed else _NOTE + ' New content added -- verify it came from the source.'}")
    return "\n".join(lines)


def report_md(issues: list[dict], before_path: str, after_path: str) -> str:
    lines = [f"## diffcheck: `{before_path}` -> `{after_path}`\n"]
    if not issues:
        lines.append(f"{_OK} No protected content changed.")
        return "\n".join(lines)
    lines.append("| Status | Category | Value | Count |")
    lines.append("|---|---|---|---|")
    lines += [_fmt_issue_md(i) for i in issues]
    removed = any("removed" in i["type"] for i in issues)
    lines.append("")
    lines.append(f"{_WARN} Hard constraints may be violated." if removed
                 else f"{_NOTE} New content added -- verify it came from the source.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    import argparse
    import io as _io
    import sys as _sys

    # Force UTF-8 output on Windows to avoid GBK codec errors with emoji
    if hasattr(_sys.stdout, "reconfigure"):
        _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    else:
        _sys.stdout = _io.TextIOWrapper(
            _sys.stdout.buffer, encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(
        description="Check that a rewrite left protected content unchanged.")
    ap.add_argument("before", help="Original file (.tex, .md, .txt)")
    ap.add_argument("after",  help="Rewritten file")
    ap.add_argument("--format", choices=["text", "md"], default="text")
    args = ap.parse_args(argv)

    try:
        before = open(args.before, encoding="utf-8").read()
        after  = open(args.after,  encoding="utf-8").read()
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    issues  = compare(before, after)
    printer = report_md if args.format == "md" else report_text
    print(printer(issues, args.before, args.after))
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
