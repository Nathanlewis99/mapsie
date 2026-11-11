"""Moments, nightlife & wellness: three ideas each for beach parties, festivals, theme and water parks,
aquariums, fireworks, yoga, spa, massage, honeymoons, proposals, weddings, family holidays, solo travel
and gap years."""
import math

from _common import Concept, Drawing, cloud, fish, circle, ellipse, waves, hills, rrect, group, bubbles

ALL = ["golden", "coastal", "meadow", "blush", "dusk"]
UNDERWATER = ["coastal", "dusk", "meadow"]
FLAME = {"pop": "#FF7B3A", "glow2": "#FFD25E"}
POOL = {"mid": "#5FBCC6", "near": "#2F8FA3"}


# ================================================================ private helpers
def _palm(d: Drawing, x0, y0, x1, y1, s=1.0, role="dark", w=5):
    """A palm tree: trunk from the ground (x0, y0) bending to the crown (x1, y1)."""
    d.limb(role, f"M{x0} {y0} Q{x0 + (x1 - x0) * 0.1:.1f} {(y0 + y1) / 2:.1f} {x1} {y1}", w * s)

    def crown():
        for f in ["M0 0 C10 -13 30 -13 40 4 C30 -4 14 -4 0 0Z", "M0 0 C6 -16 22 -24 34 -18 C22 -16 10 -10 0 0Z",
                  "M0 0 C-10 -13 -30 -13 -40 4 C-30 -4 -14 -4 0 0Z", "M0 0 C-6 -16 -22 -24 -34 -18 C-22 -16 -10 -10 0 0Z",
                  "M0 0 C-3 -14 1 -24 7 -28 C6 -18 4 -8 0 0Z"]:
            d.shape(role, f, shadow=False)
    group(d, f"translate({x1} {y1}) scale({s})", crown)


def _note(x, y, s=1.0):
    """A quaver: head, stem and flag, as one path."""
    return (ellipse(x, y, 4.6 * s, 3.4 * s) + f" M{x + 3 * s} {y - 1 * s} V{y - 17 * s} "
            f"C{x + 6 * s} {y - 12 * s} {x + 12 * s} {y - 12 * s} {x + 11 * s} {y - 5 * s} "
            f"C{x + 10 * s} {y - 9 * s} {x + 7 * s} {y - 10 * s} {x + 5 * s} {y - 10 * s} V{y - 1 * s}Z")


def _star(x, y, r, k=0.42, n=5, rot=-90):
    pts = []
    for i in range(2 * n):
        a = math.radians(rot + i * 180 / n)
        rr = r if i % 2 == 0 else r * k
        pts.append(f"{x + rr * math.cos(a):.1f} {y + rr * math.sin(a):.1f}")
    return "M" + " L".join(pts) + "Z"


def _crowd(heads, r=7.5, base=230):
    """One silhouette of heads and shoulders, left to right (a single outline, so it reads in line style)."""
    p = f"M-30 {base} V{heads[0][1] + 22}"
    for x, y in heads:
        p += (f" L{x - 13} {y + 22} Q{x - 13} {y + 11} {x - 5} {y + 9} A{r} {r} 0 1 1 {x + 5} {y + 9}"
              f" Q{x + 13} {y + 11} {x + 13} {y + 22}")
    return p + f" L230 {heads[-1][1] + 22} V{base}Z"


def _clip(d: Drawing, fn):
    """Clip to the sticker circle in both styles (line style doesn't clip shapes by itself)."""
    d.raw('<g clip-path="url(#clip)">', '<g clip-path="url(#clip)">')
    fn()
    d.raw("</g>", "</g>")


def _burst(d: Drawing, x, y, r, role, n=14, inner=0.32, w=2.4, spot=False, dots=True, rot=0.0):
    """A firework burst: radial streaks with a dot at each tip."""
    col = d.c[role] if d.paper else d.c["spot" if spot else "ink"]
    lines, tips = "", ""
    for i in range(n):
        a = math.radians(rot + i * 360 / n)
        c, s_ = math.cos(a), math.sin(a)
        lines += f"M{x + r * inner * c:.1f} {y + r * inner * s_:.1f} L{x + r * c:.1f} {y + r * s_:.1f} "
        tips += circle(round(x + (r + w * 1.3) * c, 1), round(y + (r + w * 1.3) * s_, 1), round(w * 0.8, 2)) + " "
    svg = f'<path d="{lines}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'
    if dots:
        svg += f'<path d="{tips}" fill="{col}"/>'
    d.raw(svg, svg)


def _annulus(cx, cy, r1, r2, a1, a2):
    """A segment of a ring between angles a1 and a2 (degrees)."""
    p = lambda r, a: f"{cx + r * math.cos(math.radians(a)):.1f} {cy + r * math.sin(math.radians(a)):.1f}"
    big = 1 if (a2 - a1) % 360 > 180 else 0
    return f"M{p(r2, a1)} A{r2} {r2} 0 {big} 1 {p(r2, a2)} L{p(r1, a2)} A{r1} {r1} 0 {big} 0 {p(r1, a1)}Z"


def _ring(cx, cy, r1, r2):
    """A full ring (use with fill-rule evenodd)."""
    return circle(cx, cy, r2) + " " + f"M{cx - r1} {cy} a{r1} {r1} 0 1 1 {2 * r1} 0 a{r1} {r1} 0 1 1 {-2 * r1} 0Z"


def _night(d: Drawing):
    """A night sky that still follows the palette: the darkest landscape colour, edge to edge."""
    d.band("deep", "M-30 -30 H230", shadow=False, line=False)


def _leaf(d: Drawing, x, y, length, width, angle, role="near", rib="deep", spot=False, shadow=True, line=True):
    """A pointed tropical leaf from (x, y), pointing along `angle` degrees, with a midrib."""
    L, w = length, width

    def draw():
        d.shape(role, f"M0 0 C{L * .3:.1f} {-w} {L * .7:.1f} {-w} {L} 0 C{L * .7:.1f} {w} {L * .3:.1f} {w} 0 0Z", spot=spot, shadow=shadow, line=line)
        d.stroke(rib, f"M2 0 L{L * .9:.1f} 0", 1.4, line=False)
    group(d, f"translate({x} {y}) rotate({angle})", draw)


def _frangipani(d: Drawing, x, y, s=1.0, petal="light", centre="glow2", rot=0):
    def draw():
        for i in range(5):
            d.shape(petal, "M0 0 C-6 -6 -6 -18 2 -21 C10 -22 12 -12 0 0Z", shadow=i == 0,
                    extra=f'transform="rotate({i * 72})"')
        d.shape(centre, circle(0, 0, 4.5), shadow=False, spot=True)
    group(d, f"translate({x} {y}) rotate({rot}) scale({s})", draw)


def _heart(x, y, s=1.0):
    """A heart centred on (x, y), about 20*s wide."""
    return (f"M{x} {y + 8 * s} C{x - 4 * s} {y + 4 * s} {x - 10 * s} {y} {x - 10 * s} {y - 4 * s} "
            f"C{x - 10 * s} {y - 9 * s} {x - 5 * s} {y - 11 * s} {x} {y - 6 * s} "
            f"C{x + 5 * s} {y - 11 * s} {x + 10 * s} {y - 9 * s} {x + 10 * s} {y - 4 * s} "
            f"C{x + 10 * s} {y} {x + 4 * s} {y + 4 * s} {x} {y + 8 * s}Z")


def _flags(d: Drawing, x0, y0, x1, y1, sag, n, roles, size=4.0, spot_every=2):
    """Bunting on a sagging string from (x0, y0) to (x1, y1)."""
    cx, cy = (x0 + x1) / 2, max(y0, y1) + sag
    d.stroke("dark", f"M{x0} {y0} Q{cx} {cy} {x1} {y1}", 1.3)
    for i in range(1, n + 1):
        t = i / (n + 1)
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1
        d.shape(roles[i % len(roles)], f"M{x - size:.1f} {y:.1f} L{x + size:.1f} {y:.1f} L{x:.1f} {y + size * 2:.1f}Z",
                shadow=False, spot=i % spot_every == 0)


def _bulbs(d: Drawing, x0, y0, x1, y1, sag, n, roles, r=2.6):
    """Festoon lights on a sagging string."""
    cx, cy = (x0 + x1) / 2, max(y0, y1) + sag
    d.stroke("dark", f"M{x0} {y0} Q{cx} {cy} {x1} {y1}", 1.3)
    for i in range(1, n + 1):
        t = i / (n + 1)
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1
        d.shape(roles[i % len(roles)], circle(round(x, 1), round(y + r, 1), r), shadow=False, spot=True)


# ================================================================ BEACH PARTY
def beachparty_bonfire(d: Drawing):
    d.disc("glow", 140, 52, 14)
    d.band("far", waves(112, 3, 30))
    d.band("mid", waves(128, 3, 34), line=False)
    d.band("ground", "M-30 146 Q60 136 120 142 T230 140")
    _palm(d, 26, 150, 42, 74, 0.85)
    _palm(d, 176, 148, 160, 66, 0.85)
    _bulbs(d, 46, 76, 156, 70, 22, 7, ["pop", "hero2", "light"])
    d.limb("dark", "M74 166 L126 150", 8)
    d.limb("dark", "M74 150 L126 166", 8)
    d.shape("pop", "M100 92 C112 104 124 118 122 136 C121 148 112 156 100 156 C88 156 79 148 78 136 "
                   "C77 124 84 116 90 108 C91 116 94 120 97 122 C95 112 96 102 100 92Z", spot=True)
    d.shape("glow2", "M101 116 C108 124 113 132 112 142 C111 149 106 152 100 152 C94 152 89 149 89 142 "
                     "C89 134 94 128 101 116Z", shadow=False)
    for x, y, r in [(80, 96, 1.8), (124, 100, 1.6), (114, 82, 1.4), (88, 80, 1.3)]:
        d.marks("glow2", circle(x, y, r))
    d.band("deep", "M-30 182 Q100 172 230 182", line=False)


def beachparty_boombox(d: Drawing):
    d.disc("glow", 50, 58, 17)
    d.band("far", waves(116, 3, 30))
    d.band("ground", "M-30 140 Q100 130 230 140")
    for x, y, s in [(140, 54, 1.0), (160, 74, 0.85), (122, 40, 0.75)]:
        d.marks("dark", _note(x, y, s))
    d.limb("dark", "M150 92 L170 62", 2.4)
    d.limb("dark", "M62 92 V76 H138 V92", 6)
    for x in [74, 88, 102]:
        d.shape("pop", rrect(x, 84, 10, 8, 2), shadow=False)
    d.shape("hero", rrect(36, 90, 128, 64, 12))
    d.shape("hero2", rrect(36, 90, 128, 10, 5), shadow=False, spot=True)
    for x in [66, 134]:
        d.shape("dark", circle(x, 126, 21))
        d.shape("light", circle(x, 126, 14), shadow=False)
        d.shape("dark", circle(x, 126, 7), shadow=False)
    d.shape("light", rrect(88, 108, 24, 17, 3), shadow=False)
    d.marks("dark", circle(95, 116.5, 3.2) + circle(105, 116.5, 3.2))
    d.shape("dark", rrect(90, 132, 20, 5, 2), shadow=False)
    d.shape("dark", rrect(46, 152, 14, 6, 2))
    d.shape("dark", rrect(140, 152, 14, 6, 2))


