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
    d.disc("glow", 146, 50, 16)
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
    place(d, lambda: platypus(d), 100, 104, 104, 118, 0.9)
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
    birds(d, [(150, 50, 1), (166, 42, 0.8)])
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



# ================================================================ WALLABY
# Sitting, facing right, feet on y=171.
WALLABY = ("M14 170 C30 168 46 162 54 152 C46 136 48 116 60 104 C70 92 82 84 92 78 C94 70 100 64 108 64 "
           "C116 64 122 68 126 72 L134 78 C137 80 136 85 132 85 L120 86 C114 92 110 96 108 100 "
           "C112 112 112 126 106 138 C112 146 114 156 110 164 L128 166 C132 167 132 171 128 171 L66 171 "
           "C60 171 58 166 60 162 C48 168 30 172 14 172Z")


def wallaby(d: Drawing, rock=False):
    ears = "M98 70 C91 58 93 47 99 47 C104 51 104 62 104 68Z M106 66 C106 54 110 46 115 48 C117 54 115 62 112 68Z"
    d.shape("hero", ears)
    d.shape("hero2" if rock else "mark2", "M99 52 C98 58 100 64 102 66 L103 60Z M111 52 L111 64 L113 60Z", shadow=False, line=False)
    d.shape("hero", WALLABY)
    if rock:
        rings = "".join(f"M{x} {176 - (x - 14) * 0.47:.1f} l6 -12 " for x in (18, 28, 38, 48))
        clipped(d, WALLABY, lambda: d.stroke("hero2", rings, 4.5))
        d.shape("hero2", "M112 160 L128 166 C132 167 132 171 128 171 L106 171Z", shadow=False, spot=True)
    else:
        d.shape("hero2", "M80 86 C90 76 104 70 114 74 C112 86 106 96 100 100 C94 94 86 90 80 86Z", shadow=False, spot=True)
        d.shape("mark", "M118 166 L128 166 C132 167 132 171 128 171 L116 171Z", shadow=False)
    d.shape("mark", "M126 72 L134 78 C137 80 136 85 132 85 L124 85 C123 80 124 75 126 72Z", shadow=False, line=False)
    d.marks("mark", circle(114, 74, 2.2) + "M131 78 L135 80 L132 82Z")
    d.marks("light", circle(114.7, 73.3, 0.7))
    d.limb("hero2" if rock else "hero", "M104 102 L112 116 L118 118", 5)
    d.marks("mark", circle(119, 118, 2.4))


def wallaby_portrait(d: Drawing):
    d.disc("glow", 76, 92, 46)
    d.band("far", hills(150, 6))
    tufts(d, [(28, 152, 1), (178, 150, 0.9), (150, 154, 0.7)], "near")
    d.band("ground", hills(168, 3))
    place(d, lambda: wallaby(d), 76, 171, 96, 172, 0.96, flipx=True)
    d.band("deep", hills(186, 3, 20), line=False)


def wallaby_gorge(d: Drawing):
    d.disc("glow", 52, 54, 18)
    d.band("far", "M-30 96 L10 90 L30 74 L60 70 L80 82 L120 80 L150 64 L176 66 L196 80 L230 82")
    d.band("mid", "M-30 116 L20 108 L60 112 L110 100 L160 110 L230 104")
    d.limb("dark", "M168 140 C166 120 172 104 168 80 M168 104 L186 86", 5)
    d.shape("near", scallop(176, 74, 16, 9, 0.16), shadow=False)
    # stacked boulders
    d.shape("near", "M-20 200 L-14 150 C-6 132 20 128 40 132 C60 128 80 134 96 144 C112 140 130 146 138 162 L144 200Z")
    d.stroke("deep", "M30 150 Q44 146 56 152 M88 160 Q100 156 112 164", 1.8, line=False)
    d.band("ground", "M-30 172 Q100 162 230 172")
    place(d, lambda: wallaby(d, rock=True), 76, 171, 72, 142, 0.92)
    d.band("deep", hills(188, 3, 20), line=False)


# ================================================================ DINGO
DINGO_HEAD = ("M30 84 C32 79 40 77 48 75 L54 70 L56 50 L65 61 L69 59 L75 50 L77 68 C82 72 88 80 90 88 "
              "C88 98 80 102 72 102 L62 98 L44 94 C36 92 30 89 30 84Z")


def dingo_face(d: Drawing):
    d.disc("glow", 64, 70, 40)
    d.band("far", "M-30 172 L30 166 L40 152 L70 150 L78 164 L230 170")
    place(d, lambda: dingo_bust(d), 80, 110, 112, 128, 1.45)
    for x, y, k in [(30, 78, 1), (24, 92, 0.8), (36, 98, 0.7)]:
        d.stroke("mark", f"M{x} {y} q-6 -3 -8 -9", 2 * k + 0.4)
    d.band("ground", hills(190, 3), line=False)


