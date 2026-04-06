# Loops

Frankie has four loop constructs and a rich set of iterator methods. The loop constructs handle index-based and condition-based repetition; the iterators handle collection traversal.

---

## `while`

Runs as long as the condition is truthy.

```ruby
x = 0
while x < 5
  puts x
  x += 1
end
# 0 1 2 3 4
```

---

## `until`

Runs as long as the condition is **falsy** — the inverse of `while`.

```ruby
x = 0
until x == 5
  puts x
  x += 1
end
# 0 1 2 3 4
```

---

## `do...while`

Runs the body **at least once**, then checks the condition. Borrowed from Fortran.

```ruby
x = 10
do
  puts x
  x += 1
while x < 5
# prints 10 — body ran once even though condition was already false
```

Useful when you need to guarantee at least one execution — user input loops, retry logic:

```ruby
do
  input = input("Enter a positive number: ")
  n = input.to_i
while n <= 0

puts "You entered: #{n}"
```

---

## `for...in`

Iterates over a range or a vector.

```ruby
# Over a range
for i in 1..5
  puts i
end
# 1 2 3 4 5

# Exclusive range
for i in 0...4
  puts i
end
# 0 1 2 3

# Over a vector
for item in ["apple", "banana", "cherry"]
  puts item
end

# Over a hash — gives [key, value] pairs
config = {host: "localhost", port: 5432}
for pair in config
  puts "#{pair[0]}: #{pair[1]}"
end
```

---

## `n.times`

Repeat a block exactly `n` times. The loop variable counts from `0` to `n-1`.

```ruby
3.times do |i|
  puts "iteration #{i}"
end
# iteration 0
# iteration 1
# iteration 2

# Without the variable
5.times do
  print "* "
end
# * * * * *
```

The standalone `times(n)` form is identical:

```ruby
times(3) do |i|
  puts i
end
```

---

## Loop Control

### `next` — skip to next iteration

Equivalent to `continue` in other languages.

```ruby
[1, 2, 3, 4, 5, 6].each do |n|
  next if n % 2 == 0
  puts n
end
# 1 3 5
```

### `break` — exit the loop early

```ruby
[1, 2, 3, 4, 5].each do |n|
  break if n > 3
  puts n
end
# 1 2 3
```

### `break` with a value

A `break` can carry a value out of the loop:

```ruby
result = [1, 2, 3, 4, 5].each do |n|
  break n * 10 if n == 3
end
puts result   # 30
```

### Postfix forms

```ruby
next if condition
break if condition
```

---

## Iterator Methods

For collection traversal, iterator methods with blocks are more idiomatic than `for` loops. They compose, chain, and express intent more clearly.

### `.each` — iterate for side effects

```ruby
[1, 2, 3].each do |x|
  puts x * 2
end

{name: "Alice", age: 30}.each do |k, v|
  puts "#{k}: #{v}"
end
```

### `.each_with_index` — iterate with position

```ruby
["a", "b", "c"].each_with_index do |val, i|
  puts "#{i}: #{val}"
end
# 0: a
# 1: b
# 2: c
```

### `.each_with_object` — iterate with accumulator

```ruby
result = [1, 2, 3, 4, 5].each_with_object({}) do |x, h|
  h[x] = x * x
end
puts result   # {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}
```

### `.each_slice` — iterate in fixed-size chunks

```ruby
[1, 2, 3, 4, 5, 6].each_slice(2) do |slice|
  puts slice
end
# [1, 2]
# [3, 4]
# [5, 6]
```

### `.each_cons` — iterate with sliding window

```ruby
[1, 2, 3, 4, 5].each_cons(3) do |window|
  puts window
end
# [1, 2, 3]
# [2, 3, 4]
# [3, 4, 5]
```

### `.times` — iterate n times (method form)

```ruby
5.times do |i|
  puts i
end
```

---

## `for` vs Iterators

Both work. Iterators are generally preferred for collection traversal because they compose and chain cleanly:

```ruby
# for loop
for n in [1, 2, 3, 4, 5]
  puts n if n > 3
end

# Iterator — composes with select
[1, 2, 3, 4, 5].select do |n|
  n > 3
end.each do |n|
  puts n
end
```

Use `for` when iterating over a range by index. Use iterators when transforming or filtering a collection.

---

## Infinite Loops

A `while true` loop runs forever until `break`:

```ruby
count = 0
while true
  count += 1
  break if count >= 5
end
puts count   # 5
```

---

## Nested Loops

```ruby
[1, 2, 3].each do |x|
  [10, 20].each do |y|
    puts "#{x} × #{y} = #{x * y}"
  end
end
# 1 × 10 = 10
# 1 × 20 = 20
# 2 × 10 = 20
# ...

# Or use .product for cartesian iteration
[1, 2, 3].product([10, 20]).each do |pair|
  puts "#{pair[0]} × #{pair[1]} = #{pair[0] * pair[1]}"
end
```
