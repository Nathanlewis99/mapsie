"""Animals of Sri Lanka, India and Asia: a bold portrait and a habitat scene for each of nineteen animals."""
import math

from _common import Concept, Drawing, cloud, fish, circle, ellipse, waves, hills, rrect, group  # noqa: F401

_uid = [0]


# ================================================================ helpers (copied from wildlife, plus a few new ones)
def _id(prefix):
    _uid[0] += 1
    return f"{prefix}{_uid[0]}"


def clipped(d: Drawing, path: str, fn):
    """Draw fn() clipped to `path` (stripes on a tiger, rosettes on a leopard)."""
    cid = _id("asiaclip")
    tag = f'<clipPath id="{cid}"><path d="{path}"/></clipPath><g clip-path="url(#{cid})">'
    d.raw(tag, tag)
    fn()
    d.raw("</g>", "</g>")


def flip(d: Drawing, fn, cx=100):
    group(d, f"translate({2 * cx} 0) scale(-1 1)", fn)


def scallop(cx, cy, r, n=12, bump=0.22, rot=0.0):
    """A bumpy circle: tree crowns, bushes, blossom clusters."""
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


def blob(pts):
    """A smooth closed shape through the midpoints of a polygon."""
    n = len(pts)
    mids = [((pts[i][0] + pts[(i + 1) % n][0]) / 2, (pts[i][1] + pts[(i + 1) % n][1]) / 2) for i in range(n)]
    s = f"M{mids[-1][0]:.1f} {mids[-1][1]:.1f}"
    for i in range(n):
        s += f" Q{pts[i][0]:.1f} {pts[i][1]:.1f} {mids[i][0]:.1f} {mids[i][1]:.1f}"
    return s + "Z"


def foliage(d: Drawing, pts, role="near", length=60, width=15, line=False):
    for x, y, a in pts:
        d.shape(role, leaf(x, y, length, width, a), line=line)


def blades(d: Drawing, xs, y, h, role="near", w=3.2, lean=0, shadow=False, line=False):
    """Tall grass blades rising from y."""
    for i, x in enumerate(xs):
        hh = h * (0.7 + 0.3 * ((i * 7) % 5) / 4)
        a = -90 + lean + ((i * 37) % 21 - 10)
        d.shape(role, leaf(x, y, hh, w, a), shadow=shadow, line=line)


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


def drop(x, y, r):
    return f"M{x:.1f} {y - r * 1.7:.1f} Q{x + r:.1f} {y:.1f} {x:.1f} {y + r:.1f} Q{x - r:.1f} {y:.1f} {x:.1f} {y - r * 1.7:.1f}Z"


def mist(d: Drawing, y, amp=3, step=40, opacity=".55"):
    d.raw(f'<g opacity="{opacity}">', "")
    d.band("light", waves(y, amp, step), shadow=False, line=False)
    d.raw("</g>", "")


def palm(d: Drawing, x, y, h=70, lean=8, role="dark", s=1.0, line=True):
    tx, ty = x + lean, y - h
    if line or d.paper:
        d.limb(role, f"M{x} {y} Q{x + lean * 0.1} {y - h * 0.55} {tx} {ty}", 5 * s)
    for ang, ln in [(-160, 34), (-125, 30), (-60, 30), (-20, 34), (15, 28), (165, 28)]:
        a = math.radians(ang)
        ex, ey = tx + math.cos(a) * ln * s, ty + math.sin(a) * ln * s
        mx, my = tx + math.cos(a) * ln * s * 0.5, ty + math.sin(a) * ln * s * 0.5 - 9 * s
        w = 6 * s
        d.shape(role, f"M{tx} {ty} Q{mx:.1f} {my - w:.1f} {ex:.1f} {ey:.1f} Q{mx:.1f} {my + w * 0.6:.1f} {tx} {ty}Z",
                shadow=False, line=line)


def ink(d: Drawing, role, path, shadow=True):
    """A shape that is solid in both styles (black faces, panda patches): papercut paper, line ink."""
    if d.paper:
        d.shape(role, path, shadow=shadow)
    else:
        d.marks(role, path)


def ringed(d: Drawing, path, w, role, ring, dash="5 6", spot=False, shadow=True):
    """A thick tail with bands of `ring` across it."""
    d.limb(role, path, w, spot=spot, shadow=shadow)
    if d.paper:
        d.raw(f'<path d="{path}" fill="none" stroke="{d.c[ring]}" stroke-width="{w}" stroke-dasharray="{dash}"/>')
    else:
        d.raw("", f'<path d="{path}" fill="none" stroke="{d.c["ink"]}" stroke-width="{max(w - 3, 1)}" stroke-dasharray="{dash}"/>')


def rosette(x, y, r):
    """A leopard rosette: a broken ring of four blobs."""
    return "".join(circle(x + r * math.cos(a), y + r * math.sin(a), r * 0.42) for a in (0.4, 1.95, 3.5, 5.0))


def cloudspot(x, y, s, rot=0.0):
    """The big, irregular 'cloud' blotch of a clouded leopard (outer, inner)."""
    rs = [1.0, 0.72, 1.1, 0.8, 1.05, 0.7]
    out, inn = [], []
    for i, k in enumerate(rs):
        a = rot + 2 * math.pi * i / len(rs)
        out.append((x + 1.45 * s * k * math.cos(a), y + s * k * math.sin(a)))
        inn.append((x + 1.45 * s * k * 0.62 * math.cos(a), y + s * k * 0.62 * math.sin(a)))
    return blob(out), blob(inn)


def _bez(p, t):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = p
    u = 1 - t
    x = u**3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t**3 * x3
    y = u**3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t**3 * y3
    dx = 3 * u * u * (x1 - x0) + 6 * u * t * (x2 - x1) + 3 * t * t * (x3 - x2)
    dy = 3 * u * u * (y1 - y0) + 6 * u * t * (y2 - y1) + 3 * t * t * (y3 - y2)
    n = math.hypot(dx, dy) or 1
    return x, y, dx / n, dy / n


def frame(p, t, up=0.0, fwd=0.0):
    x, y, dx, dy = _bez(p, t)
    return x + dy * up + dx * fwd, y - dx * up + dy * fwd


def spine(p, prof, n=32, t0=0.0, t1=1.0):
    """Body outline along cubic spine p (tail -> head); prof(t) -> (back, belly) half widths."""
    left, right = [], []
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        x, y, dx, dy = _bez(p, t)
        a, b = prof(t)
        left.append((x + dy * a, y - dx * a))
        right.append((x - dy * b, y + dx * b))
    pts = left + right[::-1]
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"


def flukes(p, span=16, length=12, t=0.0):
    x, y, dx, dy = _bez(p, t)
    bx, by = x - dx * length, y - dy * length
    l = (bx + dy * span, by - dx * span)
    r = (bx - dy * span, by + dx * span)
    nx, ny = x - dx * length * 0.55, y - dy * length * 0.55
    return (f"M{x + dx * 3:.1f} {y + dy * 3:.1f} Q{x + dy * span * 0.4:.1f} {y - dx * span * 0.4:.1f} {l[0]:.1f} {l[1]:.1f} "
            f"Q{nx + dy * 2:.1f} {ny - dx * 2:.1f} {nx:.1f} {ny:.1f} Q{nx - dy * 2:.1f} {ny + dx * 2:.1f} {r[0]:.1f} {r[1]:.1f} "
            f"Q{x - dy * span * 0.4:.1f} {y + dx * span * 0.4:.1f} {x + dx * 3:.1f} {y + dy * 3:.1f}Z")


def fin(p, t, h, sweep, base=10, side=1):
    x, y, dx, dy = _bez(p, t)
    nx, ny = dy * side, -dx * side
    f = (x + dx * base * 0.5, y + dy * base * 0.5)
    b = (x - dx * base * 0.5, y - dy * base * 0.5)
    tip = (x + nx * h - dx * sweep, y + ny * h - dy * sweep)
    c = (f[0] + nx * h * 0.8, f[1] + ny * h * 0.8)
    return (f"M{f[0] - nx * 3:.1f} {f[1] - ny * 3:.1f} Q{c[0]:.1f} {c[1]:.1f} {tip[0]:.1f} {tip[1]:.1f} "
            f"Q{b[0] + nx * h * 0.2:.1f} {b[1] + ny * h * 0.2:.1f} {b[0] - nx * 3:.1f} {b[1] - ny * 3:.1f}Z")


def eye(d: Drawing, x, y, r=4.4, iris="hero2", pupil="mark", slit=False):
    d.shape(iris, circle(x, y, r), shadow=False)
    d.marks(pupil, ellipse(x, y, r * 0.32, r * 0.85) if slit else circle(x, y, r * 0.55))
    d.marks("light", circle(x + r * 0.3, y - r * 0.35, r * 0.24))


def stupa(d: Drawing, x, y, s=1.0, role="far", line=True):
    """A Sri Lankan dagoba: bell dome, square box and spire, base centred at (x, y)."""
    def draw():
        d.shape(role, "M-40 0 C-40 -30 -24 -46 0 -46 C24 -46 40 -30 40 0Z", line=line)
        d.shape(role, rrect(-9, -58, 18, 13, 2), shadow=False, line=line)
        d.shape(role, "M-6 -58 L0 -86 L6 -58Z", shadow=False, line=line)
        d.shape(role, rrect(-46, -2, 92, 6, 2), shadow=False, line=line)
    group(d, f"translate({x} {y}) scale({s})", draw)


# ================================================================ SLOTH BEAR
SLOTH = {"hero": "#2B2725", "hero2": "#CFC0A5", "mark": "#141211", "light": "#F3E8D2", "pop": "#8C6A52"}
SLOTH_MUZZLE = ("M84 92 C82 106 78 120 80 132 C82 144 90 150 100 150 C110 150 118 144 120 132 "
                "C122 120 118 106 116 92 C110 86 90 86 84 92Z")


def slothbear_face(d: Drawing):
    foliage(d, [(-6, 50, 15), (-4, 104, -5), (4, 150, -30), (206, 50, 165), (204, 104, 185), (196, 150, -150)])
    for ex in (50, 150):
        d.shape("hero", tufty(ex, 54, 17, 16, 10, 0.3))
    d.shape("hero", tufty(100, 192, 82, 58, 28, 0.12))
    d.shape("light", "M62 156 L100 202 L138 156 L126 152 L100 182 L74 152Z", shadow=False, spot=True)
    d.shape("hero", tufty(100, 94, 54, 50, 28, 0.17))
    d.shape("hero2", SLOTH_MUZZLE, spot=True)
    d.marks("mark", "M88 128 C88 122 112 122 112 128 C112 136 106 140 100 140 C94 140 88 136 88 128Z")
    d.stroke("mark", "M92 146 Q100 150 108 146", 2)
    for x in (78, 122):
        eye(d, x, 90, 4.2, iris="pop")


def slothbear_yala(d: Drawing):
    d.disc("glow", 150, 58, 24)
    d.band("far", hills(130, 8))
    for x, y, r in [(150, 128, 12), (172, 122, 16), (194, 128, 12)]:
        d.shape("mid", scallop(x, y, r, 9, 0.16), line=False)
    d.band("mid", hills(146, 5, 30))
    # termite mound: sloth bears dig them open for their favourite food
    d.shape("ground", "M14 170 C16 140 24 112 32 96 C35 90 39 90 42 96 C44 104 46 110 48 116 C50 110 54 110 56 116 "
                      "C60 132 62 150 64 170Z", spot=True)
    d.stroke("pop", "M28 132 q4 2 8 0 M34 112 q3 2 6 0 M40 150 q5 2 10 0 M22 156 q4 2 8 0", 1.6, line=False)

    def bear():
        d.limb("mark", "M108 132 L104 166", 13)
        d.limb("mark", "M152 132 L156 166", 13)
        d.shape("hero", tufty(126, 120, 42, 27, 30, 0.09), spot=True)
        d.shape("hero", tufty(98, 112, 27, 27, 18, 0.12), spot=True)
        d.limb("hero", "M92 130 L88 166", 14)
        d.limb("hero", "M142 132 C146 146 144 156 142 166", 14)
        d.stroke("light", "M84 170 q-6 -1 -9 3 M88 171 q-6 0 -8 5 M92 171 q-5 1 -6 6 M138 170 q-6 -1 -9 3 M142 171 q-6 0 -8 5", 1.8)
        for ex, ey in [(64, 100), (80, 96)]:
            d.shape("hero", tufty(ex, ey, 7.5, 7.5, 8, 0.3))
        d.shape("hero", tufty(72, 114, 18, 17, 14, 0.13))
        d.shape("hero2", "M66 108 C56 110 46 118 42 128 C40 133 44 137 49 136 C58 134 68 130 80 124Z")
        d.marks("mark", ellipse(43, 131, 4.2, 3.3))
        d.marks("light", circle(70, 108, 1.8))
        d.shape("light", "M86 122 L94 140 L102 122 L97 121 L94 130 L91 121Z", shadow=False)
    bear()
    d.band("ground", hills(168, 4))
    grass(d, 120, 196, 170, 10, "near")
    d.band("deep", hills(188, 4, 30), line=False)


# ================================================================ ASIAN ELEPHANT
ELE = {"hero": "#8E919B", "hero2": "#A9ACB5", "mark": "#2F3038", "pop": "#E5AFA2"}
ASIAN_HEAD = ("M100 44 C108 33 126 31 136 42 C146 54 146 74 140 88 C134 100 124 108 116 114 L114 152 "
              "C114 164 120 168 127 166 C133 164 135 158 133 152 L143 153 C147 168 137 180 123 180 "
              "C105 180 97 168 97 154 L95 114 C82 108 66 98 60 86 C54 72 54 52 64 42 C74 31 92 33 100 44Z")
