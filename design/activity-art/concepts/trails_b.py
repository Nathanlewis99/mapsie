"""Trails B: horse riding, camel trek, off-road 4x4, road trip, camping, glamping,
stargazing, volcano hike, glacier hike, rainforest trek. Three concepts each."""
import math

from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group


def _poly(pts):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"


def _ring_blocks(cx, cy, r0, r1, n, frac=0.55, phase=0.0):
    """Tread blocks / sun rays: n trapezoids between radius r0 and r1."""
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n + phase
        w = math.pi / n * frac
        out.append(_poly([(cx + r0 * math.cos(a - w), cy + r0 * math.sin(a - w)),
                          (cx + r1 * math.cos(a - w * .8), cy + r1 * math.sin(a - w * .8)),
                          (cx + r1 * math.cos(a + w * .8), cy + r1 * math.sin(a + w * .8)),
                          (cx + r0 * math.cos(a + w), cy + r0 * math.sin(a + w))]))
    return " ".join(out)


def _pine(x, base, h, w):
    """A layered pine tree: tip at (x, base-h)."""
    t = base - h
    return (f"M{x} {t} L{x + w * .55} {t + h * .38} L{x + w * .3} {t + h * .36} L{x + w * .8} {t + h * .7} "
            f"L{x + w * .4} {t + h * .68} L{x + w} {base} L{x - w} {base} L{x - w * .4} {t + h * .68} "
            f"L{x - w * .8} {t + h * .7} L{x - w * .3} {t + h * .36} L{x - w * .55} {t + h * .38}Z")


def _stars(d, pts, role="light"):
    for x, y, r in pts:
        d.marks(role, f"M{x} {y - r} L{x + r * .3} {y - r * .3} L{x + r} {y} L{x + r * .3} {y + r * .3} "
                      f"L{x} {y + r} L{x - r * .3} {y + r * .3} L{x - r} {y} L{x - r * .3} {y - r * .3}Z")


# ================================================================ HORSE RIDING
# Side-on horse facing right; hooves at y 172.
HORSE = ("M116 94 C126 80 136 66 145 56 L146 44 L152 53 C158 56 164 62 168 70 L178 84 "
         "C181 89 179 95 173 95 C168 95 164 92 160 90 C154 90 148 86 146 76 "
         "C143 88 142 104 144 114 C145 124 140 132 132 134 C116 138 92 138 76 134 "
         "C64 132 55 124 54 112 C53 100 60 93 72 92 C86 91 100 96 108 96 C112 96 114 95 116 94Z")
HORSE_MANE = "M112 96 C120 82 132 66 141 56 L147 52 C142 68 134 84 124 98Z"
HORSE_FAR_LEGS = "M124 128 L120 150 L123 171 M86 126 L90 142 L84 157 L85 171"
HORSE_NEAR_LEGS = "M136 126 L138 150 L137 171 M66 118 L72 140 L65 157 L66 171"
HORSE_HOOVES = "M132 169 h10 v5 h-10Z M61 169 h10 v5 h-10Z M118 169 h10 v5 h-10Z M77 169 h10 v5 h-10Z"


def horse(d: Drawing, body="hero", far="hero2", mane="mark", saddle=True):
    d.limb(mane, "M56 102 C42 108 40 130 46 150", 8)
    d.limb(far, HORSE_FAR_LEGS, 8)
    d.limb(body, HORSE_NEAR_LEGS, 9)
    d.marks(mane, HORSE_HOOVES)
    d.shape(body, HORSE)
    d.shape(mane, HORSE_MANE, shadow=False)
    d.shape(mane, "M147 52 C152 55 155 62 152 67 C148 63 145 59 144 56Z", shadow=False)
    d.marks(mane, circle(158, 68, 2.3))
    d.marks(mane, ellipse(173, 88, 1.7, 1.3))
    if saddle:
        d.shape("pop", "M86 96 H114 L112 116 H88Z", shadow=False, spot=True)
        d.shape("dark", "M86 97 C92 93 98 96 104 97 C108 97 111 93 112 87 L117 88 C117 97 114 105 106 107 H91 C87 105 85 101 86 97Z")
        d.stroke("dark", "M100 106 V124", 1.8)
        d.shape("dark", rrect(95.5, 123, 9, 5, 2), shadow=False)


def horse_meadow(d: Drawing):
    d.disc("glow", 50, 60, 20)
    d.shape("light", cloud(70, 34, 0.8))
    d.band("far", hills(120, 12))
    d.band("mid", hills(140, 10, 30))
    d.limb("dark", "M14 170 V132 M40 170 V136 M2 144 Q27 138 52 146 M2 156 Q27 150 52 158", 4)
    horse(d)
    d.band("ground", hills(170, 4, 20))
    d.band("near", hills(186, 4, -20), line=False)


HORSE_HEAD = ("M34 200 C40 150 58 94 86 50 L84 28 L97 42 C104 38 112 40 118 47 C134 64 150 90 162 106 "
              "C168 116 166 128 154 131 C144 133 134 128 126 124 C120 136 98 138 94 120 "
              "C92 142 98 170 104 200Z")


def horse_head(d: Drawing):
    d.disc("glow", 128, 76, 40)
    d.band("far", hills(150, 10))
    d.band("mid", hills(172, 8, 30))
    d.shape("mark", "M86 46 C62 84 44 140 32 200 L14 200 C26 140 50 84 82 40Z", spot=True)
    d.shape("hero", HORSE_HEAD)
    d.shape("mark", "M84 30 L97 42 L92 46Z", shadow=False)
    d.shape("light", "M108 50 C122 68 140 92 152 108 L147 114 C134 98 118 74 103 56Z", shadow=False)
    d.shape("mark", "M98 40 C108 44 112 54 108 62 C104 54 98 48 92 46Z", shadow=False)
    d.limb("pop", "M96 46 L112 52 M98 50 L118 100 M130 82 L114 112 M126 124 C136 112 144 102 148 92", 4, shadow=False, spot=True)
    d.shape("hero2", circle(118, 100, 4.5), shadow=False)
    d.marks("mark", ellipse(116, 70, 4, 4.4))
    d.marks("light", circle(117.5, 68.5, 1.3))
    d.stroke("mark", "M110 64 Q116 60 122 64", 1.6)
    d.marks("mark", ellipse(152, 116, 2.6, 3.6))
    d.stroke("mark", "M140 128 Q148 132 156 129", 1.4)


def horse_canyon(d: Drawing):
    d.disc("glow", 140, 66, 26)
    d.band("far", "M-30 120 H18 L24 92 H62 L68 120 H120 L126 100 H170 L176 120 H230")
    d.band("mid", "M-30 146 H40 L46 126 H84 L90 146 H230")

    def rider():
        horse(d, "dark", "dark", "dark", saddle=False)
        d.limb("dark", "M100 98 L98 70 M98 78 L120 90", 8)
        d.limb("dark", "M98 100 L104 116 L100 126", 7)
        d.shape("dark", circle(98, 58, 7))
        d.shape("dark", "M84 54 Q98 50 112 54 L108 50 Q106 40 98 40 Q90 40 88 50Z")
    group(d, "translate(22 34) scale(.68)", rider)
    d.limb("dark", "M168 160 V112 M168 140 Q156 140 156 126 M168 132 Q180 132 180 118", 7)
    d.band("ground", "M-30 156 Q80 146 230 160")
    d.band("near", hills(182, 5), line=False)


# ================================================================ CAMEL TREK
# Dromedary facing right, hooves at y 172.
CAMEL = ("M50 104 C52 92 64 72 84 70 C100 68 110 84 118 96 C124 102 132 104 138 100 C146 94 148 82 150 74 "
         "C151 66 156 62 162 62 L164 56 L168 62 C173 63 178 66 182 72 C185 77 182 81 178 81 "
         "C172 81 166 79 163 81 C159 90 156 104 150 112 C146 118 138 122 132 122 "
         "C112 126 80 126 64 122 C54 120 48 114 50 104Z")
