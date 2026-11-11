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
    for x in (22, 178):
        post(d, "dark", x, 64, 200, 5)
    d.shape("dark", rrect(-30, 61, 260, 6, 3))
    d.shape("dark", rrect(-30, 150, 260, 4, 2))
    d.shape("dark", rrect(-30, 176, 260, 4, 2))
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
    group(d, f"translate(100 {slope(100) + 2:.1f}) rotate(-19.9) scale(1.3)", lambda: tram(d))
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
    d.shape("mid", "M-30 160 V36 H22 V160Z")
    d.shape("far", "M178 160 V48 H230 V160Z")
    for y in (52, 84, 116):
        d.marks("dark", f"M2 {y + 16} V{y + 6} Q7 {y} 12 {y + 6} V{y + 16}Z")
    for y in (64, 96, 128):
        d.marks("dark", f"M188 {y + 16} V{y + 6} Q193 {y} 198 {y + 6} V{y + 16}Z")


@framed
def gondola_bridge(d: Drawing):
    d.band("far", "M-30 112 H40 V96 L50 90 L60 96 V104 H92 V84 H104 V104 H140 V94 H170 V112 H230")
    d.shape("ground", "M-30 30 H230 V140 H196 Q100 48 4 140 H-30Z")
    d.shape("hero2", "M-30 24 H230 V32 H-30Z", shadow=False)
    for x in range(-24, 230, 12):
        d.shape("ground", f"M{x} 32 V22 Q{x + 4} 16 {x + 8} 22 V32Z", shadow=False, line=False)
    d.shape("ground", "M-30 14 H230 V18 H-30Z", shadow=False, line=False)
    d.stroke("light", "M14 140 Q100 64 186 140", 3, line=False)
    d.stroke("hero2", "M4 140 Q100 48 196 140", 4)
    venice_houses(d)
    d.band("mid", waves(140, 3, 22))
    d.band("near", waves(160, 3, 28), line=False)
    group(d, "translate(8 18) scale(.92)", lambda: (gondola(d), gondolier(d)))
    d.band("deep", waves(182, 3, 32), line=False)


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
    d.shape("hero2", "M110 78 L146 96 L144 100 L110 86Z", spot=False)
    post(d, "dark", 144, 98, 134, 2.4, shadow=False)
    d.stroke("dark", "M112 86 Q130 98 146 98", 1, line=False)
    for i, x in enumerate(range(116, 146, 7)):
        d.marks(["glow2", "pop"][i % 2], circle(x, 90 + (x - 112) * 0.3 + 3, 1.6))
    campfire(d, 162, 156)
    d.band("deep", hills(182, 4, 20), line=False)


# ================================================================ MOTORBIKE
def motorbike(d: Drawing, body="hero", bags="hero2"):
    """Touring motorbike facing right, wheels on y=150."""
    d.shape(bags, rrect(22, 92, 32, 30, 6))
    d.shape(bags, rrect(26, 76, 26, 18, 5))
    d.stroke("dark", "M38 92 V122", 1.4)
    d.limb("dark", "M146 134 L128 74", 6)
    d.shape("light", "M126 70 L138 46 L146 50 L136 76Z", shadow=False)
    d.stroke("dark", "M128 74 L116 70", 3)
    d.shape("dark", "M84 112 Q84 104 92 104 H118 Q124 104 124 112 V128 Q124 134 118 134 H90 Q84 134 84 128Z")
    d.stroke("light", "M88 138 Q70 140 40 132", 4)
    d.stroke("dark", "M88 138 Q70 140 40 132", 1, line=False)
    d.shape(body, "M48 100 Q50 92 60 92 H80 L96 98 L82 108 H52 Q46 108 48 100Z")
    d.shape("dark", "M54 92 Q64 84 84 88 L92 96 L56 96Z")
    d.shape(body, "M86 92 Q92 78 112 80 Q126 82 130 92 Q128 104 112 106 H92 Q84 102 86 92Z", spot=True)
    d.shape("light", "M96 86 Q106 82 118 85", shadow=False, line=False)
    d.shape(body, "M124 76 Q138 74 142 86 Q138 96 128 94Z")
    d.shape("glow2", ellipse(140, 85, 3.5, 5), shadow=False)
    d.stroke(body, "M136 128 A16 16 0 0 1 160 126", 3.4)
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
    d.band("far", hills(156, 6, 10))
    d.shape("hero", "M40 126 Q36 50 100 44 Q164 50 160 126 Q160 156 138 158 H62 Q40 156 40 126Z")
    d.shape("hero2", "M90 45 Q100 44 110 45 L112 78 H88Z", shadow=False, spot=True)
    d.shape("dark", "M62 112 Q62 92 100 92 Q138 92 138 112 V160 H62Z", shadow=False)
    d.stroke("hero2", "M62 158 V112 Q62 92 100 92 Q138 92 138 112 V158", 4)
    d.shape("dark", "M38 78 Q100 64 162 78 V92 Q100 78 38 92Z", shadow=False)
    for x in (74, 126):
        d.shape("dark", circle(x, 80, 18))
        d.shape("light", circle(x, 80, 13), shadow=False)
        d.shape("sky2", "M" + f"{x - 7} 74 Q{x} 68 {x + 6} 72", shadow=False, line=False)
    d.stroke("light", "M66 76 Q70 72 76 72 M118 76 Q122 72 128 72", 2.4, line=False)
    d.shape("dark", rrect(90, 76, 20, 6, 3), shadow=False)
    d.stroke("dark", "M66 150 Q100 176 134 150", 2.4)
    d.shape("light", rrect(94, 166, 12, 6, 2))


@framed
def moto_pass(d: Drawing):
    d.disc("glow", 150, 48, 15)
    d.band("far", "M-30 84 L20 54 L60 76 L100 40 L150 74 L230 50")
    d.shape("light", "M100 40 L112 52 L106 51 L100 56 L94 50 L88 52Z", shadow=False)
    d.band("mid", "M-30 112 L40 80 L110 96 L230 72")
    road = "M200 82 L50 98 Q34 102 50 108 L170 118 Q190 122 170 128 L20 146 Q4 150 20 156 L230 172"
    d.stroke("ground", road, 9, shadow=True, line=False)
    d.stroke("dark", road, 2, line=True) if False else None
    d.raw("", f'<path d="{road}" fill="none" stroke="{d.c.get("ink", "#000") if not d.paper else ""}" stroke-width="2.4" stroke-dasharray="5 6" stroke-linecap="round"/>' if not d.paper else "")
    d.raw(f'<path d="{road}" fill="none" stroke="{d.c.get("light")}" stroke-width="1.2" stroke-dasharray="3 5"/>', "")
    group(d, "translate(70 82) scale(.22)", lambda: motorbike(d))
    # warning sign
    post(d, "dark", 148, 150, 196, 4)
    d.shape("light", "M148 98 L178 150 H118Z")
    d.shape("pop", "M148 98 L178 150 H118Z M148 110 L127 145 H169Z", shadow=False, spot=True, extra=EVENODD)
    d.stroke("dark", "M154 140 Q140 134 148 128 Q156 122 142 116", 3)
    d.band("near", hills(184, 6, 30), line=False)


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
            checks=[("ground", "mid"), ("ground", "far"), ("dark", "mid"), ("light", "dark")], fixes={"ground": ["light", "glow2", "sky2"], "mid": ["near", "far"]}),
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
]
