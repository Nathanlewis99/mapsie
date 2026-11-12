"""Mapsie Originals: landmarks of Australia, New Zealand and the Pacific / Indian Ocean islands.

Great Barrier Reef (Heart Reef), Whitehaven Beach, Bondi Icebergs, Flinders Street Station, Kata Tjuta,
Byron Bay lighthouse, Tongariro Emerald Lakes, Aoraki, Church of the Good Shepherd, Moeraki Boulders,
Pohutu geyser, That Wanaka Tree, Waitomo glowworms, Diamond Head, Na Pali Coast, Fiji, Maldives,
Port Arthur, Cradle Mountain, The Pinnacles.
"""
from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group  # noqa: F401
import math


# ================================================================ private helpers (copied, not imported)
def poly(*pts, close=True) -> str:
    s = "M" + " L".join(f"{x:g} {y:g}" for x, y in pts)
    return s + ("Z" if close else "")


def clipped(fn):
    """Wrap a whole drawing in the circle clip (line-style shapes are otherwise unclipped)."""
    def draw(d: Drawing):
        d.raw('<g clip-path="url(#clip)">', '<g clip-path="url(#clip)">')
        fn(d)
        d.raw("</g>", "</g>")
    draw.__name__ = fn.__name__
    return draw


def birds(d: Drawing, pts, role="dark"):
    s = " ".join(f"M{x} {y} q{3 * k} {-3 * k} {6 * k} 0 q{3 * k} {-3 * k} {6 * k} 0" for x, y, k in pts)
    d.stroke(role, s, 1.7)


def stars(d: Drawing, pts, role="light"):
    for x, y, r in pts:
        d.marks(role, f"M{x} {y - r} L{x + r * .3} {y - r * .3} L{x + r} {y} L{x + r * .3} {y + r * .3} "
                      f"L{x} {y + r} L{x - r * .3} {y + r * .3} L{x - r} {y} L{x - r * .3} {y - r * .3}Z")


def frond(x, y, ang, length, droop, w=0.22) -> str:
    a = math.radians(ang)
    ex, ey = x + length * math.cos(a), y + length * math.sin(a) + droop
    mx, my = (x + ex) / 2, (y + ey) / 2 - droop * .6
    nx, ny = -(ey - y), ex - x
    k = w / 2
    return (f"M{x:.1f} {y:.1f} Q{mx + nx * k:.1f} {my + ny * k:.1f} {ex:.1f} {ey:.1f} "
            f"Q{mx - nx * k * .3:.1f} {my - ny * k * .3:.1f} {x:.1f} {y:.1f}Z")


def palm(d: Drawing, x0, y0, x1, y1, s=1.0, role="dark", trunk="dark", bend=10):
    d.limb(trunk, f"M{x0} {y0} Q{(x0 + x1) / 2 + bend} {(y0 + y1) / 2} {x1} {y1}", 4.2 * s)
    leaves = " ".join(frond(x1, y1, a, L * s, dr * s) for a, L, dr in
                      [(-170, 26, 10), (-130, 22, 4), (-90, 16, -2), (-50, 22, 4), (-10, 26, 10), (150, 20, 12), (30, 20, 12)])
    d.shape(role, leaves)


def reflect(d: Drawing, path: str, y: float, role: str, opacity=.22):
    """Papercut-only mirror image of a path about the waterline y."""
    if d.paper:
        d.raw(f'<path d="{path}" fill="{d.c[role]}" opacity="{opacity}" transform="matrix(1 0 0 -1 0 {2 * y})"/>')


def seaplane(d: Drawing, body="hero", trim="hero2", floats="dark"):
    """A float plane facing right, roughly x 26-172, y 64-138 (from air_snow)."""
    d.stroke("dark", "M104 74 L96 98 M128 74 L120 96", 1.8)
    d.stroke(floats, "M74 104 L70 126 M90 106 L92 126 M130 106 L134 126 M146 104 L148 126", 2.4)
    d.shape(floats, "M56 124 H160 Q170 124 174 118 C176 124 172 134 156 136 H66 Q56 136 56 130Z")
    d.shape(body, "M24 64 L38 64 L60 90 L34 94Z")
    d.shape(body, "M30 92 C40 86 64 82 100 80 L140 80 C154 80 162 86 164 94 C164 102 158 108 146 108 L100 110 C70 108 44 102 30 96Z")
    d.shape(trim, "M30 64 L38 64 L56 86 L42 88Z", shadow=False, spot=True)
    d.shape(trim, "M48 98 C70 103 90 104 100 104 L162 101 C160 105 154 108 146 108 L100 110 C76 109 60 106 48 98Z", shadow=False, spot=True)
    d.shape("light", "M122 84 H140 C148 84 154 88 156 94 H122Z", shadow=False)
    d.shape("dark", rrect(82, 70, 72, 6, 3))
    d.shape("dark", ellipse(168, 94, 2.6, 15))


def heart(cx, top, w, h) -> str:
    return (f"M{cx} {top + .2 * h} C{cx - .1 * w} {top - .05 * h} {cx - .5 * w} {top - .08 * h} {cx - .5 * w} {top + .3 * h} "
            f"C{cx - .5 * w} {top + .6 * h} {cx - .15 * w} {top + .78 * h} {cx} {top + h} "
            f"C{cx + .15 * w} {top + .78 * h} {cx + .5 * w} {top + .6 * h} {cx + .5 * w} {top + .3 * h} "
            f"C{cx + .5 * w} {top - .08 * h} {cx + .1 * w} {top - .05 * h} {cx} {top + .2 * h}Z")


def dome(x0, x1, b, top) -> str:
    """A steep-sided rounded rock dome (Kata Tjuta), feet at y=b."""
    w, h = x1 - x0, b - top
    return (f"M{x0} {b} C{x0 + w * .03:.1f} {top + h * .3:.1f} {x0 + w * .2:.1f} {top} {x0 + w * .5:.1f} {top} "
            f"C{x1 - w * .2:.1f} {top} {x1 - w * .03:.1f} {top + h * .3:.1f} {x1} {b}Z")


def dome_shade(x0, x1, b, top) -> str:
    w, h = x1 - x0, b - top
    return (f"M{x0 + w * .62:.1f} {top + 1} C{x1 - w * .2:.1f} {top} {x1 - w * .03:.1f} {top + h * .3:.1f} {x1} {b} "
            f"H{x1 - w * .2:.1f} C{x1 - w * .14:.1f} {top + h * .45:.1f} {x1 - w * .2:.1f} {top + h * .12:.1f} {x0 + w * .62:.1f} {top + 1}Z")


def spike(x, y, h, w) -> str:
    """A lupin flower spike: a stack of florets narrowing to the tip, base at (x, y)."""
    n = 8
    s = ""
    for i in range(n):
        t = i / n
        r = w / 2 * (1 - t * .75)
        cy = y - 3 - h * t
        s += circle(round(x + (1.2 if i % 2 else -1.2) * (1 - t), 1), round(cy, 1), round(r, 2)) + " "
    s += circle(x, y - 3 - h * .97, w * .12)
    return s


def lupin(d: Drawing, x, y, h, w, role):
    d.stroke("leaf", f"M{x} {y + 14} V{y - 2}", 2)
    d.shape(role, spike(x, y, h, w))


def boulder_cracks(cx, cy, r) -> str:
    """Septarian veins: a loose net of polygonal cracks on a sphere."""
    pts = [(-.5, -.3), (-.1, -.55), (.35, -.4), (.55, .05), (.25, .45), (-.25, .5), (-.6, .15), (0, -.02)]
    P = [(cx + r * x, cy + r * y) for x, y in pts]
    segs = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 0), (7, 0), (7, 2), (7, 4), (7, 6)]
    return " ".join(f"M{P[a][0]:.1f} {P[a][1]:.1f} L{P[b][0]:.1f} {P[b][1]:.1f}" for a, b in segs)


