"""Culture & sightseeing, batch B: cathedrals, mosques, palaces, street art, city tours, bridges,
lighthouses, monasteries, pilgrimages and souks."""
from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group  # noqa: F401
import math


# ================================================================ private helpers
def poly(*pts, close=True) -> str:
    s = "M" + " L".join(f"{x:g} {y:g}" for x, y in pts)
    return s + ("Z" if close else "")


def arch(x, y, w, h) -> str:
    """Round-topped opening, (x, y) top-left of its bounding box."""
    r = w / 2
    return f"M{x:g} {y + h:g} V{y + r:g} A{r:g} {r:g} 0 0 1 {x + w:g} {y + r:g} V{y + h:g}Z"


def parch(x, y, w, h, close=True) -> str:
    """Pointed (gothic / islamic) arch, (x, y) top-left; apex at (x + w/2, y)."""
    k = w * .866
    s = (f"M{x:g} {y + h:g} V{y + k:.1f} A{w:g} {w:g} 0 0 1 {x + w / 2:g} {y:g} "
         f"A{w:g} {w:g} 0 0 1 {x + w:g} {y + k:.1f} V{y + h:g}")
    return s + ("Z" if close else "")


def dome(cx, base, w, h) -> str:
    return (f"M{cx - w / 2:g} {base:g} C{cx - w / 2:g} {base - h * .62:g} {cx - w * .22:g} {base - h * .92:g} {cx:g} {base - h:g} "
            f"C{cx + w * .22:g} {base - h * .92:g} {cx + w / 2:g} {base - h * .62:g} {cx + w / 2:g} {base:g}Z")


def onion(cx, base, w, h) -> str:
    return (f"M{cx - w / 2:g} {base:g} C{cx - w * .85:g} {base - h * .3:g} {cx - w * .75:g} {base - h * .62:g} {cx - w * .14:g} {base - h * .8:g} "
            f"Q{cx - w * .03:g} {base - h * .87:g} {cx:g} {base - h:g} Q{cx + w * .03:g} {base - h * .87:g} {cx + w * .14:g} {base - h * .8:g} "
            f"C{cx + w * .75:g} {base - h * .62:g} {cx + w * .85:g} {base - h * .3:g} {cx + w / 2:g} {base:g}Z")


def crescent(cx, cy, r, k=None) -> str:
    """Crescent opening to the right."""
    k = r * .8 if k is None else k
    hy = math.sqrt(r * r - k * k / 4)
    x = cx + k / 2
    return (f"M{x:.2f} {cy - hy:.2f} A{r} {r} 0 1 0 {x:.2f} {cy + hy:.2f} "
            f"A{r} {r} 0 0 1 {x:.2f} {cy - hy:.2f}Z")


def star8(x, y, r) -> str:
    pts = []
    for i in range(16):
        a = math.pi * i / 8
        rr = r if i % 2 == 0 else r * .55
        pts.append((round(x + rr * math.cos(a), 2), round(y + rr * math.sin(a), 2)))
    return poly(*pts)


def person(x, feet, h=30.0) -> str:
    r = h * .14
    hy = feet - h + r
    sw = h * .2
    top = hy + r + h * .05
    body = (f"M{x - sw:g} {feet:g} V{top + sw * .8:g} Q{x - sw:g} {top:g} {x:g} {top:g} "
            f"Q{x + sw:g} {top:g} {x + sw:g} {top + sw * .8:g} V{feet:g}Z")
    return body + " " + circle(x, hy, r)


def clip_open(d: Drawing):
    d.raw('<g clip-path="url(#clip)">', '<g clip-path="url(#clip)">')


def clip_close(d: Drawing):
    d.raw("</g>", "</g>")


def clipped(fn):
    def draw(d: Drawing):
        clip_open(d)
        fn(d)
        clip_close(d)
    draw.__name__ = fn.__name__
    return draw


def birds(d: Drawing, pts, role="dark"):
    s = " ".join(f"M{x} {y} q{3 * k} {-3 * k} {6 * k} 0 q{3 * k} {-3 * k} {6 * k} 0" for x, y, k in pts)
    d.stroke(role, s, 1.7)


def stars(d: Drawing, pts, role="light"):
    for x, y, r in pts:
        d.marks(role, f"M{x} {y - r} L{x + r * .3} {y - r * .3} L{x + r} {y} L{x + r * .3} {y + r * .3} "
                      f"L{x} {y + r} L{x - r * .3} {y + r * .3} L{x - r} {y} L{x - r * .3} {y - r * .3}Z")


