# HTTP Client

## Overview

Frankie has a built-in HTTP client for making GET, POST, PUT, and DELETE requests — no external libraries, no imports. Built on Python's `urllib`, it handles JSON automatically and supports custom headers.

---

## Making Requests

### `http_get(url)` — GET request

```ruby
resp = http_get("https://api.example.com/users")
puts resp.status   # 200
puts resp.body     # raw response body string
```

### `http_post(url, data)` — POST request

Pass a hash to send as JSON, or a string for plain text.

```ruby
# Send JSON
resp = http_post("https://api.example.com/users", {
  name:  "Alice",
  email: "alice@example.com"
})
puts resp.status   # 201
```

### `http_put(url, data)` — PUT request

```ruby
resp = http_put("https://api.example.com/users/42", {
  name: "Alice Updated"
})
puts resp.status   # 200
```

### `http_delete(url)` — DELETE request

```ruby
resp = http_delete("https://api.example.com/users/42")
puts resp.status   # 204
```

---

## The Response Object

Every HTTP function returns an `HTTPResponse` with these fields and methods:

| Property / Method | Type | Description |
|---|---|---|
| `.status` | Integer | HTTP status code |
| `.body` | String | Raw response body |
| `.headers` | Hash | Response headers |
| `.json()` | Hash / Vector | Parse body as JSON |
| `.ok()` | Boolean | True if status is 2xx |

```ruby
resp = http_get("https://api.example.com/data")

puts resp.status              # 200
puts resp.ok()                # true
puts resp.headers["Content-Type"]   # application/json

# Parse JSON body
data = resp.json()
puts data["name"]
```

---

## Custom Headers

Pass a hash of headers as the last argument to any function.

```ruby
# Bearer token auth
resp = http_get(
  "https://api.example.com/protected",
  {"Authorization": "Bearer your_token_here"}
)

# Multiple headers
resp = http_post(
  "https://api.example.com/data",
  {value: 42},
  {
    "Authorization": "Bearer token",
    "X-Request-ID":  "abc-123"
  }
)
```

When you pass a hash as `data`, Frankie automatically sets `Content-Type: application/json`. You don't need to set it manually.

---

## Checking Status

```ruby
resp = http_get("https://api.example.com/resource")

if resp.ok()
  data = resp.json()
  puts data["result"]
else
  puts "Error #{resp.status}: #{resp.body}"
end
```

Common status codes:

| Code | Meaning |
|---|---|
| `200` | OK |
| `201` | Created |
| `204` | No Content |
| `400` | Bad Request |
| `401` | Unauthorized |
| `403` | Forbidden |
| `404` | Not Found |
| `500` | Internal Server Error |

---

## URL Utilities

### `url_encode(hash)` — Encode a hash as a query string

```ruby
params = {page: 1, limit: 20, sort: "name"}
puts url_encode(params)
# page=1&limit=20&sort=name

# Append to URL manually
base = "https://api.example.com/users"
resp = http_get("#{base}?#{url_encode(params)}")
```

### `url_decode(str)` — Decode a query string into a hash

```ruby
qs = "page=1&limit=20&sort=name"
params = url_decode(qs)
puts params["page"]    # 1
puts params["sort"]    # name
```

---

## Error Handling

HTTP errors (4xx, 5xx) are returned as responses with the corresponding status code — they do not raise exceptions. Network errors (no connection, timeout, DNS failure) do raise `RuntimeError`.

```ruby
# HTTP error — returns a response, no raise
resp = http_get("https://api.example.com/missing")
puts resp.status   # 404
puts resp.body     # error body from server

# Network error — raises
begin
  resp = http_get("https://does-not-exist.invalid/")
rescue RuntimeError e
  puts "Network error: #{e}"
end
```

---

## Practical Examples

```ruby
# Fetch and pretty-print a GitHub user
resp = http_get("https://api.github.com/users/octocat")
if resp.ok()
  user = resp.json()
  puts "Name:      #{user["name"]}"
  puts "Location:  #{user["location"]}"
  puts "Repos:     #{user["public_repos"]}"
  puts "Followers: #{user["followers"]}"
end

# POST to a REST API with auth
def create_task(token, title, due_date)
  resp = http_post(
    "https://api.example.com/tasks",
    {title: title, due: due_date, done: false},
    {"Authorization": "Bearer #{token}"}
  )
  if resp.ok()
    resp.json()
  else
    puts "Failed: #{resp.status} — #{resp.body}"
    nil
  end
end

task = create_task("my_token", "Review PR", "2024-03-20")
puts task["id"] if task != nil

# Cache API results to avoid repeated calls
def fetch_cached(url, cache_path)
  if file_exists(cache_path)
    puts "Using cache: #{cache_path}"
    return json_read(cache_path)
  end
  resp = http_get(url)
  if resp.ok()
    data = resp.json()
    json_write(cache_path, data)
    data
  else
    puts "HTTP #{resp.status}"
    nil
  end
end

data = fetch_cached(
  "https://api.example.com/products",
  "/tmp/products_cache.json"
)

# Retry with backoff
def get_with_retry(url, max_attempts)
  attempt = 0
  begin
    attempt += 1
    resp = http_get(url)
    return resp if resp.ok()
    raise "HTTP #{resp.status}"
  rescue RuntimeError e
    if attempt < max_attempts
      sleep(attempt * 0.5)
      retry
    end
    puts "All #{max_attempts} attempts failed: #{e}"
    nil
  end
end
```

---

## Quick Reference

| Function | Description |
|---|---|
| `http_get(url)` | GET request |
| `http_get(url, headers)` | GET with custom headers |
| `http_post(url, data)` | POST — hash sends as JSON |
| `http_post(url, data, headers)` | POST with custom headers |
| `http_put(url, data)` | PUT request |
| `http_put(url, data, headers)` | PUT with custom headers |
| `http_delete(url)` | DELETE request |
| `http_delete(url, headers)` | DELETE with custom headers |
| `url_encode(hash)` | Hash → query string |
| `url_decode(str)` | Query string → hash |
| `resp.status` | HTTP status code |
| `resp.body` | Raw response string |
| `resp.headers` | Response headers hash |
| `resp.json()` | Parse body as JSON |
| `resp.ok()` | True if 2xx status |
