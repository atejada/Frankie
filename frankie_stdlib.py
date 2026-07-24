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
    if isinstance(x, range):
        # v1.17: ranges print in Frankie syntax — range(1, 11) → "1..10"
        if x.step == 1:
            return f"{x.start}..{x.stop - 1}"
        return _fk_to_str(list(x))
    if isinstance(x, dict):
        # Record type — display as RecordName(field: val, ...)
        if "__type__" in x:
            type_name = x["__type__"]
            fields = ", ".join(
                f"{k}: {_fk_to_str(v)}" for k, v in x.items() if k != "__type__"
            )
            return f"{type_name}({fields})"
        pairs = ", ".join(f"{k}: {_fk_to_str(v)}" for k, v in x.items())
        return "{" + pairs + "}"
    if isinstance(x, type):
        # A class object (FrankieDB, FrankieApp, ...) — never duck-type it
        return f"<class {x.__name__}>"
    # FrankieDate duck-type check
    if hasattr(x, 'year') and hasattr(x, 'format'):
        return x.to_s()
    # FrankieHTTPResponse duck-type check
    if hasattr(x, 'status') and hasattr(x, 'body') and hasattr(x, 'ok'):
        return repr(x)
    return str(x)


# ─── Arithmetic (vector-aware) ────────────────────────────────────────────────

def _fk_arith(left_repr, left, right_repr, right, op):
    """Perform arithmetic, supporting vector (list) and string operands."""
    def scalar_op(a, b, o):
        if o == '+': return a + b
        if o == '-': return a - b
        if o == '*': return a * b
        if o == '/': return a / b
        if o == '//': return a // b
        if o == '%': return a % b
        if o == '**': return a ** b
        raise RuntimeError(f"[Frankie] Unknown operator: {o}")

    # String * n  →  "ha" * 3  →  "hahaha"
    if op == '*' and isinstance(left, str) and isinstance(right, (int, float)):
        return left * int(right)
    if op == '*' and isinstance(right, str) and isinstance(left, (int, float)):
        return right * int(left)

    # Vector * n  →  [0] * 3  →  [0, 0, 0]
    if op == '*' and isinstance(left, list) and isinstance(right, (int, float)):
        return left * int(right)
    if op == '*' and isinstance(right, list) and isinstance(left, (int, float)):
        return right * int(left)

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

def _fk_index_key(index):
    """Normalise a hash/list key — strings stay strings, ints stay ints."""
    return index

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

_FK_ATTR_MISSING = object()

def _fk_attr_or_method(obj, name):
    """Unified dot-dispatch (v1.17): obj.name as record field, hash key,
    module constant, attribute, or zero-arg method call.

    - dict (records & hashes): field/key lookup → obj[name]
    - everything else: attribute lookup; callables are invoked with no args
    """
    if isinstance(obj, dict):
        if name in obj:
            return obj[name]
        native = getattr(obj, name, _FK_ATTR_MISSING)
        if native is not _FK_ATTR_MISSING and callable(native):
            return native()   # e.g. h.clear
        type_name = obj.get('__type__', 'Hash')
        raise AttributeError(f"[Frankie] {type_name} has no field {name!r}")
    val = getattr(obj, name, _FK_ATTR_MISSING)
    if val is _FK_ATTR_MISSING:
        raise AttributeError(
            f"[Frankie] {type(obj).__name__} has no method or property {name!r}")
    if callable(val):
        return val()
    return val

def _fk_method_call(obj, name, args):
    """Safe nav helper: call obj.name(*args)."""
    return getattr(obj, name)(*args)

def _fk_method_with_block(obj, name, args, block_fn):
    """Safe nav helper: call obj.name(*args) passing block_fn where needed."""
    method = getattr(obj, name)
    if args:
        return method(*args, block_fn)
    return method(block_fn)


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

# v1.18: `frankiec bundle` embeds pre-compiled modules here, keyed by the
# path string as written in the source ("lib/utils.fk", stitch names, ...).
# require/import/stitch check this registry before touching the filesystem.
_fk_bundled_compiled = {}

def _fk_exec_bundled(key, propagate_frames=1):
    """Execute a bundled pre-compiled module; returns its globals dict."""
    import inspect as _insp
    _g = {k: v for k, v in globals().items()}
    _g['__file__'] = f"<bundle:{key}>"
    exec(compile(_fk_bundled_compiled[key], f"<bundle:{key}>", 'exec'), _g)
    if propagate_frames:
        _frame = _insp.currentframe()
        for _ in range(propagate_frames + 1):
            _frame = _frame.f_back
            if _frame is None:
                return _g
        _frame.f_globals.update({k: v for k, v in _g.items()
                                  if not k.startswith('_fk_') and k not in ('__builtins__',)})
    return _g


def _fk_require(path):
    """Load and execute another .fk file, once only (like Ruby's require)."""
    # Resolve path relative to cwd, add .fk if no extension
    if not path.endswith('.fk'):
        path = path + '.fk'
    # Bundled program? Serve from the embedded registry.
    if path in _fk_bundled_compiled:
        if path in _fk_loaded_files:
            return False
        _fk_loaded_files.add(path)
        _fk_exec_bundled(path)
        return True
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
    _cg = CodeGen()
    _py_src = _cg.generate(_ast)
    _fk_register_line_map(abs_path, _cg.line_map)
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


def _fk_stitch(name):
    """Load a stitch (package) by name.

    Resolution order:
      1. ./stitches/<n>.fk          (project-local)
      2. ~/.frankie/stitches/<n>.fk (user-global)

    Raises a friendly error if neither exists.
    Compiles and executes the stitch, then propagates all defined names
    back to the calling Frankie script scope.
    """
    import inspect as _insp
    filename = f"{name}.fk"

    # Bundled program? Serve from the embedded registry.
    _bkey = f"stitch:{name}"
    if _bkey in _fk_bundled_compiled:
        if _bkey in _fk_loaded_files:
            return False
        _fk_loaded_files.add(_bkey)
        _fk_exec_bundled(_bkey)
        return True

    # 1. Project-local
    abs_path = _os.path.join(_os.getcwd(), "stitches", filename)
    if not _os.path.exists(abs_path):
        # 2. User-global
        abs_path = _os.path.join(_os.path.expanduser("~"), ".frankie", "stitches", filename)
        if not _os.path.exists(abs_path):
            raise RuntimeError(
                f'[Frankie] Stitch not found: "{name}"\n'
                f"  Put {filename} in ./stitches/ or ~/.frankie/stitches/"
            )

    # Already loaded — nothing to do
    if abs_path in _fk_loaded_files:
        return False
    _fk_loaded_files.add(abs_path)

    # Compile and execute the stitch file
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
    _cg = CodeGen()
    _py_src = _cg.generate(_ast)
    _fk_register_line_map(abs_path, _cg.line_map)
    _g = {k: v for k, v in globals().items()}
    _g['__file__'] = abs_path
    exec(compile(_py_src, abs_path, 'exec'), _g)

    # Propagate definitions back to the calling Frankie script
    _frame = _insp.currentframe().f_back
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
        raise FileNotFoundError(f"File not found: {path!r} — check the path and try again")

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
        raise FileNotFoundError(f"File not found: {path!r} — check the path and try again")

def file_delete(path):
    """Delete a file."""
    try:
        _os.remove(path)
        return True
    except FileNotFoundError:
        return False

def file_rename(src, dst):
    """Rename or move a file from src to dst."""
    try:
        _os.rename(src, dst)
        return True
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {src!r} — check the path and try again")
    except OSError as e:
        raise RuntimeError(f"[Frankie] file_rename failed: {e}")

def file_copy(src, dst):
    """Copy a file from src to dst. Returns dst path."""
    import shutil as _shutil
    try:
        _shutil.copy2(src, dst)
        return dst
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {src!r} — check the path and try again")
    except OSError as e:
        raise RuntimeError(f"[Frankie] file_copy failed: {e}")

def file_mkdir(path, recursive=True):
    """Create a directory. If recursive=true (default), creates all intermediate dirs."""
    try:
        if recursive:
            _os.makedirs(path, exist_ok=True)
        else:
            _os.mkdir(path)
        return True
    except OSError as e:
        raise RuntimeError(f"[Frankie] file_mkdir failed: {e}")

def dir_exists(path):
    """Return true if path is an existing directory."""
    return _os.path.isdir(path)

def dir_list(path="."):
    """Return a list of filenames in directory path (excluding . and ..)."""
    try:
        return sorted(_os.listdir(path))
    except OSError as e:
        raise RuntimeError(f"[Frankie] dir_list failed: {e}")


# ─── Path Helpers ─────────────────────────────────────────────────────────────
import os.path as _osp

def path_join(*parts):
    """Join path components: path_join("a", "b", "c") → "a/b/c" """
    return _osp.join(*[str(p) for p in parts])

def path_dirname(path):
    """Directory component of a path: path_dirname("/a/b/c.txt") → "/a/b" """
    return _osp.dirname(str(path))

def path_basename(path):
    """Filename component of a path: path_basename("/a/b/c.txt") → "c.txt" """
    return _osp.basename(str(path))

def path_extname(path):
    """Extension of a path: path_extname("file.txt") → ".txt" """
    return _osp.splitext(str(path))[1]

def path_stem(path):
    """Filename without extension: path_stem("file.txt") → "file" """
    return _osp.splitext(_osp.basename(str(path)))[0]

def path_absolute(path):
    """Resolve to absolute path."""
    return _osp.abspath(str(path))

def path_expand(path):
    """Expand ~ and environment variables in path."""
    return _osp.expandvars(_osp.expanduser(str(path)))


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

def template(tmpl, values):
    """Simple string template: replace {{key}} placeholders with values from a hash.
    Example: template(\"Hello, {{name}}! You are {{age}}.\", {name: \"Alice\", age: 30})
    """
    if not isinstance(values, dict):
        raise TypeError("[Frankie] template: second argument must be a hash")
    import re as _re_tmpl
    def replacer(m):
        key = m.group(1).strip()
        if key not in values:
            raise KeyError(f"[Frankie] template: key '{{key}}' not found in hash")
        return str(values[key])
    return _re_tmpl.sub(r'\{\{([^}]+)\}\}', replacer, tmpl)


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


# ─── v1.1 Iterator Helpers ────────────────────────────────────────────────────

def _fk_iter(iterable):
    """Yield items from any iterable. For dicts, yields [key, value] lists."""
    if isinstance(iterable, dict):
        for k, v in iterable.items():
            yield [k, v]
    else:
        yield from iterable

def _fk_select(iterable, fn):
    """Return filtered elements. For dicts, returns a new dict."""
    if isinstance(iterable, dict):
        return {k: v for k, v in iterable.items() if fn([k, v])}
    return [x for x in iterable if fn(x)]

def _fk_reject(iterable, fn):
    """Return elements where fn is false. For dicts, returns a new dict."""
    if isinstance(iterable, dict):
        return {k: v for k, v in iterable.items() if not fn([k, v])}
    return [x for x in iterable if not fn(x)]

def _fk_find(iterable, fn):
    """Return the first element for which fn returns true, or None."""
    for x in _fk_iter(iterable):
        if fn(x):
            return x
    return None

def _fk_reduce(iterable, fn, initial=None):
    """Fold a list into a single value."""
    lst = list(iterable)
    if not lst:
        return initial
    if initial is None:
        acc = lst[0]
        rest = lst[1:]
    else:
        acc = initial
        rest = lst
    for item in rest:
        acc = fn(acc, item)
    return acc

def _fk_each_with_object(iterable, obj, fn):
    """Iterate passing each element and a shared accumulator object."""
    for item in iterable:
        fn(item, obj)
    return obj

def _fk_any(iterable, fn=None):
    """Return true if any element satisfies fn (or is truthy if no fn)."""
    if fn is None:
        return any(_fk_iter(iterable))
    return any(fn(x) for x in _fk_iter(iterable))

def _fk_all(iterable, fn=None):
    """Return true if all elements satisfy fn (or are truthy if no fn)."""
    if fn is None:
        return all(_fk_iter(iterable))
    return all(fn(x) for x in _fk_iter(iterable))

def _fk_none(iterable, fn=None):
    """Return true if no elements satisfy fn."""
    if fn is None:
        return not any(_fk_iter(iterable))
    return not any(fn(x) for x in _fk_iter(iterable))

def _fk_count_if(iterable, fn):
    """Count elements satisfying fn."""
    return sum(1 for x in _fk_iter(iterable) if fn(x))

def _fk_flat_map(iterable, fn):
    """Map then flatten one level."""
    result = []
    for x in iterable:
        val = fn(x)
        if isinstance(val, list):
            result.extend(val)
        else:
            result.append(val)
    return result

def _fk_zip_vecs(*vecs):
    """Zip multiple vectors into a vector of vectors."""
    return [list(t) for t in zip(*vecs)]

def _fk_take(iterable, n):
    """Take first n elements."""
    return list(iterable)[:n]

def _fk_drop(iterable, n):
    """Drop first n elements."""
    return list(iterable)[n:]

def _fk_flatten(iterable):
    """Flatten one level of nesting."""
    result = []
    for item in iterable:
        if isinstance(item, list):
            result.extend(item)
        else:
            result.append(item)
    return result

def _fk_compact(iterable):
    """Remove nil (None) values."""
    return [x for x in iterable if x is not None]

def _fk_tally(iterable):
    """Count occurrences of each element — returns a hash."""
    result = {}
    for x in iterable:
        key = _fk_to_str(x)
        result[key] = result.get(key, 0) + 1
    return result

def _fk_chunk(iterable, n):
    """Split into chunks of size n."""
    lst = list(iterable)
    return [lst[i:i+n] for i in range(0, len(lst), n)]

