"""Mapsie Originals: city skylines of Australia, New Zealand, Hawaii, Africa and the Gulf.

One layered skyline per city, built from its signature buildings and setting.
"""
from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group  # noqa: F401
import math


# ================================================================ private helpers
def poly(*pts, close=True) -> str:
    s = "M" + " L".join(f"{x:g} {y:g}" for x, y in pts)
    return s + ("Z" if close else "")


def T(x, base, w, h) -> str:
    """A plain tower standing on `base`."""
    return f"M{x:g} {base:g} V{base - h:g} H{x + w:g} V{base:g}Z"


def towers(base, specs) -> str:
    return " ".join(T(x, base, w, h) for x, w, h in specs)


def floors(d: Drawing, x, top, w, bottom, step=5.0, role="light", wd=1.0, inset=1.6):
    """Floor bands across a tower (papercut only)."""
    ys = []
    y = top + step
    while y < bottom - 1:
        ys.append(f"M{x + inset:.1f} {y:.1f} H{x + w - inset:.1f}")
        y += step
    if ys:
        d.stroke(role, " ".join(ys), wd, line=False)


def ripples(d: Drawing, segs, role="light", w=2.0, line=True):
    d.stroke(role, " ".join(f"M{x} {y} h{n}" for x, y, n in segs), w, line=line)


def birds(d: Drawing, pts, role="dark"):
    s = " ".join(f"M{x} {y} q{3 * k} {-3 * k} {6 * k} 0 q{3 * k} {-3 * k} {6 * k} 0" for x, y, k in pts)
    d.stroke(role, s, 1.6)


def frond(x, y, ang, length, droop, w=0.22) -> str:
    a = math.radians(ang)
    ex, ey = x + length * math.cos(a), y + length * math.sin(a) + droop
    mx, my = (x + ex) / 2, (y + ey) / 2 - droop * .6
    nx, ny = -(ey - y), ex - x
    k = w / 2
    return (f"M{x:.1f} {y:.1f} Q{mx + nx * k:.1f} {my + ny * k:.1f} {ex:.1f} {ey:.1f} "
            f"Q{mx - nx * k * .3:.1f} {my - ny * k * .3:.1f} {x:.1f} {y:.1f}Z")


def palm(d: Drawing, x0, y0, x1, y1, s=1.0, role="dark", trunk="dark", bend=10):
    d.limb(trunk, f"M{x0} {y0} Q{(x0 + x1) / 2 + bend} {(y0 + y1) / 2} {x1} {y1}", 3.6 * s)
    leaves = " ".join(frond(x1, y1, a, L * s, dr * s) for a, L, dr in
                      [(-170, 24, 9), (-130, 20, 4), (-90, 14, -2), (-50, 20, 4), (-10, 24, 9), (150, 18, 11), (30, 18, 11)])
    d.shape(role, leaves)


def sailboat(d: Drawing, x, y, s=1.0, hull="light", sail="light", spot=False):
    """Yacht with mainsail and jib, waterline at y."""
    d.shape(hull, f"M{x - 12 * s:.1f} {y - 4 * s:.1f} H{x + 13 * s:.1f} L{x + 9 * s:.1f} {y:.1f} H{x - 9 * s:.1f}Z")
    d.stroke("dark", f"M{x} {y - 4 * s:.1f} V{y - 34 * s:.1f}", 1.3 * s)
    d.shape(sail, f"M{x + 1.2 * s:.1f} {y - 33 * s:.1f} Q{x + 9 * s:.1f} {y - 18 * s:.1f} {x + 12 * s:.1f} {y - 7 * s:.1f} H{x + 1.2 * s:.1f}Z", spot=spot)
    d.shape(sail, f"M{x - 1.2 * s:.1f} {y - 30 * s:.1f} L{x - 1.2 * s:.1f} {y - 7 * s:.1f} H{x - 11 * s:.1f}Z")


def dhow(d: Drawing, x, y, s=1.0, hull="wood", sail="light", spot=True):
    """Arab dhow with a lateen sail, bow to the left, waterline at y."""
    def draw():
        d.stroke("dark", "M1 -8 L-2 -44", 1.6)
        d.shape(sail, "M-26 -26 L16 -52 Q20 -32 12 -12 Q-6 -16 -26 -26Z", spot=spot)
        d.stroke("dark", "M-28 -25 L18 -53", 1.4)
        d.shape(hull, "M-30 -13 L-16 0 H14 Q21 -3 23 -14 L16 -10 H-14Z")
        d.stroke("wood2", "M-18 -5 H17", 1.2, line=False)
    group(d, f"translate({x} {y}) scale({s})", draw)


def dome(cx, base, r, h=None) -> str:
    """An onion-free hemispherical dome sitting on base."""
    h = r if h is None else h
    return f"M{cx - r:g} {base:g} C{cx - r:g} {base - h * .55:g} {cx - r * .55:g} {base - h:g} {cx:g} {base - h:g} C{cx + r * .55:g} {base - h:g} {cx + r:g} {base - h * .55:g} {cx + r:g} {base:g}Z"


def dots_in_circle(cx, cy, r, step=3.6, dot=0.9) -> str:
    out = []
    j = 0
    y = cy - r + step / 2
    while y < cy + r:
        off = (step / 2) if j % 2 else 0
        x = cx - r + step / 2 + off
        while x < cx + r:
            if (x - cx) ** 2 + (y - cy) ** 2 < (r - 1.4) ** 2:
                out.append(circle(round(x, 1), round(y, 1), dot))
            x += step
        y += step * .86
        j += 1
    return " ".join(out)


def sea(d: Drawing, y, role="far", deep="mid", segs=(), deep_y=184):
    d.band(role, f"M-30 {y} H230")
    if segs:
        ripples(d, segs)
    d.band(deep, waves(deep_y, 3, 32), line=False)


# ================================================================ HOBART
def hobart(d: Drawing):
    d.disc("glow", 158, 50, 12)
    # kunanyi / Mount Wellington, with the dolerite Organ Pipes and the summit mast
    d.band("mid", "M-30 116 Q-6 98 16 78 Q34 54 58 45 Q80 38 104 40 Q126 43 142 58 Q164 80 188 92 Q208 100 230 104")
    d.shape("near", "M50 54 Q70 44 96 44 L98 58 L92 62 L86 58 L80 64 L74 60 L68 66 L62 61 L56 66 L50 62Z", shadow=False, line=False)
    d.stroke("mid", "M56 52 V62 M62 50 V60 M68 48 V63 M74 47 V58 M80 46 V61 M86 45 V56 M92 45 V59", 1.6, line=False)
    d.stroke("dark", "M100 41 V22 M97 28 H103", 1.6)
    d.band("near", "M-30 124 Q20 112 60 118 Q110 108 150 116 Q190 110 230 118")
    # the small city: low blocks and the round Wrest Point tower
    d.shape("deep", towers(140, [(58, 9, 18), (68, 8, 26), (77, 10, 20), (88, 9, 30), (98, 9, 22), (108, 8, 16), (117, 10, 12)]))
    d.shape("deep", "M150 140 V102 H162 V140Z M147 102 H165 V97 Q156 92 147 97Z")
    floors(d, 150, 102, 12, 140, 4.5, "near", 1)
    # Salamanca Place: sandstone warehouses on the quay
    ware = " ".join(f"M{x} 142 V129 L{x + 6.5} 123 L{x + 13} 129 V142Z" for x in (18, 31, 44))
    d.shape("sand", ware)
    d.marks("sand2", " ".join(rrect(x + 4.5, 133, 4, 9, 1.6) for x in (18, 31, 44)))
    sea(d, 141, "far", "mid", [(70, 150, 16), (120, 156, 20), (34, 164, 14), (150, 170, 18), (88, 176, 18)])
    sailboat(d, 106, 166, 1.0, spot=True)
    sailboat(d, 140, 156, .7)


# ================================================================ GOLD COAST
def gold_coast(d: Drawing):
    d.disc("glow", 50, 58, 14)
    d.band("far", hills(126, 6, 30))
    back = [(26, 9, 26), (36, 8, 42), (45, 10, 34), (56, 9, 56), (66, 8, 46), (112, 9, 62), (122, 10, 50), (134, 8, 58),
            (144, 10, 40), (156, 9, 32), (166, 9, 22)]
    d.shape("mid", towers(140, back))
    front = [(72, 11, 38), (110, 12, 66), (124, 10, 30), (138, 12, 44)]
    d.shape("near", towers(140, front))
    for x, w, h in front:
        floors(d, x, 140 - h, w, 140, 5, "mid", 1)
    # Q1: tallest tower, glass crown and needle spire
    d.stroke("near", "M99 40 V14", 1.8)
    d.shape("near", "M91 140 V58 L93 44 Q99 34 105 44 L107 58 V140Z")
    d.shape("light", "M97 58 L98 44 Q99 41 100 44 L101 58Z", shadow=False)
    floors(d, 91, 58, 16, 140, 5, "mid", 1)
    d.band("ground", "M-30 140 Q100 136 230 140")
    d.band("mid", waves(154, 3, 26))
    d.stroke("light", waves(156, 3, 26), 2.4)
    d.band("near", waves(172, 3, 30), line=False)
    d.stroke("light", "M30 166 h14 M120 164 h18 M70 180 h20", 1.8, line=False)
    # beach umbrellas
    for x, role in [(38, "pop"), (160, "hero2")]:
        d.stroke("dark", f"M{x} 150 V140", 1.2)
        d.shape(role, f"M{x - 8} 141 Q{x} 132 {x + 8} 141Z", spot=role == "pop")