def beachparty_cocktail(d: Drawing):
    d.disc("glow", 100, 112, 48)
    d.band("far", waves(132, 3, 30))
    d.band("ground", "M-30 160 Q100 150 230 160")
    d.limb("hero", "M92 72 L76 26", 4.5, spot=True)
    glass = ("M72 50 H128 C130 76 122 96 113 108 C109 114 109 120 111 126 C114 132 117 138 117 144 H83 "
             "C83 138 86 132 89 126 C91 120 91 114 87 108 C78 96 70 76 72 50Z")
    d.shape("light", glass)
    d.shape("pop", "M77 58 H123 C123 80 116 96 109 106 C105 112 105 120 107 126 C110 131 112 135 112 139 H88 "
                   "C88 135 90 131 93 126 C95 120 95 112 91 106 C84 96 77 80 77 58Z", shadow=False)
    d.shape("hero2", "M77 58 H123 C123 68 121 76 118 84 H82 C79 76 77 68 77 58Z", shadow=False, spot=True)
    d.shape("light", rrect(95, 144, 10, 18, 2))
    d.shape("light", ellipse(100, 164, 22, 5))
    d.shape("hero2", circle(70, 54, 13))
    d.shape("light", circle(70, 54, 9.5), shadow=False)
    d.stroke("hero2", "M70 45.5 V62.5 M61.5 54 H78.5 M64 48 L76 60 M76 48 L64 60", 2)

    def umbrella():
        d.stroke("dark", "M0 -8 V36", 2)
        d.shape("pop", "M-26 0 Q0 -26 26 0 Q13 -5 0 0 Q-13 -5 -26 0Z", spot=True)
        d.stroke("light", "M0 -12 L-14 -1 M0 -12 L14 -1", 1.4, line=False)
    group(d, "translate(128 40) rotate(22)", umbrella)


# ================================================================ MUSIC FESTIVAL
def festival_stage(d: Drawing):
    d.raw('<g opacity=".28" fill="#fff"><path d="M62 82 L2 0 L34 0Z"/><path d="M100 76 L84 0 L116 0Z"/>'
          '<path d="M138 82 L166 0 L198 0Z"/></g>', "")
    d.band("far", hills(136, 8), line=False)
    for x, h in [(56, 32), (100, 40), (144, 32)]:
        d.stroke("dark", f"M{x} 70 V{70 - h}", 1.6)
        d.shape("pop", f"M{x} {70 - h} L{x + 16} {74 - h} L{x} {78 - h}Z", shadow=False, spot=True)
    d.shape("hero", "M30 152 V100 C30 72 62 56 100 56 C138 56 170 72 170 100 V152Z")
    d.shape("dark", "M46 150 V104 C46 84 70 72 100 72 C130 72 154 84 154 104 V150Z", shadow=False)
    for x, y in [(64, 86), (82, 79), (100, 77), (118, 79), (136, 86)]:
        d.shape("glow2", circle(x, y, 3.2), shadow=False)
    d.shape("mark", rrect(52, 112, 14, 30, 2), shadow=False, line=False)
    d.shape("mark", rrect(134, 112, 14, 30, 2), shadow=False, line=False)
    d.marks("light", circle(59, 120, 3.4) + circle(59, 133, 4.2) + circle(141, 120, 3.4) + circle(141, 133, 4.2))
    d.shape("hero2", rrect(24, 142, 152, 10, 3), spot=True)
    for a in ["M66 172 L56 142", "M118 170 L128 144", "M166 172 L176 148", "M40 174 L32 150"]:
        d.limb("dark", a, 5, shadow=False)
    _clip(d, lambda: d.shape("dark", _crowd([(16, 164), (40, 168), (66, 160), (92, 166), (118, 158), (144, 165), (170, 160), (194, 166)])))


def festival_tents(d: Drawing):
    d.disc("glow", 152, 52, 15)
    d.band("far", hills(118, 10, -10))
    flag = "M0 0 C8 -3 16 3 26 0 L19 8 L26 16 C16 19 8 13 0 16Z"
    for x, y, h, role in [(38, 136, 76, "pop"), (100, 126, 84, "hero2"), (164, 132, 72, "hero")]:
        d.stroke("dark", f"M{x} {y} V{y - h}", 2)
        group(d, f"translate({x} {y - h})", lambda role=role: d.shape(role, flag, spot=role == "pop"))
    d.band("mid", hills(142, 10, 20))
    _flags(d, -10, 118, 210, 112, 20, 13, ["pop", "hero2", "light", "hero"], 3.6)

    def tent(x, y, s, body, door):
        def draw():
            d.shape(body, "M-24 0 C-22 -10 -12 -24 0 -36 C12 -24 22 -10 24 0Z")
            d.shape(door, "M-7 0 L0 -20 L7 0Z", shadow=False)
            d.stroke("dark", "M0 -36 V-42", 1.6)
        group(d, f"translate({x} {y}) scale({s})", draw)
    tent(56, 160, 1.0, "light", "dark")
    tent(150, 162, 0.9, "hero2", "dark")
    tent(102, 170, 1.3, "hero", "dark")
    d.band("near", hills(178, 6, -20))


def festival_guitar(d: Drawing):
    d.disc("glow", 100, 104, 58)
    _flags(d, -10, 52, 210, 52, 26, 11, ["pop", "hero2", "light", "hero"], 4.2)
    for x, y, r in [(36, 116, 6), (164, 126, 5), (150, 40, 4.5)]:
        d.shape("light", _star(x, y, r), shadow=False)

    def guitar():
        d.shape("dark", rrect(91, 8, 18, 22, 4))
        d.marks("light", circle(95, 14, 1.5) + circle(95, 22, 1.5) + circle(105, 14, 1.5) + circle(105, 22, 1.5))
        d.shape("hero2", rrect(95, 26, 10, 60, 2))
        d.shape("hero", "M100 74 C114 74 122 84 122 96 C122 104 118 108 118 112 C118 116 132 122 132 140 "
                        "C132 158 117 170 100 170 C83 170 68 158 68 140 C68 122 82 116 82 112 C82 108 78 104 78 96 "
                        "C78 84 86 74 100 74Z", spot=True)
        d.shape("hero2", rrect(95, 70, 10, 20, 2), shadow=False)
        d.shape("dark", circle(100, 112, 9.5), shadow=False)
        d.shape("dark", rrect(88, 146, 24, 6, 2), shadow=False)
        d.stroke("light", "M97.5 30 V148 M100 30 V148 M102.5 30 V148", 0.8, line=False)
    group(d, "translate(100 100) rotate(28) scale(.92) translate(-100 -90)", guitar)


# ================================================================ THEME PARK
def themepark_coaster(d: Drawing):
    d.shape("light", cloud(128, 44, 1.0))
    d.shape("light", cloud(20, 64, 0.8))
    d.band("far", hills(150, 10))
    for x, y in [(30, 150), (56, 140), (88, 132), (88, 96), (150, 128), (176, 104), (198, 82)]:
        d.stroke("dark", f"M{x} {y} V184", 2.2)
    d.stroke("dark", "M30 160 L56 150 M56 160 L88 142 M150 140 L176 120 M176 140 L198 100", 1.6)
    track = ("M-30 152 C10 152 50 142 84 132 C118 122 128 92 120 72 C112 52 80 50 66 68 C52 86 60 116 92 128 "
             "C122 138 150 136 168 112 C180 96 192 76 232 64")
    d.limb("hero", track, 8)
    d.stroke("light", track, 1.6, line=False)

    def car(x, y, a):
        def draw():
            d.limb("dark", "M-8 -9 L-11 -20 M7 -9 L10 -20", 2.6, shadow=False)
            d.marks("dark", circle(-5, -12, 4) + circle(6, -12, 4))
            d.shape("pop", rrect(-15, -10, 30, 12, 4), spot=True)
            d.shape("hero2", rrect(-15, -10, 30, 4, 2), shadow=False)
        group(d, f"translate({x} {y}) rotate({a})", draw)
    car(150, 128, -34)
    car(174, 102, -46)
    d.band("near", hills(176, 6, 20))


def themepark_ferris(d: Drawing):
    d.disc("glow", 100, 90, 30)
    d.band("far", hills(150, 10, -20))
    d.limb("dark", "M66 172 L100 92 L134 172", 5)
    spokes = ""
    for i in range(8):
        a = math.radians(i * 45 + 22.5)
        spokes += f"M100 92 L{100 + 54 * math.cos(a):.1f} {92 + 54 * math.sin(a):.1f} "
    d.stroke("hero", spokes, 1.6)
    d.stroke("hero", circle(100, 92, 54), 4.5)
    d.stroke("hero", circle(100, 92, 44), 1.8)
    roles = ["pop", "hero2", "light", "pop", "hero2", "light", "pop", "hero2"]
    for i in range(8):
        a = math.radians(i * 45 + 22.5)
        x, y = 100 + 54 * math.cos(a), 92 + 54 * math.sin(a)
        d.stroke("dark", f"M{x:.1f} {y:.1f} V{y + 4:.1f}", 1.5)
        d.shape(roles[i], rrect(round(x - 7, 1), round(y + 3, 1), 14, 11, 3.5), spot=i % 3 == 0)
    d.shape("dark", circle(100, 92, 6))
    d.band("near", hills(170, 6))


HORSE = ("M4 14 C6 6 12 2 18 4 L22 6 L26 4 L24 10 C26 14 26 18 30 18 L48 18 C54 18 56 22 58 26 L62 34 L58 35 L54 28 "
         "L52 36 L54 46 L50 46 L47 36 L33 36 L30 46 L26 46 L27 34 L22 40 L18 38 L22 30 C18 26 18 22 16 18 "
         "C12 18 8 20 6 20 C3 20 2 17 4 14Z")


