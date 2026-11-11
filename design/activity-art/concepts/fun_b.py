"""Nightlife & fun (b): three ideas each for nightclubs, full moon parties, karaoke, casinos, rooftop
parties, bar hopping, zoos, escape rooms, go-karting and open-air cinema."""
import math

from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group, GIRAFFE

ALL = ["golden", "coastal", "meadow", "blush", "dusk"]
SEA = ["coastal", "meadow", "blush", "dusk"]
NIGHT_FIX = {"dark": ["#343F63", "far", "mid"]}


# ================================================================ private helpers
def _clip(d: Drawing, fn):
    """Clip to the sticker circle in both styles."""
    d.raw('<g clip-path="url(#clip)">', '<g clip-path="url(#clip)">')
    fn()
    d.raw("</g>", "</g>")


_CLIPS = [0]


def _clip_to(d: Drawing, path: str, fn):
    """Clip the shapes drawn by fn to an arbitrary path (both styles)."""
    _CLIPS[0] += 1
    cid = f"fb{_CLIPS[0]}"
    svg = f'<clipPath id="{cid}"><path d="{path}"/></clipPath><g clip-path="url(#{cid})">'
    d.raw(svg, svg)
    fn()
    d.raw("</g>", "</g>")


def _night(d: Drawing):
    """A night sky that still follows the palette: the darkest landscape colour, edge to edge."""
    d.band("deep", "M-30 -30 H230", shadow=False, line=False)


def _stars(d: Drawing, pts, role="light"):
    for x, y, r in pts:
        d.marks(role, circle(x, y, r))


def _sparkle(x, y, r):
    """A four-point twinkle."""
    k = r * 0.22
    return (f"M{x} {y - r} Q{x + k} {y - k} {x + r} {y} Q{x + k} {y + k} {x} {y + r} "
            f"Q{x - k} {y + k} {x - r} {y} Q{x - k} {y - k} {x} {y - r}Z")


def _star(x, y, r, k=0.42, n=5, rot=-90):
    pts = []
    for i in range(2 * n):
        a = math.radians(rot + i * 180 / n)
        rr = r if i % 2 == 0 else r * k
        pts.append(f"{x + rr * math.cos(a):.1f} {y + rr * math.sin(a):.1f}")
    return "M" + " L".join(pts) + "Z"


def _note(x, y, s=1.0):
    """A quaver: head, stem and flag, as one path."""
    return (ellipse(x, y, 4.6 * s, 3.4 * s) + f" M{x + 3 * s} {y - 1 * s} V{y - 17 * s} "
            f"C{x + 6 * s} {y - 12 * s} {x + 12 * s} {y - 12 * s} {x + 11 * s} {y - 5 * s} "
            f"C{x + 10 * s} {y - 9 * s} {x + 7 * s} {y - 10 * s} {x + 5 * s} {y - 10 * s} V{y - 1 * s}Z")


def _annulus(cx, cy, r1, r2, a1, a2):
    """A segment of a ring between angles a1 and a2 (degrees)."""
    p = lambda r, a: f"{cx + r * math.cos(math.radians(a)):.1f} {cy + r * math.sin(math.radians(a)):.1f}"
    big = 1 if (a2 - a1) % 360 > 180 else 0
    return f"M{p(r2, a1)} A{r2} {r2} 0 {big} 1 {p(r2, a2)} L{p(r1, a2)} A{r1} {r1} 0 {big} 0 {p(r1, a1)}Z"


def _bulbs(d: Drawing, x0, y0, x1, y1, sag, n, roles, r=2.6, spot=True):
    """Festoon lights on a sagging string."""
    cx, cy = (x0 + x1) / 2, max(y0, y1) + sag
    d.stroke("dark", f"M{x0} {y0} Q{cx} {cy} {x1} {y1}", 1.3)
    for i in range(1, n + 1):
        t = i / (n + 1)
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1
        d.shape(roles[i % len(roles)], circle(round(x, 1), round(y + r, 1), r), shadow=False, spot=spot)


def _palm(d: Drawing, x0, y0, x1, y1, s=1.0, role="dark", w=5):
    """A palm tree: trunk from the ground (x0, y0) bending to the crown (x1, y1)."""
    d.limb(role, f"M{x0} {y0} Q{x0 + (x1 - x0) * 0.1:.1f} {(y0 + y1) / 2:.1f} {x1} {y1}", w * s)

    def crown():
        for f in ["M0 0 C10 -13 30 -13 40 4 C30 -4 14 -4 0 0Z", "M0 0 C6 -16 22 -24 34 -18 C22 -16 10 -10 0 0Z",
                  "M0 0 C-10 -13 -30 -13 -40 4 C-30 -4 -14 -4 0 0Z", "M0 0 C-6 -16 -22 -24 -34 -18 C-22 -16 -10 -10 0 0Z",
                  "M0 0 C-3 -14 1 -24 7 -28 C6 -18 4 -8 0 0Z"]:
            d.shape(role, f, shadow=False)
    group(d, f"translate({x1} {y1}) scale({s})", crown)


def _skyline(base, blocks):
    """A city silhouette: blocks = [(x, width, height)], sitting on y=base."""
    p = f"M-30 {base}"
    for x, w, h in blocks:
        p += f" L{x} {base} V{base - h} H{x + w} V{base}"
    return p + f" L230 {base} V230 H-30Z"


def _checker(x0, y0, w, h, nx, ny, amp=0.0, waves_=1.0, skew=0.0, odd=0):
    """Chequered cells of a (wavy) flag as one path; cells where (i + j) % 2 == odd."""
    def pt(u, v):
        x = x0 + u * w / nx
        y = y0 + v * h / ny + amp * math.sin(u / nx * math.pi * 2 * waves_) + skew * u / nx
        return f"{x:.1f} {y:.1f}"
    p = ""
    for i in range(nx):
        for j in range(ny):
            if (i + j) % 2 == odd:
                p += f"M{pt(i, j)} L{pt(i + 1, j)} L{pt(i + 1, j + 1)} L{pt(i, j + 1)}Z "
    return p


def _flag_outline(x0, y0, w, h, nx, amp, waves_=1.0, skew=0.0):
    top = [(x0 + u * w / nx, y0 + amp * math.sin(u / nx * math.pi * 2 * waves_) + skew * u / nx) for u in range(nx + 1)]
    bot = [(x, y + h) for x, y in top]
    pts = top + bot[::-1]
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"


def _mic(d: Drawing, body="hero", collar="hero2", head="light", grid="mark", spot=False):
    """A handheld microphone pointing up, head centred on (0, 0), about 80 tall."""
    d.shape(body, "M-9 14 L9 14 L5 66 C5 70 -5 70 -5 66Z", spot=spot)
    d.shape(collar, rrect(-12, 8, 24, 10, 3), shadow=False)
    d.shape(head, circle(0, 0, 15))
    _clip_to(d, circle(0, 0, 15), lambda: d.stroke(grid, "M-16 -8 H16 M-16 0 H16 M-16 8 H16 M-8 -16 V16 M0 -16 V16 M8 -16 V16", 1.1))


def _chip(d: Drawing, x, y, rx, ry, role, h=5, spot=False, top=True):
    """A casino chip seen at an angle, sitting with its base on y."""
    d.shape(role, f"M{x - rx} {y - h} V{y} A{rx} {ry} 0 0 0 {x + rx} {y} V{y - h}Z", spot=spot)
    if top:
        d.shape(role, ellipse(x, y - h, rx, ry), shadow=False, spot=spot)
        d.stroke("light", ellipse(x, y - h, rx * 0.66, ry * 0.66), 1.6, line=False)
        dash = ""
        for a in [0, 60, 120, 180, 240, 300]:
            c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
            dash += f"M{x + rx * 0.8 * c:.1f} {y - h + ry * 0.8 * s:.1f} L{x + rx * c:.1f} {y - h + ry * s:.1f} "
        d.stroke("light", dash, 2.2, line=False)


# ================================================================ NIGHTCLUB
SILVER = {"silver": "#DCE3EC", "silver2": "#9AA7B9"}


def club_discoball(d: Drawing):
    _night(d)
    if d.paper:
        d.raw(f'<g opacity=".3"><path d="M100 96 L-10 200 L30 210Z" fill="{d.c["pop"]}"/>'
              f'<path d="M100 96 L210 190 L190 214Z" fill="{d.c["hero2"]}"/>'
              f'<path d="M100 96 L84 220 L112 220Z" fill="{d.c["glow2"]}"/></g>')
    _stars(d, [(34, 70, 1.3), (168, 46, 1.2), (150, 156, 1.3), (52, 150, 1.1)])
    d.band("near", "M-30 172 Q100 164 230 172", line=False)
    for x, y in [(40, 182), (78, 176), (128, 178), (164, 184)]:
        d.shape("pop" if x % 3 else "hero2", ellipse(x, y, 9, 3), shadow=False, line=False)
    d.stroke("silver2", "M100 -10 V50", 2)
    d.shape("hero2", rrect(92, 46, 16, 9, 2.5))
    d.shape("silver", circle(100, 94, 42), spot=True)

    def facets():
        p = ""
        for y in range(60, 136, 10):
            p += f"M50 {y} H150 "
        for rx in [14, 27, 37]:
            p += ellipse(100, 94, rx, 42) + " "
        p += "M100 50 V140"
        d.stroke("silver2", p, 1.3)
        for x, y, role in [(72, 62, "light"), (84, 70, "light"), (70, 80, "light"), (114, 62, "glow2"), (124, 90, "pop"),
                           (88, 110, "hero2"), (112, 120, "pop"), (62, 100, "glow2")]:
            d.shape(role, rrect(x, y, 9, 8, 1.5), shadow=False, line=False)
        if d.paper:
            d.raw(f'<path d="M142 94 A42 42 0 0 1 100 136 A42 42 0 0 0 126 60 A42 42 0 0 1 142 94Z" fill="{d.c["silver2"]}" opacity=".45"/>')
    _clip_to(d, circle(100, 94, 42), facets)
    for x, y, r, role in [(46, 46, 9, "light"), (156, 76, 11, "glow2"), (150, 126, 6, "light"), (44, 112, 7, "glow2"), (62, 30, 5, "glow2")]:
        d.marks(role, _sparkle(x, y, r))


