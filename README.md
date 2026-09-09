<h1 align="center">Luna No. 7</h1>

<p align="center">
  A miniature amusement park on the night shift. One file, one scene,<br>
  three atmosphere modes. It starts turning the moment you open it.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/files-1-FF4D4F?style=flat-square" alt="1 file">
  <img src="https://img.shields.io/badge/atmosphere%20modes-3-FF4D4F?style=flat-square" alt="3 modes">
  <img src="https://img.shields.io/badge/three.js-0.128.0-FF4D4F?style=flat-square" alt="three 0.128.0">
  <img src="https://img.shields.io/badge/mutation%20test-25%2F25-FF4D4F?style=flat-square" alt="25/25 mutations caught">
</p>

---

## What it does

`index.html` opens a WebGL scene that runs in the browser: a Ferris wheel, a
closed-circuit roller coaster, a carousel and three vendor stalls. The camera is
dragged and zoomed with OrbitControls; if nobody touches it for three seconds it
goes back to orbiting on its own.

| Interaction | Result |
|---|---|
| Drag | Rotates the scene horizontally and vertically (`maxPolarAngle` keeps you above the horizon) |
| Wheel / two fingers | Zoom between 14 and 34 units |
| **Day** | Blue sky, stars switched off, neon emission drops to 7% |
| **Night** | Default mode: deep blue sky, full neon, 450 stars |
| **Festival** | Purple sky, 175% neon, point lights enter a colour cycle |

Mode changes are not instant: background, fog, light intensities and tone
mapping exposure are eased toward their targets on every frame.

## How to run it

```bash
git clone https://github.com/umutseve4/luna-no-7.git
cd luna-no-7
python3 -m http.server 8000   # or just drag the file into a browser
```

There is no build step, no package manager and no configuration file.

## How it is verified

### 1. The gate: the invariants of the scene

`scripts/qa_gate.py` runs on every push and every PR and checks the contract the
scene depends on: exactly two external scripts and both over `https`, a single
pinned `three` version, `data-m` buttons covering the day/night/festival triple
together with their entries in the `T` palette table, the
`prefers-reduced-motion` block in the CSS and the `matchMedia` query in the
script checked separately, a visible keyboard focus ring, an `aria-label`, and
no use of `fetch(`, `XMLHttpRequest`, `localStorage`, `sessionStorage` or
`sendBeacon` so the page stays offline. The same step also verifies that this
README still documents the contract above.

### 2. Proof that the gate measures something

A green check does not show that the gate is looking at anything.
`scripts/mutation_check.py` deliberately breaks the scene in **25 different
ways** and requires the gate to turn red for each one. A single mutation that
stays green is reported as `BROKEN` and fails CI. There is also a control run
that verifies the gate is green on the untouched tree.

That test found two real gaps. When the reduced-motion block in the CSS was
deleted entirely, the gate stayed green because the same text also occurred in
the `matchMedia` call in the script; the two rules are now looked for
separately. Nothing is claimed about the move of the gate into a file, it is
measured: `scripts/extract_baseline_gate.py` lifts the old inline gate out of a
historical commit, the mutation run executes both side by side, and if the new
gate misses a mutation the old one caught, the workflow fails with
`Regression against baseline gate`.

The baseline comparison covers the 20 mutations that target `index.html`. The
five README mutations are compared against the current gate only, and are marked
`baseline: n/a` in the log. The reason is stated rather than hidden: the
historical gate asserted Turkish README phrases, this README is English, so the
old gate can no longer speak about it. To keep the scene comparison honest the
baseline gate is handed the README from its own commit, so it is judged on the
contract it was written for.

### 3. Publication: proof that the page really serves these bytes

The `pages` workflow publishes, then `scripts/live_bytes_proof.py` fetches the
published address, requires HTTP 200, computes the SHA-256 of the body and
compares it with the SHA-256 of the committed `index.html`. If they differ the
workflow turns red. That is what makes the sentence "deployment succeeded" mean
"that address is serving the bytes of this commit".

When the Pages setting is off, the workflow skips the publishing steps and
prints it as a warning. A green run does not mean the site is live; the
publication state is visible in the repository's Environments section.

## Limits

- **The dependency comes from a CDN.** `three` 0.128.0 and `OrbitControls` are
  loaded over jsDelivr; with no network the page stays black. The version is
  pinned, but the files are not in this repository.
- **There is no measured frame rate claim.** The pixel ratio is capped at 1.6
  and the shadow map is held at 1024x1024; those are reasonable defaults, not
  measurements. There is no benchmark in the repository.
- **`prefers-reduced-motion` slows motion down, it does not remove it.** The
  Ferris wheel, the coaster and the carousel keep turning at 18% speed, while
  the automatic camera orbit is switched off completely.
- **The colour cycle in Festival mode stops under a reduced-motion preference,**
  but the high neon brightness stays.
- **The mutation test measures the gate, not the scene.** The 25/25 result says
  the listed breakages are caught; a form of breakage nobody tested is always
  possible. Visual correctness and frame rate still need a human to look.
- **The scene is modelled entirely by hand and represents no real park.**
  Dimensions, names and layout are invented.
- **The in-page copy is Turkish on purpose.** The document declares `lang="tr"`
  and the gate asserts it; this README is the English entry point.
- **This repository is the small precursor of `neon-lunapark-webgl`.** The
  larger, more detailed scene lives there; this file was kept deliberately
  plain.

---

MIT, see [`LICENSE`](./LICENSE).
