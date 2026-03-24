"""
Frankie REPL — Interactive Read-Eval-Print Loop
Invoked via: frankiec repl
"""

import sys
import os
import importlib.util

FRANKIE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.expanduser("~/.frankie_history")
HISTORY_MAX  = 1000   # max lines kept in history file

# Import the canonical version from frankiec.py so there is only one source of truth
def _load_version():
    try:
        spec = importlib.util.spec_from_file_location(
            "frankiec_meta", os.path.join(FRANKIE_DIR, "frankiec.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.FRANKIE_VERSION
    except Exception:
        return "unknown"

_VERSION = _load_version()

BANNER = rf"""
  _____                 _    _
 |  ___| __ __ _ _ __ | | _(_) ___
 | |_ | '__/ _` | '_ \| |/ / |/ _ \
 |  _|| | | (_| | | | |   <| |  __/
 |_|  |_|  \__,_|_| |_|_|\_\_|\___|

 Frankie v{_VERSION} Interactive REPL
 Type 'exit' or Ctrl+D to quit, 'help' for commands.
"""

HELP = """
REPL Commands:
  exit / quit       Exit the REPL
  clear             Clear all defined variables and functions
  vars              Show all currently defined variables
  load <file.fk>    Load and run a .fk file into this session
  help              Show this message

Tips:
  - Arrow keys, history search (Ctrl+R), and line editing are supported
  - History is saved to ~/.frankie_history across sessions
  - Multi-line blocks: keep typing — Frankie detects incomplete input
  - Use 'p expr' to debug-print with type info
  - All stdlib functions are available (sum, mean, regex, etc.)
  - .env is auto-loaded at startup (access via env("KEY"))
"""

BLOCK_OPENERS = ('def ', 'if ', 'unless ', 'while ', 'until ',
                 'for ', 'do', 'begin', 'case ')
BLOCK_CLOSERS = ('end',)
BLOCK_CONTINUERS = ('elsif ', 'else', 'rescue', 'ensure', 'when ')


def _setup_readline():
    """Enable readline for arrow-key editing, Ctrl+R search, and history."""
    try:
        import readline
        # Tab completion: complete known Frankie keywords/methods
        COMPLETIONS = [
            'def ', 'end', 'if ', 'elsif ', 'else', 'unless ', 'while ',
            'until ', 'for ', 'in ', 'do ', 'return ', 'puts ', 'print ',
            'begin', 'rescue', 'ensure', 'raise', 'require', 'case', 'when',
            'next', 'break', 'true', 'false', 'nil', 'and', 'or', 'not',
            'each', 'map', 'select', 'reject', 'reduce', 'find', 'group_by',
            'each_slice', 'each_cons', 'each_with_index', 'sort_by',
            'tally', 'chunk', 'flatten', 'compact', 'uniq', 'zip',
            'push', 'pop', 'first', 'last', 'length', 'size',
            'upcase', 'downcase', 'strip', 'split', 'join', 'include?',
            'merge', 'keys', 'values', 'has_key?', 'fetch', 'dig',
            'puts', 'print', 'p ', 'input', 'input_int', 'input_float',
            'sum', 'mean', 'median', 'stdev', 'min', 'max', 'abs',
            'sqrt', 'floor', 'ceil', 'rand', 'rand_int', 'rand_float',
            'json_parse', 'json_dump', 'csv_parse', 'csv_dump',
            'file_read', 'file_write', 'file_exists', 'file_lines',
            'file_delete', 'file_mkdir', 'dir_list', 'dir_exists',
            'db_open', 'web_app', 'today', 'now', 'template', 'zip',
            'env', 'argv', 'exit', 'sleep',
        ]

        def _completer(text, state):
            options = [c for c in COMPLETIONS if c.startswith(text)]
            return options[state] if state < len(options) else None

        readline.set_completer(_completer)
        readline.parse_and_bind("tab: complete")

        # Load history
        if os.path.exists(HISTORY_FILE):
            try:
                readline.read_history_file(HISTORY_FILE)
            except OSError:
                pass

        readline.set_history_length(HISTORY_MAX)
        return readline
    except ImportError:
        return None


def _save_history(readline):
    """Flush readline history to ~/.frankie_history."""
    if readline is None:
        return
    try:
        readline.write_history_file(HISTORY_FILE)
    except OSError:
        pass


def _load_stdlib(exec_globals):
    """Inject the full Frankie stdlib into exec_globals."""
    stdlib_path = os.path.join(FRANKIE_DIR, 'frankie_stdlib.py')
    spec = importlib.util.spec_from_file_location('frankie_stdlib', stdlib_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for k, v in vars(mod).items():
        if not k.startswith('__'):
            exec_globals[k] = v


def _load_dotenv(exec_globals):
    """Auto-load .env from the current working directory into the env() function scope."""
    env_path = os.path.join(os.getcwd(), '.env')
    if not os.path.exists(env_path):
        return
    loaded = {}
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, _, val = line.partition('=')
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key:
                    os.environ[key] = val
                    loaded[key] = val
        if loaded:
            print(f"  [.env] Loaded {len(loaded)} variable(s) from .env")
    except OSError:
        pass


def _compile_and_run(source, exec_globals):
    """Compile Frankie source and execute it, returning (output, error)."""
    sys.path.insert(0, FRANKIE_DIR)
    from compiler.lexer import Lexer, LexError
    from compiler.parser import Parser, ParseError
    from compiler.codegen import CodeGen, CodeGenError

    try:
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        py_source = CodeGen().generate(ast, repl_mode=True)
    except LexError as e:
        return None, str(e)
    except ParseError as e:
        return None, str(e)
    except CodeGenError as e:
        return None, f"[CodeGen Error] {e}"

    import io
    old_stdout = sys.stdout
    sys.stdout = buf = io.StringIO()
    error = None
    try:
        exec(compile(py_source, '<repl>', 'exec'), exec_globals)
    except SystemExit:
        sys.stdout = old_stdout
        raise
    except Exception as e:
        error = f"[Runtime Error] {type(e).__name__}: {e}"
    finally:
        sys.stdout = old_stdout

    return buf.getvalue(), error


def _is_incomplete(lines):
    """Heuristic: is the current buffer waiting for more input?"""
    depth = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('def ') or stripped.startswith('if ') or \
           stripped.startswith('unless ') or stripped.startswith('while ') or \
           stripped.startswith('until ') or stripped.startswith('for ') or \
           stripped.startswith('begin') or stripped.startswith('case') or \
           stripped == 'do':
            depth += 1
        if ' do' in stripped and not stripped.startswith('do') and not stripped.startswith('#'):
            depth += 1
        if stripped == 'end' or stripped.endswith(' end'):
            depth -= 1
    return depth > 0


def _show_vars(exec_globals):
    """Print user-defined variables (skip stdlib and private names)."""
    import types
    _stdlib_path = os.path.join(FRANKIE_DIR, 'frankie_stdlib.py')
    _spec = importlib.util.spec_from_file_location('frankie_stdlib', _stdlib_path)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    stdlib_names = set(vars(_mod).keys())
    skip = {'__name__', '__file__', '__builtins__'} | stdlib_names
    user_vars = {k: v for k, v in exec_globals.items()
                 if k not in skip and not isinstance(v, types.FunctionType)
                 and not isinstance(v, types.ModuleType) and not k.startswith('_')}
    user_fns  = {k: v for k, v in exec_globals.items()
                 if k not in skip and isinstance(v, types.FunctionType)
                 and not k.startswith('_')}
    if user_vars:
        print("Variables:")
        for k, v in sorted(user_vars.items()):
            from frankie_stdlib import _fk_to_str
            print(f"  {k} = {_fk_to_str(v)}")
    if user_fns:
        print("Functions:")
        for k in sorted(user_fns):
            print(f"  def {k}(...)")
    if not user_vars and not user_fns:
        print("  (none defined yet)")


def run_repl():
    print(BANNER)
    readline = _setup_readline()

    exec_globals = {'__name__': '__repl__', '__file__': '<repl>'}
    _load_stdlib(exec_globals)
    _load_dotenv(exec_globals)

    buffer = []
    prompt_main = "fk> "
    prompt_cont = "... "

    while True:
        try:
            prompt = prompt_cont if buffer else prompt_main
            try:
                line = input(prompt)
            except EOFError:
                print("\nGoodbye! 🧟")
                _save_history(readline)
                break

            # REPL commands
            stripped = line.strip()
            if not buffer:
                if stripped in ('exit', 'quit'):
                    print("Goodbye! 🧟")
                    _save_history(readline)
                    break
                if stripped == 'help':
                    print(HELP)
                    continue
                if stripped == 'clear':
                    exec_globals.clear()
                    exec_globals['__name__'] = '__repl__'
                    exec_globals['__file__'] = '<repl>'
                    _load_stdlib(exec_globals)
                    print("  Session cleared.")
                    continue
                if stripped == 'vars':
                    _show_vars(exec_globals)
                    continue
                if stripped.startswith('load '):
                    fk_file = stripped[5:].strip()
                    if not os.path.exists(fk_file):
                        print(f"  [Error] File not found: {fk_file}")
                    else:
                        with open(fk_file) as f:
                            src = f.read()
                        out, err = _compile_and_run(src, exec_globals)
                        if out:
                            print(out, end='')
                        if err:
                            print(err)
                        else:
                            print(f"  Loaded: {fk_file}")
                    continue
                if stripped == '':
                    continue

            buffer.append(line)

            # Check if we need more input
            if _is_incomplete(buffer):
                continue

            # Empty line flushes a multi-line block
            if stripped == '' and buffer:
                pass

            source = '\n'.join(buffer)
            buffer = []

            if source.strip() == '':
                continue

            out, err = _compile_and_run(source, exec_globals)
            if out:
                print(out, end='')
                if out and not out.endswith('\n'):
                    print()
            if err:
                print(err)

        except KeyboardInterrupt:
            buffer = []
            print("\n  (interrupted — buffer cleared)")


# Import the canonical version from frankiec.py so there is only one source of truth
def _load_version():
    try:
        spec = importlib.util.spec_from_file_location(
            "frankiec_meta", os.path.join(FRANKIE_DIR, "frankiec.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.FRANKIE_VERSION
    except Exception:
        return "unknown"

_VERSION = _load_version()

BANNER = rf"""
  _____                 _    _
 |  ___| __ __ _ _ __ | | _(_) ___
 | |_ | '__/ _` | '_ \| |/ / |/ _ \
 |  _|| | | (_| | | | |   <| |  __/
 |_|  |_|  \__,_|_| |_|_|\_\_|\___|

 Frankie v{_VERSION} Interactive REPL
 Type 'exit' or Ctrl+D to quit, 'help' for commands.
"""

HELP = """
REPL Commands:
  exit / quit       Exit the REPL
  clear             Clear all defined variables and functions
  vars              Show all currently defined variables
  load <file.fk>    Load and run a .fk file into this session
  help              Show this message

Tips:
  - Multi-line blocks: keep typing — Frankie detects incomplete input
  - Use 'p expr' to debug-print with type info
  - All stdlib functions are available (sum, mean, regex, etc.)
"""

BLOCK_OPENERS = ('def ', 'if ', 'unless ', 'while ', 'until ',
                 'for ', 'do', 'begin', 'case ')
BLOCK_CLOSERS = ('end',)
BLOCK_CONTINUERS = ('elsif ', 'else', 'rescue', 'ensure', 'when ')


def _load_stdlib(exec_globals):
    """Inject the full Frankie stdlib into exec_globals."""
    stdlib_path = os.path.join(FRANKIE_DIR, 'frankie_stdlib.py')
    spec = importlib.util.spec_from_file_location('frankie_stdlib', stdlib_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for k, v in vars(mod).items():
        if not k.startswith('__'):
            exec_globals[k] = v


def _compile_and_run(source, exec_globals):
    """Compile Frankie source and execute it, returning (output, error)."""
    sys.path.insert(0, FRANKIE_DIR)
    from compiler.lexer import Lexer, LexError
    from compiler.parser import Parser, ParseError
    from compiler.codegen import CodeGen, CodeGenError

    try:
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        py_source = CodeGen().generate(ast, repl_mode=True)
    except LexError as e:
        return None, str(e)
    except ParseError as e:
        return None, str(e)
    except CodeGenError as e:
        return None, f"[CodeGen Error] {e}"

    import io
    old_stdout = sys.stdout
    sys.stdout = buf = io.StringIO()
    error = None
    try:
        exec(compile(py_source, '<repl>', 'exec'), exec_globals)
    except SystemExit:
        sys.stdout = old_stdout
        raise
    except Exception as e:
        error = f"[Runtime Error] {type(e).__name__}: {e}"
    finally:
        sys.stdout = old_stdout

    return buf.getvalue(), error


def _is_incomplete(lines):
    """Heuristic: is the current buffer waiting for more input?"""
    depth = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('def ') or stripped.startswith('if ') or \
           stripped.startswith('unless ') or stripped.startswith('while ') or \
           stripped.startswith('until ') or stripped.startswith('for ') or \
           stripped.startswith('begin') or stripped.startswith('case') or \
           stripped == 'do':
            depth += 1
        if ' do' in stripped and not stripped.startswith('do') and not stripped.startswith('#'):
            depth += 1
        if stripped == 'end' or stripped.endswith(' end'):
            depth -= 1
    return depth > 0


def _show_vars(exec_globals):
    """Print user-defined variables (skip stdlib and private names)."""
    import types, importlib.util, os as _os2
    # Build a set of all stdlib-exported names to exclude from user view
    _stdlib_path = _os2.path.join(FRANKIE_DIR, 'frankie_stdlib.py')
    _spec = importlib.util.spec_from_file_location('frankie_stdlib', _stdlib_path)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    stdlib_names = set(vars(_mod).keys())
    skip = {'__name__', '__file__', '__builtins__'} | stdlib_names
    user_vars = {k: v for k, v in exec_globals.items()
                 if k not in skip and not isinstance(v, types.FunctionType)
                 and not isinstance(v, types.ModuleType) and not k.startswith('_')}
    user_fns  = {k: v for k, v in exec_globals.items()
                 if k not in skip and isinstance(v, types.FunctionType)
                 and not k.startswith('_')}
    if user_vars:
        print("Variables:")
        for k, v in sorted(user_vars.items()):
            from frankie_stdlib import _fk_to_str
            print(f"  {k} = {_fk_to_str(v)}")
    if user_fns:
        print("Functions:")
        for k in sorted(user_fns):
            print(f"  def {k}(...)")
    if not user_vars and not user_fns:
        print("  (none defined yet)")


def run_repl():
    print(BANNER)
    exec_globals = {'__name__': '__repl__', '__file__': '<repl>'}
    _load_stdlib(exec_globals)

    buffer = []
    prompt_main = "fk> "
    prompt_cont = "... "

    while True:
        try:
            prompt = prompt_cont if buffer else prompt_main
            try:
                line = input(prompt)
            except EOFError:
                print("\nGoodbye! 🧟")
                break

            # REPL commands
            stripped = line.strip()
            if not buffer:
                if stripped in ('exit', 'quit'):
                    print("Goodbye! 🧟")
                    break
                if stripped == 'help':
                    print(HELP)
                    continue
                if stripped == 'clear':
                    exec_globals.clear()
                    exec_globals['__name__'] = '__repl__'
                    exec_globals['__file__'] = '<repl>'
                    _load_stdlib(exec_globals)
                    print("  Session cleared.")
                    continue
                if stripped == 'vars':
                    _show_vars(exec_globals)
                    continue
                if stripped.startswith('load '):
                    fk_file = stripped[5:].strip()
                    if not os.path.exists(fk_file):
                        print(f"  [Error] File not found: {fk_file}")
                    else:
                        with open(fk_file) as f:
                            src = f.read()
                        out, err = _compile_and_run(src, exec_globals)
                        if out:
                            print(out, end='')
                        if err:
                            print(err)
                        else:
                            print(f"  Loaded: {fk_file}")
                    continue
                if stripped == '':
                    continue

            buffer.append(line)

            # Check if we need more input
            if _is_incomplete(buffer):
                continue

            # Empty line flushes a multi-line block
            if stripped == '' and buffer:
                pass

            source = '\n'.join(buffer)
            buffer = []

            if source.strip() == '':
                continue

            out, err = _compile_and_run(source, exec_globals)
            if out:
                print(out, end='')
                if out and not out.endswith('\n'):
                    print()
            if err:
                print(err)

        except KeyboardInterrupt:
            buffer = []
            print("\n  (interrupted — buffer cleared)")
