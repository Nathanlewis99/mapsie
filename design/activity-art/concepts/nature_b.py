"""Nature B: three concepts each for thirteen wildlife, garden and landscape activities."""
import math

from _common import Concept, Drawing, cloud, fish, circle, ellipse, waves, hills, rrect, group, acacia  # noqa: F401

_uid = [0]


# ================================================================ private helpers (copied from wildlife.py)
def _id(prefix):
    _uid[0] += 1
    return f"{prefix}{_uid[0]}"


def clipped(d: Drawing, path: str, fn):
    """Draw fn() clipped to `path`."""
    cid = _id("natbclip")
    tag = f'<clipPath id="{cid}"><path d="{path}"/></clipPath><g clip-path="url(#{cid})">'
    d.raw(tag, tag)
    fn()
    d.raw("</g>", "</g>")


def flip(d: Drawing, fn, cx=100):
    group(d, f"translate({2 * cx} 0) scale(-1 1)", fn)


def scallop(cx, cy, r, n=12, bump=0.22, rot=0.0, ry=None):
    """A bumpy circle (or ellipse): manes, tree crowns, flower clusters."""
    ry = r if ry is None else ry
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
    x, i = x0, 0
    while x < x1:
        k = h * (0.75 + 0.25 * ((i * 5) % 3) / 2)
        d.shape(role, f"M{x} {y} L{x + 2} {y - k * 0.7} L{x + 4} {y - 2} L{x + 6} {y - k} L{x + 8} {y - 2} "
                      f"L{x + 10} {y - k * 0.6} L{x + 12} {y}Z", shadow=False, line=line)
        x += step
        i += 1


def pine(d: Drawing, x, y, h, role="near", shadow=True, line=True):
    w = h * 0.36
    d.shape(role, f"M{x} {y - h} L{x + w * 0.6} {y - h * 0.62} L{x + w * 0.35} {y - h * 0.62} L{x + w * 0.85} {y - h * 0.3} "
                  f"L{x + w * 0.5} {y - h * 0.3} L{x + w} {y - h * 0.06} L{x - w} {y - h * 0.06} L{x - w * 0.5} {y - h * 0.3} "
                  f"L{x - w * 0.85} {y - h * 0.3} L{x - w * 0.35} {y - h * 0.62} L{x - w * 0.6} {y - h * 0.62}Z",
            shadow=shadow, line=line)


def mist(d: Drawing, y, amp=3, step=40, opacity=".55"):
    d.raw(f'<g opacity="{opacity}">', "")
    d.band("light", waves(y, amp, step), shadow=False, line=False)
    d.raw("</g>", "")


def stars(d: Drawing, pts, role="light"):
    for x, y, r in pts:
        d.marks(role, circle(x, y, r))


def pt(x, y):
    return f"{x:.1f} {y:.1f}"


# ================================================================ WALKING SAFARI
RHINO = ("M62 92 C70 80 84 74 98 76 C112 72 130 72 146 78 C164 84 174 98 172 116 C171 126 167 132 163 136 "
         "L163 160 L149 160 L147 140 C142 142 138 142 134 142 L133 160 L119 160 L117 140 L100 140 L98 160 L84 160 "
         "L82 138 C78 136 76 134 74 136 L73 158 L59 158 L60 132 C58 128 58 124 60 120Z")
RHINO_HEAD = ("M76 88 C64 86 52 92 44 102 L28 120 C24 126 22 132 28 137 C34 141 46 141 54 139 C64 137 74 131 78 125 "
              "C84 115 84 96 76 88Z")


def walksafari_rhino(d: Drawing):
    d.disc("glow", 128, 70, 34)
    birds(d, [(40, 48, 1), (56, 40, 0.8)])
    d.band("far", hills(140, 8))
    acacia(d, -70, 6, 0.55)
    d.stroke("hero", "M170 104 C178 110 180 120 177 128", 2.4)
    d.shape("mark", ellipse(177, 130, 2.4, 4), shadow=False)
    d.shape("hero", RHINO)
    d.shape("hero", RHINO_HEAD)
    d.shape("hero2", "M27 128 L20 88 C20 84 24 84 26 88 L42 120Z", spot=True)
    d.shape("hero2", "M46 112 L45 98 C45 95 49 95 50 98 L56 108Z", spot=True)
    d.shape("hero", "M72 92 L66 76 C70 74 76 80 78 90Z")
    d.shape("hero", "M80 92 L80 76 C84 76 88 84 86 94Z", shadow=False)
    d.marks("mark", circle(62, 104, 2.2))
    d.stroke("mark", "M86 100 C92 110 92 122 86 132 M120 86 C126 96 128 108 126 118", 1.4, line=False)
    # oxpecker on the back
    d.shape("dark", "M130 75 C130 70 134 67 139 68 L147 66 L143 70 C145 72 144 75 141 76 Z")
    d.marks("pop", "M130 71 L125 72 L130 73Z")
    d.band("ground", hills(170, 5))
    grass(d, 6, 60, 172, 12, "near")
    grass(d, 150, 200, 172, 12, "near")
    d.band("deep", hills(188, 4, 30), line=False)


PAW = [(-17, -14, 6.5, 8.5, -18), (-6, -24, 6.5, 8.5, -6), (7, -24, 6.5, 8.5, 6), (18, -14, 6.5, 8.5, 18)]
PAD = "M-15 6 C-16 -6 -8 -10 0 -6 C8 -10 16 -6 15 6 C14 14 8 16 4 13 C2 16 -2 16 -4 13 C-8 16 -14 14 -15 6Z"
BOOT = ("M-11 -26 C-12 -36 -6 -42 2 -42 C10 -42 14 -34 12 -24 C11 -16 8 -10 8 -4 L8 -1 H-8 C-8 -10 -11 -18 -11 -26Z "
        "M-8 6 H8 C9 14 8 22 0 22 C-8 22 -9 14 -8 6Z")


def paw(d: Drawing, x, y, s, rot, role="near"):
    def draw():
        for px, py, rx, ry, a in PAW:
            d.shape(role, ellipse(px, py, rx, ry), extra=f'transform="rotate({a} {px} {py})"', shadow=False, spot=True)
        d.shape(role, PAD, shadow=False, spot=True)
    group(d, f"translate({x} {y}) rotate({rot}) scale({s})", draw)


def boot(d: Drawing, x, y, s, rot, role="near"):
    def draw():
        d.shape(role, BOOT, shadow=False)
        d.stroke("ground", "M-6 -34 H8 M-8 -26 H9 M-7 -18 H8 M-5 -9 H5 M-5 11 H5 M-4 17 H4", 2.4, line=False)
    group(d, f"translate({x} {y}) rotate({rot}) scale({s})", draw)


def walksafari_tracks(d: Drawing):
    d.disc("glow", 52, 44, 15)
    birds(d, [(140, 30, 0.9), (156, 24, 0.7)])
    d.band("far", hills(66, 5))
    acacia(d, 60, -2, 0.5)
    d.band("ground", "M-30 70 Q100 64 230 70")
    d.stroke("mid", "M20 92 q10 -3 20 0 M150 86 q10 -3 20 0 M150 186 q10 -3 20 0 M28 170 q8 -3 16 0", 2, line=False)
    paw(d, 44, 96, 0.55, -20)
    paw(d, 76, 140, 1.3, -14)
    boot(d, 136, 112, 1.0, 12)
    boot(d, 150, 174, 0.85, 18)


def walker(d: Drawing, x, y, s=1.0, rifle=False, pack=True):
    def draw():
        d.limb("dark", "M-2 -22 L-9 0", 5, shadow=False)
        d.limb("dark", "M2 -22 L8 0", 5, shadow=False)
        d.limb("dark", "M0 -34 L-7 -20", 3.6, shadow=False)
        d.limb("dark", "M1 -34 L8 -22", 3.6, shadow=False)
        if pack:
            d.shape("dark", rrect(-11, -40, 7, 15, 2.5), shadow=False)
        d.shape("dark", rrect(-5, -42, 11, 22, 4.5), shadow=False)
        d.shape("dark", circle(1, -47, 4.6), shadow=False)
        d.shape("dark", ellipse(1, -49.5, 8.5, 1.8), shadow=False)
        d.shape("dark", rrect(-3.5, -55, 9, 6, 2.5), shadow=False)
        if rifle:
            d.stroke("dark", "M-3 -38 L-15 -60", 2.6)
        else:
            d.stroke("dark", "M8 -24 L12 0", 1.6)
    group(d, f"translate({x} {y}) scale({s})", draw)


def walksafari_file(d: Drawing):
    d.disc("glow", 100, 112, 58)
    d.disc("glow2", 100, 112, 40, shadow=False, line=False)
    birds(d, [(36, 46, 1), (52, 38, 0.8), (150, 44, 0.9)])
    d.band("far", hills(150, 6))
    acacia(d, -34, 58, 0.45)
    d.band("near", "M-30 148 Q60 136 110 140 T230 150")
    for i, (x, y) in enumerate([(150, 145), (120, 142), (90, 141), (60, 143)]):
        walker(d, x, y, 1.0, rifle=i == 0, pack=i != 0)
    d.band("deep", hills(170, 4, 30))
    grass(d, 0, 200, 172, 10, "deep")
    d.band("dark", hills(188, 4, 10), line=False)


# ================================================================ ORANGUTAN
ORANG = {"hero": "#C2602A", "hero2": "#E39050", "mark": "#2A160C", "face": "#5B4334", "face2": "#8E6C55",
         "leaf": "#4E9A4A", "leaf2": "#2F6E3A"}


def orangutan_face(d: Drawing):
    for a, x, y in [(-150, 30, 150), (-30, 170, 150), (-120, 40, 60), (-60, 160, 60)]:
        d.shape("leaf", leaf(x - 40 * math.cos(math.radians(a)), y - 40 * math.sin(math.radians(a)), 60, 16, a), line=False)
    # long shaggy hair
    d.shape("hero", "M30 200 C30 150 40 112 62 90 C70 62 86 50 100 50 C114 50 130 62 138 90 C160 112 170 150 170 200Z")
    d.shape("hero2", "M48 200 L54 150 L60 196Z M140 200 L146 150 L152 196Z M72 200 L76 160 L82 200Z M118 200 L124 160 L128 200Z",
            shadow=False, line=False)
    # cheek flanges
    d.shape("face", ellipse(100, 108, 64, 40))
    d.stroke("mark", "M46 98 C42 108 42 118 48 128 M154 98 C158 108 158 118 152 128", 1.6, line=False)
    # throat sac
    d.shape("hero2", ellipse(100, 154, 34, 20), spot=True)
    # face
    d.shape("face2", "M100 66 C116 66 126 78 126 94 C126 112 128 128 120 142 C114 152 86 152 80 142 C72 128 74 112 74 94 C74 78 84 66 100 66Z")
    d.shape("face", "M76 90 C84 82 94 84 100 88 C106 84 116 82 124 90 C118 92 108 94 100 94 C92 94 82 92 76 90Z", shadow=False)
    for x in (88, 112):
        d.marks("light", ellipse(x, 100, 5, 4))
        d.marks("mark", circle(x, 100, 3))
    d.marks("light", circle(89, 99, 1) + circle(113, 99, 1))
    d.marks("mark", ellipse(95, 118, 2.2, 3) + ellipse(105, 118, 2.2, 3))
    d.stroke("mark", "M86 134 Q100 140 114 134", 2.2)
    # hair tuft on top
    d.shape("hero", "M78 74 C78 58 90 50 100 50 C110 50 122 58 122 74 C114 66 106 64 100 64 C94 64 86 66 78 74Z")
    d.stroke("hero2", "M90 56 Q94 60 94 66 M100 54 V64 M110 56 Q106 60 106 66", 1.6, line=False)


