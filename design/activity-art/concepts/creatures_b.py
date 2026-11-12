"""Small creatures: chameleon, gecko, iguana, thorny devil, tree frog, axolotl and five insects.

Each animal gets a bold portrait and a scene in its habitat.
"""
import math

from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group, bubbles  # noqa: F401

NO_GOLD = ["coastal", "meadow", "blush", "dusk"]
UNDERWATER = ["coastal", "dusk", "meadow"]
_uid = [0]


# ================================================================ helpers (copied from animals_south / animals_australia)
def _id(prefix):
    _uid[0] += 1
    return f"{prefix}{_uid[0]}"


def clipped(d: Drawing, path: str, fn):
    """Draw fn() clipped to `path`."""
    cid = _id("crbclip")
    tag = f'<clipPath id="{cid}"><path d="{path}"/></clipPath><g clip-path="url(#{cid})">'
    d.raw(tag, tag)
    fn()
    d.raw("</g>", "</g>")


def flip(d: Drawing, fn, cx=100):
    group(d, f"translate({2 * cx} 0) scale(-1 1)", fn)


def at(d: Drawing, x, y, s, fn, rot=0, flipx=False, ox=100, oy=100):
    """Draw fn (drawn around (ox, oy)) centred at (x, y), scaled by s."""
    sx = -s if flipx else s
    group(d, f"translate({x} {y}) rotate({rot}) scale({sx} {s}) translate({-ox} {-oy})", fn)


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


def drop(x, y, r):
    return f"M{x:.1f} {y - r * 1.7:.1f} Q{x + r:.1f} {y:.1f} {x:.1f} {y + r:.1f} Q{x - r:.1f} {y:.1f} {x:.1f} {y - r * 1.7:.1f}Z"


def rays(d: Drawing, xs=((50, 22), (118, 12))):
    s = "".join(f'<path d="M{x} -10 L{x + w} -10 L{x + w + 40} 210 L{x + 40} 210Z"/>' for x, w in xs)
    d.raw(f'<g opacity=".16" fill="#fff">{s}</g>', "")


def jungle(d: Drawing, spots, role="near", line=False):
    for x, y, a, ln, w in spots:
        d.shape(role, leaf(x, y, ln, w, a), line=line)


def _catmull(pts, n=8):
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in (0, 1)))
    out.append(tuple(pts[-1]))
    return out