def club_decks(d: Drawing):
    _night(d)
    if d.paper:
        d.raw(f'<g opacity=".28"><path d="M20 -10 L60 -10 L104 120Z" fill="{d.c["pop"]}"/>'
              f'<path d="M150 -10 L190 -10 L110 120Z" fill="{d.c["hero2"]}"/></g>')
    _stars(d, [(100, 28, 1.3), (40, 80, 1.2), (164, 84, 1.2)])
    for x, y, s in [(46, 56, 0.9), (150, 50, 1.0)]:
        d.marks("light", _note(x, y, s))
    d.shape("dark", rrect(18, 150, 164, 60, 4), line=False)
    d.shape("hero", rrect(20, 78, 160, 86, 12))
    d.shape("hero2", rrect(20, 150, 160, 14, 6), shadow=False, spot=True)
    d.shape("dark", circle(78, 114, 36))
    d.stroke("mark", circle(78, 114, 29) + " " + circle(78, 114, 22), 1, line=False)
    d.shape("pop", circle(78, 114, 12), shadow=False, spot=True)
    d.marks("light", circle(78, 114, 2.4))
    d.shape("light", "M64 92 Q72 88 80 90 L79 94 Q72 92 66 95Z", shadow=False, line=False)
    # tone arm
    d.shape("light", circle(140, 92, 7))
    d.limb("light", "M140 92 L142 124 L120 138", 3.5)
    d.shape("light", rrect(110, 133, 12, 9, 2), extra='transform="rotate(-30 116 137)"')
    for x in [138, 154, 168]:
        d.shape("dark", rrect(x - 2, 104, 4, 26, 2), shadow=False)
    for x, y in [(154, 112), (138, 122), (168, 116)]:
        d.shape("light", rrect(x - 5, y - 2.5, 10, 5, 1.5), shadow=False)


def club_floor(d: Drawing):
    _night(d)
    if d.paper:
        d.raw(f'<g opacity=".3"><path d="M10 -10 L34 -10 L120 150 L90 150Z" fill="{d.c["glow2"]}"/>'
              f'<path d="M166 -10 L190 -10 L110 150 L80 150Z" fill="{d.c["pop"]}"/></g>')
    _stars(d, [(100, 30, 1.4), (60, 48, 1.1), (142, 52, 1.1)])
    d.shape("light", circle(22, 6, 12), shadow=False, line=False)
    d.shape("light", circle(178, 6, 12), shadow=False, line=False)
    vx, vy = 100, 20
    rows = [92, 104, 120, 142, 172, 214]
    cols = [-160 + 52 * k for k in range(10)]
    roles = ["pop", "hero2", "far", "glow2", "hero", "light"]
    for i in range(len(rows) - 1):
        for j in range(len(cols) - 1):
            def x_at(xb, y):
                return vx + (xb - vx) * (y - vy) / (214 - vy)
            y0, y1 = rows[i], rows[i + 1]
            a, b = cols[j], cols[j + 1]
            quad = f"M{x_at(a, y0):.1f} {y0} L{x_at(b, y0):.1f} {y0} L{x_at(b, y1):.1f} {y1} L{x_at(a, y1):.1f} {y1}Z"
            role = roles[(i * 2 + j * 3) % len(roles)]
            d.shape(role, quad, shadow=False, spot=(i + j) % 3 == 0, line=(i + j) % 3 == 0)
    d.stroke("deep", "".join(f"M-30 {y} H230 " for y in rows), 1.6, line=False)
    if not d.paper:
        grid = "".join(f"M-30 {y} H230 " for y in rows[1:])
        grid += "".join(f"M{vx + (xb - vx) * (92 - vy) / (214 - vy):.1f} 92 L{xb} 214 " for xb in cols)
        d.raw("", f'<path d="{grid}" fill="none" stroke="{d.c["ink"]}" stroke-width="2" stroke-linecap="round"/>')
    # dancers: heads and raised arms
    heads = [(36, 150, 9), (74, 138, 10), (126, 140, 10), (166, 152, 9)]
    for x, y, r in heads:
        d.limb("dark", f"M{x - r * 0.9} {y + r * 1.6} L{x - r * 1.5} {y - r * 2.2}", r * 0.42, shadow=False)
        d.limb("dark", f"M{x + r * 0.9} {y + r * 1.6} L{x + r * 1.6} {y - r * 2.0}", r * 0.42, shadow=False)
    body = "M-30 230 V190"
    for x, y, r in heads:
        body += (f" L{x - r * 1.8:.1f} {y + r * 2.6:.1f} Q{x - r * 1.8:.1f} {y + r * 1.3:.1f} {x - r * 0.7:.1f} {y + r * 1.1:.1f}"
                 f" A{r} {r} 0 1 1 {x + r * 0.7:.1f} {y + r * 1.1:.1f} Q{x + r * 1.8:.1f} {y + r * 1.3:.1f} {x + r * 1.8:.1f} {y + r * 2.6:.1f}")
    body += " L230 190 V230Z"
    _clip(d, lambda: d.shape("dark", body))


# ================================================================ FULL MOON PARTY
NEON = {"n1": "#FF4FB3", "n2": "#B8F23A", "n3": "#3DE0F2", "n4": "#FFE14D"}


def fullmoon_beach(d: Drawing):
    _night(d)
    _stars(d, [(30, 60, 1.2), (164, 40, 1.3), (150, 92, 1.1), (56, 30, 1.1), (178, 76, 1)])
    d.disc("glow2", 100, 66, 34)
    d.marks("glow", circle(88, 58, 5) + circle(110, 76, 7) + circle(108, 50, 3.4) + circle(84, 80, 3))
    d.band("dark", "M-30 112 L10 96 Q30 88 50 104 L60 112 H140 L160 104 Q180 92 230 108", line=False)
    d.band("mid", waves(112, 2, 30))
    d.stroke("glow2", "M86 120 H114 M80 128 H120 M90 136 H110 M84 144 H116", 2.8, line=False)
    d.band("ground", "M-30 152 Q100 142 230 152")
    _palm(d, 18, 156, 34, 92, 0.8)
    _palm(d, 184, 154, 168, 96, 0.75)
    heads = [(30, 168, 7), (58, 162, 7.5), (88, 166, 7), (116, 160, 7.5), (146, 166, 7), (174, 162, 7.5)]
    for k, (x, y, r) in enumerate(heads):
        if k % 2 == 0:
            d.limb("dark", f"M{x + r} {y + r * 1.6} L{x + r * 1.8} {y - r * 2}", r * 0.6, shadow=False)
    body = "M-30 230 V190"
    for x, y, r in heads:
        body += (f" L{x - r * 1.8:.1f} {y + r * 2.6:.1f} Q{x - r * 1.8:.1f} {y + r * 1.3:.1f} {x - r * 0.7:.1f} {y + r * 1.1:.1f}"
                 f" A{r} {r} 0 1 1 {x + r * 0.7:.1f} {y + r * 1.1:.1f} Q{x + r * 1.8:.1f} {y + r * 1.3:.1f} {x + r * 1.8:.1f} {y + r * 2.6:.1f}")
    body += " L230 190 V230Z"
    _clip(d, lambda: d.shape("dark", body))
    for x, y, role in [(30, 182, "n1"), (58, 178, "n2"), (88, 182, "n3"), (116, 176, "n4"), (146, 182, "n1"), (174, 178, "n3"),
                       (36, 190, "n2"), (64, 190, "n4"), (122, 188, "n2"), (152, 192, "n4")]:
        d.shape(role, circle(x, y, 2.6), shadow=False, spot=True)


def fullmoon_bucket(d: Drawing):
    _night(d)
    _stars(d, [(40, 104, 1.2), (164, 40, 1.3), (174, 100, 1.1), (130, 24, 1.1)])
    d.disc("glow2", 66, 62, 32)
    d.marks("glow", circle(56, 54, 5) + circle(76, 72, 6) + circle(74, 48, 3))
    d.band("mid", waves(124, 2, 30))
    d.band("ground", "M-30 146 Q100 136 230 146")
    d.limb("n1", "M104 104 L80 40", 4.5, spot=True)
    d.limb("n2", "M112 104 L132 36", 4.5)
    d.limb("n3", "M100 104 L114 46", 4.5)
    d.stroke("dark", "M66 100 C62 60 138 60 134 100", 2.4)
    d.shape("hero", "M62 98 H138 L130 172 C130 176 70 176 70 172Z")
    d.shape("pop", ellipse(100, 98, 38, 7), shadow=False, spot=True)
    d.shape("light", rrect(80, 92, 10, 8, 2) + " " + rrect(104, 90, 10, 8, 2), shadow=False, line=False)
    d.shape("hero2", "M64 112 H136 L135 122 H65Z", shadow=False, spot=True)
    d.stroke("light", "M74 110 L78 164", 2.4, line=False)
    d.marks("dark", circle(64, 100, 2) + circle(136, 100, 2))


