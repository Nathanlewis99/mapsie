"""Transport concepts: three ideas each for thirteen ways of getting around."""
from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group

EVENODD = 'fill-rule="evenodd"'
SEA = ["coastal", "meadow", "blush", "dusk"]


# ---------------------------------------------------------------- private helpers
def clip(d: Drawing, cid: str, path: str, fn):
    """Clip everything drawn by fn to `path`, in both styles (bands are not clipped in line style)."""
    tag = f'<clipPath id="{cid}"><path d="{path}"/></clipPath><g clip-path="url(#{cid})">'
    d.raw(tag, tag)
    fn()
    d.raw("</g>", "</g>")


def framed(fn):
    """Line style doesn't clip shapes to the sticker; clip anything that bleeds past the edge."""
    def draw(d: Drawing):
        if d.paper:
            fn(d)
        else:
            clip(d, "frame", circle(100, 100, 89), lambda: fn(d))
    draw.__name__ = fn.__name__
    return draw


def post(d: Drawing, role: str, x: float, y0: float, y1: float, w: float, shadow=True, spot=False):
    """A vertical pole as a thin shape (vertical limbs lose their shadow filter)."""
    d.shape(role, rrect(x - w / 2, y0, w, y1 - y0, w / 2), shadow=shadow, spot=spot)


def puffs(y: float, radii=(12, 16, 10, 14, 11, 15), x0: float = -30) -> str:
    """A cloud-bank edge: a row of upward bumps from x0 to past 230."""
    s, x, i = f"M{x0} {y}", x0, 0
    while x < 232:
        r = radii[i % len(radii)]
        s += f" a{r} {r} 0 0 1 {2 * r} 0"
        x += 2 * r
        i += 1
    return s


def wheel(d: Drawing, x: float, y: float, r: float, tyre="dark", hub="light", spokes=False):
    d.shape(tyre, circle(x, y, r))
    d.shape(hub, circle(x, y, r * 0.42), shadow=False)
    if spokes:
        d.marks(tyre, circle(x, y, r * 0.16))


def pine(x: float, y: float, s: float = 1.0) -> str:
    return (f"M{x} {y - 30 * s} L{x + 9 * s} {y - 16 * s} L{x + 5 * s} {y - 16 * s} L{x + 12 * s} {y - 4 * s} "
            f"L{x + 2 * s} {y - 4 * s} V{y} H{x - 2 * s} V{y - 4 * s} L{x - 12 * s} {y - 4 * s} "
            f"L{x - 5 * s} {y - 16 * s} L{x - 9 * s} {y - 16 * s}Z")


# ================================================================ FLIGHT
WIN_OUT = rrect(52, 26, 96, 140, 46)
WIN_IN = rrect(63, 39, 74, 114, 36)


@framed
def flight_window(d: Drawing):
    def view():
        d.shape("sky2", "M40 20 H160 V170 H40Z", shadow=False, line=False)
        d.disc("glow", 116, 84, 11)
        d.shape("light", cloud(70, 98, 0.55), shadow=False)
        d.shape("light", puffs(116, (8, 11, 7, 10)) + " L230 230 L-30 230Z", shadow=False)
        d.shape("hero", "M24 150 L138 114 L148 118 L54 178Z")
        d.shape("pop", "M137 114 L142 92 L149 92 L148 118Z", spot=True)
        d.stroke("dark", "M60 152 L136 124", 1.4)
        d.shape("hero2", "M40 20 H160 V60 H40Z", spot=True)
        d.shape("light", rrect(92, 54, 16, 6, 3), shadow=False)
    clip(d, "win", WIN_IN, view)
    d.shape("ground", f"M-30 -30 H230 V230 H-30Z {WIN_OUT}", line=False, extra=EVENODD)
    d.shape("light", f"{WIN_OUT} {WIN_IN}", extra=EVENODD)
    d.stroke("far", "M30 178 Q100 186 170 178", 2.4, line=False)


JET = "M44 89 H158 C174 89 184 95 188 100 C184 105 174 109 160 109 H54 C44 109 36 104 30 96 L28 91Z"


@framed
def flight_jet(d: Drawing):
    d.disc("glow", 58, 62, 20)
    d.shape("light", cloud(134, 44, 1.0))
    d.shape("light", cloud(20, 104, 0.8), shadow=False)
    d.band("light", puffs(150, (12, 16, 10, 15)))
    d.band("sky2", puffs(172, (14, 10, 16, 12), -40), line=False)

    def jet():
        d.shape("hero2", "M42 90 L24 58 L37 58 L66 90Z", spot=True)
        d.shape("hero", "M40 100 L20 110 L30 111 L60 102Z", shadow=False)
        d.shape("hero", JET)
        d.shape("hero2", "M34 100 H176 C181 101 185 102 186 103 C178 106 170 106 160 106 H52 C44 106 38 103 34 100Z",
                shadow=False, spot=True)
        for x in range(62, 156, 8):
            d.marks("light", circle(x, 95, 1.9))
        d.marks("dark", "M170 92 L179 93 L184 98 L172 98Z")
        d.shape("hero", "M114 104 L80 134 L94 134 L136 106Z")
        d.shape("dark", rrect(96, 111, 28, 11, 5.5))
        d.shape("light", rrect(118, 112.5, 5, 8, 2.5), shadow=False)
    group(d, "translate(100 100) rotate(-11) scale(.92) translate(-100 -96)", jet)


@framed
def flight_pass(d: Drawing):
    d.disc("far", 100, 100, 70)
    d.shape("mid", "M52 52 Q70 40 92 46 Q100 58 88 66 Q74 70 70 84 Q56 86 46 76Z M120 40 Q146 44 160 64 Q150 70 136 64 Q124 58 120 40Z "
                   "M150 130 Q166 120 168 136 Q160 156 142 160 Q136 148 150 130Z", shadow=False, line=False)
    d.raw('<path d="M24 70 Q90 0 176 54" fill="none" stroke="#fff" stroke-width="2.6" stroke-dasharray="1 7" stroke-linecap="round"/>', "")
    d.marks("light", "M176 54 l-9 -1 l3 4 l-3 5Z")

    def passport():
        d.shape("deep", rrect(46, 52, 70, 96, 6))
        d.stroke("hero2", circle(81, 92, 14), 2.4)
        d.stroke("hero2", "M67 92 H95 M81 78 Q72 92 81 106 Q90 92 81 78", 1.6)
        d.shape("hero2", rrect(62, 120, 38, 4, 2), shadow=False)
    group(d, "rotate(-14 81 100)", passport)

    def ticket():
        body = "M58 92 H150 a4 4 0 0 0 0 0 V102 a6 6 0 0 0 0 12 V146 H58 V114 a6 6 0 0 0 0 -12Z"
        d.shape("light", rrect(58, 92, 116, 58, 6))
        d.shape("hero", "M64 92 H136 V106 H58 V98 A6 6 0 0 1 64 92Z", shadow=False, spot=True)
        d.shape("hero", "M140 92 H168 A6 6 0 0 1 174 98 V106 H140Z", shadow=False, spot=True)
        d.stroke("dark", "M138 96 V146", 1.6)
        d.raw('<path d="M138 108 V148" stroke="#fff" stroke-width="2" stroke-dasharray="2 4"/>', "")
        # plane icon
        d.marks("dark", "M66 124 L96 124 C100 124 102 126 102 127 C102 128 100 130 96 130 L66 130 L62 122Z "
                        "M78 124 L70 112 L76 112 L90 124Z M78 130 L70 142 L76 142 L90 130Z")
        d.shape("dark", rrect(108, 114, 24, 4, 2), shadow=False)
        d.shape("dark", rrect(108, 124, 18, 4, 2), shadow=False)
        d.shape("pop", rrect(108, 134, 22, 6, 3), shadow=False)
        for i, w in enumerate([1.5, 3, 1.5, 1.5, 3, 1.5, 3, 1.5]):
            x = 146 + i * 3.2
            d.marks("dark", f"M{x} 116 h{w * 0.7} v26 h{-w * 0.7}Z")
    group(d, "rotate(8 116 120)", ticket)


# ================================================================ TRAIN JOURNEY
BULLET = "M-30 94 H112 C146 94 172 108 192 126 C194 129 192 132 188 132 H-30Z"


@framed
def train_bullet(d: Drawing):
    d.disc("glow", 64, 64, 18)
    d.band("far", "M-30 104 L40 84 L66 68 Q74 63 82 68 L118 92 L160 98 L230 92")
    d.shape("light", "M66 68 Q74 63 82 68 L92 75 L86 74 L80 78 L74 73 L68 77 L60 72Z", shadow=False)
    d.band("mid", hills(120, 8, 30))
    for y, x0, x1 in [(48, 100, 150), (60, 120, 176)]:
        d.stroke("light", f"M{x0} {y} H{x1}", 2.4, line=False)
    d.stroke("dark", "M30 94 L44 82 L54 94 M44 82 H60", 1.8)
    d.shape("hero", BULLET)
    d.shape("light", "M-30 102 H120 C134 102 146 106 154 112 H-30Z", shadow=False)
    for x in range(-24, 116, 18):
        d.marks("dark", rrect(x, 104.5, 11, 6, 2))
    d.shape("dark", "M136 103 C150 106 160 110 168 116 L150 116 C146 112 142 108 136 103Z", shadow=False)
    d.shape("hero2", "M-30 120 H170 C176 122 180 124 184 126 H-30Z", shadow=False, spot=True)
    d.stroke("dark", "M18 134 V128 M78 134 V128", 1)
    for x in (10, 30, 70, 90):
        d.shape("dark", circle(x, 135, 5), shadow=False)
    d.band("ground", "M-30 140 H230")
    d.stroke("dark", "M-30 140 H230", 2.4)
    d.band("near", hills(170, 6), line=False)


@framed
def train_tracks(d: Drawing):
    d.disc("glow", 100, 110, 30)
    d.band("far", hills(112, 10, 10))
    d.band("mid", "M-30 116 Q100 108 230 116")
    d.shape("ground", "M96 112 H104 L180 210 H20Z", line=False)
    for i in range(9):
        t = (i / 8) ** 1.7
        y = 114 + t * 84
        hw = 6 + t * 70
        th = 1 + t * 6
        d.shape("dark", f"M{100 - hw} {y} H{100 + hw} L{100 + hw * 1.02} {y + th} H{100 - hw * 1.02}Z", shadow=False)
    d.stroke("hero", "M98 112 L46 210", 3.4)
    d.stroke("hero", "M102 112 L154 210", 3.4)
    # telegraph poles
    poles = [(62, 120, 104), (44, 134, 92), (16, 164, 66)]
    for x, y, top in poles:
        w = (y - top) / 12
        post(d, "dark", x, top, y, max(2, w), shadow=False)
        d.stroke("dark", f"M{x - w * 2.4} {top + w} H{x + w * 2.4}", max(1.2, w * 0.6))
    d.stroke("dark", "M62 105 Q53 104 44 94 Q30 80 16 68", 1)
    # signal
    post(d, "dark", 150, 64, 172, 5)
    d.shape("pop", "M146 70 L186 62 L186 74 L146 80Z", spot=True)
    d.shape("light", "M170 65.5 L178 64 L178 75.5 L170 77Z", shadow=False)
    d.shape("dark", rrect(140, 60, 12, 22, 4))
    d.marks("glow2", circle(146, 67, 3))
    d.marks("light", circle(146, 75, 3))
    d.shape("dark", rrect(142, 166, 16, 8, 2))


