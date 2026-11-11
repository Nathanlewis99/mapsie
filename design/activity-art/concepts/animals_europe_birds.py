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
    neck = [(98, 96), (84, 80), (70, 62), (62, 52), (50, 56), (44, 66)] + zig([(44, 68), (46, 88), (54, 108), (64, 124)], 7, -6)[1:] + [(80, 112)]
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
    pts = [(70, 92), (52, 90), (34, 84), (24, 70), (24, 56)]
    d.shape("horn", taper(pts, 6.5, 1.4))
    clipped(d, taper(pts, 6.5, 1.4), lambda: d.shape("horntip", "M10 30 H40 V64 H10Z", shadow=False, line=False))


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
    d.limb("hero2", "M76 132 L78 162", 8)
    d.limb("hero2", "M136 132 L134 162", 8)
    # tail
    d.limb("hero", "M152 104 Q160 120 158 140", 3)
    d.shape("hero", P(zig([(160, 136), (156, 148)], 2, 4)), shadow=False)
    body = [(52, 106), (70, 94), (110, 96), (146, 96), (158, 106), (160, 124)] + zig([(158, 138), (110, 142), (60, 140)], 9, -6)[:] + [(48, 124)]
    d.shape("hero", P(body))
    d.limb("hero", "M66 134 L64 164", 9)
    d.limb("hero", "M146 134 L148 164", 9)
    d.marks("mark", "M59 162 h10 v4 h-10Z M143 162 h10 v4 h-10Z M73 160 h10 v4 h-10Z M129 160 h10 v4 h-10Z")
    # horns: one swinging toward us, one behind
    d.shape("horn", taper([(52, 98), (64, 88), (72, 74), (70, 62)], 4.5, 1.2))
    d.shape("hero", P([(28, 108), (34, 96), (52, 94), (62, 104), (58, 124), (48, 136), (34, 138), (26, 128)]))
    d.shape("horn", taper([(40, 98), (26, 92), (16, 80), (16, 68)], 5, 1.2))
    d.shape("nose", P([(24, 120), (34, 120), (38, 132), (30, 140), (22, 136)]))
    d.marks("mark", ellipse(25.5, 129, 2.2, 1.6))
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
    tail = [(134, 104), (152, 110), (170, 124), (186, 136)]
    d.limb("hero2", P([(80, 116), (88, 132), (90, 150)], False), 5)
    d.limb("hero2", P([(122, 112), (130, 130), (124, 150)], False), 5)
    d.limb("mark", P([(88, 136), (90, 150)], False), 5, shadow=False)
    d.limb("mark", P([(129, 136), (124, 150)], False), 5, shadow=False)
    d.shape("hero", taper(tail, 7, 4, wf=lambda t: 5 + 9 * math.sin(math.pi * min(1, t * 1.15)) + 2))
    d.shape("light", taper(tail[2:] + [(194, 141)], 7, 1, wf=lambda t: 8 * (1 - t) + 1.5), shadow=False, spot=True)
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
        pine(d, x, 132, h, "near", snow=True)
    d.band("far", hills(130, 4), line=False)
    d.band("light", "M-30 146 Q40 132 100 140 T230 136")
    group(d, "translate(98 154) scale(1.02) translate(-100 -150)", lambda: fox_side(d))
    d.stroke("far", "M30 166 h8 M50 172 h6 M150 168 h8 M170 160 h6", 2, line=False)
    d.band("far", hills(186, 3, 20), line=False)


