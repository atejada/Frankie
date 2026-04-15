# Frankie v1.14 — Feature Reference

## Overview

v1.14's theme is **"Frankie for real web apps"** — concurrency, a template engine, signed cookies, a middleware stack, static file serving, plus two language upgrades (hash destructuring and shape-based pattern matching) that make working with data cleaner everywhere.

| Feature | Category | Summary |
|---|---|---|
| **`spawn { }`** | language | Fire-and-forget background blocks — zero-blocking web responses |
| **`timeout(n) { }`** | language | Kill a block that runs too long — essential for external calls |
| **Async routes** | web | `app.get_async` — non-blocking route handlers |
| **Middleware stack** | web | `app.use do \|req, next_fn\|` — chainable auth, logging, rate-limiting |
| **Static file serving** | web | `app.static("/public")` — serve a directory with one line |
| **`frankietemplate`** | stitch | Mustache-compatible templates — `{{ var }}`, sections, partials, no dependencies |
| **`frankiecookie`** | stitch | HMAC-signed cookies — tamper-proof via Python's `hmac` stdlib |
| **Hash destructuring** | language | `{name, age} = user` — pull keys directly into variables |
| **Shape pattern matching** | language | `case user when {role: "admin"}` — match on hash structure |
| **`frankiec new` stitches** | tooling | Scaffold now creates `stitches/` folder and mentions it in README |
| **Global stitch install** | tooling | `install.py` copies all stitches to `~/.frankie/stitches/` |
| **`page_links` docs** | docs | Full web pagination example added to `frankiepager` reference |

---

## `spawn { }` — Background Blocks

`spawn` runs a block in a background thread and returns immediately. The web response goes out while the work continues.

```ruby
app.post("/register") do |req|
  user = req.json

  # Respond instantly — email sends in the background
  spawn do
    send_welcome_email(user["email"])
    log("email sent to #{user["email"]}")
  end

  json_response({status: "registered"}, 201)
end
```

`spawn` works anywhere — not just in web routes:

```ruby
spawn do
  result = expensive_computation(data)
  file_write("output.json", json_dump(result))
end

puts "Computation started in background."
```

Spawned blocks share the program's variables by value at spawn time. Mutations inside the block do not affect the outer scope.

---

## `timeout(n) { }` — Kill Slow Blocks

`timeout(seconds)` raises a `TimeoutError` if the block takes longer than `n` seconds. Essential for external HTTP calls, database queries, and anything that can hang.

```ruby
begin
  result = timeout(5) do
    http_get("https://slow-api.example.com/data")
  end
  puts result
rescue TimeoutError
  puts "Request took too long — using cached data"
  result = file_read("cache.json")
end
```

Works inside web routes:

```ruby
app.get("/weather") do |req|
  begin
    data = timeout(3) do
      http_get("https://api.weather.example.com/current")
    end
    json_response(data)
  rescue TimeoutError
    json_response({error: "weather service unavailable"}, 503)
  end
end
```

---

## Async Routes — `app.get_async`

Async routes are non-blocking — slow I/O in one handler does not hold up other requests. Declare a route with `_async` and use `await` inside the block.

```ruby
app = web_app()

app.get_async("/feed") do |req|
  posts  = await http_get("https://api.example.com/posts")
  likes  = await http_get("https://api.example.com/likes")
  json_response({posts: posts, likes: likes})
end

app.post_async("/notify") do |req|
  users = db.find_all("subscribers")
  users.each do |u|
    await send_push(u["token"], req.json["message"])
  end
  json_response({sent: users.length})
end

app.run(3000)
```

All five HTTP methods have async variants: `get_async`, `post_async`, `put_async`, `delete_async`, `patch_async`.

---

## Middleware Stack — `app.use`

`app.use` registers middleware that wraps every request. Middleware receives the request and a `next_fn` — call `next_fn.(req)` to pass control to the next layer.

```ruby
app = web_app()

# Logging middleware
app.use do |req, next_fn|
  puts "→ #{req.method} #{req.path}"
  resp = next_fn.(req)
  puts "← #{resp.status}"
  resp
end

# Auth middleware — reject unauthenticated requests to /admin/*
app.use do |req, next_fn|
  if req.path.start_with?("/admin") and req.headers["X-Api-Key"] != env("API_KEY")
    halt(401, "Unauthorized")
  else
    next_fn.(req)
  end
end

# Rate-limiting middleware (uses frankieconfig for limits)
app.use do |req, next_fn|
  ip = req.headers["X-Forwarded-For"] or "unknown"
  if _rate_exceeded?(ip)
    halt(429, "Too many requests")
  else
    next_fn.(req)
  end
end

app.get("/admin/users") do |req|
  json_response({users: db.find_all("users")})
end

app.run(3000)
```

Middleware runs in registration order. Each layer can short-circuit by returning a response directly instead of calling `next_fn`.