@framed
def train_clock(d: Drawing):
    import math
    d.band("mid", "M-30 -30 H230", shadow=False, line=False)
    d.shape("sky2", "M26 200 V104 A74 74 0 0 1 174 104 V200Z")
    d.stroke("mid", "M63 200 V44 M100 200 V30 M137 200 V44 M26 104 H174 M38 66 H162", 3)
    d.stroke("mid", "M50 104 A50 50 0 0 1 150 104", 3)
    d.band("near", "M-30 160 H230")
    d.shape("hero2", "M-30 160 H230 V166 H-30Z", shadow=False, spot=True)
    # bracket + clock
    post(d, "dark", 100, -10, 50, 6)
    d.shape("dark", "M86 50 H114 L108 58 H92Z")
    d.shape("dark", circle(100, 102, 46))
    d.shape("hero2", circle(100, 102, 41), shadow=False, spot=True)
    d.shape("light", circle(100, 102, 35), shadow=False)
    for i in range(12):
        a = i * math.pi / 6
        r0, r1 = (24, 31) if i % 3 == 0 else (27, 31)
        x0, y0 = 100 + r0 * math.sin(a), 102 - r0 * math.cos(a)
        x1, y1 = 100 + r1 * math.sin(a), 102 - r1 * math.cos(a)
        d.stroke("dark", f"M{x0:.1f} {y0:.1f} L{x1:.1f} {y1:.1f}", 2.6 if i % 3 == 0 else 1.4)
    d.stroke("dark", "M100 102 L115 90", 3.6)
    d.stroke("dark", "M100 102 L96 76", 2.6)
    d.stroke("pop", "M100 102 L85 121", 1.3)
    d.marks("dark", circle(100, 102, 3))
    d.shape("dark", "M92 146 H108 L103 156 H97Z")


# ================================================================ SCENIC RAILWAY
def steam_loco(d: Drawing, body="hero", trim="hero2", steam=True):
    if steam:
        d.shape("light", cloud(98, 44, 1.1))
        d.shape("light", cloud(52, 34, 1.4))
        d.shape("light", cloud(8, 46, 1.2))
    d.shape(trim, rrect(-6, 94, 40, 36, 3))
    d.shape("dark", rrect(-8, 90, 44, 6, 2), shadow=False)
    d.shape("dark", rrect(30, 62, 50, 9, 3))
    d.shape(body, rrect(36, 69, 40, 62, 3))
    d.shape("light", rrect(45, 78, 20, 18, 3), shadow=False)
    d.shape("dark", "M144 90 V64 H139 V57 H163 V64 H158 V90Z")
    d.shape(trim, "M108 92 Q108 74 119 74 Q130 74 130 92Z", spot=True)
    d.shape(body, rrect(72, 88, 80, 38, 8))
    d.shape(trim, "M96 88 h5 v38 h-5Z M132 88 h5 v38 h-5Z", shadow=False, spot=True)
    d.shape("dark", rrect(146, 86, 24, 42, 6))
    d.disc("glow2", 158, 82, 5, line=False)
    d.shape("dark", rrect(30, 124, 146, 7, 2))
    d.shape("pop", rrect(166, 128, 12, 10, 2))
    d.shape("dark", "M164 138 L188 158 H164Z")
    for x, r in [(62, 17), (102, 17)]:
        wheel(d, x, 141, r)
    wheel(d, 146, 149, 9)
    d.stroke("light", "M62 146 H102", 3.2)
    d.stroke("dark", "M62 146 H102", 1.2)
    d.marks("pop", circle(62, 146, 2.4) + circle(102, 146, 2.4))


@framed
def scenic_steam(d: Drawing):
    d.disc("glow", 150, 48, 18)
    d.band("far", hills(132, 12, -20))
    steam_loco(d)
    d.band("ground", "M-30 160 H230")
    d.stroke("dark", "M-30 159 H230", 3)
    d.band("near", hills(182, 5, 20), line=False)


def small_train(d: Drawing, body="hero", roof="dark"):
    """A little steam train facing right, rails at y=0, x from -110 to 0."""
    d.shape("light", cloud(-44, -42, 0.8))
    d.shape("light", cloud(-82, -48, 0.6))
    for x in (-108, -74):
        d.shape(body, rrect(x, -20, 32, 16, 2))
        d.shape(roof, rrect(x - 1, -23, 34, 4, 2), shadow=False)
        for wx in range(3):
            d.shape("light", rrect(x + 4 + wx * 9, -16, 6, 5, 1), shadow=False)
        d.marks("dark", circle(x + 7, -2, 3) + circle(x + 25, -2, 3))
    d.shape(roof, "M-40 -26 H-22 V-22 H-40Z")
    d.shape(body, "M-40 -22 H-24 V-4 H-40Z")
    d.shape(body, rrect(-26, -16, 24, 12, 3))
    d.shape(roof, "M-10 -16 V-26 H-14 V-29 H-3 V-26 H-7 V-16Z")
    d.marks("dark", circle(-34, -2, 4) + circle(-22, -2, 4) + circle(-8, -2, 2.6))


def viaduct_path(y0: float, n: int, x0: float, span: float, pier: float) -> str:
    s = f"M-30 {y0} H230 V230 H-30Z"
    for i in range(n):
        x = x0 + i * (span + pier)
        r = span / 2
        s += f" M{x} 230 V{y0 + 14 + r} A{r} {r} 0 0 1 {x + span} {y0 + 14 + r} V230Z"
    return s


@framed
def scenic_viaduct(d: Drawing):
    d.disc("glow", 52, 58, 16)
    d.band("far", "M-30 112 L20 70 L44 86 L84 46 L122 82 L150 64 L196 98 L230 90")
    d.shape("light", "M84 46 L96 58 L90 57 L84 62 L78 56 L73 59Z", shadow=False)
    d.shape("light", "M150 64 L160 73 L154 72 L149 76 L144 71Z", shadow=False)
    d.band("mid", hills(140, 10, -20))
    d.shape("ground", viaduct_path(118, 7, -16, 22, 8), extra=EVENODD, spot=False)
    d.shape("light", "M-30 118 H230 V122 H-30Z", shadow=False, line=False)
    group(d, "translate(170 118)", lambda: small_train(d))
    d.band("deep", waves(178, 3, 30), line=False)
    d.band("near", "M-30 170 Q20 160 60 172 Q120 186 230 166", line=True)
    for x, y, s in [(14, 172, 0.9), (30, 176, 0.7), (176, 168, 0.8)]:
        d.shape("dark", pine(x, y, s), shadow=False)


@framed
def scenic_alpine(d: Drawing):
    d.disc("glow", 150, 52, 16)
    d.band("far", "M-30 104 L12 64 L40 82 L74 36 L112 80 L146 58 L182 86 L230 70")
    for snow in ["M74 36 L88 54 L81 52 L75 58 L68 51 L62 54Z", "M12 64 L22 77 L16 75 L11 80 L5 74Z",
                 "M146 58 L157 71 L151 70 L146 75 L141 69 L136 71Z"]:
        d.shape("light", snow, shadow=False)
    d.band("mid", "M-30 150 L30 132 Q100 112 230 92")

    def train():
        d.stroke("dark", "M-40 0 H200", 2.6)
        for x in (-6, 58, 122):
            d.shape("hero", rrect(x, -26, 60, 22, 5))
            d.shape("light", rrect(x + 5, -21, 50, 9, 3), shadow=False)
            d.stroke("hero", f"M{x + 22} -21 V-12 M{x + 38} -21 V-12", 2.2)
            d.shape("hero2", rrect(x + 2, -9, 56, 3, 1.5), shadow=False, spot=True)
            d.marks("dark", circle(x + 12, -2, 3.4) + circle(x + 48, -2, 3.4))
        d.stroke("dark", "M150 -26 L156 -34 L162 -26 M148 -34 H164", 1.4)
    group(d, "translate(26 136) rotate(-15)", train)
    d.band("near", "M-30 172 Q60 150 230 128", line=False)
    for x, y, s in [(26, 170, 1.0), (44, 166, 0.8), (150, 150, 0.9), (168, 144, 1.1), (186, 140, 0.8)]:
        d.shape("deep", pine(x, y, s), shadow=False)
    d.band("light", hills(186, 5, 10), line=False)


# ================================================================ TUK-TUK
def palm(d: Drawing, x: float, y: float, s: float = 1.0, role="dark", lean=6):
    """A palm tree whose trunk base is at (x, y)."""
    tx, ty = x + lean * s, y - 62 * s
    d.limb(role, f"M{x} {y} Q{x + lean * 0.2 * s} {y - 34 * s} {tx} {ty}", 4.5 * s)
    for dx, dy, cx, cy in [(-26, 10, -14, -8), (26, 12, 14, -8), (-20, -10, -12, -14), (22, -8, 12, -14), (-4, 18, -6, 4), (6, 20, 8, 4)]:
        d.shape(role, f"M{tx} {ty} Q{tx + cx * s} {ty + cy * s} {tx + dx * s} {ty + dy * s} "
                      f"Q{tx + cx * 0.6 * s} {ty + cy * 0.2 * s} {tx} {ty + 2 * s}Z", shadow=False)


def tuktuk_side(d: Drawing):
    """Side-on tuk-tuk facing right; wheels sit on y=150."""
    for x in (40, 104):
        post(d, "dark", x, 62, 104, 4, shadow=False)
    d.shape("hero2", rrect(44, 80, 40, 26, 5), shadow=False)
    d.marks("dark", circle(117, 81, 6.5))
    d.shape("dark", "M108 106 Q108 90 117 90 Q126 90 128 106Z", shadow=False)
    d.shape("light", "M134 64 H146 L154 104 H142Z", shadow=False)
    d.stroke("dark", "M132 62 L142 106", 2.6)
    d.shape("hero", "M30 100 H128 Q144 100 152 110 L162 130 Q164 136 158 136 H132 L126 130 H34 Q30 130 30 124Z")
    d.shape("dark", "M38 128 H128 L132 134 H38Z", shadow=False)
    d.shape("hero2", "M32 64 Q30 50 48 48 H138 Q150 48 152 58 V64Z")
    d.shape("pop", "M32 64 H152 V69 H32Z", shadow=False, spot=True)
    for x in range(35, 150, 9):
        d.marks("pop", f"M{x} 68 h6 l-3 4.5Z")
    d.shape("pop", "M31 112 H156 V117 H31Z", shadow=False, spot=True)
    d.stroke("dark", "M124 96 L136 90", 2.6)
    d.shape("glow2", circle(156, 112, 4.5), shadow=False)
    d.stroke("dark", "M132 136 A15 15 0 0 1 160 134", 3)
    wheel(d, 64, 138, 12)
    wheel(d, 146, 140, 10)


