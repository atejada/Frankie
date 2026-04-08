# Strings

## What is a String?

A string is a sequence of UTF-8 characters. Strings are used for text — output, input, file content, keys, messages, templates. In Frankie, strings are **immutable** — every method that transforms a string returns a new string rather than modifying the original.

```ruby
s = "Hello, Frankie!"
puts s.upcase    # "HELLO, FRANKIE!"
puts s           # "Hello, Frankie!" — unchanged
```

---

## String Literals

The standard form is a double-quoted string:

```ruby
name = "Alice"
```

Single-quoted strings are also valid but do **not** support interpolation or escape sequences:

```ruby
puts 'Hello, #{name}'   # Hello, #{name}  — literal, not interpolated
```

**Triple-quoted strings** span multiple lines:

```ruby
message = """
  Hello, Alice!
  Welcome to Frankie.
"""
puts message
```

**Heredocs** (`<<~DELIM`) are the cleanest way to write multi-line strings in code. The `~` variant strips common leading indentation automatically:

```ruby
query = <<~SQL
  SELECT name, age
  FROM employees
  WHERE age > 30
  ORDER BY name
SQL
puts query
```

Heredocs support `#{}` interpolation just like regular strings:

```ruby
table = "employees"
limit = 10

query = <<~SQL
  SELECT * FROM #{table}
  LIMIT #{limit}
SQL
```

---

## String Interpolation

Double-quoted strings support `#{}` to embed any expression directly:

```ruby
name  = "Alice"
score = 95

puts "Hello, #{name}!"                  # Hello, Alice!
puts "Score: #{score}"                  # Score: 95
puts "Double: #{score * 2}"             # Double: 190
puts "Upper: #{name.upcase}"            # Upper: ALICE
puts "Pi ≈ #{round(3.14159, 2)}"        # Pi ≈ 3.14
```

Any valid Frankie expression works inside `#{}`. The result is automatically converted to a string.

---

## Escape Sequences

Inside double-quoted strings:

| Sequence | Meaning |
|---|---|
| `\n` | Newline |
| `\t` | Tab |
| `\\` | Literal backslash |
| `\"` | Literal double quote |

```ruby
puts "line one\nline two"
puts "column\tone\ttwo"
puts "She said \"hello\""
```

---

## String Operators

```ruby
# Concatenation
puts "Hello, " + "Frankie!"    # Hello, Frankie!

# Repetition
puts "ha" * 3                   # hahaha
puts "-" * 40                   # ────────────────────────────────────────

# Comparison
puts "apple" == "apple"         # true
puts "apple" != "banana"        # true
puts "apple" < "banana"         # true  (lexicographic)

# Match operator — returns position of first match or nil
puts "frank123" =~ "\\d+"       # 5
puts "no digits" =~ "\\d+"      # nil
```

---

## Accessing Characters and Slices

Strings are 0-indexed. Negative indices count from the end.

```ruby
s = "Frankie"

puts s[0]       # F
puts s[1]       # r
puts s[-1]      # e   (last character)
puts s[-3]      # i

# Inclusive range slice
puts s[0..4]    # Frank

# Exclusive range slice (up to but not including index 5)
puts s[0...4]   # Fran

# Last N characters
puts s[-3..-1]  # kie
```

---

## Case and Whitespace

```ruby
puts "hello".upcase     # HELLO
puts "HELLO".downcase   # hello

puts "  hello  ".strip    # hello
puts "  hello  ".lstrip   # hello   (left only)
puts "  hello  ".rstrip   # hello   (right only)

puts "hello\n".chomp    # hello  (removes trailing newline)
puts "hello!".chop      # hello  (removes last character)
```

---

## Inspection

```ruby
s = "Hello, Frankie!"

puts s.length             # 15
puts s.empty?             # false
puts "".empty?            # true

puts s.include?("rank")   # true
puts s.start_with?("He")  # true
puts s.end_with?("!")     # true

puts s.count("l")         # 2  (occurrences of "l")
```

---

## Searching and Matching

Patterns can be plain strings or regex strings. Frankie uses string patterns — `"\\d+"` not `/\d+/`.

```ruby
s = "Order 42 placed on 2024-01-15"

# Does the pattern appear?
puts s.matches?("\\d+")              # true

# Position of first match (=~ operator)
puts s =~ "\\d+"                     # 6

# First match as a match object
m = s.match("\\d+")
puts m                               # <re.Match ...>
if m != nil
  puts "found a number"
end

# All matches as a clean vector of strings
puts s.match_all("\\d+")             # [42, 2024, 01, 15]

# Standalone function forms — identical behaviour
puts matches(s, "\\d+")             # true
puts match_all(s, "\\d+")           # [42, 2024, 01, 15]
```

---

## Transformation

