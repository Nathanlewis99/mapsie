"""Culture & sightseeing: temples, castles, museums, markets, festivals and city walks."""
from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group  # noqa: F401
import math


# ================================================================ private helpers
def poly(*pts, close=True) -> str:
    s = "M" + " L".join(f"{x:g} {y:g}" for x, y in pts)
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


def pagoda_roof(cx, y, w, h=7.0) -> str:
    """Upturned east-asian eave: tips at (cx±w, y-4)."""
    return (f"M{cx - w:g} {y - 5:g} Q{cx - w * .78:g} {y + 2:g} {cx - w * .58:g} {y + 2:g} H{cx + w * .58:g} "
            f"Q{cx + w * .78:g} {y + 2:g} {cx + w:g} {y - 5:g} Q{cx + w * .62:g} {y - 3:g} {cx + w * .44:g} {y - h:g} "
            f"H{cx - w * .44:g} Q{cx - w * .62:g} {y - 3:g} {cx - w:g} {y - 5:g}Z")


def person(x, feet, h=30.0) -> str:
    """Simple standing silhouette: head plus a rounded body, feet at y=feet."""
    r = h * .14
    hy = feet - h + r
    sw = h * .2
    top = hy + r + h * .05
    body = (f"M{x - sw:g} {feet:g} V{top + sw * .8:g} Q{x - sw:g} {top:g} {x:g} {top:g} "
            f"Q{x + sw:g} {top:g} {x + sw:g} {top + sw * .8:g} V{feet:g}Z")
    return body + " " + circle(x, hy, r)


def flag_string(d: Drawing, x0, y0, x1, y1, sag, n, roles, size=4.0, spot_every=2, start=1):
    """Bunting / prayer flags hanging on a sagging string."""
    cx, cy = (x0 + x1) / 2, max(y0, y1) + sag
    clip_open(d)
    d.stroke("dark", f"M{x0} {y0} Q{cx} {cy} {x1} {y1}", 1.3)
    for i in range(start, n + start):
        t = i / (n + 2 * start - 1)
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1
        d.shape(roles[i % len(roles)], f"M{x - size:.1f} {y:.1f} L{x + size:.1f} {y:.1f} L{x:.1f} {y + size * 2.1:.1f}Z",
                shadow=False, spot=(i % spot_every == 0))
    clip_close(d)


def sq_flags(d: Drawing, x0, y0, x1, y1, sag, n, roles, size=4.5):
    """Tibetan prayer flags: square cloths on a sagging string."""
    cx, cy = (x0 + x1) / 2, max(y0, y1) + sag
    clip_open(d)
    d.stroke("dark", f"M{x0} {y0} Q{cx} {cy} {x1} {y1}", 1.2)
    for i in range(1, n + 1):
        t = i / (n + 1)
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1
        d.shape(roles[i % len(roles)], rrect(x - size / 2, y, size, size * 1.25, .8), shadow=False, spot=i % 3 == 0)
    clip_close(d)


def clip_open(d: Drawing):
    """Clip what follows to the sticker circle (line style doesn't clip shapes by itself)."""
    d.raw('<g clip-path="url(#clip)">', '<g clip-path="url(#clip)">')


def clip_close(d: Drawing):
    d.raw("</g>", "</g>")


def blossom(d: Drawing, pts, role="blossom", hi="light"):
    for x, y, r in pts:
        d.shape(role, circle(x, y, r))
    for x, y, r in pts[::2]:
        d.shape(hi, circle(x - r * .35, y - r * .35, r * .28), shadow=False, line=False)


def stars(d: Drawing, pts, role="light"):
    for x, y, r in pts:
        d.marks(role, f"M{x} {y - r} L{x + r * .3} {y - r * .3} L{x + r} {y} L{x + r * .3} {y + r * .3} "
                      f"L{x} {y + r} L{x - r * .3} {y + r * .3} L{x - r} {y} L{x - r * .3} {y - r * .3}Z")


def birds(d: Drawing, pts, role="dark"):
    s = " ".join(f"M{x} {y} q{3 * k} {-3 * k} {6 * k} 0 q{3 * k} {-3 * k} {6 * k} 0" for x, y, k in pts)
    d.stroke(role, s, 1.7)


# ================================================================ TEMPLE VISIT
def temple_pagoda(d: Drawing):
    d.disc("glow", 150, 56, 20)
    d.band("far", hills(150, 12, 10))
    cx = 116
    roofs = [(150, 46), (126, 40), (103, 34), (81, 29), (60, 24)]
    walls = [(170, 28)] + [(roofs[i][0], roofs[i][1] * .62) for i in range(4)]
    d.stroke("dark", f"M{cx} 58 V22", 2.4)
    for i, (y, w) in enumerate(roofs):
        top = roofs[i + 1][0] if i < 4 else y - 14
        wy = y - 6
        bw = w * .6
        d.shape("pop", f"M{cx - bw / 2} {top - 2} H{cx + bw / 2} V{wy + 1} H{cx - bw / 2}Z" if i else rrect(cx - 17, y - 2, 34, 22, 1),
                spot=False)
        if i == 0:
            d.shape("dark", arch(cx - 5, y + 4, 10, 16), shadow=False)
        else:
            d.marks("dark", rrect(cx - 3, top + 4, 6, wy - top - 6, 1.5))
    for i, (y, w) in reversed(list(enumerate(roofs))):
        d.shape("dark", pagoda_roof(cx, y, w))
    for y in (30, 36, 42):
        d.shape("hero2", ellipse(cx, y, 4.5, 1.6), shadow=False, spot=True)
    d.shape("hero2", circle(cx, 22, 2.6), shadow=False)
    # cherry tree
    d.limb("dark", "M52 172 C54 150 48 128 46 112 M50 142 C60 130 68 122 76 116 M47 124 C38 116 30 112 24 108", 5)
    blossom(d, [(30, 100, 13), (48, 92, 16), (68, 104, 14), (40, 114, 11), (78, 116, 9), (58, 80, 10)])
    for x, y in [(90, 136), (84, 152), (98, 160), (70, 140), (24, 130)]:
        d.marks("blossom", ellipse(x, y, 2.4, 1.5))
    d.band("ground", hills(172, 4))
    d.shape("near", rrect(cx - 38, 167, 76, 6, 2))
    d.band("near", hills(186, 3, 20), line=False)


def temple_stupa(d: Drawing):
    d.band("far", "M-30 122 L14 92 L40 106 L74 66 L102 96 L130 70 L166 102 L190 84 L230 108")
    for snow in ["M74 66 L84 79 L78 77 L73 82 L67 76 L63 79Z", "M130 70 L141 83 L135 81 L129 87 L123 80 L119 83Z",
                 "M190 84 L197 92 L192 91 L188 95 L184 90Z"]:
        d.shape("light", snow, shadow=False)
    d.band("mid", hills(140, 8))
    cx = 100
    sq_flags(d, cx, 40, 8, 120, 6, 8, ["hero", "light", "pop", "near", "hero2"])
    sq_flags(d, cx, 40, 192, 120, 6, 8, ["hero2", "near", "pop", "light", "hero"])
    d.shape("light", rrect(34, 156, 132, 12, 3))
    d.shape("light", rrect(44, 146, 112, 12, 3))
    d.shape("light", "M50 148 C50 112 74 96 100 96 C126 96 150 112 150 148Z")
    d.shape("gold", rrect(84, 82, 32, 16, 2))
    d.marks("dark", "M88 89 Q92 85 96 89 Q92 91 88 89Z M104 89 Q108 85 112 89 Q108 91 104 89Z")
    d.stroke("dark", "M100 91 q-2 3 0 4", 1.4)
    d.shape("gold", "M90 82 L100 48 L110 82Z", spot=True)
    d.stroke("dark", "M93 74 H107 M95 67 H105 M97 60 H103", 1.2, line=False)
    d.shape("gold", "M92 50 Q100 42 108 50Z")
    d.stroke("gold", "M100 44 V36", 2.4)
    d.band("ground", hills(176, 4))
    d.band("near", hills(188, 3, 30), line=False)


def temple_torii(d: Drawing):
    d.disc("glow", 100, 104, 30)
    birds(d, [(30, 62, 1), (44, 54, .8), (156, 60, .9)])
    d.band("far", "M-30 120 Q20 102 50 112 Q80 96 120 108 Q160 98 230 116")
    d.band("mid", waves(128, 3, 24))
    if d.paper:
        d.raw(f'<path d="M64 140 H76 V176 H64Z M124 140 H136 V176 H124Z" fill="{d.c["hero"]}" opacity=".3"/>')
    d.shape("hero", rrect(64, 62, 12, 82, 2))
    d.shape("hero", rrect(124, 62, 12, 82, 2))
    d.shape("hero", rrect(48, 74, 104, 9, 1.5))
    d.shape("hero", rrect(95, 56, 10, 20, 1), shadow=False)
    d.shape("hero", "M40 52 Q100 62 160 52 L157 60 Q100 69 43 60Z")
    d.shape("dark", "M36 40 Q100 53 164 40 L160 51 Q100 62 40 51Z", spot=True)
    d.shape("dark", rrect(62, 136, 16, 8, 1.5))
    d.shape("dark", rrect(122, 136, 16, 8, 1.5))
    d.band("near", waves(150, 3, 28))
    d.stroke("light", "M32 140 h14 M156 138 h12 M88 162 h24", 2)
    d.band("deep", waves(172, 3, 32), line=False)


# ================================================================ CASTLE TOUR
def castle_hilltop(d: Drawing):
    d.shape("light", cloud(16, 60, 1.1))
    d.shape("light", cloud(150, 44, .9))
    d.band("far", hills(140, 14, -10))
    # keep and towers
    d.shape("stone", battlement(86, 54, 28, 70, 3, 5))
    d.shape("stone", battlement(42, 76, 26, 78, 3, 5))
    d.shape("stone", battlement(132, 76, 26, 78, 3, 5))
    d.shape("stone", battlement(62, 100, 76, 54, 5, 5))
    d.stroke("dark", "M100 54 V34", 1.8)
    d.shape("pop", "M100 34 L116 39 L100 44Z", shadow=False, spot=True)
    d.stroke("dark", "M55 76 V62 M145 76 V62", 1.6)
    d.shape("hero", "M55 62 L66 65.5 L55 69Z", shadow=False, spot=True)
    d.shape("hero", "M145 62 L156 65.5 L145 69Z", shadow=False, spot=True)
    d.shape("dark", arch(88, 124, 24, 30), shadow=False)
    for x, y in [(51, 92), (141, 92), (51, 116), (141, 116), (96, 70), (75, 112), (121, 112)]:
        d.marks("dark", arch(x, y, 8, 12))
    d.shape("hero", "M74 128 H84 V146 L79 142 L74 146Z", shadow=False, spot=True)
    d.shape("hero", "M116 128 H126 V146 L121 142 L116 146Z", shadow=False, spot=True)
    d.band("mid", "M-30 166 Q30 150 70 154 Q100 156 130 154 Q170 150 230 164")
    d.shape("ground", "M92 154 H108 Q104 170 118 192 H90 Q96 170 92 154Z", shadow=False, line=False)
    d.band("near", hills(182, 6, 30), line=False)


