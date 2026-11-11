"""Animals of Australia & Tasmania: a portrait and a habitat scene for eighteen animals."""
import math

from _common import Concept, Drawing, cloud, fish, circle, ellipse, waves, hills, rrect, group  # noqa: F401

_uid = [0]


# ================================================================ private helpers (copied from wildlife.py, extended)
def _id(prefix):
    _uid[0] += 1
    return f"{prefix}{_uid[0]}"


def clipped(d: Drawing, path: str, fn):
    """Draw fn() clipped to `path`."""
    cid = _id("ozclip")
    tag = f'<clipPath id="{cid}"><path d="{path}"/></clipPath><g clip-path="url(#{cid})">'
    d.raw(tag, tag)
    fn()
    d.raw("</g>", "</g>")


def place(d: Drawing, fn, ax, ay, x, y, s=1.0, flipx=False, rot=0):
    """Draw fn() (designed around anchor ax, ay) at x, y, scaled, optionally mirrored and rotated."""
    sx = -s if flipx else s
    group(d, f"translate({x} {y}) rotate({rot}) scale({sx} {s}) translate({-ax} {-ay})", fn)


def scallop(cx, cy, r, n=12, bump=0.22, rot=0.0):
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


def gum(x, y, a, ln=26):
    """A slender, drooping eucalyptus leaf."""
    return leaf(x, y, ln, ln * 0.2, a)


def gum_sprig(d: Drawing, x, y, ang, n=5, ln=24, role="mid", stem="dark", spot=False, shadow=False):
    """A stem from (x, y) in direction `ang` with leaves hanging off both sides."""
    a = math.radians(ang)
    L = ln * 1.8
    ex, ey = x + math.cos(a) * L, y + math.sin(a) * L
    d.stroke(stem, f"M{x} {y} L{ex:.1f} {ey:.1f}", 2.2)
    for i in range(n):
        t = 0.25 + 0.75 * i / max(n - 1, 1)
        px, py = x + math.cos(a) * L * t, y + math.sin(a) * L * t
        side = 1 if i % 2 else -1
        la = ang + side * 50 + 25
        d.shape(role, gum(px, py, la, ln * (0.8 + 0.2 * (i % 2))), shadow=shadow, spot=spot and i % 2 == 0)


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


def zzz(d: Drawing, x, y, s=1.0, role="mark"):
    p = ""
    for i, k in enumerate((1.0, 0.8, 0.6)):
        w = 8 * s * k
        ox, oy = x + i * 11 * s, y - i * 12 * s
        p += f"M{ox:.1f} {oy:.1f} h{w:.1f} l{-w:.1f} {w:.1f} h{w:.1f} "
    d.stroke(role, p, 2.2)


def tufts(d: Drawing, pts, role="near"):
    """Spiky grass clumps (spinifex, buttongrass) at (x, y, size)."""
    for x, y, s in pts:
        p = f"M{x - 9 * s} {y} "
        for i in range(7):
            ang = math.radians(-160 + i * 23.3)
            p += f"L{x + math.cos(ang) * 13 * s:.1f} {y + math.sin(ang) * 13 * s:.1f} L{x + (i - 3) * 2.4 * s + 1.2 * s:.1f} {y - 2 * s:.1f} "
        p += f"L{x + 9 * s} {y}Z"
        d.shape(role, p, shadow=False, line=False)


def solid(d: Drawing, role, path, shadow=True):
    """Dark-furred parts: paper colour in papercut, solid ink in line style (so a devil doesn't turn into a polar bear)."""
    if d.paper:
        d.shape(role, path, shadow=shadow)
    else:
        d.raw("", f'<path d="{path}" fill="{d.c["ink"]}" stroke="{d.c["ink"]}" stroke-width="3" stroke-linejoin="round"/>')


def hilite(d: Drawing, role, path):
    """Pale markings on a dark animal: role colour in papercut, paper in line style."""
    if d.paper:
        d.marks(role, path)
    else:
        d.raw("", f'<path d="{path}" fill="{d.c["paper"]}"/>')


def inklimb(d: Drawing, role, path, w):
    """A limb on a dark animal: solid ink in line style."""
    if d.paper:
        d.limb(role, path, w)
    else:
        d.raw("", f'<path d="{path}" fill="none" stroke="{d.c["ink"]}" stroke-width="{w + 2}" stroke-linecap="round" stroke-linejoin="round"/>')


# ================================================================ KANGAROO
# Standing upright, facing right, feet on y=172.
ROO_UP = ("M18 176 C30 174 42 166 48 152 C44 130 48 104 58 88 C64 76 72 66 76 60 C78 52 84 46 92 46 "
          "C98 46 104 50 110 54 C114 56 114 60 110 62 L98 64 C92 68 88 72 86 78 C82 94 84 114 80 132 "
          "C86 138 92 146 90 156 L80 164 L104 165 C109 166 110 171 105 172 L60 172 C55 172 54 166 56 162 "
          "C46 170 32 176 18 176Z")
ROO_EARS = "M80 52 L73 30 C72 26 77 25 79 29 L87 48Z M87 48 L88 27 C88 23 93 23 93 27 L92 49Z"


def roo_up(d: Drawing, arms="box"):
    d.shape("hero", ROO_EARS)
    if arms == "box":
        d.limb("hero", "M84 92 L98 100 L112 90", 5.5, shadow=False)
    d.shape("hero", ROO_UP)
    d.shape("hero2", "M86 80 C84 100 85 118 80 132 C76 120 76 98 81 84Z", shadow=False)
    d.shape("hero2", "M79 31 L83 46 L86 46 L81 30Z", shadow=False, line=False)
    d.marks("mark", circle(97, 54, 2) + "M108 56 L112 58 L109 61Z")
    if arms == "box":
        d.limb("hero", "M84 84 L100 88 L114 78", 6)
        d.shape("mark", circle(115, 77, 4), shadow=False)
        d.shape("mark", circle(113, 89, 3.5), shadow=False)
    else:
        d.limb("hero", "M84 86 L92 104 L99 107", 5.5)
        d.marks("mark", circle(100, 107.5, 2.5))


def kangaroo_boxing(d: Drawing):
    d.disc("glow", 100, 104, 46)
    birds(d, [(36, 52, 1), (52, 44, 0.8)])
    d.band("far", hills(150, 6))
    for x in (24, 174):
        d.shape("near", f"M{x} 152 l3 -10 l3 8 l3 -12 l3 12 l3 -8 l3 10Z", shadow=False, line=False)
    place(d, lambda: roo_up(d), 110, 172, 92, 166, 0.78, rot=-7)
    place(d, lambda: roo_up(d), 110, 172, 108, 166, 0.78, flipx=True, rot=7)
    d.band("ground", hills(166, 3))
    d.band("deep", hills(184, 3, 30), line=False)