def orangutan_swing(d: Drawing):
    d.band("far", "M-30 150 Q100 130 230 150")
    for x, w in [(24, 12), (172, 14)]:
        d.shape("far", f"M{x - w / 2} 200 L{x - w / 2 + 2} 0 L{x + w / 2 - 2} 0 L{x + w / 2} 200Z", shadow=False, line=False)
    d.shape("leaf2", scallop(30, 6, 40, 9, 0.15), shadow=False)
    d.shape("leaf2", scallop(176, 10, 42, 9, 0.15), shadow=False)
    # branch
    d.limb("dark", "M-20 46 Q60 34 120 40 T230 30", 9)
    for x, y, a in [(150, 34, -60), (164, 32, 30), (48, 40, 150), (80, 37, -110)]:
        d.shape("leaf", leaf(x, y, 22, 7, a), shadow=False, spot=True)
    # vine
    d.stroke("leaf2", "M156 34 C150 80 160 120 150 200", 2.4)

    # hanging from the branch by both long arms
    d.limb("hero", "M86 90 Q70 66 74 42", 12)
    d.limb("hero", "M114 90 Q132 66 128 40", 12)
    d.shape("face", ellipse(74, 40, 6, 7))
    d.shape("face", ellipse(128, 38, 6, 7))
    for x, k in [(76, -1), (126, 1)]:
        d.shape("hero2", f"M{x} 62 L{x + 9 * k} 70 L{x + 2 * k} 72 L{x + 10 * k} 80 L{x} 80Z", shadow=False, line=False)
    # legs dangling, feet curled
    d.limb("hero", "M92 136 Q76 152 82 172", 11)
    d.limb("hero", "M110 136 Q126 152 120 172", 11)
    d.shape("face", ellipse(82, 175, 7, 5))
    d.shape("face", ellipse(120, 175, 7, 5))
    # shaggy body
    d.shape("hero", "M80 92 C74 112 76 134 90 146 L110 146 C124 134 126 112 120 92 C110 84 90 84 80 92Z")
    d.shape("hero2", "M80 128 L84 150 L90 138 L96 154 L100 140 L106 154 L110 138 L116 150 L120 128Z", shadow=False)
    # head
    d.shape("hero", circle(100, 86, 17))
    d.shape("face2", "M88 80 C88 72 112 72 112 80 C116 90 112 104 100 104 C88 104 84 90 88 80Z")
    d.marks("mark", circle(94, 84, 2) + circle(106, 84, 2))
    d.marks("mark", ellipse(97.5, 92, 1.4, 1.8) + ellipse(102.5, 92, 1.4, 1.8))
    d.stroke("mark", "M94 98 Q100 101 106 98", 1.4)
    d.shape("hero", "M86 74 C88 66 96 64 100 64 C104 64 112 66 114 74 C108 70 92 70 86 74Z", shadow=False)
    d.shape("leaf", leaf(-10, 196, 60, 18, -40), spot=True)
    d.shape("leaf2", leaf(210, 196, 56, 16, -140))


def orangutan_umbrella(d: Drawing):
    d.band("far", hills(130, 10))
    d.shape("leaf2", scallop(16, 112, 30, 8, 0.15), shadow=False)
    d.shape("leaf2", scallop(188, 104, 32, 8, 0.15), shadow=False)
    d.stroke("mid", "M30 40 l-4 10 M60 30 l-4 10 M44 70 l-4 10 M156 40 l-4 10 M176 72 l-4 10 M24 96 l-4 10 "
                    "M168 112 l-4 10 M140 20 l-4 10 M74 16 l-4 10", 2.2)
    # trunk + branch it sits on
    d.limb("dark", "M-20 168 Q100 156 230 166", 12)
    # body sitting
    d.shape("hero", "M66 166 C58 140 66 112 92 106 C116 102 136 116 138 140 C140 156 136 164 132 168Z")
    d.shape("hero2", "M70 160 L66 172 L76 166 L80 176 L86 166 L94 174 L98 164Z", shadow=False)
    d.limb("hero", "M78 150 Q90 170 108 162", 11)
    d.shape("face", ellipse(110, 160, 6, 5))
    # arm up holding the leaf stem
    d.limb("hero", "M122 120 Q134 96 122 76", 9)
    d.shape("face", ellipse(121, 76, 5.5, 6.5))
    d.stroke("leaf2", "M121 82 L118 50", 3)
    # big leaf umbrella
    d.shape("leaf", "M40 64 C46 34 80 18 114 22 C150 26 172 46 176 70 C164 62 152 62 144 70 C134 60 118 58 110 66 "
                    "C100 56 84 56 76 66 C66 58 50 58 40 64Z", spot=True)
    d.stroke("leaf2", "M110 24 Q112 44 110 64 M110 40 L80 30 M110 40 L140 32 M110 54 L70 48 M110 54 L150 48", 1.6, line=False)
    # head
    d.shape("hero", circle(96, 100, 18))
    d.shape("face2", "M84 92 C84 84 108 84 108 92 C112 100 110 116 96 118 C82 116 80 100 84 92Z")
    d.marks("mark", circle(91, 96, 2) + circle(101, 96, 2))
    d.marks("mark", ellipse(96, 106, 3, 1.4))
    d.stroke("mark", "M90 112 Q96 115 102 112", 1.3)
    d.shape("hero", "M84 86 L82 76 L90 82 L96 72 L100 82 L108 76 L106 86Z", shadow=False)


# ================================================================ TURTLE HATCHING
HATCH = {"hero": "#4C4640", "hero2": "#6E655B", "mark": "#2A2622", "egg": "#FBF6EA", "egg2": "#E6DCC8"}


def hatchling_side(d: Drawing):
    """Side-view hatchling facing right, about 90 wide, centred on (100, 100)."""
    d.shape("hero2", "M70 112 C60 120 52 126 48 124 C52 118 58 112 66 106Z")  # back flipper
    d.shape("hero2", "M118 108 C128 124 128 140 120 148 C118 134 112 122 104 114Z", spot=True)  # front flipper
    d.shape("hero", "M56 108 C60 80 86 68 108 72 C124 76 134 90 134 108 Z")  # shell
    d.shape("hero2", "M54 108 H136 C134 114 128 116 120 116 H68 C60 116 56 114 54 108Z", shadow=False)  # plastron edge
    d.stroke("mark", "M72 108 C74 92 82 82 92 78 M96 108 C96 94 98 82 104 76 M118 108 C118 96 114 86 110 80", 1.6, line=False)
    d.shape("hero", "M130 96 C136 88 150 88 156 96 C160 102 156 108 150 108 L134 110Z")  # head
    d.marks("light", circle(146, 96, 2.8))
    d.marks("mark", circle(146.6, 96, 1.6))
    d.stroke("mark", "M150 104 Q154 104 157 101", 1.2, line=False)
    d.shape("hero2", "M110 104 C122 122 138 128 150 126 C140 120 130 112 124 102Z")  # near front flipper


def hatch_egg(d: Drawing):
    d.disc("glow", 46, 48, 16)
    d.band("far", "M-30 72 H230")
    d.band("mid", waves(80, 2.5, 24))
    d.band("light", "M-30 88 Q40 82 100 88 T230 86", shadow=False, line=False)
    d.band("ground", "M-30 92 Q40 86 100 92 T230 90")
    for x, y, r in [(36, 160, 18), (158, 150, 20), (178, 182, 16), (20, 190, 14)]:
        d.shape("egg", circle(x, y, r))
        d.shape("egg2", f"M{x - r * 0.7} {y + r * 0.4} A{r} {r} 0 0 0 {x + r * 0.7} {y + r * 0.4} Q{x} {y + r * 0.7} {x - r * 0.7} {y + r * 0.4}Z", shadow=False, line=False)
    # broken shell pieces
    d.shape("egg", "M50 128 L60 122 L66 130 L58 136Z")
    d.shape("egg", "M140 112 L150 116 L146 124Z")
    # the hatching egg
    d.shape("egg", "M62 150 C58 186 142 186 138 150 L132 140 L124 148 L116 136 L108 146 L100 134 L92 146 L84 136 L76 148 L68 140Z")
    d.shape("egg2", "M64 162 C70 182 130 182 136 162 C126 176 74 176 64 162Z", shadow=False, line=False)

    def baby():
        d.shape("hero2", "M76 140 C64 132 54 118 56 112 C62 112 74 124 84 134Z", spot=True)
        d.shape("hero2", "M124 140 C136 132 146 118 144 112 C138 112 126 124 116 134Z", spot=True)
        d.shape("hero", ellipse(100, 140, 26, 14))
        d.stroke("mark", "M82 136 Q100 128 118 136", 1.4, line=False)
        d.shape("hero", "M84 120 C84 98 116 98 116 120 C116 132 84 132 84 120Z")
        for x in (91, 109):
            d.marks("light", circle(x, 112, 4))
            d.marks("mark", circle(x, 112.5, 2.5))
            d.marks("light", circle(x - 1, 111, 0.9))
        d.stroke("mark", "M94 124 Q100 128 106 124", 1.6)
    baby()
    d.shape("egg", "M70 150 L76 148 L84 156 L92 146 L100 156 L108 146 L116 156 L124 148 L130 150 C130 156 126 162 120 164 L80 164 C74 162 70 156 70 150Z")
    d.stroke("egg2", "M76 158 Q100 164 124 158", 1.4, line=False)


def hatch_moon(d: Drawing):
    stars(d, [(30, 40, 1.4), (60, 24, 1.1), (160, 28, 1.3), (176, 60, 1), (44, 70, 1), (120, 18, 1)])
    d.disc("glow", 104, 52, 22)
    d.band("far", "M-30 84 H230")
    d.shape("glow2", "M92 84 H116 L124 120 H84Z", shadow=False, line=False, extra='opacity=".7"')
    d.stroke("light", "M40 94 H64 M140 100 H168 M70 108 H90 M118 112 H138", 1.6, line=False)
    d.band("mid", waves(116, 3, 26))
    d.band("light", "M-30 122 Q40 116 100 122 T230 120", shadow=False, line=False)
    d.band("ground", "M-30 126 Q40 120 100 126 T230 124")
    # flipper tracks behind
    for i in range(5):
        x, y = 30 + i * 8, 176 - i * 4
        d.marks("near", f"M{x} {y} h4 v1.6 h-4Z M{x + 2} {y + 6} h4 v1.6 h-4Z")
    group(d, "translate(14 46) scale(.92)", lambda: hatchling_side(d))
    d.band("near", hills(190, 4, 20), line=False)


def hatch_nest(d: Drawing):
    d.disc("glow", 152, 36, 13)
    d.band("far", "M-30 52 H230")
    d.band("mid", waves(60, 2.5, 24))
    d.band("light", "M-30 66 Q40 62 100 66 T230 64", shadow=False, line=False)
    d.band("ground", "M-30 70 Q60 66 100 70 T230 70")
    d.band("near", "M-30 92 H230")
    # sand cross-section texture
    d.marks("deep", circle(30, 110, 1.4) + circle(50, 160, 1.4) + circle(170, 120, 1.4) + circle(160, 178, 1.4)
            + circle(24, 140, 1.2) + circle(184, 150, 1.2))
    # nest chamber with eggs
    d.shape("deep", "M66 92 C64 120 54 140 60 160 C68 186 132 186 140 160 C146 140 136 120 134 92Z", shadow=False)
    for x, y in [(78, 168), (96, 172), (114, 170), (130, 162), (70, 152), (88, 156), (106, 156), (122, 148), (80, 138), (116, 136)]:
        d.shape("egg", circle(x, y, 9))
    d.shape("egg2", "M92 130 L98 126 L104 132 Z", shadow=False)
    # hatchlings climbing out (top-down)
    def baby(x, y, s, rot):
        def draw():
            d.shape("hero2", ellipse(-10, -5, 9, 3), extra='transform="rotate(-35 -10 -5)"')
            d.shape("hero2", ellipse(10, -5, 9, 3), extra='transform="rotate(35 10 -5)"')
            d.shape("hero2", ellipse(-6, 9, 4.5, 2), extra='transform="rotate(40 -6 9)"')
            d.shape("hero2", ellipse(6, 9, 4.5, 2), extra='transform="rotate(-40 6 9)"')
            d.shape("hero2", ellipse(0, -13, 4, 4.6))
            d.shape("hero", ellipse(0, 1, 8.5, 10.5), spot=True)
            d.stroke("mark", "M0 -6 V8 M-5 -2 L0 -6 L5 -2", 1.1, line=False)
        group(d, f"translate({x} {y}) rotate({rot}) scale({s})", draw)
    baby(100, 108, 1.1, 4)
    baby(118, 80, 1.15, 20)
    baby(76, 78, 1.1, -26)


