# Operators

## Arithmetic

| Operator | Meaning | Example | Result |
|---|---|---|---|
| `+` | Addition | `10 + 3` | `13` |
| `-` | Subtraction | `10 - 3` | `7` |
| `*` | Multiplication | `10 * 3` | `30` |
| `/` | Float division | `10 / 3` | `3.333...` |
| `//` | Integer division | `10 // 3` | `3` |
| `%` | Modulo | `10 % 3` | `1` |
| `**` | Exponentiation | `2 ** 8` | `256` |

`/` always returns a Float. Use `//` (borrowed from Fortran) when you want a whole-number result.

```ruby
puts 10 / 3    # 3.3333333333333335
puts 10 // 3   # 3
puts 10 % 3    # 1
puts 2 ** 10   # 1024
```

`*` and `**` also work on strings and vectors:

```ruby
puts "ha" * 3        # hahaha
puts [0] * 4         # [0, 0, 0, 0]
puts [1, 2] * 3      # [1, 2, 1, 2, 1, 2]
```

---

## Compound Assignment

Shorthand for `x = x op value`:

```ruby
x = 10
x += 3    # 13
x -= 2    # 11
x *= 4    # 44
x /= 2    # 22.0  (float division)
x //= 5   # 4     (integer division)
x **= 2   # 16
x %= 5    # 1
```

Works on vector elements too:

```ruby
v = [10, 20, 30]
v[0] += 5
puts v   # [15, 20, 30]
```

---

## Comparison

Comparison operators return `true` or `false`.

| Operator | Meaning |
|---|---|
| `==` | Equal |
| `!=` | Not equal |
| `<` | Less than |
| `<=` | Less than or equal |
| `>` | Greater than |
| `>=` | Greater than or equal |

```ruby
puts 5 == 5     # true
puts 5 != 3     # true
puts 5 > 3      # true
puts 5 < 3      # false
puts 5 >= 5     # true
puts 5 <= 4     # false

# Integers and Floats compare naturally
puts 3 == 3.0   # true
puts 3 < 3.14   # true

# Strings compare lexicographically
puts "apple" < "banana"   # true
puts "z" > "a"            # true
```

---

## Logical

| Operator | Meaning | Example |
|---|---|---|
| `and` | Both must be true | `x > 0 and x < 10` |
| `or` | At least one must be true | `x < 0 or x > 100` |
| `not` | Negate | `not active` |

```ruby
age    = 25
active = true

if age >= 18 and active
  puts "eligible"
end

if age < 0 or age > 120
  puts "invalid age"
end

if not active
  puts "inactive"
end
```

Short-circuit evaluation applies — `and` stops at the first false, `or` stops at the first true.

---

## Match Operator `=~`

Returns the **position** of the first regex match, or `nil` if there is no match.

```ruby
puts "frank123" =~ "\\d+"    # 5
puts "no digits" =~ "\\d+"   # nil

pos = "hello world" =~ "world"
if pos != nil
  puts "found at position #{pos}"   # found at position 6
end
```

---

## String Concatenation `+`

```ruby
puts "Hello, " + "Frankie!"   # Hello, Frankie!

first = "Frank"
last  = "ie"
puts first + last              # Frankie
```

---

## Hash Merge `|`

Merges two hashes. Right-hand keys win on conflict.

```ruby
defaults = {color: "blue", size: "md", weight: "normal"}
custom   = {color: "red", size: "lg"}

result = defaults | custom
puts result   # {color: red, size: lg, weight: normal}

# Chains naturally
base = {a: 1, b: 2}
mid  = {b: 3, c: 4}
top  = {c: 5, d: 6}
puts base | mid | top   # {a: 1, b: 3, c: 5, d: 6}
```

---

## Pipe Operator `|>`

Passes the result of the left side as the argument to the right side. Borrowed from R.

```ruby
[1, 2, 3, 4, 5] |> sum             # 15
[1, 2, 3, 4, 5] |> mean            # 3.0
[1, 2, 3, 4, 5] |> sum |> puts     # 15

def double(x)
  x * 2
end

10 |> double |> puts   # 20

# Clean data pipelines
data = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
data |> sum |> puts    # 39
data |> mean |> puts   # 3.9
data |> stdev |> puts  # 2.375...
```

---

## Nil-Safe Navigation `&.`

Calls a method only if the receiver is not nil. Returns nil otherwise — no crash.

```ruby
name = nil
puts name&.upcase         # nil
puts name&.upcase&.length # nil — chain short-circuits

user = {name: "Alice"}
puts user["name"]&.upcase          # ALICE
puts user["missing_key"]&.upcase   # nil
```

---

## Range Operators

| Operator | Meaning | Example |
|---|---|---|
| `..` | Inclusive range | `1..5` → 1, 2, 3, 4, 5 |
| `...` | Exclusive range | `1...5` → 1, 2, 3, 4 |

Used in loops, slices, and `vec()`:

```ruby
for i in 1..5
  puts i
end

puts "hello"[1..3]    # ell
puts vec(1..10)       # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
puts vec(0...5)       # [0, 1, 2, 3, 4]
```

---

## Operator Precedence

From highest to lowest:

| Level | Operators |
|---|---|
| Highest | `**` |
| | `*` `/` `//` `%` |
| | `+` `-` |
| | `<` `<=` `>` `>=` |
| | `==` `!=` `=~` |
| | `and` |
| | `or` |
| | `\|>` |
| Lowest | `\|` (hash merge) |

Use parentheses to make intent explicit:

```ruby
puts 2 + 3 * 4      # 14  — * before +
puts (2 + 3) * 4    # 20  — parentheses first
```
