"""Mapsie Originals: famous European landmarks, second set (one concept each)."""
import math

from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group  # noqa: F401


# ================================================================ private helpers (copied, not imported)
def poly(*pts, close=True) -> str:
    s = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    return s + ("Z" if close else "")


def battlement(x, y, w, h, n, mh=6.0) -> str:
    """A wall block (x, y, w, h) whose top edge has n merlons (crenellations)."""
    mw = w / (2 * n - 1)
    s = f"M{x:g} {y + h:g} V{y:g}"
    for i in range(n):
        x0 = x + 2 * i * mw
        s += f" H{x0 + mw:g}"
        if i < n - 1:
            s += f" V{y + mh:g} H{x0 + 2 * mw:g} V{y:g}"
    return s + f" V{y + h:g}Z"


def arch(x, y, w, h) -> str:
    """Round-topped opening, (x, y) top-left of its bounding box."""
    r = w / 2
    return f"M{x:g} {y + h:g} V{y + r:g} A{r:g} {r:g} 0 0 1 {x + w:g} {y + r:g} V{y + h:g}Z"


def garch(x, y, w, h) -> str:
    """Pointed (gothic) opening, (x, y) top-left of its bounding box."""
    return (f"M{x:g} {y + h:g} V{y + w * .7:g} Q{x:g} {y + w * .15:g} {x + w / 2:g} {y:g} "
            f"Q{x + w:g} {y + w * .15:g} {x + w:g} {y + w * .7:g} V{y + h:g}Z")


def birds(d: Drawing, pts, role="dark"):
    s = " ".join(f"M{x} {y} q{3 * k} {-3 * k} {6 * k} 0 q{3 * k} {-3 * k} {6 * k} 0" for x, y, k in pts)
    d.stroke(role, s, 1.7)


def pine(x, y, s=1.0) -> str:
    return (f"M{x} {y - 40 * s} L{x + 11 * s} {y - 16 * s} L{x + 6 * s} {y - 16 * s} L{x + 14 * s} {y} L{x - 14 * s} {y} "
            f"L{x - 6 * s} {y - 16 * s} L{x - 11 * s} {y - 16 * s}Z")


def cypress(x, y, h, w=5.0) -> str:
    return (f"M{x} {y - h} C{x + w * .9} {y - h * .7} {x + w} {y - h * .3} {x + w * .6} {y} H{x - w * .6} "
            f"C{x - w} {y - h * .3} {x - w * .9} {y - h * .7} {x} {y - h}Z")


def bushes(y, r=9, step=14, x0=-30, x1=230, jitter=(0, 4, 1, 5, 2)) -> str:
    """A bumpy tree-line edge (for band())."""
    s = f"M{x0} {y}"
    x, i = x0, 0
    while x < x1:
        dy = jitter[i % len(jitter)]
        s += f" Q{x + step / 2} {y - r - dy} {x + step} {y}"
        x += step
        i += 1
    return s


def blob(x0, x1, y, r=8, step=12, jitter=(0, 4, 1, 5, 2), base=None) -> str:
    """A closed tree clump: bumpy top from x0 to x1 at height y, flat bottom at `base`."""
    base = y + 30 if base is None else base
    return bushes(y, r, step, x0, x1, jitter) + f" L{x1} {base} L{x0} {base}Z"


def clip_to(d: Drawing, outline: str, fn):
    """Draw fn() clipped to an outline."""
    n = getattr(d, "_lm2_clip", 0) + 1
    d._lm2_clip = n
    cid = f"lm2c{n}"
    d.raw(f'<clipPath id="{cid}"><path d="{outline}"/></clipPath><g clip-path="url(#{cid})">',
          f'<clipPath id="{cid}"><path d="{outline}"/></clipPath><g clip-path="url(#{cid})">')
    fn()
    d.raw("</g>", "</g>")


def ink(d: Drawing, role: str, path: str, w: float, line_w: float = 1.4):
    """Thin detail line: palette colour in papercut, fine ink in line style."""
    if d.paper:
        d.stroke(role, path, w)
    else:
        d.raw("", f'<path d="{path}" fill="none" stroke="{d.c["ink"]}" stroke-width="{line_w}" stroke-linecap="round" stroke-linejoin="round"/>')


def dark_sky(d: Drawing) -> bool:
    if not d.paper:
        return False
    h = d.c["sky"].lstrip("#")
    return sum(int(h[i:i + 2], 16) for i in (0, 2, 4)) < 300


# ================================================================ NOTRE-DAME
def notre_dame(d: Drawing):
    d.disc("glow", 166, 56, 12)
    d.shape("light", cloud(8, 58, 0.9))
    d.shape("light", cloud(150, 84, 0.7))
    birds(d, [(22, 92, .8), (34, 86, .6)])
    # the new spire, rising behind the gallery
    d.shape("lead", "M96.8 66 L100 10 L103.2 66Z")
    d.shape("lead", rrect(93.5, 54, 13, 12, 1))
    d.stroke("lead", "M100 11 V4", 1.4)
    # trees along the quai
    d.shape("mid", blob(-30, 58, 128, 10, 14, base=170))
    d.shape("mid", blob(142, 230, 124, 10, 14, base=170))
    # west front
    d.shape("stone", "M52 162 V36 H82 V62 H118 V36 H148 V162Z")
    d.shape("stone", rrect(50, 33, 34, 4, 1))
    d.shape("stone", rrect(116, 33, 34, 4, 1))
    for tx in (52, 118):
        d.marks("hole", garch(tx + 5, 41, 8, 21))
        d.marks("hole", garch(tx + 17, 41, 8, 21))
        d.marks("hole", garch(tx + 6, 86, 7, 20))
        d.marks("hole", garch(tx + 17, 86, 7, 20))
    for i in range(16):
        d.marks("hole", arch(54.2 + i * 5.85, 65, 3.4, 10))
    for i in range(18):
        d.marks("hole", arch(54.6 + i * 5.2, 119, 3, 6.5))
    ink(d, "stone2", "M52 63 H148 M52 78 H148 M52 117 H148 M52 127 H148", 1.6, 1.2)
    ink(d, "stone2", "M82 36 V162 M118 36 V162", 1.8, 1.2)
    # rose window
    d.shape("rose", circle(100, 97, 13.5), shadow=False, spot=True)
    spokes = " ".join(f"M{100 + 5 * math.cos(a):.1f} {97 + 5 * math.sin(a):.1f} L{100 + 13 * math.cos(a):.1f} {97 + 13 * math.sin(a):.1f}"
                      for a in [k * math.pi / 6 for k in range(12)])
    ink(d, "stone", spokes + " " + circle(100, 97, 5) + " " + circle(100, 97, 13.5), 1.3, 1.1)
    # three portals
    d.shape("hole", garch(86, 130, 28, 32), shadow=False)
    d.shape("hole", garch(57, 135, 20, 27), shadow=False)
    d.shape("hole", garch(123, 135, 20, 27), shadow=False)
    ink(d, "stone2", "M88 148 H112 M100 148 V162 M59 151 H75 M125 151 H141", 1.4, 1.1)
    # quai and the Seine
    d.band("near", "M-30 162 H230")
    d.band("mid", waves(172, 2.5, 22))
    d.stroke("light", "M30 180 h14 M120 184 h18", 2, line=False)
    d.band("deep", waves(188, 2.5, 30), line=False)


# ================================================================ BRANDENBURG GATE
def horse_head(x, k=1) -> str:
    """Arched neck and head of a quadriga horse rising from the plinth at y=77; k=1 faces left, -1 right."""
    X = lambda dx: x + k * dx
    return (f"M{X(7)} 77 L{X(7)} 63 Q{X(6)} 54 {X(0)} 51.5 L{X(-0.5)} 47.5 L{X(-2.5)} 51.5 L{X(-9)} 56.5 L{X(-10.5)} 60 "
            f"L{X(-7)} 61.8 L{X(-2)} 60.5 Q{X(0)} 66 {X(-2)} 77Z")


def brandenburg(d: Drawing):
    d.disc("glow", 160, 46, 12)
    d.shape("light", cloud(10, 54, 0.9))
    d.shape("light", cloud(146, 74, 0.6))
    d.band("mid", bushes(142, 12, 18))
    # side wings
    for x0 in (-14, 172):
        d.shape("stone", rrect(x0, 126, 42, 32, 0.5))
        d.shape("stone", f"M{x0 - 2} 127 L{x0 + 21} 116 L{x0 + 44} 127Z")
        for k in range(3):
            d.marks("shade", rrect(x0 + 6 + k * 12, 132, 6, 26, 0.5))
    # main gate
    d.shape("stone", "M20 160 V92 H70 V82 H130 V92 H180 V160Z", spot=True)
    cols = [29, 55, 81, 119, 145, 171]
    for a, b in zip(cols, cols[1:]):
        d.shape("shade", f"M{a + 4.5} 153 V118 H{b - 4.5} V153Z", shadow=False)
    for cx in cols:
        d.shape("stone", rrect(cx - 6.5, 115.5, 13, 3.5, 1), shadow=False)
        ink(d, "stone2", f"M{cx - 1.5} 120 V152 M{cx + 1.5} 120 V152", 0.9, 0.9)
    ink(d, "stone2", "M20 104 H180 M20 110 H180 M20 92 H180", 1.4, 1.2)
    d.stroke("stone2", " ".join(f"M{x} 105.5 V109" for x in range(24, 178, 6)), 1.2, line=False)
    for x0, x1 in [(28, 64), (136, 172)]:
        ink(d, "stone2", rrect(x0, 95, x1 - x0, 6, 0.5), 1, 0.9)
    ink(d, "stone2", rrect(78, 85, 44, 5, 0.5), 1, 0.9)
    d.shape("stone", rrect(14, 153, 172, 8, 0.5))
    # the Quadriga: Victoria with her standard, four horses abreast
    d.shape("bronze", rrect(76, 77, 48, 6, 1))
    d.stroke("bronze", "M110 64 L118 26", 2)
    d.shape("bronze", circle(119, 24, 4.6))
    d.marks("stone", circle(119, 24, 2.4))
    d.shape("bronze", "M117 18 L119 13 L121 18Z", shadow=False)
    d.shape("bronze", "M96 50 Q84 36 86 26 Q94 34 98 44Z M104 50 Q116 36 114 26 Q106 34 102 44Z")
    d.shape("bronze", "M95 68 L97 50 Q100 46 103 50 L105 68Z")
    d.shape("bronze", circle(100, 45, 3.4))
    d.limb("bronze", "M103 54 L110 62", 2.6, shadow=False)
    for x, k in [(92, 1), (84, 1), (108, -1), (116, -1)]:
        d.shape("bronze", horse_head(x, k))
    d.band("ground", "M-30 161 H230")
    d.band("near", hills(182, 3, 20), line=False)


