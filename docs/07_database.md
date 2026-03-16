# Database Access (SQLite)

Frankie has built-in SQLite support via `db_open()` — zero external dependencies,
works everywhere Python does.

---

## Opening a Database

```ruby
# In-memory database (great for testing)
db = db_open(":memory:")

# File-based database (persists to disk)
db = db_open("myapp.db")
db = db_open("/path/to/data.db")
```

---

## Creating Tables

```ruby
db.exec("CREATE TABLE IF NOT EXISTS users (
  id    INTEGER PRIMARY KEY AUTOINCREMENT,
  name  TEXT    NOT NULL,
  email TEXT    UNIQUE,
  age   INTEGER
)")
```

Use triple-quoted strings for multi-line SQL:

```ruby
sql = """
  CREATE TABLE IF NOT EXISTS products (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT    NOT NULL,
    price REAL    NOT NULL,
    stock INTEGER DEFAULT 0
  )
"""
db.exec(sql)
```

---

## Inserting Data

### Convenience insert with a hash

```ruby
db.insert("users", {name: "Alice", email: "alice@example.com", age: 30})
db.insert("users", {name: "Bob",   email: "bob@example.com",   age: 25})
```

### Raw SQL with `?` placeholders (safe from SQL injection)

```ruby
db.exec("INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
        ["Carol", "carol@example.com", 28])
```

### Bulk insert

```ruby
rows = [
  {name: "Dave",  email: "dave@x.com",  age: 35},
  {name: "Eve",   email: "eve@x.com",   age: 29},
  {name: "Frank", email: "frank@x.com", age: 42}
]
db.insert_many("users", rows)
```

### Getting the new row ID

```ruby
id = db.insert("users", {name: "Grace", email: "g@x.com", age: 31})
puts "New user ID: #{id}"
# or
db.insert("users", {name: "Hector", email: "h@x.com", age: 27})
puts "Last ID: #{db.last_id}"
```

---

## Querying Data

### Get all rows from a table

```ruby
users = db.find_all("users")
users.each do |u|
  puts "#{u["name"]} (#{u["age"]})"
end
```

### Filter by conditions (hash → AND clauses)

```ruby
devs = db.find("users", {department: "Engineering"})
puts "Engineers: #{devs.length}"
```

### Find a single row (returns nil if not found)

```ruby
alice = db.find_one("users", {name: "Alice"})
if alice != nil
  puts "Found: #{alice["name"]}, age #{alice["age"]}"
end
```

### Raw SQL queries

```ruby
# Parameterised — always use ? placeholders for user input
results = db.query(
  "SELECT name, age FROM users WHERE age > ? ORDER BY age DESC",
  [25]
)

results.each do |row|
  puts "#{row["name"]}: #{row["age"]}"
end
```

### Single-row raw query

```ruby
row = db.query_one("SELECT COUNT(*) AS n, AVG(age) AS avg FROM users")
puts "Count: #{row["n"]}, Avg age: #{row["avg"]}"
```

---

## Counting Rows

```ruby
puts db.count("users")                          # all rows
puts db.count("users", {department: "Finance"}) # filtered
```

---

## Updating Data

```ruby
updated = db.update("users", {age: 31}, {name: "Alice"})
puts "Updated #{updated} row(s)"

# Raw SQL update
db.exec("UPDATE users SET age = age + 1 WHERE department = ?", ["Engineering"])
```

---

## Deleting Data

```ruby
deleted = db.delete("users", {name: "Bob"})
puts "Deleted #{deleted} row(s)"

# Raw SQL delete
db.exec("DELETE FROM users WHERE age > ?", [60])
```

---

## Transactions

Wrap multiple operations in a transaction — all succeed or all roll back:

```ruby
db.transaction do
  db.insert("accounts", {owner: "Alice", balance: 1000})
  db.insert("accounts", {owner: "Bob",   balance: 500})
end

# Transfer with rollback on error
begin
  db.transaction do
    db.exec("UPDATE accounts SET balance = balance - 100 WHERE owner = ?", ["Alice"])
    db.exec("UPDATE accounts SET balance = balance + 100 WHERE owner = ?", ["Bob"])
    # If either fails, both roll back
  end
  puts "Transfer complete"
rescue e
  puts "Transfer failed: #{e}"
end
```

---

## Schema Introspection

```ruby
puts db.tables           # ["users", "products", ...]

cols = db.columns("users")
cols.each do |col|
  puts "#{col["name"]} (#{col["type"]})"
end
```

---

## Combining with Frankie's Stats

Query results are vectors of hashes — pipe them straight into stdlib functions:

```ruby
rows     = db.query("SELECT salary FROM employees")
salaries = rows.map do |r|
  r["salary"]
end

puts mean(salaries)    # average salary
puts stdev(salaries)   # standard deviation
puts max(salaries)     # top salary

# Or filter with select
senior_salaries = rows.select do |r|
  r["salary"] > 100000
end.map do |r|
  r["salary"]
end
puts "Senior mean: #{mean(senior_salaries)}"
```

---

## Closing the Connection

```ruby
db.close
```

Always close when done. In-memory databases are destroyed on close.

---

## Full API Reference

| Method | Description |
|---|---|
| `db_open(path)` | Open/create DB. `":memory:"` for in-memory. |
| `db.exec(sql, params)` | Run DDL/DML statement. Returns row count. |
| `db.query(sql, params)` | SELECT → vector of hashes |
| `db.query_one(sql, params)` | SELECT → first hash or nil |
| `db.insert(table, hash)` | Insert a row. Returns new row id. |
| `db.insert_many(table, rows)` | Bulk insert vector of hashes. |
| `db.find_all(table)` | All rows as vector of hashes |
| `db.find(table, where)` | Filtered rows (hash → AND) |
| `db.find_one(table, where)` | First matching row or nil |
| `db.update(table, data, where)` | Update matching rows. Returns count. |
| `db.delete(table, where)` | Delete matching rows. Returns count. |
| `db.count(table)` | Total row count |
| `db.count(table, where)` | Filtered row count |
| `db.last_id` | Rowid of last INSERT |
| `db.tables` | List of table names |
| `db.columns(table)` | Column info as vector of hashes |
| `db.transaction do...end` | Atomic block — rollback on error |
| `db.begin` | Begin explicit transaction |
| `db.commit` | Commit current transaction |
| `db.rollback` | Roll back current transaction |
| `db.close` | Close the connection |

---

## Notes

- Uses Python's built-in `sqlite3` — **no external dependencies**
- All query results are **vectors of hashes** keyed by column name (strings)
- Always use `?` placeholders for user data — never interpolate into SQL strings
- `":memory:"` databases are perfect for testing and temporary work
- File databases persist between program runs
