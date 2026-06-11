# Full Stdlib Index

Every function, method, and operator available in Frankie v1.12. All are available without any import.

---

## Math & Arithmetic

| Function | Description |
|---|---|
| `abs(x)` | Absolute value |
| `sqrt(x)` | Square root — always returns Float |
| `floor(x)` | Round down to nearest integer |
| `ceil(x)` | Round up to nearest integer |
| `round(x, n)` | Round to n decimal places (default 0) |
| `clamp(x, lo, hi)` | Constrain x between lo and hi |
| `min(a, b)` | Smaller of two values |
| `min(vec)` | Smallest element of a vector |
| `max(a, b)` | Larger of two values |
| `max(vec)` | Largest element of a vector |
| `sum(vec)` | Sum of all elements |
| `mean(vec)` | Arithmetic mean |
| `median(vec)` | Middle value (average of two middles for even length) |
| `stdev(vec)` | Sample standard deviation (n-1) |
| `variance(vec)` | Sample variance |
| `+` `-` `*` `/` | Arithmetic operators — `/` always returns Float |
| `//` | Integer (floor) division — Fortran heritage |
| `%` | Modulo |
| `**` | Exponentiation — Fortran heritage |

---

## Sequences & Vectors

| Function | Description |
|---|---|
| `seq(start, stop, step)` | Numeric sequence — `seq(1,5)` → `[1,2,3,4,5]` |
| `linspace(start, stop, n)` | Exactly n evenly-spaced values |
| `vec(range)` | Vector from range — `vec(1..10)` |
| `rep(x, n)` | Repeat a value n times — `rep(0, 3)` → `[0,0,0]` |
| `unzip(vec)` | Split vector of pairs → two vectors |
| `zip(a, b)` | Pair two vectors → vector of pairs |

---

## String Functions

| Function | Description |
|---|---|
| `sub(str, pat, rep)` | Replace first regex match |
| `gsub(str, pat, rep)` | Replace all regex matches |
| `match(str, pat)` | First match object or nil |
| `match_all(str, pat)` | All matches as a vector of strings |
| `matches(str, pat)` | True if pattern matches anywhere |
| `regex(pat, flags)` | Compile a pattern with flags (`"i"`, `"m"`, `"s"`) |
| `template(str, hash)` | `{{key}}` placeholder substitution |
| `sprintf(fmt, ...)` | C-style format string |
| `paste(..., sep:)` | Join values with separator |
| `format(fmt, ...)` | Alias for sprintf |

---

## String Methods

| Method | Description |
|---|---|
| `.upcase` | Uppercase |
| `.downcase` | Lowercase |
| `.length` | Character count |
| `.reverse` | Reversed string |
| `.strip` | Remove leading/trailing whitespace |
| `.lstrip` | Remove leading whitespace |
| `.rstrip` | Remove trailing whitespace |
| `.chomp` | Remove trailing newline |
| `.chop` | Remove last character |
| `.chars` | Vector of characters |
| `.bytes` | Vector of byte integers |
| `.lines` | Vector of lines (newlines stripped) |
| `.ord` | ASCII/Unicode code point of first character |
| `.encode` | String → vector of byte integers |
| `.decode` | Vector of byte integers → string |
| `.split(sep)` | Split by separator → Vector |
| `.join(sep)` | Join vector elements with separator |
| `.include?(s)` | True if s is a substring |
| `.start_with?(s)` | True if string starts with s |
| `.end_with?(s)` | True if string ends with s |
| `.count(sub)` | Count occurrences of sub |
| `.empty?` | True if length is 0 |
| `.nil?` | Always false for a string |
| `.match(pat)` | First match object or nil |
| `.match_all(pat)` | All matches as vector of strings |
| `.matches?(pat)` | True if pattern matches anywhere |
| `.replace(old, new)` | Replace first occurrence (alias for sub) |
| `.sub(pat, rep)` | Replace first regex match |
| `.gsub(pat, rep)` | Replace all regex matches |
| `.gsub(pat) do \|m\|` | Replace all matches — block transforms each |
| `.delete(chars)` | Remove all occurrences of any char in set |
| `.squeeze` | Collapse consecutive duplicate chars |
| `.tr(from, to)` | Translate characters position-by-position |
| `.center(w, pad)` | Center in field of width w |
| `.ljust(w, pad)` | Left-justify in field of width w |
| `.rjust(w, pad)` | Right-justify in field of width w |
| `.to_i` | Parse as integer |
| `.to_f` | Parse as float |
| `.to_s` | Return self |
| `.format(hash)` | `{key}` placeholder substitution |
| `.each_char do \|c\|` | Iterate over characters |
| `.each_line do \|l\|` | Iterate over lines |
| `[i]` | Character at index (negatives ok) |
| `[a..b]` | Inclusive slice |
| `[a...b]` | Exclusive slice |
| `* n` | Repeat string n times |
| `=~` | Position of first match or nil |