# ================================================================ BROWN BEAR
def brownbear_portrait(d: Drawing):
    d.disc("glow", 100, 92, 56)
    for x, h in [(14, 96), (34, 76), (168, 80), (188, 100)]:
        pine(d, x, 172, h, "near")
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
    d.shape("hero", P(body))
    d.shape("hero2", P([(70, 90), (88, 78), (104, 84), (90, 92), (74, 100)]), shadow=False, line=False)
    d.limb("hero", P([(86, 126), (84, 162)], False), 16)
    d.limb("hero", P([(152, 120), (158, 142), (154, 162)], False), 16)
    d.marks("mark", "M76 160 h16 l2 5 h-20Z M146 160 h16 l2 5 h-20Z")
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
        pine(d, x, 146, h, "near")
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
        pine(d, x, 190, h, "near", snow=True)
    d.band("light", hills(184, 4), line=False)
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
    d.stroke("mark", "M146 112 L158 128 M150 136 L162 146 M142 148 L150 160", 2.4)
    flip(d, lambda: d.stroke("mark", "M146 112 L158 128 M150 136 L162 146 M142 148 L150 160", 2.4))
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
    d.limb("hero2", P([(80, 122), (78, 150), (80, 166)], False), 6.5)
    d.limb("hero2", P([(130, 118), (138, 146), (132, 166)], False), 6.5)
    d.shape("hero", P([(56, 104), (70, 92), (104, 94), (134, 90), (146, 98), (148, 112), (138, 124), (106, 126), (76, 126), (60, 120)]))
    d.shape("hero", P([(144, 96), (154, 92, 1), (157, 98), (148, 106)]))
    d.shape("mark", P([(150, 92), (154, 92, 1), (157, 98), (152, 99)]), shadow=False)
    d.limb("hero", P([(68, 118), (66, 148), (64, 166)], False), 7)
    d.limb("hero", P([(142, 110), (152, 140), (148, 166)], False), 7)
    d.marks("mark", "".join(circle(x, y, 1.8) for x, y in [(80, 102), (92, 100), (104, 104), (116, 100), (128, 102), (88, 112),
                                                          (100, 114), (112, 112), (124, 112), (136, 108), (146, 120), (70, 106)]))
    for x in (64, 148):
        d.shape("hero", ellipse(x, 168, 8, 4), shadow=False)
    # head with ruff and tufts
    d.shape("hero", P([(60, 108), (56, 92), (48, 82), (38, 82), (34, 96), (44, 112)]))
    d.shape("hero", P([(48, 70, 1), (52, 52, 1), (60, 72, 1)]))
    d.stroke("mark", "M52 53 L53 40", 2.2)
    d.shape("hero2", P([(52, 92)] + zig([(56, 100), (50, 116), (34, 116)], 4, -5)[1:] + [(30, 104)]), shadow=False)
    d.shape("hero", P([(58, 78), (46, 68), (34, 70), (24, 80), (20, 86, 1), (26, 94), (40, 98), (54, 94)]))
    d.shape("light", P([(22, 88), (26, 94), (40, 98), (34, 90)]), shadow=False, line=False)
    d.marks("mark", P([(20, 85), (25, 84), (24, 89)]))
    d.shape("eye", ellipse(36, 79, 3.2, 2.4), shadow=False)
    d.marks("mark", circle(35.5, 79, 1.3))
    d.stroke("mark", "M44 98 L52 110 M50 96 L58 106", 1.6, line=False)


def lynx_snow(d: Drawing):
    d.disc("glow", 46, 56, 18)
    for x, h, r in [(140, 110, "mid"), (168, 130, "near"), (192, 96, "mid"), (8, 90, "near"), (30, 70, "mid")]:
        pine(d, x, 140, h, r, snow=True)
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
    d.shape("hero", P([(84, 120), (110, 80), (134, 80), (156, 120), (172, 160), (184, 210, 1), (70, 210, 1), (74, 160)]))
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
    d.limb("hero2", P([(82, 126), (84, 146), (82, 160)], False), 6)
    d.limb("hero2", P([(130, 124), (138, 142), (132, 160)], False), 6)
    d.shape("hero", P([(60, 104), (72, 94), (104, 96), (132, 92), (146, 100), (146, 116), (136, 128), (106, 130), (78, 130), (62, 122)]))
    d.shape("hero", P([(144, 98), (152, 92, 1), (150, 104)]))
    d.shape("light", P([(80, 128), (106, 128), (130, 126), (120, 122), (90, 122)]), shadow=False, line=False)
    d.limb("hero", P([(70, 124), (68, 146), (70, 160)], False), 7)
    d.limb("hero", P([(140, 116), (148, 142), (144, 160)], False), 7)
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
    for x, y, a in [(4, 40, 30), (8, 70, 10), (196, 160, 200), (190, 130, 170)]:
        d.shape("near", leaf(x, y, 40, 9, a), line=False)
    d.band("far", hills(176, 4))
    d.limb("dark", "M-10 180 C40 174 120 176 210 168", 10)
    group(d, "translate(102 174) scale(1.0) translate(-100 -172)", lambda: squirrel(d))


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
    group(d, "translate(96 126) scale(.62) translate(-100 -172)", lambda: squirrel(d))
    for x, y in [(150, 128), (186, 80)]:
        needles(d, x, y, 1.1)
    d.band("near", hills(190, 3), line=False)


