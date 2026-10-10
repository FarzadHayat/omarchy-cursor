"""Render SVGs to PNGs and build Xcursor themes."""

import os
import sys
import argparse
import subprocess
import shutil
import tomllib
from pathlib import Path

try:
    import cairosvg
except ImportError:
    print("Error: cairosvg is required. Install with: pip install cairosvg")
    sys.exit(1)

from . import generate
from . import colorize

def render_svgs(svg_dir: Path, png_dir: Path, sizes: list[int]):
    """Render SVGs to PNGs at multiple sizes."""
    png_dir.mkdir(parents=True, exist_ok=True)
    
    svg_files = list(svg_dir.glob("*.svg"))
    total = len(svg_files)
    
    for i, svg_file in enumerate(svg_files):
        print(f"Rendering {i+1}/{total}: {svg_file.name}")
        for size in sizes:
            out_file = png_dir / f"{svg_file.stem}_{size}.png"
            cairosvg.svg2png(
                url=str(svg_file),
                write_to=str(out_file),
                output_width=size,
                output_height=size
            )

def build_xcursors(png_dir: Path, output_dir: Path, config: dict):
    """Build Xcursor files using xcursorgen."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    fallback = config.get("fallback", {})
    sizes = fallback.get("sizes", [24, 32, 48, 64, 96])
    canvas_size = fallback.get("canvas_size", 256)
    delay = fallback.get("animation_delay", 40)
    
    cursors = config.get("cursors", {})
    
    for name, metadata in cursors.items():
        print(f"Building Xcursor: {name}")
        
        # Calculate hotspots for each size based on canvas proportion
        x_hot = metadata.get("x_hotspot", fallback.get("x_hotspot", 128))
        y_hot = metadata.get("y_hotspot", fallback.get("y_hotspot", 128))
        
        is_animated = metadata.get("animated", False)
        
        cursor_file_path = png_dir / f"{name}.cursor"
        
        with open(cursor_file_path, "w") as f:
            if is_animated:
                # Find all frames
                frames = sorted(png_dir.glob(f"{name}-*.png"))
                # Group by frame number
                import re
                frame_numbers = sorted(list(set([re.search(r'-(\d+)_', f.name).group(1) for f in frames if re.search(r'-(\d+)_', f.name)])))
                
                for size in sizes:
                    scaled_x_hot = int(x_hot * size / canvas_size)
                    scaled_y_hot = int(y_hot * size / canvas_size)
                    
                    for frame_num in frame_numbers:
                        frame_png = f"{name}-{frame_num}_{size}.png"
                        if (png_dir / frame_png).exists():
                            f.write(f"{size} {scaled_x_hot} {scaled_y_hot} {frame_png} {delay}\n")
            else:
                for size in sizes:
                    scaled_x_hot = int(x_hot * size / canvas_size)
                    scaled_y_hot = int(y_hot * size / canvas_size)
                    
                    png_name = f"{name}_{size}.png"
                    if (png_dir / png_name).exists():
                        f.write(f"{size} {scaled_x_hot} {scaled_y_hot} {png_name}\n")
        
        # Run xcursorgen
        out_cursor = output_dir / name
        try:
            subprocess.run(["xcursorgen", str(cursor_file_path), str(out_cursor)], 
                           cwd=str(png_dir), check=True, capture_output=True)
        except Exception as e:
            print(f"Error running xcursorgen for {name}: {e}")
            
        # Create symlinks
        if out_cursor.exists():
            symlinks = metadata.get("symlinks", [])
            for symlink in symlinks:
                symlink_path = output_dir / symlink
                if not symlink_path.exists():
                    os.symlink(name, str(symlink_path))

def create_theme_files(theme_dir: Path, theme_name: str):
    """Create index.theme."""
    index_content = f"""[Icon Theme]
Name={theme_name}
Comment=Omarchy cursor theme
Inherits=hicolor
"""
    with open(theme_dir / "index.theme", "w") as f:
        f.write(index_content)
        
    with open(theme_dir / "cursor.theme", "w") as f:
        f.write(f"[Icon Theme]\nName={theme_name}\nInherits={theme_name}\n")

def build_hyprcursor(theme_dir: Path, config: dict, png_dir: Path):
    """Build Hyprcursor configuration."""
    print("Building Hyprcursor theme...")
    hypr_dir = theme_dir / "hyprcursors"
    hypr_dir.mkdir(exist_ok=True)
    
    # manifest
    with open(theme_dir / "manifest.hl", "w") as f:
        f.write(f"""name = {theme_dir.name}