---

## Vector Methods

| Method | Description |
|---|---|
| `.length` / `.size` | Number of elements |
| `.first` | First element or nil |
| `.last` | Last element or nil |
| `.empty?` | True if no elements |
| `.include?(x)` | True if x is an element |
| `.count` | Number of elements |
| `.count do \|x\|` | Count elements satisfying block |
| `.tally` | Count occurrences → Hash |
| `.push(x)` | Append element, return vector |
| `.pop()` | Remove and return last element |
| `.delete(x)` | Remove first occurrence of x, return vector |
| `.sort` | Sorted copy |
| `.sort_by do \|x\|` | Sort by computed key |
| `.reverse` | Reversed copy |
| `.uniq` | Deduplicated copy (first occurrence wins) |
| `.flatten` | Deep flatten all levels |
| `.flatten(n)` | Flatten exactly n levels |
| `.compact` | Remove all nil values |
| `.take(n)` | First n elements |
| `.drop(n)` | All but first n elements |
| `.sum` | Sum of all elements |
| `.min` | Minimum element |
| `.max` | Maximum element |
| `.mean` | Arithmetic mean |
| `.map do \|x\|` | Transform each element → new vector |
| `.map_with_index do \|x, i\|` | Map with element and index |
| `.flat_map do \|x\|` | Map then flatten one level |
| `.select do \|x\|` | Keep elements where block is true |
| `.reject do \|x\|` | Keep elements where block is false |
| `.find do \|x\|` | First element where block is true |
| `.detect do \|x\|` | Alias for find |
| `.reduce(init) do \|acc, x\|` | Fold into a single value |
| `.inject(init) do \|acc, x\|` | Alias for reduce |
| `.each do \|x\|` | Iterate for side effects |
| `.each_with_index do \|x, i\|` | Iterate with index |
| `.each_with_object(init) do \|x, obj\|` | Iterate with shared accumulator |
| `.each_slice(n) do \|s\|` | Iterate in non-overlapping chunks |
| `.each_cons(n) do \|w\|` | Iterate with sliding window |
| `.any? do \|x\|` | True if any element satisfies block |
| `.all? do \|x\|` | True if all elements satisfy block |
| `.none? do \|x\|` | True if no elements satisfy block |
| `.min_by do \|x\|` | Element with smallest key value |
| `.max_by do \|x\|` | Element with largest key value |
| `.sum_by do \|x\|` | Sum of block results |
| `.sort_by do \|x\|` | Sort by computed key |
| `.group_by do \|x\|` | Bucket into hash of arrays |
| `.chunk(n)` | Split into sub-vectors of size n |
| `.zip(other)` | Pair elements with another vector |
| `.zip_with(other) do \|a, b\|` | Zip and transform each pair |
| `.product(other)` | Cartesian product |
| `.join(sep)` | Join elements as string with separator |
| `.encode` | Vector of byte ints → string |
| `.decode` | Vector of byte ints → string (explicit) |
| `.dig(i1, i2, ...)` | Safe nested access — returns nil |
| `[i]` | Element at index (negatives ok) |
| `[a..b]` | Inclusive slice |
| `[i] =` | Index assignment |
| `* n` | Repeat vector n times |

---

## Hash Methods

