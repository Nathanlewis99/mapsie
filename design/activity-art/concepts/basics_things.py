"""Everyday basics: one bold, generic sticker per common search term (car, beer, dog...)."""
from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group

EVENODD = 'fill-rule="evenodd"'
SEA = ["coastal", "meadow", "blush", "dusk"]


# ================================================================ private helpers (copied, not imported)
def clip(d: Drawing, cid: str, path: str, fn):
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


def wheel(d: Drawing, x: float, y: float, r: float, tyre="dark", hub="light", spokes=False):
    d.shape(tyre, circle(x, y, r))
    d.shape(hub, circle(x, y, r * 0.42), shadow=False)
    if spokes:
        d.marks(tyre, circle(x, y, r * 0.16))


def steam(d: Drawing, xs, y, h=22, role="light", w=3.2):
    """Wavy steam rising from y (bottom) for each x."""
    for i, x in enumerate(xs):
        k = 1 if i % 2 == 0 else -1
        q = h / 4
        d.stroke(role, f"M{x} {y} q{4*k} {-q} 0 {-2*q} t0 {-2*q}", w)


def pine(x: float, y: float, s: float = 1.0) -> str:
    return (f"M{x} {y - 30 * s} L{x + 9 * s} {y - 16 * s} L{x + 5 * s} {y - 16 * s} L{x + 12 * s} {y - 4 * s} "
            f"L{x + 2 * s} {y - 4 * s} V{y} H{x - 2 * s} V{y - 4 * s} L{x - 12 * s} {y - 4 * s} "
            f"L{x - 5 * s} {y - 16 * s} L{x - 9 * s} {y - 16 * s}Z")


def palm(d: Drawing, x: float, y: float, s: float = 1.0, role="dark", lean=6):
    tx, ty = x + lean * s, y - 62 * s
    d.limb(role, f"M{x} {y} Q{x + lean * 0.2 * s} {y - 34 * s} {tx} {ty}", 4.5 * s)
    for dx, dy, cx, cy in [(-26, 10, -14, -8), (26, 12, 14, -8), (-20, -10, -12, -14), (22, -8, 12, -14), (-4, 18, -6, 4), (6, 20, 8, 4)]:
        d.shape(role, f"M{tx} {ty} Q{tx + cx * s} {ty + cy * s} {tx + dx * s} {ty + dy * s} "
                      f"Q{tx + cx * 0.6 * s} {ty + cy * 0.2 * s} {tx} {ty + 2 * s}Z", shadow=False)


def arch(d: Drawing, x: float, y: float, r: float, role="dark"):
    """Dark wheel arch cut into a body whose bottom edge is at y."""
    d.marks(role, f"M{x - r} {y} A{r} {r} 0 0 1 {x + r} {y}Z")


def star(cx, cy, r, k=0.42):
    import math
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * k
        pts.append(f"{cx + rr * math.cos(a):.1f} {cy + rr * math.sin(a):.1f}")
    return "M" + " L".join(pts) + "Z"


def pol(cx, cy, r, deg):
    import math
    a = math.radians(deg - 90)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def road(d: Drawing, y=150):
    d.band("ground", f"M-30 {y} Q100 {y - 6} 230 {y}")
    d.band("deep", hills(y + 26, 4, 20), line=False)


# ================================================================ CAR
@framed
def car(d: Drawing):
    d.disc("glow", 100, 96, 66, line=False)
    d.shape("light", cloud(28, 62, 0.8), shadow=False)
    road(d, 152)
    body = ("M38 144 Q28 144 28 132 V122 Q28 106 46 104 L60 102 Q68 66 100 64 Q132 64 142 100 L156 104 "
            "Q174 108 174 126 V132 Q174 144 164 144Z")
    d.shape("hero", body)
    d.shape("light", "M70 100 Q76 76 96 74 V100Z", shadow=False)
    d.shape("light", "M104 74 Q126 76 133 100 H104Z", shadow=False)
    d.shape("hero2", "M29 116 H173 V124 H29Z", shadow=False, spot=True)
    d.stroke("dark", "M100 102 V138", 1.6)
    d.shape("dark", rrect(106, 106, 9, 3, 1.5), shadow=False)
    d.stroke("light", "M74 70 Q88 63 104 64", 3, line=False)
    d.shape("glow2", ellipse(168, 112, 4, 6), shadow=False)
    d.shape("pop", rrect(28, 108, 5, 9, 2), shadow=False)
    d.shape("dark", rrect(156, 134, 22, 7, 3.5))
    d.shape("dark", rrect(22, 134, 18, 7, 3.5))
    d.shape("hero", "M138 96 l7 -4 l2 6 Z")
    for x in (62, 140):
        arch(d, x, 144, 20)
        wheel(d, x, 145, 16)


# ================================================================ CONVERTIBLE
@framed
def convertible(d: Drawing):
    d.disc("glow", 100, 100, 62, line=False)
    d.band("far", hills(132, 8, 10))
    palm(d, 160, 136, 0.9, "near", 8)
    palm(d, 36, 138, 0.7, "near", -6)
    d.band("ground", "M-30 152 Q100 146 230 152")
    # seats and windscreen poke above the open body
    d.shape("dark", "M66 106 Q64 84 76 82 Q86 82 86 106Z")
    d.shape("dark", "M92 106 Q90 86 101 84 Q110 84 110 106Z")
    d.stroke("dark", "M116 100 L122 88", 3)
    d.shape("dark", ellipse(122, 88, 3, 7), extra='transform="rotate(30 122 88)"')
    d.shape("light", "M128 106 L136 80 H141 L136 106Z", spot=True)
    body = ("M24 140 Q14 140 14 130 V112 Q14 100 26 98 L60 104 H150 Q178 104 186 116 V130 Q186 140 176 140Z")
    d.shape("hero", body)
    d.shape("hero2", "M15 118 Q100 114 185 118 V124 Q100 120 15 124Z", shadow=False, spot=True)
    d.stroke("dark", "M120 106 V134", 1.6)
    d.shape("glow2", ellipse(182, 112, 3.5, 5), shadow=False)
    d.shape("pop", rrect(14, 104, 5, 10, 2), shadow=False)
    d.shape("light", rrect(170, 132, 20, 6, 3))
    d.shape("light", rrect(10, 132, 18, 6, 3))
    for x in (52, 150):
        arch(d, x, 140, 19)
        d.shape("dark", circle(x, 141, 15))
        d.shape("light", circle(x, 141, 10), shadow=False)
        d.shape("dark", circle(x, 141, 7), shadow=False, line=False)
        d.marks("light", circle(x, 141, 2.5))


