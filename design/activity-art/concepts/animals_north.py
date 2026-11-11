"""North American & Arctic animals: a bold portrait and a habitat scene for each of 22 animals."""
import math

from _common import Concept, Drawing, cloud, fish, circle, ellipse, waves, hills, rrect, group  # noqa: F401
from artkit import _lum

_uid = [0]


# ================================================================ helpers (copied / adapted from wildlife.py)
def _id(prefix):
    _uid[0] += 1
    return f"{prefix}{_uid[0]}"


def clipped(d: Drawing, path: str, fn):
    """Draw fn() clipped to `path` (rings on a tail, mottling on a narwhal)."""
    cid = _id("anclip")
    tag = f'<clipPath id="{cid}"><path d="{path}"/></clipPath><g clip-path="url(#{cid})">'
    d.raw(tag, tag)
    fn()
    d.raw("</g>", "</g>")


def flip(d: Drawing, fn, cx=100):
    group(d, f"translate({2 * cx} 0) scale(-1 1)", fn)


def place(d: Drawing, fn, x, y, s=1.0, ox=100, oy=100, mirror=False):
    """Draw fn (drawn around (ox, oy)) at (x, y), scaled by s, optionally mirrored."""
    sx = -s if mirror else s
    call = (lambda: fn(d)) if fn.__code__.co_argcount else fn
    group(d, f"translate({x} {y}) scale({sx} {s}) translate({-ox} {-oy})", call)


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


def birds(d: Drawing, pts, role="dark"):
    s = " ".join(f"M{x} {y} q{3 * k} {-3 * k} {6 * k} 0 q{3 * k} {-3 * k} {6 * k} 0" for x, y, k in pts)
    d.stroke(role, s, 1.8)


def drop(x, y, r):
    return f"M{x:.1f} {y - r * 1.7:.1f} Q{x + r:.1f} {y:.1f} {x:.1f} {y + r:.1f} Q{x - r:.1f} {y:.1f} {x:.1f} {y - r * 1.7:.1f}Z"


def pine(d: Drawing, x, y, h, role="near", shadow=True, line=True):
    w = h * 0.36
    d.shape(role, f"M{x} {y - h} L{x + w * 0.6} {y - h * 0.62} L{x + w * 0.35} {y - h * 0.62} L{x + w * 0.85} {y - h * 0.3} "
                  f"L{x + w * 0.5} {y - h * 0.3} L{x + w} {y - h * 0.06} L{x - w} {y - h * 0.06} L{x - w * 0.5} {y - h * 0.3} "
                  f"L{x - w * 0.85} {y - h * 0.3} L{x - w * 0.35} {y - h * 0.62} L{x - w * 0.6} {y - h * 0.62}Z",
            shadow=shadow, line=line)


def pines(d: Drawing, items, y, role="near", shadow=False, line=True):
    for x, h in items:
        pine(d, x, y, h, role, shadow, line)


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


def splash(d: Drawing, x, y, w=24, role="light"):
    d.stroke(role, f"M{x - w} {y} q{w * 0.25} {-w * 0.3} {w * 0.5} 0 M{x + w * 0.5} {y} q{w * 0.25} {-w * 0.3} {w * 0.5} 0", 2.4)
    for dx, dy, r in [(-w * 0.7, -10, 2.6), (-w * 0.3, -16, 2.2), (w * 0.3, -15, 2.4), (w * 0.7, -9, 2.2), (0, -20, 2)]:
        d.shape(role, drop(x + dx, y + dy, r), shadow=False)


def ripples(d: Drawing, pts, role="light", w=2.2):
    d.stroke(role, " ".join(f"M{x} {y} q{k * 4} {-k * 3} {k * 8} 0" for x, y, k in pts), w)


def foam(d: Drawing, x0, x1, y, r=7, role="water2"):
    x, s, i = x0, "", 0
    while x <= x1:
        s += circle(x, y - (i % 2) * 3, r * (0.8 + 0.3 * (i % 3) / 2))
        x += r * 1.3
        i += 1
    d.shape(role, s)


def is_night(d: Drawing):
    return d.paper and _lum(d.c["sky"]) < 0.12


def stars(d: Drawing, pts, always=False):
    """Little stars, only in a dark sky (papercut) or always in line style if asked."""
    if is_night(d) or (always and not d.paper):
        s = "".join(f"M{x} {y - r * 2} L{x + r * 0.6} {y - r * 0.6} L{x + r * 2} {y} L{x + r * 0.6} {y + r * 0.6} "
                    f"L{x} {y + r * 2} L{x - r * 0.6} {y + r * 0.6} L{x - r * 2} {y} L{x - r * 0.6} {y - r * 0.6}Z"
                    for x, y, r in pts)
        d.marks("light", s)


def aurora(d: Drawing, y=56, colour="#7FE3B5", colour2="#A88BEA"):
    """Northern lights: soft translucent ribbons in a dark papercut sky, two pen lines in line style."""
    a = (f"M-30 {y + 10} C20 {y - 30} 60 {y + 30} 110 {y - 6} S190 {y - 26} 230 {y - 4} L230 {y + 18} "
         f"C190 {y} 160 {y + 30} 110 {y + 16} C66 {y + 6} 30 {y + 40} -30 {y + 36}Z")
    b = (f"M-30 {y - 14} C30 {y - 40} 70 {y - 6} 120 {y - 30} S200 {y - 40} 230 {y - 28} L230 {y - 16} "
         f"C190 {y - 26} 160 {y - 4} 120 {y - 16} C70 {y - 30} 30 {y - 4} -30 {y}Z")
    if is_night(d):
        d.raw(f'<g opacity=".55"><path d="{a}" fill="{colour}"/></g><g opacity=".4"><path d="{b}" fill="{colour2}"/></g>', "")
    elif not d.paper:
        d.raw("", f'<path d="M-10 {y + 8} C30 {y - 20} 70 {y + 24} 110 {y - 2} S190 {y - 20} 210 {y - 2}" fill="none" '
                  f'stroke="{d.c["spot"]}" stroke-width="3" stroke-linecap="round" opacity=".8"/>'
                  f'<path d="M-10 {y - 6} C30 {y - 30} 70 {y - 4} 120 {y - 24} S190 {y - 34} 210 {y - 22}" fill="none" '
                  f'stroke="{d.c["spot"]}" stroke-width="2" stroke-linecap="round" opacity=".6"/>')


