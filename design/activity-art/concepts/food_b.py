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
    d.stroke("near", "M100 62 Q96 44 72 44", 3.2, shadow=True)
    for L, W, ang in [(40, 24, 200), (36, 20, 250), (34, 20, 150)]:
        d.shape("near", leaf(72, 50, L, W, ang), shadow=ang == 200)
        d.stroke("mark", leaf_vein(72, 50, L, ang), 1.4, line=False)
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
    d.disc("glow", 100, 80, 58, line=False)
    table(d, 154, "far", "mid")
    # masu box: top rim seen from slightly above, sake pooled inside
    d.shape("hero", "M40 112 L60 92 H164 L144 112Z")
    d.shape("hero2", "M50 109 L64 96 H154 L140 109Z", shadow=False, spot=True)
    # glass standing in it, brimming over
    d.shape("light", "M86 46 H122 L118 104 H90Z")
    d.shape("hero2", "M87.5 52 H120.5 L117 102 H91Z", shadow=False)
    d.stroke("light", "M95 58 L97 96", 3, line=False)
    d.shape("hero2", "M84 44 Q104 38 124 44 Q126 50 122 51 Q104 47 86 51 Q82 50 84 44Z", shadow=False)
    d.stroke("hero2", "M86 50 Q84 70 88 90 M122 50 Q125 66 121 84", 2.6, line=False)
    # front faces with cedar grain
    d.shape("hero", "M40 112 H144 V158 H40Z")
    d.shape("mark", "M144 112 L164 92 V138 L144 158Z")
    d.stroke("mark", "M48 124 Q92 120 136 126 M48 140 Q92 136 136 142", 1.3, line=False)
    for x, y, r in [(70, 52, 2.6), (136, 48, 3), (142, 70, 2.2)]:
        d.marks("hero2", circle(x, y, r))


def komodaru(d: Drawing, x, yb, label, w=48, h=36):
    l, r, t = x - w / 2, x + w / 2, yb - h
    d.shape("light", f"M{l} {t} Q{l-4} {yb - h/2} {l} {yb-3} Q{x} {yb+4} {r} {yb-3} Q{r+4} {yb - h/2} {r} {t} Q{x} {t+6} {l} {t}Z")
    d.shape("ground", ellipse(x, t, w / 2, 5.5), shadow=False)
    d.stroke("mark", f"M{l+3} {t} A{w/2-3} 4 0 0 0 {r-3} {t}", 1, line=False)
    d.shape(label, f"M{x-15} {t+9} Q{x} {t+13} {x+15} {t+9} V{yb-8} Q{x} {yb-4} {x-15} {yb-8}Z", shadow=False, spot=label == "pop")
    d.shape("light", circle(x, yb - h / 2 + 2, 6), shadow=False, line=False)
    d.marks("hero", circle(x, yb - h / 2 + 2, 3))
    d.stroke("dark", f"M{l+3} {t+5} Q{l} {yb - h/2} {l+3} {yb-5} M{r-3} {t+5} Q{r} {yb - h/2} {r-3} {yb-5}", 1.6)
    d.stroke("dark", f"M{l} {yb-7} Q{x} {yb} {r} {yb-7}", 1.4, line=False)

def sake_barrels(d: Drawing):
    d.band("deep", "M-30 -30 L230 -30", line=False)
    d.disc("glow", 100, 96, 64, line=False)
    d.band("far", "M-30 150 L230 150")
    def stack():
        for x, yb, lab in [(52, 160, "pop"), (100, 160, "mark"), (148, 160, "pop"), (76, 124, "mark"), (124, 124, "pop"), (100, 88, "mark")]:
            komodaru(d, x, yb, lab)
    group(d, "translate(100 116) scale(.9) translate(-100 -112)", stack)
    d.band("near", "M-30 172 L230 172", line=False)
    # shimenawa rope with paper streamers across the top
    d.limb("ground", "M-30 30 Q100 54 230 30", 7)
    for x in [60, 100, 140]:
        y = 30 + 24 * (1 - ((x - 100) / 130) ** 2) * 0.98
        d.shape("light", f"M{x-4} {y+3} H{x+4} L{x+1} {y+9} H{x+5} L{x+2} {y+15} H{x+6} L{x} {y+22} L{x-4} {y+15} H{x-1} L{x-4} {y+9} H{x}Z", shadow=False)


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
            d.shape("near", circle(x, y, r), shadow=row > 0, line=row > 0)
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
    d.shape("hero2", "M48 160 C38 130 46 102 58 90 H142 C154 102 162 130 152 160Z")
    d.stroke("mark", "M60 106 V154 M76 100 V158 M92 100 V158 M108 100 V158 M124 100 V158 M140 106 V154", 1.2, line=False)
    line_only(d, "M54 120 Q100 126 146 120 M50 140 Q100 146 150 140", 1.6)
    d.shape("hero2", ellipse(100, 90, 46, 11))
    d.shape("dark", "M58 90 C62 70 138 70 142 90 Q100 98 58 90Z", shadow=False)
    for x, y, r in [(74, 84, 20), (86, 78, -30), (98, 75, 10), (110, 78, 60), (124, 82, -20), (92, 86, 80), (114, 88, -50), (80, 90, 30), (132, 88, 10)]:
        d.shape("mark", ellipse(x, y, 5, 3.6), shadow=False, line=False, extra=f'transform="rotate({r} {x} {y})"')
        d.stroke("hero2", f"M{x-3} {y} Q{x} {y+1.2} {x+3} {y}", 1, line=False)
    # scoop with beans in front
    d.limb("hero", "M150 150 L176 134", 6)
    d.shape("hero", "M120 146 H160 C160 160 150 166 140 166 C130 166 120 160 120 146Z", spot=True)
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
    d.shape("hero", "M24 118 C44 96 156 96 176 118 C162 160 38 160 24 118Z", spot=True)
    d.stroke("pop", "M40 136 Q100 150 160 136 M56 148 Q100 156 144 148", 1.8, line=False)
    d.shape("light", "M34 118 C52 104 148 104 166 118 C152 134 48 134 34 118Z", shadow=False)
    for x, y in [(56, 116), (74, 111), (92, 109), (110, 109), (128, 111), (146, 116), (66, 124), (84, 123), (102, 123), (120, 123), (138, 123)]:
        d.shape("mark", ellipse(x, y, 8.5, 5.6), shadow=False)
        d.shape("hero2", ellipse(x - 2, y - 1.5, 3.4, 1.8), shadow=False, line=False)


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


# ================================================================ CHEESE TASTING
def holes(d: Drawing, pts):
    for x, y, rx, ry in pts:
        d.shape("mark", ellipse(x, y, rx, ry), shadow=False)


