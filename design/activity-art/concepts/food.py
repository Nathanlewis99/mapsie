"""Food & drink: three concepts each for sixteen eating and drinking activities."""
from _common import Concept, Drawing, cloud, fish, circle, ellipse, waves, hills, rrect, group


# ================================================================ helpers
def steam(d: Drawing, xs, y, h=22, role="light", w=3.2):
    """Wavy steam rising from y (bottom) for each x."""
    for i, x in enumerate(xs):
        k = 1 if i % 2 == 0 else -1
        q = h / 4
        d.stroke(role, f"M{x} {y} q{4*k} {-q} 0 {-2*q} t0 {-2*q}", w)


def table(d: Drawing, y, top="ground", front="near", lip=10):
    """Flat table top with a darker front edge, edge to edge."""
    d.band(top, f"M-30 {y} L230 {y}")
    d.band(front, f"M-30 {y+lip} L230 {y+lip}", line=False)


def chopsticks(d: Drawing, x1, y1, x2, y2, gap=7, role="dark", w=3.6):
    d.stroke(role, f"M{x1} {y1} L{x2} {y2}", w, shadow=True)
    d.stroke(role, f"M{x1+gap} {y1+gap*0.5} L{x2+gap*0.25} {y2+gap*0.9}", w, shadow=True)


def lanterns(d: Drawing, pts, string="dark", body="pop", sway=8):
    xs = [p[0] for p in pts]
    d.stroke(string, f"M-30 {pts[0][1]-14} " + " ".join(f"Q{x-12} {y-6} {x} {y-14}" for x, y in pts) + " L230 20", 1.4)
    for x, y in pts:
        d.shape(body, ellipse(x, y, 7, 9), spot=True)
        d.shape("dark", rrect(x - 4, y - 11, 8, 3, 1), shadow=False)
        d.shape("dark", rrect(x - 4, y + 8, 8, 3, 1), shadow=False)


# ================================================================ STREET FOOD
def sfood_cart(d: Drawing):
    d.disc("glow", 152, 52, 20)
    d.band("far", "M-30 150 V112 H14 V96 H34 V120 H52 V150 H148 V104 H170 V88 H190 V110 H230")
    d.band("ground", "M-30 160 Q100 154 230 160")
    # back wall and poles
    d.shape("near", rrect(54, 74, 92, 40, 2), line=False)
    d.stroke("dark", "M54 72 V114 M146 72 V114", 3)
    # awning: scalloped stripes
    d.shape("pop", rrect(42, 54, 116, 10, 3), spot=True)
    for i in range(6):
        x = 44 + i * 112 / 6
        role = "pop" if i % 2 == 0 else "light"
        d.shape(role, f"M{x:.1f} 62 H{x+112/6:.1f} V76 a{56/6:.2f} 6 0 0 1 {-112/6:.1f} 0Z", spot=i % 2 == 0, shadow=i == 0)
    # pot and steam
    steam(d, [70, 80, 90], 96, 18)
    d.shape("dark", rrect(64, 96, 32, 14, 4))
    d.shape("dark", rrect(60, 94, 40, 4, 2), shadow=False)
    # bowls stack
    d.shape("hero2", "M108 104 H136 a14 9 0 0 1 -28 0Z", spot=True)
    d.shape("hero2", "M110 98 H134 a12 7 0 0 1 -24 0Z", spot=True)
    # counter and cart body
    d.shape("hero2", rrect(46, 108, 108, 7, 2))
    d.shape("hero", rrect(52, 114, 96, 34, 3))
    d.shape("light", rrect(62, 122, 34, 18, 2), shadow=False)
    d.stroke("hero", "M68 131 H90", 2.4, line=False)
    d.stroke("dark", "M148 120 L172 110", 3.2)
    d.stroke("dark", "M140 148 V160", 3.4)
    d.shape("dark", circle(76, 152, 12))
    d.shape("light", circle(76, 152, 4.5), shadow=False)


def sfood_skewers(d: Drawing):
    d.disc("glow", 100, 92, 58)
    steam(d, [62, 84, 116, 138], 78, 26, role="light")
    # skewers lying across the grill top
    for i, y in enumerate([88, 104, 120]):
        def sk(y=y, i=i):
            d.stroke("dark", f"M34 {y+6} L168 {y-6}", 2.2, shadow=True)
            for j in range(5):
                x = 58 + j * 20
                yy = y + 6 - (x - 34) * 12 / 134
                role = ["hero", "pop", "hero", "hero2", "hero"][(j + i) % 5]
                d.shape(role, rrect(x - 8, yy - 8, 16, 16, 5), spot=role == "pop")
            d.marks("mark", "")
        sk()
    d.shape("dark", "M30 132 H170 L160 172 H40Z")
    d.shape("pop", "M40 132 H160 L157 140 H43Z", shadow=False, spot=True)
    d.stroke("glow2", "M48 136 H152", 1.6, line=False)
    d.limb("dark", "M56 170 L50 190 M144 170 L150 190", 5)


def sfood_dumplings(d: Drawing):
    d.disc("glow", 100, 70, 42)
    table(d, 140)
    steam(d, [76, 100, 124], 92, 30)
    # bamboo steamer
    d.shape("hero", "M34 110 H166 V150 a66 14 0 0 1 -132 0Z")
    d.stroke("hero2", "M34 128 a66 12 0 0 0 132 0 M34 142 a66 12 0 0 0 132 0", 2.6)
    d.shape("hero2", ellipse(100, 110, 66, 18))
    d.shape("mark", ellipse(100, 112, 58, 13), shadow=False, line=False)
    for x, y in [(70, 108), (100, 104), (130, 108), (86, 116), (116, 116)]:
        d.shape("light", f"M{x-13} {y+3} C{x-12} {y-10} {x+12} {y-10} {x+13} {y+3} Q{x} {y+7} {x-13} {y+3}Z")
        d.stroke("mark", f"M{x-5} {y-5} Q{x-3} {y-1} {x-4} {y+2} M{x} {y-6} V{y+2} M{x+5} {y-5} Q{x+3} {y-1} {x+4} {y+2}", 1.3)
    chopsticks(d, 168, 46, 122, 98, 7, "dark", 3.4)


# ================================================================ COOKING CLASS
def cook_hat(d: Drawing):
    d.disc("hero", 100, 100, 62)
    # crossed wooden spoon and whisk behind
    d.limb("ground", "M50 166 L146 62", 6)
    d.shape("ground", ellipse(152, 52, 10, 15), extra='transform="rotate(42 152 52)"')
    d.limb("dark", "M150 166 L76 86", 5)
    d.stroke("dark", "M76 86 C60 86 44 70 50 58 C56 48 78 66 76 86 M76 86 C66 76 58 64 58 54 M76 86 C72 72 68 60 64 52", 2.4)
    def hat():
        d.shape("light", "M64 108 C46 104 42 76 60 70 C62 50 86 44 98 54 C110 42 136 48 138 68 C158 70 158 104 136 108Z")
        d.stroke("hero2", "M80 104 Q78 86 84 76 M100 104 V74 M120 104 Q122 86 116 76", 2, line=False)
        d.shape("light", rrect(62, 106, 76, 26, 5))
        d.stroke("hero2", "M68 114 H132", 2.2, line=False)
    group(d, "translate(100 112) scale(.86) translate(-100 -100)", hat)


def cook_pot(d: Drawing):
    d.disc("glow", 100, 76, 50, line=False)
    table(d, 150, "far", "mid")
    steam(d, [80, 100, 120], 78, 30)
    d.limb("ground", "M126 96 L156 46", 5)
    d.shape("ground", ellipse(160, 40, 7, 10), extra='transform="rotate(30 160 40)"')
    d.shape("dark", rrect(44, 96, 112, 8, 3))
    d.shape("hero", "M50 102 H150 V128 C150 142 140 148 128 148 H72 C60 148 50 142 50 128Z", spot=True)
    d.shape("hero2", "M50 112 H150 V118 H50Z", shadow=False)
    d.shape("dark", rrect(30, 104, 22, 8, 4))
    d.shape("dark", rrect(148, 104, 22, 8, 4))
    # burner with flames
    d.shape("dark", rrect(56, 150, 88, 8, 3))
    for x in [66, 80, 94, 108, 122, 136]:
        d.shape("pop", f"M{x-4} 150 Q{x-4} 144 {x} 141 Q{x+4} 144 {x+4} 150Z", shadow=False)


def cook_board(d: Drawing):
    d.disc("glow", 140, 58, 30)
    table(d, 120, "far", "mid", 14)
    d.shape("ground", rrect(28, 100, 144, 58, 8))
    d.marks("dark", circle(160, 112, 3.5))
    d.stroke("hero2", "M38 150 H162", 1.6, line=False)
    # tomato
    d.shape("pop", circle(78, 98, 22), spot=True)
    d.shape("hero", "M78 80 l-9 -4 l6 7 l-10 2 l10 3 l3 -1 l3 1 l10 -3 l-10 -2 l6 -7Z", shadow=False)
    d.stroke("hero", "M78 80 V72", 2.4)
    d.shape("light", ellipse(68, 92, 4, 6), shadow=False, line=False)
    # carrot lying on the board
    d.shape("hero2", "M110 128 C126 116 150 106 160 104 C166 104 168 112 162 114 C150 120 126 128 110 128Z", spot=True)
    d.stroke("mark", "M130 118 l2 4 M142 112 l2 4 M152 108 l2 3", 1.4)
    d.stroke("hero", "M163 108 l12 -12 M163 108 l16 -4 M163 108 l6 -16", 3)
    # knife and slices
    d.shape("light", "M72 140 L146 132 L150 137 C126 146 96 148 74 148Z")
    d.shape("dark", rrect(36, 138, 38, 10, 4), extra='transform="rotate(-4 55 143)"')
    for x, y in [(152, 144), (164, 138), (140, 150)]:
        d.shape("hero2", circle(x, y, 6.5))
        d.marks("glow2", circle(x, y, 2.4))


# ================================================================ WINE TASTING
def wine_glass(d: Drawing, x, y, s=1.0, rot=0, wine="pop"):
    def g():
        d.shape("light", f"M{x-13} {y-32} C{x-20} {y-12} {x-16} {y+7} {x} {y+8} C{x+16} {y+7} {x+20} {y-12} {x+13} {y-32}Z")
        d.shape(wine, f"M{x-17.6} {y-16} Q{x} {y-12} {x+17.6} {y-16} C{x+17} {y+2} {x+12} {y+7} {x} {y+7.5} C{x-12} {y+7} {x-17} {y+2} {x-17.6} {y-16}Z", shadow=False, spot=True)
        d.stroke("light", f"M{x-11} {y-10} Q{x-12} {y-2} {x-8} {y+2}", 2, line=False)
        d.limb("light", f"M{x} {y+8} V{y+38}", 3.4, shadow=False)
        d.shape("light", ellipse(x, y + 39, 13, 3.5))
    group(d, f"rotate({rot} {x} {y+39}) translate({x} {y+39}) scale({s}) translate({-x} {-y-39})", g)


