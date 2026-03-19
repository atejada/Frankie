# Language Reference

## Comments

```ruby
# This is a single-line comment
```

---

## Variables

Frankie is dynamically typed. Variables are created on first assignment.

```ruby
x      = 42
name   = "Frankie"
pi     = 3.14159
alive  = true
empty  = nil
```

---

## Types

| Type    | Example              | Notes                               |
|---------|----------------------|-------------------------------------|
| Integer | `42`, `-7`           | Whole numbers                       |
| Float   | `3.14`, `-0.5`       | Decimal numbers                     |
| String  | `"hello"`, `'world'` | Double quotes support interpolation |
| Boolean | `true`, `false`      | Logical values                      |
| Nil     | `nil`                | Absence of value                    |
| Vector  | `[1, 2, 3]`          | Ordered list, 0-indexed             |
| Hash    | `{name: "Alice"}`    | Key-value map                       |

---

## String Interpolation

Double-quoted strings support `#{}` to embed any expression:

```ruby
name = "Frankie"
puts "Hello, #{name}!"
puts "Two plus two is #{2 + 2}"
puts "Pi ≈ #{3.14159}"
```

Triple-quoted strings span multiple lines:

```ruby
text = """
  Hello, #{name}!
  Welcome to Frankie.
"""
puts text
```

---

## Output

```ruby
print "no newline"
puts "adds a newline"
p 42              # debug: (Integer) 42
p [1, 2, 3]       # debug: (Vector) [1, 2, 3]
```

---

## Input

```ruby
name  = input("Name: ")
age   = input_int("Age: ")
score = input_float("Score: ")
```

---

## Arithmetic

```ruby
10 + 5      # 15       addition
10 - 3      # 7        subtraction
4  * 5      # 20       multiplication
10 / 3      # 3.333... float division
10 // 3     # 3        integer division  (Fortran)
10 % 3      # 1        modulo
2  ** 8     # 256      exponentiation   (Fortran)
```

### Compound Assignment

```ruby
x += 5    # x = x + 5
x -= 3    # x = x - 3
x *= 2    # x = x * 2
x /= 4    # x = x / 4   (float)
x //= 3   # x = x // 3  (integer, Fortran)
x **= 2   # x = x ** 2  (Fortran)
x %= 7    # x = x % 7

v[0] += 10   # works on vector elements too
```

---

## Comparison & Logic

```ruby
x == y    # equal
x != y    # not equal
x <  y    # less than
x <= y    # less than or equal
x >  y    # greater than
x >= y    # greater than or equal
x =~ pat  # regex match — returns position or nil

a and b   # logical and
a or  b   # logical or
not a     # logical not
```

---

## Ranges

```ruby
1..10     # inclusive: 1, 2, 3, ..., 10
1...10    # exclusive: 1, 2, 3, ..., 9
```

Ranges work as loop iterables and slice indices (including negative bounds):

```ruby
for i in 1..5
  puts i
end

s = "Frankenstein"
puts s[0..6]      # Franken
puts s[-5..-1]    # stein
```

---

## Conditionals

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
x = 0 unless x > 0
```

---

## Case / When

```ruby
case day
when "Saturday", "Sunday"
  puts "Weekend!"
when "Monday"
  puts "Start of the week"
else
  puts "Midweek"
end

# Bare case — no subject, uses truthy conditions
case
when x < 0
  puts "negative"
when x == 0
  puts "zero"
when x > 0
  puts "positive"
end
```

---

## Loops

```ruby
# while
while x < 10
  x += 1
end

# until
until x == 10
  x += 1
end

# do...while — body runs at least once (Fortran-style)
do
  x += 1
while x < 10

# for...in
for i in 1..5
  puts i
end

for item in ["apple", "banana"]
  puts item
end
```

### Loop Control

```ruby
# next — skip to next iteration (like continue)
[1,2,3,4,5].each do |n|
  next if n % 2 == 0
  puts n              # 1 3 5
end

