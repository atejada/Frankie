#!/usr/bin/env python3
"""
frankiec — The Frankie Language Compiler & Interpreter v1.10
Usage:
    frankiec new    <project>      Scaffold a new Frankie project
    frankiec run    <file.fk>      Run a Frankie program
    frankiec build  <file.fk>      Compile to Python source
    frankiec check  <file.fk>      Syntax check only
    frankiec test   [file.fk]      Run test suite (default: test.fk)
    frankiec fmt    [--write] [--check] <file.fk>  Auto-format source
    frankiec docs   [--output <out.md>] <file.fk>  Generate documentation
    frankiec repl                  Start the interactive REPL
    frankiec version               Show version info
"""

import sys
import os
import argparse
import traceback

# Make sure the frankie package is importable from this directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from compiler.lexer import Lexer, LexError
from compiler.parser import Parser, ParseError
from compiler.codegen import CodeGen, CodeGenError

FRANKIE_VERSION = "1.10.0"
FRANKIE_BANNER = r"""
  _____                 _    _
 |  ___| __ __ _ _ __ | | _(_) ___
 | |_ | '__/ _` | '_ \| |/ / |/ _ \
 |  _|| | | (_| | | | |   <| |  __/
 |_|  |_|  \__,_|_| |_|_|\_\_|\___|

 The Frankie Language Compiler v{version}
 Stitched together from Ruby • Python • R • Fortran
"""


def _load_dotenv():
    """Auto-load .env from the current working directory into os.environ."""
    env_path = os.path.join(os.getcwd(), '.env')
    if not os.path.exists(env_path):
        return
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, _, val = line.partition('=')
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = val
    except OSError:
        pass


def compile_source(source: str, filename: str = "<stdin>") -> str:
    """Lex → Parse → Generate Python source."""
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    return CodeGen().generate(ast)


def run_file(fk_file: str):
    """Compile and execute a .fk file."""
    if not os.path.exists(fk_file):
        print(f"[Frankie] Error: File not found: {fk_file}", file=sys.stderr)
        sys.exit(1)

    # Auto-load .env before running
    _load_dotenv()

    with open(fk_file, 'r', encoding='utf-8') as f:
        source = f.read()

    try:
        py_source = compile_source(source, fk_file)
    except LexError as e:
        _print_compile_error(str(e), e.line, source, fk_file)
        sys.exit(1)
    except ParseError as e:
        _print_compile_error(str(e), e.token.line, source, fk_file)
        sys.exit(1)
    except CodeGenError as e:
        print(f"[Frankie Codegen Error] {e}", file=sys.stderr)
        sys.exit(1)

    # Add stdlib path
    stdlib_dir = os.path.dirname(os.path.abspath(__file__))
    if stdlib_dir not in sys.path:
        sys.path.insert(0, stdlib_dir)

    # Pre-import stdlib symbols into exec namespace
    import importlib.util, types
    stdlib_path = os.path.join(stdlib_dir, 'frankie_stdlib.py')
    spec = importlib.util.spec_from_file_location("frankie_stdlib", stdlib_path)
    stdlib_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(stdlib_mod)
    stdlib_globals = {k: v for k, v in vars(stdlib_mod).items() if not k.startswith('__')}

    # Execute generated Python
    try:
        exec_globals = {**stdlib_globals, '__name__': '__main__', '__file__': fk_file}
        exec(compile(py_source, fk_file, 'exec'), exec_globals)
    except SystemExit as e:
        # Propagate the exact exit code from exit(n) calls in Frankie code
        sys.exit(e.code if e.code is not None else 0)
    except Exception as e:
        _print_runtime_error(e, fk_file, source)
        sys.exit(1)


def _print_compile_error(msg, line_no, source, fk_file):
    """Print a compile error with source context."""
    print(f"\n╔══ Frankie Compile Error ══════════════════════════════", file=sys.stderr)
    print(f"║  {msg}", file=sys.stderr)
    if source and line_no:
        lines = source.splitlines()
        lo = max(0, line_no - 3)
        hi = min(len(lines), line_no + 2)
        print(f"║", file=sys.stderr)
        print(f"║  File: {fk_file}", file=sys.stderr)
        for i, line in enumerate(lines[lo:hi], lo + 1):
            marker = "──▶" if i == line_no else "   "
            print(f"║  {marker} {i:4} │ {line}", file=sys.stderr)
    print(f"╚═══════════════════════════════════════════════════════\n", file=sys.stderr)


