#!/usr/bin/env python3
"""Build script for omarchy-cursor.

Wrapper around the omarchy_cursor module.
"""

import sys
from pathlib import Path

# Add src to python path so we can run directly
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from omarchy_cursor.render import main

if __name__ == "__main__":
    main()