def glow_halo(d: Drawing, x, y, r, role="glow2", op=.28):
    d.raw(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{d.c[role]}" opacity="{op}"/>' if d.paper else "", "")


def beam(d: Drawing, x, y, pts, op=.3):
    """Translucent light beam (papercut only) from (x, y) to the two points given."""
    if d.paper:
        (x1, y1), (x2, y2) = pts
        d.raw(f'<path d="M{x} {y} L{x1} {y1} L{x2} {y2}Z" fill="#fff" opacity="{op}"/>')


# ================================================================ CATHEDRAL VISIT
def cathedral_gothic(d: Drawing):
    d.disc("glow", 156, 56, 15)
    d.shape("light", cloud(14, 74, .8))
    d.band("far", hills(150, 10, 20))
    # nave front between the towers
    d.shape("stone", rrect(74, 86, 52, 80, 1))
    d.shape("stone", "M70 90 L100 56 L130 90Z")
    d.stroke("dark", "M100 56 V44 M95 49 H105", 1.6)
    d.shape("pop", circle(100, 104, 14), spot=True)
    d.shape("hero", circle(100, 104, 7.5), shadow=False)
    d.stroke("stone", " ".join(f"M{100 + 7.5 * math.cos(a):.1f} {104 + 7.5 * math.sin(a):.1f} L{100 + 14 * math.cos(a):.1f} {104 + 14 * math.sin(a):.1f}"
                               for a in [i * math.pi / 4 for i in range(8)]), 1.6, line=False)
    d.marks("glow2", circle(100, 104, 2.6))
    d.shape("stone2", parch(84, 124, 32, 42), shadow=False)
    d.shape("dark", parch(90, 132, 20, 34), shadow=False)
    # twin towers
    for x in (44, 126):
        d.shape("stone", rrect(x, 62, 30, 104, 1))
        d.shape("stone", f"M{x - 2} 64 L{x + 15} 16 L{x + 32} 64Z")
        d.shape("stone2", f"M{x + 15} 16 L{x + 32} 64 L{x + 21} 64Z", shadow=False, line=False)
        d.stroke("dark", f"M{x + 15} 16 V8", 1.6)
        for px in (x, x + 30):
            d.shape("stone", f"M{px - 3.5} 68 L{px} 52 L{px + 3.5} 68Z", shadow=False)
        d.marks("dark", parch(x + 8, 74, 14, 34))
        d.marks("dark", parch(x + 9, 120, 12, 22))
        d.stroke("stone2", f"M{x} 114 H{x + 30}", 1.6, line=False)
    d.band("ground", hills(166, 3))
    d.band("near", hills(184, 3, 30), line=False)


def cathedral_rose(d: Drawing):
    d.band("stone", "M-30 -10 H230", shadow=False, line=False)
    d.stroke("stone2", "M-10 20 H40 M160 20 H210 M-10 172 H210 M-10 186 H210", 1.4, line=False)
    d.shape("stone2", parch(20, 2, 160, 200))
    d.shape("stone", circle(100, 100, 70))
    d.shape("dark", circle(100, 100, 61), shadow=False)
    cx, cy = 100, 100
    for i in range(16):
        a = i * math.pi / 8
        d.shape("hero2" if i % 2 else "mid", circle(round(cx + 51 * math.cos(a), 1), round(cy + 51 * math.sin(a), 1), 7.5), shadow=False)
    for i in range(8):
        a = i * math.pi / 4 + math.pi / 8
        x, y = round(cx + 30 * math.cos(a), 1), round(cy + 30 * math.sin(a), 1)
        d.shape("pop" if i % 2 else "hero", ellipse(x, y, 15, 9), shadow=False, spot=i % 2 == 1,
                extra=f'transform="rotate({math.degrees(a):.1f} {x} {y})"')
    d.stroke("stone", " ".join(f"M{cx + 17 * math.cos(a):.1f} {cy + 17 * math.sin(a):.1f} L{cx + 60 * math.cos(a):.1f} {cy + 60 * math.sin(a):.1f}"
                               for a in [i * math.pi / 4 for i in range(8)]), 3.2)
    d.stroke("stone", circle(cx, cy, 42), 3)
    d.shape("glow2", circle(cx, cy, 15), shadow=False)
    d.shape("pop", star8(cx, cy, 9), shadow=False)
    d.marks("hero2", circle(cx, cy, 3))


def cathedral_onion(d: Drawing):
    d.disc("glow", 160, 64, 14)
    d.shape("light", cloud(8, 60, .8))
    d.band("far", hills(150, 8, 30))
    # back domes
    for x, role in [(76, "mid"), (124, "mid")]:
        d.shape("light", rrect(x - 8, 92, 16, 40, 1))
        d.shape(role, onion(x, 94, 22, 30))
        d.stroke("hero2", f"M{x} 64 V56 M{x - 3} 59 H{x + 3}", 1.4)
    # central tent tower
    d.shape("light", rrect(87, 58, 26, 80, 1))
    d.shape("hero", "M85 60 L100 24 L115 60Z", spot=True)
    d.stroke("light", "M92 50 L100 30 L108 50 M89 58 L100 34 L111 58", 1.4, line=False)
    d.shape("hero2", onion(100, 26, 10, 14))
    d.stroke("hero2", "M100 12 V5 M97 8 H103", 1.4)
    d.marks("dark", arch(96, 66, 8, 12))
    # side drums and onion domes
    for x, role, stripe in [(56, "pop", "light"), (144, "hero2", "pop")]:
        d.shape("light", rrect(x - 13, 90, 26, 48, 1))
        d.marks("dark", arch(x - 3.5, 100, 7, 12))
        d.shape(role, onion(x, 92, 34, 46), spot=role == "pop")
        for k, y in enumerate((82, 70)):
            hw = 14 if k == 0 else 11
            zz = f"M{x - hw} {y}" + "".join(f" L{x - hw + (j + 1) * hw / 3:.1f} {y + (4 if j % 2 == 0 else 0)}" for j in range(6))
            d.stroke(stripe, zz, 2.2, line=False)
        d.stroke("hero2", f"M{x} 46 V36 M{x - 4} 40 H{x + 4}", 1.6)
    # galleried base
    d.shape("light", rrect(28, 126, 144, 40, 1))
    d.shape("pop", rrect(26, 122, 148, 6, 1.5), shadow=False)
    for x in range(36, 170, 16):
        d.marks("dark", arch(x, 136, 9, 16) if x != 92 else arch(x - 2, 134, 14, 32))
    d.band("ground", hills(166, 3))
    d.band("near", hills(184, 3, 30), line=False)


# ================================================================ MOSQUE VISIT
def mosque_domes(d: Drawing):
    d.disc("glow", 150, 46, 13)
    d.disc("sky", 156, 41, 11, shadow=False, line=False)
    stars(d, [(40, 34, 2.4), (122, 30, 2), (178, 74, 2), (72, 52, 1.8)], "glow2")
    d.band("far", hills(156, 6))
    # minarets
    for x in (34, 166):
        d.shape("light", f"M{x - 5} 160 V58 H{x + 5} V160Z")
        d.shape("light", rrect(x - 8, 92, 16, 5, 2))
        d.shape("light", rrect(x - 8, 64, 16, 5, 2))
        d.shape("hero2", f"M{x - 6} 59 L{x} 34 L{x + 6} 59Z", spot=True)
        d.stroke("hero2", f"M{x} 34 V28", 1.5)
        d.marks("dark", rrect(x - 1.5, 76, 3, 9, 1.5))
    # domes
    for x in (66, 134):
        d.shape("hero2", dome(x, 112, 30, 20))
        d.stroke("hero2", f"M{x} 92 V86", 1.4)
    d.shape("light", rrect(70, 90, 60, 12, 1))
    d.shape("hero2", dome(100, 92, 62, 46), spot=True)
    d.stroke("light", "M84 90 Q86 66 100 50", 2, line=False)
    d.stroke("hero2", "M100 46 V36", 1.8)
    d.marks("hero2", crescent(100, 31, 4.2))
    for x in range(76, 128, 12):
        d.marks("dark", arch(x, 93, 4, 7))
    # prayer hall
    d.shape("light", rrect(46, 110, 108, 52, 1))
    for x in (52, 66, 120, 134):
        d.marks("dark", parch(x, 124, 9, 22))
    d.shape("light", rrect(82, 104, 36, 58, 1))
    d.shape("hero", parch(88, 112, 24, 50), shadow=False)
    d.marks("dark", parch(93, 128, 14, 34))
    d.band("ground", hills(164, 3))
    d.band("near", hills(182, 3, 30), line=False)


def mosque_lantern(d: Drawing):
    d.disc("glow", 160, 90, 20, line=False)
    d.band("far", hills(150, 6, 10))
    holes = " ".join(parch(x, 42, 46, 130) for x in (-34, 18, 70, 122, 174))
    d.shape("wall", "M-30 -10 H230 V200 H-30Z " + holes, extra='fill-rule="evenodd"', line=False)
    for x in (-34, 18, 70, 122, 174):
        d.stroke("tile", parch(x, 42, 46, 130, close=False), 4)
    d.shape("tile", "M-30 172 H230 V200 H-30Z")
    d.stroke("tile2", "M-30 178 H230", 2, line=False)
    for x in range(-24, 230, 16):
        d.marks("tile2", f"M{x} 186 l5 5 l-5 5 l-5 -5Z")
    # hanging lantern
    clip_open(d)
    d.stroke("dark", "M100 -10 V44", 1.6)
    clip_close(d)
    glow_halo(d, 100, 88, 34)
    d.shape("brass", "M88 52 Q100 36 112 52Z")
    d.shape("brass", "M84 54 H116 L124 78 L114 110 H86 L76 78Z", spot=True)
    for pts in [((88, 60), (100, 60), (100, 102), (90, 102), (82, 78)), ((100, 60), (112, 60), (118, 78), (110, 102), (100, 102))]:
        d.shape("glass", poly(*pts), shadow=False, line=False)
    d.shape("glow2", "M94 66 H106 L110 80 L104 96 H96 L90 80Z", shadow=False)
    for x, y in [(91, 70), (109, 70), (90, 90), (110, 90), (100, 64), (100, 98)]:
        d.marks("pop", star8(x, y, 3))
    d.stroke("brass2", "M84 54 H116 M76 78 H124 M86 110 H114 M100 54 V110", 1.6, line=False)
    d.shape("brass", "M90 110 H110 L100 124Z")
    d.shape("brass", circle(100, 126, 3), shadow=False)


def mosque_iwan(d: Drawing):
    d.disc("glow", 160, 54, 14)
    d.shape("light", cloud(10, 60, .8))
    d.shape("tile2", dome(100, 60, 92, 52))
    d.stroke("light", "M74 56 Q76 30 100 14", 2.2, line=False)
    d.stroke("hero2", "M100 8 V-2", 2)
    d.band("far", hills(160, 4))
    for x in (22, 178):
        d.shape("tile", f"M{x - 6} 170 V60 H{x + 6} V170Z")
        d.shape("hero2", rrect(x - 9, 74, 18, 6, 2))
        d.shape("tile2", f"M{x - 7} 61 L{x} 40 L{x + 7} 61Z")
    d.shape("tile", rrect(36, 46, 128, 130, 1))
    d.stroke("hero2", rrect(42, 52, 116, 118, 1), 2.4)
    d.shape("tile3", parch(58, 64, 84, 112), shadow=False)
    d.stroke("hero2", parch(58, 64, 84, 112, close=False), 2.4)
    for x, y in [(50, 62), (150, 62), (48, 84), (152, 84), (50, 106), (150, 106)]:
        d.marks("light", star8(x, y, 5))
    # muqarnas: rows of little arches in the half-vault
    for row, (y, xs) in enumerate([(92, (72, 84, 96, 108, 120)), (102, (66, 78, 90, 102, 114, 126)), (112, (66, 78, 90, 102, 114, 126))]):
        for x in xs:
            d.shape("tile2" if row % 2 == 0 else "light", parch(x, y, 10, 10), shadow=False, line=row == 0)
    d.shape("tile2", parch(84, 128, 32, 48), shadow=False, spot=True)
    d.shape("wood", parch(90, 140, 20, 36), shadow=False)
    d.stroke("hero2", "M100 140 V176", 1.4)
    d.band("ground", hills(176, 2))


# ================================================================ PALACE TOUR
def palace_facade(d: Drawing):
    d.disc("glow", 160, 44, 13)
    d.shape("light", cloud(8, 46, .8))
    for x, y, r in [(10, 112, 16), (30, 106, 14), (172, 110, 15), (192, 104, 14)]:
        d.shape("deep", circle(x, y, r))
    d.band("far", hills(126, 3))
    # wings
    d.shape("roof", rrect(14, 74, 172, 9, 2))
    d.shape("palace", rrect(18, 80, 164, 54, 1))
    for row, y in enumerate((88, 108)):
        for x in range(24, 180, 12):
            if 64 < x < 132:
                continue
            d.marks("win", arch(x, y, 6, 12))
    d.stroke("palace2", "M18 104 H182", 1.4, line=False)
    # central pavilion
    d.shape("roof", dome(100, 52, 34, 26), spot=True)
    d.stroke("hero2", "M100 26 V18", 1.8)
    d.shape("palace", rrect(68, 54, 64, 80, 1))
    d.shape("palace2", "M64 64 L100 42 L136 64Z")
    d.shape("palace", "M72 62 L100 46 L128 62Z", shadow=False)
    d.marks("hero2", circle(100, 56, 3.5))
    for x in (72, 86, 110, 124):
        d.shape("light", rrect(x, 68, 4, 64, 1), shadow=False)
    for x in (78, 116):
        d.marks("win", arch(x, 74, 6, 14))
        d.marks("win", arch(x, 100, 6, 14))
    d.marks("win", arch(93, 70, 14, 22))
    d.shape("dark", arch(92, 106, 16, 28), shadow=False)
    # garden and fountain
    d.band("ground", "M-30 134 H230")
    for x in (20, 46, 154, 180):
        d.shape("deep", f"M{x} 160 L{x - 8} 160 Q{x - 8} 140 {x} 128 Q{x + 8} 140 {x + 8} 160Z")
    d.stroke("light", "M100 150 V126 M100 128 Q90 128 86 142 M100 128 Q110 128 114 142", 2.2)
    d.shape("light", ellipse(100, 154, 28, 7))
    d.shape("hero", ellipse(100, 152, 22, 4), shadow=False)
    d.band("near", "M-30 168 Q100 160 230 168")


def palace_crown(d: Drawing):
    d.disc("glow", 100, 96, 60)
    # cushion on a plinth
    d.shape("dark", rrect(62, 154, 76, 26, 2))
    d.shape("hero2", rrect(56, 150, 88, 8, 2), shadow=False)
    d.shape("velvet", "M34 134 Q100 120 166 134 Q172 146 166 154 Q100 164 34 154 Q28 146 34 134Z")
    for x, s in [(34, -1), (166, 1)]:
        d.stroke("gold", f"M{x} 150 q{4 * s} 4 {3 * s} 12", 2)
        d.shape("gold", f"M{x + 3 * s - 4} 160 h8 l2 10 h-12Z", shadow=False)
    # crown
    d.shape("velvet", "M64 112 C62 84 82 68 100 66 C118 68 138 84 136 112Z")
    for path in ["M66 112 C64 86 84 70 100 66", "M134 112 C136 86 116 70 100 66", "M84 112 C82 90 92 74 100 66", "M116 112 C118 90 108 74 100 66"]:
        d.limb("gold", path, 5, spot=True)
    for t in (.35, .65):
        pass
    d.shape("gold", circle(100, 60, 7))
    d.stroke("gold", "M100 52 V38 M93 45 H107", 4)
    d.shape("gold", rrect(60, 108, 80, 18, 3), spot=True)
    d.shape("light", rrect(58, 124, 84, 10, 4))
    for x in range(64, 140, 9):
        d.marks("dark", ellipse(x, 129, 1.2, 2))
    for x, role in [(72, "hero"), (86, "pop"), (100, "hero"), (114, "pop"), (128, "hero")]:
        d.marks(role, ellipse(x, 117, 3.4, 4) if role == "pop" else rrect(x - 3.5, 113, 7, 8, 1.5))
    for x, y in [(75, 86), (125, 86), (90, 74), (110, 74)]:
        d.marks("light", circle(x, y, 2.2))


def palace_guard(d: Drawing):
    d.disc("glow", 160, 50, 13)
    d.band("far", "M-30 112 H20 V84 H60 V74 H140 V84 H180 V112 H230", line=False)
    d.band("mid", "M-30 140 H230", line=False)
    # railings with gilded tips
    rails = " ".join(f"M{x} 140 V100" for x in range(-6, 210, 12))
    d.stroke("dark", rails + " M-10 108 H210 M-10 132 H210", 2.2)
    for x in range(-6, 210, 12):
        d.marks("gold", f"M{x - 2.5} 101 L{x} 94 L{x + 2.5} 101Z")
    # sentry box
    d.shape("box", rrect(24, 70, 44, 104, 1))
    d.shape("box2", "M18 74 L46 48 L74 74Z", spot=True)
    d.shape("dark", parch(32, 84, 28, 90), shadow=False)
    d.marks("gold", circle(46, 64, 3.2))
    # guard
    d.limb("dark", "M104 126 V170", 12)
    d.limb("dark", "M120 126 V170", 12)
    d.stroke("coat", "M108 132 V168 M124 132 V168", 1.8, line=False)
    d.shape("dark", rrect(94, 166, 18, 8, 3))
    d.shape("dark", rrect(114, 166, 18, 8, 3))
    d.limb("coat", "M95 82 L90 122", 9)
    d.limb("coat", "M129 82 L134 122", 9)
    d.shape("light", circle(90, 125, 4.6))
    d.shape("light", circle(134, 125, 4.6))
    d.shape("coat", "M94 78 Q112 72 130 78 L132 130 H92Z", spot=True)
    d.shape("light", rrect(92, 106, 40, 6, 1), shadow=False)
    d.marks("gold", rrect(108, 106, 8, 6, 1))
    for y in (86, 94, 100, 118, 124):
        d.marks("gold", circle(112, y, 1.6))
    d.shape("skin", rrect(103, 56, 18, 20, 7))
    d.stroke("gold", "M103 64 Q112 80 121 64", 1.4)
    d.shape("dark", "M98 64 C94 40 102 24 112 24 C124 24 132 40 126 64 Q112 69 98 64Z")
    d.band("ground", "M-30 170 H230")


# ================================================================ STREET ART TOUR
def wing(d: Drawing, cx, cy, side):
    rows = [(68, 9, "hero"), (52, 8, "pop"), (34, 7, "hero2")]
    for L, ry, role in rows:
        for a in range(150, 262, 14):
            ang = math.radians(a if side < 0 else 180 - a)
            x = round(cx + L / 2 * math.cos(ang), 1)
            y = round(cy + L / 2 * math.sin(ang), 1)
            d.shape(role, ellipse(x, y, L / 2, ry), shadow=role == "hero" and a == 150, spot=role == "pop",
                    extra=f'transform="rotate({math.degrees(ang):.1f} {x} {y})"')


def streetart_wings(d: Drawing):
    d.band("wall", "M-30 -10 H230", shadow=False, line=False)
    bricks = " ".join(f"M{x + (12 if (y // 12) % 2 else 0)} {y} h14" for y in range(12, 160, 12) for x in range(-20, 220, 40))
    d.stroke("wall2", bricks, 1.6, line=False)
    wing(d, 92, 118, -1)
    wing(d, 108, 118, 1)
    for x, y, role in [(46, 150, "hero"), (150, 146, "hero"), (70, 154, "pop"), (132, 156, "pop")]:
        d.stroke(role, f"M{x} {y} V{y + 10}", 2.4)
        d.marks(role, circle(x, y + 11, 1.8))
    d.shape("dark", person(100, 170, 52))
    d.band("ground", "M-30 168 H230")
    d.band("near", "M-30 182 H230", line=False)


def streetart_spray(d: Drawing):
    d.disc("glow", 100, 100, 70, line=False)
    d.shape("pop", "M118 30 C140 22 162 34 170 52 C182 56 186 72 174 80 C180 96 166 108 150 102 C140 116 118 110 116 96 C100 96 96 74 108 66 C102 52 104 36 118 30Z")
    for x, y, h in [(126, 104, 22), (148, 100, 30), (162, 96, 14)]:
        d.shape("pop", f"M{x - 3} {y - 4} V{y + h} a3 3 0 0 0 6 0 V{y - 4}Z", shadow=False)
    d.shape("hero2", circle(140, 64, 18), shadow=False)
    for x, y, r in [(112, 74, 4), (104, 64, 3), (118, 84, 2.6), (98, 78, 2.2), (108, 52, 2.4)]:
        d.shape("pop", circle(x, y, r), shadow=False)

    def can():
        d.shape("hero", rrect(70, 82, 50, 96, 8), spot=True)
        d.shape("light", "M70 90 Q70 70 95 68 Q120 70 120 90Z")
        d.shape("hero2", rrect(70, 112, 50, 34, 1), shadow=False)
        d.shape("pop", "M74 128 q10 -16 22 -2 q10 12 20 -4 V144 H74Z", shadow=False)
        d.shape("dark", rrect(86, 52, 18, 18, 3))
        d.shape("dark", rrect(100, 55, 8, 6, 1.5), shadow=False)
        d.stroke("light", "M78 92 V170", 3.2, line=False)
    group(d, "rotate(-24 95 120)", can)
    d.band("near", "M-30 182 H230", line=False)


def streetart_gable(d: Drawing):
    d.disc("glow", 160, 50, 14)
    d.band("far", "M-30 120 H10 V90 H30 V104 H44 V70 H160 V96 H176 V84 H196 V110 H230")
    d.shape("wall", "M44 176 V40 L58 30 H146 L156 40 V176Z")
    # the mural: a giant flower
    d.shape("mid", rrect(54, 42, 92, 128, 2), shadow=False)
    d.shape("hero2", circle(122, 64, 14), shadow=False)
    d.limb("near", "M98 168 C96 140 102 120 100 100", 5)
    d.shape("near", "M99 140 C84 128 70 132 64 144 C78 148 90 146 99 140Z", shadow=False)
    d.shape("near", "M101 130 C114 118 128 122 134 132 C122 138 110 136 101 130Z", shadow=False)
    for i in range(8):
        a = i * math.pi / 4
        x, y = round(100 + 17 * math.cos(a), 1), round(90 + 17 * math.sin(a), 1)
        d.shape("pop", ellipse(x, y, 12, 7), shadow=False, spot=True, extra=f'transform="rotate({math.degrees(a):.1f} {x} {y})"')
    d.shape("hero2", circle(100, 90, 10), shadow=False)
    d.marks("dark", circle(96, 88, 1.6))
    d.marks("dark", circle(104, 88, 1.6))
    d.stroke("dark", "M95 93 Q100 98 105 93", 1.4)
    # ladder and paint pot
    d.limb("dark", "M150 176 L168 66 M162 176 L180 66", 3)
    d.stroke("dark", " ".join(f"M{150 + (176 - y) * 18 / 110:.1f} {y} h12" for y in range(166, 70, -14)), 2.4)
    d.shape("hero", "M34 160 H52 L50 178 H36Z")
    d.stroke("pop", "M36 160 q8 6 14 0", 2)
    d.band("ground", "M-30 176 H230")


# ================================================================ CITY BIKE TOUR
def bike(d: Drawing, frame="hero", tyre="dark"):
    for x in (54, 146):
        d.stroke(tyre, circle(x, 140, 25), 5.5)
        d.stroke(tyre, " ".join(f"M{x} 140 L{x + 22 * math.cos(a):.1f} {140 + 22 * math.sin(a):.1f}" for a in [i * math.pi / 6 for i in range(12)]), .9, line=False)
        d.marks(tyre, circle(x, 140, 3))
    d.stroke(frame, "M28 128 A27 27 0 0 1 72 116", 3)
    d.stroke(frame, "M126 118 A27 27 0 0 1 172 124", 3)
    d.limb(frame, "M54 140 L96 142 L82 96 L54 140", 5)
    d.limb(frame, "M96 142 C104 120 118 106 128 98 L146 140", 5, spot=True)
    d.limb("dark", "M128 98 L124 82 L112 78", 4)
    d.limb("dark", "M124 82 L136 80", 4)
    d.shape("dark", "M70 92 Q82 86 94 92 Q90 98 80 97 Q72 97 70 92Z")
    d.stroke("dark", "M82 96 V92", 3)
    d.shape("light", circle(96, 142, 6))
    d.stroke("dark", "M96 142 L102 152 M92 132 L96 142", 2.4)


def citybike_basket(d: Drawing):
    d.disc("glow", 150, 52, 16)
    d.band("far", "M-30 112 H8 V84 L20 72 L32 84 V96 H50 V78 H70 V100 H88 V66 L98 54 L108 66 V100 H124 V86 H142 V104 H160 V80 L172 70 L184 80 V108 H230")
    d.band("mid", hills(150, 4))
    bike(d)
    # basket of flowers
    d.limb("dark", "M134 98 L144 102", 3)
    for x, y, r, role in [(140, 70, 7, "pop"), (152, 66, 6, "hero2"), (162, 72, 6.5, "pop"), (148, 78, 5, "light")]:
        d.shape(role, circle(x, y, r), spot=role == "pop")
        d.marks("hero2" if role != "hero2" else "pop", circle(x, y, r * .35))
    d.shape("near", "M140 76 C140 72 146 70 150 74 Z", shadow=False)
    d.shape("wicker", "M132 78 H170 L166 104 H136Z")
    d.stroke("wicker2", "M134 86 H168 M135 94 H167 M146 78 L145 104 M156 78 L156 104", 1.4, line=False)
    d.band("ground", "M-30 166 H230")
    d.band("near", "M-30 180 H230", line=False)


def citybike_bell(d: Drawing):
    d.disc("glow", 100, 100, 64, line=False)
    d.shape("light", cloud(20, 52, .9))
    d.band("far", hills(170, 6))
    # handlebar sweeping across the circle
    d.limb("dark", "M10 120 C40 98 70 92 100 92 C130 92 160 98 190 120", 9)
    d.limb("hero", "M100 92 L100 196", 12, spot=True)
    d.shape("dark", rrect(90, 86, 20, 14, 4))
    d.limb("wicker2", "M10 120 L36 104", 13)
    d.limb("wicker2", "M190 120 L164 104", 13)
    d.limb("dark", "M150 104 C160 114 170 120 178 124", 3)
    # the bell
    d.limb("silver2", "M66 96 L66 84", 4)
    d.shape("silver", dome(66, 86, 50, 38))
    d.shape("silver2", rrect(40, 82, 52, 8, 4), shadow=False)
    d.shape("light", "M52 78 Q50 64 62 54 Q56 66 58 78Z", shadow=False, line=False)
    d.marks("dark", circle(66, 46, 3.5))
    d.limb("pop", "M88 88 L108 74", 5, spot=True)
    d.stroke("dark", "M28 46 q-6 -6 -4 -14 M38 38 q-4 -8 0 -14 M98 46 q6 -6 4 -14", 2.4)
    # headlamp
    d.shape("silver", ellipse(100, 140, 16, 13))
    d.shape("glow2", ellipse(100, 140, 11, 9), shadow=False)
    d.marks("light", ellipse(96, 136, 4, 3))


def citybike_sign(d: Drawing):
    d.disc("glow", 100, 96, 66, line=False)
    d.band("far", hills(146, 6))
    d.band("mid", hills(164, 4, 20))
    d.limb("silver2", "M100 196 V120", 8)
    d.shape("light", circle(100, 76, 52))
    d.shape("sign", circle(100, 76, 46), spot=True)
    # bicycle pictogram
    d.stroke("light", circle(76, 92, 13) + " " + circle(124, 92, 13), 4.5)
    d.stroke("light", "M76 92 L96 92 L88 72 L76 92 M96 92 L114 70 L124 92 M88 72 H112 M110 62 H120 M86 66 H94", 4.2)
    for x, y in [(30, 168), (48, 176), (156, 172), (172, 164), (140, 180)]:
        d.limb("near", f"M{x} {y + 14} V{y}", 2.6)
        d.shape("pop", f"M{x - 5} {y + 2} V{y - 8} L{x - 2} {y - 4} L{x} {y - 9} L{x + 2} {y - 4} L{x + 5} {y - 8} V{y + 2}Z", spot=True)
    d.band("near", hills(186, 3), line=False)


# ================================================================ HOP-ON BUS
def hopbus_side(d: Drawing):
    d.disc("glow", 160, 42, 13)
    d.band("far", "M-30 90 H14 V72 H30 V60 L40 46 L50 60 V80 H70 V58 Q84 38 98 58 V82 H118 V40 H124 V30 H128 V40 H134 V76 H156 V62 H176 V80 H230")
    # passengers on the open top deck
    for x, role in [(46, "dark"), (62, "hero2"), (96, "dark"), (128, "pop"), (146, "dark")]:
        d.shape(role, person(x, 84, 22), spot=role == "pop")
    d.stroke("light", "M24 70 H176 M30 70 V82 M60 70 V82 M90 70 V82 M120 70 V82 M150 70 V82", 2.4)
    d.shape("bus", "M24 152 V86 Q24 80 30 80 H170 Q176 80 176 86 V152Z", spot=True)
    d.shape("hero2", rrect(24, 96, 152, 5, 1), shadow=False)
    for x in range(32, 150, 22):
        d.shape("light", rrect(x, 106, 17, 20, 2), shadow=False)
    d.shape("sky2", rrect(156, 104, 18, 26, 2), shadow=False)
    d.shape("dark", rrect(134, 106, 16, 42, 1), shadow=False)
    d.stroke("light", "M142 108 V146", 1.4, line=False)
    d.band("road", "M-30 160 H230", line=False)
    d.stroke("light", "M-10 176 h22 M40 176 h22 M90 176 h22 M140 176 h22 M190 176 h22", 2.4, line=False)
    for x in (56, 148):
        d.shape("dark", circle(x, 152, 13))
        d.shape("silver", circle(x, 152, 5), shadow=False)
    d.stroke("dark", "M16 158 H190", 3)


def hopbus_front(d: Drawing):
    d.disc("glow", 100, 40, 16, line=False)
    d.shape("far", "M-30 200 V60 H14 V42 H32 V70 H48 V200Z")
    d.shape("far", "M230 200 V54 H188 V34 H170 V66 H152 V200Z")
    for x, y in [(20, 80), (20, 100), (30, 120), (160, 80), (172, 100), (160, 120)]:
        d.marks("sky", rrect(x, y, 8, 10, 1))
    d.band("ground", "M-30 160 H230")
    d.shape("road", "M78 160 H122 L178 200 H22Z", line=False)
    d.stroke("light", "M100 164 V170 M100 176 V184 M100 190 V200", 3, line=False)
    # passengers and the open deck
    for x, role in [(72, "dark"), (90, "pop"), (110, "dark"), (128, "hero2")]:
        d.shape(role, person(x, 60, 22), spot=role == "pop")
    d.stroke("light", "M56 46 H144 M58 46 V58 M100 46 V58 M142 46 V58", 2.4)
    d.limb("dark", "M50 96 L40 92 V104", 3)
    d.limb("dark", "M150 96 L160 92 V104", 3)
    d.shape("bus", rrect(52, 56, 96, 112, 10), spot=True)
    d.shape("hero2", rrect(52, 72, 96, 5, 1), shadow=False)
    d.shape("dark", rrect(64, 82, 72, 10, 2), shadow=False)
    d.marks("glow2", rrect(70, 85, 34, 4, 1))
    d.shape("sky2", rrect(60, 98, 80, 36, 4), shadow=False)
    d.stroke("dark", "M100 98 V134", 2)
    d.shape("light", "M66 100 L80 100 L64 124Z", shadow=False, line=False)
    for x in (68, 132):
        d.shape("glow2", circle(x, 148, 7), shadow=False)
        d.marks("light", circle(x - 2, 146, 2))
    d.stroke("dark", "M88 144 H112 M88 150 H112", 2)
    d.shape("dark", rrect(48, 160, 104, 10, 3))
    d.shape("dark", rrect(56, 168, 16, 14, 3))
    d.shape("dark", rrect(128, 168, 16, 14, 3))


def hopbus_stop(d: Drawing):
    d.disc("glow", 152, 44, 14)
    d.band("far", "M-30 120 H10 V96 H30 V108 H46 V88 L56 76 L66 88 V114 H120 V96 H140 V84 H160 V104 H182 V92 H198 V118 H230")
    d.band("mid", "M-30 150 H230")
    d.limb("dark", "M60 176 V70", 5)
    d.shape("sign", circle(60, 62, 30), spot=True)
    d.shape("light", circle(60, 62, 23), shadow=False)
    d.marks("dark", rrect(44, 52, 32, 18, 4) + " " + circle(51, 72, 3.6) + " " + circle(69, 72, 3.6))
    d.marks("light", rrect(48, 56, 7, 6, 1) + " " + rrect(57, 56, 7, 6, 1) + " " + rrect(66, 56, 7, 6, 1))
    # route map board
    d.limb("dark", "M112 176 V140 M168 176 V140", 4)
    d.shape("light", rrect(98, 74, 84, 70, 4))
    d.shape("sky2", rrect(104, 80, 72, 58, 2), shadow=False)
    d.stroke("hero", "M110 128 C122 128 120 96 136 98 C152 100 146 124 160 120 C170 118 170 92 168 88", 3.4)
    for x, y in [(110, 128), (128, 104), (146, 108), (160, 120), (168, 88)]:
        d.shape("light", circle(x, y, 3.4), shadow=False)
        d.marks("dark", circle(x, y, 1.6))
    d.shape("pop", "M146 108 c-6 -6 -6 -16 0 -18 c6 2 6 12 0 18Z M146 90 a6 6 0 1 1 0.1 0Z", spot=True)
    d.shape("pop", circle(146, 96, 6), spot=True)
    d.marks("light", circle(146, 96, 2.4))
    d.band("ground", "M-30 176 H230")


# ================================================================ OBSERVATION DECK
def obsdeck_viewer(d: Drawing):
    d.disc("glow", 156, 50, 15)
    d.shape("light", cloud(14, 52, 1))
    d.shape("light", cloud(150, 92, .7))
    d.band("far", "M-30 140 H6 V124 H18 V112 H28 V130 H44 V104 H52 V96 H58 V128 H74 V116 H88 V136 H112 V120 H124 V106 H134 V132 H150 V118 H166 V108 H178 V134 H230")
    d.band("mid", "M-30 150 H230", line=False)
    d.stroke("dark", "M-10 142 H210 M-6 142 V170 M24 142 V170 M150 142 V170 M180 142 V170 M210 142 V170", 3)
    d.band("near", "M-30 168 H230")
    # coin-operated viewer
    d.shape("hero", "M84 172 L88 156 H108 L112 172Z")
    d.limb("hero", "M98 158 V116", 10)
    d.shape("hero2", rrect(91, 128, 14, 18, 2), shadow=False)
    d.marks("dark", rrect(96, 132, 4, 8, 1))
    d.stroke("dark", "M80 112 L98 122 L116 112", 3)
    d.shape("dark", rrect(42, 76, 22, 30, 8))
    d.shape("hero", rrect(56, 68, 78, 48, 16), spot=True)
    d.shape("hero2", "M64 70 Q95 56 126 70 L124 76 H66Z", shadow=False)
    d.shape("light", ellipse(134, 82, 6, 9))
    d.shape("light", ellipse(134, 102, 6, 9))
    d.marks("dark", ellipse(136, 82, 3, 5.5))
    d.marks("dark", ellipse(136, 102, 3, 5.5))
    d.marks("light", rrect(62, 84, 4, 22, 2))


def obsdeck_tower(d: Drawing):
    d.disc("glow", 52, 70, 18)
    d.shape("light", cloud(122, 108, 1.0))
    d.band("far", "M-30 150 H10 V132 H24 V122 H36 V140 H58 V128 H72 V144 H128 V126 H140 V116 H152 V136 H170 V124 H186 V142 H230")
    d.band("mid", "M-30 162 H20 V152 H44 V160 H150 V150 H176 V160 H230")
    d.shape("stone", "M93 172 L97 78 H103 L107 172Z")
    d.shape("stone", "M84 172 L95 120 L97 124 L90 172Z")
    d.shape("stone", "M116 172 L105 120 L103 124 L110 172Z")
    d.shape("hero", ellipse(100, 112, 9, 5))
    d.stroke("dark", "M100 50 V12", 2.4)
    d.shape("stone", "M96 50 L98 22 H102 L104 50Z")
    d.shape("hero", "M66 76 L74 90 H126 L134 76Z", spot=True)
    d.shape("stone", rrect(68, 62, 64, 14, 4))
    d.shape("glow2", rrect(72, 66, 56, 6, 2), shadow=False)
    d.stroke("dark", "M80 66 V72 M90 66 V72 M100 66 V72 M110 66 V72 M120 66 V72", 1.2, line=False)
    d.shape("hero", "M74 62 Q100 44 126 62Z")
    d.marks("pop", circle(100, 12, 2.5))
    d.band("near", "M-30 172 H230")


def obsdeck_clouds(d: Drawing):
    d.disc("glow", 50, 120, 26)
    d.shape("far", "M150 200 V110 H160 V96 H170 V110 H180 V200Z")
    d.shape("far", "M14 200 V124 H24 V112 H36 V200Z")
    # art deco skyscraper
    d.shape("stone", "M70 200 V96 H130 V200Z")
    d.shape("stone", "M78 98 V74 H122 V98Z")
    d.shape("stone", "M86 76 V58 H114 V76Z")
    d.shape("stone", "M92 60 V48 Q100 38 108 48 V60Z")
    d.shape("stone2", "M100 38 Q108 40 108 48 V60 H100Z M100 58 H114 V76 H100Z M100 74 H122 V98 H100Z M100 96 H130 V200 H100Z", shadow=False, line=False)
    d.stroke("dark", "M100 40 V8", 2.2)
    d.stroke("dark", " ".join(f"M{x} 104 V196" for x in (78, 88, 112, 122)) + " M86 82 V96 M94 82 V96 M106 82 V96 M114 82 V96", 1.8)
    d.stroke("pop", "M74 96 H126 M82 74 H118", 3)
    # viewing deck with tiny visitors
    d.stroke("dark", "M66 94 H134", 2.2)
    for x, role in [(84, "hero"), (114, "pop")]:
        d.shape(role, person(x, 96, 12), shadow=False, spot=role == "pop")
    d.marks("glow2", rrect(96, 64, 8, 10, 1))
    # sea of clouds
    for x, y, s in [(-20, 158, 1.8), (30, 150, 1.6), (110, 156, 1.8), (150, 148, 1.5), (60, 170, 2), (130, 172, 1.9)]:
        d.shape("light", cloud(x, y, s))
    d.band("light", "M-30 176 H230", line=False)


# ================================================================ FAMOUS BRIDGE
def bridge_suspension(d: Drawing):
    d.disc("glow", 104, 84, 26)
    d.band("far", "M-30 122 Q10 96 40 110 L60 124 H140 Q170 100 200 104 Q220 108 230 118")
    d.band("mid", waves(134, 3, 28))
    # towers
    for x in (60, 146):
        d.shape("bridge", rrect(x - 11, 34, 7, 112, 1))
        d.shape("bridge", rrect(x + 4, 34, 7, 112, 1))
        for y in (40, 62, 86, 110):
            d.shape("bridge", rrect(x - 11, y, 22, 5, 1), shadow=False)
    # main cables and hangers
    cab = "M-30 122 Q20 112 60 34 Q103 140 146 34 Q186 112 230 122"
    hangers = []
    for x in range(-24, 228, 7):
        if 52 < x < 68 or 138 < x < 154:
            continue
        if x < 60:
            t = (x + 30) / 90
            y = (1 - t) ** 2 * 122 + 2 * (1 - t) * t * 112 + t * t * 34
        elif x < 146:
            t = (x - 60) / 86
            y = (1 - t) ** 2 * 34 + 2 * (1 - t) * t * 140 + t * t * 34
        else:
            t = (x - 146) / 84
            y = (1 - t) ** 2 * 34 + 2 * (1 - t) * t * 112 + t * t * 122
        if y < 124:
            hangers.append(f"M{x} {y:.1f} V126")
    d.stroke("bridge", " ".join(hangers), 1, line=False)
    d.stroke("bridge", cab, 2.6)
    d.shape("bridge", "M-30 124 H230 V131 H-30Z", spot=True)
    d.stroke("dark", "M-30 131 H230", 1.6, line=False)
    d.band("near", waves(150, 3, 30))
    d.shape("light", cloud(-10, 148, 1.4))
    d.shape("light", cloud(120, 154, 1.3))
    d.stroke("light", "M30 168 h22 M100 176 h28 M150 166 h18", 2, line=False)
    d.band("deep", waves(178, 3, 34), line=False)


def bridge_bascule(d: Drawing):
    d.disc("glow", 100, 70, 22)
    d.band("far", "M-30 112 H8 V96 H24 V104 H36 V112 H160 V92 L170 82 L180 92 V100 H196 V108 H230")
    # side-span chains
    d.stroke("hero", "M-30 114 Q10 116 42 64 M158 64 Q190 116 230 114", 3)
    d.shape("stone", "M-30 124 H44 V130 H-30Z M156 124 H230 V130 H156Z")
    # raised bascules
    d.shape("hero", "M74 128 L92 94 L98 97 L80 131Z", spot=True)
    d.shape("hero", "M126 128 L108 94 L102 97 L120 131Z", spot=True)
    # high walkways
    d.shape("hero", rrect(70, 48, 60, 7, 1))
    d.shape("hero", rrect(70, 60, 60, 5, 1))
    d.stroke("light", "M74 51 H126", 1.2, line=False)
    for x0 in (38, 126):
        cx = x0 + 18
        d.shape("stone", rrect(x0, 46, 36, 102, 1))
        d.shape("roof", f"M{x0 + 4} 48 L{cx} 20 L{x0 + 32} 48Z", spot=True)
        for tx in (x0 + 2, x0 + 34):
            d.shape("stone", rrect(tx - 4, 34, 8, 20, 1), shadow=False)
            d.shape("roof", f"M{tx - 5} 35 L{tx} 22 L{tx + 5} 35Z", shadow=False)
        d.marks("dark", parch(cx - 5, 62, 10, 22))
        d.marks("dark", parch(cx - 4, 96, 8, 18))
        d.shape("dark", parch(x0 + 30 if x0 < 100 else x0 - 4, 118, 10, 30) if False else rrect(x0 - 2, 146, 40, 8, 1))
    d.band("mid", waves(150, 3, 26))
    # tall ship passing through
    d.shape("dark", "M82 150 H120 L114 160 H88Z")
    d.stroke("dark", "M100 150 V104", 1.8)
    d.shape("light", "M100 106 L118 144 H100Z")
    d.shape("light", "M98 112 L86 144 H98Z", shadow=False)
    d.band("near", waves(166, 3, 30))
    d.stroke("light", "M30 176 h20 M140 178 h24", 2, line=False)


def bridge_stone(d: Drawing):
    d.disc("glow", 150, 50, 14)
    d.band("far", hills(92, 8, 10))
    for x, w, h in [(30, 14, 16), (46, 16, 22), (130, 16, 18), (148, 14, 14)]:
        d.shape("mid", f"M{x} 100 V{100 - h} L{x + w / 2} {100 - h - 8} L{x + w} {100 - h} V100Z")
    d.shape("mid", "M100 100 V66 L104 50 L108 66 V100Z M94 100 V80 H114 V100Z")
    d.band("mid", "M-30 100 H230", line=False)
    # bridge with three round arches
    holes = " ".join(f"M{x - 25} 148 V140 A25 25 0 0 1 {x + 25} 140 V148Z" for x in (36, 100, 164))
    d.shape("stone", "M-30 108 H230 V148 H-30Z " + holes, extra='fill-rule="evenodd"')
    d.shape("stone", rrect(-30, 98, 260, 12, 1))
    d.stroke("stone2", "M-30 104 H230", 1.4, line=False)
    for x in (68, 132):
        d.shape("stone", f"M{x - 7} 148 V128 L{x} 120 L{x + 7} 128 V148Z", shadow=False)
    for x in (4, 68, 132, 196):
        d.stroke("dark", f"M{x} 98 V74", 2.2)
        d.shape("dark", f"M{x - 4} 74 H{x + 4} L{x + 3} 66 H{x - 3}Z")
        d.marks("glow2", rrect(x - 2, 68, 4, 5, 1))
    d.band("near", "M-30 148 H230")
    for x in (36, 100, 164):
        d.stroke("stone", f"M{x - 25} 152 A25 20 0 0 0 {x + 25} 152", 3, line=False)
    d.stroke("light", "M24 168 h16 M90 172 h22 M152 166 h18", 2, line=False)
    d.band("deep", waves(184, 3, 30), line=False)


# ================================================================ LIGHTHOUSE
def tower_stripes(d: Drawing, xb0, xb1, yb, xt0, xt1, yt, n, role, spot=False):
    """Bands of `role` on a tapered tower, base (xb0..xb1 at yb), top (xt0..xt1 at yt)."""
    def at(y):
        t = (yb - y) / (yb - yt)
        return xb0 + (xt0 - xb0) * t, xb1 + (xt1 - xb1) * t
    h = (yb - yt) / (2 * n)
    for i in range(n):
        y0 = yb - (2 * i + 1) * h
        y1 = y0 - h
        a0, b0 = at(y0)
        a1, b1 = at(y1)
        d.shape(role, poly((round(a0, 1), round(y0, 1)), (round(b0, 1), round(y0, 1)), (round(b1, 1), round(y1, 1)), (round(a1, 1), round(y1, 1))),
                shadow=False, spot=spot)


def lighthouse_cliff(d: Drawing):
    beam(d, 142, 44, [(-30, 0), (-30, 70)], .35)
    d.shape("light", cloud(30, 100, .8))
    birds(d, [(60, 40, 1), (76, 50, .8)])
    d.band("mid", waves(126, 3, 28))
    d.band("near", waves(150, 4, 32))
    # headland
    d.shape("rock", "M76 200 L84 156 L104 136 L124 126 L170 122 L230 132 V200Z")
    d.shape("rock2", "M104 136 L110 160 L96 200 H76 L84 156Z", shadow=False, line=False)
    d.shape("grass", "M102 136 L122 124 L170 120 L230 128 V136 Q180 130 150 134 Q126 136 102 140Z", shadow=False)
    # keeper's cottage
    d.shape("light", rrect(160, 106, 30, 18, 1))
    d.shape("pop", "M156 108 L175 94 L194 108Z")
    d.marks("dark", rrect(166, 112, 6, 7, 1))
    # tower
    d.shape("light", "M128 128 L132 56 H152 L156 128Z")
    tower_stripes(d, 128, 156, 128, 132, 152, 56, 3, "pop", spot=True)
    d.shape("dark", rrect(126, 50, 32, 7, 2))
    d.stroke("dark", "M128 50 V44 H156 V50", 1.4)
    d.shape("glow2", rrect(134, 34, 16, 16, 1))
    d.stroke("dark", "M142 34 V50", 1.4)
    d.shape("pop", "M131 36 Q142 22 153 36Z")
    d.stroke("dark", "M142 26 V20", 1.8)
    d.marks("dark", rrect(139, 96, 6, 9, 1))
    # surf
    d.shape("light", "M62 170 Q70 150 84 156 Q78 146 90 142 Q86 156 94 160 Q80 162 76 172Z", shadow=False)
    d.stroke("light", "M20 140 h18 M40 166 h14", 2, line=False)
    d.band("deep", waves(178, 3, 30), line=False)


def lighthouse_lamp(d: Drawing):
    beam(d, 100, 94, [(-30, 40), (-30, 150)], .28)
    beam(d, 100, 94, [(230, 40), (230, 150)], .28)
    stars(d, [(30, 30, 2.4), (170, 34, 2), (176, 150, 2), (22, 150, 2)], "glow2")
    d.shape("pop", "M48 62 Q100 18 152 62Z", spot=True)
    d.shape("dark", rrect(44, 60, 112, 7, 2))
    d.shape("dark", circle(100, 30, 6))
    d.stroke("dark", "M100 24 V12", 2)
    d.shape("sky2", rrect(54, 66, 92, 64, 1))
    # fresnel lens
    d.shape("glow", "M82 76 Q100 68 118 76 L122 104 Q100 112 78 104Z")
    d.shape("glow2", "M88 80 Q100 76 112 80 L115 100 Q100 104 85 100Z", shadow=False)
    d.stroke("glow", "M82 84 Q100 90 118 84 M80 94 Q100 100 120 94", 1.6, line=False)
    d.marks("light", circle(100, 90, 4))
    d.limb("dark", "M90 108 V128 M110 108 V128", 4)
    d.stroke("dark", "M54 66 V130 M77 66 V130 M123 66 V130 M146 66 V130 M54 98 H76 M124 98 H146", 2.2)
    # gallery and tower top
    d.shape("dark", rrect(34, 128, 132, 8, 2))
    d.stroke("dark", "M38 128 V114 H162 V128 M58 114 V128 M78 114 V128 M122 114 V128 M142 114 V128", 1.6)
    d.shape("light", "M56 136 H144 L148 200 H52Z")
    d.shape("pop", "M55 156 H145 L146 176 H54Z", shadow=False, spot=True)
    d.marks("dark", parch(94, 140, 12, 14))


def lighthouse_gull(d: Drawing):
    d.disc("glow", 60, 52, 16)
    d.shape("light", cloud(130, 40, .9))
    d.band("mid", waves(118, 3, 26))
    # breakwater with a little harbour light
    d.shape("stone", "M-30 124 H70 L78 136 H-30Z")
    d.shape("pop", "M48 124 L50 84 H62 L64 124Z", spot=True)
    d.shape("light", "M49 108 H63 L63.5 116 H48.6Z", shadow=False)
    d.shape("dark", rrect(46, 80, 20, 4, 1))
    d.shape("glow2", rrect(51, 70, 10, 10, 1))
    d.shape("pop", "M48 71 Q56 62 64 71Z")
    d.band("near", waves(144, 4, 30))
    d.stroke("light", "M100 132 h18 M20 154 h16", 2, line=False)
    # mooring bollard
    d.shape("dark", "M118 200 V156 H166 V200Z")
    d.shape("dark", rrect(110, 146, 64, 12, 6))
    d.stroke("rope", "M120 166 Q142 176 166 164 M120 172 Q142 182 166 170", 3)
    # gull, facing left
    d.limb("feet", "M136 128 L134 146 M148 128 L150 146", 2.4)
    d.shape("gull", "M100 96 C108 88 120 90 128 96 C146 98 168 108 184 118 L164 120 C150 130 128 132 116 122 C106 114 100 106 100 96Z")
    d.shape("gull2", "M118 104 C136 96 162 100 184 116 L176 122 C160 120 144 122 126 118Z", spot=True)
    d.shape("dark", "M170 112 L188 118 L176 124 Z M160 112 L170 113 L174 122 L164 121Z", shadow=False)
    d.marks("light", circle(171, 117, 1.5))
    d.shape("gull", circle(108, 90, 12))
    d.shape("beak", "M98 88 L80 92 L84 95 L98 96Z")
    d.marks("pop", circle(85, 93.5, 1.6))
    d.marks("dark", circle(106, 86, 2))


# ================================================================ MONASTERY STAY
def monastery_meteora(d: Drawing):
    d.disc("glow", 160, 52, 15)
    birds(d, [(30, 52, 1), (44, 44, .8)])
    d.band("far", "M-30 130 L20 104 L50 116 L84 92 L120 112 L160 96 L230 122")
    # rock pillars
    d.shape("rock2", "M6 200 C10 160 4 128 14 110 Q26 98 40 108 C48 128 42 170 46 200Z")
    d.shape("rock2", "M154 200 C156 168 150 136 160 120 Q172 112 184 120 C190 140 186 172 192 200Z")
    d.shape("rock", "M66 200 C70 152 62 112 70 86 Q78 72 100 72 Q124 72 130 88 C138 114 128 152 134 200Z")
    d.stroke("rock2", "M84 96 C80 130 86 160 82 196 M112 92 C118 126 112 160 118 196 M98 120 C96 150 100 170 98 196", 2.2, line=False)
    # monastery on the summit
    d.shape("light", rrect(74, 52, 38, 24, 1))
    d.shape("roof", "M70 54 L78 44 H108 L116 54Z", spot=True)
    d.shape("light", rrect(106, 40, 18, 34, 1))
    d.shape("roof", dome(115, 42, 16, 12), spot=True)
    d.stroke("dark", "M115 30 V24 M112 27 H118", 1.4)
    for x in (80, 90, 100):
        d.marks("dark", arch(x, 60, 5, 9))
    d.marks("dark", arch(112, 50, 6, 10))
    d.shape("light", rrect(66, 68, 12, 10, 1))
    d.shape("roof", "M64 70 L72 63 L80 70Z", shadow=False)
    d.band("near", hills(176, 6))
    for x in (40, 150, 168):
        d.shape("deep", f"M{x} 182 C{x - 7} 170 {x - 4} 156 {x} 146 C{x + 4} 156 {x + 7} 170 {x} 182Z")
    d.band("deep", hills(188, 3), line=False)


def monastery_bell(d: Drawing):
    d.disc("glow", 100, 70, 34, line=False)
    d.shape("light", cloud(150, 120, .8))
    d.band("far", hills(156, 6))
    for x, h in [(28, 60), (174, 52)]:
        d.shape("deep", f"M{x} 176 C{x - 10} 150 {x - 6} {176 - h * .8} {x} {176 - h} C{x + 6} {176 - h * .8} {x + 10} 150 {x} 176Z")
    # bell gable with one big opening
    hole = arch(70, 50, 60, 66)
    d.shape("stone", "M44 180 V90 H56 V64 Q100 18 144 64 V90 H156 V180Z " + hole, extra='fill-rule="evenodd"')
    d.stroke("stone2", arch(70, 50, 60, 66).rstrip("Z"), 3, line=False)
    d.stroke("dark", "M100 32 V16 M94 22 H106", 2.4)
    d.shape("stone", rrect(40, 86, 120, 6, 1), shadow=False)
    d.shape("stone", rrect(64, 114, 72, 6, 1), shadow=False)
    # bell
    d.shape("dark", rrect(80, 56, 40, 6, 2))
    d.stroke("dark", "M100 62 V68", 3)
    d.shape("bell", "M86 104 C86 82 90 68 100 68 C110 68 114 82 114 104 Q118 108 122 112 H78 Q82 108 86 104Z", spot=True)
    d.shape("bell2", rrect(80, 108, 40, 4, 2), shadow=False)
    d.stroke("bell2", "M88 84 H112", 1.6, line=False)
    d.marks("light", "M92 76 Q90 88 90 100 L93 100 Q93 86 95 76Z")
    d.shape("dark", circle(100, 114, 4))
    d.stroke("rope", "M120 59 Q132 90 128 150", 2.4)
    d.marks("dark", arch(94, 140, 12, 20))
    d.band("ground", hills(178, 3))


def monastery_cloister(d: Drawing):
    d.disc("glow", 150, 30, 12, line=False)
    d.shape("deep", rrect(-30, 58, 260, 76, 0), shadow=False, line=False)
    holes = " ".join(arch(x, 70, 30, 60) for x in (-20, 26, 72, 118, 164))
    d.shape("wall", "M-30 56 H230 V136 H-30Z " + holes, extra='fill-rule="evenodd"')
    for x in (-20, 26, 72, 118, 164):
        d.stroke("stone2", arch(x, 70, 30, 60).rstrip("Z"), 2, line=False)
    for x in (10, 56, 102, 148, 194):
        d.shape("stone", rrect(x - 5, 92, 10, 4, 1), shadow=False)
    d.shape("roof", "M-30 30 H230 V58 H-30Z", spot=True)
    d.stroke("roof2", " ".join(f"M{x} 32 V56" for x in range(-24, 230, 10)), 1.6, line=False)
    d.shape("roof", rrect(-30, 54, 260, 6, 1))
    # garden
    d.band("grass", "M-30 136 H230")
    d.shape("ground", "M90 136 H110 L130 200 H70Z", shadow=False)
    for x in (38, 164):
        d.shape("deep", f"M{x} 160 C{x - 10} 140 {x - 7} 112 {x} 96 C{x + 7} 112 {x + 10} 140 {x} 160Z")
    # well
    d.shape("stone", rrect(80, 146, 40, 26, 3))
    d.shape("stone2", ellipse(100, 146, 20, 4), shadow=False)
    d.stroke("stone2", "M80 158 H120 M92 146 V158 M108 158 V172", 1.4, line=False)
    d.stroke("dark", "M84 146 V118 Q100 102 116 118 V146", 2.6)
    d.stroke("dark", "M100 110 V128", 1.4)
    d.shape("wood", rrect(95, 126, 10, 9, 2))
    d.band("near", "M-30 186 H230", line=False)


# ================================================================ PILGRIMAGE WALK
def pilgrim_shell(d: Drawing):
    d.disc("glow", 100, 100, 66, line=False)
    d.limb("wood", "M150 186 L60 18", 6)
    d.stroke("dark", "M82 58 Q76 72 74 80", 1.4)
    d.shape("gourd", "M74 80 C66 80 66 92 70 96 C60 100 60 120 74 122 C88 120 88 100 78 96 C82 92 82 80 74 80Z", spot=True)
    d.stroke("dark", "M68 96 H80", 1.6)
    # scallop shell
    hx, hy, R = 100, 160, 74
    angs = [math.radians(a) for a in range(205, 340, 15)]
    pts = [(hx + R * math.cos(a), hy + R * math.sin(a)) for a in angs]
    path = f"M{hx} {hy} L{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for a0, a1, (x1, y1) in zip(angs, angs[1:], pts[1:]):
        am = (a0 + a1) / 2
        path += f" Q{hx + R * 1.1 * math.cos(am):.1f} {hy + R * 1.1 * math.sin(am):.1f} {x1:.1f} {y1:.1f}"
    path += "Z"
    d.shape("shell", "M74 162 L80 146 L100 150Z M126 162 L120 146 L100 150Z")
    d.shape("shell", path)
    ribs = " ".join(f"M{hx + 10 * math.cos(a):.1f} {hy + 10 * math.sin(a):.1f} L{hx + R * .98 * math.cos(a):.1f} {hy + R * .98 * math.sin(a):.1f}" for a in angs[1:-1])
    d.stroke("shell2", ribs, 2.4)
    d.shape("shell2", "M88 166 Q100 154 112 166 L100 172Z")


def pilgrim_waymarker(d: Drawing):
    d.disc("glow", 150, 54, 14)
    d.band("far", "M-30 118 Q20 96 60 104 Q100 84 140 98 Q180 88 230 108")
    d.shape("far", "M140 98 V80 L144 70 L148 80 V98Z M134 98 V88 H156 V98Z")
    d.band("mid", hills(134, 6, 10))
    d.shape("ground", "M98 200 Q112 170 132 150 Q148 136 146 128 L152 128 Q158 140 148 154 Q130 176 140 200Z", shadow=False)
    d.band("near", "M-30 156 Q30 150 70 158 Q110 166 120 200 H-30Z", line=False)
    # waymarker post
    d.shape("stone", "M44 176 V82 Q44 74 52 74 H84 Q92 74 92 82 V176Z")
    d.shape("tile", rrect(51, 82, 34, 34, 3), spot=True)
    rays = " ".join(f"M68 110 L{68 + 22 * math.cos(math.radians(a)):.1f} {110 + 22 * math.sin(math.radians(a)):.1f}" for a in range(200, 345, 18))
    d.stroke("arrow", rays, 2.6)
    d.marks("arrow", circle(68, 110, 3))
    d.shape("arrow", "M52 132 H74 V126 L86 138 L74 150 V144 H52Z", shadow=False)
    d.stroke("stone2", "M44 160 H92", 1.6, line=False)
    for x, y in [(26, 168), (110, 178), (166, 166), (180, 176), (18, 180)]:
        d.limb("grass", f"M{x} {y + 10} V{y}", 2.2)
        d.shape("pop", circle(x, y - 2, 4.5), spot=True)
        d.marks("dark", circle(x, y - 2, 1.4))
    d.band("deep", hills(190, 3), line=False)


def pilgrim_walker(d: Drawing):
    d.disc("glow", 150, 64, 18)
    d.band("far", "M-30 124 Q30 100 70 112 Q110 96 150 108 Q190 98 230 116")
    d.band("mid", hills(150, 6, 20))
    d.band("ground", "M-30 172 Q100 164 230 172")
    # pilgrim striding right
    d.limb("dark", "M96 110 L86 138 L74 162", 9)
    d.shape("dark", "M64 158 Q70 154 80 158 L80 166 H64Z")
    d.limb("coat2", "M98 72 L88 96 L96 108", 6)
    d.shape("pack", rrect(70, 64, 24, 40, 7))
    d.shape("pack2", rrect(72, 84, 20, 14, 4), shadow=False)
    d.marks("light", "M82 70 l-5 7 h10Z")
    d.shape("coat", "M90 64 Q102 60 108 66 L112 112 H90Z", spot=True)
    d.limb("dark", "M104 110 L116 136 L120 162", 9)
    d.shape("dark", "M114 158 H128 Q132 160 132 166 H114Z")
    d.limb("wood", "M134 168 L122 46", 4)
    d.limb("coat", "M104 72 L116 94 L126 90", 6)
    d.shape("skin", circle(103, 54, 8.5))
    d.shape("hat", ellipse(102, 48, 18, 4))
    d.shape("hat", "M92 48 Q93 34 102 34 Q111 34 112 48Z")
    d.stroke("pop", "M93 45 H111", 2)
    d.stroke("dark", "M122 54 Q118 60 120 66", 1.2)
    d.shape("light", "M116 66 L126 66 L121 72Z", shadow=False)


# ================================================================ SOUK SHOPPING
def lamp(d: Drawing, x, y, s, glass, kind, spot=False):
    def draw():
        d.stroke("dark", "M0 -200 V-14", 1.4 / s)
        d.shape("brass", "M-8 -12 Q0 -24 8 -12Z")
        if kind == 0:
            d.shape("brass", circle(0, 6, 16), spot=spot)
            d.shape(glass, circle(0, 6, 12), shadow=False)
            d.shape("glow2", circle(0, 6, 6), shadow=False)
            for i in range(8):
                a = i * math.pi / 4
                d.marks("brass", circle(round(9 * math.cos(a), 1), round(6 + 9 * math.sin(a), 1), 1.6))
            d.shape("brass", "M-5 21 H5 L0 30Z", shadow=False)
        else:
            d.shape("brass", "M-12 -12 H12 L16 10 L8 34 H-8 L-16 10Z", spot=spot)
            d.shape(glass, "M-8 -6 H8 L11 10 L5 28 H-5 L-11 10Z", shadow=False)
            d.shape("glow2", "M-3 2 H3 L5 12 L2 20 H-2 L-5 12Z", shadow=False)
            d.stroke("brass", "M-16 10 H16 M0 -12 V34", 1.6, line=False)
            d.shape("brass", "M-5 34 H5 L0 44Z", shadow=False)
    group(d, f"translate({x} {y}) scale({s})", draw)


def souk_lamps(d: Drawing):
    d.band("deep", "M-30 -10 H230", shadow=False, line=False)
    for x, y, r in [(100, 112, 40), (52, 70, 26), (152, 76, 26), (40, 148, 22), (160, 146, 22)]:
        glow_halo(d, x, y, r, "glow2", .22)
    clip_open(d)
    lamp(d, 52, 66, 1.1, "hero", 1)
    lamp(d, 152, 72, 1.1, "mid", 0)
    lamp(d, 40, 136, .9, "hero2", 0)
    lamp(d, 162, 134, .9, "pop", 1)
    lamp(d, 100, 104, 1.6, "pop", 1, spot=True)
    clip_close(d)


def rug(d: Drawing, x, y, w, h, base, border, med, spot=False):
    d.shape(base, rrect(x, y, w, h, 1), spot=spot)
    d.stroke(border, rrect(x + 4, y + 4, w - 8, h - 8, 1), 3)
    cx, cy = x + w / 2, y + h / 2
    d.shape(border, f"M{cx} {cy - h * .22} L{cx + w * .28} {cy} L{cx} {cy + h * .22} L{cx - w * .28} {cy}Z", shadow=False)
    d.shape(med, f"M{cx} {cy - h * .12} L{cx + w * .15} {cy} L{cx} {cy + h * .12} L{cx - w * .15} {cy}Z", shadow=False)
    for yy in (y + 12, y + h - 12):
        d.marks(med, f"M{cx} {yy - 3} l3 3 l-3 3 l-3 -3Z")
    d.stroke("light", " ".join(f"M{xx} {y + h} v5" for xx in range(int(x + 3), int(x + w - 1), 4)), 1.2, line=False)


def souk_rugs(d: Drawing):
    d.band("wall", "M-30 -10 H230", shadow=False, line=False)
    d.shape("wall2", "M30 200 V70 Q30 22 100 18 Q170 22 170 70 V200Z" if False else parch(26, 6, 148, 200), shadow=False, line=False)
    d.limb("wood", "M10 34 H190", 6)
    rug(d, 22, 36, 50, 96, "hero", "hero2", "light")
    rug(d, 128, 36, 50, 90, "mid", "light", "pop")
    rug(d, 68, 36, 64, 112, "pop", "hero2", "hero", spot=True)
    # folded rugs stacked on the floor
    for i, (role, stripe) in enumerate([("hero", "light"), ("hero2", "pop"), ("near", "hero2"), ("pop", "light")]):
        y = 176 - i * 9
        d.shape(role, rrect(36 + i * 3, y - 9, 128 - i * 6, 10, 3))
        d.stroke(stripe, f"M{44 + i * 3} {y - 4} H{156 - i * 3}", 1.4, line=False)
    d.band("dark", "M-30 178 H230", line=False)


def souk_teapot(d: Drawing):
    d.disc("glow", 100, 100, 64, line=False)
    # tray
    d.shape("brass2", ellipse(100, 166, 76, 14))
    d.shape("brass", ellipse(100, 162, 72, 11), shadow=False)
    d.stroke("brass2", "M44 162 Q100 172 156 162", 1.4, line=False)
    # tea glass
    d.shape("light", "M128 120 H164 L160 160 H132Z")
    d.shape("tea", "M130 132 H162 L160 160 H132Z", shadow=False, spot=True)
    d.stroke("hero2", "M129 126 H163", 2.4)
    d.shape("leaf", "M140 132 C134 120 140 110 150 112 C150 122 146 128 140 132Z", shadow=False)
    d.shape("leaf", "M144 134 C148 122 158 120 162 126 C156 132 150 134 144 134Z", shadow=False)
    # pour
    d.stroke("tea", "M110 56 Q138 54 146 128", 3)
    # teapot (raised for the pour)
    d.limb("silver2", "M44 72 C24 70 24 100 42 104", 6)
    d.shape("silver", "M50 128 Q44 126 48 118 C38 100 46 82 66 80 H78 C98 82 106 100 96 118 Q100 126 94 128Z")
    d.shape("silver", "M92 104 C102 98 104 74 112 58 L116 58 C110 76 108 100 96 112Z", spot=True)
    d.shape("silver2", rrect(60, 70, 24, 12, 3))
    d.shape("silver", dome(72, 72, 26, 20))
    d.shape("silver", "M68 54 L72 38 L76 54Z", shadow=False)
    d.shape("silver2", circle(72, 54, 3.5), shadow=False)
    d.stroke("silver2", "M50 104 Q72 112 94 104 M48 94 Q72 100 96 94", 1.6, line=False)
    d.marks("light", "M56 92 Q56 104 62 112 L58 112 Q52 102 54 92Z")
    d.shape("silver2", rrect(52, 126, 40, 6, 2), shadow=False)


# ================================================================ concept list
GOLD = {"gold": "#E2B04A", "gold2": "#B7862C"}
STONE = {"stone": "#D8CCB8", "stone2": "#B5A68E"}
BRASS = {"brass": "#D4A23C", "brass2": "#A87A24"}
TILES = {"tile": "#2E6DA4", "tile2": "#3BAFA8", "tile3": "#1E4670", "wood": "#9C6A38"}
BUS = {"bus": "#D7372B", "road": "#5B5F6B", "silver": "#C9CED6"}
NIGHT = {"sky": "#22294A", "sky2": "#2E3B5E", "far": "#3B4876", "mid": "#52628F", "deep": "#151B30"}
ROCK = {"rock": "#A89580", "rock2": "#8A7663", "roof": "#C8643B"}
SILVER = {"silver": "#C9CED6", "silver2": "#97A1AE"}

CONCEPTS = [
    # cathedral
    Concept("cathedral-gothic", "cathedral-visit", "Gothic spires", cathedral_gothic, overrides=STONE,
            checks=[("stone", "sky"), ("stone", "far"), ("stone", "glow"), ("pop", "stone")],
            fixes={"far": ["mid", "near"], "sky": ["sky2", "far"], "stone": ["#C2B194", "#B3A285"]}),
    Concept("cathedral-rose", "cathedral-visit", "Rose window", cathedral_rose, overrides=STONE,
            checks=[("pop", "hero"), ("hero2", "mid"), ("pop", "dark"), ("hero", "dark")], fixes={"mid": ["far", "near", "light"]}),
    Concept("cathedral-onion", "cathedral-visit", "Onion domes", cathedral_onion,
            checks=[("light", "sky"), ("pop", "sky"), ("hero2", "sky"), ("hero", "sky"), ("light", "far"), ("mid", "light")],
            fixes={"sky": ["sky2", "far", "mid"], "far": ["mid", "near"]}),
    # mosque
    Concept("mosque-domes", "mosque-visit", "Domes & minarets", mosque_domes, overrides=NIGHT,
            checks=[("light", "sky"), ("hero2", "sky"), ("light", "far"), ("hero", "light")], fixes={"hero": ["near", "deep"]}),
    Concept("mosque-lantern", "mosque-visit", "Arches & lantern", mosque_lantern,
            overrides={**BRASS, **TILES, "wall": "#F4EAD8", "glass": "#2E6DA4"},
            checks=[("brass", "wall"), ("brass", "far"), ("brass", "sky"), ("wall", "sky"), ("wall", "far")],
            fixes={"sky": ["sky2", "far", "mid"], "far": ["mid", "near"]}),
    Concept("mosque-iwan", "mosque-visit", "Tiled portal", mosque_iwan, overrides=TILES,
            checks=[("tile", "sky"), ("tile2", "sky"), ("tile2", "tile"), ("hero2", "tile")]),
    # palace
    Concept("palace-facade", "palace-tour", "Baroque palace", palace_facade,
            overrides={"palace": "#F2D07A", "palace2": "#D3A84A", "roof": "#5E9C8A", "win": "#4A5B6E"},
            checks=[("palace", "sky"), ("roof", "sky"), ("palace", "far"), ("palace", "ground"), ("deep", "sky")],
            fixes={"sky": ["sky2", "far", "light"], "far": ["mid", "near"], "ground": ["light", "mid"]}),
    Concept("palace-crown", "palace-tour", "Crown jewels", palace_crown, overrides={**GOLD, "velvet": "#9E2A3A"},
            checks=[("gold", "glow"), ("velvet", "glow"), ("gold", "velvet")], fixes={"glow": ["far", "light", "sky2", "mid"]}),
    Concept("palace-guard", "palace-tour", "Palace guard", palace_guard,
            overrides={**GOLD, "coat": "#C8332B", "skin": "#E8B48A", "box": "#F4EFE6", "box2": "#2F4B7C"},
            checks=[("dark", "mid"), ("coat", "mid"), ("box", "far"), ("box", "mid"), ("dark", "ground")],
            fixes={"mid": ["far", "sky2", "light"], "far": ["mid", "near"], "ground": ["light", "far"]}),
    # street art
    Concept("streetart-wings", "street-art-tour", "Mural wings", streetart_wings, overrides={"wall": "#F4EFE6", "wall2": "#E2D8C8"},
            checks=[("hero", "wall"), ("pop", "wall"), ("hero2", "wall"), ("hero", "pop"), ("hero2", "pop")], fixes={"hero2": ["mid", "near"]}),
    Concept("streetart-spray", "street-art-tour", "Spray can", streetart_spray,
            checks=[("hero", "glow"), ("pop", "glow"), ("hero", "hero2"), ("pop", "hero2"), ("hero", "pop")],
            fixes={"glow": ["light", "sky2", "far"], "hero2": ["glow2", "light", "mid"]}),
    Concept("streetart-gable", "street-art-tour", "Gable-end mural", streetart_gable, overrides={"wall": "#F4EFE6"},
            checks=[("pop", "mid"), ("near", "mid"), ("hero2", "mid"), ("wall", "far"), ("wall", "sky")],
            fixes={"mid": ["far", "sky2", "light"], "far": ["mid", "near", "deep"]}),
    # city bike
    Concept("citybike-basket", "city-bike-tour", "Bike with basket", citybike_basket, overrides={"wicker": "#C98F52", "wicker2": "#9C6A38"},
            checks=[("hero", "far"), ("hero", "sky"), ("dark", "far"), ("pop", "far"), ("wicker", "far")],
            fixes={"far": ["sky2", "light", "mid"], "hero": ["pop", "deep"]}),
    Concept("citybike-bell", "city-bike-tour", "Bike bell", citybike_bell, overrides={**SILVER, "wicker2": "#7A4A26"},
            checks=[("silver", "glow"), ("hero", "glow"), ("dark", "glow"), ("silver", "sky")], fixes={"glow": ["far", "mid", "near"]}),
    Concept("citybike-sign", "city-bike-tour", "Cycle-route sign", citybike_sign, overrides={**SILVER, "sign": "#2E6DA4"},
            checks=[("light", "glow"), ("sign", "glow"), ("pop", "far"), ("pop", "mid")], fixes={"glow": ["far", "mid", "sky2"], "mid": ["near", "deep"]}),
    # hop-on bus
    Concept("hopbus-side", "hop-on-bus", "Open-top bus", hopbus_side, overrides=BUS,
            checks=[("bus", "far"), ("bus", "sky"), ("dark", "far"), ("light", "sky")], fixes={"far": ["mid", "sky2", "light"], "sky": ["sky2", "far"]}),
    Concept("hopbus-front", "hop-on-bus", "Bus head-on", hopbus_front, overrides=BUS,
            checks=[("bus", "sky"), ("bus", "far"), ("bus", "ground"), ("pop", "sky")], fixes={"far": ["mid", "near"], "ground": ["light", "mid"]}),
    Concept("hopbus-stop", "hop-on-bus", "Bus stop & route", hopbus_stop, overrides={"sign": "#D7372B"},
            checks=[("sign", "far"), ("sign", "sky"), ("light", "far"), ("light", "mid")], fixes={"far": ["mid", "near", "deep"], "mid": ["near", "deep"]}),
    # observation deck
    Concept("obsdeck-viewer", "observation-deck", "Coin viewer", obsdeck_viewer,
            checks=[("hero", "sky"), ("hero", "far"), ("dark", "far"), ("hero", "near")], fixes={"far": ["sky2", "mid"], "hero": ["pop", "deep"]}),
    Concept("obsdeck-tower", "observation-deck", "Sky tower", obsdeck_tower, overrides=STONE,
            checks=[("stone", "sky"), ("hero", "sky"), ("stone", "far"), ("hero", "far")], fixes={"sky": ["sky2", "far"], "far": ["mid", "near"]}),
    Concept("obsdeck-clouds", "observation-deck", "Above the clouds", obsdeck_clouds, overrides={"stone": "#D9CDB6", "stone2": "#BCAE94"},
            checks=[("stone", "sky"), ("stone", "far"), ("light", "sky"), ("far", "sky")], fixes={"sky": ["sky2", "far"], "far": ["mid", "near"]}),
    # bridges
    Concept("bridge-suspension", "famous-bridge", "Suspension bridge", bridge_suspension, overrides={"bridge": "#C8452C"},
            checks=[("bridge", "sky"), ("bridge", "glow"), ("bridge", "far"), ("bridge", "mid")], fixes={"glow": ["glow2", "light"], "far": ["mid", "near", "deep"], "mid": ["near", "deep"]}),
    Concept("bridge-bascule", "famous-bridge", "Twin-tower bridge", bridge_bascule, overrides={**STONE, "roof": "#3E5A78"},
            checks=[("stone", "sky"), ("stone", "far"), ("hero", "sky"), ("stone", "glow"), ("dark", "mid")],
            fixes={"glow": ["glow2", "light", "mid"], "far": ["mid", "near"], "hero": ["near", "deep"]}),
    Concept("bridge-stone", "famous-bridge", "Old stone bridge", bridge_stone, overrides=STONE,
            checks=[("stone", "sky"), ("stone", "mid"), ("stone", "near"), ("mid", "sky")], fixes={"mid": ["near", "deep"], "near": ["deep", "mid"]}),
    # lighthouse
    Concept("lighthouse-cliff", "lighthouse", "Clifftop lighthouse", lighthouse_cliff,
            overrides={"rock": "#9A8676", "rock2": "#7A6656", "grass": "#7DB46C"}, palettes=["coastal", "meadow", "blush", "dusk"],
            checks=[("light", "sky"), ("pop", "sky"), ("light", "mid"), ("rock", "near")], fixes={"sky": ["sky2", "far"], "near": ["deep", "mid"]}),
    Concept("lighthouse-lamp", "lighthouse", "Lantern room", lighthouse_lamp, overrides=NIGHT,
            checks=[("glow", "sky2"), ("pop", "sky"), ("light", "sky")]),
    Concept("lighthouse-gull", "lighthouse", "Harbour gull", lighthouse_gull, palettes=["coastal", "meadow", "blush", "dusk"],
            overrides={**STONE, "gull": "#FFFFFF", "gull2": "#A9B4C2", "beak": "#F2C14E", "feet": "#E8954A", "rope": "#D9B98A"},
            checks=[("gull", "sky"), ("gull", "mid"), ("gull", "near"), ("gull2", "sky"), ("pop", "mid")], fixes={"sky": ["sky2", "far"]}),
    # monastery
    Concept("monastery-meteora", "monastery-stay", "Clifftop monastery", monastery_meteora, overrides=ROCK,
            checks=[("light", "sky"), ("rock", "far"), ("rock", "sky"), ("roof", "sky")], fixes={"sky": ["sky2", "far"], "far": ["sky2", "light"]}),
    Concept("monastery-bell", "monastery-stay", "Bell gable", monastery_bell, overrides={**STONE, "bell": "#C08A3E", "bell2": "#8E6224", "rope": "#8A5A33"},
            checks=[("stone", "sky"), ("bell", "sky"), ("bell", "glow"), ("stone", "far")], fixes={"glow": ["light", "sky2"], "far": ["mid", "near"], "sky": ["sky2", "far"]}),
    Concept("monastery-cloister", "monastery-stay", "Cloister garden", monastery_cloister,
            overrides={**STONE, "wall": "#F2E8D6", "roof": "#C8643B", "roof2": "#A64E2C", "grass": "#79AE6E", "wood": "#9C6A38"},
            checks=[("wall", "deep"), ("roof", "sky"), ("deep", "grass"), ("stone", "grass")]),
    # pilgrimage
    Concept("pilgrim-shell", "pilgrimage-walk", "Scallop shell & staff", pilgrim_shell,
            overrides={"shell": "#F6E3BC", "shell2": "#D49A52", "wood": "#8A5A33", "gourd": "#D9893B"},
            checks=[("shell", "glow"), ("gourd", "glow"), ("wood", "glow"), ("shell", "sky")], fixes={"glow": ["far", "mid", "near"]}),
    Concept("pilgrim-waymarker", "pilgrimage-walk", "Waymarker", pilgrim_waymarker,
            overrides={**STONE, "tile": "#2E5FA8", "arrow": "#F2C230", "grass": "#5E9C6A"},
            checks=[("stone", "mid"), ("stone", "sky"), ("arrow", "stone"), ("pop", "near")], fixes={"mid": ["near", "deep"], "near": ["deep", "mid"]}),
    Concept("pilgrim-walker", "pilgrimage-walk", "Pilgrim on the way", pilgrim_walker,
            overrides={"coat": "#3E7CB1", "coat2": "#2C5D88", "pack": "#E07A3F", "pack2": "#B85A28", "skin": "#E8B48A", "hat": "#C9A16B", "wood": "#8A5A33"},
            checks=[("coat", "far"), ("pack", "far"), ("dark", "mid"), ("hat", "sky"), ("coat", "mid")], fixes={"far": ["sky2", "light"], "mid": ["near", "far"]}),
    # souk
    Concept("souk-lamps", "souk-shopping", "Hanging lamps", souk_lamps, overrides=BRASS,
            checks=[("brass", "deep"), ("pop", "brass"), ("hero", "brass"), ("mid", "brass")], fixes={"mid": ["far", "near"]}),
    Concept("souk-rugs", "souk-shopping", "Rug stall", souk_rugs, overrides={"wall": "#E9C9A0", "wall2": "#D8AE7E", "wood": "#7A4A26"},
            checks=[("hero", "wall2"), ("pop", "wall2"), ("mid", "wall2"), ("hero2", "pop"), ("hero2", "hero")], fixes={"mid": ["near", "deep"], "hero2": ["light", "glow2"]}),
    Concept("souk-teapot", "souk-shopping", "Mint tea pour", souk_teapot,
            overrides={**SILVER, **BRASS, "tea": "#B5562B", "leaf": "#5E9C4A"},
            checks=[("silver", "glow"), ("brass", "glow"), ("tea", "glow"), ("light", "glow")], fixes={"glow": ["far", "mid", "near", "deep"]}),
]
