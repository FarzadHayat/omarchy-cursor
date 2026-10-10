"""Arrow/pointer cursor SVG shapes.

Each function returns a complete SVG XML string for a pointer cursor.

Canvas: 256x256, viewBox="0 0 256 256"
Colors: base="#00FF00" (fill), outline="#0000FF" (stroke)
Stroke width: 17
"""


def _svg_wrap(canvas_size, inner, base):
    """Wrap SVG content with the standard header, glow filter, and footer."""
    return (
        f'<svg width="{canvas_size}" height="{canvas_size}" '
        f'viewBox="0 0 {canvas_size} {canvas_size}" fill="none" '
        f'xmlns="http://www.w3.org/2000/svg">\n'
        f"<defs>\n"
        f'  <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">\n'
        f'    <feGaussianBlur in="SourceGraphic" stdDeviation="2.5" result="blur"/>\n'
        f"    <feMerge>\n"
        f'      <feMergeNode in="blur"/>\n'
        f'      <feMergeNode in="SourceGraphic"/>\n'
        f"    </feMerge>\n"
        f"  </filter>\n"
        f"</defs>\n"
        f"{inner}\n"
        f"</svg>"
    )


def left_ptr(canvas_size=256, base="#00FF00", outline="#0000FF"):
    """Default arrow pointer pointing up-left.

    A sleek triangular arrow with slightly concave sides for a modern,
    elegant look. The tip sits at approximately (55, 17).

    Args:
        canvas_size: SVG canvas dimension (width and height).
        base: Fill color (placeholder #00FF00).
        outline: Stroke color (placeholder #0000FF).

    Returns:
        Complete SVG XML string.
    """
    # Arrow pointing up-left with concave sides for a sleek silhouette.
    # Tip at (55, 17), body fans down-right, tail notch creates the
    # classic pointer shape. Cubic beziers on the two main edges give
    # the concave curvature.
    path = (
        "M 55 17 "
        # Left edge – slight concave bow toward lower-left
        "C 53 65, 40 130, 42 175 "
        # Tail notch bottom-left
        "L 80 140 "
        # Bottom bar – the horizontal arm of the pointer
        "C 95 138, 110 155, 120 175 "
        # Right concave edge sweeping back up to the arm elbow
        "C 130 200, 140 220, 145 240 "
        # Bottom-right terminus
        "L 145 240 "
        # Inner right edge curving back up to the elbow
        "C 135 205, 120 175, 110 150 "
        # Elbow back toward tail
        "L 95 120 "
        # Right edge – concave bow back to tip
        "C 85 80, 70 45, 55 17 "
        "Z"
    )

    # Simplified, more robust pointer polygon using clean lines with
    # rounded stroke-linejoin for smooth corners.
    # Points define a classic left-ptr arrow shape:
    #   tip -> left-bottom -> tail-notch -> arm-end -> back to tip
    path = (
        "M 55 17 "
        "L 42 185 "       # left edge down
        "L 85 140 "       # tail notch inward
        "L 145 238 "      # arm extending down-right
        "L 170 220 "      # arm right edge
        "L 112 125 "      # arm back toward body
        "L 165 110 "      # right wing tip
        "Z"               # close back to arrow tip
    )

    inner = (
        f'<path d="{path}" '
        f'fill="{base}" stroke="{outline}" stroke-width="17" '
        f'stroke-linejoin="round" stroke-linecap="round" '
        f'filter="url(#glow)"/>'
    )
    return _svg_wrap(canvas_size, inner, base)


def right_ptr(canvas_size=256, base="#00FF00", outline="#0000FF"):
    """Arrow pointer pointing up-right – mirror of left_ptr.

    Tip sits at approximately (204, 17).

    Args:
        canvas_size: SVG canvas dimension (width and height).
        base: Fill color (placeholder #00FF00).
        outline: Stroke color (placeholder #0000FF).

    Returns:
        Complete SVG XML string.
    """
    # Mirror of left_ptr about x = canvas_size / 2 (128).
    # Each x coordinate is transformed: x' = 256 - x
    #   55->201≈204,  42->214,  85->171,  145->111,
    #   170->86,  112->144,  165->91
    # y coordinates stay the same.
    path = (
        "M 201 17 "
        "L 214 185 "      # right edge down
        "L 171 140 "      # tail notch inward
        "L 111 238 "      # arm extending down-left
        "L 86 220 "       # arm left edge
        "L 144 125 "      # arm back toward body
        "L 91 110 "       # left wing tip
        "Z"
    )

    inner = (
        f'<path d="{path}" '
        f'fill="{base}" stroke="{outline}" stroke-width="17" '
        f'stroke-linejoin="round" stroke-linecap="round" '
        f'filter="url(#glow)"/>'
    )
    return _svg_wrap(canvas_size, inner, base)


def center_ptr(canvas_size=256, base="#00FF00", outline="#0000FF"):
    """Upward-pointing arrow centered horizontally.

    A narrower, symmetrical arrow with tip at (127, 17).

    Args:
        canvas_size: SVG canvas dimension (width and height).
        base: Fill color (placeholder #00FF00).
        outline: Stroke color (placeholder #0000FF).

    Returns:
        Complete SVG XML string.
    """
    # Symmetrical upward arrow. Narrower profile than left_ptr.
    # Tip at center-top, two symmetric flanges at bottom, notch in
    # the middle of the base.
    path = (
        "M 127 17 "
        "L 60 175 "       # left outer edge
        "L 100 145 "      # left notch
        "L 100 238 "      # left side of stem
        "L 154 238 "      # right side of stem
        "L 154 145 "      # right notch
        "L 194 175 "      # right outer edge
        "Z"               # back to tip
    )

    inner = (
        f'<path d="{path}" '
        f'fill="{base}" stroke="{outline}" stroke-width="17" '
        f'stroke-linejoin="round" stroke-linecap="round" '
        f'filter="url(#glow)"/>'
    )
    return _svg_wrap(canvas_size, inner, base)
