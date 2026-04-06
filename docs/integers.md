# Integers

## What is an Integer?

An Integer is a whole number — positive, negative, or zero — with no decimal point. Integers in Frankie have no fixed size limit; they grow as large as needed without overflow.

```ruby
x = 42
y = -7
z = 0

big = 2 ** 64   # 18446744073709551616 — no overflow
puts big        # 18446744073709551616
```

---

## Integer Literals

Write integers directly. Negative integers use a leading minus sign.

```ruby
count  = 100
offset = -32
zero   = 0
big    = 1000000
```

Frankie does not currently support underscore separators (`1_000_000`) or hexadecimal/binary literals. Use plain decimal.

---

## Arithmetic Operators

| Operator | Meaning | Example | Result |
|---|---|---|---|
| `+` | Addition | `10 + 3` | `13` |
| `-` | Subtraction | `10 - 3` | `7` |
| `*` | Multiplication | `10 * 3` | `30` |
| `/` | Float division | `10 / 3` | `3.333...` |
| `//` | Integer division | `10 // 3` | `3` |
| `%` | Modulo (remainder) | `10 % 3` | `1` |
| `**` | Exponentiation | `2 ** 8` | `256` |

`/` always produces a Float. Use `//` (Fortran-style) when you want a truncated Integer result.

```ruby
puts 10 / 3     # 3.3333333333333335  — Float
puts 10 // 3    # 3                   — Integer
puts 10 % 3     # 1                   — remainder
puts 2 ** 10    # 1024
```

### Integer Division and Modulo with Negatives

`//` truncates toward negative infinity (floor division), consistent with Python:

```ruby
puts 7 // 2     #  3
puts (-7) // 2  # -4  (floors toward -∞, not toward zero)
puts 7 % 2      #  1
puts (-7) % 2   #  1  (result has the sign of the divisor)
```

---

## Compound Assignment

```ruby
x = 10
x += 3    # x = 13
x -= 2    # x = 11
x *= 4    # x = 44
x //= 5   # x = 8   (integer division assign)
x **= 2   # x = 64
x %= 10   # x = 4
puts x    # 4
```

---

## Comparison Operators

Comparisons return a Boolean.

```ruby
puts 5 > 3     # true
puts 5 < 3     # false
puts 5 >= 5    # true
puts 5 <= 4    # false
puts 5 == 5    # true
puts 5 != 3    # true
```

Integers and Floats compare naturally:

```ruby
puts 3 == 3.0    # true
puts 3 < 3.14    # true
```

---

## Conversion

```ruby
# Integer → Float
puts 42.to_f      # 42.0

# Integer → String
puts 42.to_s      # "42"

# Integer → Integer (no-op, but valid in generic code)
puts 42.to_i      # 42

# String → Integer
puts "42".to_i    # 42
puts "-7".to_i    # -7
puts to_int("99") # 99  — standalone function form

# Float → Integer (truncates toward zero)
puts 3.9.to_i     # 3
puts (-3.9).to_i  # -3
```

Non-numeric strings produce a runtime error — there is no silent fallback to zero:

```ruby
puts "hello".to_i   # Runtime error
```

---

## Math Functions

These standalone functions work on both Integer and Float values:

```ruby
puts abs(-42)          # 42   — absolute value
puts sqrt(144)         # 12.0 — square root (always returns Float)
puts floor(3.9)        # 3    — round down
puts ceil(3.1)         # 4    — round up
puts round(3.5)        # 4    — round to nearest
puts round(3.14159, 2) # 3.14 — round to n decimal places

puts min(3, 7)         # 3
puts max(3, 7)         # 7
puts clamp(15, 0, 10)  # 10  — clamp between lo and hi
puts clamp(-5, 0, 10)  # 0
```

---

## The `times` Loop

`n.times do |i|` iterates `n` times, with `i` counting from `0` to `n-1`. This is one of Frankie's most used integer features, borrowed from Ruby.

```ruby
3.times do |i|
  puts "iteration #{i}"
end
# iteration 0
# iteration 1
# iteration 2

# Without the loop variable
5.times do
  print "* "
end
# * * * * *
```

The standalone `times(n) do |i|` form is identical:

```ruby
times(3) do |i|
  puts i
end
```