def snowflakes(d: Drawing, pts, role="light"):
    d.marks(role, "".join(circle(x, y, r) for x, y, r in pts))


def peaks(d: Drawing, role="far", snow=True, y=120):
    d.band(role, f"M-30 {y + 4} L14 {y - 22} L34 {y - 10} L70 {y - 48} L100 {y - 18} L128 {y - 40} L160 {y - 8} L186 {y - 24} L230 {y}")
    if snow:
        d.shape("light", f"M70 {y - 48} L80 {y - 37} L74 {y - 38} L69 {y - 33} L64 {y - 38} L60 {y - 37}Z "
                         f"M128 {y - 40} L137 {y - 31} L132 {y - 32} L127 {y - 28} L122 {y - 32} L119 {y - 31}Z", shadow=False)


def bubbles(d: Drawing, pts):
    for x, y, r in pts:
        d.stroke("light", circle(x, y, r), 2)


def rays(d: Drawing):
    d.raw('<g opacity=".18" fill="#fff"><path d="M50 0 L72 0 L110 200 L88 200Z"/><path d="M122 0 L134 0 L174 200 L162 200Z"/></g>', "")


def underwater(d: Drawing, bottom=True):
    d.band("sky2", waves(36, 5, 26))
    d.band("far", waves(60, 5, 28))
    d.band("mid", waves(90, 6, 30))
    rays(d)
    d.band("near", waves(128, 6, 34))
    d.band("deep", waves(158, 5, 36), line=False)
    if bottom:
        d.band("ground", "M-30 176 Q40 164 80 174 T160 170 T230 172")


# ================================================================ BLACK BEAR
BLACK_BEAR = ("M40 112 C38 94 50 82 70 80 C92 78 116 80 132 84 C140 86 146 88 150 90 "
              "L172 101 C178 104 182 106 182 110 C182 113 179 115 175 115 L160 117 C156 121 152 122 148 122 "
              "L149 150 L134 150 L133 130 C116 133 96 133 82 130 L80 150 L65 150 L61 131 C48 129 40 123 40 112Z")


def black_bear(d: Drawing):
    """Side-on black bear walking right, feet on y=150: straight back, tall ears, tan muzzle."""
    d.shape("mark", rrect(115, 122, 13, 28, 5))
    d.shape("mark", rrect(86, 120, 13, 30, 5))
    d.shape("mark", ellipse(146, 85, 5.5, 7.5), shadow=False)
    d.shape("hero", ellipse(153, 83, 6, 8.5))
    d.shape("hero", BLACK_BEAR)
    d.shape("hero2", "M160 100 L172 102 C178 104 181 107 181 110 C181 113 178 114 175 114 L161 115 C157 111 157 104 160 100Z",
            shadow=False, spot=True)
    d.marks("mark", ellipse(180, 109, 3, 2.6))
    d.marks("light", circle(156, 96, 1.7))
    d.stroke("light", "M136 150 l2 -3 M141 150 l2 -3 M146 150 l2 -3", 1.2, line=False)


def blackbear_portrait(d: Drawing):
    d.disc("glow", 104, 92, 50)
    pines(d, [(20, 58), (36, 72), (166, 70), (184, 56)], 140, "mid")
    d.band("far", hills(138, 6), line=False)
    place(d, black_bear, 98, 154, 1.04, 110, 150)
    d.band("ground", hills(158, 4))
    d.band("deep", hills(182, 3, 30), line=False)


def bear_cub(d: Drawing):
    """A black bear cub hugging a trunk at x 100-112, looking at us."""
    d.shape("hero", circle(74, 70, 6))
    d.shape("hero", circle(95, 69, 6))
    d.shape("hero", ellipse(90, 110, 19, 24), extra='transform="rotate(-8 90 110)"')
    d.shape("hero", circle(85, 84, 15))
    d.shape("hero2", ellipse(86, 91, 8, 6), shadow=False, spot=True)
    d.marks("mark", ellipse(86, 87.5, 3.4, 2.4) + circle(79, 80, 1.9) + circle(92, 80, 1.9))
    d.stroke("mark", "M86 90 V93 M82 95 Q86 97 90 95", 1.2)
    d.limb("hero", "M92 100 C102 96 110 94 116 96", 9)
    d.limb("hero", "M96 128 C104 128 110 132 116 134", 10)


def blackbear_cub_tree(d: Drawing):
    d.band("far", "M-30 120 L10 96 L36 108 L76 66 L106 102 L130 84 L164 110 L230 100")
    d.shape("light", "M76 66 L86 78 L80 77 L75 82 L70 77 L66 79Z", shadow=False)
    pines(d, [(10, 50), (28, 64), (150, 52), (170, 66), (190, 50)], 150, "mid")
    d.band("mid", hills(146, 5), line=False)
    # the pine the cub has climbed
    for y, w in [(46, 26), (70, 34), (96, 40)]:
        d.shape("near", f"M108 {y - 30} L{108 + w} {y + 8} L108 {y}Z M108 {y - 30} L{108 - w} {y + 8} L108 {y}Z")
    d.limb("bark", "M108 210 L108 18", 13)
    d.stroke("dark", "M104 150 v8 M111 166 v10 M105 186 v8", 1.4, line=False)
    bear_cub(d)
    d.band("ground", hills(178, 4))
    d.band("deep", hills(192, 3, 20), line=False)