def wine_vineyard(d: Drawing):
    d.disc("glow", 100, 66, 26)
    d.band("far", hills(98, 12))
    d.band("mid", "M-30 112 Q100 96 230 116")
    for i, y in enumerate([118, 134, 152]):
        r = 3 + i
        row = f"M-30 {y+8} Q100 {y-8} 230 {y+10}"
        d.stroke("near", row, 2 + i, line=False)
        for k in range(-1, 12):
            x = -10 + k * (18 + 4 * i) + (i * 7)
            t = (x + 30) / 260
            yy = (1 - t) ** 2 * (y + 8) + 2 * (1 - t) * t * (y - 8) + t * t * (y + 10)
            d.shape("near", circle(x, yy - r * 0.6, r), shadow=False, line=i == 2)
    d.band("near", "M-30 172 Q100 164 230 172", line=False)
    wine_glass(d, 76, 106, rot=7)
    wine_glass(d, 124, 106, rot=-7)
    d.stroke("light", "M93 62 l-6 -5 M107 62 l6 -5 M100 58 V50", 2.4)


def wine_grapes(d: Drawing):
    d.disc("glow", 100, 100, 62, line=False)
    d.stroke("dark", "M100 52 C100 40 108 32 118 30", 4)
    d.stroke("hero", "M118 32 c8 -4 14 2 10 8 c-4 6 4 10 8 6", 2)
    d.shape("hero", "M100 50 C82 30 52 34 46 52 C60 50 58 66 74 66 C70 76 86 82 96 70 C104 64 104 56 100 50Z", spot=False)
    d.stroke("mark", "M100 50 L60 50 M80 50 L72 60 M84 50 L88 66", 1.6, line=False)
    pts = [(80, 70), (100, 68), (120, 70), (70, 88), (90, 88), (110, 88), (130, 88), (80, 106), (100, 106), (120, 106),
           (90, 124), (110, 124), (100, 142)]
    for x, y in pts:
        d.shape("hero2", circle(x, y, 11), spot=True)
        d.shape("light", circle(x - 4, y - 4, 2.6), shadow=False, line=False)


def wine_barrel(d: Drawing):
    d.band("far", "M-30 -30 L230 -30", line=False)
    d.shape("sky", "M30 164 V84 C30 40 170 40 170 84 V164Z", line=False)
    d.band("ground", "M-30 164 L230 164")
    # upright barrel
    d.shape("hero", "M48 96 C40 116 40 144 48 164 H112 C120 144 120 116 112 96Z")
    d.stroke("hero2", "M64 98 C60 118 60 142 64 162 M80 98 V162 M96 98 C100 118 100 142 96 162", 1.8, line=False)
    d.stroke("dark", "M46 104 Q80 110 114 104 M42 130 Q80 136 118 130 M46 156 Q80 162 114 156", 4)
    d.shape("hero2", ellipse(80, 96, 32, 6))
    wine_glass(d, 80, 56, 0.85)
    # bottle
    d.shape("deep", "M130 164 V112 C130 102 138 98 140 92 V66 H148 V92 C150 98 158 102 158 112 V164Z", spot=False)
    d.shape("pop", rrect(132, 122, 24, 22, 2), shadow=False, spot=True)
    d.shape("light", rrect(139, 62, 10, 6, 1), shadow=False)


# ================================================================ FINE DINING
def dine_cloche(d: Drawing):
    d.disc("glow", 100, 110, 66)
    table(d, 148, "light", "hero")
    d.shape("light", ellipse(100, 148, 70, 10))
    d.shape("hero2", "M42 146 C42 96 70 76 100 76 C130 76 158 96 158 146Z", spot=True)
    d.shape("light", "M58 132 C58 108 72 94 88 90 C76 100 68 114 66 132Z", shadow=False, line=False)
    d.shape("hero2", ellipse(100, 72, 8, 5))
    d.shape("dark", rrect(36, 142, 128, 7, 3.5))
    for x, y, s in [(46, 70, 1), (156, 62, 1.3), (168, 92, 0.8)]:
        d.marks("light", f"M{x} {y-6*s} L{x+1.6*s} {y-1.6*s} L{x+6*s} {y} L{x+1.6*s} {y+1.6*s} L{x} {y+6*s} L{x-1.6*s} {y+1.6*s} L{x-6*s} {y} L{x-1.6*s} {y-1.6*s}Z")


def dine_setting(d: Drawing):
    d.band("hero", "M-30 -30 L230 -30", line=False)
    d.shape("light", circle(100, 104, 50))
    d.shape("sky", circle(100, 104, 38), shadow=False)
    d.stroke("pop", "M80 116 C80 96 120 92 122 110", 6)
    d.shape("mark", circle(100, 104, 9))
    d.shape("far", "M100 92 l3 -8 l3 9Z", shadow=False)
    d.marks("pop", circle(114, 96, 2.5))
    d.marks("pop", circle(88, 94, 2))
    # fork
    d.shape("light", "M33.5 74 H38.5 L39.5 150 a3.5 3.5 0 0 1 -7 0Z")
    d.shape("light", "M28 52 h3 v16 h3.5 v-16 h3 v16 h3.5 v-16 h3 v18 c0 6 -4 8 -8 8 c-4 0 -8 -2 -8 -8Z")
    # knife
    d.shape("light", "M161 104 H167 L167.5 150 a3.5 3.5 0 0 1 -7 0Z")
    d.shape("light", "M160 106 V60 C168 66 170 84 168 106Z")
    # glass
    d.shape("light", circle(160, 42, 12))
    d.shape("pop", circle(160, 42, 8), shadow=False, spot=True)


def dine_candles(d: Drawing):
    d.band("far", "M-30 -30 L230 -30", line=False)
    d.disc("glow2", 100, 62, 34)
    table(d, 146, "light", "hero")
    # candle in a holder
    d.shape("light", rrect(93, 76, 14, 58, 2))
    d.shape("hero2", "M84 146 H116 L106 136 V128 H94 V136Z", spot=True)
    d.shape("hero2", ellipse(100, 128, 14, 4), shadow=False, spot=True)
    d.stroke("dark", "M100 76 V70", 1.6)
    d.shape("pop", "M100 46 C110 58 108 70 100 71 C92 70 90 58 100 46Z", shadow=False)
    d.shape("glow2", "M100 58 C104 64 104 69 100 69 C96 69 96 64 100 58Z", shadow=False, line=False)
    wine_glass(d, 58, 104, rot=-4, wine="mark")
    wine_glass(d, 142, 104, rot=4, wine="mark")
    d.shape("light", ellipse(100, 152, 30, 4), shadow=False, line=False)


# ================================================================ SEAFOOD FEAST
def sea_crab(d: Drawing):
    d.disc("glow", 100, 84, 56, line=False)
    table(d, 150, "far", "mid")
    d.shape("light", ellipse(100, 148, 76, 16))
    d.shape("sky2", ellipse(100, 147, 60, 11), shadow=False, line=False)
    # legs
    for k in (-1, 1):
        for j, (dx, dy) in enumerate([(34, 4), (40, 14), (36, 24)]):
            x0 = 100 + k * 26
            d.limb("hero", f"M{x0} {120+j*6} L{x0+k*dx} {120+dy-12+j*4} L{x0+k*(dx+8)} {140+j*2}", 4.5)
        # claw arm and pincer
        d.limb("hero", f"M{100+k*30} 112 Q{100+k*50} 106 {100+k*52} 88", 6)
        cx, cy = 100 + k * 52, 72
        import math
        a1, a2 = math.radians(-125), math.radians(-62)
        p1 = (cx + 17 * math.cos(a1), cy + 17 * math.sin(a1))
        p2 = (cx + 17 * math.cos(a2), cy + 17 * math.sin(a2))
        claw = f"M{cx} {cy-3} L{p1[0]:.1f} {p1[1]:.1f} A17 17 0 1 0 {p2[0]:.1f} {p2[1]:.1f}Z"
        d.shape("hero", claw, spot=True, extra=f'transform="rotate({k*22} {cx} {cy})"')
    d.shape("hero", ellipse(100, 120, 40, 22), spot=True)
    d.shape("hero2", "M68 116 C76 104 124 104 132 116 C124 110 76 110 68 116Z", shadow=False, line=False)
    d.stroke("dark", "M90 100 V92 M110 100 V92", 2)
    d.marks("dark", circle(90, 90, 3.2))
    d.marks("dark", circle(110, 90, 3.2))
    d.marks("mark", circle(86, 122, 2.2) + circle(100, 126, 2.2) + circle(114, 122, 2.2))
    # lemon wedge
    d.shape("hero2", "M130 152 a14 14 0 0 1 28 0Z")
    d.shape("light", "M134 152 a10 10 0 0 1 20 0Z", shadow=False, line=False)
    d.shape("hero2", "M136.5 152 a7.5 7.5 0 0 1 15 0Z", shadow=False, line=False)


def oyster(d: Drawing, x, y, rot):
    def o():
        d.shape("hero", f"M{x-20} {y} C{x-22} {y-14} {x-6} {y-20} {x+6} {y-16} C{x+20} {y-12} {x+24} {y+2} {x+16} {y+10} C{x+6} {y+18} {x-16} {y+14} {x-20} {y}Z")
        d.shape("hero2", f"M{x-14} {y} C{x-15} {y-9} {x-4} {y-13} {x+5} {y-10} C{x+15} {y-7} {x+17} {y+2} {x+11} {y+6} C{x+4} {y+11} {x-11} {y+9} {x-14} {y}Z", shadow=False)
        d.shape("mark", ellipse(x + 1, y - 1, 7, 5), shadow=False)
    group(d, f"rotate({rot} {x} {y})", o)


def sea_oysters(d: Drawing):
    d.band("near", "M-30 -30 L230 -30", line=False)
    d.shape("dark", ellipse(100, 106, 80, 60), line=False)
    d.shape("light", ellipse(100, 102, 76, 56))
    for x, y in [(60, 70), (84, 60), (116, 60), (142, 74), (152, 108), (138, 136), (108, 146), (72, 140), (50, 118), (46, 90)]:
        d.marks("sky2", circle(x, y, 6))
    for x, y, r in [(70, 82, -20), (112, 74, 10), (140, 104, 50), (110, 132, 160), (66, 118, 200)]:
        oyster(d, x, y, r)
    # lemon
    d.shape("pop", circle(98, 104, 15), spot=True)
    d.shape("light", circle(98, 104, 11), shadow=False, line=False)
    d.shape("pop", circle(98, 104, 9.5), shadow=False, line=False)
    d.stroke("light", "M98 95 V113 M89 104 H107 M92 98 L104 110 M104 98 L92 110", 1.4, line=False)