def fullmoon_paint(d: Drawing):
    _night(d)
    _stars(d, [(40, 50, 1.2), (100, 24, 1.3), (60, 92, 1.1)])
    d.disc("glow2", 146, 58, 28)
    d.marks("glow", circle(138, 50, 4.5) + circle(154, 66, 6) + circle(152, 46, 3))
    d.band("ground", "M-30 150 Q100 140 230 150")
    # splatters
    for x, y, r, role in [(30, 120, 4, "n1"), (40, 132, 2.4, "n1"), (176, 120, 3.6, "n3"), (168, 108, 2.2, "n3"),
                          (100, 64, 3.2, "n4"), (86, 72, 2, "n4"), (24, 166, 3, "n2"), (178, 170, 3, "n4")]:
        d.shape(role, circle(x, y, r), shadow=False, spot=True)

    def pot(x, y, s, role):
        def draw():
            d.shape("light", "M-20 0 V36 C-20 44 20 44 20 36 V0Z")
            d.shape(role, ellipse(0, 0, 20, 6))
            d.shape(role, "M-20 0 C-20 10 -16 16 -14 22 C-12 26 -8 24 -8 18 C-8 12 -4 8 -2 8 C0 8 2 12 2 16 "
                          "C2 20 6 22 8 18 C10 12 16 10 20 0Z", shadow=False, spot=True)
            d.stroke("mark", "M-20 0 A20 6 0 0 0 20 0", 1.2, line=False)
        group(d, f"translate({x} {y}) scale({s})", draw)
    pot(56, 118, 1.0, "n1")
    pot(146, 124, 0.9, "n3")
    pot(100, 136, 1.15, "n2")

    def brush():
        d.limb("hero", "M0 0 L0 54", 6)
        d.shape("silver", rrect(-5, -12, 10, 14, 2))
        d.shape("n4", "M-5 -12 C-6 -20 -3 -30 0 -34 C3 -30 6 -20 5 -12Z", spot=True)
    group(d, "translate(84 96) rotate(-34)", brush)


# ================================================================ KARAOKE
def karaoke_mic(d: Drawing):
    d.disc("glow", 100, 84, 50, line=False)
    if d.paper:
        d.raw(f'<path d="M86 -10 H114 L156 190 H44Z" fill="{d.c["light"]}" opacity=".35"/>')
    d.band("near", "M-30 168 H230")
    d.shape("pop", "M-30 -30 H44 C40 30 40 120 50 172 H-30Z", spot=True)
    d.shape("pop", "M230 -30 H156 C160 30 160 120 150 172 H230Z", spot=True)
    d.stroke("deep", "M10 0 C8 60 12 120 20 172 M30 0 C26 60 28 120 36 172 M190 0 C192 60 188 120 180 172 M170 0 C174 60 172 120 164 172", 1.6, line=False)
    d.shape("pop", "M-30 -30 H230 V20 Q215 34 200 20 Q185 34 170 20 Q155 34 140 20 Q125 34 110 20 Q95 34 80 20 "
                   "Q65 34 50 20 Q35 34 20 20 Q5 34 -10 20 Q-20 30 -30 20Z")
    for x, y, s in [(146, 60, 0.9), (56, 70, 1.0)]:
        d.marks("dark", _note(x, y, s))
    d.limb("dark", "M100 120 V176", 4.5)
    d.shape("dark", ellipse(100, 178, 24, 6))
    d.limb("dark", "M84 104 C84 122 116 122 116 104", 3.2)
    d.shape("hero", rrect(80, 44, 40, 64, 20), spot=True)
    d.shape("light", rrect(84, 48, 32, 56, 16), shadow=False)
    d.stroke("mark", "M86 56 H114 M84 64 H116 M84 72 H116 M84 80 H116 M84 88 H116 M84 96 H116", 1.4)
    d.shape("hero", rrect(80, 74, 40, 6, 2), shadow=False, spot=True)
    d.marks("dark", circle(100, 112, 3))


def karaoke_screen(d: Drawing):
    d.disc("glow", 140, 52, 22)
    d.band("far", hills(160, 6), line=False)
    d.shape("dark", rrect(22, 44, 140, 92, 8))
    d.shape("deep", rrect(30, 52, 124, 76, 4), shadow=False)
    d.shape("dark", "M82 136 H102 L106 150 H78Z")
    d.shape("dark", rrect(66, 148, 52, 6, 3))
    # lyric lines, the sung part highlighted
    d.shape("light", rrect(44, 96, 96, 8, 4), shadow=False)
    d.shape("pop", rrect(44, 96, 50, 8, 4), shadow=False, spot=True)
    d.shape("far", rrect(52, 112, 80, 7, 3.5), shadow=False)
    d.shape("glow2", circle(98, 84, 5), shadow=False, spot=True)
    d.stroke("glow2", "M74 90 Q84 74 92 82", 1.6, line=False)
    for x, y, s in [(54, 74, 0.7), (132, 76, 0.7)]:
        d.marks("light", _note(x, y, s))
    group(d, "translate(148 106) rotate(24) scale(.9)", lambda: _mic(d, body="hero", collar="hero2", spot=True))
    d.band("near", "M-30 180 Q100 172 230 180", line=False)


def karaoke_duet(d: Drawing):
    d.disc("glow", 100, 92, 56)
    d.shape("glow2", _star(100, 92, 50, 0.55, 8, -90), shadow=False, line=False)
    for x, y, s, role in [(36, 70, 1.0, "dark"), (160, 58, 0.9, "dark"), (168, 132, 0.8, "dark")]:
        d.marks(role, _note(x, y, s))
    for x, y, r in [(46, 130, 6), (150, 30, 5), (64, 34, 4)]:
        d.marks("hero2", _sparkle(x, y, r))
    group(d, "translate(124 70) rotate(32)", lambda: _mic(d, body="pop", collar="hero2", spot=True))
    group(d, "translate(76 70) rotate(-32)", lambda: _mic(d, body="hero", collar="hero2"))


# ================================================================ CASINO
CASINO = {"felt": "#2E7D4F", "felt2": "#256B42", "red": "#D7263D", "blk": "#23232B", "gold": "#E8B84A", "wood": "#7A4A2A"}


def _die(d: Drawing, x, y, s, rot, pips, role="red"):
    def draw():
        d.shape(role, rrect(-25, -25, 50, 50, 10), spot=True)
        d.shape("light", rrect(-25, -25, 50, 50, 10), shadow=False, line=False, extra='opacity=".18"')
        pos = {1: [(0, 0)], 2: [(-12, -12), (12, 12)], 3: [(-12, -12), (0, 0), (12, 12)],
               4: [(-12, -12), (12, -12), (-12, 12), (12, 12)], 5: [(-12, -12), (12, -12), (0, 0), (-12, 12), (12, 12)],
               6: [(-12, -13), (12, -13), (-12, 0), (12, 0), (-12, 13), (12, 13)]}[pips]
        d.marks("light", " ".join(circle(px, py, 4.6) for px, py in pos))
    group(d, f"translate({x} {y}) rotate({rot}) scale({s})", draw)


def casino_dice(d: Drawing):
    d.disc("glow", 100, 80, 48, line=False)
    d.band("felt", "M-30 132 Q100 122 230 132")
    d.stroke("gold", "M-30 140 Q100 130 230 140", 2, line=False)
    for i, role in enumerate(["blk", "gold", "red", "blk"]):
        _chip(d, 152, 168 - i * 8, 22, 8, role, 8, spot=role == "red", top=i == 3)
    _chip(d, 60, 174, 20, 7, "gold", 8)
    _chip(d, 58, 164, 20, 7, "blk", 8)
    _die(d, 70, 104, 1.05, -14, 5)
    _die(d, 122, 116, 0.95, 16, 3)


def casino_roulette(d: Drawing):
    d.band("felt", "M-30 -30 H230", shadow=False, line=False)
    d.stroke("felt2", "M-30 40 H230 M-30 160 H230 M40 -30 V230 M160 -30 V230", 2, line=False)
    cx, cy = 100, 100
    d.shape("wood", circle(cx, cy, 76))
    d.shape("gold", circle(cx, cy, 68), shadow=False)
    d.shape("wood", circle(cx, cy, 64), shadow=False)
    n = 24
    for i in range(n):
        a1, a2 = -90 + i * 360 / n, -90 + (i + 1) * 360 / n
        role = "felt" if i == 0 else ("red" if i % 2 else "blk")
        d.shape(role, _annulus(cx, cy, 40, 60, a1, a2), shadow=False, spot=role == "red")
    d.stroke("gold", "".join(f"M{cx + 40 * math.cos(math.radians(-90 + i * 15)):.1f} {cy + 40 * math.sin(math.radians(-90 + i * 15)):.1f} "
                             f"L{cx + 60 * math.cos(math.radians(-90 + i * 15)):.1f} {cy + 60 * math.sin(math.radians(-90 + i * 15)):.1f} " for i in range(n)), 1, line=False)
    d.shape("wood", circle(cx, cy, 40))
    d.shape("gold", circle(cx, cy, 30), shadow=False)
    d.stroke("wood", "M70 100 H130 M100 70 V130 M79 79 L121 121 M121 79 L79 121", 1.4, line=False)
    d.limb("gold", "M82 100 H118 M100 82 V118", 4)
    d.marks("gold", circle(82, 100, 3.4) + circle(118, 100, 3.4) + circle(100, 82, 3.4) + circle(100, 118, 3.4))
    d.shape("gold", circle(cx, cy, 7))
    d.shape("light", circle(cx + 62 * math.cos(math.radians(-40)), cy + 62 * math.sin(math.radians(-40)), 4.8))