CAMEL_FAR_LEGS = "M118 118 L114 146 L116 171 M76 118 L80 146 L76 171"
CAMEL_NEAR_LEGS = "M128 116 L131 146 L129 171 M60 114 L60 146 L64 171"


def camel(d: Drawing, body="hero", far="hero2", mark="mark", blanket=True):
    d.stroke(mark, "M50 106 C44 114 44 124 46 132", 2.4)
    d.limb(far, CAMEL_FAR_LEGS, 6)
    d.limb(body, CAMEL_NEAR_LEGS, 6.5)
    d.shape(body, CAMEL)
    d.marks(mark, circle(168, 69, 1.9))
    d.stroke(mark, "M178 78 L182 76", 1.3)
    if blanket:
        d.shape("pop", "M64 92 C70 80 78 74 86 74 C96 74 104 82 110 92 L111 114 H64Z", shadow=False, spot=True)
        d.shape("hero2", "M64 104 H111 V108.5 H64Z", shadow=False)
        d.marks("pop", " ".join(f"M{x} 113 l2.5 7 l2.5 -7Z" for x in range(64, 108, 7)))
        d.shape("dark", "M74 78 C78 66 94 66 98 78 Q86 73 74 78Z", shadow=False)


def camel_dunes(d: Drawing):
    d.disc("glow", 56, 62, 22)
    d.band("far", "M-30 134 Q30 100 80 118 Q130 136 180 104 Q210 92 230 100")
    d.band("mid", "M-30 156 Q40 132 110 148 Q170 160 230 140")
    camel(d)
    d.band("ground", "M-30 170 Q60 162 120 170 T230 168")


def camel_caravan(d: Drawing):
    d.disc("glow", 100, 96, 46)
    d.band("far", "M-30 132 Q40 112 100 124 T230 118")
    ridge = lambda x: 152 - (x + 30) * 34 / 260
    for x in (54, 100, 146):
        group(d, f"translate({x - 48:.1f} {ridge(x) - 72 + 2:.1f}) scale(.42)", lambda: _caravan_camel(d))
    d.band("mid", "M-30 152 Q100 136 230 118")
    d.band("near", "M-30 176 Q60 160 130 172 T230 162", line=False)


def _caravan_camel(d):
    camel(d, "dark", "dark", "dark", blanket=False)
    d.shape("dark", rrect(76, 34, 14, 36, 6))
    d.shape("dark", circle(83, 28, 8))
    d.shape("pop", "M74 22 Q83 12 92 22 L92 26 H74Z", shadow=False, spot=True)


CAMEL_HEAD = ("M26 200 C32 150 52 96 90 60 L86 48 L97 54 C104 46 120 44 132 51 C146 59 158 69 166 77 "
              "C173 84 175 93 170 97 L167 99 C169 104 166 109 160 109 C158 117 148 120 141 113 "
              "C132 110 120 108 112 112 C102 120 96 150 94 200Z")


def camel_head(d: Drawing):
    d.disc("glow", 52, 70, 22)
    d.band("far", "M-30 150 Q40 126 100 140 T230 132")
    d.band("mid", "M-30 176 Q60 156 120 168 T230 160")
    d.shape("hero", CAMEL_HEAD)
    d.shape("hero2", "M141 113 C148 120 158 117 160 109 C154 112 146 112 141 113Z", shadow=False)
    d.limb("pop", "M100 58 L124 104 M148 64 C142 80 140 98 142 112 M112 80 L146 86", 4.5, shadow=False, spot=True)
    for x, y in [(112, 80), (146, 86), (124, 104)]:
        d.shape("hero2", circle(x, y, 4.4), shadow=False)
    for i, (x, y) in enumerate([(118, 110), (126, 114), (134, 116)]):
        d.shape(["pop", "hero2", "light"][i], f"M{x} {y} C{x + 4} {y + 4} {x + 4} {y + 14} {x} {y + 18} C{x - 4} {y + 14} {x - 4} {y + 4} {x} {y}Z", shadow=False)
    d.shape("hero2", "M110 66 C114 58 130 58 134 66 C128 63 116 63 110 66Z", shadow=False)
    d.marks("mark", ellipse(122, 69, 4.2, 2.8))
    d.stroke("mark", "M112 69 Q122 74 132 69 M114 72 L111 76 M120 74 L119 78 M126 74 L127 78", 1.6)
    d.stroke("mark", "M162 82 Q168 84 168 90", 1.8)
    d.stroke("mark", "M167 99 Q162 101 158 100", 1.4)


# ================================================================ OFF-ROAD 4x4
TRUCK = "M40 138 V84 Q40 78 46 78 H116 L121 104 H158 Q163 104 163 109 V138Z"


def truck(d: Drawing):
    d.shape("dark", rrect(30, 100, 12, 30, 5))
    d.shape("hero", TRUCK)
    d.shape("light", rrect(47, 84, 26, 15, 2), shadow=False)
    d.shape("light", "M79 84 H113 L116 99 H79Z", shadow=False)
    d.stroke("mark", "M76 82 V136 M83 112 H90", 1.6)
    d.shape("light", "M120 108 H162", shadow=False)
    d.shape("hero2", "M40 112 H163 V116 H40Z", shadow=False, spot=True)
    d.limb("dark", "M126 128 V72 L133 70", 4.5)
    d.stroke("dark", "M52 78 V72 M80 78 V72 M108 78 V72", 2)
    d.shape("hero2", rrect(44, 68, 72, 5, 2), spot=True)
    d.shape("pop", rrect(54, 55, 15, 13, 2))
    d.shape("pop", rrect(72, 55, 15, 13, 2))
    d.shape("glow2", circle(158, 111, 3.2), shadow=False)
    d.shape("dark", rrect(156, 128, 12, 7, 2))
    for x in (66, 138):
        d.shape("dark", f"M{x - 21} 138 A21 21 0 0 1 {x + 21} 138Z", shadow=False)
        d.shape("dark", circle(x, 140, 16))
        d.shape("light", circle(x, 140, 6), shadow=False)


def offroad_river(d: Drawing):
    d.disc("glow", 160, 52, 18)
    d.band("far", "M-30 112 L10 82 L36 104 L66 70 L100 108 L132 84 L160 104 L230 92")
    for x, h in [(20, 34), (176, 30), (192, 22)]:
        d.shape("deep", _pine(x, 126, h, 10))
    d.band("mid", "M-30 126 Q100 118 230 126")
    d.band("near", waves(136, 3, 24))
    truck(d)
    d.band("mid", waves(150, 4, 22))
    d.shape("light", "M152 150 C152 138 162 128 172 126 C168 134 174 138 184 132 C182 144 174 150 162 152Z", shadow=False)
    d.shape("light", "M42 150 C40 142 34 138 26 140 C30 146 28 150 22 150Z", shadow=False)
    d.stroke("light", "M60 162 H90 M110 166 H150 M30 172 H54", 2.4)
    d.band("near", waves(182, 3, 26), line=False)


PICKUP = "M38 140 V108 H94 V90 Q94 84 100 84 H124 L134 106 H160 Q166 106 166 112 V140Z"


def offroad_dune(d: Drawing):
    d.disc("glow", 52, 54, 20)
    d.band("far", "M-30 124 Q40 96 100 116 T230 104")

    def car():
        d.stroke("dark", "M54 108 V92 Q54 88 58 88 H84 Q88 88 88 92 V108", 3.2)
        d.shape("hero", PICKUP)
        d.shape("light", "M102 90 H122 L129 106 H102Z", shadow=False)
        d.shape("hero2", "M38 118 H166 V123 H38Z", shadow=False, spot=True)
        d.shape("hero2", rrect(98, 78, 28, 5, 2), spot=True)
        d.shape("glow2", circle(161, 113, 3), shadow=False)
        d.shape("dark", rrect(162, 128, 8, 8, 2))
        for x in (64, 140):
            d.shape("dark", circle(x, 142, 16))
            d.shape("light", circle(x, 142, 6), shadow=False)
    group(d, "rotate(-14 100 120) translate(0 2)", car)
    for x, y, s in [(26, 150, 1.2), (14, 136, 0.8), (36, 128, 0.6)]:
        d.shape("ground", circle(x, y, 6 * s), line=False)
    d.band("ground", "M-30 168 Q60 166 120 136 Q160 116 230 112")
    d.band("mid", "M-30 186 Q80 170 230 176", line=False)


