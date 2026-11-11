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
    d.shape(role, s, line=False)


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
GRIZZLY_HUMP = ("M98 82 C108 66 128 58 142 66 C150 71 154 78 157 85 C152 92 146 96 140 94 C132 86 124 80 114 82 "
                "C108 84 102 84 98 82Z")


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
    group(d, "translate(4 2) rotate(-14 154 82)", lambda: flip(d, lambda: d.shape("antler2", MOOSE_ANTLER), cx=154))
    d.shape("hero", leaf(150, 82, 18, 5, -150))
    group(d, "translate(4 2) rotate(12 154 82)", lambda: d.shape("antler", MOOSE_ANTLER, spot=True))
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
    place(d, moose, 90, 160, 0.9, 110, 150)
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
        d.shape("hero2", "M130 76 C130 88 128 98 128 108 L122 110 C120 96 120 84 124 72Z", shadow=False, line=False)
        d.shape("hero", "M60 128 C70 120 84 122 90 134 C94 146 90 160 84 166 L58 166 C54 152 54 138 60 128Z", line=False)
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


# ================================================================ SEA OTTER
def otter_portrait(d: Drawing):
    d.disc("glow", 150, 52, 18)
    d.band("far", "M-30 120 L20 104 L50 112 L90 96 L130 112 L230 106", line=False)
    d.band("mid", waves(124, 3, 30))
    d.shape("hero", "M44 210 C44 164 66 134 100 134 C134 134 156 164 156 210Z")
    d.shape("hero", circle(60, 62, 8) + circle(140, 62, 8))
    d.shape("hero2", "M100 46 C130 46 148 68 148 96 C148 124 128 140 100 140 C72 140 52 124 52 96 C52 68 70 46 100 46Z")
    d.marks("mark", circle(60, 62, 3.5) + circle(140, 62, 3.5))
    d.marks("mark", circle(80, 90, 6) + circle(120, 90, 6))
    d.marks("light", circle(82, 88, 1.8) + circle(122, 88, 1.8))
    d.shape("light", circle(91, 120, 11) + circle(109, 120, 11), shadow=False)
    d.marks("mark", "M89 104 C89 98 111 98 111 104 C111 110 104 114 100 114 C96 114 89 110 89 104Z")
    d.stroke("mark", "M100 114 V120 M93 126 Q100 130 107 126", 1.6)
    d.stroke("mark", "M82 118 L56 112 M82 122 L54 124 M84 126 L60 134 M118 118 L144 112 M118 122 L146 124 M116 126 L140 134", 1.1)
    d.shape("mark", ellipse(84, 158, 10, 8) + ellipse(116, 158, 10, 8))
    d.shape("pop", "M100 140 C112 140 118 150 116 160 L84 160 C82 150 88 140 100 140Z", spot=True)
    d.stroke("pop2", "M100 142 V160 M92 144 L88 160 M108 144 L112 160", 1.4)
    d.band("near", waves(170, 4, 30))
    ripples(d, [(40, 168, 1.4), (150, 166, 1.4)])
    d.band("deep", waves(190, 4, 36), line=False)


def otter_float(d: Drawing):
    d.disc("glow", 152, 46, 16)
    d.shape("light", cloud(20, 52, 0.9), shadow=False)
    d.band("far", "M-30 96 L10 80 L44 90 L80 72 L120 94 L230 92")
    pines(d, [(30, 30), (44, 38), (58, 28)], 92, "near")
    d.band("mid", waves(100, 2, 30))
    for x, y, a in [(16, 132, -10), (170, 128, 190), (150, 146, 170)]:
        d.shape("kelp", leaf(x, y, 30, 6, a), shadow=False, line=False)
    # otter on its back: tail and hind feet at right, head at left, shell on its chest
    def otter():
        d.shape("hero", leaf(150, 118, 28, 6, -6))
        d.shape("mark", leaf(140, 110, 18, 6, -70) + leaf(146, 112, 18, 6, -50))
        d.shape("hero", "M40 116 C40 104 60 98 96 98 C124 98 146 104 150 114 C152 122 140 128 100 128 C64 128 40 126 40 116Z")
        d.shape("hero2", "M60 104 C80 100 110 100 130 104 C120 108 90 108 60 104Z", shadow=False, line=False)
        d.shape("hero", circle(38, 92, 4.5) + circle(54, 86, 4.5))
        d.shape("hero2", circle(46, 102, 15))
        d.marks("mark", "M38 99 q3 -2 6 0 M48 97 q3 -2 6 0")
        d.stroke("mark", "M37 99 q3.5 2 7 0 M48 96 q3.5 2 7 0", 1.4)
        d.marks("mark", ellipse(50, 106, 3.4, 2.4))
        d.shape("light", circle(47, 110, 4) + circle(54, 109, 4), shadow=False)
        d.shape("pop", "M78 98 C76 86 84 80 90 80 C96 80 104 86 102 98Z", spot=True)
        d.stroke("pop2", "M90 82 V97 M84 85 L82 97 M96 85 L98 97", 1.3)
        d.shape("mark", ellipse(74, 98, 6, 5) + ellipse(106, 98, 6, 5))
    place(d, otter, 100, 112, 1.35, 96, 112)
    d.band("near", waves(122, 3, 28))
    ripples(d, [(30, 136, 1.4), (120, 138, 1.6), (70, 150, 1.2)])
    d.band("deep", waves(178, 4, 36), line=False)


# ================================================================ BEAVER
def beaver_portrait(d: Drawing):
    d.disc("glow", 100, 70, 52)
    pines(d, [(14, 60), (32, 74), (168, 74), (186, 60)], 150, "mid")
    d.band("water", "M-30 150 L230 150")
    d.shape("hero", "M40 210 C40 168 64 140 100 140 C136 140 160 168 160 210Z")
    d.shape("hero", circle(58, 60, 9) + circle(142, 60, 9))
    d.marks("mark", circle(58, 60, 4) + circle(142, 60, 4))
    d.shape("hero", "M100 46 C132 46 152 68 152 98 C152 128 132 150 100 152 C68 150 48 128 48 98 C48 68 68 46 100 46Z")
    d.shape("hero2", "M100 100 C120 100 134 110 134 126 C134 140 120 148 100 148 C80 148 66 140 66 126 C66 110 80 100 100 100Z", shadow=False)
    d.marks("mark", "M88 106 C88 100 112 100 112 106 C112 112 106 116 100 116 C94 116 88 112 88 106Z")
    d.shape("teeth", rrect(89, 126, 22, 24, 4), spot=True)
    d.stroke("mark", "M100 127 V149", 1.6)
    d.marks("mark", circle(78, 84, 4) + circle(122, 84, 4))
    d.marks("light", circle(79, 83, 1.2) + circle(123, 83, 1.2))
    d.stroke("mark", "M76 118 L52 112 M76 124 L50 126 M124 118 L148 112 M124 124 L150 126", 1.1)
    d.limb("bark", "M24 166 L176 160", 9)
    d.shape("wood", ellipse(176, 160, 4, 5), shadow=False)
    d.stroke("kelp", "M150 160 l8 -10", 3)
    d.shape("kelp", leaf(158, 150, 14, 4, -60), shadow=False)
    d.shape("mark", ellipse(78, 164, 10, 8) + ellipse(122, 162, 10, 8))


BEAVER = ("M54 160 C44 146 44 118 58 102 C70 88 92 82 110 86 C124 90 134 98 140 108 C150 108 160 114 164 122 "
          "C166 128 162 132 156 132 L146 134 C142 146 132 156 116 160Z")


def beaver_lodge(d: Drawing):
    d.disc("glow", 150, 46, 16)
    pines(d, [(70, 40), (86, 52), (102, 38)], 108, "mid")
    d.band("far", hills(106, 4), line=False)
    d.band("water", "M-30 110 L230 110")
    d.shape("bark2", "M112 128 C116 100 136 88 158 88 C180 88 198 102 204 126Z")
    d.stroke("bark", "M122 114 L148 100 M134 122 L174 96 M158 124 L188 104 M176 124 L198 112 M126 104 L142 94", 2.2)
    d.stroke("water2", "M30 120 H60 M70 126 H100", 2.2)
    # gnawed aspen
    d.shape("leafc", scallop(42, 40, 26, 9, 0.18) + scallop(22, 66, 18, 8, 0.2), line=False)
    d.limb("bark", "M44 210 L44 142", 15)
    d.limb("bark", "M44 126 L44 40 M44 70 L26 56", 15)
    d.shape("wood", "M36.5 126 L51.5 126 L46 134 L51.5 142 L36.5 142 L42 134Z", shadow=False, spot=True)
    d.stroke("bark2", "M40 90 l3 -2 M46 104 l3 -2 M40 160 l3 -2", 1.6, line=False)
    d.band("ground", "M-30 146 Q60 138 120 142 T230 140")
    d.shape("wood", "M60 150 l6 -3 l2 3Z M70 156 l6 -2 l1 3Z M22 154 l5 -3 l2 3Z", shadow=False)

    def beaver():
        d.shape("mark", "M58 158 C40 160 18 164 10 172 C8 178 16 182 30 180 C44 178 56 170 62 164Z")
        d.stroke("hero", "M18 170 L46 174 M22 176 L50 166 M30 164 L40 180", 1.2, line=False)
        d.shape("hero", BEAVER)
        d.shape("hero2", "M146 112 C156 112 162 118 164 122 C166 128 162 132 156 132 L146 132 C142 126 142 116 146 112Z", shadow=False)
        d.shape("hero", circle(130, 94, 4.5), shadow=False)
        d.marks("mark", circle(145, 106, 2) + ellipse(162, 121, 3, 2.4))
        d.shape("teeth", rrect(150, 130, 6, 8, 1.5), shadow=False)
        d.shape("mark", ellipse(146, 142, 6, 4.5) + ellipse(84, 162, 14, 5))
    place(d, beaver, 112, 166, 0.86, 100, 168, mirror=True)
    d.band("deep", hills(190, 3, 30), line=False)


