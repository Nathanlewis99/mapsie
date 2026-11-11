"""African (and Madagascan) animals: a bold portrait and a habitat scene for twenty safari favourites."""
import math

from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group, acacia  # noqa: F401

_uid = [0]


# ================================================================ helpers (copied from wildlife.py, plus a few new)
def _id(prefix):
    _uid[0] += 1
    return f"{prefix}{_uid[0]}"


def clipped(d: Drawing, path: str, fn):
    """Draw fn() clipped to `path` (stripes on a zebra, rosettes on a leopard)."""
    cid = _id("afclip")
    tag = f'<clipPath id="{cid}"><path d="{path}"/></clipPath><g clip-path="url(#{cid})">'
    d.raw(tag, tag)
    fn()
    d.raw("</g>", "</g>")


def flip(d: Drawing, fn, cx=100):
    group(d, f"translate({2 * cx} 0) scale(-1 1)", fn)


def scallop(cx, cy, r, n=12, bump=0.22, rot=0.0, ry=None):
    """A bumpy circle (or ellipse with ry): manes, tree crowns, bushes."""
    ry = ry or r
    pts = []
    for i in range(n + 1):
        a = rot + 2 * math.pi * i / n
        pts.append((cx + r * math.cos(a), cy + ry * math.sin(a)))
    s = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(n):
        a = rot + 2 * math.pi * (i + 0.5) / n
        qx, qy = cx + r * (1 + bump * 2) * math.cos(a), cy + ry * (1 + bump * 2) * math.sin(a)
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


def mist(d: Drawing, y, amp=3, step=40, opacity=".55"):
    d.raw(f'<g opacity="{opacity}">', "")
    d.band("light", waves(y, amp, step), shadow=False, line=False)
    d.raw("</g>", "")


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


def spots(pts, r=2.2):
    return "".join(circle(x, y, r) for x, y in pts)


def rosette(x, y, r=3.4):
    """A leopard rosette: a broken ring of four blobs."""
    s = ""
    for k in range(4):
        a = math.radians(30 + 90 * k)
        s += ellipse(x + r * math.cos(a), y + r * math.sin(a), r * 0.48, r * 0.48)
    return s


def tri(x, y, w, h):
    """A little upward triangle (teeth, thorns, ears)."""
    return f"M{x - w / 2:.1f} {y:.1f} L{x:.1f} {y - h:.1f} L{x + w / 2:.1f} {y:.1f}Z"


def ripples(d: Drawing, pts, role="light", w=2.2):
    d.stroke(role, " ".join(f"M{x} {y} q{k * 5} {-k * 3.5} {k * 10} 0" for x, y, k in pts), w)


# ================================================================ LION
def lion_face(d: Drawing):
    d.disc("glow", 100, 100, 80, line=False)
    d.band("far", hills(170, 6), line=False)
    d.shape("hero2", scallop(100, 102, 64, 18, 0.12, ry=66), spot=True)
    d.shape("mane2", scallop(100, 106, 50, 16, 0.12, ry=52), shadow=False)
    for x in (68, 132):
        d.shape("hero", circle(x, 62, 11))
        d.marks("mark", circle(x, 63, 5.5))
    face = ("M100 54 C124 54 138 70 138 92 C138 106 132 116 128 126 C122 142 112 152 100 152 "
            "C88 152 78 142 72 126 C68 116 62 106 62 92 C62 70 76 54 100 54Z")
    d.shape("hero", face)
    # pale bridge of the nose and muzzle
    d.shape("light", "M94 84 C96 96 92 108 88 116 L112 116 C108 108 104 96 106 84 C104 80 96 80 94 84Z", shadow=False, line=False)
    d.shape("light", "M100 116 C112 112 126 120 124 132 C122 144 110 146 100 141 C90 146 78 144 76 132 "
                     "C74 120 88 112 100 116Z", shadow=False)
    d.shape("light", ellipse(100, 146, 10, 5), shadow=False)
    # eyes: amber, heavy brow
    for x, k in ((84, 1), (116, -1)):
        d.shape("eye", f"M{x - 8 * k} 92 Q{x} 85 {x + 8 * k} 92 Q{x} 98 {x - 8 * k} 92Z", shadow=False)
        d.marks("mark", circle(x, 92, 2.6))
        d.stroke("mark", f"M{x - 10 * k} 90 Q{x} 81 {x + 9 * k} 89", 2)
    d.shape("nose", "M90 110 C94 108 106 108 110 110 C110 116 104 120 100 122 C96 120 90 116 90 110Z", shadow=False, spot=True)
    d.stroke("mark", "M100 122 V128 M100 128 Q93 135 86 130 M100 128 Q107 135 114 130", 2)
    d.marks("mark", spots([(86, 122), (82, 127), (88, 128), (114, 122), (118, 127), (112, 128)], 1.2))


LION_SIDE = ("M70 100 C76 88 96 86 116 87 C134 88 148 92 152 104 C155 114 150 124 140 128 "
             "L86 128 C74 126 66 114 70 100Z")


def lion_savanna(d: Drawing):
    d.disc("glow", 128, 84, 44)
    birds(d, [(40, 52, 1), (54, 44, 0.8)])
    d.band("far", hills(132, 8))
    acacia(d, 66, 22, 0.62)
    # walking lion, side-on, facing left
    d.limb("hero", "M150 104 C166 106 170 124 168 140", 3, spot=False)
    d.shape("hero2", ellipse(168, 144, 3.6, 5.5), shadow=False, spot=True)
    d.limb("hero", "M140 118 L144 136 L136 158", 10)
    d.limb("hero", "M86 120 L80 158", 10)
    d.limb("hero", "M132 118 L124 136 L128 158", 10)
    d.limb("hero", "M100 120 L106 158", 10)
    d.shape("hero", LION_SIDE)
    d.shape("hero2", scallop(70, 92, 23, 14, 0.13, ry=25), spot=True)
    d.shape("hero", circle(70, 72, 4.5), shadow=False)
    d.shape("hero", "M44 86 C46 76 58 72 68 76 C76 80 80 90 76 98 C72 106 64 110 54 108 L44 104 "
                    "C38 102 36 96 38 92 C38 88 41 86 44 86Z")
    d.shape("light", "M38 96 C42 100 46 106 54 108 C48 110 40 106 38 96Z", shadow=False, line=False)
    d.marks("mark", circle(56, 86, 1.9) + "M37 89 L42 88 L40 93Z")
    d.stroke("mark", "M40 100 Q44 102 48 100", 1.3)
    d.band("ground", hills(160, 5))
    grass(d, -10, 210, 166, 18, "mid", 13)
    d.band("deep", hills(186, 4, 30), line=False)


# ================================================================ LEOPARD
CAT_HEAD = ("M100 48 C128 48 146 64 150 88 C153 110 146 130 130 144 C120 152 110 156 100 156 "
            "C90 156 80 152 70 144 C54 130 47 110 50 88 C54 64 72 48 100 48Z")


def leopard_face(d: Drawing):
    for x, y, a in [(-4, 50, 10), (-2, 100, -10), (6, 150, -30), (204, 50, 170), (202, 100, -170), (194, 150, -150)]:
        d.shape("near", leaf(x, y, 58, 14, a), line=False)
    for x in (64, 136):
        d.shape("hero", circle(x, 58, 15))
        d.shape("mark", circle(x, 60, 8), shadow=False)
    d.shape("hero", CAT_HEAD)
    d.marks("mark", spots([(100, 58), (92, 62), (108, 62), (86, 70), (114, 70), (100, 68), (94, 76), (106, 76),
                           (78, 64), (122, 64)], 2.6))
    d.marks("mark", rosette(62, 100) + rosette(138, 100) + rosette(66, 120, 3) + rosette(134, 120, 3)
            + rosette(78, 138, 3) + rosette(122, 138, 3) + rosette(60, 82, 2.8) + rosette(140, 82, 2.8))
    d.shape("light", "M100 100 C112 100 128 108 128 124 C128 138 114 146 100 146 C86 146 72 138 72 124 "
                     "C72 108 88 100 100 100Z", shadow=False)
    for x, k in ((82, 1), (118, -1)):
        d.shape("light", f"M{x - 13 * k} 90 Q{x} 78 {x + 12 * k} 88 Q{x} 102 {x - 13 * k} 90Z", shadow=False, line=False)
        d.shape("eye", f"M{x - 10 * k} 90 Q{x} 81 {x + 10 * k} 89 Q{x} 99 {x - 10 * k} 90Z", shadow=False, spot=True)
        d.marks("mark", ellipse(x, 90, 2.2, 4.4))
        d.stroke("mark", f"M{x - 11 * k} 90 Q{x} 80 {x + 11 * k} 88", 2)
    d.shape("nose", "M90 106 H110 C110 112 104 116 100 118 C96 116 90 112 90 106Z", shadow=False)
    d.stroke("mark", "M100 118 V124 M100 124 Q93 131 87 126 M100 124 Q107 131 113 126", 2)
    d.marks("mark", spots([(86, 118), (81, 122), (114, 118), (119, 122)], 1.2))


LEO_SIT = ("M78 92 C82 82 96 80 104 88 C112 96 126 98 140 108 C152 118 154 136 146 146 L80 146 "
           "C76 128 74 108 78 92Z")


def leopard_kopje(d: Drawing):
    d.disc("glow", 60, 66, 28)
    birds(d, [(130, 44, 1), (146, 52, 0.8)])
    d.band("far", hills(124, 8))
    acacia(d, 74, 34, 0.5)
    d.band("mid", hills(146, 5, 30))
    d.shape("near", "M30 210 L36 160 Q42 142 66 140 L150 138 Q172 140 176 160 L184 210Z")
    d.shape("deep", "M148 210 L152 168 Q160 154 176 156 Q194 160 196 180 L200 210Z", line=False)

    def cat():
        # tail hangs over the edge of the rock
        d.limb("hero", "M144 136 C162 140 166 158 160 176 C158 182 162 188 168 184", 5.5, spot=True)
        d.shape("hero", LEO_SIT)
        d.limb("hero", "M84 112 L84 144", 10)
        d.limb("hero", "M96 114 L98 144", 10)
        d.shape("hero", ellipse(83, 145, 7, 4), shadow=False)
        d.shape("hero", ellipse(99, 145, 7, 4), shadow=False)
        d.shape("hero", ellipse(132, 132, 18, 15), shadow=False)
        d.shape("hero", ellipse(124, 145, 10, 4), shadow=False)
        d.shape("hero", circle(92, 62, 5), shadow=False)
        d.shape("hero", "M74 70 C76 60 88 56 96 62 C102 66 104 76 98 82 C94 88 86 90 78 88 L72 86 "
                        "C66 84 64 78 68 74 C70 72 72 71 74 70Z")
        d.shape("light", ellipse(72, 82, 6, 4), shadow=False)
        d.marks("mark", circle(80, 71, 1.7) + "M64.5 75 L68.5 74.5 L67 78.5Z")
        clipped(d, LEO_SIT, lambda: d.marks("mark", "".join(rosette(x, y, 3.1) for x, y in [
            (94, 92), (106, 98), (118, 104), (130, 108), (140, 118), (104, 112), (118, 120), (132, 126), (144, 132),
            (112, 136), (126, 140), (90, 104)])))
        d.marks("mark", spots([(84, 122), (84, 132), (98, 124), (98, 134), (150, 150), (160, 162), (163, 172),
                               (86, 66), (90, 72)], 1.8))
    group(d, "translate(100 146) scale(1.08) translate(-100 -146)", cat)
    d.band("deep", hills(192, 3, 30), line=False)


# ================================================================ CHEETAH
def cheetah_face(d: Drawing):
    d.disc("glow", 100, 102, 78, line=False)
    grass(d, -10, 210, 196, 40, "mid", 12)
    for x in (66, 134):
        d.shape("hero", ellipse(x, 62, 11, 10))
        d.shape("mark", ellipse(x, 64, 5.5, 5), shadow=False)
    head = ("M100 50 C124 50 142 62 146 84 C150 104 144 122 132 136 C122 148 112 156 100 156 "
            "C88 156 78 148 68 136 C56 122 50 104 54 84 C58 62 76 50 100 50Z")
    d.shape("hero", head)
    d.marks("mark", spots([(100, 58), (90, 61), (110, 61), (84, 68), (116, 68), (96, 66), (104, 66), (100, 74),
                           (66, 92), (62, 104), (134, 92), (138, 104), (68, 116), (132, 116), (72, 80), (128, 80)], 2.2))
    d.shape("light", "M100 104 C112 104 124 112 124 126 C124 140 112 148 100 148 C88 148 76 140 76 126 "
                     "C76 112 88 104 100 104Z", shadow=False)
    for x, k in ((84, 1), (116, -1)):
        d.shape("light", f"M{x - 12 * k} 90 Q{x} 78 {x + 12 * k} 88 Q{x} 100 {x - 12 * k} 90Z", shadow=False, line=False)
        d.shape("eye", f"M{x - 9 * k} 90 Q{x} 82 {x + 9 * k} 89 Q{x} 98 {x - 9 * k} 90Z", shadow=False, spot=True)
        d.marks("mark", circle(x, 90, 2.6))
        # the cheetah's black "tear lines" from the eye to the corner of the mouth
        d.shape("mark", f"M{x + 7 * k} 94 C{x + 10 * k} 104 {x + 4 * k} 118 {x - 2 * k} 130 "
                        f"L{x - 6 * k} 128 C{x} 118 {x + 4 * k} 106 {x + 3 * k} 95Z", shadow=False)
    d.shape("nose", "M92 106 H108 C108 111 103 115 100 116 C97 115 92 111 92 106Z", shadow=False)
    d.stroke("mark", "M100 116 V122 M100 122 Q94 128 89 124 M100 122 Q106 128 111 124", 2)


CHEETAH_RUN = ("M52 98 C60 88 88 84 118 86 C134 86 148 88 156 94 C160 100 156 108 148 110 "
               "C130 114 108 112 90 110 C72 112 58 108 52 98Z")