def castle_fairytale(d: Drawing):
    d.disc("glow", 58, 58, 18)
    d.band("far", "M-30 128 L30 84 L60 104 L96 62 L132 100 L160 78 L230 122")
    d.shape("light", "M96 62 L106 74 L100 72 L95 77 L89 71 L85 74Z", shadow=False)
    d.band("mid", hills(150, 10, 10))

    def turret(x, top, w, h, roof_h):
        d.shape("stone", rrect(x - w / 2, top, w, h, 1))
        d.shape("hero", f"M{x - w / 2 - 3} {top + 2} L{x} {top - roof_h} L{x + w / 2 + 3} {top + 2}Z", spot=True)
        d.stroke("dark", f"M{x} {top - roof_h} v-8", 1.4)
        d.shape("pop", f"M{x} {top - roof_h - 8} l7 2.2 l-7 2.2Z", shadow=False)
        d.marks("dark", arch(x - 2.5, top + 8, 5, 9))
    d.shape("stone", rrect(58, 108, 84, 50, 1))
    d.shape("hero", "M54 110 L66 92 H134 L146 110Z")
    turret(100, 64, 20, 94, 30)
    turret(64, 96, 14, 62, 22)
    turret(136, 96, 14, 62, 22)
    turret(118, 84, 12, 30, 18)
    for x in (72, 82, 118, 128):
        d.marks("dark", arch(x - 2.5, 122, 5, 9))
    d.shape("dark", arch(93, 136, 14, 22), shadow=False)
    # pines
    for x, y, s in [(30, 170, 1.0), (44, 176, .8), (166, 172, 1.0), (180, 178, .8)]:
        d.shape("deep", f"M{x} {y - 40 * s} L{x + 12 * s} {y - 14 * s} L{x + 6 * s} {y - 14 * s} L{x + 15 * s} {y} L{x - 15 * s} {y} "
                        f"L{x - 6 * s} {y - 14 * s} L{x - 12 * s} {y - 14 * s}Z")
    d.band("near", hills(170, 5, 20))
    d.band("deep", hills(186, 3), line=False)


def castle_drawbridge(d: Drawing):
    d.shape("light", cloud(150, 30, .8))
    d.shape("stone", battlement(56, 40, 88, 110, 5, 6))
    for x in (20, 140):
        d.shape("stone", battlement(x, 24, 40, 126, 3, 7))
        d.marks("dark", arch(x + 16, 48, 8, 14))
        d.stroke("stone2", f"M{x} 70 H{x + 40} M{x} 100 H{x + 40}", 1.4, line=False)
        d.shape("pop", f"M{x + 12} 76 H{x + 28} V92 L{x + 20} 87 L{x + 12} 92Z", shadow=False, spot=True)
    d.stroke("stone2", "M56 64 H144 M56 88 H140", 1.4, line=False)
    d.shape("dark", arch(74, 76, 52, 66), shadow=False)
    # portcullis
    d.stroke("hero2", "M82 84 V114 M91 79 V114 M100 77 V114 M109 79 V114 M118 84 V114 M77 92 H123 M76 104 H124", 2.2)
    d.stroke("hero2", "M82 114 v4 M91 114 v4 M100 114 v4 M109 114 v4 M118 114 v4", 2.2)
    d.band("mid", waves(150, 3, 22))
    # lowered drawbridge
    d.shape("wood", "M74 142 H126 L140 178 H60Z", spot=True)
    d.stroke("wood2", "M70 152 H130 M66 162 H134 M63 171 H137", 1.6, line=False)
    d.stroke("dark", "M76 92 L64 146 M124 92 L136 146", 1.8)
    d.band("near", waves(172, 3, 26), line=False)
    d.shape("wood", "M60 172 H140 L141 178 H59Z", shadow=False, line=False)


# ================================================================ MUSEUM
def museum_facade(d: Drawing):
    d.disc("glow", 100, 100, 72)
    d.shape("light", "M30 66 L100 32 L170 66Z")
    d.shape("mid", "M50 62 L100 39 L150 62Z", shadow=False)
    d.shape("light", rrect(28, 64, 144, 12, 1))
    d.shape("mid", rrect(36, 76, 128, 66, 0), shadow=False)
    for x in range(40, 170, 22):
        d.shape("light", rrect(x, 78, 12, 64, 1))
        d.shape("light", rrect(x - 2.5, 76, 17, 4, 1), shadow=False)
        d.stroke("far", f"M{x + 4} 84 V136 M{x + 8} 84 V136", 1, line=False)
    d.shape("pop", rrect(73, 92, 10, 30, 1), shadow=False, spot=True)
    d.shape("pop", rrect(117, 92, 10, 30, 1), shadow=False, spot=True)
    d.marks("dark", arch(93, 112, 14, 30))
    d.shape("light", rrect(24, 140, 152, 9, 1))
    d.shape("light", rrect(16, 148, 168, 9, 1))
    d.shape("light", rrect(8, 156, 184, 9, 1))
    d.band("near", hills(168, 3))
    d.marks("glow2", circle(100, 52, 4))


def museum_dino(d: Drawing):
    d.band("far", "M-30 -10 H230", shadow=False, line=False)
    d.shape("mid", arch(44, 28, 112, 140), shadow=False, line=False)
    d.band("near", "M-30 162 H230")
    d.shape("dark", rrect(40, 156, 116, 10, 2))
    bone = "light"
    # tail, spine, neck
    d.limb(bone, "M92 98 C70 102 50 110 18 130", 7)
    d.limb(bone, "M92 98 C110 92 122 84 132 70", 8)
    for i, (x, y) in enumerate([(98, 95), (106, 92), (114, 87), (122, 81)]):
        d.limb(bone, f"M{x} {y} Q{x + 6} {y + 18} {x - 2} {y + 30 - i * 3}", 3.2)
    d.shape(bone, "M80 92 C88 86 100 90 100 100 C98 108 84 108 80 100Z")
    d.limb(bone, "M90 102 L100 126 L90 150 L98 158", 7)
    d.limb(bone, "M82 102 L80 128 L70 150 L78 158", 6)
    d.limb(bone, "M128 98 L136 104 L140 101", 3)
    skull = ("M126 62 C132 48 156 44 172 52 C178 55 180 60 178 66 L176 70 L162 72 L176 76 L172 84 "
             "C160 88 146 86 138 80 C130 76 124 70 126 62Z")
    d.shape(bone, skull)
    d.marks("dark", circle(145, 61, 4.5))
    d.marks("dark", ellipse(160, 63, 4.6, 3.2))
    d.stroke("dark", "M150 74 l2 3 l2 -3 l2 3 l2 -3 l2 3 l2 -3 l2 3 l2 -3 l2 3", 1.2)


def museum_amphora(d: Drawing):
    d.band("far", "M-30 -10 H230", shadow=False, line=False)
    d.raw('<path d="M80 -10 H120 L168 170 H32Z" fill="#fff" opacity=".22"/>', "")
    d.band("mid", "M-30 168 H230")
    d.shape("light", rrect(62, 150, 76, 24, 2))
    d.shape("light", rrect(56, 146, 88, 7, 2))
    body = ("M88 40 H112 L110 52 C132 62 142 82 140 102 C138 120 126 132 112 138 L114 146 H86 L88 138 "
            "C74 132 62 120 60 102 C58 82 68 62 90 52Z")
    d.limb("hero", "M90 54 C76 52 74 66 82 70", 5)
    d.limb("hero", "M110 54 C124 52 126 66 118 70", 5)
    d.shape("hero", body)
    d.shape("mark", "M62 86 C78 82 122 82 138 86 L140 106 C122 110 78 110 60 106Z", shadow=False, spot=True)
    d.stroke("hero", "M66 100 V92 H74 V100 H82 V92 H90 V100 H98 V92 H106 V100 H114 V92 H122 V100 H130 V92 H136", 2, line=False)
    d.stroke("mark", "M72 120 Q100 128 128 120 M80 62 Q100 58 120 62", 2.2)
    d.shape("mark", rrect(86, 36, 28, 6, 2), shadow=False)


# ================================================================ ART GALLERY
def gallery_frame(d: Drawing):
    d.band("far", "M-30 -10 H230", shadow=False, line=False)
    d.stroke("dark", "M100 26 L66 46 M100 26 L134 46", 1.4)
    d.marks("dark", circle(100, 26, 2.5))
    d.shape("gold", rrect(36, 44, 128, 108, 4))
    d.shape("gold2", rrect(44, 52, 112, 92, 2), shadow=False)
    # painting
    d.shape("sky", rrect(50, 58, 100, 80, 1), shadow=False)
    d.disc("glow", 122, 84, 13)
    d.shape("mid", "M50 116 Q76 96 110 108 Q130 114 150 104 V138 H50Z", shadow=False)
    d.shape("near", "M50 130 Q74 118 100 126 Q126 132 150 122 V138 H50Z", shadow=False)
    d.shape("dark", "M68 128 V120 L61 120 L68 104 L75 120 L68 120", shadow=False, line=False)
    d.stroke("gold2", "M50 58 H150 V138 H50Z", 1.5, line=False)
    for x, y in [(36, 44), (164, 44), (36, 152), (164, 152)]:
        d.shape("gold", circle(x, y, 7), shadow=False, spot=True)
    d.band("mid", "M-30 178 H230")


def gallery_palette(d: Drawing):
    d.disc("glow", 100, 100, 64)
    pal = ("M60 54 C88 36 140 40 160 70 C176 94 170 132 140 146 C120 156 104 142 104 130 C104 120 92 116 82 124 "
           "C70 134 46 128 40 108 C34 88 40 68 60 54Z")
    d.limb("dark", "M44 160 L136 70", 6)
    d.shape("light", "M131 75 L148 56 C152 52 158 56 154 61 L140 80Z", shadow=False)
    d.shape("wood", pal)
    d.marks("glow", ellipse(64, 104, 9, 7))
    d.shape("sky", ellipse(64, 104, 7.5, 5.5), shadow=False, line=False)
    for x, y, r, role in [(74, 64, 9, "pop"), (102, 54, 9, "hero2"), (130, 62, 9, "hero"), (150, 88, 9, "mid"),
                          (142, 118, 8.5, "light")]:
        d.shape(role, circle(x, y, r), spot=role == "pop")
    d.limb("hero", "M58 172 L118 90", 5)
    d.shape("light", "M114 92 L120 84 L126 88 L122 96Z", shadow=False)
    d.shape("pop", "M120 84 C124 72 134 66 140 64 C138 72 132 82 126 88Z", spot=True)


def gallery_wall(d: Drawing):
    d.band("far", "M-30 -10 H230", shadow=False, line=False)
    d.band("mid", "M-30 156 H230")
    d.stroke("dark", "M80 22 L68 34 M120 22 L132 34", 1.6, line=False)
    d.shape("gold", rrect(44, 36, 92, 70, 2))
    d.shape("sky2", rrect(50, 42, 80, 58, 1), shadow=False)
    d.shape("hero", "M50 100 L74 66 L92 86 L106 70 L130 100Z", shadow=False)
    d.shape("pop", circle(110, 58, 8), shadow=False, spot=True)
    d.shape("dark", rrect(144, 40, 34, 44, 2))
    d.shape("hero2", rrect(149, 45, 24, 34, 1), shadow=False)
    d.shape("near", circle(161, 62, 8), shadow=False)
    d.shape("dark", rrect(22, 112, 40, 28, 2))
    d.shape("glow", rrect(26, 116, 32, 20, 1), shadow=False)
    d.shape("hero2", "M26 136 Q42 120 58 136Z", shadow=False)
    d.shape("dark", rrect(70, 140, 70, 8, 2))
    d.limb("dark", "M76 148 V164 M134 148 V164", 4)
    d.shape("dark", person(152, 176, 60))



# ================================================================ ANCIENT RUINS
def column(d: Drawing, x, top, base, w=14, broken=False, role="stone"):
    if broken:
        d.shape(role, f"M{x} {base} V{top + 4} L{x + w * .3} {top} L{x + w * .5} {top + 5} L{x + w * .8} {top + 1} L{x + w} {top + 6} V{base}Z")
    else:
        d.shape(role, rrect(x, top + 6, w, base - top - 6, 1))
        d.shape(role, rrect(x - 3, top, w + 6, 6, 1.5), shadow=False)
    d.stroke("stone2", f"M{x + w * .33} {top + 10} V{base - 3} M{x + w * .66} {top + 10} V{base - 3}", 1.2, line=False)


def ruins_columns(d: Drawing):
    d.disc("glow", 104, 112, 46)
    birds(d, [(146, 50, 1), (160, 42, .8)])
    d.band("far", hills(150, 8))
    d.shape("dark", "M170 152 C162 120 166 92 172 76 C178 92 182 120 174 152Z")
    d.shape("dark", "M30 152 C24 128 27 108 32 96 C37 108 40 128 34 152Z")
    d.shape("stone", rrect(28, 148, 144, 8, 1))
    d.shape("stone", rrect(20, 155, 160, 8, 1))
    d.shape("stone", rrect(40, 62, 82, 12, 1))
    d.shape("stone", "M40 62 L56 50 L80 56 L74 62Z", shadow=False)
    for x in (44, 70, 96):
        column(d, x, 74, 148)
    column(d, 122, 90, 148, broken=True)
    column(d, 148, 116, 148, broken=True)
    d.band("ground", hills(170, 4))
    d.shape("stone", rrect(122, 160, 30, 12, 6))
    d.shape("stone2", ellipse(152, 166, 3.5, 6), shadow=False)
    d.band("near", hills(186, 3, 20), line=False)