def casino_slot(d: Drawing):
    d.disc("glow", 100, 96, 56)
    for x, y, r in [(30, 60, 6), (172, 50, 5), (36, 140, 4)]:
        d.marks("hero2", _sparkle(x, y, r))
    # lever
    d.limb("dark", "M150 112 H160 V60", 5)
    d.shape("pop", circle(160, 56, 8), spot=True)
    d.shape("hero", "M36 66 C36 40 64 30 100 30 C136 30 152 40 152 66 V164 H36Z")
    d.shape("hero2", "M36 66 C36 40 64 30 100 30 C136 30 152 40 152 66 V70 H36Z", shadow=False, spot=True)
    for x in [54, 72, 90, 108, 126, 144]:
        d.shape("light", circle(x - 4, 52, 3), shadow=False)
    d.shape("dark", rrect(44, 80, 100, 44, 6), shadow=False)
    for x in [50, 82, 114]:
        d.shape("light", rrect(x, 85, 24, 34, 3), shadow=False)
        d.stroke("near", f"M{x + 12} 94 Q{x + 13} 99 {x + 8} 106 M{x + 12} 94 Q{x + 15} 100 {x + 17} 106 M{x + 12} 94 L{x + 15} 91", 1.4)
        d.shape("pop", circle(x + 8, 108, 4.5) + " " + circle(x + 17, 108, 4.5), shadow=False, spot=True)
    d.shape("dark", rrect(80, 132, 28, 6, 3), shadow=False)
    d.shape("dark", rrect(30, 160, 128, 12, 4))
    d.shape("hero2", rrect(58, 150, 72, 12, 3), shadow=False)
    for x, y in [(70, 182), (92, 186), (118, 182)]:
        d.shape("hero2", ellipse(x, y, 8, 3.5))
    d.stroke("mark", "M64 182 H76 M86 186 H98 M112 182 H124", 1, line=False)


# ================================================================ ROOFTOP PARTY
CITY = [(-30, 26, 40), (0, 22, 62), (26, 18, 48), (48, 24, 76), (76, 16, 54), (96, 22, 88), (122, 18, 58),
        (144, 26, 72), (174, 18, 50), (196, 40, 64)]