def sea_fish(d: Drawing):
    d.disc("glow", 140, 54, 24)
    table(d, 100, "far", "mid", 72)
    d.shape("light", ellipse(100, 130, 84, 28))
    d.shape("sky2", ellipse(100, 128, 70, 20), shadow=False, line=False)
    fish_ = "M40 126 C56 104 104 98 140 118 L166 102 C162 116 162 126 168 142 L140 130 C104 150 56 146 40 126Z"
    d.shape("hero", fish_, spot=True)
    d.shape("hero2", "M48 128 C70 140 110 140 136 128 C104 146 60 144 48 128Z", shadow=False, line=False)
    d.stroke("mark", "M74 112 L84 136 M90 110 L100 136 M106 112 L116 136 M122 116 L130 132", 3.4)
    d.stroke("dark", "M64 114 Q60 126 64 136", 2)
    d.marks("dark", circle(52, 122, 3))
    d.marks("light", circle(51, 121, 1))
    for x, y in [(150, 140), (62, 150)]:
        d.shape("pop", circle(x, y, 9))
        d.shape("light", circle(x, y, 6.5), shadow=False, line=False)
        d.shape("pop", circle(x, y, 5.5), shadow=False, line=False)
    for x, y, r in [(110, 100, -30), (124, 104, 20), (96, 102, 10)]:
        d.shape("near", ellipse(x, y, 7, 3), extra=f'transform="rotate({r} {x} {y})"', shadow=False)


# ================================================================ BEACH BBQ
def beach(d: Drawing, sea_y=118, sand_y=140):
    d.band("far", waves(sea_y, 3, 22))
    d.band("mid", waves(sea_y + 10, 3, 26), line=False)
    d.band("ground", f"M-30 {sand_y} Q100 {sand_y-10} 230 {sand_y}")


def bbq_grill(d: Drawing):
    d.disc("glow", 52, 66, 22)
    beach(d)
    steam(d, [84, 100, 116], 84, 30, role="light")
    # kettle grill
    d.limb("dark", "M80 130 L64 172 M120 130 L136 172 M100 134 V170", 4)
    d.shape("dark", circle(64, 172, 4.5), shadow=False)
    d.shape("dark", circle(136, 172, 4.5), shadow=False)
    d.shape("hero", "M48 100 H152 C152 124 130 140 100 140 C70 140 48 124 48 100Z", spot=True)
    d.shape("dark", rrect(44, 96, 112, 7, 3))
    for i, x in enumerate([62, 82, 104, 124]):
        d.shape("pop", rrect(x, 86, 18, 9, 4.5), extra=f'transform="rotate({(-1)**i*6} {x+9} 90)"')
    d.stroke("dark", "M66 116 H76 M124 116 H134", 2.2)
    # a palm leaning in
    d.limb("dark", "M172 168 Q170 126 156 94", 5)
    for a in ["M156 94 Q170 80 184 88", "M156 94 Q148 78 132 80", "M156 94 Q162 74 176 68", "M156 94 Q142 92 136 102"]:
        d.stroke("near", a, 6, shadow=True)


def bbq_bonfire(d: Drawing):
    d.disc("light", 140, 50, 14)
    beach(d, 110, 132)
    # fish on sticks
    for k in (-1, 1):
        d.stroke("dark", f"M{100+k*72} 166 L{100+k*30} 76", 2.6)
        for t in (0.0, 0.3):
            fx, fy = 100 + k * (30 + 42 * t + 4), 76 + 90 * t + 8
            d.shape("hero", rrect(-16, -5.5, 32, 11, 5.5), extra=f'transform="translate({fx:.1f} {fy:.1f}) rotate({-65 if k < 0 else 65})"', spot=True)
    # flames
    d.shape("pop", "M100 70 C116 92 132 108 126 136 C122 148 78 148 74 136 C68 108 86 96 92 82 C96 92 98 96 100 70Z", spot=True)
    d.shape("glow2", "M100 96 C110 110 116 124 112 136 C108 144 92 144 88 136 C84 124 92 114 100 96Z", shadow=False)
    # logs and stones
    d.limb("dark", "M62 150 L138 132 M62 134 L138 152", 9)
    for x, y in [(52, 156), (74, 162), (100, 164), (126, 162), (148, 156)]:
        d.shape("mid", ellipse(x, y, 10, 6))


def bbq_corn(d: Drawing):
    d.disc("glow", 100, 100, 62, line=False)
    for y in [64, 84, 104, 124, 144]:
        d.stroke("dark", f"M30 {y-12} L170 {y+8}", 3.2, line=False)
    def corn():
        # husk behind
        d.shape("hero", "M60 100 C40 80 34 66 30 54 C48 64 60 72 70 86Z")
        d.shape("hero", "M60 104 C42 112 32 124 26 138 C46 128 60 122 70 116Z")
        d.shape("hero2", "M62 86 C70 74 110 70 150 76 C170 80 170 120 150 124 C110 130 70 126 62 114 C58 106 58 94 62 86Z", spot=True)
        for x in range(76, 156, 12):
            d.stroke("mark", f"M{x} 78 Q{x-4} 100 {x} 124", 1.6)
        d.stroke("mark", "M64 92 Q110 86 166 90 M64 108 Q110 114 166 110", 1.6, line=False)
        for x in [88, 112, 136]:
            d.stroke("dark", f"M{x} 76 L{x+8} 126", 4.5)
        d.shape("hero", "M54 98 C64 84 82 86 84 100 C82 114 64 116 54 102Z")
        d.shape("light", "M118 82 C130 80 138 84 140 90 C130 92 122 90 118 82Z", shadow=False, line=False)
    group(d, "rotate(-14 100 100)", corn)


# ================================================================ RAMEN
def ramen_bowl(d: Drawing):
    d.disc("glow", 100, 82, 56, line=False)
    table(d, 160, "far", "mid")
    steam(d, [76, 98, 120], 72, 30)
    # chopsticks lifting noodles
    chopsticks(d, 156, 36, 108, 86, 7)
    d.stroke("hero2", "M106 88 C102 100 104 108 100 116 M112 90 C108 104 112 110 108 118 M118 90 C116 102 120 108 116 118", 3, shadow=True)
    # bowl
    d.shape("hero", "M36 112 H164 C164 142 140 162 100 162 C60 162 36 142 36 112Z", spot=True)
    d.shape("mark", ellipse(100, 112, 64, 13), shadow=False)
    d.shape("pop", ellipse(100, 114, 58, 9), shadow=False, line=False)
    # toppings
    d.shape("dark", "M50 116 L56 92 L76 96 L72 117Z")
    d.shape("light", ellipse(130, 110, 13, 8))
    d.shape("hero2", circle(132, 110, 5), shadow=False)
    d.shape("light", ellipse(86, 113, 10, 5))
    d.stroke("pop", "M80 112 Q86 109 92 113", 1.6, line=False)
    d.stroke("light", "M44 132 Q100 148 156 132", 4.5, line=False)
    d.shape("dark", rrect(78, 160, 44, 5, 2), shadow=False)


def ramen_top(d: Drawing):
    d.band("hero", "M-30 -30 L230 -30", line=False)
    d.shape("light", circle(100, 104, 70))
    d.shape("pop", circle(100, 104, 60), shadow=False)
    for i in range(6):
        d.stroke("hero2", f"M{58+i*7} {78+i*4} C{78+i*6} {70+i*6} {92+i*6} {96+i*4} {110+i*6} {84+i*6}", 2.4, line=i % 2 == 0)
    d.shape("dark", "M58 70 L84 60 L94 86 L68 96Z")
    d.shape("deep", ellipse(122, 78, 18, 13))
    d.stroke("light", "M110 74 Q122 68 134 76 M112 82 Q122 76 132 84", 1.6, line=False)
    for x, y in [(128, 116), (104, 132)]:
        d.shape("light", ellipse(x, y, 14, 12))
        d.shape("hero2", circle(x, y + 1, 6.5), shadow=False)
    d.shape("light", circle(74, 120, 10))
    d.stroke("pop", "M74 120 m-2 0 a2 2 0 1 1 4 0 a4 4 0 1 1 -8 0 a6 6 0 1 1 12 0", 1.8)
    for x, y in [(88, 104), (96, 98), (92, 112), (82, 100), (148, 98), (142, 92)]:
        d.marks("near", circle(x, y, 2.6))
    chopsticks(d, 40, 160, 170, 64, 8)


def ramen_shop(d: Drawing):
    d.band("far", "M-30 -30 L230 -30", line=False)
    d.disc("glow", 160, 46, 14)
    # building
    d.shape("near", "M24 68 H176 V176 H24Z")
    d.shape("dark", "M14 72 L40 50 H160 L186 72Z")
    d.shape("dark", rrect(10, 68, 180, 8, 3), shadow=False)
    d.shape("glow2", rrect(40, 90, 120, 86, 2), shadow=False)
    d.stroke("near", "M100 90 V176", 4, line=False)
    # noren curtain
    for i in range(4):
        x = 42 + i * 29
        d.shape("hero", f"M{x} 86 H{x+27} V128 H{x}Z", spot=True)
    d.shape("dark", rrect(36, 84, 128, 5, 2), shadow=False)
    d.shape("light", circle(100, 108, 9), shadow=False)
    d.shape("hero", "M100 101 a7 7 0 0 1 0 14 a7 7 0 0 1 0 -14Z m0 3 a4 4 0 0 0 0 8Z", shadow=False, line=False)
    # lanterns
    for x in [30, 170]:
        d.stroke("dark", f"M{x} 76 V86", 1.6)
        d.shape("pop", ellipse(x, 100, 11, 14), spot=True)
        d.shape("dark", rrect(x - 6, 84, 12, 4, 1.5), shadow=False)
        d.shape("dark", rrect(x - 6, 112, 12, 4, 1.5), shadow=False)
        d.stroke("dark", f"M{x-10} 96 H{x+10} M{x-10} 104 H{x+10}", 1, line=False)
    d.band("ground", "M-30 172 L230 172")


