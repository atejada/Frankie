# Changelog

## v1.10.0 (2026)

### New Features

**Language — String & Vector `*` Repetition**
- `"ha" * 3` → `"hahaha"` — string repetition
- `[0] * 5` → `[0, 0, 0, 0, 0]` — vector fill
- `[1, 2] * 3` → `[1, 2, 1, 2, 1, 2]` — pattern repeat
- Integer on either side works: `3 * "hi"` → `"hihihi"`
- Implemented in `_fk_arith` — zero new syntax

**Language — Heredoc `<<~TEXT`**
- `<<~DELIM ... DELIM` multiline string with automatic indent-stripping
- `<<DELIM` variant (no strip) also supported
- Full `#{}` interpolation inside heredoc bodies
- Pure lexer change — no new tokens or AST nodes
- The codegen `gen_string` rewritten to use `repr()` + concatenation for multiline interpolated strings, eliminating triple-quote/backslash edge cases entirely

**Language — Named Rescue Without Variable**
- `rescue TypeError` is now valid without a binding variable
- `rescue TypeError e` still works when the message is needed
- Parser fix: variable binding is now truly optional after a typed rescue

**Standard Library — `times(n) do |i|` standalone**
- `times(n) do |i| ... end` functional form added alongside `n.times do`
- `times(n)` with no block returns `[0..n-1]` as a list
- `FuncCall` AST node gains an optional `block` field; parser attaches trailing `do...end` blocks to function calls; codegen emits a `for` loop for `times`