def themepark_carousel(d: Drawing):
    d.band("far", hills(150, 10), line=False)
    d.shape("dark", rrect(30, 150, 140, 14, 4))
    d.shape("hero2", rrect(26, 144, 148, 9, 3), spot=True)
    for x in [44, 156]:
        d.limb("hero2", f"M{x} 80 V144", 3.2, shadow=False)
    d.shape("hero", rrect(88, 80, 24, 64, 3))
    d.shape("light", "M88 92 L112 84 V92 L88 100Z M88 112 L112 104 V112 L88 120Z M88 132 L112 124 V132 L88 140Z", shadow=False)
    for x, y, flip in [(60, 120, False), (140, 106, True)]:
        d.limb("hero2", f"M{x} 80 V144", 3.2, shadow=False)
        sx = -0.85 if flip else 0.85

        def horse():
            d.shape("light", HORSE)
            d.shape("dark", "M18 4 C24 2 30 10 32 18 L28 18 C26 12 22 8 18 4Z", shadow=False)
            d.shape("pop", "M32 16 H46 C49 16 50 18 50 20 V24 H32Z", shadow=False, spot=True)
            d.marks("dark", circle(12, 9, 1.3))
        group(d, f"translate({x} {y}) scale({sx} .85) translate(-32 -22)", horse)
    roof = "M100 30 L166 74 H34Z"
    d.shape("hero", roof)
    for a, b in [(34, 56), (78, 100), (122, 144)]:
        d.shape("light", f"M100 30 L{a} 74 H{b}Z", shadow=False)
    scal = "M30 72 H170 V80"
    for i in range(7):
        x = 170 - i * 20
        scal += f" Q{x - 10} 92 {x - 20} 80"
    d.shape("pop", scal + "Z", spot=True)
    d.stroke("dark", "M100 30 V16", 1.8)
    d.shape("pop", "M100 16 L114 20 L100 24Z", shadow=False)
    d.band("near", hills(180, 5, 10))


# ================================================================ WATER PARK
def waterpark_tower(d: Drawing):
    d.disc("glow", 156, 50, 15)
    d.shape("light", cloud(104, 34, 0.9))
    d.band("far", hills(128, 10, 30))
    d.limb("dark", "M42 150 V64 M70 150 V64", 4)
    d.stroke("dark", "M42 80 L70 96 M70 96 L42 112 M42 112 L70 128 M70 128 L42 144", 2)
    d.shape("pop", "M32 60 L56 38 L80 60Z", spot=True)
    d.shape("hero2", rrect(34, 58, 44, 8, 2))
    d.limb("hero2", "M74 96 C96 100 104 116 96 130 C90 140 100 152 124 156", 11)
    d.limb("hero", "M76 64 C118 60 152 70 148 92 C144 112 88 104 92 126 C96 144 132 148 156 150", 13, spot=True)
    d.stroke("light", "M76 64 C118 60 152 70 148 92 C144 112 88 104 92 126 C96 144 132 148 156 150", 2.4, line=False)
    d.band("mid", waves(154, 3, 24))
    d.shape("light", "M140 156 L144 140 L150 150 L156 132 L162 150 L168 138 L172 156Z")
    for x, y, r in [(138, 134, 2.6), (176, 132, 2.2), (166, 124, 1.8), (148, 124, 1.8)]:
        d.marks("light", circle(x, y, r))
    d.band("near", waves(172, 4, 30))
    d.stroke("light", "M60 182 q8 -4 16 0 M108 178 q8 -4 16 0", 2, line=False)


def waterpark_ring(d: Drawing):
    d.band("ground", "M-30 -30 H230", shadow=False, line=False)
    d.stroke("far", "M-30 30 H230 M40 -30 V44 M110 -30 V44 M180 -30 V44", 1.4, line=False)
    d.band("mid", "M-30 46 H230")
    d.stroke("far", "M26 92 q10 -5 20 0 T66 92 M136 170 q10 -5 20 0 T176 170 M30 160 q10 -5 20 0", 2.4, line=False)
    d.stroke("light", circle(96, 120, 50), 1.6)
    d.shape("hero", _ring(96, 120, 18, 41), extra='fill-rule="evenodd"')
    for a in [0, 90, 180, 270]:
        d.shape("light", _annulus(96, 120, 18, 41, a + 20, a + 60), shadow=False, spot=True)
    d.shape("light", ellipse(84, 98, 9, 4), shadow=False, line=False, extra='opacity=".5" transform="rotate(-30 84 98)"')

    def ball():
        d.shape("light", circle(0, 0, 15))
        d.shape("pop", "M0 -15 A15 15 0 0 1 13 -7.5 L0 0Z M13 7.5 A15 15 0 0 1 -13 7.5 L0 0Z", shadow=False, spot=True)
        d.shape("hero2", "M-13 -7.5 A15 15 0 0 1 0 -15 L0 0Z M13 -7.5 A15 15 0 0 1 13 7.5 L0 0Z", shadow=False)
        d.marks("light", circle(0, 0, 3))
    group(d, "translate(156 98) rotate(15)", ball)


def waterpark_splash(d: Drawing):
    d.disc("glow", 152, 50, 16)
    d.band("far", hills(124, 8, -30))
    d.limb("dark", "M34 96 V160 M66 112 V160", 4)

    def slide():
        d.limb("hero", "M-30 54 C10 52 40 108 90 116", 30, spot=True)
        d.shape("dark", ellipse(92, 116, 6, 14), shadow=False, extra='transform="rotate(10 92 116)"')
        d.limb("light", "M-30 54 C10 52 40 108 92 117", 9, shadow=False)
    _clip(d, slide)
    d.limb("light", "M94 116 C108 114 118 122 126 134", 9)
    d.band("mid", waves(140, 3, 26))
    d.limb("dark", "M134 128 L124 106 M146 128 L156 107", 5, shadow=False)
    d.marks("dark", circle(140, 120, 8.5))
    d.shape("light", "M108 146 C112 134 116 132 118 122 C122 130 124 134 128 132 C129 124 130 118 132 112 "
                     "C134 122 134 130 140 132 C146 130 148 124 150 114 C152 122 152 130 154 134 C160 132 166 126 172 122 "
                     "C170 132 168 140 172 148Z")
    for x, y, r in [(112, 112, 3), (124, 100, 2.4), (166, 104, 2.6), (178, 116, 2), (104, 126, 2)]:
        d.shape("light", circle(x, y, r), shadow=False)
    d.band("near", waves(164, 4, 30))
    d.stroke("light", "M60 176 q8 -4 16 0 M120 180 q8 -4 16 0", 2, line=False)


# ================================================================ AQUARIUM
JELLY_BELL = "M-16 0 C-16 -14 -8 -21 0 -21 C8 -21 16 -14 16 0 Q12 -3 8 0 Q4 -3 0 0 Q-4 -3 -8 0 Q-12 -3 -16 0Z"


def _jelly(d: Drawing, x, y, s, spot=False):
    def draw():
        d.stroke("hero2", "M-10 0 q-4 10 0 20 t0 20 M-3 0 q4 12 0 24 t0 22 M4 0 q-4 11 0 22 t0 18 M11 0 q4 9 0 18 t0 16", 2.4)
        d.shape("hero", JELLY_BELL, spot=spot)
        d.stroke("light", "M-9 -12 C-7 -16 -3 -18 1 -18", 2, line=False)
    group(d, f"translate({x} {y}) scale({s})", draw)


def aquarium_jelly(d: Drawing):
    d.band("deep", "M-30 -30 H230", shadow=False, line=False)
    d.shape("mid", rrect(28, 22, 144, 138, 18))
    d.shape("near", "M28 112 C60 104 90 118 120 110 C140 105 160 108 172 112 V142 A18 18 0 0 1 154 160 H46 A18 18 0 0 1 28 142Z",
            shadow=False, line=False)
    bubbles(d, [(48, 128, 2.6), (54, 112, 3.4), (46, 96, 2.2)])
    _jelly(d, 74, 58, 1.0)
    _jelly(d, 130, 78, 1.25, spot=True)
    _jelly(d, 90, 110, 0.7)
    d.band("dark", "M-30 166 H230", line=False)
    d.limb("dark", "M141 150 L154 128", 5, shadow=False)
    d.shape("dark", "M124 172 C124 152 128 142 136 142 C144 142 148 152 148 172Z")
    d.shape("dark", circle(136, 132, 8.5))


MANTA = ("M100 40 C106 40 110 46 114 52 C128 54 146 58 164 70 C150 74 132 80 116 88 C112 96 106 102 100 102 "
         "C94 102 88 96 84 88 C68 80 50 74 36 70 C54 58 72 54 86 52 C90 46 94 40 100 40Z")


def aquarium_tunnel(d: Drawing):
    d.band("mid", "M-30 -30 H230", shadow=False, line=False)
    d.band("near", waves(118, 4, 30), line=False)
    for x, y, s in [(52, 104, 0.8), (64, 96, 0.7), (60, 112, 0.7), (150, 116, 0.8), (140, 108, 0.7)]:
        d.shape("hero2", fish(x, y, s, right=x > 100), shadow=False)
    d.stroke("dark", "M100 102 Q102 118 96 132", 2)
    d.shape("dark", MANTA)
    d.shape("light", "M92 56 C96 64 104 64 108 56 C106 72 94 72 92 56Z", shadow=False, line=False)
    d.shape("dark", "M88 44 L84 34 L92 42Z M112 44 L116 34 L108 42Z", shadow=False)
    def arches():
        for w, sw in [(96, 7), (70, 5), (50, 3.6)]:
            d.stroke("light", f"M{100 - w} 200 V{150 - w * 0.55:.0f} A{w} {w * 0.9:.0f} 0 0 1 {100 + w} {150 - w * 0.55:.0f} V200", sw)
    _clip(d, arches)
    _clip(d, lambda: d.shape("ground", "M58 200 L86 150 H114 L142 200Z"))
    for x in [92, 108]:
        d.shape("dark", f"M{x - 7} 174 C{x - 7} 160 {x - 4} 156 {x} 156 C{x + 4} 156 {x + 7} 160 {x + 7} 174Z")
        d.shape("dark", circle(x, 149, 5.5), shadow=False)


CLOWNFISH = {"hero": "#F77F2A", "pop": "#B98AE0", "hero2": "#E0C3F5"}


def aquarium_clownfish(d: Drawing):
    d.band("sky2", waves(40, 5, 26), line=False)
    d.band("far", waves(66, 5, 28), line=False)
    d.band("mid", waves(96, 6, 30))
    d.band("near", waves(132, 5, 34), line=False)
    bubbles(d, [(152, 60, 3), (160, 46, 2.2), (146, 36, 3.8)])
    tent = ""
    for i in range(11):
        bx = 52 + i * 9.6
        tx = 30 + i * 14 + (6 if i % 2 else -4)
        ty = 120 + abs(i - 5) * 4 + (6 if i % 2 else 0)
        d.limb("pop" if i % 2 else "hero2", f"M{bx:.1f} 176 Q{(bx + tx) / 2 + 6:.1f} {(176 + ty) / 2:.1f} {tx:.1f} {ty:.1f}", 7,
               shadow=i % 2 == 0, spot=i % 2 == 1)
    d.shape("pop", "M40 200 C40 176 62 166 100 166 C138 166 160 176 160 200Z")

    def clown():
        d.shape("hero", "M84 74 C90 60 108 60 116 74Z", spot=True)
        d.shape("hero", "M128 92 L148 76 C146 86 146 98 148 108 L128 96Z", spot=True)
        d.shape("hero", "M56 92 C60 76 80 70 100 72 C114 73 124 80 132 92 C124 104 114 110 100 111 C80 112 60 108 56 92Z", spot=True)
        for st in ["M72 76 C67 86 67 98 72 108 L80 110 C76 98 76 86 80 73Z",
                   "M98 72 C93 84 93 100 98 111 L108 110 C104 100 104 84 108 73Z",
                   "M124 82 C121 88 121 96 124 102 L130 96 L130 88Z"]:
            d.shape("light", st, shadow=False)
            d.stroke("mark", st, 1.2, line=False)
        d.shape("hero", "M84 100 C80 108 82 114 88 118 C90 112 92 106 92 102Z")
        d.marks("mark", circle(64, 88, 3))
        d.marks("light", circle(63, 87, 1))
    group(d, "translate(0 -6) rotate(-6 100 92)", clown)


