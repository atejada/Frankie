# 🧟 Frankie Programming Language

```
  _____                 _    _
 |  ___| __ __ _ _ __ | | _(_) ___
 | |_ | '__/ _` | '_ \| |/ / |/ _ \
 |  _|| | | (_| | | | |   <| |  __/
 |_|  |_|  \__,_|_| |_|_|\_\_|\___|

 The Frankie Language v1.0
 Stitched together from Ruby • Python • R • Fortran
```

> Designed and Developed by **Claude** and **Blag Aka. Alvaro Tejada Galindo**.  
> If you have any questions, feel free to ask me. Have fun 🤓

---

## What is Frankie?

![Frankie - The Programming Language](https://github.com/atejada/Frankie/blob/main/The%20Frankie%20Programming%20Language.png)

Frankie is a **procedural, expressive, terminal-native programming language** named after Frankenstein — because it's lovingly stitched together from the best parts of four legendary languages:

| Donor Language | What Frankie Borrows |
|---|---|
| **Ruby** | Syntax, `do...end`, postfix `if/unless`, `.times`, `.each`, `.map`, string interpolation, `begin/rescue/end` |
| **Python** | Clean semantics, rich data structures, execution model |
| **R** | Vectors, `mean/sum/stdev/median`, pipe operator `\|>`, `seq()`, statistical builtins |
| **Fortran** | Numeric precision focus, `do...while`, explicit integer division `//`, power `**` |

Frankie is **not object-oriented**. It's proudly procedural — functions, data, loops, and logic. No classes, no `self`, no inheritance. Just clean, powerful code.

---

## Requirements

- Python 3.10 or higher (the Frankie compiler is written in Python)
- No external dependencies — pure Python standard library

---

## Installation

Clone or download this repository, then run programs using the `frankiec.py` compiler:

```bash
# Run a Frankie program
python3 frankiec.py run examples/hello.fk

# Compile to Python source (for inspection)
python3 frankiec.py build myprogram.fk

# Check syntax only
python3 frankiec.py check myprogram.fk

# Show version
python3 frankiec.py version
```

### Optional: Install as a shell command

```bash
alias frankiec="python3 /path/to/frankie/frankiec.py"
frankiec run hello.fk
```

---

## File Extension

Frankie source files use the `.fk` extension.

---

## Quick Start

```ruby
name = "World"
puts "Hello, #{name}!"
puts "Welcome to Frankie!"
```

```bash
python3 frankiec.py run hello.fk
# Hello, World!
# Welcome to Frankie!
```

---

## Language Reference

### Comments

```ruby
# This is a comment — Ruby style
```

---

### Variables

Frankie is dynamically typed. Variables are created on assignment.

```ruby
x = 42
name = "Frankie"
pi = 3.14159
alive = true
nothing = nil
```

---

### Types

| Frankie Type | Example | Notes |
|---|---|---|
| Integer | `42`, `-7` | Whole numbers |
| Float | `3.14`, `-0.001` | Decimal numbers |
| String | `"hello"`, `'world'` | Text (double quotes support interpolation) |
| Boolean | `true`, `false` | Logical values |
| Nil | `nil` | Absence of value |
| Vector | `[1, 2, 3]` | Ordered list (R-inspired) |
| Hash | `{name: "Alice", age: 30}` | Key-value pairs |

---

### String Interpolation

Use `#{}` inside double-quoted strings to embed any expression:

```ruby
name = "Frankie"
age = 1
puts "Hello from #{name} v#{age}!"
puts "Two plus two is #{2 + 2}"
puts "Pi ≈ #{3.14159}"
```

---

### Output

```ruby
print "no newline at end"
puts "adds a newline"
p 42              # debug: prints (Integer) 42
p [1, 2, 3]       # debug: prints (Vector) [1, 2, 3]
p {name: "x"}     # debug: prints (Hash) {name: x}
```

---

### Arithmetic

```ruby
x = 10 + 5      # addition
y = 10 - 3      # subtraction
z = 4 * 5       # multiplication
w = 10 / 3      # float division → 3.333...
m = 10 % 3      # modulo → 1
e = 2 ** 8      # exponentiation → 256   (Fortran heritage)
i = 10 // 3     # integer division → 3   (Fortran heritage)
```

---

### Ranges

