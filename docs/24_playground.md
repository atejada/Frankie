# The Frankie Playground

Run Frankie in the browser, with nothing to install. The Playground is a
section of the Frankie website (`frankie_website.html`, anchor `#playground`):
an editor with syntax highlighting, an example picker, and **Run**, **Test**,
**Format**, **Stop** and **Share link** buttons.

It is **not a re-implementation**. The page runs the real compiler, standard
library, formatter, test runner and bundled stitches — the same files that
ship with `frankiec` — inside [Pyodide](https://pyodide.org) (CPython compiled
to WebAssembly). Error messages, line mapping and test output are identical
to a local install because `Run` calls `frankiec.run_file` and `Test` calls
`frankiec.run_tests`. Nothing is sent to a server: your code runs in a Web
Worker in your own tab.

## What you can do

| Button | What it does |
|--------|--------------|
| **Run** (`Ctrl/Cmd + Enter`) | Compile and run `main.fk`; output streams into the Output pane |
| **Test** | Run the `test "…" do … end` blocks with the built-in harness |
| **Format** | `frankiec fmt` — comments and parentheses are preserved (v1.22.3) |
| **Stop** | Kill the worker (a program running longer than 20 s is stopped automatically) |
| **Share link** | Copy a URL whose `#pg=…` fragment contains your (compressed) code |
| **Input (stdin)** | Lines fed to `input()`, `input_int()` and `input_float()` |

Shared links never auto-run: opening one loads the code into the editor and
waits for you to press Run.

## What does not work in a browser

Pyodide has no sockets, threads or real terminal, so these only work in a real
install: `web_app()` / `app.run`, `tcp_*` / `udp_*` / `ws_connect`, `http_*`
requests, `spawn` and `parallel_map`, the terminal engine `frankiegame` (use
`frankiecanvas` locally), `shell()`, and files that need to outlive the tab
(the in-browser filesystem resets on reload). A server program simply runs
until the 20-second timeout and is stopped with an explanatory message.

## How it is put together

```
frankie_website.html           editor UI + Web Worker (inlined, single file)
playground/
├── build_bundle.py            packs the toolchain into frankie_bundle.json
├── playground_runtime.py      ~70 lines of glue run inside Pyodide
└── frankie_bundle.json        GENERATED — compiler, stdlib, fmt, stitches
```

On first use (focusing the editor, choosing an example, or pressing Run) a
module Web Worker is started, which loads Pyodide from jsDelivr
(`pyodide.mjs`, about 7 MB over the wire, cached afterwards), downloads
`frankie_bundle.json` (about 120 KB gzipped), writes the files into Pyodide's
virtual filesystem under `/frankie`, and imports `playground_runtime`.

The page looks for the bundle at `playground/frankie_bundle.json` next to
itself and falls back to
`https://raw.githubusercontent.com/atejada/Frankie/main/playground/frankie_bundle.json`,
so the website works wherever it is hosted as long as the bundle is on `main`.

## Keeping it current

`frankie_bundle.json` is generated, but it is committed so the website works
straight from GitHub. **Regenerate it whenever the compiler, stdlib,
formatter or a stitch changes** (it is on the release checklist in
`CLAUDE.md`):

```bash
python3 playground/build_bundle.py            # rewrite the bundle
python3 playground/build_bundle.py --check    # exit 1 if it is stale (CI-friendly)
```

The Pyodide version is pinned in `frankie_website.html` (`PYODIDE_BASE`, two
places: the page script and the worker script). Bumping it means re-running
the examples against the new runtime — Pyodide 314 ships Python 3.14, and
Frankie's compiler is verified on it.

## Adding an example

Examples live in the `EXAMPLES` array in the page script
(`{id, title, cmd: "run"|"test", code, stdin?}`). Every example should run
clean in the Playground; keep them short and avoid anything from the list
above.
