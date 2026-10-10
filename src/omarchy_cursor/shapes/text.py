"""Text-related cursor SVG shapes.

Provides I-beam cursors for text editing:
- xterm: standard vertical I-beam
- vertical_text: horizontal I-beam for vertical text input
"""


def _glow_filter(color: str) -> str:
    """Return an SVG filter definition for a subtle glow effect."""
    return (
        '<defs>'
        '<filter id="textGlow" x="-20%" y="-20%" width="140%" height="140%">'
        f'<feFlood flood-color="{color}" flood-opacity="0.35" result="glowColor"/>'
        '<feComposite in="glowColor" in2="SourceGraphic" operator="in" result="glowShape"/>'
        '<feGaussianBlur in="glowShape" stdDeviation="4" result="blurred"/>'
        '<feMerge>'
        '<feMergeNode in="blurred"/>'
        '<feMergeNode in="SourceGraphic"/>'
        '</feMerge>'
        '</filter>'
        '</defs>'
    )


def xterm(canvas_size: int = 256, base: str = "#00FF00", outline: str = "#0000FF") -> str:
    """I-beam text cursor (vertical).

    A vertical line centered at (128, 128) with slightly curved serif
    brackets at top and bottom. The outline color is the primary stroke;
    the base color provides a subtle inner glow.

    Args:
        canvas_size: SVG canvas dimension (width and height).
        base: Fill / glow color placeholder.
        outline: Stroke color placeholder.

    Returns:
        Raw SVG string.
    """
    cx = canvas_size / 2
    # Vertical extents – leave comfortable padding
    top = 48
    bottom = canvas_size - 48  # 208
    serif_w = 28  # half-width of each serif curve
    sw = 17

    glow = _glow_filter(base)

    # Top serif: a gentle arc from left to right curving down into the beam
    # Bottom serif: mirror image curving up into the beam
    # Using quadratic Bézier curves for the slight organic curve
    top_serif = (
        f'M {cx - serif_w},{top} '
        f'Q {cx - serif_w},{top + 14} {cx},{top + 14} '
        f'Q {cx + serif_w},{top + 14} {cx + serif_w},{top}'
    )

    bottom_serif = (
        f'M {cx - serif_w},{bottom} '
        f'Q {cx - serif_w},{bottom - 14} {cx},{bottom - 14} '
        f'Q {cx + serif_w},{bottom - 14} {cx + serif_w},{bottom}'
    )

    # Vertical beam
    beam = f'M {cx},{top + 14} L {cx},{bottom - 14}'

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{canvas_size}" height="{canvas_size}" '
        f'viewBox="0 0 {canvas_size} {canvas_size}">'
        f'{glow}'
        f'<g filter="url(#textGlow)" '
        f'fill="none" stroke="{outline}" stroke-width="{sw}" '
        f'stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="{beam}"/>'
        f'<path d="{top_serif}"/>'
        f'<path d="{bottom_serif}"/>'
        f'</g>'
        f'</svg>'
    )


def vertical_text(canvas_size: int = 256, base: str = "#00FF00", outline: str = "#0000FF") -> str:
    """Horizontal I-beam cursor for vertical text input.

    The standard I-beam rotated 90 degrees so the beam runs horizontally
    with serif brackets on left and right. Centered at (128, 128).

    Args:
        canvas_size: SVG canvas dimension (width and height).
        base: Fill / glow color placeholder.
        outline: Stroke color placeholder.

    Returns:
        Raw SVG string.
    """
    cy = canvas_size / 2
    left = 48
    right = canvas_size - 48  # 208
    serif_h = 28  # half-height of each serif curve
    sw = 17

    glow = _glow_filter(base)

    # Left serif: gentle arc curving right into the beam
    left_serif = (
        f'M {left},{cy - serif_h} '
        f'Q {left + 14},{cy - serif_h} {left + 14},{cy} '
        f'Q {left + 14},{cy + serif_h} {left},{cy + serif_h}'
    )

    # Right serif: mirror of left
    right_serif = (
        f'M {right},{cy - serif_h} '
        f'Q {right - 14},{cy - serif_h} {right - 14},{cy} '
        f'Q {right - 14},{cy + serif_h} {right},{cy + serif_h}'
    )

    # Horizontal beam
    beam = f'M {left + 14},{cy} L {right - 14},{cy}'

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{canvas_size}" height="{canvas_size}" '
        f'viewBox="0 0 {canvas_size} {canvas_size}">'
        f'{glow}'
        f'<g filter="url(#textGlow)" '
        f'fill="none" stroke="{outline}" stroke-width="{sw}" '
        f'stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="{beam}"/>'
        f'<path d="{left_serif}"/>'
        f'<path d="{right_serif}"/>'
        f'</g>'
        f'</svg>'
    )
