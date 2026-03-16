# v1.3 Features: JSON, CSV, DateTime, HTTP & Scaffolding

All v1.3 additions use Python's built-in standard library — **zero external dependencies**.

---

## Default Parameter Values

```ruby
def greet(name, msg="Hello", punct="!")
  puts "#{msg}, #{name}#{punct}"
end

greet("Alice")             # Hello, Alice!
greet("Bob", "Hi")         # Hi, Bob!
greet("Carol", "Hey", ".") # Hey, Carol.

def power(base, exp=2)
  return base ** exp
end

puts power(4)       # 16
puts power(2, 10)   # 1024
```

Required parameters must come before optional ones.

---

## JSON

```ruby
# Serialize
data = {name: "Alice", scores: [95, 87, 92]}
puts json_dump(data)
puts json_dump(data, true)   # pretty-printed

# Parse
obj = json_parse('{"name":"Bob","age":30}')
puts obj["name"]    # Bob
puts obj["age"]     # 30

# File I/O
json_write("/tmp/data.json", data, true)
loaded = json_read("/tmp/data.json")
puts loaded["name"]
```

### JSON API

| Function | Description |
|---|---|
| `json_parse(str)` | JSON string → Frankie value |
| `json_dump(obj)` | Frankie value → JSON string |
| `json_dump(obj, true)` | Pretty-printed JSON |
| `json_read(path)` | Read and parse JSON file |
| `json_write(path, obj)` | Write JSON file |
| `json_write(path, obj, true)` | Write pretty JSON file |

---

## CSV

```ruby
# Build from vector of hashes
rows = [
  {name: "Alice", dept: "Engineering", salary: 95000},
  {name: "Bob",   dept: "Marketing",   salary: 72000}
]

text = csv_dump(rows)
puts text
# name,dept,salary
# Alice,Engineering,95000
# Bob,Marketing,72000

# Parse back
reparsed = csv_parse(text)
reparsed.each do |row|
  puts "#{row["name"]}: $#{row["salary"]}"
end

# File I/O
csv_write("/tmp/data.csv", rows)
loaded = csv_read("/tmp/data.csv")
puts loaded.length    # 2
```

### CSV API

| Function | Description |
|---|---|
| `csv_parse(text)` | CSV string → vector of hashes (uses first row as headers) |
| `csv_parse(text, false)` | CSV string → vector of vectors (no header row) |
| `csv_dump(rows)` | Vector of hashes → CSV string |
| `csv_dump(rows, headers)` | With explicit header list |
| `csv_read(path)` | Read and parse CSV file |
| `csv_write(path, rows)` | Write CSV file |

---

## DateTime

```ruby
# Current time
t = now()
puts t                       # 2025-03-16 14:23:01.123456
puts t.year                  # 2025
puts t.month                 # 3
puts t.day                   # 16
puts t.hour                  # 14
puts t.weekday_name          # Sunday

# Construct a date
d = date_from(2025, 12, 25)
puts d.format("%A, %d %B %Y")   # Thursday, 25 December 2025

# Parse a date string
d2 = date_parse("2025-03-16")
d3 = date_parse("25/12/2025", "%d/%m/%Y")

# Arithmetic
tomorrow   = d2.add_days(1)
next_hour  = now().add_hours(1)
next_week  = d2.add_days(7)

# Differences
puts d2.diff_days(d)         # 284
puts d2.diff_seconds(d)      # 24537600

# Comparison
puts d2.is_before(d)         # true
puts d2.is_after(d)          # false

# Format
puts d.format("%Y-%m-%d")    # 2025-12-25
puts d.format("%d/%m/%Y")    # 25/12/2025
puts d.weekday               # 3  (0=Monday)
puts d.weekday_name          # Thursday
puts d.timestamp             # Unix timestamp as float
```

### DateTime API

