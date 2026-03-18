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
    # FrankieDate duck-type check
    if hasattr(x, 'year') and hasattr(x, 'format'):
        return x.to_s()
    # FrankieHTTPResponse duck-type check
    if hasattr(x, 'status') and hasattr(x, 'body') and hasattr(x, 'ok'):
        return repr(x)
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


# ─── v1.1 Iterator Helpers ────────────────────────────────────────────────────

def _fk_select(iterable, fn):
    """Return a new list of elements for which fn returns true."""
    return [x for x in iterable if fn(x)]

def _fk_reject(iterable, fn):
    """Return a new list of elements for which fn returns false."""
    return [x for x in iterable if not fn(x)]

def _fk_find(iterable, fn):
    """Return the first element for which fn returns true, or None."""
    for x in iterable:
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
        return any(iterable)
    return any(fn(x) for x in iterable)

def _fk_all(iterable, fn=None):
    """Return true if all elements satisfy fn (or are truthy if no fn)."""
    if fn is None:
        return all(iterable)
    return all(fn(x) for x in iterable)

def _fk_none(iterable, fn=None):
    """Return true if no elements satisfy fn."""
    if fn is None:
        return not any(iterable)
    return not any(fn(x) for x in iterable)

def _fk_count_if(iterable, fn):
    """Count elements satisfying fn."""
    return sum(1 for x in iterable if fn(x))

def _fk_find(iterable, fn):
    """Return the first element for which fn returns truthy, else None."""
    for item in (iterable if isinstance(iterable, list) else list(iterable)):
        if fn(item):
            return item
    return None

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

def json_dump(obj, pretty=False):
    """Serialize a Frankie value → JSON string."""
    indent = 2 if pretty else None
    return _json.dumps(obj, indent=indent, default=str)

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
import re as _re
import threading as _threading


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
        self.method  = method
        self.path    = path
        self.params  = params
        self.query   = query
        self.headers = headers
        self.body    = body

    @property
    def json(self):
        try:
            import json as _j
            return _j.loads(self.body)
        except Exception:
            return None

    @property
    def form(self):
        return dict(_urllib_parse.parse_qsl(self.body))

    def __repr__(self):
        return f"<FrankieRequest {self.method} {self.path}>"


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
    """Return an error response."""
    return FrankieResponse(body, status, {}, "text/plain; charset=utf-8")


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

    def before(self, handler):
        """Register a before-filter (called before every matched route)."""
        self._before.append(handler)

    def after(self, handler):
        """Register an after-filter (called after every matched route)."""
        self._after.append(handler)

    def not_found(self, handler):
        """Register a custom 404 handler."""
        self._not_found = handler

    # ── Dispatch ────────────────────────────────────────────────────────────

    def _dispatch(self, method, path, query_string, headers, body):
        query = dict(_urllib_parse.parse_qsl(query_string))

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
                length  = int(self.headers.get('Content-Length', 0))
                body    = self.rfile.read(length).decode('utf-8', errors='replace') if length else ''
                resp    = app._dispatch(self.command, parsed.path,
                                        parsed.query, dict(self.headers), body)
                encoded = resp.body.encode('utf-8')
                self.send_response(resp.status)
                self.send_header('Content-Type', resp.content_type)
                self.send_header('Content-Length', str(len(encoded)))
                for k, v in resp.headers.items():
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


def web_app():
    """Create and return a new Frankie web application."""
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


# ─── v1.5: Sort helpers ───────────────────────────────────────────────────────

def _fk_sort_by(vec, key_fn):
    """sort_by do |x| ... end — sort by the value the block returns."""
    if not isinstance(vec, list):
        raise RuntimeError("[Frankie] sort_by requires a vector")
    return sorted(vec, key=key_fn)

def _fk_min_by(vec, key_fn):
    """min_by do |x| ... end — element with the smallest key."""
    if not isinstance(vec, list):
        raise RuntimeError("[Frankie] min_by requires a vector")
    return min(vec, key=key_fn)

def _fk_max_by(vec, key_fn):
    """max_by do |x| ... end — element with the largest key."""
    if not isinstance(vec, list):
        raise RuntimeError("[Frankie] max_by requires a vector")
    return max(vec, key=key_fn)

def _fk_sum_by(vec, key_fn):
    """sum_by do |x| ... end — sum the values the block returns."""
    if not isinstance(vec, list):
        raise RuntimeError("[Frankie] sum_by requires a vector")
    return sum(key_fn(x) for x in vec)


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

def _fk_run_tests():
    return _fk_test_suite.report()
