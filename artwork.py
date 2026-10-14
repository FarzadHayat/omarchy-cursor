"""Cursor artwork for Omarchy Cursor.

Every shape is drawn on a 32x32 grid. A cursor is a list of parts; each part
is a union of fills and strokes that gets a solid rim around its silhouette,
a gradient body, and optional detail marks drawn in the rim color on top.
Colors are resolved later by build.py, so the artwork itself is theme free.
"""

import math

GRID = 32
RIM = 1.5  # rim thickness on each side of a silhouette, in grid units


# ── Primitives ────────────────────────────────────────────


class Fill:
    def __init__(self, d):
        self.d = d


class Line:
    def __init__(self, d, width, cap="round"):
        self.d = d
        self.width = width
        self.cap = cap


class Mark:
    """Detail drawn on top of a part body. color is a palette key or hex."""

    def __init__(self, d, width=None, color="rim", cap="round"):
        self.d = d
        self.width = width  # None means filled
        self.color = color
        self.cap = cap


class Part:
    def __init__(self, shapes, paint="body", marks=(), transform=None):
        self.shapes = shapes
        self.paint = paint
        self.marks = list(marks)
        self.transform = transform


class Cursor:
    def __init__(self, name, hotspot, frames, aliases=(), delay=0):
        self.name = name
        self.hotspot = hotspot
        self.frames = frames  # list of frames, each a list of parts
        self.aliases = list(aliases)
        self.delay = delay  # ms per frame for animated cursors


def _f(v):
    return f"{v:.3f}".rstrip("0").rstrip(".")


def _pt(p):
    return f"{_f(p[0])} {_f(p[1])}"


def poly(points, radius):
    """Closed polygon with every corner rounded by a quadratic curve."""
    n = len(points)
    radii = radius if isinstance(radius, (list, tuple)) else [radius] * n
    out = []
    for i in range(n):
        p0, p1, p2 = points[i - 1], points[i], points[(i + 1) % n]
        d1 = math.dist(p0, p1)
        d2 = math.dist(p1, p2)
        l1 = min(radii[i], d1 / 2)
        l2 = min(radii[i], d2 / 2)
        a = (p1[0] + (p0[0] - p1[0]) * l1 / d1, p1[1] + (p0[1] - p1[1]) * l1 / d1)
        b = (p1[0] + (p2[0] - p1[0]) * l2 / d2, p1[1] + (p2[1] - p1[1]) * l2 / d2)
        out.append(f"{'M' if i == 0 else 'L'} {_pt(a)} Q {_pt(p1)} {_pt(b)}")
    return " ".join(out) + " Z"


def rrect(x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    return (
        f"M {_f(x + r)} {_f(y)} H {_f(x + w - r)} "
        f"A {_f(r)} {_f(r)} 0 0 1 {_f(x + w)} {_f(y + r)} V {_f(y + h - r)} "
        f"A {_f(r)} {_f(r)} 0 0 1 {_f(x + w - r)} {_f(y + h)} H {_f(x + r)} "
        f"A {_f(r)} {_f(r)} 0 0 1 {_f(x)} {_f(y + h - r)} V {_f(y + r)} "
        f"A {_f(r)} {_f(r)} 0 0 1 {_f(x + r)} {_f(y)} Z"
    )


def circle(cx, cy, r):
    return (
        f"M {_f(cx - r)} {_f(cy)} A {_f(r)} {_f(r)} 0 1 0 {_f(cx + r)} {_f(cy)} "
        f"A {_f(r)} {_f(r)} 0 1 0 {_f(cx - r)} {_f(cy)} Z"
    )


def seg(*points):
    return "M " + " L ".join(_pt(p) for p in points)


def arc(cx, cy, r, a0, a1):
    """Clockwise arc between two angles in degrees (0 = 12 o'clock)."""
    def at(a):
        t = math.radians(a)
        return (cx + r * math.sin(t), cy - r * math.cos(t))

    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f"M {_pt(at(a0))} A {_f(r)} {_f(r)} 0 {large} 1 {_pt(at(a1))}"


def rotate_point(p, deg, c=(16, 16)):
    t = math.radians(deg)
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * math.cos(t) - y * math.sin(t), c[1] + x * math.sin(t) + y * math.cos(t))


def rot(deg, c=(16, 16)):
    return f"rotate({_f(deg)} {_f(c[0])} {_f(c[1])})"


MIRROR = f"matrix(-1 0 0 1 {GRID} 0)"


# ── Building blocks ───────────────────────────────────────

ARROW_TIP = (7.4, 4.9)