# ================================================================ COLOGNE CATHEDRAL
def crockets(x0, y0, x1, y1, n, side) -> str:
    """Little hooked bumps along a spire edge."""
    s = ""
    for i in range(1, n):
        t = i / n
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        s += f"M{x:.1f} {y:.1f} l{side * 2.6:.1f} -1.2 l{-side * 1.2:.1f} -2.4Z "
    return s


def cologne_tower(d: Drawing, cx):
    d.shape("stone", rrect(cx - 15, 84, 30, 90, 0.5))
    d.shape("stone", rrect(cx - 11.5, 68, 23, 18, 0.5))
    spire = poly((cx - 10.5, 70), (cx - 1.6, 20), (cx + 1.6, 20), (cx + 10.5, 70))
    d.shape("stone", spire, spot=True)
    d.shape("stone", crockets(cx - 10.5, 70, cx - 1.6, 20, 8, -1) + crockets(cx + 10.5, 70, cx + 1.6, 20, 8, 1), shadow=False)
    d.shape("stone", poly((cx - 2.2, 21), (cx, 11), (cx + 2.2, 21)), shadow=False)
    d.shape("stone", "M{0} 12 h-4 v-2.4 h4 v-4 h2.4 v4 h4 v2.4 h-4 v4 h-2.4Z".format(cx - 1.2), shadow=False)
    for k, y in enumerate((60, 48, 36)):
        d.marks("hole", ellipse(cx, y, 2.2 - k * .4, 2.6 - k * .4))
    ink(d, "stone2", f"M{cx - 9.4} 64 H{cx + 9.4} M{cx - 7.4} 52 H{cx + 7.4} M{cx - 5.4} 40 H{cx + 5.4} M{cx - 3.5} 30 H{cx + 3.5}", 1.2, 1)
    for sx in (-1, 1):
        d.shape("stone", poly((cx + sx * 15.5, 86), (cx + sx * 13.5, 64), (cx + sx * 11.5, 86)), shadow=False)
        d.shape("stone", poly((cx + sx * 9.5, 70), (cx + sx * 8.2, 58), (cx + sx * 7, 70)), shadow=False)
    d.marks("hole", garch(cx - 7.5, 70, 6, 14))
    d.marks("hole", garch(cx + 1.5, 70, 6, 14))
    d.marks("hole", garch(cx - 8, 92, 16, 34))
    d.marks("hole", garch(cx - 6, 136, 12, 24))
    ink(d, "stone2", f"M{cx} 96 V126 M{cx - 15} 132 H{cx + 15} M{cx - 15} 88 H{cx + 15}", 1.2, 1)


def cologne(d: Drawing):
    d.disc("glow", 166, 70, 12)
    d.shape("light", cloud(150, 100, 0.7))
    d.shape("light", cloud(4, 64, 0.9))
    birds(d, [(30, 98, .8), (42, 92, .6)])
    # nave gable between the towers
    d.shape("stone", "M84 174 V104 L100 80 L116 104 V174Z")
    d.shape("stone", poly((99, 82), (100, 66), (101, 82)), shadow=False)
    d.marks("hole", garch(91, 100, 18, 30))
    d.marks("hole", garch(92, 140, 16, 26))
    ink(d, "stone2", "M100 104 V130 M84 134 H116", 1.2, 1)
    cologne_tower(d, 70)
    cologne_tower(d, 130)
    # Hohenzollern bridge over the Rhine
    d.band("mid", waves(166, 2, 20))
    for x0, x1 in [(-40, 40), (40, 120), (120, 200), (200, 280)]:
        d.limb("steel", f"M{x0} 166 Q{(x0 + x1) / 2} 132 {x1} 166", 3.2, spot=True)
        hang = " ".join(f"M{x:.0f} {166 - 34 * (1 - ((x - (x0 + x1) / 2) / ((x1 - x0) / 2)) ** 2) / 2 * 1.0:.1f} V164"
                        for x in range(x0 + 10, x1 - 5, 10))
        d.stroke("steel", hang, 1.1, line=False)
    d.shape("steel", rrect(-30, 162, 260, 4.5, 0.5))
    d.band("near", waves(176, 2.5, 24))
    d.stroke("light", "M30 184 h14 M130 186 h18", 2, line=False)
    d.band("deep", waves(190, 2.5, 30), line=False)


# ================================================================ CHARLES BRIDGE & PRAGUE CASTLE
def charles_bridge(d: Drawing):
    d.disc("glow", 32, 50, 11)
    d.shape("light", cloud(138, 34, 0.8))
    # castle hill
    d.shape("mid", "M-30 140 V114 Q14 104 50 104 L184 100 Q212 102 230 112 V140Z")
    # St Vitus: west spires, nave, great tower with its copper cupola
    d.shape("vitus", poly((90, 82), (93, 34), (96, 82)))
    d.shape("vitus", poly((100, 82), (103, 34), (106, 82)))
    d.shape("vitus", "M86 100 V80 L94 72 H150 L156 80 V100Z")
    d.shape("vitus", rrect(124, 52, 14, 44, 0.5))
    d.shape("copper", "M122 54 Q122 46 127 43 Q131 34 131 28 Q131 34 135 43 Q140 46 140 54Z", spot=True)
    d.stroke("copper", "M131 28 V22", 1.4)
    d.marks("hole", garch(127.5, 60, 7, 14))
    for x in (100, 112, 142):
        d.marks("hole", garch(x, 84, 5, 12))
    # the long palace
    d.shape("roofc", "M36 99 L42 90 H176 L182 99Z")
    d.shape("castle", rrect(38, 97, 142, 16, 0.5))
    for x in range(42, 178, 7):
        d.marks("hole", rrect(x, 101, 3, 4, 0.6))
        d.marks("hole", rrect(x, 107, 3, 4, 0.6))
    d.shape("mid", blob(-30, 230, 120, 6, 16, base=150), line=False)
    # river behind the bridge (seen through the arches)
    d.band("water", "M-30 132 H230")
    # the bridge
    piers = [56, 96, 136, 176, 216]
    deck = "M48 150 V124 H230 V150"
    for a, b in zip(piers, piers[1:]):
        deck += f" H{b - 5} V146 A{(b - a - 10) / 2} 11 0 0 0 {a + 5} 146 V150"
    d.shape("bstone", deck + " H48Z", spot=True)
    ink(d, "bstone2", "M48 129 H230", 1.6, 1.1)
    for x in [64, 84, 104, 124, 144, 164, 184, 204]:
        d.shape("dark", f"M{x - 2.2} 124 V114 Q{x} 110 {x + 2.2} 114 V124Z M{x} 108.5 a2.2 2.2 0 1 0 0.01 0Z")
    # Old Town Bridge Tower
    def tower():
        d.shape("slate", "M16 68 L32 26 L48 68Z")
        for x in (17, 47):
            d.shape("slate", poly((x - 2, 70), (x, 54), (x + 2, 70)))
        d.shape("btower", rrect(17, 64, 30, 88, 0.5))
        d.shape("btower", battlement(15, 62, 34, 6, 5, 2.5), shadow=False)
        d.marks("hole", garch(28, 76, 8, 14))
        d.marks("hole", rrect(22, 98, 6, 8, 1))
        d.marks("hole", rrect(36, 98, 6, 8, 1))
        d.shape("hole", garch(23, 124, 18, 28), shadow=False)
        ink(d, "bstone2", "M17 92 H47 M17 116 H47", 1.4, 1.1)
    group(d, "translate(7 0)", tower)
    d.band("water", waves(152, 2.5, 22))
    d.stroke("light", "M70 162 h16 M150 166 h18 M20 174 h12", 2, line=False)
    d.band("deep", waves(180, 2.5, 30), line=False)


# ================================================================ HUNGARIAN PARLIAMENT
def spike(x, base, h, w=1.4) -> str:
    return poly((x - w, base), (x, base - h), (x + w, base))


