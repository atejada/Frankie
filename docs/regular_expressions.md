# Regular Expressions

## What is a Regular Expression?

A regular expression (regex) is a pattern that describes a set of strings. In Frankie, regexes are used to search, test, extract, and transform text. You write patterns as plain strings — `"\\d+"`, `"\\w+@\\w+\\.\\w+"` — and pass them to the regex functions or string methods.

```ruby
# Does this string contain a number?
puts matches("Order 42", "\\d+")          # true

# Extract all numbers
puts match_all("x=10, y=20", "\\d+")      # [10, 20]

# Replace all vowels
puts gsub("hello", "[aeiou]", "*")        # h*ll*
```

Frankie's regex engine is Python's `re` module under the hood, so all standard regex syntax is available.

---

## Pattern Syntax

Patterns are written as strings. Because strings use `\` as an escape character, regex backslash sequences need to be doubled: write `"\\d"` to mean the regex `\d`.

### Character Classes

| Pattern | Matches |
|---|---|
| `.` | Any character except newline |
| `\\d` | Any digit — `[0-9]` |
| `\\D` | Any non-digit |
| `\\w` | Any word character — `[a-zA-Z0-9_]` |
| `\\W` | Any non-word character |
| `\\s` | Any whitespace — space, tab, newline |
| `\\S` | Any non-whitespace |
| `[aeiou]` | Any one of: a, e, i, o, u |
| `[^aeiou]` | Any character except: a, e, i, o, u |
| `[a-z]` | Any lowercase letter |
| `[A-Z]` | Any uppercase letter |
| `[0-9]` | Any digit (same as `\\d`) |
| `[a-zA-Z0-9]` | Any letter or digit |

### Quantifiers

| Pattern | Matches |
|---|---|
| `x*` | Zero or more of x |
| `x+` | One or more of x |
| `x?` | Zero or one of x (optional) |
| `x{n}` | Exactly n of x |
| `x{n,}` | n or more of x |
| `x{n,m}` | Between n and m of x |

By default quantifiers are **greedy** — they match as much as possible. Add `?` to make them **lazy** — match as little as possible:

```ruby
puts match_all("<b>hello</b><b>world</b>", "<.+>")    # [<b>hello</b><b>world</b>]
puts match_all("<b>hello</b><b>world</b>", "<.+?>")   # [<b>, </b>, <b>, </b>]
```

### Anchors

| Pattern | Matches |
|---|---|
| `^` | Start of string (or line in multiline mode) |
| `$` | End of string (or line in multiline mode) |
| `\\b` | Word boundary |
| `\\B` | Non-word boundary |

```ruby
puts matches("hello world", "^hello")    # true
puts matches("say hello", "^hello")      # false
puts matches("hello world", "world$")    # true
puts matches("worldwide", "\\bworld\\b") # false  (no boundary after "world")
```

### Groups and Alternation

| Pattern | Meaning |
|---|---|
| `(abc)` | Capturing group |
| `(?:abc)` | Non-capturing group |
| `a\|b` | Alternation — match a or b |
| `(?=abc)` | Lookahead — followed by abc |
| `(?!abc)` | Negative lookahead — not followed by abc |
| `(?<=abc)` | Lookbehind — preceded by abc |
| `(?<!abc)` | Negative lookbehind — not preceded by abc |

```ruby
# Alternation
puts matches("cat", "cat|dog")     # true
puts matches("dog", "cat|dog")     # true
puts matches("fish", "cat|dog")    # false

# Lookahead — match a word followed by a colon
puts match_all("name: Alice age: 30", "\\w+(?=:)")   # [name, age]

# Lookbehind — match what comes after a prefix
puts match_all("price: 99 total: 150", "(?<=: )\\d+")   # [99, 150]
```

---

## The Five Regex Functions

All five accept a string pattern or a compiled regex object (from `regex()`).

### `matches(string, pattern)` — Boolean test

Returns `true` if the pattern matches anywhere in the string.

```ruby
puts matches("hello world", "\\d+")        # false
puts matches("hello123", "\\d+")           # true
puts matches("alice@example.com", "\\w+@\\w+\\.\\w+")  # true
```

Also available as a string method:

```ruby
puts "hello123".matches?("\\d+")           # true
```

### `match(string, pattern)` — First match object

Returns the first match as a match object, or `nil` if nothing matches. Most useful as a boolean guard — the match object itself prints as a raw Python repr.

```ruby
m = match("Order 42 placed", "\\d+")
if m != nil
  puts "Found a number"
end

# For the matched text, use match_all instead
```

Also available as a string method:

```ruby
if "Order 42".match("\\d+") != nil
  puts "has a number"
end
```

### `match_all(string, pattern)` — All matches as a vector

Returns every non-overlapping match as a clean vector of strings. This is the function to reach for when you want the actual matched text.

```ruby
puts match_all("2024-01-15", "\\d+")           # [2024, 01, 15]
puts match_all("one 1 two 2 three 3", "\\d+")  # [1, 2, 3]
puts match_all("no digits here", "\\d+")        # []

# Chain into vector methods
total = match_all("prices: 10, 20, 30", "\\d+").map do |n|
  n.to_i
end |> sum
puts total   # 60
```

Also available as a string method:

```ruby
puts "hello world frankie".match_all("\\w+")   # [hello, world, frankie]
```

### `sub(string, pattern, replacement)` — Replace first match

Replaces only the first occurrence.

```ruby
puts sub("hello world world", "world", "Frankie")   # hello Frankie world
puts sub("aabbcc", "b+", "X")                        # aaXcc
```

Also available as a string method:

```ruby
puts "hello world world".sub("world", "Frankie")     # hello Frankie world
```

### `gsub(string, pattern, replacement)` — Replace all matches

Replaces every occurrence.

```ruby
puts gsub("hello world world", "world", "Frankie")   # hello Frankie Frankie
puts gsub("aabbcc", "b", "X")                         # aaXXcc

