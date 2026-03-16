# Changelog

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
