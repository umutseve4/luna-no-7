import re, sys, pathlib

html = pathlib.Path("index.html").read_text(encoding="utf-8")
low = html.casefold()
dense = html.replace(" ", "")
failures = []

def need(condition, message):
    if not condition:
        failures.append(message)

# --- document shell -------------------------------------------------
need(low.startswith("<!doctype html>"), "index.html must start with <!doctype html>")
need('lang="tr"' in low, 'the <html> element must declare lang="tr" (the UI copy is Turkish)')
need('name="viewport"' in low, "a viewport meta tag is required for the mobile layout")
need('name="theme-color"' in low, "theme-color must stay in sync with the night background")
need("<title>" in low, "the document needs a title")

# --- dependency pinning ---------------------------------------------
srcs = re.findall(r'<script[^>]+src="([^"]+)"', html)
need(len(srcs) == 2, f"expected exactly 2 external scripts (three + OrbitControls), found {len(srcs)}: {srcs}")
need(all(s.startswith("https://") for s in srcs), f"every external script must be https, got {srcs}")
versions = sorted({v for v in re.findall(r'three@([0-9][^/]*)/', html)})
need(len(versions) == 1, f"three must be pinned to a single exact version, found {versions}")
need("OrbitControls.js" in html, "OrbitControls is required for the orbit camera")
need("http://" not in html, "no plaintext http:// references are allowed")

# --- the three atmosphere modes -------------------------------------
modes = sorted(re.findall(r'data-m="([a-z]+)"', html))
need(modes == ["day", "festival", "night"],
     f"the mode switcher must expose exactly day/night/festival, found {modes}")
for mode in ("day", "night", "festival"):
    need(mode + ":{" in dense, f'the palette table T is missing an entry for "{mode}"')

# --- accessibility ----------------------------------------------------
need("@media(prefers-reduced-motion:reduce)" in dense,
     "the stylesheet must carry an @media (prefers-reduced-motion: reduce) block")
need("matchMedia('(prefers-reduced-motion:reduce)')" in dense,
     "the scene must query prefers-reduced-motion in script and slow itself down")
need("focus-visible{outline" in dense,
     "buttons must keep a visible keyboard focus ring (a :focus-visible rule that sets outline)")
need("aria-label" in low, "the mode switcher must be labelled for screen readers")

# --- no hidden network or storage --------------------------------------
for forbidden in ("fetch(", "XMLHttpRequest", "localStorage", "sessionStorage", "sendBeacon"):
    need(forbidden not in html, f"the scene must not use {forbidden}; it is a self-contained offline page")

# --- README contract ----------------------------------------------------
# The README is English; the in-page copy stays Turkish (see the lang="tr" check
# above). These anchors are the English names of the same contract the gate
# enforces on index.html, so a README that stops describing the scene fails CI.
readme = pathlib.Path("README.md").read_text(encoding="utf-8")
rlow = readme.casefold()
expected = ["## Limits", "**Day**", "**Night**", "**Festival**", "OrbitControls"] + versions
for phrase in expected:
    need(phrase.casefold() in rlow, f'README.md must document "{phrase}"')
need("LICENSE" in readme, "README.md must point at the licence")

if failures:
    print("QA gate failed:")
    for f in failures:
        print(" -", f)
    sys.exit(1)
print(f"OK: {len(srcs)} pinned scripts, three@{versions[0]}, 3 atmosphere modes, README contract intact.")