```ruby
r1 = 1..10      # inclusive: 1, 2, 3, ..., 10
r2 = 1...10     # exclusive: 1, 2, 3, ..., 9

for i in 1..5
  puts i
end
```

---

### Vectors (R-inspired)

Vectors are ordered lists with built-in math operations:

```ruby
v = [10, 20, 30, 40, 50]

# Statistical functions
puts sum(v)        # 150
puts mean(v)       # 30.0
puts min(v)        # 10
puts max(v)        # 50
puts length(v)     # 5
puts median(v)     # 30.0
puts stdev(v)      # standard deviation
puts variance(v)   # variance

# Vectorized arithmetic (R-style)
v2 = v * 2                    # [20, 40, 60, 80, 100]
v3 = v + [1, 2, 3, 4, 5]     # [11, 22, 33, 44, 55]

# From range
w = vec(1..10)    # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Indexing (0-based, negatives count from end)
puts v[0]         # 10
puts v[-1]        # 50
v[0] = 99         # assignment

# Range slicing
puts v[1..3]      # [20, 30, 40]
puts v[-2..-1]    # [40, 50]
puts v[0...3]     # [10, 20, 30]  (exclusive end)
```

---

### Hashes

```ruby
person = {name: "Alice", age: 30, city: "Lima"}

# Read (nil-safe — missing keys return nil, not an error)
puts person[:name]         # Alice
puts person[:missing]      # nil

# Write / add
person[:job] = "Engineer"

# Methods
puts person.keys           # [name, age, city, job]
puts person.values         # [Alice, 30, Lima, Engineer]
puts person.size           # 4
puts person.has_key?(:age) # true

# Safe fetch with default
puts person.fetch(:salary, 0)   # 0

# Delete
person.delete(:city)

# Merge (non-destructive)
extra = {email: "alice@x.com"}
full = person.merge(extra)

# Iterate
person.each do |key, val|
  puts "#{key}: #{val}"
end

# Nested hashes
config = {db: {host: "localhost", port: 5432}}
puts config[:db][:host]    # localhost

# Integer keys
leds = {0: ["_", "|_|"], 1: [" ", "  |"]}
puts leds[0][0]            # _
```

---

### Conditionals

```ruby
if score >= 90
  puts "A"
elsif score >= 80
  puts "B"
else
  puts "F"
end

unless logged_in
  puts "Please log in."
end

# Postfix — works on any statement
puts "Adult!" if age >= 18
puts "Minor!" unless age >= 18
x = x + 1 unless x >= 100
```

---

### Loops

```ruby
# while / end
while x < 10
  x = x + 1
end

# until / end
until x == 10
  x = x + 1
end

# do...while (Fortran-inspired — body runs at least once)
do
  x = x + 1
  puts x
while x < 5

# for...in with range
for i in 1..5
  puts i
end

# for...in with vector
for item in ["apple", "banana", "cherry"]
  puts item
end

# N.times
5.times do
  puts "hi"
end

5.times do |i|
  puts "iteration #{i}"
end

# .each
[10, 20, 30].each do |x|
  puts x
end

# .each with hash (two params = key/value)
{a: 1, b: 2}.each do |key, val|
  puts "#{key} => #{val}"
end

# .each_with_index
["a", "b", "c"].each_with_index do |val, idx|
  puts "#{idx}: #{val}"
end

# .map
squares = [1, 2, 3, 4, 5].map do |x|
  x ** 2
end
```

---

### Functions

```ruby
def add(a, b)
  return a + b
end

puts add(3, 4)     # 7
```

Functions require explicit `return`. Recursion is fully supported:

```ruby
def factorial(n)
  if n <= 1
    return 1
  end
  return n * factorial(n - 1)
end

puts factorial(10)    # 3628800
```

---

### Named Arguments

Functions can be called with named arguments using `name: value` syntax:

```ruby
puts paste("2025", "03", "14", sep: "-")   # 2025-03-14
puts sprintf("%-10s %d", "Frankie", 1)
```

---

### Pipe Operator (R-inspired `|>`)

```ruby
result = [1, 2, 3, 4, 5] |> sum      # 15
[1, 2, 3, 4, 5] |> mean |> puts      # 3.0

def double(x)
  return x * 2
end
10 |> double |> puts                  # 20
```

---

### Error Handling