def ruins_colosseum(d: Drawing):
    d.disc("glow", 150, 56, 18)
    d.shape("light", cloud(20, 52, 1))
    # inner far ring, seen through the broken side
    d.shape("stone2", "M108 154 V82 Q140 80 176 92 V154Z")
    for x in (118, 136, 154):
        d.marks("deep", arch(x, 96, 9, 16))
        d.marks("deep", arch(x, 124, 9, 18))
    outer = ("M22 156 V58 Q60 50 100 52 L104 58 L102 66 L112 70 L110 84 L124 88 L122 106 L140 110 L138 124 "
             "L160 126 L162 156Z")
    d.shape("stone", outer)
    for row, (y, h) in enumerate([(62, 16), (90, 20), (122, 24)]):
        for i in range(8):
            x = 28 + i * 17
            lim = {0: 98, 1: 112, 2: 156}[row]
            if x + 11 < lim:
                d.marks("deep", arch(x, y, 11, h))
    d.stroke("stone2", "M22 84 Q60 80 104 84 M22 116 Q70 112 120 112 M22 148 Q80 146 160 150", 2.2, line=False)
    d.band("mid", hills(162, 4))
    d.band("near", hills(178, 3, 20), line=False)


def ruins_llama(d: Drawing):
    d.shape("light", cloud(150, 26, .8))
    d.band("far", "M-30 104 L10 84 L40 96 L70 72 L96 92 L112 84 L230 104")
    d.shape("near", "M112 150 C118 112 128 72 138 52 Q146 38 154 52 C162 72 170 104 184 150Z")
    d.shape("deep", "M146 44 Q150 44 154 52 C162 72 168 100 178 132 C164 110 154 80 146 44Z", shadow=False, line=False)
    clip_open(d)
    for i in range(4):
        y = 112 + i * 11
        x1 = 132 + i * 12
        d.shape("mid", f"M-30 {y} H{x1} L{x1 + 8} 200 H-30Z")
    clip_close(d)
    for x, y in [(30, 106), (54, 106), (80, 106), (104, 106), (118, 117)]:
        d.shape("stone", f"M{x} {y + 6} V{y - 2} L{x + 7} {y - 8} L{x + 14} {y - 2} V{y + 6}Z")
        d.marks("dark", rrect(x + 5, y - 1, 4, 7, 1))
    d.band("ground", hills(170, 4, 10))
    llama = ("M34 140 C34 132 44 130 54 132 L68 132 L70 110 C70 104 73 100 77 99 L77 91 L80 98 L82 90 L84 99 "
             "C88 101 93 105 93 109 C93 113 89 114 85 114 L82 114 L80 138 C82 148 78 154 76 156 L76 178 L70 178 "
             "L69 158 L64 158 L63 178 L57 178 L56 158 L46 158 L45 178 L39 178 L38 157 C34 154 31 148 34 140Z")
    group(d, "translate(-14 -6) scale(1.15)", lambda: (
        d.shape("llama", llama),
        d.shape("pop", "M46 131 H68 V146 H46Z", shadow=False, spot=True),
        d.stroke("hero2", "M46 136 H68 M46 141 H68", 1.6, line=False),
        d.marks("dark", circle(84, 106, 1.6)),
        d.marks("dark", ellipse(91.5, 109, 1.2, 1))))


# ================================================================ PYRAMIDS
def camel(d: Drawing, tx, ty, s=1.0, role="dark", rider=False):
    path = ("M0 6 C1 3 5 2 7 4 L9 7 C10 10 12 12 14 12 C16 4 20 0 24 0 C30 0 33 6 34 12 C36 14 36 18 34 20 "
            "L33 31 L31 31 L30 21 L28 21 L27 31 L25 31 L24 20 L17 20 L16 31 L14 31 L13 21 L11 21 L10 31 L8 31 "
            "L8 19 C6 16 6 12 5 9 L2 9 C0 9 -1 8 0 6Z")
    def draw():
        d.shape(role, path)
        if rider:
            d.shape(role, "M20 2 C20 -6 22 -9 24 -9 C26 -9 28 -6 28 2Z " + circle(24, -12, 3.2), shadow=False)
    group(d, f"translate({tx} {ty}) scale({s})", draw)


def pyramid(d: Drawing, x, base, w, h, lit="sand", shade="sand2"):
    d.shape(lit, f"M{x - w / 2} {base} L{x} {base - h} L{x + w / 2} {base}Z")
    d.shape(shade, f"M{x} {base - h} L{x + w / 2} {base} L{x + w * .14} {base}Z", shadow=False)


def pyramids_camels(d: Drawing):
    d.disc("glow", 64, 82, 24)
    pyramid(d, 128, 146, 120, 88)
    pyramid(d, 56, 146, 76, 52)
    pyramid(d, 176, 146, 46, 30)
    d.band("ground", "M-30 150 Q50 140 110 146 T230 144")
    d.band("mid", "M-30 168 Q40 156 100 162 T230 160")
    camel(d, 48, 132, 1.0, rider=True)
    camel(d, 92, 136, .9)
    d.stroke("dark", "M58 141 Q76 150 93 140", 1.2)
    d.band("near", hills(184, 4, 30), line=False)


def pyramids_sphinx(d: Drawing):
    d.disc("glow", 150, 60, 18)
    pyramid(d, 136, 140, 120, 84)
    d.band("ground", "M-30 146 Q60 138 120 142 T230 140")
    sphinx = ("M22 164 V154 Q22 148 30 148 L60 148 L60 126 L56 112 L50 112 L48 102 L44 98 L48 92 L48 82 "
              "Q52 66 66 64 Q82 64 86 78 L90 104 Q100 112 116 112 Q150 112 162 126 L168 164Z")
    d.shape("sand", sphinx)
    d.shape("sand2", "M66 64 Q82 64 86 78 L90 104 L78 106 L72 84 Q66 74 52 76 Q56 66 66 64Z", shadow=False, spot=True)
    d.stroke("sand", "M80 78 L84 100 M74 70 L82 72", 1.6, line=False)
    d.marks("dark", ellipse(55, 88, 2.4, 1.4))
    d.stroke("sand2", "M36 156 H60 M100 150 Q120 140 140 150 M60 130 Q66 132 70 128", 1.8)
    d.band("mid", "M-30 170 Q60 160 120 166 T230 162")
    d.band("near", hills(184, 4), line=False)


def pyramids_maya(d: Drawing):
    d.disc("glow", 100, 70, 40)
    d.band("far", hills(140, 10))
    for i in range(6):
        w = 136 - i * 18
        d.shape("stone", rrect(100 - w / 2, 148 - (i + 1) * 13, w, 14, 1))
    d.shape("stone2", "M90 70 H110 L118 148 H82Z", shadow=False)
    d.stroke("stone", "M86 136 H114 M87 126 H113 M88 116 H112 M89 106 H111 M90 96 H110 M91 86 H109 M91.5 78 H108.5", 1.6, line=False)
    d.shape("stone", rrect(80, 52, 40, 20, 1))
    d.shape("stone2", rrect(78, 48, 44, 6, 1), shadow=False)
    d.marks("dark", rrect(95, 58, 10, 14, 1))
    d.marks("dark", rrect(84, 60, 6, 12, 1))
    d.marks("dark", rrect(110, 60, 6, 12, 1))
    # jungle
    clip_open(d)
    for x, y, r in [(12, 150, 22), (36, 158, 18), (172, 150, 22), (194, 140, 18), (150, 162, 14)]:
        d.shape("deep", circle(x, y, r))
    d.limb("deep", "M30 160 C26 132 22 110 26 90", 4)
    d.shape("deep", "M26 90 C14 86 6 92 2 100 C12 94 20 94 26 90Z M26 90 C38 82 48 86 54 94 C44 90 34 90 26 90Z "
                    "M26 90 C20 78 12 74 4 76 C14 80 20 84 26 90Z M26 90 C34 76 44 72 52 74 C42 80 34 84 26 90Z")
    clip_close(d)
    d.band("near", hills(170, 6, 10))
    d.band("deep", hills(186, 3), line=False)


# ================================================================ OLD TOWN STROLL
def oldtown_alley(d: Drawing):
    clip_open(d)
    d.disc("glow", 100, 40, 18)
    d.shape("light", "M70 160 V64 L100 50 L130 64 V160Z")
    d.shape("hero", arch(88, 100, 24, 40), shadow=False, spot=True)
    d.shape("hero2", "M-30 0 H74 V176 H-30Z")
    d.shape("near", "M126 0 H230 V176 H126Z")
    for x, y in [(22, 40), (46, 40), (22, 96), (46, 96)]:
        d.shape("dark", rrect(x, y, 14, 20, 1), shadow=False)
        d.shape("hero", rrect(x - 7, y, 6, 20, 1), shadow=False)
        d.shape("hero", rrect(x + 15, y, 6, 20, 1), shadow=False)
    for x, y in [(144, 46), (164, 46), (144, 104), (164, 104)]:
        d.shape("dark", rrect(x, y, 13, 20, 1), shadow=False)
        d.shape("light", rrect(x - 2, y + 20, 17, 3, 1), shadow=False)
    d.shape("pop", "M40 134 H62 L58 146 H44Z", spot=True)
    d.shape("deep", "M42 134 C38 124 46 118 51 126 C54 116 64 120 60 134Z")
    # steps
    for i in range(5):
        d.shape("ground", rrect(70 - i * 6, 140 + i * 9, 60 + i * 12, 9, 1))
    # laundry line
    d.stroke("dark", "M74 66 Q100 82 126 66", 1.2)
    d.shape("light", "M84 70 L92 72 L96 76 L98 90 L82 90 L82 74Z", spot=False)
    d.shape("pop", "M100 75 H110 L111 92 H99Z", spot=True)
    d.shape("hero2", "M112 73 L120 70 L121 86 L117 86 L116 79 L115 86 L111 86Z")
    clip_close(d)


def oldtown_canal(d: Drawing):
    d.shape("light", cloud(150, 30, .9))
    houses = [(20, 32, 60, "hero", "step"), (52, 34, 46, "pop", "bell"), (86, 30, 54, "hero2", "step"), (116, 34, 44, "mid", "bell"),
              (150, 30, 60, "near", "step")]
    for x, w, top, role, kind in houses:
        cx = x + w / 2
        if kind == "step":
            g = (f"M{x} 150 V{top + 22} H{x + 5} V{top + 14} H{x + 10} V{top + 6} H{cx - 5} V{top} H{cx + 5} V{top + 6} "
                 f"H{x + w - 10} V{top + 14} H{x + w - 5} V{top + 22} H{x + w} V150Z")
        else:
            g = (f"M{x} 150 V{top + 22} Q{x + 8} {top + 20} {x + 8} {top + 12} Q{cx - 6} {top + 10} {cx - 4} {top} H{cx + 4} "
                 f"Q{cx + 6} {top + 10} {x + w - 8} {top + 12} Q{x + w - 8} {top + 20} {x + w} {top + 22} V150Z")
        d.shape(role, g)
        for row in range(3):
            y = top + 28 + row * 22
            for col in range(2):
                wx = x + w * (.22 + col * .36)
                d.marks("light", rrect(wx, y, w * .2, 12, 1.5))
        d.marks("light", circle(cx, top + 15, 2.6))
    d.band("mid", "M-30 150 H230")
    if d.paper:
        d.raw(f'<g opacity=".3">' + "".join(
            f'<rect x="{x + 4}" y="{156 + i * 7}" width="{w - 8}" height="3" rx="1.5" fill="{d.c[role]}"/>'
            for x, w, top, role, kind in houses for i in range(3)) + '</g>')
    d.stroke("light", "M30 160 h12 M120 168 h16 M70 174 h10", 2)
    d.shape("dark", "M10 146 H190 V152 H10Z", shadow=False)


