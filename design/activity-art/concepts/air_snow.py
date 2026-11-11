"""Air and snow activities: three concepts each for skydiving, paragliding, parasailing,
helicopter tours, seaplanes, zip-lining, bungee, skiing, snowboarding, dog-sledding,
snowmobiling, ice-skating, northern lights and apres-ski."""
from _common import *  # noqa: F401,F403
from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group


# ================================================================ private helpers
def _q(p0, p1, p2, t):
    a, b = (1 - t) ** 2, 2 * (1 - t) * t
    c = t * t
    return a * p0[0] + b * p1[0] + c * p2[0], a * p0[1] + b * p1[1] + c * p2[1]


def _poly(pts, close=True):
    s = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    return s + ("Z" if close else "")


def _wing(d: Drawing, top, bot, n, base="hero", alt="hero2", spot=True, lines_to=None, line_role="dark", lw=0.9):
    """A ram-air wing between two quadratic curves, split into n cells of alternating colour."""
    tp = [_q(*top, i / n) for i in range(n + 1)]
    bp = [_q(*bot, i / n) for i in range(n + 1)]
    if lines_to:
        for i in range(0, n + 1, 2 if n > 6 else 1):
            tx, ty = lines_to[0] if i <= n / 2 else lines_to[1]
            d.stroke(line_role, f"M{bp[i][0]:.1f} {bp[i][1]:.1f} L{tx} {ty}", lw)
    d.shape(base, _poly(tp + bp[::-1]))
    for i in range(1, n, 2):
        d.shape(alt, _poly([tp[i], tp[i + 1], bp[i + 1], bp[i]]), shadow=False, spot=spot)


def _line_only(d: Drawing, path: str, w: float = 2.4):
    """An extra line drawn only in line style, clipped to the circle like the bands."""
    if not d.paper:
        d.bands.append(f'<path d="{path}" fill="none" stroke="{d.c["ink"]}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')


def _bar(x1, y1, x2, y2, w):
    """A straight rounded bar as a filled path (shadow filters clip thin, straight strokes)."""
    import math
    dx, dy = x2 - x1, y2 - y1
    n = math.hypot(dx, dy) or 1
    nx, ny = -dy / n * w / 2, dx / n * w / 2
    r = w / 2
    return (f"M{x1+nx:.1f} {y1+ny:.1f} L{x2+nx:.1f} {y2+ny:.1f} A{r} {r} 0 0 0 {x2-nx:.1f} {y2-ny:.1f} "
            f"L{x1-nx:.1f} {y1-ny:.1f} A{r} {r} 0 0 0 {x1+nx:.1f} {y1+ny:.1f}Z")


def _land(d: Drawing, role: str, shape: str, edge: str, shadow: bool = True):
    """A landmass that runs off the canvas: a filled shape in papercut, just its edge (clipped) in line style."""
    d.shape(role, shape, shadow=shadow, line=False)
    _line_only(d, edge, 3)


def _pine(x, y, h, w=None):
    """A three-tier pine standing on (x, y)."""
    w = w or h * 0.55
    t = y - h
    return (f"M{x} {t} L{x + w*0.32:.1f} {t + h*0.34:.1f} L{x + w*0.2:.1f} {t + h*0.34:.1f} L{x + w*0.42:.1f} {t + h*0.64:.1f} "
            f"L{x + w*0.26:.1f} {t + h*0.64:.1f} L{x + w*0.5:.1f} {y - h*0.1:.1f} L{x + w*0.08:.1f} {y - h*0.1:.1f} L{x + w*0.08:.1f} {y} "
            f"L{x - w*0.08:.1f} {y} L{x - w*0.08:.1f} {y - h*0.1:.1f} L{x - w*0.5:.1f} {y - h*0.1:.1f} L{x - w*0.26:.1f} {t + h*0.64:.1f} "
            f"L{x - w*0.42:.1f} {t + h*0.64:.1f} L{x - w*0.2:.1f} {t + h*0.34:.1f} L{x - w*0.32:.1f} {t + h*0.34:.1f}Z")


def _flier(d: Drawing, suit="hero", helmet="hero2", pack="dark"):
    """A skydiver seen from above in a belly-to-earth star, centred on (100, 100)."""
    d.limb(suit, "M90 90 L68 84 L60 64", 9)
    d.limb(suit, "M110 90 L132 84 L140 64", 9)
    d.limb(suit, "M94 118 L76 132 L74 154", 10)
    d.limb(suit, "M106 118 L124 132 L126 154", 10)
    for x, y in [(60, 62), (140, 62)]:
        d.marks("dark", circle(x, y, 4.2))
    for x in (74, 126):
        d.shape("dark", rrect(x - 5, 150, 10, 11, 4), shadow=False)
    d.shape(suit, rrect(86, 82, 28, 42, 13))
    d.shape(pack, rrect(90, 88, 20, 26, 6), shadow=False, spot=True)
    d.shape("pop", rrect(96, 110, 8, 4, 2), shadow=False)
    d.shape(helmet, circle(100, 74, 11))
    d.stroke("dark", "M91 70 Q100 64 109 70", 2)


def _seated_pilot(d: Drawing, x, y, s=1.0, body="dark", helmet="pop"):
    """A small seated figure in a harness, hanging from (x, y)."""
    def fig():
        d.limb(body, "M2 14 L14 18 L16 30", 5)
        d.shape(body, rrect(-5, 4, 11, 16, 5))
        d.limb(body, "M-2 8 L-6 -2", 3.5, shadow=False)
        d.limb(body, "M4 8 L8 -2", 3.5, shadow=False)
        d.shape(helmet, circle(0, 0, 5.2))
    group(d, f"translate({x} {y}) scale({s})", fig)


def _hanging_rider(d: Drawing, x, y, s=1.0, body="dark", helmet="pop"):
    """A small figure hanging upright in a harness from (x, y), legs dangling."""
    def fig():
        d.limb(body, "M-3 18 L-4 32 M3 18 L5 32", 4.2)
        d.shape(body, rrect(-5.5, 5, 11, 16, 5))
        d.limb(body, "M-4 9 L-8 -4 M4 9 L8 -4", 3.4, shadow=False)
        d.shape(helmet, circle(0, 0, 5.4))
    group(d, f"translate({x} {y}) scale({s})", fig)


# ================================================================ SKYDIVING
def sky_freefall(d: Drawing):
    def fields():
        roles = ["far", "mid", "ground", "near", "glow2", "mid", "far", "ground", "near"]
        k = 0
        for gy in range(-60, 260, 46):
            for gx in range(-60, 260, 52):
                d.shape(roles[k % len(roles)], rrect(gx, gy, 50, 44, 3), shadow=False, line=False)
                k += 1
            k += 2
    group(d, "rotate(18 100 100)", fields)
    d.stroke("light", "M-10 40 C40 60 60 30 100 50 S160 40 210 20", 5, line=False)
    _line_only(d, "M-10 40 C40 60 60 30 100 50 S160 40 210 20", 2)
    for e in ["M-30 128 L230 192", "M150 -10 L110 230"]:
        _line_only(d, e, 1.6)
    d.shape("light", cloud(26, 160, 1.2))
    d.shape("light", cloud(138, 46, 1.0))
    d.shape("light", cloud(136, 166, 1.0))
    group(d, "rotate(-14 100 108) translate(100 110) scale(1.05) translate(-100 -100)", lambda: _flier(d))


def sky_canopy(d: Drawing):
    d.disc("glow", 160, 70, 18)
    d.band("far", waves(132, 3, 40))
    _land(d, "ground", "M-30 128 C10 126 40 130 58 146 C72 160 74 186 70 230 L-30 230Z", "M-30 128 C10 126 40 130 58 146 C72 160 74 186 70 230")
    d.shape("near", "M-30 134 C6 132 34 136 48 150 C60 162 60 190 56 230 L-30 230Z", shadow=False, line=False)
    d.stroke("light", "M60 142 C74 156 78 176 76 200", 2.5, line=False)
    d.band("mid", "M70 184 Q140 176 230 186", line=False)
    d.shape("light", cloud(128, 112, 0.8))
    _wing(d, ((34, 62), (100, 22), (166, 62)), ((40, 72), (100, 36), (160, 72)), 9,
          lines_to=[(96, 118), (104, 118)])
    _hanging_rider(d, 100, 122, 1.25, body="dark", helmet="pop")


PLANE = ("M24 74 C24 64 34 60 48 60 L138 60 L160 44 L172 44 L170 62 C168 70 160 74 150 74 L48 82 C34 82 24 80 24 74Z")


def sky_plane(d: Drawing):
    d.shape("light", cloud(-6, 186, 1.8))
    d.shape("light", cloud(126, 190, 1.5))
    d.band("far", hills(196, 4), line=False)
    d.shape("light", cloud(150, 112, 0.7))
    d.stroke("dark", "M66 60 L72 50 M98 60 L92 50", 1.6)
    d.shape("hero", PLANE)
    d.shape("hero2", "M150 44 L160 44 L170 62 C168 70 160 74 150 74 L144 74 Z", shadow=False, spot=True)
    d.shape("hero2", "M36 72 L132 66 L132 70 L40 77Z", shadow=False, spot=True)
    d.shape("dark", rrect(52, 47, 64, 5, 2.5))
    for x in (44, 58, 72, 86):
        d.shape("light", rrect(x, 63, 8, 6, 2), shadow=False)
    d.shape("dark", rrect(108, 62, 15, 12, 2), shadow=False)
    d.shape("dark", ellipse(21, 72, 2.5, 13))
    d.stroke("dark", "M54 80 L50 90 M70 79 L72 90", 2)
    d.marks("dark", circle(50, 91, 3.5) + circle(72, 91, 3.5))
    group(d, "translate(86 128) rotate(-20) scale(.48) translate(-100 -100)", lambda: _flier(d, suit="pop", helmet="light"))
    group(d, "translate(150 136) scale(.42)", lambda: (
        _wing(d, ((-34, -20), (0, -46), (34, -20)), ((-30, -12), (0, -34), (30, -12)), 5, base="hero", alt="hero2",
              spot=False, lines_to=[(-2, 22), (2, 22)], lw=1.8),
        _hanging_rider(d, 0, 24, 1.2)))