# ================================================================ SUSHI
def nigiri(d: Drawing, x, y, fish="hero", stripe=True, s=1.0):
    d.shape("light", f"M{x-20*s} {y+6*s} C{x-22*s} {y-6*s} {x+22*s} {y-6*s} {x+20*s} {y+6*s} C{x+18*s} {y+12*s} {x-18*s} {y+12*s} {x-20*s} {y+6*s}Z")
    d.shape(fish, f"M{x-24*s} {y+2*s} C{x-22*s} {y-14*s} {x+18*s} {y-16*s} {x+25*s} {y-2*s} C{x+20*s} {y+2*s} {x-16*s} {y+6*s} {x-24*s} {y+2*s}Z", spot=True)
    if stripe:
        d.stroke("light", f"M{x-12*s} {y-7*s} l{6*s} {6*s} M{x-2*s} {y-10*s} l{6*s} {7*s} M{x+8*s} {y-10*s} l{6*s} {7*s}", 1.8 * s, line=False)


def sushi_board(d: Drawing):
    d.disc("glow", 100, 64, 30, line=False)
    table(d, 128, "far", "mid", 40)
    d.shape("dark", rrect(44, 148, 16, 14, 2))
    d.shape("dark", rrect(140, 148, 16, 14, 2))
    d.shape("ground", "M26 118 H174 L180 148 H20Z")
    d.shape("near", "M20 148 H180 V153 H20Z", shadow=False, line=False)
    nigiri(d, 52, 112, "hero", True, 1.2)
    nigiri(d, 100, 110, "pop", False, 1.2)
    nigiri(d, 148, 112, "hero", True, 1.2)
    d.shape("hero2", "M64 142 C66 132 78 132 80 142Z")
    d.shape("glow2", "M116 142 c0 -9 11 -11 15 -4 c4 -7 13 -2 11 4Z")


def sushi_maki(d: Drawing):
    d.disc("glow", 100, 100, 62, line=False)
    pts = [(70, 82), (130, 82), (100, 132)]
    for x, y in pts:
        d.shape("dark", circle(x, y, 26), spot=False)
        d.shape("light", circle(x, y, 21), shadow=False)
        d.shape("hero", f"M{x-8} {y-4} L{x+2} {y-10} L{x+9} {y+1} L{x-1} {y+8}Z", shadow=False, spot=True)
        d.shape("hero2", circle(x + 6, y + 8, 4), shadow=False)
        d.shape("near", rrect(x - 12, y + 4, 9, 6, 2), shadow=False, extra=f'transform="rotate(30 {x-7} {y+7})"')
        d.marks("mark", circle(x - 12, y - 10, 1) + circle(x + 13, y - 6, 1) + circle(x - 4, y + 15, 1) + circle(x + 15, y + 10, 1))
    chopsticks(d, 30, 168, 150, 140, 7)


def sushi_nigiri(d: Drawing):
    d.disc("glow", 100, 96, 60, line=False)
    table(d, 146, "far", "mid")
    # soy dish
    d.shape("light", ellipse(140, 150, 30, 10))
    d.shape("dark", ellipse(140, 149, 22, 6), shadow=False)
    # big nigiri
    nigiri(d, 86, 120, "hero", True, 2.4)
    chopsticks(d, 168, 40, 120, 98, 8)


# ================================================================ PIZZA
def pizza_oven(d: Drawing):
    d.disc("glow", 150, 52, 18)
    steam(d, [118, 128], 54, 22)
    d.shape("dark", rrect(112, 56, 16, 30, 2))
    d.band("ground", "M-30 168 L230 168")
    # base with log store
    d.shape("mid", rrect(30, 136, 140, 40, 4))
    d.shape("dark", "M62 176 V164 C62 150 138 150 138 164 V176Z", shadow=False)
    for x, y in [(78, 168), (92, 166), (106, 166), (120, 168), (85, 158), (113, 158), (99, 156)]:
        d.shape("ground", circle(x, y, 6.5), shadow=False)
        d.marks("near", circle(x, y, 2))
    # dome
    d.shape("hero", "M38 140 C38 62 162 62 162 140Z")
    d.stroke("hero2", "M58 96 h12 M84 82 h14 M120 86 h12 M50 118 h10 M142 112 h10 M66 108 h8", 2.6, line=False)
    d.shape("hero2", "M68 140 V118 C68 92 132 92 132 118 V140Z", spot=True)
    d.shape("dark", "M76 140 V120 C76 102 124 102 124 120 V140Z", shadow=False)
    d.shape("pop", "M84 140 C80 126 90 120 92 110 C98 120 102 116 104 106 C110 118 118 124 116 140Z", shadow=False)
    d.shape("glow2", "M92 140 C90 132 96 128 98 122 C102 128 108 132 108 140Z", shadow=False, line=False)
    d.shape("near", rrect(26, 134, 148, 8, 3))


def pizza_whole(d: Drawing):
    d.band("light", "M-30 -30 L230 -30", line=False)
    if d.paper:
        c = d.c["hero"]
        stripes = "".join(f'<rect x="{x}" y="0" width="14" height="200"/>' for x in range(4, 200, 28))
        stripes += "".join(f'<rect x="0" y="{y}" width="200" height="14"/>' for y in range(4, 200, 28))
        d.raw(f'<g fill="{c}" opacity=".45">{stripes}</g>')
    d.shape("ground", circle(100, 102, 68))
    d.shape("mark", circle(100, 102, 58), shadow=False)
    d.shape("hero2", "M100 48 C122 48 150 60 152 84 C158 104 150 132 132 146 C116 158 84 160 66 146 C46 132 40 108 48 84 C54 62 76 48 100 48Z", shadow=False, spot=True)
    for x, y in [(80, 74), (122, 70), (140, 104), (116, 132), (78, 132), (60, 102), (100, 100)]:
        d.shape("pop", circle(x, y, 9), shadow=False)
        d.marks("mark", circle(x - 2, y - 2, 1.4) + circle(x + 3, y + 1, 1.2))
    for x, y, r in [(100, 76, 30), (128, 88, -40), (92, 120, 70), (64, 82, 10), (138, 126, -20)]:
        d.shape("near", ellipse(x, y, 7, 3.5), extra=f'transform="rotate({r} {x} {y})"', shadow=False)
    d.stroke("ground", "M100 102 L100 34 M100 102 L159 136 M100 102 L41 136", 1.6, line=False)


def pizza_slice(d: Drawing):
    d.disc("glow", 100, 100, 60, line=False)
    def sl():
        d.shape("hero2", "M48 62 Q100 44 152 62 L104 172 Q100 178 96 172Z", spot=True)
        d.shape("hero2", "M60 72 C58 92 66 98 62 108 C60 116 70 116 68 106 C66 96 72 88 70 74Z", shadow=False)
        d.shape("hero2", "M138 72 C142 86 136 96 140 108 C142 116 132 116 134 106 C136 94 130 86 132 74Z", shadow=False)
        d.limb("ground", "M46 60 Q100 40 154 60", 13)
        for x, y in [(80, 78), (118, 80), (100, 110), (86, 136), (110, 144)]:
            d.shape("pop", circle(x, y, 9 if y < 120 else 7), shadow=False)
        for x, y, r in [(100, 84, 20), (76, 104, -30), (122, 116, 40)]:
            d.shape("near", ellipse(x, y, 6, 3), extra=f'transform="rotate({r} {x} {y})"', shadow=False)
    group(d, "rotate(-12 100 110)", sl)


# ================================================================ CURRY
def curry_plate(d: Drawing):
    d.band("hero", "M-30 -30 L230 -30", line=False)
    d.shape("light", circle(100, 104, 70))
    d.shape("hero2", circle(100, 104, 56), shadow=False, spot=True)
    d.shape("glow2", "M44 92 C44 64 70 50 92 54 C116 58 122 82 112 104 C102 126 76 132 60 124 C48 118 44 106 44 92Z")
    d.stroke("ground", "M64 80 l4 -2 M76 110 l4 2 M86 70 l3 3 M60 100 l4 -1 M96 94 l3 -3 M80 90 l4 0 M98 74 l3 2", 1.6, line=False)
    for x, y, r in [(132, 92, 9), (140, 124, 9), (104, 138, 8)]:
        d.shape("pop", rrect(x - r, y - r, 2 * r, 2 * r, 3), shadow=False)
    for x, y in [(124, 116), (120, 140), (148, 106), (84, 142)]:
        d.shape("mark", circle(x, y, 5.5), shadow=False)
    for x, y, r in [(108, 58, 20), (116, 64, -40), (66, 136, 30), (150, 140, 10)]:
        d.shape("near", ellipse(x, y, 6, 3.5), extra=f'transform="rotate({r} {x} {y})"', shadow=False)


def curry_pot(d: Drawing):
    d.disc("glow", 100, 78, 52, line=False)
    table(d, 150, "far", "mid")
    steam(d, [80, 100, 120], 82, 28)
    # naan leaning behind
    d.shape("glow2", "M118 150 C110 116 130 70 158 62 C180 58 186 92 176 118 C166 142 146 150 118 150Z", extra='transform="rotate(8 150 106)"')
    for x, y, r in [(150, 80, 3.4), (164, 94, 2.8), (146, 98, 3.4), (166, 112, 2.4)]:
        d.marks("near", circle(x, y, r))
    # handi pot
    d.shape("hero", "M36 106 H164 C168 132 150 156 100 156 C50 156 32 132 36 106Z", spot=True)
    d.shape("hero2", ellipse(100, 106, 64, 12))
    d.shape("pop", ellipse(100, 107, 56, 8), shadow=False, line=False)
    for x, y in [(80, 106), (106, 104), (124, 108)]:
        d.marks("mark", ellipse(x, y, 5, 2.4))
    d.stroke("dark", "M36 112 C24 110 22 124 34 126 M164 112 C176 110 178 124 166 126", 3.4)
    d.stroke("hero2", "M42 128 Q100 142 158 128", 3, line=False)


def sack(d: Drawing, x, y, w, spice):
    d.shape("hero", f"M{x-w} {y} C{x-w-6} {y+26} {x-w+2} {y+48} {x} {y+48} C{x+w-2} {y+48} {x+w+6} {y+26} {x+w} {y}Z")
    d.shape("hero2", f"M{x-w-3} {y} a{w+3} 6 0 0 0 {2*w+6} 0 a{w+3} 6 0 0 0 {-2*w-6} 0Z")
    d.shape(spice, f"M{x-w+1} {y+2} C{x-w*0.6} {y-w*0.5} {x-w*0.3} {y-w*0.95} {x} {y-w*0.95} C{x+w*0.3} {y-w*0.95} {x+w*0.6} {y-w*0.5} {x+w-1} {y+2}Z", spot=spice == "pop", shadow=False)
    d.stroke("hero2", f"M{x-w+4} {y+16} q4 2 8 0 M{x+w-14} {y+28} q4 2 8 0", 1.6, line=False)


