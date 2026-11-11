"""Culture C: parades, theatre, opera, live music, dance shows, tea ceremonies, calligraphy, pottery,
language classes, volunteering, homestays and Holi."""
import math

from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group  # noqa: F401

ALL = ["golden", "coastal", "meadow", "blush", "dusk"]
SEA = ["coastal", "meadow", "blush", "dusk"]


# ================================================================ private helpers
def poly(*pts, close=True) -> str:
    s = "M" + " L".join(f"{x:g} {y:g}" for x, y in pts)
    return s + ("Z" if close else "")


def rot(fn_d: Drawing, ang, cx, cy, fn):
    group(fn_d, f"rotate({ang} {cx} {cy})", fn)


def note(x, y, s=1.0):
    """A quaver: head, stem and flag, as one path."""
    return (ellipse(x, y, 4.6 * s, 3.4 * s) + f" M{x + 3 * s:.1f} {y - 1 * s:.1f} V{y - 17 * s:.1f} "
            f"C{x + 6 * s:.1f} {y - 12 * s:.1f} {x + 12 * s:.1f} {y - 12 * s:.1f} {x + 11 * s:.1f} {y - 5 * s:.1f} "
            f"C{x + 10 * s:.1f} {y - 9 * s:.1f} {x + 7 * s:.1f} {y - 10 * s:.1f} {x + 5 * s:.1f} {y - 10 * s:.1f} V{y - 1 * s:.1f}Z")


def notes(d: Drawing, pts, role="dark"):
    for x, y, s in pts:
        d.marks(role, note(x, y, s))


def star(x, y, r, k=0.45, n=5, rot_=-90):
    pts = []
    for i in range(2 * n):
        a = math.radians(rot_ + i * 180 / n)
        rr = r if i % 2 == 0 else r * k
        pts.append(f"{x + rr * math.cos(a):.1f} {y + rr * math.sin(a):.1f}")
    return "M" + " L".join(pts) + "Z"


def heart(x, y, s=1.0):
    return (f"M{x} {y + 8 * s} C{x - 4 * s} {y + 4 * s} {x - 10 * s} {y} {x - 10 * s} {y - 4 * s} "
            f"C{x - 10 * s} {y - 9 * s} {x - 5 * s} {y - 11 * s} {x} {y - 6 * s} "
            f"C{x + 5 * s} {y - 11 * s} {x + 10 * s} {y - 9 * s} {x + 10 * s} {y - 4 * s} "
            f"C{x + 10 * s} {y} {x + 4 * s} {y + 4 * s} {x} {y + 8 * s}Z")


def annulus(cx, cy, r1, r2, a1, a2):
    p = lambda r, a: f"{cx + r * math.cos(math.radians(a)):.1f} {cy + r * math.sin(math.radians(a)):.1f}"
    big = 1 if (a2 - a1) % 360 > 180 else 0
    return f"M{p(r2, a1)} A{r2} {r2} 0 {big} 1 {p(r2, a2)} L{p(r1, a2)} A{r1} {r1} 0 {big} 0 {p(r1, a1)}Z"


def blob(d: Drawing, role, circles, spot=False, shadow=True):
    """A cloud made of overlapping circles, with one clean outline in line style."""
    p = " ".join(circle(x, y, r) for x, y, r in circles)
    if d.paper:
        d.shape(role, p, shadow=shadow)
    else:
        fill = d.c["spot"] if spot else d.c["paper"]
        d.raw("", f'<path d="{p}" fill="none" stroke="{d.c["ink"]}" stroke-width="6.4"/><path d="{p}" fill="{fill}"/>')


def person(x, feet, h=30.0) -> str:
    r = h * .14
    hy = feet - h + r
    sw = h * .2
    top = hy + r + h * .05
    body = (f"M{x - sw:g} {feet:g} V{top + sw * .8:g} Q{x - sw:g} {top:g} {x:g} {top:g} "
            f"Q{x + sw:g} {top:g} {x + sw:g} {top + sw * .8:g} V{feet:g}Z")
    return body + " " + circle(x, hy, r)


def scallop_skirt(x0, x1, top, bottom, n, depth=5):
    """A box whose bottom edge is scalloped (bunting skirts, valances)."""
    w = (x1 - x0) / n
    s = f"M{x0:g} {top:g} H{x1:g} V{bottom:g}"
    for i in range(n, 0, -1):
        s += f" Q{x0 + w * (i - .5):.1f} {bottom + depth * 2:.1f} {x0 + w * (i - 1):.1f} {bottom:g}"
    return s + "Z"


def flag_string(d: Drawing, x0, y0, x1, y1, sag, n, roles, size=4.0):
    cx, cy = (x0 + x1) / 2, max(y0, y1) + sag
    d.stroke("dark", f"M{x0} {y0} Q{cx} {cy} {x1} {y1}", 1.3)
    for i in range(1, n + 1):
        t = i / (n + 1)
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1
        d.shape(roles[i % len(roles)], f"M{x - size:.1f} {y:.1f} L{x + size:.1f} {y:.1f} L{x:.1f} {y + size * 2.1:.1f}Z",
                shadow=False, spot=i % 2 == 0)


def bulbs(d: Drawing, x0, y0, x1, y1, sag, n, role="glow2", r=2.6):
    cx, cy = (x0 + x1) / 2, max(y0, y1) + sag
    d.stroke("dark", f"M{x0} {y0} Q{cx} {cy} {x1} {y1}", 1.3)
    for i in range(1, n + 1):
        t = i / (n + 1)
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1
        d.shape(role, circle(round(x, 1), round(y + r, 1), r), shadow=False, spot=True)


def confetti(d: Drawing, pts, roles=("pop", "hero2", "hero", "light")):
    for i, (x, y, a) in enumerate(pts):
        d.shape(roles[i % len(roles)], rrect(x - 3, y - 1.5, 6, 3, 1), shadow=False, line=False, extra=f'transform="rotate({a} {x} {y})"')


def leaf(d: Drawing, x, y, length, width, angle, role="leaf", spot=False, shadow=True):
    L, w = length, width
    group(d, f"translate({x} {y}) rotate({angle})",
          lambda: d.shape(role, f"M0 0 C{L * .3:.1f} {-w} {L * .7:.1f} {-w} {L} 0 C{L * .7:.1f} {w} {L * .3:.1f} {w} 0 0Z", spot=spot, shadow=shadow))


def flame(x, base, w, h):
    return (f"M{x} {base - h} C{x + w * .2} {base - h * .7} {x + w} {base - h * .5} {x + w * .8} {base - h * .18} "
            f"C{x + w * .7} {base} {x - w * .7} {base} {x - w * .8} {base - h * .18} "
            f"C{x - w} {base - h * .45} {x - w * .1} {base - h * .55} {x} {base - h}Z")