def oldtown_clocktower(d: Drawing):
    birds(d, [(140, 40, 1), (152, 32, .8)])
    d.shape("light", cloud(16, 70, 1))
    d.shape("light", rrect(84, 52, 32, 112, 1))
    d.shape("hero", "M80 54 L100 18 L120 54Z", spot=True)
    d.shape("hero", rrect(80, 52, 40, 6, 1), shadow=False)
    d.shape("light", circle(100, 76, 12))
    d.stroke("dark", circle(100, 76, 12), 1.8)
    d.stroke("dark", "M100 76 V68 M100 76 L106 79", 2.2)
    d.marks("dark", arch(95, 98, 10, 18))
    d.marks("dark", arch(95, 126, 10, 18))
    for x, w, top, role in [(14, 40, 112, "hero2"), (50, 34, 124, "pop"), (116, 36, 118, "hero2"), (150, 40, 108, "mid")]:
        d.shape(role, rrect(x, top, w, 170 - top, 0))
        d.shape("near", f"M{x - 4} {top + 2} L{x + w / 2} {top - 16} L{x + w + 4} {top + 2}Z")
        d.marks("light", rrect(x + w * .2, top + 12, w * .22, 12, 1))
        d.marks("light", rrect(x + w * .58, top + 12, w * .22, 12, 1))
    d.band("ground", "M-30 160 H230")
    d.stroke("ground2", "M10 168 h16 M34 168 h16 M58 168 h16 M82 168 h16 M106 168 h16 M130 168 h16 M154 168 h16 M178 168 h16 "
                       "M22 176 h16 M46 176 h16 M70 176 h16 M94 176 h16 M118 176 h16 M142 176 h16 M166 176 h16", 2, line=False)


# ================================================================ WALKING TOUR
def walk_guide(d: Drawing):
    d.disc("glow", 46, 56, 16)
    # domed cathedral and bell tower
    d.shape("mid", "M92 140 V96 H104 V84 Q128 46 152 84 V96 H164 V140Z")
    d.shape("mid", rrect(124, 40, 8, 16, 2), shadow=False)
    d.shape("mid", "M168 140 V64 L176 50 L184 64 V140Z")
    d.marks("glow2", arch(122, 104, 12, 22))
    d.marks("glow2", rrect(173, 72, 6, 10, 2))
    d.band("ground", "M-30 160 H230")
    d.limb("dark", "M66 164 L62 44", 2.6)
    d.shape("pop", "M62 44 L90 50 L63 60Z", spot=True)
    d.limb("hero", "M54 116 L62 98", 6)
    d.shape("hero", person(46, 174, 70), spot=True)
    for x, h, role in [(104, 50, "near"), (130, 56, "hero2"), (156, 48, "deep")]:
        d.shape(role, person(x, 176, h))
    d.band("near", hills(184, 3), line=False)


def walk_map(d: Drawing):
    d.disc("glow", 100, 100, 62)
    panels = [("M28 62 L74 50 L74 150 L28 162Z", "light"), ("M74 50 L126 62 L126 162 L74 150Z", "sky2"), ("M126 62 L172 50 L172 150 L126 162Z", "light")]
    for p, r in panels:
        d.shape(r, p)
    d.shape("mid", "M86 76 Q100 70 112 80 Q116 92 104 96 Q88 96 86 76Z", shadow=False)
    d.stroke("hero", "M28 120 Q60 108 74 118 Q100 130 126 116 Q150 102 172 108", 5)
    d.stroke("far", "M44 60 L56 156 M28 92 L74 84 M74 104 L126 112 M140 58 L150 154 M126 86 L172 78 M126 138 L172 132", 2.2)
    d.stroke("pop", "M44 142 Q56 128 70 132 Q92 140 104 120 Q114 104 136 98 Q148 94 150 82", 2.6)
    d.raw("", "")
    d.shape("pop", "M150 84 C140 72 138 62 142 56 C146 48 158 48 162 56 C166 62 164 72 154 84 Q152 88 150 84Z" if False else
            "M152 86 C144 74 140 66 140 60 C140 52 146 46 152 46 C158 46 164 52 164 60 C164 66 160 74 152 86Z", spot=True)
    d.marks("light", circle(152, 59, 4.5))
    d.marks("pop", circle(44, 142, 3.5))


def walk_signpost(d: Drawing):
    d.disc("glow", 52, 64, 20)
    d.band("far", "M-30 136 H10 V112 L22 100 L34 112 V124 H54 V96 Q62 84 70 96 V130 H120 V104 H128 V92 H136 V104 H146 V120 H170 V100 L180 90 L190 100 V128 H230")
    d.band("mid", "M-30 156 Q100 146 230 156")
    d.shape("dark", rrect(96, 44, 9, 124, 2))
    d.shape("hero", "M104 52 H156 L166 61 L156 70 H104Z", spot=True)
    d.shape("pop", "M97 78 H48 L38 87 L48 96 H97Z")
    d.shape("hero2", "M104 104 H148 L158 113 L148 122 H104Z", spot=True)
    d.stroke("light", "M114 61 H146 M58 87 H88 M114 113 H140", 2.4, line=False)
    d.shape("dark", circle(100.5, 42, 5))
    d.band("near", hills(176, 4, 20))
    d.marks("deep", ellipse(70, 172, 3, 4.5))
    d.marks("deep", ellipse(80, 166, 3, 4.5))
    d.marks("deep", ellipse(128, 176, 3, 4.5))
    d.marks("deep", ellipse(138, 170, 3, 4.5))


# ================================================================ ROOFTOP VIEWS
def bulbs(d: Drawing, x0, y0, x1, y1, sag, n, role="glow2", r=2.6):
    cx, cy = (x0 + x1) / 2, max(y0, y1) + sag
    clip_open(d)
    d.stroke("dark", f"M{x0} {y0} Q{cx} {cy} {x1} {y1}", 1.2)
    for i in range(1, n + 1):
        t = i / (n + 1)
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1
        d.disc(role, round(x, 1), round(y + r + 1, 1), r, shadow=False)
    clip_close(d)


def rooftop_skyline(d: Drawing):
    d.disc("glow", 70, 92, 26)
    d.band("far", "M-30 120 H24 V92 H40 V76 H52 V100 H70 V84 L78 70 L86 84 V112 H104 V60 H112 V48 H118 V60 H126 V108 H140 V88 H160 V104 H176 V80 H192 V116 H230")
    d.band("mid", "M-30 132 H14 V112 H34 V124 H58 V106 H80 V128 H118 V114 H136 V122 H164 V100 H180 V126 H230")
    bulbs(d, 6, 38, 196, 38, 22, 9)
    d.shape("dark", rrect(16, 136, 168, 8, 2))
    d.stroke("dark", "M28 144 V176 M52 144 V176 M76 144 V176 M100 144 V176 M124 144 V176 M148 144 V176 M172 144 V176", 3)
    d.band("near", "M-30 172 H230")
    # cocktail on the ledge
    group(d, "translate(142 136) scale(1.5) translate(-142 -136)", lambda: (
        d.shape("light", "M128 104 H156 L144 118 V132 H150 V136 H134 V132 H140 V118Z"),
        d.shape("pop", "M131 107 H153 L142 117Z", shadow=False, spot=True),
        d.stroke("dark", "M140 112 L134 94", 1.4),
        d.shape("hero2", circle(154, 104, 6)),
        d.shape("light", circle(154, 104, 3.2), shadow=False, line=False)))


def rooftop_santorini(d: Drawing):
    d.disc("glow", 150, 104, 20)
    d.band("far", "M-30 112 H230")
    d.stroke("light", "M136 120 h28 M142 128 h16", 2, line=False)
    d.shape("near", "M-30 200 V150 Q30 140 80 152 Q130 160 170 176 L190 200Z", line=False)
    for x, y, w, h in [(10, 120, 40, 40), (44, 110, 46, 46), (86, 126, 34, 30), (116, 140, 40, 26), (24, 150, 52, 30), (74, 150, 48, 34)]:
        d.shape("light", rrect(x, y, w, h, 2))
    for x, y in [(20, 132), (56, 124), (96, 136), (126, 150), (36, 162), (86, 162), (104, 166)]:
        d.shape("dome", arch(x, y, 7, 11), shadow=False)
    d.shape("light", rrect(52, 92, 30, 20, 1))
    d.shape("dome", "M50 94 C50 72 84 72 84 94Z", spot=True)
    d.shape("light", rrect(64, 64, 6, 12, 1), shadow=False)
    d.stroke("dark", "M67 64 V56 M63.5 59.5 H70.5", 1.8)
    d.shape("light", "M96 112 V86 H122 V112Z")
    d.shape("dome", arch(102, 90, 14, 16), shadow=False)
    d.marks("hero2", circle(109, 100, 3))
    d.shape("pop", circle(10, 114, 9))
    d.shape("pop", circle(24, 108, 7))
    d.shape("pop", circle(118, 138, 7))


def rooftop_cat(d: Drawing):
    d.disc("glow", 60, 58, 22)
    d.disc("sky", 70, 51, 19, shadow=False, line=False)
    stars(d, [(112, 34, 3), (146, 50, 2.4), (170, 82, 2.4), (24, 96, 2), (96, 64, 2)], "glow2")
    d.band("far", "M-30 128 H8 L20 108 H50 L60 128 H150 V112 H158 V128 H166 L178 110 H230")
    clip_open(d)
    d.shape("near", "M-30 210 V146 H12 L32 118 H168 L188 146 H230 V210Z")
    d.shape("deep", "M-30 210 V146 H230 V210Z", shadow=False, line=False)
    for x in (44, 70, 116, 142):
        d.shape("near", f"M{x} 146 V128 L{x + 8} 120 L{x + 16} 128 V146Z")
        d.marks("glow2", rrect(x + 4, 129, 8, 14, 1))
    d.stroke("deep", "M22 132 H178", 1.4, line=False)
    clip_close(d)
    for x in (52, 132):
        d.shape("near", rrect(x, 98, 12, 22, 1))
        d.shape("deep", rrect(x - 2, 95, 16, 5, 1), shadow=False)
        d.shape("hero", rrect(x + 2, 88, 4, 8, 1.5), shadow=False)
        d.shape("hero", rrect(x + 7, 90, 4, 6, 1.5), shadow=False)
    cat = ("M80 118 C77 102 82 88 90 83 C85 78 85 68 89 63 L88 51 L96 57 Q100 56 104 57 L112 51 L111 63 "
           "C115 68 115 78 110 83 C118 88 124 102 120 118Z")
    d.limb("dark", "M118 115 C136 118 140 102 132 92", 5)
    d.shape("dark", cat, spot=True)


# ================================================================ LOCAL MARKET
def market_stall(d: Drawing):
    d.disc("glow", 150, 46, 16)
    d.band("far", hills(140, 6))
    d.limb("dark", "M42 70 L42 162 M158 70 L158 162", 4)
    d.shape("hero", "M34 52 L44 40 H156 L166 52Z")
    stripes = []
    for i in range(6):
        x = 34 + i * 22
        role = "hero" if i % 2 == 0 else "light"
        d.shape(role, f"M{x} 52 H{x + 22} V72 A11 8 0 0 1 {x} 72Z", shadow=i == 0, spot=role == "hero")
    d.shape("wood", rrect(30, 126, 140, 10, 2))
    d.shape("wood", rrect(36, 136, 128, 30, 2))
    d.stroke("wood2", "M36 151 H164", 1.4, line=False)
    # crates of fruit
    for cx, role in [(62, "pop"), (100, "hero2"), (138, "fruit")]:
        for x, y in [(-10, 0), (0, 0), (10, 0), (-5, -8), (5, -8), (0, -15)]:
            d.shape(role, circle(cx + x, 118 + y, 5.5), shadow=y == 0, spot=role == "pop")
        d.shape("wood2", rrect(cx - 18, 118, 36, 12, 2))
    d.shape("leaf", "M138 101 C140 94 146 92 150 93 C148 98 144 101 138 101Z", shadow=False)
    d.band("ground", hills(170, 3))