def dingo_bust(d: Drawing):
    d.shape("hero", "M66 98 C62 124 56 160 54 210 L150 210 C140 160 118 118 90 84Z")
    d.shape("light", "M66 98 C62 124 56 160 54 210 L74 210 C74 160 76 124 80 104Z", shadow=False, spot=True)
    def head():
        d.shape("hero", DINGO_HEAD)
        d.shape("hero2", "M58 56 L59 66 L64 61Z", shadow=False, line=False)
        d.shape("pop", "M40 92 L62 96 L44 98Z", shadow=False, line=False)
        d.shape("light", "M36 92 C44 96 54 98 62 98 L72 102 C62 104 48 102 38 98Z", shadow=False, line=False)
        d.stroke("mark", "M38 91 L60 96", 1.4)
        d.marks("mark", circle(31, 83, 2.8))
        d.shape("eye", ellipse(58, 76, 3.4, 2.2), shadow=False, line=False)
        d.marks("mark", circle(58, 76, 1.3))
    group(d, "rotate(-28 80 96)", head)


DINGO = ("M30 84 C32 80 40 78 48 76 L54 70 L56 52 L64 62 L68 60 L74 52 L76 68 C80 72 84 78 88 86 "
         "C98 90 118 90 140 92 C150 94 156 102 154 112 L158 148 L149 148 L145 124 C138 126 128 126 118 124 "
         "L120 148 L111 148 L108 122 L96 120 L92 148 L83 148 L82 116 C76 108 72 100 70 96 C60 96 50 92 42 90 "
         "C35 89 30 88 30 84Z")


def dingo_side(d: Drawing):
    d.shape("hero", "M148 96 C164 92 176 80 176 64 C186 76 184 98 168 108 C162 110 156 110 152 108Z")
    d.shape("light", "M176 64 C186 76 184 90 178 98 C178 86 176 76 172 70Z", shadow=False, line=False)
    d.shape("hero", DINGO)
    d.shape("hero2", "M58 60 L60 70 L66 64Z", shadow=False, line=False)
    d.shape("light", "M36 88 C46 90 58 94 70 96 C74 102 78 108 82 116 L80 104 C72 96 62 90 50 88Z", shadow=False, line=False)
    d.stroke("light", "M83 145 H92 M111 145 H120 M149 145 H158", 3.4, line=False)
    d.marks("mark", circle(31, 83, 2.6) + circle(56, 76, 1.8))


def dingo_kgari(d: Drawing):
    d.disc("glow", 150, 54, 20)
    d.band("far", "M-30 104 L230 104", line=False)
    # SS Maheno wreck
    d.shape("rust", "M126 108 L132 86 L176 86 L184 108Z")
    d.shape("rust", "M142 86 L144 74 L156 74 L158 86Z", shadow=False)
    d.marks("dark", circle(140, 95, 1.8) + circle(150, 95, 1.8) + circle(160, 95, 1.8) + circle(170, 95, 1.8))
    d.band("mid", waves(106, 2, 30))
    d.band("light", waves(118, 3, 24), line=False)
    d.band("near", "M-30 120 Q60 116 120 120 T230 118", line=False)
    d.band("ground", "M-30 128 Q60 122 120 128 T230 124")
    d.shape("far", "M-20 132 C10 110 40 108 60 130Z", line=False)
    place(d, lambda: dingo_side(d), 100, 148, 96, 166, 0.88)
    d.stroke("deep", "M150 176 l5 -2 M164 180 l5 -2 M40 180 l5 -2", 1.6, line=False)
    d.band("deep", hills(188, 2, 20), line=False)


# ================================================================ SALTWATER CROCODILE
SALTIE_HEAD = ("M14 116 C14 106 24 100 34 102 C56 104 82 100 104 94 C114 80 130 72 146 74 C156 76 162 84 162 92 "
               "C176 92 190 94 210 100 L210 150 L14 150 C10 136 10 124 14 116Z")


def saltie_head(d: Drawing):
    d.shape("hero", SALTIE_HEAD)
    d.shape("hero", ellipse(28, 104, 9, 6), shadow=False)
    d.marks("mark", ellipse(26, 101, 2.2, 1.3) + ellipse(33, 101, 2.2, 1.3))
    teeth_up = "".join(f"M{x} 120 l3 9 l3 -9Z " for x in range(24, 140, 12))
    teeth_dn = "".join(f"M{x} 123 l3 -8 l3 8Z " for x in range(30, 130, 12))
    d.shape("light", teeth_up + teeth_dn, shadow=False)
    d.stroke("mark", "M16 122 C40 121 70 121 100 117 C118 114 136 116 152 122 C162 126 172 126 182 124", 2.4)
    d.shape("hero", "M126 80 C130 70 146 68 152 76 C150 80 140 82 126 80Z", shadow=False)
    d.shape("eye", ellipse(141, 82, 8, 5.5), shadow=False, spot=True)
    d.marks("mark", ellipse(141, 82, 1.5, 4.6))
    d.marks("hero2", circle(60, 108, 2) + circle(74, 106, 2) + circle(88, 104, 2) + circle(66, 113, 1.6) + circle(82, 112, 1.6)
            + circle(100, 108, 2) + circle(116, 98, 1.8) + circle(124, 108, 2))
    d.shape("hero", "M166 92 l5 -9 l5 9Z M180 95 l5 -10 l5 10Z M194 98 l5 -10 l5 10Z M172 104 l4 -7 l4 7Z M188 106 l4 -8 l4 8Z", shadow=False)