# ================================================================ PARAGLIDING
def para_alps(d: Drawing):
    d.disc("glow", 46, 56, 16)
    d.band("far", "M-30 126 L18 100 L46 116 L84 70 L112 102 L140 80 L176 112 L230 96")
    for snow in ["M84 70 L96 84 L90 82 L85 88 L79 82 L74 84Z", "M140 80 L150 91 L145 90 L140 95 L134 90 L130 92Z",
                 "M18 100 L27 109 L21 108 L17 112 L12 106Z"]:
        d.shape("light", snow, shadow=False)
    d.band("mid", hills(140, 16, 10))
    d.band("near", hills(162, 10, -20))
    for x, y, h in [(30, 170, 22), (44, 174, 18), (160, 168, 20), (172, 172, 16)]:
        d.shape("deep", _pine(x, y, h))
    d.band("deep", hills(182, 5, 30), line=False)
    _wing(d, ((86, 50), (128, 22), (172, 52)), ((90, 56), (128, 32), (166, 58)), 7,
          lines_to=[(126, 88), (130, 88)])
    _seated_pilot(d, 128, 90, 0.95)
    group(d, "translate(44 106) scale(.4)", lambda: (
        _wing(d, ((-34, -10), (0, -34), (34, -10)), ((-30, -4), (0, -24), (30, -4)), 5, base="pop", alt="light",
              spot=False, lines_to=[(-1, 24), (1, 24)], lw=2), _seated_pilot(d, 0, 26, 1.0)))


def para_launch(d: Drawing):
    d.shape("light", cloud(18, 70, 1.1))
    d.band("far", hills(150, 12, 30))
    d.band("mid", "M-30 120 C20 118 70 128 110 150 C130 162 150 166 230 168", line=True)
    d.band("near", "M-30 150 C30 150 70 160 100 176 C120 186 160 190 230 190")
    # windsock on its pole
    d.shape("dark", _bar(40, 150, 40, 100, 3.5))
    d.shape("pop", "M42 100 L72 104 L70 116 L42 120Z", spot=True)
    d.shape("light", "M50 101.2 L58 102.3 L58 117.6 L50 118.6Z", shadow=False)
    d.shape("light", "M64 103 L70 103.9 L70 116 L64 116.6Z", shadow=False)
    # a wing just off the ridge
    _wing(d, ((92, 46), (138, 14), (184, 44)), ((96, 54), (138, 26), (180, 52)), 7,
          lines_to=[(136, 88), (140, 88)])
    _seated_pilot(d, 138, 90, 1.0)


def para_eagle(d: Drawing):
    d.disc("glow", 100, 104, 46)
    d.band("far", "M-30 160 L20 136 L50 150 L90 124 L120 146 L150 130 L230 156")
    d.band("mid", hills(170, 10))
    d.band("near", hills(184, 5, 30), line=False)
    group(d, "translate(150 52) scale(.36)", lambda: (
        _wing(d, ((-34, -10), (0, -34), (34, -10)), ((-30, -4), (0, -24), (30, -4)), 5, spot=False,
              lines_to=[(-1, 24), (1, 24)], lw=2.2), _seated_pilot(d, 0, 26, 1.0)))
    right = ("M106 92 C126 80 150 70 176 70 L186 74 L176 78 L186 82 L174 85 L182 90 L168 91 L172 96 L158 95 "
             "C140 97 122 104 108 110Z")
    left = ("M94 92 C74 80 50 70 24 70 L14 74 L24 78 L14 82 L26 85 L18 90 L32 91 L28 96 L42 95 "
            "C60 97 78 104 92 110Z")
    d.shape("hero", left + " " + right)
    d.shape("light", "M88 120 L112 120 L116 138 L106 134 L100 140 L94 134 L84 138Z")
    d.shape("hero", ellipse(100, 104, 11, 22))
    d.shape("light", circle(100, 82, 9))
    d.shape("hero2", "M92 80 L84 84 L92 86Z", shadow=False, spot=True)
    d.marks("mark", circle(97, 80, 1.6))
    d.shape("hero2", "M95 124 L94 130 M105 124 L106 130", shadow=False)


# ================================================================ PARASAILING
def _parachute(d: Drawing, body="hero", stripe="light", centre="hero2"):
    """A round parasail canopy, centred on (100, 70), lines to (100, 130)."""
    edge = [(36, 82), (52, 88), (68, 86), (84, 90), (100, 88), (116, 90), (132, 86), (148, 88), (164, 82)]
    for x, y in edge[::2]:
        d.stroke("dark", f"M{x} {y} L100 128", 0.9)
    dome = "M36 82 C30 42 64 22 100 22 C136 22 170 42 164 82 Q156 86 148 88 Q140 84 132 86 Q124 92 116 90 Q108 86 100 88 Q92 86 84 90 Q76 92 68 86 Q60 84 52 88 Q44 86 36 82Z"
    d.shape(body, dome)
    d.shape(stripe, "M100 22 C84 24 66 40 64 86 Q66 87 68 86 Q76 92 84 90 C80 60 88 34 100 22Z", shadow=False, spot=True)
    d.shape(stripe, "M100 22 C116 24 134 40 136 86 Q134 87 132 86 Q124 92 116 90 C120 60 112 34 100 22Z", shadow=False, spot=True)
    d.shape(centre, "M100 22 C96 40 94 62 96 88 Q98 88 100 88 Q102 88 104 88 C106 62 104 40 100 22Z", shadow=False)


def parasail_boat(d: Drawing):
    d.disc("glow", 160, 46, 16)
    d.band("far", "M-30 126 L230 126", line=False)
    d.shape("near", "M146 127 Q160 114 176 118 Q188 120 196 127Z")
    d.band("mid", waves(130, 3, 30))
    d.band("near", waves(158, 4, 34))
    d.stroke("dark", "M70 92 L112 146", 1.4)
    group(d, "translate(-14 -4)", lambda: (
        d.shape("light", "M30 160 Q70 150 120 156 L120 162 Q80 162 30 170Z", shadow=False),
        d.shape("hero", "M116 154 L180 152 Q176 164 166 166 L124 166Z", spot=True),
        d.shape("dark", "M132 152 L140 142 L156 142 L160 152Z"),
        d.shape("light", "M142 144 L152 144 L154 150 L140 150Z", shadow=False),
        d.shape("dark", rrect(112, 150, 7, 12, 2))))
    group(d, "translate(70 50) scale(.5) translate(-100 -70)", lambda: _parachute(d, body="pop", stripe="light", centre="hero2"))
    _hanging_rider(d, 70, 81, 0.75)


def parasail_chute(d: Drawing):
    d.band("far", waves(150, 3, 36))
    d.band("mid", waves(166, 4, 30))
    d.band("near", waves(184, 4, 34), line=False)
    d.shape("light", cloud(10, 120, 1.2))
    d.shape("light", cloud(150, 136, 0.9))
    group(d, "translate(100 70) scale(1.05) translate(-100 -76)", lambda: _parachute(d))
    _hanging_rider(d, 100, 130, 1.6)


def _palm(d: Drawing, x, y, s=1.0):
    def p():
        d.limb("dark", "M0 0 C2 -30 10 -60 24 -84", 7)
        fronds = ["M24 -84 C10 -92 -6 -88 -16 -74 C-2 -84 12 -84 24 -84Z",
                  "M24 -84 C14 -100 -2 -104 -12 -100 C2 -98 14 -92 24 -84Z",
                  "M24 -84 C34 -100 52 -102 62 -94 C48 -96 36 -92 24 -84Z",
                  "M24 -84 C40 -86 56 -78 62 -64 C50 -76 38 -80 24 -84Z",
                  "M24 -84 C26 -96 36 -108 46 -110 C36 -102 30 -94 24 -84Z"]
        for f in fronds:
            d.shape("dark", f)
    group(d, f"translate({x} {y}) scale({s})", p)


def parasail_beach(d: Drawing):
    d.disc("glow", 140, 64, 26)
    d.band("far", waves(118, 2, 40))
    d.band("mid", waves(136, 3, 30))
    d.band("ground", "M-30 160 Q60 146 120 156 T230 150")
    d.shape("light", "M-30 158 Q60 144 120 154 T230 148 L230 152 Q170 156 120 160 Q60 150 -30 164Z", shadow=False, line=False)
    d.stroke("dark", "M126 70 L160 117", 1)
    d.shape("dark", "M154 115 L170 115 L168 119 L156 119Z")
    group(d, "translate(126 44) scale(.32) translate(-100 -70)", lambda: _parachute(d, body="pop", stripe="light", centre="hero2"))
    _hanging_rider(d, 126, 63, 0.5)
    d.shape("hero", "M44 172 L80 172 Q70 154 62 152 Q52 154 44 172Z")
    d.stroke("dark", "M62 152 L62 180", 2)
    _palm(d, 28, 186, 1.0)
    d.band("near", hills(186, 4), line=False)


# ================================================================ HELICOPTER
def _heli(d: Drawing, body="hero", stripe="hero2", glass="light"):
    """A helicopter facing right, cabin centred around (110, 100)."""
    d.stroke("dark", "M78 124 L76 132 M128 124 L130 132", 3)
    d.limb("dark", "M62 134 H146 Q152 134 154 128", 3.2)
    d.shape(body, "M76 96 L24 88 L22 82 L80 84Z")
    d.shape(body, "M18 66 L28 66 L32 88 L22 90Z")
    d.shape(stripe, "M16 72 a8 8 0 1 0 16 0 a8 8 0 1 0 -16 0Z", shadow=False, line=False)
    d.stroke("dark", "M24 64 V80 M16 72 H32", 2.4)
    d.shape(body, "M64 104 C62 86 80 74 104 72 L120 72 C142 72 158 88 158 102 C158 116 146 124 128 124 L84 124 C70 124 64 116 64 104Z")
    d.shape(glass, "M120 76 C138 76 152 88 154 100 L122 100 Z", shadow=False)
    d.shape(glass, rrect(94, 82, 20, 16, 3), shadow=False)
    d.shape(stripe, "M66 108 L157 108 C156 113 154 116 151 118 L70 118 C67 115 66 112 66 108Z", shadow=False, spot=True)
    d.shape("dark", rrect(104, 64, 10, 9, 2))
    d.shape("dark", rrect(28, 60, 164, 5, 2.5))


def heli_side(d: Drawing):
    d.disc("glow", 58, 52, 18)
    d.shape("light", cloud(20, 150, 1.4))
    d.shape("light", cloud(124, 160, 1.2))
    d.shape("light", cloud(150, 34, 0.8))
    d.band("far", hills(186, 6), line=False)
    group(d, "translate(100 100) scale(.92) rotate(-6) translate(-104 -98)", lambda: _heli(d))