# ================================================================ BEAR WATCHING
BEAR = {"hero": "#7A4B2A", "hero2": "#A0693E", "mark": "#24150C", "fish": "#E0705A", "fish2": "#F2B39E",
        "water": "#7CC6E8", "water2": "#E6F6FD"}
BEAR_PATH = ("M34 95 C36 90 44 86 52 84 L54 77 C56 72 62 72 64 77 C72 72 80 68 92 68 C112 68 140 72 154 82 "
             "C163 89 166 100 162 112 L162 142 L146 142 L144 124 C132 126 114 126 102 124 L100 142 L84 142 L82 118 "
             "C74 114 66 110 60 106 C50 106 42 104 36 101 C33 100 33 97 34 95Z")


def bearwatch_salmon(d: Drawing):
    for x, h in [(14, 50), (34, 62), (170, 58), (190, 46), (152, 44)]:
        pine(d, x, 108, h, "near", shadow=False)
    d.band("far", "M-30 104 H230", line=False)
    # waterfall ledge
    d.shape("deep", "M-30 140 L-30 102 H230 V140Z")
    d.shape("water", "M-30 104 H230 V114 C200 112 170 116 140 114 C110 112 80 116 50 114 C20 112 0 116 -30 114Z", shadow=False)
    d.shape("water", "M-30 114 C0 118 30 112 60 116 C90 120 120 112 150 116 C180 120 200 114 230 116 V170 H-30Z")
    d.stroke("water2", "M10 124 V160 M34 122 V166 M62 126 V158 M150 126 V162 M176 122 V164 M196 128 V158", 2.4, line=False)
    d.stroke("water2", "M90 126 V150 M120 126 V154", 2.4, line=False)
    d.band("mid", waves(168, 3, 26))
    d.shape("water2", "M-30 168 Q0 158 30 168 Q60 158 90 168 Q120 158 150 168 Q180 158 210 168 Q230 162 240 168 V176 H-30Z",
            shadow=False, line=False)

    def bear():
        d.shape("hero", BEAR_PATH)
        d.shape("hero2", "M64 77 C72 72 80 70 92 70 C112 70 132 74 146 80 C124 80 96 82 70 88Z", shadow=False, line=False)
        d.marks("mark", circle(50, 89, 1.8))
        d.marks("mark", ellipse(35, 95, 2.4, 2))
        d.shape("light", "M38 101 L46 102 L42 108Z", shadow=False, line=False)
    group(d, "translate(30 10) scale(.9)", bear)
    # leaping salmon, nose into the open jaws
    def salmon():
        d.shape("fish", "M0 0 C6 -8 20 -9 30 -3 L42 -10 L39 1 L42 12 L30 5 C20 10 6 9 0 0Z", spot=True)
        d.shape("fish2", "M3 2 C10 6 20 6 28 3 C20 8 8 8 3 2Z", shadow=False, line=False)
        d.marks("mark", circle(6, -1.5, 1.6))
    group(d, "translate(56 98) rotate(128) scale(1.1)", salmon)
    d.shape("mark", "M52 101 L66 104 L60 96Z", shadow=False)
    d.stroke("water2", "M16 132 q4 -8 0 -14 M26 134 q4 -8 2 -16", 1.8, line=False)


POLAR = ("M24 112 C26 106 34 102 42 100 L46 94 C48 90 52 90 54 94 C62 88 76 84 92 84 C116 84 142 86 158 94 "
         "C170 100 174 112 170 124 L170 152 L154 152 L152 134 C140 136 120 136 108 134 L106 152 L90 152 L88 130 "
         "C80 126 70 122 62 118 C52 120 40 120 30 118 C26 117 23 115 24 112Z")


def bearwatch_polar(d: Drawing):
    d.disc("glow", 140, 80, 30)
    d.band("far", "M-30 120 L20 104 L40 112 L70 96 L96 114 L230 114")
    d.band("ice", "M-30 150 Q60 144 120 150 T230 148")
    d.shape("mid", "M-30 158 Q40 156 80 162 L80 170 L-30 170Z", shadow=False, line=False, extra='opacity=".35"')
    d.shape("hero", POLAR)
    d.shape("hero2", "M60 100 C80 90 120 90 150 98 C130 96 100 96 66 106Z", shadow=False, line=False)
    d.marks("mark", circle(40, 107, 1.8))
    d.marks("mark", ellipse(25, 112, 2.6, 2.2))
    d.stroke("hero2", "M96 134 L98 148 M160 124 L162 148", 1.4, line=False)
    d.band("ice2", "M-30 172 Q60 166 120 172 T230 170")
    d.band("mid", hills(190, 3, 20), line=False)


def bearwatch_standing(d: Drawing):
    d.disc("glow", 150, 52, 18)
    d.band("far", "M-30 118 L20 78 L50 100 L84 62 L120 104 L150 80 L190 106 L230 96")
    d.shape("light", "M84 62 L96 76 L90 75 L84 80 L78 74 L74 76Z", shadow=False)
    for x, h in [(14, 44), (30, 56), (176, 52), (192, 40), (160, 38)]:
        pine(d, x, 132, h, "near", shadow=False)
    d.band("mid", hills(130, 6))
    # standing bear, front view
    d.shape("hero", "M76 182 L72 150 C62 130 64 98 82 86 C88 82 112 82 118 86 C136 98 138 130 128 150 L124 182Z")
    d.limb("hero", "M76 104 Q62 126 70 142", 14)
    d.limb("hero", "M124 104 Q138 126 130 142", 14)
    d.shape("hero2", ellipse(100, 140, 20, 26), shadow=False, line=False)
    d.shape("hero", circle(78, 54, 9))
    d.shape("hero", circle(122, 54, 9))
    d.shape("hero2", circle(78, 54, 4.5), shadow=False)
    d.shape("hero2", circle(122, 54, 4.5), shadow=False)
    d.shape("hero", "M74 74 C74 52 126 52 126 74 C126 90 116 98 100 98 C84 98 74 90 74 74Z")
    d.shape("hero2", ellipse(100, 84, 12, 9), spot=True)
    d.marks("mark", ellipse(100, 79, 5, 3.4))
    d.stroke("mark", "M100 82 V86 M95 88 Q100 91 105 88", 1.4)
    d.marks("mark", circle(88, 70, 2.2) + circle(112, 70, 2.2))
    d.band("ground", hills(176, 5))
    grass(d, 0, 200, 178, 14, "near")
    d.band("deep", hills(190, 4, 30), line=False)


# ================================================================ GREAT MIGRATION
GNU = {"hero": "#4E4741", "hero2": "#8A8076", "mark": "#1E1A17", "water": "#9C7448", "water2": "#C9A576"}
WILDEBEEST = ("M12 110 L14 106 C20 96 28 86 34 79 C40 74 46 72 50 70 C54 64 60 61 66 61 C82 63 100 70 110 78 "
              "C116 84 117 94 113 104 C111 110 110 114 110 118 L112 140 L106 140 L103 118 C102 114 101 110 99 108 "
              "L97 140 L91 140 L90 108 C80 110 66 110 58 106 L57 140 L51 140 L49 110 L46 110 L45 140 L39 140 L40 104 "
              "C40 102 36 100 34 102 C30 110 26 118 22 122 C18 124 12 123 12 118Z")
GNU_EXTRA = ("M35 81 C24 77 22 66 30 57 C29 65 33 71 43 75Z "  # horn
             "M44 78 L54 82 L46 72Z "  # ear
             "M28 101 L30 116 L34 110 L38 116 L40 104Z "  # beard
             "M112 82 C118 90 118 104 115 116 L119 128 L109 124 L112 104Z")  # tail


def wildebeest(d: Drawing, role="hero", detail=True):
    d.shape(role, WILDEBEEST)
    d.shape(role, GNU_EXTRA, shadow=False)
    if detail:
        d.shape("mark", "M44 74 C52 64 60 60 68 61 L68 65 C60 65 54 69 47 77Z", shadow=False, line=False)
        d.shape("mark", "M13 108 C20 96 27 87 33 80 L37 84 C30 92 24 104 20 118 L13 116Z", shadow=False, line=False)
        d.marks("light", circle(36, 87, 1.4))
        d.stroke("mark", "M66 70 L68 92 M73 71 L75 94 M80 73 L82 96", 1.3, line=False)


def migration_herd(d: Drawing):
    d.disc("glow", 100, 96, 46)
    birds(d, [(40, 44, 1), (56, 36, 0.8), (140, 40, 0.9)])
    d.band("far", hills(124, 5))
    acacia(d, 26, -6, 0.6)
    gnu = WILDEBEEST + GNU_EXTRA
    for x, y in [(4, 118), (20, 119), (150, 116), (166, 118), (182, 117)]:
        group(d, f"translate({x} {y}) scale(.13)", lambda: d.marks("dark", gnu))
    d.raw('<g opacity=".5">', "")
    d.band("light", "M-30 140 Q30 122 70 132 T150 126 T230 134", shadow=False, line=False)
    d.raw("</g>", "")
    d.band("mid", hills(146, 4, 30))
    herd = [(180, 123, .22), (160, 120, .27), (134, 116, .33), (100, 110, .40), (58, 104, .48), (4, 98, .58)]
    for x, y, k in herd:
        group(d, f"translate({x} {y}) scale({k})", lambda: d.shape("dark", gnu))
    d.band("near", hills(178, 4, -20))
    d.band("deep", hills(190, 4, 10), line=False)


def migration_river(d: Drawing):
    d.disc("glow", 150, 46, 18)
    d.band("far", hills(80, 6))
    # far bank with waiting herd
    d.shape("ground", "M120 200 L120 100 C140 92 180 90 230 92 L230 200Z")
    for x, y, s in [(140, 74, .24), (166, 72, .24), (188, 76, .22)]:
        group(d, f"translate({x} {y}) scale({s})", lambda: d.marks("dark", WILDEBEEST + GNU_EXTRA))
    d.band("water", "M-30 118 Q40 112 100 118 T230 116")
    d.stroke("water2", "M10 140 q8 -4 16 0 M60 150 q8 -4 16 0 M130 134 q8 -4 16 0 M30 170 q8 -4 16 0", 2, line=False)
    # swimming heads
    for x, y in [(30, 132), (60, 126)]:
        d.shape("hero", f"M{x} {y} C{x - 2} {y - 8} {x + 10} {y - 12} {x + 12} {y - 4} L{x + 14} {y} Z")
        d.stroke("hero", f"M{x + 4} {y - 9} q-4 -6 1 -9", 2)
    # croc eyes
    d.shape("dark", "M30 168 C34 160 44 160 48 166 L60 166 C62 160 70 160 74 166 L84 168Z")
    # leaping wildebeest
    group(d, "translate(140 88) rotate(-24) scale(-1.05 1.05) translate(-60 -100)", lambda: wildebeest(d))
    d.shape("water2", "M66 138 C70 126 80 124 84 132 C88 122 98 122 100 132 C104 126 112 128 112 138Z", shadow=False)
    d.band("deep", waves(184, 3, 30), line=False)