# ================================================================ QUEENSTOWN
REMARKABLES = [(16, 90), (40, 80), (62, 62), (80, 52), (98, 50), (118, 44), (136, 52), (160, 64), (186, 76)]


def queenstown(d: Drawing):
    d.disc("glow", 44, 46, 11)
    d.band("far", "M-30 116 L0 104 L16 90 L28 96 L40 80 L50 86 L62 62 L70 70 L80 52 L90 62 L98 50 L108 58 L118 44 L128 56 "
                  "L136 52 L148 70 L160 64 L172 80 L186 76 L200 90 L230 100")
    snow = " ".join(poly((px, py), (px + 6, py + 9), (px + 2, py + 7), (px - 1, py + 10), (px - 4, py + 7), (px - 6, py + 9)) for px, py in REMARKABLES)
    d.shape("light", snow, shadow=False)
    d.band("mid", "M-30 124 Q40 116 100 122 T230 120")  # far shore, Kelvin Heights
    # Lake Wakatipu
    sea(d, 126, "sky2", "far", [(26, 134, 12), (150, 132, 16), (60, 176, 20), (150, 178, 16)])
    # Bob's Peak and the town on the left shore, with the gondola
    d.shape("near", "M-30 62 Q0 62 14 78 Q34 104 58 126 Q74 138 86 146 H-30Z")
    for i, pine in enumerate([(4, 80), (14, 96), (24, 108), (8, 104)]):
        x, y = pine
        d.shape("deep", f"M{x - 4} {y + 8} L{x} {y - 4} L{x + 4} {y + 8}Z", shadow=False, line=False)
    # Skyline gondola up Bob's Peak
    d.stroke("dark", "M62 122 L12 64", 1.2)
    d.shape("light", rrect(6, 60, 12, 7, 1.5) + " " + rrect(58, 120, 10, 7, 1.5))
    for cx, cy in [(30, 85), (46, 103.5)]:
        d.stroke("dark", f"M{cx} {cy} V{cy + 4}", 1)
        d.shape("pop", rrect(cx - 3.5, cy + 3.5, 7, 6, 1.6), spot=True)
    for x, y in [(30, 126), (44, 132), (56, 138), (20, 136), (36, 140), (70, 144)]:
        d.shape("light", f"M{x - 5} {y + 6} V{y} L{x} {y - 4} L{x + 5} {y} V{y + 6}Z")
    d.marks("deep", " ".join(f"M{x - 6} {y + .5} L{x} {y - 4.5} L{x + 6} {y + .5}Z" for x, y in [(30, 126), (44, 132), (56, 138), (20, 136), (36, 140), (70, 144)]))
    # TSS Earnslaw: white hull, red funnel with a black top
    x, y = 94, 158
    d.shape("light", cloud(x + 30, y - 66, .55), shadow=False)
    d.stroke("dark", f"M{x + 10} {y - 12} V{y - 44} M{x + 72} {y - 12} V{y - 40}", 1.3)
    d.shape("funnel", rrect(x + 38, y - 46, 9, 26, 1), spot=True)
    d.shape("dark", rrect(x + 38, y - 46, 9, 5, 1), shadow=False)
    d.shape("light", rrect(x + 26, y - 26, 34, 7, 1.2))
    d.shape("light", rrect(x + 12, y - 20, 58, 9, 1.2))
    d.marks("deep", " ".join(rrect(x + 16 + i * 6.5, y - 17.5, 3.6, 3.6, .6) for i in range(8)))
    d.shape("light", f"M{x - 2} {y - 13} H{x + 82} L{x + 76} {y} H{x + 8} Q{x + 1} {y - 4} {x - 2} {y - 13}Z")
    d.stroke("funnel", f"M{x + 1} {y - 6} H{x + 79}", 1.6, line=False)
    ripples(d, [(x + 2, y + 6, 26), (x + 46, y + 8, 26)])


# ================================================================ WELLINGTON
def beehive(d: Drawing, cx, base):
    """The Beehive: a round, stepped, tapering tower with a low cap."""
    tiers = []
    y = base - 6
    for i in range(8):
        hw = 19 - i * 1.3
        tiers.append((hw, y))
        y -= 4.4
    d.shape("light", T(cx - 21, base, 42, 7))
    body = "M" + " L".join(f"{cx - hw:.1f} {ty:.1f} L{cx - hw:.1f} {ty - 4.4:.1f}" for hw, ty in tiers)
    body += " L" + " L".join(f"{cx + hw:.1f} {ty - 4.4:.1f} L{cx + hw:.1f} {ty:.1f}" for hw, ty in reversed(tiers)) + "Z"
    d.shape("light", body)
    top = tiers[-1][1] - 4.4
    hw = tiers[-1][0]
    d.shape("light", f"M{cx - hw - 2:.1f} {top:.1f} Q{cx} {top - 9:.1f} {cx + hw + 2:.1f} {top:.1f}Z")
    d.stroke("bee", " ".join(f"M{cx - h + .8:.1f} {ty - 2.2:.1f} H{cx + h - .8:.1f}" for h, ty in tiers), 2, line=False)
    d.raw("", f'<path d="{" ".join(f"M{cx - h:.1f} {ty:.1f} H{cx + h:.1f}" for h, ty in tiers[:-1])}" fill="none" stroke="{d.c.get("ink", "")}" stroke-width="1.6"/>')


def wellington(d: Drawing):
    d.disc("glow", 152, 44, 11)
    d.band("far", "M-30 98 Q6 78 36 84 Q66 68 98 78 Q128 64 158 72 Q190 66 230 84")
    d.band("deep", "M-30 122 Q30 116 70 120 Q130 108 160 100 Q190 92 230 96")
    hs = [(150, 108), (164, 102), (178, 98), (170, 112), (186, 108), (156, 120), (140, 116)]
    d.shape("light", " ".join(f"M{x - 3.5} {y + 4} V{y} L{x} {y - 3} L{x + 3.5} {y} V{y + 4}Z" for x, y in hs), shadow=False, line=False)
    # the red cable car climbing to Kelburn
    d.stroke("dark", "M112 134 L196 88", 1.6)
    group(d, "translate(160 108) rotate(-28.7)", lambda: (
        d.shape("cable", rrect(-11, -9, 22, 9, 1.8), spot=True),
        d.marks("light", " ".join(rrect(-8 + i * 5.2, -7, 3.4, 3.4, .6) for i in range(4)))))
    d.shape("near", towers(138, [(70, 10, 34), (81, 9, 48), (91, 12, 40), (104, 9, 54), (114, 10, 30), (125, 8, 22)]))  # CBD
    for x, w, h in [(81, 9, 48), (104, 9, 54)]:
        floors(d, x, 138 - h, w, 138, 5, "far", 1)
    beehive(d, 44, 140)
    sea(d, 138, "sky2", "far", [(24, 150, 14), (98, 148, 18), (140, 152, 14), (60, 168, 18), (150, 174, 18)])
    # Interislander ferry heading out
    d.shape("light", "M118 166 H170 L166 174 H124Z")
    d.shape("light", rrect(128, 158, 32, 8, 1.5))
    d.stroke("cable", "M120 169 H168", 1.6, line=False)


# ================================================================ KUWAIT CITY
def ktower(d: Drawing, x, base, tip, w=6.0, spheres=()):
    d.shape("shaft", f"M{x - w / 2} {base} L{x - .7} {tip} L{x + .7} {tip} L{x + w / 2} {base}Z")
    for cy, r in spheres:
        d.shape("sphere", circle(x, cy, r), spot=True)
        d.shape("seq", dots_in_circle(x, cy, r), shadow=False, line=False)
        d.stroke("shaft", f"M{x - r * .55} {cy + r * .82} Q{x} {cy + r * 1.1} {x + r * .55} {cy + r * .82}", 1.2, line=False)


