# Error Handling

## `begin / rescue / ensure`

Wrap risky code in a `begin` block. If an error is raised, execution jumps to the matching `rescue` clause. `ensure` always runs — whether an error occurred or not.

```ruby
begin
  result = 10 // 0
rescue e
  puts "Something went wrong: #{e}"
ensure
  puts "This always runs."
end
```

`rescue e` without a type catches any error. `ensure` is optional.

---

## Typed Rescue

Catch specific error types with typed rescue clauses. Clauses are matched in order — the first matching type wins.

```ruby
begin
  content = file_read("config.json")
rescue FileNotFoundError e
  puts "Config file missing: #{e}"
rescue RuntimeError e
  puts "Runtime error: #{e}"
rescue e
  puts "Unexpected error: #{e}"
ensure
  puts "Done."
end
```

Multiple `rescue` clauses let you respond differently to different failure modes — re-raise, recover, log, or substitute a default.

---

## Supported Error Types

| Type | When it occurs |
|---|---|
| `ZeroDivisionError` | Division or modulo by zero |
| `FileNotFoundError` | `file_read`, `file_lines`, `file_copy`, `file_rename` on a missing file |
| `TypeError` | Wrong type for an operation — e.g. adding Integer and String |
| `IndexError` | Vector index out of bounds |
| `KeyError` | Hash key not found (when using strict access) |
| `ValueError` | Invalid value — e.g. `to_i` on a non-numeric string |
| `NameError` | Undefined variable or function |
| `AttributeError` | Method or property doesn't exist on the receiver |
| `RecursionError` | Stack overflow from too-deep recursion |
| `RuntimeError` | General runtime error |
| `Exception` / `Error` | Catch-all — matches any error |

---

## `raise`

Raise an error manually with a message.

```ruby
def divide(a, b)
  raise "Cannot divide by zero" if b == 0
  a / b
end

begin
  puts divide(10, 0)
rescue RuntimeError e
  puts "Caught: #{e}"   # Caught: Cannot divide by zero
end
```

`raise` without a type raises a `RuntimeError`. Use it to signal invalid inputs, failed preconditions, or unexpected states.

---

## Rescuing File I/O

File operations raise `FileNotFoundError` when the source is missing — making `rescue` the natural pattern for optional files.

```ruby
begin
  config = file_read("config.json")
rescue FileNotFoundError e
  puts "No config found — using defaults."
  config = "{}"
end

# file_lines works the same way
begin
  rows = file_lines("data.csv")
rescue FileNotFoundError e
  rows = []
end
```

`file_delete` and `file_exists` do not raise on missing files — they return `false` instead, since those operations are naturally idempotent.

---

## Nested `begin` Blocks

`begin` blocks can be nested. Each has its own `rescue` and `ensure`.

```ruby
begin
  begin
    x = risky_parse(input)
  rescue ValueError e
    puts "Parse failed: #{e}"
    x = default_value
  end

  result = process(x)
rescue RuntimeError e
  puts "Processing failed: #{e}"
ensure
  cleanup()
end
```

---

## `ensure` for Cleanup

`ensure` is the right place for cleanup that must always happen — closing files, releasing resources, resetting state.

```ruby
f = file_open("/tmp/output.txt", "w")
begin
  f.write("result: #{compute()}")
rescue e
  puts "Write failed: #{e}"
ensure
  f.close   # always closes, even if an error occurred
end
```

---

## Error Handling in Tests

Use `assert_raises` and `assert_raises_typed` in test suites to verify that errors are raised correctly:

```ruby
# Assert that any error is raised
assert_raises(def()
  file_read("/no/such/file.txt")
end, "missing file raises an error")

# Assert that a specific type is raised
assert_raises_typed(def()
  x = 1 // 0
end, "ZeroDivisionError", "division by zero raises ZeroDivisionError")

assert_raises_typed(def()
  file_read("/no/such/file.txt")
end, "FileNotFoundError", "missing file raises FileNotFoundError")
```

---

## Common Patterns

### Provide a default on failure

```ruby
def safe_read(path, default = "")
  begin
    file_read(path)
  rescue FileNotFoundError e
    default
  end
end

content = safe_read("config.json", "{}")
```

### Retry on transient errors

```ruby
attempts = 0
begin
  attempts += 1
  result = http_get("https://api.example.com/data")
rescue RuntimeError e
  retry_limit = 3
  if attempts < retry_limit
    puts "Attempt #{attempts} failed — retrying..."
    sleep(1)
    retry
  else
    puts "All #{retry_limit} attempts failed: #{e}"
    result = nil
  end
end
```

### Log and continue

```ruby
results = []
items.each do |item|
  begin
    results.push(process(item))
  rescue e
    puts "Warning: failed to process #{item}: #{e}"
  end
end
```

---

## User-Defined Error Types (v1.17)

Declare your own error types with `error`, raise them with
`raise TypeName, "message"`, and catch them with Ruby-style binding:

```ruby
error TimeoutError
error ValidationError

def save_user(u)
  raise ValidationError, "email is required" unless u.has_key?("email")
end

begin
  save_user({name: "Blag"})
rescue ValidationError => e
  puts "Invalid: #{e}"
rescue TimeoutError => e
  puts "Too slow: #{e}"
rescue e
  puts "Something else: #{e}"
end
```

Notes:

- `raise TypeName("message")` also works.
- A typed `raise` auto-declares its type, so simple scripts can skip `error`.
- Generic `rescue e` still catches typed errors.
- `assert_raises_typed(fn, "ValidationError")` understands user types.
- The older `rescue TypeName e` binding (no `=>`) keeps working.
