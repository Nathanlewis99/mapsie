"""Mapsie Originals: famous landmarks of Asia, second set (India, China, Japan, Korea, SE Asia, Himalaya, Silk Road)."""
import math

from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group, balloon  # noqa: F401


# ================================================================ private helpers (copied from landmarks_asia.py)
def poly(*pts, close=True) -> str:
    s = "M" + " L".join(f"{x:g} {y:g}" for x, y in pts)
    return s + ("Z" if close else "")


def arch(x, y, w, h) -> str:
    """Round-topped opening, (x, y) top-left of its bounding box."""
    r = w / 2
    return f"M{x:g} {y + h:g} V{y + r:g} A{r:g} {r:g} 0 0 1 {x + w:g} {y + r:g} V{y + h:g}Z"


def parch(x, y, w, h) -> str:
    """Pointed (Islamic / Mughal) arch opening, (x, y) top-left of its bounding box."""
    return (f"M{x:g} {y + h:g} V{y + w * .55:g} Q{x:g} {y + w * .12:g} {x + w / 2:g} {y:g} "
            f"Q{x + w:g} {y + w * .12:g} {x + w:g} {y + w * .55:g} V{y + h:g}Z")


def pagoda_roof(cx, y, w, h=7.0) -> str:
    """Upturned east-asian eave: tips at (cx±w, y-5)."""
    return (f"M{cx - w:g} {y - 5:g} Q{cx - w * .78:g} {y + 2:g} {cx - w * .58:g} {y + 2:g} H{cx + w * .58:g} "
            f"Q{cx + w * .78:g} {y + 2:g} {cx + w:g} {y - 5:g} Q{cx + w * .62:g} {y - 3:g} {cx + w * .44:g} {y - h:g} "
            f"H{cx - w * .44:g} Q{cx - w * .62:g} {y - 3:g} {cx - w:g} {y - 5:g}Z")


def hip_roof(cx, y, w, top_w, h, lift=6) -> str:
    """Hip roof: upswept eave tips at (cx±w, y-lift), ridge (cx±top_w, y-h)."""
    return (f"M{cx - w:g} {y - lift:g} Q{cx - w * .86:g} {y + 2:g} {cx - w * .66:g} {y + 2:g} H{cx + w * .66:g} "
            f"Q{cx + w * .86:g} {y + 2:g} {cx + w:g} {y - lift:g} Q{cx + w * .7:g} {y - 4:g} {cx + top_w + (w - top_w) * .35:g} {y - h * .55:g} "
            f"L{cx + top_w:g} {y - h:g} H{cx - top_w:g} L{cx - top_w - (w - top_w) * .35:g} {y - h * .55:g} "
            f"Q{cx - w * .7:g} {y - 4:g} {cx - w:g} {y - lift:g}Z")


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


FLAGS = {"fb": "#3D6FB6", "fw": "#FFFFFF", "fr": "#D64541", "fg": "#3E9A5B", "fy": "#F2C14E"}


def palm(d: Drawing, x, base, h, lean=0.0, role="dark", s=1.0):
    """Coconut palm silhouette: curved trunk and a spray of fronds."""
    tx, ty = x + lean, base - h
    d.limb(role, f"M{x} {base} Q{x + lean * .2} {base - h * .5} {tx} {ty}", 3.2 * s)
    fr = ""
    for ang, L in [(-160, 20), (-125, 18), (-90, 14), (-55, 18), (-20, 20), (-190, 14), (10, 14)]:
        a = math.radians(ang)
        ex, ey = tx + math.cos(a) * L * s, ty + math.sin(a) * L * s + (6 * s if abs(ang + 90) > 50 else 0)
        mx, my = tx + math.cos(a) * L * s * .55, ty + math.sin(a) * L * s * .55 - 3 * s
        nx, ny = -math.sin(a), math.cos(a)
        fr += (f"M{tx:.1f} {ty:.1f} Q{mx + nx * 3 * s:.1f} {my + ny * 3 * s:.1f} {ex:.1f} {ey:.1f} "
               f"Q{mx - nx * 1 * s:.1f} {my - ny * 1 * s:.1f} {tx:.1f} {ty:.1f}Z ")
    d.shape(role, fr)


def karst(x, base, w, h, lean=0.0) -> str:
    return (f"M{x - w / 2:.1f} {base:.1f} C{x - w / 2 - 3:.1f} {base - h * .5:.1f} {x - w * .5 + lean:.1f} {base - h * .9:.1f} "
            f"{x - w * .12 + lean:.1f} {base - h:.1f} C{x + w * .12 + lean:.1f} {base - h * 1.05:.1f} {x + w * .42 + lean:.1f} {base - h * .94:.1f} "
            f"{x + w * .46 + lean * .6:.1f} {base - h * .7:.1f} C{x + w * .54:.1f} {base - h * .45:.1f} {x + w / 2 + 4:.1f} {base - h * .2:.1f} "
            f"{x + w / 2:.1f} {base:.1f}Z")


def pine(x, base, h, w) -> str:
    """Japanese pine: a few flat cloud-like foliage pads on a leaning trunk (pads only)."""
    return " ".join(ellipse(x + dx * w, base - h * dy, w * rx, h * ry)
                    for dx, dy, rx, ry in [(0, .95, .55, .09), (-.35, .72, .6, .1), (.4, .55, .62, .1)])


def reflect(d: Drawing, clip_id, clip_d, axis_y, draw, opacity=.35, transform=""):
    """Papercut-only mirror image of `draw` below `axis_y`, clipped to the water."""
    if not d.paper:
        return
    d.raw(f'<clipPath id="{clip_id}"><path d="{clip_d}"/></clipPath><g clip-path="url(#{clip_id})">'
          f'<g opacity="{opacity}" transform="translate(0 {2 * axis_y}) scale(1 -1)"><g transform="{transform}">')
    draw()
    d.raw("</g></g></g>")


# ================================================================ GOLDEN TEMPLE (Harmandir Sahib, Amritsar)
def golden_temple_body(d: Drawing, sh=True, ln=True):
    S = dict(shadow=sh, line=ln)
    F = dict(shadow=False, line=ln)
    # corner kiosks (chhatris) on the roof
    for x in (70, 130):
        d.shape("gold", rrect(x - 5, 80, 10, 10, 1), **S)
        d.shape("gold", f"M{x - 7} 81 Q{x - 7} 72 {x} 69 Q{x + 7} 72 {x + 7} 81Z", **S)
        d.stroke("gold2", f"M{x} 69 V64", 1.2, line=ln)
    # fluted lotus dome on its drum
    d.shape("gold", rrect(86, 78, 28, 10, 1), **S)
    d.shape("gold", "M83 80 C78 70 84 60 94 55 Q99 52 100 47 Q101 52 106 55 C116 60 122 70 117 80Z", spot=True, **S)
    d.stroke("gold2", "M92 79 Q88 68 96 57 M100 79 V52 M108 79 Q112 68 104 57", 1.1, line=ln)
    d.stroke("gold2", "M100 47 V38", 1.6, line=ln)
    d.shape("gold2", "M95 42 Q100 37 105 42Z", shadow=False, line=False)
    # parapet, upper storey (gold) and cornice
    d.shape("gold", rrect(64, 88, 72, 5, 1), **S)
    d.shape("gold", rrect(66, 92, 68, 20, 0), **S)
    d.marks("gold2", " ".join(parch(x, 96, 6, 13) for x in (72, 83, 94, 105, 116, 126)))
    d.shape("gold2", rrect(62, 111, 76, 4, 1), **S)
    # ground storey: gold above, white marble below
    d.shape("gold", rrect(64, 114, 72, 12, 0), **S)
    d.shape("marble", rrect(64, 124, 72, 10, 0), **F)
    d.shape("gold2", parch(93, 114, 14, 20), **F)
    d.marks("gold2", " ".join(parch(x, 116, 6, 9) for x in (70, 80, 114, 124)))
    # marble causeway with its golden lamps
    d.shape("marble", "M-60 126 H66 V136 H-60Z", **S)
    d.stroke("shade", "M-60 131 H64", 1.2, line=False)
    for x in (10, 28, 46):
        d.stroke("gold2", f"M{x} 126 V117", 1.4, line=ln)
        d.shape("gold", ellipse(x, 116, 2.4, 3), **F)


GT_T = "translate(100 142) scale(1.2) translate(-100 -134)"


def golden_temple(d: Drawing):
    d.disc("glow", 156, 46, 14)
    birds(d, [(30, 52, 1), (44, 44, .8)])
    # white arcade (parikrama buildings) around the pool
    d.shape("marble2", "M-30 142 V118 H14 V110 L20 104 L26 110 V118 H174 V110 L180 104 L186 110 V118 H230 V142Z", line=False)
    if d.paper:
        d.marks("shade", " ".join(arch(x, 124, 5, 9) for x in range(-24, 230, 10)))
    d.band("pool", "M-30 142 H230")
    reflect(d, "lm2gtpool", "M-30 142 H230 V230 H-30Z", 142, lambda: golden_temple_body(d, sh=False, ln=False), .4, GT_T)
    d.stroke("light", "M70 158 h18 M112 166 h22 M36 174 h14 M152 154 h16 M126 182 h20", 1.6)
    group(d, GT_T, lambda: golden_temple_body(d))
    d.band("pool2", "M-30 188 Q100 182 230 188", line=False)


GOLDEN_T = {"gold": "#EDB53C", "gold2": "#A8761C", "marble": "#FBF8F1", "marble2": "#EFE7DA", "shade": "#C9B9A0",
            "pool": "#4E8FA6", "pool2": "#3F7A90"}


# ================================================================ HAWA MAHAL (Jaipur)
def jharokha(d: Drawing, x, y, w, h, spot=False):
    """A projecting bay window: pale box, domed cap, dark lattice opening."""
    d.shape("pink2", rrect(x, y, w, h, 1), line=False)
    d.shape("pink", f"M{x - 1} {y + 1} Q{x - 1} {y - w * .55} {x + w / 2} {y - w * .75} Q{x + w + 1} {y - w * .55} {x + w + 1} {y + 1}Z", spot=spot)
    d.marks("win", arch(x + w * .28, y + 3, w * .44, h - 5))


