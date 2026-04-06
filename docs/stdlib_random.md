# Random

## Overview

Frankie has a built-in random number library — no imports required. It covers integers, floats, seeding for reproducibility, and collection operations like shuffle and sample. All functions are wrappers around Python's `random` module.

---

## Random Numbers

### `rand_int(a, b)` — Random integer, both ends inclusive

```ruby
puts rand_int(1, 6)      # dice roll: 1, 2, 3, 4, 5, or 6
puts rand_int(0, 100)    # 0 to 100
puts rand_int(-10, 10)   # -10 to 10
```

### `rand_float(a, b)` — Random float in range

Returns a float in `[a, b)` — inclusive on the left, exclusive on the right.

```ruby
puts rand_float(0.0, 1.0)    # e.g. 0.7493...
puts rand_float(-1.0, 1.0)   # e.g. -0.234...
puts rand_float(0.0, 100.0)  # e.g. 42.17...
```

### `rand()` — Random float 0.0 to 1.0

```ruby
puts rand()   # e.g. 0.4217...
```

### `rand(n)` — Random integer 0 to n-1

```ruby
puts rand(10)   # 0 to 9 (exclusive upper bound)
puts rand(2)    # 0 or 1 — coin flip
```

---

## Reproducibility

### `rand_seed(n)` — Fix the random seed

Seeding produces the same sequence every time — essential for tests, simulations, and reproducible results.

```ruby
rand_seed(42)
puts rand_int(1, 100)   # always the same value
puts rand_int(1, 100)   # next value in the same sequence
puts rand_int(1, 100)   # and so on
```

Re-seed to restart the sequence:

```ruby
rand_seed(42)
a = rand_int(1, 1000)

rand_seed(42)
b = rand_int(1, 1000)

assert_eq(a, b, "same seed produces same value")
```

---

## Collections

### `shuffle(v)` — Return a randomly reordered copy

Returns a new vector — does not modify the original.

```ruby
v = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
puts shuffle(v)    # e.g. [4, 9, 1, 7, 3, 10, 5, 2, 8, 6]
puts v             # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] — unchanged
```

### `sample(v, n)` — Random sample without replacement

Returns `n` randomly chosen elements. No element is chosen twice.

```ruby
v = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

puts sample(v, 3)   # e.g. [7, 2, 9]
puts sample(v, 1)   # e.g. [4]
```

`n` defaults to 1 if omitted:

```ruby
puts sample(["red", "green", "blue"])   # e.g. ["green"]
```

---

## Practical Examples

```ruby
# Dice simulator
def roll(sides, count)
  seq(1, count).map do |i|
    rand_int(1, sides)
  end
end

puts roll(6, 5)    # five d6 rolls: e.g. [3, 1, 6, 2, 4]
puts roll(20, 1)   # one d20 roll:  e.g. [17]

# Pick a random element from a vector
def pick(v)
  v[rand_int(0, v.length - 1)]
end

colours = ["red", "green", "blue", "yellow"]
puts pick(colours)   # e.g. "blue"

# Shuffle and deal cards
suits  = ["♠", "♥", "♦", "♣"]
values = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]

deck = suits.flat_map do |s|
  values.map do |v| "#{v}#{s}" end
end

puts deck.length       # 52
hand = sample(shuffle(deck), 5)
puts "Your hand: #{hand.join(", ")}"

# Monte Carlo probability estimate
def estimate_pi(trials)
  rand_seed(42)
  inside = 0
  trials.times do
    x = rand_float(-1.0, 1.0)
    y = rand_float(-1.0, 1.0)
    inside += 1 if x*x + y*y <= 1.0
  end
  round(4.0 * inside / trials, 5)
end

puts estimate_pi(100000)   # ≈ 3.14159

# Random password generator
def random_password(length)
  chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%"
  sample(chars.chars, length).join("")
end

puts random_password(16)   # e.g. "kR3!mZ9xQp#2wL7v"

# Weighted random choice
def weighted_pick(items, weights)
  total  = sum(weights)
  target = rand_float(0.0, total)
  cumulative = 0.0
  items.each_with_index do |item, i|
    cumulative = cumulative + weights[i]
    return item if cumulative >= target
  end
  items.last
end

outcomes = ["win", "lose", "draw"]
weights  = [1.0, 2.0, 0.5]   # lose is twice as likely as win

results = seq(1, 100).map do |i|
  weighted_pick(outcomes, weights)
end

tally = results.tally
puts "Win:  #{tally["win"]}"
puts "Lose: #{tally["lose"]}"
puts "Draw: #{tally["draw"]}"
```

---

## Quick Reference

| Function | Description |
|---|---|
| `rand_int(a, b)` | Random integer between a and b inclusive |
| `rand_float(a, b)` | Random float in [a, b) |
| `rand()` | Random float in [0.0, 1.0) |
| `rand(n)` | Random integer in [0, n) |
| `rand_seed(n)` | Fix seed for reproducibility |
| `shuffle(v)` | Return randomly reordered copy of vector |
| `sample(v, n)` | Return n randomly chosen elements (no repeats) |