def track(pts, n=8):
    """Dense points along a smooth curve with unit normals: [(x, y, nx, ny, t)]."""
    c = _catmull(pts, n)
    L = len(c)
    res = []
    for i, (x, y) in enumerate(c):
        a, b = c[max(i - 1, 0)], c[min(i + 1, L - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        m = math.hypot(dx, dy) or 1
        res.append((x, y, -dy / m, dx / m, i / (L - 1)))
    return res


def ribbon(pts, w0, w1=None, n=8, cap=True):
    """A tapering tube along a smooth curve through pts. w0/w1 are full widths, or w0 is a function of t."""
    tr = track(pts, n)
    wf = w0 if callable(w0) else (lambda t: w0 + (w1 - w0) * t)
    left = [(x + nx * wf(t) / 2, y + ny * wf(t) / 2) for x, y, nx, ny, t in tr]
    right = [(x - nx * wf(t) / 2, y - ny * wf(t) / 2) for x, y, nx, ny, t in tr]
    s = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in left)
    if cap:
        x, y, nx, ny, t = tr[-1]
        r = wf(1.0) / 2
        s += f" A{r:.1f} {r:.1f} 0 0 1 {right[-1][0]:.1f} {right[-1][1]:.1f}"
    s += " L" + " L".join(f"{x:.1f} {y:.1f}" for x, y in right[::-1]) + "Z"
    return s


def spiral(cx, cy, r0, r1, a0, a1, n=16):
    """Points on a spiral (degrees, clockwise on screen) from radius r0 to r1."""
    out = []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        r = r0 + (r1 - r0) * t
        out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def spiky(cx, cy, rx, ry, n=24, h=6.0, a0=0.0):
    """An ellipse edged with n spikes of height h."""
    s = ""
    for i in range(n):
        a = a0 + 2 * math.pi * i / n
        b = a0 + 2 * math.pi * (i + 0.5) / n
        s += f"{'M' if i == 0 else 'L'}{cx + rx * math.cos(a):.1f} {cy + ry * math.sin(a):.1f} "
        s += f"L{cx + (rx + h) * math.cos(b):.1f} {cy + (ry + h) * math.sin(b):.1f} "
    return s + "Z"


def toes(d: Drawing, x, y, ang, role="hero", pad=None, n=4, ln=8.0, spread=28.0, w=2.6, r=2.8):
    """Splayed toes from (x, y) around direction `ang`, each ending in a round pad."""
    s, pads = "", ""
    for i in range(n):
        a = math.radians(ang + (i - (n - 1) / 2) * spread)
        tx, ty = x + ln * math.cos(a), y + ln * math.sin(a)
        s += f"M{x:.1f} {y:.1f} L{tx:.1f} {ty:.1f} "
        pads += circle(round(tx, 1), round(ty, 1), r)
    d.stroke(role, s, w)
    d.shape(pad or role, pads, shadow=False)


def claw(x, y, ang, n=3, ln=5.0, spread=30.0):
    """Little claws/tarsi (strokes only)."""
    s = ""
    for i in range(n):
        a = math.radians(ang + (i - (n - 1) / 2) * spread)
        s += f"M{x:.1f} {y:.1f} l{ln * math.cos(a):.1f} {ln * math.sin(a):.1f} "
    return s


# ================================================================ CHAMELEON
CHAM_BODY = ("M36 90 C38 80 50 70 62 66 L74 50 C78 58 81 63 84 67 C96 52 128 50 146 72 "
             "C152 80 154 90 152 98 C140 112 110 118 86 114 C72 112 60 108 50 104 C42 102 36 98 36 90Z")


def chameleon(d: Drawing, tongue=None):
    """A chameleon facing left, feet gripping a branch at y ~127, tail curled below."""
    tail = [(138, 92), (156, 98), (170, 110)] + spiral(154, 138, 17, 4, -45, 330, 18)
    d.shape("hero", ribbon(tail, 16, 3))
    d.shape("hero", CHAM_BODY, spot=True)
    d.shape("hero2", "M86 102 C106 106 130 100 148 88 C146 98 124 110 88 108Z", shadow=False)
    d.marks("hero3", ellipse(100, 76, 5, 9) + ellipse(118, 72, 5, 9) + ellipse(136, 80, 4.5, 8))
    d.stroke("hero3", "M66 66 L74 54 L82 66", 1.6, line=False)
    if tongue:
        tx, ty = tongue
        d.stroke("tongue", f"M38 93 L{tx} {ty}", 3.6)
        d.shape("tongue", circle(tx, ty, 4.6), shadow=False, spot=True)
    d.stroke("mark", "M37 93 C44 99 54 100 62 96", 1.8)
    # turret eye
    d.shape("hero", circle(58, 80, 11.5))
    d.stroke("hero2", circle(58, 80, 7.5), 2.2, line=False)
    d.marks("mark", circle(54.5, 80, 3.6))
    d.marks("light", circle(53.5, 78.6, 1.3)) if d.paper else None
    # legs and grasping feet
    for leg, fx in (("M80 104 L88 116 L78 126", 77), ("M132 100 L124 114 L134 126", 135)):
        d.limb("hero", leg, 7.5)
        d.shape("hero", ellipse(fx, 127, 6.5, 3.4), shadow=False)
        d.stroke("hero3", f"M{fx} 124 v6", 1.4, line=False)


def branch(d: Drawing, y=124, role="branch"):
    d.shape(role, f"M-30 {y} C40 {y - 4} 120 {y + 4} 230 {y - 2} L230 {y + 11} C120 {y + 16} 40 {y + 8} -30 {y + 13}Z")


def chameleon_portrait(d: Drawing):
    d.disc("glow", 150, 50, 22)
    jungle(d, [(-6, 40, 20, 56, 14), (-4, 96, 4, 44, 12), (206, 168, 196, 50, 13)], "mid")
    branch(d, 126)
    d.shape("mid", leaf(30, 128, 26, 8, 120), shadow=False)
    d.shape("mid", leaf(44, 132, 22, 7, 80), shadow=False)
    at(d, 100, 100, 1.06, lambda: chameleon(d), ox=104, oy=104)


def chameleon_rainforest(d: Drawing):
    rays(d, ((30, 18), (100, 12)))
    jungle(d, [(-8, 30, 30, 70, 18), (208, 24, 150, 64, 16), (-6, 170, -20, 60, 16), (210, 182, 200, 56, 14)], "far")
    jungle(d, [(-6, 80, 10, 50, 13), (208, 96, 176, 50, 13)], "mid")
    for x, y, r in [(40, 44, 2.2), (150, 30, 2), (170, 60, 2.4), (60, 160, 2)]:
        d.shape("light", drop(x, y, r), shadow=False)
    branch(d, 138)
    # a cricket about to be caught
    def bug():
        d.stroke("dark", "M-6 2 l-6 8 M0 3 l-2 9 M5 2 l7 7 M-8 -4 q-10 -12 -18 -6 M-8 -2 q-8 -6 -14 2", 1.4)
        d.shape("bug", ellipse(0, 0, 9, 5), spot=False)
        d.shape("light", ellipse(2, -4, 7, 3.4), shadow=False)
    group(d, "translate(38 104) rotate(-10) scale(1.3)", bug)
    at(d, 124, 138, 0.8, lambda: chameleon(d, tongue=(-2, 86)), ox=104, oy=127)
    d.shape("near", leaf(-10, 196, 60, 16, -40))
    d.shape("near", leaf(210, 200, 60, 16, -140))


# ================================================================ GECKO
GECKO_BODY = "M100 60 C115 60 122 76 122 96 C122 116 114 130 100 134 C86 130 78 116 78 96 C78 76 85 60 100 60Z"
GECKO_HEAD = "M100 16 C110 16 118 26 121 38 C123 50 116 62 100 64 C84 62 77 50 79 38 C82 26 90 16 100 16Z"


def gecko(d: Drawing):
    """A day gecko seen from above, nose up, centred on (100, 96)."""
    def legs():
        d.limb("hero", "M88 78 L66 72 L58 56", 8)
        toes(d, 58, 56, -118, "hero", "pad", n=5, ln=9, spread=26, w=2.8, r=3.4)
        d.limb("hero", "M88 116 L66 124 L60 142", 8)
        toes(d, 60, 142, 112, "hero", "pad", n=5, ln=9, spread=26, w=2.8, r=3.4)
    legs()
    flip(d, legs)
    d.shape("hero", ribbon([(100, 124), (100, 146), (106, 162), (120, 172), (136, 170), (144, 158)], 20, 4))
    d.shape("hero", GECKO_BODY, spot=True)
    d.shape("hero", GECKO_HEAD)
    d.marks("pop", ellipse(100, 27, 2.6, 7) + circle(100, 46, 2.6) + circle(93, 80, 3) + circle(107, 90, 3.4)
            + circle(95, 103, 2.8) + circle(108, 114, 3) + circle(98, 124, 2.6) + circle(101, 150, 2.4) + circle(112, 165, 2))
    for ex in (82, 118):
        d.shape("hero", circle(ex, 36, 8.5), shadow=False)
        d.shape("eye", circle(ex, 36, 6.5), shadow=False, spot=True)
        d.marks("mark", ellipse(ex, 36, 1.7, 5.2))
        if d.paper:
            d.marks("light", circle(ex + (1.8 if ex > 100 else -1.8) - 0.6, 33, 1.4))


def gecko_portrait(d: Drawing):
    d.disc("glow", 46, 50, 20)
    big = leaf(10, 200, 240, 68, -52)
    d.shape("leafc", big)
    d.stroke("leafv", "M10 200 L158 11", 2.4, line=False)
    vein = ""
    for t in (0.2, 0.35, 0.5, 0.65, 0.8):
        x, y = 10 + 148 * t, 200 - 189 * t
        vein += f"M{x:.1f} {y:.1f} l{-34 * (1 - t) - 8:.1f} {-6:.1f} M{x:.1f} {y:.1f} l{10:.1f} {30 * (1 - t) + 8:.1f} "
    d.stroke("leafv", vein, 1.6, line=False)
    at(d, 104, 100, 0.86, lambda: gecko(d), rot=38, ox=100, oy=96)


def moth(d: Drawing, x, y, s=1.0, rot=0):
    def draw():
        d.shape("moth", "M0 0 C-8 -10 -20 -10 -22 -2 C-20 6 -10 8 0 4Z M0 0 C8 -10 20 -10 22 -2 C20 6 10 8 0 4Z")
        d.shape("moth2", "M0 2 C-6 6 -14 10 -14 16 C-8 16 -2 10 0 6Z M0 2 C6 6 14 10 14 16 C8 16 2 10 0 6Z", shadow=False)
        d.marks("mark", ellipse(0, 4, 2, 8))
        d.stroke("mark", "M-1 -3 q-4 -8 -10 -10 M1 -3 q4 -8 10 -10", 1.2)
    group(d, f"translate({x} {y}) rotate({rot}) scale({s})", draw)


def gecko_lamp(d: Drawing):
    d.disc("glow", 58, 62, 13)
    d.band("far", hills(124, 10), line=False)
    d.band("mid", hills(140, 8, 30), line=False)
    win = "M22 150 V82 A38 38 0 0 1 98 82 V150Z"
    d.shape("wall", f"M-30 -30 H230 V230 H-30Z {win}", extra='fill-rule="evenodd"')
    d.shape("sill", rrect(16, 148, 88, 8, 3))
    # lantern with a warm halo
    d.raw('<circle cx="152" cy="62" r="34" fill="#FFE7A0" opacity=".55"/>', "")
    d.stroke("dark", "M184 48 H160 V40", 2.6)
    d.shape("dark", "M144 44 H160 L164 50 H140Z")
    d.shape("lamp", rrect(142, 50, 20, 22, 4), spot=True)
    d.shape("dark", "M140 72 H164 L160 78 H144Z")
    moth(d, 118, 44, 0.7, -20)
    # bougainvillea spilling over the top
    jungle(d, [(-6, 18, 30, 44, 11), (40, 4, 70, 36, 9), (90, 0, 100, 30, 8)], "leafg")
    for x, y in [(14, 34), (30, 22), (50, 28), (70, 16), (38, 42), (86, 26), (104, 16), (22, 50)]:
        d.shape("bloom", circle(x, y - 3.5, 3.6) + circle(x - 3.2, y + 2, 3.6) + circle(x + 3.2, y + 2, 3.6), shadow=False, spot=True)
        d.marks("light", circle(x, y, 1.1)) if d.paper else None
    at(d, 132, 132, 0.6, lambda: gecko(d), rot=-24, ox=100, oy=96)


# ================================================================ GREEN IGUANA
GIG_HEAD = ("M28 92 C28 78 42 68 62 66 C86 62 110 66 126 76 C140 86 150 98 160 110 C172 124 180 142 184 162 "
            "L188 210 L80 210 C84 186 88 164 86 146 L76 128 C60 124 40 116 33 106 C30 101 28 97 28 92Z")


def iguana_portrait(d: Drawing):
    d.disc("glow", 156, 44, 18)
    jungle(d, [(-6, 150, -30, 56, 14), (-8, 190, -10, 60, 15)], "mid")
    # dorsal crest
    sp = ""
    for i in range(11):
        t = i / 10
        x, y = 118 + 66 * t, 70 + 74 * t ** 1.3
        h = 20 - 8 * t
        sp += f"M{x - 5:.1f} {y + 4:.1f} L{x + h * 0.5:.1f} {y - h:.1f} L{x + 6:.1f} {y + 6:.1f}Z "
    d.shape("crest", sp)
    # dewlap with its little spikes
    dew = "M40 112 C40 134 54 160 80 170 C90 158 92 142 88 128 C72 124 54 118 40 112Z"
    d.shape("hero2", dew, spot=True)
    s = ""
    for i in range(6):
        t = i / 5
        x, y = 42 + 26 * t ** 1.2, 120 + 44 * t
        s += f"M{x:.1f} {y - 4:.1f} L{x - 6:.1f} {y + 1:.1f} L{x + 1:.1f} {y + 3:.1f}Z "
    d.shape("crest", s, shadow=False)
    d.shape("hero", GIG_HEAD)
    d.shape("band", "M118 130 C130 124 150 128 162 140 L168 160 C152 150 132 146 116 150Z", shadow=False)
    d.shape("band", "M110 176 C128 168 156 172 176 186 L178 210 L108 210Z", shadow=False)
    d.marks("hero2", circle(60, 74, 2) + circle(78, 70, 2.2) + circle(96, 70, 2) + circle(112, 76, 1.8) + circle(130, 104, 2) + circle(140, 118, 2))
    # subtympanic shield
    d.shape("plate", circle(106, 106, 10), shadow=False)
    d.stroke("hero2", circle(106, 106, 10), 1.4, line=False)
    d.stroke("mark", "M30 100 C46 110 66 112 84 108", 2.2)
    d.shape("eye", circle(68, 84, 6.2), shadow=False)
    d.marks("mark", circle(68, 84, 3))
    d.marks("light", circle(66.5, 82.5, 1.2))
    d.stroke("mark", "M58 77 Q68 70 79 77", 2)
    d.marks("mark", circle(36, 86, 2))


def iguana_side(d: Drawing):
    """A green iguana lying side-on facing right, belly at y ~132, tail tip off to the left."""
    tr = [(-6, 156), (20, 150), (48, 140), (78, 130), (106, 124), (132, 118)]
    w = lambda t: 2 + 22 * (t / 0.75) ** 1.3 if t < 0.75 else 24 - (t - 0.75) * 30
    d.limb("hero", "M86 128 L74 142 L62 144 M114 122 L126 138 L138 140", 7)
    d.stroke("mark", "M62 144 l-6 -2 M62 144 l-6 2 M138 140 l6 -2 M138 140 l6 2", 1.4, line=False)
    sp = ""
    for x, y, nx, ny, t in track(tr)[14::3]:
        h = 3 + 9 * math.sin(math.pi * min((t - 0.3) * 1.4, 1)) if t > 0.3 else 3
        hw = w(t) / 2
        bx, by = x - nx * (hw - 1.5), y - ny * (hw - 1.5)
        sp += f"M{bx - 3:.1f} {by + 1:.1f} L{bx - nx * h + 2:.1f} {by - ny * h:.1f} L{bx + 3:.1f} {by + 1:.1f}Z "
    d.shape("crest", sp)
    body = ribbon(tr, w, cap=False)
    d.shape("hero", body, spot=True)
    bands = ""
    for x, y, nx, ny, t in track(tr)[2:24:4]:
        hw = w(t) / 2 + 0.5
        bands += f"M{x + nx * hw:.1f} {y + ny * hw:.1f} L{x - nx * hw:.1f} {y - ny * hw:.1f} "
    d.stroke("band", bands, 3.2, line=False)
    d.shape("band", ellipse(96, 128, 8, 4) + ellipse(72, 134, 6, 3.4), shadow=False, line=False)
    d.shape("hero2", "M134 122 C138 132 146 140 156 140 C158 134 158 128 156 122Z", spot=True)
    d.shape("hero", "M122 108 C130 96 152 96 164 102 C172 106 174 116 168 122 L138 128 C128 126 120 118 122 108Z")
    d.shape("plate", circle(138, 117, 4.4), shadow=False)
    d.marks("eye", circle(152, 107, 2.8))
    d.marks("mark", circle(152, 107, 1.4))
    d.stroke("mark", "M171 116 Q160 121 146 120", 1.4)


def iguana_tulum(d: Drawing):
    d.disc("glow", 52, 46, 16)
    d.shape("light", cloud(120, 40, 0.8), shadow=False)
    d.band("sea", "M-30 108 H230")
    d.stroke("light", "M14 118 q8 -4 16 0 M50 126 q8 -4 16 0", 2, line=False)
    # cliff and El Castillo
    d.shape("rock", "M96 112 C104 100 120 96 140 96 L230 92 V140 H90Z")
    d.shape("stone", "M118 98 V70 H124 V64 H176 V70 H182 V98Z")
    d.shape("stone", "M136 64 V54 H164 V64Z", shadow=False)
    d.marks("dark", rrect(128, 78, 7, 18, 2) + rrect(146.5, 78, 7, 18, 2) + rrect(165, 78, 7, 18, 2))
    d.stroke("rock", "M124 72 H176", 1.4, line=False)
    # palm
    d.limb("trunk", "M54 138 C56 120 60 100 70 84", 4.5)
    for a in (-160, -120, -60, -20, 30, 170):
        d.shape("palm", leaf(70, 84, 26, 6, a), shadow=False)
    # foreground stone platform
    d.shape("stone2", "M-30 140 L230 136 V230 H-30Z")
    d.stroke("rock", "M-30 160 H230 M30 140 V160 M90 138 V160 M150 137 V160 M0 160 V190 M60 160 V190 M120 160 V190 M180 160 V190 M-30 190 H230", 1.6, line=False)
    at(d, 92, 138, 0.96, lambda: iguana_side(d), ox=100, oy=132)


# ================================================================ THORNY DEVIL
def thorny_devil(d: Drawing):
    """A thorny devil side-on facing left, feet at y ~140, tail up."""
    tail = [(136, 112), (156, 104), (168, 88), (170, 68)]
    tr = track(tail)
    sp = ""
    for i, (x, y, nx, ny, t) in enumerate(tr[2::3]):
        hw = (18 - 13 * t) / 2
        for k in (1, -1):
            bx, by = x + nx * hw * k, y + ny * hw * k
            sp += f"M{bx - ny * 2.6:.1f} {by + nx * 2.6:.1f} L{bx + nx * k * 6:.1f} {by + ny * k * 6:.1f} L{bx + ny * 2.6:.1f} {by - nx * 2.6:.1f}Z "
    d.shape("hero", sp, shadow=False)
    d.shape("hero", ribbon(tail, 18, 5))
    d.stroke("hero2", "M150 106 l6 6 M160 94 l8 2 M166 80 l7 -1", 4, line=False)
    # far legs
    d.limb("hero3", "M92 124 L88 140", 6)
    d.limb("hero3", "M122 124 L126 140", 6)
    body = spiky(106, 110, 40, 22, 30, 6)
    d.shape("hero", body, spot=True)

    def pattern():
        d.shape("hero2", ellipse(86, 112, 7, 10) + ellipse(112, 108, 8, 11) + ellipse(136, 112, 6, 9), shadow=False, line=False)
        d.shape("light", "M70 94 C90 86 120 84 146 94 L146 98 C120 90 90 92 70 100Z", shadow=False)
        cones = ""
        for x, y in [(76, 118), (96, 120), (118, 120), (136, 118), (88, 110), (104, 110), (124, 112), (98, 98), (126, 98), (80, 102), (140, 104)]:
            cones += f"M{x - 2.6} {y + 2} L{x} {y - 4} L{x + 2.6} {y + 2}Z "
        if d.paper:
            d.marks("spike", cones)
    clipped(d, ellipse(106, 110, 40, 22), pattern)
    # near legs
    d.limb("hero", "M76 120 L64 132 L58 140", 7)
    d.limb("hero", "M134 120 L146 132 L152 140", 7)
    d.stroke("mark", claw(58, 140, 180, 3, 6) + claw(152, 140, 0, 3, 6), 1.6)
    # false head knob on the neck
    d.shape("hero", spiky(76, 90, 9, 8, 10, 5))
    d.shape("hero2", circle(76, 90, 5), shadow=False)
    # head
    d.shape("hero", "M54 96 L50 80 L60 92 L64 96 L68 82 L72 98Z")
    d.shape("hero", "M36 112 C36 102 44 94 56 94 C66 94 74 102 74 112 C74 120 66 125 55 125 C44 125 36 120 36 112Z")
    d.shape("hero2", "M40 104 C46 98 58 96 66 100 L62 104 C56 102 48 102 42 106Z", shadow=False)
    d.marks("eye", circle(55, 106, 3.4))
    d.marks("mark", circle(54.5, 106, 1.8))
    if d.paper:
        d.marks("light", circle(54, 105, 0.8))
    d.stroke("mark", "M38 114 Q46 119 56 116", 1.6)


def devil_portrait(d: Drawing):
    d.disc("glow", 150, 52, 22)
    d.band("red", hills(150, 10, 10))
    d.band("red2", hills(176, 6, -20), line=False)
    at(d, 100, 106, 1.2, lambda: thorny_devil(d), ox=104, oy=104)


def devil_uluru(d: Drawing):
    d.disc("glow", 152, 48, 16)
    d.band("red2", "M-30 128 H230", line=False)
    uluru = "M18 128 C22 106 38 92 66 88 C104 84 146 86 166 94 C180 100 186 114 188 128Z"
    d.shape("uluru", uluru)
    d.stroke("uluru2", "M54 92 C58 104 56 116 60 128 M86 88 C88 102 92 114 90 128 M118 87 C116 100 122 114 120 128 M150 90 C148 104 154 116 152 128", 2, line=False)
    d.band("red", "M-30 132 Q100 124 230 134")
    for x, y, s in [(26, 140, 1.0), (176, 142, 1.1), (110, 136, 0.7)]:
        p = f"M{x - 10 * s} {y} "
        for i in range(7):
            a = math.radians(-160 + i * 23.3)
            p += f"L{x + math.cos(a) * 14 * s:.1f} {y + math.sin(a) * 14 * s:.1f} L{x + (i - 3) * 2.6 * s + 1.3 * s:.1f} {y - 2 * s:.1f} "
        p += f"L{x + 10 * s} {y}Z"
        d.shape("spin", p, shadow=False, line=False)
    at(d, 98, 162, 0.92, lambda: thorny_devil(d), ox=104, oy=140)
    d.band("red2", hills(184, 3, 30), line=False)


# ================================================================ RED-EYED TREE FROG
def frog_eye(d: Drawing, x, y, r):
    d.shape("hero", circle(x, y, r + 3.5))
    d.shape("eye", circle(x, y, r), shadow=False, spot=True)
    d.marks("mark", ellipse(x, y, r * 0.24, r * 0.68))
    d.marks("light", circle(x + r * 0.32, y - r * 0.42, r * 0.2)) if d.paper else None


def treefrog_front(d: Drawing):
    def side():
        d.shape("hero", "M64 126 C48 116 30 124 28 138 C27 150 44 156 66 150Z")
        toes(d, 36, 150, 150, "feet", "feet", n=4, ln=11, spread=30, w=3, r=3.6)
    side()
    flip(d, side)
    d.shape("hero", "M100 60 C132 60 148 82 148 108 C148 134 128 150 100 150 C72 150 52 134 52 108 C52 82 68 60 100 60Z", spot=False)

    def flank():
        d.shape("blue", "M54 98 C49 114 54 134 66 146 C73 140 73 122 66 102Z", shadow=False, spot=True)
        d.stroke("bar", "M55 112 L66 109 M56 122 L69 120 M60 133 L70 131", 2.4, line=False)
    flank()
    flip(d, flank)
    d.shape("belly", ellipse(100, 130, 24, 16), shadow=False)

    def arm():
        d.limb("hero", "M76 108 L70 134 L74 150", 9)
        toes(d, 74, 151, 90, "feet", "feet", n=4, ln=9, spread=32, w=3, r=3.6)
    arm()
    flip(d, arm)
    frog_eye(d, 70, 64, 15.5)
    frog_eye(d, 130, 64, 15.5)
    d.stroke("mark", "M70 98 Q100 114 130 98", 2.2)
    d.marks("mark", circle(94, 84, 1.6) + circle(106, 84, 1.6))


def treefrog_portrait(d: Drawing):
    jungle(d, [(-6, 40, 20, 56, 14), (206, 50, 160, 56, 14), (-4, 100, 0, 44, 12), (204, 104, 180, 44, 12)], "mid")
    for x, y, r in [(40, 66, 2.2), (160, 36, 2), (170, 120, 2.4), (28, 130, 2)]:
        d.shape("light", drop(x, y, r), shadow=False)
    d.shape("leafc", "M-30 156 C30 146 150 142 230 154 V230 H-30Z")
    d.stroke("leafv", "M-30 182 C40 172 140 168 230 176 M40 176 L20 154 M90 172 L76 148 M140 172 L132 150", 2, line=False)
    at(d, 100, 98, 1.08, lambda: treefrog_front(d), ox=100, oy=106)


def treefrog_side(d: Drawing):
    """A red-eyed tree frog sitting side-on facing left, feet at y ~140."""
    d.shape("hero", "M40 110 C40 96 50 86 64 84 C84 80 108 72 128 76 C146 80 154 96 150 112 C146 128 128 136 104 136 "
                    "C80 136 54 130 44 122 C41 118 40 114 40 110Z", spot=False)
    d.shape("blue", "M82 116 C100 110 120 112 134 120 C124 132 102 136 86 132Z", shadow=False, spot=True)
    d.stroke("bar", "M92 116 L94 132 M104 113 L106 134 M116 114 L118 132 M126 117 L127 128", 2.2, line=False)
    d.shape("belly", "M44 120 C56 130 76 134 92 134 C76 138 54 134 44 124Z", shadow=False)
    # hind leg folded along the side
    d.shape("hero", "M150 106 C160 116 158 130 146 134 C132 136 120 132 118 124 C126 118 138 110 150 106Z")
    d.limb("hero", "M150 128 L118 138", 7)
    d.limb("feet", "M118 138 L104 140", 4)
    toes(d, 104, 140, 180, "feet", "feet", n=4, ln=9, spread=24, w=2.6, r=3.2)
    # front leg
    d.limb("hero", "M66 116 L62 130 L58 138", 7)
    toes(d, 58, 139, 120, "feet", "feet", n=4, ln=8, spread=30, w=2.6, r=3.2)
    frog_eye(d, 66, 82, 12)
    d.stroke("mark", "M41 112 C50 117 62 117 72 113", 1.8)
    d.marks("mark", circle(43, 102, 1.4))


def treefrog_night(d: Drawing):
    d.disc("glow", 148, 50, 18)
    d.marks("light", circle(40, 40, 1.6) + circle(70, 26, 1.2) + circle(116, 34, 1.4) + circle(30, 76, 1.2) + circle(176, 90, 1.4))
    jungle(d, [(-8, 70, -10, 70, 18), (210, 76, 190, 70, 18), (-8, 150, -30, 60, 16)], "far")
    jungle(d, [(206, 150, 210, 56, 14)], "mid")
    d.shape("leafc", "M-10 178 C30 150 100 130 196 118 C170 150 110 176 -10 186Z")
    d.stroke("leafv", "M-4 180 C60 156 120 138 190 120 M50 162 L30 154 M90 148 L72 136 M130 138 L118 126 M60 160 L66 176 M110 146 L118 162", 1.8, line=False)
    d.stroke("stem", "M-10 186 C10 196 30 204 60 210", 4)
    at(d, 104, 140, 0.92, lambda: treefrog_side(d), rot=-8, ox=96, oy=140)


# ================================================================ AXOLOTL
def gill(d: Drawing, pts, w0=7.0, fringe=6.0):
    tr = track(pts, 8)
    s = ""
    for x, y, nx, ny, t in tr[1::2]:
        f = fringe * (1 - 0.35 * t)
        s += f"M{x - nx * f:.1f} {y - ny * f:.1f} L{x + nx * f:.1f} {y + ny * f:.1f} "
    d.stroke("gill2", s, 3)
    d.shape("gill", ribbon(pts, w0, 3), spot=True, shadow=False)


def axolotl_face(d: Drawing):
    def gills():
        gill(d, [(60, 76), (46, 58), (34, 40)])
        gill(d, [(52, 90), (34, 80), (16, 74)])
        gill(d, [(52, 106), (32, 108), (14, 114)])
    gills()
    flip(d, gills)
    d.shape("hero", "M74 128 C70 160 80 190 100 206 C120 190 130 160 126 128Z")
    d.shape("hero2", "M86 140 C84 166 90 186 100 196 C110 186 116 166 114 140Z", shadow=False)

    def arm():
        d.limb("hero", "M78 136 L64 152 L60 164", 7)
        toes(d, 60, 165, 110, "hero", "hero", n=4, ln=6, spread=30, w=2.4, r=2.2)
    arm()
    flip(d, arm)
    d.shape("hero", "M100 58 C138 58 158 78 158 100 C158 124 134 140 100 140 C66 140 42 124 42 100 C42 78 62 58 100 58Z")
    d.shape("hero2", "M64 72 C78 64 94 62 110 64 C96 68 80 72 68 80Z", shadow=False, line=False)
    d.marks("blush", ellipse(66, 112, 9, 5) + ellipse(134, 112, 9, 5))
    d.marks("mark", circle(74, 94, 5) + circle(126, 94, 5))
    if d.paper:
        d.marks("light", circle(75.5, 92, 1.6) + circle(127.5, 92, 1.6))
    d.stroke("mark", "M74 110 Q100 128 126 110", 2.4)
    d.marks("mark", circle(94, 80, 1.2) + circle(106, 80, 1.2))


def axolotl_portrait(d: Drawing):
    d.band("far", hills(170, 6), line=False)
    for x, h, k in [(20, 70, 1), (178, 80, -1), (34, 50, -1)]:
        d.shape("weed", f"M{x} 200 C{x + 10 * k} {200 - h * 0.4} {x - 8 * k} {200 - h * 0.7} {x + 4 * k} {200 - h} "
                        f"C{x + 10 * k} {200 - h * 0.7} {x + 16 * k} {200 - h * 0.4} {x + 8} 200Z", shadow=False)
    bubbles(d, [(160, 40, 4), (170, 26, 2.8), (150, 54, 2.2), (36, 150, 2.4)])
    at(d, 100, 96, 1.0, lambda: axolotl_face(d), ox=100, oy=100)
    d.band("ground", "M-30 182 Q40 172 100 178 T230 176")
    d.marks("pebble", ellipse(40, 190, 6, 3) + ellipse(140, 186, 7, 3.4) + ellipse(166, 194, 5, 2.6) + ellipse(80, 194, 5, 2.6))


def axolotl_side(d: Drawing):
    """An axolotl swimming, facing left, centred around (100, 100)."""
    d.shape("hero2", "M96 92 C126 80 160 74 192 66 C184 92 162 112 132 120 C112 122 100 112 96 92Z", spot=True)
    d.limb("hero", "M122 114 L118 130", 6)
    toes(d, 118, 131, 100, "hero", "hero", n=4, ln=5, spread=30, w=2, r=1.8)
    d.shape("hero", "M26 102 C26 86 42 78 60 80 C80 82 92 90 110 92 C140 94 162 88 186 76 C178 92 160 108 136 114 "
                    "C112 120 84 120 64 122 C42 124 26 116 26 102Z")
    d.limb("hero", "M64 116 L56 132", 6)
    toes(d, 56, 133, 110, "hero", "hero", n=4, ln=5, spread=30, w=2, r=1.8)
    gill(d, [(62, 86), (58, 68), (48, 54)], 6, 5)
    gill(d, [(68, 88), (72, 68), (74, 52)], 6, 5)
    gill(d, [(72, 92), (86, 76), (98, 66)], 6, 5)
    d.marks("blush", ellipse(48, 108, 6, 3.4))
    d.marks("mark", circle(42, 96, 3.4))
    if d.paper:
        d.marks("light", circle(43, 94.6, 1.1))
    d.stroke("mark", "M27 106 Q36 114 50 110", 2)


def axolotl_canal(d: Drawing):
    d.disc("glow", 160, 30, 13)
    d.band("far", hills(66, 6), line=False)
    # trajinera boat on the canal
    d.stroke("dark", "M50 62 V44 M150 62 V44", 2.4)
    d.shape("roof", "M40 46 Q100 32 160 46 L160 52 Q100 40 40 52Z")
    d.shape("sign", "M20 60 V44 Q36 30 56 44 V60Z", spot=True)
    d.marks("pop", circle(30, 50, 2.6) + circle(38, 44, 2.6) + circle(46, 50, 2.6))
    d.shape("hull", "M14 60 H178 L168 76 H26Z")
    d.shape("pop", "M22 64 H174 L172 68 H24Z", shadow=False)
    d.band("mid", waves(72, 3, 24))
    d.band("near", waves(118, 4, 32), line=False)
    d.band("deep", waves(160, 4, 36), line=False)
    for x, h, k in [(18, 70, 1), (180, 90, -1), (154, 60, 1)]:
        d.shape("weed", f"M{x} 210 C{x + 10 * k} {210 - h * 0.4} {x - 8 * k} {210 - h * 0.7} {x + 4 * k} {210 - h} "
                        f"C{x + 10 * k} {210 - h * 0.7} {x + 16 * k} {210 - h * 0.4} {x + 8} 210Z", shadow=False, line=False)
    bubbles(d, [(30, 110, 2.4), (24, 98, 3.2)])
    at(d, 104, 130, 0.92, lambda: axolotl_side(d), rot=-6, ox=100, oy=100)


# ================================================================ PRAYING MANTIS
def mantis(d: Drawing):
    """A praying mantis side-on facing left, head turned to us, feet at y ~158."""
    d.limb("hero3", "M104 122 L96 138 L102 158", 3.4)
    d.limb("hero3", "M112 124 L128 140 L134 158", 3.4)
    d.shape("hero", "M98 116 C124 112 160 116 186 128 C170 142 128 142 100 132Z")
    d.stroke("hero3", "M120 136 l2 -4 M136 137 l2 -5 M152 136 l2 -5 M166 133 l2 -4", 1.4, line=False)
    d.shape("hero2", "M98 114 C122 102 158 104 188 124 C160 130 126 128 100 124Z", spot=True)
    d.stroke("hero3", "M104 118 C130 112 158 114 184 124", 1.4, line=False)
    d.limb("hero", "M100 124 L84 138 L76 158", 3.6)
    d.limb("hero", "M110 126 L138 142 L150 158", 3.6)
    d.stroke("mark", "M76 158 l-5 0 M102 158 l5 0 M150 158 l5 0 M134 158 l5 0", 1.4, line=False)
    # far raptorial arm
    d.limb("hero3", "M78 78 L72 100 L56 90 L62 104", 5)
    # neck (prothorax)
    d.shape("hero", "M96 126 C88 106 78 86 70 66 L80 62 C88 82 98 102 106 120Z")
    # near raptorial arm, folded in prayer
    d.limb("hero", "M82 76 L76 100", 7)
    d.limb("hero", "M76 100 L54 86", 8)
    d.stroke("hero3", "M60 92 l-2 5 M66 96 l-2 5 M71 99 l-1 5", 1.6, line=False)
    d.limb("hero", "M56 86 L64 102", 4)
    d.stroke("hero", "M64 102 l-5 3", 2.4)
    # head
    d.stroke("mark", "M70 44 C66 30 60 20 50 14 M80 44 C86 30 94 22 104 18", 1.4)
    d.shape("hero", "M54 46 C60 38 90 38 96 46 C96 54 84 66 75 72 C66 66 54 54 54 46Z")
    for ex in (59, 91):
        d.shape("eye", circle(ex, 47, 7.5), shadow=False, spot=True)
        d.marks("mark", circle(ex + (2 if ex < 75 else -2), 48, 2.2))
    d.stroke("mark", "M70 60 Q75 63 80 60", 1.4)


def mantis_portrait(d: Drawing):
    d.disc("glow", 152, 50, 20)
    d.shape("light", cloud(140, 92, 0.8), shadow=False)
    d.limb("stem", "M-20 172 C40 160 120 158 220 150", 6)
    d.shape("mid", leaf(30, 166, 30, 9, 120), shadow=False)
    d.shape("mid", leaf(168, 152, 30, 9, -60), shadow=False)
    d.shape("mid", leaf(190, 150, 26, 8, 40), shadow=False)
    at(d, 106, 112, 1.0, lambda: mantis(d), ox=118, oy=110)


def flower(d: Drawing, x, y, r, petal="pop", centre="hero2", n=10):
    p = ""
    for i in range(n):
        a = 360 * i / n
        p += leaf(x, y, r, r * 0.3, a) + " "
    d.shape(petal, p, spot=True)
    d.shape(centre, circle(x, y, r * 0.36), shadow=False)


def mantis_garden(d: Drawing):
    d.disc("glow", 46, 50, 18)
    d.band("far", hills(130, 10))
    d.band("near", hills(160, 8, 30))
    d.stroke("stem", "M30 200 C32 176 34 160 36 148 M176 200 C172 180 170 168 168 160", 2.6)
    flower(d, 36, 146, 12, "pop", "flowerc", 8)
    flower(d, 168, 158, 10, "light", "flowerc", 8)
    d.limb("stem", "M122 210 C120 180 116 156 114 140", 5)
    d.shape("stem", leaf(118, 176, 30, 8, -30), shadow=False)
    flower(d, 112, 132, 22, "petal", "flowerc", 12)
    at(d, 102, 120, 0.72, lambda: mantis(d), ox=118, oy=158)


# ================================================================ BUTTERFLIES
MORPHO_FW = "M102 90 C116 62 146 40 178 36 C186 36 188 42 184 50 C178 66 172 82 166 98 C146 106 122 106 104 100Z"
MORPHO_HW = "M103 100 C126 100 156 104 168 116 C172 128 166 140 156 148 C146 156 132 160 120 158 C110 152 104 130 103 108Z"
MONARCH_FW = "M102 90 C118 60 152 36 184 32 C190 32 192 38 188 44 C178 62 166 82 156 100 C138 106 120 104 104 100Z"
MONARCH_HW = "M103 100 C124 98 150 102 160 114 C164 130 154 146 136 152 C122 156 110 148 104 128 C102 118 102 108 103 100Z"


def butterfly_body(d: Drawing, dots=False):
    d.stroke("edge", "M98 82 C94 66 88 56 80 50 M102 82 C106 66 112 56 120 50", 1.6)
    d.marks("edge", circle(80, 50, 2.2) + circle(120, 50, 2.2))
    d.shape("edge", ellipse(100, 116, 3.6, 18), shadow=False)
    d.shape("edge", ellipse(100, 94, 5, 11), shadow=False)
    d.shape("edge", circle(100, 82, 5), shadow=False)
    if dots:
        d.marks("light", circle(98, 90, 1) + circle(102, 96, 1) + circle(98, 80, 0.9) + circle(102, 84, 0.9))


def morpho(d: Drawing):
    def half():
        for w, r1, r2 in ((MORPHO_HW, 54, 32), (MORPHO_FW, 60, 36)):
            d.shape("edge", w)

            def paint(r1=r1, r2=r2):
                d.shape("blue", circle(100, 98, r1), shadow=False, spot=True)
                d.shape("blue2", circle(108, 92, r2), shadow=False, line=False)
            clipped(d, w, paint)
        d.marks("light", circle(174, 50, 2.2) + circle(170, 62, 1.8) + circle(176, 42, 1.4) + circle(164, 76, 1.6)
                + circle(160, 146, 1.6) + circle(148, 154, 1.6) + circle(166, 132, 1.6))
        d.stroke("edge", "M106 98 L150 70 M106 100 L150 92 M106 104 L140 132 M106 106 L122 146", 1.1, line=False)
    half()
    flip(d, half)
    butterfly_body(d)


def monarch(d: Drawing):
    def half():
        for w in (MONARCH_HW, MONARCH_FW):
            d.shape("orange", w, spot=True)

            def paint(w=w):
                d.shape("orange2", circle(104, 98, 26), shadow=False, line=False)
                d.stroke("edge", w, 12)
                d.stroke("edge", "M104 96 L150 64 M104 96 L170 54 M104 98 L160 80 M104 100 L150 98 M104 98 L130 60 "
                                 "M104 102 L156 116 M104 104 L150 136 M104 104 L132 150 M104 106 L114 148", 2)
            clipped(d, w, paint)
        d.shape("edge", "M150 46 C164 36 178 32 186 32 C192 32 192 38 188 44 C182 56 176 64 168 68 C160 58 154 52 150 46Z", shadow=False, line=False)
        d.marks("light", circle(160, 44, 1.6) + circle(170, 40, 1.6) + circle(180, 38, 1.4) + circle(186, 44, 1.2) + circle(180, 52, 1.4)
                + circle(172, 62, 1.4) + circle(166, 74, 1.3) + circle(160, 86, 1.3) + circle(154, 96, 1.3)
                + circle(158, 120, 1.3) + circle(156, 132, 1.3) + circle(148, 142, 1.3) + circle(136, 149, 1.3) + circle(124, 150, 1.3))
        d.marks("orange2", circle(166, 52, 1.8) + circle(176, 48, 1.6) + circle(160, 60, 1.6))
    half()
    flip(d, half)
    butterfly_body(d, dots=True)


def morpho_portrait(d: Drawing):
    jungle(d, [(-6, 160, -30, 60, 16), (206, 170, 200, 56, 14), (-8, 40, 20, 46, 12)], "mid")
    for x, y, r in [(30, 100, 2.2), (176, 104, 2), (150, 180, 2.4)]:
        d.shape("light", drop(x, y, r), shadow=False)
    at(d, 100, 98, 1.08, lambda: morpho(d), rot=-6, ox=100, oy=98)


def morpho_rainforest(d: Drawing):
    rays(d, ((40, 20), (110, 14)))
    d.band("far", "M-30 120 Q-10 100 14 108 Q30 88 54 100 Q74 84 96 98 Q118 82 140 96 Q160 84 182 100 Q204 90 230 104", line=False)
    d.band("mid", "M-30 150 Q0 132 30 142 Q56 124 84 140 Q112 126 138 140 Q166 124 196 140 Q214 132 230 140")
    jungle(d, [(-8, 40, 30, 70, 18), (208, 30, 150, 64, 16), (-6, 110, -10, 56, 15), (208, 120, 190, 56, 15)], "near")
    jungle(d, [(-10, 200, -50, 64, 17), (210, 200, -130, 64, 17), (60, 210, -80, 40, 11)], "deep")
    at(d, 140, 50, 0.3, lambda: morpho(d), rot=20, ox=100, oy=98)
    at(d, 92, 104, 0.66, lambda: morpho(d), rot=-14, ox=100, oy=98)


def mini_monarch(x, y, s=1.0, rot=0.0, closed=False):
    """A tiny monarch glyph (two wing pairs) for swarms."""
    pts = [(-1, 0), (-10, -8), (-11, -1), (-6, 6), (0, 2), (6, 6), (11, -1), (10, -8), (1, 0)]
    if closed:
        pts = [(0, 0), (-3, -10), (4, -12), (6, -2), (2, 4)]
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)
    return "M" + " L".join(f"{x + (px * ca - py * sa) * s:.1f} {y + (px * sa + py * ca) * s:.1f}" for px, py in pts) + "Z"