```ruby
s = "Hello, World!"

# Reverse
puts s.reverse                       # !dlroW ,olleH

# Replace first occurrence
puts s.replace("World", "Frankie")   # Hello, Frankie!

# Replace using regex — first match only
puts s.sub("\\w+", "Goodbye")        # Goodbye, World!

# Replace all matches — fixed string
puts "aabbcc".gsub("b", "x")         # aaxxcc

# Replace all matches — block transforms each match
puts "hello world".gsub("\\w+") do |m|
  m.upcase
end
# HELLO WORLD

# Delete all occurrences of any character in the set
puts "hello world".delete("lo")      # he wrd

# Collapse consecutive duplicate characters
puts "aaabbbccc".squeeze             # abc

# Translate characters (from → to, position by position)
puts "hello".tr("aeiou", "*")        # h*ll*
puts "hello".tr("a-m", "A-M")        # HEllo
```

---

## Padding and Alignment

```ruby
puts "hi".center(10)         # "    hi    "
puts "hi".center(10, "-")    # "----hi----"
puts "hi".ljust(10, ".")     # "hi........"
puts "hi".rjust(10, ".")     # "........hi"
```

Useful for building fixed-width reports and tables:

```ruby
items = [["Apple", 1.20], ["Banana", 0.50], ["Cherry", 3.00]]
items.each do |name, price|
  puts "#{name.ljust(10)} $#{price.to_s.rjust(5)}"
end
# Apple       $ 1.2
# Banana      $ 0.5
# Cherry      $  3.0
```

For richer string utilities — `truncate`, `slugify`, `word_wrap`, `indent_lines`, and padding with full control — load the `frankiestring` stitch:

```ruby
stitch "frankiestring"

puts pad_left("42", 6, "0")                    # "000042"
puts pad_right("hello", 10, ".")               # "hello....."
puts truncate("A very long description", 12, "...")  # "A very long..."
puts slugify("Hello World!")                   # "hello-world"
```

---

## Splitting and Joining

```ruby
# Split into a vector
puts "a,b,c,d".split(",")          # [a, b, c, d]
puts "hello world".split(" ")      # [hello, world]
puts "one  two  three".split(" ")  # [one, two, three]

# Split into lines
puts "line1\nline2\nline3".lines    # [line1, line2, line3]

# Split into characters
puts "hello".chars                  # [h, e, l, l, o]

# Split into byte values
puts "hi".bytes                     # [104, 105]

# Join a vector back into a string
puts ["a", "b", "c"].join(", ")     # a, b, c
puts ["one", "two", "three"].join(" | ")  # one | two | three
```

---

## Iterating Over a String

```ruby
# Character by character
"hello".each_char do |c|
  print c + "-"
end
# h-e-l-l-o-

# Line by line
"line1\nline2\nline3".each_line do |l|
  puts l.upcase
end
# LINE1
# LINE2
# LINE3

# .chars chains into all vector iterators
vowels = "hello world".chars.select do |c|
  "aeiou".include?(c)
end
puts vowels   # [e, o, o]

unique_count = "mississippi".chars.uniq.length
puts unique_count   # 4
```

---

## Conversion

```ruby
# To other types
puts "42".to_i        # 42
puts "3.14".to_f      # 3.14
puts 42.to_s          # "42"
puts 3.14.to_s        # "3.14"

# Character code
puts "A".ord          # 65

# Encode to bytes / decode from bytes
puts "hi".encode      # [104, 105]
puts [104, 105].encode  # hi  (or use .decode)
puts [104, 105].decode  # hi
```

---

## Formatting

```ruby
# Template — {{key}} placeholder replacement
puts template("Hello, {{name}}! You are {{age}}.", {name: "Alice", age: 30})
# Hello, Alice! You are 30.

# .format(hash) — {key} placeholder replacement (method form)
puts "Hello, {name}! You are {age}.".format({name: "Alice", age: 30})
# Hello, Alice! You are 30.

# sprintf — C-style format strings
puts sprintf("%-10s %5.2f", "Apple", 1.2)   # Apple       1.20

# paste — join values with a separator
puts paste("Alice", "Bob", "Carol", sep: ", ")   # Alice, Bob, Carol
```

---

## Nil Safety with Strings

Calling a method on `nil` raises a runtime error. Use `&.` to return nil safely instead:

```ruby
name = nil

puts name.upcase    # Runtime error
puts name&.upcase   # nil — safe

# Useful when a value might or might not be present
user_input = nil
puts user_input&.strip&.downcase   # nil — whole chain short-circuits
```

---

## Quick Reference

| Category | Methods / Functions |
|---|---|
| Case | `.upcase` `.downcase` |
| Whitespace | `.strip` `.lstrip` `.rstrip` `.chomp` `.chop` |
| Inspection | `.length` `.empty?` `.include?` `.start_with?` `.end_with?` `.count` |
| Search | `.match` `.match_all` `.matches?` `=~` |
| Transform | `.replace` `.sub` `.gsub` `.gsub do` `.delete` `.squeeze` `.tr` `.reverse` |
| Align | `.center` `.ljust` `.rjust` |
| Split | `.split` `.lines` `.chars` `.bytes` |
| Iterate | `.each_char` `.each_line` |
| Convert | `.to_i` `.to_f` `.to_s` `.ord` `.encode` `.decode` |
| Format | `template()` `.format()` `sprintf()` `paste()` |
| Slice | `[i]` `[a..b]` `[a...b]` |
| Operators | `+` `*` `==` `!=` `<` `>` `=~` |
