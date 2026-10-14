#!/usr/bin/env python3
"""Build the Omarchy Cursor theme in the colors of an Omarchy theme.

Renders the pixel art in pixelart.py to PNGs at whole number scales, then
packages it as both an Xcursor theme (for X11, GTK and most apps) and a
Hyprcursor theme (for Hyprland).

Needs: python 3.11+, xcursorgen, hyprcursor-util.
"""

import argparse
import colorsys
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

import pixelart

THEME_NAME = "Omarchy-Cursor"
SITE_DOMAIN = "cursors.farzadhayat.dev"
SIZES = [24, 32, 36, 48, 64, 72, 96]
ROOT = Path(__file__).resolve().parent
HOME = Path.home()
THEME_DIRS = [
    HOME / ".config/omarchy/themes",
    HOME / ".local/share/omarchy/themes",
    Path("/usr/share/omarchy/themes"),
]
CURRENT_THEME_DIRS = [
    HOME / ".local/state/omarchy/current/theme",
    HOME / ".config/omarchy/current/theme",
]
FALLBACK_COLORS = {
    "mode": "dark",
    "accent": "#7aa2f7",
    "background": "#1a1b26",
    "foreground": "#c0caf5",
    "red": "#f7768e",
}


# ── Colors ────────────────────────────────────────────────


def rgb(hex_color):
    h = hex_color.strip().lstrip("#")[:6]
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def to_hex(c):
    return "#" + "".join(f"{round(max(0, min(1, v)) * 255):02x}" for v in c)


def mix(a, b, t):
    ca, cb = rgb(a), rgb(b)
    return to_hex(tuple(x + (y - x) * t for x, y in zip(ca, cb)))


