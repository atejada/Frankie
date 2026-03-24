# Frankie v1.9 — New Feature Reference

## Overview

v1.9 brings tooling maturity and two language additions that make Frankie
significantly more productive for real projects.

| Feature | Summary |
|---|---|
| **Record types** | `record Point(x, y)` — lightweight named data objects |
| **Hash `.dig`** | Safe nested access that returns `nil` instead of crashing |
| **Standalone `zip()`** | `zip(a, b)` function form alongside the existing `.zip` method |
| **`frankiec fmt`** | AST-based auto-formatter — canonical style, zero config |
| **`frankiec docs`** | Extract `##` doc-comments to Markdown |
| **readline REPL** | Arrow keys, Ctrl+R search, tab completion |
| **History persistence** | `~/.frankie_history` saved and restored across sessions |
| **`.env` auto-loader** | `.env` loaded automatically by `frankiec run` and `frankiec repl` |

---

## Record Types

Records are lightweight named data objects. They compile to constructor
functions that return a hash with a `__type__` field — so every hash method
works on them, and they print with a clean `RecordName(field: value)` format.

### Syntax

```ruby
record RecordName(field1, field2, field3)
```

### Examples

```ruby
record Point(x, y)
record Color(r, g, b)
record Employee(name, dept, salary)

# Construct with a function call
p1  = Point(3, 4)
red = Color(255, 0, 0)
emp = Employee("Alice", "Engineering", 95000)

# Pretty-printing
puts p1    # Point(x: 3, y: 4)
puts red   # Color(r: 255, g: 0, b: 0)
puts emp   # Employee(name: Alice, dept: Engineering, salary: 95000)

# Field access — records are hashes
puts p1["x"]             # 3
puts emp["dept"]         # Engineering
puts p1.has_key?("y")    # true
puts p1["__type__"]      # Point
```

### Records with iterators

Because records are hashes, every Frankie iterator works on them directly:

```ruby
record Product(name, category, price)

products = [
  Product("Widget",  "Hardware", 9.99),
  Product("Gadget",  "Hardware", 24.99),
  Product("Doohick", "Software", 4.99),
]

# group_by
by_cat = products.group_by do |p| p["category"] end
puts by_cat["Hardware"].length    # 2

# sort_by
cheapest = products.sort_by do |p| p["price"] end.first
puts cheapest["name"]    # Doohick

# select + map
hw_names = products.select do |p|
  p["category"] == "Hardware"
end.map do |p|
  p["name"]
end
puts hw_names    # [Widget, Gadget]
```

### Records and `.dig`

```ruby
record Server(host, port)

config = {
  primary:   Server("db1.local", 5432),
  secondary: Server("db2.local", 5432)
}

puts config.dig("primary", "host")   # db1.local
```

### Notes

- Records are hashes under the hood — mutation, merge (`|`), and all hash
  methods work normally.
- The `__type__` key is reserved and set automatically by the constructor.
- There is no inheritance — records are data containers, not classes.
- Field names must be valid Frankie identifiers.

---

## Hash `.dig` — Safe Nested Access

`dig` traverses a nested hash (or vector) by a sequence of keys, returning
`nil` at the first missing key instead of crashing.

### Syntax

```ruby
hash.dig(key1, key2, ...)       # hash traversal
vector.dig(index1, index2, ...) # vector traversal (integer indices)
```

### Examples

```ruby
config = {db: {host: "localhost", pool: {min: 2, max: 10}}}

# Safe two-level access
puts config.dig("db", "host")         # localhost

# Three levels — no defensive coding needed
puts config.dig("db", "pool", "max")  # 10

# Missing keys return nil cleanly
puts config.dig("db", "missing")      # nil
puts config.dig("nope", "host")       # nil  (top-level miss)

# Chains with &. for nil-safe navigation
user = nil
puts user&.dig("profile", "name")     # nil
```

### Nested vectors

```ruby
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

puts matrix.dig(1, 2)    # 6  (row 1, col 2)
puts matrix.dig(9, 0)    # nil  (out of bounds — no crash)
```

### Before and after

```ruby
# Before v1.9 — crashes if any level is nil
host = config["db"]["pool"]["min"]   # ZeroDivisionError if "pool" is nil

# After v1.9 — always safe
host = config.dig("db", "pool", "min")   # nil if anything is missing
```

---

## Standalone `zip()`

`zip` is now available as both a method (`.zip`) and a standalone function
(`zip(a, b)`), consistent with Frankie's R-inspired functional style.

### Syntax

```ruby
zip(vec1, vec2, ...)          # two or more vectors
vec1.zip(vec2)                # method form (unchanged from v1.3)
```

Both forms stop at the shortest input vector.

### Examples

