# Frankie v1.20.0 — "It's Alive… and Playing" 🎮🧟

Frankie learns to play. Two pygame-flavored game engines with **one shared API** — write your game once, pick the renderer with a single stitch line. Zero external dependencies, as always.

**`frankiegame` (terminal):** fixed-timestep loop, raw arrow keys (stdlib `termios`), flicker-free double-buffered ANSI rendering, named colors, multi-line sprites with transparency, AABB collision, and a `q`-to-quit default. Headless-safe: without a tty the engine no-ops and `max_ticks:` bounds the loop — your test suite literally plays the game.

**`frankiecanvas` (browser):** the same API on an HTML5 canvas, served by Frankie's own web server with frames streamed over WebSockets. Canvas extras: cell-unit `rect`s, mouse clicks, WebAudio `game_beep`, and `on_player_key` — every browser tab is a player, so multiplayer costs zero extra code.

**Terminal primitives in the stdlib** (useful for any TUI): `term_raw_on/off`, non-blocking `term_key` with arrow mapping, `term_size`, cursor hide/show, `term_clear`, single-write `term_render`, `clock_ms`, `beep`.

**Showcase games** in `examples/projects/`, each with a pinned `stitch.lock`, headless CI modes, and one-file `frankiec bundle` output: 🐍 **Snake** (terminal, the whole API in ~80 lines), 🧟 **Zombie Invaders** (browser waves-and-shots), and 🏓 **Pong** (browser multiplayer — two tabs, one ball; solo mode plays a tiny AI).

**Tooling:** `frankiec new --game mygame` scaffolds a playable starter with the engine pre-installed and lockfile-pinned.

**Fixes:** blocks whose single statement is an assignment or postfix conditional now compile correctly across all block forms — a latent codegen gap the engines flushed out.
