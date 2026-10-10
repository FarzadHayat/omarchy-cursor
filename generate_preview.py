#!/usr/bin/env python3
"""Generate an HTML preview of all cursors."""

import os
from pathlib import Path

def main():
    repo_root = Path(__file__).resolve().parent
    png_dir = repo_root / "build" / "png"
    
    if not png_dir.exists():
        print("Please build the cursor first by running ./install.sh")
        return

    # Find all 96px static cursors
    static_pngs = sorted([p.name for p in png_dir.glob("*_96.png") if "-" not in p.name])
    
    # Identify animated cursors
    animated_groups = {}
    animated_pngs = sorted([p.name for p in png_dir.glob("*-*_96.png")])
    for p in animated_pngs:
        prefix = p.split("-")[0]
        if prefix == "left_ptr_watch":
            prefix = "left_ptr_watch" # fix split issue
        elif p.startswith("dnd-"):
            # skip dnd-ask, dnd-copy etc which have hyphens but aren't animated
            continue
            
        # Proper detection of animated frames
        import re
        m = re.match(r'(.*?)-(\d+)_96\.png', p)
        if m:
            base_name, frame = m.groups()
            if base_name not in animated_groups:
                animated_groups[base_name] = []
            animated_groups[base_name].append(p)
            
    # Remove dnd cursors from static list since they got skipped or messed up by the naive split
    static_pngs = [p.name for p in png_dir.glob("*_96.png") if not re.match(r'(.*?)-(\d+)_96\.png', p.name)]

    html = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<title>Omarchy Cursor Preview</title>",
        "<style>",
        "body { font-family: system-ui, sans-serif; background: #1e1e2e; color: #cdd6f4; margin: 0; padding: 40px; }",
        "h1 { text-align: center; margin-bottom: 40px; color: #89b4fa; }",
        ".grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 20px; }",
        ".cursor-card { background: #313244; border-radius: 12px; padding: 20px; text-align: center; transition: transform 0.2s; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }",
        ".cursor-card:hover { transform: translateY(-5px); background: #45475a; }",
        ".cursor-card img { width: 96px; height: 96px; image-rendering: pixelated; margin-bottom: 10px; }",
        ".cursor-name { font-size: 14px; word-break: break-all; color: #bac2de; font-family: monospace; }",
        "</style>",
        "</head>",
        "<body>",
        "<h1>Omarchy Cursor Preview</h1>",
        "<div class='grid'>"
    ]

    # Add static cursors
    for png in sorted(static_pngs):
        name = png.replace("_96.png", "")
        html.append(f"""
        <div class="cursor-card">
            <img src="build/png/{png}" alt="{name}">
            <div class="cursor-name">{name}</div>
        </div>
        """)

    # Add animated cursors
    for base_name, frames in animated_groups.items():
        frames_js = str([f"build/png/{f}" for f in frames])
        html.append(f"""
        <div class="cursor-card">
            <img id="anim-{base_name}" src="build/png/{frames[0]}" alt="{base_name}">
            <div class="cursor-name">{base_name} (Animated)</div>
            <script>
                (function() {{
                    const frames = {frames_js};
                    let i = 0;
                    const img = document.getElementById('anim-{base_name}');
                    setInterval(() => {{
                        i = (i + 1) % frames.length;
                        img.src = frames[i];
                    }}, 40); // 40ms delay matching config
                }})();
            </script>
        </div>
        """)

    html.extend([
        "</div>",
        "</body>",
        "</html>"
    ])

    out_path = repo_root / "preview.html"
    with open(out_path, "w") as f:
        f.write("\n".join(html))
    
    print(f"Preview generated at: file://{out_path.absolute()}")

if __name__ == "__main__":
    main()
