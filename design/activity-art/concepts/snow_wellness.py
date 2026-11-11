"""Snow & wellness: three concepts each for ice climbing, ice fishing, ice hotels, igloo stays, sledging,
meditation, thermal baths, onsen, hammam, sauna, sound baths, surf & yoga camps and digital detox."""
import math

from _common import Concept, Drawing, cloud, fish, circle, ellipse, waves, hills, rrect, group

ALL = ["golden", "coastal", "meadow", "blush", "dusk"]
NO_GOLD = ["coastal", "meadow", "blush", "dusk"]
UNDERWATER = ["coastal", "dusk", "meadow"]

# Snow is "light" (white). In the pale palettes the sky is nearly white too, so any concept where
# snow meets the sky checks ("light", "sky") and swaps in a winter-blue sky when they'd merge.
SNOW_SKY = "#AFD5EA"
ICE = "#A6D5EC"  # glacier ice (role "glow2" in ice concepts): reads against both white snow and the sky
NIGHT = {"hero": "#5EE6A8", "hero2": "#7FD8F0"}  # aurora greens
NIGHT_FIX = {"sky": ["deep", "mark", "#1F2A44"]}
NIGHT_PALETTES = ["dusk", "coastal", "blush", "meadow"]
WOOD = "#B5703F"
POOL = {"mid": "#5FBCC6", "near": "#2F8FA3"}


# ================================================================ private helpers
def _poly(pts, close=True):
    s = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    return s + ("Z" if close else "")


def _bar(x1, y1, x2, y2, w):
    """A straight rounded bar as a filled path."""
    dx, dy = x2 - x1, y2 - y1
    n = math.hypot(dx, dy) or 1
    nx, ny = -dy / n * w / 2, dx / n * w / 2
    r = w / 2
    return (f"M{x1+nx:.1f} {y1+ny:.1f} L{x2+nx:.1f} {y2+ny:.1f} A{r} {r} 0 0 0 {x2-nx:.1f} {y2-ny:.1f} "
            f"L{x1-nx:.1f} {y1-ny:.1f} A{r} {r} 0 0 0 {x1+nx:.1f} {y1+ny:.1f}Z")


def _line_only(d: Drawing, path: str, w: float = 2.4):
    """An extra line drawn only in line style, clipped to the circle like the bands."""
    if not d.paper:
        d.bands.append(f'<path d="{path}" fill="none" stroke="{d.c["ink"]}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')


def _pine(x, y, h, w=None):
    """A three-tier pine standing on (x, y)."""
    w = w or h * 0.55
    t = y - h
    return (f"M{x} {t} L{x + w*0.32:.1f} {t + h*0.34:.1f} L{x + w*0.2:.1f} {t + h*0.34:.1f} L{x + w*0.42:.1f} {t + h*0.64:.1f} "
            f"L{x + w*0.26:.1f} {t + h*0.64:.1f} L{x + w*0.5:.1f} {y - h*0.1:.1f} L{x + w*0.08:.1f} {y - h*0.1:.1f} L{x + w*0.08:.1f} {y} "
            f"L{x - w*0.08:.1f} {y} L{x - w*0.08:.1f} {y - h*0.1:.1f} L{x - w*0.5:.1f} {y - h*0.1:.1f} L{x - w*0.26:.1f} {t + h*0.64:.1f} "
            f"L{x - w*0.42:.1f} {t + h*0.64:.1f} L{x - w*0.2:.1f} {t + h*0.34:.1f} L{x - w*0.32:.1f} {t + h*0.34:.1f}Z")


def _pines(d: Drawing, role, trees, shadow=True, line=True):
    for x, y, h in trees:
        d.shape(role, _pine(x, y, h), shadow=shadow, line=line)


def _flakes(d: Drawing, pts, role="light"):
    for x, y, r in pts:
        d.stroke(role, f"M{x-r} {y} L{x+r} {y} M{x-r*0.5} {y-r*0.87} L{x+r*0.5} {y+r*0.87} M{x-r*0.5} {y+r*0.87} L{x+r*0.5} {y-r*0.87}", 1.6)


def _stars(d: Drawing, pts):
    for x, y, r in pts:
        d.marks("light", circle(x, y, r))


def _aurora(d: Drawing, y=0, s=1.0):
    """Aurora ribbons: soft paper curtains in papercut, two clipped spot-colour waves in line style."""
    def g():
        d.shape("hero", "M-30 70 C10 30 40 80 80 40 C110 12 140 50 170 20 L230 10 L230 30 C190 44 160 70 130 62 C100 54 80 100 40 90 C20 86 0 100 -30 110Z",
                shadow=False, line=False, extra='opacity=".9"')
        d.shape("hero2", "M-30 96 C10 70 40 108 80 74 C110 50 140 80 170 54 L230 44 L230 56 C190 70 160 92 130 86 C100 80 80 118 40 110 C20 106 0 116 -30 122Z",
                shadow=False, extra='opacity=".7"', line=False)
        d.shape("light", "M-30 70 C10 30 40 80 80 40 C110 12 140 50 170 20 L230 10 L230 16 C176 28 140 56 112 34 C92 22 80 66 40 70 C10 72 0 70 -30 84Z",
                shadow=False, line=False, extra='opacity=".25"')
    group(d, f"translate(0 {y}) scale(1 {s})", g)
    if not d.paper:
        for path, w in [("M-30 84 C10 46 40 90 80 54 C110 28 140 62 170 34 L230 22", 9), ("M-30 108 C10 82 40 118 80 88 C110 64 140 92 170 66 L230 54", 4)]:
            d.bands.append(f'<path transform="translate(0 {y})" d="{path}" fill="none" stroke="{d.c["spot"]}" stroke-width="{w}" stroke-linecap="round"/>')


def steam(d: Drawing, pts, h=26, role="light", w=3):
    for x, y in pts:
        d.stroke(role, f"M{x} {y} q-5 {-h/4} 0 {-h/2} q5 {-h/4} 0 {-h/2}", w)


def _star(x, y, r, k=0.42, n=5, rot=-90):
    pts = []
    for i in range(2 * n):
        a = math.radians(rot + i * 180 / n)
        rr = r if i % 2 == 0 else r * k
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return _poly(pts)


def _cover(d: Drawing, role, path):
    """Paint over earlier detail with a flat, unshadowed, unoutlined patch (paper colour in line style)."""
    fill = d.c[role] if d.paper else d.c["paper"]
    d.raw(f'<path d="{path}" fill="{fill}"/>', f'<path d="{path}" fill="{fill}"/>')


def _icicles(x0, x1, y, n, depth, seed=0):
    """A row of icicles hanging from y, between x0 and x1."""
    step = (x1 - x0) / n
    p = f"M{x0} {y - 30} H{x1} V{y}"
    for i in range(n, 0, -1):
        xa, xb = x0 + step * i, x0 + step * (i - 1)
        dep = depth * (0.55 + 0.45 * ((i * 7 + seed) % 5) / 4)
        p += f" L{(xa + xb) / 2:.1f} {y + dep:.1f} L{xb:.1f} {y}"
    return p + "Z"


def _palm(d: Drawing, x0, y0, x1, y1, s=1.0, role="dark", w=5):
    """A palm tree: trunk from the ground (x0, y0) bending to the crown (x1, y1)."""
    d.limb(role, f"M{x0} {y0} Q{x0 + (x1 - x0) * 0.1:.1f} {(y0 + y1) / 2:.1f} {x1} {y1}", w * s)

    def crown():
        for f in ["M0 0 C10 -13 30 -13 40 4 C30 -4 14 -4 0 0Z", "M0 0 C6 -16 22 -24 34 -18 C22 -16 10 -10 0 0Z",
                  "M0 0 C-10 -13 -30 -13 -40 4 C-30 -4 -14 -4 0 0Z", "M0 0 C-6 -16 -22 -24 -34 -18 C-22 -16 -10 -10 0 0Z",
                  "M0 0 C-3 -14 1 -24 7 -28 C6 -18 4 -8 0 0Z"]:
            d.shape(role, f, shadow=False)
    group(d, f"translate({x1} {y1}) scale({s})", crown)


def _dome_blocks(cx, base, rx, ry, rows, top_skip=1):
    """Igloo block joints on an elliptical dome: course lines plus staggered vertical joints."""
    p = ""
    ys = [base - ry * (i + 1) / (rows + 1) for i in range(rows)]
    prev = base
    for j, y in enumerate(ys):
        hw = rx * math.sqrt(max(0.0, 1 - ((base - y) / ry) ** 2))
        p += f"M{cx - hw:.1f} {y:.1f} L{cx + hw:.1f} {y:.1f} "
        hw_lo = rx * math.sqrt(max(0.0, 1 - ((base - prev) / ry) ** 2))
        n = max(2, int(hw_lo / 15))
        for k in range(n):
            x = cx - hw * 0.9 + (2 * hw * 0.9) * (k + (0.5 if j % 2 else 0.0)) / n
            if abs(x - cx) < hw * 0.95:
                p += f"M{x:.1f} {prev:.1f} L{x:.1f} {y:.1f} "
        prev = y
    return p


# ================================================================ ICE CLIMBING
def _climber(d: Drawing):
    """A climber from behind, arms up, axes in the ice. Spans roughly x 72-128, y 56-148."""
    d.limb("dark", "M96 118 L86 130 L88 146", 5.5)
    d.limb("dark", "M104 118 L114 128 L112 142", 5.5)
    d.shape("dark", "M82 144 L94 144 L93 150 L82 150Z M106 140 L118 140 L117 146 L106 146Z")
    d.limb("hero", "M93 101 L84 86 L82 74", 5)
    d.limb("hero", "M107 101 L115 88 L118 76", 5)
    d.shape("hero", rrect(90, 95, 20, 28, 7))
    d.shape("dark", rrect(93, 99, 14, 16, 4), shadow=False)
    d.shape("pop", rrect(90, 117, 20, 5, 2), shadow=False)
    d.shape("pop", circle(100, 88, 7.5))
    d.shape("dark", _bar(81, 76, 79, 58, 2.8))
    d.shape("dark", "M72 60 L86 56 L86 60 L74 63Z")
    d.shape("dark", _bar(119, 78, 121, 60, 2.8))
    d.shape("dark", "M114 58 L128 60 L126 64 L114 62Z")


def iceclimb_icefall(d: Drawing):
    d.disc("glow", 150, 46, 13)
    d.band("far", "M-30 90 L20 64 L54 80 L100 50 L150 76 L230 60")
    ice = "M56 44 Q100 34 146 40 L140 110 Q150 140 144 176 L56 176 Q50 140 62 110Z"
    d.shape("glow2", ice)
    d.stroke("light", "M74 50 Q68 90 76 126 Q80 150 72 172 M100 44 Q106 80 98 112 Q94 140 102 172 M126 46 Q132 86 124 120 Q120 150 128 172", 2.6, line=False)
    _line_only(d, "M74 50 Q68 90 76 126 Q80 150 72 172 M126 46 Q132 86 124 120 Q120 150 128 172", 1.6)
    d.shape("deep", "M-30 34 L36 40 L58 60 L66 104 L56 140 L60 200 L-30 200Z")
    d.shape("deep", "M230 26 L170 34 L146 60 L138 104 L148 140 L142 200 L230 200Z")
    d.shape("light", "M-30 30 L36 36 L58 56 L60 62 L40 48 L20 50 L-30 42Z", shadow=False)
    d.shape("light", "M230 22 L170 30 L146 56 L148 62 L168 44 L196 40 L230 38Z", shadow=False)
    d.stroke("pop", "M100 128 Q116 152 100 196", 2.2)
    group(d, "translate(100 102) scale(1.3) translate(-100 -100)", lambda: _climber(d))
    d.band("light", "M-30 172 Q60 162 120 170 T230 166")


