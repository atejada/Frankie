# 🧟 Frankie Programming Language

```
  _____                _    _
 |  ___| __ __ _ _ __ | | _(_) ___
 | |_ | '__/ _` | '_ \| |/ / |/ _ \
 |  _|| | | (_| | | | |   <| |  __/
 |_|  |_|  \__,_|_| |_|_|\_\_|\___|

 The Frankie Language v1.8
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

## v1.8 Highlights

```ruby
# Lambdas — store and pass functions as values
double = ->(x) { x * 2 }
puts double.call(5)      # 10

add = ->(a, b) { a + b }
puts add.call(3, 7)      # 10

def apply(fn, val)        # higher-order functions
  return fn.call(val)
end
puts apply(double, 9)    # 18

# Hash merge operator  |
defaults = {color: "blue", size: "medium"}
overrides = {color: "red"}
puts defaults | overrides  # {color: red, size: medium}

# group_by — bucket a vector by a key
people = [{name: "Alice", dept: "Eng"}, {name: "Bob", dept: "Design"}, {name: "Carol", dept: "Eng"}]
by_dept = people.group_by do |p| p["dept"] end
puts by_dept["Eng"].length   # 2

# each_slice — iterate in fixed-size chunks
[1,2,3,4,5,6].each_slice(2) do |s|
  puts s       # [1,2]  [3,4]  [5,6]
end

# each_cons — sliding window iteration
[10, 13, 11, 15].each_cons(2) do |w|
  puts w[1] - w[0]    # 3  -2  4
end
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
| `docs/01_getting_started.md` | Installation, CLI commands, REPL guide, scaffolding |
| `docs/02_language_reference.md` | Variables, types, operators, control flow, nil safety, functions |
| `docs/03_collections.md` | Vectors, hashes, all iterators |
| `docs/04_stdlib.md` | Math, stats, randomness, strings, regex, file I/O, file system, JSON, CSV, DateTime, HTTP, testing |
| `docs/05_examples.md` | All example programs explained |
| `docs/06_changelog.md` | v1.0 – v1.8 release notes |
| `docs/07_database.md` | SQLite database access — full API reference |
| `docs/08_v17_features.md` | v1.4–v1.7 feature reference: nil safety, templates, file system, typed asserts, web server, randomness, constants, compound assignment |
| `docs/09_web.md` | Web server — routes, requests, responses, filters |
| `docs/10_v18_features.md` | v1.8 feature reference: lambdas, hash merge `\|`, group_by, each_slice, each_cons |

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