def kuwait(d: Drawing):
    d.disc("glow", 52, 58, 15)
    # Liberation Tower and Al Hamra behind
    lib = "M30 136 V66 H36 V58 H44 V66 H50 V136Z M40 58 V30"
    d.shape("far", lib)
    d.stroke("far", "M40 58 V28", 1.8)
    d.shape("far", "M160 136 V64 Q162 48 176 42 V136Z")
    d.shape("far", towers(136, [(18, 10, 30), (52, 9, 40), (62, 10, 28), (146, 12, 46), (178, 10, 32)]))
    d.shape("mid", towers(140, [(26, 12, 22), (40, 9, 30), (56, 12, 18), (70, 10, 24), (148, 10, 26), (160, 12, 18), (174, 10, 24)]))
    # Kuwait Towers on their point
    d.band("ground", "M-30 142 Q60 138 100 140 Q140 138 230 142")
    ktower(d, 90, 142, 72, 5)
    ktower(d, 136, 142, 50, 6, [(98, 11)])
    ktower(d, 112, 142, 22, 7, [(94, 14), (66, 7.5)])
    sea(d, 148, "near", "deep", [(30, 160, 16), (130, 158, 18), (80, 174, 20), (150, 176, 14)])
    dhow(d, 62, 172, .6, hull="wood", sail="light")


# ================================================================ ADELAIDE
def swan(d: Drawing, x, y, s=1.0, role="dark", bill="pop"):
    """A black swan facing right, waterline at y."""
    def draw():
        d.shape(role, "M-11 0 Q-12 -6 -6 -7 Q0 -9 4 -6 Q9 -5 10 -1 Q2 2 -11 0Z")
        d.limb(role, "M5 -5 Q10 -12 7 -19", 2.4, shadow=False)
        d.shape(role, circle(8, -20, 2.2), shadow=False)
        d.shape(bill, "M9.5 -21 L14.5 -18.5 L9.6 -18.6Z", shadow=False, spot=True)
    group(d, f"translate({x} {y}) scale({s})", draw)


def adelaide(d: Drawing):
    d.disc("glow", 150, 46, 12)
    d.band("far", "M-30 104 Q20 94 60 98 Q110 86 150 94 Q190 88 230 98")  # Mount Lofty Ranges
    d.shape("mid", towers(134, [(22, 10, 30), (33, 9, 46), (43, 12, 36), (56, 9, 54), (66, 11, 42), (78, 9, 32), (88, 10, 48),
                                (99, 8, 28), (108, 10, 36), (176, 10, 24)]))
    # St Peter's Cathedral: twin spires behind the Oval
    cath = (T(138, 134, 8, 38) + " " + T(160, 134, 8, 38) + " " + poly((137, 96), (142, 72), (147, 96)) + " " + poly((159, 96), (164, 72), (169, 96))
            + " " + poly((146, 134), (146, 106), (153, 99), (160, 106), (160, 134)))
    d.shape("deep", cath)
    d.shape("light", circle(153, 112, 3), shadow=False)
    d.band("near", "M-30 136 Q100 132 230 136")
    # Adelaide Oval: grandstands under the white petal roofs
    d.shape("deep", "M28 144 V128 H172 V144Z")
    d.shape("light", "M24 131 Q34 112 54 118 Q60 108 74 110 Q86 104 98 114 Q112 102 126 110 Q140 104 150 114 Q166 110 176 130 "
                     "Q170 126 160 127 Q100 120 40 127 Q30 127 24 131Z")
    d.stroke("far", "M54 118 Q58 122 60 126 M98 114 Q100 120 100 124 M150 114 Q148 120 148 126", 1.2, line=False)
    d.marks("mid", " ".join(rrect(34 + i * 10, 133, 6, 2.2, .6) for i in range(14)))
    sea(d, 144, "far", "mid", [(20, 154, 14), (60, 160, 18), (140, 154, 16), (40, 176, 18), (150, 172, 18)])
    swan(d, 104, 166, 1.1)
    swan(d, 126, 172, .9)


# ================================================================ DARWIN
def croc(d: Drawing, x, y, s=1.0, role="deep"):
    """A saltwater crocodile cruising with only its head and back above the water (waterline y)."""
    def draw():
        d.shape(role, "M-40 0 Q-34 -4 -20 -3 Q-14 -6 -8 -4 Q-2 -9 4 -5 Q12 -5 30 -3 Q36 -3 38 0Z")
        d.marks(role, "M-34 -2 l2 -2.5 l2 2.5Z M-26 -2.5 l2 -2.5 l2 2.5Z M-18 -3 l2 -2.5 l2 2.5Z")
        d.marks("glow", circle(0, -6, 1.3))
    group(d, f"translate({x} {y}) scale({s})", draw)


def lugger(d: Drawing, x, y, s=1.0, role="dark"):
    """Two-masted pearling lugger in silhouette, waterline y."""
    def draw():
        d.shape(role, "M-20 -6 H22 L16 0 H-16Z")
        d.stroke(role, "M-6 -6 V-40 M10 -6 V-30", 1.4)
        d.shape(role, "M-5 -38 Q4 -22 8 -8 H-5Z M11 -28 Q17 -18 19 -8 H11Z M-7 -36 L-20 -8 H-7Z")
    group(d, f"translate({x} {y}) scale({s})", draw)


def darwin(d: Drawing):
    d.disc("glow", 128, 118, 30)
    d.disc("glow2", 128, 118, 19, shadow=False, line=False)
    d.shape("light", cloud(140, 60, .9), shadow=False)
    birds(d, [(56, 54, 1), (70, 46, .8)])
    d.band("far", "M-30 120 H230")
    d.stroke("glow2", "M106 128 h44 M112 136 h32 M118 146 h20", 2.2, line=False)
    # the city on its peninsula
    d.shape("deep", "M-30 122 V120 H90 Q98 120 104 126 H-30Z")
    d.shape("deep", towers(121, [(10, 8, 22), (19, 10, 36), (30, 9, 28), (40, 11, 44), (52, 9, 30), (62, 10, 22), (73, 8, 14)]))
    d.marks("mid", " ".join(rrect(x + 2, 121 - h + 4, w - 4, 1.4, .5) for x, w, h in [(19, 10, 36), (40, 11, 44)]))
    # Stokes Hill Wharf on its piles
    d.stroke("deep", "M96 124 H178 M104 124 V132 M118 124 V132 M132 124 V132 M146 124 V132 M160 124 V132 M174 124 V132", 2)
    d.shape("deep", "M150 124 V116 L160 110 L170 116 V124Z")
    d.band("mid", waves(150, 2, 30), line=False)
    lugger(d, 70, 146, .9)
    croc(d, 120, 166, 1.0)
    ripples(d, [(70, 170, 14), (150, 172, 18), (30, 160, 14)], "far")
    palm(d, 14, 186, 26, 104, 1.05, role="dark", trunk="dark", bend=-8)
    palm(d, 186, 186, 176, 120, .85, role="dark", trunk="dark", bend=8)
    d.band("near", waves(186, 3, 32), line=False)


# ================================================================ CAIRNS
def catamaran(d: Drawing, x, y, s=1.0):
    def draw():
        d.shape("light", "M-30 -10 H30 L22 0 H-27Z")
        d.stroke("pop", "M-28 -5 H26", 1.8, line=False)
        d.shape("light", rrect(-24, -19, 42, 10, 2))
        d.shape("deep", rrect(-21, -16, 36, 3.6, 1), shadow=False, line=False)
        d.shape("light", rrect(-16, -26, 24, 8, 2))
        d.shape("deep", rrect(-13, -23.5, 18, 3, 1), shadow=False, line=False)
        d.stroke("dark", "M-6 -26 V-34", 1.2)
    group(d, f"translate({x} {y}) scale({s})", draw)


def cairns(d: Drawing):
    d.disc("glow", 44, 50, 12)
    # rainforest ranges wrapped round the city
    d.band("mid", "M-30 100 Q-4 78 26 76 Q50 60 74 70 Q98 48 126 58 Q150 46 172 64 Q198 62 230 82")
    d.stroke("near", "M30 86 q6 -6 12 0 M60 78 q6 -6 12 0 M96 66 q6 -6 12 0 M134 64 q6 -6 12 0 M160 74 q6 -6 12 0 M80 88 q6 -6 12 0 M118 82 q6 -6 12 0",
             1.6, line=False)
    d.band("near", "M-30 120 Q40 112 100 116 T230 112")
    blocks = [(38, 10, 26), (50, 12, 42), (64, 9, 30), (75, 12, 48), (89, 10, 34), (101, 12, 26), (115, 10, 36), (127, 9, 22)]
    d.shape("light", towers(136, blocks))
    for x, w, h in blocks:
        floors(d, x, 136 - h, w, 136, 4.5, "far", 1)
    for x0, x1, s in [(30, 26, .62), (58, 56, .55), (98, 100, .6), (142, 146, .68), (164, 168, .58)]:
        palm(d, x0, 140, x1, 140 - 36 * s / .6, s, role="deep", trunk="deep", bend=3)
    sea(d, 140, "far", "mid", [(20, 150, 14), (90, 148, 16), (160, 152, 14), (30, 174, 18)])
    catamaran(d, 116, 168, 1.05)