# ================================================================ FIREWORKS
def fireworks_harbour(d: Drawing):
    _night(d)
    for x, y in [(30, 50), (170, 40), (120, 24), (60, 26), (180, 92)]:
        d.marks("light", circle(x, y, 1.2))
    d.stroke("glow2", "M64 128 Q66 96 70 70 M140 128 Q138 104 136 84", 1.6, line=False)
    _burst(d, 70, 62, 32, "pop", 16, spot=True)
    _burst(d, 70, 62, 16, "hero2", 10, w=1.8)
    _burst(d, 136, 76, 24, "glow2", 14, w=2)
    _burst(d, 112, 36, 15, "light", 12, w=1.6)
    sky = "M-30 136 V122 H20 V104 H34 V116 H46 V92 H60 V112 H74 V100 H86 V120 H104 V86 H116 V114 H132 V100 H146 V118 H164 V108 H178 V124 H230 V136Z"
    _clip(d, lambda: d.shape("dark", sky))
    d.marks("glow2", rrect(108, 92, 4, 4, 1) + rrect(108, 102, 4, 4, 1) + rrect(50, 98, 4, 4, 1) + rrect(150, 108, 4, 4, 1)
            + rrect(78, 106, 4, 4, 1) + rrect(24, 110, 4, 4, 1))
    d.band("mid", waves(132, 2, 24))
    d.stroke("pop", "M62 144 H78 M64 156 H76 M66 168 H74", 2.6, line=False)
    d.stroke("glow2", "M128 142 H144 M131 154 H141", 2.6, line=False)

    def boat():
        d.stroke("dark", "M0 0 V-24", 1.6)
        d.shape("light", "M1 -22 L16 -2 H1Z", shadow=False)
        d.shape("dark", "M-14 0 H22 L16 8 H-8Z")
    group(d, "translate(100 154)", boat)


def fireworks_burst(d: Drawing):
    _night(d)
    for x, y in [(36, 60), (164, 150), (156, 40), (40, 140), (100, 22)]:
        d.marks("light", circle(x, y, 1.3))
    _burst(d, 100, 98, 62, "pop", 24, inner=0.42, w=3, spot=True)
    _burst(d, 100, 98, 42, "glow2", 18, inner=0.3, w=2.6, rot=7.5)
    _burst(d, 100, 98, 22, "light", 12, inner=0.2, w=2.2)
    d.disc("light", 100, 98, 4, shadow=False)
    _burst(d, 46, 44, 14, "hero2", 10, w=1.8)
    _burst(d, 160, 160, 12, "far", 10, w=1.6)
    d.stroke("glow2", "M160 172 Q166 186 160 200", 1.4, line=False)


def fireworks_sparkler(d: Drawing):
    _night(d)
    for x, y in [(40, 60), (160, 140), (150, 30), (44, 150), (70, 30)]:
        d.marks("light", circle(x, y, 1.3))
    d.stroke("glow2", _heart(84, 110, 3.6), 3)
    d.limb("mark", "M62 164 L118 84", 3, shadow=False)
    d.stroke("light", "M62 164 L118 84", 1, line=False)
    d.shape("hero", "M46 196 L52 166 L76 172 L72 200Z", spot=True)
    d.shape("light", rrect(54, 146, 22, 24, 9))
    d.shape("light", rrect(48, 150, 14, 9, 4.5), shadow=False)
    d.stroke("mark", "M60 158 H74 M60 164 H74", 1.2, line=False)
    _burst(d, 122, 78, 28, "glow2", 18, inner=0.2, w=2.2, spot=True)
    _burst(d, 122, 78, 16, "light", 12, inner=0.2, w=1.8, rot=15)
    d.disc("light", 122, 78, 5, shadow=False)
    for x, y in [(152, 52), (90, 62), (156, 96), (138, 40), (100, 44)]:
        d.marks("glow2", _star(x, y, 4))


# ================================================================ YOGA RETREAT
JUNGLE = {"near": "#4F9A6A", "deep": "#2F6B4E", "far": "#9CC79A"}


def yoga_deck(d: Drawing):
    d.disc("glow", 100, 70, 26)
    d.band("far", hills(108, 10))
    d.stroke("dark", "M-30 104 H230 M30 104 V124 M70 104 V124 M130 104 V124 M170 104 V124", 2.4)
    d.band("ground", "M-30 122 H230")
    d.stroke("mid", "M-30 140 H230 M-30 160 H230 M-30 182 H230", 1.6, line=False)
    d.shape("hero", "M76 130 H124 L136 176 H64Z")
    d.shape("hero2", rrect(72, 120, 56, 13, 6.5), spot=True)
    d.stroke("hero", "M76 126.5 H124", 1.4, line=False)
    d.shape("pop", "M150 150 L172 146 L178 160 L156 165Z", spot=True)
    d.shape("light", "M150 150 L172 146 L174 151 L152 155Z", shadow=False, line=False)
    def leaves():
        _leaf(d, -6, 66, 64, 15, 18, "near", "deep")
        _leaf(d, -10, 108, 60, 13, -12, "deep", "near", line=False)
        _leaf(d, -2, 150, 48, 12, -40, "near", "deep", line=False)
        _leaf(d, 206, 58, 64, 15, 162, "deep", "near")
        _leaf(d, 210, 104, 62, 14, 192, "near", "deep", line=False)
        _leaf(d, 40, -6, 50, 12, 70, "near", "deep", line=False)
        _leaf(d, 160, -6, 50, 12, 110, "near", "deep", line=False)
    _clip(d, leaves)


def yoga_pose(d: Drawing):
    d.disc("glow", 100, 96, 42)
    d.band("far", hills(138, 8, 20))
    d.band("mid", hills(158, 6, -30))
    d.shape("near", "M40 196 C44 168 64 156 100 154 C136 156 156 168 160 196Z")
    d.limb("dark", "M90 110 Q78 126 72 144 M110 110 Q122 126 128 144", 6.5)
    d.shape("dark", ellipse(100, 148, 36, 9.5))
    d.shape("dark", "M84 146 C84 126 86 112 92 107 H108 C114 112 116 126 116 146Z")
    d.shape("dark", circle(100, 94, 10))
    d.shape("dark", circle(100, 82, 5))
    d.marks("glow2", circle(71, 145, 2.6) + circle(129, 145, 2.6))
    for x, y in [(48, 60), (152, 60), (36, 92), (164, 92)]:
        pass


LOTUS = {"hero": "#F28AB2", "hero2": "#F9C6DA", "glow2": "#FFD25E", "mid": "#7FC8C2", "near": "#5E9C6A"}
PETAL = "M0 0 C-11 -12 -10 -32 0 -46 C10 -32 11 -12 0 0Z"


def yoga_lotus(d: Drawing):
    d.disc("glow", 148, 50, 16)
    d.band("far", hills(104, 8, -20))
    d.band("mid", waves(116, 2, 30))
    for x, y, rx, ry in [(44, 156, 30, 10), (160, 140, 26, 8), (128, 172, 20, 6)]:
        d.shape("near", f"M{x} {y} L{x + rx * .9:.0f} {y - ry * .4:.0f} A{rx} {ry} 0 1 1 {x + rx * .9:.0f} {y + ry * .4:.0f}Z")
    d.stroke("light", "M54 132 q10 -4 20 0 M126 132 q10 -4 20 0 M76 170 q10 -4 20 0", 2, line=False)

    def flower():
        for a in [-78, -50, 50, 78]:
            d.shape("hero2", PETAL, extra=f'transform="rotate({a})"')
        for a in [-26, 26]:
            d.shape("hero", PETAL, extra=f'transform="rotate({a})"', spot=True)
        d.shape("hero2", PETAL, extra='transform="scale(1.05)"')
        d.shape("hero", "M-26 -10 C-20 -2 -10 2 0 2 C10 2 20 -2 26 -10 C20 4 10 8 0 8 C-10 8 -20 4 -26 -10Z", spot=True)
    group(d, "translate(100 124)", flower)


# ================================================================ SPA DAY
STONES = {"hero": "#8D99AE", "hero2": "#B7C0CE", "mark": "#5C677D", "glow2": "#FFD25E"}


def spa_stones(d: Drawing):
    d.disc("glow", 100, 92, 54)
    for x, top in [(150, 30), (166, 50), (38, 44)]:
        d.limb("near", f"M{x - 1} 200 L{x + 1} {top}", 7)
        d.stroke("deep", f"M{x - 3.5} {top + 30} H{x + 3.5} M{x - 3.5} {top + 66} H{x + 3.5} M{x - 3.5} {top + 102} H{x + 3.5}", 1.6, line=False)
    _leaf(d, 150, 60, 34, 7, -30, "near", "deep")
    _leaf(d, 38, 80, 30, 6, 210, "near", "deep")
    d.band("far", waves(156, 3, 28))
    d.shape("mark", ellipse(98, 156, 44, 13))
    d.shape("hero", ellipse(98, 134, 34, 11.5), spot=True)
    d.shape("hero2", ellipse(98, 114, 26, 10))
    d.shape("mark", ellipse(98, 97, 17, 8), spot=True)
    d.stroke("light", "M84 94 Q90 91 96 91 M80 130 Q88 126 98 126", 1.6, line=False)
    _frangipani(d, 134, 150, 1.0, rot=12)
    d.band("near", waves(178, 3, 30), line=False)


def spa_bath(d: Drawing):
    d.band("far", "M-30 -30 H230", shadow=False, line=False)
    d.stroke("sky2", "M-30 40 H230 M-30 80 H230 M-30 120 H230 M30 -30 V160 M70 -30 V160 M110 -30 V160 M150 -30 V160", 1.4, line=False)
    d.band("mid", "M-30 160 H230")
    d.limb("hero2", "M148 110 V82 Q148 72 138 72 H132", 4.5)
    d.shape("light", "M38 94 C46 82 60 86 64 92 C70 80 86 82 90 90 C96 78 114 80 118 90 C124 80 142 82 144 94 "
                     "C156 92 162 102 156 110 H44 C36 106 34 98 38 94Z")
    d.shape("hero2", "M100 88 C100 80 110 78 114 84 L120 82 L116 88 C118 96 108 100 100 96Z", shadow=False)
    d.shape("light", rrect(32, 104, 136, 10, 5))
    d.shape("light", "M40 112 H160 C160 140 142 156 118 156 H82 C58 156 40 140 40 112Z", spot=True)
    d.stroke("hero2", "M46 124 H154", 2)
    d.limb("hero2", "M62 150 L56 166 M138 150 L144 166", 5)
    for x in [16, 30]:
        pass
    d.shape("light", rrect(170, 138, 12, 26, 3))
    d.shape("pop", "M176 124 C181 130 181 135 176 137 C171 135 171 130 176 124Z", shadow=False, spot=True)
    for x, y, r in [(52, 72, 4), (66, 60, 3), (140, 64, 3.5), (128, 52, 2.5)]:
        d.stroke("light", circle(x, y, r), 1.8)


