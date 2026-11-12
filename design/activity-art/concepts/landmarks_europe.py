"""Mapsie Originals: famous European landmarks (one concept each, two for Big Ben)."""
from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group  # noqa: F401


# ================================================================ private helpers
def poly(*pts, close=True) -> str:
    s = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
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


def garch(x, y, w, h) -> str:
    """Pointed (gothic) opening, (x, y) top-left of its bounding box."""
    return (f"M{x:g} {y + h:g} V{y + w * .7:g} Q{x:g} {y + w * .15:g} {x + w / 2:g} {y:g} "
            f"Q{x + w:g} {y + w * .15:g} {x + w:g} {y + w * .7:g} V{y + h:g}Z")


def birds(d: Drawing, pts, role="dark"):
    s = " ".join(f"M{x} {y} q{3 * k} {-3 * k} {6 * k} 0 q{3 * k} {-3 * k} {6 * k} 0" for x, y, k in pts)
    d.stroke(role, s, 1.7)


def pine(x, y, s=1.0) -> str:
    return (f"M{x} {y - 40 * s} L{x + 11 * s} {y - 16 * s} L{x + 6 * s} {y - 16 * s} L{x + 14 * s} {y} L{x - 14 * s} {y} "
            f"L{x - 6 * s} {y - 16 * s} L{x - 11 * s} {y - 16 * s}Z")


def bushes(y, r=9, step=14, x0=-30, x1=230, jitter=(0, 4, 1, 5, 2)) -> str:
    """A bumpy tree-line edge (for band())."""
    s = f"M{x0} {y}"
    x, i = x0, 0
    while x < x1:
        dy = jitter[i % len(jitter)]
        s += f" Q{x + step / 2} {y - r - dy} {x + step} {y}"
        x += step
        i += 1
    return s


def clip_to(d: Drawing, outline: str, fn):
    """Draw fn() clipped to an outline (stripes on a dome)."""
    n = getattr(d, "_lmeu_clip", 0) + 1
    d._lmeu_clip = n
    cid = f"lmeu{n}"
    d.raw(f'<clipPath id="{cid}"><path d="{outline}"/></clipPath><g clip-path="url(#{cid})">',
          f'<clipPath id="{cid}"><path d="{outline}"/></clipPath><g clip-path="url(#{cid})">')
    fn()
    d.raw("</g>", "</g>")


def ink(d: Drawing, role: str, path: str, w: float, line_w: float = 1.4):
    """Thin detail line: palette colour in papercut, fine ink in line style."""
    if d.paper:
        d.stroke(role, path, w)
    else:
        d.raw("", f'<path d="{path}" fill="none" stroke="{d.c["ink"]}" stroke-width="{line_w}" stroke-linecap="round" stroke-linejoin="round"/>')


# ================================================================ BIG BEN
def big_ben(d: Drawing, tx, ty, s, stone="stone", stone2="stone2", roof="slate", face="light"):
    """Elizabeth Tower, base centre at (tx, ty), 178 * s tall."""
    def draw():
        d.shape(stone, rrect(-12, -86, 24, 86, 0.5))
        d.stroke(stone2, "M-6 -80 V-12 M0 -80 V-12 M6 -80 V-12", 1.3, line=False)
        for y in (-74, -56, -38):
            d.marks("dark", rrect(-1.6, y, 3.2, 8, 1.2))
        d.shape(stone, rrect(-14, -12, 28, 12, 0.5))
        d.shape(stone, rrect(-16, -88, 32, 5, 1))
        d.shape(stone, rrect(-15, -114, 30, 28, 0.5))
        d.shape(roof, rrect(-13, -112, 26, 24, 1.5), shadow=False)
        d.shape(face, circle(0, -100, 10.5), shadow=False, spot=True)
        d.stroke("dark", circle(0, -100, 10.5), 1.2)
        d.stroke("dark", "M0 -100 V-107.5 M0 -100 L5.5 -97", 1.9)
        d.shape(stone, rrect(-17, -118, 34, 5, 1))
        d.shape(stone, rrect(-13, -132, 26, 15, 0.5))
        for x in (-10, -2.5, 5):
            d.marks("dark", garch(x, -129, 5, 11))
        d.shape(roof, "M-15 -131 Q-8 -138 -6 -151 H6 Q8 -138 15 -131Z")
        d.shape(stone, "M-16 -130 L-14 -142 L-12 -130Z M12 -130 L14 -142 L16 -130Z", shadow=False)
        d.shape(stone, rrect(-5.5, -159, 11, 9, 0.8))
        d.marks("dark", rrect(-2.5, -157, 2, 5, 0.6))
        d.marks("dark", rrect(0.5, -157, 2, 5, 0.6))
        d.shape(roof, "M-5 -158 L0 -172 L5 -158Z")
        d.stroke(roof, "M0 -171 V-179", 1.6)
    group(d, f"translate({tx} {ty}) scale({s})", draw)


def parliament(d: Drawing, x0, x1, top, base, role="near", detail="far"):
    s = f"M{x0} {base} V{top}"
    x = x0
    while x + 9 <= x1:
        s += f" H{x + 3} L{x + 4.5} {top - 6} L{x + 6} {top} H{x + 9}"
        x += 9
    s += f" H{x1} V{base}Z"
    d.shape(role, s)
    ink(d, detail, " ".join(f"M{xx} {top + 6} V{base - 4}" for xx in range(int(x0) + 6, int(x1) - 2, 6)), 1.4)


def bigben_thames(d: Drawing):
    d.disc("glow", 156, 58, 16)
    d.shape("light", cloud(14, 62, 1.1))
    d.shape("light", cloud(128, 92, 0.8))
    birds(d, [(118, 50, 1), (132, 42, .8)])
    # Victoria Tower and the Palace of Westminster
    d.shape("near", "M176 168 V74 H178 L180 64 L182 74 H186 L188 64 L190 74 H194 L196 64 L198 74 H200 V168Z")
    d.shape("near", "M134 128 V108 H138 L141 84 L144 108 H148 V128Z")
    parliament(d, 80, 186, 124, 168)
    big_ben(d, 66, 170, 0.86)
    d.band("mid", waves(164, 2.5, 22))
    d.stroke("light", "M20 172 h14 M118 174 h20 M160 170 h12", 2.2, line=False)
    d.band("deep", waves(182, 2.5, 30), line=False)


BUS = "M18 162 V116 Q18 102 32 102 H116 Q126 102 126 114 V162Z"


def routemaster(d: Drawing):
    d.shape("bus", BUS, spot=True)
    for x in (26, 46, 66, 86, 104):
        d.shape("glass", rrect(x, 110, 15 if x < 104 else 16, 13, 2.5), shadow=False)
    d.shape("light", rrect(18, 127, 108, 3, 1), shadow=False)
    d.shape("glass", rrect(22, 134, 18, 14, 2.5), shadow=False)
    for x in (46, 64, 82):
        d.shape("glass", rrect(x, 134, 14, 13, 2.5), shadow=False)
    d.shape("dark", rrect(102, 132, 24, 26, 2), shadow=False)  # open rear platform
    d.stroke("light", "M110 134 V156", 1.8)
    d.shape("glow2", rrect(14, 148, 6, 5, 1.5), shadow=False)
    for x in (38, 98):
        d.shape("dark", circle(x, 162, 10))
        d.shape("light", circle(x, 162, 4), shadow=False)


