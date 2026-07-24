# 🧟 Frankie Programming Language

```
  _____                _    _
 |  ___| __ __ _ _ __ | | _(_) ___
 | |_ | '__/ _` | '_ \| |/ / |/ _ \
 |  _|| | | (_| | | | |   <| |  __/
 |_|  |_|  \__,_|_| |_|_|\_\_|\___|

 The Frankie Language v1.19.0
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

## Showcase Projects 🧟

Complete, playable programs — each one a single `.fk` file you can read in
one sitting, run with one command, and ship as one self-contained `.py`
with `frankiec bundle`:

```bash
# 🧟 Zombie Chat — multi-room WebSocket chat (server + web UI in one file)
frankiec run examples/projects/zombie_chat/main.fk
#    → open http://localhost:4000 in two tabs and talk to yourself

# ⚡ Word Reanimator — multiplayer hangman; misses assemble a zombie
frankiec run examples/projects/word_reanimator/main.fk
#    → open http://localhost:4001 in two tabs and guess together

# 💰 Frankie Ledger — terminal expense tracker (SQLite + stitches + stats)
cd examples/projects/frankie_ledger
frankiec run main.fk add 12.50 lunch tacos al pastor
frankiec run main.fk report
```

---

## v1.19 Highlights — "Under the microscope"

```ruby
# Gradual type annotations — optional, zero runtime cost
def area(r: Float) -> Float
  3.14159 * r * r
end
puts area(3)        # fine — Int flows into Float
puts area("five")   # frankiec check: ✗ argument 1 expects Float, got String

# Full stepping debugger
#   frankiec run --debug app.fk
#   (fkdb) s · n · stack · vars · any expression · c

# Test coverage
#   frankiec test --coverage
#   ║   87.5%  test.fk  missing: 7
#   (uncovered lines appear as hints in your editor via the LSP)

# TLS clients + UDP sockets
ws  = ws_connect("wss://example.com/socket")
tls = tcp_connect("example.com", 443, tls: true)
udp_send("127.0.0.1", 9999, "ping")

# Stitches from any URL + HTML docs
#   frankiec stitch install https://example.com/foo.fk
#   frankiec docs --html mystitch.fk
```

---

## v1.18 Highlights — "From projects to products"

```ruby
# LSP — live diagnostics, completion & hover docs in any editor
#   frankiec lsp          (VS Code, Neovim, Helix, Zed — anything with LSP)

# frankiec bundle — ship your program as ONE self-contained .py
#   frankiec bundle app.fk -o app.py
#   python3 app.py        (runs anywhere — no Frankie installation needed)

# WebSockets — on the built-in web server, zero deps
app.websocket("/ws/:room") do |ws|
  ws.send("welcome to #{ws.params["room"]}")
  loop do
    msg = ws.recv()
    break if msg == nil
    ws.send("echo: #{msg}")
  end
end

sock = ws_connect("ws://localhost:3000/ws/lobby")
sock.send("hello")
puts sock.recv()

# breakpoint — pause into a scoped debug REPL
def price(qty)
  total = qty * unit_price
  breakpoint          # (fkdb) vars · where · any Frankie expression · c
  total
end

# enum — named sets of symbolic values
enum Status(pending, active, done)
puts Status.pending           # pending
puts Status.include?("done")  # true

# benchmark — time anything, get the milliseconds back
ms = benchmark "crunch" do
  heavy_work()
end                   # ⏱  crunch: 132.4ms

# Set operations + numeric underscores + scientific notation
puts [1, 2, 3].union([3, 4])        # [1, 2, 3, 4]
puts [1, 2, 3].intersect([2, 9])    # [2]
puts [1, 2, 3].difference([2])      # [1, 3]
budget = 1_250_000
tiny   = 2.5e-3

# Project-wide tooling — one line of CI
#   frankiec check .          frankiec fmt --check .

# Stitch lockfile — reproducible installs
#   frankiec stitch install frankiecolor   → writes stitch.lock (sha256-pinned)
#   frankiec stitch verify                 → detects tampering
#   frankiec stitch update                 → refresh + re-pin
```

---

## v1.17 Highlights — "Programs that grow"

