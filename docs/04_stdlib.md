# Standard Library Reference

## Math & Statistics

| Function | Description |
|---|---|
| `sqrt(x)` | Square root |
| `abs(x)` | Absolute value |
| `floor(x)` | Round down to integer |
| `ceil(x)` | Round up to integer |
| `round(x, n)` | Round to n decimal places (n defaults to 0) |
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

## Randomness

| Function | Description |
|---|---|
| `random()` | Random Float in [0.0, 1.0) |
| `rand(n)` | Random Integer in [0, n) |
| `rand_int(a, b)` | Random Integer in [a, b] (both inclusive) |
| `rand_float(a, b)` | Random Float in [a, b) |
| `shuffle(vec)` | Return a shuffled copy of a vector |
| `sample(vec, n)` | Return n randomly chosen elements (no repeats) |
| `rand_seed(n)` | Seed the RNG for reproducible results |

```ruby
rand_seed(42)
puts rand_int(1, 100)          # reproducible integer
puts rand_float(0.0, 1.0)      # reproducible float
puts shuffle([1, 2, 3, 4, 5])  # shuffled copy
puts sample([10, 20, 30], 2)   # 2 random elements
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
| `.chars` | Vector of individual characters (chainable into iterators) |
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
| `.gsub(pat, rep)` | Replace all matches with a fixed string |
| `.gsub(pat) do \|m\|` | Replace all matches — block transforms each match |
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
puts s.center(20, "-")    # --Hello, Frankie!---
puts s.ljust(20, ".")     # Hello, Frankie!.....
puts s[0..4]              # Hello
puts s[-7..-1]            # Frankie!

puts "aaabbbccc".squeeze  # abc
puts "Hello".tr("aeiou", "*")  # H*ll*

# .chars chains naturally into iterators
puts "hello".chars.select do |c| c != "l" end   # ["h", "e", "o"]
puts "mississippi".chars.uniq.length              # 4

# .gsub with block — transform each match
puts "hello".gsub("[aeiou]") do |m| m.upcase end  # hEllO
```

---

## String Formatting

```ruby
sprintf(fmt, *args)        # C-style format string
paste(*args, sep: " ")     # join values with separator
template(str, hash)        # {{key}} placeholder substitution
```

```ruby
puts sprintf("%-10s %5d %8.2f", "Frankie", 1, 3.14)
# Frankie        1     3.14

puts paste("2025", "03", "14", sep: "-")
# 2025-03-14

puts template("Hello, {{name}}! You are {{age}}.", {name: "Alice", age: 30})
# Hello, Alice! You are 30.

# template() with a loop
people = [{name: "Alice", role: "Engineer"}, {name: "Bob", role: "Designer"}]
people.each do |p|
  puts template("  {{name}} — {{role}}", p)
end
```

`template()` raises a `KeyError` if a `{{placeholder}}` key is missing from the hash.

---

## Regex

All regex functions use `(string, pattern)` argument order.

| Function | Description |
|---|---|
| `matches(str, pat)` | True if pattern matches anywhere |
| `match(str, pat)` | First match string or nil |
| `match_all(str, pat)` | Vector of all match strings |
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
| `file_rename(src, dst)` | Rename or move a file |
| `file_copy(src, dst)` | Copy a file; returns dst path |

```ruby
file_write("/tmp/data.txt", "Hello\nWorld\n")
puts file_read("/tmp/data.txt")

lines = file_lines("/tmp/data.txt")
puts length(lines)     # 2

file_append("/tmp/data.txt", "Frankie\n")
file_copy("/tmp/data.txt", "/tmp/backup.txt")
file_rename("/tmp/backup.txt", "/tmp/backup_v2.txt")
file_delete("/tmp/data.txt")
puts file_exists("/tmp/data.txt")   # false
```

---

## File System

| Function | Description |
|---|---|
| `file_mkdir(path)` | Create directory (and all parents, like `mkdir -p`) |
| `file_mkdir(path, false)` | Create a single directory only (no parents) |
| `dir_exists(path)` | True if path is an existing directory |
| `dir_list(path)` | Sorted vector of filenames in directory (default: `"."`) |

```ruby
file_mkdir("/tmp/myapp/data")
puts dir_exists("/tmp/myapp/data")     # true
puts dir_exists("/tmp/no_such_dir")    # false

file_write("/tmp/myapp/data/a.txt", "hello")
file_copy("/tmp/myapp/data/a.txt", "/tmp/myapp/data/b.txt")
puts dir_list("/tmp/myapp/data")       # [a.txt, b.txt]

# List current directory
puts dir_list()
```

---

## JSON

| Function | Description |
|---|---|
| `json_parse(str)` | JSON string → Frankie value |
| `json_dump(obj)` | Frankie value → JSON string |
| `json_dump(obj, true)` | Pretty-printed JSON |
| `json_read(path)` | Read and parse JSON file |
| `json_write(path, obj)` | Write JSON file |
| `json_write(path, obj, true)` | Write pretty JSON file |

```ruby
data = {name: "Alice", scores: [95, 87, 92]}
puts json_dump(data)
puts json_dump(data, true)   # pretty-printed

obj = json_parse('{"name":"Bob","age":30}')
puts obj["name"]    # Bob

json_write("/tmp/data.json", data, true)
loaded = json_read("/tmp/data.json")
puts loaded["name"]
```

---

## CSV

| Function | Description |
|---|---|
| `csv_parse(text)` | CSV string → vector of hashes (first row = headers) |
| `csv_parse(text, false)` | CSV string → vector of vectors (no header row) |
| `csv_dump(rows)` | Vector of hashes → CSV string |
| `csv_dump(rows, headers)` | With explicit header list |
| `csv_read(path)` | Read and parse CSV file |
| `csv_write(path, rows)` | Write CSV file |

