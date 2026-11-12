"""Mapsie Originals: famous landmarks of Asia and the Middle East."""
from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group  # noqa: F401


# ================================================================ private helpers (copied from culture.py)
def poly(*pts, close=True) -> str:
    s = "M" + " L".join(f"{x:g} {y:g}" for x, y in pts)
    return s + ("Z" if close else "")


def arch(x, y, w, h) -> str:
    """Round-topped opening, (x, y) top-left of its bounding box."""
    r = w / 2
    return f"M{x:g} {y + h:g} V{y + r:g} A{r:g} {r:g} 0 0 1 {x + w:g} {y + r:g} V{y + h:g}Z"


def parch(x, y, w, h) -> str:
    """Pointed (Islamic / Gothic) arch opening, (x, y) top-left of its bounding box."""
    return (f"M{x:g} {y + h:g} V{y + w * .55:g} Q{x:g} {y + w * .12:g} {x + w / 2:g} {y:g} "
            f"Q{x + w:g} {y + w * .12:g} {x + w:g} {y + w * .55:g} V{y + h:g}Z")


def pagoda_roof(cx, y, w, h=7.0) -> str:
    """Upturned east-asian eave: tips at (cx±w, y-4)."""
    return (f"M{cx - w:g} {y - 5:g} Q{cx - w * .78:g} {y + 2:g} {cx - w * .58:g} {y + 2:g} H{cx + w * .58:g} "
            f"Q{cx + w * .78:g} {y + 2:g} {cx + w:g} {y - 5:g} Q{cx + w * .62:g} {y - 3:g} {cx + w * .44:g} {y - h:g} "
            f"H{cx - w * .44:g} Q{cx - w * .62:g} {y - 3:g} {cx - w:g} {y - 5:g}Z")


def clip_open(d: Drawing):
    d.raw('<g clip-path="url(#clip)">', '<g clip-path="url(#clip)">')


def clip_close(d: Drawing):
    d.raw("</g>", "</g>")


def birds(d: Drawing, pts, role="dark"):
    s = " ".join(f"M{x} {y} q{3 * k} {-3 * k} {6 * k} 0 q{3 * k} {-3 * k} {6 * k} 0" for x, y, k in pts)
    d.stroke(role, s, 1.7)


def blossom(d: Drawing, pts, role="blossom", hi="light"):
    for x, y, r in pts:
        d.shape(role, circle(x, y, r))
    for x, y, r in pts[::2]:
        d.shape(hi, circle(x - r * .35, y - r * .35, r * .28), shadow=False, line=False)


def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1])


def flags(d: Drawing, x0, y0, x1, y1, sag, n, size=4.5, square=True):
    """Tibetan prayer flags (blue, white, red, green, yellow) on a sagging string."""
    roles = ["fb", "fw", "fr", "fg", "fy"]
    cx, cy = (x0 + x1) / 2, max(y0, y1) + sag
    clip_open(d)
    d.stroke("dark", f"M{x0} {y0} Q{cx} {cy} {x1} {y1}", 1.2)
    for i in range(1, n + 1):
        t = i / (n + 1)
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1
        if square:
            d.shape(roles[i % 5], rrect(x - size / 2, y, size, size * 1.2, .8), shadow=False, spot=i % 5 == 2)
        else:
            d.shape(roles[i % 5], f"M{x - size:.1f} {y:.1f} L{x + size:.1f} {y:.1f} L{x:.1f} {y + size * 2:.1f}Z",
                    shadow=False, spot=i % 5 == 2)
    clip_close(d)


def palm(d: Drawing, x, base, h, lean=0.0, role="dark", s=1.0):
    """Sugar / coconut palm silhouette: curved trunk and a spray of fronds."""
    tx, ty = x + lean, base - h
    d.limb(role, f"M{x} {base} Q{x + lean * .2} {base - h * .5} {tx} {ty}", 3.2 * s)
    fr = ""
    for ang, L in [(-160, 20), (-125, 18), (-90, 14), (-55, 18), (-20, 20), (-190, 14), (10, 14)]:
        import math
        a = math.radians(ang)
        ex, ey = tx + math.cos(a) * L * s, ty + math.sin(a) * L * s + (6 * s if abs(ang + 90) > 50 else 0)
        mx, my = tx + math.cos(a) * L * s * .55, ty + math.sin(a) * L * s * .55 - 3 * s
        nx, ny = -math.sin(a), math.cos(a)
        fr += (f"M{tx:.1f} {ty:.1f} Q{mx + nx * 3 * s:.1f} {my + ny * 3 * s:.1f} {ex:.1f} {ey:.1f} "
               f"Q{mx - nx * 1 * s:.1f} {my - ny * 1 * s:.1f} {tx:.1f} {ty:.1f}Z ")
    d.shape(role, fr)


def cypress(x, base, h, w) -> str:
    return f"M{x} {base} C{x - w} {base - h * .25} {x - w * .7} {base - h * .75} {x} {base - h} C{x + w * .7} {base - h * .75} {x + w} {base - h * .25} {x} {base}Z"


# ================================================================ TAJ MAHAL
TAJ_DOME = ("M86 94 C80 89 78 82 79 76 C80 64 92 60 97 56 L100 51 L103 56 C108 60 120 64 121 76 "
            "C122 82 120 89 114 94Z")


def taj(d: Drawing, sh=True, ln=True, detail=False):
    """Taj Mahal in local coordinates: centre x=100, plinth top y=150, finial tip y≈40."""
    S = dict(shadow=sh, line=ln)
    F = dict(shadow=False, line=ln)
    # minarets at the plinth corners
    for x in (42, 158):
        d.shape("marble", f"M{x - 4.2} 150 L{x - 3.2} 96 H{x + 3.2} L{x + 4.2} 150Z", **S)
        for y in (132, 114, 96):
            d.shape("marble2", rrect(x - 6, y - 1.5, 12, 3.2, 1), **F)
        d.shape("marble", f"M{x - 5} 94 Q{x - 5.5} 85 {x} 81 Q{x + 5.5} 85 {x + 5} 94Z", **S)
        d.stroke("shade", f"M{x} 81 V76", 1.2, line=ln)
        if detail:
            d.stroke("marble2", f"M{x - 1.5} 100 V148 M{x + 1.5} 100 V148", .8, line=False)
    # drum and onion dome
    d.shape("marble", rrect(84, 90, 32, 18, 1), **S)
    d.shape("marble", TAJ_DOME, **S)
    d.shape("marble2", "M108 60 C118 66 121 74 120 82 C119 88 116 92 114 94 L106 94 C112 84 114 70 108 60Z", **F)
    d.stroke("shade", "M100 51 V41", 1.6, line=ln)
    if sh:
        d.shape("shade", circle(100, 46, 1.8), shadow=False, line=False)
    if detail:
        d.stroke("marble2", "M88 90 Q100 86 112 90", 1.2, line=False)
        d.stroke("shade", "M96 57 Q100 62 104 57", 1, line=False)
    # small domed kiosks (chhatris) on the roof
    for x in (75, 125):
        d.shape("marble", rrect(x - 6.5, 96, 13, 12, 1), **S)
        d.shape("shade", parch(x - 2.5, 99, 5, 9), **F)
        d.shape("marble", f"M{x - 8} 97 Q{x - 8} 88 {x} 85 Q{x + 8} 88 {x + 8} 97Z", **S)
        d.stroke("shade", f"M{x} 85 V80", 1.1, line=ln)
    # chamfered corners
    for x0 in (62, 130):
        d.shape("marble2", rrect(x0, 110, 8, 40, 0), **S)
        d.shape("shade", parch(x0 + 1.8, 115, 4.4, 13), **F)
        d.shape("shade", parch(x0 + 1.8, 133, 4.4, 15), **F)
        d.stroke("marble", f"M{x0 + 4} 110 V102", 1.6, line=ln)
    # main facade
    d.shape("marble", rrect(70, 106, 60, 44, 0), **S)
    for x0 in (73, 119):
        d.shape("shade", parch(x0, 112, 8, 15), **F)
        d.shape("shade", parch(x0, 132, 8, 17), **F)
    # great arched portal (iwan) in its tall frame
    d.shape("marble", rrect(83, 97, 34, 53, 0), **S)
    d.shape("marble2", parch(88, 103, 24, 47), **F, spot=True)
    d.shape("shade", parch(93, 116, 14, 34), **F)
    d.stroke("marble", "M83 97 V91 M117 97 V91", 1.6, line=ln)
    if detail:
        d.stroke("shade", "M85 99 H115 M85 99 V148 M115 99 V148", .9, line=False)
    # plinth
    d.shape("marble2", rrect(28, 150, 144, 8, 1), **S)
    if detail:
        for x in range(34, 168, 10):
            d.stroke("shade", f"M{x} 152 V156", 1, line=False)


