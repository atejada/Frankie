# Changelog

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
