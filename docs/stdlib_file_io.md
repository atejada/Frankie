# File I/O

## Overview

Frankie has a complete file I/O library built on Python's standard `open()` — zero external dependencies. All functions are available without any import.

---

## Reading Files

### `file_read(path)` — Read entire file as a string

```ruby
content = file_read("data.txt")
puts content
```

### `file_lines(path)` — Read file as a vector of lines

Strips trailing newlines from each line.

```ruby
lines = file_lines("data.csv")
puts lines.length        # number of lines
puts lines[0]            # first line
lines.each do |line|
  puts line
end
```

Both raise `FileNotFoundError` if the file doesn't exist — use `rescue` to handle it gracefully:

```ruby
begin
  content = file_read("config.json")
rescue FileNotFoundError e
  puts "Config missing — using defaults"
  content = "{}"
end
```

---

## Writing Files

### `file_write(path, content)` — Write string to file (overwrites)

Creates the file if it doesn't exist. Overwrites silently if it does.

```ruby
file_write("output.txt", "Hello, Frankie!\n")
file_write("report.csv", "name,score\nAlice,95\nBob,87\n")
```

### `file_append(path, content)` — Append to file

Adds content to the end of the file without overwriting.

```ruby
file_write("log.txt", "Session started\n")
file_append("log.txt", "User logged in\n")
file_append("log.txt", "User logged out\n")

puts file_read("log.txt")
# Session started
# User logged in
# User logged out
```

---

## File Management

### `file_exists(path)` — Check if a file exists

Returns `true` or `false`. Never raises.

```ruby
if file_exists("config.json")
  config = json_read("config.json")
else
  config = {host: "localhost", port: 3000}
end
```

### `file_delete(path)` — Delete a file

Returns `false` if the file doesn't exist — deleting a missing file is a no-op, not an error.

```ruby
file_delete("temp.txt")          # true if deleted, false if missing
file_delete("/tmp/scratch.json") # safe to call even if missing
```

### `file_copy(src, dst)` — Copy a file

Returns the destination path on success. Raises `FileNotFoundError` if source is missing.

```ruby
file_copy("data.csv", "data.csv.bak")
```

### `file_rename(src, dst)` — Rename or move a file

Raises `FileNotFoundError` if source is missing.

```ruby
file_rename("draft.txt", "final.txt")
file_rename("output.csv", "/tmp/output.csv")   # move to different directory
```

---

## Directory Operations

### `file_mkdir(path)` — Create a directory

Creates all intermediate directories automatically (like `mkdir -p`).

```ruby
file_mkdir("data/reports/2024")   # creates all three levels
```

### `dir_exists(path)` — Check if a directory exists

```ruby
if not dir_exists("output")
  file_mkdir("output")
end
```

### `dir_list(path)` — List directory contents

Returns a sorted vector of filenames (not full paths). Defaults to current directory.

```ruby
entries = dir_list("data")
puts entries   # ["config.json", "users.csv", "report.txt"]

# List current directory
puts dir_list()
```

---

## File Handles

For fine-grained control, open a file as a handle with `file_open`:

```ruby
f = file_open("output.txt", "w")
f.write("line one\n")
f.write("line two\n")
f.close
```

Modes: `"r"` (read), `"w"` (write/overwrite), `"a"` (append).

Always close the handle when done. Use `ensure` to guarantee it:

```ruby
f = file_open("data.txt", "r")
begin
  content = f.read
  puts content
ensure
  f.close
end
```

---

## Consistent Error Behaviour

| Function | Missing file behaviour |
|---|---|
| `file_read(path)` | Raises `FileNotFoundError` |
| `file_lines(path)` | Raises `FileNotFoundError` |
| `file_copy(src, dst)` | Raises `FileNotFoundError` (src must exist) |
| `file_rename(src, dst)` | Raises `FileNotFoundError` (src must exist) |
| `file_delete(path)` | Returns `false` — idempotent |
| `file_exists(path)` | Returns `false` — that's what it tests |
| `dir_exists(path)` | Returns `false` — same |

---

## Practical Examples

```ruby
# Safe config loader with fallback
def load_config(path)
  begin
    json_read(path)
  rescue FileNotFoundError e
    {}
  end
end

config = load_config("config.json")
host = config.fetch("host", "localhost")
port = config.fetch("port", 3000)

# Process every line in a file
lines = file_lines("emails.txt")
valid = lines.select do |line|
  line.matches?("\\w+@\\w+\\.\\w+")
end
puts "#{valid.length} valid emails out of #{lines.length}"

# Write a report
rows = [
  {name: "Alice", score: 95},
  {name: "Bob",   score: 87},
  {name: "Carol", score: 92}
]

file_write("report.txt", "Score Report\n")
file_append("report.txt", "-" * 20 + "\n")
rows.each do |r|
  file_append("report.txt", "#{r["name"].ljust(10)} #{r["score"]}\n")
end
puts file_read("report.txt")

# Rotate a log file
def rotate_log(path, max_lines)
  return unless file_exists(path)
  lines = file_lines(path)
  if lines.length > max_lines
    kept = lines.drop(lines.length - max_lines)
    file_write(path, kept.join("\n") + "\n")
  end
end

rotate_log("app.log", 1000)
```

---

## Quick Reference

| Function | Description |
|---|---|
| `file_read(path)` | Read entire file as string |
| `file_lines(path)` | Read file as vector of lines |
| `file_write(path, str)` | Write string to file (overwrites) |
| `file_append(path, str)` | Append string to file |
| `file_exists(path)` | True if file exists |
| `file_delete(path)` | Delete file — returns false if missing |
| `file_copy(src, dst)` | Copy file |
| `file_rename(src, dst)` | Rename or move file |
| `file_open(path, mode)` | Open file handle (`"r"`, `"w"`, `"a"`) |
| `file_mkdir(path)` | Create directory (and parents) |
| `dir_exists(path)` | True if directory exists |
| `dir_list(path)` | Sorted vector of filenames in directory |
