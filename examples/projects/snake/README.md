# 🐍 Snake

The classic, in your terminal, in ~80 lines of Frankie — built on the
`frankiegame` stitch (v1.20): fixed-timestep loop, double-buffered ANSI
rendering, non-blocking arrow keys, zero dependencies.

## Play

```bash
frankiec run main.fk
```

Arrows steer · eat ● · don't eat yourself · `r` restarts · `q` quits.

## Ship

```bash
frankiec bundle main.fk -o snake.py
python3 snake.py               # anywhere with a terminal
```

## CI / headless

No tty? No problem — rendering and input no-op, and
`SNAKE_TICKS=40 frankiec run main.fk` simulates 40 frames and exits.
That's how the test suite plays Snake.

## The whole engine API in one game

`game_new` · `on_key` · `on_tick` · `clear` · `draw` · `text` ·
`draw_sprite` · `collide?` · `game_beep` · `run_game`. Swap
`stitch "frankiegame"` for `stitch "frankiecanvas"` and the same API
renders in a browser instead.
