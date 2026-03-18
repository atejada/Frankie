# Standard Library Reference

## Math & Statistics

| Function | Description |
|---|---|
| `sqrt(x)` | Square root |
| `abs(x)` | Absolute value |
| `floor(x)` | Round down to integer |
| `ceil(x)` | Round up to integer |
| `min(a, b)` or `min(vec)` | Minimum |
| `max(a, b)` or `max(vec)` | Maximum |
| `sum(vec)` | Sum of all elements |
| `mean(vec)` | Arithmetic mean |
| `median(vec)` | Median value |
| `stdev(vec)` | Sample standard deviation |
| `variance(vec)` | Sample variance |
| `clamp(x, lo, hi)` | Clamp x between lo and hi |
| `seq(start, stop, step)` | Numeric sequence like R's `seq()` |
| `linspace(start, stop, n)` | n evenly-spaced values |
| `rep(x, n)` | Repeat x n times like R's `rep()` |

```ruby
puts sqrt(16.0)          # 4.0
puts abs(-7)             # 7
puts clamp(150, 0, 100)  # 100
puts seq(0, 1, 0.25)     # [0, 0.25, 0.5, 0.75, 1.0]
puts linspace(0, 10, 5)  # [0.0, 2.5, 5.0, 7.5, 10.0]
puts rep(3, 4)           # [3, 3, 3, 3]

data = [4, 8, 15, 16, 23, 42]
puts mean(data)          # 18.0
puts median(data)        # 15.5
puts stdev(data)         # 13.49...
```

---

## String Methods

| Method / Function | Description |
|---|---|
| `.upcase` | Convert to uppercase |
| `.downcase` | Convert to lowercase |
| `.length` | Character count |
| `.reverse` | Reverse the string |
| `.strip` | Remove leading/trailing whitespace |
| `.lstrip` | Remove leading whitespace |
| `.rstrip` | Remove trailing whitespace |
| `.chomp` | Remove trailing newline |
| `.chop` | Remove last character |
| `.chars` | Vector of individual characters |
| `.bytes` | Vector of byte values |
| `.lines` | Vector of lines |
| `.ord` | ASCII code of first character |
| `.include?(s)` | True if s is a substring |
| `.start_with?(s)` | True if starts with s |
| `.end_with?(s)` | True if ends with s |
| `.count(sub)` | Count occurrences of sub |
| `.split(sep)` | Split by separator → Vector |
| `.join(sep)` | Join vector elements as string |
| `.center(w, pad)` | Center in field of width w |
| `.ljust(w, pad)` | Left-justify in field of width w |
| `.rjust(w, pad)` | Right-justify in field of width w |
| `.squeeze` | Remove consecutive duplicate chars |
| `.tr(from, to)` | Translate characters |
| `.each_char do \|c\|` | Iterate over characters |
| `.each_line do \|l\|` | Iterate over lines |
| `[i]` | Character at index (negatives ok) |
| `[a..b]` | Inclusive slice |
| `[a...b]` | Exclusive slice |

```ruby
s = "Hello, Frankie!"

puts s.upcase             # HELLO, FRANKIE!
puts s.length             # 15
puts s.reverse            # !eiknarF ,olleH
puts s.include?("rank")   # true
puts s.count("l")         # 2
puts s.center(20, "-")    # --Hello, Frankie!--
puts s.ljust(20, ".")     # Hello, Frankie!.....
puts s[0..4]              # Hello
puts s[-7..-1]            # Frankie!

puts "aaabbbccc".squeeze  # abc
puts "Hello".tr("aeiou", "*")  # H*ll*

"ABC".each_char do |c|
  print c + " "
end
# A B C
```

---

## String Formatting

```ruby
sprintf(format, *args)        # C-style format string
paste(*args, sep: " ")        # join values with separator
```

```ruby
puts sprintf("%-10s %5d %8.2f", "Frankie", 1, 3.14)
# Frankie        1     3.14

puts paste("2025", "03", "14", sep: "-")
# 2025-03-14

puts paste("Hello", "World")
# Hello World
```

---

## Regex

All regex functions use `(string, pattern)` argument order — read as "does X match Y?".

| Function | Description |
|---|---|
| `matches(str, pat)` | True if pattern matches anywhere |
| `match(str, pat)` | First match object or nil |
| `match_all(str, pat)` | Vector of all matches |
| `sub(str, pat, repl)` | Replace first match |
| `gsub(str, pat, repl)` | Replace all matches |
| `str =~ pat` | Match position (index) or nil |
| `regex(pat, flags)` | Compile pattern with flags |

Flags: `"i"` = case-insensitive, `"m"` = multiline, `"s"` = dot matches newline.

```ruby
puts matches("hello world", "world")            # true
puts match_all("1 and 2 and 3", "[0-9]+")       # [1, 2, 3]
puts gsub("Hello World", "World", "Frankie")    # Hello Frankie
puts "hello frankie" =~ "frankie"               # 6

r = regex("[a-z]+", "i")
puts matches("HELLO", r)                        # true
```

---

## File I/O

| Function | Description |
|---|---|
| `file_write(path, text)` | Write string (overwrites) |
| `file_append(path, text)` | Append string |
| `file_read(path)` | Read entire file as string |
| `file_lines(path)` | Read file as vector of lines |
| `file_exists(path)` | True if file exists |
| `file_delete(path)` | Delete file |

```ruby
file_write("/tmp/data.txt", "Hello\nWorld\n")
puts file_read("/tmp/data.txt")

lines = file_lines("/tmp/data.txt")
puts length(lines)          # 2

lines.each do |line|
  puts "> #{line}"
end

file_append("/tmp/data.txt", "Frankie\n")
file_delete("/tmp/data.txt")
puts file_exists("/tmp/data.txt")   # false

# Error handling for missing files
begin
  file_read("/tmp/missing.txt")
rescue e
  puts "Error: #{e}"
end
```

---

## Type Checking

```ruby
is_integer(42)      # true
is_float(3.14)      # true
is_string("hi")     # true
is_vector([1,2,3])  # true
is_nil(nil)         # true
is_bool(true)       # true
```

---

## System

```ruby
exit(0)                     # exit with code
argv()                      # command-line args as vector
env("HOME", "/tmp")         # environment variable with default
```

---

## Type Conversion

```ruby
to_int("42")        # 42
to_float("3.14")    # 3.14
to_str(100)         # "100"
```

---

## Testing

Run with `frankiec test [file.fk]`. All functions are available without imports.

```ruby
assert_true(cond, msg)            # pass if cond is truthy
assert_eq(actual, expected, msg)  # pass if actual == expected
assert_neq(actual, expected, msg) # pass if actual != expected
assert_raises(fn, msg)            # pass if calling fn raises any error
```

```ruby
# test.fk
x = 10
x += 5
assert_eq(x, 15, "+= works")

result = [1, 3, 5, 7].find do |n|
  n > 4
end
assert_eq(result, 5, ".find returns first match")

begin
  y = 1 // 0
rescue ZeroDivisionError e
  assert_true(true, "typed rescue works")
end
```

Run it:

```bash
frankiec test          # runs test.fk
frankiec test my.fk    # runs a named file
```

Output:
```
╔══ Frankie Test Runner ════════════════════════════════
║  test.fk
╠═══════════════════════════════════════════════════════
  ✓  += works
  ✓  .find returns first match
  ✓  typed rescue works
╠═══════════════════════════════════════════════════════
║  ✓  All 3 test(s) passed  (1.2ms)
╚═══════════════════════════════════════════════════════
```
