#!/usr/bin/env python3
"""Mutation check for the Luna No. 7 QA gate.

Counting assertions proves nothing. This script deliberately breaks the scene
in 25 targeted ways and demands that `scripts/qa_gate.py` turns red for each
one. A mutation the gate fails to catch is reported as BROKEN and fails CI.

It also runs an unmutated control: the gate must be green on the real files.

Baseline comparison
-------------------
`--baseline` points at the historical inline gate lifted out of git history by
`scripts/extract_baseline_gate.py`. Every mutation the old gate caught must also
be caught by the new one, otherwise the run fails with
`Regression against baseline gate`.

That comparison is scoped to the mutations that target `index.html`. The
historical gate asserted Turkish README phrases; the README is English now, so
the old gate can no longer speak about it and the five README mutations are
reported as `baseline: n/a`. To keep the scene comparison meaningful the
baseline gate is handed the README from its own commit via `--baseline-readme`,
so it is judged on the contract it was written for instead of on a document that
postdates it.
"""

import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
GATE = ROOT / "scripts" / "qa_gate.py"


def drop(needle, count=1):
    def apply(text):
        if needle not in text:
            raise LookupError(f"anchor not found: {needle!r}")
        return text.replace(needle, "", count)
    return apply


def swap(needle, replacement, count=1):
    def apply(text):
        if needle not in text:
            raise LookupError(f"anchor not found: {needle!r}")
        return text.replace(needle, replacement, count)
    return apply


def inject(snippet, anchor="</body>"):
    def apply(text):
        if anchor not in text:
            raise LookupError(f"anchor not found: {anchor!r}")
        return text.replace(anchor, snippet + anchor, 1)
    return apply


# (name, target file, transform)
MUTATIONS = [
    ("html-doctype-removed", "index.html", drop("<!doctype html>\n")),
    ("html-lang-removed", "index.html", swap('<html lang="tr">', "<html>")),
    ("html-viewport-removed", "index.html", swap('name="viewport"', 'name="viewport-x"')),
    ("html-theme-color-removed", "index.html", swap('name="theme-color"', 'name="theme-colour"')),
    ("html-title-removed", "index.html", swap("<title>", "<titl3>")),
    ("dep-third-script-added", "index.html", inject('<script src="https://example.com/extra.js"></script>')),
    ("dep-script-downgraded-to-http", "index.html", swap("https://cdn.jsdelivr.net/npm/three@0.128.0/build", "http://cdn.jsdelivr.net/npm/three@0.128.0/build")),
    ("dep-second-three-version", "index.html", swap("build/three.min.js", "build/three.min.js?also=three@0.150.0/x")),
    ("dep-orbitcontrols-removed", "index.html", swap("OrbitControls.js", "TrackballControls.js")),
    ("mode-festival-renamed", "index.html", swap('data-m="festival"', 'data-m="carnival"')),
    ("mode-palette-entry-removed", "index.html", swap("festival:{sky:0x170522", "festivalX :{sky:0x170522")),
    ("a11y-reduced-motion-removed", "index.html", swap("@media(prefers-reduced-motion:reduce)", "@media(min-width:1px)")),
    ("a11y-focus-outline-removed", "index.html", swap("button:focus-visible{outline:2px solid #fff}", "button:hover{outline:2px solid #fff}")),
    ("a11y-matchmedia-removed", "index.html", swap("matchMedia('(prefers-reduced-motion:reduce)').matches", "false")),
    ("a11y-aria-label-removed", "index.html", swap('aria-label="Atmosfer modu"', 'title="Atmosfer modu"')),
    ("privacy-fetch-injected", "index.html", inject("<script>fetch('https://example.com/ping');</script>")),
    ("privacy-xhr-injected", "index.html", inject("<script>new XMLHttpRequest();</script>")),
    ("privacy-localstorage-injected", "index.html", inject("<script>localStorage.setItem('a','b');</script>")),
    ("privacy-sessionstorage-injected", "index.html", inject("<script>sessionStorage.setItem('a','b');</script>")),
    ("privacy-beacon-injected", "index.html", inject("<script>navigator.sendBeacon('/x');</script>")),
    ("readme-limits-section-removed", "README.md", swap("## Limits", "## Notes")),
    ("readme-orbitcontrols-claim-removed", "README.md", lambda t: t.replace("OrbitControls", "camera")),
    ("readme-version-claim-removed", "README.md", lambda t: t.replace("0.128.0", "latest")),
    ("readme-licence-pointer-removed", "README.md", lambda t: t.replace("LICENSE", "licence")),
    ("readme-mode-name-removed", "README.md", lambda t: t.replace("**Night**", "**Evening**")),
]