def curry_spices(d: Drawing):
    d.disc("glow", 100, 80, 54, line=False)
    d.band("ground", "M-30 160 L230 160")
    sack(d, 54, 94, 26, "pop")
    sack(d, 146, 94, 26, "mark")
    sack(d, 100, 112, 30, "glow2")
    # scoop in the turmeric
    d.limb("dark", "M110 90 L132 64", 4)
    d.shape("light", ellipse(106, 96, 9, 5.5), extra='transform="rotate(-30 106 96)"')
    # chillies in front
    for x, y, r in [(34, 164, -6), (138, 166, 8)]:
        def ch(x=x, y=y):
            d.shape("pop", f"M{x} {y} C{x+10} {y-8} {x+28} {y-6} {x+38} {y+4} C{x+26} {y+2} {x+12} {y+6} {x} {y}Z", spot=True)
            d.stroke("near", f"M{x} {y} q-4 -2 -6 -8", 2.6)
        group(d, f"rotate({r} {x} {y})", ch)


# ================================================================ TACOS
def taco(d: Drawing, x, y, s=1.0):
    def t():
        d.shape("hero", "M-34 0 A34 30 0 0 1 34 0Z", extra="")
        d.shape("near", "M-32 -2 C-28 -16 -18 -22 -10 -18 C-4 -30 10 -30 14 -18 C22 -22 32 -14 32 -2Z", shadow=False)
        for px, py in [(-18, -12), (-2, -18), (14, -12), (-8, -8), (8, -6)]:
            d.shape("mark", circle(px, py, 5), shadow=False)
        for px, py in [(-12, -18), (6, -20), (20, -10)]:
            d.shape("pop", circle(px, py, 3.4), shadow=False)
        d.stroke("light", "M-20 -4 l6 -6 M0 -10 l4 -6 M12 -4 l6 -6", 2.2, line=False)
        d.shape("hero", "M-36 -2 A36 34 0 0 0 36 -2 C24 -2 -24 -2 -36 -2Z", spot=True)
        d.stroke("hero2", "M-26 10 Q0 22 26 10", 2.4, line=False)
    group(d, f"translate({x} {y}) scale({s})", t)


def taco_big(d: Drawing):
    d.disc("glow", 100, 92, 60, line=False)
    table(d, 150, "far", "mid")
    taco(d, 94, 116, 1.9)
    # lime wedge
    d.shape("near", "M140 152 a16 16 0 0 1 32 0Z")
    d.shape("light", "M144 152 a12 12 0 0 1 24 0Z", shadow=False, line=False)
    d.shape("hero2", "M146.5 152 a9.5 9.5 0 0 1 19 0Z", shadow=False, line=False)


def taco_truck(d: Drawing):
    d.disc("glow", 46, 56, 18)
    d.band("far", hills(130, 8))
    d.band("ground", "M-30 154 Q100 148 230 154")
    # truck
    d.shape("hero", "M30 146 V84 C30 78 34 74 40 74 H136 C142 74 146 78 146 84 V96 H158 C164 96 168 100 170 106 L176 124 V146Z", spot=False)
    d.shape("light", "M150 102 H160 L166 120 H150Z", shadow=False)
    d.shape("dark", rrect(42, 88, 82, 34, 3), shadow=False)
    d.shape("glow2", rrect(46, 92, 74, 30, 2), shadow=False, line=False)
    for i in range(5):
        x = 38 + i * 18
        d.shape("pop" if i % 2 == 0 else "light", f"M{x} 82 H{x+18} V94 a9 5 0 0 1 -18 0Z", spot=i % 2 == 0, shadow=i == 0)
    d.shape("hero2", rrect(38, 120, 90, 6, 2))
    d.shape("dark", rrect(26, 140, 154, 8, 3))
    # sign on the roof
    d.stroke("dark", "M76 74 V66 M100 74 V66", 2)
    taco(d, 88, 60, 0.62)
    for x in [58, 148]:
        d.shape("dark", circle(x, 148, 13))
        d.shape("light", circle(x, 148, 4.5), shadow=False)


def taco_fiesta(d: Drawing):
    d.disc("glow", 100, 112, 56, line=False)
    d.stroke("dark", "M-10 30 Q100 58 210 30", 1.6)
    roles = ["pop", "hero2", "far", "hero", "pop", "hero2", "far"]
    for i, x in enumerate(range(30, 180, 24)):
        t = (x + 10) / 220
        y = (1 - t) ** 2 * 30 + 2 * (1 - t) * t * 58 + t * t * 30
        d.shape(roles[i], f"M{x-9} {y-1} H{x+9} V{y+18} L{x+6} {y+15} L{x+3} {y+18} L{x} {y+15} L{x-3} {y+18} L{x-6} {y+15} L{x-9} {y+18}Z",
                shadow=False, spot=i % 2 == 0)
        d.marks("sky", circle(x, y + 7, 2.6))
    table(d, 158, "ground", "near")
    d.shape("light", ellipse(100, 156, 74, 12))
    taco(d, 62, 136, 0.95)
    taco(d, 138, 136, 0.95)
    taco(d, 100, 144, 1.05)


# ================================================================ GELATO
def scoop(d: Drawing, x, y, r, role, drips=True):
    drip = f" C{x+r*0.6} {y+r*0.9} {x+r*0.3} {y+r*0.6} {x+r*0.1} {y+r*0.75} C{x-r*0.1} {y+r*1.1} {x-r*0.4} {y+r*0.6} {x-r*0.6} {y+r*0.8}" if drips else ""
    d.shape(role, f"M{x-r} {y+r*0.55} C{x-r*1.15} {y-r*0.9} {x+r*1.15} {y-r*0.9} {x+r} {y+r*0.55}{drip} C{x-r*0.8} {y+r*0.7} {x-r*0.9} {y+r*0.6} {x-r} {y+r*0.55}Z", spot=role == "pop")


def gelato_cone(d: Drawing):
    d.disc("glow", 100, 96, 62, line=False)
    d.shape("ground", "M70 116 H130 L102 182 Q100 186 98 182Z")
    d.stroke("near", "M80 120 L112 166 M96 120 L118 150 M112 120 L124 134 M120 120 L88 166 M104 120 L82 150 M88 120 L76 134", 1.8)
    scoop(d, 100, 104, 30, "hero")
    scoop(d, 100, 70, 26, "hero2")
    d.shape("far", "M80 54 C76 30 92 22 100 22 C108 22 124 30 120 54 C112 58 88 58 80 54Z")
    d.shape("pop", circle(104, 22, 6.5))
    d.stroke("near", "M104 16 q4 -8 10 -8", 2)
    d.stroke("light", "M86 40 Q90 30 98 28", 2.4, line=False)


def gelato_cup(d: Drawing):
    d.disc("glow", 100, 96, 58, line=False)
    table(d, 164, "far", "mid")
    # wafer and spoon behind
    d.shape("ground", rrect(114, 36, 12, 50, 5), extra='transform="rotate(18 120 60)"')
    d.stroke("near", "M114 50 l12 4 M110 62 l12 4", 1.6, line=False)
    d.limb("dark", "M70 96 L56 42", 5)
    d.shape("dark", ellipse(54, 38, 6, 9), extra='transform="rotate(-14 54 38)"')
    scoop(d, 80, 98, 27, "hero")
    scoop(d, 120, 98, 27, "hero2")
    d.shape("light", "M48 112 H152 L138 164 H62Z")
    d.shape("pop", "M50 122 H150 L147 134 H53Z", shadow=False, spot=True)
    d.shape("pop", "M54 142 H146 L144 150 H56Z", shadow=False)
    d.shape("light", rrect(44, 106, 112, 9, 4))


def gelato_counter(d: Drawing):
    d.band("far", "M-30 -30 L230 -30", line=False)
    # awning
    d.shape("pop", rrect(-10, 20, 220, 18, 0), spot=True)
    for i in range(8):
        x = 4 + i * 24
        d.shape("pop" if i % 2 == 0 else "light", f"M{x} 36 H{x+24} V50 a12 7 0 0 1 -24 0Z", spot=i % 2 == 0, shadow=i == 0)
    # display tubs heaped with gelato
    d.shape("dark", rrect(20, 116, 160, 8, 3))
    roles = ["hero", "hero2", "light", "mark"]
    for i, x in enumerate([44, 81, 119, 156]):
        d.shape(roles[i], f"M{x-18} 118 C{x-20} 92 {x-8} 84 {x} 92 C{x+4} 80 {x+20} 88 {x+18} 118Z")
        d.stroke("dark", f"M{x-10} 104 Q{x} 96 {x+10} 102", 1.6, line=False)
    if d.paper:
        d.raw('<path d="M20 118 L34 72 H180 V118Z" fill="#fff" opacity=".22"/>')
    d.stroke("light", "M20 118 L34 72 H180", 2.6)
    d.shape("ground", rrect(20, 124, 160, 50, 3))
    d.shape("hero2", rrect(20, 134, 160, 7, 0), shadow=False, spot=True)
    d.stroke("near", "M70 150 V168 M130 150 V168", 2, line=False)
    d.band("deep", "M-30 172 L230 172", line=False)


# ================================================================ CAFE & CROISSANT
import math

CROISSANT = []
for _a, _th, _rx in [(-66, 18, 13), (66, 18, 13), (-36, 32, 17), (36, 32, 17), (0, 46, 21)]:
    _r = math.radians(_a)
    CROISSANT.append((100 + 50 * math.sin(_r), 146 - 50 * math.cos(_r), _rx, _th / 2, _a))


def croissant(d: Drawing, tx=0, ty=0, s=1.0, spot=True):
    def c():
        for x, y, rx, ry, r in CROISSANT:
            seg = ellipse(round(x, 1), round(y, 1), rx, ry)
            d.shape("hero", seg, extra=f'transform="rotate({r} {x:.1f} {y:.1f})"', spot=spot and r == 0)
            d.stroke("hero2", f"M{x-rx*0.5:.1f} {y-ry*0.55:.1f} Q{x:.1f} {y-ry*0.85:.1f} {x+rx*0.5:.1f} {y-ry*0.55:.1f}",
                     max(1.4, ry * 0.18), line=False) if False else None
            d.stroke("hero2", f"M{x-rx*0.55:.1f} {y-ry*0.45:.1f} Q{x:.1f} {y-ry*0.8:.1f} {x+rx*0.55:.1f} {y-ry*0.45:.1f}", max(1.4, ry * 0.16), line=False) \
                if False else d.raw(f'<path d="M{x-rx*0.55:.1f} {y-ry*0.45:.1f} Q{x:.1f} {y-ry*0.85:.1f} {x+rx*0.55:.1f} {y-ry*0.45:.1f}" fill="none" stroke="{d.c.get('hero2', '#fff')}" '
                                    f'stroke-width="{max(1.4, ry*0.16):.1f}" stroke-linecap="round" transform="rotate({r} {x:.1f} {y:.1f})"/>', "")
    group(d, f"translate({tx} {ty}) scale({s})", c)