def saltie_portrait(d: Drawing):
    d.disc("glow", 60, 54, 22)
    d.band("far", hills(84, 6))
    for x, h in [(150, 40), (176, 50), (24, 30)]:
        d.limb("light", f"M{x} 90 L{x + 2} {90 - h}", 4, shadow=False)
        d.shape("near", scallop(x + 2, 86 - h, 12, 8, 0.2), shadow=False, line=False)
    d.band("mid", "M-30 92 L230 92", line=False)
    place(d, lambda: saltie_head(d), 100, 120, 100, 112, 1.0)
    d.band("near", waves(136, 3, 34))
    d.stroke("light", "M30 146 q10 -5 20 0 M120 150 q10 -5 20 0", 2, line=False)
    for x, y in [(40, 166), (150, 170)]:
        d.shape("hero2", f"M{x - 13} {y} a13 6 0 1 0 1 -6 L{x} {y - 3}Z", line=False)
    d.shape("pop", "M96 168 l-6 -8 l6 3 l0 -8 l4 8 l4 -8 l0 8 l6 -3 l-6 8Z", shadow=False, spot=True)
    d.band("deep", waves(182, 3, 38), line=False)


def saltie_croc(d: Drawing):
    """Horizontal croc, jaws wide open, facing right (rotated upright for the jump)."""
    d.shape("pop2", "M148 92 L198 72 L198 108Z", shadow=False)
    d.limb("hero", "M118 110 L126 126 L132 128", 7)
    d.shape("hero", "M-40 104 C0 92 60 86 110 88 L130 84 C140 76 152 76 158 82 L196 66 C201 64 204 70 199 73 "
                    "L150 94 L198 110 C203 112 201 118 196 116 L146 108 C130 112 110 114 90 114 C40 116 0 112 -40 104Z")
    d.shape("light", "M160 90 l4 -6 l3 5 l4 -7 l3 5 l4 -7 l3 5 l4 -6 l2 4Z M160 104 l3 6 l4 -5 l3 7 l4 -6 l3 7 l4 -6 l3 6 l2 -3Z", shadow=False)
    d.shape("hero2", "M-40 104 C0 108 50 112 100 111 L146 108 C130 112 110 114 90 114 C40 116 0 112 -40 104Z", shadow=False, line=False)
    d.marks("mark", "M20 96 l4 -6 l4 6Z M36 93 l4 -7 l4 7Z M52 91 l4 -7 l4 7Z M68 89 l4 -7 l4 7Z M84 88 l4 -7 l4 7Z M100 88 l4 -6 l4 6Z")
    d.shape("eye", ellipse(146, 82, 5, 3.5), shadow=False, spot=True)
    d.marks("mark", ellipse(146, 82, 1, 3))
    d.limb("hero", "M60 110 L54 126 L46 128", 7)


def saltie_jump(d: Drawing):
    d.disc("glow", 50, 60, 20)
    d.band("far", hills(130, 4))
    for x in (8, 24, 172, 186):
        d.shape("near", scallop(x, 126, 12, 8, 0.2), shadow=False, line=False)
    d.band("mid", "M-30 136 L230 136")
    # the bait on a pole held out from the boat
    d.stroke("dark", "M214 14 L132 34", 3)
    d.stroke("dark", "M140 32 L140 44", 1.4)
    d.shape("pop", "M134 44 C134 40 146 40 146 44 L144 56 C142 60 138 60 136 56Z", spot=True)
    place(d, lambda: saltie_croc(d), 60, 100, 102, 150, 0.82, rot=-66)
    d.shape("light", "M50 152 C60 138 70 146 76 136 C80 146 92 140 96 150 C104 140 112 146 118 136 C124 146 136 140 146 152Z", line=False)
    d.band("near", waves(152, 3, 30))
    d.stroke("light", "M30 164 q10 -5 20 0 M140 168 q10 -5 20 0 M80 176 q10 -5 20 0", 2, line=False)
    d.band("deep", waves(184, 3, 36), line=False)


# ================================================================ FRILLED LIZARD
def frill_disc(d: Drawing, cx, cy, rx, ry, rot=0):
    def draw():
        n = 18
        d.shape("rim", scallop(cx, cy, rx, n, 0.05), extra=f'transform="translate({cx} {cy}) scale(1 {ry / rx}) translate({-cx} {-cy})"')
        d.shape("frill", circle(cx, cy, rx * 0.84), shadow=False, spot=True, extra=f'transform="translate({cx} {cy}) scale(1 {ry / rx}) translate({-cx} {-cy})"')
        d.shape("frill2", circle(cx, cy, rx * 0.5), shadow=False, line=False, extra=f'transform="translate({cx} {cy}) scale(1 {ry / rx}) translate({-cx} {-cy})"')
        ribs = ""
        for i in range(n):
            a = 2 * math.pi * (i + 0.5) / n
            ribs += f"M{cx + rx * 0.3 * math.cos(a):.1f} {cy + ry * 0.3 * math.sin(a):.1f} L{cx + rx * 0.95 * math.cos(a):.1f} {cy + ry * 0.95 * math.sin(a):.1f} "
        d.stroke("rim", ribs, 1.6)
    group(d, f"rotate({rot} {cx} {cy})", draw)