def luminance(hex_color):
    def lin(v):
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = (lin(v) for v in rgb(hex_color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def saturate(hex_color, amount):
    h, l, s = colorsys.rgb_to_hls(*rgb(hex_color))
    return to_hex(colorsys.hls_to_rgb(h, l, min(1, s * amount)))


def load_colors(theme):
    """Colors from a named theme, a theme directory, or the active theme."""
    if theme:
        candidates = [Path(theme)] + [d / theme for d in THEME_DIRS]
    else:
        candidates = CURRENT_THEME_DIRS
    for directory in candidates:
        path = directory / "colors.toml"
        if path.is_file():
            data = tomllib.loads(path.read_text())
            return {**FALLBACK_COLORS, **{k: v for k, v in data.items() if isinstance(v, str)}}, directory
    if theme:
        sys.exit(f"Theme not found: {theme}")
    return dict(FALLBACK_COLORS), None


class Palette:
    """Turns theme colors into the handful of roles the artwork uses."""

    def __init__(self, colors, overrides=None):
        accent = colors["accent"]
        dark = colors.get("darker_background") or colors.get("dark_background") or colors["background"]
        light = colors.get("bright_foreground") or colors.get("light_foreground") or colors["foreground"]
        if colors.get("mode") == "light":
            dark, light = (colors.get("foreground") or dark), (colors.get("background") or light)
        dark = mix(dark, "#000000", 0.25) if luminance(dark) > 0.02 else dark

        # Accent body with whichever theme neutral gives the strongest edge.
        overrides = overrides or {}
        self.body = overrides.get("body") or accent
        self.rim = overrides.get("rim") or max((dark, light), key=lambda c: contrast(c, self.body))
        self.head = mix(self.body, "#ffffff", 0.45 if luminance(self.body) < 0.5 else 0.7)
        self.hi = mix(self.body, "#ffffff", 0.35)
        self.lo = mix(self.body, "#000000", 0.22)
        self.track = mix(self.body, self.rim, 0.6)
        danger = colors.get("red") or "#e05561"
        if contrast(danger, self.rim) < 2.4:
            danger = saturate(mix(danger, "#ffffff" if luminance(self.rim) < 0.3 else "#000000", 0.35), 1.2)
        self.danger = danger
        self.danger_hi = mix(danger, "#ffffff", 0.22)
        self.danger_lo = mix(danger, "#000000", 0.12)
        self.shadow = 0.5 if luminance(self.rim) < 0.2 else 0.35


# ── Packaging ─────────────────────────────────────────────


def need(*tools):
    missing = [t for t in tools if not shutil.which(t)]
    if missing:
        sys.exit(f"Missing tools: {', '.join(missing)}")


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)


def png_colors(pal):
    colors = {key: tuple(round(v * 255) for v in rgb(getattr(pal, name))) + (255,)
              for key, name in pixelart.KEYS.items()}
    colors["shadow"] = (0, 0, 0, round(255 * pal.shadow * 0.8))
    return colors


def render(cursors, pal, work, hypr_dir):
    """Pixel art PNGs at whole number scales so every art pixel stays square."""
    colors = png_colors(pal)
    scales = {s: max(1, round(s / pixelart.CANVAS)) for s in SIZES}
    xlines = {}
    for cur in cursors:
        sdir = hypr_dir / cur.name
        sdir.mkdir()
        pdir = work / "png" / cur.name
        pdir.mkdir(parents=True)
        hx, hy = cur.hotspot
        meta = [
            "resize_algorithm = nearest",
            f"hotspot_x = {(hx + 0.5) / pixelart.CANVAS:.4f}",
            f"hotspot_y = {(hy + 0.5) / pixelart.CANVAS:.4f}",
            "nominal_size = 1.0",
        ]
        if cur.aliases:
            meta.append("define_override = " + ";".join(cur.aliases))
        delay = f", {cur.delay}" if cur.delay else ""
        lines = []
        for i, grid in enumerate(cur.frames):
            finished = pixelart.finish(grid)
            for k in sorted(set(scales.values())):
                (sdir / f"{cur.name}-{k}x-{i:02d}.png").write_bytes(pixelart.png(finished, colors, k))
                meta.append(f"define_size = {pixelart.CANVAS * k}, {cur.name}-{k}x-{i:02d}.png{delay}")
            for s, k in scales.items():
                png = pdir / f"{s}-{i:02d}.png"
                shutil.copy(sdir / f"{cur.name}-{k}x-{i:02d}.png", png)
                lines.append(f"{s} {hx * k + k // 2} {hy * k + k // 2} {png}"
                             + (f" {cur.delay}" if cur.delay else ""))
        (sdir / "meta.hl").write_text("\n".join(meta) + "\n")
        xlines[cur.name] = lines
    return xlines


def build(pal, out):
    """Write a complete theme into out (which must not exist yet)."""
    need("xcursorgen", "hyprcursor-util")
    cursors = list(pixelart.all_cursors())
    work = Path(tempfile.mkdtemp(prefix="omarchy-cursor-"))
    try:
        hypr_src = work / "hypr"
        (hypr_src / "hyprcursors").mkdir(parents=True)
        xlines = render(cursors, pal, work, hypr_src / "hyprcursors")

        out.mkdir(parents=True)
        xdir = out / "cursors"
        xdir.mkdir()
        for cur in cursors:
            cfg = work / f"{cur.name}.cfg"
            cfg.write_text("\n".join(xlines[cur.name]) + "\n")
            run(["xcursorgen", str(cfg), str(xdir / cur.name)])
            for alias in cur.aliases:
                if not (xdir / alias).exists():
                    (xdir / alias).symlink_to(cur.name)

        (hypr_src / "manifest.hl").write_text(
            f"name = {THEME_NAME}\n"
            "description = Animated, theme adaptive 8-bit cursors for Omarchy\n"
            "version = 2.0\n"
            "cursors_directory = hyprcursors\n"
        )
        hypr_out = work / "hypr-out"
        hypr_out.mkdir()
        run(["hyprcursor-util", "--create", str(hypr_src), "--output", str(hypr_out)])
        packed = next(hypr_out.iterdir())
        shutil.copy(packed / "manifest.hl", out / "manifest.hl")
        shutil.copytree(packed / "hyprcursors", out / "hyprcursors")

        (out / "index.theme").write_text(
            f"[Icon Theme]\nName={THEME_NAME}\nComment=Animated, theme adaptive 8-bit cursors for Omarchy\n"
            "Inherits=Adwaita\n"
        )
        (out / "cursor.theme").write_text(f"[Icon Theme]\nInherits={THEME_NAME}\n")
        return cursors, work
    except BaseException:
        shutil.rmtree(work, ignore_errors=True)
        raise


def install(staged, dest):
    """Swap the new theme into place so apps never see a half written theme."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    old = dest.with_name(dest.name + ".old")
    shutil.rmtree(old, ignore_errors=True)
    if dest.exists():
        dest.rename(old)
    shutil.move(str(staged), str(dest))
    shutil.rmtree(old, ignore_errors=True)


def apply(size):
    # Apps that load cursors themselves read these, or fall back to the "default" theme.
    default = HOME / ".local/share/icons/default/index.theme"
    default.parent.mkdir(parents=True, exist_ok=True)
    backup = default.with_name("index.theme.omarchy-cursor-backup")
    if default.exists() and f"Inherits={THEME_NAME}" not in default.read_text() and not backup.exists():
        default.rename(backup)  # uninstall.sh puts it back
    default.write_text(f"[Icon Theme]\nInherits={THEME_NAME}\n")
    env = [f"XCURSOR_THEME={THEME_NAME}", f"HYPRCURSOR_THEME={THEME_NAME}"]
    if shutil.which("systemctl"):
        subprocess.run(["systemctl", "--user", "set-environment", *env])
    if shutil.which("dbus-update-activation-environment"):
        subprocess.run(["dbus-update-activation-environment", *env])
    if shutil.which("hyprctl"):
        subprocess.run(["hyprctl", "setcursor", THEME_NAME, str(size)], stdout=subprocess.DEVNULL)
    if shutil.which("gsettings"):
        subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "cursor-theme", THEME_NAME])
        subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "cursor-size", str(size)])


def preview(cursors, work, pal, colors, dest):
    """Contact sheet on the theme background plus GIFs of the animated cursors."""
    need("magick")
    dest.mkdir(parents=True, exist_ok=True)
    size = 64
    tiles = []
    for cur in cursors:
        tiles += ["(", str(work / "png" / cur.name / f"{size}-00.png"), "-set", "label", cur.name, ")"]
    font = []
    if shutil.which("fc-match"):
        path = subprocess.run(["fc-match", "-f", "%{file}", "monospace:style=Bold"],
                              capture_output=True, text=True).stdout.strip()
        font = ["-font", path] if path else []
    for name, bg, fg in [("dark", colors["background"], colors["foreground"]),
                         ("light", "#eceff4", "#2e3440")]:
        run(["magick", "montage", *tiles, "-tile", "8x", "-geometry", "96x96+22+14", *font,
             "-background", bg, "-fill", fg, "-pointsize", "14", str(dest / f"sheet-{name}.png")])
    for cur in cursors:
        if len(cur.frames) > 1:
            frames = sorted((work / "png" / cur.name).glob("96-*.png"))
            run(["magick", "-delay", str(max(2, cur.delay // 10)), "-dispose", "background",
                 *map(str, frames), "-background", colors["background"], "-alpha", "remove",
                 "-loop", "0", str(dest / f"{cur.name}.gif")])


def test_page(dest, hosted=False):
    """Theme colors and pixel art for test.html, which draws the cursors itself.

    A hosted page only uses the stock Omarchy themes and opens on a theme,
    since visitors do not have the cursor installed.
    """
    themes = {}
    for directory in reversed(THEME_DIRS[-1:] if hosted else THEME_DIRS):  # user themes override stock
        if directory.is_dir():
            for path in sorted(directory.iterdir()):
                if (path / "colors.toml").is_file():
                    themes[path.name] = path
    if hosted:
        active = "tokyo-night" if "tokyo-night" in themes else next(iter(sorted(themes)), None)
    else:
        active = HOME / ".local/state/omarchy/current/theme.name"
        active = active.read_text().strip() if active.is_file() else None
    keys = ("mode", "accent", "background", "foreground", "red", "darker_background",
            "dark_background", "bright_foreground", "light_foreground")
    data = {
        "active": active,
        "hosted": hosted,
        "themes": {name: {k: v for k, v in load_colors(str(path))[0].items() if k in keys}
                   for name, path in sorted(themes.items())},
        "art": {cur.name: {"hotspot": list(cur.hotspot), "delay": cur.delay,
                           "frames": [["".join("%" if c == "shadow" else c for c in row)
                                       for row in pixelart.finish(g)] for g in cur.frames]}
                for cur in pixelart.all_cursors()},
    }
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("window.CURSOR_THEMES = " + json.dumps(data, separators=(",", ":")) + ";\n")
    print(f"Wrote {len(themes)} themes to {dest}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--theme", help="Omarchy theme name or directory (default: active theme)")
    parser.add_argument("--body", help="override body color (#hex)")
    parser.add_argument("--rim", help="override rim color (#hex)")
    parser.add_argument("--out", type=Path, default=ROOT / "build" / THEME_NAME, help="build output")
    parser.add_argument("--install", action="store_true", help=f"install to ~/.local/share/icons/{THEME_NAME}")
    parser.add_argument("--apply", action="store_true", help="make it the active cursor (implies --install)")
    parser.add_argument("--size", type=int, default=int(os.environ.get("XCURSOR_SIZE") or 24))
    parser.add_argument("--preview", type=Path, metavar="DIR", help="write preview sheets and GIFs")
    parser.add_argument("--test-page", action="store_true", help="render every theme for test.html")
    parser.add_argument("--site", type=Path, metavar="DIR", help="write a hosted copy of the test page")
    args = parser.parse_args()

    if args.test_page:
        test_page(ROOT / "test" / "themes.js")
        return
    if args.site:
        test_page(args.site / "themes.js", hosted=True)
        page = (ROOT / "test.html").read_text().replace('src="test/themes.js"', 'src="themes.js"')
        page = page.replace("<title>Omarchy Pixel Cursors test area</title>", "<title>Omarchy Pixel Cursors</title>")
        (args.site / "index.html").write_text(page)
        shutil.copy(ROOT / "cursors.js", args.site / "cursors.js")
        (args.site / "CNAME").write_text(f"{SITE_DOMAIN}\n")  # custom domain for GitHub Pages
        print(f"Wrote site to {args.site}")
        return

    colors, source = load_colors(args.theme)
    pal = Palette(colors, {"body": args.body, "rim": args.rim})
    print(f"Colors from {source or 'built in fallback'}: body {pal.body}, rim {pal.rim}")

    staged = Path(tempfile.mkdtemp(prefix="omarchy-cursor-out-")) / THEME_NAME
    cursors, work = build(pal, staged)
    try:
        if args.preview:
            preview(cursors, work, pal, colors, args.preview)
        if args.install or args.apply:
            dest = HOME / ".local/share/icons" / THEME_NAME
            install(staged, dest)
            print(f"Installed {len(cursors)} cursors to {dest}")
            if args.apply:
                apply(args.size)
                print(f"Applied {THEME_NAME} at size {args.size}")
                if (ROOT / "test" / "themes.js").exists():  # keep test.html's active theme current
                    test_page(ROOT / "test" / "themes.js")
        else:
            shutil.rmtree(args.out, ignore_errors=True)
            args.out.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(staged), str(args.out))
            print(f"Built {len(cursors)} cursors in {args.out}")
    finally:
        shutil.rmtree(work, ignore_errors=True)
        shutil.rmtree(staged.parent, ignore_errors=True)


if __name__ == "__main__":
    main()
