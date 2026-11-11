"""Water D: freediving, canyoning, wild swimming, deep-sea fishing, glass-bottom boats, banana boats,
sunbathing, river tubing, pool days and lagoon swims. Three concepts each."""
import math

from _common import Concept, Drawing, cloud, fish, circle, ellipse, waves, hills, rrect, group, bubbles, water

ALL = ["golden", "coastal", "meadow", "blush", "dusk"]
SEA = ["coastal", "meadow", "blush", "dusk"]  # sea and lake scenes: no golden (brown water)
UNDERWATER = ["coastal", "dusk", "meadow"]

# Natural colours shared by the module (custom roles, so they never shift with the palette).
BASE = {"skin": "#E8B48C", "hair": "#4A3226", "wood": "#9A5B34", "wood2": "#C98A55"}


def ov(**kw):
    return {**BASE, **kw}


# ================================================================ helpers
def _clip(d: Drawing, fn):
    """Clip to the sticker circle in both styles."""
    d.raw('<g clip-path="url(#clip)">', '<g clip-path="url(#clip)">')
    fn()
    d.raw("</g>", "</g>")


def clipped(fn):
    def draw(d: Drawing):
        _clip(d, lambda: fn(d))
    return draw


def _ring(cx, cy, r1, r2, ry=1.0):
    """A ring (use with fill-rule evenodd); ry squashes it vertically."""
    return ellipse(cx, cy, r2, r2 * ry) + " " + (f"M{cx - r1} {cy} a{r1} {r1 * ry} 0 1 1 {2 * r1} 0 "
                                                 f"a{r1} {r1 * ry} 0 1 1 {-2 * r1} 0Z")


def rays(d: Drawing, xs=((56, 76), (112, 124)), op=0.16):
    g = "".join(f'<path d="M{a} -10 L{b} -10 L{b + 40} 210 L{a + 40} 210Z"/>' for a, b in xs)
    d.raw(f'<g opacity="{op}" fill="#fff">{g}</g>', "")


def pines(xs, base, h, w=None):
    """A row of pointed pine silhouettes as one path: (x, height) pairs standing on y=base."""
    p = f"M-30 {base}"
    for x, hh in xs:
        ww = w or hh * 0.32
        p += f" L{x - ww} {base} L{x - ww * 0.55} {base - hh * 0.45} L{x - ww * 0.75} {base - hh * 0.45} L{x} {base - hh}"
        p += f" L{x + ww * 0.75} {base - hh * 0.45} L{x + ww * 0.55} {base - hh * 0.45} L{x + ww} {base}"
    return p + f" L230 {base}"


def spray(x, y, s=1.0, left=True):
    k = -1 if left else 1
    return (f"M{x} {y} C{x+k*4*s} {y-10*s} {x+k*14*s} {y-18*s} {x+k*24*s} {y-16*s} "
            f"C{x+k*18*s} {y-12*s} {x+k*14*s} {y-6*s} {x+k*16*s} {y}Z")


def splash(x, y, s=1.0):
    """A crown splash rising from the surface at (x, y)."""
    return (f"M{x-22*s} {y} C{x-20*s} {y-8*s} {x-24*s} {y-14*s} {x-28*s} {y-20*s} C{x-18*s} {y-16*s} {x-14*s} {y-10*s} {x-12*s} {y-6*s} "
            f"C{x-12*s} {y-16*s} {x-10*s} {y-24*s} {x-6*s} {y-32*s} C{x-2*s} {y-22*s} {x} {y-14*s} {x+2*s} {y-8*s} "
            f"C{x+6*s} {y-16*s} {x+10*s} {y-24*s} {x+16*s} {y-28*s} C{x+14*s} {y-18*s} {x+12*s} {y-10*s} {x+14*s} {y-4*s} "
            f"C{x+18*s} {y-10*s} {x+24*s} {y-14*s} {x+30*s} {y-16*s} C{x+26*s} {y-8*s} {x+24*s} {y-4*s} {x+24*s} {y}Z")


def ripples(d: Drawing, x, y, rx, ry, role="light", n=2, w=1.8):
    for i in range(n):
        k = 1 + i * 0.6
        d.stroke(role, f"M{x - rx * k} {y} A{rx * k} {ry * k} 0 0 0 {x + rx * k} {y}", w)


def leaf(tx, ty, ex, ey, bulge=0.36, droop=8):
    """A pointed, slightly drooping leaf from (tx, ty) to (ex, ey)."""
    dx, dy = ex - tx, ey - ty
    n = math.hypot(dx, dy)
    px, py = -dy / n * n * bulge / 2, dx / n * n * bulge / 2
    mx, my = (tx + ex) / 2, (ty + ey) / 2 - droop
    return f"M{tx} {ty} Q{mx+px:.1f} {my+py:.1f} {ex} {ey} Q{mx-px:.1f} {my-py:.1f} {tx} {ty}Z"


def palm(d: Drawing, x, y, h, lean, role="dark", trunk_w=6):
    """A palm tree with its base at (x, y), top at (x + lean, y - h)."""
    tx, ty = x + lean, y - h
    d.limb(role, f"M{x} {y} Q{x + lean*0.1} {y - h*0.6} {tx} {ty}", trunk_w)
    for ex, ey, dr in [(-34, 10, 6), (-28, -12, 6), (-6, -24, 4), (20, -18, 6), (34, 4, 6), (-16, 22, 2), (18, 20, 2)]:
        d.shape(role, leaf(tx, ty, tx + ex, ty + ey, 0.34, dr), shadow=False)


def freediver(d: Drawing, suit="dark", fin="hero", mask="hero2", stripe=None):
    """A freediver side-on, head to the left and face down, arms stretched ahead, long blade fins; spans x 28-194 around y 100."""
    d.shape(fin, "M142 94 L190 82 Q196 84 193 89 L144 101Z", spot=True)
    d.shape(fin, "M142 100 L193 106 Q196 111 190 113 L142 106Z", spot=True)
    d.limb(suit, "M108 100 L146 99", 10)
    d.limb(suit, "M72 92 Q52 84 28 90", 6)
    d.shape(suit, rrect(60, 89, 54, 20, 10))
    if stripe:
        d.shape(stripe, "M84 89 H92 V109 H84Z", shadow=False)
    d.shape(suit, circle(52, 100, 10))
    d.shape(mask, rrect(39, 99, 13, 9, 3), shadow=False)
    d.shape("light", rrect(41, 101, 8, 5, 2), shadow=False)


def person_top(d: Drawing, suit="pop", skin="skin", hair="hair", arms="star"):
    """A person seen from above, lying on their back, centred at (0, 0), head up."""
    if arms == "star":
        d.limb(skin, "M-9 -10 L-30 -30 M9 -10 L30 -30", 6.5)
    else:  # arms out to the sides, hands low (holding on)
        d.limb(skin, "M-9 -10 L-24 4 M9 -10 L24 4", 6.5)
    d.limb(skin, "M-5 14 L-15 46 M5 14 L15 46", 8)
    d.shape(suit, "M-11 -15 Q0 -19 11 -15 L10 6 Q12 18 4 20 H-4 Q-12 18 -10 6Z")
    d.shape(skin, circle(0, -24, 8))
    d.shape(hair, "M-8 -26 A8 8 0 0 1 8 -26 Q0 -21 -8 -26Z", shadow=False)


# ================================================================ FREEDIVING
def freedive_descent(d: Drawing):
    d.band("far", waves(30, 3, 26))
    d.band("mid", waves(72, 4, 30))
    d.band("near", waves(122, 5, 34))
    d.band("deep", waves(176, 4, 38), line=False)
    rays(d)
    d.stroke("light", "M150 26 V230", 1.8)
    for y in (70, 110, 150):
        d.shape("light", rrect(146, y, 8, 4, 2), shadow=False, line=False)
    d.shape("pop", "M134 30 Q134 18 150 18 Q166 18 166 30Z", spot=True)
    d.shape("hero2", rrect(132, 27, 36, 5, 2.5), shadow=False)
    group(d, "translate(98 108) rotate(-74) scale(.84) translate(-100 -100)", lambda: freediver(d, stripe="hero2"))
    bubbles(d, [(124, 160, 2.2), (128, 148, 3), (122, 136, 2)])


