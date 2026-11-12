"""Mapsie Originals: city skylines of the Middle East, Africa, Australia and New Zealand.

One skyline per city: pale distant towers, a mid city layer (drawn as one band so the line
style reads as a single clean outline) and the city's signature buildings in front, usually over
water or desert with a sun disc behind.
"""
from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group, acacia  # noqa: F401
from _common import GIRAFFE
import math


# ================================================================ private helpers
def poly(*pts, close=True) -> str:
    s = "M" + " L".join(f"{x:g} {y:g}" for x, y in pts)
    return s + ("Z" if close else "")


def skyline(base, specs) -> str:
    """Band edge for a row of towers standing on y=base. Each spec is (x, w, h[, spire[, crown]]):
    a box w wide and h tall, an optional mast of `spire` height and an optional narrower top tier
    `crown` tall. Overlapping towers merge into one stepped silhouette."""
    rects = []
    for s in specs:
        x, w, h = s[:3]
        sp = s[3] if len(s) > 3 else 0
        cr = s[4] if len(s) > 4 else 0
        rects.append((x, x + w, base - h + cr))
        if cr:
            rects.append((x + w * .2, x + w * .8, base - h))
        if sp:
            rects.append((x + w / 2 - .8, x + w / 2 + .8, base - h - sp))
    xs = sorted({-30, 230} | {r[0] for r in rects} | {r[1] for r in rects})
    out, cur = f"M-30 {base}", base
    for a, b in zip(xs, xs[1:]):
        m = (a + b) / 2
        y = min([t for x0, x1, t in rects if x0 < m < x1], default=base)
        if y != cur:
            out += f" H{a:.1f} V{y:.1f}"
            cur = y
    return out + f" H{230 if cur == base else 230}"


def block(d: Drawing, x0, x1, top, base, lit="tw", shade="tw2", k=.36, spot=False, line=True):
    """A plain tower with a shaded right face."""
    d.shape(lit, poly((x0, base), (x0, top), (x1, top), (x1, base)), spot=spot, line=line)
    xs = x1 - (x1 - x0) * k
    d.shape(shade, poly((xs, base), (xs, top), (x1, top), (x1, base)), shadow=False, line=False)


def floors(d: Drawing, role, x0, x1, y0, y1, gap=6.0, w=.9):
    """Horizontal floor lines (papercut only)."""
    ys, y = [], y0 + gap / 2
    while y < y1:
        ys.append(y)
        y += gap
    if ys:
        d.stroke(role, " ".join(f"M{x0:g} {v:.1f} H{x1:g}" for v in ys), w, line=False)


def mullions(d: Drawing, role, x0, x1, y0, y1, gap=4.0, w=.9):
    xs, x = [], x0 + gap / 2
    while x < x1:
        xs.append(x)
        x += gap
    if xs:
        d.stroke(role, " ".join(f"M{v:.1f} {y0:g} V{y1:g}" for v in xs), w, line=False)


def glints(d: Drawing, segs, role="light", w=2.0):
    d.stroke(role, " ".join(f"M{x} {y} h{l}" for x, y, l in segs), w)


def birds(d: Drawing, pts, role="dark"):
    s = " ".join(f"M{x} {y} q{3 * k} {-3 * k} {6 * k} 0 q{3 * k} {-3 * k} {6 * k} 0" for x, y, k in pts)
    d.stroke(role, s, 1.6)


def frond(x, y, ang, length, droop, w=0.22) -> str:
    """A palm leaf from (x, y) at angle ang (degrees), drooping by `droop`."""
    a = math.radians(ang)
    ex, ey = x + length * math.cos(a), y + length * math.sin(a) + droop
    mx, my = (x + ex) / 2, (y + ey) / 2 - droop * .6
    nx, ny = -(ey - y), ex - x
    k = w / 2
    return (f"M{x:.1f} {y:.1f} Q{mx + nx * k:.1f} {my + ny * k:.1f} {ex:.1f} {ey:.1f} "
            f"Q{mx - nx * k * .3:.1f} {my - ny * k * .3:.1f} {x:.1f} {y:.1f}Z")


def palm(d: Drawing, x0, y0, x1, y1, s=1.0, role="leaf", trunk="trunk", bend=6):
    d.limb(trunk, f"M{x0} {y0} Q{(x0 + x1) / 2 + bend} {(y0 + y1) / 2} {x1} {y1}", 3.4 * s)
    leaves = " ".join(frond(x1, y1, a, L * s, dr * s) for a, L, dr in
                      [(-170, 22, 9), (-130, 19, 4), (-90, 13, -2), (-50, 19, 4), (-10, 22, 9), (150, 17, 10), (30, 17, 10)])
    d.shape(role, leaves)


def merlons(x, y, w, n, h=5.0) -> str:
    """A row of stepped Moorish merlons sitting on y, spanning x..x+w."""
    mw = w / n
    s = ""
    for i in range(n):
        x0 = x + i * mw + mw * .1
        x1 = x0 + mw * .8
        s += (f"M{x0:.1f} {y} V{y - h * .5:.1f} H{x0 + mw * .15:.1f} V{y - h * .8:.1f} H{x0 + mw * .3:.1f} "
              f"L{(x0 + x1) / 2:.1f} {y - h:.1f} L{x1 - mw * .3:.1f} {y - h * .8:.1f} H{x1 - mw * .15:.1f} V{y - h * .5:.1f} H{x1:.1f} V{y}Z ")
    return s


def crenels(x, y, w, n, h=3.0) -> str:
    """Square battlements on y, spanning x..x+w."""
    mw = w / (2 * n - 1)
    return " ".join(poly((x + i * 2 * mw, y), (x + i * 2 * mw, y - h), (x + (i * 2 + 1) * mw, y - h), (x + (i * 2 + 1) * mw, y)) for i in range(n))


def pointed_arch(x, y, w, h) -> str:
    return f"M{x} {y + h} V{y + w * .5} Q{x} {y} {x + w / 2} {y - w * .25} Q{x + w} {y} {x + w} {y + w * .5} V{y + h}Z"


def round_arch(x, y, w, h) -> str:
    return f"M{x} {y + h} V{y + w / 2} A{w / 2} {w / 2} 0 0 1 {x + w} {y + w / 2} V{y + h}Z"


def onion(cx, base, r, h) -> str:
    """A bulbous dome on y=base, r wide, h tall."""
    return (f"M{cx - r} {base} C{cx - r * 1.05} {base - h * .55} {cx - r * .5} {base - h * .78} {cx} {base - h} "
            f"C{cx + r * .5} {base - h * .78} {cx + r * 1.05} {base - h * .55} {cx + r} {base}Z")


def dome(cx, base, r, h=None) -> str:
    h = r if h is None else h
    return f"M{cx - r} {base} C{cx - r} {base - h * .55} {cx - r * .55} {base - h} {cx} {base - h} C{cx + r * .55} {base - h} {cx + r} {base - h * .55} {cx + r} {base}Z"


def minaret(d: Drawing, x, base, top, w=4.0, lit="stone", shade="stone2", cap="gold", rings=2, pencil=False):
    """A slender minaret: shaft, balcony rings, a cap and a finial."""
    d.shape(lit, poly((x - w / 2, base), (x - w / 2, top + 6), (x + w / 2, top + 6), (x + w / 2, base)))
    for i in range(rings):
        y = top + 8 + i * (base - top - 12) / (rings + .6)
        d.shape(lit, rrect(x - w / 2 - 1.4, y, w + 2.8, 2.2, .8), shadow=False)
        d.stroke(shade, f"M{x - w / 2 - 1.4} {y + 2.2:.1f} H{x + w / 2 + 1.4}", .9, line=False)
    if pencil:
        d.shape(cap, poly((x - w / 2, top + 6), (x, top - 10), (x + w / 2, top + 6)), spot=True)
    else:
        d.shape(cap, onion(x, top + 6, w / 2 + .6, 7), spot=True)
        d.stroke(cap, f"M{x} {top - 1} V{top - 5}", 1.1)


def dhow(d: Drawing, x, y, s=1.0, hull="hull", sail="sail", sail2="sail2"):
    """A dhow with a lateen sail, waterline at y, centred near x."""
    def draw():
        d.stroke("hull", "M0 -2 V-40 M-22 -24 L26 -46", 1.6)
        d.shape(sail, poly((-20, -25), (24, -45), (8, -4)), spot=True)
        d.stroke(sail2, "M-6 -20 L12 -8 M4 -34 L14 -8", .9, line=False)
        d.shape(hull, "M-28 -8 L-20 -2 H18 L30 -12 L26 -12 L20 -6 H-18 Z M-20 -2 Q0 4 18 -2Z")
        d.shape(hull, "M-24 -5 H24 Q20 3 10 4 H-12 Q-20 2 -24 -5Z")
    group(d, f"translate({x} {y}) scale({s})", draw)


def sailboat(d: Drawing, x, y, s=1.0, sail="sail", hull="hull"):
    def draw():
        d.shape(sail, poly((0, -2), (0, -30), (11, -2)), spot=True)
        d.shape(sail, poly((-2, -4), (-2, -24), (-11, -4)))
        d.shape(hull, "M-13 0 H15 L11 5 H-9Z")
    group(d, f"translate({x} {y}) scale({s})", draw)


def bez(p0, p1, p2, t):
    return tuple((1 - t) ** 2 * a + 2 * (1 - t) * t * b + t * t * c for a, b, c in zip(p0, p1, p2))


# ================================================================ DUBAI
def burj(d: Drawing, lit="glass", shade="glass2"):
    """Burj Khalifa: stepped Y-plan wings around a central core, base y=178, tip y=8, x 70..130."""
    base = 178
    pieces = [(70, 76, 154, shade), (124, 130, 162, lit), (76, 82, 128, shade), (118, 124, 138, lit),
              (82, 88, 96, shade), (112, 118, 108, lit), (88, 94, 62, shade), (106, 112, 78, lit)]
    for x0, x1, top, role in pieces:
        if x0 < 100:
            path = poly((x0, base), (x0, top + 5), (x1, top), (x1, base))
        else:
            path = poly((x0, base), (x0, top), (x1, top + 5), (x1, base))
        d.shape(role, path)
    d.shape(lit, poly((94, base), (94, 50), (97, 46), (103, 46), (106, 50), (106, base)), spot=True)
    d.shape(lit, poly((96.5, 47), (98.5, 20), (100, 8), (101.5, 20), (103.5, 47)))
    d.stroke("light", "M100 52 V176 M97 30 H103", 1.2, line=False)


