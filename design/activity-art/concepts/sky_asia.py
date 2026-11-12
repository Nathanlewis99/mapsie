"""Mapsie Originals: city skylines of Asia (batch sky_asia).

Every skyline is built the same way: sun/moon disc, a pale distant layer ("far"),
a continuous mid layer of city ("mid"), water or ground, then the front layer of
signature buildings ("deep") drawn as one silhouette. In line style the front
layer is drawn as a single clean outline (union of its parts).
"""
import math
import random

from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group  # noqa: F401


# ================================================================ helpers
def poly(*pts, close=True) -> str:
    s = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    return s + ("Z" if close else "")


def rect(x0, x1, top, base) -> str:
    return poly((x0, base), (x0, top), (x1, top), (x1, base))


def sym(cx, prof) -> str:
    """Symmetric tower from a right-hand profile [(half_width, y), ...] listed bottom to top."""
    right = [(cx + hw, y) for hw, y in prof]
    left = [(cx - hw, y) for hw, y in reversed(prof)]
    return poly(*(right + left))


def dome(cx, by, w, h) -> str:
    """Half-ellipse dome sitting on y=by."""
    return f"M{cx - w:.1f} {by:.1f} A{w:.1f} {h:.1f} 0 0 1 {cx + w:.1f} {by:.1f}Z"


def arch(x, y, w, h) -> str:
    r = w / 2
    return f"M{x:.1f} {y + h:.1f} V{y + r:.1f} A{r:.1f} {r:.1f} 0 0 1 {x + w:.1f} {y + r:.1f} V{y + h:.1f}Z"


def pagoda_roof(cx, y, w, h=7.0) -> str:
    """Upturned east-asian eave: tips at (cx±w, y-5)."""
    return (f"M{cx - w:g} {y - 5:g} Q{cx - w * .78:g} {y + 2:g} {cx - w * .58:g} {y + 2:g} H{cx + w * .58:g} "
            f"Q{cx + w * .78:g} {y + 2:g} {cx + w:g} {y - 5:g} Q{cx + w * .62:g} {y - 3:g} {cx + w * .44:g} {y - h:g} "
            f"H{cx - w * .44:g} Q{cx - w * .62:g} {y - 3:g} {cx - w:g} {y - 5:g}Z")


def hip_roof(cx, y, w, top_w, h) -> str:
    """Chinese hip roof: upswept eave tips at (cx±w, y-5), ridge (cx±top_w, y-h)."""
    return (f"M{cx - w:g} {y - 6:g} Q{cx - w * .86:g} {y + 2:g} {cx - w * .66:g} {y + 2:g} H{cx + w * .66:g} "
            f"Q{cx + w * .86:g} {y + 2:g} {cx + w:g} {y - 6:g} Q{cx + w * .7:g} {y - 4:g} {cx + top_w + (w - top_w) * .35:g} {y - h * .55:g} "
            f"L{cx + top_w:g} {y - h:g} H{cx - top_w:g} L{cx - top_w - (w - top_w) * .35:g} {y - h * .55:g} "
            f"Q{cx - w * .7:g} {y - 4:g} {cx - w:g} {y - 6:g}Z")


def strip(x0, x1, base, seed, hmin, hmax, wmin=6.0, wmax=13.0) -> str:
    """A continuous run of low blocks (one stepped polygon)."""
    r = random.Random(seed)
    pts = [(x0, base)]
    x = x0
    while x < x1:
        w = r.uniform(wmin, wmax)
        y = base - r.uniform(hmin, hmax)
        pts += [(x, y), (min(x + w, x1), y)]
        x += w
    pts.append((x1, base))
    return poly(*pts)


def towers(specs, base) -> str:
    """Distant towers: (cx, w, top, kind). kind: f flat, s/S slanted, p antenna, r rounded, g gabled, t stepped."""
    out = []
    for cx, w, top, kind in specs:
        x0, x1 = cx - w / 2, cx + w / 2
        if kind == "s":
            out.append(poly((x0, base), (x0, top + w * .5), (x1, top), (x1, base)))
        elif kind == "S":
            out.append(poly((x0, base), (x0, top), (x1, top + w * .5), (x1, base)))
        elif kind == "p":
            out.append(rect(x0, x1, top, base) + " " + rect(cx - .7, cx + .7, top - 9, top + 1))
        elif kind == "r":
            out.append(f"M{x0:.1f} {base} V{top + w / 2:.1f} A{w / 2:.1f} {w / 2:.1f} 0 0 1 {x1:.1f} {top + w / 2:.1f} V{base}Z")
        elif kind == "g":
            out.append(poly((x0, base), (x0, top + w * .45), (cx, top), (x1, top + w * .45), (x1, base)))
        elif kind == "t":
            out.append(sym(cx, [(w / 2, base), (w / 2, top + 8), (w * .34, top + 8), (w * .34, top + 3), (w * .18, top + 3), (w * .18, top)]))
        else:
            out.append(rect(x0, x1, top, base))
    return " ".join(out)


def _norm(parts):
    out = []
    for p in parts:
        if isinstance(p, str):
            out.append((p, "deep", False))
        elif len(p) == 2:
            out.append((p[0], p[1], False))
        else:
            out.append(p)
    return out


def front(d: Drawing, parts, shadow=True):
    """The front layer of signature buildings. Line style: one clean outline around the union of the parts."""
    parts = _norm(parts)
    if d.paper:
        for p, role, _ in parts:
            d.shape(role, p, shadow=shadow, extra='fill-rule="evenodd"')
    else:
        ink, paper, spot = d.c["ink"], d.c["paper"], d.c["spot"]
        s = "".join(f'<path d="{p}" fill="none" stroke="{ink}" stroke-width="6.2" stroke-linejoin="round"/>' for p, _, _ in parts)
        s += "".join(f'<path d="{p}" fill="{spot if sp else paper}" fill-rule="evenodd"/>' for p, _, sp in parts)
        d.raw("", s)


def layer(d: Drawing, role: str, path: str, line=False):
    """Pale background layers. Line style keeps the skyline to one outline: a hill/ridge layer
    (path ending "V230 H-30Z") becomes just its top edge, everything else is left out."""
    if line and path.endswith(" V230 H-30Z") and not d.paper:
        d.band(role, path[:-len(" V230 H-30Z")])
        return
    d.shape(role, path, line=False if not d.paper else line, extra='fill-rule="evenodd"')


def shade(d: Drawing, path: str, a=.16):
    """A flat shaded side on a papercut building (3D hint)."""
    d.raw(f'<path d="{path}" fill="#1a1020" opacity="{a}"/>', "")


def lit(d: Drawing, path: str, role="glow2"):
    """Lit windows / highlights: papercut only."""
    d.shape(role, path, shadow=False, line=False)


def reflect(d: Drawing, parts, H, role="deep", op=.22, sq=.62):
    if not d.paper:
        return
    c = d.c[role]
    body = "".join(f'<path d="{p}" fill="{c}" fill-rule="evenodd"/>' for p, _, _ in _norm(parts))
    d.raw(f'<g opacity="{op}" transform="matrix(1 0 0 {-sq} 0 {H * (1 + sq):.2f})">{body}</g>')


def water(d: Drawing, H, role="far"):
    d.band(role, f"M-30 {H} H230")


def ripples(d: Drawing, pts, role="light", line=True):
    d.stroke(role, " ".join(f"M{x} {y} h{w}" for x, y, w in pts), 1.7, line=line)


def birds(d: Drawing, pts, role="dark"):
    s = " ".join(f"M{x} {y} q{3 * k} {-3 * k} {6 * k} 0 q{3 * k} {-3 * k} {6 * k} 0" for x, y, k in pts)
    d.stroke(role, s, 1.6)


def palm(d: Drawing, x, base, h, lean=0.0, role="deep", s=1.0, line=True):
    """Coconut palm silhouette: curved trunk and a spray of fronds."""
    tx, ty = x + lean, base - h
    if d.paper or line:
        d.limb(role, f"M{x} {base} Q{x + lean * .2} {base - h * .5} {tx} {ty}", 3.0 * s)
    fr = ""
    for ang, L in [(-160, 20), (-125, 18), (-90, 14), (-55, 18), (-20, 20), (-190, 14), (10, 14)]:
        a = math.radians(ang)
        ex, ey = tx + math.cos(a) * L * s, ty + math.sin(a) * L * s + (6 * s if abs(ang + 90) > 50 else 0)
        mx, my = tx + math.cos(a) * L * s * .55, ty + math.sin(a) * L * s * .55 - 3 * s
        nx, ny = -math.sin(a), math.cos(a)
        fr += (f"M{tx:.1f} {ty:.1f} Q{mx + nx * 3 * s:.1f} {my + ny * 3 * s:.1f} {ex:.1f} {ey:.1f} "
               f"Q{mx - nx * 1 * s:.1f} {my - ny * 1 * s:.1f} {tx:.1f} {ty:.1f}Z ")
    d.shape(role, fr, line=line)


def boat(x, y, s=1.0) -> str:
    """A small low boat hull."""
    return (f"M{x - 12 * s:.1f} {y - 3 * s:.1f} H{x + 12 * s:.1f} L{x + 9 * s:.1f} {y + 2 * s:.1f} "
            f"H{x - 9 * s:.1f}Z M{x - 4 * s:.1f} {y - 3 * s:.1f} V{y - 7 * s:.1f} H{x + 5 * s:.1f} V{y - 3 * s:.1f}Z")


