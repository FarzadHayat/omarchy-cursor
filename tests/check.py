#!/usr/bin/env python3
"""Checks run by CI and before releases: python3 tests/check.py"""

import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import build  # noqa: E402
import pixelart  # noqa: E402

SAMPLE_THEMES = [
    build.FALLBACK_COLORS,
    {"mode": "light", "accent": "#b0473a", "background": "#f1ebe0", "foreground": "#1e1f26", "red": "#b0473a"},
    {"mode": "dark", "accent": "#8d8d8d", "background": "#000000", "foreground": "#ffffff", "red": "#a4a4a4"},
    {"mode": "dark", "accent": "#82FB9C", "background": "#0B0C16", "foreground": "#ddf7ff", "red": "#50f872",
     "darker_background": "#05060c", "bright_foreground": "#ffffff"},
]
failures = []


def check(ok, message):
    if not ok:
        failures.append(message)


def hotspots():
    """Every click point touches the drawing, and Hyprland clicks near it at every size."""
    for cur in pixelart.all_cursors():
        x, y = cur.hotspot
        for i, grid in enumerate(cur.frames):
            finished = pixelart.finish(grid)
            around = [finished[py][px] for py in {int(y) - 1, int(y)} for px in {int(x) - 1, int(x)}
                      if 0 <= px < len(finished) and 0 <= py < len(finished)]
            check(any(p not in (".", "shadow") for p in around),
                  f"{cur.name} frame {i}: hotspot ({x}, {y}) is not on the drawing")
        for size in build.hypr_sizes(24) + build.SIZES:
            scale, ox, oy, hx, hy = pixelart.placement(cur.hotspot, size)
            check(ox + pixelart.CANVAS * scale <= size and oy + pixelart.CANVAS * scale <= size,
                  f"{cur.name} at {size}px: art does not fit")
            for click, offset, point in ((hx, ox, x), (hy, oy, y)):
                target = offset + pixelart.hyprland_round(point * scale)  # the screen pixel meant to click
                check(click == target, f"{cur.name} at {size}px: clicks pixel {click}, hotspot pixel is {target}")


def full_build():
    """A complete theme builds, with a file for every cursor name."""
    out = Path(tempfile.mkdtemp()) / "theme"
    try:
        cursors, work = build.build(build.Palette(build.FALLBACK_COLORS), out)
        shutil.rmtree(work, ignore_errors=True)
        for cur in cursors:
            for name in [cur.name, *cur.aliases]:
                check((out / "cursors" / name).exists(), f"missing Xcursor {name}")
            check((out / "hyprcursors" / f"{cur.name}.hlc").exists(), f"missing Hyprcursor {cur.name}")
    finally:
        shutil.rmtree(out.parent, ignore_errors=True)


def site_colors():
    """The website draws cursors in the same colors and positions as the installed theme."""
    if not shutil.which("node"):
        print("node not found, skipping the website color check")
        return
    expected = {}
    for n, colors in enumerate(SAMPLE_THEMES):
        for style in ("accent", "light", "dark"):
            pal = build.png_colors(build.Palette({**build.FALLBACK_COLORS, **colors}, None, style))
            pal["%"] = pal.pop("shadow")
            expected[f"{n}/{style}"] = {k: list(v) for k, v in pal.items()}
    script = """
        const { palette, placement } = require(process.argv[1]);
        const [themes, expected] = JSON.parse(require("fs").readFileSync(0, "utf8"));
        const bad = [];
        for (const [key, want] of Object.entries(expected)) {
          const [n, style] = key.split("/");
          const got = palette(themes[n], style);
          for (const k of Object.keys(want)) {
            if (JSON.stringify(got[k]) !== JSON.stringify(want[k])) bad.push(`${key} ${k}`);
          }
        }
        for (const [hotspot, size, want] of PLACEMENTS) {
          const p = placement(hotspot, size);
          if (JSON.stringify([p.scale, p.ox, p.oy]) !== JSON.stringify(want)) bad.push(`placement ${hotspot} at ${size}`);
        }
        console.log(JSON.stringify(bad));
    """
    placements = [[list(c.hotspot), size, list(pixelart.placement(c.hotspot, size)[:3])]
                  for c in pixelart.all_cursors() for size in (24, 30, 36, 42, 48, 60)]
    script = f"const PLACEMENTS = {json.dumps(placements)};" + script
    result = subprocess.run(["node", "-e", script, str(ROOT / "cursors.js")],
                            input=json.dumps([SAMPLE_THEMES, expected]), capture_output=True, text=True)
    check(result.returncode == 0, f"website color check crashed: {result.stderr.strip()}")
    if result.returncode == 0:
        for item in json.loads(result.stdout):
            failures.append(f"website color differs: {item}")


for test in (hotspots, full_build, site_colors):
    test()
    print(f"{test.__name__}: {'ok' if not failures else 'FAILED'}")
    if failures:
        break

for message in failures:
    print("  " + message)
sys.exit(1 if failures else 0)
