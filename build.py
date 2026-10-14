#!/usr/bin/env python3
"""Build the Omarchy Cursor theme in the colors of an Omarchy theme.

Renders the artwork in artwork.py to SVG, then packages it as both an
Xcursor theme (for X11, GTK and most apps) and a Hyprcursor theme (for
Hyprland, which draws the SVGs directly so they stay sharp at any scale).

Needs: python 3.11+, rsvg-convert, xcursorgen, hyprcursor-util.
"""

import argparse
import colorsys
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import artwork
from artwork import GRID, RIM, Fill, Line

THEME_NAME = "Omarchy-Cursor"
SIZES = [24, 32, 40, 48, 64, 96]
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

    def __init__(self, colors, style="accent", overrides=None):
        accent = colors["accent"]
        dark = colors.get("darker_background") or colors.get("dark_background") or colors["background"]
        light = colors.get("bright_foreground") or colors.get("light_foreground") or colors["foreground"]
        if colors.get("mode") == "light":
            dark, light = (colors.get("foreground") or dark), (colors.get("background") or light)
        dark = mix(dark, "#000000", 0.25) if luminance(dark) > 0.02 else dark

        if style == "ink":
            # Theme ink body, glowing accent rim.
            body = dark if colors.get("mode") != "light" else light
            rim = accent if contrast(accent, body) >= 3 else (light if body == dark else dark)
            head = accent
        else:
            # Accent body with whichever theme neutral gives the strongest edge.
            body = accent
            rim = max((dark, light), key=lambda c: contrast(c, body))
            head = mix(accent, "#ffffff", 0.45) if luminance(accent) < 0.5 else mix(accent, "#ffffff", 0.7)

        overrides = overrides or {}
        self.body = overrides.get("body") or body
        self.rim = overrides.get("rim") or rim
        self.head = overrides.get("head") or head
        light_body = luminance(self.body) > 0.18
        self.body_hi = mix(self.body, "#ffffff", 0.3 if light_body else 0.16)
        self.body_lo = mix(self.body, "#000000", 0.12)
        danger = colors.get("red") or "#e05561"
        if contrast(danger, self.rim) < 2.4:
            danger = saturate(mix(danger, "#ffffff" if luminance(self.rim) < 0.3 else "#000000", 0.35), 1.2)
        self.danger = danger
        self.danger_hi = mix(danger, "#ffffff", 0.22)
        self.danger_lo = mix(danger, "#000000", 0.12)
        self.track = mix(self.body, self.rim, 0.8)
        self.hi = mix(self.body, "#ffffff", 0.55)
        self.shadow = 0.5 if luminance(self.rim) < 0.2 else 0.35

    def color(self, key):
        if isinstance(key, tuple):  # ("blend", t): spinner tail rising from track to body to head
            t = key[1]
            if t < 0.7:
                return mix(self.track, self.body, t / 0.7)
            return mix(self.body, self.head, (t - 0.7) / 0.3)
        return getattr(self, key, key)


# ── SVG ───────────────────────────────────────────────────


def gradient(gid, top, bottom):
    return (
        f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="3" x2="0" y2="29">'
        f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient>'
    )


def paint_ref(pal, paint):
    return pal.track if paint == "track" else f"url(#g-{paint})"


def part_svg(part, pal):
    rim, body, marks = [], [], []
    paint = paint_ref(pal, part.paint)
    for s in part.shapes:
        if isinstance(s, Fill):
            rim.append(f'<path d="{s.d}"/>')
            body.append(f'<path d="{s.d}" fill="{paint}"/>')
        elif isinstance(s, Line):
            rim.append(f'<path d="{s.d}" fill="none" stroke-width="{s.width + 2 * RIM:.3f}" '
                       f'stroke-linecap="{s.cap}"/>')
            body.append(f'<path d="{s.d}" fill="none" stroke="{paint}" stroke-width="{s.width:.3f}" '
                        f'stroke-linecap="{s.cap}" stroke-linejoin="round"/>')
    for m in part.marks:
        c = pal.color(m.color)
        if m.width is None:
            marks.append(f'<path d="{m.d}" fill="{c}"/>')
        else:
            marks.append(f'<path d="{m.d}" fill="none" stroke="{c}" stroke-width="{m.width:.3f}" '
                         f'stroke-linecap="{m.cap}" stroke-linejoin="round"/>')
    transform = f' transform="{part.transform}"' if part.transform else ""
    return (
        f"<g{transform}>"
        f'<g fill="{pal.rim}" stroke="{pal.rim}" stroke-width="{2 * RIM:.3f}" stroke-linejoin="round">'
        + "".join(rim) + "</g>" + "".join(body) + "".join(marks) + "</g>"
    )


def frame_svg(parts, pal):
    defs = (
        gradient("g-body", pal.body_hi, pal.body_lo)
        + gradient("g-danger", pal.danger_hi, pal.danger_lo)
        + '<filter id="shadow" x="-25%" y="-25%" width="150%" height="150%">'
        f'<feDropShadow dx="0" dy="0.55" stdDeviation="0.7" flood-color="#000" flood-opacity="{pal.shadow}"/>'
        "</filter>"
    )
    body = "".join(part_svg(p, pal) for p in parts)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{GRID}" height="{GRID}" viewBox="0 0 {GRID} {GRID}">'
        f'<defs>{defs}</defs><g filter="url(#shadow)">{body}</g></svg>\n'
    )


