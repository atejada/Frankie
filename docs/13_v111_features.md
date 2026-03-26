# Frankie v1.11 — New Feature Reference

## Overview

v1.11 focuses on ergonomics — removing the most common paper cuts reported by new users while staying true to the no-dependencies mantra.

| Feature | Summary |
|---|---|
| **Implicit return** | Last expression in a function body is returned automatically — `return` is now optional |
| **String `.replace(old, new)`** | Alias for `sub()` — the method new users always try first |
| **Inline `if` expression** | `x = if cond then a else b end` — `if` usable as an expression |
| **String `.format(hash)`** | `"Hello, {name}!".format({name: "Alice"})` — named-hole template form |
| **`.zip_with do |a, b|`** | Pair-wise transform two vectors in one pass |
| **Multiple return values** | `lo, hi = minmax(data)` — ergonomic pattern, documented and tested |
| **`frankiec check` boxed errors** | Parse errors now use the same boxed format as runtime errors |
| **REPL multi-line history** | `↑` recalls a full `def...end` block, not just the last line |
| **`frankiec fmt` heredoc support** | Heredoc bodies are preserved verbatim during formatting |
| **String `.delete(chars)`** | `"hello".delete("l")` → `"heo"` — already in stdlib, now documented |

---

## Implicit Return

The last expression in a function body is now the return value. `return` is still valid and useful for early exits — it simply isn't required at the end.

```ruby
def double(x)
  x * 2          # implicitly returned
end

def greet(name)
  "Hello, #{name}!"   # implicitly returned
end

def max_of(a, b)
  if a > b
    a              # if-branch returns a
  else
    b              # else-branch returns b
  end
end

puts double(7)        # 14
puts greet("Frankie") # Hello, Frankie!
puts max_of(3, 9)     # 9
```

Early return still works exactly as before:

```ruby
def find_first(v, target)
  v.each do |x|
    return x if x == target
  end
  nil
end
```

**Note:** Only the last *expression* triggers implicit return. Assignments, loops, `puts`, and control-flow statements at the end of a function still return `nil` implicitly. This matches Ruby's behaviour.

---

## String `.replace(old, new)`

Replaces the first occurrence of `old` with `new`. A simple alias for `sub()` — the method every programmer tries before remembering that Frankie uses `sub`/`gsub`.

```ruby
puts "hello world".replace("world", "Frankie")   # hello Frankie
puts "aabbcc".replace("b", "X")                  # aaXbcc  (first only)

# sub() and gsub() still work as before
puts sub("aabbcc", "b", "X")                     # aaXbcc
puts gsub("aabbcc", "b", "X")                    # aaXXcc
```

---

## Inline `if` Expression

`if` can now be used as an expression. The result of the chosen branch becomes the value of the expression.

```ruby
x = 7
label = if x > 5 then "big" else "small" end
puts label    # big

# Useful inline:
puts if true then "yes" else "no" end   # yes

# In assignments and function args:
score = 95
grade = if score >= 90 then "A" elsif score >= 80 then "B" else "C" end
puts grade    # A

# No else clause returns nil:
note = if false then "something" end
puts note     # nil
```

The `then` keyword is optional when using a newline:

```ruby
result = if x > 0
  "positive"
else
  "non-positive"
end
```

---

## String `.format(hash)`

Named-hole string formatting using `{key}` placeholders. A method form of the existing `template()` function, for when the template is already stored in a variable.

```ruby
puts "Hello, {name}! You are {age}.".format({name: "Alice", age: 30})
# Hello, Alice! You are 30.

tmpl = "Order #{id}: {qty} x {item} @ ${price}"
puts tmpl.format({id: 42, qty: 3, item: "coffee", price: "4.50"})
# Order 42: 3 x coffee @ $4.50

# template() still works identically with {{key}} syntax
puts template("Hello, {{name}}!", {name: "Bob"})
```

Note: `.format(hash)` uses `{key}` syntax; `template()` uses `{{key}}` syntax. Pick the style that reads more naturally for your use case.

---

## `.zip_with do |a, b|`

Pair-wise transform two vectors in one pass — the missing piece between `.zip` and `.map`.

```ruby
a = [1, 2, 3]
b = [10, 20, 30]

sums = a.zip_with(b) do |x, y| x + y end
puts sums    # [11, 22, 33]

# Products:
puts [2, 3, 4].zip_with([5, 6, 7]) do |x, y| x * y end   # [10, 18, 28]

# Build records:
names  = ["Alice", "Bob", "Carol"]
scores = [95, 87, 92]
rows = names.zip_with(scores) do |n, s|
  {name: n, score: s}
end
rows.each do |r|
  puts "#{r["name"]}: #{r["score"]}"
end
```

Stops at the shorter vector, matching `.zip` behaviour.

---

## Multiple Return Values (via destructuring)

No new syntax — this is a documentation and convention pattern. Functions return a vector; the caller destructures it.

```ruby
def minmax(v)
  [min(v), max(v)]    # implicit return of a two-element vector
end

lo, hi = minmax([3, 1, 4, 1, 5, 9, 2, 6])
puts "min=#{lo}, max=#{hi}"   # min=1, max=9

def stats(v)
  [mean(v), median(v), stdev(v)]
end

avg, med, sd = stats([10, 20, 30, 40, 50])
puts "mean=#{avg}, median=#{med}, stdev=#{sd}"
```

Pairs naturally with implicit return — the last expression (the vector literal) is returned without an explicit `return`.

---

## `frankiec check` Boxed Error Output

Syntax errors from `frankiec check` now use the same boxed error display as runtime errors — consistent file path, line number, and source pointer.

```
╔══ Frankie Compile Error ══════════════════════════════
║  [Parse Error] Line 4, Col 3: Expected 'end' to close 'if'
║
║  File: my_script.fk
║     2 │ if x > 0
║     3 │   puts "positive"
║  ──▶  4 │ puts "done"
║     5 │
╚═══════════════════════════════════════════════════════
```

Exit code is still 0 for clean files, 1 for errors — CI pipelines are unaffected.

---

## REPL Multi-line History Recall

Pressing `↑` in the REPL now recalls a complete multi-line block as a single unit. Previously, each line of a `def...end` was stored separately, making re-editing cumbersome.

```
fk> def square(x)
...   x * x
... end
fk> square(5)
25
fk>          ← press ↑ twice to get the full def back
fk> def square(x)
...   x * x
... end
```

Under the hood: when a block is submitted, Frankie removes the individual line entries and replaces them with a single joined entry in `~/.frankie_history`.

---

## `frankiec fmt` Heredoc Support

The auto-formatter now handles heredoc strings correctly. Previously, heredoc bodies were run through the string formatter and could be corrupted. v1.11 detects multiline string literals and emits them as `<<~HEREDOC` blocks with their content preserved verbatim.

```ruby
# Before v1.11: formatter would mangle the indentation
# After v1.11: body is preserved, delimiter is standardised to <<~HEREDOC

query = <<~SQL
  SELECT name, dept
  FROM employees
  WHERE salary > #{threshold}
SQL
```

---

## String `.delete(chars)` — Now Documented

`_fk_str_delete` has been in the stdlib since v1.1 but wasn't surfaced in the language reference. It's now a first-class documented method.

```ruby
puts "hello world".delete("lo")    # he wrd  (removes all l and o chars)
puts "abc123def".delete("0-9")     # not a range — removes chars '0','-','9'
puts "hello".delete("aeiou")       # hll
```

Note: `.delete(chars)` removes every character in the `chars` string — it is not regex-based.