def migration_face(d: Drawing):
    d.disc("glow", 100, 70, 50)
    d.band("far", hills(150, 6))
    d.band("ground", hills(176, 4))
    # mane
    d.shape("mark", "M70 200 C70 150 80 130 100 126 C120 130 130 150 130 200Z")
    # horns
    d.shape("hero2", "M100 46 C80 40 58 42 44 52 C34 58 28 52 30 42 C32 36 36 32 38 30 C38 38 42 42 48 40 "
                     "C62 32 84 30 100 34 C116 30 138 32 152 40 C158 42 162 38 162 30 C164 32 168 36 170 42 "
                     "C172 52 166 58 156 52 C142 42 120 40 100 46Z", spot=True)
    # ears
    d.shape("hero", "M74 58 C60 56 50 62 46 70 C56 72 68 70 76 66Z")
    d.shape("hero", "M126 58 C140 56 150 62 154 70 C144 72 132 70 124 66Z")
    # face
    d.shape("hero", "M72 48 C82 40 118 40 128 48 C130 66 124 90 122 118 C122 140 116 160 100 160 "
                    "C84 160 78 140 78 118 C76 90 70 66 72 48Z")
    d.shape("mark", "M88 52 C92 46 108 46 112 52 C110 80 108 110 110 140 L90 140 C92 110 90 80 88 52Z", shadow=False)
    # beard
    d.shape("light", "M88 158 L92 186 L98 172 L102 190 L106 172 L112 184 L112 158Z")
    for x in (82, 118):
        d.marks("light", ellipse(x, 86, 4, 3.4))
        d.marks("mark", circle(x, 86, 2.2))
    d.shape("hero2", "M86 146 C86 138 114 138 114 146 C114 158 86 158 86 146Z", shadow=False)
    d.marks("mark", ellipse(93, 148, 2.2, 3) + ellipse(107, 148, 2.2, 3))



# ================================================================ REEF EXPLORING
REEF = {"coral": "#F27A6B", "coral2": "#F6B04A", "fan": "#A65AA0", "sponge": "#4FB0A0"}


def seafan(d: Drawing, x, y, h, role="fan", spot=False):
    w = h * 0.55
    d.shape(role, f"M{x - 3} {y} L{x - 3} {y - h * 0.3} C{x - w} {y - h * 0.4} {x - w} {y - h} {x} {y - h} "
                  f"C{x + w} {y - h} {x + w} {y - h * 0.4} {x + 3} {y - h * 0.3} L{x + 3} {y}Z", spot=spot)
    lat = ""
    for i in range(-3, 4):
        lat += f"M{x} {y - h * 0.3} L{x + i * w * 0.26:.1f} {y - h * 0.92:.1f} "
    for k in (0.5, 0.68, 0.84):
        lat += f"M{x - w * 0.62:.1f} {y - h * k:.1f} Q{x} {y - h * (k + 0.08):.1f} {x + w * 0.62:.1f} {y - h * k:.1f} "
    d.stroke("light", lat, 1.1, line=False)


def staghorn(d: Drawing, x, y, s=1.0, role="coral", spot=False):
    d.limb(role, f"M{x} {y} L{x} {y - 30 * s} M{x} {y - 14 * s} L{x - 16 * s} {y - 32 * s} L{x - 18 * s} {y - 46 * s} "
                 f"M{x - 16 * s} {y - 32 * s} L{x - 28 * s} {y - 38 * s} M{x} {y - 30 * s} L{x + 6 * s} {y - 50 * s} "
                 f"M{x} {y - 22 * s} L{x + 18 * s} {y - 34 * s} L{x + 22 * s} {y - 48 * s}", 7 * s, spot=spot)


def brain(d: Drawing, x, y, r, role="coral2"):
    d.shape(role, f"M{x - r} {y} A{r} {r * 0.8} 0 0 1 {x + r} {y}Z")
    d.stroke("coral", f"M{x - r * 0.75} {y - 2} q{r * 0.12} {-r * 0.3} {r * 0.25} 0 t{r * 0.25} 0 t{r * 0.25} 0 t{r * 0.25} 0 t{r * 0.25} 0 "
                      f"M{x - r * 0.5} {y - r * 0.38} q{r * 0.12} {-r * 0.25} {r * 0.25} 0 t{r * 0.25} 0 t{r * 0.25} 0 t{r * 0.25} 0", 1.5, line=False)


def sea_bg(d: Drawing, floor=164):
    d.band("sky2", waves(30, 4, 26))
    d.band("far", waves(56, 4, 28))
    d.band("mid", waves(86, 5, 30))
    d.band("near", waves(122, 5, 34))
    d.band("ground", f"M-30 {floor} Q40 {floor - 12} 80 {floor - 2} T160 {floor - 4} T230 {floor - 2}")
    d.raw('<g opacity=".16" fill="#fff"><path d="M50 0 L70 0 L110 200 L90 200Z"/><path d="M120 0 L130 0 L168 200 L158 200Z"/></g>', "")


def reef_garden(d: Drawing):
    sea_bg(d, 168)
    for x, y, s in [(120, 48, 0.8), (134, 42, 0.7), (136, 56, 0.75), (150, 48, 0.7), (60, 70, 0.7)]:
        d.shape("hero2", fish(x, y, s), shadow=False)
    seafan(d, 50, 168, 82)
    for x, h in [(84, 40), (94, 52), (104, 36)]:
        d.shape("sponge", rrect(x - 5, 168 - h, 10, h, 5))
        d.shape("deep", ellipse(x, 168 - h + 3, 3, 2), shadow=False)
    staghorn(d, 156, 170, 1.15, spot=True)
    brain(d, 120, 176, 26)
    d.shape("hero", fish(98, 104, 1.4, right=True))
    d.marks("mark", circle(106, 103, 1.6))
    d.stroke("light", "M30 70 a3 3 0 1 0 0.1 0 M36 56 a2 2 0 1 0 0.1 0 M170 100 a3 3 0 1 0 0.1 0", 1.6)
    d.shape("pop", "M30 186 l3 -8 l3 8 l8 0 l-6 5 l3 8 l-8 -5 l-8 5 l3 -8 l-6 -5Z")


IDOL = ("M34 104 L48 98 C56 80 72 62 96 50 C122 38 152 34 180 40 C150 42 126 50 114 62 C126 74 136 88 140 98 "
        "L150 96 L168 82 L170 104 L168 126 L150 112 L140 110 C134 124 120 140 104 152 L92 158 "
        "C86 140 70 124 56 114 L48 110 L34 106Z")


def reef_idol(d: Drawing):
    sea_bg(d, 176)
    staghorn(d, 30, 180, 0.9)
    brain(d, 170, 184, 22)
    for x, y, s in [(160, 160, 0.6), (172, 152, 0.55), (40, 60, 0.6)]:
        d.shape("hero2", fish(x, y, s), shadow=False)
    d.shape("light", IDOL)

    def bands():
        d.shape("mark", "M58 20 L82 20 L80 190 L56 190Z", shadow=False, spot=True)
        d.shape("mark", "M98 20 L124 20 L122 190 L96 190Z", shadow=False, spot=True)
        d.shape("hero", "M124 20 L200 20 L200 190 L122 190Z", shadow=False)
        d.shape("mark", "M150 20 L200 20 L200 190 L150 190Z", shadow=False)
        d.shape("light", "M164 20 L172 20 L172 190 L164 190Z", shadow=False, line=False)
        d.shape("hero", "M80 20 L98 20 L96 60 L80 60Z", shadow=False)
    clipped(d, IDOL, bands)
    d.stroke("mark", IDOL, 1.2, line=False)
    d.shape("hero", "M34 104 L44 99 L46 108Z", shadow=False)
    d.marks("light", circle(64, 96, 4))
    d.marks("mark", circle(64, 96, 2.4))
    bubbles = "M28 92 a3 3 0 1 0 0.1 0 M22 80 a2 2 0 1 0 0.1 0"
    d.stroke("light", bubbles, 1.6)


def reef_glassboat(d: Drawing):
    d.disc("glow", 150, 34, 15)
    d.shape("light", cloud(28, 40, 0.9), shadow=False)
    d.band("far", "M-30 74 H230")
    d.band("mid", waves(86, 3, 26))
    d.band("near", waves(118, 4, 30))
    d.band("deep", waves(150, 4, 34), line=False)
    d.band("ground", "M-30 178 Q40 168 100 176 T230 174")
    seafan(d, 36, 180, 44)
    staghorn(d, 164, 182, 0.8)
    brain(d, 100, 186, 22)
    for x, y, s in [(64, 140, 0.9), (78, 134, 0.8), (130, 150, 0.9)]:
        d.shape("hero2", fish(x, y, s), shadow=False)
    # light through the glass
    d.raw('<path d="M70 104 L130 104 L146 176 L54 176Z" fill="#fff" opacity=".22"/>', "")
    # boat
    d.stroke("dark", "M44 60 V82 M156 60 V82 M100 60 V82", 2.2)
    d.shape("pop", "M34 58 Q100 46 166 58 L166 64 Q100 54 34 64Z", spot=True)
    for x in (62, 82, 118, 138):
        d.shape("dark", circle(x, 76, 5), shadow=False)
    d.shape("hero", "M22 82 H182 L170 104 Q100 110 34 104Z")
    d.shape("light", "M70 96 H130 L128 106 Q100 108 72 106Z", shadow=False)
    d.stroke("hero2", "M26 88 H178", 3, line=False)


# ================================================================ BOTANICAL GARDENS
GARDEN = {"glass": "#8EC9C2", "leaf": "#5E9C6A", "leaf2": "#3F7A52", "bloom": "#E76F6F", "bloom2": "#F6C445",
          "water": "#6FB7C9", "water2": "#9FD3DE", "pad": "#5E9C4A", "pad2": "#86BE62", "lily": "#F7B7CB"}


def botanic_glasshouse(d: Drawing):
    d.shape("light", cloud(18, 46, 1.0))
    d.shape("light", cloud(150, 36, 0.8))
    d.band("far", hills(132, 6))
    # palms behind the glass
    for x, y in [(52, 96), (100, 60), (148, 96)]:
        for a in (-150, -110, -70, -30):
            d.shape("leaf2", leaf(x, y, 26, 6, a), shadow=False, line=False)
    d.raw('<g opacity=".82">', "")
    d.shape("glass", "M18 136 V104 C18 88 30 82 44 82 H70 V136Z")
    d.shape("glass", "M182 136 V104 C182 88 170 82 156 82 H130 V136Z")
    d.shape("glass", "M68 136 V78 C68 58 82 46 100 46 C118 46 132 58 132 78 V136Z")
    d.shape("glass", "M86 50 C86 40 92 34 100 34 C108 34 114 40 114 50Z")
    d.raw("</g>", "")
    bars = "M28 136 V88 M40 136 V83 M54 136 V82 M146 136 V82 M160 136 V83 M172 136 V88 " \
           "M18 110 H70 M130 110 H182 M80 136 V56 M92 136 V48 M108 136 V48 M120 136 V56 M68 96 H132 M68 116 H132 M70 74 H130 " \
           "M94 34 V48 M106 34 V48"
    d.stroke("light", bars, 1.6)
    d.stroke("light", "M18 136 V104 C18 88 30 82 44 82 H70 M182 136 V104 C182 88 170 82 156 82 H130 "
                      "M68 136 V78 C68 58 82 46 100 46 C118 46 132 58 132 78 V136 M86 50 C86 40 92 34 100 34 C108 34 114 40 114 50", 2.6)
    d.shape("light", rrect(96, 26, 8, 8, 2))
    d.shape("dark", rrect(90, 112, 20, 24, 3), shadow=False)
    d.band("near", "M-30 136 H230")
    d.band("mid", "M-30 150 Q100 142 230 150")
    for x in (20, 44, 156, 180):
        d.shape("bloom", scallop(x, 150, 8, 7, 0.2), shadow=False, spot=True)
    for x in (32, 168):
        d.shape("bloom2", scallop(x, 154, 7, 7, 0.2), shadow=False)
    d.shape("ground", "M84 200 L94 136 H106 L116 200Z")
    d.band("deep", hills(186, 3, 20), line=False)


