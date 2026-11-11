"""Trails C: wild camping, canyon hike, jungle trek, trail running, marathon, cave tubing,
hammock camping, cross-country skiing, ski touring, heli-skiing, snowshoeing. Three concepts each."""
import math

from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group


# ================================================================ private helpers
def _poly(pts, close=True):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + ("Z" if close else "")


def _pine(x, base, h, w):
    """A layered pine tree: tip at (x, base-h), half-width w."""
    t = base - h
    return (f"M{x} {t} L{x + w * .55:.1f} {t + h * .38:.1f} L{x + w * .3:.1f} {t + h * .36:.1f} L{x + w * .8:.1f} {t + h * .7:.1f} "
            f"L{x + w * .4:.1f} {t + h * .68:.1f} L{x + w:.1f} {base} L{x - w:.1f} {base} L{x - w * .4:.1f} {t + h * .68:.1f} "
            f"L{x - w * .8:.1f} {t + h * .7:.1f} L{x - w * .3:.1f} {t + h * .36:.1f} L{x - w * .55:.1f} {t + h * .38:.1f}Z")


def _snowy_pine(d: Drawing, x, base, h, w, role="deep", snow="light", line=True):
    """A pine with snow resting on each tier."""
    d.shape(role, _pine(x, base, h, w), line=line)
    t = base - h
    caps = [(t, .55, .38, .3, .36), (t + h * .36, .8, .7, .4, .68)]
    d.shape(snow, f"M{x} {t} L{x + w * .55:.1f} {t + h * .38:.1f} L{x + w * .2:.1f} {t + h * .3:.1f} L{x} {t + h * .36:.1f} "
                  f"L{x - w * .2:.1f} {t + h * .3:.1f} L{x - w * .55:.1f} {t + h * .38:.1f}Z", shadow=False, line=False)
    for y0, k in [(t + h * .36, .8), (t + h * .68, 1.0)]:
        yb = t + h * (.7 if k == .8 else 1.0) - (0 if k == .8 else h * 0)
    d.shape(snow, f"M{x - w * .3:.1f} {t + h * .36:.1f} L{x + w * .3:.1f} {t + h * .36:.1f} L{x + w * .8:.1f} {t + h * .7:.1f} "
                  f"L{x + w * .4:.1f} {t + h * .6:.1f} L{x:.1f} {t + h * .66:.1f} L{x - w * .4:.1f} {t + h * .6:.1f} L{x - w * .8:.1f} {t + h * .7:.1f}Z",
            shadow=False, line=False)


def _stars(d, pts, role="light"):
    for x, y, r in pts:
        d.marks(role, f"M{x} {y - r} L{x + r * .3} {y - r * .3} L{x + r} {y} L{x + r * .3} {y + r * .3} "
                      f"L{x} {y + r} L{x - r * .3} {y + r * .3} L{x - r} {y} L{x - r * .3} {y - r * .3}Z")


def _night(d: Drawing, stars):
    d.band("deep", "M-30 -30 L230 -30", shadow=False, line=False)
    _stars(d, stars)


def _moon(d: Drawing, x, y, r):
    d.disc("glow", x, y, r)
    d.shape("deep", circle(x + r * .45, y - r * .35, r * .82), shadow=False, line=False)


def _line_only(d: Drawing, path: str, w: float = 2.4):
    """An extra line drawn only in line style, clipped to the circle like the bands."""
    if not d.paper:
        d.bands.append(f'<path d="{path}" fill="none" stroke="{d.c["ink"]}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')


def _land(d: Drawing, role: str, shape: str, edge: str, shadow: bool = True):
    """A landmass that runs off the canvas: filled in papercut, just its edge in line style."""
    d.shape(role, shape, shadow=shadow, line=False)
    _line_only(d, edge, 3)


def _bar(x1, y1, x2, y2, w):
    """A straight rounded bar as a filled path."""
    dx, dy = x2 - x1, y2 - y1
    n = math.hypot(dx, dy) or 1
    nx, ny = -dy / n * w / 2, dx / n * w / 2
    r = w / 2
    return (f"M{x1+nx:.1f} {y1+ny:.1f} L{x2+nx:.1f} {y2+ny:.1f} A{r} {r} 0 0 0 {x2-nx:.1f} {y2-ny:.1f} "
            f"L{x1-nx:.1f} {y1-ny:.1f} A{r} {r} 0 0 0 {x1+nx:.1f} {y1+ny:.1f}Z")


def _ski(x1, y1, x2, y2, w=5, curl=7):
    """A ski from tail (x1, y1) to tip (x2, y2), tip curled up."""
    dx, dy = x2 - x1, y2 - y1
    n = math.hypot(dx, dy)
    ux, uy = dx / n, dy / n
    nx, ny = uy, -ux
    if ux < 0:
        nx, ny = -nx, -ny
    h = w / 2
    tip = (x2 + ux * 6 + nx * curl, y2 + uy * 6 + ny * curl)
    return (f"M{x1 - nx*h:.1f} {y1 - ny*h:.1f} L{x2 - nx*h:.1f} {y2 - ny*h:.1f} "
            f"Q{x2 + ux*7 - nx*h:.1f} {y2 + uy*7 - ny*h:.1f} {tip[0]:.1f} {tip[1]:.1f} "
            f"Q{x2 + ux*1 + nx*h:.1f} {y2 + uy*1 + ny*h:.1f} {x2 - ux*2 + nx*h:.1f} {y2 - uy*2 + ny*h:.1f} "
            f"L{x1 + nx*h:.1f} {y1 + ny*h:.1f} Q{x1 - ux*3:.1f} {y1 - uy*3:.1f} {x1 - nx*h:.1f} {y1 - ny*h:.1f}Z")


def _flakes(d: Drawing, pts):
    for x, y, r in pts:
        d.stroke("light", f"M{x-r} {y} L{x+r} {y} M{x-r*0.5} {y-r*0.87} L{x+r*0.5} {y+r*0.87} M{x-r*0.5} {y+r*0.87} L{x+r*0.5} {y-r*0.87}", 1.6)


def _leaf(x, y, L, ang, w):
    a = math.radians(ang)
    tx, ty = x + L * math.cos(a), y + L * math.sin(a)
    mx, my = (x + tx) / 2, (y + ty) / 2
    px, py = -math.sin(a) * w, math.cos(a) * w
    return (f"M{x:.1f} {y:.1f} Q{mx + px:.1f} {my + py:.1f} {tx:.1f} {ty:.1f} Q{mx - px:.1f} {my - py:.1f} {x:.1f} {y:.1f}Z",
            f"M{x:.1f} {y:.1f} L{tx:.1f} {ty:.1f}")


def _leaves(d, items, rib="light", line=True):
    for role, x, y, L, ang, w in items:
        p, r = _leaf(x, y, L, ang, w)
        d.shape(role, p, line=line)
        d.stroke(rib, r, 1.2, line=False)


def _heli(d: Drawing, body="hero", stripe="hero2", glass="light"):
    """A helicopter facing right, cabin centred around (110, 100)."""
    d.stroke("dark", "M78 124 L76 132 M128 124 L130 132", 3)
    d.limb("dark", "M62 134 H146 Q152 134 154 128", 3.2)
    d.shape(body, "M76 96 L24 88 L22 82 L80 84Z")
    d.shape(body, "M18 66 L28 66 L32 88 L22 90Z")
    d.stroke("dark", "M24 64 V80 M16 72 H32", 2.4)
    d.shape(body, "M64 104 C62 86 80 74 104 72 L120 72 C142 72 158 88 158 102 C158 116 146 124 128 124 L84 124 C70 124 64 116 64 104Z")
    d.shape(glass, "M120 76 C138 76 152 88 154 100 L122 100 Z", shadow=False)
    d.shape(glass, rrect(94, 82, 20, 16, 3), shadow=False)
    d.shape(stripe, "M66 108 L157 108 C156 113 154 116 151 118 L70 118 C67 115 66 112 66 108Z", shadow=False, spot=True)
    d.shape("dark", rrect(104, 64, 10, 9, 2))
    d.shape("dark", rrect(28, 60, 164, 5, 2.5))


# ================================================================ WILD CAMPING
def wild_lake(d: Drawing):
    d.disc("glow", 142, 60, 16)
    d.band("far", "M-30 104 L18 76 L44 92 L80 58 L112 90 L140 74 L172 96 L230 86")
    for snow in ["M80 58 L91 69 L86 68 L80 73 L75 68 L70 69Z", "M140 74 L148 81 L144 81 L140 84 L136 80 L133 81Z",
                 "M18 76 L25 83 L21 82 L17 85 L13 81Z"]:
        d.shape("light", snow, shadow=False)
    d.band("mid", hills(110, 6, 10))
    d.band("sky2", "M-30 118 Q100 112 230 118")
    d.stroke("light", "M118 128 H150 M130 136 H160 M30 130 H52", 1.8, line=False)
    _land(d, "near", "M-30 150 C20 140 70 136 110 146 C140 154 170 166 230 162 V230 H-30Z",
          "M-30 150 C20 140 70 136 110 146 C140 154 170 166 230 162")
    d.shape("deep", _pine(164, 166, 62, 16))
    d.shape("deep", _pine(184, 168, 44, 12))
    # small ridge tent, three-quarter view
    d.stroke("dark", "M48 152 L36 158 M140 152 L150 158", 1.4)
    d.shape("hero2", "M84 102 L136 110 L150 150 L112 152Z")
    d.shape("hero", "M84 102 L52 152 L112 152Z", spot=True)
    d.shape("dark", "M84 116 L70 152 H98Z", shadow=False)
    d.stroke("dark", "M84 102 V96", 2)
    d.band("ground", "M-30 168 Q60 160 120 168 T230 170", line=False)


