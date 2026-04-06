# Float, Boolean & Nil

## Float

A Float is a decimal number — any value with a fractional part, or a number produced by float division. Frankie uses IEEE 754 double-precision, the same standard as Python, Ruby, and R.

```ruby
x = 3.14
y = -0.5
z = 1.0      # explicitly Float, not Integer
e = 2.71828
```

### Float Literals

```ruby
3.14       # standard decimal
-0.5       # negative
1.0        # integer value, Float type
1.0e6      # scientific notation — 1000000.0
2.5e-3     # 0.0025
```

### Arithmetic

All standard operators work on Floats. Mixing Integer and Float produces a Float:

```ruby
puts 3.14 + 1.0    # 4.140000000000001 (float precision)
puts 3.14 * 2      # 6.28
puts 10.0 / 3      # 3.3333333333333335
puts 2.0 ** 8      # 256.0

# Integer / Integer always returns Float
puts 10 / 4        # 2.5
puts 10 // 4       # 2  — use // for integer result
```

### Floating-point Precision

Floats cannot represent all decimal values exactly. This is standard IEEE 754 behaviour, not a Frankie quirk:

```ruby
puts 0.1 + 0.2            # 0.30000000000000004
puts round(0.1 + 0.2, 2)  # 0.3  — round when displaying
```

When comparing floats, compare within a tolerance or round first:

```ruby
a = 0.1 + 0.2
b = 0.3
puts a == b                       # false — unsafe
puts abs(a - b) < 0.0001          # true  — safe comparison
puts round(a, 10) == round(b, 10) # true  — round then compare
```

### Math Functions

```ruby
puts abs(-3.14)         # 3.14
puts sqrt(2.0)          # 1.4142135623730951
puts floor(3.7)         # 3
puts ceil(3.2)          # 4
puts round(3.567, 2)    # 3.57
puts round(3.567)       # 4    (rounds to nearest integer)
puts clamp(1.5, 0.0, 1.0)   # 1.0
```

`sqrt` always returns a Float. `floor`, `ceil`, and `round(x)` with no decimal argument return an Integer.

### Conversion

```ruby
puts 3.14.to_i    # 3     — truncates toward zero
puts (-3.9).to_i  # -3    — truncates toward zero (not floor)
puts 3.14.to_s    # "3.14"
puts 3.14.to_f    # 3.14  — no-op, already a Float

puts "3.14".to_f  # 3.14
puts 42.to_f      # 42.0
```

### Type Checking

```ruby
puts is_float(3.14)   # true
puts is_float(3)      # false — Integer, not Float
puts is_float("3.14") # false
```

---

## Boolean

A Boolean is either `true` or `false`. Booleans are produced by comparisons, logical operators, and predicate methods (`.empty?`, `.nil?`, `is_integer()`, etc.).

```ruby
flag    = true
missing = false

puts 5 > 3      # true
puts 5 < 3      # false
puts 5 == 5     # true
puts 5 != 3     # true
```

### Logical Operators

```ruby
puts true and false    # false — both must be true
puts true or false     # true  — at least one must be true
puts not true          # false — negation

# Short-circuit evaluation
# 'and' stops at the first false
# 'or' stops at the first true
puts false and risky()  # false — risky() never called
puts true  or  risky()  # true  — risky() never called
```

### Truthiness

Only `false` and `nil` are falsy. Every other value — including `0`, `""`, and `[]` — is truthy. This matches Ruby's model.

```ruby
if 0     then puts "truthy" end   # prints
if ""    then puts "truthy" end   # prints
if []    then puts "truthy" end   # prints
if false then puts "truthy" end   # does NOT print
if nil   then puts "truthy" end   # does NOT print
```

### Boolean Comparison

```ruby
puts true == true    # true
puts true == false   # false
puts true != false   # true

# Booleans are not numbers — no arithmetic
# puts true + 1   # Runtime error
```

### Type Checking

```ruby
puts is_bool(true)    # true
puts is_bool(false)   # true
puts is_bool(0)       # false
puts is_bool("true")  # false
```

### Common Patterns

```ruby
# Guard clause with boolean
def process(data)
  return nil if data == nil
  return nil if data.empty?
  data.map do |x| x * 2 end
end

# Store result of a condition
valid = age >= 18 and not banned
puts "Access: #{if valid then "granted" else "denied" end}"

# Predicate methods return booleans
puts "".empty?            # true
puts [1, 2].empty?        # false
puts "hello".include?("ell")  # true
puts is_integer(42)       # true
```

---

## Nil

`nil` represents the absence of a value. It is Frankie's equivalent of `null`, `None`, or `undefined` in other languages. There is exactly one `nil` — every `nil` is the same value.

```ruby
missing = nil
puts missing        # nil
puts missing == nil # true
```

### When Nil Appears

```ruby
# Unset hash keys
h = {name: "Alice"}
puts h["age"]        # nil — key doesn't exist

# Out-of-range vector access
v = [1, 2, 3]
puts v[10]           # nil

# Missing function results
def find_user(id)
  return nil if id == 0
  {id: id, name: "User#{id}"}
end
puts find_user(0)    # nil

# Short-circuit of &. chain
puts nil&.upcase     # nil
```

### Checking for Nil

```ruby
x = nil

# Three equivalent ways
puts x == nil        # true
puts x != nil        # false
puts x.nil?          # true — method form
puts is_nil(x)       # true — function form
```

Avoid testing `if not x` to check for nil — it also catches `false`:

```ruby
x = false

if not x             # catches both nil AND false
  puts "this runs"
end

if x == nil          # only catches nil
  puts "this does not run"
end
```

### Nil Safety with `&.`

The safe navigation operator `&.` short-circuits on nil, returning nil instead of crashing:

```ruby
name = nil
puts name.upcase     # Runtime error
puts name&.upcase    # nil — safe

# Chain — stops at the first nil
user = nil
puts user&.name&.upcase&.length   # nil

# Useful when a value might or might not be present
config = {db: {host: "localhost"}}
puts config.dig("db", "host")&.upcase   # LOCALHOST
puts config.dig("db", "port")&.to_s     # nil
```

### Nil in Collections

```ruby
v = [1, nil, 2, nil, 3]
puts v.compact   # [1, 2, 3] — removes all nils

# nil propagates in arithmetic — raises an error
# puts nil + 1   # TypeError

# Nil-safe default pattern
value = get_value() || 0       # note: || is not in Frankie
# Instead use:
raw   = get_value()
value = if raw == nil then 0 else raw end
```

### Conversion

```ruby
puts nil.to_s    # ""   — nil becomes empty string
puts nil.to_a    # []   — nil becomes empty vector (via stdlib)
```

### Type Checking

```ruby
puts is_nil(nil)    # true
puts is_nil(false)  # false — false is not nil
puts is_nil(0)      # false
puts is_nil("")     # false
```