# ================================================================ RACCOON
def raccoon_portrait(d: Drawing):
    d.disc("glow", 100, 100, 62)
    pines(d, [(10, 60), (190, 60)], 170, "deep")
    d.shape("hero", "M44 210 C46 170 70 150 100 150 C130 150 154 170 156 210Z")
    for flipit in (False, True):
        ear = lambda: (d.shape("hero", "M52 74 C48 56 54 40 64 34 C74 40 82 52 82 66Z"),
                       d.shape("light", "M56 66 C54 54 58 44 64 40 C70 46 74 54 76 62Z", shadow=False),
                       d.shape("mark", "M60 64 C60 56 62 50 64 46 C68 50 70 56 72 62Z", shadow=False))
        flip(d, ear) if flipit else ear()
    d.shape("hero", "M100 52 C124 52 140 62 148 80 C156 88 164 96 170 104 L152 110 C146 128 130 144 100 162 "
                    "C70 144 54 128 48 110 L30 104 C36 96 44 88 52 80 C60 62 76 52 100 52Z")
    d.shape("light", "M52 84 C64 72 84 74 96 86 L100 90 L104 86 C116 74 136 72 148 84 C140 80 124 80 112 90 "
                     "L100 102 L88 90 C76 80 60 80 52 84Z", shadow=False)
    d.shape("mark", "M40 100 C52 86 72 84 86 92 C92 96 96 102 100 102 C104 102 108 96 114 92 C128 84 148 86 160 100 "
                    "C150 114 130 120 116 112 C108 108 104 106 100 106 C96 106 92 108 84 112 C70 120 50 114 40 100Z",
            shadow=False, spot=True)
    d.shape("light", "M100 104 C110 108 118 120 118 132 C118 146 110 154 100 156 C90 154 82 146 82 132 C82 120 90 108 100 104Z",
            shadow=False)
    d.shape("light", "M44 108 C56 118 70 122 82 120 L84 132 C70 132 58 124 44 108Z M156 108 C144 118 130 122 118 120 "
                     "L116 132 C130 132 142 124 156 108Z", shadow=False)
    d.shape("mark", "M100 58 C104 70 104 84 100 98 C96 84 96 70 100 58Z", shadow=False)
    d.marks("light", circle(76, 100, 4.5) + circle(124, 100, 4.5))
    d.marks("mark", circle(76, 100, 2.6) + circle(124, 100, 2.6))
    d.marks("mark", ellipse(100, 142, 7, 5))
    d.stroke("mark", "M100 147 V152", 1.6)


RACCOON = ("M40 120 C38 104 52 92 70 92 C92 90 112 96 126 104 C134 98 144 98 152 104 L171 114 C175 116 173 121 168 121 "
           "L154 122 C150 126 146 128 140 128 L141 146 L132 146 L130 131 C116 133 96 133 82 131 L80 146 L71 146 "
           "L67 132 C52 132 42 128 40 120Z")
RACCOON_TAIL = "M46 112 C30 112 14 120 8 134 C4 144 10 150 18 146 C24 134 36 126 50 124Z"


def raccoon_log(d: Drawing):
    d.disc("glow", 140, 54, 22)
    stars(d, [(30, 50, 1.4), (60, 30, 1.2), (176, 92, 1.2)])
    pines(d, [(6, 70), (24, 90), (44, 66), (164, 72), (184, 92)], 150, "deep")
    d.band("mid", hills(146, 4), line=False)

    def coon():
        d.shape("hero", RACCOON_TAIL)
        clipped(d, RACCOON_TAIL, lambda: d.marks("mark", "M14 118 L22 116 L20 150 L10 150Z M28 114 L36 112 L34 140 L24 142Z "
                                                         "M42 110 L48 110 L48 130 L40 132Z"))
        d.shape("hero2", rrect(116, 124, 10, 22, 4))
        d.shape("hero2", rrect(88, 122, 10, 24, 4))
        d.shape("hero", "M146 104 L148 92 L156 102Z")
        d.shape("hero", RACCOON)
        d.shape("light", "M152 104 L171 114 C175 116 173 121 168 121 L156 121 C150 118 146 112 146 108Z", shadow=False)
        d.shape("mark", "M144 104 C150 104 158 108 162 112 L156 116 C150 114 146 112 142 112Z", shadow=False, spot=True)
        d.marks("light", circle(152, 109, 1.6))
        d.marks("mark", ellipse(171, 117, 2.6, 2.2))
        d.shape("mark", rrect(130, 140, 12, 6, 3) + rrect(70, 140, 12, 6, 3), shadow=False, line=False)
    place(d, coon, 104, 150, 1.02, 100, 146)
    d.limb("bark", "M-20 160 L176 156", 20)
    d.shape("wood", ellipse(176, 156, 7, 10))
    d.stroke("bark", "M176 152 a3 4 0 1 1 0 8", 1.4)
    d.band("near", hills(178, 4))
    d.band("deep", hills(192, 3, 30), line=False)


# ================================================================ MOUNTAIN GOAT
def goat_portrait(d: Drawing):
    peaks(d, "mid", True, 150)
    d.band("near", hills(172, 6), line=False)
    d.shape("hero2", scallop(100, 168, 46, 14, 0.12))
    d.shape("hero", leaf(80, 70, 30, 7, 196) + leaf(120, 70, 30, 7, -16))
    d.shape("mark", "M88 54 C82 42 80 30 84 16 C88 28 94 40 96 50Z M112 54 C118 42 120 30 116 16 C112 28 106 40 104 50Z")
    d.shape("hero", "M100 44 C116 44 124 56 124 72 C124 96 120 118 114 134 C110 146 106 152 100 152 "
                    "C94 152 90 146 86 134 C80 118 76 96 76 72 C76 56 84 44 100 44Z")
    d.shape("hero", "M86 140 L82 182 L91 172 L100 188 L109 172 L118 182 L114 140Z")
    d.shape("hero2", "M88 150 L90 170 L100 180 L110 170 L112 150Z", shadow=False, line=False)
    d.marks("mark", ellipse(86, 82, 3.2, 3.8) + ellipse(114, 82, 3.2, 3.8))
    d.marks("mark", ellipse(94, 140, 3, 2.4) + ellipse(106, 140, 3, 2.4))
    d.stroke("hero2", "M92 56 Q100 62 108 56 M90 64 Q100 70 110 64", 1.6, line=False)


GOAT = ("M50 96 C50 86 58 80 70 80 L116 80 C122 72 126 62 130 56 C133 50 139 46 145 48 L150 52 C156 56 160 62 160 70 "
        "L156 74 C152 76 148 76 146 80 L146 96 L149 102 L145 104 L144 128 L136 128 L134 108 L126 110 L120 106 "
        "L114 110 L106 106 L98 110 L90 106 L82 110 L79 128 L71 128 L68 106 L60 104 C53 102 50 100 50 96Z")


def goat(d: Drawing):
    d.shape("hero2", rrect(126, 104, 8, 24, 3))
    d.shape("hero2", rrect(58, 102, 8, 26, 3))
    d.shape("mark", "M141 50 C138 40 134 34 126 28 C134 30 142 38 146 48Z")
    d.shape("hero", leaf(140, 56, 14, 4, 200))
    d.shape("hero", GOAT)
    d.shape("hero", "M148 72 L146 90 L156 78Z", shadow=False)
    d.marks("mark", circle(150, 60, 1.6) + circle(159, 68, 1.4))
    d.shape("mark", rrect(136, 126, 8, 3, 1) + rrect(71, 126, 8, 3, 1), shadow=False)


def goat_cliff(d: Drawing):
    d.disc("glow", 50, 52, 16)
    d.band("far", "M-30 130 L20 90 L50 106 L92 50 L124 96 L150 80 L230 120")
    d.shape("light", "M92 50 L104 66 L97 64 L92 70 L86 64 L80 66Z M20 90 L28 99 L23 98 L19 102 L15 98Z", shadow=False)
    d.band("mid", "M-30 160 L10 140 L40 150 L70 132 L230 150", line=False)
    d.shape("near", "M40 230 L44 160 L60 132 L108 128 L150 132 L168 150 L176 230Z")
    d.shape("deep", "M108 128 L150 132 L168 150 L176 230 L150 230 L148 160 Z", shadow=False, line=False)
    d.stroke("deep", "M60 150 L72 170 M90 146 L84 176 M120 150 L128 186", 2, line=False)
    place(d, goat, 104, 130, 1.0, 100, 128)


# ================================================================ ALLIGATOR
GATOR_HEAD = ("M-20 152 C10 132 40 118 70 114 C90 112 104 106 114 98 C122 90 136 88 144 96 L150 102 "
              "C164 104 178 108 188 114 C194 118 194 126 188 130 C172 134 152 134 132 134 L120 138 "
              "C100 142 80 148 60 154 C30 162 0 168 -20 172Z")


def gator_portrait(d: Drawing):
    d.disc("glow", 60, 70, 34)
    for x in (150, 170, 186):
        d.stroke("near", f"M{x} 140 Q{x - 4} 110 {x + 4} {84 + (x % 3) * 6}", 3)
    d.band("far", hills(132, 4), line=False)
    d.band("mid", waves(146, 2, 34))
    d.shape("hero2", "M120 136 C150 136 172 136 188 130 C186 140 170 146 150 146 C134 146 124 142 120 136Z")
    d.shape("hero", GATOR_HEAD)
    d.shape("hero", circle(182, 110, 5))
    d.shape("hero", circle(138, 94, 10))
    d.shape("eye", ellipse(138, 93, 6, 4.5), shadow=False)
    d.marks("mark", ellipse(138, 93, 1.4, 4) + circle(183, 108, 1.6))
    d.shape("light", " ".join(f"M{x} 132 l2.5 -6 l2.5 6Z" for x in range(126, 186, 8)), shadow=False)
    d.shape("light", " ".join(f"M{x} 134 l2.5 6 l2.5 -6Z" for x in range(130, 180, 9)), shadow=False)
    d.stroke("mark", "M124 134 C150 134 172 134 188 128", 1.6)
    bumps = "".join(f"M{x} {y} l5 -9 l5 9Z" for x, y in [(4, 142), (20, 134), (36, 127), (52, 122), (68, 118), (84, 114)])
    d.shape("hero", bumps, shadow=False)
    d.marks("mark", "".join(circle(x, y, 2) for x, y in [(30, 146), (46, 140), (62, 134), (78, 130), (94, 124), (108, 116),
                                                        (40, 156), (56, 150), (72, 144), (88, 140), (104, 132)]))
    d.band("near", waves(170, 4, 34))
    ripples(d, [(30, 180, 1.4), (150, 182, 1.6)])