def wild_stove(d: Drawing):
    d.disc("glow", 100, 86, 62)
    d.band("far", "M-30 120 L20 94 L50 110 L90 84 L120 104 L160 86 L230 112")
    d.band("mid", hills(146, 6, 20))
    d.band("ground", "M-30 168 Q100 156 230 168")
    # steam
    d.stroke("light", "M88 50 C80 42 96 36 88 28 M108 50 C100 42 116 36 108 26", 3.2)
    # gas canister
    d.shape("hero2", "M70 162 V136 C70 124 80 118 100 118 C120 118 130 124 130 136 V162Z", spot=True)
    d.shape("light", rrect(70, 140, 60, 10, 2), shadow=False, line=False)
    d.shape("dark", rrect(66, 158, 68, 8, 3))
    d.shape("dark", rrect(90, 108, 20, 12, 3))
    # pot supports
    d.limb("dark", "M84 112 L74 102 M116 112 L126 102", 3.4)
    # flame
    d.shape("pop", "M80 102 C82 96 88 94 90 90 C92 96 96 96 100 88 C104 96 108 96 110 90 C112 94 118 96 120 102Z", shadow=False)
    # pot
    d.shape("hero", "M66 100 H134 V72 Q134 66 128 66 H72 Q66 66 66 72Z")
    d.shape("dark", rrect(62, 60, 76, 9, 4))
    d.shape("dark", rrect(94, 54, 12, 7, 3))
    d.limb("dark", "M134 76 H162", 4.5)
    d.shape("light", rrect(74, 74, 6, 18, 3), shadow=False, line=False)


def wild_bivvy(d: Drawing):
    _night(d, [(30, 70, 2.4), (52, 40, 3), (84, 24, 2), (120, 42, 2.6), (176, 74, 2.2), (150, 22, 2), (100, 64, 1.8), (24, 104, 1.8)])
    d.raw('<path d="M-10 120 C40 90 110 60 210 20 L210 56 C120 90 60 120 -10 150Z" fill="#fff" opacity=".12"/>', "")
    _moon(d, 150, 54, 14)
    d.band("far", "M-30 128 L24 104 L60 120 L104 96 L140 116 L180 100 L230 120")
    _land(d, "near", "M-30 150 C30 144 120 140 230 150 V230 H-30Z", "M-30 150 C30 144 120 140 230 150")
    # sleeping mat and mummy bag
    d.shape("dark", rrect(34, 146, 140, 10, 5))
    d.shape("hero", "M40 136 C40 120 54 114 70 114 C96 114 120 120 150 124 C166 126 174 132 172 140 C170 148 162 150 150 150 L62 152 C48 152 40 146 40 136Z", spot=True)
    d.shape("hero2", "M88 115 C92 128 92 140 88 151 L94 151 C98 140 98 128 94 116Z", shadow=False)
    d.stroke("mark", "M96 120 C120 122 140 126 160 130", 1.6, line=False)
    d.shape("dark", ellipse(62, 132, 15, 14), shadow=False)
    d.shape("ground", ellipse(63, 134, 9.5, 9), shadow=False)
    d.shape("pop", "M53 130 C53 118 72 118 73 130Z", shadow=False)
    d.marks("mark", "M58 135 q2 1.6 4 0 M65 135 q2 1.6 4 0")
    d.band("deep", "M-30 176 Q100 168 230 176", line=False)


# ================================================================ CANYON HIKE
def canyon_slot(d: Drawing):
    d.disc("glow", 104, 6, 16, line=False)
    d.shape("far", "M-30 -30 H82 C70 20 98 50 86 92 C76 130 100 150 90 230 H-30Z")
    d.shape("far", "M230 -30 H118 C130 24 106 54 118 94 C128 130 106 152 114 230 H230Z")
    d.shape("mid", "M-30 -30 H62 C50 26 80 56 66 96 C56 132 80 156 66 230 H-30Z", shadow=True)
    d.shape("mid", "M230 -30 H140 C152 28 126 58 140 96 C150 132 128 156 138 230 H230Z")
    d.shape("near", "M-30 -30 H36 C26 36 56 70 40 104 C30 136 52 164 36 230 H-30Z")
    d.shape("near", "M230 -30 H166 C178 36 150 72 166 106 C176 140 154 164 168 230 H230Z")
    d.stroke("glow2", "M74 20 C66 50 92 70 82 100 M128 24 C120 56 140 76 132 104", 2, line=False)
    if d.paper:
        d.raw(f'<path d="M92 -10 L112 -10 L124 170 L84 170Z" fill="{d.c["light"]}" opacity=".35"/>')
    else:
        d.raw("", f'<path d="M92 -10 L112 -10 L124 170 L84 170Z" fill="{d.c["spot"]}" opacity=".3"/>')
    d.band("ground", "M-30 168 Q100 160 230 168")
    # small hiker in the beam
    d.limb("dark", "M102 150 L98 166 M104 150 L110 166", 4)
    d.shape("hero", rrect(96, 128, 13, 25, 5), spot=True)
    d.shape("pop", rrect(92, 132, 8, 14, 3))
    d.shape("dark", circle(103, 122, 6))
    d.band("deep", "M-30 184 Q100 178 230 184", line=False)


def canyon_switchback(d: Drawing):
    d.disc("glow", 150, 50, 16)
    d.band("far", "M-30 84 H22 L28 76 H70 L76 84 H120 L128 72 H176 L182 84 H230")
    d.band("mid", "M-30 104 H12 L18 98 H52 L60 110 H92 L100 96 H140 L148 108 H230")
    # canyon floor and river far below
    d.shape("far", "M30 230 L70 130 H140 L170 230Z", line=False)
    d.shape("sky2", "M84 230 C90 200 96 170 98 140 L106 140 C108 170 110 200 120 230Z")
    # the two walls
    _land(d, "near", "M-30 230 V112 H30 L40 122 L50 140 L66 150 L74 172 L88 186 L92 230Z",
          "M-30 112 H30 L40 122 L50 140 L66 150 L74 172 L88 186 L92 230")
    _land(d, "deep", "M230 230 V108 H176 L166 120 L150 128 L142 146 L124 160 L116 180 L110 230Z",
          "M230 108 H176 L166 120 L150 128 L142 146 L124 160 L116 180 L110 230")
    d.stroke("deep", "M-30 134 H44 M-30 160 H68 M-30 188 H88", 2, line=False)
    d.stroke("near", "M230 132 H156 M230 160 H130 M230 190 H116", 2, line=False)
    # zig-zag trail down the right wall
    d.stroke("ground", "M170 110 L154 128 L190 140 L142 154 L184 168 L128 182 L176 198 L120 212", 3.6)

    def hiker():
        d.limb("dark", "M0 -6 L-4 8 M2 -6 L6 8", 3.4)
        d.shape("hero", rrect(-6, -24, 12, 20, 4), spot=True)
        d.shape("pop", rrect(-11, -22, 7, 13, 2.5))
        d.shape("dark", circle(1, -29, 4.6))
        d.stroke("dark", "M6 -16 L10 8", 1.4)
    group(d, "translate(160 120) scale(1.2)", hiker)



def canyon_arch(d: Drawing):
    d.disc("glow", 100, 112, 30)
    d.band("far", "M-30 136 H20 L28 124 H60 L66 136 H140 L148 120 H180 L188 136 H230")
    d.band("ground", "M-30 158 Q40 146 100 152 T230 150")
    arch = ("M52 166 C50 132 44 96 58 70 C70 48 96 38 118 46 C142 56 152 86 148 118 C146 136 146 152 148 166 H128 "
            "C128 150 130 130 128 110 C126 88 116 76 102 76 C86 76 78 90 76 112 C74 130 76 150 76 166Z")
    d.shape("near", arch, spot=True)
    d.stroke("deep", "M60 92 C70 88 80 86 88 80 M132 82 C140 90 142 100 146 102 M56 130 H74 M130 132 H148", 2, line=False)
    d.shape("deep", "M118 46 C142 56 152 86 148 118 C146 136 146 152 148 166 H140 C140 140 144 100 136 74 C132 62 126 52 118 46Z", shadow=False, line=False)
    # tiny hiker under the arch
    d.limb("dark", "M101 160 L99 170 M103 160 L106 170", 2.6)
    d.shape("hero", rrect(97, 146, 9, 16, 3.5))
    d.shape("dark", circle(101.5, 142, 3.6))
    d.band("mid", "M-30 172 Q60 162 120 170 T230 166")
    d.band("deep", hills(188, 3), line=False)


