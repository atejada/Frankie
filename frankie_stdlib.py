"""
frankie_stdlib.py — Frankie Standard Library Runtime
Provides all built-in functions and helpers for compiled Frankie programs.
"""

import math
import sys


# ─── Type Conversion ─────────────────────────────────────────────────────────

def _fk_to_int(x):
    try:
        return int(x)
    except (ValueError, TypeError):
        raise RuntimeError(f"[Frankie] Cannot convert {x!r} to Integer")

def _fk_to_float(x):
    try:
        return float(x)
    except (ValueError, TypeError):
        raise RuntimeError(f"[Frankie] Cannot convert {x!r} to Float")

def _fk_to_str(x):
    if x is None:
        return "nil"
    if x is True:
        return "true"
    if x is False:
        return "false"
    if isinstance(x, list):
        inner = ", ".join(_fk_to_str(e) for e in x)
        return f"[{inner}]"
    if isinstance(x, dict):
        pairs = ", ".join(f"{k}: {_fk_to_str(v)}" for k, v in x.items())
        return "{" + pairs + "}"
    return str(x)


# ─── Arithmetic (vector-aware) ────────────────────────────────────────────────

def _fk_arith(left_repr, left, right_repr, right, op):
    """Perform arithmetic, supporting vector (list) operands."""
    def scalar_op(a, b, o):
        if o == '+': return a + b
        if o == '-': return a - b
        if o == '*': return a * b
        if o == '/': return a / b
        if o == '//': return a // b
        if o == '%': return a % b
        if o == '**': return a ** b
        raise RuntimeError(f"[Frankie] Unknown operator: {o}")

    if isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            raise RuntimeError(f"[Frankie] Vector length mismatch: {len(left)} vs {len(right)}")
        return [scalar_op(a, b, op) for a, b in zip(left, right)]
    elif isinstance(left, list) and not isinstance(right, list):
        return [scalar_op(a, right, op) for a in left]
    elif not isinstance(left, list) and isinstance(right, list):
        return [scalar_op(left, b, op) for b in right]
    else:
        return scalar_op(left, right, op)


# ─── Math Functions ───────────────────────────────────────────────────────────

def _fk_sum(v):
    if isinstance(v, (list, range)):
        return sum(v)
    return v

def _fk_mean(v):
    lst = list(v)
    if not lst:
        raise RuntimeError("[Frankie] mean() called on empty vector")
    return sum(lst) / len(lst)

def _fk_min(*args):
    if len(args) == 1 and isinstance(args[0], (list, range)):
        return min(args[0])
    return min(args)

def _fk_max(*args):
    if len(args) == 1 and isinstance(args[0], (list, range)):
        return max(args[0])
    return max(args)

def _fk_abs(x):
    return abs(x)

def _fk_sqrt(x):
    return math.sqrt(x)

def _fk_floor(x):
    return math.floor(x)

def _fk_ceil(x):
    return math.ceil(x)

def _fk_length(x):
    return len(x)


# ─── Vector Construction ──────────────────────────────────────────────────────

def _fk_vec(x):
    """Create a list from a range or iterable."""
    return list(x)


# ─── List Helpers ─────────────────────────────────────────────────────────────

def _fk_list_push(lst, val):
    lst.append(val)
    return lst


# ─── I/O ─────────────────────────────────────────────────────────────────────

def _fk_debug(val):
    """p — debug print with type info."""
    type_name = type(val).__name__
    type_map = {
        'int': 'Integer', 'float': 'Float', 'str': 'String',
        'bool': 'Boolean', 'list': 'Vector', 'dict': 'Hash',
        'NoneType': 'Nil', 'range': 'Range',
    }
    fk_type = type_map.get(type_name, type_name)
    print(f"({fk_type}) {_fk_to_str(val)}")


# ─── Statistical Functions ────────────────────────────────────────────────────

def median(v):
    """Median of a list."""
    lst = sorted(list(v))
    n = len(lst)
    if n == 0:
        raise RuntimeError("[Frankie] median() called on empty vector")
    mid = n // 2
    if n % 2 == 0:
        return (lst[mid - 1] + lst[mid]) / 2
    return lst[mid]

