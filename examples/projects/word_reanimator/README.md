# 🧟⚡ Word Reanimator

Multiplayer hangman, Frankenstein edition — in one Frankie file. Guess
letters **together** in the browser; every miss stitches another part onto
the zombie. Six misses and the word stays dead. Reveal everything and…
IT'S ALIVE!

## Play it

```bash
frankiec run main.fk
```

Open http://localhost:4001 in **two browser tabs** (or send the link to a
friend on your network). Everyone in the same room shares the same word,
the same zombie, and the same fate. Rooms live in the URL hash:
`http://localhost:4001/#morgue`.

## Ship it

```bash
frankiec bundle main.fk -o word_reanimator.py
python3 word_reanimator.py     # runs anywhere — no Frankie needed
```

## How it works

- The whole game state is one hash per room: `word`, `guessed`, `misses`,
  `players`, `phase` — with an `enum Phase(playing, reanimated, dead)`.
- `app.websocket("/ws/:room")` receives JSON actions (`guess` / `reset`)
  and broadcasts the full state back to every player after each move —
  the client just renders whatever arrives.
- Pure game logic lives in small testable functions (`apply_guess`,
  `masked_word`) — `.chars`, `.union`, `.include?` do the heavy lifting.
- The UI is a single `<<~HTML` heredoc: no frameworks, no build step.
