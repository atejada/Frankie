"""
Frankie Project Scaffolder
Invoked via: frankiec new <project_name>
"""

import os
import sys

GITIGNORE = """# Frankie project
*.py
__pycache__/
*.db
.env
"""

MAIN_FK = '''# {name}/main.fk — entry point

puts "Hello from {name}!"
puts "Built with Frankie v1.15 🧟"
'''

README_FK = """# {name}

A Frankie project.

## Run

```bash
frankiec run main.fk
```

## Test

```bash
frankiec test
```

## Project structure

```
{name}/
├── main.fk          # entry point
├── test.fk          # test suite
├── lib/             # reusable modules (require'd by main.fk)
├── stitches/        # third-party Frankie packages (stitch'd by main.fk)
├── views/           # HTML templates (render_file'd by route handlers)
│   └── partials/    # reusable template fragments ({{> name}})
├── data/            # data files (JSON, CSV, SQLite)
├── public/          # static files served by app.static("./public")
└── README.md
```

## Packages (Stitches)

Third-party Frankie packages go in `stitches/`. Load them with:

```ruby
stitch "frankietemplate"
stitch "frankiecookie"
```

Official stitches are installed globally by `install.py` and available
in every project. Drop your own `.fk` files in `stitches/` to share
utilities across this project without publishing them globally.
"""

TEST_FK = '''# {name}/test.fk — test suite

puts "Running tests for {name}..."
puts ""

passed = 0
failed = 0

def assert_eq(label, got, expected)
  if got == expected
    puts "  ✓  #{label}"
    return true
  else
    puts "  ✗  #{label}"
    puts "       expected: #{expected}"
    puts "       got:      #{got}"
    return false
  end
end

# ── Your tests here ──────────────────────────────────────────────

# Example:
# require "lib/mymodule"
# result = assert_eq("add(2, 3) == 5", add(2, 3), 5)
# passed = passed + 1 if result
# failed = failed + 1 unless result

# ─────────────────────────────────────────────────────────────────
puts ""
puts "Tests: #{passed} passed, #{failed} failed"
'''

LIB_FK = '''# {name}/lib/utils.fk — utility functions

def hello(name="World")
  return "Hello, #{name}!"
end
'''

ENV_EXAMPLE = """# .env.example — copy to .env and fill in your values
# DB_PATH=data/myapp.db
# API_KEY=your_key_here
"""



GAME_MAIN_FK = """# {name}/main.fk — a Frankie game! (frankiegame starter)
# Run:  frankiec run main.fk   ·   arrows move · q quits
# Docs: docs/22_v120_features.md — swap the stitch for "frankiecanvas"
# and the same code renders in a browser.

stitch "frankiegame"

const W = 32
const H = 18

g = game_new(width: W, height: H, fps: 15)
g["px"] = W // 2
g["py"] = H // 2
g["score"] = 0

on_key(g, "left") do |game|
  game["px"] = max(1, game["px"] - 1)
end
on_key(g, "right") do |game|
  game["px"] = min(W - 2, game["px"] + 1)
end
on_key(g, "up") do |game|
  game["py"] = max(1, game["py"] - 1)
end
on_key(g, "down") do |game|
  game["py"] = min(H - 2, game["py"] + 1)
end

on_tick(g) do |game|
  clear(game)
  text(game, 0, 0, "█" * W, color: "gray")
  text(game, 0, H - 1, "█" * W, color: "gray")
  draw(game, game["px"], game["py"], "🧟")
  text(game, 2, 0, " {name} — arrows move, q quits ", color: "green")
end

run_game(g)
puts "thanks for playing {name}!"
"""

def scaffold(project_name: str, game: bool = False):
    if os.path.exists(project_name):
        print(f"[Frankie] Error: directory '{project_name}' already exists.")
        sys.exit(1)

    dirs = [
        project_name,
        os.path.join(project_name, "lib"),
        os.path.join(project_name, "data"),
        os.path.join(project_name, "stitches"),
        os.path.join(project_name, "views"),
        os.path.join(project_name, "views", "partials"),
        os.path.join(project_name, "public"),
    ]

    STITCHES_README = """# Stitches

Third-party Frankie packages live here. Load them in your `.fk` files with:

    stitch "frankietemplate"
    stitch "frankiecookie"

Official stitches (frankieforms, frankietable, frankiecolor, frankiepager,
frankieconfig, frankiestring, frankietemplate, frankiecookie) are installed
globally by `install.py` and resolve from `~/.frankie/stitches/`.

Project-local stitches in this folder take priority over global ones —
drop a `.fk` file here to override or add project-specific packages.
"""

    files = {
        os.path.join(project_name, "main.fk"):                    (GAME_MAIN_FK if game else MAIN_FK).replace("{name}", project_name),
        os.path.join(project_name, "test.fk"):                    TEST_FK.replace("{name}", project_name),
        os.path.join(project_name, "lib", "utils.fk"):            LIB_FK.replace("{name}", project_name),
        os.path.join(project_name, "stitches", "README.md"):      STITCHES_README,
        os.path.join(project_name, "README.md"):                  README_FK.replace("{name}", project_name),
        os.path.join(project_name, ".gitignore"):                  GITIGNORE,
        os.path.join(project_name, ".env.example"):                ENV_EXAMPLE,
    }

    # Create directories
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # Write files
    for path, content in files.items():
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    print(f"""
  🧟 Created Frankie project: {project_name}/

  Structure:
    {project_name}/
    ├── main.fk        ← entry point
    ├── test.fk        ← test suite
    ├── lib/
    │   └── utils.fk   ← reusable utilities (require "lib/utils")
    ├── stitches/
    │   └── README.md  ← stitch convention explained
    ├── views/
    │   └── partials/  ← template fragments ({{> name}})
    ├── public/        ← static files (app.static("./public"))
    ├── data/          ← JSON, CSV, SQLite files
    ├── .gitignore
    ├── .env.example
    └── README.md

  Get started:
    cd {project_name}
    frankiec run main.fk
    frankiec repl
    frankiec test
""")