def monarch_portrait(d: Drawing):
    d.disc("glow", 100, 100, 70, line=False)
    d.shape("light", cloud(10, 170, 1.2), shadow=False)
    d.shape("light", cloud(150, 30, 0.9), shadow=False)
    at(d, 100, 98, 1.06, lambda: monarch(d), rot=-6, ox=100, oy=98)


def monarch_forest(d: Drawing):
    d.disc("glow", 150, 46, 18)
    d.band("far", hills(110, 12))

    def fir(x, base, h, w, role="fir"):
        p = f"M{x} {base - h} "
        for i in range(4):
            y = base - h + h * (i + 1) / 4
            hw = w * (i + 1) / 4
            p += f"L{x + hw:.1f} {y:.1f} L{x + hw * 0.45:.1f} {y - 2:.1f} "
        p += f"L{x - w * 0.45:.1f} {base - 2} "
        for i in range(3, -1, -1):
            y = base - h + h * (i + 1) / 4
            hw = w * (i + 1) / 4
            p += f"L{x - hw:.1f} {y:.1f} " + (f"L{x - hw * 0.45 - w / 4 * 0.55:.1f} {y - h / 4 + 2:.1f} " if i else "")
        d.shape(role, p + "Z")
        d.stroke("trunk", f"M{x} {base - 2} V{base + 12}", 4)
    fir(30, 160, 120, 34)
    fir(176, 158, 110, 30)
    fir(104, 130, 70, 22, "fir2")
    # monarchs clustered on the branches
    cl = ""
    for x, y in [(18, 86), (24, 92), (34, 90), (40, 96), (14, 118), (22, 124), (38, 120), (46, 126), (30, 130), (20, 146), (40, 148),
                 (164, 92), (172, 98), (182, 96), (188, 104), (162, 120), (170, 126), (186, 128), (178, 140), (160, 142)]:
        cl += mini_monarch(x, y, 0.7, (x * 37) % 40 - 20, closed=True)
    d.marks("orange", cl)
    sw = ""
    for x, y, s, r in [(70, 40, 0.8, -10), (90, 28, 0.6, 14), (124, 70, 0.7, -20), (60, 70, 0.6, 20), (136, 36, 0.55, 6),
                       (112, 52, 0.5, -24), (150, 84, 0.6, 10), (80, 92, 0.5, -6)]:
        sw += mini_monarch(x, y, s, r)
    d.marks("orange", sw)
    d.band("ground", hills(172, 5))
    at(d, 100, 140, 0.5, lambda: monarch(d), rot=-12, ox=100, oy=98)