def cheetah_sprint(d: Drawing):
    d.disc("glow", 150, 58, 26)
    d.band("far", hills(118, 8))
    acacia(d, -60, 20, 0.55)
    d.band("mid", hills(136, 5, 30))

    def cat():
        d.limb("hero", "M54 96 C40 92 28 96 20 88 C16 84 12 86 10 90", 4.5, spot=True)
        d.stroke("mark", "M18 87 L16 93 M12 85 L9 91", 2)
        # far legs (behind the body)
        d.limb("hero2", "M140 104 L162 120 L178 122", 7)
        d.limb("hero2", "M68 104 L46 122 L34 124", 7)
        # near legs, full stretch
        d.limb("hero", "M146 102 L168 106 L186 104", 8)
        d.limb("hero", "M62 102 L40 110 L24 108", 8)
        d.shape("hero", CHEETAH_RUN)
        clipped(d, CHEETAH_RUN, lambda: d.marks("mark", spots([
            (66, 96), (78, 92), (90, 90), (102, 90), (114, 90), (126, 90), (138, 92), (150, 96),
            (72, 102), (84, 98), (96, 98), (108, 98), (120, 98), (132, 99), (144, 102), (62, 104), (90, 106),
            (114, 106), (138, 106)], 1.8)))
        d.shape("hero", circle(162, 82, 3.4), shadow=False)
        d.shape("hero", "M150 88 C154 80 166 78 172 84 C176 88 180 90 182 94 C182 98 176 100 170 98 "
                        "C162 100 152 98 150 88Z")
        d.shape("light", ellipse(176, 97, 5, 2.4), shadow=False, line=False)
        d.marks("mark", circle(168, 87, 1.5) + "M181 92 L184 93 L182 96Z")
        d.stroke("mark", "M167 90 Q169 95 174 98", 1.5)
    group(d, "translate(100 112) scale(1.1) translate(-100 -100)", cat)
    d.band("ground", hills(150, 4))
    d.band("deep", hills(180, 4, 30), line=False)
    d.stroke("ground", "M6 158 q8 -4 16 0 M24 168 q6 -3 12 0", 2.4, line=False)


# ================================================================ AFRICAN ELEPHANT
def elephant_trumpet(d: Drawing):
    d.disc("glow", 52, 52, 26)
    d.band("far", hills(156, 8), line=False)
    # body rising off the left edge, the head in profile facing right
    d.shape("hero", "M-20 210 L-20 96 C0 74 30 62 60 58 C80 52 100 46 120 50 C138 54 150 66 152 84 "
                    "C154 98 148 110 138 118 C130 124 124 132 122 146 L126 210Z")
    # trunk raised in a trumpet
    d.shape("hero", "M136 98 C152 88 162 70 160 50 C159 40 166 32 176 36 C180 38 180 44 176 46 "
                    "C172 46 170 48 171 54 C174 80 164 104 144 116Z")
    d.stroke("mark", "M158 82 l6 3 M162 70 l6 2 M163 58 l6 1 M152 94 l6 4", 1.6)
    # open mouth and tusk
    d.shape("pop", "M134 118 C140 122 142 130 136 134 C130 134 126 128 128 120Z", shadow=False, line=False)
    d.shape("light", "M128 112 C138 124 156 130 172 122 C168 132 150 140 132 132 C126 128 124 120 128 112Z", spot=False)
    # huge ear, shaped a bit like Africa
    d.shape("hero2", "M92 56 C70 40 40 44 28 66 C20 82 24 104 34 118 C42 130 44 144 56 152 "
                     "C64 156 70 148 72 138 C76 120 88 110 94 96 C100 82 100 66 92 56Z", spot=True)
    d.stroke("mark", "M40 74 Q56 70 70 80 M36 98 Q52 98 64 110", 1.6, line=False)
    d.marks("mark", circle(124, 72, 3))
    d.stroke("mark", "M114 64 Q124 60 132 66", 1.8)
    d.stroke("mark", "M98 130 Q110 126 118 132", 1.6, line=False)


ELEPHANT = ("M46 120 C46 96 66 84 92 84 C108 84 120 88 128 96 C134 86 150 84 160 92 C168 99 168 112 162 120 "
            "C160 132 161 148 166 160 C168 166 163 171 158 166 C151 154 149 140 148 130 L144 132 L144 172 "
            "L132 172 L131 148 L118 148 L117 172 L105 172 L104 148 L80 146 L79 172 L67 172 L66 146 L58 145 "
            "L57 172 L45 172 L46 140 C44 134 44 126 46 120Z")
ELE_EAR = "M126 92 C116 100 114 124 124 136 C134 142 146 134 146 120 C146 106 138 92 126 92Z"
BABY_ELE = ("M50 128 C48 104 64 92 88 92 C100 92 110 96 116 104 C120 92 134 86 146 92 C156 98 158 110 152 120 "
            "L150 140 L138 140 L136 128 L124 130 L122 150 L108 150 L106 132 L80 132 L78 150 L64 150 L62 132 "
            "L52 136 C50 134 50 130 50 128Z")
BABY_EAR = "M118 98 C110 104 110 120 118 128 C126 132 134 126 135 116 C136 104 128 96 118 98Z"


def big_ele(d: Drawing, tusk=True):
    d.stroke("hero", "M46 122 Q37 130 40 142", 2.5)
    d.shape("hero", ELEPHANT)
    d.shape("hero2", ELE_EAR, shadow=False, spot=True)
    if tusk:
        d.shape("light", "M150 124 C156 134 164 138 172 134 C166 142 154 142 148 132Z", shadow=False)
    d.marks("mark", circle(152, 103, 2.2))


def elephant_kilimanjaro(d: Drawing):
    d.disc("glow", 150, 46, 18)
    d.band("far", "M-30 118 L20 110 L64 76 Q76 66 100 66 Q124 66 136 76 L180 108 L230 116")
    d.shape("light", "M64 76 Q76 66 100 66 Q124 66 136 76 L146 84 L134 82 L126 88 L118 80 L108 86 L98 78 "
                     "L88 86 L80 79 L72 85 L66 80 L56 83Z", shadow=False)
    d.shape("light", cloud(12, 100, 1.1), shadow=False, line=False)
    d.shape("light", cloud(150, 94, 0.9), shadow=False, line=False)
    d.band("mid", hills(134, 6, 20))
    group(d, "translate(-2 26) scale(.72)", lambda: big_ele(d))
    group(d, "translate(212 54) scale(-.52 .52)", lambda: big_ele(d))
    group(d, "translate(76 86) scale(.42)", lambda: (d.shape("hero", BABY_ELE), d.shape("hero2", BABY_EAR, shadow=False),
                                                   d.marks("mark", circle(144, 102, 2.6))))
    d.band("ground", hills(160, 4))
    grass(d, -10, 210, 166, 12, "near", 22)
    d.band("deep", hills(184, 4, 20), line=False)


# ================================================================ GIRAFFE
GIRAFFE_NECK = "M44 212 C62 166 82 118 100 80 L126 84 C116 120 106 166 106 212Z"
GIRAFFE_HEAD = ("M98 70 C104 56 122 50 138 56 C150 60 160 70 166 82 C170 90 166 96 158 96 C148 94 138 94 128 94 "
                "C112 94 98 86 98 70Z")


def giraffe_patches():
    return ("M56 196 L62 176 L78 172 L82 190 L70 200Z M86 186 L84 166 L96 158 L104 170 L100 190Z "
            "M66 160 L74 140 L88 136 L92 152 L80 164Z M96 148 L94 130 L106 124 L112 138 L106 152Z "
            "M78 128 L86 110 L98 106 L100 120 L90 130Z M102 116 L102 98 L114 92 L118 106 L110 118Z "
            "M88 100 L96 86 L104 84 L104 96 L96 104Z M108 92 L112 76 L124 74 L124 86 L116 94Z "
            "M118 62 L128 58 L134 66 L124 70Z M60 214 L64 204 L76 206 L72 216Z M90 214 L92 196 L104 198 L104 214Z")


def giraffe_head(d: Drawing):
    d.disc("glow", 60, 70, 34)
    d.band("far", hills(170, 6), line=False)
    group(d, "translate(88 132) scale(.9) translate(-104 -122)", lambda: _giraffe_head(d))


def _giraffe_head(d: Drawing):
    # acacia branch for it to browse
    d.limb("dark", "M230 70 C206 56 190 58 168 48", 4)
    for x, y in [(174, 58), (194, 62)]:
        d.shape("leaf", scallop(x, y, 11, 9, 0.18, ry=8), shadow=False)
    d.stroke("dark", "M176 52 l-3 -5 M190 56 l2 -6 M204 62 l-2 -6", 1.4)
    d.shape("hero", GIRAFFE_NECK)
    # short brown mane along the back of the neck
    d.limb("mark", "M48 204 C64 160 82 118 100 82", 4, shadow=False)
    # ossicones with dark tufts
    d.limb("hero", "M110 60 L104 38", 5)
    d.limb("hero", "M120 56 L118 34", 5)
    d.shape("mark", circle(104, 37, 4), shadow=False)
    d.shape("mark", circle(118, 33, 4), shadow=False)
    d.shape("hero", leaf(104, 66, 26, 7, 196))
    d.shape("hero", GIRAFFE_HEAD)
    clipped(d, GIRAFFE_NECK + " " + GIRAFFE_HEAD, lambda: d.marks("mark", giraffe_patches()))
    d.shape("hero2", "M140 80 C150 74 162 76 166 84 C168 92 162 96 156 95 C148 94 140 90 140 80Z", shadow=False, line=False)
    d.marks("mark", ellipse(162, 82, 1.6, 2.4))
    d.marks("mark", ellipse(130, 70, 3.6, 4))
    d.stroke("mark", "M125 66 l-3 -3 M128 65 l-1 -4 M132 65 l1 -4", 1.2)
    # long purple tongue reaching for the leaves
    d.limb("tongue", "M164 92 C172 92 176 82 174 66", 4.5, shadow=False, spot=True)


GIRAFFE_BODY = "M90 94 C102 84 128 86 146 94 C156 98 158 108 150 114 C136 118 118 118 104 116 C92 114 86 104 90 94Z"


def giraffe_drink(d: Drawing):
    d.disc("glow", 150, 58, 26)
    d.band("far", hills(118, 8))
    acacia(d, -40, 32, 0.48)
    d.band("mid", hills(138, 5, 30))
    d.band("water", "M-30 156 Q40 150 100 154 T230 154")
    ripples(d, [(140, 168, 1), (20, 172, 1), (80, 180, 1.2)])

    def raff():
        d.stroke("hero", "M150 100 Q160 112 158 126", 2.4)
        d.shape("mark", ellipse(158, 129, 2.4, 4), shadow=False)
        # legs: back legs straight, front legs splayed wide to reach the water
        d.limb("hero", "M142 108 L140 160", 6)
        d.limb("hero", "M150 106 L154 158", 6)
        d.limb("hero", "M98 108 L70 158", 6)
        d.limb("hero", "M104 110 L126 158", 6)
        d.shape("hero", GIRAFFE_BODY)
        d.limb("hero", "M98 98 C82 104 68 118 58 140", 12)
        d.limb("mark", "M94 92 C78 98 64 114 54 136", 3, shadow=False)
        d.shape("hero", "M50 136 C56 132 64 134 64 142 C64 150 60 158 54 162 C50 164 46 162 46 158 C46 150 46 140 50 136Z")
        d.limb("hero", "M54 138 L46 126 M58 136 L56 124", 3)
        d.shape("mark", circle(46, 125, 2.4), shadow=False)
        d.shape("mark", circle(56, 123, 2.4), shadow=False)
        d.marks("mark", circle(58, 146, 1.7))
        clipped(d, GIRAFFE_BODY, lambda: d.marks("mark", "".join(ellipse(x, y, 5, 4) for x, y in [
            (100, 96), (112, 92), (124, 94), (136, 96), (146, 102), (106, 106), (118, 104), (130, 106), (142, 110),
            (96, 108), (122, 114)])))
        d.marks("mark", "".join(ellipse(x, y, 3, 2.6) for x, y in [(86, 104), (78, 110), (70, 120), (64, 128)]))
        for x0, y0, x1, y1 in [(142, 108, 140, 160), (150, 106, 154, 158), (98, 108, 70, 158), (104, 110, 126, 158)]:
            d.marks("mark", ellipse(x0 + (x1 - x0) * 0.25, y0 + (y1 - y0) * 0.25, 2, 2.4))
            d.shape("mark", ellipse(x1, y1 + 1, 3.6, 2.4), shadow=False)
    group(d, "translate(96 160) scale(1.1) translate(-100 -160)", raff)
    # reflection of the head in the water
    d.raw('<g opacity=".25">', "")
    d.shape("mark", "M50 176 C56 180 64 178 64 170 C64 166 60 164 54 162Z", shadow=False, line=False)
    d.raw("</g>", "")
    d.band("ground", "M-30 176 Q30 170 70 176 T150 178 T230 176")
    grass(d, 150, 210, 180, 14, "near")
    d.band("deep", hills(192, 3, 30), line=False)


# ================================================================ ZEBRA
ZEBRA_FACE = ("M100 40 C120 40 133 54 133 74 C133 96 124 116 120 136 C118 150 116 168 100 170 "
              "C84 168 82 150 80 136 C76 116 67 96 67 74 C67 54 80 40 100 40Z")


def zebra_face(d: Drawing):
    d.disc("glow", 100, 100, 94, line=False)
    d.disc("glow2", 100, 112, 62, shadow=False, line=False)
    d.band("far", hills(178, 5), line=False)
    neck = "M56 210 C60 170 72 140 84 120 L116 120 C128 140 140 170 144 210Z"
    d.shape("hero", neck)
    clipped(d, neck, lambda: d.marks("mark", "".join(
        f"M{x} 120 C{x - 6 + (x - 100) * 0.3} 150 {x - 4 + (x - 100) * 0.6} 180 {x + (x - 100) * 0.7} 210 "
        f"L{x + 7 + (x - 100) * 0.7} 210 C{x + 3 + (x - 100) * 0.6} 180 {x + 1 + (x - 100) * 0.3} 150 {x + 7} 120Z"
        for x in (60, 76, 92, 108, 124, 140))))
    # ears and the upright striped mane
    for x, a in ((80, -116), (120, -64)):
        d.shape("hero", leaf(x, 52, 36, 10, a))
        d.shape("mark", leaf(x + (2 if a < -90 else -2), 50, 22, 4, a), shadow=False)
    mane = "M86 46 Q88 18 100 14 Q112 18 114 46Z"
    d.shape("hero", mane)
    clipped(d, mane, lambda: d.marks("mark", "M80 22 H120 V26 H80Z M80 31 H120 V35 H80Z M80 40 H120 V44 H80Z M96 10 H104 V20 H96Z"))
    d.shape("hero", ZEBRA_FACE)

    def stripes():
        s = ""
        for i, y in enumerate((52, 64, 76)):  # forehead chevrons
            s += f"M60 {y - 10} L100 {y + 12} L140 {y - 10} L140 {y - 4} L100 {y + 18} L60 {y - 4}Z"
        for y in (104, 118, 132):  # cheeks: bands curving down to the muzzle
            s += f"M60 {y} Q100 {y + 12} 140 {y} L140 {y + 6} Q100 {y + 18} 60 {y + 6}Z"
        return s
    clipped(d, ZEBRA_FACE, lambda: d.marks("mark", stripes()))
    d.shape("muzzle", "M82 140 C82 132 118 132 118 140 C120 156 114 170 100 170 C86 170 80 156 82 140Z", shadow=False)
    d.marks("light", ellipse(91, 156, 2.6, 4) + ellipse(109, 156, 2.6, 4))
    for x in (69, 131):
        d.shape("hero", circle(x, 90, 6.5), shadow=False, line=False)
        d.marks("mark", circle(x, 90, 4))
        d.marks("light", circle(x + 1, 88.6, 1.2))