def bigben_bus(d: Drawing):
    d.shape("light", cloud(24, 54, 1.0))
    birds(d, [(62, 82, .9), (76, 74, .7)])
    d.shape("near", "M160 152 V112 H164 L166 104 L168 112 H174 L176 104 L178 112 H184 L186 104 L188 112 H192 L194 104 L196 112 H230 V152Z")
    big_ben(d, 140, 154, 0.74)
    d.band("mid", "M-30 150 H230")
    d.stroke("far", "M-30 156 H230", 2, line=False)
    d.band("deep", "M-30 172 H230", line=False)
    routemaster(d)
    d.stroke("dark", "M-30 172.5 H230", 1.5, line=False)


# ================================================================ TOWER BRIDGE
def tb_tower(d: Drawing, x):
    w = 26
    d.shape("slate", f"M{x + 3} 54 L{x + w / 2} 22 L{x + w - 3} 54Z")
    d.shape("stone", rrect(x, 50, w, 100, 1))
    for tx in (x - 1, x + w - 6):
        d.shape("stone", rrect(tx, 42, 7, 14, 1))
        d.shape("slate", f"M{tx - 1} 44 L{tx + 3.5} 28 L{tx + 8} 44Z")
    d.marks("hole", garch(x + 9, 60, 8, 16))
    d.marks("hole", garch(x + 9, 82, 8, 12))
    d.shape("hole", garch(x + 6, 100, 14, 22), shadow=False)
    d.stroke("stone2", f"M{x} 98 H{x + w} M{x} 126 H{x + w}", 1.6, line=False)


def tower_bridge(d: Drawing):
    d.disc("glow", 100, 40, 14)
    d.shape("light", cloud(10, 70, 1.0))
    d.shape("light", cloud(150, 82, 0.8))
    # side spans: deck and suspension chains
    d.shape("steel", rrect(-30, 116, 82, 6, 0))
    d.shape("steel", rrect(148, 116, 82, 6, 0))
    for x, y in [(10, 108), (24, 100), (36, 88)]:
        d.stroke("steel", f"M{x} {y} V116", 1.6)
    for x, y in [(190, 108), (176, 100), (164, 88)]:
        d.stroke("steel", f"M{x} {y} V116", 1.6)
    d.limb("steel", "M50 66 Q30 108 -24 114", 5)
    d.limb("steel", "M150 66 Q170 108 224 114", 5)
    # high walkways
    d.shape("steel", rrect(70, 56, 60, 7, 1), spot=True)
    d.shape("steel", rrect(70, 68, 60, 7, 1), spot=True)
    d.stroke("light", "M74 59.5 L80 59.5 M86 59.5 L92 59.5 M98 59.5 L104 59.5 M110 59.5 L116 59.5 M122 59.5 L126 59.5 "
                      "M74 71.5 L80 71.5 M86 71.5 L92 71.5 M98 71.5 L104 71.5 M110 71.5 L116 71.5 M122 71.5 L126 71.5", 1.4, line=False)
    # raised bascules
    d.shape("steel", "M74 116 L91 90 L97 94 L80 124 L74 124Z", spot=True)
    d.shape("steel", "M126 116 L109 90 L103 94 L120 124 L126 124Z", spot=True)
    d.stroke("light", "M77 118 L93 93 M123 118 L107 93", 1.4, line=False)
    tb_tower(d, 48)
    tb_tower(d, 126)
    d.band("mid", waves(142, 2.5, 22))
    d.shape("slate", "M42 136 H82 L78 150 H46Z")
    d.shape("slate", "M118 136 H158 L154 150 H122Z")
    d.band("near", waves(152, 2.5, 26))
    d.stroke("light", "M14 162 h16 M92 158 h16 M170 164 h14", 2.2, line=False)
    d.band("deep", waves(176, 3, 30), line=False)


# ================================================================ STONEHENGE
def stone(x, y, w, h) -> str:
    """A rough standing stone, top-left (x, y)."""
    return (f"M{x + 1} {y + h} L{x - 1} {y + h * .45} L{x + 1} {y + 2} Q{x + w * .4} {y - 1.5} {x + w - 1} {y + 1} "
            f"L{x + w + 1} {y + h * .5} L{x + w} {y + h}Z")


def lintel(x, y, w, h) -> str:
    return f"M{x} {y + h} L{x - 1} {y + 3} Q{x + w * .5} {y - 2} {x + w} {y + 1} L{x + w + 1} {y + h - 1}Z"


def stonehenge(d: Drawing):
    d.disc("glow", 100, 106, 38)
    d.shape("light", cloud(22, 54, 1.0))
    birds(d, [(136, 54, 1), (150, 46, .8), (122, 62, .7)])
    d.band("far", hills(138, 6, 10))
    for x, y, w, h in [(18, 112, 10, 34), (36, 116, 9, 30), (144, 112, 10, 34), (162, 108, 11, 38), (180, 116, 9, 30)]:
        d.shape("stone2", stone(x, y, w, h))
    d.shape("stone2", lintel(142, 102, 32, 8))
    d.band("mid", hills(146, 3, 20), line=False)
    # side trilithons
    d.shape("stone", stone(34, 96, 13, 60))
    d.shape("stone", stone(56, 94, 13, 62))
    d.shape("stone", lintel(30, 85, 42, 11))
    d.shape("stone", stone(134, 94, 13, 62))
    d.shape("stone", "M156 156 L158 100 Q164 96 170 100 L176 104 L170 156Z")
    # great trilithon
    d.shape("stone", stone(76, 66, 16, 92), spot=True)
    d.shape("stone", stone(108, 66, 16, 92), spot=True)
    d.shape("stone", lintel(71, 54, 58, 14), spot=True)
    d.stroke("stone2", "M82 80 L84 100 M114 90 L113 112 M44 110 L45 124 M140 108 L141 126", 1.4, line=False)
    d.shape("stone", "M96 170 Q98 160 112 160 H146 Q154 162 152 170Z")
    d.band("near", hills(166, 3), line=True)
    d.band("deep", hills(184, 3, 30), line=False)