def heli_canyon(d: Drawing):
    d.disc("glow", 52, 58, 16)
    d.band("far", "M-30 112 H30 L36 104 H76 L82 112 H120 L126 98 H160 L166 112 H230")
    d.band("mid", "M-30 136 H40 L46 126 H70 L76 140 L108 140 L114 130 H150 L156 138 H230")
    d.shape("sky2", "M84 230 C92 190 120 176 110 158 C104 148 112 142 120 140 L126 140 C120 150 124 158 132 166 C144 182 126 200 132 230Z", line=False)
    d.band("near", "M-30 160 H30 L40 150 H70 C86 152 100 156 104 176 L112 230", line=True)
    _land(d, "near", "M136 230 C130 200 136 176 150 166 L160 158 H192 L198 166 H230 V230Z", "M136 230 C130 200 136 176 150 166 L160 158 H192 L198 166 H230")
    d.shape("light", "M104 230 C108 200 120 186 118 170 C116 160 120 152 124 146 C124 156 128 164 132 172 C138 186 128 200 128 230Z", shadow=False, line=False)
    _line_only(d, "M104 230 C108 200 120 186 118 170 C116 160 120 152 124 146 M124 146 C124 156 128 164 132 172 C138 186 128 200 128 230", 2.4)
    group(d, "translate(122 74) scale(.5) rotate(-8) translate(-104 -98)", lambda: _heli(d))


def heli_island(d: Drawing):
    d.disc("glow", 46, 50, 14)
    d.band("far", waves(146, 3, 36))
    d.band("mid", waves(166, 4, 30), line=False)
    cliffs = "M64 230 L70 150 L84 122 L94 134 L106 98 L118 114 L130 84 L142 102 L156 76 L172 92 L230 70"
    _land(d, "mid", cliffs + " V230Z", cliffs)
    d.shape("near", "M86 230 L92 164 L104 140 L110 152 L122 122 L130 138 L142 114 L152 132 L166 108 L230 100 V230Z", shadow=False, line=False)
    d.shape("light", "M148 106 C150 104 152 104 154 106 L156 166 L146 166Z", shadow=False, line=False)
    d.stroke("near", "M150.5 112 L150.5 160", 1, line=False)
    _line_only(d, "M148 108 L146 166 M154 108 L156 166", 2)
    d.shape("light", ellipse(151, 168, 12, 3.5), shadow=False, line=False)
    d.band("ground", "M-30 184 Q40 174 90 180 T230 178", line=False)
    d.shape("light", cloud(150, 44, 0.7))
    group(d, "translate(70 94) scale(.5) rotate(-8) translate(-104 -98)", lambda: _heli(d))


# ================================================================ SEAPLANE
def _seaplane(d: Drawing, body="hero", trim="hero2", floats="dark"):
    """A float plane facing right, roughly x 26-172, y 64-138."""
    d.stroke("dark", "M104 74 L96 98 M128 74 L120 96", 1.8)
    d.stroke(floats, "M74 104 L70 126 M90 106 L92 126 M130 106 L134 126 M146 104 L148 126", 2.4)
    d.shape(floats, "M56 124 H160 Q170 124 174 118 C176 124 172 134 156 136 H66 Q56 136 56 130Z")
    d.shape(body, "M24 64 L38 64 L60 90 L34 94Z")
    d.shape(body, "M30 92 C40 86 64 82 100 80 L140 80 C154 80 162 86 164 94 C164 102 158 108 146 108 L100 110 C70 108 44 102 30 96Z")
    d.shape(trim, "M30 64 L38 64 L56 86 L42 88Z", shadow=False, spot=True)
    d.shape(trim, "M48 98 C70 103 90 104 100 104 L162 101 C160 105 154 108 146 108 L100 110 C76 109 60 106 48 98Z", shadow=False, spot=True)
    d.shape("light", "M122 84 H140 C148 84 154 88 156 94 H122Z", shadow=False)
    d.shape("light", rrect(100, 85, 16, 9, 2.5), shadow=False)
    d.shape("dark", rrect(82, 70, 72, 6, 3))
    d.shape("dark", ellipse(168, 94, 2.6, 15))
    d.shape(trim, circle(165, 94, 3.2), shadow=False)


def seaplane_floats(d: Drawing):
    d.disc("glow", 150, 58, 20)
    d.band("far", "M-30 120 L10 108 L30 116 L60 96 L84 112 L110 102 L140 116 L170 104 L230 118")
    for x, y, h in [(20, 124, 16), (32, 126, 20), (156, 124, 18), (170, 126, 14), (184, 125, 20)]:
        d.shape("mid", _pine(x, y, h), line=False)
    d.band("mid", "M-30 124 Q100 120 230 124")
    d.band("near", waves(156, 3, 34))
    d.shape("light", "M40 150 Q30 140 34 132 Q40 142 50 146 Q60 136 70 140 Q62 146 64 152Z")
    d.shape("light", "M130 150 Q122 140 128 132 Q134 142 142 146 Q152 136 160 140 Q152 148 156 152Z")
    group(d, "translate(100 112) scale(.82) rotate(-4) translate(-100 -100)", lambda: _seaplane(d))
    d.band("deep", waves(178, 3, 40), line=False)


def _bungalow(d: Drawing, x, y, s=1.0):
    def b():
        d.stroke("dark", "M-12 0 L-12 16 M0 0 L0 16 M12 0 L12 16", 2)
        d.shape("light", rrect(-14, -12, 28, 14, 1.5))
        d.shape("dark", rrect(-4, -8, 8, 10, 1), shadow=False)
        d.shape("ground", "M-22 -10 L0 -28 L22 -10Z")
        d.stroke("near", "M-14 -16 L14 -16 M-7 -22 L7 -22", 1.2, line=False)
    group(d, f"translate({x} {y}) scale({s})", b)


def seaplane_lagoon(d: Drawing):
    d.disc("glow", 46, 56, 15)
    d.band("far", "M-30 118 Q100 112 230 118")
    d.shape("near", "M140 117 Q150 98 164 100 Q176 96 186 112 L196 117Z")
    d.band("mid", waves(124, 2.5, 40))
    d.band("sky2", waves(150, 3, 36))
    d.shape("ground", rrect(36, 158, 140, 5, 2))
    for x, y, s in [(56, 152, 0.9), (100, 152, 0.9), (144, 152, 0.9)]:
        _bungalow(d, x, y, s)
    d.band("near", waves(176, 3, 40), line=False)
    group(d, "translate(108 62) scale(.48) rotate(-6) translate(-100 -100)", lambda: _seaplane(d))
    d.shape("light", cloud(128, 92, 0.6))


def seaplane_dock(d: Drawing):
    d.disc("glow", 52, 52, 16)
    d.band("far", hills(104, 14, 20))
    for x, y, h in [(14, 116, 22), (28, 118, 30), (44, 117, 24), (150, 114, 26), (164, 117, 32), (180, 116, 22), (194, 117, 26)]:
        d.shape("deep", _pine(x, y, h))
    d.band("mid", "M-30 118 Q100 114 230 118")
    d.shape("ground", "M-30 150 L80 132 L86 136 L-30 168Z")
    d.stroke("dark", "M20 150 L20 162 M48 140 L48 152 M74 132 L74 144", 2.4)
    d.stroke("dark", "M-20 154 L82 135", 1, line=False)
    group(d, "translate(118 110) scale(.68) translate(-100 -100)", lambda: _seaplane(d))
    d.band("near", waves(160, 3, 34))
    d.stroke("light", "M60 150 Q80 146 100 150 M130 154 Q150 150 168 154", 1.6, line=False)


# ================================================================ ZIP-LINING
def _jungle(d: Drawing, y, role, amp=10, step=26, shadow=True, line=True):
    s = f"M-30 {y}"
    x = -30
    k = 0
    while x < 230:
        h = amp * (1.0 if k % 2 else 0.7)
        s += f" q{step/2} {-2*h} {step} 0"
        x += step
        k += 1
    d.band(role, s, shadow=shadow, line=line)


def _trolley(d: Drawing, body="hero", wheel="dark"):
    """A zip-line trolley riding a cable at y=100 (wheels sit on the cable), hanging down to y~138."""
    d.shape(body, "M70 98 H130 Q136 98 136 104 V116 Q136 124 126 128 L110 136 L90 136 L74 128 Q64 124 64 116 V104 Q64 98 70 98Z", spot=True)
    for x in (84, 116):
        d.shape(wheel, circle(x, 90, 11), shadow=False)
        d.shape("light", circle(x, 90, 3.6), shadow=False)
    d.marks("dark", circle(100, 126, 4))


def zip_jungle(d: Drawing):
    d.disc("glow", 150, 54, 18)
    d.band("far", "M-30 112 L20 82 L50 100 L84 74 L120 98 L150 84 L190 102 L230 92")
    _jungle(d, 132, "mid", 9, 28)
    _jungle(d, 162, "near", 10, 32)
    d.shape("dark", _bar(34, 176, 36, 70, 7))
    d.shape("ground", rrect(20, 86, 32, 5, 2))
    d.stroke("dark", "M36 72 L172 136", 1.8)
    d.shape("dark", _bar(170, 178, 171, 132, 6))
    d.shape("ground", rrect(158, 144, 26, 5, 2))

    def rider():
        d.stroke("dark", "M0 -8 L-3 6 M0 -8 L4 6", 1.4)
        d.shape("hero2", rrect(-5, -11, 10, 5, 2), shadow=False)
        _hanging_rider(d, 0, 10, 1.2, body="hero", helmet="pop")
    group(d, "translate(104 112)", rider)
    _jungle(d, 184, "deep", 6, 30, line=False)


def zip_trolley(d: Drawing):
    d.disc("glow", 46, 54, 16)
    _jungle(d, 150, "mid", 10, 30)
    _jungle(d, 176, "near", 10, 34, line=False)
    d.shape("light", cloud(136, 46, 0.9))

    def kit():
        d.stroke("dark", "M-30 101 L230 101", 3.4)
        _trolley(d)
        d.stroke("hero2", "M100 128 C88 134 88 152 100 156 C112 152 112 134 100 128Z", 4.5)
        d.limb("pop", "M100 156 Q98 172 104 200", 6, spot=True)
    group(d, "rotate(12 100 100) translate(0 -8)", kit)


TOUCAN = ("M70 120 C64 102 74 82 92 78 C100 77 106 80 110 86 L114 100 C118 116 116 132 108 146 L96 172 L88 170 L92 146 C80 142 72 132 70 120Z")