# ================================================================ TOKYO
def skytree(cx, base, top) -> str:
    k = (base - top) / 634
    y = lambda m: base - m * k
    prof = [(9.5, base), (6.0, y(180)), (4.2, y(330)), (6.6, y(340)), (6.6, y(355)), (5.4, y(365)), (3.4, y(372)),
            (3.2, y(440)), (4.6, y(444)), (4.6, y(452)), (2.8, y(456)), (2.4, y(495)), (1.5, y(500)), (.5, top)]
    return sym(cx, prof)


def tokyo_tower(cx, base, top) -> str:
    k = (base - top) / 333
    y = lambda m: base - m * k
    outer = sym(cx, [(16, base), (12.5, y(28)), (7.6, y(120)), (9, y(125)), (9, y(150)), (5.4, y(155)),
                     (3.0, y(240)), (4.2, y(243)), (4.2, y(252)), (2.0, y(256)), (1.3, y(290)), (.5, top)])
    hole = f"M{cx - 11:.1f} {base} Q{cx - 8:.1f} {y(40):.1f} {cx:.1f} {y(48):.1f} Q{cx + 8:.1f} {y(40):.1f} {cx + 11:.1f} {base}Z"
    return outer + " " + hole


def tokyo(d: Drawing):
    d.disc("glow", 152, 58, 14)
    # Mount Fuji, far beyond
    fuji = "M-30 142 C10 138 46 104 70 82 L74 80 L78 82 L82 80 L86 82 C108 102 140 136 190 142Z"
    d.shape("far", fuji, line=True)
    d.shape("light", "M62 90 L70 83 L74 81.5 L78 83 L82 81.5 L86 83 L94 90 L90 93 L86 90 L82 95 L78 91 L74 96 L70 91 L66 94Z", shadow=False, line=False)
    layer(d, "mid", towers([(18, 9, 104, "f"), (28, 8, 96, "s"), (96, 9, 104, "S"), (106, 8, 98, "f"), (148, 9, 100, "t"),
                            (170, 8, 108, "f"), (184, 9, 114, "s")], 142) + " " + strip(-30, 230, 142, 3, 12, 22))
    water(d, 142)
    tt = tokyo_tower(62, 142, 82)
    st = skytree(124, 142, 30)
    blocks = strip(-30, 230, 143, 7, 4, 11, 7, 14)
    tmg = sym(160, [(11, 143), (11, 112), (9, 112), (9, 104)]) + " " + rect(150, 156, 98, 112) + " " + rect(164, 170, 98, 112)
    parts = [blocks, tmg, st, (tt, "tt", True)]
    reflect(d, [blocks, tmg, st, tt], 142)
    front(d, parts)
    d.stroke("light", "M47 132.5 H77 M54 117 H70 M58 99 H66", 2.0, line=False)
    lit(d, " ".join(rrect(x, 128, 2.4, 3, .4) for x in (152, 158, 164)) + " " + rrect(118, 79, 12, 1.6, .5))
    ripples(d, [(24, 152, 14), (96, 160, 22), (150, 154, 16), (60, 172, 12), (130, 176, 14)])


# ================================================================ KYOTO
def five_storey(cx, base, s=1.0) -> list:
    parts = []
    body = [(14, 0), (12.5, 18), (11, 35), (9.5, 50), (8, 63)]
    roofs = [(31, 18), (28, 35), (25, 50), (22, 63), (20, 75)]
    for (hw, y0), (rw, ry) in zip(body, roofs):
        parts.append(rect(cx - hw * s, cx + hw * s, base - (ry - 1) * s, base - y0 * s))
        parts.append(pagoda_roof(cx, base - ry * s, rw * s, 7 * s))
    parts.append(rect(cx - 1.2 * s, cx + 1.2 * s, base - 108 * s, base - 80 * s))
    rings = " ".join(rect(cx - 3 * s, cx + 3 * s, base - (86 + 4 * i) * s - 1.2 * s, base - (86 + 4 * i) * s) for i in range(5))
    parts.append(rings)
    return parts


def kyoto(d: Drawing):
    d.disc("glow", 84, 72, 28)
    layer(d, "far", "M-30 112 Q10 94 40 100 Q70 88 100 100 Q130 82 160 92 Q190 84 230 98 V230 H-30Z", line=True)
    layer(d, "mid", "M-30 132 Q20 116 60 124 Q110 112 150 120 Q190 112 230 120 V230 H-30Z")
    # Kiyomizu-dera main hall on its stilted stage
    hall = (hip_roof(150, 112, 34, 12, 18) + " " + rect(124, 176, 111, 126) + " " + rect(116, 184, 125, 129))
    stilts = " ".join(rect(x, x + 2.6, 128, 150) for x in range(118, 184, 9)) + " " + rect(116, 184, 137, 139.5)
    pag = five_storey(78, 150, 1.0)
    roofs = []
    for i, x in enumerate(range(-24, 230, 22)):
        roofs.append(poly((x, 176), (x, 162), (x + 3, 156), (x + 19, 156), (x + 22, 162), (x + 22, 176)))
    front(d, [hall, stilts], shadow=True)
    d.band("near", "M-30 150 Q40 144 100 150 T230 148", line=False)
    front(d, pag)
    lit(d, " ".join(rect(x - 1.5, x + 1.5, 115, 124) for x in range(130, 172, 7)), "far")
    # sakura / maple puffs and machiya roofs
    for x, y, r in [(16, 140, 12), (30, 146, 10), (186, 142, 11), (118, 150, 8)]:
        d.shape("pop", circle(x, y, r), line=False)
    d.shape("deep", " ".join(roofs), line=False)
    d.band("deep", "M-30 170 H230")
    d.stroke("near", " ".join(f"M{x + 2} 160 H{x + 20}" for x in range(-24, 230, 22)), 1.2, line=False)


# ================================================================ OSAKA
def osaka_castle(cx, base) -> list:
    stone = poly((cx - 34, base), (cx - 28, base - 20), (cx + 28, base - 20), (cx + 34, base))
    b = base - 20
    parts = [("castle_stone", stone)]
    walls, roofs = [], []
    tiers = [(24, 0, 14, 31), (19, 14, 26, 25), (15.5, 26, 37, 21), (12.5, 37, 47, 17.5), (10, 47, 57, 15)]
    for hw, y0, y1, rw in tiers:
        walls.append(rect(cx - hw, cx + hw, b - y1, b - y0))
        roofs.append(pagoda_roof(cx, b - y1 + 1, rw, 6))
    roofs.append(poly((cx - 12, b - 58), (cx - 6, b - 66), (cx + 6, b - 66), (cx + 12, b - 58)))
    gables = " ".join(poly((cx + dx - w, b - y), (cx + dx, b - y - w * .8), (cx + dx + w, b - y)) for dx, y, w in
                      [(0, 26, 8), (-11, 37, 5), (11, 37, 5), (0, 47, 6)])
    return walls, roofs, gables


def umeda_sky(cx, base, top) -> str:
    return (rect(cx - 13, cx - 3, top, base) + " " + rect(cx + 3, cx + 13, top, base) + " " +
            rect(cx - 13, cx + 13, top - 1, top + 6) + " " + rect(cx - 6, cx + 6, top - 4, top + 3) +
            f" M{cx - 13} {top + 6} H{cx + 13} V{top + 10} H{cx + 4} A5 5 0 0 0 {cx - 4} {top + 10} H{cx - 13}Z")


def osaka(d: Drawing):
    d.disc("glow", 108, 56, 15)
    layer(d, "far", towers([(92, 8, 96, "f"), (180, 9, 96, "S"), (192, 8, 104, "f")], 140))
    layer(d, "mid", towers([(18, 9, 108, "t"), (88, 10, 100, "f"), (100, 8, 106, "s"), (174, 10, 104, "f")], 140) +
          " " + strip(-30, 230, 140, 11, 10, 20))
    water(d, 140)
    harukas = sym(160, [(12, 141), (12, 88), (10, 88), (10, 66), (7.5, 66), (7.5, 50), (5.5, 50), (5.5, 46)])
    umeda = umeda_sky(116, 141, 86)
    tsutenkaku = sym(186, [(6, 141), (3.2, 118), (5.2, 116), (5.2, 108), (2.4, 104), (.8, 98)])
    blocks = strip(-30, 230, 141, 5, 4, 10)
    reflect(d, [blocks, harukas, umeda, tsutenkaku], 140)
    front(d, [blocks, harukas, umeda, tsutenkaku])
    lit(d, " ".join(rect(x, x + 1.4, 92, 138) for x in (152, 157, 162, 167)), "near")
    walls, roofs, gables = osaka_castle(56, 162)
    d.band("near", "M-30 156 Q40 150 100 154 T230 156", line=False)
    parts = [(walls[i], "castle") for i in range(5)] + [(" ".join(roofs), "roof"), (gables, "roof")]
    front(d, [("M22 162 L28 142 H84 L90 162Z", "castle_stone")] + parts)
    d.marks("gold", "M44 97 q-2 -5 2 -7 l1 4Z M68 97 q2 -5 -2 -7 l-1 4Z")
    d.stroke("castle_stone2", "M30 152 H82 M26 158 H86", 1.2, line=False)
    lit(d, " ".join(rect(x, x + 2.4, 128, 132) for x in (40, 47, 54, 61, 68)), "roof")
    ripples(d, [(110, 150, 16), (150, 160, 20), (170, 148, 12)])
    d.band("near", "M-30 168 Q60 162 120 168 T230 166", line=False)


