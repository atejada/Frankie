# Record

## What is a Record?

A Record is a named data object — a Hash with a declared structure and a readable name. Where a plain hash is anonymous, a Record prints as `Point(x: 3, y: 4)` and carries its type name everywhere it goes.

Records are ideal when your data has a consistent shape and a meaningful name matters — domain objects, configuration structures, function return values.

```ruby
record Point(x, y)

pt = Point(3, 4)
puts pt           # Point(x: 3, y: 4)
puts pt["x"]      # 3
puts pt["__type__"]  # Point
```

---

## Defining a Record

```ruby
record Point(x, y)
record Employee(name, dept, salary)
record Config(host, port, db, timeout)
record RGB(r, g, b)
```

`record` takes a name and a list of field names. Field names become the hash keys.

---

## Creating Instances

Call the record name as a function, passing values in order:

```ruby
record Point(x, y)
record Person(name, age, role)

pt   = Point(10, 20)
alice = Person("Alice", 30, "Engineer")
origin = Point(0, 0)

puts pt      # Point(x: 10, y: 20)
puts alice   # Person(name: Alice, age: 30, role: Engineer)
```

---

## Accessing Fields

Records are Hashes. Access fields with string keys:

```ruby
record Employee(name, dept, salary)

emp = Employee("Alice", "Engineering", 95000)

puts emp["name"]     # Alice
puts emp["dept"]     # Engineering
puts emp["salary"]   # 95000

# The type name is stored under __type__
puts emp["__type__"]   # Employee
```

---

## Records are Hashes

Every hash method and iterator works on records — they are not special objects, just hashes with a `__type__` key and a readable `puts` representation.

```ruby
record Point(x, y)
pt = Point(3, 4)

puts pt.keys     # [__type__, x, y]
puts pt.values   # [Point, 3, 4]
puts pt.size     # 3

# Merge — creates a plain hash (type info preserved)
moved = pt | {"x" => 10}
puts moved       # {__type__: Point, x: 10, y: 4}

# dig
record Config(db)
db_config = Config({host: "localhost", port: 5432})
puts db_config.dig("db", "host")   # localhost
```

---

## Records in Collections

Because records are hashes, all vector and hash iterators work on them naturally:

```ruby
record Person(name, age, dept)

people = [
  Person("Alice", 32, "Engineering"),
  Person("Bob",   25, "Marketing"),
  Person("Carol", 35, "Engineering"),
  Person("Dave",  28, "Marketing"),
  Person("Eve",   41, "Engineering")
]

# select — filter by field
engineers = people.select do |p|
  p["dept"] == "Engineering"
end
puts engineers.length   # 3

# map — transform field values
names = people.map do |p|
  p["name"]
end
puts names   # [Alice, Bob, Carol, Dave, Eve]

# sort_by
by_age = people.sort_by do |p|
  p["age"]
end
puts by_age.map do |p| "#{p["name"]} (#{p["age"]})" end
# [Bob (25), Dave (28), Alice (32), Carol (35), Eve (41)]

# group_by
by_dept = people.group_by do |p|
  p["dept"]
end
by_dept.each do |dept, members|
  puts "#{dept}: #{members.map do |m| m["name"] end.join(", ")}"
end
# Engineering: Alice, Carol, Eve
# Marketing: Bob, Dave

# each_with_object — build a salary index
salary_index = people.each_with_object({}) do |person, h|
  h[person["name"]] = person["salary"]
end
```

---

## Records vs Plain Hashes

| | Hash | Record |
|---|---|---|
| Literal syntax | `{name: "Alice"}` | `Person("Alice", 30)` |
| `puts` output | `{name: Alice, age: 30}` | `Person(name: Alice, age: 30)` |
| Type name available | No | `r["__type__"]` |
| Field order guaranteed | Yes (insertion order) | Yes (definition order) |
| All hash methods | Yes | Yes |
| All iterators | Yes | Yes |
| Best for | Arbitrary/dynamic data | Structured domain objects |

Use a plain hash when the shape is dynamic or comes from external data (JSON, CSV, DB rows). Use a Record when your code defines the shape and the name carries meaning.

---

## Modifying Records

Records are mutable — field values can be changed by key assignment:

```ruby
record Config(host, port, debug)

cfg = Config("localhost", 5432, false)
puts cfg   # Config(host: localhost, port: 5432, debug: false)

cfg["debug"] = true
cfg["port"]  = 5433
puts cfg   # Config(host: localhost, port: 5433, debug: true)
```

---

## Pattern: Factory Function

Wrap record creation in a function for validation or default values:

```ruby
record User(name, email, role, active)

def make_user(name, email, role = "viewer")
  raise "Name required" if name == nil or name == ""
  raise "Email required" if email == nil or email == ""
  User(name, email, role, true)
end

admin = make_user("Alice", "alice@example.com", "admin")
guest = make_user("Bob",   "bob@example.com")

puts admin   # User(name: Alice, email: alice@example.com, role: admin, active: true)
puts guest   # User(name: Bob, email: bob@example.com, role: viewer, active: true)
```

---

## Pattern: Records as Return Values

Records make multi-value returns self-documenting:

```ruby
record Stats(count, mean, stdev, min, max)

def describe(data)
  Stats(
    data.length,
    round(mean(data), 2),
    round(stdev(data), 2),
    min(data),
    max(data)
  )
end

result = describe([23, 45, 12, 67, 34, 89])
puts result
# Stats(count: 6, mean: 45.0, stdev: 26.74, min: 12, max: 89)

puts result["mean"]    # 45.0
puts result["min"]     # 12
```

Compared to returning a plain vector `[6, 45.0, 26.74, 12, 89]`, the record is self-describing — field names are the documentation.

---

## Quick Reference

```ruby
# Define
record Point(x, y)
record Person(name, age, role)

# Create
pt     = Point(3, 4)
person = Person("Alice", 30, "Engineer")

# Access
pt["x"]             # field value
pt["__type__"]      # "Point"

# Inspect
pt.keys             # [__type__, x, y]
pt.values           # [Point, 3, 4]
pt.has_key?("x")    # true

# Modify
pt["x"] = 10

# Merge
pt | {"x" => 99}    # {__type__: Point, x: 99, y: 4}

# In collections — all vector/hash iterators work
people.select do |p| p["dept"] == "Engineering" end
people.sort_by  do |p| p["age"] end
people.group_by do |p| p["dept"] end
people.map      do |p| p["name"] end
```