def cypress(d: Drawing, x, y, h, role="dark", moss=True, s=1.0):
    d.shape(role, f"M{x - 12 * s} {y} C{x - 4 * s} {y - 12 * s} {x - 3 * s} {y - 30 * s} {x - 3 * s} {y - h} L{x + 3 * s} {y - h} "
                  f"C{x + 3 * s} {y - 30 * s} {x + 4 * s} {y - 12 * s} {x + 12 * s} {y}Z")
    d.stroke(role, f"M{x} {y - h * 0.55} L{x - 18 * s} {y - h * 0.7} M{x} {y - h * 0.75} L{x + 16 * s} {y - h * 0.88}", 2.4 * s)
    d.shape(role, ellipse(x, y - h, 24 * s, 7 * s) + ellipse(x - 18 * s, y - h * 0.7, 14 * s, 5 * s)
            + ellipse(x + 16 * s, y - h * 0.88, 14 * s, 5 * s))
    if moss:
        m = ""
        for mx, my, ml in [(x - 26 * s, y - h * 0.7, 20), (x - 12 * s, y - h * 0.7, 16), (x + 8 * s, y - h * 0.88, 22),
                           (x + 22 * s, y - h * 0.88, 14), (x - 14 * s, y - h, 18), (x + 10 * s, y - h, 24)]:
            ml *= s
            m += f"M{mx:.1f} {my:.1f} l2 {ml * 0.8:.1f} l2 {-ml * 0.5:.1f} l2 {ml:.1f} l2 {-ml * 1.3:.1f}Z "
        d.shape("moss", m, shadow=False, line=False)


def gator_swamp(d: Drawing):
    d.disc("glow", 100, 92, 30)
    d.band("far", hills(118, 4), line=False)
    cypress(d, 26, 124, 90)
    cypress(d, 172, 124, 100)
    d.band("mid", "M-30 122 L230 122")
    d.stroke("glow2", "M84 130 H116 M90 136 H110", 2.4)

    def gator():
        d.shape("hero", "M24 140 C44 134 70 132 100 132 C114 124 126 122 134 126 C146 128 160 130 172 134 "
                        "C176 138 172 141 164 141 L24 142Z")
        d.shape("hero", circle(128, 124, 6) + circle(168, 132, 3.5), shadow=False)
        d.shape("eye", ellipse(128, 123, 3.4, 2.4), shadow=False)
        d.marks("mark", ellipse(128, 123, 0.9, 2.2))
        d.shape("hero", "".join(f"M{x} 134 l4 -7 l4 7Z" for x in range(36, 100, 10)), shadow=False)
    place(d, gator, 104, 148, 1.3, 100, 140)
    d.stroke("light", "M18 156 q8 -4 16 0 M178 156 q6 -3 12 0", 2)
    for x, y in [(40, 174), (150, 170), (96, 186)]:
        d.shape("hero2", f"M{x} {y} m-12 0 a12 5 0 1 0 24 0 a12 5 0 1 0 -24 0Z M{x} {y} L{x + 12} {y - 2} L{x + 10} {y + 2}Z", shadow=True)
    d.shape("pop", "M150 168 l-4 -8 l4 3 l4 -3Z", shadow=False, spot=True)
    d.band("near", waves(194, 3, 40), line=False)


# ================================================================ MANATEE
def manatee_portrait(d: Drawing):
    underwater(d, bottom=False)
    d.shape("hero", "M30 210 C30 150 60 122 100 122 C140 122 170 150 170 210Z")
    d.shape("hero", leaf(52, 150, 40, 10, 140) + leaf(148, 150, 40, 10, 40))
    d.shape("hero", "M100 42 C134 42 156 68 156 102 C156 130 134 150 100 150 C66 150 44 130 44 102 C44 68 66 42 100 42Z")
    d.shape("hero2", "M100 96 C126 96 144 110 144 128 C144 146 124 158 100 158 C76 158 56 146 56 128 C56 110 74 96 100 96Z",
            shadow=False, spot=True)
    d.stroke("mark", "M100 118 V146 M88 150 Q100 156 112 150", 1.8)
    d.marks("mark", "M84 104 q6 -6 12 0 q-6 -2 -12 0Z M104 104 q6 -6 12 0 q-6 -2 -12 0Z")
    d.marks("mark", "".join(circle(x, y, 1.1) for x, y in [(76, 120), (82, 126), (74, 132), (124, 120), (118, 126), (126, 132),
                                                          (86, 116), (114, 116)]))
    d.marks("mark", circle(72, 84, 2.4) + circle(128, 84, 2.4))
    d.stroke("mark", "M82 62 Q100 56 118 62 M86 70 Q100 66 114 70", 1.4, line=False)
    bubbles(d, [(170, 70, 3), (176, 56, 4.5), (168, 44, 2.5)])


def manatee_spring(d: Drawing):
    underwater(d)
    for x in (20, 30, 44, 150, 164, 178):
        d.shape("mid", leaf(x, 182, 40 + (x % 3) * 6, 4, -90 + (x % 5) * 3), shadow=False, line=False)
    p = ((40, 104), (74, 92), (136, 90), (176, 112))
    prof = lambda t: (4 + 18 * math.sin(math.pi * (0.12 + 0.72 * t)), 4 + 20 * math.sin(math.pi * (0.12 + 0.72 * t)))
    x, y, dx, dy = _bez(p, 0.0)
    d.shape("hero", f"M{x + 4} {y - 4} C{x - 10} {y - 22} {x - 30} {y - 14} {x - 30} {y + 2} C{x - 30} {y + 18} {x - 10} {y + 22} {x + 4} {y + 8}Z")
    fl = frame(p, 0.74, -16)
    d.shape("hero2", leaf(fl[0], fl[1], 22, 6, 130))
    d.shape("hero", spine(p, prof))
    tip = frame(p, 1.0)
    d.shape("hero2", ellipse(tip[0] - 2, tip[1] + 2, 12, 11), shadow=False, spot=True)
    d.marks("mark", "".join(circle(tip[0] + a, tip[1] + b, 1) for a, b in [(-4, 0), (0, 4), (4, 0), (-2, 7), (3, 8)]))
    e = frame(p, 0.86, 6)
    d.marks("mark", circle(e[0], e[1], 1.8))
    d.stroke("mark", f"M{tip[0] - 4} {tip[1] - 8} q3 -3 6 0", 1.3)
    for k in range(3):
        a, b = frame(p, 0.3 + 0.12 * k, 14), frame(p, 0.34 + 0.12 * k, -12)
        d.stroke("mark", f"M{a[0]:.1f} {a[1]:.1f} Q{(a[0] + b[0]) / 2 + 3:.1f} {(a[1] + b[1]) / 2:.1f} {b[0]:.1f} {b[1]:.1f}", 1.2, line=False)
    for x, y, sc in [(140, 48, 0.8), (156, 56, 0.7), (40, 150, 0.7)]:
        d.shape("pop", fish(x, y, sc, right=True), shadow=False)
    bubbles(d, [(184, 96, 2.5), (190, 82, 3.5), (184, 68, 2.5)])


# ================================================================ ORCA
def orca(d: Drawing, p, s=1.0, spot=True):
    prof = lambda t: (s * (3 + 17 * math.sin(math.pi * (t * 0.86) ** 1.2)), s * (3 + 15 * math.sin(math.pi * (t * 0.86) ** 1.2)))
    d.shape("hero", flukes(p, 15 * s, 12 * s))
    d.shape("hero", fin(p, 0.56, 30 * s, 4 * s, 13 * s))
    pf = frame(p, 0.72, -12 * s)
    x, y, dx, dy = _bez(p, 0.72)
    ang = math.degrees(math.atan2(dy, dx)) + 120
    d.shape("hero", leaf(pf[0], pf[1], 22 * s, 7 * s, ang))
    d.shape("hero", spine(p, prof), spot=False)
    hx, hy = frame(p, 1.0)
    hb = prof(1.0)
    d.shape("hero", circle(*frame(p, 0.985, (hb[0] - hb[1]) / 2), (hb[0] + hb[1]) / 2 * 0.98), shadow=False)
    d.shape("light", spine(p, lambda t: (-2 * s, prof(t)[1] - 1.5 * s), t0=0.62, t1=0.99), shadow=False, spot=spot)
    d.shape("light", spine(p, lambda t: (-3 * s, prof(t)[1] - 2 * s + 4 * s * math.sin(math.pi * (t - 0.22) / 0.2)),
                           t0=0.22, t1=0.42), shadow=False, spot=spot)
    sx, sy = frame(p, 0.46, prof(0.46)[0] - 3 * s)
    d.shape("hero2", ellipse(sx, sy, 9 * s, 3.5 * s), shadow=False, line=False)
    ex, ey = frame(p, 0.86, 7 * s, -6 * s)
    a = math.degrees(math.atan2(*reversed(_bez(p, 0.86)[2:])))
    d.shape("light", ellipse(ex, ey, 7 * s, 3 * s), shadow=False, extra=f'transform="rotate({a:.1f} {ex:.1f} {ey:.1f})"', spot=spot)
    e = frame(p, 0.9, 3 * s)
    d.marks("mark", circle(e[0], e[1], 1.3 * s))


def orca_breach(d: Drawing):
    d.disc("glow", 150, 46, 16)
    d.shape("light", cloud(14, 56, 1.0), shadow=False)
    d.band("far", "M-30 118 L20 100 L50 108 L90 92 L130 112 L230 110", line=False)
    d.band("mid", waves(126, 3, 30))
    orca(d, ((54, 138), (50, 82), (112, 40), (170, 76)), 1.3)
    splash(d, 54, 134, 24)
    d.band("near", waves(150, 4, 34))
    ripples(d, [(110, 160, 2), (20, 166, 1.6), (150, 170, 1.6)])
    d.band("deep", waves(174, 4, 38), line=False)


