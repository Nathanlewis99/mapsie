"""Animals of South America, the Galapagos and the oceans: a portrait and a habitat scene each."""
import math

from _common import Concept, Drawing, cloud, fish, circle, ellipse, waves, hills, rrect, group, bubbles, water  # noqa: F401

UNDERWATER = ["coastal", "dusk", "meadow"]
NO_GOLD = ["coastal", "meadow", "blush", "dusk"]
_uid = [0]


# ================================================================ helpers (copied from wildlife / water_b)
def _id(prefix):
    _uid[0] += 1
    return f"{prefix}{_uid[0]}"


def clipped(d: Drawing, path: str, fn):
    """Draw fn() clipped to `path` (rosettes on a jaguar, spots on a whale shark)."""
    cid = _id("ansclip")
    tag = f'<clipPath id="{cid}"><path d="{path}"/></clipPath><g clip-path="url(#{cid})">'
    d.raw(tag, tag)
    fn()
    d.raw("</g>", "</g>")


def flip(d: Drawing, fn, cx=100):
    group(d, f"translate({2 * cx} 0) scale(-1 1)", fn)


def at(d: Drawing, x, y, s, fn, rot=0, flipx=False, ox=100, oy=100):
    """Draw fn (drawn around (ox, oy)) centred at (x, y), scaled by s."""
    sx = -s if flipx else s
    group(d, f"translate({x} {y}) rotate({rot}) scale({sx} {s}) translate({-ox} {-oy})", fn)


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


def fluff(cx, cy, rx, ry, n=14, bump=0.12, rot=0.0):
    """A fluffy ellipse (alpaca fleece, condor ruff)."""
    pts = [(cx + rx * math.cos(rot + 2 * math.pi * i / n), cy + ry * math.sin(rot + 2 * math.pi * i / n)) for i in range(n + 1)]
    s = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(n):
        a = rot + 2 * math.pi * (i + 0.5) / n
        qx, qy = cx + rx * (1 + bump * 2) * math.cos(a), cy + ry * (1 + bump * 2) * math.sin(a)
        s += f" Q{qx:.1f} {qy:.1f} {pts[i + 1][0]:.1f} {pts[i + 1][1]:.1f}"
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


def birds(d: Drawing, pts, role="dark"):
    s = " ".join(f"M{x} {y} q{3 * k} {-3 * k} {6 * k} 0 q{3 * k} {-3 * k} {6 * k} 0" for x, y, k in pts)
    d.stroke(role, s, 1.8)


def drop(x, y, r):
    return f"M{x:.1f} {y - r * 1.7:.1f} Q{x + r:.1f} {y:.1f} {x:.1f} {y + r:.1f} Q{x - r:.1f} {y:.1f} {x:.1f} {y - r * 1.7:.1f}Z"


def rays(d: Drawing, xs=((50, 22), (118, 12))):
    s = "".join(f'<path d="M{x} -10 L{x + w} -10 L{x + w + 40} 210 L{x + 40} 210Z"/>' for x, w in xs)
    d.raw(f'<g opacity=".16" fill="#fff">{s}</g>', "")


def jungle(d: Drawing, spots, role="near", line=False):
    for x, y, a, ln, w in spots:
        d.shape(role, leaf(x, y, ln, w, a), line=line)


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


def fin(p, t, h, sweep, base=10, side=1):
    x, y, dx, dy = _bez(p, t)
    nx, ny = dy * side, -dx * side
    f = (x + dx * base * 0.5, y + dy * base * 0.5)
    b = (x - dx * base * 0.5, y - dy * base * 0.5)
    tip = (x + nx * h - dx * sweep, y + ny * h - dy * sweep)
    c = (f[0] + nx * h * 0.8, f[1] + ny * h * 0.8)
    return (f"M{f[0] - nx * 3:.1f} {f[1] - ny * 3:.1f} Q{c[0]:.1f} {c[1]:.1f} {tip[0]:.1f} {tip[1]:.1f} "
            f"Q{b[0] + nx * h * 0.2:.1f} {b[1] + ny * h * 0.2:.1f} {b[0] - nx * 3:.1f} {b[1] - ny * 3:.1f}Z")


def _catmull(pts, n=8):
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in (0, 1)))
    out.append(tuple(pts[-1]))
    return out


