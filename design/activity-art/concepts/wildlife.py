"""Wildlife & nature: three concepts each for sixteen wildlife, landscape and sky activities."""
import math

from _common import Concept, Drawing, cloud, fish, circle, ellipse, waves, hills, rrect, group, acacia  # noqa: F401
from _common import GIRAFFE

_uid = [0]


# ================================================================ private helpers
def _id(prefix):
    _uid[0] += 1
    return f"{prefix}{_uid[0]}"


def clipped(d: Drawing, path: str, fn):
    """Draw fn() clipped to `path` (stripes on a zebra, rosettes on a leopard)."""
    cid = _id("wildclip")
    tag = f'<clipPath id="{cid}"><path d="{path}"/></clipPath><g clip-path="url(#{cid})">'
    d.raw(tag, tag)
    fn()
    d.raw("</g>", "</g>")


def flip(d: Drawing, fn, cx=100):
    group(d, f"translate({2 * cx} 0) scale(-1 1)", fn)


def scallop(cx, cy, r, n=12, bump=0.22, rot=0.0):
    """A bumpy circle: manes, tree crowns, blossom clusters."""
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
    """A pointed leaf from (x, y) pointing at `angle` degrees (0 = right, -90 = up)."""
    a = math.radians(angle)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    tx, ty = x + ux * length, y + uy * length
    c1 = (x + ux * length * 0.35 + px * width, y + uy * length * 0.35 + py * width)
    c2 = (x + ux * length * 0.35 - px * width, y + uy * length * 0.35 - py * width)
    return (f"M{x:.1f} {y:.1f} Q{c1[0]:.1f} {c1[1]:.1f} {tx:.1f} {ty:.1f} "
            f"Q{c2[0]:.1f} {c2[1]:.1f} {x:.1f} {y:.1f}Z")


def palm(d: Drawing, x, y, h=70, lean=8, role="dark", s=1.0):
    """Palm tree silhouette with its foot at (x, y)."""
    tx, ty = x + lean, y - h
    d.limb(role, f"M{x} {y} Q{x + lean * 0.1} {y - h * 0.55} {tx} {ty}", 5 * s)
    for ang, ln in [(-160, 34), (-125, 30), (-60, 30), (-20, 34), (15, 28), (165, 28)]:
        a = math.radians(ang)
        ex, ey = tx + math.cos(a) * ln * s, ty + math.sin(a) * ln * s
        mx, my = tx + math.cos(a) * ln * s * 0.5, ty + math.sin(a) * ln * s * 0.5 - 9 * s
        w = 6 * s
        d.shape(role, f"M{tx} {ty} Q{mx:.1f} {my - w:.1f} {ex:.1f} {ey:.1f} Q{mx:.1f} {my + w * 0.6:.1f} {tx} {ty}Z", shadow=False)


def birds(d: Drawing, pts, role="dark"):
    s = " ".join(f"M{x} {y} q{3 * k} {-3 * k} {6 * k} 0 q{3 * k} {-3 * k} {6 * k} 0" for x, y, k in pts)
    d.stroke(role, s, 1.8)


def grass(d: Drawing, x0, x1, y, h=12, role="near", step=16, line=False):
    """Little grass tufts along y."""
    x, i = x0, 0
    while x < x1:
        k = h * (0.75 + 0.25 * ((i * 5) % 3) / 2)
        d.shape(role, f"M{x} {y} L{x + 2} {y - k * 0.7} L{x + 4} {y - 2} L{x + 6} {y - k} L{x + 8} {y - 2} "
                      f"L{x + 10} {y - k * 0.6} L{x + 12} {y}Z", shadow=False, line=line)
        x += step
        i += 1


# ================================================================ GAME DRIVE
LION_BODY = ("M86 94 C96 84 122 85 140 89 C150 92 154 99 152 107 C151 111 148 113 146 114 L146 123 L139 123 L138 114 "
             "L133 113 L132 123 L125 123 L124 111 L104 111 L103 123 L96 123 L95 111 L92 110 L91 123 L84 123 L84 106 "
             "C82 100 83 97 86 94Z")
LION_HEAD = "M64 79 C70 72 82 72 87 80 C91 87 88 97 81 100 L70 100 C63 98 59 93 60 88 C60 84 61 81 64 79Z"


def lion(d: Drawing):
    d.stroke("hero", "M150 97 C162 100 164 112 160 120", 2.6, line=True)
    d.shape("hero2", ellipse(161, 122, 3.4, 5), shadow=False)
    d.shape("hero", LION_BODY)
    d.shape("hero2", scallop(84, 86, 19, 14, 0.15), spot=True)
    d.shape("hero", circle(77, 72, 4.5), shadow=False)
    d.shape("hero", LION_HEAD)
    d.marks("mark", circle(70, 84, 1.8))
    d.marks("mark", "M59 88 L64 87 L62 92Z")
    d.stroke("mark", "M62 95 Q66 97 70 95", 1.3)


def gamedrive_lion(d: Drawing):
    d.disc("glow", 82, 90, 42)
    birds(d, [(136, 46, 1), (150, 56, 0.8)])
    d.band("far", hills(150, 8))
    acacia(d, 80, 16, 0.55)
    d.shape("near", "M52 200 L58 150 Q62 128 82 124 L156 120 Q176 122 182 142 L190 200Z")
    d.stroke("deep", "M70 144 L84 140 M150 134 L166 140 M120 150 L136 152", 2, line=False)
    group(d, "translate(116 123) scale(1.14) translate(-116 -123)", lambda: lion(d))
    d.band("ground", hills(176, 5))
    grass(d, 10, 70, 178, 14, "mid")
    d.band("deep", hills(190, 4, 30), line=False)


BINO_L = "M52 98 C52 86 60 78 72 78 L86 78 L90 150 C90 160 82 166 70 166 C58 166 50 160 50 150Z"


def gamedrive_binoculars(d: Drawing):
    d.disc("glow", 140, 58, 26)
    birds(d, [(40, 48, 1), (56, 40, 0.8)])
    d.band("far", hills(108, 10))
    acacia(d, -42, -18, 0.55)
    group(d, "translate(18 66) scale(.18)", lambda: d.shape("dark", GIRAFFE))
    d.band("mid", hills(124, 6, 30))
    # strap
    d.stroke("dark", "M60 82 C40 60 30 110 26 200 M140 82 C160 60 170 110 174 200", 3)
    # binoculars
    d.shape("hero", rrect(80, 92, 40, 30, 8))
    d.shape("hero", BINO_L)
    flip(d, lambda: d.shape("hero", BINO_L))
    d.shape("dark", rrect(90, 84, 20, 16, 4))
    d.shape("hero2", rrect(56, 70, 30, 14, 5), spot=True)
    d.shape("hero2", rrect(114, 70, 30, 14, 5), spot=True)
    for cx in (70, 130):
        d.shape("mark", rrect(cx - 19, 112, 38, 8, 3), shadow=False)
        d.shape("dark", circle(cx, 146, 17))
        d.shape("deep", circle(cx, 146, 12), shadow=False)
        d.stroke("light", f"M{cx - 8} {141} A9 9 0 0 1 {cx + 1} {136}", 3)


ZEBRA = ("M44 116 C52 106 86 106 110 108 L122 86 C126 79 133 76 140 78 L152 86 C157 90 157 95 152 97 L141 97 "
         "L132 117 C131 124 128 128 124 130 L124 164 L117 164 L116 136 L111 136 L110 164 L103 164 L102 134 "
         "L70 134 L68 164 L61 164 L60 136 L55 136 L54 164 L47 164 L46 128 C43 124 42 120 44 116Z")