def _axe(d: Drawing):
    d.limb("hero", "M0 66 Q8 8 0 -52", 8, spot=True)
    d.shape("dark", rrect(-6.5, 38, 13, 30, 5))
    d.shape("dark", "M-6 70 L6 70 L0 84Z")
    d.shape("dark", "M-5 -64 L15 -64 L15 -48 L5 -48 L5 -52 Q-20 -46 -46 -26 L-50 -29 Q-32 -54 -5 -58Z")
    d.marks("light", "M-14 -50 L-12 -46 L-10 -51Z M-24 -44 L-22 -40 L-20 -45Z M-34 -37 L-32 -33 L-30 -38Z")


def iceclimb_axes(d: Drawing):
    d.band("glow2", "M-30 -30 H230", shadow=False, line=False)
    d.stroke("light", "M30 10 Q20 60 34 110 Q44 140 30 180 M166 10 Q178 70 164 120 Q156 150 170 190 M64 20 Q58 50 66 70", 3, line=False)
    _line_only(d, "M30 10 Q20 60 34 110 Q44 140 30 180 M166 10 Q178 70 164 120 Q156 150 170 190", 1.6)
    d.disc("glow", 100, 104, 50)
    d.band("light", "M-30 164 Q100 150 230 164")
    group(d, "translate(100 112) rotate(30)", lambda: _axe(d))
    group(d, "translate(100 112) scale(-1 1) rotate(30)", lambda: _axe(d))
    _flakes(d, [(40, 76, 4), (164, 78, 4.5), (150, 160, 3)])


def iceclimb_crampon(d: Drawing):
    d.band("far", "M-30 120 L10 96 L40 110 L80 84 L120 112 L230 100")
    d.band("light", "M-30 156 Q60 146 120 154 T230 150")
    _pines(d, "deep", [(20, 160, 30), (36, 164, 22)])
    wall = "M150 -30 L230 -30 L230 230 L146 230 L150 170 L140 110 L152 50Z"
    d.shape("glow2", wall)
    d.stroke("light", "M172 -10 Q166 40 176 90 Q184 140 174 200 M200 -10 Q206 60 196 120 Q190 160 200 200", 3, line=False)
    _line_only(d, "M180 20 Q174 70 184 120 Q190 160 182 200", 1.6)

    def leg():
        d.shape("dark", "M56 -30 L104 -30 L100 74 L58 78Z")
        d.shape("pop", rrect(54, 66, 50, 16, 5))
        d.shape("hero", "M58 80 L102 76 L106 106 Q132 106 146 114 Q154 119 154 127 L154 133 L56 135 Q52 108 58 80Z")
        d.shape("hero2", "M100 84 L108 84 L110 130 L102 130Z", shadow=False, spot=True)
        for y in (88, 96, 104):
            d.marks("dark", rrect(84, y, 14, 3, 1.5))
        d.shape("dark", "M53 131 L157 129 L157 139 L53 141Z", shadow=False)
        d.shape("mark", "M58 140 L64 154 L70 140Z M84 140 L90 154 L96 140Z M110 139 L116 153 L122 139Z M134 138 L140 152 L146 138Z")
        d.shape("mark", "M150 128 L176 126 L152 134Z M150 136 L176 138 L152 140Z")
    group(d, "rotate(-6 100 100) translate(-6 0)", leg)
    d.stroke("dark", "M164 112 L176 104 M166 128 L182 130 M170 120 L186 116", 1.6)
    for x, y, r in [(176, 96, 3.4), (186, 108, 2.6), (190, 126, 3), (178, 140, 2.4)]:
        d.shape("light", f"M{x} {y - r} L{x + r} {y} L{x} {y + r} L{x - r} {y}Z", shadow=False)


# ================================================================ ICE FISHING
def icefish_hole(d: Drawing):
    d.band("far", hills(70, 8))
    _pines(d, "deep", [(x, 94, 14 + (x * 7) % 9) for x in range(-14, 220, 13)], shadow=False)
    d.band("light", "M-30 92 H230")
    d.band("glow2", "M-30 99 H230", shadow=False)
    d.band("mid", "M-30 114 H230")
    _cover(d, "mid", "M90 91 H110 V115 H90Z")
    d.stroke("glow2", "M90 99 V114 M110 99 V114", 1.4, line=False)
    _line_only(d, "M90 92 V114 M110 92 V114", 3)
    d.band("near", waves(162, 4, 40), line=False)
    d.shape("pop", _bar(46, 58, 64, 66, 7), spot=True)
    d.shape("dark", _bar(62, 65, 100, 78, 3.4))
    d.stroke("dark", "M100 78 L100 146", 1.2)
    d.shape("pop", "M96 146 L104 146 L102 156 L100 160 L98 156Z")
    d.shape("hero", fish(132, 150, 2.4))
    d.marks("mark", circle(118, 148, 1.8))
    d.stroke("hero2", "M128 140 L134 160 M138 140 L144 158", 1.6, line=False)
    d.shape("hero2", fish(52, 176, 1.3, right=True))
    for x, y, r in [(112, 136, 2), (118, 126, 1.6), (70, 160, 1.6)]:
        d.stroke("light", circle(x, y, r), 1.4)
    d.shape("hero", "M140 80 L148 92 H164 L170 80Z")
    d.shape("dark", ellipse(155, 80, 15, 3), shadow=False)


def _shack(d: Drawing, x, y, s, body, door="dark"):
    def g():
        d.shape("dark", rrect(6, -32, 5, 12, 1))
        d.stroke("light", "M8.5 -36 q-4 -5 0 -10 q4 -5 0 -10", 2.2, line=False)
        d.shape(body, rrect(-15, -22, 30, 22, 2))
        d.shape("dark", "M-19 -20 L0 -34 L19 -20 L17 -18 L0 -30 L-17 -18Z")
        d.shape("light", "M-20 -21 L0 -36 L20 -21 L16 -21 L0 -32 L-16 -21Z", shadow=False)
        d.shape(door, rrect(-10, -14, 8, 14, 1), shadow=False)
        d.shape("glow", rrect(3, -15, 7, 6, 1), shadow=False, spot=True)
    group(d, f"translate({x} {y}) scale({s})", g)


def icefish_shacks(d: Drawing):
    d.disc("glow", 150, 48, 13)
    d.band("far", hills(100, 10))
    _pines(d, "deep", [(x, 114, 12 + (x * 5) % 8) for x in range(-14, 220, 11)], shadow=False)
    d.band("light", "M-30 112 Q100 106 230 112")
    d.stroke("glow2", "M20 150 L60 146 M120 170 L170 166 M140 128 L180 126", 2, line=False)
    _shack(d, 104, 126, 0.75, "hero2")
    _shack(d, 150, 134, 0.95, "pop")
    _shack(d, 62, 156, 1.35, "hero")
    d.shape("dark", ellipse(130, 168, 9, 3))
    d.stroke("dark", "M130 168 L136 148", 1.8)
    d.shape("pop", "M136 148 L146 151 L136 155Z", shadow=False, spot=True)


def icefish_bucket(d: Drawing):
    d.band("mid", hills(98, 8))
    _pines(d, "deep", [(10, 122, 30), (26, 124, 22), (170, 120, 34), (186, 124, 24), (150, 124, 18)])
    d.band("light", "M-30 124 Q100 116 230 124")
    d.shape("near", ellipse(140, 152, 16, 5))
    d.shape("glow2", "M124 152 Q140 145 156 152 Q140 148 124 152Z", shadow=False, line=False)
    d.shape("mark", fish(146, 172, 1.6))
    d.marks("light", circle(136, 171, 1.2))
    d.shape("hero2", "M60 124 H86 L90 162 H56Z")
    d.stroke("dark", "M58 136 H88 M57 150 H89", 1.4, line=False)
    d.limb("dark", "M80 120 L102 122 L104 150", 9)
    d.shape("dark", rrect(98, 148, 18, 8, 3))
    d.shape("hero", "M62 84 Q62 74 74 74 Q88 74 88 86 L88 124 L62 124Z")
    d.limb("hero", "M80 90 L96 104 L106 104", 6.5)
    d.shape("dark", _bar(104, 106, 132, 92, 3))
    d.stroke("dark", "M132 92 L140 150", 1)
    d.shape("ground", circle(76, 64, 9))
    d.shape("pop", "M65 64 Q66 48 76 48 Q86 48 87 64Z")
    d.shape("pop", circle(76, 46, 3.6), shadow=False)
    d.limb("hero2", "M66 76 H84 M68 78 L60 92", 4.5, shadow=False)
    d.marks("dark", circle(81, 64, 1.3))
    _flakes(d, [(30, 50, 4), (150, 40, 5), (120, 72, 3.5), (44, 92, 3)], role="light")


# ================================================================ ICE HOTEL
def icehotel_facade(d: Drawing):
    _stars(d, [(30, 40, 1.4), (160, 26, 1.6), (176, 60, 1.2), (60, 20, 1.2), (122, 30, 1.2)])
    _aurora(d, -22)
    d.shape("light", "M22 112 Q26 68 100 62 Q174 68 178 112Z")
    d.shape("glow2", rrect(26, 96, 148, 58, 3))
    d.stroke("light", "M26 110 H174 M26 124 H174 M26 138 H174 M44 96 V110 M80 96 V110 M140 96 V110 M160 110 V124 M60 110 V124 "
                      "M40 124 V138 M154 124 V138 M52 138 V154 M150 138 V154", 1.6, line=False)
    _line_only(d, "M26 110 H66 M134 110 H174 M26 132 H66 M134 132 H174", 1.4)
    d.shape("light", "M72 156 V114 Q72 84 100 84 Q128 84 128 114 V156 H120 V116 Q120 94 100 94 Q80 94 80 116 V156Z")
    d.shape("glow", "M80 156 V116 Q80 94 100 94 Q120 94 120 116 V156Z", shadow=False, spot=True)
    d.stroke("glow2", "M100 96 V156", 1.6, line=False)
    for x in (48, 152):
        d.shape("light", rrect(x - 5, 102, 10, 54, 3))
        d.shape("light", rrect(x - 8, 98, 16, 6, 2))
    d.band("light", "M-30 154 Q100 146 230 154")


def icehotel_bed(d: Drawing):
    d.band("light", "M-30 -30 H230", shadow=False, line=False)
    niche = "M22 166 V86 Q22 34 100 34 Q178 34 178 86 V166Z"
    d.shape("glow2", niche)
    d.stroke("light", "M22 86 H178 M22 112 H178 M32 60 H168 M60 40 H140 M100 34 V60 M60 60 V86 M140 60 V86 M100 86 V112", 1.8, line=False)
    _flakes(d, [(100, 74, 0)])
    d.stroke("light", "M100 62 V86 M90 68 L110 80 M90 80 L110 68", 2.4, line=False)
    d.shape("glow2", rrect(26, 128, 148, 34, 4))
    d.stroke("light", "M26 140 H174 M74 128 V140 M126 128 V140 M50 140 V162 M100 140 V162 M150 140 V162", 1.6, line=False)
    d.shape("ground", "M24 132 C30 120 40 126 50 118 C60 124 70 116 80 120 L150 116 C160 122 170 118 178 128 L176 136 C170 140 160 136 150 140 L40 142 C32 140 26 138 24 132Z")
    d.shape("hero", "M60 104 Q60 96 70 96 H164 Q172 96 172 106 Q172 120 160 122 H70 Q60 122 60 112Z")
    d.stroke("hero2", "M92 98 V120 M124 98 V120", 1.6, line=False)
    d.shape("light", "M34 104 Q30 94 42 92 L62 94 Q68 104 62 114 L42 116 Q32 114 34 104Z")
    d.band("far", "M-30 166 H230")
    d.shape("glow2", rrect(176, 140, 14, 18, 2))
    d.shape("pop", "M183 140 C179 134 182 130 183 126 C185 130 188 134 183 140Z", shadow=False, spot=True)


