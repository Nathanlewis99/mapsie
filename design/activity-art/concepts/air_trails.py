"""Air & trails: three concepts each for hang gliding, scenic flights, gliding, microlights,
skywalks, giant swings, drone photography, multi-day treks, bouldering, via ferrata,
abseiling, dirt biking and e-bike tours."""
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


def _line_only(d: Drawing, path: str, w: float = 2.4):
    """An extra line drawn only in line style (clipped to the circle like the bands)."""
    if not d.paper:
        d.bands.append(f'<path d="{path}" fill="none" stroke="{d.c["ink"]}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')


def _ink(d: Drawing, role: str) -> str:
    """A role's colour in papercut, the pen ink in line style."""
    return d.c[role] if d.paper else d.c["ink"]


def _land(d: Drawing, role: str, shape: str, edge: str, shadow: bool = True):
    """A landmass running off the canvas: filled in papercut, just its edge in line style."""
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


def _hanging_rider(d: Drawing, x, y, s=1.0, body="dark", helmet="pop"):
    """A small figure hanging upright in a harness from (x, y), legs dangling."""
    def fig():
        d.limb(body, "M-3 18 L-4 32 M3 18 L5 32", 4.2)
        d.shape(body, rrect(-5.5, 5, 11, 16, 5))
        d.limb(body, "M-4 9 L-8 -4 M4 9 L8 -4", 3.4, shadow=False)
        d.shape(helmet, circle(0, 0, 5.4))
    group(d, f"translate({x} {y}) scale({s})", fig)


def _snowcaps(d: Drawing, caps):
    for x, y, w in caps:
        d.shape("light", f"M{x} {y} L{x + w} {y + w*1.1} L{x + w*0.45} {y + w*0.9} L{x} {y + w*1.3} "
                         f"L{x - w*0.45} {y + w*0.9} L{x - w} {y + w*1.1}Z", shadow=False)


def _windsock(d: Drawing, x, y, h=44, flip=False):
    k = -1 if flip else 1
    d.shape("dark", rrect(x - 1.6, y - h, 3.2, h, 1.5))
    d.shape("pop", f"M{x + 2*k} {y - h} L{x + 28*k} {y - h + 4} L{x + 26*k} {y - h + 14} L{x + 2*k} {y - h + 18}Z", spot=True)
    d.shape("light", f"M{x + 9*k} {y - h + 0.9} L{x + 15*k} {y - h + 1.8} L{x + 15*k} {y - h + 16} L{x + 9*k} {y - h + 16.9}Z", shadow=False)
    d.shape("light", f"M{x + 21*k} {y - h + 2.7} L{x + 26.5*k} {y - h + 3.6} L{x + 26*k} {y - h + 14} L{x + 21*k} {y - h + 14.6}Z", shadow=False)


# ================================================================ HANG GLIDING
def _delta(d: Drawing, sail="hero", alt="hero2", pilot=True, suit="dark", helmet="pop"):
    """A hang glider seen from the front and below, nose at (0, 12), span about +-84."""
    nose = (0, 12)
    trail = [(84, 6), (58, -10), (30, -20), (0, -24), (-30, -20), (-58, -10), (-84, 6)]
    edge = "M-84 6 Q-40 22 0 12 Q40 22 84 6"
    te = " ".join(f"Q{(a[0] + b[0]) / 2 * 0.96:.1f} {(a[1] + b[1]) / 2 + 3:.1f} {b[0]} {b[1]}" for a, b in zip(trail, trail[1:]))
    d.shape(sail, f"{edge} {te}Z")
    for i in range(1, len(trail) - 1, 2):
        a, b = trail[i], trail[i + 1]
        d.shape(alt, _poly([nose, a, ((a[0] + b[0]) / 2 * 0.96, (a[1] + b[1]) / 2 + 3), b]), shadow=False, spot=True)
    d.stroke("dark", "M0 12 L0 -24", 1.6, line=False)
    # A-frame and control bar
    d.stroke("dark", "M0 12 L-22 62 H22 Z", 2.4)
    if pilot:
        d.stroke("dark", "M0 12 L0 30", 1.4)
        d.shape(suit, rrect(-8, 36, 16, 16, 6))
        d.limb(suit, "M-6 41 L-17 59 M6 41 L17 59", 3.6, shadow=False)
        d.shape(helmet, circle(0, 32, 7))
        d.shape("dark", "M-5 31 Q0 28 5 31 L5 34 Q0 32 -5 34Z", shadow=False, line=False)


def hang_delta(d: Drawing):
    d.disc("glow", 46, 44, 15)
    d.shape("light", cloud(136, 40, 0.8))
    d.band("far", waves(146, 3, 40))
    d.band("mid", waves(164, 3, 34), line=False)
    cliff = "M-30 130 L30 128 L50 136 L66 160 L76 176 L84 230 L-30 230Z"
    _land(d, "near", cliff, "M-30 130 L30 128 L50 136 L66 160 L76 176 L84 230")
    d.shape("deep", "M30 128 L50 136 L66 160 L76 176 L84 230 L70 230 L62 176 L44 144Z", shadow=False, line=False)
    d.shape("ground", "M84 230 Q120 186 230 180 L230 230Z", line=False)
    _line_only(d, "M84 230 Q120 186 230 180", 3)
    group(d, "translate(102 78) rotate(-7) scale(.98)", lambda: _delta(d))


def hang_ramp(d: Drawing):
    d.disc("glow", 152, 132, 18)
    d.band("far", "M-30 150 L20 132 L56 146 L96 124 L140 150 L180 136 L230 152")
    d.band("mid", hills(172, 8, 20))
    d.band("deep", hills(188, 4, 30), line=False)
    cliff = "M-30 108 L34 104 L46 112 L52 140 L60 160 L58 230 L-30 230Z"
    _land(d, "near", cliff, "M-30 108 L34 104 L46 112 L52 140 L60 160 L58 230")
    for x, y, h in [(-4, 108, 22), (10, 106, 18)]:
        d.shape("deep", _pine(x, y, h))
    # wooden launch ramp sticking out over the drop
    d.stroke("dark", "M48 113 L54 126 M62 117 L56 132 M70 120 L57 134", 2.4)
    d.shape("hero2", "M20 104 L82 118 L81 123 L20 110Z", spot=True)
    d.stroke("dark", "M28 106 V112 M44 109.5 V115.5 M60 113 V119 M76 116.5 V122", 1, line=False)
    _windsock(d, 24, 106, 32, flip=True)
    group(d, "translate(128 62) rotate(-12) scale(.62)", lambda: _delta(d))
    d.shape("light", cloud(54, 46, 0.8))


def hang_rio(d: Drawing):
    d.disc("glow", 60, 50, 15)
    d.shape("light", cloud(112, 34, 0.7))
    d.band("far", "M-30 130 L230 130", line=False)
    # Corcovado with the statue, then Sugarloaf and Urca
    d.shape("near", "M-30 134 L4 98 L20 80 L34 96 L58 134Z")
    d.shape("dark", "M18.8 66 h2.4 v14 h-2.4Z M14 69.5 h12 v2.2 h-12Z")
    d.stroke("dark", "M126 112 L158 74", 0.9)
    d.shape("deep", "M106 134 C108 118 116 110 126 110 C136 110 142 120 144 134Z")
    d.shape("mid", "M136 134 C138 98 146 72 160 70 C174 70 182 100 186 134Z")
    d.shape("light", rrect(140, 89, 6, 5, 1.5))
    d.band("mid", waves(134, 2, 40))
    d.band("near", waves(150, 3, 34), line=False)
    d.band("ground", "M-30 172 Q60 158 120 168 T230 164")
    d.band("deep", hills(188, 4, 20), line=False)
    group(d, "translate(82 80) rotate(8) scale(.5)", lambda: _delta(d, sail="pop", alt="light"))


# ================================================================ SCENIC FLIGHT
def _cessna(d: Drawing, body="hero", trim="hero2"):
    """A high-wing light aircraft facing right, roughly x 26-166, y 70-130."""
    d.stroke("dark", "M120 112 L126 124 M146 110 L150 124", 2.4)
    d.marks("dark", circle(126, 126, 5) + circle(150, 126, 5) + circle(38, 108, 2.6))
    d.stroke("dark", "M38 104 L38 108", 1.6)
    d.shape(body, "M30 96 L60 94 L60 100 L30 102Z")
    d.shape(body, "M34 104 L30 72 Q31 68 36 69 L60 92 L112 88 L120 80 L138 80 Q150 84 156 94 L160 100 "
                  "Q161 108 152 110 L124 114 L66 108 Z")
    d.shape(trim, "M36 70 L42 70 L58 90 L40 92Z", shadow=False, spot=True)
    d.shape(trim, "M48 101 L158 99 L158 104 Q156 108 152 108 L124 112 L66 107Z", shadow=False, spot=True)
    d.shape("light", "M139 83 Q147 86 152 94 L140 94Z", shadow=False)
    d.shape("light", rrect(116, 84, 20, 10, 2.5), shadow=False)
    d.stroke("dark", "M116 110 L134 80", 2)
    d.shape(trim, rrect(96, 73, 64, 7, 3.5))
    d.shape("dark", ellipse(162, 102, 3, 4))
    d.shape("dark", ellipse(165, 102, 2.4, 17), shadow=False)


def _plane_top(d: Drawing, body="hero", trim="hero2"):
    """A small aircraft seen from above, nose pointing up, centred on (0, 0)."""
    d.shape(body, "M-46 -8 L46 -8 L45 0 L-45 0Z")
    d.shape(body, rrect(-14, 22, 28, 6, 2.5))
    d.shape(body, "M0 -32 Q6 -30 6 -18 L3 30 L-3 30 L-6 -18 Q-6 -30 0 -32Z")
    d.shape(trim, "M-46 -8 L-38 -8 L-38 0 L-45 0Z M46 -8 L38 -8 L38 0 L45 0Z", shadow=False, spot=True)
    d.shape("light", ellipse(0, -16, 3.5, 6), shadow=False)
    d.shape("dark", rrect(-10, -36, 20, 2.6, 1.3), shadow=False)


def scenic_cessna(d: Drawing):
    d.disc("glow", 150, 50, 16)
    d.band("far", "M-30 136 L14 112 L40 126 L76 92 L106 120 L136 100 L170 124 L200 110 L230 124")
    _snowcaps(d, [(76, 92, 9), (136, 100, 8), (14, 112, 6), (200, 110, 6)])
    d.band("mid", hills(154, 10, 20))
    d.band("near", hills(172, 8, -10))
    d.shape("light", cloud(16, 150, 1.1))
    d.shape("light", cloud(140, 160, 0.9))
    d.band("deep", hills(188, 4, 30), line=False)
    d.shape("light", cloud(26, 52, 0.8))
    group(d, "translate(100 96) rotate(-6) translate(-98 -100)", lambda: _cessna(d))