# ================================================================ CHRISTCHURCH
def willow(d: Drawing, x, base, s=1.0, role="deep"):
    def draw():
        d.limb("dark", "M0 0 V-24 M0 -14 L-8 -26 M0 -16 L8 -28", 3)
        d.shape(role, "M-24 -4 Q-28 -42 0 -48 Q28 -42 24 -4 L18 -12 L13 -2 L8 -14 L3 -3 L-2 -14 L-7 -2 L-12 -13 L-17 -3Z")
        d.stroke("near", "M-14 -36 Q-18 -24 -16 -12 M-4 -40 Q-6 -26 -5 -14 M8 -40 Q10 -26 9 -14 M17 -34 Q20 -22 18 -12", 1.2, line=False)
    group(d, f"translate({x} {base}) scale({s})", draw)


def christchurch(d: Drawing):
    d.disc("glow", 154, 48, 11)
    d.band("far", "M-30 96 Q20 84 60 92 Q100 76 140 86 Q180 78 230 92")  # Port Hills
    d.shape("mid", towers(134, [(16, 10, 26), (27, 9, 34), (128, 10, 32), (139, 9, 22), (150, 12, 30), (163, 9, 20), (173, 10, 26)]))
    # ChristChurch Cathedral: Gothic tower and spire at the west end, nave behind
    d.shape("light", poly((88, 134), (88, 108), (104, 98), (120, 108), (120, 134)) + " " + T(70, 134, 18, 50))
    d.shape("spire", poly((70, 84), (79, 40), (88, 84)), spot=True)
    d.shape("spire", poly((68.5, 85), (70, 77), (71.5, 85)) + " " + poly((86.5, 85), (88, 77), (89.5, 85)), shadow=False)
    d.marks("stone2", " ".join(f"M{x} 128 V118 Q{x + 2.5} 113 {x + 5} 118 V128Z" for x in (92, 101.5, 111)))
    d.marks("stone2", "M75 120 V104 Q79 98 83 104 V120Z")
    d.stroke("stone2", "M70 90 H88 M70 96 H88", 1.2, line=False)
    d.band("near", "M-30 136 Q100 132 230 136")
    # the heritage tram along the river
    d.shape("tram", rrect(132, 123, 36, 12, 2.5), spot=True)
    d.shape("light", rrect(132, 127, 36, 2.4, .4), shadow=False, line=False)
    d.marks("light", " ".join(rrect(135 + i * 6.2, 130, 4, 3.4, .6) for i in range(5)))
    d.stroke("dark", "M150 123 L146 116 H156", 1)
    willow(d, 34, 140, 1.0)
    sea(d, 140, "sky2", "far", [(70, 150, 18), (150, 152, 16), (30, 176, 16), (156, 178, 18)])
    # a punt on the Avon
    d.shape("wood", "M64 166 H136 L132 172 H68Z")
    d.limb("dark", "M124 165 L122 156", 2.6, shadow=False)
    d.shape("light", rrect(118.5, 144, 7, 12, 2.5))
    d.shape("dark", circle(122, 140, 3))
    d.shape("hero2", "M117 138.5 H127 V137 Q122 133 117 137Z", shadow=False)
    d.stroke("dark", "M112 182 L132 132", 1.4)
    for x in (82, 94, 106):
        d.shape("dark", circle(x, 160, 2.6))
        d.shape("pop" if x == 94 else "light", rrect(x - 3.5, 162, 7, 5, 2))


# ================================================================ HONOLULU
DIAMOND = "M70 140 Q96 126 116 112 Q134 98 146 84 L156 72 Q162 67 168 71 L174 82 Q182 98 196 110 L230 120 V150 H70Z"


def outrigger(d: Drawing, x, y, s=1.0):
    def draw():
        d.stroke("dark", "M-14 -2 L-12 6 M10 -2 L12 6", 1.4)
        d.shape("dark", "M-16 6 H16 Q14 8 -14 8Z", shadow=False)
        d.shape("hero", "M-34 -6 Q-30 0 -24 0 H24 Q30 0 34 -6 Q20 -3 -20 -3Z", spot=True)
        for px in (-16, -2, 12):
            d.shape("dark", circle(px, -14, 2.4))
            d.shape("dark", f"M{px - 3} -3 L{px - 2} -11 H{px + 2} L{px + 3} -3Z", shadow=False)
            d.stroke("wood", f"M{px + 6} -16 L{px - 4} 2", 1.2)
    group(d, f"translate({x} {y}) scale({s})", draw)


def honolulu(d: Drawing):
    d.disc("glow", 56, 50, 13)
    d.shape("mid", DIAMOND)
    d.stroke("near", "M118 112 L124 128 M132 100 L138 122 M146 88 L150 114 M160 74 L162 100 M172 82 L178 104", 1.6, line=False)
    # Waikiki hotel towers
    blocks = [(12, 10, 30), (23, 12, 50), (37, 9, 38), (47, 12, 58), (61, 10, 44), (73, 12, 34), (87, 9, 26)]
    d.shape("light", towers(140, blocks))
    for x, w, h in blocks:
        floors(d, x, 140 - h, w, 140, 4.5, "far", 1)
    # the pink Royal Hawaiian
    d.shape("pink", T(92, 142, 44, 16) + " " + T(107, 142, 14, 30) + " " + dome(114, 112, 7, 7))
    d.marks("pink2", " ".join(f"M{x} 140 V134 Q{x + 2} 131 {x + 4} 134 V140Z" for x in (95, 101, 124, 130)) + " " +
            " ".join(f"M{x} 124 V118 Q{x + 2} 115 {x + 4} 118 V124Z" for x in (109.5, 114.5)))
    d.band("ground", "M-30 142 Q100 138 230 142")
    palm(d, 150, 146, 156, 104, .9, role="dark", trunk="dark", bend=-6)
    palm(d, 170, 148, 182, 118, .7, role="dark", trunk="dark", bend=-4)
    d.band("far", waves(152, 2.5, 26))
    d.stroke("light", waves(153, 2.5, 26), 2.2, line=False)
    d.band("mid", waves(170, 3, 30), line=False)
    ripples(d, [(20, 164, 16), (140, 164, 16), (40, 182, 18)])
    outrigger(d, 88, 170, 1.0)


# ================================================================ STONE TOWN
def house_of_wonders(d: Drawing, x0=56, base=140, w=88):
    sh = 11
    top = base - sh * 3
    d.shape("light", T(x0, base, w, sh * 3) + " " + T(x0 - 2, top + 2, w + 4, 3.5))
    n = 11
    gap = w / n
    for k in range(3):
        y = base - sh * (k + 1) + 2.4
        d.marks("hw", " ".join(rrect(x0 + gap * i + gap * .2, y, gap * .6, sh - 4.4, gap * .3) for i in range(n)))
        d.stroke("hw2", f"M{x0} {y + sh - 2.2} H{x0 + w}", 1.4, line=False)
    cx = x0 + w / 2
    d.shape("light", T(cx - 8, top, 16, 22) + " " + T(cx - 6, top - 22, 12, 9) + " " + poly((cx - 7.5, top - 31), (cx, top - 39), (cx + 7.5, top - 31)))
    d.shape("hero2", circle(cx, top - 13, 4), shadow=False, spot=True)
    d.stroke("hw2", f"M{cx} {top - 15.5} V{top - 13} L{cx + 2} {top - 12}", 1, line=False)
    d.stroke("dark", f"M{cx} {top - 39} V{top - 48}", 1.2)
    d.shape("pop", f"M{cx} {top - 48} h7 l-2 2.5 l2 2.5 h-7Z", shadow=False)


def stone_town(d: Drawing):
    d.disc("glow", 160, 46, 12)
    # St Joseph's twin spires and the old town behind
    d.shape("mid", towers(130, [(20, 14, 18), (36, 12, 24), (150, 12, 22), (164, 14, 16)]) + " " +
            T(140, 130, 7, 40) + " " + T(152, 130, 7, 40) + " " + poly((139, 90), (143.5, 76), (148, 90)) + " " + poly((151, 90), (155.5, 76), (160, 90)))
    palm(d, 30, 140, 24, 92, .9, role="deep", trunk="deep", bend=-6)
    palm(d, 174, 140, 178, 98, .8, role="deep", trunk="deep", bend=6)
    # the Old Fort's crenellated wall
    d.shape("fort", "M8 140 V122 " + " ".join(f"H{x} V118 H{x + 4} V122" for x in range(12, 52, 8)) + " H56 V140Z")
    house_of_wonders(d, 60, 140, 84)
    d.band("ground", "M-30 140 Q100 137 230 140")
    sea(d, 146, "near", "deep", [(30, 156, 14), (150, 154, 16), (90, 182, 18)])
    dhow(d, 60, 174, .85, hull="wood", sail="light")
    dhow(d, 148, 166, .6, hull="wood", sail="light", spot=False)