def lilypad(d: Drawing, x, y, r, rot=0, spot=False):
    notch = math.radians(rot)
    a1, a2 = notch - 0.08, notch + 0.08
    p1 = (x + r * math.cos(a1), y + r * 0.82 * math.sin(a1))
    p2 = (x + r * math.cos(a2), y + r * 0.82 * math.sin(a2))
    d.shape("pad2", f"M{pt(x, y)} L{pt(*p2)} A{r} {r * 0.82} 0 1 1 {pt(*p1)}Z", spot=spot)
    rr = r * 0.86
    q1 = (x + rr * math.cos(a1), y + rr * 0.82 * math.sin(a1))
    q2 = (x + rr * math.cos(a2), y + rr * 0.82 * math.sin(a2))
    d.shape("pad", f"M{pt(x, y)} L{pt(*q2)} A{rr} {rr * 0.82} 0 1 1 {pt(*q1)}Z", shadow=False, line=False)
    v = ""
    for i in range(1, 12):
        a = notch + 2 * math.pi * i / 12
        v += f"M{pt(x, y)} L{pt(x + rr * 0.9 * math.cos(a), y + rr * 0.82 * 0.9 * math.sin(a))} "
    d.stroke("pad2", v, 1.2)


def botanic_lily(d: Drawing):
    d.band("water", "M-30 -10 H230")
    d.stroke("water2", "M20 40 q10 -4 20 0 M140 30 q10 -4 20 0 M150 120 q10 -4 20 0 M30 150 q10 -4 20 0 M90 186 q10 -4 20 0", 2.2, line=False)
    lilypad(d, 64, 72, 52, 40)
    lilypad(d, 148, 150, 46, 200)
    lilypad(d, 158, 52, 26, 120)
    lilypad(d, 34, 170, 24, -60)
    # flower
    cx, cy = 100, 124
    for i in range(10):
        a = 2 * math.pi * i / 10
        d.shape("light", leaf(cx, cy, 30, 9, math.degrees(a)), shadow=i == 0)
    for i in range(8):
        a = 2 * math.pi * (i + 0.5) / 8
        d.shape("lily", leaf(cx, cy, 20, 7, math.degrees(a)), shadow=False, spot=True)
    d.shape("bloom2", circle(cx, cy, 6), shadow=False)
    # koi
    d.shape("hero", fish(170, 100, 1.1), shadow=False)


def botanic_strelitzia(d: Drawing):
    d.disc("glow", 100, 100, 70, line=False)
    d.shape("leaf", "M150 200 C160 140 176 100 196 80 C204 110 190 160 166 200Z")
    d.shape("leaf2", "M38 200 C30 150 12 110 -4 96 C-8 130 6 170 24 200Z")
    d.limb("leaf2", "M102 200 C100 170 100 150 104 128", 7)
    # spathe (the beak)
    d.shape("spathe", "M30 116 C60 112 96 112 128 120 C140 124 150 132 152 140 C130 134 104 132 70 128 C50 126 36 122 30 116Z")
    d.shape("spathe2", "M128 120 C140 124 150 132 152 140 C140 136 128 132 112 130Z", shadow=False, line=False)
    # orange sepals fanning up
    for x0, x1, y1 in [(86, 70, 40), (94, 92, 30), (104, 118, 40), (112, 140, 62)]:
        d.shape("orange", f"M{x0 - 6} 118 C{x0 - 4} 90 {x1 - 6} {y1 + 20} {x1} {y1} C{x1 + 4} {y1 + 24} {x0 + 6} 96 {x0 + 6} 118Z", spot=True)
    # blue petals pointing forward
    d.shape("blue", "M90 114 C78 100 64 92 48 92 C60 100 72 110 84 120Z")
    d.shape("blue", "M100 112 C92 94 84 84 70 78 C78 92 86 104 92 118Z", shadow=False)


# ================================================================ LAKE DAY
LAKE = {"water": "#6FB7D6", "water2": "#DDF1F8", "wood": "#B7804C", "wood2": "#8A5A33", "pine": "#3E6E52"}


def lake_scene(d: Drawing, shore=112, trees=True):
    d.band("far", "M-30 96 L10 74 L40 88 L76 52 L112 86 L140 68 L176 90 L230 76")
    d.shape("light", "M76 52 L88 64 L82 63 L76 68 L70 62 L66 64Z", shadow=False)
    if trees:
        for x in range(-6, 210, 12):
            h = 22 + (x * 7) % 14
            pine(d, x, shore + 2, h, "pine", shadow=False, line=x % 36 == 6)
    d.band("water", f"M-30 {shore} H230")
    d.stroke("water2", f"M30 {shore + 14} H60 M130 {shore + 10} H170 M70 {shore + 30} H100", 2, line=False)


def chair(d: Drawing, x, y, role, spot=False):
    def draw():
        d.shape(role, rrect(-24, -27, 13, 4, 1.5) + rrect(11, -27, 13, 4, 1.5), shadow=False)
        d.shape(role, rrect(-22, -25, 4, 25, 1) + rrect(18, -25, 4, 25, 1))
        d.shape(role, rrect(-17, -22, 34, 4, 1), shadow=False)
        for i in range(-2, 3):
            top = -54 + abs(i) * 4 + (i * i) * 0.8
            d.shape(role, rrect(i * 6.6 - 2.6, top, 5.2, -8 - top, 2.6), spot=spot)
        d.shape(role, rrect(-17, -14, 34, 4, 1), shadow=False)
    group(d, f"translate({x} {y})", draw)


def lakeday_dock(d: Drawing):
    d.disc("glow", 150, 46, 18)
    lake_scene(d, 108)
    d.shape("wood", "M44 210 L84 120 H116 L156 210Z")
    d.stroke("wood2", "M78 134 H122 M72 148 H128 M64 164 H136 M56 182 H144", 1.8, line=False)
    d.stroke("wood2", "M88 118 V128 M112 118 V128", 3)
    chair(d, 78, 170, "chairA", spot=True)
    chair(d, 124, 170, "chairB")


def lakeday_canoe(d: Drawing):
    d.disc("glow", 52, 48, 16)
    d.shape("light", cloud(130, 40, 0.9), shadow=False)
    lake_scene(d, 104)
    d.stroke("water2", "M24 168 H48 M150 172 H176", 2, line=False)
    # reflection
    d.raw('<g opacity=".3">', "")
    d.shape("hero", "M20 140 C50 146 150 146 180 140 C176 152 150 160 100 160 C50 160 24 152 20 140Z", shadow=False, line=False)
    d.raw("</g>", "")
    # paddle
    d.limb("wood2", "M128 92 L160 150", 3.2)
    d.shape("wood", "M156 142 C162 140 170 150 168 160 C166 170 160 168 156 160Z", extra='transform="rotate(-28 162 155)"')
    d.shape("hero", "M14 120 C30 128 60 132 100 132 C140 132 170 128 186 120 C184 132 170 142 150 144 L50 144 C30 142 16 132 14 120Z", spot=True)
    d.shape("hero2", "M14 120 C30 128 60 132 100 132 C140 132 170 128 186 120 L184 126 C170 132 140 136 100 136 C60 136 30 132 16 126Z", shadow=False)
    d.stroke("wood2", "M60 132 V138 M100 133 V140 M140 132 V138", 2.2, line=False)
    d.limb("wood2", "M150 128 L162 104", 2.6)


def lakeday_swan(d: Drawing):
    d.disc("glow", 150, 44, 16)
    lake_scene(d, 106)
    d.stroke("water2", "M14 180 H40 M150 184 H180", 2, line=False)
    d.raw('<g opacity=".25">', "")
    d.shape("swan", "M30 156 C60 164 140 164 176 156 C170 170 130 176 100 176 C70 176 40 170 30 156Z", shadow=False, line=False)
    d.raw("</g>", "")
    # body + raised wing
    d.shape("swan", "M30 120 C40 112 60 112 70 118 L140 118 C150 108 168 106 178 98 C176 116 170 140 156 152 "
                    "C130 160 70 160 44 152 C34 146 28 134 30 120Z")
    d.shape("swan2", "M70 118 C96 104 128 92 168 86 C160 104 146 122 120 128 C100 130 82 128 70 118Z", spot=True)
    # neck
    d.limb("swan", "M54 130 C40 110 30 84 44 66 C52 56 66 58 66 70", 14)
    d.shape("beak", "M62 64 L82 72 L64 76Z")
    d.shape("dark", "M60 62 C64 60 68 64 66 70 L62 72Z", shadow=False)
    d.marks("mark", circle(56, 64, 1.8))
    # seat + canopy hint
    d.stroke("pop", "M70 118 V110 M90 118 V108", 0.1, line=False)
    d.band("deep", waves(188, 3, 34), line=False)


# ================================================================ AUTUMN LEAVES
FALL = {"leafA": "#D9482B", "leafB": "#F08A24", "leafC": "#F2C230", "trunk": "#5A3B2A", "veins": "#9E2A1A"}
MAPLE_R = [(100, 26), (110, 48), (119, 44), (115, 72), (131, 63), (137, 52), (145, 66), (170, 58), (161, 80), (174, 86),
           (148, 106), (153, 116), (128, 114), (132, 128), (108, 120), (103, 144)]


def maple(cx=100, cy=100, s=1.0):
    pts = MAPLE_R + [(200 - x, y) for x, y in reversed(MAPLE_R[1:])]
    return "M" + " L".join(f"{cx + (x - 100) * s:.1f} {cy + (y - 100) * s:.1f}" for x, y in pts) + "Z"


def maple_leaf(d: Drawing, cx, cy, s, rot, role, spot=False, veins=True, shadow=True):
    def draw():
        d.limb("trunk", f"M{100} {140} L{100} {164}", 3.2, shadow=False)
        d.shape(role, maple(), spot=spot, shadow=shadow)
        if veins:
            d.stroke("veins", "M100 138 L100 34 M100 120 L164 64 M100 120 L36 64 M100 132 L148 110 M100 132 L52 110", 1.8, line=False)
            d.stroke("veins", "M100 138 L100 50", 2, line=True)
    group(d, f"translate({cx} {cy}) rotate({rot}) scale({s}) translate(-100 -100)", draw)


def autumn_maple(d: Drawing):
    d.disc("glow", 100, 100, 66, line=False)
    maple_leaf(d, 46, 52, 0.32, -30, "leafC", veins=False)
    maple_leaf(d, 160, 150, 0.36, 24, "leafB", veins=False)
    maple_leaf(d, 160, 50, 0.24, 40, "leafA", veins=False)
    maple_leaf(d, 38, 152, 0.26, -50, "leafB", veins=False)
    maple_leaf(d, 100, 96, 0.92, -10, "leafA", spot=True)


def crown(d: Drawing, x, y, r, role, spot=False):
    d.shape(role, scallop(x, y, r, 9, 0.12), spot=spot)