# ================================================================ GRIZZLY
GRIZZLY = ("M44 116 C42 100 52 92 66 90 C82 88 94 86 102 80 C110 66 128 58 142 66 C150 71 154 78 157 85 "
           "C161 82 167 82 171 86 C174 90 176 93 181 95 C187 97 190 103 186 107 L173 111 C167 117 159 120 153 120 "
           "L155 152 L138 152 L136 133 C120 137 100 137 86 134 L84 152 L68 152 L64 136 C51 134 44 126 44 116Z")
GRIZZLY_HUMP = ("M96 84 C108 66 128 58 142 66 C150 71 154 78 157 85 C156 98 152 110 150 122 C140 112 128 100 112 94 "
                "C104 90 98 88 96 84Z")


def grizzly(d: Drawing, mouth_open=False):
    """Side-on grizzly facing right, feet on y=152: shoulder hump, dished face, small round ears, long claws."""
    d.shape("mark", rrect(120, 124, 15, 28, 6))
    d.shape("mark", rrect(92, 122, 15, 30, 6))
    d.shape("hero", circle(163, 81, 5.5))
    d.shape("hero", GRIZZLY)
    d.shape("hero2", GRIZZLY_HUMP, shadow=False, spot=True)
    d.shape("hero2", "M170 94 C174 94 178 94 182 95 C187 97 188 102 185 105 L173 108 C169 104 168 98 170 94Z", shadow=False)
    if mouth_open:
        d.shape("mark", "M168 110 L186 106 C186 114 178 122 166 120Z", shadow=False)
        d.shape("pop2", "M170 112 L182 109 C180 114 176 117 170 117Z", shadow=False, line=False)
    d.marks("mark", ellipse(187, 101, 3, 2.6) + circle(166, 93, 1.8))
    d.stroke("light", "M141 152 l3 3 M146 152 l3 3 M151 152 l3 3 M71 152 l3 3 M76 152 l3 3", 1.6)


def grizzly_portrait(d: Drawing):
    d.disc("glow", 64, 62, 24)
    peaks(d, "far", True, 116)
    d.band("mid", "M-30 140 L30 118 L70 130 L120 112 L170 128 L230 116")
    place(d, grizzly, 96, 154, 1.04, 112, 152)
    d.band("near", hills(160, 4))
    d.band("deep", hills(182, 3, 30), line=False)


def salmon(x, y, s=1.0, a=0.0):
    """A salmon centred on (x, y), nose pointing at angle a (degrees, 0 = right)."""
    body = (f"M-16 0 C-10 -6 6 -8 16 -2 C19 0 19 1 16 3 C6 8 -10 6 -16 0Z "
            f"M-14 0 L-24 -7 L-22 0 L-24 7Z")
    return body, f"translate({x} {y}) rotate({a}) scale({s})"


def salmon_shape(d: Drawing, x, y, s=1.0, a=0.0, spot=True):
    body, tf = salmon(x, y, s, a)
    group(d, tf, lambda: (d.shape("pop", body, spot=spot), d.marks("mark", circle(11, -1, 1.3)),
                          d.stroke("pop2", "M-6 2 C0 4 8 3 13 1", 1.4, line=False)))


def grizzly_falls(d: Drawing):
    d.disc("glow", 150, 40, 14)
    peaks(d, "far", False, 84)
    pines(d, [(4, 54), (20, 70), (36, 50), (128, 50), (146, 66), (164, 52), (182, 70), (198, 56)], 100, "deep")
    d.band("mid", "M-30 98 L230 98", line=False)
    d.band("water", "M-30 102 Q100 96 230 102")
    d.stroke("water2", "M70 108 H100 M150 108 H186", 2.2)
    place(d, lambda: grizzly(d, mouth_open=True), 116, 134, 0.98, 110, 152, mirror=True)
    # lip of the falls, covering the bear's paws
    d.shape("water", "M-30 122 Q100 116 230 122 L230 138 L-30 138Z")
    d.stroke("water2", "M20 128 H50 M120 127 H160", 2.2)
    d.shape("water", "M-30 136 L230 136 L230 176 L-30 176Z")
    d.stroke("water2", " ".join(f"M{x} {142 + (i * 7) % 10} V{168 - (i * 5) % 10}" for i, x in enumerate(range(-6, 210, 14))), 2.2)
    d.shape("near", "M-30 180 L-30 128 Q-4 122 14 132 L22 180Z M230 180 L230 126 Q206 120 188 130 L182 180Z")
    salmon_shape(d, 30, 104, 1.15, -62)
    salmon_shape(d, 70, 150, 0.85, -40, spot=False)
    foam(d, -10, 210, 176, 7, "water2")
    d.band("water", "M-30 184 Q100 178 230 184", line=False)


# ================================================================ POLAR BEAR
POLAR_HEAD = ("M100 40 C126 40 146 54 148 78 C150 96 142 110 134 122 C126 140 114 150 100 150 C86 150 74 140 66 122 "
              "C58 110 50 96 52 78 C54 54 74 40 100 40Z")


