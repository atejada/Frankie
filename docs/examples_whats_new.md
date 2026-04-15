# What's New — Per Version

Each version of Frankie ships a runnable `whats_new_vX.fk` example file that demonstrates every new feature introduced in that release. Run any of them with:

```bash
frankiec run examples/whats_new_v114.fk
```

---

## v1.14 — `whats_new_v114.fk`

**Theme:** Frankie for real web apps — concurrency, templates, signed cookies, middleware, and two language upgrades that make data manipulation natural.

| Feature | Summary |
|---|---|
| `spawn { }` | Run a block in a background thread — returns immediately, zero boilerplate |
| `timeout(n) { }` | Kill a block that exceeds `n` seconds — raises `TimeoutError` |
| Async routes | `app.get_async` / `app.post_async` etc. — non-blocking handlers with `await` |
| Middleware stack | `app.use do \|req, next_fn\|` — chain auth, logging, rate-limiting |
| Static file serving | `app.static("./public")` — serve a directory in one line |
| `frankietemplate` | Mustache-compatible templates — `{{ var }}`, `{{# section }}`, `{{^ inverted }}`, `{{> partial }}` |
| `frankiecookie` | HMAC-signed cookies via Python's `hmac` stdlib — `set_signed_cookie` / `get_signed_cookie` |
| Hash destructuring | `{name, age} = user` — pull keys into variables directly |
| Shape pattern matching | `case user when {role: "admin"}` — match on hash structure, not just values |
| `frankiec new` scaffold | Generated project now includes `stitches/` and `views/partials/` folders |
| Global stitch install | `install.py` correctly copies all stitches to `~/.frankie/stitches/` |
| `page_links` full example | Complete web pagination with `frankiepager` + `frankietemplate` |

---

## v1.13.1 — `whats_new_v1131.fk`

**Theme:** Gap closers — no new syntax, everything real programs needed and didn't have.

| Feature | Summary |
|---|---|
| `frankiestring` v2 | Rewritten stitch: `pad_left`, `pad_right`, `truncate`, `slugify`, `word_wrap`, `indent_lines` — replaces clunky `lfill`/`rfill` API |
| `Vector .sum do \|x\|` | Block form now works — projected sum without a two-step `.map` + `sum` |
| `Vector .flat_map do \|x\|` | Multi-line block bodies now parse correctly |
| `assert_approx_eq(a, b, delta, msg)` | Float comparison in tests with configurable delta (default `0.001`) |
| `run_tests()` | Now a public stdlib function — callable from any `.fk` file, not just `frankiec test` |
| `session(req, resp)` | Cookie-backed session hash — read, mutate, `.save()`. Zero server state, single JSON cookie `_fk_session` |
| `frankiec fmt` blank lines | Intentional blank lines between statement groups inside function bodies now preserved |
| `frankiec fmt` multi-line threshold | Hashes/vectors whose inline form exceeds 60 chars auto-expand to one element per line |
| `frankiec fmt` idempotency | Running `fmt --write` twice now produces identical output — safe for pre-commit hooks and CI |
| Heredoc in `do...end` blocks | Fixed lexer bug — heredocs now work anywhere a string expression is valid |
| `Hash.each do \|k, v\|` | Two-parameter block iteration confirmed and end-to-end tested |
| Symbol key round-trip in `fmt` | `{host: "x"}` no longer becomes `{"host": "x"}` after formatting |

---

## v1.13 — `whats_new_v113.fk`

**Theme:** Stitches — a zero-dependency, zero-registry package system.

| Feature | Summary |
|---|---|
| `stitch "name"` keyword | Load a package by name — resolves from `./stitches/` then `~/.frankie/stitches/` |
| `frankieforms` | Form field validation — `required`, `min_length`, `max_length`, `email`, `numeric`, `alpha`, `matches_pattern` |
| `frankietable` | ASCII table rendering from a vector of hashes — `table(rows)` / `table(rows, cols)` |
| `frankiecolor` | ANSI color helpers — `red`, `green`, `yellow`, `bold`, `success`, `error`, `warn`, `info`, `colorize`, `strip_color` |
| `frankiepager` | Pagination math — `paginate(opts)`, `page_slice(items, page, per_page)`, `page_links(pager, url_template)` |
| `frankieconfig` | Layered config loading: defaults → JSON file → env vars → overrides, with type coercion |
| `frankiestring` | String utilities stitch (v1, superseded by v2 in v1.13.1) |
| `?` in function names | `def even?(n)` now works — `?` compiled transparently to `_q` in generated Python |