ZEBRA_STRIPES = ("M58 104 L52 140 L58 140 L64 104Z M72 104 L68 140 L74 140 L78 104Z M86 104 L84 140 L90 140 L92 104Z "
                 "M100 104 L100 140 L106 140 L106 104Z M114 100 L112 140 L118 140 L120 100Z "
                 "M118 90 L136 104 L138 99 L122 86Z M124 82 L142 92 L144 87 L128 78Z "
                 "M40 150 H130 V154 H40Z M40 160 H130 V164 H40Z "
                 "M138 74 L136 92 L140 92 L142 74Z M146 78 L145 92 L149 92 L150 80Z")


def zebra(d: Drawing):
    d.stroke("mark", "M45 118 Q36 128 38 142", 2.5)
    d.shape("hero", ZEBRA)
    clipped(d, ZEBRA, lambda: d.marks("mark", ZEBRA_STRIPES))
    d.shape("mark", "M120 86 C124 78 132 74 140 76 L136 72 C128 70 120 76 117 84Z", shadow=False)
    d.shape("hero", "M138 77 L136 66 L142 74Z", shadow=False)
    d.marks("mark", ellipse(153, 92, 4, 4.5))
    d.marks("light", circle(140, 85, 1.8))


def gamedrive_zebra(d: Drawing):
    d.disc("glow", 132, 64, 30)
    d.band("far", hills(132, 10))
    acacia(d, -96, 6, 0.6)
    d.band("mid", hills(150, 6, 40))
    group(d, "translate(114 66) scale(-.6 .6)", lambda: zebra(d))
    group(d, "translate(22 12) scale(.9)", lambda: zebra(d))
    d.band("ground", hills(178, 5))
    d.band("deep", hills(192, 4, 30), line=False)


# ================================================================ BIG CATS
LEOPARD = ("M50 98 C54 88 68 86 80 88 C100 90 124 88 140 92 C150 95 153 104 146 109 C130 113 100 111 80 110 "
           "C66 109 54 106 50 98Z")


def bigcat_leopard(d: Drawing):
    d.disc("glow", 140, 62, 28)
    birds(d, [(40, 50, 1), (56, 42, 0.8)])
    d.band("far", hills(150, 8))
    d.band("mid", hills(166, 6, 30))
    # tree
    d.limb("dark", "M152 200 C150 160 148 134 136 114 M144 130 L178 104", 10)
    d.limb("dark", "M156 114 L14 118", 9)
    d.shape("dark", "M8 124 Q40 104 86 112 Q56 128 8 124Z", shadow=False)
    d.shape("dark", "M150 108 Q178 86 204 92 Q188 108 150 108Z", shadow=False)
    # leopard draped on the branch: one front and one back leg dangling
    d.limb("hero", "M140 100 C158 104 162 126 154 146 C151 154 156 160 162 156", 5.5, spot=True)
    d.limb("hero", "M70 104 Q71 116 69 126", 12)
    d.limb("hero", "M124 104 Q126 114 124 122", 12)
    d.shape("hero", ellipse(68, 130, 7.5, 5.5), shadow=False)
    d.shape("hero", ellipse(123, 126, 7.5, 5.5), shadow=False)
    d.shape("hero", LEOPARD)
    for x in (34, 54):
        d.shape("hero", circle(x, 82, 5), shadow=False)
        d.marks("mark", circle(x, 82, 2.2))
    d.shape("hero", ellipse(44, 96, 17, 14))
    d.shape("light", ellipse(40, 104, 8, 5), shadow=False)
    d.marks("mark", circle(37, 94, 2) + circle(49, 94, 2) + "M39 100 L45 100 L42 104Z")
    spots = [(62, 94), (74, 92), (88, 94), (102, 93), (116, 92), (130, 95), (68, 102), (82, 101), (96, 102),
             (110, 101), (124, 102), (139, 101), (152, 118), (156, 134), (69, 116), (125, 114), (40, 86), (48, 86)]
    d.marks("mark", "".join(circle(x, y, 2.5) for x, y in spots))


TIGER_HEAD = ("M100 46 C130 46 150 58 156 80 C164 92 166 108 160 122 C152 144 128 160 100 160 "
              "C72 160 48 144 40 122 C34 108 36 92 44 80 C50 58 70 46 100 46Z")


def bigcat_tiger(d: Drawing):
    for x, y, a in [(10, 110, -40), (190, 106, -140), (6, 70, -10), (194, 66, -170)]:
        d.shape("mid", leaf(x, y, 62, 14, a), line=False)
    for x, y, a in [(16, 160, -60), (32, 176, -40), (184, 160, -120), (168, 176, -140), (100, 210, -90)]:
        d.shape("near", leaf(x, y, 64, 15, a), line=False)
    for cx in (52, 148):
        d.shape("hero", circle(cx, 56, 16))
        d.shape("light", circle(cx, 58, 8), shadow=False)
    d.shape("hero", TIGER_HEAD)
    stripes = ("M100 50 L95 70 L100 66 L105 70Z M84 52 L82 66 L88 58Z M116 52 L118 66 L112 58Z "
               "M42 96 L64 102 L42 106Z M40 116 L62 116 L44 124Z M158 96 L136 102 L158 106Z M160 116 L138 116 L156 124Z "
               "M72 140 L80 128 L82 144Z M128 140 L120 128 L118 144Z")
    d.marks("mark", stripes)
    d.shape("light", "M100 104 C112 104 132 110 134 126 C134 140 116 150 100 150 C84 150 66 140 66 126 C68 110 88 104 100 104Z", shadow=False)
    d.shape("light", ellipse(78, 86, 12, 7), shadow=False)
    d.shape("light", ellipse(122, 86, 12, 7), shadow=False)
    d.shape("hero2", ellipse(78, 90, 7, 6), shadow=False, spot=True)
    d.shape("hero2", ellipse(122, 90, 7, 6), shadow=False, spot=True)
    d.marks("mark", ellipse(78, 90, 2, 5) + ellipse(122, 90, 2, 5))
    d.shape("pop", "M90 112 H110 L100 124Z", shadow=False)
    d.stroke("mark", "M100 124 V130 M100 130 Q92 138 86 132 M100 130 Q108 138 114 132", 2)
    d.marks("mark", circle(86, 122, 1.3) + circle(80, 126, 1.3) + circle(114, 122, 1.3) + circle(120, 126, 1.3))


CHEETAH = ("M40 76 C42 69 52 66 58 70 C62 74 66 80 72 82 C96 78 124 80 142 84 C152 86 156 94 152 102 "
           "C150 108 146 110 144 112 L147 140 L141 140 L137 119 L134 140 L128 140 L127 112 C116 105 100 105 88 110 "
           "C84 112 80 114 78 114 L76 140 L70 140 L68 117 L65 140 L59 140 L60 106 C58 98 56 92 52 88 L44 86 "
           "C40 84 38 80 40 76Z")


def bigcat_cheetah(d: Drawing):
    d.disc("glow", 64, 74, 32)
    d.band("far", hills(132, 8))
    acacia(d, 22, -2, 0.62)
    d.band("mid", hills(150, 5, 30))

    def cat():
        d.limb("hero", "M150 92 C164 100 168 120 160 134 C156 140 160 146 166 142", 4.5, spot=True)
        d.stroke("mark", "M162 128 L168 131 M160 136 L165 141", 2.2)
        d.shape("hero", circle(51, 67, 3.6), shadow=False)
        d.shape("hero", circle(58, 70, 3.2), shadow=False)
        d.shape("hero", CHEETAH)
        spots = [(76, 88), (86, 86), (96, 86), (106, 86), (116, 86), (126, 87), (136, 89), (146, 92), (80, 96),
                 (92, 94), (102, 95), (112, 94), (122, 96), (134, 97), (144, 101), (70, 100), (98, 102), (116, 101),
                 (62, 110), (64, 122), (74, 120), (132, 118), (140, 124), (138, 108), (64, 90)]
        clipped(d, CHEETAH, lambda: d.marks("mark", "".join(circle(x, y, 1.9) for x, y in spots)))
        d.shape("light", ellipse(43, 81, 5, 3.4), shadow=False)
        d.marks("mark", circle(47, 75, 1.7) + "M38.5 79 L42 78.5 L40.5 81.5Z")
        d.stroke("mark", "M46.5 77 Q46 82 43 85", 1.6)
    group(d, "translate(100 157) scale(1.12) translate(-100 -140)", cat)
    d.band("ground", hills(160, 4))
    grass(d, 120, 200, 162, 12, "near")
    d.band("deep", hills(186, 4, 30), line=False)