def polar_portrait(d: Drawing):
    aurora(d, 52)
    stars(d, [(30, 50, 1.6), (160, 34, 1.4), (178, 70, 1.2), (46, 30, 1.1)])
    d.band("far", "M-30 150 L10 130 L40 142 L70 124 L100 146 L230 140", line=False)
    d.shape("hero2", "M24 210 C26 168 56 138 100 138 C144 138 174 168 176 210Z")
    d.shape("hero", "M30 210 C32 172 60 146 100 146 C140 146 168 172 170 210Z", shadow=False)
    for cx in (60, 140):
        d.shape("hero", circle(cx, 52, 12))
        d.shape("hero2", circle(cx, 53, 6), shadow=False, spot=True)
    d.shape("hero", POLAR_HEAD)
    d.shape("hero2", "M100 98 C116 98 128 110 128 126 C128 140 116 148 100 148 C84 148 72 140 72 126 C72 110 84 98 100 98Z", shadow=False)
    d.shape("hero", "M100 102 C112 102 122 112 122 124 C122 136 112 142 100 142 C88 142 78 136 78 124 C78 112 88 102 100 102Z", shadow=False, line=False)
    d.marks("mark", "M88 112 C88 106 112 106 112 112 C112 120 104 124 100 126 C96 124 88 120 88 112Z")
    d.stroke("mark", "M100 126 V132 M90 134 Q100 140 110 134", 2)
    d.marks("mark", circle(80, 86, 3.4) + circle(120, 86, 3.4))
    d.marks("light", circle(81, 85, 1) + circle(121, 85, 1))


POLAR = ("M38 112 C36 92 50 82 70 82 C94 80 116 84 132 90 C142 93 150 97 158 100 C164 99 170 100 176 104 "
         "C182 106 186 110 183 114 L170 117 C164 119 158 119 153 117 L149 121 L151 150 L136 150 L134 131 "
         "C118 134 96 134 82 131 L80 150 L65 150 L61 133 C47 131 38 124 38 112Z")


def polar_bear(d: Drawing):
    """Side-on polar bear facing right, feet on y=150: long neck, small head and ears, high rump."""
    d.shape("hero2", rrect(115, 124, 14, 26, 5))
    d.shape("hero2", rrect(86, 122, 14, 28, 5))
    d.shape("hero", circle(163, 97, 4.2))
    d.shape("hero", POLAR)
    d.shape("hero2", "M60 128 C74 132 100 134 120 132 C110 128 88 126 60 128Z", shadow=False, line=False)
    d.marks("mark", ellipse(184, 110.5, 2.8, 2.4) + circle(170, 104, 1.7))
    d.stroke("mark", "M174 115 Q178 116 181 114", 1.2)


def polar_floe(d: Drawing):
    aurora(d, 50)
    stars(d, [(24, 70, 1.4), (172, 30, 1.4), (150, 64, 1.1), (60, 26, 1.2)])
    d.disc("glow", 156, 50, 14)
    d.shape("ice", "M8 120 L22 92 L40 86 L52 104 L64 120Z")
    d.shape("ice2", "M40 86 L52 104 L64 120 L48 120 L50 102Z", shadow=False, line=False)
    d.band("far", waves(118, 2, 30))
    d.band("mid", waves(136, 3, 34))
    d.shape("ice", "M22 160 C18 150 28 142 60 142 L150 142 C176 142 186 150 180 160 C174 168 150 170 100 170 C60 170 28 168 22 160Z")
    d.shape("ice2", "M24 162 C40 170 160 170 178 162 C174 168 150 172 100 172 C60 172 30 170 24 162Z", shadow=False, line=False)
    place(d, polar_bear, 100, 146, 0.9, 110, 150)
    d.band("near", waves(176, 4, 36))
    ripples(d, [(30, 188, 1.6), (150, 186, 1.6)])


# ================================================================ MOOSE
ANTLER_PALM = ("M92 70 C74 74 46 74 28 64 C16 58 12 46 14 32 L21 38 L22 24 L29 34 L32 20 L38 32 L44 18 L49 32 "
               "L56 20 L59 36 L67 28 L67 44 C74 52 82 58 92 62Z")


def moose_portrait(d: Drawing):
    d.disc("glow", 100, 56, 30)
    pines(d, [(8, 60), (26, 74), (174, 74), (192, 60)], 150, "mid")
    d.band("far", hills(150, 5), line=False)
    # neck and shoulders
    d.shape("hero3", "M66 128 C56 160 44 190 40 210 H160 C156 190 144 160 134 128Z")

    def antlers():
        d.shape("antler", ANTLER_PALM, spot=True)
        flip(d, lambda: d.shape("antler", ANTLER_PALM, spot=True))
    group(d, "translate(100 70) scale(.9) translate(-100 -70)", antlers)
    for side in (1, -1):
        g = (lambda: d.shape("hero", leaf(80, 82, 28, 8, 200)))
        if side == 1:
            g()
        else:
            flip(d, g)
    # long face, bulbous muzzle, dewlap
    d.shape("hero", "M90 154 C88 172 92 188 100 196 C108 188 112 172 110 154Z")
    d.shape("hero", "M100 62 C114 62 122 70 122 86 C122 104 128 118 132 134 C136 152 122 164 100 164 "
                    "C78 164 64 152 68 134 C72 118 78 104 78 86 C78 70 86 62 100 62Z")
    d.shape("hero2", "M100 120 C118 120 130 128 131 142 C132 156 120 163 100 163 C80 163 68 156 69 142 C70 128 82 120 100 120Z",
            shadow=False)
    d.marks("mark", ellipse(89, 148, 4, 6, ) + ellipse(111, 148, 4, 6))
    d.marks("mark", circle(84, 96, 3.4) + circle(116, 96, 3.4))
    d.marks("light", circle(85, 95, 1) + circle(117, 95, 1))