# ================================================================ JUNGLE TREK
def jungle_temple(d: Drawing):
    d.disc("glow", 150, 58, 16)
    for x, y, r in [(10, 112, 22), (40, 104, 18), (166, 104, 20), (196, 112, 22)]:
        d.shape("far", circle(x, y, r), line=False)
    d.band("far", "M-30 112 L230 112", shadow=False, line=False)
    # stepped pyramid with roof comb
    tiers = [(56, 144, 88), (64, 128, 72), (72, 112, 56), (80, 96, 40)]
    for x, y, w in tiers:
        d.shape("ground", f"M{x} {y + 16} L{x + 4} {y} H{x + w - 4} L{x + w} {y + 16}Z")
    d.shape("ground", rrect(86, 70, 28, 26, 2))
    d.shape("ground", "M90 70 L92 54 H108 L110 70Z")
    d.shape("dark", rrect(96, 78, 8, 12, 2), shadow=False)
    d.shape("mid", "M94 160 L96 96 H104 L106 160Z", shadow=False, spot=True)
    d.stroke("ground", "M95 108 H105 M95 120 H105 M94 132 H106 M94 144 H106", 1.6, line=False)
    d.stroke("near", "M64 128 C66 136 62 140 66 148 M128 112 C130 118 126 124 130 132", 2.2)
    # canopy in front
    for x, y, r in [(-4, 150, 26), (26, 160, 22), (52, 168, 18), (150, 168, 18), (176, 158, 22), (206, 150, 26)]:
        d.shape("near", circle(x, y, r), line=False)
    _line_only(d, "M-30 140 C-10 120 20 130 30 140 C40 132 60 144 68 160 M132 160 C140 144 160 132 170 140 C180 130 210 120 230 140", 2.6)
    d.band("near", "M-30 170 Q100 160 230 170", shadow=False, line=False)
    _leaves(d, [("deep", -10, 196, 70, -40, 16), ("deep", 210, 196, 70, 220, 16)], line=False)
    _leaves(d, [("deep", 34, 186, 34, -60, 9), ("deep", 166, 186, 34, 240, 9)])
    d.band("deep", hills(188, 3), line=False)


MONKEY = "M90 84 C82 92 82 114 90 126 C96 134 108 134 112 124 C118 110 114 92 106 84 C102 80 94 80 90 84Z"


def jungle_monkey(d: Drawing):
    d.disc("glow", 52, 60, 16)
    _leaves(d, [("far", -10, 70, 70, -10, 18), ("far", 210, 80, 70, 190, 18), ("mid", -10, 140, 70, -30, 18),
                ("mid", 210, 150, 70, 210, 18)], line=False)
    d.band("near", "M-30 186 Q60 176 100 182 T230 180", line=False)
    d.limb("deep", "M-10 44 Q80 30 210 52", 9)
    d.stroke("near", "M150 46 C152 70 146 90 150 110", 2.4)
    # tail curled around the branch
    d.limb("hero", "M104 128 C130 140 150 120 144 90 C140 66 126 50 128 40 C130 32 140 34 138 42", 4.2)
    # arms
    d.limb("hero", "M100 88 C100 70 98 56 96 42", 6)
    d.limb("hero", "M90 92 C76 100 64 108 56 104", 6)
    # legs
    d.limb("hero", "M94 126 C88 140 80 146 76 154", 6.5)
    d.limb("hero", "M106 126 C112 138 112 148 118 156", 6.5)
    d.shape("hero", MONKEY)
    d.shape("hero2", "M94 98 C90 106 92 118 98 124 C104 118 106 106 102 98Z", shadow=False)
    # head
    d.shape("hero", circle(86, 72, 14))
    d.shape("hero2", ellipse(82, 75, 9, 8.5), shadow=False)
    d.marks("mark", circle(79, 72, 1.8) + circle(86, 72, 1.8) + ellipse(82, 80, 2.4, 1.4))
    d.shape("hero", circle(99, 68, 4.5), shadow=False)
    # hands
    d.marks("mark", circle(96, 42, 3.4) + circle(55, 104, 3.2))
    _leaves(d, [("near", 210, 196, 80, 230, 20), ("near", -10, 200, 80, -50, 20)], line=False)
    _leaves(d, [("near", 40, 40, 30, 150, 8), ("near", 160, 48, 32, 40, 8), ("near", 34, 176, 30, -60, 8)])


def jungle_boots(d: Drawing):
    _leaves(d, [("far", -10, 40, 80, 10, 20), ("far", 210, 40, 80, 170, 20), ("mid", -10, 110, 80, -15, 22),
                ("mid", 210, 120, 80, 200, 22), ("near", 100, -10, 50, 60, 14)], line=False)
    _leaves(d, [("mid", 30, 74, 34, -30, 9), ("mid", 170, 80, 34, 210, 9)])
    d.band("ground", "M-30 156 Q60 148 100 154 T230 152")

    def boot(dx, dy, role):
        def g():
            d.shape(role, "M62 58 H94 L96 120 C108 124 122 128 132 136 Q140 142 136 150 H60 Q56 150 56 144 Z", spot=role == "hero")
            d.shape("dark", "M56 144 H136 Q138 152 132 156 H60 Q56 156 56 150Z")
            d.shape("dark", rrect(58, 54, 40, 10, 4))
            d.marks("deep", "M57 136 Q64 128 70 138 Q76 130 84 138 Q92 132 100 140 Q112 132 124 140 Q132 138 136 144 H56Z")
            d.marks("deep", circle(72, 124, 2.4) + circle(88, 118, 1.8) + circle(110, 128, 2))
            d.stroke("light", "M68 68 V110", 3, line=False)
        group(d, f"translate({dx} {dy})", g)
    boot(40, -4, "hero2")
    boot(-10, 6, "hero")
    d.band("deep", "M-30 166 Q30 158 70 164 Q110 170 150 162 T230 166")
    for x, y, r in [(30, 158, 4), (160, 156, 3), (178, 162, 5), (16, 164, 3)]:
        d.shape("deep", circle(x, y, r), line=False)
    _leaves(d, [("near", -10, 196, 80, -45, 20), ("near", 210, 196, 80, 225, 20)], line=False)
    _leaves(d, [("near", 20, 190, 36, -70, 9), ("near", 182, 190, 36, 250, 9)])



# ================================================================ TRAIL RUNNING
SHOE = ("M38 118 C38 102 48 92 60 90 L80 84 C88 82 96 86 100 92 L114 106 C128 112 148 114 162 120 "
        "C172 124 172 134 164 138 L44 140 C40 138 38 130 38 118Z")


def trail_shoe(d: Drawing):
    d.disc("glow", 100, 100, 62)
    d.band("far", "M-30 120 L24 90 L56 108 L96 74 L130 102 L164 82 L230 110")
    d.band("mid", hills(150, 8, 20))
    for x, y, r in [(26, 140, 8), (14, 128, 6), (38, 128, 5), (20, 148, 6)]:
        d.shape("ground", circle(x, y, r), line=False)
    d.stroke("ground", "M10 120 C20 116 26 120 32 116 M12 136 L28 136", 2.2)

    def shoe():
        d.shape("hero", SHOE, spot=True)
        d.shape("hero2", "M38 118 C40 128 44 132 60 132 L164 130 C170 128 172 132 164 138 L44 140 C40 138 38 130 38 118Z", shadow=False)
        d.shape("light", "M64 118 C84 104 110 108 140 120 L132 124 C110 116 88 116 70 124Z", shadow=False)
        d.stroke("light", "M90 92 L84 100 M98 96 L92 104 M106 102 L100 110", 2.6)
        d.shape("dark", "M40 138 H166 Q170 138 168 144 L164 148 H46 Q40 148 40 142Z")
        for x in range(48, 164, 12):
            d.shape("dark", f"M{x} 146 L{x + 3} 154 H{x + 8} L{x + 9} 146Z", shadow=False)
        d.shape("hero2", "M60 90 L80 84 C88 82 96 86 100 92 L94 96 C88 90 80 90 64 96Z", shadow=False)
    group(d, "rotate(-12 100 120) translate(6 -6)", shoe)


def _runner(d: Drawing, body="hero", legs="dark", head="dark", cap="pop"):
    """A runner mid-stride facing right, feet around y 122."""
    d.limb(legs, "M94 92 L84 106 L68 104", 7)
    d.limb(body, "M100 74 L90 82 L82 92", 5)
    d.limb(legs, "M94 92 L110 104 L104 122", 7.5)
    d.shape("dark", "M98 120 L112 120 Q114 125 110 126 L98 126Z")
    d.shape("dark", "M62 98 L70 100 L68 108 L60 108Z")
    d.limb(body, "M102 66 L94 92", 11)
    d.limb(body, "M102 72 L112 82 L122 74", 5)
    d.shape(head, circle(106, 56, 7.5))
    d.shape(cap, "M98 54 Q100 46 108 47 Q114 48 114 54 L120 55 Q118 57 112 56 L98 56Z", shadow=False, spot=True)


def trail_ridge(d: Drawing):
    d.disc("glow", 104, 82, 44)
    d.band("far", "M-30 132 L20 110 L56 124 L88 104 L128 126 L170 102 L230 120")
    d.band("near", "M-30 176 L30 150 L70 136 L100 132 L130 136 L170 150 L230 170")
    d.stroke("ground", "M100 132 L130 136 L170 150 L230 170", 2.5, line=False)
    group(d, "translate(102 140) scale(1.15) translate(-100 -126)", lambda: _runner(d))
    d.band("deep", "M-30 190 L60 170 L120 180 L230 168", line=False)