def dubai(d: Drawing):
    d.disc("glow", 150, 58, 14)
    # Dubai Marina, far off behind the Burj Al Arab
    d.band("far", skyline(150, [(12, 8, 30), (22, 6, 40), (30, 9, 24), (66, 6, 30), (128, 8, 52), (137, 7, 64, 6), (145, 9, 70),
                                (155, 7, 60), (163, 9, 74, 0, 6), (173, 8, 56), (182, 9, 46), (192, 8, 34)]), line=False)
    d.band("mid", skyline(150, [(8, 10, 20), (20, 8, 28), (56, 10, 18), (68, 8, 24), (118, 9, 22), (130, 10, 14), (178, 10, 16), (190, 10, 22)]))
    # Emirates Towers: two wedge-topped towers
    d.shape("tw", poly((24, 150), (24, 100), (36, 88), (36, 150)))
    d.shape("tw2", poly((32, 150), (32, 92), (36, 88), (36, 150)), shadow=False, line=False)
    d.stroke("tw2", "M36 88 V78", 1.3)
    d.shape("tw", poly((39, 150), (39, 110), (49, 100), (49, 150)))
    d.shape("tw2", poly((45.5, 150), (45.5, 103.5), (49, 100), (49, 150)), shadow=False, line=False)
    # Museum of the Future: the silver torus on its green mound
    d.shape("green", "M48 151 Q50 140 64 139 Q78 140 80 151Z")
    d.shape("steel", ellipse(64, 126, 13, 14) + " " + ellipse(64, 123, 6.5, 6.5), extra='fill-rule="evenodd"', spot=True)
    d.stroke("steel2", "M54 134 Q64 142 74 134 M57 115 q3 2 5 0 M66 136 q3 -2 6 0 M51 124 q2 -3 0 -6", 1.1, line=False)
    # Burj Khalifa
    group(d, "translate(100 151) scale(.74) translate(-100 -178)", lambda: burj(d))
    # the creek / gulf
    d.band("near", waves(150, 1.4, 18))
    # Burj Al Arab on its island
    d.shape("isle", ellipse(157, 156, 21, 3.4))
    d.shape("sail", "M143 155 C137 128 146 106 167 95 L172 155Z", spot=False)
    d.stroke("sail2", "M171 150 L166 130 L170 114 L167 100 M168 96 L169 78", 1.4)
    d.stroke("sail2", "M150 152 C146 132 151 114 165 102", 1, line=False)
    d.shape("sail2", ellipse(151, 109, 6.5, 1.6), shadow=False)
    glints(d, [(36, 160, 14), (88, 166, 18), (130, 172, 14), (60, 176, 16)])
    d.band("deep", waves(182, 2.4, 30), line=False)


DUBAI = {"glass": "#6E8DAB", "glass2": "#52708E", "tw": "#7A8794", "tw2": "#5D6977", "steel": "#D6DCE3", "steel2": "#9EAAB7",
         "sail": "#FFFFFF", "sail2": "#B9C2CE", "isle": "#E9D3A6", "green": "#7FA866"}


# ================================================================ ABU DHABI
def etihad(x, w, top, base) -> str:
    """One of the Etihad Towers: a tall lozenge with a curved, leaning crown."""
    return f"M{x} {base} L{x + w * .04} {top + 16} Q{x + w * .2} {top} {x + w * .9} {top + 2} Q{x + w} {top + 8} {x + w} {top + 20} L{x + w} {base}Z"


def abu_dhabi(d: Drawing):
    d.disc("glow", 52, 58, 14)
    d.band("far", skyline(148, [(10, 8, 34), (20, 7, 44), (90, 8, 40), (100, 6, 50), (108, 9, 36), (176, 8, 44), (186, 8, 30)]), line=False)
    d.band("mid", skyline(148, [(14, 10, 24), (26, 8, 30), (80, 9, 34), (92, 8, 26), (102, 10, 30), (170, 9, 26), (182, 10, 34)]))
    # Aldar HQ: the round "coin" building, and Capital Gate leaning over
    d.shape("coin", circle(46, 108, 17))
    d.stroke("coin2", " ".join(f"M{46 + 17 * math.cos(a):.1f} {108 + 17 * math.sin(a):.1f} L{46 - 17 * math.cos(a + 1.2):.1f} {108 + 17 * math.sin(a + 1.2):.1f}"
                               for a in [i * .55 for i in range(6)]), .9, line=False)
    d.shape("coin2", "M40 124 H52 L50 148 H42Z")
    d.shape("tw", "M66 148 C66 120 70 92 80 66 L92 70 C86 96 80 124 80 148Z")
    d.shape("tw2", "M86 68 L92 70 C86 96 80 124 80 148 L75 148 C76 120 80 92 86 68Z", shadow=False, line=False)
    # Etihad Towers
    for x, w, top, role in [(170, 13, 70, "tw"), (124, 14, 50, "tw"), (156, 13, 62, "tw2"), (140, 14, 40, "tw")]:
        d.shape(role, etihad(x, w, top, 148))
        d.stroke("tw2" if role == "tw" else "tw", f"M{x + w * .7} {top + 8} V148", 1.2, line=False)
    # Sheikh Zayed Grand Mosque
    d.shape("marble", rrect(26, 136, 148, 26, 1.5))
    d.marks("marble2", " ".join(pointed_arch(32 + i * 9.4, 146, 5.4, 12) for i in range(15)))
    d.shape("marble", rrect(80, 124, 40, 14, 1))
    for cx, r, h in [(50, 6, 10), (150, 6, 10), (66, 9, 15), (134, 9, 15)]:
        d.shape("marble", onion(cx, 137, r, h))
        d.stroke("gold", f"M{cx} {137 - h} v-4", 1.2)
    d.shape("marble", onion(100, 125, 17, 30))
    d.shape("marble2", "M106 98 C113 103 118 112 117 125 H110 C111 113 109 104 106 98Z", shadow=False, line=False)
    d.stroke("gold", "M100 95 V87", 1.6)
    d.shape("gold", circle(100, 88, 2), shadow=False, spot=True)
    for x in (30, 170):
        minaret(d, x, 140, 82, 5, "marble", "marble2", "gold", rings=3)
    # reflecting pool
    d.band("pool", "M-30 162 H230")
    d.stroke("light", "M60 170 h20 M110 168 h26 M86 178 h16", 1.8)
    d.band("deep", hills(188, 3, 20), line=False)


ABU = {"marble": "#FFFFFF", "marble2": "#D9D5CB", "gold": "#E1B04A", "tw": "#6F93B2", "tw2": "#557895",
       "coin": "#8FAFC6", "coin2": "#6A8CA6", "pool": "#5C9CC0"}


# ================================================================ DOHA
def doha(d: Drawing):
    d.disc("glow", 56, 56, 14)
    d.band("far", skyline(138, [(56, 7, 36), (64, 6, 52, 5), (96, 8, 44), (140, 7, 48), (150, 9, 56, 0, 6), (160, 7, 40), (170, 8, 30)]), line=False)
    d.band("mid", skyline(138, [(44, 8, 18), (54, 9, 26), (70, 10, 34), (100, 9, 30), (132, 8, 26), (146, 10, 36), (160, 9, 22), (172, 10, 16)]))
    # Palm Towers: twin towers with sliced crowns
    for x, top in [(60, 78), (71, 84)]:
        d.shape("tw3", poly((x, 138), (x, top + 6), (x + 9, top), (x + 9, 138)))
        d.shape("tw4", poly((x + 6, 138), (x + 6, top + 2), (x + 9, top), (x + 9, 138)), shadow=False, line=False)
    # Tornado Tower: the pinched hourglass
    d.shape("tw", "M84 138 Q93 100 84 60 H101 Q92 100 101 138Z")
    d.stroke("tw2", "M86 66 Q94 70 99 66 M89 82 Q94 85 96 82 M90 100 h3.5 M89 118 Q94 121 96 118", 1.1, line=False)
    d.shape("tw2", "M96 60 H101 Q92 100 101 138 H96 Q89 100 96 60Z", shadow=False, line=False)
    # Doha Tower (Burj Qatar): a domed cylinder with its lattice skin and spire
    d.stroke("tw2", "M121 46 V28", 1.4)
    d.shape("tw", "M112 138 V62 Q112 47 121 45 Q130 47 130 62 V138Z", spot=True)
    d.shape("tw2", "M125 46 Q130 48 130 62 V138 H125Z", shadow=False, line=False)
    d.stroke("tw2", " ".join(f"M112 {y} L121 {y - 9} L130 {y} M112 {y} L121 {y + 9} L130 {y}" for y in range(70, 138, 18)), .9, line=False)
    # Al Bidda Tower with its pointed crown
    d.shape("tw3", poly((138, 138), (138, 80), (144, 68), (150, 80), (150, 138)))
    d.shape("tw4", poly((144, 138), (144, 68), (150, 80), (150, 138)), shadow=False, line=False)
    d.band("near", waves(138, 1.4, 18))
    # Museum of Islamic Art on its promontory
    d.shape("isle", "M18 152 L22 146 H82 L88 152Z")
    for x0, x1, y0, y1, ch in [(26, 78, 132, 147, 0), (32, 72, 120, 133, 3), (38, 66, 108, 121, 4), (44, 60, 98, 109, 3)]:
        d.shape("stone", poly((x0, y1), (x0, y0 + ch), (x0 + ch, y0), (x1 - ch, y0), (x1, y0 + ch), (x1, y1)))
        d.shape("stone2", poly((x1 - (x1 - x0) * .32, y1), (x1 - (x1 - x0) * .32, y0), (x1 - ch, y0), (x1, y0 + ch), (x1, y1)), shadow=False, line=False)
    d.shape("stone", dome(52, 99, 4, 5), shadow=False)
    d.marks("dark", "M47 104 Q52 100 57 104 V106 H47Z")
    d.marks("stone2", round_arch(48, 138, 8, 9))
    dhow(d, 134, 168, .95)
    glints(d, [(20, 164, 14), (60, 172, 18), (164, 162, 14), (96, 178, 14)])
    d.band("deep", waves(184, 2.4, 30), line=False)


DOHA = {"tw": "#7290AE", "tw2": "#56738F", "tw3": "#8593A2", "tw4": "#677483", "stone": "#F1E7D4", "stone2": "#CDBFA5",
        "isle": "#D9C49A", "hull": "#8A5A34", "sail": "#FFFFFF", "sail2": "#C9CED6"}