# ================================================================ HEART REEF
def heart_reef(d: Drawing):
    d.disc("glow", 150, 26, 10)
    d.band("sea2", "M-30 44 H230")
    d.band("sea", "M-30 52 Q100 49 230 52", shadow=False, line=False)
    # outer reef flats along the horizon
    d.shape("reef", ellipse(30, 62, 46, 4) + ellipse(160, 60, 52, 4.5), shadow=False)
    d.shape("reef2", ellipse(26, 62, 30, 2) + ellipse(166, 60, 32, 2.2), shadow=False, line=False)
    # the heart, seen from the air, tilted a little
    def h():
        d.shape("halo", heart(100, 84, 136, 104), shadow=False)
        d.shape("coral", heart(100, 92, 108, 82), spot=True)
        d.shape("halo", heart(100, 104, 66, 50), shadow=False)
        d.marks("coral2", " ".join(circle(x, y, r) for x, y, r in
                                   [(64, 104, 3), (74, 98, 2.4), (126, 98, 2.6), (138, 106, 3), (70, 124, 2.6),
                                    (132, 126, 2.4), (90, 150, 2.4), (110, 148, 2.6), (100, 162, 2), (56, 114, 2), (144, 116, 2)]))
    group(d, "translate(100 130) rotate(-10) scale(1 .86) translate(-100 -130)", h)
    d.stroke("light", "M18 96 q8 -4 16 0 M160 160 q8 -4 16 0 M24 168 q8 -4 16 0 M168 92 q6 -3 12 0", 2)
    group(d, "translate(30 66) scale(.28)", lambda: seaplane(d, body="light", trim="pop"))


# ================================================================ WHITEHAVEN BEACH
def whitehaven(d: Drawing):
    d.band("sea2", "M-30 54 H230")
    # Hill Inlet: white silica sand swirling through turquoise shallows
    d.band("lagoon", "M-30 66 Q60 60 120 66 T230 62")
    d.shape("chan", "M-30 96 C30 84 60 116 110 104 C150 94 172 70 230 74 V86 C182 82 160 108 116 120 C66 134 30 104 -30 112Z",
            shadow=False, line=False)
    swirls = [
        "M4 80 C40 66 96 68 126 78 C146 85 156 96 140 100 C124 90 92 84 62 88 C40 91 18 92 4 80Z",
        "M-30 130 C20 112 60 142 110 134 C150 128 170 106 200 100 C216 97 232 102 230 110 C200 110 182 130 150 146 C110 164 50 152 -30 154Z",
        "M44 176 C80 162 136 170 166 158 C186 150 194 138 210 140 C206 162 180 178 140 184 C100 190 62 188 44 176Z",
        "M150 84 C170 76 196 74 214 80 C200 84 178 92 160 94 C150 94 144 90 150 84Z",
    ]
    for p in swirls:
        d.stroke("lagoon2", p, 9, line=False)
    for i, p in enumerate(swirls):
        d.shape("sand", p, spot=i == 1)
    # forested headlands
    d.shape("forest", "M-30 52 Q0 44 26 48 Q52 52 62 62 Q56 72 30 72 Q0 74 -30 72Z")
    d.shape("forest2", "M-30 58 Q8 54 30 60 Q46 66 40 70 Q10 74 -30 72Z", shadow=False, line=False)
    d.shape("forest", "M230 150 Q196 152 176 168 Q156 186 152 230 H230Z")
    d.shape("forest2", "M230 166 Q202 168 188 182 Q174 196 172 230 H230Z", shadow=False, line=False)
    for x, y, r in [(184, 160, 8), (200, 154, 9), (216, 152, 8), (170, 176, 7)]:
        d.shape("forest", circle(x, y, r), shadow=False)


# ================================================================ BONDI ICEBERGS
def bondi(d: Drawing):
    d.disc("glow", 150, 40, 12)
    # north Bondi, across the bay
    d.band("far", "M-30 74 Q40 66 90 70 Q120 72 140 76 H230")
    d.band("sea", "M-30 80 H230")
    d.shape("sand", "M70 80 Q130 92 230 82 V88 Q130 100 70 82Z", shadow=False)
    d.stroke("light", "M20 92 h16 M56 98 h18", 2)
    # the Icebergs clubhouse on the south cliff
    d.shape("rock", "M96 230 V118 Q120 104 150 102 L230 98 V230Z")
    d.shape("light", "M104 112 V92 H146 V86 H186 V104 L230 104 V112Z")
    d.shape("trim", rrect(104, 92, 42, 3, 0) + rrect(146, 86, 40, 3, 0), shadow=False, spot=True)
    d.marks("glass", " ".join(rrect(108 + i * 9, 98, 6, 6, 1) for i in range(4)) + " " +
            " ".join(rrect(150 + i * 9, 92, 6, 6, 1) for i in range(4)))
    # the ocean pool on the rock shelf, waves pounding its seaward wall
    d.band("sea", "M-30 116 Q40 112 100 118 H230", line=False)
    d.shape("rock", "M-30 230 V166 Q20 160 40 170 L60 176 L200 152 L230 150 V230Z")
    d.shape("deck", "M18 132 L178 116 L196 150 L36 174Z")
    d.shape("pool", "M26 135 L174 120 L189 148 L41 169Z", shadow=False, spot=True)
    for t in (.25, .5, .75):
        x0, y0 = 26 + 15 * t, 135 + 34 * t
        x1, y1 = 174 + 15 * t, 120 + 28 * t
        d.stroke("light", f"M{x0 + 4:.1f} {y0 - .4:.1f} L{x1 - 4:.1f} {y1 + .4:.1f}", 1.4)
    d.stroke("deck", "M18 132 L36 174", 2, line=False)
    # whitewater spilling over the wall
    d.shape("light", "M-30 128 Q-10 112 6 120 Q10 100 26 104 Q34 92 46 102 Q54 98 56 110 Q48 118 36 126 L32 140 Q14 150 -30 152Z")
    d.shape("foam", "M30 128 Q40 132 52 130 Q62 132 66 138 Q52 140 38 136Z", shadow=False, line=False)
    d.stroke("light", "M-10 166 q8 -4 16 0 M50 186 q8 -4 16 0", 2, line=False)


# ================================================================ FLINDERS STREET STATION
def _flinders(d: Drawing):
    # wings
    d.shape("wall", "M6 172 V108 H194 V172Z")
    d.shape("trim", rrect(4, 104, 192, 6, 1) + rrect(6, 136, 188, 4, 0), shadow=False)
    for x in list(range(12, 60, 12)) + list(range(142, 146, 12)):
        d.marks("glass", f"M{x} 128 V118 Q{x + 3.5} 113 {x + 7} 118 V128Z M{x} 156 V146 Q{x + 3.5} 141 {x + 7} 146 V156Z")
    # clock tower at the corner
    d.shape("wall", "M150 172 V50 H178 V172Z")
    d.shape("trim", rrect(148, 48, 32, 4, 1) + rrect(150, 92, 28, 3, 0) + rrect(150, 104, 28, 3, 0), shadow=False)
    d.shape("copper", "M150 48 Q150 32 164 28 Q178 32 178 48Z")
    d.stroke("dark", "M164 28 V18", 1.6)
    d.shape("clock", circle(164, 68, 8.5), spot=True)
    d.stroke("dark", "M164 68 V62 M164 68 L168 70", 1.4)
    d.marks("glass", "M159 88 V80 Q164 75 169 80 V88Z M159 128 V116 Q164 111 169 116 V128Z M159 156 V146 Q164 141 169 146 V156Z")
    # central pavilion with the big arched window and the dome
    d.shape("wall", "M62 172 V66 H138 V172Z")
    d.shape("trim", rrect(60, 62, 80, 6, 1), shadow=False)
    d.shape("trim", rrect(72, 52, 56, 11, 2))
    d.shape("copper", "M72 54 C70 34 84 22 100 22 C116 22 130 34 128 54Z")
    d.stroke("copper2", "M86 52 Q86 32 100 23 M114 52 Q114 32 100 23 M100 23 V52", 1.4, line=False)
    d.shape("trim", rrect(96, 14, 8, 9, 1.5))
    d.shape("copper", "M95 15 Q100 6 105 15Z", shadow=False)
    d.stroke("dark", "M100 8 V2", 1.4)
    d.shape("glass", "M74 124 V96 A26 26 0 0 1 126 96 V124Z", shadow=False)
    d.stroke("trim", "M87 124 V80 M100 124 V70 M113 124 V80 M74 104 H126", 1.6, line=False)
    d.shape("trim", "M70 126 V96 A30 30 0 0 1 130 96 V126 H125 V96 A25 25 0 0 0 75 96 V126Z", shadow=False)
    # "under the clocks": the row of clocks over the entrance
    d.shape("dark", "M70 172 V140 H130 V172Z", shadow=False)
    d.shape("trim", rrect(66, 126, 68, 6, 1))
    for i in range(5):
        x = 76 + i * 12
        d.shape("clock", circle(x, 142, 4.4), shadow=False)
        d.stroke("dark", f"M{x} 142 V139 M{x} 142 L{x + 2} 143", 1, line=False)
    # a green tram rolling past
    d.band("road", "M-30 172 H230")
    d.stroke("dark", "M54 148 L74 134", 1.4)
    d.shape("tram", "M-20 176 V158 Q-20 150 -12 150 H58 Q66 150 66 158 V176Z")
    d.shape("trim", rrect(-20, 154, 86, 10, 0), shadow=False)
    d.marks("dark", " ".join(rrect(-12 + i * 12, 155.5, 9, 7, 1.2) for i in range(7)))
    d.marks("dark", circle(6, 178, 3.2) + circle(46, 178, 3.2))