# ================================================================ EDINBURGH CASTLE
def edinburgh(d: Drawing):
    d.shape("light", cloud(130, 46, 1.0))
    d.shape("light", cloud(18, 70, 0.8))
    # castle buildings
    d.shape("stone", rrect(58, 76, 30, 40, 0.5))
    d.shape("stone", rrect(64, 58, 13, 24, 0.5))
    d.shape("slate", "M62 60 Q70 54 70.5 46 Q71 54 79 60Z")
    d.stroke("dark", "M70.5 47 V30", 1.5)
    d.shape("flag", "M70.5 30 H84 V39 H70.5Z", shadow=False, spot=True)
    d.stroke("light", "M71.5 31 L83 38 M83 31 L71.5 38", 1.6, line=False)
    for y in (84, 98):
        for x in (62, 70, 78):
            d.marks("hole", rrect(x, y, 4, 7, 1))
    d.shape("slate", "M84 86 L92 74 H128 L136 86Z")
    d.shape("stone", rrect(86, 84, 48, 30, 0.5))
    for x in (92, 104, 116, 126):
        d.marks("hole", garch(x, 90, 5, 12))
    d.shape("slate", "M124 100 L128 94 H170 L174 100Z")
    d.shape("stone", rrect(126, 98, 46, 26, 0.5))
    for x in (130, 140, 150, 160):
        d.marks("hole", rrect(x + 1, 103, 4, 6, 1))
        d.marks("hole", rrect(x + 1, 113, 4, 6, 1))
    d.shape("stone", battlement(38, 102, 42, 24, 6, 4))
    d.shape("stone2", "M38 120 H80 V126 H38Z", shadow=False)
    d.shape("stone", battlement(80, 112, 46, 12, 6, 3))
    # castle rock
    d.shape("rock", "M-30 210 V178 Q0 172 16 160 L28 138 L36 126 H82 L90 122 H172 L180 132 L188 150 Q200 166 230 170 V210Z")
    d.stroke("rock2", "M40 132 L48 154 M62 130 L58 148 M106 126 L110 146 M150 128 L156 150 M176 140 L180 156 M28 150 L34 164", 2, line=False)
    d.band("mid", bushes(170, 15, 22, jitter=(0, 5, 2, 6, 1)))
    d.band("near", bushes(188, 12, 26, jitter=(2, 0, 4)), line=False)


# ================================================================ EIFFEL TOWER
def eiffel(d: Drawing, cx=100, base=174, H=158, hw0=38):
    def y_at(t):
        return base - H * t

    def hw(t):
        return 3 + (hw0 - 3) * (1 - t) ** 3

    ts = [i / 50 for i in range(0, 42)]  # up to t = 0.82
    left = [(cx - hw(t), y_at(t)) for t in ts]
    right = [(cx + hw(t), y_at(t)) for t in reversed(ts)]
    tip = [(cx - 1.8, y_at(.9)), (cx - .8, y_at(.94)), (cx + .8, y_at(.94)), (cx + 1.8, y_at(.9))]
    ai = hw0 * .58
    outline = poly(*left, *tip, *right, close=False)
    outline += f" L{cx + ai:.1f} {base} A{ai:.1f} {H * .145:.1f} 0 0 0 {cx - ai:.1f} {base}Z"
    hole = poly((cx - 9.5, y_at(.195)), (cx - 3.2, y_at(.33)), (cx + 3.2, y_at(.33)), (cx + 9.5, y_at(.195)))
    d.stroke("iron", f"M{cx} {y_at(.93)} V{base - H}", 1.6)
    d.shape("iron", outline + " " + hole, extra='fill-rule="evenodd"', spot=True)
    # lattice
    zz = []
    for side in (-1, 1):
        pts = []
        for i in range(0, 9):
            t = i * .02
            outer = hw(t)
            inner = ai * (1 - t / .17) + hw(.17) * .5 * (t / .17)
            pts.append((cx + side * (outer if i % 2 == 0 else inner + 1.5), y_at(t)))
        zz.append(poly(*pts, close=False))
        pts = []
        for i in range(0, 8):
            t = .19 + i * .02
            outer = hw(t)
            inner = 9.5 - (9.5 - 3.2) * (t - .195) / .135
            pts.append((cx + side * (outer - .8 if i % 2 == 0 else inner + .8), y_at(t)))
        zz.append(poly(*pts, close=False))
    pts = []
    for i in range(0, 16):
        t = .36 + i * .029
        pts.append((cx + (-1 if i % 2 == 0 else 1) * (hw(t) - .6), y_at(t)))
    zz.append(poly(*pts, close=False))
    d.stroke("iron2", " ".join(zz), 0.9, line=False)
    # platforms
    for t, extra, h in [(.17, 4, 6), (.35, 2.5, 4.5), (.82, 1.5, 3.5)]:
        w = hw(t) + extra
        d.shape("iron", rrect(cx - w, y_at(t) - h / 2, 2 * w, h, 1))
    d.stroke("iron2", f"M{cx - hw(.17) - 2} {y_at(.17)} H{cx + hw(.17) + 2}", 1, line=False)


def eiffel_sunset(d: Drawing):
    d.disc("glow", 100, 112, 46)
    d.shape("light", cloud(14, 66, 1.0))
    d.shape("light", cloud(150, 52, 0.8))
    birds(d, [(140, 84, .9), (152, 76, .7)])
    roofs = ("M-30 160 V146 H-6 L0 138 H22 L28 146 H40 V140 L46 134 H62 L68 140 V146 H76 V152 H124 V146 H134 L140 136 H158 "
             "L164 146 H176 V140 L182 132 H198 L204 140 H230 V160Z")
    d.shape("far", roofs)
    for x in (2, 12, 50, 58, 142, 152, 186, 194):
        d.marks("glow2", rrect(x, 148, 4, 6, 1))
    eiffel(d)
    d.band("mid", bushes(166, 7, 13, jitter=(0, 3, 1, 4)))
    d.band("near", hills(182, 3, 20))


# ================================================================ MONT-SAINT-MICHEL
def mont_st_michel(d: Drawing):
    d.disc("glow", 152, 70, 16)
    birds(d, [(30, 60, 1), (44, 52, .8)])
    d.shape("light", cloud(150, 98, 0.8))
    # spire and abbey church
    d.shape("slate", "M96 44 L100 16 L104 44Z")
    d.stroke("gold", "M100 17 V10", 1.6)
    d.shape("gold", circle(100, 10, 2.2), shadow=False)
    d.shape("stone", rrect(94, 40, 12, 22, 0.5))
    d.shape("slate", "M78 62 L84 52 H118 L124 62Z")
    d.shape("stone", rrect(80, 60, 42, 16, 0.5))
    for x in (85, 93, 109, 117):
        d.marks("hole", garch(x - 1.5, 63, 4, 9))
    # mount
    d.shape("rock", "M18 150 Q40 134 54 116 Q66 96 78 82 H126 Q138 96 148 114 Q160 134 184 150Z")
    d.shape("stone", rrect(72, 74, 60, 40, 1))
    d.stroke("stone2", "M80 78 V112 M90 78 V112 M114 78 V112 M124 78 V112", 2.4, line=False)
    for x in (84, 94, 108, 118):
        d.marks("hole", garch(x, 90, 4, 10))
    d.shape("leaf", "M140 118 Q142 104 152 108 Q162 110 164 124 Q172 130 170 140 L140 140Z")
    for x, y, w in [(42, 122, 14), (56, 112, 14), (60, 126, 16), (126, 118, 14), (34, 134, 14), (132, 128, 12)]:
        d.shape("slate", f"M{x - 1} {y + 2} L{x + w / 2} {y - 6} L{x + w + 1} {y + 2}Z")
        d.shape("stone", rrect(x, y + 1, w, 12, 0.5))
        d.marks("hole", rrect(x + w / 2 - 1.5, y + 5, 3, 5, 0.8))
    # ramparts
    d.shape("stone", battlement(22, 136, 156, 14, 13, 3))
    for x in (30, 92, 164):
        d.shape("stone", battlement(x - 6, 130, 13, 20, 2, 3))
    d.shape("hole", arch(96, 140, 8, 10), shadow=False)
    d.band("near", waves(150, 2, 20))
    if d.paper:
        d.raw(f'<path d="M30 152 Q60 166 100 168 Q140 166 170 152Z" fill="{d.c["stone"]}" opacity=".25"/>')
    d.stroke("light", "M30 160 h14 M150 162 h16 M86 174 h20", 2, line=False)
    d.band("ground", hills(178, 3, 10))
    d.band("deep", hills(190, 3), line=False)