# ================================================================ TEL AVIV
def tel_aviv(d: Drawing):
    d.disc("glow", 64, 58, 14)
    d.band("far", skyline(146, [(84, 8, 40), (94, 6, 54), (102, 9, 46), (172, 8, 48, 5), (182, 9, 36), (192, 8, 28)]), line=False)
    d.band("mid", skyline(146, [(80, 10, 18), (92, 9, 24), (104, 10, 16), (166, 10, 28), (178, 12, 22), (192, 10, 14)]))
    # Azrieli Center: round, triangular and square towers
    d.shape("tw", poly((112, 146), (112, 62), (126, 62), (126, 146)))
    d.shape("tw", ellipse(119, 62, 7, 2.2), shadow=False)
    d.shape("tw2", "M122 62.5 Q125 62 126 62 V146 H122Z", shadow=False, line=False)
    d.stroke("light", "M115 66 V144", 1.4, line=False)
    d.shape("tw", poly((130, 146), (130, 70), (144, 70), (144, 146)))
    d.shape("tw2", poly((135, 146), (135, 70), (144, 70), (144, 146)), shadow=False, line=False)
    d.stroke("tw", "M130 70 L135 66 L144 70", 1.4)
    d.shape("tw", poly((148, 146), (148, 78), (161, 78), (161, 146)))
    d.shape("tw2", poly((155, 146), (155, 78), (161, 78), (161, 146)), shadow=False, line=False)
    d.stroke("tw2", "M148 80 H161", 1.2, line=False)
    floors(d, "tw2", 112, 122, 66, 146, 8)
    floors(d, "tw2", 130, 135, 74, 146, 8)
    floors(d, "tw", 155, 161, 82, 146, 8)
    # Old Jaffa on its hill: stone houses, St Peter's bell tower and the sea minaret
    d.shape("hill", "M-30 150 L-30 120 Q10 108 36 110 Q62 112 86 150Z")
    d.shape("stone", poly((6, 130), (6, 120), (20, 120), (20, 116), (32, 116), (32, 122), (58, 122), (58, 126), (70, 126), (76, 140), (4, 140)))
    d.shape("stone", poly((40, 122), (40, 84), (42, 78), (44, 74), (46, 78), (48, 84), (48, 122)))
    d.shape("stone2", poly((44, 122), (44, 74), (46, 78), (48, 84), (48, 122)), shadow=False, line=False)
    d.marks("stone2", round_arch(42, 90, 3.2, 6))
    d.shape("stone", poly((14, 120), (14, 98), (17, 92), (20, 98), (20, 120)))
    d.shape("stone", rrect(12.5, 104, 9, 2, .6), shadow=False)
    d.marks("stone2", " ".join(round_arch(10 + i * 9, 128, 4, 6) for i in range(7)))
    # the beach and the Mediterranean
    d.band("near", waves(150, 1.4, 18))
    d.shape("sand", "M78 194 Q104 162 230 152 V230 H78Z")
    # lifeguard hut
    d.stroke("dark", "M146 166 L144 178 M156 166 L158 176", 1.6)
    d.shape("light", rrect(140, 156, 20, 10, 1.5))
    d.shape("pop", poly((138, 157), (150, 150), (162, 157)), spot=True)
    palm(d, 176, 176, 172, 130, .95, bend=8)
    glints(d, [(10, 160, 14), (36, 170, 16), (20, 180, 12)])
    d.band("deep", hills(194, 3, 30), line=False)


TELAVIV = {"tw": "#7690A8", "tw2": "#5A7389", "stone": "#D9B886", "stone2": "#AE8C5C", "hill": "#9E8A6A", "sand": "#F1DCAB",
           "leaf": "#4E8A4A", "trunk": "#8A5A33"}


# ================================================================ MUSCAT
def muscat(d: Drawing):
    d.disc("glow", 150, 52, 13)
    # the bare Hajar mountains wrapping round the town
    d.band("rock", "M-30 112 L-8 96 L6 100 L20 78 L32 90 L44 70 L56 84 L70 66 L84 86 L96 76 L108 92 L124 72 L138 86 L150 74 L164 92 L178 80 L196 98 L230 92")
    d.shape("rock2", "M20 78 L26 96 L32 90Z M44 70 L50 92 L56 84Z M70 66 L76 90 L84 86Z M124 72 L130 92 L138 86Z M150 74 L156 96 L164 92Z M178 80 L184 100 L196 98Z",
            shadow=False, line=False)
    d.band("rock2", "M-30 128 L10 112 L30 120 L60 106 L84 122 L120 110 L150 122 L180 108 L230 120", line=False)
    # whitewashed low town
    d.band("light", skyline(144, [(-30, 40, 6), (6, 10, 14), (18, 12, 10), (32, 8, 16), (42, 14, 8), (74, 12, 12), (88, 10, 18), (100, 12, 10),
                                  (114, 10, 14), (126, 14, 8), (142, 12, 12), (156, 10, 18), (168, 12, 10), (182, 12, 14), (196, 40, 6)]))
    # Sultan Qaboos Grand Mosque: main minaret and golden dome
    minaret(d, 40, 134, 46, 6, "stone", "stone2", "gold", rings=3)
    d.shape("stone", rrect(52, 124, 34, 16, 1))
    d.shape("gold", dome(69, 125, 14, 20), spot=True)
    d.stroke("gold2", "M58 116 Q69 112 80 116 M60 110 Q69 106 78 110", 1, line=False)
    d.stroke("gold", "M69 105 V97", 1.4)
    d.marks("stone2", " ".join(pointed_arch(55 + i * 7, 130, 4, 8) for i in range(4)))
    minaret(d, 92, 134, 96, 3.6, "stone", "stone2", "gold", rings=1)
    # Al Mirani fort on its rock above the harbour
    d.shape("rock", "M128 146 L132 128 Q140 120 152 122 L162 130 L168 146Z")
    d.shape("fort", "M136 128 V110 H150 V128Z")
    d.shape("fort", crenels(136, 110, 14, 4, 3), shadow=False)
    d.shape("fort", "M150 128 V116 Q150 112 156 112 Q162 112 162 116 V130Z")
    d.shape("fort", crenels(150, 112, 12, 3, 3), shadow=False)
    d.marks("fort2", rrect(141, 116, 3, 5, 1) + rrect(154, 118, 3, 5, 1))
    # harbour
    d.band("near", waves(146, 1.4, 18))
    dhow(d, 84, 170, .9)
    glints(d, [(20, 160, 14), (134, 164, 16), (150, 176, 14), (40, 178, 12)])
    d.band("deep", waves(184, 2.4, 30), line=False)


MUSCAT = {"rock": "#9C7358", "rock2": "#7A5642", "stone": "#FFFFFF", "stone2": "#D8D2C4", "gold": "#DDAE4C", "gold2": "#B88A2E",
          "fort": "#D8B486", "fort2": "#9E7A50", "hull": "#8A5A34", "sail": "#FFFFFF", "sail2": "#C9CED6"}


# ================================================================ CAIRO
def pyramid(d: Drawing, x, base, w, h, lit="sand", shade="sand2"):
    d.shape(lit, f"M{x - w / 2} {base} L{x} {base - h} L{x + w / 2} {base}Z")
    d.shape(shade, f"M{x} {base - h} L{x + w / 2} {base} L{x + w * .12} {base}Z", shadow=False)


def cairo(d: Drawing):
    d.disc("glow", 148, 80, 22)
    d.band("far", skyline(128, [(-30, 50, 6), (20, 8, 22), (30, 6, 30), (38, 9, 18), (90, 8, 24), (100, 9, 16)]), line=False)
    # Giza pyramids beyond the Nile
    pyramid(d, 168, 128, 52, 34)
    pyramid(d, 136, 128, 50, 33)
    pyramid(d, 110, 128, 24, 15)
    d.band("mid", skyline(130, [(-30, 50, 4), (40, 10, 14), (52, 8, 20), (84, 10, 12), (96, 8, 8)]))
    # the Nile
    d.band("near", waves(132, 1.4, 18))
    # the Citadel hill and Muhammad Ali Mosque
    d.shape("hill", "M-30 160 L-30 126 Q14 116 54 124 Q62 128 64 160Z")
    d.shape("stone", rrect(22, 106, 32, 20, 1))
    d.shape("lead", dome(38, 108, 11, 13))
    d.shape("lead", dome(27, 110, 5, 5) + " " + dome(49, 110, 5, 5), shadow=False)
    d.shape("lead2", "M42 96 C46 98 49 102 49 108 H44 C44 103 43 99 42 96Z", shadow=False, line=False)
    d.stroke("lead", "M38 95 V89", 1.3)
    for x in (20, 56):
        minaret(d, x, 126, 70, 3.2, "stone", "stone2", "lead", rings=2, pencil=True)
    # Cairo Tower: the lotus lattice tower on Gezira island
    d.shape("isle", ellipse(80, 152, 22, 4.2))
    d.shape("tower", "M74 152 L75.5 54 H84.5 L86 152Z")
    d.stroke("tower2", " ".join(f"M75.5 {y} L84.5 {y + 7} M84.5 {y} L75.5 {y + 7}" for y in range(58, 148, 7)), .9, line=False)
    d.shape("tower", "M70 44 Q72 54 75 56 H85 Q88 54 90 44 Q86 48 84 46 L80 50 L76 46 Q74 48 70 44Z", spot=True)
    d.shape("tower", rrect(73, 38, 14, 6, 1.5))
    d.marks("tower2", rrect(74.5, 40, 11, 2, .5))
    d.shape("tower", "M76 38 L80 30 L84 38Z", shadow=False)
    d.stroke("tower2", "M80 30 V20", 1.3)
    # felucca on the Nile
    d.stroke("hull", "M139 158 V118 M128 154 L160 106", 1.4)
    d.shape("sail", poly((140, 152), (158, 109), (146, 152)))
    d.shape("sail", poly((130, 152), (138, 120), (138, 152)), spot=True)
    d.shape("hull", "M122 154 H158 Q156 160 150 161 H130 Q124 160 122 154Z")
    glints(d, [(96, 142, 14), (164, 146, 12), (104, 160, 16)])
    d.band("bank", hills(172, 4, 10))
    palm(d, 172, 172, 168, 140, .8, bend=6)
    palm(d, 186, 174, 190, 148, .65, bend=-4)
    d.band("deep", hills(190, 3, 30), line=False)


CAIRO = {"sand": "#EDBE6F", "sand2": "#C98E45", "stone": "#C7B595", "stone2": "#9E8C6C", "lead": "#8C97A3", "lead2": "#6C7783",
         "hill": "#C9A277", "tower": "#D2895A", "tower2": "#A5643B", "isle": "#7FA866", "hull": "#7A4E2E", "sail": "#FFFFFF",
         "bank": "#6F9A5A", "leaf": "#4E8A4A", "trunk": "#8A5A33"}


# ================================================================ MARRAKECH
def koutoubia_tower(d: Drawing):
    """The Koutoubia minaret: shaft x 84..116, base 178, top finial y 8."""
    d.shape("stone", "M84 178 V60 H116 V178Z")
    d.shape("stone", merlons(84, 60, 32, 4, 6), shadow=False)
    d.shape("tile", rrect(84, 62, 32, 5, 0), shadow=False, spot=True)
    d.shape("stone2", pointed_arch(91, 76, 18, 26), shadow=False)
    d.stroke("stone", "M91 92 L100 84 L109 92 M91 100 L100 92 L109 100", 1.3, line=False)
    d.shape("stone2", pointed_arch(88, 112, 10, 18), shadow=False)
    d.shape("stone2", pointed_arch(102, 112, 10, 18), shadow=False)
    d.marks("dark", pointed_arch(97, 142, 6, 12))
    d.stroke("stone2", "M88 72 H112 M88 106 H112 M88 136 H112", 1.4)
    d.shape("stone", "M92 60 V38 H108 V60Z")
    d.shape("stone", merlons(92, 38, 16, 2, 4), shadow=False)
    d.shape("tile", rrect(92, 40, 16, 3, 0), shadow=False)
    d.marks("dark", pointed_arch(97.5, 46, 5, 10))
    d.shape("stone2", "M94 34 Q94 26 100 24 Q106 26 106 34Z")
    d.stroke("gold", "M100 24 V8", 1.6)
    for y, r in [(20, 3.2), (14.2, 2.6), (9.5, 2)]:
        d.shape("gold", circle(100, y, r), shadow=False, spot=True)