ASIAN_EAR = "M64 60 C48 54 30 60 28 78 C26 96 34 110 48 116 C56 112 62 104 66 96Z"


def asianelephant_face(d: Drawing):
    d.disc("glow", 100, 96, 66)
    foliage(d, [(0, 170, -40), (16, 186, -70), (200, 170, -140), (184, 186, -110)])
    for flipit in (False, True):
        def ear():
            d.shape("hero2", ASIAN_EAR, spot=True)
            d.stroke("hero", "M62 62 C50 57 36 62 32 74", 3)
            d.marks("pop", circle(40, 104, 2.2) + circle(47, 108, 1.8) + circle(34, 96, 1.6) + circle(52, 112, 1.4))
        flip(d, ear) if flipit else ear()
    d.shape("hero", ASIAN_HEAD)
    d.stroke("mark", "M100 46 C99 52 99 58 100 62", 1.6, line=False)
    d.marks("pop", circle(98, 96, 2) + circle(104, 100, 1.6) + circle(94, 102, 1.4) + circle(108, 94, 1.5)
            + circle(100, 106, 1.3) + circle(88, 96, 1.2) + circle(112, 104, 1.2))
    d.marks("mark", circle(80, 82, 3) + circle(120, 82, 3))
    d.stroke("mark", "M74 76 Q80 72 86 75 M114 75 Q120 72 126 76", 1.5)
    d.stroke("mark", "M97 128 H114 M97 138 H114 M97 148 H114 M98 158 H114", 1.6)


ASIAN_SIDE = ("M42 124 C40 100 58 82 90 78 C110 76 128 80 138 88 C138 82 143 79 149 80 C153 80 155 82 156 85 "
              "C160 82 166 84 168 90 C172 100 171 112 166 122 C163 134 163 150 167 162 C168 167 163 169 160 165 "
              "C155 154 153 142 151 132 L147 134 L147 168 L135 168 L133 146 L120 146 L118 168 L106 168 L104 142 "
              "L80 142 L78 168 L66 168 L64 142 L57 140 L56 168 L44 168 L45 140 C42 134 42 128 42 124Z")
ASIAN_SIDE_EAR = "M139 96 C133 100 132 116 138 124 C144 128 150 122 150 112 C150 102 146 96 139 96Z"


def asian_side(d: Drawing, ear_spot=True):
    d.stroke("hero", "M44 124 Q36 132 38 144", 2.5)
    d.shape("hero", ASIAN_SIDE)
    d.shape("hero2", ASIAN_SIDE_EAR, shadow=False, spot=ear_spot)
    d.marks("pop", circle(158, 116, 1.6) + circle(162, 122, 1.4) + circle(146, 124, 1.4))
    d.marks("mark", circle(157, 104, 2.2))


def asianelephant_tank(d: Drawing):
    d.disc("glow", 54, 96, 28)
    birds(d, [(130, 50, 1), (146, 42, 0.8), (160, 54, 0.7)])
    d.band("far", hills(112, 5))
    for x in range(-10, 220, 16):
        d.shape("far", scallop(x, 110 - (x * 7 % 7), 9, 8, 0.16), shadow=False, line=False)
    d.band("mid", waves(124, 2, 34))
    # dead trees standing in the tank
    d.limb("dark", "M176 140 L175 88 M175 112 L188 96 M175 102 L164 84 M188 96 L192 86", 3)
    d.limb("dark", "M22 140 L24 100 M24 116 L14 104 M24 108 L32 94", 2.6)
    group(d, "translate(100 156) scale(.8) translate(-105 -166)", lambda: asian_side(d))
    group(d, "translate(54 152) scale(.42) translate(-105 -166)", lambda: asian_side(d, ear_spot=False))
    d.band("near", waves(148, 3, 30))
    d.stroke("light", "M60 156 q8 -5 16 0 M112 158 q8 -5 16 0 M150 152 q6 -4 12 0 M30 166 q6 -4 12 0", 2.2)
    d.band("deep", waves(172, 3, 36), line=False)


# ================================================================ LEOPARD (Sri Lanka)
LEO = {"hero": "#E2A84A", "hero2": "#C8C04A", "mark": "#3A2614", "light": "#FBF1DC", "pop": "#D98C84"}
LEO_HEAD = ("M100 50 C126 50 146 62 152 84 C158 98 158 114 150 128 C140 148 122 160 100 160 "
            "C78 160 60 148 50 128 C42 114 42 98 48 84 C54 62 74 50 100 50Z")


def srileopard_face(d: Drawing):
    foliage(d, [(10, 110, -40), (190, 106, -140), (6, 70, -10), (194, 66, -170)], "mid", 62, 14)
    foliage(d, [(16, 160, -60), (32, 176, -40), (184, 160, -120), (168, 176, -140), (100, 212, -90)], "near", 64, 15)
    for cx in (65, 135):
        d.shape("hero", circle(cx, 60, 11))
        d.shape("light", circle(cx, 62, 5), shadow=False)
    d.shape("hero", LEO_HEAD)
    spots = [(100, 60, 2.4), (90, 64, 2), (110, 64, 2), (82, 70, 2.2), (118, 70, 2.2), (96, 70, 1.8), (104, 70, 1.8),
             (100, 78, 2), (90, 76, 1.6), (110, 76, 1.6), (72, 62, 2), (128, 62, 2)]
    d.marks("mark", "".join(circle(x, y, r) for x, y, r in spots))
    ros = "".join(rosette(x, y, r) for x, y, r in [(56, 102, 5), (144, 102, 5), (60, 124, 5), (140, 124, 5),
                                                   (70, 142, 4.5), (130, 142, 4.5), (52, 84, 4), (148, 84, 4)])
    clipped(d, LEO_HEAD, lambda: d.marks("mark", ros))
    d.shape("light", "M100 104 C112 104 130 110 132 126 C132 142 116 152 100 152 C84 152 68 142 68 126 C70 110 88 104 100 104Z", shadow=False)
    d.shape("light", ellipse(80, 90, 12, 8), shadow=False)
    d.shape("light", ellipse(120, 90, 12, 8), shadow=False)
    for x in (80, 120):
        eye(d, x, 92, 6, iris="hero2")
    d.shape("pop", "M90 112 H110 L100 124Z", shadow=False, spot=True)
    d.stroke("mark", "M100 124 V130 M100 130 Q92 138 86 132 M100 130 Q108 138 114 132", 2)
    d.marks("mark", circle(84, 122, 1.3) + circle(78, 126, 1.3) + circle(116, 122, 1.3) + circle(122, 126, 1.3)
            + circle(80, 132, 1.2) + circle(120, 132, 1.2))


CAT_LIE = "M64 110 C70 98 90 94 112 96 C130 96 146 100 152 112 C156 120 150 130 140 130 L76 130 C66 128 62 120 64 110Z"
CAT_LIE_HEAD = "M42 92 C42 80 52 74 62 76 C72 78 78 86 76 96 C74 106 66 110 58 110 C48 110 42 102 42 92Z"


def cat_lying(d: Drawing, tail, tail_w=6, spots="rosette", ear_r=5.5):
    """A big cat lying sphinx-like, facing left, head turned to us; lies on y=130."""
    d.limb("hero", tail, tail_w, spot=True)
    d.limb("hero", "M80 124 L52 127", 9)
    d.shape("hero", ellipse(48, 127, 7.5, 4.5), shadow=False)
    d.shape("hero", CAT_LIE)
    d.stroke("mark", "M118 128 C116 112 128 104 140 108", 1.6, line=False)
    if spots == "rosette":
        pat = "".join(rosette(x, y, 3.6) for x, y in [(84, 104), (98, 102), (112, 102), (126, 104), (140, 108),
                                                      (92, 116), (106, 114), (120, 116), (134, 120), (78, 120)])
    else:
        pat = "".join(rosette(x, y, 4.4) for x, y in [(86, 106), (104, 103), (122, 105), (140, 112), (96, 120), (116, 120)])
    clipped(d, CAT_LIE, lambda: d.marks("mark", pat))
    def head():
        for ex in (50, 68):
            d.shape("hero", circle(ex, 80, ear_r))
            d.shape("light", circle(ex, 81, ear_r * 0.5), shadow=False)
        d.shape("hero", CAT_LIE_HEAD)
        d.marks("mark", circle(52, 84, 1.2) + circle(60, 82, 1.3) + circle(68, 84, 1.2) + circle(56, 80, 1) + circle(64, 79, 1))
        d.shape("light", ellipse(59, 102, 8.5, 6), shadow=False)
        d.marks("mark", circle(53, 92, 1.9) + circle(66, 92, 1.9) + "M56 98 L62 98 L59 102Z")
    group(d, "translate(60 104) scale(1.15) translate(-60 -104)", head)


def srileopard_rock(d: Drawing):
    d.disc("glow", 150, 58, 26)
    birds(d, [(36, 50, 1), (50, 42, 0.8)])
    d.band("far", hills(140, 8))
    for x, y, r in [(16, 140, 14), (196, 140, 14)]:
        d.shape("mid", scallop(x, y, r, 9, 0.16), line=False)
    d.shape("rock2", "M120 200 C126 166 146 152 170 152 C196 154 214 176 214 200Z")
    d.shape("rock", "M8 200 C10 160 36 128 92 126 C138 124 166 148 174 200Z")
    d.stroke("rock2", "M30 168 C40 154 54 148 68 148 M120 150 C134 156 144 166 150 180", 2.4, line=False)
    group(d, "translate(102 128) scale(1.1) translate(-96 -130)", lambda: cat_lying(d, "M150 116 C164 120 168 136 164 152 C162 160 166 166 172 164"))
    d.band("deep", hills(192, 3, 30), line=False)


# ================================================================ BENGAL TIGER
TIGER = {"hero": "#E8842C", "hero2": "#C96A1E", "mark": "#231915", "light": "#FFF6EA", "pop": "#D9737B"}
CAT_TORSO = ("M58 96 C66 84 90 82 112 84 C130 84 146 86 156 92 C166 98 166 112 158 120 C150 126 136 126 124 124 "
             "C108 124 90 126 76 124 C64 122 56 110 58 96Z")
CAT_HEAD = ("M80 82 C74 72 60 68 48 72 C38 75 32 82 28 90 C24 94 22 100 24 104 C26 108 30 110 34 110 "
            "C38 116 48 120 60 120 C72 120 82 112 84 102Z")


def cat_walk(d: Drawing, pattern, tail, tail_w=7, foot=158, head_marks=None, tail_ring=None):
    """A big cat walking left. pattern(torso_path) draws the coat; feet on y=foot."""
    d.limb("hero2", f"M94 112 L100 {foot}", 13)
    d.limb("hero2", f"M148 112 C156 126 158 {foot - 14} 162 {foot}", 13)
    d.shape("hero2", ellipse(102, foot + 1, 8, 4.5) + ellipse(164, foot + 1, 8, 4.5), shadow=False)
    if tail_ring:
        ringed(d, tail, tail_w, "hero", tail_ring, "4 6", spot=True)
    else:
        d.limb("hero", tail, tail_w, spot=True)
    d.shape("hero", CAT_TORSO)
    d.limb("hero", f"M80 112 L70 {foot}", 14)
    d.limb("hero", f"M134 112 C142 126 140 {foot - 14} 136 {foot}", 14)
    d.shape("hero", ellipse(68, foot + 1, 9, 5) + ellipse(134, foot + 1, 9, 5), shadow=False)
    pattern(CAT_TORSO)
    d.shape("light", "M76 124 C96 130 120 130 140 124 C126 132 96 134 78 128Z", shadow=False, line=False)
    d.shape("hero", circle(64, 74, 7.5))
    d.shape("light", circle(64, 75, 3.6), shadow=False)
    d.shape("hero", CAT_HEAD)
    d.shape("light", "M34 108 C44 116 58 120 72 114 C78 110 82 104 84 98 C82 114 66 126 50 124 C42 122 36 116 34 108Z", shadow=False)
    d.shape("light", "M24 102 C28 108 36 112 44 110 C40 104 36 99 30 97Z", shadow=False)
    d.shape("pop", "M22 95 L29 94 L27 100Z", shadow=False)
    d.shape("light", ellipse(46, 86, 5, 3.4), shadow=False)
    d.marks("mark", circle(45, 86, 2))
    if head_marks:
        d.marks("mark", head_marks)


def tiger_stripes(path):
    s = ""
    for i, x in enumerate(range(86, 162, 9)):
        ln = 24 if i % 2 else 34
        s += f"M{x - 3} 80 L{x + 4} 80 Q{x + 2} {84 + ln * 0.5} {x - 2} {84 + ln} Q{x - 2} {84 + ln * 0.5} {x - 3} 80Z "
    for x in range(92, 150, 12):
        s += f"M{x} 130 L{x + 6} 130 L{x + 1} 114Z "
    s += "M150 96 L170 100 L150 104Z M152 110 L168 108 L154 116Z M60 98 L74 96 L62 104Z"
    return s


def bengaltiger_stride(d: Drawing):
    d.disc("glow", 104, 100, 62)
    d.band("far", hills(150, 6))
    for x, y, a in [(4, 152, -70), (14, 156, -100), (190, 150, -110), (198, 156, -80)]:
        d.shape("near", leaf(x, y, 50, 6, a), line=False)

    def pattern(p):
        clipped(d, p, lambda: d.marks("mark", tiger_stripes(p)))
        d.marks("mark", "M66 120 L78 122 L66 126Z M64 134 L76 136 L64 140Z M128 132 L142 130 L130 138Z M126 146 L140 144 L128 150Z")
    group(d, "translate(104 166) scale(.96) translate(-100 -160)", lambda: cat_walk(
        d, pattern, "M160 100 C176 106 180 124 174 140 C172 148 164 150 160 146", 7,
        head_marks="M60 74 L56 86 L63 82Z M72 80 L66 92 L75 89Z M58 104 L72 100 L62 108Z M44 78 L40 84 L47 82Z",
        tail_ring="mark"))
    d.band("ground", hills(170, 3))
    grass(d, 6, 60, 172, 12, "near")
    d.band("deep", hills(188, 3, 30), line=False)