def kangaroo_beach(d: Drawing):
    d.disc("glow", 134, 98, 26)
    d.shape("light", cloud(24, 56, 0.9), shadow=False)
    d.band("far", "M-30 108 L230 108", line=False)
    d.shape("near", "M-30 112 C-10 96 6 74 26 72 C40 70 52 84 62 98 L74 112Z")
    d.shape("deep", "M8 80 q4 -8 8 0 q4 -8 8 0 M30 74 q4 -8 8 0", shadow=False, line=False)
    d.band("mid", waves(112, 2, 30))
    d.stroke("glow2", "M118 120 H150 M124 127 H144 M128 134 H140", 2.4, line=False)
    d.band("near", waves(140, 3, 36), line=False)
    d.band("ground", "M-30 148 Q60 140 120 146 T230 144")
    place(d, lambda: roo_up(d, arms="down"), 60, 172, 158, 168, 0.42, flipx=True)
    place(d, lambda: roo_up(d, arms="down"), 60, 172, 76, 172, 0.84)
    d.stroke("deep", "M150 176 l4 -2 M160 180 l4 -2 M120 184 l4 -2", 1.6, line=False)


# ================================================================ KOALA
def koala_head(d: Drawing, cx, cy, s=1.0, sleepy=False, leaf_in_mouth=False, rot=0):
    def draw():
        for ex in (58, 142):
            d.shape("hero", scallop(ex, 60, 23, 10, 0.13))
            d.shape("light", scallop(ex, 62, 13, 8, 0.12), shadow=False)
        d.shape("hero", "M100 44 C136 44 152 68 152 94 C152 122 130 140 100 140 C70 140 48 122 48 94 C48 68 64 44 100 44Z")
        d.shape("hero2", "M64 112 C70 128 84 138 100 138 C116 138 130 128 136 112 C124 122 112 126 100 126 C88 126 76 122 64 112Z", shadow=False, line=False)
        d.marks("mark", "M100 80 C111 80 116 92 116 104 C116 117 109 124 100 124 C91 124 84 117 84 104 C84 92 89 80 100 80Z")
        d.marks("light", ellipse(94, 92, 2.5, 5))
        if sleepy:
            d.stroke("mark", "M64 96 Q71 102 78 96 M122 96 Q129 102 136 96", 2.6)
        else:
            d.marks("mark", circle(72, 94, 4.5) + circle(128, 94, 4.5))
            d.marks("light", circle(73.6, 92.4, 1.4) + circle(129.6, 92.4, 1.4))
        if leaf_in_mouth:
            d.shape("mid", gum(98, 131, 160, 34), shadow=False, spot=True)
        else:
            d.stroke("mark", "M92 131 Q100 135 108 131", 2)
    group(d, f"translate({cx} {cy}) rotate({rot}) scale({s}) translate(-100 -94)", draw)


def koala_fork(d: Drawing):
    d.disc("glow", 152, 52, 20)
    d.band("far", hills(170, 6))
    # eucalyptus fork
    d.limb("dark", "M102 220 C100 180 102 150 100 130 C92 100 70 70 52 20", 18)
    d.limb("dark", "M100 132 C112 104 132 80 160 40", 14)
    d.limb("dark", "M66 56 C54 50 40 50 24 54", 5)
    d.limb("dark", "M140 70 C152 70 164 76 176 88", 5)
    for x, y, a in [(30, 54, 100), (40, 52, 70), (24, 56, 130), (50, 52, 115)]:
        d.shape("mid", gum(x, y, a, 26), shadow=False, spot=True)
    for x, y, a in [(160, 80, 70), (170, 84, 110), (176, 88, 85), (150, 74, 95)]:
        d.shape("mid", gum(x, y, a, 26), shadow=False)
    # koala wedged in the fork, asleep with its head on the right branch
    d.shape("hero", "M68 120 C64 96 80 84 100 86 C122 88 134 104 130 128 C126 148 112 156 98 156 C80 156 70 140 68 120Z")
    d.shape("light", "M86 120 C86 108 94 100 102 100 C112 102 116 112 114 126 C110 140 100 146 94 144 C88 140 86 132 86 120Z", shadow=False, line=False)
    d.limb("hero", "M76 132 C70 140 70 150 80 154", 10)
    d.limb("hero", "M120 140 C126 148 124 154 116 158", 10)
    koala_head(d, 110, 92, 0.46, sleepy=True, rot=18)
    d.limb("hero", "M112 112 C126 108 134 100 138 92", 10)
    d.marks("mark", circle(139, 89, 1.3) + circle(141.5, 92, 1.3))
    zzz(d, 146, 120, 0.9)


def koala_munch(d: Drawing):
    for x, y, a in [(-6, 40, 30), (0, 80, 10), (206, 44, 150), (204, 86, 170), (-4, 140, -20), (204, 140, 200)]:
        d.shape("near", gum(x, y, a, 50), line=False)
    d.limb("dark", "M-10 186 C40 178 140 178 210 186", 12)
    # body, sitting front-on
    d.shape("hero", "M50 200 C46 160 60 124 100 120 C140 124 154 160 150 200Z")
    d.shape("light", "M76 200 C74 168 84 142 100 140 C116 142 126 168 124 200Z", shadow=False)
    d.shape("hero", ellipse(68, 186, 16, 10))
    d.shape("hero", ellipse(132, 186, 16, 10))
    # gum sprig held up to the mouth
    d.stroke("dark", "M96 172 C98 150 100 136 104 120", 2.4)
    for x, y, a, ln in [(97, 160, 200, 28), (98, 150, -20, 26), (100, 142, 190, 22), (101, 136, -30, 22)]:
        d.shape("mid", gum(x, y, a, ln), shadow=False, spot=True)
    koala_head(d, 100, 82, 0.8, leaf_in_mouth=True)
    d.limb("hero", "M66 148 C76 160 86 162 96 156", 12)
    d.limb("hero", "M134 148 C124 160 114 162 104 156", 12)
    d.marks("mark", circle(97, 153, 1.4) + circle(98, 158, 1.4) + circle(103, 153, 1.4) + circle(102, 158, 1.4))


# ================================================================ WOMBAT
WOMBAT = ("M44 132 C38 110 50 84 84 80 C110 76 132 80 146 86 C154 80 166 80 174 88 C181 95 185 104 183 112 "
          "C181 120 173 124 165 122 C159 128 152 132 150 138 L150 152 L134 152 L132 142 C114 146 90 146 74 144 "
          "L72 152 L56 152 L54 141 C48 139 46 136 44 132Z")


def wombat(d: Drawing):
    d.shape("hero", "M150 88 C147 76 154 70 161 73 C164 77 162 84 159 89Z")
    d.shape("hero", "M158 86 C158 74 166 70 171 76 C172 81 168 86 165 90Z")
    d.shape("hero", WOMBAT)
    d.shape("hero2", "M62 92 C80 84 110 82 136 88 C120 86 92 88 70 98Z", shadow=False, line=False)
    d.shape("hero2", "M152 94 C160 88 170 92 172 100 C166 98 158 98 152 94Z", shadow=False, line=False)
    d.marks("mark", "M174 95 C182 97 186 105 184 112 C181 117 175 117 172 113 C169 107 169 100 174 95Z")
    d.marks("mark", circle(162, 99, 2.6))
    d.marks("light", circle(162.8, 98.2, 0.8))
    d.stroke("mark", "M168 118 Q172 120 176 118", 1.4)
    d.stroke("mark", "M136 152 l-2 3 M141 152 l-1 3 M146 152 l0 3 M58 152 l-2 3 M63 152 l-1 3 M68 152 l0 3", 1.4, line=False)


