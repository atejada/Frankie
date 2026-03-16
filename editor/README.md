# Frankie Editor Support

## VS Code

### Install the extension manually

1. Copy the `editor/` folder to:
   - **macOS/Linux:** `~/.vscode/extensions/frankie-language/`
   - **Windows:** `%USERPROFILE%\.vscode\extensions\frankie-language\`

2. Restart VS Code — `.fk` files will now have syntax highlighting.

### Files in this folder

| File | Purpose |
|---|---|
| `frankie.tmLanguage.json` | TextMate grammar — syntax tokens and scopes |
| `package.json` | VS Code extension manifest |
| `language-configuration.json` | Brackets, auto-close, word patterns |

---

## Sublime Text

1. Open **Preferences → Browse Packages**
2. Create a folder called `Frankie`
3. Copy `frankie.tmLanguage.json` into it, renamed to `Frankie.tmLanguage`
4. Restart Sublime Text

---

## Other Editors

The `frankie.tmLanguage.json` file is a standard **TextMate grammar** supported by:

- **Neovim / Vim** — via `nvim-treesitter` or `vim-polyglot`
- **Atom** — place in a package folder
- **TextMate** — import directly
- **GitHub** — auto-detects `.fk` files via Linguist (with a `linguist-language` attribute)

---

## What's highlighted

- **Keywords** — `if`, `elsif`, `else`, `unless`, `while`, `until`, `for`, `do`, `end`, `def`, `return`, `begin`, `rescue`, `case`, `when`, `raise`, `require`, `next`, `break`
- **Builtins** — all stdlib functions (`sum`, `mean`, `json_parse`, `db_open`, `http_get`, etc.)
- **Literals** — strings (with interpolation `#{}`), numbers, `true`, `false`, `nil`
- **Symbols** — `:name` hash keys
- **Operators** — `|>`, `..`, `...`, `==`, `!=`, `**`, `//`, `=~`
- **Method calls** — `.upcase`, `.each`, `.select`, etc.
- **Comments** — `# line comments`
- **String interpolation** — `#{expr}` inside double-quoted strings
