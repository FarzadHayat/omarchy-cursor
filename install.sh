#!/bin/bash
# Install Omarchy Cursor, make it the active cursor, and keep it in sync with
# the Omarchy theme. Extra arguments go to build.py (e.g. --body "#f38ba8") and
# are kept for every rebuild after a theme switch. Undo with ./uninstall.sh.

set -euo pipefail

repo="$(cd "$(dirname "$0")" && pwd)"
bin="$HOME/.local/bin/omarchy-cursor"
hypr="$HOME/.config/hypr"
mark="omarchy-cursor"

missing=()
command -v python3 >/dev/null || missing+=(python)
command -v xcursorgen >/dev/null || missing+=(xorg-xcursorgen)
command -v hyprcursor-util >/dev/null || missing+=(hyprcursor)
if (( ${#missing[@]} )); then
  echo "Missing packages: ${missing[*]}"
  echo "Install them with: omarchy pkg add ${missing[*]}"
  exit 1
fi

# Launcher used by the theme-set hook. It remembers the options given here.
mkdir -p "$(dirname "$bin")"
saved=""
(( $# )) && saved="$(printf ' %q' "$@")"
printf '#!/bin/bash\nexec python3 %q%s "$@"\n' "$repo/build.py" "$saved" >"$bin"
chmod +x "$bin"

"$bin" --apply

# Keep the cursor across restarts. Newer Omarchy configures Hyprland in Lua,
# older releases in hyprland.conf.
if [[ -f $hypr/hyprland.lua ]]; then
  cat >"$hypr/cursor.lua" <<LUA
-- Written by $mark install.sh
hl.env("XCURSOR_THEME", "Omarchy-Cursor")
hl.env("HYPRCURSOR_THEME", "Omarchy-Cursor")
LUA
  grep -q 'require("hypr.cursor")' "$hypr/hyprland.lua" ||
    printf '\nrequire("hypr.cursor") -- %s\n' "$mark" >>"$hypr/hyprland.lua"
elif [[ -f $hypr/hyprland.conf ]]; then
  cat >"$hypr/cursor.conf" <<CONF
# Written by $mark install.sh
env = XCURSOR_THEME,Omarchy-Cursor
env = HYPRCURSOR_THEME,Omarchy-Cursor
CONF
  grep -q 'source = ~/.config/hypr/cursor.conf' "$hypr/hyprland.conf" ||
    printf '\nsource = ~/.config/hypr/cursor.conf # %s\n' "$mark" >>"$hypr/hyprland.conf"
else
  echo "No Hyprland config found; the cursor will reset after a restart."
fi

hook="$repo/hooks/omarchy-cursor-sync"
if ! omarchy hook install theme-set "$hook" 2>/dev/null; then
  mkdir -p "$HOME/.config/omarchy/hooks/theme-set.d"
  cp "$hook" "$HOME/.config/omarchy/hooks/theme-set.d/"
  chmod +x "$HOME/.config/omarchy/hooks/theme-set.d/omarchy-cursor-sync"
fi
echo "Done. The cursor now follows your Omarchy theme."
