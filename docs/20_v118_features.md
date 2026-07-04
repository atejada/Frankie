# Frankie v1.18 — "From projects to products"

v1.17 made big programs safe to write. v1.18 makes them pleasant to edit
(LSP), easy to ship (bundle), live (WebSockets), and debuggable
(breakpoint). Pure Python stdlib underneath — **zero external
dependencies**, as always.

---

## 1. Language Server — `frankiec lsp`

Frankie now speaks the Language Server Protocol over stdio, built directly
on the v1.17 static analyzer:

- **Live diagnostics** — undefined names, wrong argument counts, unused
  variables, lex/parse errors — as you type.
- **Completion** — stdlib functions (with signatures + docs), your own
  functions, records, enums, and keywords.
- **Hover** — signatures and documentation; `##` doc-comments above your
  `def`s show up in hover cards.

### VS Code

The extension in `editors/vscode/` now launches the server automatically:

```bash
cd editors/vscode
npm install          # pulls the standard LSP client glue
npx vsce package     # build the .vsix, then install it
```

Set `frankie.lspCommand` in settings if `frankiec` isn't on your PATH.

### Neovim (0.10+)

```lua
vim.filetype.add({ extension = { fk = "frankie" } })
vim.api.nvim_create_autocmd("FileType", {
  pattern = "frankie",
  callback = function()
    vim.lsp.start({ name = "frankie", cmd = { "frankiec", "lsp" } })
  end,
})
```

### Helix (`languages.toml`)

```toml
[language-server.frankie]
command = "frankiec"
args = ["lsp"]

[[language]]
name = "frankie"
scope = "source.frankie"
file-types = ["fk"]
language-servers = ["frankie"]
```

---

## 2. `frankiec bundle` — one-file distribution

```bash
frankiec bundle app.fk -o app.py
python3 app.py        # anywhere Python 3.8+ exists — no Frankie needed
```

The bundle inlines the entire Frankie stdlib and **pre-compiles every
statically referenced file** — `require`, `import` and `stitch` targets,
recursively. At runtime they resolve from an embedded registry instead of
the filesystem. Dynamic paths (computed at runtime) can't be bundled and
produce a warning.

Write a tool, hand someone a single file. That's the whole story.

---

## 3. WebSockets

Hand-rolled RFC 6455 on the built-in web server — handshake, framing,
ping/pong, clean close. Server side:

```ruby
app = web_app()

app.websocket("/ws/:room") do |ws|
  ws.send("welcome to #{ws.params["room"]}")
  loop do
    msg = ws.recv()
    break if msg == nil      # client closed
    ws.send("echo: #{msg}")
  end
end

app.run(3000)
```

Client side:

```ruby
sock = ws_connect("ws://localhost:3000/ws/lobby", timeout: 5)
sock.send("hello")
puts sock.recv()
sock.close()
```

Each connection runs the handler in its own thread and closes
automatically when the handler returns. `recv()` answers pings for you and
returns `nil` when the peer disconnects. (`ws://` only — TLS stays on the
wish list.)

---

## 4. `breakpoint` — debugger-lite

Drop `breakpoint` anywhere. When execution reaches it in a terminal, the
program pauses into a scoped REPL:

```
🧟 breakpoint — pricing.fk:12
   ──▶ 12 │   breakpoint
   (c)ontinue · vars · where · exit · or type any Frankie expression

(fkdb) vars
  qty = 10
  total = 45.0
(fkdb) total * 2
  => 90.0
(fkdb) c
```

- `vars` lists local variables, `where` shows the location, `exit` aborts.
- Anything else is evaluated as a Frankie expression against the paused
  scope.
- When stdin isn't a terminal (CI, pipes), breakpoints print a notice and
  are skipped — your test runs never hang.
- `breakpoint if qty > 100` works (postfix conditions).

---

## 5. `enum` — named symbolic values

```ruby
enum Status(pending, active, done)

puts Status.pending            # pending
puts Status.values             # [pending, active, done]
puts Status.include?("done")   # true

case order_state
when Status.active
  ship_it()
end
```

Contextual keyword — variables named `enum` keep working, just like
`error`, `import` and `test`.

---

## 6. `benchmark` — friendly timing

```ruby
ms = benchmark "crunch" do
  heavy_work()
end
# ⏱  crunch: 132.4ms

benchmark do        # label optional
  quick_thing()
end
```

Returns the elapsed milliseconds, so you can assert on it in tests or
collect timings in a vector.

---

## 7. Set operations on vectors

```ruby
[1, 2, 3].union([3, 4, 5])       # [1, 2, 3, 4, 5]
[1, 2, 3].intersect([2, 3, 9])   # [2, 3]
[1, 2, 3].difference([2])        # [1, 3]
```

Order-preserving and deduplicating — they behave like tidy vector
operations, not mathematical sets that scramble your data.

---

## 8. Numeric literals: underscores + scientific notation

```ruby
budget  = 1_250_000
avogadro = 6.022e23
tiny     = 2.5e-3
pi_ish   = 3.141_592
```

---

## 9. Project-wide tooling

`check` and `fmt` now accept directories and recurse into `.fk` files:

```bash
frankiec check .              # analyze the whole project
frankiec check --strict src   # CI mode — warnings fail too
frankiec fmt --check .        # formatting gate
frankiec fmt --write .        # fix everything in place
```

---

## 10. Stitch lockfile

Installing a stitch now pins it in `stitch.lock` (sha256, source, size,
date). Commit the lockfile and your builds are reproducible:

```bash
frankiec stitch install frankiecolor   # writes/updates stitch.lock
frankiec stitch verify                 # ✓ pinned · ⚠ modified · ✗ missing
frankiec stitch update                 # re-fetch everything + re-pin
frankiec stitch update frankiecolor    # or just one
```

`verify` exits 1 on problems — drop it straight into CI. Global installs
(`--global`) don't touch the lockfile.

---

## Compatibility notes

- `enum`, `benchmark` and `breakpoint` are **contextual keywords** —
  they only act specially in their own statement shape, so variables with
  those names keep working.
- The formatter now parenthesizes correctly around indexed expressions
  (`(a | b)["x"]`) and emits floats the lexer can always re-read.
- `loop`, `spawn` and friends are now valid as the last statement of a
  web route handler.