def wombat_portrait(d: Drawing):
    d.disc("glow", 64, 70, 30)
    d.band("far", hills(132, 8))
    tufts(d, [(30, 134, 1), (176, 130, 0.9)], "near")
    d.band("ground", hills(150, 3))
    place(d, lambda: wombat(d), 114, 152, 98, 156, 1.0)
    grass(d, 20, 70, 168, 12, "near")
    grass(d, 130, 186, 166, 12, "near")
    d.band("deep", hills(178, 3, 30), line=False)


CRADLE = ("M-30 112 L8 104 L24 92 L36 94 L48 72 L54 76 L60 58 L64 62 L68 50 L74 56 L78 46 L84 56 L88 52 L94 66 "
          "L104 70 L112 84 L122 80 L132 90 L150 92 L162 100 L190 98 L230 108")


def wombat_hut(d: Drawing):
    d.shape("light", cloud(130, 44, 1.0), shadow=False)
    d.band("far", CRADLE)
    d.band("mid", "M-30 106 Q60 96 120 104 T230 102")
    d.band("sky2", "M-30 118 L230 118", line=False)
    d.stroke("light", "M30 124 H52 M130 124 H160 M90 128 H110", 2, line=False)
    # Dove Lake boatshed
    d.stroke("dark", "M42 120 V128 M54 120 V128 M66 120 V128", 2)
    d.shape("pop", "M38 96 L60 96 L72 96 L72 120 L38 120Z")
    d.shape("dark", "M34 99 L55 82 L76 99 L72 99 L55 86 L38 99Z")
    d.shape("dark", "M48 104 H62 V120 H48Z", shadow=False)
    d.stroke("dark", "M38 108 H46 M64 108 H72 M38 114 H46 M64 114 H72", 1, line=False)
    d.band("near", "M-30 140 Q40 128 100 134 T230 130")
    tufts(d, [(22, 142, 0.8), (178, 136, 0.9), (150, 140, 0.6)], "deep")
    place(d, lambda: wombat(d), 114, 152, 108, 168, 0.66)
    d.band("ground", hills(180, 2), line=False)
    grass(d, 40, 90, 182, 10, "deep")


# ================================================================ TASMANIAN DEVIL
def devil_face(d: Drawing):
    d.disc("glow", 100, 90, 70, line=False)
    # shoulders and chest with the white crescent
    solid(d, "hero", "M20 210 C24 170 56 146 100 146 C144 146 176 170 180 210Z")
    d.shape("light", "M52 178 C70 166 130 166 148 178 C150 184 146 188 140 186 C120 178 80 178 60 186 C54 188 50 184 52 178Z", shadow=False, spot=True)
    # ears: pink, rounded
    for ex, rot in ((56, -28), (144, 28)):
        d.raw(f'<g transform="rotate({rot} {ex} 56)">', f'<g transform="rotate({rot} {ex} 56)">')
        solid(d, "hero", ellipse(ex, 56, 17, 22))
        d.shape("pop", ellipse(ex, 58, 10, 15), shadow=False, spot=True)
        d.raw("</g>", "</g>")
    # broad head
    solid(d, "hero", "M100 46 C136 46 154 66 156 92 C158 116 146 140 126 152 C116 158 84 158 74 152 C54 140 42 116 44 92 C46 66 64 46 100 46Z")
    d.shape("hero2", "M100 66 C114 66 122 76 122 88 L78 88 C78 76 86 66 100 66Z", shadow=False, line=False)
    # wide-open mouth with teeth
    d.shape("mark", "M66 104 C80 98 120 98 134 104 C132 126 120 144 100 146 C80 144 68 126 66 104Z")
    d.shape("pop", "M80 132 C88 124 112 124 120 132 C114 140 106 144 100 144 C94 144 86 140 80 132Z", shadow=False)
    d.shape("light", "M70 104 l4 9 l4 -9Z M80 102 l3 7 l3 -7Z M114 102 l3 7 l3 -7Z M122 104 l4 9 l4 -9Z "
                     "M74 128 l4 -9 l4 9Z M118 128 l4 -9 l4 9Z", shadow=False)
    if d.paper:
        d.marks("mark", ellipse(100, 92, 10, 6.5))
    else:
        d.raw("", f'<path d="{ellipse(100, 92, 10, 6.5)}" fill="{d.c["ink"]}" stroke="{d.c["paper"]}" stroke-width="2"/>')
    for ex in (78, 122):
        if d.paper:
            d.marks("mark", circle(ex, 78, 5.5))
            d.marks("light", circle(ex + 1.6, 76.4, 1.6))
        else:
            hilite(d, "light", circle(ex, 78, 5.5))
            d.marks("mark", circle(ex, 79, 3.2))
    if d.paper:
        d.marks("light", ellipse(97, 90, 3, 1.6))
    d.stroke("light", "M60 100 L36 96 M60 106 L34 108 M140 100 L164 96 M140 106 L166 108", 1.2, line=False)


DEVIL_SIDE = ("M54 118 C54 104 66 94 82 94 C98 92 112 92 124 94 C130 86 140 82 150 84 C162 86 170 92 176 100 "
              "L180 108 C178 113 172 115 164 115 C158 121 152 124 148 126 L148 146 L136 146 L134 130 "
              "C118 132 100 132 84 130 L82 146 L70 146 L68 128 C60 126 56 123 54 118Z")


def devil_side(d: Drawing):
    inklimb(d, "hero", "M60 110 C50 114 42 118 34 126", 9)
    solid(d, "hero", DEVIL_SIDE)
    hilite(d, "light", "M132 100 C142 104 148 114 147 127 L140 128 C140 118 136 108 128 102Z")
    d.raw('<g transform="rotate(-20 146 80)">', '<g transform="rotate(-20 146 80)">')
    solid(d, "hero", ellipse(146, 80, 7, 9), shadow=False)
    d.shape("pop", ellipse(146, 81, 4, 6), shadow=False, spot=True)
    d.raw("</g>", "</g>")
    if d.paper:
        d.marks("pop", circle(179, 106, 2.4))
    hilite(d, "light", circle(160, 96, 2.6))
    d.marks("mark", circle(160.5, 96, 1.5))
    d.stroke("pop", "M166 112 Q172 116 178 112", 1.6, line=False)


def devil_cradle(d: Drawing):
    d.disc("glow", 160, 48, 18)
    d.band("far", CRADLE.replace("L230 108", "L230 104"))
    d.shape("light", "M68 50 L74 56 L78 46 L84 56 L88 52 L92 62 L84 60 L78 54 L72 60Z", shadow=False, line=False)
    d.band("mid", hills(120, 6))
    tufts(d, [(150, 118, 0.8), (174, 120, 0.7), (40, 122, 0.7)], "near")
    # rocks and the boardwalk trail
    d.shape("near", "M-20 200 L-10 150 Q10 132 40 136 L90 140 Q110 142 116 156 L120 200Z")
    d.shape("deep", "M120 168 L134 140 L190 140 L208 168Z", line=False)
    d.stroke("light", "M136 146 H188 M132 152 H192 M128 158 H196", 1.4, line=False)
    place(d, lambda: devil_side(d), 100, 146, 82, 144, 0.82)
    d.band("ground", hills(176, 3))
    tufts(d, [(130, 178, 1), (176, 180, 0.8)], "deep")


