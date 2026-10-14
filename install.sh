#!/bin/bash
# Install Omarchy Cursor, make it the active cursor, and keep it in sync with
# the Omarchy theme. Extra arguments go to build.py (e.g. --style ink).

set -euo pipefail

repo="$(cd "$(dirname "$0")" && pwd)"
bin="$HOME/.local/bin/omarchy-cursor"
hypr="$HOME/.config/hypr"

for tool in python3 rsvg-convert xcursorgen hyprcursor-util; do
  command -v "$tool" >/dev/null || { echo "Missing $tool (pacman -S librsvg xorg-xcursorgen hyprcursor)"; exit 1; }
done

# Launcher used by the theme-set hook.
mkdir -p "$(dirname "$bin")"
printf '#!/bin/bash\nexec python3 "%s/build.py" "$@"\n' "$repo" >"$bin"
chmod +x "$bin"

"$bin" --apply "$@"

# Keep the cursor across restarts.
if [[ -f $hypr/hyprland.lua ]]; then
  cat >"$hypr/cursor.lua" <<'LUA'
-- Written by omarchy-cursor install.sh
hl.env("XCURSOR_THEME", "Omarchy-Cursor")
hl.env("HYPRCURSOR_THEME", "Omarchy-Cursor")
LUA
  grep -q 'require("hypr.cursor")' "$hypr/hyprland.lua" ||
    printf '\nrequire("hypr.cursor")\n' >>"$hypr/hyprland.lua"
fi

omarchy hook install theme-set "$repo/hooks/omarchy-cursor-sync"
echo "Done. The cursor now follows your Omarchy theme."