def icehotel_glass(d: Drawing):
    d.disc("glow", 100, 98, 66, line=False)
    _flakes(d, [(40, 60, 5), (162, 54, 5.5), (168, 98, 4), (32, 106, 4)])
    d.shape("glow2", rrect(-30, 150, 260, 60, 3))
    d.shape("light", rrect(-30, 150, 260, 6, 2), shadow=False)
    d.stroke("light", "M30 166 L60 176 M120 170 L160 164", 2, line=False)
    d.shape("near", _bar(122, 74, 140, 30, 5), spot=True)
    d.shape("glow2", "M60 58 H140 L134 152 H66Z")
    d.shape("pop", "M72 74 H128 L124 140 H76Z", shadow=False, spot=True)
    d.shape("hero2", "M72 74 H128 L127 88 H73Z", shadow=False)
    d.shape("light", rrect(80, 92, 16, 14, 3), shadow=False, extra='transform="rotate(-12 88 99)"')
    d.shape("light", rrect(100, 106, 16, 14, 3), shadow=False, extra='transform="rotate(10 108 113)"')
    d.shape("light", "M60 58 H68 L74 152 H66Z M132 58 H140 L134 152 H128Z", shadow=False, line=False, extra='opacity=".6"')
    d.shape("near", "M126 66 A12 12 0 0 1 150 66Z")
    d.shape("light", "M129 66 A9 9 0 0 1 147 66Z", shadow=False)
    d.stroke("light", "M64 64 L66 100", 3)


# ================================================================ IGLOO STAY
def igloo_day(d: Drawing):
    d.disc("glow", 152, 50, 14)
    d.band("mid", "M-30 128 L10 116 L40 124 L80 112 L120 124 L160 110 L200 122 L230 116")
    d.band("light", "M-30 140 Q100 132 230 140")
    dome = "M34 144 A66 80 0 0 1 166 144Z"
    d.shape("light", dome)
    d.stroke("glow2", _dome_blocks(100, 144, 66, 80, 4), 2, line=False)
    _line_only(d, _dome_blocks(100, 144, 66, 80, 4), 1.4)
    d.shape("light", "M76 150 V124 Q76 102 100 102 Q124 102 124 124 V150Z")
    d.stroke("glow2", "M76 130 H124 M88 130 V150 M112 130 V150 M100 102 V114 M82 112 L90 118 M118 112 L110 118", 2, line=False)
    d.shape("dark", "M88 150 V130 Q88 116 100 116 Q112 116 112 130 V150Z", shadow=False)
    d.band("light", "M-30 152 Q100 144 230 152")
    d.stroke("glow2", "M40 168 Q80 162 110 172 M130 164 Q160 158 186 164", 2, line=False)


def igloo_glass(d: Drawing):
    _stars(d, [(40, 30, 1.4), (150, 26, 1.6), (172, 60, 1.2), (24, 64, 1.2), (110, 18, 1.2)])
    _aurora(d, -6)
    d.band("far", "M-30 124 L20 106 L60 118 L110 98 L150 114 L190 102 L230 112")
    _pines(d, "dark", [(14, 138, 34), (30, 140, 24), (178, 136, 36), (194, 140, 26)])
    d.band("light", "M-30 136 Q100 128 230 136")

    def dome(cx, base, r, bed=True):
        d.shape("mark", f"M{cx - r} {base} A{r} {r} 0 0 1 {cx + r} {base}Z")
        d.shape("glow", f"M{cx - r * .8:.1f} {base} Q{cx} {base - r * .55:.1f} {cx + r * .8:.1f} {base}Z", shadow=False, spot=True)
        lat = f"M{cx} {base - r} V{base} M{cx} {base - r} A{r * .5:.1f} {r} 0 0 0 {cx - r * .5:.1f} {base} M{cx} {base - r} A{r * .5:.1f} {r} 0 0 1 {cx + r * .5:.1f} {base} "
        for k in (0.35, 0.7):
            y = base - r * k
            hw = r * math.sqrt(1 - k * k)
            lat += f"M{cx - hw:.1f} {y:.1f} L{cx + hw:.1f} {y:.1f} "
        d.stroke("light", lat, 1.4 if r > 30 else 1.1, line=r > 30)
        if bed:
            d.shape("pop", rrect(cx - r * .38, base - r * .2, r * .76, r * .2, 2), shadow=False)
    dome(44, 140, 20, False)
    dome(162, 142, 22, False)
    dome(100, 160, 46)
    d.band("light", "M-30 158 Q100 152 230 158")


def igloo_entrance(d: Drawing):
    d.disc("glow2", 46, 44, 13)
    _stars(d, [(80, 24, 1.4), (150, 30, 1.6), (176, 56, 1.2), (24, 76, 1.2), (124, 16, 1.2)])
    dome = "M-6 206 A106 150 0 0 1 206 206Z"
    d.shape("light", dome)
    d.stroke("sky2", _dome_blocks(100, 206, 106, 150, 6), 2, line=False)
    _line_only(d, "M18 120 Q100 90 182 120 M8 160 Q100 132 192 160", 1.6)
    d.shape("light", "M50 190 V140 Q50 92 100 92 Q150 92 150 140 V190Z")
    d.stroke("sky2", "M50 140 H150 M50 166 H150 M76 140 V166 M124 140 V166 M100 166 V190 M62 166 V190 M138 166 V190 M100 92 V112 M64 108 L76 118 M136 108 L124 118", 2, line=False)
    d.shape("dark", "M68 190 V146 Q68 112 100 112 Q132 112 132 146 V190Z", shadow=False)
    d.shape("glow", "M74 190 V148 Q74 120 100 120 Q126 120 126 148 V190Z", shadow=False, spot=True)
    d.shape("ground", "M80 190 L84 168 H116 L120 190Z", shadow=False)
    d.band("light", "M-30 184 Q100 178 230 184")
    for x in (36, 52):
        d.shape("hero", f"M{x} 160 H{x + 10} V178 Q{x + 18} 178 {x + 20} 184 V188 H{x} Z")
        d.shape("hero2", rrect(x - 1, 156, 12, 6, 2), shadow=False)
    d.shape("dark", rrect(152, 166, 22, 6, 2))
    d.shape("pop", rrect(154, 146, 18, 20, 3))
    d.shape("glow", rrect(158, 150, 10, 12, 2), shadow=False)
    d.limb("dark", "M156 146 Q163 136 170 146", 2.2, shadow=False)


# ================================================================ SLEDGING
def _sledge(d: Drawing, runner="hero", seat="ground"):
    """A wooden sledge side-on, front to the right. Runner bottom at y 0, from x -60 to 60."""
    d.limb("deep", "M-52 -8 H40 Q60 -8 60 -26 Q60 -38 50 -38", 4.5, shadow=False)
    for x in (-40, 0, 36):
        d.limb(runner, f"M{x} 0 V-20", 4.5)
    d.shape(seat, rrect(-60, -26, 104, 9, 3))
    d.stroke("deep", "M-34 -24 V-19 M-8 -24 V-19 M18 -24 V-19", 1.4, line=False)
    d.limb(runner, "M-60 0 H44 Q66 0 66 -22 Q66 -38 52 -38", 5, spot=True)


def sledging_wooden(d: Drawing):
    d.disc("glow", 52, 52, 15)
    d.band("mid", "M-30 112 Q40 92 100 106 T230 98")
    _pines(d, "deep", [(140, 120, 40), (158, 122, 30), (176, 120, 44), (194, 124, 28), (20, 124, 26)])
    d.band("light", "M-30 124 Q100 114 230 126")
    group(d, "translate(96 152) rotate(-5) scale(1.25)", lambda: (
        _sledge(d),
        d.limb("pop", "M58 -34 Q62 -12 40 -2 Q24 4 18 -8", 2.4, shadow=False)))
    d.limb("pop", "M60 128 Q74 122 88 130", 7, spot=True)
    d.stroke("light", "M66 126 V132 M74 124 V130 M82 126 V132", 2, line=False)
    d.band("light", "M-30 168 Q100 158 230 170", line=False)
    _flakes(d, [(150, 52, 4.5), (110, 36, 3.5), (178, 78, 3.5)])


def sledging_hill(d: Drawing):
    d.disc("glow", 152, 44, 13)
    d.band("mid", "M-30 80 Q60 70 120 86 T230 92")
    _pines(d, "deep", [(150, 104, 34), (166, 106, 26), (184, 102, 40), (200, 106, 28)])
    d.band("light", "M-30 70 Q50 74 110 104 T230 150")
    d.stroke("glow2", "M-20 82 Q30 86 76 108 M-20 90 Q30 94 72 114", 1.8, line=False)
    _line_only(d, "M-20 86 Q30 90 74 110", 1.4)

    def kid():
        d.limb("light", "M-60 -4 Q-48 -16 -40 -6 M-66 4 Q-56 -6 -46 2", 3, shadow=False)
        _sledge(d)
        d.limb("dark", "M-12 -32 L22 -32 L30 -26", 10)
        d.shape("dark", rrect(26, -34, 12, 12, 4))
        d.limb("hero2", "M-20 -60 Q-40 -64 -54 -52", 5.5, spot=True)
        d.shape("pop", rrect(-30, -70, 26, 40, 11))
        d.limb("pop", "M-12 -58 L12 -40 L40 -34", 7)
        d.shape("hero2", rrect(-30, -64, 24, 6, 3), shadow=False)
        d.shape("ground", circle(-16, -80, 11))
        d.shape("hero", "M-28 -80 Q-28 -96 -16 -96 Q-4 -96 -4 -80Z")
        d.shape("light", circle(-16, -97, 4.2), shadow=False)
        d.marks("dark", circle(-9, -80, 1.6))
    group(d, "translate(108 128) rotate(24) scale(.92)", kid)
    d.band("light", "M-30 176 Q100 168 230 180", line=False)


REINDEER = ("M60 120 C60 108 72 102 92 102 L116 102 C124 102 128 96 130 88 L134 74 C136 68 144 66 148 70 L160 80 "
            "Q164 86 158 89 L148 90 C146 100 144 112 136 120 C134 128 126 132 118 132 L76 132 C66 132 60 128 60 120Z")