# ================================================================ COLOSSEUM
def colosseum(d: Drawing):
    d.disc("glow", 160, 56, 16)
    d.shape("light", cloud(16, 34, 0.9))
    # inner ring seen through the broken side
    d.shape("stone2", "M96 158 V74 Q140 70 182 82 V158Z")
    for x in (112, 130, 148, 166):
        d.marks("hole", arch(x, 92, 9, 16))
        d.marks("hole", arch(x, 120, 9, 18))
    outer = ("M16 160 V50 Q58 42 100 44 L104 50 L101 58 L112 64 L110 78 L122 84 L120 100 L134 104 L132 118 "
             "L150 122 L150 134 L164 138 L166 160Z")
    d.shape("stone", outer, spot=True)
    rows = [(52, 18, 98, "win"), (80, 22, 108, "arch"), (108, 22, 128, "arch"), (136, 24, 162, "arch")]
    for y, h, lim, kind in rows:
        for i in range(9):
            x = 21 + i * 17
            if x + 11 > lim:
                continue
            if kind == "win":
                if i % 2 == 1:
                    d.marks("hole", rrect(x + 3, y + 5, 5, 7, 1))
            else:
                d.marks("hole", arch(x, y, 11, h))
    d.stroke("stone2", "M16 76 Q60 72 106 75 M16 104 Q66 100 120 103 M16 132 Q80 128 136 131", 2.6, line=False)
    if not d.paper:
        d.raw("", f'<path d="M16 76 Q60 72 106 75 M16 104 Q66 100 120 103 M16 132 Q80 128 136 131" fill="none" '
                  f'stroke="{d.c["ink"]}" stroke-width="1.6" stroke-linecap="round"/>')
    # umbrella pine
    d.limb("dark", "M184 170 C182 150 178 136 172 124 M178 140 L192 128", 4.5)
    d.shape("dark", "M150 126 Q154 110 176 110 Q200 110 206 124 Q180 132 150 126Z")
    d.band("ground", hills(164, 3, 10))
    d.band("near", hills(182, 3, 30), line=False)


# ================================================================ PISA
def pisa_tower(d: Drawing):
    """Leaning tower, local coords: base centre (0, 0), upright (lean applied by the caller)."""
    w = 21
    tiers = [(-30, 30, "base")] + [(-30 - 15 * (i + 1), 15, "gallery") for i in range(6)]
    d.shape("marble", rrect(-w, -122, 2 * w, 122, 1.5), spot=True)
    for y, h, kind in tiers:
        if kind == "base":
            for k in range(6):
                x = -w + 2.5 + k * 6.6
                d.stroke("marble2", arch(x, y + 6, 5, h - 8), 1.2, line=False)
            d.marks("hole", arch(-3, y + 12, 6, h - 12))
        else:
            for k in range(6):
                x = -w + 2.6 + k * 6.6
                d.marks("hole", arch(x, y + 3, 4.4, h - 5))
        d.shape("marble", rrect(-w - 2, y - 2.2, 2 * w + 4, 3.4, 1), shadow=False)
        d.stroke("marble2", f"M{-w - 2} {y + 1.2} H{w + 2}", 0.9, line=False)
    # shaded right side
    if d.paper:
        d.raw(f'<path d="M{w - 9} -120 H{w} V0 H{w - 9}Z" fill="{d.c["marble2"]}" opacity=".55"/>')
    # belfry
    d.shape("marble", rrect(-14, -137, 28, 16, 1.5))
    for k in range(4):
        d.marks("hole", arch(-11.5 + k * 6.4, -134, 4.4, 10))
    d.shape("marble", rrect(-16, -139, 32, 3.4, 1), shadow=False)
    d.stroke("marble2", "M-16 -136 H16", 0.9, line=False)


def pisa(d: Drawing):
    d.shape("light", cloud(136, 40, 1.0))
    d.shape("light", cloud(16, 76, 0.8))
    # cathedral behind on the left
    d.shape("mid", "M-30 160 V122 H6 L18 112 H40 L52 122 H70 V160Z")
    d.shape("mid", "M10 114 Q12 92 29 92 Q46 92 48 114Z")
    d.stroke("mid", "M29 92 V84", 2)
    for x in (-8, 4, 54, 62):
        d.marks("sky", arch(x, 130, 5, 12))
    d.band("near", hills(160, 3, 10))
    group(d, "translate(96 164) rotate(7)", lambda: pisa_tower(d))
    d.band("deep", hills(172, 3, 40))
    


# ================================================================ VENICE
GONDOLA = "M22 126 Q30 150 64 150 H146 Q170 150 176 124 Q170 140 154 141 H50 Q34 141 22 126Z"
FERRO = ("M170 128 L172 96 Q172 86 182 84 Q190 84 192 90 L186 91 Q182 89 180 94 L178 128Z "
         "M178 100 h9 v3.5 h-9Z M178 107 h9 v3.5 h-9Z M178 114 h9 v3.5 h-9Z M178 121 h8 v3.5 h-8Z")


def venice(d: Drawing):
    d.disc("glow", 100, 60, 16)
    # palazzi either side
    d.shape("hero2", "M-30 128 V40 H28 V128Z")
    d.shape("pop", "M172 128 V52 H230 V128Z")
    for y in (52, 78, 104):
        for x in (2, 14):
            d.marks("light", arch(x, y, 7, 14))
    for y in (64, 90):
        for x in (180, 192):
            d.marks("light", arch(x, y, 7, 14))
    d.shape("light", rrect(-30, 36, 58, 4, 1), shadow=False)
    d.shape("light", rrect(172, 48, 58, 4, 1), shadow=False)
    # Rialto bridge: deck arch, two ramps of arcaded shops, central portico
    def deck(t):
        return 14 + 172 * t, (1 - t) ** 2 * 112 + 2 * (1 - t) * t * 56 + t * t * 112

    for t0, t1 in [(0.04, 0.42), (0.58, 0.96)]:
        ts = [t0 + (t1 - t0) * i / 10 for i in range(11)]
        top = [(x, y - 13) for x, y in map(deck, ts)]
        bot = [deck(t) for t in reversed(ts)]
        d.shape("stone", poly(*top, *bot))
        d.stroke("roof", poly(*[(x, y - 13.5) for x, y in map(deck, ts)], close=False), 3.2)
        for t in [t0 + (t1 - t0) * (i + .5) / 5 for i in range(5)]:
            x, y = deck(t)
            d.marks("hole", arch(x - 2.6, y - 10, 5.2, 9))
    d.shape("stone", "M14 128 V112 Q100 56 186 112 V128 H172 A72 30 0 0 0 28 128Z", spot=True)
    d.shape("roof", "M82 76 L100 60 L118 76Z")
    d.shape("stone", "M85 88 V74 L100 64 L115 74 V88Z")
    d.shape("hole", arch(94, 74, 12, 14), shadow=False)
    d.stroke("stone2", "M30 114 Q100 74 170 114", 1.5, line=False)
    d.band("mid", waves(128, 2.5, 20))
    group(d, "translate(12 38) scale(.86)", lambda: (gondolier(d), gondola(d)))
    d.band("near", waves(172, 2.5, 26))
    d.band("deep", waves(186, 2.5, 30), line=False)