def trail_watch(d: Drawing):
    d.band("far", "M-30 134 L20 104 L52 120 L92 86 L124 112 L160 92 L230 124")
    d.band("mid", hills(162, 8, 20))
    d.shape("dark", "M76 30 H124 L120 66 H80Z")
    d.shape("dark", "M80 134 H120 L124 176 H76Z")
    d.stroke("mid", "M84 42 H116 M84 52 H116 M82 152 H118 M82 164 H118", 2, line=False)
    d.shape("dark", rrect(144, 92, 9, 16, 3))
    d.shape("hero", circle(100, 100, 46), spot=True)
    d.shape("dark", circle(100, 100, 38), shadow=False)
    d.shape("deep", circle(100, 100, 34), shadow=False, line=False)
    prof = "M70 116 L80 106 L88 110 L98 90 L106 100 L114 84 L124 104 L130 116Z"
    d.shape("glow", prof, shadow=False)
    d.stroke("pop", "M70 116 L80 106 L88 110 L98 90 L106 100 L114 84 L124 104 L130 116", 2.4)
    d.marks("pop", circle(114, 84, 3.4))
    d.stroke("light", "M84 76 H116 M90 126 H110", 3)


# ================================================================ MARATHON
def marathon_finish(d: Drawing):
    d.disc("glow", 100, 132, 26)
    d.band("far", hills(132, 6, 10))
    # road in perspective
    d.band("mid", "M-30 150 L230 150", line=False)
    d.shape("dark", "M84 150 H116 L170 230 H30Z", line=False)
    _line_only(d, "M84 150 L30 230 M116 150 L170 230", 3)
    d.stroke("light", "M100 156 V164 M100 174 V186 M100 198 V214", 3)
    # inflatable arch with a chequered band
    arch = "M30 168 V96 C30 52 170 52 170 96 V168"
    d.limb("hero", arch, 20, spot=True)
    d.stroke("light", "M30 120 V96 C30 52 170 52 170 96 V120", 8, line=False)
    d.raw(f'<path d="M30 120 V96 C30 52 170 52 170 96 V120" fill="none" stroke="{d.c.get("mark", "")}" stroke-width="8" stroke-dasharray="6 6"/>', "")
    # finish tape stretched across
    d.limb("pop", "M38 134 Q100 146 162 134", 5, spot=True)
    d.shape("dark", rrect(20, 164, 20, 8, 3))
    d.shape("dark", rrect(160, 164, 20, 8, 3))



def marathon_medal(d: Drawing):
    d.disc("sky2", 100, 100, 70, line=False)
    for i in range(12):
        a = math.radians(i * 30 + 15)
        d.shape("glow2", _poly([(100 + 50 * math.cos(a - .12), 124 + 50 * math.sin(a - .12)), (100 + 80 * math.cos(a), 124 + 80 * math.sin(a)),
                                (100 + 50 * math.cos(a + .12), 124 + 50 * math.sin(a + .12))]), shadow=False, line=False)
    # ribbon
    d.shape("hero", "M62 20 H90 L112 92 H88Z", spot=True)
    d.shape("pop", "M138 20 H110 L88 92 H112Z")
    d.shape("light", "M70 20 H78 L98 86 H92Z", shadow=False, line=False)
    d.shape("light", "M122 20 H130 L106 86 H100Z", shadow=False, line=False)
    d.shape("mark", rrect(88, 86, 24, 12, 3))
    # medal
    d.shape("hero2", circle(100, 128, 36))
    d.shape("glow", circle(100, 128, 27), shadow=False)
    star = _poly([(100 + (16 if k % 2 == 0 else 7) * math.cos(math.radians(-90 + k * 36)),
                   128 + (16 if k % 2 == 0 else 7) * math.sin(math.radians(-90 + k * 36))) for k in range(10)])
    d.shape("hero2", star, shadow=False, spot=True)
    d.stroke("light", "M76 112 C80 104 86 100 92 98", 3, line=False)
    for side in (-1, 1):
        for k in range(4):
            a = math.radians(90 + side * (40 + k * 22))
            x, y = 100 + 31 * math.cos(a), 128 + 31 * math.sin(a)
            d.marks("mark", ellipse(x, y, 2.4, 1.4))


def marathon_bib(d: Drawing):
    d.disc("glow", 100, 100, 70, line=False)
    # running vest
    d.shape("hero", "M38 200 L40 70 C40 54 54 40 66 34 C74 50 86 58 100 58 C114 58 126 50 134 34 C146 40 160 54 160 70 L162 200Z")
    d.shape("hero2", "M66 34 C74 50 86 58 100 58 C114 58 126 50 134 34 L128 30 C122 44 112 50 100 50 C88 50 78 44 72 30Z", shadow=False)
    # bib
    d.shape("light", "M56 88 H144 Q148 88 148 92 V158 Q148 162 144 162 H56 Q52 162 52 158 V92 Q52 88 56 88Z")
    d.shape("pop", "M52 92 Q52 88 56 88 H144 Q148 88 148 92 V104 H52Z", shadow=False, spot=True)
    # running shoe on the bib
    d.shape("mark", "M70 148 V128 C70 120 78 118 84 121 L94 126 C104 132 118 134 128 137 C136 139 136 147 130 149 H72 Q70 149 70 148Z", shadow=False)
    d.shape("light", "M70 142 H134 V146 H70Z", shadow=False, line=False)
    d.stroke("light", "M86 124 L82 130 M94 128 L90 134", 2, line=False)
    d.stroke("far", "M64 114 H136", 2.4, line=False)
    for x, y in [(60, 96), (140, 96), (60, 154), (140, 154)]:
        d.stroke("mark", f"M{x - 4} {y - 3} L{x + 4} {y + 3}", 2)
        d.marks("mark", circle(x - 4, y - 3, 1.8))


# ================================================================ CAVE TUBING
def _tuber(d: Drawing, tube="hero", body="hero2", head="dark", lamp=True, beam=None):
    """A person sitting in an inner tube, facing the viewer slightly left; tube centred on (0, 0)."""
    d.shape(tube, ellipse(0, 0, 26, 10), spot=True)
    d.shape("dark", ellipse(0, -2, 14, 4.5), shadow=False)
    d.limb(body, "M-2 -6 L0 -26", 11)
    d.limb("dark", "M-4 -4 L-12 6 L-18 10 M4 -4 L10 6 L16 10", 4.2)
    d.limb(body, "M-4 -22 L-14 -12 L-22 -6 M4 -22 L14 -12 L22 -6", 3.6, shadow=False)
    d.shape(tube, "M-26 0 C-26 8 -14 10 0 10 C14 10 26 8 26 0 C22 6 12 6 0 6 C-12 6 -22 6 -26 0Z", shadow=False)
    d.shape(head, circle(0, -32, 6.5))
    if lamp:
        d.shape("pop", rrect(-3.5, -38, 7, 4, 1.5), shadow=False)
        d.stroke("dark", "M-6 -35 Q0 -37 6 -35", 1.2, line=False)


def cavetube_mouth(d: Drawing):
    d.disc("glow", 46, 52, 14)
    for x, y, r in [(150, 92, 24), (180, 80, 22), (204, 96, 22)]:
        d.shape("far", circle(x, y, r), line=False)
    d.band("far", "M-30 100 L230 100", shadow=False, line=False)
    # limestone hill with the cave mouth
    d.shape("mid", "M-30 230 V112 C10 86 50 60 100 58 C150 60 190 86 230 104 V230Z")
    d.shape("dark", "M50 132 C52 98 76 82 100 82 C124 82 148 98 150 132Z", shadow=False)
    d.shape("near", "M50 132 C52 98 76 82 100 82 C108 82 112 86 108 88 L104 100 L98 92 L92 106 L86 92 L78 104 L72 96 L66 112 L60 104Z", shadow=False, line=False)
    d.shape("near", "M150 132 C148 104 136 92 122 86 L120 96 L126 92 L128 104 L134 96 L140 110Z", shadow=False, line=False)
    _leaves(d, [("near", -10, 110, 60, 10, 14), ("near", 210, 110, 60, 170, 14)], line=False)
    # river flowing out of the cave toward us
    d.shape("near", "M-30 230 V150 C20 146 40 136 50 132 H150 C160 136 180 146 230 150 V230Z", line=False)
    d.shape("sky2", "M50 132 H150 C170 150 200 176 230 186 V230 H-30 V186 C0 176 30 150 50 132Z")
    d.stroke("light", "M70 146 H92 M114 150 H140 M40 174 H70 M140 178 H166", 2)
    group(d, "translate(100 164) scale(1.05)", lambda: _tuber(d))
    _leaves(d, [("deep", -10, 200, 70, -40, 16), ("deep", 210, 200, 70, 220, 16)], line=False)


STALACTITES = ("M-30 -30 H230 V40 L210 44 L204 70 L196 46 L180 50 L172 84 L162 52 L140 56 L134 76 L124 56 L104 54 "
               "L98 66 L90 54 L70 56 L62 86 L52 52 L34 48 L26 70 L18 44 L-30 40Z")