---

## Sequences

`seq(start, stop, step)` generates a vector of integers (or floats) from `start` to `stop`.

```ruby
puts seq(1, 5)           # [1, 2, 3, 4, 5]
puts seq(0, 10, 2)       # [0, 2, 4, 6, 8, 10]
puts seq(10, 1, -1)      # [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
puts seq(0, 1, 0.25)     # [0.0, 0.25, 0.5, 0.75, 1.0]
```

`vec(range)` builds a vector from a range literal:

```ruby
puts vec(1..10)     # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
puts vec(1...10)    # [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

---

## Randomness

```ruby
# Random integer between a and b inclusive
puts rand_int(1, 6)      # dice roll — e.g. 4
puts rand_int(0, 100)    # 0 to 100

# Repeatable with a seed
rand_seed(42)
puts rand_int(1, 100)    # always the same value for seed 42
```

---

## Integers in Vectors

Vectors of integers support R-style vectorised arithmetic — operations apply element-wise:

```ruby
v = [1, 2, 3, 4, 5]

puts v * 2              # [2, 4, 6, 8, 10]
puts v + [10, 10, 10, 10, 10]   # [11, 12, 13, 14, 15]
puts v ** 2             # [1, 4, 9, 16, 25]

# Statistical functions on integer vectors
puts sum(v)             # 15
puts mean(v)            # 3.0
puts min(v)             # 1
puts max(v)             # 5
puts median(v)          # 3
puts stdev(v)           # 1.5811...
```

---

## Type Checking

```ruby
puts is_integer(42)      # true
puts is_integer(3.14)    # false
puts is_integer("42")    # false
```

---

## Practical Examples

```ruby
# FizzBuzz
seq(1, 20).each do |n|
  if n % 15 == 0
    puts "FizzBuzz"
  elsif n % 3 == 0
    puts "Fizz"
  elsif n % 5 == 0
    puts "Buzz"
  else
    puts n
  end
end

# Factorial
def factorial(n)
  if n <= 1
    1
  else
    n * factorial(n - 1)
  end
end
puts factorial(10)   # 3628800

# Check if a number is prime
def prime?(n)
  return false if n < 2
  i = 2
  while i * i <= n
    return false if n % i == 0
    i += 1
  end
  true
end

primes = seq(1, 50).select do |n| prime?(n) end
puts primes   # [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

# Digit sum
def digit_sum(n)
  n.to_s.chars.map do |c| c.to_i end |> sum
end
puts digit_sum(12345)   # 15

# Power of two?
def power_of_two?(n)
  n > 0 && n % 2 == 0 && (n // 2 == 1 || power_of_two?(n // 2))
end
puts power_of_two?(64)   # true
puts power_of_two?(48)   # false
```

---

## Quick Reference

| Category | Operation | Example | Result |
|---|---|---|---|
| Arithmetic | `+` `-` `*` | `10 + 3` | `13` |
| Float division | `/` | `10 / 3` | `3.333...` |
| Integer division | `//` | `10 // 3` | `3` |
| Modulo | `%` | `10 % 3` | `1` |
| Exponentiation | `**` | `2 ** 8` | `256` |
| Comparison | `==` `!=` `<` `>` `<=` `>=` | `5 > 3` | `true` |
| Compound assign | `+=` `-=` `*=` `//=` `**=` `%=` | `x += 1` | — |
| Convert to Float | `.to_f` | `42.to_f` | `42.0` |
| Convert to String | `.to_s` | `42.to_s` | `"42"` |
| Absolute value | `abs(n)` | `abs(-7)` | `7` |
| Square root | `sqrt(n)` | `sqrt(144)` | `12.0` |
| Rounding | `floor` `ceil` `round` | `floor(3.9)` | `3` |
| Clamp | `clamp(n, lo, hi)` | `clamp(15, 0, 10)` | `10` |
| Loop n times | `n.times do \|i\|` | `3.times do \|i\|` | — |
| Sequence | `seq(start, stop, step)` | `seq(1, 5)` | `[1,2,3,4,5]` |
| Random | `rand_int(a, b)` | `rand_int(1, 6)` | `1`–`6` |
| Type check | `is_integer(x)` | `is_integer(42)` | `true` |