def tiger_face_front(d: Drawing, eyes_dir=0):
    """Frontal tiger head centred (100, 100), about 116 wide."""
    for cx in (60, 140):
        d.shape("hero", circle(cx, 54, 13))
        d.shape("light", circle(cx, 56, 6), shadow=False)
    head = ("M100 42 C128 42 148 54 154 76 C162 88 166 104 160 118 C152 140 128 156 100 156 "
            "C72 156 48 140 40 118 C34 104 38 88 46 76 C52 54 72 42 100 42Z")
    d.shape("hero", head)
    d.shape("light", "M44 104 C52 118 66 130 82 134 L72 148 C58 140 46 126 42 110Z M156 104 C148 118 134 130 118 134 L128 148 C142 140 154 126 158 110Z", shadow=False)
    d.marks("mark", "M100 46 L94 66 L100 62 L106 66Z M84 48 L82 62 L88 56Z M116 48 L118 62 L112 56Z "
                    "M40 92 L62 98 L40 102Z M40 112 L60 112 L44 120Z M160 92 L138 98 L160 102Z M160 112 L140 112 L156 120Z "
                    "M72 136 L80 124 L82 140Z M128 136 L120 124 L118 140Z")
    d.shape("light", "M100 100 C112 100 132 106 134 122 C134 136 116 146 100 146 C84 146 66 136 66 122 C68 106 88 100 100 100Z", shadow=False)
    d.shape("light", ellipse(78, 84, 12, 7), shadow=False)
    d.shape("light", ellipse(122, 84, 12, 7), shadow=False)
    d.shape("hero2", ellipse(78 + eyes_dir, 86, 6.5, 6), shadow=False, spot=True)
    d.shape("hero2", ellipse(122 + eyes_dir, 86, 6.5, 6), shadow=False, spot=True)
    d.marks("mark", ellipse(78 + eyes_dir, 86, 2.2, 4.5) + ellipse(122 + eyes_dir, 86, 2.2, 4.5))
    d.shape("pop", "M90 108 H110 L100 120Z", shadow=False)
    d.stroke("mark", "M100 120 V126 M100 126 Q92 134 86 128 M100 126 Q108 134 114 128", 2)


def bengaltiger_grass(d: Drawing):
    d.disc("glow", 146, 48, 15)
    # Ranthambore fort on its ridge
    d.band("far", "M-30 96 L10 92 L46 74 L126 70 L166 82 L230 90")
    d.shape("deep", "M58 74 V60 H63 V56 H68 V60 H76 V56 H81 V60 H90 V54 H95 V60 H104 V56 H109 V60 H118 V72Z", shadow=False)
    d.shape("deep", "M124 60 a8 8 0 0 1 16 0Z M126 60 H138 V70 H126Z M98 54 a5 5 0 0 1 10 0Z", shadow=False)
    d.band("mid", hills(116, 6))
    blades(d, list(range(-6, 210, 9)), 140, 56, "near", 3.6, line=False)
    shoulders = "M48 210 C52 162 72 138 100 138 C128 138 148 162 152 210Z"
    d.shape("hero", shoulders)
    clipped(d, shoulders, lambda: d.marks("mark", "M52 150 L74 158 L54 162Z M50 170 L72 174 L50 180Z M148 150 L126 158 L146 162Z M150 170 L128 174 L150 180Z"))
    d.shape("light", "M82 140 C88 156 112 156 118 140 C112 170 88 170 82 140Z", shadow=False)
    group(d, "translate(100 108) scale(.72) translate(-100 -100)", lambda: tiger_face_front(d, eyes_dir=-3))
    blades(d, [8, 20, 30, 42, 52, 62, 74, 128, 140, 150, 160, 172, 182, 194], 196, 64, "deep", 4, shadow=True)
    blades(d, [86, 96, 106, 116], 200, 38, "deep", 3.6, shadow=True)
    d.band("deep", hills(186, 3, 30), line=False)


# ================================================================ PEACOCK
PEACOCK = {"hero": "#1C56B8", "hero2": "#A8703F", "train": "#2E7A4B", "train2": "#1F5C38", "eye1": "#D8A93E",
           "eye2": "#1FA39A", "eye3": "#1A2A6C", "mark": "#10183A", "light": "#FFFFFF"}


def fan(cx, cy, r, a0, a1, n=18, bump=0.05):
    """A scalloped fan (the peacock's train) from angle a0 to a1 (degrees, clockwise)."""
    s = f"M{cx} {cy}"
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        if i == 0:
            s += f" L{x:.1f} {y:.1f}"
        else:
            m = math.radians(a0 + (a1 - a0) * (i - 0.5) / n)
            qx, qy = cx + r * (1 + bump * 2) * math.cos(m), cy + r * (1 + bump * 2) * math.sin(m)
            s += f" Q{qx:.1f} {qy:.1f} {x:.1f} {y:.1f}"
    return s + "Z"


def eyespot(d: Drawing, x, y, ang, s=1.0, spot=True):
    rot = f'transform="rotate({ang + 90:.1f} {x:.1f} {y:.1f})"'
    d.shape("eye1", ellipse(x, y, 6.2 * s, 8 * s), extra=rot, shadow=False)
    d.shape("eye2", ellipse(x, y + 0.8 * s, 4 * s, 5.2 * s), extra=rot, shadow=False, spot=spot)
    d.marks("eye3", ellipse(x, y + 1.2 * s, 2 * s, 2.8 * s))


def peacock_display(d: Drawing):
    cx, cy = 100, 124
    d.shape("train", fan(cx, cy, 80, 158, 382, 22, 0.05))
    shafts = "".join(f"M{cx} {cy} L{cx + 78 * math.cos(math.radians(a)):.1f} {cy + 78 * math.sin(math.radians(a)):.1f} "
                     for a in range(162, 380, 10))
    d.stroke("train2", shafts, 1.2, line=False)
    for r, n, a0, a1, s in [(68, 11, 168, 372, 1.05), (50, 9, 176, 364, 0.95), (32, 6, 186, 354, 0.85)]:
        for i in range(n):
            a = a0 + (a1 - a0) * i / (n - 1)
            if r == 32 and 250 < a < 290:
                continue
            x, y = cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))
            eyespot(d, x, y, a, s)
    d.band("ground", hills(168, 3))
    # wings and blue body
    d.shape("hero2", "M86 118 C72 126 70 146 78 162 L94 158Z")
    d.shape("hero2", "M114 118 C128 126 130 146 122 162 L106 158Z")
    d.stroke("mark", "M80 132 L90 130 M78 142 L90 140 M80 152 L92 150 M120 132 L110 130 M122 142 L110 140 M120 152 L108 150", 1.4, line=False)
    d.stroke("mark", "M95 160 L93 176 M105 160 L107 176 M93 176 L88 180 M93 176 L96 181 M107 176 L104 181 M107 176 L112 180", 2.2)
    d.shape("hero", "M100 66 C106 68 108 78 107 90 C106 102 114 112 116 128 C118 146 110 162 100 162 "
                    "C90 162 82 146 84 128 C86 112 94 102 93 90 C92 78 94 68 100 66Z", spot=True)
    d.stroke("mark", "M100 58 L100 42 M100 58 L93 44 M100 58 L107 44 M100 58 L88 48 M100 58 L112 48", 1.2)
    d.marks("hero", circle(100, 41, 2.2) + circle(92.5, 43, 2) + circle(107.5, 43, 2) + circle(87, 47.5, 1.8) + circle(113, 47.5, 1.8))
    d.shape("hero", circle(100, 64, 8.5))
    d.shape("light", "M92 62 L97 63 L96 66Z M108 62 L103 63 L104 66Z", shadow=False)
    d.marks("mark", circle(96, 64, 1.5) + circle(104, 64, 1.5))
    d.shape("eye1", "M97.5 68 L100 75 L102.5 68Z", shadow=False)


def peacock_yala(d: Drawing):
    d.disc("glow", 150, 56, 24)
    d.band("far", hills(136, 8))
    for x, y, r in [(20, 134, 14), (186, 132, 16)]:
        d.shape("mid", scallop(x, y, r, 9, 0.16), line=False)
    d.band("mid", hills(158, 5, 30))
    # a dead tree in the scrub
    d.limb("dark", "M34 210 C38 160 34 120 44 92 M40 120 L18 100", 8)
    d.limb("dark", "M44 94 C80 92 140 96 200 80", 7)
    d.limb("dark", "M150 90 L170 66", 4)
    # long train hanging from the branch
    train = "M100 94 C122 100 140 128 150 186 L120 190 C118 150 108 120 92 102Z"
    d.shape("train", train, spot=True)
    d.stroke("train2", "M104 100 C120 120 130 150 136 188", 1.2, line=False)
    for x, y, s in [(110, 110, 0.7), (118, 126, 0.8), (124, 144, 0.9), (130, 162, 1.0), (136, 180, 1.05), (112, 126, 0.0)]:
        if s:
            eyespot(d, x, y, -90, s, spot=False)
    for x, y, s in [(140, 172, 0.8), (124, 172, 0.8), (128, 154, 0.75)]:
        eyespot(d, x, y, -90, s, spot=False)
    # the bird, perched facing left
    d.stroke("mark", "M86 96 L84 100 M94 96 L94 100", 2)
    d.shape("hero", "M72 90 C70 80 80 72 94 74 C106 76 114 84 114 92 C112 98 104 100 94 100 L82 100 C76 100 72 96 72 90Z")
    d.shape("hero2", "M88 80 C98 78 108 82 113 90 C106 95 96 95 88 90Z", shadow=False)
    d.stroke("mark", "M94 82 L96 91 M100 81 L102 92 M106 84 L107 92", 1, line=False)
    d.shape("hero", "M74 86 C72 74 74 60 76 50 C78 44 86 44 86 50 C84 60 84 72 90 82Z")
    d.shape("hero", circle(80, 46, 7))
    d.stroke("mark", "M82 40 L86 26 M82 40 L80 26 M82 40 L91 28", 1.1)
    d.marks("hero", circle(86, 26, 1.8) + circle(80, 26, 1.8) + circle(91, 28, 1.6))
    d.shape("eye1", "M74 44 L65 47 L74 49Z", shadow=False)
    d.shape("light", "M76 42 L84 44 L78 46Z M76 49 L84 49 L78 51Z", shadow=False)
    d.marks("mark", circle(78, 45.5, 1.5))
    d.band("ground", hills(184, 3))


# ================================================================ LANGUR
LANGUR = {"hero": "#D6D1C6", "hero2": "#A9A397", "mark": "#1E1E22", "light": "#F4F1EA", "pop": "#C98B3A"}
LANGUR_FACE = ("M100 70 C116 70 128 80 128 96 C128 112 120 126 108 134 C104 137 96 137 92 134 "
               "C80 126 72 112 72 96 C72 80 84 70 100 70Z")


def langur_face(d: Drawing):
    foliage(d, [(-6, 50, 15), (0, 100, -5), (206, 50, 165), (200, 100, 185)], "mid", 56, 14)
    d.limb("hero2", "M168 210 C182 170 186 120 172 86 C166 72 154 70 150 80", 10)
    d.shape("hero", tufty(100, 188, 64, 50, 24, 0.12))
    for x in (52, 148):
        ink(d, "mark", circle(x, 96, 8.5))
    d.shape("hero", tufty(100, 94, 48, 46, 26, 0.13))
    d.shape("light", tufty(100, 62, 22, 12, 12, 0.3), shadow=False)
    ink(d, "mark", LANGUR_FACE)
    d.shape("hero2", "M74 88 C82 80 94 82 100 87 C106 82 118 80 126 88 C118 87 108 89 100 93 C92 89 82 87 74 88Z", shadow=False, line=False)
    for x in (88, 112):
        d.shape("pop", circle(x, 98, 4.6), shadow=False)
        d.marks("mark", circle(x, 98, 2.3))
        d.marks("light", circle(x + 1.3, 96.6, 1))
    d.marks("hero2", ellipse(96, 114, 2, 1.4) + ellipse(104, 114, 2, 1.4))
    d.stroke("hero2", "M91 123 Q100 127 109 123", 1.8, line=False)


def langur_ruins(d: Drawing):
    d.disc("glow", 40, 52, 16)
    d.band("far", hills(120, 6))
    stupa(d, 54, 128, 0.9, "stupa")
    for x in (150, 168, 186):
        d.shape("stupa", rrect(x - 4, 92, 8, 36, 2), line=False)
    d.band("mid", hills(132, 4, 30))
    # the ruined wall
    d.shape("rock", "M-30 142 H230 V230 H-30Z")
    d.stroke("rock2", "M-30 158 H230 M-30 176 H230 M20 142 V158 M60 142 V158 M100 142 V158 M140 142 V158 M180 142 V158 "
                      "M40 158 V176 M80 158 V176 M120 158 V176 M160 158 V176 M200 158 V176", 1.8, line=False)

    def monkey():
        d.limb("hero", "M150 138 C160 152 160 172 152 190 C148 198 150 204 156 208", 6)
        d.shape("hero", "M116 142 C110 124 112 104 124 96 C136 90 150 96 154 110 C158 124 156 136 150 142Z")
        d.shape("hero", ellipse(120, 134, 13, 8))
        d.limb("hero2", "M124 108 C118 118 116 126 114 134", 7)
        ink(d, "mark", ellipse(112, 137, 4.5, 3.5))
        ink(d, "mark", ellipse(110, 142, 6, 3))
        ink(d, "mark", circle(130, 82, 4))
        d.shape("hero", tufty(122, 84, 14, 13, 12, 0.18))
        ink(d, "mark", "M114 76 C107 78 104 86 106 93 C108 99 114 101 118 97 C121 91 119 81 114 76Z", shadow=False)
        d.marks("light", circle(110, 84, 1.3))
    group(d, "translate(130 142) scale(1.35) translate(-130 -142)", monkey)