def cheese_board(d: Drawing):
    d.disc("glow", 100, 80, 58, line=False)
    table(d, 152, "far", "mid")
    d.shape("ground", "M26 122 H174 L182 150 H18Z")
    d.shape("near", rrect(18, 149, 164, 9, 3), shadow=False)
    # grapes behind
    d.stroke("near", "M108 66 Q112 56 122 54", 2.6)
    grape_pile(d, [(100, 76), (113, 74), (124, 80), (106, 88), (119, 90), (112, 101)], "pop", r=7.5)
    # round soft cheese with a slice cut out
    d.shape("light", "M104 104 C104 90 176 90 176 104 V128 C176 142 104 142 104 128Z")
    d.shape("hero2", "M140 104 L176 104 V128 L140 116Z", shadow=False)
    d.shape("light", ellipse(140, 104, 36, 10), shadow=False)
    d.shape("hero2", "M140 104 L176 104 C176 109 164 112 154 113Z", shadow=False, line=False)
    # big wedge
    d.shape("hero2", "M28 128 L98 82 L108 90 L38 136Z", shadow=False)
    d.shape("hero", "M26 134 L104 86 V140 H26Z", spot=True)
    d.shape("mark", "M104 86 L110 90 V140 H104Z", shadow=False, line=False)
    holes(d, [(70, 124, 6, 4.5), (88, 108, 4.5, 3.5), (92, 128, 4, 3), (52, 130, 3.4, 2.6), (80, 136, 3, 2)])
    # knife on the front lip
    d.shape("dark", rrect(118, 142, 22, 6, 3), shadow=False)
    d.shape("sky2", "M140 142 H170 L176 145 L170 148 H140Z", shadow=False)


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
    d.shape(role, spot=role == "pop", d=f"M{x-w/2} {yb-4} Q{x-w/2-3} {yb-h/2} {x-w/2} {yb-h+4} Q{x-w/2} {yb-h} {x-w/2+6} {yb-h} H{x+w/2-6} "
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


# ================================================================ PICNIC
def gingham(d: Drawing, x, y, w, h, n, role="pop"):
    """Red-and-white check: overlapping translucent stripes (papercut), a sparse grid (line)."""
    step = w / n
    for i in range(0, n, 2):
        d.shape(role, f"M{x + i*step:.1f} {y} h{step:.1f} v{h} h{-step:.1f}Z", shadow=False, line=False, extra='opacity=".55"')
    step_h = h / n
    for j in range(0, n, 2):
        d.shape(role, f"M{x} {y + j*step_h:.1f} h{w} v{step_h:.1f} h{-w}Z", shadow=False, line=False, extra='opacity=".55"')
    grid = " ".join(f"M{x + i*step:.1f} {y} v{h}" for i in range(2, n, 2)) + " " + " ".join(f"M{x} {y + j*step_h:.1f} h{w}" for j in range(2, n, 2))
    line_only(d, grid, 1.4)


def picnic_blanket(d: Drawing):
    d.band("mid", "M-30 -30 L230 -30", line=False)
    for x, y in [(24, 60), (170, 150), (40, 160), (160, 40), (100, 178)]:
        d.stroke("near", f"M{x} {y} l-3 -7 M{x} {y} l0 -8 M{x} {y} l3 -7", 1.6, line=False)
    def blanket():
        d.shape("light", rrect(44, 44, 112, 112, 2))
        gingham(d, 44, 44, 112, 112, 8)
    group(d, "rotate(-12 100 100)", blanket)
    # plate of sandwiches
    d.shape("light", circle(78, 82, 22))
    d.stroke("sky2", circle(78, 82, 16), 1.4, line=False)
    d.shape("hero2", "M64 74 L90 70 L76 94Z")
    d.stroke("near", "M67 76 L88 72.5", 2.4, line=False)
    d.shape("hero2", "M80 92 L94 74 L96 96Z", shadow=False)
    # watermelon slice
    d.shape("near", "M104 132 A30 30 0 0 0 158 116Z", spot=False)
    d.shape("light", "M108 129 A25 25 0 0 0 153 116Z", shadow=False, line=False)
    d.shape("hero", "M111 127 A22 22 0 0 0 150 116Z", shadow=False, spot=True)
    d.marks("dark", ellipse(126, 126, 1.4, 2.2) + ellipse(136, 123, 1.4, 2.2) + ellipse(142, 118, 1.4, 2.2))
    # cups and an apple
    for x, y in [(134, 70), (150, 84)]:
        d.shape("ground", circle(x, y, 10))
        d.shape("glow2", circle(x, y, 7), shadow=False)
    d.shape("near", circle(66, 134, 11))
    d.shape("light", circle(62, 130, 2.4), shadow=False, line=False)
    d.stroke("dark", "M66 124 l1 -5", 2)
    d.shape("mid", leaf(67, 120, 10, 6, -30), shadow=False)


def hamper(d: Drawing):
    d.limb("dark", "M66 100 C66 66 134 66 134 100", 6)
    # baguette and bottle poking out of the open side
    d.shape("deep", "M120 104 V64 C120 58 124 56 124 50 V40 H132 V50 C132 56 136 58 136 64 V104Z")
    d.shape("light", rrect(123.5, 38, 9, 5, 1.5), shadow=False)
    d.shape("hero2", "M74 102 L150 52 C156 48 162 54 158 60 L92 110Z", spot=True)
    d.stroke("mark", "M118 74 l6 6 M130 66 l6 6 M142 58 l5 5", 2)
    d.shape("hero", rrect(42, 100, 116, 56, 6))
    for y in [112, 124, 136, 148]:
        d.stroke("mark", f"M46 {y} H154", 1.4, line=False)
    for x in range(52, 152, 10):
        d.stroke("mark", f"M{x} 102 V154", 1, line=False)
    d.shape("hero", rrect(38, 94, 62, 12, 4))
    d.stroke("dark", "M62 100 V128 M138 104 V128", 4)
    d.shape("ground", rrect(56, 124, 12, 8, 2), shadow=False)
    d.shape("ground", rrect(132, 124, 12, 8, 2), shadow=False)
    # napkin hanging over the front
    def nap():
        d.shape("light", rrect(-14, -14, 28, 28, 1))
        gingham(d, -14, -14, 28, 28, 4)
    group(d, "translate(118 108) rotate(45)", nap)


def picnic_basket(d: Drawing):
    d.disc("glow", 100, 84, 58)
    d.band("mid", hills(146, 6))
    d.band("near", "M-30 172 Q100 164 230 172", line=False)
    hamper(d)


def picnic_tree(d: Drawing):
    d.disc("glow", 64, 58, 18)
    d.shape("light", cloud(18, 94, 0.9), shadow=False)
    # kite
    d.stroke("dark", "M70 52 Q80 90 104 118", 1.2)
    d.shape("hero2", "M62 30 L78 42 L70 62 L54 46Z", spot=True)
    d.stroke("pop", "M70 62 q-4 6 0 10 q4 4 0 10", 2)
    d.band("far", hills(118, 10))
    d.band("mid", "M-30 150 Q60 124 230 140")
    # big shady tree
    d.limb("dark", "M150 150 V96 M150 116 L132 98 M150 108 L166 92", 8)
    d.shape("near", "M104 96 C96 70 120 46 146 52 C164 34 196 52 190 76 C204 92 186 114 166 108 C154 120 130 116 124 106 C108 112 98 104 104 96Z")
    d.shape("deep", "M118 92 C126 82 140 86 144 94 C134 100 124 98 118 92Z", shadow=False, line=False)
    # blanket and basket under it
    A, B, C, D = (58, 156), (146, 140), (178, 162), (88, 182)
    lerp = lambda p, q, t: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    def quad(u0, u1, v0, v1):
        pts = []
        for u, v in [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]:
            top, bot = lerp(A, B, u), lerp(D, C, u)
            pts.append(lerp(top, bot, v))
        return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"
    d.shape("light", quad(0, 1, 0, 1))
    for k in range(0, 8, 2):
        d.shape("pop", quad(k / 8, (k + 1) / 8, 0, 1), shadow=False, line=False, extra='opacity=".6"')
        d.shape("pop", quad(0, 1, k / 8, (k + 1) / 8), shadow=False, line=False, extra='opacity=".6"')
    d.stroke("dark", "M116 146 C116 128 144 128 144 146", 2.6)
    d.shape("hero", rrect(112, 142, 36, 20, 3), spot=True)
    d.stroke("mark", "M114 150 H146 M114 156 H146", 1.2, line=False)


# ================================================================ FRUIT MARKET
def fruit_heap(d: Drawing, pts, role, r, spot=False, dot="mark"):
    for x, y in pts:
        d.shape(role, circle(x, y, r), spot=spot)
        d.shape("light", circle(x - r * 0.35, y - r * 0.35, r * 0.2), shadow=False, line=False)


def fruit_stall(d: Drawing):
    d.disc("glow", 150, 46, 16)
    d.band("far", "M-30 150 V96 H18 V80 H40 V104 H160 V86 H184 V100 H230")
    d.band("ground", "M-30 160 L230 160")
    d.stroke("dark", "M36 72 V160 M164 72 V160", 3.2)
    # peaked striped awning
    for i in range(8):
        x0 = 28 + i * 18
        role = "mid" if i % 2 == 0 else "light"
        d.shape(role, f"M{x0} 76 L{x0+18} 76 L{100 + (x0 + 18 - 100) * 0.5:.1f} 46 L{100 + (x0 - 100) * 0.5:.1f} 46Z", shadow=i == 0, spot=i % 2 == 0)
    d.shape("mid", rrect(26, 74, 148, 8, 2))
    # crates heaped with fruit
    fruit_heap(d, [(48, 112), (60, 110), (54, 102), (72, 112)], "hero", 8.5)
    fruit_heap(d, [(92, 110), (104, 112), (116, 110), (98, 100), (110, 101)], "pop", 8.5, spot=True)
    d.shape("hero2", "M126 112 C128 96 142 88 158 94 C146 96 136 104 134 114Z")
    d.shape("hero2", "M134 114 C138 98 152 92 166 100 C154 100 146 106 142 116Z")
    d.shape("hero2", "M142 116 C148 104 160 100 170 108 C160 108 154 112 150 118Z")
    for x in [40, 84, 128]:
        d.shape("ground", rrect(x, 114, 44, 30, 2))
        d.stroke("mark", f"M{x+2} 124 H{x+42} M{x+2} 134 H{x+42}", 1.4, line=False)
    d.shape("near", rrect(30, 144, 140, 6, 2))
    for x in [58, 102, 146]:
        d.shape("light", f"M{x-6} 122 H{x+6} V130 L{x} 134 L{x-6} 130Z", shadow=False)


def pineapple(d: Drawing, x, y, role="ground"):
    for ang, L in [(-90, 30), (-115, 26), (-65, 26), (-135, 20), (-45, 20)]:
        d.shape("near", leaf(x, y - 26, L, 9, ang))
    d.shape(role, ellipse(x, y, 21, 30), spot=True)
    d.stroke("mark", f"M{x-18} {y-12} L{x+6} {y+26} M{x-12} {y-24} L{x+18} {y+16} M{x+2} {y-29} L{x+20} {y-2} "
                     f"M{x+18} {y-12} L{x-6} {y+26} M{x+12} {y-24} L{x-18} {y+16} M{x-2} {y-29} L{x-20} {y-2}", 1.6, line=False)


def fruit_tropical(d: Drawing):
    d.disc("glow", 100, 84, 60, line=False)
    table(d, 150, "far", "mid")
    pineapple(d, 92, 92)
    # bananas
    for k, dy in enumerate([0, 9, 18]):
        d.shape("hero2", f"M118 {84+dy} C134 {108+dy} 160 {110+dy} 176 {94+dy} C178 {100+dy} 170 {116+dy} 150 {120+dy} C132 {122+dy} 120 {104+dy} 118 {84+dy}Z", spot=k == 2)
    d.shape("dark", rrect(113, 80, 8, 6, 2), shadow=False)
    # mango
    d.shape("pop", "M124 150 C112 150 106 130 124 122 C140 116 160 124 160 138 C160 150 140 152 124 150Z")
    # watermelon wedge in front
    d.shape("near", "M22 132 A44 44 0 0 0 104 132Z")
    d.shape("light", "M28 132 A38 38 0 0 0 98 132Z", shadow=False, line=False)
    d.shape("hero", "M32 132 A33 33 0 0 0 94 132Z", shadow=False, spot=True)
    for x, y in [(50, 140), (62, 148), (76, 146), (84, 138), (64, 138)]:
        d.marks("dark", ellipse(x, y, 1.6, 2.6))


def fruit_boat(d: Drawing):
    d.disc("glow", 150, 50, 17)
    d.band("far", bumpy(-30, 104, 100, 92, 230, 102, n=12))
    # stilt houses on the bank
    for x, w in [(26, 30), (128, 34)]:
        d.shape("ground", rrect(x, 84, w, 20, 1))
        d.shape("dark", f"M{x-4} 86 L{x + w/2} 70 L{x + w + 4} 86Z")
        d.marks("dark", rrect(x + w/2 - 4, 90, 8, 10, 1))
    d.band("mid", waves(112, 3, 30))
    d.band("near", waves(150, 3, 34), line=False)
    # rower with conical hat and paddle
    d.limb("dark", "M50 88 L24 156", 3.4)
    d.shape("mark", rrect(30, 98, 22, 34, 9))
    d.shape("light", "M20 102 L41 84 L62 102Z", spot=True)
    # piles of fruit
    fruit_heap(d, [(70, 124), (80, 122), (75, 114)], "pop", 6.5)
    fruit_heap(d, [(94, 124), (104, 124), (99, 115)], "hero", 6.5)
    d.shape("hero2", "M114 128 C116 112 132 108 140 116 C132 116 124 122 122 130Z")
    d.shape("hero2", "M118 130 C122 116 138 112 146 120 C138 120 130 124 126 132Z")
    fruit_heap(d, [(152, 126), (162, 124), (157, 117)], "glow2", 6)
    # long boat
    d.shape("ground", "M14 120 Q20 130 30 134 H170 Q184 128 190 112 Q190 136 168 146 H36 Q16 140 14 120Z")
    d.stroke("dark", "M30 136 H170", 2, line=False)
    d.stroke("light", "M40 158 q8 -4 16 0 M120 162 q8 -4 16 0 M160 154 q6 -3 12 0", 2)


# ================================================================ TAPAS CRAWL
def cazuela(d: Drawing, x, y, r):
    d.shape("hero", circle(x, y, r))
    d.shape("mark", circle(x, y, r - 5), shadow=False)


def tapas_plates(d: Drawing):
    d.band("ground", "M-30 -30 L230 -30", line=False)
    d.stroke("deep", "M-30 40 Q100 34 230 44 M-30 100 Q100 96 230 104 M-30 160 Q100 154 230 164", 1.6, line=False)
    # patatas bravas
    cazuela(d, 68, 78, 32)
    for x, y in [(56, 70), (70, 66), (82, 74), (60, 84), (74, 82), (66, 94), (82, 90)]:
        d.shape("hero2", rrect(x - 6, y - 6, 12, 12, 2.5), shadow=False)
    d.stroke("pop", "M54 74 Q62 70 68 78 T84 80", 3.4)
    d.marks("light", circle(64, 88, 2) + circle(76, 72, 2) + circle(58, 78, 1.6))
    # olives
    cazuela(d, 140, 82, 28)
    for x, y in [(130, 74), (144, 70), (152, 82), (138, 86), (128, 90), (148, 94)]:
        d.shape("near", ellipse(x, y, 6.5, 5), shadow=False, spot=True)
        d.marks("pop", circle(x + 2, y - 1, 1.8))
    # tortilla on a plate, one wedge pulled out
    d.shape("light", circle(100, 140, 36))
    d.stroke("sky2", circle(100, 140, 30), 1.4, line=False)
    ax, ay = 100 + 28 * math.cos(math.radians(-30)), 140 + 28 * math.sin(math.radians(-30))
    d.shape("glow2", f"M100 140 L{ax:.1f} {ay:.1f} A28 28 0 1 1 100 112Z", spot=True)
    d.stroke("mark", "M80 140 q6 -4 10 0 M92 156 q6 -4 10 0 M110 148 q4 -3 8 0 M80 124 q5 -3 9 0", 1.4, line=False)
    d.shape("glow2", f"M106 134 L106 106 A28 28 0 0 1 {ax + 6:.1f} {ay - 6:.1f}Z")
    d.stroke("mark", "M110 122 q4 -3 8 0", 1.4, line=False)


def pintxo(d: Drawing, x, top):
    d.shape("hero2", f"M{x-22} 132 C{x-24} 120 {x-20} 114 {x-14} 113 H{x+14} C{x+20} 114 {x+24} 120 {x+22} 132Z")
    d.shape("light", f"M{x-18} 118 Q{x} 112 {x+18} 118 Q{x} 121 {x-18} 118Z", shadow=False, line=False)
    top()


def tapas_pintxos(d: Drawing):
    d.disc("glow", 100, 88, 58, line=False)
    table(d, 132, "far", "mid", 12)
    d.shape("light", rrect(18, 128, 164, 8, 4))
    def p1():
        d.shape("hero", "M30 116 C30 104 54 102 56 116Z", spot=True)
        d.shape("hero", rrect(30, 104, 26, 13, 4))
        d.stroke("mark", "M32 110 H54", 1.4, line=False)
        d.stroke("ground", "M43 120 V84", 2.2)
        d.shape("near", circle(43, 82, 5))
    def p2():
        d.shape("pop", "M76 116 C72 100 84 92 90 102 C96 90 112 96 110 108 C116 112 112 118 104 116Z", spot=True)
        d.stroke("light", "M82 104 Q90 108 96 102 M96 110 Q104 112 108 106", 2, line=False)
        d.stroke("ground", "M94 120 V78", 2.2)
        d.shape("hero", "M88 80 C88 72 100 72 100 80Z", shadow=False)
    def p3():
        d.shape("pop", "M124 116 C126 104 156 100 164 112 C160 116 140 118 124 116Z")
        d.shape("dark", "M128 110 C134 98 154 96 162 104 C152 104 140 108 134 112Z")
        d.stroke("light", "M136 104 L152 102", 1.2, line=False)
        d.stroke("ground", "M146 118 V80", 2.2)
        d.shape("near", "M140 84 C142 76 150 76 152 84 L146 96Z")
    def row():
        pintxo(d, 43, p1)
        pintxo(d, 94, p2)
        pintxo(d, 146, p3)
    group(d, "translate(100 130) scale(1.16) translate(-96 -130)", row)


def tapas_jamon(d: Drawing):
    d.disc("glow", 100, 88, 60, line=False)
    table(d, 158, "far", "mid")
    # jamonero stand
    d.shape("ground", rrect(26, 146, 148, 12, 3))
    d.limb("dark", "M52 146 V64", 6)
    d.shape("dark", rrect(42, 56, 22, 12, 3))
    d.limb("dark", "M146 146 V122 M136 122 H156", 6)
    # the ham
    d.shape("hero", "M158 118 C176 102 168 74 144 72 C122 70 100 82 80 76 L58 60 L50 68 L70 90 C66 112 86 134 114 138 C132 140 148 130 158 118Z", spot=True)
    d.shape("light", "M78 88 C100 96 132 82 160 92 C156 104 112 110 82 100Z", shadow=False)
    d.shape("pop", "M84 92 C104 98 132 88 154 96 C150 102 112 106 86 98Z", shadow=False)
    d.stroke("light", "M92 96 Q112 98 124 94 M128 92 Q140 94 148 94", 1.4, line=False)
    d.shape("dark", "M44 46 L58 56 L52 66 L38 60Z")
    d.stroke("hero2", "M88 120 Q110 132 140 126", 2, line=False)
    # knife resting in front
    d.shape("sky2", "M60 150 L130 142 L134 146 C110 152 86 154 62 156Z", shadow=False)
    d.shape("dark", rrect(34, 150, 28, 7, 3), shadow=False, extra='transform="rotate(-6 48 153)"')


# ================================================================ PASTA MAKING
def pasta_machine(d: Drawing):
    d.disc("glow", 100, 80, 58, line=False)
    table(d, 150, "far", "mid")
    # dough going in at the top
    d.shape("hero", "M76 46 Q86 40 96 46 T116 46 L114 86 H78Z", spot=True)
    # body with rollers
    d.limb("dark", "M132 104 H150 L158 74", 5)
    d.shape("pop", rrect(152, 58, 12, 18, 5))
    d.shape("hero2", rrect(60, 84, 72, 66, 8))
    d.shape("mark", rrect(60, 84, 72, 10, 4), shadow=False, line=False)
    d.shape("dark", rrect(68, 84, 56, 5, 2), shadow=False)
    d.shape("light", rrect(66, 98, 8, 44, 3), shadow=False, line=False)
    d.stroke("mark", "M80 102 V140 M112 102 V140", 1.4, line=False)
    d.shape("mark", circle(58, 112, 9))
    d.marks("light", circle(58, 112, 3))
    # tagliatelle coming out of the cutter, hanging over the table edge
    for k, x in enumerate(range(70, 124, 7)):
        w = 2 if k % 2 else -2
        d.limb("hero", f"M{x} 136 V150 Q{x+w} 160 {x} 168 T{x + w*0.5} 184", 4.2, shadow=k == 0)
    d.marks("light", circle(36, 140, 1.8) + circle(44, 136, 1.4) + circle(160, 132, 1.6) + circle(150, 140, 1.2))


def pasta_well(d: Drawing):
    d.band("ground", "M-30 -30 L230 -30", line=False)
    d.stroke("deep", "M-30 40 Q100 36 230 42 M-30 170 Q100 164 230 172", 1.6, line=False)
    # rolling pin
    d.limb("mark", "M28 158 L168 176", 7)
    d.limb("mark", "M28 158 L168 176", 2, shadow=False)
    d.shape("hero", rrect(44, 156, 108, 18, 9), extra='transform="rotate(7.3 98 165)"', spot=True)
    # flour well
    d.shape("light", "M44 92 C40 56 80 40 104 44 C138 46 162 66 156 96 C152 124 126 142 98 140 C66 138 46 120 44 92Z")
    d.shape("sky2", ellipse(100, 92, 30, 24), shadow=False)
    for x, y in [(90, 88), (110, 96), (98, 104)]:
        d.shape("light", circle(x, y, 9), shadow=False, line=False)
        d.shape("hero2", circle(x, y, 6), shadow=False)
    # eggshells and fork
    for x, y in [(160, 128), (172, 110)]:
        d.shape("light", f"M{x-10} {y} A10 10 0 0 0 {x+10} {y} L{x+6} {y-3} L{x+2} {y+1} L{x-2} {y-3} L{x-6} {y+1}Z")
    d.marks("light", circle(36, 120, 2) + circle(28, 108, 1.6) + circle(150, 52, 1.8) + circle(166, 66, 1.4))


def ravioli(d: Drawing, x, y, s=26):
    h = s / 2
    zig = ""
    n = 6
    pts = []
    for side in range(4):
        for i in range(n):
            t = i / n
            if side == 0:
                px, py = x - h + s * t, y - h
            elif side == 1:
                px, py = x + h, y - h + s * t
            elif side == 2:
                px, py = x + h - s * t, y + h
            else:
                px, py = x - h, y + h - s * t
            pts.append((px, py))
    zig = "M" + " L".join(f"{px:.1f} {py:.1f}" for px, py in pts) + "Z"
    d.shape("hero", zig)
    d.shape("hero2", circle(x, y, s * 0.3), shadow=False)
    d.stroke("light", f"M{x - s*0.2:.1f} {y - s*0.14:.1f} q{s*0.1:.1f} {-s*0.1:.1f} {s*0.22:.1f} {-s*0.06:.1f}", 1.6, line=False)


def pasta_ravioli(d: Drawing):
    d.band("ground", "M-30 -30 L230 -30", line=False)
    d.stroke("deep", "M-30 40 Q100 36 230 42 M-30 170 Q100 164 230 172", 1.6, line=False)
    def tray():
        d.shape("mark", rrect(46, 46, 108, 108, 4), line=False)
        for j in range(3):
            for i in range(3):
                ravioli(d, 64 + i * 36, 64 + j * 36, 30)
    group(d, "rotate(-8 100 100)", tray)
    # fluted cutter
    d.limb("dark", "M150 150 L176 176", 7)
    teeth = " ".join(f"L{150 + 13*math.cos(a*math.pi/8):.1f} {150 + 13*math.sin(a*math.pi/8):.1f} L{150 + 10.5*math.cos((a+.5)*math.pi/8):.1f} {150 + 10.5*math.sin((a+.5)*math.pi/8):.1f}" for a in range(16))
    d.shape("sky2", "M163 150 " + teeth + "Z", spot=True)
    d.marks("dark", circle(150, 150, 2.6))
    # basil
    d.shape("near", leaf(30, 90, 26, 14, -20))
    d.shape("near", leaf(30, 90, 22, 12, 30))
    d.marks("light", circle(170, 60, 1.8) + circle(160, 48, 1.4) + circle(36, 140, 1.8))


# ================================================================ DIM SUM
def steamer_tier(d: Drawing, x, y, w, h, spot=False):
    d.shape("hero", rrect(x, y, w, h, 3), spot=spot)
    d.shape("hero2", rrect(x - 2, y, w + 4, 5, 2), shadow=False)
    d.stroke("mark", f"M{x+3} {y + h*0.62:.1f} H{x + w - 3}", 1.6, line=False)
    for k in range(1, 6):
        xx = x + w * k / 6
        d.stroke("mark", f"M{xx:.1f} {y+7} V{y + h - 3}", 1, line=False)


def dimsum_stack(d: Drawing):
    d.disc("glow", 100, 80, 58, line=False)
    table(d, 152, "far", "mid")
    steam(d, [62, 138], 100, 22)
    steam(d, [84, 116], 38, 22)
    for i, y in enumerate([126, 100, 74]):
        steamer_tier(d, 46, y, 108, 26, spot=i == 1)
    # woven lid
    d.shape("hero", "M44 76 C46 50 154 50 156 76Z")
    d.stroke("mark", "M58 70 Q100 58 142 70 M70 62 Q100 54 130 62", 1.4, line=False)
    d.stroke("mark", "M44 76 H156", 2)
    d.shape("hero2", rrect(92, 50, 16, 6, 3))
    # soy dish and chopsticks
    d.shape("light", ellipse(34, 156, 16, 5))
    d.shape("dark", ellipse(34, 155, 11, 3), shadow=False)
    chopsticks(d, 128, 158, 182, 140, 6, "pop", 3.4)


def bao(d: Drawing, x, y, s=1.0, split=False):
    def f():
        d.shape("light", "M-29 0 C-36 -46 36 -46 29 0 Q0 7 -29 0Z")
        if split:
            d.shape("pop", "M-14 -30 Q0 -40 15 -29 L9 -19 Q0 -13 -8 -19Z", shadow=False, spot=True)
            d.stroke("mark", "M-14 -30 Q0 -40 15 -29", 1.4, line=False)
        else:
            d.stroke("mark", "M0 -32 l-9 7 M0 -32 l-3 9 M0 -32 l3 9 M0 -32 l9 7", 1.6)
            d.marks("mark", circle(0, -32, 2.2))
        d.stroke("sky2", "M-18 -2 Q0 3 18 -2", 1.4, line=False)
    group(d, f"translate({x} {y}) scale({s})", f)


def dimsum_bao(d: Drawing):
    d.disc("glow", 100, 86, 58, line=False)
    table(d, 150, "far", "mid")
    # bamboo base and paper liner
    d.shape("hero", "M24 132 H176 L170 152 H30Z")
    d.stroke("mark", "M28 140 H172", 1.4, line=False)
    d.shape("hero2", ellipse(100, 132, 76, 7), shadow=False)
    steam(d, [68, 132], 70, 22)
    bao(d, 66, 124, 1.05)
    bao(d, 134, 124, 1.05)
    bao(d, 100, 144, 1.15, split=True)


def dimsum_cart(d: Drawing):
    d.disc("glow", 100, 84, 60, line=False)
    d.band("ground", "M-30 160 L230 160")
    # hanging lantern
    d.stroke("dark", "M40 10 V30", 1.4)
    d.shape("pop", ellipse(40, 42, 11, 13), spot=True)
    d.shape("dark", rrect(34, 27, 12, 4, 1), shadow=False)
    d.shape("dark", rrect(34, 53, 12, 4, 1), shadow=False)
    d.stroke("glow2", "M40 57 V66", 2)
    steam(d, [70, 92], 74, 20)
    steam(d, [130], 92, 18)
    # stacked steamers on the trolley
    steamer_tier(d, 54, 102, 54, 16)
    steamer_tier(d, 54, 86, 54, 16)
    d.shape("hero", "M52 88 C54 74 108 74 110 88Z")
    steamer_tier(d, 112, 102, 46, 16)
    d.shape("hero2", ellipse(135, 102, 23, 4.5), shadow=False)
    for x in [124, 135, 146]:
        d.shape("light", f"M{x-6} 102 C{x-6} 94 {x+6} 94 {x+6} 102Z", shadow=False)
        d.marks("pop", circle(x, 96.5, 1.6))
    # trolley
    d.limb("dark", "M160 120 L176 98", 5)
    d.shape("sky2", rrect(44, 116, 120, 8, 2))
    d.shape("deep", rrect(48, 124, 112, 22, 3), spot=True)
    d.stroke("glow2", "M54 135 H154", 2, line=False)
    d.shape("sky2", rrect(44, 144, 120, 5, 2))
    for x in [60, 148]:
        d.shape("dark", circle(x, 154, 7))
        d.marks("light", circle(x, 154, 2.2))


# ================================================================ PUB CRAWL
def pub_front(d: Drawing):
    d.band("hero", "M-30 -30 L230 -30", line=False)
    for y in range(14, 92, 9):
        off = 0 if (y // 9) % 2 else 9
        d.stroke("mark", " ".join(f"M{x} {y} h14" for x in range(-10 + off, 220, 18)), 1, line=False)
    for x in [34, 78, 122]:
        d.shape("light", rrect(x, 30, 28, 40, 2))
        d.shape("sky2", rrect(x + 3, 33, 22, 16, 1), shadow=False)
        d.shape("sky2", rrect(x + 3, 52, 22, 15, 1), shadow=False)
    # green pub frontage
    d.shape("deep", "M20 210 V88 H180 V210Z")
    d.shape("dark", rrect(26, 92, 148, 14, 2))
    d.stroke("hero2", rrect(29, 95, 142, 8, 1), 1.6, line=False)
    for x in [32, 124]:
        d.shape("glow2", rrect(x, 112, 44, 40, 3), spot=True)
        d.stroke("deep", f"M{x+22} 112 V152 M{x} 128 H{x+44}", 2.6)
    d.shape("dark", rrect(86, 112, 28, 54, 2))
    d.shape("glow2", rrect(90, 116, 20, 14, 2), shadow=False)
    d.marks("hero2", circle(108, 142, 1.8))
    d.stroke("hero2", "M24 108 H176", 2, line=False)
    # hanging baskets
    for x in [28]:
        d.shape("near", "M" + f"{x-11} 84 a11 9 0 0 0 22 0Z")
        d.marks("pop", circle(x - 6, 84, 2.6) + circle(x + 1, 88, 2.6) + circle(x + 7, 83, 2.4) + circle(x - 1, 81, 2.2))
    # hanging sign on a bracket
    d.stroke("dark", "M150 52 H180 M154 52 V58 M170 52 V58", 2.6)
    d.shape("dark", rrect(148, 58, 26, 32, 3))
    d.shape("deep", rrect(151, 61, 20, 26, 2), shadow=False)
    d.stroke("hero2", rrect(153, 63, 16, 22, 1.5), 1.2, line=False)
    d.shape("glow2", "M156 66 H166 L164.5 82 H157.5Z", shadow=False)
    d.shape("light", "M156 66 H166 L165.6 70 H156.4Z", shadow=False)
    d.band("ground", "M-30 168 L230 168")


def pint(d: Drawing, x, base, beer="hero2", h=48, foam=6, spot=False):
    d.shape("light", f"M{x-16} {base-h} H{x+16} L{x+12} {base} H{x-12}Z")
    d.shape(beer, f"M{x-14.5} {base-h+foam+1} H{x+14.5} L{x+11} {base-2} H{x-11}Z", shadow=False, spot=spot)
    d.stroke("light", f"M{x-8} {base-h+12} L{x-6} {base-6}", 2.2, line=False)


def pub_taps(d: Drawing):
    d.band("deep", "M-30 -30 L230 -30", line=False)
    d.disc("glow", 100, 70, 46, line=False)
    # tap handles on a chrome rail
    for x, role in [(56, "pop"), (100, "hero"), (144, "light")]:
        d.shape(role, f"M{x-6} 82 L{x-8} 44 C{x-8} 36 {x+8} 36 {x+8} 44 L{x+6} 82Z", spot=role == "pop")
        d.shape("sky2", rrect(x - 5, 80, 10, 6, 1), shadow=False)
        d.stroke("sky2", f"M{x} 96 V104 Q{x} 108 {x-4} 108", 4, shadow=True)
    d.shape("sky2", rrect(34, 86, 132, 12, 4))
    d.stroke("light", "M40 89 H160", 1.4, line=False)
    # pint filling under the middle spout
    d.stroke("hero2", "M96 108 V118", 3)
    pint(d, 98, 160, h=44)
    d.shape("light", "M83 118 C82 112 90 110 94 113 C98 109 106 110 108 114 C114 113 115 119 113 120 H83Z", shadow=False)
    d.band("ground", "M-30 160 L230 160")
    d.band("near", "M-30 172 L230 172", line=False)
    d.shape("light", ellipse(150, 160, 14, 3), shadow=False, line=False)


def wedge(cx, cy, r0, r1, a0, a1):
    p = lambda r, a: (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = p(r0, a0), p(r1, a0), p(r1, a1), p(r0, a1)
    return f"M{x0:.1f} {y0:.1f} L{x1:.1f} {y1:.1f} A{r1} {r1} 0 0 1 {x2:.1f} {y2:.1f} L{x3:.1f} {y3:.1f} A{r0} {r0} 0 0 0 {x0:.1f} {y0:.1f}Z"


def pub_darts(d: Drawing):
    d.band("deep", "M-30 -30 L230 -30", line=False)
    for x in [-4, 40, 160, 204]:
        d.stroke("dark", f"M{x} -10 V210", 2, line=False)
    cx, cy = 96, 104
    d.shape("dark", circle(cx, cy, 66))
    for i in range(20):
        a0, a1 = -99 + i * 18, -81 + i * 18
        light = i % 2 == 0
        d.shape("light" if light else "mark", wedge(cx, cy, 6, 52, a0, a1), shadow=False, line=False)
        d.shape("pop" if light else "near", wedge(cx, cy, 48, 54, a0, a1), shadow=False, line=False)
        d.shape("pop" if light else "near", wedge(cx, cy, 28, 32, a0, a1), shadow=False, line=False)
    d.shape("near", circle(cx, cy, 6), shadow=False, line=False)
    d.shape("pop", circle(cx, cy, 3), shadow=False, spot=True)
    line_only(d, circle(cx, cy, 54) + circle(cx, cy, 48) + circle(cx, cy, 32) + circle(cx, cy, 28) + circle(cx, cy, 6), 1.6)
    line_only(d, " ".join(f"M{cx + 6*math.cos(math.radians(-99 + i*18)):.1f} {cy + 6*math.sin(math.radians(-99 + i*18)):.1f} "
                          f"L{cx + 54*math.cos(math.radians(-99 + i*18)):.1f} {cy + 54*math.sin(math.radians(-99 + i*18)):.1f}" for i in range(20)), 1.2)
    for x, y, ang in [(cx + 2, cy - 2, -40), (cx + 22, cy - 30, -55), (cx - 18, cy + 18, -30)]:
        def dart():
            d.stroke("dark", "M0 0 L10 0", 1.6)
            d.limb("sky2", "M10 0 L28 0", 5)
            d.stroke("dark", "M28 0 L42 0", 2)
            d.shape("hero", "M38 0 L52 -9 L56 -9 L50 0 L56 9 L52 9Z", spot=True)
        group(d, f"translate({x} {y}) rotate({ang})", dart)


# ================================================================ BEER GARDEN
def stein(d: Drawing):
    d.limb("light", "M24 -22 C42 -22 42 18 24 18", 7)
    d.shape("light", rrect(-26, -38, 52, 78, 7))
    d.shape("hero2", rrect(-22, -28, 44, 62, 4), shadow=False, spot=True)
    for x, y in [(-12, -14), (0, -14), (12, -14), (-12, 0), (0, 0), (12, 0), (-12, 14), (0, 14), (12, 14)]:
        d.shape("hero", ellipse(x, y, 4.2, 5.4), shadow=False, line=False)
    d.shape("light", "M-30 -34 C-34 -46 -20 -52 -12 -46 C-6 -54 8 -54 12 -46 C20 -52 34 -46 30 -34 C30 -26 24 -26 22 -30 Q0 -26 -22 -30 C-26 -22 -30 -26 -30 -34Z", shadow=False)
    d.shape("light", rrect(-28, 34, 56, 8, 3), shadow=False)


def bavarian_bunting(d: Drawing, y=24):
    d.stroke("dark", f"M-30 {y} Q100 {y+26} 230 {y}", 1.4)
    for i, x in enumerate(range(18, 200, 18)):
        t = (x + 30) / 260
        yy = (1 - t) ** 2 * y + 2 * (1 - t) * t * (y + 26) + t * t * y
        d.shape("pop" if i % 2 == 0 else "light", f"M{x-6} {yy:.1f} H{x+6} L{x} {yy+12:.1f}Z", shadow=False, spot=i % 2 == 0)


def bgarden_steins(d: Drawing):
    d.disc("glow", 100, 100, 62, line=False)
    bavarian_bunting(d)
    table(d, 160, "far", "mid")
    group(d, "translate(66 118) rotate(-12)", lambda: stein(d))
    group(d, "translate(134 118) scale(-1 1) rotate(-12)", lambda: stein(d))
    for x, y, r in [(100, 64, 3.4), (92, 56, 2.4), (110, 54, 2.8), (100, 46, 2)]:
        d.shape("light", circle(x, y, r), shadow=False)


def bgarden_tables(d: Drawing):
    d.disc("glow", 60, 70, 20)
    # maypole with blue and white twist
    d.limb("pop", "M42 30 V150", 5, spot=True)
    d.stroke("light", " ".join(f"M39.5 {y} L44.5 {y-6}" for y in range(40, 150, 10)), 2.2, line=False)
    d.shape("near", ellipse(42, 30, 10, 4))
    d.band("far", hills(132, 6))
    # chestnut tree
    d.limb("dark", "M164 160 V90", 8)
    d.shape("near", "M96 70 C88 46 116 22 146 30 C166 12 206 26 204 58 C214 76 196 96 172 90 C156 102 126 96 118 86 C100 92 88 82 96 70Z")
    d.shape("deep", "M120 68 C130 58 146 62 150 70 C140 76 128 76 120 68Z", shadow=False, line=False)
    # string lights from tree to pole
    d.stroke("dark", "M44 66 Q90 96 130 84", 1.2)
    for t in [0.15, 0.35, 0.55, 0.75, 0.92]:
        x = (1 - t) ** 2 * 44 + 2 * (1 - t) * t * 90 + t * t * 130
        y = (1 - t) ** 2 * 66 + 2 * (1 - t) * t * 96 + t * t * 84
        d.marks("glow2", circle(x, y + 3, 3))
    d.band("ground", "M-30 150 L230 150")
    # long table with steins
    for x in [72, 100, 128]:
        d.shape("light", rrect(x - 7, 106, 14, 20, 2))
        d.shape("hero2", rrect(x - 5.5, 110, 11, 14, 1.5), shadow=False)
        d.shape("light", ellipse(x, 106, 8, 3.5), shadow=False)
        d.stroke("light", f"M{x+7} 110 q6 0 6 6 q0 6 -6 6", 2.2)
    d.shape("hero", rrect(36, 124, 128, 8, 2), spot=False)
    d.stroke("hero", "M48 132 L64 158 M64 132 L48 158 M136 132 L152 158 M152 132 L136 158", 4)
    d.shape("hero", rrect(30, 150, 140, 6, 2))
    d.stroke("hero", "M42 156 V170 M158 156 V170", 4)


PRETZEL = [((40, 84), (70, 104), (104, 128), (132, 148)), ((132, 148), (180, 126), (178, 44), (100, 44)),
           ((100, 44), (22, 44), (20, 126), (68, 148)), ((68, 148), (96, 128), (130, 104), (160, 84))]


def bgarden_pretzel(d: Drawing):
    d.band("light", "M-30 -30 L230 -30", line=False)
    for j in range(-1, 9):
        for i in range(-1, 9):
            if (i + j) % 2 == 0:
                x, y = i * 24 + (12 if j % 2 else 0), j * 24
                d.shape("pop", f"M{x} {y-12} L{x+12} {y} L{x} {y+12} L{x-12} {y}Z", shadow=False, line=False)
    d.disc("glow", 100, 100, 70, line=False)
    path = "M40 84 " + " ".join(f"C{a[0]} {a[1]} {b[0]} {b[1]} {c[0]} {c[1]}" for _, a, b, c in PRETZEL)
    d.raw('<g transform="translate(100 98) scale(.88) translate(-100 -98)">', '<g transform="translate(100 98) scale(.88) translate(-100 -98)">')
    d.limb("hero", path, 15, spot=True)
    d.stroke("hero2", "M38 80 C34 60 60 48 100 48 C140 48 166 60 162 80", 3, line=False)
    for p0, p1, p2, p3 in PRETZEL:
        for t in (0.25, 0.6):
            x = (1-t)**3*p0[0] + 3*(1-t)**2*t*p1[0] + 3*(1-t)*t*t*p2[0] + t**3*p3[0]
            y = (1-t)**3*p0[1] + 3*(1-t)**2*t*p1[1] + 3*(1-t)*t*t*p2[1] + t**3*p3[1]
            d.marks("light", rrect(x - 1.8, y - 3.4, 3.6, 3.6, 0.6))
    d.raw("</g>", "</g>")


def ftruck_van(d: Drawing):
    d.disc("glow", 150, 46, 15)
    # string lights
    d.stroke("dark", "M-30 30 Q60 52 110 36 T230 40", 1.2)
    for x, y in [(10, 40), (36, 45), (62, 46), (88, 42), (130, 34), (156, 37), (182, 42)]:
        d.marks("glow2", circle(x, y + 4, 2.8))
    d.band("far", "M-30 140 Q100 132 230 140")
    d.band("ground", "M-30 156 L230 156")
    # rounded corrugated van
    d.shape("hero", "M28 146 V84 C28 70 38 62 54 62 H136 C154 62 164 74 170 92 L176 118 V146Z", spot=True)
    for x in range(36, 170, 7):
        d.stroke("mark", f"M{x} 116 V142", 1.3, line=False)
    d.shape("light", "M146 72 H158 C162 78 166 88 168 98 H146Z", shadow=False)
    d.shape("dark", rrect(48, 80, 70, 30, 2))
    d.shape("light", rrect(44, 108, 78, 6, 2))
    d.shape("pop", "M44 80 L122 80 L128 64 L50 64Z")
    for i in range(4):
        x = 50 + i * 20
        d.shape("light", f"M{x+10} 64 H{x+20} L{x+16} 80 H{x+6}Z", shadow=False, line=False)
    d.stroke("dark", "M48 80 L44 106 M118 80 L122 106", 1.4, line=False)
    d.shape("hero2", circle(70, 104, 4), shadow=False)
    d.shape("light", rrect(88, 98, 10, 10, 2), shadow=False)
    d.shape("glow2", circle(172, 128, 4.5), shadow=False)
    for x in [60, 146]:
        d.shape("dark", circle(x, 148, 13))
        d.shape("light", circle(x, 148, 5), shadow=False)


def ftruck_burger(d: Drawing):
    d.disc("glow", 100, 86, 60, line=False)
    table(d, 152, "far", "mid")
    # fries carton
    for x, rot in [(134, -8), (142, -2), (150, 4), (158, 10), (146, 2), (154, 6)]:
        d.shape("hero", rrect(x - 3.5, 62, 7, 48, 2), extra=f'transform="rotate({rot} {x} 110)"')
    d.shape("pop", "M124 96 H172 L164 152 H132Z", spot=True)
    d.shape("pop", "M124 96 Q148 108 172 96 L170 106 Q148 116 126 106Z", shadow=False)
    # burger
    d.shape("hero2", "M30 136 Q30 152 46 152 H114 Q130 152 130 136Z")
    d.shape("deep", rrect(26, 120, 108, 16, 8))
    d.shape("hero", "M30 120 L130 120 L124 128 L114 136 L108 128 L96 130 L86 128 L72 138 L64 128 L48 128 L40 134 L34 126Z", shadow=False, spot=False)
    d.shape("pop", rrect(32, 110, 96, 9, 4), shadow=False)
    d.shape("near", "M26 112 Q34 102 42 110 Q50 100 58 110 Q66 100 74 110 Q82 100 90 110 Q98 100 106 110 Q114 100 122 110 Q130 100 136 112 Q80 118 26 112Z", shadow=False)
    d.shape("hero2", "M28 104 C28 66 132 66 132 104Z", spot=True)
    for x, y, r in [(56, 84, -20), (74, 78, 0), (92, 80, 20), (110, 88, 30), (66, 94, -10), (98, 92, 10), (82, 88, 0)]:
        d.shape("light", ellipse(x, y, 1.7, 3.2), shadow=False, line=False, extra=f'transform="rotate({r} {x} {y})"')


def ftruck_window(d: Drawing):
    d.band("hero", "M-30 -30 L230 -30", line=False)
    # awning
    d.shape("pop", "M22 72 L178 72 L188 44 L12 44Z", spot=True)
    for i in range(5):
        x = 22 + i * 31.2
        d.shape("light", f"M{x+15.6:.1f} 72 H{x+31.2:.1f} L{100 + (x + 31.2 - 100) * 1.13:.1f} 44 H{100 + (x + 15.6 - 100) * 1.13:.1f}Z", shadow=False, line=False)
    d.stroke("dark", "M30 72 L22 112 M170 72 L178 112", 2)
    # serving hatch
    d.shape("dark", rrect(30, 76, 140, 54, 3))
    d.stroke("light", "M60 76 V86 M140 76 V86", 1.2)
    d.shape("glow2", "M54 86 H66 L64 92 H56Z", shadow=False)
    d.shape("glow2", "M134 86 H146 L144 92 H136Z", shadow=False)
    d.shape("sky2", "M100 128 C100 106 108 98 118 98 C128 98 136 106 136 128Z", shadow=False, line=False)
    d.shape("sky2", ellipse(118, 98, 8, 3), shadow=False, line=False)
    # counter with orders
    d.shape("sky2", rrect(22, 126, 156, 9, 3))
    d.shape("ground", "M44 126 V100 L48 96 H66 L70 100 V126Z")
    d.stroke("mark", "M44 100 H70", 1.4)
    d.shape("light", "M82 126 L80 104 H96 L94 126Z")
    d.shape("pop", rrect(79, 101, 18, 5, 2), shadow=False)
    d.stroke("dark", "M90 101 L94 92", 1.6)
    d.shape("hero2", "M142 126 C142 114 166 114 166 126Z", spot=False)
    d.marks("hero2", circle(154, 114, 2))
    # lower panel
    d.stroke("mark", "M-30 150 H230", 2, line=False)
    d.shape("dark", rrect(40, 144, 54, 34, 3))
    d.stroke("light", "M47 153 h22 M47 161 h32 M47 169 h26", 1.6)
    d.stroke("mark", "M118 156 H160 M118 164 H160 M118 172 H160", 2.4)


# ================================================================ catalogue
WOOD = "#C68B59"
GRAPE = "#6B3F7A"
COPPER = {"hero": "#C8743E", "hero2": "#E8A877", "mark": "#9A5328"}

CONCEPTS = [
    # vineyard tour
    Concept("vtour-hills", "vineyard-tour", "Tuscan vine rows", vtour_hills,
            overrides={"mid": "#A3C46F", "deep": "#5C8A3F", "near": "#4E7D3A", "pop": "#C8643B", "dark": "#2F4F33"},
            checks=[("far", "mid"), ("dark", "far"), ("light", "far"), ("glow", "sky")],
            fixes={"far": ["near", "#D9C38C", "light"], "dark": ["deep", "mark"], "glow": ["glow2", "#F6A96B", "pop"]}),
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
            overrides={"pop": "#C8302E", "mark": "#2E4A7D", "hero": "#D9A520", "ground": "#C9A46E", "light": "#FBF7EE"},
            checks=[("light", "glow"), ("light", "far"), ("pop", "glow"), ("glow", "deep")],
            fixes={"glow": ["mid", "near", "deep", "#7FB7BE"], "far": ["mid", "near", "deep"], "deep": ["dark", "mark"]}),
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
            fixes={"glow": ["sky2", "far", "mid", "#F1E6CF", "#7FB7BE", "deep"]}),
    Concept("choc-pod", "chocolate-tasting", "Cacao pod", choc_pod,
            overrides={"hero": "#E0A33A", "pop": "#B8752A", "hero2": "#A0674A", "mark": "#6B3E26", "near": "#4F8A3C", "mid": "#7FB069", "light": "#FFF6E8", "dark": "#5A3A22"},
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


PICNIC = {"pop": "#D7263D", "mid": "#8CC084", "near": "#5E9C6A"}
WICKER = {"hero": "#C9A46E", "mark": "#9A7444"}
FRUIT = {"hero": "#F28C28", "pop": "#D7263D", "hero2": "#F6D743"}
BOARD = {"ground": "#C68B59", "deep": "#A8743F"}
BAMBOO = {"hero": "#D9B26F", "hero2": "#B88A44", "mark": "#9A7038"}
BEER = {"hero2": "#F2B33D", "hero": "#F7CD6B"}

CONCEPTS += [
    # picnic
    Concept("picnic-blanket", "picnic", "Gingham spread", picnic_blanket,
            overrides={**PICNIC, "hero": "#F2545B", "hero2": "#E8C07A", "ground": "#4AA3DF", "glow2": "#F6D365", "light": "#FFFDF7", "sky2": "#D9DCE3"},
            checks=[("light", "mid"), ("near", "light")]),
    Concept("picnic-basket", "picnic", "Picnic hamper", picnic_basket,
            overrides={**PICNIC, **WICKER, "hero2": "#E0A458", "deep": "#2F5D3A", "ground": "#7A4A2A", "light": "#FFFDF7"},
            checks=[("hero", "glow"), ("hero2", "glow"), ("deep", "glow"), ("hero", "sky")],
            fixes={"glow": ["light", "sky2", "far", "#F1E6CF"]}),
    Concept("picnic-tree", "picnic", "Under the tree", picnic_tree,
            overrides={**PICNIC, **WICKER, "near": "#4F8A3C", "deep": "#3A6B2E", "light": "#FFFDF7"},
            checks=[("near", "sky"), ("mid", "far"), ("light", "mid"), ("hero2", "sky"), ("near", "far")],
            fixes={"far": ["#D9C38C", "light", "deep"], "hero2": ["pop", "hero", "deep"]}),
    # fruit market
    Concept("fruit-stall", "fruit-market", "Market stall", fruit_stall,
            overrides={**FRUIT, "ground": "#C68B59", "mark": "#8A5A3B", "near": "#8A5A3B"},
            checks=[("mid", "light"), ("mid", "sky"), ("ground", "far"), ("hero", "far"), ("pop", "far")],
            fixes={"mid": ["near", "deep", "pop"], "far": ["mid", "deep", "sky2"]}),
    Concept("fruit-tropical", "fruit-market", "Tropical fruit", fruit_tropical,
            overrides={"ground": "#E8A93A", "mark": "#A86E1E", "near": "#4F8A3C", "hero": "#F2545B", "hero2": "#F6D743", "pop": "#F4A23A"},
            checks=[("ground", "glow"), ("hero2", "glow"), ("near", "glow"), ("pop", "far")],
            fixes={"glow": ["light", "sky2", "#7FB7BE", "deep"], "far": ["mid", "deep"]}),
    Concept("fruit-boat", "fruit-market", "Floating market", fruit_boat,
            overrides={**FRUIT, "ground": "#A0673F", "mark": "#3E5F8A", "glow2": "#8DBF4A", "light": "#F3E6C4", "mid": "#7FB5A6", "near": "#5A9488"},
            checks=[("ground", "mid"), ("ground", "near"), ("light", "far"), ("far", "sky")],
            fixes={"mid": ["far", "light"], "near": ["deep", "far"]}),
    # tapas crawl
    Concept("tapas-plates", "tapas-crawl", "Cazuelas", tapas_plates,
            overrides={**BOARD, "hero": "#C1663F", "mark": "#9C4A2C", "hero2": "#F2C14E", "pop": "#D7263D", "near": "#7A9A3A", "sky2": "#E3D5C0", "glow2": "#EDB94E", "light": "#FFF6E6"},
            checks=[("hero", "ground")], fixes={"ground": ["#E3C08F"]}),
    Concept("tapas-pintxos", "tapas-crawl", "Pintxos bar", tapas_pintxos,
            overrides={"hero2": "#D9A066", "light": "#FFF6E6", "hero": "#F2C14E", "mark": "#C99A2E", "near": "#6B7F2A", "pop": "#C8414B", "dark": "#4A4E5A", "ground": "#E8D3A8"},
            checks=[("hero2", "glow"), ("light", "glow"), ("pop", "glow"), ("hero", "glow")],
            fixes={"glow": ["#7FB7BE", "mid", "deep"]}),
    Concept("tapas-jamon", "tapas-crawl", "Jamón on the stand", tapas_jamon,
            overrides={"hero": "#8A4A2B", "hero2": "#A8603A", "pop": "#B5303A", "light": "#FFF4E6", "dark": "#3B2A20", "ground": "#C68B59", "sky2": "#C9CED6"},
            checks=[("hero", "glow"), ("dark", "glow"), ("ground", "far")],
            fixes={"glow": ["light", "sky2", "#F1E6CF", "far"], "far": ["mid", "deep"]}),
    # pasta making
    Concept("pasta-machine", "pasta-making", "Pasta machine", pasta_machine,
            overrides={"hero": "#F6D58A", "hero2": "#C9D1D8", "mark": "#8A949E", "pop": "#B5302A"},
            checks=[("hero2", "glow"), ("hero", "far")],
            fixes={"glow": ["mid", "near", "deep"], "far": ["mid", "deep", "near"]}),
    Concept("pasta-well", "pasta-making", "Flour & eggs", pasta_well,
            overrides={**BOARD, "hero": "#D9A066", "mark": "#B07A45", "light": "#FBF5E8", "sky2": "#EADFC6", "hero2": "#F6B82A"},
            checks=[("light", "ground")]),
    Concept("pasta-ravioli", "pasta-making", "Ravioli tray", pasta_ravioli,
            overrides={**BOARD, "mark": "#F3E3B4", "hero": "#F6D58A", "hero2": "#EBC46A", "sky2": "#C9CED6", "near": "#3F8A3F", "light": "#FFFBF0"},
            checks=[("mark", "ground")]),
    # dim sum
    Concept("dimsum-stack", "dim-sum", "Steamer tower", dimsum_stack,
            overrides={**BAMBOO, "pop": "#B5302A"},
            checks=[("hero", "glow"), ("hero", "far"), ("hero", "sky")],
            fixes={"glow": ["mid", "near", "deep", "#7FB7BE"], "far": ["mid", "deep"]}),
    Concept("dimsum-bao", "dim-sum", "Char siu bao", dimsum_bao,
            overrides={**BAMBOO, "hero2": "#EFE3C8", "light": "#FFFBF2", "pop": "#B5302A", "sky2": "#E6DCC8"},
            checks=[("light", "glow"), ("hero", "glow"), ("hero", "far")],
            fixes={"glow": ["mid", "near", "deep", "#7FB7BE"], "far": ["mid", "deep"]}),
    Concept("dimsum-cart", "dim-sum", "Dim sum trolley", dimsum_cart,
            overrides={**BAMBOO, "pop": "#C8302E", "sky2": "#C9D1D8", "light": "#FFFBF2"},
            checks=[("deep", "ground"), ("hero", "glow"), ("sky2", "glow"), ("deep", "glow")],
            fixes={"glow": ["mid", "near", "#7FB7BE"], "ground": ["far", "mid"]}),
    # pub crawl
    Concept("pub-front", "pub-crawl", "Corner pub", pub_front,
            overrides={"hero": "#A84A32", "mark": "#8A3A26", "sky2": "#9FB8C8", "deep": "#1F4D3A", "dark": "#14261E", "hero2": "#D4A84B",
                       "glow2": "#F6D27A", "near": "#4F8A3C", "pop": "#E84A6B", "light": "#F5F0E6"},
            checks=[("deep", "ground"), ("deep", "hero")], fixes={"ground": ["far", "light", "#BFB8AA"]}),
    Concept("pub-taps", "pub-crawl", "Pulling a pint", pub_taps,
            overrides={"deep": "#3B2A20", "sky2": "#C9D1D8", "hero2": "#E39B32", "ground": "#8A5432", "near": "#5A3420"},
            checks=[("glow", "deep"), ("sky2", "glow"), ("hero", "glow"), ("light", "glow"), ("pop", "glow")],
            fixes={"glow": ["mid", "far", "near", "#7FB7BE"], "hero": ["hero2", "near"]}),
    Concept("pub-darts", "pub-crawl", "Darts", pub_darts,
            overrides={"deep": "#8A5A3B", "dark": "#1E1E1E", "light": "#F3E3C0", "mark": "#2A2A2A", "pop": "#D7263D", "near": "#2E8B57", "sky2": "#C9CED6"},
            checks=[("hero", "light"), ("hero", "dark"), ("hero", "deep")], fixes={"hero": ["hero2", "glow", "#4AA3DF"]}),
    # beer garden
    Concept("bgarden-steins", "beer-garden", "Prost!", bgarden_steins,
            overrides={**BEER, "pop": "#3E8ED0", "light": "#FFFDF7"},
            checks=[("light", "glow"), ("hero2", "glow"), ("pop", "sky"), ("light", "far")],
            fixes={"glow": ["#7FB7BE", "mid", "near", "deep"], "far": ["mid", "deep", "near"]}),
    Concept("bgarden-tables", "beer-garden", "Under the chestnuts", bgarden_tables,
            overrides={**BEER, "pop": "#3E8ED0", "near": "#4F8A3C", "deep": "#3A6B2E", "hero": "#A0673F", "glow2": "#FFD98A", "light": "#FFFDF7"},
            checks=[("near", "sky"), ("hero", "ground"), ("pop", "sky"), ("near", "far"), ("light", "ground")],
            fixes={"ground": ["far", "mid", "deep"], "far": ["mid", "light", "#D9C38C"]}),
    Concept("bgarden-pretzel", "beer-garden", "Giant pretzel", bgarden_pretzel,
            overrides={"hero": "#9A5226", "hero2": "#C47A3F", "pop": "#7DB9E8", "light": "#FFFFFF"},
            checks=[("hero", "glow"), ("light", "glow"), ("glow", "pop")], fixes={"glow": ["glow2", "sky2", "#F6E7C1", "far"]}),
    # food truck
    Concept("ftruck-van", "food-truck", "Vintage food van", ftruck_van,
            overrides={"glow2": "#FFD98A"},
            checks=[("hero", "far"), ("hero", "sky"), ("pop", "hero"), ("hero", "ground")],
            fixes={"hero": ["pop", "deep", "near", "hero2"], "far": ["mid", "deep"]}),
    Concept("ftruck-burger", "food-truck", "Burger & fries", ftruck_burger,
            overrides={"hero": "#F6C945", "hero2": "#E0A458", "deep": "#5A3420", "pop": "#D7263D", "near": "#6FAE3A", "light": "#FFF6E0"},
            checks=[("hero2", "glow"), ("pop", "glow"), ("hero", "glow")],
            fixes={"glow": ["#7FB7BE", "mid", "deep"]}),
    Concept("ftruck-window", "food-truck", "Order hatch", ftruck_window,
            overrides={"sky2": "#C9D1D8", "ground": "#C9A46E", "hero2": "#D4A84B", "glow2": "#FFD98A"},
            checks=[("pop", "hero"), ("dark", "hero"), ("sky2", "hero"), ("light", "hero")],
            fixes={"hero": ["mid", "near", "deep", "far"]}),
]