def autumn_newengland(d: Drawing):
    d.disc("glow", 152, 44, 14)
    birds(d, [(36, 40, 1), (52, 32, 0.8)])
    d.band("far", "M-30 66 Q30 42 90 52 T230 50")
    d.band("mid", "M-30 116 Q50 92 120 106 T230 100")
    for x, y, r, role in [(4, 104, 12, "leafB"), (26, 98, 13, "leafC"), (150, 98, 12, "leafA"), (172, 96, 13, "leafB"), (194, 100, 12, "leafC")]:
        crown(d, x, y, r, role)
    # church
    d.shape("light", "M86 70 L92 52 L98 70Z")
    d.shape("light", rrect(86, 70, 12, 22, 1))
    d.shape("light", "M70 92 H116 V128 H70Z")
    d.shape("light", "M66 94 L93 78 L120 94Z")
    d.shape("dark", rrect(89, 74, 6, 7, 3), shadow=False)
    d.shape("dark", rrect(88, 108, 10, 20, 4), shadow=False)
    d.shape("dark", rrect(74, 100, 7, 10, 3) + rrect(105, 100, 7, 10, 3), shadow=False)
    d.band("near", "M-30 130 Q60 120 120 128 T230 124")
    for x, y, r, role in [(-4, 132, 22, "leafA"), (34, 126, 20, "leafC"), (64, 132, 18, "leafB"), (124, 130, 18, "leafC"),
                          (156, 126, 22, "leafA"), (196, 130, 22, "leafB")]:
        d.limb("trunk", f"M{x} {y} V{y + 30}", 4, shadow=False)
        crown(d, x, y, r, role, spot=role == "leafA")
    d.band("ground", hills(172, 4))
    d.stroke("trunk", "M-10 176 H210", 2, line=False)
    d.band("deep", hills(188, 3, 20), line=False)


def autumn_avenue(d: Drawing):
    d.disc("glow", 100, 84, 22)
    d.band("far", "M-30 96 H230", line=False)
    d.band("ground", "M-30 98 H230")
    d.shape("light", "M96 98 H104 L150 210 H50Z", shadow=False)
    trees = [(78, 98, 8, "leafC"), (122, 98, 8, "leafB"), (66, 106, 13, "leafB"), (134, 106, 13, "leafA"),
             (48, 120, 20, "leafA"), (152, 120, 20, "leafC"), (16, 144, 32, "leafC"), (184, 144, 32, "leafB")]
    for x, base, r, role in trees:
        top = base - r * 2.6
        d.limb("trunk", f"M{x} {base} V{top + r}", max(2, r * 0.3), shadow=False)
        crown(d, x, top, r * 1.25, role, spot=r > 30 and role == "leafC")
    for x, y, rot, role in [(96, 150, 20, "leafA"), (124, 176, -30, "leafB"), (70, 180, 40, "leafC"), (112, 120, 10, "leafB")]:
        maple_leaf(d, x, y, 0.12, rot, role, veins=False, shadow=False)
    for x, y, rot, role in [(60, 70, -20, "leafA"), (140, 60, 30, "leafC"), (100, 40, 0, "leafB")]:
        maple_leaf(d, x, y, 0.13, rot, role, veins=False)


# ================================================================ TULIP FIELDS
TULIP = {"tR": "#E63946", "tY": "#F6C445", "tP": "#EE7FB0", "tO": "#F2832B", "stem": "#5E9C4A", "stem2": "#3E7A3A",
         "mill": "#5A4636", "sail": "#B5523B"}


def fan_rows(d: Drawing, vx, vy, roles, x0=-120, x1=320, bottom=210, gap=0.35):
    n = len(roles)
    w = (x1 - x0) / n
    for i, role in enumerate(roles):
        a, b = x0 + i * w, x0 + (i + 1) * w - w * gap
        d.shape(role, f"M{vx} {vy} L{b:.1f} {bottom} L{a:.1f} {bottom}Z", shadow=False, line=role != "stem")


def windmill(d: Drawing, x, y, s=1.0):
    def draw():
        d.shape("mill", "M-14 0 L-10 -44 H10 L14 0Z")
        d.shape("mill", "M-12 -44 C-12 -54 12 -54 12 -44Z")
        d.shape("light", rrect(-4, -14, 8, 14, 3), shadow=False)
        d.shape("light", rrect(-3, -32, 6, 7, 2), shadow=False)
        for a in (40, 130, 220, 310):
            d.shape("sail", rrect(4, -3, 40, 7, 1), extra=f'transform="translate(0 -46) rotate({a})"', spot=a == 40)
            d.stroke("mill", "M0 0 L44 0", 1.6, line=False) if False else None
        d.shape("mill", circle(0, -46, 3.5), shadow=False)
    group(d, f"translate({x} {y}) scale({s})", draw)


def tulip_windmill(d: Drawing):
    d.disc("glow", 52, 56, 16)
    d.shape("light", cloud(128, 40, 0.9), shadow=False)
    d.band("far", "M-30 104 H230")
    windmill(d, 132, 104, 1.05)
    d.band("stem", "M-30 108 H230", line=False)
    fan_rows(d, 100, 104, ["tR", "tY", "tP", "tO", "tR", "tY", "tP", "tO"], gap=0.28)
    d.band("stem2", "M-30 196 H230", line=False)


def tulip_head(d: Drawing, x, y, s, role, rot=0, spot=False):
    def draw():
        d.shape(role, "M-16 -10 C-18 6 -10 18 0 18 C10 18 18 6 16 -10 L10 -2 L6 -20 L0 -6 L-6 -20 L-10 -2Z", spot=spot)
        d.shape(role, "M-6 -20 C-2 -14 2 -14 6 -20 L4 2 H-4Z", shadow=False)
        d.stroke("light", "M-9 0 Q-8 10 -2 14", 2, line=False)
    group(d, f"translate({x} {y}) rotate({rot}) scale({s})", draw)


def tulip_bouquet(d: Drawing):
    d.disc("glow", 100, 100, 64, line=False)
    d.shape("stem", "M60 196 C50 160 40 140 22 124 C44 132 62 150 70 196Z")
    d.shape("stem", "M140 196 C150 160 162 140 180 126 C158 132 140 150 132 196Z")
    d.limb("stem2", "M100 196 C100 160 98 120 100 92", 5)
    d.limb("stem2", "M90 196 C86 160 72 130 56 112", 5)
    d.limb("stem2", "M110 196 C116 160 130 132 146 116", 5)
    d.shape("stem", "M96 196 C80 170 76 150 80 128 C90 150 100 170 104 196Z")
    tulip_head(d, 56, 96, 1.4, "tY", -22)
    tulip_head(d, 146, 100, 1.4, "tP", 20)
    tulip_head(d, 100, 70, 1.65, "tR", 0, spot=True)


def bike(d: Drawing, x, y, s=1.0):
    def draw():
        for cx in (-34, 34):
            d.stroke("dark", circle(cx, 0, 22), 3.2, shadow=True)
            d.stroke("dark", f"M{cx} -22 V22 M{cx - 22} 0 H{cx + 22} M{cx - 15} -15 L{cx + 15} 15 M{cx - 15} 15 L{cx + 15} -15", 0.8, line=False)
        d.stroke("hero", "M-34 0 L-4 0 L-14 -30 M-4 0 L22 -26 M34 0 L22 -32 L18 -40 M-14 -30 L20 -30", 3.6, shadow=True)
        d.stroke("hero", "M-34 0 L-14 -30", 3.6)
        d.shape("dark", "M-22 -34 H-6 L-8 -30 H-20Z")
        d.stroke("dark", "M14 -42 L26 -44", 3)
        # basket of tulips
        for i, (bx, role) in enumerate([(26, "tR"), (34, "tY"), (42, "tP"), (30, "tO"), (40, "tR")]):
            d.stroke("stem2", f"M{bx} -30 L{bx + (bx - 34) * 0.4} -46", 2, line=False)
        for bx, by, role in [(22, -50, "tY"), (32, -56, "tR"), (44, -52, "tP"), (28, -44, "tO"), (40, -46, "tR")]:
            tulip_head(d, bx, by, 0.36, role)
        d.shape("hero2", "M18 -34 H50 L46 -16 H22Z", spot=True)
        d.stroke("mark", "M24 -28 H46 M24 -22 H44 M30 -34 L30 -16 M38 -34 L38 -16", 1.2, line=False)
    group(d, f"translate({x} {y}) scale({s})", draw)


def tulip_bike(d: Drawing):
    d.disc("glow", 150, 44, 16)
    d.band("far", "M-30 100 H230")
    windmill(d, 40, 100, 0.5)
    for i, role in enumerate(["tR", "tY", "tP", "tO"]):
        y0 = 104 + i * 14
        d.band("stem", f"M-30 {y0} H230", shadow=False, line=False)
        d.band(role, f"M-30 {y0 + 3} H230", shadow=False, line=False)
    d.band("ground", "M-30 158 H230")
    bike(d, 96, 150, 1.25)
    d.band("deep", hills(188, 3), line=False)



# ================================================================ LAVENDER FIELDS
LAV = {"lav": "#8E6CC0", "lav2": "#B79AE0", "lavdeep": "#5E4592", "stem": "#6E9A5A", "stem2": "#4F7A44",
       "stone": "#E8D6B5", "roof": "#C8673E", "tree": "#3F6B3A", "ribbon": "#E9C46A"}


def lav_spike(d: Drawing, x, y, h, rot=0, role="lav", role2="lav2", stem=True, spot=False):
    def draw():
        if stem:
            d.stroke("stem2", f"M0 0 L0 {-h}", 2, line=True)
        for i in range(6):
            yy = -h + i * h * 0.075
            w = 3.2 + i * 0.3
            d.shape(role if i % 2 == 0 else role2, f"M{-w} {yy} a{w} {w * 1.25} 0 1 0 {2 * w} 0 a{w} {w * 1.25} 0 1 0 {-2 * w} 0Z",
                    shadow=False, spot=spot and i % 2 == 0)
    group(d, f"translate({x} {y}) rotate({rot})", draw)


def lavender_rows(d: Drawing):
    d.disc("glow", 64, 82, 26)
    d.band("far", "M-30 94 Q60 84 120 90 T230 88")
    # lone tree and farmhouse on the horizon
    d.limb("trunk", "M144 96 V74", 3.4)
    d.shape("tree", scallop(144, 66, 14, 9, 0.12))
    d.shape("stone", "M32 96 V82 H56 V96Z")
    d.shape("roof", "M29 83 L44 74 L59 83Z")
    d.marks("dark", rrect(40, 86, 5, 6, 1))
    d.band("stone", "M-30 96 H230", line=False)
    vx, vy = 120, 94
    x0, n = -200, 13
    w = 600 / n
    for i in range(n):
        a, b = x0 + i * w, x0 + (i + 1) * w - w * 0.38
        d.shape("lav", f"M{vx} {vy} L{b:.1f} 210 L{a:.1f} 210Z", shadow=True, line=i % 2 == 0)
        d.shape("lav2", f"M{vx} {vy} L{a + (b - a) * 0.7:.1f} 210 L{a + (b - a) * 0.55:.1f} 210Z", shadow=False, line=False)


def lavender_bundle(d: Drawing):
    d.disc("light", 100, 100, 66, line=False)
    stems = [(-26, 70), (-16, 80), (-6, 88), (4, 90), (14, 84), (24, 74), (-20, 60), (20, 62)]
    for ang, h in stems:
        a = math.radians(ang * 0.9)
        d.stroke("stem2", f"M100 160 L{100 + math.sin(a) * (h + 6):.1f} {160 - math.cos(a) * (h + 6):.1f}", 2.2)
    for ang, h in stems:
        lav_spike(d, 100, 160, h + 34, ang * 0.9, stem=False)
    d.limb("stem", "M92 150 L88 192 M100 150 L100 194 M108 150 L112 192", 4)
    # ribbon bow
    d.shape("ribbon", rrect(86, 150, 28, 10, 3), spot=True)
    d.shape("ribbon", "M100 155 C90 140 74 142 76 152 C78 162 92 160 100 155Z", spot=True)
    d.shape("ribbon", "M100 155 C110 140 126 142 124 152 C122 162 108 160 100 155Z", spot=True)
    d.shape("ribbon", "M98 156 L86 178 L92 176 L94 182 L102 158Z M102 156 L114 178 L108 176 L106 182 L98 158Z", shadow=False)
    d.shape("ribbon", circle(100, 155, 5))