# ================================================================ SAILBOAT
@framed
def sailboat(d: Drawing):
    d.disc("far", 100, 100, 70, line=False)
    d.disc("glow", 150, 60, 14)
    d.shape("light", cloud(18, 70, 0.8), shadow=False)
    d.band("mid", waves(128, 4, 26))
    # mast + sails
    d.shape("dark", rrect(97, 32, 5, 108, 2.5))
    d.shape("light", "M95 38 Q66 80 46 128 H95Z")
    d.shape("light", "M104 46 Q136 86 150 124 H104Z")
    d.shape("pop", "M95 38 Q86 52 78 66 H95Z", shadow=False, spot=True)
    d.shape("pop", "M97 26 L116 31 L97 36Z", spot=True)
    d.stroke("far", "M60 112 H94 M114 106 H143", 1.6, line=False)
    # hull
    d.shape("hero", "M30 128 H170 Q160 152 140 154 H58 Q38 152 30 128Z")
    d.shape("hero2", "M33 134 H167 Q166 138 164 140 H36Z", shadow=False, spot=True)
    for x in (62, 80, 98):
        d.marks("light", circle(x + 20, 146, 2.6))
    d.band("near", waves(156, 5, 30))
    d.band("deep", waves(178, 4, 34), line=False)


# ================================================================ SPEEDBOAT
@framed
def speedboat(d: Drawing):
    d.disc("glow", 140, 62, 18)
    d.shape("light", cloud(30, 50, 0.9), shadow=False)
    d.band("far", waves(112, 3, 24))
    d.band("mid", waves(132, 4, 28))

    def boat():
        hull = "M26 104 H170 Q186 104 190 96 L182 120 Q176 134 156 136 H40 Q28 134 26 120Z"
        d.shape("dark", rrect(18, 96, 14, 34, 4))
        d.shape("dark", rrect(14, 92, 20, 10, 4))
        d.shape("light", "M108 104 L120 80 H128 L138 104Z")
        d.shape("sky2", "M114 102 L122 85 H126 L132 102Z", shadow=False, line=False)
        d.shape("dark", rrect(70, 92, 30, 12, 4))
        d.shape("hero", hull)
        d.shape("light", "M28 116 H178 L176 122 H30Z", shadow=False, spot=True)
        d.shape("hero2", "M30 124 H174 Q170 132 156 134 H40 Q32 132 30 124Z", shadow=False, spot=True)
    group(d, "rotate(-7 100 116)", boat)
    # spray and wake
    d.shape("light", "M-10 142 Q30 120 60 136 Q90 146 130 140 Q150 138 172 128 Q160 150 120 154 Q60 160 -10 156Z")
    d.shape("light", "M168 128 Q178 112 192 114 Q182 120 184 132Z", shadow=False)
    d.band("near", waves(158, 5, 30))
    d.band("deep", waves(180, 4, 34), line=False)


# ================================================================ TRAIN
@framed
def train(d: Drawing):
    d.disc("glow", 100, 100, 66, line=False)
    d.shape("light", cloud(116, 40, 1.0))
    d.shape("light", cloud(150, 26, 0.7))
    d.band("far", hills(140, 8, 10))
    # cab (back, left)
    d.shape("dark", rrect(28, 60, 52, 9, 3))
    d.shape("hero", rrect(34, 66, 44, 72, 4))
    d.shape("light", rrect(43, 76, 26, 22, 4), shadow=False)
    # boiler + chimney + dome
    d.shape("dark", "M134 98 L130 62 H150 L146 98Z")
    d.shape("dark", rrect(127, 56, 26, 9, 3))
    d.shape("hero2", "M98 98 Q98 80 110 80 Q122 80 122 98Z", spot=True)
    d.shape("hero", rrect(74, 94, 92, 40, 12))
    d.shape("hero2", "M100 94 h6 v40 h-6Z M134 94 h6 v40 h-6Z", shadow=False, spot=True)
    d.shape("dark", rrect(160, 92, 14, 44, 6))
    d.disc("glow2", 172, 106, 5, line=False)
    d.shape("dark", rrect(28, 134, 150, 8, 3))
    d.shape("pop", "M168 140 L190 160 H164Z")
    for x, r in [(58, 16), (100, 16)]:
        wheel(d, x, 148, r)
    wheel(d, 142, 154, 10)
    d.stroke("light", "M58 152 H100", 3.2)
    d.stroke("dark", "M58 152 H100", 1.2)
    d.band("ground", "M-30 164 H230")
    d.stroke("dark", "M-30 164 H230", 3)
    d.band("near", hills(184, 4, 20), line=False)


# ================================================================ PLANE
@framed
def plane(d: Drawing):
    d.disc("far", 100, 100, 70, line=False)
    d.shape("light", cloud(18, 140, 1.3))
    d.shape("light", cloud(132, 46, 1.0))
    d.shape("light", cloud(140, 150, 0.9), shadow=False)

    def jet():
        # top-down airliner pointing up (nose at y=22), centre x=100
        d.shape("light", "M100 116 L32 142 L32 152 L100 136 L168 152 L168 142Z")
        d.shape("light", "M100 156 L76 170 V176 L100 170 L124 176 V170Z")
        for x in (64, 136):
            d.shape("hero2", rrect(x - 5, 124, 10, 20, 5), spot=True)
        d.shape("light", "M100 20 C110 20 112 36 112 50 V160 C112 172 106 180 100 180 C94 180 88 172 88 160 V50 C88 36 90 20 100 20Z")
        d.shape("hero", "M94 34 Q100 28 106 34 L106 40 Q100 37 94 40Z", shadow=False)
        d.shape("hero", "M88 128 H112 V134 H88Z M30 145 L32 152 L46 149 L46 141Z M170 145 L168 152 L154 149 L154 141Z", shadow=False, spot=True)
        d.shape("hero", "M96 168 L100 186 L104 168Z")
    group(d, "rotate(42 100 100) translate(100 100) scale(.9) translate(-100 -100)", jet)


# ================================================================ BICYCLE
@framed
def bicycle(d: Drawing):
    d.disc("glow", 100, 96, 62, line=False)
    d.band("far", hills(130, 8, -10))
    d.band("ground", "M-30 156 Q100 150 230 156")
    rear, front, y = (54, 132), (146, 132), 132

    for x, _ in (rear, front):
        d.stroke("dark", circle(x, y, 26), 5, shadow=True)
        d.stroke("light", circle(x, y, 20), 1.2, line=False)
        d.marks("dark", circle(x, y, 3))
    # frame: rear hub, crank (96,132), seat (84,90), head tube (128,86)
    frame = "M54 132 L96 132 L84 90 Z M84 90 L130 92 L96 132 M128 86 L146 132"
    d.limb("hero", frame, 5)
    d.stroke("dark", "M84 90 L82 80", 3)
    d.shape("dark", "M70 78 Q82 72 94 78 Q92 82 82 82 Q72 82 70 78Z")
    d.stroke("dark", "M128 86 L126 74 Q132 70 142 74", 3)
    # basket of flowers
    d.shape("hero2", "M134 78 H164 L160 98 H138Z", spot=True)
    d.stroke("dark", "M138 86 H161 M146 78 V98 M154 78 V98", 1.2, line=False)
    for x, yy, role in [(140, 72, "pop"), (150, 66, "light"), (160, 72, "pop")]:
        d.shape(role, circle(x, yy, 5))
        d.marks("hero2" if role == "pop" else "pop", circle(x, yy, 1.8))
    d.shape("dark", circle(96, 132, 6))
    d.stroke("dark", "M96 132 L104 142", 3)
    d.shape("dark", rrect(100, 140, 10, 4, 2), shadow=False)


