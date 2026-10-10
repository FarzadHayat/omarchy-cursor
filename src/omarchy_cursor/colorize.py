"""Theme color extraction and cursor color computation for Omarchy."""

import colorsys
import re
from pathlib import Path
from typing import Optional


import tomllib
def _parse_simple_toml(text: str) -> dict[str, str]:
    """Parse TOML and return a flat dictionary of strings."""
    try:
        data = tomllib.loads(text)
        result = {}
        for k, v in data.items():
            if isinstance(v, dict):
                for sub_k, sub_v in v.items():
                    if isinstance(sub_v, str):
                        result[sub_k] = sub_v
            elif isinstance(v, str):
                result[k] = v
        return result
    except Exception:
        return {}


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB tuple to hex color."""
    return f"#{r:02x}{g:02x}{b:02x}"


def relative_luminance(hex_color: str) -> float:
    """Compute relative luminance of a color."""
    r, g, b = hex_to_rgb(hex_color)

    def linearize(c: int) -> float:
        s = c / 255.0
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4

    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)


def ensure_contrast(fg: str, bg: str, min_ratio: float = 3.0) -> str:
    """Adjust fg color to ensure minimum contrast ratio against bg."""
    lum_fg = relative_luminance(fg)
    lum_bg = relative_luminance(bg)
    lighter = max(lum_fg, lum_bg)
    darker = min(lum_fg, lum_bg)
    ratio = (lighter + 0.05) / (darker + 0.05)
    if ratio >= min_ratio:
        return fg
    # Lighten or darken fg to meet contrast
    r, g, b = hex_to_rgb(fg)
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    if lum_bg > 0.5:
        # Dark fg on light bg - darken
        l = max(0.0, l - 0.3)
    else:
        # Light fg on dark bg - lighten
        l = min(1.0, l + 0.3)
    r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
    return rgb_to_hex(int(r2 * 255), int(g2 * 255), int(b2 * 255))


def darken_color(hex_color: str, factor: float = 0.3) -> str:
    """Darken a color by a factor."""
    r, g, b = hex_to_rgb(hex_color)
    return rgb_to_hex(
        int(r * (1 - factor)),
        int(g * (1 - factor)),
        int(b * (1 - factor)),
    )


def lighten_color(hex_color: str, factor: float = 0.3) -> str:
    """Lighten a color by a factor."""
    r, g, b = hex_to_rgb(hex_color)
    return rgb_to_hex(
        min(255, int(r + (255 - r) * factor)),
        min(255, int(g + (255 - g) * factor)),
        min(255, int(b + (255 - b) * factor)),
    )


def find_theme_path(theme_name: str) -> Optional[Path]:
    """Locate an omarchy theme directory."""
    candidates = [
        Path.home() / ".config" / "omarchy" / "themes" / theme_name,
        Path("/usr/share/omarchy/themes") / theme_name,
    ]
    for p in candidates:
        if (p / "colors.toml").exists():
            return p
    return None


def extract_omarchy_colors(theme_name: str) -> dict[str, str]:
    """Read colors from an omarchy theme's colors.toml."""
    theme_path = find_theme_path(theme_name)
    if theme_path is None:
        raise FileNotFoundError(f"Theme not found: {theme_name}")
    colors_file = theme_path / "colors.toml"
    text = colors_file.read_text()
    return _parse_simple_toml(text)


def get_current_theme() -> Optional[str]:
    """Detect the currently active omarchy theme."""
    state_dir = Path.home() / ".local" / "state" / "omarchy"
    current_link = state_dir / "current"
    if current_link.is_symlink():
        return current_link.resolve().name
    # Fallback: check hyprland env
    return None


def compute_cursor_colors(
    colors: dict[str, str],
    base_override: Optional[str] = None,
    outline_override: Optional[str] = None,
    watch_override: Optional[str] = None,
) -> tuple[str, str, str]:
    """Compute base, outline, and watch colors from theme palette.

    Returns (base_color, outline_color, watch_color).
    """
    # Base: accent color - the vibrant cursor fill
    base = base_override or colors.get("accent", "#89b4fa")

    # Outline: dark background for contrast
    bg = colors.get("dark_background", colors.get("background", "#1e1e2e"))
    outline = outline_override or ensure_contrast(bg, base)

    # Watch: variant of accent for loading animations
    watch = watch_override or darken_color(
        colors.get("accent", "#89b4fa"), 0.2
    )

    return base.upper(), outline.upper(), watch.upper()


    result = result.replace("#0000ff", outline)
    result = result.replace("#ff0000", watch)
    return result