# ================================================================ ELEPHANT SANCTUARY
BABY_ELE = ("M50 128 C48 104 64 92 88 92 C100 92 110 96 116 104 C120 92 134 86 146 92 C156 98 158 110 152 120 "
            "L150 140 L138 140 L136 128 L124 130 L122 150 L108 150 L106 132 L80 132 L78 150 L64 150 L62 132 "
            "L52 136 C50 134 50 130 50 128Z")
BABY_EAR = "M118 98 C110 104 110 120 118 128 C126 132 134 126 135 116 C136 104 128 96 118 98Z"


def drop(x, y, r):
    return f"M{x:.1f} {y - r * 1.7:.1f} Q{x + r:.1f} {y:.1f} {x:.1f} {y + r:.1f} Q{x - r:.1f} {y:.1f} {x:.1f} {y - r * 1.7:.1f}Z"


def elephant_bath(d: Drawing):
    d.disc("glow", 40, 60, 18)
    d.band("far", hills(124, 8))

    def calf():
        d.limb("hero", "M146 104 C162 98 166 76 158 60 C154 54 150 54 148 60", 11)
        d.stroke("hero", "M50 118 Q42 124 44 134", 2.5)
        d.shape("hero", BABY_ELE)
        d.shape("hero2", BABY_EAR, shadow=False)
        d.marks("mark", circle(144, 102, 2.2))
    group(d, "translate(96 152) scale(1.15) translate(-100 -140)", calf)
    # a fountain of water from the raised trunk, landing on the back
    for path in ["M150 50 Q132 14 104 74", "M150 50 Q120 22 82 86", "M150 50 Q142 10 122 66"]:
        d.stroke("pop", path, 3)
    for x, y, r in [(104, 80, 3.6), (82, 92, 3.6), (122, 72, 3.4), (96, 70, 2.6), (74, 80, 2.6), (114, 62, 2.4),
                    (134, 26, 2.6), (118, 30, 2.4), (144, 22, 2.2)]:
        d.shape("pop", drop(x, y, r), shadow=False, spot=True)
    d.band("mid", waves(150, 4, 24))
    d.stroke("light", "M64 148 q8 -6 16 0 M112 147 q8 -6 16 0", 2.4)
    d.band("near", waves(164, 4, 30))
    d.stroke("light", "M30 160 q6 -4 12 0 M140 174 q6 -4 12 0 M70 180 q6 -4 12 0", 2)
    d.band("deep", waves(184, 4, 36), line=False)


ELEPHANT = ("M46 120 C46 96 66 84 92 84 C108 84 120 88 128 96 C134 86 150 84 160 92 C168 99 168 112 162 120 "
            "C160 132 161 148 166 160 C168 166 163 171 158 166 C151 154 149 140 148 130 L144 132 L144 172 "
            "L132 172 L131 148 L118 148 L117 172 L105 172 L104 148 L80 146 L79 172 L67 172 L66 146 L58 145 "
            "L57 172 L45 172 L46 140 C44 134 44 126 46 120Z")
HEART = "M0 -6 C-3 -13 -14 -12 -13 -3 C-12 4 -4 8 0 14 C4 8 12 4 13 -3 C14 -12 3 -13 0 -6Z"


def elephant_family(d: Drawing):
    d.disc("glow", 100, 98, 56)
    d.band("far", hills(150, 8))

    def mum():
        d.stroke("hero", "M46 122 Q37 130 40 142", 2.5)
        d.shape("hero", ELEPHANT)
        d.shape("hero2", "M128 98 C120 104 118 122 126 132 C134 136 142 130 143 120 C144 108 138 98 128 98Z", shadow=False, spot=True)
        d.marks("mark", circle(152, 103, 2.2))
    group(d, "translate(-16 32) scale(.8)", mum)

    def calf():
        d.stroke("hero", "M50 118 Q42 124 44 134", 2.5)
        d.limb("hero", "M150 112 C156 124 158 134 166 136", 8)
        d.shape("hero", BABY_ELE)
        d.shape("hero2", BABY_EAR, shadow=False)
        d.marks("mark", circle(144, 102, 2.2))
    group(d, "translate(212 80) scale(-.6 .6)", calf)
    group(d, "translate(136 104)", lambda: d.shape("pop", HEART, spot=True))
    d.band("ground", hills(176, 4))
    d.band("deep", hills(190, 4, 20), line=False)


BANANA = "M-6 0 C-11 -14 -5 -32 9 -38 C12 -39 13 -36 11 -34 C2 -26 0 -12 6 0Z"
EAR = "M72 70 C40 50 14 70 18 104 C22 132 46 140 64 132 C72 120 76 96 72 70Z"


def elephant_bananas(d: Drawing):
    for x, y, a in [(14, 52, -20), (4, 94, 10), (186, 52, -160), (196, 94, 170), (20, 156, -30), (180, 156, -150)]:
        d.shape("near", leaf(x, y, 56, 14, a), line=False)
    d.shape("hero2", EAR, spot=True)
    flip(d, lambda: d.shape("hero2", EAR, spot=True))
    # head and trunk, curling up at the tip to hold the bananas
    d.shape("hero", "M100 40 C126 40 140 58 138 84 C136 102 124 112 114 118 L112 150 C112 162 118 166 126 164 "
                    "C134 162 138 154 136 146 L146 148 C150 164 138 178 122 178 C104 178 96 166 96 150 L94 118 "
                    "C80 112 64 102 62 84 C60 58 74 40 100 40Z")
    d.marks("mark", circle(84, 80, 3) + circle(116, 80, 3))
    d.stroke("mark", "M96 128 H108 M96 138 H110 M98 148 H110", 1.6)
    d.stroke("mark", "M92 58 Q100 54 108 58", 1.6, line=False)
    for a in [-36, -6, 24]:
        group(d, f"translate(142 150) rotate({a})", lambda: (d.shape("pop", BANANA, spot=True), d.marks("dark", circle(10.5, -36.5, 2))))
    d.shape("dark", rrect(136, 146, 12, 9, 3), shadow=False)


# ================================================================ GORILLA TREKKING
SILVERBACK = ("M60 80 C68 66 88 60 106 66 C126 72 144 84 156 98 C166 110 168 128 162 142 L164 162 L147 162 "
              "L145 148 L139 142 C135 150 133 156 135 162 L118 162 L120 140 C108 134 98 128 90 124 L93 158 "
              "C94 162 90 164 86 164 L72 164 L70 128 L67 126 L68 158 C68 162 66 164 62 164 L48 164 L48 118 "
              "C46 104 52 90 60 80Z")
SB_HEAD = "M30 88 C28 74 40 62 54 64 C66 66 72 78 68 92 C66 104 56 112 44 110 C34 108 30 98 30 88Z"


def mist(d: Drawing, y, amp=3, step=40, opacity=".55"):
    d.raw(f'<g opacity="{opacity}">', "")
    d.band("light", waves(y, amp, step), shadow=False, line=False)
    d.raw("</g>", "")


