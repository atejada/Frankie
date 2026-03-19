# v1.4–v1.7 Features Reference

This document covers all features added since the initial release, grouped by area.

---

## Default Parameter Values (v1.3)

```ruby
def greet(name, msg="Hello", punct="!")
  puts "#{msg}, #{name}#{punct}"
end

greet("Alice")             # Hello, Alice!
greet("Bob", "Hi")         # Hi, Bob!
greet("Carol", "Hey", ".") # Hey, Carol.
```

Required parameters must come before optional ones.

---

## Loop Control — `next` and `break` (v1.5)

```ruby
# next — skip to the next iteration
[1,2,3,4,5].each do |n|
  next if n % 2 == 0
  puts n              # 1 3 5
end

# break — exit the loop early
[1,2,3,4,5].each do |n|
  break if n > 3
  puts n              # 1 2 3
end

# break with value — exit and capture a result
found = [1,2,3,4,5].each do |n|
  break n * 10 if n == 3
end
puts found    # 30

# postfix forms work too
next if x > 5
break if done
```

---

## Constants (v1.5)

`UPPER_SNAKE_CASE` identifiers are constants. Reassignment warns and preserves the original.

```ruby
MAX_RETRIES = 5
PI          = 3.14159
BASE_URL    = "https://api.example.com"

puts MAX_RETRIES    # 5
MAX_RETRIES = 99    # Warning: MAX_RETRIES is a constant
puts MAX_RETRIES    # 5  (unchanged)
```

---

## Randomness (v1.5)

| Function | Description |
|---|---|
| `random()` | Random Float in [0.0, 1.0) |
| `rand(n)` | Random Integer in [0, n) |
| `rand_int(a, b)` | Random Integer in [a, b] (both inclusive) |
| `rand_float(a, b)` | Random Float in [a, b) |
| `shuffle(vec)` | Return a shuffled copy of a vector |
| `sample(vec, n)` | Return n randomly chosen elements (no repeats) |
| `rand_seed(n)` | Seed the RNG for reproducible results |

```ruby
rand_seed(42)
puts rand_int(1, 6)           # dice roll
puts shuffle([1,2,3,4,5])     # random order
puts sample(["a","b","c"], 2) # 2 random picks
```

---

## Compound Assignment (v1.6)

```ruby
x += 5     # x = x + 5
x -= 3     # x = x - 3
x *= 2     # x = x * 2
x /= 4     # x = x / 4   (float division)
x //= 3    # x = x // 3  (integer division, Fortran)
x **= 2    # x = x ** 2  (exponentiation, Fortran)
x %= 7     # x = x % 7

# Also works on vector elements
v = [10, 20, 30]
v[0] += 5     # [15, 20, 30]
v[2] *= 3     # [15, 20, 90]
```

---

## Typed Rescue (v1.6)

Multiple `rescue` clauses matched in order — the first matching type wins.

```ruby
begin
  x = 10 // 0
rescue ZeroDivisionError e
  puts "division by zero: #{e}"
rescue TypeError e
  puts "wrong type: #{e}"
rescue RuntimeError e
  puts "runtime: #{e}"
rescue e
  puts "other: #{e}"
ensure
  puts "always runs"
end
```

Supported types: `RuntimeError`, `TypeError`, `ValueError`, `ZeroDivisionError`,
`IndexError`, `KeyError`, `IOError`, `FileNotFoundError`, `OverflowError`,
`NameError`, `AttributeError`, `Exception` / `Error`.

---

## `.find` / `.detect` (v1.6)

Return the first element where the block is true, or `nil`.

```ruby
nums = [3, 7, 2, 11, 4, 9]

big = nums.find do |n|
  n > 8
end
puts big    # 11

even = nums.detect do |n|
  n % 2 == 0
end
puts even   # 2   (.detect is an alias for .find)

# Returns nil when nothing matches
huge = nums.find do |n|
  n > 100
end
p huge      # (Nil) nil
```

---

## Nil Safety — `&.` Operator (v1.7)

`x&.method` calls `.method` on `x`, returning `nil` instead of crashing when `x` is nil.
Chains short-circuit at the first `nil`.