# ================================================================ INDIAN RHINO
RHINO = {"hero": "#8E8379", "hero2": "#B3A89E", "mark": "#463D36", "light": "#F4EEE6"}
RHINO_BODY = ("M56 100 C64 82 90 74 116 74 C144 74 164 84 170 102 C174 114 174 128 168 140 L168 166 L152 166 "
              "L150 148 L138 150 L136 166 L120 166 L118 148 L88 148 L86 166 L70 166 L68 146 C60 140 56 130 56 120Z")
RHINO_HEAD = "M68 96 C56 88 42 92 34 102 C26 112 22 124 24 132 C26 138 32 140 40 138 C50 136 58 132 66 126 C74 118 74 104 68 96Z"


def rhino(d: Drawing, spot=True):
    d.stroke("hero", "M168 104 Q176 112 174 124", 2.4)
    d.shape("hero", RHINO_BODY)
    d.shape("hero", "M60 92 L57 76 C58 71 65 72 66 77 L68 92Z")
    d.shape("hero", RHINO_HEAD)
    d.shape("hero2", "M25 124 C18 112 18 98 25 86 C29 98 34 110 39 120Z", spot=spot)
    folds = ("M68 98 C72 110 72 124 66 134 M88 78 C80 98 82 124 90 148 M140 78 C132 100 132 126 140 150 "
             "M90 132 C108 137 124 137 140 132 M140 130 C150 135 160 135 170 130 M42 132 C48 128 54 126 60 120")
    d.stroke("mark", folds, 2.4)
    d.marks("hero2", "".join(circle(x, y, 1.6) for x, y in [(74, 102), (80, 110), (76, 120), (84, 126), (72, 112),
                                                             (150, 100), (158, 108), (148, 116), (160, 120), (154, 92), (164, 98)]))
    d.marks("mark", circle(46, 114, 2) + ellipse(28, 132, 1.6, 1))


def indianrhino_side(d: Drawing):
    d.disc("glow", 116, 94, 60)
    d.band("far", hills(150, 6))
    blades(d, [2, 10, 18, 182, 190, 198], 160, 50, "near", 3)
    group(d, "translate(102 164) scale(.95) translate(-100 -166)", lambda: rhino(d))
    d.band("ground", hills(170, 3))
    grass(d, 120, 200, 172, 10, "near")
    d.band("deep", hills(188, 3, 30), line=False)


def egret(d: Drawing, x, y, s=1.0, face=-1):
    """A little white cattle egret standing at (x, y)."""
    def draw():
        d.stroke("dark", "M-2 0 L-3 8 M3 0 L4 8", 1.4)
        d.shape("light", "M-9 -4 C-8 -12 4 -14 10 -8 C12 -4 8 1 0 1 C-6 1 -9 -1 -9 -4Z")
        d.shape("light", "M6 -9 C6 -16 8 -20 12 -21 C15 -21 16 -18 14 -16 C12 -14 10 -12 10 -8Z", shadow=False)
        d.shape("pop", "M15 -19 L21 -18 L15 -16.6Z", shadow=False)
        d.marks("dark", circle(12.6, -18.8, 0.8))
    group(d, f"translate({x} {y}) scale({-s * face} {s})", draw)


def indianrhino_kaziranga(d: Drawing):
    d.disc("glow", 46, 60, 18)
    d.band("far", hills(110, 6))
    d.limb("dark", "M164 112 L162 72 M162 86 L148 70 M162 80 L176 64", 3.4)
    for x, y, r in [(146, 66, 9), (178, 60, 10), (162, 56, 9)]:
        d.shape("dark", scallop(x, y, r, 8, 0.14), shadow=False)
    mist(d, 112, 3, 40, ".6")
    d.band("mid", hills(124, 4, 30))
    blades(d, list(range(-4, 210, 8)), 136, 40, "near", 3.2)
    flip(d, lambda: group(d, "translate(98 152) scale(.72) translate(-100 -166)", lambda: rhino(d)))
    egret(d, 104, 98, 0.9, face=-1)
    d.band("sky2", waves(148, 2, 30))
    d.stroke("light", "M54 156 q8 -4 16 0 M120 158 q8 -4 16 0 M84 166 q6 -3 12 0 M150 170 q6 -3 12 0", 2.2)
    d.band("deep", waves(178, 2, 36), line=False)


# ================================================================ WATER BUFFALO
BUFFALO = {"hero": "#4A4B52", "hero2": "#6E6F78", "mark": "#1C1C21", "horn": "#8C8475", "horn2": "#6B6457", "light": "#F1EEE6",
           "pop": "#F2C14E"}
BUF_HORN = "M90 78 C62 86 30 80 24 60 C20 46 28 34 42 28 C35 38 35 52 45 60 C58 68 76 66 92 64Z"
BUF_HEAD = ("M100 56 C114 56 124 62 126 74 C128 92 122 110 118 130 C116 142 110 150 100 150 C90 150 84 142 82 130 "
            "C78 110 72 92 74 74 C76 62 86 56 100 56Z")


def waterbuffalo_face(d: Drawing):
    d.disc("glow", 100, 70, 40)
    d.band("far", hills(140, 4))
    for x in (14, 186):
        palm(d, x, 150, 50, 6 if x < 100 else -6, "mid", 0.8, line=False)
    d.band("mid", "M-30 150 L230 150")
    d.stroke("near", "M-30 162 L230 160 M-30 176 L230 174", 1.6, line=False)
    d.shape("hero", "M34 210 C40 166 66 144 100 144 C134 144 160 166 166 210Z")
    d.stroke("light", "M80 176 L100 186 L120 176", 3)
    for side in (False, True):
        def horn():
            d.shape("horn", BUF_HORN, spot=True)
            d.stroke("horn2", "M29 66 L37 61 M35 73 L42 65 M44 78 L48 68 M55 80 L57 70 M67 80 L67 70", 1.4)
            d.shape("hero", ellipse(64, 92, 14, 6), extra='transform="rotate(18 64 92)"')
            d.shape("hero2", ellipse(64, 92, 9, 3.4), extra='transform="rotate(18 64 92)"', shadow=False)
        flip(d, horn) if side else horn()
    d.shape("hero", BUF_HEAD)
    d.shape("hero", tufty(100, 62, 14, 8, 10, 0.3), shadow=False)
    d.shape("hero2", ellipse(100, 138, 19, 13), shadow=False)
    d.marks("mark", ellipse(92, 138, 3, 4.2) + ellipse(108, 138, 3, 4.2))
    for x in (82, 118):
        d.marks("light", circle(x, 92, 3.8))
        d.marks("mark", circle(x, 92, 2.4))


def buffalo_wallow(d: Drawing, egret_on=False):
    """A water buffalo up to its back in water, facing left; waterline at y=140."""
    d.shape("hero", "M60 140 C62 124 86 116 118 116 C140 116 152 126 156 140Z")
    d.shape("horn2", "M80 112 C90 100 106 96 118 100 C122 102 122 106 118 108 C108 104 96 106 86 116Z", shadow=False)
    d.shape("hero", "M82 126 C76 112 62 104 48 108 C38 111 30 118 30 127 C30 134 34 138 40 138 L80 138Z")
    d.shape("hero", ellipse(74, 116, 8, 3.4), extra='transform="rotate(-20 74 116)"')
    d.shape("horn", "M62 110 C68 96 86 88 104 90 C112 91 117 97 113 104 C108 98 100 97 92 99 C82 101 74 107 70 116Z", spot=True)
    d.marks("light", circle(52, 116, 2.2))
    d.marks("mark", circle(52, 116, 1.3) + ellipse(34, 128, 1.8, 1.2))
    if egret_on:
        egret(d, 122, 116, 1.1, face=-1)


def waterbuffalo_paddy(d: Drawing):
    d.disc("glow", 150, 62, 24)
    d.band("far", hills(110, 4))
    for x, lean in [(26, 6), (176, -8), (192, 4)]:
        palm(d, x, 116, 62, lean, "dark", 0.85)
    d.band("mid", waves(118, 2, 36))
    group(d, "translate(136 112) scale(-.52 .52) translate(-100 -140)", lambda: buffalo_wallow(d))
    group(d, "translate(96 140) scale(1.0) translate(-100 -140)", lambda: buffalo_wallow(d, egret_on=True))
    d.band("near", waves(140, 2, 30))
    d.stroke("light", "M30 148 q10 -5 20 0 M84 150 q10 -5 20 0 M128 150 q8 -4 16 0 M50 164 q8 -4 16 0 M150 166 q8 -4 16 0", 2.2)
    d.band("deep", waves(176, 3, 36), line=False)


# ================================================================ BLUE WHALE
BLUEWHALE = {"hero": "#5C7EA3", "hero2": "#93AAC4", "mark": "#1E2F42", "mottle": "#8DA6C1"}


def bluewhale_side(d: Drawing):
    d.band("sky2", waves(40, 5, 26))
    d.band("far", waves(64, 5, 28))
    d.band("mid", waves(92, 6, 30))
    d.raw('<g opacity=".18" fill="#fff"><path d="M40 0 L62 0 L100 200 L78 200Z"/><path d="M120 0 L132 0 L172 200 L160 200Z"/></g>', "")
    d.band("near", waves(152, 6, 34))
    p = ((28, 108), (70, 98), (130, 90), (186, 102))
    prof = lambda t: (2 + 12 * math.sin(math.pi * (0.05 + 0.75 * t ** 1.3)), 2 + 14 * math.sin(math.pi * (0.05 + 0.75 * t ** 1.3)))
    d.shape("hero", flukes(p, 17, 13))
    d.shape("hero", fin(p, 0.26, 5, 4, 7))
    d.shape("hero", spine(p, prof))
    d.shape("hero2", spine(p, lambda t: (-4 - 3 * t, prof(t)[1] - 1.2), t0=0.6, t1=0.985), shadow=False)
    for k in range(4):
        a = frame(p, 0.64, -8 - 2.6 * k)
        b = frame(p, 0.97, -6 - 2.2 * k)
        d.stroke("mark", f"M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f}", 1.1, line=k % 2 == 0)
    mot = ""
    for t, u, r in [(0.3, 2, 1.8), (0.38, 6, 1.4), (0.46, 1, 2), (0.52, 7, 1.4), (0.58, 3, 1.8), (0.66, 8, 1.3), (0.7, 2, 1.6),
                    (0.78, 7, 1.2), (0.42, -3, 1.3), (0.34, -2, 1.1)]:
        q = frame(p, t, u)
        mot += ellipse(q[0], q[1], r * 1.5, r)
    d.marks("mottle", mot) if d.paper else None
    fx, fy = frame(p, 0.72, -12)
    d.shape("hero", leaf(fx, fy, 22, 4, 150))
    e = frame(p, 0.9, 1)
    d.marks("mark", circle(e[0], e[1], 1.5))
    for x, y, s in [(150, 50, 0.6), (160, 44, 0.5), (164, 54, 0.55), (40, 140, 0.6), (50, 146, 0.5)]:
        d.shape("pop", fish(x, y, s, right=True), shadow=False)
    d.band("deep", waves(176, 5, 36), line=False)


def bluewhale_mirissa(d: Drawing):
    d.disc("glow", 160, 50, 15)
    d.shape("light", cloud(110, 36, 0.8), shadow=False)
    d.band("far", "M-30 102 L150 102 L170 96 L190 98 L230 100", line=False)
    # whale-watching boat out of Mirissa
    group(d, "translate(130 76) scale(.42)", lambda: (
        d.shape("light", rrect(30, 40, 50, 18, 3)),
        d.shape("light", rrect(36, 26, 34, 14, 3)),
        d.shape("sky2", rrect(36, 44, 40, 6, 2), shadow=False),
        d.shape("pop", "M10 58 H104 C100 70 94 76 84 76 H24 C16 74 12 66 10 58Z", spot=True),
    ))
    d.band("mid", waves(108, 3, 30))
    # the tall, straight blow of a blue whale
    d.shape("light", "M60 134 C58 112 53 90 45 70 C39 58 41 46 49 44 C51 36 58 34 62 40 C66 34 74 36 76 44 "
                     "C84 46 86 58 80 70 C72 90 68 112 68 134Z", spot=True)
    for x, y, r in [(42, 54, 2.2), (82, 52, 2.4), (46, 70, 1.8), (78, 68, 1.8), (60, 22, 1.8)]:
        d.shape("light", drop(x, y, r), shadow=False)
    d.shape("hero", "M30 148 C40 136 70 126 112 125 C150 124 190 130 230 142 L230 170 L30 170Z")
    d.shape("hero", "M170 130 L180 120 L184 132Z", shadow=False)
    d.marks("mottle", ellipse(90, 132, 3, 1.6) + ellipse(120, 130, 2.6, 1.4) + ellipse(146, 132, 3, 1.5)
            + ellipse(104, 138, 2, 1.2) + ellipse(160, 138, 2.4, 1.2) + ellipse(76, 136, 2, 1.1))
    d.shape("mark", ellipse(62, 133, 4, 1.6), shadow=False)
    d.band("near", waves(144, 4, 34))
    d.stroke("light", "M30 152 q8 -5 16 0 M100 156 q8 -5 16 0 M150 152 q8 -5 16 0 M64 166 q6 -4 12 0", 2.2)
    d.band("deep", waves(172, 4, 38), line=False)