def gorilla_silverback(d: Drawing):
    d.band("far", hills(108, 12))
    mist(d, 122, 6, 40)
    d.band("mid", hills(140, 8, -20))
    for x, y, a in [(164, 200, -100), (178, 196, -70), (190, 186, -120), (10, 196, -60), (24, 200, -100)]:
        d.shape("near", leaf(x, y, 70, 14, a), line=False)
    d.shape("hero", SILVERBACK)
    d.shape("hero2", "M84 70 C104 66 128 76 146 92 C138 102 118 106 102 102 C90 98 84 86 84 70Z", shadow=False, spot=True)
    d.shape("hero", SB_HEAD)
    d.shape("hero", "M40 66 Q50 52 62 66Z", shadow=False)
    d.shape("mark", "M32 90 C32 82 38 78 46 80 C52 82 56 88 54 96 C52 104 42 106 36 102 C33 99 32 95 32 90Z", shadow=False)
    d.stroke("hero", "M32 82 Q42 76 56 80", 3.4, line=False)
    d.marks("light", circle(44, 86, 1.5))
    d.marks("dark", circle(36, 95, 1.2) + circle(40, 96, 1.2))
    for x, y, a in [(60, 202, -80), (80, 202, -100), (100, 202, -70), (120, 202, -110), (140, 202, -90), (40, 202, -110)]:
        d.shape("deep", leaf(x, y, 40, 10, a), line=False)


GORILLA_HEAD = ("M100 34 C128 34 146 52 148 78 C162 82 166 104 154 112 C152 140 132 166 100 166 "
                "C68 166 48 140 46 112 C34 104 38 82 52 78 C54 52 72 34 100 34Z")


def gorilla_face(d: Drawing):
    for x, y, a in [(-6, 40, 20), (-4, 90, 0), (0, 150, -20), (206, 40, 160), (204, 90, 180), (200, 150, -160),
                    (40, 206, -80), (160, 206, -100)]:
        d.shape("near", leaf(x, y, 64, 16, a), line=False)
    d.shape("hero", GORILLA_HEAD)
    d.shape("hero2", "M100 72 C118 70 136 78 138 96 C140 116 132 132 120 144 C112 152 88 152 80 144 "
                     "C68 132 60 116 62 96 C64 78 82 70 100 72Z", shadow=False, spot=True)
    d.shape("hero", "M62 90 C70 76 90 78 100 86 C110 78 130 76 138 90 C128 88 112 90 100 96 C88 90 72 88 62 90Z", shadow=False)
    d.marks("light", circle(82, 98, 4) + circle(118, 98, 4))
    d.marks("mark", circle(82, 98, 2.3) + circle(118, 98, 2.3))
    d.shape("hero", "M86 116 C88 106 112 106 114 116 C116 124 108 128 100 128 C92 128 84 124 86 116Z", shadow=False)
    d.marks("mark", ellipse(94, 120, 3.5, 2.5) + ellipse(106, 120, 3.5, 2.5))
    d.stroke("mark", "M84 138 Q100 132 116 138", 2.2)


def gorilla_volcano(d: Drawing):
    d.disc("glow", 150, 50, 16)
    d.band("far", "M-30 124 L12 116 L54 70 L72 70 L116 116 L138 102 L156 84 L168 84 L210 118 L230 120")
    d.shape("light", "M54 70 L72 70 L80 79 L72 77 L66 82 L60 77 L47 78Z", shadow=False)
    d.shape("light", "M156 84 L168 84 L175 92 L168 90 L162 94 L156 90 L150 91Z", shadow=False)
    mist(d, 112, 3, 40, ".7")
    d.band("mid", hills(136, 8))
    for x in range(-10, 220, 22):
        d.shape("mid", scallop(x, 134 - (x * 7 % 9), 12, 8, 0.16), shadow=False, line=False)
    d.band("near", hills(158, 6, 30))
    # gorilla sitting, facing us
    d.shape("hero", "M62 176 C58 146 70 124 100 122 C130 124 142 146 138 176Z")
    d.limb("hero", "M72 134 C62 148 62 162 66 174", 15)
    d.limb("hero", "M128 134 C138 148 138 162 134 174", 15)
    d.shape("hero", "M88 92 Q100 70 112 92Z")
    d.shape("hero", "M100 82 C114 82 124 92 124 106 C124 120 112 128 100 128 C88 128 76 120 76 106 C76 92 86 82 100 82Z")
    d.shape("hero2", "M100 98 C110 98 117 104 117 112 C117 120 108 126 100 126 C92 126 83 120 83 112 C83 104 90 98 100 98Z",
            shadow=False, spot=True)
    d.shape("hero", "M82 104 Q92 96 100 102 Q108 96 118 104 Q108 103 100 108 Q92 103 82 104Z", shadow=False)
    d.marks("light", circle(92, 106, 2.2) + circle(108, 106, 2.2))
    d.marks("mark", ellipse(97, 115, 2, 1.5) + ellipse(103, 115, 2, 1.5))
    d.stroke("mark", "M93 121 Q100 118 107 121", 1.5)
    d.band("deep", hills(178, 5))
    for x, y, a in [(6, 196, -60), (22, 200, -90), (172, 200, -100), (188, 196, -120)]:
        d.shape("deep", leaf(x, y, 60, 13, a), line=False)


# ================================================================ SEA CREATURES
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
    """A point on spine p at t, moved `up` (to the left of travel, i.e. the back) and `fwd`."""
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
    """Tail flukes at the start of spine p, seen side-on."""
    x, y, dx, dy = _bez(p, t)
    bx, by = x - dx * length, y - dy * length
    l = (bx + dy * span, by - dx * span)
    r = (bx - dy * span, by + dx * span)
    nx, ny = x - dx * length * 0.55, y - dy * length * 0.55
    return (f"M{x + dx * 3:.1f} {y + dy * 3:.1f} Q{x + dy * span * 0.4:.1f} {y - dx * span * 0.4:.1f} {l[0]:.1f} {l[1]:.1f} "
            f"Q{nx + dy * 2:.1f} {ny - dx * 2:.1f} {nx:.1f} {ny:.1f} Q{nx - dy * 2:.1f} {ny + dx * 2:.1f} {r[0]:.1f} {r[1]:.1f} "
            f"Q{x - dy * span * 0.4:.1f} {y + dx * span * 0.4:.1f} {x + dx * 3:.1f} {y + dy * 3:.1f}Z")


def fin(p, t, h, sweep, base=10, side=1):
    """A curved fin on spine p at t: side 1 = back (dorsal), -1 = belly."""
    x, y, dx, dy = _bez(p, t)
    nx, ny = dy * side, -dx * side
    f = (x + dx * base * 0.5, y + dy * base * 0.5)
    b = (x - dx * base * 0.5, y - dy * base * 0.5)
    tip = (x + nx * h - dx * sweep, y + ny * h - dy * sweep)
    c = (f[0] + nx * h * 0.8, f[1] + ny * h * 0.8)
    return (f"M{f[0] - nx * 3:.1f} {f[1] - ny * 3:.1f} Q{c[0]:.1f} {c[1]:.1f} {tip[0]:.1f} {tip[1]:.1f} "
            f"Q{b[0] + nx * h * 0.2:.1f} {b[1] + ny * h * 0.2:.1f} {b[0] - nx * 3:.1f} {b[1] - ny * 3:.1f}Z")


def sea(d: Drawing, y=110, sky_line=True):
    d.band("far", waves(y, 3, 30))
    d.band("mid", waves(y + 22, 4, 34))
    d.band("near", waves(y + 46, 4, 38))
    d.band("deep", waves(y + 70, 4, 42), line=False)