def bee(d: Drawing, x, y, s=1.0, rot=0):
    def draw():
        d.raw('<g opacity=".8">', "")
        d.shape("wing", ellipse(-6, -20, 10, 16), extra='transform="rotate(-24 -6 -20)"')
        d.shape("wing", ellipse(8, -18, 8, 13), extra='transform="rotate(20 8 -18)"')
        d.raw("</g>", "")
        d.limb("beeD", "M-6 8 L-10 20 M2 10 L0 22 M10 8 L14 18", 2.4, shadow=False)
        d.shape("beeY", ellipse(0, 0, 22, 13), spot=True)
        clipped(d, ellipse(0, 0, 22, 13), lambda: d.marks("beeD", "M-8 -14 h7 v28 h-7Z M6 -14 h6 v28 h-6Z M18 -14 h8 v28 h-8Z"))
        d.shape("beeD", circle(-26, -2, 9))
        d.marks("light", circle(-29, -4, 2.4))
        d.stroke("beeD", "M-30 -9 Q-36 -18 -42 -18 M-26 -10 Q-28 -20 -34 -24", 1.6)
    group(d, f"translate({x} {y}) rotate({rot}) scale({s})", draw)


def lavender_bee(d: Drawing):
    d.disc("glow", 150, 50, 20)
    d.band("far", hills(150, 6))
    for x, h, r in [(20, 90, -10), (44, 70, 6), (168, 80, 8), (186, 100, -4), (150, 60, -12)]:
        lav_spike(d, x, 200, h, r, "lavdeep", "lav")
    lav_spike(d, 92, 200, 150, -4, spot=True)
    lav_spike(d, 120, 200, 120, 8)
    lav_spike(d, 66, 200, 112, -12)
    bee(d, 116, 74, 1.25, -10)
    d.stroke("beeD", "M150 104 q8 -6 14 2 q6 8 14 0", 1.4, line=False)


# ================================================================ RAINBOW CHASING
BOW = {"r1": "#E8504A", "r2": "#F28C28", "r3": "#F6C445", "r4": "#6CBF5A", "r5": "#4A9BD6", "r6": "#7A5BB5"}


def rainbow(d: Drawing, cx, cy, r, w=6, line_bands=(0, 5), shadow=True):
    for i, role in enumerate(["r1", "r2", "r3", "r4", "r5", "r6"]):
        rr = r - i * w
        d.stroke(role, f"M{cx - rr} {cy} A{rr} {rr} 0 0 1 {cx + rr} {cy}", w + 0.6, shadow=shadow and i == 0, line=i in line_bands)


def rainbow_hills(d: Drawing):
    d.shape("light", cloud(-6, 48, 1.4))
    rainbow(d, 100, 150, 86, 6)
    d.raw('<g opacity=".45">', "")
    rainbow(d, 100, 150, 104, 3, line_bands=(), shadow=False)
    d.raw("</g>", "")
    d.band("far", hills(118, 10))
    d.band("mid", hills(140, 12, 30))
    d.stroke("ground", "M-10 150 L40 142 L80 148 L120 140 L170 146 L214 140", 1.6, line=False)
    d.band("near", hills(162, 10, -20))
    # sheep
    for x, y, s in [(60, 154, 1.0), (140, 150, 0.8)]:
        def sheep(x=x, y=y, s=s):
            d.shape("light", scallop(0, 0, 9, 8, 0.18))
            d.shape("dark", ellipse(-10, 1, 3.6, 4.4), shadow=False)
            d.stroke("dark", "M-4 7 V13 M4 7 V13", 2)
        group(d, f"translate({x} {y}) scale({s})", sheep)
    d.band("deep", hills(184, 6, 30))


def rainbow_cloud(d: Drawing):
    d.disc("glow", 150, 66, 20)
    d.shape("pop", "M150 32 L150 24 M174 42 L180 36 M184 66 L192 66", line=False)
    d.stroke("glow", "M150 40 V30 M174 50 L181 43 M180 70 H190", 3)
    rainbow(d, 100, 140, 74, 9, line_bands=(0, 2, 4))
    for x0, y0 in [(18, 132), (130, 132)]:
        d.shape("light", f"M{x0} {y0 + 12} a12 12 0 0 1 8 -22 a16 16 0 0 1 28 -6 a13 13 0 0 1 16 14 a10 10 0 0 1 0 14Z")
    d.stroke("r5", "M34 158 l-3 8 M46 162 l-3 8 M58 158 l-3 8 M146 158 l-3 8 M158 162 l-3 8 M170 158 l-3 8", 2.4)


def rainbow_road(d: Drawing):
    rainbow(d, 100, 112, 70, 6)
    d.band("far", "M-30 112 Q40 100 100 110 T230 106")
    d.band("mid", hills(130, 6, 20))
    d.shape("dark", "M96 110 H104 L170 210 H30Z")
    d.stroke("light", "M100 116 V124 M100 134 V146 M100 158 V176 M100 188 V210", 2.6)
    # car from behind
    def car():
        d.shape("hero", "M-30 -4 C-30 -10 -26 -14 -20 -14 L-16 -28 C-14 -34 14 -34 16 -28 L20 -14 C26 -14 30 -10 30 -4 L30 10 H-30Z")
        d.shape("light", "M-14 -15 L-11 -27 H11 L14 -15Z", shadow=False)
        d.shape("pop", rrect(-27, -8, 10, 5, 2) + rrect(17, -8, 10, 5, 2), shadow=False)
        d.shape("light", rrect(-8, 0, 16, 5, 1), shadow=False)
        d.shape("dark", rrect(-28, 8, 10, 8, 2) + rrect(18, 8, 10, 8, 2), shadow=False)
        d.shape("hero2", rrect(-18, -40, 36, 6, 2), spot=True)
    group(d, "translate(100 162) scale(1.25)", car)


# ================================================================ FIREFLIES
FLY = {"sky": "#1F2A44", "sky2": "#2E3B5E", "light": "#E8EDF7", "bug": "#F7F06B", "bug2": "#FFFBC9", "fly": "#6B5A4A", "flyR": "#E0584A", "wing": "#EEF2F4", "jar": "#CFE5E8",
       "lid": "#B9A27A", "trunkN": "#2A2F3A", "grassN": "#2F4A3A"}
NIGHT_PAL = ["dusk", "coastal", "meadow", "blush"]


def glows(d: Drawing, pts, r=2.2):
    paper = "".join(f'<circle cx="{x}" cy="{y}" r="{r * k * 3.2}" fill="{d.c.get("bug", "#fff")}" opacity=".22"/>'
                    f'<circle cx="{x}" cy="{y}" r="{r * k}" fill="{d.c.get("bug2", "#fff")}"/>' for x, y, k in pts)
    line = "".join(f'<circle cx="{x}" cy="{y}" r="{r * k * 1.1}" fill="{d.c.get("spot", "#000")}"/>' for x, y, k in pts)
    d.raw(paper, line)


def firefly_jar(d: Drawing):
    stars(d, [(30, 50, 1.2), (160, 40, 1.4), (140, 24, 1), (60, 28, 1)])
    d.disc("glow", 46, 50, 12)
    d.band("far", hills(150, 8))
    grass(d, -10, 210, 156, 16, "grassN", 12)
    glows(d, [(30, 110, 1), (172, 96, 0.9), (156, 132, 1.1), (20, 140, 0.8)])
    # jar glow
    d.raw('<circle cx="100" cy="124" r="56" fill="#FFF6A8" opacity=".18"/>', "")
    d.raw('<g opacity=".88">', "")
    d.shape("jar", "M70 76 C66 82 62 90 62 100 V160 C62 170 70 176 80 176 H120 C130 176 138 170 138 160 V100 C138 90 134 82 130 76Z")
    d.raw("</g>", "")
    glows(d, [(84, 110, 1.2), (110, 98, 1), (118, 132, 1.3), (90, 150, 1.1), (104, 120, 0.9), (78, 134, 0.9), (122, 158, 1)], 2.6)
    d.stroke("light", "M72 104 V150", 3, line=False)
    d.shape("lid", rrect(66, 62, 68, 16, 4), spot=True)
    d.stroke("dark", "M70 68 H130 M70 73 H130", 1.2, line=False)
    d.stroke("lid", "M76 62 C70 40 130 40 124 62", 2.4)
    d.band("deep", hills(186, 4, 20), line=False)


def firefly_forest(d: Drawing):
    d.disc("glow", 140, 42, 14)
    stars(d, [(40, 30, 1.2), (70, 18, 1), (176, 70, 1.1), (110, 26, 1)])
    for x in range(-10, 220, 24):
        pine(d, x, 130, 50 + (x * 7) % 20, "deep", shadow=False, line=False)
    d.band("mid", hills(132, 4))
    for x, w in [(24, 14), (66, 10), (150, 12), (184, 16)]:
        d.shape("trunkN", f"M{x - w / 2} 200 L{x - w / 2 + 1} -10 L{x + w / 2 - 1} -10 L{x + w / 2} 200Z")
    d.band("grassN", hills(170, 6))
    grass(d, -10, 210, 172, 14, "grassN", 10)
    pts = [(40, 90, 1), (52, 120, 0.8), (88, 100, 1.2), (104, 70, 0.9), (118, 116, 1), (132, 90, 0.8), (96, 140, 1.1),
           (168, 110, 0.9), (82, 60, 0.7), (126, 150, 0.9), (60, 150, 1), (172, 150, 0.8), (110, 92, 0.7), (40, 132, 0.7)]
    glows(d, pts, 2.4)


def firefly_bug(d: Drawing):
    stars(d, [(30, 60, 1.2), (170, 40, 1.4), (150, 160, 1), (60, 30, 1)])
    d.band("far", hills(170, 6))
    d.shape("grassN", "M40 210 C60 160 110 120 186 104 C130 128 84 160 62 210Z")
    glows(d, [(40, 110, 1), (170, 140, 0.9), (30, 150, 0.8), (150, 70, 0.8)], 2.4)

    def bug():
        # glowing tail
        d.raw('<circle cx="64" cy="114" r="42" fill="#FFF6A8" opacity=".25"/><circle cx="64" cy="114" r="24" fill="#FFF6A8" opacity=".35"/>', "")
        d.limb("fly", "M110 108 L118 128 M126 104 L138 122 M96 110 L98 130", 2.6, shadow=False)
        d.shape("bug", "M50 100 C42 106 42 124 52 130 C64 136 80 128 88 118 C90 110 80 100 70 98Z", spot=True)
        d.shape("bug2", "M54 108 C50 114 52 122 58 124 C66 126 74 120 76 114Z", shadow=False, line=False)
        d.shape("fly", "M76 96 C96 88 128 88 146 96 C150 104 140 112 128 114 C108 118 88 118 80 112Z")
        d.shape("flyR", "M140 88 C150 84 160 88 162 96 C162 104 154 108 146 106Z")
        d.shape("fly", circle(164, 102, 8))
        d.marks("light", circle(166, 100, 2))
        d.stroke("fly", "M168 96 Q180 80 176 66 M164 94 Q168 76 160 64", 1.8)
        d.raw('<g opacity=".7">', "")
        d.shape("wing", "M120 92 C100 70 70 64 52 70 C66 84 92 94 118 98Z")
        d.raw("</g>", "")
        d.shape("fly", "M78 96 C100 82 130 82 144 92 L140 100 C120 96 96 98 80 104Z", shadow=False)
    group(d, "translate(-8 4)", bug)


# ================================================================ concepts
NIGHT_FIX = {"sky": ["deep", "mark", "#1F2A44"]}