def offroad_front(d: Drawing):
    d.disc("glow", 152, 46, 16)
    d.band("far", hills(108, 10))
    d.band("mid", "M-30 132 Q40 120 80 126 L100 120 L120 126 Q160 120 230 132")
    # tyres (front-on)
    for x in (34, 142):
        d.shape("dark", rrect(x, 112, 24, 50, 8))
        d.stroke("mark", " ".join(f"M{x + 3} {y} H{x + 21}" for y in range(120, 158, 7)), 2.2, line=False)
    d.shape("light", "M64 86 L72 52 H128 L136 86Z", spot=False)
    d.shape("sky2", "M70 82 L76 57 H124 L130 82Z", shadow=False)
    d.stroke("light", "M84 78 L96 60 M96 78 L104 66", 3, line=False)
    d.limb("dark", "M146 140 V48 H138", 5)
    d.shape("hero2", rrect(66, 44, 68, 6, 2), spot=True)
    for x in (76, 92, 108, 124):
        d.shape("glow2", circle(x, 41, 4), shadow=False)
    d.shape("hero", "M42 96 Q42 86 52 86 H148 Q158 86 158 96 V136 H42Z")
    d.shape("dark", rrect(30, 80, 10, 14, 3))
    d.shape("dark", rrect(160, 80, 10, 14, 3))
    d.limb("dark", "M40 88 L58 88 M160 88 L142 88", 3)
    for x in (66, 134):
        d.shape("light", circle(x, 108, 11), shadow=False, spot=True)
        d.shape("glow2", circle(x, 108, 6), shadow=False)
    d.shape("dark", rrect(82, 96, 36, 26, 3), shadow=False)
    d.stroke("hero", " ".join(f"M{x} 99 V119" for x in (89, 96, 104, 111)), 3, line=False)
    d.shape("dark", rrect(34, 132, 132, 14, 4))
    d.shape("light", rrect(86, 135, 28, 8, 2), shadow=False)
    for x, y, r in [(52, 128, 5), (60, 124, 3), (148, 128, 4.5), (120, 100, 3), (70, 140, 3.5)]:
        d.shape("near", circle(x, y, r), shadow=False, line=False)
    d.band("near", "M-30 160 Q20 150 34 156 Q100 170 166 156 Q180 150 230 160")
    for x, y, r in [(22, 146, 6), (12, 132, 4), (178, 142, 6), (188, 128, 4), (30, 128, 3)]:
        d.shape("near", circle(x, y, r))
    d.band("deep", hills(184, 4), line=False)


# ================================================================ ROAD TRIP
BUS = "M36 138 V88 Q36 72 54 72 H138 Q158 72 163 92 L167 120 Q169 138 156 138Z"


def road_campervan(d: Drawing):
    d.disc("glow", 150, 52, 20)
    d.band("far", waves(112, 3, 30))
    d.band("mid", "M-30 124 Q20 112 52 126 Q90 140 230 128")
    d.band("ground", "M-30 146 Q100 140 230 146")

    def bus():
        d.shape("pop", "M48 64 Q100 54 152 64 Q100 72 48 64Z", spot=True)
        d.stroke("dark", "M60 72 V66 M136 72 V66", 2.2)
        d.shape("hero", BUS)
        d.shape("light", "M36 104 V88 Q36 72 54 72 H138 Q158 72 163 92 L165 104Z", shadow=False)
        for x in (44, 70, 96):
            d.shape("sky2", rrect(x, 80, 21, 16, 3), shadow=False)
        d.shape("sky2", "M124 80 H142 Q154 80 157 96 H124Z", shadow=False)
        d.stroke("mark", "M118 106 V134 M110 116 H114", 1.6)
        d.shape("light", "M36 120 H168 V123 H36Z", shadow=False)
        d.shape("glow2", circle(163, 112, 3.5), shadow=False)
        d.stroke("mark", "M42 110 H54 M42 114 H54", 1.4, line=False)
        for x in (64, 140):
            d.shape("dark", circle(x, 138, 13))
            d.shape("light", circle(x, 138, 5.5), shadow=False)
    group(d, "translate(0 6)", bus)
    d.stroke("light", "M-10 166 H30 M60 166 H100 M130 166 H170 M200 166 H230", 3)
    d.band("near", hills(182, 4), line=False)


CAR = ("M26 132 Q26 120 38 118 L34 108 L52 116 H84 Q90 116 92 112 H112 L118 116 H150 Q168 116 172 124 "
       "L175 134 Q175 140 169 140 H32 Q26 140 26 132Z")


def road_convertible(d: Drawing):
    d.disc("glow", 100, 92, 38)
    d.band("far", "M-30 120 Q30 104 70 114 Q120 126 160 108 Q190 98 230 108")
    d.band("ground", "M-30 148 Q100 140 230 148")
    for x, y, h, k in [(168, 146, 74, 1), (30, 146, 60, -1)]:
        top = (x - 10 * k, y - h)
        d.limb("dark", f"M{x} {y} Q{x + 2 * k} {y - h * .5} {top[0]} {top[1]}", 4.5)
        tx, ty = top
        d.shape("dark", f"M{tx} {ty} Q{tx - 14} {ty - 12} {tx - 30} {ty + 2} Q{tx - 14} {ty - 4} {tx} {ty}Z "
                        f"M{tx} {ty} Q{tx + 14} {ty - 12} {tx + 30} {ty + 2} Q{tx + 14} {ty - 4} {tx} {ty}Z "
                        f"M{tx} {ty} Q{tx - 6} {ty - 18} {tx - 22} {ty - 20} Q{tx - 8} {ty - 10} {tx} {ty}Z "
                        f"M{tx} {ty} Q{tx + 6} {ty - 18} {tx + 22} {ty - 20} Q{tx + 8} {ty - 10} {tx} {ty}Z "
                        f"M{tx} {ty} Q{tx - 10} {ty + 6} {tx - 18} {ty + 18} Q{tx - 6} {ty + 8} {tx} {ty}Z "
                        f"M{tx} {ty} Q{tx + 10} {ty + 6} {tx + 18} {ty + 18} Q{tx + 6} {ty + 8} {tx} {ty}Z")

    def car():
        d.shape("dark", rrect(62, 104, 12, 16, 4))
        d.shape("dark", rrect(84, 104, 12, 16, 4))
        d.shape("light", "M110 116 L104 98 L108 97 L116 116Z", spot=True)
        d.stroke("dark", "M100 108 L106 118", 2.4)
        d.shape("hero", CAR)
        d.shape("light", "M30 126 H172 V129 H30Z", shadow=False)
        d.stroke("mark", "M96 118 V138", 1.6)
        d.shape("glow2", rrect(166, 120, 6, 5, 2), shadow=False)
        d.shape("pop", rrect(26, 120, 5, 6, 2), shadow=False)
        d.shape("light", rrect(22, 132, 14, 4, 2), shadow=False)
        d.shape("light", rrect(164, 132, 16, 4, 2), shadow=False)
        for x in (56, 146):
            d.shape("dark", circle(x, 140, 12))
            d.shape("light", circle(x, 140, 7.5), shadow=False)
            d.shape("dark", circle(x, 140, 4.5), shadow=False)
    group(d, "translate(0 -2) scale(1.0)", car)
    d.stroke("light", "M-10 168 H30 M60 168 H100 M130 168 H170 M200 168 H230", 3)
    d.band("near", hills(184, 4), line=False)