def freedive_buoy(d: Drawing):
    d.disc("glow", 48, 42, 14)
    d.shape("light", cloud(124, 34, 0.8), shadow=False)
    d.band("mid", waves(92, 3, 28))
    rays(d, ((40, 56), (128, 138)), 0.14)
    d.band("near", waves(140, 5, 34))
    d.band("deep", waves(180, 4, 38), line=False)
    d.stroke("light", "M100 98 V230", 1.8)
    group(d, "translate(122 154) rotate(90) scale(.34) translate(-100 -100)", lambda: freediver(d))
    bubbles(d, [(112, 124, 2), (118, 114, 2.6)])
    # float with a diver-down flag
    d.stroke("dark", "M100 90 V34", 2.4, shadow=True)
    d.shape("pop", "M100 34 H134 V58 H100Z", spot=True)
    d.shape("light", "M100 34 H108 L134 52 V58 H126 L100 40Z", shadow=False)
    d.shape("hero2", "M66 92 C66 82 82 78 100 78 C118 78 134 82 134 92 C134 102 118 106 100 106 C82 106 66 102 66 92Z")
    d.shape("hero", "M66 92 C66 99 82 104 100 104 C118 104 134 99 134 92 C134 97 132 100 128 102 C118 108 82 108 72 102 C68 100 66 97 66 92Z", shadow=False)
    d.shape("light", ellipse(88, 86, 10, 3), shadow=False, line=False)
    d.stroke("light", "M52 100 Q60 96 68 100 M132 100 Q140 96 148 100", 2)


MANTA = ("M100 66 C111 66 118 72 123 82 C140 82 164 90 184 104 C164 108 146 114 130 122 C122 132 110 140 100 140 "
         "C90 140 78 132 70 122 C54 114 36 108 16 104 C36 90 60 82 77 82 C82 72 89 66 100 66Z")


def freedive_manta(d: Drawing):
    water(d)
    rays(d)

    def manta():
        d.stroke("manta", "M100 136 Q102 160 96 186", 2.4)
        d.shape("manta", "M86 70 C80 60 82 52 88 50 C90 58 93 64 96 68Z M114 70 C120 60 118 52 112 50 C110 58 107 64 104 68Z")
        d.shape("manta", MANTA, spot=True)
        d.shape("manta2", "M66 94 C78 88 90 92 94 104 C84 106 74 102 66 94Z M134 94 C122 88 110 92 106 104 C116 106 126 102 134 94Z", shadow=False, line=False)
        d.stroke("light", "M88 70 Q100 75 112 70", 1.6, line=False)
    group(d, "translate(100 116) rotate(-12) scale(.86) translate(-100 -100)", manta)
    group(d, "translate(118 44) rotate(-8) scale(.42) translate(-100 -100)", lambda: freediver(d))
    bubbles(d, [(40, 66, 2.5), (34, 54, 3.4)])


# ================================================================ CANYONING
def canyon_abseil(d: Drawing):
    d.shape("far", "M140 -30 H230 V230 H150 L160 150 L146 96 L158 40Z")
    d.shape("mid", "M168 -30 H230 V230 H176 L184 150 L172 90 L182 30Z", shadow=False)
    d.shape("near", "M-30 36 Q30 30 84 34 Q94 36 94 46 L92 110 L96 180 H-30Z")
    d.shape("deep", "M-30 34 Q20 22 40 30 Q54 18 66 30 Q78 24 86 34 Q50 40 -30 42Z", shadow=False)
    d.shape("light", "M54 36 Q84 30 94 44 L98 172 L82 172 L80 54 Q72 42 54 42Z")
    d.stroke("far", "M86 56 V160 M92 70 V150", 1.6)
    d.band("teal", waves(168, 4, 26))
    d.shape("light", splash(90, 170, 0.7), shadow=False)
    # rope and canyoner
    d.stroke("hero2", "M76 38 L112 92 L118 122 Q114 146 104 168", 2.2, shadow=True)

    def person():
        d.limb("dark", "M120 124 L108 120 L98 132 M120 126 L110 132 L100 142", 6.5)
        d.limb("dark", "M120 124 L126 100", 12)
        d.limb("dark", "M124 102 L112 92 M124 104 L118 120", 5)
        d.shape("pop", rrect(113, 117, 14, 7, 2.5), shadow=False, spot=True)
        d.shape("skin", circle(130, 90, 7.5))
        d.shape("hero", "M122 89 A8.5 8.5 0 0 1 139 89 Z", shadow=False, spot=True)
    group(d, "translate(-40 -46) scale(1.36)", person)


def canyon_gear(d: Drawing):
    d.shape("near", "M-30 -30 H58 Q48 40 62 80 Q52 120 56 160 H-30Z")
    d.shape("deep", "M230 -30 H142 Q154 40 138 84 Q150 120 146 160 H230Z")
    d.shape("light", "M78 -30 H122 Q120 60 126 132 H74 Q80 60 78 -30Z")
    d.stroke("far", "M92 0 V120 M106 10 V126", 1.6)
    d.band("teal", waves(128, 3, 24))
    d.stroke("light", "M74 136 Q84 132 94 136 M110 140 Q120 136 130 140", 2)
    d.band("ground", "M-30 152 Q40 140 100 146 T230 144")
    # rope coil
    for i, (cy, rx) in enumerate([(160, 34), (154, 32), (148, 30)]):
        d.limb("pop", ellipse(132, cy, rx, 12), 6, spot=i == 2, shadow=i == 0)
    d.limb("pop", "M104 160 Q90 176 70 174", 6)
    # carabiner clipped to the coil
    d.limb("light", "M156 124 C152 110 160 98 170 100 C180 102 182 114 176 128 C172 138 160 138 156 124Z", 3.6)
    d.stroke("dark", "M157 125 L163 108", 2)
    # helmet
    d.shape("hero", "M30 152 C30 120 48 104 70 104 C92 104 108 120 108 152Z", spot=True)
    d.shape("hero2", rrect(26, 148, 86, 8, 4))
    d.marks("dark", rrect(52, 112, 7, 12, 3) + rrect(66, 108, 7, 14, 3) + rrect(80, 112, 7, 12, 3))
    d.shape("light", rrect(84, 130, 14, 10, 4), shadow=False)
    d.stroke("dark", "M84 135 H40", 2.2, line=False)


def canyon_slide(d: Drawing):
    d.disc("glow", 100, 26, 12)
    d.shape("far", "M40 -30 H160 V140 H40Z", shadow=False)
    d.shape("mid", "M120 20 Q150 34 140 70 Q130 100 100 120 Q84 132 78 156 L40 156 Q52 118 82 98 Q112 78 108 50 Q106 30 120 20Z")
    d.limb("light", "M124 24 Q140 44 126 68 Q112 92 88 108 Q70 122 66 150", 9, shadow=False)
    d.shape("near", "M-30 -30 H62 Q46 40 62 90 Q46 130 54 230 H-30Z")
    d.shape("deep", "M230 -30 H144 Q160 50 140 100 Q156 150 150 230 H230Z")
    d.band("teal", waves(156, 4, 24))

    def slider():
        d.limb("hero2", "M0 0 L-14 12 L-26 14 M0 0 L-12 16 L-22 22", 5)
        d.limb("hero", "M0 0 L6 -16", 10, spot=True)
        d.limb("skin", "M5 -12 L16 -24 M3 -12 L-4 -28", 4.5)
        d.shape("skin", circle(9, -24, 6))
        d.shape("pop", "M3 -25 A6.5 6.5 0 0 1 16 -25Z", shadow=False)
    group(d, "translate(104 104) rotate(-14) scale(1.5)", slider)
    d.shape("light", splash(68, 158, 0.8), shadow=False)
    d.stroke("light", "M84 176 Q96 172 108 176 M30 172 Q40 168 50 172", 2)