```ruby
rows = [
  {name: "Alice", dept: "Engineering", score: 95},
  {name: "Bob",   dept: "Marketing",   score: 72}
]

text = csv_dump(rows)
puts text

reparsed = csv_parse(text)
reparsed.each do |row|
  puts "#{row["name"]}: #{row["score"]}"
end

csv_write("/tmp/data.csv", rows)
loaded = csv_read("/tmp/data.csv")
puts loaded.length    # 2
```

---

## DateTime

| Function / Method | Description |
|---|---|
| `now()` | Current date and time |
| `today()` | Today at midnight |
| `date_from(y, m, d, h, min, s)` | Construct from components |
| `date_parse(str)` | Parse `YYYY-MM-DD` string |
| `date_parse(str, fmt)` | Parse with custom format |
| `.year` `.month` `.day` | Date components |
| `.hour` `.minute` `.second` | Time components |
| `.format(fmt)` | Format with `strftime` directives |
| `.add_days(n)` | Add n days → new date |
| `.add_hours(n)` | Add n hours → new date |
| `.add_minutes(n)` | Add n minutes → new date |
| `.diff_days(other)` | Absolute difference in days |
| `.diff_seconds(other)` | Absolute difference in seconds |
| `.weekday` | 0 = Monday … 6 = Sunday |
| `.weekday_name` | Full day name (Monday, Tuesday…) |
| `.is_before(other)` | Comparison |
| `.is_after(other)` | Comparison |
| `.timestamp` | Unix timestamp (float) |

```ruby
t = now()
puts t.format("%A, %d %B %Y")   # Thursday, 19 March 2026
puts t.year                      # 2026
puts t.weekday_name              # Thursday

d = date_from(2026, 12, 25)
puts d.format("%d/%m/%Y")        # 25/12/2026

next_week = today().add_days(7)
puts today().diff_days(next_week)   # 7

d2 = date_parse("2026-06-15")
puts d2.is_before(d)             # true
```

---

## HTTP Client

| Function | Description |
|---|---|
| `http_get(url)` | GET request |
| `http_get(url, headers)` | GET with custom headers |
| `http_post(url, data)` | POST (hash → JSON, string → plain text) |
| `http_put(url, data)` | PUT request |
| `http_delete(url)` | DELETE request |
| `url_encode(hash)` | Encode hash as query string |
| `url_decode(str)` | Decode query string → hash |

| Response Property | Description |
|---|---|
| `.status` | HTTP status code (integer) |
| `.body` | Response body as string |
| `.headers` | Response headers as hash |
| `.ok` | True if status is 2xx |
| `.json()` | Parse body as JSON |

```ruby
resp = http_get("https://api.example.com/users")
puts resp.status      # 200
puts resp.ok          # true
data = resp.json()
puts data["count"]

payload = {name: "Alice", email: "alice@example.com"}
resp2 = http_post("https://api.example.com/users", payload)
puts resp2.status

# With custom headers
resp3 = http_get("https://api.example.com/secret",
                 {Authorization: "Bearer mytoken"})

params = {q: "frankie lang", page: 1}
puts url_encode(params)    # q=frankie+lang&page=1
```

---

## System

| Function | Description |
|---|---|
| `exit(code)` | Exit with given code (default 0) |
| `argv()` | Command-line arguments as vector |
| `env(key, default)` | Get environment variable |
| `sleep(n)` | Pause execution for n seconds (float ok) |

```ruby
puts argv()               # ["arg1", "arg2"]
puts env("HOME", "/tmp")  # /home/user
sleep(0.5)                # pause 500ms
exit(0)
```

---

## Type Checking & Conversion

```ruby
# Conversion
to_int("42")        # 42
to_float("3.14")    # 3.14
to_str(100)         # "100"

# Checking
is_integer(42)      # true
is_float(3.14)      # true
is_string("hi")     # true
is_vector([1,2,3])  # true
is_nil(nil)         # true
is_bool(true)       # true
```

---

## Testing

Run with `frankiec test [file.fk]`. All functions are available without imports.

| Function | Description |
|---|---|
| `assert_true(cond, msg)` | Pass if cond is truthy |
| `assert_eq(actual, expected, msg)` | Pass if actual == expected |
| `assert_neq(actual, expected, msg)` | Pass if actual != expected |
| `assert_match(value, pattern, msg)` | Pass if pattern matches anywhere in value *(v1.12)* |
| `assert_nil(value, msg)` | Pass if value is nil *(v1.12)* |
| `assert_raises(fn, msg)` | Pass if calling fn raises any error |
| `assert_raises_typed(fn, type, msg)` | Pass if fn raises exactly the given error type |

```ruby
# test.fk
assert_eq(mean([1,2,3]), 2.0, "mean works")

result = [1, 3, 5, 7].find do |n|
  n > 4
end
assert_eq(result, 5, ".find returns first match")

# v1.12 — assert_match and assert_nil
assert_match("hello@example.com", "\\w+@\\w+\\.\\w+", "valid email")
assert_nil(find_user(999), "missing user returns nil")

assert_raises_typed(def()
  x = 1 // 0
end, "ZeroDivisionError", "division raises ZeroDivisionError")

assert_raises(def()
  raise "boom"
end, "raise works")
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
  ✓  mean works
  ✓  .find returns first match
  ✓  division raises ZeroDivisionError
  ✓  raise works
╠═══════════════════════════════════════════════════════
║  ✓  All 4 test(s) passed  (1.4ms)
╚═══════════════════════════════════════════════════════
```