ZEBRA = ("M42 118 C48 104 84 102 108 104 L122 82 C126 74 134 70 142 72 L156 84 C162 90 162 96 156 99 L144 99 "
         "L134 116 C134 126 130 132 126 134 L126 166 L118 166 L117 140 L112 140 L111 166 L103 166 L102 138 L68 138 "
         "L66 166 L58 166 L57 140 L52 140 L51 166 L43 166 L42 132 C40 126 40 122 42 118Z")
ZEBRA_STRIPES = ("M54 100 L48 142 L55 142 L61 100Z M68 100 L64 142 L71 142 L75 100Z M82 100 L80 142 L87 142 L89 100Z "
                 "M96 100 L96 142 L103 142 L103 100Z M110 98 L110 142 L117 142 L117 98Z M122 104 L126 142 L132 142 L128 104Z "
                 "M114 92 L136 110 L139 105 L118 86Z M120 82 L144 98 L147 93 L124 77Z "
                 "M40 148 H130 V151 H40Z M40 156 H130 V159 H40Z "
                 "M139 70 L137 90 L141 90 L143 70Z M147 76 L146 90 L150 90 L151 78Z")


def zebra(d: Drawing, stripe="mark", body="hero"):
    d.stroke(stripe, "M45 118 Q36 128 38 142", 2.5)
    d.shape(body, ZEBRA)
    clipped(d, ZEBRA, lambda: d.marks(stripe, ZEBRA_STRIPES))
    d.shape(stripe, "M118 86 C122 76 130 70 140 70 L136 66 C126 66 118 74 115 84Z", shadow=False)
    d.shape(body, "M137 73 L134 60 L142 70Z", shadow=False)
    d.marks(stripe, ellipse(156, 93, 4.5, 5))
    d.marks("light", circle(141, 83, 1.9))


def zebra_foal(d: Drawing):
    d.disc("glow", 52, 64, 26)
    d.band("far", hills(128, 8))
    acacia(d, 30, 4, 0.66)
    d.band("mid", hills(146, 5, 30))
    group(d, "translate(-6 -12) scale(1.02)", lambda: zebra(d))
    # foal: shaggier, brown stripes, nuzzling up to mum
    group(d, "translate(176 70) scale(-.58 .58)", lambda: zebra(d, stripe="foal"))
    d.band("ground", hills(170, 4))
    grass(d, -10, 210, 174, 12, "near", 20)
    d.band("deep", hills(188, 4, 30), line=False)


# ================================================================ RHINO
RHINO_HEAD = ("M-4 210 L4 116 C12 88 36 70 66 66 C88 64 104 72 116 82 C130 94 146 100 160 110 "
              "C172 118 178 128 176 140 C174 150 166 154 156 152 C142 150 130 152 120 158 "
              "C102 168 80 172 60 172 C44 182 36 196 36 210Z")


def rhino_head(d: Drawing):
    d.disc("glow", 150, 56, 30)
    d.band("far", hills(186, 4), line=False)
    for x, a in ((54, -112), (72, -86)):
        d.shape("hero", leaf(x, 72, 32, 9, a))
        d.shape("hero2", leaf(x, 70, 18, 4, a), shadow=False, line=False)
    d.shape("hero", RHINO_HEAD)
    # the two horns: a long front horn and a shorter one behind
    d.shape("horn", "M134 100 C140 74 144 50 142 30 C154 50 164 80 166 110Z", spot=True)
    d.shape("horn", "M110 84 C112 72 114 64 116 56 C122 66 128 78 130 90Z", spot=True)
    d.marks("mark", ellipse(110, 108, 2.6, 3.2))
    d.stroke("mark", "M102 104 Q110 100 118 104", 1.6)
    d.stroke("mark", "M176 140 C166 140 158 136 150 140", 2)
    d.stroke("mark", "M30 112 Q40 124 36 140 M48 128 Q58 140 52 158 M82 150 Q96 152 104 146", 1.8)
    d.marks("mark", ellipse(170, 124, 2, 3))


RHINO_BODY = ("M34 118 C32 96 52 82 82 80 C104 78 122 82 134 92 C140 104 140 120 134 134 L124 140 L60 142 "
              "C44 138 36 130 34 118Z")
RHINO_HEAD_S = ("M126 92 C138 88 150 92 158 100 C166 106 174 112 180 122 C182 130 178 136 170 136 C160 136 150 134 "
                "142 132 C132 126 126 112 126 92Z")


def rhino(d: Drawing):
    d.stroke("hero", "M36 112 Q30 120 32 130", 2.4)
    for x, y in [(56, 132), (76, 134), (112, 132), (128, 130)]:
        d.limb("hero", f"M{x} {y} L{x} 160", 15)
    d.shape("hero", RHINO_BODY)
    d.shape("hero", RHINO_HEAD_S)
    d.shape("hero", leaf(136, 92, 16, 5, -110))
    d.shape("horn", "M166 116 C170 102 174 90 180 78 C182 94 182 108 178 122Z", spot=True)
    d.shape("horn", "M154 106 C156 100 158 96 160 92 C164 98 166 104 166 110Z")
    d.marks("mark", circle(152, 114, 1.8))
    d.stroke("mark", "M118 96 Q124 112 120 128 M60 92 Q56 112 62 130", 1.5, line=False)


def oxpecker(d: Drawing, x, y, s=1.0, k=1):
    """A little red-billed oxpecker perched at (x, y), facing right (k=-1: left)."""
    def b():
        d.shape("bird", "M-10 0 C-10 -6 -4 -10 2 -10 C8 -10 12 -6 12 -2 L18 0 L12 2 C10 4 6 4 2 4 L-8 4 L-16 8 Z")
        d.marks("pop", "M11 -4 L20 -1 L11 1Z")
        d.marks("eye", circle(7, -5, 1.6))
        d.stroke("mark", "M-1 4 L-2 9 M3 4 L4 9", 1.2, line=False)
    group(d, f"translate({x} {y}) scale({s * k} {s})", b)


def rhino_oxpecker(d: Drawing):
    d.disc("glow", 150, 58, 28)
    d.band("far", hills(124, 8))
    acacia(d, -62, 4, 0.6)
    d.band("mid", hills(144, 5, 30))
    group(d, "translate(98 160) scale(1.06) translate(-104 -160)", lambda: rhino(d))
    oxpecker(d, 84, 72, 1.0)
    d.band("ground", hills(170, 4))
    grass(d, -10, 210, 172, 12, "near", 19)
    d.band("deep", hills(188, 4, 30), line=False)


# ================================================================ HIPPO
def hippo_yawn(d: Drawing):
    d.disc("glow", 52, 52, 26)
    d.band("far", hills(150, 6), line=False)
    d.stroke("reed", "M178 160 Q176 120 182 92 M188 160 Q190 126 194 104 M168 160 Q166 132 170 114", 3, line=False)
    head = ("M16 176 C12 136 26 104 48 88 C58 80 70 70 84 60 C104 44 124 30 142 22 C154 16 166 20 166 30 "
            "C166 38 160 44 152 48 C130 82 100 120 68 150 L62 176Z")
    jaw = "M38 176 L62 152 C100 146 140 138 172 124 C180 136 174 154 154 164 C124 174 84 178 38 180Z"
    d.shape("mouth", "M60 156 C96 120 128 84 152 48 C160 74 168 100 174 126 C140 138 100 148 60 156Z")
    d.shape("tongue", "M78 150 C100 136 130 126 158 122 C150 136 120 146 78 150Z", shadow=False, line=False)
    d.shape("hero", jaw)
    # tusks and teeth
    d.shape("light", "M150 136 C150 124 152 114 158 104 C162 114 164 124 162 134Z", spot=False)
    d.shape("light", "M128 142 C128 132 130 124 134 118 C138 126 140 134 138 140Z")
    d.shape("light", "M140 60 L146 74 L150 58Z M126 76 L132 88 L136 72Z", shadow=False)
    d.shape("hero", head)
    d.shape("hero", circle(62, 76, 12), shadow=False)
    d.shape("hero", ellipse(44, 74, 6, 8), shadow=False)
    d.marks("mark", ellipse(44, 74, 2.4, 4))
    d.marks("light", circle(64, 74, 4))
    d.marks("mark", circle(65, 74, 2.6))
    d.marks("mark", ellipse(150, 28, 2.6, 4) + ellipse(160, 30, 2, 3.4))
    d.marks("hero2", ellipse(36, 128, 10, 6) + ellipse(56, 110, 6, 4))
    d.band("water", waves(166, 4, 28))
    ripples(d, [(16, 178, 1), (120, 184, 1.4), (170, 176, 1)])
    d.band("deep", waves(190, 3, 34), line=False)


def hippo_head(d: Drawing, x, y, s=1.0, k=1):
    """A hippo's head above the waterline at (x, y): eyes, ears and nostrils showing."""
    def h():
        d.shape("hero", ellipse(-18, -20, 3.6, 5))
        d.shape("hero", "M-34 0 C-36 -12 -30 -22 -20 -22 C-12 -22 -8 -16 -4 -13 C6 -12 18 -16 26 -15 "
                        "C34 -14 38 -8 36 0Z")
        d.shape("hero", circle(-12, -16, 6), shadow=False)
        d.marks("mark", circle(-11, -17, 1.8))
        d.marks("mark", ellipse(30, -9, 1.6, 2.2))
        d.marks("hero2", ellipse(18, -6, 6, 3))
    group(d, f"translate({x} {y}) scale({s * k} {s})", h)


def hippo_river(d: Drawing):
    d.disc("glow", 100, 96, 46)
    birds(d, [(40, 48, 1), (54, 40, 0.8)])
    d.band("far", hills(110, 6))
    acacia(d, -82, -4, 0.62)
    acacia(d, 74, 12, 0.48)
    d.band("water", waves(118, 3, 30))
    # the big bull: his broad back breaks the water, an egret riding on top
    d.shape("hero", "M66 150 C68 128 92 116 118 118 C140 120 156 132 158 150Z")
    hippo_head(d, 160, 150, 1.25)
    d.shape("hero2", ellipse(110, 140, 12, 4), shadow=False, line=False)
    d.shape("egret", "M96 120 C94 112 100 106 108 108 C114 110 116 116 112 120Z")
    d.limb("egret", "M110 110 C112 102 112 96 118 96", 3, shadow=False)
    d.marks("bill", "M118 94 L128 97 L118 98Z")
    d.stroke("mark", "M102 120 L101 126 M106 120 L107 126", 1.2, line=False)
    hippo_head(d, 54, 140, 0.9, -1)
    hippo_head(d, 32, 166, 0.75)
    d.band("water2", waves(150, 3, 36), line=False)
    ripples(d, [(70, 156, 1.4), (130, 160, 1.6), (40, 176, 1), (150, 178, 1.2), (90, 186, 1)])
    d.stroke("reed", "M6 200 Q4 160 10 136 M16 200 Q18 166 22 148 M190 200 Q192 164 186 140 M180 200 Q178 172 182 156", 3, line=False)


# ================================================================ CAPE BUFFALO
BUF_HORN = ("M100 52 C82 46 62 50 48 62 C38 70 30 66 28 52 C24 62 24 80 36 88 C50 96 66 84 82 80 "
            "C90 78 100 78 100 78Z")
BUF_HEAD = ("M100 66 C118 66 130 76 130 92 C130 112 124 128 120 146 C118 160 110 172 100 172 "
            "C90 172 82 160 80 146 C76 128 70 112 70 92 C70 76 82 66 100 66Z")


def buffalo_face(d: Drawing):
    d.disc("glow", 100, 100, 78, line=False)
    d.band("far", hills(170, 6), line=False)
    d.shape("hero", "M30 210 C30 160 56 120 100 116 C144 120 170 160 170 210Z", line=False)
    for k in (1, -1):
        def ear():
            d.shape("hero", "M74 94 C60 92 44 96 34 106 C44 114 60 114 76 106Z")
            d.shape("hero2", "M70 98 C60 98 50 101 42 106 C52 110 62 110 72 104Z", shadow=False, line=False)
        if k == 1:
            ear()
        else:
            flip(d, ear)
    d.shape("hero", BUF_HEAD)
    d.shape("horn", BUF_HORN, spot=True)
    flip(d, lambda: d.shape("horn", BUF_HORN, spot=True))
    d.shape("horn2", "M70 60 C80 54 92 54 100 56 C108 54 120 54 130 60 C120 64 108 66 100 66 C92 66 80 64 70 60Z",
            shadow=False, line=False)
    for x in (82, 118):
        d.marks("light", circle(x, 104, 3.4))
        d.marks("mark", circle(x, 104, 2))
    d.shape("hero2", "M84 152 C84 142 116 142 116 152 C118 166 112 174 100 174 C88 174 82 166 84 152Z", shadow=False)
    d.marks("mark", ellipse(92, 158, 3, 4) + ellipse(108, 158, 3, 4))
    oxpecker(d, 128, 136, 0.8, -1)


BUF_BODY = ("M60 104 C60 86 76 76 96 76 C116 76 134 78 146 86 C156 92 158 108 152 120 C148 128 140 132 130 132 "
            "L76 132 C66 128 60 118 60 104Z")


