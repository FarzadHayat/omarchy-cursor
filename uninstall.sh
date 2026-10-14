#!/bin/bash
# Remove Omarchy Cursor and undo everything install.sh changed.

set -uo pipefail

hypr="$HOME/.config/hypr"
icons="$HOME/.local/share/icons"
mark="omarchy-cursor"
theme="Omarchy-Cursor"

rm -f "$HOME/.local/bin/omarchy-cursor"

hook="$HOME/.config/omarchy/hooks/theme-set.d/omarchy-cursor-sync"
grep -qs "Omarchy Cursor" "$hook" && rm -f "$hook"

# Hyprland config. A require or source line we added is removed with its file;
# one that was already there keeps a harmless empty file so it still loads.
if grep -qs "Written by $mark" "$hypr/cursor.lua"; then
  if grep -q "require(\"hypr.cursor\") -- $mark" "$hypr/hyprland.lua"; then
    sed -i "/require(\"hypr.cursor\") -- $mark/d" "$hypr/hyprland.lua"
    rm -f "$hypr/cursor.lua"
  else
    printf -- '-- Cursor theme settings (emptied by %s uninstall.sh)\n' "$mark" >"$hypr/cursor.lua"
  fi
fi
if grep -qs "Written by $mark" "$hypr/cursor.conf"; then
  if grep -q "cursor.conf # $mark" "$hypr/hyprland.conf"; then
    sed -i "\|source = ~/.config/hypr/cursor.conf # $mark|d" "$hypr/hyprland.conf"
    rm -f "$hypr/cursor.conf"
  else
    printf '# Cursor theme settings (emptied by %s uninstall.sh)\n' "$mark" >"$hypr/cursor.conf"
  fi
fi

# Default cursor theme for apps that pick their own.
default="$icons/default/index.theme"
if grep -qs "Inherits=$theme" "$default"; then
  if [[ -f $default.$mark-backup ]]; then
    mv "$default.$mark-backup" "$default"
  else
    rm -f "$default"
    rmdir "$icons/default" 2>/dev/null
  fi
fi

rm -rf "${icons:?}/$theme"

if [[ $(gsettings get org.gnome.desktop.interface cursor-theme 2>/dev/null) == "'$theme'" ]]; then
  gsettings reset org.gnome.desktop.interface cursor-theme
fi
systemctl --user unset-environment XCURSOR_THEME HYPRCURSOR_THEME 2>/dev/null
command -v hyprctl >/dev/null && hyprctl setcursor Adwaita "${XCURSOR_SIZE:-24}" >/dev/null

echo "Omarchy Cursor removed. Log out and back in to clear it from running apps."
