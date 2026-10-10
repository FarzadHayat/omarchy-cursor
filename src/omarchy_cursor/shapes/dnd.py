"""Drag and drop cursors."""

def get_base_svg(d_path: str, base: str, outline: str) -> str:
    return f"""<svg width="256" height="256" viewBox="0 0 256 256" fill="none" xmlns="http://www.w3.org/2000/svg">
<defs>
  <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="3" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
</defs>
<path d="{d_path}" fill="{base}" stroke="{outline}" stroke-width="17" stroke-linejoin="round" stroke-linecap="round" filter="url(#glow)"/>
</svg>"""

def copy(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    arrow = "M 55,17 L 55,200 L 100,160 L 145,220 L 175,200 L 130,140 L 195,140 Z"
    # Small plus sign at bottom right
    plus = "M 150,150 L 180,150 L 180,180 L 210,180 L 210,210 L 180,210 L 180,240 L 150,240 L 150,210 L 120,210 L 120,180 L 150,180 Z"
    return get_base_svg(arrow + " " + plus, base, outline)

def link(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    arrow = "M 55,17 L 55,200 L 100,160 L 145,220 L 175,200 L 130,140 L 195,140 Z"
    # Small curved arrow at bottom right (shortcut/link symbol)
    curve = "M 130,220 C 130,180 160,150 200,150 L 200,130 L 240,165 L 200,200 L 200,180 C 170,180 150,200 150,220 Z"
    return get_base_svg(arrow + " " + curve, base, outline)

def dnd_ask(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    # A box with a question mark
    box = "M 70,70 L 190,70 L 190,190 L 70,190 Z M 110,110 L 150,110 L 150,130 L 130,130 L 130,150 L 110,150 Z M 110,160 L 130,160 L 130,180 L 110,180 Z"
    return get_base_svg(box, base, outline)

def dnd_copy(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    # A box with a plus
    box = "M 70,70 L 190,70 L 190,190 L 70,190 Z M 120,100 L 140,100 L 140,120 L 160,120 L 160,140 L 140,140 L 140,160 L 120,160 L 120,140 L 100,140 L 100,120 L 120,120 Z"
    return get_base_svg(box, base, outline)

def dnd_link(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    # A box with a link arrow
    box = "M 70,70 L 190,70 L 190,190 L 70,190 Z"
    arrow = "M 90,170 C 90,130 120,100 160,100 L 160,80 L 200,115 L 160,150 L 160,130 C 130,130 110,150 110,170 Z"
    return get_base_svg(box + " " + arrow, base, outline)

def dnd_no_drop(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    # Crossed circle
    circle = "M 128,40 A 88,88 0 1,0 128,216 A 88,88 0 1,0 128,40 Z M 128,70 A 58,58 0 1,1 128,186 A 58,58 0 1,1 128,70 Z"
    cross = "M 76,198 L 198,76 L 180,58 L 58,180 Z"
    return get_base_svg(circle + " " + cross, base, outline)
