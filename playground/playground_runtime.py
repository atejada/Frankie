"""
playground_runtime.py — the thin glue between the browser Playground and the
real Frankie toolchain.

This file runs inside Pyodide (CPython compiled to WebAssembly), in a Web
Worker. It adds no language behaviour of its own: `run` and `test` call the
very same `frankiec.run_file` / `frankiec.run_tests` the CLI uses (so error
messages, line mapping and the test runner output are identical to a local
install), and `fmt` calls `frankie_fmt` directly.

Every entry point returns a small JSON string: {"ok": bool, "code": int,
"error": str|null, "result": str|null}. Output itself is not returned — it
streams to the page through Pyodide's stdout/stderr hooks as it is produced.
"""

import json
import os
import sys

ROOT = "/frankie"
MAIN = "main.fk"


def _prepare(code):
    os.chdir(ROOT)
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    with open(os.path.join(ROOT, MAIN), "w", encoding="utf-8") as f:
        f.write(code)
    # frankiec.run_file / run_tests load a fresh stdlib copy but the compiled
    # program's `from frankie_stdlib import *` resolves through sys.modules —
    # drop it so state (loaded stitches, test counters, line maps) never leaks
    # from one Run click into the next.
    sys.modules.pop("frankie_stdlib", None)
    sys.modules.pop("frankie_stdlib_test", None)


def _finish(fn):
    """Run fn() (a frankiec entry point), translating sys.exit into a code."""
    code, error = 0, None
    try:
        fn()
    except SystemExit as e:
        c = e.code
        code = c if isinstance(c, int) else (0 if c is None else 1)
    except BaseException as e:  # noqa: BLE001 — surface anything to the page
        code, error = 1, f"{type(e).__name__}: {e}"
    finally:
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        except Exception:
            pass
    return json.dumps({"ok": code == 0 and error is None, "code": code,
                       "error": error, "result": None})


def run(code):
    _prepare(code)
    import frankiec
    return _finish(lambda: frankiec.run_file(MAIN))


def test(code):
    _prepare(code)
    import frankiec
    return _finish(lambda: frankiec.run_tests(MAIN))


def fmt(code):
    os.chdir(ROOT)
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    try:
        from frankie_fmt import fmt_source_with_warnings
        formatted, unpreserved = fmt_source_with_warnings(code)
        if unpreserved:
            lines = ", ".join(str(n) for n in unpreserved)
            print(f"[fmt] warning: comment(s) on line(s) {lines} are dangling "
                  f"at the end of a block and could not be re-attached — "
                  f"left out of the formatted output", file=sys.stderr)
        return json.dumps({"ok": True, "code": 0, "error": None,
                           "result": formatted})
    except Exception as e:  # noqa: BLE001
        return json.dumps({"ok": False, "code": 1,
                           "error": f"{type(e).__name__}: {e}", "result": None})
