#!/usr/bin/env python3
"""
build_bundle.py — pack the Frankie toolchain into one JSON file for the
browser Playground.

The Playground (a section of frankie_website.html) runs the *real* compiler
in Pyodide. Pyodide needs the source files in its virtual filesystem; this
script collects them into playground/frankie_bundle.json:

    {"version": "1.22.3", "files": {"frankiec.py": "...", "compiler/lexer.py": "...", ...}}

Re-run it whenever the compiler, stdlib, formatter or a bundled stitch
changes (it's part of the release checklist in CLAUDE.md), then commit the
regenerated JSON next to the website:

    python3 playground/build_bundle.py            # write the bundle
    python3 playground/build_bundle.py --check    # exit 1 if it is stale

Zero dependencies — standard library only, like everything else here.
"""

import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "frankie_bundle.json")

# Everything the toolchain imports at run time. The REPL is included because
# frankie_stdlib lazily imports it; the LSP, docs generator and scaffolder
# are left out — nothing in a browser tab calls them.
TOP_LEVEL = ["frankiec.py", "frankie_stdlib.py", "frankie_fmt.py", "repl.py"]
GLOBS = ["compiler/*.py", "stitches/*.fk"]


def collect():
    files = {}
    for name in TOP_LEVEL:
        files[name] = open(os.path.join(ROOT, name), encoding="utf-8").read()
    for pattern in GLOBS:
        for path in sorted(glob.glob(os.path.join(ROOT, pattern))):
            rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
            files[rel] = open(path, encoding="utf-8").read()
    files["playground_runtime.py"] = open(
        os.path.join(HERE, "playground_runtime.py"), encoding="utf-8").read()
    return files


def build():
    files = collect()
    m = re.search(r'FRANKIE_VERSION\s*=\s*"([^"]+)"', files["frankiec.py"])
    version = m.group(1) if m else "unknown"
    # sort_keys + compact separators → byte-identical output for identical
    # input, so --check and git diffs are meaningful.
    return json.dumps({"version": version, "files": files},
                      sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")) + "\n"


def main():
    data = build()
    if "--check" in sys.argv[1:]:
        current = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if current != data:
            print("playground/frankie_bundle.json is stale — run: "
                  "python3 playground/build_bundle.py", file=sys.stderr)
            sys.exit(1)
        print("playground bundle is up to date ✓")
        return
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(data)
    n = len(json.loads(data)["files"])
    print(f"wrote {os.path.relpath(OUT, ROOT)} — {n} files, "
          f"{len(data.encode('utf-8')) // 1024} KB "
          f"(v{json.loads(data)['version']})")


if __name__ == "__main__":
    main()