@framed
def tuktuk_ride(d: Drawing):
    d.disc("glow", 64, 70, 24)
    d.band("far", "M-30 120 H20 V108 H40 V100 H62 V112 H90 V96 L100 86 L110 96 V114 H140 V104 H168 V114 H230")
    palm(d, 172, 136, 1.0, "dark", 4)
    d.band("ground", "M-30 146 H230")
    for y, x0, x1 in [(100, 4, 26), (114, -4, 22), (128, 6, 28)]:
        d.stroke("light", f"M{x0} {y} H{x1}", 3, line=False)
    group(d, "translate(14 4)", lambda: tuktuk_side(d))
    d.band("deep", hills(176, 4, 20), line=False)


@framed
def tuktuk_front(d: Drawing):
    d.disc("glow", 100, 70, 46)
    d.band("far", "M-30 110 H20 V80 H44 V96 H60 V110 H140 V90 H156 V74 H182 V110 H230")
    d.band("mid", "M-30 132 L70 114 H130 L230 132")
    # lantern string
    d.stroke("dark", "M-10 30 Q100 66 210 30", 1.4)
    for i, x in enumerate([22, 48, 152, 178]):
        y = 30 + 36 * (1 - ((x - 100) / 110) ** 2) - 1
        d.shape(["pop", "hero2"][i % 2], ellipse(x, y + 7, 5.5, 7), shadow=False, spot=i % 2 == 0)
    # tuk-tuk
    d.shape("dark", rrect(38, 134, 14, 26, 5))
    d.shape("dark", rrect(148, 134, 14, 26, 5))
    post(d, "dark", 50, 64, 112, 5, shadow=False)
    post(d, "dark", 150, 64, 112, 5, shadow=False)
    d.shape("light", "M62 66 H138 L142 104 H58Z", shadow=False)
    d.marks("dark", circle(100, 80, 7))
    d.shape("dark", "M88 104 Q88 90 100 90 Q112 90 112 104Z", shadow=False)
    d.stroke("dark", "M76 98 Q100 92 124 98", 2.6)
    d.shape("hero", "M40 102 H160 L164 140 Q100 152 36 140Z")
    d.shape("hero2", "M76 104 H124 L128 160 H72Z", spot=True)
    d.shape("dark", rrect(88, 150, 24, 18, 5))
    d.shape("dark", circle(100, 122, 11), shadow=False)
    d.shape("glow2", circle(100, 122, 7.5), shadow=False)
    d.shape("pop", "M40 128 H72 L72.5 133 H39.5Z M128 128 H160 L160.5 133 H127.5Z", shadow=False)
    d.shape("hero2", "M34 64 H166 V56 Q166 44 152 42 Q100 34 48 42 Q34 44 34 56Z")
    d.shape("pop", "M34 64 H166 V70 H34Z", shadow=False, spot=True)
    for x in range(38, 164, 9):
        d.marks("pop", f"M{x} 69 h6 l-3 4.5Z")
    for x, k in [(54, -1), (146, 1)]:
        d.stroke("dark", f"M{x} 72 L{x + 12 * k} 66", 2)
        d.shape("dark", ellipse(x + 15 * k, 64, 5, 4), shadow=False)
    d.band("near", "M-30 160 H230", line=False)


def wat(d: Drawing, role="near", trim="hero2"):
    """A Thai temple: tiered roofs with chofa finials, centred on x=100, base at y=140."""
    d.shape(role, "M44 140 V112 H156 V140Z")
    d.shape(role, "M30 114 L70 88 H130 L170 114Z")
    d.shape(role, "M50 92 L84 62 H116 L150 92Z")
    d.shape(role, "M70 66 L100 32 L130 66Z")
    d.stroke(trim, "M30 114 L70 88 M170 114 L130 88 M50 92 L84 62 M150 92 L116 62 M70 66 L100 32 L130 66", 2.4)
    d.stroke(trim, "M30 114 Q24 110 26 104 M170 114 Q176 110 174 104 M50 92 Q44 88 46 82 M150 92 Q156 88 154 82", 2.4)
    d.stroke(trim, "M100 32 V18", 2.4)
    for x in (60, 84, 116, 140):
        d.marks("dark", f"M{x - 5} 140 V124 Q{x} 116 {x + 5} 124 V140Z")


@framed
def tuktuk_temple(d: Drawing):
    d.disc("glow", 100, 76, 52)
    group(d, "translate(20 2) scale(.8)", lambda: wat(d))
    palm(d, 24, 150, 0.9, "dark", -6)
    palm(d, 182, 150, 0.8, "dark", 6)
    d.band("ground", "M-30 140 Q100 134 230 140")
    group(d, "translate(26 50) scale(.72)", lambda: tuktuk_side(d))
    d.band("deep", hills(178, 4, 30), line=False)


# ================================================================ FERRY
def ferry(d: Drawing):
    """Side-on car ferry facing right, waterline y=140."""
    d.stroke("dark", "M126 64 V48 M126 52 L140 58 L126 58", 1.6)
    d.shape("hero2", "M88 82 L92 56 H110 L113 82Z", spot=True)
    d.shape("pop", "M90.5 64 H111 V70 H89.6Z", shadow=False)
    d.shape("light", rrect(42, 98, 128, 22, 3))
    d.shape("light", rrect(62, 80, 92, 20, 3))
    d.shape("light", rrect(114, 66, 36, 16, 3))
    d.marks("dark", rrect(118, 70, 28, 5, 2))
    for x in range(68, 150, 10):
        d.marks("dark", rrect(x, 86, 6, 5, 1.5))
    for x in range(48, 166, 9):
        d.marks("dark", rrect(x, 105, 5, 6, 1.5))
    d.shape("pop", rrect(68, 94, 16, 6, 3), shadow=False)
    d.shape("pop", rrect(124, 94, 16, 6, 3), shadow=False)
    d.shape("hero", "M24 118 H184 Q180 132 168 144 H40 Q30 134 24 118Z")
    d.shape("light", "M26 124 H182 L180 128 H28Z", shadow=False)
    d.stroke("dark", "M150 132 V142 M150 132 H164", 1.2)


@framed
def ferry_crossing(d: Drawing):
    d.disc("glow", 100, 86, 64)
    d.band("far", "M-30 112 Q10 96 44 108 L230 116")
    d.stroke("dark", "M150 36 q4 -4 8 0 q4 -4 8 0 M28 56 q3 -3 6 0 q3 -3 6 0", 1.8)
    group(d, "translate(0 4)", lambda: ferry(d))
    d.band("mid", waves(146, 3, 22))
    d.shape("light", "M164 146 Q178 140 186 128 Q192 140 196 146Z", shadow=False)
    d.stroke("light", "M20 154 H60 M90 160 H140 M30 168 H70", 2.4, line=False)
    d.band("near", waves(172, 4, 30))
    d.band("deep", waves(190, 3, 34), line=False)


def lighthouse(d: Drawing, tower="light", band="pop"):
    """Lighthouse centred on x=0, base y=0, top y=-96."""
    d.shape(tower, "M-14 0 L-9 -70 H9 L14 0Z")
    d.shape(band, "M-12.4 -24 L-11.3 -40 H11.3 L12.4 -24Z M-10.3 -54 L-9.6 -66 H9.6 L10.3 -54Z", shadow=False, spot=True)
    d.shape("dark", rrect(-14, -74, 28, 6, 2))
    d.shape("glow2", rrect(-8, -88, 16, 14, 2))
    d.stroke("dark", "M-8 -81 H8 M0 -88 V-74", 1.6)
    d.shape(band, "M-10 -88 L0 -98 L10 -88Z")
    d.marks("dark", rrect(-3, -14, 6, 10, 3))


@framed
def ferry_lighthouse(d: Drawing):
    d.raw('<g opacity=".35"><path d="M40 52 L-30 30 L-30 64Z" fill="#fff"/><path d="M40 52 L230 18 L230 60Z" fill="#fff"/></g>', "")
    d.disc("glow", 160, 64, 16)
    d.shape("near", "M-30 148 L-30 104 Q-6 96 18 104 Q52 100 76 122 Q92 132 100 150Z")
    d.shape("mid", "M-30 150 L-30 122 Q10 114 40 124 Q62 132 72 152Z", shadow=False)
    group(d, "translate(40 110) scale(.6)", lambda: lighthouse(d))
    d.band("far", waves(140, 3, 26))
    group(d, "translate(118 64) scale(.46)", lambda: ferry(d))
    d.stroke("light", "M120 132 Q100 136 80 136", 2.4, line=False)
    d.stroke("dark", "M120 38 q4 -4 8 0 q4 -4 8 0 M140 46 q3 -3 6 0 q3 -3 6 0", 1.8)
    d.band("mid", waves(158, 4, 28))
    d.band("near", waves(178, 4, 32))


@framed
def ferry_lifering(d: Drawing):
    d.disc("glow", 150, 58, 16)
    d.band("far", "M-30 92 Q40 72 80 88 Q110 98 140 92 L230 96")
    d.band("mid", waves(100, 3, 24))
    d.band("near", waves(128, 3, 30), line=False)
    d.stroke("dark", "M30 56 q4 -4 8 0 q4 -4 8 0", 1.8)
    # railing
    d.shape("dark", rrect(-30, 61, 260, 6, 3))
    d.shape("dark", rrect(-30, 158, 260, 5, 2.5))
    d.stroke("hero2", "M88 66 Q86 54 100 56 Q114 54 112 66", 3)
    # ring
    ring = f"{circle(100, 112, 48)} {circle(100, 112, 22)}"
    d.shape("light", ring, extra=EVENODD)
    for a in (45, 135, 225, 315):
        d.shape("pop", "M100 64 A48 48 0 0 1 116.4 66.9 L107.5 91.3 A22 22 0 0 0 100 90Z",
                shadow=False, spot=True, extra=f'transform="rotate({a - 10} 100 112)"')
    for a in (0, 90, 180, 270):
        d.shape("hero2", rrect(96, 61, 8, 30, 4), shadow=False, extra=f'transform="rotate({a} 100 112)"')
    d.stroke("dark", circle(100, 112, 48), 1.2, line=False)


# ================================================================ CABLE CAR
def cabin(d: Drawing, body="hero", trim="hero2"):
    """Aerial tram cabin hanging from a carriage at (100, 34) on a cable sloping up to the right."""
    d.stroke("dark", "M-30 56 L230 12", 2.4)
    d.stroke("dark", "M-30 66 L230 22", 1.6)
    group(d, "rotate(-9.6 100 34)", lambda: (d.shape("dark", rrect(78, 30, 44, 12, 4)),
                                             d.marks("light", circle(86, 36, 2.6) + circle(100, 36, 2.6) + circle(114, 36, 2.6))))
    post(d, "dark", 100, 40, 80, 6)
    d.shape("dark", "M70 84 Q72 74 84 74 H116 Q128 74 130 84Z")
    d.shape(body, "M58 92 Q58 82 70 82 H130 Q142 82 142 92 L138 138 Q137 146 128 146 H72 Q63 146 62 138Z")
    d.shape("light", "M64 92 H136 L134 118 H66Z", shadow=False)
    d.stroke(body, "M88 92 V118 M112 92 V118", 3)
    d.shape(trim, "M65 124 H135 L134.6 130 H65.4Z", shadow=False, spot=True)
    d.shape("dark", rrect(70, 144, 60, 5, 2.5), shadow=False)


