"""Snakes, spiders and a scorpion: a bold portrait and a habitat scene for each of eleven creatures.

Kept friendly on purpose: big round eyes with highlights, soft smiles, chunky shapes.
"""
import math

from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group  # noqa: F401

_uid = [0]


# ================================================================ helpers (some copied from animals_asia)
def _id(prefix):
    _uid[0] += 1
    return f"{prefix}{_uid[0]}"


def clipped(d: Drawing, path: str, fn):
    """Draw fn() clipped to `path` (blotches on a python, diamonds on a rattlesnake)."""
    cid = _id("crtaclip")
    tag = f'<clipPath id="{cid}"><path d="{path}"/></clipPath><g clip-path="url(#{cid})">'
    d.raw(tag, tag)
    fn()
    d.raw("</g>", "</g>")


def flip(d: Drawing, fn, cx=100):
    group(d, f"translate({2 * cx} 0) scale(-1 1)", fn)


def leaf(x, y, length, width, angle):
    """A pointed leaf from (x, y) pointing at `angle` degrees (0 = right, -90 = up)."""
    a = math.radians(angle)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    tx, ty = x + ux * length, y + uy * length
    c1 = (x + ux * length * 0.35 + px * width, y + uy * length * 0.35 + py * width)
    c2 = (x + ux * length * 0.35 - px * width, y + uy * length * 0.35 - py * width)
    return (f"M{x:.1f} {y:.1f} Q{c1[0]:.1f} {c1[1]:.1f} {tx:.1f} {ty:.1f} "
            f"Q{c2[0]:.1f} {c2[1]:.1f} {x:.1f} {y:.1f}Z")


def foliage(d: Drawing, pts, role="near", length=60, width=15, line=False):
    for x, y, a in pts:
        d.shape(role, leaf(x, y, length, width, a), line=line)


def veined(d: Drawing, x, y, length, width, angle, role="near", vein="light", line=True):
    """A big leaf with a midrib."""
    d.shape(role, leaf(x, y, length, width, angle), line=line)
    a = math.radians(angle)
    d.stroke(vein, f"M{x:.1f} {y:.1f} L{x + math.cos(a) * length * 0.85:.1f} {y + math.sin(a) * length * 0.85:.1f}", 1.4, line=False)


def blades(d: Drawing, xs, y, h, role="near", w=3.2, lean=0, shadow=False, line=False):
    """Tall grass blades rising from y."""
    for i, x in enumerate(xs):
        hh = h * (0.7 + 0.3 * ((i * 7) % 5) / 4)
        a = -90 + lean + ((i * 37) % 21 - 10)
        d.shape(role, leaf(x, y, hh, w, a), shadow=shadow, line=line)


def blob(pts):
    """A smooth closed shape through the midpoints of a polygon."""
    n = len(pts)
    mids = [((pts[i][0] + pts[(i + 1) % n][0]) / 2, (pts[i][1] + pts[(i + 1) % n][1]) / 2) for i in range(n)]
    s = f"M{mids[-1][0]:.1f} {mids[-1][1]:.1f}"
    for i in range(n):
        s += f" Q{pts[i][0]:.1f} {pts[i][1]:.1f} {mids[i][0]:.1f} {mids[i][1]:.1f}"
    return s + "Z"


def tufty(cx, cy, rx, ry, n=24, k=0.14, rot=0.0):
    """A shaggy ellipse: n pointed, slightly swept tufts of fur round the edge."""
    s = ""
    for i in range(n):
        a = rot + 2 * math.pi * i / n
        b = rot + 2 * math.pi * (i + 1) / n
        p0 = (cx + rx * math.cos(a), cy + ry * math.sin(a))
        ta = a + (b - a) * 0.75
        tip = (cx + rx * (1 + k) * math.cos(ta), cy + ry * (1 + k) * math.sin(ta))
        ca = a + (b - a) * 0.3
        c1 = (cx + rx * (1 + k * 0.7) * math.cos(ca), cy + ry * (1 + k * 0.7) * math.sin(ca))
        p1 = (cx + rx * math.cos(b), cy + ry * math.sin(b))
        if i == 0:
            s += f"M{p0[0]:.1f} {p0[1]:.1f}"
        s += f" Q{c1[0]:.1f} {c1[1]:.1f} {tip[0]:.1f} {tip[1]:.1f} L{p1[0]:.1f} {p1[1]:.1f}"
    return s + "Z"


def ink(d: Drawing, role, path, shadow=True):
    """A shape that is solid in both styles (glossy black bodies): papercut paper, line ink."""
    if d.paper:
        d.shape(role, path, shadow=shadow)
    else:
        d.marks(role, path)


def stars(d: Drawing, pts, role="light"):
    s = "".join(f"M{x} {y - r} L{x + r * .3} {y - r * .3} L{x + r} {y} L{x + r * .3} {y + r * .3} L{x} {y + r} "
                f"L{x - r * .3} {y + r * .3} L{x - r} {y} L{x - r * .3} {y - r * .3}Z" for x, y, r in pts)
    d.marks(role, s)