def _road(y0=112, y1=188, x0=112, x1=94, sway=22, w0=2, w1=84, n=24):
    """A perspective road from the horizon (y0) to the bottom: polygon + centre-line dashes."""
    cl = []
    for i in range(n + 1):
        t = i / n
        y = y0 + (y1 - y0) * t ** 1.3
        x = x0 + (x1 - x0) * t + sway * math.sin(t * math.pi * 1.5)
        cl.append((x, y, w0 + (w1 - w0) * t ** 1.6))
    left = [(x - w / 2, y) for x, y, w in cl]
    right = [(x + w / 2, y) for x, y, w in reversed(cl)]
    dashes = " ".join(f"M{cl[i][0]:.1f} {cl[i][1]:.1f} L{cl[i + 1][0]:.1f} {cl[i + 1][1]:.1f}" for i in range(4, n, 3))
    return _poly(left + right), dashes, cl


def road_winding(d: Drawing):
    d.disc("glow", 140, 62, 18)
    d.band("far", "M-30 104 L16 76 L44 96 L78 60 L112 98 L140 82 L170 100 L196 80 L230 104")
    for snow in ["M78 60 L89 72 L83 71 L78 76 L72 70 L68 72Z", "M196 80 L203 88 L198 87 L194 91 L190 86Z"]:
        d.shape("light", snow, shadow=False)
    d.band("mid", hills(118, 8, 10))
    d.band("near", hills(136, 6, -20))
    road, dashes, cl = _road()
    d.shape("dark", road)
    d.stroke("light", dashes, 2.6)
    d.limb("dark", "M168 178 V138", 3.5, shadow=False)
    d.shape("hero2", "M168 118 L180 130 L168 142 L156 130Z", spot=True)
    d.stroke("dark", "M164 135 Q168 124 172 128 Q174 130 170 132", 1.8)
    for x, h, b in [(22, 34, 166), (38, 24, 160), (186, 24, 150)]:
        d.shape("deep", _pine(x, b, h, 9))
    d.band("deep", "M-30 186 Q100 180 230 186")


# ================================================================ CAMPING
def campfire(d: Drawing, x, y, s=1.0):
    def draw():
        d.limb("dark", "M-14 6 L14 -2 M-14 -2 L14 6", 5)
        d.shape("pop", "M0 -26 C10 -16 14 -6 10 2 C8 6 -8 6 -10 2 C-14 -6 -8 -14 -4 -16 C-4 -10 -2 -8 0 -8 C2 -14 -2 -20 0 -26Z", spot=True)
        d.shape("glow2", "M0 -12 C5 -6 6 -2 4 2 C2 4 -2 4 -4 2 C-6 -2 -4 -6 0 -12Z", shadow=False)
    group(d, f"translate({x} {y}) scale({s})", draw)


def camp_tent(d: Drawing):
    d.disc("glow", 100, 60, 20)
    d.band("far", "M-30 108 L20 74 L52 96 L90 66 L124 98 L156 76 L230 108")
    d.band("mid", hills(130, 8))
    for x, h, b in [(20, 64, 156), (38, 46, 154), (174, 58, 156), (190, 40, 152)]:
        d.shape("deep", _pine(x, b, h, h * .3))
    d.stroke("dark", "M58 152 L44 160 M142 152 L156 160 M100 84 L100 78", 1.6)
    d.shape("hero", "M54 154 L100 82 L146 154Z")
    d.shape("hero2", "M100 82 L118 154 H146Z", shadow=False)
    d.shape("dark", "M100 102 L84 154 H116Z", shadow=False)
    d.shape("light", "M100 100 L86 154 H78Z", shadow=False, spot=True)
    campfire(d, 154, 162, .8)
    d.band("ground", hills(160, 3, 20))
    d.band("near", hills(182, 4), line=False)


def camp_fire(d: Drawing):
    d.disc("glow", 100, 96, 46)
    d.band("far", hills(140, 6))
    d.band("ground", "M-30 152 Q100 146 230 152")
    for x, y, rx in [(52, 158, 12), (72, 166, 12), (100, 170, 13), (128, 166, 12), (148, 158, 12)]:
        d.shape("far", ellipse(x, y, rx, 7))
    d.limb("dark", "M48 150 L150 128 M52 128 L152 150", 11)
    for x, y in [(48, 150), (152, 150)]:
        d.shape("near", circle(x, y, 7), spot=True)
        d.stroke("dark", circle(x, y, 3.5), 1.4)
    d.shape("pop", "M100 46 C122 70 132 92 126 118 C122 136 78 136 74 118 C68 96 80 82 88 72 C88 86 92 92 96 92 C102 76 96 62 100 46Z", spot=True)
    d.shape("glow2", "M100 82 C112 94 116 106 112 120 C108 132 92 132 88 120 C84 108 92 96 100 82Z", shadow=False)
    d.limb("near", "M178 104 L124 82", 2.4, shadow=False)
    d.shape("light", rrect(116, 74, 14, 11, 4), extra='transform="rotate(22 123 79.5)"')
    d.band("near", hills(186, 4), line=False)


def camp_lantern(d: Drawing):
    d.disc("glow", 100, 100, 50)
    d.band("far", hills(150, 8))
    for x, h, b in [(28, 70, 160), (172, 62, 160)]:
        d.shape("deep", _pine(x, b, h, h * .32))
    d.stroke("dark", "M78 62 C78 38 122 38 122 62", 3.2)
    d.shape("hero", "M74 70 L82 60 H118 L126 70Z")
    d.shape("hero", rrect(96, 52, 8, 9, 2))
    d.shape("light", "M80 72 C70 90 70 114 80 132 H120 C130 114 130 90 120 72Z")
    d.shape("glow2", "M90 82 C84 96 84 112 90 124 H110 C116 112 116 96 110 82Z", shadow=False)
    d.shape("pop", "M100 92 C108 102 108 112 104 116 C102 119 98 119 96 116 C92 112 92 102 100 92Z", shadow=False, spot=True)
    d.stroke("dark", "M86 72 C78 92 78 112 86 132 M114 72 C122 92 122 112 114 132", 2.2)
    d.shape("hero", rrect(72, 130, 56, 8, 3))
    d.shape("hero", "M76 138 H124 L120 152 H80Z")
    d.shape("hero2", rrect(116, 140, 6, 6, 2), shadow=False)
    d.band("ground", "M-30 152 Q100 148 230 152")
    d.band("near", hills(180, 4), line=False)


# ================================================================ GLAMPING
def glamp_bell(d: Drawing):
    d.disc("glow", 46, 60, 16)
    d.band("far", hills(118, 10))
    for x, h, b in [(176, 62, 150), (160, 40, 148), (22, 48, 148)]:
        d.shape("deep", _pine(x, b, h, h * .3))
    d.stroke("dark", "M100 64 V54", 2.4)
    d.shape("pop", "M100 50 L110 54 L100 58Z", shadow=False, spot=True)
    d.shape("hero2", "M40 152 L46 120 L100 64 L154 120 L160 152Z")
    d.shape("ground", "M46 120 L100 64 L154 120 Q100 128 46 120Z", shadow=False)
    d.stroke("hero2", "M46 120 Q100 128 154 120", 2)
    d.shape("dark", "M100 92 L80 152 H120Z", shadow=False)
    d.shape("glow2", "M100 104 L88 152 H112Z", shadow=False)
    d.shape("hero2", "M100 92 L80 152 H72Z", shadow=False)
    d.shape("hero2", "M100 92 L120 152 H128Z", shadow=False)
    d.stroke("dark", "M42 130 Q100 146 158 130", 1.2)
    for i in range(9):
        t = i / 8
        x = 42 + 116 * t
        y = (1 - t) ** 2 * 130 + 2 * (1 - t) * t * 146 + t * t * 130
        if 78 < x < 122:
            continue
        d.shape(["pop", "hero", "light"][i % 3], f"M{x - 4:.1f} {y:.1f} L{x + 4:.1f} {y:.1f} L{x:.1f} {y + 8:.1f}Z", shadow=False, spot=i % 2 == 0)
    d.band("ground", hills(156, 3, 30))
    d.band("near", hills(180, 4), line=False)