def cafe_croissant(d: Drawing):
    d.disc("glow", 100, 100, 60, line=False)
    table(d, 146, "far", "mid")
    d.shape("light", ellipse(100, 144, 76, 12))
    croissant(d, -14, -8, 1.14)


def cafe_cup(d: Drawing):
    d.disc("glow", 100, 84, 56, line=False)
    table(d, 148, "far", "mid")
    steam(d, [62, 76, 90], 82, 24)
    d.shape("light", ellipse(76, 146, 46, 9))
    d.stroke("light", "M114 102 C132 100 132 126 112 126", 6, shadow=True)
    d.shape("light", "M40 96 H116 C116 126 102 142 78 142 C54 142 40 126 40 96Z", spot=False)
    d.shape("pop", "M44 106 H112 C111 112 110 116 108 120 H48 C46 116 45 112 44 106Z", shadow=False, spot=True)
    d.shape("mark", ellipse(78, 96, 38, 7), shadow=False)
    d.shape("hero2", "M78 101 C70 96 70 91 74 91 C76 91 78 93 78 95 C78 93 80 91 82 91 C86 91 86 96 78 101Z", shadow=False, line=False)
    croissant(d, 104, 74, 0.5, spot=False)


def cafe_bistro(d: Drawing):
    d.band("far", "M-30 -30 L230 -30", line=False)
    d.shape("sky", rrect(36, 50, 128, 100, 4), line=False)
    d.stroke("far", "M100 50 V150", 4, line=False)
    for i in range(6):
        x = 28 + i * 24
        d.shape("pop" if i % 2 == 0 else "light", f"M{x} 32 H{x+24} V52 a12 7 0 0 1 -24 0Z", spot=i % 2 == 0, shadow=i == 0)
    d.shape("pop", rrect(24, 26, 152, 8, 2))
    d.band("ground", "M-30 168 L230 168")
    # chairs
    for k in (-1, 1):
        x = 100 + k * 50
        d.stroke("dark", f"M{x} 172 V140 M{x-k*16} 172 L{x-k*14} 140 M{x+k*2} 112 C{x+k*6} 96 {x-k*12} 96 {x-k*12} 112 V140", 3.4)
        d.shape("dark", rrect(x - 14 if k > 0 else x - 4, 136, 18, 6, 3) if False else f"M{x-k*20} 138 H{x+k*4} V143 H{x-k*20}Z")
    # table
    d.stroke("dark", "M100 120 V168 M86 172 Q100 164 114 172", 3.6)
    d.shape("hero", ellipse(100, 118, 34, 7), spot=False)
    # cup & croissant on the table
    d.shape("light", "M86 102 H104 C104 112 100 114 95 114 C90 114 86 112 86 102Z")
    d.stroke("light", "M104 104 c5 0 5 6 0 6", 2.2)
    croissant(d, 72, 70, 0.22, spot=False)
    steam(d, [92, 98], 98, 12, w=2)


# ================================================================ COCKTAIL BAR
def cocktail_martini(d: Drawing):
    d.disc("glow", 100, 92, 60, line=False)
    d.limb("dark", "M132 40 L96 90", 2.6, shadow=False)
    d.marks("dark", circle(133, 39, 3))
    d.shape("light", "M44 56 H156 L100 116Z")
    d.shape("hero", "M54 64 H146 L100 108Z", shadow=False, spot=True)
    d.shape("near", ellipse(110, 76, 10, 8))
    d.marks("pop", circle(114, 74, 3.4))
    d.stroke("light", "M60 62 L94 100", 2.2, line=False)
    d.limb("light", "M100 114 V158", 4.5, shadow=False)
    d.shape("light", ellipse(100, 160, 26, 6))


def cocktail_shaker(d: Drawing):
    d.disc("glow", 100, 96, 60, line=False)
    table(d, 160, "far", "mid")
    def sh():
        d.shape("hero2", "M62 80 L70 150 H110 L118 80Z", spot=True)
        d.shape("hero2", rrect(58, 72, 64, 10, 4))
        d.shape("hero2", "M68 72 L74 52 H106 L112 72Z")
        d.shape("hero2", rrect(82, 40, 16, 14, 4))
        d.stroke("light", "M70 88 L76 142", 3, line=False)
    group(d, "rotate(-44 90 100)", sh)
    d.stroke("pop", "M126 60 Q140 76 138 112", 3.4)
    # coupe glass
    d.shape("light", "M110 112 H166 C166 132 152 140 138 140 C124 140 110 132 110 112Z")
    d.shape("pop", "M113 118 H163 C161 130 150 136 138 136 C126 136 115 130 113 118Z", shadow=False, spot=True)
    d.limb("light", "M138 140 V160", 3.4, shadow=False)
    d.shape("light", ellipse(138, 161, 14, 3.5))
    d.shape("hero", ellipse(160, 112, 9, 9))
    d.shape("light", ellipse(160, 112, 6, 6), shadow=False, line=False)


def cocktail_bar(d: Drawing):
    d.band("deep", "M-30 -30 L230 -30", line=False)
    # shelves of bottles
    for y in [80, 120]:
        d.shape("mid", rrect(10, y, 180, 5, 1))
    bottles = [(30, 80, "hero"), (48, 80, "pop"), (66, 80, "far"), (134, 80, "hero2"), (152, 80, "light"), (170, 80, "pop"),
               (24, 120, "hero2"), (42, 120, "far"), (60, 120, "hero"), (140, 120, "pop"), (158, 120, "hero"), (176, 120, "hero2")]
    for i, (x, y, role) in enumerate(bottles):
        h = 28 + (i * 7) % 10
        d.shape(role, f"M{x-6} {y} V{y-h+12} C{x-6} {y-h+6} {x-2} {y-h+6} {x-2} {y-h} H{x+2} C{x+2} {y-h+6} {x+6} {y-h+6} {x+6} {y-h+12} V{y}Z", line=i % 3 != 1)
    # pendant lamps
    for x in [100]:
        d.stroke("light", f"M{x} -10 V34", 1.6)
        d.shape("glow2", f"M{x-14} 48 C{x-14} 36 {x+14} 36 {x+14} 48Z", spot=True)
    # counter
    d.band("ground", "M-30 150 L230 150")
    d.band("near", "M-30 160 L230 160", line=False)
    # cocktail on the bar
    d.shape("light", "M78 90 H122 L100 116Z")
    d.shape("pop", "M84 94 H116 L100 112Z", shadow=False, spot=True)
    d.limb("light", "M100 114 V146", 3.4, shadow=False)
    d.shape("light", ellipse(100, 148, 16, 3.5))
    d.shape("hero2", ellipse(116, 92, 7, 7))


# ================================================================ ROOFTOP BAR
SKYLINE = ("M-30 150 V108 H6 V84 H22 V100 H34 V70 H50 V96 H62 V60 H70 V50 H76 V60 H84 V100 H98 V80 H112 V104 H124 "
           "V66 H140 V92 H152 V78 H166 V100 H180 V86 H196 V110 H230 V150Z")


def roof_glass(d: Drawing):
    d.disc("glow", 136, 96, 30)
    d.shape("far", SKYLINE)
    for x, y in [(40, 80), (40, 90), (66, 68), (66, 80), (130, 76), (130, 86), (156, 90), (102, 90)]:
        d.marks("light", rrect(x, y, 4, 5, 0.5))
    d.band("near", "M-30 142 L230 142")
    d.band("deep", "M-30 152 L230 152", line=False)
    # coupe on the ledge
    d.shape("light", "M50 92 H118 C118 116 102 126 84 126 C66 126 50 116 50 92Z")
    d.shape("pop", "M53 99 H115 C113 114 100 121 84 121 C68 121 55 114 53 99Z", shadow=False, spot=True)
    d.limb("light", "M84 126 V140", 3.6, shadow=False)
    d.shape("light", ellipse(84, 141, 16, 3.5))
    d.shape("hero2", circle(112, 92, 11))
    d.shape("light", circle(112, 92, 8), shadow=False, line=False)
    d.shape("hero2", circle(112, 92, 6.5), shadow=False, line=False)
    d.stroke("dark", "M76 96 L62 56", 2.4)
    d.shape("hero", "M48 62 Q62 40 80 50 Z")


def roof_lights(d: Drawing):
    d.disc("glow", 150, 46, 13)
    d.shape("far", SKYLINE, extra='transform="translate(0 18)"')
    for x, y in [(40, 98), (40, 108), (66, 86), (66, 98), (130, 94), (156, 108), (102, 108), (186, 112)]:
        d.marks("glow2", rrect(x, y, 4, 5, 0.5))
    # string lights
    for (y0, sag) in [(30, 34), (62, 26)]:
        d.stroke("dark", f"M-10 {y0} Q100 {y0+sag*2} 210 {y0}", 1.4)
        for i in range(1, 8):
            t = i / 8
            x = (1 - t) ** 2 * -10 + 2 * (1 - t) * t * 100 + t * t * 210
            y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * (y0 + sag * 2) + t * t * y0
            d.disc("glow2", round(x, 1), round(y + 5, 1), 4.2)
    # terrace railing and floor
    d.band("mid", "M-30 160 L230 160")
    d.stroke("dark", "M-10 132 H210", 3.4)
    for x in range(14, 200, 16):
        d.stroke("dark", f"M{x} 132 V160", 2)
    # a little bar table with drinks
    d.stroke("dark", "M100 136 V166", 3.4)
    d.shape("hero", ellipse(100, 134, 26, 5))
    d.shape("pop", "M86 118 H98 L96 132 H88Z", spot=True)
    d.shape("hero2", "M104 120 H116 L110 128 V132 H108 V128Z")


def roof_tower(d: Drawing):
    for x, y in [(36, 46), (60, 30), (150, 36), (170, 64), (44, 78), (126, 22)]:
        d.marks("light", circle(x, y, 1.6))
    d.shape("light", "M148 52 a14 14 0 1 0 12 -22 a11 11 0 1 1 -12 22Z")
    d.band("far", "M-30 200 V128 H20 V112 H40 V136 H160 V104 H180 V124 H230 V200")
    # tower
    d.shape("mid", "M70 92 H130 V200 H70Z")
    for y in range(104, 200, 14):
        for x in [78, 92, 106, 120]:
            d.marks("glow2" if (x + y) % 3 else "near", rrect(x, y, 6, 7, 1))
    # roof deck
    d.shape("dark", rrect(60, 84, 80, 8, 2))
    d.stroke("light", "M62 84 V74 H138 V84", 1.6)
    for x in [80, 120]:
        d.stroke("dark", f"M{x} 84 V60", 1.8)
        d.shape("pop", f"M{x-16} 62 Q{x} 46 {x+16} 62Z", spot=True)
    d.shape("glow2", circle(100, 78, 4), shadow=False)