# ================================================================ PLATYPUS
PLATY_BODY = "M52 96 C62 80 92 76 118 80 C136 83 148 88 154 98 C152 110 136 118 112 120 C86 122 64 116 52 106Z"


def platypus(d: Drawing):
    d.shape("hero", "M66 112 L58 128 L50 131 L55 133 L60 131 L63 135 L68 131 L72 132 L76 114Z")  # far front foot
    d.shape("hero", "M138 94 C158 86 186 86 194 96 C198 106 186 112 166 110 C154 110 144 108 138 106Z")  # flat tail
    d.stroke("mark", "M150 98 H186", 1.2, line=False)
    d.shape("hero", PLATY_BODY)
    d.shape("hero2", "M58 106 C70 114 96 118 116 116 C134 114 146 108 152 102 C148 112 134 118 112 120 C86 122 66 116 58 106Z", shadow=False, line=False)
    d.shape("hero", "M128 112 L144 126 L152 124 L148 128 L154 130 L142 132 L122 116Z")  # hind foot
    d.shape("hero", "M84 112 L80 130 L72 134 L78 136 L82 133 L86 138 L90 133 L95 134 L94 114Z")  # near front foot
    d.shape("mark", "M58 92 C44 86 22 86 12 92 C6 96 8 104 14 106 C28 109 44 108 58 106Z", spot=True)  # bill
    d.shape("hero", "M50 90 C54 86 60 86 62 92 C62 100 60 106 54 108 C50 104 48 96 50 90Z", shadow=False)
    d.stroke("hero2", "M18 96 Q32 98 46 97", 1.4, line=False)
    d.marks("mark", circle(68, 92, 2.2))
    d.marks("light", circle(68.7, 91.3, 0.7))


def platypus_portrait(d: Drawing):
    d.band("sky2", waves(30, 4, 26))
    d.band("far", waves(56, 4, 28))
    d.raw('<g opacity=".16" fill="#fff"><path d="M70 0 L90 0 L130 200 L110 200Z"/><path d="M130 0 L140 0 L180 200 L170 200Z"/></g>', "")
    d.band("mid", waves(150, 4, 30), line=False)
    for x in (18, 30, 174, 186):
        d.stroke("near", f"M{x} 190 Q{x + 4} 150 {x - 2} {120 + (x % 7) * 3}", 3)
    d.band("ground", "M-30 170 Q40 160 90 168 T230 164")
    d.shape("near", ellipse(140, 172, 18, 8))
    d.shape("deep", ellipse(54, 176, 14, 6))
    place(d, lambda: platypus(d), 100, 104, 102, 104, 0.88, rot=-6)
    for x, y, r in [(16, 84, 2.5), (22, 72, 3.5), (18, 58, 2)]:
        d.stroke("light", circle(x, y, r), 2)


def platypus_creek(d: Drawing):
    d.disc("glow", 140, 48, 18)
    d.band("far", "M-30 92 Q30 70 80 82 T170 74 T230 80")
    # tree ferns on the far bank
    for x, h in [(26, 44), (170, 38)]:
        d.limb("dark", f"M{x} 112 L{x + 2} {112 - h}", 4.5)
        for a in (-160, -130, -100, -70, -40, -15, 15, 195):
            d.shape("near", leaf(x + 2, 112 - h, 26, 4.5, a), shadow=False)
    d.band("mid", "M-30 112 Q60 104 120 110 T230 108")
    d.band("sky2", "M-30 122 L230 122", line=False)
    place(d, lambda: platypus(d), 100, 104, 104, 122, 0.9)
    d.band("near", "M-30 128 L230 128", line=False)
    d.stroke("near", "M-30 128 H230", 2.4, line=False)
    d.stroke("light", "M30 140 L60 136 M150 136 L190 142 M40 150 L76 144 M140 146 L180 154 M62 160 L90 154", 2.2)
    d.band("deep", waves(170, 3, 36), line=False)


# ================================================================ ECHIDNA
def echidna(d: Drawing):
    cx, cy, rx, ry = 112, 122, 46, 32
    d.shape("hero", "M70 128 C70 104 90 90 112 90 C138 90 158 104 158 128 C158 136 152 140 144 140 L80 140 C74 140 70 136 70 128Z")
    spikes, tips, flat = "", "", ""
    n = 21
    for i in range(n):
        a = math.radians(184 + i * (172 / (n - 1)))
        h = math.radians(4.2)
        k = 1.34 if i % 2 else 1.24
        b1 = (cx + rx * 0.92 * math.cos(a - h), cy + ry * 0.92 * math.sin(a - h))
        b2 = (cx + rx * 0.92 * math.cos(a + h), cy + ry * 0.92 * math.sin(a + h))
        tp = (cx + rx * k * math.cos(a), cy + ry * k * math.sin(a))
        mid1 = [b1[j] + (tp[j] - b1[j]) * 0.66 for j in (0, 1)]
        mid2 = [b2[j] + (tp[j] - b2[j]) * 0.66 for j in (0, 1)]
        spikes += f"M{b1[0]:.1f} {b1[1]:.1f} L{tp[0]:.1f} {tp[1]:.1f} L{b2[0]:.1f} {b2[1]:.1f}Z "
        tips += f"M{mid1[0]:.1f} {mid1[1]:.1f} L{tp[0]:.1f} {tp[1]:.1f} L{mid2[0]:.1f} {mid2[1]:.1f}Z "
    for i in range(14):
        a = math.radians(196 + i * 11)
        r0, r1 = 0.35 + 0.2 * (i % 3) / 2, 0.82
        flat += (f"M{cx + rx * r0 * math.cos(a):.1f} {cy + 4 + ry * r0 * math.sin(a):.1f} "
                 f"L{cx + rx * r1 * math.cos(a):.1f} {cy + 4 + ry * r1 * math.sin(a):.1f} ")
    d.shape("hero2", spikes, spot=True)
    d.marks("mark", tips)
    d.stroke("hero2", flat, 3.2, line=False)
    d.stroke("hero2", flat, 1.6)
    # head and long snout
    d.shape("hero", "M84 112 C76 112 68 118 64 124 C52 128 38 134 22 140 C19 142 20 145 24 145 C40 144 58 140 70 138 C78 140 86 138 90 132Z")
    d.shape("mark", "M40 133 C32 136 26 138 22 140 C19 142 20 145 24 145 C30 145 36 144 42 142Z", shadow=False, line=False)
    d.marks("mark", circle(74, 124, 2))
    # stubby legs with claws
    d.limb("hero", "M86 136 L82 148", 9)
    d.limb("hero", "M140 136 L146 148", 9)
    d.stroke("mark", "M76 152 l-3 2 M80 153 l-2 3 M84 153 l-1 3 M144 153 l2 3 M148 153 l3 2 M151 151 l4 1", 1.6)


