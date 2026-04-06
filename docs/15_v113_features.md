# Frankie v1.13 — New Feature Reference

## Overview

v1.13 introduces **stitch** — Frankie's zero-dependency, zero-registry package system. Drop a `.fk` file in the right folder and stitch it in. Five official starter stitches ship with the release.

| Feature | Category | Summary |
|---|---|---|
| **`stitch "name"`** | language | Load a package by name — resolves from `./stitches/` then `~/.frankie/stitches/` |
| **`frankieforms`** | stitch | Form field validation — required, min/max length, email, numeric, pattern |
| **`frankietable`** | stitch | ASCII table rendering from a vector of hashes |
| **`frankiecolor`** | stitch | ANSI color helpers for terminal output |
| **`frankiepager`** | stitch | Pagination math — total pages, slicing, prev/next |
| **`frankieconfig`** | stitch | Layered config loading from defaults, JSON file, and env vars |
| **`?` in function names** | language | `def even?(n)` now works — `?` is mangled to `_q` in generated Python |

---

## The `stitch` Keyword

`stitch` loads a Frankie package by name. It resolves the file in two locations, in order:

1. `./stitches/<name>.fk` — project-local (checked first)
2. `~/.frankie/stitches/<name>.fk` — user-global

If neither exists, a clear error tells you exactly what to do:

```
╔══ Frankie Runtime Error ══════════════════════════════
║  [Frankie] Stitch not found: "frankiforms"
║    Put frankiforms.fk in ./stitches/ or ~/.frankie/stitches/
╚═══════════════════════════════════════════════════════
```

Each stitch is loaded **at most once** — calling `stitch "name"` multiple times in the same program is safe.

### Compared to `require`

| | `require` | `stitch` |
|---|---|---|
| Path | Explicit: `require "lib/utils"` | By name: `stitch "frankiforms"` |
| Resolution | Relative to cwd | `./stitches/` then `~/.frankie/stitches/` |
| Signals | Your own code | Third-party packages |
| Convention | `lib/` folder | `stitches/` folder |

They use the same underlying machinery — `stitch` is `require` with a conventional resolution path and a more meaningful name for the job.

### Project layout with stitches

```
myapp/
├── main.fk
├── test.fk
├── lib/
│   └── utils.fk        ← your own code, loaded with require
└── stitches/
    ├── frankieforms.fk   ← third-party, loaded with stitch
    └── frankietable.fk
```

Anyone cloning your repo immediately knows what `stitches/` contains.

---

## `frankieforms` — Form Validation

```ruby
stitch "frankieforms"

form  = {name: "Alice", email: "alice@example.com", age: "25"}
rules = {
  name:  [{rule: "required"}, {rule: "min_length", value: 2}],
  email: [{rule: "required"}, {rule: "email"}],
  age:   [{rule: "required"}, {rule: "min_value", value: 18}]
}

if valid?(form, rules)
  puts "All good!"
else
  validate(form, rules).each do |field, msg|
    puts "#{field}: #{msg}"
  end
end
```

### Available rules

| Rule | Options | Description |
|---|---|---|
| `"required"` | — | Value must be non-nil and non-empty |
| `"min_length"` | `value: n` | At least n characters |
| `"max_length"` | `value: n` | At most n characters |
| `"email"` | — | Must match `word@word.word` |
| `"min_value"` | `value: n` | Integer value ≥ n |
| `"max_value"` | `value: n` | Integer value ≤ n |
| `"numeric"` | — | Must be a number (int or float) |
| `"alpha"` | — | Letters only |
| `"matches_pattern"` | `value: pat`, `message: msg` | Must match regex pattern |

### Functions

`validate(form, rules)` — Returns a Hash of `{field: error_message}` pairs. Empty hash = all valid.

`valid?(form, rules)` — Returns `true` if no errors.

---

## `frankietable` — ASCII Tables

```ruby
stitch "frankitable"

rows = [
  {name: "Alice", dept: "Engineering", salary: 95000},
  {name: "Bob",   dept: "Marketing",   salary: 72000},
  {name: "Carol", dept: "Finance",     salary: 88000}
]

puts table(rows)
# +-------+-------------+--------+
# | name  | dept        | salary |
# +-------+-------------+--------+
# | Alice | Engineering | 95000  |
# | Bob   | Marketing   | 72000  |
# | Carol | Finance     | 88000  |
# +-------+-------------+--------+

# Specific columns only
puts table(rows, ["name", "salary"])
```

### Functions

`table(rows)` — Render all columns. Columns inferred from first row's keys.

