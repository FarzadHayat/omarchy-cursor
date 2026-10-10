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
    """54 frames of orbital dots."""
    frames = []
    count = 54
    center = 128
    radius = 60
    dot_radius = 12
    for i in range(count):
        paths = []
        # Draw base static ring outline
        paths.append(f'<circle cx="{center}" cy="{center}" r="{radius}" fill="none" stroke="{outline}" stroke-width="17" stroke-linecap="round" filter="url(#glow)"/>')
        
        # 3 dots with trailing opacity
        for j in range(3):
            # Calculate angle for the dot
            base_angle = (i / count) * 360 + (j * 120)
            
            # Create trail
            num_trails = 5
            for k in range(num_trails):
                trail_angle = base_angle - (k * 8)
                rad = math.radians(trail_angle)
                x = center + radius * math.cos(rad)
                y = center + radius * math.sin(rad)
                opacity = 1.0 - (k / num_trails)
                if opacity > 0:
                    r = max(2, dot_radius - k * 1.5)
                    paths.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{watch}" fill-opacity="{opacity}"/>')
                    
        frames.append(get_base_svg("\n".join(paths)))
    return frames

def left_ptr_watch(canvas_size=256, base="#00FF00", outline="#0000FF", watch="#FF0000") -> list[str]:
    """54 frames of left pointer with a loading ring."""
    frames = []
    count = 54
    center_x = 160
    center_y = 160
    radius = 40
    
    for i in range(count):
        paths = []
        
        # Draw the standard pointer
        arrow_d = "M 55,17 L 55,200 L 100,160 L 145,220 L 175,200 L 130,140 L 195,140 Z"
        paths.append(f'<path d="{arrow_d}" fill="{base}" stroke="{outline}" stroke-width="17" stroke-linejoin="round" filter="url(#glow)"/>')
        
        # Draw the background track for the ring
        paths.append(f'<circle cx="{center_x}" cy="{center_y}" r="{radius}" fill="none" stroke="{outline}" stroke-width="17" filter="url(#glow)"/>')
        paths.append(f'<circle cx="{center_x}" cy="{center_y}" r="{radius}" fill="none" stroke="{base}" stroke-width="17" stroke-opacity="0.2"/>')
        
        # Draw the rotating arc
        # We'll use a stroke-dasharray trick to make it look like it's filling up or rotating
        circumference = 2 * math.pi * radius
        progress = (i / count)
        dash_length = circumference * 0.25 # 25% of the circle
        offset = circumference * (1 - progress)
        
        paths.append(f'<circle cx="{center_x}" cy="{center_y}" r="{radius}" fill="none" stroke="{watch}" stroke-width="17" stroke-dasharray="{dash_length} {circumference}" stroke-dashoffset="{offset}" stroke-linecap="round" transform="rotate(-90 {center_x} {center_y})"/>')
        
        frames.append(get_base_svg("\n".join(paths)))
    return frames
