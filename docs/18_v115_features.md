# Frankie v1.15 — Feature Reference

> Theme: **Language Polish & Developer Ergonomics**

---

## Language Features

### Ternary Operator

```frankie
label = score >= 90 ? "A" : score >= 70 ? "B" : "C"
msg   = n == 1 ? "one item" : "#{n} items"
puts x > 0 ? "positive" : "non-positive"
```

Right-associative — nesting works naturally without parentheses. Valid in any expression
position: assignment, string interpolation, function arguments, vector literals.

---

### Keyword-Style Default Parameters

Both `=` and `:` syntax are now accepted in `def`:

```frankie
# Positional default (was already supported)
def greet(name, greeting = "Hello")
  puts "#{greeting}, #{name}!"
end

# Keyword default (new in v1.15)
def connect(host, port: 5432, ssl: true, timeout: 30)
  puts "#{host}:#{port} ssl=#{ssl}"
end

connect("localhost")                          # localhost:5432 ssl=true
connect("prod", port: 3306, ssl: false)       # prod:3306 ssl=false
connect("prod", ssl: false, timeout: 10)      # prod:5432 ssl=false
```

Mixed signatures work correctly. Reserved words (`timeout`, `spawn`) are now valid
parameter names.

---

### Splat in Multi-Assign

Capture remaining elements with `*rest`:

```frankie
a, b, *rest       = [1, 2, 3, 4, 5]    # rest = [3, 4, 5]
first, *mid, last = [1, 2, 3, 4, 5]    # mid  = [2, 3, 4]
head, *tail       = [10, 20]            # tail = [] (empty, not nil)
```

Plain multi-assign (without splat) continues to work exactly as before:

```frankie
lo, hi = [min(data), max(data)]
```

---

### `const` Keyword

Explicit constant declaration — more readable than relying on ALL_CAPS convention:

```frankie
const PI           = 3.14159
const MAX_RETRIES  = 3
const APP_NAME     = "Frankie"
const BASE_URL     = env("BASE_URL", "http://localhost:3000")
```

Reassignment prints a runtime warning and preserves the original value.
The existing ALL_CAPS auto-detection still works — `const` is additive.

---

### Lambda Call Syntax — `fn.(args)` everywhere

`fn.(args)` previously only worked inside web route middleware. Now valid in all contexts:

```frankie
double = ->(x) { x * 2 }
puts double.(5)                   # 10

add = ->(a, b) do
  return a + b
end
puts add.(3, 4)                   # 7

# Store lambdas in a vector and call them
transforms = [->(x) { x * 2 }, ->(x) { x + 10 }]
result = 5
transforms.each do |f|
  result = f.(result)
end
puts result                       # (5 * 2 + 10) = 20
```

---

## Stdlib

### `json_encode`

```frankie
data = {name: "Alice", scores: [95, 87, 92]}
puts json_encode(data)
puts json_encode(data, pretty: true)

# Round-trip
raw  = json_encode([1, 2, 3])
back = json_parse(raw)
puts back[1]    # 2
```

`json_dump` remains as an alias. `json_encode` is now the preferred name.

---

### `hmac_sign` / `hmac_verify`

Previously only available as internal `_fk_hmac_sign` / `_fk_hmac_verify`. Now public:

```frankie
SECRET = env("APP_SECRET", "dev-only")

token = hmac_sign("user_id=42", SECRET)
puts token    # user_id=42:be38cbad...

subject = hmac_verify(token, SECRET)
puts subject  # user_id=42

puts hmac_verify("tampered:abc", SECRET)  # nil
```

---

### `base64_encode` / `base64_decode`

```frankie
puts base64_encode("hello:world")    # aGVsbG86d29ybGQ=
puts base64_decode("aGVsbG86d29ybGQ=")  # hello:world

# Useful for HTTP Basic Auth headers
creds = base64_encode("#{user}:#{pass}")
puts "Authorization: Basic #{creds}"
```

---

### `String#format`

```frankie
tmpl = "Hello, {name}! You have {count} messages."
puts tmpl.format({name: "Alice", count: 5})

puts "Order {id} placed by {user}".format({id: 42, user: "Bob"})
```

Raises a descriptive error for missing keys.

---

### `.chars` / `.bytes`

```frankie
"hello".chars           # [h, e, l, l, o]
"AB".bytes              # [65, 66]

"café".chars.length     # 4 (Unicode-aware)

"hello".chars.each do |c|
  print c + "-"
end
# h-e-l-l-o-
```