# ================================================================ TUNIS
def flamingo(d: Drawing, x, y, s=1.0, role="pink"):
    """A flamingo wading, facing left, feet at waterline y."""
    def draw():
        d.stroke("pink2", "M0 0 V-18 M0 -10 L5 -12", 1.2)
        d.shape(role, "M-8 -22 Q-6 -29 2 -28 Q10 -27 13 -22 Q4 -17 -8 -22Z")
        d.limb(role, "M-6 -24 Q-12 -32 -6 -40 Q-2 -46 -8 -48", 2.2, shadow=False)
        d.shape(role, circle(-8, -48, 2.2), shadow=False)
        d.shape("dark", "M-10 -49 L-14 -45 L-11 -46Z", shadow=False)
    group(d, f"translate({x} {y}) scale({s})", draw)


def tunis(d: Drawing):
    d.disc("glow", 58, 50, 12)
    # Boukornine's twin horns across the gulf
    d.band("far", "M-30 112 Q40 106 100 110 Q122 108 136 98 L146 78 L152 88 L160 74 L168 92 Q184 104 230 106")
    # the medina: white cubes and domes
    med = towers(134, [(14, 12, 14), (26, 10, 20), (64, 12, 16), (76, 10, 12), (88, 12, 18)]) + " " + dome(32, 114, 6) + " " + dome(82, 122, 5) + " " + dome(94, 116, 4.5)
    d.shape("light", med)
    # Zitouna Mosque minaret
    d.shape("stone", T(44, 136, 14, 62) + " " + T(46, 74, 10, 8) + " " + dome(51, 66, 4.5, 6))
    d.shape("stone", " ".join(f"M{x} 74 V71 H{x + 2.4} V74Z" for x in (44, 47.8, 51.6, 55.4)), shadow=False)
    d.stroke("stone2", "M44 84 H58 M44 112 H58", 1.4, line=False)
    d.marks("stone2", rrect(47.5, 90, 7, 16, 3.5) + " " + rrect(48.5, 118, 5, 9, 2.5))
    d.stroke("dark", "M51 60 V54", 1.2)
    # Cathedral of St Vincent de Paul: twin towers and dome
    cx = 140
    d.shape("stone", dome(cx, 98, 13, 14) + " " + T(cx - 2, 86, 4, 6))
    d.shape("stone", T(cx - 26, 136, 52, 36) + " " + T(cx - 26, 100, 12, 22) + " " + T(cx + 14, 100, 12, 22) + " " +
            dome(cx - 20, 78, 6, 8) + " " + dome(cx + 20, 78, 6, 8))
    d.stroke("dark", f"M{cx} 84 V76 M{cx - 2.5} 79 H{cx + 2.5}", 1.2)
    d.marks("stone2", f"M{cx - 7} 136 V118 Q{cx} 108 {cx + 7} 118 V136Z " + circle(cx, 108, 3.6) + " " +
            rrect(cx - 22, 86, 4, 8, 2) + " " + rrect(cx + 18, 86, 4, 8, 2))
    palm(d, 106, 138, 104, 104, .7, role="deep", trunk="deep", bend=-3)
    palm(d, 182, 140, 186, 106, .7, role="deep", trunk="deep", bend=3)
    # Lake of Tunis with flamingos
    sea(d, 138, "mid", "near", [(100, 150, 16), (150, 156, 18), (60, 180, 16), (140, 176, 16)])
    flamingo(d, 38, 170, .9)
    flamingo(d, 62, 176, .8)
    flamingo(d, 112, 168, .7)


# ================================================================ DAKAR
def renaissance(d: Drawing, x, base, s=1.0, role="bronze"):
    """African Renaissance Monument: a man lifting a child who points out to sea, a woman behind him."""
    def draw():
        # woman, leaning back behind him, dress and hair streaming back
        d.shape(role, "M6 0 L10 -20 Q12 -34 14 -42 Q18 -50 22 -46 Q26 -40 22 -30 Q24 -14 28 0Z")
        d.limb(role, "M18 -42 Q28 -38 34 -30", 3)
        d.shape(role, circle(20, -52, 4.2) + " M22 -55 Q32 -56 38 -48 Q30 -52 23 -49Z")
        # man: legs, torso, head
        d.limb(role, "M-6 0 L-3 -26 M6 0 L3 -26", 5.5)
        d.shape(role, "M-8 -24 Q-10 -40 -12 -52 Q-2 -56 10 -52 Q8 -40 7 -24Z")
        d.shape(role, circle(-1, -59, 5))
        d.limb(role, "M7 -48 Q14 -38 16 -36", 4)
        # raised arm carrying the child, who points out to sea
        d.limb(role, "M-9 -50 Q-16 -60 -14 -72", 4.4)
        d.shape(role, "M-20 -72 Q-14 -76 -9 -72 L-11 -84 Q-14 -88 -18 -84Z")
        d.shape(role, circle(-14, -90, 3.4))
        d.limb(role, "M-15 -82 L-28 -92", 2.6)
    group(d, f"translate({x} {base}) scale({s})", draw)


def pirogue(d: Drawing, x, y, s=1.0, body="pir", stripe="hero2", spot=True):
    """A Senegalese painted fishing pirogue with upswept bow and stern, waterline y."""
    def draw():
        d.shape(body, "M-34 -16 Q-30 -6 -20 -4 H20 Q30 -6 34 -16 Q30 -9 22 -9 H-22 Q-30 -9 -34 -16Z M-20 -4 Q-18 0 -14 0 H14 Q18 0 20 -4Z", spot=spot)
        d.stroke(stripe, "M-24 -7 H24", 1.6, line=False)
        d.marks("pop", "M-12 -7.8 l3 2.2 l3 -2.2Z M0 -7.8 l3 2.2 l3 -2.2Z M12 -7.8 l3 2.2 l3 -2.2Z")
    group(d, f"translate({x} {y}) scale({s})", draw)


def baobab(d: Drawing, x, base, s=1.0, role="deep"):
    def draw():
        d.shape(role, "M-7 0 Q-5 -14 -6 -22 L-14 -30 M-6 -22 Z M-7 0 Q-6 -16 -5 -24 L-16 -32 L-14 -34 L-3 -27 L-3 -36 L0 -36 L1 -27 L12 -35 L14 -33 L5 -24 Q6 -14 8 0Z")
        d.shape(role, ellipse(-15, -35, 7, 3.5) + " " + ellipse(13, -36, 7, 3.5) + " " + ellipse(-1, -39, 6, 3.2), shadow=False)
    group(d, f"translate({x} {base}) scale({s})", draw)


def dakar(d: Drawing):
    d.disc("glow", 160, 54, 13)
    d.shape("far", towers(122, [(14, 8, 16), (24, 10, 24), (36, 8, 18), (172, 10, 20), (184, 8, 14)]))
    # Les Mamelles: two hills, the lighthouse on one, the monument on the other
    d.band("mid", "M-30 124 Q10 116 40 104 Q56 98 72 106 Q86 116 96 114 Q110 100 124 98 Q140 98 152 108 Q172 122 230 124")
    d.shape("light", T(52, 104, 8, 18) + " " + T(50, 86, 12, 3))
    d.shape("pop", rrect(53, 80, 6, 6, 1.4), shadow=False)
    d.shape("light", dome(56, 80, 3.6, 3), shadow=False)
    d.stroke("mid", "M52 96 H60", 1.6, line=False)
    d.shape("bronze", poly((112, 100), (114, 94), (134, 94), (136, 100)))
    renaissance(d, 124, 94, .82)
    baobab(d, 168, 120, .9)
    d.band("near", "M-30 136 Q100 128 230 136")
    sea(d, 140, "far", "mid", [(30, 150, 14), (120, 148, 16), (160, 160, 14)])
    pirogue(d, 72, 170, 1.0)
    pirogue(d, 146, 178, .8, body="pir2", stripe="light", spot=False)