def echidna_portrait(d: Drawing):
    d.disc("glow", 108, 112, 60)
    d.band("far", hills(146, 6))
    d.band("ground", hills(154, 3))
    place(d, lambda: echidna(d), 110, 150, 104, 162, 1.12)
    tufts(d, [(176, 160, 0.9), (22, 162, 0.8)], "near")
    d.band("deep", hills(178, 3, 20), line=False)


def grass_tree(d: Drawing, x, y, h, s=1.0):
    d.limb("dark", f"M{x} {y} L{x + 1} {y - h}", 9 * s)
    top = y - h
    p = ""
    for i in range(13):
        a = math.radians(-180 + i * 15)
        ln = 30 * s
        ex, ey = x + math.cos(a) * ln, top + math.sin(a) * ln * 0.75 + abs(math.cos(a)) * 14 * s
        p += f"M{x} {top} Q{x + math.cos(a) * ln * 0.6:.1f} {top + math.sin(a) * ln * 0.75 - 6 * s:.1f} {ex:.1f} {ey:.1f} "
    d.stroke("near", p, 2.2)
    d.limb("dark", f"M{x} {top} L{x} {top - 46 * s}", 3 * s)
    d.limb("hero2", f"M{x} {top - 18 * s} L{x} {top - 44 * s}", 5 * s, shadow=False)


def echidna_bush(d: Drawing):
    d.disc("glow", 60, 54, 20)
    d.band("far", hills(104, 10))
    grass_tree(d, 150, 138, 26, 1.0)
    grass_tree(d, 36, 128, 16, 0.7)
    d.band("mid", hills(140, 4, 20))
    # termite mound with ants
    d.shape("ground", "M10 160 C16 134 24 118 32 116 C40 116 48 134 54 160Z")
    d.stroke("deep", "M24 134 Q30 132 34 136 M20 148 Q30 144 40 148", 1.6, line=False)
    place(d, lambda: echidna(d), 110, 150, 112, 164, 0.8)
    d.marks("mark", circle(56, 156, 1.4) + circle(62, 160, 1.4) + circle(50, 162, 1.4) + circle(58, 166, 1.2))
    d.band("ground", hills(164, 3))
    d.band("deep", hills(182, 3, 20), line=False)



# ================================================================ QUOKKA
def quokka_face(d: Drawing):
    for ex, r in ((70, -18), (130, 18)):
        d.shape("hero", ellipse(ex, 50, 11, 14), extra=f'transform="rotate({r} {ex} 50)"')
        d.shape("mark2", ellipse(ex, 52, 6, 9), extra=f'transform="rotate({r} {ex} 52)"', shadow=False, line=False)
    d.shape("hero", "M100 54 C124 54 138 70 142 88 C150 96 150 110 140 116 C134 132 118 140 100 140 C82 140 66 132 60 116 "
                    "C50 110 50 96 58 88 C62 70 76 54 100 54Z")
    d.shape("hero2", "M84 124 C90 132 110 132 116 124 C114 134 106 138 100 138 C94 138 86 134 84 124Z", shadow=False, line=False)
    d.stroke("hero2", "M60 104 l-6 2 M60 110 l-5 5 M140 104 l6 2 M140 110 l5 5", 1.6, line=False)
    d.marks("mark", "M91 104 C91 99 109 99 109 104 C109 109 103 113 100 113 C97 113 91 109 91 104Z")
    d.marks("light", ellipse(96, 103, 2.4, 1.3))
    d.shape("pop", "M88 118 C94 121 106 121 112 118 C110 126 104 130 100 130 C96 130 90 126 88 118Z", shadow=False, spot=True)
    d.stroke("mark", "M100 113 V118 M84 115 Q100 124 116 115", 2)
    for ex in (80, 120):
        d.marks("mark", circle(ex, 86, 5.5))
        d.marks("light", circle(ex + 1.8, 84.2, 1.8))
    d.stroke("pop", "M70 106 h0.1 M130 106 h0.1", 8, line=False)


def quokka_selfie(d: Drawing):
    d.disc("glow", 160, 62, 16)
    d.band("far", "M-30 150 L230 150")
    d.band("mid", "M-30 162 Q60 156 120 160 T230 158", line=False)
    d.band("ground", "M-30 172 Q60 164 120 170 T230 168")
    # body and paws
    d.shape("hero", "M54 210 C52 170 70 140 100 136 C130 140 148 170 146 210Z")
    d.shape("hero2", "M74 210 C72 178 84 156 100 152 C116 156 128 178 126 210Z", shadow=False)
    d.limb("hero", "M72 156 C80 166 88 168 96 166", 10)
    d.limb("hero", "M128 156 C120 166 112 168 104 166", 10)
    d.marks("mark", circle(95, 164, 1.3) + circle(105, 164, 1.3))
    quokka_face(d)
    # phone camera frame
    d.stroke("dark", "M36 62 V44 H54 M146 44 H164 V62 M36 150 V168 H54 M164 150 V168 H146", 3.4)
    d.marks("pop", circle(48, 56, 3.4))


QUOKKA_SIDE = ("M54 160 C40 142 42 114 62 100 C68 96 72 92 74 86 C76 74 86 66 98 66 C108 66 116 72 120 80 "
               "L128 86 C132 88 132 94 128 96 L116 98 C112 104 106 106 100 108 C106 120 108 134 104 146 "
               "L120 152 C126 154 126 160 120 160Z")


def quokka_side(d: Drawing):
    d.shape("hero", "M58 152 C46 156 34 160 22 160 C32 166 48 166 60 160Z")
    d.shape("hero", circle(88, 68, 9))
    d.shape("hero2", circle(88, 69, 5), shadow=False, line=False)
    d.shape("hero", QUOKKA_SIDE)
    d.shape("hero2", "M100 110 C106 122 106 136 102 146 C94 140 90 124 94 112Z", shadow=False, line=False)
    d.shape("hero", circle(98, 66, 8), shadow=False)
    d.shape("hero2", circle(98, 67, 4.5), shadow=False, line=False)
    d.limb("hero", "M98 110 L108 122 L113 121", 6)
    d.marks("mark", circle(108, 82, 2.6) + "M126 86 C130 87 132 90 130 93 L126 92Z")
    d.marks("light", circle(109, 81, 0.9))
    d.stroke("mark", "M116 96 Q121 100 126 96", 1.6)


def quokka_rottnest(d: Drawing):
    d.disc("glow", 150, 52, 18)
    # Wadjemup lighthouse on the hill
    d.band("far", "M-30 100 Q20 82 60 90 T130 100 T230 98")
    d.shape("light", "M38 88 L40 58 L48 58 L50 88Z")
    d.shape("dark", rrect(37, 50, 14, 9, 2))
    d.shape("dark", "M38 50 Q44 42 50 50Z", shadow=False)
    d.band("mid", "M-30 112 L230 112")
    d.stroke("light", "M120 120 H150 M30 124 H56 M150 130 H176", 2, line=False)
    d.band("near", waves(134, 2, 40), line=False)
    d.band("ground", "M-30 142 Q60 132 120 140 T230 136")
    d.shape("light", "M120 168 C124 150 150 146 176 150 C190 154 196 164 196 180Z", line=False)
    place(d, lambda: quokka_side(d), 80, 160, 92, 166, 0.92)
    d.band("deep", hills(184, 3, 20), line=False)