# break — exit the loop early
[1,2,3,4,5].each do |n|
  break if n > 3
  puts n              # 1 2 3
end

# break with value
result = [1,2,3,4,5].each do |n|
  break n * 10 if n == 3
end
puts result           # 30

# postfix forms
next if condition
break if condition
```

---

## Constants

`UPPER_SNAKE_CASE` identifiers are treated as constants. Reassignment prints a warning and preserves the original value.

```ruby
MAX_SIZE = 100
PI       = 3.14159
APP_NAME = "Frankie"

puts MAX_SIZE   # 100
MAX_SIZE = 200  # Warning: MAX_SIZE is a constant
puts MAX_SIZE   # 100  (unchanged)
```

---

## Functions

```ruby
def add(a, b)
  return a + b
end

puts add(3, 4)    # 7
```

- `return` is required — no implicit last-expression return
- Recursion is fully supported
- Variables from outer scope are accessible

### Default Parameters

```ruby
def greet(name, msg="Hello", punct="!")
  puts "#{msg}, #{name}#{punct}"
end

greet("Alice")             # Hello, Alice!
greet("Bob", "Hi")         # Hi, Bob!
greet("Carol", "Hey", ".") # Hey, Carol.
```

Required parameters must come before optional ones.

### Named Arguments

```ruby
puts paste("2025", "03", "14", sep: "-")    # 2025-03-14
puts sprintf("%-10s %d", "Frankie", 1)
```

---

## Destructuring Assignment

```ruby
a, b, c = [10, 20, 30]
puts a    # 10

def min_max(v)
  return [min(v), max(v)]
end

lo, hi = min_max([3,1,4,1,5,9])
puts "#{lo}..#{hi}"    # 1..9

# Short vectors pad with nil
x, y, z = [1, 2]
puts z    # nil
```

---

## Pipe Operator `|>` (R-inspired)

```ruby
[1,2,3,4,5] |> sum              # 15
[1,2,3,4,5] |> mean |> puts     # 3.0

def double(x)
  return x * 2
end
10 |> double |> puts            # 20
```

---

## Nil Safety — `&.` Operator

`x&.method` calls `.method` on `x`, returning `nil` if `x` is nil — no crash.

```ruby
user    = {name: "Alice"}
missing = nil

puts user["name"]&.upcase       # ALICE
puts missing&.upcase            # nil  (no crash)
puts missing&.upcase&.reverse   # nil  (chain short-circuits)
puts missing&.length            # nil
```

Chains short-circuit at the first `nil` — once a nil is encountered, the rest of the chain is skipped.

---

## Error Handling

```ruby
begin
  risky()
rescue e
  puts "Error: #{e}"
ensure
  puts "Always runs"
end

raise "message"
raise "invalid value: #{x}" if x < 0
```

### Typed Rescue

```ruby
begin
  x = 10 // 0
rescue ZeroDivisionError e
  puts "division by zero"
rescue TypeError e
  puts "wrong type: #{e}"
rescue RuntimeError e
  puts "runtime error: #{e}"
rescue e
  puts "other: #{e}"
ensure
  puts "always runs"
end
```

Multiple `rescue` clauses are matched in order; the first matching type wins.

Supported types: `RuntimeError`, `TypeError`, `ValueError`, `ZeroDivisionError`,
`IndexError`, `KeyError`, `IOError`, `FileNotFoundError`, `OverflowError`,
`NameError`, `AttributeError`, `Exception` / `Error`.

---

## Multi-file Programs

```ruby
require "utils"         # loads utils.fk
require "lib/helpers"   # loads lib/helpers.fk
```

Each file is loaded at most once.

---

## Type Conversion

```ruby
to_int("42")      # 42
to_float("3.14")  # 3.14
to_str(100)       # "100"
```

## Type Checking

```ruby
is_integer(42)      # true
is_float(3.14)      # true
is_string("hi")     # true
is_vector([1,2,3])  # true
is_nil(nil)         # true
is_bool(true)       # true
```