def marrakech(d: Drawing):
    d.disc("glow", 152, 78, 18)
    # the snowy High Atlas behind the city
    d.band("far", "M-30 112 L4 96 L22 102 L48 80 L70 96 L92 86 L116 98 L140 78 L166 94 L188 84 L230 100")
    d.shape("light", "M48 80 L56 88 L52 87 L48 91 L44 87 L40 88Z M140 78 L149 87 L144 86 L140 90 L136 86 L131 87Z "
                     "M188 84 L196 91 L191 90 L187 93 L183 89 L180 90Z M4 96 L11 102 L6 101 L2 104 L-2 100Z", shadow=False, line=False)
    # rose-pink medina rooftops with a second minaret
    d.band("town", skyline(150, [(-30, 50, 10), (14, 12, 18), (28, 10, 26), (40, 14, 16), (54, 10, 22), (70, 14, 14), (126, 12, 20),
                                 (140, 10, 28), (152, 14, 16), (168, 12, 24), (182, 50, 12)]))
    d.shape("town2", poly((32, 150), (32, 108), (40, 108), (40, 150)))
    d.shape("town2", merlons(32, 108, 8, 2, 3), shadow=False)
    d.shape("tile", rrect(32, 110, 8, 2, 0), shadow=False)
    d.marks("town3", " ".join(rrect(x, 138, 3, 5, 1) for x in (18, 46, 60, 76, 132, 146, 158, 174)))
    group(d, "translate(98 168) scale(.8) translate(-100 -178)", lambda: koutoubia_tower(d))
    palm(d, 56, 168, 52, 118, 1.0, bend=-6)
    palm(d, 146, 170, 150, 124, .9, bend=6)
    palm(d, 168, 172, 172, 136, .7, bend=6)
    # the red ramparts and a horseshoe gate
    d.band("wall", "M-30 166 H230")
    d.shape("wall", merlons(-30, 166, 260, 26, 7), shadow=False)
    d.shape("wall", poly((14, 178), (14, 150), (40, 150), (40, 178)))
    d.shape("wall", merlons(14, 150, 26, 3, 5), shadow=False)
    d.marks("dark", "M21 178 V164 Q21 156 27 156 Q33 156 33 164 V178Z")
    d.stroke("tile", "M18 158 Q27 148 36 158", 1.4, line=False)
    d.band("deep", hills(190, 4, 20), line=False)


MARRAKECH = {"stone": "#D99470", "stone2": "#B06A4A", "tile": "#3BA58B", "gold": "#E8B64A", "leaf": "#4E8A4A",
             "trunk": "#8A5A33", "wall": "#C27048", "town": "#F6D9BF", "town2": "#E7B08C", "town3": "#B77856"}


# ================================================================ CASABLANCA
def casablanca(d: Drawing):
    d.disc("glow", 156, 56, 14)
    d.band("far", skyline(142, [(86, 10, 30), (96, 9, 40), (106, 10, 36), (116, 8, 32), (124, 10, 44), (134, 8, 40), (142, 10, 30), (152, 8, 36), (160, 10, 40), (170, 10, 38), (180, 8, 30), (188, 12, 24), (200, 30, 20)]), line=False)
    # the white city
    d.band("town", skyline(142, [(90, 12, 18), (104, 10, 26), (116, 14, 20), (130, 12, 30), (168, 12, 26), (182, 10, 18), (194, 30, 12)]))
    d.marks("town2", " ".join(rrect(x, y, 2.4, 3, .5) for x, y in [(93, 128), (98, 128), (107, 120), (111, 120), (119, 126), (124, 126),
                                                                    (133, 116), (138, 116), (171, 120), (176, 120), (185, 128)]))
    # Casablanca Twin Center
    for x, top in [(140, 78), (154, 82)]:
        d.shape("tw", poly((x, 142), (x, top + 8), (x + 6, top), (x + 12, top + 8), (x + 12, 142)))
        d.shape("tw2", poly((x + 7, 142), (x + 7, top + 1.4), (x + 12, top + 8), (x + 12, 142)), shadow=False, line=False)
        floors(d, "tw2", x, x + 7, top + 10, 142, 6)
    # the Atlantic
    d.band("near", waves(144, 1.6, 18))
    # Hassan II Mosque on its platform over the sea
    d.shape("stone", poly((22, 156), (26, 148), (150, 148), (154, 156)))
    d.marks("stone2", " ".join(round_arch(30 + i * 9, 150, 5, 6) for i in range(13)))
    d.shape("stone", rrect(64, 126, 80, 22, 1))
    d.shape("tile", poly((62, 128), (70, 120), (138, 120), (146, 128)), spot=True)
    d.marks("stone2", " ".join(pointed_arch(70 + i * 10, 133, 5, 13) for i in range(7)))
    # the minaret, the tallest in Africa
    d.shape("stone", poly((48, 148), (48, 36), (66, 36), (66, 148)))
    d.shape("stone2", poly((60, 148), (60, 36), (66, 36), (66, 148)), shadow=False, line=False)
    for y in (48, 84, 120):
        d.shape("tile", rrect(51, y, 12, 20, 1), shadow=False, spot=True)
        d.marks("stone", pointed_arch(54, y + 4, 6, 14))
    d.shape("stone", poly((51, 36), (51, 24), (63, 24), (63, 36)))
    d.shape("tile", dome(57, 24, 5.4, 5), shadow=False)
    d.stroke("gold", "M57 19 V8", 1.4)
    for y, r in [(15, 2.2), (11, 1.7)]:
        d.shape("gold", circle(57, y, r), shadow=False)
    # breaking surf
    d.stroke("light", "M14 162 q6 -4 12 0 q6 -4 12 0 M120 164 q6 -4 12 0 q6 -4 12 0 M64 172 q6 -4 12 0 q6 -4 12 0 q6 -4 12 0", 2)
    d.band("deep", waves(184, 2.4, 30), line=False)


CASA = {"stone": "#D8BE92", "stone2": "#AE946A", "tile": "#2E8A6E", "gold": "#E1B04A", "town": "#FFFFFF", "town2": "#9FB3C6",
        "tw": "#7D93AA", "tw2": "#5E7489"}


# ================================================================ CAPE TOWN
TABLE = ("M-30 118 L4 108 L16 92 L26 76 L34 88 L44 76 L50 68 H144 L150 72 L156 92 L166 100 L230 112")
LIONS_HEAD = "M140 132 Q150 112 164 102 Q168 88 176 86 Q184 86 186 98 Q196 112 216 132Z"
TABLECLOTH = ("M46 70 C46 63 54 61 60 63 C64 58 74 58 78 62 C84 57 94 58 98 62 C104 57 114 58 118 62 C124 58 134 59 138 63 "
              "C144 61 150 64 148 71 L150 76 C148 80 145 78 144 84 C142 80 139 80 138 88 C136 82 133 82 132 78 "
              "L60 76 C56 76 52 82 50 76 Z")


def cape_town(d: Drawing):
    d.disc("glow", 162, 44, 12)
    d.band("near", TABLE)
    d.shape("light", TABLECLOTH)
    d.shape("deep", LIONS_HEAD)
    d.band("mid", hills(124, 6, 10))
    # the city bowl's towers
    d.band("far", skyline(138, [(-30, 60, 4), (34, 8, 10), (44, 7, 16), (54, 9, 22), (64, 8, 30), (74, 9, 24), (86, 10, 34),
                                (98, 9, 44, 4), (110, 10, 30), (122, 8, 22), (132, 10, 14), (144, 9, 8), (156, 80, 4)]))
    block(d, 64, 72, 106, 138, "tw", "tw2")
    block(d, 96, 106, 92, 138, "tw", "tw2")
    d.stroke("tw2", "M101 92 V84", 1.2)
    block(d, 112, 120, 110, 138, "tw", "tw2")
    # V&A Waterfront harbour
    d.band("water", waves(140, 1.4, 20))
    d.shape("pier", "M14 148 H76 V152 H14Z")
    d.shape("pop", poly((30, 148), (30, 128), (32, 124), (34, 120), (36, 124), (38, 128), (38, 148)), spot=True)
    d.marks("light", circle(34, 132, 2.2))
    d.shape("pop2", poly((29, 128), (34, 118), (39, 128)), shadow=False)
    sailboat(d, 128, 166, 1.0, "light", "hull")
    sailboat(d, 160, 156, .7, "light", "hull")
    glints(d, [(84, 152, 14), (40, 164, 16), (100, 176, 14), (150, 172, 12)])
    d.band("deep", waves(186, 2.4, 30), line=False)


CAPE = {"tw": "#7E8C9A", "tw2": "#626F7D", "water": "#3E86A8", "pier": "#C9A27A", "pop2": "#8E2C22", "hull": "#2B3E50"}


# ================================================================ JOHANNESBURG
def jacaranda(d: Drawing, x, base, s=1.0):
    d.limb("trunk", f"M{x} {base} L{x} {base - 14 * s} M{x} {base - 10 * s} L{x - 6 * s} {base - 18 * s} M{x} {base - 12 * s} L{x + 7 * s} {base - 19 * s}", 2.6 * s)
    blobs = [(-9, -20, 8), (0, -26, 9), (9, -20, 8), (-4, -16, 7), (5, -15, 7)]
    d.shape("jac", " ".join(circle(x + dx * s, base + dy * s, r * s) for dx, dy, r in blobs), spot=True)
    d.marks("jac2", " ".join(circle(x + dx * s, base + dy * s, 1.6 * s) for dx, dy in [(-7, -22), (3, -29), (8, -18), (-2, -14)]))


def johannesburg(d: Drawing):
    d.disc("glow", 152, 60, 16)
    # a golden mine dump on the edge of town
    d.shape("dump", "M-30 150 L-30 120 L-6 114 L34 116 L54 150Z")
    d.stroke("dump2", "M-6 120 H32 M-10 128 H38", 1.2, line=False)
    d.band("far", skyline(150, [(40, 8, 38), (98, 8, 46), (108, 6, 34), (140, 8, 54, 0, 6), (150, 7, 40), (160, 9, 46), (172, 8, 30), (182, 10, 22)]), line=False)
    d.band("mid", skyline(150, [(36, 10, 24), (60, 8, 30), (94, 10, 34), (132, 9, 28), (146, 10, 36), (164, 10, 24), (176, 12, 16)]))
    # Carlton Centre: the tall dark slab
    block(d, 108, 126, 48, 150, "dark2", "dark3")
    mullions(d, "dark3", 108, 120, 50, 150, 3.2)
    # Ponte City: the hollow cylinder with its crown ring
    d.shape("tw", poly((72, 150), (72, 72), (94, 72), (94, 150)))
    d.shape("tw", ellipse(83, 72, 11, 2.4), shadow=False)
    d.shape("tw2", poly((88, 150), (88, 72), (94, 72), (94, 150)), shadow=False, line=False)
    d.shape("crown", rrect(72, 73, 22, 7, 0), shadow=False, spot=True)
    floors(d, "tw2", 72, 88, 82, 150, 6)
    # Hillbrow Tower: tapering shaft, the stacked pod and the mast
    d.shape("tw", "M51 150 L54 58 H62 L65 150Z")
    d.shape("tw", rrect(50, 40, 16, 20, 2), spot=True)
    for y in (44, 50, 56):
        d.stroke("tw2", f"M50 {y} H66", 1.4, line=False)
    d.shape("tw", poly((54, 40), (55, 30), (61, 30), (62, 40)))
    d.stroke("tw2", "M58 30 V14", 1.6)
    d.shape("tw2", "M60 60 H62 L65 150 H61Z", shadow=False, line=False)
    # Nelson Mandela Bridge
    d.band("near", "M-30 158 H230")
    pylons = [(70, 104), (136, 120)]
    for px, top in pylons:
        fan = " ".join(f"M{px} {top + 3 + i * 4} L{px + k * (14 + i * 11)} 156" for k in (-1, 1) for i in range(4))
        d.stroke("cable", fan, .9)
    d.shape("deck", "M-30 154 H230 V159 H-30Z")
    for px, top in pylons:
        d.shape("deck", poly((px - 2.2, 170), (px - 1.4, top), (px + 1.4, top), (px + 2.2, 170)), spot=True)
    jacaranda(d, 24, 176, 1.1)
    jacaranda(d, 176, 178, 1.0)
    d.band("deep", hills(186, 3, 20), line=False)


