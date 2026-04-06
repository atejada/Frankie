# Conditionals

## `if / elsif / else`

The basic conditional. The first branch whose condition is truthy runs; the rest are skipped.

```ruby
score = 85

if score >= 90
  puts "A"
elsif score >= 80
  puts "B"
elsif score >= 70
  puts "C"
else
  puts "F"
end
```

`elsif` and `else` are optional:

```ruby
if logged_in
  puts "Welcome back!"
end
```

---

## `unless`

`unless` is `if not` — runs the block when the condition is **false**. Use it when the negative reads more naturally.

```ruby
unless logged_in
  puts "Please log in."
end

# Equivalent to:
if not logged_in
  puts "Please log in."
end
```

`unless` supports `else` but not `elsif`:

```ruby
unless admin
  puts "Access denied."
else
  puts "Welcome, admin."
end
```

---

## Postfix `if` and `unless`

For single-statement conditionals, put the condition at the end. Reads like natural English.

```ruby
puts "Adult!" if age >= 18
puts "Minor!" unless age >= 18

x = 0 unless x > 0
log(event) if debug_mode
```

---

## Inline `if` Expression

`if` can produce a value. Assign it, return it, or use it inline.

```ruby
grade = if score >= 90 then "A" elsif score >= 80 then "B" else "C" end
puts grade

# Without 'then' — newline works too
label = if x > 0
  "positive"
elsif x < 0
  "negative"
else
  "zero"
end
puts label

# Assign to a variable before using in an expression
status = if active then "on" else "off" end
puts "System is #{status}"
```

A missing `else` clause evaluates to `nil`:

```ruby
title = if admin then "Admin" end
puts title   # nil if admin is false
```

---

## `case / when`

Match a value against a series of alternatives. Cleaner than a long `if/elsif` chain when testing one variable.

```ruby
day = "Monday"

case day
when "Saturday", "Sunday"
  puts "Weekend!"
when "Monday"
  puts "Start of the week."
when "Friday"
  puts "Almost there."
else
  puts "Midweek."
end
```

Multiple values in a single `when` are separated by commas — any of them triggers the branch.

### Bare `case` — condition-based

`case` without a subject works like `if/elsif` but reads more cleanly when all branches test different conditions:

```ruby
case
when x < 0
  puts "negative"
when x == 0
  puts "zero"
when x < 100
  puts "small positive"
else
  puts "large positive"
end
```

### `case` with ranges

```ruby
case score
when 90..100
  puts "A"
when 80..89
  puts "B"
when 70..79
  puts "C"
else
  puts "F"
end
```

---

## Ternary-style with Inline `if`

Frankie does not have a `? :` ternary operator. Use inline `if` instead:

```ruby
# Instead of: label = x > 0 ? "positive" : "non-positive"
label = if x > 0 then "positive" else "non-positive" end

# Or assign first, then use
status = if active then "on" else "off" end
puts "System: #{status}"
```

---

## Truthiness

Only `false` and `nil` are falsy. Everything else is truthy:

```ruby
if 0     then puts "0 is truthy" end      # prints
if ""    then puts "empty str truthy" end  # prints
if []    then puts "empty vec truthy" end  # prints
if nil   then puts "nil is truthy" end     # does not print
if false then puts "false is truthy" end   # does not print
```

This means nil checks should always be explicit:

```ruby
result = find_user(id)

# Wrong — empty vector or 0 would also be treated as "missing"
if not result
  puts "not found"
end

# Right — test for nil specifically
if result == nil
  puts "not found"
end

# Or use .nil?
if result.nil?
  puts "not found"
end
```

---

## Combining Conditions

```ruby
if age >= 18 and active
  puts "eligible"
end

if role == "admin" or role == "moderator"
  puts "elevated access"
end

if not banned
  puts "allowed"
end

# Parentheses for clarity
if (score > 50 and attempts < 3) or override
  puts "access granted"
end
```