# Redact all digits
puts gsub("Card: 4111-1111-1111-1111", "\\d", "*")   # Card: ****-****-****-****
```

Also available as a string method with block form — the block receives each matched substring and returns its replacement:

```ruby
# Transform each match
puts "hello world".gsub("\\w+") do |m|
  m.upcase
end
# HELLO WORLD

# Double every number in a string
puts "I have 3 cats and 2 dogs".gsub("\\d+") do |m|
  (m.to_i * 2).to_s
end
# I have 6 cats and 4 dogs
```

---

## The `=~` Match Operator

Returns the **position** of the first match, or `nil` if there is no match.

```ruby
puts "frank123" =~ "\\d+"    # 5  (position where digits start)
puts "no digits" =~ "\\d+"   # nil

# Useful for position-based logic
pos = "hello world" =~ "world"
if pos != nil
  puts "found at position #{pos}"   # found at position 6
end
```

---

## Compiled Patterns with `regex()`

For case-insensitive matching, multiline mode, or dotall mode, compile a pattern first using `regex(pattern, flags)`.

| Flag | Meaning |
|---|---|
| `"i"` | Case-insensitive — `a` matches `A` |
| `"m"` | Multiline — `^` and `$` match start/end of each line |
| `"s"` | Dotall — `.` also matches newline |
| `"im"` | Combine flags freely |

```ruby
# Case-insensitive
r = regex("frankie", "i")
puts matches("I love FRANKIE!", r)    # true
puts matches("I love frankie!", r)    # true
puts matches("I love python!", r)     # false

# Pass compiled regex to any function
puts match_all("Hello WORLD hello World", regex("hello", "i"))
# [Hello, hello]

puts gsub("Hello World", regex("[aeiou]", "i"), "*")
# H*ll* W*rld

# Multiline — ^ and $ match each line
text = "line one\nline two\nline three"
puts match_all(text, regex("^line \\w+", "m"))
# [line one, line two, line three]
```

---

## Common Patterns

A reference of patterns you'll reach for regularly:

```ruby
# Integer
puts matches("42", "^-?\\d+$")                          # true
puts matches("3.14", "^-?\\d+$")                         # false

# Decimal number
puts matches("3.14", "^-?\\d+(\\.\\d+)?$")               # true

# Email (simple)
puts matches("alice@example.com", "\\w+@\\w+\\.\\w+")    # true

# URL
puts matches("https://frankie-lang.org", "^https?://")   # true

# ISO date
puts matches("2024-01-15", "^\\d{4}-\\d{2}-\\d{2}$")     # true

# Whitespace-only
puts matches("   ", "^\\s+$")                             # true
puts matches("  x  ", "^\\s+$")                           # false

# Starts with capital letter
puts matches("Alice", "^[A-Z]")                           # true
puts matches("alice", "^[A-Z]")                           # false

# Hex colour
puts matches("#ff5733", "^#[0-9a-fA-F]{6}$")             # true
```

---

## Practical Examples

```ruby
# Extract all email addresses from a block of text
text = "Contact alice@example.com or bob@corp.io for help."
emails = match_all(text, "[\\w.]+@[\\w.]+\\.[a-z]+")
puts emails   # [alice@example.com, bob@corp.io]

# Validate and parse a date string
date = "2024-01-15"
if matches(date, "^\\d{4}-\\d{2}-\\d{2}$")
  parts = match_all(date, "\\d+")
  puts "Year: #{parts[0]}, Month: #{parts[1]}, Day: #{parts[2]}"
end

# Clean up messy whitespace
messy = "too   many    spaces   here"
puts gsub(messy, "\\s+", " ")   # too many spaces here

# Extract key=value pairs from a config string
config = "host=localhost port=5432 db=myapp"
match_all(config, "\\w+=\\w+").each do |pair|
  parts = pair.split("=")
  puts "#{parts[0]} → #{parts[1]}"
end
# host → localhost
# port → 5432
# db → myapp

# Redact sensitive data
log = "User alice@corp.com logged in from IP 192.168.1.42"
clean = gsub(log, "[\\w.]+@[\\w.]+\\.\\w+", "[EMAIL]")
clean = gsub(clean, "\\d{1,3}(\\.\\d{1,3}){3}", "[IP]")
puts clean   # User [EMAIL] logged in from IP [IP]
```

---

## Quick Reference

| Function / Method | Description |
|---|---|
| `matches(str, pat)` | True if pattern matches anywhere |
| `str.matches?(pat)` | Same — method form |
| `match(str, pat)` | First match object or nil |
| `str.match(pat)` | Same — method form |
| `match_all(str, pat)` | All matches as a vector of strings |
| `str.match_all(pat)` | Same — method form |
| `sub(str, pat, rep)` | Replace first match with rep |
| `str.sub(pat, rep)` | Same — method form |
| `gsub(str, pat, rep)` | Replace all matches with rep |
| `str.gsub(pat, rep)` | Same — method form |
| `str.gsub(pat) do \|m\|` | Replace all matches — block computes each replacement |
| `str =~ pat` | Position of first match or nil |
| `regex(pat, flags)` | Compile a pattern with flags (`"i"`, `"m"`, `"s"`) |
