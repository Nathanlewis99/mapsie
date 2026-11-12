"""Mapsie Originals: city skylines of the Americas.

Every skyline is built the same way, back to front: sun or moon disc, a pale
`far` band of distant towers, a `mid` band of nearer blocks, then the city's
signature buildings (override colours, so they read the same in every palette),
and finally the water with a soft reflection of the front layer.
"""
from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group
import math
import re


# ================================================================ private helpers
def poly(*pts, close=True) -> str:
    s = "M" + " L".join(f"{x:g} {y:g}" for x, y in pts)
    return s + ("Z" if close else "")


def roofline(base, spec, x0=-30) -> str:
    """Top edge of a row of blocks for d.band: spec is [(width, height), ...] left to right."""
    s, x = f"M{x0} {base}", x0
    for w, h in spec:
        s += f" V{base - h:g} H{x + w:g}"
        x += w
    if x < 230:
        s += f" V{base} H230"
    return s


def blocks(base, spec, x0) -> str:
    """A closed row of blocks standing on `base`."""
    s, x = f"M{x0} {base}", x0
    for w, h in spec:
        s += f" V{base - h:g} H{x + w:g}"
        x += w
    return s + f" V{base}Z"


def stepped(x, base, tiers) -> str:
    """A symmetric stepped tower: tiers [(half_width, top_y), ...] from the ground up."""
    left = [(x - tiers[0][0], base)]
    for i, (hw, top) in enumerate(tiers):
        left.append((x - hw, top))
        if i + 1 < len(tiers):
            left.append((x - tiers[i + 1][0], top))
    right = [(2 * x - px, py) for px, py in reversed(left)]
    return poly(*left, *right)


def shade_tiers(d: Drawing, x, base, tiers, role, frac=0.35):
    """Darker right-hand face on a stepped tower (papercut only)."""
    y0 = base
    parts = []
    for hw, top in tiers:
        parts.append(poly((x + hw * frac, y0), (x + hw * frac, top), (x + hw, top), (x + hw, y0)))
        y0 = top + 0.01
    d.shape(role, " ".join(parts), shadow=False, line=False)


def tower(d: Drawing, x, base, tiers, role="b1", shade="b2", spot=False, frac=0.35):
    d.shape(role, stepped(x, base, tiers), spot=spot)
    if shade:
        shade_tiers(d, x, base, tiers, shade, frac)


def ink(d: Drawing, path, w=1.6):
    """Line-style-only detail."""
    if not d.paper:
        d.stroke("dark", path, w)


def mast(d: Drawing, x, top, bottom, role="b1", w=1.6):
    d.stroke(role, f"M{x} {bottom} V{top}", w)


def palm(d: Drawing, x, base, h, lean=0, role="palm", s=1.0):
    tx, ty = x + lean, base - h
    d.limb(role, f"M{x} {base} Q{x + lean * 0.2} {base - h * 0.5} {tx} {ty}", 3.2 * s)
    for ang, ln in [(-160, 20), (-120, 17), (-60, 17), (-20, 20), (20, 15), (160, 15)]:
        a = math.radians(ang)
        ln *= s
        ex, ey = tx + ln * math.cos(a), ty + ln * math.sin(a) + 6 * s
        mx, my = tx + ln * 0.5 * math.cos(a), ty + ln * 0.5 * math.sin(a) - 4 * s
        d.shape(role, f"M{tx:.1f} {ty:.1f} Q{mx:.1f} {my - 3 * s:.1f} {ex:.1f} {ey:.1f} Q{mx:.1f} {my + 3 * s:.1f} {tx:.1f} {ty:.1f}Z", shadow=False)


def birds(d: Drawing, pts, role="dark"):
    s = " ".join(f"M{x} {y} q{3 * k} {-3 * k} {6 * k} 0 q{3 * k} {-3 * k} {6 * k} 0" for x, y, k in pts)
    d.stroke(role, s, 1.6)


_FILL = re.compile(r'(fill|stroke)="#[0-9A-Fa-f]{3,8}"')


def reflect(d: Drawing, fn, W, k=0.42, role="light", opacity=0.3):
    """Soft papercut reflection of whatever `fn(sub)` draws, flipped about the waterline W."""
    if not d.paper:
        return
    sub = Drawing("papercut", d.c)
    fn(sub)
    col = d.c[role]
    body = "".join(sub.parts).replace(' filter="url(#ps)"', "").replace(' filter="url(#psl)"', "")
    body = _FILL.sub(lambda m: f'{m.group(1)}="{col}"', body)
    d.raw(f'<g opacity="{opacity}" transform="translate(0 {W * (1 + k):g}) scale(1 {-k})">{body}</g>')


def water(d: Drawing, W, front=None, ripples=None, deep=True):
    """Calm water from W down, with a reflection of `front` and a few ripple lines."""
    d.band("sea", f"M-30 {W} H230")
    if front:
        reflect(d, front, W)
        # ripple gaps cut the reflection into soft stripes
        d.stroke("sea", " ".join(f"M-30 {W + y} H230" for y in (6, 11, 17, 24, 32)), 1.3, line=False)
    if deep:
        d.band("sea2", waves(W + 30, 2, 26), line=False)
    for x, y, w in (ripples or []):
        d.stroke("light", f"M{x} {y} h{w}", 2)


def base_y(d: Drawing, W):
    """Front buildings stand a little into the water in papercut, exactly on the line in line style."""
    return W + 4 if d.paper else W


# Shared colours for the front layer: slate towers that read on every sky.
CITY = {"b1": "#4E5D78", "b2": "#39445A", "b3": "#7A8AA6", "win": "#FFD98A", "sea": "#3F86B5", "sea2": "#2C6A95"}
CITY_CHECKS = [("b1", "sky"), ("b1", "mid"), ("b1", "glow"), ("b3", "sky"), ("b3", "mid"), ("far", "sky"), ("sea", "mid")]
CITY_FIXES = {"far": ["#B7C6CF", "#A9B9C4", "sky2"], "b1": ["#66779A", "#2F3A4E"], "b3": ["#97A6BF", "b1"],
              "mid": ["near", "far"], "glow": ["glow2", "light", "pop"]}


def city_concept(cid, activity, title, fn, extra=None, checks=(), fixes=None, palettes=None):
    ov = {**CITY, **(extra or {})}
    fx = {**CITY_FIXES, **(fixes or {})}
    kw = {}
    if palettes:
        kw["palettes"] = palettes
    return Concept(cid, activity, title, fn, overrides=ov, checks=list(CITY_CHECKS) + list(checks), fixes=fx, **kw)


# ================================================================ NEW YORK
COPPER = {"cu": "#7DBFA8", "cu2": "#4F8F7B", "stone": "#D8CCB8", "stone2": "#B5A68E", "gold": "#F2B33D"}


def esb(d: Drawing, x, base, h):
    """Empire State Building, h = height to the tip of the mast."""
    f = lambda t: base - t * h
    tiers = [(h * .17, f(.20)), (h * .125, f(.31)), (h * .092, f(.70)), (h * .068, f(.735)), (h * .048, f(.79)), (h * .026, f(.83))]
    tower(d, x, base, tiers, "b1", "b2")
    d.shape("b1", poly((x - h * .016, f(.83)), (x - h * .011, f(.9)), (x + h * .011, f(.9)), (x + h * .016, f(.83))))
    mast(d, x, f(1.0), f(.9), "b1", 1.6)
    d.stroke("b3", " ".join(f"M{x + o:.1f} {f(.68):.1f} V{f(.33):.1f}" for o in (-h * .06, -h * .02)), 1.2, line=False)
    d.marks("win", rrect(x - 2, f(.78), 4, 4, 1))


def chrysler(d: Drawing, x, base, h):
    f = lambda t: base - t * h
    tower(d, x, base, [(h * .2, f(.36)), (h * .15, f(.5)), (h * .12, f(.66))], "b3", "b2")
    c = f(.66)
    hw = h * .12
    arches = ""
    for i, (w, rise) in enumerate([(hw, h * .1), (hw * .76, h * .085), (hw * .52, h * .07), (hw * .3, h * .06)]):
        y0 = c - i * h * .05
        arches += f"M{x - w:.1f} {y0 + 1:.1f} V{y0 - rise * .3:.1f} Q{x - w:.1f} {y0 - rise:.1f} {x} {y0 - rise * 1.1:.1f} Q{x + w:.1f} {y0 - rise:.1f} {x + w:.1f} {y0 - rise * .3:.1f} V{y0 + 1:.1f}Z "
    d.shape("steel", arches, spot=True)
    for i, (w, rise) in enumerate([(hw, h * .1), (hw * .76, h * .085), (hw * .52, h * .07)]):
        y0 = c - i * h * .05 - rise * .45
        d.marks("b2", " ".join(f"M{x + o:.1f} {y0 + 2:.1f} l1.3 -3 l1.3 3Z" for o in (-w * .7, -w * .25 - 1.3, w * .25 - 1.3 + 1.3, w * .55)))
    tip = c - 3 * h * .05 - h * .066
    d.shape("steel", poly((x - 1.4, tip + 1), (x, f(1.0)), (x + 1.4, tip + 1)))


def owtc(d: Drawing, x, base, h):
    """One World Trade Center: tapering faceted glass shaft, square parapet, long spire. h = spire tip."""
    f = lambda t: base - t * h
    roof = f(.77)
    pod = f(.13)
    d.shape("b1", poly((x - 12, base), (x - 12, pod), (x - 6.5, roof), (x + 6.5, roof), (x + 12, pod), (x + 12, base)))
    d.shape("b3", poly((x - 6.5, roof), (x + 6.5, roof), (x, pod)), shadow=False, line=False)
    d.shape("b2", poly((x + 6.5, roof), (x + 12, pod), (x, pod)), shadow=False, line=False)
    ink(d, f"M{x - 6.5} {roof} L{x} {pod} L{x + 6.5} {roof}", 1.4)
    d.shape("b1", rrect(x - 5, roof - 3, 10, 3.5, .8))
    d.shape("b1", poly((x - 1.6, roof - 2), (x - .6, f(1.0)), (x + .6, f(1.0)), (x + 1.6, roof - 2)))


def liberty(d: Drawing, x, base, s):
    """The Statue of Liberty on its pedestal, drawn at reference size then scaled (base = island top)."""
    def draw():
        d.shape("stone2", poly((52, 178), (60, 168), (140, 168), (148, 178)))
        d.shape("stone", poly((80, 168), (83, 140), (117, 140), (120, 168)))
        d.shape("stone", rrect(79, 135, 42, 7, 1.5))
        d.shape("cu", "M85 136 C86 112 86 96 89 84 Q93 78 100 78 Q108 78 112 84 C116 98 117 114 117 136Z")
        d.limb("cu", "M93 84 L86 50", 8)
        d.shape("gold", "M86.5 26 C94 32 96 38 92 44 H81 C77 38 79 32 86.5 26Z", spot=True)
        d.shape("cu", poly((80, 44), (93, 44), (90, 52), (83, 52)), shadow=False)
        d.shape("cu2", "M108 88 L122 86 L124 112 L110 114Z")
        rays = []
        for i in range(7):
            a = math.radians(-162 + i * 24)
            tip = (100 + 19 * math.cos(a), 64 + 19 * math.sin(a))
            b1 = (100 + 7 * math.cos(a - .25), 64 + 7 * math.sin(a - .25))
            b2 = (100 + 7 * math.cos(a + .25), 64 + 7 * math.sin(a + .25))
            rays.append(f"M{b1[0]:.1f} {b1[1]:.1f} L{tip[0]:.1f} {tip[1]:.1f} L{b2[0]:.1f} {b2[1]:.1f}Z")
        d.shape("cu", " ".join(rays))
        d.shape("cu", circle(100, 67, 8))
    group(d, f"translate({x - 100 * s:g} {base - 178 * s:g}) scale({s})", draw)


