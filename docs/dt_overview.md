# Data Types — Overview

## What is a Data Type?

Every value in Frankie has a type. The type determines what the value can do — what methods it responds to, how it behaves in arithmetic, and how it prints. You never declare types explicitly; Frankie figures them out from the values you assign.

```ruby
x     = 42          # Integer
y     = 3.14        # Float
name  = "Alice"     # String
flag  = true        # Boolean
empty = nil         # Nil
items = [1, 2, 3]   # Vector
config = {host: "localhost", port: 5432}  # Hash
```

---

## The Type System

Frankie is **dynamically typed**. A variable has no fixed type — it holds whatever was last assigned to it. The same variable can hold an Integer on one line and a String on the next.

```ruby
x = 42        # Integer
x = "hello"   # now a String — perfectly valid
x = [1, 2, 3] # now a Vector
```

Types are checked at **runtime**, not compile time. Passing a String where an Integer is expected raises a clear error when that line runs — not before.

---

## Primitive Types

Primitive types hold a single, indivisible value. They are the atoms of the language.

| Type | Example | Description |
|---|---|---|
| `Integer` | `42`, `-7`, `0` | Whole numbers, no size limit |
| `Float` | `3.14`, `-0.5`, `1.0e6` | IEEE 754 double-precision decimals |
| `String` | `"hello"`, `"Frankie"` | UTF-8 text, double-quoted |
| `Boolean` | `true`, `false` | Logical values |
| `Nil` | `nil` | The absence of a value |

Primitive values behave **immutably** — operations on them return new values rather than changing the original. `"hello".upcase` returns `"HELLO"`; the original `"hello"` is unchanged.

---

## Composite Types

Composite types hold multiple values. They are built from primitives and other composites.

| Type | Example | Description |
|---|---|---|
| `Vector` | `[1, "two", 3.0]` | Ordered, 0-indexed list of any values |
| `Hash` | `{name: "Alice", age: 30}` | Ordered key-value map |
| `Lambda` | `->(x) { x * 2 }` | A storable, callable function |
| `Record` | `Point(x: 3, y: 4)` | A named data object built on a Hash |

Composite values are **mutable** — you can change their contents after creation.

```ruby
v = [1, 2, 3]
v.push(4)     # modifies v in place
v[0] = 99     # index assignment modifies in place
puts v        # [99, 2, 3, 4]
```

---

## Stdlib Object Types

Several stdlib functions return richer objects that behave like composite types but are not part of the core language:

| Type | Created by | Used for |
|---|---|---|
| `DB` | `db_open(path)` | SQLite database connection |
| `DateTime` | `now()`, `today()`, `date_parse()` | Date and time values |
| `File` | `file_open(path, mode)` | File handle for read/write |
| `WebApp` | `web_app()` | HTTP server and routing |
| `HTTPResponse` | `http_get()`, `http_post()` | HTTP response with status, body, headers |

---

## Type Checking

```ruby
puts is_integer(42)       # true
puts is_float(3.14)       # true
puts is_string("hello")   # true
puts is_vector([1, 2])    # true
puts is_nil(nil)          # true
puts is_bool(true)        # true
```

---

## Type Conversion

Frankie does not coerce types silently. Mixing incompatible types in an expression raises a clear error. Convert explicitly when you need to cross type boundaries.

```ruby
# Numeric conversions
puts 42.to_f        # 42.0
puts 3.14.to_i      # 3  (truncates toward zero)
puts 42.to_s        # "42"

# String parsing
puts "42".to_i      # 42
puts "3.14".to_f    # 3.14

# Standalone functions
puts to_int("99")   # 99
puts to_float("1")  # 1.0
puts to_str(42)     # "42"
```

String interpolation converts any value automatically — no `.to_s` needed inside `#{}`:

```ruby
n = 42
puts "The answer is #{n}"          # The answer is 42
puts "Pi is roughly #{3.14159}"    # Pi is roughly 3.14159
```

---

## Truthiness

Only `false` and `nil` are falsy. Everything else — including `0`, `""`, and `[]` — is truthy.

```ruby
if 0   then puts "truthy" end   # prints — 0 is truthy
if ""  then puts "truthy" end   # prints — empty string is truthy
if []  then puts "truthy" end   # prints — empty vector is truthy
if nil then puts "truthy" end   # does NOT print
```

This means nil checks must be explicit:

```ruby
result = find_user(99)

if result == nil    # explicit nil check
  puts "not found"
end

if result.nil?      # method form — identical
  puts "not found"
end
```

---

## Nil Safety

Calling any method on `nil` raises a runtime error. The `&.` operator returns `nil` silently instead of crashing:

```ruby
name = nil
puts name.upcase    # Runtime error — nil has no .upcase
puts name&.upcase   # nil — safe

# Chains short-circuit at the first nil
puts name&.upcase&.reverse&.length   # nil — stops immediately
```

---

## Mutability at a Glance

| Type | Mutable? | Notes |
|---|---|---|
| `Integer` | No | Operations return new values |
| `Float` | No | Operations return new values |
| `String` | No | Methods return new strings |
| `Boolean` | No | Only two values exist |
| `Nil` | No | Only one nil exists |
| `Vector` | **Yes** | `.push`, index assignment mutate in place |
| `Hash` | **Yes** | Key assignment mutates in place |
| `Lambda` | No | Defined once, called many times |
| `Record` | **Yes** | Built on Hash — field assignment mutates in place |

---

## Type Summary

| Type | Kind | Literal | Mutable |
|---|---|---|---|
| `Integer` | Primitive | `42` | No |
| `Float` | Primitive | `3.14` | No |
| `String` | Primitive | `"hello"` | No |
| `Boolean` | Primitive | `true` / `false` | No |
| `Nil` | Primitive | `nil` | — |
| `Vector` | Composite | `[1, 2, 3]` | Yes |
| `Hash` | Composite | `{a: 1}` | Yes |
| `Lambda` | Composite | `->(x) { x * 2 }` | No |
| `Record` | Composite | `record Point(x, y)` | Yes |