def spa_towels(d: Drawing):
    d.disc("glow", 100, 100, 58)
    _leaf(d, 150, 92, 46, 10, -50, "near", "deep")
    _leaf(d, 52, 92, 46, 10, 230, "near", "deep")
    d.shape("dark", rrect(30, 156, 140, 10, 3))
    d.limb("dark", "M44 164 V186 M156 164 V186", 5)

    def towel(x, y, role, spot=False):
        d.shape(role, circle(x, y, 16), spot=spot)
        d.stroke("mark" if role == "light" else "light",
                 f"M{x} {y} m-1.5 0 a1.5 1.5 0 1 1 3 0 a4.5 4.5 0 1 1 -9 0 a7.5 7.5 0 1 1 15 0 a10.5 10.5 0 1 1 -21 0", 1.4)
    for x in [68, 100, 132]:
        towel(x, 140, "light" if x != 100 else "hero", x == 100)
    for x in [84, 116]:
        towel(x, 110, "hero")
    towel(100, 80, "light")
    _frangipani(d, 108, 62, 0.9, rot=20)
    d.shape("light", rrect(152, 128, 12, 28, 3))
    d.shape("pop", "M158 114 C163 120 163 125 158 127 C153 125 153 120 158 114Z", shadow=False, spot=True)


# ================================================================ MASSAGE
def massage_stones(d: Drawing):
    d.band("far", "M-30 -30 H230", shadow=False, line=False)
    d.shape("sky", rrect(120, 26, 52, 62, 26), line=False)
    d.disc("glow", 146, 66, 12, line=False)
    d.stroke("far", "M146 26 V88 M120 62 H172", 3, line=False)
    _leaf(d, 30, 156, 40, 10, -70, "near", "deep")
    _leaf(d, 30, 156, 34, 8, -110, "deep", "near")
    d.band("mid", "M-30 156 H230", line=False)
    d.limb("dark", "M46 136 L40 178 M154 136 L160 178", 5)
    d.shape("hero2", rrect(28, 128, 144, 12, 4), spot=True)
    d.shape("dark", "M58 128 C58 112 68 104 84 104 H120 C124 104 126 112 126 128Z")
    d.shape("light", "M112 128 C112 110 118 104 132 104 C150 104 166 112 172 128Z")
    d.stroke("far", "M120 110 L126 128 M136 106 L140 128", 1.4, line=False)
    d.shape("dark", circle(46, 114, 11))
    d.shape("dark", ellipse(36, 108, 6, 5), shadow=False)
    for x, y, rx in [(70, 103, 7), (86, 101, 8), (102, 101, 7.5)]:
        d.shape("mark", ellipse(x, y, rx, 5))
    d.stroke("light", "M66 101 Q70 99 74 100 M82 99 Q86 97 90 98", 1.2, line=False)
    _frangipani(d, 160, 112, 0.6, rot=-10)


def massage_oil(d: Drawing):
    d.disc("glow", 100, 100, 56)
    _leaf(d, 112, 150, 70, 15, -62, "near", "deep")
    _leaf(d, 96, 152, 62, 13, -118, "deep", "near")
    d.shape("dark", rrect(86, 30, 22, 30, 11))
    d.shape("dark", rrect(82, 56, 30, 16, 3))
    d.shape("hero", "M72 72 H122 C130 72 136 78 136 86 V156 C136 164 130 170 122 170 H72 C64 170 58 164 58 156 V86 C58 78 64 72 72 72Z", spot=True)
    d.shape("light", rrect(70, 104, 54, 40, 6), shadow=False)
    _leaf(d, 82, 132, 30, 7, -40, "near", "deep", shadow=False)
    d.stroke("light", "M66 88 V144", 3, line=False)
    d.shape("hero2", "M150 64 C156 74 160 80 160 86 C160 92 155 96 150 96 C145 96 140 92 140 86 C140 80 144 74 150 64Z", spot=True)
    d.shape("hero2", ellipse(150, 168, 22, 6))
    _frangipani(d, 50, 162, 0.85, rot=-8)
    _frangipani(d, 158, 146, 0.7, rot=30)


def massage_cabana(d: Drawing):
    d.disc("glow", 146, 66, 18)
    d.band("far", waves(126, 3, 30))
    d.band("ground", "M-30 146 Q100 138 230 146")
    d.limb("dark", "M44 70 V170 M156 70 V170", 4.5)
    d.shape("light", "M44 70 C40 90 52 120 46 160 C56 140 60 104 58 72Z")
    d.shape("light", "M156 70 C160 90 148 120 154 160 C144 140 140 104 142 72Z")
    d.limb("pop", "M44 116 L54 118 M156 116 L146 118", 3, shadow=False)
    d.shape("light", "M30 72 L100 38 L170 72Z", spot=True)
    scal = "M30 70 H170 V76"
    for i in range(7):
        x = 170 - i * 20
        scal += f" Q{x - 10} 86 {x - 20} 76"
    d.shape("pop", scal + "Z", spot=True)
    d.limb("dark", "M74 146 V172 M126 146 V172", 4)
    d.shape("hero", rrect(62, 136, 76, 11, 4))
    d.shape("light", rrect(66, 128, 26, 9, 4.5))
    d.shape("hero2", rrect(98, 128, 34, 9, 3), shadow=False)
    _frangipani(d, 120, 132, 0.45)


# ================================================================ HONEYMOON
def _hut(d: Drawing, x, y, s=1.0):
    def draw():
        d.limb("dark", "M-14 0 L-14.5 30 M14 0 L14.5 30 M0 0 L0.5 30", 3)
        d.shape("dark", rrect(-24, -4, 48, 6, 2))
        d.shape("light", rrect(-18, -26, 36, 24, 2))
        d.shape("dark", rrect(-5, -18, 10, 16, 1.5), shadow=False)
        d.shape("hero2", "M-30 -22 L0 -46 L30 -22 Q15 -18 0 -22 Q-15 -18 -30 -22Z", spot=True)
    group(d, f"translate({x} {y}) scale({s})", draw)


def honeymoon_bungalow(d: Drawing):
    d.disc("glow", 100, 112, 44)
    d.shape("light", cloud(26, 66, 0.9))
    d.band("far", waves(118, 3, 30))
    d.stroke("dark", "M-10 132 H96", 4)
    _hut(d, 150, 118, 0.7)
    d.band("mid", waves(136, 3, 34))
    _hut(d, 74, 128, 1.1)
    d.stroke("glow2", "M88 156 H112 M92 166 H108", 3, line=False)
    d.band("near", waves(160, 4, 30))
    _palm(d, 186, 160, 172, 84, 0.7)


def honeymoon_champagne(d: Drawing):
    d.disc("glow", 100, 104, 56)
    for x, y, r in [(46, 54, 5), (156, 50, 4), (160, 140, 4.5), (38, 128, 3.5)]:
        d.shape("light", _star(x, y, r), shadow=False)

    def flute(spot):
        d.shape("light", "M-14 -60 H14 C15 -30 10 -8 0 -4 C-10 -8 -15 -30 -14 -60Z")
        d.shape("hero2", "M-12 -46 H12 C12 -26 8 -10 0 -8 C-8 -10 -12 -26 -12 -46Z", shadow=False, spot=spot)
        d.limb("light", "M0 -4 L0.4 34", 3.5)
        d.shape("light", ellipse(0, 36, 15, 4.5))
        d.marks("light", circle(-4, -24, 1.6) + circle(3, -34, 1.3) + circle(-2, -40, 1.1) + circle(4, -18, 1.4))
    group(d, "translate(74 134) rotate(17) scale(.92)", lambda: flute(True))
    group(d, "translate(126 134) rotate(-17) scale(.92)", lambda: flute(False))
    d.stroke("hero2", "M100 68 L100 56 M90 70 L83 60 M110 70 L117 60", 2.6)
    d.shape("pop", _heart(100, 42, 0.9), spot=True)


def honeymoon_chairs(d: Drawing):
    d.disc("glow", 100, 100, 30)
    d.band("far", waves(112, 3, 30))
    d.band("mid", waves(126, 3, 34), line=False)
    d.band("ground", "M-30 140 Q100 132 230 140")

    def chair(x, canvas, spot):
        d.limb("dark", f"M{x - 20} 176 L{x - 16} 112 M{x + 20} 176 L{x + 16} 112", 4)
        d.shape(canvas, f"M{x - 18} 112 H{x + 18} L{x + 20} 156 H{x - 20}Z", spot=spot)
        d.shape("light", f"M{x - 6} 112 H{x + 6} L{x + 7} 156 H{x - 7}Z", shadow=False)
        d.limb("dark", f"M{x - 24} 156 H{x + 24}", 4)
    chair(70, "hero", True)
    chair(130, "pop", False)
    d.shape("pop", _heart(100, 70, 0.7), shadow=False)
    d.band("deep", "M-30 184 Q100 178 230 184", line=False)


# ================================================================ PROPOSAL
RING = {"hero2": "#F2C14E", "mark": "#B8862A"}


def proposal_ringbox(d: Drawing):
    d.disc("glow", 100, 100, 40)
    d.band("far", waves(116, 3, 30))
    d.band("mid", waves(128, 3, 34), line=False)
    d.band("ground", "M-30 146 Q100 136 230 146")
    d.shape("pop", "M62 112 L70 66 C71 62 74 60 78 60 H122 C126 60 129 62 130 66 L138 112Z", spot=True)
    d.shape("dark", "M70 108 L76 72 H124 L130 108Z", shadow=False)
    d.shape("pop", rrect(58, 112, 84, 46, 6), spot=True)
    d.shape("dark", rrect(66, 116, 68, 14, 4), shadow=False)
    d.stroke("hero2", ellipse(100, 106, 13, 13), 4.5)
    d.shape("light", "M92 92 L96 86 H104 L108 92 L100 100Z")
    d.stroke("far", "M92 92 H108 M96 86 L100 100 L104 86", 0.9, line=False)
    for x, y, r in [(80, 82, 4), (124, 80, 3)]:
        d.shape("light", _star(x, y, r, 0.35, 4), shadow=False)
    d.stroke("light", "M30 172 q8 -4 16 0 M148 176 q8 -4 16 0", 2, line=False)