def sledging_reindeer(d: Drawing):
    d.disc("glow", 46, 54, 13)
    d.band("mid", "M-30 120 Q40 104 100 114 T230 108")
    _pines(d, "deep", [(150, 124, 30), (166, 126, 22), (186, 124, 36), (24, 126, 22)])
    d.band("light", "M-30 132 Q100 124 230 134")

    def deer():
        d.limb("ground", "M140 72 L132 54 L122 42 M132 54 L140 40 M134 62 L124 60", 3.4)
        d.limb("ground", "M146 72 L152 52 L148 38 M152 52 L162 44 M150 60 L160 60", 3.4)
        for x1, x2 in [(70, 66), (82, 86), (118, 114), (128, 132)]:
            d.shape("ground", _bar(x1, 126, x2, 160, 6))
        d.shape("ground", REINDEER)
        d.shape("light", "M124 104 C128 112 136 114 142 106 L140 94 Q134 104 124 104Z", shadow=False)
        d.shape("light", "M58 116 Q54 108 62 108Z", shadow=False)
        d.shape("pop", "M120 98 L128 94 L136 112 L128 116Z", shadow=False, spot=True)
        d.marks("mark", circle(150, 79, 1.8))
        d.marks("mark", circle(161, 85, 2))
    group(d, "translate(44 26) scale(.8)", deer)
    d.stroke("dark", "M78 146 L146 112 M64 116 Q110 90 162 92", 1.4)
    d.shape("hero", "M8 146 Q12 158 28 158 H78 Q84 156 84 146 L78 136 H14Z")
    d.stroke("hero2", "M14 146 H80", 2, line=False)
    d.shape("dark", rrect(30, 108, 22, 32, 9))
    d.limb("dark", "M48 118 L64 116", 5)
    d.shape("ground", circle(41, 100, 8))
    d.shape("pop", "M32 100 Q32 86 41 86 Q50 86 50 100Z")
    d.shape("hero2", rrect(31, 96, 20, 4, 2), shadow=False)
    d.band("light", "M-30 166 Q100 158 230 168")


# ================================================================ MEDITATION
def meditate_garden(d: Drawing):
    d.band("ground", "M-30 -30 H230", shadow=False, line=False)
    rocks = [(76, 88, 18, [28, 38, 48]), (146, 140, 11, [19, 27])]
    lines = " ".join(f"M-30 {y} H230" for y in range(10, 200, 9))
    d.stroke("far", lines, 1.6, line=False)
    _line_only(d, " ".join(f"M-30 {y} H230" for y in range(10, 200, 18)), 1.2)
    for x, y, r, rings in rocks:
        _cover(d, "ground", circle(x, y, rings[-1] + 4))
        d.stroke("far", " ".join(circle(x, y, rr) for rr in rings), 1.8)
    d.shape("near", "M52 98 C50 82 64 74 78 76 C96 74 102 92 96 102 C90 110 60 112 52 98Z")
    d.shape("mid", "M60 92 C58 76 70 68 80 70 C92 68 98 80 94 92 C90 100 66 102 60 92Z", spot=True)
    d.shape("light", "M68 76 C72 72 80 72 84 74 C78 76 72 78 68 76Z", shadow=False, line=False)
    d.shape("mid", "M138 142 C134 132 142 126 150 128 C158 128 160 138 156 144 C150 148 140 148 138 142Z", spot=True)
    d.shape("near", "M140 146 C146 150 154 148 158 143 L160 147 C152 154 142 152 138 146Z", shadow=False, line=False)
    d.shape("pop", "M150 54 L154 46 L156 52 L162 48 L160 56 L166 58 L158 62 L160 68 L152 64 L146 68 L148 60 L142 56Z")
    d.stroke("dark", "M152 62 L144 70", 1.2)
    d.band("deep", "M-30 176 H230")
    d.stroke("dark", "M-30 182 H230", 1, line=False)


def meditate_incense(d: Drawing):
    d.disc("glow", 100, 96, 68, line=False)
    d.band("near", "M-30 156 Q100 150 230 156")
    for x0, x1, top in [(94, 82, 86), (100, 100, 80), (106, 118, 86)]:
        d.shape("dark", _bar(x0, 138, x1, top, 2.6))
    for x, y in [(82, 86), (100, 80), (118, 86)]:
        d.shape("pop", circle(x, y, 2.6), shadow=False, spot=True)
    d.stroke("light", "M100 76 C92 66 108 58 100 48 C92 38 106 30 100 22", 3)
    d.stroke("light", "M81 82 C72 74 80 64 74 56 C68 48 76 42 72 36", 2.4)
    d.stroke("light", "M119 82 C128 74 120 64 128 56 C134 48 126 42 130 36", 2.4)
    for a in (-60, -30, 0, 30, 60):
        d.shape("hero2", "M0 0 C-9 -6 -9 -20 0 -26 C9 -20 9 -6 0 0Z", extra=f'transform="translate(100 150) rotate({a})"', shadow=a == 0)
    d.shape("hero", "M70 140 H130 Q128 160 100 160 Q72 160 70 140Z")
    d.shape("ground", ellipse(100, 140, 30, 5), shadow=False)


def _bodhi(x, y, s, rot):
    return (f"M0 0 C-11 6 -13 22 -3 30 L0 40 L3 30 C13 22 11 6 0 0Z", f"translate({x} {y}) rotate({rot}) scale({s})")


def meditate_buddha(d: Drawing):
    d.disc("glow", 100, 70, 38)
    d.band("far", "M-30 150 Q100 140 230 150")
    d.limb("deep", "M-30 20 Q40 30 80 12 M230 26 Q170 34 128 14", 4, shadow=False)
    for x, y, s, r in [(14, 26, 1, 10), (40, 30, .9, -10), (64, 22, .8, 20), (152, 26, .85, -18), (178, 32, 1, 8), (198, 26, .8, -6)]:
        p, t = _bodhi(x, y, s, r)
        d.shape("near", p, extra=f'transform="{t}"')
    d.shape("hero", "M100 82 C82 84 72 92 70 108 L66 136 Q62 148 42 150 Q36 166 56 170 H144 Q164 166 158 150 Q138 148 134 136 L130 108 C128 92 118 84 100 82Z")
    d.shape("hero", "M84 66 C82 52 90 44 100 44 C110 44 118 52 116 66 C116 78 110 86 100 86 C90 86 84 78 84 66Z")
    d.shape("hero", circle(100, 42, 7))
    d.shape("hero", ellipse(83, 70, 3.5, 10), shadow=False)
    d.shape("hero", ellipse(117, 70, 3.5, 10), shadow=False)
    d.stroke("mark", "M90 66 Q94 69 98 66 M102 66 Q106 69 110 66 M96 77 Q100 79 104 77", 1.4)
    d.stroke("mark", "M86 92 Q100 120 128 132 M70 152 Q100 160 130 152", 1.4, line=False)
    d.shape("hero2", ellipse(100, 140, 17, 7), shadow=False, spot=True)
    d.shape("pop", "M38 170 H162 L154 186 H46Z")
    for x in range(48, 160, 16):
        d.shape("hero2", f"M{x} 172 Q{x + 8} 162 {x + 16} 172Z", shadow=False)


# ================================================================ THERMAL BATHS
def thermal_palace(d: Drawing):
    d.disc("glow", 40, 50, 12)
    d.shape("light", cloud(140, 44, 0.8), shadow=False)
    d.shape("mark", "M80 62 Q80 34 100 30 Q120 34 120 62Z")
    d.shape("light", rrect(97, 22, 6, 10, 2))
    d.shape("hero2", rrect(16, 78, 168, 44, 2))
    d.shape("hero2", rrect(72, 58, 56, 64, 2))
    d.shape("light", rrect(70, 56, 60, 5, 2), shadow=False)
    d.shape("light", rrect(14, 76, 172, 5, 2), shadow=False)
    for x in (24, 40, 56, 136, 152, 168):
        d.shape("dark", f"M{x - 4} 110 V94 Q{x - 4} 88 {x} 88 Q{x + 4} 88 {x + 4} 94 V110Z", shadow=False)
    for x in (84, 100, 116):
        d.shape("dark", f"M{x - 5} 112 V78 Q{x - 5} 70 {x} 70 Q{x + 5} 70 {x + 5} 78 V112Z", shadow=False)
    d.shape("light", rrect(-30, 120, 260, 6, 2))
    d.band("mid", waves(128, 2.5, 24))
    d.stroke("light", "M30 146 Q40 142 50 146 M140 150 Q150 146 160 150", 2, line=False)
    for x, y in [(70, 140), (128, 146)]:
        d.shape("dark", circle(x, y, 5.5))
        d.stroke("light", f"M{x - 10} {y + 5} Q{x} {y + 1} {x + 10} {y + 5}", 1.6, line=False)
    steam(d, [(40, 132), (100, 128), (160, 132)], 26)
    d.band("near", waves(170, 3, 30), line=False)


def _statue(x, y, s=1.0):
    return (f"M{x - 3*s} {y} L{x - 2.5*s} {y - 10*s} L{x - 5*s} {y - 9*s} L{x - 3*s} {y - 16*s} A{3.4*s} {3.4*s} 0 1 1 {x + 3*s} {y - 16*s} "
            f"L{x + 5*s} {y - 10*s} L{x + 2.5*s} {y - 10*s} L{x + 3*s} {y}Z")


def thermal_roman(d: Drawing):
    d.disc("glow", 160, 40, 11)
    d.shape("ground", rrect(-30, 60, 260, 10, 1))
    d.shape("ground", rrect(-30, 46, 260, 8, 1))
    for x in range(-14, 220, 12):
        d.shape("ground", rrect(x, 52, 4, 9, 1), shadow=False)
    for x in (40, 100, 160):
        d.shape("dark", _statue(x, 46, 1.4))
    d.shape("far", rrect(-30, 70, 260, 52, 0), shadow=False, line=False)
    for x in (12, 44, 76, 108, 140, 172):
        d.shape("ground", rrect(x, 68, 12, 54, 2))
        d.shape("ground", rrect(x - 3, 66, 18, 5, 1.5), shadow=False)
        d.stroke("far", f"M{x + 4} 74 V118 M{x + 8} 74 V118", 1, line=False)
    d.shape("ground", rrect(-30, 120, 260, 8, 1))
    d.band("mid", "M-30 130 H230")
    for x in (18, 50, 82, 114, 146, 178):
        d.stroke("near", f"M{x} 136 V150 M{x - 2} 156 V164", 3, line=False)
    _line_only(d, "M10 150 Q30 146 50 150 M120 160 Q140 156 160 160", 1.6)
    steam(d, [(30, 128), (90, 126), (150, 128)], 30)
    d.band("ground", "M-30 176 H230")


def _knight(d: Drawing, x, y, s, role):
    d.shape(role, "M-14 0 H14 L12 -7 H9 C10 -20 16 -30 14 -40 C12 -52 2 -58 -4 -58 L-7 -66 L-11 -56 C-17 -52 -22 -44 -24 -36 "
                  "L-21 -31 L-11 -35 C-6 -35 -4 -33 -6 -28 C-10 -22 -12 -14 -9 -7 H-12Z",
            extra=f'transform="translate({x} {y}) scale({s})"')


def _king(d: Drawing, x, y, s, role):
    d.shape(role, "M-13 0 H13 L10 -8 H7 L5 -32 H9 V-37 H5 C9 -40 9 -48 2 -50 V-54 H6 V-58 H2 V-62 H-2 V-58 H-6 V-54 H-2 V-50 "
                  "C-9 -48 -9 -40 -5 -37 H-9 V-32 H-5 L-7 -8 H-10Z",
            extra=f'transform="translate({x} {y}) scale({s})"')