def buffalo(d: Drawing):
    d.stroke("hero", "M150 98 Q160 112 156 132", 2.4)
    d.shape("hero", ellipse(156, 134, 2.6, 4), shadow=False)
    for x0, x1 in [(84, 84), (98, 100), (132, 134), (144, 146)]:
        d.limb("hero", f"M{x0} 124 L{x1} 160", 10)
    d.shape("hero", BUF_BODY)
    # head held low, facing left, horns sweeping down and up
    d.shape("hero", "M68 86 C58 84 46 92 40 104 C36 112 36 120 40 124 C46 128 54 124 58 118 C64 112 70 106 72 98Z")
    d.shape("horn", "M74 82 C62 72 44 74 36 86 C32 92 26 90 22 78 C18 94 28 104 42 100 C52 96 62 94 74 96Z", spot=True)
    d.shape("horn2", "M58 78 C66 76 72 80 74 86 L70 92 C66 86 62 82 58 80Z", shadow=False, line=False)
    d.shape("hero", leaf(70, 96, 16, 5, 160), shadow=False)
    d.marks("mark", circle(54, 100, 1.8))
    d.marks("hero2", ellipse(42, 120, 5, 4))


def buffalo_marsh(d: Drawing):
    d.disc("glow", 150, 58, 28)
    d.band("far", hills(120, 8))
    acacia(d, -80, -2, 0.66)
    d.band("mid", hills(140, 5, 30))
    group(d, "translate(100 152) scale(1.08) translate(-100 -152)", lambda: buffalo(d))
    oxpecker(d, 112, 76, 1.0)
    d.band("water", "M-30 160 Q40 154 100 158 T230 158")
    ripples(d, [(30, 172, 1), (100, 172, 1.2)])
    # a cattle egret wading in front
    d.stroke("bill", "M152 162 L153 176 M158 162 L158 176", 1.6)
    d.shape("egret", "M144 158 C144 150 152 146 160 148 C166 150 166 158 160 162 L148 164Z")
    d.limb("egret", "M158 150 C160 142 160 138 166 138", 3, shadow=False)
    d.marks("bill", "M166 136 L174 139 L166 140Z")
    d.band("ground", hills(184, 4, 30))
    grass(d, -10, 120, 186, 12, "near", 18)


# ================================================================ WILDEBEEST
GNU_BODY = ("M62 96 C68 84 82 78 96 80 C112 82 130 90 146 96 C156 100 158 112 152 118 L140 122 "
            "L78 124 C66 120 58 108 62 96Z")
GNU_HEAD = ("M66 86 C58 80 46 82 40 92 C34 102 30 114 30 122 C30 128 36 130 40 126 C44 118 52 110 62 104 "
            "C70 100 74 94 66 86Z")


def gnu(d: Drawing, leap=False, horns="horn"):
    d.limb("mark", "M150 100 C158 108 160 122 156 136", 3)
    if leap:
        legs = [(82, 116, 64, 120, 54, 108), (92, 118, 76, 128, 68, 118), (134, 114, 156, 128, 170, 132), (144, 112, 166, 120, 182, 120)]
        for x0, y0, x1, y1, x2, y2 in legs:
            d.limb("hero", f"M{x0} {y0} L{x1} {y1} L{x2} {y2}", 5.5)
    else:
        for x0, x1 in [(80, 78), (92, 96), (134, 132), (144, 148)]:
            d.limb("hero", f"M{x0} 116 L{x1} 160", 5.5)
    d.shape("hero", GNU_BODY)
    d.shape("hero", GNU_HEAD)
    d.shape(horns, "M58 86 C48 84 42 80 40 72 C40 66 46 64 48 70 C48 74 52 78 60 80Z")
    d.shape(horns, "M64 84 C66 76 66 70 62 64 C66 64 72 70 72 78 C72 82 70 86 66 88Z", shadow=False)
    d.shape("mark", "M66 82 C78 78 90 78 100 82 L96 86 C86 84 76 86 68 90Z", shadow=False)
    d.shape("mark", "M44 108 L44 128 L50 118 L52 130 L58 116 L62 126 L64 106Z", shadow=False)
    d.stroke("mark", "M80 88 L84 110 M88 86 L92 108 M96 86 L100 106 M104 86 L106 104", 1.6, line=False)
    d.marks("mark", circle(52, 94, 1.7))
    d.marks("mark", ellipse(33, 121, 3.4, 5))


def gnu_head(d: Drawing):
    d.disc("glow", 140, 70, 34)
    birds(d, [(30, 56, 1), (44, 48, 0.8)])
    d.band("far", hills(150, 8), line=False)
    group(d, "translate(108 38) scale(-.62 .62)", lambda: gnu(d, horns="dark"))
    group(d, "translate(212 52) scale(-.5 .5)", lambda: gnu(d, horns="dark"))
    # big portrait head, three-quarter profile facing left
    d.shape("hero", "M104 210 C100 170 110 134 128 112 L176 112 C184 140 186 176 182 210Z")
    d.shape("hero", "M138 60 C120 54 98 60 86 78 C74 96 64 118 58 136 C54 148 60 156 70 154 C82 152 90 142 98 132 "
                    "C110 118 128 108 146 100 C160 92 156 66 138 60Z")
    # horns curving out and up like handlebars
    d.shape("horn", "M118 62 C102 62 86 60 78 48 C74 40 78 32 84 34 C84 42 92 50 108 52 C114 54 120 56 120 60Z", spot=True)
    d.shape("horn", "M140 60 C150 52 158 44 156 32 C162 34 166 44 162 54 C158 62 150 66 144 68Z", spot=True)
    d.shape("hero", leaf(134, 74, 24, 7, -20))
    d.shape("mark", "M150 68 C162 76 170 92 172 112 L180 112 C176 88 168 72 152 62Z", shadow=False)
    d.shape("mark", "M148 70 C154 92 150 120 140 140 L150 150 L146 160 L160 154 L158 166 L170 156 C172 132 168 100 158 76Z",
            shadow=False)
    d.shape("mark", "M70 154 C64 154 58 150 58 142 C60 134 68 132 74 136 C78 142 76 152 70 154Z", shadow=False)
    d.stroke("mark", "M104 74 C98 90 90 104 80 118 M112 72 C106 86 98 100 90 112", 2, line=False)
    d.marks("mark", circle(116, 78, 3))
    d.marks("light", circle(117, 77, 1))
    d.band("ground", hills(186, 4), line=False)


def gnu_crossing(d: Drawing):
    d.disc("glow", 46, 50, 20)
    d.band("far", hills(84, 6))
    for i, x in enumerate(range(-6, 210, 24)):
        group(d, f"translate({x} {56 + (i % 2) * 3}) scale(.22)", lambda: (
            d.shape("dark", GNU_BODY + " " + GNU_HEAD, shadow=False),
            d.stroke("dark", "M80 120 L78 150 M94 120 L96 150 M134 120 L132 150 M144 116 L148 150", 6)))
    d.band("water", waves(100, 3, 30))
    # steep dusty bank on the right, with the next one about to jump
    d.shape("bank", "M132 230 C132 180 130 140 142 112 C150 100 176 96 230 96 L230 230Z")
    d.stroke("deep", "M150 130 l10 12 M164 116 l10 10 M146 160 l8 10", 2, line=False)
    group(d, "translate(146 30) scale(.42)", lambda: gnu(d))
    # the leap: mid-air, front legs tucked, back legs trailing
    group(d, "translate(88 92) rotate(-16) scale(.74) translate(-100 -100)", lambda: gnu(d, leap=True))
    for x, y, s in [(46, 148, 1.1), (30, 144, 0.6)]:
        d.shape("light", f"M{x - 18 * s} {y} L{x - 14 * s} {y - 16 * s} L{x - 6 * s} {y - 6 * s} L{x} {y - 22 * s} "
                         f"L{x + 6 * s} {y - 6 * s} L{x + 14 * s} {y - 16 * s} L{x + 18 * s} {y}Z", shadow=False)
    # swimmers: heads and horns above the water
    for x, y in [(70, 158), (104, 170)]:
        group(d, f"translate({x} {y}) scale(.5)", lambda: (
            d.shape("hero", "M-14 0 C-14 -12 -6 -18 4 -16 C12 -14 14 -6 12 0Z"),
            d.shape("horn", "M-4 -14 C-12 -16 -16 -22 -14 -28 C-10 -24 -6 -20 2 -18Z M4 -16 C8 -22 8 -26 6 -30 C12 -26 12 -20 8 -14Z", shadow=False),
            d.marks("mark", circle(-6, -8, 2))))
    d.band("water2", waves(152, 3, 34), line=False)
    ripples(d, [(30, 176, 1.4), (120, 160, 1.2), (60, 186, 1)])
    d.band("deep", waves(190, 3, 38), line=False)


# ================================================================ HYENA
def hyena_face(d: Drawing):
    d.disc("glow", 100, 104, 78, line=False)
    grass(d, -10, 210, 198, 36, "mid", 12)
    d.shape("hero", "M40 210 C40 170 64 136 100 132 C136 136 160 170 160 210Z", line=False)
    d.shape("mark", "M88 132 C92 128 108 128 112 132 L110 150 L90 150Z", shadow=False, line=False)
    for k in (1, -1):
        def ear():
            d.shape("hero", ellipse(64, 60, 17, 20), extra='transform="rotate(-24 64 60)"')
            d.shape("mark", ellipse(65, 62, 9, 12), shadow=False, extra='transform="rotate(-24 65 62)"')
        ear() if k == 1 else flip(d, ear)
    head = ("M100 58 C126 58 144 74 144 98 C144 116 134 128 124 136 C118 148 110 160 100 160 "
            "C90 160 82 148 76 136 C66 128 56 116 56 98 C56 74 74 58 100 58Z")
    d.shape("hero", head)
    clipped(d, head, lambda: d.marks("mark", spots([(64, 96), (70, 108), (60, 110), (136, 96), (130, 108), (140, 110),
                                                   (74, 122), (126, 122), (92, 66), (108, 66), (100, 72)], 3)))
    d.shape("muzzle", "M84 116 C84 104 116 104 116 116 C118 136 112 154 100 156 C88 154 82 136 84 116Z", shadow=False, spot=True)
    for x in (84, 116):
        d.marks("light", circle(x, 96, 5))
        d.marks("mark", circle(x, 96, 3.2))
        d.marks("light", circle(x + 1, 95, 1))
    d.marks("mark", "M90 118 C90 112 110 112 110 118 C110 124 104 128 100 128 C96 128 90 124 90 118Z")
    # the famous grin
    d.shape("mouth", "M80 140 Q100 156 120 140 Q118 160 100 162 Q82 160 80 140Z", shadow=False)
    d.shape("light", "M84 142 L88 148 L91 145 L95 150 L100 147 L105 150 L109 145 L112 148 L116 142 Q100 152 84 142Z", shadow=False)


HYENA_BODY = ("M60 92 C70 82 90 80 108 86 C124 92 138 102 146 112 C150 120 146 128 138 128 L80 126 "
              "C66 122 58 106 60 92Z")


def hyena(d: Drawing):
    d.shape("mark", "M144 112 C152 116 158 124 156 134 C150 132 144 124 140 118Z")
    for p in ["M72 112 L70 164", "M84 116 L88 164", "M130 120 L136 142 L130 164", "M140 118 L148 142 L144 164"]:
        d.limb("hero", p, 8)
    d.shape("hero", HYENA_BODY)
    d.shape("hero", "M66 80 C58 72 46 72 38 78 C32 82 28 88 24 94 C22 98 24 104 30 104 C38 104 46 104 54 106 "
                    "C62 104 70 96 66 80Z")
    d.shape("muzzle", "M24 94 C22 98 24 104 30 104 L36 104 C36 98 32 92 28 90Z", shadow=False, line=False)
    d.shape("hero", ellipse(54, 70, 6, 8), shadow=False)
    d.marks("mark", ellipse(54, 71, 3, 5))
    d.limb("mark", "M58 76 C74 76 90 80 104 86", 4, shadow=False)
    clipped(d, HYENA_BODY, lambda: d.marks("mark", spots([(80, 94), (92, 92), (104, 96), (116, 100), (128, 106),
                                                         (86, 106), (100, 106), (112, 110), (124, 114), (136, 116),
                                                         (94, 118), (110, 120)], 3)))
    d.marks("mark", spots([(72, 128), (70, 140), (86, 130), (87, 142), (134, 132), (144, 132)], 2.2))
    d.marks("mark", circle(44, 84, 1.8) + "M22 93 L26 92 L25 96Z")


def hyena_dusk(d: Drawing):
    d.disc("glow", 118, 76, 34)
    d.disc("sky", 140, 66, 6, shadow=False, line=False)
    d.disc("sky", 104, 92, 4, shadow=False, line=False)
    d.disc("sky", 124, 96, 3, shadow=False, line=False)
    d.band("far", hills(130, 8))
    acacia(d, -82, 2, 0.66)
    d.band("mid", hills(146, 5, 30))
    group(d, "translate(102 162) scale(1.12) translate(-90 -164)", lambda: hyena(d))
    d.band("ground", hills(172, 4))
    grass(d, -10, 210, 176, 12, "near", 18)
    d.band("deep", hills(190, 4, 30), line=False)


# ================================================================ AFRICAN WILD DOG
def wilddog_face(d: Drawing):
    d.disc("glow", 100, 108, 70, line=False)
    d.band("far", hills(182, 5), line=False)
    d.shape("hero", "M50 210 C52 172 72 146 100 142 C128 146 148 172 150 210Z", line=False)
    clipped(d, "M50 210 C52 172 72 146 100 142 C128 146 148 172 150 210Z",
            lambda: d.marks("mark", ellipse(70, 180, 14, 10) + ellipse(126, 168, 10, 14) + ellipse(100, 200, 16, 8)))
    d.marks("light", ellipse(84, 160, 8, 6) + ellipse(140, 192, 8, 6))
    # the huge round ears
    for k in (1, -1):
        def ear():
            d.shape("hero", "M76 80 C62 74 48 62 46 40 C46 28 56 22 66 28 C80 36 88 58 86 76Z")
            d.shape("mark", "M76 74 C66 70 56 60 54 44 C54 36 60 32 66 36 C76 44 82 58 80 72Z", shadow=False)
            d.stroke("light", "M60 54 l8 4 M58 46 l8 2 M64 64 l8 4", 2, line=False)
        ear() if k == 1 else flip(d, ear)
    head = ("M100 64 C122 64 136 78 136 98 C136 114 128 124 122 132 C116 146 110 158 100 158 "
            "C90 158 84 146 78 132 C72 124 64 114 64 98 C64 78 78 64 100 64Z")
    d.shape("hero", head)
    clipped(d, head, lambda: (d.marks("mark", ellipse(70, 116, 9, 7) + ellipse(134, 108, 7, 10) + "M96 60 H104 V104 H96Z"),
                              d.marks("light", ellipse(128, 124, 6, 4) + ellipse(68, 100, 5, 4))))
    d.shape("mark", "M90 104 C94 100 106 100 110 104 C116 120 112 150 100 158 C88 150 84 120 90 104Z", shadow=False)
    d.marks("eye", circle(84, 96, 4.4) + circle(116, 96, 4.4))
    d.marks("mark", circle(84, 96, 2.4) + circle(116, 96, 2.4))
    d.shape("mark", "M90 132 C92 126 108 126 110 132 C110 138 104 142 100 142 C96 142 90 138 90 132Z", shadow=False)
    d.marks("light", ellipse(96, 131, 2.5, 1.5))