# ================================================================ RHINOCEROS BEETLE
def beetle(d: Drawing):
    """A rhinoceros beetle side-on facing left, feet at y ~160."""
    # far legs
    d.limb("hero3", "M78 128 L66 142 L60 160", 4.5)
    d.limb("hero3", "M112 134 L108 148 L112 160", 4.5)
    d.limb("hero3", "M142 132 L162 146 L176 158", 4.5)
    d.shape("hero", "M96 84 C126 66 170 72 182 104 C186 120 176 134 154 136 L102 136 C92 122 90 100 96 84Z", spot=True)
    d.stroke("hero2", "M102 134 C130 132 160 130 178 116", 2, line=False)
    d.shape("hero", "M62 104 C64 88 78 78 98 80 C104 96 106 118 104 134 C88 136 70 130 64 120Z")
    d.shape("hero", "M84 82 C78 72 72 66 62 64 C72 62 84 66 94 80Z")
    d.shape("hero", "M42 114 C44 104 52 98 64 100 L70 126 C58 130 46 126 42 114Z")
    # the big horn, forked at the tip
    d.shape("hero", "M44 110 C34 94 30 72 36 50 C38 44 44 44 45 50 C42 70 46 90 60 102Z")
    d.shape("hero", "M36 52 C32 46 30 40 32 34 C36 36 38 42 40 48Z M40 50 C44 44 48 40 54 38 C52 44 48 48 44 54Z", shadow=False)
    # shine
    d.stroke("shine", "M110 84 C126 76 150 76 164 86", 3, line=False)
    d.stroke("shine", "M72 92 C76 86 82 84 88 84", 2.4, line=False)
    d.stroke("shine", "M38 70 C38 62 39 56 41 52", 1.8, line=False)
    d.marks("mark", circle(58, 108, 2.2))
    d.stroke("hero3", "M48 118 L38 124 M38 124 l-3 -3 M38 124 l-4 1", 1.6)
    # near legs
    d.limb("hero2", "M74 128 L56 140 L48 160", 5)
    d.limb("hero2", "M118 134 L102 148 L96 160", 5)
    d.limb("hero2", "M150 132 L170 144 L188 156", 5)
    d.stroke("hero3", claw(48, 160, 180, 2, 5, 40) + claw(96, 160, 180, 2, 5, 40) + claw(188, 156, 10, 2, 5, 40), 1.6)
    d.stroke("hero3", "M54 146 l-4 -1 M100 152 l-4 -1 M176 148 l2 -4", 1.4, line=False)