# ================================================================ KING COBRA
COBRA = {"hero": "#4D4A27", "hero2": "#E6D488", "mark": "#1E1D10", "light": "#E9DDA8", "pop": "#D8433A"}
HOOD = ("M100 44 C120 44 136 60 136 80 C136 100 124 116 114 128 C112 140 112 150 114 160 L86 160 "
        "C88 150 88 140 86 128 C76 116 64 100 64 80 C64 60 80 44 100 44Z")


def cobra_hood(d: Drawing, spot=True):
    d.shape("hero", HOOD)
    d.shape("light", "M68 72 L76 76 M66 88 L76 90 M68 104 L78 104 M132 72 L124 76 M134 88 L124 90 M132 104 L122 104", shadow=False, line=False)
    d.stroke("light", "M69 70 L77 75 M66 86 L76 89 M68 102 L78 103 M131 70 L123 75 M134 86 L124 89 M132 102 L122 103", 2.4, line=False)
    d.shape("hero2", "M100 58 C112 58 120 70 120 86 C120 102 114 118 106 128 L94 128 C86 118 80 102 80 86 C80 70 88 58 100 58Z", spot=spot)
    d.marks("hero", "M82 104 L100 112 L118 104 L117 110 L100 118 L83 110Z M88 120 L100 125 L112 120 L110 126 L100 130 L90 126Z")
    d.shape("hero", "M100 28 C112 28 119 36 119 46 C119 56 110 62 100 62 C90 62 81 56 81 46 C81 36 88 28 100 28Z")
    d.stroke("mark", "M92 34 L100 38 L108 34 M100 38 V48 M92 48 Q100 52 108 48", 1.2, line=False)
    for x in (88, 112):
        d.shape("hero2", circle(x, 44, 3.4), shadow=False)
        d.marks("mark", circle(x, 44, 2))
    d.stroke("pop", "M100 62 L100 72 M100 72 L96 78 M100 72 L104 78", 1.8)


def kingcobra_hood(d: Drawing):
    foliage(d, [(-6, 46, 20), (-4, 100, -5), (4, 150, -30), (206, 46, 160), (204, 100, 185), (196, 150, -150)])
    d.band("ground", hills(176, 3))
    d.shape("hero", ellipse(100, 170, 62, 18))
    d.stroke("light", "M52 162 Q48 170 54 180 M70 156 Q66 168 70 184 M130 156 Q134 168 130 184 M148 162 Q152 170 146 180", 2.4)
    d.shape("hero", ellipse(98, 158, 46, 14))
    d.stroke("light", "M70 152 Q66 158 70 166 M126 152 Q130 158 126 166", 2.4)
    group(d, "translate(100 100) scale(1.12) translate(-100 -100)", lambda: cobra_hood(d))


def kingcobra_forest(d: Drawing):
    d.band("far", hills(120, 8))
    if d.paper:
        for x in (24, 40, 160, 178):
            d.limb("mid", f"M{x} 200 L{x + 2} -10", 6, shadow=False)
            d.stroke("far", f"M{x - 3} 60 H{x + 5} M{x - 3} 100 H{x + 5} M{x - 3} 140 H{x + 5} M{x - 3} 20 H{x + 5}", 1.6)
    foliage(d, [(30, 40, -20), (40, 70, 30), (170, 40, 200), (164, 74, 150)], "mid", 34, 7)
    d.band("ground", hills(160, 4))
    foliage(d, [(4, 180, -30), (196, 180, -150), (60, 186, -10), (150, 190, -170)], "near", 40, 10)
    body = "M8 176 C36 162 60 188 90 178 C112 170 104 150 100 124"
    ringed(d, body, 12, "hero", "light", "2 9")
    group(d, "translate(100 82) scale(.74) translate(-100 -100)", lambda: cobra_hood(d))


# ================================================================ ORANGUTAN
ORANG = {"hero": "#C4602A", "hero2": "#9C4A1E", "flange": "#5E4B40", "face": "#8A6E5C", "face2": "#A88C78",
         "mark": "#2A1E18", "light": "#F4E6D6"}


def orangutan_face(d: Drawing):
    d.shape("hero", tufty(100, 116, 82, 76, 30, 0.1))
    d.stroke("hero2", "M40 140 Q46 168 40 190 M56 150 Q62 176 58 196 M144 150 Q138 176 142 196 M160 140 Q154 168 160 190 "
                      "M80 166 Q84 182 80 198 M120 166 Q116 182 120 198", 2, line=False)
    d.shape("flange", ellipse(100, 94, 66, 44))
    d.shape("hero", tufty(100, 56, 30, 10, 12, 0.35), shadow=False)
    d.shape("flange", "M76 130 C76 152 88 164 100 164 C112 164 124 152 124 130Z")
    d.shape("face", "M100 60 C116 60 126 72 126 88 C126 106 118 124 100 128 C82 124 74 106 74 88 C74 72 84 60 100 60Z", spot=True)
    d.shape("face2", ellipse(100, 110, 18, 14), shadow=False)
    d.stroke("mark", "M82 80 Q91 74 98 80 M102 80 Q109 74 118 80", 1.8)
    for x in (91, 109):
        d.marks("light", circle(x, 86, 3.4))
        d.marks("mark", circle(x, 86, 2))
    d.marks("mark", ellipse(96, 104, 1.8, 2.4) + ellipse(104, 104, 1.8, 2.4))
    d.stroke("mark", "M88 116 Q100 122 112 116", 2)


def orangutan_canopy(d: Drawing):
    d.band("far", hills(150, 8))
    mist(d, 130, 4, 40)
    foliage(d, [(-6, 120, -20), (0, 170, -40), (206, 120, 200), (200, 170, -140), (100, 210, -90)], "near", 56, 14)
    d.limb("dark", "M-10 44 C50 38 130 42 210 34", 8)
    foliage(d, [(30, 40, -60), (60, 40, -110), (150, 38, -70), (176, 36, -120)], "mid", 26, 7)
    d.stroke("dark", "M156 38 C162 90 150 140 160 210", 3)
    group(d, "translate(100 100) scale(1.1) translate(-100 -100)", lambda: orangutan_hanging(d))


def orangutan_hanging(d: Drawing):
    # hanging from the branch by both very long arms, legs tucked up
    d.limb("hero", "M90 100 C84 78 78 60 74 40", 11)
    d.limb("hero", "M112 100 C118 78 124 60 128 40", 11)
    d.stroke("hero2", "M83 76 l-6 5 M79 62 l-6 5 M119 76 l6 5 M123 62 l6 5", 1.6, line=False)
    d.shape("face", ellipse(74, 40, 6, 5), shadow=False)
    d.shape("face", ellipse(128, 40, 6, 5), shadow=False)
    d.limb("hero", "M90 134 C76 144 76 158 88 164", 10)
    d.limb("hero", "M112 134 C126 144 126 158 114 164", 10)
    d.shape("face", ellipse(91, 165, 5, 4) + ellipse(111, 165, 5, 4), shadow=False)
    d.shape("hero", tufty(101, 116, 23, 27, 16, 0.16))
    d.shape("hero2", "M88 104 C92 96 108 96 112 104 C114 116 112 128 100 130 C88 128 86 116 88 104Z", shadow=False, line=False)
    # baby clinging on
    d.shape("hero", tufty(104, 120, 9, 9, 10, 0.2), shadow=False)
    d.shape("face", ellipse(104, 121, 4.6, 5), shadow=False)
    d.marks("mark", circle(102.4, 120, 0.9) + circle(105.6, 120, 0.9))
    # head
    d.shape("hero", tufty(96, 84, 15, 14, 12, 0.2))
    d.shape("face", "M96 74 C103 74 107 80 106 88 C105 95 101 99 96 99 C91 99 87 95 86 88 C85 80 89 74 96 74Z", spot=True)
    d.shape("face2", ellipse(96, 93, 7, 5), shadow=False)
    d.marks("light", circle(92, 84, 1.8) + circle(100, 84, 1.8))
    d.marks("mark", circle(92, 84, 1.1) + circle(100, 84, 1.1))
    d.stroke("mark", "M92 96 Q96 98 100 96", 1.2)


# ================================================================ PROBOSCIS MONKEY
PROB = {"hero": "#C7834A", "hero2": "#B5592C", "face": "#E7A988", "nose": "#E08A6E", "light": "#EFE3C8",
        "limbs": "#B6AEA2", "mark": "#2C1D14"}


def proboscis_face(d: Drawing):
    d.disc("glow", 100, 96, 66)
    foliage(d, [(0, 60, 10), (-4, 120, -20), (200, 60, 170), (204, 120, 200)], "near", 54, 14)
    d.shape("hero", "M30 210 C34 168 66 140 112 138 C156 138 180 168 182 210Z")
    d.shape("light", tufty(118, 140, 46, 22, 18, 0.18), shadow=False)
    d.shape("hero2", "M84 74 C86 54 104 42 124 44 C144 46 156 62 154 84 C152 104 140 118 126 124 L110 124 "
                     "C118 108 116 88 106 76 C98 70 90 70 84 74Z")
    d.shape("face", "M108 70 C96 64 84 70 80 80 C76 92 78 108 86 118 C94 126 108 128 118 122 C120 106 118 84 108 70Z")
    d.stroke("mark", "M88 78 Q96 74 104 78", 1.8)
    d.marks("mark", circle(97, 84, 2.4))
    d.marks("light", circle(97.8, 83.2, 0.8))
    d.stroke("mark", "M84 130 Q92 132 98 127", 2)
    d.shape("nose", "M88 80 C76 74 60 80 56 96 C52 112 54 130 64 136 C74 140 84 132 88 118 C90 106 90 94 88 80Z", spot=True)
    d.marks("mark", ellipse(66, 132, 2.4, 1.4))


def proboscis_river(d: Drawing):
    d.disc("glow", 46, 56, 18)
    d.band("far", hills(118, 6))
    for x in range(-10, 220, 16):
        d.shape("far", scallop(x, 114 - (x * 7 % 9), 10, 8, 0.16), shadow=False, line=False)
    d.band("mid", waves(130, 2, 34))
    d.stroke("light", "M30 140 q8 -4 16 0 M70 150 q8 -4 16 0 M140 146 q8 -4 16 0", 2)
    d.band("near", waves(158, 2, 36))
    d.stroke("light", "M20 168 q8 -4 16 0 M110 170 q8 -4 16 0", 2)
    d.band("deep", waves(180, 2, 36), line=False)
    # branch over the river
    d.limb("dark", "M214 66 C170 76 120 90 30 100", 8)
    foliage(d, [(196, 70, -70), (180, 70, -120), (160, 78, -60), (204, 74, 20)], "near", 28, 7, line=True)

    def monkey():
        d.limb("light", "M120 96 C126 112 128 132 122 156", 5)
        d.limb("limbs", "M102 96 C98 106 96 114 98 124", 8)
        d.limb("limbs", "M112 96 C110 106 108 114 110 124", 8)
        d.shape("hero", "M92 98 C84 84 86 64 100 56 C114 50 126 60 127 76 C128 88 124 96 116 99Z")
        d.shape("light", "M96 98 C94 90 98 82 108 82 C118 84 122 92 118 99Z", shadow=False)
        d.limb("limbs", "M96 70 C88 80 88 90 94 96", 6)
        d.shape("light", tufty(100, 56, 13, 7, 10, 0.25), shadow=False)
        d.shape("hero2", "M88 46 C88 36 98 30 106 32 C114 34 118 42 116 50 C114 56 108 58 104 56 C102 48 96 44 88 46Z")
        d.shape("face", "M102 40 C94 36 86 40 84 48 C84 56 90 60 98 60 C104 58 106 50 102 40Z")
        d.shape("nose", "M86 46 C80 44 74 48 74 54 C74 60 78 64 84 63 C88 62 90 58 90 52Z", spot=True)
        d.marks("mark", circle(95, 45, 1.6))
    group(d, "translate(102 98) scale(1.12) translate(-104 -98)", monkey)


# ================================================================ GIANT PANDA
PANDA = {"light": "#F8F6F0", "dark": "#1F1F25", "mark": "#111114", "bamboo": "#7FAE4B", "bamboo2": "#4E7D31", "pop": "#E58C9A"}


def bamboo_stalk(d: Drawing, x, y0, y1, w=7, role="bamboo2", line=True, shadow=True):
    d.limb(role, f"M{x} {y0} L{x} {y1}", w, shadow=shadow) if (line or d.paper) else None
    if d.paper:
        d.stroke("bamboo", " ".join(f"M{x - w / 2 + 0.5} {y} H{x + w / 2 - 0.5}" for y in range(int(y1) + 20, int(y0), 26)), 1.6)