def _fk_group_by(iterable, key_fn):
    """Group elements by the result of key_fn. Returns a hash of arrays."""
    result = {}
    for item in _fk_iter(iterable):
        key = key_fn(item)
        if isinstance(key, bool):
            k = str(key).lower()
        elif key is None:
            k = 'nil'
        else:
            k = str(key)
        if k not in result:
            result[k] = []
        result[k].append(item)
    return result

def _fk_each_slice(iterable, n):
    """Yield successive non-overlapping slices of size n."""
    lst = list(iterable)
    return [lst[i:i+n] for i in range(0, len(lst), n)]

def _fk_each_cons(iterable, n):
    """Yield all consecutive windows of size n (sliding window)."""
    lst = list(iterable)
    if n > len(lst):
        return []
    return [lst[i:i+n] for i in range(len(lst) - n + 1)]

def _fk_hash_merge(h1, h2):
    """Merge two hashes — h2 values win on key conflicts. Returns a new hash."""
    if not isinstance(h1, dict):
        raise TypeError(f"| operator requires a hash on the left, got {type(h1).__name__}")
    if not isinstance(h2, dict):
        raise TypeError(f"| operator requires a hash on the right, got {type(h2).__name__}")
    return {**h1, **h2}


def _fk_dig(obj, *keys):
    """Safe deep access: hash.dig("a", "b", "c") — returns nil instead of crashing."""
    current = obj
    for key in keys:
        if current is None:
            return None
        if isinstance(current, dict):
            k = str(key) if not isinstance(key, str) else key
            current = current.get(k, current.get(key))
        elif isinstance(current, list):
            try:
                idx = int(key)
                current = current[idx] if -len(current) <= idx < len(current) else None
            except (TypeError, ValueError):
                return None
        else:
            return None
    return current


import builtins as _builtins

def zip(*vecs):
    """Standalone zip: zip([1,2,3], ["a","b","c"]) → [[1,"a"],[2,"b"],[3,"c"]]"""
    if len(vecs) == 0:
        return []
    return [list(t) for t in _builtins.zip(*vecs)]


# ─── Destructuring Helper ─────────────────────────────────────────────────────

def _fk_unpack(value, count):
    """Unpack a vector/tuple into exactly count values, padding with nil."""
    if isinstance(value, (list, tuple)):
        lst = list(value)
    else:
        lst = [value]
    # Pad with None if too short
    while len(lst) < count:
        lst.append(None)
    return lst[:count]


def _fk_unpack_splat(value, n_before, n_after):
    """Unpack with a *rest splat.
    Returns a flat list: n_before items, then rest as a list, then n_after items."""
    lst = list(value) if isinstance(value, (list, tuple)) else [value]
    total_fixed = n_before + n_after
    while len(lst) < total_fixed:
        lst.append(None)
    before = lst[:n_before]
    rest   = lst[n_before: len(lst) - n_after if n_after > 0 else len(lst)]
    after  = lst[len(lst) - n_after:] if n_after > 0 else []
    return before + [rest] + after


# ─── v1.14 Runtime Helpers ────────────────────────────────────────────────────

def _fk_timeout(seconds, fn):
    """Run fn() with a time limit. Raises TimeoutError if it exceeds seconds."""
    import threading as _t
    result = [None]
    exc    = [None]

    def _target():
        try:
            result[0] = fn()
        except Exception as e:
            exc[0] = e

    thread = _t.Thread(target=_target, daemon=True)
    thread.start()
    thread.join(timeout=float(seconds))
    if thread.is_alive():
        raise TimeoutError(f"Operation timed out after {seconds}s")
    if exc[0] is not None:
        raise exc[0]
    return result[0]


def _fk_shape_match(subject, pattern):
    """Return True if subject (a dict) contains all key/value pairs in pattern."""
    if not isinstance(subject, dict) or not isinstance(pattern, dict):
        return False
    for k, v in pattern.items():
        if subject.get(k) != v:
            return False
    return True


def _fk_hmac_sign(value: str, secret: str) -> str:
    """Sign a value with HMAC-SHA256. Returns 'value:hex_digest'."""
    import hmac as _hmac
    import hashlib as _hashlib
    sig = _hmac.new(secret.encode(), value.encode(), _hashlib.sha256).hexdigest()
    return f"{value}:{sig}"


def _fk_hmac_verify(signed: str, secret: str):
    """Verify a signed value. Returns the original value or None if invalid."""
    import hmac as _hmac
    import hashlib as _hashlib
    if ':' not in signed:
        return None
    # Split on LAST colon so values containing ':' still work
    last_colon = signed.rfind(':')
    value = signed[:last_colon]
    provided_sig = signed[last_colon + 1:]
    expected_sig = _hmac.new(secret.encode(), value.encode(), _hashlib.sha256).hexdigest()
    if _hmac.compare_digest(provided_sig, expected_sig):
        return value
    return None

# ─── v1.15 Runtime Helpers ────────────────────────────────────────────────────
# Public aliases — callable directly from Frankie scripts
def hmac_sign(value, secret):
    """Sign a string with HMAC-SHA256: hmac_sign(value, secret) → signed_token"""
    return _fk_hmac_sign(str(value), str(secret))

def hmac_verify(signed, secret):
    """Verify an HMAC-signed token: hmac_verify(token, secret) → value or nil"""
    return _fk_hmac_verify(str(signed), str(secret))

def base64_encode(s):
    """Encode a string to Base64: base64_encode('hello') → 'aGVsbG8='"""
    import base64 as _b64
    return _b64.b64encode(str(s).encode('utf-8')).decode('ascii')

def base64_decode(s):
    """Decode a Base64 string: base64_decode('aGVsbG8=') → 'hello'"""
    import base64 as _b64
    try:
        # Add padding if needed
        padded = str(s) + '=' * (-len(str(s)) % 4)
        return _b64.b64decode(padded).decode('utf-8')
    except Exception as e:
        raise RuntimeError(f"[Frankie] base64_decode error: {e}")


# ─── v1.1 String Helpers ──────────────────────────────────────────────────────

def _fk_chars(s):
    """Return a vector of individual characters."""
    return list(s)

def _fk_bytes(s):
    """Return a vector of byte values."""
    return list(s.encode('utf-8'))

def _fk_str_count(s, sub):
    """Count occurrences of sub in s."""
    return s.count(sub)

def _fk_center(s, width, pad=" "):
    """Center string in a field of width, padded with pad."""
    return s.center(int(width), pad)

def _fk_ljust(s, width, pad=" "):
    """Left-justify string in a field of width."""
    return s.ljust(int(width), pad)

def _fk_rjust(s, width, pad=" "):
    """Right-justify string in a field of width."""
    return s.rjust(int(width), pad)

def _fk_squeeze(s, char=None):
    """Remove consecutive duplicate characters."""
    if not s:
        return s
    result = [s[0]]
    for c in s[1:]:
        if char is None:
            if c != result[-1]:
                result.append(c)
        else:
            if c != char or result[-1] != char:
                result.append(c)
    return ''.join(result)

def _fk_tr(s, from_chars, to_chars):
    """Translate characters (like Ruby's tr).
    If to_chars is shorter, its last char is used for the remainder."""
    if len(to_chars) == 0:
        return s
    # Pad to_chars to match from_chars length
    if len(to_chars) < len(from_chars):
        to_chars = to_chars + to_chars[-1] * (len(from_chars) - len(to_chars))
    table = str.maketrans(from_chars, to_chars[:len(from_chars)])
    return s.translate(table)

def _fk_str_delete(s, chars):
    """Delete all occurrences of chars from s."""
    return s.translate(str.maketrans('', '', chars))

def _fk_each_char(s, fn):
    """Call fn for each character."""
    for c in s:
        fn(c)

def _fk_each_line(s, fn):
    """Call fn for each line."""
    for line in s.splitlines():
        fn(line)

def _fk_lines(s):
    """Split string into lines."""
    return s.splitlines()

def _fk_chomp(s):
    """Remove trailing newline."""
    return s.rstrip('\n').rstrip('\r')

def _fk_chop(s):
    """Remove last character."""
    return s[:-1] if s else s

def _fk_ord(s):
    """Return ASCII code of first character."""
    return ord(s[0]) if s else 0

def _fk_chr(n):
    """Return character for ASCII code."""
    return chr(int(n))

def _fk_hex(s):
    """Parse hex string to integer."""
    return int(s, 16)

def _fk_oct(s):
    """Parse octal string to integer."""
    return int(s, 8)


# ─── Database (SQLite — zero external dependencies) ───────────────────────────
import sqlite3 as _sqlite3

class FrankieDB:
    """
    Frankie database connection wrapping sqlite3.
    All query results are returned as vectors of hashes (column name → value).
    """

    def __init__(self, path):
        self._path = path
        # isolation_level=None = autocommit mode; we manage BEGIN/COMMIT explicitly
        self._conn = _sqlite3.connect(path, isolation_level=None)
        self._conn.row_factory = _sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._in_tx = False  # track whether we're inside a user transaction

    # ── Low-level ──────────────────────────────────────────────────────────

    def exec(self, sql, params=None):
        """Execute a statement (INSERT/UPDATE/DELETE/CREATE). Returns row count."""
        if not self._in_tx:
            self._conn.execute("BEGIN")
        cur = self._conn.execute(sql, params or [])
        if not self._in_tx:
            self._conn.execute("COMMIT")
        return cur.rowcount

    def query(self, sql, params=None):
        """Run a SELECT and return a vector of hashes."""
        cur = self._conn.execute(sql, params or [])
        return [dict(row) for row in cur.fetchall()]

    def query_one(self, sql, params=None):
        """Run a SELECT and return the first row as a hash, or nil."""
        cur = self._conn.execute(sql, params or [])
        row = cur.fetchone()
        return dict(row) if row else None

    def last_id(self):
        """Return the rowid of the last INSERT."""
        return self._conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    # ── Convenience helpers ────────────────────────────────────────────────

    def insert(self, table, data):
        """Insert a hash of column→value into table. Returns new row id."""
        cols   = ", ".join(str(k) for k in data.keys())
        marks  = ", ".join("?" for _ in data)
        vals   = list(data.values())
        if not self._in_tx:
            self._conn.execute("BEGIN")
        self._conn.execute(f"INSERT INTO {table} ({cols}) VALUES ({marks})", vals)
        if not self._in_tx:
            self._conn.execute("COMMIT")
        return self.last_id()

    def insert_many(self, table, rows):
        """Insert a vector of hashes. Returns number of rows inserted."""
        if not rows:
            return 0
        cols  = ", ".join(str(k) for k in rows[0].keys())
        marks = ", ".join("?" for _ in rows[0])
        vals  = [list(r.values()) for r in rows]
        if not self._in_tx:
            self._conn.execute("BEGIN")
        self._conn.executemany(f"INSERT INTO {table} ({cols}) VALUES ({marks})", vals)
        if not self._in_tx:
            self._conn.execute("COMMIT")
        return len(rows)

    def find_all(self, table):
        """Return all rows from a table as a vector of hashes."""
        return self.query(f"SELECT * FROM {table}")

    def find(self, table, where):
        """Return rows matching a hash of conditions. All conditions ANDed."""
        clause = " AND ".join(f"{k} = ?" for k in where.keys())
        vals   = list(where.values())
        return self.query(f"SELECT * FROM {table} WHERE {clause}", vals)

    def find_one(self, table, where):
        """Return first row matching conditions, or nil."""
        clause = " AND ".join(f"{k} = ?" for k in where.keys())
        vals   = list(where.values())
        return self.query_one(f"SELECT * FROM {table} WHERE {clause}", vals)

    def update(self, table, data, where):
        """Update rows matching where-hash with data-hash. Returns row count."""
        set_clause   = ", ".join(f"{k} = ?" for k in data.keys())
        where_clause = " AND ".join(f"{k} = ?" for k in where.keys())
        vals = list(data.values()) + list(where.values())
        if not self._in_tx:
            self._conn.execute("BEGIN")
        cur  = self._conn.execute(
            f"UPDATE {table} SET {set_clause} WHERE {where_clause}", vals)
        if not self._in_tx:
            self._conn.execute("COMMIT")
        return cur.rowcount

    def delete(self, table, where):
        """Delete rows matching where-hash. Returns row count."""
        clause = " AND ".join(f"{k} = ?" for k in where.keys())
        vals   = list(where.values())
        cur    = self._conn.execute(f"DELETE FROM {table} WHERE {clause}", vals)
        self._conn.commit()
        return cur.rowcount

    def count(self, table, where=None):
        """Count rows, optionally filtered."""
        if where:
            clause = " AND ".join(f"{k} = ?" for k in where.keys())
            vals   = list(where.values())
            row    = self.query_one(f"SELECT COUNT(*) as n FROM {table} WHERE {clause}", vals)
        else:
            row = self.query_one(f"SELECT COUNT(*) as n FROM {table}")
        return row["n"] if row else 0

    def tables(self):
        """Return a vector of table names in this database."""
        rows = self.query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        return [r["name"] for r in rows]

    def columns(self, table):
        """Return a vector of column info hashes for a table."""
        rows = self.query(f"PRAGMA table_info({table})")
        return rows

    # ── Transactions ──────────────────────────────────────────────────────

    def begin(self):
        """Begin an explicit transaction block."""
        self._conn.execute("BEGIN")
        self._in_tx = True

    def commit(self):
        """Commit the explicit transaction."""
        self._conn.execute("COMMIT")
        self._in_tx = False

    def rollback(self):
        """Roll back the explicit transaction."""
        self._conn.execute("ROLLBACK")
        self._in_tx = False

    # ── Lifecycle ─────────────────────────────────────────────────────────

    def close(self):
        """Commit any pending work and close the connection."""
        try:
            if self._in_tx:
                self._conn.execute("COMMIT")
        except Exception:
            pass
        self._conn.close()

    def __repr__(self):
        return f"DB({self._path!r})"



