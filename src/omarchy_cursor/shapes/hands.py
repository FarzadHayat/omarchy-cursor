"""Hand cursor shape definitions.

Provides pointing hand, open hand, and grabbing/closed-fist cursors.
Each function returns a raw SVG string using color placeholders.

Hotspots:
    hand2 (pointing): (114, 18)
    hand1 (open hand): (144, 79)
    grabbing (fist):   (128, 66)
"""


def _svg_wrap(canvas_size: int, content: str) -> str:
    """Wrap SVG content in the standard document boilerplate with glow filter."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{canvas_size}" height="{canvas_size}" '
        f'viewBox="0 0 {canvas_size} {canvas_size}">'
        f"<defs>"
        f'<filter id="glow" x="-15%" y="-15%" width="130%" height="130%">'
        f'<feGaussianBlur in="SourceAlpha" stdDeviation="2.5" result="blur"/>'
        f'<feFlood flood-color="#0000FF" flood-opacity="0.25" result="color"/>'
        f'<feComposite in="color" in2="blur" operator="in" result="shadow"/>'
        f'<feMerge><feMergeNode in="shadow"/><feMergeNode in="SourceGraphic"/></feMerge>'
        f"</filter>"
        f"</defs>"
        f"{content}"
        f"</svg>"
    )


def hand2(canvas_size: int = 256, base: str = "#00FF00", outline: str = "#0000FF") -> str:
    """Pointing hand cursor — index finger extended upward.

    A side-view hand with the index finger pointing straight up. The thumb
    tucks across the palm and the remaining fingers curl in. Designed for
    links and clickable elements.

    Hotspot: (114, 18)
    """
    # Path: index finger pointing up, palm below, thumb folded across.
    # Built from cubic bezier curves for natural organic curvature.
    hand_path = (
        # Start at tip of index finger (top-center)
        "M 114 18 "
        # Right side of index finger going down
        "C 120 18, 130 26, 132 38 "
        "L 134 72 "
        # Knuckle bump — transition to back of hand
        "C 135 80, 140 86, 148 90 "
        # Right side of hand, curled fingers form a rounded block
        "C 158 96, 166 110, 168 126 "
        # Bottom-right of curled fingers
        "C 170 142, 168 162, 162 178 "
        # Bottom of palm
        "C 158 190, 148 198, 138 204 "
        # Wrist — bottom center
        "C 130 210, 118 214, 108 214 "
        # Left side of wrist going up
        "C 96 214, 86 208, 80 198 "
        # Left side of palm
        "C 74 186, 70 170, 70 154 "
        # Thumb — sticks out to the left then curves back
        "C 68 142, 60 134, 54 130 "
        "C 48 126, 44 118, 46 110 "
        "C 48 102, 56 98, 64 98 "
        # Rejoin palm on the left side
        "C 72 98, 78 96, 82 90 "
        # Left side of index finger going up
        "C 86 80, 92 72, 94 60 "
        "L 96 38 "
        # Tip of index finger — close the path
        "C 98 26, 106 18, 114 18 "
        "Z"
    )

    content = (
        f'<g filter="url(#glow)">'
        f'<path d="{hand_path}" '
        f'fill="{base}" stroke="{outline}" stroke-width="17" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
        f"</g>"
    )

    return _svg_wrap(canvas_size, content)


def hand1(canvas_size: int = 256, base: str = "#00FF00", outline: str = "#0000FF") -> str:
    """Open hand / grab cursor — palm facing forward, all fingers spread.

    A front-facing open palm with five fingers fanned out. Slightly larger
    than hand2.  Used as the grab affordance before clicking.

    Hotspot: (144, 79)
    """
    # Five fingers emanate from a rounded palm. Each finger is a pair of
    # lines/curves going up and coming back down, connected at the tip by
    # a small arc.  The thumb sweeps out to the right.

    hand_path = (
        # --- Pinky finger (leftmost) ---
        "M 62 108 "
        "C 60 96, 58 78, 56 66 "
        "C 54 56, 56 48, 62 46 "
        "C 68 44, 74 50, 75 58 "
        "L 78 80 "
        "C 79 86, 80 92, 80 100 "

        # --- Ring finger ---
        "L 82 76 "
        "C 83 60, 82 42, 82 32 "
        "C 82 22, 86 16, 92 14 "
        "C 98 12, 104 18, 104 28 "
        "L 104 56 "
        "C 104 64, 104 72, 104 80 "

        # --- Middle finger ---
        "L 106 62 "
        "C 107 46, 106 28, 106 18 "
        "C 106 8, 112 2, 120 2 "
        "C 128 2, 134 8, 134 18 "
        "L 132 48 "
        "C 132 56, 132 66, 132 76 "

        # --- Index finger ---
        "L 134 60 "
        "C 135 44, 136 30, 136 22 "
        "C 136 12, 142 6, 148 6 "
        "C 154 6, 160 12, 160 22 "
        "L 158 58 "
        "C 158 68, 158 78, 158 86 "

        # --- Thumb (right side, sweeps outward) ---
        "C 162 88, 168 86, 176 82 "
        "C 186 76, 194 74, 200 78 "
        "C 206 82, 208 90, 204 98 "
        "C 200 106, 190 114, 180 120 "
        "C 172 126, 166 130, 162 136 "

        # --- Right side of palm going down to wrist ---
        "C 160 148, 160 164, 158 178 "
        "C 156 192, 150 204, 142 212 "

        # --- Wrist bottom ---
        "C 134 220, 120 224, 108 224 "
        "C 96 224, 84 218, 78 210 "

        # --- Left side of palm going back up ---
        "C 72 202, 66 188, 64 172 "
        "C 62 156, 60 140, 60 124 "
        "L 62 108 "
        "Z"
    )

    content = (
        f'<g filter="url(#glow)">'
        f'<path d="{hand_path}" '
        f'fill="{base}" stroke="{outline}" stroke-width="17" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
        f"</g>"
    )

    return _svg_wrap(canvas_size, content)


def grabbing(canvas_size: int = 256, base: str = "#00FF00", outline: str = "#0000FF") -> str:
    """Closed fist / grabbing cursor — clenched hand gripping something.

    A side-view clenched fist.  The fingers curl tightly over the palm and
    the thumb wraps across the front.  Used while actively dragging.

    Hotspot: (128, 66)
    """
    hand_path = (
        # --- Top of fist, curled finger knuckles (left to right) ---
        # Start at left knuckle
        "M 66 82 "
        # First curled finger bump
        "C 64 72, 66 60, 72 54 "
        "C 78 48, 86 48, 90 54 "
        "C 92 58, 92 62, 92 66 "
        # Second curled finger bump
        "C 92 58, 96 48, 104 44 "
        "C 110 40, 118 42, 120 48 "
        "C 122 52, 122 58, 122 64 "
        # Third curled finger bump
        "C 122 56, 126 46, 134 42 "
        "C 140 38, 148 40, 150 46 "
        "C 152 52, 152 58, 150 66 "
        # Fourth curled finger bump (pinky side)
        "C 152 58, 156 50, 162 48 "
        "C 168 46, 176 48, 178 56 "
        "C 180 62, 178 72, 176 80 "

        # --- Right side of fist going down ---
        "C 178 92, 178 104, 176 116 "
        "C 174 130, 170 144, 166 156 "

        # --- Bottom of palm / wrist ---
        "C 162 168, 156 178, 146 186 "
        "C 138 192, 126 196, 114 196 "
        "C 102 196, 90 192, 82 184 "
        "C 74 176, 68 166, 66 154 "

        # --- Left side going back up ---
        "C 64 142, 62 128, 60 116 "

        # --- Thumb wrapping across the front ---
        "C 58 108, 52 102, 48 96 "
        "C 44 90, 44 82, 48 76 "
        "C 52 70, 58 68, 64 70 "
        "C 66 72, 66 78, 66 82 "
        "Z"
    )

    content = (
        f'<g filter="url(#glow)">'
        f'<path d="{hand_path}" '
        f'fill="{base}" stroke="{outline}" stroke-width="17" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
        f"</g>"
    )

    return _svg_wrap(canvas_size, content)