def frilled_portrait(d: Drawing):
    d.band("far", hills(170, 4), line=False)
    frill_disc(d, 100, 90, 72, 66)
    d.shape("hero", "M66 210 C68 166 82 132 100 128 C118 132 132 166 134 210Z")
    d.limb("hero", "M78 158 L62 180 L54 182", 8)
    d.limb("hero", "M122 158 L138 180 L146 182", 8)
    d.stroke("mark", "M54 182 l-6 -2 M54 182 l-6 3 M146 182 l6 -2 M146 182 l6 3", 1.6)
    d.shape("hero", "M100 52 C118 52 128 66 128 86 C128 108 118 124 100 128 C82 124 72 108 72 86 C72 66 82 52 100 52Z")
    d.shape("mouth", "M80 92 C86 88 114 88 120 92 C120 112 112 124 100 126 C88 124 80 112 80 92Z")
    d.shape("pop", "M90 112 C94 108 106 108 110 112 C108 120 104 122 100 122 C96 122 92 120 90 112Z", shadow=False, line=False)
    for ex in (78, 122):
        d.marks("eye", circle(ex, 72, 5))
        d.marks("mark", circle(ex, 72, 2.4))
    d.marks("mark", circle(94, 62, 1.4) + circle(106, 62, 1.4))
    d.marks("hero2", circle(90, 140, 2) + circle(110, 146, 2) + circle(100, 160, 2) + circle(88, 172, 2) + circle(112, 180, 2))


def frilled_run(d: Drawing):
    d.disc("glow", 150, 60, 22)
    d.band("far", hills(118, 4))
    # cathedral termite mounds
    for x, h in [(30, 46), (58, 30), (176, 36)]:
        d.shape("mid", f"M{x - 12} 124 C{x - 10} {124 - h * 0.6} {x - 6} {124 - h} {x} {124 - h} C{x + 4} {124 - h * 0.8} {x + 4} {124 - h * 0.5} {x + 8} {124 - h * 0.4} "
                       f"C{x + 10} {124 - h * 0.2} {x + 12} 120 {x + 14} 124Z")
    d.band("ground", hills(138, 3))
    def lizard():
        d.shape("hero", "M114 134 C140 140 170 146 204 150 C170 154 140 152 112 146Z")
        d.limb("hero", "M120 140 L136 152 L150 166", 6)
        d.stroke("mark", "M150 166 l8 0 M150 166 l6 4", 1.6)
        d.shape("hero", "M86 96 C96 90 108 96 114 108 C120 120 124 132 122 142 C116 148 108 146 102 138 C94 126 86 112 86 96Z")
        d.marks("hero2", circle(98, 108, 1.6) + circle(106, 122, 1.6) + circle(112, 112, 1.6) + circle(112, 134, 1.6))
        d.limb("hero", "M114 136 L98 150 L106 168", 6.5)
        d.stroke("mark", "M106 168 l9 0 M106 168 l2 6", 1.6)
        frill_disc(d, 82, 88, 25, 29, -20)
        d.shape("hero", "M88 84 C80 76 66 70 52 72 C46 74 46 80 52 82 C62 84 74 88 86 92Z")
        d.shape("mouth", "M86 92 C76 90 62 90 52 94 C58 98 72 98 88 98Z")
        d.marks("eye", circle(70, 76, 2.6))
        d.marks("mark", circle(70, 76, 1.3))
        d.limb("hero", "M96 104 L90 116 L84 120", 4.5)
    place(d, lizard, 110, 168, 104, 170, 1.12)
    d.stroke("light", "M168 150 q4 -4 8 0 M178 156 q3 -3 6 0", 1.8, line=False)
    d.band("deep", hills(182, 3, 20), line=False)


# ================================================================ COCKATOO
def cockatoo(d: Drawing):
    for a, ln in [(-130, 44), (-110, 52), (-92, 54), (-74, 50), (-56, 42)]:
        d.shape("crest", leaf(112, 66, ln, 6, a + 25), spot=True)
    d.shape("white", "M96 96 C84 110 84 140 96 164 C108 182 134 186 146 170 C158 152 152 116 136 98Z")
    d.shape("shade", "M126 104 C144 116 150 140 144 162 C140 172 132 178 124 178 C134 160 136 130 122 110Z", shadow=False)
    d.stroke("shade2", "M130 128 Q136 140 134 156 M138 122 Q146 138 142 160", 1.4, line=False)
    d.shape("white", "M132 170 L150 196 L136 200 L120 176Z")
    d.shape("white", circle(104, 82, 27))
    d.shape("crestsoft", ellipse(114, 92, 9, 6), shadow=False, line=False)
    d.shape("beak", "M82 74 C70 72 62 82 62 96 C62 102 66 106 70 104 C70 96 74 88 84 88Z")
    d.shape("beak", "M70 104 C76 106 82 102 86 94 L84 88 C78 90 72 96 70 104Z", shadow=False)
    d.marks("ring", ellipse(97, 76, 6.5, 6))
    d.marks("mark", circle(97, 76, 3.2))
    d.marks("light", circle(98, 75, 1))
    d.stroke("beak", "M106 178 L102 188 M116 180 L116 190", 3)


def cockatoo_portrait(d: Drawing):
    d.disc("mid", 104, 100, 66, line=False)
    d.limb("dark", "M-10 192 C40 184 140 184 210 176", 10)
    place(d, lambda: cockatoo(d), 110, 188, 104, 190, 0.98)


