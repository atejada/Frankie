# 🧟 Frankie Programming Language

```
  _____                _    _
 |  ___| __ __ _ _ __ | | _(_) ___
 | |_ | '__/ _` | '_ \| |/ / |/ _ \
 |  _|| | | (_| | | | |   <| |  __/
 |_|  |_|  \__,_|_| |_|_|\_\_|\___|

 The Frankie Language v1.12
 Stitched together from Ruby • Python • R • Fortran
```

> Designed and Developed by **Claude** and **Blag Aka. Alvaro Tejada Galindo**.  
> If you have any questions, feel free to ask me. Have fun 🤓

---

## What is Frankie?

Frankie is a **procedural, expressive, terminal-native programming language** named after Frankenstein — lovingly stitched together from the best parts of four legendary languages:

| Donor | What Frankie Borrows |
|---|---|
| **Ruby** | Syntax, `do...end`, `if/unless`, iterators, string interpolation, `begin/rescue` |
| **Python** | Clean semantics, rich data structures, execution model |
| **R** | Vectors, statistics, pipe operator `\|>`, `seq()`, `mean/stdev/median` |
| **Fortran** | `do...while`, integer division `//`, exponentiation `**` |

Frankie is **not object-oriented**. Proudly procedural — functions, data, loops, logic. No classes, no `self`, no inheritance.

---

## Quick Install

```bash
cd frankie
python3 install.py
export PATH="/path/to/frankie/bin:$PATH"
```

Then:
```bash
frankiec run examples/hello.fk
frankiec repl
```

---

## Quick Taste

```ruby
# Fibonacci
def fib(n)
  if n <= 1
    return n
  end
  return fib(n - 1) + fib(n - 2)
end

puts fib(10)    # 55

# R-style stats
data = [23, 45, 12, 67, 34, 89]
puts mean(data)
puts stdev(data)
data |> sum |> puts

# Iterators
evens = [1,2,3,4,5,6].select do |x|
  x % 2 == 0
end
puts evens    # [2, 4, 6]

# Case/when
case evens.length
when 3
  puts "three evens"
else
  puts "something else"
end

# Destructuring
lo, hi = [min(data), max(data)]
puts "Range: #{lo}..#{hi}"

# Error handling
begin
  raise "oops" if lo < 0
rescue e
  puts "Caught: #{e}"
end
```

---

## v1.12 Highlights

```ruby
# String .gsub with block — transform each match
puts "hello world".gsub("[aeiou]") do |m| m.upcase end   # hEllO wOrld
puts "Card: 4111".gsub("\\d") do |m| "*" end               # Card: ****

# Hash .map_hash — transform a hash into a new hash
prices = {apple: 1.20, banana: 0.50}
puts prices.map_hash do |k, v| [k, v * 2] end   # {apple: 2.4, banana: 1.0}

# round(x, n) — finally!
puts round(3.14159, 2)   # 3.14
puts round(1.5)          # 2

# Vector .product — cartesian product
puts [1, 2].product([3, 4])   # [[1,3],[1,4],[2,3],[2,4]]

# String .chars — now first-class documented
puts "hello".chars.select do |c| c != "l" end   # ["h","e","o"]
puts "Frankie".chars.reverse.join("")             # eiknarF

# rescue FileNotFoundError now actually works
begin
  file_read("missing.txt")
rescue FileNotFoundError e
  puts "Caught: #{e}"
end

# assert_match and assert_nil in the test runner
assert_match("hello@example.com", "\\w+@\\w+\\.\\w+", "valid email")
assert_nil(find_user(999), "missing user returns nil")

# frankiec watch main.fk          — re-run on save
# frankiec watch test.fk --test   — re-run tests on save
# frankiec repl --no-banner        — headless REPL
```
---

## v1.11 Highlights

```ruby
# Implicit return — last expression is the return value
def double(x)
  x * 2
end
puts double(7)   # 14

# Inline if expression
grade = if score >= 90 then "A" elsif score >= 80 then "B" else "C" end

# String .replace()
puts "hello world".replace("world", "Frankie")   # hello Frankie

# String .format(hash)
puts "Hello, {name}! Age: {age}.".format({name: "Alice", age: 30})

# .zip_with — pair-wise transform
puts [1,2,3].zip_with([10,20,30]) do |a, b| a + b end   # [11, 22, 33]

# Multiple return values via destructuring
def minmax(v)
  [min(v), max(v)]
end
lo, hi = minmax([3, 1, 4, 1, 5, 9])
puts "#{lo}..#{hi}"   # 1..9

# frankiec check now uses boxed error output
# REPL: ↑ recalls full multi-line blocks
# frankiec fmt: heredoc bodies preserved verbatim
```
---

## v1.10 Highlights