---

## Static File Serving — `app.static`

Serve a directory of static files with one line. Files are served relative to the project root.

```ruby
app = web_app()

# Serve everything in ./public/ at /
app.static("./public")

# Or serve at a specific URL prefix
app.static("./assets", "/static")

app.get("/") do |req|
  render_file("./views/index.html", {title: "Home"})
end

app.run(3000)
```

File types served automatically include HTML, CSS, JS, images (PNG, JPG, GIF, SVG, WebP), fonts, and JSON. Directory listing is disabled by default.

---

## `frankietemplate` — Mustache-Compatible Templates

`frankietemplate` implements the core Mustache spec as a stitch — zero dependencies, pure `.fk`.

```ruby
stitch "frankietemplate"

# Render from a string
tmpl = "<h1>Hello, {{ name }}!</h1><p>You have {{ count }} messages.</p>"
puts render(tmpl, {name: "Alice", count: 5})
# <h1>Hello, Alice!</h1><p>You have 5 messages.</p>

# Render from a file
app.get("/dashboard") do |req|
  user = db.find("users", {id: session(req, resp)["user_id"]})
  html = render_file("./views/dashboard.html", {
    name:     user["name"],
    messages: db.find_all("messages", {user_id: user["id"]})
  })
  html_response(html)
end
```

### Template Syntax

```html
<!-- {{ variable }} — interpolated, HTML-escaped -->
<p>Hello, {{ name }}!</p>

<!-- {{{ variable }}} — raw / unescaped HTML -->
<div>{{{ body_html }}}</div>

<!-- {{# section }} — render if truthy, iterate if vector -->
{{# messages }}
  <li>{{ text }} — {{ author }}</li>
{{/ messages }}

<!-- {{^ inverted }} — render if falsy or empty -->
{{^ messages }}
  <p>No messages yet.</p>
{{/ messages }}

<!-- {{> partial_name }} — include ./views/partials/header.html -->
{{> header }}

<!-- {{! comment }} — not rendered -->
{{! This is a comment }}
```

### Functions

`render(template, data)` — render a template string with a data hash. Variables are HTML-escaped by default; use `{{{ }}}` for raw output.

`render_file(path, data)` — load and render a `.html` or `.mustache` file.

`partial(name)` — load a partial from `./views/partials/<name>.html` (used internally by `{{> name }}`).

### Project layout with templates

```
myapp/
├── main.fk
├── stitches/
│   └── frankietemplate.fk
└── views/
    ├── index.html
    ├── dashboard.html
    └── partials/
        ├── header.html
        └── footer.html
```

---

## `frankiecookie` — Signed Cookies

`frankiecookie` wraps Python's stdlib `hmac` + `hashlib` to give you tamper-proof cookies. The signature is verified on every read — a modified value returns `nil`.

```ruby
stitch "frankiecookie"

SECRET = env("COOKIE_SECRET", "change-me-in-production")

app = web_app()

app.post("/login") do |req|
  user = authenticate(req.json["username"], req.json["password"])
  if user == nil
    halt(401, "Invalid credentials")
  else
    resp = response("")
    set_signed_cookie(resp, "user_id", user["id"].to_s, SECRET, {
      max_age: 86400,
      same_site: "Strict"
    })
    redirect("/dashboard")
  end
end

app.get("/dashboard") do |req|
  user_id = get_signed_cookie(req, "user_id", SECRET)
  if user_id == nil
    redirect("/login")
  else
    user = db.find("users", {id: user_id.to_int})
    html_response("<h1>Welcome, #{user["name"]}</h1>")
  end
end

app.get("/logout") do |req|
  resp = response("")
  delete_cookie(resp, "user_id")
  redirect("/login")
end

app.run(3000)
```

### Functions

| Function | Description |
|---|---|
| `set_signed_cookie(resp, name, value, secret, opts)` | Write a signed cookie. Opts: `path`, `max_age`, `same_site`, `http_only`, `secure` |
| `get_signed_cookie(req, name, secret)` | Read and verify — returns the original value, or `nil` if missing or tampered |
| `delete_cookie(resp, name)` | Expire a cookie immediately (`max_age: 0`) |
| `cookie_set?(req, name)` | Returns `true` if the cookie is present on the request |

**Important:** signed cookies prove the value was written by your server. They are not encrypted — the value is visible in the browser. Do not store passwords or secrets in cookie values.

---

## Hash Destructuring

Pull hash keys directly into variables with the `{}` destructuring syntax. Keys must exist as bareword (symbol) keys in the hash.

