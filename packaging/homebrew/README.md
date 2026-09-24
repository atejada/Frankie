# 🍺 Homebrew formula for Frankie

Everything needed for `brew install atejada/frankie/frankie`.

## One-time setup (about 10 minutes)

1. **Tag a release** in the main repo:

   ```bash
   git tag v1.22.3 && git push origin v1.22.3
   ```

   Pushing the tag triggers `.github/workflows/release.yml`, which builds
   a tarball and uploads it as a real GitHub release **asset** — not the
   `archive/refs/tags/...` link GitHub generates automatically for every
   tag. That distinction matters: GitHub tracks a download count on
   uploaded assets, but not on the auto-generated one, so this is also
   what makes `download_stats.sh` (below) able to report anything at all.

2. **Copy the `url` + `sha256`** the workflow printed into `frankie.rb`
   (replacing `REPLACE_WITH_TARBALL_SHA256`) — open the workflow run for
   the tag on GitHub → Summary tab, or compute it yourself:

   ```bash
   curl -L https://github.com/atejada/Frankie/releases/download/v1.22.3/frankie-1.22.3.tar.gz | shasum -a 256
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
   brew trust atejada/frankie     # Homebrew 6.0+: third-party taps need explicit trust
   brew install frankie
   frankiec version               # Frankie v1.22.2
   ```

   One-liner alternative (auto-taps and trusts just this formula):

   ```bash
   brew install atejada/frankie/frankie
   ```

## New releases

Tag `vX.Y.Z`, wait for `.github/workflows/release.yml` to finish (uploads
the tarball asset), copy the `url` + `sha256` it prints into the tap's
`frankie.rb`, push. Users get it with `brew upgrade frankie`.

## How many people are installing it?

There's no Homebrew dashboard for third-party taps — [formulae.brew.sh/analytics](https://formulae.brew.sh/analytics/)
only covers `homebrew-core`/`homebrew-cask`. The closest available signal
is GitHub's download count on the release asset `brew install` actually
fetches (see the `url` in `frankie.rb`):

```bash
./download_stats.sh              # sums download_count across all releases
GH_TOKEN=ghp_xxx ./download_stats.sh   # optional — raises the API rate limit
```

This is a heuristic, not a precise `brew install` count — it can't tell a
Homebrew install apart from someone downloading the asset directly from
the Releases page. It only works because releases go through the workflow
above; the auto-generated tag archive GitHub used to be linked to has no
tracked download count at all.

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