def budapest(d: Drawing):
    d.disc("glow", 38, 56, 11)
    d.shape("light", cloud(150, 40, 0.8))
    # wings: steep roofs with pinnacles
    d.shape("roof", "M6 114 L14 98 H186 L194 114Z")
    d.shape("roof", " ".join(spike(x, 99, 8) for x in range(20, 182, 8)), shadow=False)
    d.shape("stone", rrect(6, 112, 188, 34, 0.5), spot=True)
    for x in range(10, 192, 6):
        if 78 < x < 120:
            continue
        d.marks("hole", garch(x, 117, 3, 9))
        d.marks("hole", garch(x, 131, 3, 9))
    # gabled pavilions and corner towers
    for x in (34, 62, 138, 166):
        d.shape("stone", f"M{x - 8} 113 V100 L{x} 86 L{x + 8} 100 V113Z")
        d.shape("roof", spike(x, 88, 10, 1.6), shadow=False)
        d.shape("stone", spike(x - 8, 102, 9, 1.4) + " " + spike(x + 8, 102, 9, 1.4), shadow=False)
        d.marks("hole", garch(x - 3, 98, 6, 12))
    for x in (8, 192):
        d.shape("stone", rrect(x - 5, 88, 10, 26, 0.5))
        d.shape("roof", poly((x - 6, 90), (x, 72), (x + 6, 90)))
    # central dome
    d.shape("stone", rrect(76, 82, 48, 32, 0.5))
    for x in range(80, 120, 7):
        d.marks("hole", garch(x, 88, 4, 14))
    d.shape("roof", "M78 84 C78 62 90 48 100 42 C110 48 122 62 122 84Z", spot=True)
    ink(d, "stone", "M100 44 V84 M89 52 C85 62 86 74 88 84 M111 52 C115 62 114 74 112 84", 1.4, 1.1)
    d.shape("stone", rrect(96.5, 32, 7, 12, 1))
    d.shape("roof", spike(100, 34, 22, 3.2))
    d.stroke("roof", "M100 12 V6", 1.4)
    for x, h in [(74, 34), (126, 34), (82, 22), (118, 22)]:
        d.shape("stone", spike(x, 86, h, 1.8), shadow=False)
    # the Danube
    d.band("water", waves(146, 2, 22))
    d.stroke("light", "M30 156 h18 M90 160 h22 M150 154 h16", 2.2, line=False)
    d.band("deep", waves(170, 2.5, 26), line=False)
    d.stroke("light", "M60 178 h14 M130 182 h18", 2, line=False)


# ================================================================ ALHAMBRA
def alhambra(d: Drawing):
    d.disc("glow", 160, 40, 11)
    # Sierra Nevada
    d.band("far", "M-30 98 L8 76 L32 86 L66 60 L96 78 L128 54 L160 74 L192 62 L230 82")
    for snow in ["M66 60 L76 70 L70 69 L66 74 L60 68 L56 70Z", "M128 54 L139 66 L133 64 L128 70 L122 64 L118 66Z",
                 "M192 62 L201 71 L196 70 L192 74 L187 69Z", "M8 76 L16 83 L11 82 L7 86 L2 81Z"]:
        d.shape("light", snow, shadow=False)
    d.band("mid", bushes(124, 10, 16))
    # palace roofs behind the walls
    d.shape("roof", "M54 100 L60 92 H112 L118 100Z")
    d.shape("roof", "M150 100 L156 93 H184 L190 100Z")
    # walls and towers (Alcazaba left, Comares right)
    d.shape("wall", battlement(4, 98, 196, 30, 24, 4), spot=True)
    d.shape("wall", battlement(18, 66, 32, 62, 4, 4))
    d.shape("wall", "M28 66 V56 Q34 50 40 56 V66Z")
    d.marks("hole", arch(31.5, 57, 5, 7))
    d.shape("wall", battlement(120, 64, 32, 64, 4, 4))
    d.shape("wall", battlement(74, 84, 16, 44, 2, 3))
    d.shape("wall", battlement(166, 82, 16, 46, 2, 3))
    ink(d, "wall2", "M50 98 V128 M120 98 V128 M18 80 H50 M120 78 H152", 1.4, 1)
    for x, y in [(26, 84), (38, 84), (128, 82), (140, 82), (80, 94), (172, 92)]:
        d.marks("hole", arch(x, y, 4, 8))
    for x in (100, 106, 112):
        d.marks("hole", arch(x - 1.5, 108, 3, 6))
    # cypresses and the wooded hill
    for x, h in [(62, 34), (96, 30), (108, 38), (190, 32)]:
        d.shape("cyp", cypress(x, 140, h, 4.5))
    d.band("near", bushes(146, 9, 14, jitter=(2, 0, 4, 1)))
    # Albaicín houses in front
    for x, y, w in [(-6, 164, 24), (24, 168, 20), (50, 162, 22), (118, 166, 22), (146, 160, 26), (178, 166, 24)]:
        d.shape("roof", f"M{x - 2} {y + 2} L{x + 4} {y - 4} H{x + w - 4} L{x + w + 2} {y + 2}Z")
        d.shape("light", rrect(x, y, w, 30, 0.5))
        d.marks("hole", rrect(x + w / 2 - 2, y + 6, 4, 5, 0.8))
    d.band("deep", hills(186, 3, 20), line=False)


# ================================================================ TREVI FOUNTAIN
def trevi(d: Drawing):
    d.shape("light", cloud(4, 26, 0.7), line=False)
    # palazzo front
    d.shape("stone", "M2 150 V46 H62 V30 H138 V46 H198 V150Z")
    d.shape("stone", rrect(0, 43, 200, 5, 1), shadow=False)
    d.shape("stone", rrect(60, 27, 80, 5, 1), shadow=False)
    for x in (68, 88, 112, 132):
        d.shape("stone", "M{0} 27 V20 Q{1} 16 {2} 20 V27Z".format(x - 2.4, x, x + 2.4))
        d.shape("stone", circle(x, 16, 2.3))
    for x in list(range(10, 52, 12)) + list(range(152, 194, 12)):
        for y in (56, 84):
            d.marks("hole", rrect(x, y, 6, 12, 0.8))
            d.stroke("stone2", f"M{x - 1.5} {y - 2} H{x + 7.5}", 1.4, line=False)
    ink(d, "stone2", "M2 76 H64 M136 76 H198 M64 36 H136", 1.3, 1.1)
    # central triumphal arch with columns
    for x in (66, 76, 124, 134):
        d.shape("stone", rrect(x - 3.5, 50, 7, 64, 1))
        d.shape("stone", rrect(x - 5, 48, 10, 3.5, 1), shadow=False)
    d.shape("hole", arch(85, 54, 30, 60), shadow=False)
    d.shape("stone2", arch(88, 57, 24, 57), shadow=False, line=False)
    for x in (41, 159):
        d.marks("hole", arch(x - 7, 82, 14, 26))
        d.shape("statue", f"M{x - 3.2} 106 L{x - 2} 92 Q{x} 89 {x + 2} 92 L{x + 3.2} 106Z", shadow=False)
        d.shape("statue", circle(x, 89, 2.2), shadow=False)
    # Oceanus on his shell
    d.shape("statue", "M93 104 L95 80 Q100 74 105 80 L107 104Z M94 82 L86 92 L89 94 L96 86Z", spot=True)
    d.shape("statue", circle(100, 73, 4))
    d.shape("statue", "M86 104 Q100 112 114 104 Q112 112 100 114 Q88 112 86 104Z")
    # rocks, sea-horses and cascades
    d.shape("rock", "M14 152 L22 136 L36 130 L48 120 L64 118 L76 110 L124 110 L136 118 L152 120 L164 130 L178 136 L186 152Z")
    ink(d, "stone2", "M30 140 L40 134 M56 128 L66 124 M134 124 L146 128 M160 134 L170 140", 1.6, 1.1)
    horse = ("M80 138 C78 128 74 122 68 117 L66 107 L64 102 L61 105 L53 107 L48 111 L50 114 L57 113 L60 118 "
             "C56 121 54 125 56 129 L46 124 L41 128 L43 131 L50 129 L58 133 L52 137 L47 143 L51 145 L59 138 Q68 142 80 138Z")
    tail = "M78 136 Q86 134 88 126 Q92 132 88 140 Q84 146 74 144Z"
    for tf in ("", "translate(200 0) scale(-1 1)"):
        group(d, tf or "translate(0 0)", lambda: (d.shape("statue", tail), d.shape("statue", horse)))
    d.shape("water", "M90 116 H110 L112 150 H88Z M60 130 L70 132 L66 150 H56Z M140 132 L130 130 L134 150 H144Z", shadow=False)
    ink(d, "light", "M94 120 V148 M100 118 V148 M106 120 V148 M62 136 V148 M138 136 V148", 1.2, 1)
    # basin
    d.band("water", waves(150, 2, 18))
    d.stroke("light", "M30 160 h12 M80 158 h16 M150 162 h14", 2, line=False)
    d.band("rim", "M-30 172 H230")
    d.stroke("stone2", "M-30 176 H230", 1.4, line=False)
    d.band("ground", "M-30 186 H230", line=False)