@framed
def cablecar_valley(d: Drawing):
    d.disc("glow", 46, 92, 16)
    d.band("far", "M-30 140 L16 100 L40 116 L76 76 L106 112 L140 86 L176 118 L230 98")
    d.shape("light", "M76 76 L88 90 L82 88 L77 93 L71 87 L66 89Z", shadow=False)
    d.shape("light", "M140 86 L150 98 L144 96 L139 101 L134 96Z", shadow=False)
    d.band("mid", "M-30 160 Q40 136 100 150 Q150 160 230 140")
    for x, y, s in [(30, 160, 0.7), (44, 158, 0.6), (160, 154, 0.7), (174, 150, 0.6)]:
        d.shape("near", pine(x, y, s), shadow=False)
    d.band("near", "M-30 178 Q60 164 100 176 T230 172")
    cabin(d)


def pylon(d: Drawing, x: float, y: float, h: float):
    w0, w1 = h * 0.16, h * 0.05
    d.shape("dark", f"M{x - w0} {y} L{x - w1} {y - h} H{x + w1} L{x + w0} {y}Z M{x - w0 + 3} {y - 2} L{x - w1 + 1} {y - h + 6} L{x + w0 - 3} {y - 2}Z", extra=EVENODD)
    d.shape("dark", rrect(x - h * 0.2, y - h - 4, h * 0.4, 5, 2))


def mini_cabin(d: Drawing, x: float, y: float, role: str, spot=False):
    d.stroke("dark", f"M{x} {y} V{y + 9}", 1.8)
    d.shape(role, rrect(x - 8, y + 9, 16, 15, 4), spot=spot)
    d.shape("light", rrect(x - 5.5, y + 12, 11, 6, 2), shadow=False)


@framed
def cablecar_pylons(d: Drawing):
    d.disc("glow", 150, 48, 16)
    d.band("far", "M-30 96 L20 60 L52 80 L92 36 L130 74 L160 56 L230 92")
    for snow in ["M92 36 L104 50 L98 48 L92 54 L86 48 L80 50Z", "M20 60 L30 72 L24 70 L19 75 L13 70Z", "M160 56 L170 67 L164 66 L159 71 L154 66Z"]:
        d.shape("light", snow, shadow=False)
    d.band("mid", "M-30 190 L230 82")
    pylon(d, 118, 132, 54)
    d.stroke("dark", "M-30 128 Q50 92 106 80 Q160 70 230 34", 1.8)
    d.stroke("dark", "M-30 140 Q50 104 130 80 Q180 66 230 46", 1.4)
    for x, y, role, sp in [(34, 104, "hero", True), (160, 63, "pop", False), (178, 72, "hero2", False), (70, 104, "hero2", False)]:
        mini_cabin(d, x, y, role, sp)
    for x, y, s in [(26, 182, 1.1), (46, 180, 0.9), (64, 172, 0.8), (166, 132, 0.9), (184, 124, 1.0)]:
        d.shape("near", pine(x, y, s), shadow=False)


def tram(d: Drawing):
    """San Francisco-style cable car facing right, wheels on y=0, x from -60 to 60."""
    d.shape("hero", "M-58 -46 H58 Q62 -46 62 -42 V-38 H-62 V-42 Q-62 -46 -58 -46Z")
    d.shape("hero2", rrect(-56, -38, 112, 6, 1), shadow=False, spot=True)
    for x in (-54, -26, 26, 54):
        post(d, "dark", x, -32, -14, 3, shadow=False)
    d.shape("light", rrect(-22, -32, 44, 16, 2))
    for x in (-12, 0, 12):
        d.stroke("dark", f"M{x} -32 V-16", 1.4)
    d.shape("hero", "M-60 -16 H60 V-6 Q60 -2 56 -2 H-56 Q-60 -2 -60 -6Z")
    d.shape("hero2", rrect(-60, -12, 120, 3, 1.5), shadow=False, spot=True)
    d.shape("dark", "M-62 -4 H62 V0 H-62Z", shadow=False)
    d.marks("dark", circle(-36, 2, 5) + circle(36, 2, 5))
    d.marks("glow2", circle(60, -26, 3))


@framed
def cablecar_tram(d: Drawing):
    d.disc("glow", 150, 46, 16)
    d.band("far", waves(84, 2, 20))
    slope = lambda x: 190 - 0.362 * (x + 30)
    roles = ["mid", "hero2", "near", "light", "mid", "hero2", "near"]
    for i, x in enumerate(range(-30, 230, 34)):
        yb = slope(x + 34) - 6
        top = yb - 70
        role = roles[i % len(roles)]
        d.shape(role, f"M{x} {yb + 40:.1f} V{top:.1f} L{x + 17} {top - 12:.1f} L{x + 34} {top:.1f} V{yb + 40:.1f}Z")
        d.marks("dark", rrect(x + 6, top + 8, 8, 12, 2) + rrect(x + 20, top + 8, 8, 12, 2) + rrect(x + 13, top - 6, 8, 6, 2))
    d.band("ground", f"M-30 {slope(-30) + 2:.1f} L230 {slope(230) + 2:.1f}")
    d.stroke("dark", f"M-30 {slope(-30) + 8:.1f} L230 {slope(230) + 8:.1f}", 1.6)
    group(d, f"translate(100 {slope(100) + 2:.1f}) rotate(-19.9) scale(1.12)", lambda: tram(d))
    d.band("deep", f"M-30 {slope(-30) + 26:.1f} L230 {slope(230) + 26:.1f}", line=False)

# ================================================================ GONDOLA
GONDOLA = "M22 126 Q30 150 64 150 H146 Q170 150 176 124 Q170 140 154 141 H50 Q34 141 22 126Z"
FERRO = ("M170 128 L172 96 Q172 86 182 84 Q190 84 192 90 L186 91 Q182 89 180 94 L178 128Z "
         "M178 100 h9 v3.5 h-9Z M178 107 h9 v3.5 h-9Z M178 114 h9 v3.5 h-9Z M178 121 h8 v3.5 h-8Z")


def gondola(d: Drawing, hull="dark", seat="pop"):
    """Gondola facing right, waterline y=146."""
    d.shape(seat, rrect(88, 130, 34, 12, 4), spot=True)
    d.shape("hero2", rrect(84, 126, 6, 16, 2), shadow=False)
    d.shape(hull, GONDOLA)
    d.stroke("hero2", "M48 144 H150", 1.6)
    d.shape("light", FERRO)
    d.shape("light", "M22 126 L18 118 L26 122Z", shadow=False)


def gondolier(d: Drawing, x: float = 44, y: float = 141):
    """Simple gondolier standing on the stern at (x, y): striped shirt, straw boater, oar."""
    d.limb("dark", f"M{x + 22} {y - 56} L{x - 22} {y + 22}", 3.4, shadow=False)
    d.limb("dark", f"M{x - 4} {y} L{x - 2} {y - 22} M{x + 5} {y} L{x + 3} {y - 22}", 5)
    d.shape("light", rrect(x - 9, y - 50, 18, 30, 6))
    for k in range(4):
        d.shape("pop", rrect(x - 9, y - 45 + k * 7, 18, 3, 1), shadow=False, spot=True)
    d.limb("dark", f"M{x + 5} {y - 44} L{x + 15} {y - 38}", 4.4, shadow=False)
    d.marks("dark", circle(x, y - 57, 6.5))
    d.shape("hero2", ellipse(x, y - 61, 11, 2.6))
    d.shape("hero2", rrect(x - 6.5, y - 70, 13, 9, 2), shadow=False)
    d.shape("pop", rrect(x - 6.5, y - 65, 13, 2.6, 1), shadow=False)


def venice_houses(d: Drawing):
    d.shape("far", "M-30 160 V36 H22 V160Z")
    d.shape("near", "M178 160 V48 H230 V160Z")
    for y in (52, 84, 116):
        d.marks("dark", f"M2 {y + 16} V{y + 6} Q7 {y} 12 {y + 6} V{y + 16}Z")
    for y in (64, 96, 128):
        d.marks("dark", f"M188 {y + 16} V{y + 6} Q193 {y} 198 {y + 6} V{y + 16}Z")


@framed
def gondola_bridge(d: Drawing):
    d.disc("glow", 100, 52, 18)
    d.band("mid", "M-30 118 H40 V92 L50 84 L60 92 V100 H84 V70 H98 V60 L104 50 L110 60 V70 H118 V100 H140 V88 H170 V118 H230")
    for x, y in [(44, 98), (64, 104), (122, 92), (150, 96)]:
        d.marks("near", rrect(x, y, 6, 9, 2))
    venice_houses(d)
    d.band("far", waves(118, 2, 22))
    d.shape("ground", "M22 120 Q100 58 178 120 V128 H164 Q100 82 36 128 H22Z")
    d.stroke("dark", "M30 112 Q100 52 170 112", 2)
    for t in [0.12, 0.25, 0.38, 0.5, 0.62, 0.75, 0.88]:
        x = 22 + 156 * t
        y = (1 - t) ** 2 * 113 + 2 * (1 - t) * t * 51 + t * t * 113
        d.stroke("dark", f"M{x:.1f} {y:.1f} V{y + 8:.1f}", 1.6)
    d.band("mid", waves(136, 3, 22))
    group(d, "translate(8 18) scale(.92)", lambda: (gondola(d), gondolier(d)))
    d.band("near", waves(168, 3, 28))
    d.band("deep", waves(186, 3, 32), line=False)


@framed
def gondola_gondolier(d: Drawing):
    d.disc("glow", 92, 104, 46)
    d.band("far", "M-30 120 H20 V104 H34 V58 L40 44 L46 58 V104 H60 V112 H120 V100 Q120 82 136 82 Q152 82 152 100 V108 H170 V114 H230")
    d.marks("glow2", rrect(37, 64, 6, 10, 2))
    d.stroke("far", "M136 82 V72", 2.4)
    d.band("mid", waves(128, 3, 24))
    group(d, "translate(100 100) scale(1.28) translate(-100 -110)", lambda: (gondola(d), gondolier(d, 46, 141)))
    d.band("near", waves(168, 3, 30))
    d.band("deep", waves(186, 3, 34), line=False)


def mooring_pole(d: Drawing, x: float, y0: float, y1: float, role="pop"):
    d.shape("light", rrect(x - 4, y0, 8, y1 - y0, 3))
    yy = y0 + 8
    while yy < y1 - 6:
        d.shape(role, f"M{x - 4} {yy + 6} L{x + 4} {yy} V{yy + 5} L{x - 4} {yy + 11}Z", shadow=False, spot=True)
        yy += 14
    d.shape(role, f"M{x - 5} {y0 + 2} Q{x} {y0 - 8} {x + 5} {y0 + 2}Z")