def orca_fin(d: Drawing, x, y, h, s=1.0, blow=False):
    d.shape("hero", f"M{x - 34 * s} {y} C{x - 26 * s} {y - 12 * s} {x + 10 * s} {y - 14 * s} {x + 34 * s} {y - 2 * s} L{x + 34 * s} {y + 4}Z")
    d.shape("hero", f"M{x - 8 * s} {y - 10 * s} C{x - 6 * s} {y - h * 0.5} {x - 4 * s} {y - h * 0.8} {x - 2 * s} {y - h} "
                    f"C{x + 4 * s} {y - h * 0.7} {x + 8 * s} {y - h * 0.4} {x + 12 * s} {y - 11 * s}Z")
    d.shape("hero2", ellipse(x - 14 * s, y - 8 * s, 8 * s, 3 * s), shadow=False, line=False)
    if blow:
        bx, by = x + 26 * s, y - 10 * s
        d.stroke("light", f"M{bx} {by} L{bx - 8} {by - 22} M{bx + 1} {by} L{bx + 1} {by - 26} M{bx + 2} {by} L{bx + 10} {by - 22}", 2.6)
        for dx, dy, r in [(-10, -28, 2.6), (1, -33, 2.8), (12, -28, 2.6), (-16, -20, 2), (18, -19, 2), (-4, -40, 2), (8, -40, 2)]:
            d.shape("light", drop(bx + dx, by + dy, r), shadow=False)


def orca_islands(d: Drawing):
    d.disc("glow", 46, 50, 16)
    d.band("far", "M-30 104 L60 100 L110 56 L150 98 L230 100")
    d.shape("light", "M110 56 L122 70 L116 69 L110 74 L104 69 L98 70Z", shadow=False)
    d.shape("near", "M110 108 C118 94 140 86 170 86 C196 86 214 96 230 108Z")
    pines(d, [(132, 22), (144, 30), (156, 24), (170, 32), (184, 26), (198, 30)], 94, "deep")
    d.band("mid", waves(108, 2, 30))
    orca_fin(d, 60, 138, 46, 1.1, blow=True)
    orca_fin(d, 138, 132, 30, 0.8)
    d.band("near", waves(140, 3, 32))
    ripples(d, [(30, 152, 1.6), (90, 150, 1.6), (150, 156, 1.4)])
    d.band("deep", waves(170, 4, 38), line=False)


# ================================================================ HUMMINGBIRD
def hummingbird(d: Drawing, flower=True):
    """Hovering ruby-throated hummingbird facing right, drawn around (100, 100)."""
    for a, role in [(-118, "wing2"), (-100, "wing")]:
        d.shape(role, leaf(98, 92, 70, 12, a), spot=role == "wing")
    d.stroke("wing2", "M40 40 Q34 60 44 76 M54 30 Q44 48 50 62", 2, line=False)
    d.shape("hero", "M60 150 L54 168 L66 158 L68 170 L76 154Z")
    d.shape("hero", "M66 150 C60 130 68 108 90 98 C100 94 112 94 120 100 C126 108 122 120 114 128 C102 142 84 152 66 150Z")
    d.shape("light", "M76 142 C88 138 104 128 114 116 C112 126 106 134 98 140 C90 146 80 148 76 142Z", shadow=False)
    d.shape("hero", circle(124, 92, 17))
    d.shape("pop", "M112 100 C118 108 128 110 136 106 C134 114 126 120 116 118 C110 114 108 106 112 100Z", shadow=False, spot=True)
    d.shape("light", "M108 104 C112 112 118 118 124 120 C118 124 110 122 104 116Z", shadow=False)
    d.limb("mark", "M138 88 L186 80", 3)
    d.marks("light", circle(127, 88, 3.2))
    d.marks("mark", circle(127.5, 88, 2))


def humming_portrait(d: Drawing):
    d.disc("glow", 100, 100, 70)
    d.shape("leafc", leaf(186, 170, 40, 10, -150) + leaf(14, 180, 50, 12, -40), line=False)
    place(d, hummingbird, 92, 98, 1.04, 110, 100)
    d.stroke("light", "M30 96 q-6 6 0 12 M22 90 q-8 10 0 20", 2)


def trumpet(d: Drawing, x, y, a, s=1.0):
    group(d, f"translate({x} {y}) rotate({a}) scale({s})", lambda: (
        d.shape("flower", "M0 -4 L24 -6 C30 -12 36 -12 38 -6 L38 6 C36 12 30 12 24 6 L0 4Z", spot=True),
        d.shape("flower2", "M30 -9 C34 -10 37 -8 38 -6 L38 6 C37 8 34 10 30 9 C33 4 33 -4 30 -9Z", shadow=False)))


def humming_flowers(d: Drawing):
    d.disc("glow", 60, 60, 24)
    peaks(d, "far", True, 140)
    d.band("mid", hills(156, 5), line=False)
    d.stroke("leafc", "M200 30 C170 60 160 100 150 200", 4)
    for x, y, a in [(186, 50, 150), (170, 76, 200), (162, 108, 150), (156, 140, 210)]:
        d.shape("leafc", leaf(x, y, 22, 7, a), shadow=False)
    trumpet(d, 168, 70, 168, 1.0)
    trumpet(d, 160, 100, 200, 0.9)
    trumpet(d, 154, 130, 150, 0.9)
    place(d, hummingbird, 128, 76, 0.66, 186, 80)
    d.band("near", hills(180, 4))


# ================================================================ ARCTIC FOX
FOX_EAR = "M66 72 C60 64 60 52 66 46 C76 46 84 54 86 64Z"


def fox_portrait(d: Drawing):
    aurora(d, 60)
    stars(d, [(30, 40, 1.4), (172, 46, 1.4), (150, 24, 1.1), (50, 70, 1.1)])
    d.band("far", hills(150, 10))
    d.band("mid", hills(170, 6, 30), line=False)
    d.shape("hero", "M60 176 C30 176 20 150 32 132 C40 124 50 128 50 138 C52 156 72 166 100 168 C130 170 150 164 164 172 "
                    "C150 186 100 188 60 176Z")
    d.shape("hero", "M66 172 C58 144 68 112 86 98 L114 98 C132 112 142 144 134 172Z")
    d.shape("hero2", "M74 168 L78 136 L86 136 L86 168Z M126 168 L122 136 L114 136 L114 168Z", shadow=False, line=False)
    d.stroke("hero2", "M88 120 Q100 130 112 120", 1.6, line=False)
    d.shape("hero", FOX_EAR)
    flip(d, lambda: d.shape("hero", FOX_EAR))
    d.shape("hero2", "M70 66 C66 60 66 54 68 51 C74 52 78 56 80 62Z", shadow=False)
    flip(d, lambda: d.shape("hero2", "M70 66 C66 60 66 54 68 51 C74 52 78 56 80 62Z", shadow=False))
    d.shape("hero", "M100 50 C124 50 140 64 140 82 C140 100 124 114 100 122 C76 114 60 100 60 82 C60 64 76 50 100 50Z")
    d.shape("hero2", "M60 84 C64 96 74 104 86 108 L76 112 C68 106 62 96 60 84Z M140 84 C136 96 126 104 114 108 L124 112 "
                     "C132 106 138 96 140 84Z", shadow=False, line=False)
    d.marks("mark", "M78 84 Q86 76 92 84 Q86 88 78 84Z M122 84 Q114 76 108 84 Q114 88 122 84Z")
    d.marks("mark", "M93 104 C93 100 107 100 107 104 C107 108 102 111 100 111 C98 111 93 108 93 104Z")
    d.stroke("mark", "M100 111 V114 M95 116 Q100 118 105 116", 1.4)
    snowflakes(d, [(24, 100, 1.8), (176, 104, 2), (160, 130, 1.5), (38, 120, 1.5)])


def fox_curled(d: Drawing):
    aurora(d, 56)
    d.disc("glow", 150, 50, 14)
    stars(d, [(30, 44, 1.4), (60, 24, 1.2), (110, 32, 1.1)])
    d.band("far", hills(118, 8))
    d.band("ice", hills(142, 6, 20))
    d.shape("ice2", "M10 170 C40 152 160 150 190 170Z", shadow=False, line=False)
    d.shape("hero", ellipse(108, 144, 46, 26))
    d.shape("hero", "M76 128 L70 106 L86 120Z M86 124 L88 102 L98 120Z")
    d.shape("hero2", "M77 124 L73 111 L82 120Z M89 122 L90 108 L95 119Z", shadow=False, line=False)
    d.shape("hero", ellipse(80, 136, 20, 15))
    d.stroke("mark", "M72 134 q4 3 8 0", 1.6)
    d.marks("mark", circle(62, 142, 2.6))
    d.shape("hero", "M150 132 C164 140 160 164 130 168 C100 172 70 166 56 152 C74 158 104 160 124 154 C140 150 152 142 150 132Z")
    d.shape("hero2", "M56 152 C74 158 104 160 124 154 C110 162 80 164 56 152Z", shadow=False, line=False)
    snowflakes(d, [(24, 80, 1.8), (176, 90, 2), (160, 116, 1.5), (40, 110, 1.6), (100, 70, 1.6), (130, 92, 1.4)])
    d.band("ice2", hills(178, 3), line=False)


# ================================================================ WALRUS
def walrus_portrait(d: Drawing):
    d.disc("glow", 152, 50, 16)
    d.band("far", "M-30 112 L20 96 L60 108 L230 104", line=False)
    d.band("mid", waves(116, 3, 30))
    d.shape("hero2", "M6 210 C10 152 48 122 100 122 C152 122 190 152 194 210Z")
    d.stroke("hero", "M30 170 Q100 150 170 170 M24 190 Q100 170 176 190", 2.4, line=False)
    d.shape("hero", "M100 36 C138 36 162 62 162 96 C162 122 148 142 130 150 L70 150 C52 142 38 122 38 96 C38 62 62 36 100 36Z")
    d.shape("tusk", "M82 128 C80 152 82 174 90 196 C95 174 95 152 95 130Z M118 128 C120 152 118 174 110 196 "
                    "C105 174 105 152 105 130Z", spot=True)
    d.shape("hero2", "M100 98 C112 88 140 90 146 108 C152 126 136 140 116 138 C108 138 102 134 100 130 C98 134 92 138 84 138 "
                     "C64 140 48 126 54 108 C60 90 88 88 100 98Z", shadow=False)
    d.marks("mark", "".join(circle(x, y, 1.3) for x, y in [(66, 112), (74, 118), (82, 112), (66, 124), (78, 126), (88, 122),
                                                          (134, 112), (126, 118), (118, 112), (134, 124), (122, 126), (112, 122)]))
    d.marks("mark", ellipse(94, 98, 2.4, 1.6) + ellipse(106, 98, 2.4, 1.6))
    d.marks("mark", circle(74, 76, 3) + circle(126, 76, 3))
    d.stroke("mark", "M84 62 Q100 56 116 62", 1.4, line=False)
    d.band("near", waves(186, 4, 34), line=False)