def proposal_ring(d: Drawing):
    d.disc("glow", 100, 100, 62)
    d.stroke("mark", ellipse(100, 124, 40, 36), 13, line=False)
    d.limb("hero2", ellipse(100, 124, 40, 36), 9, shadow=False, spot=True)
    d.stroke("light", "M68 106 C72 98 80 92 88 90", 2.4, line=False)
    d.shape("hero2", "M84 92 L92 80 H108 L116 92 L108 98 H92Z")
    d.shape("light", "M76 66 L88 52 H112 L124 66 L100 92Z", spot=True)
    d.shape("hero2", rrect(82, 64, 36, 3, 1.5), shadow=False, line=False)
    d.stroke("mark", "M76 66 H124 M88 52 L94 66 L100 92 L106 66 L112 52 M94 66 L100 52 L106 66", 1.2, line=False)
    for x, y, r in [(138, 50, 8), (60, 46, 5), (150, 84, 4.5)]:
        d.shape("light", _star(x, y, r, 0.3, 4), shadow=False)


def proposal_kneel(d: Drawing):
    d.disc("glow", 100, 106, 50)
    d.band("far", hills(146, 6))
    d.shape("near", "M-30 230 V160 Q100 138 230 160 V230Z")
    # standing partner
    d.shape("dark", "M118 92 C112 106 110 132 104 158 H144 C138 132 136 106 130 92 C128 86 120 86 118 92Z")
    d.limb("dark", "M120 98 L110 118", 4.5)
    d.shape("dark", circle(124, 78, 8.5))
    d.shape("dark", "M116 76 C116 66 132 64 133 76 C134 86 134 94 138 100 C128 98 124 90 124 84Z", shadow=False)
    # kneeling partner
    d.limb("dark", "M80 136 L74 156 L56 157 M82 136 L102 137 L101 157", 9)
    d.shape("dark", "M68 108 C66 118 70 132 72 140 H90 C90 128 90 114 86 108 C82 102 72 102 68 108Z")
    d.limb("dark", "M84 112 L102 114", 5)
    d.shape("dark", circle(78, 94, 8.5))
    d.shape("pop", rrect(102, 108, 9, 8, 2), spot=True)
    d.shape("light", circle(106.5, 106, 2.2), shadow=False)
    for x, y, sc in [(146, 46, 0.6), (162, 64, 0.45), (52, 58, 0.5)]:
        d.shape("pop", _heart(x, y, sc), shadow=False, spot=True)


# ================================================================ WEDDING
def wedding_bells(d: Drawing):
    d.disc("glow", 100, 104, 58)
    bell = "M0 -34 C-13 -34 -18 -20 -18 -8 C-18 6 -22 12 -28 18 H28 C22 12 18 6 18 -8 C18 -20 13 -34 0 -34Z"

    def b(spot):
        d.limb("hero2", "M0 -38 L0.3 -48", 3)
        d.shape("mark", circle(0, 22, 6))
        d.shape("hero2", bell, spot=spot)
        d.stroke("light", "M-9 -24 C-12 -16 -12 -6 -12 2", 3, line=False)
        d.shape("mark", rrect(-28, 14, 56, 5, 2.5), shadow=False, line=False)
    group(d, "translate(78 106) rotate(14)", lambda: b(True))
    group(d, "translate(122 106) rotate(-14)", lambda: b(False))
    d.limb("pop", "M100 62 C86 46 70 50 74 62 C78 72 92 66 100 62 C108 66 122 72 126 62 C130 50 114 46 100 62Z", 4, shadow=False)
    d.shape("pop", "M100 62 C90 46 72 48 74 60 C76 72 92 68 100 62Z M100 62 C110 46 128 48 126 60 C124 72 108 68 100 62Z", spot=True)
    d.shape("pop", "M97 62 L88 84 L94 82 L96 88 L100 66 L104 88 L106 82 L112 84 L103 62Z", shadow=False)
    d.shape("pop", circle(100, 62, 5.5), shadow=False)
    for x, y, r in [(44, 66, 4), (156, 68, 4.5), (100, 160, 3.5)]:
        d.shape("light", _star(x, y, r, 0.35, 4), shadow=False)


def wedding_arch(d: Drawing):
    d.disc("glow", 100, 100, 26)
    d.band("far", waves(110, 3, 30))
    d.band("ground", "M-30 128 Q100 120 230 128")
    d.limb("light", "M48 172 V92 C48 56 70 38 100 38 C130 38 152 56 152 92 V172", 6)
    d.shape("light", "M52 70 C48 100 62 120 56 150 C66 130 68 100 64 74Z", shadow=False)
    d.shape("light", "M148 70 C152 100 138 120 144 150 C134 130 132 100 136 74Z", shadow=False)
    pts = [(48, 92), (50, 70), (60, 52), (78, 40), (100, 36), (122, 40), (140, 52), (150, 70), (152, 92)]
    for i, (x, y) in enumerate(pts):
        _leaf(d, x, y, 14, 4, (i * 47) % 360, "near", "deep", shadow=False)
    roles = ["pop", "light", "hero2", "pop", "light", "hero2", "pop", "light", "pop"]
    for (x, y), role in zip(pts, roles):
        d.shape(role, circle(x, y, 7.5), spot=role == "pop")
        d.marks("mark" if role != "pop" else "light", circle(x, y, 1.8))
    for x, y, role in [(42, 168, "pop"), (158, 168, "pop"), (36, 156, "light"), (164, 156, "hero2")]:
        d.shape(role, circle(x, y, 6))
    d.stroke("pop", "M90 150 l2 1 M104 162 l2 1 M94 176 l2 1 M110 140 l2 1 M86 166 l2 1", 2.4, line=False)