@framed
def gondola_prow(d: Drawing):
    d.disc("glow", 64, 62, 18)
    d.band("far", "M-30 112 H60 V104 Q60 88 76 86 V78 H80 V86 Q96 88 96 104 V112 H140 V60 L146 50 L152 60 V112 H230")
    d.band("mid", waves(116, 3, 22))
    for x, y0, role in [(30, 70, "pop"), (48, 84, "hero"), (176, 76, "pop")]:
        mooring_pole(d, x, y0, 150, role)
    d.band("near", waves(144, 3, 28))
    d.shape("dark", "M-30 186 Q60 184 104 156 Q118 146 124 130 L136 132 Q132 160 112 176 Q80 198 -30 204Z")
    d.stroke("hero2", "M-30 194 Q60 190 106 164 Q120 152 128 138", 2)
    def ferro():
        d.shape("light", "M118 140 L122 66 Q124 48 142 46 Q158 46 162 58 L152 60 Q146 54 138 60 Q134 64 134 72 L132 140Z")
        for y in range(76, 132, 11):
            d.shape("light", f"M132 {y} H150 Q154 {y + 3} 150 {y + 6} H132Z", shadow=False)
        d.shape("light", "M120 124 H108 Q104 127 108 130 H120Z", shadow=False)
    ferro()
    d.band("deep", waves(190, 3, 34), line=False)


# ================================================================ CAMPERVAN
def camper(d: Drawing, body="hero", top="hero2"):
    """Side-on camper van facing right, wheels on y=150."""
    d.shape("pop", "M40 52 Q90 42 150 52 Q90 58 40 52Z", spot=True)
    d.stroke("dark", "M56 52 V58 M134 52 V58", 2.4)
    d.shape(body, "M30 78 Q30 58 52 58 H146 Q164 58 170 74 L176 116 Q178 136 164 136 H40 Q30 136 30 126Z")
    d.shape(top, "M31 100 V78 Q31 59 52 59 H146 Q163 59 169 74 L173 100Z", shadow=False)
    for x in (42, 76, 110):
        d.shape("light", rrect(x, 66, 28, 22, 5), shadow=False)
    d.shape("light", "M146 66 H156 Q164 66 166 76 L168 88 H146Z", shadow=False)
    d.stroke(body, "M140 102 V130 M104 102 V130", 1.6)
    d.shape("dark", rrect(106, 108, 8, 3, 1.5), shadow=False)
    d.shape("glow2", ellipse(174, 104, 3, 5), shadow=False)
    d.shape("dark", rrect(166, 128, 16, 6, 3), shadow=False)
    d.shape("dark", rrect(24, 128, 12, 6, 3), shadow=False)
    for x in (62, 144):
        d.marks("dark", f"M{x - 18} 136 A18 18 0 0 1 {x + 18} 136Z")
        wheel(d, x, 137, 13)


@framed
def camper_beach(d: Drawing):
    d.disc("glow", 100, 100, 54)
    d.band("far", waves(124, 2, 22))
    d.band("ground", "M-30 146 Q100 138 230 148")
    palm(d, 182, 146, 1.0, "dark", -8)
    group(d, "translate(100 100) scale(.9) translate(-104 -102)", lambda: camper(d))
    d.band("deep", hills(180, 4, 20), line=False)


@framed
def camper_front(d: Drawing):
    d.disc("glow", 150, 56, 16)
    d.band("far", "M-30 120 L20 86 L52 104 L96 62 L140 104 L172 84 L230 116")
    d.band("mid", "M-30 140 Q100 118 230 140")
    for x, y, s in [(22, 138, 1.0), (178, 138, 1.0), (192, 134, 0.7)]:
        d.shape("near", pine(x, y, s), shadow=False)
    d.shape("ground", "M84 126 H116 L190 210 H10Z", shadow=False, line=False)
    # roof rack + bags
    d.shape("pop", rrect(62, 28, 34, 12, 4), spot=True)
    d.shape("hero", rrect(98, 26, 36, 14, 4))
    d.stroke("dark", "M58 42 H142", 2.6)
    # van
    d.shape("dark", rrect(54, 150, 20, 22, 5))
    d.shape("dark", rrect(126, 150, 20, 22, 5))
    d.shape("hero", "M48 72 Q48 44 78 42 H122 Q152 44 152 72 V148 Q152 158 142 158 H58 Q48 158 48 148Z")
    d.shape("hero2", "M48 72 Q48 44 78 42 H122 Q152 44 152 72 V104 H124 L100 128 L76 104 H48Z", shadow=False, spot=True)
    d.shape("light", rrect(57, 54, 40, 32, 7), shadow=False)
    d.shape("light", rrect(103, 54, 40, 32, 7), shadow=False)
    d.shape("light", circle(100, 106, 7), shadow=False)
    d.stroke("hero", circle(100, 106, 4), 1.6, line=False)
    for x in (66, 134):
        d.shape("dark", circle(x, 130, 10), shadow=False)
        d.shape("glow2", circle(x, 130, 7), shadow=False)
    d.shape("dark", rrect(42, 148, 116, 9, 4))
    for x, k in [(48, -1), (152, 1)]:
        d.stroke("dark", f"M{x} 92 L{x + 8 * k} 86", 2)
        d.shape("dark", rrect(x + 5 * k - 4 if k > 0 else x - 13, 80, 8, 10, 3), shadow=False)


def campfire(d: Drawing, x: float, y: float):
    d.limb("dark", f"M{x - 12} {y} L{x + 12} {y - 5} M{x - 12} {y - 5} L{x + 12} {y}", 4)
    d.shape("pop", f"M{x} {y - 30} C{x + 10} {y - 18} {x + 12} {y - 10} {x + 8} {y - 4} H{x - 8} C{x - 12} {y - 10} {x - 8} {y - 20} {x} {y - 30}Z", spot=True)
    d.shape("glow2", f"M{x} {y - 18} C{x + 5} {y - 12} {x + 6} {y - 8} {x + 4} {y - 4} H{x - 4} C{x - 6} {y - 8} {x - 4} {y - 13} {x} {y - 18}Z", shadow=False)


@framed
def camper_camp(d: Drawing):
    d.disc("glow", 150, 50, 14)
    for x, y in [(40, 40), (70, 28), (110, 46), (178, 76), (30, 74)]:
        d.marks("light", f"M{x} {y - 3} L{x + 1} {y - 1} L{x + 3} {y} L{x + 1} {y + 1} L{x} {y + 3} L{x - 1} {y + 1} L{x - 3} {y} L{x - 1} {y - 1}Z")
    d.band("far", "M-30 110 L10 82 L40 98 L80 60 L120 100 L150 84 L230 112")
    d.band("mid", hills(126, 6, 20))
    for x, y, s in [(10, 130, 1.3), (28, 128, 1.0), (186, 128, 1.2)]:
        d.shape("near", pine(x, y, s), shadow=False)
    d.band("ground", "M-30 150 Q100 140 230 150")
    group(d, "translate(14 40) scale(.62)", lambda: camper(d))
    post(d, "dark", 146, 92, 148, 2.6, shadow=False)
    d.stroke("dark", "M108 80 Q128 98 146 92", 1)
    for i, t in enumerate([0.15, 0.35, 0.55, 0.75, 0.92]):
        x = (1 - t) ** 2 * 108 + 2 * (1 - t) * t * 128 + t * t * 146
        y = (1 - t) ** 2 * 80 + 2 * (1 - t) * t * 98 + t * t * 92
        d.marks(["glow2", "pop"][i % 2], circle(round(x, 1), round(y + 2.5, 1), 2))
    campfire(d, 162, 156)
    d.band("deep", hills(182, 4, 20), line=False)


# ================================================================ MOTORBIKE
def motorbike(d: Drawing, body="hero", bags="hero2"):
    """Touring motorbike facing right, wheels on y=150."""
    d.limb("dark", "M92 128 L52 132", 5)
    d.limb("dark", "M146 132 L128 76", 6)
    d.shape("light", "M124 72 L134 48 L143 51 L134 76Z", shadow=False)
    d.stroke("dark", "M128 76 L114 70", 3)
    d.marks("dark", circle(114, 70, 2.4))
    d.shape(bags, rrect(22, 96, 34, 28, 6))
    d.shape(bags, rrect(28, 78, 24, 18, 5))
    d.stroke("dark", "M39 96 V124", 1.4)
    d.shape("dark", "M88 104 H120 L124 132 H92Z")
    d.stroke("light", "M93 112 H120 M94 118 H121 M95 124 H122", 1.4, line=False)
    d.stroke("light", "M96 134 Q76 140 44 136", 4.4)
    d.stroke("dark", "M96 134 Q76 140 44 136", 1, line=False)
    d.shape(body, "M44 96 H90 L86 108 H52Z")
    d.shape("dark", "M50 96 Q56 86 86 90 L90 98 H52Z")
    d.shape(body, "M84 94 Q88 80 108 80 Q124 80 130 90 L124 104 H90Z", spot=True)
    d.shape("light", "M94 88 Q104 83 116 85", shadow=False, line=False)
    d.shape(body, circle(135, 88, 8))
    d.shape("glow2", circle(137, 88, 5), shadow=False)
    d.stroke(body, "M132 126 A17 17 0 0 1 162 124", 3.4)
    d.stroke(body, "M34 116 A20 20 0 0 1 70 116", 3.4, line=False)
    for x in (52, 146):
        wheel(d, x, 132, 18)


@framed
def moto_road(d: Drawing):
    d.disc("glow", 64, 62, 22)
    d.band("far", "M-30 104 H20 L28 82 H58 L64 104 H120 L128 86 H150 L156 104 H230")
    d.band("ground", "M-30 116 Q100 110 230 116")
    d.shape("dark", "M-30 150 H230 V172 H-30Z", line=False)
    d.raw("", "")
    group(d, "translate(100 100) scale(.96) translate(-96 -100)", lambda: motorbike(d))
    for x in range(-20, 230, 36):
        d.shape("light", rrect(x, 158, 18, 4, 2), shadow=False, line=False)
    d.band("deep", "M-30 172 H230")


@framed
def moto_helmet(d: Drawing):
    d.disc("glow", 100, 96, 70)
    d.band("far", hills(162, 6, 10))
    d.shape("hero", "M34 120 Q28 50 98 44 Q152 42 164 94 L166 110 H130 Q116 110 114 124 L112 152 H58 Q36 150 34 120Z")
    d.stroke("hero2", "M48 112 Q46 60 98 54 Q132 52 146 72", 9)
    d.stroke("hero2", "M166 110 H130 Q116 110 114 124 L112 152", 4)
    d.shape("dark", "M150 92 L184 98 Q186 104 180 106 L156 106Z")
    d.shape("dark", "M33 92 Q90 70 152 72 V86 Q90 86 35 108Z", shadow=False)
    d.shape("dark", ellipse(134, 72, 20, 15))
    d.shape("light", ellipse(134, 72, 14, 10), shadow=False, spot=True)
    d.stroke("sky2", "M126 68 Q130 64 136 64", 2.4, line=False)
    d.shape("hero2", ellipse(58, 128, 10, 13), shadow=False)
    d.stroke("dark", "M112 140 Q118 156 132 156", 2.6)
    d.shape("light", rrect(128, 152, 10, 8, 2))


@framed
def moto_pass(d: Drawing):
    d.disc("glow", 150, 48, 15)
    d.band("far", "M-30 84 L20 54 L60 76 L100 40 L150 74 L230 50")
    d.shape("light", "M100 40 L112 52 L106 51 L100 56 L94 50 L88 52Z", shadow=False)
    d.band("mid", "M-30 112 L40 80 L110 96 L230 72")
    road = "M200 82 L50 98 Q34 102 50 108 L170 118 Q190 122 170 128 L20 146 Q4 150 20 156 L230 172"
    d.limb("ground", road, 9)
    d.raw(f'<path d="{road}" fill="none" stroke="{d.c.get("light")}" stroke-width="1.2" stroke-dasharray="3 5"/>', "")
    group(d, "translate(70 82) scale(.22)", lambda: motorbike(d))
    # warning sign
    post(d, "dark", 148, 150, 196, 4)
    d.shape("light", "M148 98 L178 150 H118Z")
    d.shape("pop", "M148 98 L178 150 H118Z M148 110 L127 145 H169Z", shadow=False, spot=True, extra=EVENODD)
    d.stroke("dark", "M154 140 Q140 134 148 128 Q156 122 142 116", 3)
    d.band("near", hills(184, 6, 30), line=False)

