# Data Types

## What is a Data Type?

Every value in Frankie has a type. The type determines what the value can do — what methods it responds to, how it behaves in arithmetic, and how it prints. You never declare types explicitly; Frankie figures them out from the values you assign.

```ruby
x = 42          # Integer
y = 3.14        # Float
name = "Alice"  # String
flag = true     # Boolean
items = [1,2,3] # Vector
empty = nil     # Nil
```

---

## Primitive vs Composite Types

Frankie types fall into two groups.

**Primitive types** hold a single value. They are the atoms of the language — everything else is built from them.

| Type | Example | Description |
|---|---|---|
| `Integer` | `42`, `-7`, `0` | Whole numbers |
| `Float` | `3.14`, `-0.5`, `1.0` | Decimal numbers |
| `String` | `"hello"` | Text — UTF-8, double-quoted |
| `Boolean` | `true`, `false` | Logical values |
| `Nil` | `nil` | Absence of a value |

**Composite types** hold multiple values or represent a complex object. They are built from primitives and other composites.

| Type | Example | Description |
|---|---|---|
| `Vector` | `[1, "two", 3.0]` | Ordered list of any values |
| `Hash` | `{name: "Alice", age: 30}` | Key-value map |
| `Lambda` | `->( x) { x * 2 }` | A storable, callable function |
| `Record` | `Point(x: 3, y: 4)` | A named data object built on a Hash |

There are also **stdlib object types** — `DB`, `DateTime`, `WebApp`, `HTTPResponse`, `File` — returned by specific stdlib functions. They behave like composite types but are not part of the core language.

---

## How Variables Store Values

Frankie is **dynamically typed** — a variable has no fixed type. It holds whatever value was last assigned to it, and that value's type can change between assignments.

```ruby
x = 42        # x is an Integer
x = "hello"   # x is now a String — perfectly valid
x = [1, 2, 3] # x is now a Vector
```

Variables are created on first assignment. There is no declaration step — no `var`, `let`, or `int x`. If you reference a variable before assigning it, you get a runtime error.

```ruby
puts mystery   # Runtime error: Undefined variable: mystery
```

---

## Type Conversion

Frankie does not coerce types silently. Adding an Integer to a String is an error, not a guess. Convert explicitly when you need to cross type boundaries.

```ruby
# Explicit conversion
puts 42.to_s        # "42"    — Integer to String
puts "42".to_i      # 42     — String to Integer
puts "3.14".to_f    # 3.14   — String to Float
puts 3.14.to_i      # 3      — Float to Integer (truncates)
puts 42.to_f        # 42.0   — Integer to Float

# Type checking
puts is_integer(42)       # true
puts is_float(3.14)       # true
puts is_string("hello")   # true
puts is_vector([1, 2])    # true
puts is_nil(nil)          # true
puts is_bool(false)       # true
```

String interpolation converts any value automatically inside `#{}`:

```ruby
n = 42
puts "The answer is #{n}"   # "42" — no .to_s needed here
```

---

## Truthiness and Nil

Frankie has **strict boolean semantics**. Only `false` and `nil` are falsy. Everything else — including `0`, `""`, and `[]` — is truthy. This matches Ruby's model and avoids the silent bugs common in languages that treat `0` as false.

```ruby
if 0
  puts "0 is truthy in Frankie"   # this prints
end

if ""
  puts "empty string is truthy"   # this prints too
end

if nil
  puts "nil is falsy"   # this does NOT print
end

if false
  puts "false is falsy"   # this does NOT print
end
```

Check for nil explicitly with `.nil?` or `== nil`:

```ruby
x = nil

if x == nil
  puts "x has no value"
end

if x.nil?
  puts "same thing, method form"
end
```

---

## Mutability

In Frankie, **composite types are mutable** — you can change their contents after creation. **Primitive types are effectively immutable** — string methods like `.upcase` return new strings rather than modifying the original.

```ruby
# Strings — immutable style (methods return new values)
s = "hello"
puts s.upcase   # "HELLO"
puts s          # "hello" — unchanged

# Vectors — mutable
v = [1, 2, 3]
v.push(4)
puts v          # [1, 2, 3, 4] — modified in place

v[0] = 99
puts v          # [99, 2, 3, 4] — index assignment modifies in place

# Hashes — mutable
h = {a: 1, b: 2}
h["c"] = 3
puts h          # {a: 1, b: 2, c: 3}
```

---

## Nil Safety

Calling a method on `nil` raises a runtime error. Use the safe navigation operator `&.` to short-circuit instead:

```ruby
name = nil

puts name.upcase    # Runtime error — nil has no .upcase
puts name&.upcase   # nil — safe, no crash
```

Chains short-circuit at the first nil:

```ruby
user = nil
puts user&.address&.city   # nil — stops at user
```

---

## Type Summary

| Type | Primitive / Composite | Mutable | Literal syntax |
|---|---|---|---|
| `Integer` | Primitive | No | `42`, `-7` |
| `Float` | Primitive | No | `3.14`, `1.0` |
| `String` | Primitive | No | `"hello"` |
| `Boolean` | Primitive | No | `true`, `false` |
| `Nil` | Primitive | — | `nil` |
| `Vector` | Composite | Yes | `[1, 2, 3]` |
| `Hash` | Composite | Yes | `{a: 1}` |
| `Lambda` | Composite | No | `->(x) { x * 2 }` |
| `Record` | Composite | Yes | `record Point(x, y)` |
