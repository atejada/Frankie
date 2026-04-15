# Frankie Web Server — v1.4

Frankie ships a built-in HTTP web server in the style of Sinatra / Camping.
Zero external dependencies — it runs on Python's standard library `http.server`.

---

## Quick Start

```ruby
app = web_app()

app.get("/") do |req|
  html_response("<h1>Hello from Frankie! 🧟</h1>")
end

app.run(3000)
```

```bash
frankiec run myapp.fk
# 🧟 Frankie web server running on http://0.0.0.0:3000
```

---

## Routes

Register routes with `.get`, `.post`, `.put`, `.delete`, `.patch`.
Each takes a path pattern and a `do |req| ... end` block.
The block receives a `FrankieRequest` and must return a response value.

```ruby
app.get("/hello") do |req|
  response("Hello!")
end

app.post("/echo") do |req|
  response(req.body)
end

app.delete("/items/:id") do |req|
  response("Deleted #{req.params["id"]}")
end
```

### Path Parameters

Use `:name` segments to capture parts of the URL:

```ruby
app.get("/users/:id/posts/:slug") do |req|
  id   = req.params["id"]
  slug = req.params["slug"]
  response("User #{id}, post #{slug}")
end
```

### Query Parameters

```ruby
# GET /search?q=frankie&page=2
app.get("/search") do |req|
  q    = req.query["q"]
  page = req.query["page"]
  response("q=#{q} page=#{page}")
end
```

---

## Request Object

| Property  | Type   | Description                                          |
|-----------|--------|------------------------------------------------------|
| `method`  | String | `"GET"`, `"POST"`, `"PUT"`, `"DELETE"`, `"PATCH"`    |
| `path`    | String | URL path, e.g. `"/users/42"`                         |
| `params`  | Hash   | Path parameters, e.g. `{id: "42"}`                   |
| `query`   | Hash   | Query-string parameters, e.g. `{page: "2"}`          |
| `headers` | Hash   | HTTP request headers                                 |
| `body`    | String | Raw request body                                     |
| `json`    | Hash   | Body parsed as JSON, or `nil` if not valid JSON      |
| `form`    | Hash   | Body parsed as `application/x-www-form-urlencoded`   |

---

## Response Helpers

| Function                          | Status | Content-Type         |
|-----------------------------------|--------|----------------------|
| `response(body)`                  | 200    | text/plain           |
| `response(body, status)`          | custom | text/plain           |
| `response(body, status, headers)` | custom | text/plain           |
| `html_response(html)`             | 200    | text/html            |
| `html_response(html, status)`     | custom | text/html            |
| `json_response(hash)`             | 200    | application/json     |
| `json_response(hash, status)`     | custom | application/json     |
| `redirect(location)`              | 302    | —                    |
| `redirect(location, status)`      | custom | —                    |
| `halt(status, body)`              | custom | text/plain           |

Returning a plain string from the handler is also fine — it becomes a `200 text/plain` response automatically.
Returning a hash or vector auto-converts to JSON.

---

## JSON API

```ruby
# Receive JSON
app.post("/api/users") do |req|
  data = req.json           # parsed hash or nil
  if data == nil
    halt(400, "Expected JSON")
  else
    name = data["name"]
    json_response({id: 1, name: name}, 201)
  end
end

# Send JSON
app.get("/api/info") do |req|
  json_response({version: "1.4", alive: true})
end
```

---

## Before / After Filters

Filters run before or after every matched route.

```ruby
app.before do |req|
  puts "#{req.method} #{req.path}"
end

app.after do |req, res|
  puts "  -> #{res.status}"
end
```

`before` receives the request. `after` receives the request and the response.

---

## Custom 404

```ruby
app.not_found do |req|
  html_response("<h1>404</h1><p>Nothing at #{req.path}</p>", 404)
end
```

---

## Starting the Server

