# Omarchy Cursor

Animated cursors for [Omarchy](https://omarchy.org) that take their colors from your theme. Switch themes and the cursor rebuilds itself to match.

![Cursors in the Australia theme](preview/sheet.png)

<p align="center">
  <img src="preview/wait.gif" alt="Wait cursor" width="96"/>
  <img src="preview/progress.gif" alt="Progress cursor" width="96"/>
</p>

- Rounded vector artwork with a soft shadow, filled with your theme's accent color and outlined in whichever theme neutral gives the clearest edge.
- Animated wait and progress spinners.
- Ships as both Hyprcursor (sharp SVGs at any scale in Hyprland) and Xcursor (X11, GTK and other apps), with the usual aliases.

## Install

Needs `python3`, `librsvg`, `xorg-xcursorgen` and `hyprcursor` (all present on a stock Omarchy install).

```bash
git clone https://github.com/FarzadHayat/omarchy-cursor.git
cd omarchy-cursor
./install.sh
```

This installs the theme to `~/.local/share/icons/Omarchy-Cursor`, makes it the active cursor, keeps it across restarts via `~/.config/hypr/cursor.lua`, and adds a `theme-set` hook so it follows your theme.

## Options

```bash
./build.py --theme catppuccin --apply   # build for a specific theme
./build.py --style ink --apply          # dark body with an accent outline
./build.py --body "#f38ba8" --apply     # pick your own colors
./build.py --preview preview            # contact sheet and GIFs
```

The theme hook always rebuilds in the default style from the active theme, so these options last until your next theme switch.

## Layout

- `artwork.py`: every cursor, drawn on a 32x32 grid
- `build.py`: theme colors, SVG rendering, Xcursor and Hyprcursor packaging
- `hooks/omarchy-cursor-sync`: Omarchy `theme-set` hook