# ================================================================ KIGALI
def kigali(d: Drawing):
    d.disc("glow", 152, 46, 12)
    d.band("far", "M-30 96 Q10 80 50 86 Q90 70 130 82 Q170 72 230 88")
    # Kigali City Tower and neighbours
    d.shape("near", towers(130, [(28, 10, 22), (40, 9, 30), (116, 10, 26), (160, 10, 20)]) + " " +
            "M128 130 V70 Q136 62 146 66 V130Z")
    floors(d, 128, 70, 18, 130, 5, "mid", 1)
    # Kigali Convention Centre dome, its spiral ribs
    kcc = "M70 132 C70 112 76 92 88 84 Q94 78 100 77 Q106 78 112 84 C124 92 130 112 130 132Z"
    d.shape("hero", kcc, spot=True)
    ribs = []
    for i in range(-4, 5):
        bx = 100 + i * 7
        ribs.append(f"M{bx:.1f} 132 Q{100 + i * 6.2 + 6:.1f} 102 {100 + i * 1.4 + 2:.1f} 80")
    d.stroke("light", " ".join(ribs), 1.3, line=False)
    d.shape("hero", T(97, 78, 6, 4), shadow=False)
    d.shape("light", T(60, 136, 80, 4), shadow=False)
    d.band("mid", "M-30 140 Q40 132 100 138 T230 134")
    # red-roofed houses on the near hill
    for x, y in [(20, 142), (38, 146), (150, 140), (168, 144), (186, 140), (58, 152), (136, 150)]:
        d.shape("light", T(x - 5, y + 6, 10, 6))
        d.shape("pop", f"M{x - 7} {y + 1} L{x} {y - 4} L{x + 7} {y + 1}Z", shadow=False)
    d.band("deep", hills(170, 6, 20))
    # banana plant
    d.limb("dark", "M168 190 Q166 172 168 156", 4)
    d.shape("dark", " ".join(frond(168, 156, a, L, dr, .42) for a, L, dr in [(-150, 24, 8), (-110, 22, 2), (-70, 22, 2), (-30, 24, 8)]))
    d.band("dark", hills(188, 3, 0), line=False)


# ================================================================ WINDHOEK
def thorn_tree(d: Drawing, x, base, s=1.0, role="deep"):
    def draw():
        d.limb(role, "M0 0 V-14 M0 -12 L-9 -22 M0 -12 L10 -24", 2.8)
        d.shape(role, "M-24 -22 Q-14 -32 2 -31 Q20 -32 26 -24 Q4 -20 -24 -22Z")
    group(d, f"translate({x} {base}) scale({s})", draw)


def windhoek(d: Drawing):
    d.disc("glow", 52, 48, 13)
    d.band("far", "M-30 102 Q0 88 30 92 Q60 76 92 86 Q124 74 156 84 Q186 78 230 92")  # Eros and Auas hills
    d.shape("mid", towers(130, [(16, 12, 24), (30, 9, 34), (40, 12, 26), (150, 10, 30), (161, 12, 22), (175, 10, 16)]))
    d.band("near", "M-30 134 Q50 128 80 122 Q100 118 120 122 Q150 128 230 134")
    # Christuskirche on its knoll: slender clock tower, nave and apse
    d.shape("light", poly((104, 124), (104, 102), (122, 94), (140, 102), (140, 124)) + " " + dome(140, 124, 8, 14))
    d.shape("roof", poly((102, 103), (122, 92), (142, 103), (138, 103), (122, 96), (106, 103)), shadow=False)
    d.shape("light", T(90, 125, 14, 46) + " " + T(84, 124, 6, 22) + " " + poly((84, 102), (87, 94), (90, 102)))
    d.shape("roof", poly((89, 79), (97, 40), (105, 79)) + " " + poly((83, 103), (87, 93), (91, 103)), spot=True)
    d.shape("roof", f"M102 104 L122 95 L142 104 H136 L122 98 L108 104Z", shadow=False, line=False)
    d.marks("roof", circle(97, 88, 3) + " " + " ".join(f"M{x} 120 V110 Q{x + 2} 107 {x + 4} 110 V120Z" for x in (110, 118, 126)) +
            " M94 120 V108 Q97 104 100 108 V120Z")
    thorn_tree(d, 40, 140, 1.0)
    thorn_tree(d, 168, 142, .85)
    d.band("ground", "M-30 144 Q100 136 230 144")
    d.band("deep", hills(180, 5, 20), line=False)


# ================================================================ DURBAN
def durban(d: Drawing):
    d.disc("glow", 162, 50, 12)
    d.band("far", "M-30 118 Q40 108 100 114 T230 110")
    # Golden Mile hotels
    blocks = [(126, 10, 44), (138, 12, 58), (152, 10, 40), (164, 12, 50), (178, 9, 32)]
    d.shape("mid", towers(138, blocks))
    for x, w, h in blocks:
        floors(d, x, 138 - h, w, 138, 4.5, "far", 1)
    # Moses Mabhida Stadium: bowl under the great arch
    d.limb("near", "M18 136 Q70 -32 124 136", 4.2)
    d.stroke("near", "M38 112 L48 94 M58 110 L62 72 M80 110 L80 64 M100 110 L96 76 M116 114 L110 98", 1, line=False)
    d.shape("light", "M14 138 Q18 118 40 112 Q70 106 100 110 Q124 114 132 138Z")
    d.stroke("far", "M22 126 Q70 114 126 128", 1.6, line=False)
    d.band("ground", "M-30 140 Q100 136 230 140")
    # a pier running out through the surf
    d.shape("deep", "M70 150 H150 V153 H70Z")
    d.stroke("deep", "M80 153 V164 M96 153 V164 M112 153 V164 M128 153 V164 M144 153 V164", 1.8)
    d.band("mid", waves(158, 3, 26))
    d.stroke("light", waves(159, 3, 26), 2.4)
    d.band("near", waves(176, 3, 30), line=False)
    ripples(d, [(20, 170, 14), (150, 172, 18), (70, 184, 16)])


# ================================================================ ADDIS ABABA
def eth_cross(d: Drawing, x, y, s=1.0, role="gold"):
    d.stroke(role, f"M{x} {y + 4 * s} V{y - 8 * s} M{x - 5 * s} {y - 3 * s} H{x + 5 * s}", 1.3 * s)
    d.marks(role, " ".join(circle(px, py, 1.3 * s) for px, py in [(x, y - 8 * s), (x - 5 * s, y - 3 * s), (x + 5 * s, y - 3 * s)]))


def addis(d: Drawing):
    d.disc("glow", 52, 46, 12)
    d.band("far", "M-30 96 Q20 72 60 80 Q96 62 136 72 Q172 62 230 80")  # the Entoto hills
    d.stroke("mid", "M30 84 l3 -6 l3 6 M44 80 l3 -6 l3 6 M104 72 l3 -6 l3 6 M150 70 l3 -6 l3 6 M166 72 l3 -6 l3 6", 1.4, line=False)
    # the city, the Commercial Bank of Ethiopia tower rising highest
    d.shape("mid", towers(132, [(14, 10, 24), (26, 9, 34), (108, 10, 30), (120, 12, 40), (170, 10, 28), (182, 9, 18)]) + " " +
            "M140 132 V56 L150 34 L162 46 V132Z")
    floors(d, 140, 56, 22, 132, 5, "far", 1)
    # Holy Trinity Cathedral: domed crossing, twin front towers
    cx = 76
    d.shape("light", dome(cx, 90, 16, 18) + " " + T(cx - 2, 72, 4, 4))
    d.shape("light", T(cx - 34, 136, 68, 30) + " " + T(cx - 18, 106, 36, 16) + " " + T(cx - 34, 106, 12, 16) + " " + T(cx + 22, 106, 12, 16))
    d.shape("dome", dome(cx, 90, 16, 18) + " " + dome(cx - 28, 90, 6, 8) + " " + dome(cx + 28, 90, 6, 8), spot=True)
    d.stroke("stone2", f"M{cx - 9} 76 Q{cx - 12} 82 {cx - 13} 90 M{cx} 72 V90 M{cx + 9} 76 Q{cx + 12} 82 {cx + 13} 90", 1, line=False)
    eth_cross(d, cx, 66, 1.1)
    eth_cross(d, cx - 28, 78, .7)
    eth_cross(d, cx + 28, 78, .7)
    d.marks("stone2", f"M{cx - 6} 136 V122 Q{cx} 114 {cx + 6} 122 V136Z " + " ".join(
        f"M{x} 132 V122 Q{x + 2.5} 118 {x + 5} 122 V132Z" for x in (cx - 30, cx - 20, cx + 15, cx + 25)) + " " + circle(cx, 99, 3.5))
    d.band("near", "M-30 138 Q50 132 100 138 T230 134")
    for x, h in [(150, 44), (166, 36), (182, 40), (18, 38), (130, 30)]:
        d.limb("deep", f"M{x} 150 V{150 - h * .5}", 2.4)
        d.shape("deep", ellipse(x, 150 - h * .7, 6, h * .32))
    d.band("deep", hills(168, 6, 30))
    d.band("dark", hills(186, 3, 0), line=False)