WALRUS_SIDE = ("M14 150 C18 124 44 108 80 106 C106 104 128 96 142 84 C152 76 170 78 176 90 C182 100 180 112 174 118 "
               "L168 124 C158 132 150 140 146 150Z")


def walrus(d: Drawing):
    d.shape("hero", leaf(14, 146, 22, 7, 160) + leaf(18, 150, 22, 7, 200))
    d.shape("hero", WALRUS_SIDE)
    d.stroke("hero2", "M60 112 Q70 130 66 148 M90 108 Q102 128 98 148 M120 100 Q130 120 128 146", 2, line=False)
    d.shape("hero2", leaf(130, 132, 26, 8, 120))
    d.shape("tusk", "M164 116 C162 128 160 140 156 150 C162 142 168 130 170 118Z M170 118 C170 130 170 142 168 150 "
                    "C174 142 176 130 176 118Z", spot=True)
    d.shape("hero2", circle(166, 108, 9) + circle(176, 108, 8), shadow=False)
    d.marks("mark", "".join(circle(x, y, 1) for x, y in [(162, 106), (168, 110), (172, 106), (178, 110), (164, 112)]))
    d.marks("mark", circle(160, 90, 2))


def walrus_rock(d: Drawing):
    d.disc("glow", 46, 50, 16)
    d.shape("light", "M140 108 L152 76 L170 70 L186 92 L192 108Z")
    d.shape("ice2", "M170 70 L186 92 L192 108 L176 108 L178 90Z", shadow=False, line=False)
    d.band("far", waves(106, 2, 30))
    d.band("mid", waves(124, 3, 34))
    d.shape("rock", "M-10 176 C-6 152 24 144 60 144 L150 142 C180 142 204 152 210 176Z")
    place(d, walrus, 132, 140, 0.62, 100, 150)
    place(d, walrus, 74, 168, 0.95, 100, 150)
    d.band("near", waves(166, 4, 34))
    ripples(d, [(30, 180, 1.6), (130, 182, 1.6)])
    d.band("deep", waves(190, 3, 38), line=False)


# ================================================================ NARWHAL
def narwhal(d: Drawing, p, s=1.0, tusk_len=60):
    prof = lambda t: (s * (3 + 15 * math.sin(math.pi * (t * 0.84) ** 1.15)), s * (3 + 14 * math.sin(math.pi * (t * 0.84) ** 1.15)))
    d.shape("hero", flukes(p, 14 * s, 11 * s))
    hx, hy, dx, dy = _bez(p, 1.0)
    base = frame(p, 1.0, 2 * s, 6 * s)
    tip = (base[0] + dx * tusk_len - dy * tusk_len * 0.12, base[1] + dy * tusk_len + dx * tusk_len * 0.12)
    d.limb("tusk", f"M{base[0]:.1f} {base[1]:.1f} L{tip[0]:.1f} {tip[1]:.1f}", 3.6 * s, spot=True)
    n = int(tusk_len / 6)
    tw = " ".join(f"M{base[0] + (tip[0] - base[0]) * i / n - dy * 1.6:.1f} {base[1] + (tip[1] - base[1]) * i / n + dx * 1.6:.1f} "
                  f"l{dx * 2 + dy * 3.2:.1f} {dy * 2 - dx * 3.2:.1f}" for i in range(1, n))
    d.stroke("mark", tw, 0.9, line=False)
    pf = frame(p, 0.74, -10 * s)
    ang = math.degrees(math.atan2(dy, dx)) + 130
    d.shape("hero", leaf(pf[0], pf[1], 16 * s, 5 * s, ang))
    body = spine(p, prof)
    d.shape("hero", body)
    hb = prof(1.0)
    d.shape("hero", circle(*frame(p, 0.98, (hb[0] - hb[1]) / 2), (hb[0] + hb[1]) / 2), shadow=False)
    d.shape("hero2", spine(p, lambda t: (-3 * s, prof(t)[1] - 1.5 * s), t0=0.15, t1=0.97), shadow=False)
    spots = []
    for i in range(26):
        t = 0.08 + 0.8 * ((i * 37) % 26) / 26
        u = prof(t)[0] * (0.2 + 0.7 * ((i * 11) % 7) / 7)
        spots.append(frame(p, t, u))
    clipped(d, body, lambda: d.marks("mark", "".join(ellipse(x, y, 2.4 * s, 1.6 * s) for x, y in spots)))
    e = frame(p, 0.9, 3 * s)
    d.marks("mark", circle(e[0], e[1], 1.5 * s))


def narwhal_portrait(d: Drawing):
    d.band("sky2", waves(36, 5, 26))
    d.band("far", waves(60, 5, 28))
    d.shape("light", "M-30 30 L40 30 L50 44 L20 52 L-30 50Z M120 30 L230 30 L230 46 L160 50 L130 44Z", line=False)
    d.band("mid", waves(92, 6, 30))
    rays(d)
    d.band("near", waves(132, 6, 34))
    d.band("deep", waves(162, 5, 36), line=False)
    narwhal(d, ((16, 136), (44, 122), (90, 114), (120, 106)), 1.35, 52)
    bubbles(d, [(30, 92, 2.5), (24, 80, 3.5), (32, 68, 2.4)])


def narwhal_head(d: Drawing, x, y, lean, tusk=96):
    a = math.radians(lean)
    ux, uy = math.sin(a), -math.cos(a)
    tx, ty = x + ux * 26, y + uy * 26
    d.shape("hero", f"M{x - 15} {y + 10} C{x - 16} {y - 10} {tx - 12} {ty + 4} {tx} {ty} C{tx + 12} {ty + 4} {x + 16} {y - 10} {x + 15} {y + 10}Z")
    ex, ey = x + ux * 14 + uy * 0, y + uy * 14
    d.shape("hero2", f"M{x - 4} {y + 10} C{x - 4} {y} {x + 2} {y - 6} {x + 8} {y - 4} C{x + 12} {y} {x + 12} {y + 6} {x + 12} {y + 10}Z",
            shadow=False, line=False)
    d.marks("mark", "".join(ellipse(x + dx, y + dy, 2, 1.4) for dx, dy in [(-8, -2), (-10, 6), (-4, 4), (6, -10), (-2, -12)]))
    d.marks("mark", circle(ex + 5, ey + 4, 1.6))
    d.limb("tusk", f"M{tx:.1f} {ty:.1f} L{tx + ux * tusk:.1f} {ty + uy * tusk:.1f}", 3.6, spot=True)
    d.stroke("mark", " ".join(f"M{tx + ux * k - 1.8:.1f} {ty + uy * k:.1f} l3.6 {-2 if lean < 0 else 2}" for k in range(8, tusk, 7)),
             0.9, line=False)


def narwhal_ice(d: Drawing):
    d.disc("glow", 100, 54, 18)
    d.shape("light", "M-30 104 L-30 88 L10 84 L30 92 L60 94 L66 104Z M150 104 L156 90 L190 84 L230 88 L230 104Z")
    d.band("far", waves(104, 2, 30))
    d.shape("light", "M10 128 C10 120 30 116 50 118 C62 120 64 128 58 132 L16 134Z M150 124 C152 116 178 116 196 120 L196 132 "
                     "L154 132Z", shadow=True)
    group(d, "translate(76 144) scale(1.5) translate(-76 -144)", lambda: narwhal_head(d, 76, 144, 22, 48))
    group(d, "translate(124 144) scale(1.5) translate(-124 -144)", lambda: narwhal_head(d, 124, 144, -22, 48))
    d.band("mid", waves(140, 3, 32))
    ripples(d, [(58, 140, 1.4), (110, 140, 1.4)])
    d.band("near", waves(160, 4, 36))
    d.band("deep", waves(182, 4, 40), line=False)


# ================================================================ REINDEER
def reindeer_antler(d: Drawing, mirror=False):
    def a():
        d.limb("antler", "M92 58 C70 52 50 40 46 14", 5.5, spot=True)
        d.limb("antler", "M62 46 L42 40 M52 32 L36 24 M47 18 L56 6 M74 52 L74 32 M48 22 L38 12", 4, spot=True)
        d.shape("antler", "M94 62 C86 66 84 76 86 86 L80 80 L82 90 C76 84 74 72 80 64Z", spot=True)
    flip(d, a) if mirror else a()


def reindeer_portrait(d: Drawing):
    aurora(d, 60)
    stars(d, [(24, 70, 1.4), (178, 72, 1.4), (100, 18, 1.2)])
    d.band("far", hills(156, 6))
    pines(d, [(14, 40), (186, 44)], 166, "mid")
    d.shape("hero2", scallop(100, 172, 44, 14, 0.14))
    reindeer_antler(d)
    reindeer_antler(d, True)
    d.shape("hero", leaf(80, 76, 26, 7, 196) + leaf(120, 76, 26, 7, -16))
    d.shape("hero", "M100 58 C114 58 122 66 122 80 C122 98 128 112 130 126 C132 144 120 156 100 156 C80 156 68 144 70 126 "
                    "C72 112 78 98 78 80 C78 66 86 58 100 58Z")
    d.shape("hero2", "M100 118 C116 118 128 126 128 138 C128 150 116 156 100 156 C84 156 72 150 72 138 C72 126 84 118 100 118Z",
            shadow=False)
    d.marks("mark", ellipse(91, 132, 3.6, 5) + ellipse(109, 132, 3.6, 5))
    d.marks("mark", circle(84, 90, 3.4) + circle(116, 90, 3.4))
    d.marks("light", circle(85, 89, 1) + circle(117, 89, 1))
    d.stroke("mark", "M92 146 Q100 150 108 146", 1.6)


REINDEER = ("M46 104 C44 92 52 86 64 86 C86 84 108 84 122 86 C128 80 134 72 138 66 C142 60 148 56 154 56 "
            "L170 66 C174 69 173 74 168 75 L158 75 C154 80 150 88 148 98 C146 106 144 110 142 114 "
            "C128 120 96 120 80 118 C62 116 48 112 46 104Z")


