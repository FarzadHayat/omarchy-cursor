#!/bin/bash
# Install Omarchy Pixel Cursors, make it the active cursor, and keep it in sync
# with the Omarchy theme. Options go to build.py and are kept for every rebuild:
#   ./install.sh --style light --size 36
# Undo with ./uninstall.sh.

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

# Launcher used by the hooks. It remembers the options given here.
mkdir -p "$(dirname "$bin")"
saved=""
(( $# )) && saved="$(printf ' %q' "$@")"
printf '#!/bin/bash\nexec python3 %q%s "$@"\n' "$repo/build.py" "$saved" >"$bin"
chmod +x "$bin"

"$bin" --apply

# Keep the cursor across restarts. Omarchy reads session settings from
# ~/.config/uwsm/env.d, which its config resets leave alone. Setups without
# uwsm get the setting in their Hyprland config instead.
if [[ -d $HOME/.config/uwsm ]]; then
  mkdir -p "$HOME/.config/uwsm/env.d"
  cat >"$HOME/.config/uwsm/env.d/50-omarchy-pixel-cursors" <<ENV
# Written by $mark install.sh
export XCURSOR_THEME=Omarchy-Cursor
export HYPRCURSOR_THEME=Omarchy-Cursor
ENV
  # Older installs kept this in the Hyprland config; empty it but keep the file
  # loadable in case hyprland.lua still requires it.
  if grep -qs "Written by $mark" "$hypr/cursor.lua"; then
    printf -- '-- Moved to ~/.config/uwsm/env.d/50-omarchy-pixel-cursors by %s\n' "$mark" >"$hypr/cursor.lua"
  fi
elif [[ -f $hypr/hyprland.lua ]]; then
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
  echo "No session or Hyprland config found; the cursor will reset after a restart."
fi

# Hooks: rebuild on theme switch, re-apply size and style at login.
for pair in theme-set:omarchy-cursor-sync post-boot:omarchy-cursor-boot; do
  event="${pair%%:*}" hook="$repo/hooks/${pair#*:}"
  if ! omarchy hook install "$event" "$hook" >/dev/null 2>&1; then
    mkdir -p "$HOME/.config/omarchy/hooks/$event.d"
    cp "$hook" "$HOME/.config/omarchy/hooks/$event.d/"
    chmod +x "$HOME/.config/omarchy/hooks/$event.d/${pair#*:}"
  fi
done
echo "Done. The cursor now follows your Omarchy theme."
