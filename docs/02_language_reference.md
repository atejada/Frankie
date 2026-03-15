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
puts "Hash: #{my_hash}"
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
  x = x + 1
end

# until
until x == 10
  x = x + 1
end

# do...while — body runs at least once (Fortran-style)
do
  x = x + 1
while x < 10

# for...in
for i in 1..5
  puts i
end

for item in ["apple", "banana"]
  puts item
end
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

```ruby
def factorial(n)
  if n <= 1
    return 1
  end
  return n * factorial(n - 1)
end
```

---

## Destructuring Assignment

```ruby
a, b, c = [10, 20, 30]
puts a    # 10

# From a function returning a vector
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

## Named Arguments

```ruby
puts paste("2025", "03", "14", sep: "-")    # 2025-03-14
puts sprintf("%-10s %d", "Frankie", 1)
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

---

## Multi-file Programs

```ruby
require "utils"         # loads utils.fk
require "lib/helpers"   # loads lib/helpers.fk
```

Each file is loaded at most once.

---

## Input

```ruby
name  = input("Name: ")
age   = input_int("Age: ")
score = input_float("Score: ")
```

---

## Type Conversion

```ruby
to_int("42")      # 42
to_float("3.14")  # 3.14
to_str(100)       # "100"
```
