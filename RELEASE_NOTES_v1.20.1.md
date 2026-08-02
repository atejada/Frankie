# Frankie v1.20.1 — patch release 🐍🍺

- **Arrow keys work in terminal games.** `term_key()` was reading from Python's buffered stdin, which swallowed the tail of arrow-key escape sequences — every arrow decoded as `esc`. It now reads raw bytes from the file descriptor. Snake finally obeys.
- **`frankiec examples [name]`** — list the bundled examples and showcase games, or copy one into the current directory ready to run (`frankiec examples snake && cd snake && frankiec run main.fk`). Works for brew, git-clone, and install.py installs alike.
- **Homebrew support** — official formula in `packaging/homebrew/`: `brew tap atejada/frankie && brew trust atejada/frankie && brew install frankie`. Standard stitches now also resolve from the installation directory, so brew installs work out of the box.