def panda_face(d: Drawing, cx=100, cy=96, s=1.0):
    def draw():
        for ex in (56, 144):
            ink(d, "dark", circle(ex, 50, 18))
        d.shape("light", "M100 44 C134 44 154 66 154 96 C154 126 130 146 100 146 C70 146 46 126 46 96 C46 66 66 44 100 44Z")
        ink(d, "dark", ellipse(76, 96, 12, 17) .replace("Z", "Z"), shadow=False) if False else None
        ink(d, "dark", "M64 104 C58 96 62 80 74 78 C86 76 92 88 88 98 C84 108 72 114 64 104Z", shadow=False)
        ink(d, "dark", "M136 104 C142 96 138 80 126 78 C114 76 108 88 112 98 C116 108 128 114 136 104Z", shadow=False)
        for x in (78, 122):
            d.shape("light", circle(x, 92, 4.4), shadow=False)
            d.marks("mark", circle(x, 92, 2.6))
            d.marks("light", circle(x + 1, 91, 0.9))
        d.marks("mark", "M91 112 C91 107 109 107 109 112 C109 118 103 121 100 121 C97 121 91 118 91 112Z")
        d.stroke("mark", "M100 121 V127 M100 127 Q94 133 88 129 M100 127 Q106 133 112 129", 2)
    group(d, f"translate({cx} {cy}) scale({s}) translate(-100 -96)", draw)


def giantpanda_face(d: Drawing):
    d.shape("far", circle(100, 100, 76), line=False)
    for x in (16, 32, 170, 186):
        bamboo_stalk(d, x, 210, -10, 7, line=False)
    foliage(d, [(16, 70, -150), (32, 54, -30), (186, 66, -30), (170, 50, -150), (16, 120, -160), (186, 118, -20)], "bamboo", 30, 6)
    d.shape("dark", "M24 210 C26 170 52 146 100 144 C148 146 174 170 176 210Z")
    d.shape("light", "M72 210 C72 178 84 162 100 160 C116 162 128 178 128 210Z", shadow=False)
    panda_face(d, 100, 92, 1.0)
    # a bamboo stalk to munch
    d.limb("bamboo", "M54 200 L146 118", 7, spot=True)
    d.stroke("bamboo2", "M86 175 L92 169 M116 147 L122 141", 2, line=False)
    for x, y, a in [(146, 118, -40), (146, 118, -80), (146, 118, 0), (140, 124, -120)]:
        d.shape("bamboo", leaf(x, y, 28, 6, a), shadow=False)
    ink(d, "dark", ellipse(76, 172, 14, 10))
    ink(d, "dark", ellipse(126, 148, 13, 10))


def giantpanda_grove(d: Drawing):
    d.band("far", "M-30 112 L14 80 L40 96 L74 58 L106 92 L136 66 L168 90 L196 74 L230 96")
    mist(d, 100, 4, 40, ".6")
    d.band("mid", hills(126, 6))
    for x, top in [(14, 30), (30, 10), (172, 20), (188, 40)]:
        bamboo_stalk(d, x, 200, top, 7)
    foliage(d, [(30, 30, -40), (30, 30, -140), (14, 50, -160), (172, 40, -30), (188, 60, -40), (172, 40, -150)], "bamboo", 26, 6)
    d.band("ground", hills(170, 3))
    ink(d, "dark", ellipse(70, 168, 18, 12))
    ink(d, "dark", ellipse(130, 168, 18, 12))
    d.shape("light", "M64 168 C56 140 66 108 100 104 C134 108 144 140 136 168Z")
    ink(d, "dark", "M64 130 C68 112 82 102 100 102 C118 102 132 112 136 130 C124 122 112 120 100 120 C88 120 76 122 64 130Z", shadow=False)
    d.limb("bamboo", "M88 164 L130 62", 4.5, spot=True)
    for x, y, a in [(130, 62, -50), (130, 62, -100), (127, 70, -10)]:
        d.shape("bamboo", leaf(x, y, 22, 5, a), shadow=False)
    d.limb("dark", "M70 128 C62 146 76 152 98 142", 15)
    d.limb("dark", "M130 128 C140 146 128 152 110 132", 15)
    panda_face(d, 100, 80, 0.46)
    d.marks("pop", ellipse(66, 166, 4, 3) + ellipse(134, 166, 4, 3)) if d.paper else None
    d.band("deep", hills(188, 3, 30), line=False)


# ================================================================ RED PANDA
REDPANDA = {"hero": "#C4532A", "hero2": "#7E3418", "light": "#FBF3E8", "mark": "#1E1512", "ring": "#E4A06A", "dark": "#2E1A12",
            "pop": "#E25C7C"}
RP_EAR = "M50 74 C44 54 52 38 66 34 C74 44 78 58 76 68Z"


def redpanda_head(d: Drawing):
    for side in (False, True):
        def ear():
            d.shape("hero", RP_EAR)
            d.shape("hero2", "M56 66 C52 54 56 44 64 41 C69 48 71 58 70 64Z", shadow=False, line=False)
            d.stroke("light", "M50 72 C44 54 52 38 66 34", 3)
        flip(d, ear) if side else ear()
    d.shape("hero", "M100 50 C130 50 152 66 154 92 C156 116 136 136 100 136 C64 136 44 116 46 92 C48 66 70 50 100 50Z")
    d.shape("light", ellipse(64, 106, 13, 10), shadow=False)
    d.shape("light", ellipse(136, 106, 13, 10), shadow=False)
    d.shape("light", ellipse(80, 74, 7, 5), shadow=False)
    d.shape("light", ellipse(120, 74, 7, 5), shadow=False)
    d.shape("light", "M100 100 C112 100 126 106 128 118 C130 130 116 136 100 136 C84 136 70 130 72 118 C74 106 88 100 100 100Z", shadow=False)
    d.stroke("hero2", "M82 92 Q78 104 82 116 M118 92 Q122 104 118 116", 3.4, line=False)
    for x in (82, 118):
        d.marks("mark", circle(x, 90, 5))
        d.marks("light", circle(x + 1.6, 88.4, 1.4))
    d.marks("mark", "M92 112 C92 108 108 108 108 112 C108 117 103 120 100 120 C97 120 92 117 92 112Z")
    d.stroke("mark", "M100 120 V125 M100 125 Q95 130 90 127 M100 125 Q105 130 110 127", 1.8)


def redpanda_face(d: Drawing):
    foliage(d, [(-6, 50, 15), (-4, 104, -5), (206, 50, 165), (204, 104, 185)], "near", 56, 14)
    for x, y in [(20, 60), (182, 66), (14, 112)]:
        d.shape("pop", scallop(x, y, 7, 6, 0.3), shadow=False)
    d.shape("dark", "M56 210 C58 168 78 144 100 144 C122 144 142 168 144 210Z")
    ringed(d, "M30 168 C50 196 130 200 160 176 C178 160 176 138 160 132", 24, "hero", "ring", "9 9", spot=True)
    redpanda_head(d)


def redpanda_tree(d: Drawing):
    d.disc("glow", 150, 50, 16)
    for x, h in [(20, 60), (40, 44), (168, 52), (188, 66)]:
        d.shape("far", f"M{x} {150 - h} L{x + 14} 150 L{x - 14} 150Z", line=False)
    mist(d, 132, 4, 40)
    d.band("mid", hills(160, 5))
    d.limb("dark", "M-10 116 C50 106 140 112 210 100", 10)
    d.limb("dark", "M150 108 L176 80", 5)
    foliage(d, [(176, 80, -60), (176, 80, -10), (168, 88, -120)], "near", 24, 7)
    for x, y in [(184, 76), (164, 84)]:
        d.shape("pop", scallop(x, y, 5, 6, 0.3), shadow=False)

    def rp():
        ringed(d, "M128 102 C148 110 156 130 150 154 C148 164 140 170 132 168", 13, "hero", "ring", "6 6", spot=True)
        d.limb("dark", "M90 104 L86 114 M100 106 L100 114 M118 106 L120 114 M126 104 L130 113", 6)
        d.shape("hero", "M78 102 C78 90 90 82 106 82 C122 82 134 88 134 100 C134 108 128 110 120 110 L88 110 C82 110 78 108 78 102Z")
        d.shape("dark", "M82 106 C94 110 116 110 130 106 C124 112 94 113 84 110Z", shadow=False, line=False)
        group(d, "translate(72 86) scale(.38) translate(-100 -92)", lambda: redpanda_head(d))
    group(d, "translate(100 112) scale(1.12) translate(-100 -112)", rp)


# ================================================================ KOMODO DRAGON
KOMODO = {"hero": "#6E6553", "hero2": "#8C826C", "mark": "#2C281F", "pop": "#F0C23A", "light": "#C9BFA6"}
KOMODO_HEAD = ("M210 92 C178 82 146 78 112 80 C88 82 62 88 42 96 C30 101 26 108 30 114 C34 120 46 122 62 122 "
               "C86 124 110 128 130 136 C150 144 172 158 210 172Z")


def komodo_face(d: Drawing):
    d.disc("glow", 60, 60, 26)
    d.band("far", "M-30 120 L20 100 L50 108 L80 84 L110 100 L230 96")
    d.band("mid", hills(150, 6))
    d.limb("hero", "M156 146 C152 166 144 178 130 184", 14)
    d.stroke("light", "M130 184 l-8 -1 M131 186 l-7 4 M134 186 l-3 6", 2)
    d.shape("pop", "M32 111 L18 111 L8 103 L15 112.5 L8 122 L18 115 L32 115Z", spot=True)
    d.shape("hero", KOMODO_HEAD)
    d.shape("hero2", "M60 122 C80 130 104 136 126 140 C112 152 84 150 64 136Z", shadow=False)
    d.stroke("mark", "M30 113 C50 116 78 116 104 114 C114 114 120 112 126 106", 2)
    d.stroke("mark", "M140 88 C148 106 150 124 146 140 M158 90 C164 108 166 128 162 148 M176 92 C180 112 182 132 178 154", 2, line=False)
    d.shape("hero", "M84 84 C88 76 100 74 108 80 C104 82 96 84 88 88Z", shadow=False)
    d.marks("light", circle(96, 91, 4.4))
    d.marks("mark", circle(96, 91, 2.6))
    d.marks("mark", ellipse(38, 104, 2, 1.4))
    sc = "".join(circle(x, y, 1.4) for x in range(48, 200, 9) for y in range(86, 170, 8) if (x + y) % 2 == 0)
    clipped(d, KOMODO_HEAD, lambda: d.marks("hero2", sc)) if d.paper else None


def komodo_island(d: Drawing):
    d.disc("glow", 150, 52, 22)
    d.band("far", "M-30 112 L10 90 L34 100 L64 74 L96 98 L124 86 L150 104 L230 100")
    d.stroke("mid", "M64 74 L58 98 M64 74 L74 96 M10 90 L16 104", 1.6, line=False)
    palm(d, 176, 140, 58, -6, "dark", 0.8)
    d.band("mid", hills(130, 4, 30))
    d.band("ground", hills(152, 3))
    p = ((206, 148), (150, 150), (116, 110), (44, 106))

    def prof(t):
        if t < 0.72:
            w = math.sin(math.pi * t ** 0.65)
        else:
            w = math.sin(math.pi * 0.72 ** 0.65) * (1 - ((t - 0.72) / 0.28) ** 3) * (1 - 0.25 * math.sin(math.pi * (t - 0.72) / 0.14) if t < 0.86 else 1)
        return 1.5 + 17 * w, 1.5 + 12 * w

    for t, dx in [(0.44, 12), (0.76, 10)]:
        x, y = frame(p, t, -4)
        d.limb("hero2", f"M{x:.1f} {y:.1f} L{x + dx:.1f} {y + 12:.1f} L{x + dx - 2:.1f} 152", 8)
    d.shape("hero", spine(p, prof))
    for t, dx in [(0.48, -10), (0.8, -12)]:
        x, y = frame(p, t, -8)
        d.limb("hero", f"M{x:.1f} {y:.1f} L{x + dx:.1f} {y + 10:.1f} L{x + dx - 4:.1f} 154", 9)
        d.stroke("light", f"M{x + dx - 6:.1f} 156 l-6 0 M{x + dx - 5:.1f} 157 l-4 4", 1.6)
    tip = frame(p, 1.0, -2, 2)
    d.shape("pop", f"M{tip[0]:.1f} {tip[1]:.1f} L{tip[0] - 10:.1f} {tip[1] - 1:.1f} L{tip[0] - 15:.1f} {tip[1] - 6:.1f} "
                   f"L{tip[0] - 12:.1f} {tip[1]:.1f} L{tip[0] - 15:.1f} {tip[1] + 5:.1f} L{tip[0] - 10:.1f} {tip[1] + 2:.1f} L{tip[0]:.1f} {tip[1] + 2:.1f}Z",
            shadow=False, spot=True)
    e = frame(p, 0.93, 4)
    d.marks("mark", circle(e[0], e[1], 1.6))
    a, b = frame(p, 0.86, -1), frame(p, 0.995, -1)
    d.stroke("mark", f"M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f}", 1.3)
    d.band("deep", hills(180, 3, 30), line=False)
    grass(d, 10, 70, 182, 10, "near")


# ================================================================ HORNBILL
HORNBILL = {"hero": "#F2C232", "hero2": "#E07A2E", "dark": "#1B1C22", "light": "#FFF3D2", "pop": "#D8342A", "mark": "#111111"}


