# Frankie v1.18.0 — "From projects to products" 🧟

v1.17 made big programs safe to write; v1.18 makes them pleasant to edit, easy to ship, and live. Zero external dependencies, as always.

**Edit:** `frankiec lsp` is a full Language Server (pure Python stdlib) — live diagnostics from the static analyzer, completion with signatures and docs, and hover cards that surface your `##` doc-comments. The VS Code extension now launches it automatically; Neovim/Helix/Zed setups are documented.

**Ship:** `frankiec bundle app.fk -o app.py` compiles your program plus every `require`/`import`/`stitch` into ONE self-contained `.py` with the stdlib inlined — `python3 app.py` runs anywhere, no Frankie installation needed.

**Connect:** WebSockets on the built-in web server — `app.websocket("/ws/:room") do |ws| ... end` with hand-rolled RFC 6455 (handshake, framing, ping/pong), plus a `ws_connect` client.

**Debug:** drop `breakpoint` anywhere to pause into a scoped REPL — `vars`, `where`, evaluate any Frankie expression against the paused scope, `c` to resume. Skips politely when stdin isn't a terminal, so CI never hangs.

**Language:** `enum Status(pending, active, done)` for named symbolic values; `benchmark "label" do ... end` returns elapsed milliseconds; vector set operations `.union` / `.intersect` / `.difference`; numeric literals with underscores (`1_000_000`) and scientific notation (`2.5e-3`).

**Tooling:** `frankiec check .` and `fmt --write .` sweep whole projects; stitch installs are pinned in `stitch.lock` with `frankiec stitch verify` (CI-ready) and `update`.

**Fixes:** formatter parenthesization around indexed expressions, formatter floats always re-lexable, and `loop`/`spawn` now valid at the end of route handlers.
