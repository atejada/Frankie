#!/usr/bin/env python3
"""
frankiec — The Frankie Language Compiler & Interpreter v1.17.0
Usage:
    frankiec new    <project>      Scaffold a new Frankie project
    frankiec run    <file.fk>      Run a Frankie program
    frankiec build  <file.fk>      Compile to Python source
    frankiec check  <file.fk>      Syntax check + static analysis
    frankiec test   [file.fk] [--filter <name>] [--tag <tag>]  Run test suite
    frankiec fmt    [--write] [--check] <file.fk>  Auto-format source
    frankiec docs   [--output <out.md>] <file.fk>  Generate documentation
    frankiec stitch install <name> [--global]      Install a stitch from the registry
    frankiec stitch list                           List installed stitches
    frankiec repl   [--no-banner]  Start the interactive REPL
    frankiec watch  <file.fk> [--test]  Re-run on save
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

FRANKIE_VERSION = "1.17.0"
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


def compile_source_with_map(source: str, filename: str = "<stdin>"):
    """Like compile_source, but also returns the py→fk line map (v1.17)."""
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    cg = CodeGen()
    py_source = cg.generate(ast)
    return py_source, cg.line_map


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
        py_source, line_map = compile_source_with_map(source, fk_file)
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

    # Register the main file's line map for accurate tracebacks (v1.17)
    stdlib_mod._fk_register_line_map(os.path.abspath(fk_file), line_map)

    # Execute generated Python
    try:
        exec_globals = {**stdlib_globals, '__name__': '__main__', '__file__': fk_file}
        exec(compile(py_source, fk_file, 'exec'), exec_globals)
    except SystemExit as e:
        # Propagate the exact exit code from exit(n) calls in Frankie code
        sys.exit(e.code if e.code is not None else 0)
    except Exception as e:
        _print_runtime_error(e, fk_file, source, stdlib_mod._fk_line_maps)
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


def _friendly_type_error(e):
    msg = str(e)
    # Python: "unsupported operand type(s) for +: 'int' and 'str'"
    import re as _re
    m = _re.search(r"unsupported operand type\(s\) for (.+): '(.+)' and '(.+)'", msg)
    if m:
        op, left, right = m.group(1), m.group(2), m.group(3)
        type_names = {'int': 'Integer', 'float': 'Float', 'str': 'String',
                      'list': 'Vector', 'dict': 'Hash', 'bool': 'Boolean', 'NoneType': 'nil'}
        l = type_names.get(left, left)
        r = type_names.get(right, right)
        return f"Type mismatch — can't use {op!r} with {l} and {r}"
    m = _re.search(r"'(.+)' object is not (subscriptable|iterable|callable)", msg)
    if m:
        t = {'int': 'Integer', 'float': 'Float', 'str': 'String',
             'NoneType': 'nil'}.get(m.group(1), m.group(1))
        return f"Type error — {t} is not {m.group(2)}"
    return f"Type mismatch — {msg}"

def _friendly_index_error(e):
    msg = str(e)
    import re as _re
    m = _re.search(r'list index out of range', msg)
    if m:
        return "Index out of bounds — vector index does not exist"
    return f"Index out of bounds — {msg}"

def _friendly_file_error(e):
    msg = str(e)
    # Strip raw Python prefix like "[Errno 2] No such file or directory: 'x'"
    import re as _re
    m = _re.search(r"File not found: (.+)", msg)
    if m:
        return f"File not found: {m.group(1)}"
    m = _re.search(r"No such file or directory: '(.+)'", msg)
    if m:
        return f"File not found: '{m.group(1)}' — check the path and try again"
    return f"File not found: {msg}"


def _map_py_line(py_line, line_map):
    """Map a generated-Python line to its .fk source line via the code-
    gen line map. Falls back to the nearest preceding mapped line, then to
    the legacy header-offset heuristic."""
    if line_map:
        if py_line in line_map:
            return line_map[py_line]
        prior = [ln for ln in line_map if ln <= py_line]
        if prior:
            return line_map[max(prior)]
    return max(1, py_line - 5)


def _print_runtime_error(e, fk_file, source, line_maps=None):
    """Print a friendly runtime error with source context.

    v1.17: walks the whole traceback and reports the deepest frame inside
    ANY .fk file — so errors inside require'd files, imports and stitches
    point at the right file and the right line.
    """
    import traceback as _tb

    line_maps = line_maps or {}
    tb_frames = _tb.extract_tb(sys.exc_info()[2])
    err_file, fk_line = None, None
    for frame in reversed(tb_frames):
        if frame.filename.endswith('.fk'):
            err_file = os.path.abspath(frame.filename)
            fk_line = _map_py_line(frame.lineno, line_maps.get(err_file))
            break

    # If the error is in another .fk file, show that file's source instead
    display_file = fk_file
    display_source = source
    if err_file and err_file != os.path.abspath(fk_file):
        display_file = err_file
        try:
            with open(err_file, 'r', encoding='utf-8') as f:
                display_source = f.read()
        except OSError:
            display_source = None

    friendly = {
        'ZeroDivisionError': 'Division by zero',
        'NameError':         'Undefined variable or function: ' + (str(e).split("'")[1] if "'" in str(e) else str(e)),
        'TypeError':         _friendly_type_error(e),
        'IndexError':        _friendly_index_error(e),
        'KeyError':          f"Key not found: {e}",
        'RecursionError':    'Stack overflow (too much recursion)',
        'ValueError':        f"Invalid value: {e}",
        'FileNotFoundError': _friendly_file_error(e),
        'AttributeError':    f"No such method or property: {e}",
        'RuntimeError':      str(e),
    }
    kind = type(e).__name__
    # v1.17: user-defined error types display as "TypeName: message"
    if getattr(type(e), '_fk_user_error', False):
        desc = f"{kind}: {e}"
    else:
        desc = friendly.get(kind, str(e))

    print(f"\n╔══ Frankie Runtime Error ══════════════════════════════", file=sys.stderr)
    print(f"║  {desc}", file=sys.stderr)
    if kind not in ('RuntimeError',) and str(e) not in desc:
        print(f"║  ({kind}: {e})", file=sys.stderr)

    if fk_line and display_source:
        lines = display_source.splitlines()
        lo = max(0, fk_line - 3)
        hi = min(len(lines), fk_line + 2)
        print(f"║", file=sys.stderr)
        print(f"║  File: {display_file}", file=sys.stderr)
        for i, line in enumerate(lines[lo:hi], lo + 1):
            marker = "──▶" if i == fk_line else "   "
            print(f"║  {marker} {i:4} │ {line}", file=sys.stderr)
    elif display_source:
        print(f"║  File: {display_file}", file=sys.stderr)

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


def check_file(fk_file: str, strict: bool = False):
    """Syntax check + static analysis (v1.17).

    Reports undefined variables/functions, wrong argument counts and
    unused local variables. Exit 1 on errors (or warnings with --strict).
    """
    if not os.path.exists(fk_file):
        print(f"[Frankie] Error: File not found: {fk_file}", file=sys.stderr)
        sys.exit(1)

    with open(fk_file, 'r', encoding='utf-8') as f:
        source = f.read()

    try:
        tokens = Lexer(source).tokenize()
        program = Parser(tokens).parse()
    except LexError as e:
        _print_compile_error(str(e), e.line, source, fk_file)
        sys.exit(1)
    except ParseError as e:
        _print_compile_error(str(e), e.token.line, source, fk_file)
        sys.exit(1)

    # Static analysis — never let an analyzer bug kill the check command
    try:
        from compiler.analyzer import Analyzer
        issues = Analyzer(source_path=fk_file).analyze(program)
    except Exception:
        issues = []

    errors   = [i for i in issues if i.severity == 'error']
    warnings = [i for i in issues if i.severity == 'warning']

    if not issues:
        print(f"[Frankie] ✓ {fk_file} — No problems found.")
        return

    lines = source.splitlines()
    for issue in issues:
        icon = "\033[31m✗\033[0m" if issue.severity == 'error' else "\033[33m⚠\033[0m"
        loc = f"{fk_file}:{issue.line}" if issue.line else fk_file
        print(f"  {icon}  {loc} — {issue.message}")
        if issue.line and 0 < issue.line <= len(lines):
            print(f"        {issue.line:4} │ {lines[issue.line - 1]}")

    summary = []
    if errors:
        summary.append(f"\033[31m{len(errors)} error(s)\033[0m")
    if warnings:
        summary.append(f"\033[33m{len(warnings)} warning(s)\033[0m")
    print(f"\n[Frankie] {fk_file} — " + ", ".join(summary))

    if errors or (strict and warnings):
        sys.exit(1)


def run_tests(fk_file: str = None, test_filter: str = None, test_tag: str = None):
    """Run a Frankie test file using the built-in assert/assert_eq harness."""
    import importlib.util, time

    if fk_file is None:
        fk_file = 'test.fk'

    if not os.path.exists(fk_file):
        print(f"[Frankie] Error: Test file not found: {fk_file}", file=sys.stderr)
        sys.exit(1)

    # v1.17: --filter / --tag are passed to test() groups via the environment
    if test_filter:
        os.environ['FRANKIE_TEST_FILTER'] = test_filter
    else:
        os.environ.pop('FRANKIE_TEST_FILTER', None)
    if test_tag:
        os.environ['FRANKIE_TEST_TAG'] = test_tag
    else:
        os.environ.pop('FRANKIE_TEST_TAG', None)

    with open(fk_file, 'r', encoding='utf-8') as f:
        source = f.read()

    try:
        py_source, line_map = compile_source_with_map(source, fk_file)
    except (LexError, ParseError, CodeGenError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    # Load a fresh copy of the stdlib so we get a clean _fk_test_suite singleton
    stdlib_dir = os.path.dirname(os.path.abspath(__file__))
    stdlib_path = os.path.join(stdlib_dir, 'frankie_stdlib.py')
    spec = importlib.util.spec_from_file_location("frankie_stdlib_test", stdlib_path)
    stdlib_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(stdlib_mod)
    stdlib_mod._fk_register_line_map(os.path.abspath(fk_file), line_map)
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
    skipped = getattr(suite, '_skipped', 0)
    skip_note = f", {skipped} group(s) skipped" if skipped else ""

    print(f"╠═══════════════════════════════════════════════════════")
    if suite._fail == 0:
        print(f"║  \033[32m✓  All {total} test(s) passed\033[0m{skip_note}  ({elapsed*1000:.1f}ms)")
    else:
        print(f"║  \033[33m{suite._pass}/{total} passed, {suite._fail} failed\033[0m{skip_note}  ({elapsed*1000:.1f}ms)")
        for err in suite._errors:
            print(f"║    \033[31m✗\033[0m {err}")
    print(f"╚═══════════════════════════════════════════════════════\n")

    if suite._fail > 0:
        sys.exit(1)


HELP_TEXT = {
    'run':     "frankiec run <file.fk>\n  Compile and execute a Frankie program.\n  Exit code is propagated from exit(n) calls in Frankie code.",
    'repl':    "frankiec repl [--no-banner]\n  Start the interactive REPL with readline, tab completion, and\n  persistent history at ~/.frankie_history.\n  --no-banner   Skip the ASCII art header (useful when piping or embedding).",
    'test':    "frankiec test [file.fk] [--filter <name>] [--tag <tag>]\n  Run a Frankie test suite. Defaults to test.fk in the current directory.\n  Uses assert_eq, assert_true, assert_match, assert_nil, assert_raises, assert_raises_typed.\n  Group tests with: test \"name\", tags: [\"slow\"] do ... end\n  --filter  Only run test groups whose name contains the substring.\n  --tag     Only run test groups carrying the tag.",
    'stitch':  "frankiec stitch install <name> [--global]\n  Download a stitch from the Frankie registry (GitHub) into ./stitches/\n  (or ~/.frankie/stitches with --global). Zero dependencies — uses the\n  Python stdlib HTTP client.\nfrankiec stitch list\n  Show installed stitches and what's available in the registry.",
    'fmt':     "frankiec fmt [--write] [--check] <file.fk>\n  Auto-format Frankie source using the AST.\n  --write   Reformat file in-place.\n  --check   Exit 1 if the file is not already formatted (CI mode).",
    'docs':    "frankiec docs [--output <out.md>] <file.fk|dir>\n  Extract ## doc-comments from .fk source and render to Markdown.\n  --output  Write to a file instead of stdout.\n  Supports @param, @return, and @example tags.",
    'build':   "frankiec build <file.fk> [output.py]\n  Compile a .fk file to Python source without executing it.",
    'check':   "frankiec check [--strict] <file.fk>\n  Syntax check + static analysis without executing.\n  Finds undefined variables/functions, wrong argument counts, and\n  unused local variables. require/stitch/import are resolved.\n  Exit 0 = OK, 1 = errors found (--strict: warnings fail too).",
    'new':     "frankiec new <project_name>\n  Scaffold a new Frankie project with main.fk, test.fk, lib/, data/, .env.example.",
    'watch':   "frankiec watch <file.fk> [--test]\n  Watch a file for changes and re-run it automatically on save.\n  --test   Run as a test suite (frankiec test) instead of frankiec run.\n  Polls file modification time — zero dependencies, works everywhere.",
    'version': "frankiec version\n  Print the Frankie version string.",
}


def _watch_file(fk_file, test_mode=False):
    """Poll fk_file for mtime changes and re-run on save. Zero dependencies."""
    import time as _time
    if not os.path.exists(fk_file):
        print(f"[Frankie] watch: file not found: {fk_file!r}", file=sys.stderr)
        sys.exit(1)

    mode_label = "test" if test_mode else "run"
    print(f"[Frankie] Watching {fk_file!r} — will re-{mode_label} on save. Ctrl-C to stop.")

    def _run():
        print(f"\n[Frankie] ── Running {fk_file} ──────────────────────────")
        if test_mode:
            run_tests(fk_file)
        else:
            run_file(fk_file)

    last_mtime = None
    try:
        while True:
            try:
                mtime = os.stat(fk_file).st_mtime
            except FileNotFoundError:
                _time.sleep(0.5)
                continue

            if mtime != last_mtime:
                last_mtime = mtime
                if last_mtime is not None or True:  # always run on first pass
                    try:
                        _run()
                    except SystemExit:
                        pass  # don't let exit() kill the watcher
            _time.sleep(0.4)
    except KeyboardInterrupt:
        print("\n[Frankie] watch stopped.")


STITCH_REGISTRY_RAW = "https://raw.githubusercontent.com/atejada/Frankie/main/stitches/{name}.fk"
STITCH_REGISTRY_API = "https://api.github.com/repos/atejada/Frankie/contents/stitches"


def _stitch_command(args):
    """frankiec stitch install <name> [--global] | frankiec stitch list"""
    import urllib.request, urllib.error, json as _json

    if not args or args[0] not in ('install', 'list'):
        print("[Frankie] Usage: frankiec stitch install <name> [--global]\n"
              "         frankiec stitch list", file=sys.stderr)
        sys.exit(1)

    local_dir  = os.path.join(os.getcwd(), 'stitches')
    global_dir = os.path.join(os.path.expanduser('~'), '.frankie', 'stitches')

    if args[0] == 'list':
        found = False
        for label, d in (("project (./stitches)", local_dir),
                         ("global (~/.frankie/stitches)", global_dir)):
            if os.path.isdir(d):
                names = sorted(f[:-3] for f in os.listdir(d) if f.endswith('.fk'))
                if names:
                    found = True
                    print(f"\n  {label}:")
                    for n in names:
                        print(f"    🧵 {n}")
        if not found:
            print("[Frankie] No stitches installed yet. Try: frankiec stitch install frankiecolor")
        # Also show what's available in the registry (best-effort)
        try:
            req = urllib.request.Request(STITCH_REGISTRY_API,
                                         headers={'User-Agent': 'frankiec'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                entries = _json.loads(resp.read().decode('utf-8'))
            avail = sorted(e['name'][:-3] for e in entries
                           if e.get('name', '').endswith('.fk'))
            if avail:
                print(f"\n  available in the registry:")
                for n in avail:
                    print(f"    ⬇  {n}")
        except Exception:
            pass   # offline — local list is still useful
        print()
        return

    # install
    names = [a for a in args[1:] if not a.startswith('--')]
    if not names:
        print("[Frankie] Usage: frankiec stitch install <name> [--global]", file=sys.stderr)
        sys.exit(1)
    use_global = '--global' in args
    dest_dir = global_dir if use_global else local_dir
    os.makedirs(dest_dir, exist_ok=True)

    ok = True
    for name in names:
        name = name[:-3] if name.endswith('.fk') else name
        url = STITCH_REGISTRY_RAW.format(name=name)
        dest = os.path.join(dest_dir, f"{name}.fk")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'frankiec'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read().decode('utf-8')
            with open(dest, 'w', encoding='utf-8') as f:
                f.write(content)
            where = "~/.frankie/stitches" if use_global else "./stitches"
            print(f"[Frankie] 🧵 Installed stitch {name!r} → {where}/{name}.fk")
        except urllib.error.HTTPError as e:
            ok = False
            if e.code == 404:
                print(f"[Frankie] Stitch not found in registry: {name!r}", file=sys.stderr)
            else:
                print(f"[Frankie] Failed to fetch {name!r}: HTTP {e.code}", file=sys.stderr)
        except Exception as e:
            ok = False
            print(f"[Frankie] Failed to install {name!r}: {e}", file=sys.stderr)
    if not ok:
        sys.exit(1)


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
        no_banner = '--no-banner' in sys.argv[2:]
        run_repl(no_banner=no_banner)

    elif cmd == 'watch':
        args = sys.argv[2:]
        test_mode = '--test' in args
        files = [a for a in args if not a.startswith('--')]
        if not files:
            print("[Frankie] Usage: frankiec watch <file.fk> [--test]", file=sys.stderr)
            sys.exit(1)
        fk_file = files[0]
        _watch_file(fk_file, test_mode=test_mode)

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
        args = sys.argv[2:]
        strict = '--strict' in args
        files = [a for a in args if not a.startswith('--')]
        if not files:
            print("[Frankie] Usage: frankiec check [--strict] <file.fk>", file=sys.stderr)
            sys.exit(1)
        for f in files:
            check_file(f, strict=strict)

    elif cmd == 'test':
        args = sys.argv[2:]
        test_filter = test_tag = None
        if '--filter' in args:
            idx = args.index('--filter')
            if idx + 1 >= len(args):
                print("[Frankie] --filter requires a value", file=sys.stderr)
                sys.exit(1)
            test_filter = args[idx + 1]
            args = args[:idx] + args[idx + 2:]
        if '--tag' in args:
            idx = args.index('--tag')
            if idx + 1 >= len(args):
                print("[Frankie] --tag requires a value", file=sys.stderr)
                sys.exit(1)
            test_tag = args[idx + 1]
            args = args[:idx] + args[idx + 2:]
        fk_file = args[0] if args else None
        run_tests(fk_file, test_filter=test_filter, test_tag=test_tag)

    elif cmd == 'stitch':
        _stitch_command(sys.argv[2:])

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