# ================================================================ MOTORBIKE
@framed
def motorbike(d: Drawing):
    d.disc("glow", 100, 96, 64, line=False)
    d.band("far", hills(124, 8, 20))
    d.band("ground", "M-30 150 Q100 144 230 150")
    y = 132
    # forks + handlebar
    d.limb("dark", "M150 132 L132 78", 6)
    d.stroke("dark", "M132 78 L120 70", 3.2)
    d.marks("dark", circle(120, 70, 3))
    # engine block + exhaust
    d.shape("dark", "M82 104 H118 L122 130 H86Z")
    d.stroke("light", "M88 112 H118 M89 118 H119 M90 124 H120", 1.4, line=False)
    d.limb("light", "M90 132 Q70 140 34 132", 5)
    # tank, seat, tail
    d.shape("hero", "M40 98 Q38 90 52 90 H84 L80 104 H48Z")
    d.shape("dark", "M44 92 Q52 82 84 86 L88 94 H48Z")
    d.shape("hero", "M82 92 Q86 76 106 76 Q126 76 132 88 L126 104 H86Z", spot=True)
    d.shape("light", "M92 84 Q102 79 116 81", shadow=False, line=False)
    d.shape("hero2", "M94 92 H124", shadow=False, line=False)
    d.stroke("hero2", "M92 94 Q108 98 126 92", 3, line=False)
    # headlight
    d.shape("dark", circle(140, 86, 9))
    d.shape("glow2", circle(142, 86, 6), shadow=False)
    # mudguards
    d.stroke("hero", "M130 124 A22 22 0 0 1 168 120", 4)
    d.stroke("hero", "M28 118 A24 24 0 0 1 72 112", 4, line=False)
    for x in (52, 150):
        d.shape("dark", circle(x, y, 20))
        d.shape("light", circle(x, y, 12), shadow=False)
        d.stroke("dark", f"M{x - 12} {y} H{x + 12} M{x} {y - 12} V{y + 12} M{x - 8.5} {y - 8.5} L{x + 8.5} {y + 8.5} M{x + 8.5} {y - 8.5} L{x - 8.5} {y + 8.5}", 1.2, line=False)
        d.marks("dark", circle(x, y, 3.5))


# ================================================================ BUS
@framed
def bus(d: Drawing):
    d.disc("glow", 100, 96, 66, line=False)
    d.shape("light", cloud(130, 40, 0.8), shadow=False)
    road(d, 150)
    body = "M30 140 Q22 140 22 132 V66 Q22 54 36 54 H158 Q174 54 178 70 L182 132 Q182 140 174 140Z"
    d.shape("dark", rrect(40, 48, 100, 8, 3))
    d.shape("hero", body)
    d.shape("hero2", "M23 112 H181 V120 H23Z", shadow=False, spot=True)
    for x in range(30, 130, 26):
        d.shape("light", rrect(x, 64, 20, 30, 4), shadow=False)
    d.shape("light", rrect(134, 64, 22, 64, 4), shadow=False)
    d.stroke("hero", "M145 64 V128", 1.6)
    d.shape("light", "M162 64 H170 Q176 64 177 72 L179 94 H162Z", shadow=False)
    d.shape("glow2", ellipse(179, 124, 3, 5), shadow=False)
    d.shape("pop", rrect(22, 100, 4, 10, 2), shadow=False)
    d.shape("dark", rrect(170, 134, 16, 7, 3.5))
    d.shape("dark", rrect(18, 134, 14, 7, 3.5))
    for x in (54, 114):
        arch(d, x, 140, 18)
        wheel(d, x, 141, 14)


# ================================================================ SUITCASE
@framed
def suitcase(d: Drawing):
    d.disc("glow", 100, 100, 70, line=False)
    d.shape("dark", "M80 52 Q80 38 92 38 H108 Q120 38 120 52 V58 H112 V50 Q112 46 108 46 H92 Q88 46 88 50 V58 H80Z")
    d.shape("hero", rrect(36, 56, 128, 98, 12))
    d.shape("hero2", rrect(36, 56, 128, 14, 7), shadow=False)
    for x in (66, 134):
        d.shape("dark", rrect(x - 6, 54, 12, 102, 3))
        d.shape("hero2", rrect(x - 7, 120, 14, 10, 2), shadow=False)
        d.marks("dark", rrect(x - 3, 123, 6, 4, 1))
    for x, y in [(36, 56), (164, 56), (36, 154), (164, 154)]:
        d.marks("dark", circle(x + (6 if x < 100 else -6), y + (6 if y < 100 else -6), 3))
    # travel stickers
    d.shape("light", circle(96, 96, 14), shadow=False)
    d.shape("pop", circle(96, 96, 9), shadow=False, spot=True)
    d.shape("glow2", star(96, 96, 6), shadow=False, line=False)
    d.shape("light", rrect(84, 122, 28, 18, 3), extra='transform="rotate(-8 98 131)"', shadow=False)
    d.shape("far", "M88 136 L96 126 L102 132 L106 128 L110 136Z", extra='transform="rotate(-8 98 131)"', shadow=False, line=False)
    d.shape("pop", "M144 82 L156 82 L156 100 L150 96 L144 100Z", shadow=False)
    d.shape("light", ellipse(48, 128, 6, 9), shadow=False)
    d.shape("dark", rrect(48, 154, 14, 6, 3))
    d.shape("dark", rrect(138, 154, 14, 6, 3))


