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
        d.shape("leaf", leaf(x - 40 * math.cos(math.radians(a)), y - 40 * math.sin(math.radians(a)), 60, 16, a))
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
    d.raw('<g opacity=".55">', "")
    d.band("light", "M-30 130 Q30 112 70 124 T150 118 T230 126", shadow=False, line=False)
    d.raw("</g>", "")
    for x, y, s in [(4, 108, .22), (26, 110, .2), (48, 108, .22), (152, 108, .22), (172, 110, .2)]:
        group(d, f"translate({x} {y}) scale({s})", lambda: d.shape("dark", WILDEBEEST + GNU_EXTRA, shadow=False))
    d.band("mid", hills(136, 4, 30))
    for x, y, s in [(-10, 104, .44), (36, 108, .42), (124, 106, .44), (164, 104, .42)]:
        group(d, f"translate({x} {y}) scale({s})", lambda: d.shape("dark", WILDEBEEST + GNU_EXTRA))
    d.band("near", hills(160, 4, -20))
    for x, y, s in [(14, 100, .66), (96, 96, .7)]:
        group(d, f"translate({x} {y}) scale({s})", lambda: d.shape("dark", WILDEBEEST + GNU_EXTRA))
    d.band("deep", hills(182, 4, 10))


def migration_river(d: Drawing):
    d.disc("glow", 150, 46, 18)
    d.band("far", hills(80, 6))
    # far bank with waiting herd
    d.shape("ground", "M120 200 L120 100 C140 92 180 90 230 92 L230 200Z")
    for x, y, s in [(140, 74, .24), (166, 72, .24), (188, 76, .22)]:
        group(d, f"translate({x} {y}) scale({s})", lambda: d.shape("dark", WILDEBEEST + GNU_EXTRA, shadow=False))
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
            overrides={**HATCH, "glow": "#FFF6DA", "glow2": "#FFF6DA"},
            checks=[("sky", "light"), ("hero", "ground"), ("glow", "sky")], fixes=NIGHT_FIX),
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
]


def _sk_gnu(d):
    group(d, "translate(10 -60) scale(1.5)", lambda: wildebeest(d))