def beetle_portrait(d: Drawing):
    d.disc("glow", 128, 86, 50)
    d.limb("stem", "M-20 174 C40 166 140 164 220 172", 8)
    d.shape("mid", leaf(160, 168, 34, 10, -40), shadow=False)
    d.shape("mid", leaf(40, 170, 30, 9, -140), shadow=False)
    at(d, 100, 106, 1.08, lambda: beetle(d), ox=110, oy=110)


def beetle_log(d: Drawing):
    rays(d, ((30, 16), (120, 12)))
    jungle(d, [(-8, 30, 30, 70, 18), (208, 26, 150, 64, 16), (-6, 100, -10, 56, 15), (208, 100, 190, 56, 15)], "mid")
    # ferns
    for x, a in [(30, -100), (170, -80)]:
        d.stroke("near", f"M{x} 150 L{x + 50 * math.cos(math.radians(a)):.1f} {150 + 50 * math.sin(math.radians(a)):.1f}", 2.4, line=False)
        for i in range(6):
            t = 0.2 + i * 0.14
            px, py = x + 50 * t * math.cos(math.radians(a)), 150 + 50 * t * math.sin(math.radians(a))
            for k in (-1, 1):
                d.shape("near", leaf(px, py, 16 - 10 * t, 3.4, a + 70 * k), shadow=False, line=False)
    d.shape("log", "M-30 150 C20 142 160 140 230 146 V180 C160 176 40 178 -30 184Z")
    d.shape("moss", "M-30 150 C20 142 160 140 230 146 V150 C200 148 180 156 160 150 C130 146 110 154 90 148 C60 146 40 156 -30 156Z", shadow=False)
    d.stroke("log2", "M10 166 C50 162 100 164 140 162 M60 174 C100 170 160 172 200 170", 1.8, line=False)
    d.shape("log2", ellipse(196, 164, 8, 16), shadow=False)
    d.band("deep", hills(192, 4, 20), line=False)
    at(d, 102, 146, 0.68, lambda: beetle(d), ox=112, oy=160)