MOOSE = ("M40 98 C38 86 48 78 62 78 C84 76 104 76 116 70 C126 62 138 62 146 70 C152 76 156 82 160 88 "
         "L182 102 C189 106 189 115 182 117 C177 119 172 117 168 114 L160 112 C155 112 151 110 149 107 "
         "C149 116 147 124 141 128 C124 132 94 132 76 128 C60 124 42 112 40 98Z")
MOOSE_ANTLER = ("M150 84 C138 80 122 78 108 70 C102 66 100 60 102 54 L108 58 L108 48 L115 54 L117 42 L123 50 L127 38 "
                "L132 48 L138 38 L141 50 L148 44 L148 56 C152 64 156 74 158 82Z")


def moose(d: Drawing):
    """Side-on bull moose facing right; hooves at y=170. Hump, long legs, overhanging muzzle, dewlap, palm antler."""
    for x0, x1 in [(120, 122), (66, 62)]:
        d.limb("hero3", f"M{x0} 120 L{x1} 168", 8)
    group(d, "translate(12 4)", lambda: d.shape("antler2", MOOSE_ANTLER))
    d.shape("hero", leaf(150, 82, 18, 5, -150))
    d.shape("antler", MOOSE_ANTLER, spot=True)
    for x0, x1 in [(136, 138), (80, 76)]:
        d.limb("hero2", f"M{x0} 120 C{x0 + 2} 140 {x1} 150 {x1} 168", 9)
    d.shape("hero", MOOSE)
    d.shape("hero", "M150 108 C150 120 152 130 157 136 C160 128 160 118 157 110Z", shadow=False)
    d.shape("hero2", "M170 100 L182 102 C189 106 189 115 182 117 C177 119 172 117 168 114Z", shadow=False)
    d.marks("mark", circle(161, 94, 1.8) + ellipse(184, 107, 2.4, 1.6))


def moose_lake(d: Drawing):
    d.disc("glow", 48, 58, 18)
    peaks(d, "far", True, 112)
    pines(d, [(8, 40), (22, 52), (36, 38), (164, 44), (180, 56), (196, 40)], 118, "near")
    d.band("mid", "M-30 116 L230 116", line=False)
    place(d, moose, 100, 150, 1.0, 110, 150)
    d.band("water", "M-30 140 Q100 134 230 140")
    d.stroke("water2", "M30 150 H70 M120 148 H170 M60 162 H100 M140 166 H176", 2.4)
    ripples(d, [(62, 140, 1.2), (114, 140, 1.2)], "water2")
    d.band("deep", hills(184, 3), line=False)


# ================================================================ ELK
def elk_antler(d: Drawing, ox=0.0, oy=0.0, role="antler"):
    def pt(x, y):
        return f"{x + ox} {y + oy}"
    d.limb(role, f"M{pt(122, 76)} C{pt(108, 60)} {pt(90, 46)} {pt(66, 34)}", 5.5)
    d.limb(role, f"M{pt(114, 68)} L{pt(124, 48)} M{pt(102, 57)} L{pt(108, 34)} M{pt(90, 48)} L{pt(92, 26)} "
                 f"M{pt(78, 41)} L{pt(74, 22)} M{pt(120, 74)} L{pt(138, 66)}", 4)


def elk_portrait(d: Drawing):
    d.disc("glow", 156, 132, 24)
    peaks(d, "far", True, 150)
    d.band("mid", hills(168, 5), line=False)
    elk_antler(d, -10, 8, "antler2")
    d.shape("hero2", "M24 210 C30 170 52 134 84 110 C94 102 104 96 114 92 L140 108 C130 120 120 138 114 158 "
                     "C110 176 110 194 112 210Z")
    d.shape("hero2", "M112 150 L104 160 L114 158 L108 172 L116 166 Z M118 128 L110 136 L120 136Z", shadow=False, line=False)
    d.shape("hero", leaf(124, 80, 20, 6, 196))
    elk_antler(d)
    d.shape("hero", "M140 88 L164 76 C166 80 162 84 156 86 L144 94Z")
    d.shape("mark", "M150 70 L165 75 L144 90Z", shadow=False)
    d.shape("hero", "M112 96 C112 84 120 76 130 72 L158 50 C164 46 171 50 168 57 L156 72 C150 82 140 92 130 98 "
                    "C122 102 112 102 112 96Z")
    d.marks("mark", circle(132, 78, 2.2) + ellipse(166, 53, 1.8, 1.4))
    d.stroke("light", "M176 46 q6 -4 4 -10 M182 56 q8 -2 8 -10 M178 66 q8 2 12 -4", 2)


ELK = ("M44 102 C42 90 50 84 62 84 C84 82 108 82 124 84 C130 78 136 70 142 62 C146 54 150 48 156 46 "
       "L176 56 C181 58 181 64 176 66 L163 67 C159 72 155 80 151 92 C149 100 147 106 145 112 "
       "C130 118 96 118 80 116 C60 114 46 110 44 102Z")


def elk(d: Drawing):
    """Side-on bull elk facing right, hooves at y=160: tan body, dark neck, pale rump, swept-back antlers."""
    d.limb("hero3", "M128 112 L132 158", 6)
    d.limb("hero3", "M64 108 L60 158", 6)
    elk_antler_side(d, -6, 4, "antler2")
    d.limb("hero2", "M140 110 L142 158", 6.5)
    d.limb("hero2", "M76 110 C80 128 72 140 72 158", 7)
    d.shape("hero", ELK)
    d.shape("hero2", "M124 84 C130 78 136 70 142 62 C146 54 150 48 156 46 L162 50 C158 62 154 72 151 92 "
                     "C149 100 147 106 145 112 C138 114 132 110 128 102 C124 96 122 90 124 84Z", shadow=False, spot=True)
    d.shape("light", "M44 102 C42 90 50 84 60 84 C63 92 63 104 59 113 C51 111 45 107 44 102Z", shadow=False)
    d.shape("hero", leaf(154, 50, 14, 4.5, -160), shadow=False)
    elk_antler_side(d)
    d.marks("mark", circle(162, 55, 1.6) + circle(178, 61, 1.6))