def stdev(v):
    """Standard deviation of a list."""
    lst = list(v)
    n = len(lst)
    if n < 2:
        raise RuntimeError("[Frankie] stdev() requires at least 2 values")
    m = sum(lst) / n
    return math.sqrt(sum((x - m) ** 2 for x in lst) / (n - 1))

def variance(v):
    """Variance of a list."""
    return stdev(v) ** 2

def clamp(x, lo, hi):
    """Clamp x between lo and hi."""
    return max(lo, min(hi, x))

def linspace(start, stop, n):
    """n evenly spaced values between start and stop (inclusive)."""
    if n < 2:
        return [float(start)]
    step = (stop - start) / (n - 1)
    return [start + step * i for i in range(n)]

def seq(start, stop, step=1):
    """Sequence similar to R's seq()."""
    result = []
    current = start
    if step > 0:
        while current <= stop:
            result.append(current)
            current = round(current + step, 10)
    else:
        while current >= stop:
            result.append(current)
            current = round(current + step, 10)
    return result


# ─── String Helpers ───────────────────────────────────────────────────────────

def rep(x, times):
    """Repeat a value or list, like R's rep()."""
    if isinstance(x, list):
        return x * times
    return [x] * times

def paste(*args, sep=" "):
    """Concatenate values like R's paste()."""
    return sep.join(_fk_to_str(a) for a in args)

def sprintf(fmt, *args):
    """Formatted string like sprintf."""
    return fmt % args


# ─── Type Checks ─────────────────────────────────────────────────────────────

def is_integer(x):
    return isinstance(x, int) and not isinstance(x, bool)

def is_float(x):
    return isinstance(x, float)

def is_string(x):
    return isinstance(x, str)

def is_vector(x):
    return isinstance(x, list)

def is_nil(x):
    return x is None

def is_bool(x):
    return isinstance(x, bool)


# ─── Hash Helpers ─────────────────────────────────────────────────────────────

def _fk_hash_merge_bang(h, other):
    """Merge other into h in-place (merge!)."""
    h.update(other)
    return h

def _fk_hash_store(h, key, value):
    """Store a key-value pair in hash."""
    h[key] = value
    return h


# ─── Safe Indexing & Slicing ──────────────────────────────────────────────────

def _fk_index(target, index):
    """Nil-safe index access — returns None instead of raising KeyError."""
    if isinstance(target, dict):
        return target.get(index, None)
    try:
        return target[index]
    except IndexError:
        return None

def _fk_slice(target, start, end, inclusive=True):
    """Range-based slice for strings and vectors."""
    if inclusive:
        # For negative end index, end+1 wraps incorrectly (-1+1=0 gives empty)
        # Use None as stop to mean "to the end" when end is -1
        if end == -1:
            return target[start:]
        return target[start:end + 1]
    else:
        return target[start:end]


# ─── Regex ────────────────────────────────────────────────────────────────────
import re as _re

def regex(pattern, flags=""):
    """Compile a regex pattern. flags: 'i'=ignore case, 'm'=multiline, 's'=dotall."""
    flag_map = {'i': _re.IGNORECASE, 'm': _re.MULTILINE, 's': _re.DOTALL}
    combined = 0
    for f in flags:
        combined |= flag_map.get(f, 0)
    return _re.compile(pattern, combined)

def match(string, pattern):
    """Return first match object or nil. Pattern can be string or compiled regex."""
    if isinstance(pattern, str):
        pattern = _re.compile(pattern)
    m = pattern.search(string)
    return m if m else None

def match_all(string, pattern):
    """Return all matches as a vector of strings."""
    if isinstance(pattern, str):
        pattern = _re.compile(pattern)
    return pattern.findall(string)

def sub(string, pattern, replacement):
    """Replace first match."""
    if isinstance(pattern, str):
        pattern = _re.compile(pattern)
    return pattern.sub(replacement, string, count=1)

def gsub(string, pattern, replacement):
    """Replace all matches."""
    if isinstance(pattern, str):
        pattern = _re.compile(pattern)
    return pattern.sub(replacement, string)

