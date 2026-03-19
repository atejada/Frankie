# 🧟 Frankie Programming Language

```
  _____                 _    _
 |  ___| __ __ _ _ __ | | _(_) ___
 | |_ | '__/ _` | '_ \| |/ / |/ _ \
 |  _|| | | (_| | | | |   <| |  __/
 |_|  |_|  \__,_|_| |_|_|\_\_|\___|

 The Frankie Language v1.7
 Stitched together from Ruby • Python • R • Fortran
```

> Designed and Developed by **Claude** and **Blag Aka. Alvaro Tejada Galindo**.  
> If you have any questions, feel free to ask me. Have fun 🤓

---

## What is Frankie?

![Frankie - The Programming Language](https://github.com/atejada/Frankie/blob/main/The%20Frankie%20Programming%20Language.png)

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

## v1.7 Highlights

```ruby
# Nil Safety — &. operator
user = {name: "Alice"}
missing = nil

puts user["name"]&.upcase   # ALICE
puts missing&.upcase        # nil  (no crash, ever)
puts missing&.upcase&.reverse  # nil  (chain short-circuits)

# String Templates
msg = template("Hello, {{name}}! You are {{age}}.", {name: "Bob", age: 25})
puts msg   # Hello, Bob! You are 25.

# File System Operations
file_mkdir("/tmp/myapp/data")
puts dir_exists("/tmp/myapp/data")    # true

file_write("/tmp/myapp/data/a.txt", "hello")
file_copy("/tmp/myapp/data/a.txt", "/tmp/myapp/data/b.txt")
file_rename("/tmp/myapp/data/b.txt", "/tmp/myapp/data/c.txt")
puts dir_list("/tmp/myapp/data")      # [a.txt, c.txt]

# assert_raises_typed in tests
assert_raises_typed(def()
  x = 1 // 0
end, "ZeroDivisionError", "division raises correctly")
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
frankiec repl               # interactive REPL
frankiec version            # show version
```

---

## Documentation

Full documentation lives in the `docs/` folder:

| File | Contents |
|---|---|
| `docs/01_getting_started.md` | Installation, first program, REPL guide |
| `docs/02_language_reference.md` | Variables, types, operators, control flow, functions |
| `docs/03_collections.md` | Vectors, hashes, all iterators |
| `docs/04_stdlib.md` | Math, stats, strings, regex, file I/O, system |
| `docs/05_examples.md` | All example programs explained |
| `docs/06_changelog.md` | v1.0 – v1.7 release notes |
| `docs/07_database.md` | SQLite database access — full API reference |
| `docs/08_v13_features.md` | JSON, CSV, DateTime, HTTP, project scaffolding |
| `docs/09_web.md` | Web server — routes, requests, responses, filters |

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
├── examples/              ← example .fk programs (incl. webapp.fk, whats_new_v16.fk, whats_new_v17.fk)
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
