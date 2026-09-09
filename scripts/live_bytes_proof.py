#!/usr/bin/env python3
"""Prove the deployed URL serves exactly the committed bytes.

A green `deploy` job only says GitHub accepted an artifact. This script fetches
the live page, hashes the response body with SHA-256 and compares it with the
SHA-256 of the file in the repository. Mismatch, non-200 or timeout fails CI.

Usage: live_bytes_proof.py <url> <local-file> [attempts]
"""

import hashlib
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request


def summary(line):
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    print(line)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    url = argv[0].rstrip("/") + "/"
    local = pathlib.Path(argv[1])
    attempts = int(argv[2]) if len(argv) > 2 else 12

    want_bytes = local.read_bytes()
    want = hashlib.sha256(want_bytes).hexdigest()

    last = "no attempt made"
    for i in range(1, attempts + 1):
        try:
            request = urllib.request.Request(url, headers={"Cache-Control": "no-cache"})
            with urllib.request.urlopen(request, timeout=20) as response:
                status = response.status
                body = response.read()
            if status != 200:
                last = f"HTTP {status}"
            else:
                got = hashlib.sha256(body).hexdigest()
                if got == want:
                    summary("### Live bytes proof: PASS")
                    summary("")
                    summary(f"- URL: `{url}`")
                    summary(f"- attempt: {i}/{attempts}")
                    summary(f"- bytes served: {len(body)} (local: {len(want_bytes)})")
                    summary(f"- SHA-256: `{got}`")
                    return 0
                last = f"SHA-256 mismatch: live {got} ({len(body)} bytes) vs repo {want} ({len(want_bytes)} bytes)"
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last = f"{type(exc).__name__}: {exc}"
        print(f"attempt {i}/{attempts}: {last}")
        if i < attempts:
            time.sleep(10)

    print(f"::error title=Live bytes proof failed::{url} did not serve the committed bytes ({last})")
    summary("### Live bytes proof: FAIL")
    summary("")
    summary(f"- URL: `{url}`")
    summary(f"- last result: {last}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