def glamp_yurt(d: Drawing):
    d.disc("glow", 150, 54, 18)
    d.band("far", "M-30 112 L14 84 L40 100 L72 70 L104 98 L134 80 L164 100 L230 92")
    d.band("mid", hills(130, 8))
    d.shape("light", "M32 118 H168 V156 H32Z")
    d.stroke("mark", " ".join(f"M{x} 120 L{x + 12} 154 M{x + 12} 120 L{x} 154" for x in range(36, 160, 12)), 1.2, line=False)
    d.shape("light", "M24 120 Q60 82 100 66 Q140 82 176 120Z")
    d.shape("hero", "M24 120 Q60 82 100 66 Q140 82 176 120 Q100 112 24 120Z", shadow=False, spot=False)
    d.stroke("light", "M60 108 L100 70 L140 108 M40 116 L100 70 L160 116", 1.6, line=False)
    d.shape("hero2", ellipse(100, 70, 12, 5))
    d.shape("pop", "M30 134 Q100 140 170 134 V142 Q100 148 30 142Z", shadow=False, spot=True)
    d.shape("pop", rrect(88, 124, 24, 32, 2))
    d.shape("hero2", "M92 128 H108 V152 H92Z", shadow=False)
    d.stroke("pop", "M100 128 V152 M92 140 H108", 1.6)
    d.band("ground", hills(156, 3, 30))
    d.band("near", hills(180, 4), line=False)


def night_sky(d: Drawing, stars):
    d.band("deep", "M-30 -30 L230 -30", shadow=False, line=False)
    _stars(d, stars)


def glamp_dome(d: Drawing):
    night_sky(d, [(40, 52, 3), (62, 34, 2), (150, 40, 2.5), (170, 70, 2), (118, 26, 2), (28, 86, 2)])
    d.disc("glow", 140, 58, 13)
    d.shape("deep", circle(147, 54, 11), shadow=False, line=False)
    d.band("near", hills(124, 10))
    d.shape("light", "M44 150 A56 56 0 0 1 156 150Z")
    d.stroke("far", "M44 150 L72 102 L100 94 L128 102 L156 150 M72 102 L100 150 L128 102 M58 126 L100 150 L142 126 "
                    "M58 126 L72 102 M142 126 L128 102 M100 94 V150 M58 126 L44 150 M142 126 L156 150", 1.6)
    d.shape("glow2", circle(100, 124, 16), shadow=False)
    d.stroke("far", "M84 124 H116 M100 108 V140", 1.6)
    d.shape("hero", "M30 150 H170 V158 H30Z")
    d.stroke("hero", "M40 158 V170 M160 158 V170", 3)
    for x in range(52, 152, 14):
        d.marks("glow2", circle(x, 154 - ((x - 100) / 50) ** 2 * 4, 1.8))
    d.band("mid", hills(170, 3, 20))


# ================================================================ STARGAZING
STARS = [(30, 70, 2.2), (46, 44, 3), (70, 28, 2), (96, 40, 2.4), (120, 22, 2), (150, 34, 3), (176, 58, 2.2),
         (162, 88, 2), (36, 100, 2), (84, 62, 1.8), (132, 64, 1.8)]


def star_telescope(d: Drawing):
    night_sky(d, STARS[:6] + STARS[8:9] + STARS[9:10])
    d.disc("glow", 160, 54, 16)
    d.shape("deep", circle(168, 49, 13), shadow=False, line=False)
    d.band("near", hills(150, 10, 20))
    d.limb("hero2", "M100 110 L70 168 M100 110 L130 168 M100 110 L102 172", 5)

    def scope():
        d.shape("hero", rrect(50, 92, 98, 22, 7), spot=True)
        d.shape("light", rrect(140, 88, 14, 30, 4))
        d.shape("light", "M58 92 H66 V114 H58Z", shadow=False)
        d.shape("light", "M118 92 H124 V114 H118Z", shadow=False)
        d.shape("hero2", rrect(78, 80, 32, 8, 3))
        d.limb("dark", "M50 103 H38", 6)
    group(d, "rotate(-28 100 104)", scope)
    d.shape("dark", circle(100, 110, 7))
    d.band("mid", hills(174, 4, -10))


def star_constellation(d: Drawing):
    night_sky(d, [(30, 96, 1.6), (60, 30, 2), (120, 26, 1.6), (172, 64, 1.8), (160, 120, 1.6), (48, 120, 1.4), (182, 96, 1.4)])
    d.raw('<path d="M-10 160 C40 110 120 80 210 30 L210 70 C130 110 60 140 -10 196Z" fill="#fff" opacity=".12"/>', "")
    dipper = [(30, 62), (54, 54), (76, 60), (96, 72), (102, 96), (136, 100), (144, 74)]
    d.stroke("light", "M" + " L".join(f"{x} {y}" for x, y in dipper) + " L96 72", 1.4)
    _stars(d, [(x, y, 4.2) for x, y in dipper])
    d.stroke("light", "M178 26 L150 44", 1.8)
    _stars(d, [(148, 45, 3.4)])
    d.band("near", "M-30 150 L14 128 L40 142 L76 112 L106 138 L134 122 L164 140 L192 124 L230 146")
    d.band("dark", hills(168, 8, 20))
    d.shape("dark", circle(128, 134, 6))
    d.shape("dark", "M121 142 Q128 138 135 142 L137 170 H119Z")
    d.limb("dark", "M134 145 L146 128", 4, shadow=False)
    d.band("mid", hills(186, 3), line=False)


def star_observatory(d: Drawing):
    night_sky(d, STARS)
    d.disc("glow", 46, 50, 13)
    d.shape("deep", circle(52, 45, 11), shadow=False, line=False)
    d.stroke("light", "M180 30 L150 50", 1.8)
    _stars(d, [(148, 51, 3.4)])
    d.band("far", "M-30 150 Q40 120 100 110 Q150 104 230 140")
    d.shape("light", "M64 116 A36 36 0 0 1 136 116Z")
    d.shape("far", "M94 80.6 L106 80.6 L110 116 H90Z", shadow=False, spot=True)
    d.limb("hero2", "M100 104 L118 74", 7)
    d.shape("hero", rrect(60, 114, 80, 40, 3))
    d.shape("light", "M58 112 H142 V118 H58Z", shadow=False)
    d.shape("dark", rrect(92, 130, 16, 24, 2), shadow=False)
    d.shape("glow2", rrect(72, 126, 10, 10, 2), shadow=False)
    d.shape("glow2", rrect(118, 126, 10, 10, 2), shadow=False)
    d.band("near", hills(160, 5, 10))
    d.band("dark", hills(182, 4, -20), line=False)


# ================================================================ VOLCANO HIKE
CONE = "M14 176 C40 150 62 112 78 80 L90 86 L100 80 L112 86 L122 80 C138 112 160 150 186 176Z"


def volcano_erupt(d: Drawing):
    d.disc("glow", 160, 70, 14)
    for x, y, r in [(100, 64, 18), (84, 50, 16), (116, 46, 18), (98, 32, 16), (76, 30, 12), (124, 24, 13)]:
        d.shape("far", circle(x, y, r))
    d.band("mid", hills(150, 6))
    d.shape("deep", CONE)
    d.shape("pop", "M80 84 L90 86 L100 80 L112 86 L120 84 C116 96 112 100 114 112 C116 124 108 132 110 146 "
                   "C102 132 106 120 102 108 C98 100 92 104 90 118 C88 128 80 134 78 144 C78 126 86 112 84 100Z", spot=True, shadow=False)
    d.shape("glow2", "M90 86 L100 80 L110 86 C106 92 102 92 100 98 C98 92 94 92 90 86Z", shadow=False)
    for x, y, r in [(70, 62, 4), (132, 58, 4.5), (60, 80, 3), (142, 76, 3)]:
        d.shape("pop", circle(x, y, r), shadow=False)
    d.band("near", hills(170, 4, 20))
    d.band("ground", hills(186, 3), line=False)


