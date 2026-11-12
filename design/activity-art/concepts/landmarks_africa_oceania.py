"""Mapsie Originals: famous landmarks of Africa and Oceania.

Pyramids of Giza (x2), Abu Simbel, Kilimanjaro, Table Mountain, Victoria Falls, Koutoubia (Marrakech),
Sydney Opera House (x2), Sydney Harbour Bridge, Uluru, Twelve Apostles, Milford Sound, Bora Bora.
"""
from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group, acacia  # noqa: F401
from _common import GIRAFFE
import math


# ================================================================ private helpers
def poly(*pts, close=True) -> str:
    s = "M" + " L".join(f"{x:g} {y:g}" for x, y in pts)
    return s + ("Z" if close else "")


def clip_open(d: Drawing):
    d.raw('<g clip-path="url(#clip)">', '<g clip-path="url(#clip)">')


def clip_close(d: Drawing):
    d.raw("</g>", "</g>")


def clipped(fn):
    """Wrap a whole drawing in the circle clip (line-style shapes are otherwise unclipped)."""
    def draw(d: Drawing):
        clip_open(d)
        fn(d)
        clip_close(d)
    draw.__name__ = fn.__name__
    return draw


def birds(d: Drawing, pts, role="dark"):
    s = " ".join(f"M{x} {y} q{3 * k} {-3 * k} {6 * k} 0 q{3 * k} {-3 * k} {6 * k} 0" for x, y, k in pts)
    d.stroke(role, s, 1.7)


def stars(d: Drawing, pts, role="light"):
    for x, y, r in pts:
        d.marks(role, f"M{x} {y - r} L{x + r * .3} {y - r * .3} L{x + r} {y} L{x + r * .3} {y + r * .3} "
                      f"L{x} {y + r} L{x - r * .3} {y + r * .3} L{x - r} {y} L{x - r * .3} {y - r * .3}Z")


def camel(d: Drawing, tx, ty, s=1.0, role="dark", rider=False):
    """Dromedary facing left, feet at ty + 31*s."""
    path = ("M0 6 C1 3 5 2 7 4 L9 7 C10 10 12 12 14 12 C16 4 20 0 24 0 C30 0 33 6 34 12 C36 14 36 18 34 20 "
            "L33 31 L31 31 L30 21 L28 21 L27 31 L25 31 L24 20 L17 20 L16 31 L14 31 L13 21 L11 21 L10 31 L8 31 "
            "L8 19 C6 16 6 12 5 9 L2 9 C0 9 -1 8 0 6Z")

    def draw():
        d.shape(role, path)
        if rider:
            d.shape(role, "M20 2 C20 -6 22 -9 24 -9 C26 -9 28 -6 28 2Z " + circle(24, -12, 3.2), shadow=False)
    group(d, f"translate({tx} {ty}) scale({s})", draw)


def pyramid(d: Drawing, x, base, w, h, lit="sand", shade="sand2", cap=None):
    d.shape(lit, f"M{x - w / 2} {base} L{x} {base - h} L{x + w / 2} {base}Z")
    d.shape(shade, f"M{x} {base - h} L{x + w / 2} {base} L{x + w * .12} {base}Z", shadow=False)
    if cap:  # Khafre still wears a cap of its smooth limestone casing
        k = .2
        d.shape(cap, f"M{x - w / 2 * k} {base - h + h * k} L{x} {base - h} L{x + w / 2 * k} {base - h + h * k}Z", shadow=False)