def gondola(d: Drawing):
    d.shape("pop", rrect(88, 130, 34, 12, 4), spot=True)
    d.shape("hero2", rrect(84, 126, 6, 16, 2), shadow=False)
    d.shape("dark", GONDOLA)
    d.stroke("hero2", "M48 144 H150", 1.6)
    d.shape("light", FERRO)
    d.shape("light", "M22 126 L18 118 L26 122Z", shadow=False)


def gondolier(d: Drawing, x=44, y=141):
    d.limb("dark", f"M{x + 22} {y - 56} L{x - 22} {y + 22}", 3.4, shadow=False)
    d.limb("dark", f"M{x - 4} {y} L{x - 2} {y - 22} M{x + 5} {y} L{x + 3} {y - 22}", 5)
    d.shape("light", rrect(x - 9, y - 50, 18, 30, 6))
    for k in range(4):
        d.shape("pop", rrect(x - 9, y - 45 + k * 7, 18, 3, 1), shadow=False, spot=True)
    d.limb("dark", f"M{x + 5} {y - 44} L{x + 15} {y - 38}", 4.4, shadow=False)
    d.marks("dark", circle(x, y - 57, 6.5))
    d.shape("hero2", ellipse(x, y - 61, 11, 2.6))
    d.shape("hero2", rrect(x - 6.5, y - 70, 13, 9, 2), shadow=False)
    d.shape("pop", rrect(x - 6.5, y - 65, 13, 2.6, 1), shadow=False)


# ================================================================ SAGRADA FAMILIA
def spire(x, top, base, w) -> str:
    """Gaudi's parabolic bell tower: straight drum, then a tapering parabola."""
    H = base - top
    k = base - H * .38
    return (f"M{x - w} {base} V{k} C{x - w} {top + H * .25} {x - w * .3} {top + H * .06} {x} {top} "
            f"C{x + w * .3} {top + H * .06} {x + w} {top + H * .25} {x + w} {k} V{base}Z")


def sagrada(d: Drawing):
    d.disc("glow", 160, 70, 14)
    d.shape("light", cloud(150, 96, 0.8))
    towers = [  # x, top, base, half-width, role, pinnacle
        (100, 22, 132, 11, "stone2", "cross"),
        (79, 40, 132, 8.5, "stone2", "ball"), (121, 40, 132, 8.5, "stone2", "ball"),
        (46, 66, 150, 8, "stone", "ball"), (64, 46, 150, 8.5, "stone", "ball"),
        (136, 46, 150, 8.5, "stone", "ball"), (154, 66, 150, 8, "stone", "ball"),
    ]
    for i, (x, top, base, w, role, pin) in enumerate(towers):
        if i == 3:  # facade: gables between the front towers
            d.shape("stone", "M54 150 V120 L64 112 L74 120 L86 96 Q100 74 114 96 L126 120 L136 112 L146 120 V150Z")
        d.shape(role, spire(x, top, base, w), spot=i == 0)
        H = base - top
        for j in range(5):
            y = base - H * (.18 + j * .12)
            ww = w * (1 if j < 3 else .7 - (j - 3) * .2)
            d.marks("hole", rrect(x - ww * .5 - 1, y, 2, 5, 1))
            d.marks("hole", rrect(x + ww * .5 - 1, y, 2, 5, 1))
        if pin == "ball":
            d.stroke("dark", f"M{x} {top + 2} V{top - 5}", 1.4)
            d.shape("pop", circle(x, top - 7, 3.6), shadow=False)
            d.shape("hero2", circle(x, top - 7, 1.6), shadow=False, line=False)
        else:
            d.shape("light", "M98.5 2 H101.5 V7 H106 V10 H101.5 V16 H98.5 V10 H94 V7 H98.5Z", spot=True)
            d.stroke("dark", "M100 22 V16", 1.6)
    for x in (88, 104):
        d.marks("hole", garch(x, 118, 8, 32))
    d.shape("hole", garch(96, 106, 8, 14), shadow=False)
    d.band("mid", bushes(160, 9, 14))
    d.band("near", hills(178, 3, 10))


# ================================================================ ACROPOLIS
def acropolis(d: Drawing):
    d.disc("glow", 150, 46, 16)
    birds(d, [(24, 54, 1), (38, 46, .8)])
    # the rock and its walls
    d.shape("rock", "M-30 210 V168 Q4 162 22 150 L32 130 L40 120 H162 L170 130 L180 150 Q196 162 230 166 V210Z")
    d.stroke("rock2", "M44 130 L50 148 M70 126 L66 140 M130 126 L134 142 M160 132 L166 150 M36 142 L40 156", 2, line=False)
    d.shape("marble2", rrect(36, 116, 130, 8, 0.5))
    # Parthenon
    d.shape("marble", rrect(42, 110, 116, 7, 1))
    d.shape("marble", rrect(47, 104, 106, 7, 1))
    d.shape("marble", "M44 56 L100 36 L156 56Z", spot=True)
    d.shape("marble2", "M58 53.5 L100 39.5 L142 53.5Z", shadow=False)
    d.shape("marble", rrect(48, 54, 104, 12, 1))
    d.stroke("marble2", "M48 60 H152", 1.2, line=False)
    xs = [52 + i * 13.43 for i in range(8)]
    for i, x in enumerate(xs):
        d.shape("marble", rrect(x, 68, 9, 37, 1))
        d.shape("marble", rrect(x - 1.5, 65, 12, 4, 1), shadow=False)
        d.stroke("marble2", f"M{x + 3} 72 V102 M{x + 6} 72 V102", 1, line=False)
    d.band("mid", hills(170, 4, 10))
    for x, y, w in [(14, 164, 16), (34, 168, 12), (130, 166, 14), (150, 162, 18), (172, 168, 14), (62, 172, 14), (96, 174, 12)]:
        d.shape("light", rrect(x, y, w, 12, 1))
        d.marks("hole", rrect(x + w / 2 - 1.5, y + 4, 3, 5, 0.8))
    d.band("near", hills(184, 3, 30), line=False)