JOBURG = {"tw": "#85827C", "tw2": "#66635E", "dark2": "#5B6878", "dark3": "#465363", "crown": "#C8553D", "dump": "#D9B65A", "dump2": "#B8963A",
          "deck": "#FFFFFF", "cable": "#F2F2F2", "jac": "#9B7BC8", "jac2": "#C3AAE6", "trunk": "#5E4636"}


# ================================================================ NAIROBI
def nairobi(d: Drawing):
    d.disc("glow", 150, 84, 22)
    d.band("far", skyline(130, [(40, 8, 20), (50, 7, 28), (60, 8, 22), (138, 8, 30), (148, 7, 22), (158, 9, 16)]), line=False)
    d.band("mid", skyline(130, [(34, 10, 12), (46, 8, 18), (100, 8, 34), (140, 10, 24), (152, 9, 14)]))
    # Times Tower
    block(d, 92, 102, 74, 130, "tw3", "tw4")
    # UAP Old Mutual Tower with its sloping cap
    d.shape("tw3", poly((126, 130), (126, 66), (138, 58), (138, 130)))
    d.shape("tw4", poly((133, 130), (133, 61.3), (138, 58), (138, 130)), shadow=False, line=False)
    d.stroke("tw4", "M138 58 V48", 1.2)
    # Britam Tower: the tall slanted prism
    d.shape("tw", poly((108, 130), (108, 54), (121, 36), (122, 130)))
    d.shape("tw2", poly((116, 130), (116, 43), (121, 36), (122, 130)), shadow=False, line=False)
    d.stroke("tw2", "M121 36 V24", 1.2)
    floors(d, "tw2", 108, 116, 58, 130, 6)
    # KICC: the cylinder with its saucer crown and the conical amphitheatre
    d.shape("kicc", "M54 130 Q60 112 70 104 Q80 112 86 130Z", spot=True)
    d.stroke("kicc2", "M60 122 Q70 118 80 122 M64 114 Q70 111 76 114", 1.1, line=False)
    d.shape("kicc", poly((74, 130), (74, 78), (88, 78), (88, 130)))
    d.shape("kicc2", poly((84, 130), (84, 78), (88, 78), (88, 130)), shadow=False, line=False)
    mullions(d, "kicc2", 74, 84, 80, 130, 3)
    d.shape("kicc", "M68 78 Q70 72 81 71 Q92 72 94 78Z")
    d.shape("kicc2", rrect(70, 70, 22, 2.2, 1), shadow=False)
    d.stroke("kicc2", "M81 70 V64", 1.2)
    # the national park in front
    d.band("ground", "M-30 132 Q100 128 230 132")
    acacia(d, -78, 18, .9)
    group(d, "translate(104 64) scale(.62)", lambda: d.shape("dark", GIRAFFE))
    group(d, "translate(150 98) scale(.42)", lambda: d.shape("dark", GIRAFFE))
    d.stroke("dark", "M20 168 l2 -6 M24 168 l0 -7 M28 168 l-2 -6 M176 160 l2 -6 M180 160 l0 -7", 1.2)
    d.band("near", hills(180, 5, 10))
    d.band("deep", hills(192, 3, 30), line=False)


NAIROBI = {"tw": "#7792AD", "tw2": "#5A7591", "tw3": "#9AA7B4", "tw4": "#7A8796", "kicc": "#C2703F", "kicc2": "#97532D"}


# ================================================================ LAGOS
def lagos(d: Drawing):
    d.disc("glow", 52, 60, 14)
    d.band("far", skyline(136, [(40, 8, 26), (50, 7, 34), (96, 8, 40), (106, 7, 30), (160, 8, 38), (170, 9, 28), (182, 8, 20)]), line=False)
    d.band("mid", skyline(136, [(34, 10, 16), (46, 8, 22), (90, 9, 26), (104, 10, 18), (150, 9, 26), (164, 10, 18), (178, 10, 12)]))
    # NECOM House with its telecom mast
    block(d, 58, 70, 74, 136, "tw3", "tw4")
    d.stroke("tw4", "M64 74 V44 M60.5 54 H67.5 M61.5 62 H66.5", 1.3)
    floors(d, "tw4", 58, 66, 78, 136, 5)
    # Union Bank tower
    block(d, 74, 86, 84, 136, "tw", "tw2")
    mullions(d, "tw2", 74, 82, 86, 136, 3)
    # Civic Towers: angled glass crown
    d.shape("glass", poly((118, 136), (118, 74), (132, 64), (132, 136)))
    d.shape("glass2", poly((127, 136), (127, 67.6), (132, 64), (132, 136)), shadow=False, line=False)
    floors(d, "glass2", 118, 127, 76, 136, 5)
    block(d, 136, 146, 88, 136, "tw3", "tw4")
    # the lagoon
    d.band("near", waves(136, 1.4, 18))
    # Lekki-Ikoyi Link Bridge with a yellow danfo bus
    px, top, deck = 152, 62, 154
    fan = " ".join(f"M{px} {top + 4 + i * 5} L{px + k * (16 + i * 13)} {deck}" for k in (-1, 1) for i in range(6))
    d.stroke("cable", fan, .9)
    d.shape("deck", f"M-30 {deck} Q100 {deck - 4} 230 {deck} V{deck + 5} Q100 {deck + 1} -30 {deck + 5}Z")
    d.shape("deck", poly((px - 3, 176), (px - 2, top), (px + 2, top), (px + 3, 176)), spot=True)
    d.shape("danfo", rrect(58, 138, 30, 13, 3), spot=True)
    d.marks("dark", rrect(58, 145, 30, 1.8, 0))
    d.marks("glass2", " ".join(rrect(61 + i * 6.2, 140.5, 4.6, 3.6, .6) for i in range(4)))
    d.marks("dark", circle(65, 151, 2.6) + circle(81, 151, 2.6))
    glints(d, [(20, 166, 14), (70, 172, 18), (120, 168, 14), (168, 176, 12)])
    d.band("deep", waves(184, 2.4, 30), line=False)


LAGOS = {"tw": "#6A8098", "tw2": "#50657C", "tw3": "#85827C", "tw4": "#66635E", "glass": "#5E8FB0", "glass2": "#467492",
         "deck": "#FFFFFF", "cable": "#F2F2F2", "danfo": "#F2C230"}


# ================================================================ ACCRA
def canoe(d: Drawing, x, y, s=1.0, body="hero", stripe="hero2", band="pop"):
    def draw():
        d.shape(body, "M-28 -7 Q-14 2 0 2 Q14 2 28 -7 L24 2 Q0 10 -24 2Z", spot=True)
        d.stroke(stripe, "M-23 0 Q0 7 23 0", 1.6, line=False)
        d.stroke(band, "M-22 3 Q0 9 22 3", 1.2, line=False)
    group(d, f"translate({x} {y}) scale({s})", draw)


def star5(cx, cy, r, ri=.42) -> str:
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * ri
        pts.append((round(cx + rr * math.cos(a), 2), round(cy + rr * math.sin(a), 2)))
    return poly(*pts)


def accra(d: Drawing):
    d.disc("glow", 100, 70, 20)
    d.band("far", skyline(146, [(14, 10, 70), (40, 9, 74), (60, 10, 62), (130, 10, 64), (150, 8, 76), (160, 9, 66), (172, 8, 56), (182, 10, 40)]), line=False)
    d.band("mid", skyline(146, [(18, 12, 56), (32, 14, 58), (46, 12, 60), (58, 12, 58), (70, 14, 54), (84, 10, 56), (94, 12, 52), (106, 12, 56),
                                (118, 10, 54), (128, 14, 58), (142, 10, 52), (166, 10, 36), (180, 10, 24)]))
    # World Trade Center Accra
    block(d, 148, 162, 82, 146, "tw", "tw2")
    floors(d, "tw2", 148, 157, 86, 146, 6)
    # Jamestown Lighthouse, red and white
    d.shape("light", poly((28, 146), (31, 82), (39, 82), (42, 146)))
    for y0, y1 in [(82, 98), (110, 120), (130, 140)]:
        k0, k1 = (146 - y0) / 64 * 3, (146 - y1) / 64 * 3
        d.shape("lred", poly((28 + k0, y0), (28 + k1, y1), (42 - k1, y1), (42 - k0, y0)), shadow=False, spot=True)
    d.shape("lred", rrect(29, 78, 12, 4, 1))
    d.shape("light", rrect(31, 70, 8, 8, 1))
    d.shape("lred", "M30 70 Q35 62 40 70Z")
    # Independence Square: the Black Star Gate
    d.shape("ground", "M20 150 L26 144 H178 L184 150Z")
    gate = (f"M58 146 V100 H142 V146 H120 V122 A20 18 0 0 0 80 122 V146Z "
            f"M64 146 V128 A5 5 0 0 1 74 128 V146Z M126 146 V128 A5 5 0 0 1 136 128 V146Z")
    d.shape("gate", "M56 100 H144 V146 H56Z")
    d.marks("sky", "M80 146 V122 A20 18 0 0 1 120 122 V146Z")
    d.marks("gate2", "M64 146 V128 A5 5 0 0 1 74 128 V146Z M126 146 V128 A5 5 0 0 1 136 128 V146Z")
    d.raw("", "")  # keep layer order explicit
    d.shape("gate", rrect(52, 96, 96, 6, 1), shadow=False)
    d.stroke("gate2", "M56 108 H144 M100 102 V104", 1.2, line=False)
    d.shape("gate", poly((90, 96), (92, 88), (108, 88), (110, 96)))
    d.shape("star", star5(100, 72, 15), spot=True)
    _ = gate
    # the beach and painted fishing canoes
    d.band("near", waves(156, 1.6, 20))
    canoe(d, 58, 172, 1.0, "hero", "hero2", "pop")
    canoe(d, 136, 166, .8, "pop", "hero2", "hero")
    glints(d, [(20, 166, 12), (92, 180, 16), (160, 178, 12)])
    d.band("deep", waves(188, 2.4, 30), line=False)


