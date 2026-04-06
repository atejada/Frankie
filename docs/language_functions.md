# Functions

## Defining a Function

Use `def` to define a named function. The last expression is implicitly returned — `return` is optional at the end.

```ruby
def add(a, b)
  a + b
end

puts add(3, 4)   # 7
```

`return` is still useful for early exits:

```ruby
def divide(a, b)
  return nil if b == 0
  a / b
end

puts divide(10, 2)   # 5.0
puts divide(10, 0)   # nil
```

---

## Default Parameters

Parameters can have default values. Required parameters must come before optional ones.

```ruby
def greet(name, msg = "Hello", punct = "!")
  puts "#{msg}, #{name}#{punct}"
end

greet("Alice")              # Hello, Alice!
greet("Bob", "Hi")          # Hi, Bob!
greet("Carol", "Hey", ".")  # Hey, Carol.
```

---

## Named Arguments

Some built-in functions accept named arguments with `key: value` syntax:

```ruby
puts paste("2025", "03", "14", sep: "-")   # 2025-03-14
puts sprintf("%-10s %d", "Frankie", 1)
```

---

## Multiple Return Values

Return a vector and destructure it at the call site:

```ruby
def min_max(v)
  [min(v), max(v)]
end

lo, hi = min_max([3, 1, 4, 1, 5, 9])
puts "#{lo}..#{hi}"   # 1..9

def stats(v)
  [mean(v), median(v), stdev(v)]
end

avg, med, sd = stats([10, 20, 30, 40, 50])
puts avg   # 30.0
puts med   # 30
```

---

## Recursion

Functions can call themselves. Frankie supports full recursion.

```ruby
def factorial(n)
  return 1 if n <= 1
  n * factorial(n - 1)
end

puts factorial(10)   # 3628800

def fib(n)
  return n if n <= 1
  fib(n - 1) + fib(n - 2)
end

puts fib(10)   # 55
```

---

## Lambdas — Functions as Values

Use `->` to create an anonymous function that can be stored, passed, and called later.

```ruby
double = ->(x) { x * 2 }
puts double.call(5)   # 10

add = ->(a, b) { a + b }
puts add.call(3, 4)   # 7
```

Multi-statement bodies use `do...end`:

```ruby
clamp = ->(n, lo, hi) do
  return lo if n < lo
  return hi if n > hi
  n
end

puts clamp.call(150, 0, 100)   # 100
puts clamp.call(-5, 0, 100)    # 0
puts clamp.call(42, 0, 100)    # 42
```

Lambdas accept default parameters:

```ruby
greet = ->(name, prefix = "Hello") { "#{prefix}, #{name}!" }
puts greet.call("Alice")         # Hello, Alice!
puts greet.call("Bob", "Hi")     # Hi, Bob!
```

### Lambdas as Arguments

Pass lambdas to functions for higher-order patterns:

```ruby
def apply(fn, val)
  fn.call(val)
end

square = ->(x) { x * x }
puts apply(square, 6)   # 36

# Store in a vector and call each
transforms = [
  ->(x) { x + 1 },
  ->(x) { x * 2 },
  ->(x) { x ** 2 }
]

transforms.each do |fn|
  puts fn.call(5)
end
# 6
# 10
# 25
```

---

## Blocks

Blocks are anonymous chunks of code passed directly to a method call with `do...end` or `{ }`. They are not stored — they run once as part of the method.

```ruby
[1, 2, 3].each do |x|
  puts x * 2
end

result = [1, 2, 3].map do |x|
  x * x
end
puts result   # [1, 4, 9]
```

Single-line blocks can use braces:

```ruby
[1, 2, 3].each do |x| puts x end
```

Blocks are the foundation of Frankie's iterator system — `.map`, `.select`, `.reduce`, `.each_with_object`, and all other iterators take blocks.

---

## The Pipe Operator

Chain function calls without nesting:

```ruby
data = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]

data |> sum |> puts    # 39
data |> mean |> puts   # 3.9

def double(x)
  x * 2
end

10 |> double |> puts   # 20
```

---

## Scope

Variables defined outside a function are readable inside it. Variables assigned inside a function are local to it — they do not affect the outer scope.

```ruby
x = 10

def read_outer
  puts x   # 10 — outer x is readable
end
read_outer

def set_local
  x = 99   # local to set_local
  puts x   # 99
end
set_local
puts x     # 10 — outer x unchanged
```

---

## Multi-file Programs

Split code across files with `require`. Each file is loaded at most once.

```ruby
# lib/math_utils.fk
def circle_area(r)
  PI * r * r
end

# main.fk
require "lib/math_utils"

puts circle_area(5)   # 78.539...
```

`require` resolves paths relative to the current working directory. The `.fk` extension is optional.