def scenic_nazca(d: Drawing):
    d.disc("glow", 150, 30, 12)
    d.band("far", "M-30 52 L10 40 L36 48 L70 34 L104 46 L140 38 L176 50 L230 42")
    d.band("ground", "M-30 56 Q100 50 230 56")
    d.shape("mid", "M-30 130 Q30 110 60 140 T120 230 L-30 230Z", shadow=False, line=False)
    bird = ("M100 104 L100 166 "
            "M96 104 a4 4 0 1 1 8 0 "
            "M93 100 C90 90 92 78 100 74 C108 78 110 90 107 100 "
            "M93 92 L50 74 L48 81 L57 84 L46 88 L57 91 L48 96 L94 99 "
            "M107 92 L150 74 L152 81 L143 84 L154 88 L143 91 L152 96 L106 99 "
            "M96 76 L88 58 L93 56 L98 70 L100 54 L104 54 L102 70 L107 56 L112 58 L104 76")
    group(d, "translate(96 116) scale(1.18 .92) translate(-100 -110)", lambda: d.stroke("light", bird, 2.6))
    group(d, "translate(158 72) rotate(-60) scale(.56)", lambda: _plane_top(d))


def scenic_heart(d: Drawing):
    d.band("mid", "M-30 -30 L230 -30")
    d.shape("far", "M-30 150 C20 130 60 150 96 146 C140 142 170 160 230 140 L230 230 L-30 230Z", shadow=False, line=False)
    d.shape("far", "M150 -30 C140 10 170 40 230 40 L230 -30Z", shadow=False, line=False)
    d.stroke("light", "M-30 150 C20 130 60 150 96 146 C140 142 170 160 230 140", 2.2, line=False)
    _line_only(d, "M-30 150 C20 130 60 150 96 146 C140 142 170 160 230 140", 2.4)
    heart = "M92 82 C84 66 56 66 56 90 C56 110 78 122 92 140 C106 122 128 110 128 90 C128 66 100 66 92 82Z"
    d.shape("light", "M92 76 C82 58 50 60 50 90 C50 114 76 126 92 148 C108 126 134 114 134 90 C134 60 102 58 92 76Z", line=False)
    d.shape("pop", heart, spot=True)
    d.marks("deep", "".join(circle(x, y, r) for x, y, r in [(72, 88, 3), (84, 100, 2.4), (104, 96, 3), (112, 86, 2), (94, 116, 2.6), (78, 104, 1.8), (100, 126, 1.8)]))
    d.stroke("light", "M30 60 q6 -4 12 0 M150 112 q6 -4 12 0 M40 182 q6 -4 12 0 M150 186 q6 -4 12 0", 1.8, line=False)
    group(d, "translate(150 64) rotate(-35) scale(.62)", lambda: _plane_top(d, body="light", trim="hero"))


# ================================================================ GLIDING
def _sailplane_top(d: Drawing, body="light", trim="pop"):
    """A sailplane from below/above: very long thin wings, T-tail, nose up, centred on (0, 0)."""
    d.shape(body, "M-94 2 L-8 -6 L8 -6 L94 2 L94 6 L8 4 L-8 4 L-94 6Z")
    d.shape(body, rrect(-16, 40, 32, 5, 2.5))
    d.shape(body, "M0 -40 Q6 -36 6 -20 L2.4 46 L-2.4 46 L-6 -20 Q-6 -36 0 -40Z")
    d.shape(trim, "M-94 2 L-80 0.7 L-80 5.6 L-94 6Z M94 2 L80 0.7 L80 5.6 L94 6Z", shadow=False, spot=True)
    d.shape(trim, rrect(-2.4, 36, 4.8, 10, 1.5), shadow=False, spot=True)
    d.shape("dark", ellipse(0, -24, 3.6, 9), shadow=False)


def glide_airfield(d: Drawing):
    d.disc("glow", 46, 54, 16)
    d.shape("light", cloud(130, 30, 0.8))
    d.band("far", hills(140, 10, 20))
    d.band("mid", "M-30 162 Q60 148 120 156 T230 150")
    d.stroke("ground", "M-30 176 Q60 164 120 170 T230 166", 4, line=False)
    d.band("near", hills(186, 5, 10), line=False)
    d.shape("light", cloud(-4, 140, 1.0))

    def glider():
        # far wing rising up and away, near wing sweeping down towards us
        d.shape("hero", "M116 95 L130 95 L170 26 L165 25Z")
        d.shape("hero2", "M170 26 L165 25 L159 36 L165 37Z", shadow=False, spot=True)
        d.shape("hero", "M34 101 L38 62 L48 62 L54 99Z")
        d.shape("hero", "M26 62 L60 60 L60 65 L26 66Z")
        d.shape("hero2", "M40 63 L48 63 L46 72 L39 72Z", shadow=False, spot=True)
        d.shape("hero", "M162 102 Q160 91 142 89 L122 91 Q96 95 50 97 L34 99 L34 104 L50 104 Q96 106 122 110 Q152 112 162 102Z")
        d.shape("dark", "M124 91 Q132 82 146 86 Q154 89 156 95 Q140 92 124 91Z")
        d.shape("light", "M134 86 Q142 85 148 89 L136 89Z", shadow=False, line=False)
        d.shape("hero", "M112 104 L132 104 L82 182 L70 182Z")
        d.shape("hero2", "M82 182 L70 182 L76 172 L88 172Z", shadow=False, spot=True)
    group(d, "translate(100 100) rotate(-8) scale(.98) translate(-100 -104)", glider)


def glide_tow(d: Drawing):
    def fields():
        roles = ["far", "mid", "ground", "near", "mid", "far", "ground", "mid", "near"]
        k = 0
        for gy in range(-60, 260, 44):
            for gx in range(-60, 260, 50):
                d.shape(roles[k % len(roles)], rrect(gx, gy, 48, 42, 3), shadow=False, line=False)
                k += 1
            k += 2
    group(d, "rotate(-14 100 100)", fields)
    _line_only(d, "M-30 70 L230 20 M-30 160 L230 110 M60 -30 L90 230", 1.6)
    d.stroke("light", "M-10 150 C40 140 70 170 110 150 S170 120 210 130", 4, line=False)
    d.shape("light", cloud(10, 60, 1.1))
    d.shape("light", cloud(138, 170, 1.0))
    d.stroke("dark", "M88 108 L152 52", 1.2)
    group(d, "translate(158 46) rotate(48) scale(.5)", lambda: _plane_top(d, body="pop", trim="light"))
    group(d, "translate(80 124) rotate(48) scale(.82)", lambda: _sailplane_top(d, body="light", trim="pop"))


def glide_thermal(d: Drawing):
    d.disc("glow", 152, 50, 16)
    d.shape("light", cloud(-10, 170, 2.2))
    d.shape("light", cloud(110, 176, 1.8))
    d.shape("light", cloud(20, 54, 0.8))
    d.stroke("light", "M60 186 Q40 150 70 136 Q100 124 120 140", 2, line=False)
    # a hawk sharing the thermal
    d.shape("dark", "M150 112 Q140 104 128 106 Q140 108 146 114 L150 118 L154 114 Q160 108 172 106 Q160 104 150 112Z")
    group(d, "translate(98 92) rotate(-18) scale(.92)", lambda: _sailplane_top(d, body="hero", trim="hero2"))


# ================================================================ MICROLIGHT
def _trike(d: Drawing, wing="hero", alt="hero2", pod="pop", sil=None):
    """A flex-wing microlight trike in three-quarter view facing right, wing nose at (162, 52)."""
    w = sil or wing
    a = sil or alt
    p = sil or pod
    dk = sil or "dark"
    lt = sil or "light"
    d.stroke(dk, "M108 62 L104 104 M114 60 L130 90 L120 96", 2.4)
    # sail: nose front-right, trailing edge back-left
    d.shape(w, "M162 52 Q120 34 70 26 Q60 40 50 56 Q44 66 34 76 Q100 70 162 52Z")
    d.shape(a, "M162 52 L70 26 Q66 34 62 40Z", shadow=False, spot=sil is None)
    d.shape(a, "M162 52 L54 52 Q46 62 40 70Z", shadow=False, spot=sil is None)
    # pod, seats and wheels
    d.stroke(dk, "M88 120 L82 132 M118 120 L122 132 M142 114 L148 132", 2.6)
    d.marks(dk, circle(80, 134, 6) + circle(122, 134, 6) + circle(148, 134, 6))
    d.shape(p, "M76 112 Q78 100 92 100 L126 102 Q146 104 152 114 Q146 122 126 122 L90 122 Q78 122 76 112Z")
    d.shape(lt, "M128 103 Q144 106 150 113 L128 113Z", shadow=False)
    d.shape(dk, circle(98, 92, 6))
    d.shape(dk, circle(116, 94, 6))
    d.shape(dk, "M92 98 h12 v6 h-12Z M110 100 h12 v6 h-12Z", shadow=False)
    # pusher propeller
    d.shape(dk, ellipse(70, 110, 2.6, 18), shadow=False)
    d.marks(dk, circle(73, 110, 3))


def micro_trike(d: Drawing):
    d.disc("glow", 46, 50, 16)
    d.shape("light", cloud(138, 30, 0.8))
    d.band("far", hills(150, 12, 20))
    d.band("mid", "M-30 168 Q60 152 120 162 T230 156")
    d.stroke("ground", "M-30 182 Q60 168 120 176 T230 172", 4, line=False)
    d.band("near", hills(188, 5, 10), line=False)
    d.shape("light", cloud(10, 140, 1.0))
    group(d, "translate(100 96) rotate(-4) scale(1.05) translate(-98 -82)", lambda: _trike(d))


def micro_falls(d: Drawing):
    d.disc("glow", 160, 40, 13)
    d.band("far", "M-30 96 Q100 90 230 96")
    d.band("sky2", "M-30 104 Q100 100 230 104")
    d.stroke("light", "M10 101 h18 M70 100 h22 M140 101 h20", 1.6, line=False)
    # the curtain of water dropping into the gorge, broken by rocky buttresses
    d.band("deep", "M-30 110 Q100 106 230 110", line=False)
    for x0, x1 in [(-30, 30), (40, 112), (124, 230)]:
        d.shape("light", f"M{x0} 110 L{x1} 109 L{x1} 160 L{x0} 160Z", shadow=False, line=False)
    d.shape("near", "M30 109 L40 109 L42 160 L28 160Z M112 109 L124 109 L126 160 L110 160Z", shadow=False, line=False)
    _line_only(d, "M-30 110 Q100 106 230 110", 3)
    _line_only(d, "M30 110 L28 150 M40 110 L42 150 M112 110 L110 150 M124 110 L126 150", 2)
    d.stroke("sky2", "M6 114 V150 M20 112 V152 M52 112 V150 M66 112 V152 M82 111 V150 M98 111 V152 "
                     "M136 112 V152 M152 112 V150 M168 112 V152 M184 113 V150", 2.4, line=False)
    d.band("deep", "M-30 150 Q100 146 230 150", line=False)
    for x, y, s in [(-10, 150, 1.5), (40, 142, 1.3), (96, 150, 1.6), (150, 144, 1.3)]:
        d.shape("light", cloud(x, y, s), shadow=False, line=False)
    d.stroke("pop", "M52 150 A54 46 0 0 1 160 150", 3, line=False)
    d.stroke("hero2", "M57 150 A49 41 0 0 1 155 150", 3, line=False)
    d.stroke("far", "M62 150 A44 36 0 0 1 150 150", 3, line=False)
    _line_only(d, "M56 150 A50 42 0 0 1 156 150", 2)
    d.band("near", "M-30 172 Q40 160 100 168 T230 162")
    for x, y, h in [(26, 172, 18), (40, 170, 14), (166, 166, 18), (180, 168, 14)]:
        d.shape("deep", _pine(x, y, h), line=False)
    group(d, "translate(74 56) rotate(-6) scale(.52) translate(-98 -82)", lambda: _trike(d))