def elk_antler_side(d: Drawing, ox=0, oy=0, role="antler"):
    d.limb(role, f"M{156 + ox} {48 + oy} C{150 + ox} {32 + oy} {138 + ox} {20 + oy} {114 + ox} {12 + oy}", 4)
    d.limb(role, f"M{152 + ox} {38 + oy} L{164 + ox} {30 + oy} M{144 + ox} {28 + oy} L{150 + ox} {14 + oy} "
                 f"M{132 + ox} {20 + oy} L{134 + ox} {6 + oy} M{156 + ox} {46 + oy} L{168 + ox} {42 + oy}", 3)


def elk_meadow(d: Drawing):
    d.disc("glow", 40, 62, 18)
    peaks(d, "far", True, 122)
    pines(d, [(150, 44), (164, 56), (180, 42), (194, 50)], 132, "mid")
    d.band("mid", hills(132, 5), line=False)
    d.band("ground", hills(150, 6))
    place(d, elk, 98, 164, 1.0, 110, 158)
    d.band("near", hills(170, 4))
    for x in (20, 50, 140, 170):
        d.shape("pop", circle(x, 178, 2.6), shadow=False)
    d.band("deep", hills(188, 3, 30), line=False)


# ================================================================ GREY WOLF
WOLF_HEAD = ("M100 56 C114 56 126 62 134 72 L148 34 C151 29 157 30 158 36 L158 88 C166 100 172 114 170 128 "
             "C162 136 150 140 142 146 C132 158 116 168 100 172 C84 168 68 158 58 146 C50 140 38 136 30 128 "
             "C28 114 34 100 42 88 L42 36 C43 30 49 29 52 34 L66 72 C74 62 86 56 100 56Z")


def wolf_portrait(d: Drawing):
    d.disc("glow", 100, 70, 46)
    pines(d, [(10, 70), (30, 88), (170, 88), (190, 70)], 180, "deep")
    d.shape("hero", "M30 210 C34 170 62 150 100 150 C138 150 166 170 170 210Z")
    d.shape("hero", WOLF_HEAD)
    d.shape("mark", "M48 42 L56 70 L46 80Z M152 42 L144 70 L154 80Z", shadow=False)
    d.shape("light", "M42 100 C54 112 66 112 78 112 L84 150 C70 150 54 142 34 128 C32 118 36 108 42 100Z "
                     "M158 100 C146 112 134 112 122 112 L116 150 C130 150 146 142 166 128 C168 118 164 108 158 100Z", shadow=False)
    d.shape("light", "M100 100 C112 100 120 112 120 126 C120 144 112 160 100 166 C88 160 80 144 80 126 C80 112 88 100 100 100Z",
            shadow=False, spot=True)
    d.shape("mark", "M100 60 C106 70 108 84 104 102 L96 102 C92 84 94 70 100 60Z", shadow=False)
    d.shape("light", ellipse(78, 84, 8, 4) + ellipse(122, 84, 8, 4), shadow=False)
    d.shape("eye", "M70 96 L86 92 L84 100 Z M130 96 L114 92 L116 100Z", shadow=False)
    d.marks("mark", circle(81, 96, 1.8) + circle(119, 96, 1.8))
    d.marks("mark", "M90 124 C90 118 110 118 110 124 C110 130 104 134 100 134 C96 134 90 130 90 124Z")
    d.stroke("mark", "M100 134 V142 M92 146 Q100 150 108 146", 1.8)


WOLF_SIT = ("M50 168 C46 150 50 132 62 120 C72 108 84 98 94 90 C100 80 104 68 108 58 L106 42 L114 51 L119 41 L122 54 "
            "C128 48 136 40 142 32 C146 28 151 32 148 37 C144 46 140 54 136 60 C132 66 130 70 130 76 "
            "C130 88 128 98 128 108 L130 166 L120 166 L118 124 L113 124 L113 166 L103 166 L102 140 "
            "C96 150 92 160 90 168Z")


def wolf_howl(d: Drawing):
    d.disc("glow", 128, 66, 40)
    stars(d, [(30, 40, 1.6), (54, 62, 1.2), (180, 120, 1.2), (70, 30, 1.1)])
    pines(d, [(10, 62), (28, 80), (46, 56), (178, 70), (196, 56)], 160, "deep")
    d.band("mid", hills(158, 4), line=False)
    d.shape("dark", "M20 210 L36 168 L70 150 L110 160 L150 150 L174 176 L180 210Z")
    d.shape("near", "M70 150 L84 162 L60 172Z", shadow=False, line=False)

    def wolf():
        d.shape("hero", "M56 166 C40 170 24 168 14 160 C10 156 14 152 18 154 C28 158 42 158 54 156Z")
        d.shape("hero2", "M14 160 C10 156 14 152 18 154 L26 157 L22 164Z", shadow=False, line=False)
        d.shape("hero", WOLF_SIT)
        d.shape("hero2", "M130 76 C130 88 128 98 128 108 L122 110 C120 96 120 84 124 72Z", shadow=False)
        d.shape("hero2", "M60 128 C70 120 84 122 90 134 C94 146 90 160 84 166 L58 166 C54 152 54 138 60 128Z", shadow=False)
        d.marks("mark", circle(125, 54, 1.6) + circle(147, 34, 1.8))
    place(d, wolf, 104, 160, 1.02, 100, 168)
    d.stroke("light", "M166 34 q6 -2 8 -8 M170 46 q8 -2 12 -8", 2)