def new_york(d: Drawing):
    W = 150
    d.disc("glow", 150, 58, 20)
    birds(d, [(30, 52, .9), (44, 46, .7)])
    d.band("far", roofline(W, [(40, 30), (10, 44), (14, 36), (10, 54), (16, 40), (12, 62), (14, 46), (18, 70), (12, 52),
                               (14, 58), (10, 38), (16, 50), (12, 64), (14, 42), (18, 34), (40, 24)]), line=False)
    d.band("mid", roofline(W, [(50, 18), (14, 28), (12, 36), (16, 24), (14, 40), (10, 30), (16, 26), (12, 44), (14, 32),
                               (12, 38), (16, 22), (14, 34), (12, 28), (40, 16)]))

    def front(dd):
        B = base_y(dd, W)
        owtc(dd, 70, B, 130 * 0.98)
        esb(dd, 114, B, 104)
        chrysler(dd, 150, B, 76)
        dd.shape("b1", blocks(B, [(10, 30), (12, 22)], 86))
        dd.shape("b1", blocks(B, [(10, 26), (12, 34)], 128))
    front(d)
    water(d, W, front, [(150, 166, 18), (30, 172, 14), (96, 180, 22)])
    # Liberty on her island in the harbour
    d.shape("ground", "M4 176 Q30 164 64 174 Z")
    liberty(d, 34, 174, .44)


# ================================================================ SAN FRANCISCO
def golden_gate(d: Drawing, x, top, deck, base):
    """One Golden Gate tower with its portal struts, standing in the water."""
    legs = poly((x - 9, base), (x - 8, top), (x - 3, top), (x - 3, base)) + " " + poly((x + 3, base), (x + 3, top), (x + 8, top), (x + 9, base))
    d.shape("gg", legs, spot=True)
    for i, y in enumerate([top + 3, top + 20, top + 36, top + 52]):
        d.shape("gg", rrect(x - 8.5, y, 17, 5 if i == 0 else 4, 1), shadow=False, spot=True)
    d.marks("gg2", f"M{x - 3} {top + 9} H{x + 3} V{top + 20} H{x - 3}Z M{x - 3} {top + 25} H{x + 3} V{top + 36} H{x - 3}Z "
                   f"M{x - 3} {top + 41} H{x + 3} V{top + 52} H{x - 3}Z")


def san_francisco(d: Drawing):
    W = 150
    d.disc("glow", 150, 56, 18)
    # hills behind the city
    d.band("far", "M-30 118 Q20 96 60 106 Q100 88 150 100 Q190 92 230 108", line=False)
    d.band("mid", roofline(W, [(110, 16), (8, 30), (10, 40), (12, 28), (8, 48), (10, 36), (12, 44), (8, 30), (14, 38), (10, 24), (40, 16)]))

    def front(dd):
        B = base_y(dd, W)
        # Salesforce Tower: tallest, tapering slightly with a rounded open crown
        dd.shape("b1", f"M{150 - 11} {B} L{150 - 10} 52 Q{150 - 9} 34 150 32 Q{150 + 9} 34 {150 + 10} 52 L{150 + 11} {B}Z")
        dd.shape("b2", f"M154 {B} L154 34 Q{150 + 9} 36 {150 + 10} 52 L{150 + 11} {B}Z", shadow=False, line=False)
        dd.shape("b3", "M141.5 50 Q142 38 150 36 Q158 38 158.5 50Z", shadow=False, line=False)
        # Transamerica Pyramid with its elevator wings
        x = 118
        dd.shape("stone", poly((x - 13, B), (x - 1.6, 50), (x, 42), (x + 1.6, 50), (x + 13, B)))
        dd.shape("stone", poly((x - 9.5, 96), (x - 7.6, 72), (x - 4, 72), (x - 4, 96)) + " " + poly((x + 4, 96), (x + 4, 72), (x + 7.6, 72), (x + 9.5, 96)), shadow=False)
        dd.shape("stone2", poly((x + 1.6, 50), (x + 13, B), (x + 4, B), (x, 50)), shadow=False, line=False)
        # flanking towers
        dd.shape("b1", blocks(B, [(10, 46), (9, 58)], 88))
        dd.shape("b3", blocks(B, [(10, 40)], 170))
        dd.shape("b3", blocks(B, [(10, 30), (8, 22)], 66))
    front(d)
    # Golden Gate tower and deck running off to the left, landing at Fort Point
    deck = 118
    gx, gtop = 40, 46
    d.stroke("gg", f"M{gx} {gtop + 2} Q-6 104 -30 {deck - 6} M{gx} {gtop + 2} Q66 96 92 {deck}", 2.2)
    d.stroke("gg2", " ".join(f"M{x} {gtop + 4 + (x - gx) ** 2 * .011:.1f} V{deck}" for x in range(gx + 6, 92, 7)) +
             " " + " ".join(f"M{x} {gtop + 4 + (gx - x) ** 2 * .014:.1f} V{deck}" for x in range(gx - 6, -10, -7)), 1, line=False)
    golden_gate(d, gx, gtop, deck, base_y(d, W))
    d.shape("gg", rrect(-30, deck, 124, 6, 1), spot=True)
    water(d, W, front, [(110, 166, 22), (30, 170, 16), (150, 178, 18)])
    d.shape("light", "M-30 136 Q-14 124 2 130 Q14 120 30 128 Q44 120 58 130 Q72 124 84 136 Q60 140 -30 140Z", line=False)
    d.shape("light", cloud(170, 80, .7))


# ================================================================ CHICAGO
def willis(d: Drawing, x, base, s):
    """Willis Tower: bundled tubes stepping back at different heights, twin antennas. s = px per metre."""
    y = lambda m: base - m * s
    d.shape("b1", poly((x - 16, base), (x - 16, y(330)), (x - 5.3, y(330)), (x - 5.3, y(442)), (x + 5.3, y(442)), (x + 5.3, y(270)),
                       (x + 16, y(270)), (x + 16, y(205)), (x + 16, base)))
    d.shape("b2", poly((x + 5.3, y(442)), (x + 5.3, base), (x + 1, base), (x + 1, y(442))), shadow=False, line=False)
    d.shape("b2", poly((x + 11, y(270)), (x + 16, y(270)), (x + 16, base), (x + 11, base)), shadow=False, line=False)
    d.stroke("b3", f"M{x - 16} {y(205):.1f} H{x + 16} M{x - 16} {y(270):.1f} H{x + 5}", 1.2, line=False)
    mast(d, x - 3, y(527), y(442), "b1", 1.8)
    mast(d, x + 3, y(520), y(442), "b1", 1.8)


def hancock(d: Drawing, x, base, s):
    y = lambda m: base - m * s
    top = y(344)
    d.shape("b1", poly((x - 13, base), (x - 8, top), (x + 8, top), (x + 13, base)))
    d.shape("b2", poly((x + 3, top), (x + 8, top), (x + 13, base), (x + 4.5, base)), shadow=False, line=False)
    # X-bracing, five stacked
    n = 5
    xs = ""
    for i in range(n):
        y0 = base - (base - top) * i / n
        y1 = base - (base - top) * (i + 1) / n
        w0 = 13 - 5 * i / n
        w1 = 13 - 5 * (i + 1) / n
        xs += f"M{x - w0:.1f} {y0:.1f} L{x + w1:.1f} {y1:.1f} M{x + w0:.1f} {y0:.1f} L{x - w1:.1f} {y1:.1f} "
    d.stroke("b3", xs, 1.3)
    mast(d, x - 3.5, y(457), top, "b1", 1.8)
    mast(d, x + 3.5, y(457), top, "b1", 1.8)


def chicago(d: Drawing):
    W = 150
    s = 0.235
    d.disc("glow", 46, 62, 17)
    d.band("far", roofline(W, [(30, 26), (12, 44), (10, 60), (14, 40), (12, 52), (60, 36), (12, 64), (10, 50), (14, 70), (12, 40), (60, 30)]), line=False)
    d.band("mid", roofline(W, [(40, 18), (12, 30), (10, 44), (14, 26), (12, 36), (14, 22), (12, 40), (10, 30), (14, 48), (12, 26), (12, 34), (60, 20)]))

    def front(dd):
        B = base_y(dd, W)
        # Aon Center: plain white slab, and a stepped neighbour
        dd.shape("stone", blocks(B, [(16, 346 * s)], 156))
        dd.shape("stone2", blocks(B, [(5, 346 * s)], 167), shadow=False, line=False)
        tower(dd, 52, B, [(10, B - 60), (7, B - 74), (4, B - 80)], "b3", "b2")
        willis(dd, 84, B, s)
        hancock(dd, 128, B, s)
    front(d)
    water(d, W, front, deep=False)
    # the river, crossed by a bascule bridge
    d.shape("bridge", rrect(-30, 162, 260, 6, 1), spot=True)
    tri = " ".join(f"M{x} 162 L{x + 7} 155 L{x + 14} 162" for x in range(-28, 230, 14))
    d.stroke("bridge", "M-30 155 H230 " + tri, 1.6)
    for bx in (30, 170):
        d.shape("bridge", f"M{bx - 7} 162 V150 L{bx} 145 L{bx + 7} 150 V162Z")
        d.marks("win", rrect(bx - 2.5, 151, 5, 4, 1))
    d.band("sea2", waves(176, 2, 24), line=False)
    d.stroke("light", "M40 182 h18 M120 186 h22", 2)


# ================================================================ TORONTO
CN = {"concrete": "#A69F94", "concrete2": "#7F786E", "pod": "#8A93A3", "dome": "#F2F2EE", "dome2": "#C9CDD3"}


def toronto(d: Drawing):
    W = 156
    s = 0.25
    d.disc("glow", 148, 58, 18)
    birds(d, [(118, 40, .9), (130, 34, .7)])
    d.band("far", roofline(W, [(70, 20), (10, 34), (12, 46), (10, 30), (60, 40), (12, 54), (10, 38), (12, 48), (80, 26)]), line=False)
    d.band("mid", roofline(W, [(60, 14), (10, 22), (40, 18), (12, 30), (10, 40), (14, 34), (12, 46), (10, 28), (60, 20)]))

    def front(dd):
        B = base_y(dd, W)
        y = lambda m: W - m * s
        x = 84
        dd.stroke("concrete2", f"M{x} {y(553):.1f} V{y(450):.1f}", 2.2)
        dd.shape("concrete", poly((x - 2.6, y(447)), (x - 1.8, y(470)), (x + 1.8, y(470)), (x + 2.6, y(447))))
        dd.shape("pod", ellipse(x, y(447), 5, 3))
        dd.shape("concrete", poly((x - 9, B), (x - 3.5, y(330)), (x + 3.5, y(330)), (x + 9, B)))
        dd.shape("concrete2", poly((x + 1, y(330)), (x + 3.5, y(330)), (x + 9, B), (x + 2, B)), shadow=False, line=False)
        p = y(342)
        dd.shape("concrete", f"M{x - 13} {p - 2} Q{x - 13} {p - 8} {x} {p - 10} Q{x + 13} {p - 8} {x + 13} {p - 2} V{p + 4} H{x - 13}Z")
        dd.shape("pod", f"M{x - 19} {p + 4} Q{x} {p - 1} {x + 19} {p + 4} L{x + 16} {p + 10} Q{x} {p + 13} {x - 16} {p + 10}Z", spot=True)
        dd.shape("concrete", f"M{x - 12} {p + 10} Q{x} {p + 13} {x + 12} {p + 10} L{x + 9} {p + 16} Q{x} {p + 18} {x - 9} {p + 16}Z")
        dd.stroke("win", f"M{x - 14} {p + 6} H{x + 14}", 1.4, line=False)
        # Rogers-style dome at its foot
        dd.shape("dome", f"M30 {B} V{W - 8} Q32 {W - 30} 56 {W - 32} Q80 {W - 30} 82 {W - 8} V{B}Z")
        dd.stroke("dome2", f"M36 {W - 20} Q56 {W - 30} 78 {W - 20} M33 {W - 10} Q56 {W - 22} 81 {W - 10}", 1.4)
        dd.marks("dome2", f"M56 {W - 32} V{W - 4}")
        # downtown towers
        tower(dd, 124, B, [(9, y(298))], "b1", "b2")
        tower(dd, 141, B, [(8, y(239)), (5, y(255))], "b3", "b2")
        tower(dd, 108, B, [(7, y(220))], "b3", "b2")
        tower(dd, 158, B, [(8, y(200))], "b1", "b2")
    front(d)
    water(d, W, front, [(30, 170, 16), (120, 176, 20)])
    # sailboat on the lake
    d.shape("light", poly((150, 166), (150, 146), (162, 166)))
    d.shape("pop", "M144 168 H166 L162 173 H148Z", spot=True)


