# Lambda

## What is a Lambda?

A Lambda is an anonymous function stored as a value. Unlike a `def` function which is declared and called by name, a lambda can be assigned to a variable, stored in a vector or hash, and passed to other functions. Lambdas bring first-class function behaviour to Frankie.

```ruby
double = ->(x) { x * 2 }
puts double.call(5)   # 10
```

---

## Creating Lambdas

### Single-expression body — braces `{ }`

```ruby
double  = ->(x) { x * 2 }
add     = ->(a, b) { a + b }
greet   = ->(name) { "Hello, #{name}!" }
square  = ->(x) { x * x }
is_even = ->(x) { x % 2 == 0 }
```

### Multi-statement body — `do...end`

```ruby
clamp = ->(n, lo, hi) do
  return lo if n < lo
  return hi if n > hi
  n
end

describe = ->(v) do
  avg = mean(v)
  sd  = stdev(v)
  "mean=#{round(avg,2)}, stdev=#{round(sd,2)}"
end
```

### No parameters

```ruby
timestamp = ->() { now().format("%H:%M:%S") }
puts timestamp.call   # 14:23:07
```

### Default parameters

```ruby
greet = ->(name, prefix = "Hello") { "#{prefix}, #{name}!" }
puts greet.call("Alice")         # Hello, Alice!
puts greet.call("Bob", "Hi")     # Hi, Bob!
```

---

## Calling a Lambda

Use `.call(args)`:

```ruby
add = ->(a, b) { a + b }

puts add.call(3, 4)    # 7
puts add.call(10, 20)  # 30
```

---

## Lambdas as Values

Because lambdas are values, they can be stored and passed anywhere a value can go.

### Stored in a variable

```ruby
transform = ->(x) { x * 3 + 1 }
puts transform.call(5)   # 16
```

### Stored in a vector

```ruby
pipeline = [
  ->(x) { x + 1 },
  ->(x) { x * 2 },
  ->(x) { x ** 2 }
]

pipeline.each do |fn|
  puts fn.call(5)
end
# 6
# 10
# 25
```

### Stored in a hash

```ruby
ops = {
  add:      ->(a, b) { a + b },
  subtract: ->(a, b) { a - b },
  multiply: ->(a, b) { a * b }
}

puts ops["add"].call(10, 3)       # 13
puts ops["subtract"].call(10, 3)  # 7
puts ops["multiply"].call(10, 3)  # 30
```

### Passed to a function

```ruby
def apply(fn, value)
  fn.call(value)
end

square = ->(x) { x * x }
puts apply(square, 7)   # 49

def apply_all(fns, value)
  fns.reduce(value) do |acc, fn|
    fn.call(acc)
  end
end

steps = [->(x) { x + 1 }, ->(x) { x * 3 }, ->(x) { x - 2 }]
puts apply_all(steps, 4)   # (4+1)*3-2 = 13
```

---

## Lambdas vs `def` Functions

| | `def` | Lambda |
|---|---|---|
| Has a name | Yes | No (stored in a variable) |
| Storable as value | No | Yes |
| Passable to functions | No | Yes |
| Default parameters | Yes | Yes |
| Multi-statement body | Yes | Yes (`do...end`) |
| Implicit return | Yes | Yes |
| Explicit `return` | Yes | Yes |
| Recursion | Yes | Via the variable name |

Use `def` for named, reusable functions. Use lambdas when you need to pass behaviour as data.

---

## Higher-order Patterns

Lambdas enable higher-order programming — functions that operate on other functions.

### Map with a lambda

```ruby
double = ->(x) { x * 2 }

result = [1, 2, 3, 4, 5].map do |x|
  double.call(x)
end
puts result   # [2, 4, 6, 8, 10]
```

### Function composition

```ruby
def compose(f, g)
  ->(x) { f.call(g.call(x)) }
end

add1   = ->(x) { x + 1 }
double = ->(x) { x * 2 }

add1_then_double = compose(double, add1)
puts add1_then_double.call(5)   # (5+1)*2 = 12

double_then_add1 = compose(add1, double)
puts double_then_add1.call(5)   # (5*2)+1 = 11
```

### Memoisation

```ruby
def memoize(fn)
  cache = {}
  ->(x) do
    if cache[x] == nil
      cache[x] = fn.call(x)
    end
    cache[x]
  end
end

slow_square = ->(x) do
  sleep(0.001)   # simulate slow computation
  x * x
end

fast_square = memoize(slow_square)
puts fast_square.call(10)   # computed
puts fast_square.call(10)   # cached — instant
```

### Strategy pattern

```ruby
def sort_by_strategy(items, strategy)
  items.sort_by do |item|
    strategy.call(item)
  end
end

words = ["banana", "fig", "apple", "cherry", "kiwi"]

by_length  = ->(w) { w.length }
by_alpha   = ->(w) { w }
by_reverse = ->(w) { w.chars.reverse.join("") }

puts sort_by_strategy(words, by_length)   # [fig, kiwi, apple, banana, cherry]
puts sort_by_strategy(words, by_alpha)    # [apple, banana, cherry, fig, kiwi]
```

---

## Closures

Lambdas close over variables from the scope where they are created — they can read and remember values that were in scope at definition time.

```ruby
multiplier = 10
scale = ->(x) { x * multiplier }

puts scale.call(5)   # 50

# The lambda captures the variable, not just its value
multiplier = 3
puts scale.call(5)   # 15 — uses the current value of multiplier
```

---

## Recursion with Lambdas

A lambda can call itself by referencing its own variable:

```ruby
factorial = ->(n) do
  return 1 if n <= 1
  n * factorial.call(n - 1)
end

puts factorial.call(10)   # 3628800
```

---

## Quick Reference

```ruby
# Define
fn = ->(x) { x * 2 }
fn = ->(a, b) { a + b }
fn = ->(x, n = 1) { x + n }    # default param
fn = ->(x) do                   # multi-line
  y = x * 2
  y + 1
end

# Call
fn.call(5)
fn.call(3, 4)

# Store
pipeline = [fn1, fn2, fn3]
ops = {double: fn1, triple: fn2}

# Pass
def apply(fn, val)
  fn.call(val)
end

# Use in iterators
[1,2,3].map do |x| fn.call(x) end
```