def hornbill_face(d: Drawing):
    d.disc("glow", 150, 56, 24)
    foliage(d, [(-6, 150, -30), (4, 176, -60), (40, 206, -80), (204, 150, -150), (196, 176, -120)], "near", 60, 15)
    foliage(d, [(-6, 40, 20), (206, 40, 160)], "mid", 50, 12)
    d.shape("light", "M118 104 C132 108 144 126 148 150 C150 170 148 190 144 210 L96 210 C100 180 104 150 104 120Z")
    d.shape("dark", "M118 168 C140 154 172 160 190 182 L200 210 L108 210Z")
    d.shape("dark", "M106 76 C120 66 140 70 146 86 C150 102 140 116 124 116 C112 116 102 108 102 96Z")
    d.shape("hero", "M108 78 C96 64 74 62 54 70 C46 74 44 84 48 92 C66 86 88 86 108 92Z", spot=True)
    d.shape("dark", "M54 70 C46 74 44 84 48 92 L54 90 C52 84 52 76 58 69Z", shadow=False)
    d.shape("hero", "M108 86 C80 82 50 90 22 118 C20 121 22 123 25 121 C52 106 80 100 108 102Z")
    d.shape("hero", "M108 102 C82 102 56 110 30 122 C56 117 84 114 108 112Z")
    d.shape("hero2", "M30 114 C26 117 22 120 22 120 C21 122 23 123 25 121 C30 118 36 116 40 114Z", shadow=False)
    d.stroke("dark", "M108 102 C82 102 56 110 30 121", 1.4)
    d.shape("light", circle(126, 90, 6), shadow=False)
    d.marks("pop", circle(126, 90, 4))
    d.marks("mark", circle(126, 90, 2))


def hornbill_flight(d: Drawing):
    d.disc("glow", 50, 56, 18)
    d.band("far", hills(146, 6))
    for x in range(-10, 220, 20):
        d.shape("far", scallop(x, 144 - (x * 7 % 9), 13, 8, 0.16), shadow=False, line=False)
    mist(d, 150, 3, 40)
    d.band("mid", hills(166, 4))
    for x in range(0, 220, 26):
        d.shape("mid", scallop(x, 164 - (x * 5 % 7), 15, 8, 0.16), shadow=False, line=False)
    d.band("near", hills(184, 4, 30))

    def bird():
        d.shape("dark", "M108 104 C104 122 110 138 124 148 L128 140 L132 146 L134 136 C130 124 130 112 132 104Z")
        d.shape("light", "M138 96 L180 90 L182 108 L138 106Z")
        d.shape("dark", "M162 92 L170 91 L171 107 L163 107Z", shadow=False)
        d.shape("dark", "M86 96 C96 88 126 88 142 96 C140 106 120 110 96 108 C88 106 84 100 86 96Z")
        d.shape("dark", "M98 96 C92 72 100 46 118 30 L124 34 L128 28 L132 34 L138 30 L138 40 C134 58 130 78 126 96Z")
        d.shape("light", "M104 72 C108 58 116 48 126 42 L131 47 C122 54 115 64 111 76Z", shadow=False, spot=True)
        d.shape("light", "M74 96 C80 90 90 90 96 94 L96 106 C88 108 80 106 74 102Z")
        d.shape("dark", ellipse(66, 98, 9, 8))
        d.shape("hero", "M62 92 C52 84 38 84 28 90 C32 92 44 92 58 96Z")
        d.shape("hero", "M60 96 C46 96 30 102 18 112 C30 108 46 104 62 104Z")
        d.marks("pop", circle(68, 96, 1.6))
    group(d, "translate(100 96) scale(1.04) translate(-100 -96)", bird)


# ================================================================ SNOW LEOPARD
SNOWLEO = {"hero": "#D9D7CF", "hero2": "#A9C3A0", "mark": "#3F3F46", "light": "#FAF9F5", "pop": "#C9A0A0", "rock": "#8E8C88",
           "rock2": "#6E6C69"}
SNOW_HEAD = ("M100 52 C126 52 146 64 150 86 C156 100 156 116 148 130 C138 148 120 158 100 158 "
             "C80 158 62 148 52 130 C44 116 44 100 50 86 C54 64 74 52 100 52Z")


def snowleopard_face(d: Drawing):
    d.band("near", "M-30 120 L20 82 L48 98 L100 26 L152 92 L178 72 L230 100")
    for s in ["M100 26 L114 46 L106 43 L100 50 L93 43 L86 46Z", "M20 82 L30 92 L24 91 L19 96 L13 90Z", "M178 72 L188 82 L182 81 L177 86 L171 81Z"]:
        d.shape("light", s, shadow=False)
    d.band("deep", hills(160, 6))
    d.shape("hero", "M50 210 C54 168 76 148 100 148 C124 148 146 168 150 210Z")
    for cx in (66, 134):
        d.shape("hero", circle(cx, 62, 9))
        d.shape("pop", circle(cx, 63, 4), shadow=False)
    d.shape("hero", SNOW_HEAD)
    spots = [(100, 62, 2.4), (90, 66, 2), (110, 66, 2), (82, 72, 2), (118, 72, 2), (100, 74, 1.8), (92, 78, 1.6), (108, 78, 1.6)]
    d.marks("mark", "".join(circle(x, y, r) for x, y, r in spots))
    ros = "".join(rosette(x, y, r) for x, y, r in [(56, 104, 5), (144, 104, 5), (62, 126, 5), (138, 126, 5), (54, 86, 4), (146, 86, 4)])
    clipped(d, SNOW_HEAD, lambda: d.marks("mark", ros))
    d.shape("light", "M100 106 C112 106 128 112 130 126 C130 142 116 150 100 150 C84 150 70 142 70 126 C72 112 88 106 100 106Z", shadow=False)
    for x in (80, 120):
        d.shape("light", ellipse(x, 92, 11, 8), shadow=False)
        eye(d, x, 93, 6, iris="hero2")
    d.shape("pop", "M91 112 H109 L100 123Z", shadow=False)
    d.stroke("mark", "M100 123 V129 M100 129 Q92 136 86 131 M100 129 Q108 136 114 131", 2)
    tail = "M20 160 C44 186 140 190 172 164 C184 152 182 138 170 134"
    d.limb("hero", tail, 24, spot=True)
    d.marks("mark", "".join(rosette(x, y, 4.6) for x, y in [(40, 176), (66, 184), (94, 186), (122, 182), (148, 172), (172, 154)]))


def snowleopard_ledge(d: Drawing):
    d.disc("glow", 160, 46, 14)
    d.band("near", "M-30 124 L20 92 L44 108 L84 50 L118 90 L152 58 L190 84 L230 70")
    for s in ["M84 50 L96 66 L89 64 L84 70 L78 64 L72 68Z", "M152 58 L162 72 L156 70 L151 76 L146 70 L142 73Z", "M20 92 L28 102 L22 100 L18 104 L13 99Z"]:
        d.shape("light", s, shadow=False)
    mist(d, 128, 3, 40, ".5")
    d.band("deep", "M-30 150 L40 136 L80 146 L130 130 L230 144")
    d.shape("rock", "M230 200 L230 134 L150 128 L72 130 C62 132 58 138 62 146 L70 152 L110 156 L118 200Z")
    d.shape("rock2", "M62 146 L70 152 L110 156 L118 200 L230 200 L230 168 L120 162Z", shadow=False)
    flip(d, lambda: group(d, "translate(-30 2)", lambda: cat_lying(
        d, "M150 116 C168 120 174 140 168 162 C164 174 170 182 178 180", tail_w=10, spots="snow", ear_r=4.6)))
    d.band("deep", hills(192, 3, 30), line=False)


# ================================================================ MACAQUE
MACAQUE = {"hero": "#B9AA94", "hero2": "#8F8170", "face": "#E0705E", "face2": "#C9524A", "mark": "#2A1E1A", "light": "#FFFFFF",
           "water": "#3E8BA0", "water2": "#A9DCE4", "rock": "#7D7A76"}


def macaque_head(d: Drawing, sleepy=False, snow=True):
    d.shape("hero", tufty(100, 98, 50, 46, 26, 0.13))
    d.shape("face", "M100 70 C116 70 126 82 126 98 C126 114 116 128 100 130 C84 128 74 114 74 98 C74 82 84 70 100 70Z", spot=True)
    d.shape("face2", "M78 92 C84 84 96 86 100 90 C104 86 116 84 122 92 C116 90 108 92 100 96 C92 92 84 90 78 92Z", shadow=False, line=False)
    if sleepy:
        d.stroke("mark", "M84 100 Q90 104 96 100 M104 100 Q110 104 116 100", 2.2)
    else:
        for x in (90, 110):
            d.marks("mark", circle(x, 100, 3))
            d.marks("light", circle(x + 1, 99, 1))
    d.marks("mark", ellipse(96, 114, 1.8, 1.2) + ellipse(104, 114, 1.8, 1.2))
    d.stroke("mark", "M92 121 Q100 125 108 121", 1.8)
    if snow:
        d.shape("light", "M64 70 C66 54 84 46 100 46 C116 46 134 54 136 70 C126 64 112 62 100 64 C88 62 74 64 64 70Z", shadow=False)


def macaque_face(d: Drawing):
    d.band("far", hills(150, 8))
    for x in (12, 30, 172, 190):
        d.shape("near", f"M{x} 60 L{x + 16} 150 L{x - 16} 150Z", line=False)
        d.shape("light", f"M{x} 60 L{x + 6} 86 L{x} 82 L{x - 6} 86Z", shadow=False, line=False)
    d.band("light", hills(166, 4, 30))
    d.shape("hero", tufty(100, 190, 66, 50, 24, 0.12))
    d.shape("light", "M50 156 C64 146 80 146 90 152 C78 150 64 152 50 160Z M150 156 C136 146 120 146 110 152 C122 150 136 152 150 160Z", shadow=False)
    macaque_head(d)
    flakes = [(30, 40), (52, 28), (150, 30), (172, 46), (24, 90), (178, 92), (44, 120), (160, 124), (70, 20), (130, 22)]
    d.marks("light", "".join(circle(x, y, 2.4) for x, y in flakes))


def macaque_onsen(d: Drawing):
    d.band("far", hills(108, 8))
    for x, h in [(16, 50), (34, 36), (164, 40), (184, 54)]:
        d.shape("near", f"M{x} {112 - h} L{x + 14} 112 L{x - 14} 112Z", line=False)
        d.shape("light", f"M{x} {112 - h} L{x + 5} {112 - h + 16} L{x} {112 - h + 12} L{x - 5} {112 - h + 16}Z", shadow=False, line=False)
    d.band("light", hills(118, 4, 30))
    d.shape("water", "M-30 132 C40 126 160 126 230 132 V230 H-30Z")
    d.stroke("water2", "M24 150 q8 -4 16 0 M150 150 q8 -4 16 0 M40 176 q8 -4 16 0 M140 178 q8 -4 16 0", 2.2)
    # rocks round the pool, capped with snow
    for path, cap in [("M-30 130 C-10 112 20 110 44 120 C50 128 46 136 36 140 L-30 142Z", "M-10 118 C8 110 30 112 42 120 C30 118 14 118 -4 124Z"),
                      ("M156 120 C176 108 210 112 230 124 L230 142 L164 140 C152 136 150 126 156 120Z", "M160 118 C176 110 204 112 222 120 C204 118 180 116 162 124Z")]:
        d.shape("rock", path)
        d.shape("light", cap, shadow=False)
    # steam
    d.raw('<g opacity=".7">', "")
    d.stroke("light", "M40 128 C34 116 46 108 40 96 M160 126 C154 114 166 106 160 94 M60 140 C54 128 66 120 60 108", 3, line=False)
    d.raw("</g>", "")
    group(d, "translate(100 128) scale(.78) translate(-100 -110)", lambda: (
        d.shape("hero", tufty(100, 150, 46, 22, 20, 0.12)),
        macaque_head(d, sleepy=True),
    ))
    d.shape("water", "M-30 150 C40 144 160 144 230 150 V230 H-30Z")
    d.stroke("water2", "M64 150 q10 -5 20 0 M110 150 q10 -5 20 0 M30 170 q8 -4 16 0 M150 172 q8 -4 16 0", 2.2)
    d.shape("rock", "M-30 186 C20 172 60 178 80 196 L80 230 H-30Z M120 200 C140 178 190 174 230 184 V230 H120Z")
    d.shape("light", "M-20 182 C10 174 50 176 70 188 C50 182 20 180 -20 188Z M130 192 C150 182 190 178 220 184 C190 184 160 186 132 196Z", shadow=False)


# ================================================================ CLOUDED LEOPARD
CLOUDED = {"hero": "#C9AE7C", "hero2": "#957B52", "mark": "#2C241B", "light": "#F4EAD6", "pop": "#C98078", "eye1": "#D9B83A"}


def clouds_on(d: Drawing, spots):
    outer, inner = "", ""
    for x, y, s, r in spots:
        o, i = cloudspot(x, y, s, r)
        outer += o
        inner += i
    d.marks("mark", outer)
    d.marks("hero2", inner) if d.paper else None


def cloudedleopard_face(d: Drawing):
    foliage(d, [(-6, 46, 20), (-4, 100, -5), (4, 150, -30), (206, 46, 160), (204, 100, 185), (196, 150, -150)], "near")
    body = "M40 210 C44 166 70 146 100 146 C130 146 156 166 160 210Z"
    d.shape("hero", body)
    clipped(d, body, lambda: clouds_on(d, [(66, 166, 8, 0.3), (100, 174, 9, 0), (134, 166, 8, -0.3), (80, 194, 8, 0.2), (120, 194, 8, 0)]))
    for cx in (67, 133):
        d.shape("hero", circle(cx, 58, 9))
        d.shape("light", circle(cx, 60, 4), shadow=False)
    head = "M100 48 C124 48 142 60 146 82 C152 96 150 116 142 130 C132 148 116 158 100 158 C84 158 68 148 58 130 C50 116 48 96 54 82 C58 60 76 48 100 48Z"
    d.shape("hero", head)
    d.marks("mark", "M94 52 L96 70 L100 52Z M104 52 L106 70 L108 54Z M84 56 L88 72 L90 56Z M116 56 L112 72 L110 56Z"
                    + "".join(circle(x, y, 1.6) for x, y in [(90, 76), (110, 76), (100, 78), (86, 66), (114, 66)]))
    d.stroke("mark", "M70 98 C62 104 58 114 58 124 M74 106 C68 114 66 122 68 132 M130 98 C138 104 142 114 142 124 M126 106 C132 114 134 122 132 132", 2.6)
    d.shape("light", "M100 104 C112 104 126 110 128 124 C128 140 114 150 100 150 C86 150 72 140 72 124 C74 110 88 104 100 104Z", shadow=False)
    for x in (82, 118):
        d.shape("light", ellipse(x, 90, 10, 7), shadow=False)
        eye(d, x, 91, 5.6, iris="eye1", slit=True)
    d.shape("pop", "M92 110 H108 L100 120Z", shadow=False)
    d.stroke("mark", "M100 120 V126", 2)
    # mouth open a little: the longest canines of any cat, for its size
    d.marks("mark", "M86 128 C92 126 108 126 114 128 C112 136 106 140 100 140 C94 140 88 136 86 128Z")
    d.shape("light", "M90 128 L93 142 L96 128Z M104 128 L107 142 L110 128Z", shadow=False)