def _fk_count_dispatch(obj, arg=None):
    """Runtime dispatch for .count() — handles DB, str, list.
    Uses duck typing (hasattr) to avoid isinstance cross-namespace issues."""
    if hasattr(obj, 'tables') and hasattr(obj, 'query'):
        # It's a FrankieDB — use its count method
        if arg is not None:
            return obj.count(arg)
        return 0
    if isinstance(obj, str) and arg is not None:
        return _fk_str_count(obj, arg)     # "hello".count("l")
    return len(obj)                        # vector/string length

def db_open(path=":memory:"):
    """Open or create a SQLite database. Use ':memory:' for an in-memory DB."""
    return FrankieDB(path)


# ═══════════════════════════════════════════════════════════════════════════════
# v1.3 STANDARD LIBRARY ADDITIONS
# ═══════════════════════════════════════════════════════════════════════════════

# ─── JSON ─────────────────────────────────────────────────────────────────────
import json as _json

def json_parse(s):
    """Parse a JSON string → Frankie value (hash/vector/string/number/bool/nil)."""
    try:
        return _json.loads(s)
    except _json.JSONDecodeError as e:
        raise RuntimeError(f"[Frankie] JSON parse error: {e}")

def json_encode(obj, pretty=False):
    """Serialize a Frankie value → JSON string. Alias: json_dump."""
    indent = 2 if pretty else None
    return _json.dumps(obj, indent=indent, default=str)

def json_dump(obj, pretty=False):
    """Serialize a Frankie value → JSON string. (json_encode is preferred)"""
    return json_encode(obj, pretty=pretty)

def json_read(path):
    """Read and parse a JSON file."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return _json.load(f)
    except FileNotFoundError:
        raise RuntimeError(f"[Frankie] JSON file not found: {path!r}")
    except _json.JSONDecodeError as e:
        raise RuntimeError(f"[Frankie] JSON parse error in {path!r}: {e}")

def json_write(path, obj, pretty=False):
    """Serialize and write a Frankie value to a JSON file."""
    indent = 2 if pretty else None
    with open(path, 'w', encoding='utf-8') as f:
        _json.dump(obj, f, indent=indent, default=str)
    return True


# ─── CSV ──────────────────────────────────────────────────────────────────────
import csv as _csv
import io as _io

def csv_parse(text, headers=True):
    """Parse CSV text → vector of hashes (with headers) or vector of vectors."""
    reader = _csv.reader(_io.StringIO(text))
    rows = list(reader)
    if not rows:
        return []
    if headers:
        keys = rows[0]
        return [dict(zip(keys, row)) for row in rows[1:]]
    return rows

def csv_dump(data, headers=None):
    """Serialize vector of hashes (or vectors) → CSV string."""
    buf = _io.StringIO()
    if not data:
        return ""
    if isinstance(data[0], dict):
        keys = headers or list(data[0].keys())
        w = _csv.DictWriter(buf, fieldnames=keys)
        w.writeheader()
        w.writerows(data)
    else:
        w = _csv.writer(buf)
        if headers:
            w.writerow(headers)
        w.writerows(data)
    return buf.getvalue()

def csv_read(path, headers=True):
    """Read and parse a CSV file."""
    try:
        with open(path, 'r', encoding='utf-8', newline='') as f:
            return csv_parse(f.read(), headers=headers)
    except FileNotFoundError:
        raise RuntimeError(f"[Frankie] CSV file not found: {path!r}")

def csv_write(path, data, headers=None):
    """Write vector of hashes or vectors to a CSV file."""
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(csv_dump(data, headers=headers))
    return True


# ─── DateTime ─────────────────────────────────────────────────────────────────
import datetime as _dt

class FrankieDate:
    """Frankie date/time object."""

    def __init__(self, dt):
        self._dt = dt

    # Accessors
    @property
    def year(self):   return self._dt.year
    @property
    def month(self):  return self._dt.month
    @property
    def day(self):    return self._dt.day
    @property
    def hour(self):   return self._dt.hour if hasattr(self._dt, 'hour') else 0
    @property
    def minute(self): return self._dt.minute if hasattr(self._dt, 'minute') else 0
    @property
    def second(self): return self._dt.second if hasattr(self._dt, 'second') else 0

    def format(self, fmt="%Y-%m-%d %H:%M:%S"):
        """Format using strftime directives."""
        return self._dt.strftime(fmt)

    def to_s(self):
        return str(self._dt)

    def add_days(self, n):
        return FrankieDate(self._dt + _dt.timedelta(days=n))

    def add_hours(self, n):
        return FrankieDate(self._dt + _dt.timedelta(hours=n))

    def add_minutes(self, n):
        return FrankieDate(self._dt + _dt.timedelta(minutes=n))

    def diff_days(self, other):
        """Days between this and another FrankieDate."""
        delta = self._dt - other._dt
        return abs(delta.days)

    def diff_seconds(self, other):
        delta = self._dt - other._dt
        return abs(int(delta.total_seconds()))

    def weekday(self):
        """0=Monday ... 6=Sunday"""
        return self._dt.weekday()

    def weekday_name(self):
        return self._dt.strftime("%A")

    def is_before(self, other):
        return self._dt < other._dt

    def is_after(self, other):
        return self._dt > other._dt

    def timestamp(self):
        """Unix timestamp as float."""
        return self._dt.timestamp()

    # ── Arithmetic operators ───────────────────────────────────────────────
    def __add__(self, other):
        """date + n  →  date advanced by n days (int) or timedelta."""
        if isinstance(other, int):
            return FrankieDate(self._dt + _dt.timedelta(days=other))
        if isinstance(other, float):
            return FrankieDate(self._dt + _dt.timedelta(days=other))
        if isinstance(other, _dt.timedelta):
            return FrankieDate(self._dt + other)
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        """date - n  →  date moved back n days.
           date - date  →  integer number of days between them."""
        if isinstance(other, (int, float)):
            return FrankieDate(self._dt - _dt.timedelta(days=other))
        if isinstance(other, _dt.timedelta):
            return FrankieDate(self._dt - other)
        if isinstance(other, FrankieDate):
            return (self._dt - other._dt).days   # signed integer
        return NotImplemented

    # ── Comparison operators ───────────────────────────────────────────────
    def __eq__(self, other):
        return isinstance(other, FrankieDate) and self._dt == other._dt

    def __lt__(self, other):
        return isinstance(other, FrankieDate) and self._dt < other._dt

    def __le__(self, other):
        return isinstance(other, FrankieDate) and self._dt <= other._dt

    def __gt__(self, other):
        return isinstance(other, FrankieDate) and self._dt > other._dt

    def __ge__(self, other):
        return isinstance(other, FrankieDate) and self._dt >= other._dt

    def __repr__(self):
        return f"Date({self._dt})"


def now():
    """Current date and time."""
    return FrankieDate(_dt.datetime.now())

def today():
    """Today's date (midnight)."""
    return FrankieDate(_dt.datetime.combine(_dt.date.today(), _dt.time()))

def date_parse(s, fmt="%Y-%m-%d"):
    """Parse a date string."""
    try:
        return FrankieDate(_dt.datetime.strptime(s, fmt))
    except ValueError as e:
        raise RuntimeError(f"[Frankie] Date parse error: {e}")

def date_from(year, month, day, hour=0, minute=0, second=0):
    """Create a date from components."""
    return FrankieDate(_dt.datetime(int(year), int(month), int(day),
                                    int(hour), int(minute), int(second)))

def _fk_date_to_str(obj):
    """Hook for _fk_to_str to handle FrankieDate."""
    if hasattr(obj, 'format') and hasattr(obj, 'year'):
        return obj.to_s()
    return str(obj)


# ─── HTTP ─────────────────────────────────────────────────────────────────────
import urllib.request as _urllib_req
import urllib.parse   as _urllib_parse
import urllib.error   as _urllib_err

class FrankieHTTPResponse:
    """HTTP response object."""
    def __init__(self, status, body, headers):
        self.status  = status
        self.body    = body
        self.headers = headers

    def json(self):
        """Parse body as JSON."""
        return _json.loads(self.body)

    def ok(self):
        """True if status is 2xx."""
        return 200 <= self.status < 300

    def __repr__(self):
        return f"HTTPResponse({self.status}, {len(self.body)} bytes)"


def _build_request(url, method, data=None, headers=None):
    hdrs = {'User-Agent': 'Frankie/1.3', 'Accept': 'application/json, */*'}
    if headers:
        hdrs.update(headers)
    body = None
    if data is not None:
        if isinstance(data, (dict, list)):
            body = _json.dumps(data).encode('utf-8')
            hdrs['Content-Type'] = 'application/json'
        else:
            body = str(data).encode('utf-8')
            hdrs.setdefault('Content-Type', 'text/plain')
    req = _urllib_req.Request(url, data=body, headers=hdrs, method=method)
    return req


def http_get(url, headers=None):
    """Make an HTTP GET request. Returns FrankieHTTPResponse."""
    try:
        req = _build_request(url, 'GET', headers=headers)
        with _urllib_req.urlopen(req, timeout=30) as resp:
            return FrankieHTTPResponse(
                resp.status,
                resp.read().decode('utf-8', errors='replace'),
                dict(resp.headers)
            )
    except _urllib_err.HTTPError as e:
        return FrankieHTTPResponse(e.code, e.read().decode('utf-8', errors='replace'), {})
    except Exception as e:
        raise RuntimeError(f"[Frankie] HTTP GET error: {e}")


def http_post(url, data=None, headers=None):
    """Make an HTTP POST request."""
    try:
        req = _build_request(url, 'POST', data=data, headers=headers)
        with _urllib_req.urlopen(req, timeout=30) as resp:
            return FrankieHTTPResponse(
                resp.status,
                resp.read().decode('utf-8', errors='replace'),
                dict(resp.headers)
            )
    except _urllib_err.HTTPError as e:
        return FrankieHTTPResponse(e.code, e.read().decode('utf-8', errors='replace'), {})
    except Exception as e:
        raise RuntimeError(f"[Frankie] HTTP POST error: {e}")


def http_put(url, data=None, headers=None):
    """Make an HTTP PUT request."""
    try:
        req = _build_request(url, 'PUT', data=data, headers=headers)
        with _urllib_req.urlopen(req, timeout=30) as resp:
            return FrankieHTTPResponse(resp.status, resp.read().decode('utf-8', errors='replace'), dict(resp.headers))
    except _urllib_err.HTTPError as e:
        return FrankieHTTPResponse(e.code, e.read().decode('utf-8', errors='replace'), {})
    except Exception as e:
        raise RuntimeError(f"[Frankie] HTTP PUT error: {e}")


def http_delete(url, headers=None):
    """Make an HTTP DELETE request."""
    try:
        req = _build_request(url, 'DELETE', headers=headers)
        with _urllib_req.urlopen(req, timeout=30) as resp:
            return FrankieHTTPResponse(resp.status, resp.read().decode('utf-8', errors='replace'), dict(resp.headers))
    except _urllib_err.HTTPError as e:
        return FrankieHTTPResponse(e.code, e.read().decode('utf-8', errors='replace'), {})
    except Exception as e:
        raise RuntimeError(f"[Frankie] HTTP DELETE error: {e}")


def url_encode(params):
    """Encode a hash as URL query string."""
    return _urllib_parse.urlencode(params)

def url_decode(s):
    """Decode a URL query string → hash."""
    return dict(_urllib_parse.parse_qsl(s))


# ─── Web Server ───────────────────────────────────────────────────────────────

import http.server as _http_server
import mimetypes as _mimetypes
import re as _re
import threading as _threading


class _HaltException(Exception):
    """Raised by halt() to short-circuit request processing."""
    def __init__(self, response):
        self.response = response


class FrankieRequest:
    """
    Represents an incoming HTTP request inside a route handler.

    Properties
    ----------
    method   : "GET", "POST", "PUT", "DELETE", ...
    path     : "/hello/world"
    params   : path parameters extracted from the route pattern  {id: "42"}
    query    : query-string parameters as a hash  {page: "2"}
    headers  : request headers as a hash
    body     : raw request body as a string
    json     : parsed JSON body (hash/vector) or nil
    form     : parsed application/x-www-form-urlencoded body as a hash
    """
    def __init__(self, method, path, params, query, headers, body):
        self.method   = method
        self.path     = path
        self.params   = params
        self.query    = query
        self.headers  = headers
        self.body     = body
        # Eagerly parsed so Frankie can access them as plain attributes
        self.json     = self._parse_json(body)
        self.form     = dict(_urllib_parse.parse_qsl(body))
        self._cookies = self._parse_cookies(headers)

    def cookies(self):
        """Return the parsed Cookie header as a hash of {name: value} pairs.

        Called as req.cookies in Frankie (the compiler adds parens for method calls).
        """
        return self._cookies

    @staticmethod
    def _parse_json(body):
        try:
            import json as _j
            return _j.loads(body)
        except Exception:
            return None

    @staticmethod
    def _parse_cookies(headers):
        raw = headers.get('Cookie', '') or headers.get('cookie', '') or ''
        result = {}
        for part in raw.split(';'):
            part = part.strip()
            if '=' in part:
                k, _, v = part.partition('=')
                result[k.strip()] = v.strip()
        return result

    def __repr__(self):
        return f"<FrankieRequest {self.method} {self.path}>"

    def query_int(self, key, default=None):
        """Get a query param as an integer, or default if missing/invalid."""
        val = self.query.get(str(key))
        if val is None:
            return default
        try:
            return int(val)
        except (ValueError, TypeError):
            return default

    def query_float(self, key, default=None):
        """Get a query param as a float, or default if missing/invalid."""
        val = self.query.get(str(key))
        if val is None:
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    def query_bool(self, key, default=False):
        """Get a query param as a boolean.
        'true', '1', 'yes' → True; 'false', '0', 'no' → False."""
        val = self.query.get(str(key))
        if val is None:
            return default
        return val.lower() in ('true', '1', 'yes')