# ================================================================ SANTORINI
def santorini(d: Drawing):
    d.disc("glow", 38, 98, 18)
    d.band("sea", "M-30 104 H230")
    d.shape("deep", "M-30 112 Q-10 104 10 106 Q24 102 34 108 L40 112Z", shadow=False)
    d.stroke("light", "M140 112 h20 M56 120 h12 M150 122 h10", 2, line=False)
    # caldera cliff
    d.shape("cliff", "M-30 210 V186 Q10 176 40 160 Q60 142 76 124 L96 120 L180 118 L230 116 V210Z")
    d.stroke("cliff2", "M30 176 Q50 166 56 156 M64 150 Q72 142 76 134", 2, line=False)
    # church with blue dome and bell tower
    d.shape("whitewash", rrect(78, 94, 46, 34, 1.5))
    d.shape("dome", "M80 96 C80 66 122 66 122 96Z", spot=True)
    d.shape("whitewash", rrect(98, 62, 6, 9, 1))
    d.stroke("whitewash", "M101 62 V52 M97 56 H105", 2.2)
    d.shape("dome", arch(95, 106, 12, 22), shadow=False)
    d.shape("whitewash", "M128 128 V70 H138 V60 H146 V70 H156 V128Z")
    d.shape("whitewash", rrect(126, 68, 32, 4, 1), shadow=False)
    d.stroke("whitewash", "M142 60 V50 M138 54 H146", 2.2)
    d.marks("hole", arch(132, 76, 8, 14))
    d.marks("hole", arch(144, 76, 8, 14))
    d.marks("bell", circle(136, 86, 2.8))
    d.marks("bell", circle(148, 86, 2.8))
    d.marks("hole", arch(139, 102, 6, 12))
    # houses down the cliff
    houses = [(160, 120, 30, 22), (58, 126, 26, 20), (86, 132, 30, 22), (126, 132, 34, 22), (164, 144, 34, 24),
              (40, 148, 30, 22), (72, 154, 34, 22), (110, 156, 30, 22), (144, 166, 34, 24), (22, 172, 28, 20)]
    for x, y, w, h in houses:
        d.shape("whitewash", rrect(x, y, w, h, 1.5))
        d.marks("dome", rrect(x + w * .2, y + h * .4, w * .18, h * .45, 1))
        d.marks("hole", rrect(x + w * .6, y + h * .35, w * .16, h * .25, 0.8))
    d.shape("dome", "M164 145 C164 132 182 132 182 145Z", spot=True)
    d.shape("whitewash", rrect(170, 128, 6, 4, 1), shadow=False)
    d.shape("pop", circle(54, 120, 7))
    d.shape("pop", circle(64, 116, 5))
    d.shape("pop", circle(124, 150, 6))
    d.shape("pop", circle(34, 166, 5))


# ================================================================ NEUSCHWANSTEIN
def neuschwanstein(d: Drawing):
    d.band("mid", "M-30 118 L10 86 L34 104 L66 66 L92 94 L120 70 L150 100 L178 74 L230 112")
    for snow in ["M66 66 L76 78 L70 76 L65 81 L59 75 L55 78Z", "M178 74 L187 85 L181 83 L176 88 L171 82 L168 84Z",
                 "M10 86 L18 95 L12 94 L8 98 L4 92Z"]:
        d.shape("light", snow, shadow=False, line=False)
    d.band("near", hills(134, 10, 10))

    def turret(x, top, w, base, roof_h, role="castle"):
        d.shape(role, rrect(x - w / 2, top, w, base - top, w / 2 if w < 8 else 1))
        d.shape("slate", f"M{x - w / 2 - 1.5} {top + 2} L{x} {top - roof_h} L{x + w / 2 + 1.5} {top + 2}Z", spot=True)
    # tall stair tower behind the palas
    turret(98, 36, 9, 120, 24)
    d.shape("castle", rrect(95, 46, 6, 6, 1), shadow=False)
    # palas (main hall) with steep gable
    d.shape("slate", "M106 50 L128 24 L150 50Z")
    d.shape("castle", "M106 124 V50 H150 V124Z")
    d.shape("castle", "M110 50 L128 30 L146 50Z", shadow=False)
    for y in (58, 76, 94):
        for x in (112, 122, 132, 140):
            d.marks("hole", arch(x, y, 4, 9))
    d.marks("hole", arch(125, 38, 6, 9))
    turret(150, 44, 7, 70, 14)
    turret(106, 52, 6, 72, 12)
    # bower and square tower
    d.shape("slate", "M64 82 L70 72 H100 L106 82Z")
    d.shape("castle", rrect(66, 80, 38, 44, 0.5))
    for x in (72, 82, 92):
        d.marks("hole", arch(x, 90, 4, 9))
    turret(70, 60, 12, 124, 18)
    d.marks("hole", arch(68, 70, 4, 8))
    # gatehouse
    d.shape("brick", rrect(36, 98, 30, 30, 0.5))
    turret(38, 92, 7, 128, 12, "brick")
    turret(64, 92, 7, 128, 12, "brick")
    d.marks("hole", arch(46, 108, 10, 20))
    # crag and forest
    d.shape("rock", "M30 210 V134 L42 127 L70 129 L100 125 L156 126 L168 136 L174 160 L180 210Z")
    d.stroke("rock2", "M52 136 L56 152 M120 132 L124 148 M162 140 L166 158 M84 134 L82 146", 2, line=False)
    for x, y, s in [(18, 160, 1.1), (6, 172, 1.0), (32, 178, 1.0), (184, 158, 1.1), (196, 170, 1.0), (170, 178, 1.0)]:
        d.shape("deep", pine(x, y, s), line=False)
    d.band("deep", bushes(176, 11, 16, jitter=(0, 4, 2, 5)))


# ================================================================ MATTERHORN
MATTERHORN = ("M-30 168 L-4 150 L20 132 L38 112 L52 92 L62 74 L70 58 L76 44 L79 34 L80 26 L83 18 L88 13 L92 15 "
              "L96 22 L101 34 L106 48 L110 60 L116 70 L124 76 L130 84 L140 96 L156 108 L178 118 L204 128 L230 136 V210 H-30Z")
MATTER_SHADE = ("M92 15 L96 22 L101 34 L106 48 L110 60 L116 70 L124 76 L130 84 L140 96 L156 108 L178 118 L204 128 L230 136 "
                "V200 H130 L112 150 L100 104 L94 64 L90 32Z")


