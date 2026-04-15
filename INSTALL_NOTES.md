# Frankie v1.14 — Update Notes

## Where each file goes

```
frankie/                          ← your existing Frankie root
├── compiler/
│   ├── lexer.py                  ← REPLACE
│   ├── ast_nodes.py              ← REPLACE
│   ├── parser.py                 ← REPLACE
│   └── codegen.py                ← REPLACE
├── docs/
│   ├── 09_web.md                 ← REPLACE
│   ├── 17_v114_features.md       ← NEW
│   ├── v114_changelog_entry.md   ← NEW — prepend to 06_changelog.md
│   ├── language_conditionals.md  ← REPLACE
│   ├── language_variables.md     ← REPLACE
│   └── examples_whats_new.md     ← REPLACE
├── stitches/
│   ├── frankietemplate.fk        ← NEW
│   └── frankiecookie.fk          ← NEW
├── examples/
│   └── test_v114.fk              ← NEW
├── frankie_stdlib.py             ← REPLACE
├── install.py                    ← REPLACE
├── scaffold.py                   ← REPLACE
├── frankie_website.html          ← REPLACE
└── README.md                     ← REPLACE

## One extra step — changelog

Open docs/06_changelog.md and paste the contents of
docs/v114_changelog_entry.md at the very top (after the # Changelog heading).

## Verify the install

After replacing the files, run:

    frankiec run examples/test_v114.fk

All tests should pass with output ending in:
    === All v1.14 tests passed ===
```