class FrankieResponse:
    """
    An HTTP response returned from a route handler.

    Use the helper functions below instead of constructing this directly:
      response(body)                          -> 200 text/plain
      response(body, 201)                     -> custom status
      json_response(hash)                     -> 200 application/json
      html_response(html)                     -> 200 text/html
      redirect("/other")                      -> 302 redirect
      halt(404, "Not Found")                  -> error shortcut
    """
    def __init__(self, body="", status=200, headers=None, content_type="text/plain; charset=utf-8"):
        self.body         = str(body) if body is not None else ""
        self.status       = int(status)
        self.content_type = content_type
        self.headers      = headers or {}

    def set_cookie(self, name, value, opts=None):
        """Append a Set-Cookie header to this response.

        opts is an optional Frankie hash with keys:
          path      (default "/")
          http_only (default true)
          max_age   (default nil — omitted)
          same_site (default "Lax")
        """
        if opts is None:
            opts = {}
        path      = opts.get('path',      opts.get('path',      '/'))
        http_only = opts.get('http_only', opts.get('http_only', True))
        max_age   = opts.get('max_age',   opts.get('max_age',   None))
        same_site = opts.get('same_site', opts.get('same_site', 'Lax'))
        cookie = f"{name}={value}; Path={path}; SameSite={same_site}"
        if max_age is not None:
            cookie += f"; Max-Age={max_age}"
        if http_only:
            cookie += "; HttpOnly"
        # Collect multiple Set-Cookie values as a list
        existing = self.headers.get('Set-Cookie')
        if existing is None:
            self.headers['Set-Cookie'] = cookie
        elif isinstance(existing, list):
            existing.append(cookie)
        else:
            self.headers['Set-Cookie'] = [existing, cookie]
        return self

    def set_header(self, name, value):
        """Set an arbitrary response header."""
        self.headers[name] = value
        return self

    def __repr__(self):
        return f"<FrankieResponse {self.status}>"


def response(body="", status=200, headers=None):
    """Return a plain-text HTTP response."""
    return FrankieResponse(body, status, headers or {}, "text/plain; charset=utf-8")

def json_response(data, status=200, headers=None):
    """Serialize data as JSON and return an application/json response."""
    import json as _j
    return FrankieResponse(
        _j.dumps(data, ensure_ascii=False),
        status,
        headers or {},
        "application/json; charset=utf-8"
    )

def html_response(body="", status=200, headers=None):
    """Return a text/html response."""
    return FrankieResponse(body, status, headers or {}, "text/html; charset=utf-8")

def redirect(location, status=302):
    """Return a redirect response."""
    return FrankieResponse("", status, {"Location": location}, "text/plain")

def halt(status=500, body=""):
    """Short-circuit the current request with an error response.

    When called from a before-filter, immediately stops the request pipeline
    and sends this response to the client — the route handler is never called.
    When called from a route handler, terminates the handler early.
    """
    raise _HaltException(FrankieResponse(body, status, {}, "text/plain; charset=utf-8"))


_SESSION_COOKIE = "_fk_session"

class FrankieSession:
    """Cookie-backed session — a hash you can read, mutate, and save.

    Obtained via session(req, resp) in a route handler.  All data is stored
    as a single JSON-encoded cookie (_fk_session).  No server-side state.

    Usage:
        s = session(req, resp)
        user_id = s["user_id"]
        s["user_id"] = 42
        s.save()
    """
    def __init__(self, data: dict, resp: "FrankieResponse"):
        self._data = data
        self._resp = resp

    # Hash-style read access
    def __getitem__(self, key):
        return self._data.get(str(key))

    # Hash-style write access
    def __setitem__(self, key, value):
        self._data[str(key)] = value

    def get(self, key, default=None):
        return self._data.get(str(key), default)

    def has_key(self, key):
        return str(key) in self._data

    def keys(self):
        return list(self._data.keys())

    def values(self):
        return list(self._data.values())

    def delete(self, key):
        self._data.pop(str(key), None)

    def clear(self):
        self._data.clear()

    def save(self):
        """Serialize session data back to the response cookie."""
        import json as _json
        raw = _json.dumps(self._data, separators=(',', ':'))
        self._resp.set_cookie(
            _SESSION_COOKIE, raw,
            {"http_only": True, "same_site": "Lax", "path": "/"}
        )
        return self

    def to_hash(self):
        return dict(self._data)

    def __repr__(self):
        return f"<FrankieSession {self._data!r}>"


def session(req, resp):
    """Read the cookie-backed session for this request.

    Returns a FrankieSession that wraps the decoded session hash.
    Call .save() to write the updated session back to the response.

        s = session(req, resp)
        s["user"] = "alice"
        s.save()

    The session is stored as a single JSON cookie (_fk_session).
    It is not encrypted — do not store secrets in it.
    """
    import json as _json
    cookies = req._cookies if hasattr(req, '_cookies') else {}
    raw = cookies.get(_SESSION_COOKIE, "")
    try:
        data = _json.loads(raw) if raw else {}
        if not isinstance(data, dict):
            data = {}
    except Exception:
        data = {}
    return FrankieSession(data, resp)


class FrankieStaticResponse(FrankieResponse):
    """FrankieResponse variant that carries raw bytes for static file serving."""
    def __init__(self, data, content_type):
        super().__init__("", 200, {}, content_type)
        self._bytes = data

    def raw_bytes(self):
        """Return the raw bytes of the static file body."""
        return self._bytes


class FrankieApp:
    """
    A lightweight HTTP application in the style of Sinatra / Camping.

    Routes are registered with .get, .post, .put, .delete, .patch.
    Path parameters are declared with :name segments, e.g. "/users/:id".
    The handler block receives a FrankieRequest and must return a
    FrankieResponse (or a plain string / hash, which is wrapped automatically).

    Example (Frankie source)
    ------------------------
        app = web_app()

        app.get("/") do |req|
          html_response("<h1>Hello from Frankie!</h1>")
        end

        app.get("/greet/:name") do |req|
          name = req.params["name"]
          response("Hello, #{name}!")
        end

        app.run(3000)
    """

    def __init__(self):
        self._routes    = []   # [(method, regex, param_names, handler), ...]
        self._before    = []   # before-filters
        self._after     = []   # after-filters
        self._not_found = None # custom 404 handler
        self._static    = []   # [(url_prefix, fs_root), ...]
        self._middleware = []  # [(handler,), ...] — app.use stack
        self._ws_routes = []   # v1.18: [(regex, param_names, handler), ...]

    # ── Route registration ──────────────────────────────────────────────────

    def _register(self, method, pattern, handler):
        param_names = _re.findall(r':([a-zA-Z_][a-zA-Z0-9_]*)', pattern)
        regex_str   = _re.sub(r':([a-zA-Z_][a-zA-Z0-9_]*)', r'([^/]+)', pattern)
        self._routes.append((method.upper(), _re.compile('^' + regex_str + '$'), param_names, handler))

    def get(self, pattern, handler):    self._register('GET',    pattern, handler)
    def post(self, pattern, handler):   self._register('POST',   pattern, handler)
    def put(self, pattern, handler):    self._register('PUT',    pattern, handler)
    def delete(self, pattern, handler): self._register('DELETE', pattern, handler)
    def patch(self, pattern, handler):  self._register('PATCH',  pattern, handler)

    def websocket(self, pattern, handler):
        """v1.18: app.websocket("/ws/:room") do |ws| ... end

        The handler receives a FrankieWebSocket with .send / .recv / .close,
        plus .params (path parameters) and .path. It runs in its own thread;
        the connection closes automatically when the handler returns.
        """
        param_names = _re.findall(r':([a-zA-Z_][a-zA-Z0-9_]*)', pattern)
        regex_str   = _re.sub(r':([a-zA-Z_][a-zA-Z0-9_]*)', r'([^/]+)', pattern)
        self._ws_routes.append((_re.compile('^' + regex_str + '$'),
                                param_names, handler))

    def _match_ws(self, path):
        for regex, param_names, handler in self._ws_routes:
            m = regex.match(path)
            if m:
                return dict(zip(param_names, m.groups())), handler
        return None, None

    # Async route variants — in Frankie's threading model each request already
    # runs in its own thread, so async routes are identical to sync ones.
    def get_async(self, pattern, handler):    self._register('GET',    pattern, handler)
    def post_async(self, pattern, handler):   self._register('POST',   pattern, handler)
    def put_async(self, pattern, handler):    self._register('PUT',    pattern, handler)
    def delete_async(self, pattern, handler): self._register('DELETE', pattern, handler)
    def patch_async(self, pattern, handler):  self._register('PATCH',  pattern, handler)

    def use(self, handler):
        """Register middleware.  handler(req, next_fn) -> response.
        Call next_fn(req) to pass control to the next layer.
        Return a response directly to short-circuit the chain.
        """
        self._middleware.append(handler)

    def before(self, handler):
        """Register a before-filter (called before every matched route)."""
        self._before.append(handler)

    def after(self, handler):
        """Register an after-filter (called after every matched route)."""
        self._after.append(handler)

    def not_found(self, handler):
        """Register a custom 404 handler."""
        self._not_found = handler

    def static(self, fs_root_or_prefix, fs_root=None):
        """Serve files from a directory.

        One-argument form:   app.static("./public")        → served at /
        Two-argument form:   app.static("./assets", "/static")  → served at /static/
        """
        if fs_root is None:
            # 1-arg: app.static("./public") — serve at /
            url_prefix = '/'
            fs_root    = fs_root_or_prefix
        else:
            # 2-arg: app.static("/static", "./assets")
            url_prefix = fs_root_or_prefix
        if not url_prefix.startswith('/'):
            url_prefix = '/' + url_prefix
        self._static.append((url_prefix.rstrip('/'), _os.path.abspath(fs_root)))

    # ── Dispatch ────────────────────────────────────────────────────────────

    def _dispatch(self, method, path, query_string, headers, body):
        query = dict(_urllib_parse.parse_qsl(query_string))
        try:
            # Build the middleware chain around _dispatch_inner
            def inner(req):
                return self._dispatch_inner(req.method, req.path, req.query,
                                            req.headers, req.body)

            if self._middleware:
                # Build chain from inside out
                chain = inner
                for mw in reversed(self._middleware):
                    outer_chain = chain
                    def make_layer(handler, next_fn):
                        def layer(req):
                            return handler(req, next_fn)
                        return layer
                    chain = make_layer(mw, outer_chain)
                req = FrankieRequest(method, path, {}, query, headers, body)
                result = chain(req)
            else:
                result = self._dispatch_inner(method, path, query, headers, body)
            return result
        except _HaltException as _h:
            return _h.response

    def _dispatch_inner(self, method, path, query, headers, body):

        # Static file serving — checked before dynamic routes
        if method in ('GET', 'HEAD'):
            for url_prefix, fs_root in self._static:
                if path == url_prefix or path.startswith(url_prefix + '/'):
                    rel      = path[len(url_prefix):].lstrip('/')
                    abs_path = _os.path.join(fs_root, rel)
                    abs_path = _os.path.normpath(abs_path)
                    # Prevent directory traversal
                    if not abs_path.startswith(fs_root):
                        return FrankieResponse("403 Forbidden", 403, {}, "text/plain")
                    if _os.path.isfile(abs_path):
                        mime, _ = _mimetypes.guess_type(abs_path)
                        mime    = mime or 'application/octet-stream'
                        with open(abs_path, 'rb') as _fh:
                            data = _fh.read()
                        resp = FrankieStaticResponse(data, mime)
                        return resp
                    return FrankieResponse("404 Not Found", 404, {}, "text/plain")

        for route_method, regex, param_names, handler in self._routes:
            if route_method != method and not (method == 'HEAD' and route_method == 'GET'):
                continue
            m = regex.match(path)
            if m:
                params = dict(zip(param_names, m.groups()))
                req    = FrankieRequest(method, path, params, query, headers, body)
                for bf in self._before:
                    bf(req)
                raw  = handler(req)
                resp = self._wrap(raw)
                for af in self._after:
                    af(req, resp)
                return resp

        # No route matched -> 404
        if self._not_found:
            req = FrankieRequest(method, path, {}, query, headers, body)
            return self._wrap(self._not_found(req))
        return FrankieResponse("404 Not Found", 404, {}, "text/plain; charset=utf-8")

    @staticmethod
    def _wrap(raw):
        """Coerce handler return value to a FrankieResponse."""
        if isinstance(raw, FrankieResponse):
            return raw
        if isinstance(raw, (dict, list)):
            import json as _j
            return FrankieResponse(_j.dumps(raw, ensure_ascii=False), 200, {},
                                   "application/json; charset=utf-8")
        return FrankieResponse(str(raw) if raw is not None else "", 200, {},
                               "text/plain; charset=utf-8")

    # ── Server ──────────────────────────────────────────────────────────────

    def run(self, port=3000, host="0.0.0.0"):
        """Start the blocking HTTP server. Press Ctrl+C to stop."""
        app = self

        class _Handler(_http_server.BaseHTTPRequestHandler):
            def log_message(self, fmt, *args):
                print(f"  {self.address_string()}  {fmt % args}")

            def _serve(self):
                import urllib.parse as _up
                parsed  = _up.urlparse(self.path)

                # v1.18: WebSocket upgrade — hijack the connection
                if (self.command == 'GET'
                        and 'websocket' in self.headers.get('Upgrade', '').lower()
                        and 'upgrade' in self.headers.get('Connection', '').lower()):
                    params, ws_handler = app._match_ws(parsed.path)
                    if ws_handler is not None:
                        _fk_ws_serve_upgrade(self, parsed.path, params, ws_handler)
                        self.close_connection = True
                        return
                    self.send_response(404)
                    self.end_headers()
                    return

                length  = int(self.headers.get('Content-Length', 0))
                body    = self.rfile.read(length).decode('utf-8', errors='replace') if length else ''
                resp    = app._dispatch(self.command, parsed.path,
                                        parsed.query, dict(self.headers), body)
                encoded = resp._bytes if isinstance(resp, FrankieStaticResponse) else resp.body.encode('utf-8')
                self.send_response(resp.status)
                self.send_header('Content-Type', resp.content_type)
                self.send_header('Content-Length', str(len(encoded)))
                for k, v in resp.headers.items():
                    if isinstance(v, list):
                        for item in v:
                            self.send_header(k, item)
                    else:
                        self.send_header(k, v)
                self.end_headers()
                if self.command != 'HEAD':
                    self.wfile.write(encoded)

            def do_GET(self):    self._serve()
            def do_POST(self):   self._serve()
            def do_PUT(self):    self._serve()
            def do_DELETE(self): self._serve()
            def do_PATCH(self):  self._serve()
            def do_HEAD(self):   self._serve()

        server = _http_server.ThreadingHTTPServer((host, int(port)), _Handler)
        print(f"🧟 Frankie web server running on http://{host}:{port}")
        print(f"   Press Ctrl+C to stop.\n")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n   Shutting down.")
            server.shutdown()