# ================================================================ RIO DE JANEIRO
RIO = {"forest": "#3E7348", "forest2": "#2C5636", "rock": "#9A948A", "rock2": "#76706A", "statue": "#F4F1EA",
       "sand": "#F2D9A6", "palm": "#2F5E45", "sea": "#3F92BE", "sea2": "#2C6F99", "town": "#EDE6D8"}


def rio(d: Drawing):
    W = 146
    d.disc("glow", 106, 54, 18)
    d.band("far", "M-30 118 Q10 104 40 112 Q70 100 100 116 Q150 108 230 118", line=False)
    # Corcovado with Christ the Redeemer
    group(d, "translate(18 14)", lambda: (
        d.shape("forest", "M-48 146 L-10 120 Q10 92 26 66 Q34 50 40 48 Q46 50 50 62 Q60 90 80 120 Q96 134 110 146Z"),
        d.shape("forest2", "M40 48 Q46 50 50 62 Q60 90 80 120 Q96 134 110 146 H62 Q52 100 40 48Z", shadow=False, line=False),
        d.shape("statue", "M40 24 Q42 24 42.6 27 L54 27.4 L54 29.4 L42.6 30 L42.2 39 L43.4 49 H36.6 L37.8 39 L37.4 30 L26 29.4 L26 27.4 L37.4 27 Q38 24 40 24Z"),
        d.shape("statue", circle(40, 21.5, 2.6), shadow=False)))
    # Sugarloaf and Urca
    d.shape("rock", "M128 160 L132 120 Q134 76 152 64 Q166 56 176 68 Q190 86 192 130 L196 160Z")
    d.shape("rock2", "M164 58 Q170 60 176 68 Q190 86 192 130 L196 160 H180 Q182 100 164 58Z", shadow=False, line=False)
    d.shape("forest", "M130 150 Q140 136 156 140 Q176 134 196 150 V160 H130Z", shadow=False)
    d.shape("rock", "M94 160 Q100 120 116 112 Q130 110 136 124 Q140 140 142 160Z")
    d.shape("forest", "M94 160 Q100 140 112 138 Q130 134 142 160Z", shadow=False)
    d.stroke("dark", "M116 113 L156 65", 1)
    d.marks("pop", rrect(134, 89, 5, 4, 1))
    # city along the shore
    d.shape("town", blocks(W + 6, [(8, 12), (10, 18), (8, 10), (12, 16), (10, 12), (8, 20), (10, 14), (8, 9)], 30), line=False)
    d.marks("rock2", " ".join(rrect(x, y, 2, 2, .4) for x, y in [(33, W - 3), (41, W - 9), (43, W - 3), (51, W - 1), (59, W - 7), (61, W - 1),
                                                                 (71, W - 3), (79, W - 11), (81, W - 5), (89, W - 3), (99, W - 6)]) if d.paper else "")
    water(d, W + 4, deep=False)
    # Copacabana beach with palms
    d.band("sand", "M-30 176 Q60 160 230 172")
    d.stroke("light", "M-30 175 Q60 159 230 171", 1.6, line=False)
    palm(d, 26, 184, 46, -6)
    palm(d, 176, 182, 40, 6)
    d.stroke("light", "M60 156 h16 M130 160 h20", 2)


# ================================================================ LOS ANGELES
def slim_palm(d: Drawing, x, base, h, lean=0, role="palm"):
    """A tall Washingtonia palm: thin trunk, small mop of fronds."""
    tx, ty = x + lean, base - h
    d.limb(role, f"M{x} {base} Q{x + lean * 0.1} {base - h * 0.5} {tx} {ty}", 2.4)
    fr = ""
    for ang in (-170, -135, -100, -70, -40, -8, 25, 155):
        a = math.radians(ang)
        ex, ey = tx + 11 * math.cos(a), ty + 11 * math.sin(a) + 4
        fr += f"M{tx:.1f} {ty:.1f} Q{tx + 6 * math.cos(a):.1f} {ty + 6 * math.sin(a) - 3:.1f} {ex:.1f} {ey:.1f} "
    d.stroke(role, fr, 2.4)


def los_angeles(d: Drawing):
    W = 156
    s = 0.33
    d.disc("glow", 64, 80, 30)
    d.band("far", "M-30 116 L0 102 L20 108 L46 90 L66 100 L90 86 L116 98 L140 84 L168 96 L196 90 L230 104", line=False)
    d.band("mid", roofline(W, [(66, 10), (10, 22), (12, 30), (10, 18), (14, 34), (10, 26), (12, 20), (12, 36), (10, 24), (70, 12)]))

    def front(dd):
        B = base_y(dd, W)
        y = lambda m: W - m * s
        # City Hall: stepped tower with a pyramid cap
        x = 52
        tower(dd, x, B, [(13, W - 20), (7, y(110)), (5, y(122))], "stone", "stone2")
        dd.shape("stone", poly((x - 5, y(122)), (x, y(138)), (x + 5, y(122))))
        # Wilshire Grand: sail-shaped crown and spire
        x = 96
        dd.shape("b1", f"M{x - 11} {B} V{y(270):.1f} Q{x - 2} {y(276):.1f} {x + 9} {y(300):.1f} L{x + 11} {y(292):.1f} V{B}Z")
        dd.shape("b2", f"M{x + 4} {B} V{y(282):.1f} L{x + 9} {y(300):.1f} L{x + 11} {y(292):.1f} V{B}Z", shadow=False, line=False)
        dd.shape("b1", poly((x + 7.5, y(298)), (x + 8.6, y(335)), (x + 9.6, y(298))))
        # US Bank Tower: round shaft with a stepped glass crown
        x = 128
        tiers = [(10, y(280)), (8.5, y(292)), (7, y(300)), (5, y(310))]
        tower(dd, x, B, tiers, "b3", "b2", frac=0.3)
        dd.stroke("b2", f"M{x - 5} {y(275):.1f} V{B} M{x} {y(275):.1f} V{B}", 1, line=False)
        dd.shape("win", poly((x - 8.5, y(293)), (x + 8.5, y(293)), (x + 8.5, y(290)), (x - 8.5, y(290))), shadow=False, spot=True)
        # Aon and a flat-top neighbour
        tower(dd, 154, B, [(9, y(262))], "b1", "b2")
        tower(dd, 76, B, [(7, y(200))], "b3", "b2")
    front(d)
    # boulevard with palms
    d.band("near", f"M-30 {W} H230")
    d.band("road", f"M-30 {W + 14} H230")
    d.stroke("light", " ".join(f"M{x} {W + 22} h12" for x in range(4, 200, 26)), 2)
    d.band("deep", hills(W + 32, 2), line=False)
    for x, h, ln in [(20, 104, -3), (36, 84, 2), (172, 98, 3), (186, 80, -2)]:
        slim_palm(d, x, W + 12, h, ln)


# ================================================================ SEATTLE
def ferris(d: Drawing, x, cy, r, base, role="wheel", cab="pop"):
    d.limb(role, f"M{x - r * .55} {base} L{x} {cy} L{x + r * .55} {base}", 2.6)
    d.stroke(role, circle(x, cy, r), 2.6, shadow=True)
    d.stroke(role, " ".join(f"M{x} {cy} L{x + r * math.cos(math.radians(a)):.1f} {cy + r * math.sin(math.radians(a)):.1f}" for a in range(0, 360, 30)), 1, line=False)
    for a in range(15, 375, 30):
        cx, cyy = x + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))
        d.shape(cab, rrect(cx - 2.2, cyy - 1, 4.4, 4.4, 1.2), shadow=False, spot=True)
    d.shape(role, circle(x, cy, 2.6), shadow=False)


def seattle(d: Drawing):
    W = 152
    s = 0.31
    # Mount Rainier, big and pale behind the city
    d.shape("mtn", "M-30 126 Q20 112 60 96 Q90 70 110 52 Q122 44 132 48 Q150 60 176 86 Q204 108 230 116 V160 H-30Z")
    d.shape("snow", "M90 70 Q104 56 112 51 Q122 44 132 48 Q144 56 160 72 L150 74 L142 68 L134 76 L124 68 L114 76 L106 70 L98 76Z", shadow=False)
    d.shape("mtn2", "M132 48 Q150 60 176 86 Q204 108 230 116 V160 H160 Q160 100 132 48Z", shadow=False, line=False)
    d.band("far", roofline(W, [(80, 16), (10, 30), (12, 42), (10, 26), (14, 36), (12, 22), (90, 14)]), line=False)
    d.band("mid", roofline(W, [(50, 12), (12, 22), (10, 30), (14, 18), (12, 26), (10, 20), (14, 32), (12, 16), (90, 10)]))

    def front(dd):
        B = base_y(dd, W)
        y = lambda m: W - m * s
        # Columbia Center: dark, stepping back in three tiers
        tower(dd, 84, B, [(13, y(236)), (10.5, y(262)), (7.5, y(284))], "b1", "b2")
        # 1201 Third Avenue: pointed crown
        x = 110
        dd.shape("b3", poly((x - 9, B), (x - 9, y(215)), (x - 5, y(225)), (x, y(235)), (x + 5, y(225)), (x + 9, y(215)), (x + 9, B)))
        dd.shape("b2", poly((x + 3, B), (x + 3, y(229)), (x + 5, y(225)), (x + 9, y(215)), (x + 9, B)), shadow=False, line=False)
        # Two Union Square and a neighbour
        tower(dd, 58, B, [(9, y(200)), (6, y(212))], "b3", "b2")
        tower(dd, 128, B, [(8, y(180))], "b1", "b2")
        # Smith Tower: little white tower with a pyramid cap
        x = 40
        dd.shape("stone", poly((x - 5, B), (x - 5, y(110)), (x - 3.5, y(110)), (x, y(140)), (x + 3.5, y(110)), (x + 5, y(110)), (x + 5, B)))
    front(d)
    water(d, W, front, [(28, 166, 16), (110, 172, 22)])
    # the Great Wheel on its pier
    d.shape("pier", rrect(136, W - 6, 64, 10, 1.5))
    d.stroke("pier", "M140 160 V170 M150 160 V170 M170 160 V170 M190 160 V170", 2)
    ferris(d, 166, W - 36, 25, W - 6)
    # ferry
    def ferry():
        d.shape("light", "M0 8 H44 L40 16 H4Z")
        d.shape("hull", "M0 13 H44 L42 16 H2Z", shadow=False, spot=True)
        d.shape("light", rrect(8, 1, 28, 7, 1.5))
        d.shape("hull", rrect(19, -4, 4, 6, 1), shadow=False)
        d.marks("hull", " ".join(rrect(11 + i * 6, 3, 3.5, 2.5, .5) for i in range(4)))
    group(d, "translate(54 160)", ferry)