# ================================================================ WILD SWIMMING
def wildswim_lake(d: Drawing):
    d.disc("glow", 150, 46, 13)
    d.band("mid", "M-30 104 L20 70 L44 86 L80 50 L112 84 L138 66 L170 92 L230 80")
    for snow in ["M80 50 L91 62 L85 60 L80 65 L74 60 L69 62Z", "M138 66 L147 76 L142 74 L137 78 L132 74 L129 75Z"]:
        d.shape("light", snow, shadow=False)
    d.shape("dark", pines([(10, 30), (24, 40), (38, 28), (160, 30), (176, 42), (192, 30)], 112, 30))
    d.band("near", "M-30 110 H230")
    ripples(d, 92, 140, 22, 6, "light", 2)
    d.stroke("pop", "M108 142 Q130 146 144 134", 1.4)
    d.shape("pop", rrect(140, 118, 30, 16, 8), spot=True, extra='transform="rotate(-12 155 126)"')
    d.shape("light", rrect(146, 121, 14, 3, 1.5), shadow=False, extra='transform="rotate(-12 155 126)"')
    d.limb("skin", "M102 140 Q96 104 66 124", 7)
    d.shape("skin", ellipse(86, 136, 11, 10))
    d.shape("hero", "M75 135 A11 11 0 0 1 97 133 Q86 128 75 135Z", shadow=False, spot=True)
    d.marks("dark", rrect(76, 134, 7, 4, 2))
    d.band("deep", waves(144, 3, 22))
    d.stroke("light", "M60 160 Q68 156 76 160 M118 168 Q126 164 134 168", 2)


def wildswim_jetty(d: Drawing):
    d.disc("glow", 60, 64, 16)
    d.band("far", hills(92, 12, 10))
    d.shape("deep", pines([(116, 30), (130, 44), (146, 34), (160, 48), (176, 36), (192, 44)], 104, 30))
    d.shape("deep", pines([(6, 26), (20, 34), (34, 24)], 104, 26), shadow=False)
    d.band("near", "M-30 102 H230")
    d.stroke("light", "M20 112 H60 M120 116 H170", 2.6, line=False)
    # jetty
    d.limb("wood", "M30 120 V176 M70 120 V170 M112 120 V166", 6)
    d.stroke("dark", "M126 122 V158 M138 122 V158 M126 132 H138 M126 144 H138 M126 156 H138", 2.4)
    d.shape("wood2", "M-30 114 H142 V122 H-30Z")
    d.stroke("wood", "M-30 118 H142", 1.2, line=False)
    # towel hung over the edge
    d.shape("hero", "M54 110 H82 V138 H54Z", spot=True)
    d.shape("light", "M54 124 H82 V128 H54Z", shadow=False)
    d.shape("hero2", rrect(86, 104, 20, 10, 3))
    # swimmer by the ladder
    ripples(d, 160, 148, 12, 3.5)
    d.shape("skin", circle(160, 142, 8))
    d.shape("pop", "M152 141 A8 8 0 0 1 168 141Z", shadow=False)
    d.band("mid", waves(170, 3, 26))


def wildswim_icedip(d: Drawing):
    d.band("light", hills(84, 12, 20))
    d.shape("dark", pines([(20, 26), (34, 34), (48, 24), (140, 28), (156, 36), (172, 26)], 88, 26))
    d.band("near", "M-30 96 H230")
    d.shape("light", "M-30 110 L14 104 L40 112 L22 120 L-30 120Z")
    d.shape("light", "M150 112 L178 106 L230 110 L230 124 L170 122Z")
    d.shape("light", "M30 168 L56 160 L84 166 L70 176 L30 176Z")
    ripples(d, 100, 136, 26, 7)
    d.limb("skin", "M84 134 L66 126 M116 134 L134 126", 6)
    d.shape("hero", "M80 140 Q80 124 100 122 Q120 124 120 140Z")
    d.shape("skin", circle(100, 112, 11))
    d.shape("pop", "M88 110 Q88 96 100 96 Q112 96 112 110 Q100 106 88 110Z", spot=True)
    d.shape("light", rrect(87, 106, 26, 5, 2.5), shadow=False)
    d.shape("light", circle(100, 92, 5))
    d.marks("dark", circle(96, 114, 1.4) + circle(104, 114, 1.4))
    d.shape("light", cloud(116, 112, 0.5), line=False)
    d.band("deep", waves(140, 3, 24))
    for x, y in [(30, 40), (60, 24), (150, 30), (176, 56), (128, 58), (44, 70)]:
        d.marks("light", circle(x, y, 2.2))


# ================================================================ DEEP-SEA FISHING
MARLIN = "M50 92 C64 82 92 80 120 86 C136 90 148 94 156 98 C148 104 136 108 120 112 C92 116 64 112 50 104 Q46 98 50 92Z"


def marlin(d: Drawing):
    d.shape("marlin2", "M62 88 C64 66 78 56 98 58 C110 60 118 70 124 87Z")
    d.shape("marlin2", "M152 98 C162 88 170 78 182 64 C178 80 174 92 170 98 C174 104 178 116 182 132 C170 118 162 108 152 98Z")
    d.shape("marlin", "M53 94.5 L12 97 L53 100.5Z")
    d.shape("marlin", MARLIN, spot=True)
    d.shape("light", "M52 102 C70 108 96 110 120 108 C136 106 146 102 154 99 C146 104 136 108 120 112 C92 116 64 112 52 102Z", shadow=False)
    d.stroke("marlin3", "M78 88 V108 M90 86 V110 M102 86 V110 M114 87 V109 M126 89 V106", 2.2, line=False)
    d.shape("marlin2", "M78 104 L62 122 L90 108Z", shadow=False)
    d.marks("dark", circle(60, 96, 2.4))


def deepsea_marlin(d: Drawing):
    d.disc("glow", 152, 50, 14)
    d.band("far", "M-30 140 H230")
    d.band("mid", waves(156, 4, 30))
    group(d, "translate(100 96) rotate(30) scale(.9) translate(-100 -100)", lambda: marlin(d))
    d.stroke("dark", "M34 -10 Q50 40 63 71", 1.3)
    d.shape("light", spray(162, 146, 1.2, left=False), shadow=False)
    d.shape("light", spray(150, 148, 1.0, left=True), shadow=False)
    for x, y, r in [(180, 124, 2.4), (130, 132, 2), (122, 122, 2.4)]:
        d.shape("light", circle(x, y, r), shadow=False)
    d.band("near", waves(170, 5, 34))
    d.band("deep", waves(188, 4, 38), line=False)


def deepsea_reel(d: Drawing):
    d.disc("glow", 46, 50, 13)
    d.band("far", "M-30 120 H230")
    d.band("mid", waves(140, 4, 30))
    d.band("near", waves(166, 5, 34))
    d.stroke("dark", "M168 46 L180 124", 1.2)
    d.shape("light", spray(180, 128, 0.7, left=True), shadow=False)
    d.shape("light", spray(180, 128, 0.7, left=False), shadow=False)
    d.limb("dark", "M40 214 Q70 120 168 46", 6)
    d.limb("dark", "M46 196 L60 160", 13)
    d.shape("hero2", rrect(60, 112, 44, 34, 9), extra='transform="rotate(-30 82 129)"', spot=True)
    d.shape("light", circle(82, 129, 13), shadow=False)
    d.shape("dark", circle(82, 129, 5), shadow=False)
    d.limb("dark", "M82 129 L104 116", 4)
    d.shape("light", ellipse(106, 114, 7, 5), extra='transform="rotate(-30 106 114)"')
    for x, y in [(118, 82), (146, 60)]:
        d.marks("dark", circle(x, y, 3))


def deepsea_boat(d: Drawing):
    d.disc("glow", 46, 50, 14)
    d.shape("light", cloud(138, 36, 0.8), shadow=False)
    d.band("far", "M-30 132 H230")
    # outriggers and tuna tower
    d.stroke("dark", "M88 92 L18 40 M120 92 L184 44", 2, shadow=True)
    d.stroke("dark", "M82 98 L84 54 M118 98 L114 54 M84 54 H114 M84 72 H116 M83 86 H118", 2.4, shadow=True)
    d.shape("dark", rrect(82, 50, 34, 6, 2))
    d.shape("pop", "M98 50 V36 L110 41 L98 46Z", spot=True, shadow=False)
    d.shape("hero2", "M64 112 L72 92 H126 L134 112Z")
    d.shape("dark", "M76 96 H90 V106 H72Z M96 96 H112 V106 H96Z M118 96 H124 L128 106 H118Z", shadow=False)
    d.shape("hero", "M28 112 H168 L156 140 H48 Q34 132 28 112Z", spot=True)
    d.shape("light", "M38 122 H162 L160 127 H42Z", shadow=False)
    d.band("mid", waves(140, 3, 26))
    d.shape("light", "M140 142 Q176 136 230 150 V156 Q176 146 146 148Z", shadow=False)
    d.band("near", waves(162, 4, 30))
    d.band("deep", waves(184, 4, 36), line=False)