# ================================================================ LEAFCUTTER ANTS
def ant(d: Drawing, leaf_role="leafg", carry=True):
    """A leafcutter ant side-on facing left, feet at y ~150, holding a leaf piece aloft."""
    if carry:
        d.shape(leaf_role, "M46 108 C34 80 40 48 66 34 C92 22 126 30 132 54 C134 64 128 72 120 76 C100 82 78 94 54 112Z", spot=True)
        d.stroke("leafv", "M50 106 C70 80 96 54 124 46 M76 76 L70 52 M96 60 L100 40 M70 84 L92 82", 1.6, line=False)
    # far legs
    for p in ("M86 114 L80 128 L72 150", "M94 116 L106 130 L104 150", "M100 116 L126 128 L140 150"):
        d.limb("hero3", p, 3.2)
    d.shape("hero", ellipse(138, 106, 17, 13), extra='transform="rotate(-14 138 106)"')
    d.shape("hero", circle(110, 112, 4.5) + circle(119, 110, 5), shadow=False)
    d.shape("hero", "M74 102 C82 94 98 96 104 104 C106 112 98 118 88 118 C80 118 74 112 74 102Z")
    d.shape("hero", "M80 98 L80 90 L86 97Z M96 98 L100 92 L101 101Z", shadow=False)
    d.shape("hero", "M42 104 C42 92 52 86 64 88 C74 90 80 100 78 110 C76 120 66 124 56 122 C48 120 42 114 42 104Z")
    d.shape("hero2", "M50 92 C56 88 66 88 72 92 C64 92 56 94 50 98Z", shadow=False, line=False)
    d.shape("hero3", "M44 108 L34 104 L36 114Z", shadow=False)
    d.stroke("hero3", "M58 90 L56 74 L42 70 M64 90 L66 76 L54 66", 1.8)
    d.marks("mark", circle(52, 102, 2.4))
    if d.paper:
        d.marks("light", circle(51.4, 101.2, 0.8))
    for p in ("M82 114 L72 128 L62 150", "M90 116 L100 130 L94 150", "M98 116 L118 128 L130 150"):
        d.limb("hero", p, 3.4)