def market_basket(d: Drawing):
    d.disc("glow", 100, 100, 62)
    d.limb("wood2", "M52 104 C52 50 148 50 148 104", 6)
    d.shape("bread", "M70 110 L118 48 C122 42 132 46 128 54 L86 116Z")
    d.stroke("bread2", "M106 70 l8 4 M98 80 l8 4 M90 90 l8 4 M114 60 l8 4", 2.2)
    d.shape("leaf", "M118 104 C110 84 116 66 128 58 C140 70 140 90 132 104Z")
    d.stroke("leaf2", "M126 102 C126 86 128 74 128 62", 1.6)
    d.shape("leaf", "M134 104 C140 88 152 80 164 82 C162 94 152 104 140 106Z")
    d.shape("pop", circle(74, 102, 11), spot=True)
    d.shape("pop", circle(96, 104, 10), spot=True)
    d.stroke("leaf2", "M70 92 l4 2 l4 -2 M92 95 l4 2 l4 -2", 1.6)
    d.shape("hero2", ellipse(116, 106, 10, 8))
    d.shape("wood", "M44 104 H156 L146 158 Q144 166 136 166 H64 Q56 166 54 158Z")
    d.shape("wood2", rrect(40, 100, 120, 10, 4))
    d.stroke("wood2", "M50 124 H150 M52 140 H148 M56 154 H144 M70 110 V164 M90 110 V164 M110 110 V164 M130 110 V164", 1.6, line=False)


def market_spices(d: Drawing):
    d.band("far", "M-30 -10 H230", shadow=False, line=False)
    d.shape("mid", "M40 120 V72 C40 44 70 30 100 22 C130 30 160 44 160 72 V120Z", shadow=False, line=False)
    d.shape("light", "M52 120 V76 C52 54 76 42 100 34 C124 42 148 54 148 76 V120Z", shadow=False)
    d.disc("glow", 100, 74, 18, shadow=False)
    heaps = [(44, 132, 26, "sp1"), (100, 128, 28, "sp2"), (156, 132, 26, "sp3"), (72, 156, 26, "sp4"), (128, 156, 26, "sp5")]
    for x, y, w, role in heaps:
        d.shape(role, f"M{x - w} {y} C{x - w * .6} {y - 8} {x - 8} {y - 34} {x} {y - 34} C{x + 8} {y - 34} {x + w * .6} {y - 8} {x + w} {y}Z",
                spot=role == "sp1")
        d.shape("sack", f"M{x - w - 4} {y - 4} Q{x} {y + 6} {x + w + 4} {y - 4} L{x + w} {y + 22} Q{x} {y + 28} {x - w} {y + 22}Z")
        d.stroke("sack2", f"M{x - w - 2} {y + 2} Q{x} {y + 10} {x + w + 2} {y + 2}", 1.6, line=False)
    d.limb("wood", "M112 104 L132 86", 4)
    d.shape("wood", ellipse(108, 108, 7, 4.5), extra='transform="rotate(-40 108 108)"')


# ================================================================ NIGHT MARKET
def lantern(d: Drawing, x, y, s=1.0, role="pop", band="hero2", string=True):
    if string:
        d.stroke("dark", f"M{x} {y - 22 * s} V{y - 12 * s}", 1.3)
    d.shape(band, rrect(x - 5 * s, y - 13 * s, 10 * s, 4 * s, 1), shadow=False)
    d.shape(role, ellipse(x, y, 11 * s, 10 * s), spot=True)
    d.stroke(band, f"M{x - 5 * s} {y - 8 * s} Q{x - 9 * s} {y} {x - 5 * s} {y + 8 * s} M{x + 5 * s} {y - 8 * s} Q{x + 9 * s} {y} {x + 5 * s} {y + 8 * s}", 1.2, line=False)
    d.shape(band, rrect(x - 5 * s, y + 9 * s, 10 * s, 4 * s, 1), shadow=False)
    d.stroke(band, f"M{x} {y + 13 * s} V{y + 22 * s}", 1.6)


def nightmarket_stalls(d: Drawing):
    stars(d, [(30, 60, 2.4), (168, 54, 2.4), (100, 30, 2)], "glow2")
    d.band("far", "M-30 110 H20 V80 H44 V96 H62 V70 H90 V100 H112 V76 H140 V92 H160 V66 H186 V104 H230")
    for x, y in [(26, 86), (34, 86), (70, 78), (80, 78), (118, 84), (128, 84), (166, 74), (174, 74)]:
        d.marks("glow2", rrect(x, y, 4, 5, .6))
    # two stalls
    for x0, w, role in [(18, 76, "hero"), (106, 76, "pop")]:
        d.limb("dark", f"M{x0 + 4} 100 L{x0 + 4} 160 M{x0 + w - 4} 100 L{x0 + w - 4} 160", 3.4)
        d.shape(role, f"M{x0 - 4} 102 L{x0 + 6} 86 H{x0 + w - 6} L{x0 + w + 4} 102Z", spot=role == "pop")
        for i in range(4):
            sx = x0 - 4 + i * (w + 8) / 4
            d.shape("light" if i % 2 else role, f"M{sx} 102 H{sx + (w + 8) / 4} V108 A{(w + 8) / 8} 5 0 0 1 {sx} 108Z", shadow=False)
        d.shape("wood", rrect(x0, 130, w, 30, 2))
        d.shape("glow2", rrect(x0 + 6, 116, w - 12, 14, 2), shadow=False)
        d.stroke("dark", f"M{x0 + 10} 124 h10 M{x0 + 28} 122 h18 M{x0 + 52} 124 h12", 2, line=False)
    bulbs(d, -6, 52, 206, 52, 18, 9)
    lantern(d, 56, 128 - 60, .8)
    lantern(d, 144, 128 - 60, .8, role="hero2", band="pop")
    d.band("mid", "M-30 160 H230")
    d.band("deep", hills(182, 3), line=False)


def nightmarket_skewers(d: Drawing):
    for x, y, r in [(36, 62, 8), (164, 54, 10), (140, 30, 5), (56, 34, 6), (22, 100, 5), (178, 92, 6)]:
        d.disc("glow2", x, y, r, shadow=False, line=False)
    d.stroke("light", "M66 74 C58 62 74 54 66 42 M100 66 C92 52 108 46 100 32 M134 74 C126 62 142 54 134 42", 2.8)
    for x, colours in [(66, ["meat", "pop", "meat", "leaf"]), (100, ["meat", "leaf", "meat", "pop"]), (134, ["pop", "meat", "leaf", "meat"])]:
        d.limb("wood", f"M{x - 18} 146 L{x + 8} 76", 2.6)
        for j, role in enumerate(colours):
            t = .18 + j * .19
            cx, cy = x - 18 + 26 * t, 146 - 70 * t
            d.shape(role, rrect(cx - 9, cy - 6.5, 18, 13, 5), spot=role == "pop")
    d.shape("hero", "M24 134 H176 L166 168 H34Z")
    d.shape("pop", "M30 134 Q40 122 48 134 Q58 118 68 134 Q78 120 88 134 Q100 114 112 134 Q122 120 132 134 Q142 118 152 134 Q160 124 170 134Z", spot=True)
    d.stroke("dark", "M30 138 H170", 2.6)
    d.stroke("dark", "M48 150 H152 M52 160 H148", 2, line=False)
    d.shape("hero", rrect(44, 166, 8, 14, 2))
    d.shape("hero", rrect(148, 166, 8, 14, 2))


def nightmarket_steamers(d: Drawing):
    stars(d, [(30, 70, 2.4), (170, 64, 2.4)], "glow2")
    lantern(d, 40, 44, 1.0)
    lantern(d, 160, 44, 1.0)
    d.stroke("dark", "M-10 22 Q100 40 210 22", 1.3)
    d.stroke("light", "M84 86 C76 74 92 68 84 56 M104 82 C96 68 112 62 104 48 M122 86 C114 74 130 68 122 56", 2.8)
    d.shape("wood", rrect(50, 92, 100, 16, 6))
    d.shape("wood", "M58 92 Q100 70 142 92Z")
    d.shape("wood2", rrect(94, 76, 12, 6, 3), shadow=False)
    for y in (108, 128, 148):
        d.shape("wood", rrect(46, y, 108, 22, 4))
        d.stroke("wood2", f"M50 {y + 7} H150 M50 {y + 14} H150", 1.4, line=False)
        d.shape("wood2", rrect(46, y, 108, 4, 2), shadow=False, spot=True)
    d.band("mid", "M-30 170 H230")


# ================================================================ FESTIVAL
def burst(d: Drawing, x, y, r, role, n=12, dots=True):
    s = ""
    for i in range(n):
        a = 2 * math.pi * i / n
        s += f"M{x + math.cos(a) * r * .35:.1f} {y + math.sin(a) * r * .35:.1f} L{x + math.cos(a) * r * .85:.1f} {y + math.sin(a) * r * .85:.1f} "
    d.stroke(role, s, 2.6)
    if dots:
        for i in range(n):
            a = 2 * math.pi * (i + .5) / n
            d.marks(role, circle(round(x + math.cos(a) * r, 1), round(y + math.sin(a) * r, 1), 1.8))


def festival_fireworks(d: Drawing):
    burst(d, 70, 62, 32, "pop", 14)
    burst(d, 136, 48, 24, "glow2", 12)
    burst(d, 150, 100, 18, "light", 10)
    burst(d, 40, 106, 14, "hero2", 8)
    d.stroke("glow2", "M70 140 Q66 110 70 96", 1.4)
    d.band("far", "M-30 150 H18 V124 H36 V112 L44 98 L52 112 V134 H70 V118 H94 V96 Q104 80 114 96 V130 H132 V108 H152 V126 H176 V116 H198 V148 H230")
    for x, y in [(24, 132), (40, 120), (76, 126), (84, 126), (100, 106), (138, 116), (144, 116), (182, 124)]:
        d.marks("glow2", rrect(x, y, 4, 5, .6))
    d.band("mid", waves(158, 3, 24))
    d.stroke("glow2", "M60 168 h20 M120 166 h14 M140 176 h10", 2)
    d.band("deep", waves(178, 3, 30), line=False)


def festival_tents(d: Drawing):
    d.disc("glow", 100, 52, 16)
    flag_string(d, -6, 34, 206, 34, 26, 12, ["pop", "hero2", "hero", "light"], 4.5)
    d.band("far", hills(132, 8))

    def tent(x, base, w, h, role):
        d.shape(role, f"M{x - w / 2} {base} L{x - w / 2 + 4} {base - h * .45} L{x} {base - h} L{x + w / 2 - 4} {base - h * .45} L{x + w / 2} {base}Z",
                spot=role == "pop")
        d.shape("light", f"M{x - w * .16} {base - h * .3} L{x} {base - h} L{x + w * .16} {base - h * .3} L{x + w * .14} {base} H{x - w * .14}Z", shadow=False)
        d.shape("dark", f"M{x - 7} {base} L{x} {base - 16} L{x + 7} {base}Z", shadow=False)
        d.stroke("dark", f"M{x} {base - h} V{base - h - 10}", 1.4)
        d.shape(role, f"M{x} {base - h - 10} L{x + 9} {base - h - 7} L{x} {base - h - 4}Z", shadow=False)
    tent(44, 150, 52, 54, "hero")
    tent(156, 150, 52, 54, "hero2")
    tent(100, 158, 70, 84, "pop")
    d.band("mid", hills(160, 4))
    d.band("near", hills(180, 3, 20), line=False)