# ================================================================ GLASS-BOTTOM BOAT
def glassboat_window(d: Drawing):
    d.band("wood2", "M-30 -30 H230", shadow=False, line=False)
    d.stroke("wood", "M-30 20 H230 M-30 40 H230 M-30 160 H230 M-30 180 H230 M60 0 V40 M140 20 V60 M90 160 V200", 1.6, line=False)
    d.shape("wood", rrect(-30, 52, 260, 14, 2))
    d.shape("wood", rrect(-30, 136, 260, 14, 2))

    def window():
        d.shape("mid", rrect(40, 70, 120, 62, 8))
        d.shape("near", "M40 112 Q70 104 100 112 T160 110 V124 Q160 132 152 132 H48 Q40 132 40 124Z", shadow=False, line=False)
        d.shape("pop", "M52 132 C50 120 54 112 58 108 C60 116 62 120 64 112 C66 120 68 124 66 132Z", shadow=False, spot=True)
        d.shape("hero2", "M130 132 Q130 116 140 114 Q150 116 150 132Z", shadow=False)
        d.shape("hero2", fish(84, 88, 1.1), shadow=False, spot=True)
        d.shape("hero", fish(120, 100, 1.3, right=True), shadow=False)
        d.shape("hero2", fish(104, 120, 0.8), shadow=False)
        d.stroke("light", "M52 80 L66 74 M134 78 L148 74 M60 96 L74 90", 2, line=False)
    _clip(d, window)
    d.stroke("dark", rrect(40, 70, 120, 62, 8), 4)
    d.stroke("light", "M48 76 L60 76", 2, line=False)


def glassboat_section(d: Drawing):
    d.disc("glow", 160, 34, 12)
    d.band("far", "M-30 84 H230")
    d.band("mid", waves(98, 3, 26))
    rays(d, ((64, 80), (118, 128)), 0.12)
    d.band("near", waves(150, 4, 30))
    d.band("ground", "M-30 178 Q40 168 80 176 T160 172 T230 174")
    d.shape("pop", "M30 178 C28 160 34 150 40 146 C42 156 44 160 48 150 C52 160 54 168 52 178Z", spot=True)
    d.shape("hero2", "M140 178 Q140 160 154 158 Q168 160 168 178Z")
    for x, y, s, r in [(70, 150, 1.0, False), (128, 136, 0.9, True), (100, 162, 0.8, False)]:
        d.shape("hero2", fish(x, y, s, right=r), shadow=False)
    # boat
    d.stroke("dark", "M48 92 V56 M100 92 V56 M152 92 V56", 2.4, shadow=True)
    d.shape("hero2", "M38 58 Q100 42 162 58 V63 H38Z", spot=True)
    d.shape("hero", "M30 88 H170 L160 118 Q100 128 40 118Z", spot=True)
    d.shape("light", "M62 112 H138 L136 120 Q100 124 64 120Z", shadow=False)
    d.marks("dark", circle(78, 98, 5) + circle(100, 98, 5) + circle(122, 98, 5))
    d.stroke("light", "M64 124 V140 M100 128 V146 M136 124 V140", 1.2, line=False)


def glassboat_below(d: Drawing):
    d.band("sky2", "M-30 -30 H230", shadow=False, line=False)
    d.band("far", waves(30, 3, 24))
    rays(d, ((70, 92), (124, 138)), 0.2)
    d.band("mid", waves(100, 4, 30), shadow=False)
    d.band("near", waves(146, 5, 34))
    d.band("deep", waves(182, 4, 38), line=False)
    # the hull seen from below, with its glass panel and two faces peering down
    d.shape("hero", "M14 22 H186 Q178 58 150 72 Q100 86 50 72 Q22 58 14 22Z")
    d.shape("light", rrect(52, 34, 96, 34, 10))
    d.shape("sky2", rrect(56, 38, 88, 26, 7), shadow=False, line=False)
    for x, hair in ((82, "hair"), (118, "dark")):
        d.shape("skin", circle(x, 50, 10), shadow=False)
        d.shape(hair, f"M{x - 10} 47 A10 10 0 0 1 {x + 10} 47 Q{x} 43 {x - 10} 47Z", shadow=False)
        d.marks("dark", circle(x - 3.5, 53, 1.7) + circle(x + 3.5, 53, 1.7))
        d.stroke("dark", f"M{x - 3} 58 Q{x} 61 {x + 3} 58", 1.4)
    d.stroke("light", "M60 42 L70 36 M128 64 L138 58", 2, line=False)

    def angel():
        d.shape("hero2", "M-8 -8 C-14 -18 -24 -22 -34 -22 C-28 -12 -22 -6 -14 -3Z M-8 8 C-14 18 -24 22 -34 22 C-28 12 -22 6 -14 3Z")
        d.shape("hero2", "M0 -40 C10 -24 22 -12 24 0 C22 12 10 24 0 40 C-4 26 -6 14 -8 8 L-6 -8 C-6 -14 -4 -26 0 -40Z", spot=True)
        d.stroke("dark", "M6 -24 Q2 0 6 24 M14 -14 Q10 0 14 14", 3, line=False)
        d.marks("dark", circle(16, -4, 2.2))
    group(d, "translate(100 138) scale(-.95 .95)", angel)
    d.shape("pop", fish(150, 120, 0.8), shadow=False)
    d.shape("pop", fish(44, 130, 0.7, right=True), shadow=False)
    bubbles(d, [(146, 156, 2.2), (152, 146, 3)])


# ================================================================ BANANA BOAT
BANANA = ("M26 112 C22 100 26 90 34 86 C40 94 46 104 60 108 L150 108 C164 108 172 116 170 126 "
          "C168 134 160 138 150 138 L60 138 C42 138 30 126 26 112Z")


def banana(d: Drawing, riders=True, jackets=("pop", "hero", "pop")):
    if riders:
        for i, x in enumerate((70, 104, 138)):
            d.limb("skin", f"M{x} 102 L{x - 14} 98", 5)
            d.shape(jackets[i], rrect(x - 8, 82, 18, 26, 6), spot=i == 1)
            d.shape("skin", circle(x + 1, 74, 7.5))
            d.shape("hair", f"M{x - 6.5} 72 A7.5 7.5 0 0 1 {x + 8.5} 72 Q{x + 1} 69 {x - 6.5} 72Z", shadow=False)
    d.shape("banana", BANANA)
    d.shape("banana2", "M30 122 C40 132 50 136 60 136 L150 136 C160 136 166 132 169 128 C168 134 160 138 150 138 L60 138 C46 138 36 132 30 122Z",
            shadow=False)
    d.shape("dark", "M28 90 C30 84 34 82 38 84 L34 90Z", shadow=False)
    d.stroke("banana2", "M58 116 H156", 2, line=False)
    if riders:
        for x in (62, 96, 130):
            d.marks("dark", rrect(x - 2, 104, 4, 6, 1.5))


def banana_ride(d: Drawing):
    d.disc("glow", 160, 40, 14)
    d.shape("light", cloud(24, 40, 0.8), shadow=False)
    d.band("far", "M-30 112 H230")
    d.stroke("dark", "M-10 90 L30 92", 1.6)
    d.band("mid", waves(126, 3, 26))
    group(d, "translate(6 4) scale(.94)", lambda: banana(d))
    d.shape("light", spray(176, 140, 1.4, left=False), shadow=False)
    d.shape("light", "M24 138 Q60 146 120 140 L176 140 Q120 150 60 152 Q36 150 24 138Z", shadow=False)
    d.band("near", waves(150, 4, 28))
    d.band("deep", waves(178, 4, 34), line=False)