def splash(d: Drawing, x, y, w=24, role="light"):
    d.stroke(role, f"M{x - w} {y} q{w * 0.25} {-w * 0.3} {w * 0.5} 0 M{x + w * 0.5} {y} q{w * 0.25} {-w * 0.3} {w * 0.5} 0", 2.4)
    for dx, dy, r in [(-w * 0.7, -10, 2.6), (-w * 0.3, -16, 2.2), (w * 0.3, -15, 2.4), (w * 0.7, -9, 2.2), (0, -20, 2)]:
        d.shape(role, drop(x + dx, y + dy, r), shadow=False)


# ---------------------------------------------------------------- whales
FLUKE = ("M88 156 C90 130 92 112 95 100 C78 96 54 84 38 62 C34 56 40 53 46 57 C64 70 84 74 100 80 "
         "C116 74 136 70 154 57 C160 53 166 56 162 62 C146 84 122 96 105 100 C108 112 110 130 112 156Z")


def whale_tail(d: Drawing):
    d.disc("glow", 150, 52, 18)
    d.band("far", "M-30 112 L10 96 L34 104 L60 86 L84 104 L230 108", line=False)
    d.shape("light", cloud(18, 50, 1.0), shadow=False)
    d.band("mid", waves(112, 3, 30))
    d.shape("hero", FLUKE)
    d.shape("hero2", "M48 62 C62 72 80 78 96 84 L94 90 C76 86 58 76 48 62Z M152 62 C138 72 120 78 104 84 L106 90 C124 86 142 76 152 62Z",
            shadow=False, spot=True)
    d.marks("mark", circle(70, 78, 1.6) + circle(128, 79, 1.4) + circle(62, 72, 1.2))
    for x, y, r in [(46, 74, 2.6), (52, 90, 2.2), (152, 74, 2.6), (148, 92, 2.2), (60, 104, 2), (140, 106, 2)]:
        d.shape("light", drop(x, y, r), shadow=False)
    d.band("near", waves(140, 4, 34))
    d.stroke("light", "M66 140 q8 -6 16 0 M118 140 q8 -6 16 0 M54 150 q6 -4 12 0 M134 150 q6 -4 12 0", 2.4)
    d.band("deep", waves(168, 4, 38), line=False)


def whale_boat(d: Drawing):
    d.disc("glow", 160, 50, 16)
    d.shape("light", cloud(24, 44, 1.0), shadow=False)
    d.band("far", "M-30 104 L20 88 L44 96 L80 80 L110 100 L230 100", line=False)
    d.band("mid", waves(106, 3, 30))
    group(d, "translate(2 22) scale(.68)", lambda: (
        d.stroke("dark", "M56 82 V110", 2.4),
        d.shape("pop", "M57 82 L72 87 L57 92Z", shadow=False, spot=True),
        d.shape("light", rrect(36, 104, 40, 22, 4)),
        d.shape("sky2", rrect(42, 108, 9, 7, 2), shadow=False),
        d.shape("sky2", rrect(55, 108, 9, 7, 2), shadow=False),
        d.marks("dark", circle(84, 116, 4) + circle(94, 116, 4) + "M80 124 a4 5 0 0 1 8 0Z M90 124 a4 5 0 0 1 8 0Z"),
        d.shape("hero2", "M18 124 H112 C110 140 100 150 86 150 H36 C26 146 20 136 18 124Z", spot=True),
        d.shape("light", "M22 132 H110 V136 H22Z", shadow=False),
    ))
    d.band("near", waves(124, 3, 32), line=False)
    # spout from the blowhole, then the whale's broad back
    d.shape("light", "M114 124 C108 98 90 80 72 76 C92 72 108 84 113 98 C114 76 124 58 142 50 C130 70 122 94 121 124Z", spot=True)
    for x, y, r in [(70, 88, 3), (82, 70, 2.6), (142, 64, 2.6), (150, 82, 3), (104, 60, 2.2), (124, 44, 2.2)]:
        d.shape("light", drop(x, y, r), shadow=False)
    d.shape("hero", "M84 152 C96 124 140 112 180 118 C200 122 212 134 218 152Z")
    d.shape("hero", "M156 118 L170 102 L174 120Z", shadow=False)
    d.shape("mark", ellipse(116, 126, 3, 1.6), shadow=False)
    d.band("deep", waves(146, 4, 36))
    d.stroke("light", "M30 160 q8 -6 16 0 M140 166 q8 -6 16 0 M86 172 q6 -4 12 0", 2.2)


def whale_humpback(d: Drawing):
    d.band("sky2", waves(40, 5, 26))
    d.band("far", waves(64, 5, 28))
    d.band("mid", waves(90, 6, 30))
    d.raw('<g opacity=".18" fill="#fff"><path d="M40 0 L62 0 L100 200 L78 200Z"/><path d="M120 0 L132 0 L172 200 L160 200Z"/></g>', "")
    d.band("near", waves(150, 6, 34))
    p = ((30, 100), (62, 80), (118, 76), (168, 100))
    prof = lambda t: (3 + 16 * math.sin(math.pi * (t * 0.8) ** 1.25), 3 + 20 * math.sin(math.pi * (t * 0.8) ** 1.25))
    d.shape("hero", flukes(p, 18, 15))
    d.shape("hero", fin(p, 0.42, 6, 6, 10))
    d.shape("hero2", leaf(120, 108, 58, 9, 128), spot=True)
    d.shape("hero", spine(p, prof))
    d.shape("hero2", spine(p, lambda t: (-4 - 5 * t, prof(t)[1] - 1.5), t0=0.55, t1=1.0), shadow=False)
    for k in range(3):
        a = frame(p, 0.62, -9 - 4 * k)
        b = frame(p, 0.98, -6 - 4 * k)
        d.stroke("hero", f"M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f}", 1.5)
    e = frame(p, 0.86, 0)
    d.marks("light", circle(e[0], e[1], 2.4))
    d.marks("mark", circle(e[0], e[1], 1.3))
    for t, u in [(0.92, 9), (0.96, 5), (0.88, 13), (0.97, 11)]:
        q = frame(p, t, u)
        d.marks("mark", circle(q[0], q[1], 1.4))
    for x, y, s in [(44, 136, 0.8), (58, 144, 0.7), (150, 46, 0.8), (164, 54, 0.7)]:
        d.shape("pop", fish(x, y, s, right=True), shadow=False)
    d.band("deep", waves(174, 5, 36), line=False)
    for x, y, r in [(176, 76, 2.5), (182, 64, 3.5), (176, 52, 2.5)]:
        d.stroke("light", circle(x, y, r), 2)


# ---------------------------------------------------------------- dolphins
def dolphin(d: Drawing, p, s=1.0, body="hero", belly="hero2", spot=False):
    prof = lambda t: (s * (2 + 12 * math.sin(math.pi * t ** 1.5)), s * (2 + 10 * math.sin(math.pi * t ** 1.5)))
    d.shape(body, flukes(p, 12 * s, 10 * s))
    d.shape(body, fin(p, 0.55, 13 * s, 9 * s, 12 * s))
    d.shape(body, fin(p, 0.72, 9 * s, 7 * s, 6 * s, side=-1), shadow=False)
    d.shape(body, spine(p, prof), spot=spot)
    d.shape(belly, spine(p, lambda t: (-1.5 * s, prof(t)[1] - 1.2 * s), t0=0.35, t1=0.96), shadow=False)
    e = frame(p, 0.86, 3 * s)
    d.marks("mark", circle(e[0], e[1], 1.7 * s))