def reindeer(d: Drawing):
    d.limb("hero3", "M126 112 L128 152", 6)
    d.limb("hero3", "M64 108 L62 152", 6)
    d.limb("antler2", "M146 58 C134 44 132 30 140 14 M136 38 L124 32 M134 26 L122 18", 3.6)
    d.limb("hero", "M138 112 L140 152", 6.5)
    d.limb("hero", "M76 112 C80 128 74 140 74 152", 7)
    d.shape("hero", REINDEER)
    d.shape("hero2", "M140 66 C150 70 152 90 146 110 L138 116 C134 108 132 100 134 90 C134 80 136 72 140 66Z", shadow=False)
    d.shape("hero2", "M46 102 C46 94 50 90 56 90 C58 98 58 106 56 112 C50 110 47 106 46 102Z", shadow=False, line=False)
    d.shape("hero", leaf(150, 60, 13, 4, -150), shadow=False)
    d.limb("antler", "M152 58 C142 44 138 28 148 10 M144 40 L132 34 M142 26 L130 20 M148 10 L158 4", 3.6, spot=True)
    d.shape("antler", "M154 58 C160 52 168 52 172 46 L170 54 C166 58 160 60 156 62Z", spot=True)
    d.marks("mark", circle(160, 64, 1.7) + circle(171, 70, 1.6))
    d.shape("mark", rrect(124, 150, 8, 4, 1.5) + rrect(136, 150, 8, 4, 1.5) + rrect(58, 150, 8, 4, 1.5) + rrect(70, 150, 8, 4, 1.5),
            shadow=False, line=False)


def reindeer_lapland(d: Drawing):
    aurora(d, 50)
    d.disc("glow", 160, 46, 14)
    stars(d, [(26, 76, 1.4), (60, 30, 1.2), (130, 26, 1.1)])
    d.band("far", hills(118, 8))
    pines(d, [(150, 46), (166, 58), (182, 44), (196, 52)], 128, "mid")
    for x, h in [(150, 46), (166, 58), (182, 44), (196, 52)]:
        d.shape("light", f"M{x} {128 - h} L{x + h * 0.14} {128 - h * 0.78} L{x - h * 0.14} {128 - h * 0.78}Z", shadow=False, line=False)
    # lavvu tent with a warm glow in the doorway
    d.shape("tent", "M14 136 L38 82 L62 136Z")
    d.stroke("dark", "M32 74 L40 88 M44 74 L36 88", 2)
    d.shape("glow2", "M32 136 L38 116 L44 136Z", shadow=False, spot=True)
    d.band("snow", hills(134, 5))
    place(d, reindeer, 100, 164, 0.86, 110, 152)
    d.band("snow2", hills(176, 3), line=False)


# ================================================================ SNOWY OWL
def owl_flecks(pts, s=1.0):
    return "".join(f"M{x - 3 * s} {y} q{3 * s} {-2.4 * s} {6 * s} 0 q{-3 * s} {1 * s} {-6 * s} 0Z" for x, y in pts)


def owl_portrait(d: Drawing):
    stars(d, [(30, 40, 1.5), (170, 36, 1.4), (180, 76, 1.2)])
    d.disc("glow", 160, 54, 18)
    d.band("far", hills(170, 5))
    d.shape("post", rrect(70, 168, 60, 40, 4))
    d.shape("hero2", "M48 100 C40 130 48 160 70 176 L84 150Z M152 100 C160 130 152 160 130 176 L116 150Z")
    d.shape("hero", "M100 40 C134 40 154 64 154 96 C154 136 136 166 100 176 C64 166 46 136 46 96 C46 64 66 40 100 40Z")
    d.shape("hero2", circle(80, 88, 19) + circle(120, 88, 19), shadow=False, line=False)
    d.shape("hero", "M100 82 C108 90 110 104 100 118 C90 104 92 90 100 82Z", shadow=False, line=False)
    d.shape("eye", circle(80, 88, 10) + circle(120, 88, 10), shadow=False, spot=True)
    d.marks("mark", circle(80, 88, 5) + circle(120, 88, 5))
    d.marks("light", circle(82, 86, 1.6) + circle(122, 86, 1.6))
    d.shape("mark", "M95 104 L105 104 L100 115Z", shadow=False)
    d.marks("mark", owl_flecks([(76, 132), (92, 138), (108, 136), (124, 130), (84, 150), (100, 152), (116, 150),
                                (92, 164), (110, 164), (70, 60), (88, 52), (112, 54), (130, 62), (60, 120), (140, 120)]))
    d.marks("mark", owl_flecks([(54, 130), (58, 146), (146, 130), (142, 146)], 0.8))
    d.shape("hero2", "M84 174 l4 8 l4 -8 Z M108 174 l4 8 l4 -8Z", shadow=False)
    d.stroke("mark", "M86 180 l-1 4 M90 180 l1 4 M110 180 l-1 4 M114 180 l1 4", 1.4)


OWL_WING = ("M92 98 C76 82 54 70 26 66 C18 66 10 70 8 76 L18 78 L6 86 L20 88 L10 96 L26 96 L20 106 L36 102 "
            "C56 104 76 108 90 114Z")


def owl_flight(d: Drawing):
    d.disc("glow", 100, 70, 40)
    stars(d, [(30, 40, 1.4), (174, 40, 1.4), (160, 100, 1.1)])
    d.band("far", hills(146, 6))
    d.band("snow", hills(160, 5, 30))

    def wing():
        group(d, "rotate(-6 92 100)", lambda: (
            d.shape("hero", OWL_WING),
            d.marks("mark", owl_flecks([(30, 78), (44, 80), (58, 84), (36, 92), (52, 94), (70, 92), (66, 102), (20, 84)], 0.9))))
    wing()
    flip(d, wing)
    d.shape("hero", "M100 88 C116 88 122 104 120 120 C118 134 110 142 100 142 C90 142 82 134 80 120 C78 104 84 88 100 88Z")
    d.marks("mark", owl_flecks([(92, 116), (108, 118), (100, 128), (90, 130), (110, 130)], 0.8))
    d.stroke("mark", "M92 140 l-2 8 M96 141 l0 8 M104 141 l0 8 M108 140 l2 8", 1.8)
    d.shape("hero", circle(100, 82, 18))
    d.shape("eye", circle(93, 80, 5) + circle(107, 80, 5), shadow=False, spot=True)
    d.marks("mark", circle(93, 80, 2.5) + circle(107, 80, 2.5) + "M97 88 L103 88 L100 94Z")
    d.marks("mark", owl_flecks([(92, 68), (108, 68)], 0.7))
    d.band("snow2", hills(180, 3), line=False)


# ================================================================ PUFFIN
def puffin_beak(d: Drawing):
    d.shape("pop", "M136 72 C156 74 176 86 186 100 C176 108 156 116 136 118Z", spot=True)
    d.shape("beakbase", "M136 72 C141 73 145 75 148 77 L148 114 C144 116 140 117 136 118Z", shadow=False)
    d.shape("hero2", "M148 77 L155 80 L155 111 L148 114Z", shadow=False)
    d.stroke("pop2", "M164 84 C160 94 160 104 164 110 M174 90 C171 96 171 102 174 106", 1.6, line=False)
    d.stroke("mark", "M136 100 L184 100", 1.3)
    d.shape("hero2", circle(136, 102, 4), shadow=False)


def puffin_portrait(d: Drawing):
    d.disc("glow", 52, 52, 18)
    d.band("far", "M-30 130 L30 120 L40 100 L60 96 L70 120 L230 126", line=False)
    d.band("mid", waves(140, 3, 30))
    d.shape("dark", "M40 210 C34 170 52 134 84 126 C108 120 128 128 140 144 C152 162 158 190 156 210Z")
    d.shape("light", "M126 150 C144 160 156 186 158 210 L110 210 C112 190 116 166 126 150Z", shadow=False)
    d.shape("dark", "M44 150 C30 104 50 54 94 44 C120 38 140 50 146 72 L136 72 C120 64 98 66 84 78 C72 90 70 112 76 132Z")
    d.shape("face", "M76 132 C70 104 78 80 100 68 C116 62 130 64 136 72 L136 118 C130 130 116 138 100 140 C88 140 80 138 76 132Z")
    d.shape("hero2", "M76 132 C80 120 96 116 112 120 C120 124 128 130 132 128 C122 138 108 142 92 140 C84 140 79 137 76 132Z",
            shadow=False, line=False)
    puffin_beak(d)
    d.marks("eyeliner", "M106 80 L120 74 L126 82Z M112 96 L122 92 L120 104Z")
    d.shape("pop2", circle(118, 86, 5.5), shadow=False)
    d.marks("mark", circle(118, 86, 3))
    d.band("near", waves(184, 4, 36), line=False)


def puffin_standing(d: Drawing, fish_=True):
    d.shape("pop", ellipse(98, 162, 9, 3) + ellipse(112, 162, 9, 3), shadow=False)
    d.shape("dark", "M84 160 C70 140 72 104 90 88 C98 80 112 80 118 88 C124 96 124 108 120 116 C128 132 128 150 118 162Z")
    d.shape("light", "M112 114 C122 128 125 148 116 161 L100 161 C106 146 108 128 112 114Z", shadow=False)
    d.shape("dark", "M88 104 C80 120 80 140 86 154 C92 140 96 122 94 104Z", shadow=False, line=False)
    d.shape("face", "M104 82 C114 78 124 84 124 94 C124 102 118 108 110 108 C104 104 102 92 104 82Z", shadow=False)
    d.shape("pop", "M122 84 C130 86 138 92 142 98 C136 102 130 104 122 104Z", spot=True)
    d.shape("beakbase", "M122 84 L126 85 L126 103 L122 104Z", shadow=False)
    if fish_:
        for k, a in enumerate([70, 82, 96, 108]):
            d.shape("fishc", leaf(128 + k * 2, 98, 20, 2.6, a), shadow=False)
    d.marks("eyeliner", "M110 88 L117 85 L119 90Z")
    d.marks("mark", circle(115, 91, 1.8))


def puffin_cliff(d: Drawing):
    d.disc("glow", 150, 48, 16)
    d.band("far", waves(108, 2, 30))
    d.band("mid", waves(126, 3, 34))
    d.band("near", waves(150, 4, 38), line=False)

    def flier():
        d.shape("dark", ellipse(100, 100, 12, 6))
        d.shape("dark", "M96 98 L84 82 L104 96Z M104 102 L96 118 L110 102Z", shadow=False)
        d.shape("face", circle(110, 97, 4), shadow=False)
        d.shape("pop", "M113 96 L120 99 L113 101Z", shadow=False)
    place(d, flier, 40, 62, 0.9)
    d.shape("cliff", "M-30 230 L-30 150 C10 144 60 150 100 152 C140 154 170 156 230 150 L230 230Z")
    d.shape("turf", "M-30 154 C10 146 60 150 100 152 C140 154 170 156 230 152 L230 162 C170 166 140 162 100 162 "
                    "C60 162 10 158 -30 164Z", shadow=False)
    for x, y in [(30, 150), (150, 154), (176, 152)]:
        d.shape("turf", f"M{x} {y} l3 -9 l2 8 l3 -10 l2 11Z", shadow=False, line=False)
    place(d, puffin_standing, 98, 160, 1.28, 106, 162)