def cloudedleopard_tree(d: Drawing):
    d.band("far", hills(160, 8))
    mist(d, 150, 4, 40)
    foliage(d, [(-6, 40, 20), (0, 90, -10), (206, 150, 200), (196, 180, -140), (10, 180, -40)], "near", 60, 15)
    foliage(d, [(206, 40, 160), (200, 90, 190)], "mid", 56, 14)

    def scene():
        d.limb("dark", "M-40 152 L240 152", 14)
        cat_walk(d, lambda p: clipped(d, p, lambda: clouds_on(d, [(84, 98, 7, 0.2), (104, 94, 8, -0.2), (126, 96, 8, 0.1),
                                                                     (146, 100, 7, 0.3), (96, 114, 6, 0), (118, 114, 6, 0.4), (140, 114, 6, 0)])),
                 "M160 100 C178 110 184 136 178 164 C176 178 182 188 190 186", tail_w=10, foot=145,
                 head_marks="M58 74 L56 84 L61 80Z M68 76 L64 88 L70 84Z M56 104 L70 100 L60 108Z M52 98 L64 92 L54 100Z",
                 tail_ring="mark")
    group(d, "translate(100 100) rotate(-22) scale(.95) translate(-100 -110)", scene)


# ================================================================ concepts
ALL = ["golden", "coastal", "meadow", "blush", "dusk"]
WET = ["coastal", "meadow", "blush", "dusk"]
UNDERWATER = ["coastal", "dusk", "meadow"]
SKY_FIX = ["sky2", "far", "glow"]

CONCEPTS = [
    # Sri Lanka & India
    Concept("slothbear-portrait", "animal-sloth-bear", "Sloth bear", slothbear_face, overrides=SLOTH,
            checks=[("hero", "sky"), ("hero", "near"), ("hero2", "hero")], fixes={"sky": SKY_FIX, "near": ["mid", "far"]}),
    Concept("slothbear-yala", "animal-sloth-bear", "Sloth bear at Yala", slothbear_yala, overrides={**SLOTH, "ground": "#C2703F"},
            checks=[("hero", "sky"), ("hero", "mid"), ("hero", "ground"), ("hero", "glow")], fixes={"sky": SKY_FIX, "mid": ["far", "near"]}),
    Concept("asianelephant-portrait", "animal-asian-elephant", "Asian elephant", asianelephant_face, overrides=ELE,
            checks=[("hero", "glow"), ("hero2", "glow"), ("hero2", "sky")], fixes={"glow": ["glow2", "far", "light", "sky2"]}),
    Concept("asianelephant-tank", "animal-asian-elephant", "Elephants at the tank", asianelephant_tank, WET, overrides=ELE,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "mid"), ("hero", "glow")], fixes={"far": ["mid", "near"], "mid": ["near", "far"]}),
    Concept("srileopard-portrait", "animal-sri-lankan-leopard", "Sri Lankan leopard", srileopard_face, overrides=LEO,
            checks=[("hero", "sky"), ("hero", "mid"), ("hero", "near")], fixes={"near": ["deep", "dark"], "mid": ["far", "near", "deep"]}),
    Concept("srileopard-rock", "animal-sri-lankan-leopard", "Leopard on the rock", srileopard_rock,
            overrides={**LEO, "rock": "#8F8880", "rock2": "#6F6962"},
            checks=[("hero", "sky"), ("hero", "glow"), ("rock", "far")], fixes={"glow": ["glow2", "#E07A5F", "near"], "sky": SKY_FIX}),
    Concept("bengaltiger-portrait", "animal-bengal-tiger", "Bengal tiger", bengaltiger_stride, overrides=TIGER,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero", "ground")], fixes={"glow": ["glow2", "light", "far", "sky2"], "ground": ["near", "deep"]}),
    Concept("bengaltiger-ranthambore", "animal-bengal-tiger", "Tiger at Ranthambore", bengaltiger_grass, overrides=TIGER,
            checks=[("hero", "near"), ("hero", "mid"), ("hero", "deep")], fixes={"near": ["deep", "mid"], "mid": ["far", "near"]}),
    Concept("peacock-display", "animal-peacock", "Peacock display", peacock_display, overrides=PEACOCK,
            checks=[("train", "sky"), ("hero", "train")], fixes={"sky": SKY_FIX}),
    Concept("peacock-yala", "animal-peacock", "Peacock in the scrub", peacock_yala, overrides=PEACOCK,
            checks=[("hero", "sky"), ("train", "mid"), ("train", "ground"), ("hero", "glow")], fixes={"mid": ["far", "near"], "ground": ["far", "light"]}),
    Concept("langur-portrait", "animal-langur-monkey", "Grey langur", langur_face, overrides=LANGUR,
            checks=[("hero", "sky"), ("hero", "mid")], fixes={"sky": ["far", "mid", "sky2"], "mid": ["near", "deep"]}),
    Concept("langur-ruins", "animal-langur-monkey", "Langur at the ruins", langur_ruins,
            overrides={**LANGUR, "rock": "#9C8A72", "rock2": "#7C6A54", "stupa": "#EFE9DC"},
            checks=[("hero", "sky"), ("stupa", "far"), ("hero", "rock")], fixes={"sky": ["far", "sky2", "mid"], "far": ["mid", "near"]}),
    Concept("indianrhino-portrait", "animal-indian-rhino", "Indian rhino", indianrhino_side, overrides=RHINO,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero", "ground")], fixes={"glow": ["glow2", "far", "light"], "ground": ["near", "deep"]}),
    Concept("indianrhino-kaziranga", "animal-indian-rhino", "Rhino at Kaziranga", indianrhino_kaziranga, WET, overrides=RHINO,
            checks=[("hero", "near"), ("hero", "mid"), ("light", "hero")], fixes={"near": ["deep", "mid"], "mid": ["far", "near"]}),
    Concept("waterbuffalo-portrait", "animal-water-buffalo", "Water buffalo", waterbuffalo_face, overrides=BUFFALO,
            checks=[("hero", "glow"), ("horn", "sky"), ("hero", "mid"), ("horn", "glow")], fixes={"sky": SKY_FIX, "glow": ["glow2", "light"]}),
    Concept("waterbuffalo-wallow", "animal-water-buffalo", "Buffalo wallow", waterbuffalo_paddy, WET, overrides=BUFFALO,
            checks=[("hero", "mid"), ("hero", "near"), ("horn", "sky")], fixes={"mid": ["far", "sky2"], "near": ["mid", "far"]}),
    Concept("bluewhale-portrait", "animal-blue-whale", "Blue whale", bluewhale_side, UNDERWATER, overrides=BLUEWHALE,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "far")], fixes={"far": ["sky2", "light"], "mid": ["far", "sky2"], "near": ["deep"]}),
    Concept("bluewhale-mirissa", "animal-blue-whale", "Blue whale off Mirissa", bluewhale_mirissa, WET, overrides=BLUEWHALE,
            checks=[("hero", "mid"), ("hero", "near"), ("light", "sky")], fixes={"sky": ["sky2", "far"], "mid": ["far"], "near": ["deep"]}),
    Concept("kingcobra-portrait", "animal-king-cobra", "King cobra", kingcobra_hood, overrides=COBRA,
            checks=[("hero", "sky"), ("hero", "near"), ("hero", "ground")], fixes={"near": ["mid", "far"], "ground": ["far", "light"]}),
    Concept("kingcobra-forest", "animal-king-cobra", "Cobra in the forest", kingcobra_forest, overrides=COBRA,
            checks=[("hero", "sky"), ("hero", "ground"), ("hero", "far"), ("hero", "mid")], fixes={"ground": ["far", "light", "glow2"], "mid": ["far", "near"]}),
    # Asia
    Concept("orangutan-portrait", "animal-orangutan", "Orangutan", orangutan_face, overrides=ORANG,
            checks=[("hero", "sky")], fixes={"sky": SKY_FIX}),
    Concept("orangutan-canopy", "animal-orangutan", "Orangutan in the canopy", orangutan_canopy, overrides=ORANG,
            checks=[("hero", "sky"), ("hero", "near"), ("hero", "far")], fixes={"far": ["mid", "sky2"], "near": ["deep", "mid"]}),
    Concept("proboscis-portrait", "animal-proboscis-monkey", "Proboscis monkey", proboscis_face, overrides=PROB,
            checks=[("nose", "glow"), ("hero2", "glow"), ("hero", "glow")], fixes={"glow": ["sky2", "far", "light", "near"]}),
    Concept("proboscis-river", "animal-proboscis-monkey", "On the Kinabatangan", proboscis_river, WET, overrides=PROB,
            checks=[("hero", "far"), ("hero", "mid"), ("hero", "sky")], fixes={"far": ["near", "deep"], "mid": ["near", "deep"]}),
    Concept("giantpanda-portrait", "animal-giant-panda", "Giant panda", giantpanda_face, overrides=PANDA,
            checks=[("light", "far"), ("bamboo", "far"), ("dark", "sky")], fixes={"far": ["mid", "near"]}),
    Concept("giantpanda-bamboo", "animal-giant-panda", "Bamboo forest", giantpanda_grove, overrides=PANDA,
            checks=[("light", "mid"), ("light", "far"), ("dark", "ground")], fixes={"mid": ["near", "deep"], "far": ["mid", "near"]}),
    Concept("redpanda-portrait", "animal-red-panda", "Red panda", redpanda_face, overrides=REDPANDA,
            checks=[("hero", "sky"), ("hero", "near")], fixes={"near": ["mid", "deep"]}),
    Concept("redpanda-tree", "animal-red-panda", "Red panda in the treetops", redpanda_tree, overrides=REDPANDA,
            checks=[("hero", "sky"), ("hero", "mid"), ("hero", "far")], fixes={"mid": ["far", "near"]}),
    Concept("komodo-portrait", "animal-komodo-dragon", "Komodo dragon", komodo_face, overrides=KOMODO,
            checks=[("hero", "sky"), ("hero", "mid"), ("hero", "far"), ("pop", "sky")], fixes={"mid": ["far", "ground", "near"], "far": ["sky2", "glow2"]}),
    Concept("komodo-island", "animal-komodo-dragon", "Komodo island", komodo_island, overrides=KOMODO,
            checks=[("hero", "ground"), ("hero", "mid"), ("hero2", "ground")], fixes={"ground": ["glow2", "light", "far"]}),
    Concept("hornbill-portrait", "animal-hornbill", "Great hornbill", hornbill_face, overrides=HORNBILL,
            checks=[("hero", "sky"), ("hero", "glow"), ("light", "sky")], fixes={"glow": ["near", "mid"], "sky": ["sky2", "far", "mid"]}),
    Concept("hornbill-flight", "animal-hornbill", "Hornbill over the rainforest", hornbill_flight, overrides=HORNBILL,
            checks=[("dark", "sky"), ("hero", "sky"), ("light", "sky")], fixes={"sky": ["sky2", "far", "mid"]}),
    Concept("snowleopard-portrait", "animal-snow-leopard", "Snow leopard", snowleopard_face, overrides=SNOWLEO,
            checks=[("hero", "near"), ("hero", "deep"), ("hero", "sky"), ("near", "sky")], fixes={"sky": ["mid", "far", "sky2"]}),
    Concept("snowleopard-ledge", "animal-snow-leopard", "Himalayan ledge", snowleopard_ledge, overrides=SNOWLEO,
            checks=[("hero", "sky"), ("hero", "rock"), ("hero", "near"), ("near", "sky")], fixes={"sky": ["mid", "far", "sky2"]}),
    Concept("macaque-portrait", "animal-macaque", "Snow monkey", macaque_face, overrides=MACAQUE,
            checks=[("hero", "sky"), ("light", "sky"), ("hero", "far")], fixes={"sky": ["far", "mid", "sky2"], "far": ["mid", "near"]}),
    Concept("macaque-onsen", "animal-macaque", "Hot spring bath", macaque_onsen, overrides=MACAQUE,
            checks=[("hero", "water"), ("hero", "light"), ("near", "light")], fixes={"near": ["deep", "mid"]}),
    Concept("cloudedleopard-portrait", "animal-clouded-leopard", "Clouded leopard", cloudedleopard_face, overrides=CLOUDED,
            checks=[("hero", "sky"), ("hero", "near")], fixes={"near": ["deep", "mid"], "sky": SKY_FIX}),
    Concept("cloudedleopard-tree", "animal-clouded-leopard", "Clouded leopard on the branch", cloudedleopard_tree, overrides=CLOUDED,
            checks=[("hero", "sky"), ("hero", "near"), ("hero", "dark")], fixes={"near": ["deep", "mid"], "sky": SKY_FIX}),
]