def dolphin_leap(d: Drawing):
    d.disc("glow", 100, 112, 52)
    d.shape("light", cloud(14, 60, 1.0), shadow=False)
    d.shape("light", cloud(150, 44, 0.8), shadow=False)
    d.band("mid", waves(130, 4, 30))
    dolphin(d, ((50, 134), (52, 80), (112, 44), (164, 84)), 1.35)
    splash(d, 46, 132, 22)
    d.band("near", waves(148, 4, 34))
    d.stroke("light", "M120 146 q8 -6 16 0 M30 160 q6 -4 12 0 M150 160 q6 -4 12 0", 2.4)
    d.band("deep", waves(172, 4, 38), line=False)


def dolphin_pod(d: Drawing):
    d.disc("glow", 100, 108, 34)
    for y, w in [(100, 1.2), (110, 1.0)]:
        pass
    d.band("far", waves(112, 2, 30))
    birds(d, [(40, 48, 1), (54, 40, 0.8), (150, 44, 0.9)])
    dolphin(d, ((24, 124), (24, 96), (56, 82), (78, 100)), 0.78)
    dolphin(d, ((70, 122), (70, 84), (114, 62), (142, 92)), 1.0)
    dolphin(d, ((134, 128), (134, 102), (162, 90), (182, 106)), 0.7)
    d.band("mid", waves(124, 3, 30))
    d.band("near", waves(146, 4, 34))
    d.stroke("light", "M64 140 q8 -6 16 0 M128 140 q8 -6 16 0 M20 160 q6 -4 12 0 M160 162 q6 -4 12 0", 2.2)
    d.band("deep", waves(170, 4, 38), line=False)


def dolphin_bow(d: Drawing):
    d.disc("glow", 152, 50, 18)
    d.shape("light", cloud(96, 40, 0.9), shadow=False)
    d.band("far", waves(100, 2, 30))
    d.band("mid", waves(118, 3, 30))
    dolphin(d, ((84, 142), (88, 96), (130, 72), (168, 96)), 1.15, spot=True)
    splash(d, 84, 140, 18)
    d.band("near", waves(142, 4, 34))
    # the bow of the tour boat, cutting in from the left
    d.stroke("dark", "M-30 78 L60 86 M0 79 V90 M20 81 V92 M40 83 V94 M58 86 V96", 2.2)
    d.shape("pop", "M-30 88 L70 96 C62 114 50 132 30 150 L-30 150Z", spot=True)
    d.shape("light", "M-30 100 L64 106 L60 112 L-30 106Z", shadow=False)
    d.marks("dark", circle(20, 126, 3.5))
    d.stroke("light", "M48 148 q10 -6 20 2 M34 160 q10 -6 20 2", 2.4)
    d.band("deep", waves(170, 4, 38), line=False)


# ---------------------------------------------------------------- penguins
PENGUIN = "M83 100 C70 74 72 34 88 14 C94 6 108 3 115 12 C120 18 121 28 117 38 C127 54 128 82 119 100Z"
PENGUIN_BELLY = "M107 38 C119 52 122 80 114 98 L91 98 C94 78 96 54 107 38Z"


def penguin(d: Drawing, x, y, s=1.0, flipx=False, crest=False, patch=True):
    """A penguin standing with its feet at (x, y), facing right (drawn around (100, 100) so shadows aren't clipped)."""
    def draw():
        d.shape("dark", "M86 50 C76 64 74 80 78 92 C86 78 90 64 90 50Z", shadow=False)
        d.shape("pop", ellipse(94, 100, 7, 3) + ellipse(109, 100, 7, 3), shadow=False)
        d.shape("dark", PENGUIN)
        d.shape("light", PENGUIN_BELLY, shadow=False)
        if patch:
            d.shape("hero2", "M108 26 C114 30 116 36 114 42 C110 38 106 34 106 28Z", shadow=False, spot=True)
        d.shape("pop", "M115 16 L132 21 L115 23Z", shadow=False, spot=not patch)
        if crest:
            d.stroke("hero2", "M110 12 Q120 8 126 2 M108 12 Q118 10 124 8", 2)
        d.marks("light", circle(109, 16, 2))
        d.shape("dark", "M92 50 C98 62 98 80 92 92 C88 80 88 62 92 50Z", shadow=False)
    sx = -s if flipx else s
    group(d, f"translate({x} {y}) scale({sx} {s}) translate(-100 -100)", draw)


def penguin_emperor(d: Drawing):
    d.disc("glow", 52, 64, 20)
    d.band("far", "M-30 120 L20 120 L30 96 L48 90 L58 110 L230 116", line=True)
    d.shape("far", "M120 118 L132 80 L150 74 L164 92 L170 118Z")
    d.shape("mid", "M150 74 L164 92 L170 118 L152 118 L158 96Z", shadow=False, line=False)
    d.band("mid", hills(140, 6))
    d.band("light", hills(150, 6, 30))
    penguin(d, 86, 160, 1.2)
    # chick
    d.shape("pop", ellipse(130, 160, 5, 2.5) + ellipse(140, 160, 5, 2.5), shadow=False)
    d.shape("hero2", "M120 158 C114 140 118 124 128 120 C136 118 146 122 148 134 C150 146 148 154 146 158Z")
    d.shape("dark", circle(134, 114, 11))
    d.shape("light", ellipse(137, 116, 6, 5), shadow=False)
    d.marks("dark", circle(138, 114, 1.6))
    d.shape("dark", "M144 112 L150 115 L143 117Z", shadow=False)
    d.band("light", hills(166, 3, 60), shadow=True)
    d.band("far", hills(186, 3, 20), line=False)


def penguin_floe(d: Drawing):
    d.disc("glow", 150, 50, 16)
    d.shape("light", "M10 108 L26 66 L44 58 L60 82 L74 108Z")
    d.shape("far", "M44 58 L60 82 L74 108 L56 108 L58 84Z", shadow=False, line=False)
    sea(d, 106)
    d.shape("light", "M44 146 C40 136 54 128 100 128 C150 128 164 136 160 146 C156 154 140 158 100 158 C60 158 48 154 44 146Z")
    d.shape("far", "M46 148 C60 156 140 156 158 148 C156 154 140 158 100 158 C60 158 48 154 46 148Z", shadow=False, line=False)
    penguin(d, 72, 138, 0.62, flipx=True, crest=True, patch=False)
    penguin(d, 100, 140, 0.74, crest=True, patch=False)
    penguin(d, 128, 136, 0.58, crest=True, patch=False)
    d.stroke("light", "M20 166 q8 -6 16 0 M164 170 q8 -6 16 0", 2.4)


def penguin_swim(d: Drawing):
    d.band("sky2", waves(40, 5, 26))
    d.band("far", waves(64, 5, 28))
    d.band("mid", waves(96, 6, 30))
    d.band("near", waves(128, 6, 34))
    d.band("deep", waves(156, 5, 36), line=False)
    d.band("ground", "M-30 176 Q40 164 80 174 T160 170 T230 172")
    p = ((40, 128), (70, 116), (120, 88), (160, 70))
    prof = lambda t: (2 + 16 * math.sin(math.pi * (0.15 + 0.8 * t)), 2 + 16 * math.sin(math.pi * (0.15 + 0.8 * t)))
    d.shape("pop", flukes(p, 9, 8))
    d.shape("dark", spine(p, prof))
    d.shape("light", spine(p, lambda t: (-3, prof(t)[1] - 1.5), t0=0.08, t1=0.82), shadow=False)
    d.shape("dark", "M96 92 C88 112 80 120 66 126 C78 112 84 102 88 90Z")
    e = frame(p, 0.86, 5)
    d.marks("light", circle(e[0], e[1], 2.2))
    tip = frame(p, 1.0, 0, 13)
    a, b = frame(p, 0.96, 4), frame(p, 0.96, -4)
    d.shape("pop", f"M{a[0]:.1f} {a[1]:.1f} L{tip[0]:.1f} {tip[1]:.1f} L{b[0]:.1f} {b[1]:.1f}Z", shadow=False, spot=True)
    bubbles_ = [(30, 140, 3), (22, 128, 4), (30, 116, 2.5), (40, 148, 2)]
    for x, y, r in bubbles_:
        d.stroke("light", circle(x, y, r), 2)
    for x, y, s in [(150, 130, 0.8), (164, 138, 0.7), (140, 146, 0.7)]:
        d.shape("hero2", fish(x, y, s), shadow=False)


