# Getting Started with Frankie

## Requirements

- Python 3.10 or higher
- No external dependencies — pure Python standard library

## Installation

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
```

## Your First Program

Create `hello.fk`:

```ruby
name = "World"
puts "Hello, #{name}!"
puts "Welcome to Frankie v1.7!"
```

Run it:
```bash
frankiec run hello.fk
```

Output:
```
Hello, World!
Welcome to Frankie v1.7!
```

## CLI Commands

| Command | Description |
|---|---|
| `frankiec run <file.fk>` | Compile and run a Frankie program |
| `frankiec build <file.fk>` | Compile to Python source (for inspection) |
| `frankiec check <file.fk>` | Syntax check — no execution |
| `frankiec test [file.fk]` | Run test suite (default: `test.fk`) |
| `frankiec new <project>` | Scaffold a new project |
| `frankiec repl` | Start the interactive REPL |
| `frankiec version` | Show version info |

Running `frankiec` with no arguments also launches the REPL.

## The REPL

The REPL (Read-Eval-Print Loop) lets you run Frankie interactively:

```
$ frankiec repl

  Frankie v1.7 Interactive REPL
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

Multi-line blocks are detected automatically — keep typing and Frankie waits for `end`.

## Project Scaffolding

```bash
frankiec new myapp
```

Creates:

```
myapp/
├── main.fk          ← entry point
├── test.fk          ← test suite
├── lib/
│   └── utils.fk     ← reusable utilities
├── data/            ← JSON, CSV, SQLite files
├── .gitignore
├── .env.example
└── README.md
```

Then:

```bash
cd myapp
frankiec run main.fk
frankiec test
frankiec repl
```

## How it Works

```
Source (.fk) → Lexer → Parser → AST → CodeGen → Python → exec()
```

Your `.fk` file is compiled to Python on the fly and executed immediately.
No intermediate files are left on disk unless you use `frankiec build`.