def volcano_trail(d: Drawing):
    d.disc("glow", 160, 50, 14)
    for x, y, r in [(100, 62, 12), (90, 50, 11), (106, 42, 13), (96, 30, 10)]:
        d.shape("far", circle(x, y, r))
    d.band("mid", hills(150, 6))
    d.shape("deep", "M6 178 C40 150 62 112 78 84 L88 90 L100 86 L112 90 L122 84 C138 112 160 150 194 178Z")
    d.shape("pop", "M80 86 Q100 78 120 86 Q100 94 80 86Z", shadow=False, spot=True)
    trail = [(70, 170), (124, 156), (70, 140), (116, 126), (82, 112), (108, 100), (94, 90)]
    segs = []
    for (x0, y0), (x1, y1) in zip(trail, trail[1:]):
        for k in range(0, 10, 2):
            a, b = k / 10, (k + 1.1) / 10
            segs.append(f"M{x0 + (x1 - x0) * a:.1f} {y0 + (y1 - y0) * a:.1f} L{x0 + (x1 - x0) * b:.1f} {y0 + (y1 - y0) * b:.1f}")
    d.stroke("light", " ".join(segs), 2.6)
    d.stroke("dark", "M152 182 V140", 3.5)
    d.shape("hero2", "M136 132 H164 L172 139 L164 146 H136Z", spot=True)
    d.band("near", hills(178, 4, -30))


def volcano_boot(d: Drawing):
    d.disc("glow", 100, 84, 50)
    d.band("far", hills(130, 8))
    d.band("deep", "M-30 150 L20 144 L60 152 L100 146 L150 154 L230 146")
    d.stroke("pop", "M10 162 L36 156 L48 166 L78 160 M120 170 L140 160 L170 166 L196 158 M60 180 L90 172 L112 182", 3)
    d.stroke("glow2", "M24 159 L36 156 M144 161 L156 163", 1.6, line=False)
    for x in (32, 160):
        d.stroke("light", f"M{x} 150 C{x - 6} 140 {x + 6} 132 {x} 122", 2.2)

    def boot():
        d.shape("hero", "M66 52 H108 L112 98 Q140 102 158 114 Q168 122 166 136 H58 Q58 100 66 52Z")
        d.shape("hero2", rrect(62, 46, 50, 10, 4))
        d.shape("hero2", "M60 112 Q90 108 112 98 Q140 102 158 114 Q168 122 166 130 H60Z", shadow=False)
        d.stroke("light", "M106 60 L116 66 M108 72 L118 78 M110 84 L122 90 M114 96 L128 100", 2.4)
        d.shape("dark", "M54 134 H168 Q172 134 172 140 V146 H54Z")
        d.stroke("deep", " ".join(f"M{x} 143 V147" for x in range(62, 170, 9)), 2.4, line=False)
    group(d, "translate(-8 4)", boot)


# ================================================================ GLACIER HIKE
def glacier_valley(d: Drawing):
    d.disc("glow", 150, 46, 14)
    d.band("far", "M-30 96 L10 66 L40 86 L76 44 L108 82 L136 58 L170 86 L196 66 L230 92")
    for snow in ["M76 44 L88 58 L82 56 L76 62 L70 56 L65 58Z", "M136 58 L146 70 L140 68 L135 73 L130 68 L126 70Z",
                 "M10 66 L18 75 L12 74 L8 78 L3 73Z"]:
        d.shape("light", snow, shadow=False)
    d.shape("light", "M94 70 Q102 66 110 70 C114 94 98 104 108 124 C116 138 138 144 162 150 Q100 162 38 150 C60 140 74 128 72 112 C70 94 90 88 94 70Z")
    d.stroke("mid", "M102 70 C100 90 86 100 92 120 C96 134 100 144 100 156", 2.6)
    d.stroke("sky2", "M86 92 l6 3 M106 86 l-5 3 M80 112 l7 2 M108 108 l-6 3 M70 136 l8 2 M120 134 l-7 3 M84 144 l6 2 M134 146 l-6 2", 2.2)
    d.shape("mid", "M-30 92 C30 90 70 96 90 76 C92 110 74 140 40 160 H-30Z", line=False)
    d.shape("mid", "M230 92 C170 90 130 96 112 76 C114 110 128 140 160 160 H230Z", line=False)
    d.band("near", waves(152, 3, 30))
    for x, y, w in [(64, 160, 12), (138, 164, 10), (100, 170, 8)]:
        d.shape("light", f"M{x - w} {y} L{x - w * .5} {y - w * .8} L{x + w * .3} {y - w * .6} L{x + w} {y}Z")
    d.band("deep", waves(178, 3, 34), line=False)


def glacier_axe(d: Drawing):
    d.disc("glow", 52, 54, 16)
    d.band("far", "M-30 104 L20 74 L54 96 L96 56 L134 94 L166 72 L230 100")
    for snow in ["M96 56 L108 70 L102 68 L96 74 L90 68 L84 70Z", "M166 72 L175 82 L170 81 L165 85 L160 80Z"]:
        d.shape("light", snow, shadow=False)
    d.band("light", "M-30 128 L20 120 L60 130 L110 118 L160 128 L230 120")
    d.stroke("sky2", "M30 140 L44 152 M70 134 L66 146 M150 138 L160 150 M176 134 L170 142", 2.4)
    d.stroke("hero2", "M126 150 C150 150 170 140 166 128 C162 118 140 122 140 132 C140 146 166 150 176 140", 4)
    d.limb("hero", "M78 158 L118 64", 7, spot=True)
    d.shape("dark", "M114 60 C130 60 146 70 158 82 C164 88 168 96 168 102 C156 90 140 80 120 74 Z")
    d.marks("light", "M150 84 l3 4 l2 -5Z M140 77 l3 4 l2 -5Z")
    d.shape("dark", "M120 62 L92 52 Q86 52 84 58 L84 62 L116 72Z")
    d.shape("light", "M76 158 L71 172 L82 162Z", shadow=False)
    d.band("light", "M-30 160 Q60 150 100 158 T230 156")
    d.band("sky2", "M-30 180 Q60 172 100 178 T230 174", line=False)


CAVE = [("mark", "M28 168 C18 90 56 30 102 28 C152 30 186 92 176 168Z"),
        ("hero2", "M40 160 C34 96 64 48 102 46 C144 48 170 98 162 160Z"),
        ("hero", "M50 150 C46 100 70 66 100 62 C134 64 156 102 150 150Z")]


def glacier_cave(d: Drawing):
    d.band("far", "M-30 120 L30 90 L60 110 L100 70 L140 108 L170 92 L230 120", line=False)
    d.shape("light", "M88 82 L100 70 L112 82 L106 80 L100 86 L94 80Z", shadow=False, line=False)
    d.band("ground", hills(140, 5), line=False)
    for role, hole in reversed(CAVE):
        d.shape(role, "M-30 -30 H230 V230 H-30Z " + hole, extra='fill-rule="evenodd"', line=False)
    d.stroke("light", "M40 70 L52 92 M150 54 L142 74 M164 120 L174 138 M30 130 L24 150", 2.2, line=False)
    ink = d.c.get("ink", "")
    spot = d.c.get("spot", "")
    d.raw("", f'<path d="{CAVE[1][1]} {CAVE[2][1]}" fill="{spot}" fill-rule="evenodd"/>'
              f'<path d="M60 150 L64 118 L80 100 L100 76 L120 100 L136 116 L142 150" fill="none" stroke="{ink}" stroke-width="3" stroke-linejoin="round"/>'
              + "".join(f'<path d="{h}" fill="none" stroke="{ink}" stroke-width="3"/>' for _, h in CAVE))
    d.band("light", "M-30 160 Q100 146 230 160")
    d.shape("dark", circle(100, 132, 4))
    d.shape("dark", "M96 137 Q100 135 104 137 L105 150 H95Z")
    d.band("hero2", "M-30 182 Q100 172 230 182", line=False)


