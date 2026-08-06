# Frankie v1.21 — "The Book Edition"

Frankie's last feature release for a while: real bitmap sprites and a proper
synth API for `frankiecanvas`, a new binary-safe file primitive underneath
both, and a language freeze while the language gets a book written about it.
Pure Python stdlib, as always: **zero external dependencies**.

---

## 1. Image sprites — real PNGs in `frankiecanvas`

```ruby
stitch "frankiecanvas"

zombie = load_image("zombie.png")     # read once, outside the game loop

on_tick(g) do |game|
  clear(game)
  draw_image(game, 10, 4, zombie, w: 2, h: 2)   # cell coordinates, like draw
end
```

- `load_image(path)` reads a PNG/JPEG/GIF file and returns `{src: "data:image/...;base64,..."}`.
  Call it once before `run_game`, not per frame — it hits disk.
- `draw_image(g, x, y, image, w:, h:)` places the image at cell `(x, y)`,
  sized `w × h` cells (default `1×1`). Every connected browser decodes and
  caches the image the first time it's drawn; later frames just resend
  coordinates.
- `frankiegame` (terminal) gained a matching `load_image`/`draw_image` for
  API parity — since a tty can't show real pixels, `draw_image` there
  renders a `▒` placeholder block instead. Same function calls work
  against either engine.

---

## 2. WebAudio synth — real tones, not just a beep

```ruby
synth_play(g, freq: 220, wave: "sawtooth", dur: 0.2, gain: 0.08)
```

- `synth_play(g, freq:, wave:, dur:, gain:)` plays a WebAudio oscillator
  tone in every connected browser. `wave` is `"sine"`, `"square"`,
  `"sawtooth"`, or `"triangle"`. Defaults: `440`, `"sine"`, `0.08`s, `0.06`.
- `game_beep(g)` still works — it's now a thin wrapper over `synth_play`
  with the original beep settings (`520`Hz square, `0.07`s).
- `frankiegame` (terminal) gained `synth_play` too, mapped to the terminal
  bell — parameters accepted but ignored, so cross-engine code compiles
  either way.

---

## 3. `file_read_base64` — the stdlib primitive underneath it all

```ruby
data = file_read_base64("sprite.png")
```

`file_read` is text-mode and corrupts binary data. `file_read_base64`
reads a file as raw bytes and returns it Base64-encoded — this is what
`load_image` uses internally, and it's generally useful for any binary
file (images, audio, zips) you want to embed or ship as text.

---

## 4. Fixed: `frankiec fmt` silently dropping code

A single-statement block whose body was an assignment or a postfix
`if`/`unless` — e.g. `game["shots"].each do |s| hit = true if collide?(...) end` —
formatted to `do |s| nil end`, discarding the actual logic. Root cause:
`_is_stmt_only()` in `frankie_fmt.py` didn't recognize `Assign`, `PostfixIf`,
and several other statement node types, so the one-line inline path tried
to render them as expressions and silently fell back to `nil`. Fixed by
teaching the formatter to fall back to the (safe) multi-line block form for
every statement kind it can't inline. Verified by comparing compiled Python
output before and after reformatting — byte-identical.

If you've run `frankiec fmt --write` on code containing this pattern before
v1.21, it's worth a diff review — this is the kind of bug you want caught
before it ships in a book, not after.

---

## 5. 🧊 Frankie is frozen

v1.21 is the last planned feature release for a while: Blag is writing
**The Book of Frankie**, and it's being written against this exact
version. Language grammar, stdlib signatures, and stitch APIs are locked —
bug fixes and documentation corrections continue as patch releases, but no
new syntax or behavior changes until the freeze lifts. See `CLAUDE.md` for
the freeze policy.

---

## Compatibility notes

Fully backward compatible. `game_beep` behaves identically to v1.20. No
existing function signatures changed — `synth_play` and `draw_image` are
additive on both stitches.