def banana_aerial(d: Drawing):
    d.band("mid", "M-30 -30 H230", shadow=False, line=False)
    d.stroke("far", "M10 40 q8 -4 16 0 M150 150 q8 -4 16 0 M30 170 q8 -4 16 0 M160 30 q8 -4 16 0", 2.4, line=False)
    # wake fanning out behind the speedboat
    d.shape("light", "M128 48 L40 140 L52 150 Z M128 48 L150 176 L166 170Z", shadow=False, line=False, extra='opacity=".55"')

    def boat():
        d.shape("light", "M0 -26 C10 -14 12 4 10 22 H-10 C-12 4 -10 -14 0 -26Z")
        d.shape("hero", "M0 -16 C5 -10 6 -2 6 4 H-6 C-6 -2 -5 -10 0 -16Z", shadow=False, spot=True)
        d.shape("dark", rrect(-6, 8, 12, 6, 2), shadow=False)
    group(d, "translate(130 44) rotate(40)", boat)
    d.stroke("dark", "M114 62 L92 92", 1.4)

    def ban():
        d.shape("banana", "M-10 -40 C-4 -46 4 -46 8 -40 C12 -20 12 20 6 44 C2 50 -6 50 -8 44 C-12 20 -14 -20 -10 -40Z")
        d.shape("dark", "M-4 -44 C-2 -48 2 -48 4 -44Z", shadow=False)
        d.stroke("banana2", "M5 -34 C9 -10 9 20 4 40", 2, line=False)
        for i, y in enumerate((-22, 0, 22)):
            role = ("pop", "hero", "pop")[i]
            d.shape(role, ellipse(0, y + 3, 9, 6), spot=i == 1)
            d.shape("skin", circle(0, y, 4.6))
            d.shape("hair", circle(0, y + 1, 3.6), shadow=False)
            d.limb("skin", f"M-7 {y + 3} L-10 {y - 6} M7 {y + 3} L10 {y - 6}", 3.2)
    group(d, "translate(76 118) rotate(40)", ban)


def banana_wipeout(d: Drawing):
    d.disc("glow", 40, 48, 13)
    d.band("far", "M-30 104 H230")
    d.band("mid", waves(118, 3, 26))
    group(d, "translate(120 92) rotate(-24) scale(.66) translate(-100 -112)", lambda: banana(d, riders=False))
    d.shape("light", splash(132, 132, 1.1), shadow=False)
    d.band("near", waves(140, 4, 28))
    for x, y, jacket, spot in [(62, 140, "pop", True), (104, 154, "hero", False)]:
        ripples(d, x, y + 4, 16, 4)
        d.limb("skin", f"M{x - 8} {y - 2} L{x - 18} {y - 22} M{x + 8} {y - 2} L{x + 18} {y - 22}", 5)
        d.shape(jacket, rrect(x - 11, y - 8, 22, 14, 6), spot=spot)
        d.shape("skin", circle(x, y - 16, 8))
        d.shape("hair", f"M{x - 8} {y - 18} A8 8 0 0 1 {x + 8} {y - 18} Q{x} {y - 14} {x - 8} {y - 18}Z", shadow=False)
        d.marks("dark", ellipse(x, y - 11, 2.6, 1.8))
    for x, y, r in [(80, 104, 2.6), (152, 96, 2.4), (164, 110, 2), (96, 90, 2)]:
        d.shape("light", circle(x, y, r), shadow=False)
    d.band("deep", waves(176, 4, 34), line=False)


# ================================================================ SUNBATHING
def sunbathe_lounger(d: Drawing):
    d.disc("glow", 150, 46, 18)
    d.band("far", "M-30 100 H230")
    d.band("mid", waves(114, 3, 26))
    d.band("ground", "M-30 128 Q60 120 120 126 T230 124")
    # lounger
    d.limb("dark", "M58 166 L66 144 M150 166 L144 144 M38 166 L46 136", 3.6)
    d.shape("hero2", "M46 138 H168 V146 H46Z")
    d.shape("hero2", "M48 144 L24 100 L31 96 L56 140Z")
    d.shape("light", "M66 138 H82 V146 H66Z M98 138 H114 V146 H98Z M130 138 H146 V146 H130Z", shadow=False, line=False)
    # sunbather, arms behind the head
    d.limb("skin", "M70 132 L118 130 L160 132", 10)
    d.limb("skin", "M44 108 L70 132", 16)
    d.shape("suit", "M44 106 L56 102 L76 126 L72 138 L60 136Z", spot=True)
    d.limb("skin", "M48 106 L60 92 L42 84", 5)
    d.shape("skin", circle(38, 96, 10))
    d.shape("hair", "M28 98 A10 10 0 0 1 44 87 Q34 90 28 98Z", shadow=False)
    d.marks("dark", "M34 96 H46 Q46 102 41 102 Q37 102 36 98Z")
    d.stroke("dark", "M36 104 Q40 106 44 104", 1.3, line=False)
    # straw hat on the sand
    d.shape("glow2", ellipse(176, 152, 16, 4))
    d.shape("glow2", "M166 152 Q166 138 176 138 Q186 138 186 152Z")
    d.shape("pop", "M166 148 H186 V151 H166Z", shadow=False)
    d.band("near", hills(184, 4, 20), line=False)


def sunbathe_lotion(d: Drawing):
    d.disc("glow", 150, 46, 16)
    d.band("far", "M-30 100 H230")
    d.band("mid", waves(114, 3, 24))
    d.band("ground", "M-30 128 Q60 120 120 126 T230 124")
    # towel
    d.shape("hero2", "M-30 150 L230 138 V230 H-30Z")
    d.shape("light", "M-30 160 L230 148 V156 L-30 168Z", shadow=False)
    # bottle
    d.shape("dark", rrect(80, 46, 26, 14, 3))
    d.shape("light", rrect(76, 56, 34, 10, 3))
    d.shape("hero", "M74 66 H112 Q116 66 116 72 L118 160 Q118 166 112 166 H74 Q68 166 68 160 L70 72 Q70 66 74 66Z", spot=True)
    d.shape("light", rrect(76, 92, 34, 44, 6), shadow=False)
    d.shape("glow2", circle(93, 114, 9), shadow=False)
    d.stroke("glow2", "M93 99 V102 M93 126 V129 M78 114 H81 M105 114 H108 M83 104 L85 106 M101 122 L103 124 M83 124 L85 122 M101 106 L103 104", 2, line=False)
    # sunglasses and shell
    d.limb("dark", "M120 152 L126 146 M150 150 L176 144", 2.6)
    d.shape("dark", ellipse(134, 156, 12, 9) + ellipse(160, 154, 12, 9))
    d.stroke("dark", "M144 154 Q147 150 150 154", 2.4)
    d.shape("light", ellipse(130, 152, 4, 2), shadow=False, line=False)
    d.shape("pop", "M28 140 L50 140 Q48 124 39 122 Q30 124 28 140Z")
    d.stroke("light", "M39 124 V139 M34 128 L33 139 M44 128 L45 139", 1.2, line=False)


def sunbathe_sun(d: Drawing):
    d.band("far", "M-30 150 H230")
    d.band("mid", waves(162, 3, 24))
    d.band("ground", "M-30 176 Q60 168 120 174 T230 172")
    pts = []
    for i in range(12):
        a = math.radians(i * 30)
        ca, sa = math.cos(a), math.sin(a)
        c2, s2 = math.cos(a + 0.16), math.sin(a + 0.16)
        c3, s3 = math.cos(a - 0.16), math.sin(a - 0.16)
        pts.append(f"M{100 + 50 * c3:.1f} {84 + 50 * s3:.1f} L{100 + 70 * ca:.1f} {84 + 70 * sa:.1f} L{100 + 50 * c2:.1f} {84 + 50 * s2:.1f}Z")
    d.shape("glow2", " ".join(pts), spot=True)
    d.shape("glow", circle(100, 84, 46))
    d.stroke("dark", "M54 74 L66 76 M146 74 L134 76", 3, line=False)
    d.marks("dark", "M64 70 H96 Q96 92 80 92 Q64 92 64 74Z M104 70 H136 V74 Q136 92 120 92 Q104 92 104 70Z M94 72 H106 V76 H94Z")
    d.shape("light", "M70 74 L78 74 L72 84Z M110 74 L118 74 L112 84Z", shadow=False)
    d.stroke("dark", "M84 104 Q100 116 116 104", 3)
    d.shape("pop", ellipse(70, 100, 6, 3.5), shadow=False, line=False)
    d.shape("pop", ellipse(130, 100, 6, 3.5), shadow=False, line=False)


