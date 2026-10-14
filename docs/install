#!/bin/bash
# One line install for Omarchy Pixel Cursors:
#   curl -fsSL https://cursors.farzadhayat.dev/install | bash
# Clones (or updates) the repo, then runs its installer.

set -euo pipefail

repo="https://github.com/FarzadHayat/omarchy-pixel-cursors.git"
dir="$HOME/.local/share/omarchy-pixel-cursors"

if ! command -v xcursorgen >/dev/null; then
  echo "Installing xorg-xcursorgen..."
  omarchy pkg add xorg-xcursorgen
fi

if [[ -d $dir/.git ]]; then
  echo "Updating $dir..."
  git -C "$dir" pull --ff-only --quiet
else
  echo "Downloading to $dir..."
  git clone --quiet --depth 1 "$repo" "$dir"
fi

"$dir/install.sh" "$@"
