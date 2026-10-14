#!/usr/bin/env python3
"""Add or remove the Style > Cursor entries in the Omarchy menu.

    python3 menu.py install
    python3 menu.py remove

Entries go between marker comments in ~/.config/omarchy/extensions/omarchy-menu.jsonc,
so removing them leaves the rest of the file untouched.
"""

import json
import os
import sys
from pathlib import Path

MENU = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "omarchy/extensions/omarchy-menu.jsonc"
START = "  // omarchy-pixel-cursors start"
END = "  // omarchy-pixel-cursors end"
CONFIG = "$HOME/.config/omarchy-pixel-cursors/config.json"
SET = "$HOME/.local/bin/omarchy-cursor --save --apply"


def entries():
    rows = {"style.cursor": {"icon": "󰇀", "label": "Cursor", "aliases": ["cursor", "cursors"]}}
    for style, label, icon in [("accent", "Accent", "󰏘"), ("light", "Light", "󰖨"), ("dark", "Dark", "󰖔")]:
        saved = f"grep -q '\"style\": \"{style}\"' {CONFIG}"
        if style == "accent":
            saved = f"! grep -qs '\"style\": \"\\(light\\|dark\\)\"' {CONFIG}"
        rows[f"style.cursor.{style}"] = {
            "icon": icon, "label": label, "description": f"{label} cursor style",
            "action": f"{SET} --style {style}", "checked": saved,
        }
    for size, label in [(24, "Small"), (36, "Medium"), (48, "Large")]:
        saved = f"grep -q '\"size\": {size}[,}}]' {CONFIG}"
        if size == 24:
            saved = f"! grep -qs '\"size\": ' {CONFIG} || {saved}"
        rows[f"style.cursor.size{size}"] = {
            "icon": "󰁌", "label": f"{label} size", "description": f"Cursor size {size}",
            "action": f"{SET} --size {size}", "checked": saved,
        }
    return rows


def strip_block(text):
    if START not in text:
        return text
    before, rest = text.split(START, 1)
    after = rest.split(END, 1)[1] if END in rest else ""
    return before.rstrip("\n") + "\n" + after.lstrip("\n")


def install():
    text = MENU.read_text() if MENU.exists() else "{\n}\n"
    text = strip_block(text)
    close = text.rstrip().rfind("}")
    if close < 0:
        sys.exit(f"Can't read {MENU}; add the cursor menu by hand.")
    head = text[:close].rstrip()
    # The last real entry before ours needs a comma.
    last = [line for line in head.splitlines() if line.strip() and not line.strip().startswith("//")]
    if last and not last[-1].rstrip().endswith((",", "{")):
        head += ","
    block = "\n".join(f"  {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)},"
                      for k, v in entries().items())
    MENU.parent.mkdir(parents=True, exist_ok=True)
    MENU.write_text(f"{head}\n{START}\n{block}\n{END}\n}}\n")


def remove():
    if MENU.exists():
        MENU.write_text(strip_block(MENU.read_text()))


if __name__ == "__main__":
    {"install": install, "remove": remove}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: sys.exit(__doc__))()