| Method | Description |
|---|---|
| `h[key]` | Get value — nil if missing |
| `h[key] =` | Set value |
| `.keys` | Vector of all keys |
| `.values` | Vector of all values |
| `.size` / `.count` | Number of pairs |
| `.has_key?(k)` | True if key exists |
| `.empty?` | True if no pairs |
| `.fetch(key, default)` | Get with explicit default |
| `.dig(k1, k2, ...)` | Safe nested access — nil at any missing level |
| `.delete(key)` | Remove key, return modified hash |
| `.merge(other)` | New merged hash — right wins on conflict |
| `.merge_bang(other)` | Merge in place |
| `h1 \| h2` | Merge operator — right wins on conflict |
| `.store(key, val)` | Method form of `h[key]=` |
| `.to_a` | Convert to vector of `[key, value]` pairs |
| `.each do \|k, v\|` | Iterate pairs |
| `.each_pair do \|k, v\|` | Alias for each |
| `.each_with_object(init) do \|pair, obj\|` | Iterate with accumulator |
| `.map do \|k, v\|` | Transform pairs → vector |
| `.map_hash do \|k, v\|` | Transform pairs → new hash |
| `.select do \|k, v\|` | Keep pairs where block is true → new hash |
| `.reject do \|k, v\|` | Keep pairs where block is false → new hash |
| `.find do \|k, v\|` | First pair where block is true |
| `.any? do \|k, v\|` | True if any pair satisfies block |
| `.all? do \|k, v\|` | True if all pairs satisfy block |
| `.none? do \|k, v\|` | True if no pair satisfies block |
| `.count do \|k, v\|` | Count pairs satisfying block |
| `.sort_by do \|k, v\|` | Sort pairs by key → vector |
| `.min_by do \|k, v\|` | Pair with smallest key value |
| `.max_by do \|k, v\|` | Pair with largest key value |
| `.group_by do \|k, v\|` | Bucket pairs by block result |

---

## Integer Methods

| Method | Description |
|---|---|
| `.to_f` | Convert to Float |
| `.to_s` | Convert to String |
| `.to_i` | Return self |
| `.times do \|i\|` | Repeat block n times, i from 0 to n-1 |

---

## Float Methods

| Method | Description |
|---|---|
| `.to_i` | Truncate to Integer (toward zero) |
| `.to_s` | Convert to String |
| `.to_f` | Return self |

---

## File I/O

| Function | Description |
|---|---|
| `file_read(path)` | Read entire file as string — raises `FileNotFoundError` |
| `file_lines(path)` | Read file as vector of lines — raises `FileNotFoundError` |
| `file_write(path, str)` | Write string to file (overwrites) |
| `file_append(path, str)` | Append string to file |
| `file_exists(path)` | True if file exists |
| `file_delete(path)` | Delete file — returns false if missing |
| `file_copy(src, dst)` | Copy file — raises `FileNotFoundError` if src missing |
| `file_rename(src, dst)` | Rename/move file — raises `FileNotFoundError` if src missing |
| `file_open(path, mode)` | Open file handle (`"r"`, `"w"`, `"a"`) |
| `file_mkdir(path)` | Create directory and all parents |
| `dir_exists(path)` | True if directory exists |
| `dir_list(path)` | Sorted vector of filenames in directory |

### File Handle Methods

| Method | Description |
|---|---|
| `.read` | Read full contents as string |
| `.write(str)` | Write string |
| `.close` | Close the handle |

---

## JSON & CSV

| Function | Description |
|---|---|
| `json_read(path)` | Read and parse JSON file |
| `json_write(path, data)` | Write data as JSON file |
| `json_write(path, data, true)` | Write pretty-printed JSON |
| `json_parse(str)` | Parse JSON string → value |
| `json_dump(data)` | Serialise value → JSON string |
| `json_dump(data, true)` | Pretty-printed JSON string |
| `csv_read(path)` | Read CSV → vector of hashes |
| `csv_read(path, false)` | Read CSV → vector of vectors |
| `csv_write(path, data)` | Write vector of hashes to CSV |
| `csv_write(path, data, headers)` | Write with explicit column order |
| `csv_parse(str)` | Parse CSV string → vector of hashes |
| `csv_dump(data)` | Serialise → CSV string |

---

## DateTime