SISTERS = ("M-30 112 L30 110 L38 104 L44 76 C46 70 52 70 54 76 L56 96 L62 96 L64 70 C66 62 74 62 76 70 L78 96 "
           "L84 96 L86 62 C88 52 98 52 100 62 L104 98 L130 100 L230 106")


def cockatoo_sisters(d: Drawing):
    d.disc("glow", 160, 46, 16)
    birds(d, [(130, 40, 1), (146, 32, 0.8)], "light")
    d.band("far", SISTERS)
    d.shape("deep", "M54 76 L56 96 M76 70 L78 96 M100 62 L104 98", line=False)
    d.band("mid", "M-30 122 Q40 116 100 122 T230 118")
    d.band("near", "M-30 140 Q40 132 100 138 T230 132")
    d.limb("dark", "M210 150 C170 152 140 158 110 172 C90 180 60 182 30 200", 8)
    for x, y, a in [(186, 146, 110), (196, 146, 70), (176, 150, 95)]:
        d.shape("deep", gum(x, y, a, 26), shadow=False)
    place(d, lambda: cockatoo(d), 110, 188, 132, 166, 0.6)


# ================================================================ RAINBOW LORIKEET
def lorikeet(d: Drawing):
    d.shape("green", "M132 160 L156 196 L142 198 L124 166Z")
    d.shape("green", "M92 100 C82 118 84 146 98 164 C110 176 132 174 140 156 C148 134 142 108 128 96Z")
    d.shape("belly", "M90 142 C94 158 106 168 118 170 C126 160 126 146 122 138 C112 146 100 148 90 142Z", shadow=False, line=False)
    d.shape("chest", "M90 108 C84 120 84 134 90 144 C102 150 116 146 122 134 C122 120 114 106 100 102Z", shadow=False, spot=True)
    d.stroke("chest2", "M90 118 Q102 122 116 116 M88 128 Q102 132 120 126 M92 138 Q104 142 118 136", 2.2, line=False)
    d.shape("green", "M118 98 C142 104 152 128 148 152 C146 164 138 172 128 172 C136 150 134 120 118 106Z")
    d.stroke("green2", "M132 120 Q140 136 138 156 M124 112 Q134 128 132 150", 1.4, line=False)
    d.shape("collar", "M86 100 C98 96 118 98 128 106 L126 113 C114 106 100 104 90 108Z", shadow=False)
    d.shape("blue", circle(102, 80, 24))
    d.shape("beak", "M82 74 C72 74 64 82 66 94 C68 98 72 98 74 94 C74 88 78 84 86 86Z")
    d.shape("beak", "M74 96 C78 98 84 96 86 90 L84 86 C78 88 76 92 74 96Z", shadow=False)
    d.marks("eye", circle(96, 76, 4.6))
    d.marks("mark", circle(96, 76, 2.4))
    d.marks("light", circle(97, 75, 0.8))
    d.stroke("mark", "M104 168 L100 178 M114 170 L114 180", 2.6)


def lorikeet_portrait(d: Drawing):
    for x, y, a in [(-6, 40, 30), (0, 86, 10), (206, 44, 150), (204, 96, 170)]:
        d.shape("near", gum(x, y, a, 54), line=False)
    d.limb("dark", "M-10 180 C40 172 140 172 210 166", 10)
    place(d, lambda: lorikeet(d), 110, 176, 104, 176, 1.02)


def bottlebrush(d: Drawing, x, y, ang, s=1.0):
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    p = ""
    for i in range(14):
        t = 4 + i * 2.3
        bx, by = x + ux * t * s, y + uy * t * s
        for k in (-1, 1):
            p += f"M{bx:.1f} {by:.1f} L{bx + px * k * 11 * s + ux * 2 * s:.1f} {by + py * k * 11 * s + uy * 2 * s:.1f} "
    d.stroke("dark", f"M{x - ux * 6} {y - uy * 6} L{x + ux * 38 * s:.1f} {y + uy * 38 * s:.1f}", 2.2)
    d.stroke("brush", p, 1.8, shadow=True)
    d.marks("brush2", "".join(circle(x + ux * (4 + i * 3.6) * s + px * k * 11 * s + ux * 2 * s, y + uy * (4 + i * 3.6) * s + py * k * 11 * s + uy * 2 * s, 1.4 * s)
                              for i in range(0, 9, 2) for k in (-1, 1)))


def lorikeet_bottlebrush(d: Drawing):
    d.disc("glow", 150, 48, 18)
    d.band("far", hills(170, 4), line=False)
    d.limb("dark", "M-10 150 C40 140 120 138 210 120", 7)
    for x, y, a in [(160, 128, 80), (176, 124, 120), (20, 146, 70), (100, 136, 100)]:
        d.shape("near", gum(x, y, a, 30), shadow=False, line=False)
    for x, y, a in [(150, 126, -80), (40, 144, -100), (186, 120, -60)]:
        bottlebrush(d, x, y, a, 0.9)
    place(d, lambda: lorikeet(d), 110, 176, 78, 148, 0.56)
    place(d, lambda: lorikeet(d), 110, 176, 128, 136, 0.48, flipx=True)