# ================================================================ ST PETER'S
def st_peters(d: Drawing):
    d.shape("light", cloud(10, 46, 0.9))
    d.shape("light", cloud(156, 36, 0.7))
    # minor domes
    for x in (52, 148):
        d.shape("dome", f"M{x - 9} 96 Q{x - 9} 84 {x} 82 Q{x + 9} 84 {x + 9} 96Z")
        d.shape("dome", rrect(x - 2, 76, 4, 7, 1))
    # drum and great dome
    d.shape("stone", rrect(66, 74, 68, 26, 0.5))
    for x in range(70, 132, 9):
        d.stroke("stone2", f"M{x} 76 V98 M{x + 2.6} 76 V98", 1.2, line=False)
    for x in range(74, 128, 9):
        d.marks("hole", rrect(x + .3, 82, 3.6, 8, 0.8))
    d.shape("dome", "M68 76 C68 50 84 36 100 34 C116 36 132 50 132 76Z", spot=True)
    ink(d, "dome2", "M100 35 V76 M86 39 C80 50 79 62 80 76 M114 39 C120 50 121 62 120 76 "
                    "M74 52 C72 60 72 68 72 76 M126 52 C128 60 128 68 128 76", 1.3, 1)
    d.shape("stone", rrect(66, 72, 68, 4, 1), shadow=False)
    # lantern and cross
    d.shape("stone", rrect(94, 22, 12, 14, 1))
    d.shape("dome", "M93 24 Q100 14 107 24Z")
    d.stroke("stone", "M100 17 V8 M97 11 H103", 1.6)
    d.marks("hole", rrect(97, 26, 2, 6, 0.6))
    d.marks("hole", rrect(101, 26, 2, 6, 0.6))
    # Maderno's facade with statues
    d.shape("stone", rrect(30, 98, 140, 44, 0.5))
    d.shape("stone", "M80 100 L100 90 L120 100Z")
    d.shape("stone", " ".join(f"M{x - 1.6} 98 V93 Q{x} 90 {x + 1.6} 93 V98Z M{x} 89.8 a1.5 1.5 0 1 0 .01 0Z" for x in range(36, 168, 10)), shadow=False)
    for x in range(34, 168, 11):
        d.stroke("stone2", f"M{x} 106 V140", 2, line=False)
    ink(d, "stone2", "M30 104 H170 M30 118 H170", 1.3, 1.1)
    for x in range(38, 164, 22):
        d.marks("hole", arch(x, 108, 5, 9))
    for x in (78, 92, 106, 120):
        d.marks("hole", arch(x - .5, 124, 7, 18))
    # Bernini's colonnades curving in front
    for side in (-1, 1):
        x0, x1 = (-30, 68) if side < 0 else (132, 230)
        top = f"M{x0} 140 Q{(x0 + x1) / 2} {136 + side * -0} {x1} 146"
        d.shape("stone", f"{top} V160 H{x0}Z")
        cols = " ".join(f"M{x} 148 V160" for x in range(x0 + 6, x1, 7))
        d.stroke("stone2", cols, 2, line=False)
        d.shape("stone", " ".join(f"M{x - 1.3} {141 + (x - x0) / (x1 - x0) * 5:.1f} v-4 q1.3 -2.5 2.6 0 v4Z" for x in range(x0 + 4, x1 - 2, 9)), shadow=False)
    # obelisk
    d.shape("stone", "M97 164 L98.5 116 L100 110 L101.5 116 L103 164Z")
    d.shape("stone", rrect(93, 160, 14, 8, 1))
    d.stroke("stone", "M100 110 V104", 1.2)
    d.band("ground", "M-30 166 Q100 160 230 166")
    d.stroke("stone2", "M10 176 L60 172 M140 172 L190 176", 1.4, line=False)


# ================================================================ FLORENCE DUOMO
def florence(d: Drawing):
    d.disc("glow", 166, 64, 11)
    d.shape("light", cloud(150, 92, 0.7))
    d.band("far", hills(130, 10, 30))
    for x, h in [(10, 22), (18, 16), (186, 20)]:
        d.shape("cyp", cypress(x, 130, h, 3.5))
    # nave and transept
    d.shape("marble", rrect(56, 104, 140, 46, 0.5))
    d.shape("dome", "M160 108 Q170 96 182 108Z")
    ink(d, "green", " ".join(f"M{x} 106 V148" for x in range(62, 196, 10)) + " M56 116 H196 M56 128 H196", 1.6, 1)
    for x in range(64, 196, 20):
        d.marks("hole", rrect(x, 132, 4, 10, 1))
    # Brunelleschi's dome
    d.shape("marble", rrect(84, 98, 62, 18, 0.5))
    for x in (94, 107, 123, 136):
        d.shape("hole", circle(x, 106, 2.8), shadow=False)
    ink(d, "green", "M84 101 H146", 1.4, 1)
    d.shape("dome", "M86 100 C86 72 100 54 111 47 H119 C130 54 144 72 144 100Z", spot=True)
    ink(d, "rib", "M115 47 V100 M112 48 C102 58 97 76 98 100 M118 48 C128 58 133 76 132 100 M86 100 H144", 2.4, 1.2)
    d.shape("rib", rrect(109, 33, 12, 15, 1))
    d.shape("rib", poly((108, 34), (115, 22), (122, 34)))
    d.shape("gold", circle(115, 20, 2.2), shadow=False)
    d.stroke("gold", "M115 18 V12", 1.3)
    d.marks("hole", rrect(112, 37, 2, 7, 0.6))
    d.marks("hole", rrect(116, 37, 2, 7, 0.6))
    # Giotto's campanile
    d.shape("marble", rrect(36, 46, 22, 112, 0.5))
    d.shape("marble", rrect(33.5, 42, 27, 5, 1))
    ink(d, "green", "M36 64 H58 M36 92 H58 M36 116 H58 M36 136 H58 M39 46 V158 M55 46 V158", 1.6, 1)
    if d.paper:
        for y in (120, 140):
            d.marks("pink", rrect(41, y, 12, 8, 0.5))
    d.marks("hole", garch(42.5, 50, 9, 12))
    d.marks("hole", garch(40, 68, 6, 20))
    d.marks("hole", garch(48, 68, 6, 20))
    d.marks("hole", garch(41, 96, 5, 14))
    d.marks("hole", garch(48, 96, 5, 14))
    # terracotta roofs of the city
    d.band("near", "M-30 152 H0 L8 146 H34 L40 152 H64 L70 144 H96 L104 152 H130 L136 146 H164 L170 152 H230")
    d.stroke("deep", "M-30 158 H230", 1.2, line=False)
    for x in (4, 24, 54, 84, 114, 144, 176):
        d.marks("light", rrect(x, 162, 4, 6, 0.8))
    d.band("deep", hills(178, 3, 20), line=False)


# ================================================================ CINQUE TERRE
HOUSE_ROLES = ["h1", "h2", "h3", "h4", "h5", "h6"]


def house(d: Drawing, x, y, w, h, role, floors=None):
    d.shape(role, rrect(x, y, w, h, 0.5), spot=role in ("h1", "h3"))
    d.shape("tile", rrect(x - 1, y - 2, w + 2, 3, 0.8), shadow=False)
    floors = floors or max(1, int(h / 9))
    n = max(1, int(w / 7))
    for f in range(floors):
        for k in range(n):
            wx = x + (k + .5) * w / n - 1.6
            d.marks("shutter", rrect(wx, y + 4 + f * 9, 3.2, 4.6, 0.6))


def cinque_terre(d: Drawing):
    d.disc("glow", 160, 40, 11)
    # terraced vineyard hill behind
    d.shape("mid", "M-30 200 V96 Q24 60 92 54 Q150 52 230 86 V200Z")
    ink(d, "near", "M-10 92 Q40 66 92 62 M-14 106 Q40 80 100 74 Q150 72 210 92 M150 64 Q190 70 224 88 "
                   "M-20 120 Q40 96 110 90", 1.6, 1.1)
    # sea
    d.band("sea", "M-30 142 H230")
    d.stroke("light", "M150 154 h18 M176 166 h12 M10 160 h12", 2, line=False)
    # the rock the village sits on
    d.shape("rock", "M14 210 V150 Q18 138 30 136 L64 132 L150 136 Q168 138 174 152 L180 210Z")
    ink(d, "rock2", "M30 150 L36 164 M60 146 L56 160 M140 148 L146 166 M160 152 L164 164", 1.6, 1.1)
    # houses: back rows first
    rows = [
        [(62, 56, 14, 30), (76, 50, 14, 36), (90, 54, 16, 32), (106, 58, 14, 28)],
        [(42, 80, 16, 32), (58, 74, 15, 38), (73, 78, 15, 34), (88, 72, 17, 40), (105, 76, 15, 36), (120, 82, 16, 30)],
        [(26, 104, 18, 34), (44, 98, 16, 40), (60, 102, 18, 36), (78, 96, 16, 42), (94, 100, 18, 38), (112, 104, 16, 34),
         (128, 100, 18, 38), (146, 108, 16, 30)],
    ]
    i = 0
    for row in rows:
        for x, y, w, h in row:
            house(d, x, y, w, h, HOUSE_ROLES[i % 6])
            i += 1
    # church bell tower at the top
    d.shape("h5", rrect(118, 38, 10, 30, 0.5))
    d.shape("tile", poly((117, 40), (123, 30), (129, 40)))
    d.marks("hole", arch(120.5, 43, 5, 7))
    # little boats on the slipway and at sea
    d.shape("boat", "M150 146 Q152 152 160 152 H174 Q178 150 180 146Z")
    d.shape("pop", "M30 178 Q32 184 40 184 H52 Q56 182 58 178Z")
    d.band("deep", waves(190, 2.5, 30), line=False)