| Function / Method | Description |
|---|---|
| `now()` | Current date and time |
| `today()` | Today at midnight |
| `date_parse(str, fmt)` | Parse string — default fmt `"%Y-%m-%d"` |
| `date_from(y, m, d, h, min, s)` | Build from components |
| `.year` `.month` `.day` | Date components |
| `.hour` `.minute` `.second` | Time components |
| `.format(fmt)` | Format with strftime codes |
| `.add_days(n)` | Add n days (negative subtracts) |
| `.add_hours(n)` | Add n hours |
| `.add_minutes(n)` | Add n minutes |
| `.diff_days(other)` | Days between two dates |
| `.diff_seconds(other)` | Seconds between two datetimes |
| `.weekday` | 0=Monday … 6=Sunday |
| `.is_before(other)` | True if earlier |
| `.is_after(other)` | True if later |
| `.timestamp` | Unix timestamp as Float |

---

## HTTP Client

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
| `url_encode(hash)` | Hash → URL query string |
| `url_decode(str)` | Query string → Hash |

### HTTPResponse Properties

| Property / Method | Description |
|---|---|
| `.status` | HTTP status code |
| `.body` | Raw response body string |
| `.headers` | Response headers hash |
| `.json()` | Parse body as JSON |
| `.ok()` | True if 2xx status |

---

## Database (SQLite)

| Function / Method | Description |
|---|---|
| `db_open(path)` | Open or create SQLite database |
| `.exec(sql, params)` | Execute statement — returns row count |
| `.query(sql, params)` | SELECT → vector of hashes |
| `.query_one(sql, params)` | SELECT → first row as hash or nil |
| `.insert(table, hash)` | Insert row from hash — returns last id |
| `.insert_many(table, rows)` | Insert vector of hashes |
| `.find(table, where)` | SELECT with where hash → vector of hashes |
| `.find_one(table, where)` | SELECT first match → hash or nil |
| `.update(table, data, where)` | UPDATE rows — returns count |
| `.delete(table, where)` | DELETE rows — returns count |
| `.count(table)` | COUNT rows in table |
| `.tables` | Vector of table names |
| `.columns(table)` | Vector of column names |
| `.last_id` | Last inserted row id |
| `.begin` | Begin transaction |
| `.commit` | Commit transaction |
| `.rollback` | Rollback transaction |
| `.close` | Close connection |

---

## Web Server

| Function / Method | Description |
|---|---|
| `web_app()` | Create a new web application |
| `.get(path) do \|req\|` | Register GET route |
| `.post(path) do \|req\|` | Register POST route |
| `.put(path) do \|req\|` | Register PUT route |
| `.delete(path) do \|req\|` | Register DELETE route |
| `.patch(path) do \|req\|` | Register PATCH route |
| `.before do \|req\|` | Before filter — runs before every route |
| `.after do \|req\|` | After filter — runs after every route |
| `.not_found do \|req\|` | Custom 404 handler |
| `.run(port)` | Start server on port |
| `response(body, status, headers)` | Build a response |
| `json_response(data, status)` | JSON response |
| `html_response(body, status)` | HTML response |
| `redirect(location, status)` | Redirect response |
| `halt(status, body)` | Abort with status |

### FrankieRequest Properties

| Property | Description |
|---|---|
| `.path` | URL path |
| `.method` | HTTP method string |
| `.params` | Path parameters hash |
| `.query` | Query string parameters hash |
| `.form` | Form body parameters hash |
| `.json` | Parsed JSON body |
| `.body` | Raw request body string |
| `.headers` | Request headers hash |

---

## Random

| Function | Description |
|---|---|
| `rand_int(a, b)` | Random integer a..b inclusive |
| `rand_float(a, b)` | Random float in [a, b) |
| `rand()` | Random float in [0.0, 1.0) |
| `rand(n)` | Random integer in [0, n) |
| `rand_seed(n)` | Fix seed for reproducibility |
| `shuffle(vec)` | Randomly reordered copy of vector |
| `sample(vec, n)` | n randomly chosen elements (no repeats) |

---

## Testing