ACCRA = {"gate": "#ECE5D7", "gate2": "#C3B9A6", "star": "#1E1E22", "lred": "#D2412F", "tw": "#6A8098", "tw2": "#50657C"}


# ================================================================ AMMAN
def hill_town(y_of, x0, x1, widths, heights) -> str:
    """Band edge: little cube houses stacked along a hillside curve y_of(x)."""
    out = f"M-30 {y_of(-30):.1f} L{x0} {y_of(x0):.1f}"
    x, i = x0, 0
    while x < x1:
        w = widths[i % len(widths)]
        h = heights[i % len(heights)]
        y = y_of(x + w / 2) - h
        out += f" V{y:.1f} H{x + w:.1f}"
        x += w
        i += 1
    return out + f" V{y_of(x):.1f} L230 {y_of(230):.1f}"


def amman(d: Drawing):
    d.disc("glow", 64, 52, 13)
    far_y = lambda x: 112 - 14 * math.sin((x + 20) / 60)
    d.band("far", hill_town(far_y, -10, 210, [7, 9, 6, 8, 10, 7], [6, 9, 5, 8, 7, 10]), line=False)
    # Abdali towers in the distance
    block(d, 170, 178, 66, 110, "far2", "far2", line=False)
    # Raghadan flagpole
    d.stroke("pole", "M150 132 V38", 1.6)
    d.shape("fl1", "M150 38 Q158 36 168 40 V45 Q158 41 150 43Z", shadow=False)
    d.shape("fl2", "M150 43 Q158 41 168 45 V50 Q158 46 150 48Z", shadow=False)
    d.shape("fl3", "M150 48 Q158 46 168 50 V55 Q158 51 150 53Z", shadow=False)
    d.shape("fl4", "M150 38 L157 45.5 L150 53Z", shadow=False, spot=True)
    mid_y = lambda x: 132 - 10 * math.sin((x - 10) / 44)
    d.band("mid", hill_town(mid_y, -20, 220, [8, 10, 7, 9, 11, 8], [7, 10, 6, 9, 8, 11]))
    d.marks("mid2", " ".join(rrect(x, mid_y(x) - 6, 2.2, 2.6, .4) for x in range(-6, 206, 13)))
    # King Abdullah I Mosque: the blue dome
    d.shape("stone", rrect(110, 116, 30, 16, 1))
    d.shape("blue", dome(125, 117, 13, 16), spot=True)
    d.stroke("blue2", "M114 110 Q125 106 136 110", 1, line=False)
    d.stroke("gold", "M125 101 V94", 1.3)
    minaret(d, 144, 132, 92, 3.6, "stone", "stone2", "gold", rings=2, pencil=True)
    # the Citadel hill and the Temple of Hercules
    d.shape("hill", "M-30 132 L-30 106 Q6 96 34 98 Q58 100 74 132Z")
    d.shape("stone", rrect(6, 98, 50, 5, 1))
    for x in (14, 26, 38):
        d.shape("stone", rrect(x, 66, 6, 33, 1))
        d.shape("stone2", rrect(x + 3.6, 66, 2.4, 33, .5), shadow=False, line=False)
        d.shape("stone", rrect(x - 1.5, 63, 9, 4, 1), shadow=False)
    d.shape("stone", poly((11, 63), (11, 57), (34, 57), (34, 63)))
    d.shape("stone", poly((48, 98), (48, 86), (52, 82), (54, 98)))
    # the Roman Theatre carved into the hill
    d.shape("stone", "M24 140 Q100 122 176 140 L162 172 Q100 160 38 172Z")
    d.stroke("stone2", " ".join(f"M{24 + i * 3.1:.1f} {140 + i * 6.4:.1f} Q100 {122 + i * 7.2:.1f} {176 - i * 3.1:.1f} {140 + i * 6.4:.1f}" for i in range(1, 5)), 1.3)
    d.marks("stone2", poly((96, 128), (104, 128), (106, 170), (94, 170)))
    d.shape("stone", rrect(40, 170, 120, 8, 1))
    d.marks("stone2", " ".join(rrect(46 + i * 10, 172, 3, 6, .5) for i in range(11)))
    d.band("deep", hills(190, 3, 20), line=False)


AMMAN = {"stone": "#D9A85E", "stone2": "#A87A38", "hill": "#8C6E4A", "blue": "#3F7FB5", "blue2": "#2D6596", "gold": "#E1B04A",
         "pole": "#8A8F96", "fl1": "#1E1E22", "fl2": "#FFFFFF", "fl3": "#2E8A4E", "fl4": "#D2412F", "far2": "#00000000", "mid2": "#00000022"}


# ================================================================ RIYADH
def riyadh(d: Drawing):
    d.disc("glow", 54, 64, 15)
    d.band("far", skyline(150, [(20, 8, 30), (30, 7, 40), (40, 9, 26), (104, 8, 34), (148, 8, 44), (158, 7, 32, 5), (168, 9, 40), (180, 8, 26)]), line=False)
    d.band("mid", skyline(150, [(16, 10, 18), (28, 9, 24), (100, 10, 26), (110, 8, 18), (152, 10, 22), (166, 9, 30), (180, 10, 16)]))
    # Kingdom Centre: the "bottle opener" with its sky bridge
    d.shape("glass", "M64 150 C64 96 70 56 76 24 C78 50 81 70 84 70 C87 70 90 50 92 24 C98 56 104 96 104 150Z", spot=True)
    d.shape("glass2", "M92 24 C98 56 104 96 104 150 H94 C94 110 92 70 90 50Z", shadow=False, line=False)
    d.shape("glass", rrect(76.5, 44, 15, 3, .8), shadow=False)
    floors(d, "glass2", 66, 94, 76, 150, 6)
    # Al Faisaliah Tower with its golden globe
    d.shape("tw", poly((116, 150), (127, 78), (131, 78), (142, 150)))
    d.shape("tw2", poly((129, 150), (129, 78), (131, 78), (142, 150)), shadow=False, line=False)
    d.stroke("tw2", "M121 120 L137 120 M118 136 L140 136 M124 100 H134", 1, line=False)
    d.shape("gold", circle(129, 72, 7), spot=True)
    d.shape("tw", poly((127.6, 66), (129, 36), (130.4, 66)))
    # Masmak fort, mud brick with tapering towers
    d.shape("mud", "M96 168 L98 146 H156 L158 168Z")
    for x, top in [(94, 128), (152, 130), (122, 134)]:
        d.shape("mud", poly((x - 3, 168), (x - 1, top), (x + 9, top), (x + 11, 168)))
        d.shape("mud", " ".join(poly((x - 1 + i * 3.6, top), (x + .8 + i * 3.6, top - 4), (x + 2.6 + i * 3.6, top)) for i in range(3)), shadow=False)
        d.marks("mud2", rrect(x + 2.5, top + 6, 3, 5, 1))
    d.shape("mud2", " ".join(poly((100 + i * 4.4, 146), (102 + i * 4.4, 142), (104 + i * 4.4, 146)) for i in range(12)), shadow=False)
    d.marks("dark", "M120 168 V158 Q125 152 130 158 V168Z")
    palm(d, 30, 172, 26, 128, 1.0, bend=-6)
    palm(d, 178, 172, 180, 136, .8, bend=6)
    d.band("ground", "M-30 168 Q60 160 120 166 T230 164")
    d.band("dune", "M-30 182 Q50 172 110 178 T230 176", line=False)


RIYADH = {"glass": "#7896B0", "glass2": "#5A7892", "tw": "#7D8896", "tw2": "#606B79", "gold": "#E5B548", "mud": "#A87648",
          "mud2": "#7E5530", "leaf": "#4E8A4A", "trunk": "#8A5A33", "dune": "#D9A05A"}


# ================================================================ SYDNEY
def shell(fx, bx, base, tx, ty) -> str:
    h = base - ty
    return (f"M{fx} {base} C{fx} {base - h * .5} {tx + (fx - tx) * .35} {ty + h * .2} {tx} {ty} "
            f"C{tx + (bx - tx) * .62} {ty + h * .04} {bx} {ty + h * .42} {bx} {base}Z")


def shell_rib(fx, bx, base, tx, ty) -> str:
    h = base - ty
    mx = fx + (bx - fx) * .42
    return f"M{tx} {ty} C{tx + (bx - tx) * .3} {ty + h * .2} {mx} {base - h * .45} {mx} {base}"


def opera_house(d: Drawing):
    """Sydney Opera House side-on: podium y 126..144, x 18..184."""
    d.shape("podium", "M18 144 L24 126 H170 L184 144Z")
    d.shape("dark", "M24 126 H170 L172 130 H23Z", shadow=False)
    for s in [(150, 172, 127, 146, 100), (164, 180, 127, 158, 108)]:
        d.shape("shell2", shell(*s))
    for s in [(150, 124, 127, 156, 70), (88, 126, 127, 84, 52), (78, 106, 127, 72, 72), (70, 90, 127, 62, 92)]:
        d.shape("shell2", shell(*s))
    for s in [(124, 96, 127, 130, 78), (60, 104, 127, 54, 44), (48, 82, 127, 40, 68), (38, 64, 127, 30, 92)]:
        d.shape("shell", shell(*s))
        d.stroke("shell2", shell_rib(*s), 1.6, line=False)