# ---------------------------------------------------------------- crocodiles
def croc_eyes(d: Drawing):
    d.disc("glow", 150, 56, 22)
    d.band("far", hills(104, 8))
    for x in (20, 30, 172, 182):
        d.stroke("near", f"M{x} 120 Q{x - 2} 90 {x + 4} {70 + (x % 4) * 4}", 3)
    d.shape("near", ellipse(24, 76, 3, 9), shadow=False)
    d.shape("near", ellipse(178, 70, 3, 9), shadow=False)
    d.band("mid", waves(110, 2, 34))
    head = ("M30 132 C34 124 44 122 56 122 C76 120 92 118 104 116 C108 104 118 98 128 100 C134 101 138 106 140 112 "
            "C150 110 160 112 168 118 L176 132Z")
    d.shape("hero", head)
    d.shape("hero", "M40 124 C40 118 46 116 50 120Z", shadow=False)
    d.shape("hero2", ellipse(126, 108, 6.5, 5), shadow=False, spot=True)
    d.marks("mark", ellipse(127, 108, 1.4, 4))
    d.stroke("mark", "M46 120 L46 120", 3)
    d.marks("mark", "M146 116 L150 108 L154 116Z M158 118 L162 110 L166 118Z")
    d.band("near", waves(130, 3, 30))
    d.stroke("light", "M40 140 q10 -6 20 0 M110 140 q10 -6 20 0 M150 152 q8 -5 16 0 M70 154 q8 -5 16 0", 2.2)
    d.shape("hero2", "M150 166 a12 6 0 1 0 1 -10 L156 160Z", line=False)
    d.band("deep", waves(170, 3, 38), line=False)


CROC_SIDE = ("M6 150 C30 152 56 146 76 140 C96 136 112 136 126 136 L134 128 C142 122 152 118 160 114 L184 88 "
             "C188 85 192 89 189 93 L166 124 C176 126 186 128 192 130 C196 132 195 137 190 137 L150 140 "
             "C142 148 130 152 118 152 L80 154 C56 156 30 156 6 150Z")


def croc_jaws(d: Drawing):
    d.disc("glow", 60, 70, 30)
    d.band("far", hills(118, 8))
    for x in (140, 152, 164):
        d.stroke("near", f"M{x} 140 Q{x + 2} 110 {x - 4} {86 + (x % 5) * 3}", 3, line=False)
    d.band("mid", waves(134, 3, 30))
    d.band("ground", "M-30 156 Q60 140 120 148 T230 150")
    def croc():
        d.limb("hero", "M70 148 L62 160 L54 162", 7)
        d.limb("hero", "M122 148 L130 160 L140 161", 7)
        d.shape("pop", "M140 128 L184 92 L170 122 L188 132 L150 136Z", shadow=False)
        d.shape("hero", CROC_SIDE)
        d.shape("light", "M166 110 l4 4 l1 -6 l4 3 l1 -6 l4 3 l1 -6Z M164 128 l3 -6 l2 6 l3 -6 l2 6 l3 -6 l2 6Z", shadow=False)
        d.shape("hero2", "M30 152 C60 152 100 148 120 148 L150 140 C142 148 130 152 118 152 L80 154 C60 155 40 155 30 152Z", shadow=False)
        d.shape("hero", ellipse(140, 120, 8, 6), shadow=False)
        d.shape("hero2", ellipse(140, 119, 4.5, 3.5), shadow=False, spot=True)
        d.marks("mark", ellipse(140.5, 119, 1, 3))
        d.marks("mark", "M20 146 l4 -6 l4 6Z M36 145 l4 -7 l4 7Z M52 143 l4 -8 l4 8Z M68 139 l4 -8 l4 8Z M84 136 l4 -8 l4 8Z M100 135 l4 -8 l4 8Z M116 135 l4 -7 l4 7Z")
    group(d, "translate(94 152) scale(.94) translate(-100 -152)", croc)
    d.band("deep", hills(180, 4, 30), line=False)


def croc_sign(d: Drawing):
    birds(d, [(150, 30, 0.9), (166, 38, 0.7)])
    d.band("far", hills(118, 8))
    for x in (150, 162, 174, 22, 34):
        d.stroke("near", f"M{x} 150 Q{x + 2} 118 {x - 4} {92 + (x % 5) * 3}", 3, line=False)
    d.band("mid", waves(132, 3, 30))
    d.band("near", waves(150, 3, 34))
    d.band("ground", "M-30 168 Q60 156 120 162 T230 164")
    d.limb("dark", "M100 166 L100 110", 7)
    d.shape("hero2", rrect(42, 40, 116, 88, 10), spot=True)
    d.stroke("mark", rrect(48, 46, 104, 76, 6), 2.4)
    group(d, "translate(98 86) scale(.56) translate(-100 -130)", lambda: d.marks("mark", CROC_SIDE))
    d.marks("mark", rrect(62, 104, 76, 6, 3) + rrect(74, 113, 52, 5, 2.5))
    d.band("deep", hills(186, 4, 30), line=False)


# ================================================================ colours
LION = {"hero": "#E0A458", "hero2": "#9C5A2B", "mark": "#3B2A20"}
ZEBRA_C = {"hero": "#FBF7EE", "mark": "#24262E"}
LEOPARD_C = {"hero": "#E8B04B", "mark": "#4A2E14", "light": "#FBF1DC"}
TIGER_C = {"hero": "#EC8A33", "hero2": "#F6C64A", "mark": "#2A1E18", "light": "#FFF8EE", "pop": "#D9737B"}
CHEETAH_C = {"hero": "#E8BA62", "mark": "#2D2219", "light": "#FBF1DC"}
ELE_GREY = {"hero": "#8D99AE", "hero2": "#B7C0CE", "mark": "#2B2D42"}
ELE_FEED = {"hero": "#8D99AE", "hero2": "#A9B3C3", "mark": "#2B2D42", "pop": "#F6CF45"}
GORILLA = {"hero": "#34343C", "hero2": "#9A9BA6", "mark": "#16161A", "light": "#F4F0E6"}
GORILLA_SIT = {"hero": "#3A3A42", "hero2": "#6C6C78", "mark": "#16161A", "light": "#E8E2D4"}
GORILLA_FACE = {"hero": "#2E2E35", "hero2": "#56565F", "mark": "#121215", "light": "#C9B9A0"}
WHALE = {"hero": "#3D5A73", "hero2": "#DDE6EE", "mark": "#1E2F3D"}
WHALE_DEEP = {"hero": "#3D5A73", "hero2": "#B9CAD8", "mark": "#1E2F3D"}
DOLPHIN = {"hero": "#6E8FAE", "hero2": "#D5E1EC", "mark": "#1F2F40"}
DOLPHIN_DARK = {"hero": "#3F5F7F", "hero2": "#A9BDD1", "mark": "#16222F"}
PENGUIN_C = {"dark": "#1F2633", "light": "#FFFFFF", "pop": "#F28C28", "hero2": "#F6C445"}
CROC_SIGN = {"hero2": "#F6C445", "mark": "#1F1A14"}
CROC = {"hero": "#5E7A3A", "hero2": "#C8C26A", "mark": "#2E3D1C", "pop": "#E8838F", "light": "#FFFDF4"}