def arrow(transform=None):
    body = poly([(7, 3.6), (7.5, 25.4), (12.5, 19.6), (20.8, 19.4)], [1.5, 1.9, 1.3, 1.9])
    return Part([Fill(body)], transform=transform)


def badge(cx=23.2, cy=23.2, r=5.6, paint="body", marks=()):
    return Part([Fill(circle(cx, cy, r))], paint=paint, marks=marks)


def arrow_head(tip, direction, length=6.2, half=5.0):
    """Rounded triangular arrow head pointing along direction (degrees, 0 = up)."""
    t = math.radians(direction)
    ux, uy = math.sin(t), -math.cos(t)
    bx, by = tip[0] - ux * length, tip[1] - uy * length
    px, py = -uy, ux
    pts = [tip, (bx + px * half, by + py * half), (bx - px * half, by - py * half)]
    return Fill(poly(pts, [1.2, 1.3, 1.3]))


def spinner(cx, cy, r, width, t, track_marks=()):
    """Track ring plus a comet arc whose head leads; t in [0, 1)."""
    track = Part([Line(circle(cx, cy, r), width)], paint="track", marks=list(track_marks))
    # Arc length breathes while the head keeps turning, so motion never looks mechanical.
    ease = 0.5 - 0.5 * math.cos(2 * math.pi * t)
    length = 110 + 170 * ease
    head = 360 * t + 120 * ease
    steps = 40
    for i in range(steps):
        a0 = head - length + length * i / steps
        a1 = head - length + length * (i + 1) / steps + 0.6
        k = (i + 1) / steps
        track.marks.append(Mark(arc(cx, cy, r, a0, a1), width, color=("blend", k ** 1.6), cap="butt"))
    hx = cx + r * math.sin(math.radians(head))
    hy = cy - r * math.cos(math.radians(head))
    track.marks.append(Mark(circle(hx, hy, width / 2), color="head"))
    return track


# ── Cursors ───────────────────────────────────────────────


def pointers():
    yield Cursor("default", ARROW_TIP, [[arrow()]],
                 ["left_ptr", "arrow", "top_left_arrow", "wayland-cursor", "x-cursor"])
    yield Cursor("right_ptr", (GRID - ARROW_TIP[0], ARROW_TIP[1]), [[arrow(MIRROR)]],
                 ["draft_large", "draft_small", "right-arrow"])
    up = poly([(16, 3.6), (24.4, 24.8), (16, 19.4), (7.6, 24.8)], [1.5, 1.9, 1.3, 1.9])
    yield Cursor("center_ptr", (16, 4.9), [[Part([Fill(up)])]])


def hands():
    # Pointing hand: index finger raised, three folded fingers, thumb at the side.
    palm = poly([(9.6, 16.4), (25.6, 16.4), (25.6, 23.4), (22.4, 29), (12.4, 29), (9.6, 24)],
                [3, 3, 3.6, 2.4, 2.4, 3.6])
    pointing = Part(
        [
            Fill(rrect(12.2, 3.4, 4.6, 16, 2.3)),
            Fill(rrect(16.5, 11.6, 4.4, 9, 2.2)),
            Fill(rrect(20.6, 12.6, 4.2, 8.4, 2.1)),
            Fill(rrect(23.2, 14.4, 3.2, 7.2, 1.6)),
            Fill(palm),
            Line(seg((11.6, 23.4), (6.6, 17.2)), 4.2),
        ],
        marks=[
            Mark(seg((16.5, 14), (16.5, 17.6)), 0.95),
            Mark(seg((20.75, 15), (20.75, 18.2)), 0.95),
            Mark(seg((23.6, 16.6), (23.6, 19.2)), 0.95),
        ],
    )
    yield Cursor("pointer", (14.5, 4.4), [[pointing]],
                 ["hand2", "hand", "pointing_hand", "9d800788f1b08800ae810202380a0822",
                  "e29285e634086352946a0e7090d73106"])

    open_palm = poly([(9.2, 15), (24.2, 15), (24.2, 23), (21, 28.6), (12.6, 28.6), (9.2, 23.6)],
                     [3, 3, 3.6, 2.4, 2.4, 3.6])
    grab = Part(
        [
            Fill(rrect(9.6, 7.2, 3.9, 12, 1.95)),
            Fill(rrect(13.4, 4.8, 3.9, 14, 1.95)),
            Fill(rrect(17.2, 5.8, 3.9, 13, 1.95)),
            Fill(rrect(21, 8.8, 3.4, 10.5, 1.7)),
            Fill(open_palm),
            Line(seg((11.2, 22.4), (5.6, 15.6)), 3.9),
        ],
        marks=[
            Mark(seg((13.45, 11.6), (13.45, 16.4)), 0.95),
            Mark(seg((17.25, 10.4), (17.25, 16.4)), 0.95),
            Mark(seg((21.05, 12.2), (21.05, 16.6)), 0.95),
        ],
    )
    yield Cursor("grab", (16, 16), [[grab]],
                 ["openhand", "hand1", "5aca4d189052212118709018842178c0"])

    fist_palm = poly([(8.8, 14.6), (24.4, 14.6), (24.4, 22.4), (21.2, 27.8), (12, 27.8), (8.8, 22.6)],
                     [3, 3, 3.6, 2.4, 2.4, 3.6])
    fist = Part(
        [
            Fill(rrect(9.2, 10.4, 3.9, 7.2, 1.95)),
            Fill(rrect(13, 9.4, 3.9, 8.2, 1.95)),
            Fill(rrect(16.8, 9.8, 3.9, 7.8, 1.95)),
            Fill(rrect(20.6, 11, 3.8, 6.6, 1.9)),
            Fill(fist_palm),
            Line(seg((11.4, 23.4), (7.8, 19.4)), 3.8),
        ],
        marks=[
            Mark(seg((13.05, 13.2), (13.05, 16)), 0.95),
            Mark(seg((16.85, 12.6), (16.85, 16)), 0.95),
            Mark(seg((20.65, 13.4), (20.65, 16)), 0.95),
        ],
    )
    yield Cursor("grabbing", (16, 16), [[fist]],
                 ["closedhand", "dnd-move", "dnd-none", "fcf21c00b30f7e3f83fe0dfd12e71cff"])