def _fk_tmpl_escape(s):
    """HTML-escape a string for safe output."""
    s = str(s) if s is not None else ''
    return (s.replace('&', '&amp;')
             .replace('<', '&lt;')
             .replace('>', '&gt;')
             .replace('"', '&quot;')
             .replace("'", '&#39;'))


def _fk_tmpl_lookup(data, key):
    """Look up key in data dict; return None if missing."""
    key = key.strip()
    if isinstance(data, dict):
        return data.get(key)
    return None


def _fk_tmpl_render(tmpl, data):
    """Core Mustache-compatible renderer.

    Supports:
      {{ var }}             — HTML-escaped interpolation
      {{{ var }}}           — raw unescaped interpolation
      {{# section }}...{{/ section }} — truthy block / vector iteration
      {{^ inverted }}...{{/ inverted }} — falsy / empty block
      {{! comment }}        — stripped from output
    """
    import re as _re

    # Strip comments
    tmpl = _re.sub(r'\{\{![^}]*\}\}', '', tmpl)

    # Sections {{# key }} ... {{/ key }}
    def render_section(m):
        key = m.group(1).strip()
        inner = m.group(2)
        value = _fk_tmpl_lookup(data, key)
        if value is None or value is False:
            return ''
        if isinstance(value, list):
            out = []
            for item in value:
                merged = dict(data, **item) if isinstance(item, dict) else data
                out.append(_fk_tmpl_render(inner, merged))
            return ''.join(out)
        if value is True or isinstance(value, (dict, str, int, float)):
            merged = dict(data, **value) if isinstance(value, dict) else data
            return _fk_tmpl_render(inner, merged)
        return ''

    tmpl = _re.sub(
        r'\{\{#\s*(\w+)\s*\}\}([\s\S]*?)\{\{/\s*\1\s*\}\}',
        render_section, tmpl)

    # Inverted sections {{^ key }} ... {{/ key }}
    def render_inverted(m):
        key = m.group(1).strip()
        inner = m.group(2)
        value = _fk_tmpl_lookup(data, key)
        if value is None or value is False or (isinstance(value, list) and len(value) == 0):
            return _fk_tmpl_render(inner, data)
        return ''

    tmpl = _re.sub(
        r'\{\{\^\s*(\w+)\s*\}\}([\s\S]*?)\{\{/\s*\1\s*\}\}',
        render_inverted, tmpl)

    # Triple mustache {{{ var }}} — raw output
    def raw_var(m):
        key = m.group(1).strip()
        val = _fk_tmpl_lookup(data, key)
        return '' if val is None else str(val)

    tmpl = _re.sub(r'\{\{\{([^}]+)\}\}\}', raw_var, tmpl)

    # Double mustache {{ var }} — HTML-escaped
    def escaped_var(m):
        key = m.group(1).strip()
        val = _fk_tmpl_lookup(data, key)
        return '' if val is None else _fk_tmpl_escape(val)

    tmpl = _re.sub(r'\{\{([^#\^/>{!][^}]*)\}\}', escaped_var, tmpl)

    return tmpl


def render(template_str_or_path, data=None):
    """Render a Mustache-compatible template string with a data hash.

    render(template, data)       — render a string template
    render(path, data)           — kept for backward compat: if it looks like a
                                   file path (contains / or ends with .html/.mustache),
                                   reads the file first.

    Syntax:
      {{ var }}               HTML-escaped interpolation
      {{{ var }}}             raw / unescaped interpolation
      {{# section }}...{{/ section }}   truthy block or vector iteration
      {{^ inverted }}...{{/ inverted }}  falsy / empty block
      {{! comment }}          stripped from output

    Example:
        tmpl = \"Hello, {{ name }}! You have {{ count }} messages.\"
        puts render(tmpl, {name: \"Alice\", count: 7})
    """
    import os as _os
    d = data or {}
    s = template_str_or_path
    # Treat as a file path only if it looks like an actual path:
    # no newlines, no spaces, no < or > (rules out HTML), and either
    # has a recognised extension or contains an OS path separator.
    is_path = (
        '\n' not in s
        and ' ' not in s
        and '<' not in s
        and '>' not in s
        and '{' not in s
        and (s.endswith('.html') or s.endswith('.mustache')
             or _os.sep in s)
    )
    if is_path:
        with open(s, 'r', encoding='utf-8') as _fh:
            s = _fh.read()
        return html_response(_fk_tmpl_render(s, d))
    return _fk_tmpl_render(s, d)


def render_file(path, data=None):
    """Load a template file and render it with a data hash.

    Returns the rendered string (not a response object).
    Use html_response(render_file(...)) inside a route handler.

    Example:
        html = render_file(\"./views/dashboard.html\", {name: user[\"name\"]})
        html_response(html)
    """
    with open(path, 'r', encoding='utf-8') as _fh:
        tmpl = _fh.read()
    return _fk_tmpl_render(tmpl, data or {})


def web_app():
    """Create and return a new Frankie web application.

    Features
    --------
    Routing       app.get / .post / .put / .delete / .patch(pattern, handler)
    Middleware    app.before(fn)  — return a FrankieResponse to short-circuit
                  app.after(fn)  — inspect/mutate the response
    Static files  app.static(url_prefix, fs_root)
    Custom 404    app.not_found(fn)

    Request properties
    ------------------
    req.method / .path / .params / .query / .headers / .body / .json / .form
    req.cookies   — parsed Cookie header as a hash

    Response helpers
    ----------------
    response(body, status)      html_response(html)
    json_response(hash)         redirect(location)   halt(status, body)
    render(path, data)          — fill a .html file with {{key}} placeholders
    resp.set_cookie(name, val)  — append a Set-Cookie header
    resp.set_header(name, val)  — set an arbitrary response header
    """
    return FrankieApp()


# ─── v1.5: Randomness ────────────────────────────────────────────────────────

import random as _random

def random():
    """Return a random Float between 0.0 (inclusive) and 1.0 (exclusive)."""
    return _random.random()

def rand(n=None):
    """
    rand()    -> random Float 0.0..1.0
    rand(n)   -> random Integer 0...n  (exclusive upper bound)
    rand(a,b) -> not supported yet; use rand(b-a)+a
    """
    if n is None:
        return _random.random()
    return _random.randrange(int(n))

def rand_float(a, b):
    """Return a random Float in [a, b)."""
    return _random.uniform(float(a), float(b))

def rand_int(a, b):
    """Return a random Integer in [a, b] (both inclusive)."""
    return _random.randint(int(a), int(b))

def shuffle(vec):
    """Return a new shuffled copy of the vector."""
    if not isinstance(vec, list):
        raise RuntimeError("[Frankie] shuffle() requires a vector")
    result = list(vec)
    _random.shuffle(result)
    return result

def sample(vec, n=1):
    """Return n randomly chosen elements from vec (no repeats)."""
    if not isinstance(vec, list):
        raise RuntimeError("[Frankie] sample() requires a vector")
    return _random.sample(vec, int(n))

def rand_seed(n):
    """Seed the random number generator for reproducible results."""
    _random.seed(n)
    return n


# ─── v1.5: Sleep ─────────────────────────────────────────────────────────────

import time as _time

def sleep(seconds):
    """Pause execution for the given number of seconds (float ok)."""
    _time.sleep(float(seconds))
    return seconds


# ─── v1.10: New helpers ───────────────────────────────────────────────────────

def times(n, fn=None):
    """Standalone times(n) — call fn(i) for i in 0..n-1, or return list(range(n))."""
    if fn is None:
        return list(range(int(n)))
    for i in range(int(n)):
        fn(i)


def pp(val, _indent=0):
    """Pretty-print a value with indented multiline output for nested structures."""
    pad  = "  " * _indent
    pad2 = "  " * (_indent + 1)
    if isinstance(val, dict):
        if not val:
            print(pad + "{}")
            return
        if "__type__" in val:
            type_name = val["__type__"]
            fields = {k: v for k, v in val.items() if k != "__type__"}
            if not fields:
                print(pad + f"{type_name}()")
                return
            print(pad + f"{type_name}(")
            items = list(fields.items())
            for i, (k, v) in enumerate(items):
                comma = "," if i < len(items) - 1 else ""
                if isinstance(v, (dict, list)) and v:
                    print(pad2 + f"{k}:")
                    pp(v, _indent + 2)
                else:
                    print(pad2 + f"{k}: {_fk_to_str(v)}{comma}")
            print(pad + ")")
        else:
            print(pad + "{")
            items = list(val.items())
            for i, (k, v) in enumerate(items):
                comma = "," if i < len(items) - 1 else ""
                if isinstance(v, (dict, list)) and v:
                    print(pad2 + f"{k}:")
                    pp(v, _indent + 2)
                else:
                    print(pad2 + f"{k}: {_fk_to_str(v)}{comma}")
            print(pad + "}")
    elif isinstance(val, list):
        if not val:
            print(pad + "[]")
            return
        if all(not isinstance(e, (dict, list)) for e in val):
            print(pad + "[" + ", ".join(_fk_to_str(e) for e in val) + "]")
        else:
            print(pad + "[")
            for e in val:
                pp(e, _indent + 1)
            print(pad + "]")
    else:
        print(pad + _fk_to_str(val))


def _fk_flatten_deep(iterable, depth):
    """Flatten up to depth levels. depth=None means fully recursive."""
    result = []
    for item in iterable:
        if isinstance(item, list) and depth != 0:
            next_depth = None if depth is None else depth - 1
            result.extend(_fk_flatten_deep(item, next_depth))
        else:
            result.append(item)
    return result


def _fk_map_with_index(iterable, fn):
    """Map with index: fn(element, index) → new vector."""
    return [fn(x, i) for i, x in enumerate(iterable)]


def _fk_str_encode(s, encoding='utf-8'):
    """Encode a string to a vector of byte integers."""
    return list(s.encode(encoding))


def _fk_str_decode(byte_vec, encoding='utf-8'):
    """Decode a vector of byte integers back to a string."""
    return bytes(byte_vec).decode(encoding)




# ─── v1.5: Sort helpers ───────────────────────────────────────────────────────

def _fk_sort_by(vec, key_fn):
    """sort_by do |x| ... end — sort by the value the block returns."""
    items = list(_fk_iter(vec))
    return sorted(items, key=key_fn)

def _fk_min_by(vec, key_fn):
    """min_by do |x| ... end — element with the smallest key."""
    items = list(_fk_iter(vec))
    return min(items, key=key_fn)

def _fk_max_by(vec, key_fn):
    """max_by do |x| ... end — element with the largest key."""
    items = list(_fk_iter(vec))
    return max(items, key=key_fn)

def _fk_sum_by(vec, key_fn):
    """sum_by do |x| ... end — sum the values the block returns."""
    return sum(key_fn(x) for x in _fk_iter(vec))


# ─── v1.5: Unzip ─────────────────────────────────────────────────────────────

def unzip(vec):
    """
    Inverse of zip: a vector of [a, b] pairs → [all_as, all_bs].
    unzip([[1,"a"],[2,"b"]]) -> [[1,2],["a","b"]]
    """
    if not isinstance(vec, list) or not vec:
        return []
    width = len(vec[0]) if isinstance(vec[0], list) else 2
    return [[row[i] for row in vec] for i in range(width)]


# ─── v1.5: format alias ───────────────────────────────────────────────────────

def format(fmt, *args, **kwargs):
    """Alias for sprintf — format a string with positional or named values."""
    return sprintf(fmt, *args, **kwargs)


# ─── v1.5: Constants ─────────────────────────────────────────────────────────

_fk_constants = {}

def _fk_const_set(name, value):
    """
    Called by ConstAssign codegen.
    First assignment stores the value. Subsequent assignments warn and
    return the original value (constants are immutable by convention).
    """
    if name in _fk_constants:
        import sys as _sys2
        print(f"[Frankie] Warning: reassignment of constant {name}", file=_sys2.stderr)
        return _fk_constants[name]   # preserve original value
    _fk_constants[name] = value
    return value


# ─── Test harness (frankiec test) ─────────────────────────────────────────────