def zip_toucan(d: Drawing):
    _jungle(d, 120, "far", 10, 30)
    _jungle(d, 152, "mid", 12, 34)
    _jungle(d, 180, "near", 8, 30, line=False)
    d.stroke("dark", "M-20 162 L220 112", 1.8)
    group(d, "translate(166 112) scale(.5)", lambda: (d.stroke("dark", "M0 -10 L-3 4 M0 -10 L4 4", 2.4), _hanging_rider(d, 0, 8, 1.4, body="hero", helmet="pop")))
    group(d, "translate(-4 -6)", lambda: (
        d.shape("dark", TOUCAN),
        d.shape("hero2", "M92 82 C102 82 108 88 110 96 C110 104 104 108 96 108 C88 106 84 100 84 94 C84 88 88 82 92 82Z", shadow=False),
        d.shape("hero", "M106 84 C120 78 140 80 158 92 C146 94 134 96 112 100Z", spot=True),
        d.shape("pop", "M156 91 C150 92 146 92 140 93 C146 88 152 89 156 91Z", shadow=False),
        d.stroke("mark", "M112 92 C128 90 140 91 152 92", 1, line=False),
        d.shape("light", circle(100, 88, 4.2), shadow=False),
        d.marks("mark", circle(100.5, 88, 2)),
        ))
    d.marks("mark", "M86 147 L92 145 L93 149 L87 151Z M96 145 L102 143 L103 147 L97 149Z")


# ================================================================ BUNGEE
def _jumper(d: Drawing, x, y, s=1.0, body="dark", head="pop"):
    """A small bungee jumper hanging head-down from the cord end at (x, y)."""
    def fig():
        d.limb(body, "M-2 0 L-3 14 M2 0 L3 14", 4)
        d.shape(body, rrect(-5.5, 12, 11, 15, 5))
        d.limb(body, "M-4 22 L-10 32 M4 22 L10 32", 3.2, shadow=False)
        d.shape(head, circle(0, 32, 5.4))
    group(d, f"translate({x} {y}) scale({s})", fig)


def bungee_bridge(d: Drawing):
    d.disc("glow", 152, 50, 15)
    _land(d, "far", "M-30 230 V86 L14 84 L42 108 L54 112 L60 230Z", "M-30 86 L14 84 L42 108 L54 112 L60 230")
    _land(d, "far", "M230 230 V80 L190 82 L160 106 L146 112 L140 230Z", "M230 80 L190 82 L160 106 L146 112 L140 230")
    d.band("sky2", waves(176, 3, 30))
    d.shape("mid", "M-30 230 V136 L20 138 L52 166 L66 230Z", line=False)
    d.shape("mid", "M230 230 V130 L180 134 L150 164 L136 230Z", line=False)
    d.stroke("dark", "M50 112 Q100 34 150 112", 4.5)
    d.stroke("dark", "M60 96 L60 66 M74 78 L74 58 M87 69 L87 56 M113 69 L113 56 M126 78 L126 58 M140 96 L140 66", 1.8)
    d.shape("dark", rrect(26, 50, 148, 8, 2))
    d.shape("hero2", rrect(26, 48, 148, 3.5, 1.5), shadow=False, spot=True)
    d.stroke("pop", "M106 58 C110 74 102 86 106 104 C110 116 102 124 105 132", 2.4)
    _jumper(d, 105, 132, 1.15)


def bungee_dive(d: Drawing):
    d.disc("glow", 100, 112, 44)
    d.band("far", hills(150, 10, 20))
    d.shape("sky2", "M62 230 C72 196 112 186 106 166 C104 158 110 154 116 154 C122 160 120 170 130 180 C142 194 134 214 138 230Z", line=False)
    _line_only(d, "M62 230 C72 196 112 186 106 166 C104 158 110 154 116 154 M116 154 C122 160 120 170 130 180 C142 194 134 214 138 230", 2.4)
    d.band("near", hills(182, 6, 30), line=False)
    d.stroke("pop", "M100 -10 C92 6 108 18 100 36", 3.4)
    d.shape("dark", _bar(96, 48, 95, 98, 10))
    d.shape("dark", _bar(104, 48, 105, 98, 10))
    d.shape("dark", "M90 40 C88 34 92 30 98 30 L99 44 L90 44Z")
    d.shape("dark", "M110 40 C112 34 108 30 102 30 L101 44 L110 44Z")
    d.shape("pop", rrect(88, 40, 24, 9, 3), spot=True)
    d.limb("hero", "M90 112 L64 98 L42 92", 8)
    d.limb("hero", "M110 112 L136 98 L158 92", 8)
    d.shape("hero", rrect(86, 92, 28, 36, 11))
    d.shape("hero2", rrect(86, 92, 28, 8, 4), shadow=False)
    d.shape("light", circle(100, 138, 11))
    d.shape("dark", "M89 140 C90 150 110 150 111 140 C108 146 92 146 89 140Z", shadow=False)
    d.marks("mark", circle(42, 92, 4) + circle(158, 92, 4))


def bungee_cliff(d: Drawing):
    d.disc("glow", 56, 52, 16)
    d.band("far", hills(110, 14, -20))
    _land(d, "mid", "M230 230 V70 L170 72 L160 96 L150 230Z", "M230 70 L170 72 L160 96 L150 230")
    _land(d, "mid", "M-30 230 V140 L20 142 L44 230Z", "M-30 140 L20 142 L44 230", shadow=True)
    d.shape("ground", rrect(116, 66, 60, 7, 2))
    d.stroke("dark", "M120 74 L132 92 M140 74 L150 90", 2)
    d.stroke("dark", "M120 66 L120 58 M132 66 L132 58 M120 59 H174", 1.4)
    d.band("sky2", waves(174, 3, 34))
    d.band("near", hills(188, 5), line=False)
    d.stroke("pop", "M122 70 C112 82 104 84 100 96 C96 108 90 108 90 118", 2.4)
    _jumper(d, 90, 118, 1.15)


# ================================================================ SNOW HELPERS
def _peaks(d: Drawing, role, pts, caps=True, cap_depth=13, line=True):
    """A mountain band through the given (x, y) points with snow caps on the peaks."""
    d.band(role, "M" + " L".join(f"{x} {y}" for x, y in pts), line=line)
    if not caps:
        return
    for i in range(1, len(pts) - 1):
        (x0, y0), (x, y), (x1, y1) = pts[i - 1], pts[i], pts[i + 1]
        if y < y0 and y < y1:
            k = cap_depth
            lx, ly = x + (x0 - x) * k / (y0 - y), y + k
            rx, ry = x + (x1 - x) * k / (y1 - y), y + k
            d.shape("light", f"M{x} {y} L{rx:.1f} {ry:.1f} L{x + (rx-x)*0.45:.1f} {y + k*0.7:.1f} L{x:.1f} {y + k:.1f} "
                             f"L{x + (lx-x)*0.45:.1f} {y + k*0.75:.1f} L{lx:.1f} {ly:.1f}Z", shadow=False)


def _flakes(d: Drawing, pts):
    for x, y, r in pts:
        d.stroke("light", f"M{x-r} {y} L{x+r} {y} M{x-r*0.5} {y-r*0.87} L{x+r*0.5} {y+r*0.87} M{x-r*0.5} {y+r*0.87} L{x+r*0.5} {y-r*0.87}", 1.6)


def _ski(x1, y1, x2, y2, w=5):
    """A ski from tail (x1, y1) to tip (x2, y2), tip curled up."""
    import math
    dx, dy = x2 - x1, y2 - y1
    n = math.hypot(dx, dy)
    ux, uy = dx / n, dy / n
    nx, ny = uy, -ux  # "up" side normal for a ski pointing right
    h = w / 2
    tip = (x2 + ux * 6 + nx * 7, y2 + uy * 6 + ny * 7)
    return (f"M{x1 - nx*h:.1f} {y1 - ny*h:.1f} L{x2 - nx*h:.1f} {y2 - ny*h:.1f} "
            f"Q{x2 + ux*7 - nx*h:.1f} {y2 + uy*7 - ny*h:.1f} {tip[0]:.1f} {tip[1]:.1f} "
            f"Q{x2 + ux*1 + nx*h:.1f} {y2 + uy*1 + ny*h:.1f} {x2 - ux*2 + nx*h:.1f} {y2 - uy*2 + ny*h:.1f} "
            f"L{x1 + nx*h:.1f} {y1 + ny*h:.1f} Q{x1 - ux*3:.1f} {y1 - uy*3:.1f} {x1 - nx*h:.1f} {y1 - ny*h:.1f}Z")


# ================================================================ SKIING
def ski_chairlift(d: Drawing):
    d.disc("glow", 156, 50, 15)
    _peaks(d, "far", [(-30, 120), (14, 92), (40, 106), (78, 70), (112, 104), (146, 80), (176, 100), (230, 88)])
    d.band("mid", hills(146, 12, 10))
    for x, y, h in [(18, 152, 24), (32, 156, 18), (150, 150, 22), (164, 154, 28), (180, 152, 20)]:
        d.shape("deep", _pine(x, y, h))
    d.band("light", "M-30 164 Q60 154 120 162 T230 158")
    d.stroke("dark", "M-20 30 L220 62", 2)

    def chair():
        d.shape("dark", rrect(96, 42, 16, 9, 3))
        d.limb("dark", "M104 50 L104 70 Q104 76 98 76 L72 76 Q66 76 66 82 L66 118", 4.5)
        d.shape("hero", rrect(60, 84, 11, 38, 4))
        d.shape("pop", _ski(78, 158, 146, 138, 5.5), spot=True)
        d.limb("dark", "M80 110 L110 113 L114 142", 9)
        d.shape("dark", rrect(106, 138, 15, 9, 3))
        d.shape("pop", rrect(72, 80, 21, 36, 9))
        d.limb("pop", "M86 92 L104 104", 6, shadow=False)
        d.shape("hero2", circle(84, 71, 9.5))
        d.shape("dark", rrect(84, 66, 13, 6, 3), shadow=False)
        d.shape("light", rrect(87, 67.5, 8, 3, 1.5), shadow=False)
        d.shape("hero", rrect(60, 116, 56, 8, 3))
    group(d, "translate(0 -2)", chair)


BOOT = ("M62 44 L104 40 Q108 40 108 44 L106 88 C120 92 138 96 150 104 Q156 108 156 116 L156 124 "
        "L56 126 L56 104 Q56 96 60 90Z")