def ant_portrait(d: Drawing):
    d.disc("glow", 160, 112, 22)
    d.band("far", hills(150, 8), line=False)
    d.band("ground", "M-30 160 Q100 152 230 160")
    d.marks("near", circle(40, 172, 2) + circle(150, 176, 2.4) + circle(176, 168, 1.6) + circle(96, 180, 1.8))
    at(d, 102, 106, 1.2, lambda: ant(d), ox=90, oy=100)


def ants_trail(d: Drawing):
    rays(d, ((50, 18),))
    jungle(d, [(-8, 30, 30, 70, 18), (208, 26, 150, 64, 16), (-6, 92, -10, 50, 13), (208, 100, 190, 50, 13)], "mid")
    d.shape("branchb", "M-30 138 C30 120 120 104 230 76 L230 92 C120 120 40 138 -30 154Z")
    d.stroke("bark", "M10 140 C40 132 70 126 100 120 M120 108 C150 100 180 92 210 86", 1.6, line=False)
    roles = ["leafg", "leafa", "leafg", "leafb", "leafa"]
    for i, t in enumerate([0.14, 0.33, 0.52, 0.71, 0.9]):
        x = -10 + 230 * t
        y = 138 - (138 - 76) * t ** 1.05 - 6 * math.sin(math.pi * t)
        at(d, x, y + 2, 0.36, lambda r=roles[i]: ant(d, r), rot=-14, ox=90, oy=150)
    jungle(d, [(-10, 200, -50, 64, 17), (210, 210, -120, 64, 17)], "near")


# ================================================================ colours
CHAM_C = {"hero": "#5AB34A", "hero2": "#D6E86A", "hero3": "#2F7A3A", "mark": "#1C3320", "light": "#FFFFFF",
          "branch": "#7A5232", "tongue": "#F07C9A", "bug": "#9A7B48"}
GECKO_C = {"hero": "#6CC93F", "pad": "#B8EE7A", "pop": "#E2483A", "eye": "#F2C14E", "mark": "#1B2A18", "light": "#FFFFFF",
           "leafc": "#2E6E45", "leafv": "#4E9A60"}
GECKO_L = {**GECKO_C, "wall": "#F4E8D2", "sill": "#D8C4A0", "lamp": "#FFD36E", "dark": "#3B2E28", "moth": "#B9A27E",
           "moth2": "#8E7A5C", "leafg": "#3F8F4A", "bloom": "#D9358A"}
GIG_C = {"hero": "#5FAE45", "hero2": "#93CF5C", "crest": "#B8D86A", "band": "#3D7F34", "plate": "#E3EFC8", "eye": "#E39B3A",
         "mark": "#1E3420", "light": "#FFFFFF"}
GIG_T = {**GIG_C, "sea": "#3FB8C4", "rock": "#A88E66", "stone": "#CDB68A", "stone2": "#E6D6B0", "crest": "#9ACB4A", "dark": "#4A3A2C",
         "trunk": "#8A6A48", "palm": "#4E9A4A"}
DEVIL_C = {"hero": "#DDA24A", "hero2": "#A84A2A", "hero3": "#9C6A30", "light": "#F6E3B4", "spike": "#7E3A1E", "mark": "#2A1A10",
           "eye": "#E8C25A", "red": "#C65A30", "red2": "#A9452A"}
DEVIL_U = {**DEVIL_C, "uluru": "#CF6A3A", "uluru2": "#A94E2A", "red": "#A9452A", "red2": "#8E3A22", "spin": "#A9A65A"}
TREEFROG = {"hero": "#5CBF3A", "eye": "#E52B2B", "blue": "#2E6CD1", "bar": "#F4D35E", "feet": "#F48A2A", "belly": "#F3F0C9",
            "mark": "#141414", "light": "#FFFFFF", "leafc": "#2D7A45", "leafv": "#4F9C5A", "stem": "#3E6B3A"}
AXO = {"hero": "#F6B1C2", "hero2": "#FBD6DF", "gill": "#E0507A", "gill2": "#EE87A3", "blush": "#F08AA6", "mark": "#3A1F2A",
       "light": "#FFFFFF", "weed": "#4E9A5A", "pebble": "#B9A68A"}
AXO_C = {**AXO, "roof": "#F2C94C", "sign": "#E34A6F", "hull": "#2E86C1", "pop": "#F28F3B", "dark": "#5A3A2A"}
MANTIS_C = {"hero": "#7BC043", "hero2": "#A9D86E", "hero3": "#4C8A2C", "eye": "#E6F2A8", "mark": "#1E2A14", "stem": "#5E7A3A",
            "petal": "#F2A7C0", "flowerc": "#E9B83A"}