def micro_sunset(d: Drawing):
    d.disc("glow", 100, 106, 52)
    d.disc("glow2", 100, 106, 34, shadow=False, line=False)
    d.band("far", hills(156, 6))
    for x, s in [(32, 0.62), (160, 0.5)]:
        group(d, f"translate({x} 156) scale({s})", lambda: (
            d.limb("dark", "M0 0 L0 -22 M0 -14 L-10 -26 M0 -16 L12 -28", 3.6),
            d.shape("dark", "M-28 -26 Q-6 -42 26 -34 Q36 -30 34 -26 Q6 -22 -28 -26Z")))
    d.band("deep", hills(176, 5, 20))
    d.stroke("dark", "M30 70 q4 -4 8 0 q4 -4 8 0 M152 62 q3 -3 6 0 q3 -3 6 0", 1.8)
    group(d, "translate(104 92) rotate(-6) scale(.86) translate(-98 -82)", lambda: _trike(d, sil="dark"))


# ================================================================ SKYWALK
def skywalk_horseshoe(d: Drawing):
    d.disc("glow", 160, 46, 14)
    d.band("far", "M-30 80 H60 L66 88 H120 L126 78 H230")
    d.band("mid", "M-30 110 H70 L78 120 H130 L138 108 H230")
    d.band("near", "M-30 142 H80 L88 152 H140 L150 138 H230")
    d.band("deep", "M-30 174 Q60 168 100 172 T230 170")
    d.stroke("sky2", "M80 230 Q90 196 120 186 T150 172", 4, line=False)
    _land(d, "ground", "M-30 92 H46 L50 230 H-30Z", "M-30 92 H46 L50 230")
    d.shape("near", "M32 92 H46 L50 230 H38Z", shadow=False, line=False)
    d.stroke("dark", "M-30 108 H42 M-30 132 H44 M-30 160 H45", 1.2, line=False)
    # the horseshoe seen from above: a glass-walled U over the void
    d.shape("dark", "M44 128 H138 A20 16 0 0 0 158 112 L158 117 A20 16 0 0 1 138 133 H44Z", shadow=False)
    d.shape("light", "M44 96 H138 A20 16 0 0 1 138 128 H44Z M44 104 H136 A10 8 0 0 1 136 120 H44Z", extra='fill-rule="evenodd"')
    d.stroke("dark", "M44 104 H136 A10 8 0 0 1 136 120 H44", 1.2, line=False)
    # people on the far arm and at the tip
    for x, y, role in [(70, 101, "pop"), (100, 101, "hero"), (146, 112, "hero2")]:
        d.limb("dark", f"M{x} {y} V{y - 6}", 2.6, shadow=False)
        d.shape(role, rrect(x - 3, y - 15, 6, 10, 3), shadow=False)
        d.marks("dark", circle(x, y - 18, 2.8))
    d.raw('<path d="M44 96 H138 A20 16 0 0 1 158 112 L158 103 A20 16 0 0 0 138 87 H44Z M44 128 H138 A20 16 0 0 0 158 112 '
          'L158 103 A20 16 0 0 1 138 119 H44Z" fill="#fff" opacity=".45"/>', "")
    d.stroke("dark", "M44 87 H138 A20 16 0 0 1 138 119 H44", 1.6)
    d.stroke("dark", "M64 87 V96 M88 87 V96 M112 87 V96 M136 87 V96 M64 119 V128 M88 119 V128 M112 119 V128 M136 119 V128 M157 103 V112", 1)


def skywalk_glass(d: Drawing):
    # looking straight down through the glass floor
    d.band("mid", "M-30 -30 L230 -30")
    d.shape("near", "M-30 40 C30 60 40 120 10 230 L-30 230Z", shadow=False, line=False)
    d.shape("near", "M230 20 C170 50 166 140 200 230 L230 230Z", shadow=False, line=False)
    d.stroke("sky2", "M60 -10 C70 40 120 50 110 100 C100 150 140 170 130 210", 7, line=False)
    _line_only(d, "M60 -10 C70 40 120 50 110 100 C100 150 140 170 130 210", 2)
    d.marks("deep", "".join(circle(x, y, r) for x, y, r in [(30, 30, 5), (40, 40, 4), (24, 46, 4), (160, 70, 5), (150, 82, 4),
                                                               (170, 150, 5), (40, 150, 4), (52, 160, 5), (150, 30, 4)]))
    d.shape("light", cloud(130, 120, 0.7), shadow=False, line=False)
    d.raw('<g fill="#fff" opacity=".25"><rect x="-10" y="-10" width="220" height="220"/></g>', "")
    d.stroke("light", "M-10 70 H210 M66 -10 V210 M134 -10 V210", 3)
    d.raw('<path d="M12 50 L50 12 M150 190 L190 150" stroke="#fff" stroke-width="4" opacity=".7" stroke-linecap="round"/>', "")

    def shoe():
        d.limb("hero", "M0 30 L0 70", 20, shadow=False)
        d.shape("dark", "M0 -32 C11 -32 15 -20 14 -8 C13 2 10 8 10 16 C10 28 -10 28 -10 16 C-10 8 -14 2 -14 -8 C-15 -20 -11 -32 0 -32Z")
        d.shape("hero2", "M0 -29 C9 -29 12 -19 11 -8 C10 1 8 7 8 15 C8 24 -8 24 -8 15 C-8 7 -11 1 -11 -8 C-12 -19 -9 -29 0 -29Z", shadow=False, spot=True)
        d.stroke("light", "M-5 -10 H5 M-5 -4 H5 M-5 2 H5", 1.6)
        d.shape("hero", ellipse(0, 14, 8, 8), shadow=False)
    group(d, "translate(80 106) rotate(-8)", shoe)
    group(d, "translate(120 112) rotate(8)", shoe)


def skywalk_tower(d: Drawing):
    d.disc("glow", 50, 58, 16)
    d.shape("light", cloud(136, 120, 0.9))
    for x, w, h, role in [(-10, 22, 46, "far"), (14, 18, 30, "far"), (34, 16, 56, "far"), (138, 20, 50, "far"), (160, 24, 36, "far"), (186, 20, 54, "far")]:
        d.shape(role, rrect(x, 190 - h, w, h + 20, 1), line=False)
    d.band("far", "M-30 178 L230 178")
    d.shape("deep", "M92 230 L96 110 H104 L108 230Z")
    d.shape("deep", "M98 20 H102 L103 66 H97Z")
    d.shape("mid", "M70 72 H130 L138 82 H62Z")
    d.shape("hero2", rrect(60, 82, 80, 12, 4), spot=True)
    d.shape("mid", "M64 94 H136 L118 110 H82Z")
    d.shape("light", "M70 85 H130 V91 H70Z", shadow=False)
    d.stroke("dark", "M60 94 H140", 1.8)
    d.stroke("dark", "M58 70 H142", 1.6)
    # edge-walkers leaning out on their tethers
    d.stroke("dark", "M66 70 L54 80 M134 70 L146 80", 1)
    group(d, "translate(52 82) rotate(-28) scale(.6)", lambda: _hanging_rider(d, 0, 0, 1, body="dark", helmet="pop"))
    group(d, "translate(148 82) rotate(28) scale(.6)", lambda: _hanging_rider(d, 0, 0, 1, body="dark", helmet="hero"))
    d.band("near", "M-30 186 Q100 180 230 186", line=False)


# ================================================================ GIANT SWING
def swing_canyon(d: Drawing):
    d.disc("glow", 100, 128, 30)
    d.band("far", "M-30 150 L20 136 L60 150 L100 140 L140 150 L180 134 L230 150")
    d.band("deep", "M-30 180 Q100 172 230 180", line=False)
    left = "M-30 28 L30 30 L36 60 L30 96 L40 140 L34 180 L44 230 L-30 230Z"
    right = "M230 28 L170 30 L164 64 L172 100 L160 140 L168 180 L156 230 L230 230Z"
    _land(d, "near", left, "M-30 28 L30 30 L36 60 L30 96 L40 140 L34 180 L44 230")
    _land(d, "near", right, "M230 28 L170 30 L164 64 L172 100 L160 140 L168 180 L156 230")
    d.shape("deep", "M30 30 L36 60 L30 96 L40 140 L34 180 L44 230 L34 230 L26 180 L30 140 L22 96 L28 60Z", shadow=False, line=False)
    d.shape("deep", "M170 30 L164 64 L172 100 L160 140 L168 180 L156 230 L166 230 L176 180 L170 140 L180 100 L174 64Z", shadow=False, line=False)
    d.stroke("dark", "M28 30 Q100 44 172 30", 2.2)
    d.raw('<path d="M60 112 A84 84 0 0 0 132 120" fill="none" stroke="#fff" stroke-width="2" stroke-dasharray="4 5" opacity=".9"/>', "")
    d.stroke("dark", "M100 38 L136 104", 1.8)
    d.stroke("light", "M152 124 l10 4 M146 134 l9 6 M156 114 l10 2", 2)
    group(d, "translate(136 104) rotate(-28)", lambda: _hanging_rider(d, 0, 0, 1.7, body="hero", helmet="pop"))


