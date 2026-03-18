# Frankie Language Specification v1.2

Frankie is a procedural, expressive programming language named after Frankenstein —
stitched together from the best parts of Ruby, Python, R, and Fortran.

---

## Design Philosophy

- **Ruby-like syntax** — readable, expressive, human-friendly
- **Python's power** — rich data structures, clean semantics
- **R's statistical soul** — built-in vectors, ranges, pipe operator, statistical builtins
- **Fortran's precision** — explicit typing when you want it, numeric power

Frankie is **not object-oriented**. No classes, no `self`, no inheritance.

---

## File Extension

`.fk`

---

## 1. Comments

```frankie
# This is a single-line comment
```

---

## 2. Variables & Assignment

Variables are dynamically typed. Created on first assignment.

```frankie
x = 42
name = "Frankie"
pi = 3.14159
flag = true
nothing = nil
```

---

## 3. Types

| Type    | Example              | Notes                                 |
|---------|----------------------|---------------------------------------|
| Integer | `42`, `-7`           | Whole numbers                         |
| Float   | `3.14`, `-0.5`       | Decimal numbers                       |
| String  | `"hello"`, `'world'` | Double quotes support interpolation   |
| Boolean | `true`, `false`      | Logical values                        |
| Nil     | `nil`                | Absence of value                      |
| Vector  | `[1, 2, 3]`          | Ordered list, 0-indexed               |
| Hash    | `{a: 1, b: 2}`       | Key-value map                         |

---

## 4. Printing

```frankie
print "no newline"
puts "with newline"
p 42             # debug: (Integer) 42
p [1, 2, 3]      # debug: (Vector) [1, 2, 3]
```

---

## 5. String Interpolation

Double-quoted strings support `#{}` interpolation. Any expression is valid inside:

```frankie
name = "Frankie"
puts "Hello, #{name}!"
puts "Sum = #{1 + 2 + 3}"
puts "Hash = #{h}"
```

---

## 6. Arithmetic

```frankie
x = 10 + 5      # addition
y = 10 - 3      # subtraction
z = 4 * 5       # multiplication
w = 10 / 3      # float division → 3.333...
m = 10 % 3      # modulo → 1
e = 2 ** 8      # exponentiation (Fortran)
i = 10 // 3     # integer division (Fortran)
```

### Compound Assignment

All arithmetic operators have a compound assignment form:

```frankie
x += 5    # x = x + 5
x -= 3    # x = x - 3
x *= 2    # x = x * 2
x /= 4    # x = x / 4   (float division)
x //= 3   # x = x // 3  (integer division, Fortran)
x **= 2   # x = x ** 2  (exponentiation, Fortran)
x %= 7    # x = x % 7

# Also works on vector elements
v[0] += 10
v[i] *= 2
```

---

## 7. Comparison & Logic

```frankie
x == y    # equal
x != y    # not equal
x < y     # less than
x <= y    # less than or equal
x > y     # greater than
x >= y    # greater than or equal

a and b   # logical and
a or b    # logical or
not a     # logical not
```

---

## 8. Ranges

```frankie
1..10     # inclusive range: 1 to 10
1...10    # exclusive range: 1 to 9 (excludes end)
```

Ranges work as for-loop iterables and as slice indices.

---

## 9. Vectors

```frankie
v = [1, 2, 3, 4, 5]
w = vec(1..10)          # from range: [1,2,3,...,10]

# Indexing (0-based, negatives count from end)
v[0]      # 1
v[-1]     # 5

# Range slicing
v[1..3]   # [2, 3, 4]
v[-2..-1] # [4, 5]
v[0...3]  # [1, 2, 3]  (exclusive end)

# Assignment
v[0] = 99

# Vectorized arithmetic (R-style)
v * 2              # [2, 4, 6, 8, 10]
v + [10,10,10,10,10]  # [11,12,13,14,15]
```

Vector methods: `.length`, `.sort`, `.uniq`, `.first`, `.last`, `.reverse`,
`.push(x)`, `.pop()`, `.join(sep)`, `.flatten`, `.empty?`,
`.sum`, `.min`, `.max`, `.mean`

---

## 10. Hashes

```frankie
h = {name: "Alice", age: 30}   # symbol keys
h2 = {0: "zero", 1: "one"}     # integer keys
```

Keys use `:name` symbol syntax (stored as strings internally).

```frankie
# Access (nil-safe — missing keys return nil)
h[:name]            # "Alice"
h[:missing]         # nil

# Write / add
h[:city] = "Lima"

# Methods
h.keys              # [name, age]
h.values            # [Alice, 30]
h.size              # 2
h.has_key?(:name)   # true
h.fetch(:x, "def")  # "def"  (default if missing)
h.delete(:age)
h.merge({z: 1})     # non-destructive merge
h.each do |k, v|    # iterate key/value pairs
  puts "#{k}: #{v}"
end
```