# ================================================================ BELUGA
def beluga(d: Drawing, p, s=1.0):
    prof = lambda t: (s * (3 + 17 * math.sin(math.pi * (t * 0.86) ** 1.15)), s * (3 + 15 * math.sin(math.pi * (t * 0.86) ** 1.15)))
    d.shape("hero", flukes(p, 14 * s, 11 * s))
    x, y, dx, dy = _bez(p, 0.74)
    pf = frame(p, 0.74, -12 * s)
    d.shape("hero2", leaf(pf[0], pf[1], 18 * s, 6 * s, math.degrees(math.atan2(dy, dx)) + 130))
    body = spine(p, prof)
    d.shape("hero", body)
    m = frame(p, 0.93, 6 * s)
    hb = prof(1.0)
    d.shape("hero", circle(m[0], m[1], 13 * s), shadow=False)
    beak = frame(p, 1.0, -4 * s, 4 * s)
    d.shape("hero", circle(beak[0], beak[1], 6 * s), shadow=False)
    a, b = frame(p, 0.9, -8 * s), frame(p, 1.0, -6 * s, 6 * s)
    d.stroke("mark", f"M{a[0]:.1f} {a[1]:.1f} Q{(a[0] + b[0]) / 2:.1f} {(a[1] + b[1]) / 2 + 3 * s:.1f} {b[0]:.1f} {b[1]:.1f}", 1.4 * s)
    e = frame(p, 0.86, 2 * s)
    d.marks("mark", circle(e[0], e[1], 1.6 * s))
    d.stroke("hero2", " ".join(f"M{frame(p, t, prof(t)[0] - 3 * s)[0]:.1f} {frame(p, t, prof(t)[0] - 3 * s)[1]:.1f} "
                               f"L{frame(p, t + 0.08, prof(t + 0.08)[0] - 3 * s)[0]:.1f} {frame(p, t + 0.08, prof(t + 0.08)[0] - 3 * s)[1]:.1f}"
                               for t in (0.3, 0.42)), 2, line=False)


def beluga_portrait(d: Drawing):
    underwater(d, bottom=False)
    beluga(d, ((20, 136), (56, 118), (110, 100), (150, 104)), 1.5)
    bubbles(d, [(176, 84, 2.5), (182, 70, 3.5), (174, 58, 2.5)])
    for x, y, sc in [(40, 56, 0.8), (54, 64, 0.7)]:
        d.shape("pop", fish(x, y, sc), shadow=False)


def beluga_kayak(d: Drawing):
    d.disc("glow", 160, 34, 12)
    d.band("far", "M-30 52 L20 44 L60 50 L100 40 L140 50 L230 46", line=False)
    d.band("mid", "M-30 62 L230 62")
    # kayak on the surface
    d.limb("dark", "M66 30 L118 66", 2.6)
    d.shape("pop2", "M64 28 l6 -4 l2 6Z M116 64 l6 4 l-6 2Z", shadow=False)
    d.marks("dark", circle(92, 38, 5))
    d.shape("dark", "M86 58 C86 46 98 44 100 56Z")
    d.shape("pop", "M54 58 L132 58 C126 66 112 68 92 68 C74 68 60 66 54 58Z", spot=True)
    d.band("near", waves(68, 3, 30))
    rays(d)
    d.band("deep", waves(150, 5, 36), line=False)
    beluga(d, ((24, 118), (60, 100), (110, 90), (150, 98)), 1.15)
    beluga(d, ((90, 156), (110, 146), (140, 140), (166, 146)), 0.62)
    bubbles(d, [(170, 88, 2.4), (176, 78, 3.2)])


# ================================================================ colours
BLACK_BEAR_C = {"hero": "#2B2A2F", "hero2": "#C49A6C", "mark": "#121115", "bark": "#7A5236"}
GRIZZLY_C = {"hero": "#7E5130", "hero2": "#A87C50", "mark": "#2B1B10", "pop": "#E0603F", "pop2": "#F29A84",
             "light": "#F3E6CF", "water": "#7CC6E8", "water2": "#E6F6FD"}
POLAR_C = {"hero": "#F7F4EC", "hero2": "#D9D2C2", "mark": "#16171C", "ice": "#A9CFE2", "ice2": "#7FB0C9"}
MOOSE_C = {"hero": "#4B3427", "hero2": "#7B604C", "hero3": "#36261C", "mark": "#16100C", "antler": "#CDAE78", "antler2": "#A88A58",
           "water": "#6FB5D6", "water2": "#DDF0F8"}
ELK_C = {"hero": "#C08E5B", "hero2": "#5C3B25", "hero3": "#3E281A", "mark": "#21160E", "antler": "#A98A60",
         "antler2": "#7E6646", "light": "#F1E4C8", "pop2": "#8A4A3A"}
WOLF_C = {"hero": "#7D8590", "hero2": "#A9AFB8", "mark": "#2E3138", "light": "#F1EFEA", "eye": "#E9A93A"}
EAGLE_C = {"hero": "#4A3122", "hero2": "#6E4A33", "mark": "#1E140D", "light": "#FFFFFF", "pop": "#F4B731",
           "eye": "#F6D348", "eyebrow": "#C9C3B8", "water": "#6FB5D6", "water2": "#DDF0F8"}
OTTER_C = {"hero": "#6B4630", "hero2": "#D8C3A5", "mark": "#20150F", "light": "#F7EFE2", "pop": "#E89AA6", "pop2": "#B85D6C",
           "kelp": "#8A7B2C"}
BEAVER_C = {"hero": "#7A4E30", "hero2": "#A87A55", "mark": "#24170E", "teeth": "#F08A24", "bark": "#8A5E3B", "bark2": "#A08E70",
            "wood": "#EBCB93", "kelp": "#5E8C4A", "leafc": "#7FA650", "water": "#6FB5D6", "water2": "#DDF0F8"}
RACCOON_C = {"hero": "#8E9097", "hero2": "#6B6D74", "mark": "#1C1D22", "light": "#F4F2EE", "bark": "#6E4A30", "wood": "#D9B47E"}
GOAT_C = {"hero": "#F7F5EF", "hero2": "#DDD8CB", "mark": "#1E1E22"}
GATOR_C = {"hero": "#4B5A36", "hero2": "#C9C08A", "mark": "#20271A", "eye": "#E8C23A", "light": "#FFFDF2", "moss": "#A9B596",
           "pop": "#F3A6C0"}
MANATEE_C = {"hero": "#8C959B", "hero2": "#A9B1B6", "mark": "#3A4044", "pop": "#F6C445"}
ORCA_C = {"hero": "#1D1F25", "hero2": "#8C939C", "light": "#FFFFFF", "mark": "#0B0C0F"}
HUMMING_C = {"hero": "#3C9A63", "pop": "#D8304A", "light": "#FFFFFF", "mark": "#1E2420", "wing": "#86BCB2", "wing2": "#5F958A",
             "leafc": "#4E8A4A", "flower": "#E8503A", "flower2": "#F6A23B"}
FOX_C = {"hero": "#F7F5EF", "hero2": "#D6D2C8", "mark": "#1E1F26", "ice": "#9DBFD6", "ice2": "#7FA6C2", "light": "#FFFFFF"}
WALRUS_C = {"hero": "#A8735C", "hero2": "#C99A84", "mark": "#3A2219", "tusk": "#F7F0DC", "rock": "#5E5853", "ice2": "#BCD8E6"}
NARWHAL_C = {"hero": "#7F8B95", "hero2": "#DDE3E7", "mark": "#3A444D", "tusk": "#F4EEDC", "light": "#FFFFFF"}
REINDEER_C = {"hero": "#7B5E47", "hero2": "#EDE5D6", "hero3": "#5A4433", "mark": "#21170F", "antler": "#B79A6E", "antler2": "#8F774F",
              "tent": "#D8C4A0", "snow": "#F4F7FA", "snow2": "#DCE6EE", "light": "#FFFFFF"}
OWL_C = {"hero": "#FBFAF6", "hero2": "#DEDBD2", "mark": "#2A2A30", "eye": "#F4C430", "post": "#7A5A3E", "snow": "#BCD3E2",
         "snow2": "#9DBBD0", "light": "#FFFFFF"}
PUFFIN_C = {"dark": "#1D1F26", "light": "#FFFFFF", "face": "#F1F0EC", "hero2": "#F6C445", "pop": "#EE6B2C", "pop2": "#D8402A",
            "beakbase": "#56677A", "eyeliner": "#6B7682", "mark": "#111216", "fishc": "#C6D2DB", "turf": "#6E9F4E",
            "cliff": "#8C7A68"}