def cavetube_dark(d: Drawing):
    d.band("deep", "M-30 -30 L230 -30", shadow=False, line=False)
    d.shape("near", STALACTITES)
    d.shape("near", "M-30 230 V120 L0 112 L14 128 L-30 140Z M230 230 V116 L204 110 L192 130 L230 140Z", line=False)
    d.band("mid", waves(150, 3, 28))
    d.stroke("far", "M30 164 H56 M120 170 H150 M70 184 H96", 2)
    beams = ["M58 112 L140 64 L156 100Z", "M128 128 L200 104 L204 136Z"]
    for b in beams:
        if d.paper:
            d.raw(f'<path d="{b}" fill="{d.c["glow2"]}" opacity=".45"/>')
        else:
            d.raw("", f'<path d="{b}" fill="{d.c["spot"]}" opacity=".3"/>')
    group(d, "translate(62 144) scale(.8)", lambda: _tuber(d, head="ground"))
    group(d, "translate(128 160) scale(1.0)", lambda: _tuber(d, head="ground"))
    d.band("near", waves(186, 3, 34), line=False)


def cavetube_ring(d: Drawing):
    d.band("deep", "M-30 -30 L230 -30", shadow=False, line=False)
    d.shape("near", STALACTITES)
    d.shape("near", "M-30 230 V96 L-6 90 L10 110 L24 120 L-30 128Z M230 230 V92 L206 88 L190 108 L178 118 L230 126Z", line=False)
    beam = "M146 112 L230 40 L230 110Z"
    if d.paper:
        d.raw(f'<path d="{beam}" fill="{d.c["glow2"]}" opacity=".4"/>')
    else:
        d.raw("", f'<path d="{beam}" fill="{d.c["spot"]}" opacity=".3"/>')
    d.band("mid", waves(118, 3, 28))
    d.stroke("far", "M24 134 H50 M156 138 H182 M30 178 H54 M148 182 H172", 2)
    # big inner tube on the water
    d.shape("hero", ellipse(100, 146, 64, 30), spot=True)
    d.shape("deep", ellipse(100, 140, 30, 12), shadow=False)
    d.shape("mid", "M70 142 C76 148 88 152 100 152 C112 152 124 148 130 142 C128 150 116 156 100 156 C84 156 72 150 70 142Z", shadow=False, line=False)
    d.stroke("light", "M52 130 C58 122 70 118 80 116", 4, line=False)
    d.shape("dark", rrect(97, 116, 6, 6, 1.5))
    # headlamp resting on the tube
    d.limb("dark", "M120 120 C128 108 152 108 160 120", 4)
    d.shape("dark", rrect(128, 106, 24, 14, 5))
    d.disc("glow2", 140, 113, 5)



# ================================================================ HAMMOCK CAMPING
def _trunk(d, x, role="dark", w=10):
    d.limb(role, f"M{x} 30 L{x} 190", w)


def hammock_forest(d: Drawing):
    d.disc("glow", 100, 56, 16)
    for x, h, b in [(56, 60, 120), (78, 46, 118), (128, 52, 120), (150, 64, 122)]:
        d.shape("far", _pine(x, b, h, h * .32), line=False)
    d.band("mid", hills(130, 6, 10))
    d.band("ground", hills(160, 4, 30))
    d.limb("deep", "M30 -10 V184", 14)
    d.limb("deep", "M170 -10 V184", 14)
    d.shape("deep", "M-30 -30 H60 C40 0 30 20 -30 40Z M230 -30 H140 C160 0 170 20 230 40Z", line=False)
    d.stroke("dark", "M36 80 L50 98 M164 80 L150 98", 1.8)
    d.limb("dark", "M24 80 H36 M164 80 H176", 4)
    # sleeper tucked into the hammock
    d.shape("light", circle(66, 100, 9))
    d.shape("pop", "M57 98 C57 86 75 86 76 96Z", shadow=False)
    d.shape("hero2", "M68 108 C90 96 124 98 140 104 C138 116 126 122 104 122 C86 122 72 118 68 108Z")
    # hammock
    d.shape("hero", "M48 98 C60 160 140 160 152 98 C134 120 118 128 100 128 C82 128 66 120 48 98Z", spot=True)
    d.shape("pop", "M58 122 C80 148 120 148 142 122 L144 116 C120 140 80 140 56 116Z", shadow=False)
    d.band("near", hills(186, 3, -20), line=False)


def _foot(d: Drawing, x, left=True):
    k = 1 if left else -1
    d.shape("ground", f"M{x - 8} 176 C{x - 12} 160 {x - 13} 140 {x - 12} 128 C{x - 11} 118 {x - 6} 114 {x} 114 "
                      f"C{x + 6} 114 {x + 11} 118 {x + 12} 128 C{x + 13} 140 {x + 10} 160 {x + 8} 176Z")
    for dx, dy, r in [(6.5, 109, 5), (-.5, 106.5, 3.8), (-5.8, 108, 3.3), (-9.8, 111.5, 2.9), (-12.6, 116, 2.5)]:
        d.shape("ground", circle(x + dx * k, dy, r), shadow=False)
    d.stroke("glow2", f"M{x - 3 * k} 132 C{x - 7 * k} 142 {x - 6 * k} 152 {x - 2 * k} 160", 2, line=False)


def hammock_feet(d: Drawing):
    d.disc("glow", 150, 64, 16)
    d.band("far", "M-30 108 L20 80 L52 98 L94 64 L130 94 L164 76 L230 104")
    for snow in ["M94 64 L105 75 L100 74 L94 79 L89 74 L84 75Z", "M164 76 L172 83 L168 83 L164 86 L160 82 L157 83Z"]:
        d.shape("light", snow, shadow=False)
    d.band("mid", hills(118, 6, 30))
    d.band("sky2", "M-30 124 Q100 118 230 124")
    d.stroke("mid", "M130 134 H164 M140 144 H176 M20 136 H44", 1.8, line=False)
    # bare feet propped up in the hammock
    group(d, "rotate(-9 82 184) translate(82 184) scale(1.3) translate(-82 -176)", lambda: _foot(d, 82, True))
    group(d, "rotate(9 118 184) translate(118 184) scale(1.3) translate(-118 -176)", lambda: _foot(d, 118, False))
    # hammock edge filling the bottom of the frame
    d.shape("hero", "M-30 230 V150 C30 168 70 174 100 172 C140 170 200 150 230 140 V230Z", spot=True)
    d.shape("hero2", "M-30 162 C30 180 80 188 120 184 C160 180 200 162 230 152 V160 C200 172 160 190 120 194 C80 198 30 190 -30 172Z", shadow=False)



def hammock_stars(d: Drawing):
    _night(d, [(30, 60, 2.4), (56, 30, 2.6), (100, 22, 2), (150, 30, 2.4), (178, 66, 2), (124, 52, 1.8), (20, 100, 1.6), (180, 100, 1.6)])
    _moon(d, 70, 52, 12)
    d.band("far", hills(150, 8, 20))
    for x, h, b in [(20, 70, 150), (184, 66, 152)]:
        d.shape("dark", _pine(x, b, h, h * .3), line=False)
    d.limb("dark", "M36 60 V176", 10)
    d.limb("dark", "M164 60 V176", 10)
    # tarp
    d.stroke("light", "M36 74 L164 74", 1.4)
    d.shape("hero2", "M100 74 L52 122 L148 122Z")
    d.shape("pop", "M100 74 L148 122 L120 122Z", shadow=False, line=False)
    d.stroke("light", "M52 122 L40 140 M148 122 L160 140", 1.2)
    # hammock under the tarp
    d.stroke("light", "M40 104 L62 118 M160 104 L138 118", 1.6)
    d.shape("hero", "M60 118 C74 152 126 152 140 118 C124 130 112 134 100 134 C88 134 76 130 60 118Z", spot=True)
    # lantern
    d.stroke("light", "M100 74 V94", 1.2)
    d.disc("glow2", 100, 100, 6)
    d.band("near", hills(176, 4), line=False)


# ================================================================ CROSS-COUNTRY SKIING
def xc_tracks(d: Drawing):
    d.disc("glow", 150, 56, 16)
    d.band("far", "M-30 106 L24 80 L58 98 L96 70 L134 96 L170 78 L230 102")
    for x in range(-12, 214, 12):
        d.shape("deep", _pine(x, 118 + (x % 3), 16 + (x * 7) % 8, 6), line=False)
    _line_only(d, "M-30 116 H230", 2.2)
    d.band("light", "M-30 118 Q100 114 230 118", shadow=True)
    # groomed classic tracks curving away
    for k in (-1, 1):
        o = k * 8
        d.stroke("mid", f"M{40 + o * 2} 230 C{60 + o * 2} 180 {130 + o} 166 {120 + o * .6} 146 C{112 + o * .4} 132 {92 + o * .2} 128 {96 + o * .2} 120", 2.6)
        d.stroke("mid", f"M{70 + o * 2} 230 C{90 + o * 2} 184 {148 + o} 168 {134 + o * .6} 146 C{124 + o * .4} 132 {104 + o * .2} 128 {104 + o * .2} 120", 2.6)
    for x, b, h in [(30, 176, 74), (180, 168, 66), (164, 186, 42)]:
        _snowy_pine(d, x, b, h, h * .32)