```ruby
# String & vector * repetition
puts "ha" * 3           # hahaha
puts [0] * 5            # [0, 0, 0, 0, 0]

# Heredoc — multiline strings with indent-stripping and interpolation
version = "1.10"
msg = <<~SQL
  SELECT * FROM users WHERE version = '#{version}'
SQL
puts msg

# times() as a standalone function
times(3) do |i|
  puts "tick #{i}"
end

# flatten(depth)
puts [[1,[2]],[3,[4,[5]]]].flatten     # [1,2,3,4,5]
puts [[1,[2]],[3,[4,[5]]]].flatten(1)  # [1,[2],3,[4,[5]]]

# map_with_index
puts ["a","b","c"].map_with_index do |v,i| "#{i}:#{v}" end

# pp — pretty-print nested structures and records
pp({server: {host: "localhost", port: 3000}})

# Named rescue without variable
begin
  x = 1 // 0
rescue ZeroDivisionError
  puts "caught"
end

# encode / decode
puts "hi".encode       # [104, 105]
puts [104, 105].decode  # hi

# exit(42) now propagates exact code to the shell
# frankiec --help  /  frankiec run --help
```
---

## Testing

```ruby
# test.fk
x = 10
x += 5
assert_eq(x, 15, "+= works")

result = [1, 3, 5, 7].find do |n|
  n > 4
end
assert_eq(result, 5, ".find returns first match")
```

```bash
frankiec test           # runs test.fk
frankiec test my.fk     # runs a named file
```

---

## Web Server

```ruby
# Sinatra-style web server — zero dependencies
app = web_app()

app.get("/greet/:name") do |req|
  name = req.params["name"]
  response("Hello, #{name}!")
end

app.get("/api/status") do |req|
  json_response({status: "ok", version: "1.6"})
end

app.post("/notes") do |req|
  data = req.json
  json_response({id: 1, text: data["text"]}, 201)
end

app.run(3000)
```

---

## SQLite

```ruby
# SQLite — zero dependencies
db = db_open(":memory:")
db.exec("CREATE TABLE notes (id INTEGER PRIMARY KEY, text TEXT)")
db.insert("notes", {text: "Frankie has SQLite!"})
db.insert("notes", {text: "Zero dependencies."})
db.find_all("notes").each do |row|
  puts "#{row[\"id\"]}: #{row[\"text\"]}"
end
db.close
```

---

## CLI Commands

```bash
frankiec                    # launch the REPL
frankiec run   <file.fk>    # run a program
frankiec build <file.fk>    # compile to Python source
frankiec check <file.fk>    # syntax check only
frankiec test  [file.fk]    # run test suite (default: test.fk)
frankiec fmt   [--write] [--check] <file.fk>   # auto-format
frankiec docs  [--output out.md] <file.fk>     # generate docs
frankiec repl               # interactive REPL
frankiec version            # show version
frankiec --help             # full usage
frankiec <cmd> --help       # per-command help
```

---

## Documentation

Full documentation lives in the `docs/` folder:

| File | Contents |
|---|---|
| `docs/01_getting_started.md` | Installation, CLI commands, REPL guide, scaffolding |
| `docs/02_language_reference.md` | Variables, types, operators, control flow, nil safety, functions |
| `docs/03_collections.md` | Vectors, hashes, all iterators |
| `docs/04_stdlib.md` | Math, stats, randomness, strings, regex, file I/O, file system, JSON, CSV, DateTime, HTTP, testing |
| `docs/05_examples.md` | All example programs explained |
| `docs/06_changelog.md` | v1.0 – v1.12 release notes |
| `docs/07_database.md` | SQLite database access — full API reference |
| `docs/08_v17_features.md` | v1.4–v1.7 feature reference: nil safety, templates, file system, typed asserts, web server, randomness, constants, compound assignment |
| `docs/09_web.md` | Web server — routes, requests, responses, filters |
| `docs/10_v18_features.md` | v1.8 feature reference: lambdas, hash merge `\|`, group_by, each_slice, each_cons |
| `docs/11_v19_features.md` | v1.9 feature reference: records, dig, zip, fmt, docs, readline REPL, .env loader |
| `docs/12_v110_features.md` | v1.10 feature reference: string/vector *, heredoc, times(), flatten(depth), map_with_index, pp, encode/decode |
| `docs/13_v111_features.md` | v1.11 feature reference: implicit return, inline if, .replace(), .format(hash), .zip_with, multiple return values |
| `docs/14_v112_features.md` | v1.12 feature reference: gsub block, map_hash, round, product, chars, FileNotFoundError, assert_match/nil, watch, --no-banner |

The formal language grammar lives in `SPEC.md`.

---

## Project Structure

```
frankie/
├── bin/
│   └── frankiec           ← executable (created by install.py)
├── compiler/
│   ├── lexer.py           ← tokeniser
│   ├── parser.py          ← recursive descent parser
│   ├── ast_nodes.py       ← AST node definitions
│   └── codegen.py         ← Python code generator
├── docs/                  ← full documentation
├── examples/              ← example .fk programs (incl. webapp.fk, whats_new_v16.fk … whats_new_v112.fk)
├── frankiec.py            ← compiler CLI entry point
├── frankie_stdlib.py      ← runtime standard library
├── repl.py                ← interactive REPL
├── install.py             ← installer
├── SPEC.md                ← language specification
└── README.md              ← this file
```

---

## Requirements

- Python 3.10+
- No external dependencies

---

## License

Frankie is open and free. Build things, break things, stitch things together.

*"It's alive!"* 🧟⚡
