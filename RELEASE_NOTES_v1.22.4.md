# Frankie v1.22.4 — patch release 🐛

- **Python-keyword names no longer crash.** Using a name such as `pass`, `class` or `global` as a `for` loop variable, a destructuring target (`a, b = ...` or `{x, y} = hash`), a lambda parameter or a `rescue` variable produced invalid Python and failed at runtime with "invalid syntax". All of these now use the same keyword-safe renaming as ordinary assignments. `for pass in 1..100` works.

This is a bug-fix-only release under the language freeze — no new syntax, no stdlib changes.