# ================================================================ CASSOWARY
def cassowary_head(d: Drawing):
    for x, y, a in [(-10, 30, 30), (-6, 80, 10), (210, 40, 150), (206, 96, 170), (-6, 130, -10), (6, 170, -30)]:
        d.shape("near", leaf(x, y, 64, 15, a), line=False)
    d.shape("mid", leaf(200, 140, 50, 12, 200), line=False)
    solid(d, "dark", "M50 210 C52 176 84 150 128 150 C172 152 196 180 198 210Z")
    d.stroke("hero2", "M80 172 L76 186 M100 162 L98 180 M124 160 L126 178 M148 164 L152 180 M170 174 L176 188", 2, line=False)
    d.shape("hero", "M102 162 C98 134 92 112 86 92 L118 84 C124 106 136 132 146 158Z")
    d.shape("pop", "M114 86 C124 104 134 126 146 152 C136 140 126 122 118 106 C116 100 112 92 110 88Z", shadow=False, spot=True)
    d.shape("hero", "M74 74 C76 60 90 52 104 54 C118 56 124 68 122 82 C120 94 108 100 96 100 C84 100 74 90 74 74Z")
    d.shape("casque", "M80 66 C76 44 84 22 98 12 C112 20 120 40 118 64 C108 58 92 58 80 66Z")
    d.stroke("dark", "M96 18 C92 32 92 48 94 60", 1.4, line=False)
    d.shape("dark", "M80 66 C68 68 56 74 46 84 C58 84 72 84 82 82Z")
    d.stroke("light", "M52 81 L78 78", 1.2, line=False)
    d.shape("pop", "M88 96 C84 108 84 124 92 128 C98 124 98 110 94 98Z")
    d.shape("pop", "M96 98 C94 110 96 122 102 124 C106 118 104 106 100 98Z", spot=True)
    d.marks("eye", circle(98, 74, 5))
    d.marks("mark", circle(98, 74, 2.6))
    d.marks("light", circle(99, 73, 1))


CASS_BODY = ("M60 118 C60 90 90 76 124 78 C156 80 178 98 180 122 L174 128 L170 122 L164 132 L158 124 L150 134 "
             "L144 124 L136 134 L130 124 L122 134 L116 124 L108 132 L102 122 L94 130 L88 120 L80 128 L74 118 L66 124Z")


def cassowary_full(d: Drawing):
    d.limb("leg", "M126 124 L136 152 L128 178", 8)
    d.stroke("leg", "M128 178 L114 180 M128 178 L122 184 M128 178 L136 182", 3)
    solid(d, "dark", CASS_BODY)
    d.stroke("hero2", "M90 100 L86 116 M110 92 L108 112 M132 92 L134 112 M154 98 L158 114", 1.6, line=False)
    d.limb("leg", "M104 124 L96 152 L104 178", 9)
    d.stroke("leg", "M104 178 L90 180 M104 178 L98 184 M104 178 L112 182", 3.4)
    d.shape("hero", "M66 104 C62 86 58 72 54 56 L72 52 C74 68 82 86 92 98Z")
    d.shape("pop", "M70 54 C74 70 80 84 92 98 C82 92 74 80 68 66Z", shadow=False, spot=True)
    d.shape("hero", ellipse(62, 48, 13, 10))
    d.shape("casque", "M52 46 C48 32 54 18 62 12 C72 18 76 32 72 46 C66 42 58 42 52 46Z")
    d.shape("dark", "M52 46 C44 48 38 52 32 58 C40 58 48 58 54 55Z")
    d.shape("pop", "M58 58 C55 66 56 74 60 76 C64 72 63 64 61 58Z", spot=True)
    d.marks("mark", circle(62, 46, 2))


def cassowary_forest(d: Drawing):
    d.band("far", "M-30 120 Q50 100 100 110 T230 104", line=False)
    for x, y, a, r in [(-8, 20, 30, "mid"), (-10, 70, 0, "near"), (208, 30, 150, "mid"), (210, 80, 180, "near"),
                       (150, -4, 100, "near"), (40, -6, 70, "near")]:
        d.shape(r, leaf(x, y, 66, 16, a), line=False)
    d.limb("deep", "M168 200 C166 160 170 130 168 90", 10)
    d.band("ground", hills(166, 3))
    for x, y, a in [(4, 176, -40), (190, 174, -140), (16, 180, -70)]:
        d.shape("near", leaf(x, y, 40, 9, a), shadow=False, line=False)
    place(d, lambda: cassowary_full(d), 100, 180, 100, 178, 0.92)


# ================================================================ EMU
EMU_BODY = ("M76 96 C80 72 104 62 130 64 C158 66 174 84 170 108 C168 122 162 128 156 132 L152 124 L148 136 "
            "L142 126 L136 138 L130 128 L124 138 L118 128 L112 138 L106 128 L100 134 L96 124 C84 120 74 110 76 96Z")


def emu(d: Drawing, run=False):
    if run:
        d.limb("leg", "M134 128 L152 146 L176 156", 6)
        d.stroke("leg", "M176 156 L184 154 M176 156 L182 160", 2.4)
    else:
        d.limb("leg", "M136 128 L146 152 L138 180", 6)
        d.stroke("leg", "M138 180 L126 181 M138 180 L132 185 M138 180 L146 183", 2.6)
    d.shape("hero", EMU_BODY)
    fl = ""
    for row, y in enumerate(range(78, 132, 11)):
        for x in range(86 + (row % 2) * 7, 172, 14):
            fl += f"M{x} {y} q2 5 -1 9 "
    clipped(d, EMU_BODY, lambda: d.stroke("hero2", fl, 1.8, line=False))
    if run:
        d.limb("leg", "M114 128 L100 150 L82 172", 6.5)
        d.stroke("leg", "M82 172 L70 172 M82 172 L76 178 M82 172 L88 178", 2.8)
    else:
        d.limb("leg", "M116 128 L124 154 L114 182", 6.5)
        d.stroke("leg", "M114 182 L100 183 M114 182 L108 187 M114 182 L122 186", 2.8)
    d.shape("hero", "M82 104 C76 88 68 68 64 48 L78 44 C80 64 88 82 98 94Z")
    d.shape("neck", "M66 50 L76 48 C78 60 80 68 84 78 C76 70 70 62 66 50Z", shadow=False, spot=True)
    d.shape("hero", ellipse(68, 42, 11, 8.5))
    d.shape("dark", "M60 40 C52 40 46 42 42 45 C48 48 55 48 62 46Z")
    d.marks("eye", circle(68, 40, 2.6))
    d.marks("mark", circle(68, 40, 1.3))


