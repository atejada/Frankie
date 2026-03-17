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

## Web API Summary

| Function / Method                    | Description                              |
|--------------------------------------|------------------------------------------|
| `web_app()`                          | Create a new application                 |
| `app.get(path) do \|req\| end`       | Register a GET route                     |
| `app.post(path) do \|req\| end`      | Register a POST route                    |
| `app.put(path) do \|req\| end`       | Register a PUT route                     |
| `app.delete(path) do \|req\| end`    | Register a DELETE route                  |
| `app.patch(path) do \|req\| end`     | Register a PATCH route                   |
| `app.before do \|req\| end`          | Register a before-filter                 |
| `app.after do \|req, res\| end`      | Register an after-filter                 |
| `app.not_found do \|req\| end`       | Register a custom 404 handler            |
| `app.run(port)`                      | Start the server (blocking)              |
| `response(body, status, headers)`    | Plain-text response                      |
| `html_response(body, status)`        | HTML response                            |
| `json_response(data, status)`        | JSON response                            |
| `redirect(location, status)`         | Redirect response                        |
| `halt(status, body)`                 | Error response                           |
