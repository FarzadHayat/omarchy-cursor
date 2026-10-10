"""Hand cursor shape definitions."""

def _svg_wrap(canvas_size: int, content: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{canvas_size}" height="{canvas_size}" '
        f'viewBox="0 0 {canvas_size} {canvas_size}">'
        f"<defs>"
        f'<filter id="glow" x="-15%" y="-15%" width="130%" height="130%">'
        f'<feGaussianBlur in="SourceGraphic" stdDeviation="2.5" result="blur"/>'
        f'<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>'
        f"</filter>"
        f"</defs>"
        f"{content}"
        f"</svg>"
    )

def hand2(canvas_size: int = 256, base: str = "#00FF00", outline: str = "#0000FF") -> str:
    """Pointing hand cursor."""
    # A geometric pointing hand that looks clean and recognizable
    outline_path = (
        "M 100 110 "
        "L 100 35 C 100 20 128 20 128 35 " # Index finger
        "L 128 95 "
        "L 142 95 C 150 95 156 100 156 108 " # Middle finger
        "L 156 115 "
        "L 170 115 C 178 115 184 120 184 128 " # Ring finger
        "L 184 135 "
        "L 198 135 C 206 135 212 140 212 148 " # Pinky
        "L 212 190 C 212 215 190 235 165 235 " # Right side of palm
        "L 90 235 C 65 235 45 215 45 190 " # Left side of palm
        "L 45 155 C 45 140 60 130 75 140 " # Thumb
        "L 100 155 "
        "Z"
    )
    
    creases = (
        f'<path d="M 128 95 L 128 150" stroke="{outline}" stroke-width="17" stroke-linecap="round"/>'
        f'<path d="M 156 108 L 156 160" stroke="{outline}" stroke-width="17" stroke-linecap="round"/>'
        f'<path d="M 184 128 L 184 170" stroke="{outline}" stroke-width="17" stroke-linecap="round"/>'
    )

    content = (
        f'<g filter="url(#glow)">'
        f'<path d="{outline_path}" fill="{base}" stroke="{outline}" stroke-width="17" stroke-linejoin="round" stroke-linecap="round"/>'
        f'{creases}'
        f"</g>"
    )
    return _svg_wrap(canvas_size, content)


def hand1(canvas_size: int = 256, base: str = "#00FF00", outline: str = "#0000FF") -> str:
    """Open hand cursor."""
    outline_path = (
        "M 72 135 "
        "L 72 65 C 72 50 100 50 100 65 " # Index finger
        "L 100 120 "
        "L 128 50 C 128 35 156 35 156 50 " # Middle finger
        "L 156 120 "
        "L 184 65 C 184 50 212 50 212 65 " # Ring finger
        "L 212 125 "
        "L 240 90 C 255 105 250 125 240 135 " # Pinky
        "L 212 165 C 212 210 180 240 135 240 " # Right side of palm
        "L 90 240 C 45 240 20 210 20 165 " # Left side of palm
        "L 20 145 C 20 130 45 120 60 135 " # Thumb
        "L 72 145 "
        "Z"
    )
    
    creases = (
        f'<path d="M 100 120 L 100 180" stroke="{outline}" stroke-width="17" stroke-linecap="round"/>'
        f'<path d="M 156 120 L 156 190" stroke="{outline}" stroke-width="17" stroke-linecap="round"/>'
        f'<path d="M 212 125 L 212 170" stroke="{outline}" stroke-width="17" stroke-linecap="round"/>'
    )

    content = (
        f'<g filter="url(#glow)">'
        f'<path d="{outline_path}" fill="{base}" stroke="{outline}" stroke-width="17" stroke-linejoin="round" stroke-linecap="round"/>'
        f'{creases}'
        f"</g>"
    )
    return _svg_wrap(canvas_size, content)


def grabbing(canvas_size: int = 256, base: str = "#00FF00", outline: str = "#0000FF") -> str:
    """Grabbing cursor (fist)."""
    outline_path = (
        "M 60 100 "
        "C 60 80 80 70 100 85 "
        "C 105 70 125 70 140 85 "
        "C 150 75 170 80 180 95 "
        "C 190 90 210 100 210 120 "
        "L 210 160 C 210 200 180 230 140 230 "
        "L 100 230 C 60 230 40 200 40 160 "
        "L 40 130 C 40 110 60 100 70 120 "
        "Z"
    )
    
    creases = (
        f'<path d="M 100 85 L 100 140" stroke="{outline}" stroke-width="17" stroke-linecap="round"/>'
        f'<path d="M 140 85 L 140 140" stroke="{outline}" stroke-width="17" stroke-linecap="round"/>'
        f'<path d="M 180 95 L 180 140" stroke="{outline}" stroke-width="17" stroke-linecap="round"/>'
    )

    content = (
        f'<g filter="url(#glow)">'
        f'<path d="{outline_path}" fill="{base}" stroke="{outline}" stroke-width="17" stroke-linejoin="round" stroke-linecap="round"/>'
        f'{creases}'
        f"</g>"
    )
    return _svg_wrap(canvas_size, content)