def track(pts, n=8):
    """Dense points along a smooth curve with unit normals: [(x, y, nx, ny, t)]."""
    c = _catmull(pts, n)
    L = len(c)
    res = []
    for i, (x, y) in enumerate(c):
        a, b = c[max(i - 1, 0)], c[min(i + 1, L - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        m = math.hypot(dx, dy) or 1
        res.append((x, y, -dy / m, dx / m, i / (L - 1)))
    return res


def ribbon(pts, w0, w1=None, n=8, cap=True):
    """A tapering tube along a smooth curve through pts. w0/w1 are full widths, or w0 is a function of t."""
    tr = track(pts, n)
    wf = w0 if callable(w0) else (lambda t: w0 + (w1 - w0) * t)
    left = [(x + nx * wf(t) / 2, y + ny * wf(t) / 2) for x, y, nx, ny, t in tr]
    right = [(x - nx * wf(t) / 2, y - ny * wf(t) / 2) for x, y, nx, ny, t in tr]
    s = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in left)
    if cap:
        x, y, nx, ny, t = tr[-1]
        r = wf(1.0) / 2
        s += f" A{r:.1f} {r:.1f} 0 0 1 {right[-1][0]:.1f} {right[-1][1]:.1f}"
    s += " L" + " L".join(f"{x:.1f} {y:.1f}" for x, y in right[::-1]) + "Z"
    return s


def rosette(d: Drawing, x, y, r, rot=0.0, inner="rose"):
    """A jaguar rosette: a broken ring of blotches with a dot in the middle."""
    d.shape(inner, circle(x, y, r * 0.85), shadow=False, line=False)
    s = ""
    for k in range(5):
        a = math.radians(rot + k * 72)
        s += circle(x + r * math.cos(a), y + r * math.sin(a), r * 0.36)
    s += circle(x, y, r * 0.24)
    d.marks("mark", s)


def claws(x, y, k=1, s=1.0):
    """Three hooked sloth claws over a branch top at (x, y)."""
    out = ""
    for i in (-1, 0, 1):
        bx = x + i * 3.6 * s
        out += f"M{bx - 1.5 * k * s:.1f} {y + 4 * s:.1f} C{bx - 2 * k * s:.1f} {y - 6 * s:.1f} {bx + 5 * k * s:.1f} {y - 7 * s:.1f} {bx + 6 * k * s:.1f} {y - 1 * s:.1f} "
    return out


# ================================================================ SLOTH
def sloth_face(d: Drawing, cx, cy, s=1.0, sleepy=False):
    def draw():
        d.shape("hero", scallop(0, 0, 24, 14, 0.06, 0.2))
        d.shape("hero2", "M-19 1 C-19 -11 -9 -18 0 -18 C9 -18 19 -11 19 1 C19 13 10 20 0 20 C-10 20 -19 13 -19 1Z", shadow=False)
        d.shape("mark", "M-17 -6 C-13 -11 -6 -9 -3 -3 C-5 3 -12 7 -21 9 C-21 2 -20 -3 -17 -6Z", shadow=False)
        d.shape("mark", "M17 -6 C13 -11 6 -9 3 -3 C5 3 12 7 21 9 C21 2 20 -3 17 -6Z", shadow=False)
        if sleepy:
            d.stroke("light", "M-12 -2 Q-9 1 -6 -2 M6 -2 Q9 1 12 -2", 1.4)
        else:
            d.marks("light", circle(-8.5, -3.5, 1.7) + circle(8.5, -3.5, 1.7))
        d.marks("mark", ellipse(0, 5, 4.4, 3.2))
        d.stroke("mark", "M-8 11 Q0 17 8 11", 1.8)
    group(d, f"translate({cx} {cy}) scale({s})", draw)


SLOTH_BODY = ("M70 96 C70 80 92 72 116 72 C140 72 162 80 162 96 C162 108 156 116 148 120 L145 129 L138 121 L131 131 "
              "L124 122 L117 132 L110 122 L103 130 L98 120 L90 127 L87 117 C76 112 70 106 70 96Z")


def sloth_hanging(d: Drawing):
    d.disc("glow", 40, 104, 16)
    d.band("far", hills(166, 10))
    jungle(d, [(-6, 150, -30, 56, 14), (4, 190, -60, 60, 15), (206, 156, -150, 56, 14), (196, 196, -120, 60, 15),
               (100, 214, -95, 44, 12)])
    d.limb("dark", "M-20 64 C40 56 140 50 224 42", 11)
    d.shape("near", leaf(24, 59, 30, 8, 115))
    d.shape("near", leaf(36, 58, 26, 7, 70), shadow=False)
    d.shape("near", leaf(184, 46, 30, 8, 75))
    d.shape("near", leaf(194, 45, 24, 7, 120), shadow=False)
    d.limb("fur2", "M86 96 L74 58", 13)
    d.limb("fur2", "M136 92 L146 50", 13)
    d.shape("hero", SLOTH_BODY)
    d.stroke("fur2", "M92 84 q6 4 4 12 M110 80 q6 4 4 12 M128 80 q6 4 4 12 M146 86 q4 4 2 10", 2, line=False)
    d.limb("hero", "M98 98 L93 56", 14)
    d.limb("hero", "M150 96 L160 50", 14)
    d.stroke("claw", claws(74, 54) + claws(93, 52) + claws(146, 48) + claws(160, 47), 2.2)
    sloth_face(d, 66, 124, 1.08)


def sloth_cecropia(d: Drawing):
    d.band("far", hills(150, 12))
    d.band("mid", hills(176, 8, 30))
    # cecropia: ringed trunk and big star-shaped leaves
    d.limb("dark", "M146 214 C144 140 142 70 148 -14", 24)
    d.stroke("far", "M135 180 h22 M134 150 h22 M134 120 h22 M135 90 h22 M136 60 h22 M138 30 h22", 1.6, line=False)
    for cx, cy, r, rot in [(40, 30, 34, 10), (186, 40, 26, -8), (30, 130, 24, 20)]:
        for i in range(8):
            d.shape("near", leaf(cx, cy, r, r * 0.24, rot + i * 45), shadow=i % 2 == 0)
        d.shape("deep", circle(cx, cy, 3.5), shadow=False, line=False)
    d.limb("dark", "M146 56 Q166 46 186 40", 4)
    # mum hugging the trunk, baby on her tummy
    d.limb("fur2", "M118 104 L146 96", 12)
    d.shape("hero", fluff(106, 120, 31, 42, 16, 0.06))
    d.stroke("fur2", "M88 108 q4 6 2 12 M118 132 q4 6 2 12 M96 146 q4 6 2 10", 2, line=False)
    d.limb("hero", "M96 88 C108 72 124 62 146 58", 13)
    d.limb("hero", "M108 152 C120 164 134 164 148 156", 13)
    d.stroke("claw", "M145 51 c7 -2 10 2 9 8 M147 57 c7 -1 9 3 8 9 M147 63 c6 0 8 4 6 9 "
                     "M147 150 c7 -2 10 2 9 8 M148 156 c7 -1 9 3 8 9 M148 162 c6 0 8 4 6 9", 2.2)
    sloth_face(d, 98, 70, 1.0)
    d.limb("hero", "M112 124 Q122 116 130 118", 8)
    sloth_face(d, 98, 128, 0.58)


# ================================================================ JAGUAR
JAG_HEAD = ("M100 42 C132 42 152 58 158 84 C164 106 160 130 146 146 C132 160 116 166 100 166 C84 166 68 160 54 146 "
            "C40 130 36 106 42 84 C48 58 68 42 100 42Z")


def jaguar_face(d: Drawing):
    jungle(d, [(-6, 40, 20, 64, 16), (-4, 96, 0, 56, 15), (2, 156, -25, 64, 16), (206, 40, 160, 64, 16),
               (204, 96, 180, 56, 15), (198, 156, -155, 64, 16), (50, 210, -75, 50, 13), (150, 210, -105, 50, 13)])
    for cx in (58, 142):
        d.shape("hero", circle(cx, 56, 16))
        d.shape("mark", circle(cx + (2 if cx < 100 else -2), 58, 11), shadow=False)
        d.shape("light", circle(cx + (3 if cx < 100 else -3), 60, 7.5), shadow=False)
    d.shape("hero", JAG_HEAD, spot=True)
    for x, y, r, a in [(56, 98, 6, 10), (50, 118, 5.5, 40), (62, 136, 5, 80), (144, 98, 6, 50), (150, 118, 5.5, 20),
                       (138, 136, 5, 0), (70, 66, 5, 30), (130, 66, 5, 60), (84, 52, 4, 0), (116, 52, 4, 30)]:
        rosette(d, x, y, r, a)
    d.marks("mark", "".join(circle(x, y, r) for x, y, r in [(100, 50, 2.6), (92, 60, 2.2), (108, 60, 2.2), (100, 66, 2.4),
                                                           (88, 70, 2), (112, 70, 2), (100, 76, 2), (94, 80, 1.6), (106, 80, 1.6)]))
    d.shape("light", "M100 110 C112 104 128 110 130 125 C131 140 116 148 100 148 C84 148 69 140 70 125 C72 110 88 104 100 110Z", shadow=False)
    d.shape("light", "M86 150 C92 158 108 158 114 150 C110 163 90 163 86 150Z", shadow=False)
    for x in (78, 122):
        d.shape("light", ellipse(x, 90, 12, 8), shadow=False)
        d.shape("hero2", circle(x, 90, 6.5), shadow=False)
        d.marks("mark", circle(x, 90, 3.4))
        d.marks("light", circle(x + 1.6, 88.4, 1.3))
    d.stroke("mark", "M66 87 Q78 80 90 88 M134 87 Q122 80 110 88 M89 94 Q93 102 92 108 M111 94 Q107 102 108 108", 2)
    d.shape("pop", "M88 106 C88 100 112 100 112 106 L104 116 C102 118 98 118 96 116Z", shadow=False)
    d.stroke("mark", "M100 117 V126 M100 126 Q92 134 84 129 M100 126 Q108 134 116 129", 2)
    d.marks("mark", "".join(circle(x, y, 1.4) for x, y in [(82, 122), (88, 128), (80, 132), (118, 122), (112, 128), (120, 132)]))
    d.stroke("light", "M76 128 L50 124 M76 133 L52 138 M124 128 L150 124 M124 133 L148 138", 1.2, line=False)


JAG_BODY = ("M62 96 C74 84 96 82 116 84 C134 85 150 84 160 92 C168 99 168 112 162 120 L165 140 L154 140 L150 124 L144 124 "
            "L143 140 L132 140 L130 120 C116 122 98 122 86 120 L85 140 L74 140 L72 122 L69 140 L58 140 L58 116 C56 108 58 100 62 96Z")
JAG_SIDE_HEAD = "M24 100 C22 82 36 68 54 66 C70 64 82 76 84 92 C86 108 76 120 60 122 L38 120 C30 118 24 110 24 100Z"


def jaguar(d: Drawing):
    d.limb("hero", "M160 96 C174 102 178 118 172 134", 7)
    d.limb("mark", "M174 126 Q174 131 172 134", 7, shadow=False)
    d.shape("hero", circle(64, 68, 7.5), shadow=False)
    d.marks("mark", circle(64, 68, 4))
    d.shape("hero", JAG_BODY, spot=True)
    d.shape("hero", JAG_SIDE_HEAD)
    pts = [(90, 92), (106, 91), (122, 92), (138, 92), (152, 96), (98, 104), (114, 104), (130, 104), (146, 108),
           (106, 116), (122, 116), (64, 124), (138, 124), (156, 128), (76, 100), (160, 112)]
    clipped(d, JAG_BODY, lambda: [rosette(d, x, y, 4.4, x * 7) for x, y in pts[::1]])
    d.marks("mark", "".join(circle(x, y, 1.7) for x, y in [(58, 78), (68, 82), (62, 92), (72, 96), (50, 86), (74, 108), (64, 106),
                                                          (54, 74), (46, 78)]))
    d.shape("light", "M24 102 C26 112 34 118 46 118 C40 112 38 106 38 100Z", shadow=False)
    d.marks("pop", "M23 92 C23 88 31 88 32 92 L28 97Z")
    d.shape("hero2", ellipse(44, 86, 4.6, 3.4), shadow=False)
    d.marks("mark", circle(43.5, 86, 1.9))
    d.stroke("mark", "M28 106 Q34 110 42 109 M28 97 V102", 1.4)


def jaguar_riverbank(d: Drawing):
    d.disc("glow", 58, 64, 26)
    birds(d, [(130, 40, 1), (146, 48, 0.8)])
    trees = "M-30 108" + "".join(f" Q{x - 7} {94 - (x % 3) * 3} {x} {104 - (x % 2) * 3}" for x in range(-16, 236, 14)) + " L230 120"
    d.band("far", trees)
    d.band("ground", "M-30 136 Q60 128 120 134 T230 132")
    group(d, "translate(104 104) scale(.98) translate(-100 -104)", lambda: jaguar(d))
    d.band("mid", waves(150, 3, 28))
    d.stroke("light", "M60 160 q8 -5 16 0 M120 162 q8 -5 16 0", 2, line=False)
    d.shape("croc", "M128 172 C132 166 142 165 150 168 C158 166 168 168 176 172Z")
    d.marks("mark", circle(141, 167.5, 1.6) + circle(153, 167.5, 1.6))
    d.band("near", waves(174, 3, 34))
    d.band("deep", waves(190, 3, 38), line=False)


# ================================================================ MACAW
def macaw_portrait(d: Drawing):
    jungle(d, [(-6, 150, -30, 60, 15), (0, 188, -60, 56, 14), (-8, 110, 0, 50, 13), (40, 210, -80, 46, 12)])
    d.shape("hero", "M90 56 C96 38 118 30 138 36 C160 44 172 64 170 90 C168 112 162 136 168 166 L180 210 L80 210 "
                    "C86 180 92 150 94 128 C86 116 82 84 90 56Z")
    d.shape("blue", "M106 172 C130 160 160 160 182 166 L190 210 L110 210Z")
    d.shape("green", "M104 150 C128 138 158 138 178 146 L182 172 C160 166 132 168 108 180Z", shadow=False)
    d.shape("hero2", "M104 122 C124 110 154 112 172 124 L176 152 C158 146 130 148 106 158 C100 146 100 132 104 122Z", spot=True)
    d.stroke("green", "M110 150 q6 -6 12 -2 M124 146 q6 -6 12 -2 M138 144 q6 -6 12 -2 M152 144 q6 -6 12 -2", 2, line=False)
    d.stroke("hero", "M110 132 q6 -6 12 -2 M126 128 q6 -6 12 -2 M142 126 q6 -6 12 -2 M156 128 q6 -6 12 -2", 1.6, line=False)
    d.shape("light", "M86 64 C92 54 106 52 116 58 C122 66 120 84 114 94 C106 102 94 104 88 98 C82 90 82 76 86 64Z", shadow=False)
    d.stroke("hero", "M92 66 q3 2 6 0 M101 63 q3 2 6 0 M89 75 q3 2 6 0 M89 84 q3 2 6 0 M97 89 q3 2 6 0 M106 88 q3 2 6 0 M95 95 q3 2 6 0", 1.3, line=False)
    d.shape("iris", circle(105, 73, 7), shadow=False)
    d.marks("mark", circle(105, 73, 3.4))
    d.marks("light", circle(106.5, 71.5, 1.2))
    d.shape("mark", "M66 98 C76 94 86 98 94 106 C94 118 84 124 74 122 C66 120 62 110 66 98Z")
    d.shape("beak", "M92 56 C76 50 58 56 52 74 C48 90 50 106 58 122 C58 110 60 100 66 94 C74 88 84 90 92 98Z")
    d.shape("mark", "M70 91 C77 87 86 90 92 98 L91 102 C84 96 77 94 70 96Z", shadow=False)


def macaw_small(d: Drawing):
    """A scarlet macaw clinging upright, facing left, drawn around (100, 110)."""
    d.shape("hero", "M102 120 L94 192 L104 194 L114 124Z")
    d.shape("blue", "M95 176 L94 192 L104 194 L106 178Z", shadow=False)
    d.shape("blue", "M106 84 C120 90 122 112 116 130 L108 152 C102 132 100 106 106 84Z")
    d.shape("hero", "M92 74 C86 90 88 112 98 126 C106 132 114 126 116 112 C118 94 112 78 104 70Z")
    d.shape("green", "M105 98 C114 100 118 110 117 120 C112 116 106 112 103 108Z", shadow=False)
    d.shape("hero2", "M106 84 C116 88 119 96 118 104 C112 102 106 100 103 96Z", shadow=False, spot=True)
    d.shape("hero", circle(96, 66, 13))
    d.shape("light", "M86 62 C88 56 94 54 98 58 C100 64 98 70 94 72 C90 72 86 68 86 62Z", shadow=False)
    d.marks("mark", circle(94, 63, 1.9))
    d.shape("mark", "M80 74 C84 72 88 72 90 74 C90 80 86 84 82 82Z")
    d.shape("beak", "M88 58 C78 56 72 62 72 70 C72 76 75 80 79 82 C79 76 81 72 89 70Z")
    d.stroke("mark", "M98 128 q-6 2 -8 6 M104 128 q-4 4 -4 8", 2.2)


def macaw_flying(d: Drawing):
    """A scarlet macaw flying left, wings up, drawn around (100, 100)."""
    d.shape("hero", "M112 106 L172 146 L176 140 L120 98Z")
    d.shape("blue", "M150 132 L172 146 L176 140 L156 126Z", shadow=False)
    d.shape("blue", "M104 104 C112 126 124 144 146 152 C136 134 128 116 116 98Z")
    d.shape("blue", "M100 96 C96 70 84 48 60 34 C64 58 72 84 88 106Z")
    d.shape("hero2", "M100 96 C98 82 94 70 88 62 C80 72 78 90 88 106Z", shadow=False, spot=True)
    d.shape("green", "M88 62 C86 66 84 70 83 74 C82 80 82 86 84 92 L80 80 C80 72 84 66 88 62Z", shadow=False)
    d.shape("hero", "M76 92 C86 82 104 86 116 96 C122 102 120 110 110 110 C96 110 82 104 76 92Z")
    d.shape("hero", circle(76, 88, 10))
    d.shape("light", "M68 86 C70 82 76 80 79 84 C80 88 78 92 74 92 C70 92 68 90 68 86Z", shadow=False)
    d.marks("mark", circle(75, 86, 1.6))
    d.shape("beak", "M68 82 C60 80 56 86 56 92 C56 96 58 98 62 99 C62 94 64 91 69 90Z")


def macaw_claylick(d: Drawing):
    d.band("clay", "M-30 62 Q40 52 100 60 T230 54")
    d.stroke("clay2", "M-30 92 Q60 84 120 92 T230 88 M-30 124 Q50 116 110 124 T230 120 M-30 154 Q70 148 130 154 T230 150", 3)
    d.marks("clay2", "".join(ellipse(x, y, rx, 2.4) for x, y, rx in [(30, 106, 6), (150, 104, 7), (96, 138, 6), (176, 140, 5),
                                                                       (44, 140, 5), (120, 76, 5), (66, 78, 4)]))
    for i, x in enumerate(range(-16, 236, 22)):
        d.shape("near", circle(x, 46 + (i % 2) * 6, 17), line=False)
    d.band("mid", waves(176, 3, 30))
    d.band("deep", waves(190, 3, 36), line=False)
    at(d, 48, 112, 0.42, lambda: macaw_small(d), ox=100, oy=120)
    at(d, 92, 122, 0.46, lambda: macaw_small(d), ox=100, oy=120, flipx=True)
    at(d, 136, 104, 0.44, lambda: macaw_small(d), ox=100, oy=120)
    at(d, 166, 134, 0.36, lambda: macaw_small(d), ox=100, oy=120, flipx=True)
    at(d, 108, 44, 0.54, lambda: macaw_flying(d), rot=-6)


# ================================================================ CAPYBARA
CAPY_BODY = ("M66 96 C76 76 120 70 152 78 C174 84 184 106 180 128 C178 142 170 150 160 152 L160 168 L148 168 L146 154 "
             "L104 156 L102 168 L90 168 L88 152 C76 146 66 132 66 116Z")
CAPY_HEAD = ("M26 90 C26 76 38 66 58 64 C76 62 92 66 100 80 C106 92 102 108 94 118 C88 126 78 128 66 128 L38 126 "
             "C30 124 26 116 26 106Z")


def capybara(d: Drawing, friend=False):
    d.shape("hero", CAPY_BODY)
    d.stroke("hero2", "M152 100 C166 112 168 136 160 150 M96 132 C100 142 98 150 96 154", 2.4, line=False)
    d.shape("hero2", circle(84, 62, 6.5))
    d.shape("hero", CAPY_HEAD, spot=True)
    d.shape("hero2", circle(82, 64, 3.5), shadow=False, line=False)
    d.marks("mark", ellipse(66, 78, 3, 2.6))
    d.marks("light", circle(67, 77, 0.9))
    d.stroke("mark", "M30 86 q3 -2 6 1 M28 114 Q32 118 40 117", 1.8)
    d.stroke("hero2", "M78 72 Q86 92 84 116", 1.6, line=False)
    if friend:
        d.stroke("mark", "M58 64 L58 56 M64 64 L63 56", 1.4)
        d.shape("bird", ellipse(62, 49, 10, 7))
        d.shape("mark", "M66 46 C74 44 80 46 84 50 C78 52 72 52 66 52Z", shadow=False)
        d.shape("bird", circle(53, 42, 5.5))
        d.shape("mark", "M48 41 L42 43 L48 45Z", shadow=False)
        d.marks("mark", circle(52, 40.5, 1.2))


def capybara_friend(d: Drawing):
    d.disc("glow", 150, 62, 24)
    d.band("far", hills(140, 8))
    d.band("ground", hills(164, 4, 30))
    group(d, "translate(102 102) scale(1.02) translate(-100 -110)", lambda: capybara(d, friend=True))
    d.band("near", hills(184, 3, 10), line=False)
    for x in (24, 40, 168, 182):
        d.stroke("near", f"M{x} 168 l-3 -10 M{x} 168 l1 -12 M{x} 168 l5 -9", 2, line=False)


def capybara_wetland(d: Drawing):
    d.disc("glow", 150, 52, 18)
    trees = "M-30 100" + "".join(f" Q{x - 7} {88 - (x % 3) * 3} {x} {96 - (x % 2) * 3}" for x in range(-16, 236, 14)) + " L230 110"
    d.band("far", trees)
    d.band("mid", "M-30 108 H230")
    # mum swimming: head and back above the water
    clipped(d, "M-30 -30 H230 V136 H-30Z", lambda: (
        group(d, "translate(84 112) scale(.82) translate(-100 -110)", lambda: capybara(d)),
        group(d, "translate(150 132) scale(.42) translate(-100 -110)", lambda: capybara(d)),
        group(d, "translate(184 134) scale(.36) translate(-100 -110)", lambda: capybara(d))))
    d.band("near", waves(134, 3, 30))
    d.stroke("light", "M30 128 q10 -5 20 0 M130 128 q8 -4 16 0 M166 128 q6 -4 12 0", 2.2)
    for x, y, rx in [(36, 158, 24), (150, 166, 28), (96, 186, 22)]:
        d.shape("lily", ellipse(x, y, rx, rx * 0.3))
        d.stroke("lily2", ellipse(x, y - 1.5, rx - 2.5, rx * 0.3 - 2.5), 1.6, line=False)
        d.shape("near", f"M{x} {y} L{x + rx * 0.9:.1f} {y - 2} L{x + rx * 0.9:.1f} {y + 2}Z", shadow=False, line=False)
    d.shape("pop", "M64 150 L70 138 L74 148 L80 136 L84 148 L90 138 L94 150Z", spot=True)
    d.shape("light", ellipse(79, 151, 15, 3), shadow=False)
    d.band("deep", waves(192, 3, 38), line=False)


# ================================================================ ALPACA
ALPACA_EAR = "M77 66 C66 52 60 36 64 22 C72 28 82 44 86 62Z"


def alpaca_portrait(d: Drawing):
    d.disc("glow", 152, 56, 18)
    d.band("far", "M-30 120 L10 96 L34 108 L64 72 L92 104 L120 80 L150 100 L176 82 L230 112")
    for snow in ["M64 72 L74 84 L68 82 L63 87 L58 81 L54 84Z", "M176 82 L184 91 L179 90 L175 94 L171 89 L168 91Z"]:
        d.shape("light", snow, shadow=False)
    d.band("mid", hills(150, 8))
    d.shape("hero", fluff(100, 196, 50, 44, 16, 0.07))
    d.shape("hero", fluff(100, 140, 32, 30, 12, 0.08), shadow=False)
    d.shape("hero", ALPACA_EAR)
    flip(d, lambda: d.shape("hero", ALPACA_EAR))
    d.shape("hero2", "M75 60 C70 50 67 40 68 30 C74 38 79 48 81 58Z", shadow=False, line=False)
    flip(d, lambda: d.shape("hero2", "M75 60 C70 50 67 40 68 30 C74 38 79 48 81 58Z", shadow=False, line=False))
    d.shape("hero", "M76 74 C74 58 126 58 124 74 C126 96 120 120 114 134 C110 142 90 142 86 134 C80 120 74 96 76 74Z")
    d.shape("hero2", fluff(100, 58, 24, 18, 12, 0.14))
    d.shape("hero2", ellipse(100, 128, 15, 13), shadow=False)
    for x in (84, 116):
        d.marks("mark", ellipse(x, 94, 5.5, 6.5))
        d.marks("light", circle(x + 1.6, 92, 1.6))
    d.stroke("mark", "M76 88 l-4 -3 M77 92 l-5 0 M124 88 l4 -3 M123 92 l5 0", 1.4)
    d.stroke("mark", "M93 123 Q96 126 99 124 M101 124 Q104 126 107 123 M100 126 V133 M93 135 Q100 139 107 135", 1.8)
    # Andean yarn tassels on the ears
    for x, y in [(70, 48), (130, 48)]:
        d.stroke("pop", f"M{x} {y} l-3 10 M{x} {y} l1 11 M{x} {y} l4 9", 2)
        d.shape("pop", circle(x, y, 5), spot=True)
        d.shape("pop2", circle(x - 3, y + 11, 3.4), shadow=False)
        d.shape("pop2", circle(x + 4, y + 10, 3), shadow=False)


def alpaca_side(d: Drawing):
    """An alpaca standing, facing right, hooves at y = 172."""
    for x0, x1 in [(68, 66), (110, 112)]:
        d.limb("fur2", f"M{x0 + 6} 136 L{x1 + 8} 172", 7)
    d.shape("hero", fluff(58, 120, 8, 8, 8, 0.15))
    d.shape("hero", fluff(96, 124, 38, 22, 16, 0.07))
    for x0, x1 in [(66, 64), (118, 120)]:
        d.limb("hero", f"M{x0} 136 L{x1} 172", 8)
    d.shape("dark", rrect(58, 170, 11, 4, 2) + rrect(114, 170, 11, 4, 2), shadow=False)
    d.shape("hero", "M116 118 C120 98 122 82 122 62 L142 60 C144 82 140 104 134 122Z")
    d.shape("hero", "M128 40 C126 32 126 26 130 22 C134 28 135 36 134 42Z")
    d.shape("hero", "M118 56 C120 46 132 42 140 46 C146 50 150 54 156 58 C160 62 158 68 152 68 L138 70 C130 70 122 64 118 56Z")
    d.shape("hero2", fluff(130, 46, 9, 7, 10, 0.18))
    d.shape("hero", "M136 42 C135 34 136 28 140 24 C143 30 143 38 141 44Z")
    d.marks("mark", circle(140, 54, 2) + circle(156.5, 61, 1.2))
    d.stroke("mark", "M152 66 Q155 67 158 64", 1.2)


def alpaca_terraces(d: Drawing):
    d.disc("glow", 50, 46, 16)
    d.band("far", "M-30 116 L16 94 L40 104 L64 90 L92 108 L230 104")
    # Huayna Picchu
    d.shape("mid", "M80 132 C98 118 112 74 128 52 C138 40 152 44 158 62 C164 82 172 104 196 114 C210 120 220 122 236 124 V150 H80Z")
    d.stroke("near", "M120 72 h14 M114 84 h22 M108 96 h30", 1.6, line=False)
    # stone ruins on the saddle
    for x, w, h in [(10, 20, 13), (34, 26, 17), (62, 18, 11)]:
        d.shape("stone", f"M{x} 132 V{132 - h} L{x + w / 2} {132 - h - 9} L{x + w} {132 - h} V132Z")
        d.marks("stone2", f"M{x + w / 2 - 3} {132 - h + 4} L{x + w / 2 + 3} {132 - h + 4} L{x + w / 2 + 4} {132 - h + 11} L{x + w / 2 - 4} {132 - h + 11}Z")
    for i, y in enumerate([134, 150, 166, 182]):
        d.band("near", f"M-30 {y + 2} Q100 {y - 4} 230 {y + 2}", line=i < 3)
        d.stroke("stone", f"M-30 {y + 4} Q100 {y - 2} 230 {y + 4}", 2.4, line=False)
    at(d, 70, 170, 0.62, lambda: alpaca_side(d), ox=100, oy=172)


# ================================================================ ANDEAN CONDOR
def condor_portrait(d: Drawing):
    d.band("far", "M-30 140 L10 110 L36 124 L70 80 L100 116 L136 74 L170 112 L230 96")
    for snow in ["M70 80 L80 93 L74 91 L69 96 L63 90 L59 93Z", "M136 74 L147 89 L141 87 L135 93 L129 86 L125 89Z"]:
        d.shape("light", snow, shadow=False)
    d.shape("dark", "M22 210 C28 162 62 136 100 134 C140 132 172 156 180 210Z")
    d.shape("wing", "M126 152 C150 154 168 172 176 204 L150 206 C146 184 138 166 122 158Z", shadow=False)
    d.stroke("dark", "M136 166 Q150 172 156 190 M130 160 Q146 170 150 194", 1.4, line=False)
    d.shape("light", fluff(100, 132, 50, 14, 16, 0.12))
    d.shape("hero", "M74 132 C72 116 74 100 80 88 L112 84 C116 98 120 116 124 132Z")
    d.stroke("hero2", "M82 100 q6 4 12 0 M80 110 q8 4 16 0 M80 120 q10 4 22 0", 1.8)
    d.shape("hero", "M58 74 C58 58 72 48 88 48 C104 48 116 58 116 74 C116 88 106 96 92 96 L72 96 C64 94 58 86 58 74Z")
    d.shape("hero2", "M64 92 C62 100 68 108 76 106 C76 100 72 94 64 92Z")
    d.shape("hero2", "M62 62 C58 52 62 44 70 44 C72 38 80 36 84 42 C88 38 96 40 96 46 C100 46 102 52 98 56 C88 58 74 60 62 62Z", spot=True)
    d.shape("beak", "M64 66 C52 64 40 68 36 78 C34 86 36 92 40 96 C40 90 42 86 48 86 L64 86Z")
    d.stroke("mark", "M64 66 C52 64 40 68 36 78 C34 86 36 92 40 96 C40 90 42 86 48 86", 1.4, line=False)
    d.shape("hero2", "M58 64 L65 64 L65 86 L58 86Z", shadow=False)
    d.shape("hero", "M48 86 L65 86 L65 92 C58 94 52 92 48 88Z", shadow=False)
    d.shape("light", circle(82, 68, 4.6), shadow=False)
    d.marks("mark", circle(82, 68, 2.5))


def condor_wing():
    s = "M98 92 C80 84 58 82 42 84"
    for i in range(6):
        y0 = 84 + i * 3.9
        y1 = y0 + 3.9
        tx = 16 + abs(i - 2.2) * 3
        ty = (y0 + y1) / 2 - 4 + i * 1.4
        s += f" L{44 if i else 42} {y0 + 0.7:.1f} Q{tx + 2:.1f} {ty - 2:.1f} {tx:.1f} {ty:.1f} Q{tx + 3:.1f} {ty + 2.5:.1f} 44 {y1 - 0.6:.1f}"
    s += " L42 108 C58 114 80 114 98 106Z"
    return s


def condor_soaring(d: Drawing):
    d.disc("glow", 150, 150, 26)
    d.band("far", "M-30 136 L14 112 L40 124 L74 88 L104 120 L140 92 L176 122 L230 104")
    for snow in ["M74 88 L84 101 L78 99 L73 104 L67 98 L63 101Z", "M140 92 L150 105 L144 103 L139 108 L133 102 L129 104Z",
                 "M14 112 L22 120 L17 119 L13 123 L9 118Z"]:
        d.shape("light", snow, shadow=False)
    d.band("mid", "M-30 160 L24 138 L60 156 L100 136 L140 158 L180 140 L230 156")
    d.band("near", hills(182, 8))

    def bird():
        d.shape("dark", "M94 112 L100 130 L106 112Z")
        d.shape("dark", condor_wing())
        flip(d, lambda: d.shape("dark", condor_wing()))
        d.shape("wing", "M96 99 C80 104 62 104 48 100 L48 105 C62 111 80 111 96 106Z", shadow=False, spot=True)
        flip(d, lambda: d.shape("wing", "M96 99 C80 104 62 104 48 100 L48 105 C62 111 80 111 96 106Z", shadow=False, spot=True))
        d.shape("dark", ellipse(100, 100, 9, 16))
        d.shape("light", fluff(100, 86, 7.5, 5, 10, 0.18), shadow=False)
        d.shape("hero", ellipse(100, 78, 5, 6.5), shadow=False)
        d.shape("beak", "M98 72 L100 66 L102 72Z", shadow=False)
    group(d, "translate(100 72) scale(.96) rotate(-8) translate(-100 -100)", bird)


# ================================================================ GIANT TORTOISE
DOME = "M44 132 C40 92 70 58 112 56 C152 54 180 86 178 132 C160 138 66 140 44 132Z"


def tortoise_portrait(d: Drawing):
    d.disc("glow", 150, 58, 22)
    d.band("far", hills(132, 8))
    d.band("ground", hills(162, 4, 30))

    def t():
        d.shape("hero2", "M146 122 L148 164 L172 164 L168 120Z")
        d.shape("hero2", "M58 116 C52 134 50 150 52 164 L78 164 C80 148 82 134 84 120Z")
        d.shape("hero", DOME, spot=True)
        d.shape("hero2", "M44 132 C66 140 160 138 178 132 L176 141 C158 147 66 149 46 141Z", shadow=False)
        d.stroke("mark", "M60 136 V145 M80 138 V147 M100 139 V148 M120 139 V148 M140 138 V147 M160 136 V144", 1.6, line=False)
        d.stroke("mark", "M64 80 L80 96 L74 128 M80 96 L110 90 L140 96 L148 128 M140 96 L154 76 M110 90 L112 58 "
                         "M110 90 L110 130 M86 62 L80 96 M134 60 L140 96", 2.4)
        d.stroke("light", "M90 72 Q100 66 110 70 M118 74 Q126 72 132 78", 2, line=False)
        d.shape("hero2", "M62 112 C48 102 40 90 36 76 L54 68 C58 82 66 94 76 102Z")
        d.stroke("mark", "M44 90 l8 -4 M48 98 l8 -5 M54 104 l8 -5", 1.4)
        d.shape("hero2", "M22 70 C22 58 32 52 42 52 C52 52 58 60 56 70 C54 78 46 82 36 82 C28 82 22 78 22 70Z")
        d.stroke("mark", "M23 72 Q30 77 40 74", 1.6)
        d.marks("mark", circle(40, 63, 2.3) + circle(25, 65, 1))
        d.stroke("mark", "M35 59 Q40 56 45 60", 1.4)
        d.marks("mark", "".join(circle(x, y, 1.3) for x, y in [(60, 150), (66, 156), (72, 148), (154, 150), (162, 156), (160, 142)]))
    group(d, "translate(106 112) scale(.9) translate(-100 -110)", t)


def opuntia(d: Drawing):
    d.limb("trunk", "M164 190 C162 160 164 130 160 100", 9)
    d.limb("trunk", "M161 112 L140 80 M161 104 L166 70 M162 96 L176 84", 6)
    for x, y, rx, ry, a in [(118, 50, 11, 15, -40), (144, 44, 11, 16, -8), (168, 58, 11, 15, 28), (170, 90, 10, 14, 50),
                            (100, 70, 9, 13, -60)]:
        d.shape("pad", ellipse(x, y, rx, ry), extra=f'transform="rotate({a} {x} {y})"')
        d.marks("pad2", circle(x - 3, y - 3, 1) + circle(x + 3, y + 2, 1) + circle(x - 2, y + 6, 1))
    for x, y in [(140, 30), (176, 48), (112, 38)]:
        d.shape("pop", scallop(x, y, 3.4, 5, 0.3), shadow=False, spot=True)


def tortoise_cactus(d: Drawing):
    d.disc("glow", 44, 52, 18)
    d.band("far", "M-30 120 Q10 116 36 102 L62 76 Q76 70 90 76 L120 104 Q160 118 230 116")
    d.band("mid", hills(146, 6))
    opuntia(d)
    d.band("ground", hills(166, 4, 30))

    def t():
        d.shape("hero2", "M112 126 L118 164 L136 164 L132 124Z")
        d.shape("hero2", "M48 128 L46 166 L66 166 L68 128Z")
        d.shape("hero", "M36 150 C34 116 54 94 82 92 C102 92 116 98 124 104 C130 96 138 98 140 106 C142 120 140 136 138 152 C110 158 60 158 36 150Z", spot=True)
        d.shape("hero2", "M36 148 C60 156 110 156 138 150 L137 157 C110 162 60 162 37 156Z", shadow=False)
        d.stroke("mark", "M52 120 L68 108 L92 106 L112 112 L122 128 M68 108 L66 150 M92 106 L94 152 M112 112 L116 150 M44 136 L136 136", 2.2)
        d.shape("hero2", "M128 116 C132 100 136 86 140 72 L154 74 C150 90 146 106 140 120Z")
        d.stroke("mark", "M136 104 l9 3 M139 92 l9 3", 1.3)
        d.shape("hero2", "M136 70 C134 60 140 52 148 52 C156 52 162 58 160 66 C158 72 152 76 144 76 C140 76 137 74 136 70Z")
        d.marks("mark", circle(148, 60, 2) + circle(158, 61, 0.9))
        d.stroke("mark", "M160 64 Q154 68 146 66", 1.3)
    group(d, "translate(-4 8)", t)


# ================================================================ BLUE-FOOTED BOOBY
def booby(d: Drawing, raise_foot=True, point=False):
    """A blue-footed booby facing left, standing with feet at y ~168, drawn around (100, 100)."""
    d.limb("hero2", "M110 140 L112 164", 5)
    d.shape("hero2", "M94 168 L112 161 L131 168 Q113 175 94 168Z", spot=True)
    if raise_foot:
        d.limb("hero2", "M94 138 L80 142", 5)
        d.shape("hero2", "M82 143 L60 126 Q52 138 58 152 Z", spot=True)
        d.stroke("mark", "M80 143 L60 130 M80 143 L57 140 M80 143 L59 150", 1, line=False)
    else:
        d.limb("hero2", "M94 140 L90 164", 5)
        d.shape("hero2", "M72 168 L90 161 L106 168 Q89 175 72 168Z", spot=True)
    d.shape("hero", "M128 124 L158 148 L152 154 L122 134Z")
    d.shape("light", "M86 62 C72 72 66 98 72 120 C78 138 94 146 110 144 C128 140 136 124 134 100 C132 80 118 64 102 58Z")
    if point:
        d.shape("hero", "M114 70 C138 60 156 66 166 54 C162 82 146 112 130 136 C122 140 112 132 114 118Z")
        d.shape("hero", "M86 74 C70 62 54 62 40 52 C46 76 60 104 76 124 C82 126 88 116 88 104Z")
    else:
        d.shape("hero", "M114 66 C134 76 144 106 136 132 C130 144 116 148 108 144 C122 126 124 96 114 66Z")
        d.marks("light", "".join(circle(x, y, 1.2) for x, y in [(124, 88), (130, 100), (126, 112), (132, 122), (120, 100)]))
    if point:
        d.shape("head", "M88 74 C84 60 86 46 92 36 L110 38 C114 50 114 62 112 72Z")
        d.shape("head", circle(100, 34, 13))
        d.shape("beak", "M92 26 L98 -14 L106 26Z")
        d.shape("eye", circle(96, 32, 3.6), shadow=False)
        d.marks("mark", circle(96, 32, 1.6))
    else:
        d.shape("head", "M86 56 C84 64 84 70 88 76 L110 72 C112 64 112 58 110 52Z")
        d.shape("head", circle(98, 46, 16))
        d.stroke("hero", "M104 36 q4 4 2 10 M110 44 q2 4 0 8 M98 58 q4 4 8 4", 1.2, line=False)
        d.shape("beak", "M86 38 L44 56 L86 55Z")
        d.stroke("mark", "M86 49 L52 55", 1.2)
        d.shape("mark", "M84 38 L90 42 L88 52 L84 54Z", shadow=False)
        d.shape("eye", circle(95, 44, 4.4), shadow=False)
        d.marks("mark", circle(95, 44, 1.9))


def booby_feet(d: Drawing):
    d.disc("glow", 150, 52, 20)
    d.band("far", "M-30 112 H230")
    d.band("mid", waves(128, 3, 28))
    d.band("lava", "M-30 160 C10 150 40 156 70 158 C110 162 150 150 230 158")
    d.marks("lava2", circle(30, 176, 2) + circle(150, 172, 2.4) + circle(176, 184, 1.6) + circle(50, 190, 1.8))
    group(d, "translate(104 104) scale(1.0) translate(-100 -100)", lambda: booby(d))


def booby_dance(d: Drawing):
    d.disc("glow", 100, 78, 30)
    d.shape("light", cloud(18, 56, 0.9), shadow=False)
    d.band("far", "M-30 118 H230")
    d.band("mid", waves(134, 3, 28))
    d.band("lava", "M-30 158 C20 148 60 152 100 154 C140 156 170 148 230 154")
    at(d, 66, 124, 0.64, lambda: booby(d, raise_foot=False), flipx=True)
    at(d, 136, 122, 0.7, lambda: booby(d, raise_foot=True, point=True))
    d.marks("lava2", circle(36, 178, 2) + circle(140, 176, 2.4) + circle(170, 186, 1.6))


# ================================================================ MARINE IGUANA
IGUANA_HEAD = ("M36 98 C34 80 48 66 70 62 C92 58 114 62 128 72 C142 82 150 92 160 104 C172 118 180 138 184 160 "
               "L188 210 L64 210 C70 184 76 160 74 138 C60 134 44 126 38 116 C36 110 36 104 36 98Z")


def iguana_portrait(d: Drawing):
    d.disc("glow", 150, 46, 18)
    d.band("far", "M-30 124 H230")
    d.band("mid", waves(142, 3, 28))
    d.stroke("light", "M20 138 q8 -5 16 0", 2, line=False)
    # crest spines down the neck
    sp = ""
    for i in range(10):
        t = i / 9
        x, y = 124 + 58 * t, 70 + 68 * t ** 1.3
        h = 14 - 5 * t
        sp += f"M{x - 4:.1f} {y + 3:.1f} L{x + h * 0.55:.1f} {y - h:.1f} L{x + 6:.1f} {y + 5:.1f}Z "
    d.shape("hero", sp)
    d.shape("hero", IGUANA_HEAD, spot=True)
    bumps = ""
    for x, y in [(48, 72), (58, 65), (70, 61), (82, 59), (94, 59), (106, 61), (117, 65)]:
        bumps += f"M{x - 6} {y + 4} Q{x} {y - 9} {x + 6} {y + 4}Z "
    d.shape("hero", bumps, shadow=False)
    d.shape("light", "M46 72 C60 62 92 56 116 62 C102 68 76 70 50 80Z", shadow=False)
    d.marks("light", circle(58, 70, 2.4) + circle(76, 64, 2) + circle(96, 62, 2.2) + circle(110, 66, 1.6))
    d.shape("hero2", "M88 96 C100 90 118 96 122 108 C114 116 98 116 90 110Z", shadow=False)
    d.shape("hero2", "M120 120 C132 114 146 120 150 132 C140 140 126 138 120 130Z", shadow=False)
    d.shape("green", "M104 134 C116 130 128 138 126 150 C116 154 104 148 104 140Z", shadow=False)
    d.shape("green", "M150 150 C162 146 172 154 172 166 C160 170 150 164 150 156Z", shadow=False)
    d.shape("hero2", "M90 160 C102 156 114 164 112 176 C100 180 90 172 90 166Z", shadow=False)
    d.stroke("mark", "M38 106 C52 114 70 116 86 112", 2.2)
    d.shape("eye", circle(74, 86, 5.2), shadow=False)
    d.marks("mark", circle(74, 86, 2.6))
    d.stroke("mark", "M63 80 Q74 73 85 80", 2)
    d.marks("mark", circle(44, 86, 2.2))
    for x, y, r in [(30, 74, 2.4), (22, 82, 2), (26, 64, 2), (16, 72, 1.6), (20, 58, 1.4)]:
        d.shape("light", drop(x, y, r), shadow=False)
    d.limb("hero", "M86 186 C74 190 62 192 50 190", 12)
    d.stroke("mark", "M52 186 l-8 -4 M50 190 l-9 0 M52 194 l-8 4", 2)
    d.band("near", hills(196, 4), line=False)


def iguana_side(d: Drawing):
    """A marine iguana sprawled on a rock, facing right, claws at y ~140."""
    tr = [(14, 152), (34, 140), (60, 129), (86, 123), (112, 121), (136, 118)]
    w = lambda t: 2 + 24 * (t / 0.72) ** 1.2 if t < 0.72 else 26 - (t - 0.72) * 34
    d.limb("hero", "M84 126 L72 138 L62 140 M118 124 L130 138 L140 140", 7)
    d.stroke("mark", "M62 140 l-6 -2 M62 140 l-6 2 M140 140 l6 -2 M140 140 l6 2", 1.4, line=False)
    sp = ""
    for x, y, nx, ny, t in track(tr)[12::3]:
        h = 3 + 7 * math.sin(math.pi * min(t * 1.1, 1))
        hw = w(t) / 2
        bx, by = x - nx * (hw - 1.5), y - ny * (hw - 1.5)
        sp += f"M{bx - 3.2:.1f} {by + 1:.1f} L{bx - nx * h + 1.5:.1f} {by - ny * h:.1f} L{bx + 3.2:.1f} {by + 1:.1f}Z "
    d.shape("hero", sp)
    d.shape("hero", ribbon(tr, w, cap=False), spot=True)
    d.shape("hero2", ellipse(100, 124, 10, 5) + ellipse(76, 128, 7, 4), shadow=False)
    d.shape("green", ellipse(118, 126, 7, 4) + ellipse(56, 134, 6, 3.4), shadow=False)
    d.shape("hero", "M126 108 C134 98 152 98 164 104 C171 108 171 118 164 122 L138 128 C130 126 124 116 126 108Z")
    d.shape("light", "M130 104 C138 98 154 98 164 104 C152 104 140 106 132 112Z", shadow=False)
    d.marks("eye", circle(150, 110, 2.6))
    d.marks("mark", circle(150, 110, 1.3))
    d.stroke("mark", "M168 117 Q156 122 142 120", 1.4)


def iguana_lava(d: Drawing):
    d.disc("glow", 150, 48, 18)
    d.band("far", "M-30 88 H230")
    d.band("mid", waves(104, 3, 26))
    d.shape("light", "M-30 118 Q10 104 40 112 Q60 100 84 112 Q120 102 150 112 Q180 100 230 112 V124 H-30Z", shadow=False)
    d.shape("lava", "M-30 140 C-10 118 20 110 50 114 C70 116 84 124 90 140Z")
    at(d, 56, 116, 0.5, lambda: iguana_side(d), flipx=True, ox=100, oy=140)
    d.band("lava", "M-30 154 C20 140 60 140 100 146 C140 152 180 138 230 146")
    d.marks("lava2", circle(30, 172, 2) + circle(110, 176, 2.4) + circle(176, 166, 1.6) + circle(70, 188, 1.8) + circle(150, 190, 2))
    at(d, 106, 150, 0.98, lambda: iguana_side(d), ox=100, oy=140)

    def crab():
        d.stroke("crab2", "M-8 2 l-8 6 l-2 8 M-6 4 l-6 10 M8 2 l8 6 l2 8 M6 4 l6 10 M-4 5 l-2 10 M4 5 l2 10", 2.2)
        d.shape("crab", ellipse(0, 0, 11, 8), spot=True)
        d.limb("crab", "M-8 -4 L-14 -10 M8 -4 L14 -10", 3.5)
        d.shape("crab", ellipse(-15, -12, 4, 3) + ellipse(15, -12, 4, 3), shadow=False)
        d.marks("mark", circle(-3, -7, 1.4) + circle(3, -7, 1.4))
    group(d, "translate(142 176) rotate(-8)", crab)


# ================================================================ SEA LION
SEALION_BODY = "M160 200 C160 158 148 124 124 98 C110 84 94 74 82 68 L60 92 C74 100 84 114 88 132 C92 154 86 178 76 200Z"
SEALION_HEAD = "M86 68 C84 52 70 44 56 46 C44 48 32 56 28 66 C26 74 30 80 38 80 C46 82 56 88 64 96 C80 96 88 84 86 68Z"


def sealion_portrait(d: Drawing):
    d.disc("glow", 148, 54, 22)
    d.shape("light", cloud(116, 34, 0.8), shadow=False)
    d.band("far", "M-30 128 H230")
    d.band("mid", waves(146, 3, 28))
    d.shape("hero", SEALION_BODY)
    d.shape("hero2", "M66 94 C80 104 88 118 90 134 C92 154 88 178 80 200 L94 200 C100 176 102 152 98 130 C94 112 84 98 72 88Z", shadow=False)
    d.shape("hero", SEALION_HEAD, spot=True)
    d.shape("flipper", "M72 56 C76 52 82 54 80 61Z", shadow=False)
    d.marks("mark", circle(54, 62, 5))
    d.marks("light", circle(55.6, 60.4, 1.7))
    d.marks("mark", ellipse(30, 67, 3, 2.2))
    d.stroke("mark", "M32 76 Q40 81 50 79", 1.7)
    d.marks("mark", circle(40, 74, 0.9) + circle(44, 76, 0.9) + circle(38, 78, 0.9))
    d.stroke("light", "M40 74 L14 70 M40 77 L16 80 M42 79 L22 90", 1.2)
    d.shape("flipper", "M88 136 C76 150 62 166 44 178 C60 184 82 174 98 158Z")
    d.band("rock", "M-30 184 C20 172 60 176 100 180 C140 182 170 172 230 176")


def sealion_bench(d: Drawing):
    d.disc("glow", 150, 46, 16)
    d.band("far", "M-30 96 H230")
    d.band("mid", waves(108, 2, 26), line=False)
    d.shape("light", "M20 92 L44 92 L40 98 L24 98Z", shadow=False)
    d.stroke("dark", "M32 92 V76", 1.4)
    d.shape("pop", "M33 77 L40 86 H33Z", shadow=False)
    d.band("ground", "M-30 118 H230")
    d.limb("wood2", "M42 150 L40 180 M158 150 L160 180 M44 96 L44 142 M156 96 L156 142", 6)
    d.shape("wood", rrect(26, 92, 148, 10, 3), spot=True)
    d.shape("wood", rrect(26, 106, 148, 10, 3), spot=True)
    # sea lion napping along the seat
    tr = [(40, 128), (70, 124), (104, 126), (138, 130), (160, 134)]
    w = lambda t: 26 + 8 * math.sin(math.pi * min(t * 1.2, 1)) - 18 * t ** 3
    d.shape("flipper", "M156 132 C166 124 178 124 182 128 C178 134 170 138 160 140Z")
    d.shape("flipper", "M156 136 C166 136 176 142 178 148 C170 148 162 146 154 142Z")
    d.shape("hero", ribbon(tr, w, cap=False))
    d.shape("hero2", ribbon([(48, 136), (80, 136), (120, 138), (148, 140)], 6, 4), shadow=False)
    d.shape("flipper", "M80 136 C78 148 74 160 66 168 C76 168 86 158 92 140Z")
    d.shape("hero", "M50 112 C40 104 26 104 20 112 C16 118 18 126 24 128 C32 132 44 134 54 136Z")
    d.stroke("mark", "M30 114 Q34 117 38 114", 1.6)
    d.marks("mark", ellipse(20, 116, 2.2, 1.8))
    d.stroke("light", "M24 122 L8 120 M24 124 L10 128", 1.1, line=False)
    d.shape("wood", rrect(20, 140, 160, 10, 3), spot=True)
    d.stroke("dark", "M52 84 h8 l-8 8 h8 M64 68 h11 l-11 11 h11", 1.8)
    d.band("near", hills(190, 3), line=False)


# ================================================================ PINK RIVER DOLPHIN
BOTO_BODY = ("M40 108 C60 96 90 84 118 84 C132 84 138 74 150 72 C164 70 172 80 170 94 L194 101 C196 102 196 105 194 106 "
             "L166 108 C158 113 148 115 140 116 C124 122 96 124 72 120 C56 118 46 116 40 114Z")


def boto(d: Drawing, flipper=True):
    """An Amazon river dolphin facing right: chunky body, round melon, long thin beak. Drawn around (100, 100)."""
    d.shape("hero", "M44 111 C36 104 26 96 14 94 C20 104 24 110 28 112 C24 116 20 124 16 134 C28 128 38 120 46 114Z")
    d.shape("hero", "M90 88 C98 80 106 78 116 80 C108 82 102 86 96 90Z")
    d.shape("hero", BOTO_BODY, spot=True)
    d.shape("hero2", "M72 118 C96 121 124 118 146 112 C136 117 122 121 104 122 C92 123 82 121 72 118Z", shadow=False)
    if flipper:
        d.shape("hero", "M120 112 C122 128 116 140 104 150 C120 148 132 136 134 116Z")
    d.stroke("mark", "M194 104 L168 105", 1.2)
    d.stroke("hero2", "M138 86 Q142 96 140 108", 1.6, line=False)
    d.marks("mark", circle(160, 92, 1.9))


def pinkdolphin_portrait(d: Drawing):
    water(d, bottom=False)
    rays(d)
    d.limb("dark", "M18 -10 C22 60 16 120 26 210", 10)
    d.limb("dark", "M24 120 L50 150 M20 60 L44 40", 4)
    d.limb("dark", "M178 -10 C172 50 182 120 172 210", 9)
    d.limb("dark", "M176 90 L156 70 M174 150 L196 168", 4)
    for x, y, a in [(44, 40, -40), (50, 150, 40), (156, 70, -140), (194, 166, 30)]:
        d.shape("near", leaf(x, y, 18, 5, a), shadow=False, line=False)
    group(d, "translate(98 104) scale(1.0) rotate(-22) translate(-104 -100)", lambda: boto(d))
    for x, y, s in [(56, 64, 0.8), (70, 56, 0.7), (126, 154, 0.8), (140, 162, 0.7)]:
        d.shape("hero2", fish(x, y, s, right=True), shadow=False)
    bubbles(d, [(150, 46, 2.5), (156, 34, 3.5), (148, 24, 2)])


def pinkdolphin_amazon(d: Drawing):
    d.disc("glow", 52, 58, 20)
    trees = "M-30 104" + "".join(f" Q{x - 8} {84 - (x % 3) * 5} {x} {98 - (x % 2) * 4}" for x in range(-14, 236, 16)) + " L230 112"
    d.band("far", trees)
    # stilt house on the bank
    d.stroke("dark", "M150 112 V96 M162 112 V96 M174 112 V96", 2)
    d.shape("ground", rrect(146, 82, 32, 15, 1))
    d.shape("dark", "M140 84 L162 68 L184 84Z")
    d.marks("dark", rrect(156, 86, 7, 7, 1))
    d.band("mid", "M-30 110 H230")
    clipped(d, "M-30 -30 H230 V140 H-30Z", lambda: group(d, "translate(96 116) rotate(-30) translate(-112 -100)", lambda: boto(d, flipper=False)))
    d.band("near", waves(138, 3, 30))
    for x, y, r in [(150, 132, 3), (160, 126, 2.4), (140, 124, 2.2), (44, 132, 2.4), (34, 126, 2)]:
        d.shape("light", drop(x, y, r), shadow=False)
    d.stroke("light", "M30 140 q8 -5 16 0 M144 142 q8 -5 16 0 M86 160 q8 -5 16 0", 2.2)
    # dugout canoe
    d.shape("dark", "M12 164 H76 C72 172 64 176 56 176 H28 C20 176 14 170 12 164Z")
    d.shape("dark", circle(44, 148, 5.5))
    d.shape("dark", rrect(39, 152, 10, 13, 4))
    d.limb("dark", "M54 146 L64 178", 2.4)
    d.band("deep", waves(184, 3, 36), line=False)


# ================================================================ POISON DART FROG
def frog_front(d: Drawing):
    for k in (1, -1):
        def side():
            d.shape("hero2", "M62 142 C46 140 36 124 44 110 C52 100 68 104 76 118Z")
            d.limb("hero2", "M56 140 L40 156", 6)
            d.shape("hero2", circle(32, 158, 4) + circle(38, 164, 4) + circle(46, 166, 3.6), shadow=False)
        if k == 1:
            side()
        else:
            flip(d, side)
    d.shape("hero", "M100 72 C124 72 140 90 142 112 C144 134 126 152 100 152 C74 152 56 134 58 112 C60 90 76 72 100 72Z", spot=True)
    d.shape("hero", "M66 88 C66 66 82 56 100 56 C118 56 134 66 134 88 C134 102 120 110 100 110 C80 110 66 102 66 88Z")
    for k in (1, -1):
        def arm():
            d.limb("hero2", "M76 112 L66 134 L56 140", 7)
            d.shape("hero2", circle(50, 138, 3.8) + circle(54, 146, 3.8) + circle(62, 146, 3.4), shadow=False)
        if k == 1:
            arm()
        else:
            flip(d, arm)
    d.marks("mark", "".join(ellipse(x, y, rx, ry) for x, y, rx, ry in [
        (100, 92, 5, 4), (88, 122, 4.6, 3.6), (112, 124, 5, 4), (100, 140, 4, 3), (124, 106, 3, 4), (76, 106, 3, 4),
        (90, 76, 2.4, 2), (112, 78, 2.6, 2), (122, 140, 3, 2.4), (78, 138, 3, 2.4)]))
    for x in (78, 122):
        d.shape("mark", circle(x, 68, 11))
        d.marks("light", circle(x + 3, 64, 2.8))
    d.stroke("mark", "M82 100 Q100 106 118 100", 1.8)


def dartfrog_blue(d: Drawing):
    jungle(d, [(-6, 40, 20, 60, 15), (-4, 96, 0, 50, 13), (206, 50, 160, 60, 15), (204, 104, 180, 50, 13)], "mid")
    d.shape("near", "M-20 170 C20 140 90 140 140 146 C170 150 200 160 220 176 C180 190 120 196 60 192 C20 190 -10 184 -20 170Z")
    d.stroke("deep", "M-10 172 C40 162 120 162 210 176 M60 168 L40 182 M100 166 L86 186 M140 168 L130 188 M60 166 L50 152 M120 164 L120 150", 2, line=False)
    for x, y, r in [(40, 60, 2.4), (160, 40, 2), (170, 130, 2.6)]:
        d.shape("light", drop(x, y, r), shadow=False)
    group(d, "translate(100 96) scale(1.04) translate(-100 -110)", lambda: frog_front(d))


def frog_side(d: Drawing):
    """A frog sitting side-on facing left, feet at y ~ 136."""
    d.shape("hero2", "M106 116 C122 108 140 112 142 126 C144 134 132 138 120 136 L100 134Z")
    d.limb("hero2", "M120 134 L96 138", 6)
    d.shape("hero2", circle(92, 136, 3.4) + circle(96, 141, 3.4), shadow=False)
    d.shape("hero", "M52 116 C52 104 62 94 76 92 C92 88 112 92 126 102 C136 110 138 122 130 128 C120 134 100 134 84 132 L64 130 C56 128 52 122 52 116Z", spot=True)
    d.shape("hero", circle(70, 96, 8))
    d.shape("mark", circle(70, 95, 6), shadow=False)
    d.marks("light", circle(72, 93, 1.6))
    d.limb("hero2", "M74 124 L70 138 L62 140", 6)
    d.shape("hero2", circle(58, 140, 3.2) + circle(62, 145, 3.2), shadow=False)
    d.stroke("mark", "M54 118 Q62 122 72 120", 1.4)
    d.marks("mark", "".join(circle(x, y, r) for x, y, r in [(92, 98, 1.6), (104, 104, 1.8), (116, 108, 1.5), (96, 112, 1.4), (84, 106, 1.3), (110, 120, 1.5)]))


def dartfrog_bromeliad(d: Drawing):
    jungle(d, [(-6, 40, 20, 60, 15), (-4, 100, 0, 50, 13), (206, 50, 160, 60, 15), (204, 104, 180, 50, 13)], "mid")
    for x, y, r in [(30, 30, 2), (60, 50, 2.4), (160, 26, 2.2), (176, 60, 2), (130, 40, 1.8)]:
        d.shape("light", drop(x, y, r), shadow=False)
    for i, a in enumerate([-172, -150, -128, -52, -30, -8]):
        d.shape("brom" if i % 2 else "brom2", leaf(100, 186, 92, 16, a))
    for a in [-160, -20]:
        d.shape("bromtip", leaf(100 + 70 * math.cos(math.radians(a)), 186 + 70 * math.sin(math.radians(a)), 22, 6, a), shadow=False)
    d.shape("brom", leaf(100, 186, 76, 16, -110))
    d.shape("brom2", leaf(100, 186, 76, 16, -70))
    d.shape("brom", "M60 140 C70 128 130 128 140 140 C130 150 70 150 60 140Z")
    d.shape("water", ellipse(100, 138, 34, 6), shadow=False)
    d.stroke("light", "M84 138 q6 -3 12 0", 1.6, line=False)
    at(d, 104, 112, 1.0, lambda: frog_side(d), ox=96, oy=136)
    d.shape("brom2", leaf(100, 186, 64, 15, -118))
    d.shape("brom", leaf(100, 186, 64, 15, -62))


# ================================================================ TOUCAN
K_UPPER = "M98 52 C70 44 38 54 24 78 C18 88 16 98 18 106 C30 94 54 86 98 82Z"
K_LOWER = "M98 82 C54 86 30 94 18 106 C34 104 62 100 98 96Z"


def keel_bill(d: Drawing):
    d.shape("bill", K_UPPER, spot=True)
    clipped(d, K_UPPER, lambda: (
        d.shape("bill2", "M78 30 C64 50 56 70 50 100 L66 100 C72 74 82 52 92 34Z", shadow=False, line=False),
        d.shape("bill3", "M10 60 L36 60 L30 110 L10 110Z", shadow=False),
    ))
    d.shape("bill4", K_LOWER)
    clipped(d, K_LOWER, lambda: (
        d.shape("bill", "M80 80 L100 80 L100 100 L76 100Z", shadow=False, line=False),
        d.shape("bill3", "M10 90 L34 90 L30 110 L10 110Z", shadow=False),
    ))
    d.stroke("mark", "M98 82 C54 86 30 94 19 105", 1.4)


def toucan_rainbow(d: Drawing):
    jungle(d, [(206, 60, 160, 56, 14), (204, 120, 180, 50, 13), (196, 176, -150, 60, 15), (-6, 170, -20, 56, 14),
               (30, 210, -70, 46, 12)])
    d.shape("dark", "M96 48 C120 38 156 46 168 74 C182 104 176 150 160 210 L96 210 C100 170 96 130 92 100 C86 80 84 60 96 48Z")
    d.shape("hero2", "M92 70 C94 92 100 116 112 136 C120 146 126 128 124 110 C120 90 112 74 104 64Z", shadow=False)
    d.stroke("pop", "M106 134 Q114 146 124 128", 3, line=False)
    keel_bill(d)
    d.shape("ring", circle(108, 62, 9.5), shadow=False)
    d.marks("mark", circle(108, 62, 4.4))
    d.marks("light", circle(109.6, 60.4, 1.4))


def toucan_hollow(d: Drawing):
    jungle(d, [(-6, 40, 20, 60, 15), (206, 40, 160, 60, 15), (206, 150, -170, 56, 14), (-6, 150, -10, 56, 14)], "mid")
    d.shape("trunk", "M56 -10 C62 60 60 140 50 210 L158 210 C148 140 146 60 152 -10Z")
    d.stroke("trunk2", "M70 10 Q74 50 70 90 M140 20 Q136 60 140 100 M68 150 Q72 180 66 210 M138 140 Q134 180 140 210", 2.4, line=False)
    d.shape("trunk2", ellipse(108, 110, 30, 36), shadow=False)
    d.shape("hole", ellipse(108, 112, 24, 30), shadow=False)
    # toucan peeking out
    def bird():
        d.shape("dark", "M90 140 C84 112 92 84 108 74 C122 66 136 80 136 104 C136 122 132 138 126 146Z")
        d.shape("hero2", "M92 92 C92 108 96 126 106 136 C114 128 116 110 112 90 C106 84 98 84 92 92Z", shadow=False)
        d.stroke("pop", "M98 134 Q106 140 114 130", 3, line=False)
        group(d, "translate(98 84) scale(.82) translate(-98 -72)", lambda: keel_bill(d))
        d.shape("ring", circle(112, 76, 8), shadow=False)
        d.marks("mark", circle(112, 76, 3.6))
        d.marks("light", circle(113.3, 74.7, 1.2))
    bird()
    d.shape("trunk", "M78 130 C90 144 126 144 138 130 L140 150 H76Z", shadow=False)
    d.shape("trunk2", "M80 136 C94 148 122 148 136 136", line=False, shadow=False)
    for x, y, a in [(150, 160, -20), (150, 160, -60), (150, 160, 10), (58, 60, -160), (58, 60, -120)]:
        d.shape("near", leaf(x, y, 30, 8, a))


# ================================================================ OCEAN HELPERS
def snorkeller(d: Drawing, suit="hero2", fins="pop", skin="dark"):
    """A snorkeller floating face-down, head to the left at (60, 52)."""
    d.limb(skin, "M112 52 L140 46 M112 58 L142 60", 7)
    d.shape(fins, ellipse(150, 42, 11, 4.5), extra='transform="rotate(-14 150 42)"', spot=True)
    d.shape(fins, ellipse(152, 62, 11, 4.5), extra='transform="rotate(10 152 62)"', spot=True)
    d.shape(suit, rrect(66, 46, 52, 18, 9))
    d.limb(suit, "M74 60 Q60 70 46 66", 6)
    d.shape(suit, circle(60, 52, 10))
    d.shape(skin, rrect(48, 49, 12, 9, 3), shadow=False)
    d.shape("light", rrect(50, 51, 8, 5, 2), shadow=False)
    d.stroke(fins, "M66 46 V32", 3)


def diver(d: Drawing, suit="dark", tank="hero2", fins="pop"):
    """The pilot scuba diver, swimming left, centred near (100, 100)."""
    d.stroke(fins, "M84 86 Q60 78 47 99", 2.6)
    d.shape(tank, rrect(78, 80, 46, 15, 7.5), spot=True)
    d.limb(suit, "M128 97 L152 87", 8)
    d.limb(suit, "M130 107 L155 107", 8)
    d.shape(fins, ellipse(166, 81, 14, 5.5), extra='transform="rotate(-24 166 81)"', spot=True)
    d.shape(fins, ellipse(169, 108, 14, 5.5), extra='transform="rotate(4 169 108)"', spot=True)
    d.shape(suit, rrect(60, 93, 74, 21, 10.5))
    d.limb(suit, "M73 111 Q58 119 41 118", 7)
    d.shape(suit, circle(54, 103, 12))
    d.shape(tank, rrect(40, 97, 15, 11, 3.5), shadow=False)
    d.shape("light", rrect(42.5, 99.5, 10, 6, 2), shadow=False)


def deep_water(d: Drawing, bottom=False):
    d.band("sky2", waves(30, 4, 26))
    d.band("far", waves(58, 5, 28))
    d.band("mid", waves(92, 6, 30))
    d.band("near", waves(130, 6, 34))
    d.band("deep", waves(164, 5, 36), line=False)
    if bottom:
        d.band("ground", "M-30 180 Q40 168 80 178 T160 174 T230 176")


# ================================================================ MANTA RAY
MANTA_OUT = ("M100 50 C112 50 120 56 126 64 C146 64 166 72 180 90 C168 96 146 104 128 118 C122 130 112 138 100 138 "
             "C88 138 78 130 72 118 C54 104 32 96 20 90 C34 72 54 64 74 64 C80 56 88 50 100 50Z")
MANTA_BELLY = ("M100 62 C110 62 118 68 122 76 C138 78 154 84 164 92 C150 96 134 104 122 114 C116 124 108 130 100 130 "
               "C92 130 84 124 78 114 C66 104 50 96 36 92 C46 84 62 78 78 76 C82 68 90 62 100 62Z")
MANTA_HORN = "M80 64 C74 56 72 46 76 38 C79 33 84 34 85 38 C83 42 82 46 84 50 C85 55 88 59 89 62Z"


def manta_belly(d: Drawing):
    deep_water(d)
    d.disc("glow", 100, 8, 26)
    rays(d, ((40, 20), (110, 14), (150, 10)))
    for x, y, s in [(40, 150, 0.8), (54, 158, 0.7), (150, 160, 0.8), (164, 152, 0.7)]:
        d.shape("pop", fish(x, y, s), shadow=False)

    def ray():
        d.stroke("hero", "M100 136 Q106 160 98 190", 3)
        d.shape("hero", MANTA_HORN)
        flip(d, lambda: d.shape("hero", MANTA_HORN))
        d.shape("hero", MANTA_OUT)
        d.shape("light", MANTA_BELLY, shadow=False, spot=True)
        d.shape("mark", rrect(82, 54, 36, 7, 3.5), shadow=False)
        gills = ""
        for i in range(5):
            y = 78 + i * 7
            gills += f"M{74 - i * 0.5} {y} q7 2.5 14 0.5 M{126 + i * 0.5} {y} q-7 2.5 -14 0.5 "
        d.stroke("mark", gills, 1.8)
        d.marks("mark", "".join(circle(x, y, r) for x, y, r in [(100, 112, 2.6), (108, 118, 1.8), (92, 104, 2), (114, 104, 1.6),
                                                               (96, 122, 1.6), (62, 92, 1.8)]))
    group(d, "rotate(-8 100 100) translate(0 4)", ray)
    bubbles(d, [(160, 70, 2.5), (166, 58, 3.4)])


def manta_diver(d: Drawing):
    water(d)
    rays(d)
    d.shape("pop", "M30 176 C28 160 36 150 46 150 C56 150 62 160 60 176Z")
    d.stroke("mark", "M36 168 q6 -6 12 0 M40 160 q5 -5 10 0", 1.4, line=False)
    d.limb("hero2", "M160 178 V160 M160 166 L150 154 M160 162 L170 150", 5)

    def ray():
        d.stroke("hero", "M100 136 Q96 160 104 184", 3)
        d.shape("hero", MANTA_HORN)
        flip(d, lambda: d.shape("hero", MANTA_HORN))
        d.shape("hero", MANTA_OUT, spot=True)
        d.shape("light", "M90 66 C78 70 60 76 46 86 C62 84 78 82 92 78Z", shadow=False)
        flip(d, lambda: d.shape("light", "M90 66 C78 70 60 76 46 86 C62 84 78 82 92 78Z", shadow=False))
        d.shape("hero", "M96 126 L100 136 L104 126Z", shadow=False)
        d.stroke("mark", "M100 58 V128", 1.2, line=False)
    group(d, "translate(96 92) scale(.86) rotate(-14) translate(-100 -94)", ray)
    at(d, 150, 140, 0.42, lambda: diver(d), rot=-20)
    bubbles(d, [(116, 118, 2.2), (112, 108, 3), (118, 98, 2)])


# ================================================================ SEA TURTLE
def seaturtle_portrait(d: Drawing):
    water(d, bottom=False)
    rays(d)
    for x, y, s in [(150, 160, 0.8), (164, 168, 0.7), (40, 44, 0.7)]:
        d.shape("pop", fish(x, y, s), shadow=False)

    def t():
        d.shape("hero2", "M168 104 C178 108 186 116 188 128 C178 126 168 120 162 110Z")
        d.shape("flip2", "M96 100 C104 92 118 86 132 84 C124 92 112 100 102 106Z")
        d.shape("hero", "M66 102 C70 72 100 54 134 56 C162 58 182 76 184 98 C170 108 120 114 66 108Z", spot=True)
        d.shape("light", "M66 104 C110 112 160 108 184 98 C182 104 176 108 168 110 C130 116 96 116 70 112Z", shadow=False)
        d.stroke("mark", "M84 80 L104 66 M104 66 L126 61 L148 65 L166 78 M104 66 L108 92 M126 61 L128 94 M148 65 L150 92 "
                         "M78 98 L108 92 L128 94 L150 92 L178 94", 2)
        d.shape("hero2", "M70 92 C62 88 58 86 54 84 L58 104 C62 104 66 106 72 108Z")
        d.shape("hero2", "M84 104 C74 120 60 140 36 156 C30 160 30 166 38 164 C64 156 86 136 100 114Z")
        d.stroke("light", "M80 122 l8 5 M70 134 l8 5 M58 146 l7 4", 1.4, line=False)
        d.shape("hero2", "M60 80 C52 72 38 72 30 78 C22 84 20 94 24 100 C30 106 44 108 58 106 C66 104 68 96 66 88Z")
        d.stroke("light", "M48 77 L54 85 L48 93 M54 85 L64 88 M36 94 L48 93 L54 101", 1.4, line=False)
        d.stroke("mark", "M24 98 Q34 102 46 100", 1.6)
        d.marks("mark", circle(42, 86, 3.4))
        d.marks("light", circle(43.2, 84.8, 1.1))
    group(d, "translate(104 104) scale(.86) translate(-100 -100)", t)
    bubbles(d, [(36, 62, 2.5), (30, 50, 3.4)])


def seaturtle_nesting(d: Drawing):
    d.disc("glow", 150, 44, 16)
    d.marks("light", "".join(circle(x, y, r) for x, y, r in [(30, 50, 1.2), (60, 30, 1), (100, 22, 1.3), (118, 48, 1), (176, 76, 1.1), (44, 76, 0.9)]))
    d.band("far", "M-30 92 H230")
    d.stroke("glow2", "M140 100 H160 M144 106 H156", 2, line=False)
    d.band("mid", waves(110, 2, 26))
    d.shape("light", "M-30 120 Q20 112 60 120 T150 118 T230 120 V128 H-30Z", shadow=False, line=False)
    d.band("ground", "M-30 126 Q60 118 120 126 T230 124")
    tr = ""
    for i in range(7):
        x, y = 30 + i * 9, 132 + i * 6
        tr += f"M{x - 6} {y} l5 -2 M{x + 4} {y + 4} l5 -2 "
    d.stroke("sand2", tr, 2.4)

    def t():
        d.shape("hero2", "M66 160 C54 162 44 168 40 176 C52 178 64 172 74 166Z")
        d.shape("flip2", "M118 148 C130 136 146 130 160 132 C152 142 138 150 124 156Z")
        d.shape("hero2", "M150 146 C156 134 170 128 182 134 C190 138 190 148 184 152 C176 158 164 156 156 154Z")
        d.shape("hero", "M58 164 C60 140 86 126 116 126 C144 126 162 142 164 162 C140 168 84 170 58 164Z", spot=True)
        d.stroke("mark", "M84 136 L104 130 L126 130 L146 140 M104 130 L106 162 M126 130 L128 162 M70 150 L106 146 L128 146 L158 150", 2)
        d.shape("light", "M58 164 C84 170 140 168 164 162 L162 168 C140 174 84 174 60 170Z", shadow=False)
        d.shape("hero2", "M128 160 C144 160 162 168 178 180 C162 186 142 182 124 172Z")
        d.stroke("light", "M144 168 l6 6 M156 172 l5 6", 1.3, line=False)
        d.marks("mark", circle(176, 140, 2.4))
        d.stroke("mark", "M190 146 Q182 150 172 149", 1.4)
    group(d, "translate(100 150) scale(.84) translate(-112 -152)", t)
    d.shape("sand2", "M30 178 Q60 170 90 178 Q60 182 30 178Z", shadow=False, line=False)


# ================================================================ SEAHORSE
SH_TRACK = [(106, 58), (114, 80), (114, 104), (106, 126), (100, 142), (102, 158), (112, 168), (124, 164), (126, 152),
            (118, 147), (113, 153)]
SH_W = [22, 28, 30, 24, 15, 11, 9, 7, 5.5, 4.5, 3.5]


def _interp_w(ws):
    def f(t):
        x = t * (len(ws) - 1)
        i = min(int(x), len(ws) - 2)
        return ws[i] + (ws[i + 1] - ws[i]) * (x - i)
    return f


def seahorse(d: Drawing, spot=True):
    """A seahorse facing left, head at (100, 46), tail curled at the bottom."""
    wf = _interp_w(SH_W)
    d.shape("hero2", "M120 92 C134 94 140 106 136 122 L120 118Z")
    d.stroke("mark", "M122 98 L134 104 M121 106 L136 112 M120 114 L135 119", 1, line=False)
    d.shape("hero", ribbon(SH_TRACK, wf), spot=spot)
    d.shape("hero", ellipse(104, 104, 15, 20), shadow=False)
    rings = ""
    for x, y, nx, ny, t in track(SH_TRACK)[4:64:4]:
        hw = wf(t) / 2
        rings += f"M{x + nx * hw:.1f} {y + ny * hw:.1f} L{x - nx * hw:.1f} {y - ny * hw:.1f} "
    d.stroke("mark", rings, 1.4, line=False)
    d.shape("hero", "M86 46 C88 32 106 28 116 38 C122 44 122 56 114 62 L98 66 C90 62 86 54 86 46Z")
    d.shape("hero", "M92 50 L66 57 C61 58 59 61 60 65 L64 67 C70 66 76 64 94 62Z")
    d.shape("hero", "M96 34 L98 22 L102 31 L106 22 L108 32 L112 26 L112 36Z", shadow=False)
    d.shape("hero2", "M112 60 C118 58 124 62 122 70 C118 68 114 66 112 62Z", shadow=False)
    d.shape("light", circle(100, 46, 4.6), shadow=False)
    d.marks("mark", circle(99.5, 46, 2.4))
    d.marks("hero2", "".join(circle(x, y, 1.3) for x, y in [(96, 92), (100, 112), (110, 84), (92, 104), (108, 120), (74, 60)]))


def seagrass(d: Drawing, xs, role="near", h=120):
    for i, x in enumerate(xs):
        k = 1 if i % 2 else -1
        d.shape(role, ribbon([(x, 214), (x + 4 * k, 214 - h * 0.4), (x - 6 * k, 214 - h * 0.75), (x + 4 * k, 214 - h)], 9, 3), line=False)


def seahorse_portrait(d: Drawing):
    water(d, bottom=False)
    rays(d)
    seagrass(d, [20, 34, 168, 182, 194], "near", 110)
    group(d, "translate(108 102) scale(1.04) translate(-100 -100)", lambda: seahorse(d))
    bubbles(d, [(52, 40, 2.5), (44, 30, 3.4), (54, 22, 2)])


def seahorse_pair(d: Drawing):
    water(d)
    rays(d)
    seagrass(d, [16, 186], "near", 120)
    d.shape("near", ribbon([(100, 214), (102, 170), (98, 130), (102, 96)], 8, 3))
    at(d, 62, 104, 0.66, lambda: seahorse(d), flipx=True, ox=110, oy=100)
    at(d, 138, 104, 0.66, lambda: seahorse(d, spot=False), ox=110, oy=100)
    group(d, "translate(100 42) scale(.55)", lambda: d.shape("pop", "M0 -6 C-3 -13 -14 -12 -13 -3 C-12 4 -4 8 0 14 C4 8 12 4 13 -3 C14 -12 3 -13 0 -6Z", spot=True))


# ================================================================ OCTOPUS
OCTO_ARMS = [
    [(76, 112), (52, 120), (30, 114), (22, 100), (28, 90), (36, 94), (34, 100)],
    [(82, 118), (64, 142), (44, 154), (30, 150), (30, 140), (38, 140)],
    [(90, 122), (84, 150), (74, 172), (60, 176), (54, 166), (62, 162)],
    [(97, 124), (98, 152), (104, 172), (116, 174), (118, 164), (110, 162)],
]


def octopus(d: Drawing, arms=True):
    """An octopus facing us, mantle on top, centred near (100, 90)."""
    if arms:
        for k in (1, -1):
            for i, a in enumerate(OCTO_ARMS):
                pts = a if k == 1 else [(200 - x, y) for x, y in a]
                d.shape("hero", ribbon(pts, 15, 3), spot=i % 2 == 0)
                tr = track(pts)
                sk = ""
                for x, y, nx, ny, t in tr[6::5]:
                    w = (15 + (3 - 15) * t) / 2
                    sk += circle(x, y, max(w * 0.42, 1))
                d.shape("hero2", sk, shadow=False, line=False)
    d.shape("hero", "M100 18 C130 18 146 40 144 66 C142 86 132 98 122 106 C128 112 126 122 116 124 L84 124 "
                    "C74 122 72 112 78 106 C68 98 58 86 56 66 C54 40 70 18 100 18Z")
    d.marks("hero2", "".join(circle(x, y, r) for x, y, r in [(86, 40, 2.4), (110, 32, 2), (122, 52, 2.6), (92, 58, 1.8),
                                                            (76, 60, 2), (106, 70, 2.2), (130, 74, 1.6), (70, 80, 1.6)]))
    for x in (80, 120):
        d.shape("hero", circle(x, 98, 12), shadow=False)
        d.shape("light", circle(x, 99, 8.5), shadow=False)
        d.marks("mark", rrect(x - 6, 97, 12, 4.4, 2.2))
        d.stroke("hero", f"M{x - 12} 92 Q{x} 82 {x + 12} 92", 3, line=False)


def octopus_portrait(d: Drawing):
    water(d, bottom=False)
    rays(d)
    bubbles(d, [(154, 30, 2.5), (162, 20, 3.4), (40, 30, 2.2)])
    group(d, "translate(100 104) scale(.98) translate(-100 -100)", lambda: octopus(d))


def octopus_den(d: Drawing):
    water(d)
    rays(d)
    for x, y, s_ in [(150, 46, 0.8), (164, 54, 0.7), (40, 60, 0.7)]:
        d.shape("hero2", fish(x, y, s_), shadow=False)
    d.shape("dark", "M-30 210 L-30 130 C-10 110 20 106 40 116 C52 96 80 88 100 96 C124 86 156 94 166 114 C188 106 220 112 230 126 V210Z")
    d.shape("hole", ellipse(100, 146, 44, 30), shadow=False)
    group(d, "translate(100 122) scale(.72) translate(-100 -84)", lambda: octopus(d, arms=False))
    d.shape("dark", "M40 150 C60 166 140 166 160 150 L176 210 H24Z", shadow=False)
    d.stroke("deep", "M50 160 C70 172 130 172 150 160", 2, line=False)
    arms = [[(84, 156), (66, 160), (50, 152), (44, 138), (52, 132), (58, 138)],
            [(116, 156), (136, 162), (152, 156), (158, 142), (150, 136), (144, 142)],
            [(92, 160), (86, 176), (72, 186), (60, 182), (62, 174)],
            [(108, 160), (116, 178), (132, 186), (142, 178), (136, 172)]]
    for i, a in enumerate(arms):
        d.shape("hero", ribbon(a, 12, 3), spot=i < 2)
        sk = "".join(circle(x, y, max((12 - 9 * t) * 0.2, 1)) for x, y, nx, ny, t in track(a)[8::5])
        d.shape("hero2", sk, shadow=False, line=False)
    d.marks("deep", circle(20, 150, 3) + circle(180, 150, 3.4) + circle(170, 190, 2.4) + circle(30, 186, 2.6))
    d.shape("pop", "M176 132 C170 116 176 102 188 100 C192 112 188 124 186 136Z")
    d.shape("pop2", "M16 132 C8 120 10 108 20 104 C26 114 26 124 22 136Z M30 128 C28 114 34 104 44 102 C46 114 42 124 36 132Z", shadow=False)


# ================================================================ WHALE SHARK
WS_HEAD = "M22 104 C24 80 58 64 100 64 C142 64 176 80 178 104 C178 126 150 142 100 142 C50 142 22 126 22 104Z"


def whaleshark_face(d: Drawing):
    deep_water(d)
    rays(d, ((30, 18), (120, 14)))
    for x, y, s in [(56, 160, 0.8), (70, 168, 0.7), (130, 166, 0.8), (144, 158, 0.7), (100, 172, 0.7)]:
        d.shape("pop", fish(x, y, s, right=x > 100), shadow=False)
    d.shape("hero", "M86 72 L100 26 L120 72Z")
    d.shape("hero", "M40 118 C26 128 12 144 6 162 C22 156 40 142 54 130Z")
    flip(d, lambda: d.shape("hero", "M40 118 C26 128 12 144 6 162 C22 156 40 142 54 130Z"))
    d.shape("hero", WS_HEAD, spot=True)
    clipped(d, WS_HEAD, lambda: d.shape("light", "M0 112 C40 132 160 132 200 112 V160 H0Z", shadow=False))
    d.shape("mark", "M38 108 C62 120 138 120 162 108 C156 124 132 134 100 134 C68 134 44 124 38 108Z", shadow=False)
    d.shape("mouth", "M50 114 C70 122 130 122 150 114 C144 124 126 129 100 129 C74 129 56 124 50 114Z", shadow=False, line=False)
    spots = ""
    for r, (y, xs) in enumerate([(74, range(56, 150, 10)), (82, range(42, 162, 10)), (91, range(34, 170, 10)), (100, range(30, 172, 11))]):
        for x in xs:
            if abs(x - 100) > 4 or r < 3:
                spots += circle(x + (5 if r % 2 else 0), y, 2.1)
    clipped(d, WS_HEAD, lambda: d.marks("light", spots))
    d.stroke("hero2", "M60 70 Q100 62 140 70", 1.4, line=False)
    for x in (30, 170):
        d.shape("light", circle(x, 102, 4), shadow=False)
        d.marks("mark", circle(x, 102, 2.2))
    d.shape("remora", "M84 146 C90 142 110 142 116 146 C110 150 90 150 84 146Z", shadow=False)


WS_BODY = "M34 116 C60 104 96 92 136 92 C160 92 178 98 184 108 C186 116 182 124 170 128 C140 136 96 136 64 128 C52 124 42 122 34 116Z"


def whaleshark_snorkel(d: Drawing):
    d.band("sky2", waves(22, 3, 26))
    d.band("far", waves(44, 4, 28))
    d.band("mid", waves(84, 6, 30))
    d.band("near", waves(130, 6, 34))
    d.band("deep", waves(168, 5, 36), line=False)
    rays(d, ((40, 16), (120, 12)))
    at(d, 96, 34, 0.34, lambda: snorkeller(d), ox=100, oy=52)
    bubbles(d, [(70, 46, 1.6), (66, 54, 2.2)])

    def shark():
        d.shape("hero", "M40 118 L18 80 C22 98 24 110 28 120 L16 150 C28 138 36 128 44 122Z")
        d.shape("hero", "M98 94 L112 68 L126 93Z")
        d.shape("hero", "M62 108 L66 96 L76 104Z")
        d.shape("hero", "M140 126 L122 154 L156 130Z")
        d.shape("hero", WS_BODY, spot=True)
        d.shape("light", "M60 124 C96 134 140 134 172 126 C150 134 110 138 76 132 C68 130 64 128 60 124Z", shadow=False)
        dots = ""
        for c, x in enumerate(range(48, 178, 9)):
            for y in range(94, 128, 8):
                dots += circle(x + (4 if (y // 8) % 2 else 0), y + (c % 2) * 2, 1.7)
        lines = " ".join(f"M{x} 90 L{x - 4} 126" for x in range(70, 150, 18))
        clipped(d, WS_BODY, lambda: (d.marks("light", dots), d.stroke("light", lines, 1.2, line=False),
                                     d.stroke("hero2", "M60 112 C100 104 140 102 180 106", 1.4, line=False)))
        d.stroke("mark", "M150 104 V122 M155 103 V122 M160 103 V122", 1.4)
        d.stroke("mark", "M184 112 C178 115 172 115 166 113", 2)
        d.marks("mark", circle(170, 104, 1.8))
    group(d, "translate(0 18)", shark)
    for x, y, s in [(150, 60, 0.6), (162, 66, 0.5)]:
        d.shape("pop", fish(x, y, s, right=True), shadow=False)


# ================================================================ HAMMERHEAD
HAMMER = ("M28 60 C26 52 36 48 50 50 C66 52 82 50 92 46 C96 44 104 44 108 46 C118 50 134 52 150 50 C164 48 174 52 172 60 "
          "C170 66 162 68 150 68 C134 68 118 72 112 80 L88 80 C82 72 66 68 50 68 C38 68 30 66 28 60Z")
HH_BODY = "M88 76 C82 96 84 120 90 140 C94 152 98 162 100 174 C102 162 106 152 110 140 C116 120 118 96 112 76Z"
HH_FIN = "M90 98 C80 106 70 118 64 132 C76 130 86 122 94 112Z"
HH_TAIL = "M100 170 C96 180 88 192 78 198 C92 196 100 188 102 180 C106 188 110 192 116 194 C110 184 106 176 102 168Z"


def hammerhead(d: Drawing, body="hero", under="light", eye="mark", detail=True):
    """A hammerhead seen from below, head at the top, centred near (100, 110)."""
    d.shape(body, HH_TAIL)
    d.shape(body, HH_FIN)
    flip(d, lambda: d.shape(body, HH_FIN))
    d.shape(body, "M92 148 L84 160 L96 154Z M108 148 L116 160 L104 154Z", shadow=False)
    d.shape(body, HH_BODY + HAMMER, spot=detail)
    if detail:
        d.shape(under, "M92 80 C88 98 90 120 94 138 C96 148 99 158 100 166 C101 158 104 148 106 138 C110 120 112 98 108 80Z", shadow=False)
        d.stroke(eye, "M86 62 Q100 68 114 62", 2)
        d.stroke(eye, "M86 84 l-4 2 M86 88 l-4 2 M86 92 l-4 2 M114 84 l4 2 M114 88 l4 2 M114 92 l4 2", 1.3, line=False)
    d.marks(eye, circle(30, 59, 2.6) + circle(170, 59, 2.6))


def hammerhead_portrait(d: Drawing):
    deep_water(d)
    rays(d, ((26, 16), (120, 12)))
    for x, y, s in [(40, 150, 0.8), (54, 158, 0.7), (150, 40, 0.7), (164, 48, 0.6)]:
        d.shape("pop", fish(x, y, s, right=True), shadow=False)
    group(d, "translate(100 100) scale(.86) rotate(28) translate(-100 -112)", lambda: hammerhead(d))
    bubbles(d, [(30, 70, 2.5), (24, 58, 3.4)])


HH_SIL = ("M94 74 C90 100 92 130 97 160 L99 172 L90 196 L101 186 L110 194 L101 170 L103 160 C108 130 110 100 106 74Z "
          "M93 98 L74 124 L96 112Z M107 98 L126 124 L104 112Z")


def hammerhead_school(d: Drawing):
    deep_water(d)
    rays(d, ((30, 16), (110, 12), (160, 8)))
    for x, y, s, r, role in [(40, 50, 0.3, 30, "far2"), (150, 34, 0.26, 36, "far2"), (98, 58, 0.34, 32, "far2"),
                             (166, 90, 0.36, 28, "school"), (30, 108, 0.38, 34, "school"), (76, 118, 0.48, 30, "school"),
                             (134, 132, 0.52, 34, "school")]:
        at(d, x, y, s, lambda role=role: d.shape(role, HH_SIL + HAMMER), rot=r, ox=100, oy=110)
    at(d, 56, 172, 0.36, lambda: diver(d), rot=-24)
    bubbles(d, [(36, 150, 2.2), (32, 140, 3), (38, 130, 2)])


# ================================================================ JELLYFISH
NETTLE_BELL = ("M48 86 C48 50 72 32 100 32 C128 32 152 50 152 86 Q146 92 139 88 Q132 94 126 89 Q119 95 113 90 "
               "Q106 96 100 90 Q94 96 87 90 Q81 95 74 89 Q68 94 61 88 Q54 92 48 86Z")


def frill(pts, w, amp=3, n=14):
    """A ruffled ribbon: an oral arm with wavy edges."""
    return ribbon(pts, lambda t: w * (1 - 0.7 * t) + amp * math.sin(t * n * math.pi), n=10)


def jelly_nettle(d: Drawing):
    deep_water(d)
    d.marks("light", "".join(circle(x, y, r) for x, y, r in [(30, 60, 1.2), (170, 40, 1), (160, 150, 1.3), (40, 160, 1), (180, 110, 1.1), (20, 110, 0.9)]))
    tent = ""
    for i, x in enumerate(range(54, 150, 10)):
        k = 1 if i % 2 else -1
        tent += f"M{x} 88 C{x + 10 * k} 120 {x - 10 * k} 150 {x + 6 * k} 196 "
    d.stroke("hero", tent, 1.8)
    d.shape("hero2", frill([(92, 84), (82, 112), (92, 142), (80, 170), (88, 194)], 14), spot=True)
    d.shape("hero2", frill([(108, 84), (120, 114), (108, 144), (122, 172), (114, 196)], 14), spot=True)
    d.shape("hero2", frill([(100, 86), (100, 118), (94, 150), (102, 180)], 10), shadow=False)
    d.shape("hero", NETTLE_BELL)
    clipped(d, NETTLE_BELL, lambda: d.stroke("mark", " ".join(f"M100 30 L{100 + 70 * math.sin(math.radians(a)):.1f} {30 + 70 * math.cos(math.radians(a)):.1f}"
                                                              for a in range(-60, 61, 12)), 2.4, line=False))
    d.shape("light", "M64 60 C70 46 84 38 98 38 C86 44 74 52 68 64Z", shadow=False)


def golden_jelly(d: Drawing, x, y, s, spot=False):
    def draw():
        for dx in (-8, -3, 3, 8):
            d.shape("hero2", ribbon([(dx, 8), (dx * 1.2, 18), (dx, 26)], 5, 3), shadow=False)
            d.shape("hero2", circle(dx, 28, 3.4), shadow=False)
        d.shape("hero", "M-18 8 C-18 -10 -8 -18 0 -18 C8 -18 18 -10 18 8 Q9 12 0 9 Q-9 12 -18 8Z", spot=spot)
        d.marks("light", circle(-6, -6, 1.6) + circle(4, -10, 1.3) + circle(8, -2, 1.5) + circle(-2, 2, 1.2))
    group(d, f"translate({x} {y}) scale({s})", draw)


def jelly_lake(d: Drawing):
    d.band("sky2", "M-30 18 H230")
    d.band("far", waves(40, 4, 26))
    d.band("mid", waves(84, 5, 30))
    d.band("near", waves(130, 5, 34))
    d.band("deep", waves(170, 5, 36), line=False)
    rays(d, ((30, 16), (100, 12), (150, 10)))
    at(d, 100, 26, 0.42, lambda: snorkeller(d, suit="dark", fins="dark"), ox=100, oy=52)
    for x, y, s in [(38, 74, 0.7), (154, 70, 0.8), (64, 120, 1.25), (138, 124, 1.5), (100, 84, 0.9), (30, 150, 0.8),
                    (172, 160, 0.7), (96, 168, 1.0), (122, 52, 0.55)]:
        golden_jelly(d, x, y, s, spot=s > 1.2)


# ================================================================ CLOWNFISH
def clown_side(d: Drawing):
    """A clownfish facing left, centred near (94, 92)."""
    d.shape("hero", "M84 74 C90 60 108 60 116 74Z")
    d.shape("hero", "M128 92 L148 76 C146 86 146 98 148 108 L128 96Z")
    d.shape("hero", "M56 92 C60 76 80 70 100 72 C114 73 124 80 132 92 C124 104 114 110 100 111 C80 112 60 108 56 92Z", spot=True)
    for st in ["M72 76 C67 86 67 98 72 108 L80 110 C76 98 76 86 80 73Z",
               "M98 72 C93 84 93 100 98 111 L108 110 C104 100 104 84 108 73Z",
               "M124 82 C121 88 121 96 124 102 L130 96 L130 88Z"]:
        d.shape("light", st, shadow=False)
        d.stroke("mark", st, 1.2, line=False)
    d.stroke("mark", "M86 68 C92 62 106 62 114 70 M146 78 C145 86 145 98 146 106", 2, line=False)
    d.shape("hero", "M84 100 C80 108 82 114 88 118 C90 112 92 106 92 102Z")
    d.marks("mark", circle(64, 88, 3))
    d.marks("light", circle(63, 87, 1))


def clownfish_face(d: Drawing):
    water(d, bottom=False)
    for i in range(13):
        a = math.radians(-180 + i * 15)
        x0, y0 = 100 + 40 * math.cos(a) * 0.6, 196
        x1, y1 = 100 + 92 * math.cos(a), 150 + 70 * math.sin(a) * 0.6
        d.limb("pop", f"M{x0:.1f} {y0} Q{(x0 + x1) / 2 + 8:.1f} {(y0 + y1) / 2 + 10:.1f} {x1:.1f} {y1:.1f}", 9, shadow=i % 2 == 0)
        d.shape("pop2", circle(x1, y1, 5), shadow=False, line=False)

    def fishy():
        d.shape("hero", "M84 46 C90 30 110 30 116 46 L110 60 H90Z")
        d.stroke("mark", "M86 44 C92 32 108 32 114 44", 2.4, line=False)
        for k in (1, -1):
            def finn():
                d.shape("hero", "M66 104 C48 94 30 98 24 112 C38 118 54 120 68 116Z")
                d.stroke("mark", "M26 111 C30 100 44 97 54 100", 2.4, line=False)
            finn() if k == 1 else flip(d, finn)
        d.shape("hero", "M84 150 L76 174 L96 156Z M116 150 L124 174 L104 156Z")
        d.shape("light", ellipse(100, 102, 44, 56))
        d.stroke("mark", ellipse(100, 102, 44, 56), 2.4)
        d.shape("hero", ellipse(100, 106, 30, 44), spot=True)
        d.stroke("mark", ellipse(100, 106, 30, 44), 1.6, line=False)
        d.shape("hero", "M88 154 C94 162 106 162 112 154 C106 158 94 158 88 154Z", shadow=False)
        for x in (76, 124):
            d.shape("hero2", circle(x, 88, 11), shadow=False)
            d.marks("mark", circle(x, 88, 7))
            d.marks("light", circle(x + 2.5, 85, 2.2))
        d.shape("hero2", ellipse(100, 126, 9, 6), shadow=False)
        d.marks("mark", ellipse(100, 126, 5, 3.2))
    group(d, "translate(0 -6)", fishy)
    bubbles(d, [(160, 40, 2.5), (166, 28, 3.4), (156, 18, 2)])


def clownfish_family(d: Drawing):
    water(d)
    rays(d)
    d.limb("coral", "M156 182 V152 M156 162 L144 148 M156 158 L170 142 M144 148 L140 136 M170 142 L176 132", 5)
    d.shape("anem2", "M30 196 C30 172 60 164 100 164 C140 164 170 172 170 196Z")

    def tentacles(front):
        for i in range(13):
            if (i % 2 == 0) != front:
                continue
            bx = 40 + i * 10
            tx = 18 + i * 13.7 + (5 if i % 2 else -5)
            ty = 118 + abs(i - 6) * 4.5 + (10 if i % 2 else 0)
            d.limb("anem", f"M{bx} 176 Q{(bx + tx) / 2:.1f} {(176 + ty) / 2 + 6:.1f} {tx:.1f} {ty:.1f}", 8, shadow=False)
            d.shape("anem", circle(tx, ty, 6.5), shadow=front, spot=front and i % 4 == 0)
            d.shape("tip", circle(tx, ty - 1.4, 3.2), shadow=False, line=False)
    tentacles(False)
    at(d, 80, 112, 0.7, lambda: clown_side(d), ox=94, oy=92)
    at(d, 132, 132, 0.5, lambda: clown_side(d), flipx=True, ox=94, oy=92)
    tentacles(True)
    at(d, 110, 66, 0.4, lambda: clown_side(d), ox=94, oy=92, rot=-10)
    bubbles(d, [(40, 60, 2.5), (34, 48, 3.4)])


# ================================================================ CONCEPTS
SLOTH ={"hero": "#A38A6C", "hero2": "#EFE4CC", "mark": "#3B2B1F", "fur2": "#7E6850", "claw": "#2E241B", "light": "#FFFFFF"}
JAGUAR = {"hero": "#E2A447", "hero2": "#C9B23A", "mark": "#24190F", "light": "#FBF1DC", "rose": "#C98A35", "pop": "#C8786A",
          "croc": "#6B6B3A"}
MACAW = {"hero": "#D62D2D", "hero2": "#F6C329", "green": "#3F9A4E", "blue": "#2A6BBE", "beak": "#F1E6CF", "iris": "#F3E2A0",
         "mark": "#1E1A1A", "light": "#FFFFFF"}
CLAY = {**MACAW, "clay": "#D99A6C", "clay2": "#B9704A"}
CAPY = {"hero": "#A6744B", "hero2": "#7E5234", "mark": "#2E2018", "light": "#FFFFFF", "bird": "#F2C230"}
CAPY_WET = {**CAPY, "lily": "#5E9A4A", "lily2": "#3F7A34", "pop": "#F2A7C3"}
ALPACA = {"hero": "#C8955F", "hero2": "#E2BB86", "mark": "#3A2A20", "pop": "#E0457B", "pop2": "#F6C445"}
ALPACA_T = {**ALPACA, "fur2": "#A67845", "stone": "#9C9384", "stone2": "#5A5048", "dark": "#3A2A20"}
CONDOR = {"dark": "#1D1D22", "hero": "#A0675A", "hero2": "#6E3A36", "light": "#FFFFFF", "beak": "#E8DCC2", "mark": "#201414",
          "wing": "#E9E9EC"}
TORT = {"hero": "#6B6152", "hero2": "#948A77", "mark": "#3A3229", "light": "#B9AF99"}
TORT_C = {**TORT, "trunk": "#8A5A3C", "pad": "#6E9A48", "pad2": "#3F6A2A", "pop": "#F6C445"}
BOOBY = {"hero": "#7D5E45", "hero2": "#33B4D8", "light": "#FFFFFF", "head": "#E3D8CA", "beak": "#7F98A6", "eye": "#F2D23C",
         "mark": "#2A2018", "lava": "#3E3A40", "lava2": "#2A272C"}
IGUANA = {"hero": "#3E3D42", "hero2": "#B9473A", "green": "#6E9A4C", "mark": "#151518", "light": "#F4F1EA", "eye": "#C9B26A"}
IGUANA_L = {**IGUANA, "hero": "#2C2B30", "lava": "#77706E", "lava2": "#5A5452", "crab": "#E5482C", "crab2": "#C23A22"}
SEALION = {"hero": "#8B7763", "hero2": "#B8A48C", "mark": "#231D19", "light": "#FFFFFF", "flipper": "#5E4E40", "rock": "#6E6A66"}
SEALION_B = {**SEALION, "wood": "#5DB7A9", "wood2": "#2E7A70"}
BOTO = {"hero": "#E99AAA", "hero2": "#F8D3DA", "mark": "#3A2228"}
FROG_BLUE = {"hero": "#2F6FD3", "hero2": "#1F4CA0", "mark": "#0F1626", "light": "#FFFFFF"}
FROG_RED = {"hero": "#D8312A", "hero2": "#2C5DB8", "mark": "#1A1012", "light": "#FFFFFF", "brom": "#4F9A55", "brom2": "#7CC06A",
            "bromtip": "#D24A6A", "water": "#9FD6E6"}
TOUCAN_K = {"dark": "#16171D", "hero2": "#F6D02F", "bill": "#8CC63F", "bill2": "#F08A24", "bill3": "#D62B3F", "bill4": "#3D8FD6",
            "ring": "#9AD24A", "mark": "#0E0E12", "pop": "#D62B3F", "light": "#FFFFFF"}
TOUCAN_H = {**TOUCAN_K, "trunk": "#8C6A4A", "trunk2": "#6A4E36", "hole": "#2A1C14"}

SOUTH = [
    Concept("sloth-hanging", "animal-sloth", "Hanging around", sloth_hanging, overrides=SLOTH,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "dark"), ("hero", "near")],
            fixes={"near": ["deep", "mid"], "far": ["mid", "sky2"]}),
    Concept("sloth-cecropia", "animal-sloth", "Mum & baby", sloth_cecropia, overrides=SLOTH,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "dark"), ("hero", "near"), ("hero", "mid")],
            fixes={"near": ["deep", "mid"], "far": ["sky2", "mid"], "mid": ["near", "deep"]}),
    Concept("jaguar-face", "animal-jaguar", "Jaguar", jaguar_face, overrides=JAGUAR,
            checks=[("hero", "sky"), ("hero", "near")], fixes={"near": ["deep", "mid", "dark"], "sky": ["sky2"]}),
    Concept("jaguar-pantanal", "animal-jaguar", "Pantanal riverbank", jaguar_riverbank, overrides=JAGUAR,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero", "far"), ("hero", "ground")],
            fixes={"glow": ["glow2", "light", "#E07A5F"], "ground": ["near", "mid", "deep"], "far": ["mid", "near", "deep"]}),
    Concept("macaw-portrait", "animal-macaw", "Scarlet macaw", macaw_portrait, overrides=MACAW,
            checks=[("hero", "sky"), ("hero", "near")], fixes={"near": ["deep", "mid"], "sky": ["sky2", "far"]}),
    Concept("macaw-claylick", "animal-macaw", "Clay lick", macaw_claylick, overrides=CLAY,
            checks=[("hero", "clay"), ("hero", "near"), ("near", "clay"), ("hero", "sky")],
            fixes={"near": ["deep", "mid", "dark"]}),
    Concept("capybara-friend", "animal-capybara", "Capybara & friend", capybara_friend, overrides=CAPY,
            checks=[("hero", "sky"), ("hero", "glow"), ("hero", "far"), ("hero", "ground"), ("bird", "sky"), ("bird", "glow")],
            fixes={"glow": ["light", "far", "#E07A5F"], "ground": ["near", "mid", "deep"], "far": ["mid", "near"]}),
    Concept("capybara-wetland", "animal-capybara", "Wetland swim", capybara_wetland, NO_GOLD, CAPY_WET,
            checks=[("hero", "mid"), ("hero", "far"), ("hero", "near"), ("lily", "near")],
            fixes={"far": ["deep", "dark"], "mid": ["far", "sky2"], "near": ["mid", "deep"]}),
    Concept("alpaca-portrait", "animal-alpaca", "Alpaca", alpaca_portrait, overrides=ALPACA,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "mid"), ("hero2", "sky")],
            fixes={"far": ["mid", "near", "deep"], "mid": ["near", "deep"]}),
    Concept("alpaca-terraces", "animal-alpaca", "Andean terraces", alpaca_terraces, overrides=ALPACA_T,
            checks=[("hero", "near"), ("hero", "sky"), ("hero", "far"), ("stone", "far"), ("mid", "far")],
            fixes={"near": ["deep", "mid", "#5E9C6A"], "mid": ["near", "deep"], "far": ["sky2", "mid"]}),
    Concept("condor-portrait", "animal-andean-condor", "Andean condor", condor_portrait, overrides=CONDOR,
            checks=[("hero", "sky"), ("hero", "far"), ("dark", "sky"), ("dark", "far")],
            fixes={"sky": ["sky2", "far", "glow2"], "far": ["mid", "sky2", "light"]}),
    Concept("condor-andes", "animal-andean-condor", "Over the Andes", condor_soaring, overrides=CONDOR,
            checks=[("dark", "sky"), ("dark", "far"), ("dark", "glow")],
            fixes={"sky": ["sky2", "glow2", "light"], "far": ["mid", "light"]}),
    Concept("tortoise-portrait", "animal-giant-tortoise", "Giant tortoise", tortoise_portrait, overrides=TORT,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "glow"), ("hero2", "ground"), ("hero2", "sky")],
            fixes={"far": ["mid", "near", "sky2"], "ground": ["near", "mid", "far"], "sky": ["sky2", "glow2"]}),
    Concept("tortoise-cactus", "animal-giant-tortoise", "Saddleback & cactus", tortoise_cactus, overrides=TORT_C,
            checks=[("hero", "sky"), ("hero", "mid"), ("hero", "ground"), ("hero2", "sky"), ("pad", "sky"), ("pad", "far")],
            fixes={"mid": ["far", "near"], "ground": ["far", "near"], "sky": ["sky2", "glow2"], "far": ["sky2", "mid", "near"]}),
    Concept("booby-feet", "animal-blue-footed-booby", "Happy feet", booby_feet, overrides=BOOBY,
            checks=[("light", "sky"), ("hero2", "lava"), ("hero2", "sky"), ("light", "far"), ("hero", "far")],
            fixes={"sky": ["sky2", "far"], "far": ["mid", "near"]}),
    Concept("booby-dance", "animal-blue-footed-booby", "Booby dance", booby_dance, overrides=BOOBY,
            checks=[("light", "sky"), ("hero2", "lava"), ("light", "far"), ("hero", "glow"), ("light", "glow")],
            fixes={"sky": ["sky2", "far"], "far": ["mid", "near"], "glow": ["glow2", "#E07A5F", "far"]}),
    Concept("iguana-portrait", "animal-marine-iguana", "Marine iguana", iguana_portrait, overrides=IGUANA,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "mid"), ("light", "sky")],
            fixes={"sky": ["sky2", "glow2", "far"], "far": ["mid", "sky2", "glow2"], "mid": ["far", "near"]}),
    Concept("iguana-lava", "animal-marine-iguana", "Basking on lava", iguana_lava, overrides=IGUANA_L,
            checks=[("hero", "lava"), ("hero", "mid"), ("crab", "lava")], fixes={"mid": ["far", "near"]}),
    Concept("sealion-portrait", "animal-sea-lion", "Sea lion", sealion_portrait, overrides=SEALION,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "mid"), ("hero", "glow")],
            fixes={"far": ["mid", "near", "sky2"], "mid": ["near", "far", "deep"], "glow": ["glow2", "light"]}),
    Concept("sealion-bench", "animal-sea-lion", "Bench nap", sealion_bench, overrides=SEALION_B,
            checks=[("hero", "wood"), ("hero", "ground"), ("hero", "far"), ("wood", "ground"), ("hero", "sky")],
            fixes={"ground": ["near", "far", "mid"], "far": ["mid", "near"]}),
    Concept("pinkdolphin-portrait", "animal-pink-river-dolphin", "Boto", pinkdolphin_portrait, UNDERWATER, BOTO,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "far")]),
    Concept("pinkdolphin-amazon", "animal-pink-river-dolphin", "Amazon surfacing", pinkdolphin_amazon, overrides=BOTO,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "far"), ("hero", "sky")],
            fixes={"mid": ["near", "far", "deep"], "near": ["deep", "mid"], "far": ["deep", "near"]}),
    Concept("dartfrog-blue", "animal-poison-dart-frog", "Blue dart frog", dartfrog_blue, overrides=FROG_BLUE,
            checks=[("hero", "near"), ("hero", "sky"), ("hero", "mid"), ("hero2", "near")],
            fixes={"near": ["mid", "far"], "mid": ["far", "near"]}),
    Concept("dartfrog-bromeliad", "animal-poison-dart-frog", "Strawberry frog", dartfrog_bromeliad, overrides=FROG_RED,
            checks=[("hero", "brom"), ("hero", "sky"), ("brom2", "sky"), ("brom", "mid")],
            fixes={"mid": ["far", "deep"], "sky": ["sky2"]}),
    Concept("toucan-rainbow", "animal-toucan", "Rainbow bill", toucan_rainbow, overrides=TOUCAN_K,
            checks=[("dark", "sky"), ("bill", "sky"), ("bill", "near"), ("dark", "near"), ("bill4", "sky")],
            fixes={"near": ["mid", "far"], "sky": ["sky2", "far", "glow2"]}),
    Concept("toucan-hollow", "animal-toucan", "Tree hollow", toucan_hollow, overrides=TOUCAN_H,
            checks=[("trunk", "sky"), ("trunk", "mid"), ("bill", "sky"), ("trunk", "near")],
            fixes={"mid": ["far", "near"], "near": ["mid", "far"], "sky": ["sky2", "far"]}),
]

