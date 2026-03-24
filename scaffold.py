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
puts "Built with Frankie v1.9 🧟"
'''

README_FK = """# {name}

A Frankie project.

## Run

```bash
frankiec run main.fk
```

## Project structure

```
{name}/
├── main.fk          # entry point
├── lib/             # reusable modules (require'd by main.fk)
├── data/            # data files (JSON, CSV, SQLite)
└── README.md
```
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


def scaffold(project_name: str):
    if os.path.exists(project_name):
        print(f"[Frankie] Error: directory '{project_name}' already exists.")
        sys.exit(1)

    dirs = [
        project_name,
        os.path.join(project_name, "lib"),
        os.path.join(project_name, "data"),
    ]

    files = {
        os.path.join(project_name, "main.fk"):          MAIN_FK.replace("{name}", project_name),
        os.path.join(project_name, "test.fk"):           TEST_FK.replace("{name}", project_name),
        os.path.join(project_name, "lib", "utils.fk"):   LIB_FK.replace("{name}", project_name),
        os.path.join(project_name, "README.md"):          README_FK.replace("{name}", project_name),
        os.path.join(project_name, ".gitignore"):         GITIGNORE,
        os.path.join(project_name, ".env.example"):       ENV_EXAMPLE,
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
    │   └── utils.fk   ← reusable utilities
    ├── data/          ← JSON, CSV, SQLite files
    ├── .gitignore
    ├── .env.example
    └── README.md

  Get started:
    cd {project_name}
    frankiec run main.fk
    frankiec repl
    frankiec run test.fk
""")