WDOG_BODY = ("M50 96 C58 86 80 84 104 86 C122 86 136 88 142 96 C146 106 140 116 130 118 C112 120 86 114 66 112 "
             "C56 110 50 104 50 96Z")


def wilddog(d: Drawing, phase=0):
    legs = [["M132 106 L150 122 L166 122", "M126 108 L132 130 L144 140", "M62 104 L46 120 L30 118", "M70 106 L62 130 L50 138"],
            ["M132 106 L138 130 L150 140", "M126 108 L146 116 L162 112", "M62 104 L54 128 L42 138", "M70 106 L50 114 L34 108"]][phase]
    for p in legs[1::2]:
        d.limb("hero2", p, 5)
    d.limb("hero", "M54 94 C40 96 32 102 26 100", 6)
    d.shape("light", circle(24, 100, 5.5), shadow=False)
    for p in legs[0::2]:
        d.limb("hero", p, 5.5)
    d.shape("hero", WDOG_BODY)
    clipped(d, WDOG_BODY, lambda: (d.marks("mark", ellipse(66, 96, 9, 7) + ellipse(96, 104, 11, 6) + ellipse(122, 94, 7, 6)
                                           + ellipse(84, 90, 5, 4)),
                                   d.marks("light", ellipse(80, 106, 6, 4) + ellipse(110, 92, 6, 4) + ellipse(134, 104, 4, 3))))
    for x in (144, 152):
        d.shape("hero", ellipse(x, 72, 5.5, 9.5), extra=f'transform="rotate({(x - 148) * 3} {x} 72)"')
        d.marks("mark", ellipse(x, 73, 3, 6.5))
    d.shape("hero", "M136 92 C138 82 148 78 156 80 C162 82 168 86 174 90 C176 94 172 98 166 98 C158 98 146 100 140 100Z")
    d.shape("mark", "M160 84 C166 86 172 88 174 90 C176 94 172 98 166 98 L158 96Z", shadow=False)
    d.marks("eye", circle(154, 86, 1.8))


def wilddog_pack(d: Drawing):
    d.disc("glow", 60, 60, 26)
    birds(d, [(130, 46, 1), (146, 54, 0.8)])
    d.band("far", hills(108, 8))
    acacia(d, 34, -40, 0.56)
    d.band("mid", hills(124, 5, 30))
    group(d, "translate(66 46) scale(.62)", lambda: wilddog(d, 1))
    d.band("ground", hills(150, 4))
    group(d, "translate(-10 34) scale(1.0)", lambda: wilddog(d, 0))
    grass(d, -10, 210, 178, 12, "near", 20)
    d.band("deep", hills(188, 4, 30), line=False)


# ================================================================ MEERKAT
def meerkat(d: Drawing, look=0):
    """An upright meerkat, front-on, standing on its back legs. Feet at y=188, about 150 tall."""
    d.limb("hero", "M122 178 C140 182 150 176 156 166", 7)
    d.shape("mark", ellipse(156, 164, 4, 6), shadow=False, extra='transform="rotate(30 156 164)"')
    d.shape("hero", "M84 92 C70 104 64 130 66 156 C68 176 80 188 100 188 C120 188 132 176 134 156 "
                    "C136 130 130 104 116 92Z")
    d.shape("hero2", "M90 104 C82 116 80 140 82 160 C84 176 92 184 100 184 C108 184 116 176 118 160 "
                     "C120 140 118 116 110 104Z", shadow=False, line=False)
    d.shape("hero", ellipse(82, 186, 9, 4.5), shadow=False)
    d.shape("hero", ellipse(118, 186, 9, 4.5), shadow=False)
    d.limb("hero", "M84 108 C80 118 84 126 92 126", 8)
    d.limb("hero", "M116 108 C120 118 116 126 108 126", 8)
    d.shape("mark", ellipse(93, 128, 4, 3), shadow=False, line=False)
    d.shape("mark", ellipse(107, 128, 4, 3), shadow=False, line=False)

    def head():
        d.shape("mark", ellipse(74, 58, 4, 6), extra='transform="rotate(-20 74 58)"')
        d.shape("mark", ellipse(126, 58, 4, 6), extra='transform="rotate(20 126 58)"')
        d.shape("hero", "M100 34 C116 34 126 46 126 58 C126 70 118 80 110 88 C106 92 103 96 100 100 "
                        "C97 96 94 92 90 88 C82 80 74 70 74 58 C74 46 84 34 100 34Z")
        d.shape("hero2", "M88 74 C92 70 108 70 112 74 C112 82 106 92 100 98 C94 92 88 82 88 74Z", shadow=False, line=False)
        d.marks("mark", ellipse(88, 62, 6, 8.5) + ellipse(112, 62, 6, 8.5))
        d.marks("light", circle(89 + look, 61, 2.4) + circle(113 + look, 61, 2.4))
        d.marks("mark", "M95 94 C95 92 105 92 105 94 L100 100Z")
    group(d, f"rotate({look * 3} 100 92)", head)


def meerkat_sentry(d: Drawing):
    d.disc("glow", 100, 96, 80, line=False)
    d.band("far", hills(170, 6), line=False)
    group(d, "translate(100 178) scale(.96) translate(-100 -188)", lambda: meerkat(d))
    d.band("ground", hills(178, 6))
    d.band("deep", hills(192, 4, 30), line=False)


def meerkat_family(d: Drawing):
    d.disc("glow", 150, 52, 22)
    # a hawk overhead: the reason for the lookout
    d.shape("dark", "M44 46 C52 40 60 40 64 44 C68 40 76 40 84 46 C76 46 70 48 66 52 L64 56 L62 52 C58 48 52 46 44 46Z",
            shadow=False)
    d.band("far", hills(124, 8))
    acacia(d, 88, 12, 0.52)
    d.band("mid", hills(140, 5, 30))
    # sandy burrow mound
    d.shape("ground", "M10 200 C20 168 50 150 100 150 C150 150 180 168 190 200Z")
    d.shape("deep", ellipse(150, 170, 10, 6), shadow=False, line=False)
    group(d, "translate(62 158) scale(.5) translate(-100 -188)", lambda: meerkat(d, look=-2))
    group(d, "translate(136 166) scale(.42) translate(-100 -188)", lambda: meerkat(d, look=2))
    group(d, "translate(100 156) scale(.66) translate(-100 -188)", lambda: meerkat(d, look=-2))
    group(d, "translate(150 168) scale(.26) translate(-100 -188)", lambda: meerkat(d))
    d.band("deep", hills(190, 4, 30), line=False)


# ================================================================ CHIMPANZEE
def chimp_face(d: Drawing):
    for x, y, a in [(-6, 46, 20), (-4, 100, 0), (2, 156, -20), (206, 46, 160), (204, 100, 180), (198, 156, -160)]:
        d.shape("near", leaf(x, y, 60, 15, a), line=False)
    d.shape("hero", "M30 210 C34 170 60 146 100 144 C140 146 166 170 170 210Z", line=False)
    for k in (1, -1):
        def ear():
            d.shape("face2", "M58 86 C40 80 32 98 38 112 C42 122 52 124 60 118Z")
            d.stroke("mark", "M52 96 C44 98 44 110 52 114", 2, line=False)
        ear() if k == 1 else flip(d, ear)
    d.shape("hero", scallop(100, 96, 46, 16, 0.08, ry=56))
    face = ("M100 66 C114 66 128 70 132 82 C136 94 134 106 128 116 C136 126 136 142 126 152 C118 160 108 162 100 162 "
            "C92 162 82 160 74 152 C64 142 64 126 72 116 C66 106 64 94 68 82 C72 70 86 66 100 66Z")
    d.shape("face", face)
    # heavy brow ridge
    d.shape("face2", "M68 88 C72 76 88 74 100 82 C112 74 128 76 132 88 C126 86 114 86 100 92 C86 86 74 86 68 88Z", shadow=False)
    for x in (86, 114):
        d.marks("mark", ellipse(x, 98, 5, 4.4))
        d.marks("light", circle(x + 1.4, 96.6, 1.3))
    d.stroke("face2", "M80 108 Q86 112 92 108 M108 108 Q114 112 120 108", 1.6, line=False)
    d.marks("mark", ellipse(94, 120, 2.4, 1.6) + ellipse(106, 120, 2.4, 1.6))
    d.stroke("mark", "M96 104 Q100 112 104 104", 1.4, line=False)
    d.shape("face2", "M76 134 C80 128 120 128 124 134 C126 146 114 156 100 156 C86 156 74 146 76 134Z", shadow=False)
    d.stroke("mark", "M78 136 Q100 146 122 136", 2.2)


def chimp_termites(d: Drawing):
    d.band("far", hills(104, 10))
    mist(d, 116, 4, 40)
    for x, y, r in [(16, 90, 22), (52, 76, 20), (186, 80, 24), (156, 66, 18)]:
        d.shape("mid", scallop(x, y, r, 9, 0.14), shadow=False, line=False)
    d.limb("dark", "M24 210 L22 70 M182 210 L184 72", 8)
    d.band("mid", hills(150, 5, 30))
    # termite mound
    d.shape("mound", "M118 190 L128 136 C130 120 134 104 138 92 C140 84 146 84 148 92 C152 106 156 122 160 140 "
                     "L172 190Z", spot=True)
    d.stroke("mark", "M136 120 l6 2 M140 144 l6 -2 M150 112 l4 4 M152 158 l6 2", 1.6, line=False)
    d.marks("mark", ellipse(146, 130, 2.6, 3.4))

    def chimp():
        # sitting, side-on, facing right, poking a grass stem into the mound
        d.shape("hero", "M48 182 C40 160 44 132 60 116 C70 106 86 104 96 112 C104 120 106 140 104 160 L104 182Z")
        d.limb("hero", "M60 170 C74 168 86 172 92 182", 16)
        d.limb("hero", "M86 124 C100 132 110 140 120 138", 10)
        d.shape("face", ellipse(124, 138, 5, 4.4), shadow=False)
        d.stroke("dark", "M122 140 L150 128", 1.8)
        d.shape("hero", "M74 86 C74 74 84 66 96 66 C108 66 118 76 116 90 C114 100 104 106 94 106 C82 106 74 98 74 86Z")
        d.shape("face", "M98 78 C106 76 116 80 120 88 C124 96 120 104 112 106 C104 108 98 102 98 96Z")
        d.shape("face", ellipse(84, 84, 6, 8), shadow=False)
        d.shape("face2", "M98 80 C104 76 116 78 118 84 C112 84 104 86 98 86Z", shadow=False)
        d.marks("mark", circle(109, 88, 1.8))
        d.stroke("mark", "M108 100 Q114 102 120 98", 1.4)
    group(d, "translate(-4 2)", chimp)
    for x, y in [(152, 126), (156, 132), (147, 122)]:
        d.marks("mark", ellipse(x, y, 1.6, 1))
    d.band("near", hills(184, 4))
    for x, y, a in [(4, 200, -60), (20, 204, -90), (190, 204, -110), (178, 200, -90)]:
        d.shape("near", leaf(x, y, 40, 9, a), line=False)


# ================================================================ WARTHOG
def warthog_face(d: Drawing):
    d.disc("glow", 100, 100, 80, line=False)
    d.band("far", hills(176, 6), line=False)
    d.shape("hero", "M40 210 C44 170 68 140 100 138 C132 140 156 170 160 210Z", line=False)
    # bristly mane, ears
    d.shape("mane", "M84 54 L80 30 L90 44 L94 22 L100 42 L106 22 L110 44 L120 30 L116 54Z")
    for k in (1, -1):
        def side():
            d.shape("hero", leaf(76, 62, 30, 10, -150))
            d.shape("mark", leaf(74, 62, 18, 4, -150), shadow=False, line=False)
            # tusks curling up and out from the snout
            d.shape("light", "M84 150 C64 150 50 136 48 108 C46 102 52 100 54 106 C58 126 68 136 84 140Z")
        side() if k == 1 else flip(d, side)
    d.shape("hero", "M100 46 C118 46 130 56 132 72 C134 90 128 106 124 122 C122 134 122 146 120 154 L80 154 "
                    "C78 146 78 134 76 122 C72 106 66 90 68 72 C70 56 82 46 100 46Z")
    # warts: the knobbly bumps on the face
    for k in (1, -1):
        def wart():
            d.shape("hero", "M72 98 C64 96 58 102 60 108 C62 112 68 112 74 110Z")
            d.shape("hero", "M78 126 C72 126 70 132 72 136 C74 138 78 138 80 136Z", shadow=False)
        wart() if k == 1 else flip(d, wart)
    d.stroke("hero2", "M86 96 C90 110 92 130 90 146 M114 96 C110 110 108 130 110 146", 2, line=False)
    d.marks("mark", circle(86, 82, 3) + circle(114, 82, 3))
    d.stroke("mark", "M80 76 Q86 72 92 76 M108 76 Q114 72 120 76", 1.6)
    d.shape("hero2", ellipse(100, 156, 24, 13))
    d.marks("mark", ellipse(92, 156, 3.4, 4.4) + ellipse(108, 156, 3.4, 4.4))
    d.stroke("light", "M66 116 Q60 126 62 136 M134 116 Q140 126 138 136", 2.2, line=False)


WARTHOG_BODY = ("M54 104 C56 88 72 80 92 80 C112 80 130 84 142 92 C150 98 152 110 146 120 C140 128 128 130 116 130 "
                "L72 130 C60 126 52 116 54 104Z")