# ================================================================ LITTLE PENGUIN
def little_penguin(d: Drawing):
    d.shape("feet", "M84 172 C80 176 76 180 82 182 L98 182 L96 172Z M104 172 L104 182 L120 182 C124 180 120 176 116 172Z")
    d.shape("hero", "M96 38 C110 36 120 46 122 60 C130 78 138 104 138 128 C138 156 126 174 104 176 C82 176 66 160 66 132 "
                    "C66 108 72 88 76 72 C76 52 84 40 96 38Z")
    d.shape("white", "M80 66 C88 72 92 82 90 96 C86 120 88 150 104 172 C82 174 70 158 70 134 C70 110 74 88 80 66Z", shadow=False)
    d.shape("hero", "M118 92 C130 104 136 128 132 150 C128 154 124 152 122 148 C124 128 120 110 112 98Z", shadow=False)
    d.stroke("white", "M122 148 C126 130 124 112 116 100", 1.4, line=False)
    d.shape("dark", "M80 58 C70 58 60 60 54 64 C60 68 70 70 82 68Z")
    d.marks("eye", circle(92, 56, 3.6))
    d.marks("mark", circle(92, 56, 1.8))


def penguin_rock(d: Drawing):
    d.disc("glow", 150, 66, 24)
    d.band("far", "M-30 120 L230 120")
    d.stroke("light", "M20 128 H50 M140 130 H176 M70 136 H100", 2, line=False)
    d.band("mid", waves(142, 2, 30), line=False)
    d.shape("near", "M10 210 L18 176 C26 160 52 156 80 160 C110 156 150 158 168 172 L180 210Z")
    d.stroke("deep", "M40 176 Q60 172 74 178 M118 174 Q136 172 150 178", 1.8, line=False)
    place(d, lambda: little_penguin(d), 100, 182, 100, 170, 0.98)


def penguin_parade(d: Drawing):
    d.disc("glow", 136, 92, 28)
    d.band("far", "M-30 104 L230 104")
    d.band("mid", waves(114, 2, 30), line=False)
    d.band("light", waves(124, 3, 22), line=False)
    d.band("ground", "M-30 128 Q60 122 120 128 T230 124")
    d.shape("near", "M-20 200 C0 160 30 150 60 152 C40 162 30 180 30 200Z", line=False)
    for x, y, s in [(150, 140, 0.34), (124, 146, 0.4), (94, 154, 0.48), (58, 166, 0.58)]:
        place(d, lambda: little_penguin(d), 100, 182, x, y + 20 * s, s, rot=-6)
    d.stroke("deep", "M110 184 l4 -2 M150 176 l4 -2 M170 186 l4 -2", 1.6, line=False)


# ================================================================ SUGAR GLIDER
def glider_face(d: Drawing, s_eyes=11):
    for ex, r in ((62, -32), (138, 32)):
        d.shape("hero", ellipse(ex, 66, 15, 22), extra=f'transform="rotate({r} {ex} 66)"')
        d.shape("ear", ellipse(ex, 68, 9, 15), extra=f'transform="rotate({r} {ex} 68)"', shadow=False, spot=True)
    d.shape("hero", "M100 60 C126 60 144 78 144 100 C144 124 124 138 100 138 C76 138 56 124 56 100 C56 78 74 60 100 60Z")
    d.shape("hero2", "M64 112 C72 128 86 136 100 136 C114 136 128 128 136 112 C124 120 112 122 100 122 C88 122 76 120 64 112Z", shadow=False, line=False)
    d.marks("mark", "M96 60 L104 60 L104 98 L100 110 L96 98Z")
    d.marks("mark", "M66 78 C74 82 84 88 88 96 L84 102 C76 96 70 88 66 78Z M134 78 C126 82 116 88 112 96 L116 102 C124 96 130 88 134 78Z")
    for ex in (78, 122):
        d.marks("mark", circle(ex, 98, s_eyes))
        d.marks("light", circle(ex + 3, 94, s_eyes * 0.3) + circle(ex - 3, 102, s_eyes * 0.12))
    d.marks("ear", ellipse(100, 114, 4, 3))
    d.stroke("mark", "M96 122 Q100 125 104 122", 1.4)


def glider_portrait(d: Drawing):
    d.shape("dark", "M36 -10 C46 60 40 140 26 210 L174 210 C162 140 156 60 164 -10Z")
    d.stroke("bark", "M48 10 C52 40 50 60 46 80 M154 20 C150 50 152 70 156 96 M44 150 C46 170 42 186 40 200 M158 150 C156 170 160 186 162 200", 2, line=False)
    d.shape("deep", ellipse(100, 150, 46, 32))
    glider_face(d)
    d.shape("hero", "M60 150 C64 132 80 126 100 126 C120 126 136 132 140 150 Z", shadow=False)
    d.limb("hero", "M72 150 L70 158", 9)
    d.limb("hero", "M128 150 L130 158", 9)
    d.marks("ear", circle(66, 160, 2) + circle(71, 161, 2) + circle(76, 160, 2) + circle(124, 160, 2) + circle(129, 161, 2) + circle(134, 160, 2))
    d.shape("dark", "M50 156 C70 148 130 148 150 156 L160 200 L40 200Z", line=False)