def flinders(d: Drawing):
    group(d, "translate(100 190) scale(.9) translate(-100 -190)", lambda: _flinders(d))
    d.band("road", "M-30 180 H230", line=False)


# ================================================================ KATA TJUTA
def kata_tjuta(d: Drawing):
    d.disc("glow", 152, 50, 15)
    domes_back = [(-8, 44, 146, 92), (150, 206, 146, 88)]
    domes_mid = [(30, 82, 146, 74), (112, 166, 146, 66)]
    domes_front = [(60, 138, 146, 46), (-4, 52, 146, 102), (142, 204, 146, 106), (102, 146, 146, 112)]
    for x0, x1, b, t in domes_back:
        d.shape("rock3", dome(x0, x1, b, t))
    for x0, x1, b, t in domes_mid:
        d.shape("rock2", dome(x0, x1, b, t))
        d.shape("rock3", dome_shade(x0, x1, b, t), shadow=False, line=False)
    for i, (x0, x1, b, t) in enumerate(domes_front):
        d.shape("rock", dome(x0, x1, b, t), spot=i == 0)
        d.shape("rock2", dome_shade(x0, x1, b, t), shadow=False, line=False)
    d.stroke("rock2", "M82 60 Q78 90 80 140 M98 50 Q96 90 98 136 M116 58 Q120 96 116 140 M18 112 Q14 126 16 142 M162 114 Q160 128 164 142",
             1.8, line=False)
    d.band("earth", "M-30 144 Q100 139 230 144")
    for x, y, s in [(22, 160, 1), (60, 166, .8), (140, 160, .9), (180, 168, 1.1), (100, 172, .7)]:
        d.shape("bush", " ".join(f"M{x + k * s} {y} L{x + k * 1.6 * s} {y - 11 * s + abs(k) * .5 * s} L{x + k * s + 2 * s} {y}Z"
                                 for k in (-8, -4, 0, 4, 8)), shadow=True)
    d.limb("dark", "M40 182 L42 150 M42 160 L32 146 M42 156 L52 142", 3)
    d.shape("dark", ellipse(32, 142, 8, 5) + ellipse(52, 138, 8, 5) + ellipse(42, 134, 9, 6), shadow=False)
    d.band("near", hills(182, 4, 20), line=False)


# ================================================================ BYRON BAY LIGHTHOUSE
FLUKE = ("M88 156 C90 130 92 112 95 100 C78 96 54 84 38 62 C34 56 40 53 46 57 C64 70 84 74 100 80 "
         "C116 74 136 70 154 57 C160 53 166 56 162 62 C146 84 122 96 105 100 C108 112 110 130 112 156Z")


def byron(d: Drawing):
    d.disc("glow", 46, 50, 13)
    d.band("sea", "M-30 116 H230")
    d.stroke("light", "M10 128 h16 M40 140 h14 M8 152 h18", 2)
    group(d, "translate(36 104) scale(.26) translate(-100 -100)", lambda: d.shape("whale", FLUKE))
    # the headland
    d.shape("cliff", "M60 230 L66 150 Q70 128 90 124 L230 112 V230Z")
    d.shape("grass", "M84 128 Q100 118 130 116 L230 110 V136 Q160 140 120 138 Q96 136 84 128Z")
    d.shape("light", cloud(-6, 172, 1.4), shadow=False)
    d.stroke("cliff2", "M80 150 L76 190 M96 146 L94 186 M70 170 L68 200", 1.6, line=False)
    # keeper's cottage
    d.shape("light", rrect(140, 108, 34, 16, 1))
    d.shape("roof", "M136 110 L144 98 H170 L178 110Z")
    d.marks("glass", rrect(146, 113, 5, 6, 1) + rrect(162, 113, 5, 6, 1))
    # the lighthouse
    d.shape("light", "M102 124 L106 64 H124 L128 124Z", spot=False)
    d.shape("shade", "M117 64 H124 L128 124 H119Z", shadow=False, line=False)
    d.shape("light", rrect(96, 118, 38, 8, 2))
    d.shape("roof", rrect(102, 60, 26, 5, 1.5))
    d.shape("glass", rrect(107, 48, 16, 12, 1), shadow=False)
    d.stroke("roof", "M112 48 V60 M118 48 V60", 1.2, line=False)
    d.shape("roof", "M104 49 Q105 36 115 34 Q125 36 126 49Z", spot=True)
    d.stroke("roof", "M115 34 V28", 1.6)
    d.marks("glass", rrect(112, 82, 6, 8, 1.5) + rrect(111.5, 104, 7, 10, 2))
    d.band("grass2", "M-30 230 L60 200 Q120 168 230 160 V230", line=False)


# ================================================================ TONGARIRO EMERALD LAKES
def tongariro(d: Drawing):
    d.shape("light", cloud(140, 42, 1.0), shadow=False)
    # Ngauruhoe, the perfect cone, behind
    d.shape("ash2", "M8 120 L58 40 Q64 34 70 40 L124 120Z")
    d.shape("ash", "M64 37 L70 40 L124 120 H84 Q76 80 64 37Z", shadow=False, line=False)
    # Red Crater ridge
    d.band("red", "M-30 118 Q30 92 70 98 Q96 100 120 84 Q150 70 170 82 Q196 96 230 98")
    d.shape("red2", "M120 84 Q150 70 170 82 Q160 96 140 110 Q130 98 120 84Z", shadow=False, line=False)
    d.raw('<path d="M136 92 C128 80 136 66 146 72 C150 60 164 62 162 76 C170 76 170 88 160 90Z" fill="#fff" opacity=".7"/>', "")
    d.band("scree", "M-30 132 Q60 118 120 124 T230 120")
    # the three emerald lakes
    for cx, cy, rx, ry, role in [(150, 128, 26, 6, "lake2"), (56, 144, 40, 10, "lake"), (136, 164, 46, 13, "lake3")]:
        d.shape("rim", ellipse(cx, cy, rx + 4, ry + 3), shadow=False)
        d.shape(role, ellipse(cx, cy + .5, rx, ry), spot=True)
        d.shape("lakehi", ellipse(cx - rx * .25, cy - ry * .2, rx * .5, ry * .35), shadow=False, line=False)
    d.raw('<path d="M22 132 C16 122 24 112 32 118 C34 108 46 110 44 120 C50 122 48 130 42 130Z" fill="#fff" opacity=".6"/>', "")
    d.band("scree2", "M-30 190 Q60 178 100 186 Q150 194 230 184", line=False)


# ================================================================ AORAKI / MOUNT COOK
AORAKI = "M-30 118 L10 100 L30 92 L52 70 L70 62 L84 46 L94 34 L100 30 L108 40 L122 48 L140 62 L160 78 L178 86 L230 104"