```ruby
user    = {name: "Alice"}
missing = nil

puts user["name"]&.upcase      # ALICE
puts missing&.upcase           # nil  (no crash)
puts missing&.upcase&.reverse  # nil  (chain stops at first nil)
puts missing&.length           # nil

# Great for optional data
def display(val)
  result = val&.upcase
  if result == nil
    return "N/A"
  end
  return result
end

puts display("hello")   # HELLO
puts display(nil)       # N/A
```

All Frankie method aliases work through `&.` — `&.upcase`, `&.length`, `&.reverse`, `&.split`, etc.

---

## String Templates — `template()` (v1.7)

Replace `{{key}}` placeholders in a string with values from a hash.

```ruby
msg = template("Hello, {{name}}! You are {{age}}.", {name: "Alice", age: 30})
puts msg    # Hello, Alice! You are 30.

# Works great with loops
people = [
  {name: "Alice", role: "Engineer"},
  {name: "Bob",   role: "Designer"}
]
people.each do |p|
  puts template("  {{name}} — {{role}}", p)
end

# Raises KeyError if a placeholder key is missing
begin
  template("{{missing}}", {})
rescue e
  puts "Error: #{e}"
end
```

---

## File System Operations (v1.7)

| Function | Description |
|---|---|
| `file_rename(src, dst)` | Rename or move a file |
| `file_copy(src, dst)` | Copy a file (preserves metadata); returns dst |
| `file_mkdir(path)` | Create directory and all parents (like `mkdir -p`) |
| `file_mkdir(path, false)` | Create single directory only (no parents) |
| `dir_exists(path)` | True if path is an existing directory |
| `dir_list(path)` | Sorted vector of filenames in directory (default: `"."`) |

```ruby
# Create nested directories
file_mkdir("/tmp/myapp/data/reports")
puts dir_exists("/tmp/myapp/data/reports")   # true
puts dir_exists("/tmp/ghost")                # false

# Copy and rename files
file_write("/tmp/myapp/data/a.txt", "hello")
file_copy("/tmp/myapp/data/a.txt", "/tmp/myapp/data/b.txt")
file_rename("/tmp/myapp/data/b.txt", "/tmp/myapp/data/c.txt")

# List a directory
puts dir_list("/tmp/myapp/data")    # [a.txt, c.txt]
puts dir_list()                     # current directory
```

---

## `assert_raises_typed` (v1.7)

Assert that a specific error *type* is raised — not just any error.

```ruby
# Passes only if ZeroDivisionError is raised
assert_raises_typed(def()
  x = 1 // 0
end, "ZeroDivisionError", "division raises correctly")

# Passes only if RuntimeError is raised
assert_raises_typed(def()
  file_read("/no/such/file.txt")
end, "RuntimeError", "missing file raises RuntimeError")

# Fails with a clear message if the wrong type is raised
assert_raises_typed(def()
  raise "oops"   # RuntimeError, not ZeroDivisionError
end, "ZeroDivisionError", "this will fail")
# ✗  this will fail (got RuntimeError instead)
```

Supported type strings mirror typed `rescue`: `RuntimeError`, `TypeError`, `ValueError`,
`ZeroDivisionError`, `IndexError`, `KeyError`, `IOError`, `FileNotFoundError`,
`OverflowError`, `NameError`, `AttributeError`, `Exception` / `Error`.

---

## Web Server (v1.4)

See `docs/09_web.md` for the full reference.

```ruby
app = web_app()

app.get("/") do |req|
  html_response("<h1>Hello from Frankie!</h1>")
end

app.get("/greet/:name") do |req|
  name = req.params["name"]
  response("Hello, #{name}!")
end

app.get("/api/status") do |req|
  json_response({status: "ok", version: "1.7"})
end

app.post("/notes") do |req|
  data = req.json
  json_response({id: 1, text: data["text"]}, 201)
end

app.not_found do |req|
  halt(404, "No route for #{req.path}")
end

app.run(3000)
```

---

## SQLite (v1.2)

See `docs/07_database.md` for the full reference.

```ruby
db = db_open(":memory:")
db.exec("CREATE TABLE notes (id INTEGER PRIMARY KEY, text TEXT)")
db.insert("notes", {text: "Hello from Frankie!"})
db.insert("notes", {text: "Zero dependencies."})

db.find_all("notes").each do |row|
  puts "#{row["id"]}: #{row["text"]}"
end

top = db.query_one("SELECT * FROM notes LIMIT 1", [])
puts top["text"]
db.close
```