def ski_boot(d: Drawing):
    _peaks(d, "far", [(-30, 96), (30, 64), (64, 86), (110, 50), (150, 80), (230, 60)])
    d.band("mid", hills(140, 10))
    d.band("light", hills(160, 8, 20))

    def boot():
        d.shape("hero2", _ski(14, 144, 182, 126, 8), spot=True)
        d.shape("dark", "M40 122 L60 120 L60 134 L36 136Z")
        d.shape("dark", "M146 112 L166 110 L170 124 L146 128Z")
        d.shape("hero", BOOT)
        d.shape("dark", "M62 44 L104 40 Q108 40 108 44 L107 52 L62 56Z", shadow=False)
        for y, x2 in [(66, 106), (84, 106)]:
            d.shape("light", f"M58 {y} L{x2} {y-3} L{x2} {y+4} L58 {y+7}Z", shadow=False)
        d.shape("light", "M112 96 L132 100 L130 108 L110 105Z", shadow=False)
        d.shape("light", "M136 102 L150 108 L148 116 L134 111Z", shadow=False)
        for x, y in [(100, 64), (100, 82), (124, 100), (144, 108)]:
            d.marks("dark", rrect(x - 4, y - 1, 9, 5, 2))
        d.shape("dark", "M56 118 L156 116 L156 126 L56 128Z", shadow=False)
    group(d, "rotate(-6 100 100) translate(0 4)", boot)
    d.stroke("light", "M22 160 Q12 150 18 138 M30 166 Q20 160 22 150", 3, line=False)


def ski_matterhorn(d: Drawing):
    d.disc("glow", 44, 52, 14)
    d.band("far", "M-30 136 L20 118 L50 128 L150 120 L176 108 L230 124")
    horn = "M30 150 L74 92 L90 64 L94 40 L102 34 L108 50 L118 70 L140 104 L176 150Z"
    d.shape("mid", horn, line=False)
    _line_only(d, "M30 150 L74 92 L90 64 L94 40 L102 34 L108 50 L118 70 L140 104 L176 150", 3)
    d.shape("light", "M94 40 L102 34 L108 50 L118 70 L110 66 L104 74 L98 62 L90 68 L90 64Z", shadow=False)
    d.shape("light", "M74 92 L82 80 L88 92 L80 90Z M128 86 L140 104 L132 98 L126 102Z", shadow=False)
    d.shape("near", "M102 34 L108 50 L118 70 L140 104 L176 150 L120 150 L112 104 L106 70Z", shadow=False, line=False)
    d.band("light", "M-30 150 Q60 140 120 148 T230 144")
    for x, y, h in [(26, 156, 22), (40, 160, 16), (170, 154, 20)]:
        d.shape("deep", _pine(x, y, h))
    d.stroke("pop", "M150 166 Q120 156 96 168 Q74 180 54 174", 2, line=False)
    _line_only(d, "M150 166 Q120 156 96 168 Q74 180 54 174", 1.6)
    d.shape("pop", _bar(122, 186, 136, 120, 6), spot=True)
    d.shape("hero", _bar(140, 188, 124, 122, 6))
    d.stroke("dark", "M114 182 L130 132 M150 184 L136 132", 2)
    d.band("light", "M-30 182 Q100 172 230 182", line=False)


# ================================================================ SNOWBOARDING
def board_planted(d: Drawing):
    d.disc("glow", 52, 58, 18)
    _peaks(d, "far", [(-30, 120), (24, 96), (56, 112), (100, 80), (140, 108), (176, 86), (230, 104)])
    d.band("mid", hills(142, 10, 20))

    def board():
        d.shape("hero", rrect(80, 26, 40, 150, 20))
        d.shape("hero2", "M80 62 L100 48 L120 62 L120 74 L100 60 L80 74Z", shadow=False, spot=True)
        d.shape("hero2", "M80 86 L100 72 L120 86 L120 98 L100 84 L80 98Z", shadow=False, spot=True)
        d.shape("light", rrect(86, 116, 28, 10, 3), shadow=False)
        d.shape("light", rrect(86, 140, 28, 10, 3), shadow=False)
        d.shape("dark", rrect(83, 114, 34, 5, 2), shadow=False)
        d.shape("dark", rrect(83, 138, 34, 5, 2), shadow=False)
    group(d, "rotate(10 100 150)", board)
    d.band("light", "M-30 160 Q30 150 70 156 Q100 142 130 156 Q170 150 230 160")
    d.stroke("mid", "M60 172 Q90 166 110 174", 2, line=False)


def board_goggles(d: Drawing):
    d.band("far", hills(150, 10))
    d.band("light", hills(170, 8, 20))
    d.limb("pop", "M-20 104 Q20 92 40 96", 18, spot=True)
    d.limb("pop", "M220 104 Q180 92 160 96", 18, spot=True)
    frame = "M30 86 C30 64 60 58 100 58 C140 58 170 64 170 86 C170 116 156 132 132 132 C118 132 112 120 100 120 C88 120 82 132 68 132 C44 132 30 116 30 86Z"
    d.shape("dark", frame)
    lens = "M40 88 C40 72 64 68 100 68 C136 68 160 72 160 88 C160 110 150 122 132 122 C120 122 114 110 100 110 C86 110 80 122 68 122 C50 122 40 110 40 88Z"
    d.shape("glow", lens, shadow=False)
    d.shape("glow2", "M40 92 C60 90 80 86 100 88 C124 90 144 86 160 88 C160 110 150 122 132 122 C120 122 114 110 100 110 C86 110 80 122 68 122 C50 122 40 110 40 92Z", shadow=False, line=False)
    d.shape("mid", "M42 104 L66 84 L80 94 L104 74 L126 96 L140 86 L159 100 C156 114 146 122 132 122 C120 122 114 110 100 110 C86 110 80 122 68 122 C54 122 44 114 42 104Z", shadow=False, spot=True)
    d.shape("light", "M104 74 L111 81 L106 80 L102 84 L98 80 L96 81Z M66 84 L72 89 L68 89 L64 91 L61 88Z", shadow=False)
    d.stroke("light", "M52 78 L66 72 M48 86 L58 82", 3)


def board_jump(d: Drawing):
    d.disc("glow", 104, 92, 50)
    _peaks(d, "far", [(-30, 150), (20, 130), (50, 142), (230, 140)], caps=False)
    d.band("light", "M-30 176 Q40 170 70 152 Q80 146 90 160 Q130 184 230 176")

    def rider():
        d.shape("hero2", rrect(56, 116, 92, 12, 6), spot=True)
        d.limb("dark", "M78 118 L84 96 L100 90", 10)
        d.limb("dark", "M122 118 L120 96 L106 90", 10)
        d.limb("hero", "M100 90 L96 66", 15)
        d.limb("hero", "M98 72 L74 56 L62 40", 7)
        d.limb("hero", "M100 74 L120 92 L130 116", 7)
        d.shape("dark", rrect(70, 114, 18, 7, 3), shadow=False)
        d.shape("dark", rrect(112, 114, 18, 7, 3), shadow=False)
        d.shape("pop", circle(92, 52, 10))
        d.shape("dark", rrect(88, 47, 16, 7, 3.5), shadow=False)
        d.shape("light", rrect(92, 48.5, 10, 4, 2), shadow=False)
    group(d, "rotate(-18 100 96) translate(4 0)", rider)


# ================================================================ DOG-SLEDDING
def husky_head(d: Drawing):
    _peaks(d, "far", [(-30, 128), (20, 98), (60, 120), (140, 116), (176, 92), (230, 116)])
    d.band("light", hills(176, 6))
    head = ("M48 128 C44 96 52 74 64 62 L58 26 L88 50 C96 48 104 48 112 50 L142 26 L136 62 C148 74 156 96 152 128 "
            "C150 160 128 182 100 184 C72 182 50 160 48 128Z")
    d.shape("hero", head)
    d.shape("hero2", "M64 36 L84 52 L70 60Z M136 36 L116 52 L130 60Z", shadow=False)
    mask = ("M100 70 C94 70 90 80 88 92 C78 88 64 94 60 112 C58 142 78 172 100 178 C122 172 142 142 140 112 "
            "C136 94 122 88 112 92 C110 80 106 70 100 70Z")
    d.shape("light", mask, shadow=False)
    d.shape("light", ellipse(78, 90, 6, 4) + " " + ellipse(122, 90, 6, 4), shadow=False)
    d.shape("pop", "M70 108 Q80 98 90 108 Q80 114 70 108Z M110 108 Q120 98 130 108 Q120 114 110 108Z", shadow=False, spot=True)
    d.marks("mark", circle(80, 107, 3) + circle(120, 107, 3))
    d.marks("mark", "M90 134 Q100 128 110 134 Q108 142 100 144 Q92 142 90 134Z")
    d.stroke("mark", "M100 144 V152 M100 152 Q92 160 86 154 M100 152 Q108 160 114 154", 2)


DOG = ("M0 12 L4 8 L10 6 L12 -2 L16 4 L20 4 L22 10 C30 10 40 9 48 10 C52 6 56 2 58 -2 C60 4 56 10 52 14 "
       "C52 18 50 20 48 22 L58 30 L54 33 L44 24 L28 24 L16 32 L12 29 L20 21 C16 20 12 16 6 16 L2 15Z")


def _dog(d: Drawing, x, y, s=1.0, role="dark", harness="pop"):
    def g():
        d.shape(role, DOG)
        d.stroke(harness, "M20 9 L24 22 M22 13 L40 12", 2.2)
    group(d, f"translate({x} {y}) scale({s})", g)


def sled_team(d: Drawing):
    d.disc("glow", 100, 100, 46)
    _peaks(d, "far", [(-30, 128), (20, 104), (56, 120), (100, 96), (140, 118), (180, 102), (230, 124)])
    d.band("light", "M-30 136 Q100 130 230 136")
    d.stroke("dark", "M40 128 L132 128", 1.6)
    _dog(d, 14, 104, 1.2)
    _dog(d, 72, 104, 1.2)

    def sled():
        d.limb("dark", "M122 150 H168 Q180 150 182 138", 3.2)
        d.stroke("dark", "M130 150 L132 136 M150 150 L150 136 M166 150 L166 112", 2.2)
        d.shape("hero", "M124 120 L166 120 L166 138 L128 138Z", spot=True)
        d.limb("dark", "M170 148 L170 126 M178 148 L178 126", 4.5)
        d.shape("hero2", rrect(162, 92, 22, 36, 9))
        d.limb("hero2", "M166 102 L160 116", 5.5, shadow=False)
        d.shape("pop", circle(173, 84, 8.5))
        d.shape("dark", "M164 82 Q173 70 182 82Z", shadow=False)
    group(d, "translate(-12 -12)", sled)
    d.band("mid", "M-30 152 Q100 144 230 152", line=False)
    d.band("light", "M-30 156 Q100 148 230 156", shadow=False, line=False)