def falls(d: Drawing, x0, x1, y0, y1, water="light", lines="far", gap=12):
    d.shape(water, f"M{x0} {y0} Q{(x0 + x1) / 2} {y0 - 3} {x1} {y0} L{x1 + 3} {y1} H{x0 - 3}Z")
    n = max(2, int((x1 - x0) // gap))
    step = (x1 - x0) / (n + 1)
    flow = " ".join(f"M{x0 + step * i:.1f} {y0 + 5} L{x0 + step * i:.1f} {y1 - 6}" for i in range(1, n + 1))
    d.stroke(lines, flow, 1.6)


def frond(x, y, ang, length, droop, w=0.22) -> str:
    """A palm leaf from (x, y) at angle ang (degrees), drooping by `droop`."""
    a = math.radians(ang)
    ex, ey = x + length * math.cos(a), y + length * math.sin(a) + droop
    mx, my = (x + ex) / 2, (y + ey) / 2 - droop * .6
    nx, ny = -(ey - y), ex - x
    k = w / 2
    return (f"M{x:.1f} {y:.1f} Q{mx + nx * k:.1f} {my + ny * k:.1f} {ex:.1f} {ey:.1f} "
            f"Q{mx - nx * k * .3:.1f} {my - ny * k * .3:.1f} {x:.1f} {y:.1f}Z")


def palm(d: Drawing, x0, y0, x1, y1, s=1.0, role="dark", trunk="dark", bend=10):
    d.limb(trunk, f"M{x0} {y0} Q{(x0 + x1) / 2 + bend} {(y0 + y1) / 2} {x1} {y1}", 4.2 * s)
    leaves = " ".join(frond(x1, y1, a, L * s, dr * s) for a, L, dr in
                      [(-170, 26, 10), (-130, 22, 4), (-90, 16, -2), (-50, 22, 4), (-10, 26, 10), (150, 20, 12), (30, 20, 12)])
    d.shape(role, leaves)


def shell(fx, bx, base, tx, ty) -> str:
    """One Opera House sail shell. Front foot fx, back foot bx, tip (tx, ty).
    The front edge rises almost straight and leans out to the tip; the back is a full convex curve.
    Works pointing left (fx < bx) or right (fx > bx)."""
    h = base - ty
    return (f"M{fx} {base} C{fx} {base - h * .5} {tx + (fx - tx) * .35} {ty + h * .2} {tx} {ty} "
            f"C{tx + (bx - tx) * .62} {ty + h * .04} {bx} {ty + h * .42} {bx} {base}Z")


def shell_rib(fx, bx, base, tx, ty) -> str:
    """The ridge line running from tip down the middle of a shell."""
    h = base - ty
    mx = fx + (bx - fx) * .42
    return f"M{tx} {ty} C{tx + (bx - tx) * .3} {ty + h * .2} {mx} {base - h * .45} {mx} {base}"


def opera_house(d: Drawing, shell="shell", shell2="shell2", podium="podium", glass="dark", ribs="sky2"):
    """Sydney Opera House seen side-on from the west: podium at y 128..142, x 22..182, harbour to the left.
    Three staggered shell groups: Concert Hall (front), Joan Sutherland Theatre (behind, shifted right)
    and the small Bennelong restaurant shells at the back (right)."""
    d.shape(podium, "M18 144 L24 126 H170 L184 144Z")
    d.shape(glass, "M24 126 H170 L172 130 H23Z", shadow=False)
    # Bennelong restaurant (small, rear right)
    for s in [(150, 172, 127, 146, 100), (164, 180, 127, 158, 108)]:
        d.shape(shell2, shell_path(*s))
    # Joan Sutherland Theatre: behind, shifted right
    grp_b = [(150, 124, 127, 156, 70), (88, 126, 127, 84, 52), (78, 106, 127, 72, 72), (70, 90, 127, 62, 92)]
    for s in grp_b:
        d.shape(shell2, shell_path(*s))
    # Concert Hall: front
    grp_a = [(124, 96, 127, 130, 78), (60, 104, 127, 54, 44), (48, 82, 127, 40, 68), (38, 64, 127, 30, 92)]
    for s in grp_a:
        d.shape(shell, shell_path(*s), spot=False)
        d.stroke(ribs, shell_rib(*s), 1.2, line=False)


shell_path = shell


# ================================================================ PYRAMIDS OF GIZA
def pyr_sunset(d: Drawing):
    d.disc("glow", 122, 70, 22)
    d.band("far", hills(130, 5, 20))
    pyramid(d, 150, 140, 112, 74)  # Khufu, farthest
    pyramid(d, 90, 136, 106, 72, cap="sand3")  # Khafre, on higher ground
    pyramid(d, 36, 142, 58, 38)  # Menkaure
    d.band("ground", "M-30 146 Q50 138 110 144 T230 142")
    d.band("dune", "M-30 166 Q50 154 110 160 T230 158")
    d.stroke("dark", "M48 152 Q58 158 70 153 M82 154 Q92 160 104 155", 1.1)
    camel(d, 26, 139, .7, rider=True)
    camel(d, 62, 140, .66, rider=True)
    camel(d, 97, 142, .62)
    d.band("near", hills(186, 4, 30), line=False)


SPHINX = ("M16 166 L16 155 Q16 148 24 148 L66 148 L70 132 Q72 118 76 112 L70 102 L65 99 L62 92 L59 89 L62 86 L61 80 "
          "L66 76 L68 66 Q70 60 80 60 L94 60 Q102 60 104 68 L110 100 Q118 112 134 114 Q158 116 170 120 "
          "Q182 126 182 142 L182 166Z")
NEMES = ("M66 76 L68 66 Q70 60 80 60 L94 60 Q102 60 104 68 L112 102 L84 112 L80 96 L74 92 L73 78Z")


def pyr_sphinx(d: Drawing):
    d.disc("glow", 46, 56, 16)
    pyramid(d, 142, 146, 132, 96, cap="sand3")
    pyramid(d, 30, 148, 46, 30)
    d.band("ground", "M-30 150 Q60 142 120 146 T230 144")
    d.shape("sand", SPHINX)
    d.shape("sand2", NEMES, shadow=False, spot=True)
    d.stroke("sand", "M76 68 L100 66 M78 76 L104 74 M82 85 L107 84 M85 94 L110 93 M86 102 L111 100", 2.2, line=False)
    d.shape("sand2", "M64 98 L72 100 L72 112 L66 110Z", shadow=False)  # beard stub / neck shadow
    d.marks("dark", ellipse(66.5, 82, 2.4, 1.3))
    d.stroke("sand2", "M64 72 L67 64", 2.2, line=False)  # uraeus on the brow
    d.stroke("sand2", "M20 157 H64 M88 160 Q86 134 102 124 M152 164 Q148 142 166 130 M120 130 Q130 126 140 130 M118 142 Q130 138 142 142", 1.8)
    d.band("dune", "M-30 172 Q60 162 120 168 T230 164")
    d.band("near", hills(186, 4), line=False)


# ================================================================ ABU SIMBEL
def pharaoh_head(d: Drawing, cx, top, lit="stone", shade="stone2"):
    """Nemes headcloth flaring to the shoulders, face, beard and double crown. Crown tip at y=top."""
    t = top
    d.shape(lit, f"M{cx - 6} {t + 22} L{cx - 5.5} {t + 8} Q{cx - 5} {t} {cx} {t} Q{cx + 5} {t} {cx + 5.5} {t + 8} L{cx + 6} {t + 22}Z")
    d.shape(lit, f"M{cx - 17} {t + 48} L{cx - 13} {t + 30} Q{cx - 12} {t + 20} {cx} {t + 19} Q{cx + 12} {t + 20} {cx + 13} {t + 30} L{cx + 17} {t + 48}Z")
    d.stroke(shade, f"M{cx - 11} {t + 30} L{cx - 14} {t + 44} M{cx + 11} {t + 30} L{cx + 14} {t + 44} "
                    f"M{cx - 8} {t + 34} L{cx - 9} {t + 46} M{cx + 8} {t + 34} L{cx + 9} {t + 46}", 1.4, line=False)
    d.shape(shade, rrect(cx - 7, t + 23, 14, 19, 4), shadow=False)
    d.shape(lit, rrect(cx - 6, t + 24, 12, 17, 3.5), shadow=False, line=False)
    d.marks("dark", ellipse(cx - 2.6, t + 30, 1.5, .8) + ellipse(cx + 2.6, t + 30, 1.5, .8))
    d.stroke(shade, f"M{cx} {t + 31} V{t + 35}", 1.2, line=False)
    d.shape(shade, rrect(cx - 2.2, t + 40, 4.4, 8, 1.5), shadow=False)


def colossus(d: Drawing, cx, b, broken=False):
    """Seated Ramesses II, front view, crown tip at b-112, base b."""
    lit, shade = "stone", "stone2"
    # legs, feet and the throne block behind
    d.shape(lit, rrect(cx - 14, b - 40, 13, 40, 2.5))
    d.shape(lit, rrect(cx + 1, b - 40, 13, 40, 2.5))
    # lap with hands on the knees
    d.shape(lit, rrect(cx - 16, b - 50, 32, 13, 5))
    d.marks(shade, ellipse(cx - 8, b - 42, 5, 2.4) + ellipse(cx + 8, b - 42, 5, 2.4))
    if broken:
        d.shape(lit, poly((cx - 15, b - 46), (cx - 15, b - 60), (cx - 8, b - 55), (cx - 3, b - 66), (cx + 3, b - 57),
                          (cx + 9, b - 64), (cx + 15, b - 56), (cx + 15, b - 46)))
        return
    # torso, arms down to the knees
    d.shape(lit, f"M{cx - 15} {b - 46} L{cx - 18} {b - 70} Q{cx - 18} {b - 76} {cx - 11} {b - 76} H{cx + 11} "
                 f"Q{cx + 18} {b - 76} {cx + 18} {b - 70} L{cx + 15} {b - 46}Z")
    d.stroke(shade, f"M{cx - 11} {b - 72} L{cx - 10} {b - 48} M{cx + 11} {b - 72} L{cx + 10} {b - 48} M{cx - 9} {b - 56} H{cx + 9}", 1.4)
    pharaoh_head(d, cx, b - 112, lit, shade)


def _abu_simbel(d: Drawing):
    d.disc("glow", 166, 58, 13)
    d.band("rock", "M-30 120 Q0 76 30 54 Q100 36 170 54 Q200 76 230 120")
    d.shape("stone2", "M14 166 L26 40 H174 L186 166Z")
    # cornice with its row of sun-worshipping baboons
    d.shape("stone", rrect(28, 40, 144, 6, 1.5), shadow=False)
    d.marks("stone2", " ".join(circle(36 + i * 11, 38, 2.8) for i in range(13)))
    # doorway and the falcon-headed Ra in a niche above it
    d.marks("dark", "M93 166 V132 Q100 124 107 132 V166Z")
    d.marks("stone", rrect(94, 104, 12, 22, 2))
    d.marks("dark", rrect(97, 108, 6, 14, 1.5))
    for cx, br in [(40, False), (73, True), (127, False), (160, False)]:
        colossus(d, cx, 162, br)
    d.band("ground", "M-30 168 Q60 162 120 168 T230 166")
    # the fallen head of the broken colossus, toppled on the sand
    group(d, "rotate(-74 78 166) translate(0 6)", lambda: pharaoh_head(d, 78, 120))
    d.band("near", hills(186, 4, 20), line=False)


def _abu_scaled(d: Drawing):
    group(d, "translate(100 108) scale(.9) translate(-100 -108)", lambda: _abu_simbel(d))


abu_simbel = clipped(_abu_scaled)


# ================================================================ KILIMANJARO
KIBO = ("M-30 150 Q10 128 40 104 L62 76 Q70 66 82 64 L126 62 Q138 63 146 72 L172 100 Q196 122 230 132")
KIBO_SNOW = ("M63 77 Q71 67 82 65.5 L126 63.5 Q137 64.5 145 73 L142 78 L137 75 L134 84 L129 77 L123 86 L118 77 "
             "L110 84 L104 76 L97 86 L91 77 L84 83 L79 76 L72 86Z")


def kilimanjaro(d: Drawing):
    d.disc("glow", 148, 40, 13)
    d.band("far", "M-30 128 L-6 112 L6 98 L12 104 L18 90 L26 100 L36 96 L54 120 L230 124")  # Mawenzi
    d.band("mid", KIBO)
    d.shape("light", KIBO_SNOW, shadow=False)
    d.shape("light", cloud(8, 112, 1.25))
    d.shape("light", cloud(136, 106, 1.1))
    d.band("ground", "M-30 146 Q60 138 120 144 T230 140")
    group(d, "translate(16 100) scale(.36)", lambda: d.shape("dark", GIRAFFE))
    acacia(d, 26, 34, .82)
    d.band("near", hills(174, 6, 10))
    d.band("deep", hills(190, 4, 40), line=False)


# ================================================================ TABLE MOUNTAIN
TABLE = ("M-30 116 L4 108 L16 92 L26 76 L34 88 L44 76 L50 68 H144 L150 72 L156 92 L166 100 L230 112")
LIONS_HEAD = "M140 132 Q150 112 164 102 Q168 88 176 86 Q184 86 186 98 Q196 112 216 132Z"
TABLECLOTH = ("M46 70 C46 63 54 61 60 63 C64 58 74 58 78 62 C84 57 94 58 98 62 C104 57 114 58 118 62 C124 58 134 59 138 63 "
              "C144 61 150 64 148 71 L150 76 C148 80 145 78 144 84 C142 80 139 80 138 88 C136 82 133 82 132 78 "
              "L60 76 C56 76 52 82 50 76 Z")


def table_mountain(d: Drawing):
    d.disc("glow", 160, 44, 13)
    d.band("near", TABLE)
    d.shape("light", TABLECLOTH)
    d.shape("deep", LIONS_HEAD)
    d.band("mid", hills(122, 6, 10))
    for i, (x, w, h) in enumerate([(30, 7, 5), (39, 5, 9), (46, 8, 4), (58, 6, 7), (67, 9, 5), (80, 5, 11), (87, 7, 6), (98, 9, 8),
                                   (110, 6, 5), (118, 7, 7), (128, 8, 4)]):
        d.shape("light" if i % 3 else "hero2", rrect(x, 128 - h, w, h + 6, .8), shadow=False, line=i % 3 == 0)
    d.band("far", "M-30 130 Q100 126 230 130")
    d.stroke("light", "M30 146 h18 M76 156 h24 M132 144 h16 M48 170 h20 M120 172 h26", 2)
    d.shape("light", "M146 152 L146 124 L162 150Z", spot=True)
    d.shape("hero", "M136 154 H166 L162 160 H140Z")
    d.band("sky2", waves(182, 3, 30), line=False)


# ================================================================ VICTORIA FALLS
def victoria_falls(d: Drawing):
    """A mile-wide curtain split by wooded islands, spray boiling out of the gorge, a rainbow in the mist."""
    d.band("far", "M-30 48 Q100 42 230 48")
    # "the smoke that thunders": spray billowing up behind the lip
    d.raw('<path d="M110 60 C100 46 110 30 126 32 C130 14 156 10 164 28 C178 22 194 36 188 52 C198 56 196 62 192 64Z" fill="#fff" opacity=".7"/>', "")
    d.band("river", "M-30 56 Q100 52 230 56")
    d.stroke("light", "M14 60 h16 M100 58 h18 M170 60 h14", 1.6, line=False)
    d.band("rock", "M-30 66 Q100 64 230 66")
    d.shape("light", "M-30 67 Q100 64 230 67 V132 H-30Z")
    xs = range(-22, 230, 12)
    d.stroke("river", " ".join(f"M{x} 73 V126" for x in xs), 1.6, line=False)
    d.raw("", '<path d="M40 84 V112 M70 76 V100 M130 80 V108 M160 76 V96" fill="none" stroke="%s" stroke-width="2.4" stroke-linecap="round"/>' % d.c.get("ink", ""))
    # wooded islands on the lip between the sections
    d.shape("veg", "M38 69 Q42 58 54 60 Q62 52 72 58 Q84 56 88 69Z M126 69 Q130 59 142 60 Q150 53 160 59 Q172 58 172 69Z")
    # rainbow in the spray
    for i, role in enumerate(["rb1", "rb2", "rb3"]):
        r = 70 - i * 5
        d.stroke(role, f"M{100 - r} 150 A{r} {r} 0 0 1 {100 + r} 150", 4.6)
    for x, y, s in [(-14, 124, 1.6), (30, 130, 1.3), (80, 122, 1.5), (132, 128, 1.4), (176, 122, 1.3)]:
        d.shape("light", cloud(x, y, s))
    d.band("light", "M-30 136 Q100 128 230 136", shadow=False, line=False)
    # the near cliff with its rainforest
    d.band("veg", "M-30 154 Q40 146 90 154 T230 150")
    for x, y, r in [(8, 150, 13), (28, 156, 10), (174, 148, 12), (192, 152, 11)]:
        d.shape("veg", circle(x, y, r))
    d.band("veg2", hills(180, 5, 20), line=False)


# ================================================================ MARRAKECH: KOUTOUBIA
def merlons(x, y, w, n, h=5.0) -> str:
    """A row of stepped Moorish merlons sitting on y, spanning x..x+w."""
    mw = w / n
    s = ""
    for i in range(n):
        x0 = x + i * mw + mw * .1
        x1 = x0 + mw * .8
        s += (f"M{x0:.1f} {y} V{y - h * .5:.1f} H{x0 + mw * .15:.1f} V{y - h * .8:.1f} H{x0 + mw * .3:.1f} "
              f"L{(x0 + x1) / 2:.1f} {y - h:.1f} L{x1 - mw * .3:.1f} {y - h * .8:.1f} H{x1 - mw * .15:.1f} V{y - h * .5:.1f} H{x1:.1f} V{y}Z ")
    return s


def pointed_arch(x, y, w, h) -> str:
    return f"M{x} {y + h} V{y + w * .5} Q{x} {y} {x + w / 2} {y - w * .25} Q{x + w} {y} {x + w} {y + w * .5} V{y + h}Z"


def koutoubia(d: Drawing):
    d.disc("glow", 150, 76, 20)
    d.band("far", "M-30 146 L10 126 L40 134 L70 112 L104 132 L134 116 L170 130 L200 118 L230 130")
    d.shape("light", "M10 126 L18 130 L24 128 L28 131 L40 134 L28 125 L20 124Z M70 112 L80 120 L86 117 L90 121 L96 126 L84 115Z "
                     "M134 116 L144 122 L150 120 L156 124 L144 116Z M200 118 L190 122 L182 120 L192 116Z", shadow=False, line=False)
    # minaret shaft
    d.shape("stone", "M84 178 V60 H116 V178Z")
    d.shape("stone", merlons(84, 60, 32, 4, 6), shadow=False)
    d.shape("tile", rrect(84, 62, 32, 5, 0), shadow=False, spot=True)
    d.shape("stone2", pointed_arch(91, 76, 18, 26), shadow=False)
    d.stroke("stone", "M91 92 L100 84 L109 92 M91 100 L100 92 L109 100", 1.3, line=False)
    d.shape("stone2", pointed_arch(88, 112, 10, 18), shadow=False)
    d.shape("stone2", pointed_arch(102, 112, 10, 18), shadow=False)
    d.marks("dark", pointed_arch(97, 142, 6, 12))
    d.stroke("stone2", "M88 72 H112 M88 106 H112 M88 136 H112", 1.4)
    # lantern, dome and three golden globes
    d.shape("stone", "M92 60 V38 H108 V60Z")
    d.shape("stone", merlons(92, 38, 16, 2, 4), shadow=False)
    d.shape("tile", rrect(92, 40, 16, 3, 0), shadow=False)
    d.marks("dark", pointed_arch(97.5, 46, 5, 10))
    d.shape("stone2", "M94 34 Q94 26 100 24 Q106 26 106 34Z")
    d.stroke("gold", "M100 24 V8", 1.6)
    for y, r in [(20, 3.2), (14.2, 2.6), (9.5, 2)]:
        d.shape("gold", circle(100, y, r), shadow=False, spot=True)
    palm(d, 46, 182, 42, 120, 1.05, role="leaf", trunk="trunk", bend=-6)
    palm(d, 156, 186, 160, 128, .95, role="leaf", trunk="trunk", bend=8)
    d.band("wall", "M-30 166 H230", line=True)
    d.shape("wall", merlons(-30, 166, 260, 26, 7), shadow=False)
    d.band("deep", hills(190, 4, 20), line=False)


# ================================================================ SYDNEY OPERA HOUSE
def opera_harbour(d: Drawing):
    d.disc("glow", 160, 52, 14)
    d.band("far", "M-30 120 Q60 114 120 118 T230 116")
    for x, w, h in [(132, 8, 16), (142, 6, 26), (150, 9, 20), (162, 7, 32), (172, 8, 18), (182, 6, 24)]:
        d.shape("far", rrect(x, 118 - h, w, h + 4, .6), shadow=False, line=False)
    opera_house(d)
    d.band("mid", waves(142, 3, 26))
    d.stroke("light", "M30 156 h16 M70 162 h22 M124 154 h18 M150 166 h20 M44 174 h18", 2)
    # a harbour ferry
    d.shape("ferry", "M38 160 H76 L72 168 H42Z")
    d.shape("light", rrect(44, 150, 26, 10, 2))
    d.shape("ferry2", rrect(46, 146, 20, 5, 1.5), shadow=False, spot=True)
    d.band("near", waves(182, 3, 32), line=False)


def opera_bridge(d: Drawing):
    d.disc("glow", 150, 46, 13)
    # the Harbour Bridge behind, at left
    arch_bridge(d, 60, 64, steel="far", pylon="far", deck_y=100, crown=50, bearing=124, lattice="sky")
    group(d, "translate(62 30) scale(.68)", lambda: opera_house(d))
    d.band("mid", waves(128, 3, 26))
    d.stroke("light", "M24 150 h18 M64 158 h20 M120 148 h16 M150 160 h20 M90 170 h18", 2)
    d.band("near", waves(180, 3, 32), line=False)


# ================================================================ SYDNEY HARBOUR BRIDGE
def arch_bridge(d: Drawing, cx, half, steel="steel", pylon="pylon", deck_y=118, crown=72,
                bearing=136, lattice="sky", hangers=True, pylon2=None):
    """A single steel through-arch with a granite pylon at each end.
    cx: centre x, half: half-span; the arch springs at y=bearing; deck at deck_y."""
    xl, xr = cx - half, cx + half
    top_end = deck_y - 12  # where the top chord meets the pylons
    depth = 9  # arch depth at the crown
    # arch ribbon: top chord from pylon to pylon, bottom chord from bearing to bearing
    a = (f"M{xl} {bearing} Q{cx} {2 * (crown + depth) - bearing} {xr} {bearing} "
         f"L{xr - 4} {top_end} Q{cx} {2 * crown - top_end} {xl + 4} {top_end}Z")
    d.shape(steel, a)
    # lattice: zigzag between the chords
    pts = []
    n = 16
    for i in range(n + 1):
        t = i / n
        x = xl + 4 + (xr - xl - 8) * t
        u = (x - cx) / (half - 4)
        y_top = crown + (top_end - crown) * u * u
        ub = (x - cx) / half
        y_bot = crown + depth + (bearing - crown - depth) * ub * ub
        pts.append((x, y_top + 2.4 if i % 2 == 0 else y_bot - 2.4))
    d.stroke(lattice, "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts), 1.4, line=False)
    if hangers:
        hs = []
        for i in range(-5, 6):
            x = cx + i * half / 6.2
            ub = (x - cx) / half
            y_bot = crown + depth + (bearing - crown - depth) * ub * ub
            if y_bot < deck_y - 2:
                hs.append(f"M{x:.1f} {y_bot:.1f} V{deck_y}")
        d.stroke(steel, " ".join(hs), 1.3)
    # deck
    d.shape(steel, f"M-30 {deck_y} H230 V{deck_y + 5} H-30Z")
    # pylons
    pw = half * .2
    ptop = deck_y - 30
    for px in (xl - pw * .1, xr + pw * .1):
        d.shape(pylon, f"M{px - pw / 2} {bearing + 30} V{ptop + 4} L{px - pw / 2 + 2} {ptop} H{px + pw / 2 - 2} L{px + pw / 2} {ptop + 4} V{bearing + 30}Z")
        if pylon2:
            d.shape(pylon2, rrect(px - pw / 2, ptop + 8, pw, 2.4, 0), shadow=False)
            d.marks(pylon2, pointed_arch(px - pw * .22, deck_y - 14, pw * .44, 12))


def harbour_bridge(d: Drawing):
    d.disc("glow", 100, 100, 26)
    d.band("far", "M-30 132 Q100 126 230 132")
    arch_bridge(d, 100, 70, deck_y=114, crown=56, bearing=134, lattice="sky", pylon2="pylon2")
    d.band("mid", waves(138, 3, 24))
    d.stroke("light", "M28 152 h16 M140 150 h18 M110 172 h22 M52 176 h14", 2)
    # Sydney ferry: green hull, cream cabin, yellow funnel trim
    d.shape("ferry", "M60 160 H118 L112 170 H66Z")
    d.shape("light", rrect(68, 150, 42, 11, 2))
    d.marks("ferry", " ".join(rrect(72 + i * 7, 153, 4.5, 4, 1) for i in range(5)))
    d.shape("ferry2", rrect(80, 145, 18, 6, 1.5), spot=True)
    d.band("near", waves(184, 3, 32), line=False)


# ================================================================ ULURU
ULURU = ("M14 140 C15 126 20 114 30 107 C36 102 44 98 56 97 Q70 93 84 96 Q98 92 112 95 Q126 91 140 95 "
         "Q156 96 166 104 C177 112 183 126 186 140Z")


def uluru(d: Drawing):
    d.disc("glow", 156, 52, 14)
    d.raw('<g transform="translate(0 140) scale(1 1.3) translate(0 -140)">', '<g transform="translate(0 140) scale(1 1.3) translate(0 -140)">')
    d.shape("rock", ULURU)
    d.shape("rock2", "M166 104 C177 112 183 126 186 140 H170 C172 126 170 114 166 104Z", shadow=False)
    d.stroke("rock2", "M38 104 Q36 120 40 138 M56 98 Q54 116 58 136 M76 96 Q78 112 74 132 M98 94 Q96 112 100 128 "
                      "M120 94 Q124 112 118 130 M142 96 Q140 116 146 136 M24 116 Q24 128 28 138", 2)
    d.marks("rock2", ellipse(64, 128, 4, 2.2) + ellipse(110, 132, 5, 2.2) + ellipse(136, 126, 3, 2))
    d.raw("</g>", "</g>")
    d.band("earth", "M-30 140 Q100 135 230 140")
    for x, y, s in [(26, 156, 1), (64, 162, .8), (138, 158, .9), (176, 164, 1.1), (104, 168, .7)]:
        d.shape("bush", f"M{x - 10 * s} {y} Q{x - 9 * s} {y - 9 * s} {x} {y - 10 * s} Q{x + 9 * s} {y - 9 * s} {x + 10 * s} {y}Z")
    # desert oak
    d.limb("dark", "M158 170 L160 118 M160 132 L150 116 M160 126 L170 112", 3.4)
    d.shape("dark", ellipse(150, 112, 9, 6) + ellipse(171, 108, 9, 6) + ellipse(160, 101, 10, 7), shadow=False)
    d.band("near", hills(178, 5, 20))


# ================================================================ TWELVE APOSTLES
def stack(d: Drawing, x0, x1, top, base, jag=(0, 0, 0, 0)):
    """A weathered limestone stack: flared foot, notched sides, domed scrubby crown."""
    w, h = x1 - x0, base - top
    a, b, c, e = (j * w for j in jag)
    left = [(x0 - w * .14, base), (x0 + a, base - h * .3), (x0 + w * .08, base - h * .5), (x0 + b, base - h * .72), (x0 + w * .1, top + h * .1)]
    right = [(x1 - w * .12, top + h * .12), (x1 + c, base - h * .7), (x1 - w * .06, base - h * .5), (x1 + e, base - h * .28), (x1 + w * .14, base)]
    crown = f"Q{x0 + w * .2} {top - 2} {x0 + w * .5} {top - 1} Q{x1 - w * .15} {top - 1} "
    p = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in left) + f" {crown}" + " L".join(f"{x:.1f} {y:.1f}" for x, y in right) + "Z"
    p = p.replace(f" {crown}", f" {crown}", 1)
    d.shape("stone", p)
    # shaded right flank
    d.shape("stone2", f"M{x0 + w * .62} {top + h * .06} L{x1 - w * .12} {top + h * .12} L{x1 + c} {base - h * .7} L{x1 - w * .06} {base - h * .5} "
                      f"L{x1 + e} {base - h * .28} L{x1 + w * .14} {base} H{x0 + w * .6}Z", shadow=False)
    d.stroke("stone2", " ".join(f"M{x0 + w * .06:.1f} {top + h * f:.1f} H{x1 - w * .2:.1f}" for f in (.3, .52, .74)), 1.3, line=False)
    d.shape("grass", f"M{x0 + w * .1} {top + h * .1} Q{x0 + w * .2} {top - 2} {x0 + w * .5} {top - 1} Q{x1 - w * .15} {top - 1} {x1 - w * .12} {top + h * .12} "
                     f"Q{x0 + w * .5} {top + h * .04} {x0 + w * .1} {top + h * .1}Z", shadow=False, line=False)


def twelve_apostles(d: Drawing):
    d.disc("glow", 52, 96, 18)
    d.band("far", "M-30 104 H230")
    d.shape("stone2", "M-30 104 L-30 92 Q-10 90 6 96 L14 104Z", shadow=False)
    # mainland cliffs receding along the right
    d.shape("stone", "M230 40 L170 56 L132 84 L124 106 L124 112 Q160 140 230 168Z")
    d.shape("stone2", "M132 84 L124 106 L124 112 Q160 140 230 168 V176 Q170 150 140 122Z", shadow=False)
    d.shape("grass", "M230 36 L168 52 L130 82 L134 86 L172 60 L230 46Z")
    d.stroke("stone2", "M140 96 L230 72 M138 108 L230 92 M150 124 L230 116", 1.2, line=False)
    d.band("mid", waves(116, 2.5, 22))
    stack(d, 92, 106, 86, 118, (.06, -.08, .08, -.04))
    stack(d, 22, 34, 94, 120, (-.04, .06, -.06, .04))
    stack(d, 110, 118, 98, 114)
    stack(d, 42, 76, 64, 150, (-.06, .1, -.1, .06))
    d.shape("light", ellipse(60, 150, 26, 4) + ellipse(99, 118, 12, 2.5) + ellipse(28, 120, 9, 2), shadow=False)
    d.band("near", waves(158, 3, 28))
    d.stroke("light", "M20 172 h18 M90 170 h22 M140 178 h18", 2)
    d.band("deep", waves(186, 3, 32), line=False)


# ================================================================ MILFORD SOUND
MITRE = ("M52 152 Q74 124 84 90 L94 52 L99 30 L103 36 L106 32 L112 58 Q120 92 136 114 Q150 132 170 152Z")


def milford(d: Drawing):
    d.shape("light", cloud(130, 50, 1.1), shadow=False)
    d.shape("rock2", "M100 152 L120 96 L140 72 L160 64 L176 80 L230 88 V152Z")
    d.shape("rock", MITRE)
    d.shape("rock2", "M103 36 L106 32 L112 58 Q120 92 136 114 Q150 132 170 152 H118 Q114 110 108 70Z", shadow=False)
    d.shape("light", "M99 30 L103 36 L106 32 L108 40 L104 44 L101 40 L97 44Z", shadow=False)
    d.shape("forest", "M52 152 Q70 130 80 110 Q92 120 106 116 Q122 112 132 110 Q150 130 170 152Z")
    # fiord walls
    d.shape("forest2", "M-30 30 Q4 32 22 54 Q36 90 44 120 L58 152 H-30Z")
    d.shape("forest2", "M230 70 Q196 74 180 96 Q170 120 160 152 H230Z")
    falls(d, 20, 25, 72, 148, lines="sky2")
    d.raw('<path d="M40 106 Q70 96 104 104 Q136 96 168 104 Q136 112 104 108 Q70 114 40 106Z" fill="#fff" opacity=".7"/>', "")
    d.band("water", "M-30 150 H230")
    d.raw(f'<path d="{MITRE}" fill="#ffffff" opacity=".18" transform="matrix(1 0 0 -1 0 302)"/>', "")
    d.stroke("light", "M20 166 h18 M120 164 h16 M150 176 h20 M60 180 h20", 2)
    # a cruise boat
    d.shape("light", "M50 162 H96 L90 170 H56Z")
    d.shape("light", rrect(58, 154, 28, 8, 2))
    d.shape("hero", rrect(64, 150, 14, 5, 1.5), shadow=False, spot=True)
    d.band("deep", waves(186, 3, 32), line=False)


# ================================================================ BORA BORA
OTEMANU = ("M10 122 Q28 114 42 108 L52 96 Q58 86 64 92 L68 86 Q72 80 76 90 L84 98 Q90 96 92 90 L96 64 L100 46 "
           "Q103 38 110 38 L118 37 Q124 39 124 46 L125 70 L130 92 Q150 100 168 110 Q182 116 194 122Z")


def bungalow(d: Drawing, x, y, s=1.0):
    """An overwater bungalow: thatched hip roof on a hut on stilts, deck level y."""
    d.stroke("wood", f"M{x - 8 * s} {y} V{y + 9 * s} M{x} {y} V{y + 9 * s} M{x + 8 * s} {y} V{y + 9 * s}", 1.5 * s)
    d.shape("wood", rrect(x - 12 * s, y - 2 * s, 24 * s, 3 * s, .8), shadow=False)
    d.shape("light", rrect(x - 9 * s, y - 11 * s, 18 * s, 10 * s, 1))
    d.marks("dark", rrect(x - 2.5 * s, y - 8 * s, 5 * s, 7 * s, .8))
    d.shape("thatch", f"M{x - 15 * s} {y - 9 * s} L{x - 6 * s} {y - 22 * s} H{x + 6 * s} L{x + 15 * s} {y - 9 * s}Z", spot=True)
    d.stroke("thatch2", f"M{x - 10 * s} {y - 12 * s} H{x + 10 * s}", 1.2 * s, line=False)


def bora_bora(d: Drawing):
    d.disc("glow", 160, 50, 13)
    d.shape("light", cloud(116, 36, .9), shadow=False)
    d.band("sea", "M-30 116 H230")
    d.shape("island", OTEMANU)
    d.shape("rock", "M92 90 L96 64 L100 46 Q103 38 110 38 L118 37 Q124 39 124 46 L125 70 L128 86 Q118 82 110 88 Q100 82 92 90Z", shadow=False)
    d.stroke("island", "M104 50 V74 M112 44 V70 M119 46 V66", 1.6, line=False)
    d.band("lagoon", "M-30 124 Q100 120 230 124")
    d.band("lagoon2", "M-30 140 Q100 132 230 140", shadow=False, line=False)
    # boardwalk to the bungalows
    d.stroke("wood", "M-10 168 L40 156 L82 146 L116 138 L146 132", 2.4)
    for x, y, s in [(146, 132, .62), (116, 138, .72), (82, 146, .86), (40, 156, 1.05)]:
        bungalow(d, x, y, s)
    # motu with a palm
    d.shape("sand", "M150 126 Q170 118 196 124 L196 128 H150Z")
    palm(d, 176, 126, 168, 98, .6, role="island", trunk="wood", bend=6)
    d.stroke("light", "M100 166 h22 M150 158 h18 M130 178 h20", 2)
    d.band("lagoon3", waves(186, 3, 32), line=False)


# ================================================================ concepts
SAND = {"sand": "#EDBE6F", "sand2": "#C98E45", "sand3": "#FBEBCB", "dune": "#D9A05A"}
STONE = {"stone": "#EBBE86", "stone2": "#C08350", "rock": "#A9653A"}
OPERA = {"shell": "#FFFFFF", "shell2": "#E7E1D4", "podium": "#C99A74", "ferry": "#2E7D4F", "ferry2": "#F2C14E"}
KOUTOUBIA = {"stone": "#D99470", "stone2": "#B06A4A", "tile": "#3BA58B", "gold": "#E8B64A", "leaf": "#4E8A4A",
             "trunk": "#8A5A33", "wall": "#C97B52"}
BRIDGE = {"steel": "#6F7D8C", "pylon": "#DCC7A1", "pylon2": "#B59C76", "ferry": "#2E7D4F", "ferry2": "#F2C14E"}
ULURU_C = {"rock": "#C8552B", "rock2": "#97361C", "earth": "#E08A4E", "bush": "#9AA04A"}
APOSTLES = {"stone": "#E6B67C", "stone2": "#BF8550", "grass": "#7E9B4E"}
MILFORD = {"rock": "#7F8996", "rock2": "#5F6976", "forest": "#3E7556", "forest2": "#2C5440", "water": "#2F6F86"}
BORA = {"sea": "#1C6FA0", "lagoon": "#36C2BC", "lagoon2": "#7FE0D6", "lagoon3": "#24A7A7", "island": "#3E8E4E",
        "rock": "#4D6150", "thatch": "#C99A5B", "thatch2": "#9C7038", "wood": "#7A5030", "sand": "#F2DDAA"}
NO_SEA_GOLD = ["coastal", "meadow", "blush", "dusk"]

CONCEPTS = [
    Concept("lm-pyramids-sunset", "landmark-pyramids", "Pyramids of Giza", pyr_sunset, overrides=SAND,
            checks=[("sand", "sky"), ("sand", "glow"), ("sand", "far"), ("dark", "ground"), ("sand", "ground"), ("dark", "dune")],
            fixes={"glow": ["#E2704A", "near", "light"], "sky": ["sky2", "far", "light"], "far": ["mid", "near"], "ground": ["#C98A4B", "near", "mid"],
                   "mid": ["near", "ground"]}),
    Concept("lm-pyramids-sphinx", "landmark-pyramids", "Pyramids of Giza: Sphinx", pyr_sphinx, overrides={**SAND, "sand": "#E9B96E", "sand2": "#B98444"},
            checks=[("sand", "sky"), ("sand", "ground"), ("sand", "glow")],
            fixes={"sky": ["sky2", "far", "light"], "ground": ["#C48548", "near", "mid"], "mid": ["near", "deep"], "glow": ["#E2704A", "near", "light"]}),
    Concept("lm-abusimbel-temple", "landmark-abu-simbel", "Abu Simbel", abu_simbel, overrides=STONE,
            checks=[("rock", "sky"), ("stone", "stone2"), ("stone", "ground"), ("rock", "glow")],
            fixes={"ground": ["mid", "near"], "glow": ["light", "glow2"]}),
    Concept("lm-kilimanjaro-savannah", "landmark-kilimanjaro", "Mount Kilimanjaro", kilimanjaro,
            checks=[("mid", "sky"), ("light", "mid"), ("far", "sky"), ("mid", "far"), ("dark", "ground"), ("dark", "mid"), ("ground", "mid")],
            fixes={"far": ["near", "deep"], "ground": ["far", "light"]}),
    Concept("lm-tablemountain-bay", "landmark-table-mountain", "Table Mountain", clipped(table_mountain), palettes=NO_SEA_GOLD,
            checks=[("near", "sky"), ("light", "near"), ("deep", "near"), ("light", "sky"), ("mid", "far"), ("light", "mid"), ("deep", "mid")],
            fixes={"sky": ["sky2", "glow2", "far"], "far": ["sky2", "light"], "deep": ["dark", "mid"]}),
    Concept("lm-victoriafalls-rainbow", "landmark-victoria-falls", "Victoria Falls", clipped(victoria_falls),
            overrides={"river": "#8FB8C4", "rock": "#4E3B2E", "veg": "#4E8A4A", "veg2": "#3A6B3E",
                       "rb1": "#E8553E", "rb2": "#F5C44E", "rb3": "#4A90C8"},
            checks=[("light", "rock"), ("far", "sky"), ("veg", "light"), ("rb1", "light"), ("far", "river"), ("veg", "river")],
            fixes={"far": ["mid", "near"]}),
    Concept("lm-marrakech-koutoubia", "landmark-marrakech", "Koutoubia, Marrakech", koutoubia, overrides=KOUTOUBIA,
            checks=[("stone", "sky"), ("stone", "far"), ("stone", "glow"), ("leaf", "sky"), ("wall", "deep")],
            fixes={"glow": ["light", "glow2", "pop"], "far": ["near", "deep"], "sky": ["sky2", "far"]}),
    Concept("lm-opera-harbour", "landmark-sydney-opera-house", "Sydney Opera House", opera_harbour, palettes=NO_SEA_GOLD, overrides=OPERA,
            checks=[("shell", "sky"), ("shell", "far"), ("light", "mid"), ("podium", "mid")],
            fixes={"sky": ["sky2", "far", "mid"], "far": ["mid", "near", "deep"], "podium": ["#9C6B52", "#7E5442"]}),
    Concept("lm-opera-bridge", "landmark-sydney-opera-house", "Sydney Opera House & Bridge", opera_bridge, palettes=NO_SEA_GOLD, overrides=OPERA,
            checks=[("shell", "far"), ("far", "sky"), ("podium", "mid")],
            fixes={"far": ["mid", "near", "deep"], "podium": ["#9C6B52", "#7E5442"]}),
    Concept("lm-harbourbridge-arch", "landmark-harbour-bridge", "Sydney Harbour Bridge", harbour_bridge, palettes=NO_SEA_GOLD, overrides=BRIDGE,
            checks=[("steel", "sky"), ("steel", "glow"), ("pylon", "sky"), ("pylon", "mid"), ("light", "mid")],
            fixes={"sky": ["sky2", "far"], "glow": ["glow2", "light", "pop"], "pylon": ["#BFA57E", "#A88D66"]}),
    Concept("lm-uluru-sunset", "landmark-uluru", "Uluru", uluru, overrides=ULURU_C,
            checks=[("rock", "sky"), ("rock", "earth"), ("bush", "earth"), ("dark", "sky")],
            fixes={"sky": ["sky2", "far", "deep"]}),
    Concept("lm-apostles-stacks", "landmark-twelve-apostles", "Twelve Apostles", clipped(twelve_apostles), palettes=NO_SEA_GOLD, overrides=APOSTLES,
            checks=[("stone", "sky"), ("stone", "far"), ("stone", "mid"), ("stone", "glow")],
            fixes={"glow": ["#E2704A", "pop", "light"], "far": ["mid", "near"], "mid": ["near", "deep"]}),
    Concept("lm-milford-mitre", "landmark-milford-sound", "Milford Sound", clipped(milford), palettes=NO_SEA_GOLD, overrides=MILFORD,
            checks=[("rock", "sky"), ("forest2", "sky")]),
    Concept("lm-borabora-lagoon", "landmark-bora-bora", "Bora Bora", bora_bora, overrides=BORA,
            checks=[("island", "sky"), ("rock", "sky"), ("thatch", "lagoon2"), ("sea", "sky")],
            fixes={"sky": ["sky2", "light"]}),
]