def emu_portrait(d: Drawing):
    d.disc("glow", 140, 66, 34)
    d.band("far", hills(150, 6))
    tufts(d, [(30, 154, 1), (174, 152, 0.9)], "near")
    d.band("ground", hills(170, 3))
    place(d, lambda: emu(d), 108, 182, 104, 182, 1.0)
    d.band("deep", hills(186, 3, 20), line=False)


def emu_outback(d: Drawing):
    d.disc("glow", 66, 112, 40)
    d.band("far", "M-30 130 L10 128 L14 118 L50 116 L56 128 L230 130")
    d.band("mid", hills(144, 4))
    tufts(d, [(150, 146, 0.9), (180, 148, 0.7), (24, 150, 0.8)], "near")
    d.band("ground", hills(160, 3))
    place(d, lambda: emu(d, run=True), 108, 172, 162, 154, 0.46)
    place(d, lambda: emu(d, run=True), 108, 172, 92, 172, 0.84)
    d.stroke("light", "M172 166 q4 -4 8 0 M178 172 q3 -3 6 0", 1.8, line=False)
    d.band("deep", hills(188, 3, 20), line=False)


# ================================================================ KOOKABURRA
def kookaburra(d: Drawing, laugh=True):
    d.shape("hero", "M128 140 L150 184 L136 190 L120 146Z")
    d.stroke("mark", "M130 158 L140 154 M134 166 L144 162 M138 174 L148 170 M142 182 L150 178", 2.2, line=False)
    d.shape("hero2", "M94 90 C86 110 90 136 104 150 C116 158 132 154 136 138 C142 118 138 98 128 86Z")
    d.shape("hero", "M118 86 C140 90 152 114 150 138 C148 150 140 158 132 158 C138 138 136 110 118 96Z", spot=True)
    d.shape("pop", "M122 96 C132 100 140 110 140 120 C134 112 128 106 120 104Z", shadow=False)
    d.stroke("mark", "M136 128 L142 128 M134 138 L140 138", 1.4, line=False)
    head = "M74 74 C74 58 88 46 104 48 C118 50 128 62 126 78 C124 92 112 100 100 100 C86 100 74 90 74 74Z"
    rot = "rotate(-20 100 74)" if laugh else "rotate(0 100 74)"
    d.raw(f'<g transform="{rot}">', f'<g transform="{rot}">')
    d.shape("hero2", head)
    d.shape("hero", "M76 68 C80 54 92 48 104 48 C116 50 124 58 126 70 C116 62 106 60 98 62 C88 62 82 64 76 68Z", shadow=False)
    d.shape("hero", "M80 78 C94 74 112 76 128 84 C112 88 94 88 80 84Z", shadow=False, line=False)
    if laugh:
        d.shape("beak2", "M80 82 C66 82 50 84 32 90 C46 92 64 92 82 90Z")
        d.shape("mark", "M80 72 C64 66 48 64 32 66 C40 72 60 76 82 80Z")
        d.shape("pop2", "M80 80 C68 78 54 78 40 80 C54 84 68 84 80 84Z", shadow=False, line=False)
    else:
        d.shape("beak2", "M80 80 C66 80 50 80 34 82 C46 88 64 90 82 88Z")
        d.shape("mark", "M80 70 C64 68 48 70 34 80 C48 80 64 80 82 82Z")
    d.marks("mark", circle(98, 76, 4))
    d.marks("light", circle(99.3, 74.7, 1.2))
    d.raw("</g>", "</g>")
    d.stroke("mark", "M110 150 L106 160 M118 152 L118 162", 2.6)


def kookaburra_laugh(d: Drawing):
    d.disc("glow", 104, 86, 56)
    d.limb("dark", "M-10 166 C40 158 120 160 210 150", 10)
    d.limb("dark", "M160 154 L182 124", 5)
    for x, y, a in [(182, 124, 70), (176, 132, 110), (186, 128, 40)]:
        d.shape("mid", gum(x, y, a, 26), shadow=False)
    for x, y, a in [(8, 40, 60), (16, 36, 90), (2, 52, 40), (24, 34, 110)]:
        d.shape("mid", gum(x, y, a, 30), shadow=False, line=False)
    place(d, lambda: kookaburra(d, True), 112, 162, 106, 160, 1.0)
    d.stroke("mark", "M30 66 L18 58 M28 80 L14 80 M34 52 L28 40", 2.4)


def kookaburra_fence(d: Drawing):
    d.disc("glow", 98, 112, 46)
    d.band("far", hills(138, 6))
    # gum trees on the hill
    for x, h, s in [(30, 50, 1.0), (184, 40, 0.8)]:
        d.limb("dark", f"M{x} 132 C{x - 2} {132 - h * 0.6} {x + 4} {132 - h * 0.8} {x + 2} {132 - h}", 4 * s)
        d.shape("near", scallop(x + 2, 132 - h - 4 * s, 16 * s, 9, 0.18), shadow=False)
    d.band("mid", hills(150, 4))
    d.stroke("dark", "M-10 150 H210 M-10 162 H210", 2)
    d.shape("dark", rrect(86, 128, 22, 80, 3))
    d.stroke("ground", "M92 140 V200 M101 136 V200", 1.2, line=False)
    d.band("ground", hills(176, 3))
    place(d, lambda: kookaburra(d, False), 112, 162, 94, 132, 0.72)


# ================================================================ colours
ROO_RED = {"hero": "#B65A30", "hero2": "#E6C29A", "mark": "#2E1C10"}
KOALA_C = {"hero": "#98A1AB", "hero2": "#C7CDD4", "light": "#F1F2F4", "mark": "#2B2D35"}
WOMBAT_C = {"hero": "#7E6A58", "hero2": "#A08A74", "mark": "#231C17", "light": "#FFFFFF"}
WOMBAT_HUT = {**WOMBAT_C, "pop": "#9A6440", "dark": "#4A3426"}
DEVIL_C = {"hero": "#1F1B1E", "hero2": "#2E292D", "mark": "#120F11", "pop": "#E8919A", "light": "#FBF7F2"}
PLATY_C = {"hero": "#6E4A30", "hero2": "#C9A27A", "mark": "#35302E", "light": "#FFFFFF"}
ECHIDNA_C = {"hero": "#5A4030", "hero2": "#F0DDB0", "mark": "#2A1D14"}

QUOKKA_C = {"hero": "#9C7B5C", "hero2": "#CDB496", "mark2": "#6E5440", "mark": "#2A1F18", "pop": "#E8919A", "light": "#FFFFFF"}
CASS_C = {"hero": "#2F7FC8", "hero2": "#3A3A44", "casque": "#9A7A55", "dark": "#18181C", "pop": "#D7263D",
          "mark": "#18181C", "eye": "#E0A040", "light": "#FFFFFF", "leg": "#5E5E66"}
EMU_C = {"hero": "#6E5D4C", "hero2": "#4A3D31", "neck": "#8FAAC8", "dark": "#2A2420", "eye": "#C0602E", "mark": "#1A1410",
         "leg": "#4F4A45"}
KOOKA_C = {"hero": "#6B4A2E", "hero2": "#F2E8D4", "mark": "#2A2018", "pop": "#5DA9D6", "beak2": "#D9C8A2", "pop2": "#B85A5A",
           "light": "#FFFFFF"}

