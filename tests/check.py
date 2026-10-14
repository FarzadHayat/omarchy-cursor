#!/usr/bin/env python3
"""Checks run by CI and before releases: python3 tests/check.py"""

import json
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
    """Every click point sits on a drawn pixel, and stays put at every size."""
    for cur in pixelart.all_cursors():
        x, y = cur.hotspot
        for i, grid in enumerate(cur.frames):
            pixel = pixelart.finish(grid)[y][x]
            check(pixel not in (".", "shadow"), f"{cur.name} frame {i}: hotspot ({x}, {y}) is on an empty pixel")
        for size in build.hypr_sizes(24) + build.SIZES:
            scale, ox, oy, hx, hy = pixelart.placement(cur.hotspot, size)
            check(ox + pixelart.CANVAS * scale <= size and oy + pixelart.CANVAS * scale <= size,
                  f"{cur.name} at {size}px: art does not fit")
            for got, h in ((hx + 0.5, x), (hy + 0.5, y)):
                want = (h + 0.5) / pixelart.CANVAS * size
                check(abs(got - want) <= 1, f"{cur.name} at {size}px: hotspot {got} is far from {want:.2f}")


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
    """The website draws cursors in exactly the colors the installed theme uses."""
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
        const { palette } = require(process.argv[1]);
        const [themes, expected] = JSON.parse(require("fs").readFileSync(0, "utf8"));
        const bad = [];
        for (const [key, want] of Object.entries(expected)) {
          const [n, style] = key.split("/");
          const got = palette(themes[n], style);
          for (const k of Object.keys(want)) {
            if (JSON.stringify(got[k]) !== JSON.stringify(want[k])) bad.push(`${key} ${k}`);
          }
        }
        console.log(JSON.stringify(bad));
    """
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