# ================================================================ DUBROVNIK
def dubrovnik(d: Drawing):
    d.disc("glow", 160, 36, 10)
    d.band("far", "M-30 78 Q30 56 100 52 Q170 50 230 70")
    # Minčeta tower and the landward wall
    d.shape("wall", "M20 120 V74 H110 V120Z")
    d.shape("wall", battlement(20, 70, 90, 8, 10, 3), shadow=False)
    d.shape("wall", "M26 84 L28 54 Q42 50 56 54 L58 84Z")
    d.shape("wall", battlement(25, 44, 34, 11, 5, 3))
    d.stroke("wall2", "M26 56 Q42 60 58 56", 1.6, line=False)
    ink(d, "wall2", "M48 58 V84", 1.2, 0.9)
    d.marks("hole", rrect(40, 64, 4, 6, 1))
    # roofs rising up the hill, in rows
    rows = [(78, 30, 120), (92, 14, 190), (106, -10, 200)]
    for y, x0, x1 in rows:
        x = x0
        k = 0
        while x < x1:
            w = 16 + (k * 7) % 9
            d.shape("house", rrect(x, y, w, 18, 0.5))
            d.shape("roof" if k % 3 else "roof2", f"M{x - 1} {y + 1} L{x + w / 2} {y - 7} L{x + w + 1} {y + 1}Z")
            d.marks("hole", rrect(x + w / 2 - 1.5, y + 6, 3, 4, 0.6))
            x += w + 1
            k += 1
    # bell tower and the cathedral dome
    d.shape("house", rrect(122, 58, 10, 44, 0.5))
    d.shape("roof2", "M120 60 Q127 50 134 60Z")
    d.marks("hole", arch(124.5, 64, 5, 8))
    d.shape("house", rrect(150, 86, 24, 14, 0.5))
    d.shape("dome", "M152 88 Q162 72 172 88Z")
    d.stroke("dome", "M162 76 V70", 1.4)
    # sea walls with the round St John fortress
    d.shape("wall", battlement(-30, 118, 260, 34, 28, 4), spot=True)
    d.shape("wall", "M150 152 V112 Q172 104 194 112 V152Z")
    d.shape("wall", battlement(148, 104, 48, 10, 6, 3), shadow=False)
    d.shape("wall", "M2 152 V114 H34 V152Z")
    d.shape("wall", battlement(0, 108, 36, 8, 5, 3), shadow=False)
    ink(d, "wall2", "M-30 132 H230 M10 124 V150 M162 120 V150 M180 120 V150", 1.4, 1)
    for x in (14, 24, 60, 90, 120, 166, 178):
        d.marks("hole", rrect(x, 136, 3, 5, 0.6))
    d.shape("rock", "M-30 210 V150 Q30 148 60 154 Q110 150 150 154 Q190 150 230 152 V210Z")
    d.band("sea", waves(162, 2.5, 22))
    d.shape("light", "M86 158 L94 140 V158Z M96 158 L96 142 L104 158Z", shadow=False)
    d.shape("pop", "M82 160 H108 L104 165 H86Z")
    d.stroke("light", "M30 172 h14 M140 176 h18", 2, line=False)
    d.band("deep", waves(184, 2.5, 30), line=False)


# ================================================================ METEORA
def meteora(d: Drawing):
    d.disc("glow", 160, 44, 12)
    d.shape("light", cloud(14, 40, 0.8))
    birds(d, [(118, 34, .9), (132, 28, .7)])
    d.band("far", hills(132, 12, 20))
    # side pillars
    d.shape("rock2", "M-30 200 V96 Q-20 62 8 58 Q30 58 40 80 Q48 120 46 200Z")
    d.shape("rock2", "M152 200 Q148 130 154 100 Q160 82 180 82 Q200 84 206 104 Q212 140 214 200Z")
    # small monastery on the right pillar (Roussanou-like)
    d.shape("wall", rrect(160, 72, 24, 12, 0.5))
    d.shape("roof", "M158 74 L164 66 H180 L186 74Z")
    d.marks("hole", rrect(166, 76, 3, 4, 0.6))
    d.marks("hole", rrect(175, 76, 3, 4, 0.6))
    # the great pillar
    d.shape("rock", "M58 200 Q60 150 62 116 Q62 88 72 78 Q84 70 100 70 Q118 70 128 80 Q138 92 138 120 Q138 160 142 200Z")
    ink(d, "rock3", "M72 92 Q68 130 70 186 M86 80 Q82 120 84 176 M100 84 Q98 120 100 160 M114 80 Q118 120 116 180 "
                    "M128 92 Q130 130 128 186", 1.8, 1.1)
    ink(d, "rock3", "M8 70 Q4 110 6 160 M24 64 Q30 100 28 150 M168 96 Q164 130 166 170 M188 92 Q192 130 190 170", 1.4, 1)
    # monastery on top (Varlaam-like)
    d.shape("wall", rrect(66, 54, 30, 20, 0.5))
    d.shape("wall", rrect(94, 46, 36, 28, 0.5))
    d.shape("wall", rrect(126, 58, 14, 16, 0.5))
    d.shape("roof", "M64 56 L70 48 H92 L98 56Z", spot=True)
    d.shape("roof", "M92 48 L100 38 H124 L132 48Z", spot=True)
    d.shape("roof", "M124 60 L128 54 H138 L142 60Z", spot=True)
    d.shape("dome", "M104 40 Q112 26 120 40Z")
    d.stroke("dome", "M112 30 V24 M109.5 26.5 H114.5", 1.4)
    for x, y in [(72, 60), (82, 60), (100, 54), (110, 54), (120, 54), (100, 64), (120, 64), (130, 64)]:
        d.marks("hole", rrect(x, y, 3.4, 5, 0.6))
    d.marks("hole", arch(108, 62, 6, 12))
    # wooded plain
    d.band("mid", bushes(176, 9, 14))
    for x, s in [(24, .7), (166, .8), (186, .6)]:
        d.shape("deep", cypress(x, 182, 30 * s, 4))
    d.band("near", hills(188, 3, 20), line=False)


# ================================================================ MYKONOS WINDMILLS
def windmill(d: Drawing, spokes=8, sails=(0, 2, 4, 6)):
    """Cycladic windmill, base centre at (0, 0), about 120 tall incl. sails."""
    d.shape("whitewash", "M-17 0 L-14 -62 H14 L17 0Z", spot=True)
    d.shape("thatch", "M-16 -60 Q-12 -76 0 -80 Q12 -76 16 -60Z")
    d.shape("door", arch(-5.5, -20, 11, 20), shadow=False)
    d.marks("hole", rrect(-3, -46, 6, 8, 1))
    d.stroke("whitewash2", "M-15 -30 H15", 1.2, line=False)
    hx, hy, R = 0, -70, 38
    tips = [(hx + R * math.cos(a), hy + R * math.sin(a)) for a in [-math.pi / 2 + k * 2 * math.pi / spokes + .2 for k in range(spokes)]]
    for k in sails:
        tx, ty = tips[k]
        nx, ny = tips[(k + 1) % spokes]
        mx, my = hx + (nx - hx) * .55, hy + (ny - hy) * .55
        d.shape("sail", poly((hx + (tx - hx) * .18, hy + (ty - hy) * .18), (tx, ty), (mx, my)), shadow=False)
    d.stroke("wood", " ".join(f"M{hx} {hy} L{x:.1f} {y:.1f}" for x, y in tips), 2.2, shadow=True)
    ink(d, "wood", poly(*tips), 0.8, 0.8)
    d.shape("wood", circle(hx, hy, 3.2))


def mykonos(d: Drawing):
    d.disc("glow", 44, 58, 13)
    d.shape("light", cloud(140, 30, 0.8))
    d.band("sea", "M-30 112 H230")
    d.shape("far", "M150 113 Q170 102 200 104 Q218 106 230 112Z", shadow=False)
    d.stroke("light", "M20 124 h16 M70 132 h12", 2, line=False)
    d.band("hill", "M-30 140 Q30 124 90 128 Q150 134 230 150")
    group(d, "translate(28 128) scale(.48)", lambda: windmill(d, sails=(1, 4, 6)))
    group(d, "translate(72 132) scale(.64)", lambda: windmill(d, sails=(0, 3, 5)))
    group(d, "translate(138 158) scale(1.04)", lambda: windmill(d))
    d.band("hill2", hills(176, 4, 30))
    for x, y in [(10, 172), (186, 176)]:
        d.shape("whitewash", rrect(x, y, 20, 16, 1))
        d.marks("door", rrect(x + 7, y + 5, 5, 7, 1))
    d.band("deep", hills(190, 3, 20), line=False)


# ================================================================ KINDERDIJK
def mill_nl(d: Drawing, sails=True, spot=False):
    """Dutch thatched ground-sailer, base centre (0, 0)."""
    d.shape("thatch", "M-15 0 L-8 -58 H8 L15 0Z", spot=spot)
    d.shape("thatch", "M-10 -56 Q-10 -68 0 -70 Q10 -68 10 -56Z")
    d.shape("wood", rrect(-4, -14, 8, 14, 1), shadow=False)
    d.marks("glow2", rrect(-2, -40, 4, 5, 0.6))
    if not sails:
        return
    hx, hy = -3, -62
    for a in (35, 125, 215, 305):
        def blade(a=a):
            d.stroke("frame", "M0 0 V-54", 2.2, shadow=True)
            d.shape("sail", rrect(1, -52, 9, 44, 0.5), shadow=False)
            ink(d, "frame", "M1 -52 H10 V-8 H1 M5.5 -52 V-8 " + " ".join(f"M1 {y} H10" for y in range(-46, -8, 6)), 0.9, 0.8)
        group(d, f"translate({hx} {hy}) rotate({a})", blade)
    d.shape("frame", circle(hx, hy, 2.6), shadow=False)


def kinderdijk(d: Drawing):
    d.disc("glow", 64, 70, 16)
    d.shape("light", cloud(140, 40, 0.8))
    birds(d, [(150, 70, .8), (162, 64, .6)])
    d.band("far", "M-30 124 Q100 118 230 124")
    group(d, "translate(40 124) scale(.42)", lambda: mill_nl(d))
    group(d, "translate(72 126) scale(.56)", lambda: mill_nl(d))
    d.band("mid", "M-30 130 Q20 126 60 130 Q120 134 230 128")
    d.band("water", "M-30 140 H230")
    # reflections of the near mill
    d.raw(f'<path d="M116 142 L110 176 H134 L128 142Z" fill="{d.c["thatch"]}" opacity=".35"/>' if d.paper else "", "")
    d.stroke("light", "M20 152 h18 M60 166 h14 M150 160 h16", 2, line=False)
    group(d, "translate(122 140) scale(1.02)", lambda: mill_nl(d, spot=True))
    d.band("near", "M-30 166 Q40 160 100 170 Q160 178 230 168")
    reeds = " ".join(f"M{x} 176 Q{x + 1} 166 {x + (2 if x % 2 else -2)} 158" for x in range(-8, 210, 7))
    d.stroke("deep", reeds, 1.8)
    d.band("deep", hills(186, 3, 20), line=False)