def xc_skier(d: Drawing):
    d.disc("glow", 104, 88, 46)
    d.band("far", "M-30 128 L22 104 L60 120 L98 96 L140 118 L176 100 L230 122")
    for x in range(-10, 210, 13):
        d.shape("deep", _pine(x, 140, 14 + (x * 7) % 8, 5.5), line=False)
    d.band("light", "M-30 142 Q100 136 230 142")
    d.stroke("mid", "M-30 160 Q100 154 230 160 M-30 166 Q100 160 230 166", 1.8)

    def skier():
        d.shape("hero2", _ski(20, 150, 92, 140, 4, 5), spot=True)
        d.shape("hero2", _ski(90, 152, 176, 152, 4, 6), spot=True)
        d.stroke("dark", "M76 104 L44 146", 2)
        d.limb("dark", "M98 108 L86 126 L68 138", 8)
        d.limb("dark", "M98 108 L116 126 L118 148", 8)
        d.shape("dark", "M110 146 L126 146 Q128 151 124 152 L110 152Z")
        d.shape("dark", "M60 134 L72 136 L70 144 L58 142Z")
        d.limb("hero", "M108 70 L98 108", 12)
        d.limb("hero", "M106 76 L94 88 L80 100", 5.5)
        d.limb("hero", "M108 78 L122 90 L134 90", 5.5)
        d.stroke("dark", "M134 88 L124 148", 2)
        d.shape("dark", circle(114, 58, 8))
        d.shape("pop", "M105 56 C105 44 122 44 123 54Z", shadow=False)
        d.shape("pop", circle(110, 44, 3.5), shadow=False)
    group(d, "translate(-4 0)", skier)
    d.band("light", "M-30 170 Q100 164 230 170", line=False)


def xc_skis(d: Drawing):
    d.disc("glow", 52, 58, 16)
    d.band("far", "M-30 112 L20 84 L54 102 L96 72 L132 98 L168 80 L230 108")
    for x, b, h in [(150, 140, 76), (176, 146, 56), (24, 146, 50)]:
        _snowy_pine(d, x, b, h, h * .32)
    d.band("light", "M-30 150 Q60 136 120 144 T230 140")
    # two skinny skis standing in the snow
    d.shape("hero", "M84 160 L90 32 Q93 22 96 32 L96 160Z", spot=True)
    d.shape("hero2", "M104 160 L106 32 Q110 22 112 32 L118 160Z", spot=True)
    d.shape("dark", rrect(86, 104, 11, 8, 2), shadow=False)
    d.shape("dark", rrect(105, 104, 11, 8, 2), shadow=False)
    # crossed poles with baskets
    d.stroke("dark", "M58 160 L138 40 M142 160 L62 40", 2.6)
    for x, y in [(62, 40), (138, 40)]:
        d.shape("pop", rrect(x - 3, y - 4, 6, 14, 2.5))
    d.stroke("dark", "M58 160 L58 160", 0, line=False)
    for x, y in [(66, 148), (134, 148)]:
        d.stroke("dark", circle(x, y, 6), 1.8)
    d.band("light", "M-30 158 Q100 148 230 160")
    d.stroke("mid", "M30 172 Q60 168 80 174 M120 176 Q150 170 170 176", 2, line=False)


# ================================================================ SKI TOURING
def tour_skintrack(d: Drawing):
    d.disc("glow", 50, 50, 14)
    d.band("far", "M-30 122 L20 96 L50 110 L230 100")
    # big mountain with a rocky rim so the snow never meets the sky directly
    d.shape("mid", "M-10 190 L60 96 L100 36 L114 44 L132 70 L210 190Z")
    d.shape("light", "M-4 190 L62 102 L100 46 L112 54 L120 72 L112 76 L130 80 L200 190Z", shadow=False)
    d.shape("far", "M100 46 L112 54 L120 72 L112 76 L130 80 L150 112 L132 102 L118 86 L104 78Z", shadow=False, line=False)
    # zig-zag skin track
    d.stroke("mid", "M60 190 L140 168 L74 150 L128 134 L86 118 L118 104 L98 92 L110 80 L102 66", 2)
    # skier with pack, small
    def skier():
        d.shape("hero2", _ski(-12, 2, 14, -4, 3, 4), spot=True)
        d.limb("dark", "M0 -10 L-2 0 M2 -10 L6 -2", 3.2)
        d.shape("hero", rrect(-4, -24, 9, 16, 3.5))
        d.shape("pop", rrect(-9, -22, 7, 12, 2.5))
        d.shape("dark", circle(1, -28, 3.6))
        d.stroke("dark", "M6 -16 L10 0", 1.2)
    group(d, "translate(108 108) scale(1.2)", skier)
    d.band("light", "M-30 182 Q100 172 230 182", line=False)


def tour_hut(d: Drawing):
    d.disc("glow", 150, 52, 15)
    d.band("far", "M-30 112 L16 82 L44 100 L84 58 L118 96 L150 76 L190 104 L230 92")
    for snow in ["M84 58 L96 71 L90 70 L84 75 L78 70 L72 71Z", "M150 76 L159 85 L155 84 L150 88 L145 84 L142 85Z",
                 "M16 82 L23 89 L19 88 L15 91 L11 87Z"]:
        d.shape("light", snow, shadow=False)
    d.band("mid", hills(124, 6, -20))
    # stone hut
    d.shape("near", rrect(54, 104, 84, 50, 2))
    d.stroke("deep", "M54 118 H138 M54 132 H138 M70 104 V118 M100 104 V118 M124 104 V118 M84 118 V132 M114 118 V132", 1.4, line=False)
    d.shape("hero", "M44 108 L96 72 L148 108 L140 110 L96 80 L52 110Z", spot=True)
    d.shape("light", "M46 104 L96 68 L146 104 L140 106 L96 76 L52 106Z", shadow=False)
    d.shape("dark", rrect(86, 124, 18, 30, 2), shadow=False)
    d.shape("glow2", rrect(62, 124, 14, 12, 2), shadow=False)
    d.shape("glow2", rrect(114, 124, 14, 12, 2), shadow=False)
    d.shape("dark", rrect(120, 76, 8, 16, 1))
    # skis stuck in the snow beside the hut
    d.shape("pop", _bar(156, 158, 160, 92, 5))
    d.shape("hero2", _bar(168, 158, 164, 92, 5))
    d.stroke("dark", "M150 158 L170 98 M178 158 L158 98", 1.6)
    d.band("light", "M-30 152 Q100 144 230 156")
    d.stroke("mid", "M60 172 Q100 166 130 176", 2, line=False)


def tour_pack(d: Drawing):
    d.disc("glow", 100, 96, 60)
    d.band("far", "M-30 132 L20 104 L52 120 L94 84 L130 112 L166 94 L230 124")
    for snow in ["M94 84 L106 95 L100 94 L94 99 L88 94 L82 95Z"]:
        d.shape("light", snow, shadow=False)
    d.band("light", hills(162, 6, 20))
    # skis A-framed on the pack
    d.shape("hero2", _bar(58, 160, 90, 22, 8), spot=True)
    d.shape("hero2", _bar(142, 160, 110, 22, 8), spot=True)
    d.shape("dark", "M86 26 Q90 14 96 22Z M114 26 Q110 14 104 22Z", line=False)
    # shovel handle
    d.shape("dark", _bar(100, 60, 100, 34, 5))
    d.shape("dark", rrect(92, 30, 16, 6, 3))
    # pack
    d.shape("hero", "M66 70 C66 56 80 50 100 50 C120 50 134 56 134 70 L138 150 Q138 160 128 160 H72 Q62 160 62 150Z")
    d.shape("hero", "M66 70 C68 58 80 52 100 52 C120 52 132 58 134 70 C128 76 116 80 100 80 C84 80 72 76 66 70Z", shadow=False)
    d.shape("pop", rrect(76, 104, 48, 36, 8))
    d.stroke("dark", "M76 116 H124", 1.6)
    d.shape("dark", rrect(56, 88, 88, 8, 3))
    d.shape("dark", rrect(58, 132, 84, 8, 3))
    d.shape("light", rrect(96, 86, 8, 12, 2), shadow=False)


# ================================================================ HELI-SKIING
def heli_dropoff(d: Drawing):
    d.disc("glow", 46, 50, 14)
    # sea of peaks below
    d.band("far", "M-30 138 L10 116 L36 130 L64 108 L92 132 L120 112 L150 134 L182 110 L230 132")
    for x, y in [(10, 116), (64, 108), (120, 112), (182, 110)]:
        d.shape("light", f"M{x} {y} L{x + 9} {y + 8} L{x + 4} {y + 7} L{x} {y + 11} L{x - 4} {y + 7} L{x - 9} {y + 8}Z", shadow=False)
    d.band("mid", "M-30 166 L20 140 L60 150 L230 146", line=False)
    # summit plateau of snow on a rocky base
    d.shape("deep", "M-30 230 V160 L30 136 H170 L230 158 V230Z")
    d.shape("light", "M-30 230 V166 L30 140 H170 L230 164 V230Z", shadow=False)
    group(d, "translate(100 124) scale(.62) translate(-104 -104)", lambda: _heli(d))
    # skis stuck upright beside it
    d.shape("pop", _bar(160, 150, 164, 104, 4.5))
    d.shape("hero2", _bar(170, 150, 168, 104, 4.5))
    d.stroke("mid", "M20 176 Q60 170 90 180 M120 184 Q150 176 180 182", 2, line=False)