# ================================================================ SCOOTER
def scooter(d: Drawing, body="hero", seat="dark"):
    """Vintage scooter facing right, wheels on y=150."""
    d.shape(seat, "M48 92 Q50 82 64 82 H94 Q100 82 100 88 L98 94 H50Z")
    d.limb("dark", "M138 70 L146 134", 5)
    d.shape(body, "M96 126 H130 L132 134 H96Z")
    d.shape(body, "M38 128 Q32 96 70 92 H98 Q106 92 106 102 L102 132 H44Z")
    d.shape("light", "M44 112 Q46 100 64 98 H90 Q92 106 82 110Z", shadow=False)
    d.shape(body, "M118 134 Q128 104 130 78 L142 76 Q144 104 152 124 L154 134Z")
    d.stroke("dark", "M130 66 L118 62 M140 66 L132 58", 2.6)
    d.shape("dark", circle(132, 56, 3.4) + circle(116, 61, 2.4), shadow=False)
    d.shape(body, rrect(126, 64, 26, 11, 5))
    d.shape("glow2", circle(150, 69, 4.5), shadow=False)
    d.shape("pop", "M40 120 Q60 116 100 118 L100 122 Q60 120 41 124Z", shadow=False, spot=True)
    d.shape(body, "M134 142 Q134 124 150 122 Q164 122 168 136 L162 138 Q158 130 150 130 Q142 130 140 142Z")
    wheel(d, 64, 140, 11)
    wheel(d, 150, 140, 11)


@framed
def scooter_side(d: Drawing):
    d.disc("glow", 100, 96, 62)
    d.band("far", hills(132, 8, 20))
    d.band("ground", "M-30 152 Q100 146 230 152")
    for y, x0, x1 in [(104, 14, 36), (118, 6, 32), (132, 14, 34)]:
        d.stroke("light", f"M{x0} {y} H{x1}", 3, line=False)
    group(d, "translate(100 100) scale(1.12) translate(-100 -108)", lambda: scooter(d))
    d.band("deep", hills(182, 4, 20), line=False)


def house(d: Drawing, x, y, w, h, role, shutters="hero", door=False):
    d.shape(role, f"M{x} {y + h} V{y} H{x + w} V{y + h}Z")
    d.shape("dark", f"M{x - 2} {y} H{x + w + 2} V{y + 4} H{x - 2}Z", shadow=False, line=False)
    for wx in range(int(x + 6), int(x + w - 8), 16):
        for wy in range(int(y + 10), int(y + h - 24), 22):
            d.marks("dark", rrect(wx, wy, 8, 12, 1.5))
            d.shape(shutters, f"M{wx - 3} {wy} h3 v12 h-3Z M{wx + 8} {wy} h3 v12 h-3Z", shadow=False, line=False)
    if door:
        d.marks("dark", f"M{x + w / 2 - 6} {y + h} V{y + h - 16} Q{x + w / 2} {y + h - 24} {x + w / 2 + 6} {y + h - 16} V{y + h}Z")


@framed
def scooter_street(d: Drawing):
    d.disc("glow", 100, 40, 22)
    house(d, -30, 30, 62, 130, "far", "near")
    house(d, 32, 54, 52, 106, "glow2", "near", True)
    house(d, 84, 40, 54, 120, "mid", "near")
    house(d, 138, 60, 54, 100, "far", "near", True)
    house(d, 192, 36, 50, 124, "glow2", "near")
    d.stroke("dark", "M-30 72 Q60 96 170 70", 1.2)
    for i, x in enumerate(range(0, 170, 14)):
        t = (x + 30) / 200
        d.shape(["pop", "light", "hero2"][i % 3], f"M{x - 3} {80 + 8 * (1 - (2 * t - 1) ** 2):.1f} h6 l-3 6Z", shadow=False, line=False)
    d.band("ground", "M-30 158 H230")
    for x in range(-28, 230, 14):
        d.stroke("near", f"M{x} 166 h8 M{x + 7} 176 h8", 1.4, line=False)
    group(d, "translate(100 100) scale(.84) translate(-104 -78)", lambda: scooter(d))
    d.marks("dark", ellipse(100, 160, 50, 2.4)) if False else None


@framed
def scooter_front(d: Drawing):
    d.disc("glow", 150, 50, 16)
    d.band("far", "M-30 124 Q0 66 44 80 Q66 88 76 124 H230")
    for x, y, w, h, role in [(4, 88, 14, 14, "light"), (20, 84, 12, 18, "hero2"), (34, 90, 14, 14, "light"), (12, 102, 14, 12, "pop")]:
        d.shape(role, rrect(x, y, w, h, 1.5), shadow=False, line=False)
        d.marks("dark", rrect(x + w / 2 - 2, y + 4, 4, 5, 1))
    d.band("mid", waves(124, 2, 24))
    d.band("near", waves(150, 3, 30), line=False)
    # scooter head-on: leg shield, then wheel and mudguard in front of it
    d.shape("hero", "M64 150 Q58 110 76 80 H124 Q142 110 136 150 Q100 158 64 150Z")
    d.shape("dark", "M94 86 L106 86 L102 106 H98Z", shadow=False)
    d.shape("pop", "M66 134 Q100 140 134 134 L135 140 Q100 146 65 140Z", shadow=False, spot=True)
    d.shape("dark", rrect(89, 140, 22, 36, 9))
    d.shape("hero", "M82 156 Q82 128 100 128 Q118 128 118 156 V160 H82Z")
    d.stroke("dark", "M100 80 V62", 4)
    d.stroke("dark", "M44 64 Q72 68 100 64 Q128 68 156 64", 4)
    d.shape("dark", rrect(34, 60, 14, 8, 4), shadow=False)
    d.shape("dark", rrect(152, 60, 14, 8, 4), shadow=False)
    for x, k in [(60, -1), (140, 1)]:
        d.stroke("dark", f"M{x} 64 L{x + 8 * k} 46", 2.2)
        d.shape("light", circle(x + 9 * k, 42, 6))
    d.shape("hero", "M78 60 Q78 46 100 46 Q122 46 122 60 V72 Q100 80 78 72Z")
    d.shape("dark", circle(100, 61, 10), shadow=False)
    d.shape("glow2", circle(100, 61, 7), shadow=False)
    d.band("ground", "M-30 174 Q100 168 230 174")


# ================================================================ CRUISE SHIP
def liner(d: Drawing):
    """Cruise ship facing right, waterline y=140."""
    d.shape("pop", "M118 62 L120 40 Q120 34 128 34 H142 Q148 34 146 40 L140 62Z", spot=True)
    d.shape("dark", "M119 44 H146 L145 48 H119Z", shadow=False)
    d.shape("light", "M44 112 V86 Q44 80 50 80 H156 L164 112Z")
    d.shape("light", "M58 80 V70 Q58 64 64 64 H150 L156 80Z")
    d.shape("light", rrect(70, 54, 52, 12, 3))
    d.shape("dark", "M150 68 H156 L158 76 H150Z", shadow=False)
    for y, x0, x1 in [(70, 64, 148), (86, 50, 152), (98, 50, 158)]:
        for x in range(x0, x1, 7):
            d.marks("hero", rrect(x, y, 4.4, 5, 1))
    for x in range(54, 150, 22):
        d.shape("hero2", rrect(x, 104, 14, 6, 3), shadow=False)
    d.shape("hero", "M14 110 H180 L192 108 Q186 128 172 144 H34 Q22 134 14 110Z")
    d.shape("light", "M18 120 H186 L184 124 H20Z", shadow=False)
    for x in range(32, 170, 9):
        d.marks("light", circle(x, 132, 1.6))


@framed
def cruise_liner(d: Drawing):
    d.disc("glow", 152, 64, 18)
    d.shape("light", cloud(20, 54, 0.9), shadow=False)
    d.band("far", "M-30 112 Q0 98 26 108 L230 116")
    d.stroke("dark", "M30 28 q4 -4 8 0 q4 -4 8 0 M48 38 q3 -3 6 0 q3 -3 6 0", 1.8)
    group(d, "translate(100 100) scale(.98) translate(-100 -96)", lambda: liner(d))
    d.band("mid", waves(146, 3, 22))
    d.stroke("light", "M30 154 H70 M100 160 H150 M40 168 H80", 2.4, line=False)
    d.band("near", waves(170, 4, 30))
    d.band("deep", waves(188, 3, 34), line=False)


@framed
def cruise_porthole(d: Drawing):
    d.band("hero", "M-30 -30 H230", shadow=False, line=False)
    for x, y in [(30, 40), (170, 40), (30, 160), (170, 160)]:
        d.marks("dark", circle(x, y, 2.2))

    def view():
        d.shape("sky", "M40 30 H160 V170 H40Z", shadow=False, line=False)
        d.disc("glow", 120, 76, 14)
        d.shape("near", "M50 112 Q64 92 80 104 Q90 96 98 112Z")
        palm(d, 72, 104, 0.4, "dark", 4)
        d.shape("mid", waves(112, 2, 14) + " L230 230 L-30 230Z", shadow=False)
        d.shape("near", waves(136, 3, 22) + " L230 230 L-30 230Z")
        d.shape("light", "M110 106 h28 l-3 5 h-22Z", shadow=False)
        d.stroke("dark", "M120 106 V98 M128 106 V96", 1.4)
    clip(d, "port", circle(100, 100, 46), view)
    d.shape("hero2", f"{circle(100, 100, 60)} {circle(100, 100, 46)}", extra=EVENODD, spot=True)
    d.shape("dark", f"{circle(100, 100, 47)} {circle(100, 100, 44)}", shadow=False, extra=EVENODD, line=False)
    import math
    for i in range(8):
        a = i * math.pi / 4 + math.pi / 8
        d.marks("dark", circle(round(100 + 53 * math.cos(a), 1), round(100 + 53 * math.sin(a), 1), 2.6))
    d.raw('<path d="M70 72 Q80 62 94 60" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".6"/>', "")


@framed
def cruise_anchor(d: Drawing):
    d.disc("glow", 100, 96, 64)
    d.band("mid", waves(150, 3, 24))
    d.band("near", waves(170, 4, 30), line=False)
    a = "dark"
    d.shape(a, f"{circle(100, 46, 12)} {circle(100, 46, 6)}", extra=EVENODD)
    d.shape(a, rrect(94, 56, 12, 96, 4))
    d.shape(a, rrect(74, 66, 52, 10, 5))
    d.shape(a, "M46 116 L58 108 Q62 142 100 150 Q138 142 142 108 L154 116 L150 120 Q144 160 100 166 Q56 160 50 120Z")
    d.shape(a, "M40 112 L58 104 L60 120Z M160 112 L142 104 L140 120Z")
    d.stroke("hero2", "M100 34 Q140 30 146 52 Q150 72 120 80 Q90 88 96 104 Q102 120 128 118", 5)
    d.stroke("hero2", "M100 34 Q140 30 146 52 Q150 72 120 80 Q90 88 96 104 Q102 120 128 118", 1, line=False) if False else None
    d.raw('<path d="M100 34 Q140 30 146 52 Q150 72 120 80 Q90 88 96 104 Q102 120 128 118" fill="none" stroke="#000" stroke-opacity=".25" stroke-width="5" stroke-dasharray="1.6 3.2"/>', "")