def warthog(d: Drawing, tail="hero"):
    d.stroke(tail, "M144 96 L150 54", 2.2)
    d.shape("mane", leaf(150, 54, 12, 3.4, -80), shadow=False)
    for x0, x1, y1 in [(76, 72, 160), (90, 94, 158), (126, 130, 160), (138, 134, 158)]:
        d.limb("hero", f"M{x0} 120 L{x1} {y1}", 8)
    d.shape("hero", WARTHOG_BODY)
    d.shape("mane", "M60 84 L64 72 L70 82 L76 70 L82 80 L90 70 L96 80 L104 72 L110 82 L118 76 L120 86 Z", shadow=False)
    # head, low and long, facing left
    d.shape("hero", "M68 88 C60 82 50 84 44 92 C38 100 32 112 28 122 C26 128 30 134 36 132 C44 130 52 124 60 118 "
                    "C68 112 74 100 68 88Z")
    d.shape("hero2", ellipse(30, 128, 5, 6), shadow=False)
    d.shape("light", "M36 122 C30 116 28 106 32 98 C34 96 36 98 35 100 C34 108 36 114 40 118Z")
    d.shape("hero", leaf(62, 86, 14, 5, -120), shadow=False)
    d.shape("hero", ellipse(48, 112, 4, 5), shadow=False)
    d.marks("mark", circle(54, 98, 1.8))


def warthog_run(d: Drawing):
    d.disc("glow", 150, 60, 28)
    d.band("far", hills(124, 8))
    acacia(d, -62, 6, 0.6)
    d.band("mid", hills(142, 5, 30))
    group(d, "translate(96 160) scale(1.0) translate(-100 -160)", lambda: warthog(d))
    for x in (156, 182):
        group(d, f"translate({x} 162) scale(.34) translate(-100 -160)", lambda: warthog(d))
    d.band("ground", hills(168, 4))
    grass(d, -10, 210, 172, 12, "near", 19)
    d.band("deep", hills(188, 4, 30), line=False)


# ================================================================ OSTRICH
def ostrich_head(d: Drawing):
    d.disc("glow", 52, 60, 28)
    d.band("far", hills(168, 6), line=False)
    # black body plumage with white wing plumes at the bottom
    d.shape("dark", scallop(96, 214, 70, 16, 0.08, ry=48))
    for x, a in [(40, -120), (56, -104), (150, -60), (136, -76)]:
        d.shape("light", leaf(x, 196, 40, 9, a), shadow=False)
    d.limb("hero", "M98 186 C94 150 102 110 112 72", 20)
    d.stroke("hero2", "M92 172 C90 146 96 116 104 86", 2, line=False)
    head = ("M94 58 C96 42 112 32 128 34 C138 36 146 42 152 50 L172 56 C178 58 178 64 172 66 L148 70 "
            "C134 76 112 78 102 72 C96 68 93 64 94 58Z")
    d.shape("hero", head)
    d.shape("bill", "M140 54 L172 56 C178 58 178 64 172 66 L146 70 C142 66 140 60 140 54Z", shadow=False, spot=True)
    d.stroke("mark", "M146 62 L172 61", 1.6)
    d.marks("mark", ellipse(168, 58, 1.4, 1))
    d.marks("light", circle(124, 52, 9))
    d.marks("mark", circle(125, 52, 6))
    d.marks("light", circle(127, 49.5, 2))
    d.stroke("mark", "M114 46 L110 42 M117 43 L115 38 M121 41 L121 36 M126 41 L128 36 M131 42 L134 38", 1.6)
    d.stroke("hero2", "M100 40 q2 -6 6 -6 M108 36 q2 -6 6 -6 M116 34 q4 -5 8 -4", 1.6, line=False)


def ostrich(d: Drawing):
    # far leg, then near leg mid-stride
    d.limb("leg", "M106 120 L118 148 L104 176 L112 178", 6)
    d.limb("leg", "M96 120 L82 146 L66 166 L72 170", 7)
    d.shape("leg", ellipse(92, 124, 10, 12))
    d.shape("dark", "M54 104 C54 84 74 74 98 74 C118 74 134 82 140 94 C144 104 138 118 124 124 C108 130 86 130 70 126 "
                    "C60 122 54 114 54 104Z")
    d.shape("light", "M50 92 C40 86 30 88 26 96 C36 96 44 100 52 106Z")
    d.shape("light", "M64 82 C80 76 100 80 112 90 C100 96 80 96 64 92Z", shadow=False)
    d.limb("leg", "M128 88 C140 74 140 54 136 36", 7)
    d.shape("leg", "M130 32 C132 26 140 24 144 28 L154 32 C156 34 154 36 152 36 L142 38 C136 40 130 38 130 32Z")
    d.marks("mark", circle(138, 31, 1.6))


def ostrich_run(d: Drawing):
    d.disc("glow", 52, 58, 24)
    d.band("far", hills(118, 8))
    acacia(d, 66, -2, 0.6)
    d.band("mid", hills(140, 5, 30))
    d.band("ground", hills(164, 4))
    group(d, "translate(100 168) scale(1.12) translate(-96 -176)", lambda: ostrich(d))
    for x, y, s in [(44, 168, 0.6), (30, 162, 0.4)]:
        d.shape("light", cloud(x, y, s), shadow=False, line=False)
    grass(d, 100, 210, 176, 12, "near", 20)
    d.band("deep", hills(188, 4, 30), line=False)


# ================================================================ LEMUR
def ring_tail(d: Drawing, pts, w=14, a="hero2", b="mark"):
    """A ring-tailed lemur's tail along the polyline pts, alternating light and black rings."""
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        d.limb(b if i % 2 else a, f"M{x0:.1f} {y0:.1f} L{x1:.1f} {y1:.1f}", w, shadow=(i == 0), spot=bool(i % 2))


def lemur_face(d: Drawing):
    d.disc("glow", 100, 100, 70, line=False)
    # the striped tail curling round the portrait
    pts = []
    for i in range(23):
        t = i / 22
        a = math.radians(80 - 270 * t)
        r = 74 - 10 * t
        pts.append((100 + r * math.cos(a), 104 + r * math.sin(a)))
    ring_tail(d, pts, 15)
    d.shape("hero", "M50 210 C52 170 72 146 100 142 C128 146 148 170 150 210Z")
    for k in (1, -1):
        def ear():
            d.shape("hero", leaf(70, 64, 26, 10, -130))
            d.shape("light", leaf(70, 64, 18, 6, -130), shadow=False, line=False)
        ear() if k == 1 else flip(d, ear)
    head = ("M100 52 C122 52 138 64 140 82 C142 98 132 116 120 130 C114 138 106 146 100 150 "
            "C94 146 86 138 80 130 C68 116 58 98 60 82 C62 64 78 52 100 52Z")
    d.shape("light", head)
    d.shape("hero", "M100 52 C116 52 128 58 134 68 C122 66 110 70 100 78 C90 70 78 66 66 68 C72 58 84 52 100 52Z",
            shadow=False, line=False)
    # dark eye patches and long dark muzzle
    d.marks("mark", "M74 82 C82 78 94 84 96 96 C94 104 84 106 78 100 C74 94 72 88 74 82Z")
    d.marks("mark", "M126 82 C118 78 106 84 104 96 C106 104 116 106 122 100 C126 94 128 88 126 82Z")
    d.shape("mark", "M94 102 C96 98 104 98 106 102 L108 134 C106 144 94 144 92 134Z", shadow=False)
    d.marks("eye", circle(86, 93, 5) + circle(114, 93, 5))
    d.marks("mark", circle(86, 93, 2.4) + circle(114, 93, 2.4))
    d.marks("light", circle(87.4, 91.6, 1) + circle(115.4, 91.6, 1))


def baobab(d: Drawing, x, y, h, w, role="dark", s=1.0):
    """A Madagascan baobab: a tall bottle trunk with a small flat crown of branches."""
    top = y - h
    d.shape(role, f"M{x - w / 2} {y} C{x - w * 0.6} {y - h * 0.5} {x - w * 0.32} {top + 10} {x - w * 0.3} {top} "
                  f"L{x + w * 0.3} {top} C{x + w * 0.32} {top + 10} {x + w * 0.6} {y - h * 0.5} {x + w / 2} {y}Z")
    d.stroke(role, f"M{x - w * 0.2} {top + 2} L{x - w * 0.9} {top - 10} M{x} {top + 2} L{x - w * 0.2} {top - 14} "
                   f"M{x + w * 0.1} {top + 2} L{x + w * 0.4} {top - 14} M{x + w * 0.2} {top + 2} L{x + w * 0.9} {top - 8}", 3 * s)
    d.shape(role, scallop(x, top - 12, w * 0.9, 9, 0.12, ry=5 * s), shadow=False)


def lemur_baobab(d: Drawing):
    d.disc("glow", 100, 84, 40)
    d.band("far", hills(148, 4))
    baobab(d, 28, 150, 70, 18)
    baobab(d, 172, 150, 76, 20)
    baobab(d, 140, 150, 44, 12, s=0.7)
    d.band("mid", hills(160, 3, 30))
    # branch
    d.limb("branch", "M-10 112 C40 108 120 110 210 104", 9)

    def lemur():
        pts = [(104, 108), (110, 120), (114, 132), (116, 144), (114, 156), (108, 166), (98, 172), (88, 170), (82, 162),
               (84, 152), (92, 148)]
        ring_tail(d, pts, 9)
        d.shape("hero", "M74 108 C70 92 76 80 90 78 C102 78 108 88 108 100 L106 110Z")
        d.shape("light", "M80 108 C78 98 82 90 90 88 C96 90 98 98 96 108Z", shadow=False, line=False)
        d.limb("hero", "M84 100 L82 112", 6)
        d.limb("hero", "M98 102 L100 112", 6)
        d.shape("hero", leaf(76, 62, 12, 5, -130), shadow=False)
        d.shape("hero", leaf(96, 60, 12, 5, -50), shadow=False)
        d.shape("light", "M86 58 C96 58 102 64 102 72 C102 80 96 86 90 90 C88 92 86 92 84 90 C78 86 72 80 72 72 "
                         "C72 64 78 58 86 58Z")
        d.marks("mark", "M76 68 C80 66 86 70 86 74 C84 78 80 78 77 75Z M96 68 C92 66 86 70 86 74 C88 78 92 78 95 75Z")
        d.shape("mark", "M84 74 C85 72 88 72 89 74 L89 86 C88 90 85 90 84 86Z", shadow=False)
        d.marks("eye", circle(80.5, 72, 2) + circle(91.5, 72, 2))
    group(d, "translate(100 112) scale(1.3) translate(-92 -110)", lemur)
    d.band("ground", hills(176, 4))
    d.band("deep", hills(190, 4, 30), line=False)


# ================================================================ SHOEBILL
def shoebill_head(d: Drawing):
    for x, y, a in [(-4, 160, -40), (8, 190, -70), (204, 160, -140), (192, 190, -110)]:
        d.shape("near", leaf(x, y, 60, 10, a), line=False)
    d.disc("glow", 160, 50, 22)
    d.shape("hero", "M30 210 C30 170 44 140 64 124 L96 124 C92 150 96 180 104 210Z")
    d.shape("hero", "M38 70 C30 64 28 56 32 50 C36 56 42 58 48 58Z")
    d.shape("hero", "M40 90 C40 66 58 50 80 50 C98 50 110 60 112 76 L112 120 C100 136 74 140 58 132 C46 124 40 108 40 90Z")
    # the huge clog-shaped bill with its hooked tip
    d.shape("bill", "M100 68 C132 64 160 72 178 94 C182 100 182 110 174 112 L168 106 C160 120 132 128 104 126 "
                    "C96 112 94 82 100 68Z", spot=True)
    d.shape("bill2", "M174 112 C182 110 182 100 178 94 C176 100 172 104 168 106Z", shadow=False, line=False)
    d.stroke("mark", "M104 104 C130 108 152 106 168 106", 1.8)
    d.marks("bill2", ellipse(124, 84, 4, 3) + ellipse(140, 90, 3, 2.4) + ellipse(118, 116, 3, 2.4) + ellipse(150, 114, 3, 2))
    d.marks("eye", circle(78, 82, 7.5))
    d.marks("mark", circle(78, 82, 3.4))
    d.stroke("mark", "M68 74 Q78 68 90 74", 2)


SHOEBILL = ("M70 92 C66 78 72 66 84 64 C96 62 104 72 104 84 L104 92 C108 110 112 128 108 140 "
            "C100 152 80 152 72 144 C62 132 60 110 70 92Z")


def shoebill_swamp(d: Drawing):
    d.disc("glow", 50, 56, 22)
    d.band("far", hills(124, 6))
    for x, y in [(160, 70), (182, 86), (24, 92), (140, 96)]:
        d.stroke("reed", f"M{x} 200 L{x} {y}", 2.6)
        d.shape("reed", f"M{x} {y} L{x - 14} {y - 10} L{x - 6} {y - 16} L{x} {y - 18} L{x + 6} {y - 16} L{x + 14} {y - 10}Z",
                shadow=False)
    d.band("water", waves(150, 3, 30))

    def bird():
        d.limb("leg", "M84 146 L82 178 M96 146 L98 178", 4)
        d.shape("hero", "M76 96 C70 120 74 148 90 152 C104 154 116 140 116 120 C116 104 108 92 96 90Z")
        d.shape("hero2", "M110 104 C118 112 120 130 114 144 C108 138 106 120 110 104Z", shadow=False, line=False)
        d.limb("hero", "M86 96 L88 66", 12)
        d.shape("hero", "M74 46 C70 42 70 36 74 32 C76 36 78 38 82 40Z")
        d.shape("hero", "M74 54 C74 42 82 36 92 36 C100 36 106 42 106 50 L106 60 C100 70 86 72 80 68 C76 64 74 60 74 54Z")
        d.shape("bill", "M100 44 C116 42 128 48 136 58 C138 62 138 66 134 66 L132 64 C126 70 112 72 102 70 "
                        "C98 62 98 50 100 44Z", spot=True)
        d.stroke("mark", "M102 62 C114 64 124 64 132 64", 1.4)
        d.marks("eye", circle(90, 50, 3.6))
        d.marks("mark", circle(90, 50, 1.6))
    group(d, "translate(100 176) scale(1.18) translate(-92 -176)", bird)
    d.band("water2", waves(176, 3, 34))
    ripples(d, [(40, 168, 1), (150, 166, 1.2), (110, 188, 1)])
    for x, y in [(12, 130), (196, 120)]:
        d.stroke("reed", f"M{x} 210 L{x} {y}", 2.6)
        d.shape("reed", f"M{x} {y} L{x - 14} {y - 10} L{x - 6} {y - 16} L{x} {y - 18} L{x + 6} {y - 16} L{x + 14} {y - 10}Z",
                shadow=False)


