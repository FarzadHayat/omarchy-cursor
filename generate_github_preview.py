#!/usr/bin/env python3
"""Generate images for GitHub README."""

from pathlib import Path
import re
from PIL import Image, ImageDraw

def main():
    repo_root = Path(__file__).resolve().parent
    png_dir = repo_root / "build" / "png"
    preview_dir = repo_root / "preview"
    preview_dir.mkdir(exist_ok=True)
    
    if not png_dir.exists():
        print("Please build the cursor first")
        return

    # Identify cursors
    static_pngs = sorted([p for p in png_dir.glob("*_96.png") if not re.match(r'(.*?)-(\d+)_96\.png', p.name)])
    
    animated_groups = {}
    animated_pngs = sorted([p for p in png_dir.glob("*-*_96.png")])
    for p in animated_pngs:
        m = re.match(r'(.*?)-(\d+)_96\.png', p.name)
        if m:
            base_name, frame = m.groups()
            if base_name not in animated_groups:
                animated_groups[base_name] = []
            animated_groups[base_name].append(p)

    # 1. Create Animated GIFs
    print("Generating GIFs for animated cursors...")
    for base_name, frames in animated_groups.items():
        if not frames:
            continue
        
        # Load frames
        images = [Image.open(f) for f in frames]
        
        # Save as GIF
        gif_path = preview_dir / f"{base_name}.gif"
        images[0].save(
            gif_path,
            save_all=True,
            append_images=images[1:],
            duration=40, # 40ms per frame
            loop=0, # loop forever
            disposal=2 # clear frame before next
        )
        print(f"Created {gif_path.name}")

    # 2. Create Grid of Static Cursors
    print("Generating static cursor grid...")
    # Filter to show a nice selection, or show all. Let's show all in a grid.
    cols = 8
    rows = (len(static_pngs) + cols - 1) // cols
    
    cell_w = 120
    cell_h = 140
    img_w = cols * cell_w
    img_h = rows * cell_h
    
    # Dark background matching Omarchy
    grid_img = Image.new('RGBA', (img_w, img_h), (30, 30, 46, 255))
    draw = ImageDraw.Draw(grid_img)
    
    for i, p in enumerate(static_pngs):
        col = i % cols
        row = i // cols
        
        x = col * cell_w
        y = row * cell_h
        
        # Paste cursor icon centered horizontally in the cell
        icon = Image.open(p)
        grid_img.paste(icon, (x + (cell_w - 96) // 2, y + 10), icon)
        
        # Draw name below it
        name = p.name.replace("_96.png", "")
        # Truncate if too long
        if len(name) > 14:
            name = name[:12] + ".."
            
        # Draw text (just using default font)
        # Fallback to simple text drawing since we don't know if specific TTF exists
        text_bbox = draw.textbbox((0, 0), name)
        text_w = text_bbox[2] - text_bbox[0]
        draw.text((x + (cell_w - text_w) // 2, y + 115), name, fill=(205, 214, 244, 255))

    grid_path = preview_dir / "grid.png"
    grid_img.save(grid_path)
    print(f"Created {grid_path.name}")

if __name__ == "__main__":
    main()