```ruby
# import — namespaced modules (require still merges into your scope)
import "lib/geometry" as geo
puts geo.circle_area(5)
puts geo.PI

# error — user-defined error types, with Ruby-style rescue binding
error TimeoutError
error ValidationError

begin
  raise ValidationError, "email is required"
rescue ValidationError => e
  puts "Invalid: #{e}"
rescue TimeoutError => e
  puts "Too slow: #{e}"
end

# First-class ranges — print, convert, stride, and match
r = 1..10
puts r                  # 1..10
puts r.to_vec           # [1, 2, ..., 10]
puts r.include?(7)      # true
puts (1..10).step(3)    # [1, 4, 7, 10]

case score
when 90..100
  puts "A"
when 70..89
  puts "B"
end

# Records now support dot access
record Point(x, y)
p1 = Point(3, 4)
puts p1.x               # 3

# parallel_map — thread-pool map for I/O-bound work
pages = parallel_map(urls, workers: 8) do |u|
  http_get(u)
end

# TCP sockets — terminal-native networking, zero deps
tcp_serve(7777) do |client|
  msg = client.recv_line()
  client.send_line("echo: #{msg}")
end

# Static analysis — catch bugs before running
#   frankiec check app.fk
#   ✗ app.fk:12 — Undefined function: 'greeet'
#   ✗ app.fk:30 — greet() expects 1..2 argument(s), got 3
#   ⚠ app.fk:3  — Unused variable 'tmp' in function 'greet'

# Test groups with filtering, tags, and stubs
test "api parsing", tags: ["fast"] do
  stub("http_get", ->(url) { {body: "{}"} })
  assert_eq(http_get("x")["body"], "{}")
  unstub()
end
#   frankiec test --filter api
#   frankiec test --tag fast

# Stitch installer — fetch community stitches from GitHub
#   frankiec stitch install frankiecolor
#   frankiec stitch list

# Accurate cross-file tracebacks — errors in require'd files now point
# at the right file AND the right line.

# REPL: expressions echo their value, `_` holds the last result,
# and `help <function>` shows documentation.
```

---

## v1.16.2 Highlights

```ruby
# shell() — run any OS command, get structured output
result = shell("git log --oneline -5")
if result["ok"]
  puts result["stdout"]
else
  puts "Exit #{result["exit_code"]}: #{result["stderr"]}"
end

# dotenv() — load .env files into the environment
dotenv()                        # loads .env by default
dotenv(".env.production")       # or any path
puts env("DATABASE_URL")        # now available via env()

# loop do...end — infinite loops, exit with break
i = 0
loop do
  puts "tick #{i}"
  i += 1
  break if i >= 3
end

# ||= — assign only if nil or false (Ruby-compatible)
config = nil
config ||= load_defaults()
cache ||= {}

# Hash#transform_values and transform_keys
prices = {apple: 1.0, banana: 0.5}
doubled = prices.transform_values do |v| v * 2 end
upper   = prices.transform_keys   do |k| k.upcase end

# String#scan — extract all pattern matches
emails = "Send to alice@example.com and bob@test.org".scan(/[\w.]+@[\w.]+/)
puts emails   # [alice@example.com, bob@test.org]

# Hash#deep_merge — recursive merge for nested configs
defaults = {db: {host: "localhost", port: 5432}, debug: false}
overrides = {db: {host: "prod-db"}, debug: true}
config = defaults.deep_merge(overrides)
# => {db: {host: prod-db, port: 5432}, debug: true}

# frankiemail stitch — send email via SMTP (zero extra deps)
stitch "frankiemail"
send_mail(
  to:      "alice@example.com",
  subject: "Hello from Frankie!",
  body:    "Script finished successfully.",
  smtp:    env("SMTP_HOST", "smtp.gmail.com"),
  user:    env("SMTP_USER"),
  pass:    env("SMTP_PASS")
)

# frankiecli stitch — structured CLI argument parsing
stitch "frankiecli"
cli = cli_parse(argv())
name  = cli_get(cli,  "name",    "World")
debug = cli_flag(cli, "verbose")
puts "Hello, #{name}!"

# frankiecache stitch — in-memory TTL cache
stitch "frankiecache"
cache_set("user:42", {name: "Alice"}, ttl: 300)
user = cache_get("user:42")   # nil after 300 seconds
puts cache_size()
```

---

## v1.15 Highlights