# ================================================================ GIANT'S CAUSEWAY
def causeway(d: Drawing):
    d.disc("glow", 128, 40, 12)
    d.shape("light", cloud(150, 30, 0.8))
    d.band("sea", "M-30 100 H230")
    # headland
    d.shape("cliff", "M110 100 Q120 72 150 66 H230 V100Z")
    d.shape("grass", "M110 100 Q120 72 150 66 H230 V72 H152 Q126 78 116 100Z", shadow=False)
    ink(d, "cliff2", "M136 76 V100 M150 72 V100 M166 70 V100 M184 70 V100 M200 70 V100", 1.2, 0.9)
    d.stroke("light", "M130 112 h16 M160 120 h12", 2, line=False)
    # hexagonal basalt columns, back to front
    w, hh = 21.0, 8.4
    cols = []
    for r in range(6):
        for c in range(-1, 12):
            x = -4 + c * w * .75
            y = 108 + r * hh + (c % 2) * hh / 2
            jit = ((c * 7 + r * 13) % 5 - 2) * 3
            e = 64 - max(0, x - 40) * .5 - abs(min(0, x - 40)) * .3 - r * 6 + jit
            e = 6 * round(e / 6)
            if e > 2 and 4 < x < 184:
                cols.append((y, x, y - e))
    cols.sort()
    for _, x, ty in cols:
        L = 120
        body = poly((x - w / 2, ty), (x - w / 2, ty + L), (x + w / 2, ty + L), (x + w / 2, ty))
        d.shape("basalt", body, shadow=False)
        if d.paper:
            d.marks("basalt2", poly((x - w / 4, ty + hh / 2), (x - w / 4, ty + L), (x + w / 4, ty + L), (x + w / 4, ty + hh / 2)))
        top = poly((x - w / 2, ty), (x - w / 4, ty - hh / 2), (x + w / 4, ty - hh / 2), (x + w / 2, ty), (x + w / 4, ty + hh / 2), (x - w / 4, ty + hh / 2))
        d.shape("top", top, shadow=False, spot=(int(x) + int(ty)) % 3 == 0)
        if d.paper:
            d.stroke("basalt2", top, 0.8)
    # surf around the stones
    d.band("sea", waves(166, 3, 20))
    d.shape("light", cloud(4, 166, 0.9), shadow=False)
    d.shape("light", cloud(160, 170, 0.8), shadow=False)
    d.band("deep", waves(182, 2.5, 26), line=False)


# ================================================================ CLIFFS OF MOHER
def moher(d: Drawing):
    d.disc("glow", 40, 46, 12)
    d.shape("light", cloud(110, 30, 0.8))
    birds(d, [(60, 74, .9), (74, 66, .7)])
    d.band("sea", "M-30 110 H230")
    # distant headlands
    d.shape("cliff3", "M-30 118 V100 Q-10 96 10 98 L30 104 V118Z")
    d.shape("grass", "M-30 100 Q-10 96 10 98 L30 104 L26 106 L8 101 Q-10 99 -30 103Z", shadow=False)
    d.shape("cliff2", "M10 130 L16 92 Q40 86 70 88 L84 92 L80 130Z")
    d.shape("grass", "M16 92 Q40 86 70 88 L84 92 L83 96 L70 93 Q40 91 16 97Z", shadow=False)
    ink(d, "cliff3", "M18 104 H80 M17 114 H80", 1.2, 0.9)
    # sea stack
    d.shape("cliff", "M88 170 L90 124 Q96 118 104 122 L106 170Z")
    d.shape("grass", "M90 124 Q96 118 104 122 L104 125 Q96 121 90 127Z", shadow=False)
    # the near cliff
    d.shape("cliff", "M112 210 L116 140 L114 100 L120 66 Q160 56 230 54 V210Z", spot=True)
    d.shape("grass", "M120 66 Q160 56 230 54 V62 Q160 64 121 73Z", shadow=False)
    ink(d, "cliff2", "M117 84 Q150 80 170 82 Q200 84 230 78 M115 100 Q140 96 160 99 Q196 102 230 96 "
                     "M116 118 Q150 112 180 116 Q206 118 230 112 M116 138 Q146 134 170 136 Q200 138 230 132", 1.6, 1)
    # O'Brien's Tower
    d.shape("tower", rrect(150, 44, 10, 16, 0.5))
    d.shape("tower", battlement(148.5, 40, 13, 5, 3, 2), shadow=False)
    d.marks("hole", rrect(153.5, 48, 3, 5, 0.6))
    # surf
    d.band("sea", waves(168, 2.5, 22))
    d.stroke("light", "M88 168 Q96 160 106 168 M110 172 Q130 164 160 170 M20 150 h16 M40 140 h12", 2.2, line=False)
    d.band("deep", waves(184, 2.5, 30), line=False)


# ================================================================ HALLSTATT
def hallstatt(d: Drawing):
    d.shape("light", cloud(120, 30, 0.8))
    # steep mountains each side
    d.shape("mtn2", "M-30 140 V20 L10 30 L40 60 L70 108 L90 140Z")
    d.shape("mtn", "M70 140 L110 64 L132 40 L160 22 L190 14 L230 20 V140Z")
    d.shape("light", "M132 40 L160 22 L190 14 L196 22 L176 26 L166 34 L150 34 L140 46Z", shadow=False)
    for x, y, s in [(26, 112, .8), (44, 120, .9), (12, 100, .7), (150, 106, .8), (170, 98, .9), (190, 108, .8), (130, 112, .7),
                    (206, 100, .8), (112, 114, .6)]:
        d.shape("forest", pine(x, y, s), line=False)
    # village along the shore
    houses = [(4, 112, 18, "hw1"), (22, 108, 16, "hw2"), (38, 114, 16, "hw3"), (96, 112, 18, "hw2"), (114, 106, 18, "hw1"),
              (132, 112, 16, "hw3"), (148, 108, 18, "hw1"), (166, 114, 18, "hw2"), (184, 110, 18, "hw3")]
    for x, y, w, role in houses:
        d.shape(role, rrect(x, y, w, 140 - y, 0.5))
        d.shape("roof", f"M{x - 2} {y + 2} L{x + w / 2} {y - 8} L{x + w + 2} {y + 2}Z")
        for k in range(2):
            d.marks("hole", rrect(x + 3 + k * (w - 9), y + 8, 3, 4, 0.6))
            d.marks("hole", rrect(x + 3 + k * (w - 9), y + 16, 3, 4, 0.6))
    # the Protestant church: white tower, slender dark spire
    d.shape("church", rrect(56, 98, 30, 42, 0.5))
    d.shape("roof", "M54 100 L62 90 H80 L88 100Z")
    d.shape("church", rrect(60, 66, 14, 74, 0.5), spot=True)
    d.shape("spire", poly((59, 68), (67, 22), (75, 68)))
    d.stroke("spire", "M67 22 V14", 1.4)
    d.marks("hole", arch(64.5, 74, 5, 9))
    d.marks("clock", circle(67, 90, 3.2))
    for x in (78, 82):
        d.marks("hole", arch(x - 1.5, 108, 3, 8))
    d.band("lake", "M-30 140 H230")
    # reflections
    if d.paper:
        d.raw(f'<path d="M60 142 H74 V170 L67 186 L60 170Z" fill="{d.c["church"]}" opacity=".35"/>')
    d.stroke("light", "M14 152 h20 M100 158 h18 M150 150 h22 M40 170 h14 M130 176 h16", 2, line=False)
    d.band("deep", waves(184, 2.5, 30), line=False)


# ================================================================ LAKE BLED
def bled(d: Drawing):
    d.disc("glow", 46, 44, 11)
    # Julian Alps
    d.band("far", "M-30 96 L10 70 L34 82 L64 52 L94 76 L118 60 L150 84 L230 80")
    for snow in ["M64 52 L74 63 L68 62 L64 67 L58 61 L54 63Z", "M118 60 L127 70 L122 69 L118 73 L113 68Z", "M10 70 L18 78 L13 77 L9 81 L4 76Z"]:
        d.shape("light", snow, shadow=False)
    d.band("mid", bushes(112, 10, 18))
    # castle on its cliff
    def castle():
        d.shape("rock", "M140 210 V126 L146 90 L150 76 L160 70 H230 V210Z")
        ink(d, "rock2", "M150 90 L154 120 M160 80 L158 104 M146 112 L150 130", 1.6, 1)
        d.shape("castle", rrect(156, 54, 50, 18, 0.5))
        d.shape("croof", "M154 56 L160 48 H202 L208 56Z")
        d.shape("castle", rrect(162, 36, 12, 22, 0.5))
        d.shape("croof", poly((160, 38), (168, 26), (176, 38)))
        for x in (178, 186, 194):
            d.marks("hole", rrect(x, 60, 3, 5, 0.6))
    group(d, "translate(-10 4)", castle)
    d.band("lake", "M-30 132 H230")
    # the island with its pilgrimage church
    d.shape("trees", "M36 140 Q38 118 58 114 Q66 104 80 108 L120 108 Q134 106 140 118 Q148 126 146 140Z")
    d.shape("church", rrect(74, 98, 34, 20, 0.5))
    d.shape("croof", "M72 100 L80 90 H104 L110 100Z")
    d.shape("church", rrect(104, 66, 12, 52, 0.5), spot=True)
    d.shape("spire", poly((103, 68), (110, 32), (117, 68)))
    d.stroke("spire", "M110 32 V26", 1.4)
    d.marks("hole", arch(107.5, 72, 5, 9))
    d.marks("hole", arch(80, 104, 4, 8))
    d.marks("hole", arch(90, 104, 4, 8))
    d.shape("church", "M84 140 L88 118 H96 L100 140Z", shadow=False)
    ink(d, "stone2", "M86 128 H98 M85 134 H99 M87 122 H97", 1, 0.8)
    for x, y, h in [(46, 134, 20), (128, 132, 22), (138, 136, 16)]:
        d.shape("deep", cypress(x, y, h, 4.5))
    # pletna boat with its striped awning
    d.shape("boat", "M44 166 Q48 172 60 172 H96 Q104 170 106 164Z")
    d.shape("awning", "M56 164 V154 Q76 148 96 154 V164Z", shadow=False, spot=True)
    d.stroke("light", "M62 152 V164 M70 150 V164 M78 150 V164 M86 151 V164", 2.2, line=False)
    d.stroke("light", "M14 150 h16 M150 152 h18 M120 178 h14", 2, line=False)
    d.band("deep", waves(184, 2.5, 30), line=False)