class _FKTestSuite:
    """Lightweight test harness — zero external dependencies."""

    def __init__(self):
        self._pass = 0
        self._fail = 0
        self._skipped = 0   # v1.17: groups skipped by --filter / --tag
        self._errors = []

    def assert_true(self, value, msg=None):
        label = msg or "assertion"
        if value:
            self._pass += 1
            print(f"  \033[32m✓\033[0m  {label}")
        else:
            self._fail += 1
            self._errors.append(label)
            print(f"  \033[31m✗\033[0m  {label}")

    def assert_eq(self, actual, expected, msg=None):
        ok = actual == expected
        if ok:
            self._pass += 1
            label = msg or f"{actual!r} == {expected!r}"
            print(f"  \033[32m✓\033[0m  {label}")
        else:
            self._fail += 1
            label = msg or f"expected {expected!r}, got {actual!r}"
            self._errors.append(label)
            print(f"  \033[31m✗\033[0m  {label}")

    def assert_neq(self, actual, expected, msg=None):
        ok = actual != expected
        if ok:
            self._pass += 1
            label = msg or f"{actual!r} != {expected!r}"
            print(f"  \033[32m✓\033[0m  {label}")
        else:
            self._fail += 1
            label = msg or f"expected values to differ, both were {actual!r}"
            self._errors.append(label)
            print(f"  \033[31m✗\033[0m  {label}")

    def assert_match(self, value, pattern, msg=None):
        import re as _re_am
        if isinstance(pattern, str):
            pattern = _re_am.compile(pattern)
        ok = bool(pattern.search(str(value)))
        label = msg or f"{value!r} =~ {pattern.pattern!r}"
        if ok:
            self._pass += 1
            print(f"  \033[32m✓\033[0m  {label}")
        else:
            self._fail += 1
            self._errors.append(label)
            print(f"  \033[31m✗\033[0m  {label}")

    def assert_nil(self, value, msg=None):
        ok = value is None
        label = msg or f"expected nil, got {value!r}"
        if ok:
            self._pass += 1
            print(f"  \033[32m✓\033[0m  {msg or 'value is nil'}")
        else:
            self._fail += 1
            self._errors.append(label)
            print(f"  \033[31m✗\033[0m  {label}")

    def assert_not_nil(self, value, msg=None):
        ok = value is not None
        label = msg or "expected non-nil value, got nil"
        if ok:
            self._pass += 1
            print(f"  \033[32m✓\033[0m  {msg or 'value is not nil'}")
        else:
            self._fail += 1
            self._errors.append(label)
            print(f"  \033[31m✗\033[0m  {label}")

    def assert_in(self, item, collection, msg=None):
        ok = item in collection
        label = msg or f"expected {item!r} to be in {collection!r}"
        if ok:
            self._pass += 1
            print(f"  \033[32m✓\033[0m  {msg or f'{item!r} in collection'}")
        else:
            self._fail += 1
            self._errors.append(label)
            print(f"  \033[31m✗\033[0m  {label}")

    def assert_approx_eq(self, actual, expected, delta=0.001, msg=None):
        try:
            diff = abs(float(actual) - float(expected))
        except (TypeError, ValueError):
            diff = float('inf')
        ok = diff <= abs(float(delta))
        if ok:
            self._pass += 1
            label = msg or f"{actual} ≈ {expected} (delta {delta})"
            print(f"  \033[32m✓\033[0m  {label}")
        else:
            self._fail += 1
            label = msg or f"expected {actual} ≈ {expected} within {delta}, diff was {diff}"
            self._errors.append(label)
            print(f"  \033[31m✗\033[0m  {label}")

    def assert_raises(self, fn, msg=None):
        label = msg or "expected an error to be raised"
        try:
            fn()
            self._fail += 1
            self._errors.append(f"{label} (no error was raised)")
            print(f"  \033[31m✗\033[0m  {label} (no error was raised)")
        except Exception:
            self._pass += 1
            print(f"  \033[32m✓\033[0m  {label}")

    def assert_raises_typed(self, fn, error_type, msg=None):
        label = msg or f"expected {error_type} to be raised"
        # error_type can be a string name or an actual exception class
        if isinstance(error_type, str):
            _type_map = {
                'RuntimeError': RuntimeError, 'TypeError': TypeError,
                'ValueError': ValueError, 'ZeroDivisionError': ZeroDivisionError,
                'IndexError': IndexError, 'KeyError': KeyError,
                'IOError': IOError, 'FileNotFoundError': FileNotFoundError,
                'OverflowError': OverflowError, 'NameError': NameError,
                'AttributeError': AttributeError, 'Exception': Exception,
                'Error': Exception,
            }
            # v1.17: user-defined error types take precedence
            exc_class = _fk_error_types.get(error_type) or _type_map.get(error_type, Exception)
        else:
            exc_class = error_type
        try:
            fn()
            self._fail += 1
            self._errors.append(f"{label} (no error was raised)")
            print(f"  \033[31m✗\033[0m  {label} (no error was raised)")
        except exc_class:
            self._pass += 1
            print(f"  \033[32m✓\033[0m  {label}")
        except Exception as e:
            self._fail += 1
            actual = type(e).__name__
            detail = f"{label} (got {actual} instead)"
            self._errors.append(detail)
            print(f"  \033[31m✗\033[0m  {detail}")

    def report(self):
        total = self._pass + self._fail
        print()
        if self._errors:
            for e in self._errors:
                print(f"    \033[31m✗\033[0m {e}")
        if self._fail == 0:
            print(f"  \033[32m✓  All {total} test(s) passed.\033[0m")
        else:
            print(f"  \033[31m✗  {self._fail} of {total} test(s) failed.\033[0m")
        print()
        return self._fail == 0

_fk_test_suite = _FKTestSuite()

def assert_true(value, msg=None):
    _fk_test_suite.assert_true(value, msg)

def assert_eq(actual, expected, msg=None):
    _fk_test_suite.assert_eq(actual, expected, msg)

def assert_neq(actual, expected, msg=None):
    _fk_test_suite.assert_neq(actual, expected, msg)

def assert_raises(fn, msg=None):
    _fk_test_suite.assert_raises(fn, msg)

def assert_raises_typed(fn, error_type, msg=None):
    _fk_test_suite.assert_raises_typed(fn, error_type, msg)

def assert_match(value, pattern, msg=None):
    _fk_test_suite.assert_match(value, pattern, msg)

def assert_nil(value, msg=None):
    _fk_test_suite.assert_nil(value, msg)

def assert_not_nil(value, msg=None):
    _fk_test_suite.assert_not_nil(value, msg)

def assert_in(item, collection, msg=None):
    _fk_test_suite.assert_in(item, collection, msg)

def assert_approx_eq(actual, expected, delta=0.001, msg=None):
    _fk_test_suite.assert_approx_eq(actual, expected, delta, msg)

def _fk_run_tests():
    return _fk_test_suite.report()

# Public alias — callable as run_tests() from any .fk file
run_tests = _fk_run_tests

# ─── v1.11 stdlib additions ───────────────────────────────────────────────────

def _fk_str_sub(s, old, new):
    """String .replace(old, new) — replace first occurrence (alias for sub)."""
    if not isinstance(s, str):
        raise TypeError(f"[Frankie] replace: expected a string, got {type(s).__name__}")
    return s.replace(str(old), str(new), 1)

def _fk_str_format(s, values):
    """String .format(hash) — replace {key} placeholders with hash values.
    Delegates to template() using {{key}} syntax after converting {key} → {{key}}.
    """
    if not isinstance(values, dict):
        raise TypeError("[Frankie] format: argument must be a hash")
    import re as _re_fmt
    def _replacer(m):
        key = m.group(1).strip()
        if key not in values:
            raise KeyError(f"[Frankie] format: key '{key}' not found in hash")
        return str(values[key])
    return _re_fmt.sub(r'\{(\w+)\}', _replacer, s)

def _fk_zip_with(a, b, fn):
    """Pair-wise transform: zip two vectors and apply fn(a, b) to each pair."""
    return [fn(x, y) for x, y in zip(a, b)]


# ─── v1.12 stdlib additions ───────────────────────────────────────────────────

def _fk_gsub_with_block(string, pattern, block_fn):
    """String .gsub(pattern) do |m| ... end — transform each match via block."""
    import re as _re_gsub
    if isinstance(pattern, str):
        pattern = _re_gsub.compile(pattern)
    return pattern.sub(lambda m: str(block_fn(m.group(0))), string)

def _fk_map_hash(h, fn):
    """Hash .map_hash do |k, v| [new_k, new_v] end — transform a hash into a new hash."""
    result = {}
    for k, v in h.items():
        pair = fn(k, v)
        if isinstance(pair, list) and len(pair) == 2:
            result[pair[0]] = pair[1]
        else:
            raise RuntimeError(f"[Frankie] map_hash: block must return a two-element vector, got {pair!r}")
    return result

def fk_round(x, n=0):
    """round(x, n) — round x to n decimal places (default 0)."""
    return round(float(x), int(n))

def _fk_cartesian_product(a, b):
    """Vector .product(other) — cartesian product as a vector of pairs."""
    return [[x, y] for x in a for y in b]

def _fk_vec_delete(vec, val):
    """Vector .delete(val) — remove first occurrence of val, return the modified vector."""
    try:
        vec.remove(val)
    except ValueError:
        pass
    return vec

def _fk_hash_delete(h, key):
    """Hash .delete(key) — remove key, return the modified hash."""
    h.pop(key, None)
    return h


# ─── v1.16 stdlib additions ───────────────────────────────────────────────────

def _fk_shell(cmd):
    """shell(cmd) — run a shell command; returns {stdout, stderr, exit_code, ok}."""
    import subprocess as _sp
    result = _sp.run(cmd, shell=True, capture_output=True, text=True)
    return {
        'stdout':    result.stdout.rstrip('\n'),
        'stderr':    result.stderr.rstrip('\n'),
        'exit_code': result.returncode,
        'ok':        result.returncode == 0,
    }


def _fk_dotenv(path='.env'):
    """dotenv(path) — parse a .env file and load vars into the environment.
    Returns a hash of the key/value pairs that were loaded.
    Lines starting with # are comments. Blank lines are skipped.
    Values may be quoted with " or '.
    """
    import os as _os
    import re as _re_env
    loaded = {}
    try:
        with open(path, 'r', encoding='utf-8') as _f:
            for line in _f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                m = _re_env.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)', line)
                if not m:
                    continue
                key, val = m.group(1), m.group(2)
                # Strip surrounding quotes
                if (val.startswith('"') and val.endswith('"')) or \
                   (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                _os.environ[key] = val
                loaded[key] = val
    except FileNotFoundError:
        pass   # silently return empty hash if file doesn't exist
    return loaded


def _fk_hash_transform_values(h, fn):
    """Hash .transform_values do |v| ... end — new hash with each value replaced by block result."""
    return {k: fn(v) for k, v in h.items()}


def _fk_hash_transform_keys(h, fn):
    """Hash .transform_keys do |k| ... end — new hash with each key replaced by block result."""
    return {fn(k): v for k, v in h.items()}


def _fk_hash_deep_merge(h1, h2):
    """Hash .deep_merge(other) — recursive merge; nested hashes are merged rather than replaced."""
    result = dict(h1)
    for k, v in h2.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _fk_hash_deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def _fk_smtp_send(opts):
    """Internal stdlib hook for frankiemail stitch — sends email via smtplib."""
    import smtplib as _smtp
    from email.mime.text import MIMEText as _MIMEText
    from email.mime.multipart import MIMEMultipart as _MIMEMultipart
    to      = opts.get('to', '')
    subject = opts.get('subject', '')
    body    = opts.get('body', '')
    from_   = opts.get('from', 'frankie@localhost')
    smtp    = opts.get('smtp', 'localhost')
    port    = int(opts.get('port', 587))
    user    = opts.get('user', '')
    pw      = opts.get('pass', '')
    html    = opts.get('html', False)
    cc      = opts.get('cc', '')
    bcc     = opts.get('bcc', '')
    try:
        if html:
            msg = _MIMEMultipart('alternative')
            msg.attach(_MIMEText(body, 'html'))
        else:
            msg = _MIMEText(body)
        msg['Subject'] = subject
        msg['From']    = from_
        msg['To']      = to
        if cc:  msg['Cc']  = cc
        recipients = [r.strip() for r in [to, cc, bcc] if r.strip()]
        with _smtp.SMTP(smtp, port) as s:
            s.ehlo()
            s.starttls()
            if user:
                s.login(user, pw)
            s.sendmail(from_, recipients, msg.as_string())
        return {'ok': True, 'error': None}
    except Exception as e:
        return {'ok': False, 'error': str(e)}


def _fk_str_scan(s, pattern):
    """String .scan(pattern) — return all capture groups from all matches.
    If the pattern has groups, returns a vector of vectors (one per match).
    If no groups, returns a vector of full match strings (like match_all).
    """
    import re as _re_scan
    try:
        compiled = _re_scan.compile(pattern)
    except Exception:
        return []
    matches = compiled.findall(s)
    # findall returns strings if no groups, tuples if >1 group, strings if 1 group
    result = []
    for m in matches:
        if isinstance(m, tuple):
            result.append(list(m))
        else:
            result.append(m)
    return result


# ═══ v1.17 — "Programs that grow" ═════════════════════════════════════════════

# ─── Range helpers ────────────────────────────────────────────────────────────

def _fk_to_vec(x):
    """.to_vec / .to_a — convert range/string/hash to a vector.
    Hashes become a vector of [key, value] pairs (Ruby's Hash#to_a)."""
    if isinstance(x, dict):
        return [list(pair) for pair in x.items()]
    if isinstance(x, str):
        return list(x)
    return list(x)

def _fk_range_step(r, step):
    """(1..10).step(2) — stride over a range (or any vector)."""
    step = int(step)
    if step == 0:
        raise RuntimeError("[Frankie] step: stride cannot be 0")
    if isinstance(r, range):
        return range(r.start, r.stop, step)
    return list(r)[::step]


# ─── User-defined error types ────────────────────────────────────────────────

class FrankieError(RuntimeError):
    """Base class for all user-defined Frankie error types."""
    _fk_user_error = True

_fk_error_types = {}

def _fk_def_error(name):
    """error TimeoutError — create (or fetch) a user-defined error class."""
    if name in _fk_error_types:
        return _fk_error_types[name]
    cls = type(name, (FrankieError,), {'_fk_user_error': True})
    _fk_error_types[name] = cls
    return cls

_FK_BUILTIN_ERRORS = {
    'RuntimeError': RuntimeError, 'TypeError': TypeError,
    'ValueError': ValueError, 'ZeroDivisionError': ZeroDivisionError,
    'IndexError': IndexError, 'KeyError': KeyError,
    'IOError': IOError, 'FileNotFoundError': FileNotFoundError,
    'OverflowError': OverflowError, 'NameError': NameError,
    'AttributeError': AttributeError, 'StopIteration': StopIteration,
    'TimeoutError': TimeoutError,
    'Exception': Exception, 'Error': Exception,
}

class _FkNeverMatches(Exception):
    """Returned by _fk_exc for unknown type names so a rescue clause for a
    never-raised type simply never matches (instead of crashing the handler)."""
    pass

def _fk_exc(name):
    """Resolve an error type name → exception class (user types first)."""
    if name in _fk_error_types:
        return _fk_error_types[name]
    if name in _FK_BUILTIN_ERRORS:
        return _FK_BUILTIN_ERRORS[name]
    return _FkNeverMatches

def _fk_make_error(name, message):
    """raise TimeoutError, "msg" — instantiate a typed error."""
    cls = _fk_error_types.get(name) or _FK_BUILTIN_ERRORS.get(name)
    if cls is None:
        # Auto-declare on first raise so simple scripts don't need 'error X'
        cls = _fk_def_error(name)
    return cls(message)


# ─── Cross-file tracebacks: line-map registry ────────────────────────────────
# Maps abs .fk path → {generated_py_line: fk_source_line}.
# Populated by frankiec (main file) and _fk_require/_fk_stitch/_fk_import.

_fk_line_maps = {}

def _fk_register_line_map(abs_path, line_map):
    _fk_line_maps[abs_path] = dict(line_map)


# ─── Namespaced imports: import "lib/math" as math ───────────────────────────

class FrankieModule:
    """Namespace object returned by import — holds a module's public names."""
    def __init__(self, name, names):
        self._fk_module_name = name
        for k, v in names.items():
            setattr(self, k, v)

    def __repr__(self):
        return f"<module {self._fk_module_name}>"

_fk_module_cache = {}

def _fk_import(path):
    """import "lib/math" as math — load a .fk file into its own namespace.

    Unlike require (which merges everything into the caller's scope),
    import returns a module object: math.circle_area(5), math.PI.
    Modules are cached — importing the same file twice returns the same module.
    """
    if not path.endswith('.fk'):
        path = path + '.fk'
    # Bundled program? Serve from the embedded registry.
    if path in _fk_bundled_compiled:
        if path in _fk_module_cache:
            return _fk_module_cache[path]
        _g = _fk_exec_bundled(path, propagate_frames=0)
        module_name = _os.path.basename(path)[:-3]
        public = {k: v for k, v in _g.items()
                  if not k.startswith('_') and k != '__builtins__'
                  and (k not in globals() or globals()[k] is not v)}
        mod = FrankieModule(module_name, public)
        _fk_module_cache[path] = mod
        return mod
    abs_path = _os.path.abspath(path)
    if abs_path in _fk_module_cache:
        return _fk_module_cache[abs_path]
    if not _os.path.exists(abs_path):
        raise RuntimeError(f"[Frankie] import: file not found: {path!r}")

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
    _cg = CodeGen()
    _py_src = _cg.generate(_ast)
    _fk_register_line_map(abs_path, _cg.line_map)

    # Execute in an isolated namespace seeded with the stdlib
    _baseline = {k: v for k, v in globals().items()}
    _g = dict(_baseline)
    _g['__file__'] = abs_path
    exec(compile(_py_src, abs_path, 'exec'), _g)

    # Public names = everything new (or changed) that isn't private
    module_name = _os.path.basename(abs_path)[:-3]
    public = {}
    for k, v in _g.items():
        if k.startswith('_') or k == '__builtins__':
            continue
        if k in _baseline and _baseline[k] is v:
            continue   # unchanged stdlib symbol
        public[k] = v
    mod = FrankieModule(module_name, public)
    _fk_module_cache[abs_path] = mod
    return mod


# ─── parallel_map — thread-pool map (zero deps) ──────────────────────────────

def parallel_map(vec, fn, workers=4):
    """parallel_map(vec, workers: 4) do |x| ... end

    Runs the block across a thread pool and returns results in input order.
    Perfect for I/O-bound work: HTTP calls, shell commands, file reads.
    The first exception raised by any worker is re-raised.
    """
    from concurrent.futures import ThreadPoolExecutor
    items = list(vec)
    if not items:
        return []
    workers = max(1, int(workers))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(fn, items))


