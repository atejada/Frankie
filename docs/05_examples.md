# Example Programs

All examples live in the `examples/` folder. Run any of them with:

```bash
frankiec run examples/<name>.fk
```

---

## hello.fk — Hello World

The classic first program.

```ruby
name = "World"
puts "Hello, #{name}!"
puts "Welcome to Frankie — stitched together from the finest languages."
```

---

## fizzbuzz.fk — FizzBuzz

Classic FizzBuzz using `for..in` and `elsif`.

```ruby
for i in 1..100
  if i % 15 == 0
    puts "FizzBuzz"
  elsif i % 3 == 0
    puts "Fizz"
  elsif i % 5 == 0
    puts "Buzz"
  else
    puts i
  end
end
```

---

## fibonacci.fk — Recursive Fibonacci

Demonstrates recursive functions.

```ruby
def fibonacci(n)
  if n <= 1
    return n
  end
  return fibonacci(n - 1) + fibonacci(n - 2)
end

for i in 0..10
  puts "fib(#{i}) = #{fibonacci(i)}"
end
```

---

## stats.fk — Statistical Analysis

R-heritage in action — vectors, statistics, and the pipe operator.

```ruby
data = [23, 45, 12, 67, 34, 89, 15, 56, 78, 42]

puts "Mean   : #{mean(data)}"
puts "StdDev : #{stdev(data)}"
puts "Median : #{median(data)}"

# Pipe operator
data |> sum |> puts

# Vectorized operations
v = [1, 2, 3, 4, 5]
puts v * 2          # [2, 4, 6, 8, 10]
```

---

## sorting.fk — Sorting Algorithms

Bubble sort and selection sort implemented in Frankie, plus the built-in `.sort`.

---

## hashmaps.fk — Full Hashmap Tour

Covers all 12 hash features: create, read, write, iterate, merge, nest,
delete, fetch, build dynamically, hash of vectors.

---

## leds.fk — 7-Segment LED Display

Displays numbers as 3-row ASCII LED digits. Translated from Ruby.

```ruby
leds = {
  0: [' _  ', '| | ', '|_| '],
  1: ['  ',   '| ',   '| '  ],
  # ...
}

print "Enter a number: "
number = input("")

for i in 0...3
  for j in 0...length(number)
    print leds[to_int(number[j])][i]
  end
  puts ""
end
```

Try: `echo "12345" | frankiec run examples/leds.fk`

---

## calculator.fk — Terminal Calculator

An interactive menu-driven calculator with all four operations, powers,
square roots, and statistical analysis of a list.

---

## greet.fk — Interactive Greeter

A simple interactive terminal app using `input` and `input_int`.

---

## test_errors.fk — Error Handling

Demonstrates `begin/rescue/ensure/end` and `raise`.

```ruby
begin
  raise "something broke"
rescue e
  puts "Rescued: #{e}"
ensure
  puts "This always runs"
end
```

---

## test_regex.fk — Regex

Full regex showcase: `matches`, `match`, `match_all`, `sub`, `gsub`,
`=~`, case-insensitive patterns, and email validation.

---

## showcase.fk — Everything in One

A tour of all Frankie v1.0+ features in a single file:
error handling, regex, file I/O, named arguments, slicing,
nil-safe hashes, and a mini log analyser.

---

## Writing Your Own

A typical Frankie program structure:

```ruby
# myprogram.fk

# 1. Define any helper functions
def greet(name)
  return "Hello, #{name}!"
end

# 2. Main logic at top level
name = input("Your name: ")
age  = input_int("Your age: ")

puts greet(name)

case
when age < 18
  puts "You're young!"
when age < 60
  puts "You're in your prime!"
else
  puts "Seasoned wisdom!"
end

# 3. Use stdlib freely
data = [age, age * 2, age // 2]
puts "Mean of your age variants: #{mean(data)}"
```

Run it:
```bash
frankiec run myprogram.fk
```