# ================================================================ RIVER TUBING
def tubing_float(d: Drawing):
    d.disc("glow", 160, 40, 13)
    d.band("far", hills(84, 14, 10))
    d.band("mid", "M-30 100 Q40 90 100 98 T230 94")
    d.band("teal", "M-30 112 H230")
    d.stroke("light", "M20 124 H50 M150 120 H180", 2, line=False)
    # tube back rim, sunbather, tube front rim
    d.shape("tube", ellipse(98, 140, 48, 16))
    d.shape("teal", ellipse(98, 136, 24, 7), shadow=False)
    d.limb("skin", "M98 136 L128 122 L150 140", 8)
    d.limb("skin", "M96 134 L70 112", 15)
    d.shape("pop", "M66 110 L76 104 L100 132 L92 140Z", spot=True)
    d.limb("skin", "M72 110 L52 130 M76 112 L94 96 L96 80", 5)
    d.shape("light", rrect(91, 70, 9, 13, 2))
    d.shape("hero", rrect(91, 74, 9, 6, 1), shadow=False)
    d.shape("skin", circle(64, 100, 9))
    d.shape("hair", "M55 98 A9 9 0 0 1 72 96 Q62 94 55 98Z", shadow=False)
    d.marks("dark", rrect(62, 98, 10, 4, 2))
    d.shape("tube", "M50 140 C50 150 72 158 98 158 C124 158 146 150 146 140 C146 146 124 150 98 150 C72 150 50 146 50 140Z", shadow=False)
    d.stroke("light", "M64 148 Q80 152 96 152", 2, line=False)
    ripples(d, 98, 156, 54, 6, n=1)
    d.band("near", waves(170, 3, 26))


def tubing_karst(d: Drawing):
    d.disc("glow", 150, 34, 11)
    d.shape("far", "M-30 124 V60 Q-22 24 0 30 Q8 4 26 14 Q42 30 36 70 Q46 96 52 124Z")
    d.shape("far", "M120 124 Q112 70 126 46 Q130 16 150 18 Q166 10 174 30 Q188 46 182 80 Q196 100 200 124Z")
    d.shape("mid", "M40 124 Q40 80 54 60 Q60 32 80 34 Q98 36 100 62 Q112 90 112 124Z")
    for d_ in ["M0 30 Q8 4 26 14 Q34 22 34 30 Q22 22 14 30 Q6 24 0 30Z", "M126 46 Q130 16 150 18 Q166 10 174 30 Q160 26 150 32 Q138 28 126 46Z",
               "M54 60 Q60 32 80 34 Q98 36 100 62 Q90 50 78 54 Q64 48 54 60Z"]:
        d.shape("jungle", d_, shadow=False)
    d.shape("light", cloud(86, 92, 0.9), shadow=False, line=False, extra='opacity=".85"')
    d.band("near", "M-30 120 Q60 112 120 118 T230 114")
    d.band("teal", "M-30 130 Q100 122 230 128")
    d.stroke("light", "M20 144 H44 M156 140 H180", 2, line=False)
    for x, y, s, role, spot in [(148, 142, 0.75, "hero2", False), (60, 154, 0.95, "pop", True), (122, 174, 1.2, "hero", False)]:
        def t(role=role, spot=spot):
            d.shape(role, _ring(0, 0, 10, 22, 0.36), extra='fill-rule="evenodd"', spot=spot)
            d.limb("skin", "M0 -4 L-14 -12", 7)
            d.shape("skin", circle(-16, -18, 6.5))
            d.limb("skin", "M2 -2 L16 -4 L22 4", 5)
        group(d, f"translate({x} {y}) scale({s})", t)


def tubing_train(d: Drawing):
    d.band("ground", "M-30 -30 H230", shadow=False, line=False)
    d.shape("near", "M-30 -30 H60 Q40 30 56 80 Q70 130 40 230 H-30Z")
    d.shape("near", "M230 -30 H150 Q166 40 150 100 Q136 160 166 230 H230Z")
    d.shape("teal", "M60 -30 H150 Q166 40 150 100 Q136 160 166 230 H40 Q70 130 56 80 Q40 30 60 -30Z", shadow=False)
    d.stroke("light", "M80 20 q6 -3 12 0 M120 60 q6 -3 12 0 M70 140 q6 -3 12 0 M130 190 q6 -3 12 0", 2.2, line=False)
    for x, y, role, spot, rot in [(94, 46, "hero", False, -10), (104, 106, "pop", True, 4), (98, 166, "hero2", False, -6)]:
        def t(role=role, spot=spot):
            d.shape(role, _ring(0, 0, 13, 26), extra='fill-rule="evenodd"', spot=spot)
            person_top(d, "dark", arms="hold")
        group(d, f"translate({x} {y}) rotate({rot}) scale(.78)", t)
    d.shape("deep", "M-30 -30 H40 Q30 20 44 50 Q20 70 -30 60Z")
    d.shape("deep", "M230 120 Q176 130 172 170 Q190 200 230 210Z")


# ================================================================ POOL DAY
def pool_ladder(d: Drawing):
    d.band("pool", "M-30 -30 H230", shadow=False, line=False)
    d.stroke("pool2", "M-30 84 Q0 76 30 86 T90 84 T150 86 T230 82 M-30 120 Q10 112 50 122 T130 120 T230 118 "
                      "M-30 156 Q20 148 60 158 T140 156 T230 154 M-30 190 Q20 182 60 192 T140 190 T230 188", 2.6, line=False)
    d.stroke("pool2", "M40 64 V200 M100 64 V200 M160 64 V200", 1.2, line=False)
    d.shape("ground", "M-30 -30 H230 V50 H-30Z")
    d.shape("light", "M-30 48 H230 V60 H-30Z")
    d.stroke("far", "M10 -30 V48 M60 -30 V48 M110 -30 V48 M160 -30 V48 M-30 18 H230", 1.2, line=False)
    for y in (98, 128, 158):
        d.shape("steel", rrect(68, y, 64, 6, 3), extra='opacity=".75"', shadow=False)
    d.limb("steel", "M64 184 V58 Q64 30 88 28 Q104 28 106 46", 8)
    d.limb("steel", "M136 184 V58 Q136 30 160 28 Q176 28 178 46", 8)
    d.stroke("light", "M61 176 V62 M133 176 V62", 1.8, line=False)
    ripples(d, 64, 186, 10, 3, n=1)
    ripples(d, 136, 186, 10, 3, n=1)

    def duck():
        d.shape("pop", "M-14 6 Q-16 -6 -4 -6 Q-4 -16 6 -16 Q14 -16 14 -8 Q14 -4 10 -2 Q18 4 10 12 Q0 16 -10 12 Q-14 10 -14 6Z", spot=True)
        d.shape("glow2", "M13 -10 L22 -8 L13 -5Z", shadow=False)
        d.marks("dark", circle(8, -10, 1.6))
    group(d, "translate(32 128)", duck)
    ripples(d, 32, 142, 14, 3, n=1)


def pool_flamingo(d: Drawing):
    d.disc("glow", 100, 36, 12)
    group(d, "translate(44 104) scale(.8)", lambda: palm(d, 0, 0, 86, 10))
    d.band("ground", "M-30 100 H230")
    d.band("light", "M-30 106 H230")
    d.band("pool", "M-30 112 H230")
    d.stroke("pool2", "M-30 136 Q10 128 50 138 T130 136 T230 134 M-30 172 Q20 164 60 174 T140 172 T230 170", 2.6, line=False)
    # flamingo float
    d.shape("flam", "M40 138 C34 122 44 110 60 112 C74 104 120 104 140 116 C152 124 152 136 140 144 C120 156 64 156 48 148 Q40 144 40 138Z")
    d.shape("flam2", "M60 120 C78 112 112 112 126 124 C110 120 82 122 64 132Z", shadow=False)
    d.shape("flam", "M42 128 C30 118 28 108 34 100 C38 110 44 116 52 118Z", shadow=False)
    d.limb("flam", "M132 124 C150 110 154 92 140 80 C128 70 128 56 140 50", 11, spot=True)
    d.shape("flam", circle(144, 50, 10))
    d.shape("light", "M150 46 L166 52 L154 58Z", shadow=False)
    d.shape("dark", "M160 50 L166 52 L164 60 L158 56Z", shadow=False)
    d.marks("dark", circle(146, 47, 1.8))
    d.stroke("light", "M30 154 Q50 160 70 158 M130 158 Q150 156 166 150", 2.2)