# ================================================================ LAS VEGAS
def las_vegas(d: Drawing):
    W = 154
    s = 0.36
    d.disc("glow", 104, 104, 46)
    d.band("far", "M-30 120 L4 104 L22 112 L44 96 L60 106 L84 94 L110 108 L140 98 L164 108 L190 96 L230 110", line=False)
    d.band("mid", roofline(W, [(60, 10), (14, 22), (10, 16), (12, 30), (90, 14), (12, 26), (60, 12)]))

    def front(dd):
        B = base_y(dd, W)
        y = lambda m: W - m * s
        # observation tower: tapering shaft, two-storey pod, spire
        x = 46
        dd.shape("tw", poly((x - 7, B), (x - 2.5, y(250)), (x + 2.5, y(250)), (x + 7, B)))
        dd.shape("tw2", poly((x + 1, y(250)), (x + 2.5, y(250)), (x + 7, B), (x + 2, B)), shadow=False, line=False)
        p = y(260)
        dd.shape("tw", f"M{x - 12} {p} L{x - 9} {p - 9} H{x + 9} L{x + 12} {p} L{x + 9} {p + 6} H{x - 9}Z")
        dd.shape("pop", poly((x - 12, p), (x + 12, p), (x + 10.5, p + 3), (x - 10.5, p + 3)), shadow=False, spot=True)
        dd.shape("tw", poly((x - 1.4, p - 9), (x, y(350)), (x + 1.4, p - 9)))
        # pyramid with its beam of light
        x = 96
        if dd.paper:
            dd.raw(f'<path d="M{x - 3} {y(105):.1f} L{x - 9} -10 L{x + 9} -10 L{x + 3} {y(105):.1f}Z" fill="{dd.c["light"]}" opacity=".55"/>')
        dd.shape("pyr", poly((x - 30, B), (x, y(105)), (x + 30, B)))
        dd.shape("pyr2", poly((x, y(105)), (x + 30, B), (x + 6, B)), shadow=False, line=False)
        # curved bronze resort tower
        x = 142
        dd.shape("gold", f"M{x - 15} {B} V{y(150):.1f} Q{x - 2} {y(196):.1f} {x + 14} {y(186):.1f} V{B}Z", spot=True)
        dd.shape("gold2", f"M{x + 4} {B} V{y(192):.1f} Q{x + 9} {y(190):.1f} {x + 14} {y(186):.1f} V{B}Z", shadow=False, line=False)
        dd.stroke("gold2", " ".join(f"M{x - 15} {y(m):.1f} H{x + 4}" for m in range(20, 150, 20)), 1, line=False)
        # Y-shaped tower block
        tower(dd, 120, B, [(10, y(110)), (6, y(118))], "tw", "tw2")
    front(d)
    # big wheel on the Strip edge
    ferris(d, 168, W - 30, 19, W + 2, "tw", "pop")
    # desert floor with palms
    d.band("ground", f"M-30 {W} H230")
    d.band("near", hills(W + 20, 3), line=False)
    for x, h, ln in [(26, 44, -3), (186, 40, 3)]:
        palm(d, x, W + 14, h, ln, s=.85)
    d.stroke("dark", "M70 172 h20 M120 176 h16", 2)


# ================================================================ MIAMI
def miami(d: Drawing):
    W = 150
    s = 0.36
    d.disc("glow", 52, 58, 18)
    d.band("far", roofline(W, [(40, 20), (10, 44), (12, 58), (10, 36), (14, 66), (12, 48), (10, 60), (14, 40), (12, 54), (80, 24)]), line=False)
    d.band("mid", roofline(W, [(40, 12), (10, 24), (12, 34), (14, 20), (10, 40), (12, 28), (14, 22), (12, 36), (10, 18), (70, 12)]))

    def front(dd):
        B = base_y(dd, W)
        y = lambda m: W - m * s
        # Southeast Financial Center: saw-tooth slanted crown
        x = 68
        dd.shape("b3", poly((x - 11, B), (x - 11, y(205)), (x - 4, y(233)), (x - 4, y(215)), (x + 4, y(225)), (x + 11, y(200)), (x + 11, B)))
        dd.shape("b2", poly((x + 4, B), (x + 4, y(225)), (x + 11, y(200)), (x + 11, B)), shadow=False, line=False)
        # Panorama Tower: tallest, plain slab
        tower(dd, 94, B, [(10, y(265))], "b1", "b2")
        # Four Seasons: tapering crown
        x = 116
        dd.shape("b3", poly((x - 8, B), (x - 8, y(225)), (x - 5, y(240)), (x + 5, y(240)), (x + 8, y(225)), (x + 8, B)))
        dd.shape("b2", poly((x + 3, B), (x + 3, y(240)), (x + 5, y(240)), (x + 8, y(225)), (x + 8, B)), shadow=False, line=False)
        # Miami Tower: three stepped half-round crowns, lit in pastel colours
        x = 146
        top = y(190)
        dd.shape("b1", f"M{x - 13} {B} V{top + 26} H{x + 13} V{B}Z")
        dd.shape("lit1", f"M{x - 13} {top + 27} V{top + 22} A13 9 0 0 1 {x + 13} {top + 22} V{top + 27}Z", spot=True)
        dd.shape("lit2", f"M{x - 10} {top + 15} A10 7 0 0 1 {x + 10} {top + 15} V{top + 18} H{x - 10}Z", spot=True)
        dd.shape("lit1", f"M{x - 7} {top + 7} A7 5.5 0 0 1 {x + 7} {top + 7} V{top + 9} H{x - 7}Z", spot=True)
        dd.shape("b1", f"M{x - 10} {top + 22} V{top + 18} H{x + 10} V{top + 22}Z M{x - 7} {top + 15} V{top + 9} H{x + 7} V{top + 15}Z", shadow=False)
        dd.shape("b2", f"M{x + 5} {B} V{top + 27} H{x + 13} V{B}Z", shadow=False, line=False)
        # Freedom Tower: Spanish-style tower with a cupola
        x = 40
        dd.shape("cream", poly((x - 9, B), (x - 9, W - 26), (x - 5, W - 26), (x - 5, W - 50), (x + 5, W - 50), (x + 5, W - 26), (x + 9, W - 26), (x + 9, B)))
        dd.shape("terra", f"M{x - 6} {W - 50} Q{x - 6} {W - 62} {x} {W - 64} Q{x + 6} {W - 62} {x + 6} {W - 50}Z")
        dd.shape("terra", poly((x - 1, W - 63), (x, W - 70), (x + 1, W - 63)), shadow=False)
    front(d)
    water(d, W, front, [(110, 166, 20), (40, 174, 14)])
    palm(d, 18, 192, 54, 6)
    palm(d, 184, 194, 46, -6)


# ================================================================ NEW ORLEANS
def new_orleans(d: Drawing):
    W = 150
    s = 0.4
    d.disc("glow", 152, 66, 20)
    # Crescent City Connection, cantilever truss in the distance
    d.band("far", roofline(W, [(40, 16), (10, 26), (12, 34), (10, 22), (14, 30), (100, 14)]), line=False)
    d.band("mid", roofline(W, [(40, 12), (10, 22), (12, 28), (14, 18), (10, 34), (12, 24), (14, 16), (100, 10)]))

    def front(dd):
        B = base_y(dd, W)
        y = lambda m: W - m * s
        # Superdome
        dd.shape("dome", f"M18 {B} V{W - 14} Q20 {W - 30} 48 {W - 32} Q76 {W - 30} 78 {W - 14} V{B}Z")
        dd.stroke("dome2", f"M20 {W - 18} H76 M24 {W - 24} Q48 {W - 30} 72 {W - 24}", 1.4)
        # Hancock Whitney Center: pyramid top
        x = 96
        dd.shape("b1", poly((x - 9, B), (x - 9, y(175)), (x, y(197)), (x + 9, y(175)), (x + 9, B)))
        dd.shape("b2", poly((x + 3, B), (x + 3, y(190)), (x, y(197)), (x + 9, y(175)), (x + 9, B)), shadow=False, line=False)
        # One Shell Square: white slab
        tower(dd, 120, B, [(9, y(212))], "stone", "stone2")
        tower(dd, 76, B, [(7, y(150))], "b3", "b2")
        # St. Louis Cathedral: three spires on the riverfront
        x = 156
        dd.shape("stone", poly((x - 20, B), (x - 20, W - 26), (x + 20, W - 26), (x + 20, B)))
        dd.shape("stone", poly((x - 20, W - 26), (x - 20, W - 40), (x - 14, W - 40), (x - 14, W - 26)))
        dd.shape("stone", poly((x + 14, W - 26), (x + 14, W - 40), (x + 20, W - 40), (x + 20, W - 26)))
        dd.shape("slate", poly((x - 20.5, W - 40), (x - 17, W - 56), (x - 13.5, W - 40)) + " " + poly((x + 13.5, W - 40), (x + 17, W - 56), (x + 20.5, W - 40)), spot=True)
        dd.shape("stone", poly((x - 6, W - 26), (x - 6, W - 46), (x + 6, W - 46), (x + 6, W - 26)))
        dd.shape("slate", poly((x - 7, W - 46), (x, W - 74), (x + 7, W - 46)), spot=True)
        dd.marks("stone2", " ".join(f"M{px - 2} {W - 6} V{W - 14} Q{px - 2} {W - 17} {px} {W - 17} Q{px + 2} {W - 17} {px + 2} {W - 14} V{W - 6}Z" for px in (x - 12, x - 4, x + 4, x + 12)))
        dd.marks("dark", circle(x, W - 36, 2.4))
    front(d)
    water(d, W, front, [(130, 176, 20)])
    # paddle steamer
    def boat():
        d.shape("hull", rrect(14, -10, 3.5, 14, 1))
        d.shape("hull", rrect(22, -10, 3.5, 14, 1))
        d.shape("hull", "M12.5 -10 H19 L18 -13 H13.5Z M20.5 -10 H27 L26 -13 H21.5Z", shadow=False)
        d.shape("light", rrect(8, 4, 40, 7, 1))
        d.shape("light", rrect(4, 11, 50, 7, 1))
        d.shape("light", "M0 18 H58 L54 25 H4Z")
        d.stroke("hull", "M8 14.5 H52 M12 7.5 H44", 1.2, line=False)
        d.shape("wheel", "M58 10 A8 8 0 0 1 58 26 H52 V10Z", spot=True)
        d.stroke("light", "M55 12 V24 M53 18 H62", 1, line=False)
        d.shape("pop", poly((30, 4), (30, -6), (38, -3), (30, 0)), shadow=False)
    group(d, "translate(40 152)", boat)