def glider_fly(d: Drawing):
    d.limb("hero", "M100 128 C102 150 96 170 100 196", 11)
    d.limb("mark", "M100 184 L100 198", 11, shadow=False)
    d.shape("hero", "M58 70 C80 78 120 78 142 70 L152 74 C146 96 146 116 152 132 L142 136 C120 128 80 128 58 136 "
                    "L48 132 C54 116 54 96 48 74Z")
    d.shape("hero2", "M62 128 C80 122 120 122 138 128 L142 136 C120 128 80 128 58 136Z", shadow=False, line=False)
    d.marks("mark", "M97 72 L103 72 L103 130 L97 130Z")
    for x, y in [(50, 72), (150, 72), (48, 134), (152, 134)]:
        d.marks("ear", circle(x, y, 3.2))
    for ex, r in ((88, -30), (112, 30)):
        d.shape("hero", ellipse(ex, 52, 6, 9), extra=f'transform="rotate({r} {ex} 52)"', shadow=False)
    d.shape("hero", circle(100, 62, 14))
    d.marks("mark", "M98 48 L102 48 L102 62 L100 66 L98 62Z")
    d.marks("mark", circle(93, 62, 3.6) + circle(107, 62, 3.6))
    d.marks("light", circle(94, 61, 1) + circle(108, 61, 1))


def glider_night(d: Drawing):
    d.disc("glow", 140, 52, 26)
    d.marks("light", circle(40, 40, 1.4) + circle(70, 24, 1.2) + circle(170, 100, 1.4) + circle(30, 84, 1.2))
    d.limb("dark", "M24 210 C20 150 28 100 20 -10", 18)
    d.limb("dark", "M176 210 C180 160 172 120 180 -10", 18)
    d.limb("dark", "M178 140 L204 120", 5)
    d.limb("dark", "M24 70 L-4 52", 5)
    for x, y, a in [(-2, 54, 80), (6, 60, 110), (196, 122, 70), (186, 128, 110)]:
        d.shape("near", gum(x, y, a, 26), shadow=False, line=False)
    place(d, lambda: glider_fly(d), 100, 110, 98, 110, 0.82, rot=-56)
    d.band("far", hills(186, 3), line=False)


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
WALLABY_C = {"hero": "#8E8780", "hero2": "#B0653E", "mark": "#2A2420", "mark2": "#6A625C", "light": "#FFFFFF"}
ROCKWALLABY_C = {"hero": "#9A958F", "hero2": "#E2A23B", "mark": "#2A2420", "mark2": "#6A625C", "light": "#FFFFFF"}
DINGO_C = {"hero": "#D38B47", "hero2": "#E9B98A", "light": "#FBF1E2", "mark": "#231A14", "eye": "#E2A63B", "pop": "#E88A8A"}
DINGO_BEACH = {**DINGO_C, "rust": "#8E4A30", "dark": "#2E2420"}
SALTIE = {"hero": "#5E6B43", "hero2": "#8E9660", "mark": "#20241A", "light": "#FFFDF2", "eye": "#E3C547", "pop": "#F2A7C0"}
SALTIE_JUMP = {**SALTIE, "hero2": "#D7CF94", "pop2": "#E8838F", "pop": "#B23A3A"}
FRILL_C = {"hero": "#8C7A60", "hero2": "#5E503E", "mark": "#231C14", "frill": "#E8873A", "frill2": "#F6C445",
           "rim": "#9E3B22", "mouth": "#F6DD7C", "eye": "#E3B23C", "pop": "#E88A8A"}
COCKY_C = {"white": "#FCFCF8", "shade": "#E3E4DE", "shade2": "#C9CBC2", "crest": "#F5CF2E", "crestsoft": "#F8E7A0",
           "beak": "#34343A", "ring": "#DCE9F4", "mark": "#1A1A1E", "light": "#FFFFFF"}
LORI_C = {"blue": "#3D4FC6", "green": "#2E9E4A", "green2": "#1E7A38", "chest": "#F2862E", "chest2": "#F7D13A",
          "belly": "#2B3F9E", "collar": "#A9D63B", "beak": "#E3402C", "eye": "#E3402C", "mark": "#1A1A1E",
          "light": "#FFFFFF", "brush": "#D7263D", "brush2": "#F6D13A"}