# ================================================================ RAINFOREST TREK
def _leaf(x, y, L, ang, w):
    a = math.radians(ang)
    tx, ty = x + L * math.cos(a), y + L * math.sin(a)
    mx, my = (x + tx) / 2, (y + ty) / 2
    px, py = -math.sin(a) * w, math.cos(a) * w
    return (f"M{x:.1f} {y:.1f} Q{mx + px:.1f} {my + py:.1f} {tx:.1f} {ty:.1f} Q{mx - px:.1f} {my - py:.1f} {x:.1f} {y:.1f}Z",
            f"M{x:.1f} {y:.1f} L{tx:.1f} {ty:.1f}")


def leaves(d, items, rib="light", line=True):
    for role, x, y, L, ang, w in items:
        p, r = _leaf(x, y, L, ang, w)
        d.shape(role, p, line=line)
        d.stroke(rib, r, 1.2, line=False)


TOUCAN_BODY = "M80 88 C68 102 66 130 74 148 C78 158 84 172 88 186 L100 186 C98 170 104 152 108 132 C112 112 108 96 100 88Z"


def rf_toucan(d: Drawing):
    d.disc("glow", 140, 52, 18)
    leaves(d, [("far", -10, 60, 70, -20, 18), ("far", 210, 70, 70, 200, 18), ("mid", -10, 120, 70, -40, 18),
               ("mid", 210, 120, 80, 210, 20), ("far", 160, 196, 60, 250, 14)], line=False)
    leaves(d, [("mid", 150, 120, 34, -40, 9), ("mid", 46, 112, 30, 220, 8)])
    d.band("near", "M-30 182 Q40 168 100 178 T230 172", line=False)
    d.limb("deep", "M14 150 Q80 140 188 147", 10)
    d.shape("dark", TOUCAN_BODY)
    d.shape("dark", circle(92, 78, 19))
    d.shape("hero2", "M104 68 C114 76 116 94 110 112 C106 122 98 122 94 110 C92 98 94 84 104 68Z", shadow=False)
    d.shape("hero", "M104 64 C128 56 158 64 174 92 C150 84 128 88 108 92 C104 84 102 74 104 64Z", spot=True)
    d.shape("pop", "M160 74 C166 80 170 86 174 92 C168 88 162 86 156 86Z", shadow=False)
    d.stroke("dark", "M108 80 C128 76 148 78 170 90", 1.4)
    d.shape("glow2", circle(94, 74, 6), shadow=False)
    d.marks("dark", circle(94, 74, 3))
    d.stroke("dark", "M90 148 L92 150 M98 148 L96 152", 3)
    leaves(d, [("near", 210, 190, 90, 225, 22), ("near", -10, 196, 80, -50, 20)], line=False)
    leaves(d, [("near", 150, 176, 34, -60, 9), ("near", 40, 178, 32, 240, 8)])


def rf_bridge(d: Drawing):
    d.disc("glow", 100, 52, 16)
    for x, y, r in [(10, 100, 26), (42, 86, 22), (160, 82, 24), (192, 98, 24), (100, 104, 26), (70, 100, 20), (132, 98, 22)]:
        d.shape("far", circle(x, y, r), line=False)
    d.band("far", "M-30 110 L230 110", shadow=False, line=False)
    d.band("mid", "M-30 144 Q0 128 30 140 Q60 126 90 142 Q120 126 150 140 Q180 128 230 142")
    sag = lambda x, y0, depth: y0 + depth * (1 - ((x - 100) / 66) ** 2)
    d.limb("deep", "M34 52 V184 M166 52 V184", 9)
    d.stroke("dark", " ".join(f"M{x} {sag(x, 78, 24):.1f} V{sag(x, 104, 26):.1f}" for x in range(46, 160, 12)), 1.4)
    d.stroke("dark", "M34 78 Q100 126 166 78", 2.4)
    d.limb("hero2", "M34 104 Q100 156 166 104", 6, spot=True)
    d.stroke("dark", " ".join(f"M{x} {sag(x, 102, 26):.1f} V{sag(x, 108, 26):.1f}" for x in range(40, 164, 7)), 1.2)
    leaves(d, [("near", -10, 40, 60, 20, 14), ("near", 210, 40, 60, 160, 14), ("deep", -10, 150, 70, -30, 18),
               ("deep", 210, 160, 70, 210, 18), ("near", 20, 196, 60, -80, 14), ("near", 180, 196, 60, 260, 14)], line=False)
    leaves(d, [("near", 34, 60, 30, -30, 8), ("near", 166, 60, 30, 210, 8), ("near", 34, 150, 28, -20, 7), ("near", 166, 150, 28, 200, 7)])
    d.band("deep", hills(186, 4), line=False)


def rf_waterfall(d: Drawing):
    d.disc("glow", 150, 46, 14)
    d.band("far", "M-30 62 Q40 46 100 54 T230 50")
    d.band("deep", "M-30 70 Q30 60 70 64 L80 62 H120 L130 64 Q170 60 230 70")
    d.shape("light", "M80 62 H120 C121 90 122 120 126 148 H74 C78 120 79 90 80 62Z", spot=True)
    d.stroke("sky2", "M90 70 V140 M100 66 V146 M110 70 V140", 2.4, line=False)
    d.band("mid", waves(146, 3, 24))
    for x, y, r in [(80, 148, 8), (96, 150, 9), (112, 147, 8), (124, 150, 6)]:
        d.shape("light", circle(x, y, r), shadow=False)
    d.stroke("light", "M60 162 H80 M110 166 H140", 2)
    leaves(d, [("near", -10, 70, 80, 10, 18), ("near", 210, 60, 80, 170, 18), ("near", -10, 190, 80, -40, 20),
               ("near", 210, 190, 80, 220, 20), ("hero", 30, 196, 60, -70, 14), ("hero", 176, 196, 56, 250, 12)], line=False)
    leaves(d, [("near", 20, 100, 40, -10, 10), ("near", 180, 96, 40, 190, 10), ("near", 34, 170, 36, -40, 10), ("near", 166, 170, 36, 220, 10)])
    d.band("near", hills(188, 3), line=False)


# ================================================================ concept list
HORSE_BROWN = {"hero": "#9C5B34", "hero2": "#74401F", "mark": "#3B2A20"}
CAMEL_TAN = {"hero": "#D2A060", "hero2": "#A9773F", "mark": "#4A3220"}

NIGHT = ["coastal", "blush", "dusk", "golden"]
LAVA = {"pop": "#F25C2A", "glow2": "#FFC845"}
SMOKE = {"far": "#B9B4AE", **LAVA}
ICE = {"hero": "#5FA8CC", "hero2": "#9FD3E8", "mark": "#D2EEF7", "light": "#F4FBFE"}
TOUCAN = {"hero": "#F7941D", "hero2": "#FFE27A", "pop": "#D7263D", "dark": "#1E1E24"}
JUNGLE_PALETTES = ["meadow", "coastal", "dusk", "golden", "blush"]