# ================================================================ SEOUL
def seoul(d: Drawing):
    d.disc("glow", 88, 46, 13)
    layer(d, "far", "M-30 104 L0 90 L20 98 L44 72 L60 86 L80 80 L104 96 L130 84 L160 98 L190 90 L230 104 V230 H-30Z", line=True)
    # Namsan
    layer(d, "mid", "M-30 136 Q20 126 40 112 Q56 104 72 110 Q98 124 140 126 Q190 124 230 132 V230 H-30Z" + " " +
          towers([(110, 9, 112, "f"), (124, 8, 106, "s"), (182, 9, 112, "f"), (194, 8, 118, "S")], 136))
    water(d, 138)
    lotte = ("M140 139 C141 104 145 66 148.6 38 L150 30 L151.4 38 C155 66 159 104 160 139Z")
    ntower = sym(56, [(4.5, 112), (2.6, 104), (2.4, 82), (5.4, 80), (6.4, 76), (6.4, 72), (4.8, 70), (4.8, 66), (1.6, 64), (1.1, 52), (.4, 44)])
    sixty3 = poly((22, 139), (22, 96), (34, 90), (36, 92), (36, 139))
    blocks = strip(-30, 230, 139, 21, 4, 12)
    reflect(d, [blocks, lotte, sixty3], 138)
    front(d, [ntower])
    front(d, [blocks, lotte, sixty3])
    d.stroke("light", "M150 40 V136", 1.2, line=False)
    d.shape("hero2", poly((24, 137), (24, 97.5), (34, 92.5), (34, 137)), shadow=False, line=False)
    d.stroke("deep", "M27.5 96 V137 M31 94 V137", 1, line=False)
    # Han River bridge
    bridge = rect(-30, 230, 150, 154) + " " + " ".join(rect(x, x + 3, 153, 164) for x in range(-10, 230, 26))
    front(d, [bridge])
    ripples(d, [(30, 170, 16), (94, 176, 20), (150, 172, 14), (70, 146, 12), (120, 145, 14)])


# ================================================================ HONG KONG
def junk(d: Drawing, tx, ty, s):
    def draw():
        d.shape("hull", "M58 150 H146 L154 140 L158 142 L150 162 Q104 168 70 162 Q62 158 58 150Z")
        for m, top, w, hgt, sp in [(76, 102, 22, 44, False), (102, 78, 30, 66, True), (132, 98, 20, 46, False)]:
            d.stroke("hull", f"M{m} 146 V{top - 4}", 1.8)
            sail = f"M{m} {top + 4} L{m + w * .9:.1f} {top:.1f} Q{m + w * 1.25:.1f} {top + hgt * .5:.1f} {m + w:.1f} {top + hgt:.1f} L{m} {top + hgt}Z"
            d.shape("sail", sail, spot=sp)
            bat = " ".join(f"M{m} {top + 4 + (hgt - 4) * k / 5:.1f} L{m + w * (1.02 + .14 * (1 - abs(2 * k / 5 - 1))):.1f} {top + hgt * k / 5:.1f}"
                           for k in range(1, 5))
            d.stroke("sail2", bat, 1.4, line=False)
    group(d, f"translate({tx} {ty}) scale({s})", draw)


def hong_kong(d: Drawing):
    d.disc("glow", 150, 44, 12)
    # Victoria Peak ridges
    layer(d, "far", "M-30 96 Q10 80 40 84 Q70 66 100 74 Q130 62 160 78 Q190 72 230 86 V230 H-30Z", line=True)
    layer(d, "mid", towers([(18, 9, 104, "f"), (34, 8, 96, "S"), (76, 9, 100, "f"), (88, 8, 92, "s"), (130, 9, 96, "f"),
                            (172, 9, 100, "t"), (186, 8, 108, "f")], 138) + " " + strip(-30, 230, 138, 31, 14, 26))
    water(d, 138)
    ifc = sym(56, [(8.5, 139), (8.5, 66), (7.2, 66), (7.2, 59), (6, 59), (6, 54)]) + " " + \
        poly((50, 55), (51, 46), (53, 54), (55, 44), (57, 54), (59, 46), (60.5, 55))
    boc = poly((94, 139), (94, 62), (104, 74), (104, 84), (110, 92), (110, 100), (117, 108), (117, 139)) + " " + \
        rect(94.2, 95.6, 50, 64) + " " + rect(97.2, 98.4, 54, 66)
    cp = sym(146, [(9, 139), (9, 72), (5, 64), (.8, 58), (.6, 50)])
    center = sym(124, [(7, 139), (7, 90), (5, 90), (5, 84), (3, 84), (3, 80)])
    blocks = strip(-30, 230, 139, 37, 4, 14)
    reflect(d, [blocks, ifc, boc, cp, center], 138)
    front(d, [blocks, center, ifc, cp, boc])
    # Bank of China's triangular braces
    d.stroke("light", "M94 139 L117 108 M94 108 L117 139 M94 108 H117 M94 108 L110 92 M94 84 L110 92 M94 84 L104 74", 1.3, line=False)
    if not d.paper:
        d.stroke("light", "M94 139 L117 108 M94 108 L117 139 M94 108 H117 M94 84 L110 92", 1.4)
    d.stroke("light", " ".join(f"M138 {y} H154" for y in range(78, 136, 8)), .9, line=False)
    lit(d, " ".join(rect(x, x + 1.3, 70, 136) for x in (51, 55, 59)), "near")
    junk(d, 26, 104, .52)
    ripples(d, [(110, 150, 16), (150, 160, 20), (160, 146, 12), (120, 174, 12)])


# ================================================================ SHANGHAI
def pearl(cx, base, top) -> str:
    s = (base - top) / 468
    y = lambda m: base - m * s
    legs = (f"M{cx - 15:.1f} {base} L{cx - 5:.1f} {y(80):.1f} H{cx - 1.5:.1f} L{cx - 9:.1f} {base}Z "
            f"M{cx + 15:.1f} {base} L{cx + 5:.1f} {y(80):.1f} H{cx + 1.5:.1f} L{cx + 9:.1f} {base}Z "
            f"M{cx - 1.8:.1f} {base} V{y(70):.1f} H{cx + 1.8:.1f} V{base}Z")
    shaft = rect(cx - 4.4, cx - 1.6, y(330), y(95)) + " " + rect(cx + 1.6, cx + 4.4, y(330), y(95)) + " " + \
        rect(cx - 1.2, cx + 1.2, y(470), y(95))
    spheres = circle(cx, y(93), 10.5) + " " + circle(cx, y(268), 8.2) + " " + circle(cx, y(345), 3.6)
    return legs + " " + shaft + " " + spheres + " " + poly((cx - 1.1, y(345)), (cx - .3, top), (cx + .3, top), (cx + 1.1, y(345)))


def shanghai(d: Drawing):
    d.disc("glow", 176, 70, 11)
    layer(d, "far", towers([(10, 8, 92, "f"), (26, 9, 84, "s"), (88, 9, 82, "f"), (176, 9, 96, "S"), (188, 8, 88, "f")], 128))
    layer(d, "mid", towers([(20, 9, 100, "t"), (84, 8, 92, "s"), (166, 10, 98, "f"), (184, 9, 102, "g")], 128) + " " +
          strip(-30, 230, 128, 41, 8, 16))
    water(d, 128)
    H = 129
    p = pearl(58, H, 50)
    jin = sym(104, [(8, H), (8, 106), (7, 106), (7.6, 104), (6.6, 96), (7, 94), (6, 88), (6.2, 86), (5.2, 81), (5.4, 79),
                    (4.4, 75), (4.4, 72), (2.6, 69), (1.2, 64), (.4, 58)])
    swfc = poly((119, H), (120, 58), (134, 52), (135, H)) + " " + poly((123.5, 63.5), (125, 58), (129.5, 56.5), (131, 61.5), (129.5, 63.5))
    sht = "M141 129 C141.5 96 143 62 146.5 36 L156 30.5 C157 62 159 96 160 129Z"
    blocks = strip(-30, 230, H, 43, 3, 9)
    reflect(d, [blocks, p, jin, swfc, sht], 128, sq=.5)
    front(d, [blocks, swfc, jin, sht, p])
    d.stroke("light", "M145 128 C146 96 148.5 64 151 34", 1.2, line=False)
    d.marks("pop", circle(58, 129 - 93 * (79 / 468), 4.6) + " " + circle(58, 129 - 268 * (79 / 468), 3.6))
    ripples(d, [(98, 140, 16), (140, 146, 18), (170, 138, 12)])
    # the Bund: Custom House clock tower and Peace Hotel
    bund = (rect(-30, 230, 160, 182) + " " + rect(4, 40, 146, 160) + " " + rect(44, 70, 140, 160) + " " + rect(51, 63, 120, 140) +
            " " + poly((51, 120), (54, 114), (60, 114), (63, 120)) + " " + rect(56.4, 57.6, 108, 114) +
            " " + rect(74, 100, 144, 160) + " " + poly((80, 144), (87, 132), (94, 144)) + " " + rect(104, 132, 148, 160) +
            " " + rect(136, 160, 150, 160))
    front(d, [bund])
    d.marks("light", circle(57, 128, 3))
    lit(d, " ".join(rrect(x, 150, 2.4, 4, .5) for x in (8, 15, 22, 29, 48, 55, 62, 78, 85, 92, 108, 115, 122)))
    d.stroke("near", "M-30 165 H230", 1.6, line=False)