```ruby
names  = ["Alice", "Bob", "Carol"]
scores = [95, 87, 92]

# Standalone function — natural for pipelines
pairs = zip(names, scores)
pairs.each do |pair|
  puts "#{pair[0]}: #{pair[1]}"
end

# Three-way zip
ids = [1, 2, 3]
rows = zip(ids, names, scores)
rows.each do |row|
  puts "#{row[0]}. #{row[1]} — #{row[2]}"
end

# Build a hash from two vectors
keys = ["host", "port", "db"]
vals = ["localhost", 5432, "myapp"]
config = zip(keys, vals).reduce({}) do |acc, pair|
  acc[pair[0]] = pair[1]
  acc
end
puts config.dig("host")   # localhost
```

---

## `frankiec fmt` — Auto-Formatter

The formatter parses your source into an AST and reprints it in a canonical
style. Output is always syntactically valid — if it formats, it compiles.

### Usage

```bash
# Print formatted output to stdout
frankiec fmt myfile.fk

# Reformat in-place
frankiec fmt --write myfile.fk

# CI mode — exit 1 if not already formatted
frankiec fmt --check myfile.fk

# Format multiple files
frankiec fmt --write lib/*.fk
```

### Canonical style

| Rule | Detail |
|---|---|
| Indentation | 2 spaces |
| Blocks | Multi-statement blocks use `do...end` on separate lines |
| Single-expr blocks | Inlined: `.each do \|x\| puts x end` |
| Hash literals | `{key: value, other: val}` |
| Lambdas | Single-expr: `->(x) { x * 2 }`, multi: `do...end` |
| Blank lines | One blank line after top-level `def` blocks |
| Trailing newline | Always present |

### Example

Before:
```ruby
def greet(   name,  msg="Hello"  )
x="#{msg}, #{name}!"
return x
end
```

After `frankiec fmt --write`:
```ruby
def greet(name, msg = "Hello")
  x = "#{msg}, #{name}!"
  return x
end
```

---

## `frankiec docs` — Documentation Generator

Extract `##` doc-comments from `.fk` source files and render them as Markdown.

### Doc-comment syntax

```ruby
## Brief description of what this function does.
## Longer explanation can span multiple lines.
##
## @param name   The person's name
## @param age    Their age in years
## @return       A greeting string
## @example
##   result = greet("Alice", 30)
##   puts result     # Hello, Alice! (age 30)
def greet(name, age)
  return "Hello, #{name}! (age #{age})"
end

## A point in 2D space.
## @param x  Horizontal coordinate
## @param y  Vertical coordinate
record Point(x, y)
```

### Usage

```bash
# Markdown to stdout
frankiec docs lib/utils.fk

# Write to file
frankiec docs --output docs/api.md lib/utils.fk

# All .fk files in a directory
frankiec docs lib/
```

### Output example

Running `frankiec docs lib/utils.fk` produces:

```markdown
# utils

*Auto-generated from `utils.fk` by `frankiec docs`*

## Functions

### 🔧 `greet(name, age)`

Brief description of what this function does.

**Parameters:**
- `name` — The person's name
- `age` — Their age in years

**Returns:** A greeting string

**Example:**
```ruby
result = greet("Alice", 30)
puts result     # Hello, Alice! (age 30)
```
```

---

## REPL: readline, Tab Completion, History

### Arrow keys and history search

The REPL now uses Python's built-in `readline` module:

| Key | Action |
|---|---|
| `↑` / `↓` | Browse command history |
| `Ctrl+R` | Reverse-search through history |
| `Ctrl+A` / `Ctrl+E` | Jump to start / end of line |
| `Ctrl+K` | Delete to end of line |
| `Tab` | Complete Frankie keywords and method names |

### History persistence

History is saved to `~/.frankie_history` when you exit the REPL (via `exit`,
`quit`, or Ctrl+D). It is restored automatically at startup, so every session
picks up where the last one left off.

```bash
frankiec repl
# fk> double = ->(x) { x * 2 }   ← typed in a previous session
# fk> ↑                           ← press up: history restored
```

The history file keeps the last 1000 entries.

---

## `.env` Auto-Loader

`frankiec run` and `frankiec repl` now automatically load a `.env` file from
the current working directory into `os.environ` before execution. Values are
then accessible via the existing `env()` stdlib function.

### `.env` format

```bash
# .env
DB_PATH=data/myapp.db
API_KEY=secret123
DEBUG=true
PORT=3000
```

### Accessing in Frankie

```ruby
db   = env("DB_PATH", "data/default.db")
port = to_int(env("PORT", "3000"))
debug = env("DEBUG", "false") == "true"

puts "Connecting to #{db} on port #{port}"
```

### Rules

- Lines starting with `#` are comments and are ignored.
- Values are trimmed of surrounding quotes (`"` or `'`).
- Variables already set in the shell environment take precedence — `.env`
  values are only applied when the key is not already present in `os.environ`.
- The `.env` file is never required — if it doesn't exist, startup proceeds
  normally.
- `.env` is already in the `.gitignore` generated by `frankiec new`.

---

## Formatter in `frankie_fmt.py`

The formatter is also importable as a Python module for build tooling:

```python
from frankie_fmt import fmt_source, fmt_file

# Format a string
formatted = fmt_source("x=1\nputs x\n")

# Format a file (write=True for in-place, check=True for CI)
ok = fmt_file("myfile.fk", write=True)
```
