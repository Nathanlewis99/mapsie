"""Animals: European wildlife and birds of the world. Two concepts each (portrait + habitat)."""
import math

from _common import Concept, Drawing, cloud, fish, circle, ellipse, waves, hills, rrect, group  # noqa: F401

_uid = [0]


# ================================================================ helpers
def _id(prefix):
    _uid[0] += 1
    return f"{prefix}{_uid[0]}"


def clipped(d: Drawing, path: str, fn):
    """Draw fn() clipped to `path`."""
    cid = _id("aebclip")
    tag = f'<clipPath id="{cid}"><path d="{path}"/></clipPath><g clip-path="url(#{cid})">'
    d.raw(tag, tag)
    fn()
    d.raw("</g>", "</g>")


def flip(d: Drawing, fn, cx=100):
    group(d, f"translate({2 * cx} 0) scale(-1 1)", fn)


def place(d: Drawing, x, y, s, fn, ox=100, oy=100, mirror=False):
    """Draw fn() (designed around (ox, oy)) at (x, y), scaled by s, optionally mirrored."""
    sx = -s if mirror else s
    group(d, f"translate({x} {y}) scale({sx} {s}) translate({-ox} {-oy})", fn)


def faded(d: Drawing, fn, opacity=".55"):
    d.raw(f'<g opacity="{opacity}">', "")
    fn()
    d.raw("</g>", "")


def P(pts, closed=True, k=1.0):
    """Smooth path through points (Catmull-Rom). A point (x, y, 1) is a sharp corner."""
    n = len(pts)

    def at(i):
        if closed:
            return pts[i % n]
        return pts[max(0, min(n - 1, i))]

    def sharp(i):
        p = at(i)
        return len(p) > 2 and p[2]

    s = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(n if closed else n - 1):
        p0, p1, p2, p3 = at(i - 1), at(i), at(i + 1), at(i + 2)
        c1 = (p1[0], p1[1]) if sharp(i) else (p1[0] + (p2[0] - p0[0]) * k / 6, p1[1] + (p2[1] - p0[1]) * k / 6)
        c2 = (p2[0], p2[1]) if sharp(i + 1) else (p2[0] - (p3[0] - p1[0]) * k / 6, p2[1] - (p3[1] - p1[1]) * k / 6)
        s += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return s + ("Z" if closed else "")


def mx(pts, cx=100):
    return [(2 * cx - p[0], p[1], *p[2:]) for p in pts]


def sym(right, cx=100):
    """Full closed outline from the right half (top centre -> bottom centre)."""
    return right + mx(right[-2:0:-1], cx)


def spline(pts, n=8):
    """Sample a smooth open curve through pts."""
    out = []
    m = len(pts)
    at = lambda i: pts[max(0, min(m - 1, i))]
    for i in range(m - 1):
        p0, p1, p2, p3 = at(i - 1), at(i), at(i + 1), at(i + 2)
        for j in range(n):
            t = j / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[k] + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2
                                     + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in (0, 1)))
    out.append((pts[-1][0], pts[-1][1]))
    return out