BELUGA_C = {"hero": "#F6F7F7", "hero2": "#D2DCE2", "mark": "#2C3A45", "pop": "#E4572E", "pop2": "#F6C445", "dark": "#1E2A36"}

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
            fixes={"sky": ["sky2", "glow2", "#8EC3DD", "#79B2D2"], "far": ["mid", "near"], "near": ["mid", "deep"]}),
    # sea otter
    Concept("seaotter-portrait", "animal-sea-otter", "Sea otter", otter_portrait, NO_GOLD, OTTER_C,
            checks=[("hero2", "sky"), ("hero2", "mid"), ("hero", "mid"), ("hero", "near"), ("hero2", "far")],
            fixes={"sky": ["sky2", "far", "mid", "near"], "mid": ["near", "far"], "near": ["deep", "mid"], "far": ["mid", "near"]}),
    Concept("seaotter-float", "animal-sea-otter", "Floating otter", otter_float, NO_GOLD, OTTER_C,
            checks=[("hero", "mid"), ("hero", "near"), ("hero2", "mid"), ("pop", "hero")],
            fixes={"mid": ["far", "near"], "near": ["deep", "far"]}),
    # beaver
    Concept("beaver-portrait", "animal-beaver", "Beaver", beaver_portrait, overrides=BEAVER_C,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero", "water"), ("hero", "mid")],
            fixes={"glow": ["glow2", "light", "far"], "sky": ["sky2", "far"], "mid": ["far", "near"]}),
    Concept("beaver-tree", "animal-beaver", "Busy beaver", beaver_lodge, NO_GOLD, BEAVER_C,
            checks=[("hero", "ground"), ("hero", "water"), ("hero", "sky"), ("bark", "sky"), ("hero", "bark2")],
            fixes={"ground": ["light", "far", "mid"], "sky": ["sky2"]}),
    # raccoon
    Concept("raccoon-portrait", "animal-raccoon", "Raccoon", raccoon_portrait, overrides=RACCOON_C,
            checks=[("hero", "glow"), ("light", "glow"), ("hero", "sky")],
            fixes={"glow": ["near", "mid", "deep", "far"], "sky": ["sky2", "far"]}),
    Concept("raccoon-log", "animal-raccoon", "Night prowler", raccoon_log, overrides=RACCOON_C,
            checks=[("hero", "sky"), ("hero", "deep"), ("hero", "bark"), ("hero", "glow")],
            fixes={"sky": ["sky2", "far"], "deep": ["near", "dark"], "glow": ["glow2", "light"]}),
    # mountain goat
    Concept("mtgoat-portrait", "animal-mountain-goat", "Mountain goat", goat_portrait, overrides=GOAT_C,
            checks=[("hero", "sky"), ("hero", "mid"), ("hero2", "near"), ("hero2", "mid")],
            fixes={"sky": ["far", "mid", "near"], "mid": ["near", "deep"], "near": ["deep", "dark"]}),
    Concept("mtgoat-cliff", "animal-mountain-goat", "Cliff hanger", goat_cliff, overrides=GOAT_C,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "near"), ("hero", "mid")],
            fixes={"sky": ["sky2", "far", "mid"], "far": ["mid", "near"], "near": ["deep", "dark"], "mid": ["near", "deep"]}),
    # alligator
    Concept("gator-portrait", "animal-alligator", "Alligator", gator_portrait, overrides=GATOR_C,
            checks=[("hero", "sky"), ("hero", "glow"), ("hero", "mid"), ("hero", "near")],
            fixes={"sky": ["sky2", "glow2", "light"], "mid": ["far", "sky2"], "near": ["far", "mid"]}),
    Concept("gator-swamp", "animal-alligator", "Cypress swamp", gator_swamp, overrides=GATOR_C,
            checks=[("hero", "mid"), ("hero", "glow"), ("dark", "sky"), ("hero2", "near"), ("dark", "glow")],
            fixes={"mid": ["far", "glow2", "sky2"], "near": ["deep", "mid"], "sky": ["sky2", "far", "mid"]}),
    # manatee
    Concept("manatee-portrait", "animal-manatee", "Manatee", manatee_portrait, ["coastal", "dusk", "meadow", "blush"], MANATEE_C,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "far"), ("hero", "sky2")],
            fixes={"mid": ["near", "deep"], "far": ["near", "sky2"], "near": ["deep"]}),
    Concept("manatee-spring", "animal-manatee", "Gentle giant", manatee_spring, ["coastal", "dusk", "meadow", "blush"], MANATEE_C,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "far")],
            fixes={"mid": ["near", "deep"], "far": ["sky2", "near"], "near": ["deep"]}),
    # orca
    Concept("orca-breach", "animal-orca", "Breaching orca", orca_breach, NO_GOLD, ORCA_C,
            checks=[("hero", "sky"), ("hero", "mid"), ("hero", "glow"), ("hero", "near"), ("light", "sky")],
            fixes={"sky": ["sky2", "far"], "mid": ["far", "near"], "near": ["far", "mid"]}),
    Concept("orca-islands", "animal-orca", "Orcas & islands", orca_islands, NO_GOLD, ORCA_C,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "far"), ("light", "far")],
            fixes={"mid": ["far", "sky2"], "near": ["mid", "far"], "far": ["sky2", "mid"]}),
    # hummingbird
    Concept("hummingbird-portrait", "animal-hummingbird", "Hummingbird", humming_portrait, overrides=HUMMING_C,
            checks=[("hero", "glow"), ("pop", "glow"), ("wing", "glow"), ("wing", "sky")],
            fixes={"glow": ["glow2", "light", "sky2", "far"], "sky": ["sky2", "far", "mid"]}),
    Concept("hummingbird-flowers", "animal-hummingbird", "Sipping nectar", humming_flowers, overrides=HUMMING_C,
            checks=[("hero", "sky"), ("hero", "far"), ("flower", "sky"), ("wing", "sky"), ("hero", "glow"), ("wing", "far")],
            fixes={"sky": ["sky2", "glow2"], "far": ["mid", "near"], "glow": ["glow2", "light", "far"]}),
    # arctic fox
    Concept("arcticfox-portrait", "animal-arctic-fox", "Arctic fox", fox_portrait, overrides=FOX_C,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "mid")],
            fixes={"sky": ["mid", "near", "deep"], "far": ["near", "deep", "mid"], "mid": ["deep", "near"]}),
    Concept("arcticfox-curled", "animal-arctic-fox", "Curled up in the snow", fox_curled, overrides=FOX_C,
            checks=[("hero", "ice"), ("hero", "sky"), ("hero", "far"), ("ice", "far")],
            fixes={"sky": ["mid", "near", "deep"], "far": ["near", "deep", "mid"]}),
    # walrus
    Concept("walrus-portrait", "animal-walrus", "Walrus", walrus_portrait, NO_GOLD, WALRUS_C,
            checks=[("hero", "sky"), ("hero", "mid"), ("hero2", "mid"), ("hero2", "sky"), ("tusk", "near"), ("tusk", "hero2")],
            fixes={"mid": ["near", "far", "deep"], "sky": ["sky2", "far"], "near": ["deep"]}),
    Concept("walrus-rock", "animal-walrus", "Walrus haul-out", walrus_rock, NO_GOLD, WALRUS_C,
            checks=[("hero", "rock"), ("hero", "mid"), ("hero", "far"), ("tusk", "rock"), ("light", "sky")],
            fixes={"mid": ["near", "far"], "far": ["sky2", "mid"], "sky": ["sky2", "far"]}),
    # narwhal
    Concept("narwhal-portrait", "animal-narwhal", "Narwhal", narwhal_portrait, ["coastal", "dusk", "meadow", "blush"], NARWHAL_C,
            checks=[("hero", "mid"), ("hero", "near"), ("tusk", "mid"), ("tusk", "far"), ("hero2", "near")],
            fixes={"mid": ["near", "deep"], "near": ["deep", "mid"], "far": ["mid", "near"]}),
    Concept("narwhal-ice", "animal-narwhal", "Narwhals in the ice", narwhal_ice, NO_GOLD, NARWHAL_C,
            checks=[("hero", "mid"), ("tusk", "sky"), ("tusk", "far"), ("light", "far"), ("hero", "near")],
            fixes={"sky": ["sky2", "far", "mid"], "far": ["mid", "near"], "mid": ["far", "near"], "near": ["deep"]}),
    # reindeer
    Concept("reindeer-portrait", "animal-reindeer", "Reindeer", reindeer_portrait, overrides=REINDEER_C,
            checks=[("hero", "sky"), ("antler", "sky"), ("hero2", "far"), ("hero2", "mid"), ("hero", "far")],
            fixes={"sky": ["sky2", "far", "mid"], "far": ["mid", "near", "deep"], "mid": ["near", "deep"]}),
    Concept("reindeer-lapland", "animal-reindeer", "Lapland lights", reindeer_lapland, overrides=REINDEER_C,
            checks=[("hero", "snow"), ("hero", "far"), ("antler", "sky"), ("antler", "far"), ("tent", "far"), ("hero", "sky")],
            fixes={"far": ["mid", "near", "deep"], "sky": ["sky2", "far", "mid"], "tent": ["#B8966A", "light"]}),
    # snowy owl
    Concept("snowyowl-portrait", "animal-snowy-owl", "Snowy owl", owl_portrait, overrides=OWL_C,
            checks=[("hero", "sky"), ("hero", "far"), ("hero2", "sky"), ("hero", "glow")],
            fixes={"sky": ["mid", "near", "deep"], "far": ["near", "deep"], "glow": ["glow2", "pop"]}),
    Concept("snowyowl-flight", "animal-snowy-owl", "Owl in flight", owl_flight, overrides=OWL_C,
            checks=[("hero", "sky"), ("hero", "glow"), ("hero", "far"), ("hero", "snow")],
            fixes={"glow": ["pop", "near", "deep", "hero"], "sky": ["mid", "near", "deep"], "far": ["near", "deep"]}),
    # puffin
    Concept("puffin-portrait", "animal-puffin", "Puffin", puffin_portrait, NO_GOLD, PUFFIN_C,
            checks=[("dark", "sky"), ("face", "sky"), ("pop", "sky"), ("dark", "mid"), ("dark", "near"), ("face", "glow")],
            fixes={"sky": ["sky2", "far", "mid"], "mid": ["far", "near"], "near": ["mid", "far"], "glow": ["glow2", "pop"]}),
    Concept("puffin-cliff", "animal-puffin", "Puffin with fish", puffin_cliff, NO_GOLD, PUFFIN_C,
            checks=[("dark", "sky"), ("dark", "far"), ("dark", "mid"), ("face", "mid"), ("pop", "mid"), ("dark", "turf")],
            fixes={"sky": ["sky2", "far"], "mid": ["far", "near"], "far": ["sky2", "mid"]}),
    # beluga
    Concept("beluga-portrait", "animal-beluga-whale", "Beluga", beluga_portrait, ["coastal", "dusk", "meadow", "blush"], BELUGA_C,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "far"), ("hero", "sky2")],
            fixes={"mid": ["near", "deep"], "far": ["near", "mid"], "sky2": ["far", "mid"], "near": ["deep"]}),
    Concept("beluga-kayak", "animal-beluga-whale", "Kayaking with belugas", beluga_kayak, NO_GOLD, BELUGA_C,
            checks=[("hero", "near"), ("hero", "deep"), ("pop", "near"), ("pop", "mid"), ("dark", "sky")],
            fixes={"near": ["mid", "deep"], "deep": ["near"], "mid": ["far", "sky2"], "sky": ["sky2", "far"]}),
]
