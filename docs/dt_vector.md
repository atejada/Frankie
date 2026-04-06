# Vector

## What is a Vector?

A Vector is an ordered, 0-indexed list of values. Vectors can hold any mix of types — integers, strings, booleans, other vectors, hashes. They are Frankie's most-used composite type and the foundation of the R-inspired statistical functions.

```ruby
numbers = [1, 2, 3, 4, 5]
mixed   = [42, "hello", true, nil, 3.14]
empty   = []
nested  = [[1, 2], [3, 4], [5, 6]]
```

Vectors are **mutable** — their contents can be changed after creation.

---

## Creating Vectors

```ruby
# Literal
v = [10, 20, 30]

# From a range
v = vec(1..10)      # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
v = vec(0...5)      # [0, 1, 2, 3, 4]

# From seq()
v = seq(0, 10, 2)   # [0, 2, 4, 6, 8, 10]
v = seq(1.0, 2.0, 0.25)  # [1.0, 1.25, 1.5, 1.75, 2.0]

# Repetition
v = [0] * 5         # [0, 0, 0, 0, 0]
v = [1, 2] * 3      # [1, 2, 1, 2, 1, 2]
```

---

## Accessing Elements

Vectors are 0-indexed. Negative indices count from the end.

```ruby
v = [10, 20, 30, 40, 50]

puts v[0]     # 10  — first
puts v[2]     # 30
puts v[-1]    # 50  — last
puts v[-2]    # 40

# Out of range returns nil
puts v[99]    # nil
```

### Slicing

```ruby
v = [10, 20, 30, 40, 50]

puts v[1..3]    # [20, 30, 40]  — inclusive
puts v[1...3]   # [20, 30]      — exclusive
puts v[-3..-1]  # [30, 40, 50]  — last three
puts v[0..1]    # [10, 20]      — first two
```

### Assignment

```ruby
v = [1, 2, 3, 4, 5]
v[0] = 99
puts v   # [99, 2, 3, 4, 5]

v[-1] = 0
puts v   # [99, 2, 3, 4, 0]
```

---

## Basic Operations

```ruby
v = [1, 2, 3, 4, 5]

puts v.length    # 5
puts v.first     # 1
puts v.last      # 5
puts v.empty?    # false
puts [].empty?   # true

puts v.include?(3)   # true
puts v.include?(9)   # false
```

### Adding and Removing Elements

```ruby
v = [1, 2, 3]

v.push(4)        # append — v is now [1, 2, 3, 4]
v.pop()          # remove last — returns 4, v is now [1, 2, 3]

v.delete(2)      # remove by value — v is now [1, 3]
puts v           # [1, 3]
```

---

## R-style Vectorised Arithmetic

Operations on vectors apply element-wise — borrowed from R:

```ruby
v = [1, 2, 3, 4, 5]

puts v * 2              # [2, 4, 6, 8, 10]
puts v + [10, 10, 10, 10, 10]   # [11, 12, 13, 14, 15]
puts v ** 2             # [1, 4, 9, 16, 25]
```

Vectors of different lengths raise a runtime error for arithmetic. For pairing, use `.zip` instead.

---

## Statistical Functions

```ruby
data = [23, 45, 12, 67, 34, 89, 56]

puts sum(data)      # 326
puts mean(data)     # 46.57...
puts median(data)   # 45
puts min(data)      # 12
puts max(data)      # 89
puts stdev(data)    # 24.9...
puts variance(data) # 621.6...
```

Also as methods:

```ruby
puts data.sum    # 326
puts data.min    # 12
puts data.max    # 89
puts data.mean   # 46.57...
```

---

## Sorting and Ordering

```ruby
v = [3, 1, 4, 1, 5, 9, 2, 6]

puts v.sort             # [1, 1, 2, 3, 4, 5, 6, 9]
puts v.reverse          # [6, 2, 9, 5, 1, 4, 1, 3]
puts v.uniq             # [3, 1, 4, 5, 9, 2, 6]  — deduped

# Sort by computed key
words = ["banana", "fig", "apple", "cherry"]
puts words.sort_by do |w| w.length end   # [fig, apple, banana, cherry]
puts words.sort_by do |w| w end          # [apple, banana, cherry, fig]

# Min/max by key
puts words.min_by do |w| w.length end    # fig
puts words.max_by do |w| w.length end    # banana
```

---

## Transformation