# ================================================================ BOSTON
def boston(d: Drawing):
    W = 152
    s = 0.36
    d.disc("glow", 54, 62, 18)
    d.band("far", roofline(W, [(30, 18), (12, 30), (10, 40), (14, 26), (40, 34), (12, 46), (10, 30), (14, 38), (90, 20)]), line=False)
    # Back Bay rooftops with the gold State House dome
    d.band("mid", roofline(W, [(44, 14), (10, 20), (12, 16), (14, 24), (12, 18), (10, 22), (14, 16), (12, 26), (10, 18), (90, 14)]))

    def front(dd):
        B = base_y(dd, W)
        y = lambda m: W - m * s
        # State House
        x = 34
        dd.shape("brick", poly((x - 14, B), (x - 14, W - 18), (x + 14, W - 18), (x + 14, B)))
        dd.shape("stone", poly((x - 14, W - 18), (x, W - 24), (x + 14, W - 18)))
        dd.shape("gold", f"M{x - 8} {W - 22} Q{x - 8} {W - 34} {x} {W - 35} Q{x + 8} {W - 34} {x + 8} {W - 22}Z", spot=True)
        dd.shape("gold", poly((x - 1.4, W - 34), (x, W - 40), (x + 1.4, W - 34)), shadow=False)
        dd.marks("stone", " ".join(f"M{px} {W - 4} V{W - 14}" for px in ()) or rrect(x - 10, W - 14, 20, 2, .5))
        # Prudential Tower with its mast
        x = 72
        tower(dd, x, B, [(11, y(229)), (8, y(236))], "b1", "b2")
        mast(dd, x, y(270), y(236), "b1", 1.8)
        # 200 Clarendon (Hancock): slim mirror-glass slab with its notch
        x = 104
        dd.shape("glass", poly((x - 11, B), (x - 11, y(241)), (x + 11, y(241)), (x + 11, B)))
        dd.shape("glass2", poly((x - 11, y(241)), (x - 5, y(241)), (x - 5, B), (x - 11, B)), shadow=False, line=False)
        dd.marks("b2", f"M{x - .8} {y(238):.1f} H{x + .8} V{B} H{x - .8}Z")
        tower(dd, 128, B, [(8, y(180))], "b3", "b2")
        # Zakim bridge: inverted-Y tower with fanned cables
        x = 162
        cables = " ".join(f"M{x} {W - 64 + i * 3} L{x + o} {W - 18}" for i, o in enumerate((-32, -24, -16, 16, 24, 32)))
        dd.stroke("cable", cables, 1, line=True)
        dd.shape("cable", poly((x - 12, B), (x - 1.5, W - 70), (x, W - 80), (x + 1.5, W - 70), (x + 12, B), (x + 8, B), (x, W - 46), (x - 8, B)), spot=True)
        dd.shape("cable", rrect(124, W - 20, 76, 4, 1))
    front(d)
    water(d, W, front, [(30, 168, 16)])
    # sailboat on the Charles
    d.shape("light", poly((54, 172), (54, 146), (68, 172)))
    d.shape("light", poly((52, 172), (52, 156), (44, 172)))
    d.shape("pop", "M40 174 H72 L68 179 H44Z", spot=True)


# ================================================================ WASHINGTON, D.C.
def washington(d: Drawing):
    W = 150
    d.disc("glow", 146, 56, 18)
    d.band("far", "M-30 136 Q-10 128 10 132 Q24 124 40 130 Q60 122 78 130 Q100 124 120 130 Q140 122 160 130 Q180 124 200 130 Q216 126 230 132", line=False)
    d.band("mid", "M-30 144 Q-14 138 2 142 Q16 134 34 140 Q50 134 66 140 Q84 136 100 140 Q120 134 136 140 Q156 134 172 140 Q190 136 230 142")

    def front(dd):
        B = base_y(dd, W)
        # Capitol: dome on a colonnaded drum, low wings
        x = 44
        dd.shape("stone", poly((x - 34, B), (x - 34, W - 14), (x + 34, W - 14), (x + 34, B)))
        dd.shape("stone", poly((x - 12, W - 14), (x - 12, W - 30), (x + 12, W - 30), (x + 12, W - 14)))
        dd.shape("stone", f"M{x - 10} {W - 30} Q{x - 10} {W - 48} {x} {W - 50} Q{x + 10} {W - 48} {x + 10} {W - 30}Z")
        dd.shape("stone", rrect(x - 2.5, W - 56, 5, 7, 1.5))
        dd.shape("stone", poly((x - 1, W - 56), (x, W - 61), (x + 1, W - 56)))
        dd.stroke("stone2", " ".join(f"M{x + o} {W - 28} V{W - 16}" for o in range(-9, 10, 3)) + " " +
                  " ".join(f"M{x + o} {W - 12} V{W - 2}" for o in list(range(-31, -12, 4)) + list(range(15, 34, 4))), 1.1, line=False)
        dd.shape("stone2", f"M{x + 3} {W - 30} V{W - 49} Q{x + 10} {W - 46} {x + 10} {W - 30}Z", shadow=False, line=False)
        # Lincoln Memorial: wide temple on its steps
        x = 160
        dd.shape("stone", poly((x - 30, B), (x - 30, W - 8), (x - 26, W - 8), (x - 26, W - 30), (x + 26, W - 30), (x + 26, W - 8), (x + 30, W - 8), (x + 30, B)))
        dd.shape("stone", rrect(x - 28, W - 38, 56, 9, 1))
        dd.stroke("stone2", " ".join(f"M{x + o} {W - 28} V{W - 9}" for o in range(-22, 23, 4.4 and 4)), 1.6, line=False)
        ink(dd, " ".join(f"M{x + o} {W - 28} V{W - 9}" for o in range(-20, 21, 8)), 1.4)
        # Washington Monument
        x = 100
        dd.shape("stone", poly((x - 7, B), (x - 4.8, 34), (x, 24), (x + 4.8, 34), (x + 7, B)))
        dd.shape("stone2", poly((x + 1.5, B), (x + 1.3, 34), (x, 24), (x + 4.8, 34), (x + 7, B)), shadow=False, line=False)
        dd.stroke("stone2", f"M{x - 6.2} 100 H{x + 6.2}", 1, line=False)
    front(d)
    water(d, W, front, [(76, 168, 14), (110, 174, 16)])
    # cherry blossoms at the water's edge
    d.band("grass", "M-30 184 Q100 176 230 184")
    d.limb("trunk", "M46 186 Q46 176 40 168 M45 178 L54 170 M154 186 Q154 176 160 168 M155 178 L146 170", 3)
    for cx, cy, r in [(32, 166, 11), (44, 158, 12), (56, 166, 10), (42, 170, 9), (168, 166, 11), (156, 158, 12), (144, 166, 10), (158, 170, 9)]:
        d.shape("blossom", circle(cx, cy, r), spot=True, shadow=cy == 158)
    d.marks("blossom2", " ".join(circle(x, y, 1.7) for x, y in [(38, 156), (50, 162), (32, 170), (56, 170), (162, 156), (150, 162), (168, 170), (144, 170)]))


# ================================================================ NASHVILLE
def nashville(d: Drawing):
    W = 150
    s = 0.48
    d.disc("glow", 50, 62, 18)
    d.band("far", "M-30 122 Q30 106 80 116 Q130 104 180 114 Q210 108 230 116", line=False)
    d.band("mid", roofline(W, [(40, 12), (10, 22), (12, 30), (14, 20), (10, 38), (12, 26), (14, 18), (12, 34), (10, 22), (80, 12)]))

    def front(dd):
        B = base_y(dd, W)
        y = lambda m: W - m * s
        # Nashville City Center: pyramid peak
        x = 64
        dd.shape("b3", poly((x - 9, B), (x - 9, y(110)), (x, y(122)), (x + 9, y(110)), (x + 9, B)))
        dd.shape("b2", poly((x + 3, B), (x + 3, y(118)), (x, y(122)), (x + 9, y(110)), (x + 9, B)), shadow=False, line=False)
        # Pinnacle: stepped crown
        tower(dd, 138, B, [(10, y(130)), (7.5, y(145)), (5, y(156)), (1.2, y(166))], "b3", "b2")
        # AT&T "Batman" Building: two tall spires on a gabled crown
        x = 102
        top = y(140)
        dd.shape("b1", poly((x - 13, B), (x - 13, top), (x - 11, top - 4), (x - 11, y(189)), (x - 8.5, top - 10),
                            (x - 8, top - 6), (x, top - 14), (x + 8, top - 6), (x + 8.5, top - 10), (x + 11, y(189)),
                            (x + 11, top - 4), (x + 13, top), (x + 13, B)))
        dd.shape("b2", poly((x + 4, B), (x + 4, top - 9), (x + 8, top - 6), (x + 8.5, top - 10), (x + 11, y(189)), (x + 11, top - 4), (x + 13, top), (x + 13, B)), shadow=False, line=False)
        dd.shape("b3", poly((x - 8, top - 4), (x, top - 11), (x + 8, top - 4), (x + 8, top + 2), (x - 8, top + 2)), shadow=False, line=False)
        dd.stroke("b2", " ".join(f"M{x - 6 + i * 3} {top - 3} V{top + 2}" for i in range(5)), 1, line=False)
        tower(dd, 158, B, [(7, y(100))], "b1", "b2")
        tower(dd, 42, B, [(8, y(90)), (4, y(100))], "b1", "b2")
    front(d)
    water(d, W, front, deep=False)
    # pedestrian truss bridge across the Cumberland
    d.shape("bridge", rrect(-30, 164, 260, 5, 1), spot=True)
    arcs = " ".join(f"M{x} 164 Q{x + 20} 146 {x + 40} 164" for x in range(-30, 230, 40))
    web = " ".join(f"M{x} 164 L{x + 10} {164 - 10 * (1 - ((x + 30) % 40 - 20) ** 2 / 400) - 1:.1f}" for x in range(-30, 230, 10))
    d.stroke("bridge", arcs, 2.4)
    d.stroke("bridge", web, 1.2, line=False)
    d.band("sea2", waves(178, 2, 24), line=False)
    d.stroke("light", "M40 184 h18 M126 186 h22", 2)