def thermal_chess(d: Drawing):
    d.band("far", "M-30 72 H230", line=False)
    d.shape("hero2", rrect(-30, 40, 260, 32, 0))
    for x in range(-10, 220, 22):
        d.shape("dark", f"M{x} 72 V56 Q{x} 48 {x + 7} 48 Q{x + 14} 48 {x + 14} 56 V72Z", shadow=False)
    d.shape("light", rrect(-30, 70, 260, 6, 2))
    d.band("mid", waves(78, 2.5, 24))
    steam(d, [(30, 100), (170, 96), (150, 176)], 26)

    def board():
        d.shape("ground", rrect(-40, -40, 80, 80, 4))
        sq = ""
        for i in range(4):
            for j in range(4):
                if (i + j) % 2 == 0:
                    sq += f"M{-36 + i * 18} {-36 + j * 18} h18 v18 h-18Z "
        d.shape("dark", sq, shadow=False)
    group(d, "translate(100 138) scale(1 .5) rotate(45)", board)
    d.stroke("light", "M30 150 Q44 146 58 150 M142 154 Q154 150 168 154 M60 176 Q100 184 140 176", 2.2, line=False)
    _line_only(d, "M30 150 Q44 146 58 150 M142 154 Q154 150 168 154", 1.6)
    _king(d, 82, 140, 1.15, "dark")
    _knight(d, 124, 144, 1.0, "light")
    d.stroke("dark", "M114 120 Q117 118 120 120", 1.2, line=False)
    d.marks("dark", circle(113, 102, 1.6))


# ================================================================ ONSEN
def onsen_rotenburo(d: Drawing):
    d.disc("glow", 150, 40, 12)
    d.band("far", "M-30 104 Q40 86 100 98 T230 92")
    _pines(d, "deep", [(120, 110, 30), (140, 112, 24), (102, 112, 20)])
    d.band("light", "M-30 110 Q100 102 230 112")
    d.limb("dark", "M50 40 V118", 6)
    d.shape("dark", "M-30 24 L92 40 L98 50 L-30 38Z")
    d.shape("light", "M-30 18 L90 34 L94 40 L-30 26Z", shadow=False)
    d.stroke("ground", "M-20 34 L80 46", 1.2, line=False)
    d.shape("hero", ellipse(100, 150, 80, 24), spot=True)
    d.stroke("light", "M60 148 Q70 144 80 148 M120 156 Q132 152 144 156", 2, line=False)
    for x, y, rx, ry in [(26, 136, 16, 9), (50, 128, 14, 7), (152, 128, 14, 7), (176, 140, 16, 9), (34, 170, 18, 9), (166, 172, 18, 8), (100, 180, 22, 7)]:
        d.shape("mid", ellipse(x, y, rx, ry))
        d.shape("light", f"M{x - rx * .7:.1f} {y - ry * .5:.1f} Q{x} {y - ry * 1.3:.1f} {x + rx * .7:.1f} {y - ry * .5:.1f} Q{x} {y - ry * .9:.1f} {x - rx * .7:.1f} {y - ry * .5:.1f}Z", shadow=False)

    def lantern():
        d.shape("mid", rrect(-10, 0, 20, 5, 1))
        d.shape("mid", rrect(-4, -24, 8, 24, 1))
        d.shape("mid", rrect(-9, -28, 18, 5, 1))
        d.shape("mid", rrect(-7, -42, 14, 14, 1))
        d.shape("glow", rrect(-4, -39, 8, 8, 1), shadow=False, spot=True)
        d.shape("mid", "M-16 -42 Q0 -50 16 -42 L10 -50 Q0 -56 -10 -50Z")
        d.shape("light", "M-15 -45 Q0 -54 15 -45 L10 -50 Q0 -56 -10 -50Z", shadow=False)
        d.shape("mid", circle(0, -57, 3))
    group(d, "translate(170 124) scale(1.15)", lantern)
    steam(d, [(76, 136), (100, 130), (124, 136)], 30)


def onsen_noren(d: Drawing):
    d.band("ground", "M-30 30 H230", shadow=False)
    d.stroke("near", "M-30 60 H230 M-30 100 H230 M-30 140 H230", 1, line=False)
    d.shape("dark", rrect(40, 56, 120, 130, 2))
    d.shape("dark", "M-30 14 Q100 26 230 14 L230 40 L-30 40Z")
    d.stroke("mark", "M-30 22 Q100 34 230 22", 1.2, line=False)
    d.shape("deep", rrect(-30, 38, 260, 8, 1))
    d.shape("deep", rrect(30, 50, 140, 8, 2))
    d.limb("dark", "M36 66 H164", 4, shadow=False)
    for x in (44, 82, 120):
        d.shape("hero", rrect(x, 66, 36, 70, 2))
    d.shape("hero", rrect(44, 66, 112, 10, 2), shadow=False, line=False)
    sym = ("M84 104 Q84 124 100 124 Q116 124 116 104 "
           "M92 110 q-4 -6 0 -12 q4 -6 0 -12 M100 112 q-4 -7 0 -14 q4 -7 0 -14 M108 110 q-4 -6 0 -12 q4 -6 0 -12")
    d.stroke("light", sym, 3.4)
    if not d.paper:
        d.parts.append(f'<path d="{sym}" fill="none" stroke="{d.c["spot"]}" stroke-width="2" stroke-linecap="round"/>')
    d.shape("near", rrect(30, 182, 140, 8, 2))
    d.limb("dark", "M178 52 V66", 1.6, shadow=False)
    d.shape("pop", "M170 70 Q178 64 186 70 L188 96 Q178 102 168 96Z", spot=True)
    d.shape("dark", rrect(172, 66, 12, 4, 1.5), shadow=False)
    d.shape("dark", rrect(172, 97, 12, 4, 1.5), shadow=False)
    d.stroke("deep", "M169 78 H187 M169 88 H187", 1, line=False)
    steam(d, [(54, 172), (146, 172)], 28)


def onsen_soaker(d: Drawing):
    d.band("far", "M-30 96 Q40 82 100 92 T230 88")
    _pines(d, "deep", [(20, 104, 34), (38, 106, 24), (164, 102, 36), (182, 106, 26)])
    d.band("light", "M-30 104 Q100 96 230 106")
    for x, y, rx, ry in [(20, 120, 22, 10), (180, 118, 24, 10)]:
        d.shape("mid", ellipse(x, y, rx, ry))
        d.shape("light", f"M{x - rx * .7:.1f} {y - ry * .5:.1f} Q{x} {y - ry * 1.3:.1f} {x + rx * .7:.1f} {y - ry * .5:.1f} Q{x} {y - ry * .9:.1f} {x - rx * .7:.1f} {y - ry * .5:.1f}Z", shadow=False)
    d.band("near", "M-30 122 Q100 118 230 122")
    d.shape("hero2", "M68 108 C68 84 82 72 100 72 C118 72 132 84 132 108 C132 126 118 138 100 138 C82 138 68 126 68 108Z")
    d.shape("dark", "M68 104 C66 82 82 70 100 70 C118 70 134 82 132 104 C126 92 114 88 100 88 C86 88 74 92 68 104Z", shadow=False)
    d.shape("light", "M74 70 Q100 62 126 70 L124 82 Q100 76 76 82Z")
    d.stroke("pop", "M80 74 Q100 69 120 74", 2, line=False)
    d.stroke("mark", "M84 106 Q89 110 94 106 M106 106 Q111 110 116 106 M95 120 Q100 123 105 120", 2)
    d.marks("pop", ellipse(82, 116, 4, 2.4) + " " + ellipse(118, 116, 4, 2.4))
    d.band("near", "M-30 128 Q100 124 230 128", line=False)
    _line_only(d, "M-30 128 Q100 124 230 128", 2.4)
    d.stroke("light", "M68 130 Q100 140 132 130 M30 150 Q40 146 50 150 M150 156 Q160 152 170 156", 2, line=False)
    for x, y in [(46, 138), (152, 140), (164, 166)]:
        d.shape("glow2", circle(x, y, 6), spot=True)
        d.marks("near", circle(x + 2, y - 2, 1.2))
    steam(d, [(54, 120), (146, 120)], 26)
    d.band("deep", "M-30 182 Q100 176 230 182", line=False)


# ================================================================ HAMMAM
def hammam_dome(d: Drawing):
    d.band("far", "M-30 -30 H230", shadow=False, line=False)
    d.shape("mid", "M6 116 A94 94 0 0 1 194 116Z")
    for r, n, off in [(74, 7, 0), (48, 5, 18), (22, 1, 0)]:
        for i in range(n):
            a = math.radians(180 + (i + 0.5) * 180 / n) if n > 1 else math.radians(270)
            x, y = 100 + r * math.cos(a), 116 + r * math.sin(a) * 0.95
            d.shape("glow", _star(x, y, 6 if r > 30 else 8, 0.5, 8 if r < 30 else 6), shadow=False, spot=True)
    d.raw('<path d="M90 38 L110 38 L150 160 L50 160Z" fill="#FFFFFF" opacity=".18"/>'
          '<path d="M46 72 L56 70 L72 160 L60 160Z M144 70 L154 72 L140 160 L128 160Z" fill="#FFFFFF" opacity=".14"/>', "")
    d.shape("deep", rrect(-30, 112, 260, 8, 1))
    for x in (22, 178):
        d.shape("deep", f"M{x - 14} 176 V140 Q{x - 14} 126 {x} 126 Q{x + 14} 126 {x + 14} 140 V176Z", shadow=False)
        d.shape("hero", f"M{x - 9} 150 H{x + 9} Q{x + 8} 160 {x} 160 Q{x - 8} 160 {x - 9} 150Z")
    d.shape("ground", "M34 172 L52 152 H148 L166 172 V184 H34Z")
    d.shape("light", "M34 172 L52 152 H148 L166 172Z", shadow=False)
    d.stroke("far", "M60 158 Q80 166 98 160 M118 166 Q136 160 150 166", 1.2, line=False)
    steam(d, [(80, 148), (120, 146)], 26)
    d.band("near", "M-30 184 H230", line=False)


def hammam_tas(d: Drawing):
    d.disc("glow", 100, 92, 64, line=False)
    d.band("light", "M-30 146 H230")
    d.stroke("far", "M10 160 Q40 154 60 164 T110 166 M130 176 Q160 170 190 178", 1.4, line=False)
    d.shape("pop", "M120 104 L176 96 L180 146 L118 150Z")
    for y in (110, 122, 134):
        d.shape("light", f"M119 {y} L177 {y - 7} L177.6 {y - 3} L119.2 {y + 4}Z", shadow=False, spot=True)
    d.shape("pop", "M118 150 L180 146 L184 162 L124 168Z", shadow=False)
    d.stroke("light", "M126 168 V176 M136 167 V175 M146 166 V174 M156 165 V173 M166 164 V172 M176 163 V171", 1.6, line=False)
    steam(d, [(66, 70), (84, 64), (102, 70)], 28)
    d.shape("hero", "M28 96 H138 Q134 136 83 138 Q32 136 28 96Z")
    d.shape("hero2", ellipse(83, 96, 56, 9), shadow=False)
    d.shape("near", ellipse(83, 97, 48, 6), shadow=False, line=False)
    d.shape("glow2", ellipse(83, 98, 44, 4.5), shadow=False, spot=True)
    dots = " ".join(circle(x, 112 + abs(x - 83) * 0.05, 1.6) for x in range(42, 128, 9))
    d.marks("hero2", dots)
    d.stroke("hero2", "M40 120 Q83 130 126 120", 1.4, line=False)
    d.shape("near", rrect(36, 150, 34, 20, 5))
    d.shape("light", "M40 154 H60", shadow=False, line=False)
    d.stroke("light", "M42 156 H58", 2, line=False)


def _zellige(cx, cy, r):
    """An eight-pointed star tile."""
    return _star(cx, cy, r, 0.62, 8, -90)