def pool_dive(d: Drawing):
    d.disc("glow", 152, 44, 13)
    d.shape("light", cloud(30, 40, 0.8), shadow=False)
    d.band("ground", "M-30 116 H230")
    # diving board
    d.limb("dark", "M30 116 V84 M46 116 V84", 4)
    d.shape("hero2", "M14 80 H96 V86 H14Z")
    d.shape("dark", rrect(18, 70, 12, 10, 2))
    d.band("pool", "M-30 126 H230")
    d.stroke("pool2", "M-30 150 Q20 142 60 152 T140 150 T230 148", 2.6, line=False)
    # lane rope
    for i, x in enumerate(range(-20, 230, 12)):
        d.shape("hero" if i % 2 else "light", ellipse(x, 168, 5.5, 4), shadow=False, spot=i % 2 == 1)

    def diver():
        d.limb("skin", "M-2 -46 L-2 -8 M4 -46 L4 -8", 7)
        d.shape("suit", rrect(-7, -10, 15, 13, 4), spot=True)
        d.limb("skin", "M1 2 L1 28", 13)
        d.limb("skin", "M-3 30 L-1 52 M5 30 L3 52", 5)
        d.shape("skin", circle(1, 36, 7))
        d.shape("hero", "M-6 38 A7 7 0 0 0 8 38 Z", shadow=False)
    group(d, "translate(128 70) rotate(-24)", diver)
    d.shape("light", splash(146, 128, 0.7), shadow=False)
    ripples(d, 146, 132, 16, 4)


# ================================================================ LAGOON SWIM
def lagoon_cliffs(d: Drawing):
    d.disc("glow", 104, 46, 12)
    d.band("far", "M-30 110 H230")
    d.shape("near", "M-30 -30 H44 Q60 10 50 40 Q66 70 56 100 Q70 130 80 140 H-30Z")
    d.shape("jungle", "M-30 -30 H50 Q60 -6 54 10 Q40 16 30 8 Q16 18 -30 10Z", shadow=False)
    d.shape("jungle", "M48 40 Q60 36 62 46 Q54 50 46 46Z M54 96 Q66 92 70 102 Q60 106 52 102Z", shadow=False)
    d.shape("deep", "M230 -30 H150 Q136 20 150 50 Q132 80 146 108 Q130 128 120 140 H230Z")
    d.shape("jungle", "M230 -30 H150 Q140 -6 146 12 Q160 18 170 10 Q186 20 230 12Z M140 72 Q150 66 156 74 Q148 80 138 78Z", shadow=False)
    d.band("lagoon", "M-30 132 Q100 126 230 132")
    d.band("lagoon2", waves(160, 3, 26))
    d.stroke("light", "M40 150 Q50 146 60 150 M130 176 Q140 172 150 176", 2, line=False)
    def swimmer():
        ripples(d, 0, 8, 14, 4)
        d.limb("skin", "M-8 6 L-20 -8 M8 6 L20 -8", 4.5)
        d.shape("skin", circle(0, 0, 7.5))
        d.shape("pop", "M-7.5 -1 A7.5 7.5 0 0 1 7.5 -1Z", shadow=False, spot=True)
    group(d, "translate(102 146) scale(1.5)", swimmer)
    d.shape("hero2", "M168 126 L190 126 L186 132 H172Z")
    d.stroke("dark", "M179 126 V112", 1.4)
    d.shape("light", "M180 112 L188 124 H180Z", shadow=False)


def lagoon_stingray(d: Drawing):
    d.band("shallow", "M-30 -30 H230", shadow=False, line=False)
    d.stroke("shallow2", "M-30 40 Q20 30 60 42 T140 40 T230 38 M-30 80 Q30 70 70 82 T150 80 T230 78 "
                         "M-30 150 Q20 140 60 152 T140 150 T230 148 M-30 190 Q20 182 60 192 T140 190 T230 188", 2.6, line=False)
    ray = "M100 52 C112 60 140 76 160 104 C140 112 118 122 104 130 Q100 134 96 130 C82 122 60 112 40 104 C60 76 88 60 100 52Z"
    d.shape("shade", ray, shadow=False, line=False, extra='opacity=".35" transform="translate(10 16)"')
    d.stroke("shade", "M100 132 Q104 160 98 196", 3, line=False)
    d.stroke("ray", "M100 128 Q106 158 98 194", 2.6)
    d.shape("ray", ray, spot=True)
    d.shape("ray2", "M100 60 C110 68 130 82 146 102 C130 106 116 112 104 118 Q100 120 96 118 C84 112 70 106 54 102 C70 82 90 68 100 60Z",
            shadow=False, line=False)
    d.marks("dark", circle(92, 76, 2.4) + circle(108, 76, 2.4))
    d.stroke("ray", "M96 116 Q100 112 104 116", 1.2, line=False)
    d.shape("hero2", fish(46, 160, 0.8), shadow=False)
    d.shape("hero2", fish(62, 172, 0.7), shadow=False)
    d.shape("pop", fish(152, 40, 0.9, right=True), shadow=False)
    d.shape("pop", fish(166, 50, 0.7, right=True), shadow=False)


def lagoon_float(d: Drawing):
    d.band("shallow", "M-30 -30 H230", shadow=False, line=False)
    d.stroke("shallow2", "M-30 40 Q20 30 60 42 T140 40 T230 38 M-30 80 Q30 70 70 82 T150 80 T230 78 "
                         "M-30 120 Q30 110 70 122 T150 120 T230 118 M-30 160 Q20 150 60 162 T140 160 T230 158", 2.6, line=False)
    d.raw('<g opacity=".3" transform="translate(116 118) rotate(-20)">', "")
    if d.paper:
        dd = Drawing("papercut", {**d.c, "pop": d.c["shade"], "skin": d.c["shade"], "hair": d.c["shade"]})
        person_top(dd, "pop")
        d.parts.append("".join(p.replace(' filter="url(#ps)"', "").replace(' filter="url(#psl)"', "") for p in dd.parts))
    d.raw("</g>", "")
    group(d, "translate(92 92) rotate(-20) scale(1.1)", lambda: person_top(d, "pop"))
    d.shape("hero2", fish(150, 150, 0.9, right=True), shadow=False)
    d.shape("hero2", fish(140, 166, 0.7, right=True), shadow=False)


# ================================================================ concepts
PINK = {"flam": "#F48FB1", "flam2": "#F9C6D3"}
POOL = {"pool": "#5CC8DA", "pool2": "#3FAFC6", "steel": "#8E9BA6"}
TEAL = {"teal": "#4FBFC0"}
SHALLOW = {"shallow": "#9FE3D8", "shallow2": "#83D3C8", "shade": "#3E8F8A"}