# ================================================================ BACKPACK
@framed
def backpack(d: Drawing):
    d.disc("glow", 100, 100, 70, line=False)
    # rolled mat on top
    d.shape("hero2", rrect(50, 26, 100, 22, 11), spot=True)
    d.stroke("dark", "M66 26 V48 M134 26 V48", 2.6)
    d.stroke("dark", ellipse(146, 37, 3.5, 8), 1.4, line=False)
    # side straps / pockets
    d.shape("hero2", rrect(32, 96, 18, 50, 7))
    d.shape("hero2", rrect(150, 96, 18, 50, 7))
    d.shape("hero", "M46 70 Q46 52 66 50 H134 Q154 52 154 70 V156 Q154 166 144 166 H56 Q46 166 46 156Z")
    # lid
    d.shape("hero", "M44 72 Q44 48 70 46 H130 Q156 48 156 72 Q156 84 146 86 H54 Q44 84 44 72Z")
    d.stroke("dark", "M86 86 V104 M114 86 V104", 3.2)
    d.shape("dark", rrect(81, 100, 10, 8, 2), shadow=False)
    d.shape("dark", rrect(109, 100, 10, 8, 2), shadow=False)
    # front pocket
    d.shape("hero2", "M62 118 Q62 112 70 112 H130 Q138 112 138 118 V150 Q138 158 130 158 H70 Q62 158 62 150Z", spot=True)
    d.stroke("dark", "M66 122 Q100 128 134 122", 1.8)
    d.marks("dark", rrect(97, 124, 6, 8, 2))


# ================================================================ CAMERA
@framed
def camera(d: Drawing):
    d.disc("glow", 100, 100, 70, line=False)
    d.stroke("dark", "M32 86 Q20 150 70 160 M168 86 Q180 150 130 160", 3.2, shadow=True)
    d.shape("dark", rrect(76, 48, 40, 20, 5))
    d.shape("dark", rrect(126, 54, 18, 12, 3))
    d.shape("hero", rrect(28, 64, 144, 86, 14))
    d.shape("dark", "M28 84 H172 V132 H28Z", shadow=False)
    d.shape("light", rrect(40, 72, 24, 14, 3), shadow=False)
    d.shape("pop", circle(152, 76, 5), shadow=False, spot=True)
    d.shape("hero", circle(100, 108, 38))
    d.shape("dark", circle(100, 108, 30), shadow=False)
    d.shape("hero2", circle(100, 108, 21), shadow=False, spot=True)
    d.shape("dark", circle(100, 108, 13), shadow=False)
    d.marks("light", circle(93, 101, 4) + circle(106, 112, 2))


# ================================================================ TENT
@framed
def tent(d: Drawing):
    d.disc("glow", 140, 56, 16)
    for x, y in [(40, 46), (64, 32), (100, 44), (178, 82), (26, 80)]:
        d.marks("light", f"M{x} {y - 3} L{x + 1} {y - 1} L{x + 3} {y} L{x + 1} {y + 1} L{x} {y + 3} L{x - 1} {y + 1} L{x - 3} {y} L{x - 1} {y - 1}Z")
    d.band("far", "M-30 112 L14 84 L44 100 L84 66 L124 102 L156 80 L230 114")
    for x, y, s in [(22, 140, 1.4), (172, 136, 1.2), (190, 140, 0.9)]:
        d.shape("near", pine(x, y, s), shadow=False)
    d.band("ground", "M-30 146 Q100 136 230 146")
    d.stroke("dark", "M100 50 V40", 3)
    d.shape("pop", "M100 40 L112 44 L100 48Z", spot=True)
    d.shape("hero", "M100 48 L160 150 H40Z")
    d.shape("hero2", "M100 48 L130 150 H100Z", shadow=False)
    d.shape("dark", "M100 70 L122 150 H78Z", shadow=False)
    d.shape("hero2", "M100 70 L80 150 H64Z", spot=True)
    d.stroke("dark", "M40 150 L24 158 M160 150 L176 158", 2)
    d.band("deep", hills(178, 4, 20), line=False)


# ================================================================ COCKTAIL
@framed
def cocktail(d: Drawing):
    d.disc("glow", 100, 100, 70, line=False)
    # umbrella + straw behind glass rim
    d.stroke("dark", "M112 70 L136 34", 2.6)
    d.shape("pop", "M116 26 Q138 18 156 40 L136 34Z", spot=True)
    d.shape("hero2", "M116 26 Q122 34 136 34 Z", shadow=False)
    d.limb("light", "M86 86 L66 36", 4.5, shadow=True)
    # glass
    d.shape("light", "M38 64 H162 L106 118 H94Z")
    d.shape("hero", "M46 72 H154 L104 116 H96Z", shadow=False, spot=True)
    d.shape("light", "M52 74 L60 74 L84 98", shadow=False, line=False)
    d.limb("light", "M100 116 V156", 5)
    d.shape("light", ellipse(100, 160, 26, 6))
    # lime wheel on rim
    d.shape("near", circle(150, 66, 15))
    d.shape("glow2", circle(150, 66, 11.5), shadow=False)
    d.stroke("near", "M150 56 V76 M140 66 H160 M143 59 L157 73 M157 59 L143 73", 1.2, line=False)
    d.marks("pop", circle(80, 92, 3.5))


# ================================================================ BEER
@framed
def beer(d: Drawing):
    d.disc("glow", 100, 100, 70, line=False)
    # handle
    d.limb("light", "M140 80 H150 Q166 80 166 96 V114 Q166 130 150 130 H140", 9)
    d.shape("light", "M50 64 H140 L136 160 Q136 166 130 166 H60 Q54 166 54 160Z")
    d.shape("hero", "M56 78 H134 L131 154 Q131 158 127 158 H63 Q59 158 59 154Z", shadow=False, spot=True)
    for x, y, r in [(76, 140, 3), (88, 120, 2.4), (110, 132, 2.6), (118, 108, 2), (96, 100, 2)]:
        d.marks("hero2", circle(x, y, r))
    d.stroke("light", "M66 90 V146", 4, line=False)
    # foam
    d.shape("light", "M44 66 Q40 46 58 46 Q62 30 80 36 Q92 24 106 34 Q122 26 132 40 Q150 38 148 58 Q150 70 140 72 "
                     "L140 84 Q140 90 134 90 Q128 90 128 84 V74 H62 V80 Q62 86 56 86 Q50 86 50 80 V72 Q44 72 44 66Z")
    d.marks("sky2", circle(74, 56, 3) + circle(100, 48, 2.5) + circle(124, 56, 3))


# ================================================================ WINE
def wine_glass(d: Drawing, x, y, s=1.0, rot=0, wine="pop"):
    def g():
        d.shape("light", f"M{x-13} {y-32} C{x-20} {y-12} {x-16} {y+7} {x} {y+8} C{x+16} {y+7} {x+20} {y-12} {x+13} {y-32}Z")
        d.shape(wine, f"M{x-17.6} {y-16} Q{x} {y-12} {x+17.6} {y-16} C{x+17} {y+2} {x+12} {y+7} {x} {y+7.5} C{x-12} {y+7} {x-17} {y+2} {x-17.6} {y-16}Z", shadow=False, spot=True)
        d.stroke("light", f"M{x-11} {y-10} Q{x-12} {y-2} {x-8} {y+2}", 2, line=False)
        d.limb("light", f"M{x} {y+8} V{y+38}", 3.4, shadow=False)
        d.shape("light", ellipse(x, y + 39, 13, 3.5))
    group(d, f"rotate({rot} {x} {y+39}) translate({x} {y+39}) scale({s}) translate({-x} {-y-39})", g)