def text():
    beam = (
        "M 11.5 5 C 14.4 5 16 6 16 8.6 V 23.4 C 16 26 14.4 27 11.5 27 "
        "M 20.5 5 C 17.6 5 16 6 16 8.6 M 16 23.4 C 16 26 17.6 27 20.5 27"
    )
    ibeam = Part([Line(beam, 2.1), Line(seg((13.8, 16), (18.2, 16)), 1.8)])
    yield Cursor("text", (16, 16), [[ibeam]], ["xterm", "ibeam"])
    vert = Part([Line(beam, 2.1), Line(seg((13.8, 16), (18.2, 16)), 1.8)], transform=rot(90))
    yield Cursor("vertical-text", (16, 16), [[vert]], ["048008013003cff3c00c801001200000"])


def precision():
    arms = [seg((16, 4), (16, 12.4)), seg((16, 19.6), (16, 28)),
            seg((4, 16), (12.4, 16)), seg((19.6, 16), (28, 16))]
    cross = Part([Line(d, 2.2) for d in arms] + [Fill(circle(16, 16, 1.7))])
    yield Cursor("crosshair", (16, 16), [[cross]], ["cross", "tcross", "cross_reverse", "diamond_cross"])

    plus = Part([Line(seg((16, 7.5), (16, 24.5)), 5), Line(seg((7.5, 16), (24.5, 16)), 5)])
    yield Cursor("cell", (16, 16), [[plus]], ["plus"])

    target = Part([Line(circle(16, 16, 8.4), 2.4), Fill(circle(16, 16, 2.4))])
    yield Cursor("dotbox", (16, 16), [[target]], ["target", "dot_box_mask", "draped_box", "icon"])

    x = Part([Line(seg((8.5, 8.5), (23.5, 23.5)), 4.4), Line(seg((23.5, 8.5), (8.5, 23.5)), 4.4)])
    yield Cursor("X_cursor", (16, 16), [[x]], ["pirate", "kill"])