```ruby
v = [1, 2, 3, 4, 5]

# map — transform each element
puts v.map do |x| x * x end          # [1, 4, 9, 16, 25]
puts v.map do |x| x.to_s end         # ["1", "2", "3", "4", "5"]

# select / reject — filter
puts v.select do |x| x > 3 end       # [4, 5]
puts v.reject do |x| x > 3 end       # [1, 2, 3]

# reduce — fold into a single value
puts v.reduce(0) do |acc, x| acc + x end   # 15
puts v.reduce(1) do |acc, x| acc * x end   # 120

# flat_map — map then flatten one level
puts [[1,2],[3,4]].flat_map do |sub| sub end       # [1, 2, 3, 4]
puts ["hi","bye"].flat_map do |w| w.chars end       # [h,i,b,y,e]

# map_with_index — element and position together
puts v.map_with_index do |x, i| "#{i}:#{x}" end
# ["0:1", "1:2", "2:3", "3:4", "4:5"]
```

---

## Searching

```ruby
v = [1, 2, 3, 4, 5, 6]

# find — first matching element
puts v.find do |x| x > 4 end       # 5

# any? / all? / none?
puts v.any?  do |x| x > 5 end      # true
puts v.all?  do |x| x > 0 end      # true
puts v.none? do |x| x > 9 end      # true

# count — with a block
puts v.count do |x| x.even? end    # error — .even? not available
puts v.count do |x| x % 2 == 0 end # 3
```

---

## Grouping and Bucketing

```ruby
v = [1, 2, 3, 4, 5, 6]

# tally — count occurrences
puts ["a","b","a","c","b","a"].tally   # {a: 3, b: 2, c: 1}

# group_by — bucket by key
by_parity = v.group_by do |x|
  if x % 2 == 0 then "even" else "odd" end
end
puts by_parity["even"]   # [2, 4, 6]
puts by_parity["odd"]    # [1, 3, 5]

# chunk — fixed-size sub-vectors
puts v.chunk(2)   # [[1,2],[3,4],[5,6]]
```

---

## Iteration with State

```ruby
# each_with_object — shared accumulator
freq = ["a","b","a","c","b","a"].each_with_object({}) do |x, h|
  cur = h[x]
  h[x] = (if cur == nil then 0 else cur end) + 1
end
puts freq   # {a: 3, b: 2, c: 1}

# each_with_index
["x", "y", "z"].each_with_index do |val, i|
  puts "#{i}: #{val}"
end

# each_slice — non-overlapping windows
[1,2,3,4,5,6].each_slice(2) do |s|
  puts s
end
# [1, 2]  [3, 4]  [5, 6]

# each_cons — sliding window
[1,2,3,4,5].each_cons(3) do |w|
  puts w
end
# [1,2,3]  [2,3,4]  [3,4,5]
```

---

## Combining Vectors

```ruby
a = [1, 2, 3]
b = [4, 5, 6]

# zip — pair elements
puts a.zip(b)      # [[1,4],[2,5],[3,6]]

# zip_with — pair and transform
puts a.zip_with(b) do |x, y| x + y end   # [5, 7, 9]

# product — cartesian product
puts [1,2].product([3,4])   # [[1,3],[1,4],[2,3],[2,4]]

# flatten — deep flatten
puts [[1,[2]],[3,[4,5]]].flatten     # [1, 2, 3, 4, 5]
puts [[1,[2]],[3,[4,5]]].flatten(1)  # [1, [2], 3, [4, 5]]

# compact — remove nils
puts [1, nil, 2, nil, 3].compact   # [1, 2, 3]

# unzip — split pairs back into two vectors
puts unzip([[1,"a"],[2,"b"],[3,"c"]])   # [[1,2,3],["a","b","c"]]
```

---

## The Pipe Operator

Vectors work naturally with `|>`:

```ruby
data = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]

data |> sum  |> puts    # 39
data |> mean |> puts    # 3.9
data |> min  |> puts    # 1
data |> max  |> puts    # 9
```

---

## Quick Reference

| Category | Method / Function |
|---|---|
| Access | `[i]` `[a..b]` `.first` `.last` `.take(n)` `.drop(n)` `.dig(...)` |
| Inspect | `.length` `.empty?` `.include?(x)` `.count` `.tally` |
| Mutate | `.push(x)` `.pop()` `.delete(x)` `[i]=` |
| Transform | `.map` `.flat_map` `.map_with_index` `.reverse` `.flatten` `.compact` |
| Filter | `.select` `.reject` `.find` `.uniq` |
| Aggregate | `.reduce` `.each_with_object` `.sum` `.min` `.max` `.mean` |
| Test | `.any?` `.all?` `.none?` `.count do` |
| Sort | `.sort` `.sort_by` `.min_by` `.max_by` `.reverse` |
| Group | `.group_by` `.chunk` `.each_slice` `.each_cons` |
| Combine | `.zip` `.zip_with` `.product` `.flatten` `unzip()` |
| Stats | `sum()` `mean()` `median()` `stdev()` `variance()` `min()` `max()` |
| Create | `vec(range)` `seq(start, stop, step)` `[x] * n` |