---

## v1.12 — `whats_new_v112.fk`

**Theme:** Filling stdlib gaps, fixing error handling, tooling polish.

| Feature | Summary |
|---|---|
| `String .gsub` with block | Transform each regex match via a block — `"hello".gsub("[aeiou]") do \|m\| m.upcase end` |
| `Hash .map_hash` | Transform a hash into a new hash — block returns `[new_key, new_value]` |
| `round(x, n)` | Round to n decimal places — `round(3.14159, 2)` → `3.14` |
| `Vector .product(other)` | Cartesian product — `[1,2].product([3,4])` → `[[1,3],[1,4],[2,3],[2,4]]` |
| `String .chars` | Promoted to first-class documented method — chains into iterators |
| `each_with_object` + Hash | Hash accumulator now explicitly documented and tested |
| `assert_match` / `assert_nil` | Two new test runner assertions |
| `rescue FileNotFoundError` | `file_read` and `file_lines` now raise the correct type |
| `frankiec watch` | Re-run on save — `frankiec watch main.fk` |
| `frankiec repl --no-banner` | Headless REPL for scripts and pipes |
| Friendlier runtime errors | Type errors now say "Integer and String", not Python internals |

---

## v1.11 — `whats_new_v111.fk` *(in docs/13_v111_features.md)*

**Theme:** Ergonomics — removing paper cuts, making the common case obvious.

| Feature | Summary |
|---|---|
| Implicit return | Last expression in a function is returned automatically |
| Inline `if` expression | `grade = if score >= 90 then "A" else "B" end` |
| `String .replace(old, new)` | The method new users always reach for first |
| `String .format(hash)` | `"Hello, {name}!".format({name: "Alice"})` |
| `.zip_with do \|a, b\|` | Pair-wise transform two vectors in one pass |
| Multiple return values | `lo, hi = min_max(data)` — destructuring from functions |
| `frankiec check` boxed errors | Parse errors now use the same box as runtime errors |
| REPL multi-line history | `↑` recalls a full `def...end` block |
| `frankiec fmt` heredoc support | Heredoc bodies preserved verbatim during formatting |
| `String .delete(chars)` | `"hello".delete("l")` → `"heo"` — documented |

---

## v1.10 — `whats_new_v110.fk`

**Theme:** Expressiveness — more ways to write less.

| Feature | Summary |
|---|---|
| `String * n` / `Vector * n` | `"ha" * 3` → `"hahaha"` · `[0] * 5` → `[0,0,0,0,0]` |
| Heredoc `<<~TEXT` | Multi-line strings with auto indent-stripping and interpolation |
| `times()` standalone | `times(5) do \|i\|` alongside `5.times do` |
| `flatten(depth)` | Flatten exactly n levels — `flatten(1)` vs deep `flatten` |
| `map_with_index` | `v.map_with_index do \|x, i\|` |
| `pp` — pretty print | `pp({host: "localhost", port: 3000})` |
| `encode` / `decode` | `"hi".encode` → `[104, 105]` · `[104, 105].decode` → `"hi"` |
| Exit codes | `exit(0)` / `exit(1)` — propagated to shell |
| `--help` flag | `frankiec run --help` etc. |

---

## v1.9 — `whats_new_v19.fk`

**Theme:** Safety and tooling.

| Feature | Summary |
|---|---|
| Hash `.dig` | `config.dig("db", "host")` — safe nested access, returns nil |
| `zip()` standalone | `zip([1,2,3], ["a","b","c"])` → `[[1,"a"],[2,"b"],[3,"c"]]` |
| Record types | `record Point(x, y)` — named data objects built on Hash |
| `frankiec fmt` | AST-based auto-formatter with `--write` and `--check` |
| `frankiec docs` | Extract `##` doc-comments to Markdown |
| REPL readline + history | Arrow keys, Ctrl+R, tab completion, persistent `~/.frankie_history` |
| `.env` auto-loading | `.env` in the project root is loaded automatically at startup |

---

## v1.8 — `whats_new_v18.fk`

**Theme:** Functional programming and collection power.

| Feature | Summary |
|---|---|
| Lambdas | `->(x) { x * 2 }` — storable, passable first-class functions |
| Hash merge `\|` | `h1 \| h2` — right wins on conflict, chains naturally |
| `group_by` | Bucket elements into a hash of arrays by block result |
| `each_slice(n)` | Iterate in non-overlapping chunks |
| `each_cons(n)` | Iterate with a sliding window |

