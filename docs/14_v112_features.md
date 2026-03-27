# Frankie v1.12 — New Feature Reference

## Overview

v1.12 fills the most-requested gaps in the stdlib, tightens error messages, and adds two long-overdue tooling conveniences — all with zero new dependencies.

| Feature | Category | Summary |
|---|---|---|
| **`String .gsub` with block** | stdlib | Transform each match with a block instead of a fixed string |
| **`Hash .map_hash do \|k, v\|`** | stdlib | Map a hash to a new hash in one step |
| **`assert_match` / `assert_nil`** | tooling | Two obviously-missing test assertions |
| **Friendlier runtime errors** | runtime | Type mismatch and index errors read as Frankie messages, not Python internals |
| **`FileNotFoundError` from file I/O** | runtime | `rescue FileNotFoundError` now actually works for `file_read` / `file_lines` |
| **`Vector .each_with_object` + hash** | stdlib | Hash accumulator now documented and tested |
| **`String .chars`** | stdlib | Promoted to first-class documented method alongside `.bytes` and `.lines` |
| **`frankiec watch <file.fk>`** | tooling | Re-run on save — zero dependencies |
| **`Vector .product(other)`** | stdlib | Cartesian product — pure nested loop, no `itertools` |
| **`frankiec repl --no-banner`** | tooling | Skip the ASCII header for piped/embedded use |
| **`round(x, n)`** | stdlib | Round to N decimal places — finally |

---

## String `.gsub` with Block

The block form of `gsub` is what you reach for when you need to transform each match, not replace it with a fixed string. The pattern regex engine was already in place — this just loops over matches and passes each to the block.

```ruby
# Upcase every vowel
result = "hello world".gsub("[aeiou]") do |m|
  m.upcase
end
puts result   # → "hEllO wOrld"

# Redact digits
masked = "Card: 4111-1111-1111-1111".gsub("\\d") do |m|
  "*"
end
puts masked   # → "Card: ****-****-****-****"

# Transform matched words with arbitrary logic
words = "one two three".gsub("\\w+") do |m|
  m.length.to_s
end
puts words    # → "3 3 5"
```

The block receives the matched substring as its only argument. The return value of the block becomes the replacement string.

---

## Hash `.map_hash do |k, v|`

`.map` on a hash already returned a vector of pairs. `.map_hash` returns a new hash, making hash transformation idiomatic in one step.

```ruby
prices = {apple: 1.20, banana: 0.50, cherry: 3.00}

# Double all values
doubled = prices.map_hash do |k, v|
  [k, v * 2]
end
puts doubled   # → {apple: 2.4, banana: 1.0, cherry: 6.0}

# Upcase all keys
upcased = {a: 1, b: 2}.map_hash do |k, v|
  [k.to_s.upcase, v]
end
puts upcased   # → {"A": 1, "B": 2}

# Filter-and-transform: drop cheap items, mark expensive ones
flagged = prices.map_hash do |k, v|
  [k, v > 1.0 ? "expensive" : "cheap"]
end
puts flagged   # → {apple: "expensive", banana: "cheap", cherry: "expensive"}
```

The block must return a two-element vector `[new_key, new_value]`. Any other return raises a runtime error with a clear message.

---

## `assert_match` and `assert_nil`

Two assertions every test suite needs but had to fake with `assert_true(matches(...))` and `assert_eq(x, nil)`.

```ruby
describe "string patterns" do
  assert_match("hello@example.com", "\\w+@\\w+\\.\\w+", "valid email format")
  assert_match("2024-01-15", "^\\d{4}-\\d{2}-\\d{2}$", "ISO date format")
end

describe "optional values" do
  result = find_user(999)
  assert_nil(result, "missing user returns nil")

  assert_nil(ENV["MISSING_KEY"], "missing env var is nil")
end
```

`assert_match(value, pattern, msg)` — checks that `pattern` matches anywhere in `value`. Pattern can be a regex literal or a string.

`assert_nil(value, msg)` — checks that `value` is `nil`. Cleaner and more descriptive than `assert_eq(x, nil)`.

---

## Friendlier Runtime Error Messages

Runtime errors no longer expose raw Python internals. The error box now shows Frankie-idiomatic descriptions.

**Before:**
```
╔══ Frankie Runtime Error ══════════════════════════════
║  Wrong type for operation
╚═══════════════════════════════════════════════════════
```

**After:**
```
╔══ Frankie Runtime Error ══════════════════════════════
║  Type mismatch — can't use '+' with Integer and String
╚═══════════════════════════════════════════════════════
```

Similarly for index errors:
```
╔══ Frankie Runtime Error ══════════════════════════════
║  Index out of bounds — vector index does not exist
╚═══════════════════════════════════════════════════════
```

---

## `FileNotFoundError` from File I/O

