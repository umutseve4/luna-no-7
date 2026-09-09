#!/usr/bin/env python3
"""Lift the old inline QA gate out of git history.

Before this change the gate lived as a `python3 - <<'PY' ... PY` heredoc inside
`.github/workflows/qa.yml`. `scripts/qa_gate.py` replaced it. To prove the move
lost nothing, CI extracts the historical heredoc with this script and hands it
to `scripts/mutation_check.py --baseline`, which requires the new gate to catch
every mutation the old one caught.

Usage: extract_baseline_gate.py <commit-ish> <output-path>
"""

import pathlib
import subprocess
import sys

START = "python3 - <<'PY'"
END = "PY"


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    commit, out = argv
    blob = subprocess.run(
        ["git", "show", f"{commit}:.github/workflows/qa.yml"],
        check=True, capture_output=True, text=True,
    ).stdout

    lines = blob.splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == START)
    except StopIteration:
        print(f"::error title=Baseline heredoc not found::no {START!r} in {commit}:.github/workflows/qa.yml")
        return 1

    body = []
    for line in lines[start + 1:]:
        if line.strip() == END:
            break
        body.append(line)
    else:
        print("::error title=Baseline heredoc unterminated::no closing PY marker")
        return 1

    indents = [len(l) - len(l.lstrip()) for l in body if l.strip()]
    pad = min(indents) if indents else 0
    source = "\n".join(l[pad:] if l.strip() else "" for l in body) + "\n"

    compile(source, "baseline_gate.py", "exec")  # must be valid Python
    pathlib.Path(out).write_text(source, encoding="utf-8")
    print(f"baseline gate extracted from {commit}: {len(body)} lines -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