```ruby
# Ternary operator — right-associative, works everywhere
grade = score >= 90 ? "A" : score >= 70 ? "B" : "C"
msg   = n == 1 ? "one item" : "#{n} items"

# Keyword-style default parameters
def connect(host, port: 5432, ssl: true, timeout: 30)
  puts "#{host}:#{port} ssl=#{ssl}"
end
connect("localhost")
connect("prod", port: 3306, ssl: false)

# Splat multi-assign
a, b, *rest       = [1, 2, 3, 4, 5]   # rest = [3, 4, 5]
first, *mid, last = ["a", "b", "c", "d"]

# const keyword
const PI       = 3.14159
const BASE_URL = env("BASE_URL", "http://localhost:3000")

# fn.(args) lambda call syntax — now works everywhere
double = ->(x) { x * 2 }
puts double.(6)   # 12

# json_encode — canonical inverse of json_parse
puts json_encode({name: "Alice", scores: [95, 87]})

# base64 and HMAC now public
token = hmac_sign("user_id=42", SECRET)
puts base64_encode("admin:secret")

# String#format with named placeholders
puts "Hello, {name}! v{ver}".format({name: "Blag", ver: "1.15"})

# Path helpers
puts path_join("home", "blag", "frankie")
puts path_extname("script.fk")    # .fk

# Date arithmetic
d = date_from(2026, 4, 17)
puts (d + 30).format("%Y-%m-%d")  # 2026-05-17
puts (d + 30) - d                 # 30

# New test assertions
assert_not_nil(result, "query returned a result")
assert_in("admin", user_roles, "user is admin")

# frankieauth stitch — Basic Auth + Bearer tokens (zero deps)
stitch "frankieauth"
app.use do |req, next_fn|
  if not basic_auth_ok?(req, "admin", env("PASS"))
    halt(401, "Unauthorized")
  end
  next_fn.(req)
end

# frankieratelimit stitch — in-memory per-IP rate limiting
stitch "frankieratelimit"
app.use do |req, next_fn|
  rate_limit_check(req, next_fn, max: 60, window: 60)
end

# Query-string typed helpers
page  = req.query_int("page", 1)
debug = req.query_bool("debug", false)
```

---

## v1.14 Highlights

```ruby
# Hash destructuring — pull keys into variables directly
user = {name: "Alice", role: "admin", age: 30}
{name, role} = user
puts "#{name} is a #{role}"   # Alice is a admin

# Shape pattern matching — case on hash structure
case user
when {role: "admin"}
  puts "Admin panel access granted"
when {role: "moderator", active: true}
  puts "Moderator tools available"
when {active: false}
  puts "Account suspended"
else
  puts "Regular user"
end

# spawn — fire-and-forget background blocks
app.post("/register") do |req|
  spawn do
    send_welcome_email(req.json["email"])
  end
  json_response({status: "registered"}, 201)
end

# timeout — kill slow operations
result = timeout(5) do
  http_get("https://slow-api.example.com/data")
end

# Middleware stack
app.use do |req, next_fn|
  puts "→ #{req.method} #{req.path}"
  next_fn.(req)
end

# Static files
app.static("./public")

# frankietemplate — Mustache-compatible templates
stitch "frankietemplate"
html = render_file("./views/dashboard.html", {
  name: user["name"],
  posts: db.find_all("posts")
})
html_response(html)

# frankiecookie — HMAC-signed cookies
stitch "frankiecookie"
SECRET = env("COOKIE_SECRET")
set_signed_cookie(resp, "user_id", "42", SECRET, {max_age: 86400})
id = get_signed_cookie(req, "user_id", SECRET)   # nil if tampered
```
---

## v1.13.1 Highlights

```ruby
# frankiestring v2 — clean, Frankie-convention string helpers
stitch "frankiestring"

pad_left("42", 6, "0")                   # "000042"
pad_right("hello", 10, ".")              # "hello....."
truncate("Frankie is a language", 12, "...") # "Frankie is a..."
slugify("Hello World!")                  # "hello-world"
word_wrap("The quick brown fox", 12)     # "The quick\nbrown fox"
indent_lines("a\nb\nc", 4)              # "    a\n    b\n    c"

# .sum do — projected sum in one step (was broken before)
cart = [{price: 0.99, qty: 4}, {price: 2.49, qty: 2}]
total = cart.sum do |item|
  item["price"] * item["qty"]
end
puts total   # 8.94

# .flat_map do — multi-line block bodies now work
groups = [["ruby", "scripting"], ["frankie", "fun"]]
all = groups.flat_map do |g|
  g
end
puts all   # [ruby, scripting, frankie, fun]

# assert_approx_eq — float testing
assert_approx_eq(sqrt(2.0), 1.4142, 0.0001, "sqrt(2)")
assert_approx_eq(0.1 + 0.2, 0.3, "float addition")   # default delta 0.001
run_tests()   # now callable from any .fk file

# Cookie-backed session — zero server state
app = web_app()
app.get("/counter") do |req|
  resp = response("")
  s = session(req, resp)
  s["count"] = (s["count"] or 0) + 1
  s.save()
  html_response("Visits: #{s["count"]}")
end
app.run()
```
---

