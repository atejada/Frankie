#!/usr/bin/env python3
"""
frankiec — The Frankie Language Compiler & Interpreter v1.3
Usage:
    frankiec new    <project>      Scaffold a new Frankie project
    frankiec run    <file.fk>      Run a Frankie program
    frankiec build  <file.fk>      Compile to Python source
    frankiec check  <file.fk>      Syntax check only
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

FRANKIE_VERSION = "1.3.0"
FRANKIE_BANNER = r"""
  _____                 _    _        
 |  ___| __ __ _ _ __ | | _(_) ___   
 | |_ | '__/ _` | '_ \| |/ / |/ _ \  
 |  _|| | | (_| | | | |   <| |  __/  
 |_|  |_|  \__,_|_| |_|_|\_\_|\___|  

 The Frankie Language Compiler v{version}
 Stitched together from Ruby • Python • R • Fortran
"""


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
    except SystemExit:
        raise
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


def main():
    if len(sys.argv) < 2:
        from repl import run_repl
        run_repl()
        return

    cmd = sys.argv[1]

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

    else:
        print(f"[Frankie] Unknown command: {cmd!r}", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