# ================================================================ BEIJING
def beijing(d: Drawing):
    d.disc("glow", 120, 54, 13)
    layer(d, "far", "M-30 110 Q20 92 50 100 Q80 86 120 98 Q160 88 230 102 V230 H-30Z", line=True)
    layer(d, "mid", towers([(102, 9, 104, "f"), (116, 8, 110, "s"), (186, 9, 106, "t")], 142) + " " + strip(-30, 230, 142, 51, 10, 20))
    # CCTV headquarters: the leaning loop
    cctv = (poly((100, 143), (108, 90), (150, 90), (157, 118), (149, 118), (146, 143)) + " " +
            poly((113, 131), (117, 103), (137, 103), (135, 131)))
    zun = ("M156 143 C157 116 159 94 159.5 84 C160 66 157 54 155 40 H181 C179 54 176 66 176.5 84 C177 94 179 116 180 143Z")
    blocks = strip(-30, 230, 143, 57, 4, 12)
    front(d, [blocks, cctv, zun])
    shade(d, poly((137, 103), (150, 90), (157, 118), (149, 118), (146, 143), (135, 143), (135, 131)), .16)
    d.stroke("light", " ".join(f"M{x} 44 C{x + .5} 60 {x - 1} 74 {x - 1} 86" for x in (161, 168, 174)), .9, line=False)
    d.band("ground", "M-30 142 H230", line=False)
    # Temple of Heaven: Hall of Prayer for Good Harvests
    cx = 64
    terr = [rect(cx - 52, cx + 52, 160, 168), rect(cx - 44, cx + 44, 152, 160), rect(cx - 36, cx + 36, 144, 152)]
    bodies = [rect(cx - 20, cx + 20, 128, 145), rect(cx - 15, cx + 15, 109, 121), rect(cx - 11, cx + 11, 93, 102)]
    roofs = [f"M{cx - 31} 129 Q{cx - 20} 126 {cx - 16} 117 H{cx + 16} Q{cx + 20} 126 {cx + 31} 129 Q{cx} 133 {cx - 31} 129Z",
             f"M{cx - 25} 110 Q{cx - 15} 107 {cx - 12} 100 H{cx + 12} Q{cx + 15} 107 {cx + 25} 110 Q{cx} 114 {cx - 25} 110Z",
             f"M{cx - 20} 94 Q{cx - 9} 91 {cx - 3} 77 H{cx + 3} Q{cx + 9} 91 {cx + 20} 94 Q{cx} 98 {cx - 20} 94Z"]
    front(d, [(t, "marble") for t in terr] + [(b, "red") for b in bodies] + [(r, "roof", i == 1) for i, r in enumerate(roofs)] +
          [(circle(cx, 73, 3.4) + " " + rect(cx - 1, cx + 1, 66, 72), "gold")])
    d.stroke("marble2", " ".join(f"M{x} {y - 3} V{y}" for y, w in [(160, 52), (152, 44), (144, 36)] for x in range(cx - w + 4, cx + w, 7)), 1.2, line=False)
    d.stroke("gold", f"M{cx - 20} 126 H{cx + 20} M{cx - 15} 107 H{cx + 15} M{cx - 11} 91 H{cx + 11}", 1.6, line=False)
    d.stroke("red2", " ".join(f"M{x} 131 V144" for x in range(cx - 16, cx + 18, 6)), 1.4, line=False)
    d.band("near", "M-30 168 Q60 164 120 168 T230 166")


# ================================================================ SINGAPORE
def supertree(x, base, h, w) -> str:
    top = base - h
    return (f"M{x - 1.8:.1f} {base} L{x - 1.6:.1f} {top + h * .3:.1f} L{x - w:.1f} {top + 2:.1f} Q{x:.1f} {top - 3:.1f} {x + w:.1f} {top + 2:.1f} "
            f"L{x + 1.6:.1f} {top + h * .3:.1f} L{x + 1.8:.1f} {base}Z")


def singapore(d: Drawing):
    d.disc("glow", 150, 44, 12)
    layer(d, "far", towers([(30, 9, 80, "f"), (42, 8, 72, "s"), (54, 10, 66, "t"), (66, 8, 74, "f"), (78, 9, 70, "S"), (90, 8, 82, "r")], 138))
    # Singapore Flyer
    if d.paper:
        d.stroke("mid", circle(26, 98, 21), 2.6, shadow=True, line=False)
        d.stroke("mid", " ".join(f"M26 98 L{26 + 21 * math.cos(a * math.pi / 8):.1f} {98 + 21 * math.sin(a * math.pi / 8):.1f}" for a in range(16)), .8, line=False)
    else:
        d.stroke("mid", circle(26, 98, 21), 2.4)
    layer(d, "mid", poly((16, 138), (26, 98), (36, 138), (32, 138), (26, 110), (20, 138)) + " " +
          towers([(46, 9, 96, "f"), (60, 8, 90, "s"), (72, 9, 100, "f")], 138) + " " + strip(-30, 230, 138, 61, 6, 12))
    water(d, 138)
    mbs = []
    for cx in (106, 128, 150):
        mbs.append(poly((cx - 8, 139), (cx - 6, 82), (cx + 6, 82), (cx + 8, 139)))
    sky = "M92 76 H160 L176 74 L174 78 L162 82 H92Z"
    art = " ".join(f"M{x} 139 Q{x + 2 * k} 128 {x + 7 * k} {y}" + f" L{x + 4 * k} 139Z" for x, k, y in [(76, -1, 120), (78, -.4, 116), (80, .4, 116), (82, 1, 120)])
    art = "M68 139 Q66 128 70 122 L74 132 Q76 120 80 116 Q84 120 86 132 L90 122 Q94 128 92 139Z"
    blocks = strip(-30, 230, 139, 67, 2, 6)
    reflect(d, [blocks, sky, art] + mbs, 138)
    front(d, [blocks, art] + mbs + [sky])
    d.stroke("light", "M106 84 V138 M128 84 V138 M150 84 V138", 1, line=False)
    # Gardens by the Bay supertrees in front
    d.band("near", "M-30 160 Q60 154 120 158 T230 156", line=False)
    trees = [supertree(x, 170, h, w) for x, h, w in [(132, 50, 9), (152, 62, 11), (172, 46, 8), (188, 54, 9)]]
    front(d, [(t, "tree", i == 1) for i, t in enumerate(trees)])
    d.stroke("tree2", " ".join(f"M{x} {170 - h + 4} V168" for x, h in [(132, 50), (152, 62), (172, 46), (188, 54)]), 1, line=False)
    ripples(d, [(30, 148, 14), (80, 152, 18), (20, 160, 12)])
    d.band("deep", "M-30 172 Q100 166 230 172", line=False)


# ================================================================ BANGKOK
def prang(cx, base, h, w) -> str:
    """Khmer-style prang (Wat Arun): stepped base, swelling corncob tower and spire."""
    pts_r = [(w, base), (w, base - h * .12), (w * .8, base - h * .12), (w * .8, base - h * .22), (w * .62, base - h * .22),
             (w * .62, base - h * .3)]
    for i in range(8):
        t = i / 8
        y = base - h * (.3 + .55 * t)
        hw = w * .56 * (1 - t ** 1.4) + w * .06
        pts_r += [(hw + w * .04, y), (hw, y - h * .055)]
    pts_r += [(w * .05, base - h * .9), (w * .02, base - h)]
    return sym(cx, pts_r)


def bangkok(d: Drawing):
    d.disc("glow", 76, 82, 32)
    layer(d, "far", towers([(130, 9, 70, "f"), (144, 8, 80, "s"), (182, 9, 84, "f"), (196, 8, 92, "S")], 138))
    mahanakhon = poly((158, 138), (158, 60), (164, 56), (166, 64), (170, 62), (170, 74), (168, 80), (172, 88), (172, 138))
    layer(d, "mid", mahanakhon + " " + towers([(124, 9, 96, "f"), (140, 8, 104, "f"), (184, 9, 100, "t")], 138) + " " +
          strip(80, 230, 138, 71, 6, 14))
    water(d, 138)
    temple = (prang(76, 139, 98, 34) + " " + prang(30, 139, 46, 14) + " " + prang(122, 139, 46, 14) + " " +
              rect(10, 142, 132, 139) + " " + strip(-30, 230, 139, 79, 2, 5))
    reflect(d, [temple], 138)
    front(d, [temple])
    d.stroke("far", "M48 127.2 H104 M53 117.4 H99 M58 109.6 H94", 1.3, line=False)
    # long-tail boat
    lt = "M96 160 H162 L172 150 L170 158 L162 166 H104Z M150 160 V152 H162 V160Z"
    front(d, [(lt, "hero", True)])
    d.stroke("deep", "M100 162 L84 172", 1.6)
    ripples(d, [(30, 152, 18), (60, 166, 14), (120, 172, 22), (140, 146, 12)])


