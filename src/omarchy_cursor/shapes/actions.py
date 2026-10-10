"""Action cursor SVG shapes.

Each function returns a raw SVG string (256x256 canvas).
Colors use placeholders: base=#00FF00 (fill), outline=#0000FF (stroke).
"""


def _svg_wrap(content: str, canvas_size: int = 256) -> str:
    """Wrap SVG content with the standard header, glow filter, and footer."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{canvas_size}" height="{canvas_size}" '
        f'viewBox="0 0 {canvas_size} {canvas_size}">'
        f"<defs>"
        f'<filter id="glow" x="-20%" y="-20%" width="140%" height="140%">'
        f'<feGaussianBlur in="SourceGraphic" stdDeviation="2" result="blur"/>'
        f'<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>'
        f"</filter>"
        f"</defs>"
        f'{content}'
        f"</svg>"
    )


def crosshair(canvas_size: int = 256, base: str = "#00FF00", outline: str = "#0000FF") -> str:
    """Precision crosshair.

    Thin cross lines intersecting at center (128,128) with a small gap
    at the center point. Circle outline around it.
    """
    cx, cy = canvas_size // 2, canvas_size // 2
    gap = 14
    arm = 52
    circle_r = 60

    content = (
        f'<g filter="url(#glow)" stroke="{outline}" stroke-width="17" '
        f'stroke-linecap="round" stroke-linejoin="round" fill="none">'
        # Outer circle
        f'<circle cx="{cx}" cy="{cy}" r="{circle_r}"/>'
        # Top arm
        f'<line x1="{cx}" y1="{cy - gap}" x2="{cx}" y2="{cy - arm}"/>'
        # Bottom arm
        f'<line x1="{cx}" y1="{cy + gap}" x2="{cx}" y2="{cy + arm}"/>'
        # Left arm
        f'<line x1="{cx - gap}" y1="{cy}" x2="{cx - arm}" y2="{cy}"/>'
        # Right arm
        f'<line x1="{cx + gap}" y1="{cy}" x2="{cx + arm}" y2="{cy}"/>'
        f"</g>"
        # Center dot
        f'<circle cx="{cx}" cy="{cy}" r="4" fill="{base}" stroke="none"/>'
    )
    return _svg_wrap(content, canvas_size)


def pencil(canvas_size: int = 256, base: str = "#00FF00", outline: str = "#0000FF") -> str:
    """Pencil/edit cursor.

    Angled pencil pointing down-left, tip at (46, 211).
    Simple geometric pencil shape.
    """
    # Pencil body: a rotated rectangle with a pointed tip.
    # The pencil runs from lower-left (tip) to upper-right (eraser end).
    # Tip at (46, 211). Body angle ~-45 degrees.
    content = (
        f'<g filter="url(#glow)" stroke="{outline}" stroke-width="17" '
        f'stroke-linecap="round" stroke-linejoin="round" fill="{base}">'
        # Pencil body as a polygon:
        # tip -> left edge of body -> eraser top-left -> eraser top-right -> right edge of body
        f'<polygon points="46,211 72,160 88,144 196,36 220,60 108,168 92,184"/>'
        f"</g>"
        # Pencil line detail (the writing edge / tip divider)
        f'<line x1="80" y1="176" x2="92" y2="152" '
        f'stroke="{outline}" stroke-width="8" stroke-linecap="round"/>'
    )
    return _svg_wrap(content, canvas_size)


def plus(canvas_size: int = 256, base: str = "#00FF00", outline: str = "#0000FF") -> str:
    """Plus/cell cursor.

    A plus sign centered at (128,128).
    """
    cx, cy = canvas_size // 2, canvas_size // 2
    arm = 56

    content = (
        f'<g filter="url(#glow)" stroke="{outline}" stroke-width="17" '
        f'stroke-linecap="round" stroke-linejoin="round" fill="none">'
        # Vertical bar
        f'<line x1="{cx}" y1="{cy - arm}" x2="{cx}" y2="{cy + arm}"/>'
        # Horizontal bar
        f'<line x1="{cx - arm}" y1="{cy}" x2="{cx + arm}" y2="{cy}"/>'
        f"</g>"
    )
    return _svg_wrap(content, canvas_size)


def _magnifier(cx: int, cy: int, r: int, handle_len: int,
               inner_svg: str, outline: str, base: str) -> str:
    """Shared magnifying glass shape used by zoom_in and zoom_out."""
    # Handle extends from circle edge at 45 degrees toward bottom-right
    import math
    angle = math.radians(45)
    hx1 = cx + int(r * math.cos(angle))
    hy1 = cy + int(r * math.sin(angle))
    hx2 = cx + int((r + handle_len) * math.cos(angle))
    hy2 = cy + int((r + handle_len) * math.sin(angle))

    return (
        f'<g filter="url(#glow)" stroke="{outline}" stroke-width="17" '
        f'stroke-linecap="round" stroke-linejoin="round" fill="none">'
        # Glass circle
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{base}"/>'
        # Handle
        f'<line x1="{hx1}" y1="{hy1}" x2="{hx2}" y2="{hy2}"/>'
        # Inner symbol (+ or -)
        f'{inner_svg}'
        f"</g>"
    )


def zoom_in(canvas_size: int = 256, base: str = "#00FF00", outline: str = "#0000FF") -> str:
    """Magnifying glass with + sign inside.

    Circle centered at (116,116) with handle extending down-right.
    """
    cx, cy = 116, 116
    r = 58
    handle_len = 70
    sign_arm = 22

    inner = (
        # Vertical stroke of +
        f'<line x1="{cx}" y1="{cy - sign_arm}" x2="{cx}" y2="{cy + sign_arm}"/>'
        # Horizontal stroke of +
        f'<line x1="{cx - sign_arm}" y1="{cy}" x2="{cx + sign_arm}" y2="{cy}"/>'
    )
    content = _magnifier(cx, cy, r, handle_len, inner, outline, base)
    return _svg_wrap(content, canvas_size)


def zoom_out(canvas_size: int = 256, base: str = "#00FF00", outline: str = "#0000FF") -> str:
    """Magnifying glass with - sign inside.

    Same shape as zoom_in but minus instead of plus.
    """
    cx, cy = 116, 116
    r = 58
    handle_len = 70
    sign_arm = 22

    inner = (
        # Horizontal stroke of -
        f'<line x1="{cx - sign_arm}" y1="{cy}" x2="{cx + sign_arm}" y2="{cy}"/>'
    )
    content = _magnifier(cx, cy, r, handle_len, inner, outline, base)
    return _svg_wrap(content, canvas_size)


def tcross(canvas_size: int = 256, base: str = "#00FF00", outline: str = "#0000FF") -> str:
    """Color picker crosshair (T-shaped).

    Similar to crosshair but the top arm is replaced by a horizontal bar,
    creating a T-cross shape. Used as a color picker cursor.
    """
    cx, cy = canvas_size // 2, canvas_size // 2
    arm = 52
    bar_half = 40

    content = (
        f'<g filter="url(#glow)" stroke="{outline}" stroke-width="17" '
        f'stroke-linecap="round" stroke-linejoin="round" fill="none">'
        # Vertical line (full downward from center, short upward)
        f'<line x1="{cx}" y1="{cy - arm}" x2="{cx}" y2="{cy + arm}"/>'
        # Horizontal bar at top
        f'<line x1="{cx - bar_half}" y1="{cy - arm}" x2="{cx + bar_half}" y2="{cy - arm}"/>'
        # Left arm
        f'<line x1="{cx - arm}" y1="{cy}" x2="{cx - 14}" y2="{cy}"/>'
        # Right arm
        f'<line x1="{cx + 14}" y1="{cy}" x2="{cx + arm}" y2="{cy}"/>'
        f"</g>"
        # Center dot
        f'<circle cx="{cx}" cy="{cy}" r="4" fill="{base}" stroke="none"/>'
    )
    return _svg_wrap(content, canvas_size)


def dotbox(canvas_size: int = 256, base: str = "#00FF00", outline: str = "#0000FF") -> str:
    """Dot in a box.

    Square outline with a dot at center.
    """
    cx, cy = canvas_size // 2, canvas_size // 2
    half = 60  # half side-length of the box
    dot_r = 12

    content = (
        f'<g filter="url(#glow)" stroke="{outline}" stroke-width="17" '
        f'stroke-linecap="round" stroke-linejoin="round" fill="none">'
        # Outer square
        f'<rect x="{cx - half}" y="{cy - half}" '
        f'width="{half * 2}" height="{half * 2}" rx="8"/>'
        f"</g>"
        # Center dot
        f'<circle cx="{cx}" cy="{cy}" r="{dot_r}" fill="{base}" '
        f'stroke="{outline}" stroke-width="6"/>'
    )
    return _svg_wrap(content, canvas_size)
