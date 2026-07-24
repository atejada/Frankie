# Frankie v1.19.0 — "Under the microscope" 🔬🧟

v1.18 made programs easy to ship; v1.19 makes them easy to **trust**. Zero external dependencies, as always.

**Types:** gradual type annotations — `def area(r: Float) -> Float`. Optional everywhere, zero runtime cost; argument types, return flow and simple local inference are checked by `frankiec check`, in CI, and live in your editor through the LSP. `Int` flows into `Float`, keyword defaults coexist untouched.

**Stepping:** `breakpoint` grew into a real debugger — `s`/`step`, `n`/`next`, `stack`, `vars`, and expression evaluation at the `(fkdb)` prompt, plus `frankiec run --debug` to break at the first line. Line-accurate everywhere via the compiler's line maps.

**Coverage:** `frankiec test --coverage` prints per-file percentages with missing-line ranges mapped back to `.fk` source, and writes `.frankie_coverage.json` — which the LSP reads to mark uncovered lines as editor hints.

**Networking:** TLS clients (`wss://` WebSockets and `tcp_connect(..., tls: true)` via stdlib `ssl`) and UDP sockets (`udp_listen` / `udp_send`).

**Tooling:** `frankiec stitch install <url>` installs from any raw URL (lockfile-pinned), and `frankiec docs --html` renders `##` doc-comments into a styled single-page HTML.

**Showcase:** three complete programs in `examples/projects/`, featured in the website's new "Built with Frankie" section — 🧟 **Zombie Chat** (multi-room WebSocket chat, server + web UI in one file), ⚡ **Word Reanimator** (multiplayer hangman where misses assemble the zombie), and 💰 **Frankie Ledger** (terminal expense tracker: SQLite, lockfile-pinned stitches, R-style stats with outlier detection). Each is a single `.fk` file, each ships as one `.py` via `frankiec bundle`.

**Fixes:** the formatter round-trips `return x if cond` correctly, `_fk_to_str` no longer misreads class objects, the debugger REPL survives its own errors, and the website's language-comparison tabs work again.
