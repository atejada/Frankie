# Frankie v1.17 — "Programs that grow"

v1.17 is the release that takes Frankie from great-for-scripts to
safe-for-1000-line projects — without losing the simplicity. Everything
below is pure Python stdlib underneath: **zero external dependencies**,
as always.

---

## 1. Namespaced imports — `import "path" as name`

`require` merges everything into your scope — perfect for small scripts,
risky for big ones. `import` gives each file its own namespace:

```ruby
# lib/geometry.fk
PI = 3.14159265

def circle_area(r)
  PI * r * r
end
```

```ruby
# main.fk
import "lib/geometry" as geo

puts geo.circle_area(5)   # 78.539...
puts geo.PI               # 3.14159265
```

- The alias is optional: `import "lib/geometry"` defines `geometry`.
- Modules are cached — importing the same file twice returns the same module.
- `require` is unchanged and fully supported.

---

## 2. User-defined error types — `error`

```ruby
error TimeoutError
error ValidationError

def save_user(u)
  raise ValidationError, "email is required" unless u["email"]
end

begin
  save_user({name: "Blag"})
rescue ValidationError => e
  puts "Invalid: #{e}"
rescue TimeoutError => e
  puts "Too slow: #{e}"
end
```

- `raise TypeName, "message"` and `raise TypeName("message")` both work.
- Ruby-style `rescue TypeName => e` binding is new; the existing
  `rescue TypeName e` form still works.
- Typed errors are still caught by a generic `rescue e`.
- A typed `raise` auto-declares the type, so quick scripts can skip `error`.
- `assert_raises_typed(fn, "ValidationError")` knows your types.

---

## 3. First-class ranges

Ranges were already iterable; now they behave like proper values:

```ruby
r = 1..10
puts r                    # 1..10        (used to print range(1, 11))
puts r.to_vec             # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
puts r.include?(7)        # true
puts (1..10).step(3)      # [1, 4, 7, 10]
puts (1..4).sum           # 10
puts (1...4).to_vec       # [1, 2, 3]    (exclusive)

case score
when 90..100
  puts "A"
when 70..89
  puts "B"
end
```

`case/when` now tests **membership** for range values.

---

## 4. Record dot access

```ruby
record Point(x, y)
p1 = Point(3, 4)
puts p1.x        # 3  — previously required p1["x"]
puts p1.y        # 4
```

Hash-style access still works. The same mechanism powers module
constants (`geo.PI`) and zero-arg methods everywhere.

---

## 5. `parallel_map` — easy concurrency

Thread-pool map for I/O-bound work (HTTP calls, shell commands, file
reads). Results come back in input order; the first worker exception is
re-raised:

```ruby
pages = parallel_map(urls, workers: 8) do |u|
  http_get(u)
end
```

---

## 6. TCP sockets

```ruby
# Client
sock = tcp_connect("example.com", 7777, timeout: 5)
sock.send_line("ping")
puts sock.recv_line()
puts sock.peer()          # "93.184.216.34:7777"
sock.close()

# Manual server
server = tcp_listen(7777)
client = server.accept()

# Threaded server loop — one thread per client, auto-close
tcp_serve(7777) do |client|
  msg = client.recv_line()
  client.send_line("echo: #{msg}")
end
```

`send`/`recv(n)` for raw data, `send_line`/`recv_line` for line
protocols. `recv` returns `nil` when the peer closes.

---

## 7. Static analysis — `frankiec check`

`check` used to be syntax-only. It now finds real bugs before the
program runs:

```
$ frankiec check app.fk
  ✗  app.fk:11 — Undefined function: 'greeet'
  ✗  app.fk:9  — greet() expects 1..2 argument(s), got 3
  ⚠  app.fk:3  — Unused variable 'unused_thing' in function 'greet'

[Frankie] app.fk — 2 error(s), 1 warning(s)
```

- Undefined variables/functions and wrong argument counts are **errors**
  (exit 1); unused locals are **warnings**.
- `require`, `stitch` and `import` targets are resolved and analyzed, so
  multi-file programs check cleanly.
- Names inside string interpolation (`"#{typo}"`) are checked too.
- `--strict` makes warnings fail the build (CI mode).
- If a required file can't be resolved (dynamic path), undefined-name
  errors downgrade to warnings instead of guessing.

---

## 8. Accurate cross-file tracebacks

The compiler now records a precise line map for every compiled file —
main program, `require`d files, `import`s and stitches. Runtime errors
point at the right file *and* the right line:

```
╔══ Frankie Runtime Error ══════════════════════════════
║  Division by zero
║
║  File: /home/blag/app/lib/mathx.fk
║         7 │ def buggy(x)
║  ──▶    8 │   x / 0
║         9 │ end
╚═══════════════════════════════════════════════════════
```

---

## 9. Test groups, filtering, tags and stubs

```ruby
test "math basics" do
  assert_eq(1 + 1, 2, "addition works")
end

test "slow integration", tags: ["slow", "network"] do
  assert_true(http_get("http://localhost:3000/health")["ok"])
end

test "stubbing" do
  stub("shell", ->(cmd) { {ok: true, stdout: "fake", exit_code: 0} })
  assert_eq(shell("anything")["stdout"], "fake")
  unstub("shell")    # or unstub() to restore everything
end
```

```
frankiec test                    # run everything
frankiec test --filter math      # groups whose name contains "math"
frankiec test --tag slow         # groups tagged "slow"
```

Skipped groups are reported in the summary. `stub`/`unstub` swap any
global function (including `shell` and `http_get`) — perfect for testing
without side effects.

---

## 10. Stitch installer

```
frankiec stitch install frankiecolor            # → ./stitches/
frankiec stitch install frankiecache --global   # → ~/.frankie/stitches/
frankiec stitch list                            # installed + registry
```

Stitches are fetched straight from the Frankie GitHub repository using
the Python stdlib HTTP client. A package manager with no packaging.

---

## 11. REPL upgrades

```
fk> 2 + 3
=> 5
fk> _ * 10
=> 50
fk> help parallel_map
  parallel_map(vec, fn, workers=4)
    parallel_map(vec, workers: 4) do |x| ... end
    Runs the block across a thread pool...
```

- Bare expressions echo their value (`=>`), like Ruby's irb.
- `_` always holds the last echoed result.
- `help <function>` shows the signature and documentation of any stdlib
  or user-defined function.

---

## Compatibility notes

- `error`, `import` and `test` are **contextual keywords** — they only
  act specially in their statement position (`error TypeName`,
  `import "path"`, `test "name" do`). Variables named `error`, `import`
  or `test` keep working.
- Generated f-strings now avoid nested quotes, so compiled programs run
  on every supported Python (3.8+), not just 3.12+.
- `Integer#chr`, `String#hex` and `String#oct` are wired into codegen
  (previously stdlib-only).
