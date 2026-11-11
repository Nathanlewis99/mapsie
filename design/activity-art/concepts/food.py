"""Food & drink: three concepts each for sixteen eating and drinking activities."""
from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group


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
    d.shape("dark", "M44 64 L100 46 L156 64Z")
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
    # crossed spoon and whisk behind
    d.limb("ground", "M42 160 L118 74", 6)
    d.shape("ground", ellipse(126, 64, 10, 15), extra='transform="rotate(42 126 64)"')
    d.limb("dark", "M158 160 L96 86", 5)
    d.stroke("light", "M96 86 C70 70 66 42 82 36 C98 30 104 60 96 86 M96 86 C84 60 96 30 112 38 C126 46 116 72 96 86", 2.4)
    # toque
    d.shape("light", "M64 108 C46 104 42 76 60 70 C62 50 86 44 98 54 C110 42 136 48 138 68 C158 70 158 104 136 108Z")
    d.stroke("hero2", "M80 104 Q78 86 84 76 M100 104 V74 M120 104 Q122 86 116 76", 2, line=False)
    d.shape("light", rrect(62, 106, 76, 26, 5))
    d.stroke("hero2", "M68 114 H132", 2.2, line=False)


def cook_pot(d: Drawing):
    d.disc("glow", 100, 76, 50)
    table(d, 150, "far", "mid")
    steam(d, [80, 100, 120], 78, 30)
    d.limb("ground", "M126 96 L156 46", 5)
    d.shape("ground", ellipse(160, 40, 7, 10), extra='transform="rotate(30 160 40)"')
    d.shape("dark", rrect(44, 96, 112, 8, 3))
    d.shape("hero", "M50 102 H150 V128 C150 142 140 148 128 148 H72 C60 148 50 142 50 128Z", spot=True)
    d.shape("hero2", "M50 112 H150 V118 H50Z", shadow=False)
    d.limb("dark", "M48 108 H34 M152 108 H166", 6)
    # burner with flames
    d.shape("dark", rrect(56, 150, 88, 8, 3))
    for x in [66, 80, 94, 108, 122, 136]:
        d.shape("pop", f"M{x-4} 150 Q{x-4} 144 {x} 141 Q{x+4} 144 {x+4} 150Z", shadow=False)


def cook_board(d: Drawing):
    d.disc("glow", 140, 58, 30)
    table(d, 120, "far", "mid", 14)
    # board
    d.shape("ground", rrect(30, 104, 140, 52, 8))
    d.shape("ground", circle(160, 116, 0.1), shadow=False, line=False)
    d.marks("dark", circle(154, 114, 3.5))
    d.stroke("hero2", "M40 146 H160", 1.6, line=False)
    # knife
    d.shape("light", "M78 128 L152 112 L156 118 C130 130 100 134 82 134Z", spot=False)
    d.shape("dark", rrect(40, 128, 40, 10, 4), extra='transform="rotate(-8 60 133)"')
    # carrot slices and tomato
    for x, y in [(52, 116), (64, 112), (76, 108)]:
        d.shape("hero2", circle(x, y, 6.5))
        d.marks("glow2", circle(x, y, 2.4))
    d.shape("pop", circle(108, 90, 22), spot=True)
    d.shape("hero", "M108 72 l-9 -4 l6 7 l-10 2 l10 3 l3 -1 l3 1 l10 -3 l-10 -2 l6 -7Z", shadow=False)
    d.stroke("hero", "M108 72 V64", 2.4)
    d.shape("light", ellipse(98, 84, 4, 6), shadow=False, line=False)
    # carrot
    d.shape("hero2", "M128 102 L174 84 C178 84 180 90 176 92 Z", spot=True)
    d.shape("hero", "M174 86 l10 -10 M174 86 l14 -2 M174 86 l8 -14", extra="")
    d.stroke("hero", "M174 87 l10 -10 M174 87 l13 -3 M174 87 l7 -13", 3)
    d.stroke("mark", "M140 98 l3 4 M152 93 l3 4 M162 89 l2 3", 1.4)