# ================================================================ KUALA LUMPUR
def petronas(cx, base, top) -> list:
    s = (base - top) / 174
    tiers = [(16, 82), (13.5, 66), (11, 55), (9, 47), (7, 40)]
    y = lambda v: base - (182 - v) * s
    prof = [(16 * s, base)]
    prev = 182
    for hw, t in tiers:
        prof += [(hw * s, y(t + 2)), (hw * s - 1.1 * s, y(t))]
    prof += [(4.5 * s, y(41)), (2 * s, y(26)), (.9 * s, y(26)), (.5 * s, top)]
    return [sym(cx, prof)]


def kuala_lumpur(d: Drawing):
    d.disc("glow", 176, 70, 11)
    layer(d, "far", towers([(16, 9, 100, "f"), (94, 9, 98, "s"), (178, 9, 104, "f"), (190, 8, 96, "S")], 140))
    # Bukit Nanas hill
    layer(d, "mid", "M-30 140 Q10 132 30 128 Q50 122 70 128 Q90 134 110 136 L230 136 V230 H-30Z" + " " +
          towers([(100, 8, 112, "f"), (172, 9, 108, "t")], 140) + " " + strip(80, 230, 140, 83, 8, 16))
    d.band("ground", "M-30 141 H230", line=False)
    kl = sym(52, [(5.6, 127), (2.8, 116), (2.4, 66), (4.6, 64), (7.2, 58), (7.6, 54), (6.2, 52), (6.2, 50), (5, 46), (2, 44), (1.4, 40), (.5, 26)])
    t1 = petronas(112, 142, 30)[0]
    t2 = petronas(148, 142, 30)[0]
    bridge = rect(116, 144, 92, 97) + " " + poly((128, 97), (130, 97), (124, 108), (122, 108)) + " " + poly((130, 97), (132, 97), (138, 108), (136, 108))
    blocks = strip(-30, 230, 142, 89, 3, 9)
    front(d, [blocks, kl, t1, t2, (bridge, "deep", True)])
    shade(d, sym(118, [(4, 141), (4, 52)]) + " " + sym(154, [(4, 141), (4, 52)]), .14)
    d.stroke("light", " ".join(f"M{x - 8} {y} H{x + 8}" for x in (112, 148) for y in range(104, 140, 8)), .8, line=False)
    lit(d, rect(46, 58, 55.5, 57) , "glow2")
    d.band("near", "M-30 156 Q40 150 100 156 T230 154")
    for x, h in [(14, 30), (34, 24), (176, 28), (192, 22)]:
        palm(d, x, 168, h, 3 if x < 100 else -3, "deep", .8, line=False)
    d.band("deep", "M-30 168 Q100 162 230 168", line=False)


# ================================================================ TAIPEI
def taipei101(cx, base, top) -> str:
    k = (base - top) / 108
    pts = [(12, base), (10, base - 22 * k), (8, base - 26 * k)]
    y = base - 26 * k
    for i in range(8):
        y1 = y - 7.5 * k
        pts += [(7.2, y), (10.2, y1), (8.0, y1)]
        y = y1
    pts += [(6, y), (6, y - 3 * k), (4.6, y - 3 * k), (4.6, y - 6 * k), (3, y - 6 * k), (3, y - 9 * k), (1.2, y - 9 * k), (.5, top)]
    return sym(cx, pts)


def taipei(d: Drawing):
    d.disc("glow", 64, 56, 14)
    layer(d, "far", "M-30 112 Q20 92 60 100 Q100 82 140 96 Q180 86 230 100 V230 H-30Z", line=True)
    layer(d, "mid", towers([(84, 8, 106, "f"), (98, 9, 112, "s"), (150, 9, 104, "f"), (164, 8, 110, "S"), (180, 10, 114, "f")], 140) +
          " " + strip(-30, 230, 140, 91, 8, 16))
    t = taipei101(124, 141, 30)
    blocks = strip(60, 230, 141, 97, 4, 10)
    front(d, [blocks, t])
    d.stroke("light", "M124 34 V44", 1, line=False)
    # Elephant Mountain in front, and Chiang Kai-shek Memorial Hall on the left
    d.band("near", "M-30 150 Q30 128 70 140 Q100 150 140 154 Q180 156 230 150")
    cx = 46
    hall = [(rect(cx - 30, cx + 30, 150, 156), "marble"), (rect(cx - 24, cx + 24, 144, 150), "marble"),
            (rect(cx - 16, cx + 16, 122, 144), "marble"),
            (f"M{cx - 22} 124 Q{cx - 14} 120 {cx - 12} 114 H{cx + 12} Q{cx + 14} 120 {cx + 22} 124Z", "roof", True),
            (rect(cx - 10, cx + 10, 108, 115), "marble"),
            (f"M{cx - 16} 110 Q{cx - 8} 106 {cx - 6} 98 H{cx + 6} Q{cx + 8} 106 {cx + 16} 110Z", "roof", True),
            (rect(cx - .8, cx + .8, 92, 99), "gold")]
    front(d, hall)
    d.marks("roof", rect(cx - 5, cx + 5, 130, 144))
    d.stroke("marble2", f"M{cx - 30} 153 H{cx + 30} M{cx - 24} 147 H{cx + 24}", 1, line=False)
    d.band("deep", "M-30 162 Q60 156 120 160 T230 158")
    for x, y, r in [(100, 160, 9), (114, 158, 7), (150, 160, 10), (170, 156, 8), (190, 160, 9)]:
        d.shape("deep", circle(x, y, r), line=False)


# ================================================================ HANOI
def hanoi(d: Drawing):
    d.disc("glow", 150, 52, 13)
    layer(d, "far", towers([(26, 9, 66, "S"), (60, 8, 90, "f"), (74, 9, 84, "s"), (172, 9, 92, "f"), (186, 8, 98, "f")], 128) +
          " " + sym(42, [(6, 128), (6, 50), (4.5, 50), (4.5, 44)]))
    trees = " ".join(circle(x, y, r) for x, y, r in [(-6, 120, 14), (14, 118, 12), (32, 122, 12), (54, 120, 13), (76, 122, 11), (96, 118, 13),
                                                     (118, 122, 12), (140, 118, 13), (162, 121, 12), (184, 118, 13), (204, 122, 12)])
    layer(d, "mid", trees + " " + rect(-30, 230, 120, 130))
    water(d, 130)
    # Turtle Tower on its islet
    cx = 132
    tt = (rect(cx - 18, cx + 18, 116, 137) + " " + rect(cx - 13, cx + 13, 100, 117) + " " + rect(cx - 8, cx + 8, 88, 101) +
          " " + pagoda_roof(cx, 88, 13, 6) + " " + poly((cx - 3, 82), (cx, 74), (cx + 3, 82)) +
          " " + rect(cx - 20, cx + 20, 114, 117.5) + " " + rect(cx - 15, cx + 15, 98.5, 101.5))
    islet = "M98 140 Q112 132 132 134 Q152 132 166 140Z"
    reflect(d, [tt, islet], 140, op=.2)
    d.band("far", "M-30 140 H230", line=False)
    front(d, [tt, (islet, "near")])
    d.marks("far", " ".join(arch(x, 122, 6, 15) for x in (cx - 14, cx - 3, cx + 8)) + " " +
            " ".join(arch(x, 104, 5, 11) for x in (cx - 9, cx + 4)) + " " + arch(cx - 2.5, 91, 5, 8))
    # The Huc bridge
    bridge = "M-30 146 Q30 116 92 146 L92 152 Q30 126 -30 152Z"
    rails = " ".join(f"M{x} {146 - 30 * (1 - ((x - 31) / 61) ** 2):.1f} V{146 - 30 * (1 - ((x - 31) / 61) ** 2) - 8:.1f}" for x in range(-14, 92, 8))
    d.stroke("bridge", rails, 1.4)
    d.stroke("bridge", "M-30 138 Q30 108 92 138", 2.2)
    front(d, [(bridge, "bridge", True)])
    d.limb("bridge", "M8 152 V180 M60 150 V176", 3)
    ripples(d, [(110, 152, 18), (150, 162, 22), (176, 148, 12), (90, 176, 16)])