def aoraki(d: Drawing):
    d.disc("glow", 160, 44, 11)
    d.band("far", "M-30 104 L-4 88 L16 96 L40 84 L60 100 L230 110", line=False)
    d.band("snow", AORAKI)
    d.shape("snow2", "M100 30 L108 40 L122 48 L140 62 L160 78 L178 86 L230 104 V120 H118 Q114 86 104 60 Z", shadow=False, line=False)
    d.stroke("snow2", "M84 46 L76 80 M70 62 L62 94 M52 70 L46 96 M122 48 L130 78 M140 62 L150 92", 1.4, line=False)
    d.band("rock", "M-30 124 L10 108 L30 112 L50 98 L70 108 L90 96 L110 106 L136 98 L160 108 L184 100 L230 112")
    d.band("lake", "M-30 128 H230")
    d.stroke("light", "M30 140 h22 M110 136 h18 M150 146 h20 M70 150 h14", 2)
    d.band("tussock", "M-30 160 Q40 150 90 158 T230 156")
    for x, y in [(20, 160), (52, 156), (150, 158), (178, 160), (96, 164)]:
        d.shape("tussock2", " ".join(f"M{x + k} {y + 2} Q{x + k * 1.8} {y - 10} {x + k * 2.4} {y - 14} Q{x + k * 1.2} {y - 6} {x + k + 2} {y + 2}Z"
                                     for k in (-5, -2, 1, 4)), shadow=False)
    d.band("tussock2", hills(184, 4, 20), line=False)


# ================================================================ CHURCH OF THE GOOD SHEPHERD
def tekapo(d: Drawing):
    d.band("far", "M-30 96 L0 78 L22 86 L48 66 L74 88 L96 74 L126 90 L150 70 L180 84 L230 76")
    d.shape("light", "M48 66 L56 74 L52 73 L48 77 L44 72 L40 74Z M150 70 L158 77 L154 76 L150 80 L146 75 L142 77Z "
                     "M-0 78 L6 82 L2 82 L-2 84Z", shadow=False, line=False)
    d.band("lake", "M-30 98 H230")
    d.stroke("light", "M14 110 h18 M54 106 h14 M160 108 h16", 2)
    d.band("shore", "M-30 132 Q60 122 120 128 T230 124")
    # the little stone church
    d.shape("stone", "M96 140 V108 H156 V140Z")
    d.shape("stone", "M156 140 V104 L170 88 L184 104 V140Z")
    d.shape("roof", "M92 110 L104 80 H168 L162 92 L156 108Z")
    d.shape("roof2", "M156 106 L170 86 L186 106 L183 108 L170 92 L159 108Z", shadow=False)
    d.stroke("roof", "M170 86 V76 M166 80 H174", 2)
    d.shape("stone", "M110 140 V122 L118 114 L126 122 V140Z")
    d.marks("dark", "M115 140 V126 Q118 122 121 126 V140Z")
    d.marks("glass", "M140 132 V120 Q143 116 146 120 V132Z M166 128 V108 Q170 102 174 108 V128Z")
    d.marks("stone2", " ".join(ellipse(x, y, 2.4, 1.6) for x, y in
                               [(100, 114), (104, 126), (100, 134), (132, 112), (136, 126), (150, 114), (150, 134), (130, 136),
                                (160, 112), (180, 112), (162, 134), (178, 134), (106, 118)]))
    # lupins
    d.band("meadow", "M-30 150 Q40 140 100 146 T230 142")
    spikes = [(14, 150, 46, 11, "lup1"), (30, 154, 56, 12, "lup2"), (46, 152, 40, 10, "lup3"), (62, 160, 50, 12, "lup1"),
              (80, 164, 36, 10, "lup2"), (150, 160, 34, 10, "lup3"), (168, 156, 48, 12, "lup2"), (186, 152, 40, 11, "lup1"),
              (6, 172, 42, 11, "lup3"), (40, 178, 46, 12, "lup1"), (128, 174, 30, 9, "lup1"), (100, 182, 34, 10, "lup3")]
    for x, y, h, w, role in spikes:
        lupin(d, x, y, h, w, role)
    d.band("leaf", hills(184, 5, 20), line=False)
    d.shape("leaf", " ".join(ellipse(x, y, 9, 3.4) for x, y in [(20, 182), (60, 186), (150, 180), (180, 178)]), shadow=False, line=False)


# ================================================================ MOERAKI BOULDERS
def moeraki(d: Drawing):
    d.disc("glow", 64, 96, 20)
    d.band("sea", "M-30 96 H230")
    d.stroke("light", "M110 104 h22 M150 110 h18 M20 112 h18", 2)
    d.band("surf", waves(118, 2.5, 20), shadow=False)
    d.band("wet", "M-30 122 Q100 118 230 122")
    for cx, cy, r in [(146, 112, 11), (30, 132, 18), (166, 140, 24), (82, 146, 34)]:
        reflect(d, circle(cx, cy, r), cy + r * .9, "boulder", .25)
    for cx, cy, r in [(146, 112, 11), (30, 132, 18), (166, 140, 24), (82, 146, 34)]:
        d.shape("boulder", circle(cx, cy, r), spot=r > 30)
        d.shape("boulder2", f"M{cx + r * .2:.1f} {cy - r * .97:.1f} A{r} {r} 0 0 1 {cx - r * .5:.1f} {cy + r * .86:.1f} "
                            f"A{r * 1.1:.1f} {r * 1.1:.1f} 0 0 0 {cx + r * .2:.1f} {cy - r * .97:.1f}Z", shadow=False, line=False)
        d.stroke("crack", boulder_cracks(cx - r * .1, cy - r * .05, r), max(1.0, r * .06))
        d.shape("light", ellipse(cx - r * .45, cy - r * .5, r * .16, r * .1), shadow=False, line=False)
        d.shape("foam", ellipse(cx, cy + r * .92, r * .95, r * .14), shadow=False, line=False)
    d.stroke("light", "M20 176 q10 -4 20 0 M120 182 q10 -4 20 0", 2)


# ================================================================ POHUTU GEYSER
def pohutu(d: Drawing):
    d.band("bush", "M-30 120 Q10 100 40 106 Q70 96 100 104 Q140 92 170 104 Q200 98 230 108")
    for x, y, r in [(10, 108, 12), (40, 102, 10), (168, 100, 12), (196, 104, 10)]:
        d.shape("bush", circle(x, y, r), shadow=False)
    # the column of boiling water and steam
    plume = ("M92 140 C90 120 86 100 82 84 C70 80 66 66 74 58 C64 50 70 34 84 36 C86 22 104 16 112 28 C126 22 140 34 132 46 "
             "C144 52 140 70 126 72 C120 90 112 116 108 140Z")
    d.shape("steam", plume)
    d.shape("steam2", "M108 140 C112 116 120 90 126 72 C140 70 144 52 132 46 C138 60 128 66 118 66 C112 90 104 116 100 140Z", shadow=False, line=False)
    d.shape("steam", cloud(120, 44, .9), shadow=False, line=False)
    d.raw('<path d="M84 36 C72 26 76 12 90 14 C96 2 116 4 118 16 C130 12 140 24 132 34Z" fill="#fff" opacity=".75"/>', "")
    d.stroke("steam2", "M96 132 V96 M102 136 V88 M90 120 V100", 1.6, line=False)
    # sinter terraces
    d.shape("sinter", "M-30 230 V148 Q20 138 60 140 Q80 130 100 136 Q130 130 150 138 Q190 136 230 144 V230Z")
    d.shape("sinter2", "M-30 158 Q20 150 64 152 Q90 146 110 150 Q150 146 230 154 V162 Q150 156 112 160 Q80 156 60 162 Q20 160 -30 168Z",
            shadow=False, line=False)
    d.shape("sinter3", "M-30 176 Q40 168 100 172 Q160 168 230 176 V184 Q160 176 100 180 Q40 178 -30 186Z", shadow=False, line=False)
    d.stroke("sinter2", "M30 146 Q50 144 60 148 M130 142 Q150 140 168 146", 1.6)
    d.marks("dark", ellipse(100, 138, 9, 2.6))
    # a carved pou watching over the valley
    d.shape("carve", "M30 160 V100 Q30 88 40 86 Q50 88 50 100 V160Z")
    d.shape("carve2", rrect(26, 156, 28, 8, 2))
    for y in (124, 140):
        d.stroke("carve2", f"M32 {y} Q40 {y + 6} 48 {y} M32 {y + 6} Q40 {y + 12} 48 {y + 6}", 1.4, line=False)
    d.shape("paua", circle(35.5, 100, 3.6) + circle(44.5, 100, 3.6), shadow=False)
    d.marks("dark", circle(35.5, 100, 1.4) + circle(44.5, 100, 1.4))
    d.marks("carve2", "M36 110 Q40 116 44 110 L42 118 H38Z")