# ================================================================ BEIRUT
PIGEON = ("M116 156 L120 122 Q124 104 140 98 Q158 92 172 102 Q180 114 182 156Z "
          "M130 156 V140 Q131 126 140 124 Q149 126 150 140 V156Z")


def beirut(d: Drawing):
    d.disc("glow", 46, 50, 12)
    d.band("far", "M-30 92 L10 80 L36 70 L60 76 L90 64 L120 72 L150 62 L180 72 L230 80")  # Mount Lebanon
    d.shape("light", poly((30, 72), (36, 70), (60, 76), (54, 78), (46, 74), (40, 77)) + " " + poly((80, 68), (90, 64), (112, 70), (104, 72), (96, 69), (88, 72)) +
             " " + poly((140, 65), (150, 62), (172, 70), (164, 71), (156, 67), (148, 70)), shadow=False)
    d.shape("mid", towers(134, [(14, 10, 30), (25, 12, 50), (39, 9, 38), (90, 10, 34), (101, 12, 52), (115, 10, 40), (127, 9, 28),
                                (138, 12, 44), (152, 10, 30), (164, 12, 36), (178, 10, 24)]))
    # Mohammad Al-Amin Mosque: blue dome and four slim minarets
    cx = 66
    d.shape("light", T(cx - 20, 136, 40, 22))
    d.shape("dome", dome(cx, 114, 16, 20) + " " + dome(cx - 13, 116, 5, 6) + " " + dome(cx + 13, 116, 5, 6), spot=True)
    d.stroke("gold", f"M{cx} 94 V86", 1.4)
    for mx, top in [(cx - 26, 70), (cx + 26, 70), (cx - 21, 82), (cx + 21, 82)]:
        d.shape("light", f"M{mx - 2.2} 136 V{top + 6} L{mx} {top} L{mx + 2.2} {top + 6}Z")
        d.shape("light", rrect(mx - 3.4, top + 16, 6.8, 2.4, .8), shadow=False)
    d.marks("stone2", " ".join(f"M{x} 136 V128 Q{x + 2.5} 124 {x + 5} 128 V136Z" for x in (cx - 15, cx - 2.5, cx + 10)))
    d.band("near", "M-30 138 H230")  # the Corniche
    palm(d, 18, 140, 22, 110, .7, role="deep", trunk="deep", bend=3)
    palm(d, 104, 140, 100, 112, .62, role="deep", trunk="deep", bend=-3)
    sea(d, 142, "far", "mid", [(24, 152, 14), (70, 160, 18), (40, 178, 16)])
    # Pigeon Rocks with their sea arch
    d.shape("rock", PIGEON, extra='fill-rule="evenodd"', spot=True)
    d.shape("rock2", "M168 100 Q180 114 182 156 H170 Q172 124 164 102Z", shadow=False, line=False)
    d.shape("green", "M128 106 Q142 94 160 96 Q170 98 172 102 Q156 96 140 102Z", shadow=False, line=False)
    d.shape("rock", "M92 156 L96 136 Q100 128 106 130 Q112 134 112 156Z")
    d.stroke("light", "M112 158 h76 M90 158 h24", 2, line=False)


# ================================================================ MANAMA
def wtc_tower(cx, base, top, outer, inner, side) -> str:
    """One Bahrain WTC sail tower. side=-1: left tower, +1: right tower."""
    xo = cx + side * outer  # outer foot
    xi = cx + side * inner  # inner foot
    tip = cx + side * (inner - 2)
    return (f"M{xi} {base} L{xi + side * 1} {top + 30} Q{tip} {top + 10} {tip} {top} "
            f"Q{xo - side * 6} {top + 34} {xo} {base}Z")


def turbine(d: Drawing, x, y, r):
    d.shape("turb", circle(x, y, 2), shadow=False)
    blades = []
    for a in (-90, 30, 150):
        t = math.radians(a)
        ex, ey = x + r * math.cos(t), y + r * math.sin(t)
        nx, ny = -math.sin(t) * 1.6, math.cos(t) * 1.6
        blades.append(f"M{x + nx:.1f} {y + ny:.1f} L{ex:.1f} {ey:.1f} L{x - nx:.1f} {y - ny:.1f}Z")
    d.shape("turb", " ".join(blades), shadow=False)


def manama(d: Drawing):
    d.disc("glow", 160, 50, 13)
    # Bahrain Financial Harbour twins and the city behind
    d.shape("far", towers(134, [(14, 10, 30), (25, 12, 42), (150, 10, 36), (176, 12, 30)]) + " " +
            "M38 134 V62 Q44 70 48 80 V134Z M52 134 V80 Q56 70 62 62 V134Z")
    d.shape("mid", towers(136, [(20, 12, 20), (64, 10, 24), (138, 12, 20), (162, 10, 28), (174, 12, 16)]))
    # Bahrain World Trade Center: two sails with three turbines on bridges
    d.shape("near", wtc_tower(100, 138, 30, 34, 13, -1) + " " + wtc_tower(100, 138, 30, 34, 13, 1))
    d.stroke("light", "M93 120 L92 48 M107 120 L108 48", 1.2, line=False)
    for y in (108, 84, 60):
        d.shape("near", T(86, y + 3, 28, 3), shadow=False)
        turbine(d, 100, y, 11)
    d.band("ground", "M-30 140 Q100 136 230 140")
    sea(d, 144, "far", "mid", [(30, 154, 14), (150, 154, 16), (120, 178, 18)])
    dhow(d, 60, 174, .8, hull="wood", sail="light")


# ================================================================ PORT LOUIS
def port_louis(d: Drawing):
    d.disc("glow", 30, 66, 10)
    # the Moka range: Le Pouce's thumb and Pieter Both's balanced boulder
    d.band("far", "M-30 108 L-4 96 L14 90 L28 94 L42 80 L50 66 Q52 56 58 55 Q64 56 63 64 L70 78 L86 86 L104 82 L118 70 L128 58 "
                  "L133 52 L139 52 L144 60 L152 72 L166 82 L184 84 L200 94 L230 100")
    d.shape("far", "M133.5 53 L134.6 44 H137.4 L138.5 53Z " + circle(136, 40, 5))
    d.band("near", "M-30 118 Q20 106 60 112 Q100 104 140 112 Q180 106 230 114")
    blocks = [(30, 10, 22), (42, 12, 34), (56, 9, 26), (66, 12, 40), (80, 10, 28), (122, 10, 24), (134, 12, 36), (148, 10, 22)]
    d.shape("light", towers(134, blocks))
    for x, w, h in blocks:
        floors(d, x, 134 - h, w, 134, 5, "far", 1)
    # the Caudan waterfront: red roofs on the quay
    d.shape("sand", T(90, 136, 30, 10) + " " + T(160, 136, 22, 9))
    d.shape("pop", poly((88, 127), (105, 119), (122, 127)) + " " + poly((158, 128), (171, 121), (184, 128)), shadow=False)
    palm(d, 20, 140, 16, 104, .8, role="deep", trunk="deep", bend=-5)
    palm(d, 112, 140, 116, 112, .6, role="deep", trunk="deep", bend=4)
    sea(d, 138, "far", "mid", [(30, 150, 14), (100, 148, 16), (156, 154, 16), (40, 178, 18)])
    pirogue(d, 116, 172, .9, body="pir", stripe="light")
    sailboat(d, 64, 166, .7)


# ================================================================ concepts
NO_GOLD = ["coastal", "meadow", "blush", "dusk"]
WOOD = {"wood": "#9A6A3E", "wood2": "#6E4728"}
SKY_FIX = ["far", "mid", "sky2"]  # a deeper sky so white buildings stand out

