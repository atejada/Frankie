# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is Frankie?

Frankie is a programming language that compiles to Python. It has Ruby-inspired syntax and is implemented entirely in pure Python (no external dependencies). The compiler pipeline is: `.fk` source → Lexer → AST → CodeGen → Python → `exec()`.

Current version: **1.16.2**

## Commands

```bash
# Run a program
frankiec run <file.fk>
python3 frankiec.py run <file.fk>   # without installing

# Run tests (defaults to test.fk)
frankiec test
frankiec test <specific_test.fk>

# Syntax check only
frankiec check <file.fk>

# Compile to Python (for inspection)
frankiec build <file.fk>

# Auto-format
frankiec fmt --write <file.fk>
frankiec fmt --check <file.fk>      # CI mode, exit 1 if not formatted

# Generate docs from ## comments
frankiec docs <file.fk>

# Interactive REPL
frankiec repl

# Scaffold new project
frankiec new <project_name>

# Watch and re-run on save
frankiec watch <file.fk> [--test]
```

## Architecture

### Compiler pipeline (`compiler/`)

- **`lexer.py`** — Tokenizes `.fk` source into `Token` objects (type `TT` enum + value + line/col). Raises `LexError` with line info.
- **`ast_nodes.py`** — Pure dataclasses for every AST node (no methods). All nodes inherit from `Node`.
- **`parser.py`** — Recursive-descent parser. Consumes tokens, emits AST nodes. Raises `ParseError` with the offending token attached.
- **`codegen.py`** — Walks the AST and emits Python source as a string. Uses `_py_safe()` to escape Frankie identifiers that collide with Python keywords (`?` → `_q`, `!` → `_bang`). Raises `CodeGenError`.

### Runtime

- **`frankie_stdlib.py`** — All built-in functions available in Frankie programs. Compiled programs execute via `exec()` with stdlib symbols pre-injected into the globals. The test harness uses a fresh `importlib` load of this module per test run to get a clean `_fk_test_suite` singleton.
- **`frankiec.py`** — CLI entry point. Handles `.env` auto-loading, the `exec()` harness, and friendly error formatting (maps Python exceptions to Frankie-friendly messages with source context).
- **`repl.py`** — Interactive REPL with readline, tab completion, and `~/.frankie_history`.
- **`frankie_fmt.py`** — AST-based formatter (not text-based).
- **`frankie_docs.py`** — Extracts `## doc-comments` with `@param`/`@return`/`@example` tags.
- **`scaffold.py`** — Generates new project skeleton (`main.fk`, `test.fk`, `lib/`, `data/`, `.env.example`).

### Stitches (`stitches/`)

Reusable Frankie library modules. Loaded in `.fk` files via `stitch "frankieconfig"`. Available stitches: `frankieconfig`, `frankieauth`, `frankiecache`, `frankiecli`, `frankiecolor`, `frankiecookie`, `frankieforms`, `frankiemail`, `frankiepager`, `frankieratelimit`, `frankiestring`, `frankietable`, `frankietemplate`.

### Generated Python header

Every compiled `.fk` file gets a 5-line header prepended by CodeGen. The runtime error handler subtracts 5 from traceback line numbers to map back to the `.fk` source line.

## Testing

Frankie has a built-in test harness (no external framework). Write tests in `.fk` using `assert_eq`, `assert_true`, `assert_match`, `assert_nil`, `assert_raises`, `assert_raises_typed`. The `_fk_test_suite` object tracks pass/fail counts.

## Editor support

- Vim: `editors/frankie.vim`
- VS Code extension: `editors/vscode/` (TextMate grammar + language config)
- Generic TextMate grammar: `editors/frankie.tmLanguage.json`

# Important

- Please remember to update the README, the Docs, frankiec wrapper should have the latest version baked in, and Frankie's website.
- Make sure that there are no missing functions in the codegen.py
- Can you also make a small description of the changes for the release notes?
- Showcase should be updated as well, to show examples from all versions.