# ─── TCP sockets ──────────────────────────────────────────────────────────────
import socket as _socket

class FrankieSocket:
    """TCP connection returned by tcp_connect() / server.accept()."""
    def __init__(self, sock, host=None, port=None):
        self._sock = sock
        self._host = host
        self._port = port
        self._open = True

    def send(self, data):
        """Send a string (or vector of byte ints). Returns bytes sent."""
        if isinstance(data, list):
            payload = bytes(data)
        else:
            payload = str(data).encode('utf-8')
        self._sock.sendall(payload)
        return len(payload)

    def send_line(self, data):
        """Send a string followed by a newline."""
        return self.send(str(data) + "\n")

    def recv(self, n=4096):
        """Receive up to n bytes as a string. Returns nil when the peer closes."""
        chunk = self._sock.recv(int(n))
        if not chunk:
            return None
        return chunk.decode('utf-8', errors='replace')

    def recv_line(self):
        """Receive until newline (exclusive). Returns nil when the peer closes."""
        buf = bytearray()
        while True:
            ch = self._sock.recv(1)
            if not ch:
                return buf.decode('utf-8', errors='replace') if buf else None
            if ch == b'\n':
                return buf.decode('utf-8', errors='replace')
            buf.extend(ch)

    def close(self):
        if self._open:
            self._open = False
            try:
                self._sock.close()
            except OSError:
                pass
        return None

    def peer(self):
        """Return "host:port" of the remote end."""
        try:
            host, port = self._sock.getpeername()[:2]
            return f"{host}:{port}"
        except OSError:
            return None

    def __repr__(self):
        state = "open" if self._open else "closed"
        return f"<tcp {self._host}:{self._port} {state}>"


class FrankieServerSocket:
    """Listening socket returned by tcp_listen()."""
    def __init__(self, sock, port):
        self._sock = sock
        self._port = port

    def accept(self):
        """Block until a client connects; returns a FrankieSocket."""
        client, addr = self._sock.accept()
        return FrankieSocket(client, addr[0], addr[1])

    def close(self):
        try:
            self._sock.close()
        except OSError:
            pass
        return None

    def __repr__(self):
        return f"<tcp-server :{self._port}>"


def tcp_connect(host, port, timeout=None, tls=False):
    """Open a TCP connection: sock = tcp_connect("example.com", 80)

    v1.19: pass tls: true for a TLS-wrapped connection (stdlib ssl,
    certificate-verified): tcp_connect("example.com", 443, tls: true)
    """
    s = _socket.create_connection((host, int(port)),
                                  timeout=float(timeout) if timeout else None)
    if tls:
        import ssl as _ssl
        s = _ssl.create_default_context().wrap_socket(s, server_hostname=host)
    return FrankieSocket(s, host, int(port))

def tcp_listen(port, host="0.0.0.0", backlog=16):
    """Listen on a port: server = tcp_listen(7777); client = server.accept()"""
    s = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
    s.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1)
    s.bind((host, int(port)))
    s.listen(int(backlog))
    return FrankieServerSocket(s, int(port))

def tcp_serve(port, handler, host="0.0.0.0"):
    """tcp_serve(7777) do |client| ... end — threaded accept loop.

    Each client connection runs the block in its own thread and is closed
    automatically afterwards. Blocks forever (Ctrl+C to stop).
    """
    server = tcp_listen(port, host)
    print(f"🧟 Frankie TCP server listening on {host}:{port}")
    try:
        while True:
            client = server.accept()
            def _handle(c=client):
                try:
                    handler(c)
                finally:
                    c.close()
            _threading.Thread(target=_handle, daemon=True).start()
    except KeyboardInterrupt:
        print("\n[Frankie] TCP server stopped.")
    finally:
        server.close()


# ─── Test harness extras: groups, tags, filtering, stubs ────────────────────

def test(name, fn, tags=None):
    """test "name" do ... end — a named, filterable test group.

    Filtering (set by `frankiec test --filter X --tag Y`):
      FRANKIE_TEST_FILTER — substring match on the group name
      FRANKIE_TEST_TAG    — group must carry the tag
    """
    flt = _os.environ.get('FRANKIE_TEST_FILTER', '')
    tag = _os.environ.get('FRANKIE_TEST_TAG', '')
    tag_list = [str(t) for t in (tags or [])]
    if flt and flt.lower() not in str(name).lower():
        _fk_test_suite._skipped += 1
        return None
    if tag and tag not in tag_list:
        _fk_test_suite._skipped += 1
        return None
    label = f"{name}" + (f"  [{', '.join(tag_list)}]" if tag_list else "")
    print(f"  ── {label}")
    fn()
    return None

_fk_stubs = {}

# Codegen rewrites some public stdlib names to internal helpers; stubbing
# the public name must patch the internal one too.
_FK_STUB_ALIASES = {
    'shell': '_fk_shell', 'exec_cmd': '_fk_shell', 'dotenv': '_fk_dotenv',
    'smtp_send': '_fk_smtp_send', 'sum': '_fk_sum', 'mean': '_fk_mean',
    'min': '_fk_min', 'max': '_fk_max', 'length': '_fk_length',
}

def _fk_stub_targets(name):
    targets = [name]
    if name in _FK_STUB_ALIASES:
        targets.append(_FK_STUB_ALIASES[name])
    return targets

def stub(name, replacement):
    """stub("http_get", ->(url) { fake_response }) — swap a global function.

    Replaces `name` in the calling script's scope, remembering the original.
    Restore with unstub("http_get") or unstub() for all.
    """
    import inspect as _insp
    frame = _insp.currentframe().f_back
    g = frame.f_globals
    for target in _fk_stub_targets(name):
        if target not in _fk_stubs:
            _fk_stubs[target] = g.get(target)
        g[target] = replacement
    return None

def unstub(name=None):
    """unstub("http_get") — restore a stubbed function (or all with no args)."""
    import inspect as _insp
    frame = _insp.currentframe().f_back
    g = frame.f_globals
    if name:
        names = _fk_stub_targets(name)
    else:
        names = list(_fk_stubs.keys())
    for n in names:
        if n in _fk_stubs:
            original = _fk_stubs.pop(n)
            if original is None:
                g.pop(n, None)
            else:
                g[n] = original
    return None


# ═══ v1.18 — "From projects to products" ═════════════════════════════════════

# ─── Set operations on vectors (order-preserving, deduped) ───────────────────

def _fk_union(a, b):
    """[1,2,3].union([3,4]) → [1, 2, 3, 4] — order-preserving, deduped."""
    out, seen = [], set()
    for x in list(a) + list(b):
        key = repr(x)
        if key not in seen:
            seen.add(key)
            out.append(x)
    return out

def _fk_intersect(a, b):
    """[1,2,3].intersect([2,3,4]) → [2, 3] — keeps a's order, deduped."""
    b_keys = {repr(x) for x in b}
    out, seen = [], set()
    for x in a:
        key = repr(x)
        if key in b_keys and key not in seen:
            seen.add(key)
            out.append(x)
    return out

def _fk_difference(a, b):
    """[1,2,3].difference([2]) → [1, 3] — keeps a's order, deduped."""
    b_keys = {repr(x) for x in b}
    out, seen = [], set()
    for x in a:
        key = repr(x)
        if key not in b_keys and key not in seen:
            seen.add(key)
            out.append(x)
    return out


# ─── benchmark do ... end ─────────────────────────────────────────────────────

def benchmark(label_or_fn, fn=None):
    """benchmark ["label"] do ... end — time a block, return elapsed ms.

    Prints a friendly timing line and returns the elapsed milliseconds
    (rounded to 0.1ms), so you can assert on it or collect it.
    """
    if fn is None:
        run, label = label_or_fn, "benchmark"
    else:
        run, label = fn, str(label_or_fn)
    t0 = _time.perf_counter()
    run()
    ms = round((_time.perf_counter() - t0) * 1000, 1)
    print(f"⏱  {label}: {ms}ms")
    return ms


# ─── enum Status(pending, active, done) ──────────────────────────────────────

class FrankieEnum:
    """Named set of symbolic values created by `enum Name(a, b, c)`.

    Status.pending  → "pending"
    Status.values   → ["pending", "active", "done"]
    Status.include?("active") → true    (via `in`)
    """
    def __init__(self, name, members):
        self._fk_enum_name = name
        self._fk_members = list(members)
        for m in members:
            setattr(self, m, m)

    def values(self):
        return list(self._fk_members)

    def __contains__(self, x):
        return x in self._fk_members

    def __iter__(self):
        return iter(self._fk_members)

    def __len__(self):
        return len(self._fk_members)

    def __repr__(self):
        return f"{self._fk_enum_name}({', '.join(self._fk_members)})"

def _fk_def_enum(name, members):
    return FrankieEnum(name, members)


# ─── breakpoint — debugger-lite ───────────────────────────────────────────────