CONCEPTS = [
    Concept("horse-saddled-meadow", "horse-riding", "Saddled horse", horse_meadow, overrides=HORSE_BROWN,
            checks=[("hero", "mid"), ("hero", "far"), ("hero", "sky"), ("pop", "hero")],
            fixes={"pop": ["hero2", "light", "#3E7CB1"]}),
    Concept("horse-head", "horse-riding", "Horse & bridle", horse_head, overrides=HORSE_BROWN,
            checks=[("hero", "glow"), ("hero", "sky"), ("pop", "hero"), ("mark", "far")],
            fixes={"glow": ["glow2", "far", "light"], "pop": ["#3E7CB1", "light"]}),
    Concept("horse-canyon-ride", "horse-riding", "Canyon trail ride", horse_canyon,
            checks=[("dark", "glow"), ("dark", "mid"), ("dark", "far"), ("dark", "ground")]),
    Concept("camel-dunes", "camel-trek", "Camel in the dunes", camel_dunes, overrides=CAMEL_TAN,
            checks=[("hero", "sky"), ("hero", "mid"), ("hero", "far"), ("hero", "ground"), ("pop", "hero")],
            fixes={"ground": ["near", "deep"], "pop": ["#3E7CB1", "mark"]}),
    Concept("camel-caravan", "camel-trek", "Caravan at sunset", camel_caravan,
            checks=[("dark", "glow"), ("dark", "mid"), ("dark", "sky")]),
    Concept("camel-head", "camel-trek", "Camel portrait", camel_head, overrides=CAMEL_TAN,
            checks=[("hero", "sky"), ("hero", "glow"), ("pop", "hero"), ("hero", "mid")],
            fixes={"glow": ["glow2", "light"], "pop": ["#3E7CB1", "mark"]}),
    Concept("offroad-river", "off-road-4x4", "River crossing", offroad_river, ["coastal", "meadow", "dusk"],
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "near"), ("hero", "mid")],
            fixes={"hero": ["pop", "hero2", "deep"]}),
    Concept("offroad-dune", "off-road-4x4", "Dune climb", offroad_dune,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "ground")],
            fixes={"hero": ["pop", "deep", "near"]}),
    Concept("offroad-front", "off-road-4x4", "Muddy 4x4", offroad_front,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "mid"), ("hero", "near"), ("near", "sky"), ("dark", "near")],
            fixes={"hero": ["pop", "hero2", "light"]}),
    Concept("road-campervan", "road-trip", "Campervan on the coast", road_campervan,
            checks=[("hero", "ground"), ("hero", "mid"), ("light", "sky"), ("hero", "far"), ("pop", "sky")],
            fixes={"hero": ["pop", "deep", "near"], "pop": ["hero2", "near"], "light": ["hero2", "glow2", "far"]}),
    Concept("road-convertible", "road-trip", "Vintage convertible", road_convertible,
            checks=[("hero", "glow"), ("hero", "far"), ("hero", "ground"), ("hero", "sky"), ("light", "sky")],
            fixes={"glow": ["glow2", "far", "light"], "hero": ["pop", "deep"], "light": ["hero2", "glow2"]}),
    Concept("road-winding", "road-trip", "Open road", road_winding,
            checks=[("dark", "near"), ("hero2", "near"), ("deep", "near")],
            fixes={"hero2": ["light", "glow"], "deep": ["dark", "mid"]}),
    Concept("camp-tent", "camping", "Tent in the pines", camp_tent,
            checks=[("hero", "mid"), ("hero", "far"), ("deep", "mid"), ("hero", "ground"), ("hero", "hero2")],
            fixes={"hero": ["pop", "deep"], "hero2": ["glow2", "light", "pop"]}),
    Concept("camp-fire", "camping", "Campfire", camp_fire,
            checks=[("pop", "glow"), ("dark", "glow"), ("glow2", "pop"), ("far", "ground")],
            fixes={"glow": ["sky2", "far", "light"], "far": ["mid", "near"]}),
    Concept("camp-lantern", "camping", "Camp lantern", camp_lantern,
            checks=[("hero", "glow"), ("light", "glow"), ("glow2", "light"), ("deep", "far")],
            fixes={"glow": ["near", "mid", "deep"], "glow2": ["#FFD25E", "hero2"]}),
    Concept("glamp-bell-tent", "glamping", "Bell tent", glamp_bell,
            checks=[("hero2", "sky"), ("hero2", "far"), ("ground", "hero2"), ("hero2", "deep")],
            fixes={"hero2": ["hero", "pop"], "ground": ["light", "far"]}),
    Concept("glamp-yurt", "glamping", "Yurt", glamp_yurt,
            checks=[("light", "mid"), ("light", "far"), ("hero", "sky"), ("pop", "light"), ("hero", "far")],
            fixes={"hero": ["deep", "pop", "near"]}),
    Concept("glamp-dome", "glamping", "Dome under the stars", glamp_dome, ["coastal", "blush", "dusk", "golden", "meadow"],
            checks=[("light", "near"), ("near", "deep"), ("glow", "deep"), ("light", "deep")]),
    Concept("star-telescope", "stargazing", "Telescope", star_telescope, NIGHT,
            checks=[("hero", "deep"), ("near", "deep"), ("hero2", "near"), ("light", "deep")],
            fixes={"hero": ["pop", "hero2"]}),
    Concept("star-constellation", "stargazing", "Constellations", star_constellation, NIGHT,
            checks=[("near", "deep"), ("dark", "near"), ("light", "deep")], fixes={"near": ["mid", "far"]}),
    Concept("star-observatory", "stargazing", "Observatory", star_observatory, NIGHT,
            checks=[("light", "deep"), ("far", "deep"), ("light", "far"), ("hero", "far"), ("near", "far")],
            fixes={"far": ["mid", "near"], "near": ["dark"]}),
    Concept("volcano-erupt", "volcano-hike", "Eruption", volcano_erupt, overrides={"deep": "#5A4A48", **SMOKE},
            checks=[("deep", "sky"), ("deep", "mid"), ("pop", "deep"), ("far", "sky"), ("deep", "near")],
            fixes={"far": ["#8E8A86", "light"], "near": ["dark", "mid"]}),
    Concept("volcano-trail", "volcano-hike", "Crater trail", volcano_trail,
            overrides={"deep": "#5A4A48", **SMOKE},
            checks=[("deep", "sky"), ("deep", "mid"), ("light", "deep"), ("hero2", "near"), ("far", "sky"), ("pop", "deep"), ("near", "deep")],
            fixes={"far": ["#8E8A86"], "near": ["mid", "ground", "far"]}),
    Concept("volcano-boot", "volcano-hike", "Boot on lava", volcano_boot, overrides=LAVA,
            checks=[("hero", "glow"), ("hero", "deep"), ("pop", "deep"), ("hero2", "hero"), ("dark", "deep")],
            fixes={"glow": ["glow2", "far", "sky2"], "dark": ["mark", "#111111"]}),
    Concept("glacier-valley", "glacier-hike", "Glacier valley", glacier_valley,
            checks=[("light", "mid"), ("light", "far"), ("light", "near"), ("sky2", "light")],
            fixes={"sky2": ["far", "mid"]}),
    Concept("glacier-axe", "glacier-hike", "Ice axe", glacier_axe,
            checks=[("hero", "light"), ("dark", "light"), ("hero", "far"), ("dark", "far"), ("light", "far")],
            fixes={"hero": ["pop", "deep"]}),
    Concept("glacier-cave", "glacier-hike", "Ice cave", glacier_cave, overrides=ICE,
            checks=[("hero", "ground"), ("hero", "sky"), ("light", "ground")], fixes={"ground": ["near", "mid"]}),
    Concept("rf-toucan", "rainforest-trek", "Toucan", rf_toucan, JUNGLE_PALETTES, overrides=TOUCAN,
            checks=[("dark", "mid"), ("dark", "far"), ("hero", "sky"), ("hero", "far"), ("dark", "deep")],
            fixes={"deep": ["#7A5230"]}),
    Concept("rf-bridge", "rainforest-trek", "Canopy bridge", rf_bridge, JUNGLE_PALETTES,
            checks=[("hero", "far"), ("hero", "mid"), ("dark", "far"), ("near", "far"), ("hero2", "mid")],
            fixes={"hero": ["dark", "deep"], "hero2": ["ground", "light"]}),
    Concept("rf-waterfall", "rainforest-trek", "Jungle waterfall", rf_waterfall, JUNGLE_PALETTES,
            checks=[("light", "deep"), ("near", "deep"), ("near", "mid"), ("hero", "near"), ("light", "mid")]),
]