def sled_trail(d: Drawing):
    d.disc("glow", 140, 64, 18)
    _peaks(d, "far", [(-30, 110), (30, 80), (70, 104), (110, 84), (150, 102), (230, 92)])
    d.band("light", "M-30 116 Q100 110 230 116")
    for x in range(-10, 210, 13):
        d.shape("mid", _pine(x, 120 + (x % 3), 20 + (x * 7) % 9), line=False)
    _line_only(d, "M-30 116 Q100 110 230 116", 2.4)
    d.band("light", "M-30 124 Q100 118 230 124", line=False)
    d.stroke("mid", "M140 128 C158 136 160 146 132 154 C96 164 76 176 96 196 M146 128 C166 136 168 148 140 156 C104 166 88 178 104 196", 2.4)
    group(d, "translate(80 112) scale(.5)", lambda: (_dog(d, 0, 0), _dog(d, 50, 0), d.stroke("dark", "M40 14 L104 14", 2),
                                                    d.shape("hero", rrect(100, 6, 32, 16, 3)), d.limb("dark", "M128 6 L130 -14", 6),
                                                    d.shape("pop", circle(130, -22, 7))))
    for x, y, h in [(26, 186, 54), (48, 190, 40), (172, 186, 58)]:
        d.shape("deep", _pine(x, y, h))


# ================================================================ SNOWMOBILE
def _snowmobile(d: Drawing, body="hero", trim="hero2", rider=True):
    """A snowmobile facing right, x ~36-176, y ~60-146."""
    d.limb("dark", "M138 124 L144 140", 4)
    d.limb("dark", "M120 146 H164 Q176 146 178 136", 4.5)
    d.shape("dark", rrect(40, 118, 92, 20, 10))
    for x in (52, 74, 96, 118):
        d.shape("light", circle(x, 128, 4.5), shadow=False, line=False)
    if rider:
        d.limb("dark", "M80 96 L98 102 L100 120", 10)
        d.shape("pop", rrect(68, 62, 22, 38, 10))
        d.limb("pop", "M82 76 L112 82", 7, shadow=False)
        d.shape("hero2" if trim != "hero2" else "light", circle(80, 54, 10))
        d.shape("dark", rrect(80, 49, 14, 7, 3.5), shadow=False)
    d.shape(body, "M40 102 L112 96 C130 92 156 98 170 112 L172 122 L40 122Z")
    d.shape(trim, "M40 112 L150 108 L168 114 L170 120 L40 120Z", shadow=False, spot=True)
    d.shape("light", "M112 96 L122 74 L132 76 L128 96Z", shadow=False)
    d.limb("dark", "M110 84 L116 90", 4, shadow=False)
    d.shape("light", ellipse(164, 110, 4, 3), shadow=False)
    if not rider:
        d.shape("dark", rrect(48, 92, 56, 10, 5))


def sm_side(d: Drawing):
    d.disc("glow", 150, 50, 16)
    _peaks(d, "far", [(-30, 112), (30, 80), (66, 104), (104, 74), (146, 104), (230, 90)])
    for x, y, h in [(150, 128, 26), (166, 130, 34), (184, 128, 24), (20, 128, 24)]:
        d.shape("deep", _pine(x, y, h))
    d.band("light", "M-30 128 Q100 120 230 128")
    d.shape("light", cloud(-2, 150, 1.5))
    d.shape("light", cloud(18, 140, 1.0))
    group(d, "translate(8 22) scale(.92)", lambda: _snowmobile(d))
    d.band("mid", "M-30 170 Q100 160 230 170", line=False)
    d.band("light", "M-30 174 Q100 164 230 174", shadow=False, line=False)


def sm_lake(d: Drawing):
    d.disc("glow", 150, 56, 18)
    _peaks(d, "far", [(-30, 112), (24, 82), (60, 104), (102, 70), (140, 100), (176, 84), (230, 106)])
    d.band("mid", hills(122, 6, 20))
    d.band("sky2", "M-30 128 Q100 122 230 128")
    d.stroke("light", "M20 138 H50 M130 134 H170", 1.6, line=False)
    d.band("light", "M-30 154 Q100 140 230 154")
    d.stroke("mid", "M-10 184 C30 170 40 156 60 150", 2.4)
    d.stroke("mid", "M-4 190 C36 176 48 160 66 154", 2.4)
    d.shape("light", cloud(36, 144, 0.55), line=False)
    group(d, "translate(44 100) scale(.62)", lambda: _snowmobile(d))


def sm_jump(d: Drawing):
    d.disc("glow", 108, 96, 50)
    d.band("far", hills(160, 8))
    d.band("light", "M-30 172 Q20 168 50 150 Q62 144 70 160 Q120 180 230 174")
    d.shape("light", cloud(18, 120, 1.2))
    d.shape("light", cloud(36, 108, 0.8))
    group(d, "translate(104 96) rotate(-14) scale(.86) translate(-104 -104)", lambda: _snowmobile(d))


# ================================================================ ICE-SKATING
SKATE = ("M66 34 L102 32 Q110 32 110 40 L110 84 C116 92 130 98 142 102 Q154 106 154 116 L154 122 Q154 128 146 128 "
         "L70 128 Q62 128 62 120 L64 50Z")


def _skate(d: Drawing, boot="light", trim="hero", blade="dark"):
    """A figure skate facing right, x ~50-166, y ~30-148."""
    d.shape(blade, "M52 144 H150 Q160 144 164 136 L166 128 L162 128 L162 132 L158 132 L158 136 L154 136 Q152 140 148 140 H56 Q50 140 52 144Z")
    d.stroke(blade, "M70 128 L68 141 M140 128 L144 140", 3.6)
    d.shape(boot, SKATE)
    d.shape(trim, "M66 34 L102 32 Q110 32 110 40 L110 46 L65 48Z", shadow=False, spot=True)
    d.shape(trim, "M62 112 L70 112 L72 128 H70 Q62 128 62 120Z", shadow=False)
    d.shape(trim, rrect(62, 124, 30, 9, 3))
    for i in range(5):
        y = 54 + i * 9
        x = 106 + (i * 3.4 if i < 4 else 14)
        d.stroke("mark", f"M{x-6:.1f} {y-3} L{x+4:.1f} {y+4} M{x-6:.1f} {y+4} L{x+4:.1f} {y-3}", 1.6)
    d.stroke("mark", "M104 50 L104 96 M110 92 Q118 96 122 104", 1.2, line=False)
    d.stroke("mark", "M100 40 Q92 24 102 20 Q110 24 104 40", 1.6)


def skate_boot(d: Drawing):
    d.disc("mid", 100, 92, 62, line=False)
    d.band("far", "M-30 150 Q100 140 230 150")
    d.stroke("light", "M40 160 Q80 150 120 158 Q150 164 170 154", 2.4)
    _flakes(d, [(52, 48, 5), (150, 50, 6), (160, 82, 4), (40, 86, 4)])
    group(d, "translate(100 96) rotate(-8) scale(.98) translate(-108 -88)", lambda: _skate(d))


def skate_rink(d: Drawing):
    d.disc("glow", 42, 48, 12)
    for x, w, h in [(-10, 30, 60), (22, 22, 84), (46, 26, 50), (128, 24, 70), (154, 30, 92), (186, 30, 58)]:
        d.shape("far", rrect(x, 140 - h, w, h + 20, 1.5), line=False)
        for wy in range(int(140 - h + 8), 132, 12):
            for wx in range(x + 5, x + w - 4, 8):
                d.shape("glow2", rrect(wx, wy, 3.5, 5, 0.5), shadow=False, line=False)
    _line_only(d, "M-10 82 H20 V58 H44 V92 H72 M128 72 H152 V50 H184 V84 H216", 2.2)
    d.stroke("dark", "M-10 70 Q40 90 100 64 Q160 90 210 70", 1.2)
    for i, (x, y) in enumerate([(14, 76), (36, 82), (58, 80), (80, 72), (124, 72), (146, 80), (168, 82), (188, 76)]):
        d.marks("pop" if i % 2 else "glow2", circle(x, y, 2.6))
    d.shape("deep", "M100 40 L118 74 L110 74 L126 102 L116 102 L134 132 L66 132 L84 102 L74 102 L90 74 L82 74Z")
    d.shape("dark", rrect(96, 130, 8, 10, 1))
    for x, y in [(96, 70), (106, 88), (90, 96), (112, 112), (84, 118), (100, 124)]:
        d.marks("pop", circle(x, y, 2.8))
    d.shape("glow2", "M100 30 L103 37 L110 37 L104.5 41.5 L106.5 48.5 L100 44 L93.5 48.5 L95.5 41.5 L90 37 L97 37Z", shadow=False)
    d.band("near", "M-30 138 Q100 132 230 138")
    d.shape("sky2", ellipse(100, 160, 96, 22), line=False)
    d.shape("light", ellipse(100, 160, 90, 18), shadow=False, line=False)
    _line_only(d, "M-30 142 Q100 136 230 142", 0.1)
    d.stroke("sky2", "M30 158 Q70 150 100 162 Q130 172 168 160", 1.4, line=False)
    for x, c in [(70, "hero"), (128, "pop")]:
        group(d, f"translate({x} 136) scale(.62)", lambda c=c: (
            d.limb("dark", "M-2 24 L-8 38 M2 24 L10 36", 4),
            d.shape(c, rrect(-6, 6, 12, 20, 5)),
            d.limb(c, "M-5 12 L-14 18 M5 12 L14 18", 3.4, shadow=False),
            d.shape("hero2", circle(0, 0, 5.5))))


def skate_pond(d: Drawing):
    d.disc("glow", 150, 56, 18)
    _peaks(d, "far", [(-30, 104), (24, 80), (60, 98), (100, 70), (140, 96), (230, 84)])
    d.band("light", "M-30 116 Q100 108 230 116")
    for x, y, h in [(16, 122, 30), (32, 124, 22), (160, 120, 26), (176, 124, 34), (192, 122, 22)]:
        d.shape("deep", _pine(x, y, h))
    d.shape("sky2", ellipse(100, 152, 92, 26))
    d.stroke("light", "M40 156 C60 140 90 140 96 150 C102 162 80 168 72 158 C64 146 110 136 140 150 C160 160 150 168 132 162", 1.8)
    group(d, "translate(116 112) scale(1.1)", lambda: (
        d.limb("dark", "M2 20 L-2 36", 4.5),
        d.limb("dark", "M2 20 L16 28 L26 26", 4.5),
        d.shape("hero", rrect(-4, 0, 13, 23, 6)),
        d.limb("hero", "M0 6 L-14 10 M6 6 L18 0", 3.6, shadow=False),
        d.shape("pop", circle(3, -6, 5.5)),
        d.shape("hero2", rrect(-3, -3, 13, 4, 2), shadow=False),
        d.stroke("dark", "M-8 38 L4 38 M22 28 L32 22", 1.6)))
    d.band("light", "M-30 182 Q100 170 230 182", line=False)