@framed
def wine(d: Drawing):
    d.disc("glow", 100, 100, 70, line=False)
    # bottle
    d.shape("hero", "M66 34 H80 V60 Q94 70 94 92 V160 Q94 166 88 166 H58 Q52 166 52 160 V92 Q52 70 66 60Z")
    d.shape("pop", rrect(64, 28, 18, 10, 2), spot=True)
    d.shape("light", rrect(55, 104, 36, 34, 3), shadow=False)
    d.shape("pop", rrect(62, 112, 22, 6, 2), shadow=False)
    d.stroke("hero", "M62 126 H84 M66 131 H80", 1.6, line=False)
    d.stroke("light", "M60 90 V100 M60 144 V156", 3, line=False)
    wine_glass(d, 128, 98, 1.6)


# ================================================================ COFFEE
@framed
def coffee(d: Drawing):
    d.disc("glow", 100, 100, 70, line=False)
    steam(d, [84, 100, 116], 66, 30)
    d.shape("hero2", ellipse(100, 150, 64, 14))
    d.shape("dark", ellipse(100, 146, 34, 6), shadow=False, line=False)
    d.limb("hero", "M150 92 Q170 92 170 110 Q170 128 146 128", 9)
    d.shape("hero", "M40 82 H160 Q160 148 100 148 Q40 148 40 82Z", spot=True)
    d.shape("light", ellipse(100, 82, 60, 12))
    d.shape("ground", ellipse(100, 83, 53, 8.5), shadow=False)
    d.shape("light", "M100 92 C96 84 86 84 88 80 C90 76 96 78 100 82 C104 78 110 76 112 80 C114 84 104 84 100 92Z", shadow=False)
    d.stroke("light", "M52 100 Q56 124 72 136", 4, line=False)


# ================================================================ NOODLES
def chopsticks(d: Drawing, x1, y1, x2, y2, gap=7, role="dark", w=3.6):
    d.stroke(role, f"M{x1} {y1} L{x2} {y2}", w, shadow=True)
    d.stroke(role, f"M{x1+gap} {y1+gap*0.5} L{x2+gap*0.25} {y2+gap*0.9}", w, shadow=True)


@framed
def noodles(d: Drawing):
    d.disc("glow", 100, 96, 70, line=False)
    steam(d, [62, 140], 98, 26)
    chopsticks(d, 160, 26, 104, 70, 8, w=5)
    for x0, x1 in [(98, 70), (104, 84), (110, 100), (116, 114)]:
        d.stroke("hero2", f"M{x0} 70 C{x0 - 4} 84 {x1 + 6} 96 {x1} 116", 3.4, shadow=True)
    d.shape("hero", "M30 112 H170 C170 146 142 166 100 166 C58 166 30 146 30 112Z", spot=True)
    d.shape("mark", ellipse(100, 112, 70, 13), shadow=False)
    d.shape("pop", ellipse(100, 114, 64, 9), shadow=False, line=False)
    d.stroke("hero2", "M48 112 q8 -6 16 0 t16 0 M118 114 q8 -6 16 0 t16 0", 3, line=False)
    d.shape("light", ellipse(136, 110, 13, 7.5))
    d.shape("glow2", circle(138, 110, 5), shadow=False)
    d.shape("near", "M52 108 L60 102 L64 110Z M66 104 L72 100 L74 108Z", shadow=False, line=False)
    d.stroke("light", "M40 130 Q100 150 160 130", 4.5, line=False)
    d.stroke("pop", "M54 140 Q60 146 66 140 M134 140 Q140 146 146 140", 2.4)
    d.shape("dark", rrect(76, 164, 48, 6, 3), shadow=False)


# ================================================================ BURGER
@framed
def burger(d: Drawing):
    d.disc("glow", 100, 100, 72, line=False)
    d.shape("hero2", "M34 140 H166 Q166 162 146 162 H54 Q34 162 34 140Z")
    d.shape("mark", rrect(30, 118, 140, 22, 11))
    d.shape("pop", "M30 112 Q40 124 52 114 Q64 126 76 114 Q88 126 100 114 Q112 126 124 114 Q136 126 148 114 Q160 126 170 112 V118 H30Z")
    d.shape("glow2", "M34 108 H166 L160 120 L150 128 L144 120 H120 L110 132 L102 120 H62 L52 130 L46 120 Z", shadow=False, spot=True)
    d.shape("near", "M28 104 Q36 96 44 104 Q52 96 60 104 Q68 96 76 104 Q84 96 92 104 Q100 96 108 104 Q116 96 124 104 "
                     "Q132 96 140 104 Q148 96 156 104 Q164 96 172 104 Q164 114 156 108 Q148 116 140 108 Q132 116 124 108 "
                     "Q116 116 108 108 Q100 116 92 108 Q84 116 76 108 Q68 116 60 108 Q52 116 44 108 Q36 114 28 104Z")
    d.shape("hero2", "M30 100 Q30 44 100 44 Q170 44 170 100 Q170 106 164 106 H36 Q30 106 30 100Z")
    d.stroke("light", "M52 72 Q60 58 76 54", 4, line=False)
    for x, y, r in [(70, 66, -20), (92, 58, 0), (116, 60, 15), (136, 70, 30), (84, 80, -10), (110, 78, 10), (128, 88, 25), (58, 88, -30)]:
        d.marks("light", f"M{x-3.4} {y} a3.4 1.8 {r} 1 0 6.8 0 a3.4 1.8 {r} 1 0 -6.8 0Z")


