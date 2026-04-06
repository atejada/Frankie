# Modules

## Splitting Code Across Files

As programs grow, splitting them across multiple `.fk` files keeps things manageable. Use `require` to load another file.

```ruby
require "utils"          # loads utils.fk
require "lib/helpers"    # loads lib/helpers.fk
require "lib/math"       # loads lib/math.fk
```

The `.fk` extension is optional. Paths are resolved relative to the current working directory.

---

## How `require` Works

When you `require` a file, Frankie loads and executes it in the current scope. Everything defined in that file — functions, constants, records — becomes available to the file that required it.

```ruby
# lib/math_utils.fk
PI = 3.14159265358979

def circle_area(r)
  PI * r * r
end

def circle_perimeter(r)
  2 * PI * r
end
```

```ruby
# main.fk
require "lib/math_utils"

puts circle_area(5)        # 78.539...
puts circle_perimeter(5)   # 31.415...
puts PI                    # 3.14159265358979
```

Each file is loaded **at most once** — calling `require` on the same file multiple times has no effect after the first load.

---

## Recommended Project Structure

For anything beyond a single script, use `frankiec new` to scaffold a standard layout:

```bash
frankiec new myapp
```

This creates:

```
myapp/
├── main.fk          ← entry point
├── test.fk          ← test suite
├── lib/
│   └── utils.fk     ← reusable functions
├── data/            ← JSON, CSV, SQLite files
├── .env.example     ← environment variable template
├── .gitignore
└── README.md
```

A typical `main.fk` requiring several modules:

```ruby
require "lib/config"
require "lib/database"
require "lib/routes"
require "lib/helpers"

db = db_open(env("DB_PATH", ":memory:"))
app = web_app()

setup_routes(app, db)
app.run(3000)
```

---

## Conventions

**One concern per file.** A file should do one thing — math utilities, database helpers, route definitions. Keep files focused and short.

**Put reusable code in `lib/`**. Anything that could be used by both `main.fk` and `test.fk` belongs in a lib file.

**Load order matters.** If `lib/routes.fk` uses functions from `lib/helpers.fk`, require helpers first:

```ruby
require "lib/helpers"   # must come first
require "lib/routes"    # can now use helpers
```

**Constants and records defined in any required file are global.** There are no namespaces — keep names descriptive enough to avoid collisions.

---

## Testing Across Files

`frankiec test` runs your test suite. A typical `test.fk` requires the same lib files as `main.fk`:

```ruby
# test.fk
require "lib/math_utils"
require "lib/helpers"

describe "circle_area" do
  assert_eq(round(circle_area(1), 4), 3.1416, "unit circle area")
  assert_eq(round(circle_area(0), 2), 0.0,    "zero radius")
end

describe "helpers" do
  assert_eq(clamp(150, 0, 100), 100, "clamp above max")
  assert_eq(clamp(-5,  0, 100), 0,   "clamp below min")
end
```

Run it with:

```bash
frankiec test test.fk
```

Or just `frankiec test` if your test file is named `test.fk` in the current directory.

---

## Environment Variables

`.env` files in the project root are loaded automatically at startup. Use them to keep secrets and configuration out of source code.

```bash
# .env
DB_PATH=data/app.db
API_KEY=your_key_here
DEBUG=false
```

```ruby
# main.fk — .env is already loaded
db_path = env("DB_PATH", ":memory:")
api_key = env("API_KEY")
debug   = env("DEBUG", "false")

puts "Connecting to #{db_path}"
```

`env(key, default)` returns the default if the variable is not set. `env(key)` with no default returns `nil` if missing.