---

### Path Helpers

```frankie
path_join("home", "alice", "docs")       # "home/alice/docs"
path_join("/usr", "local", "bin")        # "/usr/local/bin"

path_dirname("/home/alice/report.txt")   # "/home/alice"
path_basename("/home/alice/report.txt")  # "report.txt"
path_extname("/home/alice/report.txt")   # ".txt"
path_stem("/home/alice/report.txt")      # "report"
path_absolute("./data/db.sqlite")        # absolute path
```

---

### Date Arithmetic

```frankie
d = date_from(2025, 6, 1)

puts (d + 30).format("%Y-%m-%d")    # 2025-07-01
puts (d - 7).format("%Y-%m-%d")     # 2025-05-25
puts (d + 30) - d                   # 30  (integer days)

# Comparison
puts d < date_from(2025, 12, 31)    # true
puts d == date_from(2025, 6, 1)     # true
```

---

### `.zip_with` Block

```frankie
a = [1, 2, 3]
b = [4, 5, 6]

sums = a.zip_with(b) do |x, y| x + y end
puts sums    # [5, 7, 9]

# No block — returns pairs
puts a.zip_with(b)    # [[1, 4], [2, 5], [3, 6]]
```

---

### Testing: `assert_not_nil` / `assert_in`

```frankie
assert_not_nil(user, "user was found")
assert_not_nil(result["id"], "result has an id")

assert_in("admin", roles, "user has admin role")
assert_in(42, valid_ids, "id is valid")

run_tests()
```

---

### `FrankieRequest` Query Helpers

```frankie
app.get("/items") do |req|
  page     = req.query_int("page", 1)
  per_page = req.query_int("per_page", 20)
  min_score = req.query_float("min_score", 0.0)
  show_all  = req.query_bool("show_all", false)

  items = db.find_all("items")
  json_response({page: page, per_page: per_page, items: items})
end
```

`query_int` / `query_float` / `query_bool` all accept a default as the second argument.
`query_bool` treats `"true"`, `"1"`, `"yes"` as `true`; everything else as `false`.

---

## New Stitches

### `frankieauth`

```frankie
stitch "frankieauth"

SECRET = env("TOKEN_SECRET", "dev-secret")

# Basic Auth middleware
app.use do |req, next_fn|
  if not basic_auth_ok?(req, "admin", env("ADMIN_PASS", "secret"))
    halt(401, "Unauthorized")
  end
  next_fn.(req)
end

# Bearer token login
app.post("/login") do |req|
  user = req.json["username"]
  token = auth_token_create(user, SECRET)
  json_response({token: token})
end

# Protected route
app.get("/me") do |req|
  user = bearer_required(req, SECRET)
  json_response({user: user})
end
```

Functions: `basic_auth_ok?(req, user, pass)`, `auth_token_create(subject, secret)`,
`auth_token_verify(req, secret)`, `bearer_required(req, secret)`.

---

### `frankieratelimit`

```frankie
stitch "frankieratelimit"

# Global: 60 req/min per IP
app.use do |req, next_fn|
  rate_limit_check(req, next_fn)
end

# Strict on login: 5 req/min
app.post("/login") do |req|
  rate_limit_check(req, nil, max: 5, window: 60)
  # ... login logic
end
```

In-memory sliding window — zero dependencies, resets on server restart.

---

## Tooling

### `frankiec check`

```bash
frankiec check app.fk          # exit 0 — no errors
frankiec check broken.fk       # exit 1 — prints error location
```

Parses without executing. Useful in CI:

```bash
frankiec check src/*.fk && echo "All files OK"
```

### `frankiec new`

```bash
frankiec new myapp
cd myapp
frankiec run main.fk
frankiec test
```

Scaffolds a complete project layout:

```
myapp/
├── main.fk         ← entry point
├── test.fk         ← test suite (runs with frankiec test)
├── lib/
│   └── utils.fk    ← shared utilities (require "lib/utils")
├── stitches/       ← project-local stitches
├── views/          ← frankietemplate HTML templates
├── public/         ← static files (app.static("./public"))
├── data/           ← JSON, CSV, SQLite files
├── .env.example
├── .gitignore
└── README.md
```

### `frankiec watch` *(now official)*

```bash
frankiec watch app.fk           # re-run on save
frankiec watch test.fk --test   # re-run tests on save
```