# ================================================================ NORTHERN LIGHTS
def _aurora(d: Drawing, y=0, s=1.0):
    """Aurora ribbons: soft paper curtains in papercut, two clipped spot-colour waves in line style."""
    def g():
        d.shape("hero", "M-30 70 C10 30 40 80 80 40 C110 12 140 50 170 20 L230 10 L230 30 C190 44 160 70 130 62 C100 54 80 100 40 90 C20 86 0 100 -30 110Z",
                shadow=False, line=False, extra='opacity=".9"')
        d.shape("hero2", "M-30 96 C10 70 40 108 80 74 C110 50 140 80 170 54 L230 44 L230 56 C190 70 160 92 130 86 C100 80 80 118 40 110 C20 106 0 116 -30 122Z",
                shadow=False, extra='opacity=".7"', line=False)
        d.shape("light", "M-30 70 C10 30 40 80 80 40 C110 12 140 50 170 20 L230 10 L230 16 C176 28 140 56 112 34 C92 22 80 66 40 70 C10 72 0 70 -30 84Z",
                shadow=False, line=False, extra='opacity=".25"')
    group(d, f"translate(0 {y}) scale(1 {s})", g)
    if not d.paper:
        for path, w in [("M-30 84 C10 46 40 90 80 54 C110 28 140 62 170 34 L230 22", 9), ("M-30 108 C10 82 40 118 80 88 C110 64 140 92 170 66 L230 54", 4)]:
            d.bands.append(f'<path transform="translate(0 {y})" d="{path}" fill="none" stroke="{d.c["spot"]}" stroke-width="{w}" stroke-linecap="round"/>')


def _stars(d: Drawing, pts):
    for x, y, r in pts:
        d.marks("light", circle(x, y, r))


NIGHT = {"hero": "#5EE6A8", "hero2": "#7FD8F0"}
NIGHT_FIX = {"sky": ["deep", "mark", "#1F2A44"]}
NIGHT_PALETTES = ["dusk", "coastal", "blush", "meadow"]


def aurora_cabin(d: Drawing):
    _stars(d, [(40, 30, 1.4), (150, 26, 1.6), (172, 60, 1.2), (24, 64, 1.2), (110, 18, 1.2)])
    _aurora(d, -4)
    _peaks(d, "far", [(-30, 126), (20, 104), (60, 120), (110, 96), (150, 116), (190, 102), (230, 118)])
    d.band("light", "M-30 136 Q100 128 230 136")
    for x, y, h in [(26, 146, 38), (44, 150, 26), (164, 144, 42), (180, 150, 30)]:
        d.shape("dark", _pine(x, y, h))
    d.shape("near", "M70 116 L100 94 L130 116 L130 152 L70 152Z")
    d.shape("light", "M62 120 L100 88 L138 120 L132 122 L100 96 L68 122Z")
    d.shape("dark", rrect(116, 92, 7, 16, 1))
    d.shape("light", rrect(114, 88, 11, 5, 2), shadow=False)
    d.shape("glow", rrect(78, 124, 16, 14, 2), shadow=False, spot=True)
    d.shape("glow", rrect(104, 124, 16, 28, 2), shadow=False)
    d.stroke("near", "M86 124 V138 M78 131 H94", 1.6, line=False)
    d.band("light", "M-30 158 Q100 148 230 158")


def aurora_lake(d: Drawing):
    _stars(d, [(30, 40, 1.4), (160, 24, 1.6), (176, 56, 1.2), (60, 20, 1.2), (130, 36, 1.0)])
    _aurora(d, 0)
    _peaks(d, "far", [(-30, 120), (16, 98), (40, 108), (78, 66), (110, 102), (136, 84), (170, 106), (230, 96)])
    for x in range(-14, 214, 9):
        d.shape("dark", _pine(x, 128 + (x % 2), 9 + (x * 7) % 6), shadow=False, line=False)
    d.band("dark", "M-30 126 Q100 122 230 126", shadow=False)
    d.band("mid", "M-30 130 Q100 126 230 130", line=False)
    d.shape("far", "M-30 130 L16 150 L40 142 L78 184 L110 146 L136 162 L170 144 L230 152 L230 130Z", shadow=False, line=False, extra='opacity=".45"')
    d.shape("hero", "M-30 168 C10 178 40 158 80 176 C110 188 140 168 170 180 L230 186 L230 192 C190 192 160 178 130 190 C100 198 70 184 40 186 C10 186 0 190 -30 188Z",
            shadow=False, line=False, extra='opacity=".5"')
    d.stroke("light", "M40 150 H64 M120 158 H150 M60 170 H84", 1.6, line=False)
    _line_only(d, "M40 150 H64 M120 158 H150 M60 170 H84", 1.6)
    d.band("light", "M-30 186 Q60 178 120 184 T230 182", line=False)


REINDEER = ("M60 120 C60 108 72 102 92 102 L116 102 C124 102 128 96 130 88 L134 74 C136 68 144 66 148 70 L160 80 "
            "Q164 86 158 89 L148 90 C146 100 144 112 136 120 C134 128 126 132 118 132 L76 132 C66 132 60 128 60 120Z")


def aurora_reindeer(d: Drawing):
    _stars(d, [(30, 50, 1.4), (170, 40, 1.6), (150, 72, 1.0), (56, 26, 1.2), (110, 24, 1.2)])
    _aurora(d, -10)
    d.band("far", "M-30 150 L30 132 L70 144 L120 126 L160 140 L230 130")
    d.band("light", "M-30 162 Q60 150 120 158 T230 152")

    def deer():
        d.limb("ground", "M140 72 L132 54 L122 42 M132 54 L140 40 M134 62 L124 60", 3.4)
        d.limb("ground", "M146 72 L152 52 L148 38 M152 52 L162 44 M150 60 L160 60", 3.4)
        for x1, x2 in [(70, 68), (82, 84), (118, 116), (128, 130)]:
            d.shape("ground", _bar(x1, 126, x2, 160, 6))
        d.shape("ground", REINDEER)
        d.shape("light", "M124 104 C128 112 136 114 142 106 L140 94 Q134 104 124 104Z", shadow=False)
        d.shape("light", "M58 116 Q54 108 62 108Z", shadow=False)
        d.marks("mark", circle(150, 79, 1.8))
        d.marks("mark", circle(161, 85, 2))
    group(d, "translate(-6 0)", deer)
    d.band("light", "M-30 172 Q100 164 230 172", line=False)


# ================================================================ APRES-SKI
def apres_mug(d: Drawing):
    d.disc("far", 100, 100, 70, line=False)
    _flakes(d, [(44, 56, 5), (156, 50, 6), (164, 92, 4), (36, 100, 4)])
    d.stroke("light", "M86 52 C78 42 94 36 86 24 M104 50 C96 40 112 34 104 22", 3)
    d.band("ground", "M-30 168 Q100 162 230 168")
    d.limb("hero", "M128 98 C150 98 152 132 128 134", 9)
    d.shape("hero", "M60 76 H132 L128 156 Q128 166 118 166 H74 Q64 166 64 156Z")
    d.shape("hero2", "M62 100 H131 L130.4 112 H62.6Z", shadow=False, spot=True)
    d.shape("light", "M56 78 C54 66 66 60 76 64 C80 54 96 52 102 60 C110 52 126 56 126 66 C136 66 140 76 134 80 C110 86 80 86 56 78Z")
    d.shape("light", rrect(70, 58, 12, 12, 3))
    d.shape("light", rrect(108, 60, 11, 11, 3))
    d.shape("pop", _bar(118, 74, 138, 34, 6), spot=True)
    d.stroke("light", "M122 66 L128 68 M126 58 L132 60 M130 50 L136 52 M134 42 L139 44", 2.4, line=False)


def apres_chalet(d: Drawing):
    d.disc("glow", 150, 44, 14)
    _peaks(d, "far", [(-30, 110), (20, 80), (56, 100), (100, 66), (150, 98), (230, 84)])
    for x, y, h in [(18, 140, 36), (34, 144, 26), (178, 140, 38)]:
        d.shape("deep", _pine(x, y, h))
    d.band("light", "M-30 144 Q100 136 230 144")
    d.shape("near", "M52 150 L52 112 L100 66 L148 112 L148 150Z")
    d.shape("dark", "M40 116 L100 56 L160 116 L152 120 L100 70 L48 120Z")
    d.shape("light", "M38 114 L100 52 L162 114 L156 116 L100 60 L44 116Z", shadow=False)
    d.shape("dark", rrect(128, 62, 9, 22, 1))
    d.shape("light", rrect(126, 58, 13, 6, 2), shadow=False)
    d.stroke("light", "M132 50 C126 42 138 36 130 26", 3, line=False)
    d.shape("glow2", "M86 96 L100 82 L114 96Z", shadow=False)
    d.shape("glow2", rrect(66, 116, 26, 18, 2), shadow=False, spot=True)
    d.shape("glow2", rrect(108, 116, 26, 18, 2), shadow=False, spot=True)
    d.stroke("near", "M79 116 V134 M121 116 V134 M66 125 H92 M108 125 H134", 1.6, line=False)
    d.shape("dark", rrect(48, 136, 104, 5, 2))
    d.shape("pop", _bar(156, 156, 166, 110, 5), spot=True)
    d.shape("hero", _bar(166, 158, 174, 112, 5))
    d.band("light", "M-30 154 Q100 146 230 154")


def apres_fondue(d: Drawing):
    d.disc("glow", 100, 96, 64, line=False)
    d.band("ground", "M-30 156 Q100 150 230 156")
    d.shape("dark", "M68 150 L74 128 H126 L132 150Z")
    d.shape("pop", "M92 140 C94 130 100 126 100 120 C104 128 108 132 108 140 C108 146 92 146 92 140Z", shadow=False)
    d.shape("hero", "M54 92 H146 C146 120 132 134 100 134 C68 134 54 120 54 92Z")
    d.shape("dark", rrect(144, 98, 26, 7, 3.5))
    d.shape("hero2", ellipse(100, 92, 46, 8), shadow=False, spot=True)
    d.shape("light", "M60 104 H140", shadow=False, line=False)
    d.stroke("light", "M64 106 Q100 114 136 106", 2.4, line=False)
    d.shape("dark", _bar(86, 84, 60, 28, 3))
    d.shape("dark", _bar(112, 84, 140, 26, 3))
    d.shape("pop", _bar(64, 36, 56, 20, 7), spot=True)
    d.shape("pop", _bar(136, 34, 144, 18, 7), spot=True)
    d.shape("ground", rrect(80, 74, 14, 14, 3), extra='transform="rotate(-20 87 81)"')
    d.shape("ground", rrect(106, 72, 14, 14, 3), extra='transform="rotate(18 113 79)"')
    d.shape("hero2", "M80 82 Q86 90 94 86 L94 92 Q86 94 82 90Z M108 84 Q114 92 120 86 L120 92 Q112 94 108 90Z", shadow=False, line=False)
    d.shape("hero2", "M62 96 Q66 108 70 100 Q72 94 76 98 L76 94 H62Z", shadow=False)
    d.band("near", "M-30 172 Q100 166 230 172", line=False)