def _windows(d: Drawing, base, blocks, role="glow2"):
    p = ""
    for k, (x, w, h) in enumerate(blocks):
        for row in range(int(h // 14) - 1):
            for col in range(int(w // 8)):
                if (row * 3 + col + k) % 4 == 0:
                    p += rrect(x + 3 + col * 8, base - h + 8 + row * 14, 3.5, 5, 0.8) + " "
    if p:
        d.marks(role, p)


def rooftopparty_lights(d: Drawing):
    d.disc("glow", 100, 116, 46)
    d.band("far", _skyline(132, [(x, w, h * 0.7) for x, w, h in CITY]), line=False)
    d.band("mid", _skyline(140, [(x + 11, w, h * 0.55) for x, w, h in CITY[::-1]]))
    _windows(d, 140, [(x + 11, w, h * 0.55) for x, w, h in CITY[::-1]], "light")
    d.band("ground", "M-30 156 H230")
    d.shape("dark", rrect(-30, 136, 260, 4, 2))
    d.stroke("dark", "".join(f"M{x} 138 V156 " for x in range(-20, 230, 14)), 1.6)
    d.band("near", "M-30 172 H230", line=False)
    for x0, y0, x1, y1 in [(10, 20, 190, 34), (-10, 60, 210, 54)]:
        _bulbs(d, x0, y0, x1, y1, 26, 9, ["glow2", "pop", "hero2"], 3)

    def pot(x, s):
        def draw():
            d.shape("near", "M0 0 C-14 -8 -20 -24 -16 -38 C-8 -30 -4 -20 0 -10 C2 -22 6 -36 14 -42 C16 -28 10 -12 0 0Z")
            d.shape("hero", "M-11 0 H11 L8 18 H-8Z", spot=True)
        group(d, f"translate({x} 156) scale({s})", draw)
    pot(32, 1.0)
    pot(170, 0.9)
    d.limb("dark", "M100 128 V170", 3)
    d.shape("dark", ellipse(100, 172, 12, 3))
    d.shape("hero2", ellipse(100, 128, 20, 4))
    d.shape("light", "M88 108 H98 L95 120 H91Z M92 120 V127", shadow=False)
    d.stroke("light", "M93 120 V127", 1.4)
    d.shape("pop", "M104 112 H112 V127 H104Z")


def rooftopparty_watertower(d: Drawing):
    d.disc("glow", 150, 86, 26)
    blocks = [(x, w, h * 0.8) for x, w, h in CITY]
    d.band("far", _skyline(150, blocks))
    _windows(d, 150, blocks, "light")
    d.band("ground", "M-30 156 H230")
    d.shape("near", rrect(-30, 150, 260, 8, 2))
    # water tower on stilts
    d.limb("wood2", "M50 156 L56 112 M90 156 L84 112 M70 156 V112", 3.6)
    d.stroke("wood2", "M52 140 L88 124 M88 140 L52 124", 1.6)
    d.shape("wood", "M44 66 H96 V112 C96 116 44 116 44 112Z")
    d.stroke("wood2", "M44 76 H96 M44 92 H96 M44 106 H96", 2)
    d.stroke("wood2", "M56 66 V114 M70 66 V115 M84 66 V114", 0.9, line=False)
    d.shape("wood2", "M40 68 L70 36 L100 68Z")
    d.stroke("wood2", "M70 36 V28", 1.6)
    _bulbs(d, 98, 66, 200, 112, 10, 7, ["glow2", "pop", "hero2"], 3)
    _bulbs(d, 98, 80, 196, 140, 10, 6, ["pop", "hero2", "glow2"], 3)
    _bulbs(d, 6, 110, 46, 72, 12, 3, ["hero2", "glow2", "pop"], 3)
    d.band("near", "M-30 176 H230", line=False)


def rooftopparty_bubbly(d: Drawing):
    _night(d)
    _stars(d, [(30, 70, 1.2), (176, 60, 1.3), (60, 26, 1.1), (150, 30, 1.1)])
    d.disc("glow2", 152, 70, 14)
    blocks = [(x, w, h * 0.7) for x, w, h in CITY]
    d.band("near", _skyline(176, blocks))
    _windows(d, 176, blocks, "glow2")
    d.band("dark", "M-30 178 H230", line=False)
    for x, y, a, role in [(40, 96, 20, "pop"), (166, 104, -30, "hero2"), (64, 140, 50, "light"), (176, 140, 10, "pop"),
                          (120, 24, -20, "hero2"), (30, 130, 40, "hero2"), (96, 72, 30, "pop")]:
        d.shape(role, rrect(x - 3.5, y - 1.8, 7, 3.6, 1), shadow=False, extra=f'transform="rotate({a} {x} {y})"')
    # foam arcing up out of the neck
    d.limb("light", "M100 98 C88 74 76 62 58 56", 9)
    for x, y, r in [(54, 54, 7), (44, 58, 5), (60, 44, 5), (48, 46, 3.4), (70, 52, 3.6), (38, 66, 3)]:
        d.shape("light", circle(x, y, r), shadow=False)
    d.shape("cork", rrect(76, 22, 16, 13, 4), extra='transform="rotate(-30 84 28)"')
    d.stroke("light", "M94 40 L100 48 M100 34 L108 38", 1.6)

    def bottle():
        d.shape("bottle", "M-16 76 V12 C-16 -4 -6 -10 -5 -22 V-46 H5 V-22 C6 -10 16 -4 16 12 V76 C16 80 -16 80 -16 76Z", spot=True)
        d.shape("gold", "M-5.5 -48 H5.5 V-24 C8 -16 10 -12 11 -6 H-11 C-10 -12 -8 -16 -5.5 -24Z", shadow=False)
        d.shape("light", rrect(-13, 20, 26, 28, 3), shadow=False)
        d.shape("gold", rrect(-13, 28, 26, 6, 1), shadow=False)
        d.stroke("light", "M-9 2 V66", 2, line=False)
    group(d, "translate(124 132) rotate(-30)", bottle)


# ================================================================ BAR HOPPING
BEER = {"beer": "#F2A93B", "foam": "#FFF8EC", "olive": "#7FA34A", "wood": "#8A5A34", "wood2": "#6B4226", "wine": "#8E2C48"}


def barhop_round(d: Drawing):
    d.disc("glow", 100, 92, 54, line=False)
    d.shape("deep", rrect(-30, 50, 260, 6, 2), line=False)
    for x, h, role in [(18, 30, "dark"), (36, 38, "near"), (52, 26, "dark"), (148, 34, "near"), (164, 26, "dark"), (180, 40, "near")]:
        d.shape(role, f"M{x - 6} 50 V{50 - h + 12} C{x - 6} {50 - h + 6} {x - 3} {50 - h + 6} {x - 3} {50 - h} H{x + 3} "
                      f"C{x + 3} {50 - h + 6} {x + 6} {50 - h + 6} {x + 6} {50 - h + 12} V50Z", line=False)
    d.band("wood", "M-30 150 H230")
    d.shape("wood2", rrect(-30, 150, 260, 6, 1), shadow=False)
    # pint
    d.shape("light", "M38 66 H82 L78 150 H42Z")
    d.shape("beer", "M41 82 H79 L76 146 H44Z", shadow=False, spot=True)
    d.shape("foam", "M38 66 H82 V80 C76 86 70 78 64 84 C58 88 52 80 46 84 C42 86 40 82 38 80Z", shadow=False)
    d.stroke("light", "M50 92 L52 138", 2.4, line=False)
    d.marks("light", circle(64, 110, 1.6) + circle(58, 124, 1.3) + circle(68, 132, 1.5))
    # martini
    d.shape("light", "M96 70 H150 L123 104Z")
    d.shape("pop", "M101 74 H145 L123 101Z", shadow=False, spot=True)
    d.limb("light", "M123 104 V146", 3)
    d.shape("light", ellipse(123, 148, 15, 3.5))
    d.stroke("dark", "M112 64 L130 92", 1.6)
    d.shape("olive", circle(126, 86, 5), shadow=False)
    # shot
    d.shape("light", "M154 120 H178 L175 150 H157Z")
    d.shape("hero2", "M156 128 H176 L174 146 H158Z", shadow=False)
    d.marks("light", _sparkle(170, 100, 6))


def barhop_street(d: Drawing):
    _night(d)
    _stars(d, [(30, 70, 1.2), (170, 66, 1.1), (100, 22, 1.3)])
    d.disc("glow2", 150, 40, 14)
    facades = [(-4, 68, 74, "hero", "pop"), (64, 72, 60, "far", "hero2"), (136, 70, 80, "near", "pop")]
    for x, w, h, role, awn in facades:
        d.shape(role, f"M{x} 160 V{150 - h} H{x + w} V160Z")
        d.stroke("deep", f"M{x} {150 - h} H{x + w}", 2, line=False)
    for x, w, h, role, awn in facades:
        cx = x + w / 2
        d.shape("glow2", rrect(cx - 18, 118, 14, 30, 2), shadow=False, spot=True)
        d.shape("dark", rrect(cx + 4, 120, 14, 40, 2), shadow=False)
        aw = f"M{cx - 24} 106 H{cx + 24} L{cx + 28} 116"
        for k in range(7):
            xx = cx + 28 - (k + 1) * 8
            aw += f" Q{xx + 4} 122 {xx} 116"
        d.shape(awn, aw + "Z", shadow=False)
        d.stroke("light", f"M{cx - 12} 106 L{cx - 14} 116 M{cx} 106 V116 M{cx + 12} 106 L{cx + 14} 116", 2.2, line=False)
    # hanging signs
    for x, y, icon in [(64, 72, "pint"), (136, 66, "glass")]:
        d.stroke("dark", f"M{x} {y} H{x + 18} M{x + 8} {y} V{y + 4} M{x + 16} {y} V{y + 4}", 2)
        d.shape("light", rrect(x + 2, y + 4, 20, 20, 10))
        if icon == "pint":
            d.marks("dark", f"M{x + 7} {y + 9} H{x + 17} L{x + 16} {y + 20} H{x + 8}Z")
        else:
            d.marks("dark", f"M{x + 6} {y + 9} H{x + 18} L{x + 12} {y + 15}Z M{x + 11.2} {y + 15} H{x + 12.8} V{y + 19} H{x + 15} V{y + 20.5} H{x + 9} V{y + 19} H{x + 11.2}Z")
    _bulbs(d, -10, 50, 210, 44, 16, 9, ["glow2", "pop", "hero2"], 2.6)
    d.band("ground", "M-30 160 H230")
    d.stroke("deep", "M-30 172 H230 M10 160 L4 172 M50 160 L46 172 M90 160 V172 M130 160 L134 172 M170 160 L176 172 "
                     "M-30 186 H230 M26 172 L20 186 M70 172 L68 186 M112 172 L114 186 M152 172 L156 186", 1.2, line=False)


def _pin(d: Drawing, x, y, role, icon, spot=False):
    d.shape(role, f"M{x} {y} C{x - 6} {y - 10} {x - 16} {y - 18} {x - 16} {y - 30} A16 16 0 0 1 {x + 16} {y - 30} "
                  f"C{x + 16} {y - 18} {x + 6} {y - 10} {x} {y}Z", spot=spot)
    d.shape("light", circle(x, y - 30, 11), shadow=False)
    cx, cy = x, y - 30
    if icon == "pint":
        d.marks("dark", f"M{cx - 5} {cy - 6} H{cx + 5} L{cx + 4} {cy + 6} H{cx - 4}Z")
    elif icon == "cocktail":
        d.marks("dark", f"M{cx - 7} {cy - 6} H{cx + 7} L{cx + 0.8} {cy} V{cy + 5} H{cx + 4} V{cy + 6.5} H{cx - 4} V{cy + 5} H{cx - 0.8} V{cy}Z")
    else:
        d.marks("dark", f"M{cx - 5} {cy - 7} H{cx + 5} C{cx + 5} {cy - 1} {cx + 3} {cy + 1} {cx + 0.8} {cy + 1} V{cy + 5} H{cx + 4} "
                        f"V{cy + 6.5} H{cx - 4} V{cy + 5} H{cx - 0.8} V{cy + 1} C{cx - 3} {cy + 1} {cx - 5} {cy - 1} {cx - 5} {cy - 7}Z")


def barhop_route(d: Drawing):
    d.band("ground", "M-30 -30 H230", shadow=False, line=False)
    for x, y, w, h in [(14, 20, 40, 30), (62, 14, 50, 36), (120, 22, 34, 28), (162, 14, 40, 40), (8, 62, 30, 40),
                       (46, 64, 46, 26), (130, 58, 40, 30), (178, 62, 30, 36), (14, 112, 46, 30), (70, 104, 34, 40),
                       (112, 96, 40, 34), (160, 106, 40, 34), (20, 154, 40, 30), (68, 156, 50, 30), (128, 146, 30, 40), (166, 150, 40, 30)]:
        d.shape("far", rrect(x, y, w, h, 3), shadow=False, line=False)
    d.shape("mid", "M-30 92 C30 98 70 86 112 92 C150 96 190 88 230 92 V100 C190 96 150 104 112 100 C70 94 30 106 -30 100Z", shadow=False, line=False)
    d.shape("near", rrect(158, 130, 30, 24, 6), shadow=False, line=False)
    route = "M48 150 C40 120 60 100 92 104 C120 108 128 84 112 66 C100 52 120 40 146 50"
    d.stroke("dark", route, 3.2)
    d.stroke("ground", route, 1.4, line=False)
    if d.paper:
        d.raw(f'<path d="{route}" fill="none" stroke="{d.c["dark"]}" stroke-width="3.4" stroke-dasharray="5 5" stroke-linecap="round"/>')
    else:
        pass
    d.shape("dark", circle(92, 104, 4))
    _pin(d, 48, 160, "pop", "pint", spot=True)
    _pin(d, 100, 112, "hero", "cocktail")
    _pin(d, 148, 64, "pop", "wine", spot=True)


# ================================================================ ZOO
ELEPHANT = ("M46 120 C46 96 66 84 92 84 C108 84 120 88 128 96 C134 86 150 84 160 92 C168 99 168 112 162 120 "
            "C160 132 161 148 166 160 C168 166 163 171 158 166 C151 154 149 140 148 130 L144 132 L144 172 "
            "L132 172 L131 148 L118 148 L117 172 L105 172 L104 148 L80 146 L79 172 L67 172 L66 146 L58 145 "
            "L57 172 L45 172 L46 140 C44 134 44 126 46 120Z")
GIRAFFE_GOLD = {"hero": "#F6C453", "mark": "#A0522D", "tongue": "#5B3A6B", "skin": "#E8B48A", "leaf": "#6DAA4F", "wood": "#9A6B3F", "wood2": "#6B4226"}
SEAL = {"seal": "#5E6B7A", "seal2": "#8D99AE"}


def zoo_booth(d: Drawing):
    d.disc("glow", 156, 50, 15)
    d.shape("light", cloud(104, 30, 0.8))
    d.band("far", hills(132, 10))
    d.shape("near", circle(186, 112, 20), line=False)
    group(d, "translate(102 40) scale(-.66 .66)", lambda: d.shape("dark", GIRAFFE))
    d.band("mid", hills(158, 6, 20), line=False)
    # booth
    d.shape("hero", "M74 94 H154 V164 H74Z")
    d.shape("dark", rrect(84, 106, 60, 32, 2), shadow=False)
    d.stroke("light", "M114 106 V138", 1.6)
    d.shape("hero2", rrect(78, 136, 72, 8, 2))
    d.shape("light", "M104 130 H122 V138 H104Z", shadow=False)
    d.stroke("dark", "M117 130 V138", 1, line=False)
    aw = "M66 78 H162 L166 94"
    for k in range(8):
        xx = 166 - (k + 1) * 12.5
        aw += f" Q{xx + 6.25} 104 {xx} 94"
    d.shape("pop", aw + "Z", spot=True)
    for k in range(4):
        x = 66 + 25 * k + 6
        d.shape("light", f"M{x} 78 H{x + 12.5} L{x + 13} 94 Q{x + 6.5} 104 {x} 94Z", shadow=False)
    d.shape("hero", "M68 78 L114 48 L160 78Z")
    d.stroke("dark", "M114 48 V32", 1.6)
    d.shape("pop", "M114 32 L128 36 L114 40Z", shadow=False)
    d.band("ground", "M-30 164 H230")
    # paw prints on the path
    for x, y in [(40, 178), (62, 172)]:
        d.marks("dark", ellipse(x, y, 4, 3.2) + circle(x - 4, y - 5, 1.5) + circle(x, y - 6.5, 1.5) + circle(x + 4, y - 5, 1.5))


def zoo_seal(d: Drawing):
    d.disc("glow", 60, 70, 24)
    d.band("far", "M-30 150 H230", line=False)
    d.band("mid", waves(160, 3, 24))
    for x, y, r in [(38, 150, 2.6), (166, 152, 2.2), (154, 142, 1.8)]:
        d.marks("light", circle(x, y, r))
    # podium
    d.shape("hero", "M62 140 H138 V166 C138 172 62 172 62 166Z", spot=True)
    d.shape("hero2", ellipse(100, 140, 38, 7))
    d.marks("light", _star(100, 156, 7))
    # seal facing right, nose up
    seal = ("M64 140 C60 120 66 100 82 86 C92 78 100 70 106 60 C110 52 118 48 126 52 C134 56 138 62 136 66 "
            "L126 70 C120 80 118 94 120 108 C122 122 126 132 130 140Z")
    d.shape("seal", "M66 140 C56 142 46 140 40 132 C50 132 58 134 64 134Z")
    d.shape("seal", seal)
    d.shape("seal2", "M124 70 C118 84 116 100 118 116 C120 128 124 136 128 140 L114 140 C110 120 110 96 118 74Z", shadow=False, line=False)
    d.shape("seal", "M106 112 C114 122 122 128 134 128 C128 120 120 112 112 106Z", shadow=False)
    d.marks("dark", circle(118, 60, 2.6) + circle(136, 64, 2.4))
    d.stroke("dark", "M128 70 L140 72 M128 72 L138 76", 1, line=False)

    def ball():
        d.shape("light", circle(0, 0, 16), spot=False)
        d.shape("pop", "M0 -16 A16 16 0 0 1 14 -8 L0 0Z M14 8 A16 16 0 0 1 -14 8 L0 0Z", shadow=False, spot=True)
        d.shape("hero2", "M-14 -8 A16 16 0 0 1 0 -16 L0 0Z M14 -8 A16 16 0 0 1 14 8 L0 0Z", shadow=False)
        d.marks("light", circle(0, 0, 3))
    group(d, "translate(140 38) rotate(20)", ball)
    d.band("near", waves(178, 4, 30))
    d.shape("light", "M50 178 L54 166 L60 174 L64 160 L70 174 L76 166 L80 178Z")


def zoo_giraffe(d: Drawing):
    d.shape("light", cloud(130, 30, 1.0))
    d.shape("near", circle(28, 58, 24), line=False)
    d.shape("mid", circle(176, 132, 26), line=False)
    d.band("far", hills(150, 8))
    neck = "M98 86 L120 70 C134 100 154 150 176 214 L132 214 C122 160 112 122 98 86Z"
    d.shape("hero", neck)
    d.marks("mark", ellipse(122, 100, 5, 6) + ellipse(134, 126, 6, 7) + ellipse(120, 132, 4, 5) + ellipse(144, 154, 6, 7)
            + ellipse(130, 168, 5, 6) + ellipse(154, 186, 6, 7) + ellipse(112, 108, 3, 4))
    d.stroke("mark", "M120 70 C132 98 150 140 168 190", 4, line=False)
    d.limb("hero", "M96 62 L94 44 M106 62 L108 44", 4)
    d.marks("mark", circle(94, 43, 4) + circle(108, 43, 4))
    d.shape("hero", "M112 66 L128 56 L120 72Z")
    d.limb("tongue", "M62 88 C56 96 48 98 42 94", 5)
    d.shape("hero", "M58 74 C62 64 76 58 92 58 C102 58 110 60 116 66 L122 74 C118 84 110 88 100 90 "
                    "C88 94 72 94 62 90 C55 87 54 80 58 74Z")
    d.shape("hero2", "M56 78 C56 72 62 68 68 70 C70 80 70 88 66 92 C60 92 55 86 56 78Z", shadow=False, line=False)
    d.marks("mark", ellipse(98, 72, 4, 3) + ellipse(110, 74, 3, 2.4))
    d.marks("dark", circle(88, 70, 3))
    d.marks("dark", circle(60, 77, 1.6))
    # platform rail, an arm holding out lettuce
    d.shape("wood", rrect(-30, 150, 120, 10, 2))
    d.limb("wood2", "M10 160 V214 M60 160 V214", 6)
    d.shape("wood", rrect(-30, 182, 120, 8, 2))
    d.limb("pop", "M-12 176 L22 126", 14)
    d.shape("skin", circle(28, 116, 9))
    d.shape("leaf", "M30 112 C18 104 18 88 30 84 C34 74 48 74 50 84 C60 88 58 102 48 106 C44 114 36 116 30 112Z", spot=True)
    d.stroke("near", "M32 108 L44 88 M38 98 L50 94 M36 100 L28 90", 1.6)
    d.shape("skin", rrect(22, 108, 14, 10, 5), shadow=False)


# ================================================================ ESCAPE ROOM
LOCK = {"brass": "#D9A93F", "brass2": "#B9862A", "steel": "#B7C0CE", "steel2": "#7D8797"}


def escape_padlock(d: Drawing):
    d.disc("glow", 100, 100, 56, line=False)
    for x, y, r in [(40, 54, 6), (160, 150, 5), (156, 44, 4)]:
        d.marks("light", _sparkle(x, y, r))
    d.limb("steel", "M70 96 V66 C70 30 130 30 130 66 V96", 13)
    d.stroke("steel2", "M65 96 V66 C65 26 135 26 135 66", 1.2, line=False)
    d.shape("brass", rrect(52, 88, 96, 80, 14), spot=True)
    d.shape("brass2", rrect(52, 152, 96, 16, 8), shadow=False, line=False)
    d.stroke("brass2", "M60 100 H140", 2, line=False)
    d.marks("dark", circle(100, 120, 9) + "M95 124 L105 124 L103 146 H97Z")

    def key():
        d.stroke("steel", circle(0, 0, 11), 7)
        d.limb("steel", "M11 0 H62", 6)
        d.shape("steel", "M46 3 V12 H52 V3Z M56 3 V15 H62 V3Z")
    group(d, "translate(122 172) rotate(-28)", key)


def escape_door(d: Drawing):
    _night(d)
    d.shape("near", "M-30 -30 H230 V160 H-30Z", shadow=False, line=False)
    d.stroke("deep", "M-30 40 H230 M-30 84 H230 M-30 128 H230 M30 -30 V40 M170 -30 V40 M10 40 V84 M190 40 V84 M30 84 V128 M170 84 V128", 1.2, line=False)
    if d.paper:
        d.raw(f'<path d="M96 160 L124 160 L230 200 L230 230 L60 230Z" fill="{d.c["glow2"]}" opacity=".45"/>')
    d.shape("dark", rrect(56, 30, 88, 134, 4))
    d.shape("hero", rrect(62, 36, 76, 124, 3), spot=True)
    d.stroke("dark", rrect(70, 46, 60, 42, 3) + " " + rrect(70, 100, 60, 50, 3), 2)
    d.shape("glow2", "M128 158 H136 V164 H128Z", shadow=False, line=False)
    d.shape("brass", circle(124, 98, 5))
    d.shape("brass", rrect(118, 104, 12, 18, 4))
    d.marks("glow2", circle(124, 110, 2.6) + "M122.6 111 H125.4 L126 117 H122Z")
    if d.paper:
        d.raw(f'<g opacity=".6" fill="{d.c["glow2"]}"><path d="M126 114 L160 104 L160 112Z"/><path d="M126 114 L160 120 L158 126Z"/></g>')
    d.band("ground", "M-30 164 H230")
    # key hanging on a nail
    d.marks("dark", circle(168, 58, 2))
    d.stroke("dark", "M168 58 L162 70 M168 58 L174 70", 1)

    def key():
        d.stroke("brass", circle(0, 0, 6.5), 4)
        d.limb("brass", "M0 6.5 V36", 3.6)
        d.shape("brass", "M2 26 H8 V30 H2Z M2 32 H9 V36 H2Z", shadow=False)
    group(d, "translate(168 76)", key)
    for x, y in [(30, 172), (60, 186)]:
        d.marks("dark", circle(x, y, 1.6))


def escape_safe(d: Drawing):
    d.disc("glow", 100, 100, 56)
    d.band("far", "M-30 172 H230", line=False)
    d.shape("steel2", rrect(34, 50, 104, 116, 10))
    d.shape("steel", rrect(42, 58, 88, 100, 6), shadow=False)
    d.shape("steel2", rrect(34, 162, 18, 10, 2))
    d.shape("steel2", rrect(120, 162, 18, 10, 2))
    d.shape("dark", rrect(38, 72, 6, 16, 2), shadow=False)
    d.shape("dark", rrect(38, 128, 6, 16, 2), shadow=False)
    d.shape("dark", circle(86, 104, 26))
    d.shape("light", circle(86, 104, 20), shadow=False)
    tick = ""
    for i in range(12):
        a = math.radians(i * 30)
        tick += f"M{86 + 15 * math.cos(a):.1f} {104 + 15 * math.sin(a):.1f} L{86 + 19 * math.cos(a):.1f} {104 + 19 * math.sin(a):.1f} "
    d.stroke("dark", tick, 1.4)
    d.shape("pop", circle(86, 104, 8), spot=True)
    d.marks("dark", "M85 78 H87 L86 82Z")
    d.limb("dark", "M112 92 V116", 4)
    d.limb("dark", "M112 92 H122 M112 116 H122", 3)

    def hourglass():
        d.shape("wood", rrect(-16, -40, 32, 6, 2))
        d.shape("wood", rrect(-16, 34, 32, 6, 2))
        d.limb("wood", "M-13 -34 V34 M13 -34 V34", 2.6, shadow=False)
        d.shape("light", "M-11 -34 H11 C11 -14 2 -6 2 0 C2 6 11 14 11 34 H-11 C-11 14 -2 6 -2 0 C-2 -6 -11 -14 -11 -34Z", shadow=False)
        d.shape("sand", "M-7 -18 H7 C5 -10 2 -6 1 -2 H-1 C-2 -6 -5 -10 -7 -18Z", shadow=False, spot=True)
        d.shape("sand", "M-10 34 C-8 24 -3 20 0 20 C3 20 8 24 10 34Z", shadow=False, spot=True)
        d.stroke("sand", "M0 -2 V20", 1, line=False)
    group(d, "translate(158 128)", hourglass)


# ================================================================ GO-KARTING
KART = {"tyre": "#26262E", "tyre2": "#5A5A66", "kerb": "#E23B3B"}


def kart_side(d: Drawing):
    d.shape("light", cloud(122, 40, 0.9))
    d.band("far", hills(124, 8))
    d.band("ground", "M-30 140 H230")
    d.shape("light", "M-30 172 H230 V182 H-30Z", shadow=False)
    d.marks("kerb", "".join(f"M{x} 172 H{x + 14} V182 H{x}Z " for x in range(-30, 230, 28)))
    d.band("near", "M-30 182 H230", line=False)
    d.stroke("light", "M8 112 H34 M2 124 H26", 2.6, line=False)
    # chequered flag on a pole behind
    d.limb("dark", "M164 140 V54", 2.6)
    d.shape("light", _flag_outline(164, 54, 30, 22, 6, 2.2))
    d.marks("dark", _checker(164, 54, 30, 22, 6, 4, 2.2))
    # kart facing right: engine, seat, driver, pods, nose
    d.shape("dark", rrect(30, 128, 20, 16, 3))
    d.limb("dark", "M34 128 L28 118", 3)
    d.limb("hero2", "M74 140 L122 144", 10)
    d.shape("dark", "M56 150 L58 112 C58 108 66 108 68 112 L70 150Z")
    d.limb("hero2", "M72 138 L80 108", 15)
    d.limb("dark", "M112 126 L130 148", 3)
    d.limb("hero2", "M82 112 L108 124", 6)
    d.shape("dark", ellipse(111, 125, 3, 9), extra='transform="rotate(-30 111 125)"')
    d.shape("pop", circle(84, 92, 13), spot=True)
    d.shape("dark", "M88 84 H97 C98 88 98 94 96 98 H88Z", shadow=False)
    d.stroke("light", "M72 90 H84", 2.4, line=False)
    d.limb("dark", "M36 156 H174", 4)
    d.shape("hero", "M76 158 L82 140 H120 L126 158Z", spot=True)
    d.shape("hero", "M134 150 L140 138 H164 C176 138 182 146 178 154 H134Z", spot=True)
    d.shape("light", rrect(154, 141, 14, 8, 4), shadow=False)
    for x, r in [(50, 16), (146, 13)]:
        d.shape("tyre", circle(x, 156, r))
        d.shape("tyre2", circle(x, 156, r * 0.45), shadow=False)


def kart_flag(d: Drawing):
    d.shape("light", cloud(22, 152, 1.2))
    d.disc("glow", 150, 150, 22)
    d.band("far", hills(170, 6), line=False)
    # tyre stack
    for i, (x, y) in enumerate([(148, 178), (176, 178), (162, 160), (134, 160)]):
        d.shape("tyre", rrect(x - 14, y - 9, 28, 18, 6))
        d.shape("tyre2", ellipse(x, y - 9, 14, 4), shadow=False)
        d.shape("tyre", ellipse(x, y - 9, 7, 2), shadow=False)
        d.stroke("light" if i % 2 else "kerb", f"M{x - 14} {y - 1} H{x + 14}", 2.4, line=False)
    d.limb("dark", "M44 186 L66 24", 4)

    def flag():
        d.shape("light", _flag_outline(0, 0, 112, 72, 14, 7, 1.2, 10))
        d.marks("dark", _checker(0, 0, 112, 72, 7, 5, 7, 1.2, 10))
    group(d, "translate(66 26) rotate(6)", flag)


def kart_helmet(d: Drawing):
    d.disc("glow", 100, 100, 58, line=False)
    d.shape("light", _flag_outline(-30, 150, 260, 40, 13, 0), shadow=False)
    d.marks("dark", _checker(-30, 150, 260, 40, 13, 2))
    d.band("near", "M-30 190 H230", line=False)
    for y in [64, 84, 104]:
        d.stroke("light", f"M14 {y} H{38 - (y - 64) // 4}", 3, line=False)
    helmet = "M44 124 C40 82 66 46 106 46 C142 46 164 72 166 104 L166 128 C166 138 160 144 150 144 L58 144 C50 144 45 136 44 124Z"
    d.shape("hero", helmet, spot=True)
    _clip_to(d, helmet, lambda: d.shape("light", "M30 92 C70 80 110 80 170 100 V116 C110 96 70 96 30 108Z", shadow=False))
    d.shape("dark", "M104 74 C124 70 150 74 164 88 L166 116 C146 116 124 116 108 112 C98 104 98 84 104 74Z")
    d.shape("light", "M112 80 C126 78 142 80 152 86 L150 90 C138 86 124 84 112 86Z", shadow=False, line=False)
    d.shape("hero2", rrect(150, 120, 18, 14, 4), shadow=False)
    d.stroke("dark", "M154 124 H164 M154 129 H164", 1.2)
    d.shape("dark", rrect(48, 138, 112, 8, 4), shadow=False)
    d.marks("dark", circle(100, 102, 3.2))


# ================================================================ OPEN-AIR CINEMA
def cinema_screen(d: Drawing):
    _night(d)
    _stars(d, [(30, 60, 1.3), (170, 40, 1.2), (60, 30, 1.1), (150, 22, 1.1), (180, 92, 1.2), (24, 100, 1)])
    d.disc("glow2", 158, 64, 8)
    if d.paper:
        d.raw(f'<path d="M164 176 L48 52 L48 112 Z" fill="{d.c["light"]}" opacity=".18"/>'
              f'<path d="M164 176 L152 52 L152 112 Z" fill="{d.c["light"]}" opacity=".12"/>')
    d.band("near", hills(140, 10), line=False)
    for x in [24, 182]:
        d.shape("dark", f"M{x - 14} 146 C{x - 18} 120 {x - 8} 96 {x} 90 C{x + 8} 96 {x + 18} 120 {x + 14} 146Z")
    d.limb("dark", "M60 112 V150 M140 112 V150", 3.6)
    d.shape("light", rrect(42, 46, 116, 70, 3))
    d.shape("far", rrect(48, 52, 104, 58, 1), shadow=False)
    d.shape("glow2", circle(126, 70, 9), shadow=False, spot=True)
    d.shape("mid", "M48 110 V96 L70 80 L88 94 L104 82 L130 100 L152 92 V110Z", shadow=False)
    d.band("mid", "M-30 150 Q100 144 230 150", line=False)
    heads = [(28, 168, 8), (62, 164, 8.5), (98, 168, 8), (132, 164, 8.5)]
    body = "M-30 230 V196"
    for x, y, r in heads:
        body += (f" L{x - r * 1.8:.1f} {y + r * 2.6:.1f} Q{x - r * 1.8:.1f} {y + r * 1.3:.1f} {x - r * 0.7:.1f} {y + r * 1.1:.1f}"
                 f" A{r} {r} 0 1 1 {x + r * 0.7:.1f} {y + r * 1.1:.1f} Q{x + r * 1.8:.1f} {y + r * 1.3:.1f} {x + r * 1.8:.1f} {y + r * 2.6:.1f}")
    body += " L150 196 V230Z"
    _clip(d, lambda: d.shape("dark", body))
    d.shape("hero", rrect(156, 166, 20, 14, 3), spot=True)
    d.shape("light", circle(156, 172, 4), shadow=False)
    d.limb("dark", "M160 180 L156 196 M172 180 L176 196", 2.4)


def cinema_projector(d: Drawing):
    _night(d)
    _stars(d, [(30, 70, 1.3), (60, 30, 1.2), (164, 34, 1.2), (180, 140, 1.1), (36, 150, 1.2)])
    if d.paper:
        d.raw(f'<path d="M140 116 L240 70 L240 176Z" fill="{d.c["light"]}" opacity=".24"/>'
              f'<path d="M140 116 L240 98 L240 140Z" fill="{d.c["glow2"]}" opacity=".3"/>')
    else:
        d.raw("", f'<path d="M150 108 L196 88 M150 124 L196 146" fill="none" stroke="{d.c["ink"]}" stroke-width="2" stroke-dasharray="5 5" stroke-linecap="round"/>')
    for cx, cy, r in [(64, 66, 26), (118, 72, 21)]:
        d.shape("hero", circle(cx, cy, r), spot=True)
        for k in range(5):
            a = math.radians(k * 72 - 90)
            d.shape("deep", circle(round(cx + r * 0.55 * math.cos(a), 1), round(cy + r * 0.55 * math.sin(a), 1), r * 0.2), shadow=False)
        d.shape("light", circle(cx, cy, r * 0.16), shadow=False)
    d.stroke("light", "M64 92 C80 112 104 108 118 93", 1.6)
    d.limb("dark", "M64 66 L86 104 M118 72 L104 104", 4)
    d.shape("dark", rrect(48, 100, 92, 42, 6))
    d.shape("mark", rrect(54, 106, 40, 30, 3), shadow=False, line=False)
    d.stroke("light", "M60 114 H88 M60 122 H88 M60 130 H88", 1.4, line=False)
    d.shape("light", rrect(140, 106, 16, 20, 3))
    d.shape("dark", rrect(152, 102, 8, 28, 3))
    d.shape("glow2", rrect(158, 108, 3, 16, 1.5), shadow=False)
    d.limb("dark", "M66 142 L56 176 M122 142 L132 176 M94 142 V176", 3.4)
    d.band("near", "M-30 176 H230", line=False)


def cinema_popcorn(d: Drawing):
    _night(d)
    _stars(d, [(30, 70, 1.3), (176, 100, 1.2), (60, 30, 1.2), (150, 24, 1.1), (24, 120, 1.1)])
    d.disc("glow2", 156, 52, 18)
    d.marks("glow", circle(150, 46, 3.4) + circle(162, 58, 4.4))
    mid = "M-30 166 C20 150 40 118 76 114 C116 110 150 130 230 100"
    d.limb("dark", mid, 24)
    for dy in (-7.5, 7.5):
        path = f'<path d="{mid}" transform="translate(0 {dy})" fill="none" stroke="%s" stroke-width="3.6" stroke-dasharray="4 5"/>'
        d.raw(path % d.c.get("light", ""), path % d.c.get("ink", ""))
    d.band("ground", "M-30 178 Q100 172 230 178")
    for x, y, r in [(70, 76, 14), (90, 66, 16), (112, 66, 15), (132, 78, 13), (80, 90, 13), (122, 92, 13), (100, 84, 14), (60, 92, 10), (142, 94, 10)]:
        d.shape("light", circle(x, y, r))
        d.stroke("glow2", f"M{x - r * 0.4:.1f} {y + r * 0.2:.1f} Q{x:.1f} {y - r * 0.4:.1f} {x + r * 0.4:.1f} {y + r * 0.2:.1f}", 2, line=False)
    box = "M60 98 H140 L130 182 H70Z"
    d.shape("light", box)
    _clip_to(d, box, lambda: d.shape("pop", "M66 90 H80 L80 190 H72Z M93 90 H107 V190 H93Z M120 90 H134 L128 190 H120Z", shadow=False, spot=True))
    d.shape("light", rrect(57, 96, 86, 8, 3))
    for x, y in [(156, 166), (44, 162)]:
        d.shape("light", circle(x, y, 6))


ESCAPE = {**LOCK, "wood": "#8A5A34", "sand": "#E9B44C"}
NIGHT_CHECKS = [("glow2", "deep")]

CONCEPTS = [
    Concept("club-discoball", "nightclub", "Disco ball", club_discoball, overrides=SILVER,
            checks=[("silver", "deep"), ("hero2", "deep")], fixes={"hero2": ["pop", "glow2", "light"]}),
    Concept("club-decks", "nightclub", "DJ decks", club_decks,
            checks=[("hero", "deep"), ("dark", "hero"), ("pop", "dark")], fixes={"hero": ["pop", "hero2", "far", "mid"], "pop": ["hero2", "glow2"]}),
    Concept("club-floor", "nightclub", "Light-up dance floor", club_floor,
            checks=[("dark", "pop"), ("dark", "hero2"), ("dark", "far")], fixes={"far": ["light", "glow2"]}),
    Concept("fullmoon-beach", "full-moon-party", "Full moon over the beach", fullmoon_beach, SEA, NEON,
            checks=[("glow2", "deep"), ("mid", "deep"), ("dark", "ground"), ("dark", "mid")], fixes=NIGHT_FIX),
    Concept("fullmoon-bucket", "full-moon-party", "Party bucket", fullmoon_bucket, SEA, NEON,
            checks=[("glow2", "deep"), ("hero", "deep"), ("hero", "ground"), ("hero", "glow2")], fixes={"hero": ["pop", "hero2", "light"]}),
    Concept("fullmoon-paint", "full-moon-party", "Glow paint", fullmoon_paint, ALL, {**NEON, **SILVER},
            checks=[("glow2", "deep"), ("light", "ground"), ("light", "deep"), ("n2", "light")], fixes={"ground": ["near", "mid", "far"]}),
    Concept("karaoke-mic", "karaoke", "Stage microphone", karaoke_mic,
            checks=[("hero", "glow"), ("pop", "sky"), ("dark", "glow"), ("light", "glow")], fixes={"glow": ["far", "glow2", "sky2"], "hero": ["deep", "near", "mark"]}),
    Concept("karaoke-screen", "karaoke", "Lyrics on screen", karaoke_screen,
            checks=[("dark", "sky"), ("pop", "deep"), ("light", "deep"), ("hero", "sky"), ("hero", "glow")], fixes={"hero": ["pop", "near", "deep"], "deep": ["mark", "dark"]}),
    Concept("karaoke-duet", "karaoke", "Duet mics", karaoke_duet,
            checks=[("hero", "glow"), ("pop", "glow"), ("light", "glow2"), ("hero", "glow2")], fixes={"glow2": ["far", "glow", "mid"], "glow": ["near", "far", "mid"]}),
    Concept("casino-dice", "casino", "Dice & chips", casino_dice, overrides=CASINO,
            checks=[("red", "glow"), ("red", "felt"), ("blk", "felt")], fixes={"glow": ["far", "light", "glow2", "sky2"]}),
    Concept("casino-roulette", "casino", "Roulette wheel", casino_roulette, overrides=CASINO,
            checks=[("wood", "felt")]),
    Concept("casino-slot", "casino", "Slot machine", casino_slot,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero2", "hero"), ("pop", "light")], fixes={"glow": ["far", "glow2"], "hero": ["deep", "near", "pop"]}),
    Concept("rooftopparty-lights", "rooftop-party", "Festoon-lit terrace", rooftopparty_lights,
            checks=[("mid", "glow"), ("far", "sky"), ("ground", "mid"), ("dark", "ground")], fixes={"far": ["sky2", "glow2"], "mid": ["near", "deep"]}),
    Concept("rooftopparty-watertower", "rooftop-party", "Water-tower party", rooftopparty_watertower, overrides={"wood": "#A0653A", "wood2": "#6B4226"},
            checks=[("wood", "far"), ("wood", "sky"), ("far", "sky")], fixes={"far": ["mid", "near"]}),
    Concept("rooftopparty-bubbly", "rooftop-party", "Popping bubbly", rooftopparty_bubbly, overrides={"bottle": "#2F7A4A", "gold": "#E8B84A", "cork": "#C9955B"},
            checks=[("bottle", "deep"), ("bottle", "near"), ("near", "deep"), ("glow2", "deep")], fixes={"near": ["mid", "far", "#343F63"], "bottle": ["#3E9A5E", "#245C38"]}),
    Concept("barhop-round", "bar-hopping", "A round of drinks", barhop_round, overrides=BEER,
            checks=[("light", "glow"), ("beer", "glow"), ("pop", "glow"), ("light", "wood")], fixes={"glow": ["far", "mid", "near", "sky2"]}),
    Concept("barhop-street", "bar-hopping", "Bar street at night", barhop_street,
            checks=[("hero", "deep"), ("far", "deep"), ("near", "deep"), ("glow2", "deep")], fixes={"near": ["mid", "hero2", "pop"], "far": ["mid", "light"]}),
    Concept("barhop-route", "bar-hopping", "Bar crawl route", barhop_route,
            checks=[("pop", "ground"), ("hero", "ground"), ("pop", "far"), ("hero", "far"), ("dark", "ground")], fixes={"hero": ["deep", "near", "hero2"]}),
    Concept("zoo-booth", "zoo", "Zoo ticket booth", zoo_booth, overrides={"giraffe": "#F6C453"},
            checks=[("hero", "sky"), ("hero", "far"), ("pop", "hero"), ("dark", "sky"), ("dark", "far")], fixes={"hero": ["near", "deep", "pop"], "far": ["mid", "sky2"]}),
    Concept("zoo-seal", "zoo", "Seal show", zoo_seal, SEA, SEAL,
            checks=[("seal", "sky"), ("seal", "glow"), ("hero", "far"), ("pop", "light")], fixes={"glow": ["far", "light"], "hero": ["pop", "deep"]}),
    Concept("zoo-giraffe", "zoo", "Giraffe feeding", zoo_giraffe, overrides=GIRAFFE_GOLD,
            checks=[("pop", "far"), ("pop", "sky"), ("hero", "sky"), ("hero", "far"), ("hero", "mid"), ("leaf", "near"), ("leaf", "sky")], fixes={"near": ["deep", "mid"], "far": ["mid", "near"]}),
    Concept("escape-padlock", "escape-room", "Padlock & key", escape_padlock, overrides=LOCK,
            checks=[("brass", "glow"), ("steel", "glow")], fixes={"glow": ["near", "mid", "deep", "far"]}),
    Concept("escape-door", "escape-room", "Locked door", escape_door, overrides=ESCAPE,
            checks=[("hero", "near"), ("dark", "near"), ("brass", "hero")], fixes={"hero": ["pop", "hero2", "light"]}),
    Concept("escape-safe", "escape-room", "Safe & hourglass", escape_safe, overrides=ESCAPE,
            checks=[("steel2", "glow"), ("steel", "steel2"), ("wood", "glow")], fixes={"glow": ["far", "mid", "near"]}),
    Concept("kart-side", "go-karting", "Go-kart", kart_side, overrides=KART,
            checks=[("hero", "ground"), ("hero", "far"), ("pop", "far"), ("tyre", "ground")], fixes={"hero": ["pop", "deep", "near"], "pop": ["hero2", "light"]}),
    Concept("kart-flag", "go-karting", "Chequered flag", kart_flag, overrides=KART,
            checks=[("light", "sky"), ("dark", "sky")], fixes={"sky": ["sky2", "far"]}),
    Concept("kart-helmet", "go-karting", "Racing helmet", kart_helmet,
            checks=[("hero", "glow"), ("hero", "sky"), ("dark", "hero")], fixes={"glow": ["far", "glow2", "sky2"], "hero": ["pop", "deep", "near"]}),
    Concept("cinema-screen", "open-air-cinema", "Screen under the stars", cinema_screen,
            checks=[("light", "deep"), ("far", "light"), ("dark", "near"), ("dark", "mid")], fixes=NIGHT_FIX),
    Concept("cinema-projector", "open-air-cinema", "Film projector", cinema_projector,
            checks=[("hero", "deep"), ("dark", "deep"), ("deep", "hero")], fixes={"dark": ["#343F63", "mark", "near", "mid"], "hero": ["pop", "hero2", "glow2"]}),
    Concept("cinema-popcorn", "open-air-cinema", "Popcorn & moon", cinema_popcorn, overrides={"pop": "#E63946"},
            checks=[("light", "deep"), ("pop", "light"), ("dark", "deep"), ("glow2", "deep")], fixes={"dark": ["#343F63", "near", "mid"]}),
]