def wedding_cake(d: Drawing):
    d.disc("glow", 100, 100, 58)
    d.shape("dark", "M56 170 H144 L136 162 H64Z")
    d.limb("dark", "M100 162 L100.5 176", 6)
    d.shape("dark", rrect(70, 174, 60, 6, 3))

    def tier(x, y, w, h):
        d.shape("light", rrect(x, y, w, h, 4))
        drip = f"M{x} {y + 4} H{x + w}"
        n = int(w // 12)
        for i in range(n):
            x0 = x + w - i * w / n
            drip += f" V{y + 8} Q{x0 - w / n / 2:.1f} {y + 15} {x0 - w / n:.1f} {y + 8}"
        d.shape("hero2", drip + f" V{y + 4}Z", shadow=False, spot=True)
        d.stroke("mark", f"M{x + 4} {y + h - 6} H{x + w - 4}", 1.2, line=False)
    tier(58, 132, 84, 30)
    tier(70, 104, 60, 28)
    tier(82, 78, 36, 26)
    for x, y in [(66, 150), (134, 150), (76, 122), (124, 122), (100, 96)]:
        d.shape("pop", circle(x, y, 5), shadow=False, spot=True)
        d.marks("light", circle(x, y, 1.4))
    d.limb("dark", "M100 78 L100.3 64", 2)
    d.shape("pop", _heart(100, 56, 0.9), spot=True)


# ================================================================ FAMILY HOLIDAY
def family_sandcastle(d: Drawing):
    d.disc("glow", 152, 50, 15)
    d.shape("light", cloud(28, 52, 0.9))
    d.band("far", waves(104, 3, 30))
    d.band("mid", waves(118, 3, 34), line=False)
    d.band("ground", "M-30 132 Q100 124 230 132")
    crenel = lambda x, y, w: f"M{x} {y} h{w / 5:.1f} v-5 h{w / 5:.1f} v5 h{w / 5:.1f} v-5 h{w / 5:.1f} v5 h{w / 5:.1f}"
    d.stroke("dark", "M100 72 V50", 1.6)
    d.shape("pop", "M100 50 L114 55 L100 60Z", shadow=False, spot=True)
    castle = (f"M50 160 V118 {crenel(50, 118, 26)[crenel(50, 118, 26).index('h'):]} V136 H86 V100 "
              f"{crenel(86, 100, 28)[crenel(86, 100, 28).index('h'):]} V136 H124 V118 "
              f"{crenel(124, 118, 26)[crenel(124, 118, 26).index('h'):]} V160Z")
    d.shape("hero2", castle)
    d.shape("hero2", "M92 100 L100 76 L108 100Z")
    d.shape("dark", "M92 160 V146 A8 8 0 0 1 108 146 V160Z", shadow=False)
    d.marks("mark", rrect(60, 128, 6, 8, 3) + rrect(134, 128, 6, 8, 3) + rrect(97, 112, 6, 9, 3))
    d.shape("hero", "M150 140 L174 140 L170 170 H154Z", spot=True)
    d.stroke("dark", "M150 141 Q162 124 174 141", 1.6)
    d.shape("hero2", rrect(149, 136, 26, 6, 2), shadow=False, line=False)
    d.limb("dark", "M32 168 L50 132", 3.4)
    d.shape("pop", "M46 124 L58 128 L54 142 C48 146 42 142 44 136Z", spot=True)
    d.shape("light", "M76 176 C76 168 86 168 86 176Z M118 178 l4 -8 l4 8Z", shadow=False)


def family_car(d: Drawing):
    d.disc("glow", 52, 58, 16)
    d.band("far", hills(108, 12, 20))
    d.band("mid", hills(126, 8, -20), line=False)
    d.band("dark", "M-30 146 Q100 140 230 146")
    d.stroke("light", "M-30 160 H30 M50 158 H90 M110 157 H150 M170 158 H230", 2.4, line=False)
    d.shape("hero2", rrect(60, 66, 38, 14, 3))
    d.shape("pop", rrect(98, 62, 32, 18, 3), spot=True)
    d.shape("light", "M64 52 L140 50 C146 50 148 54 144 58 L68 60 C62 60 60 54 64 52Z")
    d.stroke("dark", "M62 82 L138 82 M70 80 V86 M130 80 V86", 2.2)
    d.shape("hero", "M34 136 C34 120 40 112 52 110 L66 88 H128 L146 110 C160 112 168 118 168 130 V136 C168 140 166 142 162 142 H38 C35 142 34 140 34 136Z")
    d.shape("light", "M72 94 H96 V110 H62Z", shadow=False)
    d.shape("light", "M102 94 H124 L136 110 H102Z", shadow=False)
    d.shape("glow2", rrect(158, 116, 8, 6, 2), shadow=False)
    d.stroke("mark", "M99 94 V136 M104 118 H110", 1.6, line=False)
    for x in [64, 140]:
        d.shape("dark", circle(x, 140, 14))
        d.shape("light", circle(x, 140, 5.5), shadow=False)


def _person(d: Drawing, x, base, s, role="dark"):
    """A very simple standing figure (head, rounded body, legs), feet on `base`. Absolute coordinates
    (no group transform: Chrome mis-clips drop shadows inside some translated groups)."""
    X = lambda dx: round(x + dx * s, 1)
    Y = lambda dy: round(base + dy * s, 1)
    d.limb(role, f"M{X(-5)} {Y(-2)} L{X(-5.5)} {Y(-26)} M{X(5)} {Y(-2)} L{X(5.5)} {Y(-26)}", 6.5 * s)
    d.shape(role, f"M{X(-11)} {Y(-26)} V{Y(-50)} C{X(-11)} {Y(-58)} {X(-6)} {Y(-62)} {X(0)} {Y(-62)} "
                  f"C{X(6)} {Y(-62)} {X(11)} {Y(-58)} {X(11)} {Y(-50)} V{Y(-26)}Z")
    d.shape(role, circle(X(0), Y(-72), 9 * s))


def family_together(d: Drawing):
    d.disc("glow", 100, 112, 50)
    d.band("far", waves(132, 3, 30))
    d.band("ground", "M-30 156 Q100 148 230 156")
    d.limb("dark", "M57 116 Q66 126 75 128 M86 128 Q100 132 114 128 M125 128 Q134 126 143 116", 4.5, shadow=False)
    _person(d, 50, 170, 1.0)
    _person(d, 150, 170, 1.0)
    _person(d, 80, 170, 0.66)
    _person(d, 120, 170, 0.66)
    d.shape("hero", circle(150, 58, 9), spot=True)
    d.stroke("dark", "M150 67 L148 98", 1.2)
    d.shape("pop", circle(166, 70, 7), spot=False)
    d.stroke("dark", "M166 77 L152 98", 1.2)
    d.band("deep", "M-30 184 Q100 178 230 184", line=False)


# ================================================================ SOLO TRAVEL
def solo_backpack(d: Drawing):
    d.disc("glow", 64, 74, 22)
    d.band("far", "M-30 112 L20 92 L50 104 L84 78 L118 102 L150 86 L230 108")
    d.band("mid", hills(130, 10, 30))
    d.shape("near", "M-30 230 V164 C30 150 80 132 128 130 C170 128 200 140 230 150 V230Z")
    d.stroke("dark", "M150 158 Q156 150 164 146 M30 180 Q40 172 54 170", 1.6, line=False)

    def pack():
        d.limb("dark", "M-16 -36 C-30 -26 -30 0 -22 10", 4.5)
        d.shape("pop", rrect(-24, -74, 48, 14, 7))
        d.stroke("dark", "M-12 -74 V-60 M12 -74 V-60", 1.6)
        d.shape("hero", "M-24 -46 C-24 -58 -14 -64 0 -64 C14 -64 24 -58 24 -46 V4 C24 10 20 12 14 12 H-14 C-20 12 -24 10 -24 4Z", spot=True)
        d.shape("hero2", "M-24 -46 C-24 -58 -14 -64 0 -64 C14 -64 24 -58 24 -46 V-34 C12 -28 -12 -28 -24 -34Z", shadow=False)
        d.stroke("dark", "M0 -30 V-20", 2)
        d.shape("hero", rrect(-15, -16, 30, 22, 6))
        d.stroke("mark", "M-15 -8 H15", 1.4, line=False)
        d.shape("dark", rrect(-28, -30, 6, 30, 3), shadow=False)
        d.shape("dark", rrect(22, -30, 6, 30, 3), shadow=False)
    group(d, "translate(120 140) rotate(-4)", pack)
    for x, y in [(150, 50), (164, 58)]:
        d.stroke("dark", f"M{x - 5} {y} q2.5 -3 5 0 q2.5 -3 5 0", 1.6)


def solo_window(d: Drawing):
    d.band("ground", "M-30 -30 H230", shadow=False, line=False)
    d.stroke("far", "M-30 22 H230 M-30 178 H230", 2, line=False)
    d.shape("light", rrect(46, 28, 108, 146, 50))
    d.shape("sky2", rrect(58, 40, 84, 122, 40), shadow=False)
    d.disc("glow", 118, 92, 13, shadow=False)
    d.shape("far", "M58 134 C80 128 110 132 142 126 V124 A40 40 0 0 1 102 164 H98 A40 40 0 0 1 58 124Z", shadow=False, line=False)
    d.shape("light", "M64 112 C68 102 82 102 86 108 C92 100 106 102 108 110 C116 108 124 114 122 120 H70 C62 120 60 116 64 112Z", line=False)
    d.shape("dark", "M70 150 L128 110 C132 108 136 110 136 114 L138 120 L78 160 Z", spot=True)
    d.shape("pop", "M124 116 L134 104 L139 119Z", shadow=False)
    d.shape("light", "M58 78 C58 56 76 40 100 40 C124 40 142 56 142 78Z")
    d.shape("far", rrect(90, 70, 20, 5, 2.5), shadow=False)


def solo_compass(d: Drawing):
    d.shape("ground", "M28 52 L72 40 L118 54 L168 42 L176 150 L130 162 L84 148 L36 160Z")
    d.shape("far", "M72 40 L118 54 L130 162 L84 148Z", shadow=False)
    d.stroke("pop", "M44 140 C60 120 50 90 80 80 C104 72 98 60 120 60", 2.4)
    d.stroke("pop", "M114 54 L126 66 M126 54 L114 66", 2.6)
    d.shape("dark", circle(112, 116, 40))
    d.shape("hero2", circle(112, 116, 35), shadow=False, spot=True)
    d.shape("light", circle(112, 116, 29), shadow=False)
    ticks = ""
    for i in range(16):
        a = math.radians(i * 22.5)
        r0 = 22 if i % 4 == 0 else 25
        ticks += f"M{112 + r0 * math.cos(a):.1f} {116 + r0 * math.sin(a):.1f} L{112 + 28 * math.cos(a):.1f} {116 + 28 * math.sin(a):.1f} "
    d.stroke("mark", ticks, 1.4)
    d.shape("pop", "M112 116 L120 94 L112 92 Z M112 116 L104 94 L112 92 Z", shadow=False)
    d.shape("pop", "M104 94 L112 116 L120 94 L112 90Z", spot=True)
    d.shape("mark", "M104 138 L112 116 L120 138 L112 142Z")
    d.shape("dark", circle(112, 116, 3.5), shadow=False)
    d.shape("dark", rrect(106, 70, 12, 8, 3))
    d.stroke("dark", "M112 70 C112 62 120 58 126 60", 3)


# ================================================================ GAP YEAR
def gapyear_globe(d: Drawing):
    d.disc("glow", 100, 92, 62, line=False)
    d.limb("dark", "M100 146 L100.4 164", 6)
    d.shape("dark", ellipse(100, 168, 30, 7))
    d.shape("hero", circle(100, 92, 46))
    land = ("M70 66 C78 58 92 58 96 64 C100 70 92 74 92 80 C92 88 84 94 76 92 C68 90 62 76 70 66Z "
            "M104 54 C114 52 126 58 128 66 C122 70 114 68 108 64Z "
            "M108 84 C118 80 132 84 138 94 C140 106 130 118 120 124 C114 128 110 118 112 108 C106 102 102 90 108 84Z "
            "M76 106 C84 104 90 110 88 118 C86 126 78 130 74 124 C70 118 70 110 76 106Z")
    d.shape("near", land, shadow=False, spot=True)
    d.limb("mark", "M42 82 C42 46 82 30 112 40", 3.6, shadow=False)
    d.stroke("mark", "M152 120 A56 56 0 0 1 54 128", 3.6)
    d.stroke("pop", "M48 132 C30 110 34 66 66 46 C96 28 140 34 160 60", 2.2)
    for x, y in [(48, 132), (98, 38)]:
        d.shape("pop", circle(x, y, 4), shadow=False)

    def plane():
        d.shape("light", "M-12 0 C-12 -3 -8 -3 0 -3 L12 -3 C16 -3 18 -1 18 0 C18 1 16 3 12 3 L0 3 C-8 3 -12 3 -12 0Z")
        d.shape("light", "M2 -2 L-6 -14 L-1 -14 L9 -2Z M2 2 L-6 14 L-1 14 L9 2Z M-10 -1 L-15 -7 L-12 -7 L-6 -1Z", shadow=False)
    group(d, "translate(162 64) rotate(52)", plane)


def gapyear_rucksack(d: Drawing):
    d.disc("glow", 100, 104, 60)
    d.limb("dark", "M66 64 C54 80 54 130 62 160 M134 64 C146 80 146 130 138 160", 6)
    d.shape("hero", "M62 66 C62 50 78 42 100 42 C122 42 138 50 138 66 V156 C138 166 132 172 122 172 H78 C68 172 62 166 62 156Z", spot=True)
    d.shape("hero2", "M62 70 C62 50 78 42 100 42 C122 42 138 50 138 70 C126 80 74 80 62 70Z", shadow=False)
    d.stroke("dark", "M86 60 V82 M114 60 V82", 2.2)
    d.shape("hero", rrect(72, 116, 56, 44, 8))
    d.shape("pop", rrect(52, 28, 96, 18, 9))
    d.stroke("dark", "M76 28 V46 M124 28 V46", 2)
    d.marks("dark", ellipse(100, 37, 3, 9) if False else "M140 30 a9 9 0 0 1 0 14Z")
    d.shape("light", circle(84, 98, 9), shadow=False)
    d.shape("pop", "M75 98 A9 9 0 0 1 93 98Z", shadow=False)
    d.shape("light", rrect(104, 90, 22, 15, 2), shadow=False)
    d.shape("hero2", rrect(104, 95, 22, 5, 0), shadow=False)
    d.shape("light", _star(100, 138, 9), shadow=False)
    d.stroke("mark", "M76 124 H124", 1.4, line=False)


def gapyear_passport(d: Drawing):
    d.disc("glow", 100, 100, 58)
    d.shape("dark", "M30 64 L96 56 L104 56 L170 64 L172 150 L104 156 L96 156 L28 150Z")
    d.shape("light", "M34 62 L98 54 V150 L32 144Z")
    d.shape("light", "M102 54 L166 62 L168 144 L102 150Z")
    d.stroke("far", "M100 54 V150", 1.4, line=False)
    d.stroke("pop", circle(64, 82, 13), 2.6)
    d.stroke("pop", circle(64, 82, 8), 1.2)
    d.shape("pop", _star(64, 82, 5), shadow=False)
    d.stroke("hero", rrect(44, 108, 40, 24, 4), 2.6)
    d.stroke("hero", "M50 120 H78", 1.4)
    d.stroke("near", "M118 70 L150 74 L148 98 L116 94Z", 2.6)
    d.shape("near", "M124 84 L140 80 L146 82 L140 86 L124 88Z M132 82 L128 76 L132 76 L138 82Z", shadow=False)
    d.stroke("mark", circle(140, 122, 14), 2.6)
    d.stroke("mark", "M130 122 H150 M140 112 V132", 1.2)
    d.shape("hero", "M140 156 L150 156 L150 176 L145 171 L140 176Z", spot=True)


CONCEPTS = [
    Concept("beachparty-bonfire", "beach-party", "Beach bonfire", beachparty_bonfire, overrides=FLAME,
            checks=[("pop", "ground"), ("pop", "sky"), ("dark", "sky")], fixes={"sky": ["sky2", "far"]}),
    Concept("beachparty-boombox", "beach-party", "Boombox on the sand", beachparty_boombox,
            checks=[("hero", "ground"), ("hero", "far"), ("hero", "sky")], fixes={"hero": ["pop", "near", "deep"]}),
    Concept("beachparty-cocktail", "beach-party", "Sundowner cocktail", beachparty_cocktail,
            checks=[("pop", "glow"), ("pop", "far"), ("hero2", "pop")], fixes={"glow": ["near", "deep", "mid"], "hero2": ["glow2", "light"]}),
    Concept("festival-stage", "music-festival", "Main stage", festival_stage,
            checks=[("hero", "sky"), ("dark", "hero"), ("dark", "far")], fixes={"hero": ["pop", "near", "mid"]}),
    Concept("festival-tents", "music-festival", "Tents & flags", festival_tents,
            checks=[("hero", "mid"), ("light", "mid"), ("hero2", "mid"), ("pop", "sky")], fixes={"mid": ["near", "deep"]}),
    Concept("festival-guitar", "music-festival", "Guitar & bunting", festival_guitar,
            checks=[("hero", "glow"), ("hero2", "hero")], fixes={"glow": ["glow2", "far", "light"], "hero2": ["light", "glow2"]}),
    Concept("themepark-coaster", "theme-park", "Rollercoaster loop", themepark_coaster,
            checks=[("hero", "sky"), ("hero", "far"), ("pop", "hero")], fixes={"hero": ["deep", "mark", "near"]}),
    Concept("themepark-ferris", "theme-park", "Ferris wheel", themepark_ferris,
            checks=[("hero", "sky"), ("hero", "glow")], fixes={"hero": ["deep", "mark", "near"]}),
    Concept("themepark-carousel", "theme-park", "Carousel", themepark_carousel,
            checks=[("hero", "sky"), ("pop", "hero"), ("light", "hero")], fixes={"hero": ["deep", "near", "mark"]}),
    Concept("waterpark-tower", "water-park", "Slide tower", waterpark_tower, overrides=POOL,
            checks=[("hero", "sky"), ("hero", "far"), ("hero2", "far"), ("light", "mid")], fixes={"hero": ["pop", "deep", "near"]}),
    Concept("waterpark-ring", "water-park", "Rubber ring", waterpark_ring, overrides=POOL,
            checks=[("hero", "mid"), ("light", "mid"), ("mid", "ground"), ("pop", "light")], fixes={"hero": ["pop", "hero2", "deep"]}),
    Concept("waterpark-splash", "water-park", "Big splash", waterpark_splash, overrides=POOL,
            checks=[("hero", "sky"), ("hero", "far"), ("light", "mid"), ("dark", "light")], fixes={"hero": ["pop", "deep", "near"]}),
    Concept("aquarium-jelly", "aquarium", "Jellyfish tank", aquarium_jelly, UNDERWATER, {"hero": "#F49AC1", "hero2": "#FBD3E9"},
            checks=[("hero", "mid"), ("hero2", "mid"), ("dark", "mid")]),
    Concept("aquarium-tunnel", "aquarium", "Manta tunnel", aquarium_tunnel, UNDERWATER,
            checks=[("dark", "mid"), ("light", "mid"), ("dark", "ground")]),
    Concept("aquarium-clownfish", "aquarium", "Clownfish & anemone", aquarium_clownfish, UNDERWATER, CLOWNFISH,
            checks=[("hero", "mid"), ("hero", "far"), ("pop", "near"), ("hero", "pop")]),
    Concept("fireworks-harbour", "fireworks", "Harbour fireworks", fireworks_harbour,
            checks=[("pop", "deep"), ("glow2", "deep"), ("dark", "deep"), ("mid", "dark")], fixes={"dark": ["far", "mid", "near", "#343F63"], "mid": ["far", "near", "#6272A8"]}),
    Concept("fireworks-burst", "fireworks", "Big burst", fireworks_burst,
            checks=[("pop", "deep"), ("glow2", "deep"), ("far", "deep")], fixes={"far": ["light", "hero2"]}),
    Concept("fireworks-sparkler", "fireworks", "Sparkler heart", fireworks_sparkler,
            checks=[("glow2", "deep"), ("hero", "deep")], fixes={"hero": ["pop", "hero2"]}),
    Concept("yoga-deck", "yoga-retreat", "Jungle deck", yoga_deck, overrides=JUNGLE,
            checks=[("hero", "ground"), ("hero2", "ground"), ("near", "sky"), ("deep", "sky")], fixes={"hero": ["pop", "near", "deep"], "hero2": ["pop", "light", "glow"]}),
    Concept("yoga-pose", "yoga-retreat", "Lotus pose at sunrise", yoga_pose,
            checks=[("dark", "glow"), ("dark", "near"), ("dark", "sky")], fixes={"near": ["mid", "far"]}),
    Concept("yoga-lotus", "yoga-retreat", "Lotus flower", yoga_lotus, overrides=LOTUS,
            checks=[("hero", "mid"), ("hero2", "mid"), ("near", "mid")], fixes={"near": ["deep", "dark"]}),
    Concept("spa-stones", "spa-day", "Stones & frangipani", spa_stones, overrides=STONES,
            checks=[("hero", "glow"), ("hero2", "glow"), ("mark", "far"), ("light", "far")], fixes={"glow": ["far", "glow2", "light"]}),
    Concept("spa-bath", "spa-day", "Bubble bath", spa_bath,
            checks=[("light", "far"), ("light", "mid")]),
    Concept("spa-towels", "spa-day", "Rolled towels", spa_towels,
            checks=[("light", "glow"), ("hero", "glow"), ("hero", "light")], fixes={"glow": ["far", "mid"], "hero": ["pop", "near"]}),
    Concept("massage-stones", "massage", "Hot stones", massage_stones, overrides={"mark": "#8D99AE"},
            checks=[("dark", "far"), ("mark", "dark"), ("hero2", "far"), ("light", "far")], fixes={"far": ["mid", "near"]}),
    Concept("massage-oil", "massage", "Massage oil", massage_oil,
            checks=[("hero", "glow"), ("hero2", "glow"), ("dark", "glow")], fixes={"glow": ["far", "light", "glow2"]}),
    Concept("massage-cabana", "massage", "Beach cabana", massage_cabana,
            checks=[("light", "sky"), ("hero", "ground"), ("pop", "light")], fixes={"sky": ["sky2", "far"]}),
    Concept("honeymoon-bungalow", "honeymoon", "Overwater bungalow", honeymoon_bungalow,
            checks=[("light", "far"), ("light", "mid"), ("hero2", "glow"), ("hero2", "sky"), ("dark", "mid")], fixes={"hero2": ["near", "deep"], "far": ["mid", "near"]}),
    Concept("honeymoon-champagne", "honeymoon", "Two glasses", honeymoon_champagne, overrides={"hero2": "#F6CF5E"},
            checks=[("light", "glow"), ("hero2", "light")], fixes={"glow": ["near", "mid", "deep"]}),
    Concept("honeymoon-chairs", "honeymoon", "Two deckchairs", honeymoon_chairs,
            checks=[("hero", "far"), ("pop", "far"), ("hero", "ground"), ("pop", "sky")], fixes={"hero": ["deep", "near", "mark"]}),
    Concept("proposal-ringbox", "proposal", "Ring box at sunset", proposal_ringbox, overrides=RING,
            checks=[("pop", "far"), ("pop", "ground"), ("pop", "glow"), ("hero2", "dark")], fixes={"glow": ["glow2", "light", "far"]}),
    Concept("proposal-ring", "proposal", "Diamond ring", proposal_ring, overrides=RING,
            checks=[("hero2", "glow"), ("light", "glow"), ("hero2", "sky")], fixes={"glow": ["near", "mid", "deep", "hero"]}),
    Concept("proposal-kneel", "proposal", "Down on one knee", proposal_kneel,
            checks=[("dark", "glow"), ("dark", "near"), ("dark", "sky"), ("pop", "dark")], fixes={"near": ["mid", "far"], "sky": ["sky2", "far"]}),
    Concept("wedding-bells", "wedding", "Wedding bells", wedding_bells, overrides=RING,
            checks=[("hero2", "glow"), ("pop", "glow"), ("hero2", "sky")], fixes={"glow": ["near", "mid", "deep", "hero"]}),
    Concept("wedding-arch", "wedding", "Flower arch", wedding_arch,
            checks=[("light", "far"), ("light", "ground"), ("pop", "light"), ("light", "sky")], fixes={"sky": ["sky2", "far"], "far": ["mid", "near"]}),
    Concept("wedding-cake", "wedding", "Wedding cake", wedding_cake,
            checks=[("light", "glow"), ("hero2", "light"), ("pop", "light")], fixes={"glow": ["near", "mid", "deep"], "hero2": ["far", "glow2"]}),
    Concept("family-sandcastle", "family-holiday", "Sandcastle & bucket", family_sandcastle, overrides={"hero2": "#D9A35A", "mark": "#9A6A30"},
            checks=[("hero2", "ground"), ("hero2", "far"), ("hero", "ground"), ("pop", "ground")], fixes={"ground": ["#F7E3B5"], "hero": ["near", "deep"]}),
    Concept("family-car", "family-holiday", "Packed car", family_car,
            checks=[("hero", "far"), ("hero", "mid"), ("hero", "sky"), ("pop", "sky"), ("hero2", "sky")], fixes={"hero": ["pop", "deep", "near"], "hero2": ["near", "deep"]}),
    Concept("family-together", "family-holiday", "Family on the beach", family_together,
            checks=[("dark", "glow"), ("dark", "ground"), ("dark", "far"), ("dark", "sky")], fixes={"sky": ["sky2", "far"]}),
    Concept("solo-backpack", "solo-travel", "Backpack on a hill", solo_backpack,
            checks=[("hero", "near"), ("hero", "mid"), ("hero", "sky"), ("pop", "near")], fixes={"hero": ["pop", "deep", "dark"], "pop": ["hero2", "light"]}),
    Concept("solo-window", "solo-travel", "Window seat", solo_window,
            checks=[("light", "ground"), ("dark", "sky2"), ("dark", "far")], fixes={"ground": ["far", "mid"], "dark": ["hero", "mark"]}),
    Concept("solo-compass", "solo-travel", "Compass & map", solo_compass,
            checks=[("ground", "sky"), ("dark", "ground"), ("pop", "light")], fixes={"ground": ["far", "light", "glow2"]}),
    Concept("gapyear-globe", "gap-year", "Round the world", gapyear_globe, overrides={"hero": "#4A90C2", "near": "#8CC084"},
            checks=[("hero", "glow"), ("near", "hero"), ("pop", "glow")], fixes={"glow": ["far", "light", "sky2"], "near": ["ground", "hero2", "light"]}),
    Concept("gapyear-rucksack", "gap-year", "Big rucksack", gapyear_rucksack,
            checks=[("hero", "glow"), ("pop", "glow"), ("hero2", "hero")], fixes={"glow": ["far", "light", "sky2"], "hero2": ["light", "glow2"]}),
    Concept("gapyear-passport", "gap-year", "Passport stamps", gapyear_passport,
            checks=[("light", "glow"), ("dark", "glow")], fixes={"glow": ["near", "mid", "deep", "hero"]}),
]