# ================================================================ COCONUT ON THE BEACH
def coco_straw(d: Drawing):
    d.disc("glow", 46, 56, 18)
    beach(d, 104, 134)
    d.shape("dark", ellipse(104, 160, 40, 6), shadow=False, line=False, extra='opacity=".18"')
    # straw and umbrella
    d.limb("pop", "M108 92 L132 40 L146 36", 4.5, spot=True)
    d.stroke("dark", "M86 96 L78 52", 2)
    d.shape("hero2", "M56 58 Q78 30 100 50 Z")
    # coconut
    d.shape("hero", "M60 110 C56 86 74 80 100 80 C126 80 144 86 140 110 C138 140 122 160 100 160 C78 160 62 140 60 110Z", spot=True)
    d.shape("light", ellipse(100, 86, 30, 8), shadow=False)
    d.shape("mark", ellipse(100, 86, 30, 8), shadow=False, line=False, extra='opacity="0"')
    d.stroke("mark", "M70 104 Q74 132 92 152 M130 104 Q126 132 110 152", 2, line=False)


def coco_palm(d: Drawing):
    d.disc("glow", 132, 100, 32)
    d.band("far", waves(126, 3, 22))
    d.band("mid", waves(138, 3, 26), line=False)
    d.band("ground", "M-30 160 Q40 146 100 152 T230 160")
    d.limb("dark", "M44 172 Q48 112 94 66", 8)
    for a in ["M94 62 C112 42 146 40 168 60 C150 58 136 58 122 62 C110 64 100 66 94 62Z",
              "M94 62 C80 44 52 38 30 52 C50 52 64 56 74 62 C82 66 90 66 94 62Z",
              "M94 62 C120 60 148 76 156 104 C142 88 126 80 112 74 C102 70 96 66 94 62Z",
              "M94 62 C70 58 46 70 38 96 C52 82 66 74 80 70 C88 68 92 66 94 62Z",
              "M94 62 C100 40 120 24 144 22 C128 32 116 42 108 52 C102 58 98 62 94 62Z"]:
        d.shape("hero", a, spot=a.startswith("M94 62 C120"))
    for x, y in [(88, 72), (102, 74), (94, 84)]:
        d.shape("hero2", circle(x, y, 8))
        d.marks("dark", circle(x - 2, y - 2, 1.4))


def coco_halves(d: Drawing):
    d.disc("glow", 100, 92, 58, line=False)
    d.band("ground", "M-30 148 Q100 138 230 148")
    # half facing us
    d.shape("hero", ellipse(74, 112, 38, 35))
    d.shape("light", ellipse(74, 112, 30, 27), shadow=False)
    d.shape("sky2", ellipse(74, 112, 21, 18), shadow=False, line=False)
    d.stroke("mark", "M40 96 l6 2 M38 116 l6 0 M46 136 l5 -3 M106 128 l-5 -2", 1.6, line=False)
    # half lying open like a bowl
    d.shape("hero", "M116 122 C116 150 172 154 178 124Z")
    d.shape("light", ellipse(147, 122, 32, 9), extra='transform="rotate(-3 147 122)"')
    d.shape("sky2", ellipse(147, 122, 24, 5.5), extra='transform="rotate(-3 147 122)"', shadow=False, line=False)
    d.stroke("mark", "M126 134 l5 -1 M150 144 l1 -5 M168 134 l-4 -2", 1.6, line=False)
    # hibiscus
    for a in range(0, 360, 72):
        d.shape("pop", ellipse(148, 52, 9, 14), extra=f'transform="rotate({a} 148 64)"', spot=True, shadow=a == 0)
    d.shape("hero2", circle(148, 64, 4), shadow=False)
    d.stroke("hero2", "M148 64 L162 52", 1.6)