```ruby
begin
  x = 10 / 0
rescue e
  puts "Caught: #{e}"     # Caught: division by zero
end

# With ensure (always runs)
begin
  raise "something broke"
rescue e
  puts "Error: #{e}"
ensure
  puts "Cleanup done"
end

# Raise with a message
def must_be_positive(n)
  if n <= 0
    raise "Expected positive, got #{n}"
  end
  return n
end

begin
  must_be_positive(-5)
rescue e
  puts e
end
```

---

### Multi-file Programs (`require`)

Split your program across multiple `.fk` files. Each file is loaded once:

```ruby
# mathlib.fk
def circle_area(r)
  return 3.14159 * r * r
end
```

```ruby
# main.fk
require "mathlib"
puts circle_area(5)    # 78.53975
```

---

### Regex

All regex functions use `(string, pattern)` argument order:

```ruby
# Test for a match
puts matches("hello world", "world")        # true
puts matches("hello world", "xyz")          # false

# Find first match (returns match object or nil)
m = match("price: 42 dollars", "[0-9]+")
puts m != nil                               # true

# Find all matches
nums = match_all("1 and 2 and 3", "[0-9]+")
puts nums                                   # [1, 2, 3]

# Replace first / all
puts sub("Hello World World", "World", "Frankie")    # Hello Frankie World
puts gsub("Hello World World", "World", "Frankie")   # Hello Frankie Frankie

# Match position operator =~  (returns index or nil)
puts "hello frankie" =~ "frankie"           # 6
puts "hello world" =~ "xyz"                 # nil

# Compiled regex with flags (i=case-insensitive, m=multiline, s=dotall)
r = regex("[a-z]+", "i")
puts matches("HELLO", r)                    # true
```

---

### File I/O

```ruby
# Write and read
file_write("/tmp/data.txt", "Hello\nWorld\n")
puts file_read("/tmp/data.txt")

# Read as vector of lines
lines = file_lines("/tmp/data.txt")
puts length(lines)        # 2

# Append
file_append("/tmp/data.txt", "Frankie\n")

# Check existence and delete
puts file_exists("/tmp/data.txt")    # true
file_delete("/tmp/data.txt")
puts file_exists("/tmp/data.txt")    # false

# Error handling for missing files
begin
  file_read("/tmp/no_such_file.txt")
rescue e
  puts "Error: #{e}"
end
```

---

### String Formatting

```ruby
puts sprintf("Hello %s, you are %d years old", "Alice", 30)
puts sprintf("Pi is %.4f", 3.14159)
puts sprintf("%-10s %5d", "Frankie", 1)

puts paste("Hello", "World")              # Hello World
puts paste("2025", "03", "14", sep: "-") # 2025-03-14
```

---

### String Methods

```ruby
s = "Hello, Frankie!"

puts s.upcase            # HELLO, FRANKIE!
puts s.downcase          # hello, frankie!
puts s.length            # 15
puts s.reverse           # !eiknarF ,olleH
puts s.strip             # trims whitespace
puts s.include?("ie")    # true
puts s.start_with?("He") # true
puts s.end_with?("!")    # true
puts s.split(", ")       # [Hello, Frankie!]

# Indexing and slicing
puts s[0]       # H
puts s[-1]      # !
puts s[0..4]    # Hello
puts s[-7..-1]  # Frankie!
```

---

### Vector Methods

```ruby
v = [3, 1, 4, 1, 5, 9, 2, 6]

puts v.length    # 8
puts v.sort      # [1, 1, 2, 3, 4, 5, 6, 9]
puts v.uniq      # [3, 1, 4, 5, 9, 2, 6]
puts v.first     # 3
puts v.last      # 6
puts v.sum       # 31
puts v.min       # 1
puts v.max       # 9
puts v.mean      # 3.875
puts v.reverse   # [6, 2, 9, 5, 1, 4, 1, 3]
v.push(99)
v.pop()

puts v.join(", ")

# Slicing
puts v[1..3]     # [1, 4, 1]
puts v[-2..-1]   # [2, 6]
```

---

### Hash Methods

```ruby
h = {name: "Alice", age: 30}

puts h.keys                   # [name, age]
puts h.values                 # [Alice, 30]
puts h.size                   # 2
puts h.has_key?(:name)        # true
puts h.fetch(:missing, "N/A") # N/A
h.delete(:age)
h2 = h.merge({city: "Lima"})

h.each do |key, val|
  puts "#{key}: #{val}"
end
```

---

### Math & Statistics Builtins