MANTA = {"hero": "#24313F", "light": "#F1F3F5", "mark": "#121A22", "pop": "#FFC857"}
MANTA_D = {"hero": "#24313F", "light": "#E9EEF2", "mark": "#0E151C", "pop": "#FF7A5C"}
SEATURTLE = {"hero": "#6E6A3A", "hero2": "#A69A62", "flip2": "#857A48", "mark": "#3B361C", "light": "#EDE5C6"}
NESTING = {"hero": "#5E5A36", "hero2": "#8C8256", "flip2": "#6F6744", "mark": "#2E2A16", "light": "#E8E0C2", "sand2": "#C9AE7C"}
SEAHORSE = {"hero": "#F2A23A", "hero2": "#F8D27E", "mark": "#9A4B1A", "light": "#FFFFFF", "pop": "#FF6F91"}
OCTO = {"hero": "#D8613C", "hero2": "#F6B48E", "mark": "#3A140C", "light": "#FFF6EE", "hole": "#0B1520", "pop": "#F2789A", "pop2": "#FFC857"}
WHALESHARK = {"hero": "#3F5E78", "hero2": "#6F8DA6", "light": "#EEF3F6", "mark": "#132029", "mouth": "#24343F", "remora": "#8A99A6"}
HAMMER_C = {"hero": "#7B8794", "light": "#D9E0E6", "mark": "#1C252E", "school": "#22323F", "far2": "#4D6272"}
NETTLE = {"hero": "#E8893A", "hero2": "#F8D9B0", "mark": "#B4552A", "light": "#FFF3E6"}
GOLDJELLY = {"hero": "#F2B84B", "hero2": "#E39A3A", "light": "#FFF4D6", "pop": "#FF7A5C"}
CLOWN = {"hero": "#F26B1F", "hero2": "#F9B27A", "light": "#FFFFFF", "mark": "#151515", "pop": "#B98AE0", "pop2": "#E0C3F5"}
CLOWN_F = {"hero": "#F26B1F", "light": "#FFFFFF", "mark": "#151515", "anem": "#E7849F", "anem2": "#B65A78", "tip": "#F9D3DE",
           "coral": "#FFC857"}