def hawa_mahal(d: Drawing):
    d.disc("glow", 162, 50, 13)
    birds(d, [(26, 64, .9), (38, 56, .7)])
    # five storeys stepping up to the crowned centre
    tiers = [(146, 178, 12, 188), (118, 146, 18, 182), (92, 118, 32, 168), (68, 92, 50, 150), (46, 68, 68, 132)]
    for y0, y1, x0, x1 in tiers:
        d.shape("pink", rrect(x0, y0, x1 - x0, y1 - y0 + 2, 0))
    # crown: curved central gable with three little domes
    d.shape("pink", "M76 48 Q76 30 100 22 Q124 30 124 48Z")
    d.stroke("light", "M81 46 Q83 33 100 27 Q117 33 119 46", 1.3, line=False)
    d.marks("win", arch(95, 33, 10, 12))
    for x, y, r in [(100, 20, 4.5), (70, 46, 3.6), (130, 46, 3.6)]:
        d.shape("pink2", f"M{x - r} {y + 1} Q{x - r} {y - r * 1.2} {x} {y - r * 1.6} Q{x + r} {y - r * 1.2} {x + r} {y + 1}Z")
        d.stroke("win", f"M{x} {y - r * 1.6} V{y - r * 2.4}", 1, line=False)
    # rows of domed jharokhas (bay windows)
    rows = [(54, 70, 130, 10), (77, 52, 148, 10), (102, 34, 166, 10), (128, 20, 180, 10), (156, 14, 186, 10)]
    for y, x0, x1, w in rows:
        n = int((x1 - x0) // (w + 2))
        gap = ((x1 - x0) - n * w) / (n + 1)
        for i in range(n):
            x = x0 + gap + i * (w + gap)
            jharokha(d, x, y, w, 12 if y < 150 else 11, spot=(i % 2 == 0 and y == 102))
    for y0, y1, x0, x1 in tiers:
        d.stroke("light", f"M{x0} {y1} H{x1}", 1.4, line=False)
    # gateway at street level
    d.shape("pink2", rrect(88, 170, 24, 10, 0), shadow=False)
    d.marks("win", arch(93, 170, 14, 10))
    d.band("ground", "M-30 178 Q100 174 230 178")
    d.band("deep", hills(190, 3, 20), line=False)


HAWA = {"pink": "#E28A6F", "pink2": "#EFA488", "win": "#7A3530", "light": "#FFF4EC"}


# ================================================================ VARANASI GHATS
def shikhara(x, base, w, h) -> str:
    """North-Indian temple spire (curvilinear tower) with an amalaka cap."""
    return (f"M{x - w} {base} C{x - w * 1.05} {base - h * .5} {x - w * .7} {base - h * .85} {x} {base - h} "
            f"C{x + w * .7} {base - h * .85} {x + w * 1.05} {base - h * .5} {x + w} {base}Z "
            + ellipse(x, base - h - 1.5, w * .42, 2.2))


def parasol(d: Drawing, x, base, r):
    d.stroke("dark", f"M{x} {base} V{base - r * 1.3}", 1.3)
    d.shape("straw", f"M{x - r} {base - r * .95} Q{x} {base - r * 1.9} {x + r} {base - r * .95} Q{x} {base - r * 1.15} {x - r} {base - r * .95}Z")


def varanasi(d: Drawing):
    d.disc("glow", 160, 56, 20)
    birds(d, [(118, 36, .9), (132, 30, .7)])
    # skyline of old riverfront buildings and temple spires
    d.shape("b3", poly((-30, 112), (-30, 70), (-6, 70), (-6, 60), (14, 60), (14, 74), (30, 74), (30, 112)))
    d.shape("b1", shikhara(42, 80, 9, 36))
    d.shape("pop", "M42 42 V32 L50 35 L42 38", shadow=False)
    d.shape("b2", poly((26, 112), (26, 80), (60, 80), (60, 112)))
    d.shape("b3", poly((58, 112), (58, 64), (84, 64), (84, 112)))
    d.shape("b1", poly((82, 112), (82, 76), (112, 76), (112, 112)))
    d.shape("b1", shikhara(98, 76, 8, 28))
    d.shape("b2", poly((110, 112), (110, 86), (150, 86), (150, 112)))
    d.shape("b3", poly((148, 112), (148, 94), (230, 94), (230, 112)))
    wins = ""
    for x0, x1, y0, y1 in [(-24, 26, 76, 104), (30, 56, 86, 104), (62, 80, 70, 104), (86, 108, 82, 104), (114, 146, 92, 104), (152, 196, 100, 104)]:
        for y in range(y0, y1, 11):
            for x in range(x0, x1 - 3, 8):
                wins += arch(x, y, 4, 7) + " "
    d.marks("win", wins)
    # the ghat steps down to the river
    d.shape("step", "M-30 110 H230 V142 H-30Z")
    d.stroke("step2", " ".join(f"M-30 {y} H230" for y in range(116, 142, 5)), 1.3, line=False)
    d.shape("step2", "M60 110 H76 V142 H60Z M150 110 H166 V142 H150Z", shadow=False, line=False)
    for x, b, r in [(22, 128, 11), (44, 134, 12), (104, 126, 10), (126, 134, 12), (190, 130, 11)]:
        parasol(d, x, b, r)
    # the Ganges and a wooden rowing boat
    d.band("mid", "M-30 140 H230")
    d.stroke("light", "M130 152 h18 M156 148 h12 M30 176 h16 M150 182 h20", 1.6)
    d.stroke("glow", "M150 146 h20 M148 154 h24 M152 162 h16", 1.6, line=False)
    d.shape("boat", "M34 160 H130 Q124 176 108 178 H52 Q38 176 34 160Z", spot=True)
    d.shape("boat2", "M34 160 H130 L128 165 H36Z", shadow=False)
    d.stroke("dark", "M108 160 L134 182", 1.8)
    d.shape("straw", "M58 160 V146 Q78 140 98 146 V160Z")
    d.stroke("boat2", "M62 146 V160 M78 143 V160 M94 146 V160", 1, line=False)
    d.band("near", waves(186, 2.5, 22), line=False)


VARANASI = {"b1": "#E5B464", "b2": "#D8846A", "b3": "#F1E2C4", "win": "#6B4A3A", "step": "#D9C3A0", "step2": "#B89C76",
            "straw": "#C9A05A", "boat": "#8A5A36", "boat2": "#5E3B22"}


# ================================================================ GATEWAY OF INDIA (Mumbai)
def turret(d: Drawing, x, base, w, h):
    d.shape("stone", rrect(x - w / 2, base - h, w, h, 0))
    d.marks("stone2", " ".join(parch(x - w * .3 + k * w * .35, base - h + 4, w * .25, h * .55) for k in (0, 1)))
    d.shape("stone", rrect(x - w / 2 - 1.5, base - h - 2, w + 3, 3, 1), shadow=False)
    d.shape("stone", f"M{x - w / 2} {base - h - 1} Q{x - w / 2} {base - h - w * .9} {x} {base - h - w * 1.1} "
                     f"Q{x + w / 2} {base - h - w * .9} {x + w / 2} {base - h - 1}Z")
    d.stroke("stone2", f"M{x} {base - h - w * 1.1} V{base - h - w * 1.1 - 5}", 1.2)


def gateway_body(d: Drawing):
    # the central dome behind the facade
    d.shape("stone2", "M80 64 Q80 44 100 40 Q120 44 120 64Z")
    d.stroke("stone2", "M100 40 V33", 1.4)
    # wings
    for x0 in (26, 132):
        d.shape("stone", rrect(x0, 64, 42, 88, 0))
        d.shape("stone2", parch(x0 + 9, 104, 24, 48), shadow=False)
        d.shape("shade", parch(x0 + 13, 112, 16, 40), shadow=False)
        d.marks("stone2", " ".join(parch(x0 + 7 + k * 10, 74, 7, 16) for k in range(3)))
        d.stroke("stone2", f"M{x0} 96 H{x0 + 42}", 1.4, line=False)
    # central block with the great arch
    d.shape("stone", rrect(64, 52, 72, 100, 0))
    d.shape("stone2", parch(72, 74, 56, 78), shadow=False, spot=True)
    d.shape("shade", parch(80, 84, 40, 68), shadow=False)
    d.marks("stone2", " ".join(rrect(x, 58, 5, 9, 1) for x in range(70, 130, 8)))
    d.stroke("stone2", "M64 68 H136", 1.4, line=False)
    # cornice and the four corner turrets
    d.shape("stone", rrect(22, 62, 156, 5, 1))
    d.shape("stone", rrect(60, 50, 80, 5, 1))
    for x in (30, 170):
        turret(d, x, 62, 12, 14)
    for x in (66, 134):
        turret(d, x, 50, 11, 14)


def gateway_of_india(d: Drawing):
    d.disc("glow", 100, 76, 40)
    birds(d, [(30, 46, .9), (44, 38, .7), (158, 40, .8)])
    group(d, "translate(100 152) scale(.88) translate(-100 -152)", lambda: gateway_body(d))
    # harbour wall and the Arabian Sea
    d.shape("stone2", rrect(-30, 150, 260, 8, 0))
    d.band("sea", "M-30 158 H230")
    d.stroke("light", "M30 168 h16 M120 170 h22 M70 182 h14", 1.6)
    # a little ferry
    d.shape("boatw", "M136 172 H184 L178 182 H142Z")
    d.shape("boat", rrect(146, 164, 26, 8, 1.5))
    d.marks("dark", " ".join(rrect(x, 166, 3, 3, .5) for x in (149, 155, 161, 167)))
    d.stroke("dark", "M156 164 V156", 1.4)
    d.band("sea2", waves(188, 2.5, 22), line=False)


GATEWAY = {"stone": "#E2C389", "stone2": "#B8945C", "shade": "#7C5E3A", "sea": "#4F9AB5", "sea2": "#3E8099",
           "boat": "#3A6EA5", "boatw": "#F5F2EA"}


# ================================================================ POTALA PALACE (Lhasa)
def potala_windows(x0, x1, y0, y1, dx=7, dy=9) -> str:
    s = ""
    y = y0
    while y + 3.5 <= y1:
        x = x0
        while x + 2.4 <= x1:
            s += f"M{x - .6:.1f} {y + 3.6:.1f} L{x:.1f} {y:.1f} H{x + 2.4:.1f} L{x + 3:.1f} {y + 3.6:.1f}Z "
            x += dx
        y += dy
    return s


def potala(d: Drawing):
    d.disc("glow", 162, 40, 12)
    d.band("far", "M-30 100 L8 74 L32 88 L60 62 L88 84 L118 66 L146 80 L176 56 L230 86", line=False)
    # Marpo Ri hill
    d.band("hill", "M-30 156 Q20 142 50 146 Q100 136 150 144 Q190 140 230 154")
    # White Palace wings (battered walls stepping down to the sides)
    d.shape("white", poly((-6, 156), (-2, 118), (22, 116), (22, 156)) + " " + poly((178, 156), (178, 114), (200, 116), (206, 156)))
    d.shape("white", poly((12, 156), (17, 100), (60, 96), (60, 156)) + " " + poly((140, 156), (140, 92), (182, 96), (188, 156)))
    d.shape("band", poly((17, 100), (60, 96), (60, 101), (16.6, 105)) + " " + poly((140, 92), (182, 96), (182.4, 101), (140, 97)), shadow=False)
    d.marks("win", potala_windows(24, 56, 110, 150, 8, 10) + potala_windows(146, 180, 106, 150, 8, 10)
            + potala_windows(2, 20, 124, 150, 8, 10) + potala_windows(182, 198, 122, 150, 8, 10))
    # Red Palace in the middle, rising above a white base
    d.shape("white", poly((54, 156), (57, 86), (143, 86), (146, 156)))
    d.shape("red", poly((64, 130), (68, 52), (132, 52), (136, 130)), spot=True)
    d.shape("band", poly((68, 52), (132, 52), (132.3, 60), (67.6, 60)), shadow=False)
    d.marks("win", potala_windows(74, 126, 68, 124, 8, 10))
    d.marks("win", potala_windows(62, 138, 136, 152, 8, 9))
    # golden roofs on top of the Red Palace
    for cx, w in [(80, 10), (100, 12), (120, 10)]:
        d.shape("gold", pagoda_roof(cx, 52, w, 6))
        d.shape("gold", f"M{cx - 1.5} 46 L{cx} 40 L{cx + 1.5} 46Z", shadow=False)
    # zig-zag stairways climbing the hill
    d.stroke("white", "M8 174 L40 164 L14 160 M192 174 L160 164 L186 160", 3)
    d.band("ground", "M-30 172 Q100 166 230 172")
    d.band("deep", hills(190, 3, 20), line=False)


POTALA = {"white": "#F6F2E9", "red": "#A8332B", "band": "#5E2620", "win": "#3B2A24", "gold": "#E8B23A", "hill": "#8E7A5C"}


# ================================================================ TERRACOTTA ARMY (Xi'an)
def warrior(d: Drawing, x, base, s=1.0, face=True, spot=False, ln=True):
    """A standing terracotta infantryman, feet at (x, base), ~140 tall at s=1."""
    def draw():
        if not ln and not d.paper:
            return
        d.shape("clay", rrect(-17, -4, 34, 6, 1))
        # legs and square-toed shoes
        d.shape("clay2", rrect(-13, -32, 10, 30, 2) + " " + rrect(3, -32, 10, 30, 2))
        d.shape("clay3", rrect(-15, -8, 13, 6, 2) + " " + rrect(2, -8, 13, 6, 2), shadow=False)
        # robe skirt
        d.shape("clay", "M-18 -66 L-25 -28 Q0 -23 25 -28 L18 -66Z")
        d.stroke("clay2", "M-24 -32 Q0 -27 24 -32", 1.6, line=False)
        # armoured torso with rivets
        d.shape("clay", "M-21 -104 Q-25 -82 -18 -62 H18 Q25 -82 21 -104 Q0 -110 -21 -104Z", spot=spot)
        if face:
            riv = " ".join(circle(px, py, 1.1) for py in range(-96, -66, 7) for px in range(-14, 16, 7))
            d.marks("clay2", riv)
            d.stroke("clay2", "M-19 -70 H19", 1.6, line=False)
        # arms with hands clasped in front
        d.limb("clay3", "M-20 -100 Q-30 -78 -20 -64 Q-10 -58 -2 -62", 11, shadow=False)
        d.limb("clay3", "M20 -100 Q30 -78 20 -64 Q10 -58 2 -62", 11, shadow=False)
        d.shape("clay", ellipse(0, -62, 6.5, 5), shadow=False)
        # neck, head, hair and the side topknot
        d.shape("clay", rrect(-5, -113, 10, 10, 2))
        d.shape("clay", ellipse(0, -123, 10.5, 12.5))
        d.shape("clay", ellipse(-10.5, -121, 2.2, 3.4) + " " + ellipse(10.5, -121, 2.2, 3.4), shadow=False)
        d.shape("clay2", "M-11 -124 Q-12 -138 0 -139 Q12 -138 11 -124 Q7 -131 0 -131 Q-7 -131 -11 -124Z", shadow=False)
        d.shape("clay2", ellipse(6, -140, 5.2, 4.2))
        if face:
            d.marks("dark", ellipse(-4.2, -123, 1.6, 1) + " " + ellipse(4.2, -123, 1.6, 1))
            d.stroke("clay2", "M-7 -127 L-2 -126.5 M7 -127 L2 -126.5", 1.1)
            d.stroke("clay2", "M-6 -114 Q-3 -117 0 -115.6 Q3 -117 6 -114", 1.4)
    group(d, f"translate({x} {base}) scale({s})", draw)


def terracotta(d: Drawing):
    d.band("far", "M-30 -10 H230", line=False)
    d.band("mid", "M-30 58 H230", line=False)
    # three ranks in their earthen corridors, back to front
    for x in range(-6, 216, 22):
        warrior(d, x, 88, .4, face=False, ln=False)
    d.band("near", "M-30 82 H230")
    for x in range(-12, 222, 30):
        warrior(d, x, 124, .56, face=False, ln=False)
    d.band("near", "M-30 112 H230")
    d.band("ground", "M-30 160 H230", line=False)
    warrior(d, 36, 184, .8)
    warrior(d, 164, 184, .8)
    warrior(d, 100, 192, 1.0, spot=True)


CLAY = {"clay": "#C4946C", "clay2": "#8F6446", "clay3": "#B07F59"}


# ================================================================ LI RIVER KARSTS (Guilin)
def hump(x, base, w, h) -> str:
    """Guilin karst: a steep rounded sugarloaf hill."""
    return (f"M{x - w:.1f} {base:.1f} C{x - w * .9:.1f} {base - h * .55:.1f} {x - w * .6:.1f} {base - h:.1f} {x:.1f} {base - h:.1f} "
            f"C{x + w * .6:.1f} {base - h:.1f} {x + w * .9:.1f} {base - h * .55:.1f} {x + w:.1f} {base:.1f}Z")


def bamboo_raft(d: Drawing):
    # long, narrow bamboo raft with an upturned bow
    d.shape("raft", "M30 160 H136 Q154 160 166 144 L170 147 Q160 168 136 170 H34 Q26 168 30 160Z", spot=True)
    d.stroke("raft2", "M34 164 H150 M38 167 H136", 1.1, line=False)
    # cormorants perched on the raft
    for x in (48, 136):
        d.shape("dark", f"M{x - 4} 160 Q{x - 6} 150 {x - 1} 146 Q{x} 138 {x + 4} 139 L{x + 9} 140 L{x + 4} 142 Q{x + 3} 148 {x + 5} 152 Q{x + 6} 158 {x + 2} 160Z")
    # fisherman in a conical hat, poling the raft
    d.limb("dark", "M90 160 L88 146 M96 160 L98 146", 4.4, shadow=False)
    d.shape("dark", "M84 148 Q86 128 93 126 Q100 128 102 148Z")
    d.limb("dark", "M95 132 L108 138", 4, shadow=False)
    d.stroke("dark", "M122 98 L84 196", 1.8)
    d.shape("hat", "M78 124 L93 111 L108 124 Q93 128 78 124Z")
    # lantern hanging at the bow
    d.stroke("dark", "M156 150 V140 L162 136", 1.2)
    d.shape("pop", ellipse(162, 141, 3, 4))


def li_river(d: Drawing):
    d.disc("glow", 140, 62, 16)
    d.shape("mid", hump(40, 124, 16, 56) + " " + hump(70, 124, 14, 44) + " " + hump(112, 124, 15, 60)
            + " " + hump(142, 124, 13, 40) + " " + hump(176, 124, 16, 58) + " " + hump(10, 124, 12, 40), line=False)
    d.shape("light", cloud(116, 96, .9), shadow=False, line=False)
    d.shape("near", hump(-2, 130, 20, 70) + " " + hump(58, 130, 16, 52) + " " + hump(92, 130, 13, 36)
            + " " + hump(160, 130, 18, 50) + " " + hump(204, 130, 18, 64))
    d.shape("light", cloud(20, 108, .7), shadow=False, line=False)
    d.shape("deep", hump(-10, 136, 30, 104) + " " + hump(28, 136, 14, 60) + " " + hump(212, 136, 30, 88) + " " + hump(178, 136, 12, 46))
    d.band("river", "M-30 134 H230")
    if d.paper:
        d.raw('<g opacity=".3">')
        d.shape("deep", "M-30 134 H44 Q30 146 -10 156 Q-20 158 -30 158Z M230 134 H166 Q182 150 230 154Z", shadow=False)
        d.raw("</g>")
    d.stroke("river2", "M60 140 h18 M120 142 h22 M14 182 h16 M160 184 h20", 1.6)
    bamboo_raft(d)
    d.band("river2", waves(180, 2.5, 22), line=False)


LIRIVER = {"river": "#5EAFA6", "river2": "#8DCBC2", "raft": "#C9A15E", "raft2": "#8E6A35", "hat": "#E6C98A"}


# ================================================================ KINKAKU-JI (Kyoto)
def kinkaku_body(d: Drawing, sh=True, ln=True):
    S = dict(shadow=sh, line=ln)
    F = dict(shadow=False, line=ln)
    # fishing pavilion jutting over the pond
    d.shape("wood", rrect(134, 114, 18, 14, 0), **S)
    d.shape("roof", "M130 115 Q140 116 156 112 L150 108 H134Z", **S)
    # ground floor: natural wood and white panels
    d.shape("wood", rrect(66, 106, 68, 22, 0), **S)
    d.shape("paper", " ".join(rrect(x, 110, 7, 15, 0) for x in range(70, 130, 10)), **F)
    d.shape("roof", "M50 106 Q58 110 66 108 H134 Q142 110 150 106 L140 99 H60Z", **S)
    # middle floor: gold leaf, with balcony
    d.shape("gold", rrect(70, 82, 60, 18, 0), **S, spot=True)
    d.stroke("gold2", " ".join(f"M{x} 84 V98" for x in range(76, 128, 9)), 1, line=False)
    d.shape("gold2", rrect(66, 95, 68, 3, 0), **F)
    d.shape("roof", "M52 82 Q60 86 68 84 H132 Q140 86 148 82 L138 75 H62Z", **S)
    # top floor: gold, with bell-shaped windows
    d.shape("gold", rrect(82, 61, 36, 15, 0), **S)
    d.marks("gold2", " ".join(arch(x, 64, 6, 9) for x in (88, 97, 106)))
    d.shape("roof", "M64 62 Q72 66 80 64 H120 Q128 66 136 62 L106 42 H94Z", **S)
    # gilded phoenix on the ridge
    d.shape("gold", "M96 42 Q96 36 100 34 Q101 30 104 31 Q101 33 103 36 Q106 38 105 42Z", **S)


def kinkakuji(d: Drawing):
    d.disc("glow", 160, 44, 13)
    d.band("far", "M-30 104 Q-10 84 14 90 Q30 70 52 84 Q66 74 80 86 L120 86 Q136 70 152 82 Q170 66 190 84 Q210 76 230 88", line=False)
    d.band("near", "M-30 120 Q-14 100 4 108 Q16 92 34 104 Q48 94 60 110 L140 110 Q152 94 166 104 Q184 92 196 106 Q214 98 230 110")
    d.band("mid", "M-30 126 Q20 120 50 122 H150 Q180 120 230 124", line=False)
    d.band("pond", "M-30 128 H230")
    reflect(d, "lm2kkpond", "M-30 128 H230 V230 H-30Z", 128, lambda: kinkaku_body(d, sh=False, ln=False), .45)
    d.stroke("light", "M60 150 h18 M110 158 h22 M150 146 h14 M80 176 h16", 1.6)
    kinkaku_body(d)
    # rocky islets with little pines
    for x, y, w in [(28, 150, 20), (176, 158, 16)]:
        d.shape("rock", f"M{x - w} {y} Q{x - w * .6} {y - 7} {x} {y - 7} Q{x + w * .6} {y - 7} {x + w} {y}Z")
        d.limb("dark", f"M{x} {y - 6} Q{x + 3} {y - 14} {x - 1} {y - 22}", 2.4)
        d.shape("pine", ellipse(x - 1, y - 23, w * .6, 4.5) + " " + ellipse(x - 6, y - 15, w * .45, 3.5) + " " + ellipse(x + 6, y - 17, w * .45, 3.5))
    d.band("pond2", waves(184, 2.5, 22), line=False)


KINKAKU = {"gold": "#E9B23A", "gold2": "#A87A1E", "roof": "#4A3B34", "wood": "#8C6A4C", "paper": "#F4EEE0",
           "pond": "#4E8F8A", "pond2": "#3E7A76", "pine": "#3E6B47", "rock": "#7C7F78"}


# ================================================================ HIMEJI CASTLE
def gable(cx, y, w, h) -> str:
    return f"M{cx - w} {y} L{cx} {y - h} L{cx + w} {y}Z"


def keep_tier(d: Drawing, cx, y0, y1, hw, roof_w, spot=False):
    d.shape("wall", rrect(cx - hw, y0, hw * 2, y1 - y0, 0))
    d.shape("roof", hip_roof(cx, y0 + 2, roof_w, hw * .8, 9, 4), spot=spot)


def himeji(d: Drawing):
    d.disc("glow", 160, 44, 13)
    d.band("far", hills(150, 8, 20), line=False)
    # stone base with its curving battered walls
    d.shape("stone", "M34 156 Q44 142 50 124 H150 Q156 142 166 156Z")
    d.stroke("stone2", "M44 146 H156 M48 136 H152", 1.2, line=False)
    # small west keep
    d.shape("wall", rrect(18, 110, 30, 20, 0))
    d.shape("roof", hip_roof(33, 112, 22, 10, 9, 4))
    d.shape("wall", rrect(24, 94, 18, 14, 0))
    d.shape("roof", hip_roof(33, 96, 15, 4, 9, 4))
    d.shape("stone", "M10 156 Q16 142 18 130 H50 Q52 142 58 156Z")
    # main keep: white walls under grey tiled roofs with gables
    keep_tier(d, 100, 106, 126, 48, 58)
    d.shape("roof", gable(76, 104, 14, 12) + " " + gable(124, 104, 14, 12))
    d.shape("wall", gable(76, 102, 9, 7) + " " + gable(124, 102, 9, 7), shadow=False)
    keep_tier(d, 100, 88, 106, 42, 50, spot=True)
    d.shape("roof", gable(100, 86, 20, 15))
    d.shape("wall", gable(100, 84, 13, 9), shadow=False)
    keep_tier(d, 100, 72, 88, 34, 42)
    d.shape("roof", "M84 70 Q100 58 116 70 Q100 66 84 70Z")
    keep_tier(d, 100, 58, 72, 28, 36)
    d.shape("roof", gable(84, 56, 9, 8) + " " + gable(116, 56, 9, 8))
    d.shape("wall", rrect(80, 42, 40, 16, 0))
    d.shape("roof", hip_roof(100, 44, 32, 12, 12, 4))
    d.shape("roof", gable(100, 34, 12, 10))
    d.shape("roof2", "M84 31 Q82 25 86 23 Q86 27 88 29Z M116 31 Q118 25 114 23 Q114 27 112 29Z", shadow=False)
    # windows
    d.marks("win", " ".join(rrect(x, 114, 4, 6, .5) for x in (64, 74, 84, 112, 122, 132))
            + " " + " ".join(rrect(x, 94, 4, 6, .5) for x in (66, 76, 120, 130))
            + " " + " ".join(rrect(x, 77, 4, 6, .5) for x in (74, 84, 112, 122))
            + " " + " ".join(rrect(x, 62, 4, 6, .5) for x in (78, 88, 108, 118))
            + " " + " ".join(rrect(x, 47, 4, 6, .5) for x in (88, 98, 108))
            + " " + " ".join(rrect(x, 116, 3.5, 5, .5) for x in (24, 32, 40)))
    # cherry blossom
    d.band("near", "M-30 164 Q100 156 230 164")
    blossom(d, [(42, 160, 11), (58, 168, 9), (34, 174, 8), (158, 160, 11), (142, 168, 9), (168, 174, 8)])
    d.band("deep", hills(190, 3, 20), line=False)


HIMEJI = {"wall": "#FBF9F3", "roof": "#62707F", "roof2": "#3E4955", "stone": "#A39E92", "stone2": "#7E796F",
          "win": "#3E4955", "blossom": "#F6B8C8"}


# ================================================================ ITSUKUSHIMA FLOATING TORII
def o_torii(d: Drawing, sh=True, ln=True):
    S = dict(shadow=sh, line=ln)
    F = dict(shadow=False, line=ln)
    # auxiliary legs with their little roofs
    for x in (40, 70, 130, 160):
        d.shape("torii", rrect(x - 3.5, 92, 7, 64, 1), **S)
        d.shape("kuro", rrect(x - 6, 88, 12, 5, 1), **F)
    d.shape("torii", rrect(36, 104, 38, 4, 0) + " " + rrect(126, 104, 38, 4, 0), **F)
    # main pillars (slightly splayed)
    d.shape("torii", poly((50, 156), (54, 50), (64, 50), (66, 156)) + " " + poly((134, 156), (136, 50), (146, 50), (150, 156)), **S)
    # nuki tie beam, centre strut and plaque
    d.shape("torii", rrect(34, 76, 132, 8, 1), **S)
    d.shape("torii", rrect(95, 56, 10, 20, 0), **F)
    d.shape("kuro", rrect(92, 58, 16, 14, 1), **F)
    # shimaki and the black kasagi with upswept ends
    d.shape("torii", "M38 54 Q100 60 162 54 L160 62 Q100 66 40 62Z", **S)
    d.shape("kuro", "M26 40 Q100 54 174 40 L170 52 Q100 60 30 52Z", **S, spot=True)
    # dark feet where the tide laps
    d.shape("kuro", rrect(48, 150, 20, 6, 1) + " " + rrect(132, 150, 20, 6, 1), **F)


def itsukushima(d: Drawing):
    d.disc("glow", 100, 104, 40)
    d.band("far", "M-30 120 Q20 100 50 108 Q80 90 110 104 Q140 94 170 108 Q200 98 230 112", line=False)
    d.band("sea", "M-30 132 H230")
    reflect(d, "lm2itsea", "M-30 132 H230 V230 H-30Z", 156, lambda: o_torii(d, sh=False, ln=False), .35)
    d.stroke("light", "M14 146 h16 M176 150 h14 M84 170 h30 M40 184 h18 M150 186 h20", 1.6)
    o_torii(d)
    birds(d, [(150, 42, .9), (164, 34, .7)])
    d.band("sea2", waves(190, 2.5, 22), line=False)


ITSUKU = {"torii": "#E4482C", "kuro": "#2A2421", "sea": "#4E8FB0", "sea2": "#3E7A99"}


# ================================================================ GYEONGBOKGUNG (Seoul)
def gyeongbokgung(d: Drawing):
    d.disc("glow", 46, 50, 13)
    # Bugaksan, the granite peak behind the palace
    d.band("far", "M-30 110 Q20 92 60 96 Q96 56 128 50 Q150 48 166 74 Q190 92 230 96", line=False)
    d.shape("light", "M128 50 Q150 48 166 74 Q150 66 142 72 Q136 60 128 58Z", shadow=False, line=False)
    d.band("mid", "M-30 124 Q30 110 70 116 Q130 108 170 116 Q200 112 230 120")
    # two-tier stone terrace with balustrades
    for x0, y, w in [(28, 140, 144), (14, 152, 172)]:
        d.shape("stone", rrect(x0, y, w, 12, 1))
        d.stroke("stone2", f"M{x0} {y - 3} H{x0 + w} " + " ".join(f"M{x} {y - 6} V{y}" for x in range(int(x0) + 4, int(x0 + w), 10)), 1.3)
    d.shape("stone2", "M90 140 H110 L114 164 H86Z", shadow=False)
    d.stroke("stone", "M88 148 H112 M87 156 H113", 1.2, line=False)
    # lower storey: red columns and lattice doors
    d.shape("door", rrect(46, 112, 108, 28, 0))
    d.stroke("door2", " ".join(f"M{x} 116 V138" for x in range(52, 150, 4)), .8, line=False)
    d.shape("red", " ".join(rrect(x - 2.5, 110, 5, 30, 0) for x in (48, 61.5, 75, 88.5, 111.5, 125, 138.5, 152)))
    d.shape("green", rrect(42, 106, 116, 6, 0), shadow=False)
    # lower roof
    d.shape("roof", hip_roof(100, 108, 76, 56, 12, 9))
    d.stroke("roof2", "M30 98 Q100 104 170 98", 1.2, line=False)
    # upper storey
    d.shape("door", rrect(66, 78, 68, 20, 0))
    d.stroke("door2", " ".join(f"M{x} 81 V97" for x in range(70, 132, 4)), .8, line=False)
    d.shape("red", " ".join(rrect(x - 2.5, 76, 5, 22, 0) for x in range(68, 136, 13)))
    d.shape("green", rrect(62, 72, 76, 6, 0), shadow=False)
    # upper hip-and-gable roof with its heavy ridge
    d.shape("roof", hip_roof(100, 74, 62, 36, 26, 10), spot=True)
    d.shape("roof2", rrect(62, 46, 76, 5, 2))
    d.shape("roof2", "M62 49 Q58 42 61 38 Q63 43 66 46Z M138 49 Q142 42 139 38 Q137 43 134 46Z", shadow=False)
    d.stroke("roof2", " ".join(f"M{x} {54 + abs(x - 100) * .18:.0f} V{70 - abs(x - 100) * .05:.0f}" for x in range(70, 132, 6)), .9, line=False)
    d.band("ground", "M-30 164 H230")
    d.band("ground2", "M-30 180 H230", line=False)


GYEONG = {"roof": "#59616A", "roof2": "#3D444B", "red": "#B23A2C", "green": "#3D8C78", "door": "#C8754C", "door2": "#8E4A2E",
          "stone": "#E4DED2", "stone2": "#B4AC9E", "ground2": "#00000018"}


# ================================================================ BAGAN
def zedi(x, base, w) -> str:
    """Burmese bell stupa: stepped terraces, bell, rings and spire."""
    return (poly((x - w, base), (x - w, base - w * .3), (x - w * .8, base - w * .3), (x - w * .8, base - w * .55),
                  (x + w * .8, base - w * .55), (x + w * .8, base - w * .3), (x + w, base - w * .3), (x + w, base)) + " "
            f"M{x - w * .62:.1f} {base - w * .5:.1f} C{x - w * .6:.1f} {base - w * 1.1:.1f} {x - w * .3:.1f} {base - w * 1.3:.1f} {x - w * .14:.1f} {base - w * 1.5:.1f} "
            f"L{x:.1f} {base - w * 2.5:.1f} L{x + w * .14:.1f} {base - w * 1.5:.1f} C{x + w * .3:.1f} {base - w * 1.3:.1f} {x + w * .6:.1f} {base - w * 1.1:.1f} {x + w * .62:.1f} {base - w * .5:.1f}Z")


def pahto(x, base, w) -> str:
    """Bagan temple: square hall, stepped terraces and a curving shikhara spire."""
    return (poly((x - w, base), (x - w, base - w * .7), (x - w * .8, base - w * .7), (x - w * .8, base - w * .9),
                 (x - w * .6, base - w * .9), (x - w * .6, base - w * 1.05), (x + w * .6, base - w * 1.05), (x + w * .6, base - w * .9),
                 (x + w * .8, base - w * .9), (x + w * .8, base - w * .7), (x + w, base - w * .7), (x + w, base)) + " "
            f"M{x - w * .42:.1f} {base - w * 1:.1f} C{x - w * .44:.1f} {base - w * 1.5:.1f} {x - w * .2:.1f} {base - w * 1.8:.1f} {x - w * .08:.1f} {base - w * 1.95:.1f} "
            f"L{x:.1f} {base - w * 2.6:.1f} L{x + w * .08:.1f} {base - w * 1.95:.1f} C{x + w * .2:.1f} {base - w * 1.8:.1f} {x + w * .44:.1f} {base - w * 1.5:.1f} {x + w * .42:.1f} {base - w * 1:.1f}Z")


def bagan(d: Drawing):
    d.disc("glow", 80, 100, 40)
    d.disc("glow2", 80, 100, 26, shadow=False, line=False)
    group(d, "translate(118 14) scale(.34)", lambda: balloon(d))
    group(d, "translate(22 34) scale(.22)", lambda: balloon(d, body="pop", stripes="light", centre="hero2"))
    group(d, "translate(166 64) scale(.15)", lambda: balloon(d, body="hero2", stripes="light", centre="pop"))
    d.shape("far", zedi(22, 124, 8) + " " + pahto(50, 124, 9) + " " + zedi(104, 124, 7) + " " + pahto(126, 124, 8)
            + " " + zedi(160, 124, 9) + " " + zedi(84, 124, 5) + " " + pahto(186, 124, 7), line=False)
    d.band("far", "M-30 122 H230", line=False)
    d.shape("mid", pahto(14, 142, 14) + " " + zedi(66, 142, 9) + " " + zedi(96, 142, 12) + " " + pahto(186, 142, 12))
    d.band("mid", "M-30 138 Q60 134 120 138 T230 136")
    # the great temple in the foreground
    d.shape("brick", pahto(132, 170, 36), spot=True)
    d.marks("brick2", " ".join(arch(x, 154, 7, 14) for x in (110, 128.5, 147)) + " " + arch(128.5, 136, 7, 7))
    d.stroke("brick2", "M100 145 H164 M107 138 H157", 1.3, line=False)
    d.shape("gold", "M129 87 L132 72 L135 87Z", shadow=False)
    d.shape("brick", zedi(44, 172, 18))
    d.stroke("brick2", "M28 162 H60", 1.3, line=False)
    # trees
    d.shape("near", ellipse(80, 164, 14, 9) + " " + ellipse(92, 168, 10, 7) + " " + ellipse(-2, 166, 16, 10) + " " + ellipse(196, 168, 14, 9))
    d.band("near", "M-30 170 Q60 166 120 170 T230 168")
    d.band("deep", hills(188, 3, 20), line=False)


BAGAN = {"brick": "#B4603E", "brick2": "#7E3C26", "gold": "#E8B23A"}


# ================================================================ WAT ARUN (Bangkok)
def lotus_tower(x, base, w, h, tiers=6) -> str:
    """Khmer-style prang: tiered, swelling, then tapering to a point."""
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


def prang(d: Drawing, x, base, s=1.0, spot=False, w=13.0, h=84.0):
    """Wat Arun prang: stepped terraces, a tall corn-cob tower and a trident finial."""
    def hw(py):
        t = (-30 - py) / h
        return w * (1 - t ** 1.7) ** .6 if 0 <= t <= 1 else 0

    def draw():
        d.shape("prang2", poly((-28, 0), (-28, -10), (-22, -10), (-22, -20), (-17, -20), (-17, -30), (17, -30), (17, -20),
                               (22, -20), (22, -10), (28, -10), (28, 0)))
        d.stroke("prang", "M-28 -5 H28 M-22 -15 H22 M-17 -25 H17", 1.4, line=False)
        d.shape("prang", lotus_tower(0, -30, w, h, 8), spot=spot)
        # bands of porcelain mosaic
        dots = ""
        for k, py in enumerate(range(int(-30 - h * .85), -36, 9)):
            n = int(hw(py) // 3.2)
            dots += " ".join(circle(px * 3.2 + (1.6 if k % 2 else 0), py, 1.15) for px in range(-n, n) if abs(px * 3.2 + (1.6 if k % 2 else 0)) < hw(py) - 2.5) + " "
        d.marks("tile", dots)
        d.stroke("tile2", " ".join(f"M{-hw(py) + 1.5:.1f} {py + 4.5} H{hw(py) - 1.5:.1f}" for py in range(int(-30 - h * .8), -36, 18)), 1.3, line=False)
        d.stroke("prang2", f"M0 {-30 - h - 4} V{-30 - h - 16} M-3 {-30 - h - 12} L0 {-30 - h - 16} L3 {-30 - h - 12}", 1.4)
        d.marks("dark", arch(-3.5, -46, 7, 10))
    group(d, f"translate({x} {base}) scale({s})", draw)


def wat_arun(d: Drawing):
    d.disc("glow", 156, 60, 16)
    birds(d, [(26, 46, .9), (40, 38, .7)])
    d.band("far", "M-30 140 Q100 132 230 140", line=False)
    prang(d, 42, 146, .52)
    prang(d, 158, 146, .52)
    prang(d, 100, 152, 1.0, spot=True, w=21, h=100)
    d.shape("prang2", rrect(4, 146, 192, 8, 1))
    d.band("river", "M-30 154 H230")
    d.stroke("river2", "M20 164 h16 M140 166 h22 M30 182 h14", 1.6)
    # long-tail boat
    d.shape("boat", "M52 172 H142 Q150 172 156 164 L158 166 Q154 180 140 182 H60 Q50 180 52 172Z")
    d.shape("pop", "M52 172 H156 L155 175 H53Z", shadow=False)
    d.limb("dark", "M60 172 L40 186", 2.4, shadow=False)
    d.shape("light", rrect(84, 164, 40, 8, 1.5))
    d.stroke("boat", "M88 164 V172 M100 164 V172 M112 164 V172", 1.2, line=False)
    d.band("river2", waves(190, 2.5, 22), line=False)


WATARUN = {"prang": "#EFE8DA", "prang2": "#C7BBA6", "tile": "#3E86B0", "tile2": "#D4573E", "river": "#7E8F6A", "river2": "#A3B08A",
           "boat": "#7A4A2A"}


# ================================================================ BANAUE RICE TERRACES
def banaue(d: Drawing):
    d.disc("glow", 150, 44, 13)
    d.band("far", "M-30 72 Q20 46 60 58 Q100 40 140 56 Q180 44 230 62", line=False)
    d.shape("light", cloud(30, 74, 1.1), shadow=False, line=False)
    d.shape("light", cloud(140, 66, .9), shadow=False, line=False)
    # contour terraces, back to front: walls (dark lip) then the paddy
    roles = ["r1", "r2", "r3", "r2", "r1", "r3", "r2", "r1", "r3", "r2"]
    for i in range(10):
        y = 80 + i * 11.5
        amp = 10 + i * 1.8
        edge = f"M-30 {y + amp * .4:.1f} Q30 {y - amp:.1f} 80 {y + amp * .3:.1f} T190 {y - amp * .2:.1f} T300 {y:.1f}"
        d.band("wall", edge)
        d.band(roles[i], f"M-30 {y + 2.4 + amp * .4:.1f} Q30 {y + 2.4 - amp:.1f} 80 {y + 2.4 + amp * .3:.1f} T190 {y + 2.4 - amp * .2:.1f} T300 {y + 2.4:.1f}", shadow=False, line=False)
        if i == 4:
            # an Ifugao house on stilts
            d.limb("dark", "M146 108 V128 M164 108 V128", 2.6, shadow=False)
            d.shape("hut", rrect(142, 100, 26, 10, 1))
            d.shape("thatch", "M136 102 L155 70 L174 102Z", spot=True)
            d.stroke("hut2", "M146 96 L155 80 L164 96", 1.1, line=False)
        if i == 7:
            d.shape("palm", ellipse(30, 148, 9, 7) + " " + ellipse(40, 152, 7, 5))
    d.band("deep", hills(192, 3, 20), line=False)


BANAUE = {"wall": "#4E6E34", "r1": "#9CC75E", "r2": "#7FB34D", "r3": "#B4D37A", "hut": "#7A5234", "hut2": "#5A3A22",
          "thatch": "#C99A55", "palm": "#3E6B3A"}


# ================================================================ ULUN DANU BRATAN (Bali)
def meru(d: Drawing, x, base, tiers, w0, w1, gap, spot=False):
    """Balinese meru: a shrine base with a stack of black thatch roofs shrinking upward."""
    d.shape("base", rrect(x - w0 * .55, base - 18, w0 * 1.1, 18, 1))
    d.shape("brick", rrect(x - w0 * .55, base - 18, w0 * 1.1, 4, 0), shadow=False)
    d.marks("dark", rrect(x - 3, base - 12, 6, 12, 1))
    y = base - 18
    for i in range(tiers):
        w = w0 + (w1 - w0) * i / max(tiers - 1, 1)
        h = gap
        d.shape("thatch", f"M{x - w:.1f} {y:.1f} Q{x - w * .6:.1f} {y - h * .2:.1f} {x - w * .58:.1f} {y - h:.1f} H{x + w * .58:.1f} "
                          f"Q{x + w * .6:.1f} {y - h * .2:.1f} {x + w:.1f} {y:.1f}Z", spot=spot and i == 0)
        y -= h + 1.4
        d.shape("base", rrect(x - w * .3, y, w * .6, 1.6, 0), shadow=False, line=False)
    d.shape("thatch", f"M{x - 3} {y + 1} L{x} {y - 6} L{x + 3} {y + 1}Z")


def ulun_danu(d: Drawing):
    d.disc("glow", 46, 56, 14)
    d.band("far", "M-30 108 Q20 70 70 80 Q110 60 150 70 Q190 64 230 90", line=False)
    d.band("mid", "M-30 122 Q40 108 90 114 Q150 104 230 116")
    d.band("lake", "M-30 128 H230")
    def shrines():
        d.shape("island", "M60 150 Q66 142 82 142 H166 Q178 142 184 150Z")
        meru(d, 152, 146, 3, 16, 9, 7)
        meru(d, 100, 146, 11, 22, 7, 6.2, spot=True)
    reflect(d, "lm2ulunlake", "M-30 150 H230 V230 H-30Z", 150, shrines, .32)
    shrines()
    d.limb("dark", "M178 146 Q180 120 186 104", 3)
    d.shape("near", ellipse(186, 102, 13, 9) + " " + ellipse(196, 112, 10, 7))
    d.stroke("light", "M20 160 h18 M120 166 h22 M40 180 h14 M150 182 h20", 1.6)
    # a little outrigger canoe
    d.shape("boat", "M14 170 H50 Q46 176 40 176 H20 Q14 176 14 170Z")
    d.stroke("dark", "M18 178 H48", 1.3)
    d.band("lake2", waves(190, 2.5, 22), line=False)


ULUN = {"thatch": "#33302C", "base": "#EDE4D2", "brick": "#B5653F", "island": "#8C8576", "lake": "#5C9EB5", "lake2": "#4A88A0",
        "boat": "#D9A441"}


# ================================================================ HOI AN LANTERNS
def lantern(d: Drawing, x, top, w, h, role, spot=False):
    d.stroke("dark", f"M{x} -10 V{top}", 1.2)
    d.shape("cap", rrect(x - w * .35, top, w * .7, 3.5, 1))
    body = (f"M{x - w * .35} {top + 3} C{x - w * 1.05} {top + h * .2} {x - w * 1.05} {top + h * .8} {x - w * .35} {top + h - 3} "
            f"H{x + w * .35} C{x + w * 1.05} {top + h * .8} {x + w * 1.05} {top + h * .2} {x + w * .35} {top + 3}Z")
    d.shape(role, body, spot=spot)
    d.stroke("cap", f"M{x - w * .3} {top + 4} Q{x - w * .62} {top + h / 2} {x - w * .3} {top + h - 4} M{x} {top + 4} V{top + h - 4} "
                    f"M{x + w * .3} {top + 4} Q{x + w * .62} {top + h / 2} {x + w * .3} {top + h - 4}", 1, line=False)
    d.shape("cap", rrect(x - w * .35, top + h - 3.5, w * .7, 3.5, 1), shadow=False)
    d.stroke(role, f"M{x} {top + h} V{top + h + 9} M{x - 2} {top + h + 1} V{top + h + 8} M{x + 2} {top + h + 1} V{top + h + 8}", 1.2)


def hoi_an(d: Drawing):
    # yellow shophouses with tiled roofs and wooden balconies
    for x0, x1, top, role in [(-30, 46, 92, "wall"), (44, 112, 82, "wall2"), (110, 168, 90, "wall"), (166, 230, 98, "wall2")]:
        d.shape(role, rrect(x0, top, x1 - x0, 150 - top, 0))
        d.shape("roof", f"M{x0 - 4} {top + 2} L{x0 + 6} {top - 10} H{x1 - 6} L{x1 + 4} {top + 2}Z")
        d.stroke("roof2", " ".join(f"M{x} {top - 8} V{top}" for x in range(int(x0) + 8, int(x1) - 6, 5)), .9, line=False)
        d.shape("wood", rrect(x0 + 6, top + 30, x1 - x0 - 12, 4, 0), shadow=False)
        d.stroke("wood", " ".join(f"M{x} {top + 22} V{top + 30}" for x in range(int(x0) + 8, int(x1) - 6, 5)), 1, line=False)
        for wx in range(int(x0) + 10, int(x1) - 14, 20):
            d.shape("wood", rrect(wx, top + 8, 10, 12, 0), shadow=False)
            d.shape("wood", rrect(wx, top + 40, 10, 18, 0), shadow=False)
    # river front and a little boat
    d.band("river", "M-30 150 H230")
    reflect(d, "lm2hoianriver", "M-30 150 H230 V230 H-30Z", 150, lambda: [d.shape(r, rrect(x0, 92, x1 - x0, 58, 0), shadow=False, line=False)
                                                                        for x0, x1, r in [(-30, 46, "wall"), (44, 112, "wall2"), (110, 168, "wall"), (166, 230, "wall2")]], .3)
    d.stroke("light", "M20 164 h14 M120 160 h20 M60 184 h16", 1.6)
    d.shape("boat", "M96 172 H164 Q160 182 150 184 H108 Q98 182 96 172Z")
    d.shape("roof", "M112 172 V164 Q130 158 148 164 V172Z")
    for x, y, r in [(40, 176, "l1"), (64, 170, "l2"), (178, 178, "l1")]:
        d.shape(r, f"M{x - 4} {y} Q{x} {y - 7} {x + 4} {y}Z", shadow=False)
        d.shape("cap", rrect(x - 4.5, y, 9, 2, .6), shadow=False)
    # lanterns strung across the street, big and close
    clip_open(d)
    d.stroke("dark", "M-10 22 Q100 50 210 22", 1.4)
    clip_close(d)
    for x, top, w, h, r, sp in [(42, 34, 12, 28, "l2", False), (66, 36, 15, 34, "l1", True), (100, 42, 13, 30, "l3", False),
                                (134, 36, 15, 34, "l1", False), (158, 34, 12, 28, "l2", False)]:
        lantern(d, x, top, w, h, r, sp)
    d.band("river2", waves(192, 2.5, 22), line=False)


HOIAN = {"l1": "#E2412E", "l2": "#F4B82E", "l3": "#E8762F", "cap": "#5A2E1E", "wall": "#F2C64E", "wall2": "#E9B13C",
         "roof": "#8E4B32", "roof2": "#6A3422", "wood": "#6B4429", "river": "#4E8C8A", "river2": "#3E7674", "boat": "#6B4429"}


# ================================================================ TIGER'S NEST (Paro Taktsang)
def bhutan_house(d: Drawing, x, y, w, h, roof=True):
    """White Bhutanese temple building with a dark red band under a little gold-roofed top."""
    d.shape("white", rrect(x, y, w, h, 0))
    d.shape("band", rrect(x, y, w, 5, 0), shadow=False)
    d.marks("win", " ".join(rrect(wx, y + 9, 3.6, 5, .5) for wx in range(int(x) + 3, int(x + w) - 3, 7)))
    if roof:
        d.shape("roof", f"M{x - 4} {y + 1} L{x + 4} {y - 6} H{x + w - 4} L{x + w + 4} {y + 1}Z")


def tigers_nest(d: Drawing):
    d.disc("glow", 44, 50, 13)
    birds(d, [(24, 76, .8), (38, 70, .6)])
    d.band("far", "M-30 132 Q10 104 40 112 Q60 100 80 116", line=False)
    # the sheer cliff, with the monastery perched on a ledge halfway up
    cliff = "M108 -10 H230 V230 H116 C108 200 112 170 104 150 C96 136 90 128 82 124 L80 118 C92 110 98 100 96 84 C94 60 100 30 108 -10Z"
    d.shape("rock", cliff)
    d.stroke("rock2", "M134 6 Q126 40 134 76 M160 0 Q154 50 162 104 M140 130 Q132 160 142 196 M186 20 Q178 80 188 140", 2.2)
    d.shape("rock2", "M108 -10 H126 C118 30 124 62 116 90 C112 104 106 112 98 118 L82 124 L80 118 C92 110 98 100 96 84 C94 60 100 30 108 -10Z", shadow=False, line=False)
    # the temple buildings, stepping along the ledge
    d.shape("rock", "M44 124 Q60 118 84 122 L100 150 Q86 144 76 152 Q66 140 44 124Z")
    bhutan_house(d, 46, 98, 26, 24)
    bhutan_house(d, 66, 74, 30, 48, roof=False)
    d.shape("roof", "M60 75 L70 64 H92 L102 75Z", spot=True)
    d.shape("gold", "M78 64 L81 54 L84 64Z", shadow=False)
    bhutan_house(d, 94, 88, 26, 32)
    bhutan_house(d, 112, 102, 22, 20)
    d.shape("white", rrect(42, 120, 96, 6, 0))
    # prayer flags strung to the ledge, forest below
    flags(d, -20, 104, 46, 112, 10, 6)
    d.band("near", "M-30 156 Q20 140 60 150 Q90 158 116 176 T230 190")
    for x, b, h in [(10, 168, 50), (32, 160, 40), (52, 164, 36), (72, 172, 32), (-8, 174, 42), (90, 182, 28)]:
        d.shape("pine", f"M{x - h * .2:.1f} {b} L{x} {b - h} L{x + h * .2:.1f} {b}Z")
    d.band("deep", hills(192, 3, 20), line=False)


TIGER = {"rock": "#7B746C", "rock2": "#5E5850", "white": "#F6F1E7", "band": "#8E2E25", "win": "#3A2A24", "roof": "#C98E3A",
         "gold": "#E8B23A", "pine": "#2F5A3C", **FLAGS}


# ================================================================ BOUDHANATH STUPA (Kathmandu)
def boudhanath(d: Drawing):
    d.disc("glow", 160, 50, 12)
    # prayer flags fanning out from the spire
    for x1, y1 in [(-20, 120), (-20, 80), (220, 120), (220, 80)]:
        flags(d, 100, 36, x1, y1, 4, 8, size=4, square=False)
    # stepped mandala terraces
    d.shape("white", rrect(6, 152, 188, 12, 1))
    d.shape("white", rrect(18, 142, 164, 12, 1))
    d.stroke("dome2", "M6 158 H194 M18 148 H182", 1.2, line=False)
    # the great whitewashed dome with saffron lotus arcs
    d.shape("white", "M30 144 C30 104 62 90 100 90 C138 90 170 104 170 144Z")
    d.shape("dome2", "M136 94 C158 102 170 118 170 144 H152 C152 122 146 106 136 94Z", shadow=False, line=False)
    d.stroke("saffron", " ".join(f"M{x} 118 Q{x + 8} 106 {x + 16} 118" for x in range(36, 160, 16)), 2.2, line=False)
    # harmika with the painted eyes
    d.shape("gold", rrect(76, 86, 48, 5, 1))
    d.shape("white", rrect(78, 64, 44, 23, 1))
    d.marks("dark", "M83 77 Q90 71 97 77 Q90 80 83 77Z M103 77 Q110 71 117 77 Q110 80 103 77Z")
    d.stroke("dark", "M83 71 Q90 67 97 71 M103 71 Q110 67 117 71 M100 77 Q103 79.5 100 82 Q97 83.5 100 85", 1.4)
    d.shape("pop", circle(100, 69, 1.4), shadow=False)
    # thirteen gilded steps and the parasol pinnacle
    d.shape("gold", poly((82, 64), (89, 32), (111, 32), (118, 64)), spot=True)
    d.stroke("gold2", " ".join(f"M{82 + (64 - y) * 7 / 32:.1f} {y} H{118 - (64 - y) * 7 / 32:.1f}" for y in range(38, 64, 2)), .9, line=False)
    d.shape("gold", "M84 34 Q100 22 116 34Z")
    d.shape("gold", rrect(97, 14, 6, 10, 1))
    d.stroke("gold2", "M100 14 V7", 1.6)
    # pilgrims' ground
    d.band("ground", "M-30 164 H230")
    d.stroke("dark", "M30 172 h10 M150 176 h12", 1.4, line=False)
    d.band("deep", hills(188, 3, 20), line=False)


BOUDHA = {"white": "#FAF7F0", "dome2": "#DCD4C4", "saffron": "#E8A23A", "gold": "#E5AC36", "gold2": "#A87A1E", **FLAGS}


# ================================================================ REGISTAN (Samarkand)
def melon_dome(cx, base, r) -> str:
    return f"M{cx - r} {base} C{cx - r * 1.15} {base - r * 1.2} {cx - r * .4} {base - r * 1.6} {cx} {base - r * 1.7} C{cx + r * .4} {base - r * 1.6} {cx + r * 1.15} {base - r * 1.2} {cx + r} {base}Z"


def minaret_tower(d: Drawing, x, base, top, w):
    d.shape("brick", poly((x - w, base), (x - w * .8, top), (x + w * .8, top), (x + w, base)))
    d.stroke("tile", " ".join(f"M{x - w * .95:.1f} {y} H{x + w * .95:.1f}" for y in range(int(top) + 8, int(base), 12)), 1.2, line=False)
    d.shape("tile", rrect(x - w - 1.5, top - 3, w * 2 + 3, 4, 1))
    d.shape("tile2", f"M{x - w} {top - 2} Q{x - w} {top - w * 2} {x} {top - w * 2.4} Q{x + w} {top - w * 2} {x + w} {top - 2}Z")


def pishtaq(d: Drawing, x0, x1, top, base, spot=False):
    """Monumental portal: a tall frame of tiles around a deep pointed-arch recess."""
    w = x1 - x0
    d.shape("brick", rrect(x0, top, w, base - top, 0))
    d.shape("tile", rrect(x0 + 3, top + 3, w - 6, base - top - 3, 0), shadow=False, spot=spot)
    d.shape("brick", parch(x0 + w * .16, top + 10, w * .68, base - top - 10), shadow=False)
    d.shape("tile2", parch(x0 + w * .24, top + 16, w * .52, base - top - 16), shadow=False)
    d.shape("shade", parch(x0 + w * .32, top + 30, w * .36, base - top - 30), shadow=False)
    d.stroke("light", f"M{x0 + 5} {top + 6} H{x1 - 5}", 1.2, line=False)


def registan(d: Drawing):
    d.disc("glow", 166, 40, 11)
    base = 160
    # ribbed turquoise domes on their drums
    for cx in (34, 166):
        d.shape("brick", rrect(cx - 18, 96, 36, 12, 0))
        d.stroke("tile", f"M{cx - 18} 100 H{cx + 18}", 2, line=False)
        d.shape("tile2", melon_dome(cx, 98, 17))
        d.stroke("tile", f"M{cx - 9} 98 Q{cx - 9} 80 {cx} 69 M{cx + 9} 98 Q{cx + 9} 80 {cx} 69 M{cx} 98 V69", 1.2, line=False)
        d.stroke("tile", f"M{cx} 69 V62", 1.4)
    # arcaded wings
    d.shape("brick", rrect(-30, 106, 260, base - 106, 0))
    d.stroke("tile", "M-30 111 H230", 2.2, line=False)
    d.marks("shade", " ".join(parch(x, 118, 10, 16) + " " + parch(x, 140, 10, 16) for x in [*range(-24, 48, 15), *range(142, 230, 15)]))
    # the great portal (pishtaq) flanked by minarets
    pishtaq(d, 56, 144, 54, base, spot=True)
    for x in (52, 148):
        minaret_tower(d, x, base, 52, 5.5)
    d.band("ground", "M-30 160 H230")
    d.stroke("ground2", "M-30 170 H230 M-30 180 H230 M30 160 L10 200 M70 160 L60 200 M100 160 V200 M130 160 L140 200 M170 160 L190 200", 1.1, line=False)


REGISTAN = {"brick": "#DDBA82", "tile": "#2F6FAE", "tile2": "#3DB2B4", "shade": "#6B4A2E", "ground2": "#00000018"}


# ================================================================ NINE ARCH BRIDGE (Ella)
def nine_arch(d: Drawing):
    d.disc("glow", 150, 46, 13)
    d.band("far", "M-30 76 Q30 50 80 60 Q130 44 170 56 Q200 50 230 62", line=False)
    d.band("hill", "M-30 92 Q30 66 80 76 Q130 60 170 72 Q200 66 230 78")
    # tea rows on the hills
    d.stroke("hill2", "M-30 90 Q20 78 60 82 M-30 98 Q30 86 80 90 M120 78 Q170 70 230 82 M120 88 Q170 80 230 90", 1.6, line=False)
    # the viaduct
    deck, foot = 96, 166
    pier, span = 6, 20
    x = -24
    body = f"M-30 {deck} H230 V{foot} H-30Z"
    holes = ""
    while x < 230:
        holes += f"M{x + pier} {foot} V{deck + 24} A{span / 2} {span / 2} 0 0 1 {x + pier + span} {deck + 24} V{foot}Z "
        x += pier + span
    d.raw('<g>', '<g>')
    if d.paper:
        d.raw(f'<path filter="url(#ps)" d="{body} {holes}" fill-rule="evenodd" fill="{d.c["stone"]}"/>')
    else:
        d.raw("", f'<path d="{body} {holes}" fill-rule="evenodd" fill="{d.c["paper"]}" stroke="{d.c["ink"]}" stroke-width="3" stroke-linejoin="round"/>')
    d.raw('</g>', '</g>')
    d.stroke("stone2", f"M-30 {deck + 8} H230 M-30 {deck + 12} H230", 1.2, line=False)
    # blue train crossing
    for x0 in (-40, 4, 48, 92):
        d.shape("train", rrect(x0, deck - 16, 42, 15, 3), spot=x0 == 92)
        d.shape("train2", rrect(x0, deck - 8, 42, 3, 0), shadow=False)
        d.marks("win", " ".join(rrect(wx, deck - 13, 5, 4, .6) for wx in range(x0 + 4, x0 + 38, 8)))
    d.shape("train", "M134 80 H140 Q148 80 150 90 V95 H134Z")
    d.marks("win", rrect(139, 83, 6, 5, .8))
    d.shape("light", cloud(150, 60, .7), shadow=False, line=False)
    # jungle
    d.band("jungle", "M-30 150 Q-10 132 10 142 Q24 126 42 140 Q58 128 74 146 Q92 136 108 150 Q126 134 144 146 Q160 130 178 142 Q196 128 212 144 Q222 136 230 140")
    d.band("jungle2", "M-30 172 Q0 158 30 168 Q60 154 90 170 Q120 158 150 170 Q180 156 230 168")
    d.band("deep", hills(190, 3, 20), line=False)


NINEARCH = {"stone": "#DCC8A6", "stone2": "#A8937A", "train": "#2E62A8", "train2": "#E8B23A", "win": "#16324F",
            "hill": "#86B060", "hill2": "#6E9A4C", "jungle": "#3F7A45", "jungle2": "#2E5E36"}


# ================================================================ catalogue
WATER = ["coastal", "meadow", "blush", "dusk"]

CONCEPTS = [
    Concept("lm2-goldentemple", "landmark-golden-temple", "Golden Temple", golden_temple, WATER, overrides=GOLDEN_T,
            checks=[("gold", "sky"), ("gold", "glow"), ("gold", "marble2"), ("gold", "pool"), ("marble2", "sky")],
            fixes={"glow": ["pop", "glow2", "hero"], "sky": ["sky2", "far", "mid"]}),
    Concept("lm2-hawamahal", "landmark-hawa-mahal", "Hawa Mahal", hawa_mahal, overrides=HAWA,
            checks=[("pink", "sky"), ("pink", "glow"), ("pink2", "ground")],
            fixes={"sky": ["sky2", "far", "light"], "glow": ["glow2", "light", "hero"], "ground": ["near", "mid", "deep"]}),
    Concept("lm2-varanasi", "landmark-varanasi", "Varanasi ghats", varanasi, overrides=VARANASI,
            checks=[("b3", "sky"), ("b1", "sky"), ("step", "mid"), ("boat", "mid"), ("glow", "sky")],
            fixes={"b3": ["b2"], "sky": ["sky2", "far", "mid"], "mid": ["near", "deep"], "glow": ["pop", "glow2"]}),
    Concept("lm2-gateway", "landmark-gateway-of-india", "Gateway of India", gateway_of_india, WATER, overrides=GATEWAY,
            checks=[("stone", "sky"), ("stone", "glow")],
            fixes={"glow": ["hero", "pop", "near"], "sky": ["sky2", "hero", "far", "mid"]}),
    Concept("lm2-potala", "landmark-potala-palace", "Potala Palace", potala, overrides={**POTALA},
            checks=[("white", "sky"), ("white", "far"), ("red", "far"), ("white", "hill"), ("far", "sky")],
            fixes={"sky": ["#A9CFE8", "#7FB2DA"], "far": ["mid", "near", "deep"]}),
    Concept("lm2-terracotta", "landmark-terracotta-army", "Terracotta Army", terracotta, overrides=CLAY,
            checks=[("clay", "near"), ("clay", "ground"), ("clay", "mid"), ("clay3", "ground")],
            fixes={"near": ["deep", "mid", "far"], "ground": ["far", "light", "sky2", "deep"], "mid": ["far", "deep", "sky2"]}),
    Concept("lm2-liriver", "landmark-guilin", "Li River karsts", li_river, WATER, overrides=LIRIVER,
            checks=[("mid", "sky"), ("near", "mid"), ("deep", "near"), ("deep", "river"), ("raft", "river"), ("dark", "river")],
            fixes={"mid": ["far"], "deep": ["dark"], "river": ["#4E9E96", "#7CC2BA"]}),
    Concept("lm2-kinkakuji", "landmark-kinkakuji", "Kinkaku-ji Golden Pavilion", kinkakuji, WATER, overrides=KINKAKU,
            checks=[("gold", "sky"), ("roof", "sky"), ("gold", "near"), ("near", "far"), ("roof", "far"), ("pine", "pond"), ("far", "sky")],
            fixes={"near": ["deep", "mid"], "far": ["mid", "sky2"], "sky": ["sky2", "light"]}),
    Concept("lm2-himeji", "landmark-himeji-castle", "Himeji Castle", himeji, overrides=HIMEJI,
            checks=[("wall", "sky"), ("roof", "sky"), ("stone", "far"), ("blossom", "near"), ("wall", "far")],
            fixes={"sky": ["sky2", "far", "#A9CFE8"], "far": ["mid", "near"], "blossom": ["#EE8FAA", "#E57A9B", "pop"], "near": ["deep", "mid"]}),
    Concept("lm2-itsukushima", "landmark-itsukushima", "Itsukushima floating torii", itsukushima, WATER, overrides=ITSUKU,
            checks=[("torii", "glow"), ("torii", "sea"), ("torii", "far"), ("kuro", "sky"), ("torii", "sky")],
            fixes={"glow": ["glow2", "light", "sky2"], "far": ["mid", "near", "deep"]}),
    Concept("lm2-gyeongbokgung", "landmark-gyeongbokgung", "Gyeongbokgung Palace", gyeongbokgung, overrides=GYEONG,
            checks=[("roof", "far"), ("roof", "mid"), ("roof2", "far"), ("stone", "ground"), ("far", "sky"), ("red", "mid")],
            fixes={"far": ["mid", "sky2", "near"], "mid": ["near", "far"], "ground": ["mid", "near", "deep"]}),
    Concept("lm2-bagan", "landmark-bagan", "Bagan temples", bagan, overrides=BAGAN,
            checks=[("brick", "mid"), ("brick", "near"), ("brick", "glow"), ("far", "glow"), ("hero", "sky"), ("mid", "far")],
            fixes={"near": ["deep", "mid"], "glow": ["glow2", "light"], "far": ["mid", "near"], "hero": ["pop", "deep"]}),
    Concept("lm2-watarun", "landmark-wat-arun", "Wat Arun", wat_arun, overrides=WATARUN,
            checks=[("prang", "sky"), ("prang", "glow"), ("prang", "far"), ("prang2", "river")],
            fixes={"sky": ["sky2", "far", "mid"], "glow": ["glow2", "pop", "hero"], "far": ["mid", "near"]}),
    Concept("lm2-banaue", "landmark-banaue", "Banaue rice terraces", banaue, overrides=BANAUE,
            checks=[("far", "sky"), ("thatch", "r2"), ("r1", "far")],
            fixes={"far": ["mid", "near"]}),
    Concept("lm2-ulundanu", "landmark-ulun-danu", "Ulun Danu Bratan temple", ulun_danu, WATER, overrides=ULUN,
            checks=[("thatch", "far"), ("thatch", "mid"), ("thatch", "lake"), ("far", "sky"), ("mid", "lake"), ("base", "lake")],
            fixes={"far": ["sky2", "mid"], "mid": ["near", "far"]}),
    Concept("lm2-hoian", "landmark-hoi-an", "Hoi An lanterns", hoi_an, overrides=HOIAN,
            checks=[("l1", "wall"), ("l2", "sky"), ("l3", "wall2"), ("wall", "sky"), ("l1", "sky")],
            fixes={"sky": ["deep", "mark", "dark"]}),
    Concept("lm2-tigersnest", "landmark-tigers-nest", "Tiger's Nest", tigers_nest, overrides=TIGER,
            checks=[("rock", "sky"), ("white", "rock"), ("pine", "near"), ("near", "rock")],
            fixes={"near": ["mid", "far"], "sky": ["sky2", "light"]}),
    Concept("lm2-boudhanath", "landmark-boudhanath", "Boudhanath stupa", boudhanath, overrides=BOUDHA,
            checks=[("white", "sky"), ("gold", "sky"), ("white", "ground")],
            fixes={"sky": ["sky2", "far", "mid", "#A9CFE8"], "ground": ["mid", "near", "deep"]}),
    Concept("lm2-registan", "landmark-registan", "Registan", registan, overrides=REGISTAN,
            checks=[("brick", "sky"), ("tile2", "sky"), ("brick", "ground"), ("tile", "sky")],
            fixes={"sky": ["sky2", "light", "far"], "ground": ["mid", "near", "deep"]}),
    Concept("lm2-ninearch", "landmark-nine-arch-bridge", "Nine Arch Bridge", nine_arch, overrides=NINEARCH,
            checks=[("stone", "hill"), ("stone", "jungle"), ("train", "hill"), ("hill", "far"), ("far", "sky"), ("train", "far")],
            fixes={"far": ["sky2", "mid", "light"]}),
]