FILES = ("index.html", "README.md", "LICENSE", ".nojekyll")

# The historical gate predates the English README, so it is only asked about
# mutations of the file it can still judge.
BASELINE_TARGETS = {"index.html"}


def run_gate(workdir, gate=None):
    proc = subprocess.run(
        [sys.executable, str(gate or GATE)],
        cwd=workdir,
        capture_output=True,
        text=True,
    )
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def stage(tmp, baseline_readme=None):
    for name in FILES:
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, tmp / name)
    if baseline_readme is not None:
        shutil.copy2(baseline_readme, tmp / "README.md")


def main(argv):
    baseline = None
    baseline_readme = None
    if "--baseline" in argv:
        baseline = pathlib.Path(argv[argv.index("--baseline") + 1]).resolve()
        if not baseline.exists():
            print(f"::error title=Baseline gate missing::{baseline}")
            return 1
    if "--baseline-readme" in argv:
        baseline_readme = pathlib.Path(argv[argv.index("--baseline-readme") + 1]).resolve()
        if not baseline_readme.exists():
            print(f"::error title=Baseline README missing::{baseline_readme}")
            return 1
    if baseline is not None and baseline_readme is None:
        print("::error title=Baseline README required::--baseline needs --baseline-readme; "
              "the historical gate asserts the README of its own commit.")
        return 1

    broken = []
    errors = []
    regressions = []

    with tempfile.TemporaryDirectory() as raw:
        control = pathlib.Path(raw)
        stage(control)
        code, out = run_gate(control)
        if code != 0:
            print("CONTROL FAILED: the gate is red on the unmutated tree.")
            print(out)
            return 1
        print("control            : gate green on the real files (exit 0)")

    if baseline is not None:
        with tempfile.TemporaryDirectory() as raw:
            control = pathlib.Path(raw)
            stage(control, baseline_readme)
            bcode, bout = run_gate(control, baseline)
            if bcode != 0:
                print("CONTROL FAILED: the baseline gate is red on the unmutated tree "
                      "(index.html from HEAD, README.md from the baseline commit).")
                print(bout)
                return 1
            print("control (baseline) : baseline gate green on the real files (exit 0)")

    for name, target, transform in MUTATIONS:
        with tempfile.TemporaryDirectory() as raw:
            tmp = pathlib.Path(raw)
            stage(tmp)
            path = tmp / target
            try:
                path.write_text(transform(path.read_text(encoding="utf-8")), encoding="utf-8")
            except LookupError as exc:
                errors.append((name, str(exc)))
                print(f"{name:35s}: ANCHOR MISSING ({exc})")
                continue
            code, _ = run_gate(tmp)

        suffix = ""
        if baseline is not None:
            if target not in BASELINE_TARGETS:
                suffix = "   [baseline: n/a (README language changed)]"
            else:
                with tempfile.TemporaryDirectory() as raw:
                    btmp = pathlib.Path(raw)
                    stage(btmp, baseline_readme)
                    bpath = btmp / target
                    bpath.write_text(transform(bpath.read_text(encoding="utf-8")), encoding="utf-8")
                    bcode, _ = run_gate(btmp, baseline)
                suffix = "   [baseline: caught]" if bcode != 0 else "   [baseline: missed]"
                if bcode != 0 and code == 0:
                    regressions.append(name)

        if code == 0:
            broken.append(name)
            print(f"{name:35s}: BROKEN (gate stayed green){suffix}")
        else:
            print(f"{name:35s}: caught (exit {code}){suffix}")

    total = len(MUTATIONS)
    caught = total - len(broken) - len(errors)
    print(f"\n{caught}/{total} mutations caught by scripts/qa_gate.py")
    if baseline is not None:
        print(f"baseline gate compared: {baseline}")
        print(f"baseline README used  : {baseline_readme}")
        print("superset claim: every index.html mutation the baseline caught must also be caught here.")
        print("scope: the 5 README mutations are not compared, the historical gate asserts Turkish phrases.")

    if errors:
        for name, msg in errors:
            print(f"::error title=Mutation anchor missing::{name}: {msg}")
    if broken:
        for name in broken:
            print(f"::error title=Gate does not catch mutation::{name}")
    if regressions:
        for name in regressions:
            print(f"::error title=Regression against baseline gate::{name}")
    return 1 if (broken or errors or regressions) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
