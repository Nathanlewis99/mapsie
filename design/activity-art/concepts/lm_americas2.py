"""Mapsie Originals: famous landmarks of the Americas, part two."""
from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group, balloon
import math


# ================================================================ private helpers
def poly(*pts, close=True) -> str:
    s = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    return s + ("Z" if close else "")


def smooth(pts, close=False) -> str:
    """A smooth curve through the points (Catmull-Rom as cubic Beziers)."""
    s = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    n = len(pts)
    for i in range(n - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < n else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        s += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return s + ("Z" if close else "")


def pine(x: float, base: float, h: float, w: float | None = None) -> str:
    """A three-tier pine tree, base centred on (x, base)."""
    w = w or h * 0.55
    t = base - h
    return (f"M{x} {t} L{x + w*0.32} {t + h*0.32} L{x + w*0.2} {t + h*0.32} L{x + w*0.42} {t + h*0.62} "
            f"L{x + w*0.28} {t + h*0.62} L{x + w*0.5} {base - h*0.12} L{x - w*0.5} {base - h*0.12} "
            f"L{x - w*0.28} {t + h*0.62} L{x - w*0.42} {t + h*0.62} L{x - w*0.2} {t + h*0.32} L{x - w*0.32} {t + h*0.32}Z")


def birds(d: Drawing, pts, role="dark"):
    s = " ".join(f"M{x} {y} q{3 * k} {-3 * k} {6 * k} 0 q{3 * k} {-3 * k} {6 * k} 0" for x, y, k in pts)
    d.stroke(role, s, 1.7)


def palm(d: Drawing, x, base, h, lean=0, role="dark"):
    tx, ty = x + lean, base - h
    d.limb(role, f"M{x} {base} Q{x + lean * 0.2} {base - h * 0.5} {tx} {ty}", 3.2)
    for ang, ln in [(-160, 20), (-120, 17), (-60, 17), (-20, 20), (20, 15), (160, 15)]:
        a = math.radians(ang)
        ex, ey = tx + ln * math.cos(a), ty + ln * math.sin(a) + 6
        mx, my = tx + ln * 0.5 * math.cos(a), ty + ln * 0.5 * math.sin(a) - 4
        d.shape(role, f"M{tx} {ty} Q{mx:.1f} {my - 3:.1f} {ex:.1f} {ey:.1f} Q{mx:.1f} {my + 3:.1f} {tx} {ty}Z", shadow=False)


def canopy(x0, x1, y, r, bottom) -> str:
    """A jungle edge: a row of round treetops from x0 to x1 along y, filled down to `bottom`."""
    n = max(1, round((x1 - x0) / (r * 1.6)))
    step = (x1 - x0) / n
    s = f"M{x0:g} {bottom:g} V{y:g}"
    for i in range(n):
        s += f" A{r * .9:g} {r:g} 0 0 1 {x0 + (i + 1) * step:.1f} {y + (2 if i % 2 else -1):g}"
    return s + f" V{bottom:g}Z"


def mirror_y(d: Drawing, y0: float, fn, opacity=".55"):
    """Draw fn() reflected about the horizontal line y = y0 (water mirror)."""
    d.raw(f'<g opacity="{opacity}" transform="translate(0 {2 * y0}) scale(1 -1)">',
          f'<g opacity="{opacity}" transform="translate(0 {2 * y0}) scale(1 -1)">')
    fn()
    d.raw("</g>", "</g>")


# a natural daytime blue, for white monuments that would vanish into a pale sky
BLUE_SKY = "#8DB8D6"


# ================================================================ TIKAL
TIKAL = {"stone": "#BFB49D", "stone2": "#958A74", "stone3": "#655C4C", "jungle": "#4E8A4A", "jungle2": "#36683A", "jungle3": "#5F9E55"}


def maya_temple(d: Drawing, x, base, s=1.0, st="stone", st2="stone2", st3="stone3"):
    """Tikal's Temple I: nine steep tiers, a sanctuary and a tall roof comb."""
    def draw():
        n, h = 9, 8.4
        for i in range(n):
            y0, y1 = -i * h, -(i + 1) * h
            w0 = 74 - i * 4.4
            w1 = w0 - 2.6
            d.shape(st, poly((-w0 / 2, y0), (-w1 / 2, y1 + 2), (-w1 / 2, y1), (w1 / 2, y1), (w1 / 2, y1 + 2), (w0 / 2, y0)))
            d.shape(st2, poly((w1 / 2 - 7, y1), (w1 / 2, y1), (w1 / 2, y1 + 2), (w0 / 2, y0), (w0 / 2 - 7, y0)), shadow=False, line=False)
        top = -n * h
        d.shape(st2, poly((-7, 0), (-5, top), (5, top), (7, 0)))
        d.stroke(st3, " ".join(f"M{-6.6 + i * 0.22:.1f} {-4 - i * 5.4:.1f} H{6.6 - i * 0.22:.1f}" for i in range(14)), 1.2, line=False)
        d.shape(st, rrect(-14, top - 15, 28, 15, 1))
        d.shape(st2, poly((6, top - 15), (14, top - 15), (14, top), (6, top)), shadow=False, line=False)
        d.marks("stone3", rrect(-3.5, top - 11, 7, 11, 1))
        d.shape(st2, rrect(-15.5, top - 19, 31, 5, 1))
        d.shape(st, poly((-11, top - 19), (-9, top - 46), (9, top - 46), (11, top - 19)))
        d.shape(st2, poly((3, top - 46), (9, top - 46), (11, top - 19), (4, top - 19)), shadow=False, line=False)
        d.marks(st3, rrect(-6, top - 40, 4, 6, 1) + " " + rrect(2, top - 40, 4, 6, 1) + " " + rrect(-3, top - 30, 6, 5, 1))
    group(d, f"translate({x} {base}) scale({s})", draw)


def tikal(d: Drawing):
    d.disc("glow", 100, 86, 46)
    birds(d, [(146, 44, 1), (160, 36, .8)])
    # Temple II, further off in the haze
    maya_temple(d, 30, 150, 0.6, st="stone2", st2="stone3", st3="stone3")
    d.shape("light", "M-30 136 Q20 122 60 132 Q100 124 140 132 Q180 122 230 134 V148 H-30Z", shadow=False, line=False)
    maya_temple(d, 104, 156, 1.08)
    d.shape("jungle3", canopy(-30, 60, 136, 10, 210))
    d.shape("jungle3", canopy(150, 230, 134, 10, 210))
    d.shape("jungle", canopy(-30, 230, 150, 11, 210))
    d.shape("jungle2", canopy(-30, 230, 170, 13, 210), line=False)


# ================================================================ TEOTIHUACAN
TEO = {"stone": "#BC9F7E", "stone2": "#957A5E", "stone3": "#6A5542", "hill": "#6F7F5C", "dry": "#E0C592", "dry2": "#C9A574", "ledge": "#DCC6A6", "nopal": "#5E8C4E", "nopal2": "#E4572E"}


def teotihuacan(d: Drawing):
    d.disc("glow", 150, 70, 18)
    # Cerro Gordo behind
    d.band("hill", "M-30 132 Q10 112 50 108 Q90 90 130 100 Q170 104 230 126")
    d.band("dry", "M-30 158 Q100 152 230 158")
    # Pyramid of the Sun: four sloping bodies on terraces, a flat top
    tiers = [(166, 140, 140, 124), (138, 116, 108, 92), (114, 98, 82, 70), (96, 84, 60, 50)]
    for yb, yt, wb, wt in tiers:
        d.shape("stone", poly((100 - wb / 2, yb), (100 - wt / 2, yt), (100 + wt / 2, yt), (100 + wb / 2, yb)))
        d.shape("stone2", poly((100 + wt / 2 - 12, yt), (100 + wt / 2, yt), (100 + wb / 2, yb), (100 + wb / 2 - 14, yb)), shadow=False, line=False)
        d.stroke("stone3", " ".join(f"M{100 - wb / 2 + 4 + k * (wb - wt) / 8:.1f} {yb - 4 - k * (yb - yt) / 4:.1f} H{100 + wb / 2 - 4 - k * (wb - wt) / 8:.1f}"
                                    for k in range(3)), 0.9, line=False)
        d.shape("ledge", rrect(100 - wt / 2 - 1, yt - 2, wt + 2, 3, 1), shadow=False, line=False)
    d.shape("stone2", poly((91, 166), (95, 84), (105, 84), (109, 166)))
    d.stroke("stone3", " ".join(f"M{91.5 + i * .27:.1f} {162 - i * 5:.1f} H{108.5 - i * .27:.1f}" for i in range(16)), 1.1, line=False)
    d.shape("ledge", " ".join(rrect(92 + k, y, 16 - 2 * k, 3, 1) for k, y in [(0, 138), (1, 114), (2, 96)]), shadow=False, line=False)
    # Avenue of the Dead running towards us, platforms along it
    d.shape("dry2", "M84 168 H116 L136 210 H64Z", spot=True)
    d.shape("stone", poly((26, 186), (32, 174), (52, 174), (56, 186)) + " " + poly((144, 186), (148, 174), (168, 174), (174, 186)))
    d.shape("stone2", poly((44, 174), (52, 174), (56, 186), (46, 186)) + " " + poly((160, 174), (168, 174), (174, 186), (164, 186)), shadow=False, line=False)
    def nopal():
        d.shape("nopal", ellipse(0, -8, 7, 10))
        d.shape("nopal", ellipse(-8, -22, 5.5, 8), extra='transform="rotate(-25 -8 -22)"')
        d.shape("nopal", ellipse(7, -24, 5, 7.5), extra='transform="rotate(20 7 -24)"')
        d.marks("nopal2", circle(-10, -30, 2) + " " + circle(9, -31, 2))
    group(d, "translate(18 172) scale(.9)", nopal)
    group(d, "translate(186 170) scale(.8)", nopal)
    group(d, "translate(26 22) scale(.3)", lambda: balloon(d))
    group(d, "translate(140 30) scale(.22)", lambda: balloon(d, body="pop", stripes="light", centre="hero2"))

# ================================================================ GATEWAY ARCH
ARCH = {"steel": "#B4BCC7", "steel2": "#808A98", "steel3": "#E9EDF1", "court": "#D9CBB2", "dome": "#6F9187"}


def catenary(W, H, top, cx=100, n=31):
    """Points on a catenary of half-width W and height H, apex at (cx, top)."""
    lo, hi = 0.5, 5000.0
    for _ in range(80):
        a = (lo + hi) / 2
        if a * (math.cosh(W / a) - 1) > H:
            lo = a
        else:
            hi = a
    return [(cx + x, top + a * (math.cosh(x / a) - 1)) for x in [-W + 2 * W * i / (n - 1) for i in range(n)]]


def gateway_arch(d: Drawing):
    d.disc("glow", 100, 116, 24)
    birds(d, [(140, 40, 1), (152, 32, .8)])
    d.shape("far", "M-30 200 V150 H4 V126 H18 V138 H28 V112 H42 V150 H158 V120 H170 V104 H182 V130 H194 V116 H206 V150 H230 V200Z")
    # the Old Courthouse, framed by the arch
    d.shape("court", rrect(76, 138, 48, 16, 1))
    d.shape("court", rrect(91, 126, 18, 13, 1))
    d.shape("dome", "M91 127 Q91 112 100 110 Q109 112 109 127Z")
    d.stroke("dome", "M100 110 V104", 1.8)
    d.band("mid", "M-30 152 Q100 146 230 152")
    outer = catenary(64, 130, 34)
    inner = catenary(50, 123, 42)
    d.shape("steel", poly(*outer, *reversed(inner)), spot=True)
    d.shape("steel2", poly(*[p for p in outer if p[0] >= 99.9], *reversed([p for p in inner if p[0] >= 99.9])), shadow=False, line=False)
    mid = [((o[0] + i[0]) / 2 - 2, (o[1] + i[1]) / 2) for o, i in zip(outer, inner)][2:13]
    d.stroke("steel3", smooth(mid), 2, line=False)
    d.band("near", waves(166, 3, 24))
    d.stroke("light", "M40 176 h18 M130 174 h24", 2)
    d.band("deep", waves(184, 3, 30), line=False)


# ================================================================ LINCOLN MEMORIAL
MARBLE = {"marble": "#EEE9E0", "marble2": "#CFC6B6", "marble3": "#A99F8E", "hall": "#6F6963", "pool": "#7DB3CF", "pool2": "#C4E2EF"}
COLS = [33, 46, 59, 72, 85, 115, 128, 141, 154, 167]


def lincoln_building(d: Drawing, reflect=False):
    d.shape("marble2", rrect(20, 132, 160, 10, 1))
    d.shape("marble", rrect(25, 125, 150, 8, 1))
    d.shape("hall", rrect(30, 72, 140, 54, 0))
    if not reflect:
        # the seated statue in the hall
        d.shape("marble", rrect(90, 114, 20, 11, 1))
        d.shape("marble2", rrect(88, 94, 24, 21, 3))
        d.shape("marble", "M94 112 V98 Q94 95 100 95 Q106 95 106 98 V112Z", shadow=False)
        d.shape("marble", circle(100, 91, 3.6), shadow=False)
        d.shape("marble", rrect(93, 106, 14, 5, 1), shadow=False)
    for x in COLS:
        d.shape("marble", rrect(x - 3.6, 72, 7.2, 53, 1))
        d.stroke("marble2", f"M{x - 1.2} 76 V122 M{x + 1.2} 76 V122", 0.8, line=False)
    d.shape("marble", rrect(24, 60, 152, 13, 1))
    d.stroke("marble2", "M26 66 H174", 1.2, line=False)
    d.shape("marble", rrect(32, 45, 136, 15, 1))
    d.shape("marble2", rrect(36, 40, 128, 6, 1))
    d.marks("marble3", " ".join(rrect(x - 3, 48, 6, 6, 3) for x in range(46, 160, 14)))


def lincoln(d: Drawing):
    for x, y, r in [(4, 112, 22), (22, 126, 14), (196, 112, 22), (178, 126, 14)]:
        d.shape("near", circle(x, y, r))
    d.band("mid", "M-30 140 H230")
    lincoln_building(d)
    d.band("pool", "M-30 150 H230", line=False)
    if d.paper:
        d.raw('<g opacity=".35" transform="translate(0 296) scale(1 -1)">'
              + "".join(f'<rect x="{x - 3.6}" y="72" width="7.2" height="53" fill="{d.c["pool2"]}"/>' for x in COLS)
              + f'<rect x="24" y="60" width="152" height="13" fill="{d.c["pool2"]}"/></g>')
    else:
        d.stroke("dark", "M-30 150 H230", 2.6)
        d.stroke("dark", " ".join(f"M{x} 156 V{166 + (i % 3) * 4}" for i, x in enumerate(COLS)), 1.4)
    d.stroke("pool2", "M20 182 h30 M120 186 h40", 2)
    d.band("mid", "M-30 190 H230", line=False)


# ================================================================ WASHINGTON MONUMENT
OBELISK = {"marble": "#F2EDE4", "marble2": "#D2C9BA", "blossom": "#F7BCCD", "blossom2": "#E98EAB", "bark": "#5B4038",
           "basin": "#6FA9C9", "basin2": "#BFE0EE", "flag": "#D2423A"}


def blossom_tree(d: Drawing, x, base, flip=1):
    def draw():
        d.limb("bark", "M0 0 Q4 -24 -6 -44 M2 -22 Q14 -34 26 -40 M-2 -30 Q-16 -40 -26 -42", 4)
        for cx, cy, r in [(-22, -46, 13), (-6, -56, 15), (14, -50, 14), (28, -40, 11), (-30, -32, 10), (4, -38, 10)]:
            d.shape("blossom", circle(cx, cy, r), spot=True)
        d.marks("blossom2", " ".join(circle(cx, cy, 2) for cx, cy in [(-18, -50), (-8, -62), (8, -54), (20, -46), (-26, -36), (2, -44), (26, -36), (-12, -44)]))
    group(d, f"translate({x} {base}) scale({flip} 1)", draw)


def washington(d: Drawing):
    d.band("near", "M-30 152 Q40 144 100 148 Q160 144 230 150")
    # the obelisk, with its colour change a third of the way up
    d.shape("marble", poly((90, 166), (93.6, 46), (106.4, 46), (110, 166)))
    d.shape("marble", poly((93.6, 46.5), (100, 28), (106.4, 46.5)), shadow=False)
    d.shape("marble2", poly((100, 28), (106.4, 46), (110, 166), (102.5, 166), (100.8, 46)), shadow=False, line=False)
    d.stroke("marble2", "M91.8 124 H108.2", 1.2, line=False)
    d.marks("dark", rrect(97.5, 50, 2, 3, .5) + " " + rrect(100.5, 50, 2, 3, .5))
    # ring of flags
    d.band("mid", "M-30 166 Q100 158 230 166")
    poles = list(range(60, 142, 8))
    d.stroke("dark", " ".join(f"M{x} {165 - abs(x - 100) * 0.06:.1f} V{152 - abs(x - 100) * 0.06:.1f}" for x in poles), 1)
    for x in poles:
        y = 152 - abs(x - 100) * 0.06
        d.marks("flag", f"M{x} {y} h5 v3.4 h-5Z")
    d.band("basin", "M-30 174 Q100 168 230 174")
    d.stroke("basin2", "M70 182 h20 M112 184 h18", 1.8)
    blossom_tree(d, 22, 196, 1)
    blossom_tree(d, 178, 196, -1)


# ================================================================ BROOKLYN BRIDGE
BKLYN = {"stone": "#CDB79A", "stone2": "#A68E70", "stone3": "#7A6650", "cable": "#454A54", "deck": "#6A6560"}


def bez_y(p0, p1, p2, x):
    """y on a quadratic Bezier (monotonic in x) at x."""
    lo, hi = 0.0, 1.0
    for _ in range(40):
        t = (lo + hi) / 2
        bx = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        if (bx - x) * (p2[0] - p0[0]) < 0:
            lo = t
        else:
            hi = t
    return (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]


def brooklyn(d: Drawing):
    d.disc("glow", 40, 70, 16)
    # lower Manhattan with One World Trade
    d.shape("far", "M120 200 V120 H130 V106 H140 V124 H150 V96 H158 V120 H162 V70 L168 60 V40 L170 60 L176 70 V120 H184 V102 H196 V116 H206 V96 H214 V126 H230 V200Z")
    d.band("mid", waves(150, 3, 22))
    deck = 120
    for side in (-1, 1):
        x0 = 100 + side * 36
        p0, p1, p2 = (x0, 36), (100 + side * 86, 106), (100 + side * 134, 116)
        hang = " ".join(f"M{x} {bez_y(p0, p1, p2, x):.1f} V{deck}" for x in range(int(x0 + side * 6), int(100 + side * 130), side * 6))
        d.stroke("cable", hang, 0.9, line=False)
        stays = " ".join(f"M{x0 - side * 1} 42 L{x0 + side * k} {deck}" for k in range(10, 120, 14))
        d.stroke("cable", stays, 1.0)
        d.stroke("cable", f"M{p0[0]} {p0[1]} Q{p1[0]} {p1[1]} {p2[0]} {p2[1]}", 2.6)
    d.shape("deck", rrect(-30, deck, 260, 8, 0))
    d.stroke("stone3", f"M-30 {deck + 3} H230", 1, line=False)
    # the tower: granite with two pointed gothic arches
    body = poly((62, 178), (64, 40), (136, 40), (138, 178))
    holes = ("M72 128 V76 C72 66 76 60 81 52 C86 60 90 66 90 76 V128Z "
             "M110 128 V76 C110 66 114 60 119 52 C124 60 128 66 128 76 V128Z")
    d.shape("stone", body + " " + holes, spot=True, extra='fill-rule="evenodd"')
    d.shape("stone2", poly((128, 40), (136, 40), (138, 178), (128, 178)) + " " + poly((100, 40), (110, 40), (110, 178), (100, 178)) +
            " " + poly((64, 40), (72, 40), (72, 178), (63.4, 178)), shadow=False, line=False, extra='opacity=".55"')
    d.stroke("stone3", holes, 1.4, line=False)
    d.stroke("stone2", "M64 96 H72 M90 96 H110 M128 96 H136 M64 140 H137 M64 156 H137", 1.2, line=False)
    d.shape("stone", rrect(58, 32, 84, 9, 1))
    d.shape("stone2", rrect(60, 27, 80, 6, 1))
    d.shape("stone3", rrect(58, 128, 84, 5, 1), shadow=False)
    d.band("near", waves(168, 3, 26))
    d.band("deep", waves(184, 3, 30), line=False)


# ================================================================ ALCATRAZ
ALCA = {"rock": "#8C7C68", "rock2": "#6A5C4D", "scrub": "#6E8E58", "cell": "#ECE5D4", "cell2": "#BDB29C", "gg": "#C0362C"}


def alcatraz(d: Drawing):
    d.disc("glow", 150, 56, 16)
    # Marin headlands and a glimpse of the Golden Gate
    d.band("far", "M-30 108 Q0 92 30 98 Q50 88 80 104 L230 108")
    d.stroke("gg", "M14 70 V104 M30 70 V104 M-30 96 Q-6 72 14 72 Q22 94 30 72 Q50 84 70 98", 1.6, line=False)
    d.stroke("gg", "M-30 96 H80", 1.8, line=False)
    d.shape("light", cloud(150, 92, 1.0), shadow=False)
    d.band("mid", waves(112, 2.5, 22))
    # the island
    d.shape("rock", "M18 146 Q26 130 42 126 L54 114 Q66 106 86 108 L140 106 Q158 106 166 116 L178 128 Q188 136 190 146Z")
    d.shape("rock2", "M18 146 Q26 136 44 134 Q100 130 160 134 Q182 136 190 146Z", shadow=False, line=False)
    d.shape("scrub", "M46 120 Q60 110 86 112 L140 110 Q156 110 164 118 Q140 122 100 120 Q70 122 46 120Z", shadow=False)
    # cellhouse
    d.shape("cell", rrect(64, 88, 78, 26, 1), spot=True)
    d.shape("cell2", rrect(62, 84, 82, 6, 1))
    d.shape("cell2", poly((126, 90), (142, 90), (142, 114), (126, 114)), shadow=False, line=False)
    d.marks("dark", " ".join(rrect(x, 95, 3, 12, 1) for x in range(70, 138, 7)))
    # warden's house and staff buildings below
    d.shape("cell2", rrect(40, 116, 18, 10, 1))
    d.shape("cell", rrect(146, 118, 20, 10, 1))
    # lighthouse
    d.shape("cell", poly((49, 116), (51, 70), (57, 70), (59, 116)))
    d.shape("dark", rrect(50, 62, 8, 9, 1))
    d.shape("glow", rrect(51.5, 64, 5, 5, 1), shadow=False)
    d.shape("dark", poly((49, 63), (54, 56), (59, 63)))
    # water tower
    d.stroke("dark", "M148 116 L151 94 M162 116 L159 94 M149 108 H161 M150 100 H160", 1.4)
    d.shape("cell2", rrect(145, 82, 20, 13, 1.5))
    d.shape("cell2", poly((145, 83), (155, 76), (165, 83)), shadow=False)
    d.band("near", waves(150, 3, 26))
    def sailboat():
        d.shape("light", "M0 0 L0 -26 L16 -2Z")
        d.shape("light", "M-2 -2 L-2 -20 L-12 -2Z", shadow=False)
        d.shape("pop", "M-14 0 H20 L16 6 H-10Z", spot=True)
    group(d, "translate(150 170) scale(.9)", sailboat)
    d.band("deep", waves(180, 3, 30), line=False)
    birds(d, [(96, 46, .9), (110, 40, .7)])


# ================================================================ OLD FAITHFUL
GEYSER = {"steam": "#FFFFFF", "steam2": "#D3E1E8", "sinter": "#DCD5C4", "sinter2": "#B9AE96", "rust": "#D38E4A",
          "pine": "#355E45", "bison": "#4A3528", "board": "#9A7A58"}
PLUME = ("M95 152 C94 132 92 114 90 98 C80 96 74 86 79 78 C68 74 66 62 74 56 C68 44 78 32 90 36 C94 24 110 22 116 32 "
         "C128 28 138 40 132 50 C142 56 140 70 130 72 C134 84 122 92 112 88 C110 106 108 128 106 152Z")


def old_faithful(d: Drawing):
    d.band("mid", "M-30 132 Q20 118 60 124 Q110 114 150 122 Q190 114 230 128")
    for x, h in [(-4, 40), (12, 52), (28, 38), (44, 30), (156, 32), (172, 46), (188, 54), (204, 40)]:
        d.shape("pine", pine(x, 150, h))
    d.band("near", "M-30 146 Q60 140 100 144 Q150 140 230 148", line=False)
    # the eruption
    d.shape("steam", PLUME, spot=True)
    d.shape("steam2", "M106 152 C108 128 110 106 112 88 C122 92 134 84 130 72 C140 70 142 56 132 50 C136 60 128 66 120 66 "
                      "C124 76 116 82 108 80 C104 104 102 128 100 152Z", shadow=False, line=False)
    d.stroke("steam2", "M86 46 Q92 42 98 46 M80 64 Q86 60 92 64 M104 40 Q110 36 116 40", 1.6, line=False)
    for x, y, r in [(84, 140, 2.2), (116, 136, 2.4), (80, 126, 1.6), (120, 120, 1.8), (88, 112, 1.4)]:
        d.shape("steam", circle(x, y, r), shadow=False)
    # sinter cone
    d.shape("sinter", "M28 172 Q56 152 86 150 Q100 147 114 150 Q144 152 172 172Z")
    d.shape("rust", "M60 160 Q80 152 92 152 Q84 158 86 166 Q72 162 60 160Z M140 160 Q122 152 108 152 Q116 158 114 166 Q128 162 140 160Z", shadow=False)
    d.shape("sinter2", ellipse(100, 151, 9, 2.6), shadow=False)
    d.band("sinter2", "M-30 170 Q100 164 230 170")
    # boardwalk
    d.shape("board", "M-30 180 Q100 172 230 180 V186 Q100 178 -30 186Z")
    d.stroke("board", " ".join(f"M{x} {178 - (1 - ((x - 100) / 130) ** 2) * 6:.1f} v10" for x in range(-20, 230, 18)), 1.6)
    # bison
    def bison():
        d.shape("bison", "M2 -2 C-2 -8 0 -14 6 -17 C9 -25 18 -28 27 -25 C35 -23 41 -19 45 -15 C49 -13 51 -8 50 -2 L49 7 L46 7 "
                         "L45 1 L41 2 L41 9 L38 9 L37 2 L19 2 L18 9 L15 9 L14 2 C11 2 9 7 4 7 C0 7 -1 3 2 -2Z", spot=True)
        d.stroke("bison", "M50 -6 Q55 -2 54 4", 1.4)
        d.stroke("light", "M4 -15 Q2 -19 5 -21", 1.2)
    group(d, "translate(140 162) scale(.62)", bison)


# ================================================================ DELICATE ARCH
SLICKROCK = {"arch": "#D9783F", "arch2": "#A9532C", "slick": "#E7A56B", "slick2": "#C98250", "mtn": "#8F8DB2", "snow": "#FFFFFF"}


def delicate_arch(d: Drawing):
    d.disc("glow", 156, 60, 15)
    # La Sal mountains, snow-capped, seen through the arch
    d.band("mtn", "M-30 130 L6 116 L24 120 L46 98 L60 108 L80 92 L98 106 L118 96 L136 110 L158 102 L180 116 L230 122")
    d.shape("snow", "M46 98 L52 103 L48 103 L44 106 L41 102Z M80 92 L87 98 L82 97 L78 101 L74 97Z M118 96 L124 101 L120 100 L116 103 L113 100Z "
                    "M158 102 L163 106 L159 106 L155 108 L153 105Z", shadow=False)
    # the slickrock bowl
    d.band("slick", "M-30 158 Q30 146 80 154 Q130 162 230 148")
    d.shape("slick2", "M-30 178 Q40 162 100 174 Q150 182 230 170 V200 H-30Z")
    d.stroke("arch2", "M10 172 Q50 164 90 174 M120 182 Q170 178 210 174", 1.6, line=False)
    # the arch: a free-standing loop of sandstone, the left leg pinched near its foot
    outer = ("M60 162 C64 152 66 140 61 124 C55 104 53 78 60 60 C70 40 88 30 106 30 C126 30 140 42 144 60 "
             "C148 80 145 104 143 124 C142 140 144 152 150 162Z")
    hole = ("M77 162 C81 150 81 136 77 118 C73 100 74 80 82 70 C92 58 112 60 120 72 C126 84 126 104 125 124 "
            "C124 142 125 152 127 162Z")
    d.shape("arch", outer + " " + hole, spot=True, extra='fill-rule="evenodd"')
    d.shape("arch2", "M136 46 C141 51 143 56 144 60 C148 80 145 104 143 124 C142 140 144 152 150 162 H140 C136 150 135 138 136 122 "
                     "C138 100 140 76 136 46Z", shadow=False, line=False)
    d.shape("arch2", "M82 70 C92 58 112 60 120 72 C110 66 92 66 82 70Z M125 124 C124 142 125 152 127 162 H131 C129 150 129 138 130 124Z", shadow=False, line=False)
    d.stroke("arch2", "M62 62 Q90 50 128 44 M58 86 Q64 92 60 100 M66 134 Q70 138 66 144", 1.4, line=False)
    d.shape("arch2", "M54 164 Q58 156 70 156 L80 158 Q84 162 82 166Z M120 166 Q122 158 134 156 Q148 156 156 164Z")
    # a hiker for scale
    d.limb("dark", "M166 162 V154", 2.4, shadow=False)
    d.marks("dark", circle(166, 150.5, 2))

# ================================================================ ANTELOPE CANYON
SLOT = {"w1": "#6E2A2E", "w2": "#9C3B2E", "w3": "#C9603A", "w4": "#E98E4E", "w5": "#F6B970", "sand": "#E9B57C", "beam": "#FFF6DC"}


def antelope_canyon(d: Drawing):
    def cx(y):
        return 100 + 7 * math.sin(y / 26)
    layers = [("w5", 6, 5, 0.0), ("w4", 16, 7, 0.9), ("w3", 28, 8, 1.9), ("w2", 42, 9, 2.8), ("w1", 58, 10, 3.9)]
    ys = list(range(-20, 230, 12))
    for role, gap, amp, ph in layers:
        left = [(cx(y) - gap - amp * math.sin(y / 17 + ph), y) for y in ys]
        right = [(cx(y) + gap + amp * math.sin(y / 15 + ph + 1.3), y) for y in ys]
        d.shape(role, smooth(left) + " L-30 220 L-30 -20Z", spot=role == "w3")
        d.shape(role, smooth(right) + " L230 220 L230 -20Z", spot=role == "w3")
        # flowing striations
        inl = [(x - 6, y) for x, y in left]
        inr = [(x + 6, y) for x, y in right]
        shade = {"w5": "w4", "w4": "w3", "w3": "w2", "w2": "w1", "w1": "w2"}[role]
        d.stroke(shade, smooth(inl[2:-2]) + " " + smooth(inr[2:-2]), 1.4, line=False)
    # the sand floor
    d.shape("sand", "M30 210 Q60 172 100 170 Q140 172 170 210Z")
    # the light beam from the slot above
    d.raw(f'<path d="M98 -10 L106 -10 L116 176 L86 176Z" fill="{d.c.get("beam", "#fff")}" opacity=".55"/>'
          f'<path d="M100 -10 L104 -10 L108 176 L94 176Z" fill="#FFFFFF" opacity=".6"/>'
          f'<ellipse cx="101" cy="176" rx="22" ry="6" fill="#FFFFFF" opacity=".55"/>',
          f'<path d="M98 -10 L106 -10 L116 176 L86 176Z" fill="{d.c.get("spot", "#fff")}" opacity=".35"/>'
          f'<path d="M98 -10 L86 176 M106 -10 L116 176" stroke="{d.c.get("ink", "#000")}" stroke-width="1.6" fill="none" stroke-dasharray="6 6"/>')


# ================================================================ HORSESHOE BEND
BEND = {"c1": "#ECB27A", "c2": "#D6874F", "c3": "#B2613B", "c4": "#80402B", "c5": "#5E2E22", "river": "#2E8C7B", "river2": "#7CCAB5", "haze": "#D9A790"}


def horseshoe_bend(d: Drawing):
    d.disc("glow", 152, 36, 13)
    d.band("haze", "M-30 52 L30 51 L36 44 H56 L62 50 L140 50 L146 42 H168 L174 50 L230 52")
    d.band("c1", "M-30 58 H230", line=False)
    d.stroke("c2", "M-30 86 Q20 80 40 90 M170 90 Q190 80 230 86 M-30 126 Q0 120 20 132 M200 130 Q210 120 230 124", 1.6, line=False)
    # the river makes an omega loop round the butte, the neck far away at the top
    loop = [(74, 48), (54, 70), (38, 104), (46, 144), (100, 168), (154, 144), (162, 104), (146, 70), (126, 48)]
    path = smooth(loop)
    if d.paper:
        d.limb("c3", path, 20)
    d.limb("river", path, 11, spot=True)
    d.stroke("river2", smooth([(44, 92), (40, 118), (54, 146), (84, 162)]) + " " + smooth([(158, 96), (160, 122), (146, 146), (118, 160)]), 1.4, line=False)
    # the butte: its banded wall facing us, then the rounded top
    butte = [(76, 56), (60, 74), (52, 104), (60, 136), (100, 154), (140, 136), (148, 104), (140, 74), (124, 56)]
    d.shape("c3", smooth(butte) + " Z")
    d.stroke("c4", smooth([(58, 112), (68, 138), (100, 150), (132, 138), (142, 112)]) + " " + smooth([(54, 96), (60, 124), (80, 140)]) +
             " " + smooth([(146, 96), (140, 124), (120, 140)]), 1.4, line=False)
    top = [(80, 56), (66, 74), (62, 100), (72, 124), (100, 134), (128, 124), (138, 100), (134, 74), (120, 56)]
    d.shape("c1", smooth(top) + " Z", shadow=False)
    if not d.paper:
        d.stroke("dark", smooth([(60, 116), (74, 140), (100, 148), (126, 140), (140, 116)]), 1.6)
    d.shape("c2", smooth([(70, 92), (76, 114), (100, 124), (124, 114), (130, 92)]) + " Q100 102 70 92Z", shadow=False, line=False)
    # the overlook we stand on
    d.shape("c4", "M-30 200 V170 Q10 168 40 178 Q62 186 78 200Z M230 200 V164 Q190 166 160 180 Q144 188 136 200Z")
    d.shape("c5", "M-30 200 V184 Q10 182 30 190 Q40 196 44 200Z M230 200 V182 Q196 182 176 192 Q168 196 166 200Z", shadow=False)
    d.limb("dark", "M152 180 V170", 2.6, shadow=False)
    d.marks("dark", circle(152, 166, 2.3))

# ================================================================ MORAINE LAKE
MORAINE = {"peak": "#8E8B96", "peak2": "#6A6773", "snow": "#FFFFFF", "forest": "#2F5D45", "forest2": "#22473A",
           "lake": "#2DBFC6", "lake2": "#8AE2E6", "rock": "#A39A8B", "rock2": "#7B7366"}
TEN = [(-30, 108), (-12, 72), (2, 84), (16, 56), (28, 70), (42, 46), (54, 64), (66, 40), (78, 60), (90, 36), (102, 56),
       (114, 42), (126, 62), (138, 46), (150, 66), (162, 50), (176, 72), (190, 60), (204, 80), (230, 98)]


def moraine_lake(d: Drawing):
    d.shape("light", cloud(150, 26, 0.8))
    # the Ten Peaks
    d.shape("peak", poly(*TEN, (230, 140), (-30, 140)))
    shade, snow = [], []
    for i in range(1, len(TEN) - 1):
        (px, py), (nx, ny) = TEN[i], TEN[i + 1]
        if py < TEN[i - 1][1] and py < ny:  # a summit: shade its right face, snow on top
            shade.append(poly((px, py), (nx, ny), (nx - 4, 128), (px + 2, 128)))
            snow.append(poly((px, py), (px + 4, py + 7), (px + 1, py + 6), (px - 2, py + 10), (px - 5, py + 7)))
            snow.append(poly((px - 1, py + 16), (px + 2, py + 22), (px - 3, py + 34), (px - 4, py + 24)))
    d.shape("peak2", " ".join(shade), shadow=False, line=False)
    d.shape("snow", " ".join(snow), shadow=False)
    # forested slopes running down to the water
    d.shape("forest", "M-30 92 Q10 98 40 116 Q60 126 80 128 H230 V140 H-30Z")
    d.shape("forest", "M230 96 Q200 104 170 120 Q156 126 140 128 H230Z")
    for x, h in [(-20, 30), (-6, 26), (8, 24), (22, 22), (36, 18), (50, 16), (176, 18), (190, 24), (204, 28), (218, 30)]:
        d.shape("forest2", pine(x, 134, h), shadow=False)
    d.shape("lake", "M-30 130 Q100 126 230 130 V200 H-30Z", spot=True)
    # mirrored peaks in the still water
    if d.paper:
        d.raw(f'<g opacity=".18" transform="translate(0 258) scale(1 -1)"><path d="{poly(*TEN, (230, 128), (-30, 128))}" fill="#fff"/></g>')
    d.stroke("lake2", "M60 146 h30 M112 152 h40 M40 162 h22", 2)
    # the rockpile
    d.shape("rock", "M-30 200 V150 Q-10 140 10 146 Q24 136 40 146 Q56 144 62 160 Q78 170 80 200Z")
    d.shape("rock2", "M-30 200 V174 Q0 166 24 174 Q44 168 56 182 Q66 188 68 200Z", shadow=False)
    d.stroke("rock2", "M10 146 Q14 156 8 164 M40 146 Q38 156 44 164", 1.6, line=False)
    # a red canoe
    d.shape("pop", "M118 172 Q140 178 162 172 Q156 180 140 180 Q124 180 118 172Z", spot=True)
    d.stroke("dark", "M136 176 L130 166", 1.6)


# ================================================================ CHATEAU FRONTENAC
FRONTENAC = {"brick": "#B65B41", "brick2": "#8A412E", "roof": "#62A38B", "roof2": "#3F7D68", "cliff": "#857A6C", "cliff2": "#655C51", "terrace": "#E2D8C8"}


def turret(d: Drawing, x, top, base, w=12, cone=26):
    d.shape("brick", rrect(x - w / 2, top, w, base - top, 1))
    d.shape("brick2", poly((x + 1, top), (x + w / 2, top), (x + w / 2, base), (x + 1, base)), shadow=False, line=False)
    d.shape("roof", poly((x - w / 2 - 2, top + 1), (x, top - cone), (x + w / 2 + 2, top + 1)), spot=True)
    d.shape("roof2", poly((x, top - cone), (x + w / 2 + 2, top + 1), (x + 1, top + 1)), shadow=False, line=False)
    d.marks("dark", rrect(x - 1.5, top + 6, 3, 5, 1))


def frontenac(d: Drawing):
    d.disc("glow", 46, 56, 16)
    # wings with steep copper roofs
    for x0, x1, top, rtop in [(24, 86, 96, 76), (114, 176, 98, 80)]:
        d.shape("roof", poly((x0 - 1, top + 1), (x0 + 6, rtop), (x1 - 6, rtop), (x1 + 1, top + 1)))
        d.shape("roof2", poly((x1 - 6, rtop), (x1 + 1, top + 1), (x1 - 12, top + 1)), shadow=False, line=False)
        d.marks("brick2", " ".join(poly((x - 3, top - 2), (x, top - 10), (x + 3, top - 2)) for x in range(int(x0) + 12, int(x1) - 6, 12)))
        d.shape("brick", rrect(x0, top, x1 - x0, 140 - top, 1))
        d.marks("dark", " ".join(rrect(x, y, 3, 5, 1) for x in range(int(x0) + 5, int(x1) - 4, 8) for y in (top + 7, top + 19, top + 31)))
    turret(d, 30, 92, 140, 13, 28)
    turret(d, 170, 94, 140, 13, 28)
    turret(d, 82, 84, 140, 10, 20)
    turret(d, 118, 86, 140, 10, 20)
    # the central tower with its tall pyramid roof
    d.shape("brick", rrect(84, 66, 32, 74, 1), spot=False)
    d.shape("brick2", poly((106, 66), (116, 66), (116, 140), (106, 140)), shadow=False, line=False)
    d.marks("dark", " ".join(rrect(x, y, 3.4, 6, 1) for x in (89, 96.3, 103.6, 110) for y in (74, 88, 102, 116)))
    d.shape("roof", poly((81, 67), (92, 30), (108, 30), (119, 67)), spot=True)
    d.shape("roof2", poly((108, 30), (119, 67), (106, 67)), shadow=False, line=False)
    d.marks("brick2", poly((94, 56), (97, 48), (100, 56)) + " " + poly((102, 56), (105, 48), (108, 56)) + " " + poly((97, 42), (100, 36), (103, 42)))
    d.stroke("roof2", "M100 30 V18", 1.8)
    # Dufferin Terrace and the cliff above the river
    d.shape("terrace", rrect(-30, 138, 260, 6, 0))
    for x in (40, 150):
        d.shape("roof", "M" + f"{x - 8} 136 Q{x} 124 {x + 8} 136Z", spot=True)
        d.stroke("light", f"M{x - 6} 136 V142 M{x + 6} 136 V142", 1.4)
    d.shape("cliff", "M-30 144 H230 V200 H-30Z")
    d.shape("cliff2", "M-30 160 Q20 152 60 162 Q110 172 150 160 Q190 150 230 158 V200 H-30Z", shadow=False, line=False)
    d.stroke("cliff2", "M20 150 L16 160 M70 148 L74 158 M130 148 L126 156", 1.6, line=False)
    d.band("mid", waves(172, 3, 24))
    d.band("near", waves(186, 3, 30), line=False)


# ================================================================ HAVANA
HAVANA = {"b1": "#F4C95D", "b2": "#7CC6BF", "b3": "#EE9D88", "trim": "#FFF7EA", "shutter": "#3E7C6E", "capitol": "#CDBF9F",
          "capitol2": "#A89A7C", "road": "#5C5A5E", "walk": "#D8CFC0", "chrome": "#E4E8EC", "tyre": "#26262A"}


def facade(d: Drawing, x0, x1, top, role):
    d.shape(role, rrect(x0, top, x1 - x0, 170 - top, 0))
    d.shape("trim", rrect(x0 - 1, top - 3, x1 - x0 + 2, 5, 1), shadow=False)
    d.shape("trim", rrect(x0 - 1, 124, x1 - x0 + 2, 3, 0), shadow=False, line=False)
    for x in range(int(x0) + 8, int(x1) - 8, 16):
        for y in (top + 10, top + 46):
            d.marks("shutter", f"M{x} {y + 18} V{y + 4} Q{x + 4} {y} {x + 8} {y + 4} V{y + 18}Z")
            d.stroke("trim", f"M{x - 2} {y + 20} H{x + 10} M{x} {y + 20} V{y + 16} M{x + 4} {y + 20} V{y + 16} M{x + 8} {y + 20} V{y + 16}", 1)


def havana(d: Drawing):
    # El Capitolio's dome, behind the street
    d.shape("capitol", rrect(84, 34, 32, 18, 1))
    d.shape("capitol", "M86 35 Q86 14 100 12 Q114 14 114 35Z")
    d.shape("capitol2", "M100 12 Q114 14 114 35 H104 Q106 20 100 12Z", shadow=False, line=False)
    d.stroke("capitol2", " ".join(f"M{x} 38 V50" for x in range(87, 115, 4)), 1, line=False)
    d.stroke("capitol2", "M100 12 V4", 2)
    facade(d, -30, 62, 30, "b1")
    facade(d, 138, 230, 36, "b3")
    facade(d, 62, 138, 52, "b2")
    palm(d, 178, 168, 64, lean=-6, role="shutter")
    d.shape("walk", "M-30 160 H230 V166 H-30Z")
    d.shape("road", "M-30 166 H230 V210 H-30Z", line=False)
    d.stroke("trim", "M10 186 h18 M70 186 h18 M130 186 h18 M190 186 h18", 2, line=False)
    # 1950s hardtop with tail fins
    def car():
        body = ("M30 150 L31 140 Q33 134 44 133 L66 132 L77 117 Q81 113 90 113 L122 113 Q130 113 136 121 L143 131 "
                "L164 132 L174 124 L176 136 L175 150 Q174 156 168 156 L36 156 Q30 156 30 150Z")
        d.shape("hero", body, spot=True)
        d.shape("light", "M70 131 L79 118 Q82 115 90 115 L121 115 Q128 115 133 121 L139 131Z", shadow=False)
        d.shape("sky2", "M76 129 L83 119 H103 V129Z M107 119 H122 Q127 119 131 124 L134 129 H107Z", shadow=False)
        d.shape("light", "M31 144 H175 V148 H31Z", shadow=False)
        d.stroke("chrome", "M44 140 Q100 136 168 138", 1.6, line=False)
        d.shape("chrome", rrect(26, 148, 14, 6, 2.5))
        d.shape("chrome", rrect(166, 148, 14, 6, 2.5))
        d.marks("chrome", circle(34, 140, 3))
        d.marks("pop", rrect(172, 137, 4, 6, 1.5))
        for x in (58, 148):
            d.shape("tyre", circle(x, 156, 11))
            d.shape("chrome", circle(x, 156, 6.5), shadow=False)
            d.shape("tyre", circle(x, 156, 2.4), shadow=False)
    group(d, "translate(0 6)", car)


# ================================================================ SALAR DE UYUNI
UYUNI = {"salt": "#F4F1EA", "salt2": "#C6D3DC", "jeep": "#E8E4DA", "tyre": "#2C2C30"}
HORIZON = 112


def uyuni(d: Drawing):
    # distant volcanoes on the horizon, mirrored
    mts = "M-30 112 L10 108 L30 100 L44 103 L60 98 L76 106 L130 106 L148 96 L160 99 L176 92 L196 104 L230 108 V112Z"
    d.disc("glow", 52, 112, 13)
    d.shape("far", mts + " " + mts.replace("M-30 112", "M-30 112").replace(" V112Z", " V112Z"), shadow=False)
    d.shape("far", "M-30 112 L10 116 L30 124 L44 121 L60 126 L76 118 L130 118 L148 128 L160 125 L176 132 L196 120 L230 116 V112Z",
            shadow=False, line=False, extra='opacity=".6"')
    d.shape("light", cloud(116, 46, 1.2))
    d.shape("light", cloud(14, 64, 0.8))
    d.shape("light", cloud(160, 76, 0.7))
    mirror_y(d, HORIZON, lambda: (d.shape("light", cloud(116, 46, 1.2), shadow=False), d.shape("light", cloud(14, 64, 0.8), shadow=False),
                                  d.shape("light", cloud(160, 76, 0.7), shadow=False)), ".75")
    d.stroke("light", "M-30 112 H230", 1.6, line=False)
    if not d.paper:
        d.stroke("dark", "M-30 112 H230", 2)
    # a 4x4 standing on the mirror
    ground = 140
    def jeep():
        d.shape("hero", f"M70 {ground - 6} V{ground - 20} L76 {ground - 22} L82 {ground - 36} H124 L127 {ground - 22} L134 {ground - 20} V{ground - 6}Z", spot=True)
        d.shape("light", rrect(84, ground - 34, 12, 11, 1.5), shadow=False)
        d.shape("light", rrect(99, ground - 34, 11, 11, 1.5), shadow=False)
        d.shape("light", rrect(113, ground - 34, 10, 11, 1.5), shadow=False)
        d.shape("dark", rrect(82, ground - 42, 42, 4, 1))
        d.stroke("dark", f"M86 {ground - 38} V{ground - 36} M120 {ground - 38} V{ground - 36}", 1.4)
        d.shape("tyre", circle(84, ground - 5, 7))
        d.shape("tyre", circle(120, ground - 5, 7))
        d.shape("light", circle(84, ground - 5, 2.6), shadow=False)
        d.shape("light", circle(120, ground - 5, 2.6), shadow=False)
        # two travellers
        d.limb("dark", f"M146 {ground} V{ground - 14} M154 {ground} V{ground - 14}", 3.2, shadow=False)
        d.marks("dark", circle(146, ground - 18, 2.8) + " " + circle(154, ground - 18, 2.8))
        d.limb("dark", f"M146 {ground - 12} L140 {ground - 22} M154 {ground - 12} L160 {ground - 22}", 2.2, shadow=False)
    jeep()
    mirror_y(d, ground + 2, jeep, ".45")
    d.stroke("light", f"M30 {ground + 2} H180", 1.4, line=False)
    if not d.paper:
        d.stroke("dark", f"M40 {ground + 2} H70 M134 {ground + 2} H170", 1.6)
    # hexagon salt crust at the very front
    hexes = []
    for row, y in enumerate((178, 192)):
        for i in range(-1, 9):
            x = i * 26 + (13 if row else 0)
            hexes.append(f"M{x - 13} {y} L{x - 6} {y - 7} H{x + 6} L{x + 13} {y}")
    d.shape("salt", "M-30 172 Q100 166 230 172 V210 H-30Z")
    d.stroke("salt2", " ".join(hexes), 1.4)


# ================================================================ PERITO MORENO
GLACIER = {"ice": "#F3F9FC", "ice2": "#BFE2F1", "ice3": "#79BEDF", "lake": "#7CB7C6", "lake2": "#B8DDE6", "rock": "#8C8A9C", "rock2": "#6A6878", "forest": "#4C7148"}


def perito_moreno(d: Drawing):
    # Andes behind
    d.band("rock", "M-30 104 L0 72 L20 82 L44 50 L66 70 L90 56 L116 80 L140 52 L166 70 L188 58 L230 84")
    d.shape("light", "M44 50 L52 60 L46 58 L40 64 L36 58Z M140 52 L148 62 L142 60 L136 66 L132 60Z M188 58 L195 66 L190 65 L185 70 L181 65Z", shadow=False)
    # the ice river pouring down the valley
    d.shape("ice", "M60 112 Q86 86 104 76 Q122 66 140 62 Q164 58 230 66 V120 H60Z")
    d.stroke("ice2", "M100 84 Q130 74 170 72 M90 96 Q130 84 190 84 M84 106 Q130 96 210 98", 1.8, line=False)
    d.shape("forest", "M-30 98 Q10 88 40 100 Q60 110 70 124 H-30Z")
    # the ice front: jagged towers falling into the lake
    top = [(-30, 132), (-10, 120), (0, 126), (10, 112), (20, 118), (30, 106), (40, 114), (52, 102), (62, 110), (74, 98),
           (84, 106), (96, 96), (108, 104), (120, 94), (132, 102), (144, 92), (156, 100), (168, 92), (180, 100), (194, 94), (206, 104), (230, 100)]
    d.shape("ice", poly(*top, (230, 146), (-30, 146)))
    d.shape("ice2", poly(*[(x, y + 18) for x, y in top], (230, 146), (-30, 146)), shadow=False, line=False)
    cracks = " ".join(f"M{x} {y + 4} L{x + 2} {y + 26} L{x - 1} {146}" for x, y in top[2:-1:2])
    d.stroke("ice3", cracks, 2.2, line=False)
    d.shape("ice3", " ".join(poly((x - 3, y + 10), (x + 3, y + 10), (x + 4, 146), (x - 4, 146)) for x, y in top[1:-1:3]), shadow=False, line=False)
    if not d.paper:
        d.stroke("dark", " ".join(f"M{x} {y + 8} V{y + 24}" for x, y in top[3:-2:3]), 1.4)
    # lake with floating ice
    d.shape("lake", "M-30 144 H230 V200 H-30Z", spot=True)
    d.shape("light", "M86 146 Q100 136 116 146 Q100 150 86 146Z", shadow=False)
    for x, y, w in [(40, 164, 14), (128, 172, 20), (166, 158, 10), (70, 182, 10)]:
        d.shape("ice", f"M{x} {y} L{x + w * .3} {y - w * .5} L{x + w * .7} {y - w * .45} L{x + w} {y}Z")
        d.shape("ice2", f"M{x + w * .55} {y - w * .47} L{x + w * .7} {y - w * .45} L{x + w} {y} H{x + w * .55}Z", shadow=False, line=False)
    d.stroke("lake2", "M10 176 h20 M96 166 h16 M150 186 h22", 1.8)


# ================================================================ ANGEL FALLS
TEPUI = {"rock": "#A06A52", "rock2": "#7A4B3A", "rock3": "#5C372B", "top": "#5E8F4E", "fall": "#FFFFFF", "fall2": "#D9ECF3",
         "jungle": "#3F7A44", "jungle2": "#2F5E36"}


def angel_falls(d: Drawing):
    d.shape("far", "M150 200 V86 Q152 80 160 80 H230 V200Z")
    d.shape("light", cloud(160, 64, 0.9))
    # the tepui: a sheer-walled table mountain
    face = "M-30 200 V44 L20 38 L60 36 L96 34 L124 38 L138 44 Q144 80 140 110 Q138 140 146 200Z"
    d.shape("rock", face)
    d.shape("rock2", "M118 40 L124 38 L138 44 Q144 80 140 110 Q138 140 146 200 H120 Q126 140 124 100 Q122 70 118 40Z", shadow=False, line=False)
    d.stroke("rock2", "M14 48 V170 M34 44 V150 M56 42 V160 M76 40 V140 M88 52 V110", 1.6, line=False)
    d.shape("top", "M-30 46 L20 38 L60 36 L96 34 L124 38 L138 44 L132 48 Q100 42 60 44 Q20 44 -30 52Z")
    # notch where the river leaves the summit
    d.shape("rock3", "M94 36 Q100 46 106 36 L104 60 Q100 64 96 60Z", shadow=False)
    # the fall: a long white ribbon breaking into spray
    d.shape("fall", "M97 36 Q101 34 105 36 L106 80 Q110 110 114 140 Q100 146 88 140 Q92 110 96 80Z", spot=True)
    d.stroke("fall2", "M101 44 V82 Q102 110 104 138 M98 90 Q96 112 94 136 M108 96 Q110 116 110 136", 1.4, line=False)
    d.shape("light", "M60 156 Q66 140 82 142 Q90 130 104 136 Q118 128 128 140 Q144 140 146 156Z")
    d.shape("light", cloud(-6, 96, 1.1), shadow=False)
    d.shape("jungle", canopy(-30, 230, 154, 11, 210))
    d.shape("jungle2", canopy(-30, 230, 172, 13, 210), line=False)
    birds(d, [(160, 110, 1), (172, 104, .8)])


# ================================================================ SUGARLOAF
LOAF = {"rock": "#9C948C", "rock2": "#726B65", "forest": "#3E7348", "forest2": "#2C5636", "car": "#D94A35", "cablecol": "#2B2D35", "sea": "#4F9CC6"}


def sugarloaf(d: Drawing):
    d.disc("glow", 60, 58, 20)
    # Corcovado far off, with its statue
    d.shape("far", "M-30 150 V128 Q0 120 18 104 Q28 94 34 106 Q44 126 66 150Z")
    d.stroke("far", "M27 96 V86 M23 89.5 H31", 1.8)
    d.band("sea", "M-30 148 H230", line=False)
    if not d.paper:
        d.stroke("dark", "M-30 148 H230", 2)
    # Morro da Urca
    d.shape("forest", "M34 158 Q44 126 64 116 Q78 110 88 120 Q100 134 108 158Z")
    d.shape("forest2", "M78 112 Q84 114 88 120 Q100 134 108 158 H90 Q88 130 78 112Z", shadow=False, line=False)
    # Sugarloaf: a tall, leaning granite dome
    d.shape("rock", "M100 160 C100 118 106 68 124 46 Q136 34 150 40 C168 54 176 104 186 160Z", spot=True)
    d.shape("rock2", "M150 40 C168 54 176 104 186 160 H162 C164 112 158 66 142 40Z", shadow=False, line=False)
    d.stroke("rock2", "M116 80 Q112 110 114 150 M128 56 Q122 90 126 140 M140 52 Q138 80 142 110", 1.4, line=False)
    d.shape("forest", "M96 160 Q104 138 120 142 Q130 134 144 144 Q162 136 178 148 Q188 152 192 160Z")
    d.shape("forest", "M130 44 Q136 36 146 40 Q140 44 130 46Z", shadow=False)
    # the cable car line from Urca up to the summit
    d.stroke("cablecol", "M78 114 L136 44 M80 116 L138 46", 1)
    def gondola():
        d.stroke("cablecol", "M0 -10 V-4", 1.4)
        d.shape("car", rrect(-7, -5, 14, 10, 2.5), spot=True)
        d.shape("light", rrect(-5, -3, 10, 4, 1), shadow=False)
    group(d, "translate(107 89)", gondola)
    d.band("near", waves(168, 3, 24))
    def boat():
        d.shape("light", "M0 0 L0 -18 L11 -1Z")
        d.shape("pop", "M-10 0 H14 L11 4 H-7Z")
    group(d, "translate(50 178) scale(.9)", boat)
    d.band("deep", waves(184, 3, 30), line=False)

# ================================================================ FITZ ROY
FITZ = {"granite": "#E3804B", "granite2": "#B5552F", "snow": "#FFFFFF", "glacier": "#DCEEF5", "lake": "#3BB4C1", "lake2": "#8EDCE2",
        "moraine": "#7E776F", "moraine2": "#5F5952"}


def fitz_roy(d: Drawing):
    d.disc("glow", 160, 56, 14)
    # the massif: Fitz Roy's broad tooth flanked by sharp needles
    massif = poly((-30, 132), (10, 108), (24, 82), (30, 96), (40, 70), (46, 86), (54, 58), (60, 62), (66, 40), (72, 70),
                  (80, 62), (88, 34), (98, 22), (106, 24), (114, 40), (122, 54), (130, 50), (136, 60), (142, 56), (152, 80),
                  (160, 72), (168, 92), (184, 100), (230, 120), (230, 140), (-30, 140))
    d.shape("granite", massif, spot=True)
    d.shape("granite2", poly((98, 22), (106, 24), (114, 40), (122, 54), (128, 120), (100, 120), (104, 60)) + " " +
            poly((66, 40), (72, 70), (76, 110), (68, 110)) + " " + poly((136, 60), (142, 56), (152, 80), (148, 112), (138, 112)) + " " +
            poly((40, 70), (46, 86), (48, 112), (40, 112)), shadow=False, line=False)
    d.stroke("granite2", "M90 50 L86 96 M60 76 V104", 1.4, line=False)
    d.shape("snow", poly((86, 38), (92, 44), (90, 52), (84, 48)) + " " + poly((98, 22), (106, 24), (102, 30), (96, 28)) + " " +
            poly((116, 46), (120, 52), (116, 58)), shadow=False)
    # glaciers draped below
    d.shape("glacier", "M-30 136 Q10 112 40 116 Q60 104 80 112 Q100 100 124 110 Q150 104 176 116 Q200 112 230 124 V150 H-30Z")
    d.stroke("moraine", "M30 124 Q60 116 90 122 M120 120 Q150 114 180 124", 1.4, line=False)
    d.shape("moraine", "M-30 150 Q30 132 70 140 Q100 134 130 140 Q170 132 230 146 V200 H-30Z")
    d.shape("lake", "M30 154 Q100 142 170 154 Q150 170 100 170 Q50 170 30 154Z", spot=False)
    d.stroke("lake2", "M66 158 h24 M110 160 h20", 1.8)
    d.shape("moraine2", "M-30 200 V172 Q20 162 60 176 Q90 186 100 200Z M230 200 V170 Q180 164 150 180 Q136 190 132 200Z")


# ================================================================ ARENAL
ARENAL = {"ash": "#7D766C", "ash2": "#5E5850", "green": "#5B9A50", "green2": "#3F7A3E", "jungle": "#3C7A42", "jungle2": "#2C5C34", "steam": "#FFFFFF"}


def arenal(d: Drawing):
    d.disc("glow", 152, 70, 18)
    d.band("far", "M-30 140 Q30 128 70 134 Q130 126 230 136")
    # the cone: steep concave flanks, a notched summit
    cone = "M4 168 Q60 132 82 64 Q86 48 94 46 L98 49 L103 45 Q112 47 118 64 Q140 132 196 168Z"
    d.shape("ash", cone, spot=True)
    d.shape("ash2", "M103 45 Q112 47 118 64 Q140 132 196 168 H150 Q120 120 108 60Z", shadow=False, line=False)
    d.stroke("ash2", "M92 56 Q86 90 72 120 M100 56 Q98 90 92 126", 1.4, line=False)
    # green lower flanks
    d.shape("green", "M4 168 Q40 146 58 124 L66 118 L72 122 L80 112 L88 118 L96 108 L104 116 L112 110 L120 120 L128 114 L136 124 Q156 148 196 168Z")
    d.shape("green2", "M112 110 L120 120 L128 114 L136 124 Q156 148 196 168 H150 Q130 140 112 110Z", shadow=False, line=False)
    # cloud cap and a wisp of steam
    d.shape("steam", "M78 54 Q80 44 90 44 Q94 34 106 38 Q116 34 120 44 Q130 46 128 56 Q100 60 78 54Z")
    d.shape("light", cloud(20, 90, 0.9))
    d.shape("light", cloud(140, 100, 0.8))
    d.shape("jungle", canopy(-30, 230, 160, 10, 210))
    palm(d, 30, 190, 44, lean=-8, role="jungle2")
    palm(d, 172, 190, 50, lean=8, role="jungle2")
    d.shape("jungle2", canopy(-30, 230, 178, 12, 210), line=False)


# ================================================================ concepts
NO_GOLD = ["coastal", "meadow", "blush", "dusk"]

CONCEPTS = [
    Concept("lm2-tikal", "landmark-tikal", "Tikal", tikal, overrides=TIKAL,
            checks=[("stone", "glow"), ("stone", "sky"), ("stone2", "light"), ("jungle", "stone")],
            fixes={"glow": ["near", "mid", "pop", "deep"]}),
    Concept("lm2-teotihuacan", "landmark-teotihuacan", "Teotihuacan", teotihuacan, overrides=TEO,
            checks=[("stone", "hill"), ("stone", "sky"), ("hill", "sky"), ("hero", "sky"), ("pop", "sky")],
            fixes={"hero": ["pop", "deep", "near"], "pop": ["hero", "deep"]}),
    Concept("lm2-gatewayarch", "landmark-gateway-arch", "Gateway Arch", gateway_arch, overrides=ARCH,
            checks=[("steel", "sky"), ("steel", "far"), ("steel", "glow"), ("far", "sky"), ("court", "far")],
            fixes={"far": ["mid", "near", "deep"], "glow": ["pop", "glow2", "near"]}),
    Concept("lm2-lincoln", "landmark-lincoln-memorial", "Lincoln Memorial", lincoln, overrides=MARBLE,
            checks=[("marble", "sky"), ("marble", "near"), ("near", "sky"), ("pool", "mid")],
            fixes={"sky": ["glow2", "far", BLUE_SKY], "mid": ["near", "deep"]}),
    Concept("lm2-washington", "landmark-washington-monument", "Washington Monument", washington, overrides=OBELISK,
            checks=[("marble", "sky"), ("marble", "near"), ("blossom", "sky"), ("near", "sky")],
            fixes={"sky": ["glow2", "far", BLUE_SKY]}),
    Concept("lm2-brooklyn", "landmark-brooklyn-bridge", "Brooklyn Bridge", brooklyn, overrides=BKLYN,
            checks=[("stone", "sky"), ("stone", "far"), ("cable", "sky"), ("far", "sky"), ("deck", "mid")],
            fixes={"far": ["mid", "near", "deep"], "deck": ["#8E877E"]}),
    Concept("lm2-alcatraz", "landmark-alcatraz", "Alcatraz", alcatraz, NO_GOLD, overrides=ALCA,
            checks=[("cell", "sky"), ("cell", "far"), ("rock", "mid"), ("far", "sky")],
            fixes={"sky": ["sky2", BLUE_SKY], "far": ["mid", "near", "deep"], "mid": ["near", "deep"]}),
    Concept("lm2-oldfaithful", "landmark-old-faithful", "Old Faithful", old_faithful, overrides=GEYSER,
            checks=[("steam", "sky"), ("steam", "mid"), ("pine", "mid"), ("sinter", "near")],
            fixes={"sky": ["#9CC8E2"], "mid": ["near", "deep"], "near": ["deep", "mid"]}),
    Concept("lm2-delicatearch", "landmark-delicate-arch", "Delicate Arch", delicate_arch, overrides=SLICKROCK,
            checks=[("arch", "sky"), ("arch", "mtn"), ("mtn", "sky"), ("arch", "slick")],
            fixes={"sky": ["sky2", "light"]}),
    Concept("lm2-antelope", "landmark-antelope-canyon", "Antelope Canyon", antelope_canyon, ["golden", "blush", "coastal", "meadow"], overrides=SLOT,
            checks=[("w5", "sky")], fixes={"sky": ["light"]}),
    Concept("lm2-horseshoe", "landmark-horseshoe-bend", "Horseshoe Bend", horseshoe_bend, overrides=BEND,
            checks=[("haze", "sky"), ("river", "c3"), ("glow", "sky")],
            fixes={"haze": ["#C49AA6", "#B88C8C", "far"], "glow": ["glow2", "pop", "light"]}),
    Concept("lm2-moraine", "landmark-moraine-lake", "Moraine Lake", moraine_lake, NO_GOLD, overrides=MORAINE,
            checks=[("peak", "sky"), ("lake", "forest"), ("pop", "lake")],
            fixes={"pop": ["#D9472B"]}),
    Concept("lm2-frontenac", "landmark-chateau-frontenac", "Château Frontenac", frontenac, overrides=FRONTENAC,
            checks=[("roof", "sky"), ("brick", "sky"), ("roof", "glow"), ("mid", "cliff")],
            fixes={"glow": ["glow2", "light", "pop"], "mid": ["near", "far"]}),
    Concept("lm2-havana", "landmark-havana", "Havana classic cars", havana, overrides=HAVANA,
            checks=[("hero", "b2"), ("hero", "b1"), ("hero", "b3"), ("hero", "walk"), ("capitol", "sky")],
            fixes={"hero": ["pop", "deep", "#D6336C", "#2E5C8A"], "sky": ["sky2", "far"]}),
    Concept("lm2-uyuni", "landmark-uyuni", "Salar de Uyuni", uyuni, NO_GOLD, overrides=UYUNI,
            checks=[("light", "sky"), ("hero", "sky"), ("far", "sky"), ("glow", "far")],
            fixes={"sky": ["#7FB3DA"], "hero": ["pop", "deep", "near"], "far": ["mid", "near"]}),
    Concept("lm2-peritomoreno", "landmark-perito-moreno", "Perito Moreno Glacier", perito_moreno, NO_GOLD, overrides=GLACIER,
            checks=[("ice", "rock"), ("ice", "lake"), ("rock", "sky"), ("forest", "rock")]),
    Concept("lm2-angelfalls", "landmark-angel-falls", "Angel Falls", angel_falls, overrides=TEPUI,
            checks=[("rock", "sky"), ("top", "sky"), ("fall", "rock"), ("far", "sky")],
            fixes={"far": ["mid", "near"]}),
    Concept("lm2-sugarloaf", "landmark-sugarloaf", "Sugarloaf Mountain", sugarloaf, NO_GOLD, overrides=LOAF,
            checks=[("rock", "sky"), ("rock", "glow"), ("far", "sky"), ("forest", "sea")],
            fixes={"glow": ["glow2", "pop", "light"], "far": ["mid", "near"]}),
    Concept("lm2-fitzroy", "landmark-fitz-roy", "Mount Fitz Roy", fitz_roy, overrides=FITZ,
            checks=[("granite", "sky"), ("granite", "glow"), ("glacier", "granite")],
            fixes={"glow": ["light", "glow2"], "sky": ["sky2", "#9CC8E2"]}),
    Concept("lm2-arenal", "landmark-arenal", "Arenal Volcano", arenal, overrides=ARENAL,
            checks=[("ash", "sky"), ("steam", "sky"), ("ash", "glow"), ("far", "green")],
            fixes={"sky": ["#9CC8E2"], "glow": ["glow2", "pop"], "far": ["mid", "near"]}),
]
