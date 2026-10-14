"""8-bit pixel art for Omarchy Cursor.

Every cursor is a 17x17 grid of palette keys, drawn as ASCII art or built from
small grid operations. Outlines, the top left bevel and a hard drop shadow are
added automatically, so the art only has to describe the filled shape:

    #  body          r  danger body     s  sand / flat body
    t  dim track     h  bright head     X  rim (explicit marks inside a shape)
    .  empty
"""

import math
import struct
import zlib

N = 17  # art grid; the image canvas is one pixel larger to fit the shadow
CANVAS = N + 1
BEVELED = {"#": ("w", "d"), "r": ("R", "D")}
# Grid keys to Palette roles in build.py.
KEYS = {"#": "body", "w": "hi", "d": "lo", "s": "body", "t": "track", "h": "head",
        "r": "danger", "R": "danger_hi", "D": "danger_lo", "X": "rim"}
SOLID = set("#rsthwdRDX")


class Grid:
    def __init__(self, rows=None):
        self.px = [["."] * N for _ in range(N)]
        for y, row in enumerate(rows or []):
            for x, c in enumerate(row):
                if c != ".":
                    self.px[y][x] = c

    def copy(self):
        g = Grid()
        g.px = [r[:] for r in self.px]
        return g

    def get(self, x, y):
        return self.px[y][x] if 0 <= x < N and 0 <= y < N else "."

    def put(self, x, y, c):
        if 0 <= x < N and 0 <= y < N:
            self.px[y][x] = c
        return self

    def where(self, test, c):
        for y in range(N):
            for x in range(N):
                if test(x, y):
                    self.px[y][x] = c
        return self

    def over(self, other):
        """Paint other's non empty pixels on top of this grid."""
        for y in range(N):
            for x in range(N):
                if other.px[y][x] != ".":
                    self.px[y][x] = other.px[y][x]
        return self

    def map(self, f):
        g = Grid()
        for y in range(N):
            for x in range(N):
                sx, sy = f(x, y)
                g.px[y][x] = self.get(sx, sy)
        return g

    def rot90(self):  # clockwise
        return self.map(lambda x, y: (y, N - 1 - x))

    def flip(self):
        return self.map(lambda x, y: (N - 1 - x, y))

    def transpose(self):
        return self.map(lambda x, y: (y, x))