def heli_powder(d: Drawing):
    d.band("far", "M-30 110 L10 82 L44 102 L84 52 L120 92 L150 70 L230 110")
    for snow in ["M84 52 L96 66 L90 64 L84 70 L78 64 L72 66Z", "M150 70 L159 80 L154 79 L150 83 L146 79 L142 80Z"]:
        d.shape("light", snow, shadow=False)
    group(d, "translate(150 40) scale(.36) translate(-104 -100)", lambda: _heli(d))
    # steep powder slope
    d.shape("mid", "M-30 230 V120 L230 196 V230Z", line=False)
    d.shape("light", "M-30 230 V126 L230 202 V230Z", shadow=False)
    _line_only(d, "M-30 124 L230 200", 3)
    # powder plume behind the skier
    for x, y, r in [(54, 118, 16), (36, 104, 14), (70, 104, 12), (22, 122, 13), (48, 90, 10)]:
        d.shape("light", circle(x, y, r))

    def skier():
        d.shape("hero2", _ski(60, 146, 134, 154, 5), spot=True)
        d.shape("hero2", _ski(70, 156, 144, 164, 5), spot=True)
        d.limb("dark", "M98 120 L88 134 L96 154 M98 120 L110 134 L118 156", 8)
        d.limb("hero", "M104 92 L98 122", 13)
        d.limb("hero", "M104 98 L122 104 L132 98 M100 98 L82 110 L72 108", 5.5)
        d.stroke("dark", "M132 98 L144 140 M72 108 L66 140", 1.8)
        d.shape("pop", circle(108, 82, 8.5))
        d.shape("dark", rrect(108, 78, 10, 5, 2.5), shadow=False)
    group(d, "rotate(18 100 130) translate(0 -10)", skier)


def heli_lines(d: Drawing):
    d.disc("glow", 156, 46, 14)
    d.band("far", "M-30 116 L230 104", line=False)
    d.shape("mid", "M-30 190 L40 90 L96 34 L112 46 L140 76 L230 150 V190Z")
    d.shape("light", "M-24 190 L44 96 L96 44 L108 52 L104 66 L120 70 L136 86 L226 156 L230 190Z", shadow=False)
    d.shape("far", "M96 44 L108 52 L104 66 L120 70 L136 86 L160 110 L132 96 L112 80 L98 76Z", shadow=False, line=False)
    # snaking first tracks from the summit
    for dx in (-14, 0, 14):
        x0 = 100 + dx
        pts = f"M{x0} 58 " + " ".join(f"Q{x0 + (16 if i % 2 == 0 else -16) + dx * i * .3:.1f} {66 + i * 22} {x0 + dx * (i + 1) * .3:.1f} {76 + i * 22}" for i in range(6))
        d.stroke("mid", pts, 1.8)
    group(d, "translate(56 52) scale(.3) translate(-104 -100)", lambda: _heli(d))
    d.band("light", "M-30 184 Q100 176 230 184", line=False)


# ================================================================ SNOWSHOEING
SNOWSHOE = ("M0 -52 C16 -52 22 -30 22 -6 C22 18 14 36 6 52 L-6 52 C-14 36 -22 18 -22 -6 C-22 -30 -16 -52 0 -52Z")


def _snowshoe(d: Drawing, deck="hero", frame="dark", strap="pop"):
    d.shape(frame, SNOWSHOE)
    d.shape(deck, "M0 -46 C12 -46 17 -28 17 -6 C17 16 10 32 4 46 L-4 46 C-10 32 -17 16 -17 -6 C-17 -28 -12 -46 0 -46Z", shadow=False, spot=True)
    d.stroke(frame, "M-17 -18 H17 M-16 16 H16", 2.2)
    d.shape(strap, rrect(-12, -12, 24, 7, 2.5), shadow=False)
    d.shape(strap, rrect(-10, 2, 20, 6, 2.5), shadow=False)
    d.shape(frame, "M-10 -2 L-12 6 L-6 4 L-4 10 L0 4 L4 10 L6 4 L12 6 L10 -2Z", shadow=False)


def snowshoe_pair(d: Drawing):
    d.disc("glow", 100, 92, 58)
    d.band("far", "M-30 120 L20 92 L56 110 L100 76 L140 104 L176 88 L230 112")
    for x, b, h in [(24, 150, 60), (178, 152, 64)]:
        _snowy_pine(d, x, b, h, h * .32)
    group(d, "translate(80 100) rotate(-16)", lambda: _snowshoe(d))
    group(d, "translate(122 102) rotate(14)", lambda: _snowshoe(d, deck="hero2"))
    d.band("light", "M-30 150 Q50 140 100 146 T230 144")
    d.stroke("mid", "M40 168 Q70 162 92 170 M118 172 Q146 164 168 172", 2, line=False)


def snowshoe_hiker(d: Drawing):
    d.disc("glow", 140, 62, 16)
    d.band("far", "M-30 112 L18 84 L52 102 L92 70 L128 98 L164 80 L230 106")
    for x, b, h in [(26, 136, 70), (176, 132, 62), (44, 140, 44)]:
        _snowy_pine(d, x, b, h, h * .32)
    d.band("light", "M-30 134 Q100 126 230 134")
    # trail of prints behind
    for x, y, s in [(52, 176, 1), (36, 166, .9), (64, 160, .85), (48, 152, .75), (72, 146, .7)]:
        d.shape("mid", ellipse(x, y, 6 * s, 2.6 * s), shadow=False)

    def hiker():
        d.limb("dark", "M98 118 L90 136 L86 154 M102 118 L112 134 L118 152", 8)
        d.shape("hero2", ellipse(84, 156, 13, 4.5), spot=True)
        d.shape("hero2", ellipse(120, 154, 13, 4.5), spot=True)
        d.limb("hero", "M100 84 L100 120", 14)
        d.shape("pop", rrect(84, 82, 12, 26, 4))
        d.limb("hero", "M102 90 L114 104 L122 100 M98 92 L90 108 L82 112", 5.5)
        d.stroke("dark", "M122 98 L130 152 M82 110 L74 152", 2)
        d.shape("dark", circle(102, 72, 8))
        d.shape("pop", "M94 70 C94 58 110 58 111 68Z", shadow=False)
        d.shape("pop", circle(102, 58, 3.2), shadow=False)
    group(d, "translate(6 2)", hiker)
    _flakes(d, [(150, 100, 3), (170, 120, 2.5), (30, 70, 3), (60, 50, 2.5)])
    d.band("light", "M-30 174 Q100 166 230 174", line=False)


PRINT = "M0 -11 C5 -11 7 -5 7 0 C7 6 3 10 0 12 C-3 10 -7 6 -7 0 C-7 -5 -5 -11 0 -11Z"


def snowshoe_tracks(d: Drawing):
    d.disc("glow", 150, 52, 16)
    d.band("far", "M-30 112 L24 86 L60 104 L100 78 L140 104 L176 88 L230 110")
    for x in range(-14, 214, 10):
        d.shape("deep", _pine(x, 122 + (x % 3), 18 + (x * 7) % 10, 6), line=False)
    d.band("light", "M-30 122 Q100 116 230 122")
    for x, b, h in [(22, 168, 84), (184, 176, 76)]:
        _snowy_pine(d, x, b, h, h * .3)
    # a line of snowshoe prints running away into the forest
    for x, y, s in [(84, 182, 1.25), (116, 158, .95), (90, 142, .72), (110, 132, .55), (96, 126, .42)]:
        def g():
            d.shape("mid", SNOWSHOE, shadow=False)
            d.stroke("light", "M-14 -18 H14 M-14 14 H14", 4, line=False)
            d.shape("near", "M-9 -6 L-11 6 L-4 3 L0 10 L4 3 L11 6 L9 -6Z", shadow=False, line=False)
        group(d, f"translate({x} {y}) scale({s * .55:.2f} {s * .32:.2f})", g)




# ================================================================ concept list
NIGHT = ["dusk", "coastal", "blush", "meadow"]
JUNGLE = ["meadow", "coastal", "dusk", "golden", "blush"]
MONKEY_C = {"hero": "#6B4226", "hero2": "#E3B98A", "mark": "#2A1A10"}
GREEN = {"far": "#A8D5A2", "mid": "#6DB37A", "near": "#3E8E5A", "deep": "#245C3C"}
SKIN = {"ground": "#EDB98F", "glow2": "#C98E68"}
CANYON = {"far": "#F0B27A", "mid": "#D9784A", "near": "#B04F2E", "deep": "#6E2E22"}
WATER = ["coastal", "meadow", "dusk", "blush"]