WOOD = {"ground": "#C68B59", "near": "#9A6338"}
WOOD = {"ground": "#C68B59", "near": "#9A6338"}
WOOD = {"ground": "#C68B59", "near": "#9A6338"}
WOOD = {"ground": "#C68B59", "near": "#9A6338"}
PINK_STEAM = {}
CONCEPTS = [
    # street food
    Concept("sfood-cart", "street-food-tour", "Street food cart", sfood_cart, checks=[("hero", "ground"), ("hero", "far"), ("pop", "near"), ("light", "near")],
            fixes={"near": ["deep", "dark"], "hero": ["pop", "deep"]}),
    Concept("sfood-skewers", "street-food-tour", "Grill skewers", sfood_skewers,
            overrides={"hero": "#A0522D", "hero2": "#7FB069", "mark": "#5A2E1A"},
            checks=[("hero", "glow"), ("light", "glow")], fixes={"glow": ["near", "mid", "deep"]}),
    Concept("sfood-dumplings", "street-food-tour", "Dumpling steamer", sfood_dumplings,
            overrides={"hero": "#E0B36A", "hero2": "#B98A45", "mark": "#8A6430", **WOOD},
            checks=[("light", "glow"), ("hero", "near")], fixes={"glow": ["mid", "near", "deep"]}),
    # cooking class
    Concept("cook-hat", "cooking-class", "Chef's hat", cook_hat, overrides={"ground": "#C68B59", "hero2": "#D9DCE3"},
            checks=[("light", "hero"), ("hero", "sky"), ("ground", "hero")], fixes={"hero": ["near", "deep", "mid"]}),
    Concept("cook-pot", "cooking-class", "Pot on the stove", cook_pot, overrides={"ground": "#C68B59", "pop": "#4AA3DF"},
            checks=[("hero", "glow"), ("light", "glow"), ("hero", "far")], fixes={"glow": ["near", "mid", "deep"], "hero": ["pop", "deep", "dark"]}),
    Concept("cook-board", "cooking-class", "Chopping board", cook_board,
            overrides={"ground": "#D9A066", "pop": "#E63946", "hero": "#4C9A2A", "hero2": "#F08A24", "glow2": "#FFD08A"},
            checks=[("ground", "far"), ("pop", "glow")], fixes={"far": ["mid", "near", "deep"]}),
    # wine tasting
    Concept("wine-vineyard", "wine-tasting", "Glasses & vineyard", wine_vineyard, overrides={"pop": "#8E1B3A"},
            checks=[("light", "far"), ("light", "mid"), ("light", "sky")], fixes={"sky": ["sky2", "far"]}),
    Concept("wine-grapes", "wine-tasting", "Bunch of grapes", wine_grapes, overrides={"hero": "#6A994E", "hero2": "#6B3F7A", "mark": "#3E6B2E"},
            checks=[("hero2", "glow"), ("hero", "glow")], fixes={"glow": ["glow2", "far", "light"]}),
    Concept("wine-barrel", "wine-tasting", "Barrel & bottle", wine_barrel,
            overrides={"hero": "#B07A4A", "hero2": "#C99366", "pop": "#8E1B3A", "deep": "#2F4A3A"},
            checks=[("hero", "sky"), ("deep", "sky"), ("hero", "far")], fixes={"far": ["near", "deep", "dark"]}),
    # fine dining
    Concept("dine-cloche", "fine-dining", "Silver cloche", dine_cloche, overrides={"hero2": "#B9C0CB"},
            checks=[("hero2", "glow"), ("light", "hero")], fixes={"glow": ["near", "mid", "deep"]}),
    Concept("dine-setting", "fine-dining", "Place setting", dine_setting, overrides={"pop": "#8E1B3A"},
            checks=[("light", "hero"), ("pop", "sky")], fixes={"hero": ["near", "deep", "mid"]}),
    Concept("dine-candles", "fine-dining", "Candlelit dinner", dine_candles, overrides={"hero2": "#D4A84B", "pop": "#FF8A3D", "mark": "#8E1B3A", "glow2": "#FFD98A"},
            checks=[("light", "far"), ("glow2", "far"), ("hero2", "light"), ("mark", "far")], fixes={"far": ["near", "deep", "dark"]}),
    # seafood feast
    Concept("sea-crab", "seafood-feast", "Crab platter", sea_crab, overrides={"hero": "#E4572E", "hero2": "#F6D743", "mark": "#B23A1E"},
            checks=[("hero", "glow"), ("hero", "far"), ("hero", "light")], fixes={"glow": ["glow2", "far", "light", "sky2"], "far": ["mid", "near", "deep"]}),
    Concept("sea-oysters", "seafood-feast", "Oysters on ice", sea_oysters,
            overrides={"hero": "#8E8A99", "hero2": "#EFE6D8", "mark": "#D9CBB4", "pop": "#F6D743"},
            checks=[("light", "near"), ("hero", "light")], fixes={"near": ["deep", "dark", "mid"]}),
    Concept("sea-fish", "seafood-feast", "Grilled fish", sea_fish,
            overrides={"hero": "#D08C4A", "hero2": "#EBC48A", "mark": "#5A3A22", "pop": "#F6D743", "near": "#5E9C6A"},
            checks=[("light", "far"), ("hero", "sky2"), ("far", "sky")], fixes={"far": ["mid", "near", "deep", "dark"]}),
    # beach bbq
    Concept("bbq-grill", "beach-bbq", "Grill on the beach", bbq_grill, overrides={"pop": "#B5452E", "near": "#4F9A5E"},
            checks=[("hero", "ground"), ("hero", "far"), ("light", "sky"), ("hero", "sky")], fixes={"hero": ["deep", "dark", "pop"], "sky": ["sky2", "far"]}),
    Concept("bbq-bonfire", "beach-bbq", "Beach bonfire", bbq_bonfire, overrides={"pop": "#FF7B3A", "glow2": "#FFD25E", "dark": "#4A3426", "hero": "#B5452E"},
            checks=[("pop", "far"), ("pop", "ground"), ("hero", "sky")], palettes=["dusk", "coastal", "golden", "blush"], fixes={"far": ["deep", "near"]}),
    Concept("bbq-corn", "beach-bbq", "Grilled corn", bbq_corn, overrides={"hero": "#8DBF5A", "hero2": "#F6C945", "mark": "#D9A520"},
            checks=[("hero2", "glow"), ("hero", "glow")], fixes={"glow": ["near", "deep", "mid", "dark"]}),
    # ramen
    Concept("ramen-bowl", "ramen", "Steaming ramen", ramen_bowl, overrides={"pop": "#E8B04B", "hero2": "#F6DFA0", "mark": "#B5651D"},
            checks=[("hero", "glow"), ("light", "glow"), ("hero", "far")], fixes={"glow": ["near", "deep", "mid"]}),
    Concept("ramen-top", "ramen", "Ramen from above", ramen_top,
            overrides={"pop": "#E8B04B", "hero2": "#F6A623", "deep": "#B5734A", "near": "#4C9A2A", "dark": "#1F3B2C"},
            checks=[("light", "hero")], fixes={"hero": ["near", "deep", "mid"]}),
    Concept("ramen-shop", "ramen", "Ramen shop", ramen_shop, overrides={"pop": "#E4572E"},
            checks=[("hero", "glow2"), ("near", "far"), ("pop", "near")], fixes={"hero": ["deep", "dark", "pop"], "far": ["sky", "sky2"]}),
    # sushi
    Concept("sushi-board", "sushi", "Sushi board", sushi_board,
            overrides={"hero": "#F4845F", "pop": "#C8102E", "hero2": "#8DBF5A", "glow2": "#F7B7A3", **WOOD},
            checks=[("ground", "far"), ("glow", "sky")], fixes={"far": ["mid", "deep", "dark"], "glow": ["glow2", "far"]}),
    Concept("sushi-maki", "sushi", "Maki rolls", sushi_maki, overrides={"hero": "#F4845F", "hero2": "#8DBF5A", "near": "#F6C945", "dark": "#1F2E26"},
            checks=[("dark", "glow")], fixes={"glow": ["glow2", "far", "sky2"]}),
    Concept("sushi-nigiri", "sushi", "Salmon nigiri", sushi_nigiri, overrides={"hero": "#F4845F"},
            checks=[("hero", "glow"), ("light", "glow")], fixes={"glow": ["near", "deep", "mid"]}),
    # pizza
    Concept("pizza-oven", "pizza", "Wood-fired oven", pizza_oven,
            overrides={"hero": "#C8643B", "hero2": "#E39B6B", "pop": "#FF7B3A", "glow2": "#FFD25E", "ground": "#C68B59", "near": "#8A5A3B"},
            checks=[("hero", "sky"), ("hero", "mid"), ("mid", "ground")], fixes={"mid": ["far", "deep", "light"], "ground": ["far", "deep"]}),
    Concept("pizza-whole", "pizza", "Pizza & gingham", pizza_whole,
            overrides={"ground": "#E0A458", "mark": "#C8432B", "hero2": "#F7D17A", "pop": "#B5302A", "near": "#3F8A3A"},
            checks=[("ground", "light"), ("ground", "hero")], fixes={"hero": ["pop", "deep", "near"]}),
    Concept("pizza-slice", "pizza", "Cheesy slice", pizza_slice,
            overrides={"ground": "#E0A458", "hero2": "#F7D17A", "pop": "#B5302A", "near": "#3F8A3A"},
            checks=[("hero2", "glow"), ("ground", "glow")], fixes={"glow": ["#E07A5F", "mid", "deep"]}),
    # curry
    Concept("curry-plate", "curry", "Curry & rice", curry_plate,
            overrides={"hero2": "#D9822B", "glow2": "#FFF8E8", "pop": "#F2C46D", "mark": "#8B4A2B", "near": "#4C9A2A", "ground": "#E6D8B8", "sky": "#FFFFFF"},
            checks=[("light", "hero")], fixes={"hero": ["near", "deep", "mid"]}),
    Concept("curry-pot", "curry", "Copper pot & naan", curry_pot,
            overrides={"hero": "#B8643A", "hero2": "#D98A5A", "pop": "#E08A2E", "mark": "#8B4A2B", "glow2": "#EBC27C", "near": "#9A6338"},
            checks=[("hero", "glow"), ("light", "glow"), ("glow2", "glow"), ("hero", "far")], fixes={"glow": ["mid", "deep", "#E07A5F"], "far": ["mid", "deep"]}),
    Concept("curry-spices", "curry", "Spice market", curry_spices,
            overrides={"hero": "#C9A46E", "hero2": "#A9824F", "glow2": "#F2B705", "pop": "#D7263D", "mark": "#8C5A2B", "near": "#3F8A3A", "dark": "#5A3A22"},
            checks=[("hero", "glow"), ("hero", "ground"), ("pop", "glow"), ("mark", "glow"), ("glow2", "glow")], fixes={"glow": ["far", "light", "#E07A5F", "deep"], "ground": ["far", "mid", "deep"]}),
    # tacos
    Concept("taco-big", "tacos", "Loaded taco", taco_big,
            overrides={"hero": "#F2C14E", "hero2": "#D99A2B", "near": "#6FAE3A", "mark": "#8B4A2B", "pop": "#E63946"},
            checks=[("hero", "glow"), ("hero", "far")], fixes={"glow": ["#E07A5F", "mid", "deep"], "far": ["mid", "deep"]}),
    Concept("taco-truck", "tacos", "Taco truck", taco_truck,
            overrides={"pop": "#E63946"},
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "ground")], fixes={"hero": ["deep", "near", "pop"]}),
    Concept("taco-fiesta", "tacos", "Taco fiesta", taco_fiesta,
            overrides={"hero": "#F2C14E", "hero2": "#D99A2B", "near": "#6FAE3A", "mark": "#8B4A2B", "pop": "#E63946"},
            checks=[("hero", "glow"), ("light", "glow")], fixes={"glow": ["#E07A5F", "mid", "deep"]}),
    # gelato
    Concept("gelato-cone", "gelato", "Triple scoop", gelato_cone,
            overrides={"hero": "#A8D08D", "hero2": "#F7A1B5", "far": "#7B4B2A", "ground": "#D9A066", "near": "#A8743F", "pop": "#D7263D"},
            checks=[("hero", "glow"), ("hero2", "glow"), ("ground", "sky")], fixes={"glow": ["near", "deep", "mid", "dark"]}),
    Concept("gelato-cup", "gelato", "Gelato cup", gelato_cup,
            overrides={"hero": "#F7A1B5", "hero2": "#A8D08D", "ground": "#D9A066", "near": "#A8743F"},
            checks=[("hero", "glow"), ("hero2", "glow"), ("light", "glow")], fixes={"glow": ["near", "deep", "mid", "dark"]}),
    Concept("gelato-counter", "gelato", "Gelateria", gelato_counter,
            overrides={"hero": "#F7A1B5", "hero2": "#A8D08D", "mark": "#7B4B2A", "near": "#F6C945", "light": "#FFF6E0"},
            checks=[("light", "far"), ("hero", "far"), ("mark", "far"), ("ground", "far")], fixes={"far": ["deep", "dark", "mid"]}),
    # cafe & croissant
    Concept("cafe-croissant", "cafe-and-croissant", "Golden croissant", cafe_croissant,
            overrides={"hero": "#E2A04A", "hero2": "#F5C77E", "mark": "#A8642A"},
            checks=[("hero", "glow"), ("hero", "light"), ("light", "far")], fixes={"glow": ["#F1E6CF", "mid", "deep"], "far": ["mid", "deep"]}),
    Concept("cafe-cup", "cafe-and-croissant", "Latte & croissant", cafe_cup,
            overrides={"hero": "#E2A04A", "hero2": "#F1D9B5", "mark": "#6F4E37"},
            checks=[("light", "glow"), ("light", "far"), ("hero", "far")], fixes={"glow": ["mid", "#E07A5F", "deep"], "far": ["mid", "deep"]}),
    Concept("cafe-bistro", "cafe-and-croissant", "Bistro table", cafe_bistro,
            overrides={"hero": "#E2A04A", "hero2": "#F5C77E"},
            checks=[("hero", "sky"), ("light", "sky"), ("sky", "far"), ("dark", "sky")], fixes={"far": ["mid", "near", "deep"], "sky": ["sky2", "glow2"]}),
    # cocktail bar
    Concept("cocktail-martini", "cocktail-bar", "Martini & olive", cocktail_martini,
            overrides={"hero": "#C8D78E", "near": "#5E7F1E", "pop": "#D7263D"},
            checks=[("light", "glow"), ("hero", "light")], fixes={"glow": ["mid", "near", "deep", "#E07A5F"]}),
    Concept("cocktail-shaker", "cocktail-bar", "Shaker & coupe", cocktail_shaker,
            overrides={"hero2": "#C9CED6", "hero": "#F6C945"},
            checks=[("hero2", "glow"), ("light", "glow"), ("pop", "glow")], fixes={"glow": ["mid", "near", "deep"]}),
    Concept("cocktail-bar", "cocktail-bar", "Back bar", cocktail_bar,
            checks=[("light", "deep"), ("pop", "deep"), ("hero", "deep"), ("ground", "deep")], fixes={"deep": ["dark", "mark", "near"]}),
    # rooftop bar
    Concept("roof-glass", "rooftop-bar", "Skyline cocktail", roof_glass, overrides={"pop": "#F28F3B", "hero2": "#F6D743"},
            checks=[("light", "far"), ("light", "sky"), ("far", "sky"), ("pop", "far")], fixes={"far": ["mid", "near", "deep"], "sky": ["sky2", "glow2"]}),
    Concept("roof-lights", "rooftop-bar", "String lights", roof_lights, palettes=["dusk", "blush", "coastal", "golden"],
            overrides={"glow2": "#FFD98A"}, checks=[("glow2", "sky"), ("far", "sky"), ("dark", "sky")], fixes={"sky": ["deep", "near", "dark"]}),
    Concept("roof-tower", "rooftop-bar", "Sky bar", roof_tower, palettes=["dusk", "blush", "coastal", "golden", "meadow"],
            overrides={"glow2": "#FFD98A"}, checks=[("light", "sky"), ("mid", "sky"), ("mid", "far")], fixes={"sky": ["deep", "dark", "mark"], "far": ["near", "deep"]}),
    # coconut on the beach
    Concept("coco-straw", "coconut-on-the-beach", "Coconut & straw", coco_straw,
            overrides={"hero": "#7CB342", "mark": "#4E7D23", "light": "#FFF6E0"},
            checks=[("hero", "ground"), ("hero", "far"), ("hero", "mid"), ("hero", "sky")], fixes={"mid": ["near", "deep"], "far": ["near", "deep"]}),
    Concept("coco-palm", "coconut-on-the-beach", "Palm & coconuts", coco_palm,
            overrides={"hero": "#4F9A5E", "hero2": "#7B5032", "dark": "#6B4A2E"},
            checks=[("hero", "sky"), ("hero", "glow"), ("hero", "far")], fixes={"glow": ["#E07A5F", "glow2", "light"], "far": ["mid", "near", "deep"]}),
    Concept("coco-halves", "coconut-on-the-beach", "Cracked coconut", coco_halves,
            overrides={"hero": "#7B5032", "mark": "#4E3420", "pop": "#E84A6B", "hero2": "#F6D743", "light": "#FFFBF2"},
            checks=[("hero", "glow"), ("hero", "ground"), ("pop", "glow")], fixes={"glow": ["glow2", "far", "light"]}),
]
