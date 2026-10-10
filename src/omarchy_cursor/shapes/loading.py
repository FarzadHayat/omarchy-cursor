"""Animated loading cursors."""

import math

def get_base_svg(d_paths: str) -> str:
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
{d_paths}
</svg>"""

def wait(canvas_size=256, base="#00FF00", outline="#0000FF", watch="#FF0000") -> list[str]:
    """54 frames of a spinning ring."""
    frames = []
    count = 54
    center = 128
    radius = 60
    
    for i in range(count):
        paths = []
        # Background track
        paths.append(f'<circle cx="{center}" cy="{center}" r="{radius}" fill="none" stroke="{outline}" stroke-width="20" filter="url(#glow)"/>')
        paths.append(f'<circle cx="{center}" cy="{center}" r="{radius}" fill="none" stroke="{base}" stroke-width="20" stroke-opacity="0.3"/>')
        
        # Rotating arc (smooth stroke dash array trick)
        circumference = 2 * math.pi * radius
        dash_length = circumference * 0.4 # 40% of the circle is the spinning line
        offset = circumference - (i / count) * circumference
        
        paths.append(f'<circle cx="{center}" cy="{center}" r="{radius}" fill="none" stroke="{watch}" stroke-width="20" stroke-dasharray="{dash_length} {circumference}" stroke-dashoffset="{offset}" stroke-linecap="round"/>')
                    
        frames.append(get_base_svg("\n".join(paths)))
    return frames

def left_ptr_watch(canvas_size=256, base="#00FF00", outline="#0000FF", watch="#FF0000") -> list[str]:
    """54 frames of left pointer with a loading ring."""
    frames = []
    count = 54
    center_x = 160
    center_y = 160
    radius = 35
    
    for i in range(count):
        paths = []
        
        # Draw the standard pointer matching pointers.left_ptr
        arrow_d = "M 55 17 L 42 185 L 85 140 L 145 238 L 170 220 L 112 125 L 165 110 Z"
        paths.append(f'<path d="{arrow_d}" fill="{base}" stroke="{outline}" stroke-width="17" stroke-linejoin="round" filter="url(#glow)"/>')
        
        # Draw the background track for the ring
        paths.append(f'<circle cx="{center_x}" cy="{center_y}" r="{radius}" fill="none" stroke="{outline}" stroke-width="15" filter="url(#glow)"/>')
        paths.append(f'<circle cx="{center_x}" cy="{center_y}" r="{radius}" fill="none" stroke="{base}" stroke-width="15" stroke-opacity="0.3"/>')
        
        # Draw the rotating arc
        circumference = 2 * math.pi * radius
        dash_length = circumference * 0.4
        offset = circumference - (i / count) * circumference
        
        paths.append(f'<circle cx="{center_x}" cy="{center_y}" r="{radius}" fill="none" stroke="{watch}" stroke-width="15" stroke-dasharray="{dash_length} {circumference}" stroke-dashoffset="{offset}" stroke-linecap="round"/>')
        
        frames.append(get_base_svg("\n".join(paths)))
    return frames