def festival_dragon(d: Drawing):
    stars(d, [(40, 40, 2.4), (160, 36, 3), (120, 26, 2)], "glow2")
    d.disc("glow", 150, 64, 14)
    d.band("far", hills(150, 6))
    d.limb("dark", "M76 112 L74 160 M118 92 L118 160 M160 104 L162 160", 2.4)
    body = "M60 100 C80 70 100 70 118 92 C134 112 150 116 170 96 C180 86 190 88 196 96"
    d.limb("hero2", body, 26)
    d.limb("pop", body, 18, shadow=False, spot=True)
    for x, y in [(78, 80), (96, 74), (112, 84), (128, 102), (146, 108), (162, 102), (180, 90)]:
        d.marks("hero2", f"M{x - 4} {y + 2} Q{x} {y - 6} {x + 4} {y + 2}Z")
    d.shape("hero2", "M76 72 L82 60 L88 72 Z M98 66 L104 54 L110 70Z M136 100 L144 88 L150 104Z M160 94 L168 82 L172 96Z", shadow=False)
    head = ("M24 104 C22 88 34 78 48 78 L58 66 L60 80 C70 82 76 92 74 104 C72 116 62 122 50 122 L36 124 C28 122 24 116 24 104Z")
    d.shape("pop", head, spot=True)
    d.shape("hero2", "M24 108 C34 112 50 114 72 108 C70 116 62 122 50 122 L36 124 C28 122 24 116 24 108Z", shadow=False)
    d.shape("light", circle(48, 94, 7), shadow=False)
    d.marks("dark", circle(49, 94, 3.4))
    d.stroke("hero2", "M30 104 C18 104 12 112 14 122 M34 100 C20 94 12 98 8 104", 2.2)
    d.stroke("dark", "M28 112 h10", 2)
    d.band("mid", hills(166, 4))
    d.band("near", hills(182, 3, 20), line=False)


# ================================================================ CARNIVAL
def confetti(d: Drawing, pts):
    roles = ["pop", "hero2", "hero", "light"]
    for i, (x, y, a) in enumerate(pts):
        d.shape(roles[i % 4], rrect(x - 3, y - 1.5, 6, 3, 1), shadow=False, line=False, extra=f'transform="rotate({a} {x} {y})"')


def carnival_mask(d: Drawing):
    d.disc("glow", 100, 100, 62)
    confetti(d, [(30, 70, 30), (46, 150, -20), (160, 156, 50), (174, 116, -40), (40, 112, 70), (150, 40, 10), (62, 46, -30)])
    for ang, role in [(-50, "hero"), (-30, "pop"), (-10, "hero2"), (10, "hero")]:
        d.shape(role, ellipse(150, 52, 8, 30), extra=f'transform="rotate({ang} 150 82)"', spot=role == "pop")
    d.limb("wood", "M146 122 L172 176", 5)
    mask = ("M40 92 C52 78 78 80 100 92 C122 80 148 78 160 92 C166 110 154 128 136 130 C120 132 110 122 100 114 "
            "C90 122 80 132 64 130 C46 128 34 110 40 92Z")
    d.shape("gold", mask)
    d.shape("pop", "M40 92 C52 78 78 80 100 92 C122 80 148 78 160 92 C158 98 156 100 152 100 C140 92 118 90 100 100 "
                   "C82 90 60 92 48 100 C44 100 42 98 40 92Z", shadow=False, spot=True)
    d.marks("dark", "M60 106 Q74 94 90 106 Q74 114 60 106Z M110 106 Q126 94 140 106 Q126 114 110 106Z")
    d.stroke("pop", "M62 120 Q70 126 80 120 M120 120 Q130 126 138 120", 2)
    d.marks("pop", circle(100, 104, 3.5))
    d.marks("light", circle(150, 84, 3))


def carnival_carousel(d: Drawing):
    d.band("far", "M-30 -10 H230", shadow=False, line=False)
    clip_open(d)
    d.shape("hero", "M-10 -10 H210 V38 H-10Z")
    for i in range(8):
        x = 0 + i * 26
        d.shape("hero" if i % 2 else "light", f"M{x} 34 H{x + 26} V40 A13 9 0 0 1 {x} 40Z", shadow=False, spot=i % 2 == 1)
    clip_close(d)
    for x in range(14, 200, 26):
        d.marks("glow2", circle(x + 13, 26, 2.6))
    d.shape("gold", rrect(97, 40, 8, 150, 2), spot=True)
    d.stroke("gold2", "M97 60 l8 -6 M97 76 l8 -6 M97 150 l8 -6 M97 166 l8 -6 M97 182 l8 -6", 2.2, line=False)
    horse = ("M40 84 C44 72 56 62 66 62 L66 52 L73 61 C82 65 88 76 92 90 C106 93 126 93 140 93 C156 93 166 102 166 114 "
             "C166 122 162 126 156 128 L172 146 L166 152 L148 134 L140 133 L148 152 L141 156 L128 135 "
             "C116 137 106 137 96 133 L90 150 L94 160 L86 162 L80 148 L86 128 L82 124 L68 138 L62 132 L76 116 "
             "C73 109 72 102 72 96 L60 100 C54 102 50 101 48 98 L44 98 C40 96 38 90 40 84Z")
    d.limb("hero2", "M164 106 C178 110 184 124 178 138", 7)
    d.shape("horse", horse)
    d.shape("hero2", "M66 62 C80 62 92 76 96 92 L88 92 C84 80 76 70 66 66Z", shadow=False)
    d.shape("pop", "M110 92 H136 V104 Q123 110 110 104Z", shadow=False, spot=True)
    d.shape("hero2", rrect(106, 90, 34, 4, 2), shadow=False)
    d.stroke("pop", "M66 70 L54 90 M60 82 L86 90", 1.8)
    d.marks("dark", circle(56, 76, 2))
    d.band("mid", "M-30 178 H230")


def carnival_ferris(d: Drawing):
    d.disc("glow", 160, 50, 14)
    d.band("far", hills(150, 8, 20))
    cx, cy, r = 100, 90, 56
    d.limb("dark", f"M{cx} {cy} L68 166 M{cx} {cy} L132 166", 5)
    d.stroke("hero", circle(cx, cy, r), 5)
    d.stroke("hero", circle(cx, cy, r * .62), 2.2)
    sp = " ".join(f"M{cx} {cy} L{cx + r * math.cos(a):.1f} {cy + r * math.sin(a):.1f}" for a in [i * math.pi / 5 for i in range(10)])
    d.stroke("hero", sp, 1.6)
    roles = ["pop", "hero2", "light", "pop", "hero2"]
    for i in range(10):
        a = i * math.pi / 5 + math.pi / 10
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        d.stroke("dark", f"M{x:.1f} {y:.1f} V{y + 5:.1f}", 1.4)
        d.shape(roles[i % 5], f"M{x - 7:.1f} {y + 5:.1f} H{x + 7:.1f} L{x + 6:.1f} {y + 15:.1f} H{x - 6:.1f}Z", spot=roles[i % 5] == "pop")
    d.shape("hero2", circle(cx, cy, 7))
    d.band("mid", hills(168, 4))
    d.shape("pop", "M30 168 V150 L42 137 L54 150 V168Z")
    d.shape("light", "M36 168 V157 H48 V168Z", shadow=False)
    d.shape("hero", "M148 168 V152 L159 140 L170 152 V168Z")
    d.band("near", hills(184, 3), line=False)


# ================================================================ CONCERT
def notes(d: Drawing, pts, role="dark"):
    for x, y, k in pts:
        d.marks(role, ellipse(x, y, 4.2 * k, 3.2 * k))
        d.stroke(role, f"M{x + 3.8 * k:.1f} {y:.1f} V{y - 16 * k:.1f} q{4 * k:.1f} {3 * k:.1f} {7 * k:.1f} {6 * k:.1f}", 1.8)


def concert_guitar(d: Drawing):
    d.disc("glow", 100, 100, 60)
    notes(d, [(36, 66, 1.2), (160, 140, 1), (48, 140, .9), (164, 64, 1.1)])

    def guitar():
        d.shape("guitar", "M100 70 C116 70 124 80 124 92 C124 102 118 106 120 112 C130 118 134 128 134 140 C134 160 120 172 100 172 "
                          "C80 172 66 160 66 140 C66 128 70 118 80 112 C82 106 76 102 76 92 C76 80 84 70 100 70Z")
        d.shape("guitar2", "M100 76 C112 76 118 84 118 92 C118 100 112 106 114 112 C124 118 128 128 128 140 C128 156 116 166 100 166 "
                           "C84 166 72 156 72 140 C72 128 76 118 86 112 C88 106 82 100 82 92 C82 84 88 76 100 76Z", shadow=False, line=False)
        d.shape("dark", circle(100, 116, 10), shadow=False, spot=True)
        d.shape("neck", rrect(94, 12, 12, 100, 2))
        d.shape("dark", rrect(91, -4, 18, 20, 3))
        d.marks("light", "M89 0 h-4 v3 h4Z M89 7 h-4 v3 h4Z M111 0 h4 v3 h-4Z M111 7 h4 v3 h-4Z")
        d.shape("dark", rrect(88, 146, 24, 6, 2), shadow=False)
        d.stroke("light", "M97 16 V148 M100 16 V148 M103 16 V148", .8, line=False)
        d.stroke("dark", "M94 40 H106 M94 58 H106 M94 74 H106 M94 88 H106", .9, line=False)
    group(d, "rotate(32 100 100) translate(100 104) scale(.86) translate(-100 -92)", guitar)


def concert_stage(d: Drawing):
    if d.paper:
        d.raw(f'<g opacity=".28" fill="{d.c["glow2"]}"><path d="M40 30 L54 30 L104 150 L60 150Z"/><path d="M146 30 L160 30 L140 150 L96 150Z"/>'
              f'<path d="M96 30 L104 30 L124 150 L76 150Z"/></g>')
    d.shape("dark", rrect(26, 22, 148, 8, 1))
    d.stroke("dark", "M30 30 L34 22 L38 30 L42 22 L46 30 L50 22 L54 30 M146 30 L150 22 L154 30 L158 22 L162 30 L166 22 L170 30", 1.2, line=False)
    for x in (47, 100, 153):
        d.shape("hero", f"M{x - 6} 30 H{x + 6} L{x + 4} 40 H{x - 4}Z", shadow=False)
        d.marks("glow2", ellipse(x, 40, 4, 2))
    d.disc("glow", 100, 94, 30)
    d.shape("mid", rrect(20, 128, 160, 22, 2))
    d.limb("dark", "M108 96 L118 68", 5)
    d.shape("dark", person(100, 128, 60), spot=True)
    d.stroke("dark", "M86 128 L88 90", 2)
    d.shape("dark", rrect(85, 84, 7, 9, 3), extra='transform="rotate(10 88 88)"')
    # crowd
    for x, y, arm in [(14, 164, 1), (38, 158, 0), (60, 166, 1), (84, 160, 0), (108, 164, 1), (132, 158, 1), (156, 166, 0), (182, 160, 1)]:
        if arm:
            d.limb("crowd", f"M{x + 6} {y + 4} L{x + 12} {y - 18}", 5, shadow=False)
        d.shape("crowd", circle(x, y, 9), shadow=False)
    d.band("crowd", "M-30 168 H230", line=False)


def concert_violin(d: Drawing):
    d.disc("glow", 100, 100, 60)
    notes(d, [(40, 62, 1.1), (166, 138, 1), (34, 128, .9)])

    def violin():
        d.shape("violin", "M100 84 C112 84 124 88 124 102 C124 110 116 114 116 120 C116 126 128 132 128 146 C128 164 114 174 100 174 "
                          "C86 174 72 164 72 146 C72 132 84 126 84 120 C84 114 76 110 76 102 C76 88 88 84 100 84Z")
        d.shape("dark", "M96 40 H104 L106 150 H94Z", spot=True)
        d.shape("violin2", rrect(95, 22, 10, 22, 3))
        d.shape("violin2", circle(100, 20, 6))
        d.marks("dark", circle(100, 20, 2.4))
        d.stroke("dark", "M84 120 q-4 8 0 16 M116 120 q4 8 0 16", 2)
        d.shape("light", rrect(90, 136, 20, 4, 1), shadow=False)
        d.shape("dark", "M94 154 H106 L104 170 H96Z", shadow=False)
        d.stroke("light", "M98 40 V156 M102 40 V156", .7, line=False)
    group(d, "rotate(-28 100 100) translate(100 100) scale(.9) translate(-100 -98)", violin)
    d.limb("wood", "M40 160 L166 54", 3)
    d.stroke("light", "M46 162 L170 58", 1.2, line=False)
    d.shape("dark", rrect(160, 50, 10, 8, 2), extra='transform="rotate(-40 165 54)"')