`file_read` and `file_lines` previously raised `RuntimeError`, which meant `rescue FileNotFoundError` silently did nothing. They now raise a proper `FileNotFoundError`, so defensive file handling works as expected.

```ruby
# This now works correctly — previously caught nothing
begin
  content = file_read("config.json")
rescue FileNotFoundError e
  puts "Config missing: #{e}"
  content = "{}"
end

# file_lines too
begin
  rows = file_lines("data.csv")
rescue FileNotFoundError e
  puts "No data file found — starting fresh"
  rows = []
end
```

The error message is also cleaner — no more `[Frankie]` prefix inside the box that already says `Frankie Runtime Error`.

**Consistent file I/O behaviour:**

| Function | Missing file | Rationale |
|---|---|---|
| `file_read(path)` | raise `FileNotFoundError` | Caller asked for content that doesn't exist |
| `file_lines(path)` | raise `FileNotFoundError` | Same |
| `file_copy(src, dst)` | raise `FileNotFoundError` | Source must exist |
| `file_rename(src, dst)` | raise `FileNotFoundError` | Source must exist |
| `file_delete(path)` | return `false` | Idempotent — already gone is fine |
| `file_exists(path)` | return `false` | That's literally what the function asks |

---

## `Vector .each_with_object` with Hash Accumulator

The method already existed but was only tested with vector accumulators. Hash accumulators work naturally — now documented and tested.

```ruby
# Build a frequency map
freq = ["a", "b", "a", "c", "b", "a"].each_with_object({}) do |x, h|
  h[x] = (h[x] || 0) + 1
end
puts freq   # → {"a": 3, "b": 2, "c": 1}

# Build a lookup hash from a vector of records
lookup = [1, 4, 9, 16].each_with_object({}) do |x, h|
  h[x] = sqrt(x).to_i
end
puts lookup   # → {1: 1, 4: 2, 9: 3, 16: 4}
```

---

## `String .chars`

`.chars` has been in the method map since v1.0 and `.each_char` was already documented, but `.chars` itself was nowhere in the docs or examples. It's now a first-class documented method.

```ruby
# Chain into iterators
vowels = "hello world".chars.select do |c|
  "aeiou".include?(c)
end
puts vowels   # → ["e", "o", "o"]

# Count unique characters
unique = "mississippi".chars.uniq.length
puts unique   # → 4

# Reverse a string character by character
reversed = "Frankie".chars.reverse.join("")
puts reversed   # → "eiknarF"
```

---

## `frankiec watch <file.fk>`

Re-run your Frankie program automatically whenever you save. Invaluable for iterative scripting and teaching. Zero dependencies — polls `os.stat` mtime in a loop.

```bash
# Re-run on every save
frankiec watch main.fk

# Re-run tests on every save
frankiec watch test.fk --test
```

Output on each save:

```
[Frankie] Watching 'main.fk' — will re-run on save. Ctrl-C to stop.

[Frankie] ── Running main.fk ──────────────────────────
Hello, world!

[Frankie] ── Running main.fk ──────────────────────────
Hello, Frankie!
```

Press `Ctrl-C` to stop watching.

---

## `Vector .product(other)`

Cartesian product — every combination of elements from two vectors. Natural companion to `.zip` and `.zip_with`. Pure nested loop, no `itertools`.

```ruby
suits  = ["♠", "♥", "♦", "♣"]
values = ["A", "K", "Q", "J"]

# All face card combinations
face_cards = suits.product(values)
puts face_cards.length   # → 16
puts face_cards.first    # → ["♠", "A"]

# Grid coordinates
xs = [0, 1, 2]
ys = [0, 1, 2]
grid = xs.product(ys)
puts grid   # → [[0,0],[0,1],[0,2],[1,0],[1,1],[1,2],[2,0],[2,1],[2,2]]
```

---

## `frankiec repl --no-banner`

Skip the ASCII art and version header when you need the REPL embedded in another tool or piped into a script.

```bash
# Normal REPL — prints the banner
frankiec repl

# Headless — no banner, just the prompt
frankiec repl --no-banner

# Pipe expressions in without the banner noise
echo 'puts 2 + 2' | frankiec repl --no-banner
```

---

## `round(x, n)`

Round a number to N decimal places. Strikingly absent until now — you could `floor` and `ceil` but not round to a specific precision.

```ruby
puts round(3.14159, 2)   # → 3.14
puts round(2.71828, 3)   # → 2.718
puts round(1.5)          # → 2     (n defaults to 0)
puts round(99.999, 1)    # → 100.0

# Useful for display and comparison
prices = [1.2345, 9.8765, 4.5005]
display = prices.map do |p|
  round(p, 2)
end
puts display   # → [1.23, 9.88, 4.5]
```

`round(x)` with no second argument rounds to the nearest integer (same as `round(x, 0)`).