# ================================================================ KIRKJUFELL
KIRK = ("M-30 150 L22 142 Q44 120 62 92 Q76 66 88 46 L94 38 L98 42 L104 56 Q112 70 122 80 L134 88 Q146 96 156 108 "
        "L172 118 Q196 128 230 134 V150Z")


def kirkjufell(d: Drawing):
    if dark_sky(d):
        d.raw(f'<g opacity=".7"><path d="M-10 70 C30 40 60 70 100 34 C130 8 170 30 214 4 L216 24 C176 46 140 30 106 54 '
              f'C70 84 30 60 -6 92Z" fill="{d.c["aurora"]}"/>'
              f'<path d="M40 90 C70 66 110 80 150 56 C170 44 190 46 212 36 L212 46 C190 56 170 56 150 68 C110 92 70 80 42 100Z" '
              f'fill="{d.c["aurora2"]}"/></g>')
        for x, y in [(30, 40), (150, 70), (176, 52), (60, 30), (126, 24)]:
            d.marks("light", circle(x, y, 1.1))
    else:
        d.disc("glow", 160, 50, 12)
        d.shape("light", cloud(16, 44, 0.8))
    d.shape("mtn", KIRK, spot=True)
    d.shape("mtn2", "M98 42 L104 56 Q112 70 122 80 L134 88 Q146 96 156 108 L172 118 Q196 128 230 134 V150 H120 Q112 110 100 70Z",
            shadow=False, line=False)
    ink(d, "light", "M70 82 Q90 78 104 66 M58 100 Q86 96 116 82 M44 118 Q80 114 128 96 Q146 104 150 108 "
                    "M34 132 Q90 128 140 114 L166 122", 2.4, 1.2)
    d.shape("light", "M88 46 L94 38 L98 42 L101 50 L96 48 L92 54Z", shadow=False)
    # grassy bank and the waterfall
    d.band("grass", "M-30 150 Q30 140 70 146 Q120 152 230 146")
    d.shape("rockf", "M-30 210 V164 Q0 158 30 160 L46 150 H96 L104 160 Q150 156 230 166 V210Z")
    d.shape("fall", "M48 151 H66 L70 172 H44Z M76 151 H92 L96 172 H72Z", shadow=False, spot=True)
    ink(d, "light", "M52 154 V170 M58 154 V170 M80 154 V170 M86 154 V170", 1.2, 1)
    d.band("fall", waves(174, 2, 16))
    d.stroke("light", "M40 180 h14 M90 182 h18", 2, line=False)
    d.band("rockf", hills(190, 3, 20), line=False)


# ================================================================ BELÉM TOWER
def sentry(d: Drawing, x, y, s=1.0):
    """Manueline sentry box with ribbed dome, base centre (x, y)."""
    d.shape("stone", rrect(x - 4 * s, y - 10 * s, 8 * s, 10 * s, 1))
    d.shape("stone", f"M{x - 5 * s} {y - 9 * s} Q{x - 5 * s} {y - 17 * s} {x} {y - 19 * s} Q{x + 5 * s} {y - 17 * s} {x + 5 * s} {y - 9 * s}Z")
    ink(d, "stone2", f"M{x} {y - 19 * s} V{y - 9 * s} M{x - 2.6 * s} {y - 17 * s} Q{x - 3 * s} {y - 13 * s} {x - 3 * s} {y - 9 * s} "
                     f"M{x + 2.6 * s} {y - 17 * s} Q{x + 3 * s} {y - 13 * s} {x + 3 * s} {y - 9 * s}", 0.9, 0.8)
    d.stroke("stone", f"M{x} {y - 19 * s} V{y - 22 * s}", 1.2)


def shields(x0, x1, y, n, h=6.0) -> str:
    """Row of shield-shaped merlons along a parapet top."""
    w = (x1 - x0) / n
    return " ".join(f"M{x0 + i * w + w * .18:.1f} {y} V{y - h * .6:.1f} H{x0 + (i + 1) * w - w * .18:.1f} V{y - h * .6:.1f} "
                    f"Q{x0 + (i + 1) * w - w * .18:.1f} {y - h * .1:.1f} {x0 + (i + .5) * w:.1f} {y + 1:.1f} "
                    f"Q{x0 + i * w + w * .18:.1f} {y - h * .1:.1f} {x0 + i * w + w * .18:.1f} {y - h * .6:.1f}Z"
                    for i in range(n))


def belem(d: Drawing):
    d.disc("glow", 160, 48, 12)
    d.shape("light", cloud(10, 50, 0.8))
    birds(d, [(140, 82, .8), (152, 76, .6)])
    d.band("water", "M-30 146 H230")
    # bastion
    d.shape("stone", "M34 152 V118 H166 V152Z", spot=True)
    d.shape("stone", shields(34, 166, 112, 13, 8) + " M34 118 H166 V114 H34Z", shadow=False)
    for x in range(42, 166, 12):
        d.marks("hole", rrect(x, 128, 3.4, 7, 1.2))
    ink(d, "stone2", "M34 124 H166 M34 140 H166", 1.2, 1)
    sentry(d, 34, 118, 1.1)
    sentry(d, 166, 118, 1.1)
    # tower
    d.shape("stone", rrect(76, 40, 48, 78, 0.5))
    d.shape("stone", shields(76, 124, 36, 5, 7) + " M76 40 H124 V37 H76Z", shadow=False)
    sentry(d, 78, 40, 0.9)
    sentry(d, 122, 40, 0.9)
    d.shape("stone", rrect(96, 26, 16, 12, 0.5))
    d.shape("stone", shields(96, 112, 24, 2, 5), shadow=False)
    # loggia, balconies and windows
    d.shape("stone", rrect(78, 62, 44, 4, 1), shadow=False)
    for x in (82, 94, 106):
        d.marks("hole", arch(x, 66, 9, 14))
    d.shape("stone", rrect(78, 80, 44, 4, 1), shadow=False)
    ink(d, "stone2", "M78 82 H122", 1, 0.8)
    for x in (86, 106):
        d.marks("hole", arch(x, 90, 8, 14))
    d.marks("hole", arch(97, 46, 6, 10))
    ink(d, "stone2", "M76 88 H124 M76 108 H124", 1.2, 1)
    d.marks("pop", "M97 98 h6 v6 q-3 3 -6 0Z")
    d.stroke("light", "M14 160 h16 M150 164 h20 M80 170 h18", 2, line=False)
    d.band("water", waves(176, 2.5, 22))
    d.band("deep", waves(188, 2.5, 30), line=False)


# ================================================================ concepts
NOTRE = {"stone": "#CDBB96", "stone2": "#A6936F", "hole": "#4A4038", "rose": "#3C4C7C", "lead": "#5B6475"}
BRAND = {"stone": "#D2BF98", "stone2": "#A8956F", "shade": "#7E6E55", "bronze": "#4E9C84", "bronze2": "#33705E"}
COLOGNE = {"stone": "#5F5B57", "stone2": "#85807A", "hole": "#2A2827", "steel": "#5C7470"}
PRAGUE = {"vitus": "#4D4F5C", "copper": "#6FB09A", "castle": "#F0E8D6", "roofc": "#A65A42", "hole": "#4A3F3A",
          "bstone": "#8C7B66", "bstone2": "#6C5D4C", "btower": "#7E6E5C", "slate": "#3B3D48", "water": "#3F86B5"}
BUDA = {"stone": "#DCCCAE", "stone2": "#B8A88A", "roof": "#A8452F", "hole": "#6B5A48", "water": "#3E7FAE"}
ALHAM = {"wall": "#C46E48", "wall2": "#9C5034", "roof": "#E3A06A", "hole": "#5A2E22", "cyp": "#2F5A3A"}
TREVI = {"stone": "#EFE6D2", "stone2": "#CDBFA3", "hole": "#7A6C5A", "statue": "#FBF8F1", "rock": "#D8CCB2",
         "water": "#48BFC8", "rim": "#E2D6BE"}
PETER = {"stone": "#ECDDC0", "stone2": "#C4B190", "hole": "#5E5244", "dome": "#A7B5C2", "dome2": "#7D8C9C"}
DUOMO = {"marble": "#F4EEE2", "green": "#3F7A5E", "pink": "#E2A79E", "hole": "#4E4A44", "dome": "#C9623A",
         "rib": "#F7F3EA", "gold": "#E2B04A", "cyp": "#2F5A3A"}