# ================================================================ VANCOUVER
def vancouver(d: Drawing):
    W = 150
    s = 0.36
    d.disc("glow", 152, 52, 15)
    # North Shore mountains with the Lions
    d.shape("mtn", "M-30 120 L-6 96 L14 102 L34 76 L44 66 L50 74 L56 64 L64 76 L86 94 L110 84 L132 96 L158 80 L184 98 L206 92 L230 104 V160 H-30Z")
    d.shape("snow", "M34 76 L44 66 L50 74 L56 64 L64 76 L58 78 L54 74 L49 80 L44 75 L38 80Z M152 84 L158 80 L166 86 L160 88Z", shadow=False)
    d.band("far", roofline(W, [(40, 14), (10, 28), (12, 40), (10, 24), (14, 34), (12, 46), (10, 30), (14, 38), (80, 18)]), line=False)
    d.band("mid", roofline(W, [(30, 10), (12, 22), (10, 30), (14, 18), (12, 36), (10, 26), (14, 20), (12, 32), (10, 16), (90, 10)]))

    def front(dd):
        B = base_y(dd, W)
        y = lambda m: W - m * s
        # Living Shangri-La: slim glass tower with a fin top
        x = 108
        dd.shape("b1", poly((x - 8, B), (x - 8, y(190)), (x + 6, y(201)), (x + 8, y(201)), (x + 8, B)))
        dd.shape("b2", poly((x + 3, B), (x + 3, y(197)), (x + 8, y(201)), (x + 8, B)), shadow=False, line=False)
        tower(dd, 88, B, [(8, y(150))], "b3", "b2")
        tower(dd, 150, B, [(8, y(140))], "b1", "b2")
        # Harbour Centre with its flying-saucer lookout
        x = 130
        dd.shape("b3", poly((x - 6, B), (x - 6, y(130)), (x + 6, y(130)), (x + 6, B)))
        dd.shape("b2", poly((x + 2, B), (x + 2, y(130)), (x + 6, y(130)), (x + 6, B)), shadow=False, line=False)
        p = y(134)
        dd.shape("b1", f"M{x - 14} {p} Q{x} {p - 8} {x + 14} {p} Q{x} {p + 6} {x - 14} {p}Z", spot=True)
        dd.shape("b1", f"M{x - 8} {p - 3} Q{x} {p - 9} {x + 8} {p - 3}Z", shadow=False)
        mast(dd, x, y(165), p - 6, "b1", 1.4)
        # Stanley Park trees on the left
        for cx, cy, r in [(14, W - 12, 16), (36, W - 8, 14), (52, W - 4, 10)]:
            dd.shape("tree", circle(cx, cy, r))
    front(d)
    water(d, W, front, [(150, 172, 18)])
    # Canada Place: white sails on its pier
    x0 = 52
    d.shape("pierv", rrect(x0 - 6, 156, 86, 7, 1.5))
    d.shape("sail", "M" + " ".join(f"{x0 + i * 15} 157 L{x0 + i * 15 + 7.5} 138" for i in range(5)) + f" L{x0 + 75} 157Z", spot=True)
    d.stroke("sail2", " ".join(f"M{x0 + i * 15 + 7.5} 138 V157" for i in range(5)), 1, line=False)
    # seaplane
    d.shape("light", "M140 184 Q150 178 168 180 L174 176 L176 182 Q160 188 140 184Z")
    d.stroke("dark", "M146 186 h22 M150 182 v4 M162 182 v4", 1.4)


# ================================================================ MONTREAL
def montreal(d: Drawing):
    W = 152
    s = 0.4
    d.disc("glow", 150, 48, 15)
    # Mount Royal with its lit cross
    d.shape("mtnr", "M-30 130 Q0 100 30 92 Q56 86 80 98 Q104 110 130 124 V160 H-30Z")
    d.stroke("cross", "M40 66 V90 M33 74 H47", 2.4, shadow=True)
    d.band("far", roofline(W, [(40, 14), (10, 26), (12, 36), (14, 22), (10, 30), (60, 18), (12, 28), (80, 14)]), line=False)
    d.band("mid", roofline(W, [(44, 10), (12, 20), (10, 28), (14, 16), (12, 24), (10, 18), (14, 26), (100, 10)]))

    def front(dd):
        B = base_y(dd, W)
        y = lambda m: W - m * s
        # 1000 de La Gauchetiere: copper pyramid roof
        x = 66
        dd.shape("b3", poly((x - 10, B), (x - 10, y(180)), (x + 10, y(180)), (x + 10, B)))
        dd.shape("b2", poly((x + 4, B), (x + 4, y(180)), (x + 10, y(180)), (x + 10, B)), shadow=False, line=False)
        dd.shape("copper", poly((x - 11, y(180)), (x, y(205)), (x + 11, y(180))), spot=True)
        dd.shape("copper2", poly((x, y(205)), (x + 11, y(180)), (x + 3, y(180))), shadow=False, line=False)
        # Place Ville Marie: cruciform slab with its rooftop beacon
        x = 90
        tower(dd, x, B, [(12, y(188))], "b1", "b2")
        dd.stroke("b2", f"M{x - 4} {y(186):.1f} V{B} M{x + 4} {y(186):.1f} V{B}", 1, line=False)
        mast(dd, x, y(200), y(188), "b1", 1.6)
        tower(dd, 112, B, [(8, y(150))], "b3", "b2")
        # Olympic Stadium with its leaning tower
        dd.shape("stade", f"M116 {B} V{W - 10} Q142 {W - 26} 176 {W - 18} L180 {B}Z")
        dd.stroke("stade2", f"M122 {W - 10} Q142 {W - 22} 174 {W - 14}", 1.4)
        dd.shape("stade", f"M140 {W - 20} L130 {W - 26} Q146 {W - 64} 170 {W - 84} L176 {W - 78} Q156 {W - 56} 150 {W - 22}Z")
        dd.shape("stade2", f"M170 {W - 84} L176 {W - 78} L172 {W - 74} L166 {W - 80}Z", shadow=False)
    front(d)
    water(d, W, front, [(120, 170, 20), (70, 178, 14)])
    # the Biosphere on its island
    def bio():
        d.shape("isle", "M-30 24 Q0 12 30 24Z")
        d.shape("bio", "M-17 20 A17 17 0 1 1 17 20Z", spot=True)
        if d.paper:
            d.stroke("bio2", "M-15 12 H15 M-10 2 H10 M0 -0.5 V20 M-9 4 Q-13 12 -11 20 M9 4 Q13 12 11 20", 1, line=False)
        else:
            d.stroke("dark", "M-15 12 H15 M0 -0.5 V20", 1.4)
    group(d, "translate(46 154)", bio)


# ================================================================ MEXICO CITY
def mexico_city(d: Drawing):
    W = 158
    s = 0.36
    d.disc("glow", 150, 52, 16)
    # Popocatepetl and Iztaccihuatl
    d.shape("mtn", "M-30 128 L10 108 Q30 90 44 86 L54 88 Q64 96 78 102 L96 112 L120 104 Q150 78 160 70 Q166 66 172 70 Q190 86 230 108 V160 H-30Z")
    d.shape("snow", "M24 98 Q34 88 44 86 L54 88 Q62 94 70 98 L60 100 L50 96 L40 102 L32 98Z M146 82 Q154 74 160 70 Q166 66 172 70 Q180 76 186 82 L178 84 L170 80 L162 86 L154 82Z", shadow=False)
    d.band("far", roofline(W, [(30, 14), (12, 26), (10, 34), (14, 22), (12, 30), (60, 16), (14, 28), (10, 20), (70, 12)]), line=False)
    d.band("mid", roofline(W, [(40, 10), (12, 18), (14, 26), (10, 16), (12, 22), (60, 12), (12, 20), (80, 10)]))

    def front(dd):
        B = base_y(dd, W)
        y = lambda m: W - m * s
        # Torre Reforma: tallest, with a slanted top
        x = 110
        dd.shape("b1", poly((x - 9, B), (x - 9, y(236)), (x + 9, y(246)), (x + 9, B)))
        dd.shape("b2", poly((x + 3, B), (x + 3, y(243)), (x + 9, y(246)), (x + 9, B)), shadow=False, line=False)
        dd.stroke("b3", " ".join(f"M{x - 9} {y(m):.1f} H{x + 3}" for m in range(40, 230, 40)), 1, line=False)
        # Torre Latinoamericana: stepped top and antenna
        x = 140
        tower(dd, x, B, [(9, y(140)), (7, y(150)), (5, y(158)), (3, y(166))], "b3", "b2")
        mast(dd, x, y(182), y(166), "b3", 1.6)
        tower(dd, 164, B, [(8, y(120))], "b1", "b2")
        # El Angel de la Independencia
        x = 66
        dd.shape("stone", poly((x - 18, B), (x - 18, W - 8), (x - 12, W - 8), (x - 12, W - 16), (x + 12, W - 16), (x + 12, W - 8), (x + 18, W - 8), (x + 18, B)))
        dd.shape("stone", rrect(x - 7, W - 22, 14, 7, 1))
        dd.shape("stone", poly((x - 4, W - 22), (x - 3, 62), (x + 3, 62), (x + 4, W - 22)))
        dd.stroke("stone2", f"M{x - 3.6} 110 H{x + 3.6} M{x - 3.3} 84 H{x + 3.3}", 1.2, line=False)
        dd.shape("stone", rrect(x - 5, 58, 10, 5, 1))
        # gilded winged Victory
        dd.shape("gold", f"M{x - 2} 58 L{x - 2.5} 46 Q{x} 42 {x + 2.5} 46 L{x + 2} 58Z", spot=True)
        dd.shape("gold", f"M{x} 47 Q{x - 10} 36 {x - 14} 40 Q{x - 8} 42 {x - 1} 50Z M{x} 47 Q{x + 10} 36 {x + 14} 40 Q{x + 8} 42 {x + 1} 50Z", spot=True)
        dd.shape("gold", circle(x, 42, 2.2), shadow=False)
        dd.stroke("gold", f"M{x + 1} 44 L{x + 6} 34", 1.6)
    front(d)
    # Paseo de la Reforma with jacarandas
    d.band("near", f"M-30 {W} H230")
    d.band("road", f"M-30 {W + 12} H230")
    d.stroke("light", " ".join(f"M{x} {W + 20} h12" for x in range(4, 200, 26)), 2)
    d.limb("trunk", f"M40 {W + 22} L38 {W - 2} M160 {W + 22} L162 {W - 2}", 3)
    for cx, cy, r in [(28, W - 4, 11), (40, W - 12, 12), (52, W - 4, 10), (38, W + 2, 9), (172, W - 4, 11), (160, W - 12, 12), (148, W - 4, 10), (162, W + 2, 9)]:
        d.shape("jac", circle(cx, cy, r), spot=True, shadow=cy == W - 12)
    d.band("deep", hills(W + 30, 2), line=False)


# ================================================================ HAVANA
def havana(d: Drawing):
    W = 154
    d.disc("glow", 150, 78, 22)
    d.band("far", roofline(W - 12, [(40, 10), (14, 18), (12, 24), (10, 14), (16, 20), (12, 16), (90, 12)]), line=False)

    def front(dd):
        B = base_y(dd, W - 12)
        # El Capitolio
        x = 100
        dd.shape("stone", poly((x - 40, B), (x - 40, W - 36), (x + 40, W - 36), (x + 40, B)))
        dd.shape("stone", poly((x - 14, W - 36), (x - 14, W - 50), (x + 14, W - 50), (x + 14, W - 36)))
        dd.shape("stone", f"M{x - 12} {W - 50} Q{x - 12} {W - 72} {x} {W - 74} Q{x + 12} {W - 72} {x + 12} {W - 50}Z")
        dd.shape("stone2", f"M{x + 3} {W - 50} V{W - 73} Q{x + 12} {W - 70} {x + 12} {W - 50}Z", shadow=False, line=False)
        dd.shape("stone", rrect(x - 3, W - 82, 6, 9, 2))
        dd.shape("stone", poly((x - 1, W - 82), (x, W - 88), (x + 1, W - 82)))
        dd.stroke("stone2", " ".join(f"M{x + o} {W - 48} V{W - 38}" for o in range(-11, 12, 4)), 1.1, line=False)
        # colourful colonial row along the Malecon
        row = [(-30, 22, "c1"), (18, 20, "c2"), (38, 26, "c3"), (58, 18, "c1"), (120, 24, "c2"), (140, 18, "c3"), (160, 26, "c1"), (180, 20, "c2"), (200, 30, "c3")]
        for i, (x0, h, role) in enumerate(row):
            w = (row[i + 1][0] - x0) if i + 1 < len(row) else 30
            dd.shape(role, poly((x0, B), (x0, W - 12 - h), (x0 + w, W - 12 - h), (x0 + w, B)))
            dd.marks("dark", " ".join(f"M{x0 + o} {W - 14} V{W - 20 - h * .3:.1f} Q{x0 + o + 2} {W - 23 - h * .3:.1f} {x0 + o + 4} {W - 20 - h * .3:.1f} V{W - 14}Z"
                                      for o in range(4, int(w) - 4, 8)))
    front(d)
    # El Morro lighthouse on its rock, left
    x = 30
    d.shape("rock", "M-30 160 L-30 124 Q-6 116 20 120 Q40 122 52 136 L58 160Z")
    d.shape("stone", poly((-20, 122), (-20, 112), (40, 112), (46, 128), (-20, 128)))
    d.shape("stone", poly((x - 5, 112), (x - 4, 72), (x + 4, 72), (x + 5, 112)))
    d.shape("stone2", poly((x + 1, 112), (x + 1, 72), (x + 4, 72), (x + 5, 112)), shadow=False, line=False)
    d.shape("dark", rrect(x - 6, 68, 12, 4, 1))
    d.shape("glow2", rrect(x - 3.5, 61, 7, 7, 1), spot=True)
    d.shape("dark", f"M{x - 4.5} 61 Q{x} 54 {x + 4.5} 61Z")
    # Malecon sea wall and the surf
    d.band("wall", f"M-30 {W - 12} H230")
    d.band("wall2", f"M-30 {W - 4} H230", line=False)
    d.band("sea", f"M-30 {W + 2} H230")
    d.band("sea2", waves(W + 24, 2, 24), line=False)
    d.stroke("light", "M40 170 h20 M100 176 h16 M150 184 h22", 2)
    # vintage car on the Malecon
    def car():
        d.shape("car", "M0 0 Q2 -6 10 -7 L14 -12 Q22 -14 30 -12 L34 -7 Q44 -6 46 0 V3 H0Z", spot=True)
        d.shape("light", "M15 -11 Q22 -12.5 29 -11 L31 -7 H13Z", shadow=False)
        d.shape("dark", circle(10, 3, 3.6))
        d.shape("dark", circle(36, 3, 3.6))
        d.stroke("light", "M2 -1 H44", 1, line=False)
    group(d, f"translate(70 {W - 15})", car)