# ================================================================ LONGTAIL BOAT
LONGTAIL = "M18 112 Q22 148 64 150 H140 Q168 146 178 108 L182 66 L188 66 Q190 112 178 124 Q160 128 140 126 L20 116Z"


def longtail(d: Drawing, hull="hero", trim="hero2"):
    """Longtail boat facing right, waterline y=144; long-shaft engine at the stern."""
    d.limb("dark", "M30 112 L-20 150", 3.2)
    d.shape(hull, LONGTAIL)
    d.shape(trim, "M20 116 L140 126 Q160 128 178 124 L177 131 Q160 134 140 132 L21 122Z", shadow=False, spot=True)
    d.stroke("dark", "M30 132 Q60 142 140 140 Q164 138 172 128", 1.2, line=False)
    d.shape("dark", rrect(16, 98, 22, 16, 4))
    d.stroke("dark", "M28 102 L46 90", 2.6)
    for i, (role, dx) in enumerate([("pop", -8), ("glow2", -2), ("light", 4), ("pop", 9)]):
        d.shape(role, f"M184 70 Q{178 + dx} 86 {174 + dx} 102 L{178 + dx} 102 Q{182 + dx * 0.5} 86 186 72Z", shadow=False)
    d.shape("pop", circle(185, 66, 4.5))


def karst(x: float, base: float, w: float, h: float) -> str:
    return (f"M{x - w / 2} {base} Q{x - w / 2 - 4} {base - h * 0.6} {x - w / 3} {base - h * 0.85} "
            f"Q{x - w / 4} {base - h} {x} {base - h} Q{x + w / 3} {base - h} {x + w / 2.6} {base - h * 0.75} "
            f"Q{x + w / 2 + 4} {base - h * 0.4} {x + w / 2} {base}Z")


@framed
def longtail_karsts(d: Drawing):
    d.disc("glow", 140, 52, 16)
    d.shape("mid", karst(150, 130, 50, 92) + " " + karst(46, 130, 40, 70))
    d.shape("near", karst(16, 134, 44, 100) + " " + karst(186, 134, 36, 66))
    for x, y in [(8, 52), (24, 46), (14, 70), (180, 82), (190, 96), (138, 52), (154, 46), (40, 70)]:
        d.shape("deep", f"M{x} {y} q4 -7 8 0 q-4 4 -8 0Z", shadow=False, line=False)
    d.band("far", waves(126, 2, 22))
    group(d, "translate(100 100) scale(.82) translate(-100 -112)", lambda: longtail(d))
    d.band("mid", waves(150, 3, 26))
    d.band("near", waves(172, 3, 32), line=False)


@framed
def longtail_prow(d: Drawing):
    d.disc("glow", 52, 54, 16)
    d.shape("mid", karst(64, 128, 50, 80), line=False)
    for x, y in [(52, 66), (70, 60), (80, 80), (48, 90)]:
        d.shape("near", f"M{x} {y} q4 -7 8 0 q-4 4 -8 0Z", shadow=False, line=False)
    d.band("far", waves(124, 2, 22))
    d.shape("hero", "M-30 132 H88 Q124 130 138 96 L148 40 L160 40 Q160 106 144 136 Q126 166 90 168 H-30Z")
    d.shape("hero2", "M-30 132 H88 Q124 130 138 96 L141 86 Q140 122 120 136 Q104 142 88 142 H-30Z", shadow=False, spot=True)
    d.stroke("dark", "M-30 152 H92 Q124 150 140 124 M-30 160 H90 Q118 160 134 144", 1.4, line=False)
    for i, (role, dx) in enumerate([("pop", -14), ("glow2", -6), ("light", 2), ("pop", 10), ("glow2", 16)]):
        d.shape(role, f"M154 46 Q{148 + dx} 80 {142 + dx} 112 L{148 + dx} 112 Q{154 + dx * 0.5} 80 158 48Z", shadow=dx == 2)
    d.shape("light", circle(154, 48, 7))
    d.shape("pop", circle(154, 48, 4), shadow=False)
    for x, y, role in [(148, 70, "light"), (140, 86, "glow2"), (152, 84, "pop")]:
        d.shape(role, circle(x, y, 3.6), shadow=False)
    d.band("mid", waves(166, 3, 26))
    d.band("near", waves(184, 3, 32), line=False)


@framed
def longtail_beach(d: Drawing):
    d.disc("glow", 150, 52, 16)
    d.disc("glow", 0, 0, 0, line=False) if False else None
    d.shape("mid", karst(44, 116, 60, 84), line=False)
    for x, y in [(34, 48), (50, 44), (62, 64), (28, 76)]:
        d.shape("near", f"M{x} {y} q4 -7 8 0 q-4 4 -8 0Z", shadow=False, line=False)
    d.band("far", waves(112, 2, 22))
    d.band("light", "M-30 128 Q60 120 230 132", line=False)
    d.band("ground", "M-30 134 Q60 124 230 138")
    palm(d, 186, 144, 1.0, "dark", -4)
    d.marks("dark", ellipse(102, 152, 66, 3.5)) if False else None
    group(d, "translate(88 100) scale(.88) translate(-100 -92) rotate(-3 100 146)", lambda: longtail(d))
    d.band("deep", hills(186, 4, 20), line=False)


# ================================================================ BACKPACKING
@framed
def backpack(d: Drawing):
    d.disc("glow", 100, 100, 72)
    d.shape("pop", rrect(56, 30, 88, 20, 10), spot=True)
    d.stroke("dark", "M72 30 V50 M128 30 V50", 2.4)
    d.shape("hero", "M52 64 Q52 48 72 46 H128 Q148 48 148 64 V160 Q148 168 140 168 H60 Q52 168 52 160Z")
    d.shape("hero2", "M50 60 Q50 44 72 42 H128 Q150 44 150 60 L148 84 Q100 92 52 84Z")
    d.stroke("dark", "M78 84 V102 M122 84 V102", 3)
    d.shape("dark", rrect(73, 98, 10, 7, 2), shadow=False)
    d.shape("dark", rrect(117, 98, 10, 7, 2), shadow=False)
    d.shape("hero", rrect(64, 118, 72, 42, 8))
    d.stroke("dark", "M64 128 H136", 1.6)
    d.shape("light", circle(84, 142, 9), shadow=False)
    d.marks("pop", circle(84, 142, 5))
    d.shape("glow2", "M110 134 L122 132 L124 144 L112 146Z", shadow=False)
    d.shape("light", rrect(118, 98, 0.1, 0.1, 0), shadow=False, line=False)
    d.shape("pop", "M100 60 L104 68 L113 69 L106 75 L108 84 L100 79 L92 84 L94 75 L87 69 L96 68Z", shadow=False, spot=True) if False else None
    d.shape("light", rrect(88, 104, 24, 8, 2), shadow=False)
    d.shape("pop", rrect(88, 104, 8, 8, 1), shadow=False, spot=True)
    d.shape("pop", rrect(104, 104, 8, 8, 1), shadow=False, spot=True)
    d.shape("light", rrect(150, 104, 12, 46, 5))
    d.shape("near", rrect(152, 98, 8, 8, 2))
    d.stroke("dark", "M40 70 Q36 120 52 150", 3) if False else None
    d.band("far", hills(178, 4), line=False)


@framed
def hostel_bunk(d: Drawing):
    d.band("far", "M-30 -30 H230", shadow=False, line=False)
    d.shape("sky2", rrect(122, 34, 46, 46, 4))
    d.stroke("far", "M145 34 V80 M122 57 H168", 3)
    d.disc("glow", 136, 47, 6, line=False)
    d.band("mid", "M-30 168 H230")
    for x in (40, 160):
        d.shape("dark", rrect(x - 4, 36, 8, 140, 3))
    for y in (82, 140):
        d.shape("light", rrect(42, y - 8, 116, 12, 4))
        d.shape("dark", rrect(40, y + 4, 120, 6, 2))
    d.shape("light", rrect(50, 64, 28, 12, 6), shadow=False)
    d.shape("hero", "M80 74 Q110 60 154 74 V80 H80Z", spot=True)
    d.shape("light", rrect(50, 122, 28, 12, 6), shadow=False)
    d.shape("hero2", "M80 132 Q116 120 154 132 V138 H80Z")
    d.stroke("dark", "M146 90 V160 M162 90 V160", 2.2) if False else None
    for y in (100, 116, 132, 150):
        d.shape("dark", rrect(130, y, 20, 3, 1.5), shadow=False)
    d.shape("dark", rrect(128, 88, 3, 80, 1.5), shadow=False)
    d.shape("dark", rrect(149, 88, 3, 80, 1.5), shadow=False)
    # backpack on the floor
    d.shape("pop", "M82 172 Q80 148 98 146 Q116 148 114 172Z")
    d.shape("hero2", "M80 156 Q98 140 116 156 L114 160 Q98 150 82 160Z", shadow=False)
    d.shape("dark", rrect(90, 162, 16, 3, 1.5), shadow=False)


@framed
def map_compass(d: Drawing):
    d.disc("glow", 100, 100, 70)

    def mapsheet():
        panels = [("light", "M36 56 L72 46 V146 L36 156Z"), ("sky2", "M72 46 L108 56 V156 L72 146Z"),
                  ("light", "M108 56 L144 46 V146 L108 156Z"), ("sky2", "M144 46 L172 54 V154 L144 146Z")]
        d.shape("light", "M36 56 L72 46 L108 56 L144 46 L172 54 V154 L144 146 L108 156 L72 146 L36 156Z")
        for role, p in panels:
            d.shape(role, p, shadow=False, line=False)
        d.stroke("dark", "M72 46 V146 M108 56 V156 M144 46 V146", 1.4)
        d.shape("mid", "M40 104 Q56 92 68 104 Q82 116 96 100 L104 108 Q92 124 70 112 Q56 104 40 116Z", shadow=False, line=False)
        d.raw('<path d="M46 140 Q70 120 90 128 Q120 140 130 110 Q138 86 160 76" fill="none" stroke="#E4572E" stroke-width="2.4" stroke-dasharray="4 4" stroke-linecap="round"/>',
              '<path d="M46 140 Q70 120 90 128 Q120 140 130 110 Q138 86 160 76" fill="none" stroke="#1D2D44" stroke-width="2.2" stroke-dasharray="4 4" stroke-linecap="round"/>')
        d.shape("pop", "M160 78 C150 66 152 56 160 56 C168 56 170 66 160 78Z", spot=True)
        d.marks("light", circle(160, 62, 2.4))
    group(d, "rotate(-6 100 100)", mapsheet)
    # compass
    d.shape("hero2", f"{circle(76, 128, 30)}")
    d.shape("dark", rrect(70, 92, 12, 8, 3))
    d.shape("light", circle(76, 128, 24), shadow=False)
    for a, l in [(0, 4), (90, 3), (180, 3), (270, 3)]:
        d.stroke("dark", f"M76 {104 + 1} V{104 + l + 1}", 2, line=True) if False else None
    d.stroke("dark", "M76 106 V110 M76 146 V150 M54 128 H58 M94 128 H98", 2)
    d.shape("pop", "M76 128 L71 126 L82 108Z", shadow=False, spot=True)
    d.shape("pop", "M76 128 L81 130 L82 108Z", shadow=False, spot=True)
    d.shape("dark", "M76 128 L81 130 L70 148Z M76 128 L71 126 L70 148Z", shadow=False)
    d.marks("hero2", circle(76, 128, 2.6))