def finish(grid):
    """Outline, bevel and shadow; returns a CANVAS x CANVAS grid of color keys."""
    g = [["."] * CANVAS for _ in range(CANVAS)]
    for y in range(N):
        for x in range(N):
            g[y][x] = grid.px[y][x]

    def at(x, y):
        return g[y][x] if 0 <= x < CANVAS and 0 <= y < CANVAS else "."

    outline = [(x, y) for y in range(CANVAS) for x in range(CANVAS) if g[y][x] == "."
               and any(at(x + dx, y + dy) not in ".X" for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for x, y in outline:
        g[y][x] = "X"
    edge = set(outline)

    shaded = [r[:] for r in g]
    for y in range(CANVAS):
        for x in range(CANVAS):
            c = g[y][x]
            if c in BEVELED:
                hi, lo = BEVELED[c]
                # Light from the top left; stair steps on right edges stay unlit.
                if (x - 1, y) in edge or ((x, y - 1) in edge and (x + 1, y) not in edge):
                    shaded[y][x] = hi
                elif (x, y + 1) in edge:
                    shaded[y][x] = lo
    for y in range(CANVAS):
        for x in range(CANVAS):
            if shaded[y][x] == "." and x > 0 and y > 0 and shaded[y - 1][x - 1] in SOLID:
                shaded[y][x] = "shadow"
    return shaded


def png(grid, colors, scale):
    """Encode a finished grid as an RGBA PNG, each art pixel scale x scale."""
    size = CANVAS * scale
    raw = bytearray()
    for y in range(size):
        raw.append(0)
        for x in range(size):
            raw += bytes(colors.get(grid[y // scale][x // scale], (0, 0, 0, 0)))

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


class Cursor:
    def __init__(self, name, hotspot, frames, aliases=(), delay=0):
        self.name = name
        self.hotspot = hotspot  # art pixel
        self.frames = frames  # list of Grid
        self.aliases = list(aliases)
        self.delay = delay


# ── Art ───────────────────────────────────────────────────

def arrow():
    """Arrowhead symmetric about the diagonal, tip at (1, 1), with a notched back."""
    def inside(x, y):
        a, b = x - 1, y - 1
        along, across = a + b, abs(a - b)
        return a >= 0 and b >= 0 and across <= along * 0.4 + 1 and along <= 10 + across * 1.5 and along <= 14

    return Grid().where(inside, "#")


ARROW = arrow()

POINTER = Grid([
    ".................",
    ".....##..........",
    ".....##..........",
    ".....##..........",
    ".....##..........",
    ".....##.##.......",
    ".....##.##.##....",
    ".....##.##.##.#..",
    "..##.##.##.##.#..",
    "..##.##########..",
    "..#############..",
    "...############..",
    "...###########...",
    "....##########...",
    ".....########....",
])

GRAB = Grid([
    ".................",
    "........##.......",
    ".....##.##.##....",
    ".....##.##.##....",
    ".....##.##.##.#..",
    ".....##.##.##.#..",
    ".....##.##.##.#..",
    "..#..##.##.##.#..",
    "..##.##.##.##.#..",
    "...############..",
    "...############..",
    "....###########..",
    "....##########...",
    ".....########....",
])

GRABBING = Grid([
    ".................",
    ".................",
    ".................",
    ".................",
    "....##.##.##.##..",
    "....##X##X##X##..",
    "..#############..",
    "..###X#########..",
    "...#X##########..",
    "...############..",
    "....##########...",
    ".....########....",
])

IBEAM = Grid([
    ".................",
    ".................",
    "......##.##......",
    "........#........",
    "........#........",
    "........#........",
    "........#........",
    "........#........",
    ".......###.......",
    "........#........",
    "........#........",
    "........#........",
    "........#........",
    "........#........",
    "......##.##......",
])


def disk(cx, cy, r0, r1, c="#"):
    return Grid().where(lambda x, y: r0 <= math.hypot(x - cx, y - cy) <= r1, c)


def up_arrow_head(g, tip_x, tip_y, depth=3, c="#"):
    for i in range(depth):
        for x in range(tip_x - i, tip_x + i + 1):
            g.put(x, tip_y + i, c)
    return g


def double_arrow():
    g = Grid().where(lambda x, y: y == 8 and 3 <= x <= 13, "#")
    left = up_arrow_head(Grid(), 8, 1).rot90().rot90().rot90()
    return g.over(left).over(left.flip())


def edge_arrow():  # arrow pushing up against a bar, for n-resize
    g = Grid().where(lambda x, y: y == 1 and 4 <= x <= 12, "#")
    up_arrow_head(g, 8, 4)
    return g.where(lambda x, y: x == 8 and 7 <= y <= 15, "#")


def diagonal_arrow():  # double headed, top left to bottom right
    g = Grid().where(lambda x, y: x - y in (0, 1) and 4 <= x <= 12, "#")
    head = Grid().where(lambda x, y: 2 <= x <= 6 and 2 <= y <= 6 and x + y <= 8, "#")
    return g.over(head).over(head.rot90().rot90())


def corner_arrow():  # arrow pushing into the top left corner
    g = Grid().where(lambda x, y: (y == 1 and 1 <= x <= 7) or (x == 1 and 1 <= y <= 7), "#")
    g.where(lambda x, y: 4 <= x <= 8 and 4 <= y <= 8 and x + y <= 12, "#")
    return g.where(lambda x, y: x - y in (0, 1) and 8 <= x <= 14, "#")


def split_arrow():  # col-resize: two bars with arrows pushing outward
    g = Grid().where(lambda x, y: x in (7, 9) and 4 <= y <= 12, "#")
    g.where(lambda x, y: y == 8 and (3 <= x <= 5 or 11 <= x <= 13), "#")
    left = up_arrow_head(Grid(), 8, 0).rot90().rot90().rot90()
    return g.over(left).over(left.flip())


def badge(glyph=(), c="#", square=False):
    g = Grid().where(lambda x, y: 10 <= x <= 16 and 10 <= y <= 16, c)
    if not square:
        for x, y in ((10, 10), (16, 10), (10, 16), (16, 16)):
            g.put(x, y, ".")
    for x, y in glyph:
        g.put(x, y, "X")
    return g


def with_badge(b):
    return ARROW.copy().where(lambda x, y: x >= 9 and y >= 9, ".").over(b)


def glyph(rows, ox=11, oy=11):
    return [(ox + x, oy + y) for y, row in enumerate(rows) for x, c in enumerate(row) if c == "X"]


def hourglass(t):
    """Hourglass with sand draining; t in [0, 1]."""
    top = [(x, y) for y in range(3, 8) for x in range(8 - (8 - y), 8 + (8 - y) + 1)]
    bottom = [(x, y) for y in range(9, 14) for x in range(8 - (y - 8), 8 + (y - 8) + 1)]
    g = Grid().where(lambda x, y: y in (1, 15) and 2 <= x <= 14, "#")
    for x, y in top + bottom + [(8, 8)]:
        g.put(x, y, "t")
    drained = round(len(top) * t)
    top.sort(key=lambda p: (p[1], abs(p[0] - 8)))  # surface dips in the middle first
    bottom.sort(key=lambda p: (13 - p[1]) + abs(p[0] - 8) * 0.6)  # pile builds a mound
    for x, y in top[drained:]:
        g.put(x, y, "s")
    for x, y in bottom[:drained]:
        g.put(x, y, "s")
    if 0 < drained < len(top):
        g.put(8, 8, "h")
        g.put(8, 9 + drained % 2, "h")
    return g


RING = ([(x, 10) for x in range(11, 15)] + [(15, y) for y in range(11, 15)]
        + [(x, 15) for x in range(14, 10, -1)] + [(10, y) for y in range(14, 10, -1)])


def mini_spinner(step):
    g = Grid().where(lambda x, y: 10 <= x <= 15 and 10 <= y <= 15, "t")
    for x, y in ((10, 10), (15, 10), (10, 15), (15, 15)):
        g.put(x, y, ".")
    g.where(lambda x, y: 11 <= x <= 14 and 11 <= y <= 14, "X")
    for i, c in enumerate(("h", "h", "s", "s", "s")):
        x, y = RING[(step - i) % len(RING)]
        g.put(x, y, c)
    return g


def pencil():
    g = Grid().where(lambda x, y: 16 <= x + y <= 18 and 5 <= x <= 14 and 2 <= y, "#")
    g.where(lambda x, y: 16 <= x + y <= 18 and x == 12, "X")
    g.where(lambda x, y: 16 <= x + y <= 18 and x >= 13, "w")
    g.where(lambda x, y: (x, y) in {(3, 13), (4, 12), (3, 14), (4, 13), (5, 12), (4, 11)}, "#")
    return g.put(2, 14, "X")


def dropper():
    """Eyedropper lying on the diagonal: bulb top right, tip at (2, 14)."""
    def part(x, y):
        along, across = x - y, x + y - 16
        if -12 <= along <= -9 and across in (0, 1):
            return "t"  # tip
        if -8 <= along <= 1 and -1 <= across <= 1:
            return "s" if along <= -3 else "t"  # glass tube, part filled
        if 2 <= along <= 3 and -4 <= across <= 4:
            return "#"  # collar flange
        if 5 <= along <= 12 and -3 <= across <= 3 and abs(across) + max(0, along - 9) <= 4:
            return "r"  # rubber bulb
        return "."

    g = Grid()
    for y in range(N):
        for x in range(N):
            g.put(x, y, part(x, y))
    return g


def lens(plus):
    g = disk(6, 6, 0, 4.6).where(lambda x, y: x - y in (0, 1) and 10 <= x <= 15 and 9 <= y <= 15, "#")
    g.where(lambda x, y: y == 6 and 4 <= x <= 8, "X")
    if plus:
        g.where(lambda x, y: x == 6 and 4 <= y <= 8, "X")
    return g


def center_arrow():
    g = Grid()
    for y in range(1, 13):
        half = (y - 1) // 2
        for x in range(8 - half, 8 + half + 1):
            g.put(x, y, "#")
    return g.where(lambda x, y: y >= 10 and abs(x - 8) <= (y - 10) * 2, ".")


# ── Cursor list ───────────────────────────────────────────


def all_cursors(frames=16, delay=70):
    yield Cursor("default", (1, 1), [ARROW],
                 ["left_ptr", "arrow", "top_left_arrow", "wayland-cursor", "x-cursor"])
    yield Cursor("right_ptr", (15, 1), [ARROW.flip()], ["draft_large", "draft_small", "right-arrow"])
    yield Cursor("center_ptr", (8, 1), [center_arrow()])
    yield Cursor("pointer", (5, 1), [POINTER],
                 ["hand2", "hand", "pointing_hand", "9d800788f1b08800ae810202380a0822",
                  "e29285e634086352946a0e7090d73106"])
    yield Cursor("grab", (8, 8), [GRAB], ["openhand", "hand1", "5aca4d189052212118709018842178c0"])
    yield Cursor("grabbing", (8, 8), [GRABBING],
                 ["closedhand", "dnd-move", "dnd-none", "fcf21c00b30f7e3f83fe0dfd12e71cff"])
    yield Cursor("text", (8, 8), [IBEAM], ["xterm", "ibeam"])
    yield Cursor("vertical-text", (8, 8), [IBEAM.transpose()], ["048008013003cff3c00c801001200000"])

    cross = Grid().where(lambda x, y: (x == 8 and (1 <= y <= 5 or 11 <= y <= 15))
                         or (y == 8 and (1 <= x <= 5 or 11 <= x <= 15)) or (x, y) == (8, 8), "#")
    yield Cursor("crosshair", (8, 8), [cross], ["cross", "tcross", "cross_reverse", "diamond_cross"])
    plus = Grid().where(lambda x, y: (7 <= x <= 9 and 3 <= y <= 13) or (7 <= y <= 9 and 3 <= x <= 13), "#")
    yield Cursor("cell", (8, 8), [plus], ["plus"])
    target = disk(8, 8, 4.5, 5.6).over(disk(8, 8, 0, 1.2))
    yield Cursor("dotbox", (8, 8), [target], ["target", "dot_box_mask", "draped_box", "icon"])
    x_mark = Grid().where(lambda x, y: 3 <= x <= 13 and 3 <= y <= 13
                          and (abs(x - y) <= 1 or abs(x + y - 16) <= 1), "#")
    yield Cursor("X_cursor", (8, 8), [x_mark], ["pirate", "kill"])

    ew = double_arrow()
    yield Cursor("ew-resize", (8, 8), [ew],
                 ["sb_h_double_arrow", "h_double_arrow", "size_hor", "left_right",
                  "14fef782d02440884392942c11205230", "028006030e0e7ebffc7f7070c0600140"])
    yield Cursor("ns-resize", (8, 8), [ew.transpose()],
                 ["sb_v_double_arrow", "v_double_arrow", "size_ver", "up_down",
                  "2870a09082c103050810ffdffffe0204", "00008160000006810000408080010102"])
    diag = diagonal_arrow()
    yield Cursor("nwse-resize", (8, 8), [diag],
                 ["bd_double_arrow", "size_fdiag", "c7088f0f3e6c8088236ef8e1e3e70000"])
    yield Cursor("nesw-resize", (8, 8), [diag.flip()],
                 ["fd_double_arrow", "size_bdiag", "fcf1c3c7cd4491d801f1e1c78f100000"])

    edge, corner = edge_arrow(), corner_arrow()
    for name, turns, aliases in [
        ("n-resize", 0, ["top_side", "sb_up_arrow", "up_arrow"]),
        ("e-resize", 1, ["right_side", "sb_right_arrow", "right_arrow"]),
        ("s-resize", 2, ["bottom_side", "sb_down_arrow", "down_arrow"]),
        ("w-resize", 3, ["left_side", "sb_left_arrow", "left_arrow"]),
    ]:
        g = edge
        for _ in range(turns):
            g = g.rot90()
        yield Cursor(name, (8, 8), [g], aliases)
    for name, turns, aliases in [
        ("nw-resize", 0, ["top_left_corner", "ul_angle"]),
        ("ne-resize", 1, ["top_right_corner", "ur_angle"]),
        ("se-resize", 2, ["bottom_right_corner", "lr_angle"]),
        ("sw-resize", 3, ["bottom_left_corner", "ll_angle"]),
    ]:
        g = corner
        for _ in range(turns):
            g = g.rot90()
        yield Cursor(name, (8, 8), [g], aliases)

    split = split_arrow()
    yield Cursor("col-resize", (8, 8), [split], ["split_h"])
    yield Cursor("row-resize", (8, 8), [split.transpose()], ["split_v"])
    move = Grid().where(lambda x, y: (x == 8 and 3 <= y <= 13) or (y == 8 and 3 <= x <= 13), "#")
    head = up_arrow_head(Grid(), 8, 1)
    for g in (head, head.rot90(), head.rot90().rot90(), head.rot90().rot90().rot90()):
        move.over(g)
    yield Cursor("move", (8, 8), [move],
                 ["fleur", "size_all", "4498f0e0c1937ffe01fd06f973665830",
                  "9081237383d90e509aa00f00170e968f"])

    scroll = disk(8, 8, 0, 1.2)
    head = up_arrow_head(Grid(), 8, 1)
    for g in (head, head.rot90(), head.rot90().rot90(), head.rot90().rot90().rot90()):
        scroll.over(g)
    yield Cursor("all-scroll", (8, 8), [scroll], ["scroll"])

    sand = [hourglass(i / (frames - 1)) for i in range(frames)]
    wait = sand + [sand[-1], sand[-1].rot90()]  # hold, then a quarter turn back to the start
    yield Cursor("wait", (8, 8), wait, ["watch", "clock"], delay * 2)
    progress = [with_badge(mini_spinner(i)) for i in range(len(RING))]
    yield Cursor("progress", (1, 1), progress,
                 ["left_ptr_watch", "half-busy", "00000000000000020006000e7e9ffc3f",
                  "08e8e1c95fe2fc01f976f1e063a24ccd", "3ecb610c1bf2410f44200f48c40d3599"], delay)

    yield Cursor("help", (1, 1), [with_badge(badge(glyph([".XXX.", "X...X", "..XX.", ".....", "..X.."])))],
                 ["question_arrow", "whats_this", "left_ptr_help", "dnd-ask",
                  "d9ce0ab605698f320427677b458ad60b", "5c6cd98b3f3ebcb1f9c7f1c204630408"])
    yield Cursor("copy", (1, 1), [with_badge(badge(glyph(["..X..", "..X..", "XXXXX", "..X..", "..X.."])))],
                 ["dnd-copy", "1081e37283d90000800003c07f3ef6bf", "6407b0e94181790501fd1e167b474872",
                  "08ffe1cb5fe6fc01f906f1c063814ccf"])
    yield Cursor("alias", (1, 1), [with_badge(badge(glyph(["..XXX", "...XX", "..X.X", ".X...", "X...."])))],
                 ["dnd-link", "link", "3085a0e285430894940527032f8b26df", "640fb0e74195791501fd1ed57b41487f",
                  "a2a266d0498c3104214a47bd64ab0fc8", "0876e1c15ff2fc01f906f1c363074c0f"])
    yield Cursor("context-menu", (1, 1),
                 [with_badge(badge(glyph(["XXXXX", ".....", "XXXXX", ".....", "XXX.."]), square=True))])
    yield Cursor("no-drop", (1, 1), [with_badge(badge(glyph(["....X", "...X.", "..X..", ".X...", "X...."]), c="r"))],
                 ["dnd_no_drop", "dnd-no-drop", "forbidden"])
    nope = disk(8, 8, 4.6, 6.9, "r").where(lambda x, y: abs(x + y - 16) <= 1 and 3 <= x <= 13, "r")
    yield Cursor("not-allowed", (8, 8), [nope], ["crossed_circle", "circle", "03b6e0fcb3499374a867c041f52298f0"])

    yield Cursor("pencil", (2, 14), [pencil()], ["draft"])
    yield Cursor("color-picker", (2, 14), [dropper()])
    yield Cursor("zoom-in", (6, 6), [lens(True)], ["zoom_in"])
    yield Cursor("zoom-out", (6, 6), [lens(False)], ["zoom_out"])