# ================================================================ CHICKEN
@framed
def chicken(d: Drawing):
    d.disc("glow", 100, 96, 66, line=False)
    d.band("far", hills(140, 6, 10))
    d.stroke("dark", "M-30 128 H230 M-30 144 H230", 3, line=False)
    for x in (14, 186):
        d.shape("ground", rrect(x - 4, 116, 8, 40, 2), shadow=False, line=False)
    # legs
    d.limb("pop", "M88 140 V164 M108 140 V164", 4.5)
    d.stroke("pop", "M80 166 H96 M100 166 H116 M88 164 L84 160 M108 164 L104 160", 3)
    # tail feathers
    d.shape("hero2", "M48 112 Q20 92 34 50 Q46 72 62 80 Q46 54 58 36 Q66 70 82 88Z")
    # body (plump), head, wing
    d.shape("hero", "M40 104 Q40 76 70 78 Q92 80 110 70 Q118 50 132 42 Q154 36 160 58 Q164 74 154 86 Q160 112 146 134 Q128 154 92 152 Q48 150 40 104Z")
    d.shape("hero2", "M68 104 Q86 86 118 96 Q126 118 104 132 Q78 134 68 104Z", shadow=False, spot=True)
    d.stroke("hero", "M86 110 Q98 106 110 112 M84 120 Q96 116 106 122", 2, line=False)
    # comb, wattle, beak, eye
    d.shape("pop", "M126 44 Q124 30 134 34 Q136 22 146 30 Q154 24 156 36 Q160 42 152 46Z", spot=True)
    d.shape("pop", "M156 68 Q164 74 158 84 Q150 84 150 74Z", shadow=False, spot=True)
    d.shape("glow2", "M158 56 L174 62 L158 68Z")
    d.marks("dark", circle(144, 54, 3.4))
    d.marks("light", circle(145, 53, 1))
    d.band("ground", "M-30 160 Q100 152 230 160")
    d.band("near", hills(182, 4, 10), line=False)


# ================================================================ COW
@framed
def cow(d: Drawing):
    d.disc("far", 100, 92, 66, line=False)
    d.band("mid", hills(136, 8, -10))
    d.band("near", "M-30 156 Q100 146 230 156")
    # back legs
    d.limb("light", "M54 124 V158 M140 124 V158", 11)
    # tail
    d.stroke("light", "M38 96 Q30 116 32 134", 3)
    d.shape("dark", "M28 132 Q32 128 36 132 L34 142 Z", shadow=False)
    body = "M38 100 Q38 78 60 76 H134 Q150 76 152 92 L154 120 Q154 132 140 132 H54 Q38 132 38 112Z"
    d.shape("light", body)
    d.limb("light", "M70 124 V160 M126 124 V160", 11, shadow=False)
    d.shape("dark", "M62 77 Q78 76 86 84 Q90 98 78 104 Q64 106 58 96 Q54 84 62 77Z", shadow=False)
    d.shape("dark", "M108 96 Q122 92 130 102 Q132 116 118 120 Q104 118 104 108Z", shadow=False)
    d.shape("dark", "M38 100 Q38 86 46 82 Q52 92 46 104 Q42 110 38 110Z", shadow=False)
    d.shape("pop", "M84 132 Q90 142 100 142 Q110 142 112 132Z", spot=True)
    for x in (70, 126, 54, 140):
        d.shape("dark", rrect(x - 6, 154, 12, 7, 2), shadow=False)
    # head
    d.shape("light", "M150 72 L176 64 L172 74Z")
    d.shape("ground", "M136 58 Q132 48 140 44 Q140 52 146 58Z M168 58 Q174 48 166 44 Q166 52 160 58Z")
    d.shape("light", "M136 64 Q138 54 152 54 Q166 54 168 64 L170 98 Q170 110 160 110 H146 Q136 110 136 98Z")
    d.shape("dark", "M130 62 Q120 60 122 70 Q130 72 138 68Z")
    d.shape("dark", "M174 62 Q184 60 182 70 Q174 72 166 68Z")
    d.shape("dark", "M142 56 Q152 52 158 58 Q152 66 146 64Z", shadow=False)
    d.shape("pop", rrect(136, 90, 34, 22, 11), shadow=False, spot=True)
    d.marks("dark", ellipse(146, 100, 2.4, 3.2) + ellipse(160, 100, 2.4, 3.2))
    d.marks("dark", circle(144, 74, 3) + circle(162, 74, 3))
    d.shape("glow2", "M146 116 H160 L158 130 H148Z", spot=True)
    d.stroke("dark", "M148 110 Q153 116 158 110", 1.6)


# ================================================================ DOG
@framed
def dog(d: Drawing):
    d.disc("glow", 100, 100, 70, line=False)
    d.band("ground", "M-30 168 Q100 162 230 168")
    # tail
    d.limb("hero", "M134 150 Q160 140 160 112", 8)
    # sitting body
    d.shape("hero", "M66 168 Q58 128 76 104 H124 Q142 128 134 168Z")
    d.shape("light", "M86 108 H114 Q120 130 110 150 H90 Q80 130 86 108Z", shadow=False)
    d.shape("hero", rrect(74, 140, 18, 30, 9))
    d.shape("hero", rrect(108, 140, 18, 30, 9))
    d.stroke("dark", "M80 166 V170 M86 166 V170 M114 166 V170 M120 166 V170", 1.4, line=False)
    # collar + tag
    d.shape("pop", "M72 104 Q100 116 128 104 L130 112 Q100 124 70 112Z", spot=True)
    d.shape("glow2", circle(100, 122, 5))
    # head
    d.shape("hero", "M60 72 Q60 38 100 38 Q140 38 140 72 Q140 104 100 106 Q60 104 60 72Z")
    d.shape("hero2", "M64 50 Q46 46 42 70 Q40 92 54 96 Q66 92 68 70Z")
    d.shape("hero2", "M136 50 Q154 46 158 70 Q160 92 146 96 Q134 92 132 70Z")
    d.shape("hero2", "M104 40 Q124 40 128 56 Q118 64 106 58Z", shadow=False)
    d.shape("light", "M78 92 Q78 74 100 74 Q122 74 122 92 Q122 104 100 104 Q78 104 78 92Z", shadow=False)
    d.shape("pop", "M94 100 Q94 114 100 114 Q106 114 106 100Z", spot=True)
    d.marks("dark", "M92 80 Q100 76 108 80 Q108 88 100 90 Q92 88 92 80Z")
    d.stroke("dark", "M100 90 V96 M90 96 Q100 102 110 96", 2)
    d.marks("dark", circle(84, 66, 4.4) + circle(116, 66, 4.4))
    d.marks("light", circle(85.5, 64.5, 1.4) + circle(117.5, 64.5, 1.4))