MARBLE = {"marble": "#FFFDF7", "marble2": "#E9DFCF", "shade": "#B8A68C"}


def taj_reflection(d: Drawing):
    d.disc("glow", 100, 52, 36)
    birds(d, [(30, 58, 1), (44, 50, .8), (152, 44, .8)])
    d.band("mid", "M-30 112 Q10 104 30 108 Q50 100 70 110 L130 110 Q150 100 170 108 Q190 104 230 112", line=False)
    T = "translate(20 -8.4) scale(.8)"
    group(d, T, lambda: taj(d))
    d.band("near", "M-30 118 H230")
    pool = "M84 118 H116 L148 200 H52Z"
    d.shape("pool", pool, shadow=False)
    if d.paper:
        d.raw(f'<clipPath id="lmtajpool"><path d="{pool}"/></clipPath><g clip-path="url(#lmtajpool)">'
              f'<g opacity=".38" transform="translate(0 236) scale(1 -1)"><g transform="{T}">')
        taj(d, sh=False, ln=False)
        d.raw('</g></g></g>')
    d.stroke("light", "M92 140 h10 M104 154 h14 M82 168 h12 M110 178 h16", 1.6)
    d.stroke("marble2", "M84 118 L52 200 M116 118 L148 200", 3, line=False)
    for x, b, h, w in [(78, 128, 12, 3.2), (122, 128, 12, 3.2), (70, 142, 18, 4.2), (130, 142, 18, 4.2),
                       (58, 162, 26, 5.5), (142, 162, 26, 5.5), (42, 190, 36, 7), (158, 190, 36, 7)]:
        d.shape("deep", cypress(x, b, h, w))


def taj_dome(d: Drawing):
    d.disc("glow", 146, 40, 14)
    birds(d, [(40, 34, .9), (54, 26, .7)])
    d.band("mid", "M-30 150 Q20 140 50 146 Q80 138 100 144 Q130 138 160 146 Q190 140 230 150", line=False)
    group(d, "translate(-30 -40) scale(1.3)", lambda: taj(d, detail=True))
    d.band("near", "M-30 166 Q100 160 230 166")
    for x, b, h, w in [(14, 184, 40, 8), (186, 184, 40, 8), (36, 190, 30, 6), (164, 190, 30, 6)]:
        d.shape("deep", cypress(x, b, h, w))
    d.band("deep", hills(186, 3, 20), line=False)


# ================================================================ MOUNT EVEREST
EVEREST = "M-30 160 L20 126 L56 96 L80 70 L104 28 L126 58 L150 76 L176 92 L230 114 V230 H-30Z"


def everest_summit(d: Drawing):
    d.shape("rock", EVEREST)
    # sunlit snowy face up to the ridge that runs down from the summit
    d.shape("light", "M104 28 L80 70 L56 96 L20 126 L-30 160 V230 H128 L122 150 L114 104 L108 64Z", shadow=False)
    d.shape("rock2", "M58 118 L70 104 L76 122Z M84 96 L92 82 L96 100Z M36 140 L46 130 L50 144Z", shadow=False, line=False)
    d.shape("rock", "M104 28 L108 64 L114 104 L122 150 L128 230 H230 V114 L176 92 L150 76 L126 58Z", shadow=False, spot=True)
    # snow gullies on the dark face
    d.shape("snow2", "M126 58 L136 98 L130 94Z M150 76 L160 112 L154 108Z M176 92 L182 120 L177 117Z M114 44 L120 80 L116 76Z", shadow=False)
    d.stroke("fy", "M112 92 Q140 98 170 108", 2.4, line=False)
    # wind-blown summit plume
    d.shape("light", "M106 30 Q130 20 156 24 Q178 26 200 18 Q194 28 176 32 Q186 34 196 32 Q178 42 152 38 Q128 36 108 36Z", line=False)
    flags(d, 104, 32, -10, 130, 6, 9)
    flags(d, 104, 32, 206, 124, 4, 9)
    d.band("light", "M-30 168 L20 152 L52 160 L96 142 L132 154 L170 144 L230 158")
    d.band("rock2", "M-30 186 L40 176 L90 184 L150 174 L230 182", line=False)

def tent(d: Drawing, x, base, w, h, role="tent", spot=False):
    d.shape(role, f"M{x - w} {base} C{x - w} {base - h * 1.3} {x + w} {base - h * 1.3} {x + w} {base}Z", spot=spot)
    d.stroke("dark", f"M{x - w * .8} {base} Q{x} {base - h * 1.25} {x + w * .55} {base - h * .2} "
                     f"M{x + w * .8} {base} Q{x} {base - h * 1.25} {x - w * .55} {base - h * .2}", 1.1, line=False)
    d.marks("dark", f"M{x - w * .32} {base} Q{x} {base - h * .9} {x + w * .32} {base}Z")


def everest_camp(d: Drawing):
    d.disc("glow", 160, 52, 14)
    # Everest's dark pyramid peeking over the Nuptse ridge, Lhotse to the right
    d.shape("rock", "M30 120 L66 64 L94 26 L110 46 L124 56 L146 92 L156 120Z")
    d.shape("light", "M94 26 L86 44 L94 40 L86 58 L98 52 L94 70 L104 58 L108 44Z", shadow=False)
    d.stroke("light", "M118 54 L124 72 M130 66 L136 84", 2.4, line=False)
    d.shape("light", "M96 28 Q120 18 144 24 Q162 26 180 20 Q172 30 152 32 Q126 32 102 34Z")
    d.shape("light", "M110 120 L130 82 L144 70 L160 54 L174 70 L190 88 L230 110 V130 H110Z")
    d.shape("snow2", "M160 54 L156 72 L150 80 L162 84 L174 70Z M144 70 L140 92 L148 86Z", shadow=False)
    d.shape("light", "M-30 128 L4 98 L20 86 L36 78 L48 86 L64 82 L80 92 L98 98 L114 112 L130 128Z")
    d.shape("snow2", "M36 78 L32 96 L42 92 L48 86Z M64 82 L60 100 L70 96 L80 92Z", shadow=False)
    # Khumbu glacier and moraine
    d.band("snow2", "M-30 128 Q40 120 100 126 T230 124")
    d.stroke("light", "M20 134 Q70 128 120 134 M60 140 Q120 134 180 140", 1.6, line=False)
    d.band("ground", "M-30 150 Q30 140 80 146 T230 142")
    flags(d, 14, 118, 186, 126, 10, 12, size=4)
    d.stroke("dark", "M14 118 V156 M186 126 V152", 1.6)
    tent(d, 164, 156, 11, 10, "tent2")
    tent(d, 130, 162, 15, 14, "tent")
    tent(d, 92, 168, 19, 18, "tent2")
    tent(d, 48, 172, 23, 21, "tent", spot=True)
    d.band("rock2", "M-30 178 Q40 174 100 180 T230 176")
    d.marks("rock", ellipse(40, 186, 6, 3) + ellipse(130, 186, 7, 3) + ellipse(160, 180, 4, 2))


