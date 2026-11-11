"""Food & drink, second batch: three concepts each for sixteen tasting, market and eating-out activities."""
import math

from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group


# ================================================================ helpers
def steam(d: Drawing, xs, y, h=22, role="light", w=3.2):
    """Wavy steam rising from y (bottom) for each x."""
    for i, x in enumerate(xs):
        k = 1 if i % 2 == 0 else -1
        q = h / 4
        d.stroke(role, f"M{x} {y} q{4*k} {-q} 0 {-2*q} t0 {-2*q}", w)


def table(d: Drawing, y, top="ground", front="near", lip=10):
    """Flat table top with a darker front edge, edge to edge."""
    d.band(top, f"M-30 {y} L230 {y}")
    d.band(front, f"M-30 {y+lip} L230 {y+lip}", line=False)


def chopsticks(d: Drawing, x1, y1, x2, y2, gap=7, role="dark", w=3.6):
    d.stroke(role, f"M{x1} {y1} L{x2} {y2}", w, shadow=True)
    d.stroke(role, f"M{x1+gap} {y1+gap*0.5} L{x2+gap*0.25} {y2+gap*0.9}", w, shadow=True)


def leaf(x, y, L, W, ang):
    """A pointed leaf from (x, y), length L, width W, pointing at angle ang (degrees)."""
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    tx, ty = x + L * ca, y + L * sa
    mx, my = x + L / 2 * ca, y + L / 2 * sa
    px, py = -sa * W, ca * W
    return (f"M{x:.1f} {y:.1f} Q{mx+px:.1f} {my+py:.1f} {tx:.1f} {ty:.1f} "
            f"Q{mx-px:.1f} {my-py:.1f} {x:.1f} {y:.1f}Z")


def leaf_vein(x, y, L, ang, k=0.8):
    a = math.radians(ang)
    return f"M{x:.1f} {y:.1f} L{x + L*k*math.cos(a):.1f} {y + L*k*math.sin(a):.1f}"


VINE_LEAF = ("M0 18 C-6 12 -22 14 -24 2 C-28 -6 -16 -10 -18 -16 C-12 -24 -4 -18 0 -26 "
             "C4 -18 12 -24 18 -16 C16 -10 28 -6 24 2 C22 14 6 12 0 18Z")


def vine_leaf(d: Drawing, x, y, s=1.0, rot=0, role="near", vein="mark", spot=False):
    def f():
        d.shape(role, VINE_LEAF, spot=spot)
        d.stroke(vein, "M0 18 V-18 M0 6 L-16 -8 M0 6 L16 -8", 1.4, line=False)
    group(d, f"translate({x} {y}) rotate({rot}) scale({s})", f)


def grape_pile(d: Drawing, pts, role, r=8.5, spot=False):
    for x, y in pts:
        d.shape(role, circle(x, y, r), spot=spot)
        d.shape("light", circle(x - r * 0.35, y - r * 0.35, r * 0.22), shadow=False, line=False)


def line_only(d: Drawing, path, w=3):
    if d.paper:
        return
    d.raw("", f'<path d="{path}" fill="none" stroke="{d.c["ink"]}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')