def swing_bali(d: Drawing):
    d.disc("glow", 64, 58, 16)
    d.band("far", hills(110, 12, 30))
    d.band("mid", "M-30 130 Q50 120 100 128 T230 124")
    for k, y in enumerate([142, 156, 170, 184]):
        role = ["near", "mid", "near", "mid"][k]
        d.band(role, f"M-30 {y} Q50 {y - 10} 100 {y - 2} T230 {y - 6}", line=k < 3)
        d.stroke("light", f"M-30 {y + 3} Q50 {y - 7} 100 {y + 1} T230 {y - 3}", 1.2, line=False)

    def palm(x, y, s, flip=1):
        def p():
            d.limb("dark", f"M0 0 C{2*flip} -30 {10*flip} -60 {22*flip} -84", 5)
            for f in [f"M{22*flip} -84 C{8*flip} -92 {-8*flip} -88 {-16*flip} -74 C{-2*flip} -84 {10*flip} -84 {22*flip} -84Z",
                      f"M{22*flip} -84 C{14*flip} -100 {-2*flip} -104 {-10*flip} -100 C{2*flip} -96 {14*flip} -92 {22*flip} -84Z",
                      f"M{22*flip} -84 C{34*flip} -100 {50*flip} -100 {58*flip} -92 C{46*flip} -94 {34*flip} -90 {22*flip} -84Z",
                      f"M{22*flip} -84 C{38*flip} -84 {52*flip} -76 {56*flip} -64 C{46*flip} -74 {34*flip} -78 {22*flip} -84Z"]:
                d.shape("deep", f)
        group(d, f"translate({x} {y}) scale({s})", p)
    palm(168, 150, 0.9, -1)
    palm(20, 186, 1.0, 1)
    # swing ropes from a branch out of view, rider in a flowing dress
    d.stroke("dark", "M54 -10 L116 112 M70 -10 L128 108", 1.6)

    def rider():
        d.shape("pop", "M2 -18 C-14 -10 -36 4 -64 0 C-48 10 -28 14 -6 8 C4 4 8 -4 6 -12Z", spot=True)
        d.limb("dark", "M2 -2 L16 -6 L26 6", 3.4)
        d.shape("pop", "M-4 -26 Q6 -28 8 -14 L8 -2 Q-2 2 -6 -4Z")
        d.limb("dark", "M2 -22 L6 -30 L10 -28", 2.8, shadow=False)
        d.shape("dark", "M-6 -36 Q-18 -30 -24 -22 Q-14 -32 -4 -30Z", shadow=False)
        d.shape("hero2", circle(-1, -35, 6))
        d.shape("dark", "M-7 -36 a6 6 0 0 1 12 -2 Q0 -38 -7 -36Z", shadow=False)
        d.shape("dark", rrect(-6, -2, 20, 3.4, 1.5), shadow=False)
    group(d, "translate(116 112) rotate(-20)", rider)


def swing_treehouse(d: Drawing):
    d.disc("glow", 176, 70, 11)
    d.band("far", "M-30 136 L40 126 L90 132 L140 124 L230 130")
    d.shape("mid", "M110 134 L148 76 L160 76 L198 134Z")
    d.shape("light", "M148 76 L160 76 L168 88 L161 85 L155 91 L149 85 L141 88Z", shadow=False)
    d.raw('<g fill="#fff" opacity=".8"><circle cx="154" cy="66" r="6"/><circle cx="160" cy="56" r="7"/><circle cx="152" cy="46" r="5"/></g>', "")
    d.band("light", "M-30 144 Q0 132 30 142 Q60 132 90 142 Q120 130 150 140 Q180 132 230 140")
    d.band("sky2", "M-30 168 Q20 158 60 166 Q100 156 140 166 Q180 158 230 164", line=False)
    _land(d, "near", "M-30 160 Q20 140 50 144 Q74 150 80 230 L-30 230Z", "M-30 160 Q20 140 50 144 Q74 150 80 230")
    d.limb("dark", "M46 150 L48 62 M48 82 Q80 66 126 68", 7)
    d.shape("deep", "M14 66 Q8 40 40 34 Q56 20 78 34 Q102 34 100 54 Q94 68 66 64 Q40 76 14 66Z")
    d.shape("ground", rrect(26, 100, 44, 26, 2))
    d.shape("dark", rrect(42, 110, 11, 16, 1.5), shadow=False)
    d.shape("pop", "M20 102 L48 84 L76 102Z")
    d.stroke("dark", "M18 126 H78", 2.6)
    d.stroke("dark", "M116 68 L140 136 M122 68 L150 134", 1.6)

    def rider():
        d.shape("dark", rrect(-12, -2, 24, 4, 2))
        d.limb("hero", "M-2 -4 L12 -10 L20 0", 4)
        d.limb("hero2", "M-2 -4 L-6 -22", 7)
        d.limb("hero2", "M-5 -18 L-2 -30", 3, shadow=False)
        d.shape("dark", circle(-8, -30, 5))
    group(d, "translate(146 136) rotate(-20)", rider)


