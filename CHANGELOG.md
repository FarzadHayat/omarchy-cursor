# Changelog

## 1.1.1

- Clicks land exactly where the cursor points. Arrow tips click their visible point, and centered cursors like the crosshair and I-beam no longer lean half a pixel down and right at 1.5x and 2x scaling.
- The click test on the test page measures in screen pixels and no longer leans half a pixel itself.

## 1.1.0

- Style > Cursor in the Omarchy menu switches style and size, with a ✓ on the current choice. Choices are saved in `~/.config/omarchy-pixel-cursors/config.json`.
- The wait hourglass now flips with a smooth half turn instead of jumping.
- Clearer thumb on the grabbing hand.
- The site shows cursors drawn for 100%, 150% and 200% screens, and has a tab icon and a preview card for links.

## 1.0.0

First release.

- 8-bit pixel art cursors in your Omarchy theme's colors, rebuilt on every theme switch.
- Accent, light and dark styles, and a size option, kept through theme switches.
- Drawn at every size Hyprland asks for, including each connected monitor's scale, so pixels stay square.
- Animated wait and progress cursors, and every standard cursor name.
- One line installer and an uninstaller. Settings live in `~/.config/uwsm/env.d`, so Omarchy config resets keep the cursor.
- Notification when a rebuild fails.
- Browser test area at [cursors.farzadhayat.dev](https://cursors.farzadhayat.dev/), with stock themes, your own `colors.toml`, and all three styles.
