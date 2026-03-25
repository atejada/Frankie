# Frankie v1.10 — New Feature Reference

## Overview

v1.10 focuses on polish and filling the gaps — every feature here is something
a new user hits in their first hour.

| Feature | Summary |
|---|---|
| **String `*` repetition** | `"ha" * 3` → `"hahaha"`, `[0] * 5` → `[0,0,0,0,0]` |
| **Heredoc `<<~TEXT`** | Multiline strings with automatic indent-stripping and `#{}` interpolation |
| **`times()` standalone** | `times(5) do \|i\|` alongside the existing `5.times do` method form |
| **`flatten(depth)`** | Full deep flatten or `flatten(n)` for a specific number of levels |
| **`map_with_index`** | `.map_with_index do \|x, i\|` — index available inside map |
| **`pp` pretty-print** | Indented multiline output for nested hashes and records |
| **Named rescue** | `rescue TypeError` without requiring a binding variable |
| **`encode` / `decode`** | `"hello".encode` → bytes vector; `bytes.decode` → string |
| **Exit code propagation** | `exit(42)` now propagates to the shell; `echo $?` works |
| **`--help` flag** | `frankiec --help` and `frankiec <cmd> --help` |

---

## String & Vector `*` Repetition

The `*` operator now works on strings and vectors when one side is an integer.

```ruby
puts "ha" * 3           # hahaha
puts "-" * 40           # ----------------------------------------
puts [0] * 5            # [0, 0, 0, 0, 0]
puts [1, 2] * 3         # [1, 2, 1, 2, 1, 2]
puts 3 * "hi"           # hihihi  (integer on left also works)
```

### Practical uses

```ruby
# Table separator
cols = [12, 8, 10]
sep = cols.map do |w| "-" * w end.join("+")
puts sep    # ------------+--------+----------

# Fixed-size fill
row = [nil] * 10
puts row.length    # 10

# Center a title
title = "[ Results ]"
width = 40
pad = " " * ((width - title.length) // 2)
puts pad + title
```

---

## Heredoc `<<~TEXT`

Heredocs let you write multiline strings without escaping newlines. The `<<~`
variant strips the common leading whitespace from every line, so you can indent
your source naturally.

### Syntax

```ruby
variable = <<~DELIMITER
  content line 1
  content line 2
DELIMITER
```

The closing delimiter must appear alone on its own line. Any identifier works
as the delimiter (`TEXT`, `SQL`, `HTML`, `QUERY`, `END`, etc.).

### Examples

```ruby
# SQL query — no escaping, indents cleanly
query = <<~SQL
  SELECT name, dept, salary
  FROM employees
  WHERE salary > 80000
  ORDER BY salary DESC
SQL
puts query

# HTML template
html = <<~HTML
  <article>
    <h1>Hello</h1>
    <p>From Frankie.</p>
  </article>
HTML

# String interpolation works inside heredocs
version = "1.10"
banner = <<~BANNER
  ┌────────────────────────┐
  │  Frankie #{version} is alive!  │
  └────────────────────────┘
BANNER
puts banner
```

### `<<~` vs `<<`

| | `<<~TEXT` | `<<TEXT` |
|---|---|---|
| Indent stripping | Yes — strips common leading whitespace | No — content is literal |
| Typical use | Normal code with indented heredoc body | Rare — when exact indentation matters |

---

## `times()` Standalone Function

`5.times do |i|` has always worked. Now `times(5) do |i|` works too — the
functional form is more natural when composing or passing counts as variables.

```ruby
# Method form (unchanged)
5.times do |i|
  puts i
end

# Standalone function form (v1.10)
times(5) do |i|
  puts i
end

# No-block form — returns a list (useful with map, select, etc.)
puts times(5)             # [0, 1, 2, 3, 4]

indices = times(10).select do |i| i % 2 == 0 end
puts indices              # [0, 2, 4, 6, 8]

# Build n copies of a record
record Row(id, active)
rows = times(4).map do |i| Row(i + 1, true) end
rows.each do |r| puts r end
```

---

## `flatten(depth)`

`.flatten` with no argument now does a **full deep** flatten instead of
one level. Pass a depth integer to control how many levels to unwrap.

