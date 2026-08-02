# 🏓 Frankie Pong

Two browsers, one ball. Every tab that opens the game becomes a player —
that's `frankiecanvas` multiplayer, and it costs zero extra code.

## Play

```bash
frankiec run main.fk        # → open http://localhost:4300 in TWO tabs
```

Tab 1 is the left paddle, tab 2 the right (send the link to a friend on
your network for proper trash talk). ↑ ↓ move · first to 5 · `r` rematch.
Playing solo? The right paddle plays itself.

## Ship

```bash
frankiec bundle main.fk -o pong.py
python3 pong.py
```

## CI / headless

`PONG_TICKS=120 frankiec run main.fk` runs a bounded simulation; the test
suite connects two scripted WebSocket clients and moves both paddles.

## The multiplayer trick

`on_player_key(g) do |game, player, key| ... end` — the canvas renderer
tags every key event with the connecting browser's player number (1, 2,
3…). Routing input per player is one conditional.
