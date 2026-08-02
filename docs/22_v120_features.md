# Frankie v1.20 — "It's Alive… and Playing"

Frankie learns to play: two pygame-flavored game engines with **one shared
API** — one renders in the terminal, one in the browser — plus three
playable showcase games. Pure Python stdlib underneath: **zero external
dependencies**, as always.

---

## 1. The shared engine API

Write your game once against this API; the stitch line picks the renderer:

```ruby
stitch "frankiegame"      # …or "frankiecanvas" — that's the whole switch

g = game_new(width: 32, height: 18, fps: 15)

on_key(g, "left") do |game|            # arrows, space, enter, esc, a–z…
  game["px"] -= 1
end

on_tick(g) do |game|                   # called once per frame
  clear(game)
  draw(game, game["px"], 10, "🧟", color: "green")
  draw_sprite(game, 4, 2, sprite)      # multi-line; spaces are transparent
  text(game, 1, 0, "score #{game["score"]}", color: "yellow")
  game_beep(game) if game["hit"]
end

run_game(g)                            # fixed-timestep blocking loop
```

Also shared: `on_any_key`, `stop_game`, `collide?` (AABB), `render_frame`
(the buffer as a string — great for tests), and `max_ticks:` to bound the
loop for CI. The game state is just a hash — stash whatever you like in it.

---

## 2. `frankiegame` — the terminal renderer

- Raw keyboard mode (no Enter needed) via stdlib `termios`, with arrows
  mapped to `"up"/"down"/"left"/"right"`; `q` quits by default.
- Double-buffered ANSI rendering: each frame is one write — flicker-free.
- 8 named colors (`GAME_COLORS`), background char, sprites, collision.
- **Headless-safe**: without a tty, input and rendering no-op — your test
  suite can literally play the game (`max_ticks` + `render_frame`).

New stdlib primitives underneath (useful for any TUI, not just games):
`term_raw_on/off`, `term_key`, `term_size`, `term_hide_cursor` /
`term_show_cursor`, `term_clear`, `term_render`, `clock_ms`, `beep`.

---

## 3. `frankiecanvas` — the browser renderer

Same API, real pixels: Frankie serves an HTML5 canvas page from its own
web server and streams draw ops over WebSockets (~20–30 fps). Key and
mouse events stream back with the **same key names** as the terminal.

Canvas extras:

```ruby
rect(g, x, y, w, h, "green")             # filled rects in cell units
on_player_key(g) do |game, player, key|  # every browser tab is a player
  move_paddle(game, player, key)
end
puts players_count(g)                    # connected browsers
game_beep(g)                             # WebAudio blip in every tab
```

Mouse clicks arrive as `"click:x,y"` through `on_any_key` /
`on_player_key`. Multiplayer costs zero extra code — that's the WebSocket
architecture from v1.18 doing its thing.

---

## 4. Showcase games

| Game | Renderer | The lesson |
|---|---|---|
| 🐍 `examples/projects/snake/` | terminal | the whole engine API in ~80 lines |
| 🧟 `examples/projects/zombie_invaders/` | browser | rects, sprites, waves, beeps |
| 🏓 `examples/projects/pong/` | browser | multiplayer via `on_player_key` — two tabs, one ball (solo vs. a tiny AI) |

Each ships its own pinned `stitches/` + `stitch.lock`, runs headless in CI
(`SNAKE_TICKS=40` etc.), and bundles to a single `.py` with
`frankiec bundle`.

---

## 5. `frankiec new --game`

```bash
frankiec new --game mygame
cd mygame && frankiec run main.fk
```

Scaffolds a playable starter (a zombie you steer with the arrows) with the
`frankiegame` stitch pre-installed and lockfile-pinned.

---

## Compatibility notes

- Engine functions live in stitches — nothing enters the global stdlib
  namespace unless you `stitch` an engine. Load ONE renderer per program.
- Blocks whose single statement is an assignment (`do |g| g["x"] = 1 end`)
  or a postfix conditional now compile correctly (previously a codegen
  error) — a fix the engines flushed out.
- Prefer single-width glyphs in the terminal renderer; emoji work but can
  wobble in some terminals.
