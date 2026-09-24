#!/usr/bin/env bash
# download_stats.sh — sum GitHub release-asset download counts for Frankie.
#
# Only counts UPLOADED release assets (the tarball + .sha256 that
# .github/workflows/release.yml attaches on every vX.Y.Z tag push).
# GitHub does not track downloads of the "Source code (tar.gz)" link it
# auto-generates for every tag, so this only works because releases go
# through that workflow instead of relying on the auto-generated archive.
#
# This is a heuristic for "is anyone installing this," not a precise
# `brew install` count — it can't distinguish a Homebrew install from
# someone downloading the asset straight off the Releases page or
# curl-ing the URL from a script. It's the closest thing available for a
# personal tap, though: Homebrew's own analytics dashboard
# (formulae.brew.sh/analytics) only covers homebrew-core/homebrew-cask,
# nothing for third-party taps.
#
# Usage:
#   ./download_stats.sh                  # defaults to atejada/Frankie
#   ./download_stats.sh owner/repo       # check a different repo
#   GH_TOKEN=ghp_xxx ./download_stats.sh # optional, raises the unauthenticated
#                                         # 60-req/hr GitHub API rate limit

set -euo pipefail

REPO="${1:-atejada/Frankie}"
API="https://api.github.com/repos/${REPO}/releases"

command -v jq >/dev/null 2>&1 || { echo "error: this script needs jq (brew install jq)" >&2; exit 1; }

auth_args=()
if [ -n "${GH_TOKEN:-}" ]; then
  auth_args=(-H "Authorization: Bearer ${GH_TOKEN}")
fi

releases_json=$(curl -sSL "${auth_args[@]}" "$API")

if ! echo "$releases_json" | jq -e 'type == "array"' >/dev/null 2>&1; then
  echo "error: unexpected response from $API" >&2
  echo "$releases_json" >&2
  exit 1
fi

count=$(echo "$releases_json" | jq 'length')
if [ "$count" -eq 0 ]; then
  echo "No releases found for $REPO yet."
  exit 0
fi

echo "Downloads per release for $REPO (uploaded assets only):"
echo

total=0
while IFS=$'\t' read -r tag downloads; do
  printf "  %-14s %s\n" "$tag" "$downloads"
  total=$((total + downloads))
done < <(echo "$releases_json" | jq -r '
  sort_by(.published_at) | reverse | .[] | [
    .tag_name,
    ([.assets[].download_count] | add // 0)
  ] | @tsv
')

echo
echo "Total: $total"