# ================================================================ THAT WANAKA TREE
def fringe(cx, cy, rx, ry) -> str:
    """A willow clump: rounded top, ragged hanging fringe below."""
    s = f"M{cx - rx} {cy} A{rx} {ry} 0 0 1 {cx + rx} {cy}"
    n = 9
    drops = [.7, 1.1, .5, .95, .6, 1.2, .55, .9, .65]
    for i in range(n, 0, -1):
        x = cx - rx + 2 * rx * (i - .5) / n
        s += f" L{x:.1f} {cy + ry * drops[i - 1]:.1f} L{cx - rx + 2 * rx * (i - 1) / n:.1f} {cy + ry * .2:.1f}"
    return s + "Z"


WILLOW_CLUMPS = [(108, 82, 24, 15), (88, 96, 20, 13), (128, 92, 22, 14), (110, 98, 20, 11), (142, 112, 14, 10)]
WILLOW = " ".join(fringe(*c) for c in WILLOW_CLUMPS)



def wanaka(d: Drawing):
    d.disc("glow", 46, 50, 12)
    d.band("far", "M-30 104 L4 82 L26 92 L54 70 L84 90 L112 80 L142 94 L170 74 L198 88 L230 82")
    d.shape("light", "M54 70 L62 77 L58 76 L54 80 L50 75 L46 77Z M170 74 L178 81 L174 80 L170 84 L166 79 L162 81Z "
                     "M4 82 L10 86 L6 86 L2 88Z", shadow=False, line=False)
    d.band("mid", "M-30 112 Q30 100 70 108 Q120 100 160 110 Q200 104 230 108")
    d.band("lake", "M-30 116 H230")
    trunk = "M114 160 Q110 142 104 128 Q98 114 102 100 M104 128 Q116 118 126 106 M108 138 Q122 132 136 124"
    if d.paper:
        d.raw(f'<g opacity=".25" transform="translate(112 160) scale(1.1 -1.1) translate(-112 -160)"><path d="{trunk}" fill="none" stroke="{d.c["bark"]}" '
              f'stroke-width="5" stroke-linecap="round"/><path d="{WILLOW}" fill="{d.c["leaf"]}"/></g>')
    d.stroke("light", "M20 132 h22 M150 136 h20 M30 176 h16 M150 180 h24", 2)
    def tree():
        d.limb("bark", trunk, 5.5)
        d.shape("leaf", WILLOW, spot=True)
        d.stroke("leaf2", " ".join(f"M{cx - rx * .5:.1f} {cy - ry * .2:.1f} L{cx - rx * .55:.1f} {cy + ry * .5:.1f} M{cx + rx * .1:.1f} {cy - ry * .4:.1f} "
                                   f"L{cx + rx * .1:.1f} {cy + ry * .6:.1f} M{cx + rx * .6:.1f} {cy - ry * .1:.1f} L{cx + rx * .62:.1f} {cy + ry * .5:.1f}"
                                   for cx, cy, rx, ry in WILLOW_CLUMPS), 1.4, line=False)
    group(d, "translate(112 160) scale(1.1) translate(-112 -160)", tree)
    d.stroke("lakehi", "M96 162 Q114 158 132 162", 2.4)