CONCEPTS = [
    Concept("walksafari-rhino", "walking-safari", "White rhino", walksafari_rhino,
            overrides={"hero": "#9A928A", "hero2": "#D9CFC0", "mark": "#3A332E"},
            checks=[("hero", "glow"), ("hero", "sky"), ("hero", "ground"), ("hero", "far")],
            fixes={"glow": ["glow2", "light", "far"], "far": ["mid", "near"]}),
    Concept("walksafari-tracks", "walking-safari", "Reading the tracks", walksafari_tracks,
            checks=[("near", "ground"), ("mid", "ground")], fixes={"near": ["deep", "dark"], "mid": ["near", "deep"]}),
    Concept("walksafari-single-file", "walking-safari", "Single file", walksafari_file,
            checks=[("dark", "glow"), ("dark", "near"), ("glow", "sky")], fixes={"near": ["mid", "far"], "glow": ["glow2", "hero2", "#F2A65A"]}),
    Concept("orangutan-face", "orangutan-spotting", "Orangutan", orangutan_face, overrides=ORANG,
            checks=[("hero", "sky"), ("leaf", "sky")], fixes={"sky": ["sky2", "far"]}),
    Concept("orangutan-swing", "orangutan-spotting", "Swinging through the canopy", orangutan_swing, overrides=ORANG,
            checks=[("hero", "sky"), ("hero", "far"), ("dark", "sky")], fixes={"far": ["mid", "sky2"]}),
    Concept("orangutan-leaf-umbrella", "orangutan-spotting", "Leaf umbrella", orangutan_umbrella, overrides=ORANG,
            checks=[("hero", "sky"), ("hero", "far"), ("leaf", "sky"), ("leaf", "far")], fixes={"far": ["mid", "near", "sky2"]}),
    Concept("hatch-egg", "turtle-hatching", "Just hatched", hatch_egg, overrides=HATCH,
            checks=[("egg", "ground"), ("hero", "egg")], fixes={"ground": ["far", "mid", "#E7C78E"]}),
    Concept("hatch-moonlit-dash", "turtle-hatching", "Dash to the sea", hatch_moon, ["dusk", "coastal", "meadow", "blush"],
            overrides={**HATCH, "sky": "#1F2A44", "light": "#E8EDF7", "glow": "#FFF6DA", "glow2": "#FFF6DA"},
            checks=[("far", "sky"), ("hero", "ground"), ("glow", "sky")], fixes={"far": ["mid", "near"]}),
    Concept("hatch-nest", "turtle-hatching", "Inside the nest", hatch_nest, overrides=HATCH,
            checks=[("egg", "deep"), ("hero", "near"), ("hero", "ground"), ("near", "ground")],
            fixes={"near": ["#E2B97C", "mid"], "deep": ["#8A5A3A", "dark"]}),
    Concept("bearwatch-salmon", "bear-watching", "Catching salmon", bearwatch_salmon, ["coastal", "meadow", "dusk", "blush", "golden"],
            overrides=BEAR, checks=[("hero", "deep"), ("hero", "water"), ("fish", "sky")], fixes={"deep": ["far", "mid", "#5C6B73"]}),
    Concept("bearwatch-polar", "bear-watching", "Polar bear", bearwatch_polar,
            overrides={"hero": "#F5EEDC", "hero2": "#D9CBB0", "mark": "#1F1F24", "ice": "#9CC5DB", "ice2": "#E4F1F8"},
            checks=[("hero", "sky"), ("hero", "glow"), ("hero", "ice"), ("hero", "far")],
            fixes={"sky": ["sky2", "#A9CBE0"], "glow": ["glow2", "pop", "hero2"], "far": ["mid", "near"]}),
    Concept("bearwatch-grizzly", "bear-watching", "Grizzly standing tall", bearwatch_standing, overrides=BEAR,
            checks=[("hero", "sky"), ("hero", "mid"), ("hero", "far"), ("hero", "ground")], fixes={"mid": ["far", "near"]}),
    Concept("migration-herd", "great-migration", "The herd", migration_herd,
            checks=[("dark", "glow"), ("dark", "mid"), ("dark", "near")], fixes={"near": ["mid", "far", "ground"]}),
    Concept("migration-river-crossing", "great-migration", "River crossing", migration_river, overrides=GNU,
            checks=[("hero", "sky"), ("hero", "water"), ("dark", "ground"), ("water", "ground")], fixes={"sky": ["sky2", "far"], "ground": ["far", "mid", "#E3C48E"]}),
    Concept("migration-wildebeest", "great-migration", "Wildebeest", migration_face, overrides=GNU,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero2", "glow")], fixes={"glow": ["glow2", "light", "far"]}),
    Concept("reef-coral-garden", "reef-exploring", "Coral garden", reef_garden, ["coastal", "dusk", "meadow"], {**REEF, "hero": "#F28C28"},
            checks=[("fan", "near"), ("coral", "near"), ("sponge", "near"), ("hero", "mid")], fixes={"sponge": ["#7FD1C1", "light"]}),
    Concept("reef-moorish-idol", "reef-exploring", "Moorish idol", reef_idol, ["coastal", "dusk", "meadow"],
            {**REEF, "hero": "#F6C445", "mark": "#1C1C22", "light": "#FFFFFF"}, checks=[("light", "mid"), ("hero", "mid")]),
    Concept("reef-glass-boat", "reef-exploring", "Glass-bottom boat", reef_glassboat, ["coastal", "dusk", "meadow", "blush"], REEF,
            checks=[("hero", "mid"), ("hero", "sky"), ("hero", "near")], fixes={"hero": ["pop", "light", "dark"]}),
    Concept("botanic-palm-house", "botanical-gardens", "Palm house", botanic_glasshouse, overrides=GARDEN,
            checks=[("glass", "sky"), ("glass", "far")], fixes={"sky": ["sky2", "light"]}),
    Concept("botanic-giant-lilies", "botanical-gardens", "Giant water lilies", botanic_lily, overrides=GARDEN,
            checks=[("pad2", "water"), ("light", "pad")]),
    Concept("botanic-bird-of-paradise", "botanical-gardens", "Bird of paradise", botanic_strelitzia,
            overrides={**GARDEN, "spathe": "#4F7A5E", "spathe2": "#9E4A6A", "orange": "#F4892E", "blue": "#3C5DC8"},
            checks=[("orange", "glow"), ("orange", "sky"), ("spathe", "glow")], fixes={"glow": ["light", "sky2", "far"]}),
    Concept("lakeday-dock-chairs", "lake-day", "Dock chairs", lakeday_dock, ["coastal", "meadow", "blush", "dusk"], {**LAKE, "chairA": "#C23B2E", "chairB": "#F7F3EA"},
            checks=[("chairA", "wood"), ("chairB", "wood"), ("wood", "water"), ("chairA", "water"), ("chairB", "water")]),
    Concept("lakeday-canoe", "lake-day", "Red canoe", lakeday_canoe, ["coastal", "meadow", "blush", "dusk"], {**LAKE, "hero": "#D64545", "hero2": "#F4E3C1"},
            checks=[("hero", "water"), ("hero", "pine")]),
    Concept("lakeday-swan-pedalo", "lake-day", "Swan pedalo", lakeday_swan, ["coastal", "meadow", "blush", "dusk"],
            {**LAKE, "swan": "#FFFFFF", "swan2": "#E8EEF2", "beak": "#F28C28", "mark": "#1F1F24"},
            checks=[("swan", "water"), ("swan", "pine"), ("swan", "far")], fixes={"far": ["mid", "near"]}),
    Concept("autumn-maple-leaf", "autumn-leaves", "Maple leaf", autumn_maple, overrides=FALL,
            checks=[("leafA", "glow"), ("leafA", "sky"), ("leafC", "sky")], fixes={"glow": ["light", "sky2"], "sky": ["sky2", "far"]}),
    Concept("autumn-new-england", "autumn-leaves", "New England fall", autumn_newengland, overrides=FALL,
            checks=[("light", "mid"), ("light", "far"), ("leafA", "near"), ("leafC", "near")], fixes={"mid": ["near", "deep"], "near": ["deep", "mid"]}),
    Concept("autumn-golden-avenue", "autumn-leaves", "Golden avenue", autumn_avenue, overrides=FALL,
            checks=[("leafC", "sky"), ("leafB", "ground"), ("light", "ground")], fixes={"sky": ["sky2", "far"], "ground": ["mid", "near"]}),
    Concept("tulip-windmill", "tulip-fields", "Windmill & stripes", tulip_windmill, overrides=TULIP,
            checks=[("mill", "sky"), ("sail", "sky"), ("sail", "far")], fixes={"sky": ["sky2", "far"], "far": ["mid", "near"]}),
    Concept("tulip-bouquet", "tulip-fields", "Three tulips", tulip_bouquet, overrides=TULIP,
            checks=[("tR", "glow"), ("tY", "glow"), ("tP", "glow")], fixes={"glow": ["light", "sky2", "far"]}),
    Concept("tulip-bike", "tulip-fields", "Bike & tulips", tulip_bike, overrides={**TULIP, "hero": "#2F6690", "hero2": "#C9A36A"},
            checks=[("hero", "sky"), ("dark", "ground"), ("hero", "far")], fixes={"far": ["mid", "near"]}),
    Concept("lavender-provence-rows", "lavender-fields", "Provence rows", lavender_rows, overrides={**LAV, "trunk": "#4A3A2A"},
            checks=[("lav", "stone"), ("tree", "sky"), ("tree", "glow"), ("lav", "glow")], fixes={"glow": ["glow2", "pop", "hero2"]}),
    Concept("lavender-bundle", "lavender-fields", "Lavender bunch", lavender_bundle, overrides=LAV,
            checks=[("lav", "light"), ("lav", "sky"), ("ribbon", "lav"), ("ribbon", "light")], fixes={"ribbon": ["#D9A33A", "pop"]}),
    Concept("lavender-bee", "lavender-fields", "Bee on lavender", lavender_bee,
            overrides={**LAV, "beeY": "#F6C445", "beeD": "#2A2420", "wing": "#FFFFFF"},
            checks=[("beeY", "sky"), ("lav", "far"), ("beeY", "lav"), ("lav", "sky")], fixes={"far": ["mid", "near"], "sky": ["sky2"]}),
    Concept("rainbow-over-hills", "rainbow-chasing", "Rainbow over the hills", rainbow_hills, overrides=BOW,
            checks=[("r1", "sky"), ("r6", "sky"), ("light", "mid"), ("r3", "sky")], fixes={"sky": ["sky2", "#DCE9F2"]}),
    Concept("rainbow-sun-cloud", "rainbow-chasing", "Sun, cloud & rainbow", rainbow_cloud, overrides=BOW,
            checks=[("r1", "sky"), ("r6", "sky"), ("light", "sky"), ("r3", "sky")], fixes={"sky": ["far", "sky2", "#BFD8E6"]}),
    Concept("rainbow-road-trip", "rainbow-chasing", "Chasing the rainbow", rainbow_road, overrides=BOW,
            checks=[("r1", "sky"), ("r6", "sky"), ("hero", "dark"), ("dark", "mid"), ("r3", "sky")],
            fixes={"sky": ["sky2", "#DCE9F2"], "hero": ["pop", "hero2", "light"]}),
    Concept("firefly-jar", "fireflies", "Jar of fireflies", firefly_jar, NIGHT_PAL, overrides=FLY,
            checks=[("jar", "sky"), ("lid", "sky"), ("far", "sky")], fixes={"far": ["mid", "near"]}),
    Concept("firefly-forest", "fireflies", "Glowing forest", firefly_forest, NIGHT_PAL, overrides=FLY,
            checks=[("deep", "sky"), ("trunkN", "mid"), ("far", "sky")], fixes={"deep": ["near", "mid"], "mid": ["near", "far"]}),
    Concept("firefly-closeup", "fireflies", "Firefly", firefly_bug, NIGHT_PAL, overrides=FLY,
            checks=[("fly", "sky"), ("bug", "sky"), ("grassN", "far")], fixes={"far": ["mid", "near", "far"]}),
]


def _sk_gnu(d):
    group(d, "translate(10 -60) scale(1.5)", lambda: wildebeest(d))