```ruby
nested = [1, [2, 3], [4, [5, [6, 7]]]]

puts nested.flatten        # [1, 2, 3, 4, 5, 6, 7]   — all levels
puts nested.flatten(1)     # [1, 2, 3, 4, [5, [6, 7]]] — one level
puts nested.flatten(2)     # [1, 2, 3, 4, 5, [6, 7]]   — two levels
puts nested.flatten(0)     # [1, [2, 3], [4, [5, [6, 7]]]] — no-op
```

**Note:** This is a breaking change from v1.9 where `.flatten` only flattened
one level. Use `.flatten(1)` to get the old behaviour explicitly.

---

## `map_with_index`

`.map_with_index do |element, index|` gives you the index inside a map block
without needing `.each_with_index` and a manual accumulator.

```ruby
words = ["Ruby", "Python", "R", "Fortran"]

numbered = words.map_with_index do |w, i|
  "#{i + 1}. #{w}"
end
puts numbered    # [1. Ruby, 2. Python, 3. R, 4. Fortran]

# Useful for building position-aware structures
cells = ["A", "B", "C"].map_with_index do |val, col|
  {col: col, val: val, label: "#{val}#{col}"}
end
cells.each do |c| puts c end
```

---

## `pp` — Pretty-Print

`pp(value)` prints deeply nested hashes, vectors, and record types with
indented multiline output. Use it instead of `puts json_dump(thing)` when
you need human-readable debug output.

```ruby
data = {
  server: {host: "localhost", port: 3000},
  db:     {path: "app.db", pool: {min: 2, max: 10}},
  tags:   ["production", "v1.10"]
}
pp(data)
```

Output:
```
{
  server:
    {
      host: localhost,
      port: 3000
    }
  db:
    {
      path: app.db,
      pool:
        {
          min: 2,
          max: 10
        }
    }
  tags:
    [production, v1.10]
}
```

Records print with their type name:

```ruby
record Point(x, y)
pp(Point(3, 4))
# Point(
#   x: 3,
#   y: 4
# )
```

---

## Named Rescue Without Variable

`rescue TypeName` no longer requires a binding variable. This is the natural
form when you want to catch a specific error type but don't need the message.

```ruby
# Before v1.10 — required variable even if unused
begin
  x = 1 // 0
rescue ZeroDivisionError e
  puts "caught"
end

# v1.10 — variable is optional
begin
  x = 1 // 0
rescue ZeroDivisionError
  puts "caught cleanly"
end

# Multiple typed clauses, no variables
begin
  risky_operation()
rescue ZeroDivisionError
  puts "divide by zero"
rescue TypeError
  puts "type mismatch"
rescue RuntimeError e
  puts "runtime: #{e}"    # variable still available when needed
end
```

---

## `encode` / `decode`

Convert strings to and from vectors of byte integers.

```ruby
b = "hello".encode              # [104, 101, 108, 108, 111]
puts b.decode                   # hello

# Explicit encoding
puts "hi".encode("utf-8")       # [104, 105]
puts [70, 114, 97, 110, 107, 105, 101].decode   # Frankie

# Useful for checksums, byte manipulation, network protocols
bytes = "GET / HTTP/1.1".encode
puts bytes.length               # 14
```

---

## Exit Code Propagation

`exit(n)` now propagates the exact exit code to the shell. This makes Frankie
scripts composable with shell pipelines, Makefiles, and CI systems.

```ruby
# script.fk
result = run_checks()
if result == false
  exit(1)    # signal failure to the shell
end
exit(0)      # explicit success
```

```bash
frankiec run script.fk
echo $?    # 0 or 1 as set by the Frankie program

# In a Makefile or CI:
frankiec run test.fk || exit 1
```

---

## `--help` Flag

```bash
frankiec --help           # Full usage listing
frankiec run --help       # frankiec run <file.fk> — Run a Frankie program...
frankiec fmt --help       # frankiec fmt [--write] [--check] <file.fk>...
frankiec docs --help      # frankiec docs [--output <out.md>] <file.fk|dir>...
frankiec test --help      # frankiec test [file.fk]...
```

Every command now has a short help description accessible with `--help`.
