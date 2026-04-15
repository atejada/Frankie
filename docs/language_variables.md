# Variables & Types

## Variables

Variables are created on first assignment. There is no declaration step — no `var`, `let`, or type annotation. Frankie figures out the type from the value.

```ruby
name    = "Alice"
age     = 30
score   = 97.5
active  = true
nothing = nil
```

Variable names are lowercase with underscores. A variable referenced before assignment raises a runtime error.

```ruby
puts mystery   # Runtime error: Undefined variable: mystery
```

### Reassignment

A variable can be reassigned to any type at any time:

```ruby
x = 42
x = "hello"   # now a String — valid
x = [1, 2, 3] # now a Vector — still valid
```

### Multiple Assignment (Destructuring)

Assign several variables at once from a vector:

```ruby
a, b, c = [10, 20, 30]
puts a   # 10
puts b   # 20
puts c   # 30

# Extra variables are set to nil
x, y, z = [1, 2]
puts z   # nil

# Common use: functions that return multiple values
def min_max(v)
  [min(v), max(v)]
end

lo, hi = min_max([3, 1, 4, 1, 5, 9])
puts "#{lo}..#{hi}"   # 1..9
```

### Hash Destructuring *(v1.14)*

Pull hash keys directly into local variables using `{ }` on the left-hand side. Keys must be bareword (symbol) keys — matching the hash literal convention.

```ruby
user = {name: "Alice", age: 30, role: "admin"}

{name, age} = user
puts name   # Alice
puts age    # 30
```

Missing keys evaluate to `nil` — no error is raised:

```ruby
{name, nickname} = {name: "Alice"}
puts name       # Alice
puts nickname   # nil
```

Works anywhere an assignment is valid — inside functions, loops, and route handlers:

```ruby
# Unpack a config hash in a function
def start_server(config)
  {host, port, debug} = config
  puts "Starting on #{host}:#{port} (debug=#{debug})"
end

start_server({host: "localhost", port: 3000, debug: true})

# Unpack database rows in a loop
db.find_all("users").each do |row|
  {name, email, role} = row
  puts "#{name} <#{email}> [#{role}]"
end

# Unpack a request body in a route handler
app.post("/users") do |req|
  {name, email, password} = req.json
  user = create_user(name, email, password)
  json_response({id: user["id"]}, 201)
end
```

---

## Constants

Names written in `UPPER_SNAKE_CASE` are treated as constants. Reassignment prints a warning and the original value is preserved.

```ruby
MAX_RETRIES = 3
PI          = 3.14159
APP_NAME    = "Frankie"

puts MAX_RETRIES   # 3
MAX_RETRIES = 10   # Warning: MAX_RETRIES is a constant
puts MAX_RETRIES   # 3  — unchanged
```

---

## Types

Frankie is **dynamically typed** — every value has a type, but variables do not. The type is determined by the value at the time it is used.

| Type | Example | Description |
|---|---|---|
| `Integer` | `42`, `-7` | Whole numbers, no size limit |
| `Float` | `3.14`, `-0.5` | Decimal numbers |
| `String` | `"hello"` | UTF-8 text |
| `Boolean` | `true`, `false` | Logical values |
| `Nil` | `nil` | Absence of a value |
| `Vector` | `[1, 2, 3]` | Ordered list |
| `Hash` | `{name: "Alice"}` | Key-value map |
| `Lambda` | `->(x) { x * 2 }` | Storable function |
| `Record` | `Point(x: 3, y: 4)` | Named data object |

---

## Type Checking

```ruby
puts is_integer(42)      # true
puts is_float(3.14)      # true
puts is_string("hello")  # true
puts is_vector([1,2,3])  # true
puts is_nil(nil)         # true
puts is_bool(true)       # true
```

---

## Type Conversion

Frankie does not coerce types silently. Convert explicitly:

```ruby
puts 42.to_s       # "42"    — Integer to String
puts 42.to_f       # 42.0   — Integer to Float
puts "42".to_i     # 42     — String to Integer
puts "3.14".to_f   # 3.14   — String to Float
puts 3.9.to_i      # 3      — Float to Integer (truncates)

# Standalone function forms
puts to_int("42")      # 42
puts to_float("3.14")  # 3.14
puts to_str(42)        # "42"
```

Inside `#{}` interpolation, any value is converted to a string automatically — no `.to_s` needed:

```ruby
n = 42
puts "The answer is #{n}"         # The answer is 42
puts "Double is #{n * 2}"         # Double is 84
puts "Type check: #{is_integer(n)}"  # Type check: true
```

---

## Truthiness

Only `false` and `nil` are falsy. Everything else — including `0` and `""` — is truthy:

```ruby
if 0     then puts "truthy" end   # prints
if ""    then puts "truthy" end   # prints
if []    then puts "truthy" end   # prints
if false then puts "truthy" end   # does not print
if nil   then puts "truthy" end   # does not print
```

---

## Nil Safety

Calling a method on `nil` raises a runtime error. The `&.` operator returns `nil` instead of crashing:

```ruby
name = nil
puts name.upcase    # Runtime error
puts name&.upcase   # nil — safe

# Chains short-circuit at the first nil
puts name&.upcase&.reverse   # nil
```

---

## Scope

Frankie has simple lexical scope. Variables defined in the outer scope are readable inside functions and blocks. Variables assigned inside a function are local to that function.

```ruby
x = 10

def show
  puts x   # readable — outer scope is accessible
end
show   # 10

def modify
  x = 99   # local to modify — does not affect outer x
end
modify
puts x     # 10 — unchanged
```