```ruby
app.run(3000)           # listen on 0.0.0.0:3000 (default)
app.run(8080)           # custom port
app.run(3000, "127.0.0.1")  # localhost only
```

The server is multi-threaded (one thread per request) and blocks until Ctrl+C.

---

## Full Example

See `examples/webapp.fk` for a complete demo including:

- HTML and plain text responses
- Path and query parameters
- JSON POST/GET/DELETE endpoints
- In-memory notes store
- Custom 404 handler

Run it:

```bash
frankiec run examples/webapp.fk
```

Then try:

```bash
curl http://localhost:3000/
curl http://localhost:3000/greet/Alice
curl http://localhost:3000/api/status
curl -X POST http://localhost:3000/notes \
     -H "Content-Type: application/json" \
     -d '{"text": "Buy milk"}'
curl http://localhost:3000/notes
curl http://localhost:3000/notes/1
curl -X DELETE http://localhost:3000/notes/1
```

---

## Cookies and Sessions *(v1.13.1)*

### Reading and Writing Cookies

Every request exposes its cookies as a hash via `req.cookies`. Every response can set a cookie via `resp.set_cookie(name, value, opts)`.

```ruby
app.get("/prefs") do |req|
  theme = req.cookies["theme"] or "light"
  resp = html_response("<p>Theme: #{theme}</p>")
  resp.set_cookie("theme", theme, {max_age: 86400})
  resp
end
```

`set_cookie` options (all optional):

| Option | Default | Description |
|---|---|---|
| `path` | `"/"` | Cookie scope path |
| `http_only` | `true` | Hide from JavaScript |
| `max_age` | `nil` | Expiry in seconds (omit for session cookie) |
| `same_site` | `"Lax"` | CSRF protection (`"Strict"`, `"Lax"`, `"None"`) |

### Cookie-Backed Sessions

`session(req, resp)` returns a `FrankieSession` — a hash-like object backed by a single JSON cookie (`_fk_session`). Read it, mutate it, and call `.save()` before returning the response. No server-side state, no database, no configuration.

```ruby
app = web_app()

app.get("/counter") do |req|
  resp = response("")
  s = session(req, resp)

  count = (s["count"] or 0) + 1
  s["count"] = count
  s.save()

  html_response("You have visited #{count} time(s).")
end

app.post("/login") do |req|
  user = req.json["username"]
  resp = response("")
  s = session(req, resp)
  s["user"] = user
  s["logged_in_at"] = now()
  s.save()
  redirect("/dashboard")
end

app.get("/logout") do |req|
  resp = response("")
  s = session(req, resp)
  s.clear()
  s.save()
  redirect("/")
end

app.run()
```

**Session API:**

| Method | Description |
|---|---|
| `s["key"]` | Read value (`nil` if missing) |
| `s["key"] = value` | Write value |
| `s.has_key?(key)` | Check existence |
| `s.keys` | All session keys |
| `s.delete(key)` | Remove one key |
| `s.clear()` | Remove all keys |
| `s.save()` | Write cookie to response — must be called before returning |

**Important:** the session cookie is `HttpOnly` and `SameSite=Lax`. It is **not encrypted** — store user IDs, not passwords or secrets.

---

## Web API Summary