def hammam_arch(d: Drawing):
    d.band("ground", "M-30 -30 H230", shadow=False, line=False)
    d.shape("hero", rrect(36, 26, 128, 162, 3))
    for i, x in enumerate(range(46, 160, 18)):
        d.shape("light" if i % 2 else "pop", _zellige(x, 36, 6), shadow=False, spot=i % 2 == 0)
    for y in range(58, 180, 20):
        d.shape("pop", _zellige(46, y, 5), shadow=False, spot=True)
        d.shape("pop", _zellige(154, y, 5), shadow=False, spot=True)
    arch_o = "M58 190 V108 C46 86 56 48 100 46 C144 48 154 86 142 108 V190Z"
    arch_i = "M68 190 V110 C58 92 66 58 100 56 C134 58 142 92 132 110 V190Z"
    d.shape("light", arch_o, shadow=False)
    d.shape("deep", arch_i, shadow=False)
    d.raw('<path d="M80 190 Q100 120 120 190Z" fill="#FFFFFF" opacity=".12"/>', "")
    d.stroke("dark", "M100 56 V80", 1.4)
    d.shape("glow2", "M90 82 H110 L106 110 H94Z")
    d.shape("glow", rrect(95, 88, 10, 16, 2), shadow=False, spot=True)
    d.shape("glow2", "M92 82 L100 74 L108 82Z", shadow=False)
    steam(d, [(84, 170), (116, 168)], 34)
    d.band("mid", "M-30 188 H230")


# ================================================================ SAUNA
def _cabin(d: Drawing, x, y, s, window="glow", snow=False):
    def g():
        d.shape("dark", rrect(14, -46, 8, 16, 1))
        d.shape("hero", rrect(-30, -30, 60, 30, 1))
        d.stroke("hero2", "M-30 -22 H30 M-30 -14 H30 M-30 -6 H30", 1.4, line=False)
        d.shape("dark", "M-38 -28 L0 -52 L38 -28 L34 -26 L0 -46 L-34 -26Z")
        if snow:
            d.shape("light", "M-40 -29 L0 -54 L40 -29 L34 -29 L0 -48 L-34 -29Z", shadow=False)
        d.shape("dark", rrect(-22, -22, 12, 22, 1), shadow=False)
        d.shape(window, rrect(4, -22, 14, 10, 1), shadow=False, spot=True)
    group(d, f"translate({x} {y}) scale({s})", g)


def sauna_lake(d: Drawing):
    d.disc("glow", 150, 66, 18)
    d.band("far", "M-30 104 Q40 92 100 100 T230 96")
    _pines(d, "deep", [(x, 108, 12 + (x * 7) % 9) for x in range(90, 220, 11)], shadow=False)
    d.band("mid", "M-30 108 H230")
    d.stroke("glow", "M126 118 H174 M136 126 H164 M144 134 H156", 2.4, line=False)
    _line_only(d, "M126 120 H174 M138 130 H162", 1.6)
    d.shape("near", "M-30 120 Q30 110 74 126 Q96 136 104 160 L-30 180Z")
    _pines(d, "deep", [(8, 124, 40), (24, 120, 30)])
    d.stroke("light", "M82 70 q-5 -6 0 -12 q5 -6 0 -12 q-5 -6 0 -12", 3)
    _cabin(d, 66, 126, 1.05)
    d.shape("dark", rrect(86, 140, 84, 5, 1.5))
    d.stroke("dark", "M100 144 V162 M126 144 V160 M154 144 V158", 2.6)
    d.stroke("dark", "M166 140 V156 M174 140 V156 M166 148 H174", 1.6)
    d.band("near", waves(176, 2.5, 36), line=False)


def sauna_stove(d: Drawing):
    d.band("hero", "M-30 -30 H230", shadow=False, line=False)
    d.stroke("hero2", " ".join(f"M{x} -30 V230" for x in range(-6, 220, 22)), 1.4, line=False)
    d.shape("hero2", rrect(-30, 54, 260, 10, 1))
    d.shape("hero2", rrect(-30, 172, 260, 40, 1))
    d.shape("dark", rrect(48, 108, 84, 68, 4))
    d.shape("pop", rrect(64, 146, 52, 18, 3), shadow=False, spot=True)
    d.stroke("dark", "M76 146 V164 M90 146 V164 M104 146 V164", 1.6, line=False)
    d.shape("dark", rrect(44, 102, 92, 10, 3))
    for x, y, rx, ry in [(60, 100, 11, 8), (80, 96, 12, 9), (102, 98, 11, 8), (122, 100, 11, 8), (70, 88, 10, 8), (92, 84, 11, 8), (114, 88, 10, 7)]:
        d.shape("mark", ellipse(x, y, rx, ry))
        d.shape("light", ellipse(x - rx * .3, y - ry * .4, rx * .35, ry * .25), shadow=False, line=False, extra='opacity=".45"')
    d.shape("light", cloud(70, 58, 1.2), shadow=False)
    d.shape("light", cloud(96, 48, 1.4), shadow=False)
    d.shape("light", cloud(54, 40, 0.9), shadow=False)
    d.shape("ground", _bar(178, 26, 118, 66, 5))
    d.shape("ground", "M108 60 Q104 72 116 76 Q126 76 126 66 L120 58Z")
    d.shape("glow2", "M110 78 Q108 84 110 88 Q112 84 110 78Z", shadow=False, spot=True)
    d.shape("ground", "M144 132 H182 L178 176 H148Z")
    d.stroke("dark", "M145 142 H181 M147 164 H179", 2.4)
    d.shape("glow2", ellipse(163, 132, 19, 4), shadow=False)


def sauna_icehole(d: Drawing):
    d.disc("glow", 150, 60, 14)
    d.band("mid", "M-30 100 Q40 88 100 96 T230 92")
    _pines(d, "deep", [(x, 108, 14 + (x * 7) % 10) for x in range(-14, 220, 12)], shadow=False)
    d.band("light", "M-30 106 Q100 100 230 108")
    d.stroke("light", "M54 50 q-5 -6 0 -12 q5 -6 0 -12", 3)
    _cabin(d, 44, 120, 0.95, snow=True)
    d.shape("deep", "M86 140 L150 134 L170 156 L96 164Z")
    d.shape("near", "M90 142 L148 137 L164 155 L98 161Z", shadow=False, spot=True)
    d.stroke("light", "M104 152 L124 150 M132 148 L150 146", 1.6, line=False)
    d.limb("dark", "M118 162 V128 M132 160 V126", 3, shadow=False)
    d.stroke("dark", "M118 134 H132 M118 142 H132 M118 150 H132", 2)
    steam(d, [(104, 136), (150, 132)], 28)
    for x, y in [(70, 144), (80, 150), (66, 156), (76, 164), (62, 172)]:
        d.marks("glow2", ellipse(x, y, 2.4, 1.4))


# ================================================================ SOUND BATH
def soundbath_bowl(d: Drawing):
    d.disc("glow", 100, 100, 70, line=False)
    rings = ""
    for r in (58, 68):
        for a0, a1 in ((150, 200), (-20, 30)):
            p0 = (100 + r * math.cos(math.radians(a0)), 104 + r * math.sin(math.radians(a0)))
            p1 = (100 + r * math.cos(math.radians(a1)), 104 + r * math.sin(math.radians(a1)))
            rings += f"M{p0[0]:.1f} {p0[1]:.1f} A{r} {r} 0 0 1 {p1[0]:.1f} {p1[1]:.1f} "
    d.stroke("light", rings, 3)
    d.shape("pop", "M30 158 Q30 136 100 136 Q170 136 170 158 Q170 176 100 176 Q30 176 30 158Z", spot=True)
    d.marks("deep", circle(36, 168, 3) + circle(164, 168, 3))
    d.shape("hero", "M48 96 H152 C150 132 130 150 100 150 C70 150 50 132 48 96Z")
    d.stroke("hero2", "M54 116 H146 M58 124 H142", 1.6, line=False)
    d.shape("hero2", ellipse(100, 96, 52, 10), shadow=False)
    d.shape("deep", ellipse(100, 97, 45, 6.5), shadow=False, line=False)
    d.shape("hero", ellipse(100, 99, 42, 4.5), shadow=False, line=False)
    d.shape("dark", _bar(122, 92, 166, 62, 6))
    d.shape("near", _bar(146, 76, 166, 62, 8))


def soundbath_gong(d: Drawing):
    d.band("far", "M-30 170 H230")
    d.limb("dark", "M28 176 V44 M172 176 V44", 9)
    d.shape("dark", rrect(18, 36, 164, 12, 4))
    d.stroke("dark", "M84 48 L90 58 M116 48 L110 58", 2)
    d.shape("hero", circle(100, 108, 52))
    d.stroke("hero2", circle(100, 108, 40) + " " + circle(100, 108, 28), 2)
    d.shape("hero2", circle(100, 108, 14), spot=True)
    d.shape("light", "M66 82 Q74 70 88 66 Q76 74 70 86Z", shadow=False, line=False, extra='opacity=".6"')
    d.stroke("light", "M164 84 Q170 108 164 132 M176 76 Q184 108 176 140", 2.6, line=False)
    d.stroke("light", "M36 84 Q30 108 36 132 M24 76 Q16 108 24 140", 2.6, line=False)
    d.shape("ground", _bar(136, 172, 158, 136, 4))
    d.shape("pop", ellipse(160, 132, 10, 8), extra='transform="rotate(-30 160 132)"', spot=True)


def soundbath_lying(d: Drawing):
    d.disc("glow", 100, 84, 50)
    d.band("far", "M-30 128 H230")
    d.stroke("pop", "M70 66 Q80 58 90 66 T110 66 T130 66 M78 50 Q88 42 98 50 T118 50", 2.6)
    d.shape("hero2", rrect(14, 120, 172, 8, 3), spot=True)
    d.shape("ground", circle(36, 110, 10))
    d.shape("dark", "M26 112 C24 98 36 94 44 100 C40 102 34 104 30 114Z", shadow=False)
    d.shape("pop", rrect(32, 104, 10, 4, 2), shadow=False)
    d.shape("light", rrect(22, 114, 22, 8, 4))
    d.shape("hero", "M46 108 Q46 98 58 98 L150 100 Q160 100 162 92 Q170 92 170 104 L170 120 H46Z")
    d.stroke("hero2", "M80 100 V120 M118 100 V120", 1.6, line=False)
    for x, w, h in [(50, 34, 20), (98, 42, 24), (148, 30, 18)]:
        d.shape("light", f"M{x - w / 2} {164 - h} H{x + w / 2} C{x + w / 2} {164 - h * .2} {x + w * .3} 166 {x} 166 C{x - w * .3} 166 {x - w / 2} {164 - h * .2} {x - w / 2} {164 - h}Z")
        d.shape("glow2", ellipse(x, 164 - h, w / 2, 3), shadow=False)
    d.shape("dark", _bar(112, 150, 132, 136, 4))
    d.stroke("light", "M30 146 Q24 136 30 128 M168 142 Q176 132 170 124", 2, line=False)


# ================================================================ SURF & YOGA CAMP
def _board(d: Drawing, x, y, rot, role, stripe, spot=False, s=1.0):
    def g():
        d.shape(role, "M0 -72 C16 -52 18 30 11 62 Q0 70 -11 62 C-18 30 -16 -52 0 -72Z", spot=spot)
        d.shape(stripe, "M-1 -66 C1 -40 1 40 -1 64 L1 64 C3 40 3 -40 1 -66Z", shadow=False)
        d.shape(stripe, "M-15 -10 H15 L15.5 -4 H-15.5Z", shadow=False)
    group(d, f"translate({x} {y}) rotate({rot}) scale({s})", g)