EVEREST_C = {"rock": "#5E6272", "rock2": "#8A8E9A", "snow2": "#DCE4EE",
             "fb": "#3D6FB6", "fw": "#FFFFFF", "fr": "#D64541", "fg": "#3E9A5B", "fy": "#F2C14E",
             "tent": "#F2B33D", "tent2": "#E8603A"}


# ================================================================ GREAT WALL
def wall_run(d: Drawing, p, h0, h1, n=24):
    """A stretch of crenellated wall standing on the cubic base line p, h0 -> h1 tall."""
    pts = [bez(*p, i / n) for i in range(n + 1)]
    hs = [h0 + (h1 - h0) * i / n for i in range(n + 1)]
    top = [(x, y - h) for (x, y), h in zip(pts, hs)]
    face = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in top) + " L" + " L".join(f"{x:.1f} {y:.1f}" for x, y in reversed(pts)) + "Z"
    d.shape("stone", face)
    teeth = ""
    for i in range(n):
        (xa, ya), (xb, yb) = top[i], top[i + 1]
        h = (hs[i] + hs[i + 1]) / 2
        tw = h * .3
        th = h * .32
        seg = ((xb - xa) ** 2 + (yb - ya) ** 2) ** .5
        k = 0.0
        while k + tw <= seg:
            t0, t1 = k / seg, (k + tw) / seg
            x0, y0 = xa + (xb - xa) * t0, ya + (yb - ya) * t0
            x1, y1 = xa + (xb - xa) * t1, ya + (yb - ya) * t1
            teeth += f"M{x0:.1f} {y0 + .5:.1f} L{x0:.1f} {y0 - th:.1f} L{x1:.1f} {y1 - th:.1f} L{x1:.1f} {y1 + .5:.1f}Z "
            k += tw * 2
    d.shape("stone", teeth, shadow=False)
    # walkway edge and brick course
    d.stroke("stone2", "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in top), 1.6, line=False)
    mid = [(x, y - h * .45) for (x, y), h in zip(pts, hs)]
    d.stroke("stone2", "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in mid), 1.2, line=False)


def watchtower(d: Drawing, x, base, w, h):
    m = w / 7
    top = base - h
    s = f"M{x - w / 2} {base} V{top}"
    for i in range(4):
        x0 = x - w / 2 + 2 * i * m
        s += f" H{x0 + m}"
        if i < 3:
            s += f" V{top + m} H{x0 + 2 * m} V{top}"
    s += f" V{base}Z"
    d.shape("stone", s)
    d.stroke("stone2", f"M{x - w / 2} {top + m * 1.6} H{x + w / 2}", 1.4, line=False)
    for k in (-1, 0, 1):
        d.marks("dark", arch(x + k * w * .28 - w * .07, top + h * .35, w * .14, h * .26))


def great_wall(d: Drawing):
    d.disc("glow", 52, 62, 18)
    d.band("far", "M-30 104 L10 88 L36 98 L62 76 L88 94 L110 82 L140 96 L168 72 L196 88 L230 80")
    d.band("mid", "M-30 130 Q20 108 60 120 Q100 128 130 112 Q170 96 230 116")
    d.band("near", "M-30 200 C20 176 70 128 122 108 C138 114 152 108 172 86 C186 78 204 84 230 92")
    wall_run(d, [(122, 106), (138, 112), (152, 106), (172, 84)], 10, 6, 10)
    watchtower(d, 172, 88, 14, 18)
    wall_run(d, [(-34, 204), (16, 174), (70, 126), (122, 106)], 32, 10, 26)
    watchtower(d, 122, 110, 26, 36)
    d.band("deep", "M-30 196 Q60 186 120 192 T230 180", line=False)


# ================================================================ MOUNT FUJI
FUJI_L = [(103, 62), (73, 84), (30, 146), (-30, 154)]
FUJI_R = [(133, 62), (163, 84), (206, 146), (266, 154)]


def fuji_cone(d: Drawing, snow_t=0.24):
    edge = ("M-30 154 C30 146 73 84 103 62 L108 60 L113 62 L118 59 L123 62 L128 60 L133 62 "
            "C163 84 206 146 266 154")
    d.band("fuji", edge)
    a = bez(*FUJI_L, snow_t)
    b = bez(*FUJI_R, snow_t)
    left = [bez(*FUJI_L, snow_t * i / 6) for i in range(7)]
    right = [bez(*FUJI_R, snow_t * i / 6) for i in range(7)]
    fingers = []
    n = 9
    for i in range(1, n):
        x = a[0] + (b[0] - a[0]) * i / n
        y = a[1] + (b[1] - a[1]) * i / n
        fingers.append((x, y + (13 if i % 2 else -2) + (4 if i in (3, 5) else 0)))
    pts = left + fingers + list(reversed(right))
    s = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    s += " L128 60 L123 62 L118 59 L113 62 L108 60Z"
    d.shape("light", s, shadow=False, spot=False)


def fuji_sakura(d: Drawing):
    fuji_cone(d)
    d.band("mid", "M-30 150 Q30 132 70 140 Q100 146 130 156 T230 160")
    # Chureito five-storey pagoda on the hillside
    cx = 52
    roofs = [(138, 21), (124, 18.5), (111, 16), (99, 13.5), (88, 11)]
    d.stroke("dark", f"M{cx} 92 V64", 1.8)
    for y in (70, 74, 78):
        d.shape("pagoda2", ellipse(cx, y, 3, 1.1), shadow=False)
    for i, (y, w) in enumerate(roofs):
        top = roofs[i + 1][0] if i < 4 else y - 10
        bw = w * .62
        d.shape("pagoda", f"M{cx - bw / 2} {top - 2} H{cx + bw / 2} V{y + (12 if i == 0 else 1)} H{cx - bw / 2}Z", spot=i == 0)
    for y, w in reversed(roofs):
        d.shape("dark", pagoda_roof(cx, y, w, 6))
    d.marks("dark", rrect(cx - 2.5, 140, 5, 10, 1))
    # cherry blossom
    d.limb("dark", "M214 18 C190 32 168 44 140 52 M178 38 C174 48 170 56 162 62", 3.2)
    blossom(d, [(140, 52, 8), (154, 45, 8), (162, 62, 7.5), (170, 46, 6.5), (130, 58, 5), (150, 60, 6)])
    blossom(d, [(18, 132, 12), (34, 140, 10), (80, 142, 10), (92, 152, 9), (14, 152, 10)])
    d.band("near", "M-30 160 Q40 150 90 158 T230 156")
    blossom(d, [(130, 168, 12), (150, 160, 11), (168, 172, 12), (186, 160, 9), (40, 176, 10), (60, 170, 8)])
    for x, y in [(118, 110), (128, 96), (142, 118), (90, 120), (100, 104)]:
        d.marks("blossom", ellipse(x, y, 2.4, 1.5))
    d.band("deep", hills(190, 3, 30), line=False)


# ================================================================ FUSHIMI INARI
def torii(d: Drawing, s, vx=100, vy=92, ln=True):
    def draw():
        S = dict(line=ln)
        for x in (-60, 48):
            d.shape("torii", rrect(x, -54, 12, 164, 1), **S)
            d.shape("kuro", rrect(x - 1, 92, 14, 18, 1), shadow=False, **S)
        d.shape("torii", rrect(-74, -40, 148, 9, 1), **S)
        d.shape("torii", "M-80 -64 Q0 -54 80 -64 L77 -52 Q0 -44 -77 -52Z", **S)
        d.shape("kuro", "M-86 -74 Q0 -62 86 -74 L82 -64 Q0 -54 -82 -64Z", spot=(s == 1.0), **S)
    group(d, f"translate({vx} {vy}) scale({s})", draw)


def fushimi_gates(d: Drawing):
    d.band("deep", "M-30 -10 H230", line=False)
    d.shape("near", "M-30 40 Q10 30 40 44 Q60 30 80 56 L100 92 L120 56 Q140 30 160 44 Q190 30 230 40 V230 H-30Z", shadow=False, line=False)
    d.disc("glow", 100, 84, 14)
    d.shape("ground", "M100 92 L178 206 H22Z", shadow=False)
    d.stroke("ground2", "M100 92 L84 206 M100 92 L116 206", 1.4, line=False)
    for i, s in enumerate([.13, .18, .245, .33, .45, .6, .8]):
        torii(d, s, ln=i >= 4)
    torii(d, 1.0)
    # stone fox guardian and lantern glow
    d.shape("light", cloud(150, 186, .8), shadow=False, line=False)


FUSHIMI = {"torii": "#E3482D", "kuro": "#2A2421", "ground2": "#00000022"}


# ================================================================ ANGKOR WAT
def lotus_tower(x, base, w, h, tiers=6) -> str:
    """Angkor's lotus-bud prang: tiered, swelling, then tapering to a point."""
    def hw(t):
        return w * (1 - t ** 1.7) ** .6
    left, right = [], []
    for i in range(tiers):
        t0, t1 = i / tiers, (i + 1) / tiers
        y0, y1 = base - h * t0, base - h * t1
        a, b = hw(t0) + 1.3, hw(t1)
        left += [(x - a, y0), (x - a, y0 - 1.6), (x - b - .2, y1)]
        right += [(x + a, y0), (x + a, y0 - 1.6), (x + b + .2, y1)]
    pts = left + [(x, base - h - 6)] + list(reversed(right))
    return "M" + " L".join(f"{px:.1f} {py:.1f}" for px, py in pts) + "Z"


def angkor_temple(d: Drawing, sh=True, ln=True, role="dark"):
    S = dict(shadow=sh, line=ln)
    d.shape(role, lotus_tower(52, 116, 9, 30, 5) + " " + lotus_tower(148, 116, 9, 30, 5), **S)
    d.shape(role, lotus_tower(76, 106, 10, 40, 6) + " " + lotus_tower(124, 106, 10, 40, 6), **S)
    d.shape(role, lotus_tower(100, 100, 13, 58, 7), **S)
    upper = poly((60, 116), (60, 104), (64, 100), (136, 100), (140, 104), (140, 116))
    mid = poly((36, 128), (36, 118), (42, 113), (158, 113), (164, 118), (164, 128))
    low = poly((10, 138), (10, 130), (18, 126), (182, 126), (190, 130), (190, 138))
    d.shape(role, upper + " " + mid + " " + low, **S)
    # entrance gopuras on the outer gallery
    d.shape(role, lotus_tower(100, 128, 8, 14, 3) + " " + lotus_tower(28, 128, 5, 8, 2) + " " + lotus_tower(172, 128, 5, 8, 2), **S)


def angkor_sunrise(d: Drawing):
    d.disc("glow", 100, 82, 46)
    d.disc("glow2", 100, 82, 30, shadow=False, line=False)
    birds(d, [(140, 44, 1), (154, 36, .8), (40, 50, .8)])
    angkor_temple(d)
    d.band("deep", "M-30 138 H230", line=False)
    d.band("far", "M-30 142 Q100 138 230 142")
    if d.paper:
        d.raw('<clipPath id="lmangpond"><path d="M-30 142 Q100 138 230 142 V230 H-30Z"/></clipPath><g clip-path="url(#lmangpond)">'
              '<g opacity=".3" transform="translate(0 280) scale(1 -1)">')
        angkor_temple(d, sh=False, ln=False)
        d.raw('</g></g>')
    d.stroke("light", "M60 156 h16 M110 164 h22 M80 176 h12 M140 150 h12", 1.6)
    for x, y in [(44, 168), (150, 172), (160, 162)]:
        d.shape("pop", f"M{x - 4} {y} Q{x - 4} {y - 5} {x} {y - 7} Q{x + 4} {y - 5} {x + 4} {y}Z", shadow=False)
        d.shape("lily", ellipse(x, y + 1.5, 7, 2), shadow=False)
    palm(d, 14, 150, 62, 4, "dark", 1.1)
    palm(d, 186, 150, 50, -4, "dark", 1.0)
    d.band("dark", "M-30 186 Q60 178 120 184 T230 180", line=False)


# ================================================================ PETRA
def petra_treasury(d: Drawing):
    d.shape("rock", "M-30 -10 H230 V230 H-30Z", shadow=False, line=False)
    d.stroke("rock3", "M20 30 Q60 20 90 30 M110 24 Q150 18 186 30 M16 46 Q40 40 60 44 M150 40 Q170 36 196 44", 2, line=False)
    # recessed facade panel
    d.shape("rock3", "M38 178 V48 Q100 40 162 48 V178Z", shadow=False)
    lit = "facade"
    # --- upper storey: broken pediment pavilions and the round tholos
    d.shape(lit, rrect(40, 96, 120, 8, 1))
    for x0 in (42, 130):
        d.shape("rock3", rrect(x0, 74, 28, 22, 0), shadow=False)
        for cx in (x0 + 3, x0 + 25):
            d.shape(lit, rrect(cx - 3, 74, 6, 22, 1))
    d.shape(lit, poly((40, 76), (72, 64), (72, 70), (44, 80)) + " " + poly((160, 76), (128, 64), (128, 70), (156, 80)))
    d.shape("rock3", rrect(86, 72, 28, 24, 0), shadow=False)
    for cx in (89, 100, 111):
        d.shape(lit, rrect(cx - 2.6, 72, 5.2, 24, 1))
    d.shape(lit, rrect(84, 68, 32, 5, 1))
    d.shape(lit, "M84 68 L100 52 L116 68Z")
    d.shape(lit, "M100 52 C95 52 95 44 100 42 C105 44 105 52 100 52Z", spot=True)
    d.stroke(lit, "M46 76 V68 M154 76 V68 M72 64 V58 M128 64 V58", 2.2)
    # --- lower storey: six columns under a triangular pediment
    d.shape(lit, "M56 120 L100 100 L144 120Z")
    d.stroke("rock3", "M66 117 L100 102 L134 117", 1.2, line=False)
    d.shape(lit, rrect(40, 118, 120, 8, 1))
    d.marks("dark", rrect(92, 138, 16, 34, 1))
    for cx in (48, 64, 80, 120, 136, 152):
        d.shape(lit, rrect(cx - 4, 128, 8, 44, 1))
        d.shape(lit, rrect(cx - 5.5, 125, 11, 4, 1), shadow=False)
        d.stroke("rock3", f"M{cx - 1.5} 132 V170 M{cx + 1.5} 132 V170", .8, line=False)
    d.shape(lit, rrect(36, 172, 128, 6, 1))
    # the narrow Siq framing the first glimpse
    d.band("ground", "M-30 182 Q100 176 230 182")
    d.shape("siq", "M-30 -10 H58 C44 20 30 50 34 90 C38 130 26 160 30 230 H-30Z")
    d.shape("siq", "M230 -10 H146 C160 20 172 50 168 90 C164 130 176 160 172 230 H230Z")
    d.stroke("siq2", "M10 40 Q22 70 14 110 M22 130 Q16 160 20 190 M188 40 Q178 70 186 110 M178 130 Q184 160 180 190", 2, line=False)


PETRA = {"rock": "#D98A6B", "rock3": "#A5584A", "facade": "#F2B596", "siq": "#8C4A3E", "siq2": "#6E362D"}


# ================================================================ BURJ KHALIFA
def burj(d: Drawing):
    base = 178
    pieces = [(70, 76, 154, "glass2"), (124, 130, 162, "glass"), (76, 82, 128, "glass2"), (118, 124, 138, "glass"),
              (82, 88, 96, "glass2"), (112, 118, 108, "glass"), (88, 94, 62, "glass2"), (106, 112, 78, "glass")]
    for x0, x1, top, role in pieces:
        if x0 < 100:
            path = poly((x0, base), (x0, top + 5), (x1, top), (x1, base))
        else:
            path = poly((x0, base), (x0, top), (x1, top + 5), (x1, base))
        d.shape(role, path)
    d.shape("glass", poly((94, base), (94, 50), (97, 46), (103, 46), (106, 50), (106, base)), spot=True)
    d.shape("glass", poly((96.5, 47), (98.5, 20), (100, 8), (101.5, 20), (103.5, 47)))
    d.stroke("light", "M100 52 V176 M97 30 H103", 1, line=False)
    d.stroke("glass2", "M73 160 V176 M79 134 V176 M85 102 V176 M91 68 V176 M109 84 V176 M115 114 V176 M121 144 V176 M127 168 V176", .9, line=False)


def burj_khalifa(d: Drawing):
    d.disc("glow", 56, 66, 20)
    d.shape("far", poly((14, 182), (14, 146), (24, 146), (24, 130), (34, 130), (34, 150), (42, 150), (42, 120), (48, 114), (54, 120), (54, 182)) + " " +
            poly((140, 182), (140, 132), (150, 126), (152, 132), (152, 146), (162, 146), (162, 120), (170, 120), (170, 142), (180, 142), (180, 152), (190, 152), (190, 182)))
    d.shape("mid", poly((30, 182), (30, 156), (40, 156), (40, 140), (52, 140), (52, 160), (62, 160), (62, 182)) + " " +
            poly((136, 182), (136, 158), (148, 158), (148, 146), (158, 140), (158, 164), (172, 164), (172, 182)))
    burj(d)
    d.band("near", "M-30 178 Q100 172 230 178")
    d.stroke("light", "M60 186 Q100 180 140 186", 2, line=False)
    d.band("deep", hills(192, 3, 20), line=False)


GLASS = {"glass": "#C9DCEB", "glass2": "#8FB0CB"}


# ================================================================ SIGIRIYA
def sigiriya(d: Drawing):
    d.disc("glow", 150, 46, 15)
    birds(d, [(30, 50, 1), (44, 42, .8)])
    d.band("far", hills(128, 8, 20), line=False)
    rock = "M38 140 C34 112 40 84 48 64 C52 52 60 46 72 45 L130 44 C142 45 149 51 153 62 C162 84 166 112 162 140Z"
    d.shape("rock", rock)
    d.shape("rock2", "M140 46 C146 48 150 54 152 60 C160 80 164 112 160 140 L146 140 C150 110 148 76 140 46Z", shadow=False, line=False)
    d.stroke("rock2", "M62 66 Q58 92 64 124 M98 56 Q94 76 99 100 M128 54 Q132 80 127 112", 1.8)
    d.stroke("rock2", "M76 60 Q74 72 77 84 M112 56 Q114 66 111 78 M54 92 Q70 96 84 92", 1.4, line=False)
    d.shape("near", "M52 60 C56 50 62 46 72 45 L130 44 C142 45 148 50 152 60 Q140 52 128 56 Q116 50 104 55 Q90 50 78 55 Q64 50 52 60Z", shadow=False)
    d.band("mid", "M-30 136 Q0 124 20 130 Q40 120 60 130 Q80 122 100 130 Q120 120 140 130 Q160 122 180 130 Q200 124 230 132")
    # the lion staircase: two giant paws flanking the steps
    d.shape("brick", "M76 184 L86 128 H114 L124 184Z")
    d.stroke("brick2", "M86 136 H114 M84 145 H116 M82 154 H118 M80 163 H120 M78 172 H122", 1.6)
    for k in (-1, 1):
        cx = 100 + k * 44
        leg = f"M{cx - 25} 176 V146 Q{cx - 25} 128 {cx - 8} 126 H{cx + 8} Q{cx + 25} 128 {cx + 25} 146 V176Z"
        d.shape("paw", leg)
        d.stroke("paw2", f"M{cx - 25 + 6 * (k > 0)} 150 Q{cx} 142 {cx + 25 - 6 * (k < 0)} 150", 1.6)
        toes = [cx - 16, cx, cx + 16]
        for x in toes:
            d.shape("paw2", f"M{x - 3.5} 174 Q{x + 1} 186 {x + 5} 176 Q{x} 180 {x - 3.5} 174Z", shadow=False)
        d.shape("paw", " ".join(ellipse(x, 164, 8, 12) for x in toes), spot=True)
        d.stroke("paw2", " ".join(f"M{x} 156 V168" for x in toes), 1.2, line=False)
    d.band("ground", "M-30 184 Q100 180 230 184")

SIGIRIYA = {"rock": "#B58A6A", "rock2": "#8E6A52", "paw": "#D29C70", "paw2": "#8E5A3A", "brick": "#C27C55", "brick2": "#9A5C3E"}


# ================================================================ PETRONAS TOWERS
def petronas(d: Drawing, cx):
    base = 182
    tiers = [(16, 82), (13.5, 66), (11, 55), (9, 47), (7, 40)]
    prev = base
    for hw, top in tiers:
        d.shape("steel", rrect(cx - hw, top, hw * 2, prev - top + 2, 2.5))
        d.shape("steel2", f"M{cx + hw * .35} {top + 1} H{cx + hw - .5} V{prev} H{cx + hw * .35}Z", shadow=False, line=False)
        prev = top
    d.shape("steel", poly((cx - 4.5, 41), (cx - 2, 26), (cx + 2, 26), (cx + 4.5, 41)))
    d.shape("steel", circle(cx, 30, 3), shadow=False)
    d.stroke("steel", f"M{cx} 26 V8", 1.8)
    d.stroke("steel2", f"M{cx - 8} 88 V178 M{cx - 2} 70 V178 M{cx + 4} 70 V178", .9, line=False)
    d.stroke("win", " ".join(f"M{cx - 15} {y} H{cx + 15}" for y in range(92, 178, 8)), .8, line=False)


def petronas_towers(d: Drawing):
    d.disc("glow", 100, 66, 20)
    d.shape("far", poly((-30, 184), (-30, 150), (12, 150), (12, 136), (26, 136), (26, 156), (40, 156), (40, 184)) + " " +
            poly((160, 184), (160, 146), (172, 140), (184, 146), (184, 132), (196, 132), (196, 154), (230, 154), (230, 184)), line=False)
    petronas(d, 68)
    petronas(d, 132)
    # skybridge with its two-legged support
    d.limb("steel2", "M100 114 L86 138 M100 114 L114 138", 2.4)
    d.shape("steel", rrect(82, 106, 36, 8, 1.5), spot=True)
    d.stroke("win", "M85 110 H115", 1, line=False)
    d.band("near", "M-30 176 Q20 168 50 174 Q100 182 150 174 Q180 168 230 176")
    d.band("deep", hills(192, 3, 20), line=False)


STEEL = {"steel": "#D5DCE4", "steel2": "#A3AFBD", "win": "#7D8A9A"}


# ================================================================ HA LONG BAY
def karst(x, base, w, h, lean=0.0) -> str:
    return (f"M{x - w / 2:.1f} {base:.1f} C{x - w / 2 - 3:.1f} {base - h * .5:.1f} {x - w * .5 + lean:.1f} {base - h * .9:.1f} "
            f"{x - w * .12 + lean:.1f} {base - h:.1f} C{x + w * .12 + lean:.1f} {base - h * 1.05:.1f} {x + w * .42 + lean:.1f} {base - h * .94:.1f} "
            f"{x + w * .46 + lean * .6:.1f} {base - h * .7:.1f} C{x + w * .54:.1f} {base - h * .45:.1f} {x + w / 2 + 4:.1f} {base - h * .2:.1f} "
            f"{x + w / 2:.1f} {base:.1f}Z")


def junk(d: Drawing):
    d.shape("hull", "M58 150 H146 L154 140 L158 142 L150 162 Q104 168 70 162 Q62 158 58 150Z")
    d.stroke("hull2", "M66 156 H150", 1.4, line=False)
    d.shape("light", rrect(84, 142, 46, 9, 1.5), shadow=False)
    d.marks("dark", " ".join(rrect(x, 145, 4, 3.5, .5) for x in (90, 98, 106, 114, 122)))
    for m, top, w, hgt, sp in [(76, 102, 22, 44, False), (102, 78, 30, 66, True), (132, 98, 20, 46, False)]:
        d.stroke("dark", f"M{m} 146 V{top - 4}", 1.8)
        sail = f"M{m} {top + 4} L{m + w * .9:.1f} {top:.1f} Q{m + w * 1.25:.1f} {top + hgt * .5:.1f} {m + w:.1f} {top + hgt:.1f} L{m} {top + hgt}Z"
        d.shape("sail", sail, spot=sp)
        bat = " ".join(f"M{m} {top + 4 + (hgt - 4) * k / 5:.1f} L{m + w * (1.02 + .14 * (1 - abs(2 * k / 5 - 1))):.1f} {top + hgt * k / 5:.1f}"
                       for k in range(1, 5))
        d.stroke("sail2", bat, 1.2, line=False)


def ha_long_bay(d: Drawing):
    d.disc("glow", 70, 58, 16)
    birds(d, [(130, 40, .9), (144, 34, .7)])
    d.shape("far", karst(150, 122, 22, 50, 2) + " " + karst(176, 122, 18, 36) + " " + karst(118, 122, 14, 30, -2) + " " + karst(30, 122, 18, 34), line=False)
    d.shape("mid", karst(132, 126, 22, 42, -3) + " " + karst(60, 126, 22, 48, 3) + " " + karst(88, 126, 14, 26))
    d.shape("near", karst(22, 134, 38, 92, 6) + " " + karst(186, 134, 34, 74, -4))
    d.stroke("deep", "M12 60 Q10 90 14 124 M30 70 Q34 100 30 128 M182 76 Q180 100 184 126", 1.6, line=False)
    d.band("sea", "M-30 124 H230")
    d.stroke("sea2", "M20 134 h16 M150 132 h22 M40 176 h18 M150 178 h20", 1.6)
    junk(d)
    d.band("sea2", waves(170, 2.5, 22), line=False)


HALONG = {"sea": "#4FA39E", "sea2": "#7CC2BA", "sail": "#D9673E", "sail2": "#9C3F22", "hull": "#7A4A2A", "hull2": "#5A3420"}


# ================================================================ BOROBUDUR
def bell(x, base, w) -> str:
    """Perforated bell stupa (with harmika and spire), w = half-width."""
    return (f"M{x - w:.1f} {base:.1f} C{x - w:.1f} {base - w * 1.25:.1f} {x - w * .55:.1f} {base - w * 1.55:.1f} {x:.1f} {base - w * 1.55:.1f} "
            f"C{x + w * .55:.1f} {base - w * 1.55:.1f} {x + w:.1f} {base - w * 1.25:.1f} {x + w:.1f} {base:.1f}Z "
            f"M{x - w * .3:.1f} {base - w * 1.5:.1f} V{base - w * 1.85:.1f} H{x + w * .3:.1f} V{base - w * 1.5:.1f}Z "
            f"M{x - w * .18:.1f} {base - w * 1.85:.1f} L{x:.1f} {base - w * 2.5:.1f} L{x + w * .18:.1f} {base - w * 1.85:.1f}Z")


def lattice(x, base, w) -> str:
    s = ""
    for row, (dy, n) in enumerate([(.4, 2), (.95, 1)]):
        for i in range(n):
            px = x + (i - (n - 1) / 2) * w * .55
            py = base - w * dy - w * .15
            r = w * .17
            s += f"M{px:.1f} {py - r:.1f} L{px + r:.1f} {py:.1f} L{px:.1f} {py + r:.1f} L{px - r:.1f} {py:.1f}Z "
    return s


def borobudur(d: Drawing):
    d.disc("glow", 100, 62, 34)
    d.band("far", "M-30 118 Q20 114 40 102 L64 80 L74 82 L100 106 Q140 116 230 112", line=False)
    d.shape("light", cloud(52, 70, .7), shadow=False, line=False)
    # central great stupa
    d.shape("stone", "M74 88 C74 64 86 54 100 54 C114 54 126 64 126 88Z")
    d.shape("stone", rrect(92, 42, 16, 13, 1))
    d.shape("stone", "M94 42 L100 20 L106 42Z", spot=True)
    d.stroke("stone2", "M96 37 H104 M97 31 H103", 1.2, line=False)
    rows = [(102, 9, [64, 82, 118, 136], (50, 88, 100, 8)),
            (122, 10, [32, 55, 78, 100, 122, 145, 168], (26, 102, 148, 8)),
            (144, 11, [10, 35, 60, 85, 115, 140, 165, 190], (8, 122, 184, 8))]
    for base, w, xs, (wx, wy, ww, wh) in rows:
        d.shape("stone2", rrect(wx, wy, ww, wh, 1))
        for x in xs:
            d.shape("stone", bell(x, base, w))
            d.marks("stone2", lattice(x, base, w))
    for x0, y, w in [(0, 144, 200), (-10, 154, 220)]:
        d.shape("stone2", rrect(x0, y, w, 10, 1))
        d.stroke("stone", " ".join(f"M{x} {y + 3} V{y + 7}" for x in range(int(x0) + 6, int(x0 + w), 10)), 1.6, line=False)
    d.shape("stone", "M93 144 H107 V176 H93Z", shadow=False)
    d.stroke("stone2", "M93 154 H107 M93 164 H107", 1.4, line=False)
    palm(d, 10, 182, 50, 6, "deep", .95)
    palm(d, 190, 182, 46, -6, "deep", .9)
    d.band("near", "M-30 172 Q100 166 230 172")
    d.band("deep", hills(188, 3, 20), line=False)

BORO = {"stone": "#A49C8E", "stone2": "#6F685D"}


# ================================================================ FORBIDDEN CITY
def hip_roof(cx, y, w, top_w, h) -> str:
    """Chinese hip roof: upswept eave tips at (cx±w, y-5), ridge (cx±top_w, y-h)."""
    return (f"M{cx - w:g} {y - 6:g} Q{cx - w * .86:g} {y + 2:g} {cx - w * .66:g} {y + 2:g} H{cx + w * .66:g} "
            f"Q{cx + w * .86:g} {y + 2:g} {cx + w:g} {y - 6:g} Q{cx + w * .7:g} {y - 4:g} {cx + top_w + (w - top_w) * .35:g} {y - h * .55:g} "
            f"L{cx + top_w:g} {y - h:g} H{cx - top_w:g} L{cx - top_w - (w - top_w) * .35:g} {y - h * .55:g} "
            f"Q{cx - w * .7:g} {y - 4:g} {cx - w:g} {y - 6:g}Z")


def forbidden_city(d: Drawing):
    d.disc("glow", 156, 46, 15)
    birds(d, [(30, 44, .9), (44, 36, .7)])
    d.band("far", "M-30 128 H230")
    d.shape("roof", hip_roof(14, 126, 26, 8, 14) + " " + hip_roof(186, 126, 26, 8, 14), line=False)
    # marble terraces
    for x0, y, w in [(30, 136, 140), (20, 146, 160), (10, 156, 180)]:
        d.shape("marble", rrect(x0, y, w, 10, 1))
        d.stroke("marble2", " ".join(f"M{x} {y - 4} V{y}" for x in range(int(x0) + 4, int(x0 + w), 8)) + f" M{x0} {y - 2} H{x0 + w}", 1.4)
    d.shape("marble2", "M90 136 H110 L116 166 H84Z", shadow=False)
    d.stroke("marble", "M88 146 H112 M86 156 H114", 1.2, line=False)
    # hall body
    d.shape("red", rrect(44, 100, 112, 36, 0))
    d.shape("red2", rrect(56, 108, 88, 28, 0), shadow=False)
    for x in range(56, 146, 11):
        d.shape("red", rrect(x - 2, 106, 4, 30, 0), shadow=False)
    for x in range(61, 140, 11):
        d.stroke("roof", f"M{x} 112 V132 M{x - 3} 120 H{x + 3}", 1.0, line=False)
    d.shape("teal", rrect(46, 98, 108, 6, 0), shadow=False)
    # double-eaved golden roof
    d.shape("roof", hip_roof(100, 102, 72, 52, 14), spot=True)
    d.stroke("roof2", " ".join(f"M{x} 92 V101" for x in range(42, 160, 8)), 1, line=False)
    d.shape("red", rrect(60, 74, 80, 16, 0))
    d.shape("teal", rrect(62, 74, 76, 5, 0), shadow=False)
    d.shape("roof", hip_roof(100, 76, 60, 28, 28))
    d.stroke("roof2", " ".join(f"M{x} {54 + abs(x - 100) * .2:.0f} V74" for x in range(52, 150, 7)), 1, line=False)
    d.stroke("roof2", "M72 48 H128", 3)
    d.shape("roof2", "M70 50 Q66 44 70 40 Q72 44 74 46Z M130 50 Q134 44 130 40 Q128 44 126 46Z", shadow=False)
    d.band("ground", "M-30 166 H230")
    d.band("ground2", "M-30 182 H230", line=False)


FORBIDDEN = {"roof": "#EDB12E", "roof2": "#B9821A", "red": "#B8322A", "red2": "#8C2219", "teal": "#2F7A72",
             "marble": "#F4F0E8", "marble2": "#C9C1B3", "ground2": "#00000018"}


# ================================================================ HAGIA SOPHIA
def minaret(d: Drawing, x, base, top, w=3.4, balconies=2):
    d.shape("minaret", f"M{x - w} {base} V{top} H{x + w} V{base}Z")
    for i in range(balconies):
        y = top + 8 + i * (base - top) * .3
        d.shape("minaret", rrect(x - w - 2, y, w * 2 + 4, 3, 1), shadow=False)
    d.shape("lead", f"M{x - w - .5} {top + 1} L{x} {top - 16} L{x + w + .5} {top + 1}Z")


def hagia_sophia(d: Drawing):
    d.disc("glow", 150, 52, 13)
    d.band("far", "M-30 150 Q100 144 230 150", line=False)
    # rear minarets (half hidden)
    minaret(d, 60, 124, 66, 3, 1)
    minaret(d, 140, 124, 66, 3, 1)
    # main dome on its ring of windows
    d.shape("wall", rrect(70, 88, 60, 16, 1))
    d.marks("dark", " ".join(arch(x, 92, 3.2, 8) for x in range(73, 128, 6)))
    d.shape("lead", "M66 90 Q68 56 100 54 Q132 56 134 90Z", spot=True)
    d.shape("lead2", "M112 57 Q132 62 134 90 H120 Q122 70 112 57Z", shadow=False, line=False)
    d.stroke("wall", "M100 54 V46", 1.6)
    # cascading semi-domes
    for cx, r in [(62, 18), (138, 18)]:
        d.shape("wall", rrect(cx - r - 2, 104, 2 * r + 4, 10, 1))
        d.shape("lead", f"M{cx - r} 106 A{r} {r * .8} 0 0 1 {cx + r} 106Z")
    d.shape("lead", "M38 118 A10 8 0 0 1 58 118Z M142 118 A10 8 0 0 1 162 118Z")
    # main block and buttresses
    d.shape("wall", rrect(40, 112, 120, 58, 0))
    d.shape("wall2", poly((40, 170), (40, 100), (52, 96), (52, 170)) + " " + poly((148, 170), (148, 96), (160, 100), (160, 170)))
    d.shape("wall2", rrect(84, 104, 32, 66, 0))
    d.marks("dark", " ".join(arch(x, 116, 5, 10) for x in (88, 97.5, 107)))
    for x in (60, 72, 124, 136):
        d.marks("dark", arch(x, 126, 6, 12))
        d.marks("dark", arch(x, 146, 6, 12))
    d.marks("dark", arch(94, 144, 12, 26))
    d.stroke("wall2", "M40 138 H84 M116 138 H160", 1.4, line=False)
    # front minarets
    minaret(d, 30, 172, 70, 3.8, 2)
    minaret(d, 170, 172, 70, 3.8, 2)
    d.band("near", "M-30 170 Q100 164 230 170")
    for x, b, h, w in [(18, 184, 26, 5), (182, 184, 26, 5), (52, 182, 18, 4), (148, 182, 18, 4)]:
        d.shape("deep", cypress(x, b, h, w))
    d.band("deep", hills(190, 3, 20), line=False)


HAGIA = {"wall": "#E3A585", "wall2": "#C8836A", "lead": "#8796A6", "lead2": "#6B7A8B", "minaret": "#D6BE9E"}


# ================================================================ catalogue
CONCEPTS = [
    Concept("lm-taj-reflection", "landmark-taj-mahal", "Taj Mahal", taj_reflection,
            overrides={**MARBLE, "pool": "#6FA9C4"},
            checks=[("marble", "sky"), ("marble", "glow"), ("deep", "near"), ("pool", "near"), ("marble", "mid")],
            fixes={"sky": ["far", "sky2", "mid"], "glow": ["glow2", "pop", "far"], "mid": ["near", "far"], "near": ["mid", "far"]}),
    Concept("lm-taj-dome", "landmark-taj-mahal", "Taj Mahal dome & minarets", taj_dome, overrides=MARBLE,
            checks=[("marble", "sky"), ("marble", "glow"), ("deep", "near"), ("marble", "mid")],
            fixes={"sky": ["far", "sky2", "mid"], "glow": ["glow2", "pop", "far"], "mid": ["near", "far"], "near": ["mid", "far"]}),
    Concept("lm-everest-summit", "landmark-everest", "Mount Everest", everest_summit, overrides=EVEREST_C,
            checks=[("rock", "sky"), ("light", "sky")],
            fixes={"sky": ["sky2", "far", "mid"]}),
    Concept("lm-everest-camp", "landmark-everest", "Everest base camp", everest_camp, overrides=EVEREST_C,
            checks=[("rock", "sky"), ("light", "sky"), ("tent", "ground"), ("tent2", "ground"), ("light", "rock")],
            fixes={"sky": ["sky2", "far", "mid"], "ground": ["mid", "near", "deep"]}),
    Concept("lm-great-wall", "landmark-great-wall", "Great Wall of China", great_wall,
            overrides={"stone": "#E2CFA6", "stone2": "#B39B72"},
            checks=[("stone", "near"), ("stone", "mid"), ("stone", "far"), ("far", "sky")],
            fixes={"near": ["deep", "mid"], "mid": ["near", "deep"], "far": ["mid", "near"]}),
    Concept("lm-fuji-sakura", "landmark-mount-fuji", "Mount Fuji", fuji_sakura,
            overrides={"fuji": "#5E7FB5", "blossom": "#F6B8C8", "pagoda": "#D2452F", "pagoda2": "#E2B04A"},
            checks=[("fuji", "sky"), ("light", "fuji"), ("blossom", "sky"), ("blossom", "near"), ("pagoda", "fuji"), ("mid", "fuji")],
            fixes={"blossom": ["#EE8FAA", "#E57A9B", "pop"], "mid": ["near", "deep"], "near": ["deep", "mid"]}),
    Concept("lm-fushimi-gates", "landmark-fushimi-inari", "Fushimi Inari gates", fushimi_gates, overrides=FUSHIMI,
            checks=[("torii", "deep"), ("torii", "near"), ("torii", "ground"), ("torii", "glow")],
            fixes={"near": ["deep", "mid"], "glow": ["glow2", "light"], "ground": ["mid", "far", "near"]}),
    Concept("lm-angkor-sunrise", "landmark-angkor-wat", "Angkor Wat", angkor_sunrise,
            overrides={"lily": "#5E9C6A"},
            checks=[("dark", "glow"), ("dark", "sky"), ("far", "deep"), ("dark", "far")],
            fixes={"sky": ["sky2", "far", "glow2"], "far": ["sky2", "glow2", "light"]}),
    Concept("lm-petra-treasury", "landmark-petra", "Petra Treasury", petra_treasury, overrides=PETRA,
            checks=[("facade", "rock3"), ("siq", "rock"), ("ground", "siq")],
            fixes={"ground": ["#E9C9A0", "light"]}),
    Concept("lm-burj-khalifa", "landmark-burj-khalifa", "Burj Khalifa", burj_khalifa, overrides=GLASS,
            checks=[("glass", "sky"), ("glass2", "sky"), ("glass", "far"), ("glass", "glow"), ("glass2", "mid")],
            fixes={"sky": ["sky2", "far", "mid", "near"], "far": ["mid", "near", "deep"], "mid": ["near", "deep"], "glow": ["glow2", "pop"]}),
    Concept("lm-sigiriya-rock", "landmark-sigiriya", "Sigiriya Lion Rock", sigiriya, overrides=SIGIRIYA,
            checks=[("rock", "sky"), ("rock", "far"), ("paw", "mid"), ("paw", "ground"), ("near", "rock")],
            fixes={"sky": ["sky2", "light"], "far": ["sky2", "light", "mid"], "mid": ["near", "deep"], "ground": ["near", "deep"], "near": ["deep", "mid"]}),
    Concept("lm-petronas-towers", "landmark-petronas-towers", "Petronas Towers", petronas_towers, overrides=STEEL,
            checks=[("steel", "sky"), ("steel", "glow"), ("steel", "far"), ("steel", "near")],
            fixes={"sky": ["sky2", "far", "mid"], "glow": ["glow2", "pop", "hero"], "far": ["mid", "near", "deep"], "near": ["deep", "mid"]}),
    Concept("lm-halong-junk", "landmark-ha-long-bay", "Ha Long Bay", ha_long_bay, ["coastal", "meadow", "blush", "dusk"], overrides=HALONG,
            checks=[("sail", "near"), ("sail", "sky"), ("near", "sea"), ("mid", "sea"), ("far", "sky"), ("mid", "far")],
            fixes={"sky": ["light", "sky2"], "near": ["deep", "mid"], "mid": ["near", "deep"]}),
    Concept("lm-borobudur-stupas", "landmark-borobudur", "Borobudur", borobudur, overrides=BORO,
            checks=[("stone", "sky"), ("stone", "glow"), ("stone", "far"), ("deep", "near")],
            fixes={"glow": ["glow2", "light", "pop"], "far": ["mid", "sky2", "near"], "near": ["mid", "ground"]}),
    Concept("lm-forbidden-city", "landmark-forbidden-city", "Forbidden City", forbidden_city, overrides=FORBIDDEN,
            checks=[("roof", "sky"), ("marble", "far"), ("roof", "far"), ("marble", "ground"), ("red", "far")],
            fixes={"sky": ["sky2", "far", "mid"], "far": ["mid", "near", "deep"], "ground": ["mid", "near"]}),
    Concept("lm-hagia-sophia", "landmark-hagia-sophia", "Hagia Sophia", hagia_sophia, overrides=HAGIA,
            checks=[("wall", "sky"), ("lead", "sky"), ("minaret", "sky"), ("deep", "near"), ("wall", "near")],
            fixes={"sky": ["sky2", "far", "mid"], "near": ["mid", "deep", "ground"]}),
]