# ================================================================ PHOTOGRAPHY WALK
def photo_camera(d: Drawing):
    d.disc("glow", 100, 100, 62)
    d.stroke("dark", "M30 84 Q20 140 60 150 M170 84 Q180 140 140 150", 2.6, line=False)
    d.shape("light", rrect(48, 60, 104, 26, 6))
    d.shape("dark", rrect(58, 52, 22, 10, 2))
    d.shape("pop", rrect(126, 54, 14, 8, 2), spot=True)
    d.shape("hero", rrect(36, 74, 128, 72, 10))
    d.shape("dark", rrect(36, 92, 128, 36, 0), shadow=False)
    d.shape("light", rrect(46, 80, 22, 10, 2), shadow=False)
    d.shape("sky2", rrect(48, 82, 18, 6, 1.5), shadow=False, line=False)
    d.shape("light", circle(100, 110, 30))
    d.shape("dark", circle(100, 110, 23))
    d.shape("hero", circle(100, 110, 16), shadow=False, spot=True)
    d.shape("dark", circle(100, 110, 10), shadow=False)
    d.marks("light", circle(94, 104, 3.5))
    d.marks("light", circle(106, 116, 1.6))
    d.shape("glow2", circle(146, 84, 4), shadow=False)


def photo_polaroids(d: Drawing):
    d.disc("glow", 100, 100, 62)
    clip_open(d)
    d.stroke("dark", "M-10 52 Q100 76 210 52", 1.6)
    clip_close(d)

    def snap(x, y, ang, scene):
        def draw():
            d.shape("light", rrect(x - 22, y, 44, 52, 2))
            d.shape("sky2", rrect(x - 18, y + 4, 36, 34, 1), shadow=False)
            scene(x, y + 4)
            d.shape("wood", rrect(x - 3, y - 6, 6, 14, 1.5), spot=True)
        group(d, f"rotate({ang} {x} {y})", draw)

    def mountains(x, y):
        d.marks("glow", circle(x + 8, y + 10, 5))
        d.shape("mid", f"M{x - 18} {y + 34} L{x - 6} {y + 14} L{x + 2} {y + 24} L{x + 8} {y + 18} L{x + 18} {y + 34}Z", shadow=False)
        d.shape("light", f"M{x - 6} {y + 14} L{x - 2} {y + 20} L{x - 10} {y + 20}Z", shadow=False, line=False)

    def tower(x, y):
        d.shape("hero", f"M{x - 2} {y + 6} L{x + 2} {y + 6} L{x + 10} {y + 34} H{x + 4} Q{x} {y + 24} {x - 4} {y + 34} H{x - 10}Z", shadow=False)
        d.stroke("light", f"M{x - 5} {y + 22} H{x + 5}", 1.4, line=False)

    def sea(x, y):
        d.marks("glow", circle(x - 6, y + 14, 6))
        d.shape("near", f"M{x - 18} {y + 22} Q{x - 9} {y + 18} {x} {y + 22} T{x + 18} {y + 22} V{y + 34} H{x - 18}Z", shadow=False)
        d.shape("hero2", f"M{x + 4} {y + 20} L{x + 10} {y + 8} L{x + 10} {y + 20}Z", shadow=False)
    snap(52, 58, -8, mountains)
    snap(100, 66, 4, tower)
    snap(148, 58, 10, sea)
    d.marks("dark", "M98 160 m0 0" if False else "M0 0")


def photo_tripod(d: Drawing):
    d.disc("glow", 140, 82, 22)
    d.band("far", "M-30 128 L20 96 L50 112 L90 70 L124 108 L150 92 L230 120")
    d.shape("light", "M90 70 L100 81 L94 79 L89 84 L83 78 L79 81Z", shadow=False)
    d.band("mid", hills(146, 8, 10))
    d.band("near", hills(168, 6, -20))
    d.limb("dark", "M74 106 L44 174 M74 106 L76 178 M74 106 L104 172", 3.4)
    d.shape("dark", rrect(66, 100, 16, 8, 2))
    d.shape("hero", rrect(50, 76, 46, 28, 5), spot=True)
    d.shape("hero", rrect(56, 70, 14, 8, 2))
    d.shape("dark", rrect(94, 80, 16, 20, 3))
    d.shape("light", rrect(108, 82, 5, 16, 1.5))
    d.shape("light", rrect(56, 82, 14, 8, 1.5), shadow=False)
    d.marks("pop", circle(84, 72, 2.6))
    d.band("deep", hills(186, 3), line=False)


# ================================================================ LANTERN FESTIVAL
def sky_lantern(d: Drawing, x, y, s, role="pop", core="glow2"):
    d.shape(role, f"M{x - 9 * s} {y - 12 * s} Q{x} {y - 15 * s} {x + 9 * s} {y - 12 * s} L{x + 6 * s} {y + 10 * s} Q{x} {y + 12 * s} {x - 6 * s} {y + 10 * s}Z",
            spot=True, shadow=s > .6)
    d.shape(core, ellipse(x, y + 8 * s, 4 * s, 2.4 * s), shadow=False)


def lantern_sky(d: Drawing):
    stars(d, [(30, 70, 2.4), (60, 36, 2), (150, 30, 2.6), (176, 74, 2), (110, 22, 1.8)], "light")
    d.band("far", "M-30 140 Q30 118 70 132 Q110 112 150 128 Q180 118 230 134")
    d.band("mid", waves(150, 3, 26))
    if d.paper:
        d.raw(f'<g opacity=".35" fill="{d.c["glow2"]}"><rect x="66" y="158" width="6" height="3" rx="1.5"/><rect x="118" y="164" width="8" height="3" rx="1.5"/>'
              f'<rect x="96" y="156" width="10" height="3" rx="1.5"/></g>')
    for x, y, s in [(52, 104, .5), (150, 104, .55), (128, 50, .7), (70, 52, .6), (172, 60, .45), (30, 116, .4), (40, 74, .45)]:
        sky_lantern(d, x, y, s)
    sky_lantern(d, 100, 94, 1.5)
    d.band("deep", waves(172, 3, 30), line=False)


def lantern_red(d: Drawing):
    d.disc("glow", 100, 70, 26)
    clip_open(d)
    d.stroke("dark", "M-10 22 Q100 50 210 22", 1.6)
    clip_close(d)
    lantern(d, 44, 76, 1.6)
    lantern(d, 156, 76, 1.6)
    lantern(d, 100, 112, 2.4)


def lantern_river(d: Drawing):
    d.disc("glow", 140, 52, 16)
    stars(d, [(40, 40, 2.4), (80, 30, 2), (176, 80, 2)], "light")
    d.band("far", "M-30 104 H20 V92 L28 80 L36 92 V100 H70 L84 78 L80 74 L90 62 L100 74 L96 78 L110 100 H150 V90 H170 V104 H230")
    d.band("mid", "M-30 112 H230")
    d.stroke("glow2", "M30 124 h20 M120 120 h30 M70 132 h14", 1.8)

    def lotus(x, y, s):
        def draw():
            d.shape("glow2", ellipse(0, -14, 3, 6), shadow=False)
            d.shape("pop", "M-6 -10 Q0 4 6 -10Z", shadow=False)
            d.shape("lotus", "M-18 0 C-22 -10 -16 -14 -12 -14 C-10 -6 -6 -2 0 0 C6 -2 10 -6 12 -14 C16 -14 22 -10 18 0Z", spot=True)
            d.shape("lotus2", "M-8 0 C-10 -8 -6 -14 0 -18 C6 -14 10 -8 8 0Z", shadow=False)
            d.shape("leaf", ellipse(0, 2, 22, 4))
        group(d, f"translate({x} {y}) scale({s})", draw)
    if d.paper:
        d.raw(f'<g opacity=".3" fill="{d.c["glow2"]}"><ellipse cx="100" cy="168" rx="16" ry="3"/><ellipse cx="46" cy="148" rx="8" ry="2"/><ellipse cx="156" cy="152" rx="8" ry="2"/></g>')
    lotus(46, 136, .7)
    lotus(156, 140, .75)
    lotus(132, 120, .45)
    lotus(100, 156, 1.35)

GOLD = {"gold": "#E2B04A", "gold2": "#B7862C"}
STONE = {"stone": "#D8CCB8", "stone2": "#B5A68E"}
WOOD = {"wood": "#B07A4A", "wood2": "#8A5A33"}
BLOSSOM = {"blossom": "#F6B8C8"}
NIGHT = {"sky": "#22294A", "sky2": "#2E3B5E", "far": "#3B4876", "mid": "#52628F", "deep": "#151B30"}