# ================================================================ WAITOMO GLOWWORM CAVES
def waitomo(d: Drawing):
    d.band("deep", "M-30 -30 H230")
    d.shape("dark", "M-30 -30 H230 V60 Q200 40 170 36 Q140 30 100 30 Q60 30 30 40 Q0 50 -30 70Z")
    import random
    rnd = random.Random(7)
    pts = []
    for _ in range(70):
        x = rnd.uniform(4, 196)
        y = rnd.uniform(36, 112) - (0 if 20 < x < 180 else -10)
        pts.append((x, y, rnd.uniform(.9, 2.1)))
    if d.paper:
        d.raw('<g fill="' + d.c["glowd"] + '" opacity=".28">' + "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 2.4:.1f}"/>' for x, y, r in pts) + "</g>")
        d.raw('<g stroke="' + d.c["glowd"] + '" stroke-width=".6" opacity=".55">' +
              "".join(f'<path d="M{x:.1f} {y:.1f} v{6 + r * 6:.1f}"/>' for x, y, r in pts[::3]) + "</g>")
    d.marks("glowd", " ".join(circle(round(x, 1), round(y, 1), round(r, 2)) for x, y, r in pts))
    # cave walls
    d.shape("dark", "M-30 230 V60 Q4 70 12 110 Q16 140 30 150 H-30Z")
    d.shape("dark", "M230 230 V56 Q198 66 186 104 Q180 136 168 150 H230Z")
    # still water, reflecting the stars on the ceiling
    d.band("water", "M-30 150 H230")
    if d.paper:
        d.raw('<g fill="' + d.c["glowd"] + '" opacity=".45">' +
              "".join(f'<circle cx="{x:.1f}" cy="{300 - y + 10:.1f}" r="{r * .8:.1f}"/>' for x, y, r in pts if 300 - y + 10 > 156) + "</g>")
    # the boat, gliding through the dark
    d.shape("boat", "M56 158 H144 L136 168 H64Z", spot=True)
    d.shape("boat", " ".join(circle(x, 151, 4) + " " + rrect(x - 5, 152, 10, 8, 3) for x in (76, 92, 108, 124)), shadow=False)
    d.stroke("glowd", "M40 172 h22 M140 174 h22", 1.4)


# ================================================================ DIAMOND HEAD
DIAMOND = ("M-30 126 Q10 120 34 110 Q58 96 86 90 Q108 86 124 84 L134 78 L142 66 L150 58 L156 62 L162 74 "
           "Q170 92 184 110 Q198 122 230 128")


def diamond_head(d: Drawing):
    d.disc("glow", 60, 54, 13)
    d.shape("light", cloud(150, 30, .9), shadow=False)
    d.band("crater", DIAMOND)
    d.shape("crater2", "M150 58 L156 62 L162 74 Q170 92 184 110 Q198 122 230 128 V132 H170 Q160 100 150 58Z", shadow=False, line=False)
    d.stroke("crater2", "M40 110 L36 126 M58 100 L54 126 M76 93 L74 126 M96 89 L96 126 M114 86 L116 126 M132 80 L136 126 "
                        "M144 66 L152 124", 1.8, line=False)
    d.band("sea", "M-30 126 H230")
    d.stroke("light", "M90 140 h18 M140 136 h16 M170 146 h18 M120 156 h14", 2)
    # a catamaran off Waikiki
    d.shape("light", "M136 132 L136 106 L152 130Z", spot=True)
    d.shape("dark", "M126 134 H158 L154 138 H130Z")
    d.band("sand", "M-30 160 Q30 146 90 164 Q130 176 230 172")
    d.band("surf", "M-30 162 Q30 148 90 166 Q130 178 230 174", shadow=False, line=False)
    palm(d, 26, 186, 34, 92, 1.15, role="leaf", trunk="bark", bend=-10)
    palm(d, 52, 190, 66, 120, .9, role="leaf", trunk="bark", bend=6)
    d.band("sand2", hills(190, 4, 30), line=False)


# ================================================================ NA PALI COAST
def ridge(peaks, base=None) -> str:
    return "M" + " L".join(f"{x} {y}" for x, y in peaks) + (f" V230 H{peaks[0][0]}Z" if base is None else "")


def na_pali(d: Drawing):
    d.shape("light", cloud(130, 30, 1.0), shadow=False)
    d.band("sea", "M-30 120 H230")
    far = [(56, 122), (72, 90), (80, 96), (92, 64), (100, 76), (112, 54), (124, 70), (138, 60), (156, 76), (176, 58), (196, 70), (230, 60)]
    mid = [(26, 136), (44, 100), (54, 108), (70, 70), (80, 84), (94, 56), (106, 76), (120, 66), (140, 90), (160, 72), (184, 90), (230, 80)]
    near = [(82, 166), (100, 120), (110, 128), (126, 82), (136, 100), (150, 62), (162, 90), (180, 78), (200, 96), (230, 88)]
    d.shape("ridge3", ridge(far))
    d.shape("ridge2", ridge(mid))
    d.stroke("ridge3", "M70 70 L58 124 M94 56 L84 130 M120 66 L118 130 M160 72 L160 130", 1.6, line=False)
    d.shape("ridge1", ridge(near))
    d.shape("ridge1b", "M150 62 L162 90 L180 78 L200 96 L230 88 V230 H150 Q160 150 150 62Z", shadow=False, line=False)
    d.stroke("ridge1b", "M100 120 L92 168 M126 82 L116 170 M150 62 L136 176 M136 100 L128 170", 1.8, line=False)
    d.stroke("ridge2", "M162 90 L160 184 M180 78 L178 186 M200 96 L196 186", 1.8, line=False)
    d.stroke("light", "M133 98 L131 140", 1.6, line=False)
    d.band("sea2", waves(164, 3, 26))
    d.shape("foam", "M20 140 Q40 136 56 142 M80 166 Q90 162 100 168", shadow=False, line=False)
    d.stroke("light", "M26 140 h16 M86 168 h14 M40 180 h18", 2)
    # a sailboat in the swell
    d.shape("light", "M44 150 L44 118 L62 148Z", spot=True)
    d.shape("dark", "M34 152 H66 L62 158 H38Z")
    d.band("sea", waves(188, 3, 32), line=False)


# ================================================================ FIJI
def crab_claw(d: Drawing):
    """Fijian camakau: outrigger canoe with a crab-claw sail."""
    d.stroke("bark", "M84 144 L112 70 M84 144 L148 100", 2)
    d.shape("sail", "M86 140 L112 72 Q116 100 146 102Z", spot=True)
    d.stroke("sail2", "M92 128 Q112 108 132 104 M100 110 Q114 96 124 92", 1.4, line=False)
    d.shape("bark", "M66 146 H138 Q136 152 128 152 H74 Q68 152 66 146Z")
    d.stroke("bark", "M84 148 L86 160 M120 148 L122 160", 1.6)
    d.shape("bark", rrect(78, 158, 52, 3.5, 1.7))


def fiji(d: Drawing):
    d.disc("glow", 156, 46, 12)
    d.shape("light", cloud(18, 40, 1.0), shadow=False)
    d.band("sea", "M-30 92 H230")
    d.shape("reef", ellipse(98, 116, 82, 20), shadow=False)
    d.shape("reef2", ellipse(98, 114, 62, 13), shadow=False, line=False)
    d.shape("sand", ellipse(98, 112, 44, 8))
    palm(d, 92, 112, 84, 70, .9, role="leaf", trunk="bark", bend=-6)
    palm(d, 106, 112, 118, 78, .8, role="leaf", trunk="bark", bend=6)
    palm(d, 80, 112, 66, 88, .62, role="leaf", trunk="bark", bend=-4)
    d.stroke("light", "M24 150 h18 M160 146 h18 M140 172 h20 M30 176 h14", 2)
    group(d, "translate(52 158) scale(.6) translate(-100 -140)", lambda: crab_claw(d))
    d.band("sea2", waves(184, 3, 32), line=False)


# ================================================================ MALDIVES
def maldives(d: Drawing):
    d.disc("glow", 160, 28, 10)
    d.band("sea", "M-30 44 H230")
    # the atoll island, seen from a seaplane
    d.shape("lagoon", ellipse(92, 104, 92, 44), shadow=False)
    d.shape("lagoon2", ellipse(84, 100, 62, 28), shadow=False, line=False)
    d.shape("sand", ellipse(78, 96, 46, 20))
    d.shape("leaf", ellipse(76, 93, 38, 15))
    d.marks("leaf2", " ".join(circle(x, y, r) for x, y, r in [(54, 92, 6), (68, 86, 6.5), (84, 88, 7), (98, 92, 6), (64, 100, 5), (88, 99, 5)]))
    # a straight jetty out to the water villas, villas on spurs either side
    x0, y0, x1, y1 = 100, 114, 130, 184
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    d.stroke("jetty", f"M{x0} {y0} L{x1} {y1}", 3, shadow=True)
    spots = []
    for i in range(6):
        t = 16 + i * 10.5
        side = 1 if i % 2 else -1
        jx, jy = x0 + ux * t, y0 + uy * t
        spots.append((jx - uy * 13 * side, jy + ux * 13 * side, jx, jy))
    for vx, vy, jx, jy in spots:
        d.stroke("jetty", f"M{jx:.1f} {jy:.1f} L{vx:.1f} {vy:.1f}", 2, line=False)
    for vx, vy, jx, jy in spots:
        def v(x=vx, y=vy):
            d.shape("deck", rrect(x - 8, y - 6.5, 16, 13, 2))
            d.shape("thatch", rrect(x - 6.5, y - 5.5, 13, 8.5, 2.5), spot=True)
            d.stroke("thatch2", f"M{x - 4} {y - 1.3} H{x + 4}", 1.2, line=False)
            d.shape("pool", rrect(x - 4.5, y + 3.4, 9, 2.4, 1), shadow=False, line=False)
        group(d, f"rotate({ang + 90:.1f} {vx:.1f} {vy:.1f})", v)
    d.stroke("light", "M20 160 q8 -4 16 0 M170 76 q8 -4 16 0 M176 176 q8 -4 16 0", 2)


# ================================================================ PORT ARTHUR
def port_arthur(d: Drawing):
    d.band("far", "M-30 106 Q40 94 100 100 T230 96")
    d.band("bay", "M-30 112 H230", line=False)
    for x, r in [(10, 20), (190, 22)]:
        d.limb("bark", f"M{x} 160 V120", 4)
        d.shape("tree", ellipse(x, 104, r * .7, r) + ellipse(x - r * .4, 120, r * .5, r * .6) + ellipse(x + r * .4, 118, r * .5, r * .6))
    # the roofless Penitentiary
    wall = ("M22 156 V84 H28 V72 L40 60 L52 72 V84 L62 84 L64 80 L74 80 L76 86 L88 86 L90 82 L100 82 L104 88 L114 88 L116 84 "
            "L126 84 L128 80 L138 80 L140 84 H148 V72 L160 60 L172 72 V84 H178 V156Z")
    d.shape("stone", wall, spot=False)
    d.shape("stone2", "M28 72 L40 60 L52 72 V84 H48 V74 L40 66 L32 74 V84 H28Z M148 72 L160 60 L172 72 V84 H168 V74 L160 66 L152 74 V84 H148Z",
            shadow=False, line=False)
    d.shape("stone2", rrect(22, 120, 156, 2.4, 0) + rrect(22, 102, 156, 2, 0), shadow=False, line=False)
    wins = []
    for row, y in enumerate((92, 106, 126)):
        for i in range(13):
            x = 30 + i * 11.4
            wins.append(f"M{x} {y + 9} V{y + 2} Q{x + 3} {y - 1} {x + 6} {y + 2} V{y + 9}Z")
    for i in range(13):
        x = 30 + i * 11.4
        wins.append(f"M{x} 154 V{144} Q{x + 3} 140 {x + 6} 144 V154Z")
    d.shape("sky", " ".join(wins), shadow=False)
    d.marks("dark", "M34 82 V76 Q40 70 46 76 V82Z M154 82 V76 Q160 70 166 76 V82Z")
    d.shape("stone2", "M22 156 H178 V160 H22Z", shadow=False, line=False)
    d.band("lawn", "M-30 156 Q100 152 230 156")
    d.stroke("path", "M60 230 Q90 180 100 160", 4, line=False)
    d.band("lawn2", hills(186, 4, 20), line=False)


# ================================================================ CRADLE MOUNTAIN
CRADLE = ("M-30 116 Q6 110 22 98 L32 82 L38 72 L42 80 L52 90 L62 86 L72 72 L80 62 L86 66 L92 52 L98 58 L104 46 L110 54 "
          "L116 44 L122 52 L128 46 L134 56 L142 60 L150 72 L162 86 Q184 102 230 110")


def cradle(d: Drawing):
    d.shape("light", cloud(150, 30, 1.0), shadow=False)
    d.band("rock", CRADLE)
    d.shape("rock2", "M116 44 L122 52 L128 46 L134 56 L142 60 L150 72 L162 86 Q184 102 230 110 V124 H130 Q126 90 116 44Z", shadow=False, line=False)
    d.stroke("rock2", "M80 64 V100 M86 68 V104 M92 56 V100 M98 60 V96 M104 50 V98 M110 56 V96 M38 76 V96 M44 82 V100", 1.4, line=False)
    d.band("scrub", "M-30 118 Q10 108 40 106 Q80 96 120 104 Q160 100 230 114")
    d.band("forest", "M-30 128 Q20 118 60 124 Q120 120 160 124 Q200 120 230 126")
    for x, y, r in [(20, 122, 6), (60, 121, 5), (150, 120, 6), (186, 120, 5)]:
        d.shape("forest", circle(x, y, r), shadow=False)
    d.band("lake", "M-30 132 H230")
    reflect(d, CRADLE + " V230 H-30Z", 132, "rock", .16)
    d.stroke("light", "M110 146 h22 M150 156 h18 M90 166 h16", 2)
    # the old boatshed
    d.stroke("timber", "M26 148 V160 M38 148 V160 M50 148 V160", 1.8)
    d.shape("timber", "M22 150 V128 L38 114 L54 128 V150Z", spot=True)
    d.shape("timber2", "M18 130 L38 110 L58 130 L54 132 L38 116 L22 132Z", shadow=False)
    d.marks("dark", "M31 150 V136 H45 V150Z")
    d.stroke("timber2", "M24 140 H30 M46 140 H52", 1.2, line=False)
    reflect(d, "M22 150 V128 L38 114 L54 128 V150Z", 150, "timber", .25)
    d.band("shore", "M-30 172 Q30 160 70 168 Q120 178 230 170")
    d.shape("shore2", ellipse(70, 168, 10, 5) + ellipse(140, 174, 8, 4) + ellipse(20, 168, 7, 4), shadow=False)
    d.band("scrub", hills(190, 4, 30), line=False)


# ================================================================ THE PINNACLES
def pillar(x, base, h, w, lean=0) -> str:
    """A knobbly limestone pinnacle: wider foot, lumpy rounded top."""
    t = base - h
    return (f"M{x - w * .62:.1f} {base} C{x - w * .5:.1f} {base - h * .4:.1f} {x - w * .58 + lean:.1f} {base - h * .7:.1f} {x - w * .46 + lean:.1f} {t + w * .3:.1f} "
            f"Q{x - w * .4 + lean:.1f} {t:.1f} {x - w * .05 + lean:.1f} {t + w * .06:.1f} Q{x + w * .2 + lean:.1f} {t - w * .1:.1f} {x + w * .45 + lean:.1f} {t + w * .35:.1f} "
            f"C{x + w * .56 + lean:.1f} {base - h * .65:.1f} {x + w * .48:.1f} {base - h * .35:.1f} {x + w * .64:.1f} {base}Z")


def pillar_shade(x, base, h, w, lean=0) -> str:
    t = base - h
    return (f"M{x + w * .12 + lean:.1f} {t + w * .06:.1f} Q{x + w * .2 + lean:.1f} {t - w * .1:.1f} {x + w * .45 + lean:.1f} {t + w * .35:.1f} "
            f"C{x + w * .56 + lean:.1f} {base - h * .65:.1f} {x + w * .48:.1f} {base - h * .35:.1f} {x + w * .64:.1f} {base} "
            f"H{x + w * .2:.1f} C{x + w * .22:.1f} {base - h * .4:.1f} {x + w * .3 + lean:.1f} {t + h * .3:.1f} {x + w * .12 + lean:.1f} {t + w * .06:.1f}Z")


def pinnacles(d: Drawing):
    d.disc("glow", 150, 48, 13)
    d.band("far", "M-30 112 Q60 104 120 108 T230 104")
    d.band("sand", "M-30 116 Q100 112 230 116")
    rows = [
        [(14, 120, 10, 5), (34, 122, 14, 6), (62, 119, 8, 4), (90, 121, 12, 5), (120, 120, 9, 4), (150, 122, 14, 6), (178, 121, 10, 5)],
        [(2, 138, 28, 10), (58, 138, 34, 12), (112, 136, 24, 9), (142, 140, 30, 11), (198, 138, 26, 10)],
        [(32, 180, 82, 26, 2), (92, 164, 50, 18, -1), (164, 178, 88, 28, -2), (126, 190, 40, 16, 1)],
    ]
    for row in rows:
        for p in row:
            x, b, h, w = p[:4]
            lean = p[4] if len(p) > 4 else 0
            d.shape("sand2", ellipse(x + w * .9, b, w * .9, w * .14), shadow=False, line=False)
            d.shape("lime", pillar(x, b, h, w, lean), spot=h > 80)
            d.shape("lime2", pillar_shade(x, b, h, w, lean), shadow=False, line=False)
            if h > 30:
                d.stroke("lime2", f"M{x - w * .3:.1f} {b - h * .3:.1f} q{w * .2:.1f} {-2} {w * .4:.1f} 0 M{x - w * .2:.1f} {b - h * .6:.1f} q{w * .2:.1f} -2 {w * .3:.1f} 0", 1.2, line=False)
    d.band("sand2", hills(190, 4, 20), line=False)


# ================================================================ concepts
NO_GOLD = ["coastal", "meadow", "blush", "dusk"]
REEF = {"sea": "#1E6FA6", "sea2": "#2A86BC", "reef": "#55CFC6", "reef2": "#9BE6DD", "halo": "#5FD8CB",
        "coral": "#9A8550", "coral2": "#6E5C30", "light": "#FFFFFF"}
WHITEHAVEN = {"chan": "#1F98AE", "sea2": "#1F74A8", "lagoon": "#2FB4C2", "lagoon2": "#7FDDD8", "sand": "#FFFEF8", "forest": "#2E6B45", "forest2": "#24563A"}
BONDI = {"sea": "#2385B8", "sand": "#F1D9A4", "rock": "#C8925E", "deck": "#EDE6D8", "pool": "#45C4E6", "foam": "#D9F2FA",
         "trim": "#2C6E9E", "glass": "#2F4858", "light": "#FFFFFF"}
FLINDERS = {"wall": "#E3A04E", "trim": "#F7E6C4", "copper": "#4E9E86", "copper2": "#3A7C68", "glass": "#47606E",
            "clock": "#FFFBEF", "tram": "#3F8A55", "road": "#6E6A66"}
KATA = {"rock": "#C9562C", "rock2": "#A2401F", "rock3": "#B66A4B", "earth": "#E08A4E", "bush": "#A3A14C"}
BYRON = {"sea": "#2486B5", "whale": "#2F3E4C", "cliff": "#A9805A", "cliff2": "#86603F", "grass": "#5E9C4E", "grass2": "#4C8A42",
         "roof": "#5A6470", "glass": "#3C4A56", "shade": "#E3E6EA", "light": "#FFFFFF"}
TONGA = {"ash": "#5D5552", "ash2": "#7A706A", "red": "#A84A2E", "red2": "#7D3420", "scree": "#8C7462", "scree2": "#6F5A4B",
         "rim": "#E6DDA6", "lake": "#2EC4A4", "lake2": "#3FB2C8", "lake3": "#21A98E", "lakehi": "#9BEFD8"}
AORAKI_C = {"snow": "#FFFFFF", "snow2": "#C9D8E6", "rock": "#6F7A84", "lake": "#5CC8D2", "tussock": "#D2A85A", "tussock2": "#B8893F",
            "light": "#FFFFFF"}
TEKAPO = {"lake": "#46C0CE", "shore": "#D8C9A4", "stone": "#CDB896", "stone2": "#9C8566", "roof": "#535866", "roof2": "#3B3F4A",
          "glass": "#3A4652", "meadow": "#6E9E4C", "leaf": "#4F8A3E", "lup1": "#8A58C4", "lup2": "#E36FA8", "lup3": "#5E6CD8"}
MOERAKI = {"sea": "#3B8FB4", "surf": "#DDF0F4", "wet": "#C9AE84", "boulder": "#8E8579", "boulder2": "#706759", "crack": "#D9CDB6",
           "foam": "#F2F7F7", "light": "#FFFFFF"}
POHUTU = {"bush": "#3E6E4A", "steam": "#FFFFFF", "steam2": "#DCE4EA", "sinter": "#E8DCC0", "sinter2": "#D99A5E", "sinter3": "#C9B48E",
          "carve": "#8E3A24", "carve2": "#64271A", "paua": "#4FB5AE"}
WANAKA = {"lake": "#5E9FC0", "bark": "#5A4632", "leaf": "#D9A23C", "leaf2": "#F0C460", "lakehi": "#BFE0EC", "light": "#FFFFFF"}
WAITOMO = {"glowd": "#A6FFF0", "water": "#0B1A22", "boat": "#05090C"}
DIAMOND_C = {"crater": "#8C9A58", "crater2": "#6C7A44", "sea": "#2E9FC6", "sand": "#F1D9A0", "sand2": "#E2C384", "surf": "#FFFFFF",
             "leaf": "#3E7F48", "bark": "#7A5A3A", "light": "#FFFFFF"}
NAPALI = {"ridge1": "#2F7A48", "ridge1b": "#25623A", "ridge2": "#4F9A5C", "ridge3": "#8CC28A", "sea": "#1F7FB0", "sea2": "#2A90C0",
          "foam": "#FFFFFF", "light": "#FFFFFF"}
FIJI = {"sea": "#1E78B0", "sea2": "#2386BE", "reef": "#4FD0C6", "reef2": "#8FE6DA", "sand": "#F6E6BA", "leaf": "#3E8A4A",
        "bark": "#6E4A2C", "sail": "#E9D7A8", "sail2": "#B89A60", "light": "#FFFFFF"}
MALDIVES = {"sea": "#1C6FAE", "lagoon": "#3FC9D0", "lagoon2": "#8AE6E0", "sand": "#FBF3DA", "leaf": "#3F8A48", "leaf2": "#2F6E3A",
            "jetty": "#9C7448", "deck": "#C79A63", "thatch": "#A97842", "thatch2": "#7C5528", "pool": "#5FD6F0", "light": "#FFFFFF"}
PORT = {"stone": "#D9A574", "stone2": "#B07E50", "tree": "#3F6E46", "bark": "#5A4632", "lawn": "#7DAA56", "lawn2": "#6A9848",
        "path": "#E8D7B2", "bay": "#5FA8C4"}
CRADLE_C = {"rock": "#77706A", "rock2": "#5A544F", "scrub": "#A69A4E", "forest": "#2F5B3E", "lake": "#2E5E7E", "timber": "#7A4A2A",
            "timber2": "#55311A", "shore": "#B79A72", "shore2": "#8E775A", "light": "#FFFFFF"}
PINN = {"sand": "#EBA94A", "sand2": "#C98A32", "lime": "#F4E7C6", "lime2": "#CDB284"}

CONCEPTS = [
    Concept("lm2-heartreef", "landmark-heart-reef", "Great Barrier Reef", clipped(heart_reef), palettes=NO_GOLD, overrides=REEF,
            checks=[("sea2", "sky"), ("glow", "sky")], fixes={"glow": ["glow2", "#FFC857"], "sky": ["sky2", "light"]}),
    Concept("lm2-whitehaven", "landmark-whitehaven", "Whitehaven Beach", clipped(whitehaven), palettes=NO_GOLD, overrides=WHITEHAVEN,
            checks=[("sea2", "sky"), ("forest", "sky")], fixes={"sky": ["sky2", "light"]}),
    Concept("lm2-bondi", "landmark-bondi", "Bondi Beach", clipped(bondi), palettes=NO_GOLD, overrides=BONDI,
            checks=[("far", "sky"), ("sea", "far")], fixes={"sky": ["sky2", "far", "glow2"], "far": ["mid", "near"]}),
    Concept("lm2-flinders", "landmark-flinders-street", "Flinders Street Station", clipped(flinders), overrides=FLINDERS,
            checks=[("wall", "sky"), ("copper", "sky")], fixes={"sky": ["sky2", "far", "light"]}),
    Concept("lm2-katatjuta", "landmark-kata-tjuta", "Kata Tjuta", clipped(kata_tjuta), overrides=KATA,
            checks=[("rock", "sky"), ("rock3", "sky"), ("rock", "glow"), ("dark", "earth"), ("rock", "earth")],
            fixes={"glow": ["glow2", "light"], "sky": ["sky2", "far"]}),
    Concept("lm2-byron", "landmark-byron-lighthouse", "Byron Bay lighthouse", clipped(byron), palettes=NO_GOLD, overrides=BYRON,
            checks=[("light", "sky"), ("roof", "sky"), ("sea", "sky")], fixes={"sky": ["sky2", "far", "mid"]}),
    Concept("lm2-tongariro", "landmark-tongariro", "Tongariro Emerald Lakes", clipped(tongariro), overrides=TONGA,
            checks=[("ash2", "sky"), ("red", "sky")], fixes={"sky": ["sky2", "far"]}),
    Concept("lm2-aoraki", "landmark-aoraki", "Aoraki / Mount Cook", clipped(aoraki), palettes=NO_GOLD, overrides=AORAKI_C,
            checks=[("snow", "sky"), ("far", "sky"), ("snow", "far")], fixes={"sky": ["sky2", "far", "mid", "near"], "far": ["mid", "near", "deep"]}),
    Concept("lm2-tekapo", "landmark-tekapo", "Church of the Good Shepherd", clipped(tekapo), palettes=NO_GOLD, overrides=TEKAPO,
            checks=[("far", "sky"), ("roof", "lake"), ("stone", "lake"), ("light", "far")], fixes={"far": ["mid", "near", "deep"]}),
    Concept("lm2-moeraki", "landmark-moeraki", "Moeraki Boulders", clipped(moeraki), palettes=NO_GOLD, overrides=MOERAKI,
            checks=[("boulder", "sky"), ("sea", "sky"), ("glow", "sea")], fixes={"sky": ["sky2", "light"]}),
    Concept("lm2-pohutu", "landmark-pohutu", "Pohutu geyser", clipped(pohutu), overrides=POHUTU,
            checks=[("steam", "sky")], fixes={"sky": ["sky2", "far", "mid"]}),
    Concept("lm2-wanaka", "landmark-wanaka-tree", "That Wanaka Tree", clipped(wanaka), palettes=NO_GOLD, overrides=WANAKA,
            checks=[("far", "sky"), ("leaf", "lake"), ("leaf", "far"), ("mid", "far")], fixes={"far": ["mid", "near"], "mid": ["near", "deep"]}),
    Concept("lm2-waitomo", "landmark-waitomo", "Waitomo glowworm caves", clipped(waitomo), palettes=["coastal", "dusk", "blush", "golden"],
            overrides=WAITOMO, checks=[("glowd", "deep"), ("deep", "dark")], fixes={"deep": ["near", "mid"]}),
    Concept("lm2-diamondhead", "landmark-diamond-head", "Diamond Head", clipped(diamond_head), palettes=NO_GOLD, overrides=DIAMOND_C,
            checks=[("crater", "sky"), ("glow", "sky")], fixes={"glow": ["glow2", "#FFC857"], "sky": ["sky2", "light"]}),
    Concept("lm2-napali", "landmark-na-pali", "Nā Pali Coast", clipped(na_pali), palettes=NO_GOLD, overrides=NAPALI,
            checks=[("ridge3", "sky"), ("sea", "sky")], fixes={"sky": ["sky2", "light", "glow2"]}),
    Concept("lm2-fiji", "landmark-fiji", "Fiji islands", clipped(fiji), palettes=NO_GOLD, overrides=FIJI,
            checks=[("sea", "sky"), ("leaf", "sky")], fixes={"sky": ["sky2", "light"]}),
    Concept("lm2-maldives", "landmark-maldives", "Maldives", clipped(maldives), palettes=NO_GOLD, overrides=MALDIVES,
            checks=[("sea", "sky")], fixes={"sky": ["sky2", "light"]}),
    Concept("lm2-portarthur", "landmark-port-arthur", "Port Arthur", clipped(port_arthur), overrides=PORT,
            checks=[("stone", "sky"), ("far", "sky"), ("tree", "sky"), ("stone", "far")], fixes={"far": ["mid", "near", "deep"]}),
    Concept("lm2-cradle", "landmark-cradle-mountain", "Cradle Mountain", clipped(cradle), palettes=NO_GOLD, overrides=CRADLE_C,
            checks=[("rock", "sky")], fixes={"sky": ["sky2", "light"]}),
    Concept("lm2-pinnacles", "landmark-pinnacles", "The Pinnacles", clipped(pinnacles), overrides=PINN,
            checks=[("lime", "sky"), ("lime", "sand"), ("sand", "far"), ("far", "sky")],
            fixes={"sky": ["sky2", "far", "mid"], "far": ["mid", "near", "deep"]}),
]