# ================================================================ HO CHI MINH CITY
def ho_chi_minh(d: Drawing):
    d.disc("glow", 64, 54, 13)
    layer(d, "far", towers([(84, 9, 90, "f"), (96, 8, 98, "s"), (178, 9, 92, "S"), (192, 9, 100, "f")], 138))
    layer(d, "mid", towers([(92, 9, 112, "f"), (128, 9, 104, "t"), (172, 10, 108, "f")], 138) + " " + strip(-30, 230, 138, 101, 8, 16))
    water(d, 138)
    bitexco = ("M98 139 C97 120 97 104 99 92 C100 86 104 80 112 70 C114 78 116 92 116 104 C116 116 115 128 114 139Z "
               "M86 98 Q86 94 98 94 H101 V100 H98 Q86 100 86 98Z")
    l81 = (rect(144, 160, 76, 139) + " " + rect(140, 146, 96, 139) + " " + rect(158, 164, 88, 139) + " " + rect(148, 156, 48, 80) +
           " " + rect(150.5, 153.5, 40, 50) + " " + rect(151.5, 152.5, 32, 42))
    blocks = strip(-30, 230, 139, 103, 3, 9)
    reflect(d, [blocks, bitexco, l81], 138)
    front(d, [blocks, l81, bitexco])
    d.stroke("light", "M144 80 V137 M148 50 V137 M156 50 V137 M160 80 V137", .9, line=False)
    d.stroke("light", "M106 80 C104 96 104 120 105 136", 1, line=False)
    # Notre-Dame Cathedral Basilica in front on the river bank
    d.band("deep", "M-30 156 Q30 150 70 152 Q120 158 230 156", line=False)
    cx = 46
    cath = (rect(cx - 26, cx + 26, 128, 160) + " " + poly((cx - 10, 128), (cx, 116), (cx + 10, 128)) +
            " " + rect(cx - 26, cx - 13, 102, 160) + " " + rect(cx + 13, cx + 26, 102, 160) +
            " " + poly((cx - 27, 102), (cx - 19.5, 72), (cx - 12, 102)) + " " + poly((cx + 12, 102), (cx + 19.5, 72), (cx + 27, 102)))
    front(d, [(cath, "brick", False)])
    d.marks("deep", circle(cx, 136, 4.5) + " " + arch(cx - 4, 146, 8, 14) + " " + arch(cx - 22, 112, 5, 9) + " " + arch(cx + 17, 112, 5, 9) +
            " " + arch(cx - 22, 134, 5, 12) + " " + arch(cx + 17, 134, 5, 12))
    d.shape("hero", "M110 168 H156 L164 160 L160 170 L150 174 H116Z M120 168 V160 H140 V168Z", spot=True)
    ripples(d, [(90, 150, 14), (160, 148, 16), (60, 176, 14)])


# ================================================================ MUMBAI
def mumbai(d: Drawing):
    d.disc("glow", 160, 58, 13)
    layer(d, "far", towers([(110, 9, 72, "f"), (122, 8, 80, "s"), (172, 9, 76, "t"), (186, 8, 86, "f"), (196, 9, 94, "S")], 140))
    layer(d, "mid", towers([(116, 9, 96, "f"), (180, 9, 98, "f")], 140) + " " + strip(-30, 230, 140, 111, 8, 16))
    water(d, 140)
    # Taj Mahal Palace hotel
    taj = (rect(98, 174, 108, 141) + " " + rect(126, 146, 98, 108) + " " + dome(136, 99, 11, 15) + " " + rect(135.3, 136.7, 78, 86) +
           " " + " ".join(rect(x - 3.5, x + 3.5, 100, 108) + " " + dome(x, 100.5, 4, 6) for x in (100, 114, 158, 172)))
    # Gateway of India
    gx = 52
    gate = (rect(gx - 34, gx + 34, 104, 141) + " " + arch(gx - 13, 108, 26, 34) +
            " " + " ".join(rect(x - 5, x + 5, 92, 104) + " " + dome(x, 92.5, 5.6, 7) + " " + rect(x - .6, x + .6, 81, 86) for x in (gx - 28, gx - 12, gx + 12, gx + 28)) +
            " " + rect(gx - 9, gx + 9, 98, 104) + " " + dome(gx, 98.5, 8, 6))
    blocks = strip(70, 230, 141, 113, 3, 8)
    reflect(d, [blocks, taj, gate], 140)
    front(d, [blocks, taj])
    d.marks("dome", dome(136, 99, 11, 15))
    lit(d, " ".join(rrect(x, y, 2.4, 3.4, .5) for x in range(102, 172, 6) for y in (114, 124, 133)))
    front(d, [gate])
    d.stroke("far", f"M{gx - 34} 120 H{gx - 15} M{gx + 15} 120 H{gx + 34} M{gx - 25} 104.5 H{gx + 25}", 1.3, line=False)
    d.marks("far", " ".join(arch(x - 3, 125, 6, 14) for x in (gx - 26, gx + 26)))
    # a little sailing boat
    d.shape("hull", "M120 168 H160 L154 175 H126Z")
    d.shape("light", "M140 166 V140 L156 166Z", spot=True)
    d.shape("light", "M138 166 V146 L128 166Z")
    ripples(d, [(40, 154, 16), (90, 162, 18), (20, 172, 12), (170, 152, 14)])


# ================================================================ DELHI
def qutub(cx, base, top) -> str:
    h = base - top
    pts = []
    bands = [(0, 7.2), (.32, 6.0), (.58, 5.0), (.78, 4.2), (.92, 3.4)]
    for i, (t, hw) in enumerate(bands):
        y0 = base - h * t
        t1 = bands[i + 1][0] if i + 1 < len(bands) else 1.0
        y1 = base - h * t1
        pts += [(hw, y0), (hw * .88, y1 + 2.2), (hw * 1.05 + .9, y1 + 2.2), (hw * 1.05 + .9, y1)]
    pts[-2:] = [(3.6, top + 3), (1.4, top + 1), (.4, top)]
    return sym(cx, pts)


def india_gate(cx, base, top) -> str:
    return (rect(cx - 22, cx + 22, top + 30, base) + " " + arch(cx - 9, top + 44, 18, base - top - 44) +
            " " + rect(cx - 18, cx + 18, top + 18, top + 31) + " " + rect(cx - 13, cx + 13, top + 10, top + 19) +
            " " + f"M{cx - 10} {top + 10.5} Q{cx} {top - 1} {cx + 10} {top + 10.5}Z" + " " + rect(cx - 25, cx + 25, top + 28, top + 32))


def lotus_temple(cx, base) -> str:
    s = ""
    for dx, h, w in [(-24, 18, 9), (24, 18, 9), (-15, 28, 10), (15, 28, 10), (-6, 36, 9), (6, 36, 9), (0, 40, 8)]:
        x = cx + dx
        lean = dx * .25
        s += f"M{x - w:.1f} {base} Q{x - w + lean * .3:.1f} {base - h * .6:.1f} {x + lean:.1f} {base - h:.1f} Q{x + w + lean * .3:.1f} {base - h * .6:.1f} {x + w:.1f} {base}Z "
    return s + rect(cx - 34, cx + 34, base - 3, base + 1)


def delhi(d: Drawing):
    d.disc("glow", 100, 62, 22)
    layer(d, "far", towers([(140, 9, 104, "f"), (180, 9, 98, "s"), (196, 8, 106, "f")], 140) + " " + dome(176, 120, 14, 12) + " " + rect(175, 177, 102, 110))
    trees = " ".join(circle(x, 132, r) for x, r in [(-10, 12), (10, 10), (62, 9), (78, 11), (124, 10), (140, 12), (190, 11), (212, 10)])
    layer(d, "mid", trees + " " + rect(-30, 230, 130, 140))
    water(d, 140)
    gate = india_gate(100, 141, 54)
    q = qutub(36, 141, 40)
    lotus = lotus_temple(162, 141)
    blocks = rect(-30, 230, 137, 141)
    reflect(d, [blocks, gate, q, lotus], 140)
    front(d, [blocks, q, lotus, gate])
    d.stroke("far", "M78 86 H122", 1.2, line=False)
    d.stroke("far", " ".join(f"M{36 - 8} {y} H{36 + 8}" for y in (124, 106, 92)), 1.0, line=False)
    d.stroke("far", "M146 141 Q150 124 156 113 M178 141 Q174 124 168 113 M162 141 V104", 1.0, line=False)
    ripples(d, [(30, 152, 16), (110, 158, 20), (160, 150, 14), (70, 172, 14)])
    d.band("near", "M-30 176 H230")


# ================================================================ KATHMANDU
FLAGS = {"fb": "#3E6FB0", "fw": "#F4F1EA", "fr": "#C8372D", "fg": "#3F8F5A", "fy": "#E9B949"}


def flag_string(d: Drawing, x0, y0, x1, y1, sag, n, size=3.2):
    roles = ["fb", "fw", "fr", "fg", "fy"]
    cx, cy = (x0 + x1) / 2, max(y0, y1) + sag
    d.stroke("deep", f"M{x0} {y0} Q{cx} {cy} {x1} {y1}", .9, line=False)
    for i in range(1, n + 1):
        t = i / (n + 1)
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1
        d.shape(roles[i % 5], rect(x - size / 2, x + size / 2, y, y + size * 1.2), shadow=False, line=False)