# ================================================================ colours
DEER = {"hero": "#A4532C", "hero2": "#C98A5A", "mark": "#2A1A12", "light": "#F6EBDD", "mane": "#6E3A20", "horn": "#D8C29A"}
COO = {"hero": "#C2652F", "hero2": "#DE8A4A", "mark": "#2A1812", "horn": "#F0E4C6", "horntip": "#4A3A30", "nose": "#5A3A32",
       "heather": "#A260A8"}
HOG = {"hero": "#6B4A33", "hero2": "#CFA77C", "mark": "#1E1612", "light": "#EBDCC4", "leaf1": "#D9772B", "leaf2": "#B5432C",
       "leaf3": "#E8B23C", "pop": "#D23B2C"}
FOX = {"hero": "#DE6A2A", "hero2": "#B9541F", "light": "#FFF8EE", "mark": "#1F1A17", "eye": "#F2B33D"}
BEAR = {"hero": "#7A4E2E", "hero2": "#A97A4E", "mark": "#22160E", "light": "#FFFFFF"}
LYNX = {"hero": "#C69A64", "hero2": "#EAD8B6", "light": "#FBF3E4", "mark": "#2A2018", "eye": "#C9C44E", "pop": "#C98580"}
IBEX = {"hero": "#9C8468", "hero2": "#5E4B3A", "mark": "#231C15", "light": "#EFE6D8", "horn": "#6A5644", "horn2": "#4A3B2E",
        "eye": "#D9A84A"}
SQUIRREL = {"hero": "#C8551E", "hero2": "#E07A3A", "light": "#FFF3E2", "mark": "#1F1712", "nut": "#7A4A24", "nut2": "#4A2A14",
            "trunk": "#7A4630"}

CONCEPTS = [
    Concept("reddeer-portrait", "animal-red-deer", "Red deer stag", reddeer_portrait, overrides=DEER,
            checks=[("hero", "glow"), ("horn", "glow"), ("horn", "sky"), ("mane", "far")],
            fixes={"glow": ["glow2", "light", "far", "sky2"], "horn": ["#9C7E56", "#EFE3C8"], "far": ["mid", "near", "ground"]}),
    Concept("reddeer-roar", "animal-red-deer", "Highland roar", reddeer_roar, overrides=DEER,
            checks=[("hero", "sky"), ("mane", "sky"), ("horn", "sky"), ("hero", "near"), ("hero", "mid"), ("horn", "far")],
            fixes={"near": ["deep", "far", "ground"], "mid": ["far", "near"], "horn": ["#9C7E56", "#EFE3C8"], "sky": ["sky2"]}),
    Concept("highlandcow-portrait", "animal-highland-cow", "Highland coo", highlandcow_portrait, overrides=COO,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "mid"), ("horn", "sky"), ("horn", "far"), ("hero", "glow")],
            fixes={"far": ["mid", "near", "deep"], "mid": ["near", "deep"], "glow": ["glow2", "light"], "horn": ["#D2BC8E", "#BFA273"]}),
    Concept("highlandcow-glen", "animal-highland-cow", "Coo in the glen", highlandcow_glen, overrides=COO,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "far"), ("horn", "far"), ("horn", "sky"), ("heather", "ground")],
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
]