CONCEPTS = [
    Concept("sky-adelaide", "skyline-adelaide", "Adelaide", adelaide, NO_GOLD,
            checks=[("mid", "far"), ("deep", "far"), ("deep", "sky"), ("light", "mid"), ("light", "deep"), ("near", "deep"), ("dark", "far")],
            fixes={"far": ["sky2", "mid"], "mid": ["near", "far"], "deep": ["dark"]}),
    Concept("sky-gold-coast", "skyline-gold-coast", "Gold Coast", gold_coast, NO_GOLD,
            checks=[("mid", "sky"), ("near", "mid"), ("near", "sky"), ("ground", "mid"), ("ground", "near"), ("light", "mid"), ("far", "sky")],
            fixes={"mid": ["far", "near"], "near": ["deep", "light"], "far": ["sky2", "mid"]}),
    Concept("sky-hobart", "skyline-hobart", "Hobart", hobart, NO_GOLD, overrides={"sand": "#DDB27A", "sand2": "#9C6E44"},
            checks=[("mid", "sky"), ("near", "mid"), ("deep", "near"), ("deep", "far"), ("light", "far"), ("sand", "far"), ("sand", "near")],
            fixes={"near": ["deep", "far"], "deep": ["dark", "near"], "mid": ["near", "far"], "sand": ["#C48A52", "#A8703F"]}),
    Concept("sky-darwin", "skyline-darwin", "Darwin", darwin, ["golden", "coastal", "blush", "dusk", "meadow"],
            checks=[("deep", "far"), ("deep", "sky"), ("deep", "glow"), ("dark", "sky"), ("dark", "glow"), ("deep", "mid")],
            fixes={"far": ["mid", "sky2"], "mid": ["near", "far"], "deep": ["dark"], "dark": ["deep"]}),
    Concept("sky-cairns", "skyline-cairns", "Cairns", cairns, NO_GOLD,
            checks=[("mid", "sky"), ("near", "mid"), ("light", "mid"), ("light", "near"), ("deep", "far"), ("deep", "light"), ("light", "far")],
            fixes={"mid": ["near", "far"], "near": ["deep", "mid"], "far": ["mid", "near"]}),
    Concept("sky-wellington", "skyline-wellington", "Wellington", wellington, NO_GOLD, overrides={"cable": "#C8372D", "bee": "#B9A88E"},
            checks=[("deep", "far"), ("near", "far"), ("near", "deep"), ("near", "sky"), ("light", "far"), ("light", "deep"),
                    ("cable", "deep"), ("light", "sky2")],
            fixes={"far": ["mid", "sky2"], "near": ["mid", "far"], "sky2": ["far", "mid"]}),
    Concept("sky-queenstown", "skyline-queenstown", "Queenstown", queenstown, NO_GOLD, overrides={"funnel": "#C8372D"},
            checks=[("light", "far"), ("mid", "far"), ("near", "sky2"), ("light", "sky2"), ("light", "near"), ("near", "sky")],
            fixes={"far": ["mid", "near"], "sky2": ["mid", "far"], "mid": ["near", "deep"], "near": ["deep", "mid"]}),
    Concept("sky-christchurch", "skyline-christchurch", "Christchurch", christchurch, NO_GOLD,
            overrides={**WOOD, "stone2": "#9C8664", "spire": "#7D7A74", "tram": "#B8352A"},
            checks=[("mid", "far"), ("light", "far"), ("light", "mid"), ("spire", "sky"), ("spire", "far"), ("deep", "near"), ("tram", "near"), ("light", "sky2")],
            fixes={"far": ["mid", "sky2"], "mid": ["near", "deep"], "sky2": ["far", "mid"], "deep": ["dark"], "spire": ["#A29C92", "#5E5A55"]}),
    Concept("sky-honolulu", "skyline-honolulu", "Honolulu", honolulu, NO_GOLD, overrides={**WOOD, "pink": "#F2A0B4", "pink2": "#C2667E"},
            checks=[("mid", "sky"), ("light", "mid"), ("light", "sky"), ("pink", "mid"), ("dark", "mid"), ("dark", "sky"), ("ground", "light"), ("far", "ground")],
            fixes={"sky": SKY_FIX, "mid": ["near", "deep"], "far": ["mid", "near"]}),
    Concept("sky-stone-town", "skyline-zanzibar-town", "Stone Town", stone_town, NO_GOLD,
            overrides={**WOOD, "fort": "#C9935C", "hw": "#5F6F6A", "hw2": "#A9B3AE"},
            checks=[("light", "sky"), ("light", "mid"), ("mid", "sky"), ("deep", "sky"), ("fort", "mid"), ("light", "near"), ("ground", "near")],
            fixes={"sky": SKY_FIX, "mid": ["near", "deep", "far"], "deep": ["dark"]}),
    Concept("sky-tunis", "skyline-tunis", "Tunis", tunis, NO_GOLD,
            overrides={"stone": "#E2C08E", "stone2": "#A97F4E", "pink": "#F08DA4", "pink2": "#9C4A5E"},
            checks=[("light", "far"), ("light", "sky"), ("stone", "sky"), ("stone", "far"), ("deep", "far"), ("pink", "mid"), ("light", "mid")],
            fixes={"sky": SKY_FIX, "far": ["mid", "near"], "mid": ["near", "deep"]}),
    Concept("sky-dakar", "skyline-dakar", "Dakar", dakar, NO_GOLD,
            overrides={"bronze": "#4A3A2E", "pir": "#2C8C7E", "pir2": "#D9573B"},
            checks=[("bronze", "sky"), ("bronze", "mid"), ("mid", "sky"), ("light", "mid"), ("deep", "mid"),
                    ("pir", "far"), ("pir2", "far")],
            fixes={"bronze": ["#6E5642", "#80654D"], "mid": ["near", "far"], "deep": ["dark"]}),
    Concept("sky-kigali", "skyline-kigali", "Kigali", kigali,
            checks=[("near", "far"), ("near", "sky"), ("hero", "far"), ("hero", "near"), ("hero", "mid"), ("light", "mid"), ("pop", "mid"), ("dark", "deep"), ("mid", "far"), ("dark", "mid")],
            fixes={"near": ["deep", "light"], "hero": ["pop", "hero2", "deep"], "mid": ["near", "deep"], "dark": ["far", "mid"]}),
    Concept("sky-windhoek", "skyline-windhoek", "Windhoek", windhoek, overrides={"roof": "#7A4A3A"},
            checks=[("mid", "far"), ("light", "sky"), ("light", "near"), ("light", "mid"), ("roof", "sky"), ("deep", "ground"), ("deep", "far")],
            fixes={"sky": SKY_FIX, "far": ["mid", "near"], "mid": ["near", "deep"], "deep": ["dark"]}),
    Concept("sky-durban", "skyline-durban", "Durban", durban, NO_GOLD,
            checks=[("mid", "far"), ("mid", "sky"), ("near", "sky"), ("light", "far"), ("light", "near"), ("ground", "mid"), ("light", "mid")],
            fixes={"far": ["sky2", "mid"], "mid": ["near", "far"], "near": ["deep", "dark"]}),
    Concept("sky-addis-ababa", "skyline-addis-ababa", "Addis Ababa", addis,
            overrides={"stone": "#E4D2B0", "stone2": "#A28B66", "dome": "#4F8C7A", "gold": "#E2B04A"},
            checks=[("mid", "far"), ("mid", "sky"), ("light", "mid"), ("light", "far"), ("dome", "far"), ("dome", "sky"), ("deep", "near")],
            fixes={"far": ["mid", "near"], "mid": ["near", "deep"], "deep": ["dark"]}),
    Concept("sky-beirut", "skyline-beirut", "Beirut", beirut, NO_GOLD,
            overrides={"stone": "#E8DCC6", "stone2": "#9F8F74", "dome": "#2F6FA8", "gold": "#E2B04A", "rock": "#C9A27C", "rock2": "#A07B57", "green": "#7E9B4E"},
            checks=[("light", "far"), ("mid", "far"), ("dome", "mid"), ("light", "mid"), ("rock", "far"), ("rock", "sky"), ("deep", "near")],
            fixes={"far": ["mid", "near"], "mid": ["near", "deep"], "deep": ["dark"], "rock": ["#B08660", "#9A7250"]}),
    Concept("sky-manama", "skyline-manama", "Manama", manama, NO_GOLD, overrides={**WOOD, "turb": "#56636F"},
            checks=[("near", "sky"), ("near", "far"), ("turb", "sky"), ("turb", "near"), ("mid", "far"), ("ground", "mid")],
            fixes={"far": ["mid", "sky2"], "mid": ["near", "deep"], "near": ["mid", "far", "deep"]}),
    Concept("sky-kuwait", "skyline-kuwait", "Kuwait City", kuwait, NO_GOLD,
            overrides={**WOOD, "shaft": "#5E6E80", "sphere": "#2C7FA8", "seq": "#9ED6DA"},
            checks=[("mid", "far"), ("shaft", "sky"), ("sphere", "sky"), ("sphere", "mid"), ("shaft", "ground"), ("near", "ground")],
            fixes={"far": ["mid", "near"], "mid": ["near", "deep"], "ground": ["light", "far"], "sky": ["sky2", "light"]}),
    Concept("sky-port-louis", "skyline-port-louis", "Port Louis", port_louis, NO_GOLD, overrides={"pir": "#2C8C7E", "sand": "#E8C79A"},
            checks=[("near", "far"), ("light", "near"), ("light", "far"), ("deep", "near"), ("deep", "light"), ("pir", "far"), ("sand", "near")],
            fixes={"near": ["mid", "deep"], "deep": ["dark", "near"]}),
]
