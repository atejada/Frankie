# DateTime

## Overview

Frankie has a built-in DateTime type for working with dates and times — no external libraries required. DateTime objects are created by functions like `now()`, `today()`, and `date_parse()`, and support arithmetic, formatting, comparison, and field access.

---

## Creating DateTime Values

### `now()` — Current date and time

```ruby
dt = now()
puts dt   # Date(2024-03-15 14:23:07.123456)
```

### `today()` — Today at midnight

```ruby
d = today()
puts d.year    # 2024
puts d.month   # 3
puts d.day     # 15
```

### `date_parse(str, fmt)` — Parse a string

Default format is `"%Y-%m-%d"`. Pass a custom format string as the second argument.

```ruby
d = date_parse("2024-03-15")
puts d.year    # 2024
puts d.month   # 3
puts d.day     # 15

# Custom format
d2 = date_parse("15/03/2024", "%d/%m/%Y")
puts d2.year   # 2024

d3 = date_parse("March 15, 2024", "%B %d, %Y")
puts d3.month  # 3
```

### `date_from(year, month, day, hour, minute, second)` — Build from components

Hour, minute, and second default to 0.

```ruby
d = date_from(2024, 3, 15)
puts d   # Date(2024-03-15 00:00:00)

dt = date_from(2024, 3, 15, 14, 30, 0)
puts dt  # Date(2024-03-15 14:30:00)
```

---

## Accessing Fields

```ruby
dt = date_from(2024, 3, 15, 14, 30, 45)

puts dt.year     # 2024
puts dt.month    # 3
puts dt.day      # 15
puts dt.hour     # 14
puts dt.minute   # 30
puts dt.second   # 45
```

---

## Formatting

Use `strftime` format codes:

```ruby
dt = date_from(2024, 3, 15, 14, 30, 0)

puts dt.format("%Y-%m-%d")            # 2024-03-15
puts dt.format("%d/%m/%Y")            # 15/03/2024
puts dt.format("%B %d, %Y")          # March 15, 2024
puts dt.format("%A")                  # Friday
puts dt.format("%H:%M:%S")            # 14:30:00
puts dt.format("%Y-%m-%d %H:%M:%S")  # 2024-03-15 14:30:00
puts dt.format("%d %b %Y %I:%M %p")  # 15 Mar 2024 02:30 PM
```

### Common Format Codes

| Code | Meaning | Example |
|---|---|---|
| `%Y` | 4-digit year | `2024` |
| `%m` | Month (01–12) | `03` |
| `%d` | Day (01–31) | `15` |
| `%H` | Hour 24h (00–23) | `14` |
| `%I` | Hour 12h (01–12) | `02` |
| `%M` | Minute (00–59) | `30` |
| `%S` | Second (00–59) | `00` |
| `%A` | Full weekday name | `Friday` |
| `%a` | Short weekday name | `Fri` |
| `%B` | Full month name | `March` |
| `%b` | Short month name | `Mar` |
| `%p` | AM/PM | `PM` |

---

## Arithmetic

### `.add_days(n)` — Add days

Returns a new DateTime. Negative values subtract.

```ruby
d = date_from(2024, 3, 15)
puts d.add_days(7).format("%Y-%m-%d")    # 2024-03-22
puts d.add_days(-1).format("%Y-%m-%d")   # 2024-03-14
puts d.add_days(30).format("%Y-%m-%d")   # 2024-04-14
```

### `.add_hours(n)` — Add hours

```ruby
dt = date_from(2024, 3, 15, 10, 0, 0)
puts dt.add_hours(5).format("%H:%M")    # 15:00
puts dt.add_hours(48).format("%Y-%m-%d %H:%M")  # 2024-03-17 10:00
```

### `.add_minutes(n)` — Add minutes

```ruby
dt = date_from(2024, 3, 15, 14, 45, 0)
puts dt.add_minutes(20).format("%H:%M")    # 15:05
puts dt.add_minutes(-30).format("%H:%M")   # 14:15
```

---

## Comparison

### `.is_before(other)` / `.is_after(other)`

```ruby
a = date_from(2024, 1, 1)
b = date_from(2024, 6, 1)

puts a.is_before(b)   # true
puts a.is_after(b)    # false
puts b.is_after(a)    # true
```

---

## Difference

### `.diff_days(other)` — Days between two dates

```ruby
start_date = date_from(2024, 1, 1)
end_date   = date_from(2024, 3, 15)

puts start_date.diff_days(end_date)   # 74
```

### `.diff_seconds(other)` — Seconds between two datetimes

```ruby
a = date_from(2024, 3, 15, 9, 0, 0)
b = date_from(2024, 3, 15, 11, 30, 0)

puts a.diff_seconds(b)   # 9000  (2.5 hours)
```

---

## Weekday

### `.weekday` — Day of week as integer

Returns 0 (Monday) through 6 (Sunday).

```ruby
d = date_from(2024, 3, 15)   # a Friday
puts d.weekday   # 4

days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
puts days[d.weekday]   # Friday
```

---

## Unix Timestamp

### `.timestamp` — Seconds since epoch

```ruby
dt = now()
puts dt.timestamp   # e.g. 1710507787.123456
```

---

## Practical Examples

```ruby
# Age calculator
def age_in_years(birth_str)
  birth    = date_parse(birth_str)
  today_dt = today()
  years    = today_dt.year - birth.year
  # Adjust if birthday hasn't occurred yet this year
  if today_dt.month < birth.month
    years -= 1
  elsif today_dt.month == birth.month and today_dt.day < birth.day
    years -= 1
  end
  years
end

puts age_in_years("1990-06-15")

# Days until an event
def days_until(date_str)
  target = date_parse(date_str)
  today().diff_days(target)
end

puts "Days until event: #{days_until("2024-12-31")}"

# Format a range of dates
start_dt = date_from(2024, 3, 1)
7.times do |i|
  d = start_dt.add_days(i)
  puts d.format("%A, %B %d")
end
# Friday, March 01
# Saturday, March 02
# ...

# Timestamp a log entry
def log(msg)
  ts = now().format("%Y-%m-%d %H:%M:%S")
  file_append("app.log", "[#{ts}] #{msg}\n")
end

log("Application started")
log("User Alice logged in")

# Check if a date has passed
deadline = date_parse("2024-06-01")
if today().is_after(deadline)
  puts "Deadline has passed"
else
  puts "#{today().diff_days(deadline)} days remaining"
end
```

---

## Quick Reference

| Function / Method | Description |
|---|---|
| `now()` | Current date and time |
| `today()` | Today at midnight |
| `date_parse(str, fmt)` | Parse string → DateTime |
| `date_from(y, m, d, h, min, s)` | Build from components |
| `.year` `.month` `.day` | Date components |
| `.hour` `.minute` `.second` | Time components |
| `.format(fmt)` | Format with strftime codes |
| `.add_days(n)` | Add n days (negative to subtract) |
| `.add_hours(n)` | Add n hours |
| `.add_minutes(n)` | Add n minutes |
| `.diff_days(other)` | Days between two dates |
| `.diff_seconds(other)` | Seconds between two datetimes |
| `.weekday` | 0=Monday … 6=Sunday |
| `.is_before(other)` | True if earlier |
| `.is_after(other)` | True if later |
| `.timestamp` | Unix timestamp as float |