`table(rows, cols)` — Render specific columns in the given order.

`table_print(rows, cols)` — Shorthand for `puts table(rows, cols)`.

---

## `frankiecolor` — Terminal Colors

```ruby
stitch "frankicolor"

puts red("Error: something failed")
puts green("Success: all tests passed")
puts yellow("Warning: disk space low")
puts blue("Info: connecting...")
puts bold("Important!")
puts underline("Click here")

# Semantic helpers
puts success("Build complete")   # ✓ in green
puts error("Build failed")       # ✗ in red
puts warn("Deprecated API")      # ⚠ in yellow
puts info("Server on port 3000") # ℹ in cyan

# Generic
puts colorize("hello", "magenta")
```

### Color functions

`black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white` — wrap a string in that ANSI color.

### Style functions

`bold`, `dim`, `italic`, `underline`, `inverse` — apply text styles.

### Utilities

`colorize(str, color_name)` — generic color by name string.

`strip_color(str)` — remove all ANSI escape codes (for writing colored output to a log file).

---

## `frankiepager` — Pagination

```ruby
stitch "frankipager"

pager = paginate({total: 247, page: 3, per_page: 20})

puts pager["page"]         # 3
puts pager["total_pages"]  # 13
puts pager["from"]         # 41
puts pager["to"]           # 60
puts pager["has_prev"]     # true
puts pager["has_next"]     # true
puts pager["prev_page"]    # 2
puts pager["next_page"]    # 4

# Slice a vector to the current page
items = seq(1, 247)
page_items = page_slice(items, 3, 20)
puts page_items   # [41, 42, 43, ... 60]
```

### Pager hash keys

| Key | Description |
|---|---|
| `page` | Current page (clamped to valid range) |
| `per_page` | Items per page |
| `total` | Total item count |
| `total_pages` | Total number of pages |
| `from` | First item number on this page |
| `to` | Last item number on this page |
| `has_prev` | True if there is a previous page |
| `has_next` | True if there is a next page |
| `prev_page` | Previous page number or nil |
| `next_page` | Next page number or nil |
| `first_page` | True if on the first page |
| `last_page` | True if on the last page |

### Functions

`paginate(opts)` — Compute pagination. Opts: `total`, `page`, `per_page`.

`page_slice(items, page, per_page)` — Return the slice of a vector for the given page.

`page_links(pager, url_template)` — Generate a vector of `{label, url, active}` hashes for navigation links. Use `{page}` in the template: `"/posts?page={page}"`.

---

## `frankieconfig` — Layered Config

```ruby
stitch "frankiconfig"

config = load_config({
  file:       "config.json",
  env_prefix: "APP",
  defaults:   {host: "localhost", port: 3000, debug: false}
})

puts config["host"]    # APP_HOST env → config.json → "localhost"
puts config["port"]    # APP_PORT env → config.json → 3000
puts config["debug"]   # APP_DEBUG env → config.json → false
```

Sources are merged in priority order: defaults → JSON file → env vars → overrides. Higher priority wins.

Type coercion is automatic — if the default is an Integer, the env var string is converted to Integer. Same for Float and Boolean.

### Functions

`load_config(opts)` — Load and merge config. Opts: `file`, `env_prefix`, `defaults`, `overrides`.

`config_get(config, key, fallback)` — Get a key with a fallback if missing.

---

## `?` in User-defined Function Names

Predicate functions can now use `?` in their names, just like Ruby:

```ruby
def even?(n)
  n % 2 == 0
end

def palindrome?(s)
  s == s.chars.reverse.join("")
end

puts even?(4)                # true
puts even?(3)                # false
puts palindrome?("racecar")  # true
puts palindrome?("frankie")  # false
```

Frankie compiles `?` to `_q` internally so the generated Python is valid. This is a transparent implementation detail — you just write `?` and it works.

---

## Writing Your Own Stitch

A stitch is any `.fk` file. Drop it in `./stitches/` and `stitch "name"` loads it.

```ruby
# stitches/myutils.fk

def slugify(s)
  s.downcase.gsub("[^a-z0-9]+", "-").strip
end

def truncate(s, n)
  if s.length <= n
    s
  else
    s[0...n] + "..."
  end
end
```

```ruby
# main.fk
stitch "myutils"

puts slugify("Hello World!")    # hello-world
puts truncate("Long string", 4) # Long...
```

### Conventions

- Prefix private helper functions with `_` to signal they're internal.
- Use `##` doc-comments for `frankiec docs` compatibility.
- Keep each stitch focused on one concern.
- Avoid redefining stdlib functions.