# ================================================================ CONCEPTS
CONCEPTS = [
    Concept("skydive-freefall", "skydiving", "Freefall", sky_freefall, checks=[("hero", "mid"), ("hero", "near"), ("hero", "far")],
            fixes={"hero": ["pop", "deep", "dark"]}),
    Concept("skydive-canopy", "skydiving", "Canopy over the coast", sky_canopy, checks=[("hero", "sky"), ("hero2", "sky")],
            fixes={"hero2": ["light", "glow2", "pop"]}),
    Concept("skydive-plane", "skydiving", "Jump plane", sky_plane, checks=[("hero", "sky"), ("hero", "light")]),
    Concept("para-alps", "paragliding", "Over the Alps", para_alps, checks=[("hero", "sky"), ("hero2", "sky")],
            fixes={"hero2": ["light", "pop"]}),
    Concept("para-launch", "paragliding", "Launch & windsock", para_launch, checks=[("hero", "sky"), ("pop", "mid"), ("pop", "near")],
            fixes={"pop": ["hero2", "light"]}),
    Concept("para-eagle", "paragliding", "Eagle & glider", para_eagle, overrides={"hero": "#5B3A24", "hero2": "#F2B134"},
            checks=[("hero", "glow"), ("hero", "far"), ("hero", "sky")], fixes={"glow": ["glow2", "far", "light"]}),
    Concept("parasail-boat", "parasailing", "Boat & chute", parasail_boat, checks=[("hero", "near"), ("pop", "sky")],
            fixes={"pop": ["hero", "deep"], "hero": ["pop", "hero2"]}),
    Concept("parasail-chute", "parasailing", "Big canopy", parasail_chute, checks=[("hero", "sky"), ("hero", "light")]),
    Concept("parasail-beach", "parasailing", "Palm beach", parasail_beach, checks=[("pop", "sky"), ("pop", "glow"), ("dark", "glow"), ("dark", "sky")],
            fixes={"pop": ["hero", "deep"], "glow": ["glow2", "light"]}),
    Concept("heli-side", "helicopter-tour", "Helicopter", heli_side, checks=[("hero", "sky"), ("hero", "light")]),
    Concept("heli-canyon", "helicopter-tour", "Canyon flight", heli_canyon, checks=[("hero", "sky"), ("hero", "far")],
            fixes={"hero": ["pop", "deep", "dark"]}),
    Concept("heli-island", "helicopter-tour", "Island cliffs", heli_island, checks=[("hero", "sky"), ("hero", "mid"), ("light", "near")],
            fixes={"hero": ["pop", "hero2"]}),
    Concept("seaplane-floats", "seaplane-flight", "Floatplane landing", seaplane_floats, checks=[("hero", "sky"), ("dark", "near"), ("hero", "glow")],
            fixes={"glow": ["glow2", "light"]}),
    Concept("seaplane-lagoon", "seaplane-flight", "Lagoon bungalows", seaplane_lagoon, checks=[("hero", "sky"), ("ground", "sky2"), ("light", "sky2")],
            fixes={"sky2": ["mid", "near"]}),
    Concept("seaplane-dock", "seaplane-flight", "Lake dock", seaplane_dock, checks=[("hero", "mid"), ("hero", "near"), ("dark", "near")],
            fixes={"hero": ["pop", "hero2"]}),
    Concept("zip-jungle", "zip-lining", "Jungle zip line", zip_jungle, checks=[("hero", "sky"), ("hero", "mid"), ("dark", "sky")]),
    Concept("zip-trolley", "zip-lining", "Trolley close-up", zip_trolley, checks=[("hero", "sky"), ("pop", "mid"), ("pop", "near")],
            fixes={"pop": ["hero2", "dark"]}),
    Concept("zip-toucan", "zip-lining", "Toucan on the line", zip_toucan, overrides={"hero": "#F28F3B", "hero2": "#FFE8A3", "dark": "#1C1B22"},
            checks=[("dark", "sky"), ("dark", "far"), ("hero", "sky")]),
    Concept("bungee-bridge", "bungee-jumping", "Gorge bridge", bungee_bridge, checks=[("dark", "sky"), ("far", "sky")],
            fixes={"far": ["mid", "near"]}),
    Concept("bungee-dive", "bungee-jumping", "Swan dive", bungee_dive, checks=[("hero", "sky"), ("dark", "sky"), ("hero", "far"), ("pop", "sky")],
            fixes={"hero": ["pop", "hero2"]}),
    Concept("bungee-cliff", "bungee-jumping", "Cliff jump", bungee_cliff, checks=[("pop", "sky"), ("dark", "sky"), ("mid", "sky")]),
    Concept("ski-chairlift", "skiing", "Chairlift", ski_chairlift, checks=[("hero", "sky"), ("pop", "sky"), ("pop", "far"), ("light", "mid"), ("dark", "sky")],
            fixes={"pop": ["hero2", "deep"]}),
    Concept("ski-boot", "skiing", "Boot & binding", ski_boot, checks=[("hero", "far"), ("hero", "mid"), ("hero2", "light"), ("light", "mid")],
            fixes={"hero2": ["pop", "hero"], "hero": ["pop", "deep"]}),
    Concept("ski-matterhorn", "skiing", "Matterhorn pistes", ski_matterhorn, checks=[("mid", "sky"), ("light", "mid"), ("light", "far")]),
    Concept("board-planted", "snowboarding", "Board in the snow", board_planted, checks=[("hero", "far"), ("hero", "sky"), ("light", "mid")],
            fixes={"hero": ["pop", "deep"]}),
    Concept("board-goggles", "snowboarding", "Goggles", board_goggles, checks=[("pop", "sky"), ("pop", "far"), ("mid", "glow2"), ("dark", "sky")]),
    Concept("board-jump", "snowboarding", "Big air", board_jump, checks=[("hero", "glow"), ("dark", "glow"), ("hero2", "glow"), ("hero", "sky")],
            fixes={"hero2": ["pop", "light"], "glow": ["glow2", "far", "light"]}),
    Concept("husky-portrait", "dog-sledding", "Husky", husky_head, overrides={"hero": "#5F6B7A", "hero2": "#E8A0A0", "pop": "#6EC6F0", "mark": "#1E2430"},
            checks=[("hero", "sky"), ("hero", "far"), ("light", "hero")], fixes={"far": ["mid", "near"]}),
    Concept("sled-team", "dog-sledding", "Husky team", sled_team, checks=[("dark", "glow"), ("dark", "light"), ("hero2", "glow"), ("light", "far")],
            fixes={"glow": ["glow2", "far"]}),
    Concept("sled-trail", "dog-sledding", "Forest trail", sled_trail, checks=[("light", "far"), ("mid", "light"), ("deep", "light")]),
    Concept("snowmobile-side", "snowmobiling", "Snowmobile", sm_side, checks=[("hero", "sky"), ("hero", "light"), ("pop", "sky"), ("dark", "light")],
            fixes={"pop": ["hero2", "deep"]}),
    Concept("snowmobile-lake", "snowmobiling", "Frozen lake", sm_lake, overrides={"sky2": "#A9D6E5"}, checks=[("hero", "light"), ("light", "sky2"), ("light", "mid")],
            fixes={"sky2": ["far", "mid"]}),
    Concept("snowmobile-jump", "snowmobiling", "Jump", sm_jump, checks=[("hero", "glow"), ("pop", "glow"), ("dark", "glow")],
            fixes={"glow": ["light", "far", "glow2"]}),
    Concept("skate-boot", "ice-skating", "Figure skate", skate_boot, checks=[("light", "mid"), ("hero", "light"), ("dark", "mid")]),
    Concept("skate-rink", "ice-skating", "City rink", skate_rink, checks=[("deep", "sky"), ("deep", "far"), ("far", "sky"), ("pop", "deep")],
            fixes={"far": ["mid", "near"]}),
    Concept("skate-pond", "ice-skating", "Frozen pond", skate_pond, overrides={"sky2": "#A9D6E5"}, checks=[("sky2", "light"), ("hero", "sky2"), ("light", "far")],
            fixes={"sky2": ["far", "mid"]}),
    Concept("aurora-cabin", "northern-lights", "Cabin & aurora", aurora_cabin, NIGHT_PALETTES, overrides=NIGHT,
            checks=[("sky", "light"), ("hero", "sky"), ("far", "sky"), ("dark", "light"), ("near", "light")], fixes=NIGHT_FIX),
    Concept("aurora-lake", "northern-lights", "Mountain lake", aurora_lake, NIGHT_PALETTES, overrides=NIGHT,
            checks=[("sky", "light"), ("hero", "sky"), ("far", "sky"), ("dark", "far")], fixes=NIGHT_FIX),
    Concept("aurora-reindeer", "northern-lights", "Reindeer", aurora_reindeer, NIGHT_PALETTES, overrides={**NIGHT, "ground": "#9C6B43"},
            checks=[("sky", "light"), ("hero", "sky"), ("ground", "sky"), ("ground", "light"), ("far", "sky")], fixes=NIGHT_FIX),
    Concept("apres-mug", "apres-ski", "Hot chocolate", apres_mug, checks=[("hero", "far"), ("light", "far"), ("hero", "ground")],
            fixes={"hero": ["pop", "deep"]}),
    Concept("apres-chalet", "apres-ski", "Chalet", apres_chalet, checks=[("near", "light"), ("dark", "sky"), ("glow2", "near")],
            fixes={"dark": ["deep", "mid"]}),
    Concept("apres-fondue", "apres-ski", "Fondue", apres_fondue, overrides={"hero2": "#F6C453"},
            checks=[("hero", "glow"), ("hero2", "hero"), ("ground", "glow")], fixes={"glow": ["far", "mid", "sky2"]}),
]
