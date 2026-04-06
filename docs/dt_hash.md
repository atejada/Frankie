# Hash

## What is a Hash?

A Hash is an ordered collection of key-value pairs. Keys map to values — you look up a value by its key. Hashes are Frankie's dictionary type, modelled after Python's `dict` but with Ruby's `do...end` iteration syntax.

```ruby
person  = {name: "Alice", age: 30, active: true}
config  = {host: "localhost", port: 5432, db: "app"}
empty   = {}
```

Hashes are **mutable** — you can add, change, and remove keys after creation.

---

## Creating Hashes

### Symbol Keys (most common)

```ruby
user = {name: "Alice", age: 30}
```

Symbol keys are written without quotes — `name:` is the key, `"Alice"` is the value.

### String Keys

When keys come from external data (JSON, user input, database results), they are string keys:

```ruby
row = {"name" => "Alice", "age" => 30}
```

In practice, both forms work interchangeably for access — Frankie normalises keys internally.

### Nested Hashes

```ruby
config = {
  database: {
    host: "localhost",
    port: 5432,
    credentials: {user: "admin", pass: "secret"}
  },
  cache: {ttl: 300}
}
```

---

## Accessing Values

```ruby
h = {name: "Alice", age: 30}

puts h["name"]   # Alice
puts h["age"]    # 30

# Missing key returns nil — no crash
puts h["missing"]   # nil
```

### Safe Nested Access with `.dig`

```ruby
config = {database: {host: "localhost", port: 5432}}

puts config.dig("database", "host")     # localhost
puts config.dig("database", "port")     # 5432
puts config.dig("database", "missing")  # nil  — no crash
puts config.dig("nope", "also_nope")    # nil  — no crash
```

`.dig` works through any combination of hashes and vectors:

```ruby
data = {users: [{name: "Alice", score: 95}, {name: "Bob", score: 87}]}
puts data.dig("users", 0, "name")    # Alice
puts data.dig("users", 1, "score")   # 87
puts data.dig("users", 5, "name")    # nil
```

### Fetch with Default

```ruby
h = {name: "Alice"}

puts h.fetch("name", "unknown")    # Alice
puts h.fetch("age",  0)            # 0  — key missing, returns default
```

---

## Modifying Hashes

```ruby
h = {a: 1, b: 2}

# Add or update a key
h["c"] = 3
h["a"] = 99
puts h   # {a: 99, b: 2, c: 3}

# Remove a key
h.delete("b")
puts h   # {a: 99, c: 3}

# Merge — returns new hash, right wins on conflict
puts {a: 1, b: 2} | {b: 3, c: 4}   # {a: 1, b: 3, c: 4}

# Merge in place
h.merge_bang({d: 5, a: 0})
puts h   # {a: 0, c: 3, d: 5}
```

---

## Inspecting Hashes

```ruby
h = {name: "Alice", age: 30, active: true}

puts h.keys         # [name, age, active]
puts h.values       # [Alice, 30, true]
puts h.size         # 3
puts h.has_key?("name")     # true
puts h.has_key?("missing")  # false
```

---

## Iterating

### `.each` — key and value

```ruby
{name: "Alice", age: 30}.each do |k, v|
  puts "#{k}: #{v}"
end
# name: Alice
# age: 30
```

### `.each_pair` — identical to `.each`

```ruby
config.each_pair do |key, val|
  puts "#{key} = #{val}"
end
```

### `.map` — transform to a vector

`.map` on a hash yields `[key, value]` pairs as a vector of vectors:

```ruby
pairs = {a: 1, b: 2, c: 3}.map do |k, v|
  "#{k}=#{v}"
end
puts pairs   # ["a=1", "b=2", "c=3"]
```

### `.map_hash` — transform to a new hash

```ruby
prices = {apple: 1.20, banana: 0.50, cherry: 3.00}

doubled = prices.map_hash do |k, v|
  [k, v * 2]
end
puts doubled   # {apple: 2.4, banana: 1.0, cherry: 6.0}

# Upcase all keys
upper = {a: 1, b: 2}.map_hash do |k, v|
  [k.to_s.upcase, v]
end
puts upper   # {"A": 1, "B": 2}
```

### `.select` / `.reject` — filter pairs

```ruby
scores = {alice: 95, bob: 72, carol: 88, dave: 61}

passing = scores.select do |k, v|
  v >= 80
end
puts passing   # {alice: 95, carol: 88}

failing = scores.reject do |k, v|
  v >= 80
end
puts failing   # {bob: 72, dave: 61}
```

---

## Converting

```ruby
h = {x: 1, y: 2, z: 3}

# To a vector of [key, value] pairs
puts h.to_a   # [["x", 1], ["y", 2], ["z", 3]]

# Build a hash from a vector using each_with_object
squares = [1,2,3,4,5].each_with_object({}) do |n, h|
  h[n] = n * n
end
puts squares   # {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}
```

---

## The `|` Merge Operator

Merges two hashes. Right-hand keys win on conflict. Chains naturally.

```ruby
defaults = {color: "blue", size: "md", weight: "normal"}
custom   = {color: "red", size: "lg"}

result = defaults | custom
puts result   # {color: red, size: lg, weight: normal}

# Layered config
base = {debug: false, log: "info", timeout: 30}
env  = {log: "debug"}
local = {timeout: 5}

config = base | env | local
puts config   # {debug: false, log: debug, timeout: 5}
```

---

## Nested Access Patterns

```ruby
# Safe navigation with &.
h = {user: {name: "Alice"}}
puts h["user"]&.[]("name")   # Alice — awkward

# Better: use .dig
puts h.dig("user", "name")   # Alice — clean

# Deep default pattern
def get_config(h, *keys)
  result = h.dig(*keys)
  if result == nil then "default" else result end
end
puts get_config(h, "user", "name")   # Alice
puts get_config(h, "user", "age")    # default
```

---

## Common Patterns

```ruby
# Frequency count
words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
freq = words.each_with_object({}) do |w, h|
  cur = h[w]
  h[w] = (if cur == nil then 0 else cur end) + 1
end
puts freq   # {apple: 3, banana: 2, cherry: 1}

# Index by field
people = [
  {name: "Alice", id: 1},
  {name: "Bob",   id: 2},
  {name: "Carol", id: 3}
]
by_id = people.each_with_object({}) do |person, h|
  h[person["id"]] = person["name"]
end
puts by_id[2]   # Bob

# Invert a hash
original = {a: 1, b: 2, c: 3}
inverted = original.map_hash do |k, v|
  [v, k.to_s]
end
puts inverted   # {1: "a", 2: "b", 3: "c"}
```

---

## Quick Reference

| Category | Method / Operation |
|---|---|
| Access | `h[key]` `.dig(k1, k2, ...)` `.fetch(key, default)` |
| Inspect | `.keys` `.values` `.size` `.has_key?(k)` |
| Mutate | `h[key]=` `.delete(key)` `.merge_bang(other)` |
| Merge | `h1 \| h2` `.merge(other)` |
| Iterate | `.each do \|k,v\|` `.each_pair do \|k,v\|` |
| Transform | `.map do \|k,v\|` `.map_hash do \|k,v\|` |
| Filter | `.select do \|k,v\|` `.reject do \|k,v\|` |
| Convert | `.to_a` `.keys` `.values` |