# ================================================================ VULTURE
def vulture_head(d: Drawing):
    d.disc("glow", 100, 100, 78, line=False)
    d.band("far", hills(176, 5), line=False)
    # hunched brown body and folded wings
    d.shape("hero", "M30 210 C26 166 46 130 80 120 L130 120 C160 130 176 166 172 210Z")
    d.stroke("hero2", "M48 170 Q70 160 88 168 M118 168 Q136 160 156 170 M56 190 Q76 180 94 188", 2.2, line=False)
    # fluffy white ruff
    d.shape("light", scallop(102, 126, 36, 14, 0.14, ry=18))
    # bare neck and head, facing left, with the big hooked beak
    d.limb("skin", "M108 122 C112 104 108 90 100 78", 16)
    d.shape("skin", "M76 62 C80 48 96 42 108 48 C118 54 120 68 112 78 C104 86 92 88 84 84Z")
    d.shape("skin2", "M110 80 C118 86 120 96 114 104 C110 96 106 90 104 84Z", shadow=False, line=False)
    d.shape("beak", "M86 58 C74 56 60 60 52 70 C46 76 46 86 52 90 C52 84 56 80 60 80 L68 82 C76 82 84 78 88 72Z", spot=True)
    d.shape("mark", "M80 58 C84 56 90 58 92 62 L88 74 C84 76 80 72 80 68Z", shadow=False)
    d.marks("mark", ellipse(70, 66, 2, 1.4))
    d.marks("light", circle(98, 62, 3.6))
    d.marks("mark", circle(98, 62, 2))
    d.stroke("mark", "M92 56 Q100 52 106 58", 1.6)


VULTURE = ("M58 92 C56 76 66 64 80 64 C96 64 108 76 110 96 C112 116 106 134 96 146 L90 160 L76 160 L72 146 "
           "C62 132 58 114 58 92Z")


def vulture(d: Drawing, k=1):
    def v():
        d.shape("hero", VULTURE)
        d.shape("hero2", "M70 80 C82 76 96 82 102 96 C104 112 100 126 92 140 C88 126 80 106 70 80Z", shadow=False, line=False)
        d.shape("light", scallop(78, 66, 13, 9, 0.16, ry=7), shadow=False)
        d.limb("skin", "M78 64 C76 54 70 48 62 46", 6, shadow=False)
        d.shape("skin", ellipse(60, 46, 7, 6), shadow=False)
        d.shape("beak", "M54 44 C48 44 44 48 44 54 C46 52 50 52 54 52Z", shadow=False)
        d.marks("mark", circle(60, 44, 1.4))
    group(d, f"translate({100 - 100 * k} 0) scale({k} 1)", v)


def vulture_tree(d: Drawing):
    d.disc("glow", 118, 120, 46)
    d.band("far", hills(156, 6))
    # a dead acacia: bare branches to perch on
    d.limb("dark", "M98 210 L98 140 C98 124 90 114 70 104 M98 150 C106 132 124 122 150 116 M84 112 L60 106 "
                   "M128 120 L148 104 M74 106 L64 92", 7)
    group(d, "translate(26 22) scale(.62)", lambda: vulture(d))
    group(d, "translate(54 40) scale(.62)", lambda: vulture(d, -1))
    # one soaring overhead, primaries spread like fingers
    soar = ("M100 60 C88 52 70 48 50 50 L42 46 L44 52 L36 50 L40 56 L34 56 L40 61 C60 62 82 66 94 70 L98 76 L102 76 "
            "L106 70 C118 66 140 62 160 61 L166 56 L160 56 L164 50 L156 52 L158 46 L150 50 C130 48 112 52 100 60Z")
    group(d, "translate(108 22) scale(.5)", lambda: (d.shape("hero", soar), d.shape("light", ellipse(100, 58, 5, 3.4), shadow=False)))
    d.band("ground", hills(178, 4))
    grass(d, -10, 210, 182, 12, "near", 20)


# ================================================================ NILE CROCODILE
def croc_head(d: Drawing, plover=True):
    # open jaws, side-on, facing right
    d.shape("mouth", "M60 116 C100 100 140 84 176 70 L178 128 C140 130 100 128 60 122Z")
    d.shape("light", "M78 108 l4 7 l3 -8 l4 7 l3 -8 l4 7 l3 -8 l4 7 l3 -8 l4 7 l3 -9 l4 7 l3 -9 l4 7 l3 -9 l4 7 l3 -9 l4 6 "
                     "l3 -9 l4 6 l3 -9 l4 6 l3 -9 l4 6 l3 -9 l4 6 L176 72Z", shadow=False)
    d.shape("light", "M80 124 l4 -7 l3 8 l4 -7 l3 8 l4 -7 l3 8 l4 -7 l3 8 l4 -7 l3 8 l4 -7 l3 8 l4 -7 l3 8 l4 -7 l3 8 l4 -7 "
                     "l3 8 l4 -7 l3 8 l4 -7 l3 8 l4 -7 l3 8 l4 -6 L178 128Z", shadow=False)
    # lower jaw
    d.shape("hero", "M10 150 C30 140 56 126 70 122 C100 128 140 130 176 126 C186 128 188 136 182 140 "
                    "C150 148 110 152 70 154 C50 160 30 168 10 172Z")
    d.shape("hero2", "M40 152 C60 142 80 138 110 140 C140 140 160 138 180 138 C160 146 120 150 80 152 C60 154 50 158 40 160Z",
            shadow=False, line=False)
    # upper jaw and head, eye bump on top
    d.shape("hero", "M-10 128 C10 110 34 96 52 92 C58 80 72 76 80 84 C110 76 146 66 174 58 C184 56 190 62 188 68 "
                    "C186 74 180 74 176 72 C140 84 100 100 64 118 C44 124 20 132 -10 142Z")
    d.shape("hero", circle(70, 82, 10), shadow=False)
    d.shape("eye", ellipse(70, 81, 6, 5), shadow=False, spot=True)
    d.marks("mark", ellipse(70, 81, 1.4, 4.4))
    d.marks("mark", circle(182, 62, 2) + circle(178, 64, 1.6))
    d.marks("mark", "M20 120 l6 -10 l6 8Z M36 110 l6 -10 l6 8Z M2 130 l6 -10 l6 8Z")
    d.stroke("mark", "M96 92 l6 -4 M116 84 l6 -4 M136 78 l6 -4 M92 142 l6 4 M116 144 l6 4", 1.6, line=False)
    if plover:
        # an Egyptian plover hopping in to pick the teeth
        def bird():
            d.stroke("mark", "M-2 6 L-3 13 M3 6 L4 13", 1.4)
            d.shape("bird", "M-12 0 C-12 -8 -4 -12 4 -12 C10 -12 14 -8 14 -4 L20 -3 L14 0 C12 6 4 8 -2 8 L-14 6Z")
            d.marks("light", "M-4 2 C0 6 8 6 12 0 C10 6 2 8 -2 8Z")
            d.marks("mark", "M-2 -12 C4 -14 12 -10 14 -6 L4 -6 C0 -8 -2 -10 -2 -12Z M0 0 L12 -2 L12 1 L0 3Z")
            d.marks("light", "M2 -8 L14 -6 L14 -5 L2 -6Z")
        group(d, "translate(134 108) scale(1.1)", bird)


def croc_plover(d: Drawing):
    d.disc("glow", 46, 50, 26)
    d.band("far", hills(170, 5), line=False)
    group(d, "translate(100 110) scale(1.04) translate(-96 -110)", croc_head)
    d.band("water", waves(166, 4, 30))
    ripples(d, [(30, 180, 1.2), (130, 184, 1.4)])
    d.band("deep", waves(190, 3, 34), line=False)


def felucca(d: Drawing, x, y, s=1.0):
    def b():
        d.shape("dark", "M-18 0 L18 0 L14 6 L-14 6Z")
        d.stroke("dark", "M0 0 L0 -26", 1.6)
        d.shape("light", "M-2 -2 L-16 -2 L4 -40 C8 -30 6 -14 -2 -2Z")
    group(d, f"translate({x} {y}) scale({s})", b)


def croc_nile(d: Drawing):
    d.disc("glow", 100, 70, 30)
    d.band("far", hills(98, 4))
    from_x = [(22, 94, 46, 4), (40, 96, 38, -4), (176, 94, 44, -6)]
    for x, y, h, lean in from_x:
        palm(d, x, y, h, lean, "dark", 0.62)
    d.band("water", waves(102, 3, 30))
    felucca(d, 130, 112, 0.9)
    ripples(d, [(30, 118, 1), (84, 124, 1.2)])
    d.band("water2", waves(128, 3, 34), line=False)
    # sandbank and the basking croc, jaws agape to cool off
    d.shape("ground", "M-30 230 L-30 160 C20 140 90 134 150 140 C190 144 220 156 230 166 L230 230Z")

    def croc():
        d.limb("hero", "M70 156 L60 168 L50 168", 8)
        d.limb("hero", "M124 154 L134 166 L146 166", 8)
        d.shape("hero", "M-10 160 C20 150 50 142 76 140 C96 138 112 138 126 138 L136 132 L176 116 "
                        "C182 114 186 120 180 124 L146 140 L184 140 C190 142 188 148 182 148 L140 150 "
                        "C126 158 104 160 80 160 C50 162 20 166 -10 170Z")
        d.shape("mouth", "M138 134 L176 118 C182 116 184 120 180 122 L146 138 L180 140 C184 140 184 144 180 144 L142 146Z",
                shadow=False, line=False)
        d.shape("hero2", "M10 164 C40 158 80 156 110 156 L140 150 C126 158 104 160 80 160 C50 162 30 164 10 166Z",
                shadow=False, line=False)
        d.shape("hero", circle(132, 132, 6), shadow=False)
        d.marks("eye", ellipse(132, 131, 3, 2.4))
        d.marks("mark", "M30 150 l4 -7 l4 7Z M46 146 l4 -7 l4 7Z M62 143 l4 -7 l4 7Z M78 141 l4 -7 l4 7Z M94 140 l4 -7 l4 7Z "
                        "M110 140 l4 -6 l4 6Z")
    group(d, "translate(96 150) scale(1.08) translate(-96 -150)", croc)
    d.band("deep", hills(188, 4, 30), line=False)


# ================================================================ colours
LION_C = {"hero": "#E0A458", "hero2": "#8A4A22", "mane2": "#B8702E", "mark": "#3B2A20", "light": "#F8E9CF",
          "eye": "#F2B33D", "nose": "#B5624A"}
LEOPARD_C = {"hero": "#E8B04B", "mark": "#3A2414", "light": "#FBF1DC", "eye": "#9CC43A", "nose": "#C8806E"}
CHEETAH_C = {"hero": "#E8BA62", "hero2": "#CF9C48", "mark": "#2D2219", "light": "#FBF1DC", "eye": "#E9A93A",
             "nose": "#3A2A20"}
AFELE = {"hero": "#858079", "hero2": "#BDB6AC", "mark": "#3A3532", "light": "#F4EAD2", "pop": "#C9787A"}
AFELE_KILI = {"hero": "#8D99AE", "hero2": "#A9B3C3", "mark": "#2B2D42", "light": "#FFFFFF"}
GIRAFFE_C = {"leaf": "#7FA650", "hero": "#F2C46A", "hero2": "#E8D5A8", "mark": "#9A5530", "tongue": "#5B4A78"}
GIRAFFE_D = {"hero": "#F2C46A", "mark": "#9A5530", "water": "#7CC6E8"}

ZEBRA_C = {"hero": "#FBF7EE", "mark": "#24262E", "muzzle": "#3A3A40", "foal": "#6E4E3A", "light": "#FFFFFF"}
RHINO_C = {"hero": "#9A948C", "hero2": "#C9A6A0", "horn": "#C7B497", "mark": "#3A3532", "bird": "#7A5A3A",
           "pop": "#E0402E", "eye": "#F2C14E"}
HIPPO_C = {"hero": "#7E6F7C", "hero2": "#C98F98", "mouth": "#E7929C", "tongue": "#C9667A", "mark": "#2E2430",
           "light": "#FBF3E4", "water": "#5FA8C6", "reed": "#5E7A3A"}
HIPPO_R = {"hero": "#6E606E", "hero2": "#B88690", "mark": "#2E2430", "egret": "#FFFFFF", "bill": "#F2B33D",
           "water": "#5FA8C6", "water2": "#3F86A8", "reed": "#4E6A30"}
BUFFALO_C = {"hero": "#3E3836", "hero2": "#6A625D", "horn": "#8C8178", "horn2": "#A69A8E", "mark": "#1E1A18",
             "light": "#F4EAD8", "bird": "#7A5A3A", "pop": "#E0402E", "eye": "#F2C14E"}
BUFFALO_M = {**BUFFALO_C, "egret": "#FFFFFF", "bill": "#F2B33D", "water": "#7CB8D0"}
GNU_C = {"hero": "#6F6C74", "mark": "#2A2628", "horn": "#3A3436", "light": "#FFFFFF"}
GNU_X = {**GNU_C, "water": "#A8916A", "water2": "#93795A", "light": "#FBF6EC", "bank": "#E6CC9C", "horn": "#2A2426"}

HYENA_C = {"hero": "#B89A72", "mark": "#3A2C22", "muzzle": "#4A3A30", "mouth": "#7A2E2E", "light": "#FBF3E4"}
WDOG_C = {"hero": "#C99A55", "hero2": "#A87C40", "mark": "#2A221C", "light": "#F4E8CF", "eye": "#C98A3A"}
MEERKAT_C = {"hero": "#C9A27A", "hero2": "#ECDAC0", "mark": "#3A2A20", "light": "#FFFFFF"}
CHIMP_C = {"hero": "#2E2622", "face": "#D8B49A", "face2": "#B98C74", "mark": "#1A1412", "light": "#FFFFFF",
           "mound": "#B9764A", "dark": "#3A2A20"}
WARTHOG_C = {"hero": "#8A7468", "hero2": "#B08A7A", "mane": "#4A3628", "mark": "#2A1E18", "light": "#F4EAD2"}

OSTRICH_C = {"hero": "#D9B3A3", "hero2": "#B88E7E", "bill": "#E8B07A", "mark": "#2A2224", "dark": "#2A2426",
             "light": "#FFFFFF", "leg": "#E3A592"}