def _print_runtime_error(e, fk_file, source):
    """Print a friendly runtime error with source context."""
    import traceback as _tb

    # Find line from the traceback — the compiled code uses fk_file as filename
    tb_frames = _tb.extract_tb(sys.exc_info()[2])
    fk_line = None
    for frame in reversed(tb_frames):
        if os.path.abspath(frame.filename) == os.path.abspath(fk_file):
            # Compiled code has a 5-line header; subtract to get .fk line
            # (header: comment, import math, import sys, from stdlib, blank)
            fk_line = max(1, frame.lineno - 5)
            break

    friendly = {
        'ZeroDivisionError': 'Division by zero',
        'NameError':         'Undefined variable or function: ' + (str(e).split("'")[1] if "'" in str(e) else str(e)),
        'TypeError':         'Wrong type for operation',
        'IndexError':        'Index out of bounds',
        'KeyError':          f"Key not found: {e}",
        'RecursionError':    'Stack overflow (too much recursion)',
        'ValueError':        f"Invalid value: {e}",
        'FileNotFoundError': f"File not found: {e}",
        'AttributeError':    f"No such method or property: {e}",
        'RuntimeError':      str(e),
    }
    kind = type(e).__name__
    desc = friendly.get(kind, str(e))

    print(f"\n╔══ Frankie Runtime Error ══════════════════════════════", file=sys.stderr)
    print(f"║  {desc}", file=sys.stderr)
    if kind not in ('RuntimeError',) and str(e) not in desc:
        print(f"║  ({kind}: {e})", file=sys.stderr)

    if fk_line and source:
        lines = source.splitlines()
        lo = max(0, fk_line - 3)
        hi = min(len(lines), fk_line + 2)
        print(f"║", file=sys.stderr)
        print(f"║  File: {fk_file}", file=sys.stderr)
        for i, line in enumerate(lines[lo:hi], lo + 1):
            marker = "──▶" if i == fk_line else "   "
            print(f"║  {marker} {i:4} │ {line}", file=sys.stderr)
    elif source:
        print(f"║  File: {fk_file}", file=sys.stderr)

    print(f"╚═══════════════════════════════════════════════════════\n", file=sys.stderr)