CONCEPTS = [
    Concept("temple-pagoda", "temple-visit", "Pagoda & cherry blossom", temple_pagoda, overrides=BLOSSOM,
            checks=[("pop", "sky"), ("dark", "far"), ("blossom", "sky"), ("pop", "far")], fixes={"pop": ["hero", "#D9534F"], "blossom": ["#EE8FAA", "light"]}),
    Concept("temple-stupa", "temple-visit", "Stupa & prayer flags", temple_stupa, overrides=GOLD,
            checks=[("light", "mid"), ("gold", "sky"), ("gold", "far"), ("light", "far")], fixes={"far": ["near", "deep"]}),
    Concept("temple-torii", "temple-visit", "Torii gate", temple_torii, overrides={"hero": "#D64933"},
            checks=[("hero", "glow"), ("hero", "far"), ("hero", "sky"), ("hero", "mid")], fixes={"glow": ["glow2", "light"], "far": ["deep", "near"]}),
    Concept("castle-hilltop", "castle-tour", "Hilltop fortress", castle_hilltop, overrides=STONE,
            checks=[("stone", "sky"), ("stone", "far"), ("stone", "mid")], fixes={"stone": ["#C2B194", "#B3A285", "#A69577"], "far": ["mid", "near"], "mid": ["near", "deep"]}),
    Concept("castle-fairytale", "castle-tour", "Fairytale turrets", castle_fairytale, overrides=STONE,
            checks=[("stone", "far"), ("stone", "mid"), ("hero", "far"), ("hero", "sky"), ("stone", "sky")], fixes={"stone": ["#C2B194", "#B3A285", "#A69577"], "far": ["near", "deep"], "mid": ["near", "deep"]}),
    Concept("castle-drawbridge", "castle-tour", "Drawbridge gate", castle_drawbridge, overrides={**STONE, **WOOD},
            checks=[("stone", "sky"), ("wood", "mid"), ("stone", "mid")], fixes={"stone": ["#C2B194", "#B3A285", "#A69577"], "mid": ["near", "deep"]}),
    Concept("museum-facade", "museum", "Classical museum", museum_facade,
            checks=[("light", "glow"), ("light", "sky"), ("light", "mid"), ("light", "near")], fixes={"sky": ["far", "sky2"], "glow": ["glow2", "mid", "near"]}),
    Concept("museum-dino", "museum", "Dinosaur skeleton", museum_dino,
            checks=[("light", "far"), ("light", "mid"), ("dark", "near")], fixes={"far": ["mid", "near", "deep"], "mid": ["near", "deep"]}),
    Concept("museum-amphora", "museum", "Greek amphora", museum_amphora, overrides={"hero": "#D07A45", "mark": "#2B211C"},
            checks=[("hero", "far"), ("light", "far"), ("light", "mid")], fixes={"far": ["deep", "near", "mid"]}),
    Concept("gallery-frame", "art-gallery", "Golden frame", gallery_frame, overrides=GOLD,
            checks=[("gold", "far"), ("gold", "mid")], fixes={"far": ["deep", "near", "mid"], "mid": ["near", "deep"]}),
    Concept("gallery-palette", "art-gallery", "Paint palette", gallery_palette, overrides={"wood": "#D9A66B"},
            checks=[("wood", "glow"), ("wood", "sky")], fixes={"glow": ["near", "deep", "mid"]}),
    Concept("gallery-wall", "art-gallery", "Gallery wall", gallery_wall, overrides=GOLD,
            checks=[("gold", "far"), ("dark", "far"), ("dark", "mid")], fixes={"far": ["light", "sky2", "glow2"]}),
    Concept("ruins-columns", "ancient-ruins", "Temple columns", ruins_columns, overrides={"stone": "#EFE3CC", "stone2": "#CDBB9C"},
            checks=[("stone", "glow"), ("stone", "sky"), ("stone", "far"), ("dark", "glow")], fixes={"glow": ["near", "mid", "deep"], "sky": ["sky2", "far", "mid"], "far": ["near", "deep"]}),
    Concept("ruins-colosseum", "ancient-ruins", "Colosseum", ruins_colosseum, overrides={"stone": "#E2C292", "stone2": "#C29A66"},
            checks=[("stone", "sky"), ("stone2", "sky"), ("stone", "mid")], fixes={"mid": ["near", "deep"]}),
    Concept("ruins-llama", "ancient-ruins", "Mountain citadel & llama", ruins_llama, overrides={"llama": "#FBF2E2", "stone": "#CDBFA6"},
            checks=[("llama", "mid"), ("llama", "ground"), ("near", "far"), ("stone", "mid")], fixes={"far": ["sky2", "light"], "mid": ["near", "deep"], "ground": ["mid", "near"]}),
    Concept("pyramids-camels", "pyramids", "Pyramids & camels", pyramids_camels, overrides={"sand": "#EDBE6F", "sand2": "#C98E45"},
            checks=[("sand", "sky"), ("sand", "glow"), ("dark", "ground"), ("sand", "ground")], fixes={"glow": ["near", "pop", "light"], "sky": ["sky2", "far", "light"], "ground": ["mid", "near"]}),
    Concept("pyramids-sphinx", "pyramids", "Sphinx", pyramids_sphinx, overrides={"sand": "#E9B96E", "sand2": "#B98444"},
            checks=[("sand", "sky"), ("sand", "ground"), ("sand", "mid")], fixes={"sky": ["sky2", "far", "light"], "ground": ["mid", "near"], "mid": ["near", "deep"]}),
    Concept("pyramids-maya", "pyramids", "Jungle step pyramid", pyramids_maya, overrides={"stone": "#C9B48E", "stone2": "#A38D69"},
            checks=[("stone", "glow"), ("stone", "far"), ("stone", "sky"), ("deep", "far")], fixes={"glow": ["near", "pop", "mid"], "far": ["mid", "near"]}),
    Concept("oldtown-alley", "old-town-stroll", "Laundry-line alley", oldtown_alley,
            checks=[("hero2", "sky"), ("near", "sky"), ("light", "sky"), ("ground", "hero2")], fixes={"sky": ["sky2", "far", "glow"], "hero2": ["mid", "far"]}),
    Concept("oldtown-canal", "old-town-stroll", "Canal houses", oldtown_canal,
            checks=[("hero", "sky"), ("hero2", "sky"), ("pop", "sky"), ("mid", "sky"), ("near", "sky")], fixes={"sky": ["sky2", "light"]}),
    Concept("oldtown-clocktower", "old-town-stroll", "Clock tower square", oldtown_clocktower, overrides={"ground2": "#00000022"},
            checks=[("light", "sky"), ("hero", "sky"), ("hero2", "sky")], fixes={"sky": ["sky2", "far", "mid"]}),
    Concept("walk-guide", "walking-tour", "Follow the guide", walk_guide,
            checks=[("mid", "sky"), ("hero", "ground"), ("near", "ground"), ("hero2", "ground"), ("deep", "ground"), ("hero", "mid"), ("hero2", "mid")],
            fixes={"mid": ["far", "near"], "ground": ["light", "far"]}),
    Concept("walk-map", "walking-tour", "City map & pin", walk_map,
            checks=[("light", "glow"), ("pop", "light"), ("pop", "sky2")], fixes={"glow": ["mid", "far", "near"]}),
    Concept("walk-signpost", "walking-tour", "Signpost", walk_signpost,
            checks=[("hero", "sky"), ("pop", "sky"), ("hero2", "sky"), ("hero", "far"), ("pop", "far"), ("hero2", "far")], fixes={"far": ["light", "mid", "near"]}),
    Concept("rooftop-skyline", "rooftop-views", "Skyline & cocktail", rooftop_skyline,
            checks=[("far", "sky"), ("mid", "far"), ("light", "mid"), ("dark", "near"), ("glow2", "sky")], fixes={"far": ["mid", "near"], "mid": ["near", "deep"], "glow2": ["pop", "glow"]}),
    Concept("rooftop-santorini", "rooftop-views", "Blue domes", rooftop_santorini, overrides={"dome": "#2F6DB5"},
            checks=[("light", "far"), ("light", "sky"), ("dome", "sky"), ("dome", "light")], fixes={"sky": ["sky2", "glow2"], "far": ["mid", "near"]}),
    Concept("rooftop-cat", "rooftop-views", "Rooftop cat", rooftop_cat,
            checks=[("dark", "sky"), ("near", "far"), ("near", "sky"), ("far", "sky")], fixes={"far": ["mid", "sky2"]}),
    Concept("market-stall", "local-market", "Fruit stall", market_stall, overrides={**WOOD, "fruit": "#7FB347", "leaf": "#5E9C4A"},
            checks=[("hero", "sky"), ("light", "sky"), ("wood", "ground"), ("hero2", "wood"), ("pop", "wood")], fixes={"sky": ["sky2", "far"], "hero2": ["glow2", "light"]}),
    Concept("market-basket", "local-market", "Market basket", market_basket,
            overrides={"wood": "#C98F52", "wood2": "#9C6A38", "bread": "#E8B76A", "bread2": "#B9813C", "leaf": "#6DAA4F", "leaf2": "#3F7A35"},
            checks=[("wood", "glow"), ("bread", "glow"), ("leaf", "glow"), ("pop", "wood")], fixes={"glow": ["light", "sky2", "far"], "pop": ["#D9412F"]}),
    Concept("market-spices", "local-market", "Spice mounds", market_spices,
            overrides={"sp1": "#C8432B", "sp2": "#E8B12A", "sp3": "#D9792B", "sp4": "#7A9A3A", "sp5": "#8B4A2B", "sack": "#D9B98A", "sack2": "#B0905F", "wood": "#9C6A38"},
            checks=[("sack", "far"), ("sp2", "far"), ("light", "mid"), ("sp2", "light")], fixes={"far": ["near", "deep", "mid"], "mid": ["near", "deep"]}),
    Concept("nightmarket-stalls", "night-market", "Lantern-lit stalls", nightmarket_stalls, palettes=["dusk", "golden", "coastal", "blush"], overrides={**NIGHT, **WOOD},
            checks=[("hero", "far"), ("pop", "far"), ("wood", "mid")], fixes={}),
    Concept("nightmarket-skewers", "night-market", "Grill skewers", nightmarket_skewers, palettes=["dusk", "golden", "coastal", "blush"],
            overrides={**NIGHT, "meat": "#A0582F", "leaf": "#6DAA4F", "wood": "#C9A16B"},
            checks=[("meat", "sky"), ("pop", "hero"), ("hero", "sky")], fixes={"pop": ["hero2", "glow2"]}),
    Concept("nightmarket-steamers", "night-market", "Dumpling steamers", nightmarket_steamers, palettes=["dusk", "golden", "coastal", "blush"],
            overrides={**NIGHT, "wood": "#D9B07A", "wood2": "#A87C45"}, checks=[("wood", "sky"), ("pop", "sky"), ("wood", "mid")]),
    Concept("festival-fireworks", "festival", "Fireworks over town", festival_fireworks, palettes=["dusk", "golden", "coastal", "blush", "meadow"], overrides=NIGHT,
            checks=[("pop", "sky"), ("glow2", "sky"), ("far", "sky"), ("mid", "far")], fixes={"mid": ["deep", "near"]}),
    Concept("festival-marquees", "festival", "Festival marquees", festival_tents,
            checks=[("pop", "sky"), ("hero", "far"), ("hero2", "far"), ("pop", "far"), ("light", "hero2")], fixes={"far": ["mid", "near"], "hero2": ["glow", "near"]}),
    Concept("festival-dragon", "festival", "Dragon dance", festival_dragon, overrides={"pop": "#D7372B", "hero2": "#F2C14E"},
            checks=[("pop", "sky"), ("hero2", "sky"), ("pop", "far"), ("hero2", "far")], fixes={"sky": ["sky2", "far", "mid"], "far": ["mid", "near", "deep"]}),
    Concept("carnival-mask", "carnival", "Masquerade mask", carnival_mask, overrides={**GOLD, "wood": "#8A5A33"},
            checks=[("gold", "glow"), ("pop", "gold"), ("hero", "glow"), ("hero2", "glow")], fixes={"glow": ["mid", "near", "deep"]}),
    Concept("carnival-carousel", "carnival", "Carousel horse", carnival_carousel, overrides={**GOLD, "horse": "#FFFFFF"},
            checks=[("horse", "far"), ("hero", "far"), ("gold", "far"), ("hero", "sky")], fixes={"far": ["mid", "near", "deep"]}),
    Concept("carnival-ferris", "carnival", "Ferris wheel", carnival_ferris,
            checks=[("hero", "sky"), ("hero", "far"), ("pop", "sky"), ("hero2", "sky"), ("light", "sky")], fixes={"sky": ["sky2", "far"], "far": ["mid", "near"]}),
    Concept("concert-guitar", "concert", "Acoustic guitar", concert_guitar, overrides={"guitar": "#D9893B", "guitar2": "#E9A65A", "neck": "#7A4A26"},
            checks=[("guitar", "glow"), ("neck", "glow"), ("dark", "glow")], fixes={"glow": ["far", "mid", "light", "near"]}),
    Concept("concert-stage", "concert", "Live on stage", concert_stage, palettes=["dusk", "golden", "coastal", "blush", "meadow"],
            overrides={**NIGHT, "crowd": "#0B0F1C"}, checks=[("dark", "mid"), ("dark", "glow"), ("crowd", "mid"), ("glow", "sky")], fixes={"glow": ["glow2", "pop"]}),
    Concept("concert-violin", "concert", "Violin & bow", concert_violin, overrides={"violin": "#B5562B", "violin2": "#8A3D1C", "wood": "#5A3A22"},
            checks=[("violin", "glow"), ("violin2", "glow"), ("wood", "glow")], fixes={"glow": ["light", "far", "sky2"]}),
    Concept("photo-camera", "photography-walk", "Vintage camera", photo_camera,
            checks=[("hero", "glow"), ("light", "glow"), ("dark", "hero")], fixes={"glow": ["far", "mid", "near"]}),
    Concept("photo-polaroids", "photography-walk", "Instant snaps", photo_polaroids, overrides={"wood": "#C98F52"},
            checks=[("light", "glow"), ("mid", "sky2"), ("hero", "sky2")], fixes={"glow": ["far", "mid", "near"]}),
    Concept("photo-tripod", "photography-walk", "Camera on tripod", photo_tripod,
            checks=[("hero", "mid"), ("hero", "far"), ("hero", "sky"), ("dark", "near"), ("dark", "mid")], fixes={"hero": ["pop", "hero2", "light"]}),
    Concept("lantern-sky", "lantern-festival", "Sky lanterns", lantern_sky, palettes=["dusk", "golden", "coastal", "blush", "meadow"], overrides=NIGHT,
            checks=[("pop", "sky"), ("pop", "far")], fixes={"pop": ["hero2", "glow"]}),
    Concept("lantern-red", "lantern-festival", "Red lanterns", lantern_red, overrides={"pop": "#D7372B", "hero2": "#F2C14E"},
            checks=[("pop", "sky"), ("pop", "glow"), ("hero2", "sky")], fixes={"glow": ["far", "light", "mid"], "sky": ["sky2", "far"]}),
    Concept("lantern-river", "lantern-festival", "River lanterns", lantern_river, palettes=["dusk", "golden", "coastal", "blush", "meadow"],
            overrides={**NIGHT, "lotus": "#F4A6B8", "lotus2": "#FBD3DC", "leaf": "#4F8A5B"}, checks=[("lotus", "mid"), ("leaf", "mid"), ("far", "sky")]),
]