def resizing():
    # Two headed arrows, drawn horizontally and rotated into place.
    def double(transform=None, span=1.0):
        a, b = 16 - 12.4 * span, 16 + 12.4 * span
        return Part(
            [Line(seg((a + 4, 16), (b - 4, 16)), 2.6),
             arrow_head((a, 16), 270), arrow_head((b, 16), 90)],
            transform=transform,
        )

    yield Cursor("ew-resize", (16, 16), [[double()]],
                 ["sb_h_double_arrow", "h_double_arrow", "size_hor", "left_right",
                  "14fef782d02440884392942c11205230", "028006030e0e7ebffc7f7070c0600140"])
    yield Cursor("ns-resize", (16, 16), [[double(rot(90))]],
                 ["sb_v_double_arrow", "v_double_arrow", "size_ver", "up_down",
                  "2870a09082c103050810ffdffffe0204", "00008160000006810000408080010102"])
    yield Cursor("nwse-resize", (16, 16), [[double(rot(45), 0.98)]],
                 ["bd_double_arrow", "size_fdiag", "c7088f0f3e6c8088236ef8e1e3e70000"])
    yield Cursor("nesw-resize", (16, 16), [[double(rot(-45), 0.98)]],
                 ["fd_double_arrow", "size_bdiag", "fcf1c3c7cd4491d801f1e1c78f100000"])

    # Single edge: an arrow pressing against a bar. Drawn pointing up.
    def edge(deg):
        return Part(
            [Line(seg((9, 4.6), (23, 4.6)), 2.4),
             arrow_head((16, 8.4), 0), Line(seg((16, 12), (16, 26.5)), 2.6)],
            transform=rot(deg),
        )

    for name, deg, aliases in [
        ("n-resize", 0, ["top_side", "sb_up_arrow", "up_arrow"]),
        ("e-resize", 90, ["right_side", "sb_right_arrow", "right_arrow"]),
        ("s-resize", 180, ["bottom_side", "sb_down_arrow", "down_arrow"]),
        ("w-resize", 270, ["left_side", "sb_left_arrow", "left_arrow"]),
    ]:
        yield Cursor(name, (16, 16), [[edge(deg)]], aliases)

    # Corner: an arrow pressing into an L bracket. Drawn for the top left corner.
    def corner(deg):
        return Part(
            [Line(seg((5, 13.6), (5, 5), (13.6, 5)), 2.4),
             arrow_head((8.8, 8.8), 315, 6, 4.8), Line(seg((11.6, 11.6), (24.6, 24.6)), 2.6)],
            transform=rot(deg),
        )

    for name, deg, aliases in [
        ("nw-resize", 0, ["top_left_corner", "ul_angle"]),
        ("ne-resize", 90, ["top_right_corner", "ur_angle"]),
        ("se-resize", 180, ["bottom_right_corner", "lr_angle"]),
        ("sw-resize", 270, ["bottom_left_corner", "ll_angle"]),
    ]:
        yield Cursor(name, (16, 16), [[corner(deg)]], aliases)

    def split(transform=None):
        return Part(
            [Line(seg((13.6, 8.5), (13.6, 23.5)), 2.2), Line(seg((18.4, 8.5), (18.4, 23.5)), 2.2),
             arrow_head((3.6, 16), 270, 5.6, 4.6), Line(seg((7, 16), (12, 16)), 2.6),
             arrow_head((28.4, 16), 90, 5.6, 4.6), Line(seg((20, 16), (25, 16)), 2.6)],
            transform=transform,
        )

    yield Cursor("col-resize", (16, 16), [[split()]], ["split_h", "sb_h_double_arrow_col"])
    yield Cursor("row-resize", (16, 16), [[split(rot(90))]], ["split_v"])

    move = Part(
        [Line(seg((16, 8), (16, 24)), 2.6), Line(seg((8, 16), (24, 16)), 2.6),
         arrow_head((16, 3.2), 0, 5.6, 4.6), arrow_head((28.8, 16), 90, 5.6, 4.6),
         arrow_head((16, 28.8), 180, 5.6, 4.6), arrow_head((3.2, 16), 270, 5.6, 4.6),
         Fill(circle(16, 16, 2.8))],
    )
    yield Cursor("move", (16, 16), [[move]],
                 ["fleur", "all-scroll", "size_all", "4498f0e0c1937ffe01fd06f973665830",
                  "9081237383d90e509aa00f00170e968f"])


def busy(frames=48, delay=22):
    wait = [[spinner(16, 16, 9.2, 4.2, i / frames)] for i in range(frames)]
    yield Cursor("wait", (16, 16), wait, ["watch", "clock"], delay)

    progress = [[arrow(), spinner(23.4, 23.4, 4.6, 2.6, i / frames)] for i in range(frames)]
    yield Cursor("progress", ARROW_TIP, progress,
                 ["left_ptr_watch", "half-busy", "00000000000000020006000e7e9ffc3f",
                  "08e8e1c95fe2fc01f976f1e063a24ccd", "3ecb610c1bf2410f44200f48c40d3599"], delay)