| Function / Method | Description |
|---|---|
| `now()` | Current date and time |
| `today()` | Today at midnight |
| `date_from(y, m, d, h, min, s)` | Construct from components |
| `date_parse(str)` | Parse `YYYY-MM-DD` string |
| `date_parse(str, fmt)` | Parse with custom format |
| `.year` `.month` `.day` | Date components |
| `.hour` `.minute` `.second` | Time components |
| `.format(fmt)` | Format with `strftime` directives |
| `.add_days(n)` | Add n days → new date |
| `.add_hours(n)` | Add n hours → new date |
| `.add_minutes(n)` | Add n minutes → new date |
| `.diff_days(other)` | Absolute difference in days |
| `.diff_seconds(other)` | Absolute difference in seconds |
| `.weekday()` | 0 = Monday … 6 = Sunday |
| `.weekday_name()` | Full day name (Monday, Tuesday…) |
| `.is_before(other)` | Comparison |
| `.is_after(other)` | Comparison |
| `.timestamp()` | Unix timestamp (float) |

---

## HTTP

```ruby
# GET request
resp = http_get("https://api.example.com/users")
puts resp.status      # 200
puts resp.ok          # true
data = resp.json()    # parse body as JSON
puts data["count"]

# POST with JSON body (dict auto-encoded)
payload = {name: "Alice", email: "alice@example.com"}
resp2 = http_post("https://api.example.com/users", payload)
puts resp2.status

# With custom headers
resp3 = http_get("https://api.example.com/secret",
                 {Authorization: "Bearer mytoken123"})

# Error handling
begin
  resp = http_get("https://api.example.com/data")
  if resp.ok
    puts resp.json()
  else
    puts "Error #{resp.status}: #{resp.body}"
  end
rescue e
  puts "Request failed: #{e}"
end

# URL helpers
params = {q: "frankie lang", page: 1}
puts url_encode(params)      # q=frankie+lang&page=1
decoded = url_decode("q=hello+world&n=42")
puts decoded["q"]            # hello world
```

### HTTP API

| Function | Description |
|---|---|
| `http_get(url)` | GET request |
| `http_get(url, headers)` | GET with custom headers |
| `http_post(url, data)` | POST (dict → JSON, string → plain text) |
| `http_put(url, data)` | PUT request |
| `http_delete(url)` | DELETE request |
| `url_encode(hash)` | Encode hash as query string |
| `url_decode(str)` | Decode query string → hash |

### HTTP Response

| Property / Method | Description |
|---|---|
| `.status` | HTTP status code (integer) |
| `.body` | Response body as string |
| `.headers` | Response headers as hash |
| `.ok` | True if status is 2xx |
| `.json()` | Parse body as JSON |

---

## Project Scaffolding

```bash
frankiec new myapp
```

Creates:

```
myapp/
├── main.fk          ← entry point (puts "Hello from myapp!")
├── test.fk          ← test suite with assert_eq helper
├── lib/
│   └── utils.fk     ← reusable utilities
├── data/            ← JSON, CSV, SQLite files go here
├── .gitignore
├── .env.example
└── README.md
```

Then:

```bash
cd myapp
frankiec run main.fk     # Hello from myapp!
frankiec run test.fk     # run the test suite
frankiec repl            # interactive session
```

---

## Better Error Messages

Compile errors now show a boxed display with source context:

```
╔══ Frankie Compile Error ══════════════════════════════
║  [Parse Error] Line 5, Col 1: Expected 'end' to close 'if'
║
║  File: myprogram.fk
║         3 │   puts "big"
║         4 │ # missing end
║  ──▶    5 │ puts "done"
╚═══════════════════════════════════════════════════════
```

Runtime errors show friendly descriptions:

```
╔══ Frankie Runtime Error ══════════════════════════════
║  Division by zero
║  (ZeroDivisionError: division by zero)
║
║  File: myprogram.fk
║         1 │ x = 10
║         2 │ y = 0
║  ──▶    3 │ puts x / y
╚═══════════════════════════════════════════════════════
```

---

## Syntax Highlighting

Editor support files are in the `editors/` folder:

| File | Description |
|---|---|
| `editors/vscode/` | VS Code extension (copy to `~/.vscode/extensions/frankie-language/`) |
| `editors/frankie.vim` | Vim / Neovim syntax file |
| `editors/frankie.tmLanguage.json` | TextMate / Sublime Text grammar |

See `editors/README.md` for installation instructions for each editor.
