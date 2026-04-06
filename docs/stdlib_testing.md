# Testing

## Overview

Frankie has a built-in test runner — no external libraries, no configuration. Write assertions in any `.fk` file and run it with `frankiec test`. Every assertion prints a ✓ or ✗ in real time, and the runner exits with code 1 if any test fails, making it CI-friendly.

---

## Running Tests

```bash
frankiec test             # runs test.fk in the current directory
frankiec test mytest.fk   # runs a specific file
```

Output looks like:

```
╔══ Frankie Test Runner ════════════════════════════════
║  test.fk
╠═══════════════════════════════════════════════════════
  ✓  addition works
  ✓  mean of [1,2,3] is 2.0
  ✗  expected 4, got 5
  ✓  FileNotFoundError raised on missing file

╠═══════════════════════════════════════════════════════
║  3/4 passed, 1 failed  (12.3ms)
╚═══════════════════════════════════════════════════════
```

---

## Assertions

All assertion functions are available without any import inside a test file.

### `assert_eq(actual, expected, msg)` — Equality

The workhorse. Passes if `actual == expected`.

```ruby
assert_eq(2 + 2,            4,     "addition")
assert_eq(mean([1,2,3]),    2.0,   "mean of 1..3")
assert_eq("hello".upcase,  "HELLO", "upcase")
assert_eq([1,2,3].length,  3,     "vector length")
```

### `assert_neq(actual, expected, msg)` — Inequality

Passes if `actual != expected`.

```ruby
assert_neq(rand_int(1, 100), 0, "rand_int never returns 0")
assert_neq("hello", "",         "non-empty string")
```

### `assert_true(value, msg)` — Truthy

Passes if `value` is truthy (anything except `false` and `nil`).

```ruby
assert_true(file_exists("/tmp"),         "tmp dir exists")
assert_true([1,2,3].include?(2),         "include? works")
assert_true("hello".start_with?("he"),   "start_with?")
assert_true(5 > 3,                       "comparison")
```

### `assert_nil(value, msg)` — Nil check

Passes if `value` is `nil`.

```ruby
assert_nil(find_user(999),      "missing user returns nil")
assert_nil([1,2,3].find do |x| x > 9 end, "find with no match")
assert_nil({a: 1}["missing"],   "missing hash key is nil")
```

### `assert_match(value, pattern, msg)` — Regex match

Passes if `pattern` matches anywhere in `value`.

```ruby
assert_match("alice@example.com", "\\w+@\\w+\\.\\w+", "valid email")
assert_match("2024-03-15",        "^\\d{4}-\\d{2}-\\d{2}$", "ISO date")
assert_match("Error: timeout",    "timeout",  "error message contains timeout")
```

### `assert_raises(fn, msg)` — Any error raised

Passes if calling `fn` raises any error.

```ruby
assert_raises(def()
  x = 1 // 0
end, "division by zero raises")

assert_raises(def()
  file_read("/no/such/file.txt")
end, "missing file raises")
```

### `assert_raises_typed(fn, type, msg)` — Specific error type

Passes if calling `fn` raises exactly the specified error type.

```ruby
assert_raises_typed(def()
  x = 1 // 0
end, "ZeroDivisionError", "division raises ZeroDivisionError")

assert_raises_typed(def()
  file_read("/no/such/file.txt")
end, "FileNotFoundError", "missing file raises FileNotFoundError")

assert_raises_typed(def()
  "hello" + 42
end, "TypeError", "string + int raises TypeError")
```

Supported type strings: `"ZeroDivisionError"`, `"FileNotFoundError"`, `"TypeError"`, `"ValueError"`, `"IndexError"`, `"KeyError"`, `"NameError"`, `"AttributeError"`, `"RuntimeError"`, `"Exception"`.

---

## Structuring Tests

There is no required structure — assertions anywhere in the file are collected and reported together. For readability, group related assertions with comments:

```ruby
# test.fk

# ── Math ──────────────────────────────────────────────────────
assert_eq(abs(-5),          5,    "abs negative")
assert_eq(abs(5),           5,    "abs positive")
assert_eq(round(3.14159,2), 3.14, "round to 2dp")
assert_eq(clamp(15, 0, 10), 10,   "clamp above max")
assert_eq(clamp(-5, 0, 10), 0,    "clamp below min")

# ── String ────────────────────────────────────────────────────
assert_eq("hello".upcase,          "HELLO",  "upcase")
assert_eq("  hi  ".strip,          "hi",     "strip")
assert_eq("a,b,c".split(",").length, 3,      "split count")
assert_match("frank123", "\\d+",             "contains digits")

# ── Vector ────────────────────────────────────────────────────
v = [3, 1, 4, 1, 5, 9, 2, 6]
assert_eq(v.length, 8,         "length")
assert_eq(min(v),   1,         "min")
assert_eq(max(v),   9,         "max")
assert_eq(v.sort[0], 1,        "sort first")
assert_eq(v.uniq.length, 7,    "uniq removes one duplicate")

# ── Error handling ────────────────────────────────────────────
assert_raises_typed(def()
  1 // 0
end, "ZeroDivisionError", "division by zero")

assert_raises_typed(def()
  file_read("/no/such/file.txt")
end, "FileNotFoundError", "missing file")
```

---

## Testing Your Own Functions

Require your lib files the same way `main.fk` does:

```ruby
# test.fk
require "lib/math_utils"
require "lib/string_utils"

# ── math_utils ────────────────────────────────────────────────
assert_eq(circle_area(1),    round(3.14159, 2), "unit circle")
assert_eq(circle_area(0),    0.0,               "zero radius")
assert_eq(factorial(5),      120,               "factorial 5")
assert_eq(factorial(0),      1,                 "factorial 0")

# ── string_utils ──────────────────────────────────────────────
assert_eq(slugify("Hello World"),  "hello-world",   "slugify basic")
assert_eq(slugify("  spaces  "),   "spaces",        "slugify trims")
assert_eq(truncate("hello", 3),    "hel...",        "truncate")
assert_nil(truncate("hi", 10),     "no truncate needed returns nil")
```

---

## Testing File I/O

Use a temporary path and clean up in every test:

```ruby
path = "/tmp/fk_test_#{rand_int(1000, 9999)}.txt"

# Write and read back
file_write(path, "hello frankie\n")
assert_true(file_exists(path),            "file was created")
assert_eq(file_read(path).strip, "hello frankie", "content correct")

# Append
file_append(path, "second line\n")
assert_eq(file_lines(path).length, 2,    "two lines after append")

# Delete
file_delete(path)
assert_true(not file_exists(path),       "file deleted")

# FileNotFoundError
assert_raises_typed(def()
  file_read("/no/such/file.txt")
end, "FileNotFoundError", "missing file raises correctly")
```

---

## Watch Mode

Run tests automatically whenever you save:

```bash
frankiec watch test.fk --test
```

Every time you save `test.fk` (or any file, since watch triggers on the target file), the test suite re-runs. Combine with `require` to automatically pick up changes in your lib files too.

---

## Quick Reference

| Assertion | Passes when |
|---|---|
| `assert_eq(actual, expected, msg)` | `actual == expected` |
| `assert_neq(actual, expected, msg)` | `actual != expected` |
| `assert_true(value, msg)` | `value` is truthy |
| `assert_nil(value, msg)` | `value` is nil |
| `assert_match(value, pattern, msg)` | pattern matches anywhere in value |
| `assert_raises(fn, msg)` | calling `fn` raises any error |
| `assert_raises_typed(fn, type, msg)` | calling `fn` raises that specific type |