LEMUR_C = {"hero": "#9E9894", "hero2": "#F6F2EC", "light": "#F6F2EC", "mark": "#232023", "eye": "#F2A21E",
           "branch": "#6B4A32"}
SHOEBILL_C = {"hero": "#8C9CAA", "hero2": "#6F7F8E", "bill": "#C9B48A", "bill2": "#8F7B58", "eye": "#F2EAC0",
              "mark": "#2A2E33", "leg": "#3A3A3C", "water": "#6FB0C4", "water2": "#4F94AA", "reed": "#5E8A3A"}
VULTURE_C = {"hero": "#5E4636", "hero2": "#7A5E48", "light": "#F7F1E6", "skin": "#D9827A", "skin2": "#C0625C",
             "beak": "#E8D9B8", "mark": "#231A16"}
CROC_C = {"hero": "#6E7F3E", "hero2": "#C9C27A", "mark": "#2E3818", "mouth": "#EBA9A2", "light": "#FFFBEE",
          "eye": "#E8C23A", "bird": "#9A9A92", "water": "#5FA8BE"}
CROC_N = {**CROC_C, "water": "#5FA8BE", "water2": "#4C94AA", "light": "#FFFFFF"}

SAVANNA_FIX = {"glow": ["glow2", "light", "#E07A5F", "far"], "sky": ["sky2", "far"]}

CONCEPTS = [
    Concept("lion-mane", "animal-lion", "Lion's mane", lion_face, overrides=LION_C,
            checks=[("hero2", "glow"), ("hero2", "sky"), ("hero", "hero2")],
            fixes={"glow": ["glow2", "far", "light"]}),
    Concept("lion-long-grass", "animal-lion", "Lion in the long grass", lion_savanna, overrides=LION_C,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero", "ground"), ("hero2", "glow"), ("hero", "far")],
            fixes={"glow": ["glow2", "light", "#E07A5F"], "ground": ["near", "mid", "deep"], "far": ["mid", "near"]}),
    Concept("leopard-face", "animal-leopard", "Leopard eyes", leopard_face, overrides=LEOPARD_C,
            checks=[("hero", "sky"), ("hero", "near")], fixes={"near": ["deep", "mid", "dark"], "sky": ["sky2"]}),
    Concept("leopard-kopje", "animal-leopard", "Leopard on the rocks", leopard_kopje, overrides=LEOPARD_C,
            checks=[("hero", "near"), ("hero", "sky"), ("hero", "far"), ("hero", "mid")],
            fixes={"near": ["deep", "dark"], "far": ["mid", "sky2"], "mid": ["near", "far"]}),
    Concept("cheetah-tears", "animal-cheetah", "Cheetah face", cheetah_face, overrides=CHEETAH_C,
            checks=[("hero", "glow"), ("hero", "sky")], fixes={"glow": ["glow2", "far", "#E07A5F", "near"]}),
    Concept("cheetah-sprint", "animal-cheetah", "Cheetah sprint", cheetah_sprint, overrides=CHEETAH_C,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "mid"), ("hero", "glow")],
            fixes={"far": ["near", "mid", "deep"], "mid": ["near", "deep"], "glow": ["glow2", "#E07A5F"], "sky": ["sky2"]}),
    Concept("african-elephant-trumpet", "animal-african-elephant", "Trumpeting elephant", elephant_trumpet, overrides=AFELE,
            checks=[("hero", "sky"), ("hero2", "hero"), ("hero", "glow")], fixes={"glow": ["glow2", "far"]}),
    Concept("african-elephant-kilimanjaro", "animal-african-elephant", "Under Kilimanjaro", elephant_kilimanjaro,
            overrides=AFELE_KILI, checks=[("hero", "far"), ("hero", "mid"), ("light", "sky"), ("far", "sky")],
            fixes={"far": ["mid", "near"], "mid": ["ground", "near"], "sky": ["sky2", "glow2"]}),
    Concept("giraffe-browse", "animal-giraffe", "Giraffe browsing", giraffe_head, overrides=GIRAFFE_C,
            checks=[("hero", "sky"), ("hero", "glow")], fixes={"glow": ["#E07A5F", "#C8553D", "near"], "sky": ["sky2", "far"]}),
    Concept("giraffe-drink", "animal-giraffe", "Giraffe at the waterhole", giraffe_drink, overrides=GIRAFFE_D,
            checks=[("hero", "sky"), ("hero", "mid"), ("hero", "water"), ("hero", "far"), ("hero", "ground")],
            fixes={"mid": ["near", "deep"], "far": ["near", "mid"], "ground": ["near", "deep"], "sky": ["sky2"]}),
    Concept("zebra-face", "animal-zebra", "Zebra face", zebra_face, overrides=ZEBRA_C,
            checks=[("hero", "glow"), ("hero", "glow2"), ("hero", "far")],
            fixes={"glow": ["mid", "near", "#E07A5F"], "glow2": ["near", "mid", "deep"], "far": ["near", "deep"]}),
    Concept("zebra-foal", "animal-zebra", "Zebra & foal", zebra_foal, overrides=ZEBRA_C,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero", "far"), ("hero", "mid")],
            fixes={"glow": ["glow2", "near", "#E07A5F"], "sky": ["sky2", "far"], "far": ["mid", "near"], "mid": ["near", "deep"]}),
    Concept("rhino-horns", "animal-rhino", "Rhino horns", rhino_head, overrides=RHINO_C,
            checks=[("hero", "sky"), ("hero", "glow"), ("horn", "sky"), ("horn", "hero")], fixes={"glow": ["glow2", "#E07A5F", "far"], "sky": ["sky2", "far"]}),
    Concept("rhino-oxpecker", "animal-rhino", "Rhino & oxpecker", rhino_oxpecker, overrides=RHINO_C,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "mid"), ("hero", "ground"), ("bird", "sky")],
            fixes={"far": ["near", "mid"], "mid": ["near", "deep"], "ground": ["near", "deep"], "sky": ["sky2"]}),
    Concept("hippo-yawn", "animal-hippo", "Hippo yawn", hippo_yawn, [p for p in ("golden", "coastal", "meadow", "blush", "dusk")], HIPPO_C,
            checks=[("hero", "sky"), ("hero", "water"), ("mouth", "sky")], fixes={"sky": ["sky2", "glow2"]}),
    Concept("hippo-river", "animal-hippo", "Hippos at sunset", hippo_river, overrides=HIPPO_R,
            checks=[("hero", "water"), ("hero", "glow"), ("egret", "hero"), ("glow", "sky")],
            fixes={"glow": ["glow2", "#E07A5F", "pop"]}),
    Concept("cape-buffalo-boss", "animal-cape-buffalo", "Buffalo horns", buffalo_face, overrides=BUFFALO_C,
            checks=[("hero", "glow"), ("hero", "sky"), ("horn", "glow")], fixes={"glow": ["glow2", "far", "light"], "sky": ["glow2", "light"]}),
    Concept("cape-buffalo-marsh", "animal-cape-buffalo", "Buffalo & egrets", buffalo_marsh, overrides=BUFFALO_M,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "mid"), ("hero", "water")],
            fixes={"far": ["mid", "sky2", "ground"], "mid": ["far", "ground", "glow2"], "sky": ["glow2", "light"]}),
    Concept("wildebeest-head", "animal-wildebeest-migration", "Wildebeest", gnu_head, overrides=GNU_C,
            checks=[("hero", "sky"), ("hero", "glow"), ("hero", "far")], fixes={"glow": ["glow2", "far", "#E07A5F"], "far": ["ground", "mid"], "sky": ["sky2", "glow2"]}),
    Concept("wildebeest-crossing", "animal-wildebeest-migration", "River crossing", gnu_crossing, overrides=GNU_X,
            checks=[("hero", "sky"), ("hero", "water"), ("hero", "bank"), ("dark", "far"), ("bank", "water")],
            fixes={"sky": ["sky2", "glow2"], "far": ["mid", "ground"]}),
    Concept("hyena-grin", "animal-hyena", "Laughing hyena", hyena_face, overrides=HYENA_C,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero", "mid")], fixes={"glow": ["glow2", "far", "light", "#E07A5F"], "mid": ["near", "deep"]}),
    Concept("hyena-dusk", "animal-hyena", "Hyena at dusk", hyena_dusk, overrides=HYENA_C,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero", "far"), ("hero", "mid"), ("hero", "ground")],
            fixes={"glow": ["glow2", "light", "#E07A5F"], "far": ["near", "deep", "mid"], "mid": ["near", "deep"], "ground": ["near", "deep"]}),
    Concept("african-wild-dog-ears", "animal-african-wild-dog", "Wild dog", wilddog_face, overrides=WDOG_C,
            checks=[("hero", "glow"), ("hero", "sky"), ("mark", "glow")], fixes={"glow": ["glow2", "light", "far", "#E07A5F"]}),
    Concept("african-wild-dog-pack", "animal-african-wild-dog", "Painted wolves", wilddog_pack, overrides=WDOG_C,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "mid"), ("hero", "ground")],
            fixes={"far": ["near", "deep"], "mid": ["near", "deep"], "ground": ["near", "deep"], "sky": ["sky2"]}),
    Concept("meerkat-sentry", "animal-meerkat", "Meerkat on guard", meerkat_sentry, overrides=MEERKAT_C,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero2", "hero")], fixes={"glow": ["far", "mid", "near", "#E07A5F"]}),
    Concept("meerkat-family", "animal-meerkat", "Meerkat lookout", meerkat_family, overrides=MEERKAT_C,
            checks=[("hero", "sky"), ("hero", "ground"), ("hero", "far"), ("hero", "mid")],
            fixes={"ground": ["near", "deep"], "far": ["near", "mid", "deep"], "mid": ["near", "deep"], "sky": ["sky2"]}),
    Concept("chimpanzee-face", "animal-chimpanzee", "Chimpanzee", chimp_face, overrides=CHIMP_C,
            checks=[("hero", "sky"), ("hero", "near"), ("face2", "hero")], fixes={"near": ["mid", "far"]}),
    Concept("chimpanzee-termites", "animal-chimpanzee", "Termite fishing", chimp_termites, overrides=CHIMP_C,
            checks=[("hero", "far"), ("hero", "mid"), ("hero", "sky"), ("mound", "mid"), ("mound", "far")],
            fixes={"mid": ["far", "ground", "glow2"], "far": ["sky2", "glow2", "mid"]}),
    Concept("warthog-tusks", "animal-warthog", "Warthog", warthog_face, overrides=WARTHOG_C,
            checks=[("hero", "glow"), ("hero", "sky"), ("light", "glow")], fixes={"glow": ["mid", "near", "far", "#E07A5F"]}),
    Concept("warthog-tails-up", "animal-warthog", "Tails up!", warthog_run, overrides=WARTHOG_C,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "mid"), ("hero", "ground")],
            fixes={"far": ["near", "mid", "deep"], "mid": ["near", "deep", "far"], "ground": ["near", "deep"], "sky": ["sky2"]}),
    Concept("ostrich-eyelashes", "animal-ostrich", "Ostrich", ostrich_head, overrides=OSTRICH_C,
            checks=[("hero", "sky"), ("hero", "glow"), ("dark", "far")], fixes={"glow": ["glow2", "far", "#E07A5F"], "sky": ["sky2", "far"]}),
    Concept("ostrich-run", "animal-ostrich", "Ostrich on the run", ostrich_run, overrides=OSTRICH_C,
            checks=[("dark", "sky"), ("dark", "far"), ("dark", "mid"), ("leg", "ground"), ("leg", "sky"), ("leg", "mid")],
            fixes={"far": ["mid", "ground"], "mid": ["far", "near", "deep"], "ground": ["near", "deep"], "sky": ["sky2"]}),
    Concept("lemur-tail", "animal-lemur", "Ring-tailed lemur", lemur_face, overrides=LEMUR_C,
            checks=[("hero2", "glow"), ("hero", "glow"), ("hero2", "sky"), ("hero", "sky")],
            fixes={"glow": ["mid", "near", "#E07A5F"], "sky": ["far", "mid", "near"]}),
    Concept("lemur-baobabs", "animal-lemur", "Lemur & baobabs", lemur_baobab, overrides=LEMUR_C,
            checks=[("hero", "glow"), ("hero2", "glow"), ("hero", "sky"), ("hero2", "sky"), ("branch", "glow")],
            fixes={"glow": ["mid", "near", "#E07A5F", "far"], "sky": ["sky2", "far"]}),
    Concept("shoebill-bill", "animal-shoebill", "Shoebill", shoebill_head, overrides=SHOEBILL_C,
            checks=[("hero", "sky"), ("bill", "sky"), ("bill", "glow"), ("hero", "near")],
            fixes={"glow": ["glow2", "#E07A5F", "far"], "sky": ["sky2", "far"], "near": ["deep", "mid"]}),
    Concept("shoebill-swamp", "animal-shoebill", "Shoebill in the swamp", shoebill_swamp, overrides=SHOEBILL_C,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "water"), ("bill", "sky"), ("bill", "far")],
            fixes={"far": ["mid", "near", "ground"], "sky": ["sky2"]}),
    Concept("vulture-ruff", "animal-vulture", "Vulture", vulture_head, overrides=VULTURE_C,
            checks=[("skin", "glow"), ("hero", "glow"), ("light", "glow"), ("beak", "glow")],
            fixes={"glow": ["far", "mid", "near", "glow2", "#7FA7C9"]}),
    Concept("vulture-tree", "animal-vulture", "Vultures at sunset", vulture_tree, overrides=VULTURE_C,
            checks=[("hero", "glow"), ("hero", "sky"), ("dark", "glow"), ("hero", "far")],
            fixes={"glow": ["glow2", "light", "#E07A5F"], "far": ["mid", "ground"]}),
    Concept("nile-crocodile-plover", "animal-nile-crocodile", "Croc & plover", croc_plover, overrides=CROC_C,
            checks=[("hero", "sky"), ("hero", "glow"), ("hero", "water"), ("mouth", "sky")],
            fixes={"glow": ["glow2", "#E07A5F"], "sky": ["sky2", "far"], "water": ["#2F7F9A", "deep"]}),
    Concept("nile-crocodile-felucca", "animal-nile-crocodile", "Basking on the Nile", croc_nile, overrides=CROC_N,
            checks=[("hero", "ground"), ("hero", "water2"), ("light", "water"), ("dark", "sky")],
            fixes={"ground": ["#E8D5A6", "glow2", "far"]}),
]
