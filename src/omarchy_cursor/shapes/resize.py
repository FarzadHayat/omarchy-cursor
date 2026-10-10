"""Resize cursor shapes."""

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

def top_side(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    return get_base_svg("M 128,30 L 98,70 L 118,70 L 118,110 L 138,110 L 138,70 L 158,70 Z", base, outline)

def bottom_side(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    return get_base_svg("M 128,226 L 98,186 L 118,186 L 118,146 L 138,146 L 138,186 L 158,186 Z", base, outline)

def left_side(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    return get_base_svg("M 30,128 L 70,98 L 70,118 L 110,118 L 110,138 L 70,138 L 70,158 Z", base, outline)

def right_side(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    return get_base_svg("M 226,128 L 186,98 L 186,118 L 146,118 L 146,138 L 186,138 L 186,158 Z", base, outline)

def top_left_corner(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    return get_base_svg("M 34,34 L 84,34 L 84,54 L 68,54 L 98,84 L 84,98 L 54,68 L 54,84 L 34,84 Z", base, outline)

def top_right_corner(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    return get_base_svg("M 222,34 L 172,34 L 172,54 L 188,54 L 158,84 L 172,98 L 202,68 L 202,84 L 222,84 Z", base, outline)

def bottom_left_corner(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    return get_base_svg("M 34,222 L 84,222 L 84,202 L 68,202 L 98,172 L 84,158 L 54,188 L 54,172 L 34,172 Z", base, outline)

def bottom_right_corner(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    return get_base_svg("M 222,222 L 172,222 L 172,202 L 188,202 L 158,172 L 172,158 L 202,188 L 202,172 L 222,172 Z", base, outline)

def sb_h_double_arrow(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    return get_base_svg("M 30,128 L 70,98 L 70,118 L 186,118 L 186,98 L 226,128 L 186,158 L 186,138 L 70,138 L 70,158 Z", base, outline)

def sb_v_double_arrow(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    return get_base_svg("M 128,30 L 158,70 L 138,70 L 138,186 L 158,186 L 128,226 L 98,186 L 118,186 L 118,70 L 98,70 Z", base, outline)

def bd_double_arrow(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    return get_base_svg("M 34,34 L 84,34 L 84,54 L 68,54 L 188,174 L 172,174 L 172,154 L 222,154 L 222,204 L 202,204 L 202,188 L 82,68 L 82,84 L 54,84 L 54,84 Z M 34,34 L 54,34 L 54,54 Z M 222,204 L 202,204 L 202,224 Z", base, outline)

def fd_double_arrow(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    return get_base_svg("M 222,34 L 172,34 L 172,54 L 188,54 L 68,174 L 84,174 L 84,154 L 34,154 L 34,204 L 54,204 L 54,188 L 174,68 L 174,84 L 202,84 L 202,84 Z M 222,34 L 202,34 L 202,54 Z M 34,204 L 54,204 L 54,224 Z", base, outline)

def move(canvas_size=256, base="#00FF00", outline="#0000FF") -> str:
    return get_base_svg("M 128,30 L 158,60 L 138,60 L 138,118 L 196,118 L 196,98 L 226,128 L 196,158 L 196,138 L 138,138 L 138,196 L 158,196 L 128,226 L 98,196 L 118,196 L 118,138 L 60,138 L 60,158 L 30,128 L 60,98 L 60,118 L 118,118 L 118,60 L 98,60 Z", base, outline)