| Function / Method                    | Description                              |
|--------------------------------------|------------------------------------------|
| `web_app()`                          | Create a new application                 |
| `app.get(path) do \|req\| end`       | Register a GET route                     |
| `app.post(path) do \|req\| end`      | Register a POST route                    |
| `app.put(path) do \|req\| end`       | Register a PUT route                     |
| `app.delete(path) do \|req\| end`    | Register a DELETE route                  |
| `app.patch(path) do \|req\| end`     | Register a PATCH route                   |
| `app.get_async(path) do \|req\| end` | Register a non-blocking GET route        |
| `app.post_async(path) do \|req\| end`| Register a non-blocking POST route       |
| `app.use do \|req, next_fn\| end`    | Register middleware                      |
| `app.static(dir)`                    | Serve a directory at `/`                 |
| `app.static(dir, prefix)`            | Serve a directory at a URL prefix        |
| `app.before do \|req\| end`          | Register a before-filter                 |
| `app.after do \|req, res\| end`      | Register an after-filter                 |
| `app.not_found do \|req\| end`       | Register a custom 404 handler            |
| `app.run(port)`                      | Start the server (blocking)              |
| `response(body, status, headers)`    | Plain-text response                      |
| `html_response(body, status)`        | HTML response                            |
| `json_response(data, status)`        | JSON response                            |
| `redirect(location, status)`         | Redirect response                        |
| `halt(status, body)`                 | Error response                           |
| `req.cookies`                        | Parsed Cookie header as a hash           |
| `resp.set_cookie(name, val, opts)`   | Append a Set-Cookie header               |
| `session(req, resp)`                 | Cookie-backed session hash               |
| `spawn { }`                          | Run block in background thread           |
| `timeout(n) { }`                     | Run block with a time limit              |
| `await expr`                         | Non-blocking wait inside async routes    |

---

## Concurrency *(v1.14)*

### `spawn { }` — Background Blocks

`spawn` runs a block in a background thread and returns immediately. Use it inside route handlers to do work after the response goes out.

```ruby
app.post("/register") do |req|
  user = req.json

  spawn do
    send_welcome_email(user["email"])
    log("welcome email sent to #{user["email"]}")
  end

  json_response({status: "registered"}, 201)
end
```

Works anywhere — not just in web routes:

```ruby
spawn do
  result = crunch_numbers(data)
  file_write("report.json", json_dump(result))
end
puts "Crunching in background..."
```

Spawned blocks capture variables by value at spawn time. Mutations inside the block do not affect the outer scope.

### `timeout(n) { }` — Time-Bounded Execution

`timeout(seconds)` raises `TimeoutError` if the block takes longer than `n` seconds.

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

### Async Routes — `app.get_async`

Async routes are non-blocking — slow I/O in one handler does not hold up other requests. Use `await` inside the block for non-blocking calls.

```ruby
app = web_app()

app.get_async("/feed") do |req|
  posts = await http_get("https://api.example.com/posts")
  likes = await http_get("https://api.example.com/likes")
  json_response({posts: posts, likes: likes})
end

app.run(3000)
```

All five HTTP methods have async variants: `get_async`, `post_async`, `put_async`, `delete_async`, `patch_async`.

---

## Middleware *(v1.14)*

`app.use` registers middleware that runs around every request. Each layer receives the request and a `next_fn` — call `next_fn.(req)` to pass control forward, or return a response directly to short-circuit.

```ruby
app = web_app()

# Logging
app.use do |req, next_fn|
  puts "→ #{req.method} #{req.path}"
  resp = next_fn.(req)
  puts "← #{resp.status}"
  resp
end

# Auth guard for /admin/*
app.use do |req, next_fn|
  if req.path.start_with?("/admin") and req.headers["X-Api-Key"] != env("API_KEY")
    halt(401, "Unauthorized")
  else
    next_fn.(req)
  end
end

app.get("/admin/dashboard") do |req|
  html_response("<h1>Admin</h1>")
end

app.run(3000)
```

Middleware runs in registration order. `before` and `after` filters still work alongside `use` — they run inside the middleware chain.

---

## Static File Serving *(v1.14)*

Serve a directory of files with one line. Files are served relative to the project root.

```ruby
app = web_app()

# Serve ./public/ at /
app.static("./public")

# Serve ./assets/ at /static/
app.static("./assets", "/static")

app.get("/") do |req|
  html_response(file_read("./public/index.html"))
end

app.run(3000)
```

Served automatically: `.html`, `.css`, `.js`, `.json`, `.png`, `.jpg`, `.gif`, `.svg`, `.webp`, `.ico`, `.woff`, `.woff2`. Directory listing is disabled — unlisted paths return 404.
