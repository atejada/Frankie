# Frankie v1.8 — New Feature Reference

## Overview

v1.8 adds four features focused on functional programming patterns and
data-processing ergonomics:

| Feature | Syntax / Method | Summary |
|---|---|---|
| **Lambdas** | `->(x) { x * 2 }` | Store and pass functions as first-class values |
| **Hash merge operator** | `h1 \| h2` | Merge two hashes with a clean operator |
| **group_by** | `.group_by do \|x\| ... end` | Bucket a vector into a hash of arrays |
| **each_slice** | `.each_slice(n) do \|s\| ... end` | Iterate in fixed-size non-overlapping chunks |
| **each_cons** | `.each_cons(n) do \|w\| ... end` | Iterate with a sliding window of size n |

---

## Lambdas — Anonymous Functions

Frankie v1.8 lets you store and pass functions as ordinary values.
A lambda is created with the `->` arrow operator.

### Syntax

```ruby
# Single-expression body (brace block)
fn = ->(params) { expression }

# Multi-statement body (do...end block)
fn = ->(params) do
  statements
  return value
end

# Call with .call(...)
fn.call(arg1, arg2)
```

### Examples

```ruby
# Store a function in a variable
double = ->(x) { x * 2 }
puts double.call(5)      # 10
puts double.call(21)     # 42

# Multiple parameters
add = ->(a, b) { a + b }
puts add.call(3, 7)      # 10

# Default parameters work the same as in def
greet = ->(name, prefix = "Hello") { "#{prefix}, #{name}!" }
puts greet.call("Alice")           # Hello, Alice!
puts greet.call("Bob", "Hi")       # Hi, Bob!

# Multi-statement lambda
clamp = ->(n, lo, hi) do
  if n < lo
    return lo
  end
  if n > hi
    return hi
  end
  return n
end
puts clamp.call(3, 1, 10)    # 3
puts clamp.call(-5, 0, 100)  # 0
puts clamp.call(200, 0, 100) # 100
```

### Higher-Order Functions

Pass lambdas to user-defined functions to parameterise behaviour:

```ruby
def apply(fn, value)
  return fn.call(value)
end

def apply_all(fns, value)
  result = value
  fns.each do |fn|
    result = fn.call(result)
  end
  return result
end

square  = ->(x) { x * x }
inc     = ->(x) { x + 1 }
to_str  = ->(x) { "result=#{x}" }

puts apply(square, 5)                        # 25
puts apply_all([inc, square, to_str], 4)     # result=25
```

### Lambdas in Vectors and Hashes

```ruby
# Vector of lambdas — dispatch table
ops = {
  double: ->(x) { x * 2 },
  square: ->(x) { x * x },
  negate: ->(x) { -x }
}

puts ops["double"].call(7)   # 14
puts ops["square"].call(4)   # 16
puts ops["negate"].call(9)   # -9
```

### Using Lambdas with .map, .select, .each

Lambdas are first-class values but Frankie blocks are still the most
natural way to use iterators. The two styles compose easily:

```ruby
normalize = ->(s) { s.downcase.strip }

names = ["  Alice ", "BOB", "  Carol"]
clean = names.map do |n| normalize.call(n) end
puts clean    # [alice, bob, carol]
```

---

## Hash Merge Operator `|`

The `|` operator merges two hashes into a new hash. Right-hand keys
win when both hashes share the same key. Neither original hash is
modified.

### Syntax

```ruby
merged = hash1 | hash2
```

### Examples

```ruby
defaults = {color: "blue", size: "medium", weight: 1}
overrides = {color: "red", weight: 5}

merged = defaults | overrides
puts merged["color"]   # red    ← right wins
puts merged["size"]    # medium ← left preserved
puts merged["weight"]  # 5      ← right wins

# Chain merges
base  = {a: 1, b: 2}
extra = {b: 99, c: 3}
more  = {c: 100, d: 4}
puts base | extra | more   # {a: 1, b: 99, c: 100, d: 4}

# Originals are untouched
puts base["b"]    # 2  (not 99)
```

### Common Patterns

```ruby
# Config layering
app_defaults = {timeout: 30, retries: 3, debug: false}
env_config   = {timeout: 60}
user_config  = {debug: true}

config = app_defaults | env_config | user_config
puts config["timeout"]   # 60
puts config["retries"]   # 3
puts config["debug"]     # true
```

The `|` operator complements the existing `.merge(other)` method.
Use `|` when writing expressions; use `.merge` when chaining method calls.

---

## `group_by`

Groups the elements of a vector into a hash of arrays, using the
block's return value as the key. Elements with the same key end up
in the same array, in their original order.

