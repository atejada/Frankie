# 🧟 Frankie Ledger

A terminal expense tracker in one Frankie file — SQLite storage, colored
ASCII reports, R-style statistics, and outlier detection. Where Zombie Chat
and Word Reanimator show Frankie's networking side, Ledger shows the
everyday-tool side.

## Use it

```bash
frankiec run main.fk add 12.50 lunch tacos al pastor
frankiec run main.fk add 899 tech mechanical keyboard --date 2026-07-01
frankiec run main.fk list                  # this month (--month 2026-06 | all)
frankiec run main.fk report                # totals, bars, stats, outliers
frankiec run main.fk categories            # lifetime totals per category
frankiec run main.fk export july.csv       # CSV dump (--month filters)
```

`report` prints a bar chart per category, `mean`/`median`/`stdev` straight
from Frankie's R donor, and flags anything over 3× the median as
**unusual spending** ⚡.

Data lives in `./ledger.db` (override with the `LEDGER_DB` env variable).

## Ship it

```bash
frankiec bundle main.fk -o ledger.py
alias ledger="python3 ~/bin/ledger.py"     # a real CLI tool, one file
```

## How it works

- `db_open()` + SQLite: schema created on first run, queries return
  vectors of hashes.
- **Three stitches**, shipped in this project's own `stitches/` folder and
  pinned by `stitch.lock` (`frankiec stitch verify` passes): `frankiecli`
  for argument parsing, `frankietable` for tables, `frankiecolor` for ANSI
  output.
- The bar chart is just `"█" * n` — string repetition doing data viz.
- `argv()` normalization means the same file works under `frankiec run`
  and as a bundled `python3 ledger.py`.