---

## 11. Conditionals

```frankie
if x > 10
  puts "big"
elsif x == 10
  puts "ten"
else
  puts "small"
end

unless logged_in
  puts "Please log in."
end

# Postfix — valid after any statement
puts "positive" if x > 0
x = 0 unless x > 0
puts "hi" unless done
```

---

## 12. Loops

### while / end

```frankie
while x > 0
  x = x - 1
end
```

### until / end

```frankie
until x == 10
  x = x + 1
end
```

### do...while (Fortran-style)

Body executes at least once.

```frankie
do
  x = x + 1
while x < 10
```

### for...in / end

```frankie
for i in 1..5
  puts i
end

for item in my_vector
  puts item
end
```

### N.times do / end

```frankie
5.times do
  puts "hi"
end

5.times do |i|
  puts i
end
```

### .each do / end

```frankie
[1, 2, 3].each do |x|
  puts x
end

# Two params on a hash → key/value
{a: 1, b: 2}.each do |key, val|
  puts "#{key} = #{val}"
end
```

### .each_with_index do / end

```frankie
["a", "b", "c"].each_with_index do |val, idx|
  puts "#{idx}: #{val}"
end
```

### .map do / end

```frankie
squares = [1, 2, 3].map do |x|
  x ** 2
end
# [1, 4, 9]
```

---

## 13. Functions

```frankie
def greet(name)
  return "Hello, #{name}!"
end

result = greet("World")
```

- Functions use `def...end`
- Parameters are positional
- `return` is required (no implicit last-expression return)
- Recursion is fully supported
- Variables in outer scope are accessible (closure-like behaviour)

---

## 14. Named Arguments

```frankie
puts paste("a", "b", "c", sep: "-")   # a-b-c
```

Named args use `name: value` at the call site and map to Python keyword arguments.

---

## 15. Pipe Operator `|>` (R-inspired)

Passes the left-hand value as the first argument to the right-hand function:

```frankie
data |> sum                      # sum(data)
data |> mean |> puts             # puts(mean(data))
data |> stdev |> floor |> puts   # chain of three
```

---

## 16. Error Handling

```frankie
begin
  risky_operation()
rescue e
  puts "Error: #{e}"
ensure
  puts "Always runs"
end

raise "descriptive message"
raise "code #{code} invalid" if code < 0
```

- `begin...rescue e...end` — catches any runtime error, binds message to `e`
- `ensure` block always runs (even if no error)
- `raise` throws a runtime error with a message

### Typed Rescue

Rescue clauses can specify an error type to catch only that category:

```frankie
begin
  x = 10 // 0
rescue ZeroDivisionError e
  puts "division by zero: #{e}"
rescue RuntimeError e
  puts "runtime error: #{e}"
rescue e
  puts "something else: #{e}"
ensure
  puts "always runs"
end
```

Multiple `rescue` clauses are checked in order; the first matching type wins.
An untyped `rescue e` acts as a catch-all.

Supported error types: `RuntimeError`, `TypeError`, `ValueError`,
`ZeroDivisionError`, `IndexError`, `KeyError`, `IOError`,
`FileNotFoundError`, `OverflowError`, `NameError`, `AttributeError`,
`StopIteration`, `Exception`, `Error` (alias for `Exception`).

---

## 17. Multi-file Programs (`require`)

```frankie
require "utils"          # loads utils.fk from current directory
require "lib/helpers"    # loads lib/helpers.fk
```

- Adds `.fk` extension automatically if omitted
- Each file is loaded at most once (subsequent `require` of same file is a no-op)
- Definitions from the required file become available in the requiring file

---

## 18. Regex

All regex functions use `(string, pattern)` argument order.

```frankie
matches(string, pattern)            # → true/false
match(string, pattern)              # → match object or nil
match_all(string, pattern)          # → vector of all matches
sub(string, pattern, replacement)   # → string with first match replaced
gsub(string, pattern, replacement)  # → string with all matches replaced
string =~ pattern                   # → index of first match or nil
regex(pattern, flags)               # → compiled regex object
```

Flags: `"i"` (case-insensitive), `"m"` (multiline), `"s"` (dot matches newline).

```frankie
matches("hello", "ell")                  # true
match_all("1 and 2 and 3", "[0-9]+")    # [1, 2, 3]
gsub("aa bb aa", "aa", "cc")            # "cc bb cc"
"hello frankie" =~ "frankie"            # 6
regex("[a-z]+", "i")                    # case-insensitive pattern
```

---

## 19. File I/O

```frankie
file_write(path, content)     # write string to file (overwrites)
file_append(path, content)    # append string to file
file_read(path)               # read entire file as string
file_lines(path)              # read file as vector of lines
file_exists(path)             # → true/false
file_delete(path)             # delete file, → true/false
```

---

## 20. String Formatting