def matterhorn(d: Drawing):
    d.shape("light", cloud(134, 34, 1.0))
    d.shape("light", cloud(4, 74, 0.8))
    d.shape("rock", MATTERHORN)
    d.shape("rock2", MATTER_SHADE, shadow=False, line=False)
    # snow: summit cap, east-face ice fields, ridge shoulders
    d.shape("light", "M80 26 L83 18 L88 13 L92 15 L96 22 L99 30 L95 28 L92 36 L89 28 L85 34 L82 28 L78 36Z", shadow=False, spot=True)
    d.shape("light", "M62 74 L70 58 L72 66 L76 64 L74 76 L68 74 L62 86Z M38 112 L52 92 L54 102 L48 104 L44 102 L38 118Z "
                     "M116 70 L124 76 L130 84 L124 84 L120 80 L114 86 L112 76Z M140 96 L156 108 L148 108 L142 104 L138 108Z", shadow=False)
    d.stroke("light", "M84 44 L78 66 M90 46 L86 70 M80 82 L74 98", 2.2, line=False)
    d.band("far", hills(140, 8, -10))
    d.band("mid", hills(154, 10, 30))
    for x, y, s in [(146, 168, 1.0), (162, 174, 1.2), (180, 164, .9), (26, 170, .9), (12, 176, 1.1)]:
        d.shape("deep", pine(x, y, s))
    # chalet
    d.shape("wood", rrect(66, 150, 40, 24, 0.5))
    d.shape("dark", "M60 154 L86 136 L112 154 L108 156 L86 141 L64 156Z", spot=True)
    d.shape("wood", "M66 152 L86 138 L106 152Z", shadow=False)
    d.marks("light", rrect(72, 158, 8, 8, 1))
    d.marks("light", rrect(92, 158, 8, 8, 1))
    d.marks("pop", rrect(72, 166, 8, 3, 1))
    d.marks("pop", rrect(92, 166, 8, 3, 1))
    d.band("near", hills(176, 4, 10))
    d.band("deep", hills(190, 3, 30), line=False)


# ================================================================ ST BASIL'S
def onion(cx, by, w, h) -> str:
    """Onion dome, bottom centre (cx, by), max width w, height h (tip at by - h)."""
    return (f"M{cx - w * .36} {by} C{cx - w * .62} {by - h * .2} {cx - w * .56} {by - h * .55} {cx - w * .2} {by - h * .74} "
            f"Q{cx - w * .03} {by - h * .84} {cx} {by - h} Q{cx + w * .03} {by - h * .84} {cx + w * .2} {by - h * .74} "
            f"C{cx + w * .56} {by - h * .55} {cx + w * .62} {by - h * .2} {cx + w * .36} {by}Z")


def dome(d: Drawing, cx, by, w, h, base, stripe, pattern, spot=False):
    out = onion(cx, by, w, h)
    d.shape(base, out, spot=spot)
    if pattern == "swirl":
        p = " ".join(f"M{cx - w + k * w * .34} {by + 4} Q{cx - w * .3 + k * w * .34} {by - h * .4} {cx + k * w * .34 - w * .1} {by - h - 4}"
                     for k in range(0, 7))
        clip_to(d, out, lambda: ink(d, stripe, p, w * .1, 1.2))
    elif pattern == "zigzag":
        p = " ".join(poly(*[(cx - w + i * w * .16, by - h * f - (3 if i % 2 else -3) * w / 30) for i in range(14)], close=False)
                     for f in (.15, .34, .53, .72))
        clip_to(d, out, lambda: ink(d, stripe, p, w * .07, 1.2))
    elif pattern == "scales":
        p = " ".join(f"M{cx - w + i * w * .2 + (w * .1 if r % 2 else 0)} {by - h * (.12 + r * .17)} a{w * .07} {w * .07} 0 0 0 {w * .14} 0"
                     for r in range(4) for i in range(11))
        clip_to(d, out, lambda: ink(d, stripe, p, 1.6, 1.0))
    elif pattern == "bands":
        p = " ".join(f"M{cx - w} {by - h * f} Q{cx} {by - h * f + h * .08} {cx + w} {by - h * f}" for f in (.18, .38, .58))
        clip_to(d, out, lambda: ink(d, stripe, p, w * .09, 1.2))
    d.stroke("gold", f"M{cx} {by - h + 1} V{by - h - 9} M{cx - 3} {by - h - 5} H{cx + 3}", 1.6)


def drum(d: Drawing, cx, top, base, w, role="brick"):
    d.shape(role, rrect(cx - w / 2, top, w, base - top, 0.5))
    d.stroke("trim", f"M{cx - w / 2} {top + 3} H{cx + w / 2}", 1.6, line=False)
    n = max(2, int(w / 7))
    for i in range(n):
        x = cx - w / 2 + (i + .5) * w / n
        d.marks("hole", arch(x - 1.4, top + 6, 2.8, 7))


def st_basils(d: Drawing):
    d.shape("light", cloud(20, 46, 0.9), line=False)
    d.shape("light", cloud(150, 34, 0.8), line=False)
    # central tented tower
    d.shape("brick", "M90 128 V78 H110 V128Z")
    d.shape("tent", "M88 80 L100 30 L112 80Z", spot=True)
    d.stroke("brick2", "M94 72 L100 40 L106 72 M91 64 H109 M93 52 H107", 1.2, line=False)
    d.shape("brick", rrect(97, 24, 6, 8, 1))
    d.shape("gold", onion(100, 25, 9, 12))
    d.stroke("gold", "M100 13 V6 M97.5 9 H102.5", 1.4)
    for x in (92, 99, 106):
        d.marks("hole", arch(x - 1.4, 86, 2.8, 8))
    # outer small domes
    drum(d, 36, 108, 136, 14)
    dome(d, 36, 110, 22, 26, "dblue", "light", "swirl")
    drum(d, 164, 108, 136, 14)
    dome(d, 164, 110, 22, 26, "dgreen", "gold", "zigzag")
    # big domes
    drum(d, 64, 86, 136, 18)
    dome(d, 64, 88, 32, 38, "dgreen", "gold", "swirl", spot=True)
    drum(d, 136, 86, 136, 18)
    dome(d, 136, 88, 32, 38, "dred", "light", "swirl", spot=True)
    # front dome
    drum(d, 100, 104, 140, 18)
    dome(d, 100, 106, 28, 32, "dgold", "dred", "scales")
    # body with kokoshnik arches
    d.shape("brick", "M20 172 V138 H180 V172Z")
    for x in range(26, 176, 16):
        d.shape("trim", f"M{x} 140 Q{x + 6} 130 {x + 12} 140Z", shadow=False)
        d.marks("hole", arch(x + 3, 148, 6, 12))
    d.stroke("trim", "M20 141 H180", 2.4, line=False)
    d.band("ground", "M-30 166 H230")
    d.stroke("near", "M-30 178 H230 M-30 190 H230", 1.4, line=False)


# ================================================================ concepts
BIGBEN = {"stone": "#CFB27A", "stone2": "#B2945E", "slate": "#2E3A55"}
TB = {"stone": "#CBBDA2", "stone2": "#A8977A", "slate": "#3E4A60", "steel": "#4F8FC9", "hole": "#3A3F4E"}
STONES = {"stone": "#8E8A80", "stone2": "#6F6A62"}
EDIN = {"stone": "#A89880", "stone2": "#8A7B66", "slate": "#3E4656", "hole": "#2F2A26", "rock": "#5F5850", "rock2": "#46413B",
        "flag": "#2E62B0"}
EIFFEL = {"iron": "#6E4E3A", "iron2": "#9A7454"}
MSM = {"stone": "#C9B99C", "stone2": "#AE9C7E", "slate": "#3E4656", "gold": "#E2B04A", "hole": "#3A342C", "rock": "#7D7464",
       "leaf": "#4F7A4A"}