# ================================================================ DRONE PHOTOGRAPHY
def _drone(d: Drawing, body="hero", trim="hero2"):
    """A quadcopter in three-quarter front view, centred on (100, 100)."""
    def rotor(x, y, rx, ry):
        d.stroke("dark", f"M{x} {y} V{y + 8}", 3)
        if d.paper:
            d.raw(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{d.c["light"]}" opacity=".65"/>')
        else:
            d.raw("", f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="none" stroke="{d.c["ink"]}" stroke-width="1.6" stroke-dasharray="4 4"/>')
        d.stroke("dark", f"M{x - rx * .8} {y + 1} L{x + rx * .8} {y - 1}", 2)
    rotor(70, 76, 22, 5)
    rotor(130, 76, 22, 5)
    d.limb("dark", "M84 96 L70 82 M116 96 L130 82", 4.5)
    d.limb("dark", "M84 104 L48 112 M116 104 L152 112", 5.5)
    d.stroke("dark", "M82 112 L74 140 M118 112 L126 140", 3)
    d.shape(body, "M76 94 Q78 84 100 84 Q122 84 124 94 L122 108 Q118 116 100 116 Q82 116 78 108Z")
    d.shape(trim, "M78 102 H122 L121 107 H79Z", shadow=False, spot=True)
    d.shape("dark", rrect(90, 114, 20, 14, 4))
    d.shape("light", circle(100, 121, 5), shadow=False)
    d.marks("dark", circle(100, 121, 2.6))
    d.marks("pop", circle(84, 96, 1.8) + circle(116, 96, 1.8))
    d.stroke("dark", "M48 112 V102 M152 112 V102", 3)
    for x in (48, 152):
        if d.paper:
            d.raw(f'<ellipse cx="{x}" cy="101" rx="30" ry="7" fill="{d.c["light"]}" opacity=".7"/>')
        else:
            d.raw("", f'<ellipse cx="{x}" cy="101" rx="30" ry="7" fill="none" stroke="{d.c["ink"]}" stroke-width="1.6" stroke-dasharray="4 4"/>')
        d.stroke("dark", f"M{x - 24} 103 L{x + 24} 99", 2.2)
        d.marks("dark", circle(x, 101, 3))


def drone_quad(d: Drawing):
    d.disc("glow", 152, 48, 16)
    d.band("far", "M-30 150 L16 126 L46 140 L84 112 L120 140 L156 120 L230 146")
    _snowcaps(d, [(84, 112, 8), (156, 120, 7)])
    d.band("mid", hills(166, 10, 20))
    d.band("near", hills(184, 5, -10))
    d.shape("light", cloud(14, 60, 0.8))
    group(d, "translate(100 96) rotate(-6) scale(1.05) translate(-100 -100)", lambda: _drone(d))


def drone_beach(d: Drawing):
    d.band("ground", "M-30 -30 L230 -30")
    sea = "M60 -30 C80 30 110 70 150 100 C180 124 200 150 230 160 L230 -30Z"
    d.shape("far", sea, shadow=False, line=False)
    d.shape("mid", "M110 -30 C126 20 150 50 180 70 C200 84 214 94 230 98 L230 -30Z", shadow=False, line=False)
    d.shape("near", "M160 -30 C170 0 190 24 230 36 L230 -30Z", shadow=False, line=False)
    d.stroke("light", "M60 -30 C80 30 110 70 150 100 C180 124 200 150 230 160", 3.4, line=False)
    _line_only(d, "M60 -30 C80 30 110 70 150 100 C180 124 200 150 230 160", 2.4)
    d.stroke("light", "M84 -10 C100 34 126 64 160 88 M120 -20 C134 18 156 44 186 62", 1.6, line=False)

    def brolly(x, y, r, a, b):
        d.shape(a, circle(x, y, r))
        d.shape(b, f"M{x} {y} L{x} {y - r} A{r} {r} 0 0 1 {x + r * .87} {y - r / 2}Z M{x} {y} L{x + r * .87} {y + r / 2} "
                   f"A{r} {r} 0 0 1 {x} {y + r}Z M{x} {y} L{x - r * .87} {y + r / 2} A{r} {r} 0 0 1 {x - r * .87} {y - r / 2}Z",
                shadow=False, spot=True)
        d.marks("dark", circle(x, y, 1.6))
    d.shape("hero", rrect(44, 112, 14, 26, 2), shadow=False)
    d.shape("light", rrect(66, 132, 14, 26, 2), shadow=False)
    brolly(56, 106, 15, "pop", "light")
    brolly(98, 134, 13, "hero", "hero2")
    brolly(40, 160, 12, "hero2", "pop")
    d.shape("hero2", rrect(110, 150, 13, 24, 2), shadow=False)
    # viewfinder frame
    d.stroke("light", "M46 62 V46 H62 M138 46 H154 V62 M154 138 V154 H138 M62 154 H46 V138", 3.2)
    d.marks("pop", circle(56, 56, 3.4) if d.paper else "")
    d.stroke("light", "M94 101 H106 M100 95 V107", 1.8)


def drone_controller(d: Drawing):
    d.shape("light", cloud(150, 130, 0.8))
    d.shape("light", cloud(4, 136, 0.7))
    d.band("far", hills(150, 10, 20))
    d.band("near", hills(176, 6, -10))
    # phone on the clamp, showing the live view
    d.stroke("dark", "M68 104 V92 M132 104 V92", 4)
    d.shape("dark", rrect(48, 30, 104, 64, 8))
    d.shape("sky2", rrect(54, 36, 92, 52, 4), shadow=False, line=False)
    d.raw('<clipPath id="atscr"><rect x="54" y="36" width="92" height="52" rx="4"/></clipPath>', "")
    d.raw('<g clip-path="url(#atscr)">', "")
    d.shape("mid", "M54 88 L54 70 L76 52 L92 66 L108 50 L146 76 L146 88Z", shadow=False, line=False)
    d.shape("light", "M76 52 L84 60 L78 58 L72 62 L68 58Z M108 50 L117 57 L111 56 L106 60 L102 56Z", shadow=False, line=False)
    d.shape("near", "M54 88 Q90 70 146 84 V88Z", shadow=False, line=False)
    d.shape("glow", circle(128, 50, 6), shadow=False, line=False)
    d.raw("</g>", "")
    d.marks("pop", circle(62, 44, 2.6))
    d.stroke("light", "M136 44 h6 M136 48 h4", 1.4, line=False)
    _line_only(d, "M60 74 L76 56 L92 68 L108 54 L140 78", 2)
    # the controller
    d.limb("dark", "M50 116 L34 88 M150 116 L166 88", 4)
    d.shape("hero", "M48 108 Q50 100 62 100 H138 Q150 100 152 108 L162 150 Q164 164 150 164 Q140 164 134 152 "
                    "Q130 144 120 144 H80 Q70 144 66 152 Q60 164 50 164 Q36 164 38 150Z")
    d.shape("hero2", rrect(88, 108, 24, 8, 3), shadow=False, spot=True)
    for x in (70, 130):
        d.shape("dark", circle(x, 124, 9), shadow=False)
        d.shape("light", circle(x, 124, 3.6), shadow=False)
    d.marks("dark", circle(92, 128, 2.4) + circle(108, 128, 2.4))


# ================================================================ MULTI-DAY TREK
def trek_hut(d: Drawing):
    d.disc("glow", 46, 50, 14)
    d.band("far", "M-30 100 L20 70 L50 88 L90 40 L126 82 L160 56 L200 84 L230 70")
    _snowcaps(d, [(90, 40, 10), (160, 56, 9), (20, 70, 6)])
    d.band("mid", "M-30 132 Q40 110 90 120 Q120 124 150 114 Q190 106 230 120")
    d.band("near", "M-30 168 Q60 148 120 160 T230 150")
    d.stroke("ground", "M64 230 L96 190 L60 176 L104 158 L88 146 L112 132", 3.6, line=False)
    _line_only(d, "M64 230 L96 190 L60 176 L104 158 L88 146 L112 132", 1.6)
    # the hut on the saddle
    d.raw("", "")
    d.stroke("light", "M150 76 Q156 70 150 64 Q144 58 152 52", 2.2, line=False)
    d.shape("dark", rrect(142, 84, 7, 16, 1))
    d.shape("light", rrect(104, 100, 64, 30, 2))
    d.shape("pop", "M96 102 L128 78 L148 78 L176 102Z", spot=True)
    d.shape("light", "M104 102 L128 84 L132 84 L132 102Z", shadow=False, line=False)
    d.shape("pop", "M96 102 L128 78 L134 78 L102 102Z", shadow=False)
    for x in (112, 146):
        d.shape("dark", rrect(x, 108, 12, 10, 1.5), shadow=False)
        d.shape("pop", rrect(x - 5, 107, 4.5, 12, 1), shadow=False)
        d.shape("pop", rrect(x + 12.5, 107, 4.5, 12, 1), shadow=False)
    d.shape("dark", rrect(130, 112, 10, 18, 1.5), shadow=False)
    d.stroke("dark", "M82 130 V88", 1.8)
    d.shape("hero", "M83 88 L97 92 L83 97Z", spot=True)
    d.stroke("dark", "M104 116 H110 M160 122 H168 M116 124 H124", 1.2, line=False)
    d.band("deep", hills(188, 4, 30), line=False)


def trek_cairn(d: Drawing):
    d.disc("glow", 146, 54, 18)
    d.band("far", "M-30 112 L10 90 L44 104 L86 70 L120 100 L156 80 L196 104 L230 96")
    _snowcaps(d, [(86, 70, 9), (156, 80, 8)])
    d.band("mid", hills(130, 10, 30))
    d.stroke("ground", "M200 230 Q150 180 170 156 Q190 138 140 130 Q110 126 116 118", 6, line=False)
    _line_only(d, "M200 230 Q150 180 170 156 Q190 138 140 130 Q110 126 116 118", 2)
    d.band("near", "M-30 176 Q40 160 90 168 Q120 172 140 182 L150 230", line=True)
    stones = [(68, 168, 34, 13, "far"), (66, 146, 28, 11, "mid"), (70, 127, 24, 10, "ground"), (66, 110, 19, 8, "far"),
              (69, 96, 14, 7, "mid"), (67, 85, 9, 5.5, "ground")]
    for x, y, rx, ry, role in stones:
        d.shape("dark", ellipse(x, y, rx, ry))
        d.shape(role, ellipse(x, y - 1.2, rx - 1.6, ry - 1.6), shadow=False, line=False)
    d.stroke("light", "M48 162 q8 -6 16 -4 M50 142 q8 -5 14 -4 M56 106 q6 -4 12 -3", 1.6, line=False)
    d.limb("dark", "M118 182 L132 108 M128 184 L136 110", 2.6)
    d.shape("hero2", rrect(129, 104, 6, 14, 2), spot=True)
    d.shape("hero2", rrect(134, 106, 6, 14, 2), spot=True)


def trek_torres(d: Drawing):
    d.disc("glow", 160, 46, 13)
    d.shape("light", cloud(14, 54, 0.8))
    towers = "M44 118 L52 60 Q56 48 62 54 L66 80 L76 36 Q82 26 88 34 L94 76 L104 48 Q110 40 116 50 L122 118Z"
    d.shape("mid", "M10 128 L30 100 L44 104 L122 104 L140 90 L170 108 L200 98 L230 120 L230 140 L10 140Z")
    d.shape("near", towers)
    d.shape("deep", "M52 60 Q56 48 62 54 L66 80 L60 118 L54 118Z M76 36 Q82 26 88 34 L94 76 L90 118 L82 118Z "
                    "M104 48 Q110 40 116 50 L122 118 L112 118Z", shadow=False, line=False)
    d.shape("light", "M140 90 L150 96 L144 96 L140 100 L136 96 L130 98Z", shadow=False)
    d.band("far", "M-30 132 L20 124 L60 130 L100 122 L140 132 L230 126")
    d.band("sky2", "M-30 144 Q100 138 230 144")
    d.stroke("light", "M30 152 h22 M96 150 h26 M150 154 h20", 1.6, line=False)
    d.band("ground", "M-30 168 Q60 156 120 164 T230 160")
    d.shape("hero", "M136 166 L148 146 L160 166Z", spot=True)
    d.shape("dark", "M146 166 L148 156 L150 166Z", shadow=False)
    d.band("deep", hills(186, 5, 20), line=False)


# ================================================================ BOULDERING
def boulder_pad(d: Drawing):
    d.disc("glow", 152, 42, 13)
    for x, y, h in [(10, 120, 50), (30, 126, 64), (52, 118, 42), (150, 122, 56), (172, 120, 46), (190, 126, 60)]:
        d.shape("deep", _pine(x, y, h), line=False)
    d.band("far", "M-30 124 Q100 118 230 124", line=False)
    d.band("mid", hills(146, 6, 20))
    rock = "M26 164 L30 126 L50 94 L88 74 L130 72 L158 90 L172 124 L170 164Z"
    d.shape("far", rock)
    d.shape("near", "M130 72 L158 90 L172 124 L170 164 L136 164 L146 120Z", shadow=False, line=False)
    d.shape("light", "M50 94 L88 74 L130 72 L112 84 L74 90Z", shadow=False, line=False)
    _line_only(d, "M130 72 L146 120 L136 164", 1.8)
    d.stroke("near", "M60 114 L70 126 L66 144 M96 86 L104 100", 2, line=False)
    holds = [(58, 140, "pop"), (74, 116, "hero2"), (94, 104, "pop"), (114, 90, "hero2"), (130, 110, "pop"), (100, 132, "hero2")]
    for x, y, role in holds:
        d.raw(f'<ellipse cx="{x}" cy="{y + 1}" rx="8" ry="6" fill="#fff" opacity=".55"/>', "")
        d.shape(role, f"M{x - 6} {y + 1} Q{x - 6} {y - 5} {x} {y - 5} Q{x + 7} {y - 5} {x + 6} {y + 2} Q{x} {y + 5} {x - 6} {y + 1}Z", spot=role == "pop")
    d.band("ground", "M-30 168 Q100 160 230 168")
    # crash pad
    d.shape("hero", "M50 160 L150 156 L156 176 L44 182Z")
    d.shape("dark", "M44 182 L156 176 L156 182 L44 188Z", shadow=False)
    d.stroke("hero2", "M78 159 L76 182 M120 157 L122 179", 3.2)


def boulder_chalk(d: Drawing):
    d.disc("glow", 152, 50, 15)
    d.band("far", "M-30 140 C10 100 40 96 70 120 C90 104 120 100 140 116 C170 96 200 110 230 130")
    d.band("near", hills(178, 6, 20))
    if d.paper:
        d.raw('<g fill="#fff" opacity=".85">' + "".join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in
              [(82, 56, 10), (98, 46, 12), (116, 54, 9), (128, 40, 6), (70, 42, 6), (106, 30, 5)]) + "</g>")
    else:
        d.raw("", '<g fill="none" stroke-dasharray="3 4">' + "".join(
            f'<circle cx="{x}" cy="{y}" r="{r}" stroke="{d.c["ink"]}" stroke-width="1.4"/>' for x, y, r in
            [(82, 56, 10), (98, 46, 12), (116, 54, 9)]) + "</g>")
    d.limb("dark", "M44 150 H156", 5)
    d.shape("hero", "M62 82 L138 82 L134 152 Q133 166 118 166 H82 Q67 166 66 152Z")
    d.shape("hero2", "M64 130 L136 130 L135 142 L65 142Z", shadow=False, spot=True)
    d.raw('<g fill="#fff" opacity=".5"><ellipse cx="80" cy="104" rx="6" ry="3"/><ellipse cx="118" cy="114" rx="5" ry="2.5"/></g>', "")
    d.shape("light", "M58 76 Q100 64 142 76 Q144 88 136 90 Q100 82 64 90 Q56 88 58 76Z")
    d.stroke("dark", "M68 86 Q56 98 60 112", 1.6)
    d.shape("dark", rrect(56, 110, 8, 10, 3))
    # brush in its holder
    d.shape("dark", rrect(136, 100, 10, 30, 3))
    d.shape("pop", rrect(138.5, 80, 5, 26, 2), spot=True)
    d.shape("dark", rrect(136, 66, 10, 16, 2.5))
    d.stroke("light", "M139 69 V79 M143 69 V79", 1, line=False)


def boulder_shoe(d: Drawing):
    d.disc("glow", 52, 52, 16)
    d.band("far", "M-30 112 C20 92 60 96 100 108 C140 96 180 92 230 104")
    for x, y, role in [(22, 128, "pop"), (180, 120, "hero2"), (160, 160, "pop")]:
        d.shape(role, f"M{x - 7} {y + 1} Q{x - 7} {y - 6} {x} {y - 6} Q{x + 8} {y - 6} {x + 7} {y + 2} Q{x} {y + 6} {x - 7} {y + 1}Z")
    d.band("mid", hills(172, 6, 20))
    shoe = ("M30 112 C30 92 46 82 64 82 L92 82 C106 82 118 90 130 98 C148 108 166 118 172 132 C174 140 166 146 156 144 "
            "C134 140 112 138 92 140 C70 144 52 148 40 142 C32 136 30 124 30 112Z")
    sole = ("M30 120 C30 132 32 140 40 144 C52 150 70 146 92 142 C112 140 134 142 156 146 C166 148 176 142 172 130 "
            "C166 136 158 138 152 136 C130 132 110 132 92 134 C70 138 52 140 42 136 C34 132 32 126 30 120Z")
    d.shape("hero", shoe)
    d.shape("dark", sole, shadow=False)
    d.shape("dark", "M140 108 C156 116 168 122 172 132 C164 128 152 126 140 122Z", shadow=False)
    d.shape("dark", "M30 108 C30 96 36 88 46 84 L48 104 Q40 108 30 112Z", shadow=False)
    d.shape("pop", "M46 84 C40 74 44 66 52 68 L56 84Z", spot=True)
    for x in (82, 102, 120):
        d.shape("hero2", f"M{x} 82 L{x + 14} 86 L{x + 8} 128 L{x - 6} 126Z", shadow=False, spot=True)
        d.stroke("dark", f"M{x + 1} 104 H{x + 9}", 1, line=False)
    d.band("deep", hills(188, 4, 20), line=False)


# ================================================================ VIA FERRATA
def _biner(d: Drawing, x, y, rot, role="pop", s=1.0):
    group(d, f"translate({x} {y}) rotate({rot}) scale({s})", lambda: (
        d.stroke(role, "M-6 -12 Q-6 -18 0 -18 Q8 -18 8 -10 L6 12 Q5 18 0 18 Q-6 18 -6 12Z", 4.4, shadow=True),
        d.stroke("dark", "M8 -8 L6 6", 2.2)))


def vf_rungs(d: Drawing):
    d.disc("glow", 164, 50, 13)
    d.band("far", "M-30 150 L60 124 L100 140 L140 116 L230 140")
    face = "M-30 -30 L120 -30 L132 30 L124 70 L140 110 L132 150 L148 230 L-30 230Z"
    _land(d, "mid", face, "M120 -30 L132 30 L124 70 L140 110 L132 150 L148 230")
    d.shape("near", "M120 -30 L132 30 L124 70 L140 110 L132 150 L148 230 L128 230 L116 150 L122 110 L108 70 L116 30 L106 -30Z", shadow=False, line=False)
    d.stroke("near", "M20 20 L40 60 L30 100 M60 120 L70 160 L60 200 M80 10 L70 40", 2, line=False)
    # iron rungs climbing the face
    for i, (x, y) in enumerate([(30, 184), (44, 156), (58, 128), (72, 100), (86, 72), (100, 44), (112, 16)]):
        d.stroke("dark", f"M{x - 12} {y - 4} V{y + 2} Q{x - 12} {y + 6} {x - 8} {y + 6} H{x + 8} Q{x + 12} {y + 6} {x + 12} {y + 2} V{y - 4}", 3.6, shadow=True)
        d.marks("dark", circle(x - 12, y - 4, 2.4) + circle(x + 12, y - 4, 2.4))
    d.stroke("light", "M4 176 L22 156 L34 140 L50 118 L66 96 L80 72 L96 46 L104 30", 2.6, shadow=True)
    for x, y in [(22, 156), (50, 118), (80, 72), (104, 30)]:
        d.shape("dark", rrect(x - 3, y - 3, 6, 6, 1.5))
    d.stroke("hero", "M60 230 Q64 180 54 140 M60 230 Q72 170 66 124", 3)
    _biner(d, 46, 128, 38, "pop", 1.15)
    _biner(d, 62, 108, 38, "hero2", 1.15)


def vf_bridge(d: Drawing):
    d.disc("glow", 100, 70, 20)
    d.band("far", "M-30 120 L20 100 L50 112 L100 80 L150 110 L180 96 L230 116")
    _snowcaps(d, [(100, 80, 9)])
    d.band("deep", "M-30 172 Q100 164 230 172", line=False)
    _land(d, "near", "M-30 90 L40 84 L50 110 L42 150 L54 230 L-30 230Z", "M-30 90 L40 84 L50 110 L42 150 L54 230")
    _land(d, "near", "M230 98 L162 94 L152 120 L160 160 L148 230 L230 230Z", "M230 98 L162 94 L152 120 L160 160 L148 230")
    d.shape("deep", "M40 84 L50 110 L42 150 L54 230 L44 230 L32 150 L40 110Z", shadow=False, line=False)
    d.shape("deep", "M162 94 L152 120 L160 160 L148 230 L158 230 L170 160 L162 120Z", shadow=False, line=False)
    foot = [_q((40, 92), (100, 132), (162, 100), i / 10) for i in range(11)]
    hand = [_q((40, 70), (100, 104), (162, 76), i / 10) for i in range(11)]
    for (fx, fy), (hx, hy) in zip(foot[1:-1], hand[1:-1]):
        d.stroke("dark", f"M{hx - 4:.1f} {hy:.1f} L{fx:.1f} {fy:.1f} L{hx + 4:.1f} {hy:.1f}", 1)
    d.stroke("dark", "M40 92 Q100 132 162 100", 3)
    d.stroke("dark", "M38 68 Q100 106 164 74 M42 72 Q100 110 160 78", 1.6)
    d.shape("dark", rrect(36, 64, 6, 30, 2))
    d.shape("dark", rrect(159, 70, 6, 32, 2))
    # climber mid-span, clipped on
    group(d, "translate(112 92) scale(1.2)", lambda: (
        d.limb("hero", "M-2 0 L-6 16 M2 0 L4 16", 4),
        d.shape("hero2", rrect(-6, -16, 12, 18, 5)),
        d.limb("hero2", "M-4 -12 L-8 -22 M4 -12 L8 -22", 3, shadow=False),
        d.shape("pop", circle(0, -22, 5.4))))


def vf_dolomites(d: Drawing):
    d.disc("glow", 160, 44, 14)
    d.shape("mid", "M18 136 L34 70 L44 64 L52 136Z M46 136 L62 46 L74 38 L88 136Z M84 136 L96 72 L106 68 L116 136Z")
    d.shape("near", "M44 64 L52 136 L46 136 L40 90Z M74 38 L88 136 L80 136 L72 70Z M106 68 L116 136 L110 136 L104 96Z", shadow=False, line=False)
    d.shape("light", "M34 70 L44 64 L41 76Z M62 46 L74 38 L69 54Z M96 72 L106 68 L102 80Z", shadow=False)
    d.band("far", "M-30 138 Q20 126 60 132 T140 128 T230 132")
    for x, y, h in [(4, 146, 18), (18, 148, 22), (34, 146, 16), (70, 148, 20), (86, 146, 16)]:
        d.shape("deep", _pine(x, y, h), line=False)
    cliff = "M108 230 L118 140 L126 100 L120 60 L132 20 L130 -30 L230 -30 L230 230Z"
    _land(d, "near", cliff, "M108 230 L118 140 L126 100 L120 60 L132 20 L130 -30")
    d.stroke("deep", "M150 40 L160 90 L150 140 M180 20 L176 70 M190 120 L200 170", 2, line=False)
    # ladder bolted to the face
    d.stroke("dark", "M138 230 L148 26 M156 230 L164 26", 2.6, shadow=True)
    for y in range(40, 200, 14):
        d.stroke("dark", f"M{148 - (y - 26) * 10 / 204:.1f} {y} H{164 - (y - 26) * 8 / 204:.1f}", 2.2)
    group(d, "translate(156 108) scale(1.2)", lambda: (
        d.limb("hero", "M-3 6 L-6 22 M3 6 L6 14 L4 22", 4),
        d.shape("hero2", rrect(-6, -12, 12, 20, 5)),
        d.limb("hero2", "M-4 -9 L-6 -22 M4 -9 L6 -18", 3, shadow=False),
        d.shape("pop", circle(0, -18, 5.4))))
    d.band("deep", hills(178, 6, 10), line=False)
    d.band("ground", "M-30 192 Q60 182 120 188")


# ================================================================ ABSEILING
def abseil_eight(d: Drawing):
    d.disc("glow", 160, 52, 14)
    d.band("far", "M-30 156 L30 138 L70 150 L120 128 L170 148 L230 136")
    d.band("mid", hills(180, 6, 20))
    # carabiner up top
    d.stroke("dark", "M100 -10 V24", 3)
    group(d, "translate(100 40) scale(1.1)", lambda: (
        d.stroke("hero2", "M-8 -14 Q-8 -22 0 -22 Q10 -22 10 -12 L8 14 Q7 22 0 22 Q-8 22 -8 14Z", 5, shadow=True),
        d.stroke("dark", "M10 -8 L8 8", 2.4)))
    # rope comes down into the big ring, round the neck and away
    d.limb("pop", "M54 -10 Q60 60 92 114", 7, spot=True)
    d.shape("light", "M86 54 a14 14 0 1 0 28 0 a14 14 0 1 0 -28 0Z M93 54 a7 7 0 1 1 14 0 a7 7 0 1 1 -14 0Z", extra='fill-rule="evenodd"')
    d.shape("light", rrect(93, 64, 14, 26, 3))
    d.shape("light", "M68 120 a32 32 0 1 0 64 0 a32 32 0 1 0 -64 0Z M83 120 a17 17 0 1 1 34 0 a17 17 0 1 1 -34 0Z", extra='fill-rule="evenodd"')
    d.limb("pop", "M92 114 Q100 150 122 146 Q146 136 132 102 Q122 82 104 80", 7, spot=True)
    d.limb("pop", "M104 80 Q86 80 88 98", 7, spot=True)
    d.limb("pop", "M88 98 Q96 160 150 230", 7, spot=True)
    d.stroke("dark", "M58 10 l4 -2 M64 40 l4 -2 M74 72 l4 -3 M118 186 l4 -3 M134 210 l4 -3", 1.4, line=False)


def abseil_cliff(d: Drawing):
    d.disc("glow", 50, 52, 16)
    d.band("far", "M-30 150 L20 130 L60 146 L100 124 L130 140 L230 128")
    d.band("mid", hills(176, 8, 20))
    face = "M150 -30 L156 40 L148 90 L158 140 L150 230 L230 230 L230 -30Z"
    _land(d, "near", face, "M150 -30 L156 40 L148 90 L158 140 L150 230")
    d.stroke("deep", "M170 30 L180 70 L172 110 M196 80 L190 140 L200 180", 2, line=False)
    d.stroke("dark", "M154 -10 Q150 40 118 114", 1.8)
    d.stroke("dark", "M112 120 Q110 170 124 230", 1.8)

    def person():
        d.limb("hero", "M112 118 L148 112", 7)
        d.shape("dark", rrect(146, 104, 8, 14, 3), shadow=False)
        d.limb("hero2", "M112 118 L104 88", 11)
        d.limb("hero2", "M106 94 L124 104 L134 84", 4, shadow=False)
        d.limb("hero2", "M104 96 L100 112 L110 124", 4, shadow=False)
        d.shape("dark", rrect(106, 112, 14, 7, 3), shadow=False)
        d.shape("light", circle(100, 76, 7.5))
        d.shape("pop", "M92 75 a8 8 0 0 1 16 -2 Q100 70 92 75Z", spot=True)
    group(d, "translate(130 110) scale(1.3) translate(-126 -104)", person)


def abseil_falls(d: Drawing):
    d.disc("glow", 160, 40, 12)
    _land(d, "mid", "M-30 30 Q40 20 70 26 L74 230 L-30 230Z", "M-30 30 Q40 20 70 26 L74 230")
    _land(d, "mid", "M230 30 Q160 22 132 26 L128 230 L230 230Z", "M230 30 Q160 22 132 26 L128 230")
    d.shape("near", "M-30 60 L40 70 L50 120 L36 230 L-30 230Z M230 70 L170 66 L156 130 L168 230 L230 230Z", shadow=False, line=False)
    d.shape("light", "M76 24 Q100 20 126 24 L124 170 L78 170Z", line=False)
    d.stroke("sky2", "M84 30 V168 M96 26 V170 M108 26 V168 M118 30 V170", 2.4, line=False)
    _line_only(d, "M76 26 L78 170 M126 26 L124 170 M96 40 V80 M108 90 V130", 2.2)
    d.band("sky2", waves(170, 3, 26))
    d.band("far", waves(184, 3, 30), line=False)
    for x, y, s in [(60, 162, 1.0), (104, 164, 1.0)]:
        d.shape("light", cloud(x, y, s), shadow=False, line=False)
    for leaf in ["M-10 40 Q30 30 44 50 Q20 54 -10 40Z", "M-10 80 Q24 70 40 88 Q14 94 -10 80Z",
                 "M210 50 Q176 40 160 60 Q186 64 210 50Z", "M210 96 Q180 86 164 104 Q190 108 210 96Z"]:
        d.shape("deep", leaf)
    d.stroke("dark", "M132 20 L136 230", 1.8)

    def person():
        d.limb("hero", "M-2 0 L-14 -4", 5)
        d.limb("hero2", "M0 0 L6 -18", 8)
        d.limb("hero2", "M5 -14 L-2 -24 M2 -10 L-6 2", 3, shadow=False)
        d.shape("pop", circle(8, -24, 5.4))
    group(d, "translate(140 108) scale(1.2)", person)
    d.stroke("dark", "M126 92 L130 120", 1.6, line=False)


# ================================================================ DIRT BIKING
def _dirtbike(d: Drawing, body="hero", trim="hero2", rider=False, suit="hero2", helmet="pop"):
    """A motocross bike facing right, wheels at (54, 138) and (148, 138)."""
    for x in (54, 148):
        d.stroke("dark", circle(x, 138, 22), 7, shadow=True)
        d.raw(f'<circle cx="{x}" cy="138" r="26" fill="none" stroke="{_ink(d, "dark")}" stroke-width="3" stroke-dasharray="3.4 3"/>', "")
        d.stroke("dark", f"M{x - 18} 138 H{x + 18} M{x} 120 V156 M{x - 13} 125 L{x + 13} 151 M{x - 13} 151 L{x + 13} 125", 0.8, line=False)
        d.marks("dark", circle(x, 138, 4))
    d.limb("dark", "M54 138 L98 120", 5)
    d.stroke("dark", "M78 128 L88 96", 3)
    d.limb("dark", "M148 138 L132 80", 4.5)
    d.shape("dark", rrect(84, 108, 30, 22, 5))
    d.stroke("light", "M90 114 h18 M90 120 h18", 1.4, line=False)
    d.stroke("dark", "M112 126 Q120 134 104 136 Q80 130 70 104 L52 98", 3)
    d.shape("dark", rrect(36, 92, 26, 6, 3))
    d.shape(body, "M18 82 L60 92 L76 90 L110 88 Q122 86 130 80 L134 84 L128 104 L110 108 L92 106 L80 100 L62 100Z", spot=True)
    d.shape("dark", "M40 85 Q70 86 108 84 L110 89 L76 91 L60 93 L40 88Z", shadow=False)
    d.shape("light", "M64 93 L84 92 L82 100 L67 100Z", shadow=False)
    d.shape(body, "M132 92 L172 96 L168 102 L134 100Z", spot=True)
    d.shape("light", "M128 76 Q138 76 140 84 L138 92 Q130 88 128 76Z")
    d.limb("dark", "M124 72 L134 74 L142 70", 3)
    d.stroke(trim, "M24 92 L58 94", 2, line=False)
    if rider:
        d.limb("dark", "M98 106 L114 92 L102 74", 6)
        d.limb(suit, "M102 74 L120 52", 11)
        d.limb(suit, "M118 56 L130 66 L138 70", 4.5)
        d.shape(helmet, "M116 36 Q130 32 136 42 L142 44 L136 48 Q134 54 124 54 Q114 52 116 36Z", spot=True)
        d.shape("light", "M128 40 L137 44 L133 48 L127 47Z", shadow=False)


def dirt_bike(d: Drawing):
    d.disc("glow", 152, 50, 16)
    d.band("far", hills(118, 10, 20))
    d.band("mid", "M-30 150 Q30 120 70 140 Q110 158 150 130 Q180 112 230 132")
    d.band("ground", "M-30 160 Q100 154 230 160")
    d.marks("near", "".join(circle(x, y, r) for x, y, r in [(26, 150, 5), (16, 140, 3.6), (32, 136, 3), (10, 152, 2.4)]))
    group(d, "translate(102 104) rotate(-4) translate(-96 -112)", lambda: _dirtbike(d))
    d.band("near", "M-30 182 Q100 174 230 182", line=False)


def dirt_jump(d: Drawing):
    d.disc("glow", 60, 56, 20)
    d.band("far", hills(140, 10, 20))
    _land(d, "ground", "M-30 230 L-30 150 Q10 146 40 128 Q56 120 64 124 L76 230Z", "M-30 150 Q10 146 40 128 Q56 120 64 124 L76 230")
    _land(d, "ground", "M120 230 Q150 160 180 158 Q210 158 230 162 L230 230Z", "M120 230 Q150 160 180 158 Q210 158 230 162")
    d.band("near", "M-30 186 Q100 178 230 186", line=False)
    d.marks("mid", "".join(circle(x, y, r) for x, y, r in [(54, 118, 5), (42, 110, 4), (60, 104, 3), (34, 120, 3)]))
    d.stroke("dark", "M30 72 q4 -4 8 0 M160 60 q4 -4 8 0", 1.6)
    group(d, "translate(118 98) rotate(-18) scale(.72) translate(-96 -100)", lambda: _dirtbike(d, rider=True))


def dirt_tyre(d: Drawing):
    d.disc("glow", 46, 46, 14)
    d.band("far", hills(110, 8, 20))
    d.band("ground", "M-30 168 Q100 162 230 168")
    d.stroke("near", "M-30 186 Q40 180 90 186 M-30 196 Q40 190 90 196", 3, line=False)
    d.marks("near", "".join(circle(x, y, r) for x, y, r in [(28, 120, 6), (16, 104, 4), (40, 98, 4.5), (8, 132, 3.6), (30, 84, 3), (52, 80, 2.4)]))
    cx, cy = 108, 112
    import math
    knobs = ""
    for i in range(28):
        a = i * 2 * math.pi / 28
        x, y = cx + 56 * math.cos(a), cy + 56 * math.sin(a)
        knobs += f'<rect x="-5" y="-4" width="10" height="8" rx="2" transform="translate({x:.1f} {y:.1f}) rotate({math.degrees(a):.1f})"/>'
    d.raw(f'<g fill="{_ink(d, "dark")}">{knobs}</g>', f'<g fill="{_ink(d, "dark")}">{knobs}</g>')
    d.shape("dark", circle(cx, cy, 54))
    d.shape("light", circle(cx, cy, 38), shadow=False)
    d.shape("dark", circle(cx, cy, 35), shadow=False)
    d.stroke("light", " ".join(f"M{cx} {cy} L{cx + 34 * math.cos(i * math.pi / 8):.1f} {cy + 34 * math.sin(i * math.pi / 8):.1f}" for i in range(16)), 1.2)
    d.shape("light", circle(cx, cy, 16), shadow=False)
    d.shape("dark", circle(cx, cy, 7), shadow=False)
    d.limb("hero2", "M140 -10 L112 112", 12, spot=True)
    d.shape("hero", "M66 52 Q100 30 150 44 L156 54 Q110 44 70 62Z", spot=True)
    d.shape("light", rrect(84, 30, 34, 26, 8), extra='transform="rotate(-14 101 43)"')
    d.marks("dark", "M96 36 h8 v18 h-4 v-14 h-4Z" if d.paper else "")


# ================================================================ E-BIKE TOUR
def _ebike(d: Drawing, frame="hero", battery="hero2", wheels="dark"):
    """A step-through e-bike facing right, rear wheel at (60,140), front at (140,140)."""
    rx, fx, y, r = 60, 140, 140, 22
    for x in (rx, fx):
        d.stroke(wheels, circle(x, y, r), 5, shadow=True)
        d.stroke(wheels, f"M{x - r + 3} {y} H{x + r - 3} M{x} {y - r + 3} V{y + r - 3} M{x - r * .7} {y - r * .7} L{x + r * .7} {y + r * .7} "
                         f"M{x - r * .7} {y + r * .7} L{x + r * .7} {y - r * .7}", 0.8, line=False)
    d.shape("dark", circle(rx, y, 7))
    d.marks("dark", circle(fx, y, 2.6))
    d.limb("dark", f"M{rx} {y} L{rx + 4} 108 M{rx - 18} 106 L{rx + 24} 106", 2.4)
    d.shape(battery, rrect(32, 96, 26, 12, 2))
    d.limb(frame, f"M{rx} {y} L92 142 L84 104 M{rx} {y} L84 106 M92 142 Q100 120 122 104 M120 98 L{fx} {y}", 5, spot=True)
    d.limb("dark", "M77 102 L92 100", 4)
    d.limb("dark", "M120 98 L118 88 L128 84", 3.6)
    d.shape("dark", rrect(114, 82, 8, 5, 1.5), shadow=False)
    group(d, "translate(103 124) rotate(-50)", lambda: (
        d.shape(battery, rrect(-15, -5.5, 30, 11, 4), spot=True),
        d.marks("dark", "M2 -4 L-4 1 L0 1 L-2 4.5 L5 -1 L1 -1Z")))
    d.marks("dark", circle(92, 142, 5))
    d.stroke("dark", "M92 142 L99 150", 2.6)
    d.stroke("dark", "M126 112 Q146 112 150 128", 2.4, line=False)


def ebike_side(d: Drawing):
    d.disc("glow", 150, 54, 18)
    d.band("far", "M-30 124 L20 100 L50 112 L86 82 L120 108 L156 90 L230 114")
    _snowcaps(d, [(86, 82, 8), (156, 90, 7)])
    d.band("mid", hills(146, 10, 20))
    d.shape("light", cloud(14, 60, 0.8))
    d.band("ground", "M-30 168 Q100 158 230 168")
    group(d, "translate(102 104) scale(1.12) translate(-100 -118)", lambda: _ebike(d))
    d.band("near", "M-30 186 Q100 178 230 186", line=False)


def ebike_vineyard(d: Drawing):
    d.disc("glow", 50, 48, 16)
    d.band("far", hills(96, 10, 20))
    d.shape("dark", rrect(150, 72, 12, 16, 1))
    d.shape("light", rrect(140, 80, 34, 16, 1))
    d.shape("pop", "M136 82 L157 70 L178 82Z")
    d.band("mid", "M-30 118 Q60 98 120 108 T230 104")
    for i in range(8):
        x0 = -20 + i * 32
        d.stroke("deep", f"M{x0} {116 - i * 1.2:.1f} Q{x0 - 30} 150 {x0 - 80} 190", 4.2, line=False)
        _line_only(d, f"M{x0} {116 - i * 1.2:.1f} Q{x0 - 30} 150 {x0 - 80} 190", 1.4) if i % 2 == 0 else None
    d.band("ground", "M-30 156 Q60 144 120 152 T230 146")
    d.band("near", "M-30 182 Q100 172 230 182", line=False)
    group(d, "translate(108 126) scale(.62) translate(-100 -118)", lambda: _ebike(d))


def ebike_charge(d: Drawing):
    d.disc("glow", 50, 50, 16)
    d.band("far", hills(118, 10, 20))
    d.shape("ground", rrect(140, 70, 64, 80, 2))
    d.shape("hero2", "M134 72 L172 54 L210 72Z")
    d.shape("dark", rrect(156, 96, 14, 24, 2), shadow=False)
    d.band("mid", "M-30 150 Q100 144 230 150")
    # charging post with its cable to the battery
    d.shape("dark", rrect(124, 62, 24, 92, 6))
    d.shape("light", rrect(128, 70, 16, 20, 3), shadow=False)
    d.marks("pop", "M138 72 L131 81 L136 81 L133 88 L142 78 L137 78Z")
    d.stroke("dark", "M136 106 Q136 136 112 134 Q92 132 80 124", 2.4)
    group(d, "translate(64 130) scale(.86) translate(-100 -118)", lambda: _ebike(d))
    d.band("near", "M-30 176 Q100 168 230 176", line=False)


# ================================================================ concepts
SEA = ["coastal", "meadow", "blush", "dusk"]

CONCEPTS = [
    Concept("hang-delta-wing", "hang-gliding", "Delta wing", hang_delta, SEA,
            checks=[("hero", "sky"), ("hero2", "hero"), ("near", "far")], fixes={"hero": ["pop", "deep", "near"]}),
    Concept("hang-launch-ramp", "hang-gliding", "Launch ramp", hang_ramp,
            checks=[("hero", "sky"), ("hero2", "near"), ("near", "mid")], fixes={"hero": ["pop", "deep"], "hero2": ["light", "pop"]}),
    Concept("hang-rio-bay", "hang-gliding", "Over the bay", hang_rio, SEA,
            checks=[("pop", "sky"), ("mid", "sky"), ("near", "sky"), ("deep", "mid")], fixes={"pop": ["hero", "deep"]}),
    Concept("scenic-bush-plane", "scenic-flight", "Bush plane", scenic_cessna,
            checks=[("hero", "sky"), ("hero", "far"), ("hero2", "hero")], fixes={"hero": ["pop", "deep"]}),
    Concept("scenic-nazca-lines", "scenic-flight", "Nazca lines", scenic_nazca, overrides={"ground": "#C98B5B", "mid": "#B97A4E", "light": "#FBEBD0"},
            checks=[("hero", "ground"), ("far", "sky")], fixes={"hero": ["hero2", "pop"]}),
    Concept("scenic-heart-reef", "scenic-flight", "Heart Reef", scenic_heart, SEA,
            checks=[("pop", "light"), ("pop", "mid"), ("light", "mid")], fixes={"pop": ["hero", "deep"]}),
    Concept("glide-sailplane", "gliding", "Sailplane over the hills", glide_airfield,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "mid")], fixes={"hero": ["pop", "deep"]}),
    Concept("glide-aerotow", "gliding", "Aerotow", glide_tow,
            checks=[("light", "far"), ("light", "ground"), ("light", "mid")], fixes={"far": ["near"]}),
    Concept("glide-thermal", "gliding", "Riding the thermal", glide_thermal,
            checks=[("hero", "sky"), ("hero2", "hero")], fixes={"hero": ["pop", "deep"]}),
    Concept("micro-trike", "microlight-flight", "Flex-wing trike", micro_trike,
            checks=[("hero", "sky"), ("pop", "sky"), ("hero2", "hero")], fixes={"hero": ["deep", "pop"], "pop": ["hero2", "deep"]}),
    Concept("micro-victoria-falls", "microlight-flight", "Over Victoria Falls", micro_falls, SEA,
            checks=[("hero", "sky"), ("light", "deep"), ("light", "far")], fixes={"hero": ["deep", "pop"]}),
    Concept("micro-sunset", "microlight-flight", "Sunset flight", micro_sunset,
            checks=[("dark", "glow"), ("dark", "glow2"), ("dark", "sky")]),
    Concept("skywalk-horseshoe", "skywalk", "Canyon skywalk", skywalk_horseshoe,
            checks=[("light", "mid"), ("light", "near"), ("ground", "far")], fixes={"ground": ["deep", "near"]}),
    Concept("skywalk-glass-floor", "skywalk", "Glass floor", skywalk_glass,
            checks=[("hero2", "mid"), ("hero", "mid"), ("hero", "hero2")], fixes={"hero2": ["light", "pop"], "hero": ["deep", "pop"]}),
    Concept("skywalk-tower", "skywalk", "Tower edge walk", skywalk_tower,
            checks=[("deep", "sky"), ("mid", "sky"), ("hero2", "mid")], fixes={"hero2": ["pop", "light"]}),
    Concept("swing-canyon", "giant-swing", "Canyon swing", swing_canyon,
            checks=[("hero", "sky"), ("near", "sky"), ("hero", "glow")], fixes={"hero": ["pop", "deep"]}),
    Concept("swing-bali", "giant-swing", "Jungle swing", swing_bali,
            checks=[("pop", "sky"), ("pop", "far"), ("deep", "sky")], fixes={"pop": ["hero", "deep"]}),
    Concept("swing-treehouse", "giant-swing", "Swing at the end of the world", swing_treehouse,
            checks=[("hero2", "sky"), ("hero2", "mid"), ("pop", "deep"), ("light", "far"), ("mid", "sky")], fixes={"hero2": ["pop", "hero"], "mid": ["near", "deep"]}),
    Concept("drone-quad", "drone-photography", "Quadcopter", drone_quad,
            checks=[("hero", "sky"), ("hero", "far"), ("dark", "sky")], fixes={"hero": ["pop", "deep"]}),
    Concept("drone-beach-shot", "drone-photography", "Beach from above", drone_beach, SEA,
            checks=[("ground", "far"), ("pop", "ground"), ("hero", "ground")], fixes={"hero": ["deep", "pop"]}),
    Concept("drone-controller", "drone-photography", "Controller & live view", drone_controller,
            checks=[("hero", "sky"), ("hero", "far"), ("mid", "sky2")], fixes={"hero": ["pop", "deep"]}),
    Concept("trek-mountain-hut", "multi-day-trek", "Mountain hut", trek_hut,
            checks=[("light", "mid"), ("pop", "mid"), ("far", "sky")], fixes={"pop": ["hero", "deep"]}),
    Concept("trek-cairn", "multi-day-trek", "Cairn on the trail", trek_cairn,
            checks=[("dark", "mid"), ("dark", "near"), ("far", "sky")], fixes={"far": ["mid"]}),
    Concept("trek-torres", "multi-day-trek", "Granite towers", trek_torres, SEA,
            checks=[("near", "sky"), ("near", "mid"), ("hero", "ground")], fixes={"hero": ["pop", "deep"]}),
    Concept("boulder-crash-pad", "bouldering", "Boulder & crash pad", boulder_pad,
            checks=[("far", "sky"), ("far", "deep"), ("hero", "ground"), ("hero", "far")], fixes={"hero": ["pop", "deep"]}),
    Concept("boulder-chalk-bag", "bouldering", "Chalk bag", boulder_chalk,
            checks=[("hero", "sky"), ("hero", "far"), ("hero2", "hero")], fixes={"hero": ["pop", "deep"]}),
    Concept("boulder-shoe", "bouldering", "Climbing shoe", boulder_shoe,
            checks=[("hero", "sky"), ("hero", "far"), ("hero2", "hero")], fixes={"hero": ["pop", "deep"]}),
    Concept("ferrata-rungs", "via-ferrata", "Iron rungs", vf_rungs,
            checks=[("dark", "mid"), ("pop", "mid"), ("hero2", "mid"), ("light", "mid")], fixes={"hero2": ["light", "hero"]}),
    Concept("ferrata-bridge", "via-ferrata", "Cable bridge", vf_bridge,
            checks=[("near", "sky"), ("hero2", "sky"), ("dark", "sky")], fixes={"hero2": ["pop", "hero"]}),
    Concept("ferrata-dolomites", "via-ferrata", "Dolomites ladder", vf_dolomites,
            checks=[("mid", "sky"), ("hero2", "near"), ("dark", "near")], fixes={"hero2": ["light", "pop"]}),
    Concept("abseil-figure-eight", "abseiling", "Figure-8 descender", abseil_eight,
            checks=[("light", "sky"), ("pop", "sky"), ("pop", "light")], fixes={"light": ["mid", "far", "near"]}),
    Concept("abseil-cliff", "abseiling", "Over the edge", abseil_cliff,
            checks=[("hero2", "sky"), ("hero", "sky"), ("near", "sky")], fixes={"hero2": ["pop", "hero"]}),
    Concept("abseil-waterfall", "abseiling", "Waterfall descent", abseil_falls, SEA,
            checks=[("light", "mid"), ("hero2", "mid"), ("pop", "mid")], fixes={"hero2": ["light", "hero"]}),
    Concept("dirt-motocross", "dirt-biking", "Motocross bike", dirt_bike,
            checks=[("hero", "sky"), ("hero", "far"), ("dark", "ground")], fixes={"hero": ["pop", "deep"]}),
    Concept("dirt-big-air", "dirt-biking", "Big air", dirt_jump,
            checks=[("hero", "sky"), ("pop", "sky"), ("hero2", "sky")], fixes={"hero": ["pop", "deep"]}),
    Concept("dirt-knobbly-tyre", "dirt-biking", "Knobbly tyre", dirt_tyre,
            checks=[("dark", "sky"), ("hero", "sky"), ("hero2", "sky")], fixes={"hero2": ["pop", "deep"]}),
    Concept("ebike-alpine", "e-bike-tour", "E-bike", ebike_side,
            checks=[("hero", "sky"), ("hero", "mid"), ("hero2", "hero")], fixes={"hero": ["pop", "deep"]}),
    Concept("ebike-vineyard", "e-bike-tour", "Vineyard ride", ebike_vineyard,
            checks=[("hero", "ground"), ("deep", "mid"), ("dark", "ground")], fixes={"hero": ["pop", "deep"]}),
    Concept("ebike-charging", "e-bike-tour", "Charging stop", ebike_charge,
            checks=[("hero", "mid"), ("hero", "sky"), ("dark", "ground")], fixes={"hero": ["pop", "deep"]}),
]