### Syntax

```ruby
hash = vector.group_by do |element|
  key_expression
end
```

The block must return a value for every element. The returned hash maps
each distinct key to the array of elements that produced it.

### Examples

```ruby
# Group by first character
words = ["ant", "ape", "bear", "bee", "cat"]
by_letter = words.group_by do |w| w[0] end
puts by_letter["a"]   # [ant, ape]
puts by_letter["b"]   # [bear, bee]

# Group by computed property
people = [
  {name: "Alice", dept: "Engineering"},
  {name: "Bob",   dept: "Design"},
  {name: "Carol", dept: "Engineering"},
  {name: "Dave",  dept: "Design"}
]
by_dept = people.group_by do |p| p["dept"] end
puts by_dept["Engineering"].length   # 2

# Group numbers by remainder
nums = [1, 2, 3, 4, 5, 6, 7, 8, 9]
by_mod3 = nums.group_by do |n| n % 3 end
puts by_mod3["0"]   # [3, 6, 9]
puts by_mod3["1"]   # [1, 4, 7]
puts by_mod3["2"]   # [2, 5, 8]
```

### Pairing with `.tally` and `.sort_by`

`group_by` works naturally with the other collection methods:

```ruby
logs = ["INFO start", "ERROR disk", "INFO request", "ERROR timeout", "WARN mem"]

groups  = logs.group_by do |line| line.split(" ")[0] end
counts  = groups.keys.map do |k| {level: k, n: groups[k].length} end
sorted  = counts.sort_by do |row| row["n"] end

sorted.each do |row|
  puts "#{row["level"]}: #{row["n"]}"
end
```

---

## `each_slice`

Iterates over the collection in non-overlapping chunks of exactly `n`
elements. The last chunk may be smaller if the collection length is not
evenly divisible by `n`.

### Syntax

```ruby
# With block — iterate chunks
vector.each_slice(n) do |slice|
  # slice is a vector of up to n elements
end

# Without block — returns vector of slices
slices = vector.each_slice(n)
```

### Examples

```ruby
# Paginate results
rows = [1, 2, 3, 4, 5, 6, 7]
rows.each_slice(3) do |page|
  puts page     # [1,2,3]  [4,5,6]  [7]
end

# Batch processing
ids = [101, 102, 103, 104, 105]
ids.each_slice(2) do |batch|
  puts "Sending: #{batch}"
end

# As a value — returns nested vector
puts [1,2,3,4,5].each_slice(2)   # [[1,2],[3,4],[5]]

# Sum pairs
total_pairs = []
[10, 20, 30, 40].each_slice(2) do |pair|
  total_pairs.push(pair[0] + pair[1])
end
puts total_pairs   # [30, 70]
```

---

## `each_cons`

Iterates over all consecutive windows of exactly `n` elements, advancing
one position at a time (sliding window). Returns nothing if `n` is
greater than the collection length.

### Syntax

```ruby
# With block — iterate windows
vector.each_cons(n) do |window|
  # window is a vector of exactly n elements
end

# Without block — returns vector of windows
windows = vector.each_cons(n)
```

### Examples

```ruby
# Consecutive pairs (deltas)
prices = [100, 105, 103, 108, 112]
prices.each_cons(2) do |w|
  puts w[1] - w[0]    # 5  -2  5  4
end

# 3-element sliding window
temps = [20, 22, 19, 25, 23, 28]
temps.each_cons(3) do |w|
  puts mean(w)    # 3-day rolling average
end

# As a value — returns nested vector
puts [1,2,3,4].each_cons(2)   # [[1,2],[2,3],[3,4]]

# Detect rising streaks
readings = [3, 5, 5, 7, 6, 8, 9]
readings.each_cons(2) do |w|
  if w[1] > w[0]
    puts "Rising: #{w[0]} → #{w[1]}"
  end
end
```

### `each_slice` vs `each_cons`

| | `each_slice(n)` | `each_cons(n)` |
|---|---|---|
| Window overlap | None — chunks are disjoint | Full — windows slide by 1 |
| Number of windows | `ceil(length / n)` | `length - n + 1` |
| Use case | Batching, pagination | Rolling averages, delta detection |

---

## Changes to `_block_to_lambda` (internal)

v1.8 also fixes a latent issue where blocks whose body contained
control-flow statements (`if`, `case`, `unless`) as the final expression
would crash the code generator. All iterators that use `_block_to_lambda`
internally — `select`, `reject`, `sort_by`, `min_by`, `max_by`,
`sum_by`, `find`, `flat_map`, `group_by` — now correctly handle
if/case/unless as value-producing expressions inside their blocks.