LPENG_C = {"hero": "#5A86B0", "white": "#FFFFFF", "dark": "#2A2E36", "eye": "#C9D6E2", "mark": "#1A1E26", "feet": "#F2B9B0"}
GLIDER_C = {"bark": "#3A2A1E", "hero": "#9AA0A8", "hero2": "#E6E7EA", "mark": "#1F1E22", "ear": "#E9A9B4", "light": "#FFFFFF"}

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
    Concept("wallaby-portrait", "animal-wallaby", "Red-necked wallaby", wallaby_portrait, overrides=WALLABY_C,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero", "ground"), ("hero", "far")],
            fixes={"glow": ["glow2", "light", "near"], "ground": ["light", "far"], "far": ["mid", "sky2"]}),
    Concept("wallaby-gorge", "animal-wallaby", "Rock-wallaby in the gorge", wallaby_gorge, overrides=ROCKWALLABY_C,
            checks=[("hero", "near"), ("hero", "far"), ("hero", "mid"), ("hero2", "near")],
            fixes={"near": ["deep", "ground"], "mid": ["far", "sky2"], "far": ["sky2", "mid"]}),
    Concept("dingo-portrait", "animal-dingo", "Dingo", dingo_face, overrides=DINGO_C,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero", "far")],
            fixes={"glow": ["light", "glow2", "far"], "far": ["near", "deep", "sky2"]}),
    Concept("dingo-kgari", "animal-dingo", "Dingo on K'gari", dingo_kgari, ["coastal", "meadow", "blush", "dusk"], DINGO_BEACH,
            checks=[("hero", "ground"), ("hero", "near"), ("hero", "mid"), ("rust", "mid"), ("rust", "sky")],
            fixes={"ground": ["light", "#F3E3C0"], "mid": ["far", "near"]}),
    Concept("saltie-head", "animal-saltwater-crocodile", "Saltie at the billabong", saltie_portrait, ["coastal", "meadow", "blush", "dusk"], SALTIE,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "far"), ("hero", "sky")],
            fixes={"mid": ["sky2", "far", "glow2"], "near": ["deep", "far"], "far": ["sky2", "mid"]}),
    Concept("saltie-jump", "animal-saltwater-crocodile", "Jumping croc", saltie_jump, ["golden", "coastal", "meadow", "blush", "dusk"], SALTIE_JUMP,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "near"), ("hero", "mid")],
            fixes={"far": ["sky2", "mid"], "near": ["deep", "mid"], "mid": ["far", "deep"]}),
    Concept("frilled-portrait", "animal-frilled-lizard", "Frilled lizard", frilled_portrait, overrides=FRILL_C,
            checks=[("rim", "sky"), ("frill", "sky"), ("hero", "frill2"), ("hero", "far")],
            fixes={"sky": ["sky2", "far", "light"], "far": ["near", "deep"]}),
    Concept("frilled-run", "animal-frilled-lizard", "Frilled lizard on the run", frilled_run, overrides=FRILL_C,
            checks=[("hero", "ground"), ("hero", "sky"), ("hero", "far"), ("frill", "far"), ("frill", "sky"), ("hero", "glow")],
            fixes={"ground": ["light", "far"], "far": ["sky2", "mid"], "glow": ["glow2", "light"]}),
    Concept("cockatoo-portrait", "animal-cockatoo", "Sulphur-crested cockatoo", cockatoo_portrait, overrides=COCKY_C,
            checks=[("white", "mid"), ("crest", "mid"), ("crest", "sky"), ("white", "dark")],
            fixes={"mid": ["near", "deep", "far"]}),
    Concept("cockatoo-sisters", "animal-cockatoo", "Cockatoo & the Three Sisters", cockatoo_sisters, overrides=COCKY_C,
            checks=[("white", "near"), ("white", "mid"), ("crest", "mid"), ("crest", "near"), ("far", "sky")],
            fixes={"near": ["deep", "mid"], "mid": ["near", "deep"], "far": ["mid", "near"]}),
    Concept("lorikeet-portrait", "animal-rainbow-lorikeet", "Rainbow lorikeet", lorikeet_portrait, overrides=LORI_C,
            checks=[("blue", "sky"), ("green", "sky"), ("green", "near"), ("chest", "sky")],
            fixes={"near": ["deep", "far", "mid"], "sky": ["sky2"]}),
    Concept("lorikeet-bottlebrush", "animal-rainbow-lorikeet", "Lorikeets in the bottlebrush", lorikeet_bottlebrush, overrides=LORI_C,
            checks=[("blue", "sky"), ("green", "sky"), ("brush", "sky"), ("green", "near")],
            fixes={"near": ["far", "deep"], "sky": ["sky2"]}),
    Concept("littlepenguin-portrait", "animal-little-penguin", "Little penguin", penguin_rock, ["coastal", "meadow", "blush", "dusk"], LPENG_C,
            checks=[("hero", "far"), ("hero", "near"), ("white", "far"), ("hero", "sky"), ("hero", "glow")],
            fixes={"far": ["mid", "deep"], "near": ["deep", "ground", "far"], "glow": ["glow2", "light"]}),
    Concept("littlepenguin-parade", "animal-little-penguin", "Penguin parade", penguin_parade, ["coastal", "meadow", "blush", "dusk"], LPENG_C,
            checks=[("hero", "ground"), ("white", "ground"), ("hero", "near"), ("hero", "light")],
            fixes={"ground": ["#E8D3A8", "far", "mid"], "near": ["deep", "mid"]}),
    Concept("glider-portrait", "animal-sugar-glider", "Sugar glider", glider_portrait, overrides=GLIDER_C,
            checks=[("hero", "dark"), ("hero", "deep"), ("ear", "dark"), ("dark", "sky")],
            fixes={"dark": ["#6B4A32", "near", "mid"], "deep": ["#2A1D14", "dark"]}),
    Concept("glider-night", "animal-sugar-glider", "Gliding by moonlight", glider_night, ["dusk", "coastal", "meadow", "blush", "golden"], GLIDER_C,
            checks=[("hero", "sky"), ("hero", "dark"), ("hero", "glow")],
            fixes={"sky": ["sky2", "deep", "near"], "glow": ["glow2", "light", "far"]}),
]
