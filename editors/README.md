# Editor Support for Frankie

## VS Code

1. Copy the `vscode/` folder to your VS Code extensions directory:
   - **macOS/Linux:** `~/.vscode/extensions/frankie-language/`
   - **Windows:** `%USERPROFILE%\.vscode\extensions\frankie-language\`

2. Restart VS Code.

3. `.fk` files will now have syntax highlighting, bracket matching,
   and auto-indentation.

### Manual install via symlink (recommended for development)

```bash
ln -s /path/to/frankie/editors/vscode \
      ~/.vscode/extensions/frankie-language
```

---

## Vim / Neovim

1. Copy `frankie.vim` to your syntax directory:

```bash
# Vim
cp frankie.vim ~/.vim/syntax/frankie.vim

# Neovim
cp frankie.vim ~/.config/nvim/syntax/frankie.vim
```

2. Add filetype detection to `~/.vim/filetype.vim` (create if it doesn't exist):

```vim
au BufRead,BufNewFile *.fk set filetype=frankie
```

3. For Neovim, add to `~/.config/nvim/init.vim` or `init.lua`:

```vim
" init.vim
autocmd BufRead,BufNewFile *.fk set filetype=frankie
```

---

## Sublime Text

1. Open the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Select **Preferences: Browse Packages**
3. Create a folder called `Frankie/`
4. Copy `frankie.tmLanguage.json` into it, renamed to `Frankie.tmLanguage`

---

## TextMate

1. Double-click `frankie.tmLanguage.json` (rename to `frankie.tmLanguage`)
2. TextMate will install it automatically.

---

## Other editors (tmLanguage-compatible)

Any editor that supports TextMate grammar files (`.tmLanguage`) can use
`frankie.tmLanguage.json`. Editors include:

- Atom
- Zed
- Nova
- Kate (partial support)