def kathmandu(d: Drawing):
    d.disc("glow", 46, 50, 12)
    peaks = "M-30 100 L10 80 L28 90 L56 58 L76 80 L98 66 L122 88 L150 54 L176 82 L196 70 L230 92 V230 H-30Z"
    layer(d, "far", peaks, line=True)
    d.shape("light", "M56 58 L66 70 L60 69 L55 74 L50 66 L46 70Z M150 54 L161 68 L155 66 L149 72 L143 65 L139 68Z "
                     "M98 66 L106 75 L100 74 L96 78 L91 73Z", shadow=False, line=False)
    # Swayambhunath on its hill
    layer(d, "mid", "M-30 140 Q0 120 30 112 Q50 104 68 112 Q100 128 140 130 Q190 128 230 136 V230 H-30Z" + " " +
          dome(48, 107, 9, 7) + " " + poly((45, 101), (46.5, 90), (49.5, 90), (51, 101)) + " " + strip(80, 230, 138, 121, 6, 12))
    d.band("ground", "M-30 140 Q100 136 230 140", line=False)
    # a Newari tiered temple (Durbar Square)
    cx = 40
    steps = " ".join(rect(cx - w, cx + w, y - 6, y) for w, y in [(30, 172), (26, 166), (22, 160), (18, 154)])
    temple = [steps, rect(cx - 12, cx + 12, 132, 148), pagoda_roof(cx, 132, 26, 7), rect(cx - 9, cx + 9, 118, 128),
              pagoda_roof(cx, 118, 21, 7), rect(cx - 6, cx + 6, 106, 114), pagoda_roof(cx, 106, 16, 7),
              poly((cx - 1.5, 99), (cx, 90), (cx + 1.5, 99))]
    front(d, temple)
    d.marks("gold", poly((cx - 2, 99), (cx, 90), (cx + 2, 99)))
    # Boudhanath stupa
    bx = 130
    base_t = rect(bx - 56, bx + 56, 166, 174) + " " + rect(bx - 48, bx + 48, 158, 166) + " " + rect(bx - 40, bx + 40, 151, 158)
    st_dome = dome(bx, 152, 32, 22)
    harmika = rect(bx - 9, bx + 9, 115, 131)
    spire = sym(bx, [(8, 115), (2.4, 90)]) + " " + f"M{bx - 7} 90 Q{bx} 82 {bx + 7} 90Z" + " " + rect(bx - .8, bx + .8, 76, 84)
    flag_string(d, bx, 80, bx - 64, 152, 0, 9)
    flag_string(d, bx, 80, bx + 66, 150, 0, 9)
    front(d, [(base_t, "stupa"), (st_dome, "stupa"), (harmika, "gold", True), (spire, "gold")])
    d.stroke("gold2", " ".join(f"M{bx - 7.5 + i * .55:.1f} {113 - i * 2.2:.1f} H{bx + 7.5 - i * .55:.1f}" for i in range(11)), .9, line=False)
    d.marks("deep", f"M{bx - 7} 123 q2.5 -3 5 0 q-2.5 2 -5 0Z M{bx + 2} 123 q2.5 -3 5 0 q-2.5 2 -5 0Z M{bx - .6} 125 q1.6 2 0 4 q2 0 1.2 -4Z")
    d.stroke("gold2", f"M{bx - 32} 152 H{bx + 32}", 1.4, line=False)


# ================================================================ COLOMBO
def colombo(d: Drawing):
    d.disc("glow", 152, 52, 13)
    layer(d, "far", towers([(96, 9, 88, "f"), (108, 8, 82, "s"), (176, 9, 92, "f"), (190, 8, 100, "S")], 138))
    layer(d, "mid", towers([(18, 9, 110, "f"), (90, 9, 106, "t"), (184, 9, 104, "f")], 138) + " " + strip(-30, 230, 138, 131, 8, 16))
    water(d, 138)
    stem = sym(66, [(6, 139), (3, 118), (2.6, 76)])
    bud = (f"M66 52 C58 58 54 66 55 74 L58 79 H74 L77 74 C78 66 74 58 66 52Z "
           f"M58 79 L54 72 L57 82 H75 L78 72 L74 79Z")
    spire = poly((64.6, 54), (65.6, 30), (66.4, 30), (67.4, 54))
    wtc = rect(112, 124, 92, 139) + " " + rect(128, 140, 92, 139)
    altair = poly((150, 139), (152, 86), (160, 86), (160, 139)) + " " + poly((160, 139), (166, 92), (174, 94), (170, 139))
    blocks = strip(-30, 230, 139, 137, 3, 9)
    reflect(d, [blocks, stem, bud, wtc, altair], 138)
    front(d, [blocks, wtc, altair, (stem, "stem"), (spire, "stem"), (bud, "bud", True)])
    d.stroke("lotus2", "M66 54 V78 M60 60 Q60 70 62 78 M72 60 Q72 70 70 78", 1, line=False)
    lit(d, " ".join(rect(x, x + 1.6, 96, 136) for x in (115, 120, 131, 136)), "near")
    # Galle Face: palms on the shore and the ocean
    d.band("near", "M-30 164 Q60 158 120 162 T230 160", line=False)
    palm(d, 22, 166, 44, 6, "deep", 1.0)
    palm(d, 182, 166, 36, -5, "deep", .9)
    ripples(d, [(80, 150, 18), (130, 152, 14), (40, 146, 12), (160, 146, 14)])
    d.band("ground", "M-30 168 Q100 162 230 170")


# ================================================================ MANILA
def manila(d: Drawing):
    d.disc("glow", 140, 132, 30)
    layer(d, "far", towers([(16, 9, 80, "f"), (28, 8, 72, "s"), (40, 9, 86, "f"), (52, 8, 78, "S"), (64, 9, 90, "t")], 132))
    layer(d, "mid", towers([(22, 9, 100, "f"), (58, 9, 104, "f")], 132) + " " + strip(-30, 100, 132, 141, 6, 12))
    water(d, 132)
    # Manila Cathedral: dome with lantern and the bell tower
    cx = 52
    cath = (rect(cx - 30, cx + 18, 104, 133) + " " + poly((cx - 30, 104), (cx - 6, 92), (cx + 18, 104)) + " " +
            rect(cx + 2, cx + 18, 86, 104) + " " + dome(cx + 10, 87, 11, 16) + " " + rect(cx + 7.5, cx + 12.5, 63, 72) + " " + dome(cx + 10, 64, 3.2, 4) +
            " " + rect(cx - 40, cx - 26, 90, 133) + " " + rect(cx - 38, cx - 28, 76, 90) + " " + dome(cx - 33, 77, 5.5, 7))
    blocks = strip(-30, 100, 133, 143, 3, 8)
    reflect(d, [blocks, cath], 132)
    front(d, [blocks, cath])
    d.marks("far", circle(cx - 6, 112, 3.6) + " " + arch(cx - 9, 120, 6, 13) + " " + arch(cx - 36, 94, 6, 9) + " " + arch(cx - 36, 112, 6, 10))
    # reflection of the setting sun
    d.stroke("glow2", "M118 140 h44 M124 148 h32 M130 156 h20 M134 164 h12", 2.2, line=False)
    # a bangka outrigger
    bk = ("M100 166 Q132 174 164 164 L170 158 L160 168 Q132 178 104 170Z M118 166 L130 128 L150 164Z")
    front(d, [(bk, "deep")])
    d.stroke("deep", "M96 176 H176 M112 166 V176 M156 165 V176", 1.6)
    palm(d, 182, 182, 74, -8, "deep", 1.1)
    palm(d, 10, 186, 44, 6, "deep", .9)
    ripples(d, [(30, 150, 14), (70, 160, 16), (180, 144, 12)])


# ================================================================ JAKARTA
def jakarta(d: Drawing):
    d.disc("glow", 152, 50, 12)
    layer(d, "far", towers([(20, 9, 82, "f"), (126, 9, 72, "t"), (140, 8, 86, "s"), (168, 9, 60, "p"), (184, 8, 84, "f"), (196, 9, 94, "S")], 140))
    layer(d, "mid", towers([(30, 9, 104, "f"), (134, 10, 98, "f"), (154, 9, 106, "s"), (176, 9, 100, "r")], 140) + " " + strip(-30, 230, 140, 151, 10, 18))
    d.band("ground", "M-30 141 H230", line=False)
    # Istiqlal Mosque dome and minaret
    ist = dome(46, 142, 26, 18) + " " + rect(18, 74, 136, 142) + " " + rect(43.5, 48.5, 116, 126) + " " + \
        sym(84, [(3.2, 142), (2.6, 64), (3.6, 62), (3.6, 58), (2, 56), (.4, 44)])
    blocks = strip(-30, 230, 143, 157, 3, 9)
    front(d, [blocks, ist])
    # Monas
    cx = 116
    monas = (rect(cx - 44, cx + 44, 154, 164) + " " + poly((cx - 34, 154), (cx - 30, 146), (cx + 30, 146), (cx + 34, 154)) +
             " " + sym(cx, [(7, 147), (3.8, 66), (8.5, 64), (6, 58), (3, 58)]))
    flame = f"M{cx - 4} 58 Q{cx - 6} 50 {cx - 1} 44 Q{cx - 1} 48 {cx + 1} 49 Q{cx + 1} 40 {cx - 1} 34 Q{cx + 8} 40 {cx + 6} 52 Q{cx + 6} 55 {cx + 4} 58Z"
    d.band("near", "M-30 156 Q60 150 120 154 T230 152", line=False)
    front(d, [(monas, "stone"), (flame, "gold", True)])
    shade(d, sym(cx + 2.6, [(2.4, 146), (1.2, 66)]), .12)
    d.stroke("stone2", f"M{cx - 44} 158 H{cx + 44}", 1.2, line=False)
    d.band("deep", "M-30 166 Q100 160 230 166")
    for x, y, r in [(10, 162, 9), (26, 166, 8), (184, 162, 10), (198, 166, 8)]:
        d.shape("deep", circle(x, y, r), line=False)