def build_file(fk_file: str, output: str = None):
    """Compile .fk to .py and write to disk."""
    if not os.path.exists(fk_file):
        print(f"[Frankie] Error: File not found: {fk_file}", file=sys.stderr)
        sys.exit(1)

    with open(fk_file, 'r', encoding='utf-8') as f:
        source = f.read()

    try:
        py_source = compile_source(source, fk_file)
    except (LexError, ParseError, CodeGenError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    if output is None:
        output = os.path.splitext(fk_file)[0] + '.py'

    with open(output, 'w', encoding='utf-8') as f:
        f.write(py_source)

    print(f"[Frankie] Compiled: {fk_file} → {output}")


def check_file(fk_file: str):
    """Syntax check only — no code generation."""
    if not os.path.exists(fk_file):
        print(f"[Frankie] Error: File not found: {fk_file}", file=sys.stderr)
        sys.exit(1)

    with open(fk_file, 'r', encoding='utf-8') as f:
        source = f.read()

    try:
        tokens = Lexer(source).tokenize()
        Parser(tokens).parse()
        print(f"[Frankie] ✓ {fk_file} — No syntax errors.")
    except (LexError, ParseError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


def run_tests(fk_file: str = None):
    """Run a Frankie test file using the built-in assert/assert_eq harness."""
    import importlib.util, time

    if fk_file is None:
        fk_file = 'test.fk'

    if not os.path.exists(fk_file):
        print(f"[Frankie] Error: Test file not found: {fk_file}", file=sys.stderr)
        sys.exit(1)

    with open(fk_file, 'r', encoding='utf-8') as f:
        source = f.read()

    try:
        py_source = compile_source(source, fk_file)
    except (LexError, ParseError, CodeGenError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    # Load a fresh copy of the stdlib so we get a clean _fk_test_suite singleton
    stdlib_dir = os.path.dirname(os.path.abspath(__file__))
    stdlib_path = os.path.join(stdlib_dir, 'frankie_stdlib.py')
    spec = importlib.util.spec_from_file_location("frankie_stdlib_test", stdlib_path)
    stdlib_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(stdlib_mod)
    stdlib_globals = {k: v for k, v in vars(stdlib_mod).items() if not k.startswith('__')}

    # The generated code does `from frankie_stdlib import *` which would pull
    # from the installed module, not our fresh copy.  Patch sys.modules so the
    # import inside exec picks up our fresh copy (with its clean suite).
    import sys as _sys
    _old = _sys.modules.get('frankie_stdlib')
    _sys.modules['frankie_stdlib'] = stdlib_mod

    print(f"\n╔══ Frankie Test Runner ════════════════════════════════")
    print(f"║  {fk_file}")
    print(f"╠═══════════════════════════════════════════════════════")
    t0 = time.time()

    exec_globals = {**stdlib_globals, '__name__': '__main__', '__file__': fk_file}

    try:
        exec(compile(py_source, fk_file, 'exec'), exec_globals)
    except SystemExit:
        pass
    except Exception as e:
        stdlib_mod._fk_test_suite._fail += 1
        stdlib_mod._fk_test_suite._errors.append(str(e))
        print(f"  \033[31m✗\033[0m  Uncaught error: {e}")
    finally:
        # Restore sys.modules
        if _old is None:
            _sys.modules.pop('frankie_stdlib', None)
        else:
            _sys.modules['frankie_stdlib'] = _old

    suite = stdlib_mod._fk_test_suite
    elapsed = time.time() - t0
    total = suite._pass + suite._fail

    print(f"╠═══════════════════════════════════════════════════════")
    if suite._fail == 0:
        print(f"║  \033[32m✓  All {total} test(s) passed\033[0m  ({elapsed*1000:.1f}ms)")
    else:
        print(f"║  \033[33m{suite._pass}/{total} passed, {suite._fail} failed\033[0m  ({elapsed*1000:.1f}ms)")
        for err in suite._errors:
            print(f"║    \033[31m✗\033[0m {err}")
    print(f"╚═══════════════════════════════════════════════════════\n")

    if suite._fail > 0:
        sys.exit(1)


HELP_TEXT = {
    'run':     "frankiec run <file.fk>\n  Compile and execute a Frankie program.\n  Exit code is propagated from exit(n) calls in Frankie code.",
    'repl':    "frankiec repl\n  Start the interactive REPL with readline, tab completion, and\n  persistent history at ~/.frankie_history.",
    'test':    "frankiec test [file.fk]\n  Run a Frankie test suite. Defaults to test.fk in the current directory.\n  Uses assert_eq, assert_true, assert_raises, assert_raises_typed.",
    'fmt':     "frankiec fmt [--write] [--check] <file.fk>\n  Auto-format Frankie source using the AST.\n  --write   Reformat file in-place.\n  --check   Exit 1 if the file is not already formatted (CI mode).",
    'docs':    "frankiec docs [--output <out.md>] <file.fk|dir>\n  Extract ## doc-comments from .fk source and render to Markdown.\n  --output  Write to a file instead of stdout.\n  Supports @param, @return, and @example tags.",
    'build':   "frankiec build <file.fk> [output.py]\n  Compile a .fk file to Python source without executing it.",
    'check':   "frankiec check <file.fk>\n  Syntax-check a .fk file without executing it. Exit 0 = OK, 1 = error.",
    'new':     "frankiec new <project_name>\n  Scaffold a new Frankie project with main.fk, test.fk, lib/, data/, .env.example.",
    'version': "frankiec version\n  Print the Frankie version string.",
}


def main():
    if len(sys.argv) < 2:
        from repl import run_repl
        run_repl()
        return

    cmd = sys.argv[1]

    # Global help
    if cmd in ('--help', '-h', 'help'):
        print(__doc__)
        return

    # Per-command help
    if '--help' in sys.argv[2:] or '-h' in sys.argv[2:]:
        if cmd in HELP_TEXT:
            print(HELP_TEXT[cmd])
        else:
            print(__doc__)
        return

    if cmd == 'version':
        print(f"Frankie v{FRANKIE_VERSION}")

    elif cmd == 'new':
        if len(sys.argv) < 3:
            print("[Frankie] Usage: frankiec new <project_name>", file=sys.stderr)
            sys.exit(1)
        from scaffold import scaffold
        scaffold(sys.argv[2])

    elif cmd == 'repl':
        from repl import run_repl
        run_repl()

    elif cmd == 'run':
        if len(sys.argv) < 3:
            print("[Frankie] Usage: frankiec run <file.fk>", file=sys.stderr)
            sys.exit(1)
        run_file(sys.argv[2])

    elif cmd == 'build':
        if len(sys.argv) < 3:
            print("[Frankie] Usage: frankiec build <file.fk>", file=sys.stderr)
            sys.exit(1)
        out = sys.argv[3] if len(sys.argv) > 3 else None
        build_file(sys.argv[2], out)

    elif cmd == 'check':
        if len(sys.argv) < 3:
            print("[Frankie] Usage: frankiec check <file.fk>", file=sys.stderr)
            sys.exit(1)
        check_file(sys.argv[2])

    elif cmd == 'test':
        fk_file = sys.argv[2] if len(sys.argv) > 2 else None
        run_tests(fk_file)

    elif cmd == 'fmt':
        from frankie_fmt import fmt_file
        args = sys.argv[2:]
        write = '--write' in args
        check = '--check' in args
        files = [a for a in args if not a.startswith('--')]
        if not files:
            print("[Frankie] Usage: frankiec fmt [--write] [--check] <file.fk>", file=sys.stderr)
            sys.exit(1)
        ok = True
        for f in files:
            ok = fmt_file(f, write=write, check=check) and ok
        if not ok:
            sys.exit(1)

    elif cmd == 'docs':
        from frankie_docs import docs_file, docs_directory
        args = sys.argv[2:]
        output = None
        if '--output' in args:
            idx = args.index('--output')
            output = args[idx + 1]
            args = [a for i, a in enumerate(args) if i != idx and i != idx + 1]
        targets = [a for a in args if not a.startswith('--')]
        if not targets:
            print("[Frankie] Usage: frankiec docs [--output <file.md>] <file.fk|dir>", file=sys.stderr)
            sys.exit(1)
        ok = True
        for t in targets:
            if os.path.isdir(t):
                from frankie_docs import docs_directory
                ok = docs_directory(t, output) and ok
            else:
                ok = docs_file(t, output) and ok
        if not ok:
            sys.exit(1)

    else:
        print(f"[Frankie] Unknown command: {cmd!r}", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