CONCEPTS = [
    Concept("wildcamp-lakeside", "wild-camping", "Lakeside pitch", wild_lake, WATER,
            checks=[("hero", "near"), ("hero2", "near"), ("hero", "sky2"), ("hero2", "sky2"), ("deep", "near"), ("hero", "hero2")],
            fixes={"hero2": ["light", "glow2", "pop"], "hero": ["pop", "hero2"]}),
    Concept("wildcamp-stove", "wild-camping", "Camp stove brew", wild_stove,
            checks=[("hero", "glow"), ("hero2", "ground"), ("dark", "glow"), ("pop", "hero"), ("light", "glow")],
            fixes={"glow": ["glow2", "far", "sky2"], "pop": ["hero2", "light"], "ground": ["mid", "near"]}),
    Concept("wildcamp-bivvy", "wild-camping", "Bivvy under the stars", wild_bivvy, NIGHT,
            checks=[("hero", "near"), ("dark", "near"), ("far", "deep"), ("near", "far"), ("light", "deep")],
            fixes={"far": ["mid", "near"], "near": ["mid", "far"]}),
    Concept("canyon-slot", "canyon-hike", "Slot canyon", canyon_slot, overrides=CANYON,
            checks=[("far", "mid"), ("mid", "near"), ("hero", "ground"), ("far", "sky")],
            fixes={"hero": ["pop", "dark"]}),
    Concept("canyon-switchbacks", "canyon-hike", "Canyon switchbacks", canyon_switchback, overrides={**CANYON, "sky2": "#7CC6D9"},
            checks=[("ground", "deep"), ("hero", "deep"), ("near", "mid"), ("far", "sky"), ("deep", "near"), ("sky2", "far")],
            fixes={"hero": ["pop", "light"]}),
    Concept("canyon-arch", "canyon-hike", "Sandstone arch", canyon_arch,
            checks=[("near", "glow"), ("near", "sky"), ("near", "far"), ("near", "ground")],
            fixes={"glow": ["glow2", "light", "sky2"]}),
    Concept("jungle-temple", "jungle-trek", "Temple in the jungle", jungle_temple, JUNGLE, overrides={**GREEN, "ground": "#D8C9A3"},
            checks=[("ground", "sky"), ("ground", "far"), ("near", "ground"), ("mid", "ground")],
            fixes={"ground": ["light", "glow2"]}),
    Concept("jungle-monkey", "jungle-trek", "Spider monkey", jungle_monkey, JUNGLE, overrides=MONKEY_C,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "mid"), ("hero", "glow"), ("deep", "sky")]),
    Concept("jungle-boots", "jungle-trek", "Muddy boots", jungle_boots, JUNGLE, overrides={**GREEN, "ground": "#8A5A3B", "deep": "#5A3A26"},
            checks=[("hero", "mid"), ("hero2", "mid"), ("hero", "far"), ("hero2", "far"), ("hero", "hero2"), ("hero", "deep"), ("hero2", "deep")],
            fixes={"hero2": ["light", "glow2"], "hero": ["pop", "dark"]}),
    Concept("trailrun-shoe", "trail-running", "Trail shoe", trail_shoe,
            checks=[("hero", "glow"), ("hero", "far"), ("hero", "mid"), ("hero2", "hero")],
            fixes={"glow": ["glow2", "sky2", "light"], "hero2": ["light", "pop"]}),
    Concept("trailrun-ridge", "trail-running", "Ridge runner", trail_ridge,
            checks=[("hero", "glow"), ("dark", "glow"), ("near", "glow"), ("near", "far"), ("hero", "sky")],
            fixes={"glow": ["glow2", "far", "light"], "hero": ["pop", "light"]}),
    Concept("trailrun-watch", "trail-running", "GPS watch", trail_watch,
            checks=[("hero", "far"), ("hero", "sky"), ("dark", "far"), ("glow", "deep"), ("hero", "mid")],
            fixes={"hero": ["pop", "hero2"]}),
    Concept("marathon-finish", "marathon", "Finish line", marathon_finish,
            checks=[("hero", "sky"), ("hero", "far"), ("pop", "sky"), ("pop", "hero"), ("dark", "mid")],
            fixes={"pop": ["hero2", "deep"]}),
    Concept("marathon-medal", "marathon", "Finisher medal", marathon_medal, overrides={"hero2": "#E9B52F", "glow": "#F7D774", "mark": "#3A2E1A"},
            checks=[("hero2", "sky2"), ("hero", "sky2"), ("pop", "sky2"), ("hero", "pop"), ("hero2", "glow2")],
            fixes={"pop": ["deep", "mark"], "glow2": ["light", "far"]}),
    Concept("marathon-bib", "marathon", "Race bib", marathon_bib,
            checks=[("hero", "glow"), ("light", "hero"), ("pop", "light"), ("hero", "sky")],
            fixes={"glow": ["glow2", "far", "sky2"]}),
    Concept("cavetube-mouth", "cave-tubing", "Out of the cave", cavetube_mouth, WATER,
            checks=[("hero", "sky2"), ("mid", "sky"), ("dark", "mid"), ("sky2", "near"), ("mid", "far")],
            fixes={"hero": ["pop", "hero2"], "far": ["near", "deep"]}),
    Concept("cavetube-dark", "cave-tubing", "Headlamps underground", cavetube_dark, WATER,
            checks=[("hero", "mid"), ("near", "deep"), ("mid", "deep"), ("hero2", "mid")],
            fixes={"hero": ["pop", "hero2"], "hero2": ["light", "glow2"]}),
    Concept("cavetube-ring", "cave-tubing", "Tube & headlamp", cavetube_ring, WATER,
            checks=[("hero", "mid"), ("hero", "far"), ("near", "deep"), ("mid", "deep")],
            fixes={"hero": ["pop", "hero2"]}),
    Concept("hammock-forest", "hammock-camping", "Hammock in the woods", hammock_forest,
            checks=[("hero", "mid"), ("hero", "ground"), ("hero", "far"), ("deep", "sky"), ("hero2", "hero"), ("pop", "hero")],
            fixes={"hero": ["pop", "deep"], "hero2": ["light", "glow2"], "pop": ["hero2", "light"]}),
    Concept("hammock-view", "hammock-camping", "Feet up with a view", hammock_feet, WATER, overrides=SKIN,
            checks=[("hero", "sky2"), ("ground", "sky2"), ("ground", "mid"), ("ground", "hero"), ("hero", "mid"), ("ground", "far")],
            fixes={"hero": ["deep", "near", "pop"]}),
    Concept("hammock-stars", "hammock-camping", "Hammock under the stars", hammock_stars, NIGHT,
            checks=[("hero", "deep"), ("hero2", "deep"), ("hero", "far"), ("dark", "far"), ("far", "deep")],
            fixes={"far": ["mid", "near"], "hero2": ["light", "glow2"]}),
    Concept("xc-tracks", "cross-country-skiing", "Groomed tracks", xc_tracks,
            checks=[("light", "far"), ("mid", "light"), ("deep", "light"), ("far", "sky")],
            fixes={"far": ["mid", "near"]}),
    Concept("xc-skier", "cross-country-skiing", "Classic stride", xc_skier,
            checks=[("hero", "glow"), ("dark", "glow"), ("hero2", "light"), ("light", "far"), ("hero", "light")],
            fixes={"glow": ["glow2", "far", "sky2"], "hero2": ["pop", "hero"]}),
    Concept("xc-skis", "cross-country-skiing", "Skinny skis", xc_skis,
            checks=[("hero", "sky"), ("hero2", "sky"), ("hero", "far"), ("hero2", "far"), ("light", "far"), ("hero2", "light")],
            fixes={"hero2": ["pop", "deep"], "hero": ["pop", "deep"]}),
    Concept("skitour-skintrack", "ski-touring", "Skin track", tour_skintrack,
            checks=[("mid", "sky"), ("light", "mid"), ("mid", "light"), ("hero", "light"), ("far", "sky")],
            fixes={"far": ["near"]}),
    Concept("skitour-hut", "ski-touring", "Mountain hut", tour_hut,
            checks=[("near", "mid"), ("hero", "far"), ("light", "far"), ("light", "mid"), ("pop", "light"), ("hero2", "light")],
            fixes={"hero2": ["pop", "deep"], "near": ["deep", "far"]}),
    Concept("skitour-pack", "ski-touring", "Skis on the pack", tour_pack,
            checks=[("hero", "glow"), ("hero2", "glow"), ("hero2", "far"), ("pop", "hero"), ("hero", "light")],
            fixes={"glow": ["glow2", "far", "sky2"], "hero2": ["light", "pop"], "pop": ["hero2", "light"]}),
    Concept("heliski-dropoff", "heli-skiing", "Summit drop-off", heli_dropoff,
            checks=[("hero", "sky"), ("hero", "light"), ("light", "far"), ("far", "sky"), ("pop", "light")],
            fixes={"far": ["mid", "near"]}),
    Concept("heliski-powder", "heli-skiing", "Powder turn", heli_powder,
            checks=[("hero", "light"), ("light", "far"), ("hero", "far"), ("hero2", "light"), ("far", "sky")],
            fixes={"far": ["mid", "near"], "hero2": ["pop", "deep"]}),
    Concept("heliski-lines", "heli-skiing", "First tracks", heli_lines,
            checks=[("mid", "sky"), ("light", "mid"), ("hero", "sky"), ("mid", "light")]),
    Concept("snowshoe-pair", "snowshoeing", "Snowshoes", snowshoe_pair,
            checks=[("hero", "glow"), ("dark", "glow"), ("hero2", "glow"), ("light", "far")],
            fixes={"glow": ["glow2", "far", "sky2"], "hero2": ["pop", "light"]}),
    Concept("snowshoe-hiker", "snowshoeing", "Snowshoe hike", snowshoe_hiker,
            checks=[("hero", "light"), ("hero", "far"), ("light", "far"), ("hero2", "light"), ("deep", "light")],
            fixes={"hero2": ["pop", "deep"]}),
    Concept("snowshoe-tracks", "snowshoeing", "Snowshoe tracks", snowshoe_tracks,
            checks=[("mid", "light"), ("light", "far"), ("deep", "light"), ("glow", "sky")],
            fixes={"mid": ["near", "far"], "glow": ["glow2", "far"]}),
]
