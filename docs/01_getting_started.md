# Getting Started with Frankie

## Requirements

- Python 3.10 or higher
- No external dependencies — pure Python standard library

## Installation

Frankie installs into its own `bin/` folder — the whole directory stays self-contained.

```bash
# 1. Unzip and enter the folder
cd frankie

# 2. Run the installer
python3 install.py

# 3. Add frankie/bin to your PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="/path/to/frankie/bin:$PATH"
```

To uninstall:
```bash
python3 install.py --uninstall
```

### Without installing

```bash
python3 frankiec.py run examples/hello.fk
./bin/frankiec run examples/hello.fk   # after install
```

## Your First Program

Create `hello.fk`:

```ruby
name = "World"
puts "Hello, #{name}!"
puts "Welcome to Frankie!"
```

Run it:
```bash
frankiec run hello.fk
```

Output:
```
Hello, World!
Welcome to Frankie!
```

## The frankiec Command

```bash
frankiec run   <file.fk>    # Run a Frankie program
frankiec build <file.fk>    # Compile to Python source (for inspection)
frankiec check <file.fk>    # Syntax check — no execution
frankiec repl               # Start the interactive REPL
frankiec version            # Show version info
```

Running `frankiec` with no arguments also launches the REPL.

## The REPL

The REPL (Read-Eval-Print Loop) lets you run Frankie interactively:

```
$ frankiec repl

  Frankie v1.1 Interactive REPL
  Type 'exit' or Ctrl+D to quit, 'help' for commands.

fk> x = 42
fk> puts x * 2
84
fk> v = [1,2,3,4,5]
fk> puts v.select do |n|
...   n > 3
... end
[4, 5]
fk> vars
Variables:
  v = [1, 2, 3, 4, 5]
  x = 42
fk> exit
```

### REPL Commands

| Command | Description |
|---|---|
| `exit` / `quit` | Exit the REPL |
| `vars` | Show all defined variables and functions |
| `clear` | Reset the session |
| `load <file.fk>` | Load a .fk file into the current session |
| `help` | Show help |

Multi-line blocks are detected automatically — just keep typing and Frankie waits for `end`.

## File Extension

Frankie source files use the `.fk` extension.

## How it Works

Frankie uses a transpilation architecture:

```
Source (.fk) → Lexer → Parser → AST → CodeGen → Python → exec()
```

Your `.fk` file is compiled to Python on the fly and executed immediately. No intermediate files are left on disk unless you use `frankiec build`.