MORPHO_C = {"blue": "#2F7FE8", "blue2": "#7CC8FF", "edge": "#141A33", "light": "#FFFFFF"}
MONARCH_C = {"orange": "#F28A1E", "orange2": "#F9B54C", "edge": "#1B1512", "light": "#FFFFFF"}
MONARCH_F = {**MONARCH_C, "fir": "#2F5A44", "fir2": "#3E6E52", "trunk": "#4A3426"}
BEETLE_C = {"hero": "#4A2A1C", "hero2": "#6E3F28", "hero3": "#2A1810", "shine": "#C8957A", "mark": "#120A06", "stem": "#6B4A32"}
BEETLE_L = {**BEETLE_C, "log": "#7A5636", "log2": "#5A3E26", "moss": "#7DAA4A"}
ANT_C = {"hero": "#B04A22", "hero2": "#D97A44", "hero3": "#7A3016", "mark": "#1E0E08", "light": "#FFFFFF",
         "leafg": "#5DB94A", "leafa": "#8ACB4E", "leafb": "#3E9A48", "leafv": "#3A8A3A", "branchb": "#C9A57A", "bark": "#A07E56"}

CONCEPTS = [
    Concept("chameleon-portrait", "animal-chameleon", "Chameleon", chameleon_portrait, ["meadow", "coastal", "blush", "dusk", "golden"], overrides=CHAM_C,
            checks=[("hero", "sky"), ("hero", "mid"), ("hero", "glow"), ("branch", "sky")],
            fixes={"mid": ["deep", "near", "far"], "glow": ["glow2", "light", "pop"], "sky": ["sky2"]}),
    Concept("chameleon-rainforest", "animal-chameleon", "Chameleon in the rainforest", chameleon_rainforest, ["meadow", "coastal", "blush", "dusk", "golden"], overrides=CHAM_C,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "near"), ("branch", "far")],
            fixes={"far": ["sky2", "mid", "deep"], "near": ["deep", "mid"]}),
    Concept("gecko-portrait", "animal-gecko", "Gecko", gecko_portrait, ["meadow", "coastal", "blush", "dusk", "golden"], overrides=GECKO_C,
            checks=[("leafc", "sky"), ("hero", "leafc")], fixes={"sky": ["sky2", "far", "light"]}),
    Concept("gecko-lamp", "animal-gecko", "Gecko by the lamp", gecko_lamp, overrides=GECKO_L,
            checks=[("hero", "wall"), ("wall", "sky"), ("glow", "sky")], fixes={"sky": ["sky2", "far", "mid"]}),
    Concept("iguana-green-portrait", "animal-green-iguana", "Green iguana", iguana_portrait, overrides=GIG_C,
            checks=[("hero", "sky"), ("crest", "sky"), ("hero", "mid"), ("hero2", "sky")],
            fixes={"sky": ["sky2", "far", "glow2"], "mid": ["deep", "near", "far"]}),
    Concept("iguana-green-tulum", "animal-green-iguana", "Iguana at Tulum", iguana_tulum, overrides=GIG_T,
            checks=[("hero", "stone2"), ("crest", "stone2"), ("sea", "sky"), ("stone", "sky")],
            fixes={"sky": ["sky2", "glow2"]}),
    Concept("thornydevil-portrait", "animal-thorny-devil", "Thorny devil", devil_portrait, overrides=DEVIL_C,
            checks=[("hero", "sky"), ("hero", "red"), ("hero", "glow")],
            fixes={"glow": ["light", "glow2", "far"], "sky": ["sky2", "far"]}),
    Concept("thornydevil-uluru", "animal-thorny-devil", "Thorny devil at Uluru", devil_uluru, overrides=DEVIL_U,
            checks=[("hero", "red"), ("uluru", "sky"), ("uluru", "glow")],
            fixes={"glow": ["light", "glow2"], "sky": ["sky2"]}),
    Concept("treefrog-portrait", "animal-red-eyed-tree-frog", "Red-eyed tree frog", treefrog_portrait, ["meadow", "coastal", "blush", "dusk", "golden"], overrides=TREEFROG,
            checks=[("hero", "sky"), ("hero", "mid"), ("eye", "hero")],
            fixes={"mid": ["deep", "near", "far"], "sky": ["sky2"]}),
    Concept("treefrog-night", "animal-red-eyed-tree-frog", "Tree frog at night", treefrog_night, ["meadow", "coastal", "blush", "dusk", "golden"], overrides=TREEFROG,
            checks=[("hero", "sky"), ("hero", "far"), ("leafc", "sky"), ("leafc", "far")],
            fixes={"far": ["deep", "mid", "near"], "sky": ["sky2"]}),
    Concept("axolotl-portrait", "animal-axolotl", "Axolotl", axolotl_portrait, overrides=AXO,
            checks=[("hero", "sky"), ("gill", "sky"), ("hero", "ground")],
            fixes={"sky": ["sky2", "far", "mid"], "ground": ["near", "deep"]}),
    Concept("axolotl-canal", "animal-axolotl", "Axolotl in Xochimilco", axolotl_canal, ["coastal", "meadow", "dusk", "blush"], AXO_C,
            checks=[("hero", "near"), ("hero", "mid"), ("gill", "mid"), ("hull", "mid")],
            fixes={"mid": ["far", "near", "deep"], "near": ["deep", "mid"]}),
    Concept("mantis-portrait", "animal-praying-mantis", "Praying mantis", mantis_portrait, overrides=MANTIS_C,
            checks=[("hero", "sky"), ("hero2", "sky")], fixes={"sky": ["sky2"]}),
    Concept("mantis-garden", "animal-praying-mantis", "Mantis in the garden", mantis_garden, overrides=MANTIS_C,
            checks=[("hero", "sky"), ("hero", "far"), ("petal", "far"), ("petal", "near")],
            fixes={"far": ["sky2", "mid"], "near": ["deep", "mid"]}),
    Concept("morpho-portrait", "animal-blue-morpho", "Blue morpho", morpho_portrait, ["meadow", "coastal", "blush", "dusk", "golden"], overrides=MORPHO_C,
            checks=[("blue", "sky"), ("edge", "sky"), ("blue", "mid")],
            fixes={"sky": ["sky2", "far", "light"], "mid": ["near", "far"]}),
    Concept("morpho-rainforest", "animal-blue-morpho", "Morpho in the rainforest", morpho_rainforest, ["meadow", "coastal", "blush", "dusk", "golden"], overrides=MORPHO_C,
            checks=[("blue", "far"), ("edge", "far"), ("blue", "mid"), ("edge", "near")],
            fixes={"far": ["sky2", "mid", "near"], "mid": ["near", "far"], "near": ["mid", "far"]}),
    Concept("monarch-portrait", "animal-monarch-butterfly", "Monarch butterfly", monarch_portrait, overrides=MONARCH_C,
            checks=[("orange", "glow"), ("edge", "glow"), ("glow", "sky")],
            fixes={"glow": ["sky2", "light", "far", "mid"]}),
    Concept("monarch-forest", "animal-monarch-butterfly", "Monarch sanctuary", monarch_forest, overrides=MONARCH_F,
            checks=[("orange", "fir"), ("orange", "sky"), ("fir", "sky"), ("orange", "far")],
            fixes={"far": ["sky2", "mid", "near"], "sky": ["sky2"]}),
    Concept("beetle-portrait", "animal-rhinoceros-beetle", "Rhinoceros beetle", beetle_portrait, overrides=BEETLE_C,
            checks=[("hero", "glow"), ("hero", "sky")], fixes={"sky": ["sky2", "far"], "glow": ["glow2", "light"]}),
    Concept("beetle-log", "animal-rhinoceros-beetle", "Beetle on a jungle log", beetle_log, ["meadow", "coastal", "blush", "dusk", "golden"], overrides=BEETLE_L,
            checks=[("hero", "mid"), ("hero", "sky"), ("hero", "log")],
            fixes={"mid": ["far", "near"], "sky": ["sky2", "far"]}),
    Concept("leafcutter-portrait", "animal-leafcutter-ants", "Leafcutter ant", ant_portrait, overrides=ANT_C,
            checks=[("hero", "sky"), ("leafg", "sky"), ("hero", "ground"), ("hero", "glow")],
            fixes={"glow": ["light", "glow2", "far"], "ground": ["far", "near"]}),
    Concept("leafcutter-trail", "animal-leafcutter-ants", "Leafcutter trail", ants_trail, ["meadow", "coastal", "blush", "dusk", "golden"], overrides=ANT_C,
            checks=[("hero", "branchb"), ("leafg", "mid"), ("leafg", "sky"), ("branchb", "sky")],
            fixes={"mid": ["deep", "far", "near"], "sky": ["sky2"]}),
]