| Function | Description |
|---|---|
| `assert_eq(actual, expected, msg)` | Pass if actual == expected |
| `assert_neq(actual, expected, msg)` | Pass if actual != expected |
| `assert_true(value, msg)` | Pass if value is truthy |
| `assert_nil(value, msg)` | Pass if value is nil |
| `assert_match(value, pattern, msg)` | Pass if pattern matches anywhere in value |
| `assert_raises(fn, msg)` | Pass if fn raises any error |
| `assert_raises_typed(fn, type, msg)` | Pass if fn raises that specific error type |

---

## Type Checking & Conversion

| Function | Description |
|---|---|
| `is_integer(x)` | True if x is an Integer |
| `is_float(x)` | True if x is a Float |
| `is_string(x)` | True if x is a String |
| `is_vector(x)` | True if x is a Vector |
| `is_nil(x)` | True if x is nil |
| `is_bool(x)` | True if x is Boolean |
| `to_int(x)` | Convert to Integer |
| `to_float(x)` | Convert to Float |
| `to_str(x)` | Convert to String |

---

## Input & Output

| Function | Description |
|---|---|
| `puts(val)` | Print with newline |
| `print(val)` | Print without newline |
| `pp(val)` | Pretty-print with type annotation |
| `input(prompt)` | Read line from stdin as string |
| `input_int(prompt)` | Read line from stdin as integer |
| `input_float(prompt)` | Read line from stdin as float |

---

## System

| Function | Description |
|---|---|
| `exit(code)` | Exit with given code (default 0) |
| `argv()` | Command-line arguments as vector |
| `env(key, default)` | Read environment variable |
| `sleep(seconds)` | Pause execution |
| `times(n) do \|i\|` | Repeat block n times — standalone form |
| `require(path)` | Load another .fk file (once only) |

---

## Operators Reference

| Operator | Description |
|---|---|
| `+` `-` `*` `/` | Arithmetic |
| `//` | Integer (floor) division |
| `%` | Modulo |
| `**` | Exponentiation |
| `==` `!=` `<` `<=` `>` `>=` | Comparison |
| `and` `or` `not` | Logical |
| `=~` | Regex match — returns position or nil |
| `\|>` | Pipe — pass left as argument to right |
| `&.` | Nil-safe navigation — returns nil instead of crashing |
| `\|` | Hash merge — right wins on conflict |
| `..` | Inclusive range |
| `...` | Exclusive range |
| `+=` `-=` `*=` `/=` `//=` `**=` `%=` | Compound assignment |
| `#{}` | String interpolation |

---

## Concurrency & Networking (v1.17)

| Function | Description |
|---|---|
| `parallel_map(vec, workers: 4) do \|x\| ... end` | Thread-pool map, results in input order |
| `tcp_connect(host, port, timeout: nil)` | Open a TCP connection |
| `tcp_listen(port, host: "0.0.0.0")` | Listen on a port; `.accept()` returns a client socket |
| `tcp_serve(port) do \|client\| ... end` | Threaded accept loop, auto-closes clients |
| `sock.send(s)` / `sock.send_line(s)` | Send a string (newline appended by send_line) |
| `sock.recv(n)` / `sock.recv_line()` | Receive a string — `nil` when peer closes |
| `sock.peer` / `sock.close()` | Remote "host:port" / close the connection |

## Testing Extras (v1.17)

| Function | Description |
|---|---|
| `test "name", tags: ["slow"] do ... end` | Named, filterable test group |
| `stub(name, fn)` | Replace a global function (e.g. `"shell"`, `"http_get"`) |
| `unstub(name)` / `unstub()` | Restore one / all stubbed functions |

## Modules & Errors (v1.17)

| Syntax | Description |
|---|---|
| `import "lib/math" as math` | Load a `.fk` file into its own namespace |
| `error TypeName` | Declare a user-defined error type |
| `raise TypeName, "msg"` | Raise a typed error |
| `rescue TypeName => e` | Catch a typed error (Ruby-style binding) |

## Range Methods (v1.17)

| Method | Description |
|---|---|
| `(1..10).to_vec` / `.to_a` | Convert to a vector |
| `(1..10).include?(x)` | Membership test |
| `(1..10).step(n)` | Stride: `[1, 4, 7, 10]` |
| `when 90..100` | Range membership in `case/when` |