def with_badges():
    question = badge(marks=[
        Mark("M 21.2 21.7 C 21.2 20.4 22.1 19.7 23.2 19.7 C 24.4 19.7 25.2 20.5 25.2 21.5 "
             "C 25.2 22.9 23.3 22.9 23.3 24.5", 1.55),
        Mark(circle(23.3, 26.7, 0.95)),
    ])
    yield Cursor("help", ARROW_TIP, [[arrow(), question]],
                 ["question_arrow", "whats_this", "left_ptr_help", "dnd-ask",
                  "d9ce0ab605698f320427677b458ad60b", "5c6cd98b3f3ebcb1f9c7f1c204630408"])

    plus = badge(marks=[Mark(seg((23.2, 20.6), (23.2, 25.8)), 1.6), Mark(seg((20.6, 23.2), (25.8, 23.2)), 1.6)])
    yield Cursor("copy", ARROW_TIP, [[arrow(), plus]],
                 ["dnd-copy", "1081e37283d90000800003c07f3ef6bf", "6407b0e94181790501fd1e167b474872",
                  "08ffe1cb5fe6fc01f906f1c063814ccf"])

    link = badge(marks=[
        Mark("M 20.8 25.8 V 24.4 C 20.8 22.6 21.8 21.7 23.6 21.7 H 24.6", 1.55),
        Mark(poly([(26.4, 21.7), (24, 19.5), (24, 23.9)], 0.45)),
    ])
    yield Cursor("alias", ARROW_TIP, [[arrow(), link]],
                 ["dnd-link", "link", "3085a0e285430894940527032f8b26df", "640fb0e74195791501fd1ed57b41487f",
                  "a2a266d0498c3104214a47bd64ab0fc8", "0876e1c15ff2fc01f906f1c363074c0f"])

    menu = Part([Fill(rrect(17.6, 17.4, 11.2, 11.4, 2.6))], marks=[
        Mark(seg((20.4, 20.9), (26, 20.9)), 1.3),
        Mark(seg((20.4, 23.1), (26, 23.1)), 1.3),
        Mark(seg((20.4, 25.3), (24.2, 25.3)), 1.3),
    ])
    yield Cursor("context-menu", ARROW_TIP, [[arrow(), menu]])

    nope = badge(paint="danger", marks=[
        Mark(circle(23.2, 23.2, 3.1), 1.4),
        Mark(seg((21, 25.4), (25.4, 21)), 1.4),
    ])
    yield Cursor("no-drop", ARROW_TIP, [[arrow(), nope]],
                 ["dnd_no_drop", "dnd-no-drop", "forbidden"])

    ring = Part([Line(circle(16, 16, 9.6), 3.6), Line(seg((9.2, 22.8), (22.8, 9.2)), 3.6)], paint="danger")
    yield Cursor("not-allowed", (16, 16), [[ring]],
                 ["crossed_circle", "circle", "03b6e0fcb3499374a867c041f52298f0"])


def tools():
    # Pencil drawn upright with its tip at the bottom, then tilted 45 degrees.
    tilt = 45
    pencil = Part(
        [Fill(rrect(12.6, 3.4, 6.8, 18.6, 1.9)),
         Fill(poly([(12.6, 21), (19.4, 21), (16, 28.6)], [0.6, 0.6, 0.9]))],
        marks=[Mark(seg((12.6, 7.6), (19.4, 7.6)), 1.1),
               Mark(seg((12.6, 21.4), (19.4, 21.4)), 1.1),
               Mark(poly([(14.5, 25.2), (17.5, 25.2), (16, 28.6)], 0.4))],
        transform=rot(tilt),
    )
    yield Cursor("pencil", rotate_point((16, 28.2), tilt), [[pencil]], ["draft"])

    dropper = Part(
        [Fill(rrect(13, 3, 6, 9.4, 3)), Fill(rrect(11, 11.2, 10, 3, 1.4)),
         Fill(rrect(14, 13.6, 4, 11.6, 1.2)), Line(seg((16, 24.6), (16, 28.4)), 1.7)],
        marks=[Mark(seg((15.9, 17.4), (15.9, 23.2)), 1.1, color="hi")],
        transform=rot(tilt),
    )
    yield Cursor("color-picker", rotate_point((16, 28.6), tilt), [[dropper]])

    for name, aliases, plus in [("zoom-in", ["zoom_in"], True), ("zoom-out", ["zoom_out"], False)]:
        glyph = [Mark(seg((10.2, 13.2), (16.2, 13.2)), 2)]
        if plus:
            glyph.append(Mark(seg((13.2, 10.2), (13.2, 16.2)), 2))
        lens = Part([Fill(circle(13.2, 13.2, 9)), Line(seg((19.6, 19.6), (26.6, 26.6)), 4.4)],
                    marks=glyph)
        yield Cursor(name, (13.2, 13.2), [[lens]], aliases)


def all_cursors():
    for group in (pointers, hands, text, precision, resizing, busy, with_badges, tools):
        yield from group()