---

## v1.7 — `whats_new_v17.fk`

**Theme:** Safety and real-world utility.

| Feature | Summary |
|---|---|
| Nil safety `&.` | `name&.upcase` returns nil instead of crashing |
| `template(str, hash)` | `{{key}}` placeholder substitution |
| File system ops | `file_mkdir`, `dir_exists`, `dir_list`, `file_copy`, `file_rename` |
| `assert_raises_typed` | Test that a specific error type is raised |

---

## v1.6 — `whats_new_v16.fk`

**Theme:** Control flow completeness.

| Feature | Summary |
|---|---|
| Compound assignment | `+=`, `-=`, `*=`, `/=`, `//=`, `**=`, `%=` |
| Typed rescue | `rescue ZeroDivisionError e` — catch specific error types |
| `.find` / `.detect` | First element matching a block condition |
| `frankiec test` | Built-in test runner |

---

## v1.5 — `whats_new_v15.fk`

**Theme:** Loop control, randomness, and collection utilities.

| Feature | Summary |
|---|---|
| `next` | Skip to next iteration — like `continue` |
| `break` | Exit a loop early |
| `break value` | Exit with a result — `result = loop.break n * 10` |
| Constants | `UPPER_CASE` — warn on reassignment |
| `rand_int`, `rand_float` | Random number functions |
| `shuffle`, `sample` | Random collection operations |
| `sleep(n)` | Pause execution |
| `sort_by` | Sort by computed key |
| `min_by`, `max_by`, `sum_by` | Aggregate by key |
| `unzip` | Split vector of pairs into two vectors |

---

## v1.4 — `whats_new_v14.fk`

**Theme:** Built-in web server.

| Feature | Summary |
|---|---|
| Web server | `web_app()` — Sinatra-style routing |
| Route definitions | `.get`, `.post`, `.put`, `.delete`, `.patch` |
| Path parameters | `/users/:id` → `req.params["id"]` |
| Query parameters | `req.query["page"]` |
| JSON body | `req.json` — auto-parsed |
| Before/after filters | `app.before do`, `app.after do` |
| Response helpers | `html_response`, `json_response`, `redirect`, `halt` |

---

## v1.3 — `whats_new_v13.fk`

**Theme:** External data and project structure.

| Feature | Summary |
|---|---|
| JSON | `json_read`, `json_write`, `json_parse`, `json_dump` |
| CSV | `csv_read`, `csv_write`, `csv_parse`, `csv_dump` |
| DateTime | `now()`, `today()`, `date_parse()`, `date_from()` |
| HTTP client | `http_get`, `http_post`, `http_put`, `http_delete` |
| `frankiec new` | Project scaffolding |

---

## v1.2 *(no whats_new file)*

**Theme:** Database and multi-file programs.

| Feature | Summary |
|---|---|
| SQLite built-in | `db_open`, `db.query`, `db.insert`, `db.exec`, transactions |
| `require` | Load other `.fk` files — each loaded at most once |

---

## v1.1 — `whats_new_v11.fk`

**Theme:** Collection power.

| Feature | Summary |
|---|---|
| `select` / `reject` | Filter a vector by a condition |
| `reduce` / `inject` | Fold a vector into a single value |
| `any?` / `all?` / `none?` | Boolean tests across a collection |
| `each_with_object` | Iterate with a shared accumulator |
| `take`, `drop`, `chunk`, `tally`, `compact` | Collection utilities |
| `flat_map`, `zip` | Flattening and pairing |
| `case / when` | Pattern matching on values |
| Destructuring assignment | `a, b, c = [1, 2, 3]` |
| New string methods | `.chomp`, `.chop`, `.center`, `.ljust`, `.rjust`, `.squeeze`, `.tr` |
| `count` with block | Count elements matching a condition |

---

## v1.0 *(initial release)*

The foundation: variables, strings with `#{}` interpolation, integers, floats, booleans, nil, vectors, hashes, `if/elsif/else/unless`, `while/until/for`, functions with default params, `begin/rescue/ensure`, `raise`, regex (`matches`, `match_all`, `sub`, `gsub`, `=~`), file I/O (`file_read`, `file_write`), R-style statistics (`mean`, `stdev`, `median`, `sum`), vectorised arithmetic, the pipe operator `|>`, `seq`, `linspace`, the REPL, and `frankiec run/build/check`.