def taper(pts, w0, w1, n=8, wf=None):
    """A tapering shape (horn, tail, neck, bill) along a smooth curve; w0/w1 are half widths."""
    s = spline(pts, n)
    L, R = [], []
    for i, (x, y) in enumerate(s):
        a, b = s[max(0, i - 1)], s[min(len(s) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        h = math.hypot(dx, dy) or 1
        t = i / (len(s) - 1)
        w = wf(t) if wf else w0 + (w1 - w0) * t
        L.append((x + dy / h * w, y - dx / h * w))
        R.append((x - dy / h * w, y + dx / h * w))
    q = L + R[::-1]
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in q) + "Z"


def zig(pts, n, h, start=True):
    """Zigzag (sharp points) along a polyline: fur, spines, shaggy fringes. h>0 points left of travel."""
    s = spline(pts, 6)
    seg = [math.hypot(s[i + 1][0] - s[i][0], s[i + 1][1] - s[i][1]) for i in range(len(s) - 1)]
    total = sum(seg)

    def at(dist):
        acc = 0
        for i, l in enumerate(seg):
            if acc + l >= dist or i == len(seg) - 1:
                t = (dist - acc) / (l or 1)
                x = s[i][0] + (s[i + 1][0] - s[i][0]) * t
                y = s[i][1] + (s[i + 1][1] - s[i][1]) * t
                return x, y, (s[i + 1][0] - s[i][0]) / (l or 1), (s[i + 1][1] - s[i][1]) / (l or 1)
            acc += l

    out = []
    for i in range(2 * n + 1):
        x, y, dx, dy = at(total * i / (2 * n))
        if i % 2:
            out.append((x + dy * h, y - dx * h, 1))
        elif start or i:
            out.append((x, y, 1))
    return out


def fingers(hx, hy, r0, r1, a0, a1, n):
    """Primary feathers fanning from a 'hand' at (hx, hy), from angle a0 to a1 (degrees)."""
    pts = []
    step = (a1 - a0) / n
    for i in range(n + 1):
        a = math.radians(a0 + step * i)
        pts.append((hx + r0 * math.cos(a), hy + r0 * math.sin(a), 1))
        if i < n:
            am = math.radians(a0 + step * (i + 0.5))
            w = math.radians(step * 0.16)
            pts.append((hx + r1 * math.cos(am - w), hy + r1 * math.sin(am - w)))
            pts.append((hx + r1 * math.cos(am + w), hy + r1 * math.sin(am + w)))
    return pts


def claw(x, y, a, s=1.0):
    """A hooked talon at (x, y) pointing at angle a (degrees), curling clockwise."""
    r = math.radians(a)
    ux, uy, px, py = math.cos(r), math.sin(r), -math.sin(r), math.cos(r)
    p = lambda f, g: (x + (ux * f + px * g) * s, y + (uy * f + py * g) * s)
    a1, a2, tip, b1 = p(0, -2), p(6, -2.5), p(9, 3), p(0, 2)
    c = p(5, 1.5)
    return (f"M{a1[0]:.1f} {a1[1]:.1f} Q{a2[0]:.1f} {a2[1]:.1f} {tip[0]:.1f} {tip[1]:.1f} "
            f"Q{c[0]:.1f} {c[1]:.1f} {b1[0]:.1f} {b1[1]:.1f}Z")


def scallop(cx, cy, r, n=12, bump=0.22, rot=0.0):
    pts = []
    for i in range(n + 1):
        a = rot + 2 * math.pi * i / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    s = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(n):
        a = rot + 2 * math.pi * (i + 0.5) / n
        qx, qy = cx + r * (1 + bump * 2) * math.cos(a), cy + r * (1 + bump * 2) * math.sin(a)
        s += f" Q{qx:.1f} {qy:.1f} {pts[i + 1][0]:.1f} {pts[i + 1][1]:.1f}"
    return s + "Z"


def leaf(x, y, length, width, angle):
    a = math.radians(angle)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    tx, ty = x + ux * length, y + uy * length
    c1 = (x + ux * length * 0.35 + px * width, y + uy * length * 0.35 + py * width)
    c2 = (x + ux * length * 0.35 - px * width, y + uy * length * 0.35 - py * width)
    return (f"M{x:.1f} {y:.1f} Q{c1[0]:.1f} {c1[1]:.1f} {tx:.1f} {ty:.1f} "
            f"Q{c2[0]:.1f} {c2[1]:.1f} {x:.1f} {y:.1f}Z")


def oak(x, y, s, a):
    """A lobed oak leaf."""
    pts = [(0, 0, 1), (4, -3), (6, -1, 1), (9, -5), (12, -3, 1), (15, -6), (18, -3, 1), (21, -5), (24, 0, 1),
           (21, 5), (18, 3, 1), (15, 6), (12, 3, 1), (9, 5), (6, 1, 1), (4, 3)]
    r = math.radians(a)
    c, sn = math.cos(r), math.sin(r)
    return P([(x + (px * c - py * sn) * s, y + (px * sn + py * c) * s, *rest) for px, py, *rest in pts])


def birds(d: Drawing, pts, role="dark"):
    s = " ".join(f"M{x} {y} q{3 * k} {-3 * k} {6 * k} 0 q{3 * k} {-3 * k} {6 * k} 0" for x, y, k in pts)
    d.stroke(role, s, 1.8)


def grass(d: Drawing, x0, x1, y, h=12, role="near", step=16, line=False):
    x, i = x0, 0
    while x < x1:
        k = h * (0.75 + 0.25 * ((i * 5) % 3) / 2)
        d.shape(role, f"M{x} {y} L{x + 2} {y - k * 0.7} L{x + 4} {y - 2} L{x + 6} {y - k} L{x + 8} {y - 2} "
                      f"L{x + 10} {y - k * 0.6} L{x + 12} {y}Z", shadow=False, line=line)
        x += step
        i += 1


def pine(d: Drawing, x, y, h, role="near", shadow=True, line=True, snow=False):
    w = h * 0.36
    d.shape(role, f"M{x} {y - h} L{x + w * 0.6} {y - h * 0.62} L{x + w * 0.35} {y - h * 0.62} L{x + w * 0.85} {y - h * 0.3} "
                  f"L{x + w * 0.5} {y - h * 0.3} L{x + w} {y - h * 0.06} L{x - w} {y - h * 0.06} L{x - w * 0.5} {y - h * 0.3} "
                  f"L{x - w * 0.85} {y - h * 0.3} L{x - w * 0.35} {y - h * 0.62} L{x - w * 0.6} {y - h * 0.62}Z",
            shadow=shadow, line=line)
    if snow:
        for f, ww in [(0.62, 0.6), (0.3, 0.85), (0.06, 1.0)]:
            yy = y - h * f
            d.shape("light", f"M{x - w * ww:.1f} {yy:.1f} Q{x:.1f} {yy - h * 0.12:.1f} {x + w * ww:.1f} {yy:.1f} "
                             f"Q{x:.1f} {yy - h * 0.05:.1f} {x - w * ww:.1f} {yy:.1f}Z", shadow=False, line=False)
        d.shape("light", f"M{x} {y - h} L{x + w * 0.25:.1f} {y - h * 0.84:.1f} L{x - w * 0.25:.1f} {y - h * 0.84:.1f}Z",
                shadow=False, line=False)


def mist(d: Drawing, y, amp=3, step=40, opacity=".55"):
    d.raw(f'<g opacity="{opacity}">', "")
    d.band("light", waves(y, amp, step), shadow=False, line=False)
    d.raw("</g>", "")


def peaks(d: Drawing, edge, caps, role="far"):
    d.band(role, edge)
    for c in caps:
        d.shape("light", c, shadow=False)


def eye(d: Drawing, x, y, r, iris=None, glint=True):
    if iris:
        d.shape(iris, circle(x, y, r), shadow=False)
        d.marks("mark", circle(x, y, r * 0.55))
    else:
        d.marks("mark", circle(x, y, r))
    if glint:
        d.marks("light", circle(x - r * 0.3, y - r * 0.35, max(0.9, r * 0.28)))


# ================================================================ RED DEER
def antler(d: Drawing, role="horn"):
    """Right-hand antler of a front-on stag (mirror for the left)."""
    d.limb(role, P([(106, 84), (118, 72), (132, 62), (144, 50), (149, 38), (148, 28)], False), 6)
    d.limb(role, P([(114, 76), (110, 64), (112, 54)], False), 4.2, shadow=False)
    d.limb(role, P([(133, 62), (128, 50), (131, 40)], False), 4.2, shadow=False)
    d.limb(role, P([(147, 42), (139, 34), (137, 24)], False), 4, shadow=False)
    d.limb(role, P([(148, 42), (158, 36), (162, 28)], False), 4, shadow=False)


def reddeer_portrait(d: Drawing):
    d.disc("glow", 100, 92, 58)
    d.band("far", hills(170, 8))
    d.band("mid", hills(186, 5, 30), line=False)

    def stag():
        # neck mane
        d.shape("mane", P([(62, 210, 1), (66, 186, 1), (56, 178, 1), (68, 168, 1), (60, 156, 1), (72, 150, 1), (70, 138, 1), (84, 128),
                           (116, 128), (130, 138, 1), (128, 150, 1), (140, 156, 1), (132, 168, 1), (144, 178, 1), (134, 186, 1), (138, 210, 1)]))
        d.shape("mane", P([(82, 150, 1), (86, 182, 1), (93, 170, 1), (100, 188, 1), (107, 170, 1), (114, 182, 1), (118, 150, 1)]), shadow=False)
        antler(d)
        flip(d, lambda: antler(d))
        for side in (False, True):
            def ear():
                d.shape("hero", P([(120, 94, 1), (140, 80), (162, 80, 1), (150, 98), (122, 108, 1)]))
                d.shape("light", P([(126, 96, 1), (142, 86), (156, 84, 1), (146, 96), (128, 102, 1)]), shadow=False, line=False)
            flip(d, ear) if side else ear()
        head = sym([(100, 80), (114, 82), (124, 94), (124, 110), (118, 130), (111, 150), (106, 162), (100, 165)])
        d.shape("hero", P(head))
        d.shape("hero2", P(sym([(100, 132), (108, 134), (110, 150), (106, 162), (100, 165)])), shadow=False, line=False)
        d.marks("mark", ellipse(100, 156, 9, 6.5))
        d.marks("hero2", ellipse(96, 155, 2, 1.6) + ellipse(104, 155, 2, 1.6))
        for x, a in [(82, 20), (118, -20)]:
            d.shape("light", ellipse(x, 108, 6.5, 4.6), extra=f'transform="rotate({a} {x} 108)"', shadow=False, line=False)
            d.marks("mark", ellipse(x, 108, 4.2, 3.2))
            d.marks("light", circle(x - 1.2, 106.8, 1.1))
        d.stroke("mane", "M100 84 V128", 2, line=False)
    group(d, "translate(100 128) scale(.9) translate(-100 -128)", stag)


STAG_BODY = [(62, 112), (70, 98), (90, 92), (116, 95), (138, 93), (150, 102), (150, 118), (142, 132), (116, 134), (86, 134), (68, 130)]


def roaring_stag(d: Drawing):
    # far legs
    d.limb("hero2", P([(86, 128), (87, 148), (89, 168)], False), 5.5)
    d.limb("hero2", P([(126, 124), (121, 138), (131, 151), (129, 168)], False), 5.5)
    d.shape("mark", "M149 100 Q158 102 155 111 L149 110Z", shadow=False)
    d.shape("hero", P(STAG_BODY))
    d.shape("hero2", P([(142, 96), (150, 103), (149, 117), (141, 112)]), shadow=False, line=False)
    d.limb("hero", P([(73, 126), (72, 148), (70, 168)], False), 6)
    d.limb("hero", P([(138, 122), (133, 138), (144, 151), (142, 168)], False), 6.5)
    d.marks("mark", "M66 166 h8 v3 h-8Z M138 166 h8 v3 h-8Z M85 166 h8 v3 h-8Z M125 166 h8 v3 h-8Z")
    # antlers sweeping back
    for path, w in [([(58, 48), (63, 32), (75, 20), (91, 13), (106, 14)], 5), ([(60, 42), (50, 33), (46, 24)], 3.6),
                    ([(67, 28), (63, 15)], 3.4), ([(90, 14), (91, 2)], 3.2), ([(99, 12), (106, 2)], 3.2),
                    ([(104, 14), (117, 12)], 3.2)]:
        d.limb("horn", P(path, False), w, shadow=w > 4)
    # thick shaggy neck, stretched up
    neck = [(98, 96), (84, 80), (70, 62), (62, 52), (50, 56), (44, 66)] + zig([(44, 68), (46, 88), (54, 108), (64, 124)], 9, -4.5)[1:] + [(80, 112)]
    d.shape("mane", P(neck))
    d.shape("hero", P([(58, 50, 1), (72, 38), (77, 42, 1), (68, 54, 1)]))
    # head raised, mouth wide open
    d.shape("hero", P([(54, 62), (40, 52), (30, 48, 1), (29, 53, 1), (40, 62), (52, 70)]))
    d.marks("mark", P([(50, 52), (30, 43), (30, 48, 1), (47, 60)]))
    d.shape("hero", P([(66, 54), (54, 44), (40, 36), (27, 30), (20, 32, 1), (21, 37, 1), (34, 42), (46, 50), (54, 60), (62, 64)]))
    d.marks("mark", circle(21.5, 33.5, 2.2))
    eye(d, 47, 45, 2.2)
    # breath clouds and roar
    faded(d, lambda: [d.shape("light", cloud(-4, 38, 0.55), shadow=False, line=False),
                      d.shape("light", cloud(-12, 24, 0.4), shadow=False, line=False)], ".85")
    d.stroke("light", "M14 22 Q8 18 2 20 M16 50 Q10 54 4 52", 2)


def reddeer_roar(d: Drawing):
    d.disc("glow", 150, 64, 22)
    peaks(d, "M-30 112 L12 88 L40 100 L74 72 L104 98 L134 82 L160 96 L188 76 L230 104",
          ["M74 72 L84 81 L78 80 L73 85 L67 79 L63 82Z", "M188 76 L196 83 L190 82 L186 86 L181 81Z"])
    mist(d, 106, 4, 44, ".6")
    d.band("mid", hills(132, 8, 30))
    mist(d, 138, 3, 36, ".5")
    d.band("near", "M-30 176 Q30 150 100 160 Q150 168 230 156")
    group(d, "translate(106 164) scale(.8) translate(-100 -168)", lambda: roaring_stag(d))
    d.band("deep", hills(188, 4, 20), line=False)


# ================================================================ HIGHLAND COW
def coo_horn(d: Drawing):
    pts = [(74, 94), (54, 92), (36, 86), (24, 72), (22, 52)]
    d.shape("horn2", taper(pts, 10.6, 3.2))
    d.shape("horn", taper(pts, 9, 2), shadow=False)
    clipped(d, taper(pts, 9, 2), lambda: d.shape("horntip", "M6 30 H40 V60 H6Z", shadow=False, line=False))


def highlandcow_portrait(d: Drawing):
    d.disc("glow", 100, 70, 40)
    d.band("far", "M-30 120 L20 94 L52 110 L88 80 L120 104 L150 86 L230 114")
    d.band("mid", hills(150, 8))
    # shaggy shoulders
    d.shape("hero", P(zig([(14, 210), (24, 166), (60, 140)], 6, 7) + [(140, 140)] + zig([(140, 140), (176, 166), (186, 210)], 6, 7)[1:]))
    coo_horn(d)
    flip(d, lambda: coo_horn(d))
    for side in (0, 1):
        ear = lambda: d.shape("hero", P([(126, 104)] + zig([(140, 96), (160, 104), (164, 114)], 3, -5) + [(138, 120)]))
        flip(d, ear) if side else ear()
    head = sym([(100, 72), (122, 76), (134, 92), (134, 118), (126, 138), (122, 156), (118, 172), (100, 178)])
    d.shape("hero", P(head))
    # cheek tufts
    d.shape("hero", P(zig([(128, 112), (138, 130), (128, 158)], 4, 6)), shadow=False, line=False)
    flip(d, lambda: d.shape("hero", P(zig([(128, 112), (138, 130), (128, 158)], 4, 6)), shadow=False, line=False))
    # muzzle
    d.shape("nose", P(sym([(100, 146), (114, 147), (122, 156), (120, 170), (110, 178), (100, 179)])))
    d.marks("mark", ellipse(91, 162, 3.8, 2.6) + ellipse(109, 162, 3.8, 2.6))
    d.stroke("mark", "M94 172 Q100 175 106 172", 1.6)
    # the famous fringe, hiding the eyes
    fringe = ([(66, 96, 1), (74, 78), (90, 70), (98, 60, 1), (104, 70), (118, 70), (130, 80), (136, 98, 1)]
              + [(130, 112, 1), (126, 104, 1), (122, 126, 1), (114, 112, 1), (108, 134, 1), (100, 116, 1), (92, 134, 1),
                 (86, 112, 1), (78, 126, 1), (74, 104, 1), (70, 112, 1)])
    d.shape("hero2", P(fringe), spot=True)
    d.stroke("hero", "M84 84 Q86 100 82 116 M96 78 Q98 100 96 124 M108 80 Q108 100 112 120 M120 86 Q120 100 122 112", 1.6, line=False)


def coo_side(d: Drawing):
    # far legs
    d.limb("hero2", "M78 132 L79 160", 11)
    d.limb("hero2", "M134 132 L133 160", 11)
    # tail
    d.limb("hero", "M152 104 Q160 120 158 140", 3)
    d.shape("hero", P(zig([(160, 136), (156, 148)], 2, 4)), shadow=False)
    body = [(52, 106), (70, 94), (110, 96), (146, 96), (158, 106), (160, 124)] + zig([(158, 138), (110, 142), (60, 140)], 9, -6)[:] + [(48, 124)]
    d.shape("hero", P(body))
    d.limb("hero", "M66 134 L65 162", 12)
    d.limb("hero", "M146 134 L147 162", 12)
    d.marks("mark", "M58 160 h14 v5 h-14Z M140 160 h14 v5 h-14Z M72 158 h14 v4 h-14Z M126 158 h14 v4 h-14Z")
    group(d, "translate(46 112) scale(1.3) translate(-46 -112)", lambda: coo_head(d))


def coo_head(d: Drawing):
    # horns: one swinging toward us, one behind
    d.shape("horn2", taper([(52, 98), (64, 88), (72, 74), (70, 62)], 5.8, 2.2))
    d.shape("horn", taper([(52, 98), (64, 88), (72, 74), (70, 62)], 4.5, 1.2), shadow=False)
    d.shape("hero", P([(28, 108), (34, 96), (52, 94), (62, 104), (58, 124), (48, 136), (34, 138), (26, 128)]))
    d.shape("horn2", taper([(40, 98), (26, 92), (16, 80), (16, 68)], 6.3, 2.2))
    d.shape("horn", taper([(40, 98), (26, 92), (16, 80), (16, 68)], 5, 1.2), shadow=False)
    d.shape("nose", P([(25, 122), (34, 122), (37, 131), (31, 137), (24, 134)]))
    d.marks("mark", ellipse(26.5, 129, 2, 1.5))
    d.shape("hero2", P(zig([(30, 96), (48, 92), (60, 100)], 5, 3) + [(56, 106, 1), (50, 116, 1), (46, 106, 1), (40, 118, 1), (36, 106, 1), (30, 114, 1)]),
            shadow=False, spot=True)
    d.shape("hero", P(zig([(58, 106), (68, 110), (74, 104)], 2, -4)), shadow=False, line=False)


def highlandcow_glen(d: Drawing):
    d.disc("glow", 150, 56, 18)
    peaks(d, "M-30 116 L16 82 L46 102 L84 66 L118 100 L146 84 L178 98 L230 86",
          ["M84 66 L95 77 L88 76 L83 81 L77 75 L72 78Z", "M16 82 L25 90 L19 89 L15 93 L10 88Z"])
    mist(d, 112, 3, 40, ".5")
    d.band("mid", hills(140, 6, 30))
    d.band("near", hills(160, 4, -20))
    group(d, "translate(100 156) scale(1.04) translate(-96 -164)", lambda: coo_side(d))
    d.band("ground", hills(178, 3, 10))
    for x in range(-6, 210, 13):
        d.shape("heather", scallop(x, 178 + (x * 7 % 6), 5.5, 7, 0.2), shadow=False, line=False)
    d.band("deep", hills(194, 3, 30), line=False)


# ================================================================ HEDGEHOG
def hedgehog(d: Drawing, leaf_on_back=False):
    """Hedgehog side-on, facing left, sitting on y=160."""
    dome = [(62, 140), (60, 112), (74, 84), (100, 68), (130, 70), (154, 88), (166, 116), (166, 146)]
    spines = [(60, 150, 1)] + zig(dome, 15, 11)[1:] + [(166, 156, 1), (120, 160), (80, 160)]
    d.shape("hero", P(spines))
    for i in range(16):
        a = math.radians(-170 + i * 10.5)
        cx, cy = 114, 132
        d.stroke("light", f"M{cx + 36 * math.cos(a):.1f} {cy + 46 * math.sin(a):.1f} L{cx + 52 * math.cos(a + 0.06):.1f} {cy + 62 * math.sin(a + 0.06):.1f}", 1.6, line=False)
    d.limb("hero2", "M88 154 L86 162", 7, shadow=False)
    d.limb("hero2", "M144 154 L146 162", 7, shadow=False)
    face = [(92, 104), (78, 98), (60, 106), (42, 122), (28, 130, 1), (30, 138), (48, 146), (72, 156), (100, 160), (112, 140)]
    d.shape("hero2", P(face))
    d.shape("hero2", circle(80, 104, 6), shadow=False)
    d.marks("mark", circle(80, 104, 3))
    d.marks("mark", circle(28, 133, 5.2))
    d.marks("light", circle(26.5, 131.5, 1.5))
    eye(d, 60, 120, 3.4)
    d.stroke("mark", "M36 142 Q42 145 48 144", 1.4)
    if leaf_on_back:
        d.shape("leaf1", oak(112, 72, 1.5, -20), shadow=False, spot=True)


def hedgehog_portrait(d: Drawing):
    d.disc("glow", 116, 98, 64)
    d.band("far", hills(150, 6))
    group(d, "translate(100 168) scale(1.08) translate(-100 -160)", lambda: hedgehog(d))
    d.band("ground", hills(170, 3, 20))
    grass(d, -10, 210, 172, 14, "near", 14)
    d.band("near", hills(186, 3), line=False)


def toadstool(d: Drawing, x, y, s=1.0):
    def draw():
        d.shape("light", "M-4 0 L-3 -14 Q0 -16 3 -14 L4 0Z")
        d.shape("pop", "M-14 -12 Q-14 -28 0 -28 Q14 -28 14 -12Z", spot=True)
        d.marks("light", circle(-6, -18, 2) + circle(4, -22, 1.8) + circle(8, -15, 1.5) + circle(-1, -15, 1.3))
    group(d, f"translate({x} {y}) scale({s})", draw)


def hedgehog_autumn(d: Drawing):
    d.disc("glow", 48, 60, 20)
    d.limb("dark", "M150 -10 L152 150", 16)
    d.limb("dark", "M152 66 Q170 52 196 46", 5)
    d.limb("dark", "M30 -10 L28 140", 10)
    for x, y, a, r in [(170, 44, 30, "leaf1"), (186, 40, -30, "leaf2"), (160, 30, 80, "leaf3"), (14, 30, 200, "leaf2"), (44, 22, 140, "leaf1")]:
        d.shape(r, oak(x, y, 1.1, a), shadow=False, line=False)
    d.band("far", hills(146, 4))
    d.band("ground", hills(158, 3, 30))
    toadstool(d, 160, 166, 1.1)
    toadstool(d, 178, 162, 0.7)
    group(d, "translate(96 170) scale(-.8 .8) translate(-100 -160)", lambda: hedgehog(d, True))
    for x, y, a, r in [(4, 176, -10, "leaf1"), (30, 182, 20, "leaf2"), (58, 186, -30, "leaf3"), (120, 184, 10, "leaf2"),
                       (146, 186, -20, "leaf1"), (176, 182, 30, "leaf3"), (90, 190, 0, "leaf1"), (20, 164, 60, "leaf3")]:
        d.shape(r, oak(x, y, 1.15, a), shadow=False, spot=r == "leaf2")
    for x, y in [(130, 172), (44, 168)]:
        d.shape("hero2", ellipse(x, y, 3.5, 4.5))
        d.shape("hero", f"M{x - 4.5} {y - 2} Q{x} {y - 8} {x + 4.5} {y - 2}Z", shadow=False)


# ================================================================ RED FOX
def fox_face(d: Drawing):
    for side in (0, 1):
        def ear():
            d.shape("hero", P([(112, 80, 1), (132, 30, 1), (146, 82, 1)]))
            d.shape("mark", P([(126, 46, 1), (132, 30, 1), (138, 46, 1), (132, 50)]), shadow=False)
            d.shape("light", P([(120, 76, 1), (131, 42), (140, 78, 1)]), shadow=False, line=False)
        flip(d, ear) if side else ear()
    face = sym([(100, 64), (124, 70), (142, 88), (150, 110, 1), (160, 128, 1), (146, 128), (154, 144, 1), (136, 140),
                (124, 152), (110, 164), (100, 168)])
    d.shape("hero", P(face))
    cheek = sym([(100, 118), (110, 124), (124, 128), (146, 128, 1), (136, 140), (124, 152), (110, 164), (100, 168)])
    d.shape("light", P(cheek), shadow=False, spot=True)
    d.shape("hero", P(sym([(100, 74), (110, 82), (112, 120), (108, 140), (100, 144)])), shadow=False, line=False)
    d.marks("mark", P(sym([(100, 140), (108, 141), (108, 147), (100, 152)])))
    d.stroke("mark", "M100 152 V158 M92 160 Q100 166 108 160", 1.6)
    for x, a in [(80, 22), (120, -22)]:
        d.shape("eye", ellipse(x, 108, 8, 5), extra=f'transform="rotate({a} {x} 108)"', shadow=False)
        d.marks("mark", ellipse(x, 108, 1.8, 4.2))
        d.stroke("mark", f"M{x - 8 if x < 100 else x + 8} {104 if x < 100 else 104} L{x + 9 if x < 100 else x - 9} {113}", 1.4, line=False)


def redfox_portrait(d: Drawing):
    d.disc("glow", 100, 100, 62)
    for x, y, a, r in [(14, 160, -40, "far"), (186, 160, -140, "far"), (6, 120, -10, "mid"), (194, 120, -170, "mid")]:
        d.shape(r, leaf(x, y, 50, 12, a), line=False)
    d.shape("hero", P(zig([(30, 210), (40, 170), (70, 150)], 4, 6) + [(130, 150)] + zig([(130, 150), (160, 170), (170, 210)], 4, 6)[1:]))
    d.shape("light", P(zig([(78, 210), (82, 172), (100, 160)], 3, 5) + zig([(100, 160), (118, 172), (122, 210)], 3, 5)[1:]), shadow=False, line=False)
    group(d, "translate(100 112) scale(1.02) translate(-100 -112)", lambda: fox_face(d))


def fox_side(d: Drawing):
    tail = [(134, 104), (152, 112), (166, 126), (176, 140)]
    d.limb("hero2", P([(80, 116), (88, 132), (90, 150)], False), 5)
    d.limb("hero2", P([(122, 112), (130, 130), (124, 150)], False), 5)
    d.limb("mark", P([(88, 136), (90, 150)], False), 5, shadow=False)
    d.limb("mark", P([(129, 136), (124, 150)], False), 5, shadow=False)
    d.shape("hero", taper(tail, 7, 4, wf=lambda t: 5 + 9 * math.sin(math.pi * min(1, t * 1.15)) + 2))
    d.shape("light", taper(tail[2:] + [(182, 148)], 7, 1, wf=lambda t: 8 * (1 - t) + 1.5), shadow=False, spot=True)
    d.shape("hero", P([(58, 106), (68, 96), (100, 98), (128, 96), (140, 104), (134, 116), (110, 120), (80, 120), (62, 118)]))
    d.limb("hero", P([(68, 114), (64, 132), (60, 150)], False), 5.5)
    d.limb("hero", P([(132, 110), (144, 130), (142, 150)], False), 5.5)
    d.limb("mark", P([(64, 136), (60, 150)], False), 5.5, shadow=False)
    d.limb("mark", P([(144, 134), (142, 150)], False), 5.5, shadow=False)
    # neck + head
    d.shape("hero", P([(76, 100), (62, 84), (50, 76), (40, 80), (48, 96), (58, 118)]))
    d.shape("light", P([(44, 86), (56, 100), (62, 116), (54, 112), (44, 96)]), shadow=False)
    d.shape("hero", P([(56, 76, 1), (60, 58, 1), (66, 80, 1)]))
    d.shape("hero", P([(48, 70, 1), (50, 54, 1), (58, 72, 1)]))
    d.shape("hero", P([(62, 78), (54, 70), (42, 72), (30, 82), (18, 88, 1), (22, 92), (36, 94), (52, 92), (62, 88)]))
    d.shape("light", P([(22, 92), (36, 94), (52, 92), (46, 86), (30, 90, 1)]), shadow=False, line=False)
    d.marks("mark", circle(19, 88, 2.4) + "M48 54.5 L50 54 L54 63 L50 62Z M58.5 58.5 L60 58 L62 66 L59 65Z")
    d.marks("mark", ellipse(44, 80, 2.6, 1.8))


def redfox_snow(d: Drawing):
    d.disc("glow", 150, 54, 18)
    for x, h in [(10, 70), (30, 92), (178, 84), (196, 64), (160, 60)]:
        pine(d, x, 132, h, "near", snow=True, line=x in (30, 178))
    d.band("far", hills(130, 4), line=False)
    d.band("light", "M-30 146 Q40 132 100 140 T230 136")
    group(d, "translate(100 156) scale(.94) translate(-106 -150)", lambda: fox_side(d))
    d.stroke("far", "M30 166 h8 M50 172 h6 M150 168 h8 M170 160 h6", 2, line=False)
    d.band("far", hills(186, 3, 20), line=False)


# ================================================================ BROWN BEAR
def brownbear_portrait(d: Drawing):
    d.disc("glow", 100, 92, 56)
    for x, h in [(14, 96), (34, 76), (168, 80), (188, 100)]:
        pine(d, x, 172, h, "near", line=False)
    d.band("far", hills(176, 4), line=False)
    d.shape("hero", P(zig([(6, 210), (16, 160), (60, 130)], 6, 7) + [(140, 130)] + zig([(140, 130), (184, 160), (194, 210)], 6, 7)[1:]))
    for x in (56, 144):
        d.shape("hero", circle(x, 58, 17))
        d.shape("hero2", circle(x, 60, 9), shadow=False)
    head = [(100, 46)] + zig([(122, 50), (146, 70), (156, 98)], 4, 4)[1:] + zig([(156, 98), (150, 126), (130, 146), (100, 156)], 5, 4)[1:]
    d.shape("hero", P(sym(head)))
    d.shape("hero2", P(sym([(100, 104), (114, 106), (126, 118), (126, 134), (116, 146), (100, 150)])))
    d.marks("mark", P(sym([(100, 108), (110, 109), (112, 116), (104, 124), (100, 126)])))
    d.marks("light", ellipse(97, 112, 2.5, 1.6))
    d.stroke("mark", "M100 126 V134 M90 138 Q100 144 110 138", 2)
    eye(d, 80, 92, 4)
    eye(d, 120, 92, 4)
    d.stroke("mark", "M72 84 Q80 80 88 84 M112 84 Q120 80 128 84", 1.6, line=False)


def bear_side(d: Drawing):
    d.limb("hero2", P([(70, 126), (72, 160)], False), 15)
    d.limb("hero2", P([(140, 124), (148, 140), (144, 160)], False), 15)
    body = [(56, 106), (68, 86), (88, 76), (106, 82), (130, 88), (150, 96), (164, 108), (164, 126), (152, 134),
            (120, 136), (90, 136), (66, 130)]
    d.shape("hero", P(body), spot=True)
    d.shape("hero2", P([(70, 90), (88, 78), (104, 84), (90, 92), (74, 100)]), shadow=False, line=False)
    d.limb("hero", P([(86, 126), (84, 162)], False), 16)
    d.limb("hero", P([(152, 120), (158, 142), (154, 162)], False), 16)
    d.marks("mark", "M76 160 h16 l2 5 h-20Z M146 160 h16 l2 5 h-20Z")
    group(d, "translate(64 112) scale(1.28) translate(-64 -112)", lambda: bear_head(d))


def bear_head(d: Drawing):
    head = [(70, 104), (62, 92), (50, 88), (38, 94), (26, 104), (16, 110, 1), (16, 116), (30, 122), (50, 126), (68, 122)]
    d.shape("hero", P(head))
    d.shape("hero", circle(54, 86, 6.5))
    d.shape("hero2", circle(54, 87, 3.2), shadow=False)
    d.shape("hero2", P([(30, 104), (18, 110, 1), (18, 116), (30, 120), (40, 116), (38, 108)]), shadow=False, line=False)
    d.marks("mark", ellipse(18, 111, 3.5, 3))
    eye(d, 38, 102, 2.2)
    d.stroke("mark", "M24 120 Q30 122 36 120", 1.4)


def brownbear_forest(d: Drawing):
    d.disc("glow", 64, 62, 24)
    for x, h in [(150, 90), (170, 112), (188, 92), (132, 70), (8, 80), (24, 64)]:
        pine(d, x, 146, h, "near", line=x < 140)
    d.band("far", hills(140, 4), line=False)
    d.band("mid", hills(150, 3, 30))
    group(d, "translate(100 164) scale(1.04) translate(-90 -164)", lambda: bear_side(d))
    d.band("ground", hills(170, 3, 20))
    for x, y, r in [(24, 176, 8), (150, 182, 10), (172, 176, 6)]:
        d.shape("far", ellipse(x, y, r * 1.4, r * 0.8))
    d.band("deep", hills(190, 3, 40), line=False)


# ================================================================ LYNX
def lynx_portrait(d: Drawing):
    d.disc("glow", 100, 104, 70)
    for x, h in [(12, 100), (32, 80), (170, 84), (190, 104)]:
        pine(d, x, 190, h, "near", snow=True, line=False)
    d.band("light", hills(184, 4), line=False)
    group(d, "translate(100 120) scale(.88) translate(-100 -112)", lambda: lynx_face(d))


def lynx_face(d: Drawing):
    d.shape("hero", P(zig([(24, 210), (36, 172), (66, 156)], 4, 6) + [(134, 156)] + zig([(134, 156), (164, 172), (176, 210)], 4, 6)[1:]))
    for side in (0, 1):
        def ear():
            d.shape("hero", P([(112, 70, 1), (136, 30, 1), (148, 76, 1)]))
            d.shape("mark", P([(130, 40, 1), (136, 30, 1), (142, 42, 1), (136, 46)]), shadow=False)
            d.stroke("mark", "M136 32 L138 8", 3.2)
            d.shape("light", P([(120, 68, 1), (135, 42), (142, 72, 1)]), shadow=False, line=False)
        flip(d, ear) if side else ear()
    # ruff
    ruff = [(100, 112)] + zig([(134, 98), (160, 120), (164, 146), (146, 162)], 6, 9)[1:] + [(100, 172)]
    d.shape("hero2", P(sym(ruff)))
    d.stroke("mark", "M148 116 L156 128 M152 138 L160 146", 2)
    flip(d, lambda: d.stroke("mark", "M148 116 L156 128 M152 138 L160 146", 2))
    head = sym([(100, 60), (122, 64), (138, 78), (142, 98), (138, 118), (124, 136), (112, 148), (100, 150)])
    d.shape("hero", P(head))
    d.shape("light", P(sym([(100, 112), (110, 112), (122, 122), (124, 134), (114, 146), (100, 150)])), shadow=False, line=False)
    d.marks("mark", "".join(circle(x, y, 2) for x, y in [(86, 72), (114, 72), (78, 80), (122, 80), (100, 76), (92, 66), (108, 66),
                                                        (130, 96), (70, 96), (134, 108), (66, 108)]))
    d.marks("pop", P(sym([(100, 116), (108, 116), (106, 122), (100, 126)])))
    d.stroke("mark", "M100 126 V132 M92 136 Q100 140 108 136", 1.6)
    for x, a in [(84, 12), (116, -12)]:
        d.shape("eye", ellipse(x, 100, 7.5, 5.5), extra=f'transform="rotate({a} {x} 100)"', shadow=False)
        d.marks("mark", ellipse(x, 100, 2, 4.4))
    d.stroke("mark", "M76 96 Q84 90 92 94 M124 96 Q116 90 108 94", 1.6, line=False)


def lynx_side(d: Drawing):
    d.limb("legs2", P([(84, 116), (86, 146), (87, 162)], False), 8)
    d.limb("legs2", P([(126, 112), (132, 138), (128, 162)], False), 8)
    d.shape("legs2", ellipse(88, 164, 7, 4), shadow=False)
    d.shape("legs2", ellipse(128, 164, 7, 4), shadow=False)
    d.limb("hero", P([(146, 98), (156, 94), (160, 92)], False), 8)
    d.limb("mark", P([(157, 93), (160, 92)], False), 8, shadow=False)
    d.shape("hero", P([(58, 102), (72, 92), (104, 94), (130, 86), (146, 92), (150, 106), (140, 120), (108, 122), (78, 122), (60, 118)]))
    d.limb("hero", P([(68, 112), (66, 144), (64, 162)], False), 9.5)
    d.limb("hero", P([(140, 108), (148, 136), (144, 162)], False), 9.5)
    for x in (64, 144):
        d.shape("hero", ellipse(x - 2, 164, 9, 5), shadow=False)
        d.stroke("mark", f"M{x - 6} 166 v-3 M{x - 2} 167 v-3 M{x + 2} 166 v-3", 1.2, line=False)
    d.marks("mark", "".join(circle(x, y, 1.6) for x, y in [(84, 102), (98, 100), (112, 102), (124, 98), (136, 100), (92, 112),
                                                          (106, 112), (120, 110), (134, 110), (146, 116), (70, 128), (144, 128)]))
    group(d, "translate(50 96) scale(1.12) translate(-50 -88)", lambda: lynx_side_head(d))


def lynx_side_head(d: Drawing):
    d.shape("hero", P([(46, 72, 1), (44, 52, 1), (56, 70, 1)]))
    d.stroke("mark", "M44 53 L43 40", 2.4)
    d.shape("hero", P([(58, 76, 1), (60, 56, 1), (68, 76, 1)]))
    d.stroke("mark", "M60 57 L62 44", 2.4)
    d.shape("mark", P([(44, 53, 1), (46, 62, 1), (42, 60, 1)]), shadow=False)
    d.shape("hero", P([(66, 80), (60, 70), (46, 68), (34, 74), (28, 84), (30, 96), (42, 104), (58, 104), (68, 94)]))
    ruff = [(64, 86)] + zig([(68, 96), (62, 110), (44, 114), (32, 106)], 5, -6)[1:] + [(38, 98), (56, 98)]
    d.shape("hero2", P(ruff), shadow=False)
    d.stroke("mark", "M60 104 L64 112 M50 106 L50 114", 1.8, line=False)
    d.shape("light", P([(30, 90), (34, 98), (44, 100), (40, 92)]), shadow=False, line=False)
    d.marks("pop", P([(27, 86), (32, 85), (30, 90)]))
    d.shape("eye", ellipse(38, 80, 3.4, 2.6), shadow=False)
    d.marks("mark", ellipse(38, 80, 1.1, 2.2))
    d.stroke("mark", "M30 92 Q34 95 38 93", 1.3)


def lynx_snow(d: Drawing):
    d.disc("glow", 46, 56, 18)
    for x, h, r in [(140, 110, "mid"), (168, 130, "near"), (192, 96, "mid"), (8, 90, "near"), (30, 70, "mid")]:
        pine(d, x, 140, h, r, snow=True, line=x == 168)
    d.band("light", "M-30 144 Q60 130 120 140 T230 136")
    group(d, "translate(102 160) scale(1.04) translate(-96 -166)", lambda: lynx_side(d))
    d.stroke("far", "M20 176 q6 -3 12 0 M150 178 q6 -3 12 0", 2, line=False)
    d.band("far", hills(190, 3, 20), line=False)


# ================================================================ IBEX
IBEX_HORN = [(98, 64), (104, 40), (122, 24), (148, 22), (168, 36), (176, 60), (172, 86)]


def ibex_horns(d: Drawing, pts=IBEX_HORN, w=11):
    shape = taper(pts, w, 2.2)
    d.shape("horn", shape, spot=True)
    s = spline(pts, 6)
    ridges = ""
    for i in range(3, len(s) - 6, 3):
        (x0, y0), (x1, y1) = s[i - 1], s[i + 1]
        dx, dy = x1 - x0, y1 - y0
        h = math.hypot(dx, dy) or 1
        t = i / (len(s) - 1)
        ww = w + (2.2 - w) * t
        ridges += f"M{s[i][0] + dy / h * ww * 0.95:.1f} {s[i][1] - dx / h * ww * 0.95:.1f} L{s[i][0] - dy / h * ww * 0.2:.1f} {s[i][1] + dx / h * ww * 0.2:.1f} "
    d.stroke("horn2", ridges, 2, line=False)


def ibex_portrait(d: Drawing):
    peaks(d, "M-30 150 L20 112 L50 130 L84 96 L118 128 L150 104 L230 140",
          ["M84 96 L96 108 L89 107 L84 112 L78 106 L72 109Z", "M150 104 L160 112 L154 111 L150 115 L144 110Z"])
    d.band("mid", hills(176, 6))
    group(d, "translate(96 128) scale(.8) translate(-100 -110)", lambda: ibex_head(d))


def ibex_head(d: Drawing):
    d.shape("hero", P([(84, 120), (110, 80), (134, 80), (156, 120), (172, 160), (184, 230, 1), (70, 230, 1), (74, 160)]))
    d.shape("hero", P([(120, 70, 1), (142, 56), (150, 64), (130, 82, 1)]))
    ibex_horns(d, [(108, 62), (112, 36), (130, 18), (156, 18), (176, 34), (184, 62), (178, 92)], 13)
    head = [(122, 82), (112, 60), (96, 58), (80, 70), (60, 92), (44, 108), (40, 118, 1), (46, 126), (62, 128), (82, 120), (104, 116), (126, 110)]
    d.shape("hero", P(head))
    d.shape("hero2", P([(46, 126), (62, 128), (64, 136)] + [(60, 160, 1), (56, 146, 1), (50, 154, 1), (50, 136)]), spot=False)
    d.shape("light", P([(42, 118), (46, 126), (58, 126), (54, 118)]), shadow=False, line=False)
    d.marks("mark", ellipse(46, 112, 2.6, 1.8))
    d.stroke("mark", "M44 122 Q50 124 54 122", 1.4)
    d.shape("eye", ellipse(92, 80, 4.6, 3.6), shadow=False)
    d.marks("mark", ellipse(92, 80, 3.2, 1.4))
    d.stroke("hero2", "M82 70 Q90 64 100 68", 1.8, line=False)


def ibex_side(d: Drawing):
    d.limb("hero2", P([(82, 126), (84, 146), (82, 160)], False), 7.5)
    d.limb("hero2", P([(130, 124), (138, 142), (132, 160)], False), 7.5)
    d.shape("hero", P([(60, 104), (72, 94), (104, 96), (132, 92), (146, 100), (146, 116), (136, 128), (106, 130), (78, 130), (62, 122)]))
    d.shape("hero", P([(144, 98), (152, 92, 1), (150, 104)]))
    d.limb("hero", P([(70, 124), (68, 146), (70, 160)], False), 8.5)
    d.limb("hero", P([(140, 116), (148, 142), (144, 160)], False), 8.5)
    d.marks("mark", "M64 158 h10 l1 4 h-12Z M138 158 h10 l1 4 h-12Z")
    d.shape("hero", P([(74, 100), (64, 84), (58, 74), (50, 76), (52, 96), (62, 116)]))
    ibex_horns(d, [(58, 70), (58, 48), (70, 32), (90, 28), (106, 38), (112, 56)], 6.5)
    d.shape("hero", P([(64, 76), (58, 66), (48, 66), (36, 76), (28, 86, 1), (32, 92), (44, 90), (60, 86)]))
    d.shape("hero2", P([(34, 90), (44, 90), (44, 102, 1), (40, 96, 1), (36, 100, 1)]), shadow=False)
    d.marks("mark", circle(31, 86, 1.6))
    eye(d, 48, 74, 2)


def ibex_ledge(d: Drawing):
    d.disc("glow", 150, 50, 16)
    peaks(d, "M-30 118 L14 80 L40 96 L80 50 L112 88 L140 70 L170 94 L230 74",
          ["M80 50 L93 64 L86 63 L80 69 L73 62 L67 66Z", "M140 70 L149 79 L143 78 L139 82 L134 77Z",
           "M14 80 L22 88 L17 87 L13 91 L8 86Z"])
    d.band("mid", "M-30 150 L20 128 L56 144 L100 120 L150 140 L230 126")
    # the crag the ibex stands on
    d.shape("near", "M-30 230 L-30 176 L20 168 L40 160 L60 158 L130 160 L150 166 L162 178 L176 230Z")
    d.stroke("deep", "M40 180 L50 200 M110 172 L104 190 M140 176 L150 196", 2, line=False)
    group(d, "translate(98 160) scale(1.06) translate(-100 -160)", lambda: ibex_side(d))
    d.band("deep", hills(196, 3, 40), line=False)


# ================================================================ RED SQUIRREL
def squirrel(d: Drawing, nut=True):
    """Sitting upright, facing left, holding a nut. Sits on y=170."""
    tail = [(128, 166), (150, 150), (160, 116), (152, 80), (140, 54), (126, 40), (110, 38)]
    d.shape("hero", taper(tail, 6, 6, wf=lambda t: 8 + 16 * math.sin(math.pi * (0.15 + 0.8 * t))), spot=True)
    d.shape("hero2", taper(tail[1:-1], 3, 3, wf=lambda t: 3 + 6 * math.sin(math.pi * t)), shadow=False, line=False)
    body = [(84, 92), (100, 90), (122, 108), (134, 142), (130, 166), (110, 172), (86, 170), (74, 150), (72, 120)]
    d.shape("hero", P(body))
    d.shape("light", P([(80, 112), (90, 110), (98, 130), (100, 160), (90, 170), (78, 156), (74, 130)]), shadow=False, line=False)
    d.shape("hero", ellipse(116, 162, 18, 10))
    d.shape("hero", P([(98, 168), (116, 166), (124, 172), (100, 174)]))
    # head
    d.shape("hero", P([(98, 56, 1), (96, 36, 1), (90, 26, 1), (100, 34), (106, 50)]))
    d.shape("hero", P([(84, 58), (74, 56), (60, 64), (50, 76), (48, 82, 1), (54, 88), (70, 94), (90, 96), (104, 84), (104, 66)]))
    d.shape("hero", P([(86, 52, 1), (86, 32, 1), (80, 22, 1), (92, 30), (96, 48)]))
    d.shape("light", P([(52, 86), (62, 92), (76, 94), (70, 86), (58, 84)]), shadow=False, line=False)
    d.marks("mark", circle(49, 81, 2.2))
    eye(d, 68, 70, 3.6)
    if nut:
        d.limb("hero", P([(84, 106), (70, 102), (62, 98)], False), 6)
        d.shape("nut", ellipse(58, 96, 7, 8))
        d.shape("nut2", "M50 92 Q58 82 66 92 Q58 88 50 92Z", shadow=False)
        d.limb("hero", P([(88, 112), (72, 108), (64, 102)], False), 6, shadow=False)


def redsquirrel_portrait(d: Drawing):
    d.disc("glow", 92, 90, 60)
    for x, y, a in [(196, 160, 200), (190, 130, 170), (6, 150, -20)]:
        d.shape("near", leaf(x, y, 40, 9, a), line=False)
    d.band("far", hills(176, 4))
    d.limb("dark", "M-10 180 C40 174 120 176 210 168", 10)
    group(d, "translate(94 174) scale(.92) translate(-100 -172)", lambda: squirrel(d))


def needles(d: Drawing, x, y, s=1.0, role="near"):
    for a in range(-170, 10, 20):
        r = math.radians(a)
        d.stroke(role, f"M{x} {y} L{x + 16 * s * math.cos(r):.1f} {y + 16 * s * math.sin(r):.1f}", 2.2, line=False)


def cone(d: Drawing, x, y, s=1.0):
    d.shape("nut", ellipse(x, y + 8 * s, 5 * s, 9 * s))
    d.stroke("nut2", f"M{x - 5 * s} {y + 4 * s} L{x + 5 * s} {y + 8 * s} M{x - 5 * s} {y + 10 * s} L{x + 5 * s} {y + 13 * s} "
                     f"M{x + 5 * s} {y + 4 * s} L{x - 5 * s} {y + 8 * s} M{x + 5 * s} {y + 10 * s} L{x - 5 * s} {y + 13 * s}", 1.2, line=False)


def redsquirrel_pine(d: Drawing):
    d.disc("glow", 150, 60, 22)
    for x, h in [(20, 100), (44, 76), (180, 80)]:
        pine(d, x, 160, h, "far", line=False)
    d.band("mid", hills(166, 4))
    d.limb("trunk", "M168 230 L172 -10", 22)
    d.limb("trunk", "M170 132 C130 128 70 134 -10 128", 9)
    for x, y in [(30, 128), (60, 128), (100, 128), (8, 128)]:
        needles(d, x, y)
    cone(d, 40, 130, 1.0)
    cone(d, 120, 132, 0.9)
    group(d, "translate(94 127) scale(.78) translate(-100 -172)", lambda: squirrel(d))
    for x, y in [(150, 128), (186, 80)]:
        needles(d, x, y, 1.1)
    d.band("near", hills(190, 3), line=False)


# ================================================================ GOLDEN EAGLE
def eagle_spread(d: Drawing):
    """Golden eagle, front-on, wings up and spread, talons out. Centred on (100, 100)."""
    d.shape("mark", P([(92, 122), (108, 122), (122, 150, 1), (112, 156), (100, 158), (88, 156), (78, 150, 1)]))
    d.stroke("hero", "M94 130 L90 152 M100 130 V156 M106 130 L110 152", 1.4, line=False)

    def wing():
        outline = [(98, 84), (80, 70), (64, 62)] + fingers(52, 72, 16, 31, 228, 130, 5) + [(52, 96), (66, 102), (80, 105), (96, 100)]
        d.shape("mark", P(outline))
        d.shape("hero", P([(98, 84), (80, 70), (62, 62), (46, 63), (44, 72), (56, 82), (72, 90), (94, 96)]), shadow=False)
        d.shape("hero2", P([(94, 82), (80, 73), (62, 67), (70, 77), (86, 86)]), shadow=False, line=False)
        d.stroke("mark", "M60 96 L64 88 M70 100 L73 92 M80 102 L82 95", 1.4, line=False)
    wing()
    flip(d, wing)
    d.shape("hero", P([(100, 64), (112, 72), (116, 92), (111, 116), (100, 128), (89, 116), (84, 92), (88, 72)]))
    d.stroke("mark", "M94 96 l3 3 l3 -3 M100 104 l3 3 l3 -3 M94 110 l3 3 l3 -3", 1.3, line=False)
    # feathered legs, yellow feet, talons out
    d.limb("hero", "M94 114 L90 132", 10)
    d.limb("hero", "M106 114 L110 132", 10)
    for fx, k in [(89, 1), (111, -1)]:
        toes = [(-8 * k, 10, 125 if k > 0 else 55), (-1 * k, 13, 98 if k > 0 else 82), (7 * k, 10, 70 if k > 0 else 110)]
        for dx, dy, a in toes:
            d.limb("pop", f"M{fx} 134 L{fx + dx} {134 + dy}", 3.6, shadow=False)
            d.marks("dark", claw(fx + dx, 134 + dy, a, 0.9))
    # head turned to profile, hooked beak
    d.shape("hero2", circle(100, 62, 12))
    d.shape("hero2", P(zig([(108, 70), (112, 78), (104, 84)], 3, -3) + [(96, 74)]), shadow=False, line=False)
    d.shape("beak", P([(92, 55, 1), (84, 55), (78, 60), (77, 69, 1), (81, 64), (87, 64), (92, 65, 1)]))
    d.shape("pop", P([(93, 54), (89, 54), (88, 59), (92, 61)]), shadow=False)
    d.shape("eye", circle(97, 58, 2.6), shadow=False)
    d.marks("mark", circle(96.6, 58, 1.4))
    d.stroke("mark", "M92 55 Q97 52 103 55", 1.6)


def goldeneagle_highlands(d: Drawing):
    peaks(d, "M-30 140 L10 116 L40 128 L74 96 L104 124 L136 102 L164 118 L192 96 L230 120",
          ["M74 96 L84 106 L78 105 L73 110 L67 104 L63 107Z", "M136 102 L145 110 L139 109 L135 113 L130 108Z",
           "M192 96 L200 103 L194 102 L190 106 L185 101Z"])
    mist(d, 130, 4, 44, ".6")
    d.band("mid", hills(156, 8, 30))
    d.band("near", hills(178, 5, -10))
    birds(d, [(30, 56, 0.7), (40, 50, 0.5)])
    group(d, "translate(100 92) scale(1.0) translate(-100 -100)", lambda: eagle_spread(d))
    d.band("deep", hills(194, 3, 30), line=False)


def goldeneagle_portrait(d: Drawing):
    d.disc("glow", 128, 78, 46)
    peaks(d, "M-30 168 L20 140 L60 156 L100 128 L140 152 L230 132", ["M100 128 L110 137 L104 136 L99 141 L94 135 L89 138Z"])
    d.band("mid", hills(186, 5))
    d.shape("hero", P([(108, 34), (136, 40), (154, 60), (162, 94), (176, 128), (196, 214, 1), (40, 214, 1), (62, 160), (72, 124),
                       (78, 100), (82, 82)]))
    nape = ([(82, 74), (88, 48), (108, 34), (136, 40), (152, 58)] + zig([(158, 72), (166, 104), (172, 134)], 5, 7)[1:]
            + zig([(156, 126), (136, 104), (114, 88)], 5, 6)[1:] + [(96, 80)])
    d.shape("hero2", P(nape), spot=True)
    d.stroke("hero", "M150 76 L156 96 M140 82 L146 104 M130 90 L134 104", 1.6, line=False)
    d.shape("beak2", P([(86, 58, 1), (74, 60), (62, 66), (54, 76), (51, 88), (54, 100, 1), (58, 91), (64, 85), (74, 82), (86, 82, 1)]))
    clipped(d, P([(86, 58, 1), (74, 60), (62, 66), (54, 76), (51, 88), (54, 100, 1), (58, 91), (64, 85), (74, 82), (86, 82, 1)]),
            lambda: d.shape("beak", "M30 50 H64 V110 H30Z", shadow=False, line=False))
    d.shape("beak2", P([(84, 82, 1), (70, 85), (62, 90, 1), (72, 92), (86, 89, 1)]), shadow=False)
    d.shape("pop", P([(88, 56, 1), (80, 59), (78, 70), (84, 82, 1), (92, 76)]), shadow=False)
    d.stroke("pop", "M84 85 L100 86", 2.4, line=False)
    d.marks("mark", ellipse(81, 66, 2.4, 1.6))
    d.shape("eye", circle(102, 64, 6), shadow=False)
    d.marks("mark", circle(101, 64, 3.4))
    d.marks("light", circle(99.5, 62.5, 1.3))
    d.shape("hero", P([(88, 60), (98, 52), (114, 54), (110, 58), (98, 58), (92, 62)]), shadow=False)


# ================================================================ BARN OWL
OWL_DISC = sym([(100, 57, 1), (112, 45), (128, 43), (141, 55), (145, 78), (138, 105), (121, 127), (107, 140), (100, 145)])


def owl_face(d: Drawing):
    d.shape("hero", P(sym([(100, 28), (128, 32), (150, 50), (158, 80), (152, 112), (134, 138), (100, 150)])))
    d.marks("hero2", "".join(circle(x, y, 1.5) for x, y in [(90, 36), (104, 34), (116, 38), (96, 42), (110, 42), (124, 44), (80, 42), (72, 48)]))
    d.shape("rim", P(sym([(100, 50, 1), (112, 38), (130, 36), (147, 52), (151, 78), (143, 108), (125, 132), (108, 146), (100, 152)])), shadow=False)
    d.shape("light", P(OWL_DISC), shadow=False)
    d.shape("ridge", P([(100, 58, 1), (104, 70), (103, 90), (100, 97), (97, 90), (96, 70)]), shadow=False, line=False)
    for x in (82, 118):
        d.shape("ridge", ellipse(x + (3 if x < 100 else -3), 86, 9, 11), shadow=False, line=False)
        d.marks("mark", ellipse(x, 84, 6.5, 7.5))
        d.marks("light", circle(x - 2, 81.5, 1.8))
    d.shape("beak", P([(96, 96), (104, 96), (102, 108), (100, 113, 1), (98, 108)]), shadow=False)


def barnowl_portrait(d: Drawing):
    d.disc("glow", 100, 96, 68)
    d.marks("light", "".join(circle(x, y, r) for x, y, r in [(30, 54, 1.6), (166, 46, 1.4), (174, 76, 1.2), (24, 90, 1.2)]))
    d.band("far", hills(176, 5), line=False)
    d.shape("hero", P([(36, 214, 1), (42, 156), (66, 124), (134, 124), (158, 156), (164, 214, 1)]))
    d.shape("light", P(sym([(100, 128), (118, 132), (128, 160), (126, 214, 1)])), shadow=False)
    d.marks("hero2", "".join(circle(x, y, 1.2) for x, y in [(92, 160), (104, 168), (112, 154), (88, 176), (100, 184), (114, 180), (96, 146)]))
    for k in (0, 1):
        def wing():
            d.shape("hero", P([(48, 214, 1), (50, 166), (62, 136), (78, 138), (82, 170), (82, 214, 1)]), spot=True)
            d.stroke("hero2", "M56 176 L78 172 M54 190 L80 188 M56 204 L80 202", 2, line=False)
        flip(d, wing) if k else wing()
    group(d, "translate(100 98) scale(1.02) translate(-100 -98)", lambda: owl_face(d))


def owl_flying(d: Drawing):
    d.limb("light", "M95 128 L92 146", 6)
    d.limb("light", "M105 128 L108 146", 6)
    for x, k in [(92, 1), (108, -1)]:
        d.stroke("beak2", f"M{x} 147 l{-4 * k} 6 M{x} 147 l0 7 M{x} 147 l{4 * k} 6", 1.6)

    def wing():
        outline = [(96, 96), (74, 76), (52, 60), (40, 54)] + fingers(40, 66, 10, 20, 236, 150, 5)[1:] + [(42, 84), (56, 100), (76, 110), (94, 110)]
        d.shape("light", P(outline))
        d.shape("hero", P([(96, 96), (74, 76), (52, 60), (40, 55), (34, 60), (46, 70), (68, 86), (90, 100)]), shadow=False)
        d.stroke("hero2", "M36 70 L48 66 M34 78 L46 74 M40 86 L50 80", 1.8, line=False)
        d.marks("hero2", circle(60, 78, 1.3) + circle(72, 86, 1.3) + circle(52, 70, 1.3))
    wing()
    flip(d, wing)
    d.shape("light", P(sym([(100, 84), (112, 92), (114, 112), (108, 128), (100, 134)])))
    group(d, "translate(100 76) scale(.42) translate(-100 -92)", lambda: owl_face(d))


def barnowl_dusk(d: Drawing):
    d.disc("glow", 150, 52, 20)
    d.band("far", hills(132, 6))
    d.shape("dark", "M14 134 L14 110 L30 96 L46 110 L46 134Z")
    d.shape("glow2", rrect(26, 112, 8, 8, 1), shadow=False)
    d.band("mid", hills(150, 4, 30))
    for x in (40, 84, 128, 172):
        d.shape("dark", rrect(x - 3, 140 + (x % 7), 6, 30, 1.5))
    d.stroke("dark", "M37 150 L178 156 M37 158 L178 164", 1.2)
    d.band("near", hills(170, 4, 20))
    grass(d, -10, 210, 172, 16, "near", 13)
    group(d, "translate(100 94) scale(.88) translate(-100 -100)", lambda: owl_flying(d))
    d.band("deep", hills(190, 3), line=False)


# ================================================================ ALBATROSS
def albatross_portrait(d: Drawing):
    d.disc("glow", 136, 92, 48)
    d.band("far", waves(150, 4, 30))
    d.band("mid", waves(168, 4, 34))
    d.band("near", waves(186, 4, 38), line=False)
    d.shape("light", P([(96, 40), (124, 38), (146, 52), (152, 76), (150, 110), (156, 150), (168, 214, 1), (60, 214, 1), (72, 160),
                        (82, 128), (80, 104), (76, 84), (80, 60)]))
    d.shape("hero", P([(146, 98), (166, 104), (186, 128), (196, 214, 1), (136, 214, 1), (146, 164), (144, 126)]), spot=True)
    d.stroke("hero2", "M160 130 L172 190 M152 136 L160 200", 1.6, line=False)
    bill = P([(84, 54, 1), (68, 58), (50, 63), (36, 66), (28, 71), (26, 79), (29, 87, 1), (32, 79), (42, 76), (62, 76), (82, 77, 1)])
    d.shape("beak", bill)
    clipped(d, bill, lambda: d.shape("pop", "M10 40 H40 V100 H10Z", shadow=False, line=False))
    d.shape("beak", P([(82, 77, 1), (60, 78), (42, 80), (34, 84, 1), (46, 87), (64, 86), (84, 84, 1)]), shadow=False)
    d.stroke("beak2", "M82 64 Q60 66 38 72", 1.3, line=False)
    d.shape("mark", P([(82, 58), (96, 54), (112, 56), (122, 62), (106, 64), (90, 66)]), shadow=False)
    d.marks("mark", circle(98, 60, 3.6))
    d.marks("light", circle(97, 58.8, 1.1))


def albatross_glide(d: Drawing):
    d.shape("light", cloud(20, 52, 1.1), shadow=False)
    d.shape("light", cloud(140, 150, 0.7), shadow=False, line=False)
    d.band("far", waves(132, 5, 30))
    d.band("mid", "M-30 160 Q10 136 40 150 Q70 166 100 148 Q130 130 160 150 Q190 168 230 146")
    d.shape("light", "M22 145 Q34 136 46 144 Q38 142 30 148Z M120 140 Q132 132 144 140 Q136 138 128 144Z", shadow=False)
    d.band("near", waves(176, 5, 36))
    d.band("deep", waves(192, 4, 40), line=False)

    def bird():
        d.shape("hero", taper([(104, 88), (136, 76), (162, 66), (184, 58)], 1, 1, wf=lambda t: 10 * (1 - t) ** 0.8 + 1))
        d.shape("light", P([(62, 92), (74, 84), (98, 84), (124, 88), (138, 94, 1), (124, 98), (98, 102), (74, 100)]))
        d.shape("mark", P([(132, 92), (146, 92, 1), (140, 98), (128, 98)]), shadow=False)
        d.shape("hero", taper([(98, 94), (70, 104), (44, 114), (18, 126)], 1, 1, wf=lambda t: 11 * (1 - t) ** 0.8 + 1), spot=True)
        d.shape("hero2", taper([(86, 99), (64, 107), (44, 114)], 1, 1, wf=lambda t: 3.2 * (1 - t) + 0.5), shadow=False, line=False)
        d.shape("beak", P([(66, 86, 1), (54, 89), (50, 93, 1), (56, 93), (66, 92, 1)]))
        d.marks("mark", ellipse(70, 88, 3, 1.2))
    group(d, "translate(100 96) rotate(-6) translate(-100 -96)", bird)


# ================================================================ PELICAN
def pelican_portrait(d: Drawing):
    d.disc("glow", 96, 96, 62)
    d.band("far", waves(162, 4, 30))
    d.band("near", waves(182, 4, 36), line=False)
    d.shape("light", P([(146, 214, 1), (140, 170), (128, 130), (124, 96), (118, 78), (126, 54), (142, 50), (154, 64), (150, 88), (154, 120),
                        (168, 160), (178, 214, 1)]))
    d.shape("light", P(zig([(146, 54), (158, 50), (166, 62)], 3, 4) + [(156, 66)]), shadow=False)
    d.shape("mark", P([(166, 186), (178, 176), (194, 200), (196, 214, 1), (172, 214, 1)]))
    pouch = P([(122, 74), (90, 80), (56, 84), (38, 86, 1), (48, 100), (70, 114), (96, 120), (114, 112), (124, 94)])
    d.shape("pouch", pouch)
    clipped(d, pouch, lambda: [d.shape("pouch2", fish(76, 102, 1.8), shadow=False, line=False),
                               d.stroke("pouch2", "M50 90 Q80 104 116 98", 1.2, line=False)])
    d.shape("beak", P([(124, 64, 1), (90, 70), (54, 76), (34, 78), (26, 82, 1), (30, 88, 1), (36, 84), (56, 84), (92, 80), (124, 76, 1)]), spot=True)
    d.shape("pop", "M26 82 L30 88 L36 84 L32 79Z", shadow=False)
    d.shape("skin", ellipse(132, 66, 8, 6), shadow=False)
    d.marks("mark", circle(132, 66, 2.6))
    d.marks("light", circle(131, 65, 0.9))


def pelican_post(d: Drawing):
    # pelican resting on a post, bill tucked down on its chest
    d.limb("legs", "M98 120 L96 132 M110 120 L112 132", 3)
    d.shape("light", P([(76, 92), (92, 82), (124, 84), (146, 98), (162, 114, 1), (140, 116), (112, 124), (86, 120), (74, 108)]))
    d.shape("light", P([(88, 88), (106, 84), (134, 92), (156, 110, 1), (130, 108), (104, 104)]), shadow=False)
    d.shape("mark", P([(126, 100), (146, 104), (166, 116, 1), (142, 114)]), shadow=False)
    d.shape("light", taper([(84, 96), (76, 82), (74, 66), (80, 56)], 9, 7))
    d.shape("light", circle(82, 54, 11))
    d.shape("light", P(zig([(86, 44), (94, 42), (98, 50)], 2, 3) + [(92, 52)]), shadow=False, line=False)
    d.shape("pouch", P([(76, 56), (68, 100), (66, 108, 1), (78, 102), (86, 84), (86, 64)]))
    d.shape("beak", P([(73, 47, 1), (62, 104), (61, 111, 1), (66, 108), (79, 52, 1)]), spot=True)
    d.marks("pop", "M61 104 L61 111 L66 108Z")
    d.shape("skin", ellipse(84, 52, 4.5, 3.6), shadow=False)
    d.marks("mark", circle(84, 52, 1.6))


def pelican_pier(d: Drawing):
    d.disc("glow", 48, 60, 22)
    d.band("far", waves(116, 3, 30))
    d.shape("dark", "M150 112 L176 112 L172 118 L154 118Z M162 112 V96 L172 108 L162 108", shadow=False)
    d.band("mid", waves(134, 4, 34))
    d.band("near", waves(156, 4, 38))
    d.shape("wood", rrect(160, 112, 14, 80, 3))
    d.shape("wood2", ellipse(167, 112, 7, 2.5), shadow=False)
    d.stroke("dark", "M104 140 Q136 156 166 130", 1.8)
    d.shape("wood", rrect(88, 130, 30, 80, 4))
    d.shape("wood2", ellipse(103, 130, 15, 4), shadow=False)
    d.stroke("wood2", "M96 146 V186 M110 150 V190", 1.4, line=False)
    group(d, "translate(102 86) scale(1.18) translate(-104 -98)", lambda: pelican_post(d))
    d.stroke("light", "M30 170 q8 -4 16 0 M140 176 q8 -4 16 0", 2.2)
    d.band("deep", waves(184, 4, 40), line=False)


# ================================================================ SWAN
SWAN_HEAD = [(80, 56), (74, 50), (66, 50), (60, 56), (60, 64), (68, 68)]


def swan_head(d: Drawing):
    d.shape("light", P([(84, 60), (78, 50), (66, 48), (58, 54), (56, 62), (64, 68), (78, 70)]))
    d.shape("beak", P([(60, 54, 1), (52, 60), (44, 68), (42, 72, 1), (48, 72), (58, 66), (64, 64, 1)]))
    d.marks("mark", P([(42, 72), (44, 68), (47, 66), (48, 72)]))
    d.marks("mark", P([(66, 50), (60, 52), (58, 60), (63, 61), (66, 56)]))
    d.marks("mark", circle(67, 57, 1.9))


def swan_busk(d: Drawing):
    wing = ([(84, 126), (84, 100)] + zig([(92, 84), (112, 68), (136, 62), (160, 70), (176, 92), (180, 118)], 10, 4)[1:] +
            [(164, 124), (132, 120), (104, 126)])
    d.shape("light", P(wing))
    d.stroke("hero2", "M108 104 Q120 86 140 80 M114 114 Q130 96 156 90 M124 120 Q142 108 168 106", 1.6)
    d.shape("light", P([(56, 140), (70, 124), (100, 118), (140, 116), (168, 122), (178, 134), (162, 150), (110, 156), (70, 154)]))
    d.stroke("hero2", "M110 140 Q130 132 156 132", 1.6, line=False)
    d.shape("light", taper([(80, 132), (66, 112), (66, 92), (74, 76), (76, 64)], 10, 7))
    swan_head(d)


def swan_portrait(d: Drawing):
    d.disc("glow", 128, 90, 54)
    d.band("mid", "M-30 132 Q60 122 120 128 T230 124")
    d.band("near", waves(150, 3, 30))
    group(d, "translate(108 102) scale(1.06) translate(-110 -112)", lambda: swan_busk(d))
    d.raw('<g opacity=".35">', "")
    d.stroke("light", "M40 166 H80 M110 170 H160 M60 180 H120", 2.4, line=False)
    d.raw("</g>", "")
    d.band("deep", waves(178, 3, 36), line=False)


def swan_glide(d: Drawing):
    d.shape("light", P([(70, 130), (86, 116), (120, 110), (148, 108), (164, 100, 1), (160, 116), (150, 130), (120, 138), (84, 138)]))
    wing = [(92, 122)] + zig([(100, 112), (128, 108), (156, 106)], 6, 3)[1:] + [(150, 124), (120, 128)]
    d.shape("light", P(wing), shadow=False)
    d.stroke("hero2", "M104 124 Q124 118 146 118", 1.4, line=False)
    d.shape("light", taper([(84, 128), (74, 106), (74, 86), (80, 72), (76, 62)], 8, 6))
    group(d, "translate(76 58) scale(1.0) translate(-76 -60)", lambda: swan_head(d))


def cygnet(d: Drawing, x, y, s=1.0):
    def draw():
        d.shape("cyg", P([(-12, 0), (-8, -8), (6, -8), (12, -2), (8, 4), (-8, 4)]))
        d.shape("cyg", circle(-10, -12, 5))
        d.shape("mark", "M-14 -12 L-19 -10 L-14 -9Z", shadow=False)
        d.marks("mark", circle(-11, -13, 1))
    group(d, f"translate({x} {y}) scale({s})", draw)


def swan_cygnets(d: Drawing):
    d.disc("glow", 152, 56, 18)
    d.band("far", hills(104, 6))
    d.shape("mid", "M120 104 V82 h6 v-6 h4 v6 h8 v-14 l5 -8 l5 8 v14 h8 v-6 h4 v6 h6 V104Z", shadow=False, line=False)
    d.band("mid", "M-30 112 Q60 100 120 108 T230 104")
    d.band("lake", "M-30 116 L230 116")
    d.raw('<g opacity=".5">', "")
    d.stroke("light", "M30 132 H70 M120 128 H170 M40 170 H90 M130 176 H180", 2, line=False)
    d.raw("</g>", "")
    group(d, "translate(102 118) scale(1.08) translate(-110 -120)", lambda: swan_glide(d))
    cygnet(d, 152, 146, 1.0)
    cygnet(d, 178, 150, 0.85)
    d.stroke("lake2", "M50 150 q12 -4 24 0 M88 154 q12 -4 24 0 M138 152 q6 -2 12 0", 2)
    for x, h in [(12, 74), (20, 92), (28, 66), (180, 70), (190, 88)]:
        d.stroke("near", f"M{x} 200 Q{x + 2} {200 - h / 2} {x - 2} {200 - h}", 2.4, line=False)
        d.shape("deep", ellipse(x - 2, 200 - h + 8, 2.6, 7), shadow=False, line=False)
    d.band("lake2", waves(190, 3, 40), line=False)


# ================================================================ HERON
def heron_portrait(d: Drawing):
    d.disc("glow", 100, 96, 66)
    for x, h in [(14, 70), (24, 90), (34, 60), (168, 80), (180, 100), (190, 66)]:
        d.stroke("near", f"M{x} 214 Q{x + 3} {200 - h / 2} {x - 4} {200 - h}", 3, line=False)
    d.shape("hero", P([(110, 214, 1), (118, 170), (140, 150), (172, 160), (190, 214, 1)]))
    d.shape("mark", P([(138, 154), (160, 152), (176, 166), (150, 166)]), shadow=False)
    d.shape("light", taper([(116, 66), (120, 96), (112, 128), (118, 170), (128, 214)], 1, 1, wf=lambda t: 11 + 12 * t))
    d.stroke("mark", "M112 104 l-2 6 M108 118 l-2 6 M108 132 l-2 6 M110 146 l-1 6 M114 160 l-1 6", 2.2)
    d.shape("mark", taper([(126, 58), (150, 64), (176, 74)], 3, 0.6), shadow=False)
    d.shape("mark", taper([(126, 62), (148, 72), (170, 84)], 2.6, 0.5), shadow=False)
    d.shape("light", P([(126, 50), (110, 44), (92, 48), (82, 56), (86, 66), (100, 72), (118, 72), (128, 62)]))
    d.shape("hero2", P([(98, 46), (114, 44), (126, 50), (114, 50)]), shadow=False, line=False)
    d.shape("mark", P([(92, 52), (108, 48), (124, 52), (134, 58, 1), (120, 60), (104, 58)]), shadow=False)
    d.shape("beak", P([(86, 52, 1), (60, 57), (24, 64, 1), (60, 66), (86, 68, 1)]), spot=True)
    d.stroke("beak2", "M84 61 L36 64", 1.2)
    d.shape("eye", circle(92, 56, 3), shadow=False)
    d.marks("mark", circle(92, 56, 1.5))


def heron_stand(d: Drawing):
    d.limb("legs", "M116 112 L114 152", 2.8)
    d.limb("legs", "M124 112 L128 152", 2.8)
    d.shape("hero", P([(96, 92), (110, 84), (134, 86), (150, 100), (168, 126, 1), (150, 120), (126, 116), (104, 110)]))
    d.shape("mark", P([(132, 96), (150, 104), (166, 124, 1), (146, 114)]), shadow=False)
    d.shape("light", taper([(104, 96), (90, 86), (88, 70), (96, 58), (92, 48)], 8, 5))
    d.stroke("mark", "M94 74 l-2 4 M92 84 l-2 4", 1.6)
    d.shape("light", P([(98, 44), (90, 38), (80, 40), (76, 46), (82, 52), (94, 52)]))
    d.shape("mark", P([(82, 42), (92, 39), (100, 44), (112, 52, 1), (98, 48)]), shadow=False)
    d.shape("beak", P([(78, 42, 1), (66, 45), (50, 48, 1), (66, 49), (78, 50, 1)]))
    d.marks("mark", circle(82, 44, 1.3))


def heron_reeds(d: Drawing):
    d.disc("glow", 52, 64, 24)
    d.band("far", hills(128, 5))
    d.band("water", "M-30 146 L230 146")
    group(d, "translate(104 160) scale(1.06) translate(-120 -152)", lambda: heron_stand(d))
    d.raw('<g opacity=".45">', "")
    d.stroke("light", "M74 156 H116 M86 164 H128 M40 176 H80 M136 172 H170", 2, line=False)
    d.raw("</g>", "")
    for x, h, r in [(10, 96, "near"), (22, 120, "deep"), (34, 84, "near"), (160, 92, "near"), (172, 124, "deep"), (186, 104, "near")]:
        d.stroke(r, f"M{x} 214 Q{x + 3} {200 - h / 2} {x - 4} {200 - h}", 2.6)
        d.shape("reed", ellipse(x - 3.2, 200 - h + 10, 3, 9), shadow=False)
    d.shape("near", leaf(150, 200, 40, 6, -110), shadow=False, line=False)
    d.shape("near", leaf(40, 200, 44, 6, -70), shadow=False, line=False)
    d.band("water2", waves(192, 3, 40), line=False)


# ================================================================ PEREGRINE
def peregrine_portrait(d: Drawing):
    d.disc("glow", 128, 88, 52)
    d.band("far", "M-30 150 L20 130 L30 140 L60 112 L74 124 L100 104 L120 130 L230 150")
    d.band("mid", hills(180, 5))
    d.shape("light", P([(84, 74), (90, 50), (110, 36), (140, 38), (160, 60), (170, 110), (180, 150), (190, 214, 1), (50, 214, 1),
                        (66, 160), (80, 124), (84, 100)]))
    bars = "".join(f"M{x - 4} {y} q4 3 8 0" for y in range(140, 214, 10) for x in range(72 + (y % 20) // 2, 176, 12))
    d.stroke("mark", bars, 1.6, line=False)
    d.shape("hero", P([(160, 100), (178, 130), (194, 214, 1), (152, 214, 1), (162, 160)]))
    hood = [(84, 72), (90, 46), (110, 34), (136, 36), (156, 52), (164, 84), (168, 112), (156, 110), (146, 98), (132, 94), (120, 98),
            (114, 106), (110, 128, 1), (99, 126), (97, 106), (92, 92), (86, 84)]
    d.shape("hero", P(hood), spot=True)
    bill = P([(88, 64, 1), (78, 66), (70, 72), (66, 82), (68, 92, 1), (72, 86), (80, 84), (90, 84, 1)])
    d.shape("beak", bill)
    clipped(d, bill, lambda: d.shape("mark", "M50 70 H74 V100 H50Z", shadow=False, line=False))
    d.shape("pop", P([(90, 62), (84, 64), (82, 74), (90, 78)]), shadow=False)
    d.shape("pop", circle(106, 68, 9.5), shadow=False)
    d.marks("mark", circle(106, 68, 7))
    d.marks("light", circle(103.5, 65.5, 2))


def falcon_stoop(d: Drawing):
    spine_ = [(152, 48), (126, 76), (98, 104), (74, 126), (66, 134)]
    body = taper(spine_, 1, 1, wf=lambda t: 3 + 13 * math.sin(math.pi * min(t, 0.85) / 1.25))
    d.shape("hero", body)
    belly = taper([(140, 66), (116, 92), (92, 114), (74, 130)], 1, 1, wf=lambda t: 3 + 6 * math.sin(math.pi * t * 0.8))
    group(d, "translate(5 5)", lambda: d.shape("light", belly, shadow=False))
    group(d, "translate(5 5)", lambda: clipped(d, belly, lambda: d.stroke("mark", "".join(
        f"M{x} {y} l5 3" for x, y in [(96, 108), (104, 100), (112, 92), (120, 84), (128, 76), (100, 112), (110, 104), (118, 96), (88, 116)]), 1.4, line=False)))
    wing = taper([(84, 114), (110, 90), (136, 64), (164, 36)], 1, 1, wf=lambda t: 9 * (1 - t) ** 0.7 + 1)
    group(d, "translate(-4 -3)", lambda: d.shape("hero2", wing, spot=True))
    d.stroke("hero", "M118 82 L150 50 M126 78 L158 46", 1.2, line=False)
    d.shape("hero", circle(64, 134, 11))
    d.shape("light", P([(64, 138), (72, 134), (76, 142), (68, 146)]), shadow=False)
    d.shape("beak", P([(56, 140, 1), (52, 146), (50, 152, 1), (56, 148), (60, 144)]))
    d.shape("pop", circle(60, 132, 3.6), shadow=False)
    d.marks("mark", circle(60, 132, 2.4))
    d.limb("pop", "M88 122 L84 128", 3, shadow=False)


def peregrine_stoop(d: Drawing):
    d.disc("glow", 46, 50, 18)
    d.shape("light", cloud(120, 30, 1.0), shadow=False)
    d.band("far", waves(150, 3, 30))
    d.shape("near", "M150 230 L150 140 L160 120 L176 112 L192 100 L230 96 L230 230Z")
    d.shape("deep", "M170 230 L172 160 L184 140 L230 130 L230 230Z", shadow=False, line=False)
    d.band("mid", waves(168, 4, 34))
    for x0, y0, ln in [(160, 66, 30), (150, 92, 22), (170, 46, 20), (136, 108, 16)]:
        d.stroke("light", f"M{x0} {y0} l{ln * 0.72:.1f} {-ln * 0.69:.1f}", 2.2)
    group(d, "translate(96 92) scale(1.12) translate(-104 -92)", lambda: falcon_stoop(d))
    d.band("deep", waves(186, 4, 38), line=False)


# ================================================================ KINGFISHER
def kingfisher_bust(d: Drawing):
    """Kingfisher head and breast, facing left, a fish across its bill."""
    d.shape("hero2", P([(56, 214, 1), (60, 160), (76, 124), (126, 120), (150, 150), (156, 214, 1)]))
    d.shape("hero", P([(136, 120), (158, 140), (172, 180), (176, 214, 1), (140, 214, 1), (146, 160)]))
    d.shape("pop", taper([(150, 132), (160, 170), (164, 214)], 3, 4), shadow=False)
    d.shape("hero", circle(104, 86, 38))
    d.marks("pop", "".join(circle(x, y, 1.6) for x, y in [(96, 58), (108, 56), (120, 62), (102, 66), (114, 68), (128, 72), (90, 66)]))
    d.shape("hero2", P([(88, 82), (108, 76), (128, 80), (134, 90), (120, 96), (98, 96), (88, 92)]), shadow=False)
    d.shape("light", ellipse(136, 100, 9, 7), shadow=False)
    d.shape("hero", P([(76, 100), (110, 102), (132, 110), (112, 110), (80, 106)]), shadow=False, line=False)
    d.shape("light", P([(70, 100), (84, 106), (86, 118), (72, 114)]), shadow=False)
    d.marks("mark", circle(92, 82, 4.6))
    d.marks("light", circle(90.6, 80.6, 1.4))
    group(d, "rotate(-10 40 92)", lambda: [d.shape("fishc", fish(40, 92, 3.0, right=False), extra='transform="rotate(90 40 92)"'),
                                           d.marks("mark", circle(40, 78, 1.6)),
                                           d.stroke("fishd", "M36 84 V100", 1.4, line=False)])
    d.shape("mark", P([(76, 78, 1), (48, 86), (16, 94, 1), (48, 92), (76, 90, 1)]))
    d.shape("mark", P([(76, 92, 1), (48, 95), (20, 98, 1), (48, 100), (76, 98, 1)]))


def kingfisher_catch(d: Drawing):
    d.disc("glow", 86, 92, 64)
    for x, h in [(10, 80), (20, 104), (30, 70), (176, 90), (186, 74), (194, 100)]:
        d.stroke("near", f"M{x} 214 Q{x + 3} {200 - h / 2} {x - 4} {200 - h}", 3, line=False)
    flip(d, lambda: group(d, "translate(100 100) scale(.96) translate(-100 -100)", lambda: kingfisher_bust(d)))


def kingfisher_diving(d: Drawing):
    d.shape("hero", taper([(104, 88), (82, 70), (66, 50), (60, 36)], 1, 1, wf=lambda t: 8 * (1 - t) ** 0.6 + 1))
    d.shape("hero", taper([(116, 40), (110, 70), (102, 100), (98, 116)], 1, 1, wf=lambda t: 4 + 9 * math.sin(math.pi * min(t, 0.8) / 1.1)))
    d.shape("hero2", taper([(112, 66), (108, 92), (103, 112)], 1, 1, wf=lambda t: 2 + 5 * math.sin(math.pi * t)), shadow=False)
    d.shape("pop", taper([(110, 46), (104, 76), (98, 100)], 1.5, 1.5), shadow=False)
    d.shape("hero", taper([(100, 92), (118, 70), (132, 50), (140, 34)], 1, 1, wf=lambda t: 9 * (1 - t) ** 0.6 + 1), spot=True)
    d.stroke("mark", "M122 66 L132 52 M126 70 L136 56", 1.2, line=False)
    d.shape("hero", circle(98, 116, 13))
    d.shape("hero2", P([(98, 112), (110, 108), (112, 120), (102, 124)]), shadow=False)
    d.shape("light", P([(104, 124), (110, 122), (108, 130)]), shadow=False, line=False)
    d.marks("mark", circle(102, 116, 2.4))
    d.shape("mark", P([(92, 124, 1), (96, 146), (98, 158, 1), (100, 146), (104, 126, 1)]))


def kingfisher_dive(d: Drawing):
    d.disc("glow", 152, 58, 20)
    d.limb("dark", "M-10 70 C30 64 60 62 84 52", 5)
    d.shape("near", leaf(30, 66, 22, 6, -60), shadow=False, line=False)
    d.band("far", hills(132, 5))
    d.band("water", "M-30 150 L230 150")
    group(d, "translate(98 90) scale(1.08) translate(-100 -100)", lambda: kingfisher_diving(d))
    d.band("water2", "M-30 158 Q100 152 230 158", shadow=False, line=False)
    for dx, dy, r in [(-16, -10, 3), (-8, -18, 2.6), (8, -16, 2.8), (16, -8, 2.6), (0, -22, 2)]:
        d.shape("light", f"M{97 + dx} {150 + dy - r * 1.7} Q{97 + dx + r} {150 + dy} {97 + dx} {150 + dy + r} Q{97 + dx - r} {150 + dy} {97 + dx} {150 + dy - r * 1.7}Z", shadow=False)
    d.stroke("light", "M70 152 Q84 144 92 150 M102 150 Q110 144 124 152", 2.6)
    d.raw('<g opacity=".55">', "")
    d.stroke("light", "M60 166 Q97 158 134 166 M40 180 Q97 170 154 180", 2, line=False)
    d.raw("</g>", "")
    for x, h in [(14, 70), (24, 90), (176, 80), (188, 64)]:
        d.stroke("near", f"M{x} 214 Q{x + 3} {200 - h / 2} {x - 4} {200 - h}", 3)
    d.band("water3", waves(194, 3, 40), line=False)


# ================================================================ FLAMINGO
def flamingo_portrait(d: Drawing):
    d.disc("glow", 100, 92, 60)
    d.band("far", "M-30 140 L30 112 L60 128 L96 100 L130 126 L160 114 L230 136")
    d.band("lagoon", "M-30 150 L230 150")
    d.shape("hero", P(zig([(118, 214), (124, 172), (150, 150), (182, 160)], 6, 6) + [(196, 214, 1)]))
    d.shape("hero2", P([(140, 214, 1), (146, 182), (166, 168), (186, 176), (194, 214, 1)]), shadow=False)
    d.shape("mark", P([(170, 196), (190, 186), (196, 214, 1), (176, 214, 1)]), shadow=False)
    d.shape("hero", taper([(132, 190), (130, 150), (110, 120), (100, 92), (104, 66), (114, 52)], 1, 1, wf=lambda t: 9 + 3 * (1 - t)))
    d.shape("hero", ellipse(112, 50, 14, 11))
    bill = P([(100, 42, 1), (84, 44), (72, 48), (62, 58), (58, 72), (60, 86, 1), (66, 80), (70, 68), (78, 60), (90, 60), (102, 60, 1)])
    d.shape("beak", bill)
    clipped(d, bill, lambda: d.shape("mark", "M40 64 L76 60 L80 100 L40 100Z", shadow=False, line=False))
    d.marks("mark", "M74 54 L96 50 L96 52 L76 56Z")
    d.shape("eye", circle(110, 46, 3.2), shadow=False)
    d.marks("mark", circle(110, 46, 1.6))


def flamingo_oneleg(d: Drawing):
    d.limb("legs", "M102 98 L104 124 L103 150", 3)
    d.marks("legs", ellipse(104, 124, 3, 3.5))
    d.limb("legs", "M108 96 L124 112 L110 104", 3)
    d.shape("hero", P([(76, 86), (86, 74), (110, 70), (130, 74), (142, 82, 1), (128, 90), (110, 98), (88, 98)]))
    d.shape("hero2", P([(96, 78), (118, 74), (138, 80, 1), (120, 86), (100, 88)]), shadow=False, spot=True)
    d.shape("mark", P([(126, 80), (142, 82, 1), (128, 88)]), shadow=False)
    d.shape("hero", taper([(84, 84), (72, 74), (74, 56), (86, 44), (82, 32), (74, 28)], 4.2, 3.4))
    d.shape("hero", ellipse(74, 28, 7, 5.5))
    bill = P([(70, 24, 1), (62, 26), (58, 32), (58, 40, 1), (62, 36), (64, 32), (70, 32, 1)])
    d.shape("beak", bill)
    clipped(d, bill, lambda: d.shape("mark", "M50 32 H62 V44 H50Z", shadow=False, line=False))
    d.marks("mark", circle(74, 26, 1.2))


def flamingo_lagoon(d: Drawing):
    d.disc("glow", 150, 52, 18)
    peaks(d, "M-30 124 L10 110 L44 80 L60 80 L96 112 L130 100 L164 72 L196 104 L230 112",
          ["M44 80 L60 80 L68 89 L60 87 L54 92 L48 87 L39 88Z", "M164 72 L172 80 L166 79 L162 83 L157 78Z"])
    d.band("lagoon", "M-30 132 L230 132")
    for x in (20, 34, 48, 160, 176):
        d.shape("hero", f"M{x} 130 q4 -6 8 0 l-3 0 l-1 -8 l-1 0 Z M{x + 3.5} 122 l0 -4 l-2 0Z", shadow=False, line=False)
    d.raw('<g opacity=".35" transform="translate(0 300) scale(1 -1)">', "")
    group(d, "translate(98 150) scale(.98) translate(-100 -150)", lambda: flamingo_oneleg(d))
    d.raw("</g>", "")
    d.raw("", "")
    group(d, "translate(98 150) scale(.98) translate(-100 -150)", lambda: flamingo_oneleg(d))
    d.stroke("light", "M74 152 q10 -4 20 0 M110 152 q10 -4 20 0 M30 170 q8 -3 16 0 M150 176 q8 -3 16 0", 2)
    d.band("lagoon2", waves(190, 3, 40), line=False)


# ================================================================ PARROT
def parrot_portrait(d: Drawing):
    for x, y, a, r in [(-6, 40, 20, "mid"), (-4, 96, 0, "near"), (2, 150, -20, "mid"), (206, 36, 160, "near"), (204, 96, 180, "mid"),
                       (198, 150, -160, "near")]:
        d.shape(r, leaf(x, y, 64, 15, a), line=False)
    d.shape("hero", P([(98, 36), (126, 34), (150, 50), (160, 78), (156, 108), (150, 132), (160, 214, 1), (54, 214, 1), (66, 150),
                       (80, 120), (82, 96), (84, 64)]), spot=True)
    d.shape("hero2", P([(118, 164), (150, 146), (176, 160), (190, 214, 1), (128, 214, 1)]))
    d.shape("pop2", P([(140, 186), (170, 170), (190, 186), (196, 214, 1), (150, 214, 1)]))
    d.stroke("hero", "M132 168 l6 6 M146 160 l6 6 M160 158 l5 6", 1.6, line=False)
    d.shape("light", P([(86, 58), (102, 52), (120, 58), (126, 74), (116, 88), (98, 92), (86, 86)]), shadow=False)
    d.stroke("hero", "M92 66 h6 M102 64 h6 M112 66 h6 M94 74 h6 M104 74 h6 M114 76 h6 M98 82 h6 M108 84 h6", 1.4, line=False)
    upper = P([(86, 56, 1), (72, 56), (58, 64), (50, 78), (50, 96), (56, 108, 1), (58, 96), (64, 88), (74, 84), (88, 86, 1)])
    d.shape("beak", upper)
    d.shape("mark", P([(88, 86, 1), (74, 88), (64, 96), (66, 106), (78, 110), (90, 100)]))
    d.shape("beak", upper, shadow=False, line=False)
    d.stroke("mark", "M84 60 Q76 70 78 84", 1.6)
    d.shape("eye", circle(106, 70, 6), shadow=False)
    d.marks("mark", circle(106, 70, 3.2))
    d.marks("light", circle(104.8, 68.8, 1.1))


def macaw_flying(d: Drawing):
    d.shape("pop2", taper([(112, 102), (124, 120), (136, 136)], 7, 2))
    d.shape("hero", taper([(126, 96), (150, 112), (172, 130), (192, 150)], 6, 1.5), spot=True)
    d.shape("pop2", taper([(132, 98), (156, 116), (178, 136), (196, 156)], 2.5, 1.2), shadow=False, line=False)
    d.shape("hero", P([(58, 88), (70, 78), (96, 78), (120, 86), (134, 96), (120, 102), (92, 102), (70, 98)]), spot=True)
    wing = [(86, 82), (94, 58), (110, 38)] + fingers(128, 34, 8, 24, 210, 330, 5)[1:-1] + [(140, 46), (122, 66), (110, 86)]
    d.shape("pop2", P(wing))
    d.shape("hero2", P([(86, 82), (94, 62), (106, 46), (118, 50), (114, 70), (106, 86)]), shadow=False)
    d.shape("hero", P([(86, 82), (92, 70), (100, 64), (106, 72), (104, 86)]), shadow=False, line=False)
    d.shape("light", P([(60, 82), (68, 78), (74, 84), (68, 90), (60, 90)]), shadow=False)
    d.shape("beak", P([(60, 80, 1), (52, 80), (46, 86), (46, 96, 1), (50, 90), (56, 90), (62, 92, 1)]))
    d.shape("mark", P([(62, 92, 1), (54, 92), (52, 98), (60, 98)]), shadow=False)
    d.marks("mark", circle(67, 84, 1.8))


def parrot_flight(d: Drawing):
    d.disc("glow", 152, 52, 18)
    d.band("far", hills(130, 6))
    for x in range(-10, 220, 24):
        d.shape("mid", scallop(x, 138 - (x * 7 % 10), 16, 8, 0.16), shadow=False, line=False)
    d.band("mid", hills(150, 4))
    d.band("river", "M-30 170 Q60 156 120 166 T230 160")
    for x in range(-6, 220, 30):
        d.shape("near", scallop(x, 192 - (x * 3 % 8), 16, 8, 0.16), shadow=False, line=False)
    d.band("near", hills(190, 3), line=False)
    group(d, "translate(100 108) scale(1.12) translate(-110 -90)", lambda: macaw_flying(d))


# ================================================================ colours
DEER = {"hero": "#A4532C", "hero2": "#C98A5A", "mark": "#2A1A12", "light": "#F6EBDD", "mane": "#6E3A20", "horn": "#D8C29A"}
COO = {"hero": "#C2652F", "hero2": "#DE8A4A", "mark": "#2A1812", "horn": "#F0E4C6", "horn2": "#8A6A4A", "horntip": "#4A3A30", "nose": "#5A3A32",
       "heather": "#A260A8"}
HOG = {"hero": "#6B4A33", "hero2": "#CFA77C", "mark": "#1E1612", "light": "#EBDCC4", "leaf1": "#D9772B", "leaf2": "#B5432C",
       "leaf3": "#E8B23C", "pop": "#D23B2C"}
FOX = {"hero": "#DE6A2A", "hero2": "#B9541F", "light": "#FFF8EE", "mark": "#1F1A17", "eye": "#F2B33D"}
BEAR = {"hero": "#7A4E2E", "hero2": "#A97A4E", "mark": "#22160E", "light": "#FFFFFF"}
LYNX = {"hero": "#C69A64", "hero2": "#EAD8B6", "light": "#FBF3E4", "mark": "#2A2018", "eye": "#C9C44E", "pop": "#C98580", "legs2": "#A57E50"}
IBEX = {"hero": "#9C8468", "hero2": "#5E4B3A", "mark": "#231C15", "light": "#EFE6D8", "horn": "#6A5644", "horn2": "#4A3B2E",
        "eye": "#D9A84A"}
SQUIRREL = {"hero": "#C8551E", "hero2": "#E07A3A", "light": "#FFF3E2", "mark": "#1F1712", "nut": "#7A4A24", "nut2": "#4A2A14",
            "trunk": "#7A4630"}

EAGLE = {"hero": "#6B4426", "hero2": "#D9A040", "mark": "#3A2414", "pop": "#F2C14E", "dark": "#1E1612", "beak": "#2E2A2A",
         "beak2": "#7D7F8A", "eye": "#B9741F", "light": "#FFFFFF"}
OWL = {"hero": "#D9A35E", "hero2": "#8F8A86", "light": "#FFFDF7", "rim": "#B9773E", "ridge": "#EBD8BC", "mark": "#16110E",
       "beak": "#E8C3A6", "beak2": "#9A8E86"}
ALBA = {"hero": "#3B414D", "hero2": "#C9D0D8", "light": "#FFFFFF", "mark": "#1C2027", "beak": "#F2A93B", "beak2": "#C47A20", "pop": "#E8697A"}
PELICAN = {"light": "#FFFFFF", "mark": "#22252B", "pouch": "#F4A44E", "pouch2": "#D9822E", "beak": "#F08A6E", "pop": "#D9433B",
           "skin": "#F7C9A9", "legs": "#E79A7E", "wood": "#8A6440", "wood2": "#5E4228"}
SWAN = {"light": "#FFFFFF", "hero2": "#A8ADB6", "mark": "#1C1C1E", "beak": "#F08A2E", "lake": "#7FB9D6", "lake2": "#5C9CC0", "cyg": "#8E8780"}
HERON = {"hero": "#8E99A6", "hero2": "#DDE2E8", "light": "#FFFFFF", "mark": "#1E2228", "beak": "#F2B23A", "beak2": "#B9801F",
         "eye": "#F6D24A", "legs": "#C9A060", "reed": "#7A4E2C", "water": "#8EC5DE", "water2": "#6AAACB"}
FALCON = {"hero": "#3E4A5C", "hero2": "#56647A", "light": "#FBF5EA", "mark": "#151A22", "beak": "#6C7C96", "pop": "#F6C33E"}
KINGF = {"hero": "#1F8FCB", "hero2": "#F08A3C", "mark": "#151B24", "light": "#FFFFFF", "pop": "#6FE0F0", "fishc": "#A9C0CC",
         "fishd": "#7E95A3", "water": "#7FC1DD", "water2": "#A7D8EC", "water3": "#5CA4C8"}
FLAMINGO = {"hero": "#EE7591", "hero2": "#E04F72", "mark": "#1E1A1C", "beak": "#F7D7DC", "eye": "#F6D24A", "legs": "#E77F95",
            "lagoon": "#F6C2CB", "lagoon2": "#EFA8B6", "light": "#FFFFFF"}
MACAW = {"hero": "#D9262E", "hero2": "#F6C33E", "pop2": "#2D6FD0", "light": "#FFFFFF", "mark": "#1A1A1E", "beak": "#F1E6D2",
         "eye": "#F6E7A6", "river": "#6FB7D6"}

CONCEPTS = [
    Concept("reddeer-portrait", "animal-red-deer", "Red deer stag", reddeer_portrait, overrides=DEER,
            checks=[("hero", "glow"), ("horn", "glow"), ("horn", "sky"), ("mane", "far")],
            fixes={"glow": ["glow2", "light", "far", "sky2"], "horn": ["#9C7E56", "#EFE3C8"], "far": ["mid", "near", "ground"]}),
    Concept("reddeer-roar", "animal-red-deer", "Highland roar", reddeer_roar, overrides=DEER,
            checks=[("hero", "sky"), ("mane", "sky"), ("horn", "sky"), ("hero", "near"), ("hero", "mid"), ("horn", "far")],
            fixes={"near": ["deep", "far", "ground"], "mid": ["far", "near"], "horn": ["#9C7E56", "#EFE3C8"], "sky": ["sky2"]}),
    Concept("highlandcow-portrait", "animal-highland-cow", "Highland coo", highlandcow_portrait, overrides=COO,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "mid"), ("horn2", "sky"), ("hero", "glow")],
            fixes={"far": ["mid", "near", "deep"], "mid": ["near", "deep"], "glow": ["glow2", "light"], "horn": ["#D2BC8E", "#BFA273"]}),
    Concept("highlandcow-glen", "animal-highland-cow", "Coo in the glen", highlandcow_glen, overrides=COO,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "far"), ("horn2", "sky"), ("heather", "ground")],
            fixes={"near": ["deep", "mid"], "mid": ["far", "near"], "far": ["mid", "sky2"], "horn": ["#D2BC8E", "#BFA273"]}),
    Concept("hedgehog-portrait", "animal-hedgehog", "Hedgehog", hedgehog_portrait, overrides=HOG,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero2", "glow"), ("hero2", "sky")],
            fixes={"glow": ["glow2", "light", "far"], "sky": ["sky2"]}),
    Concept("hedgehog-autumn", "animal-hedgehog", "Autumn hedgehog", hedgehog_autumn, overrides=HOG,
            checks=[("hero", "ground"), ("hero2", "ground"), ("hero", "far"), ("dark", "sky")],
            fixes={"ground": ["mid", "far", "near"], "far": ["mid", "near"], "dark": ["#5A4636"]}),
    Concept("redfox-portrait", "animal-red-fox", "Red fox", redfox_portrait, overrides=FOX,
            checks=[("hero", "glow"), ("hero", "sky"), ("light", "glow")],
            fixes={"glow": ["glow2", "far", "mid", "near"], "sky": ["sky2"]}),
    Concept("redfox-snow", "animal-red-fox", "Fox in the snow", redfox_snow, overrides=FOX,
            checks=[("hero", "light"), ("hero", "sky"), ("hero", "near"), ("light", "sky")],
            fixes={"sky": ["sky2", "far"], "near": ["mid", "deep"]}),
    Concept("brownbear-portrait", "animal-brown-bear", "Brown bear", brownbear_portrait, overrides=BEAR,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero", "near")],
            fixes={"glow": ["glow2", "light", "far"], "near": ["mid", "far"]}),
    Concept("brownbear-forest", "animal-brown-bear", "Bear in the forest", brownbear_forest, overrides=BEAR,
            checks=[("hero", "near"), ("hero", "mid"), ("hero", "ground"), ("hero", "sky")],
            fixes={"near": ["deep", "far"], "mid": ["far", "ground"], "ground": ["mid", "far"]}),
    Concept("lynx-portrait", "animal-lynx", "Lynx", lynx_portrait, overrides=LYNX,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero2", "glow")],
            fixes={"glow": ["near", "mid", "deep"], "sky": ["sky2", "far"]}),
    Concept("lynx-snow", "animal-lynx", "Lynx in the snow", lynx_snow, overrides=LYNX,
            checks=[("hero", "light"), ("hero", "mid"), ("hero", "near"), ("light", "sky")],
            fixes={"mid": ["near", "deep"], "near": ["deep", "dark"], "sky": ["sky2", "far"]}),
    Concept("ibex-portrait", "animal-ibex", "Alpine ibex", ibex_portrait, overrides=IBEX,
            checks=[("hero", "sky"), ("hero", "far"), ("horn", "sky"), ("horn", "far"), ("hero", "mid")],
            fixes={"far": ["sky2", "mid", "near"], "mid": ["near", "far"]}),
    Concept("ibex-ledge", "animal-ibex", "Ibex on the ledge", ibex_ledge, overrides=IBEX,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "mid"), ("hero", "near"), ("horn", "far")],
            fixes={"near": ["deep", "dark"], "mid": ["far", "near"], "far": ["sky2", "mid"]}),
    Concept("redsquirrel-portrait", "animal-red-squirrel", "Red squirrel", redsquirrel_portrait, overrides=SQUIRREL,
            checks=[("hero", "glow"), ("hero", "sky"), ("nut", "hero")],
            fixes={"glow": ["glow2", "light", "far"], "sky": ["sky2"]}),
    Concept("redsquirrel-pine", "animal-red-squirrel", "Squirrel in the pines", redsquirrel_pine, overrides=SQUIRREL,
            checks=[("hero", "sky"), ("hero", "trunk"), ("hero", "far"), ("trunk", "sky")],
            fixes={"sky": ["sky2"], "far": ["mid", "near"]}),
    # birds
    Concept("goldeneagle-highlands", "animal-golden-eagle", "Over the Highlands", goldeneagle_highlands, overrides=EAGLE,
            checks=[("hero", "sky"), ("mark", "sky"), ("hero", "far"), ("mark", "far"), ("hero2", "sky"), ("pop", "mid"), ("hero", "mid")],
            fixes={"far": ["sky2", "mid"], "mid": ["near", "far", "ground"], "sky": ["sky2"]}),
    Concept("goldeneagle-portrait", "animal-golden-eagle", "Golden eagle", goldeneagle_portrait, overrides=EAGLE,
            checks=[("hero2", "glow"), ("hero2", "sky"), ("hero", "far"), ("beak2", "glow"), ("hero", "sky")],
            fixes={"glow": ["light", "sky2", "far", "mid"], "sky": ["sky2", "far"], "far": ["mid", "near"]}),
    Concept("barnowl-portrait", "animal-barn-owl", "Barn owl", barnowl_portrait, overrides=OWL,
            checks=[("hero", "glow"), ("rim", "glow"), ("hero", "sky")],
            fixes={"glow": ["glow2", "far", "light", "mid", "near"], "sky": ["sky2", "far"]}),
    Concept("barnowl-dusk", "animal-barn-owl", "Owl at dusk", barnowl_dusk, overrides=OWL,
            checks=[("hero", "sky"), ("light", "sky"), ("hero", "far")],
            fixes={"sky": ["sky2", "far", "mid"], "far": ["mid", "near"]}),
    Concept("albatross-portrait", "animal-albatross", "Albatross", albatross_portrait, ["coastal", "meadow", "blush", "dusk"], ALBA,
            checks=[("light", "glow"), ("light", "sky"), ("beak", "glow"), ("light", "far")],
            fixes={"glow": ["far", "mid", "near"], "sky": ["sky2", "far", "mid"], "far": ["mid", "near"]}),
    Concept("albatross-glide", "animal-albatross", "Southern Ocean glide", albatross_glide, ["coastal", "meadow", "blush", "dusk"], ALBA,
            checks=[("hero", "sky"), ("hero", "mid"), ("hero", "far"), ("light", "sky")],
            fixes={"sky": ["sky2", "far"], "far": ["mid", "near"], "mid": ["near", "far"]}),
    Concept("pelican-portrait", "animal-pelican", "Pelican", pelican_portrait, overrides=PELICAN,
            checks=[("light", "glow"), ("pouch", "glow"), ("beak", "glow"), ("light", "sky")],
            fixes={"glow": ["far", "mid", "near", "deep"], "sky": ["sky2", "far", "mid"]}),
    Concept("pelican-pier", "animal-pelican", "Pelican on the pier", pelican_pier, ["coastal", "meadow", "blush", "dusk"], PELICAN,
            checks=[("light", "sky"), ("light", "far"), ("wood", "mid"), ("light", "mid")],
            fixes={"sky": ["sky2", "far", "mid"], "far": ["mid", "near"], "mid": ["near", "deep"]}),
    Concept("swan-portrait", "animal-swan", "Mute swan", swan_portrait, ["coastal", "meadow", "blush", "dusk"], SWAN,
            checks=[("light", "glow"), ("light", "sky"), ("light", "mid"), ("light", "near")],
            fixes={"glow": ["far", "mid", "near"], "sky": ["sky2", "far"], "mid": ["near", "deep"], "near": ["deep", "mid"]}),
    Concept("swan-cygnets", "animal-swan", "Swan & cygnets", swan_cygnets, ["coastal", "meadow", "blush", "dusk"], SWAN,
            checks=[("light", "lake"), ("cyg", "lake"), ("mid", "far")],
            fixes={"mid": ["near", "deep"]}),
    Concept("heron-portrait", "animal-heron", "Grey heron", heron_portrait, overrides=HERON,
            checks=[("light", "glow"), ("hero", "glow"), ("beak", "glow"), ("light", "sky"), ("hero", "sky")],
            fixes={"glow": ["mid", "near", "far", "deep"], "sky": ["sky2", "far"]}),
    Concept("heron-reeds", "animal-heron", "Heron in the reeds", heron_reeds, ["coastal", "meadow", "blush", "dusk"], HERON,
            checks=[("hero", "sky"), ("light", "sky"), ("hero", "far"), ("light", "far"), ("legs", "water")],
            fixes={"sky": ["sky2", "far"], "far": ["mid", "near"]}),
    Concept("peregrine-portrait", "animal-peregrine-falcon", "Peregrine falcon", peregrine_portrait, overrides=FALCON,
            checks=[("light", "glow"), ("hero", "glow"), ("light", "sky"), ("hero", "far")],
            fixes={"glow": ["mid", "far", "near"], "sky": ["sky2", "far"], "far": ["mid", "near", "#8C97B8"]}),
    Concept("peregrine-stoop", "animal-peregrine-falcon", "The stoop", peregrine_stoop, ["coastal", "meadow", "blush", "dusk"], FALCON,
            checks=[("hero", "sky"), ("hero2", "sky"), ("hero", "near")],
            fixes={"near": ["far", "mid", "ground"]}),
    Concept("kingfisher-catch", "animal-kingfisher", "Catch of the day", kingfisher_catch, overrides=KINGF,
            checks=[("hero", "glow"), ("hero2", "glow"), ("hero", "sky"), ("fishc", "glow")],
            fixes={"glow": ["glow2", "light", "far", "sky2"], "sky": ["sky2"]}),
    Concept("kingfisher-dive", "animal-kingfisher", "Kingfisher dive", kingfisher_dive, ["coastal", "meadow", "blush", "dusk"], KINGF,
            checks=[("hero", "sky"), ("hero", "far"), ("hero2", "far"), ("hero", "water")],
            fixes={"far": ["sky2", "mid"], "sky": ["sky2"]}),
    Concept("flamingo-portrait", "animal-flamingo", "Flamingo", flamingo_portrait, overrides=FLAMINGO,
            checks=[("hero", "glow"), ("hero", "sky"), ("beak", "glow"), ("hero", "far")],
            fixes={"glow": ["light", "glow2", "far", "mid"], "sky": ["sky2", "far"], "far": ["mid", "near"]}),
    Concept("flamingo-lagoon", "animal-flamingo", "Pink lagoon", flamingo_lagoon, ["coastal", "meadow", "blush", "dusk"], FLAMINGO,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "lagoon")],
            fixes={"sky": ["sky2", "far"], "far": ["mid", "near"]}),
    Concept("parrot-portrait", "animal-parrot", "Scarlet macaw", parrot_portrait, overrides=MACAW,
            checks=[("hero", "sky"), ("hero", "near"), ("hero", "mid")],
            fixes={"near": ["deep", "far"], "mid": ["far", "near"]}),
    Concept("parrot-flight", "animal-parrot", "Macaw in flight", parrot_flight, overrides=MACAW,
            checks=[("hero", "sky"), ("pop2", "sky"), ("hero", "far"), ("hero", "mid"), ("hero2", "sky")],
            fixes={"far": ["mid", "near"], "mid": ["near", "deep"], "sky": ["sky2"]}),
]