description = Omarchy cursor theme
version = 1.0
cursors_directory = hyprcursors
""")

    fallback = config.get("fallback", {})
    canvas_size = fallback.get("canvas_size", 256)
    delay = fallback.get("animation_delay", 40)
    
    cursors = config.get("cursors", {})
    for name, metadata in cursors.items():
        cursor_dir = hypr_dir / name
        cursor_dir.mkdir(exist_ok=True)
        
        x_hot = metadata.get("x_hotspot", fallback.get("x_hotspot", 128))
        y_hot = metadata.get("y_hotspot", fallback.get("y_hotspot", 128))
        
        # Normalize hotspots to 0.0 - 1.0
        norm_x = x_hot / canvas_size
        norm_y = y_hot / canvas_size
        
        meta_content = f"""resize_algorithm = bilinear
hotspot_x = {norm_x:.4f}
hotspot_y = {norm_y:.4f}
"""
        
        is_animated = metadata.get("animated", False)
        if is_animated:
            # For hyprcursor we use the largest rendered pngs for better scaling
            frames = sorted(png_dir.glob(f"{name}-*_96.png"))
            for frame in frames:
                shutil.copy(frame, cursor_dir / frame.name)
                meta_content += f"frame = {frame.name}, {delay}\n"
        else:
            # Copy largest png
            png_name = f"{name}_96.png"
            if (png_dir / png_name).exists():
                shutil.copy(png_dir / png_name, cursor_dir / png_name)
                meta_content += f"frame = {png_name}, 0\n"
                
        with open(cursor_dir / "meta.hl", "w") as f:
            f.write(meta_content)
            
        # Symlinks for hyprcursor
        symlinks = metadata.get("symlinks", [])
        for symlink in symlinks:
            symlink_dir = hypr_dir / symlink
            if not symlink_dir.exists():
                os.symlink(name, str(symlink_dir))
                
def main():
    parser = argparse.ArgumentParser(description="Build Omarchy Cursor Theme")
    parser.add_argument("--theme", help="Omarchy theme name to sync colors with")
    parser.add_argument("--base", help="Base/fill color (hex)")
    parser.add_argument("--outline", help="Outline/stroke color (hex)")
    parser.add_argument("--watch", help="Watch/accent color (hex)")
    parser.add_argument("--install", action="store_true", help="Install to ~/.local/share/icons")
    parser.add_argument("--name", default="Omarchy-Cursor", help="Output theme name")
    
    args = parser.parse_args()
    
    # Determine colors
    base_color = args.base
    outline_color = args.outline
    watch_color = args.watch
    
    if args.theme:
        try:
            colors = colorize.extract_omarchy_colors(args.theme)
            base_color, outline_color, watch_color = colorize.compute_cursor_colors(
                colors, args.base, args.outline, args.watch
            )
        except Exception as e:
            print(f"Error loading theme {args.theme}: {e}")
            sys.exit(1)
    
    # Defaults if not specified
    if not base_color: base_color = "#89b4fa"
    if not outline_color: outline_color = "#1e1e2e"
    if not watch_color: watch_color = colorize.darken_color(base_color, 0.2)
    
    print(f"Building theme '{args.name}' with colors:")
    print(f"  Base:    {base_color}")
    print(f"  Outline: {outline_color}")
    print(f"  Watch:   {watch_color}")
    
    # Setup paths
    repo_root = Path(__file__).resolve().parent.parent.parent
    build_dir = repo_root / "build"
    svg_dir = build_dir / "svg"
    png_dir = build_dir / "png"
    
    if args.install:
        out_dir = Path.home() / ".local" / "share" / "icons" / args.name
    else:
        out_dir = repo_root / "output" / args.name
        
    cursors_out_dir = out_dir / "cursors"
    
    # Clean build dirs
    for d in [svg_dir, png_dir, out_dir]:
        if d.exists():
            shutil.rmtree(d)
    
    # Load config
    config_path = repo_root / "config" / "cursors.toml"
    with open(config_path, "rb") as f:
        config = tomllib.load(f)
        
    # 1. Generate SVGs
    print("Generating SVGs...")
    generate.generate_all(svg_dir, base=base_color, outline=outline_color, watch=watch_color)
    
    # 2. Render to PNGs
    print("Rendering PNGs...")
    fallback = config.get("fallback", {})
    sizes = fallback.get("sizes", [24, 32, 48, 64, 96])
    render_svgs(svg_dir, png_dir, sizes)
    
    # 3. Build Xcursor
    print("Building Xcursor theme...")
    build_xcursors(png_dir, cursors_out_dir, config)
    
    # 4. Create Theme metadata
    create_theme_files(out_dir, args.name)
    
    # 5. Build Hyprcursor
    build_hyprcursor(out_dir, config, png_dir)
    
    print(f"Successfully built {args.name} at {out_dir}")
    
    if args.install:
        print(f"You can now apply it using: hyprctl setcursor {args.name} 24")

if __name__ == "__main__":
    main()