# ================================================================ MACAU
def macau(d: Drawing):
    d.disc("glow", 104, 46, 12)
    layer(d, "far", "M-30 120 Q20 108 50 112 Q80 102 110 112 Q160 100 230 114 V230 H-30Z", line=True)
    layer(d, "mid", towers([(92, 8, 106, "f"), (186, 9, 104, "f"), (198, 8, 110, "S")], 138) + " " + strip(60, 230, 138, 161, 8, 16))
    water(d, 138)
    tower = sym(152, [(7, 139), (3.4, 120), (3, 76), (6, 74), (11, 70), (11, 66), (7, 64), (5, 60), (3, 60), (1.6, 58), (.9, 40), (.4, 36)])
    lisboa = ("M110 139 C108 124 106 112 108 100 C110 88 114 82 112 74 L108 62 L113 68 L114 58 L118 68 L121 56 L123 68 L127 58 L128 68 "
              "L133 62 L129 74 C127 82 131 88 133 100 C135 112 133 124 131 139Z")
    blocks = strip(72, 230, 139, 163, 3, 9)
    reflect(d, [blocks, tower, lisboa], 138)
    front(d, [blocks, lisboa, tower])
    d.stroke("light", "M121 70 V136", 1, line=False)
    lit(d, rect(141.5, 162.5, 67.4, 69), "glow2")
    # Governor Nobre de Carvalho bridge with its hump
    br = "M60 152 Q120 150 150 142 Q170 136 182 142 Q200 150 240 150 V154 Q200 154 182 146 Q170 140 150 146 Q120 154 60 156Z"
    front(d, [br])
    d.stroke("deep", " ".join(f"M{x} 154 V164" for x in range(70, 230, 18)), 2, line=False)
    ripples(d, [(90, 170, 18), (150, 166, 16), (180, 176, 12)])
    # Ruins of St. Paul's on its stairway
    d.shape("near", "M-30 150 Q20 140 60 148 Q80 156 86 190 H-30Z", line=False)
    cx = 38
    ruins = (rect(cx - 26, cx + 26, 116, 160) + " " + rect(cx - 22, cx + 22, 100, 116) + " " + rect(cx - 16, cx + 16, 86, 100) +
             " " + poly((cx - 12, 86), (cx, 70), (cx + 12, 86)) + " " + poly((cx - 36, 186), (cx - 26, 160), (cx + 26, 160), (cx + 36, 186)))
    front(d, [(ruins, "stone")])
    d.marks("stone2", arch(cx - 5, 140, 10, 20) + " " + arch(cx - 19, 144, 7, 16) + " " + arch(cx + 12, 144, 7, 16) +
            " " + arch(cx - 4, 120, 8, 12) + " " + arch(cx - 17, 122, 6, 10) + " " + arch(cx + 11, 122, 6, 10) +
            " " + circle(cx, 93, 3.5) + " " + arch(cx - 13, 104, 5, 8) + " " + arch(cx + 8, 104, 5, 8))
    d.stroke("stone2", " ".join(f"M{cx - 26 - i * 2.4:.1f} {164 + i * 5} H{cx + 26 + i * 2.4:.1f}" for i in range(5)) +
             f" M{cx - 26} 116 H{cx + 26} M{cx - 22} 100 H{cx + 22}", 1.2, line=False)


# ================================================================ catalogue
LAYER_CHECKS = [("deep", "sky"), ("deep", "mid"), ("deep", "far"), ("mid", "sky"), ("mid", "far"), ("deep", "glow")]
LAYER_FIXES = {
    "deep": ["light"],
    "mid": ["near", "#6E7BAA", "#7C88B5"],
    "glow": ["glow2", "light", "pop"],
}


def city(cid, activity, title, fn, palettes=None, checks=(), overrides=None, fixes=None):
    return Concept(cid, activity, title, fn, palettes=list(palettes or ["golden", "coastal", "meadow", "blush", "dusk"]),
                   overrides=dict(overrides or {}), checks=LAYER_CHECKS + list(checks), fixes={**LAYER_FIXES, **(fixes or {})})


CASTLE = {"castle": "#F4F1EA", "roof": "#5F8F7A", "castle_stone": "#9A9488", "castle_stone2": "#6F6A60", "gold": "#E2B04A"}
HEAVEN = {"roof": "#2F5F9E", "red": "#B8322A", "red2": "#8C2219", "gold": "#EDB12E", "marble": "#F4F0E8", "marble2": "#C9C1B3"}
CKS = {"marble": "#F4F0E8", "marble2": "#C9C1B3", "roof": "#2F5F9E", "gold": "#E2B04A"}
STUPA = {"stupa": "#F7F3EA", "gold": "#E2B04A", "gold2": "#A87A22", **FLAGS}
LOTUS = {"stem": "#4E8F6A", "bud": "#8E5BA8", "lotus2": "#5E3A75"}

CONCEPTS = [
    city("sky-tokyo", "skyline-tokyo", "Tokyo", tokyo, overrides={"tt": "#E4572E"},
         checks=[("tt", "far"), ("tt", "mid"), ("tt", "deep")]),
    city("sky-kyoto", "skyline-kyoto", "Kyoto", kyoto, checks=[("pop", "mid"), ("deep", "near")],
         fixes={"pop": ["hero", "#D9573B"]}),
    city("sky-osaka", "skyline-osaka", "Osaka", osaka, overrides=CASTLE,
         checks=[("castle", "near"), ("castle", "mid"), ("roof", "castle"), ("castle_stone", "near")], fixes={"near": ["deep", "mid"]}),
    city("sky-seoul", "skyline-seoul", "Seoul", seoul, checks=[("hero2", "deep")]),
    city("sky-hong-kong", "skyline-hong-kong", "Hong Kong", hong_kong, ["coastal", "meadow", "blush", "dusk"],
         overrides={"sail": "#D9673E", "sail2": "#9C3F22", "hull": "#6A3E22"}, checks=[("sail", "far"), ("hull", "far")]),
    city("sky-shanghai", "skyline-shanghai", "Shanghai", shanghai),
    city("sky-beijing", "skyline-beijing", "Beijing", beijing, overrides=HEAVEN,
         checks=[("roof", "sky"), ("marble", "ground"), ("red", "mid"), ("deep", "ground")],
         fixes={"ground": ["mid", "near"]}),
    city("sky-singapore", "skyline-singapore", "Singapore", singapore, ["coastal", "meadow", "blush", "dusk"],
         overrides={"tree": "#B5536B", "tree2": "#7E3248"}, checks=[("tree", "near"), ("tree", "far")]),
    city("sky-bangkok", "skyline-bangkok", "Bangkok", bangkok, checks=[("hero", "far")], fixes={"hero": ["pop", "hero2"]}),
    city("sky-kuala-lumpur", "skyline-kuala-lumpur", "Kuala Lumpur", kuala_lumpur, checks=[("deep", "ground")],
         fixes={"ground": ["mid", "near"]}),
    city("sky-taipei", "skyline-taipei", "Taipei", taipei, overrides=CKS, checks=[("marble", "near"), ("deep", "near"), ("roof", "mid")]),
    city("sky-hanoi", "skyline-hanoi", "Hanoi", hanoi, overrides={"bridge": "#C8372D"},
         checks=[("bridge", "far"), ("bridge", "mid"), ("near", "far")], fixes={"near": ["deep", "mid"]}),
    city("sky-ho-chi-minh", "skyline-ho-chi-minh", "Ho Chi Minh City", ho_chi_minh, overrides={"brick": "#C0623F"},
         checks=[("brick", "deep"), ("brick", "mid"), ("hero", "far")], fixes={"hero": ["pop", "hero2"]}),
    city("sky-mumbai", "skyline-mumbai", "Mumbai", mumbai,
         overrides={"dome": "#C2483A", "hull": "#6A3E22"}, checks=[("dome", "deep"), ("light", "far")]),
    city("sky-delhi", "skyline-delhi", "Delhi", delhi),
    city("sky-kathmandu", "skyline-kathmandu", "Kathmandu", kathmandu, overrides=STUPA,
         checks=[("stupa", "mid"), ("stupa", "ground"), ("light", "far"), ("deep", "ground")], fixes={"ground": ["near", "mid"]}),
    city("sky-colombo", "skyline-colombo", "Colombo", colombo, overrides=LOTUS,
         checks=[("bud", "sky"), ("stem", "far"), ("bud", "mid")]),
    city("sky-manila", "skyline-manila", "Manila", manila),
    city("sky-jakarta", "skyline-jakarta", "Jakarta", jakarta, overrides={"stone": "#EFE8DA", "stone2": "#B9AE98", "gold": "#E9B949"},
         checks=[("stone", "near"), ("stone", "mid"), ("gold", "sky")]),
    city("sky-macau", "skyline-macau", "Macau", macau, overrides={"stone": "#D8C49A", "stone2": "#8E7A56"},
         checks=[("stone", "near"), ("stone", "mid")], fixes={"near": ["deep", "mid"]}),
]