# ================================================================ COMPASS: brass pocket compass
@framed
def compass_brass(d: Drawing):
    d.disc("glow", 100, 100, 72, line=False)
    # open lid behind (inside of the lid, tilted back)
    d.shape("hero", ellipse(100, 58, 50, 24))
    d.shape("hero2", ellipse(100, 58, 42, 18), shadow=False)
    d.stroke("light", "M74 52 Q90 44 110 46", 3, line=False)
    d.shape("hero", rrect(88, 78, 24, 10, 4))
    # crown + ring on the right
    d.shape("hero", rrect(156, 116, 12, 10, 3))
    d.stroke("hero", circle(176, 121, 9), 5, shadow=True)
    # case
    d.shape("hero", circle(100, 122, 54))
    d.shape("hero2", circle(100, 122, 47), shadow=False)
    d.shape("light", circle(100, 122, 42), shadow=False)
    # ticks
    ticks = []
    for deg in range(0, 360, 30):
        x1, y1 = pol(100, 122, 40, deg)
        x2, y2 = pol(100, 122, 34 if deg % 90 == 0 else 37, deg)
        ticks.append(f"M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}")
    d.stroke("dark", " ".join(ticks), 1.8)
    # N mark (a small triangle, no lettering)
    d.marks("pop", "M100 86 L104 94 H96Z")
    # needle
    d.shape("pop", "M100 122 L94 120 L104 92Z M100 122 L106 124 L104 92Z", shadow=False, spot=True)
    d.shape("dark", "M100 122 L106 124 L96 152Z M100 122 L94 120 L96 152Z", shadow=False)
    d.marks("hero", circle(100, 122, 4))
    d.stroke("light", "M66 104 Q72 88 86 82", 3, line=False)


# ================================================================ COMPASS: 16-point rose on old paper
def fleur(cx, top):
    """Fleur-de-lis pointing up, tip at (cx, top), ~20 tall."""
    t = top
    return (f"M{cx} {t} Q{cx + 6} {t + 7} {cx + 2} {t + 16} Q{cx + 8} {t + 9} {cx + 12} {t + 10} Q{cx + 12} {t + 16} {cx + 4} {t + 19} "
            f"H{cx - 4} Q{cx - 12} {t + 16} {cx - 12} {t + 10} Q{cx - 8} {t + 9} {cx - 2} {t + 16} Q{cx - 6} {t + 7} {cx} {t}Z")


@framed
def compass_rose(d: Drawing):
    d.band("ground", "M-30 -30 H230", line=False)
    d.stroke("mark", "M-30 60 Q40 50 100 64 T230 60 M-30 150 Q50 140 110 152 T230 146", 1.4, line=False)
    d.stroke("mark", circle(100, 104, 62), 2)
    d.stroke("mark", circle(100, 104, 56), 1.2)
    cx, cy = 100, 104
    # 8 small points (by-points)
    for deg in range(0, 360, 45):
        a = deg + 22.5
        tx, ty = pol(cx, cy, 44, a)
        lx, ly = pol(cx, cy, 10, a - 22.5)
        rx, ry = pol(cx, cy, 10, a + 22.5)
        d.shape("near", f"M{tx:.1f} {ty:.1f} L{lx:.1f} {ly:.1f} L{cx} {cy} L{rx:.1f} {ry:.1f}Z", shadow=False)
    # 4 intercardinal + 4 cardinal points, two-tone halves
    for deg, R, w, a1, a2 in [(45, 46, 11, "hero2", "hero"), (135, 46, 11, "hero2", "hero"), (225, 46, 11, "hero2", "hero"), (315, 46, 11, "hero2", "hero"),
                               (0, 62, 13, "light", "dark"), (90, 62, 13, "light", "dark"), (180, 62, 13, "light", "dark"), (270, 62, 13, "light", "dark")]:
        tx, ty = pol(cx, cy, R, deg)
        lx, ly = pol(cx, cy, w, deg - 45)
        rx, ry = pol(cx, cy, w, deg + 45)
        d.shape(a1, f"M{tx:.1f} {ty:.1f} L{lx:.1f} {ly:.1f} L{cx} {cy}Z", shadow=deg % 90 == 0)
        d.shape(a2, f"M{tx:.1f} {ty:.1f} L{rx:.1f} {ry:.1f} L{cx} {cy}Z", shadow=False, spot=deg % 90 == 0)
    d.shape("pop", circle(cx, cy, 7), spot=True)
    d.marks("ground", circle(cx, cy, 2.6))
    d.shape("pop", fleur(100, 18), spot=True)


# ================================================================ COMPASS: baseplate hiking compass
@framed
def compass_baseplate(d: Drawing):
    d.disc("glow", 100, 100, 72, line=False)
    d.stroke("far", "M20 150 Q60 120 100 140 T180 128 M30 166 Q70 140 110 156 T190 146 M14 70 Q40 56 64 70", 2, line=False)

    def plate():
        d.shape("light", "M76 18 H124 Q134 18 134 28 V172 Q134 184 122 184 H78 Q66 184 66 172 V28 Q66 18 76 18Z")
        d.shape("pop", "M100 26 L110 48 H90Z", shadow=False, spot=True)
        d.stroke("dark", "M100 50 V70", 2.4)
        d.stroke("dark", "M70 34 H76 M70 44 H74 M70 54 H76 M70 64 H74 M70 74 H76 M124 34 H130 M126 44 H130 M124 54 H130 M126 64 H130 M124 74 H130", 1.4)
        d.shape("hero", circle(100, 124, 40))
        d.shape("light", circle(100, 124, 32), shadow=False)
        ticks = []
        for deg in range(0, 360, 15):
            x1, y1 = pol(100, 124, 39, deg)
            x2, y2 = pol(100, 124, 34, deg)
            ticks.append(f"M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}")
        d.stroke("light", " ".join(ticks), 1.4, line=False)
        d.stroke("far", "M88 96 V152 M112 96 V152", 1.4, line=False)
        d.shape("far", "M100 94 L106 104 H94Z", shadow=False, line=False)
        d.shape("pop", "M100 124 L94 122 L100 96Z M100 124 L106 126 L100 96Z", shadow=False, spot=True)
        d.shape("dark", "M100 124 L106 126 L100 152Z M100 124 L94 122 L100 152Z", shadow=False)
        d.marks("hero", circle(100, 124, 3.4))
        d.marks("dark", circle(100, 174, 4))
    group(d, "rotate(-24 100 100) translate(100 100) scale(.84) translate(-100 -100)", plate)