# ================================================================ BALD EAGLE
def eagle_portrait(d: Drawing):
    d.disc("glow", 60, 58, 22)
    peaks(d, "far", True, 150)
    pines(d, [(16, 50), (30, 62), (180, 58), (196, 46)], 172, "mid")
    d.shape("hero", "M10 210 C14 168 40 140 66 128 L120 126 C142 140 150 172 150 210Z")
    d.stroke("hero2", "M30 188 C42 170 56 158 72 152 M64 200 C74 184 88 172 102 168", 2.4, line=False)
    d.shape("light", "M54 140 C50 106 66 76 96 64 C120 54 146 58 160 74 L164 82 C152 90 142 98 134 108 L140 120 "
                     "L128 118 L131 130 L118 126 L118 138 L106 132 L102 144 L92 136 L84 148 L76 138 L68 150 L62 140Z")
    d.shape("pop", "M150 72 C166 66 182 74 188 92 C192 104 188 114 180 118 C180 108 176 102 168 102 L148 104 "
                   "C140 96 142 80 150 72Z", spot=True)
    d.shape("pop", "M146 104 L170 103 C172 110 166 114 158 114 L144 110Z", shadow=False, spot=True)
    d.stroke("mark", "M146 104 L168 103", 1.4)
    d.marks("mark", ellipse(170, 84, 2.4, 1.6))
    d.shape("eye", circle(134, 86, 5.2), shadow=False)
    d.marks("mark", circle(135, 86, 2.4))
    d.marks("eyebrow", "M118 80 C126 74 140 74 150 80 L148 83 C140 79 128 79 120 84Z")


EAGLE_WING = ("M92 92 C76 74 56 56 32 44 C24 40 14 42 8 48 L18 52 L4 60 L18 62 L6 72 L22 70 L14 82 L28 78 "
              "L26 90 L38 84 L40 96 C56 96 74 102 90 112Z")
EAGLE_COVERT = "M92 92 C78 78 60 64 42 54 C40 66 44 78 52 86 C66 92 80 98 90 104Z"


def eagle_flight(d: Drawing):
    d.disc("glow", 160, 46, 16)
    peaks(d, "far", True, 136)
    pines(d, [(6, 44), (20, 56), (34, 42), (162, 46), (178, 58), (194, 44)], 148, "near")
    d.band("water", "M-30 146 L230 146")
    d.stroke("water2", "M24 158 H60 M120 160 H170 M70 172 H110", 2.4)
    d.band("deep", hills(188, 3), line=False)

    def eagle():
        # tail, wings, body, head, talons
        def wing():
            group(d, "rotate(10 92 96)", lambda: (d.shape("hero", EAGLE_WING), d.shape("hero2", EAGLE_COVERT, shadow=False, spot=True)))
        wing()
        flip(d, wing)
        d.shape("light", "M88 120 L78 152 L90 148 L100 156 L110 148 L122 152 L112 120Z")
        d.shape("hero", "M100 74 C114 74 120 90 118 108 C116 122 110 130 100 130 C90 130 84 122 82 108 C80 90 86 74 100 74Z")
        d.limb("pop", "M92 122 L84 140", 4.5)
        d.limb("pop", "M108 122 L116 140", 4.5)
        d.stroke("mark", "M80 140 l-4 4 M84 141 l-2 6 M88 140 l2 5 M112 140 l-2 5 M116 141 l2 6 M120 140 l4 4", 2)
        group(d, "translate(100 72) scale(1.25) translate(-100 -72)", lambda: (
            d.shape("light", "M100 54 C110 54 116 62 116 70 C116 78 112 84 100 86 C88 84 84 78 84 70 C84 62 90 54 100 54Z"),
            d.shape("pop", "M112 63 C121 61 127 66 127 72 C127 77 124 79 120 79 C120 75 118 73 113 73Z", spot=True),
            d.marks("mark", circle(108, 65, 1.7)),
            d.marks("eyebrow", "M102 61 L113 60 L112 62.5 L103 63Z")))
    place(d, eagle, 100, 92, 1.0, 100, 96)


# ================================================================ colours
BLACK_BEAR_C = {"hero": "#2B2A2F", "hero2": "#C49A6C", "mark": "#121115", "bark": "#7A5236"}
GRIZZLY_C = {"hero": "#7E5130", "hero2": "#B68A5C", "mark": "#2B1B10", "pop": "#E0603F", "pop2": "#F29A84",
             "light": "#F3E6CF", "water": "#7CC6E8", "water2": "#E6F6FD"}
POLAR_C = {"hero": "#F7F4EC", "hero2": "#D9D2C2", "mark": "#16171C", "ice": "#A9CFE2", "ice2": "#7FB0C9"}
MOOSE_C = {"hero": "#4B3427", "hero2": "#7B604C", "hero3": "#36261C", "mark": "#16100C", "antler": "#CDAE78", "antler2": "#A88A58",
           "water": "#6FB5D6", "water2": "#DDF0F8"}
ELK_C = {"hero": "#C08E5B", "hero2": "#5C3B25", "hero3": "#3E281A", "mark": "#21160E", "antler": "#A98A60",
         "antler2": "#7E6646", "light": "#F1E4C8", "pop2": "#8A4A3A"}