```frankie
sprintf(format, *args)        # C-style format string
paste(*args, sep: " ")        # join values with separator
```

```frankie
sprintf("%-10s %d", "Frankie", 1)    # "Frankie     1"
paste("2025", "03", "14", sep: "-")  # "2025-03-14"
```

---

## 21. Input

```frankie
name  = input("Prompt: ")          # string
age   = input_int("Age: ")         # integer
score = input_float("Score: ")     # float
```

---

## 22. Type Conversion

```frankie
to_int("42")      # → 42
to_float("3.14")  # → 3.14
to_str(100)       # → "100"
```

---

## 23. Math & Statistics Builtins

| Function              | Description                             |
|-----------------------|-----------------------------------------|
| `sqrt(x)`             | Square root                             |
| `abs(x)`              | Absolute value                          |
| `floor(x)`            | Round down                              |
| `ceil(x)`             | Round up                                |
| `min(a, b)`           | Minimum of two values                   |
| `min(vec)`            | Minimum of a vector                     |
| `max(a, b)`           | Maximum of two values                   |
| `max(vec)`            | Maximum of a vector                     |
| `sum(vec)`            | Sum of vector                           |
| `mean(vec)`           | Arithmetic mean                         |
| `median(vec)`         | Median value                            |
| `stdev(vec)`          | Sample standard deviation               |
| `variance(vec)`       | Sample variance                         |
| `clamp(x, lo, hi)`    | Clamp x between lo and hi               |
| `seq(start, stop, step)` | Numeric sequence (R's `seq()`)       |
| `linspace(start, stop, n)` | n evenly-spaced values             |
| `rep(x, n)`           | Repeat x n times (R's `rep()`)          |

---

## 24. String Methods

| Method             | Description                        |
|--------------------|------------------------------------|
| `.upcase`          | Convert to uppercase               |
| `.downcase`        | Convert to lowercase               |
| `.length`          | Character count                    |
| `.reverse`         | Reverse the string                 |
| `.strip`           | Remove leading/trailing whitespace |
| `.include?(s)`     | True if s is a substring           |
| `.start_with?(s)`  | True if starts with s              |
| `.end_with?(s)`    | True if ends with s                |
| `.split(sep)`      | Split by separator → vector        |
| `[i]`              | Character at index (0-based, negative ok) |
| `[a..b]`           | Inclusive substring slice          |
| `[a...b]`          | Exclusive substring slice          |

---

## 25. System

```frankie
exit(0)           # exit program with code
argv()            # command-line args as vector
env("KEY", "def") # read environment variable with default
```

---

## 26. Reserved Words

`def`, `end`, `if`, `elsif`, `else`, `unless`, `while`, `until`, `for`, `in`,
`do`, `return`, `true`, `false`, `nil`, `print`, `puts`, `p`, `and`, `or`, `not`,
`begin`, `rescue`, `ensure`, `raise`, `require`

---

## Grammar Summary (informal)

```
program     ::= statement*
statement   ::= func_def | if_stmt | unless_stmt | while_stmt | until_stmt
              | for_stmt | do_while | begin_rescue | raise_stmt | require_stmt
              | return_stmt | print_stmt | expr_stmt [postfix_if]
postfix_if  ::= ('if' | 'unless') expr
func_def    ::= 'def' IDENT ['(' params ')'] body 'end'
if_stmt     ::= 'if' expr body ('elsif' expr body)* ['else' body] 'end'
unless_stmt ::= 'unless' expr body ['else' body] 'end'
while_stmt  ::= 'while' expr body 'end'
until_stmt  ::= 'until' expr body 'end'
do_while    ::= 'do' body 'while' expr
for_stmt    ::= 'for' IDENT 'in' expr body 'end'
begin_rescue::= 'begin' body ['rescue' [IDENT] body] ['ensure' body] 'end'
raise_stmt  ::= 'raise' [expr]
require_stmt::= 'require' expr
expr        ::= pipe_expr
pipe_expr   ::= assign ('|>' call_or_ident)*
assign      ::= IDENT '=' expr | index_assign | or_expr
or_expr     ::= and_expr ('or' and_expr)*
and_expr    ::= not_expr ('and' not_expr)*
not_expr    ::= 'not' not_expr | comparison
comparison  ::= addition (('=='|'!='|'<'|'<='|'>'|'>='|'=~') addition)*
addition    ::= multiply (('+' | '-') multiply)*
multiply    ::= unary (('*'|'/'|'//'|'%'|'**') unary)*
unary       ::= '-' postfix | postfix [('..' | '...') unary]
postfix     ::= primary ('.' method | '[' expr ']')*
primary     ::= INTEGER | FLOAT | STRING | BOOL | NIL
              | IDENT ['(' args ')']
              | '[' elements ']'
              | '{' pairs '}'
              | '(' expr ')'
              | input_expr
```

---

*Frankie v1.2 — "It's alive!" 🧟⚡*