UNDERWATER = ["coastal", "dusk", "meadow"]

CONCEPTS = [
    Concept("kangaroo-boxing", "animal-kangaroo", "Boxing roos", kangaroo_boxing, overrides=ROO_RED,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero", "far"), ("hero", "ground")],
            fixes={"glow": ["glow2", "light", "#F2C46B"], "far": ["mid", "near", "sky2"], "ground": ["near", "far"]}),
    Concept("kangaroo-beach", "animal-kangaroo", "Roos on the beach", kangaroo_beach, ["coastal", "meadow", "blush", "dusk"], ROO_RED,
            checks=[("hero", "ground"), ("hero", "near"), ("hero", "mid"), ("hero", "glow")],
            fixes={"ground": ["#EED9B0", "light"], "mid": ["far", "sky2"]}),
    Concept("koala-fork", "animal-koala", "Asleep in a gum tree", koala_fork, overrides=KOALA_C,
            checks=[("hero", "dark"), ("hero", "sky"), ("mid", "sky"), ("hero", "far")],
            fixes={"mid": ["near", "deep"], "far": ["mid", "near"], "sky": ["sky2"]}),
    Concept("koala-munch", "animal-koala", "Gum leaf lunch", koala_munch, overrides=KOALA_C,
            checks=[("hero", "sky"), ("hero", "near"), ("mid", "light"), ("hero", "dark")],
            fixes={"sky": ["sky2", "far"], "near": ["deep", "mid"]}),
    Concept("wombat-portrait", "animal-wombat", "Wombat", wombat_portrait, overrides=WOMBAT_C,
            checks=[("hero", "ground"), ("hero", "sky"), ("hero", "far")],
            fixes={"ground": ["far", "light"], "far": ["mid", "sky2"]}),
    Concept("wombat-hut", "animal-wombat", "Wombat at Dove Lake", wombat_hut, ["coastal", "meadow", "blush", "dusk"], WOMBAT_HUT,
            checks=[("hero", "near"), ("far", "sky"), ("pop", "mid"), ("pop", "sky2")],
            fixes={"near": ["mid", "far", "ground"], "far": ["mid", "near"]}),
    Concept("devil-portrait", "animal-tasmanian-devil", "Tasmanian devil", devil_face, overrides=DEVIL_C,
            checks=[("hero", "glow"), ("hero", "sky"), ("pop", "hero")],
            fixes={"glow": ["glow2", "far", "light"]}),
    Concept("devil-cradle", "animal-tasmanian-devil", "Devil at Cradle Mountain", devil_cradle, overrides=DEVIL_C,
            checks=[("hero", "near"), ("hero", "mid"), ("far", "sky")],
            fixes={"near": ["far", "ground", "mid"], "mid": ["far", "sky2"], "far": ["mid", "near"]}),
    Concept("platypus-portrait", "animal-platypus", "Platypus", platypus_portrait, UNDERWATER + ["blush"], PLATY_C,
            checks=[("hero", "far"), ("hero", "mid"), ("hero", "sky2"), ("mark", "far")],
            fixes={"far": ["sky2", "sky"]}),
    Concept("platypus-creek", "animal-platypus", "Platypus in the creek", platypus_creek, ["coastal", "meadow", "blush", "dusk"], PLATY_C,
            checks=[("hero", "sky2"), ("hero", "near"), ("hero", "mid")],
            fixes={"near": ["mid", "far"]}),
    Concept("echidna-portrait", "animal-echidna", "Echidna", echidna_portrait, overrides=ECHIDNA_C,
            checks=[("hero2", "glow"), ("hero", "glow"), ("hero", "ground"), ("glow", "sky")],
            fixes={"glow": ["mid", "near", "far", "deep"], "ground": ["far", "light"]}),
    Concept("echidna-bush", "animal-echidna", "Echidna & grass trees", echidna_bush, overrides=ECHIDNA_C,
            checks=[("hero2", "mid"), ("hero", "ground"), ("hero2", "far"), ("hero2", "near")],
            fixes={"mid": ["near", "deep"], "far": ["mid", "near", "deep"], "ground": ["light", "far"]}),
    Concept("quokka-selfie", "animal-quokka", "Quokka selfie", quokka_selfie, overrides=QUOKKA_C,
            checks=[("hero", "sky"), ("hero", "far"), ("dark", "sky"), ("hero", "ground")],
            fixes={"far": ["mid", "near"], "ground": ["light", "far"], "dark": ["light"]}),
    Concept("quokka-rottnest", "animal-quokka", "Quokka on Rottnest", quokka_rottnest, ["coastal", "meadow", "blush", "dusk"], QUOKKA_C,
            checks=[("hero", "ground"), ("hero", "mid"), ("hero", "near"), ("light", "far")],
            fixes={"ground": ["light", "#F5E6C4"], "far": ["mid", "near"], "near": ["deep", "mid", "far"]}),
    Concept("cassowary-portrait", "animal-cassowary", "Cassowary", cassowary_head, overrides=CASS_C,
            checks=[("hero", "sky"), ("hero", "near"), ("casque", "sky"), ("casque", "near")],
            fixes={"near": ["mid", "far", "deep"], "sky": ["sky2"]}),
    Concept("cassowary-rainforest", "animal-cassowary", "Rainforest cassowary", cassowary_forest, overrides=CASS_C,
            checks=[("dark", "sky"), ("dark", "far"), ("hero", "sky"), ("hero", "near"), ("leg", "ground"), ("casque", "near")],
            fixes={"far": ["sky2", "mid"], "near": ["mid", "far"], "ground": ["far", "light"]}),
    Concept("emu-portrait", "animal-emu", "Emu", emu_portrait, overrides=EMU_C,
            checks=[("hero", "sky"), ("hero", "glow"), ("hero", "far"), ("leg", "ground"), ("leg", "far")],
            fixes={"glow": ["glow2", "light"], "far": ["sky2", "ground"], "ground": ["light", "far"]}),
    Concept("emu-outback", "animal-emu", "Emus in the outback", emu_outback, overrides=EMU_C,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero", "mid"), ("leg", "ground"), ("hero", "far")],
            fixes={"glow": ["glow2", "light"], "mid": ["far", "ground"], "ground": ["light", "far"], "far": ["sky2", "ground"]}),
    Concept("kookaburra-laugh", "animal-kookaburra", "Laughing kookaburra", kookaburra_laugh, overrides=KOOKA_C,
            checks=[("hero2", "glow"), ("hero", "glow"), ("hero", "dark"), ("glow", "sky")],
            fixes={"glow": ["near", "mid", "deep"], "dark": ["#3B2A20", "mark"]}),
    Concept("kookaburra-fence", "animal-kookaburra", "Kookaburra on the fence", kookaburra_fence, overrides=KOOKA_C,
            checks=[("hero2", "glow"), ("hero", "glow"), ("glow", "sky"), ("dark", "ground"), ("dark", "mid")],
            fixes={"glow": ["near", "mid", "deep"], "mid": ["near", "far"]}),
]