# ================================================================ BUENOS AIRES
def buenos_aires(d: Drawing):
    W = 152
    s = 0.42
    d.disc("glow", 52, 58, 18)
    d.band("far", roofline(W, [(40, 18), (10, 34), (12, 46), (10, 30), (14, 52), (12, 40), (10, 58), (14, 36), (12, 44), (80, 20)]), line=False)
    d.band("mid", roofline(W, [(40, 12), (12, 24), (10, 30), (14, 20), (12, 34), (10, 26), (14, 22), (12, 30), (90, 12)]))

    def front(dd):
        B = base_y(dd, W)
        # Palacio Barolo: tower with a domed lighthouse top
        x = 46
        tower(dd, x, B, [(16, W - 44), (9, W - 62), (6, W - 72)], "stone", "stone2")
        dd.shape("stone", f"M{x - 6} {W - 72} Q{x - 6} {W - 82} {x} {W - 84} Q{x + 6} {W - 82} {x + 6} {W - 72}Z")
        dd.shape("glow2", rrect(x - 2, W - 90, 4, 6, 1), spot=True)
        dd.shape("stone", poly((x - 3, W - 89), (x, W - 94), (x + 3, W - 89)), shadow=False)
        # glass towers of Puerto Madero
        tower(dd, 136, B, [(10, W - 90)], "b1", "b2")
        tower(dd, 156, B, [(8, W - 76), (5, W - 82)], "b3", "b2")
        tower(dd, 72, B, [(8, W - 58)], "b3", "b2")
        # the Obelisco
        x = 104
        dd.shape("obel", poly((x - 7.5, B), (x - 5, 40), (x, 28), (x + 5, 40), (x + 7.5, B)))
        dd.shape("obel2", poly((x + 1.5, B), (x + 1.2, 40), (x, 28), (x + 5, 40), (x + 7.5, B)), shadow=False, line=False)
        dd.marks("dark", rrect(x - 1.2, 50, 2.4, 4, .6))
    front(d)
    water(d, W, front, deep=False)
    # Puerto Madero dock cranes
    def crane(x):
        d.limb("crane", f"M{x - 6} {W} L{x - 2} {W - 22} M{x + 6} {W} L{x + 2} {W - 22}", 2.4)
        d.shape("crane", rrect(x - 6, W - 30, 12, 9, 1.5))
        d.limb("crane", f"M{x + 4} {W - 28} L{x - 18} {W - 50}", 2.2)
    crane(178)
    # Puente de la Mujer: white leaning mast with a fan of cables to the deck
    deck = 174
    bx, tx, ty = 64, 34, 134
    pts = [(bx + (tx - bx) * t, deck + (ty - deck) * t) for t in (.55, .7, .85, 1.0)]
    d.stroke("cable2", " ".join(f"M{x:.1f} {y:.1f} L{bx + 14 + i * 14} {deck}" for i, (x, y) in enumerate(pts)), 1.1)
    d.shape("bridge", rrect(-30, deck, 180, 4.5, 1.5))
    d.shape("bridge", poly((bx - 3, deck + 2), (tx - 1.5, ty), (tx + 1.5, ty - 1), (bx + 4, deck + 2)), spot=True)
    d.band("sea2", waves(184, 2, 24), line=False)


# ================================================================ LIMA
def paraglider(d: Drawing, x, y, s=1.0, role="pop"):
    def draw():
        d.shape(role, "M-16 0 Q0 -8 16 0 L13 3 Q0 -3 -13 3Z", spot=True)
        d.stroke("dark", "M-12 2 L0 16 L12 2 M-5 -1 L0 16 L5 -1", .8)
        d.shape("dark", circle(0, 17, 2), shadow=False)
    group(d, f"translate({x} {y}) scale({s})", draw)


def lima(d: Drawing):
    W = 160
    d.disc("glow", 100, 100, 30)
    # towers on top of the Costa Verde cliffs
    d.band("far", roofline(112, [(50, 8), (12, 24), (10, 34), (14, 20), (12, 40), (10, 26), (14, 18), (12, 30), (90, 10)]), line=False)

    def front(dd):
        B = 120
        tower(dd, 40, B, [(9, 74)], "b1", "b2")
        tower(dd, 60, B, [(7, 84)], "b3", "b2")
        tower(dd, 134, B, [(8, 78), (5, 72)], "b1", "b2")
        tower(dd, 116, B, [(6, 90)], "b3", "b2")
        tower(dd, 172, B, [(8, 86)], "b3", "b2")
        # La Marina lighthouse, red and white
        x = 154
        dd.shape("lh", poly((x - 4.5, B), (x - 3, 82), (x + 3, 82), (x + 4.5, B)))
        dd.shape("lh2", poly((x - 4.2, 112), (x - 3.9, 106), (x + 3.9, 106), (x + 4.2, 112)) + " " + poly((x - 3.7, 98), (x - 3.4, 92), (x + 3.4, 92), (x + 3.7, 98)), shadow=False, spot=True)
        dd.shape("dark", rrect(x - 4, 79, 8, 3, .8))
        dd.shape("glow2", rrect(x - 2.4, 73, 4.8, 6, 1))
        dd.shape("lh2", f"M{x - 3.4} 73 Q{x} 67 {x + 3.4} 73Z", shadow=False)
    front(d)
    # cliffs
    d.band("cliff", "M-30 118 L10 118 L20 116 H70 L80 118 H120 L130 116 H230")
    d.stroke("cliff2", "M-30 128 Q20 124 60 132 Q110 126 150 134 Q190 126 230 130 M-30 142 Q40 136 90 146 Q140 138 230 144", 1.6, line=False)
    d.band("sand", "M-30 150 Q100 144 230 150")
    d.band("sea", f"M-30 {W} Q60 156 100 {W} T230 {W}")
    d.stroke("light", f"M-30 {W + 2} Q60 158 100 {W + 2} T230 {W + 2}", 2)
    d.band("sea2", waves(W + 20, 2, 24), line=False)
    d.stroke("light", "M30 176 h16 M120 182 h20", 2)
    paraglider(d, 56, 42)
    paraglider(d, 150, 34, .7, "hero2")
    paraglider(d, 88, 64, .55, "light")


# ================================================================ CARTAGENA
def cartagena(d: Drawing):
    W = 156
    d.disc("glow", 154, 54, 16)
    # Bocagrande towers across the bay
    d.band("far", roofline(110, [(130, 0), (8, 22), (10, 34), (8, 28), (10, 40), (8, 26), (10, 32), (60, 0)]), line=False)

    def front(dd):
        B = W - 22
        # cathedral bell tower with its dome
        x = 84
        dd.shape("ochre", poly((x - 9, B), (x - 9, 74), (x + 9, 74), (x + 9, B)))
        dd.shape("ochre", poly((x - 7, 74), (x - 7, 62), (x + 7, 62), (x + 7, 74)))
        dd.marks("dark", " ".join(f"M{x + o} 72 V66 Q{x + o + 1.6} 63.5 {x + o + 3.2} 66 V72Z" for o in (-5, 1.8)))
        dd.shape("terra", f"M{x - 8} 62 Q{x - 8} 48 {x} 46 Q{x + 8} 48 {x + 8} 62Z", spot=True)
        dd.shape("terra", rrect(x - 1.6, 40, 3.2, 6, 1), shadow=False)
        # Torre del Reloj: yellow clock tower
        x = 124
        dd.shape("yel", poly((x - 12, B), (x - 12, 102), (x + 12, 102), (x + 12, B)))
        dd.shape("yel", poly((x - 8, 102), (x - 8, 88), (x + 8, 88), (x + 8, 102)))
        dd.marks("light", circle(x, 95, 4.2))
        dd.marks("dark", f"M{x} 95 V92.2 M{x} 95 H{x + 2}" if not dd.paper else circle(x, 95, .8))
        dd.shape("yel", poly((x - 6, 88), (x - 6, 78), (x + 6, 78), (x + 6, 88)))
        dd.shape("terra", f"M{x - 7} 78 Q{x} 66 {x + 7} 78Z", spot=True)
        dd.marks("dark", f"M{x - 4} {B} V{B - 14} Q{x} {B - 20} {x + 4} {B - 14} V{B}Z")
        # colourful colonial houses with balconies
        row = [(10, 30, "c1"), (34, 24, "c2"), (54, 28, "c3"), (96, 22, "c1"), (138, 30, "c2"), (160, 24, "c3"), (182, 28, "c1")]
        for x0, h, role in row:
            w = 22 if x0 != 96 else 16
            dd.shape(role, poly((x0, B), (x0, B - h), (x0 + w, B - h), (x0 + w, B)))
            dd.shape("terra", poly((x0 - 1.5, B - h), (x0 + w / 2, B - h - 5), (x0 + w + 1.5, B - h)), shadow=False)
            dd.shape("wood", rrect(x0 + 2, B - h * .6, w - 4, 3, .6), shadow=False, line=False)
            dd.marks("dark", " ".join(f"M{x0 + o} {B - h * .6:.1f} V{B - h * .6 - 6:.1f} H{x0 + o + 3} V{B - h * .6:.1f}Z" for o in range(4, int(w) - 4, 7)))
    front(d)
    # the city wall with a garita (sentry box)
    d.band("wall", f"M-30 {W - 22} H230")
    d.stroke("wall2", f"M-30 {W - 14} H230 M-30 {W - 6} H230", 1.2, line=False)
    x = 46
    d.shape("wall", f"M{x - 8} {W - 20} V{W - 36} H{x + 8} V{W - 20}Z")
    d.shape("wall", f"M{x - 9} {W - 36} Q{x} {W - 50} {x + 9} {W - 36}Z")
    d.shape("wall", circle(x, W - 49, 2), shadow=False)
    d.marks("dark", rrect(x - 1.6, W - 32, 3.2, 6, 1.4))
    palm(d, 176, W - 10, 46, 4)
    water(d, W, deep=True, ripples=[(30, 170, 18), (110, 176, 24)])