CINQUE = {"h1": "#F2C14E", "h2": "#EE8B6E", "h3": "#D9534F", "h4": "#F4A261", "h5": "#F7DCC4", "h6": "#E79AA6",
          "shutter": "#2F6B4F", "tile": "#7A6A62", "rock": "#6E5E52", "rock2": "#53463D", "sea": "#2F86B8",
          "boat": "#2F5FA8", "hole": "#3A3A44"}
DUBRO = {"wall": "#D6C29C", "wall2": "#B09A74", "house": "#F2E8D6", "roof": "#D7693E", "roof2": "#BC5432",
         "dome": "#8C8C84", "hole": "#4A3F36", "rock": "#9C8F7C", "sea": "#2C82B4"}

METEORA = {"rock": "#A08A72", "rock2": "#CBBBA6", "rock3": "#7E6A56", "wall": "#D2C2A6", "roof": "#B5503A", "dome": "#8A7A6A", "hole": "#4A3E34"}
MYKONOS = {"whitewash": "#FFFFFF", "whitewash2": "#DCD6CC", "thatch": "#8E6440", "door": "#2F62B0", "hole": "#3B3B48",
           "wood": "#5A4030", "sail": "#F5EFE2", "sea": "#2F7FBF", "hill": "#E3CFA2", "hill2": "#CDB27E"}
KINDER = {"thatch": "#5A4636", "wood": "#7E2F2A", "sail": "#CDB894", "frame": "#2E2620", "water": "#4F8FB8"}
CAUSEWAY = {"basalt": "#4E525B", "basalt2": "#3A3D45", "top": "#A2A7AE", "cliff": "#6E6058", "cliff2": "#56493F",
            "grass": "#6BA34E", "sea": "#2E7FAF"}
MOHER = {"cliff": "#5E5047", "cliff2": "#9A8E82", "cliff3": "#B5ACA2", "grass": "#6CA64C", "tower": "#B9AE9C",
         "hole": "#3A3530", "sea": "#2E78A6"}
HALL = {"mtn": "#6C7F78", "mtn2": "#5A6E66", "forest": "#2F5640", "hw1": "#F6F0E4", "hw2": "#F1D498", "hw3": "#E6B19C",
        "roof": "#5A3E36", "church": "#F8F4EC", "spire": "#3A3F4C", "clock": "#3A3F4C", "hole": "#4A4048", "lake": "#3E8C8C"}
BLED = {"rock": "#BDB3A2", "rock2": "#978C7A", "castle": "#D2C2A6", "croof": "#C2553A", "trees": "#3E7048",
        "church": "#F4EBD8", "spire": "#7A5848", "stone2": "#B9AC94", "hole": "#4A4048", "lake": "#3F9A9E",
        "boat": "#6B4A32", "awning": "#D8473C"}
KIRKJU = {"mtn": "#5E6E5C", "mtn2": "#4C5B4B", "grass": "#7DAE5A", "rockf": "#4A4A48", "fall": "#CDEBF2",
          "aurora": "#5FE0A6", "aurora2": "#8EF0C8"}
BELEM = {"stone": "#EDE4D0", "stone2": "#BFB196", "hole": "#4E473F", "water": "#3C86B0", "pop": "#C2453A"}

SEA = ["coastal", "dusk", "meadow", "blush"]

CONCEPTS = [
    Concept("lm2-notredame", "landmark-notre-dame", "Notre-Dame de Paris", notre_dame, overrides=NOTRE,
            checks=[("stone", "sky"), ("lead", "sky"), ("stone", "mid"), ("mid", "sky")], fixes={"sky": ["sky2", "far"], "mid": ["near", "deep"]}),
    Concept("lm2-brandenburg", "landmark-brandenburg-gate", "Brandenburg Gate", brandenburg, overrides=BRAND,
            checks=[("stone", "sky"), ("bronze", "sky"), ("stone", "mid"), ("mid", "sky")], fixes={"sky": ["sky2", "far"], "mid": ["near", "deep"]}),
    Concept("lm2-cologne", "landmark-cologne-cathedral", "Cologne Cathedral", cologne, overrides=COLOGNE,
            checks=[("stone", "sky"), ("steel", "mid")], fixes={"steel": ["#8FA8A2", "#3E4E4B"]}),
    Concept("lm2-charlesbridge", "landmark-charles-bridge", "Charles Bridge & Prague Castle", charles_bridge, overrides=PRAGUE,
            checks=[("vitus", "sky"), ("castle", "mid"), ("btower", "sky"), ("slate", "sky"), ("mid", "sky")],
            fixes={"mid": ["near", "deep"], "sky": ["sky2"], "slate": ["#6A6C7C", "far"]}),
    Concept("lm2-parliament", "landmark-budapest-parliament", "Hungarian Parliament", budapest, palettes=SEA, overrides=BUDA,
            checks=[("stone", "sky"), ("roof", "sky")], fixes={"sky": ["sky2", "far"]}),
    Concept("lm2-alhambra", "landmark-alhambra", "Alhambra", alhambra, overrides=ALHAM,
            checks=[("wall", "sky"), ("wall", "mid"), ("wall", "far"), ("far", "sky"), ("cyp", "near")],
            fixes={"mid": ["near", "deep"], "near": ["deep", "mid"], "far": ["#A9B3C6", "mid"]}),
    Concept("lm2-trevi", "landmark-trevi-fountain", "Trevi Fountain", trevi, overrides=TREVI,
            checks=[("stone", "sky")], fixes={"sky": ["sky2", "far", "mid"]}),
    Concept("lm2-stpeters", "landmark-st-peters", "St Peter's Basilica", st_peters, overrides=PETER,
            checks=[("stone", "sky"), ("dome", "sky")], fixes={"sky": ["sky2", "far", "mid"]}),
    Concept("lm2-duomo", "landmark-florence-duomo", "Florence Duomo", florence, overrides=DUOMO,
            checks=[("dome", "sky"), ("marble", "sky"), ("marble", "far"), ("dome", "glow")], fixes={"sky": ["sky2", "far"], "far": ["mid", "near"], "glow": ["light", "glow2"]}),
    Concept("lm2-cinqueterre", "landmark-cinque-terre", "Cinque Terre", cinque_terre, palettes=SEA, overrides=CINQUE,
            checks=[("mid", "sky"), ("h1", "mid"), ("h5", "mid")], fixes={"mid": ["near", "deep"]}),
    Concept("lm2-dubrovnik", "landmark-dubrovnik", "Dubrovnik old town", dubrovnik, palettes=SEA, overrides=DUBRO,
            checks=[("wall", "sky"), ("wall", "far"), ("far", "sky")], fixes={"far": ["mid", "near"], "sky": ["sky2"]}),
    Concept("lm2-meteora", "landmark-meteora", "Meteora monasteries", meteora, overrides=METEORA,
            checks=[("rock", "sky"), ("rock2", "sky"), ("rock", "rock2"), ("wall", "sky"), ("roof", "sky"), ("rock", "far")],
            fixes={"far": ["mid", "near"], "sky": ["sky2"]}),
    Concept("lm2-mykonos", "landmark-mykonos-windmills", "Mykonos windmills", mykonos, palettes=SEA, overrides=MYKONOS,
            checks=[("whitewash", "sky"), ("whitewash", "sea"), ("thatch", "sky"), ("hill", "sea")], fixes={"sky": ["sky2", "far"]}),
    Concept("lm2-kinderdijk", "landmark-kinderdijk", "Kinderdijk windmills", kinderdijk, palettes=SEA, overrides=KINDER,
            checks=[("thatch", "sky"), ("sail", "sky"), ("thatch", "water"), ("far", "sky")], fixes={"sky": ["sky2", "far"], "far": ["mid", "near"]}),
    Concept("lm2-causeway", "landmark-giants-causeway", "Giant's Causeway", causeway, palettes=SEA, overrides=CAUSEWAY,
            checks=[("basalt", "sea"), ("top", "sea"), ("cliff", "sky")]),
    Concept("lm2-moher", "landmark-cliffs-of-moher", "Cliffs of Moher", moher, palettes=SEA, overrides=MOHER,
            checks=[("cliff", "sea"), ("grass", "sky"), ("cliff2", "sea"), ("cliff3", "sky"), ("tower", "sky")], fixes={"sky": ["sky2"]}),
    Concept("lm2-hallstatt", "landmark-hallstatt", "Hallstatt", hallstatt, palettes=SEA, overrides=HALL,
            checks=[("mtn", "sky"), ("mtn2", "sky"), ("church", "mtn2"), ("spire", "mtn2")], fixes={"spire": ["#23262E"]}),
    Concept("lm2-bled", "landmark-lake-bled", "Lake Bled", bled, palettes=SEA, overrides=BLED,
            checks=[("church", "mid"), ("spire", "far"), ("castle", "sky"), ("trees", "lake"), ("far", "sky"), ("church", "trees")],
            fixes={"mid": ["near", "deep"], "far": ["mid", "near"], "spire": ["#A0705A"]}),
    Concept("lm2-kirkjufell", "landmark-kirkjufell", "Kirkjufell", kirkjufell, palettes=["dusk", "coastal", "meadow", "blush"], overrides=KIRKJU,
            checks=[("mtn", "sky"), ("grass", "mtn")]),
    Concept("lm2-belem", "landmark-belem-tower", "Belém Tower", belem, palettes=SEA, overrides=BELEM,
            checks=[("stone", "sky"), ("stone", "water")], fixes={"sky": ["sky2", "far", "mid"]}),
]