COLOSSEUM = {"stone": "#DDB98A", "stone2": "#BB9466", "hole": "#6B4B33"}
PISA = {"marble": "#F6F0E4", "marble2": "#D6CAB4", "hole": "#7A7064"}
VENICE = {"stone": "#EDE3CF", "stone2": "#CDBFA4", "hole": "#5A4E44", "roof": "#C0603E"}
SAGRADA = {"stone": "#D6B88C", "stone2": "#B99A6E", "hole": "#5E4630"}
ACRO = {"marble": "#F2E8D4", "marble2": "#D2C2A0", "hole": "#5C5344", "rock": "#BE9468", "rock2": "#97704C"}
SANTO = {"whitewash": "#FFFFFF", "dome": "#2456A6", "sea": "#2F78B7", "hole": "#3B3B48", "bell": "#C9A13A", "pop": "#D9417E", "cliff": "#A4644A", "cliff2": "#7E4836"}
NEUSCH = {"castle": "#F2EDE4", "slate": "#4D5E78", "brick": "#C27A62", "hole": "#4A4A58", "rock": "#B8AFA0", "rock2": "#948A7A"}
MATTER = {"rock": "#8A8F9E", "rock2": "#6B7080", "wood": "#9A6238"}
BASIL = {"brick": "#B5452E", "brick2": "#8E3322", "trim": "#F3E9D6", "hole": "#4A2A22", "gold": "#E8B12A",
         "tent": "#DDB65A", "dred": "#D2392C", "dgreen": "#2E8B57", "dblue": "#2F6DB5", "dgold": "#E8B12A"}

SEA = ["coastal", "dusk", "meadow", "blush"]

CONCEPTS = [
    Concept("lm-bigben-thames", "landmark-big-ben", "Big Ben", bigben_thames, overrides=BIGBEN,
            checks=[("stone", "sky"), ("stone", "near"), ("near", "sky"), ("slate", "sky")],
            fixes={"near": ["mid", "far", "deep"], "slate": ["mid", "far"]}),
    Concept("lm-bigben-bus", "landmark-big-ben", "Big Ben & red bus", bigben_bus,
            overrides={**BIGBEN, "bus": "#D7372B", "glass": "#F6EBD8"},
            checks=[("stone", "sky"), ("bus", "sky"), ("bus", "mid"), ("near", "sky"), ("slate", "sky"), ("stone", "near")],
            fixes={"near": ["mid", "far", "deep"], "slate": ["mid", "far"]}),
    Concept("lm-towerbridge-bascules", "landmark-tower-bridge", "Tower Bridge", tower_bridge, palettes=SEA, overrides=TB,
            checks=[("stone", "sky"), ("steel", "sky"), ("slate", "sky"), ("slate", "mid"), ("steel", "stone")]),
    Concept("lm-stonehenge-sunset", "landmark-stonehenge", "Stonehenge", stonehenge, overrides=STONES,
            checks=[("stone", "glow"), ("stone", "sky"), ("stone", "mid"), ("stone2", "far")],
            fixes={"glow": ["glow2", "light", "far"], "far": ["mid", "sky2"], "mid": ["near", "far"]}),
    Concept("lm-edinburgh-rock", "landmark-edinburgh-castle", "Edinburgh Castle", edinburgh, overrides=EDIN,
            checks=[("stone", "sky"), ("rock", "sky"), ("slate", "sky"), ("mid", "rock")], fixes={"mid": ["far", "near"]}),
    Concept("lm-eiffel-sunset", "landmark-eiffel-tower", "Eiffel Tower", eiffel_sunset, overrides=EIFFEL,
            checks=[("iron", "glow"), ("iron", "sky"), ("iron", "far"), ("far", "sky")],
            fixes={"far": ["mid", "near"], "iron": ["#E0A040"], "glow": ["light", "glow2"]}),
    Concept("lm-montstmichel-tide", "landmark-mont-saint-michel", "Mont-Saint-Michel", mont_st_michel, palettes=SEA, overrides=MSM,
            checks=[("stone", "sky"), ("slate", "sky"), ("stone", "near"), ("near", "sky")]),
    Concept("lm-colosseum-ruin", "landmark-colosseum", "Colosseum", colosseum, overrides=COLOSSEUM,
            checks=[("stone", "sky"), ("stone2", "sky"), ("stone", "glow"), ("dark", "sky")], fixes={"glow": ["light", "glow2", "far"], "dark": ["#4A5A44"]}),
    Concept("lm-pisa-lean", "landmark-pisa", "Leaning Tower of Pisa", pisa, overrides=PISA,
            checks=[("marble", "sky"), ("marble", "near"), ("mid", "sky")], fixes={"sky": ["far", "glow2"], "mid": ["near", "deep"], "deep": ["dark"]}),
    Concept("lm-venice-rialto", "landmark-venice", "Venice canals", venice, palettes=SEA, overrides=VENICE,
            checks=[("stone", "sky"), ("dark", "mid"), ("dark", "near"), ("stone", "mid")], fixes={"sky": ["far", "glow2"]}),
    Concept("lm-sagrada-spires", "landmark-sagrada-familia", "Sagrada Família", sagrada, overrides=SAGRADA,
            checks=[("stone", "sky"), ("stone2", "sky"), ("pop", "sky")]),
    Concept("lm-acropolis-parthenon", "landmark-acropolis", "Acropolis", acropolis, overrides=ACRO,
            checks=[("marble", "sky"), ("rock", "sky"), ("marble", "rock"), ("light", "mid")], fixes={"sky": ["sky2", "far", "mid"]}),
    Concept("lm-santorini-domes", "landmark-santorini", "Santorini", santorini, palettes=SEA, overrides=SANTO,
            checks=[("whitewash", "sky"), ("dome", "sky"), ("whitewash", "sea"), ("whitewash", "cliff"), ("cliff", "sea")],
            fixes={"sky": ["sky2", "far", "glow2"]}),
    Concept("lm-neuschwanstein-alps", "landmark-neuschwanstein", "Neuschwanstein", neuschwanstein, overrides=NEUSCH,
            checks=[("castle", "sky"), ("castle", "mid"), ("castle", "near"), ("slate", "sky"), ("mid", "sky"), ("deep", "near"), ("rock", "near"), ("castle", "rock")],
            fixes={"sky": ["far", "glow2"], "mid": ["near", "deep"], "deep": ["dark"]}),
    Concept("lm-matterhorn-peak", "landmark-matterhorn", "Matterhorn", matterhorn, overrides=MATTER,
            checks=[("rock", "sky"), ("light", "rock"), ("far", "rock"), ("wood", "mid")], fixes={"far": ["mid", "near"]}),
    Concept("lm-stbasils-domes", "landmark-st-basils", "St Basil's Cathedral", st_basils, overrides=BASIL,
            checks=[("dgreen", "sky"), ("dred", "sky"), ("dblue", "sky"), ("dgold", "sky"), ("tent", "sky")],
            fixes={"sky": ["sky2", "far"]}),
]
