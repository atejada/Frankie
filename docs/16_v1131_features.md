# Frankie v1.13.1 — Feature Reference

## Overview

v1.13.1 closes the gaps that actually bite. No new syntax, no new concepts — everything here is something real programs needed and didn't have.

| Feature | Category | Summary |
|---|---|---|
| **`frankiestring` v2** | stitch | Replaced clunky `lfill`/`rfill` API with `pad_left`, `pad_right`, `truncate`, `slugify`, `word_wrap`, `indent_lines` |
| **Vector `.sum do`** | stdlib | Block form now works — projected sums without a two-step map+sum |
| **Vector `.flat_map do`** | stdlib | Multi-line block form now works correctly |
| **`assert_approx_eq`** | stdlib | Float comparison in tests with a configurable delta |
| **`session(req, resp)`** | web | Cookie-backed session hash — read, mutate, save, zero server state |
| **`frankiec fmt`** | tooling | Blank lines inside function bodies preserved; long hashes/vectors expand to multi-line; idempotent |

---

## `frankiestring` v2

The `frankiestring` stitch has been rewritten with a clean, Frankie-convention API. The old `lfill`/`rfill` functions (clunky argument order, misleading names) are replaced.

```ruby
stitch "frankiestring"

pad_left("42", 6, "0")           # "000042"  — right-align, zero-fill
pad_right("hello", 10, ".")      # "hello....."  — left-align, dot-fill

truncate("Frankie is a dynamically-typed language", 20, "...")
# "Frankie is a dynami..."

slugify("Hello World! This is Frankie.")
# "hello-world-this-is-frankie"

word_wrap("The quick brown fox jumps over the lazy dog", 20)
# "The quick brown fox\njumps over the lazy\ndog"

indent_lines("line one\nline two\nline three", 4)
# "    line one\n    line two\n    line three"
```

All six functions accept plain strings and return plain strings — no method extension, no magic.

| Function | Signature | Description |
|---|---|---|
| `pad_left` | `(str, n, char)` | Right-align `str` in a field of width `n`, filled with `char` |
| `pad_right` | `(str, n, char)` | Left-align `str` in a field of width `n`, filled with `char` |
| `truncate` | `(str, n, suffix)` | Trim to `n` chars and append `suffix` if the string was longer |
| `slugify` | `(str)` | Lowercase, replace non-alphanumeric runs with `-`, strip leading/trailing `-` |
| `word_wrap` | `(str, width)` | Break at word boundaries to fit within `width` characters per line |
| `indent_lines` | `(str, n)` | Prepend `n` spaces to every line in a multi-line string |

---

## Vector `.sum do`, `.flat_map do`

### `.sum do |x| ... end`

Projected sum — the block maps each element to a number, then sums the results. Replaces the two-step `.map do ... end |> sum` pattern.

```ruby
products = [
  {name: "apple", price: 0.99, qty: 4},
  {name: "bread", price: 2.49, qty: 2},
  {name: "milk",  price: 1.79, qty: 3}
]

total = products.sum do |item|
  item["price"] * item["qty"]
end
puts total   # 14.31
```

`.sum_by` is an alias for the same operation — both work identically.

### `.flat_map do |x| ... end`

Map each element to a vector, then flatten one level. Multi-line block bodies now work correctly (previously failed with a parse error).

```ruby
sentences = [["hello", "world"], ["frankie", "is", "fun"]]
words = sentences.flat_map do |group|
  group
end
puts words   # [hello, world, frankie, is, fun]
```

`.count do` was already working in v1.13 and is confirmed here:

```ruby
nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
evens = nums.count do |x|
  x % 2 == 0
end
puts evens   # 5
```

---

## `assert_approx_eq(actual, expected, delta, msg)`

Float comparison in tests no longer requires `assert_true(abs(a - b) < 0.001, ...)`. The delta defaults to `0.001` if omitted.

```ruby
assert_approx_eq(3.14159, 3.14,   0.01,    "pi to 2 places")
assert_approx_eq(sqrt(2), 1.4142, 0.0001,  "sqrt(2)")
assert_approx_eq(mean([1.0, 2.0, 3.0]), 2.0, 0.001, "mean of 1..3")

# Default delta (0.001)
assert_approx_eq(0.1 + 0.2, 0.3, "float addition")

run_tests()
```

On failure, the output shows the actual difference:

```
  ✗  expected 1.0 ≈ 2.0 within 0.5, diff was 1.0
```

`run_tests()` is now also available as a public stdlib function — callable from any `.fk` file, not just `frankiec test`.

---

## Web Session Helper

`session(req, resp)` gives you a hash-like object backed by a single JSON cookie (`_fk_session`). No server-side state, no database, no configuration.

```ruby
app = web_app()

app.get("/counter") do |req|
  resp = response("")
  s = session(req, resp)

  count = (s["count"] or 0) + 1
  s["count"] = count
  s.save()

  html_response("You have visited #{count} time(s).")
end

app.get("/reset") do |req|
  resp = response("")
  s = session(req, resp)
  s.clear()
  s.save()
  redirect("/counter")
end

app.run()
```

### Session API

| Method | Description |
|---|---|
| `s["key"]` | Read a value (returns `nil` if missing) |
| `s["key"] = value` | Write a value |
| `s.has_key?(key)` | Check if key exists |
| `s.keys` | List all session keys |
| `s.delete(key)` | Remove a single key |
| `s.clear()` | Remove all session data |
| `s.save()` | Write updated session back to the response cookie |

**Call `.save()` before returning the response** — unsaved mutations are silently discarded.

The session cookie is `HttpOnly`, `SameSite=Lax`, and scoped to `/`. It is **not encrypted** — do not store passwords, tokens, or sensitive data in it. Store a user ID and look up the rest from a database.

---

## `frankiec fmt` Improvements

### Blank lines inside function bodies

The formatter now preserves intentional blank lines between statement groups inside function bodies, `if` branches, loops, and blocks. Blank lines in the original source are re-emitted in the formatted output.

```ruby
# Before: blank lines stripped
def process(data)
  validate(data)

  result = transform(data)

  save(result)
end

# After fmt: blank lines preserved — output is identical to input
```

### Long hashes and vectors expand to multi-line

Hashes and vectors whose inline form would exceed 60 characters are automatically expanded to one element per line:

```ruby
# Short — stays inline
h = {name: "Alice", age: 30}

# Long — expands to multi-line
config = {
  "host": "localhost",
  "port": 3000,
  "debug": true,
  "log_level": "info",
  "timeout": 30
}
```

### Idempotency

Running `frankiec fmt --write` twice now produces identical output in all cases. The formatter is safe to use in pre-commit hooks and CI pipelines.

```bash
frankiec fmt --write myfile.fk
frankiec fmt --check myfile.fk   # exits 0 — already formatted
```