# ── Packaging ─────────────────────────────────────────────


def need(*tools):
    missing = [t for t in tools if not shutil.which(t)]
    if missing:
        sys.exit(f"Missing tools: {', '.join(missing)}")


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)


def build(pal, out, sizes):
    """Write a complete theme into out (which must not exist yet)."""
    need("rsvg-convert", "xcursorgen", "hyprcursor-util")
    cursors = list(artwork.all_cursors())
    work = Path(tempfile.mkdtemp(prefix="omarchy-cursor-"))
    try:
        hypr_src = work / "hypr"
        (hypr_src / "hyprcursors").mkdir(parents=True)
        renders = []
        for cur in cursors:
            sdir = hypr_src / "hyprcursors" / cur.name
            sdir.mkdir()
            pdir = work / "png" / cur.name
            pdir.mkdir(parents=True)
            frames = []
            for i, parts in enumerate(cur.frames):
                svg = sdir / f"{cur.name}-{i:02d}.svg"
                svg.write_text(frame_svg(parts, pal))
                frames.append(svg)
                renders += [(svg, pdir / f"{s}-{i:02d}.png", s) for s in sizes]
            hx, hy = cur.hotspot
            delay = f", {cur.delay}" if cur.delay else ""
            meta = [
                "resize_algorithm = none",
                f"hotspot_x = {hx / GRID:.4f}",
                f"hotspot_y = {hy / GRID:.4f}",
                "nominal_size = 1.0",
            ]
            if cur.aliases:
                meta.append("define_override = " + ";".join(cur.aliases))
            meta += [f"define_size = 0, {f.name}{delay}" for f in frames]
            (sdir / "meta.hl").write_text("\n".join(meta) + "\n")

        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as pool:
            list(pool.map(lambda r: run(["rsvg-convert", "-w", str(r[2]), "-h", str(r[2]),
                                         "-o", str(r[1]), str(r[0])]), renders))

        out.mkdir(parents=True)
        xdir = out / "cursors"
        xdir.mkdir()
        for cur in cursors:
            lines = []
            for i in range(len(cur.frames)):
                for s in sizes:
                    x = round(cur.hotspot[0] * s / GRID)
                    y = round(cur.hotspot[1] * s / GRID)
                    delay = f" {cur.delay}" if cur.delay else ""
                    lines.append(f"{s} {x} {y} {work / 'png' / cur.name / f'{s}-{i:02d}.png'}{delay}")
            cfg = work / f"{cur.name}.cfg"
            cfg.write_text("\n".join(lines) + "\n")
            run(["xcursorgen", str(cfg), str(xdir / cur.name)])
            for alias in cur.aliases:
                if not (xdir / alias).exists():
                    (xdir / alias).symlink_to(cur.name)

        (hypr_src / "manifest.hl").write_text(
            f"name = {THEME_NAME}\n"
            "description = Animated, theme adaptive cursors for Omarchy\n"
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
            f"[Icon Theme]\nName={THEME_NAME}\nComment=Animated, theme adaptive cursors for Omarchy\n"
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
    for name, bg, fg in [("dark", colors["background"], colors["foreground"]),
                         ("light", "#eceff4", "#2e3440")]:
        run(["magick", "montage", *tiles, "-tile", "8x", "-geometry", "96x96+14+10",
             "-background", bg, "-fill", fg, "-pointsize", "11", str(dest / f"sheet-{name}.png")])
    for cur in cursors:
        if len(cur.frames) > 1:
            frames = sorted((work / "png" / cur.name).glob("96-*.png"))
            run(["magick", "-delay", str(max(2, cur.delay // 10)), "-dispose", "background",
                 *map(str, frames), "-background", colors["background"], "-alpha", "remove",
                 "-loop", "0", str(dest / f"{cur.name}.gif")])


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--theme", help="Omarchy theme name or directory (default: active theme)")
    parser.add_argument("--style", choices=["accent", "ink"], default="accent",
                        help="accent: accent body with dark rim; ink: dark body with accent rim")
    parser.add_argument("--body", help="override body color (#hex)")
    parser.add_argument("--rim", help="override rim color (#hex)")
    parser.add_argument("--out", type=Path, default=ROOT / "build" / THEME_NAME, help="build output")
    parser.add_argument("--install", action="store_true", help=f"install to ~/.local/share/icons/{THEME_NAME}")
    parser.add_argument("--apply", action="store_true", help="make it the active cursor (implies --install)")
    parser.add_argument("--size", type=int, default=int(os.environ.get("XCURSOR_SIZE") or 24))
    parser.add_argument("--preview", type=Path, metavar="DIR", help="write preview sheets and GIFs")
    args = parser.parse_args()

    colors, source = load_colors(args.theme)
    pal = Palette(colors, args.style, {"body": args.body, "rim": args.rim})
    print(f"Colors from {source or 'built in fallback'}: body {pal.body}, rim {pal.rim}")

    staged = Path(tempfile.mkdtemp(prefix="omarchy-cursor-out-")) / THEME_NAME
    cursors, work = build(pal, staged, SIZES)
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