def _mat(d: Drawing, x, y, rot, role="pop", s=1.0):
    def g():
        d.shape(role, rrect(-8, -46, 16, 50, 4))
        d.shape(role, ellipse(0, -46, 8, 4), shadow=False)
        d.stroke("dark", "M0 -46 m-4 0 a4 2 0 1 0 8 0 a2 1 0 1 0 -4 0", 1, line=False)
        d.limb("dark", "M-8 -32 H8 M-8 -10 H8", 1.6, shadow=False)
    group(d, f"translate({x} {y}) rotate({rot}) scale({s})", g)


def surfyoga_boards(d: Drawing):
    d.disc("glow", 150, 60, 16)
    d.band("far", waves(108, 3, 30))
    d.band("mid", waves(122, 3, 34))
    d.band("ground", "M-30 140 Q100 130 230 142")
    _palm(d, 24, 150, 40, 44, 0.9)
    _board(d, 80, 112, -10, "hero", "light", spot=True)
    _board(d, 116, 116, 8, "hero2", "light", s=0.92)
    _mat(d, 150, 160, 18, "pop", 1.1)
    d.band("ground", "M-30 170 Q100 164 230 172", line=False)


def surfyoga_camp(d: Drawing):
    d.disc("glow", 46, 60, 15)
    d.band("far", waves(112, 3, 30))
    d.band("ground", "M-30 132 Q100 122 230 134")

    def tent(x, y, s, flag="pop"):
        def g():
            d.stroke("dark", "M0 -56 V-70", 1.6)
            d.shape(flag, "M0 -70 L12 -66 L0 -62Z", shadow=False, spot=True)
            d.shape("light", "M-44 0 L-38 -24 L0 -58 L38 -24 L44 0Z")
            d.stroke("far", "M-38 -24 Q0 -20 38 -24", 1.6, line=False)
            d.shape("dark", "M-10 0 L0 -34 L10 0Z", shadow=False)
            d.shape("glow", "M-6 0 L0 -24 L6 0Z", shadow=False)
        group(d, f"translate({x} {y}) scale({s})", g)
    tent(150, 128, 0.7, "hero2")
    tent(84, 148, 1.15)
    _board(d, 152, 150, 16, "hero", "light", spot=True, s=0.68)
    d.shape("hero2", "M30 176 L70 166 L90 182 L46 194Z")
    d.stroke("pop", "M20 100 Q50 108 74 102", 1.2, line=False)


def surfyoga_pose(d: Drawing):
    d.disc("glow", 100, 92, 44)
    d.band("far", waves(116, 2.5, 30))
    d.band("mid", waves(128, 3, 34))
    d.band("ground", "M-30 142 Q100 134 230 144")
    d.shape("hero", "M28 158 Q30 146 100 146 Q170 146 172 158 Q170 168 100 168 Q30 168 28 158Z", spot=True)
    d.shape("light", "M34 157 H166 L166 159 H34Z", shadow=False)
    d.limb("dark", "M100 154 V108", 6.5)
    d.limb("dark", "M100 110 L118 120 L102 128", 6)
    d.shape("dark", rrect(92, 74, 16, 38, 7))
    d.limb("dark", "M94 80 L86 60 L100 40", 4.6)
    d.limb("dark", "M106 80 L114 60 L100 40", 4.6)
    d.shape("dark", circle(100, 66, 8))
    d.shape("dark", ellipse(100, 154, 6, 3))


# ================================================================ DIGITAL DETOX
def _phone(d: Drawing, x, y, rot, s=1.0):
    def g():
        d.shape("dark", rrect(-14, -26, 28, 52, 6))
        d.shape("mark", rrect(-11, -21, 22, 42, 3), shadow=False, line=False)
        d.shape("light", rrect(-11, -21, 22, 42, 3), shadow=False, extra='opacity=".12"', line=False)
        d.marks("light", rrect(-4, -24, 8, 1.6, .8))
        d.stroke("light", "M-6 -14 L2 -18", 1.2, line=False)
    group(d, f"translate({x} {y}) rotate({rot}) scale({s})", g)


def detox_basket(d: Drawing):
    d.disc("glow", 52, 54, 14)
    d.band("far", "M-30 98 L20 76 L54 90 L96 62 L140 92 L176 76 L230 90")
    d.shape("light", "M96 62 L106 70 L100 70 L96 74 L90 70 L86 70Z", shadow=False)
    _pines(d, "deep", [(x, 108, 12 + (x * 7) % 9) for x in range(-14, 220, 11)], shadow=False)
    d.band("mid", "M-30 106 H230")
    d.stroke("light", "M20 122 H50 M150 118 H180 M160 134 H186", 2, line=False)
    _line_only(d, "M20 124 H50 M150 120 H180", 1.4)
    d.shape("ground", "M64 130 H136 L176 230 H24Z")
    d.stroke("near", "M62 140 H138 M56 156 H144 M48 176 H152 M38 200 H162", 1.4, line=False)
    _phone(d, 106, 128, 12, 1.05)
    d.limb("hero2", "M74 136 Q100 96 126 136", 3.2, shadow=False)
    d.shape("hero2", "M64 134 H136 L128 176 H72Z", spot=True)
    d.stroke("near", "M66 144 H134 M68 154 H132 M70 164 H130 M84 136 L86 176 M100 136 V176 M116 136 L114 176", 1.2, line=False)
    d.shape("near", rrect(62, 130, 76, 7, 3))


def detox_hammock(d: Drawing):
    d.disc("glow", 100, 70, 16)
    d.band("far", "M-30 108 L20 88 L60 100 L100 80 L140 98 L180 86 L230 100")
    d.band("mid", "M-30 112 H230")
    d.stroke("light", "M70 122 H100 M120 128 H150", 2, line=False)
    d.band("near", "M-30 140 Q100 130 230 142")
    d.limb("dark", "M30 190 V40", 9)
    d.limb("dark", "M170 190 V40", 9)
    d.shape("deep", "M-30 -30 H230 V30 Q200 52 170 40 Q140 56 110 40 Q100 30 90 40 Q60 56 30 40 Q0 52 -30 30Z")
    d.stroke("dark", "M34 96 L54 110 M166 96 L146 110", 1.4)
    d.shape("pop", "M52 104 Q100 156 148 104 Q148 118 140 120 Q100 150 60 120 Q52 118 52 104Z", spot=True)
    d.stroke("light", "M60 116 Q100 142 140 116", 1.6, line=False)
    d.shape("light", "M86 116 L100 122 L114 114 L112 120 L100 128 L88 122Z")
    d.stroke("near", "M100 122 V128", 1.2, line=False)
    d.shape("hero2", ellipse(128, 112, 12, 4))
    d.shape("hero2", "M122 112 Q122 102 128 102 Q134 102 134 112Z")
    d.stroke("pop", "M122 110 H134", 1.6, line=False)
    d.band("near", "M-30 182 Q100 174 230 184", line=False)


def _leafy(x, y, L, w, a):
    return (f"M0 0 C{L * .3:.1f} {-w} {L * .7:.1f} {-w} {L} 0 C{L * .7:.1f} {w} {L * .3:.1f} {w} 0 0Z",
            f"translate({x} {y}) rotate({a})")


def detox_sprout(d: Drawing):
    d.disc("glow", 100, 92, 62, line=False)
    d.band("near", "M-30 158 Q100 148 230 160")
    _phone(d, 100, 112, -8, 1.65)
    d.stroke("mid", "M96 158 C88 130 120 116 104 92 C94 76 112 62 106 48", 3)
    for x, y, L, w, a in [(94, 140, 18, 6, 200), (108, 120, 18, 6, -20), (98, 98, 16, 5, 210), (108, 78, 16, 5, -30), (104, 60, 14, 5, 220)]:
        p, t = _leafy(x, y, L, w, a)
        d.shape("mid", p, extra=f'transform="{t}"')
    for i in range(5):
        d.shape("pop", "M0 0 C-5 -5 -5 -13 0 -15 C5 -13 5 -5 0 0Z", shadow=i == 0, spot=True,
                extra=f'transform="translate(106 46) rotate({i * 72})"')
    d.shape("hero2", circle(106, 46, 3.6), shadow=False)
    for x in (40, 64, 140, 166):
        d.shape("mid", f"M{x - 6} 160 Q{x - 4} 146 {x} 140 Q{x + 2} 150 {x + 6} 160Z", shadow=False)
    d.shape("hero", "M150 74 Q140 64 146 58 Q152 60 152 70 Q156 60 162 62 Q164 70 152 76Z")
    d.stroke("dark", "M152 64 V76", 1.2)


# ================================================================ CONCEPTS
SNOW_FIX = {"sky": [SNOW_SKY]}


def C(id, act, title, fn, palettes=None, overrides=None, checks=(), fixes=None):
    return Concept(id, act, title, fn, list(palettes or ALL), dict(overrides or {}), list(checks), dict(fixes or {}))