WOLF_C = {"hero": "#7D8590", "hero2": "#A9AFB8", "mark": "#2E3138", "light": "#F1EFEA", "eye": "#E9A93A"}
EAGLE_C = {"hero": "#4A3122", "hero2": "#6E4A33", "mark": "#1E140D", "light": "#FFFFFF", "pop": "#F4B731",
           "eye": "#F6D348", "eyebrow": "#C9C3B8", "water": "#6FB5D6", "water2": "#DDF0F8"}

SKY_DARK = ["sky2", "far", "mid", "near", "deep"]
NO_GOLD = ["coastal", "meadow", "blush", "dusk"]

CONCEPTS = [
    # black bear
    Concept("blackbear-portrait", "animal-black-bear", "Black bear", blackbear_portrait, overrides=BLACK_BEAR_C,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero", "ground"), ("hero", "mid")],
            fixes={"sky": ["sky2", "far", "glow2"], "mid": ["far", "near"], "ground": ["far", "glow2", "light"]}),
    Concept("blackbear-cub-tree", "animal-black-bear", "Cub up a pine", blackbear_cub_tree, overrides=BLACK_BEAR_C,
            checks=[("hero", "bark"), ("hero", "near"), ("hero", "sky"), ("hero", "far"), ("near", "sky")],
            fixes={"sky": ["sky2", "glow2", "light"], "near": ["mid", "far"], "far": ["sky2", "mid"]}),
    # grizzly
    Concept("grizzly-portrait", "animal-grizzly-bear", "Grizzly", grizzly_portrait, overrides=GRIZZLY_C,
            checks=[("hero", "sky"), ("hero", "ground"), ("hero", "near"), ("hero", "far"), ("hero2", "sky")],
            fixes={"ground": ["light", "far", "mid"], "near": ["deep", "mid"], "sky": ["sky2", "far"], "far": ["sky2", "mid"]}),
    Concept("grizzly-salmon", "animal-grizzly-bear", "Salmon catch", grizzly_falls, NO_GOLD, GRIZZLY_C,
            checks=[("hero", "water"), ("hero", "deep"), ("hero", "sky"), ("pop", "water"), ("water", "near")],
            fixes={"deep": ["near", "mid"], "near": ["deep", "dark"]}),
    # polar bear
    Concept("polarbear-portrait", "animal-polar-bear", "Polar bear", polar_portrait, overrides=POLAR_C,
            checks=[("hero", "sky"), ("hero", "far")],
            fixes={"sky": ["mid", "near", "deep"], "far": ["near", "deep", "mid"]}),
    Concept("polarbear-floe", "animal-polar-bear", "On the ice floe", polar_floe, NO_GOLD, POLAR_C,
            checks=[("hero", "sky"), ("hero", "ice"), ("ice", "mid"), ("hero", "far")],
            fixes={"sky": ["mid", "near", "deep"], "far": ["near", "deep"], "mid": ["near", "deep"]}),
    # moose
    Concept("moose-portrait", "animal-moose", "Moose", moose_portrait, overrides=MOOSE_C,
            checks=[("hero", "glow"), ("hero", "sky"), ("antler", "sky"), ("antler", "glow"), ("hero", "mid")],
            fixes={"glow": ["glow2", "light", "far"], "sky": ["sky2", "far", "mid"], "mid": ["far", "near"]}),
    Concept("moose-lake", "animal-moose", "Moose in the lake", moose_lake, NO_GOLD, MOOSE_C,
            checks=[("hero", "near"), ("hero", "far"), ("hero", "water"), ("antler", "far"), ("antler", "sky")],
            fixes={"near": ["mid", "deep"], "far": ["sky2", "mid"]}),
    # elk
    Concept("elk-bugle", "animal-elk", "Bugling elk", elk_portrait, overrides=ELK_C,
            checks=[("hero", "sky"), ("hero2", "sky"), ("antler", "sky"), ("hero", "glow")],
            fixes={"sky": ["sky2", "far", "mid"], "glow": ["glow2", "near"]}),
    Concept("elk-meadow", "animal-elk", "Elk in the Rockies", elk_meadow, overrides=ELK_C,
            checks=[("hero", "ground"), ("hero", "far"), ("hero", "sky"), ("antler", "sky"), ("antler", "far"), ("hero2", "ground")],
            fixes={"ground": ["mid", "near", "deep"], "far": ["mid", "sky2"], "sky": ["sky2"]}),
    # wolf
    Concept("wolf-portrait", "animal-grey-wolf", "Grey wolf", wolf_portrait, overrides=WOLF_C,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero", "deep"), ("light", "glow")],
            fixes={"glow": ["glow2", "far", "near"], "sky": ["sky2", "far", "glow2"]}),
    Concept("wolf-howl", "animal-grey-wolf", "Howling at the moon", wolf_howl, overrides=WOLF_C,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero", "dark"), ("hero", "deep")],
            fixes={"glow": ["glow2", "light", "far"], "sky": ["sky2", "far"], "deep": ["near", "dark"]}),
    # bald eagle
    Concept("eagle-portrait", "animal-bald-eagle", "Bald eagle", eagle_portrait, overrides=EAGLE_C,
            checks=[("light", "sky"), ("pop", "sky"), ("hero", "far"), ("hero", "mid"), ("light", "far")],
            fixes={"sky": ["sky2", "far", "mid", "near"], "far": ["mid", "near", "deep"], "mid": ["near", "deep"]}),
    Concept("eagle-flight", "animal-bald-eagle", "Eagle over the lake", eagle_flight, NO_GOLD, EAGLE_C,
            checks=[("hero", "sky"), ("light", "sky"), ("hero", "far"), ("light", "far"), ("hero", "near"), ("far", "sky")],
            fixes={"sky": ["sky2", "glow2", "far"], "far": ["mid", "sky2"], "near": ["mid", "deep"]}),
]