def arch_bridge(d: Drawing, cx, half, deck_y, crown, bearing, steel="steel", pylon="pylon", lattice="sky"):
    xl, xr = cx - half, cx + half
    top_end = deck_y - 10
    depth = 7
    a = (f"M{xl} {bearing} Q{cx} {2 * (crown + depth) - bearing} {xr} {bearing} "
         f"L{xr - 4} {top_end} Q{cx} {2 * crown - top_end} {xl + 4} {top_end}Z")
    d.shape(steel, a)
    pts = []
    n = 14
    for i in range(n + 1):
        t = i / n
        x = xl + 4 + (xr - xl - 8) * t
        u = (x - cx) / (half - 4)
        y_top = crown + (top_end - crown) * u * u
        ub = (x - cx) / half
        y_bot = crown + depth + (bearing - crown - depth) * ub * ub
        pts.append((x, y_top + 2 if i % 2 == 0 else y_bot - 2))
    d.stroke(lattice, "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts), 1.2, line=False)
    hs = []
    for i in range(-4, 5):
        x = cx + i * half / 5.2
        ub = (x - cx) / half
        y_bot = crown + depth + (bearing - crown - depth) * ub * ub
        if y_bot < deck_y - 2:
            hs.append(f"M{x:.1f} {y_bot:.1f} V{deck_y}")
    d.stroke(steel, " ".join(hs), 1.1)
    d.shape(steel, f"M-30 {deck_y} H{xr + 30} V{deck_y + 4} H-30Z")
    pw = half * .2
    ptop = deck_y - 24
    for px in (xl - pw * .1, xr + pw * .1):
        d.shape(pylon, f"M{px - pw / 2} {bearing + 20} V{ptop + 3} L{px - pw / 2 + 1.5} {ptop} H{px + pw / 2 - 1.5} L{px + pw / 2} {ptop + 3} V{bearing + 20}Z")


def sydney(d: Drawing):
    d.disc("glow", 162, 50, 12)
    d.band("far", skyline(128, [(60, 8, 30), (70, 7, 40), (80, 9, 34), (118, 8, 44), (128, 7, 30), (138, 9, 22)]), line=False)
    # Sydney Tower: golden turret on a slim shaft
    d.shape("tower", poly((100, 128), (101, 52), (105, 52), (106, 128)))
    d.stroke("tower", "M103 34 V22", 1.4)
    d.shape("gold", "M95 52 V42 Q95 36 103 35 Q111 36 111 42 V52 Q103 55 95 52Z", spot=True)
    d.stroke("gold2", "M95 45 H111 M95 49 H111", 1, line=False)
    d.band("mid", skyline(128, [(56, 10, 20), (68, 9, 28), (80, 10, 36), (92, 8, 24), (110, 9, 32), (122, 10, 24), (136, 10, 16), (150, 10, 10)]))
    arch_bridge(d, 40, 46, deck_y=110, crown=84, bearing=128)
    d.band("near", waves(128, 1.4, 18))
    group(d, "translate(98 66) scale(.52)", lambda: opera_house(d))
    # a harbour ferry
    d.shape("ferry", "M36 160 H72 L68 167 H40Z")
    d.shape("light", rrect(42, 151, 24, 9, 2))
    d.shape("ferry2", rrect(48, 147, 12, 4.4, 1.2), shadow=False, spot=True)
    glints(d, [(88, 150, 14), (130, 160, 16), (20, 172, 12), (96, 174, 18)])
    d.band("deep", waves(184, 2.4, 30), line=False)


SYDNEY = {"shell": "#FFFFFF", "shell2": "#E2DCCF", "podium": "#C99A74", "steel": "#6F7D8C", "pylon": "#DCC7A1", "tower": "#8E9AA7",
          "gold": "#E2B24A", "gold2": "#B68A2C", "ferry": "#2E7D4F", "ferry2": "#F2C14E"}


# ================================================================ MELBOURNE
def melbourne(d: Drawing):
    d.disc("glow", 52, 62, 14)
    d.band("far", skyline(138, [(64, 8, 40), (74, 7, 52), (84, 9, 44), (136, 8, 36), (146, 9, 48), (170, 8, 30), (180, 9, 22)]), line=False)
    d.band("mid", skyline(138, [(60, 10, 26), (72, 8, 34), (84, 9, 28), (130, 9, 30), (166, 10, 22), (178, 10, 16)]))
    # Eureka Tower with its gold crown
    d.shape("tw", poly((94, 138), (94, 38), (100, 38), (100, 32), (108, 32), (108, 138)))
    d.shape("gold", poly((94, 56), (94, 38), (100, 38), (100, 32), (108, 32), (108, 56)), shadow=False, spot=True)
    d.stroke("tw", "M98 50 H108 M98 44 H108", 1, line=False)
    d.shape("tw2", poly((103, 138), (103, 56), (108, 56), (108, 138)), shadow=False, line=False)
    d.marks("pop", rrect(94, 58, 14, 3, 0))
    # Australia 108 and its golden starburst
    d.shape("tw3", "M112 138 V36 Q118 26 124 28 L126 138Z")
    d.shape("gold", "M124 66 L131 70 L124 74 Z M112 66 L108 70 L112 74Z", shadow=False)
    d.shape("gold", rrect(111, 66, 15, 8, 2), shadow=False)
    d.shape("tw4", "M121 30 Q123 28 124 28 L126 138 H121Z", shadow=False, line=False)
    # Arts Centre spire
    d.stroke("spire2", "M154 54 V30", 1.4)
    d.shape("spire", "M140 138 Q148 128 151 100 L153 54 H155 L157 100 Q160 128 168 138Z", spot=True)
    d.stroke("spire2", "M146 132 L162 132 M149 122 L159 122 M151 110 L157 110 M152 96 L156 96 M150 132 L156 104 L152 76 M158 132 L152 104 L156 76", .9, line=False)
    # Flinders Street Station on the north bank
    d.shape("ochre", rrect(24, 120, 68, 30, 1))
    d.marks("ochre2", " ".join(round_arch(28 + i * 8.6, 128, 5, 10) for i in range(8)))
    d.shape("ochre", rrect(42, 108, 22, 14, 1))
    d.shape("copper", dome(53, 109, 11, 15), spot=True)
    d.shape("ochre", rrect(50.5, 89, 5, 6, 1))
    d.shape("copper", dome(53, 90, 2.6, 4), shadow=False)
    d.shape("ochre", rrect(76, 98, 10, 24, 1))
    d.shape("copper", poly((75, 98), (81, 88), (87, 98)))
    d.marks("light", circle(81, 106, 3))
    d.stroke("ochre2", "M81 104 V106 H82.6", .8, line=False)
    # the Yarra and a rowing eight
    d.band("near", waves(150, 1.4, 18))
    d.shape("hull", "M98 168 H176 Q172 172 164 172 H104 Q100 171 98 168Z")
    d.stroke("dark", " ".join(f"M{110 + i * 8} 166 L{104 + i * 8} 176" for i in range(8)), 1.1)
    d.marks("dark", " ".join(circle(111 + i * 8, 164, 2) for i in range(8)))
    glints(d, [(24, 162, 14), (50, 176, 16), (150, 180, 14)])
    d.band("deep", waves(186, 2.4, 30), line=False)


MELB = {"tw": "#6C7D90", "tw2": "#53637A", "tw3": "#7D8896", "tw4": "#606B79", "gold": "#E4B44C", "spire": "#F4F1EA", "spire2": "#B8B2A6",
        "ochre": "#E3A64A", "ochre2": "#B67A2A", "copper": "#5E9E86", "hull": "#C8553D"}


# ================================================================ BRISBANE
def brisbane(d: Drawing):
    d.disc("glow", 156, 52, 13)
    d.band("far", skyline(138, [(70, 8, 36), (80, 7, 50), (140, 8, 44), (150, 7, 56), (160, 9, 40), (172, 8, 26)]), line=False)
    d.band("mid", skyline(138, [(62, 10, 22), (74, 8, 30), (134, 9, 36), (146, 10, 28), (160, 10, 20), (176, 12, 12)]))
    # City Hall clock tower
    d.shape("sand", rrect(80, 82, 12, 56, 1))
    d.shape("sand", rrect(78, 78, 16, 6, 1), shadow=False)
    d.marks("light", circle(86, 90, 3.4))
    d.shape("sand", dome(86, 78, 6, 9))
    d.shape("sand", rrect(84.4, 64, 3.2, 6, .8), shadow=False)
    d.stroke("sand2", "M86 64 V58 M89 82 V138", 1.1)
    # 1 William Street, Brisbane Skytower and Infinity
    d.shape("tw", poly((98, 138), (98, 48), (110, 42), (110, 138)))
    d.shape("tw2", poly((105, 138), (105, 44.5), (110, 42), (110, 138)), shadow=False, line=False)
    d.shape("tw3", "M114 138 V40 Q114 34 120 33 Q126 34 126 40 V138Z")
    d.shape("tw4", poly((122, 138), (122, 33.5), (126, 40), (126, 138)), shadow=False, line=False)
    floors(d, "tw4", 114, 122, 42, 138, 6)
    d.shape("tw", poly((130, 138), (130, 60), (135, 50), (140, 60), (140, 138)))
    d.shape("tw2", poly((135, 138), (135, 50), (140, 60), (140, 138)), shadow=False, line=False)
    # the river
    d.band("near", waves(140, 1.4, 18))
    # Story Bridge: cantilever truss with two tall piers
    top = "M-30 122 L22 90 L50 112 L78 90 L130 122"
    d.shape("steel", top + " V130 H-30Z")
    d.shape("sky", "M-14 124 L22 98 L44 118 Z M56 118 L78 98 L114 124Z", shadow=False, line=False)
    d.stroke("steel", "M-6 124 L4 108 L14 124 L22 98 M22 98 L30 124 L38 116 M62 116 L70 124 L78 98 L86 124 L96 110 L104 124", 1.4, line=False)
    d.shape("steel", "M-30 124 H130 V130 H-30Z", spot=True)
    for x in (22, 78):
        d.shape("pier", rrect(x - 5, 128, 10, 22, 1))
    # Wheel of Brisbane
    d.stroke("wheel", "M164 148 L172 122 L180 148", 2.2)
    d.stroke("wheel", circle(172, 114, 18) + " " + " ".join(f"M172 114 L{172 + 18 * math.cos(i * math.pi / 6):.1f} {114 + 18 * math.sin(i * math.pi / 6):.1f}" for i in range(12)), 1.2)
    d.stroke("wheel", circle(172, 114, 18), 2.2)
    d.marks("pop", " ".join(circle(172 + 18 * math.cos(i * math.pi / 6), 114 + 18 * math.sin(i * math.pi / 6), 1.8) for i in range(12)))
    # a CityCat ferry
    d.shape("light", "M96 166 H146 L140 172 H100Z")
    d.shape("cat", rrect(104, 157, 32, 9, 2), spot=True)
    d.marks("light", " ".join(rrect(107 + i * 6, 159, 4, 3.4, .6) for i in range(5)))
    glints(d, [(30, 160, 14), (60, 176, 16), (156, 170, 14)])
    d.band("deep", waves(186, 2.4, 30), line=False)


BRIS = {"sand": "#D9A85E", "sand2": "#B0803A", "tw": "#6A8098", "tw2": "#50657C", "tw3": "#7D8896", "tw4": "#606B79",
        "steel": "#5F6E7E", "pier": "#C9B48E", "wheel": "#FFFFFF", "cat": "#2E6FA3"}


# ================================================================ PERTH
def perth(d: Drawing):
    d.disc("glow", 160, 54, 13)
    d.band("far", skyline(140, [(70, 8, 40), (80, 7, 30), (146, 8, 46), (156, 7, 36), (166, 9, 28), (178, 8, 20)]), line=False)
    d.band("mid", skyline(140, [(64, 10, 24), (76, 9, 30), (142, 10, 30), (154, 9, 22), (166, 12, 14)]))
    # QV1, Central Park (with its mast) and Brookfield Place
    block(d, 86, 98, 64, 140, "tw3", "tw4")
    d.shape("tw", poly((104, 140), (104, 42), (108, 42), (108, 36), (116, 36), (116, 42), (120, 42), (120, 140)))
    d.shape("tw2", poly((114, 140), (114, 36), (116, 36), (116, 42), (120, 42), (120, 140)), shadow=False, line=False)
    d.stroke("tw2", " ".join(f"M104 {y} L114 {y + 14} M114 {y} L104 {y + 14}" for y in range(46, 136, 14)), .9, line=False)
    d.stroke("tw2", "M112 36 V18", 1.4)
    d.shape("tw3", poly((124, 140), (124, 46), (128, 46), (128, 40), (138, 40), (138, 140)))
    d.shape("tw4", poly((133, 140), (133, 40), (138, 40), (138, 140)), shadow=False, line=False)
    # the Bell Tower: glass spire between copper sails
    d.shape("copper", "M30 146 Q32 116 42 94 L42 146Z M60 146 Q58 116 48 94 L48 146Z", spot=True)
    d.shape("glass", poly((40, 146), (42, 96), (45, 72), (48, 96), (50, 146)))
    d.stroke("glass2", "M45 76 V144 M42 110 H48 M41 128 H49", 1, line=False)
    # the Swan River
    d.band("near", waves(146, 1.4, 18))
    # Elizabeth Quay bridge
    d.limb("deck", "M60 160 C70 128 90 128 102 152", 3.2)
    d.limb("deck", "M88 152 C100 128 120 128 130 160", 3.2)
    d.shape("deck", "M56 158 Q95 146 134 158 V161 Q95 149 56 161Z")
    # a black swan
    d.shape("swan", "M144 176 Q140 164 152 162 Q164 160 176 166 Q168 166 170 170 Q166 178 150 178Z")
    d.limb("swan", "M168 166 Q176 150 168 142 Q164 138 160 142", 3.4)
    d.shape("beak", poly((158, 141), (151, 145), (160, 144)), shadow=False, spot=True)
    d.stroke("light", "M152 168 Q158 164 164 168", 1, line=False)
    glints(d, [(20, 160, 14), (40, 176, 16), (110, 174, 16)])
    d.band("deep", waves(188, 2.4, 30), line=False)


PERTH = {"tw": "#6A8098", "tw2": "#50657C", "tw3": "#7D8896", "tw4": "#606B79", "copper": "#B8703A", "glass": "#BFDCE8",
         "glass2": "#86AFC4", "deck": "#FFFFFF", "swan": "#1E1E24", "beak": "#D7263D"}


# ================================================================ AUCKLAND
def auckland(d: Drawing):
    d.disc("glow", 54, 56, 14)
    # Rangitoto, the low volcano across the harbour
    d.band("far", "M-30 134 L-10 132 Q14 118 32 110 Q44 104 54 110 Q72 120 96 134 H230", line=False)
    d.band("mid", skyline(134, [(66, 10, 20), (78, 8, 30), (106, 12, 36), (122, 9, 26), (134, 10, 18), (146, 10, 10)]))
    # Vero Centre and other towers
    d.shape("tw", "M112 134 V78 Q118 72 126 76 V134Z")
    d.shape("tw2", "M121 134 V74.4 Q124 74.8 126 76 V134Z", shadow=False, line=False)
    block(d, 130, 140, 88, 134, "tw3", "tw4")
    block(d, 74, 84, 92, 134, "tw3", "tw4")
    # Sky Tower
    d.shape("sky1", "M90 134 L92.5 56 H99.5 L102 134Z")
    d.shape("sky2b", "M97 56 H99.5 L102 134 H98Z", shadow=False, line=False)
    d.shape("sky1", rrect(86, 50, 20, 7, 3))
    d.shape("sky1", rrect(84, 42, 24, 8, 3.5), spot=True)
    d.marks("sky2b", rrect(84, 45, 24, 2.4, 1))
    d.shape("sky1", rrect(88, 36, 16, 6, 2.5))
    d.shape("sky1", poly((92, 36), (93, 28), (99, 28), (100, 36)))
    d.stroke("sky2b", "M96 28 V12", 1.6)
    # Harbour Bridge with its arched navigation span
    d.shape("bridge", "M146 128 Q166 112 186 128 H230 V132 H146Z")
    d.stroke("bridge", "M150 129 L156 120 L162 129 L168 117 L174 129 L180 121 L186 129", 1.1, line=False)
    d.stroke("bridge", "M156 132 V140 M182 132 V140 M206 132 V140", 2)
    # the harbour full of sails
    d.band("near", waves(138, 1.4, 18))
    sailboat(d, 44, 168, 1.1, "light", "hull")
    sailboat(d, 128, 160, .9, "light", "hull")
    sailboat(d, 168, 172, .75, "light", "hull")
    d.shape("pop", "M80 152 Q74 140 82 128 Q92 138 88 152Z", spot=True)
    d.stroke("hull", "M82 152 V126", 1.2)
    d.shape("hull", "M72 152 H94 L90 156 H76Z")
    glints(d, [(20, 150, 12), (100, 172, 16), (60, 182, 12), (150, 182, 12)])
    d.band("deep", waves(188, 2.4, 30), line=False)


AUCK = {"sky1": "#B9B5AD", "sky2b": "#8C877E", "tw": "#7891AA", "tw2": "#5B748D", "tw3": "#97A6B6", "tw4": "#76879A",
        "bridge": "#6F8079", "hull": "#2B3E50"}


# ================================================================ concepts
NO_SEA_GOLD = ["coastal", "meadow", "blush", "dusk"]
SKY_FIX = {"sky": ["sky2", "far"], "glow": ["glow2", "light", "pop"], "near": ["deep"], "mid": ["far"], "far": ["sky2", "mid"]}


def C(cid, act, title, fn, palettes=None, overrides=None, checks=(), fixes=None):
    return Concept(cid, act, title, fn, palettes=list(palettes or ["golden", "coastal", "meadow", "blush", "dusk"]),
                   overrides=overrides or {}, checks=list(checks), fixes=fixes if fixes is not None else dict(SKY_FIX))


def fx(**extra):
    return {**SKY_FIX, **extra}


CONCEPTS = [
    C("sky-dubai", "skyline-dubai", "Dubai", dubai, NO_SEA_GOLD, DUBAI,
      [("glass", "sky"), ("glass", "mid"), ("tw", "mid"), ("tw", "sky"), ("sail", "far"), ("steel", "mid"), ("far", "sky"), ("mid", "near")]),
    C("sky-abu-dhabi", "skyline-abu-dhabi", "Abu Dhabi", abu_dhabi, None, ABU,
      [("tw", "sky"), ("tw", "mid"), ("marble", "mid"), ("coin", "sky"), ("marble", "tw"), ("far", "sky")]),
    C("sky-doha", "skyline-doha", "Doha", doha, NO_SEA_GOLD, DOHA,
      [("tw", "sky"), ("tw", "mid"), ("tw3", "mid"), ("stone", "near"), ("far", "sky"), ("mid", "near")]),
    C("sky-tel-aviv", "skyline-tel-aviv", "Tel Aviv", tel_aviv, NO_SEA_GOLD, TELAVIV,
      [("tw", "sky"), ("tw", "mid"), ("stone", "sky"), ("stone", "hill"), ("far", "sky"), ("mid", "near")]),
    C("sky-muscat", "skyline-muscat", "Muscat", muscat, NO_SEA_GOLD, MUSCAT,
      [("rock", "sky"), ("light", "rock2"), ("gold", "light"), ("stone", "rock"), ("light", "near")]),
    C("sky-cairo", "skyline-cairo", "Cairo", cairo, None, CAIRO,
      [("tower", "sky"), ("tower", "near"), ("sand", "sky"), ("sand", "glow"), ("far", "sky"), ("stone", "sky"), ("sail", "near")]),
    C("sky-marrakech", "skyline-marrakech", "Marrakech", marrakech, None, MARRAKECH,
      [("stone", "sky"), ("stone", "far"), ("stone", "town"), ("town", "far"), ("leaf", "far"), ("far", "sky"), ("stone", "glow")],
      fx(far=["near", "mid", "deep"])),
    C("sky-casablanca", "skyline-casablanca", "Casablanca", casablanca, NO_SEA_GOLD, CASA,
      [("stone", "sky"), ("stone", "near"), ("tw", "sky"), ("tw", "town"), ("town", "far"), ("far", "sky")]),
    C("sky-cape-town", "skyline-cape-town", "Cape Town", cape_town, NO_SEA_GOLD, CAPE,
      [("near", "sky"), ("light", "near"), ("deep", "near"), ("far", "mid"), ("tw", "far"), ("tw", "mid"), ("far", "water")],
      fx(far=["sky2", "light"], deep=["dark", "mid"])),
    C("sky-johannesburg", "skyline-johannesburg", "Johannesburg", johannesburg, None, JOBURG,
      [("tw", "sky"), ("tw", "mid"), ("dark2", "mid"), ("dark2", "sky"), ("deck", "mid"), ("deck", "near"), ("far", "sky"), ("dump", "sky")]),
    C("sky-nairobi", "skyline-nairobi", "Nairobi", nairobi, None, NAIROBI,
      [("tw", "sky"), ("tw", "mid"), ("kicc", "mid"), ("kicc", "sky"), ("dark", "ground"), ("dark", "glow"), ("far", "sky"), ("tw", "glow")]),
    C("sky-lagos", "skyline-lagos", "Lagos", lagos, NO_SEA_GOLD, LAGOS,
      [("tw", "mid"), ("tw3", "mid"), ("glass", "mid"), ("tw3", "sky"), ("deck", "near"), ("danfo", "near"), ("far", "sky")]),
    C("sky-accra", "skyline-accra", "Accra", accra, NO_SEA_GOLD, ACCRA,
      [("gate", "mid"), ("star", "glow"), ("tw", "mid"), ("light", "mid"), ("lred", "sky"), ("lred", "mid"), ("far", "sky"), ("mid", "far")]),
    C("sky-amman", "skyline-amman", "Amman", amman, None, AMMAN,
      [("stone", "mid"), ("stone", "sky"), ("blue", "mid"), ("stone", "hill"), ("far", "sky"), ("mid", "far")],
      fx(mid=["near"])),
    C("sky-riyadh", "skyline-riyadh", "Riyadh", riyadh, None, RIYADH,
      [("glass", "sky"), ("glass", "mid"), ("tw", "sky"), ("tw", "mid"), ("gold", "sky"), ("mud", "ground"), ("mud", "mid"), ("far", "sky")]),
    C("sky-sydney", "skyline-sydney", "Sydney", sydney, NO_SEA_GOLD, SYDNEY,
      [("shell", "mid"), ("shell", "near"), ("steel", "sky"), ("steel", "mid"), ("gold", "sky"), ("tower", "sky"), ("far", "sky"), ("mid", "near")]),
    C("sky-melbourne", "skyline-melbourne", "Melbourne", melbourne, NO_SEA_GOLD, MELB,
      [("tw", "sky"), ("tw", "mid"), ("tw3", "mid"), ("spire", "mid"), ("ochre", "mid"), ("ochre", "near"), ("far", "sky")]),
    C("sky-brisbane", "skyline-brisbane", "Brisbane", brisbane, NO_SEA_GOLD, BRIS,
      [("tw", "sky"), ("tw", "mid"), ("tw3", "mid"), ("sand", "mid"), ("sand", "sky"), ("steel", "sky"), ("steel", "mid"), ("wheel", "near"), ("far", "sky")]),
    C("sky-perth", "skyline-perth", "Perth", perth, NO_SEA_GOLD, PERTH,
      [("tw", "sky"), ("tw", "mid"), ("tw3", "mid"), ("glass", "mid"), ("copper", "mid"), ("deck", "near"), ("swan", "near"), ("far", "sky")]),
    C("sky-auckland", "skyline-auckland", "Auckland", auckland, NO_SEA_GOLD, AUCK,
      [("sky1", "sky"), ("tw", "mid"), ("light", "near"), ("far", "sky"), ("bridge", "sky"), ("mid", "near")]),
]