def _fk_breakpoint(file, line, g, l, frame=None):
    """Pause execution and drop into a scoped debug REPL.

    Commands:  c / continue   resume the program
               s / step       execute one line (stepping into calls)
               n / next       execute one line (stepping over calls)
               stack          show the Frankie call stack
               vars           list local variables
               where          show the current location
               exit           abort the program
    Anything else is evaluated as a Frankie expression in the current scope.
    """
    import inspect as _insp
    if frame is None:
        frame = _insp.currentframe().f_back
    import sys as _s
    if not _s.stdin.isatty():
        print(f"[Frankie] breakpoint at {file}:{line} skipped (stdin is not a terminal)")
        return None

    # Merged view of the paused scope (function locals shadow globals)
    scope = dict(g)
    scope.update(l)

    src_line = ""
    try:
        with open(file, 'r', encoding='utf-8') as _f:
            lines = _f.read().splitlines()
        if 0 < line <= len(lines):
            src_line = lines[line - 1].strip()
    except OSError:
        pass

    print(f"\n🧟 breakpoint — {file}:{line}")
    if src_line:
        print(f"   ──▶ {line} │ {src_line}")
    print("   (c)ontinue · vars · where · exit · or type any Frankie expression\n")

    from repl import _compile_and_run
    while True:
        try:
            cmd = input("(fkdb) ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if cmd in ('c', 'continue', ''):
            return None
        if cmd in ('s', 'step', 'n', 'next'):
            _fk_step['mode'] = 'step' if cmd in ('s', 'step') else 'next'
            _fk_step['depth'] = _fk_frame_depth(frame)
            _fk_step['last'] = (file, line)
            _fk_trace_on(frame)
            return None
        if cmd == 'stack':
            for entry in _fk_stack_frames(frame):
                print(f"  {entry}")
            continue
        if cmd == 'exit':
            raise SystemExit(1)
        if cmd == 'where':
            print(f"  {file}:{line}" + (f"  →  {src_line}" if src_line else ""))
            continue
        if cmd == 'vars':
            import types as _types
            user_vars = {k: v for k, v in l.items()
                         if not k.startswith('_')
                         and k not in ('__builtins__',)
                         and not isinstance(v, (type, _types.FunctionType,
                                                _types.BuiltinFunctionType,
                                                _types.ModuleType))}
            if not user_vars:
                print("  (no local variables)")
            for k in sorted(user_vars):
                try:
                    print(f"  {k} = {_fk_to_str(user_vars[k])}")
                except Exception:
                    print(f"  {k} = {user_vars[k]!r}")
            continue
        try:
            out, err = _compile_and_run(cmd, scope)
            if out:
                print(out, end='' if out.endswith('\n') else '\n')
            if err:
                print(f"  {err}")
            elif not out and scope.get('_') is not None:
                print(f"  => {_fk_to_str(scope['_'])}")
        except SystemExit:
            raise
        except Exception as repl_err:
            print(f"  [debugger] {type(repl_err).__name__}: {repl_err}")


# ─── WebSockets — RFC 6455, hand-rolled on the stdlib (v1.18) ─────────────────

_WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

def _fk_ws_accept_key(key):
    import hashlib as _hl, base64 as _b64
    digest = _hl.sha1((key + _WS_GUID).encode('ascii')).digest()
    return _b64.b64encode(digest).decode('ascii')


class FrankieWebSocket:
    """A WebSocket connection (server- or client-side).

    ws.send("hello")     — send a text message
    ws.recv()            — receive the next text message (nil when closed)
    ws.close()           — send a close frame and shut the connection
    ws.params            — path parameters (server-side routes)
    ws.path              — request path
    ws.peer              — remote "host:port"
    """
    def __init__(self, sock, rfile=None, client_side=False,
                 path=None, params=None):
        self._sock = sock
        self._rfile = rfile if rfile is not None else sock.makefile('rb')
        self._client_side = client_side
        self._open = True
        self.path = path
        self.params = params or {}

    # ── Receiving ────────────────────────────────────────────────────────────

    def _read_exact(self, n):
        data = self._rfile.read(n)
        if data is None or len(data) < n:
            raise ConnectionError("websocket: connection closed mid-frame")
        return data

    def recv(self):
        """Block until the next text/binary message. Returns nil on close.
        Ping frames are answered automatically."""
        if not self._open:
            return None
        buffer = bytearray()
        try:
            while True:
                b1, b2 = self._read_exact(2)
                fin    = b1 & 0x80
                opcode = b1 & 0x0F
                masked = b2 & 0x80
                length = b2 & 0x7F
                if length == 126:
                    import struct as _st
                    length = _st.unpack('>H', self._read_exact(2))[0]
                elif length == 127:
                    import struct as _st
                    length = _st.unpack('>Q', self._read_exact(8))[0]
                mask = self._read_exact(4) if masked else None
                payload = self._read_exact(length) if length else b''
                if mask:
                    payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))

                if opcode == 0x8:                    # close
                    self._send_raw(0x8, payload[:2] if payload else b'')
                    self._shutdown()
                    return None
                if opcode == 0x9:                    # ping → pong
                    self._send_raw(0xA, payload)
                    continue
                if opcode == 0xA:                    # pong → ignore
                    continue
                buffer.extend(payload)
                if fin:
                    return buffer.decode('utf-8', errors='replace')
        except (ConnectionError, OSError):
            self._shutdown()
            return None

    # ── Sending ──────────────────────────────────────────────────────────────

    def _send_raw(self, opcode, payload):
        import struct as _st, os as _o
        if not self._open:
            return
        header = bytes([0x80 | opcode])
        mask_bit = 0x80 if self._client_side else 0x00
        n = len(payload)
        if n < 126:
            header += bytes([mask_bit | n])
        elif n < 65536:
            header += bytes([mask_bit | 126]) + _st.pack('>H', n)
        else:
            header += bytes([mask_bit | 127]) + _st.pack('>Q', n)
        if self._client_side:
            mask = _o.urandom(4)
            payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
            data = header + mask + payload
        else:
            data = header + payload
        try:
            self._sock.sendall(data)
        except OSError:
            self._shutdown()

    def send(self, message):
        """Send a text message (anything non-string is stringified)."""
        self._send_raw(0x1, _fk_to_str(message).encode('utf-8')
                       if not isinstance(message, str)
                       else message.encode('utf-8'))
        return None

    def close(self, code=1000):
        if self._open:
            import struct as _st
            self._send_raw(0x8, _st.pack('>H', int(code)))
            self._shutdown()
        return None

    def _shutdown(self):
        self._open = False
        try:
            self._sock.close()
        except OSError:
            pass

    def peer(self):
        try:
            host, port = self._sock.getpeername()[:2]
            return f"{host}:{port}"
        except OSError:
            return None

    def __repr__(self):
        state = "open" if self._open else "closed"
        return f"<websocket {self.path or ''} {state}>"


def _fk_ws_serve_upgrade(handler, path, params, ws_handler):
    """Complete the server-side handshake on a BaseHTTPRequestHandler,
    then hand the connection to the Frankie websocket handler."""
    key = handler.headers.get('Sec-WebSocket-Key', '')
    if not key:
        handler.send_response(400)
        handler.end_headers()
        return
    accept = _fk_ws_accept_key(key)
    raw = ("HTTP/1.1 101 Switching Protocols\r\n"
           "Upgrade: websocket\r\n"
           "Connection: Upgrade\r\n"
           f"Sec-WebSocket-Accept: {accept}\r\n\r\n")
    handler.connection.sendall(raw.encode('ascii'))
    ws = FrankieWebSocket(handler.connection, rfile=handler.rfile,
                          client_side=False, path=path, params=params)
    try:
        ws_handler(ws)
    finally:
        ws.close()


def ws_connect(url, timeout=None):
    """Open a WebSocket client connection: ws = ws_connect("ws://host:port/path")

    Returns a FrankieWebSocket. Only ws:// is supported (no TLS) — Frankie's
    zero-dependency mantra, stitched to your terminal.
    """
    import base64 as _b64, os as _o
    from urllib.parse import urlparse as _parse
    parsed = _parse(url)
    if parsed.scheme not in ('ws', 'wss'):
        raise RuntimeError(f"[Frankie] ws_connect: expected a ws:// or wss:// URL, got {parsed.scheme!r}")
    use_tls = parsed.scheme == 'wss'
    host = parsed.hostname
    port = parsed.port or (443 if use_tls else 80)
    path = parsed.path or '/'
    if parsed.query:
        path += '?' + parsed.query

    sock = _socket.create_connection((host, port),
                                     timeout=float(timeout) if timeout else None)
    if use_tls:
        import ssl as _ssl
        sock = _ssl.create_default_context().wrap_socket(sock, server_hostname=host)
    key = _b64.b64encode(_o.urandom(16)).decode('ascii')
    request = (f"GET {path} HTTP/1.1\r\n"
               f"Host: {host}:{port}\r\n"
               "Upgrade: websocket\r\n"
               "Connection: Upgrade\r\n"
               f"Sec-WebSocket-Key: {key}\r\n"
               "Sec-WebSocket-Version: 13\r\n\r\n")
    sock.sendall(request.encode('ascii'))

    rfile = sock.makefile('rb')
    status_line = rfile.readline().decode('latin-1').strip()
    parts = status_line.split()
    if len(parts) < 2 or parts[1] != '101':
        sock.close()
        raise RuntimeError(f"[Frankie] ws_connect: handshake rejected: {status_line}")
    headers = {}
    while True:
        line = rfile.readline().decode('latin-1').strip()
        if not line:
            break
        if ':' in line:
            k, _, v = line.partition(':')
            headers[k.strip().lower()] = v.strip()
    expected = _fk_ws_accept_key(key)
    if headers.get('sec-websocket-accept') != expected:
        sock.close()
        raise RuntimeError("[Frankie] ws_connect: invalid Sec-WebSocket-Accept from server")
    sock.settimeout(None)
    return FrankieWebSocket(sock, rfile=rfile, client_side=True, path=path)


# ═══ v1.19 — "Under the microscope": tracing machinery ═══════════════════════

_fk_step = {'mode': None, 'depth': 0, 'last': None}
_fk_coverage_data = None    # abs path → set of executed fk lines (when active)


def _fk_frame_line(frame):
    """(abs_fk_path, fk_line) for a frame inside compiled Frankie code."""
    fname = frame.f_code.co_filename
    if not (fname.endswith('.fk') or fname.startswith('<bundle:')):
        return None, None
    key = _os.path.abspath(fname) if fname.endswith('.fk') else fname
    lm = _fk_line_maps.get(key)
    if not lm:
        return None, None
    return key, lm.get(frame.f_lineno)


def _fk_frame_depth(frame):
    d = 0
    while frame is not None:
        d += 1
        frame = frame.f_back
    return d


def _fk_stack_frames(frame):
    """Human-readable Frankie stack (innermost first)."""
    out = []
    while frame is not None:
        path, fk_line = _fk_frame_line(frame)
        if path is not None and fk_line is not None:
            fn = frame.f_code.co_name
            label = fn if not fn.startswith('<') else '(top level)'
            out.append(f"{_os.path.basename(path)}:{fk_line}  in {label}")
        frame = frame.f_back
    return out if out else ["(no Frankie frames)"]


def _fk_tracer(frame, event, arg):
    """Global tracer: powers step/next and coverage collection."""
    if event == 'call':
        return _fk_tracer
    if event != 'line':
        return _fk_tracer

    path, fk_line = _fk_frame_line(frame)
    if path is None or fk_line is None:
        return _fk_tracer

    # Coverage collection (cheap: one set-add per line event)
    if _fk_coverage_data is not None:
        _fk_coverage_data.setdefault(path, set()).add(fk_line)

    # Stepping
    mode = _fk_step['mode']
    if mode is not None:
        if mode == 'next' and _fk_frame_depth(frame) > _fk_step['depth']:
            return _fk_tracer
        if _fk_step['last'] == (path, fk_line):
            return _fk_tracer          # still on the same source line
        _fk_step['mode'] = None
        if _fk_coverage_data is None:
            import sys as _s
            _s.settrace(None)
        _fk_breakpoint(path, fk_line, frame.f_globals, frame.f_locals,
                       frame=frame)
    return _fk_tracer


def _fk_trace_on(frame=None):
    """Enable the tracer globally and on the current frame chain."""
    import sys as _s
    _s.settrace(_fk_tracer)
    while frame is not None:
        frame.f_trace = _fk_tracer
        frame = frame.f_back


def _fk_debug_start():
    """frankiec run --debug — break at the first Frankie line."""
    _fk_step['mode'] = 'step'
    _fk_step['depth'] = 0
    _fk_step['last'] = None
    _fk_trace_on()


def _fk_coverage_start():
    global _fk_coverage_data
    _fk_coverage_data = {}
    _fk_trace_on()


def _fk_coverage_stop():
    global _fk_coverage_data
    import sys as _s
    _s.settrace(None)
    data = _fk_coverage_data
    _fk_coverage_data = None
    return data or {}


# ─── UDP sockets (v1.19) ──────────────────────────────────────────────────────

class FrankieUDPSocket:
    """UDP socket returned by udp_listen()."""
    def __init__(self, sock, port=None):
        self._sock = sock
        self._port = port

    def recv(self, n=4096):
        """Block for the next datagram → {data:, host:, port:}."""
        data, addr = self._sock.recvfrom(int(n))
        return {'data': data.decode('utf-8', errors='replace'),
                'host': addr[0], 'port': addr[1]}

    def send_to(self, host, port, message):
        payload = message if isinstance(message, bytes) else _fk_to_str(message).encode('utf-8') if not isinstance(message, str) else message.encode('utf-8')
        return self._sock.sendto(payload, (host, int(port)))

    def close(self):
        try:
            self._sock.close()
        except OSError:
            pass
        return None

    def __repr__(self):
        return f"<udp :{self._port}>"


def udp_listen(port, host="0.0.0.0"):
    """Bind a UDP socket: sock = udp_listen(9999); msg = sock.recv()"""
    s = _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)
    s.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1)
    s.bind((host, int(port)))
    return FrankieUDPSocket(s, int(port))


def udp_send(host, port, message):
    """Fire-and-forget datagram: udp_send("127.0.0.1", 9999, "ping")"""
    s = _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)
    try:
        payload = message.encode('utf-8') if isinstance(message, str) else _fk_to_str(message).encode('utf-8')
        return s.sendto(payload, (host, int(port)))
    finally:
        s.close()
