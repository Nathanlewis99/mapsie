"""Mapsie Originals: famous landmarks of the Middle East and Africa (second landmark round).

Sheikh Zayed Mosque, Wadi Rum, Pamukkale, Cappadocia, Library of Celsus, Karnak, Chefchaouen, Sahara dunes,
Lalibela, Avenue of the Baobabs, Deadvlei, Djenne, Zanzibar dhow, Ngorongoro, Cape Point, Blyde River Canyon,
Mount Kenya, Anse Source d'Argent, Le Morne Brabant, Dead Sea.
"""
from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group, acacia, balloon  # noqa: F401
import math


# ================================================================ private helpers (copied, not imported)
def poly(*pts, close=True) -> str:
    s = "M" + " L".join(f"{x:g} {y:g}" for x, y in pts)
    return s + ("Z" if close else "")


def clipped(fn):
    """Wrap a whole drawing in the circle clip (line-style shapes are otherwise unclipped)."""
    def draw(d: Drawing):
        d.raw('<g clip-path="url(#clip)">', '<g clip-path="url(#clip)">')
        fn(d)
        d.raw("</g>", "</g>")
    draw.__name__ = fn.__name__
    return draw


def birds(d: Drawing, pts, role="dark"):
    s = " ".join(f"M{x} {y} q{3 * k} {-3 * k} {6 * k} 0 q{3 * k} {-3 * k} {6 * k} 0" for x, y, k in pts)
    d.stroke(role, s, 1.7)


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


def frond(x, y, ang, length, droop, w=0.22) -> str:
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


def pointed_arch(x, y, w, h) -> str:
    return f"M{x} {y + h} V{y + w * .5} Q{x} {y} {x + w / 2} {y - w * .25} Q{x + w} {y} {x + w} {y + w * .5} V{y + h}Z"


def round_arch(x, y, w, h) -> str:
    """Round-topped opening: top of the arch at y, bottom at y+h."""
    r = w / 2
    return f"M{x} {y + h} V{y + r} A{r} {r} 0 0 1 {x + w} {y + r} V{y + h}Z"


ELEPHANT = ("M46 120 C46 96 66 84 92 84 C108 84 120 88 128 96 C134 86 150 84 160 92 C168 99 168 112 162 120 "
            "C160 132 161 148 166 160 C168 166 163 171 158 166 C151 154 149 140 148 130 L144 132 L144 172 "
            "L132 172 L131 148 L118 148 L117 172 L105 172 L104 148 L80 146 L79 172 L67 172 L66 146 L58 145 "
            "L57 172 L45 172 L46 140 C44 134 44 126 46 120Z")


# ================================================================ SHEIKH ZAYED GRAND MOSQUE
def bulb(cx, base, w, h) -> str:
    """A slightly bulbous dome, widest just above its base, rising to a point."""
    return (f"M{cx - w / 2:.1f} {base} C{cx - w * .62:.1f} {base - h * .45:.1f} {cx - w * .16:.1f} {base - h * .8:.1f} {cx} {base - h} "
            f"C{cx + w * .16:.1f} {base - h * .8:.1f} {cx + w * .62:.1f} {base - h * .45:.1f} {cx + w / 2:.1f} {base}Z")


def bulb_shade(cx, base, w, h) -> str:
    return (f"M{cx} {base - h} C{cx + w * .16:.1f} {base - h * .8:.1f} {cx + w * .62:.1f} {base - h * .45:.1f} {cx + w / 2:.1f} {base} "
            f"H{cx + w * .12:.1f} C{cx + w * .2:.1f} {base - h * .4:.1f} {cx + w * .08:.1f} {base - h * .8:.1f} {cx} {base - h}Z")


def dome(d: Drawing, cx, base, w, h, drum=0, spot=False):
    if drum:
        d.shape("marble", rrect(cx - w * .42, base, w * .84, drum, 1))
        d.shape("shade", rrect(cx - w * .42, base + drum * .45, w * .84, 1.6, 0), shadow=False, line=False)
    d.shape("marble", bulb(cx, base, w, h), spot=spot)
    d.shape("shade", bulb_shade(cx, base, w, h), shadow=False, line=False)
    d.stroke("gold", f"M{cx} {base - h + 1} V{base - h - h * .22 - 2}", 1.6)
    d.marks("gold", circle(cx, base - h - 1.5, max(1.2, w * .045)))


def minaret(d: Drawing, x, base, top):
    """Slender four-stage minaret with balconies and a small gilded cap."""
    h = base - top
    d.shape("marble", f"M{x - 4.5} {base} V{top + 14} H{x + 4.5} V{base}Z")
    d.shape("shade", f"M{x + 1.5} {base} V{top + 14} H{x + 4.5} V{base}Z", shadow=False, line=False)
    for f in (.35, .58, .78):
        y = top + h * (1 - f)
        d.shape("marble", rrect(x - 6.5, y, 13, 3, 1), shadow=False)
    d.shape("marble", f"M{x - 3.5} {top + 15} V{top + 10} Q{x - 3.5} {top + 3} {x} {top} Q{x + 3.5} {top + 3} {x + 3.5} {top + 10} V{top + 15}Z")
    d.shape("gold", f"M{x - 3.2} {top + 8} Q{x - 3} {top + 3} {x} {top} Q{x + 3} {top + 3} {x + 3.2} {top + 8}Z", shadow=False)
    d.stroke("gold", f"M{x} {top} V{top - 6}", 1.2)


def sheikh_zayed(d: Drawing):
    d.disc("glow", 152, 50, 11)
    # minarets at the four corners (rear pair smaller)
    minaret(d, 50, 128, 66)
    minaret(d, 150, 128, 66)
    # domes, back to front
    for cx in (40, 160):
        dome(d, cx, 108, 16, 15, drum=6)
    for cx in (66, 134):
        dome(d, cx, 98, 26, 25, drum=10)
    dome(d, 100, 80, 50, 46, drum=16, spot=True)
    # arcaded prayer hall and platform
    d.shape("marble", "M24 108 H176 V134 H24Z")
    d.marks("shade", " ".join(pointed_arch(30 + i * 12.4, 114, 7, 16) for i in range(12)))
    d.shape("gold", rrect(24, 108, 152, 2.2, 0), shadow=False, line=False)
    minaret(d, 26, 140, 48)
    minaret(d, 174, 140, 48)
    d.shape("marble", "M8 134 H192 V142 H8Z")
    # reflecting pool with the domes mirrored in it
    d.band("pool", "M-30 146 H230")
    d.raw('<g opacity=".28" fill="#fff" transform="matrix(1 0 0 -.55 0 226)">'
          f'<path d="{bulb(100, 80, 50, 46)}"/><path d="{bulb(66, 98, 26, 25)}"/><path d="{bulb(134, 98, 26, 25)}"/>'
          '<path d="M24 108 H176 V134 H24Z"/></g>', "")
    d.stroke("light", "M30 158 h18 M120 160 h22 M70 168 h16 M150 170 h14", 1.8)
    d.band("pave", "M-30 176 H230")
    d.stroke("shade", "M-30 182 H230", 1.2, line=False)


# ================================================================ WADI RUM
JEBEL = ("M70 150 L80 124 Q80 104 88 92 Q90 74 102 70 Q108 58 122 60 Q130 50 144 56 Q152 46 166 52 Q178 50 186 60 "
         "Q196 64 198 80 L208 104 Q216 110 230 112 V150Z")


def wadi_rum(d: Drawing):
    d.disc("glow", 52, 62, 16)
    d.band("rock3", "M-30 112 L-8 98 Q4 84 18 88 Q30 80 40 90 L54 106 L80 110 L230 104")
    d.shape("rock", JEBEL)
    d.shape("rock2", "M166 52 Q178 50 186 60 Q196 64 198 80 L208 104 Q216 110 230 112 V150 H176 Q180 110 174 80Z", shadow=False, spot=True)
    d.stroke("rock2", "M92 96 Q90 116 94 136 M104 74 Q100 100 106 132 M118 64 Q114 92 120 128 M132 60 Q128 90 134 126 "
                      "M146 58 Q142 84 150 120 M160 56 Q156 82 162 116", 2, line=False)
    d.raw("", f'<path d="M104 80 Q100 104 106 130 M132 66 Q128 92 134 124 M160 60 Q156 84 162 114" fill="none" stroke="{d.c.get("ink", "")}" stroke-width="2" stroke-linecap="round"/>')
    # rock arch / mushroom outcrop on the left
    d.shape("rock", "M-30 150 V112 Q-14 100 0 104 Q10 94 22 100 Q34 102 40 116 L48 150Z")
    d.stroke("rock2", "M2 108 Q0 126 4 146 M20 104 Q16 124 22 146 M34 112 Q32 128 38 146", 1.8, line=False)
    d.band("sand", "M-30 146 Q40 134 100 142 T230 136")
    d.band("sand2", "M-30 168 Q60 156 120 164 T230 158", shadow=False, line=False)
    d.stroke("sand2", "M120 150 Q140 146 160 150 M150 158 Q170 154 190 158", 1.6, line=False)
    camel(d, 70, 128, .9, rider=True)
    d.limb("dark", "M62 156 Q60 150 62 146", 3)  # walking guide
    d.marks("dark", circle(62, 141, 3) + "M58 146 Q62 143 66 146 L66 157 H58Z")
    d.band("near", "M-30 182 Q60 172 120 178 T230 174", line=False)