CONCEPTS = [
    Concept("flight-window-seat", "flight", "Window seat", flight_window,
            checks=[("light", "ground"), ("hero", "sky2"), ("hero2", "sky2"), ("hero", "light")],
            fixes={"ground": ["far", "mid", "near"], "hero2": ["pop", "glow2", "mid"]}),
    Concept("flight-jet", "flight", "Jet above the clouds", flight_jet,
            checks=[("hero", "sky"), ("hero", "light"), ("hero2", "hero")], fixes={"hero2": ["light", "glow2", "pop"]}),
    Concept("flight-boarding-pass", "flight", "Boarding pass", flight_pass,
            checks=[("light", "far"), ("deep", "far"), ("hero", "light"), ("light", "deep")], fixes={"far": ["mid", "near", "glow"]}),
    Concept("train-bullet", "train-journey", "Bullet train", train_bullet,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "mid"), ("hero2", "hero")],
            fixes={"hero": ["light", "pop"], "hero2": ["pop", "light", "dark"]}),
    Concept("train-tracks", "train-journey", "Rails to the horizon", train_tracks,
            checks=[("ground", "mid"), ("dark", "ground"), ("pop", "sky")], fixes={"ground": ["far", "glow2"], "pop": ["hero", "near"]}),
    Concept("train-station-clock", "train-journey", "Station clock", train_clock,
            checks=[("mid", "sky2"), ("dark", "sky2"), ("near", "mid")], fixes={"sky2": ["sky", "light"], "near": ["deep", "far"]}),
    Concept("scenic-steam-engine", "scenic-railway", "Steam engine", scenic_steam,
            checks=[("hero", "sky"), ("hero", "far"), ("hero2", "hero")], fixes={"hero2": ["glow2", "pop", "light"]}),
    Concept("scenic-viaduct", "scenic-railway", "Steam train on a viaduct", scenic_viaduct,
            checks=[("ground", "mid"), ("ground", "far"), ("hero", "sky")], fixes={"ground": ["light", "glow2", "far"]}),
    Concept("scenic-alpine", "scenic-railway", "Alpine railway", scenic_alpine,
            checks=[("hero", "mid"), ("hero", "far"), ("deep", "near")], fixes={"hero": ["pop", "hero2"], "deep": ["dark"]}),
    Concept("tuktuk-ride", "tuk-tuk-ride", "Tuk-tuk", tuktuk_ride,
            checks=[("hero", "sky"), ("hero", "ground"), ("hero2", "hero"), ("hero", "far")], fixes={"hero2": ["light", "glow2"], "far": ["mid", "near"]}),
    Concept("tuktuk-front", "tuk-tuk-ride", "Tuk-tuk head-on", tuktuk_front,
            checks=[("hero", "glow"), ("hero", "mid"), ("hero2", "hero"), ("hero2", "sky")], fixes={"glow": ["far", "sky2"], "hero2": ["light", "glow2"]}),
    Concept("tuktuk-temple", "tuk-tuk-ride", "Tuk-tuk by the temple", tuktuk_temple,
            checks=[("near", "glow"), ("hero", "ground"), ("hero", "near")], fixes={"near": ["deep", "mid"], "hero": ["pop", "light"]}),
    Concept("ferry-crossing", "ferry-crossing", "Car ferry", ferry_crossing, SEA,
            checks=[("light", "glow"), ("light", "far"), ("hero", "mid")], fixes={"glow": ["mid", "far", "near"], "far": ["mid", "near"], "hero": ["deep", "dark"]}),
    Concept("ferry-lighthouse", "ferry-crossing", "Past the lighthouse", ferry_lighthouse, SEA,
            checks=[("light", "near"), ("hero", "far"), ("near", "far")], fixes={"near": ["deep", "dark"], "hero": ["deep", "pop"]}),
    Concept("ferry-life-ring", "ferry-crossing", "Life ring", ferry_lifering, SEA,
            checks=[("light", "mid"), ("light", "near"), ("pop", "light"), ("dark", "sky")], fixes={"pop": ["hero", "near"]}),
    Concept("cablecar-valley", "cable-car", "Cabin over the valley", cablecar_valley,
            checks=[("hero", "far"), ("hero", "mid"), ("hero", "sky"), ("hero2", "hero")], fixes={"hero": ["pop", "deep"], "hero2": ["light", "glow2"]}),
    Concept("cablecar-pylons", "cable-car", "Gondola lift", cablecar_pylons,
            checks=[("dark", "mid"), ("hero", "mid"), ("pop", "mid"), ("hero2", "mid")], fixes={"mid": ["far", "sky2", "ground"]}),
    Concept("cablecar-tram", "cable-car", "Hill cable car", cablecar_tram,
            checks=[("hero", "ground"), ("hero", "sky"), ("light", "hero"), ("hero", "mid"), ("hero", "near"), ("hero", "hero2")], fixes={"hero": ["deep", "pop", "dark"]}),
    Concept("gondola-bridge", "gondola-ride", "Under the bridge", gondola_bridge,
            checks=[("ground", "mid"), ("ground", "far"), ("dark", "mid"), ("dark", "far")], fixes={"ground": ["light", "glow2", "hero2"]}),
    Concept("gondola-gondolier", "gondola-ride", "Gondolier", gondola_gondolier,
            checks=[("dark", "glow"), ("dark", "mid"), ("dark", "sky"), ("far", "glow")], fixes={"glow": ["glow2", "far", "light"], "far": ["mid", "near"]}),
    Concept("gondola-prow", "gondola-ride", "Gondola prow", gondola_prow,
            checks=[("light", "near"), ("light", "mid"), ("dark", "near"), ("light", "sky")], fixes={"sky": ["sky2", "far"], "near": ["deep"]}),
    Concept("camper-beach", "campervan", "Camper by the sea", camper_beach,
            checks=[("hero", "glow"), ("hero2", "glow"), ("hero", "ground"), ("hero2", "sky"), ("hero2", "hero")], fixes={"glow": ["far", "mid", "sky2"], "hero2": ["light", "glow2"]}),
    Concept("camper-front", "campervan", "Camper head-on", camper_front,
            checks=[("hero", "mid"), ("hero2", "far"), ("hero2", "hero"), ("hero2", "sky")], fixes={"hero2": ["light", "glow2"], "far": ["mid", "near"]}),
    Concept("camper-campsite", "campervan", "Campsite", camper_camp,
            checks=[("hero", "mid"), ("hero2", "far"), ("hero2", "hero"), ("pop", "ground")], fixes={"hero2": ["light", "glow2"], "pop": ["#E4572E", "hero"]}),
    Concept("moto-open-road", "motorbike-tour", "Open road", moto_road,
            checks=[("hero", "ground"), ("hero2", "ground"), ("dark", "ground"), ("hero", "hero2")], fixes={"ground": ["far", "mid"], "hero2": ["light", "pop"]}),
    Concept("moto-helmet", "motorbike-tour", "Helmet & goggles", moto_helmet,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero2", "hero")], fixes={"glow": ["far", "mid", "sky2"], "hero2": ["light", "glow2"]}),
    Concept("moto-mountain-pass", "motorbike-tour", "Mountain pass", moto_pass,
            checks=[("ground", "mid"), ("pop", "mid"), ("light", "mid")], fixes={"ground": ["light", "far"], "mid": ["near", "deep"]}),
    Concept("scooter-classic", "scooter-ride", "Vintage scooter", scooter_side,
            checks=[("hero", "glow"), ("hero", "far"), ("hero", "sky"), ("hero", "ground")], fixes={"glow": ["far", "sky2", "mid"], "hero": ["pop", "deep"]}),
    Concept("scooter-street", "scooter-ride", "Scooter on a side street", scooter_street,
            checks=[("hero", "glow2"), ("hero", "far"), ("hero", "mid"), ("hero", "ground")], fixes={"hero": ["deep", "pop", "dark"]}),
    Concept("scooter-front", "scooter-ride", "Scooter head-on", scooter_front,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "sky"), ("hero", "ground")], fixes={"hero": ["pop", "deep", "hero2"]}),
    Concept("cruise-liner", "cruise-ship", "Cruise liner", cruise_liner, SEA,
            checks=[("light", "far"), ("hero", "mid"), ("pop", "light")], fixes={"far": ["mid", "near"], "hero": ["deep", "dark"]}),
    Concept("cruise-porthole", "cruise-ship", "Porthole view", cruise_porthole, SEA,
            checks=[("hero2", "hero"), ("near", "mid"), ("hero2", "near")], fixes={"hero2": ["light", "glow2", "glow"]}),
    Concept("cruise-anchor", "cruise-ship", "Anchor", cruise_anchor, SEA,
            checks=[("dark", "glow"), ("dark", "sky"), ("hero2", "dark"), ("hero2", "glow")], fixes={"glow": ["far", "sky2"], "hero2": ["pop", "light"]}),
    Concept("longtail-karsts", "longtail-boat", "Among the karsts", longtail_karsts, SEA,
            checks=[("hero", "far"), ("hero", "mid"), ("near", "mid"), ("mid", "sky")], fixes={"hero": ["pop", "hero2", "deep"]}),
    Concept("longtail-prow", "longtail-boat", "Garlanded prow", longtail_prow, SEA,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "mid"), ("pop", "hero"), ("mid", "sky")], fixes={"hero": ["deep", "dark"], "pop": ["light"]}),
    Concept("longtail-beach", "longtail-boat", "Beached longtail", longtail_beach, SEA,
            checks=[("hero", "ground"), ("hero", "sky"), ("mid", "sky"), ("hero", "mid")], fixes={"hero": ["deep", "pop", "dark"]}),
    Concept("backpacking-pack", "backpacking", "Patched backpack", backpack,
            checks=[("hero", "glow"), ("hero2", "glow"), ("hero2", "hero"), ("pop", "glow")], fixes={"glow": ["far", "sky2", "mid"], "hero2": ["light", "glow2"]}),
    Concept("backpacking-bunk", "backpacking", "Hostel bunk", hostel_bunk,
            checks=[("dark", "far"), ("light", "far"), ("hero", "far"), ("pop", "mid")], fixes={"far": ["mid", "near"], "pop": ["hero"]}),
    Concept("backpacking-map", "backpacking", "Map & compass", map_compass,
            checks=[("light", "glow"), ("hero2", "light"), ("hero2", "sky2")], fixes={"glow": ["far", "mid", "near"], "hero2": ["hero", "glow"]}),
]