CONCEPTS = [
    # freediving
    Concept("freedive-descent", "freediving", "Into the blue", freedive_descent, UNDERWATER, ov(),
            checks=[("dark", "mid"), ("dark", "near"), ("hero", "far"), ("hero", "mid")], fixes={"hero": ["pop", "hero2", "light"]}),
    Concept("freedive-buoy", "freediving", "Buoy & dive line", freedive_buoy, SEA, ov(),
            checks=[("hero2", "sky"), ("hero2", "mid"), ("pop", "sky"), ("dark", "near")], fixes={"hero2": ["glow2", "pop", "hero"]}),
    Concept("freedive-manta", "freediving", "Manta ray", freedive_manta, UNDERWATER, ov(manta="#2E3A48", manta2="#56677A"),
            checks=[("manta", "mid"), ("manta", "near"), ("dark", "far")], fixes={"manta": ["#4A5868", "#26303B"]}),
    # canyoning
    Concept("canyon-abseil", "canyoning", "Abseiling the falls", clipped(canyon_abseil), ALL, ov(**TEAL),
            checks=[("dark", "far"), ("dark", "sky"), ("near", "sky"), ("light", "near")], fixes={"near": ["deep", "mid"]}),
    Concept("canyon-gear", "canyoning", "Helmet & rope", clipped(canyon_gear), ALL, ov(**TEAL),
            checks=[("hero", "ground"), ("pop", "ground"), ("hero", "near"), ("light", "near"), ("light", "deep")],
            fixes={"hero": ["pop", "deep"], "pop": ["hero", "deep"], "near": ["mid", "deep"]}),
    Concept("canyon-slide", "canyoning", "Rock slide", clipped(canyon_slide), ALL, ov(**TEAL),
            checks=[("hero", "mid"), ("light", "mid"), ("near", "far"), ("deep", "far")], fixes={"hero": ["pop", "deep"], "far": ["sky2", "light"]}),
    # wild swimming
    Concept("wildswim-lake", "wild-swimming", "Mountain lake", wildswim_lake, SEA, ov(),
            checks=[("pop", "near"), ("hero", "near"), ("skin", "near"), ("mid", "sky"), ("dark", "near")],
            fixes={"hero": ["pop", "light"], "pop": ["hero2", "glow2"]}),
    Concept("wildswim-jetty", "wild-swimming", "Jetty dip", wildswim_jetty, SEA, ov(),
            checks=[("hero", "near"), ("wood2", "near"), ("deep", "far"), ("skin", "near"), ("deep", "near")],
            fixes={"hero": ["pop", "light"], "wood2": ["#E3B27A", "wood"]}),
    Concept("wildswim-icedip", "wild-swimming", "Ice dip", wildswim_icedip, SEA, ov(),
            checks=[("light", "near"), ("light", "sky"), ("pop", "near"), ("skin", "near")], fixes={"sky": ["sky2", "far"], "pop": ["hero", "deep"]}),
    # deep-sea fishing
    Concept("deepsea-marlin", "deep-sea-fishing", "Blue marlin", deepsea_marlin, SEA,
            ov(marlin="#2C5F8E", marlin2="#1E3F66", marlin3="#8FC1E8"),
            checks=[("marlin", "sky"), ("marlin", "glow"), ("marlin", "far")], fixes={"glow": ["glow2", "light"]}),
    Concept("deepsea-reel", "deep-sea-fishing", "Big-game reel", deepsea_reel, SEA, ov(),
            checks=[("hero2", "far"), ("hero2", "mid"), ("dark", "sky"), ("dark", "mid")], fixes={"hero2": ["pop", "hero"]}),
    Concept("deepsea-boat", "deep-sea-fishing", "Sportfishing boat", deepsea_boat, SEA, ov(),
            checks=[("hero", "mid"), ("hero", "far"), ("hero2", "sky"), ("dark", "sky")], fixes={"hero": ["pop", "deep"], "hero2": ["light", "glow2"]}),
    # glass-bottom boat
    Concept("glassboat-window", "glass-bottom-boat", "Window to the reef", glassboat_window, UNDERWATER + ["blush"], ov(),
            checks=[("hero2", "mid"), ("hero", "mid"), ("pop", "near")], fixes={"hero2": ["light", "glow2"], "pop": ["hero", "deep"]}),
    Concept("glassboat-section", "glass-bottom-boat", "Glass-bottom boat", glassboat_section, SEA, ov(),
            checks=[("hero", "mid"), ("hero", "far"), ("hero2", "sky"), ("hero2", "near")], fixes={"hero": ["pop", "deep"], "hero2": ["glow2", "pop", "deep"]}),
    Concept("glassboat-below", "glass-bottom-boat", "Faces at the glass", glassboat_below, UNDERWATER, ov(),
            checks=[("hero", "far"), ("hero2", "mid"), ("hero2", "near")], fixes={"hero": ["pop", "deep"], "hero2": ["glow2", "light"]}),
    # banana boat
    Concept("banana-ride", "banana-boat", "Banana ride", banana_ride, SEA, ov(banana="#FFD43B", banana2="#E9AE12"),
            checks=[("banana", "mid"), ("banana", "far"), ("pop", "sky"), ("hero", "banana")], fixes={"hero": ["pop", "deep"]}),
    Concept("banana-aerial", "banana-boat", "Towed from above", banana_aerial, SEA, ov(banana="#FFD43B", banana2="#E9AE12"),
            checks=[("banana", "mid"), ("light", "mid"), ("hero", "banana")], fixes={"hero": ["pop", "deep"]}),
    Concept("banana-wipeout", "banana-boat", "Wipeout", banana_wipeout, SEA, ov(banana="#FFD43B", banana2="#E9AE12"),
            checks=[("banana", "mid"), ("banana", "far"), ("pop", "near"), ("hero", "near")], fixes={"hero": ["pop", "light"], "pop": ["hero2", "light"]}),
    # sunbathing
    Concept("sunbathe-lounger", "sunbathing", "On the lounger", sunbathe_lounger, SEA, ov(suit="#E4572E"),
            checks=[("hero2", "ground"), ("skin", "far"), ("skin", "hero2"), ("glow2", "ground"), ("suit", "skin"), ("suit", "far")],
            fixes={"far": ["near", "deep"], "hero2": ["hero", "pop", "deep"], "glow2": ["hero2", "pop", "near"], "suit": ["#2E86AB", "#1D3557"]}),
    Concept("sunbathe-lotion", "sunbathing", "Sun cream", sunbathe_lotion, ALL, ov(),
            checks=[("hero", "ground"), ("hero", "hero2"), ("hero", "sky"), ("hero2", "ground")], fixes={"hero2": ["pop", "far", "mid"], "hero": ["deep", "pop"]}),
    Concept("sunbathe-sun", "sunbathing", "Sun in shades", sunbathe_sun, ALL,
            checks=[("glow", "sky"), ("glow2", "sky"), ("glow", "glow2")], fixes={"glow2": ["hero2", "pop", "light"], "sky": ["sky2", "far", "deep"]}),
    # river tubing
    Concept("tubing-float", "river-tubing", "Lazy float", tubing_float, ALL, ov(tube="#30343A", **TEAL),
            checks=[("tube", "teal"), ("skin", "teal"), ("pop", "skin")], fixes={"pop": ["hero", "deep", "mark"]}),
    Concept("tubing-karst", "river-tubing", "Karst river", tubing_karst, ALL, ov(jungle="#5E9C5A", **TEAL),
            checks=[("far", "sky"), ("mid", "far"), ("hero", "teal"), ("pop", "teal"), ("hero2", "teal")],
            fixes={"far": ["mid", "near"], "mid": ["near", "deep"], "hero2": ["light", "glow2"], "hero": ["pop", "deep"]}),
    Concept("tubing-train", "river-tubing", "Tube train", tubing_train, ALL, ov(**TEAL),
            checks=[("hero", "teal"), ("pop", "teal"), ("hero2", "teal"), ("near", "teal")], fixes={"hero2": ["light", "glow2"], "hero": ["pop", "deep"]}),
    # pool day
    Concept("pool-ladder", "pool-day", "Pool ladder", pool_ladder, ALL, ov(**POOL),
            checks=[("pop", "pool"), ("ground", "light"), ("steel", "pool")], fixes={"ground": ["far", "mid"]}),
    Concept("pool-flamingo", "pool-day", "Flamingo float", pool_flamingo, ALL, ov(**POOL, **PINK),
            checks=[("flam", "sky"), ("flam", "pool"), ("dark", "sky")]),
    Concept("pool-dive", "pool-day", "Off the board", pool_dive, ALL, ov(suit="#E4572E", **POOL),
            checks=[("skin", "sky"), ("hero2", "sky"), ("suit", "skin"), ("ground", "sky")],
            fixes={"hero2": ["hero", "pop", "deep"], "suit": ["#2E86AB"], "ground": ["far", "mid"]}),
    # lagoon swim
    Concept("lagoon-cliffs", "lagoon-swim", "Hidden lagoon", clipped(lagoon_cliffs), SEA,
            ov(lagoon="#5ED0C8", lagoon2="#36B0B0", jungle="#5E9C5A"),
            checks=[("near", "sky"), ("deep", "sky"), ("near", "lagoon"), ("deep", "lagoon")], fixes={"near": ["deep", "mid"]}),
    Concept("lagoon-stingray", "lagoon-swim", "Stingray shallows", lagoon_stingray, SEA, ov(ray="#7E8C99", ray2="#93A1AD", **SHALLOW),
            checks=[("ray", "shallow"), ("hero2", "shallow"), ("pop", "shallow")], fixes={"hero2": ["pop", "hero", "deep"]}),
    Concept("lagoon-float", "lagoon-swim", "Clear-water float", lagoon_float, SEA, ov(**SHALLOW),
            checks=[("pop", "shallow"), ("skin", "shallow"), ("hero2", "shallow")], fixes={"hero2": ["pop", "hero", "deep"], "pop": ["hero", "deep"]}),
]
