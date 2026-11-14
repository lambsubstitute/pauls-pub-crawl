#!/usr/bin/env bash
# Build the web export and publish it to the gh-pages branch (served by GitHub Pages).
#
#   tools/deploy_pages.sh
#
# The web preset is single-threaded, so it needs no COOP/COEP headers and runs on plain
# GitHub Pages hosting.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GODOT="${GODOT:-/Applications/Godot.app/Contents/MacOS/Godot}"
cd "$ROOT"

rm -rf build/web && mkdir -p build/web
"$GODOT" --headless --export-release "Web" build/web/index.html
touch build/web/.nojekyll

SRC_SHA="$(git rev-parse --short HEAD)"
WT="$(mktemp -d)"
trap 'git worktree remove --force "$WT" 2>/dev/null || true; rm -rf "$WT"' EXIT

if git ls-remote --exit-code --heads origin gh-pages >/dev/null 2>&1; then
  git fetch -q origin gh-pages
  git worktree add -q -B gh-pages "$WT" origin/gh-pages
else
  git worktree add -q --detach "$WT"
  git -C "$WT" checkout -q --orphan gh-pages
fi

git -C "$WT" rm -rq --ignore-unmatch . >/dev/null 2>&1 || true
cp -R build/web/. "$WT"/
git -C "$WT" add -A
if git -C "$WT" diff --cached --quiet; then
  echo "gh-pages already up to date"
else
  git -C "$WT" commit -q -m "Deploy web build from $SRC_SHA"
  git -C "$WT" push -q origin gh-pages
  echo "pushed gh-pages (build of $SRC_SHA)"
fi