def matches(string, pattern):
    """Return true if pattern matches anywhere in string."""
    if isinstance(pattern, str):
        pattern = _re.compile(pattern)
    return bool(pattern.search(string))

def _fk_match_op(left, right):
    """Implement =~ operator: string =~ pattern."""
    if isinstance(right, str):
        right = _re.compile(right)
    m = right.search(left)
    return m.start() if m else None


# ─── Multi-file: require ──────────────────────────────────────────────────────
import os as _os
import importlib.util as _ilu

_fk_loaded_files = set()

def _fk_require(path):
    """Load and execute another .fk file, once only (like Ruby's require)."""
    # Resolve path relative to cwd, add .fk if no extension
    if not path.endswith('.fk'):
        path = path + '.fk'
    abs_path = _os.path.abspath(path)
    if abs_path in _fk_loaded_files:
        return False   # already loaded
    if not _os.path.exists(abs_path):
        raise RuntimeError(f"[Frankie] require: file not found: {path!r}")
    _fk_loaded_files.add(abs_path)
    # Import the frankie compiler lazily
    import sys as _sys
    _frankie_dir = _os.path.dirname(_os.path.abspath(__file__))
    if _frankie_dir not in _sys.path:
        _sys.path.insert(0, _frankie_dir)
    from compiler.lexer import Lexer
    from compiler.parser import Parser
    from compiler.codegen import CodeGen
    with open(abs_path, 'r', encoding='utf-8') as _f:
        _src = _f.read()
    _tokens = Lexer(_src).tokenize()
    _ast = Parser(_tokens).parse()
    _py_src = CodeGen().generate(_ast)
    # Execute in caller's global scope (inject stdlib)
    import builtins
    _g = {k: v for k, v in globals().items()}
    _g['__file__'] = abs_path
    exec(compile(_py_src, abs_path, 'exec'), _g)
    # Propagate any new definitions back up
    import inspect
    _frame = inspect.currentframe().f_back
    if _frame:
        _frame.f_globals.update({k: v for k, v in _g.items()
                                  if not k.startswith('_fk_') and k not in ('__builtins__',)})
    return True


# ─── File I/O ─────────────────────────────────────────────────────────────────

class FrankieFile:
    """File handle returned by file_open()."""
    def __init__(self, path, mode):
        self._path = path
        self._mode = mode
        self._fh = open(path, mode, encoding='utf-8')

    def read(self):
        return self._fh.read()

    def write(self, text):
        self._fh.write(_fk_to_str(text))
        return self

    def close(self):
        self._fh.close()

    def __repr__(self):
        return f"File({self._path!r}, {self._mode!r})"


def file_read(path):
    """Read entire file as a string."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise RuntimeError(f"[Frankie] File not found: {path!r}")

def file_write(path, content):
    """Write string to file (overwrites)."""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(_fk_to_str(content))
    return True

def file_append(path, content):
    """Append string to file."""
    with open(path, 'a', encoding='utf-8') as f:
        f.write(_fk_to_str(content))
    return True

def file_exists(path):
    """Return true if file exists."""
    return _os.path.exists(path)

def file_lines(path):
    """Read file as a vector of lines (strips newlines)."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return [line.rstrip('\n') for line in f.readlines()]
    except FileNotFoundError:
        raise RuntimeError(f"[Frankie] File not found: {path!r}")

def file_delete(path):
    """Delete a file."""
    try:
        _os.remove(path)
        return True
    except FileNotFoundError:
        return False


# ─── String Formatting ────────────────────────────────────────────────────────

def format(template, *args):
    """Ruby/Python-style format: format("Hello %s, you are %d", name, age)"""
    try:
        return template % args
    except TypeError:
        return template

# sprintf is already defined above — alias it
def sprintf(fmt, *args):
    try:
        return fmt % args
    except TypeError:
        return fmt


# ─── System ───────────────────────────────────────────────────────────────────

def exit(code=0):
    import sys as _sys
    _sys.exit(code)

def argv():
    """Return command-line arguments as a vector."""
    import sys as _sys
    return _sys.argv[1:]

def env(key, default=None):
    """Get environment variable."""
    return _os.environ.get(key, default)