# ---------------------------------------------------------------- smooth tubes (snake bodies)
def smooth(pts, n=10):
    """Catmull-Rom curve through pts, as a dense list of points."""
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[j] + (p2[j] - p0[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (3 * p1[j] - p0[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(tuple(pts[-1]))
    return out


def _frames(pts):
    s = smooth(pts)
    L = [0.0]
    for a, b in zip(s, s[1:]):
        L.append(L[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    tot = L[-1] or 1
    fr = []
    for i, (x, y) in enumerate(s):
        a, b = s[max(i - 1, 0)], s[min(i + 1, len(s) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy) or 1
        fr.append((x, y, dx / n, dy / n, L[i] / tot))
    return fr


def tube(pts, prof):
    """Closed outline of a body along pts; prof(t) gives the full width at t (0 = first point)."""
    fr = _frames(pts)
    left = [(x + dy * prof(t) / 2, y - dx * prof(t) / 2) for x, y, dx, dy, t in fr]
    right = [(x - dy * prof(t) / 2, y + dx * prof(t) / 2) for x, y, dx, dy, t in fr]
    x, y, dx, dy, t = fr[-1]
    w = prof(t) / 2
    cap = [(x + dx * w * 0.7 + dy * w * 0.7, y + dy * w * 0.7 - dx * w * 0.7), (x + dx * w, y + dy * w),
           (x + dx * w * 0.7 - dy * w * 0.7, y + dy * w * 0.7 + dx * w * 0.7)]
    ring = left + cap + right[::-1]
    return "M" + " L".join(f"{a:.1f} {b:.1f}" for a, b in ring) + "Z"


def centre(pts):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in smooth(pts))


def at(pts, t):
    """Point and direction (degrees) at fraction t along the curve."""
    fr = _frames(pts)
    best = min(fr, key=lambda f: abs(f[4] - t))
    x, y, dx, dy, _ = best
    return x, y, math.degrees(math.atan2(dy, dx))


def taper(w, tail=0.35, tip=1.5, head=1.0):
    """Width profile: thin tail tip at t=0, full width by `tail`, slight neck at the head end."""
    def prof(t):
        if t < tail:
            k = t / tail
            return tip + (w - tip) * (1 - (1 - k) ** 2)
        return w * (1 - (1 - head) * max(0, (t - 0.9) / 0.1))
    return prof


def pattern(d: Drawing, body, pts, role, w, dash, offset=0, cap="round"):
    """Dashed markings along the body centreline, clipped to the body (papercut only)."""
    if not d.paper:
        return
    clipped(d, body, lambda: d.raw(f'<path d="{centre(pts)}" fill="none" stroke="{d.c[role]}" stroke-width="{w}" '
                                   f'stroke-dasharray="{dash}" stroke-dashoffset="{offset}" stroke-linecap="{cap}"/>'))


def place(d: Drawing, x, y, ang, fn, s=1.0):
    """Draw fn() in a local frame at (x, y) pointing along ang, never upside down."""
    flipy = -1 if math.cos(math.radians(ang)) < 0 else 1
    group(d, f"translate({x:.1f} {y:.1f}) rotate({ang:.1f}) scale({s} {s * flipy})", fn)


# Snake heads, drawn pointing +x with the neck at the origin (local frame).
HEAD_ROUND = "M-8 -8 C2 -12 16 -13 25 -9 C32 -6 35 -2 35 2 C35 6 31 9 23 10 C13 11 2 11 -8 8Z"
HEAD_VIPER = "M-8 -8 C-2 -15 14 -17 25 -11 C32 -7 35 -3 35 1 C35 5 31 9 23 11 C12 15 -2 14 -8 8Z"
HEAD_COFFIN = "M-8 -7 C4 -10 20 -11 30 -8 C36 -6 39 -2 39 1 C39 4 35 7 28 8 C18 9 4 9 -8 7Z"


def snake_head(d: Drawing, path=HEAD_ROUND, role="hero", lip="hero2", eye_x=17, eye_y=-3, eye_r=5.2, tongue=True,
               lashes=False, gape=False, iris="light", smile=True):
    if gape:
        # mouth open: the inky black inside is the black mamba's signature
        if tongue:
            d.stroke("pop", "M28 7 L46 9 M46 9 L51 5 M46 9 L50 14", 2.2)
        d.shape(role, "M-8 4 C2 6 18 9 31 11 C35 11.5 36 14 33 15 C22 16 6 13.5 -8 10Z")
        ink(d, "mark", "M8 3 L38 0.5 C38.5 5 36 9 32 11.5 L12 8.5Z", shadow=False)
        if tongue and d.paper:
            d.stroke("pop", "M22 8 L34 9", 2.2)
        d.shape(role, "M-8 -7 C0 -11 14 -13 26 -11 C34 -10 40 -6 41 -2 C41 0 39 1 36 1 C28 1 18 2 8 3 C2 4 -4 5 -8 5Z")
        d.marks("mark", circle(35, -5, 1.1))
    else:
        if tongue:
            d.stroke("pop", "M30 3 L40 4 M40 4 L46 0 M40 4 L46 8", 2.2)
        d.shape(role, path)
        if lip and d.paper:
            d.shape(lip, "M-6 7 C6 10 18 10 26 9 C31 8 34 5 35 2 C30 6 22 7 12 7 C4 7 -2 6 -6 5Z", shadow=False)
        if smile:
            d.stroke("mark", "M33 4 C29 6 25 6 21 5", 1.5)
        d.marks("mark", circle(31, -3, 1.1))
    if lashes:
        # a brow of soft spiky scales over the eye
        d.shape(role, f"M{eye_x - 8} {eye_y - 4} L{eye_x - 10} {eye_y - 11} L{eye_x - 5} {eye_y - 7} L{eye_x - 4} {eye_y - 14} "
                      f"L{eye_x} {eye_y - 8} L{eye_x + 3} {eye_y - 14} L{eye_x + 4} {eye_y - 7} L{eye_x + 9} {eye_y - 11} "
                      f"L{eye_x + 8} {eye_y - 3}Z", shadow=False)
    d.shape(iris, circle(eye_x, eye_y, eye_r), shadow=False)
    d.marks("mark", circle(eye_x + 0.8, eye_y + 0.3, eye_r * 0.62))
    d.marks("light", circle(eye_x + 2.2, eye_y - 1.4, eye_r * 0.26))


def snake(d: Drawing, pts, w, head_fn, prof=None, marks=None, spot=False, s=1.0, belly=None):
    """A snake along pts (tail first, head last). marks(body) adds the pattern."""
    prof = prof or taper(w)
    body = tube(pts, prof)
    d.shape("hero", body, spot=spot)
    if belly:
        pattern(d, body, pts, belly[0], belly[1], belly[2])
    if marks:
        marks(body)
    x, y, a = at(pts, 1.0)
    place(d, x, y, a, head_fn, s)
    return body


def coil(d: Drawing, cx, cy, rx, ry, w, role="hero", marks=None, spot=False):
    """One ring of a coiled snake, seen slightly from above."""
    p = ellipse(cx, cy, rx, ry)
    d.limb(role, p, w, spot=spot)
    if marks and d.paper:
        marks(p)


def dashes(d: Drawing, p, role, w, dash, offset=0, cap="round"):
    if d.paper:
        d.raw(f'<path d="{p}" fill="none" stroke="{d.c[role]}" stroke-width="{w}" stroke-dasharray="{dash}" '
              f'stroke-dashoffset="{offset}" stroke-linecap="{cap}"/>')


def branch(d: Drawing, path, w=14, role="bark", knots=()):
    d.limb(role, path, w)
    for x, y in knots:
        d.stroke("bark2", f"M{x - 4} {y} q4 -3 8 0", 1.6, line=False)


def saguaro(d: Drawing, x, y, h=80, s=1.0, role="cactus", line=True):
    def draw():
        d.limb(role, f"M0 0 V{-h}", 14, spot=False) if (line or d.paper) else None
        d.limb(role, f"M0 {-h * 0.45} H-16 Q-22 {-h * 0.45} -22 {-h * 0.55} V{-h * 0.8}", 10) if (line or d.paper) else None
        d.limb(role, f"M0 {-h * 0.6} H14 Q20 {-h * 0.6} 20 {-h * 0.7} V{-h * 0.92}", 10) if (line or d.paper) else None
        d.stroke("cactus2", f"M-3 {-h + 6} V-4 M3 {-h + 6} V-4", 1.4, line=False)
    group(d, f"translate({x} {y}) scale({s})", draw)


def rays(d: Drawing, cx, cy, r0, r1, n=12, role="light", w=2, a0=0):
    s = ""
    for i in range(n):
        a = math.radians(a0 + 360 * i / n)
        s += f"M{cx + r0 * math.cos(a):.1f} {cy + r0 * math.sin(a):.1f} L{cx + r1 * math.cos(a):.1f} {cy + r1 * math.sin(a):.1f} "
    d.stroke(role, s, w, line=False)


def walk(points, spacing, offset=0.0):
    """Points every `spacing` along a dense polyline: (x, y, angle in degrees)."""
    out, acc, nxt = [], 0.0, offset
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        seg = math.hypot(x1 - x0, y1 - y0)
        while seg and nxt <= acc + seg:
            k = (nxt - acc) / seg
            out.append((x0 + (x1 - x0) * k, y0 + (y1 - y0) * k, math.degrees(math.atan2(y1 - y0, x1 - x0))))
            nxt += spacing
        acc += seg
    return out


def ring_pts(cx, cy, rx, ry, n=90):
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n + 1)]


def diamond(x, y, ang, a, b):
    r = math.radians(ang)
    ux, uy, px, py = math.cos(r), math.sin(r), -math.sin(r), math.cos(r)
    return (f"M{x + ux * a:.1f} {y + uy * a:.1f} L{x + px * b:.1f} {y + py * b:.1f} "
            f"L{x - ux * a:.1f} {y - uy * a:.1f} L{x - px * b:.1f} {y - py * b:.1f}Z")


def diamonds(d: Drawing, points, spacing, a, b, offset=0.0, edge="light", fill="blotch"):
    """Diamondback markings: pale-edged dark diamonds along a body."""
    spots = walk(points, spacing, offset)
    if d.paper:
        d.marks(edge, "".join(diamond(x, y, g, a + 2, b + 2) for x, y, g in spots))
    d.marks(fill, "".join(diamond(x, y, g, a, b) for x, y, g in spots))


# ================================================================ GREEN TREE PYTHON
TREEPY = {"hero": "#3FA34D", "hero2": "#C9E66B", "mark": "#173D1E", "light": "#FFFFFF", "pop": "#E0475B",
          "bark": "#8A5A3B", "bark2": "#5E3B25"}


def treepython_coils(d: Drawing, spot=True):
    """The famous pose: saddle loops draped over a branch, head resting on the coils in the middle."""
    branch(d, "M-30 120 C40 118 160 114 230 110", 18, knots=[(20, 119), (180, 112)])
    for p, off in [("M58 112 C48 152 92 156 88 112", 0), ("M116 112 C112 152 156 150 148 110", 6)]:
        d.limb("hero", p, 16, spot=spot)
        dashes(d, p, "light", 2.4, "2 17", off)
    for cx, cy, rx, ry, w, off in [(102, 106, 56, 11, 17, 0), (102, 95, 40, 9, 16, 9)]:
        p = ellipse(cx, cy, rx, ry)
        d.limb("hero", p, w)
        dashes(d, p, "light", 2.4, "2 17", off)
    neck = [(136, 96), (130, 84), (112, 80), (94, 82)]
    body = tube(neck, lambda t: 15)
    d.shape("hero", body)
    pattern(d, body, neck, "light", 2.4, "2 17", 4)
    place(d, 94, 82, 182, lambda: snake_head(d, HEAD_VIPER, eye_r=5.8))


def treepython_portrait(d: Drawing):
    foliage(d, [(-6, 46, 20), (-4, 100, -5), (206, 46, 160), (204, 100, 185)], "near", 54, 13)
    foliage(d, [(2, 158, -20), (198, 162, -160)], "mid", 48, 12)
    group(d, "translate(100 104) scale(1.32) translate(-100 -110)", lambda: treepython_coils(d))


def treepython_rainforest(d: Drawing):
    d.band("far", hills(150, 10))
    d.raw('<g opacity=".55">', "")
    d.band("light", waves(146, 3, 40), shadow=False, line=False)
    d.raw("</g>", "")
    d.stroke("near", "M30 -10 Q36 40 28 92 M178 -10 Q170 30 176 70", 2.4)
    foliage(d, [(30, 60, 150), (28, 80, 30), (176, 50, 20), (176, 66, 160)], "near", 18, 6)
    foliage(d, [(-10, 20, 20), (210, 20, 160), (40, -6, 80), (160, -6, 100)], "mid", 52, 13)
    d.band("mid", hills(176, 6, 20))
    for x, y, a in [(-4, 186, -40), (204, 186, -140), (40, 200, -70), (160, 200, -110)]:
        veined(d, x, y, 50, 13, a, "near")
    group(d, "translate(100 108) scale(.82) translate(-100 -112)", lambda: treepython_coils(d))
    for x, y, a in [(150, 196, -100), (60, 196, -80)]:
        veined(d, x, y, 40, 11, a, "deep", line=False)


# ================================================================ BURMESE PYTHON
BURMESE = {"hero": "#D8B47A", "hero2": "#EFDDB4", "mark": "#3A2716", "blotch": "#7A5130", "light": "#FFFFFF", "pop": "#D8433A"}


def burmese_ring(d: Drawing, cx, cy, rx, ry, w=17, off=0, spot=False):
    p = ellipse(cx, cy, rx, ry)
    d.limb("hero", p, w, spot=spot)
    dashes(d, p, "mark", w * 0.72, "13 8", off)
    dashes(d, p, "blotch", w * 0.5, "10 11", off - 1.5)


def burmese_portrait(d: Drawing):
    foliage(d, [(-6, 50, 15), (-4, 104, -5), (206, 50, 165), (204, 104, 185)], "near", 50, 12)
    d.band("ground", hills(172, 3))
    burmese_ring(d, 100, 160, 66, 18, 19, 0, spot=True)
    burmese_ring(d, 100, 146, 52, 15, 18, 6)
    burmese_ring(d, 100, 134, 36, 11, 17, 3)
    neck = [(126, 132), (138, 116), (126, 96), (98, 86), (82, 70), (90, 54)]
    body = tube(neck, lambda t: 17 - 3 * t)
    d.shape("hero", body)
    pattern(d, body, neck, "mark", 12, "12 7", 4)
    pattern(d, body, neck, "blotch", 8, "10 9", 3)
    x, y, a = at(neck, 1.0)

    def head():
        snake_head(d, HEAD_ROUND, eye_r=5.8)
        d.marks("blotch", "M-4 -9 L12 -11 L22 -9 L12 -7 L2 -7Z")
    place(d, x, y, 10, head, 1.25)


def burmese_river(d: Drawing):
    d.disc("glow", 152, 56, 20)
    d.band("far", "M-30 104 Q0 92 20 98 Q40 84 60 96 Q84 86 104 98 Q130 84 150 96 Q176 88 200 98 Q216 92 230 96")
    for x in (22, 60, 104, 150, 196):
        d.stroke("far", f"M{x} 98 V112", 2, line=False)
    d.band("mid", "M-30 112 C30 108 170 108 230 112")
    d.band("near", waves(150, 3, 44), line=False)
    pts = [(18, 150), (44, 132), (74, 146), (104, 160), (136, 142), (150, 118), (146, 96)]
    body = tube(pts, taper(16, 0.3))
    d.shape("hero", body, spot=True)
    pattern(d, body, pts, "mark", 12, "12 7", 0)
    pattern(d, body, pts, "blotch", 8, "10 9", -1)
    d.raw('<g opacity=".85">', "")
    for x, y in [(30, 144), (88, 156), (118, 156)]:
        d.shape("mid", ellipse(x, y + 4, 12, 4), shadow=False, line=False)
    d.raw("</g>", "")
    d.stroke("light", "M20 160 q8 -4 16 0 M82 170 q8 -4 16 0 M120 168 q8 -4 16 0 M160 150 q8 -4 16 0 M40 178 q8 -4 16 0 M140 182 q8 -4 16 0", 2.2)
    x, y, a = at(pts, 1.0)
    place(d, x, y, a, lambda: snake_head(d, HEAD_ROUND, eye_r=5.6))
    for px, py, a in [(-6, 190, -60), (8, 198, -30), (206, 190, -120), (194, 200, -150)]:
        d.shape("deep", leaf(px, py, 40, 7, a), shadow=False, line=False)


# ================================================================ RATTLESNAKE
RATTLE = {"hero": "#C9A36F", "hero2": "#EAD7A9", "mark": "#3D2B1C", "blotch": "#6E4E32", "light": "#F4E6C6", "pop": "#D8433A",
          "rattle": "#B08A5E", "cactus": "#4F8D5A", "cactus2": "#3A6E46"}


def rattle(d: Drawing, x, y, n=5, s=1.0, spot=True):
    """The rattle: a stack of rounded segments, tip up, with shake lines."""
    def draw():
        for i in range(n):
            ww = 9 - i * 0.7
            yy = -i * 7.5
            d.shape("rattle", f"M{-ww} {yy} C{-ww} {yy - 8} {ww} {yy - 8} {ww} {yy} C{ww} {yy + 4} {-ww} {yy + 4} {-ww} {yy}Z",
                    spot=spot and i % 2 == 0)
            d.stroke("mark", f"M{-ww + 2} {yy + 1} Q0 {yy + 3} {ww - 2} {yy + 1}", 1.2, line=False)
        d.stroke("mark", "M-15 -30 q-5 6 0 12 M-21 -34 q-6 9 0 18 M15 -30 q5 6 0 12 M21 -34 q6 9 0 18", 1.8)
    group(d, f"translate({x} {y}) scale({s})", draw)


def rattlesnake_coiled(d: Drawing, spot=True):
    # tail rising from the back of the coil, banded black and white just before the rattle
    tail = [(118, 150), (140, 140), (150, 118), (152, 96)]
    tb = tube(tail, lambda t: 14 - 5 * t)
    d.shape("hero", tb)
    pattern(d, tb, tail, "mark", 16, "5 5", -38, cap="butt")
    rattle(d, 152, 92, 5, 1.0, spot)
    for cx, cy, rx, ry, w, off in [(100, 160, 60, 16, 18, 0), (100, 146, 44, 13, 17, 7)]:
        d.limb("hero", ellipse(cx, cy, rx, ry), w)
        diamonds(d, ring_pts(cx, cy, rx, ry), 15, 6.5, w * 0.3, off)
    neck = [(78, 142), (66, 124), (74, 100), (92, 88), (88, 70)]
    body = tube(neck, lambda t: 17 - 2 * t)
    d.shape("hero", body)
    diamonds(d, smooth(neck), 15, 6.5, 5, 6)
    place(d, 88, 70, -10, lambda: snake_head(d, HEAD_VIPER, eye_r=5.6), 1.15)


def rattlesnake_portrait(d: Drawing):
    d.disc("glow", 58, 60, 26)
    d.band("ground", hills(168, 4))
    for x, y in [(30, 170), (170, 166)]:
        d.shape("blotch", f"M{x - 10} {y + 4} Q{x - 8} {y - 6} {x} {y - 7} Q{x + 9} {y - 6} {x + 10} {y + 4}Z", line=False)
    group(d, "translate(100 100) scale(1.25) translate(-100 -118)", lambda: rattlesnake_coiled(d))


def rattlesnake_desert(d: Drawing):
    d.disc("glow", 60, 64, 22)
    d.band("far", "M-30 120 L20 120 L26 100 L64 100 L70 120 L120 122 L126 108 L150 108 L156 122 L230 120")
    saguaro(d, 160, 150, 82, 1.0)
    saguaro(d, 34, 136, 50, 0.7)
    d.band("ground", hills(148, 4))
    for x, y in [(30, 162), (172, 170)]:
        d.shape("blotch", f"M{x - 9} {y + 4} Q{x - 7} {y - 5} {x} {y - 6} Q{x + 8} {y - 5} {x + 9} {y + 4}Z", line=False)
    group(d, "translate(96 126) scale(.8) translate(-100 -118)", lambda: rattlesnake_coiled(d))


# ================================================================ BLACK MAMBA
MAMBA = {"hero": "#7D7C68", "hero2": "#B9B69A", "mark": "#151515", "light": "#FFFFFF", "pop": "#D8433A",
         "mound": "#C48A55", "mound2": "#A06A3E"}


def mamba_raised(d: Drawing, spot=True):
    """Coiled base, then a tall slender S rising to the coffin-shaped head with its inky black mouth."""
    coil(d, 100, 168, 56, 12, 12, spot=spot)
    coil(d, 104, 158, 40, 9, 11)
    pts = [(66, 164), (58, 142), (76, 124), (118, 114), (128, 90), (106, 72), (90, 62)]
    d.shape("hero", tube(pts, lambda t: 12 - 0.5 * t))
    place(d, 90, 62, -14, lambda: snake_head(d, HEAD_COFFIN, eye_r=5.4, gape=True), 1.25)


def mamba_portrait(d: Drawing):
    blades(d, [-4, 8, 22, 36, 164, 178, 192, 204], 196, 70, "near", 5)
    blades(d, [14, 30, 170, 186], 196, 46, "mid", 4)
    d.band("ground", hills(180, 3))
    group(d, "translate(100 100) scale(1.12) translate(-100 -108)", lambda: mamba_raised(d))


def mamba_savanna(d: Drawing):
    d.disc("glow", 146, 84, 32)
    d.band("far", hills(140, 8))
    group(d, "translate(-62 18) scale(.6)", lambda: (
        d.limb("dark", "M152 184 L153 142 M153 142 L141 125 M153 142 L165 122", 5),
        d.shape("dark", "M116 124 Q138 104 166 108 Q190 111 192 124 Q160 130 116 124Z"),
        d.shape("dark", "M128 112 Q150 97 178 104 Q162 113 128 112Z", shadow=False)))
    mound = "M48 176 C54 150 56 120 66 96 C70 84 76 70 82 60 C86 54 90 56 92 62 C96 78 98 92 104 100 C110 92 114 96 116 104 C122 124 128 152 138 176Z"
    d.shape("mound", mound)
    d.stroke("mound2", "M70 110 Q74 130 68 160 M86 76 Q90 110 84 150 M112 112 Q118 136 120 166", 2, line=False)
    ink(d, "mark", ellipse(98, 130, 11, 8), shadow=False)
    d.band("ground", hills(172, 4))
    blades(d, [10, 22, 160, 176, 190], 186, 30, "near", 3.5)
    pts = [(98, 134), (112, 118), (124, 96), (112, 72), (118, 50)]
    d.shape("hero", tube(pts, lambda t: 11), spot=True)
    place(d, 118, 50, -10, lambda: snake_head(d, HEAD_COFFIN, eye_r=5.4, gape=True), 1.05)


# ================================================================ EYELASH VIPER
EYELASH = {"hero": "#F4C430", "hero2": "#FBE58A", "mark": "#3A2A10", "speck": "#C9771A", "light": "#FFFFFF", "pop": "#E0475B",
           "bark": "#7A5A3E", "bark2": "#56402B", "flower": "#E2453C", "flower2": "#F6D04D"}


def speckle_ring(d: Drawing, cx, cy, rx, ry, w, off=0):
    p = ellipse(cx, cy, rx, ry)
    dashes(d, p, "speck", 3, "0.1 9", off)


def eyelash_coil(d: Drawing, s_head=1.4, spot=True):
    """A tight coil on a branch, head resting on top facing left (local: branch at y=150)."""
    branch(d, "M-30 158 C40 154 140 148 230 140", 16, knots=[(30, 156), (168, 146)])
    for cx, cy, rx, ry, w, off in [(104, 140, 54, 13, 18, 0), (104, 128, 40, 11, 17, 4)]:
        d.limb("hero", ellipse(cx, cy, rx, ry), w, spot=spot and off == 0)
        speckle_ring(d, cx, cy, rx, ry, w, off)
    neck = [(136, 126), (134, 108), (114, 96), (94, 96)]
    body = tube(neck, lambda t: 17)
    d.shape("hero", body)
    pattern(d, body, neck, "speck", 3, "0.1 9", 0)

    def head():
        snake_head(d, HEAD_VIPER, eye_r=6, lashes=True)
        d.marks("speck", circle(4, -6, 1.2) + circle(8, 4, 1.2) + circle(26, -6, 1) + circle(-2, 2, 1.1))
    place(d, 94, 96, 184, head, s_head)


def eyelash_portrait(d: Drawing):
    foliage(d, [(-6, 40, 20), (-4, 96, -5), (206, 40, 160), (206, 96, 185), (2, 156, -25), (198, 160, -155)], "near", 52, 13)
    group(d, "translate(106 100) scale(1.2) translate(-100 -118)", lambda: eyelash_coil(d))


def heliconia(d: Drawing, x, y, s=1.0):
    """An upright heliconia: boat-shaped red bracts, tipped yellow, zigzagging up the stem."""
    def draw():
        nodes = [(0, 0), (6, -24), (-2, -46), (4, -66)]
        d.limb("near", "M0 90 L0 0 L6 -24 L-2 -46 L4 -66", 5)
        for i, (nx, ny) in enumerate(nodes):
            side = -1 if i % 2 == 0 else 1
            k = 1 - i * 0.12
            tx, ty = nx + side * 36 * k, ny - 26 * k
            p = (f"M{nx} {ny + 6} C{nx + side * 14 * k} {ny + 10} {nx + side * 32 * k} {ny + 2} {tx} {ty} "
                 f"C{nx + side * 24 * k} {ny - 12 * k} {nx + side * 10 * k} {ny - 8} {nx} {ny - 6}Z")
            d.shape("flower", p, spot=True)
            d.shape("flower2", f"M{tx} {ty} C{nx + side * 26 * k} {ny - 13 * k} {nx + side * 14 * k} {ny - 9} {nx + side * 4} {ny - 6} "
                               f"C{nx + side * 14 * k} {ny - 6 * k} {nx + side * 28 * k} {ny - 8 * k} {tx} {ty}Z", shadow=False)
    group(d, f"translate({x} {y}) scale({s})", draw)


def eyelash_heliconia(d: Drawing):
    d.band("far", hills(150, 8))
    for x, y, a in [(-10, 24, 30), (-6, 80, 5), (210, 30, 150), (210, 88, 175)]:
        veined(d, x, y, 66, 18, a, "mid")
    heliconia(d, 100, 158, 1.15)
    for x, y, a in [(-4, 170, -30), (204, 176, -150)]:
        veined(d, x, y, 60, 16, a, "near")
    d.band("deep", hills(190, 4), line=False)

    def viper():
        for cx, cy, rx, ry, w, off in [(104, 140, 34, 9, 13, 0), (104, 131, 24, 7, 12, 4)]:
            d.limb("hero", ellipse(cx, cy, rx, ry), w, spot=off == 0)
            speckle_ring(d, cx, cy, rx, ry, w, off)
        neck = [(124, 130), (124, 116), (110, 106), (94, 106)]
        body = tube(neck, lambda t: 12)
        d.shape("hero", body)
        pattern(d, body, neck, "speck", 2.6, "0.1 8", 0)
        place(d, 94, 106, 184, lambda: snake_head(d, HEAD_VIPER, eye_r=6, lashes=True), 1.0)
    group(d, "translate(0 -62)", viper)


# ================================================================ spider helpers
def pl(pts):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)


def legs(d: Drawing, specs, w, role="hero", band=None, band_at=(0.1, 0.32), band2=None, cx=100, spot=False, shadow=True):
    """Spider legs given for the left side (hip, knee, ..., foot); mirrored to the right about cx."""
    def draw():
        for pts in specs:
            d.limb(role, pl(pts), w, spot=spot, shadow=shadow)
            if band:
                (kx, ky), (fx, fy) = pts[1], pts[2]
                a, b = band_at
                d.limb(band, f"M{kx + (fx - kx) * a:.1f} {ky + (fy - ky) * a:.1f} L{kx + (fx - kx) * b:.1f} {ky + (fy - ky) * b:.1f}",
                       w + 0.4, spot=True, shadow=False)
            if band2:
                (hx, hy), (kx, ky) = pts[0], pts[1]
                d.limb(band2, f"M{hx + (kx - hx) * 0.55:.1f} {hy + (ky - hy) * 0.55:.1f} L{hx + (kx - hx) * 0.75:.1f} {hy + (ky - hy) * 0.75:.1f}",
                       w + 0.4, shadow=False)
    draw()
    flip(d, draw, cx)


def cute_eyes(d: Drawing, x1, x2, y, r=4.6, small=True, sclera="light"):
    """Two big glossy front eyes, plus a pair of little ones above."""
    for x in (x1, x2):
        if d.paper:
            d.marks("mark", circle(x, y, r))
        else:
            d.marks("mark", circle(x, y, r))
        d.raw(f'<circle cx="{x + r * 0.32:.1f}" cy="{y - r * 0.35:.1f}" r="{r * 0.34:.1f}" fill="{d.c[sclera] if d.paper else d.c["paper"]}"/>')
        d.raw(f'<circle cx="{x - r * 0.35:.1f}" cy="{y + r * 0.35:.1f}" r="{r * 0.14:.1f}" fill="{d.c[sclera] if d.paper else d.c["paper"]}"/>')
    if small:
        k = (x2 - x1) * 0.3
        d.marks("mark", circle(x1 - k * 0.4, y - r * 1.5, r * 0.36) + circle(x2 + k * 0.4, y - r * 1.5, r * 0.36))


# ================================================================ TARANTULA (Mexican red-knee: the friendly, famous one)
TARANT = {"hero": "#3A2C27", "hero2": "#EE7A2E", "fur": "#6E574B", "mark": "#120D0B", "light": "#FFFFFF", "pop": "#EE7A2E"}
TARANT_LEGS = [[(90, 82), (62, 56), (54, 26)], [(86, 90), (44, 76), (26, 56)], [(86, 100), (42, 112), (24, 134)], [(90, 108), (58, 138), (54, 170)]]


def tarantula_top(d: Drawing):
    legs(d, TARANT_LEGS, 12, band="hero2", band_at=(0.06, 0.34))
    legs(d, [[(95, 76), (88, 62), (86, 54)]], 8)
    if d.paper:
        for pts in TARANT_LEGS:
            d.stroke("fur", pl(pts), 1.4, line=False)
    d.shape("hero", tufty(100, 138, 30, 33, 26, 0.12))
    if d.paper:
        d.shape("fur", tufty(100, 140, 20, 23, 18, 0.12), shadow=False)
        d.stroke("hero", "M100 118 V158 M90 122 Q86 140 92 156 M110 122 Q114 140 108 156", 1.6)
    d.shape("hero", tufty(100, 90, 24, 21, 20, 0.1))
    if d.paper:
        d.stroke("hero2", "M88 98 Q100 106 112 98", 2.2)
    cute_eyes(d, 92, 108, 84, 5.4)


def tarantula_portrait(d: Drawing):
    foliage(d, [(-6, 44, 20), (-4, 100, -5), (206, 44, 160), (204, 100, 185), (6, 160, -30), (194, 160, -150)], "near", 46, 11)
    group(d, "translate(100 100) scale(.96) translate(-100 -98)", lambda: tarantula_top(d))


def tarantula_side(d: Drawing):
    """Side view walking right; ground at y=160."""
    far = [[(118, 128), (150, 104), (174, 158)], [(112, 130), (138, 98), (156, 160)], [(104, 130), (96, 100), (86, 160)], [(98, 130), (72, 108), (60, 158)]]
    near = [[(122, 134), (144, 112), (166, 160)], [(116, 136), (130, 104), (146, 162)], [(108, 136), (94, 108), (80, 162)], [(102, 136), (68, 114), (52, 160)]]
    for pts in far:
        d.limb("fur", pl(pts), 10)
    d.shape("hero", tufty(72, 124, 30, 24, 24, 0.12))
    if d.paper:
        d.shape("fur", tufty(70, 122, 18, 13, 16, 0.14), shadow=False)
    d.shape("hero", tufty(112, 124, 20, 15, 18, 0.1))
    d.shape("hero2", ellipse(112, 121, 11, 6), shadow=False, spot=True)
    d.shape("hero", ellipse(112, 120, 6, 3.5), shadow=False)
    for pts in near:
        d.limb("hero", pl(pts), 11)
        (kx, ky), (fx, fy) = pts[1], pts[2]
        d.limb("hero2", f"M{kx + (fx - kx) * .06:.1f} {ky + (fy - ky) * .06:.1f} L{kx + (fx - kx) * .32:.1f} {ky + (fy - ky) * .32:.1f}", 11.4, spot=True, shadow=False)
    d.limb("hero", "M126 130 L138 136 L142 148", 8)
    cute_eyes(d, 124, 133, 117, 3.8, small=False)


def tarantula_front(d: Drawing):
    """Front view, legs arching out either side like a little bridge; feet on y=164."""
    back = [[(86, 120), (46, 86), (24, 160)], [(86, 126), (52, 100), (38, 164)]]
    front = [[(86, 132), (60, 112), (52, 166)], [(88, 138), (72, 130), (68, 168)]]
    legs(d, back, 11, band="hero2", band_at=(0.04, 0.3))
    d.shape("hero", tufty(100, 108, 32, 26, 24, 0.12))
    if d.paper:
        d.shape("fur", tufty(100, 104, 20, 14, 16, 0.14), shadow=False)
    legs(d, front, 11, band="hero2", band_at=(0.04, 0.32))
    d.shape("hero", tufty(100, 136, 24, 19, 20, 0.1))
    legs(d, [[(94, 150), (90, 158), (90, 166)]], 7)
    if d.paper:
        d.stroke("hero2", "M86 124 Q100 118 114 124", 2.2)
    cute_eyes(d, 92, 108, 136, 5.2)


def tarantula_desert(d: Drawing):
    d.disc("glow", 146, 60, 26)
    d.band("far", "M-30 112 L30 112 L36 92 L84 92 L90 112 L230 112")
    d.band("mid", hills(140, 6, 20))
    d.band("ground", hills(160, 3))
    d.shape("rock", "M14 178 C22 160 60 156 100 158 C144 156 178 162 188 178 Z")
    d.shape("rock2", "M30 172 C50 166 80 166 100 170 C80 170 50 172 30 176Z", shadow=False, line=False)
    group(d, "translate(100 112) scale(.86) translate(-100 -120)", lambda: tarantula_front(d))
    for x, y, a in [(-6, 192, -60), (206, 192, -120)]:
        d.shape("near", leaf(x, y, 34, 7, a), shadow=False, line=False)


# ================================================================ HUNTSMAN SPIDER
HUNTS = {"hero": "#8A6744", "hero2": "#B48D63", "mark": "#3E2B1B", "light": "#FFFFFF",
         "bark": "#D9CBB3", "bark2": "#B8A68A", "bark3": "#EEE4D2", "gum": "#7FA386"}
HUNTS_LEGS = [[(90, 86), (58, 62), (44, 28)], [(88, 92), (40, 80), (20, 58)], [(88, 100), (38, 110), (18, 134)], [(90, 106), (58, 136), (52, 170)]]


def huntsman_top(d: Drawing):
    legs(d, HUNTS_LEGS, 6.5, band="mark", band_at=(0.3, 0.45), band2="mark")
    legs(d, [[(95, 80), (90, 70), (88, 64)]], 5.5)
    d.shape("hero", ellipse(100, 124, 14, 19))
    d.marks("mark", "M100 110 L94 116 L100 114 L106 116Z M100 120 L92 127 L100 124 L108 127Z M100 130 L93 136 L100 134 L107 136Z")
    d.shape("hero2", ellipse(100, 94, 17, 15))
    d.stroke("mark", "M100 84 V96 M90 92 L96 96 M110 92 L104 96", 1.6, line=False)
    cute_eyes(d, 94, 106, 84, 3.6)


def huntsman_portrait(d: Drawing):
    foliage(d, [(-6, 46, 20), (206, 46, 160), (6, 162, -30), (194, 162, -150)], "gum", 44, 9)
    group(d, "translate(100 100) scale(.94) translate(-100 -100)", lambda: huntsman_top(d))


def huntsman_gumtree(d: Drawing):
    d.band("far", hills(150, 8))
    d.band("mid", hills(172, 6, 30))
    trunk = "M48 210 C54 150 50 80 56 -10 L150 -10 C148 80 146 150 156 210Z"
    d.shape("bark", trunk)
    for p in ["M70 30 C80 26 92 34 90 50 C86 62 72 60 68 48Z", "M120 60 C132 58 140 70 136 84 C130 92 118 86 116 74Z",
              "M64 150 C76 144 90 152 88 166 C84 176 68 174 64 162Z", "M128 160 C140 156 146 168 142 178 C136 184 126 178 126 170Z"]:
        d.shape("bark3", p, shadow=False, line=False)
    d.stroke("bark2", "M72 -10 C70 40 76 100 70 210 M134 -10 C132 50 136 120 132 210", 1.6, line=False)
    # gum leaves hanging in from the top
    for x, y, a in [(20, -6, 100), (30, -8, 80), (178, -6, 96), (168, -8, 70), (190, 0, 120)]:
        d.shape("gum", leaf(x, y, 40, 6, a))
    group(d, "translate(102 104) rotate(-8) scale(.74) translate(-100 -100)", lambda: huntsman_top(d))


# ================================================================ REDBACK SPIDER
REDBACK = {"hero": "#1B1A1F", "hero2": "#3A3842", "mark": "#0E0D10", "light": "#FFFFFF", "pop": "#E8322E",
           "fence": "#B08A62", "fence2": "#8A6A48"}
REDBACK_LEGS = [[(92, 70), (66, 42), (58, 20)], [(90, 74), (52, 62), (30, 72)], [(90, 80), (56, 94), (40, 116)], [(94, 82), (56, 132), (50, 170)]]


def redback_top(d: Drawing, s=1.0):
    legs(d, REDBACK_LEGS, 5, role="hero")
    if d.paper:
        legs(d, REDBACK_LEGS, 1.4, role="hero2", shadow=False)
    ink(d, "hero", circle(100, 122, 36))
    if d.paper:
        d.raw(f'<ellipse cx="86" cy="104" rx="14" ry="8" transform="rotate(-35 86 104)" fill="#fff" opacity=".28"/>')
        d.raw(f'<ellipse cx="82" cy="100" rx="5" ry="3" transform="rotate(-35 82 100)" fill="#fff" opacity=".7"/>')
    stripe = ("M100 92 C104 98 106 104 104 110 C110 114 110 120 104 124 C108 130 108 138 103 144 C104 150 102 154 100 156 "
              "C98 154 96 150 97 144 C92 138 92 130 96 124 C90 120 90 114 96 110 C94 104 96 98 100 92Z")
    d.shape("pop", stripe, shadow=False, spot=True)
    ink(d, "hero", circle(100, 76, 14))
    cute_eyes(d, 94, 106, 72, 3.4, sclera="light")


def redback_portrait(d: Drawing):
    d.stroke("light", "M-10 30 L210 170 M-10 150 L210 50 M100 -10 V210 M20 -10 L180 210", 1.4, line=False)
    d.stroke("light", "M30 70 Q60 40 100 50 Q140 40 170 70 Q190 110 160 150 Q100 170 40 150 Q10 110 30 70Z", 1.2, line=False)
    group(d, "translate(100 100) scale(1.04) translate(-100 -98)", lambda: redback_top(d))


def redback_web(d: Drawing):
    d.disc("glow", 150, 60, 22)
    d.band("far", hills(150, 8))
    # timber fence
    for x in (-6, 34, 74, 114, 154, 194):
        d.shape("fence", f"M{x} 200 L{x} 96 L{x + 18} 88 L{x + 36} 96 L{x + 36} 200Z" if False else rrect(x, 92, 36, 120, 3))
        d.stroke("fence2", f"M{x + 12} 104 V200 M{x + 24} 100 V200", 1.4, line=False)
    d.shape("fence2", rrect(-30, 120, 260, 10, 2), line=False)
    d.band("ground", hills(176, 3))
    for x, y, a in [(-4, 196, -60), (10, 200, -80), (196, 196, -120), (184, 200, -100)]:
        d.shape("near", leaf(x, y, 40, 7, a), shadow=False, line=False)
    # tangled web
    d.raw('<g opacity=".85">', "")
    d.stroke("light", "M40 92 L100 128 L160 92 M70 92 L100 128 L130 92 M100 92 L100 128 M40 92 L80 150 L100 128 L120 150 L160 92 "
                      "M60 110 L140 110 M50 132 L150 132 M80 150 L120 150 M100 128 L100 176 M80 150 L100 176 L120 150", 1.2)
    d.raw("</g>", "")
    # redback hanging upside down, red hourglass showing
    def spider():
        legs(d, [[(94, 120), (70, 104), (56, 84)], [(92, 124), (64, 122), (48, 112)], [(92, 128), (68, 140), (56, 156)], [(94, 132), (78, 156), (74, 176)]], 4)
        ink(d, "hero", circle(100, 110, 20))
        if d.paper:
            d.raw('<ellipse cx="92" cy="101" rx="7" ry="4" transform="rotate(-35 92 101)" fill="#fff" opacity=".35"/>')
        d.shape("pop", "M92 102 L108 102 L102 110 L108 118 L92 118 L98 110Z", shadow=False, spot=True)
        ink(d, "hero", circle(100, 136, 9))
    spider()


# ================================================================ PEACOCK SPIDER
PEACOCK = {"hero": "#2E2622", "hero2": "#5A4A40", "mark": "#0F0B09", "light": "#FFFFFF", "pop": "#E8562A",
           "fan1": "#E8562A", "fan2": "#2B6FD6", "fan3": "#30C2B4", "fan4": "#F6B93B", "fem": "#A88B6E"}


def fan_wedge(cx, cy, r, a0, a1):
    a0, a1 = math.radians(a0), math.radians(a1)
    return (f"M{cx} {cy} L{cx + r * math.cos(a0):.1f} {cy + r * math.sin(a0):.1f} "
            f"A{r} {r} 0 0 1 {cx + r * math.cos(a1):.1f} {cy + r * math.sin(a1):.1f}Z")


def peacock_male(d: Drawing):
    """Front view, fan raised and third legs up: mid-dance. Fan centred (100, 112)."""
    cx, cy = 100, 112
    d.shape("fan1", fan_wedge(cx, cy, 70, 192, 348), spot=True)
    d.stroke("light", f"M{cx + 70 * math.cos(math.radians(192)):.1f} {cy + 70 * math.sin(math.radians(192)):.1f} "
                      f"A70 70 0 0 1 {cx + 70 * math.cos(math.radians(348)):.1f} {cy + 70 * math.sin(math.radians(348)):.1f}", 3, line=False)
    if d.paper:
        d.shape("fan3", fan_wedge(cx, cy, 58, 196, 344), shadow=False)
        d.shape("fan2", fan_wedge(cx, cy, 48, 200, 340), shadow=False)
        d.shape("fan1", fan_wedge(cx, cy, 36, 206, 334), shadow=False)
        d.shape("fan4", fan_wedge(cx, cy, 24, 214, 326), shadow=False)
        # blue chevrons on the orange
        d.shape("fan2", "M100 60 L88 76 L100 72 L112 76Z", shadow=False)
    else:
        d.stroke("mark", f"M{cx - 50} {cy - 10} A50 50 0 0 1 {cx + 50} {cy - 10} M{cx - 30} {cy - 8} A30 30 0 0 1 {cx + 30} {cy - 8}", 2)
    # raised third legs, white-tipped
    for side in (-1, 1):
        def leg(side=side):
            d.limb("hero", f"M{100 - 18} 130 L{100 - 50} 112 L{100 - 64} 70", 7)
            d.limb("light", f"M{100 - 60} 82 L{100 - 64} 70", 7.4, spot=False, shadow=False)
        leg() if side == -1 else flip(d, leg)
    legs(d, [[(86, 146), (64, 156), (52, 180)], [(90, 150), (78, 166), (76, 188)]], 7)
    # face: fuzzy cephalothorax with the huge jumping-spider eyes
    d.shape("hero", "M72 150 C70 128 82 118 100 118 C118 118 130 128 128 150 C126 162 114 166 100 166 C86 166 74 162 72 150Z")
    d.shape("pop", "M76 132 C84 124 116 124 124 132 C116 128 84 128 76 132Z", shadow=False)
    if d.paper:
        for x in (88, 112):
            d.marks("mark", circle(x, 142, 10))
            d.marks("light", circle(x + 3.4, 138.6, 3.2))
            d.marks("light", circle(x - 3.6, 146, 1.4))
    else:
        for x in (88, 112):
            d.marks("mark", circle(x, 142, 10))
            d.raw(f'<circle cx="{x + 3.4}" cy="138.6" r="3.2" fill="{d.c["paper"]}"/>')
    d.marks("mark", circle(74, 140, 2.6) + circle(126, 140, 2.6))
    d.shape("light", ellipse(94, 162, 4, 3), shadow=False)
    d.shape("light", ellipse(106, 162, 4, 3), shadow=False)


def peacockspider_portrait(d: Drawing):
    foliage(d, [(-6, 150, -20), (206, 150, -160), (-6, 190, -40), (206, 190, -140)], "near", 46, 11)
    d.band("ground", hills(186, 2))
    group(d, "translate(100 100) scale(1.12) translate(-100 -112)", lambda: peacock_male(d))


def peacockspider_leaf(d: Drawing):
    d.disc("glow", 148, 54, 22)
    d.band("far", hills(130, 8))
    blades(d, [10, 24, 40, 170, 186], 170, 54, "mid", 3.5)
    d.shape("near", "M-20 170 C30 150 120 150 220 166 C150 178 40 184 -20 170Z")
    d.stroke("deep", "M-10 170 C40 162 120 162 210 166", 1.6, line=False)
    group(d, "translate(80 106) scale(.64) translate(-100 -112)", lambda: peacock_male(d))
    # the female: small, brown, watching
    legs(d, [[(156, 150), (146, 140), (140, 162)], [(156, 154), (150, 148), (148, 164)]], 3.6, role="fem", cx=162)
    d.shape("fem", ellipse(162, 142, 10, 9))
    d.shape("fem", ellipse(162, 154, 9, 7))
    cute_eyes(d, 158, 166, 153, 2.4, small=False)
    d.shape("pop", "M156 118 C156 114 162 114 162 118 C162 114 168 114 168 118 C168 123 162 126 162 128 C162 126 156 123 156 118Z", spot=True)


# ================================================================ GOLDEN ORB-WEAVER
ORB = {"hero": "#6E6A36", "hero2": "#DAD6CA", "mark": "#1E1A16", "spots": "#F2D35B", "light": "#FFFFFF",
       "legs": "#26201B", "knee": "#E8B923", "silk": "#E3AE2E"}
ORB_LEGS = [[(94, 66), (66, 40), (60, 12)], [(92, 72), (52, 58), (30, 44)], [(92, 78), (68, 86), (58, 104)], [(94, 84), (64, 128), (58, 168)]]


def web(d: Drawing, cx, cy, r, n=14, turns=7, w=1.3, role="silk"):
    spokes = ""
    for i in range(n):
        a = 2 * math.pi * i / n + 0.12
        spokes += f"M{cx} {cy} L{cx + r * math.cos(a):.1f} {cy + r * math.sin(a):.1f} "
    d.stroke(role, spokes, w)
    pts = []
    for k in range(n * turns):
        a = 2 * math.pi * k / n + 0.12
        rr = 12 + (r - 14) * k / (n * turns)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.stroke(role, pl(pts), w)


def orb_spider(d: Drawing):
    legs(d, ORB_LEGS, 4.4, role="legs", band="knee", band_at=(0.0, 0.14), band2="knee")
    for pts in ORB_LEGS:
        pass
    legs(d, [[(96, 60), (92, 52), (90, 46)]], 4, role="legs")
    d.shape("hero", "M100 82 C114 82 118 98 118 116 C118 136 110 150 100 150 C90 150 82 136 82 116 C82 98 86 82 100 82Z", spot=True)
    d.marks("spots", "".join(circle(x, y, 2.6) for x, y in [(92, 98), (108, 98), (90, 114), (110, 114), (93, 130), (107, 130), (100, 140)]))
    d.shape("hero2", ellipse(100, 70, 12, 14))
    cute_eyes(d, 95, 105, 62, 3.2, small=False)


def orbweaver_portrait(d: Drawing):
    web(d, 100, 100, 110, 16, 9, 1.4)
    group(d, "translate(100 100) scale(1.12) translate(-100 -92)", lambda: orb_spider(d))


def orbweaver_forest(d: Drawing):
    d.disc("glow", 100, 96, 46)
    d.band("far", hills(160, 8))
    d.limb("dark", "M22 210 L28 -10", 18)
    d.limb("dark", "M178 210 L172 -10", 16)
    d.limb("dark", "M28 60 L60 36 M172 90 L146 70", 6)
    foliage(d, [(60, 36, -30), (60, 36, 10), (146, 70, -150), (146, 70, 170)], "near", 26, 7)
    d.band("mid", hills(186, 5, 20))
    d.stroke("silk", "M36 28 L66 60 M164 24 L136 58 M34 172 L64 142 M166 170 L136 142", 1.3)
    web(d, 100, 100, 62, 14, 7, 1.3)
    group(d, "translate(100 100) scale(.6) translate(-100 -96)", lambda: orb_spider(d))


# ================================================================ SCORPION
SCORP = {"hero": "#D69A3C", "hero2": "#F0C46E", "mark": "#6A4218", "sting": "#4A2C10", "light": "#FFFFFF"}


def chela(x, y, ang, s=1.0):
    """A scorpion pincer: a fat hand with two curved fingers, pointing along ang."""
    r = math.radians(ang)
    ux, uy, px, py = math.cos(r), math.sin(r), -math.sin(r), math.cos(r)
    P = lambda a, b: f"{x + (ux * a + px * b) * s:.1f} {y + (uy * a + py * b) * s:.1f}"
    return (f"M{P(-4, -8)} C{P(6, -12)} {P(16, -10)} {P(20, -6)} C{P(28, -6)} {P(34, -4)} {P(36, 1)} "
            f"C{P(30, -1)} {P(24, -1)} {P(20, 0)} L{P(20, 2)} C{P(26, 3)} {P(32, 6)} {P(33, 10)} "
            f"C{P(26, 9)} {P(18, 9)} {P(12, 9)} C{P(4, 10)} {P(-4, 8)} {P(-4, -8)}Z")


def scorp_tail(d: Drawing, pts, w0, w1, n_seg=6):
    """A segmented tail along pts (body end first), ending in the bulb and curved sting."""
    body = tube(pts, lambda t: w0 + (w1 - w0) * t)
    d.shape("hero", body)
    fr = _frames(pts)
    if True:
        s = ""
        for k in range(1, n_seg):
            t = k / n_seg
            x, y, dx, dy, _ = min(fr, key=lambda f: abs(f[4] - t))
            hw = (w0 + (w1 - w0) * t) / 2
            s += f"M{x + dy * hw:.1f} {y - dx * hw:.1f} L{x - dy * hw:.1f} {y + dx * hw:.1f} "
        d.stroke("mark", s, 1.6)
    x, y, a = at(pts, 1.0)

    def bulb():
        d.shape("hero2", "M-3 -7 C8 -9 16 -5 16 1 C16 6 8 9 -3 7Z", spot=True)
        d.shape("sting", "M14 -2 C20 -2 24 3 22 10 C20 6 17 4 13 4Z", shadow=False)
    place(d, x, y, a, bulb)


def scorpion_top(d: Drawing):
    """Seen from above: pincers forward (up), tail curled round to the side like a question mark."""
    legs(d, [[(90, 82), (70, 74), (60, 64)], [(88, 90), (66, 90), (54, 84)], [(88, 98), (66, 106), (56, 112)], [(90, 106), (70, 120), (62, 132)]], 5.5)
    for side in (-1, 1):
        def arm():
            d.limb("hero", "M92 68 L78 60 L72 50", 8)
            d.shape("hero", chela(72, 50, -95, 0.9), spot=True)
        arm() if side == -1 else flip(d, arm)
    scorp_tail(d, [(100, 112), (104, 136), (122, 154), (146, 150), (156, 128), (148, 110)], 15, 10)
    d.shape("hero", "M100 58 C112 58 116 68 116 80 C116 98 112 116 100 122 C88 116 84 98 84 80 C84 68 88 58 100 58Z")
    d.stroke("mark", "M88 84 Q100 88 112 84 M87 94 Q100 98 113 94 M89 104 Q100 108 111 104 M92 113 Q100 116 108 113", 1.8)
    cute_eyes(d, 95, 105, 68, 3.2, small=False)


def scorpion_portrait(d: Drawing):
    for x, y in [(36, 164), (164, 40), (40, 40)]:
        d.shape("ground", f"M{x - 12} {y + 5} Q{x - 10} {y - 6} {x} {y - 7} Q{x + 10} {y - 6} {x + 12} {y + 5}Z", line=False)
    group(d, "translate(100 100) scale(1.12) translate(-104 -96)", lambda: scorpion_top(d))


def scorpion_side(d: Drawing):
    """Side view facing left, standing on y=160, tail arched up over its back."""
    legs(d, [[(96, 150), (88, 140), (80, 160)], [(104, 150), (100, 138), (96, 160)], [(112, 150), (116, 138), (114, 160)], [(120, 150), (128, 140), (132, 160)]], 4.5, cx=1000)
    scorp_tail(d, [(134, 146), (154, 136), (162, 114), (154, 94), (136, 86), (122, 92)], 13, 9, 6)
    d.shape("hero", "M74 146 C80 138 100 136 118 138 C130 140 138 144 140 150 C132 156 100 158 80 156 C74 154 72 150 74 146Z")
    d.stroke("mark", "M92 140 V156 M104 139 V157 M116 140 V156 M128 142 V154", 1.6, line=False)
    d.limb("hero", "M78 146 L64 138 L54 142", 6)
    d.shape("hero", chela(52, 142, 192, 0.8), spot=True)
    cute_eyes(d, 80, 87, 143, 2.6, small=False)


def scorpion_desert(d: Drawing):
    d.disc("glow", 60, 62, 26)
    stars(d, [(130, 40, 3), (160, 64, 2.4), (100, 30, 2), (176, 100, 2)])
    d.band("far", "M-30 120 Q30 96 80 116 T230 108")
    d.band("mid", "M-30 150 Q50 126 110 146 T230 138")
    saguaro(d, 172, 150, 56, 0.8)
    d.band("ground", "M-30 172 Q60 150 120 166 T230 162")
    group(d, "translate(104 136) scale(1.15) translate(-108 -150)", lambda: scorpion_side(d))


# ================================================================ concepts

SCORP_CACTUS = {**SCORP, "cactus": "#4F8D5A", "cactus2": "#3A6E46"}
ALL = ["golden", "coastal", "meadow", "blush", "dusk"]
WET = ["coastal", "meadow", "blush", "dusk"]

CONCEPTS = [
    Concept("treepython-portrait", "animal-green-tree-python", "Green tree python", treepython_portrait, overrides=TREEPY,
            checks=[("hero", "sky"), ("hero", "near"), ("hero", "mid"), ("hero", "bark")], fixes={"near": ["deep", "dark"], "mid": ["far", "deep", "glow2"]}),
    Concept("treepython-rainforest", "animal-green-tree-python", "Tree python in the rainforest", treepython_rainforest, overrides=TREEPY,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "near"), ("hero", "mid")], fixes={"near": ["deep", "dark"], "mid": ["deep", "dark"], "far": ["sky2", "glow2"]}),
    Concept("burmesepython-portrait", "animal-burmese-python", "Burmese python", burmese_portrait, overrides=BURMESE,
            checks=[("hero", "sky"), ("hero", "ground"), ("hero", "near")], fixes={"ground": ["near", "mid", "deep"], "near": ["deep", "mid"]}),
    Concept("burmesepython-river", "animal-burmese-python", "Python in the river", burmese_river, WET, overrides=BURMESE,
            checks=[("hero", "near"), ("hero", "mid"), ("hero", "glow")], fixes={"near": ["deep", "mid"], "mid": ["near", "deep"], "glow": ["light", "glow2"]}),
    Concept("rattlesnake-portrait", "animal-rattlesnake", "Rattlesnake", rattlesnake_portrait, overrides=RATTLE,
            checks=[("hero", "sky"), ("hero", "ground"), ("hero", "glow"), ("rattle", "sky")], fixes={"ground": ["near", "mid", "deep"], "glow": ["near", "mid"], "sky": ["sky2", "far"]}),
    Concept("rattlesnake-desert", "animal-rattlesnake", "Rattlesnake in the desert", rattlesnake_desert, overrides=RATTLE,
            checks=[("hero", "sky"), ("hero", "ground"), ("cactus", "sky"), ("rattle", "far")], fixes={"ground": ["near", "mid", "deep"], "far": ["mid", "near"]}),
    Concept("mamba-portrait", "animal-black-mamba", "Black mamba", mamba_portrait, overrides=MAMBA,
            checks=[("hero", "sky"), ("hero", "ground"), ("hero", "near")], fixes={"sky": ["sky2", "glow2", "light"], "ground": ["light", "glow2"], "near": ["mid", "far"]}),
    Concept("mamba-savanna", "animal-black-mamba", "Mamba on the savanna", mamba_savanna, overrides=MAMBA,
            checks=[("hero", "sky"), ("hero", "glow"), ("hero", "mound")], fixes={"glow": ["glow2", "light"], "sky": ["sky2", "glow2"]}),
    Concept("eyelashviper-portrait", "animal-eyelash-viper", "Eyelash viper", eyelash_portrait, overrides=EYELASH,
            checks=[("hero", "sky"), ("hero", "near"), ("hero", "bark")], fixes={"near": ["deep", "mid"], "sky": ["sky2", "far"]}),
    Concept("eyelashviper-heliconia", "animal-eyelash-viper", "Eyelash viper on a heliconia", eyelash_heliconia, overrides=EYELASH,
            checks=[("hero", "sky"), ("hero", "mid"), ("flower", "mid"), ("flower", "near")], fixes={"mid": ["near", "deep"], "near": ["deep", "mid"], "sky": ["sky2", "far"]}),
    Concept("tarantula-portrait", "animal-tarantula", "Tarantula", tarantula_portrait, overrides=TARANT,
            checks=[("hero", "sky"), ("hero", "near"), ("hero2", "sky")], fixes={"sky": ["light", "sky2", "glow2"], "near": ["mid", "far"]}),
    Concept("tarantula-desert", "animal-tarantula", "Tarantula at dusk", tarantula_desert, overrides={**TARANT, "rock": "#A89580", "rock2": "#8C7A66"},
            checks=[("hero", "sky"), ("hero", "glow"), ("hero", "rock"), ("rock", "ground")], fixes={"sky": ["light", "sky2"], "ground": ["near", "mid", "deep"]}),
    Concept("huntsman-portrait", "animal-huntsman-spider", "Huntsman spider", huntsman_portrait, overrides=HUNTS,
            checks=[("hero", "sky"), ("hero2", "sky"), ("gum", "sky")], fixes={"sky": ["light", "sky2", "far"]}),
    Concept("huntsman-gumtree", "animal-huntsman-spider", "Huntsman on a gum tree", huntsman_gumtree, overrides=HUNTS,
            checks=[("hero", "bark"), ("bark", "sky"), ("gum", "sky")], fixes={"sky": ["far", "mid", "sky2"]}),
    Concept("redback-portrait", "animal-redback-spider", "Redback spider", redback_portrait, overrides=REDBACK,
            checks=[("hero", "sky"), ("pop", "hero")], fixes={"sky": ["far", "mid", "sky2"]}),
    Concept("redback-web", "animal-redback-spider", "Redback in its web", redback_web, overrides=REDBACK,
            checks=[("hero", "fence"), ("fence", "sky"), ("light", "fence")], fixes={"sky": ["far", "mid", "deep"]}),
    Concept("peacockspider-portrait", "animal-peacock-spider", "Peacock spider", peacockspider_portrait, overrides=PEACOCK,
            checks=[("fan1", "sky"), ("hero", "fan1")], fixes={"sky": ["light", "sky2", "far", "deep"]}),
    Concept("peacockspider-leaf", "animal-peacock-spider", "Peacock spider dancing", peacockspider_leaf, overrides=PEACOCK,
            checks=[("fan1", "sky"), ("fan1", "far"), ("fem", "near"), ("hero", "near")], fixes={"far": ["mid", "sky2"], "near": ["deep", "mid", "far"]}),
    Concept("orbweaver-portrait", "animal-orb-weaver", "Golden orb-weaver", orbweaver_portrait, overrides=ORB,
            checks=[("silk", "sky"), ("hero", "sky"), ("hero2", "sky")], fixes={"sky": ["mid", "near", "deep", "sky2"]}),
    Concept("orbweaver-forest", "animal-orb-weaver", "Golden orb-weaver's web", orbweaver_forest, overrides=ORB,
            checks=[("silk", "sky"), ("silk", "glow"), ("hero", "glow")], fixes={"glow": ["light", "glow2", "far", "mid"], "sky": ["sky2", "mid", "near"]}),
    Concept("scorpion-portrait", "animal-scorpion", "Scorpion", scorpion_portrait, overrides=SCORP,
            checks=[("hero", "sky"), ("hero2", "sky")], fixes={"sky": ["far", "mid", "sky2"]}),
    Concept("scorpion-desert", "animal-scorpion", "Scorpion on the dunes", scorpion_desert, overrides=SCORP_CACTUS,
            checks=[("hero", "ground"), ("hero", "sky"), ("hero", "mid")], fixes={"ground": ["near", "deep", "light"], "mid": ["far", "near"]}),
]