CONCEPTS = [
    C("iceclimb-icefall", "ice-climbing", "Frozen waterfall", iceclimb_icefall, overrides={"glow2": ICE},
      checks=[("glow2", "far"), ("hero", "glow2"), ("pop", "glow2"), ("deep", "glow2"), ("light", "deep"), ("far", "sky")],
      fixes={"far": ["mid", "near"]}),
    C("iceclimb-axes", "ice-climbing", "Crossed ice axes", iceclimb_axes, overrides={"glow2": ICE},
      checks=[("hero", "glow"), ("dark", "glow"), ("glow", "glow2"), ("hero", "glow2"), ("dark", "glow2"), ("light", "glow2")],
      fixes={"glow": ["glow2", "far", "mid"], "hero": ["pop", "deep"]}),
    C("iceclimb-crampon", "ice-climbing", "Crampon kick", iceclimb_crampon, overrides={"glow2": ICE, "mark": "#8D99AE"},
      checks=[("hero", "sky"), ("hero", "glow2"), ("mark", "glow2"), ("light", "far"), ("far", "sky"), ("pop", "dark")],
      fixes={"hero": ["pop", "deep"], "far": ["mid", "near"]}),
    C("icefish-hole", "ice-fishing", "Under the ice", icefish_hole, UNDERWATER, {"glow2": ICE},
      checks=[("light", "far"), ("hero", "mid"), ("pop", "mid"), ("glow2", "mid"), ("far", "sky"), ("hero2", "mid")],
      fixes={"far": ["near", "deep"], "mid": ["near"], "hero": ["pop", "light"], "hero2": ["light", "glow"], "pop": ["hero2", "light"]}),
    C("icefish-shacks", "ice-fishing", "Shacks on the lake", icefish_shacks, overrides={"glow2": ICE},
      checks=[("light", "deep"), ("hero", "light"), ("pop", "light"), ("hero2", "light"), ("far", "sky")],
      fixes={"hero2": ["mid", "near"], "far": ["mid"]}),
    C("icefish-bucket", "ice-fishing", "Fishing through the ice", icefish_bucket, overrides={"glow2": ICE},
      checks=[("light", "deep"), ("hero", "light"), ("hero2", "light"), ("mark", "light"), ("light", "sky"), ("pop", "sky"), ("mid", "sky"), ("mid", "light")],
      fixes={**SNOW_FIX, "hero2": ["glow", "mid"]}),
    C("icehotel-facade", "ice-hotel", "Ice hotel entrance", icehotel_facade, NIGHT_PALETTES, {**NIGHT, "glow2": ICE},
      checks=[("sky", "light"), ("glow2", "sky"), ("glow2", "light"), ("glow", "light")],
      fixes={**NIGHT_FIX, "glow": ["#F2A541"], "glow2": ["#86BEDD"]}),
    C("icehotel-bed", "ice-hotel", "Ice bed", icehotel_bed, overrides={"glow2": ICE, "ground": "#B98A5E"},
      checks=[("glow2", "light"), ("hero", "ground"), ("hero", "glow2"), ("ground", "glow2"), ("far", "glow2")],
      fixes={"hero": ["pop", "deep"], "far": ["mid", "near"]}),
    C("icehotel-glass", "ice-hotel", "Ice bar glass", icehotel_glass, overrides={"glow2": ICE},
      checks=[("glow2", "glow"), ("pop", "glow2"), ("glow2", "sky"), ("light", "sky"), ("near", "glow")],
      fixes={"glow": ["far", "mid"], "sky": [SNOW_SKY, "far"]}),
    C("igloo-day", "igloo-stay", "Snow-block igloo", igloo_day, overrides={"glow2": ICE},
      checks=[("light", "sky"), ("mid", "light"), ("glow2", "light"), ("mid", "sky")], fixes={**SNOW_FIX, "glow2": ["#86BEDD"]}),
    C("igloo-glass", "igloo-stay", "Glass igloos", igloo_glass, NIGHT_PALETTES, NIGHT,
      checks=[("sky", "light"), ("mark", "light"), ("mark", "sky"), ("far", "sky"), ("dark", "light")],
      fixes={**NIGHT_FIX, "mark": ["deep", "dark", "near"]}),
    C("igloo-entrance", "igloo-stay", "Glowing igloo door", igloo_entrance, NIGHT_PALETTES,
      overrides={"glow2": "#F7E7A6", "sky2": "#C9DCEA"},
      checks=[("sky", "light"), ("hero", "light"), ("glow", "dark"), ("pop", "light")], fixes=NIGHT_FIX),
    C("sledging-wooden", "sledging", "Wooden sledge", sledging_wooden, overrides={"ground": WOOD},
      checks=[("light", "sky"), ("hero", "light"), ("ground", "light"), ("light", "mid"), ("pop", "light"), ("mid", "sky")],
      fixes={**SNOW_FIX, "hero": ["pop", "deep"]}),
    C("sledging-hill", "sledging", "Downhill run", sledging_hill, overrides={"ground": "#E9B48A", "glow2": ICE},
      checks=[("light", "sky"), ("pop", "light"), ("hero", "light"), ("dark", "light"), ("mid", "sky"), ("light", "mid"), ("hero2", "pop")],
      fixes={**SNOW_FIX, "hero2": ["light", "glow"]}),
    C("sledging-reindeer", "sledging", "Reindeer sledge", sledging_reindeer, overrides={"ground": "#9C6B43"},
      checks=[("light", "sky"), ("ground", "light"), ("hero", "light"), ("ground", "sky"), ("mid", "sky"), ("light", "mid")],
      fixes=SNOW_FIX),
    C("meditate-garden", "meditation", "Zen garden", meditate_garden,
      checks=[("mid", "ground"), ("near", "ground"), ("far", "ground"), ("pop", "ground")],
      fixes={"far": ["mid", "near"], "mid": ["deep", "dark"]}),
    C("meditate-incense", "meditation", "Incense", meditate_incense,
      checks=[("light", "glow"), ("dark", "glow"), ("hero", "near"), ("hero2", "glow"), ("hero", "glow")],
      fixes={"glow": ["far", "mid"], "hero2": ["pop", "light"]}),
    C("meditate-buddha", "meditation", "Buddha & bodhi leaves", meditate_buddha, overrides={"hero": "#D4A94F", "hero2": "#F2D58C"},
      checks=[("hero", "glow"), ("hero", "sky"), ("hero", "far"), ("pop", "far"), ("near", "sky")],
      fixes={"glow": ["far", "light", "mid"], "far": ["mid", "near"]}),
    C("thermal-palace", "thermal-baths", "Bath palace", thermal_palace, NO_GOLD, {"hero2": "#F3C350", "mark": "#4F9A86", **POOL},
      checks=[("hero2", "sky"), ("mark", "sky"), ("light", "mid"), ("dark", "hero2"), ("light", "hero2")], fixes={"sky": [SNOW_SKY]}),
    C("thermal-roman", "thermal-baths", "Roman bath", thermal_roman, overrides={"mid": "#6FAE8F", "near": "#4C8A72", "ground": "#E7D3A8", "far": "#9C8466"},
      checks=[("ground", "sky"), ("ground", "far"), ("light", "mid"), ("dark", "sky"), ("ground", "mid")], fixes={"sky": ["#9CC6E2", "#8DBBDB"]}),
    C("thermal-chess", "thermal-baths", "Chess in the pool", thermal_chess, NO_GOLD, {**POOL, "ground": "#C9955A", "hero2": "#F3C350"},
      checks=[("dark", "mid"), ("light", "mid"), ("ground", "mid"), ("hero2", "far")], fixes={"far": ["sky", "light"]}),
    C("onsen-rotenburo", "onsen", "Rock pool & lantern", onsen_rotenburo, overrides={"hero": "#86CFD3", "mid": "#9AA3AE"},
      checks=[("light", "sky"), ("hero", "mid"), ("dark", "light"), ("mid", "light"), ("far", "sky"), ("light", "far")],
      fixes={**SNOW_FIX, "far": ["near", "deep"]}),
    C("onsen-noren", "onsen", "Noren curtain", onsen_noren, overrides={"ground": "#C8955F"},
      checks=[("hero", "dark"), ("light", "hero"), ("pop", "ground"), ("dark", "ground")], fixes={"hero": ["pop", "mid", "near"]}),
    C("onsen-soaker", "onsen", "Towel on the head", onsen_soaker, overrides={"hero2": "#F1C9A0", "glow2": "#F4C430", "near": "#5FB3BE"},
      checks=[("light", "sky"), ("hero2", "near"), ("light", "dark"), ("glow2", "near"), ("far", "sky"), ("mid", "light")],
      fixes={**SNOW_FIX, "far": ["mid", "deep"]}),
    C("hammam-dome", "hammam", "Star-lit dome", hammam_dome,
      checks=[("glow", "mid"), ("mid", "far"), ("light", "far"), ("deep", "far")], fixes={"glow": ["glow2", "light"], "mid": ["near", "deep"]}),
    C("hammam-tas", "hammam", "Copper bowl & towel", hammam_tas, overrides={"hero": "#C97B3F", "hero2": "#EDB06C", "glow2": "#BFE6EE"},
      checks=[("hero", "glow"), ("pop", "glow"), ("hero", "light"), ("near", "light")], fixes={"glow": ["far", "sky2", "mid"]}),
    C("hammam-arch", "hammam", "Tiled arch", hammam_arch, overrides={"glow2": "#D9A441"},
      checks=[("hero", "ground"), ("pop", "hero"), ("light", "hero"), ("deep", "light"), ("glow2", "deep")],
      fixes={"hero": ["near", "mid", "deep"], "pop": ["hero2", "light"]}),
    C("sauna-lake", "sauna", "Lakeside sauna", sauna_lake, NO_GOLD, {"hero": WOOD, "hero2": "#8A4E2A"},
      checks=[("hero", "near"), ("hero", "mid"), ("dark", "mid"), ("light", "sky"), ("deep", "far"), ("near", "mid")],
      fixes={"sky": [SNOW_SKY, "sky2"], "near": ["deep", "ground"]}),
    C("sauna-stove", "sauna", "Löyly on the stones", sauna_stove, overrides={"hero": "#C98B55", "hero2": "#A86E3E", "mark": "#7D8794", "ground": "#7A4B2A"},
      checks=[("mark", "hero"), ("light", "hero"), ("dark", "hero"), ("ground", "hero")]),
    C("sauna-icehole", "sauna", "Ice hole plunge", sauna_icehole, overrides={"hero": WOOD, "hero2": "#8A4E2A", "glow2": ICE},
      checks=[("light", "sky"), ("light", "deep"), ("hero", "light"), ("near", "light"), ("mid", "sky")],
      fixes=SNOW_FIX),
    C("soundbath-bowl", "sound-bath", "Singing bowl", soundbath_bowl, overrides={"hero": "#D9A441", "hero2": "#F2CF7A"},
      checks=[("hero", "glow"), ("light", "glow"), ("pop", "hero"), ("hero", "sky")],
      fixes={"glow": ["far", "mid", "near"], "pop": ["near", "deep"]}),
    C("soundbath-gong", "sound-bath", "Gong", soundbath_gong, overrides={"hero": "#D9A441", "hero2": "#B8862E"},
      checks=[("hero", "sky"), ("light", "sky"), ("dark", "sky"), ("hero", "far")], fixes={"sky": ["far", "mid"], "far": ["near", "deep"]}),
    C("soundbath-lying", "sound-bath", "Crystal bowls", soundbath_lying, overrides={"glow2": "#D6E8F5"},
      checks=[("light", "far"), ("hero", "far"), ("pop", "glow"), ("pop", "sky"), ("hero", "glow")],
      fixes={"far": ["mid", "near"], "pop": ["hero", "deep"]}),
    C("surfyoga-boards", "surf-and-yoga-camp", "Boards & mat", surfyoga_boards, NO_GOLD,
      checks=[("hero", "mid"), ("light", "sky"), ("light", "ground"), ("pop", "ground"), ("hero", "far")],
      fixes={"sky": ["sky2", SNOW_SKY], "pop": ["hero2", "deep"], "ground": ["#E3C08A"]}),
    C("surfyoga-camp", "surf-and-yoga-camp", "Beach camp", surfyoga_camp, NO_GOLD,
      checks=[("light", "far"), ("light", "ground"), ("hero", "ground"), ("hero2", "ground"), ("light", "sky")],
      fixes={"ground": ["#E3C08A"], "hero2": ["pop", "deep"], "hero": ["pop", "light"], "sky": [SNOW_SKY]}),
    C("surfyoga-pose", "surf-and-yoga-camp", "Tree pose on the board", surfyoga_pose, NO_GOLD,
      checks=[("dark", "glow"), ("hero", "ground"), ("glow", "far")], fixes={"hero": ["pop", "deep"]}),
    C("detox-basket", "digital-detox", "Phone in the basket", detox_basket, NO_GOLD, {"hero2": "#D9A866", "ground": "#8C6A4A", "near": "#5E4128"},
      checks=[("dark", "mid"), ("hero2", "ground"), ("ground", "mid"), ("far", "sky")], fixes={"far": ["mid"]}),
    C("detox-hammock", "digital-detox", "Hammock & book", detox_hammock, NO_GOLD,
      checks=[("pop", "mid"), ("pop", "near"), ("dark", "mid"), ("deep", "sky"), ("far", "sky")],
      fixes={"pop": ["hero", "hero2"], "far": ["mid", "near"], "deep": ["mid", "near"]}),
    C("detox-sprout", "digital-detox", "Phone gone to seed", detox_sprout, overrides={"mid": "#5E9C6A", "near": "#8CC084"},
      checks=[("dark", "glow"), ("mid", "glow"), ("pop", "glow"), ("hero", "glow"), ("near", "sky")],
      fixes={"glow": ["far", "sky2"], "pop": ["hero", "deep"]}),
]