## v1.13 Highlights

```ruby
# stitch — zero-dependency package system
stitch "frankieforms"
stitch "frankietable"
stitch "frankiecolor"
stitch "frankiepager"
stitch "frankieconfig"

# Form validation
rules = {email: [{rule: "required"}, {rule: "email"}]}
puts valid?({email: "alice@example.com"}, rules)  # true
validate({email: "bad"}, rules)   # {email: "must be a valid email address"}

# ASCII tables
puts table([{name: "Alice", score: 95}, {name: "Bob", score: 87}])
# +-------+-------+
# | name  | score |
# +-------+-------+
# | Alice | 95    |
# | Bob   | 87    |
# +-------+-------+

# Terminal colors
puts red("Error!")
puts green("Done!")
puts success("All tests passed")

# Pagination
pg = paginate({total: 247, page: 3, per_page: 20})
puts "#{pg["from"]}–#{pg["to"]} of #{pg["total"]}"   # 41–60 of 247

# Layered config
config = load_config({defaults: {host: "localhost", port: 3000}})
puts config["host"]   # APP_HOST env → "localhost"

# ? in user-defined function names — now works
def even?(n)
  n % 2 == 0
end
puts even?(4)   # true
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
frankiec bundle <file.fk> [-o out.py]  # bundle into ONE self-contained .py
frankiec check [--strict] <file.fk|dir>   # syntax check + static analysis
frankiec test  [file.fk] [--filter <name>] [--tag <tag>]   # run test suite
frankiec fmt   [--write] [--check] <file.fk|dir>   # auto-format
frankiec docs  [--output out.md] <file.fk>     # generate docs
frankiec stitch install <name> [--global]      # install a stitch (writes stitch.lock)
frankiec stitch list        # list installed + available stitches
frankiec stitch verify      # check stitches against stitch.lock
frankiec stitch update      # re-fetch + re-pin stitches
frankiec lsp                # start the Language Server (LSP over stdio)
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
| `docs/06_changelog.md` | v1.0 – v1.13.1 release notes |
| `docs/07_database.md` | SQLite database access — full API reference |
| `docs/08_v17_features.md` | v1.4–v1.7 feature reference: nil safety, templates, file system, typed asserts, web server, randomness, constants, compound assignment |
| `docs/09_web.md` | Web server — routes, requests, responses, filters |
| `docs/10_v18_features.md` | v1.8 feature reference: lambdas, hash merge `\|`, group_by, each_slice, each_cons |
| `docs/11_v19_features.md` | v1.9 feature reference: records, dig, zip, fmt, docs, readline REPL, .env loader |
| `docs/12_v110_features.md` | v1.10 feature reference: string/vector *, heredoc, times(), flatten(depth), map_with_index, pp, encode/decode |
| `docs/13_v111_features.md` | v1.11 feature reference: implicit return, inline if, .replace(), .format(hash), .zip_with, multiple return values |
| `docs/14_v112_features.md` | v1.12 feature reference: gsub block, map_hash, round, product, chars, FileNotFoundError, assert_match/nil, watch, --no-banner |
| `docs/15_v113_features.md` | v1.13 feature reference: stitch keyword, frankieforms, frankietable, frankiecolor, frankiepager, frankieconfig, ? in function names |
| `docs/16_v1131_features.md` | v1.13.1 feature reference: frankiestring v2, .sum do / .flat_map do fixes, assert_approx_eq, run_tests(), session(req,resp), fmt improvements |
| `docs/17_v114_features.md` | v1.14 feature reference: spawn, timeout, async routes, middleware, static files, frankietemplate, frankiecookie, hash destructuring, shape matching |
| `docs/18_v115_features.md` | v1.15 feature reference: ternary, keyword defaults, splat multi-assign, const, fn.(args), json_encode, base64, hmac, String#format, path helpers, date arithmetic, frankieauth, frankieratelimit, frankiec check/new |

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
├── examples/              ← example .fk programs (incl. webapp.fk, whats_new_v16.fk … whats_new_v114.fk)
├── stitches/              ← official starter stitches (frankieforms, frankietable, frankiecolor, frankiepager, frankieconfig, frankiestring, frankietemplate, frankiecookie)
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