# ================================================================ PARADE
def parade_float(d: Drawing):
    d.disc("glow", 154, 56, 15)
    d.band("far", "M-30 122 H14 V88 L28 76 L42 88 V104 H58 V80 H80 V98 L92 88 L104 98 V72 H128 V96 H146 V82 L160 70 L174 82 V100 H190 V88 H230")
    for x, y in [(22, 94), (32, 94), (64, 88), (72, 88), (110, 80), (118, 80), (154, 88), (164, 88), (180, 106)]:
        d.marks("light", rrect(x, y, 4, 6, .8))
    flag_string(d, -6, 26, 206, 26, 22, 12, ["pop", "hero2", "hero", "light"], 4.2)
    # balloons tied to the float
    for x, y, role in [(48, 84, "pop"), (152, 80, "hero2")]:
        d.stroke("dark", f"M{x} {y + 12} Q{x + (100 - x) * .2} {y + 30} {x + (100 - x) * .25} 124", 1.2)
        d.shape(role, ellipse(x, y, 10, 12), spot=role == "pop")
        d.shape(role, f"M{x - 2.5} {y + 14} L{x + 2.5} {y + 14} L{x} {y + 11}Z", shadow=False)
        d.shape("light", ellipse(x - 3.5, y - 4, 2.4, 3.6), shadow=False, line=False)
    # giant flower on the float
    d.limb("leaf", "M100 124 V84", 5)
    leaf(d, 100, 112, 22, 7, -30)
    leaf(d, 100, 104, 22, 7, 210)
    for i in range(8):
        a = i * 45
        cx, cy = 100 + 14 * math.cos(math.radians(a)), 66 + 14 * math.sin(math.radians(a))
        d.shape("pop", ellipse(round(cx, 1), round(cy, 1), 11, 7), extra=f'transform="rotate({a} {cx:.1f} {cy:.1f})"', spot=True)
    d.shape("hero2", circle(100, 66, 8))
    d.marks("dark", circle(97, 64, 1.4) + circle(103, 64, 1.4))
    d.stroke("dark", "M96 69 Q100 72 104 69", 1.3)
    # the float
    for x in (60, 140):
        d.shape("dark", circle(x, 154, 9))
        d.shape("light", circle(x, 154, 3.4), shadow=False)
    d.shape("hero", scallop_skirt(30, 170, 132, 148, 8, 4))
    d.shape("hero2", rrect(26, 122, 148, 12, 4), spot=True)
    for x in range(36, 170, 16):
        d.shape("light" if (x // 16) % 2 else "pop", circle(x, 128, 3.2), shadow=False, line=False)
    confetti(d, [(30, 60, 30), (70, 46, -20), (130, 50, 50), (176, 120, -40), (24, 112, 70), (88, 104, 10), (126, 100, -30)])
    d.band("ground", "M-30 163 H230")
    d.band("deep", hills(186, 3), line=False)


def parade_drum(d: Drawing):
    d.disc("glow", 100, 100, 62)
    d.stroke("pop", "M22 70 C34 60 30 46 44 38 M156 36 C170 44 166 58 180 66", 3)
    d.stroke("hero2", "M26 128 C36 120 30 108 40 100 M162 104 C172 112 168 124 178 130", 3)
    confetti(d, [(36, 84, 30), (166, 86, -30), (60, 34, 20), (142, 30, -50), (30, 150, 60), (170, 150, -10)])
    d.shape("hero", "M44 76 V142 A56 14 0 0 0 156 142 V76Z", spot=True)
    # zig-zag tension cords
    zz = "M48 90"
    for i in range(1, 9):
        zz += f" L{48 + i * 13} {90 if i % 2 == 0 else 136}"
    d.stroke("light", zz, 2.4)
    d.shape("hero2", "M44 132 V144 A56 14 0 0 0 156 144 V132 A56 14 0 0 1 44 132Z", shadow=False)
    d.shape("hero2", "M44 76 V88 A56 14 0 0 0 156 88 V76Z", shadow=False)
    d.shape("light", ellipse(100, 76, 56, 14))
    d.stroke("hero2", ellipse(100, 76, 56, 14), 2.4)
    for x, y in [(52, 91), (76, 95), (100, 96), (124, 95), (148, 91)]:
        d.marks("dark", rrect(x - 2, y - 3, 4, 6, 1))
    # crossed sticks resting on the head
    for x0, x1 in [(40, 118), (160, 82)]:
        d.limb("wood", f"M{x0} 26 L{x1} 72", 5)
        d.shape("light", circle(x1 + (6 if x1 > 100 else -6) * .5, 74, 5.5), line=True)


def parade_balloon(d: Drawing):
    d.shape("light", cloud(26, 52, 1.1))
    d.shape("light", cloud(140, 30, .9))
    # streets either side
    d.shape("near", "M-10 82 H40 V200 H-10Z")
    d.shape("mid", "M160 96 H210 V200 H160Z")
    for y in (92, 112, 132):
        d.shape("light", rrect(16, y, 10, 12, 1), shadow=False, line=False)
        d.shape("light", rrect(170, y + 12, 10, 12, 1), shadow=False, line=False)
    flag_string(d, 40, 86, 160, 100, 14, 8, ["pop", "hero2", "light"], 3.4)
    # ropes to the handlers
    d.stroke("dark", "M80 112 L52 160 M90 130 L80 164 M110 130 L122 164 M120 112 L148 160", 1.4)
    # inflatable bear
    for x in (78, 122):
        d.shape("hero", circle(x, 38, 10))
        d.shape("hero2", circle(x, 38, 5), shadow=False)
    d.shape("hero", ellipse(74, 96, 8, 14), extra='transform="rotate(30 74 96)"')
    d.shape("hero", ellipse(126, 96, 8, 14), extra='transform="rotate(-30 126 96)"')
    d.shape("hero", ellipse(86, 126, 10, 8))
    d.shape("hero", ellipse(114, 126, 10, 8))
    d.shape("hero", ellipse(100, 106, 25, 22), spot=True)
    d.shape("hero2", ellipse(100, 110, 14, 13), shadow=False)
    d.shape("hero", circle(100, 60, 27), spot=True)
    d.shape("hero2", ellipse(100, 70, 12, 9), shadow=False)
    d.marks("dark", ellipse(100, 65, 4.5, 3.2) + circle(90, 55, 3) + circle(110, 55, 3))
    d.stroke("dark", "M96 73 Q100 76 104 73", 1.4)
    d.shape("light", ellipse(88, 44, 5, 3), shadow=False, line=False, extra='transform="rotate(-30 88 44)"')
    # handlers and crowd
    for x, h in [(52, 26), (80, 24), (122, 24), (148, 26)]:
        d.shape("dark", person(x, 186, h), shadow=False)
    d.band("ground", "M-30 176 H230")


# ================================================================ THEATRE
def theatre_curtains(d: Drawing):
    d.band("deep", "M-30 -30 H230", shadow=False, line=False)
    if d.paper:
        d.raw(f'<path d="M84 -10 H116 L150 156 H50Z" fill="{d.c["glow2"]}" opacity=".35"/>')
    else:
        d.raw("", f'<path d="M84 -10 L50 156 M116 -10 L150 156" stroke="{d.c["ink"]}" stroke-width="1.6" stroke-dasharray="4 5" fill="none"/>')
    d.band("wood", "M-30 156 H230")
    d.stroke("wood2", "M-10 168 H210 M-10 182 H210", 1.4, line=False)
    d.shape("glow2", ellipse(100, 157, 44, 7), shadow=False)
    # actor in the spotlight, arm out
    d.limb("dark", "M106 131 Q118 126 124 108", 5)
    d.shape("dark", person(100, 157, 46), spot=False)
    # footlights
    for x in range(10, 200, 22):
        d.shape("gold", f"M{x - 5} 160 A5 4 0 0 1 {x + 5} 160Z", shadow=False)
    for side in (1, -1):
        def curtain():
            d.shape("curtain", "M-14 10 H66 C64 50 56 82 42 100 C50 118 56 140 58 172 H-14Z")
            d.stroke("curtain2", "M10 14 C12 50 14 80 18 100 M30 14 C32 50 30 80 32 98 M48 14 C48 50 44 80 38 98 "
                                 "M20 108 C20 130 18 150 18 172 M38 108 C40 130 40 150 42 172", 2.2, line=False)
            d.shape("gold", rrect(30, 96, 18, 8, 3), extra='transform="rotate(-12 39 100)"')
        group(d, "translate(0 0)" if side == 1 else "translate(200 0) scale(-1 1)", curtain)
    d.shape("curtain", scallop_skirt(-14, 214, -10, 22, 7, 6), spot=True)
    w = 228 / 7
    fringe = "".join(f" M{-14 + w * i:.1f} 22 Q{-14 + w * (i + .5):.1f} 34 {-14 + w * (i + 1):.1f} 22" for i in range(7))
    d.stroke("gold", fringe, 3)


MASK_FACE = "M-26 -30 C-12 -38 12 -38 26 -30 C31 -6 26 18 0 34 C-26 18 -31 -6 -26 -30Z"


def theatre_masks(d: Drawing):
    d.disc("glow", 100, 100, 62)
    d.limb("pop", "M150 74 C168 92 150 112 168 134", 4)
    d.limb("pop", "M40 66 C26 84 44 104 30 124", 4)

    def tragedy():
        d.shape("hero", MASK_FACE, spot=True)
        d.marks("dark", "M-18 -10 Q-10 -18 -4 -8 Q-12 -6 -18 -10Z M18 -10 Q10 -18 4 -8 Q12 -6 18 -10Z")
        d.stroke("dark", "M-19 -20 Q-12 -24 -5 -17 M19 -20 Q12 -24 5 -17", 2)
        d.marks("dark", "M-12 20 Q0 4 12 20 Q0 13 -12 20Z")
        d.stroke("light", "M-12 -2 Q-13 4 -11 8", 1.6, line=False)
    group(d, "translate(128 104) rotate(14)", tragedy)

    def comedy():
        d.shape("gold", MASK_FACE)
        d.marks("dark", "M-18 -10 Q-11 -20 -4 -10 Q-11 -13 -18 -10Z M18 -10 Q11 -20 4 -10 Q11 -13 18 -10Z")
        d.stroke("dark", "M-19 -21 Q-12 -27 -5 -22 M19 -21 Q12 -27 5 -22", 2)
        d.marks("dark", "M-15 6 Q0 26 15 6 Q0 13 -15 6Z")
        d.shape("pop", circle(-17, 6, 4), shadow=False, line=False)
        d.shape("pop", circle(17, 6, 4), shadow=False, line=False)
    group(d, "translate(76 88) rotate(-14)", comedy)
    for x, y, r in [(156, 46, 5), (40, 150, 4), (166, 150, 3.5)]:
        d.marks("light", star(x, y, r, .4, 4, -90))


def theatre_globe(d: Drawing):
    d.disc("glow", 150, 50, 15)
    d.shape("light", cloud(22, 52, 1.0))
    d.band("far", hills(132, 10))
    for x, y in [(26, 116), (176, 112)]:
        d.limb("dark", f"M{x} {y} V150", 3)
        blob(d, "tree", [(x, y, 13), (x - 6, y + 8, 9), (x + 7, y + 7, 9)])
    # thatched drum of timber-framed walls
    d.shape("light", "M30 102 L56 94 H144 L170 102 V160 H30Z")
    d.stroke("wood2", "M30 102 V160 M56 94 V160 M78 94 V160 M100 94 V160 M122 94 V160 M144 94 V160 M170 102 V160 "
                      "M30 122 L56 118 H144 L170 122 M30 142 L56 140 H144 L170 142 "
                      "M56 94 L78 118 M100 94 L78 118 M100 94 L122 118 M144 94 L122 118 "
                      "M30 122 L56 140 M144 140 L170 122", 2.4)
    d.shape("wood2", "M90 160 V146 Q100 136 110 146 V160Z", shadow=False)
    d.shape("thatch", "M20 106 L50 80 H150 L180 106 L170 110 L146 94 H54 L30 110Z")
    d.stroke("thatch2", "M40 98 L46 92 M62 90 L66 86 M86 90 L88 86 M112 90 L114 86 M136 90 L138 86 M156 96 L160 92", 1.6, line=False)
    d.stroke("dark", "M100 84 V44", 2)
    d.shape("pop", "M100 44 L122 49 L100 56Z", spot=True)
    d.band("near", hills(160, 3))
    d.band("deep", hills(182, 3, 20), line=False)


# ================================================================ OPERA
def sail(xb, xf, tx, ty, base=124):
    return (f"M{xb} {base} C{xb} {base - (base - ty) * .7:.1f} {tx + (xb - tx) * .55:.1f} {ty} {tx} {ty} "
            f"Q{xf + 2} {ty + (base - ty) * .45:.1f} {xf} {base}Z")


def opera_house(d: Drawing):
    d.disc("glow", 46, 60, 14)
    d.shape("light", cloud(130, 40, .9), shadow=False)
    # harbour bridge, far left
    d.stroke("far", "M-30 112 H48 M-24 112 Q12 74 48 112", 3)
    d.stroke("far", "M-14 112 V100 M0 112 V90 M14 112 V88 M28 112 V94 M40 112 V104", 1.4, line=False)
    d.band("mid", waves(134, 3, 26))
    d.shape("stone", "M36 124 H182 L178 138 H40Z")
    for xb, xf, tx, ty in [(184, 150, 144, 88), (160, 116, 106, 58), (126, 84, 74, 72), (94, 62, 52, 96)]:
        d.shape("light", sail(xb, xf, tx, ty))
        mid = (xb + xf) / 2
        d.stroke("stone2", f"M{tx + 6} {ty + 4} Q{mid} {ty + 14} {mid + 4} 124 M{tx + 3} {ty + 2} Q{xf + 6} {ty + 20} {xf + 8} 124", 1.2, line=False)
        d.shape("stone", f"M{xf} 124 Q{xf + 2} {124 - (124 - ty) * .25:.1f} {xf + 8} {124 - (124 - ty) * .3:.1f} L{xf + 10} 124Z", shadow=False)
    d.band("near", waves(150, 4, 30))
    d.stroke("light", "M60 160 h18 M120 158 h14 M150 168 h12", 2)
    d.band("deep", waves(172, 4, 34), line=False)


def opera_glasses(d: Drawing):
    d.disc("glow", 100, 96, 60)
    notes(d, [(40, 52, 1.1), (160, 44, 1.0), (168, 142, .9)])
    d.limb("gold", "M144 112 L160 156", 7, spot=True)
    d.shape("gold2", circle(161, 158, 5))
    # rose
    d.limb("leaf", "M54 150 Q86 146 122 132", 3)
    leaf(d, 80, 147, 16, 6, -40)
    leaf(d, 98, 141, 15, 5, 30)
    d.shape("pop", "M42 140 C40 130 50 124 58 128 C66 126 72 134 68 142 C66 152 54 158 46 154 C40 150 40 146 42 140Z", spot=True)
    d.stroke("dark", "M56 134 Q50 136 52 142 Q56 146 60 140", 1.6)
    d.shape("pop", "M44 148 Q52 152 60 146 Q56 156 48 156Z", shadow=False)
    # lorgnette
    d.shape("gold2", rrect(90, 80, 20, 20, 4))
    for cx in (72, 128):
        d.shape("gold", circle(cx, 90, 26))
        d.shape("gold2", circle(cx, 90, 20.5), shadow=False)
        d.shape("dark", circle(cx, 90, 16), shadow=False)
        d.shape("light", annulus(cx, 90, 9, 12, 200, 260), shadow=False)
    d.shape("gold", rrect(94, 72, 12, 8, 3))


def opera_diva(d: Drawing):
    d.band("deep", "M-30 -30 H230", shadow=False, line=False)
    d.disc("glow", 100, 84, 50)
    d.band("wood", "M-30 156 H230")
    for side in ("translate(0 0)", "translate(200 0) scale(-1 1)"):
        group(d, side, lambda: d.shape("curtain", "M-14 -10 H44 C40 40 30 70 22 92 C28 110 30 140 32 172 H-14Z"))
    # diva, arms open
    d.limb("dark", "M90 82 Q74 70 64 52", 5)
    d.limb("dark", "M110 82 Q126 70 136 52", 5)
    d.shape("dark", circle(63, 50, 4))
    d.shape("dark", circle(137, 50, 4))
    d.shape("hero", "M88 100 C82 122 68 142 50 160 Q100 168 150 160 C132 142 118 122 112 100Z", spot=True)
    d.shape("hero", "M88 78 Q100 74 112 78 L113 102 H87Z")
    d.shape("hero2", rrect(86, 98, 28, 5, 2), shadow=False)
    d.shape("dark", rrect(96, 66, 8, 10, 2))
    d.shape("dark", circle(100, 60, 10))
    d.shape("dark", circle(106, 48, 6))
    d.marks("glow", ellipse(100, 64, 2.4, 3))
    d.stroke("light", "M93 80 Q100 86 107 80", 1.4, line=False)
    notes(d, [(146, 32, 1), (160, 74, .8), (40, 70, .9)], "light")


# ================================================================ LIVE MUSIC
def livemusic_sax(d: Drawing):
    d.disc("glow", 100, 100, 60)
    notes(d, [(36, 70, 1.2), (44, 128, .9), (160, 46, 1.0)])

    def sax():
        d.limb("gold", "M74 38 Q86 32 96 46", 6)
        d.shape("dark", rrect(64, 32, 14, 7, 3), extra='transform="rotate(-20 71 35)"')
        d.limb("gold", "M102 120 Q104 156 124 154 Q142 152 142 128", 18)
        d.shape("gold", "M91 44 L104 44 L111 126 L93 126Z", spot=True)
        d.shape("gold", "M131 134 C131 120 128 110 125 100 L163 100 C157 110 153 120 153 134Z", spot=True)
        d.shape("gold2", ellipse(144, 100, 19, 6), shadow=False)
        d.shape("dark", ellipse(144, 100, 14, 3.6), shadow=False)
        d.stroke("gold2", "M106 52 L112 120", 2)
        for x, y in [(98, 62), (99, 78), (100, 94), (101, 110), (134, 120)]:
            d.shape("light", circle(x, y, 4), shadow=False)
            d.marks("gold2", circle(x, y, 1.8))
        d.stroke("gold2", "M104 140 Q112 150 126 146", 1.6, line=False)
    group(d, "rotate(16 100 100) translate(4 4)", sax)


def livemusic_mic(d: Drawing):
    d.band("far", "M-30 -30 H230", shadow=False, line=False)
    bricks = ""
    for i, y in enumerate(range(10, 200, 14)):
        bricks += f" M-10 {y} H210"
        off = 0 if i % 2 else 14
        for x in range(-10 + off, 210, 28):
            bricks += f" M{x} {y} V{y + 14}"
    d.stroke("mid", bricks, 1.2, line=False)
    if d.paper:
        d.raw(f'<path d="M86 -10 H114 L150 170 H50Z" fill="{d.c["glow2"]}" opacity=".35"/>')
    d.disc("glow", 100, 74, 44)
    for x, y, r in [(30, 50, 4), (168, 64, 5), (40, 120, 3), (160, 128, 3.5)]:
        d.disc("glow2", x, y, r, shadow=False, line=False)
    d.limb("dark", "M100 120 V164", 5)
    d.shape("dark", ellipse(100, 168, 28, 7))
    d.stroke("dark", "M70 76 Q70 122 100 122 Q130 122 130 76", 4.2)
    d.shape("chrome", rrect(78, 32, 44, 80, 22), spot=True)
    d.stroke("chrome2", " ".join(f"M{80 if y > 44 and y < 100 else 86} {y} H{120 if y > 44 and y < 100 else 114}" for y in range(42, 108, 6)), 1.4, line=False)
    d.shape("gold", rrect(75, 68, 50, 10, 4))
    d.shape("light", rrect(84, 38, 6, 24, 3), shadow=False, line=False)
    d.shape("dark", circle(70, 76, 4))
    d.shape("dark", circle(130, 76, 4))
    notes(d, [(32, 92, 1.1), (166, 100, 1.0)], "light")


def livemusic_drums(d: Drawing):
    d.band("far", "M-30 -30 H230", shadow=False, line=False)
    bulbs(d, -6, 30, 206, 30, 18, 9)
    d.band("mid", "M-30 150 H230")
    d.band("deep", "M-30 172 H230", line=False)
    # cymbal stands
    d.stroke("dark", "M38 76 V150 M30 150 L38 136 L46 150 M164 66 V150 M156 150 L164 136 L172 150", 2)
    d.shape("gold", ellipse(38, 76, 24, 5), extra='transform="rotate(-10 38 76)"')
    d.shape("gold", ellipse(164, 66, 24, 5), extra='transform="rotate(12 164 66)"')
    # toms
    for x, a in [(76, -10), (124, 10)]:
        def tom(x=x):
            d.shape("hero", rrect(x - 16, 78, 32, 22, 4), spot=True)
            d.shape("light", ellipse(x, 78, 16, 5))
        group(d, f"rotate({a} {x} 90)", tom)
    # snare and floor tom
    d.stroke("dark", "M44 124 L36 150 M44 124 L52 150 M152 132 V152 M174 132 V152", 2)
    d.shape("hero", rrect(28, 108, 32, 16, 3))
    d.shape("light", ellipse(44, 108, 16, 4.5))
    d.shape("hero", rrect(146, 104, 34, 34, 4))
    d.shape("light", ellipse(163, 104, 17, 5))
    # bass drum
    d.shape("hero", circle(100, 124, 36), spot=True)
    d.shape("light", circle(100, 124, 29))
    d.shape("pop", star(100, 125, 13, .45))
    for a in range(0, 360, 45):
        d.marks("dark", circle(round(100 + 32.5 * math.cos(math.radians(a)), 1), round(124 + 32.5 * math.sin(math.radians(a)), 1), 1.6))
    d.stroke("dark", "M72 154 L66 162 M128 154 L134 162", 3)


# ================================================================ CULTURAL DANCE SHOW
def dance_flamenco(d: Drawing):
    d.disc("glow", 100, 92, 60)
    d.band("ground", "M-30 168 H230")
    # skirt flaring to the left
    skirt = "M90 92 H108 C116 114 136 134 150 158 Q126 170 100 164 Q78 172 56 162 Q38 154 30 136 C52 124 76 110 90 92Z"
    d.shape("pop", skirt, spot=True)
    d.shape("light", "M30 136 Q38 154 56 162 Q78 172 100 164 Q126 170 150 158 L146 152 Q124 162 100 156 Q78 164 58 154 Q42 148 36 132Z", shadow=False)
    d.shape("pop", "M40 128 Q52 140 70 144 Q90 150 110 142 Q130 148 142 144 L138 138 Q120 142 106 136 Q88 142 72 136 Q56 132 46 124Z", shadow=False, line=False)
    for x, y in [(70, 118), (84, 128), (100, 120), (112, 134), (60, 134), (126, 146), (96, 146), (80, 110)]:
        d.marks("light", circle(x, y, 2.2))
    d.shape("dark", ellipse(96, 168, 6, 2.6))
    d.shape("dark", ellipse(110, 167, 6, 2.6))
    # torso and arms
    d.limb("dark", "M92 64 Q76 78 64 96", 4.4)
    d.limb("dark", "M104 62 Q122 52 118 32 Q114 24 104 26", 4.4)
    d.shape("pop", "M90 62 Q98 56 106 62 L109 94 H89Z")
    d.stroke("light", "M90 66 Q98 74 106 66", 1.6, line=False)
    d.shape("dark", rrect(94, 52, 7, 9, 2))
    d.shape("dark", circle(96, 46, 9.5))
    d.shape("dark", circle(104, 41, 5.5))
    d.shape("hero2", circle(103, 35, 4), shadow=False)
    d.marks("glow", circle(88, 47, 1.6))


def dance_dervish(d: Drawing):
    d.disc("glow", 100, 70, 26)
    d.shape("far", "M44 176 V86 Q44 46 100 26 Q156 46 156 86 V176Z")
    d.band("ground", "M-30 160 H230")
    d.stroke("dark", "M32 120 Q22 140 40 158 M168 120 Q178 140 160 158", 2.2)
    # whirling white skirt
    d.shape("light", "M92 94 C80 118 60 138 40 152 Q70 166 100 164 Q130 166 160 152 C140 138 120 118 108 94Z")
    d.stroke("sky2", "M96 100 L64 156 M100 100 L86 162 M104 100 L114 162 M106 100 L138 156", 1.6, line=True)
    d.shape("light", "M40 152 Q70 166 100 164 Q130 166 160 152 L160 156 Q130 172 100 170 Q70 172 40 156Z", shadow=False)
    # arms: right palm up, left palm down
    d.limb("light", "M108 70 Q124 58 132 38", 6)
    d.limb("light", "M92 70 Q76 80 62 90", 6)
    d.shape("dark", ellipse(134, 34, 4, 3))
    d.shape("dark", ellipse(59, 92, 4, 3))
    d.shape("light", "M89 66 Q100 60 111 66 L110 98 H90Z")
    d.shape("dark", rrect(89, 92, 22, 5, 2), shadow=False)
    d.shape("dark", circle(104, 54, 8.5))
    d.shape("hat", rrect(99, 24, 12, 26, 6), extra='transform="rotate(16 105 44)"')


def dance_kecak(d: Drawing):
    d.disc("glow", 100, 100, 46)
    d.band("far", hills(150, 6))
    # split temple gate (candi bentar)
    for side in ("translate(0 0)", "translate(200 0) scale(-1 1)"):
        group(d, side, lambda: d.shape("near", poly((50, 150), (50, 104), (56, 104), (56, 90), (62, 90), (62, 76), (68, 76), (68, 62), (74, 62),
                                                     (74, 48), (80, 48), (80, 36), (86, 30), (86, 150))))
    # torch and fire
    d.limb("dark", "M100 160 V112", 4)
    d.shape("dark", rrect(92, 106, 16, 8, 2))
    d.shape("pop", flame(100, 108, 16, 44), spot=True)
    d.shape("glow2", flame(100, 108, 8, 24), shadow=False)
    # ring of chanting dancers, arms raised
    for x, y in [(30, 150), (56, 158), (144, 158), (170, 150)]:
        d.limb("dark", f"M{x - 5} {y + 6} L{x - 14} {y - 16} M{x + 5} {y + 6} L{x + 14} {y - 16}", 4, shadow=False)
    heads = [(30, 150), (56, 158), (82, 164), (118, 164), (144, 158), (170, 150)]
    p = "M-30 230 V172"
    for x, y in heads:
        p += f" L{x - 13} {y + 22} Q{x - 13} {y + 11} {x - 5} {y + 9} A7.5 7.5 0 1 1 {x + 5} {y + 9} Q{x + 13} {y + 11} {x + 13} {y + 22}"
    d.shape("dark", p + " L230 172 V230Z")


# ================================================================ TEA CEREMONY
def tea_matcha(d: Drawing):
    d.disc("glow", 100, 96, 62)
    d.band("tatami", "M-30 150 H230")
    d.stroke("tatami2", "M-10 162 H210 M-10 176 H210", 1.4, line=False)
    d.stroke("light", "M74 82 C68 72 80 66 74 56 M92 78 C86 66 98 60 92 48", 2.6)
    # bowl
    d.shape("bowl", rrect(66, 146, 36, 9, 3))
    d.shape("bowl", "M38 106 Q40 150 84 152 Q128 150 130 106Z", spot=True)
    d.shape("bowl2", "M38 106 Q39 116 42 122 Q50 116 56 124 Q64 114 72 122 Q80 112 90 122 Q100 114 108 122 Q116 114 124 122 Q128 116 130 106Z", shadow=False, line=False)
    d.shape("matcha", ellipse(84, 106, 46, 10), shadow=False)
    d.shape("foam", ellipse(80, 105, 24, 5), shadow=False, line=False)
    d.stroke("matcha", "M70 105 Q80 101 90 105", 1.2, line=False)
    # whisk
    d.shape("bamboo", "M140 108 H164 L174 150 Q152 158 130 150Z")
    d.stroke("bamboo2", "M144 112 L138 150 M149 112 L146 152 M154 112 L154 153 M159 112 L162 152 M163 112 L170 150", 1.4)
    d.shape("bamboo2", rrect(140, 104, 24, 8, 3), shadow=False)
    d.shape("bamboo", rrect(145, 66, 14, 40, 4))
    d.stroke("bamboo2", "M152 70 V102", 1.2, line=False)
    # scoop
    d.limb("bamboo", "M44 168 Q90 162 132 168", 4)
    d.shape("bamboo", ellipse(138, 168, 8, 4.5))


def tea_house(d: Drawing):
    d.disc("glow", 152, 50, 14)
    d.band("far", hills(120, 10))
    # maple
    d.limb("dark", "M40 154 Q36 126 44 104 M42 120 L28 104 M44 110 L58 98", 5)
    blob(d, "maple", [(38, 86, 15), (56, 84, 12), (24, 98, 11), (48, 100, 12), (64, 98, 9), (30, 76, 9)], spot=True)
    for x, y in [(32, 80), (52, 80), (28, 96)]:
        d.shape("maple2", circle(x, y, 4), shadow=False, line=False)
    # tea house
    d.shape("wood", rrect(66, 96, 82, 58, 1))
    d.shape("light", rrect(72, 102, 34, 46, 1), shadow=False)
    d.stroke("wood", "M83 102 V148 M94 102 V148 M72 117 H106 M72 132 H106", 1.4)
    d.shape("light", circle(128, 120, 12), shadow=False)
    d.stroke("wood", "M128 108 V132 M116 120 H140", 1.4)
    d.shape("roof", "M54 100 Q70 98 80 74 H134 Q144 98 160 100 L162 104 H52Z")
    d.shape("roof2", rrect(78, 70, 58, 6, 2))
    d.shape("dark", rrect(70, 152, 74, 6, 1))
    # stone lantern
    d.shape("stone", rrect(166, 128, 6, 26, 1))
    d.shape("stone", rrect(160, 118, 18, 12, 2))
    d.shape("glow2", rrect(164, 121, 10, 6, 1), shadow=False)
    d.shape("stone", "M156 120 L169 106 L182 120Z")
    d.band("near", hills(156, 3))
    for x, y in [(96, 164), (110, 174), (92, 184)]:
        d.shape("stone", ellipse(x, y, 9, 3.5))


def tea_mint(d: Drawing):
    d.disc("glow", 104, 104, 60)
    # teapot, held high by its handle
    d.limb("pot2", "M48 62 Q30 74 48 92", 5)
    d.limb("pot", "M86 82 Q100 76 108 58", 6)
    d.shape("pot", "M50 62 C40 74 44 98 70 100 C96 98 100 74 90 62Z", spot=True)
    d.shape("pot2", "M52 68 C50 76 52 84 58 90 Q70 84 82 90 C88 84 90 76 88 68Z", shadow=False, line=False)
    d.shape("pot", "M54 62 Q56 48 70 46 Q84 48 86 62Z")
    d.shape("pot2", rrect(52, 60, 36, 4, 2), shadow=False)
    d.shape("pot2", circle(70, 42, 3.5))
    d.limb("hero", "M-14 78 L28 76", 16, spot=True)
    d.shape("dark", "M26 70 C32 64 42 66 42 74 C42 82 34 86 26 82Z")
    # tea stream
    d.stroke("tea", "M109 57 Q126 60 129 124", 3.4)
    # glass on a tray
    d.shape("brass", ellipse(110, 160, 58, 10))
    d.shape("brass2", ellipse(110, 158, 50, 7), shadow=False, line=False)
    d.shape("light", "M110 116 H148 L143 158 H115Z")
    d.shape("tea", "M112 132 H146 L143 158 H115Z", shadow=False)
    d.stroke("brass", "M111 125 H147", 2.8)
    leaf(d, 140, 122, 14, 4.5, -60, "leaf", shadow=False)
    leaf(d, 142, 122, 12, 4, -20, "leaf", shadow=False)
    d.shape("light", "M72 140 H92 L90 156 H74Z")
    d.shape("tea", "M73 146 H91 L90 156 H74Z", shadow=False)
    d.stroke("brass", "M73 144 H91", 2)


# ================================================================ CALLIGRAPHY CLASS
def leaf_path(x, y, L, w, ang):
    c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    P = lambda u, v: f"{x + u * c - v * s_:.1f} {y + u * s_ + v * c:.1f}"
    return f"M{P(0, 0)} C{P(L * .3, -w)} {P(L * .7, -w * .6)} {P(L, 0)} C{P(L * .7, w * .4)} {P(L * .3, w)} {P(0, 0)}Z"


def bamboo_painting(d: Drawing):
    """Sumi-e bamboo: ink stalks with nodes and slender leaves."""
    p = ""
    for x0, segs, w in [(96, [(140, 118), (115, 94), (91, 70), (67, 46)], 7), (122, [(140, 122), (119, 100), (97, 80)], 5)]:
        for i, (y1, y0) in enumerate(segs):
            x = x0 + i * 1.5
            p += f" M{x - w / 2:.1f} {y1} L{x - w / 2 + .8:.1f} {y0 + 1} Q{x:.1f} {y0 - 1} {x + w / 2 + .8:.1f} {y0 + 1} L{x + w / 2:.1f} {y1}Z"
    for x, y, L, w, a in [(100, 70, 30, 5, -35), (100, 70, 26, 4.5, -10), (101, 47, 24, 4, -60), (98, 94, 28, 5, 200), (98, 94, 24, 4, 170),
                          (124, 98, 26, 4.5, -30), (124, 98, 22, 4, 5), (95, 118, 22, 4, 210)]:
        p += " " + leaf_path(x, y, L, w, a)
    d.marks("ink", p)


def calligraphy_inkstone(d: Drawing):
    d.band("wood", "M-30 -30 H230", shadow=False, line=False)
    d.stroke("wood2", "M-10 40 Q60 34 210 46 M-10 100 Q90 94 210 104 M-10 170 Q100 164 210 176", 1.4, line=False)
    # paper with a bold stroke and seal
    def paper():
        d.shape("light", rrect(64, 26, 92, 122, 2))
        bamboo_painting(d)
        d.shape("pop", rrect(136, 124, 11, 11, 1.5), shadow=False, spot=True)
        d.shape("light", rrect(139, 127, 2, 5, .3) + rrect(143, 127, 2, 5, .3), shadow=False, line=False)
    group(d, "rotate(6 110 86)", paper)
    # ink stone with ink stick
    d.shape("ink2", rrect(20, 106, 42, 64, 8))
    d.shape("ink", rrect(25, 113, 32, 50, 6), shadow=False)
    d.shape("ink3", ellipse(41, 124, 11, 6), shadow=False)
    d.shape("ink2", rrect(40, 136, 10, 40, 2), extra='transform="rotate(-24 45 156)"')
    d.shape("gold", rrect(41, 146, 8, 4, 1), shadow=False, extra='transform="rotate(-24 45 156)"')
    # brush
    d.limb("bamboo", "M176 178 L120 124", 7)
    d.stroke("bamboo2", "M164 166 L160 162 M152 154 L148 150", 2, line=False)
    d.shape("dark", "M124 128 C114 120 104 108 100 102 C108 104 120 112 128 120Z", spot=False)
    d.shape("pop", rrect(118, 118, 10, 6, 2), extra='transform="rotate(45 123 121)"', spot=True)


def calligraphy_scroll(d: Drawing):
    d.band("sky2", "M-30 -30 H230", shadow=False, line=False)
    d.shape("wood", rrect(16, -10, 12, 170, 1))
    d.shape("wood", rrect(172, -10, 12, 170, 1))
    d.shape("wood2", rrect(10, 156, 180, 12, 2))
    d.band("near", "M-30 168 H230")
    # hanging scroll
    d.stroke("dark", "M100 16 L80 32 M100 16 L120 32", 1.4)
    d.marks("dark", circle(100, 16, 2.2))
    d.shape("hero", rrect(70, 32, 60, 116, 1), spot=True)
    d.shape("light", rrect(76, 44, 48, 92, 1), shadow=False)
    d.shape("dark", rrect(66, 30, 68, 5, 2))
    d.marks("ink", annulus(100, 84, 13, 20, 210, 495))
    d.marks("ink", annulus(100, 84, 14, 18, 190, 212))
    d.shape("pop", rrect(110, 116, 8, 8, 1), shadow=False)
    d.shape("dark", rrect(64, 146, 72, 6, 2))
    d.shape("dark", circle(63, 149, 4))
    d.shape("dark", circle(137, 149, 4))
    # ikebana
    d.limb("dark", "M152 140 Q150 120 160 104 M152 130 Q142 118 140 108", 2)
    d.shape("pop", circle(160, 102, 5))
    d.shape("pop", circle(140, 106, 4))
    leaf(d, 152, 128, 12, 4, -30, "leaf")
    d.shape("bowl", "M142 140 H164 L160 156 H146Z")


def calligraphy_quill(d: Drawing):
    d.disc("glow", 100, 100, 62)
    def parchment():
        d.shape("parch", rrect(34, 92, 100, 76, 3))
        d.stroke("ink", "M46 140 C54 116 76 112 80 128 C84 144 62 148 64 132 C66 116 96 108 104 124 C110 136 100 150 92 140 "
                        "C86 130 104 122 122 128", 2.4)
        d.stroke("ink", "M48 156 Q78 150 118 156", 1.6)
    group(d, "rotate(-8 84 130)", parchment)
    # ink well
    d.shape("glass", rrect(122, 126, 46, 38, 10), spot=True)
    d.shape("ink", rrect(126, 140, 38, 20, 6), shadow=False, line=False)
    d.shape("glass", rrect(134, 114, 22, 14, 3))
    d.shape("gold", rrect(130, 110, 30, 7, 3))
    d.shape("light", rrect(128, 132, 5, 18, 2.5), shadow=False, line=False)
    # quill in the well
    def quill():
        d.shape("light", "M0 0 C-10 -20 -14 -60 -6 -96 C4 -76 10 -40 4 -6Z M2 -8 C14 -30 18 -64 10 -90 C2 -70 -2 -36 0 -6Z")
        d.stroke("feather", "M-2 -20 L-9 -30 M-2 -34 L-10 -46 M-2 -50 L-9 -62 M-1 -64 L-6 -76 M2 -22 L10 -32 M2 -40 L12 -52 M2 -58 L10 -70", 1.2, line=False)
        d.stroke("dark", "M0 10 L2 -86", 1.6)
    group(d, "translate(142 116) rotate(-28)", quill)


# ================================================================ POTTERY CLASS
def pottery_wheel(d: Drawing):
    d.disc("glow", 100, 92, 60)
    d.shape("dark", rrect(48, 152, 104, 20, 4))
    d.shape("tray", "M28 138 H172 L164 158 H36Z", spot=True)
    d.shape("metal", ellipse(100, 136, 52, 9))
    d.stroke("light", "M30 116 Q24 126 30 136 M170 116 Q176 126 170 136", 2)
    # pot being thrown
    d.shape("clay", "M74 134 C68 116 70 100 82 92 C88 88 86 80 82 74 H118 C114 80 112 88 118 92 C130 100 132 116 126 134Z")
    d.shape("clay2", ellipse(100, 74, 18, 4), shadow=False)
    d.stroke("clay2", "M76 108 Q100 112 124 108 M74 120 Q100 124 126 120", 1.4, line=False)
    # hands
    d.limb("hero", "M-6 170 L50 120", 14)
    d.limb("hero", "M206 170 L150 120", 14)
    d.shape("skin", "M52 120 C56 108 66 100 76 102 C82 104 82 114 76 118 C70 124 60 128 52 126Z")
    d.shape("skin", "M148 120 C144 108 134 100 124 102 C118 104 118 114 124 118 C130 124 140 128 148 126Z")
    d.stroke("clay2", "M66 108 Q72 106 76 110 M134 108 Q128 106 124 110", 1.4, line=False)


def pottery_kiln(d: Drawing):
    d.disc("glow", 152, 52, 14)
    d.band("far", hills(146, 8))
    d.stroke("light", "M100 30 C92 22 108 16 100 6 M108 28 C118 20 110 12 120 4", 3)
    d.shape("kiln", rrect(88, 30, 24, 30, 2))
    d.shape("kiln", "M46 160 V112 Q48 60 100 54 Q152 60 154 112 V160Z", spot=True)
    d.stroke("kiln2", "M50 96 H150 M48 118 H152 M48 140 H152 M70 70 V96 M130 70 V96 M100 56 V96 M84 96 V118 M116 96 V118 "
                      "M64 118 V140 M136 118 V140", 1.4, line=False)
    d.shape("dark", "M76 160 V134 A24 24 0 0 1 124 134 V160Z")
    d.shape("pop", flame(92, 160, 12, 28))
    d.shape("pop", flame(108, 160, 12, 22))
    d.shape("glow2", flame(100, 160, 10, 20), shadow=False)
    d.band("near", hills(160, 3))
    for x, h, w in [(30, 22, 12), (174, 18, 10)]:
        d.shape("clay", f"M{x - w} {162} C{x - w - 4} {162 - h * .5} {x - w * .5} {162 - h * .8} {x - w * .4} {162 - h} H{x + w * .4} "
                        f"C{x + w * .5} {162 - h * .8} {x + w + 4} {162 - h * .5} {x + w} {162}Z")
    d.band("deep", hills(182, 3, 20), line=False)


def pottery_shelf(d: Drawing):
    d.disc("glow", 100, 100, 62)
    # shelf
    d.limb("wood2", "M40 140 L52 156 M160 140 L148 156", 4)
    d.shape("wood", rrect(18, 134, 164, 9, 2))
    # tall vase
    d.shape("hero", "M38 134 C30 124 30 98 42 88 C46 84 44 76 40 72 H62 C58 76 56 84 60 88 C72 98 72 124 64 134Z", spot=True)
    d.shape("hero2", "M42 88 C46 84 44 76 40 72 H62 C58 76 56 84 60 88 C64 92 67 96 68 100 Q62 96 58 104 Q54 94 48 102 Q44 94 36 100 C37 95 39 91 42 88Z", shadow=False)
    # jug
    d.limb("clay2", "M126 84 Q144 86 140 104 Q138 116 126 118", 5)
    d.shape("clay", "M78 134 C70 118 72 98 86 90 L84 72 Q100 66 116 72 L120 66 L118 90 C132 98 132 118 124 134Z")
    d.shape("clay2", ellipse(100, 72, 15, 3.5), shadow=False)
    d.stroke("light", "M80 112 Q102 118 124 112", 2.4)
    d.marks("light", circle(90, 122, 2) + circle(102, 124, 2) + circle(114, 122, 2))
    # bowl
    d.shape("pop", "M134 112 H178 Q178 134 156 134 Q134 134 134 112Z", spot=True)
    d.shape("light", ellipse(156, 112, 22, 4), shadow=False)
    # tools below
    d.limb("bamboo", "M70 170 L96 152", 4)
    d.stroke("dark", "M96 152 C104 146 106 156 100 158 C96 160 94 154 96 152", 1.6)
    d.shape("sponge", ellipse(124, 164, 12, 7))


# ================================================================ LANGUAGE CLASS
def bubble(x, y, w, h, tail_left=True):
    r = 14
    if tail_left:
        bottom = f"H{x + 30} L{x + 10} {y + h + 16} L{x + 16} {y + h} H{x + r}"
    else:
        bottom = f"H{x + w - 16} L{x + w - 10} {y + h + 16} L{x + w - 30} {y + h} H{x + r}"
    return (f"M{x + r} {y} H{x + w - r} A{r} {r} 0 0 1 {x + w} {y + r} V{y + h - r} A{r} {r} 0 0 1 {x + w - r} {y + h} "
            f"{bottom} A{r} {r} 0 0 1 {x} {y + h - r} V{y + r} A{r} {r} 0 0 1 {x + r} {y}Z")


def language_bubbles(d: Drawing):
    d.disc("glow", 100, 100, 62)
    d.shape("hero", bubble(22, 36, 94, 64, True), spot=True)
    d.shape("light", circle(69, 68, 20), shadow=False)
    d.stroke("hero", "M49 68 H89 M69 48 V88 M69 48 Q56 68 69 88 M69 48 Q82 68 69 88 M53 56 Q69 62 85 56 M53 80 Q69 74 85 80", 1.6)
    d.shape("pop", bubble(84, 98, 94, 60, False))
    d.shape("light", heart(131, 130, 1.7), shadow=False)
    for x in (40, 54, 68):
        d.shape("hero2", circle(x, 156, 5))


def flashcard(d: Drawing, x, y, ang, pic):
    def card():
        d.shape("light", rrect(-28, -38, 56, 76, 6))
        d.shape("hero", rrect(-28, -38, 56, 10, 4), shadow=False)
        d.shape("hero", rrect(-28, -32, 56, 4, 0), shadow=False, line=False)
        pic()
        d.marks("mark", rrect(-14, 24, 28, 4, 2))
    group(d, f"translate({x} {y}) rotate({ang})", card)


def language_cards(d: Drawing):
    d.disc("glow", 100, 96, 60)
    d.band("wood", "M-30 158 H230")

    def apple():
        d.shape("pop", "M0 -10 C-6 -16 -18 -14 -18 0 C-18 12 -8 20 0 16 C8 20 18 12 18 0 C18 -14 6 -16 0 -10Z", spot=True)
        d.stroke("dark", "M0 -10 Q0 -16 3 -20", 2)
        leaf(d, 2, -16, 10, 4, -20, "leaf", shadow=False)

    def house():
        d.shape("hero2", "M-16 -2 L0 -16 L16 -2Z", spot=True)
        d.shape("hero2", rrect(-12, -3, 24, 20, 1))
        d.shape("dark", rrect(-4, 6, 8, 11, 1), shadow=False)

    def cat():
        d.shape("dark", "M-14 -6 L-14 -20 L-6 -12 H6 L14 -20 L14 -6 C14 10 -14 10 -14 -6Z M-14 2 C-18 12 -8 20 0 20 C8 20 18 12 14 2Z")
        d.marks("glow2", circle(-6, -3, 2.2) + circle(6, -3, 2.2))
    flashcard(d, 58, 108, -16, apple)
    flashcard(d, 142, 108, 16, cat)
    flashcard(d, 100, 96, 0, house)
    d.limb("hero2", "M56 172 L150 166", 5)
    d.shape("dark", "M150 163 L162 166 L150 169Z")


def language_board(d: Drawing):
    d.disc("glow", 100, 100, 62)
    d.shape("wood", rrect(24, 34, 152, 98, 4))
    d.shape("board", rrect(30, 40, 140, 86, 2), shadow=False, spot=True)
    # chalk drawings
    d.stroke("chalk", "M58 74 C52 66 40 68 40 80 C40 92 50 100 58 96 C66 100 76 92 76 80 C76 68 64 66 58 74Z M58 74 Q58 66 62 62", 2)
    d.stroke("chalk", "M86 82 H110 M104 76 L110 82 L104 88", 2.2)
    d.stroke("chalk", "M122 60 H158 Q162 60 162 64 V88 Q162 92 158 92 H134 L126 100 L128 92 H122 Q118 92 118 88 V64 Q118 60 122 60Z", 2)
    d.stroke("chalk", heart(140, 78, .9), 2)
    d.shape("wood", rrect(40, 128, 120, 6, 2))
    d.shape("light", rrect(64, 124, 12, 4, 2), shadow=False)
    # desk, books and globe
    d.band("near", "M-30 156 H230")
    d.shape("hero", rrect(28, 140, 48, 10, 2))
    d.shape("pop", rrect(34, 130, 42, 10, 2))
    d.shape("hero2", rrect(30, 122, 40, 8, 2))
    d.stroke("dark", "M150 156 V146 M140 158 H160", 3)
    d.stroke("dark", "M132 106 A24 24 0 0 0 168 140", 2.4)
    d.shape("sea", circle(150, 124, 20), spot=True)
    d.shape("land", "M136 116 Q142 106 152 110 Q156 118 148 122 Q144 130 138 126Z M156 128 Q166 126 166 134 Q160 142 154 138Z", shadow=False)


# ================================================================ VOLUNTEERING
def volunteer_tree(d: Drawing):
    d.disc("glow", 140, 58, 16)
    d.shape("light", cloud(30, 56, 1.0))
    d.band("far", hills(134, 10))
    d.band("mid", hills(156, 6, 30))
    # watering can
    d.limb("hero", "M30 122 Q30 106 46 106 Q62 106 62 122", 4)
    d.limb("hero", "M66 134 L84 116", 4)
    d.shape("hero", ellipse(87, 113, 5, 3.5), extra='transform="rotate(-45 87 113)"')
    d.shape("hero", rrect(28, 120, 38, 34, 5), spot=True)
    d.shape("light", rrect(28, 128, 38, 4, 0), shadow=False, line=False)
    # spade
    d.limb("wood", "M162 90 L146 152", 4)
    d.stroke("wood", "M154 88 H170", 4)
    d.shape("metal", "M138 148 L154 152 L150 170 Q140 172 136 164Z")
    # sapling on a soil mound
    d.shape("soil", "M70 172 Q76 150 104 150 Q132 150 138 172Z")
    d.limb("dark", "M104 152 Q102 128 106 98", 3)
    for x, y, a, L in [(104, 136, 200, 20), (104, 128, -20, 22), (105, 114, 210, 18), (105, 108, -30, 18), (106, 98, -80, 14)]:
        leaf(d, x, y, L, 6, a, "leaf", spot=True)
    d.band("ground", hills(176, 3))
    d.band("deep", hills(190, 2, 20), line=False)


def volunteer_beach(d: Drawing):
    d.disc("glow", 48, 52, 16)
    d.band("far", waves(96, 3, 26))
    d.band("mid", waves(112, 3, 30))
    d.band("ground", "M-30 128 Q100 118 230 128")
    d.shape("light", "M-30 128 Q100 118 230 128 L230 132 Q100 122 -30 132Z", shadow=False, line=False)
    # rubbish bag
    d.shape("hero", "M40 172 C30 160 34 124 52 116 L60 108 L56 100 L70 104 L84 98 L80 108 L88 116 C106 124 110 160 100 172Z", spot=True)
    d.stroke("mark", "M58 108 L82 108", 2.4)
    d.stroke("mark", "M58 140 Q66 150 64 160 M86 132 Q82 146 88 158", 1.4, line=False)
    d.shape("light", rrect(76, 92, 8, 18, 3), extra='transform="rotate(20 80 100)"')
    d.shape("pop", rrect(77, 88, 6, 5, 1), extra='transform="rotate(20 80 100)"')
    # litter picker grabbing a bottle
    d.limb("dark", "M168 70 L126 154", 3.2)
    d.shape("hero2", rrect(160, 58, 14, 22, 4), extra='transform="rotate(27 167 69)"', spot=True)
    d.stroke("dark", "M126 154 L120 164 M126 154 L132 164", 2.4)
    d.shape("light", rrect(110, 160, 28, 10, 4), extra='transform="rotate(-8 124 165)"')
    d.shape("pop", rrect(136, 160, 6, 7, 1.5), extra='transform="rotate(-8 124 165)"')
    d.shape("pop", "M160 176 Q164 166 172 170 Q170 178 160 176Z")
    d.shape("light", "M22 160 Q28 152 34 160Z")


def volunteer_build(d: Drawing):
    d.disc("glow", 156, 52, 14)
    d.band("far", hills(144, 10))
    d.shape("stone", rrect(36, 150, 128, 10, 1))
    d.limb("wood", "M44 150 V100 M66 150 V100 M88 150 V100 M112 150 V100 M134 150 V100 M156 150 V100", 5)
    d.limb("wood", "M40 100 H160 M44 150 H156", 5)
    d.limb("wood", "M36 104 L100 54 L164 104 M100 54 V100 M68 79 V100 M132 79 V100", 5)
    d.limb("wood2", "M44 148 L66 102 M156 148 L134 102", 3.4)
    # ladder
    d.limb("dark", "M146 160 L170 82 M160 162 L184 84", 2.6)
    d.stroke("dark", "M152 142 L166 144 M158 122 L172 124 M164 102 L178 104", 2.2)
    d.band("ground", hills(162, 3))
    # hard hat and hammer
    d.shape("hat", "M30 172 Q32 146 56 146 Q80 146 82 172Z", spot=True)
    d.shape("hat", rrect(24, 168, 64, 6, 3))
    d.shape("light", rrect(52, 146, 8, 24, 3), shadow=False, line=False)
    d.limb("wood", "M104 180 L124 154", 5)
    d.shape("metal", rrect(114, 144, 24, 9, 2), extra='transform="rotate(-52 126 148)"')


# ================================================================ HOMESTAY
def homestay_door(d: Drawing):
    d.band("wall", "M-30 -30 H230", shadow=False, line=False)
    d.shape("roof", "M-10 -10 H210 V22 Q100 30 -10 22Z")
    d.stroke("roof2", "M-10 16 Q100 24 210 16", 2, line=False)
    # glowing doorway
    d.shape("wood", rrect(62, 50, 76, 108, 3))
    d.shape("glow2", rrect(70, 58, 60, 100, 1), shadow=False)
    d.stroke("dark", "M100 58 V72", 1.4)
    d.shape("pop", "M92 72 H108 L104 82 H96Z", shadow=False)
    d.shape("light", "M72 158 V60 L88 66 V152Z", shadow=False)
    d.shape("wood", "M120 60 L140 52 V160 L120 156Z")
    d.marks("dark", circle(125, 108, 2))
    # step and shoes
    d.shape("stone", rrect(52, 156, 96, 8, 2))
    d.band("ground", "M-30 168 H230")

    def shoe(x, y, role):
        d.shape(role, f"M{x} {y} V{y - 9} Q{x + 6} {y - 13} {x + 11} {y - 9} Q{x + 19} {y - 7} {x + 22} {y}Z", spot=role == "pop")
        d.shape("light", rrect(x, y - 2, 22, 2.5, 1), shadow=False, line=False)
    for x, role in [(34, "hero"), (46, "hero"), (80, "pop"), (92, "pop"), (126, "dark"), (138, "dark")]:
        shoe(x, 167, role)
    # plant and lantern
    d.shape("pot", "M24 136 H50 L46 166 H28Z")
    for a, L in [(-100, 26), (-130, 22), (-60, 22), (-150, 16), (-30, 16)]:
        leaf(d, 37, 136, L, 6, a, "leaf")
    d.stroke("dark", "M162 22 V44", 1.4)
    d.shape("hero2", rrect(154, 44, 16, 22, 5), spot=True)
    d.stroke("dark", "M154 52 H170 M154 58 H170", 1, line=False)


def homestay_meal(d: Drawing):
    d.disc("glow", 100, 100, 74, line=False)
    d.shape("wood", circle(100, 100, 68), spot=False)
    d.stroke("wood2", circle(100, 100, 62), 1.4, line=False)
    # shared pot in the middle
    d.shape("dark", circle(100, 100, 24))
    d.shape("stew", circle(100, 100, 19), shadow=False, spot=True)
    for x, y, r in [(94, 94, 4), (106, 98, 3.5), (98, 108, 3), (108, 108, 3.5)]:
        d.shape("hero2", circle(x, y, r), shadow=False, line=False)
    d.limb("metal", "M106 96 L134 70", 3)
    # bowls and chopsticks around
    for a in (30, 120, 210, 300):
        cx, cy = 100 + 46 * math.cos(math.radians(a)), 100 + 46 * math.sin(math.radians(a))
        d.shape("light", circle(round(cx, 1), round(cy, 1), 13))
        d.shape("rice", circle(round(cx, 1), round(cy, 1), 9.5), shadow=False, line=False)
        ca, sa = math.cos(math.radians(a + 90)), math.sin(math.radians(a + 90))
        ox, oy = cx + 18 * ca, cy + 18 * sa
        ux, uy = math.cos(math.radians(a)), math.sin(math.radians(a))
        d.stroke("dark", f"M{ox - 10 * ux:.1f} {oy - 10 * uy:.1f} L{ox + 12 * ux:.1f} {oy + 12 * uy:.1f} "
                         f"M{ox - 10 * ux + 3 * ca:.1f} {oy - 10 * uy + 3 * sa:.1f} L{ox + 12 * ux + 3 * ca:.1f} {oy + 12 * uy + 3 * sa:.1f}", 1.8)
    # side dishes
    for a in (75, 255):
        cx, cy = 100 + 44 * math.cos(math.radians(a)), 100 + 44 * math.sin(math.radians(a))
        d.shape("pop", ellipse(round(cx, 1), round(cy, 1), 11, 8))
        d.shape("leaf", ellipse(round(cx, 1), round(cy, 1), 6, 4), shadow=False, line=False)


def homestay_village(d: Drawing):
    d.disc("glow", 46, 50, 14)
    d.band("far", hills(118, 12))
    d.band("mid", hills(140, 8, 30))
    d.stroke("light", "M136 52 C128 44 140 38 132 28 M142 50 C152 42 144 34 152 24", 2.6)
    d.shape("hero", rrect(128, 56, 12, 22, 1))
    # house
    d.shape("light", rrect(56, 96, 92, 62, 1))
    d.shape("hero", "M46 100 L102 56 L158 100 L152 104 L102 66 L52 104Z", spot=True)
    d.shape("light", "M52 100 L102 62 L152 100Z", shadow=False)
    d.shape("glow2", circle(102, 84, 7), shadow=False)
    d.shape("wood", rrect(92, 120, 22, 38, 2))
    d.shape("glow2", rrect(64, 112, 18, 16, 1), shadow=False, spot=True)
    d.shape("glow2", rrect(124, 112, 18, 16, 1), shadow=False, spot=True)
    d.stroke("wood", "M73 112 V128 M64 120 H82 M133 112 V128 M124 120 H142", 1.4)
    # family waving at the door
    d.shape("dark", person(84, 160, 28), shadow=False)
    d.limb("dark", "M90 140 L96 126", 3, shadow=False)
    d.shape("dark", person(120, 160, 20), shadow=False)
    # washing line and tree
    d.stroke("dark", "M150 118 Q168 126 186 118", 1.2)
    for x, role in [(158, "pop"), (172, "hero2")]:
        d.shape(role, rrect(x - 5, 121, 10, 12, 1), shadow=False)
    d.limb("dark", "M30 160 V120", 4)
    d.shape("leaf", circle(30, 108, 18))
    d.band("near", hills(160, 3))
    d.shape("ground", "M92 160 Q100 172 94 200 H118 Q112 172 114 160Z", shadow=False)
    d.band("deep", hills(184, 3, 20), line=False)


# ================================================================ HOLI FESTIVAL
def holi_clouds(d: Drawing):
    blob(d, "c4", [(146, 72, 22), (164, 92, 18), (136, 92, 16), (156, 56, 14)])
    blob(d, "c2", [(118, 48, 20), (98, 44, 16), (136, 40, 13), (110, 66, 14)], spot=True)
    blob(d, "c1", [(58, 64, 24), (40, 80, 16), (74, 82, 18), (52, 44, 14)])
    blob(d, "c3", [(92, 92, 20), (110, 98, 16), (78, 104, 14)])
    blob(d, "c5", [(48, 108, 12), (34, 116, 9)])
    for x, y, r, role in [(30, 46, 3, "c1"), (82, 30, 2.5, "c2"), (150, 30, 2.8, "c4"), (176, 70, 3, "c4"), (24, 96, 2.4, "c5"),
                          (170, 116, 2.6, "c3"), (128, 116, 2.2, "c2"), (70, 124, 2.4, "c1")]:
        d.marks(role, circle(x, y, r))
    # crowd with raised arms
    for x, y in [(36, 150), (70, 144), (128, 144), (164, 150)]:
        d.limb("dark", f"M{x - 6} {y + 6} L{x - 14} {y - 18} M{x + 6} {y + 6} L{x + 14} {y - 18}", 4.4, shadow=False)
    heads = [(36, 150), (70, 144), (100, 154), (128, 144), (164, 150)]
    p = "M-30 230 V172"
    for x, y in heads:
        p += f" L{x - 14} {y + 24} Q{x - 14} {y + 12} {x - 5} {y + 10} A8 8 0 1 1 {x + 5} {y + 10} Q{x + 14} {y + 12} {x + 14} {y + 24}"
    d.shape("dark", p + " L230 172 V230Z")


def holi_bowls(d: Drawing):
    for x, y, r, role in [(28, 60, 10, "c1"), (172, 140, 11, "c4"), (166, 50, 8, "c2"), (34, 146, 8, "c3")]:
        blob(d, role, [(x, y, r), (x + r * .8, y + r * .4, r * .7), (x - r * .6, y + r * .5, r * .6)], shadow=False)
    d.shape("brass", circle(100, 100, 64))
    d.shape("brass2", circle(100, 100, 56), shadow=False, line=False)
    roles = ["c1", "c2", "c3", "c4", "c6"]
    for i, role in enumerate(roles):
        a = -90 + i * 72
        cx, cy = round(100 + 36 * math.cos(math.radians(a)), 1), round(100 + 36 * math.sin(math.radians(a)), 1)
        d.shape("brass", circle(cx, cy, 17))
        d.shape(role, circle(cx, cy, 13), shadow=False, spot=i == 0)
        d.shape("light", circle(cx - 4, cy - 4, 3.6), shadow=False, line=False)
    d.shape("c5", circle(100, 100, 12), spot=True)
    for a in range(0, 360, 45):
        d.shape("c2", circle(round(100 + 12 * math.cos(math.radians(a)), 1), round(100 + 12 * math.sin(math.radians(a)), 1), 4.5), shadow=False, line=False)
    d.shape("c5", circle(100, 100, 7), shadow=False, line=False)


def holi_celebrant(d: Drawing):
    blob(d, "c1", [(56, 50, 20), (40, 62, 14), (70, 34, 13), (40, 38, 10)])
    blob(d, "c4", [(146, 48, 20), (162, 62, 14), (130, 34, 13), (162, 38, 10)], spot=True)
    blob(d, "c2", [(100, 36, 12), (90, 26, 9), (110, 24, 9)])
    blob(d, "c3", [(30, 120, 12), (20, 132, 9)], shadow=False)
    blob(d, "c5", [(172, 116, 12), (182, 128, 8)], shadow=False)
    d.band("ground", "M-30 172 H230")
    # celebrant in white, arms up
    d.limb("dark", "M94 156 L92 174 M106 156 L108 174", 6)
    d.limb("light", "M88 112 Q72 92 66 70", 9)
    d.limb("light", "M112 112 Q128 92 134 70", 9)
    d.shape("dark", circle(65, 66, 5.5))
    d.shape("dark", circle(135, 66, 5.5))
    d.shape("light", "M84 110 Q100 102 116 110 L124 162 H76Z")
    for x, y, r, role in [(92, 124, 4, "c1"), (108, 118, 3.5, "c4"), (102, 140, 4.5, "c3"), (86, 146, 3, "c2"), (114, 150, 3.5, "c1"),
                          (72, 86, 3, "c2"), (130, 84, 3, "c1")]:
        d.marks(role, circle(x, y, r))
    d.shape("dark", rrect(96, 96, 8, 10, 2))
    d.shape("dark", circle(100, 88, 11))
    d.marks("c1", circle(94, 84, 3) + circle(106, 92, 2.4))


# ================================================================ concept list
GOLD = {"gold": "#E2B04A", "gold2": "#B7862C"}
WOOD = {"wood": "#B07A4A", "wood2": "#8A5A33"}
CURTAIN = {"curtain": "#B8323B", "curtain2": "#8E2430"}
LEAF = {"leaf": "#5E9C4A"}
HOLI = {"c1": "#E8457A", "c2": "#F7C531", "c3": "#3FB37F", "c4": "#3F8FD8", "c5": "#F28A2E", "c6": "#9B5DE5"}
NIGHT = {"sky": "#22294A", "sky2": "#2E3B5E", "far": "#3B4876", "mid": "#52628F", "deep": "#151B30"}

CONCEPTS = [
    # parade
    Concept("parade-float", "parade", "Flower float", parade_float, overrides={**LEAF, "leaf": "#4F8A3F"},
            checks=[("hero", "far"), ("hero", "ground"), ("pop", "sky"), ("hero2", "hero"), ("pop", "hero2")],
            fixes={"hero": ["near", "deep", "mark"], "pop": ["#D7372B", "mark"]}),
    Concept("parade-drum", "parade", "Marching drum", parade_drum, overrides={"wood": "#7A4A26"},
            checks=[("hero", "glow"), ("hero2", "hero"), ("light", "glow")], fixes={"glow": ["far", "mid", "sky2"], "hero2": ["pop", "light"]}),
    Concept("parade-balloon", "parade", "Giant parade balloon", parade_balloon,
            checks=[("hero", "sky"), ("hero", "near"), ("hero", "mid"), ("hero2", "hero"), ("dark", "ground")],
            fixes={"hero": ["pop", "deep"], "near": ["far", "deep"], "mid": ["far", "deep"]}),
    # theatre
    Concept("theatre-curtains", "theatre-show", "Curtain up", theatre_curtains, overrides={**CURTAIN, **GOLD, **WOOD},
            checks=[("curtain", "deep"), ("dark", "glow2")], fixes={"deep": ["dark", "mark"]}),
    Concept("theatre-masks", "theatre-show", "Comedy & tragedy masks", theatre_masks, overrides=GOLD,
            checks=[("gold", "glow"), ("hero", "glow"), ("gold", "hero"), ("pop", "glow")], fixes={"glow": ["far", "mid", "near", "sky2", "light", "deep"], "hero": ["pop", "mark", "deep"]}),
    Concept("theatre-globe", "theatre-show", "Round timber playhouse", theatre_globe,
            overrides={"wood2": "#5A3A22", "thatch": "#C9A25E", "thatch2": "#9C7A3A", "tree": "#4F8A3F"},
            checks=[("light", "far"), ("light", "sky"), ("thatch", "sky"), ("thatch", "far"), ("tree", "far")], fixes={"sky": ["sky2", "far", "glow", "mid"], "far": ["mid", "near", "sky2", "light"]}),
    # opera
    Concept("opera-house", "opera", "Harbour opera house", opera_house, SEA, overrides={"stone": "#D8CCB8", "stone2": "#B5A68E"},
            checks=[("light", "sky"), ("light", "mid")], fixes={"sky": ["sky2", "far", "mid", "near"]}),
    Concept("opera-glasses", "opera", "Opera glasses & rose", opera_glasses, overrides={**GOLD, **LEAF, "pop": "#D7372B"},
            checks=[("gold", "glow"), ("pop", "glow")], fixes={"glow": ["far", "mid", "near", "sky2", "light", "deep"]}),
    Concept("opera-diva", "opera", "Diva on stage", opera_diva, overrides={**CURTAIN, **WOOD},
            checks=[("dark", "glow"), ("hero", "glow"), ("hero", "deep"), ("curtain", "deep")], fixes={"hero": ["pop", "light"], "deep": ["dark", "mark"]}),
    # live music
    Concept("livemusic-sax", "live-music", "Jazz saxophone", livemusic_sax, overrides=GOLD,
            checks=[("gold", "glow"), ("dark", "glow")], fixes={"glow": ["far", "mid", "near", "deep"]}),
    Concept("livemusic-mic", "live-music", "Vintage microphone", livemusic_mic, overrides={**GOLD, "chrome": "#D5DAE1", "chrome2": "#9AA3AE"},
            checks=[("chrome", "glow"), ("dark", "far"), ("chrome", "far")], fixes={"glow": ["near", "deep", "mid"], "far": ["near", "deep"]}),
    Concept("livemusic-drums", "live-music", "Drum kit", livemusic_drums, overrides={**GOLD, **NIGHT},
            checks=[("hero", "far"), ("hero", "mid"), ("gold", "far"), ("light", "hero")], fixes={"hero": ["pop", "hero2"]}),
    # cultural dance show
    Concept("dance-flamenco", "cultural-dance-show", "Flamenco dancer", dance_flamenco, overrides={"pop": "#C8282E", "hero2": "#F2C14E"},
            checks=[("pop", "glow"), ("dark", "glow"), ("pop", "sky"), ("pop", "ground")], fixes={"glow": ["glow2", "light", "far", "sky2"], "ground": ["mid", "near"]}),
    Concept("dance-dervish", "cultural-dance-show", "Whirling dervish", dance_dervish, overrides={"hat": "#8A5A3C"},
            checks=[("light", "far"), ("dark", "far"), ("far", "sky"), ("light", "ground")], fixes={"far": ["mid", "near", "deep"], "ground": ["mid", "near", "deep"]}),
    Concept("dance-kecak", "cultural-dance-show", "Fire dance at sunset", dance_kecak, overrides={"pop": "#E4572E", "glow2": "#FFD25E"},
            checks=[("near", "glow"), ("pop", "glow"), ("dark", "far"), ("near", "sky")], fixes={"glow": ["glow2", "light", "sky2"], "near": ["deep", "dark"]}),
    # tea ceremony
    Concept("tea-matcha", "tea-ceremony", "Matcha bowl & whisk", tea_matcha,
            overrides={"bowl": "#5A3A2E", "bowl2": "#8C6A50", "matcha": "#7FA843", "foam": "#A9C96B", "bamboo": "#E3CC94", "bamboo2": "#B89A5A",
                       "tatami": "#9C9A5E", "tatami2": "#7E7C46"},
            checks=[("bowl", "glow"), ("bamboo", "glow"), ("bowl", "tatami"), ("bamboo", "tatami")], fixes={"glow": ["far", "mid", "near", "sky2"]}),
    Concept("tea-house", "tea-ceremony", "Garden tea house", tea_house,
            overrides={**WOOD, "maple": "#D2553A", "maple2": "#E98A5A", "roof": "#4A4E5A", "roof2": "#6A6F7C", "stone": "#BDB6A8"},
            checks=[("maple", "far"), ("roof", "far"), ("roof", "sky"), ("stone", "near"), ("maple", "sky")], fixes={"far": ["sky2", "mid"], "near": ["mid", "deep"]}),
    Concept("tea-mint", "tea-ceremony", "Moroccan mint tea", tea_mint,
            overrides={"pot": "#C9CED6", "pot2": "#9AA3AE", "tea": "#C77A2A", "brass": "#D4A64A", "brass2": "#B98A30", **LEAF},
            checks=[("pot", "glow"), ("light", "glow"), ("brass", "glow"), ("hero", "glow")], fixes={"glow": ["far", "mid", "near", "deep"]}),
    # calligraphy class
    Concept("calligraphy-inkstone", "calligraphy-class", "Ink painting & brush", calligraphy_inkstone,
            overrides={"wood": "#9C6A40", "wood2": "#7E5230", "ink": "#22242B", "ink2": "#3E414C", "ink3": "#15161A", "pop": "#C8282E",
                       "bamboo": "#E3CC94", "bamboo2": "#B89A5A", **GOLD}),
    Concept("calligraphy-scroll", "calligraphy-class", "Ensō scroll", calligraphy_scroll,
            overrides={**WOOD, "ink": "#22242B", "pop": "#C8282E", "bowl": "#5A3A2E", **LEAF},
            checks=[("hero", "sky2"), ("near", "sky2"), ("wood", "sky2")], fixes={"hero": ["deep", "mark", "pop"], "sky2": ["light", "sky"]}),
    Concept("calligraphy-quill", "calligraphy-class", "Quill & inkwell", calligraphy_quill,
            overrides={**GOLD, "parch": "#F1E2C0", "ink": "#2B2D42", "glass": "#3E5C76", "feather": "#B5A68E"},
            checks=[("light", "glow"), ("parch", "glow"), ("glass", "glow")], fixes={"glow": ["far", "mid", "near"]}),
    # pottery class
    Concept("pottery-wheel", "pottery-class", "Throwing on the wheel", pottery_wheel,
            overrides={"clay": "#C8794A", "clay2": "#A2582F", "metal": "#8C939C", "tray": "#5E6670", "skin": "#E0A57A"},
            checks=[("clay", "glow"), ("skin", "glow"), ("hero", "glow"), ("skin", "clay")], fixes={"glow": ["far", "light", "sky2", "mid"], "hero": ["mark", "deep"]}),
    Concept("pottery-kiln", "pottery-class", "Wood-fired kiln", pottery_kiln,
            overrides={"kiln": "#B5563A", "kiln2": "#8A3D26", "clay": "#C8794A", "pop": "#FF7B3A", "glow2": "#FFD25E"},
            checks=[("kiln", "sky"), ("kiln", "far"), ("clay", "near"), ("clay", "far")], fixes={"far": ["mid", "near", "sky2"], "near": ["deep", "mid"]}),
    Concept("pottery-shelf", "pottery-class", "Glazed pots", pottery_shelf,
            overrides={**WOOD, "clay": "#C8794A", "clay2": "#A2582F", "bamboo": "#E3CC94", "sponge": "#F2D06B"},
            checks=[("hero", "glow"), ("clay", "glow"), ("pop", "glow"), ("hero2", "hero"), ("wood", "glow")], fixes={"glow": ["far", "mid", "sky2", "near"], "hero2": ["light", "pop"]}),
    # language class
    Concept("language-bubbles", "language-class", "Speech bubbles", language_bubbles,
            checks=[("hero", "glow"), ("pop", "glow"), ("pop", "hero"), ("hero2", "glow")], fixes={"glow": ["far", "sky2", "light"], "pop": ["mark", "deep"]}),
    Concept("language-cards", "language-class", "Picture flash cards", language_cards, overrides={**WOOD, **LEAF},
            checks=[("light", "glow"), ("hero", "light"), ("wood", "glow")], fixes={"glow": ["far", "mid", "near"]}),
    Concept("language-board", "language-class", "Chalkboard & globe", language_board,
            overrides={**WOOD, "board": "#2F4A3E", "chalk": "#F4F1E8", "sea": "#3F8FD8", "land": "#6DAA4F"},
            checks=[("wood", "glow"), ("sea", "near"), ("hero", "near"), ("pop", "near")], fixes={"glow": ["far", "light", "sky2"], "near": ["light", "far", "deep"]}),
    # volunteering
    Concept("volunteer-tree", "volunteering", "Planting a tree", volunteer_tree,
            overrides={"wood": "#8A5A33", "metal": "#8C939C", "soil": "#7A4A2A", **LEAF},
            checks=[("leaf", "far"), ("leaf", "mid"), ("hero", "far"), ("hero", "mid"), ("soil", "mid")], fixes={"far": ["sky2", "light"], "mid": ["ground", "near"]}),
    Concept("volunteer-beach", "volunteering", "Beach clean-up", volunteer_beach, SEA,
            checks=[("hero", "ground"), ("hero", "mid"), ("dark", "ground"), ("light", "ground")], fixes={"hero": ["deep", "mark", "pop"], "ground": ["#F2D49B"]}),
    Concept("volunteer-build", "volunteering", "Building a home", volunteer_build,
            overrides={"wood": "#C9955A", "wood2": "#8A5A33", "hat": "#F2B630", "metal": "#5E6670", "stone": "#BDB6A8"},
            checks=[("wood", "sky"), ("wood", "far"), ("hat", "ground"), ("hat", "glow")], fixes={"far": ["mid", "near"], "sky": ["sky2", "far"], "ground": ["mid", "near"]}),
    # homestay
    Concept("homestay-door", "homestay", "Shoes at the door", homestay_door,
            overrides={**WOOD, "wall": "#EADBC4", "roof": "#A0452E", "roof2": "#7E3422", "stone": "#BDB6A8", "pot": "#C8794A", **LEAF},
            checks=[("glow2", "wood"), ("wood", "wall"), ("roof", "wall"), ("hero", "stone"), ("pop", "glow2")],
            fixes={"roof": ["near", "deep"], "glow2": ["glow", "#FFD25E"], "pop": ["#D7372B", "mark"]}),
    Concept("homestay-meal", "homestay", "Family dinner", homestay_meal,
            overrides={"wood": "#B07A4A", "wood2": "#8A5A33", "stew": "#C2562F", "rice": "#F6F1E4", "metal": "#8C939C", **LEAF},
            checks=[("wood", "glow"), ("wood", "sky"), ("pop", "wood")], fixes={"glow": ["far", "mid", "light"], "pop": ["hero", "hero2"]}),
    Concept("homestay-village", "homestay", "Village home", homestay_village, overrides={**WOOD, **LEAF},
            checks=[("light", "far"), ("light", "mid"), ("hero", "sky"), ("hero", "far"), ("leaf", "far"), ("dark", "near")],
            fixes={"far": ["sky2", "mid", "near"], "mid": ["near", "deep"], "hero": ["pop", "deep"]}),
    # holi
    Concept("holi-clouds", "holi-festival", "Colour clouds", holi_clouds, overrides=HOLI,
            checks=[("c1", "sky"), ("c2", "sky"), ("c3", "sky"), ("c4", "sky")], fixes={"sky": ["light", "sky2"]}),
    Concept("holi-bowls", "holi-festival", "Bowls of colour", holi_bowls, overrides={**HOLI, "brass": "#D4A64A", "brass2": "#B98A30"},
            checks=[("brass", "sky")], fixes={"sky": ["sky2", "far", "mid"]}),
    Concept("holi-celebrant", "holi-festival", "Throwing colour", holi_celebrant, overrides=HOLI,
            checks=[("light", "sky"), ("light", "ground"), ("dark", "ground")], fixes={"sky": ["sky2", "far"], "ground": ["mid", "near"]}),
]