```ruby
user = {name: "Alice", age: 30, role: "admin"}

# Basic destructuring
{name, age} = user
puts name   # Alice
puts age    # 30

# In a function — unpack a config hash
def start_server(config)
  {host, port, debug} = config
  puts "Starting on #{host}:#{port} (debug=#{debug})"
end

start_server({host: "localhost", port: 3000, debug: true})

# With database records
db.find_all("users").each do |row|
  {name, email, role} = row
  puts "#{name} <#{email}> [#{role}]"
end

# Nested — destructure from a route handler
app.post("/users") do |req|
  {name, email, password} = req.json
  user = create_user(name, email, password)
  json_response({id: user["id"]}, 201)
end
```

Missing keys evaluate to `nil`:

```ruby
{name, nickname} = {name: "Alice"}
puts name       # Alice
puts nickname   # nil
```

---

## Shape Pattern Matching

`case / when` now matches hash shapes. A `when` clause with a hash literal matches any hash that contains at least those keys with those values.

```ruby
user = {name: "Alice", role: "admin", active: true}

case user
when {role: "admin"}
  puts "Admin panel access granted"
when {role: "moderator", active: true}
  puts "Moderator tools available"
when {active: false}
  puts "Account suspended"
else
  puts "Regular user"
end
```

Shapes match on a subset — extra keys in the hash are ignored:

```ruby
event = {type: "click", target: "button", x: 42, y: 18}

case event
when {type: "click", target: "button"}
  puts "Button clicked at #{event["x"]},#{event["y"]}"
when {type: "click"}
  puts "Click at #{event["x"]},#{event["y"]}"
when {type: "keydown"}
  puts "Key pressed"
end
```

Mix value and shape matching in the same `case`:

```ruby
case response
when {status: 200}
  puts "OK"
when {status: 404}
  puts "Not found"
when {status: 500}
  puts "Server error"
when nil
  puts "No response"
else
  puts "Unexpected: #{response}"
end
```

Works with records too — `record Point(x, y)` creates a hash under the hood, so `when {x: 0}` matches a point on the y-axis.

---

## `frankiec new` — Updated Scaffold

`frankiec new myapp` now creates a `stitches/` folder and a `stitches/README.md` explaining how stitches work.

```
myapp/
├── main.fk
├── test.fk
├── lib/
│   └── utils.fk
├── stitches/
│   └── README.md        ← explains stitch convention
├── views/               ← created for web projects
│   └── partials/
├── data/
├── .gitignore
├── .env.example
└── README.md
```

The generated `README.md` now documents the `stitches/` convention:

```markdown
## Packages (Stitches)

Third-party Frankie packages go in `stitches/`. Load them with:

    stitch "frankietemplate"

Stitches ship with Frankie and are installed globally by `install.py`.
Drop your own `.fk` files in `stitches/` to share utilities across the project.
```

---

## Global Stitch Install

`install.py` now correctly copies all bundled stitches to `~/.frankie/stitches/` during installation, making them available to every project without copying files manually.

```bash
python3 install.py

# Output now includes:
#   Installed: /path/to/frankie/bin/frankiec
#   Installed stitches to /Users/you/.frankie/stitches/
#     frankiecolor.fk
#     frankieconfig.fk
#     frankiecookie.fk
#     frankieforms.fk
#     frankiepager.fk
#     frankiestring.fk
#     frankietable.fk
#     frankietemplate.fk
```

After installation, `stitch "frankietemplate"` works from any directory without copying the `.fk` file into the project.

---

## `page_links` — Full Web Pagination Example

`page_links(pager, url_template)` generates a ready-to-render navigation link vector. Use `{page}` in the URL template as the page placeholder.

```ruby
stitch "frankiepager"
stitch "frankietemplate"

app = web_app()

app.get("/posts") do |req|
  current_page = (req.query["page"] or "1").to_int
  total_posts  = db.count("posts")

  pager = paginate({total: total_posts, page: current_page, per_page: 10})
  posts = page_slice(db.find_all("posts"), current_page, 10)
  links = page_links(pager, "/posts?page={page}")

  html = render_file("./views/posts.html", {
    posts: posts,
    links: links,
    from:  pager["from"],
    to:    pager["to"],
    total: pager["total"]
  })

  html_response(html)
end

app.run(3000)
```

Corresponding template (`views/posts.html`):

```html
<p>Showing {{ from }}–{{ to }} of {{ total }} posts</p>

{{# posts }}
  <article>
    <h2>{{ title }}</h2>
    <p>{{ summary }}</p>
  </article>
{{/ posts }}

<nav>
  {{# links }}
    {{# active }}
      <strong>{{ label }}</strong>
    {{/ active }}
    {{^ active }}
      <a href="{{ url }}">{{ label }}</a>
    {{/ active }}
  {{/ links }}
</nav>
```

### `page_links` return value

Each element in the returned vector is a hash with three keys:

| Key | Type | Description |
|---|---|---|
| `label` | String | Display text — `"1"`, `"2"`, `"← Prev"`, `"Next →"` |
| `url` | String | Full URL for this page link |
| `active` | Boolean | `true` for the current page — style it as non-clickable |