# ================================================================ PAMUKKALE
def _q(p0, p1, p2, t):
    return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])


def basin(d: Drawing, x0, x1, y, h, dip=9, seed=0):
    """One travertine pool: a crescent of turquoise water held by a curved white rim,
    with a curtain of calcite icicles hanging from the rim."""
    m = (x0 + x1) / 2
    w = x1 - x0
    A, C, B = (x0, y), (m, y + 2 * dip), (x1, y)
    n = max(4, int(w // 5))
    lens = [2, 6, 3, 8, 1, 5, 4, 7]
    pts = []
    for i in range(n, -1, -1):
        px, py = _q(A, C, B, i / n)
        L = lens[(i + seed) % len(lens)] if 0 < i < n else 0
        pts.append((px, py + h + L))
        if i > 0:
            qx, qy = _q(A, C, B, (i - .5) / n)
            pts.append((qx, qy + h - 1))
    curtain = " L".join(f"{px:.1f} {py:.1f}" for px, py in pts)
    d.shape("trav", f"M{x0} {y} Q{m} {y + 2 * dip} {x1} {y} L{curtain}Z")
    d.shape("trav2", f"M{x0} {y + h * .5} Q{m} {y + 2 * dip + h * .5} {x1} {y + h * .5} L{curtain}Z", shadow=False, line=False)
    d.shape("pool", f"M{x0 + 2} {y} Q{m} {y - 6} {x1 - 2} {y} Q{m} {y + 2 * dip - 3} {x0 + 2} {y}Z", shadow=False, spot=True)
    d.stroke("pool2", f"M{m - w * .22:.1f} {y + 1:.1f} H{m + w * .08:.1f}", 1.5, line=False)


def pamukkale(d: Drawing):
    d.disc("glow", 152, 42, 12)
    d.band("hill", "M-30 70 Q30 50 90 54 Q150 44 230 62")
    d.band("trav", "M-30 86 Q40 66 100 68 T230 74")
    rows = [(78, 10, 8, [(34, 82), (78, 128), (124, 170)]),
            (102, 11, 9, [(-2, 46), (42, 98), (94, 142), (138, 196)]),
            (128, 12, 10, [(-30, 18), (14, 70), (66, 124), (120, 172), (168, 226)]),
            (156, 13, 10, [(-10, 50), (46, 104), (100, 160), (156, 214)])]
    for r, (y, h, dip, spans) in enumerate(rows):
        for i, (x0, x1) in enumerate(spans):
            basin(d, x0, x1, y + (3 if i % 2 else 0), h, dip, seed=i * 3 + r)
    d.band("pool", "M-30 190 Q100 186 230 190", line=False)


# ================================================================ CAPPADOCIA
def chimney(d: Drawing, x, base, w, h, cap=True):
    """A fairy chimney: tapering tuff cone wearing a darker basalt cap, with carved openings."""
    t = base - h
    d.shape("tuff", f"M{x - w / 2} {base} Q{x - w * .26} {base - h * .45} {x - w * .14} {t + 4} Q{x} {t - 2} {x + w * .14} {t + 4} "
                    f"Q{x + w * .26} {base - h * .45} {x + w / 2} {base}Z")
    d.shape("tuff2", f"M{x + w * .06} {t + 6} Q{x + w * .18} {base - h * .45} {x + w * .2} {base} H{x + w / 2} "
                     f"Q{x + w * .26} {base - h * .45} {x + w * .14} {t + 4}Z", shadow=False, line=False)
    if cap:
        cw = w * .42
        d.shape("cap", f"M{x - cw} {t + 6} Q{x - cw} {t - cw * .9} {x} {t - cw * .95} Q{x + cw} {t - cw * .9} {x + cw} {t + 6} Q{x} {t + 2} {x - cw} {t + 6}Z", spot=True)


def cappadocia(d: Drawing):
    d.disc("glow", 150, 92, 20)
    group(d, "translate(140 44) scale(.2)", lambda: balloon(d, body="hero2", stripes="light", centre="pop"))
    group(d, "translate(10 62) scale(.22)", lambda: balloon(d, body="pop", stripes="hero2", centre="light"))
    group(d, "translate(152 4) scale(.16)", lambda: balloon(d, body="hero", stripes="light", centre="hero2"))
    group(d, "translate(26 14) scale(.14)", lambda: balloon(d, body="hero2", stripes="pop", centre="hero"))
    group(d, "translate(54 2) scale(.5)", lambda: balloon(d))
    d.band("ridge", "M-30 132 L10 122 Q30 116 50 122 L80 118 Q110 112 130 120 L170 116 Q200 112 230 120")
    chimney(d, 30, 160, 26, 48)
    chimney(d, 172, 160, 28, 54)
    chimney(d, 150, 162, 22, 36)
    d.band("tuff2", "M-30 160 Q30 148 80 152 Q120 146 230 156", line=False)
    chimney(d, 62, 176, 30, 62)
    chimney(d, 120, 178, 34, 80)
    chimney(d, 92, 180, 22, 40)
    d.marks("dark", round_arch(115, 126, 5, 7) + round_arch(124, 140, 5, 7) + round_arch(116, 156, 6, 10) + round_arch(58, 140, 5, 7)
            + round_arch(64, 154, 5, 8) + round_arch(26, 134, 4, 6) + round_arch(171, 128, 4, 6))
    d.band("near", hills(182, 5, 20))


# ================================================================ LIBRARY OF CELSUS
def column(d: Drawing, x, top, base, w=5.0):
    d.shape("marble", rrect(x - w / 2, top, w, base - top, .6))
    d.shape("marble", rrect(x - w / 2 - 1.2, top - 2.5, w + 2.4, 2.8, .5), shadow=False)  # capital
    d.stroke("marble2", f"M{x + w * .15:.1f} {top + 2} V{base - 1}", 1, line=False)


def pediment(d: Drawing, x0, x1, y, kind):
    m = (x0 + x1) / 2
    if kind == "tri":
        d.shape("marble", f"M{x0} {y} L{m} {y - 11} L{x1} {y}Z")
        d.shape("marble2", f"M{x0 + 4} {y - 1.2} L{m} {y - 8.5} L{x1 - 4} {y - 1.2}Z", shadow=False, line=False)
    else:
        d.shape("marble", f"M{x0} {y} Q{m} {y - 18} {x1} {y}Z")
        d.shape("marble2", f"M{x0 + 4} {y - 1.2} Q{m} {y - 13} {x1 - 4} {y - 1.2}Z", shadow=False, line=False)


def celsus(d: Drawing):
    d.band("far", "M-30 60 Q30 38 90 44 Q150 34 230 52")
    # cypresses
    for x, h in [(18, 64), (184, 58), (172, 44)]:
        d.shape("cypress", f"M{x} {150 - h} Q{x + 8} {150 - h * .5} {x + 5} 150 H{x - 5} Q{x - 8} {150 - h * .5} {x} {150 - h}Z")
    # back wall of both storeys
    d.shape("wall", "M36 62 H164 V158 H36Z")
    # doors with windows above
    d.marks("dark", rrect(91, 122, 18, 36, 1) + rrect(54, 130, 12, 28, 1) + rrect(134, 130, 12, 28, 1))
    d.marks("dark", rrect(93, 110, 14, 8, 1) + rrect(55, 118, 10, 7, 1) + rrect(135, 118, 10, 7, 1))
    d.stroke("marble", "M89 121 H111 M52 129 H68 M132 129 H148", 2.2)
    # lower storey: four pairs of columns on pedestals, each pair carrying its own projecting entablature
    for cx in (42, 78, 122, 158):
        d.shape("marble", rrect(cx - 10, 146, 20, 12, .8))
        column(d, cx - 5, 112, 146)
        column(d, cx + 5, 112, 146)
        d.shape("marble", rrect(cx - 11, 103, 22, 7, .6))
        d.shape("marble2", rrect(cx - 11, 108, 22, 1.6, 0), shadow=False, line=False)
    d.shape("marble", rrect(34, 104, 132, 4, .5), shadow=False)
    # upper storey: three aediculae over the gaps, triangular at the sides, segmental in the middle
    for cx, kind in [(60, "tri"), (100, "seg"), (140, "tri")]:
        column(d, cx - 8, 76, 103, 4.4)
        column(d, cx + 8, 76, 103, 4.4)
        d.shape("marble", rrect(cx - 12, 68, 24, 6, .6))
        pediment(d, cx - 13, cx + 13, 68, kind)
    d.marks("dark", rrect(95, 82, 10, 16, 4) + rrect(55, 84, 10, 14, 4) + rrect(135, 84, 10, 14, 4))
    # steps
    d.shape("marble", "M26 158 H174 V164 H26Z")
    d.shape("marble", "M18 164 H182 V170 H18Z")
    d.band("ground", "M-30 170 Q100 166 230 170")
    d.band("near", hills(186, 4, 30), line=False)


# ================================================================ KARNAK
def glyph_band(x0, x1, y) -> str:
    """Abstract carved relief marks (ornament, not writing)."""
    s, x, i = "", x0 + 3, 0
    while x < x1 - 4:
        k = i % 4
        if k == 0:
            s += ellipse(x + 1.6, y, 1.8, 1.2)
        elif k == 1:
            s += rrect(x, y - 3, 1.6, 6, .6)
        elif k == 2:
            s += f"M{x} {y + 2.5} Q{x + 2} {y - 4} {x + 4} {y + 2.5}Z"
        else:
            s += rrect(x, y - .8, 4, 1.6, .6)
        x += 5.4
        i += 1
    return s


def papyrus_column(d: Drawing, cx, w, top, base, rich=True, spot=False):
    """Massive hypostyle column: open papyrus capital under a square abacus, carved bands and a cartouche."""
    cap_top = top + w * .2
    shaft_top = cap_top + w * .38
    d.shape("stone", f"M{cx - w / 2} {base} L{cx - w / 2 + 1} {shaft_top} H{cx + w / 2 - 1} L{cx + w / 2} {base}Z")
    d.shape("stone2", f"M{cx + w * .2} {base} L{cx + w * .22} {shaft_top} H{cx + w / 2 - 1} L{cx + w / 2} {base}Z", shadow=False, line=False)
    # open papyrus capital flaring out to the abacus
    d.shape("stone", f"M{cx - w / 2 + 1} {shaft_top + 1} Q{cx - w / 2 - 1} {cap_top + w * .2} {cx - w * .68} {cap_top} H{cx + w * .68} "
                     f"Q{cx + w / 2 + 1} {cap_top + w * .2} {cx + w / 2 - 1} {shaft_top + 1}Z", spot=spot)
    d.stroke("stone2", f"M{cx - w * .3} {shaft_top} Q{cx - w * .4} {cap_top + w * .2} {cx - w * .5} {cap_top + 1} "
                       f"M{cx} {shaft_top} V{cap_top + 1} M{cx + w * .3} {shaft_top} Q{cx + w * .4} {cap_top + w * .2} {cx + w * .5} {cap_top + 1}", 1.4, line=False)
    d.shape("stone", rrect(cx - w * .4, top, w * .8, cap_top - top, .5))
    d.shape("stone2", rrect(cx + w * .1, top, w * .3, cap_top - top, .5), shadow=False, line=False)
    if not rich:
        d.stroke("stone2", f"M{cx - w / 2 + 1} {shaft_top + 6} H{cx + w / 2 - 1} M{cx - w / 2 + 1} {shaft_top + 10} H{cx + w / 2 - 1}", 1.2)
        return
    # carved bands of relief and a big cartouche
    y = shaft_top + 6
    d.stroke("stone2", f"M{cx - w / 2 + 1} {y} H{cx + w / 2 - 1} M{cx - w / 2 + 1} {y + 16} H{cx + w / 2 - 1}", 1.6)
    d.marks("stone2", glyph_band(cx - w / 2 + 2, cx + w / 2 - 2, y + 8))
    d.shape("stone2", ellipse(cx - 2, y + 40, w * .2, 15), shadow=False)
    d.shape("stone", ellipse(cx - 2, y + 40, w * .2 - 2, 13), shadow=False, line=False)
    d.marks("stone2", circle(cx - 2, y + 32, 2.6) + rrect(cx - 5, y + 38, 6, 2, .6) + f"M{cx - 6} {y + 50} Q{cx - 2} {y + 42} {cx + 2} {y + 50}Z")
    d.stroke("stone2", f"M{cx - 4 - w * .2} {y + 57} H{cx + w * .2}", 1.6)
    d.stroke("stone2", f"M{cx - w / 2 + 1} {y + 64} H{cx + w / 2 - 1} M{cx - w / 2 + 1} {y + 80} H{cx + w / 2 - 1}", 1.6)
    d.marks("stone2", glyph_band(cx - w / 2 + 2, cx + w / 2 - 2, y + 72))


def karnak(d: Drawing):
    d.disc("glow", 58, 112, 12)
    d.band("far", "M-30 150 Q100 146 230 150")
    # Hatshepsut's obelisk seen between the columns
    d.shape("obel", "M137 150 L138.5 70 L142 63 L145.5 70 L147 150Z")
    d.shape("obel2", "M142 63 L145.5 70 L147 150 H142.5Z", shadow=False, line=False)
    d.marks("obel2", " ".join(rrect(140.3, 78 + i * 13, 3.4, 7, .6) for i in range(5)))
    # lintels resting on the abaci
    d.shape("stone", "M-30 6 H230 V22 H-30Z")
    d.stroke("stone2", "M-30 16 H230", 1.6, line=False)
    papyrus_column(d, 14, 48, 22, 170)
    papyrus_column(d, 186, 48, 22, 170)
    papyrus_column(d, 100, 54, 22, 172, spot=True)
    d.band("ground", "M-30 164 Q100 158 230 164")
    d.shape("stone2", "M40 174 L58 168 L76 172 L70 180Z")
    d.band("near", hills(188, 4, 20), line=False)


# ================================================================ CHEFCHAOUEN
def chefchaouen(d: Drawing):
    d.band("far", "M-30 70 L20 46 L48 60 L84 30 L118 56 L150 40 L186 58 L230 46")
    # house at the top of the stairs, with an arched passage
    d.shape("blue2", "M58 132 V62 H142 V132Z")
    d.shape("blue3", round_arch(84, 86, 32, 48), shadow=False)
    d.shape("blue2", rrect(56, 60, 88, 4, 1), shadow=False)
    d.marks("blue3", rrect(64, 74, 8, 10, 1.5) + rrect(128, 74, 8, 10, 1.5))
    # stairs climbing toward the arch
    steps = [(130, 84, 116), (140, 74, 126), (151, 62, 138), (163, 50, 150), (176, 36, 164), (190, 20, 180)]
    prev = (122, 88, 112)
    for y, xl, xr in steps:
        py, pl, pr = prev
        d.shape("step", f"M{pl} {py} H{pr} L{xr} {y - 4} H{xl}Z", shadow=False)
        d.shape("blue", f"M{xl} {y - 4} H{xr} V{y} H{xl}Z", shadow=False)
        prev = (y, xl, xr)
    d.shape("step", "M20 190 H180 V230 H20Z", shadow=False, line=False)
    # left house: tall wall with a deep blue door and a window
    d.shape("blue", "M-30 30 L66 44 L84 124 L36 230 H-30Z")
    d.shape("blue3", "M66 44 L84 124 L76 142 L60 50Z", shadow=False)
    d.shape("door", round_arch(18, 108, 24, 48), spot=True)
    d.stroke("blue", "M30 112 V156 M20 130 H40", 1.2, line=False)
    d.marks("blue3", round_arch(30, 56, 16, 22))
    # right house
    d.shape("blue", "M230 24 L136 40 L116 124 L164 230 H230Z")
    d.shape("blue3", "M136 40 L116 124 L124 142 L140 46Z", shadow=False)
    d.marks("blue3", round_arch(156, 96, 18, 26))
    d.shape("door", round_arch(150, 136, 24, 46), spot=True)
    d.stroke("blue", "M162 140 V182 M152 160 H172", 1.2, line=False)
    # hanging flower pots
    for x, y in [(14, 90), (48, 78), (56, 104), (176, 64), (150, 82), (186, 120)]:
        d.shape("leaf", ellipse(x, y - 4, 7, 4.5), shadow=False)
        d.shape("pot", f"M{x - 5} {y - 2} H{x + 5} L{x + 3.5} {y + 6} H{x - 3.5}Z", spot=True)
        d.marks("pop", circle(x - 3, y - 7, 1.6) + circle(x + 3, y - 6, 1.6))


# ================================================================ SAHARA DUNES (MERZOUGA)
def merzouga(d: Drawing):
    d.disc("glow", 140, 64, 22)
    d.band("dune3", "M-30 120 Q30 104 70 110 Q120 96 170 108 Q200 112 230 104")
    # the big star dune: lit face left, shadow right of the knife-edge crest
    d.band("dune", "M-30 150 Q30 128 70 96 Q90 78 104 72 Q130 86 170 112 Q200 126 230 128")
    d.shape("dune2", "M104 72 Q130 86 170 112 Q200 126 230 128 V170 H140 Q128 116 104 72Z", shadow=False, spot=True)
    # front dune with the caravan along its crest
    d.band("dune", "M-30 150 Q40 132 100 140 Q160 146 230 134")
    d.shape("dune2", "M100 140 Q160 146 230 134 V200 H150 Q140 160 100 140Z", shadow=False, line=False)
    d.stroke("dune2", "M20 160 Q40 154 60 160 M40 170 Q62 164 84 170 M10 178 Q30 172 50 178", 1.5, line=False)
    camel(d, 104, 114, .62, rider=True)
    camel(d, 80, 111, .62, rider=True)
    camel(d, 56, 110, .62)
    d.limb("dark", "M48 130 Q47 124 48 120", 2.4)
    d.marks("dark", circle(48, 115.5, 2.3) + "M45 120 Q48 118 51 120 L51 130 H45Z")
    d.stroke("dark", "M53 126 Q62 130 66 125", 1)
    d.band("near", "M-30 186 Q60 176 120 182 T230 178", line=False)


# ================================================================ LALIBELA (BETE GIYORGIS)
def lalibela(d: Drawing):
    """Bete Giyorgis seen from the rim: a cross-shaped church carved down into the rock, in its trench."""
    cx, cy, k, a, arm, h = 100, 72, .56, 52, 18, 50
    sy = lambda py: cy + py * k

    def cross(dy=0.0, s=1.0):
        A, W = a * s, arm * s
        pts = [(-W, -A), (W, -A), (W, -W), (A, -W), (A, W), (W, W), (W, A), (-W, A), (-W, W), (-A, W), (-A, -W), (-W, -W)]
        return poly(*[(round(cx + x, 1), round(sy(y) + dy, 1)) for x, y in pts])

    d.band("plateau", "M-30 30 Q100 22 230 30")
    # the trench: far wall face, then its floor
    back, front, side = -62, 92, 66
    yb, yf = sy(back), sy(front)
    d.shape("pitwall", poly((cx - side, yb), (cx + side, yb), (cx + side, yf), (cx - side, yf)), shadow=False)
    d.shape("pitfloor", poly((cx - side, yb + h), (cx + side, yb + h), (cx + side, yf), (cx - side, yf)), shadow=False, line=False)
    # the church: a cross extruded straight down; only the faces turned to us show
    body = (cross(h) + " " + poly((cx - arm, sy(a)), (cx + arm, sy(a)), (cx + arm, sy(a) + h), (cx - arm, sy(a) + h))
            + " " + poly((cx - a, sy(arm)), (cx - arm, sy(arm)), (cx - arm, sy(arm) + h), (cx - a, sy(arm) + h))
            + " " + poly((cx + arm, sy(arm)), (cx + a, sy(arm)), (cx + a, sy(arm) + h), (cx + arm, sy(arm) + h)))
    d.shape("rock2", body)
    wins = ""
    for x in (-arm + 5, arm - 10):
        wins += round_arch(cx + x, sy(a) + 8, 5, 10)
    for x in (-a + 8, a - 15):
        wins += round_arch(cx + x, sy(arm) + 9, 5, 10) + round_arch(cx + x, sy(arm) + 26, 5, 10)
    d.marks("dark", wins)
    d.stroke("rock", f"M{cx - a} {sy(arm) + 5} H{cx - arm} M{cx + arm} {sy(arm) + 5} H{cx + a} M{cx - arm} {sy(a) + 4} H{cx + arm}", 1.4, line=False)
    # the roof: nested crosses carved in relief
    d.shape("roof", cross(), spot=True)
    d.stroke("rock2", cross(0, .74), 1.8)
    d.stroke("rock2", cross(0, .46), 1.6, line=False)
    # the near rim hides the foot of the walls
    d.band("plateau", f"M-30 {yf} H230")
    d.stroke("rock2", f"M-30 {yf + 6} Q100 {yf + 2} 230 {yf + 6}", 1.2, line=False)
    for x, y, r in [(18, 46, 9), (32, 38, 7), (176, 42, 10), (190, 54, 7), (26, 162, 8), (172, 166, 9), (186, 152, 6), (40, 176, 6)]:
        d.shape("tree", circle(x, y, r))
    d.band("near", "M-30 186 Q100 180 230 186", line=False)


# ================================================================ AVENUE OF THE BAOBABS
def baobab(d: Drawing, x, base, h, w, role="dark"):
    t = base - h
    d.shape(role, f"M{x - w / 2} {base} C{x - w * .58} {base - h * .4} {x - w * .46} {t + h * .2} {x - w * .32} {t} "
                  f"H{x + w * .32} C{x + w * .46} {t + h * .2} {x + w * .58} {base - h * .4} {x + w / 2} {base}Z")
    br = (f"M{x - w * .2:.1f} {t + 1} Q{x - w * .5:.1f} {t - h * .08:.1f} {x - w * .95:.1f} {t - h * .1:.1f} "
          f"M{x - w * .1:.1f} {t + 1} Q{x - w * .2:.1f} {t - h * .12:.1f} {x - w * .38:.1f} {t - h * .18:.1f} "
          f"M{x + w * .05:.1f} {t + 1} Q{x + w * .1:.1f} {t - h * .12:.1f} {x + w * .2:.1f} {t - h * .2:.1f} "
          f"M{x + w * .2:.1f} {t + 1} Q{x + w * .5:.1f} {t - h * .08:.1f} {x + w * .95:.1f} {t - h * .12:.1f}")
    d.limb(role, br, max(1.4, w * .12), shadow=False)
    tufts = (ellipse(x - w * .95, t - h * .11, w * .28, w * .13) + ellipse(x - w * .38, t - h * .19, w * .26, w * .13)
             + ellipse(x + w * .2, t - h * .21, w * .26, w * .13) + ellipse(x + w * .95, t - h * .13, w * .28, w * .13))
    d.shape(role, tufts, shadow=False)


def baobabs(d: Drawing):
    d.disc("glow", 100, 128, 34)
    d.band("far", "M-30 140 Q100 136 230 140")
    d.band("ground", "M-30 144 Q100 140 230 144")
    d.shape("road", "M96 142 H104 L150 230 H50Z", shadow=False)
    for x, base, h, w in [(86, 146, 34, 7), (114, 146, 36, 7), (72, 150, 54, 11), (128, 150, 56, 11)]:
        baobab(d, x, base, h, w)
    for x, base, h, w in [(46, 160, 86, 17), (156, 160, 90, 18), (12, 176, 120, 25), (190, 178, 116, 24)]:
        baobab(d, x, base, h, w)
    d.stroke("dark", "M86 166 h10 M106 180 h14", 1.4, line=False)
    d.band("near", hills(190, 4, 20), line=False)


# ================================================================ DEADVLEI
def dead_tree(d: Drawing, x, base, s=1.0, flip=1):
    k = s
    f = flip
    trunk = (f"M{x} {base} Q{x - 2 * k * f} {base - 18 * k} {x + 2 * k * f} {base - 30 * k} "
             f"M{x + 1 * k * f} {base - 26 * k} Q{x - 10 * k * f} {base - 38 * k} {x - 20 * k * f} {base - 44 * k} "
             f"M{x - 12 * k * f} {base - 39 * k} L{x - 14 * k * f} {base - 52 * k} "
             f"M{x + 2 * k * f} {base - 30 * k} Q{x + 12 * k * f} {base - 40 * k} {x + 16 * k * f} {base - 56 * k} "
             f"M{x + 12 * k * f} {base - 43 * k} L{x + 24 * k * f} {base - 48 * k} "
             f"M{x - 20 * k * f} {base - 44 * k} L{x - 28 * k * f} {base - 42 * k} "
             f"M{x + 2 * k * f} {base - 30 * k} L{x + 3 * k * f} {base - 46 * k}")
    d.limb("tree", trunk, 3.6 * k)
    d.limb("tree", f"M{x} {base} L{x - 1 * f} {base - 18 * k}", 6 * k, shadow=False)


def deadvlei(d: Drawing):
    d.band("dune", "M-30 128 Q20 84 60 66 Q84 54 98 50 Q140 70 190 108 Q210 120 230 122")
    d.shape("dune2", "M98 50 Q140 70 190 108 Q210 120 230 122 V150 H150 Q130 90 98 50Z", shadow=False, spot=True)
    d.band("dune3", "M-30 132 Q10 112 34 104 Q48 110 70 132")
    d.shape("dune", "M34 104 Q48 110 70 132 H40 Q40 116 34 104Z", shadow=False, line=False)
    d.band("clay", "M-30 136 Q100 128 230 136")
    d.stroke("clay2", "M20 150 L40 146 L52 152 M60 166 L84 160 L96 168 M120 152 L140 156 L156 150 M150 172 L170 166 "
                      "M30 176 L46 170", 1.2, line=False)
    d.shape("clay2", ellipse(70, 166, 22, 3) + ellipse(140, 150, 14, 2) + ellipse(176, 141, 8, 1.4), shadow=False, line=False)
    dead_tree(d, 176, 141, .42, -1)
    dead_tree(d, 140, 150, .7)
    dead_tree(d, 68, 166, 1.25, -1)
    d.band("clay", "M-30 186 Q100 182 230 186", shadow=False, line=False)


# ================================================================ GREAT MOSQUE OF DJENNE
def mud_tower(d: Drawing, x, w, top, base, beams_y):
    d.shape("mud", f"M{x - w / 2} {base} L{x - w / 2 + 1.5} {top + w * .45} Q{x - w / 2 + 2} {top} {x} {top - 2} "
                   f"Q{x + w / 2 - 2} {top} {x + w / 2 - 1.5} {top + w * .45} L{x + w / 2} {base}Z")
    d.shape("mud2", f"M{x + w * .15} {base} L{x + w * .17} {top + w * .3} Q{x + w * .3} {top + 1} {x + w / 2 - 1.5} {top + w * .45} L{x + w / 2} {base}Z", shadow=False, line=False)
    # pinnacle with its ostrich egg
    d.shape("mud", f"M{x - 4} {top + 1} Q{x - 3} {top - 10} {x} {top - 14} Q{x + 3} {top - 10} {x + 4} {top + 1}Z")
    d.shape("egg", ellipse(x, top - 16, 2.4, 3), shadow=False, spot=True)
    d.stroke("mud2", f"M{x - w * .25} {top + 10} V{base} M{x + w * .05} {top + 8} V{base}", 1.2, line=False)
    sticks = ""
    for y in beams_y:
        for xx in (x - w * .32, x, x + w * .32):
            sticks += f"M{xx - 2.6:.1f} {y} h5.2 "
    d.stroke("wood", sticks, 2)


def djenne(d: Drawing):
    d.disc("glow", 160, 46, 12)
    # long facade wall with a parapet of small pinnacles
    d.shape("mud", "M26 140 V92 H174 V140Z")
    d.shape("mud", " ".join(f"M{x - 3} 93 V84 Q{x} 78 {x + 3} 84 V93Z" for x in [30, 40, 72, 82, 118, 128, 160, 170]), shadow=False)
    d.stroke("mud2", " ".join(f"M{x} 92 V140" for x in [30, 40, 72, 82, 118, 128, 160, 170]), 1.3, line=False)
    sticks = " ".join(f"M{x - 2.6} {y} h5.2" for y in (104, 122) for x in [30, 40, 72, 82, 118, 128, 160, 170])
    d.stroke("wood", sticks, 2)
    # the three great towers
    mud_tower(d, 56, 26, 58, 140, (72, 90, 108, 126))
    mud_tower(d, 144, 26, 58, 140, (72, 90, 108, 126))
    mud_tower(d, 100, 30, 40, 140, (56, 74, 92, 110))
    d.marks("dark", pointed_arch(94, 120, 12, 20))
    # raised plinth and market square
    d.shape("mud", "M12 152 L18 138 H182 L188 152Z")
    d.shape("mud2", "M12 152 L18 138 H182 L188 152Z", shadow=False, line=False)
    d.shape("mud", rrect(86, 138, 28, 6, 1), shadow=False)
    d.band("ground", "M-30 152 Q100 148 230 152")
    for x, y, c in [(40, 166, "pop"), (66, 172, "hero2"), (150, 168, "hero"), (124, 176, "pop")]:
        d.shape(c, f"M{x - 8} {y} Q{x} {y - 9} {x + 8} {y}Z")
        d.stroke("dark", f"M{x} {y - 6} V{y + 6}", 1.4)
    d.band("near", hills(186, 4, 20), line=False)


# ================================================================ ZANZIBAR DHOW
def zanzibar(d: Drawing):
    d.disc("glow", 52, 92, 18)
    # Stone Town on the horizon
    town = "M100 112 V104 H108 V100 H116 V106 H122 V96 H126 V92 H130 V96 H134 V106 H146 V102 H156 V108 H166 V104 H176 V112Z"
    d.shape("far", town, shadow=False)
    d.band("sea", "M-30 112 H230")
    d.band("sea2", waves(130, 2.5, 22), shadow=False)
    # lateen-rigged dhow, bow to the left
    d.limb("hull", "M30 120 L172 30", 2.4, shadow=False)
    d.shape("sail", "M36 118 L168 33 Q164 86 150 134 Q100 128 36 118Z", spot=False)
    d.shape("sail2", "M168 33 Q164 86 150 134 Q140 133 138 132 Q152 90 168 33Z", shadow=False, line=False)
    d.stroke("sail2", "M64 112 Q100 84 160 50 M90 118 Q118 96 156 76 M116 124 Q134 112 152 102", 1.2, line=False)
    d.limb("hull", "M120 140 L118 78", 3)
    d.shape("hull", "M18 128 Q26 132 34 142 Q44 152 60 154 H150 Q166 150 172 136 L178 126 L168 132 Q120 138 60 138 Q40 136 18 128Z", spot=True)
    d.stroke("hull2", "M36 144 Q50 148 66 148 H150 Q160 146 166 140", 2, line=False)
    d.stroke("light", "M40 160 h20 M110 162 h26 M150 168 h14 M20 176 h22 M80 178 h18", 2)
    d.band("sea3", waves(186, 3, 32), line=False)


# ================================================================ NGORONGORO CRATER
def ngorongoro(d: Drawing):
    d.shape("light", cloud(-6, 46, 1.2), shadow=False)
    # far crater rim: a long even wall, clouds pouring over its lip
    d.band("far", "M-30 84 Q0 66 40 62 Q100 56 160 60 Q200 62 230 78")
    d.shape("light", cloud(52, 62, 1.1) + cloud(118, 58, 1.3), shadow=False)
    d.band("mid", "M-30 104 Q40 94 100 96 T230 100", shadow=False)
    d.band("floor", "M-30 112 Q100 106 230 112")
    d.shape("lake", ellipse(118, 120, 34, 5.5), shadow=False)
    d.marks("pop", circle(98, 120, .9) + circle(102, 121, .9) + circle(106, 119.5, .9) + circle(110, 121, .9) + circle(126, 120, .9))
    d.marks("dark", " ".join(ellipse(x, y, 1.6, 1) for x, y in [(56, 116), (62, 118), (66, 115), (70, 117), (150, 128), (156, 130), (161, 127)]))
    # near rim, an elephant on the lip looking in
    d.band("near", "M-30 142 Q40 128 90 136 Q140 144 230 128")
    acacia(d, 32, -2, .78)
    group(d, "translate(66 72) scale(.5)", lambda: d.shape("dark", ELEPHANT, spot=True))
    d.stroke("light", "M140 130 q4 -2 8 0", 1, line=False)
    d.band("deep", hills(178, 6, 20))


# ================================================================ CAPE POINT
def cape_point(d: Drawing):
    d.disc("glow", 46, 60, 14)
    d.band("far", "M-30 120 Q-6 112 14 116 L230 120")
    d.band("sea", "M-30 118 H230")
    # the headland: cliffs plunging to the sea, lighthouse on the summit
    d.shape("rock", "M230 70 Q190 70 150 78 Q132 70 120 68 L110 70 Q98 78 92 96 L78 112 L66 132 L58 146 H230Z")
    d.shape("rock2", "M92 96 L78 112 L66 132 L58 146 H96 L100 124 L108 104 L110 70 Q98 78 92 96Z", shadow=False)
    d.stroke("rock2", "M120 90 L126 120 M140 92 L136 130 M160 86 L166 116", 1.4, line=False)
    d.shape("fynbos", "M230 70 Q190 70 150 78 Q132 70 120 68 L110 70 L112 76 Q130 76 150 86 Q190 78 230 84Z", shadow=False)
    # lighthouse
    d.shape("light", "M111 70 L113 42 H123 L125 70Z")
    d.shape("lamp", rrect(112.5, 34, 11, 8, 1), shadow=False)
    d.shape("roof", "M110.5 35 Q118 24 125.5 35Z", spot=True)
    d.stroke("lamp", "M118 25 V21", 1.4)
    d.shape("light", rrect(108, 68, 20, 4, 1), shadow=False)
    d.raw('<path d="M120 38 L200 22 L200 50Z" fill="#fff" opacity=".35"/>', "")
    # surf and waves
    d.stroke("light", "M56 146 Q66 140 72 146 Q80 140 88 146 M40 132 h14 M20 150 h18 M70 162 h24 M120 158 h20", 2)
    d.band("sea2", waves(160, 3, 26))
    d.band("sea3", waves(182, 3, 32), line=False)
    birds(d, [(150, 50, 1), (166, 42, .8)])


# ================================================================ BLYDE RIVER CANYON (THREE RONDAVELS)
def rondavel(d: Drawing, x, base, w, h):
    """One of the Three Rondavels: a round drum of banded rock under a green, hut-like conical crown."""
    t = base - h
    d.shape("rock", f"M{x - w / 2} {base} L{x - w * .44} {t + 8} Q{x} {t + 3} {x + w * .44} {t + 8} L{x + w / 2} {base}Z")
    d.shape("rock2", f"M{x + w * .14} {base} L{x + w * .16} {t + 7} Q{x + w * .35} {t + 6} {x + w * .44} {t + 8} L{x + w / 2} {base}Z", shadow=False, line=False)
    d.stroke("rock2", f"M{x - w * .45} {t + 20} Q{x} {t + 16} {x + w * .46} {t + 20} M{x - w * .47} {t + 34} Q{x} {t + 30} {x + w * .48} {t + 34}", 1.6, line=False)
    d.stroke("light", f"M{x - w * .3} {t + 12} V{t + 30} M{x - w * .1} {t + 12} V{t + 24}", 1.2, line=False)
    d.shape("grass", f"M{x - w * .5} {t + 11} Q{x - w * .3} {t - w * .2} {x - w * .06} {t - w * .5} Q{x} {t - w * .56} {x + w * .06} {t - w * .5} "
                     f"Q{x + w * .3} {t - w * .2} {x + w * .5} {t + 11} Q{x} {t + 5} {x - w * .5} {t + 11}Z", spot=True)
    d.shape("grass2", f"M{x + w * .06} {t - w * .5} Q{x + w * .3} {t - w * .2} {x + w * .5} {t + 11} Q{x + w * .3} {t + 7} {x + w * .2} {t + 7} "
                      f"Q{x + w * .2} {t - w * .2} {x + w * .06} {t - w * .5}Z", shadow=False, line=False)


def blyde(d: Drawing):
    d.disc("glow", 150, 44, 11)
    # far canyon rim: a flat-topped escarpment
    d.band("far", "M-30 84 L6 80 L20 70 H120 L132 76 L180 74 L196 80 L230 82")
    rondavel(d, 58, 126, 34, 54)
    rondavel(d, 100, 122, 38, 62)
    rondavel(d, 142, 126, 34, 56)
    # wooded canyon slopes, the river (Blyde Dam) below
    d.band("veg", "M-30 128 Q30 116 80 124 Q130 132 170 118 Q200 112 230 120")
    d.band("water", "M-30 152 Q40 142 100 148 Q150 154 230 142")
    d.stroke("light", "M70 152 h16 M140 150 h14", 1.6, line=False)
    # cliff walls of the gorge framing the view
    d.shape("rock", "M-30 40 L14 56 L22 90 L30 122 L42 150 L50 230 H-30Z")
    d.shape("rock2", "M14 56 L22 90 L30 122 L42 150 L50 230 H30 L26 150 L16 110 Z", shadow=False, line=False)
    d.stroke("rock2", "M-30 76 L18 74 M-30 100 L26 104 M-30 126 L32 132", 1.6, line=False)
    d.shape("grass", "M-30 36 L14 52 L16 58 L-30 46Z", shadow=False)
    d.shape("rock", "M230 70 L192 80 L182 110 L170 150 L164 230 H230Z")
    d.shape("rock2", "M230 70 L192 80 L182 110 L170 150 L164 230 H230 Z M192 80 L230 82", shadow=False, line=False)
    d.stroke("rock", "M230 104 L186 100 M230 130 L176 128", 1.6, line=False)
    d.shape("grass", "M230 66 L190 78 L192 82 L230 74Z", shadow=False)
    d.band("veg2", "M-30 172 Q40 162 100 172 T230 166")
    d.band("veg2", hills(188, 4, 10), line=False)


# ================================================================ MOUNT KENYA
def rosette(x, y, r) -> str:
    """A cabbage-like rosette of spiky leaves, seen from the side."""
    pts = []
    for i in range(18):
        ang = math.pi + i * math.pi / 17 * 1.0
        rr = r if i % 2 == 0 else r * .62
        pts.append((x + rr * math.cos(ang) * 1.15, y + rr * math.sin(ang) * .8))
    pts += [(x + r * .9, y + r * .35), (x, y + r * .55), (x - r * .9, y + r * .35)]
    return poly(*[(round(px, 1), round(py, 1)) for px, py in pts])


def groundsel(d: Drawing, x, base, h, s=1.0, fork=True):
    """Giant groundsel (Dendrosenecio): thick shaggy stems ending in cabbage rosettes."""
    if fork:
        stems = [(x, base, x - 10 * s, base - h), (x, base - h * .45, x + 12 * s, base - h * .82)]
    else:
        stems = [(x, base, x, base - h)]
    for x0, y0, x1, y1 in stems:
        d.limb("trunk", f"M{x0} {y0} Q{(x0 + x1) / 2} {(y0 + y1) / 2} {x1} {y1 + 6}", 7 * s)
    for _, _, x1, y1 in stems:
        r = 11 * s
        d.shape("trunk2", f"M{x1 - 5 * s} {y1 + 2} Q{x1} {y1 + 18 * s} {x1 + 5 * s} {y1 + 2}Z", shadow=False, line=False)
        d.shape("rosette", rosette(x1, y1, r), spot=True)
        d.shape("rosette2", ellipse(x1, y1 - r * .15, r * .45, r * .3), shadow=False, line=False)


def mount_kenya(d: Drawing):
    d.disc("glow", 46, 50, 12)
    d.band("rock", "M-30 122 Q20 108 50 104 L72 84 L84 60 L90 48 L94 34 L98 44 L102 30 L108 46 L114 56 L126 74 L150 96 Q190 106 230 112")
    snow = ("M84 60 L90 48 L94 34 L98 44 L102 30 L108 46 L114 56 L111 60 L106 54 L103 62 L98 56 L94 64 L90 58 L86 64Z "
            "M72 84 L80 72 L82 78 L77 84Z M120 68 L126 74 L134 82 L126 80 L122 84Z")
    d.shape("rock2", "M102 30 L108 46 L114 56 L126 74 L150 96 Q130 92 118 82 L108 62Z", shadow=False, line=False)
    d.shape("light", snow, shadow=False)
    d.shape("light", cloud(30, 100, 1.1) + cloud(130, 98, 1.2), shadow=False)
    d.band("mid", "M-30 130 Q40 116 100 122 T230 118")
    d.band("near", hills(150, 8, 20))
    # giant lobelia spike
    d.shape("lobelia", "M118 160 Q114 124 124 100 Q134 124 130 160Z")
    d.stroke("rosette2", "M119 150 L129 146 M118 138 L130 134 M119 126 L129 122 M121 114 L127 112", 1.4, line=False)
    groundsel(d, 160, 176, 70, 1.15)
    groundsel(d, 40, 168, 48, 1.0, fork=False)
    d.band("deep", hills(184, 5, 10), line=False)


# ================================================================ ANSE SOURCE D'ARGENT
def boulder(d: Drawing, path, grooves):
    d.shape("granite", path)
    d.stroke("granite2", grooves, 1.5, line=False)


def seychelles(d: Drawing):
    d.disc("glow", 140, 46, 11)
    d.band("sea", "M-30 112 H230")
    d.band("lagoon", "M-30 124 Q100 120 230 124")
    d.band("lagoon2", "M-30 140 Q100 134 230 140", shadow=False, line=False)
    # granite boulders
    boulder(d, "M118 140 Q114 104 132 88 Q150 72 172 80 Q196 86 204 110 Q214 130 210 150 H118Z",
            "M136 92 Q132 112 136 140 M152 82 Q148 110 154 142 M170 82 Q166 108 172 142 M186 92 Q184 116 190 144")
    d.shape("granite2", "M186 92 Q200 100 204 110 Q214 130 210 150 H190 Q194 116 186 92Z", shadow=False, line=False)
    boulder(d, "M150 150 Q148 124 166 118 Q186 116 194 134 Q200 146 196 158 H150Z",
            "M162 122 Q158 136 162 156 M178 118 Q176 136 180 158")
    boulder(d, "M-30 150 V70 Q-4 52 20 58 Q44 62 52 82 Q62 104 58 124 Q56 140 64 154Z",
            "M2 62 Q-2 96 4 146 M20 60 Q14 96 22 148 M38 70 Q32 100 40 150")
    d.shape("granite2", "M38 70 Q50 78 52 82 Q62 104 58 124 Q56 140 64 154 H44 Q46 110 38 70Z", shadow=False, line=False)
    # leaning palm
    palm(d, 26, 156, 92, 56, 1.0, role="leaf", trunk="trunk", bend=-14)
    d.band("sand", "M-30 152 Q60 146 120 154 T230 150")
    d.stroke("lagoon2", "M60 152 Q90 148 120 154 Q150 158 180 152", 2, line=False)
    d.shape("sand2", ellipse(100, 172, 30, 3) + ellipse(40, 180, 18, 2), shadow=False, line=False)
    d.band("sand2", hills(190, 3, 10), line=False)


# ================================================================ LE MORNE BRABANT
MORNE = ("M-30 132 Q0 122 24 116 Q40 110 52 98 L66 82 Q76 66 92 60 Q104 56 118 58 L140 56 Q150 56 154 64 "
         "L158 84 L162 108 L170 124 L182 132Z")


def le_morne(d: Drawing):
    d.disc("glow", 140, 40, 11)
    d.band("sea", "M-30 116 H230")
    d.shape("rock", MORNE)
    d.shape("rock2", "M140 56 Q150 56 154 64 L158 84 L162 108 L170 124 L182 132 H150 L150 96 Q146 74 140 56Z", shadow=False)
    d.stroke("rock2", "M100 62 L104 88 M120 60 L124 84 M138 60 L140 86", 1.4, line=False)
    d.shape("forest", "M-30 132 Q0 122 24 116 Q40 110 52 98 L62 88 Q74 96 90 94 Q110 98 130 96 Q144 100 156 98 L162 108 L170 124 L182 132Z")
    d.shape("forest2", "M-30 132 Q20 118 60 120 Q100 116 140 122 Q160 124 182 132Z", shadow=False, line=False)
    d.band("lagoon", "M-30 134 Q100 130 230 134")
    d.stroke("light", "M-30 132 Q100 128 230 132", 2.4)  # the reef break
    d.band("lagoon2", "M-30 150 Q100 144 230 150", shadow=False, line=False)
    # a kitesurfer on the lagoon
    d.stroke("dark", "M150 156 L168 92 M150 156 L188 104", .8, line=True)
    d.shape("kite", "M160 96 Q176 80 196 98 L190 102 Q176 90 166 100Z", spot=True)
    d.marks("dark", circle(149, 148, 2.2) + "M147 151 L151 151 L152 158 L146 158Z")
    d.shape("hero2", rrect(141, 158, 16, 3, 1.5), shadow=False)
    d.stroke("light", "M30 160 h18 M80 168 h22 M120 176 h16 M170 170 h18", 2)
    d.band("lagoon3", waves(186, 3, 32), line=False)


# ================================================================ DEAD SEA
def dead_sea(d: Drawing):
    d.disc("glow", 150, 56, 14)
    d.band("far", "M-30 104 Q10 92 40 96 Q70 86 100 92 Q140 84 170 92 Q200 88 230 96")
    d.band("sea", "M-30 112 H230")
    d.stroke("light", "M20 124 h18 M160 122 h20", 1.6, line=False)
    # floater lying back, reading
    d.stroke("sea2", "M44 136 Q100 144 162 136", 3, line=False)
    d.limb("skin", "M108 132 L126 116 L146 130", 7)       # raised knee
    d.limb("skin", "M108 134 L150 136", 7)                # straight leg
    d.marks("skin", ellipse(152, 133, 4, 3) + ellipse(148, 128, 4, 3))
    d.shape("skin", "M62 136 Q60 124 72 120 L104 126 Q112 130 110 136Z")
    d.shape("suit", "M72 121 L104 126 Q112 130 110 136 L96 136 Q88 128 74 130Z", spot=True)
    d.shape("skin", circle(58, 114, 8))
    d.shape("hair", "M50 116 Q48 104 58 104 Q66 104 66 110 Q58 108 50 116Z", shadow=False)
    d.limb("skin", "M72 124 L80 108 L82 100", 4.6)
    # the newspaper (blank sheet, no lettering)
    d.shape("light", "M68 82 L96 76 L102 100 L74 106Z")
    d.stroke("paper2", "M74 88 L92 84 M75 93 L94 89 M76 98 L96 94", 1.2, line=False)
    d.stroke("paper2", "M82 80 L88 104", 1, line=False)
    d.limb("skin", "M72 124 L74 104", 4.6)
    # salt formations on the shore
    d.band("salt", "M-30 166 Q40 160 100 166 T230 162")
    d.shape("salt", "M20 166 Q18 152 28 150 Q38 150 36 166Z M140 164 Q136 148 150 146 Q164 148 160 164Z "
                    "M168 166 Q166 156 174 154 Q182 156 180 166Z", shadow=True)
    d.stroke("salt2", "M24 156 h8 M144 154 h12 M30 174 h20 M100 176 h24", 1.2, line=False)
    d.band("salt2", hills(188, 3, 20), line=False)


# ================================================================ concepts
MARBLE = {"marble": "#FFFFFF", "shade": "#DDE1E6", "gold": "#E2B149", "pool": "#5CB8CF", "pave": "#EDE7DC"}
RUM = {"rock": "#C2603D", "rock2": "#97412A", "rock3": "#DE9670", "sand": "#E8854D", "sand2": "#CF6A38"}
PAMU = {"trav": "#FFFFFF", "trav2": "#DCE9EE", "pool": "#5DCAD8", "pool2": "#B5EEF2", "hill": "#93AE74"}
CAPPA = {"tuff": "#F1D2A6", "tuff2": "#D7A877", "cap": "#8C5E40", "ridge": "#C98A5A"}
CELSUS = {"marble": "#F2E6CD", "marble2": "#CDB48D", "wall": "#D6BE97", "cypress": "#3F6B45"}
KARNAK = {"stone": "#E5B87D", "stone2": "#BC8A52", "obel": "#E9C38E", "obel2": "#C49660"}
CHAOUEN = {"blue": "#4F8FD6", "blue2": "#86B6EA", "blue3": "#2E62A8", "step": "#C7DEF5", "door": "#1F4E8C",
           "pot": "#D9734A", "leaf": "#4E8A4A", "pop": "#F2C14E"}
DUNES = {"dune": "#EF9C48", "dune2": "#CF7330", "dune3": "#F0B070"}
LALI = {"plateau": "#B4844F", "rock": "#C98C5A", "rock2": "#9A6038", "roof": "#D9A06C", "pitwall": "#7C4A2C",
        "pitfloor": "#A26D44", "tree": "#4A6B38"}
BAOBAB = {"road": "#C8784A"}
VLEI = {"dune": "#E0692F", "dune2": "#B2461F", "dune3": "#C9562A", "clay": "#F4EEE3", "clay2": "#D7CBB8", "tree": "#2B201A"}
DJENNE = {"mud": "#C99561", "mud2": "#A97347", "wood": "#5A3E26", "egg": "#F7F0E0", "ground": "#E8CFA0"}
DHOW = {"far": "#5E8FA8", "sail": "#F6EDDC", "sail2": "#D9C8A8", "hull": "#7B4B2A", "hull2": "#B07A45", "sea": "#2E8FB0", "sea2": "#4FB3C6", "sea3": "#1E6F92"}
NGORO = {"floor": "#C7C27A", "lake": "#94C9D4"}
CAPE = {"far": "#6F8FA0", "rock": "#8E7B62", "rock2": "#6A5946", "fynbos": "#7E9A55", "lamp": "#2E3A40", "roof": "#C8473A",
        "sea": "#2A7FA8", "sea2": "#3F98BE", "sea3": "#1E5F86"}
BLYDE = {"rock": "#C9733F", "rock2": "#9E512B", "grass": "#6E9A4A", "grass2": "#557D3A", "veg": "#5A8A48", "veg2": "#3F6B3C", "water": "#4FA0B2"}
KENYA = {"rock": "#7D8798", "rock2": "#5E6878", "trunk": "#6B5A48", "trunk2": "#4E4134", "rosette": "#7FA556", "rosette2": "#5C8240", "lobelia": "#7E9C62"}
SEYCH = {"granite": "#C4A79A", "granite2": "#9C7E72", "sea": "#2C8FB4", "lagoon": "#45C7C1", "lagoon2": "#93E3DB",
         "sand": "#FBF2E2", "sand2": "#EADDC4", "leaf": "#4E8A4A", "trunk": "#8A6A4A"}
MORNE_C = {"rock": "#6F6A60", "rock2": "#545048", "forest": "#4D8A4A", "forest2": "#3C7040", "sea": "#1F6FA0",
           "lagoon": "#3FC4C0", "lagoon2": "#86E0D8", "lagoon3": "#2AA8B0", "kite": "#E8553E"}
DEAD = {"sea": "#5BB7C8", "sea2": "#8FD6DF", "skin": "#E0A27C", "suit": "#E4572E", "hair": "#3B2A20", "paper2": "#B9BEC4",
        "salt": "#FFFFFF", "salt2": "#E3E6E2"}
NO_GOLD = ["coastal", "meadow", "blush", "dusk"]

CONCEPTS = [
    Concept("lm2-sheikhzayed", "landmark-sheikh-zayed-mosque", "Sheikh Zayed Mosque", sheikh_zayed, overrides=MARBLE,
            checks=[("marble", "sky"), ("marble", "glow"), ("pool", "pave"), ("marble", "pool")],
            fixes={"sky": ["sky2", "far", "mid"], "glow": ["glow2", "pop", "hero"]}),
    Concept("lm2-wadirum", "landmark-wadi-rum", "Wadi Rum", wadi_rum, overrides=RUM,
            checks=[("rock", "sky"), ("rock3", "sky"), ("rock", "glow"), ("dark", "sand"), ("sand", "rock")],
            fixes={"sky": ["sky2", "far", "light"], "glow": ["light", "glow2", "#FFE8B0"]}),
    Concept("lm2-pamukkale", "landmark-pamukkale", "Pamukkale", clipped(pamukkale), overrides=PAMU,
            checks=[("hill", "sky"), ("trav", "hill"), ("pool", "trav")],
            fixes={"sky": ["sky2", "light"]}),
    Concept("lm2-cappadocia", "landmark-cappadocia", "Cappadocia balloons", cappadocia, overrides=CAPPA,
            checks=[("hero", "sky"), ("hero2", "sky"), ("tuff", "sky"), ("tuff", "ridge"), ("hero", "glow")],
            fixes={"sky": ["sky2", "far", "#A9D8EA"], "glow": ["glow2", "light", "far"], "hero2": ["pop", "light"]}),
    Concept("lm2-celsus", "landmark-celsus-library", "Library of Celsus", celsus, overrides=CELSUS,
            checks=[("marble", "far"), ("wall", "far"), ("far", "sky"), ("marble", "ground"), ("cypress", "far")],
            fixes={"far": ["mid", "near", "deep"], "ground": ["near", "mid", "deep"]}),
    Concept("lm2-karnak", "landmark-karnak", "Karnak Temple", karnak, overrides=KARNAK,
            checks=[("stone", "sky"), ("obel", "sky"), ("stone", "ground"), ("obel", "glow")],
            fixes={"sky": ["sky2", "far", "mid", "deep"], "ground": ["near", "mid", "deep"], "glow": ["near", "light", "pop"]}),
    Concept("lm2-chefchaouen", "landmark-chefchaouen", "Chefchaouen", clipped(chefchaouen), overrides=CHAOUEN,
            checks=[("blue", "sky"), ("blue2", "far"), ("far", "sky")],
            fixes={"far": ["mid", "near", "deep"]}),
    Concept("lm2-merzouga", "landmark-merzouga", "Sahara dunes", merzouga, overrides=DUNES,
            checks=[("dune", "sky"), ("dune3", "sky"), ("dark", "dune2"), ("dune", "glow")],
            fixes={"glow": ["light", "#FFF3D6", "pop"]}),
    Concept("lm2-lalibela", "landmark-lalibela", "Lalibela rock churches", lalibela, overrides=LALI,
            checks=[("plateau", "sky"), ("roof", "pitwall"), ("roof", "plateau"), ("tree", "plateau")]),
    Concept("lm2-baobabs", "landmark-baobabs", "Avenue of the Baobabs", baobabs, overrides=BAOBAB,
            checks=[("dark", "sky"), ("dark", "glow"), ("dark", "ground"), ("road", "ground")],
            fixes={"ground": ["far", "mid", "#E6B87C"], "road": ["#A65A36", "mid"]}),
    Concept("lm2-deadvlei", "landmark-deadvlei", "Deadvlei", deadvlei, overrides=VLEI,
            checks=[("dune", "sky"), ("dune2", "sky"), ("clay", "dune3"), ("tree", "clay"), ("tree", "dune")],
            fixes={"sky": ["sky2", "far", "deep"]}),
    Concept("lm2-djenne", "landmark-djenne", "Great Mosque of Djenné", djenne, overrides=DJENNE,
            checks=[("mud", "sky"), ("mud", "ground"), ("mud", "glow"), ("egg", "sky")],
            fixes={"sky": ["sky2", "far", "mid"], "glow": ["light", "pop", "near"]}),
    Concept("lm2-zanzibar", "landmark-zanzibar", "Zanzibar dhow", zanzibar, palettes=NO_GOLD, overrides=DHOW,
            checks=[("sail", "sky"), ("sail", "sea"), ("far", "sky"), ("hull", "sea")],
            fixes={"sky": ["#86C5DE"], "far": ["mid", "near", "deep"]}),
    Concept("lm2-ngorongoro", "landmark-ngorongoro", "Ngorongoro Crater", ngorongoro, overrides=NGORO,
            checks=[("far", "sky"), ("floor", "mid"), ("dark", "near"), ("dark", "floor"), ("lake", "floor"), ("light", "far")],
            fixes={"far": ["mid", "near"], "mid": ["near", "deep"]}),
    Concept("lm2-capepoint", "landmark-cape-point", "Cape Point lighthouse", cape_point, palettes=NO_GOLD, overrides=CAPE,
            checks=[("rock", "sky"), ("light", "sky"), ("rock", "sea"), ("far", "sky")],
            fixes={"sky": ["#86C5DE"], "far": ["mid", "near"]}),
    Concept("lm2-blyde", "landmark-blyde-canyon", "Blyde River Canyon", blyde, overrides=BLYDE,
            checks=[("rock", "far"), ("grass", "far"), ("far", "sky"), ("veg", "rock")],
            fixes={"far": ["mid", "near", "deep", "light"]}),
    Concept("lm2-mountkenya", "landmark-mount-kenya", "Mount Kenya", mount_kenya, overrides=KENYA,
            checks=[("rock", "sky"), ("light", "rock"), ("rosette", "near"), ("rosette", "mid"), ("trunk", "near")],
            fixes={"far": ["mid", "near", "deep"], "near": ["deep", "ground"], "mid": ["far", "ground"]}),
    Concept("lm2-seychelles", "landmark-seychelles", "Anse Source d'Argent", clipped(seychelles), palettes=NO_GOLD, overrides=SEYCH,
            checks=[("granite", "sky"), ("granite", "lagoon"), ("granite", "sand"), ("leaf", "sky")],
            fixes={"sky": ["sky2", "far", "mid"]}),
    Concept("lm2-mauritius", "landmark-mauritius", "Le Morne Brabant", le_morne, palettes=NO_GOLD, overrides=MORNE_C,
            checks=[("rock", "sky"), ("forest", "sky"), ("kite", "sky"), ("forest", "lagoon")],
            fixes={"sky": ["sky2", "far"]}),
    Concept("lm2-deadsea", "landmark-dead-sea", "Dead Sea", dead_sea, palettes=NO_GOLD, overrides=DEAD,
            checks=[("far", "sky"), ("skin", "sea"), ("salt", "sea"), ("light", "sea")],
            fixes={"far": ["mid", "near"]}),
]
