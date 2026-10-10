"""SVG generation orchestrator."""

import os
from pathlib import Path
from .shapes import pointers, hands, text, resize, actions, dnd, loading, misc

def generate_all(output_dir: Path, base="#00FF00", outline="#0000FF", watch="#FF0000"):
    """Generate all SVGs and save them to output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    shapes = {
        "left_ptr": pointers.left_ptr,
        "right_ptr": pointers.right_ptr,
        "center_ptr": pointers.center_ptr,
        
        "hand1": hands.hand1,
        "hand2": hands.hand2,
        "grabbing": hands.grabbing,
        
        "xterm": text.xterm,
        "vertical-text": text.vertical_text,
        
        "top_side": resize.top_side,
        "bottom_side": resize.bottom_side,
        "left_side": resize.left_side,
        "right_side": resize.right_side,
        "top_left_corner": resize.top_left_corner,
        "top_right_corner": resize.top_right_corner,
        "bottom_left_corner": resize.bottom_left_corner,
        "bottom_right_corner": resize.bottom_right_corner,
        "sb_h_double_arrow": resize.sb_h_double_arrow,
        "sb_v_double_arrow": resize.sb_v_double_arrow,
        "bd_double_arrow": resize.bd_double_arrow,
        "fd_double_arrow": resize.fd_double_arrow,
        "move": resize.move,
        
        "crosshair": actions.crosshair,
        "pencil": actions.pencil,
        "plus": actions.plus,
        "zoom-in": actions.zoom_in,
        "zoom-out": actions.zoom_out,
        "tcross": actions.tcross,
        "dotbox": actions.dotbox,
        
        "copy": dnd.copy,
        "link": dnd.link,
        "dnd-ask": dnd.dnd_ask,
        "dnd-copy": dnd.dnd_copy,
        "dnd-link": dnd.dnd_link,
        "dnd_no_drop": dnd.dnd_no_drop,
        
        "circle": misc.circle,
        "crossed_circle": misc.crossed_circle,
        "context-menu": misc.context_menu,
        "question_arrow": misc.question_arrow,
        "X_cursor": misc.X_cursor,
        "cross": misc.cross,
        "pointer-move": misc.pointer_move,
        "person": misc.person,
        "pin": misc.pin,
        "wayland-cursor": misc.wayland_cursor,
    }
    
    animated_shapes = {
        "wait": loading.wait,
        "left_ptr_watch": loading.left_ptr_watch,
    }
    
    for name, func in shapes.items():
        svg_content = func(canvas_size=256, base=base, outline=outline)
        with open(output_dir / f"{name}.svg", "w") as f:
            f.write(svg_content)
            
    for name, func in animated_shapes.items():
        frames = func(canvas_size=256, base=base, outline=outline, watch=watch)
        for i, frame_content in enumerate(frames):
            frame_name = f"{name}-{i+1:02d}.svg"
            with open(output_dir / frame_name, "w") as f:
                f.write(frame_content)