# ================================================================ concepts
BRASS = {"hero": "#C9962E", "hero2": "#E8C46A", "light": "#FBF5E6"}
WOOD_BROWN = "#7A4A2A"
CONCEPTS = [
    Concept("basic-car", "basic-car", "Car", car,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero", "ground"), ("hero2", "hero"), ("light", "hero")],
            fixes={"glow": ["far", "sky2", "mid"], "hero2": ["light", "glow2", "pop"], "hero": ["pop", "deep"]}),
    Concept("basic-convertible", "basic-convertible", "Convertible", convertible,
            checks=[("hero", "glow"), ("hero", "far"), ("hero", "ground"), ("hero2", "hero"), ("light", "glow")],
            fixes={"glow": ["far", "sky2", "mid"], "hero2": ["light", "glow2"], "hero": ["pop", "deep"]}),
    Concept("basic-sailboat", "basic-sailboat", "Sailboat", sailboat, SEA,
            checks=[("light", "far"), ("hero", "near"), ("hero", "mid"), ("dark", "far")],
            fixes={"far": ["mid", "near"], "hero": ["pop", "dark", "deep"]}),
    Concept("basic-speedboat", "basic-speedboat", "Speedboat", speedboat, SEA,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "mid"), ("light", "mid"), ("hero2", "hero")],
            fixes={"hero": ["pop", "deep"], "hero2": ["dark", "glow2"]}),
    Concept("basic-train", "basic-train", "Train", train,
            checks=[("hero", "glow"), ("hero", "far"), ("hero2", "hero"), ("light", "glow")],
            fixes={"glow": ["far", "sky2", "mid"], "hero2": ["glow2", "pop", "light"], "hero": ["pop", "deep"]}),
    Concept("basic-plane", "basic-plane", "Plane", plane,
            checks=[("light", "far"), ("hero", "light")], fixes={"far": ["mid", "near"]}),
    Concept("basic-bicycle", "basic-bicycle", "Bicycle", bicycle,
            checks=[("hero", "glow"), ("dark", "glow"), ("hero", "far"), ("hero2", "glow")],
            fixes={"glow": ["far", "sky2", "light"], "hero": ["pop", "deep"]}),
    Concept("basic-motorbike", "basic-motorbike", "Motorbike", motorbike,
            checks=[("hero", "glow"), ("dark", "glow"), ("hero", "far")],
            fixes={"glow": ["far", "sky2", "light"], "hero": ["pop", "deep"]}),
    Concept("basic-bus", "basic-bus", "Bus", bus,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero2", "hero"), ("light", "hero"), ("hero", "ground")],
            fixes={"glow": ["far", "sky2", "mid"], "hero2": ["light", "glow2", "pop"], "hero": ["pop", "deep"]}),
    Concept("basic-suitcase", "basic-suitcase", "Suitcase", suitcase, overrides={"hero": "#B5651D", "hero2": "#D98E4A", "dark": "#4A2E1A"},
            checks=[("hero", "glow"), ("pop", "hero")], fixes={"glow": ["far", "sky2", "mid", "light"]}),
    Concept("basic-backpack", "basic-backpack", "Backpack", backpack,
            checks=[("hero", "glow"), ("hero2", "hero"), ("hero2", "glow")],
            fixes={"glow": ["far", "sky2", "mid"], "hero2": ["glow2", "pop", "light"]}),
    Concept("basic-camera", "basic-camera", "Camera", camera, overrides={"hero": "#C9CED6", "hero2": "#5FA8D3"},
            checks=[("hero", "glow"), ("dark", "glow")], fixes={"glow": ["far", "mid", "near", "deep"]}),
    Concept("basic-tent", "basic-tent", "Tent", tent,
            checks=[("hero", "far"), ("hero", "ground"), ("hero2", "hero"), ("hero", "sky")],
            fixes={"hero": ["pop", "deep"], "hero2": ["glow2", "light"]}),
    Concept("basic-cocktail", "basic-cocktail", "Cocktail", cocktail, overrides={"hero": "#F25C78", "near": "#6A994E", "glow2": "#C5E07A"},
            checks=[("light", "glow"), ("hero", "light"), ("pop", "glow")], fixes={"glow": ["far", "mid", "near", "deep"]}),
    Concept("basic-beer", "basic-beer", "Beer", beer, overrides={"hero": "#F2A93B", "hero2": "#FFE08A"},
            checks=[("light", "glow"), ("hero", "glow")], fixes={"glow": ["far", "mid", "near", "deep"]}),
    Concept("basic-wine", "basic-wine", "Wine", wine, overrides={"hero": "#2F4A3A", "pop": "#8E1B3A"},
            checks=[("light", "glow"), ("hero", "glow")], fixes={"glow": ["far", "mid", "glow2"]}),
    Concept("basic-coffee", "basic-coffee", "Coffee", coffee, overrides={"ground": "#8B5A2B"},
            checks=[("hero", "glow"), ("hero2", "glow"), ("light", "glow")], fixes={"glow": ["far", "mid", "near"], "hero2": ["light", "glow2"]}),
    Concept("basic-noodles", "basic-noodles", "Noodles", noodles, overrides={"pop": "#E8B04B", "hero2": "#F6DFA0", "mark": "#B5651D"},
            checks=[("hero", "glow"), ("light", "glow"), ("hero2", "glow")], fixes={"glow": ["near", "deep", "mid"]}),
    Concept("basic-burger", "basic-burger", "Burger", burger,
            overrides={"hero2": "#E9A25F", "mark": "#6B3B24", "pop": "#E4572E", "near": "#7BB662", "glow2": "#FFC93C", "light": "#FFF6E0"},
            checks=[("hero2", "glow"), ("near", "glow")], fixes={"glow": ["far", "mid", "deep", "sky2"]}),
    Concept("basic-chicken", "basic-chicken", "Chicken", chicken,
            overrides={"hero": "#D9823B", "hero2": "#A8582A", "pop": "#E0352B", "glow2": "#F4B33A"},
            checks=[("hero", "glow"), ("hero2", "sky"), ("hero", "far")], fixes={"glow": ["sky2", "far", "light", "mid"]}),
    Concept("basic-cow", "basic-cow", "Cow", cow, overrides={"light": "#FFFFFF", "dark": "#2B2B2B", "pop": "#F2A7A0", "ground": "#D8C9A8"},
            checks=[("light", "far"), ("light", "mid"), ("light", "near")], fixes={"far": ["mid", "near", "deep"]}),
    Concept("basic-dog", "basic-dog", "Dog", dog, overrides={"hero": "#D9A066", "hero2": "#8B5A2B", "light": "#F6E7CF", "dark": "#2B2220"},
            checks=[("hero", "glow"), ("hero2", "glow"), ("hero", "ground")], fixes={"glow": ["far", "mid", "sky2", "near"], "ground": ["near", "mid"]}),
    Concept("basic-compass-brass", "basic-compass", "Compass (brass pocket)", compass_brass, overrides=BRASS,
            checks=[("hero", "glow"), ("hero", "sky")], fixes={"glow": ["far", "mid", "near", "deep"]}),
    Concept("basic-compass-rose", "basic-compass", "Compass rose", compass_rose, overrides={"ground": "#F1DFB6", "mark": "#B08A5A", "light": "#FFF8E8"},
            checks=[("dark", "ground"), ("hero", "ground"), ("hero2", "ground"), ("pop", "ground"), ("light", "dark")],
            fixes={"hero2": ["far", "mid", "glow"], "hero": ["near", "deep"]}),
    Concept("basic-compass-hiking", "basic-compass", "Compass (hiking)", compass_baseplate,
            checks=[("light", "glow"), ("hero", "light"), ("hero", "glow")], fixes={"glow": ["far", "mid", "near"]}),
]
