# Frankie v1.19 — "Under the microscope"

v1.18 made programs easy to ship; v1.19 makes them easy to **trust**:
type annotations, a real stepping debugger, and test coverage — plus TLS,
UDP, and three showcase projects. Zero external dependencies, as always.

---

## 1. Gradual type annotations

```ruby
def area(r: Float) -> Float
  3.14159 * r * r
end

def clamp(x: Int, lo: Int, hi: Int) -> Int
  return lo if x < lo
  return hi if x > hi
  x
end

puts area(3)        # fine — Int flows into Float
puts area("five")   # ✗ area() argument 1 expects Float, got String
```

- **Optional everywhere.** Un-annotated code is completely untouched, and
  annotations cost nothing at runtime — they're checked statically by
  `frankiec check`, in CI, and live in your editor via the LSP.
- Type names: `Int`/`Integer`, `Float`/`Number`, `String`/`Str`,
  `Bool`/`Boolean`, `Vector`, `Hash`, `Lambda`, `Range`, `Nil`, `Any`.
- Return annotations are checked against every `return` and the implicit
  final expression; simple local inference follows literals, arithmetic,
  and calls to annotated functions.
- Coexists with keyword defaults: `def connect(host: String, port: 5432)`.

---

## 2. Full stepping debugger

`breakpoint` grew up. The `(fkdb)` prompt now understands:

```
(fkdb) s          # step — execute one line, stepping into calls
(fkdb) n          # next — one line, stepping over calls
(fkdb) stack      # the Frankie call stack, innermost first
(fkdb) vars       # local variables (clean — no stdlib noise)
(fkdb) total * 2  # evaluate any expression in the paused scope
(fkdb) c          # continue
```

And `frankiec run --debug app.fk` breaks at the very first line, so you
can step through a program you've never read. Line-accurate everywhere
thanks to the compiler's line maps — including inside `require`d files.

---

## 3. Test coverage

```
$ frankiec test examples/test.fk --coverage
╠══ Coverage ═══════════════════════════════════════════
║   87.5%  examples/test.fk  missing: 7
║  ── overall: 87.5% (7/8 lines)
```

- Percentages and missing-line ranges are mapped back to `.fk` source.
- Writes `.frankie_coverage.json` — and the **LSP reads it**: after a
  coverage run, uncovered lines show up as unobtrusive hints in your
  editor.

---

## 4. TLS clients + UDP sockets

```ruby
ws  = ws_connect("wss://echo.example.com/socket")     # TLS WebSockets
tls = tcp_connect("example.com", 443, tls: true)      # TLS TCP

sock = udp_listen(9999)
msg = sock.recv()                  # {data:, host:, port:}
sock.send_to(msg["host"], msg["port"], "pong")
udp_send("127.0.0.1", 9999, "ping")   # fire-and-forget
```

Certificate-verified via Python's stdlib `ssl`. Server-side TLS stays on
the wish list.

---

## 5. `frankiec docs --html`

Renders `##` doc-comments (with `@param` / `@return` / `@example`) into a
styled single-page HTML matching the website's dark-lab theme:

```
frankiec docs --html mystitch.fk --output mystitch.html
```

---

## 6. Stitch installs from any URL

```
frankiec stitch install https://example.com/stitches/foo.fk
```

Pinned in `stitch.lock` with the URL recorded as its source — `verify`
and `update` work exactly as with registry stitches.

---

## 7. Showcase projects

Three complete programs ship in `examples/projects/` — each a single
`.fk` file, each shippable as one `.py` via `frankiec bundle`:

| Project | What it shows |
|---|---|
| 🧟 `zombie_chat/` | Multi-room WebSocket chat — server + web UI in one file |
| ⚡ `word_reanimator/` | Multiplayer browser hangman — shared state over WebSockets |
| 💰 `frankie_ledger/` | Terminal expense tracker — SQLite, stitches + `stitch.lock`, R-style stats |

All three are featured in the "Built with Frankie" section of the website.

---

## Compatibility notes

- Annotations use the existing `name: value` parameter syntax — a bare
  reserved type name is an annotation, anything else is still a keyword
  default. No existing code changes meaning.
- The formatter now round-trips `return x if cond` and friends correctly
  (previously postfix statements could collapse to `nil`).
