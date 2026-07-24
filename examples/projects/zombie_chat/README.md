# 🧟 Zombie Chat

A multi-room chat server **and** its web UI in one Frankie file — about 150
lines including the HTML. No frameworks, no npm, no dependencies. Just
Frankie's built-in web server and v1.18 WebSockets.

## Run it

```bash
frankiec run main.fk
```

Open http://localhost:4000 in **two browser tabs**, pick two names, and talk
to yourself. Rooms live in the URL hash: `http://localhost:4000/#graveyard`.

`PORT=5000 frankiec run main.fk` to change the port.

## Ship it

```bash
frankiec bundle main.fk -o zombie_chat.py
python3 zombie_chat.py        # runs anywhere — no Frankie needed
```

## How it works

- `app.get("/")` serves the entire UI from a single `<<~HTML` heredoc.
- `app.websocket("/ws/:room")` handles each client in its own thread:
  the **first message is your nickname**, everything after is chat.
- A plain hash (`room → members`) is the entire database. Joins, leaves
  and messages are broadcast as `json_encode`d events; an `enum` names the
  event types.

That's the whole architecture. Read `main.fk` top to bottom in one coffee.