| Function | Description |
|---|---|
| `sqrt(x)` | Square root |
| `abs(x)` | Absolute value |
| `floor(x)` | Round down |
| `ceil(x)` | Round up |
| `min(a, b)` or `min(vec)` | Minimum |
| `max(a, b)` or `max(vec)` | Maximum |
| `sum(vec)` | Sum of vector |
| `mean(vec)` | Arithmetic mean |
| `median(vec)` | Median value |
| `stdev(vec)` | Sample standard deviation |
| `variance(vec)` | Sample variance |
| `seq(start, stop, step)` | Numeric sequence like R's `seq()` |
| `linspace(start, stop, n)` | n evenly-spaced values |
| `rep(x, n)` | Repeat x n times like R's `rep()` |
| `clamp(x, lo, hi)` | Clamp x between lo and hi |

---

### Input

```ruby
name  = input("What is your name? ")
age   = input_int("How old are you? ")
score = input_float("Enter your score: ")
```

---

### Type Conversion

```ruby
x = to_int("42")
y = to_float("3.14")
z = to_str(100)
```

---

### System

```ruby
exit(0)          # exit with code
args = argv()    # command-line arguments as vector
home = env("HOME", "/tmp")  # environment variable with default
```

---

## Example Programs

The `examples/` directory contains:

| File | Description |
|---|---|
| `hello.fk` | Hello World |
| `fizzbuzz.fk` | Classic FizzBuzz |
| `fibonacci.fk` | Recursive Fibonacci |
| `stats.fk` | R-style statistical analysis |
| `sorting.fk` | Bubble sort & selection sort |
| `hashmaps.fk` | Full hashmap feature tour |
| `leds.fk` | 7-segment LED digit display |
| `calculator.fk` | Interactive terminal calculator |
| `greet.fk` | Interactive terminal greeter |
| `showcase.fk` | All features in one program |
| `test_errors.fk` | Error handling examples |
| `test_regex.fk` | Regex examples |

---

## Project Structure

```
frankie/
├── frankiec.py          ← Compiler CLI (run, build, check, version)
├── frankie_stdlib.py    ← Runtime standard library (~450 lines)
├── README.md            ← This file
├── SPEC.md              ← Full language specification
├── compiler/
│   ├── lexer.py         ← Tokeniser: source → token stream (~410 lines)
│   ├── parser.py        ← Parser: tokens → AST, recursive descent (~600 lines)
│   ├── ast_nodes.py     ← 35+ AST node dataclasses (~260 lines)
│   └── codegen.py       ← Code generator: AST → Python source (~610 lines)
└── examples/
    └── *.fk             ← 12 example programs
```

Total compiler: ~2,300 lines of Python.

---

## How the Compiler Works

Frankie uses a **transpilation** architecture — Frankie source is compiled to Python, then executed:

```
Source (.fk)
    │
    ▼
┌─────────┐
│  Lexer  │  lexer.py — converts source text into a typed token stream
└────┬────┘
     │
     ▼
┌─────────┐
│ Parser  │  parser.py — recursive descent parser builds an AST
└────┬────┘
     │
     ▼
┌─────────┐
│ CodeGen │  codegen.py — walks the AST and emits Python 3 source
└────┬────┘
     │
     ▼
┌──────────────┐
│ Python exec  │  frankie_stdlib injected; Python runtime executes it
└──────────────┘
```

---

## Design Decisions

- **No classes** — Frankie is fully procedural. Functions are the primary unit of abstraction.
- **Vector-aware arithmetic** — Like R, `[1,2,3] * 2` gives `[2,4,6]`. Scalar-vector and vector-vector operations work transparently.
- **Postfix `if/unless`** — Works after any statement, including `puts` and assignments.
- **`do...while`** — Fortran-style; body always runs at least once.
- **Pipe `|>`** — R's pipe operator for clean data transformation chains.
- **Explicit `return`** — Unlike Ruby, Frankie does not implicitly return the last expression.
- **Named arguments** — `func(x, sep: "-")` for readable call sites.
- **Nil-safe indexing** — Missing hash keys return `nil` rather than raising an error.
- **Symbol keys** — `:name` syntax for hash keys, identical to Ruby symbols but stored as strings.

---

## License

Frankie is open and free. Build things, break things, stitch things together. That's the spirit.

---

*"It's alive!"* 🧟⚡
