# 🍺 Homebrew formula for Frankie

Everything needed for `brew install atejada/frankie/frankie`.

## One-time setup (about 10 minutes)

1. **Tag a release** in the main repo (the formula pulls the tag tarball):

   ```bash
   git tag v1.20.0 && git push origin v1.20.0
   ```

2. **Compute the tarball checksum** and paste it into `frankie.rb`
   (replacing `REPLACE_WITH_TARBALL_SHA256`):

   ```bash
   curl -L https://github.com/atejada/Frankie/archive/refs/tags/v1.20.0.tar.gz | shasum -a 256
   ```

3. **Create the tap repository** — a GitHub repo named exactly
   `homebrew-frankie` under your account, containing:

   ```
   homebrew-frankie/
   └── Formula/
       └── frankie.rb        ← copy of this formula, sha256 filled in
   ```

4. **Install it** (and tell the world):

   ```bash
   brew tap atejada/frankie
   brew install frankie
   frankiec version          # Frankie v1.20.0 🧟
   ```

## New releases

Tag `vX.Y.Z`, update `url` + `sha256` in the tap's `frankie.rb`, push.
Users get it with `brew upgrade frankie`.

## Verifying locally before pushing

```bash
brew install --build-from-source ./frankie.rb
brew test frankie
brew audit --strict ./frankie.rb
```

## Notes

- Frankie is pure Python stdlib, so the formula's only dependency is
  `python@3.12` — no build step, no compiled extensions.
- The formula installs the whole tree into `libexec` and shims
  `bin/frankiec`; standard stitches resolve from the installed tree
  (v1.20+), with `./stitches` and `~/.frankie/stitches` taking precedence.
- Later, if Frankie clears homebrew-core's notability bar (stars/forks),
  the same formula can be submitted there — then it's just
  `brew install frankie` with no tap.
