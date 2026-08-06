# 🧟 Zombie Invaders

Space Invaders, Frankenstein edition — real pixels in your browser, zero
dependencies. Built on the `frankiecanvas` stitch: an HTML5 canvas served
by Frankie's own web server, frames streamed over WebSockets. v1.21 swapped
the 🧟 emoji for an actual PNG sprite (`assets/zombie.png`, drawn via
`load_image`/`draw_image`) and upgraded the beeps to `synth_play` tones.

## Play

```bash
frankiec run main.fk        # → open http://localhost:4200
```

← → move · space shoots · clear the wave, the next one shambles faster ·
`r` restarts after the horde wins.

## Ship

```bash
frankiec bundle main.fk -o zombie_invaders.py
python3 zombie_invaders.py     # anywhere — no Frankie needed
```

## CI / headless

`INVADERS_TICKS=100 frankiec run main.fk` simulates 100 frames without a
browser. The test suite plays it with a scripted WebSocket client.

## Same API, two renderers

This game uses the shared engine API (`game_new` / `on_key` / `on_tick` /
`draw` / `text` / `collide?` / `run_game`) plus canvas extras (`rect`,
per-player input). Swap the stitch for `frankiegame` and the same calls
still work: `draw_image` falls back to a `▒` placeholder block (no real
pixels in a terminal) and `synth_play`/`game_beep` ring the terminal bell
instead of playing a WebAudio tone.