# ================================================================ concepts
CONCEPTS = [
    city_concept("sky-newyork", "skyline-new-york", "New York", new_york,
                 {**COPPER, "steel": "#C9CED6", "ground": "#8BA27A"},
                 checks=[("steel", "sky"), ("cu", "sea"), ("steel", "glow")],
                 fixes={"steel": ["#AEB6C2", "#E6E9EE"]}),
    city_concept("sky-sanfrancisco", "skyline-san-francisco", "San Francisco", san_francisco,
                 {"gg": "#C0362C", "gg2": "#8E2620", "stone": "#E9E4DA", "stone2": "#C2BAAA", "hill": "#6E8F5E"},
                 checks=[("gg", "sky"), ("stone", "mid"), ("stone", "far")],
                 fixes={"far": ["#B7C6CF", "mid", "near"]}),
    city_concept("sky-chicago", "skyline-chicago", "Chicago", chicago,
                 {"b1": "#3A4252", "b2": "#262C38", "stone": "#E6E2DA", "stone2": "#C2BDB3", "bridge": "#3F6A5A"},
                 checks=[("stone", "mid"), ("stone", "far"), ("bridge", "sea")]),
    city_concept("sky-toronto", "skyline-toronto", "Toronto", toronto, CN,
                 checks=[("concrete", "sky"), ("concrete", "glow"), ("concrete", "far"), ("dome", "mid")],
                 fixes={"sky": ["sky2"]}),
    city_concept("sky-rio", "skyline-rio", "Rio de Janeiro", rio, RIO,
                 checks=[("forest", "sky"), ("rock", "sky"), ("rock", "glow"), ("statue", "sky"), ("forest", "glow")],
                 fixes={"glow": ["glow2", "pop", "hero2"], "statue": ["#BDB6A8", "#A39C90"]}),
    city_concept("sky-losangeles", "skyline-los-angeles", "Los Angeles", los_angeles,
                 {"stone": "#E6DFD0", "stone2": "#BFB5A3", "palm": "#2F4A3A", "road": "#5A5E66"},
                 checks=[("stone", "mid"), ("palm", "sky"), ("palm", "glow"), ("palm", "near")],
                 fixes={"near": ["mid", "deep"]}),
    city_concept("sky-seattle", "skyline-seattle", "Seattle", seattle,
                 {"mtn": "#9AA9BC", "mtn2": "#7E8DA2", "snow": "#F5F8FB", "stone": "#E8E2D6", "wheel": "#F3F1EC", "pier": "#6B5A4C", "hull": "#2F7D5A"},
                 checks=[("mtn", "sky"), ("far", "mtn"), ("b3", "mtn"), ("b1", "mtn"), ("wheel", "sea"), ("stone", "mid")],
                 fixes={"far": ["#C9D3DC", "sky2", "mid", "#6F8296"], "wheel": ["light"]}),
    city_concept("sky-lasvegas", "skyline-las-vegas", "Las Vegas", las_vegas,
                 {"tw": "#E9E3D6", "tw2": "#C4BBA9", "pyr": "#2E3440", "pyr2": "#1E232C", "gold": "#C8913E", "gold2": "#9C6B2A", "palm": "#2F4A3A"},
                 checks=[("tw", "glow"), ("tw", "mid"), ("gold", "glow"), ("gold", "mid"), ("pyr", "mid"), ("tw", "sky"), ("palm", "ground")],
                 fixes={"glow": ["pop", "glow2", "near"], "tw": ["#C9C0B0", "#B7AD9B", "#A9B3C2", "#98A3B3", "#8C96A6", "#7F8A9A"]}),
    city_concept("sky-miami", "skyline-miami", "Miami", miami,
                 {"b1": "#2F5F7A", "b2": "#244A60", "b3": "#5E9BB5", "lit1": "#F28FAD", "lit2": "#7FD8CB", "cream": "#EFE3C8", "terra": "#C8643E", "palm": "#2F5E45"},
                 checks=[("cream", "mid"), ("terra", "sky"), ("palm", "sea")],
                 fixes={"b3": ["#7FB3C8", "b1"]}),
    city_concept("sky-neworleans", "skyline-new-orleans", "New Orleans", new_orleans,
                 {"stone": "#EDE6D8", "stone2": "#C2B8A6", "slate": "#3A4252", "dome": "#D8DCE2", "dome2": "#A9B0BA", "truss": "#7D8796", "hull": "#2B2D42", "wheel": "#C8463A", "sea": "#5A8C8A", "sea2": "#43706E"},
                 checks=[("stone", "mid"), ("dome", "mid"), ("dome", "far"), ("slate", "sky"), ("slate", "glow"), ("light", "sea")],
                 fixes={"dome": ["#B9C0CA", "#9CA4B0"], "slate": ["#5A6478", "#6B7488"]}),
    city_concept("sky-boston", "skyline-boston", "Boston", boston,
                 {"brick": "#A65A44", "stone": "#EDE6D8", "gold": "#E8B33A", "glass": "#8FB5D3", "glass2": "#6F98BA", "cable": "#EEF0F2"},
                 checks=[("glass", "sky"), ("glass", "mid"), ("cable", "sky"), ("cable", "mid"), ("gold", "mid"), ("brick", "mid")],
                 fixes={"glass": ["#6F98BA", "#5B86AA"], "cable": ["#C9C0B0", "#B7AD9B", "#A9B3C2", "#98A3B3", "#8C96A6", "#7F8A9A"], "brick": ["#7E3F32", "#C2705A"], "gold": ["#F6D06A", "#FFD95E"]}),
    city_concept("sky-washington", "skyline-washington", "Washington, D.C.", washington,
                 {"stone": "#EFEAE0", "stone2": "#C9C0B0", "blossom": "#F4A7C0", "blossom2": "#FFFFFF", "trunk": "#5A4038", "grass": "#6E9E52"},
                 checks=[("stone", "sky"), ("stone", "glow"), ("stone", "mid"), ("blossom", "sea"), ("blossom", "sky")],
                 fixes={"stone": ["#C9C0B0", "#B7AD9B", "#A9B3C2", "#98A3B3", "#8C96A6", "#7F8A9A"], "blossom": ["#E57FA3", "#D0668D"], "glow": ["glow2", "pop"]}),
    city_concept("sky-nashville", "skyline-nashville", "Nashville", nashville,
                 {"bridge": "#2E3440"},
                 checks=[("bridge", "sea")]),
    city_concept("sky-vancouver", "skyline-vancouver", "Vancouver", vancouver,
                 {"b1": "#2F6670", "b2": "#244E56", "b3": "#6FA6AE", "mtn": "#6F8798", "snow": "#F5F8FB", "tree": "#2E5238",
                  "pierv": "#8A8F96", "sail": "#FBFBF8", "sail2": "#C9CDD3"},
                 checks=[("mtn", "sky"), ("far", "mtn"), ("b3", "mtn"), ("sail", "sea"), ("sail", "mid"), ("tree", "mid")],
                 fixes={"far": ["#C9D3DC", "sky2", "mid"], "b3": ["#8EC0C6", "b1"]}),
    city_concept("sky-montreal", "skyline-montreal", "Montreal", montreal,
                 {"mtnr": "#5E8B5A", "cross": "#FFFFFF", "copper": "#5FA38C", "copper2": "#3F7D6A", "stade": "#E8E4DC", "stade2": "#B8B2A6",
                  "isle": "#6E9E52", "bio": "#C9D2DA", "bio2": "#8B98A6"},
                 checks=[("mtnr", "sky"), ("far", "mtnr"), ("stade", "mid"), ("stade", "sky"), ("copper", "sky"), ("bio", "sea")],
                 fixes={"far": ["#C9D3DC", "sky2", "mid"], "stade": ["#C9C0B0", "#B7AD9B", "#A9B3C2", "#98A3B3", "#8C96A6", "#7F8A9A"]}),
    city_concept("sky-mexicocity", "skyline-mexico-city", "Mexico City", mexico_city,
                 {"mtn": "#8E9CB0", "snow": "#F5F8FB", "stone": "#E6DFD0", "stone2": "#BFB5A3", "gold": "#E8B33A", "jac": "#9B7BC8", "road": "#5A5E66", "trunk": "#5A4038"},
                 checks=[("mtn", "sky"), ("far", "mtn"), ("gold", "sky"), ("stone", "mid"), ("jac", "near")],
                 fixes={"far": ["#C9D3DC", "sky2", "mid", "#6F8296", "#5F7088"], "gold": ["#D19A2A", "#B8801E"], "glow": ["glow2", "pop", "light"], "jac": ["#7A5AA8", "#B39AE0"]}),
    city_concept("sky-havana", "skyline-havana", "Havana", havana,
                 {"stone": "#EDE6D8", "stone2": "#C2B8A6", "rock": "#9C8670", "c1": "#F2A7A0", "c2": "#F6D28B", "c3": "#8FD3C8",
                  "wall": "#D9CDB6", "wall2": "#B5A68E", "car": "#E85D75"},
                 checks=[("stone", "sky"), ("stone", "glow"), ("stone", "far"), ("wall", "sea"), ("car", "wall")],
                 fixes={"stone": ["#C9C0B0", "#B7AD9B", "#A9B3C2", "#98A3B3", "#8C96A6", "#7F8A9A"], "glow": ["pop", "glow2"], "far": ["#C9D3DC", "mid"]}),
    city_concept("sky-buenosaires", "skyline-buenos-aires", "Buenos Aires", buenos_aires,
                 {"stone": "#E2D6C0", "stone2": "#BBAE96", "obel": "#F4F1EA", "obel2": "#CFC8BA", "crane": "#C8463A", "bridge": "#F4F4F2", "cable2": "#D8DADE"},
                 checks=[("obel", "sky"), ("obel", "mid"), ("obel", "far"), ("stone", "mid"), ("crane", "sea"), ("bridge", "sea")],
                 fixes={"obel": ["#C9C0B0", "#B7AD9B", "#A9B3C2", "#98A3B3", "#8C96A6", "#7F8A9A"]}),
    city_concept("sky-lima", "skyline-lima", "Lima", lima,
                 {"cliff": "#A27B5C", "cliff2": "#7F5E46", "sand": "#D9BF95", "lh": "#F4F1EA", "lh2": "#C8463A"},
                 checks=[("cliff", "sky"), ("cliff", "far"), ("lh", "sky"), ("lh", "glow"), ("cliff", "glow")],
                 fixes={"lh": ["#C9C0B0", "#B7AD9B", "#A9B3C2", "#98A3B3", "#8C96A6", "#7F8A9A"], "glow": ["glow2", "pop"]}),
    city_concept("sky-cartagena", "skyline-cartagena", "Cartagena", cartagena,
                 {"ochre": "#D9A441", "terra": "#C0583A", "yel": "#F2C94C", "c1": "#E86F5A", "c2": "#4FB3BF", "c3": "#F2A541", "wood": "#7A4E2D",
                  "wall": "#CDB894", "wall2": "#A8926B", "palm": "#2F5E45"},
                 checks=[("ochre", "sky"), ("terra", "sky"), ("yel", "sky"), ("wall", "sea"), ("terra", "glow")],
                 fixes={"yel": ["#E0A93A", "#D9973A"], "ochre": ["#B88234", "#9C6B2A"], "glow": ["glow2", "pop"]}),
]
