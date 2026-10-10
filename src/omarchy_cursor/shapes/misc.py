"""Misc cursors."""

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

def circle(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    return get_base_svg("M 128,40 A 88,88 0 1,0 128,216 A 88,88 0 1,0 128,40 Z M 128,70 A 58,58 0 1,1 128,186 A 58,58 0 1,1 128,70 Z", base, outline)

def crossed_circle(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    return get_base_svg("M 128,40 A 88,88 0 1,0 128,216 A 88,88 0 1,0 128,40 Z M 128,70 A 58,58 0 1,1 128,186 A 58,58 0 1,1 128,70 Z M 76,198 L 198,76 L 180,58 L 58,180 Z", base, outline)

def context_menu(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    arrow = "M 55,17 L 55,200 L 100,160 L 145,220 L 175,200 L 130,140 L 195,140 Z"
    # Three lines representing a menu
    menu = "M 150,150 L 220,150 L 220,170 L 150,170 Z M 150,180 L 220,180 L 220,200 L 150,200 Z M 150,210 L 220,210 L 220,230 L 150,230 Z"
    return get_base_svg(arrow + " " + menu, base, outline)

def question_arrow(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    arrow = "M 42,86 L 42,200 L 70,170 L 100,210 L 120,190 L 90,150 L 130,150 Z"
    # Question mark shape
    qmark = "M 140,50 C 140,20 200,20 200,50 C 200,80 170,90 170,120 L 150,120 C 150,80 180,70 180,50 C 180,30 160,30 160,50 Z M 150,140 L 170,140 L 170,160 L 150,160 Z"
    return get_base_svg(arrow + " " + qmark, base, outline)

def X_cursor(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    return get_base_svg("M 80,60 L 128,108 L 176,60 L 196,80 L 148,128 L 196,176 L 176,196 L 128,148 L 80,196 L 60,176 L 108,128 L 60,80 Z", base, outline)

def cross(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    return get_base_svg("M 118,50 L 138,50 L 138,118 L 206,118 L 206,138 L 138,138 L 138,206 L 118,206 L 118,138 L 50,138 L 50,118 L 118,118 Z", base, outline)

def pointer_move(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    arrow = "M 55,17 L 55,140 L 100,120 Z"
    move_cross = "M 180,140 L 210,170 L 190,170 L 190,228 L 248,228 L 248,208 L 278,238 L 248,268 L 248,248 L 190,248 L 190,306 L 210,306 L 180,336 L 150,306 L 170,306 L 170,248 L 112,248 L 112,268 L 82,238 L 112,208 L 112,228 L 170,228 L 170,170 L 150,170 Z"
    return get_base_svg(arrow + " " + move_cross, base, outline)

def person(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    return get_base_svg("M 128,40 A 30,30 0 1,1 128,100 A 30,30 0 1,1 128,40 Z M 70,210 C 70,140 186,140 186,210 Z", base, outline)

def pin(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    return get_base_svg("M 108,40 L 148,40 L 148,60 L 108,60 Z M 118,60 L 138,60 L 138,120 L 158,160 L 98,160 L 118,120 Z M 123,160 L 133,160 L 133,220 L 123,220 Z", base, outline)

def wayland_cursor(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    return get_base_svg("M 50,50 L 206,50 L 206,206 L 50,206 Z M 90,90 L 166,90 L 166,166 L 90,166 Z", base, outline)