OCEANS = [
    Concept("manta-belly", "animal-manta-ray", "Manta from below", manta_belly, UNDERWATER, MANTA,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "far"), ("hero", "deep")],
            fixes={"deep": ["near", "mid"], "near": ["mid", "far"]}),
    Concept("manta-diver", "animal-manta-ray", "Manta & diver", manta_diver, UNDERWATER, MANTA_D,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "far")], fixes={"near": ["mid", "far"]}),
    Concept("seaturtle-portrait", "animal-sea-turtle", "Green turtle", seaturtle_portrait, UNDERWATER, SEATURTLE,
            checks=[("hero", "mid"), ("hero", "near"), ("hero2", "mid"), ("hero2", "near"), ("hero", "far")],
            fixes={"near": ["deep", "far"], "mid": ["far", "sky2"]}),
    Concept("seaturtle-nesting", "animal-sea-turtle", "Nesting night", seaturtle_nesting, NO_GOLD, NESTING,
            checks=[("hero", "ground"), ("hero2", "ground"), ("hero", "far"), ("hero", "mid")],
            fixes={"ground": ["light", "far"], "mid": ["far", "near"]}),
    Concept("seahorse-portrait", "animal-seahorse", "Seahorse", seahorse_portrait, UNDERWATER, SEAHORSE,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "far"), ("hero", "sky2")],
            fixes={"far": ["mid", "near"], "sky2": ["far", "mid"]}),
    Concept("seahorse-pair", "animal-seahorse", "Seahorse sweethearts", seahorse_pair, UNDERWATER, SEAHORSE,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "far")], fixes={"far": ["mid", "near"]}),
    Concept("octopus-portrait", "animal-octopus", "Octopus", octopus_portrait, UNDERWATER, OCTO,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "far"), ("hero", "sky2")],
            fixes={"near": ["deep", "far"], "mid": ["deep", "far"]}),
    Concept("octopus-den", "animal-octopus", "Octopus den", octopus_den, UNDERWATER, OCTO,
            checks=[("hero", "dark"), ("hero", "hole"), ("hero", "deep"), ("hero", "mid")], fixes={"mid": ["far", "near"]}),
    Concept("whaleshark-face", "animal-whale-shark", "Whale shark", whaleshark_face, UNDERWATER, WHALESHARK,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "far"), ("hero", "sky2")],
            fixes={"hero": ["#6F8FAA", "#7E9DB8"], "far": ["sky2", "mid"]}),
    Concept("whaleshark-snorkel", "animal-whale-shark", "Snorkel with a giant", whaleshark_snorkel, UNDERWATER, WHALESHARK,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "far")], fixes={"hero": ["#6F8FAA", "#7E9DB8"]}),
    Concept("hammerhead-portrait", "animal-hammerhead-shark", "Hammerhead", hammerhead_portrait, UNDERWATER, HAMMER_C,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "far"), ("hero", "sky2")],
            fixes={"hero": ["#4F5D6A", "#9AA6B2"], "far": ["mid", "sky2"]}),
    Concept("hammerhead-school", "animal-hammerhead-shark", "Hammerhead school", hammerhead_school, UNDERWATER, HAMMER_C,
            checks=[("school", "mid"), ("school", "near"), ("far2", "far"), ("far2", "sky2")],
            fixes={"school": ["dark", "deep"], "far2": ["mid", "near", "deep"]}),
    Concept("jellyfish-nettle", "animal-jellyfish", "Sea nettle", jelly_nettle, UNDERWATER, NETTLE,
            checks=[("hero", "far"), ("hero", "mid"), ("hero", "near"), ("hero2", "near"), ("hero2", "deep")],
            fixes={"far": ["mid", "near", "deep"], "mid": ["near", "deep"]}),
    Concept("jellyfish-lake", "animal-jellyfish", "Jellyfish lake", jelly_lake, UNDERWATER, GOLDJELLY,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "far"), ("hero", "deep")],
            fixes={"far": ["mid", "near"], "mid": ["near", "deep"]}),
    Concept("clownfish-face", "animal-clownfish", "Clownfish hello", clownfish_face, UNDERWATER, CLOWN,
            checks=[("hero", "mid"), ("hero", "near"), ("light", "far"), ("light", "mid"), ("pop", "near")],
            fixes={"far": ["mid", "near"], "pop": ["#D96BB8", "#8E5BC9"]}),
    Concept("clownfish-anemone", "animal-clownfish", "Bubble-tip home", clownfish_family, UNDERWATER, CLOWN_F,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "anem"), ("anem", "near"), ("anem", "deep")],
            fixes={"near": ["far", "deep"], "anem": ["#F2A7C3", "#C45C86"]}),
]

CONCEPTS = SOUTH + OCEANS
