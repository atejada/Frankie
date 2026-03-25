# Collections

## Vectors

Vectors are ordered, 0-indexed lists with built-in R-style math.

```ruby
v = [10, 20, 30, 40, 50]

# Indexing (negatives count from end)
v[0]     # 10
v[-1]    # 50

# Range slicing
v[1..3]     # [20, 30, 40]
v[-2..-1]   # [40, 50]
v[0...3]    # [10, 20, 30]

# Assignment
v[0] = 99

# From range
w = vec(1..10)    # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Vectorized arithmetic (R-style)
v * 2                    # [20, 40, 60, 80, 100]
v + [1, 2, 3, 4, 5]     # [11, 22, 33, 44, 55]
```

### Vector Methods

| Method | Description |
|---|---|
| `.length` | Number of elements |
| `.first` | First element |
| `.last` | Last element |
| `.reverse` | Reversed copy |
| `.sort` | Sorted copy |
| `.uniq` | Deduplicated copy |
| `.flatten` | Full deep flatten *(changed in v1.10 — was one-level in v1.9)* |
| `.flatten(n)` | Flatten exactly n levels; `.flatten(1)` = old v1.9 behaviour *(v1.10)* |
| `.map_with_index { \|x, i\| }` | Map with element index available *(v1.10)* |
| `.compact` | Remove nil values |
| `.push(x)` | Append element |
| `.pop()` | Remove and return last element |
| `.join(sep)` | Join as string |
| `.sum` | Sum of all elements |
| `.min` | Minimum element |
| `.max` | Maximum element |
| `.mean` | Arithmetic mean |
| `.take(n)` | First n elements |
| `.drop(n)` | All but first n elements |
| `.tally` | Count occurrences → Hash |
| `.chunk(n)` | Split into sub-vectors of size n |
| `.zip(other)` | Zip two vectors together |
| `.flatten` | Flatten one level |
| `.empty?` | True if empty |
| `.group_by { \|x\| key }` | Bucket into hash of arrays by key *(v1.8)* |
| `.each_slice(n)` | Iterate in non-overlapping chunks of n *(v1.8)* |
| `.each_cons(n)` | Iterate with sliding window of n *(v1.8)* |

### Iteration

```ruby
# .each
[1, 2, 3].each do |x|
  puts x
end

# .each_with_index
["a", "b", "c"].each_with_index do |val, idx|
  puts "#{idx}: #{val}"
end

# .map — transform every element
squares = [1, 2, 3, 4, 5].map do |x|
  x ** 2
end
# [1, 4, 9, 16, 25]

# .select — keep matching elements
evens = [1,2,3,4,5,6].select do |x|
  x % 2 == 0
end
# [2, 4, 6]

# .reject — drop matching elements
odds = [1,2,3,4,5,6].reject do |x|
  x % 2 == 0
end
# [1, 3, 5]

# .find / .detect — first matching element (or nil)
first_big = [3, 7, 2, 11, 4].find do |x|
  x > 8
end
# 11

first_even = [3, 7, 2, 11, 4].detect do |x|
  x % 2 == 0
end
# 2   (.detect is an alias for .find)

no_match = [1, 2, 3].find do |x|
  x > 100
end
# nil

# .reduce / .inject — fold to a single value
total = [1,2,3,4,5].reduce(0) do |acc, x|
  acc + x
end
# 15

# .each_with_object — iterate with a shared accumulator
result = [1,2,3].each_with_object([]) do |x, arr|
  arr.push(x * 2)
end
# [2, 4, 6]

# .flat_map — map then flatten
[1, 2, 3].flat_map do |x|
  [x, x * 10]
end
# [1, 10, 2, 20, 3, 30]

# .any? — true if any element matches
[1,2,3].any? do |x|
  x > 2
end
# true

# .all? — true if all elements match
[2,4,6].all? do |x|
  x % 2 == 0
end
# true

# .none? — true if no elements match
[1,2,3].none? do |x|
  x > 5
end
# true

# .count with block
[1,2,3,4,5].count do |x|
  x > 3
end
# 2

# N.times
5.times do |i|
  puts i
end
```

---

## Hashes

```ruby
person = {name: "Alice", age: 30}    # symbol keys
config = {0: "zero", 1: "one"}       # integer keys
```

### Access

```ruby
person[:name]           # "Alice"  (nil-safe — missing keys → nil)
person[:missing]        # nil
person[:age] = 31       # write / add
```

### Hash Methods

| Method | Description |
|---|---|
| `.keys` | Vector of all keys |
| `.values` | Vector of all values |
| `.size` / `.count` | Number of pairs |
| `.has_key?(k)` | True if key exists |
| `.fetch(k, default)` | Get with default |
| `.delete(k)` | Remove key |
| `.merge(other)` | Return merged hash (method form) |
| `h1 \| h2` | Merge operator — right wins on conflict *(v1.8)* |
| `.dig(k1, k2, ...)` | Safe nested access — returns nil instead of crashing *(v1.9)* |
| `.to_a` | Convert to vector of pairs |

### Hash Iteration

```ruby
# Two-param block → key/value
person.each do |key, val|
  puts "#{key}: #{val}"
end

# .each_pair (identical to .each)
person.each_pair do |key, val|
  puts "#{key} = #{val}"
end
```

### Nested Hashes

```ruby
config = {
  db:  {host: "localhost", port: 5432},
  app: {host: "0.0.0.0",  port: 3000}
}

puts config[:db][:host]     # localhost
puts config[:app][:port]    # 3000
```

### Building Dynamically

```ruby
counts = {}
words = ["the", "quick", "the", "fox"]
words.each do |w|
  if counts.has_key?(w)
    counts[w] = counts[w] + 1
  else
    counts[w] = 1
  end
end
puts counts    # {the: 2, quick: 1, fox: 1}

# Or using each_with_object
counts = words.each_with_object({}) do |w, h|
  h[w] = h.fetch(w, 0) + 1
end
```

### Hash of Vectors

```ruby
scores = {alice: [90,85,92], bob: [78,80,88]}
scores.each do |name, s|
  puts "#{name}: avg=#{mean(s)}"
end
```