# ================================================================ WINE TASTING
def wine_glass(d: Drawing, x, y, s=1.0, rot=0):
    def g():
        d.shape("light", f"M{x-16} {y-30} H{x+16} C{x+18} {y-10} {x+12} {y+6} {x} {y+8} C{x-12} {y+6} {x-18} {y-10} {x-16} {y-30}Z")
        d.shape("pop", f"M{x-17} {y-14} H{x+17} C{x+15} {y-2} {x+10} {y+6} {x} {y+7} C{x-10} {y+6} {x-15} {y-2} {x-17} {y-14}Z", shadow=False, spot=True)
        d.limb("light", f"M{x} {y+8} V{y+38}", 3.4, shadow=False)
        d.shape("light", ellipse(x, y + 39, 13, 3.5))
        d.stroke("light", f"M{x-11} {y-26} Q{x-12} {y-18} {x-10} {y-12}", 2, line=False)
    group(d, f"rotate({rot} {x} {y+39})", g)


def wine_vineyard(d: Drawing):
    d.disc("glow", 100, 70, 30)
    d.band("far", hills(98, 12))
    d.band("mid", "M-30 112 Q100 96 230 116")
    for i, y in enumerate([118, 132, 148]):
        d.stroke("near", f"M-30 {y+8} Q100 {y-8} 230 {y+10}", 5 + i, line=i != 0)
    d.band("near", "M-30 170 Q100 160 230 170")
    wine_glass(d, 80, 108, rot=-10)
    wine_glass(d, 120, 108, rot=10)
    d.stroke("light", "M98 64 l-4 -6 M102 64 l4 -6 M100 62 V54", 2.2)


def wine_grapes(d: Drawing):
    d.disc("glow", 100, 100, 62)
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
    d.shape("sky", "M30 160 V84 C30 40 170 40 170 84 V160Z", line=False)
    d.band("ground", "M-30 160 L230 160")
    # barrel on its side
    d.shape("hero", ellipse(80, 112, 42, 42))
    d.shape("hero2", ellipse(80, 112, 34, 34), shadow=False)
    d.stroke("dark", "M54 112 H106 M58 96 H102 M58 128 H102 M66 82 H94 M66 142 H94", 1.6, line=False)
    d.stroke("dark", circle(80, 112, 38), 3.2)
    d.shape("dark", rrect(76, 132, 8, 8, 2), shadow=False)
    # bottle and glass
    d.shape("deep", "M132 160 V112 C132 102 140 98 142 92 V70 H150 V92 C152 98 160 102 160 112 V160Z", spot=False)
    d.shape("pop", rrect(134, 120, 24, 20, 2), shadow=False, spot=True)
    d.shape("light", rrect(141, 66, 10, 6, 1), shadow=False)
    wine_glass(d, 108, 118, 0.6)


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
    d.limb("light", "M36 70 V150", 5)
    d.stroke("light", "M30 54 V70 M36 54 V70 M42 54 V70 M30 70 Q36 76 42 70", 3)
    # knife
    d.limb("light", "M164 100 V150", 5)
    d.shape("light", "M160 102 V60 C168 66 170 84 168 102Z")
    # glass
    d.shape("light", circle(160, 42, 12))
    d.shape("pop", circle(160, 42, 8), shadow=False, spot=True)


def dine_candles(d: Drawing):
    d.band("far", "M-30 -30 L230 -30", line=False)
    d.shape("sky", "M50 140 V70 C50 34 150 34 150 70 V140Z", line=False)
    d.stroke("far", "M100 38 V140 M50 90 H150", 3.4, line=False)
    d.disc("glow", 128, 64, 12)
    table(d, 140, "light", "hero")
    for x, h in [(56, 54), (144, 54)]:
        d.shape("light", rrect(x - 5, 140 - h - 16, 10, h - 8, 2))
        d.shape("hero2", f"M{x-12} 140 H{x+12} L{x+4} 128 V{140-24} H{x-4} V128Z", spot=True)
        d.shape("hero2", rrect(x - 9, 140 - 28, 18, 5, 2), shadow=False)
        d.shape("pop", f"M{x} {140-h-34} C{x+7} {140-h-24} {x+6} {140-h-16} {x} {140-h-16} C{x-6} {140-h-16} {x-7} {140-h-24} {x} {140-h-34}Z", shadow=False)
    wine_glass(d, 86, 100, rot=-6)
    wine_glass(d, 114, 100, rot=6)


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
    Concept("dine-candles", "fine-dining", "Candlelit dinner", dine_candles, overrides={"hero2": "#D4A84B", "pop": "#FF8A3D"},
            checks=[("light", "sky"), ("light", "far"), ("hero2", "light")], fixes={"far": ["near", "deep", "dark"], "sky": ["deep", "dark"]}),
]