**Standard Library — `flatten(depth)`**
- `.flatten` with no argument now does **full deep** flatten (breaking change from v1.9's one-level-only behaviour)
- `.flatten(n)` flattens exactly `n` levels; `.flatten(0)` is a no-op
- Backed by new `_fk_flatten_deep(iterable, depth)` in stdlib

**Standard Library — `map_with_index`**
- `.map_with_index do |x, i| ... end` — index available in map block
- Single-expression blocks compile to a list comprehension; multi-statement blocks use a helper function

**Standard Library — `pp(value)` pretty-print**
- Indented multiline output for hashes, vectors, and records
- Records printed as `RecordName(\n  field: value,\n  ...)`
- Flat vectors printed on one line; nested structures indented recursively

**Standard Library — `encode` / `decode`**
- `"hello".encode` → `[104, 101, 108, 108, 111]` (UTF-8 bytes as vector)
- `"hello".encode("ascii")` — explicit encoding
- `[104, 105].decode` → `"hi"`
- `[104, 105].decode("utf-8")` — explicit encoding

**Runtime — Exit Code Propagation**
- `exit(42)` in Frankie code now propagates the exact code to the shell
- `frankiec run` catches `SystemExit` and calls `sys.exit(e.code)` instead of re-raising

**CLI — `--help` Flag**
- `frankiec --help` prints the full usage docstring
- `frankiec <cmd> --help` prints a short description for that specific command
- All commands covered: `run`, `repl`, `test`, `fmt`, `docs`, `build`, `check`, `new`, `version`

### Bug Fixes
- `gen_string` multiline interpolation: single-line f-strings were emitted with literal embedded newlines (invalid Python syntax). Fixed by using `repr()` + string concatenation for all multiline interpolated strings.
- `flatten` semantics changed to full-deep by default; use `.flatten(1)` for the old one-level behaviour.

---

## v1.9.0 (2026)


### New Features

**Language — Record Types (`record`)**
- `record Point(x, y)` defines a lightweight named data object
- Constructor function generated automatically: `p = Point(3, 4)`
- Prints as `Point(x: 3, y: 4)` — clean, readable output
- Records are hashes under the hood — all hash methods, iterators, `dig`, `|`, and `.merge` work on them
- New lexer token `RECORD`, new AST node `RecordDef`, new `gen_record_def` in codegen
- `_fk_to_str` updated to detect `__type__` and display record notation

```ruby
record Employee(name, dept, salary)
emp = Employee("Alice", "Engineering", 95000)
puts emp               # Employee(name: Alice, dept: Engineering, salary: 95000)
puts emp["dept"]       # Engineering
by_dept = employees.group_by do |e| e["dept"] end
```

**Standard Library — `hash.dig(key, ...)`**
- Safe nested access: returns `nil` at the first missing key, never crashes
- Works on hashes (string/symbol keys) and vectors (integer indices)
- Chains correctly with `&.` for nil-safe navigation

```ruby
config = {db: {host: "localhost", pool: {max: 10}}}
puts config.dig("db", "pool", "max")   # 10
puts config.dig("db", "missing")       # nil  (no crash)
```

**Standard Library — Standalone `zip(*vecs)`**
- `zip(a, b)` function form alongside the existing `.zip` method
- Accepts two or more vectors; stops at the shortest
- Consistent with Frankie's R-inspired functional style

```ruby
zip(["Alice", "Bob"], [95, 87])   # [["Alice", 95], ["Bob", 87]]
```

**Tooling — `frankiec fmt` (Auto-Formatter)**
- New command: `frankiec fmt <file.fk>` — print canonically formatted source
- `--write` flag: reformat in-place
- `--check` flag: exit 1 if not already formatted (CI-friendly)
- Implemented in `frankie_fmt.py` — walks the AST, zero new dependencies
- Canonical style: 2-space indent, single-expr blocks inlined, blank line after top-level `def`

**Tooling — `frankiec docs` (Documentation Generator)**
- New command: `frankiec docs <file.fk>` — extract `##` doc-comments to Markdown
- `--output <file.md>` flag: write to file instead of stdout
- Supports `@param`, `@return`, `@example` tags
- Works on directories: `frankiec docs lib/` generates docs for every `.fk` file
- Implemented in `frankie_docs.py` — pure Python, zero new dependencies

**REPL — readline, Tab Completion, History Persistence**
- Arrow key navigation (`↑`/`↓`) and Ctrl+R reverse-search via Python's built-in `readline`
- Tab completion for Frankie keywords, stdlib functions, and common method names
- History saved to `~/.frankie_history` on exit; restored at next startup (max 1000 entries)
- `.env` auto-loaded from the current working directory at REPL startup

**Runtime — `.env` Auto-Loader**
- `frankiec run` and `frankiec repl` automatically load `.env` from the current directory
- Keys already set in the shell environment take precedence
- Values accessible via the existing `env(key, default)` stdlib function
- No crash if `.env` is absent

### Bug Fixes
- `record` added as a reserved keyword — programs that used `record` as a variable name must rename it (the existing `.fk` examples in the repo have been updated)
- `scaffold.py` version string updated from `v1.3` to `v1.9`

---

## v1.8.0 (2026)


### New Features

**Language — Lambda / Anonymous Functions (`->`)**
- Store functions as first-class values: `double = ->(x) { x * 2 }`
- Call with `.call(args)`: `double.call(5)` → `10`
- Single-expression bodies use brace syntax: `->(x) { x * 2 }`
- Multi-statement bodies use `do...end`: `->(x) do ... end`
- Default parameters are supported: `->(x, y = 1) { x + y }`
- Lambdas can be stored in variables, vectors, and hashes
- Lambdas can be passed to functions as arguments (higher-order functions)
- Lambdas can be returned from functions
- New token: `ARROW` (`->`)
- New AST node: `LambdaLiteral`

```ruby
double = ->(x) { x * 2 }
add    = ->(a, b) { a + b }
puts double.call(7)      # 14
puts add.call(3, 4)      # 7

def apply(fn, val)
  return fn.call(val)
end
puts apply(double, 9)    # 18
```

**Language — Hash Merge Operator `|`**
- `h1 | h2` merges two hashes; right-hand keys win on conflict
- Returns a new hash — neither operand is modified
- Chains naturally: `a | b | c`
- Complements the existing `.merge(other)` method

```ruby
defaults = {color: "blue", size: "medium"}
overrides = {color: "red"}
puts defaults | overrides   # {color: red, size: medium}
```

**Standard Library — `group_by`**
- `vector.group_by do |x| key end` buckets elements by block return value
- Returns a hash whose values are arrays of matching elements, in original order
- Pairs naturally with `.tally`, `.sort_by`, `.each`, and the new `|` operator

```ruby
words = ["ant", "ape", "bear", "bee", "cat"]
puts words.group_by do |w| w[0] end
# {"a" => ["ant", "ape"], "b" => ["bear", "bee"], "c" => ["cat"]}
```

**Standard Library — `each_slice` and `each_cons`**
- `vector.each_slice(n)` — iterate non-overlapping chunks of size `n`
- `vector.each_cons(n)` — iterate all consecutive windows of size `n` (sliding window)
- Both accept an optional `do |var| ... end` block; without a block, return a vector of slices/windows
- Mirrors Ruby's API; natural fit for data-processing, batch operations, and rolling statistics

```ruby
[1,2,3,4,5,6].each_slice(2) do |s|
  puts s     # [1,2]  [3,4]  [5,6]
end

[10, 13, 11, 15].each_cons(2) do |w|
  puts w[1] - w[0]    # 3  -2  4
end
```

### Bug Fixes
- **`_block_to_lambda`** — blocks whose body ends with a control-flow expression
  (`if`, `case`, `unless`) now correctly capture the result value instead of
  raising a `CodeGenError`. Affects `select`, `reject`, `sort_by`, `min_by`,
  `max_by`, `sum_by`, `find`, `flat_map`, and the new `group_by`.

---

## v1.7.1 (2025)

### Bug Fixes
- **`N.times do`** — `def _gen_times` method definition was accidentally dropped from
  `compiler/codegen.py` during v1.7 development, causing an `AttributeError` at runtime.
  The method body was present but the `def` header was missing.
- **`test_v17.fk`** — example test file used `def()` anonymous function syntax inside
  `assert_raises_typed` which does not exist in Frankie yet. Rewritten to use
  `begin/rescue` blocks instead.

---

## v1.7.0 (2025)

### New Features

**Language — Nil Safety Operator `&.`**
- `x&.method` — call `.method` on `x`, returning `nil` if `x` is nil (no crash)
- `x&.method(args)` — nil-safe method call with arguments
- `x&.property` — nil-safe property / zero-arg attribute access
- Chains naturally: `a&.b&.c` — short-circuits at the first nil
- Works with any value: strings, hashes, vectors, custom objects
- No language keywords added — `&.` is a single new operator token

```ruby
user = {name: "Alice"}
missing = nil

puts user["name"]&.upcase   # ALICE
puts missing&.upcase        # nil  (no crash)
puts missing&.upcase&.reverse  # nil  (chain short-circuits)
```

**Standard Library — `template(str, hash)`**
- Replace `{{key}}` placeholders in a string with values from a hash
- Clean alternative to `sprintf` / `#{}` when keys are dynamic or templates are stored externally
- Raises `KeyError` if a placeholder key is missing from the hash

```ruby
msg = template("Hello, {{name}}! Age: {{age}}.", {name: "Alice", age: 30})
puts msg   # Hello, Alice! Age: 30.
```

**Standard Library — File System Operations**
- `file_rename(src, dst)` — rename or move a file
- `file_copy(src, dst)` — copy a file (preserving metadata); returns `dst`
- `file_mkdir(path)` — create a directory; creates intermediate dirs by default (like `mkdir -p`)
- `file_mkdir(path, false)` — create a single directory only (no parents)
- `dir_exists(path)` — return `true` if path is an existing directory
- `dir_list(path)` — return a sorted vector of filenames in a directory (default: `"."`)
- All use Python's built-in `os` / `shutil` — zero external dependencies

```ruby
file_mkdir("/tmp/myapp/data")
puts dir_exists("/tmp/myapp/data")     # true

file_write("/tmp/myapp/data/a.txt", "hello")
file_copy("/tmp/myapp/data/a.txt", "/tmp/myapp/data/b.txt")
file_rename("/tmp/myapp/data/b.txt", "/tmp/myapp/data/c.txt")

puts dir_list("/tmp/myapp/data")       # [a.txt, c.txt]
```

**Standard Library — `assert_raises_typed(fn, type, msg)`**
- Extends the test runner to assert that a specific error *type* was raised
- `type` can be a string (`"ZeroDivisionError"`) or a Python exception class
- Fails with a clear message if no error is raised, or if the wrong type is raised
- Supported type names mirror typed `rescue`: `RuntimeError`, `TypeError`, `ValueError`,
  `ZeroDivisionError`, `IndexError`, `KeyError`, `IOError`, `FileNotFoundError`,
  `OverflowError`, `NameError`, `AttributeError`, `Exception` / `Error`

```ruby
assert_raises_typed(def()
  x = 1 // 0
end, "ZeroDivisionError", "division by zero raises correctly")

assert_raises_typed(def()
  file_read("/no/such/file.txt")
end, "RuntimeError", "missing file raises RuntimeError")
```

### Bug Fixes
- `&.` operator correctly short-circuits chains — once a nil is encountered, remaining
  method calls in the chain are skipped without raising errors

---

## v1.6.0 (2025)

### New Features

**Language — Compound Assignment Operators**
- `+=` — add and assign: `x += 5`
- `-=` — subtract and assign: `x -= 3`
- `*=` — multiply and assign: `x *= 2`
- `/=` — divide and assign (float): `x /= 4`
- `//=` — integer-divide and assign (Fortran): `x //= 3`
- `**=` — exponentiate and assign (Fortran): `x **= 2`
- `%=` — modulo and assign: `x %= 7`
- All operators also work on vector elements: `v[i] += 1`

**Language — Typed Rescue Clauses**
- `rescue TypeError e` — catch only `TypeError` errors
- `rescue ZeroDivisionError e` — catch only division by zero
- Multiple `rescue` clauses on one `begin...end` block, checked in order
- Full list of supported types: `RuntimeError`, `TypeError`, `ValueError`,
  `ZeroDivisionError`, `IndexError`, `KeyError`, `IOError`,
  `FileNotFoundError`, `OverflowError`, `NameError`, `AttributeError`,
  `StopIteration`, `Exception` / `Error` (catch-all aliases)
- Untyped `rescue e` remains valid and catches everything

**Standard Library — `.find` / `.detect`**
- `.find do |x| ... end` — return the first element for which the block is true, or `nil`
- `.detect do |x| ... end` — alias for `.find`
- Works on any vector, including vectors of hashes
- Chains naturally with `.select`, `.map`, `.sort_by`, etc.

**Tooling — `frankiec test`**
- `frankiec test` — run `test.fk` in the current directory
- `frankiec test <file.fk>` — run a named test file
- Built-in assertions (no imports needed):
  - `assert_true(cond, msg)` — pass if condition is truthy
  - `assert_eq(actual, expected, msg)` — pass if values are equal
  - `assert_neq(actual, expected, msg)` — pass if values differ
  - `assert_raises(fn, msg)` — pass if calling `fn` raises any error
- Live `✓` / `✗` output per assertion
- Summary line with pass count, fail count, and elapsed time
- Exits with code 1 if any assertion fails (CI-friendly)

### Bug Fixes
- `_fk_test_suite` singleton now uses a fresh isolated copy per `frankiec test` run,
  preventing state leakage between multiple test invocations in the same process

---

## v1.5.0 (2025)

### New Features

**Language — Loop Control**
- `next` — skip to the next iteration (like `continue` in other languages); supports postfix `next if cond`
- `break` — exit a loop early; supports postfix `break if cond`
- `break value` — exit a loop and store a result in `_fk_break_val`; supports postfix form

**Language — Constants**
- `UPPER_CASE = value` — UPPER_SNAKE_CASE identifiers are treated as constants
- Reassignment prints a warning and preserves the original value
- Works with any type: integers, floats, strings, vectors, hashes

**Standard Library — Randomness**
- `random()` — random Float in [0.0, 1.0)
- `rand(n)` — random Integer in [0, n)
- `rand_int(a, b)` — random Integer in [a, b] (both inclusive)
- `rand_float(a, b)` — random Float in [a, b)
- `shuffle(vec)` — return a shuffled copy of a vector
- `sample(vec, n)` — return n randomly chosen elements (no repeats)
- `rand_seed(n)` — seed the RNG for reproducible results

**Standard Library — Sorting**
- `.sort_by do |x| key end` — sort a vector by any computed key
- `.min_by do |x| key end` — element with the smallest key
- `.max_by do |x| key end` — element with the largest key
- `.sum_by do |x| val end` — sum the values the block returns

**Standard Library — Other**
- `sleep(n)` — pause execution for n seconds (float supported)
- `unzip(vec)` — inverse of zip: vector of pairs → vector of columns
- `format(fmt, ...)` — alias for `sprintf`

### Bug Fixes
- Block parameters named `p` (e.g. `do |p|`) now parse correctly — `p` was always tokenised as the debug-print keyword, preventing it from being used as a loop variable
- `p[...]` and `p.method` now correctly treated as variable access rather than a debug-print call
- `break if cond` and `next if cond` (postfix forms) parse without errors

---

## v1.4.0 (2025)

### New Features

**Web Server** (built-in `http.server` — zero deps)
- `web_app()` — create a new Frankie web application
- `app.get(path) do |req| end` — register a GET route
- `app.post(path) do |req| end` — register a POST route
- `app.put(path) do |req| end` — register a PUT route
- `app.delete(path) do |req| end` — register a DELETE route
- `app.patch(path) do |req| end` — register a PATCH route
- `app.before do |req| end` — before-filter (runs before every matched route)
- `app.after do |req, res| end` — after-filter (runs after every matched route)
- `app.not_found do |req| end` — custom 404 handler
- `app.run(port)` / `app.run(port, host)` — start the server (blocking, multi-threaded)
- Path parameters with `:name` segments: `"/users/:id"` → `req.params["id"]`
- Query string access: `req.query["page"]`
- JSON body parsing: `req.json` — returns parsed hash/vector or nil
- Form body parsing: `req.form` — returns decoded hash
- `response(body, status, headers)` — plain-text response
- `html_response(body, status)` — HTML response
- `json_response(data, status)` — JSON response (auto-serializes hashes and vectors)
- `redirect(location, status)` — redirect response (default 302)
- `halt(status, body)` — error response shortcut
- Returning a plain string from a handler auto-wraps as `200 text/plain`
- Returning a hash or vector auto-wraps as `200 application/json`
- Full request object: `.method`, `.path`, `.params`, `.query`, `.headers`, `.body`, `.json`, `.form`
- See `docs/09_web.md` and `examples/webapp.fk` for full reference and demo

### Bug Fixes
- `raise expr if cond` (postfix `if` on `raise`) now parsed correctly — was leaving the `if` clause unconsumed, causing `rescue` to be seen as an unexpected token in `begin/rescue` blocks
- `data |> sum |> puts` — `puts` and `print` now accepted as bare pipe targets (previously raised an unexpected token error)

---

## v1.3.0 (2025)

### New Features

**Language**
- Default parameter values: `def greet(name, msg="Hello", punct="!")`
- Keyword-named parameters (e.g. `times`, `each`) now usable as variable/param names
- Triple-quoted multi-line strings: `"""..."""` and `'''...'''` with interpolation

**JSON** (built-in `json` module — zero deps)
- `json_parse(str)` — parse JSON string → Frankie value
- `json_dump(obj, pretty)` — serialize to JSON string
- `json_read(path)` — read and parse JSON file
- `json_write(path, obj, pretty)` — serialize and write JSON file

**CSV** (built-in `csv` module — zero deps)
- `csv_parse(text, headers)` — parse CSV text → vector of hashes
- `csv_dump(data, headers)` — serialize vector of hashes → CSV string
- `csv_read(path, headers)` — read and parse CSV file
- `csv_write(path, data, headers)` — write CSV file

**DateTime** (built-in `datetime` module — zero deps)
- `now()` — current date and time
- `today()` — today's date at midnight
- `date_from(year, month, day, hour, minute, second)` — construct a date
- `date_parse(str, fmt)` — parse a date string (default fmt: `%Y-%m-%d`)
- `.year`, `.month`, `.day`, `.hour`, `.minute`, `.second` — accessors
- `.format(fmt)` — format with `strftime` directives
- `.add_days(n)`, `.add_hours(n)`, `.add_minutes(n)` — arithmetic
- `.diff_days(other)`, `.diff_seconds(other)` — differences
- `.weekday()`, `.weekday_name()` — day of week
- `.is_before(other)`, `.is_after(other)` — comparison
- `.timestamp()` — Unix timestamp

**HTTP** (built-in `urllib` — zero deps)
- `http_get(url, headers)` — GET request
- `http_post(url, data, headers)` — POST request (auto JSON-encodes dicts)
- `http_put(url, data, headers)` — PUT request
- `http_delete(url, headers)` — DELETE request
- Response: `.status`, `.body`, `.headers`, `.json()`, `.ok()`
- `url_encode(hash)` — encode params as query string
- `url_decode(str)` — decode query string → hash

**Tooling**
- `frankiec new <project>` — scaffold a new project with `main.fk`, `test.fk`, `lib/`, `data/`, `README.md`, `.gitignore`
- Better error messages — compile and runtime errors now show a boxed display with source context and line pointer (──▶)
- Syntax highlighting for **VS Code** (`.tmLanguage.json` + `package.json` + `language-configuration.json`)
- Syntax highlighting for **Vim/Neovim** (`frankie.vim`)
- Syntax highlighting for **Sublime Text / TextMate** (`frankie.tmLanguage.json`)
- All editor files in `editors/`

### Bug Fixes
- Fixed `print` output disappearing when running from a different working directory
- `times`, `each`, `map` keywords can now be used as parameter and variable names
- Template placeholders in `frankiec new` use `.replace()` to avoid `str.format()` key conflicts

---

## v1.2.0 (2025)

### New Features

**Database Access (SQLite)**
- `db_open(path)` — open or create a SQLite database; `":memory:"` for in-memory
- `db.exec(sql, params)` — run DDL/DML with `?` placeholders; returns row count
- `db.query(sql, params)` — SELECT → vector of hashes keyed by column name
- `db.query_one(sql, params)` — SELECT → first row as hash or nil
- `db.insert(table, hash)` — insert a hash of column→value; returns new row id
- `db.insert_many(table, rows)` — bulk insert a vector of hashes
- `db.find_all(table)` — all rows as vector of hashes
- `db.find(table, where)` — filtered rows (where is a hash, conditions ANDed)
- `db.find_one(table, where)` — first matching row or nil
- `db.update(table, data, where)` — update matching rows; returns count
- `db.delete(table, where)` — delete matching rows; returns count
- `db.count(table)` / `db.count(table, where)` — row counts
- `db.last_id` — rowid of last INSERT
- `db.tables` — list of table names in the database
- `db.columns(table)` — column info as vector of hashes
- `db.transaction do...end` — atomic block; rolls back on any error
- `db.begin` / `db.commit` / `db.rollback` — explicit transaction control
- `db.close` — close the connection
- Zero external dependencies — uses Python's built-in `sqlite3`

**Multi-line Strings**
- Triple-quoted strings `"""..."""` and `'''...'''` spanning multiple lines
- String interpolation `#{}` works inside triple-double-quoted strings
- Perfect for embedding multi-line SQL, templates, or long text

### Bug Fixes
- `isinstance(obj, FrankieDB)` cross-namespace failure — fixed with duck typing
  (`hasattr` checks instead) so DB objects work correctly inside `exec()` globals
- `db.delete(table, where)` was intercepted by string/hash delete handler — now
  correctly dispatches based on argument count (2 args = DB call)
- `.count("sub")` on a DB object was routing to `_fk_str_count` — fixed via
  `_fk_count_dispatch` with duck typing
- Transaction `BEGIN`/`COMMIT`/`ROLLBACK` now uses explicit `isolation_level=None`
  with an `_in_tx` flag for correct per-operation autocommit and block rollback

---

## v1.1.0 (2025)

### New Features

**Iterators & Collections**
- `.select do |x|` — filter elements where block is true
- `.reject do |x|` — filter elements where block is false
- `.reduce(init) do |acc, x|` — fold to a single value (also `.inject`)
- `.each_with_object(init) do |x, obj|` — iterate with shared accumulator
- `.any? do |x|` — true if any element matches
- `.all? do |x|` — true if all elements match
- `.none? do |x|` — true if no elements match
- `.count do |x|` — count matching elements (or `.count("sub")` for strings)
- `.flat_map do |x|` — map then flatten one level
- `.take(n)` — first n elements
- `.drop(n)` — all but first n elements
- `.tally` — count occurrences → Hash
- `.compact` — remove nil values
- `.chunk(n)` — split into sub-vectors of size n
- `.zip(other)` — zip two vectors together

**Control Flow**
- `case/when/else/end` — pattern matching on values or conditions
- Bare `case` (no subject) — uses truthy when-clauses

**Destructuring Assignment**
- `a, b, c = [1, 2, 3]` — unpack vector into named variables
- Pads with `nil` if vector is shorter than target count

**String Methods (new)**
- `.chars` — vector of individual characters
- `.bytes` — vector of byte values
- `.lines` — vector of lines
- `.chomp` — remove trailing newline
- `.chop` — remove last character
- `.count("sub")` — count substring occurrences
- `.center(w, pad)` — center in field
- `.ljust(w, pad)` — left-justify in field
- `.rjust(w, pad)` — right-justify in field
- `.squeeze` — collapse consecutive duplicates
- `.tr(from, to)` — translate characters
- `.each_char do |c|` — iterate over characters
- `.each_line do |l|` — iterate over lines
- `.lstrip` / `.rstrip` — directional whitespace trim

**REPL (Interactive Mode)**
- `frankiec repl` — starts the interactive REPL
- `frankiec` with no arguments also launches the REPL
- Multi-line block detection — automatically waits for `end`
- `vars` — show all user-defined variables and functions
- `clear` — reset the session
- `load <file.fk>` — load a file into the current session
- `help` — show available commands
- Persistent state across expressions in a session

### Bug Fixes
- `do...while` body was accidentally consuming the `while` keyword
- Postfix `if`/`unless` now works after `puts` (not just expressions)
- `matches()` and all regex functions had flipped argument order — fixed to `(string, pattern)`
- `s[-5..-1]` negative range ends now parse as `(-5)..(-1)` correctly
- `[x, x * 2]` vector literal with multiplication was mis-parsed as destructuring — fixed with backtracking
- `gen_pipe` method lost its `def` header during code insertion — restored
- `count` method now correctly dispatches: `.count("sub")` for strings, `.count do` for filtering, `.count` for length

### Compiler Version
- Version header in generated files updated to v1.1

---

## v1.0.0 (2025)

### Initial Release

**Core language**
- 7 data types: Integer, Float, String, Boolean, Nil, Vector, Hash
- Full arithmetic: `+`, `-`, `*`, `/`, `//`, `%`, `**`
- String interpolation with `#{}`
- Ranges: `1..10` (inclusive), `1...10` (exclusive)
- Conditionals: `if/elsif/else/end`, `unless/end`
- Postfix `if`/`unless`
- Loops: `while`, `until`, `do...while`, `for...in`
- Iterators: `.times`, `.each`, `.each_with_index`, `.map`
- Functions with `def...end` and explicit `return`
- Named arguments: `func(x, sep: "-")`
- Pipe operator `|>`
- Destructuring (v1.1)

**Collections**
- Vectors with R-style vectorized arithmetic
- Hashes with symbol and integer keys, nil-safe access
- Full method suites for both types

**Standard Library**
- Math: `sqrt`, `abs`, `floor`, `ceil`, `min`, `max`
- Statistics: `sum`, `mean`, `median`, `stdev`, `variance`
- Sequences: `seq`, `linspace`, `rep`, `clamp`
- String formatting: `sprintf`, `paste`
- Regex: `matches`, `match`, `match_all`, `sub`, `gsub`, `=~`, `regex()`
- File I/O: `file_read`, `file_write`, `file_append`, `file_lines`, `file_exists`, `file_delete`
- Type conversion: `to_int`, `to_float`, `to_str`
- Type checking: `is_integer`, `is_float`, `is_string`, `is_vector`, `is_nil`, `is_bool`
- System: `exit`, `argv`, `env`

**Error handling**
- `begin/rescue/ensure/end`
- `raise`

**Multi-file**
- `require "filename"` — load another `.fk` file once

**Tooling**
- `frankiec run` — run a program
- `frankiec build` — compile to Python source
- `frankiec check` — syntax check
- `frankiec version`
- `python3 install.py` — install `frankiec` to `frankie/bin/`