def bumpy(x0, y0, cx, cy, x1, y1, n=14, r=None):
    """A quadratic edge from (x0,y0) to (x1,y1) made of little upward bumps (bush tops)."""
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append(((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1, (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1))
    rr = r or (x1 - x0) / n * 0.62
    s = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for x, y in pts[1:]:
        s += f" A{rr:.1f} {rr:.1f} 0 0 1 {x:.1f} {y:.1f}"
    return s


# ================================================================ VINEYARD TOUR
def vtour_hills(d: Drawing):
    d.disc("glow", 140, 56, 20)
    # farmhouse and cypresses sit on the far ridge (bases hidden by it)
    d.shape("light", "M112 104 V82 H136 V104Z")
    d.shape("pop", "M109 84 L124 74 L139 84Z", shadow=False, spot=True)
    d.marks("dark", rrect(118, 88, 4, 5, 1) + rrect(127, 88, 4, 5, 1))
    for x, y, rx, ry in [(40, 80, 4.5, 16), (51, 84, 4, 13), (160, 84, 4, 13)]:
        d.shape("dark", ellipse(x, y, rx, ry))
    d.band("far", hills(100, 12, 10))
    d.band("mid", "M-30 122 Q70 104 230 118")
    # vine rows fanning out from the horizon
    for x in range(-110, 330, 34):
        t = 14 / 110
        x0 = 100 + (x - 100) * t
        dx = (x - 100) / 110
        top, bot = 2.2, 10
        p = f"M{x0-top:.1f} 114 L{x0+top:.1f} 114 L{x+bot:.1f} 224 L{x-bot:.1f} 224Z"
        d.shape("deep", p, shadow=False, line=False)
        line_only(d, f"M{x0:.1f} 118 L{x:.1f} 224", 2.4)
    d.band("near", "M-30 186 Q100 176 230 186", line=False)


def vtour_crate(d: Drawing):
    d.disc("glow", 100, 88, 60, line=False)
    table(d, 152, "far", "deep")
    vine_leaf(d, 52, 88, 1.3, -30)
    vine_leaf(d, 150, 84, 1.2, 35)
    grape_pile(d, [(84, 86), (100, 82), (92, 98), (76, 100), (108, 96), (100, 110), (68, 110), (86, 112)], "hero2")
    grape_pile(d, [(126, 92), (140, 98), (118, 104), (132, 108), (148, 110), (124, 116)], "pop")
    d.stroke("dark", "M98 76 Q100 66 106 62", 3)
    # wooden harvest crate
    d.shape("hero", "M38 112 H162 L156 160 H44Z", spot=True)
    d.stroke("mark", "M40 128 H160 M42 144 H158", 2.4)
    d.marks("mark", rrect(86, 117, 28, 7, 3.5))
    d.stroke("mark", "M58 112 V160 M142 112 V160", 1.6, line=False)


def barrel_end(d: Drawing, x, y, r, spot=False):
    d.shape("hero", circle(x, y, r), spot=spot)
    d.stroke("dark", circle(x, y, r * 0.84), 3)
    d.shape("hero2", circle(x, y, r * 0.74), shadow=False, line=False)
    d.stroke("mark", f"M{x - r*0.7:.1f} {y - r*0.2:.1f} H{x + r*0.7:.1f} M{x - r*0.7:.1f} {y + r*0.2:.1f} H{x + r*0.7:.1f}", 1.2, line=False)
    d.marks("dark", circle(x, y - r * 0.5, r * 0.09))


def vtour_cellar(d: Drawing):
    d.band("deep", "M-30 -30 L230 -30", line=False)
    d.shape("far", "M26 210 V98 C26 30 174 30 174 98 V210Z")
    d.stroke("dark", "M100 34 V48", 1.6)
    d.disc("glow2", 100, 54, 7)
    d.band("mid", "M-30 168 L230 168")
    for x, y in [(55, 146), (100, 146), (145, 146), (77.5, 107), (122.5, 107), (100, 68)]:
        barrel_end(d, x, y, 22, spot=(x, y) == (100, 68))
    d.shape("dark", rrect(24, 166, 152, 8, 3))


# ================================================================ BREWERY TOUR
def steel_tank(d: Drawing, cx, top, w, cyl, floor):
    h = w / 2
    d.stroke("dark", f"M{cx-h+4} {cyl} L{cx-h+2} {floor} M{cx+h-4} {cyl} L{cx+h-2} {floor}", 3)
    d.shape("hero2", f"M{cx-h} {top+w*0.32} C{cx-h} {top-2} {cx+h} {top-2} {cx+h} {top+w*0.32} V{cyl} L{cx+5} {cyl+18} H{cx-5} L{cx-h} {cyl}Z")
    d.stroke("mark", f"M{cx-h} {top+w*0.6} H{cx+h} M{cx-h} {cyl-10} H{cx+h}", 2, line=False)
    d.stroke("light", f"M{cx-h+6} {top+w*0.4} V{cyl-6}", 3, line=False)


def brew_tanks(d: Drawing):
    d.disc("glow", 100, 72, 54, line=False)
    d.band("ground", "M-30 160 L230 160")
    d.band("near", "M-30 174 L230 174", line=False)
    steel_tank(d, 44, 54, 38, 120, 160)
    steel_tank(d, 156, 54, 38, 120, 160)
    d.limb("dark", "M62 128 H140", 4)
    # copper kettle
    d.limb("hero", "M100 84 V36", 10)
    d.shape("hero", rrect(92, 30, 16, 7, 3))
    d.shape("hero", "M62 160 V114 C62 94 80 82 100 82 C120 82 138 94 138 114 V160Z", spot=True)
    d.stroke("pop", "M72 150 V114 C72 102 80 94 90 90", 4, line=False)
    d.shape("dark", circle(100, 118, 11), shadow=False)
    d.shape("glow2", circle(100, 118, 7.5), shadow=False, line=False)
    d.shape("dark", rrect(58, 156, 84, 6, 2), shadow=False)


def taster(d: Drawing, x, base, beer, foam=True, spot=False):
    d.shape("light", f"M{x-13} {base-58} H{x+13} L{x+9} {base} H{x-9}Z")
    d.shape(beer, f"M{x-11.6} {base-48} H{x+11.6} L{x+8.2} {base-2} H{x-8.2}Z", shadow=False, spot=spot)
    if foam:
        d.shape("light", f"M{x-13} {base-50} C{x-14} {base-58} {x-7} {base-62} {x} {base-59} C{x+6} {base-63} {x+14} {base-58} {x+13} {base-50}Z", shadow=False)


def brew_flight(d: Drawing):
    d.disc("glow", 100, 84, 58, line=False)
    table(d, 144, "far", "mid")
    d.shape("ground", rrect(150, 132, 30, 9, 4.5))
    d.shape("ground", rrect(20, 128, 134, 18, 6))
    for x, beer, sp in [(39, "hero", False), (69, "pop", True), (99, "mark", False), (129, "dark", False)]:
        taster(d, x, 134, beer, spot=sp)
    d.stroke("near", "M26 140 H148", 1.4, line=False)


def hop_cone(d: Drawing, cx=100):
    rows = [(132, 1, 0), (118, 2, 11), (104, 3, 19), (90, 3, 20), (76, 2, 14)]
    for y, n, half in rows:
        xs = [cx] if n == 1 else [cx - half + i * (2 * half / (n - 1)) for i in range(n)]
        w = 30 if n < 3 else 24
        for x in xs:
            h = 26
            d.shape("hero", f"M{x-w/2:.1f} {y} Q{x-w/2:.1f} {y+h*0.7:.1f} {x:.1f} {y+h} Q{x+w/2:.1f} {y+h*0.7:.1f} {x+w/2:.1f} {y} "
                            f"Q{x:.1f} {y-h*0.3:.1f} {x-w/2:.1f} {y}Z", spot=True)
            d.stroke("mark", f"M{x:.1f} {y+3} V{y+h-6}", 1.3, line=False)


def brew_hops(d: Drawing):
    d.disc("glow", 100, 100, 62, line=False)
    # barley ear behind
    d.stroke("hero2", "M150 172 Q140 120 154 52", 3, shadow=True)
    for i in range(6):
        y = 60 + i * 13
        for k in (-1, 1):
            d.shape("hero2", leaf(152 - i * 0.6, y + 6, 14, 6, -90 + k * 32), shadow=False)
    vine_leaf(d, 62, 70, 1.5, -40, role="near")
    d.stroke("near", "M100 62 Q96 44 80 40", 3.2, shadow=True)
    hop_cone(d)


# ================================================================ WHISKY DISTILLERY
def still(d: Drawing):
    d.limb("hero", "M0 -110 Q2 -124 16 -120 L46 -100", 7)
    d.shape("hero", "M-8 -74 L-6 -112 H6 L8 -74Z")
    d.shape("hero", ellipse(0, -84, 13, 8), shadow=False)
    d.shape("hero", "M-34 0 C-46 -26 -36 -52 -14 -60 L-10 -74 C-10 -80 10 -80 10 -74 L14 -60 C36 -52 46 -26 34 0Z", spot=True)
    d.stroke("hero2", "M-28 -10 C-36 -28 -28 -44 -14 -52", 4, line=False)
    d.stroke("mark", "M-38 -28 Q0 -22 38 -28", 1.6, line=False)
    d.shape("dark", rrect(-40, -4, 80, 10, 2))


def whisky_stills(d: Drawing):
    d.disc("glow", 100, 80, 52, line=False)
    d.band("ground", "M-30 166 L230 166")
    d.band("near", "M-30 178 L230 178", line=False)
    group(d, "translate(74 166) scale(-1 1)", lambda: still(d))
    group(d, "translate(142 166) scale(.76)", lambda: still(d))


def whisky_glass(d: Drawing):
    d.band("far", "M-30 -30 L230 -30", line=False)
    # cask lying on its side
    d.shape("hero", circle(70, 90, 46))
    d.stroke("dark", circle(70, 90, 40), 4)
    d.shape("hero2", circle(70, 90, 35), shadow=False, line=False)
    d.stroke("mark", "M38 76 H102 M36 90 H104 M38 104 H102", 1.4, line=False)
    d.marks("dark", circle(70, 62, 3.5))
    table(d, 150, "mid", "deep")
    # glencairn glass
    d.shape("light", ellipse(124, 150, 23, 5))
    d.shape("light", rrect(117, 136, 14, 13, 2), shadow=False)
    d.shape("light", "M110 64 C106 80 98 94 98 112 C98 130 110 139 124 139 C138 139 150 130 150 112 C150 94 142 80 138 64Z")
    d.shape("pop", "M99 113 Q124 107 149 113 C149 128 138 137 124 137 C110 137 99 128 99 113Z", shadow=False, spot=True)
    d.stroke("glow2", "M105 117 Q110 126 116 130", 2, line=False)
    d.stroke("sky2", "M106 82 C102 92 102 100 103 106", 2.4, line=False)


def whisky_pagoda(d: Drawing):
    d.disc("glow", 150, 52, 16)
    d.band("far", "M-30 108 Q20 66 60 94 Q100 58 150 90 Q180 74 230 98")
    d.band("mid", hills(130, 10))
    # long stillhouse
    d.shape("light", rrect(30, 112, 92, 36, 1))
    d.shape("dark", "M26 114 L40 98 H110 L124 114Z")
    for x in [40, 58, 76, 94]:
        d.marks("dark", rrect(x, 122, 8, 10, 1))
    # malt kiln with pagoda roof
    d.shape("light", rrect(118, 96, 38, 52, 1))
    d.shape("dark", "M110 100 Q124 94 128 74 H146 Q150 94 164 100Z", spot=True)
    d.shape("dark", rrect(131, 62, 12, 13, 1))
    d.shape("dark", "M126 64 L137 54 L148 64Z")
    d.marks("dark", rrect(133, 112, 8, 12, 1) + rrect(133, 132, 8, 16, 1))
    d.band("near", "M-30 152 Q100 142 230 154")
    d.stroke("light", "M20 172 Q70 160 120 170 T200 166", 3, line=False)
    for x, y in [(38, 160), (52, 164), (150, 160), (164, 166), (176, 158)]:
        d.marks("pop", circle(x, y, 2.6) + circle(x + 4, y - 3, 2.2))


# ================================================================ SAKE TASTING
TOKKURI = ("M-9 -86 H9 L7 -80 C5 -74 5 -70 6 -64 C24 -56 30 -36 26 -16 C24 -6 18 0 12 0 H-12 "
           "C-18 0 -24 -6 -26 -16 C-30 -36 -24 -56 -6 -64 C-5 -70 -5 -74 -7 -80Z")


def ochoko(d: Drawing, x, y, s=1.0):
    def f():
        d.shape("hero", "M-13 -18 H13 C13 -6 8 0 0 0 C-8 0 -13 -6 -13 -18Z")
        d.shape("hero2", ellipse(0, -18, 13, 3.6), shadow=False)
        d.stroke("mark", "M-12 -11 Q0 -8 12 -11", 2.2, line=False)
    group(d, f"translate({x} {y}) scale({s})", f)


def sake_set(d: Drawing):
    d.disc("glow", 100, 86, 58, line=False)
    table(d, 146, "far", "mid")
    d.shape("dark", "M24 136 H176 L170 150 H30Z")
    def flask():
        d.shape("hero", TOKKURI, spot=True)
        d.shape("hero", rrect(-11, -90, 22, 5, 2), shadow=False)
        d.stroke("mark", "M-25 -30 Q-18 -38 -10 -30 T6 -30 T22 -30", 2.4)
        d.stroke("mark", "M-27 -22 H27", 1.6, line=False)
    group(d, "translate(78 138)", flask)
    ochoko(d, 126, 138, 1.15)
    ochoko(d, 158, 138, 1.15)
    for x, y, r in [(150, 62, 0), (40, 70, 40), (170, 92, 80)]:
        d.shape("pop", "M0 -6 C4 -6 6 -2 4 2 L0 6 L-4 2 C-6 -2 -4 -6 0 -6Z", shadow=False,
                extra=f'transform="translate({x} {y}) rotate({r})"')


def sake_masu(d: Drawing):
    d.disc("glow", 100, 78, 56, line=False)
    table(d, 152, "far", "mid")
    # masu box: back rim and the sake pooled in it
    d.shape("hero", "M46 116 L66 100 H160 L140 116Z")
    d.shape("hero2", "M54 113 L69 103 H151 L137 113Z", shadow=False)
    # glass standing in it, overflowing
    d.shape("light", "M82 54 H126 L121 110 H87Z")
    d.shape("hero2", "M83 60 H125 L120.6 108 H87.4Z", shadow=False)
    d.shape("hero2", "M80 56 Q104 50 128 56 Q130 64 126 66 Q104 60 82 66 Q78 64 80 56Z", shadow=False, spot=True)
    d.stroke("hero2", "M82 62 Q80 80 84 96 M126 62 Q129 78 124 92", 2.6, line=False)
    d.stroke("light", "M92 66 V100", 2.4, line=False)
    # front faces
    d.shape("hero", "M46 116 H140 V156 H46Z", spot=False)
    d.shape("mark", "M140 116 L160 100 V140 L140 156Z")
    d.stroke("mark", "M52 124 H134", 1.2, line=False)
    for x, y in [(64, 46), (140, 44), (148, 70)]:
        d.marks("hero2", circle(x, y, 3))


def komodaru(d: Drawing, x, yb, crest, w=44, h=40):
    d.shape("light", rrect(x - w / 2, yb - h, w, h, 4))
    d.shape("ground", ellipse(x, yb - h, w / 2, 5), shadow=False)
    d.shape("pop", rrect(x - w / 2, yb - h + 3, w, 6, 1), shadow=False)
    d.shape("pop", rrect(x - w / 2, yb - 9, w, 6, 1), shadow=False)
    d.shape(crest, circle(x, yb - h / 2 + 1, 8), shadow=False, spot=crest == "mark")
    d.stroke("dark", f"M{x - w/2 + 4} {yb - h + 9} L{x - w/2 + 10} {yb - 3} M{x + w/2 - 4} {yb - h + 9} L{x + w/2 - 10} {yb - 3}", 1.4, line=False)


def sake_barrels(d: Drawing):
    d.disc("glow", 100, 90, 60, line=False)
    d.band("far", "M-30 152 L230 152")
    def stack():
        for x, yb, cr in [(54, 160, "hero"), (100, 160, "mark"), (146, 160, "hero"), (77, 120, "mark"), (123, 120, "hero"), (100, 80, "mark")]:
            komodaru(d, x, yb, cr)
    group(d, "translate(100 112) scale(.86) translate(-100 -110)", stack)
    d.band("near", "M-30 174 L230 174", line=False)


# ================================================================ COFFEE PLANTATION
def cherries(d: Drawing, pts, r=7.5):
    for x, y, role in pts:
        d.shape(role, circle(x, y, r), spot=role == "pop")
        d.shape("light", circle(x - 2.5, y - 2.5, 1.8), shadow=False, line=False)
        d.marks("mark", circle(x + 2, y + 3, 1.2))


def coffee_branch(d: Drawing):
    d.disc("glow", 100, 100, 62, line=False)
    d.limb("dark", "M26 156 Q74 128 116 106 T178 62", 6)
    for x, y, L, ang in [(56, 140, 40, 205), (60, 138, 44, 115), (100, 114, 46, 250), (104, 112, 42, 60),
                         (144, 86, 40, 225), (148, 84, 42, 40), (170, 68, 30, 300)]:
        d.shape("near", leaf(x, y, L, 16, ang), spot=False)
        d.stroke("mid", leaf_vein(x, y, L, ang), 1.5, line=False)
    cherries(d, [(76, 126, "pop"), (86, 132, "pop"), (80, 140, "hero2"), (70, 136, "pop"),
                 (120, 100, "hero"), (130, 104, "pop"), (124, 112, "pop"), (114, 110, "hero2"),
                 (158, 78, "pop"), (166, 82, "hero")])


def coffee_hills(d: Drawing):
    d.disc("glow", 152, 56, 17)
    d.band("far", "M-30 112 L40 112 L82 64 Q100 54 118 64 L160 112 L230 112")
    d.shape("light", "M82 64 Q100 54 118 64 L110 74 L104 68 L98 76 L92 69 L88 73Z", shadow=False)
    d.band("mid", "M-30 126 Q60 106 230 124")
    for row, (y0, cy, y1, n) in enumerate([(132, 114, 130, 11), (150, 132, 150, 10), (172, 154, 172, 9)]):
        for i in range(n):
            t = (i + 0.5) / n
            x = -10 + t * 220
            y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1
            r = 8 + row * 2.5
            d.shape("near", circle(x, y, r), shadow=row > 0)
            if (i + row) % 2 == 0:
                d.marks("pop", circle(x - 2, y + 1, 1.8 + row * 0.4) + circle(x + 3, y + 3, 1.8 + row * 0.4))
    # shade tree
    d.limb("dark", "M40 134 V92", 4)
    d.shape("deep", "M14 96 Q40 70 66 96 Q40 102 14 96Z", spot=True)


def bean(x, y, rot, s=1.0):
    return f'<ellipse cx="0" cy="0" rx="{5.4*s}" ry="{3.8*s}" transform="translate({x} {y}) rotate({rot})"/>'


def coffee_sack(d: Drawing):
    d.disc("glow", 100, 86, 58, line=False)
    table(d, 158, "far", "mid")
    d.shape("hero2", "M48 160 C38 130 46 102 58 90 H142 C154 102 162 130 152 160Z", spot=True)
    d.stroke("mark", "M60 106 V154 M76 100 V158 M92 100 V158 M108 100 V158 M124 100 V158 M140 106 V154", 1.2, line=False)
    d.shape("hero2", ellipse(100, 90, 46, 11))
    d.shape("dark", "M58 90 C62 70 138 70 142 90 Q100 98 58 90Z", shadow=False)
    for x, y, r in [(74, 84, 20), (86, 78, -30), (98, 75, 10), (110, 78, 60), (124, 82, -20), (92, 86, 80), (114, 88, -50), (80, 90, 30), (132, 88, 10)]:
        d.shape("mark", ellipse(x, y, 5, 3.6), shadow=False, line=False, extra=f'transform="rotate({r} {x} {y})"')
        d.stroke("hero2", f"M{x-3} {y} Q{x} {y+1.2} {x+3} {y}", 1, line=False)
    # scoop with beans in front
    d.limb("hero", "M150 150 L176 134", 6)
    d.shape("hero", "M120 146 H160 C160 160 150 166 140 166 C130 166 120 160 120 146Z")
    for x, y in [(130, 145), (140, 142), (150, 145)]:
        d.shape("dark", ellipse(x, y, 5, 3.6), shadow=False)
    for x, y, r in [(52, 168, 20), (66, 172, -30), (96, 170, 40)]:
        d.shape("dark", ellipse(x, y, 5, 3.6), extra=f'transform="rotate({r} {x} {y})"')
        d.stroke("hero2", f"M{x-3} {y} Q{x} {y+1.2} {x+3} {y}", 1, line=False)


# ================================================================ TEA PLANTATION
def tea_terraces(d: Drawing):
    d.disc("glow", 58, 52, 18)
    d.band("far", "M-30 96 Q30 58 80 82 Q130 48 230 86")
    d.shape("light", cloud(110, 84, 1.3), shadow=False)
    rows = [(108, "mid"), (122, "near"), (136, "mid"), (150, "near"), (164, "mid"), (178, "near"), (192, "mid")]
    for i, (y, role) in enumerate(rows):
        d.band(role, bumpy(-30, y + 14, 90, y - 22, 230, y + 10, n=16 + i))
    d.shape("light", cloud(-6, 116, 1.1), shadow=False, line=False)
    # a picker's conical hat on the slope
    d.shape("hero2", "M132 120 L144 110 L156 120Z", spot=True)
    d.shape("dark", "M141 120 H147 V128 H141Z", shadow=False)


def tea_sprig(d: Drawing):
    d.disc("glow", 100, 96, 60, line=False)
    table(d, 160, "far", "deep")
    # heap of fresh leaves in the basket
    for x, y, ang in [(60, 116, 210), (74, 114, 240), (90, 112, 260), (110, 112, 280), (126, 114, 300), (140, 116, 330),
                      (70, 118, 280), (130, 118, 250)]:
        d.shape("mid" if (x // 10) % 2 else "near", leaf(x, y, 24, 12, ang), shadow=False)
    # two leaves and a bud
    d.stroke("near", "M100 116 Q98 90 102 60", 3, shadow=True)
    d.shape("near", leaf(100, 98, 40, 22, 205), spot=True)
    d.stroke("mid", leaf_vein(100, 98, 40, 205), 1.5, line=False)
    d.shape("near", leaf(101, 80, 36, 20, 330), spot=True)
    d.stroke("mid", leaf_vein(101, 80, 36, 330), 1.5, line=False)
    d.shape("mid", leaf(102, 64, 28, 10, 275))
    # wicker basket
    d.shape("hero", "M40 116 H160 L148 164 H52Z")
    for y in [128, 140, 152]:
        d.stroke("mark", f"M{44 + (y-116)*0.25:.0f} {y} H{156 - (y-116)*0.25:.0f}", 1.6, line=False)
    for x in range(56, 150, 12):
        d.stroke("mark", f"M{x} 118 L{x + (100 - x) * 0.12:.0f} 162", 1.2, line=False)
    d.limb("hero2", "M40 117 H160", 7)


def tea_pour(d: Drawing):
    d.disc("glow", 100, 88, 58, line=False)
    table(d, 152, "far", "mid")
    d.stroke("pop", "M117 88 Q120 102 120 122", 3.4)
    # cup on saucer
    d.shape("light", ellipse(122, 152, 36, 6))
    d.stroke("light", "M146 128 C160 126 160 142 144 142", 4, shadow=True)
    d.shape("light", "M96 120 H148 C148 140 138 150 122 150 C106 150 96 140 96 120Z")
    d.shape("pop", ellipse(122, 121, 25, 4.5), shadow=False, spot=True)
    steam(d, [112, 132], 112, 18)
    def pot():
        d.stroke("hero", "M38 70 C18 66 18 96 40 92", 5, shadow=True)
        d.shape("hero", "M88 84 Q104 80 108 64 L114 62 Q110 86 92 96Z")
        d.shape("hero", ellipse(64, 82, 30, 24), spot=True)
        d.shape("hero2", ellipse(64, 60, 16, 4.5), shadow=False)
        d.shape("hero2", circle(64, 54, 4), shadow=False)
        d.stroke("hero2", "M38 88 Q64 98 90 88", 2.4, line=False)
    group(d, "rotate(28 64 80)", pot)


# ================================================================ CHOCOLATE TASTING
def choc_bar(d: Drawing):
    d.disc("glow", 100, 100, 62, line=False)
    def bar():
        d.shape("hero", "M60 68 H164 V132 H36 V102 L46 99 L44 90 L54 86 L52 76 L60 74Z", spot=False)
        cells = [(i, j) for i in range(5) for j in range(2)]
        for i, j in cells:
            x, y = 36 + i * 25.6, 68 + j * 32
            if (i, j) == (0, 0):
                continue
            d.shape("hero2", rrect(x + 3.5, y + 3.5, 18.6, 25, 3), shadow=False, line=(i < 3))
            d.shape("mark", f"M{x+3.5} {y+28.5} H{x+22.1} V{y+6} L{x+19} {y+25}H{x+6}Z", shadow=False, line=False)
        # foil and paper sleeve
        d.shape("light", "M120 64 H168 V136 H120 L124 128 L118 120 L124 112 L118 104 L124 96 L118 88 L124 80 L118 72Z")
        d.shape("pop", "M140 62 H170 V138 H140Z", spot=True)
        d.stroke("light", "M146 62 V138", 2, line=False)
    group(d, "rotate(-18 100 100)", bar)
    # the broken-off piece
    d.shape("hero", "M36 140 L58 134 L64 154 L48 162 L42 156 L34 158Z")
    d.shape("hero2", "M41 142 L55 138 L59 151 L46 156Z", shadow=False, line=False)


def choc_pod(d: Drawing):
    d.disc("glow", 100, 96, 60, line=False)
    d.shape("near", leaf(150, 64, 44, 22, 330))
    d.shape("near", leaf(150, 64, 40, 20, 260))
    d.stroke("mid", leaf_vein(150, 64, 44, 330) + " " + leaf_vein(150, 64, 40, 260), 1.5, line=False)
    # whole pod behind
    def whole():
        d.shape("hero", "M0 -22 C22 -22 50 -12 56 0 C50 12 22 22 0 22 C-22 22 -50 12 -56 0 C-50 -12 -22 -22 0 -22Z")
        d.stroke("mark", "M-50 -6 Q0 -16 50 -6 M-52 6 Q0 16 52 6 M-56 0 H56", 1.6)
        d.stroke("dark", "M-56 0 L-62 -2", 3)
    group(d, "translate(118 80) rotate(-30)", whole)
    # split pod in front
    d.shape("hero", "M28 124 C40 104 160 104 172 124 C164 150 36 150 28 124Z", spot=True)
    d.shape("light", "M36 124 C48 110 152 110 164 124 C156 140 44 140 36 124Z", shadow=False)
    for x, y in [(58, 120), (76, 116), (94, 115), (112, 116), (130, 117), (148, 121), (66, 130), (84, 131), (102, 131), (120, 131), (138, 129)]:
        d.shape("mark", ellipse(x, y, 7.5, 5), shadow=False)
    d.stroke("mark", "M28 124 C40 140 160 140 172 124", 1.4, line=False)


def bonbon(d: Drawing, x, y, kind):
    d.shape("light", circle(x, y, 14), shadow=False)
    d.stroke("ground", circle(x, y, 12.5), 1, line=False)
    if kind == 0:
        d.shape("hero", circle(x, y, 10.5))
        d.stroke("hero2", f"M{x-7} {y-3} L{x-3} {y+3} L{x+1} {y-3} L{x+5} {y+3} L{x+8} {y-1}", 1.6)
    elif kind == 1:
        d.shape("hero2", rrect(x - 10, y - 10, 20, 20, 3))
        d.marks("pop", circle(x, y, 3))
    elif kind == 2:
        d.shape("mark", circle(x, y, 10.5))
        for dx, dy in [(-4, -3), (3, -5), (5, 2), (-2, 4), (0, 0), (-6, 2)]:
            d.marks("hero2", circle(x + dx, y + dy, 1))
    else:
        d.shape("pop", f"M{x} {y+9} C{x-14} {y} {x-10} {y-12} {x} {y-5} C{x+10} {y-12} {x+14} {y} {x} {y+9}Z", spot=True)


def choc_truffles(d: Drawing):
    d.disc("glow", 100, 100, 74, line=False)
    def box():
        d.shape("deep", rrect(44, 44, 112, 112, 8))
        d.shape("dark", rrect(50, 50, 100, 100, 5), shadow=False, line=False)
        for j in range(3):
            for i in range(3):
                bonbon(d, 67 + i * 33, 67 + j * 33, (i + j * 2) % 4)
    group(d, "rotate(-10 100 100)", box)
    d.limb("pop", "M150 34 Q160 60 168 64", 5, spot=True)


# ================================================================ CHEESE TASTING
def holes(d: Drawing, pts):
    for x, y, rx, ry in pts:
        d.shape("mark", ellipse(x, y, rx, ry), shadow=False)


def cheese_board(d: Drawing):
    d.disc("glow", 100, 82, 58, line=False)
    table(d, 150, "far", "mid")
    d.shape("ground", "M28 118 H172 L180 146 H20Z")
    d.shape("near", rrect(20, 145, 160, 9, 3), shadow=False)
    # grapes behind
    grape_pile(d, [(92, 96), (104, 98), (98, 108), (110, 108), (86, 106), (104, 116)], "pop", r=7)
    d.stroke("near", "M98 90 Q100 82 108 80", 2.4)
    # wedge
    d.shape("hero2", "M36 132 L92 98 L98 104 L44 138Z", shadow=False)
    d.shape("hero", "M34 136 L96 102 V138 H34Z", spot=True)
    holes(d, [(70, 128, 4, 3), (84, 116, 3.5, 3), (86, 131, 3, 2.4), (56, 132, 2.5, 2)])
    # round soft cheese with a slice cut out
    d.shape("light", "M118 112 C118 102 170 102 170 112 V134 C170 144 118 144 118 134Z")
    d.shape("hero2", "M144 112 L170 112 V134 L144 120Z", shadow=False)
    d.shape("light", ellipse(144, 112, 26, 7), shadow=False)
    d.shape("hero2", "M144 112 L170 112 C170 116 160 118 152 119Z", shadow=False, line=False)
    # cheese knife on the board front
    d.shape("dark", rrect(40, 140, 30, 6, 3), shadow=False)
    d.shape("sky2", "M70 140 H120 L126 143 L120 146 H70Z", shadow=False)


def cheese_swiss(d: Drawing):
    d.disc("glow", 152, 48, 15)
    d.band("far", "M-30 108 L18 74 L44 94 L84 50 L118 90 L148 62 L190 98 L230 82")
    for s in ["M84 50 L95 63 L89 61 L84 66 L78 60 L73 62Z", "M148 62 L158 72 L152 71 L147 75 L142 70 L139 70Z", "M18 74 L26 82 L20 81 L16 85 L12 80Z"]:
        d.shape("light", s, shadow=False)
    d.band("mid", hills(120, 10))
    def wedge():
        d.shape("hero2", "M40 120 L150 88 L168 110Z")
        d.shape("hero", "M40 120 L168 110 V148 L40 156Z", spot=True)
        d.shape("pop", "M168 110 L150 88 V124 L168 148Z")
        holes(d, [(70, 136, 7, 5.5), (104, 128, 5, 4), (132, 138, 8, 6), (152, 124, 4, 3.4), (90, 146, 4, 3),
                  (116, 104, 6, 2.5), (142, 98, 4, 1.8)])
        d.shape("hero2", "M84 114 a6 4 0 0 0 12 -1Z", shadow=False, line=False)
    group(d, "translate(100 122) scale(.96) translate(-104 -122)", wedge)
    d.band("near", "M-30 172 Q100 164 230 174", line=False)


def cheese_wheel(d: Drawing, x, yb, w, h, role="hero"):
    d.shape(role, f"M{x-w/2} {yb-4} Q{x-w/2-3} {yb-h/2} {x-w/2} {yb-h+4} Q{x-w/2} {yb-h} {x-w/2+6} {yb-h} H{x+w/2-6} "
                  f"Q{x+w/2} {yb-h} {x+w/2} {yb-h+4} Q{x+w/2+3} {yb-h/2} {x+w/2} {yb-4} Q{x+w/2} {yb} {x+w/2-6} {yb} H{x-w/2+6} Q{x-w/2} {yb} {x-w/2} {yb-4}Z")
    d.stroke("hero2", f"M{x-w/2+4} {yb-h/2} H{x+w/2-4}", 2, line=False)


def cheese_cellar(d: Drawing):
    d.band("deep", "M-30 -30 L230 -30", line=False)
    d.limb("dark", "M34 20 V190 M166 20 V190", 7)
    for y in [76, 118, 160]:
        d.shape("ground", rrect(-30, y, 260, 7, 1))
    for x, yb, w, h, r in [(66, 76, 42, 22, "hero"), (110, 76, 40, 20, "pop"), (110, 56, 36, 18, "hero"), (150, 76, 34, 18, "hero"),
                           (58, 118, 40, 22, "pop"), (100, 118, 42, 24, "hero"), (142, 118, 40, 22, "hero"),
                           (64, 160, 44, 24, "hero"), (64, 136, 40, 22, "hero"), (110, 160, 40, 22, "pop"), (150, 160, 36, 20, "hero")]:
        cheese_wheel(d, x, yb, w, h, r)
    d.band("near", "M-30 172 L230 172", line=False)


# ================================================================ catalogue
WOOD = "#C68B59"
GRAPE = "#6B3F7A"
COPPER = {"hero": "#C8743E", "hero2": "#E8A877", "mark": "#9A5328"}

CONCEPTS = [
    # vineyard tour
    Concept("vtour-hills", "vineyard-tour", "Tuscan vine rows", vtour_hills,
            overrides={"mid": "#A3C46F", "deep": "#5C8A3F", "near": "#4E7D3A", "pop": "#C8643B", "dark": "#2F4F33"},
            checks=[("far", "mid"), ("dark", "far"), ("light", "far"), ("glow", "sky")],
            fixes={"far": ["near", "#D9C38C", "light"], "dark": ["deep", "mark"]}),
    Concept("vtour-crate", "vineyard-tour", "Harvest crate", vtour_crate,
            overrides={"hero": WOOD, "mark": "#8A5A3B", "hero2": GRAPE, "pop": "#A7C957", "near": "#5E9C4A"},
            checks=[("hero", "glow"), ("hero2", "glow"), ("pop", "glow"), ("near", "glow")],
            fixes={"glow": ["light", "sky2", "far", "#F1E6CF"]}),
    Concept("vtour-cellar", "vineyard-tour", "Barrel cellar", vtour_cellar,
            overrides={"hero": "#A8683A", "hero2": "#C68B59", "mark": "#8A5432", "dark": "#3B2A20", "glow2": "#FFD98A"},
            checks=[("hero", "far"), ("hero", "mid"), ("far", "deep")],
            fixes={"far": ["light", "sky2", "ground"], "mid": ["ground", "light", "far"]}),
    # brewery tour
    Concept("brew-tanks", "brewery-tour", "Copper brewhouse", brew_tanks,
            overrides={**COPPER, "hero2": "#C9D1D8", "mark": "#8A949E", "pop": "#E8A877", "light": "#F4F6F8"},
            checks=[("hero", "glow"), ("hero2", "glow"), ("hero", "ground")],
            fixes={"glow": ["light", "sky2", "far", "mid"], "ground": ["near", "deep", "far"]}),
    Concept("brew-flight", "brewery-tour", "Tasting flight", brew_flight,
            overrides={"hero": "#F2C14E", "pop": "#D9822B", "mark": "#9E3B1F", "dark": "#3B2418", "ground": "#B07A45", "near": "#7A5232"},
            checks=[("light", "glow"), ("ground", "far"), ("hero", "glow")],
            fixes={"glow": ["mid", "near", "deep", "#7FB7BE"], "far": ["mid", "deep", "sky2"]}),
    Concept("brew-hops", "brewery-tour", "Hops & barley", brew_hops,
            overrides={"hero": "#A8C66C", "mark": "#6E9440", "near": "#4F8A3C", "hero2": "#E0B44C"},
            checks=[("hero", "glow"), ("near", "glow"), ("hero2", "glow")],
            fixes={"glow": ["light", "sky2", "#F1E6CF", "deep"]}),
    # whisky distillery
    Concept("whisky-stills", "whisky-distillery", "Copper stills", whisky_stills, overrides=COPPER,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero", "ground")],
            fixes={"glow": ["light", "sky2", "far"], "ground": ["near", "deep", "far"]}),
    Concept("whisky-glass", "whisky-distillery", "Dram & cask", whisky_glass,
            overrides={"hero": "#A8683A", "hero2": "#C68B59", "mark": "#8A5432", "pop": "#D98A1E", "glow2": "#F2B65A"},
            checks=[("light", "far"), ("hero", "far"), ("light", "mid")],
            fixes={"far": ["mid", "near", "deep"], "mid": ["deep", "near", "dark"]}),
    Concept("whisky-pagoda", "whisky-distillery", "Highland distillery", whisky_pagoda,
            overrides={"dark": "#3A3F4B", "pop": "#9B5DA5", "near": "#6E9A55"},
            checks=[("light", "mid"), ("dark", "far"), ("dark", "sky"), ("light", "near")],
            fixes={"mid": ["near", "deep"], "dark": ["#6B7180", "mark"], "far": ["mid", "light"]}),
    # sake tasting
    Concept("sake-set", "sake-tasting", "Sake set", sake_set,
            overrides={"hero": "#F3EDE2", "mark": "#2E4A7D", "hero2": "#F6E8B8", "pop": "#F2A7B8", "dark": "#2B2224"},
            checks=[("hero", "glow"), ("hero", "far"), ("dark", "far")],
            fixes={"glow": ["mid", "near", "deep"], "far": ["mid", "deep"]}),
    Concept("sake-masu", "sake-tasting", "Overflowing masu", sake_masu,
            overrides={"hero": "#E8C99A", "mark": "#C9A06A", "hero2": "#F7EBC0"},
            checks=[("hero", "glow"), ("light", "glow"), ("hero", "far")],
            fixes={"glow": ["mid", "near", "deep"], "far": ["mid", "deep", "near"]}),
    Concept("sake-barrels", "sake-tasting", "Sake barrels", sake_barrels,
            overrides={"pop": "#C8302E", "mark": "#2E4A7D", "hero": "#D9A520", "ground": "#C9A46E"},
            checks=[("light", "glow"), ("light", "far"), ("light", "sky")],
            fixes={"glow": ["mid", "near", "deep"], "far": ["mid", "near", "deep"]}),
    # coffee plantation
    Concept("coffee-branch", "coffee-plantation", "Coffee cherries", coffee_branch,
            overrides={"pop": "#C8202E", "hero2": "#E8783A", "hero": "#9CC25A", "near": "#3F7D3A", "mid": "#6FA858", "dark": "#6B4A2E", "mark": "#5A1A12"},
            checks=[("pop", "glow"), ("near", "glow")], fixes={"glow": ["light", "sky2", "#F1E6CF"]}),
    Concept("coffee-hills", "coffee-plantation", "Volcano slopes", coffee_hills,
            overrides={"mid": "#8DBF6A", "near": "#4C8A3F", "deep": "#2F5F33", "pop": "#C8202E", "dark": "#6B4A2E"},
            checks=[("far", "sky"), ("far", "mid"), ("deep", "far")], fixes={"far": ["deep", "dark", "mark"], "deep": ["dark", "#1F3F22"]}),
    Concept("coffee-sack", "coffee-plantation", "Sack of beans", coffee_sack,
            overrides={"hero2": "#C9A46E", "mark": "#4A2A18", "dark": "#5A3420", "hero": "#9A6338"},
            checks=[("hero2", "glow"), ("hero2", "far"), ("dark", "far")],
            fixes={"glow": ["mid", "near", "deep"], "far": ["mid", "deep", "near"]}),
    # tea plantation
    Concept("tea-terraces", "tea-plantation", "Terraced tea rows", tea_terraces,
            overrides={"mid": "#8DC26F", "near": "#4F9150", "hero2": "#E8D9A8"},
            checks=[("far", "mid"), ("far", "sky"), ("hero2", "near"), ("hero2", "mid")],
            fixes={"far": ["deep", "#6E8F9E", "dark"]}),
    Concept("tea-sprig", "tea-plantation", "Two leaves & a bud", tea_sprig,
            overrides={"near": "#3F8A3F", "mid": "#8DC26F", "hero": "#C9A46E", "hero2": "#A9824F", "mark": "#8C6A3E"},
            checks=[("near", "glow"), ("hero", "glow"), ("mid", "glow"), ("hero", "far")],
            fixes={"glow": ["light", "sky2", "#F1E6CF"], "far": ["deep", "dark"]}),
    Concept("tea-pour", "tea-plantation", "Pouring tea", tea_pour,
            overrides={"pop": "#C9782E"},
            checks=[("hero", "glow"), ("light", "glow"), ("hero", "sky")],
            fixes={"hero": ["near", "deep", "mark"], "glow": ["mid", "near", "deep"]}),
    # chocolate tasting
    Concept("choc-bar", "chocolate-tasting", "Broken bar", choc_bar,
            overrides={"hero": "#6B3E26", "hero2": "#86513A", "mark": "#4A2A1A", "light": "#D9DCE3"},
            checks=[("hero", "glow"), ("pop", "glow"), ("light", "glow"), ("hero", "sky")],
            fixes={"glow": ["light", "sky2", "far", "mid"], "pop": ["hero2", "near", "deep"]}),
    Concept("choc-pod", "chocolate-tasting", "Cacao pod", choc_pod,
            overrides={"hero": "#E0A33A", "mark": "#6B3E26", "near": "#4F8A3C", "mid": "#7FB069", "light": "#FFF6E8", "dark": "#5A3A22"},
            checks=[("hero", "glow"), ("near", "glow")], fixes={"glow": ["mid", "near", "deep", "#7FB7BE"]}),
    Concept("choc-truffles", "chocolate-tasting", "Box of bonbons", choc_truffles,
            overrides={"hero": "#6B3E26", "hero2": "#A0673F", "mark": "#3E2416", "deep": "#8A2E3B", "dark": "#2E1C14", "light": "#F5ECDD", "ground": "#C9B79C"},
            checks=[("deep", "glow"), ("deep", "sky")], fixes={"glow": ["light", "sky2", "far"]}),
    # cheese tasting
    Concept("cheese-board", "cheese-tasting", "Cheese board", cheese_board,
            overrides={"hero": "#F6C945", "hero2": "#FBE08A", "mark": "#D9A520", "ground": "#C68B59", "near": "#9A6338", "pop": GRAPE, "light": "#FFFBF0", "sky2": "#C9CED6"},
            checks=[("ground", "far"), ("ground", "glow"), ("light", "glow")],
            fixes={"far": ["mid", "deep"], "glow": ["mid", "near", "deep"]}),
    Concept("cheese-swiss", "cheese-tasting", "Alpine wedge", cheese_swiss,
            overrides={"hero": "#F6C945", "hero2": "#FBE08A", "mark": "#D9A520", "pop": "#E0A33A", "mid": "#8CC084", "near": "#5E9C6A"},
            checks=[("hero", "mid"), ("hero2", "far"), ("pop", "far"), ("far", "mid")],
            fixes={"far": ["deep", "near", "#6E8F9E"]}),
    Concept("cheese-cellar", "cheese-tasting", "Ageing cellar", cheese_cellar,
            overrides={"hero": "#E8B04B", "hero2": "#F5CF7A", "pop": "#C98A2E", "ground": "#9A6338", "dark": "#5A3A22"},
            checks=[("hero", "deep"), ("pop", "deep"), ("ground", "deep")],
            fixes={"deep": ["dark", "mark", "near"]}),
]