CONCEPTS = [
    # game drive
    Concept("gamedrive-lion-rock", "game-drive", "Lion on the rock", gamedrive_lion, overrides=LION,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero2", "glow"), ("hero", "near"), ("near", "far")],
            fixes={"glow": ["glow2", "light", "far", "#E07A5F"], "near": ["deep", "mid", "dark"]}),
    Concept("gamedrive-binoculars", "game-drive", "Binoculars", gamedrive_binoculars,
            checks=[("hero", "far"), ("hero", "mid"), ("hero", "sky"), ("hero2", "hero"), ("dark", "hero")],
            fixes={"hero": ["deep", "pop", "near", "dark"], "hero2": ["glow2", "light", "pop"]}),
    Concept("gamedrive-zebra", "game-drive", "Zebras", gamedrive_zebra, overrides=ZEBRA_C,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero", "far"), ("hero", "mid")],
            fixes={"glow": ["glow2", "near", "mid", "#E07A5F"], "sky": ["sky2", "far"]}),
    # big cats
    Concept("bigcat-leopard-tree", "big-cat-spotting", "Leopard in a tree", bigcat_leopard, overrides=LEOPARD_C,
            checks=[("hero", "sky"), ("hero", "dark"), ("hero", "glow"), ("hero", "far")],
            fixes={"glow": ["glow2", "#E07A5F", "near"], "sky": ["sky2", "far"]}),
    Concept("bigcat-tiger-face", "big-cat-spotting", "Tiger", bigcat_tiger, overrides=TIGER_C,
            checks=[("hero", "sky"), ("hero", "mid"), ("hero", "near")],
            fixes={"near": ["deep", "dark"], "mid": ["far", "near", "deep"]}),
    Concept("bigcat-cheetah", "big-cat-spotting", "Cheetah lookout", bigcat_cheetah, overrides=CHEETAH_C,
            checks=[("hero", "sky"), ("hero", "glow"), ("hero", "ground"), ("hero", "mid")],
            fixes={"glow": ["glow2", "#E07A5F", "near"], "ground": ["near", "deep", "mid"], "sky": ["sky2", "far"]}),
    # elephant sanctuary
    Concept("elephant-bath", "elephant-sanctuary", "Bath time", elephant_bath, overrides={**ELE_GREY, "pop": "#4FA9D6"},
            checks=[("hero", "sky"), ("hero", "far"), ("pop", "sky"), ("pop", "hero"), ("hero", "mid")],
            fixes={"sky": ["sky2", "far"], "far": ["mid", "near", "ground"], "pop": ["#2C78B8", "#1F5F99", "#BFE6F7"], "mid": ["far", "near"]}),
    Concept("elephant-mum-calf", "elephant-sanctuary", "Mother & calf", elephant_family, overrides=ELE_GREY,
            checks=[("hero", "glow"), ("hero", "sky"), ("pop", "glow")],
            fixes={"glow": ["glow2", "far", "near", "deep"]}),
    Concept("elephant-bananas", "elephant-sanctuary", "Feeding time", elephant_bananas, overrides=ELE_FEED,
            checks=[("hero", "sky"), ("hero2", "sky"), ("hero2", "near"), ("pop", "near")],
            fixes={"sky": ["sky2", "far", "glow"], "near": ["mid", "deep"]}),
    # gorilla trekking
    Concept("gorilla-silverback", "gorilla-trekking", "Silverback", gorilla_silverback, overrides=GORILLA,
            checks=[("hero", "far"), ("hero", "mid"), ("hero2", "hero")],
            fixes={"mid": ["far", "sky2"], "far": ["sky2", "glow"]}),
    Concept("gorilla-face", "gorilla-trekking", "Gorilla face", gorilla_face, overrides=GORILLA_FACE,
            checks=[("hero", "sky"), ("hero", "near")],
            fixes={"near": ["mid", "far"]}),
    Concept("gorilla-volcano", "gorilla-trekking", "Virunga mists", gorilla_volcano, overrides=GORILLA_SIT,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "deep"), ("far", "sky"), ("hero2", "hero")],
            fixes={"near": ["mid", "far", "ground"], "mid": ["far", "glow2"], "deep": ["near", "mid"]}),
    # whale watching
    Concept("whale-tail", "whale-watching", "Whale tail", whale_tail, overrides=WHALE,
            checks=[("hero", "sky"), ("hero", "mid"), ("hero", "glow"), ("hero", "far")],
            fixes={"far": ["mid", "sky2"], "hero": ["#7FA0BD"]}),
    Concept("whale-boat", "whale-watching", "Thar she blows", whale_boat, overrides=WHALE,
            checks=[("hero", "deep"), ("hero", "mid"), ("hero", "near"), ("light", "sky"), ("hero2", "mid")],
            fixes={"deep": ["far", "mid", "sky2"], "hero": ["#7FA0BD"], "sky": ["sky2", "far"], "hero2": ["pop", "glow2", "#E4572E"]}),
    Concept("whale-humpback", "whale-watching", "Humpback", whale_humpback, ["coastal", "dusk", "meadow"], WHALE_DEEP,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "far")]),
    # dolphin watching
    Concept("dolphinwatch-leap", "dolphin-watching", "Leaping dolphin", dolphin_leap, overrides=DOLPHIN,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero", "mid")],
            fixes={"glow": ["glow2", "#E07A5F", "near", "deep"], "sky": ["sky2"]}),
    Concept("dolphinwatch-pod", "dolphin-watching", "Dolphins at sunset", dolphin_pod, overrides=DOLPHIN_DARK,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero", "far")],
            fixes={"glow": ["glow2", "#E07A5F", "light"]}),
    Concept("dolphinwatch-bow", "dolphin-watching", "Bow riding", dolphin_bow, overrides=DOLPHIN,
            checks=[("hero", "sky"), ("hero", "mid"), ("hero", "far"), ("pop", "sky"), ("pop", "near"), ("pop", "mid")],
            fixes={"pop": ["dark", "deep", "#E4572E"], "far": ["mid", "near"], "mid": ["far", "near"]}),
    # penguins
    Concept("penguin-emperor", "penguin-spotting", "Emperor & chick", penguin_emperor, overrides=PENGUIN_C,
            checks=[("dark", "sky"), ("dark", "far"), ("hero2", "light"), ("light", "sky")],
            fixes={"sky": ["sky2", "far", "mid"], "far": ["mid", "near"]}),
    Concept("penguin-floe", "penguin-spotting", "Penguins on the ice", penguin_floe, overrides=PENGUIN_C,
            checks=[("light", "far"), ("light", "mid"), ("dark", "light"), ("light", "sky")],
            fixes={"sky": ["sky2", "far"]}),
    Concept("penguin-swim", "penguin-spotting", "Swimming penguin", penguin_swim, ["coastal", "dusk", "meadow"], PENGUIN_C,
            checks=[("dark", "mid"), ("dark", "near"), ("light", "far")]),
    # crocodiles
    Concept("croc-eyes", "crocodile-spotting", "Eyes above water", croc_eyes, overrides=CROC,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "sky"), ("hero", "far")],
            fixes={"mid": ["far", "sky2"], "near": ["deep", "far"]}),
    Concept("croc-jaws", "crocodile-spotting", "Snap!", croc_jaws, overrides=CROC,
            checks=[("hero", "ground"), ("hero", "mid"), ("hero", "sky"), ("pop", "hero")],
            fixes={"ground": ["near", "far"], "mid": ["far", "sky2"]}),
    Concept("croc-sign", "crocodile-spotting", "Croc warning", croc_sign, overrides=CROC_SIGN,
            checks=[("hero2", "sky"), ("hero2", "far"), ("hero2", "glow"), ("mark", "hero2")],
            fixes={"glow": ["near", "deep", "#E07A5F"], "sky": ["sky2", "far"], "far": ["mid", "near"]}),
]
