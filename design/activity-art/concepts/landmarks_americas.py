"""Mapsie Originals: famous landmarks of the Americas."""
from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group
import math


# ================================================================ private helpers
def poly(*pts, close=True) -> str:
    s = "M" + " L".join(f"{x:g} {y:g}" for x, y in pts)
    return s + ("Z" if close else "")


def pine(x: float, base: float, h: float, w: float | None = None) -> str:
    """A three-tier pine tree, base centred on (x, base)."""
    w = w or h * 0.55
    t = base - h
    return (f"M{x} {t} L{x + w*0.32} {t + h*0.32} L{x + w*0.2} {t + h*0.32} L{x + w*0.42} {t + h*0.62} "
            f"L{x + w*0.28} {t + h*0.62} L{x + w*0.5} {base - h*0.12} L{x - w*0.5} {base - h*0.12} "
            f"L{x - w*0.28} {t + h*0.62} L{x - w*0.42} {t + h*0.62} L{x - w*0.2} {t + h*0.32} L{x - w*0.32} {t + h*0.32}Z")


def birds(d: Drawing, pts, role="dark"):
    s = " ".join(f"M{x} {y} q{3 * k} {-3 * k} {6 * k} 0 q{3 * k} {-3 * k} {6 * k} 0" for x, y, k in pts)
    d.stroke(role, s, 1.7)


def stars(d: Drawing, pts, role="light"):
    for x, y, r in pts:
        d.marks(role, f"M{x} {y-r} L{x+r*0.3} {y-r*0.3} L{x+r} {y} L{x+r*0.3} {y+r*0.3} L{x} {y+r} "
                      f"L{x-r*0.3} {y+r*0.3} L{x-r} {y} L{x-r*0.3} {y-r*0.3}Z")


def palm(d: Drawing, x, base, h, lean=0, role="dark"):
    tx, ty = x + lean, base - h
    d.limb(role, f"M{x} {base} Q{x + lean * 0.2} {base - h * 0.5} {tx} {ty}", 3.2)
    for ang, ln in [(-160, 20), (-120, 17), (-60, 17), (-20, 20), (20, 15), (160, 15)]:
        a = math.radians(ang)
        ex, ey = tx + ln * math.cos(a), ty + ln * math.sin(a) + 6
        mx, my = tx + ln * 0.5 * math.cos(a), ty + ln * 0.5 * math.sin(a) - 4
        d.shape(role, f"M{tx} {ty} Q{mx:.1f} {my - 3:.1f} {ex:.1f} {ey:.1f} Q{mx:.1f} {my + 3:.1f} {tx} {ty}Z", shadow=False)


# ================================================================ GRAND CANYON
CANYON = {"haze": "#D8A49C", "pine": "#3F6B4A", "c1": "#E7B07A", "c2": "#D3814E", "c3": "#B4603B", "c4": "#8C432F", "c5": "#6A3127", "river": "#3F93B8", "river2": "#8FCBE0"}


def canyon_steps(d: Drawing, steps, side=1):
    """Stacked rock ledges stepping down into the canyon. steps: (role, top_y, edge_x), back to front.
    side=1 builds the left wall (ledges reach right to edge_x); side=-1 mirrors for the right wall."""
    for role, top, xe in steps:
        if side == 1:
            pts = [(-30, top), (xe - 5, top), (xe, top + 6), (xe + 3, 200), (-30, 200)]
        else:
            pts = [(230, top), (xe + 5, top), (xe, top + 6), (xe - 3, 200), (230, 200)]
        d.shape(role, poly(*pts))
        x0, x1 = (-30, xe - 2) if side == 1 else (xe + 2, 230)
        d.stroke("c5", f"M{x0} {top + 9} H{x1}", 1.6, line=False)


def canyon_sunset(d: Drawing):
    d.disc("glow", 100, 98, 30, line=False)
    d.raw("", f'<path d="M74 99 A26 26 0 0 1 126 99Z" fill="{d.c.get("spot", "")}"/>')
    birds(d, [(128, 46, 1), (142, 40, .8)])
    d.band("haze", "M-30 100 L24 99 L30 90 H48 L54 98 L148 98 L154 88 H170 L176 99 L230 100")
    d.band("c1", "M-30 114 L8 113 L14 104 H34 L40 112 L62 113 L68 102 L74 98 H92 L98 108 L118 110 L124 104 H138 L144 112 L230 112")
    d.stroke("c2", "M-30 120 H20 M70 108 H94 M60 120 H130 M150 118 H230", 1.8, line=False)
    d.band("c2", "M-30 130 L30 128 L36 120 H58 L64 128 L130 128 L136 118 L142 116 H164 L170 126 L230 128")
    d.stroke("c3", "M-30 136 H60 M38 126 H58 M140 122 H164 M120 135 H230", 1.8, line=False)
    d.band("c3", "M-30 148 L20 146 L26 138 H44 L50 146 L150 146 L156 140 H176 L182 148 L230 148")
    d.shape("river", "M96 147 Q112 152 102 160 Q90 170 100 180 Q110 190 98 200 H124 Q134 188 122 178 Q112 168 120 160 Q128 152 108 147Z", spot=True)
    d.stroke("river2", "M108 156 Q98 164 104 172", 1.6, line=False)
    d.shape("c4", poly((-30, 152), (30, 150), (38, 158), (60, 160), (68, 170), (84, 174), (90, 200), (-30, 200)))
    d.shape("c4", poly((230, 150), (178, 150), (170, 160), (148, 162), (140, 172), (126, 176), (124, 200), (230, 200)))
    d.stroke("c5", "M-30 162 H34 M-30 178 H64 M230 160 H174 M230 178 H140", 2, line=False)
    d.band("c5", "M-30 190 Q20 184 60 188 Q80 192 90 196 L230 196", line=False)


def canyon_rim(d: Drawing):
    d.shape("light", cloud(20, 52, 1.0))
    d.shape("light", cloud(140, 40, 0.8))
    d.shape("far", "M-30 96 L60 96 L66 88 H92 L98 95 L140 95 L146 84 H166 L172 94 L230 96 V200 H-30Z")
    # buttes across the canyon
    d.shape("c1", poly((70, 200), (74, 118), (84, 116), (88, 106), (112, 106), (116, 116), (130, 118), (136, 200)))
    d.shape("c1", poly((150, 200), (154, 112), (164, 110), (168, 100), (196, 100), (198, 108), (230, 110), (230, 200)))
    d.stroke("c2", "M76 126 H132 M86 112 H114 M156 120 H230 M168 106 H196", 2.2, line=False)
    d.shape("c2", poly((60, 200), (66, 140), (80, 138), (86, 130), (120, 130), (126, 138), (150, 140), (158, 132), (190, 132), (196, 140), (230, 142), (230, 200)))
    d.stroke("c3", "M68 150 H230 M88 136 H118 M160 138 H188", 2.4, line=False)
    d.shape("river", "M110 170 Q140 164 170 168 Q200 172 230 166 V176 Q200 182 170 178 Q140 174 110 178Z", spot=True)
    d.shape("c3", poly((60, 200), (70, 178), (110, 178), (140, 176), (160, 182), (200, 178), (230, 180), (230, 200)))
    # the rim we stand on
    d.shape("c4", poly((-30, 116), (40, 118), (70, 120), (86, 124), (84, 136), (90, 146), (84, 160), (92, 176), (88, 200), (-30, 200)))
    d.shape("c3", poly((-30, 116), (40, 118), (70, 120), (86, 124), (84, 130), (-30, 128)), shadow=False, line=False)
    d.stroke("c5", "M-30 146 H70 M-30 166 H74 M10 130 H60", 2.6, line=False)
    # lone pine on the rim, leaning out
    group(d, "rotate(8 44 120)", lambda: (d.limb("dark", "M44 121 V104", 4), d.shape("pine", pine(44, 110, 52, 30), spot=True)))
    # condor
    def condor():
        d.shape("dark", "M0 0 C-10 -4 -22 -4 -34 2 L-40 0 L-36 6 L-30 5 L-24 8 C-14 5 -6 4 0 4 C6 4 14 5 24 8 L30 5 L36 6 L40 0 L34 2 C22 -4 10 -4 0 0Z")
        d.shape("light", "M-6 3 C-12 4 -18 5 -24 7 C-16 4 -10 3 -6 3Z M6 3 C12 4 18 5 24 7 C16 4 10 3 6 3Z", shadow=False, line=False)
        d.shape("dark", "M-3 2 C-3 -2 3 -2 3 2 L2 8 L-2 8Z", shadow=False)
        d.marks("pop", circle(0, -2, 2.2))
    group(d, "translate(128 64) rotate(-6) scale(1.1)", condor)


# ================================================================ STATUE OF LIBERTY
COPPER = {"cu": "#7DBFA8", "cu2": "#4F8F7B", "stone": "#D8CCB8", "stone2": "#B5A68E", "gold": "#F2B33D", "water": "#5BA8C8"}


def liberty_torch(d: Drawing):
    d.disc("glow", 140, 70, 22)
    d.shape("light", cloud(150, 108, 0.8))
    # Manhattan, far across the harbour
    d.band("far", "M-30 150 H120 V138 H128 V130 H134 V140 H142 V122 H146 V112 H150 V122 H154 V134 H162 V126 H170 V140 H178 V132 H188 V146 H230")
    d.band("mid", waves(158, 3, 22))
    # pedestal on its star fort
    d.shape("stone2", poly((52, 178), (60, 168), (140, 168), (148, 178)))
    d.shape("stone", poly((78, 168), (82, 140), (118, 140), (122, 168)))
    d.shape("stone", rrect(77, 135, 46, 7, 1.5))
    d.shape("stone2", rrect(80, 130, 40, 6, 1.5))
    d.marks("stone2", rrect(94, 146, 12, 16, 1.5))
    # robe
    d.shape("cu", "M84 131 C86 112 86 96 89 84 Q93 78 100 78 Q108 78 112 84 C116 98 117 114 118 131Z")
    d.stroke("cu2", "M95 88 C94 104 92 118 92 130 M104 92 C106 106 108 118 110 130 M88 110 C94 108 100 112 112 104", 1.6)
    # raised right arm and torch
    d.limb("cu", "M93 84 L86 50", 7)
    d.shape("cu", poly((82, 46), (91, 46), (90, 54), (83, 54)), shadow=False)
    d.shape("gold", poly((79, 36), (94, 36), (90, 44), (83, 44)))
    d.shape("gold", "M86.5 18 C93 24 96 30 92 36 H81 C77 30 80 24 86.5 18Z", spot=True)
    # tablet in the left arm
    d.shape("cu2", "M108 88 L122 86 L124 112 L110 114Z")
    d.limb("cu", "M110 84 Q116 96 113 106", 6)
    # head and crown
    d.limb("cu", "M100 78 V72", 6)
    rays = []
    for i in range(7):
        a = math.radians(-162 + i * 24)
        cx, cy = 100, 64
        tip = (cx + 19 * math.cos(a), cy + 19 * math.sin(a))
        b1 = (cx + 7 * math.cos(a - .2), cy + 7 * math.sin(a - .2))
        b2 = (cx + 7 * math.cos(a + .2), cy + 7 * math.sin(a + .2))
        rays.append(f"M{b1[0]:.1f} {b1[1]:.1f} L{tip[0]:.1f} {tip[1]:.1f} L{b2[0]:.1f} {b2[1]:.1f}Z")
    d.shape("cu", " ".join(rays))
    d.shape("cu", circle(100, 66, 7.5))
    d.shape("cu2", "M92.5 63 Q100 58 107.5 63 L107 60 Q100 54 93 60Z", shadow=False)
    d.band("near", waves(174, 3, 26))
    d.band("deep", waves(186, 3, 30), line=False)


# ================================================================ GOLDEN GATE
BRIDGE = {"gg": "#C0362C", "gg2": "#8E2620"}


def gg_tower(d: Drawing, x, top, deck):
    legs = poly((x - 11, deck + 26), (x - 9, top), (x - 3, top), (x - 3, deck + 26)) + " " + \
        poly((x + 3, deck + 26), (x + 3, top), (x + 9, top), (x + 11, deck + 26))
    d.shape("gg", legs, spot=True)
    for i, y in enumerate([top + 3, top + 22, top + 40, top + 58]):
        d.shape("gg", rrect(x - 9.5, y, 19, 6 if i == 0 else 5, 1), shadow=False, spot=True)
    d.shape("gg", poly((x - 8, top), (x - 7, top - 6), (x - 4, top - 6), (x - 4, top)) + " " +
            poly((x + 4, top), (x + 4, top - 6), (x + 7, top - 6), (x + 8, top)), shadow=False, spot=True)
    d.marks("gg2", f"M{x - 3} {top + 9} H{x + 3} V{top + 22} H{x - 3}Z M{x - 3} {top + 28} H{x + 3} V{top + 40} H{x - 3}Z "
                   f"M{x - 3} {top + 46} H{x + 3} V{top + 58} H{x - 3}Z")


def goldengate_fog(d: Drawing):
    d.disc("glow", 100, 70, 18)
    d.band("far", "M-30 112 Q20 86 60 96 Q100 76 150 92 Q190 84 230 100")
    d.band("mid", waves(132, 3, 24))
    deck, top, xl, xr = 116, 36, 54, 146
    # main cable: quadratic between tower tops, side spans to the anchorages
    main_c = 176
    def cable_y(x):
        t = (x - xl) / (xr - xl)
        return (1 - t) ** 2 * top + 2 * (1 - t) * t * main_c + t * t * top
    hangers = " ".join(f"M{x} {cable_y(x):.1f} V{deck}" for x in range(xl + 8, xr - 4, 8))
    hangers += " " + " ".join(f"M{x} {top + (xl - x) * 1.6 + (xl - x) ** 2 * -0.004:.1f} V{deck}" for x in range(xl - 8, -10, -8) if top + (xl - x) * 1.6 < deck)
    d.stroke("gg2", hangers, 1, line=False)
    d.stroke("gg", f"M{xl} {top + 2} Q100 {main_c} {xr} {top + 2} M{xl} {top + 2} Q24 90 -30 112 M{xr} {top + 2} Q176 90 230 112", 2.6)
    gg_tower(d, xl, top, deck)
    gg_tower(d, xr, top, deck)
    d.shape("gg", rrect(-30, deck, 260, 7, 1), spot=True)
    d.stroke("gg2", "M-30 121 H230", 1.6, line=False)
    # fog rolling under the deck
    d.shape("light", "M-30 134 Q-10 124 10 130 Q24 120 44 128 Q60 122 72 130 Q90 124 104 132 Q122 122 140 130 Q158 122 172 130 Q196 120 230 130 V146 H-30Z")
    d.band("near", waves(150, 3, 26))
    d.band("deep", waves(170, 3, 30), line=False)
    d.stroke("light", "M30 158 h18 M120 162 h24", 2)


# ================================================================ EMPIRE STATE
ESB = {"tower": "#5D6B82", "tower2": "#3E4A5E"}


def empire_state(d: Drawing):
    d.disc("glow", 100, 96, 54)
    birds(d, [(150, 40, 1), (162, 34, .8)])
    # neighbouring blocks
    d.shape("far", "M18 200 V120 H40 V108 H52 V200Z M150 200 V112 H164 V96 H178 V200Z M186 200 V130 H200 V200Z")
    d.shape("mid", "M-30 200 V140 H24 V128 H50 V150 H64 V200Z M140 200 V136 H156 V124 H176 V146 H230 V200Z")
    x = 100
    # needle, mast, crown setbacks, shaft, base setbacks
    d.stroke("tower", f"M{x} 12 V30", 2)
    d.shape("tower", poly((x - 3, 44), (x - 2.5, 30), (x + 2.5, 30), (x + 3, 44)))
    d.shape("tower", rrect(x - 5, 42, 10, 6, 1.5))
    d.shape("tower", poly((x - 9, 60), (x - 9, 52), (x - 7, 48), (x + 7, 48), (x + 9, 52), (x + 9, 60)))
    d.shape("tower", rrect(x - 13, 58, 26, 8, 1))
    d.shape("tower", rrect(x - 17, 64, 34, 98, 1), spot=True)
    d.shape("tower2", poly((x + 4, 64), (x + 17, 64), (x + 17, 162), (x + 4, 162)), shadow=False, line=False)
    d.shape("tower", rrect(x - 24, 126, 48, 36, 1))
    d.shape("tower2", poly((x + 8, 126), (x + 24, 126), (x + 24, 162), (x + 8, 162)), shadow=False, line=False)
    d.shape("tower", rrect(x - 32, 146, 64, 40, 1))
    d.shape("tower2", poly((x + 12, 146), (x + 32, 146), (x + 32, 186), (x + 12, 186)), shadow=False, line=False)
    # vertical deco stripes and lit windows
    d.stroke("glow2", f"M{x - 11} 70 V158 M{x - 4} 70 V158 M{x + 4} 70 V158 M{x + 11} 70 V158", 1.4, line=False)
    d.stroke("glow2", f"M{x - 18} 132 V160 M{x + 18} 132 V160 M{x - 26} 152 V184 M{x - 18} 152 V184 M{x + 18} 152 V184 M{x + 26} 152 V184", 1.4, line=False)
    if not d.paper:
        d.stroke("dark", f"M{x - 6} 70 V158 M{x + 6} 70 V158 M{x - 12} 132 V160 M{x + 12} 132 V160 M{x - 20} 152 V184 M{x + 20} 152 V184", 1.4)
    d.marks("glow2", rrect(x - 3, 51, 6, 6, 1))
    d.band("near", "M-30 180 H230")


# ================================================================ MOUNT RUSHMORE
GRANITE = {"rock": "#C4BCAD", "rock2": "#A69E8F", "rock3": "#837B6E", "pine": "#3F6B4A"}


def head(d: Drawing, x, y, s=1.0, turn=1):
    """A carved granite face: (x, y) is the brow centre, turn=1 lit from the left."""
    def draw():
        d.shape("rock", "M-14 -18 C-14 -26 14 -26 14 -18 L15 6 C15 20 8 30 0 31 C-8 30 -15 20 -15 6Z")
        d.shape("rock2", f"M{6 * turn} -4 C{14 * turn} 0 {14 * turn} 14 {6 * turn} 30 C{12 * turn} 24 {15 * turn} 16 {15 * turn} 6 L{14 * turn} -18Z",
                shadow=False, line=False)
        d.shape("rock2", "M-13 -6 Q-6 -10 -1 -6 Q6 -10 13 -6 L13 -3 Q6 -6 -1 -3 Q-6 -6 -13 -3Z", shadow=False)
        d.marks("rock3", ellipse(-6.5, -1, 3.6, 2.2))
        d.marks("rock3", ellipse(6.5, -1, 3.6, 2.2))
        d.shape("rock2", f"M{-1 + turn} -4 L{2 * turn} 11 L{-3 * turn} 12 Z", shadow=False)
        d.stroke("rock3", "M-6 19 Q0 21 6 19", 1.6)
    group(d, f"translate({x} {y}) scale({s})", draw)


def rushmore_faces(d: Drawing):
    d.shape("light", cloud(150, 34, 0.8))
    d.shape("light", cloud(16, 44, 0.7))
    # the mountain, with shadowed recesses where the rock was cut back
    d.shape("rock", "M-30 200 V108 Q-6 70 20 70 Q40 50 70 52 Q100 40 130 52 Q160 50 184 74 Q208 82 230 102 V200Z")
    d.shape("rock2", "M24 92 Q22 120 30 136 H160 Q170 120 166 92 Q150 128 140 124 Q128 120 124 104 Q116 128 106 126 Q94 124 92 104 "
                     "Q84 120 74 120 Q62 120 58 98 Q50 130 40 128 Q30 124 24 92Z", shadow=False, line=False)
    d.shape("rock2", "M176 76 Q200 84 230 104 V140 H180 Q176 110 176 76Z", shadow=False, line=False)
    head(d, 44, 94, 1.05, 1)
    head(d, 76, 86, 0.95, 1)
    head(d, 110, 98, 0.85, -1)
    head(d, 148, 90, 1.1, -1)
    # rubble and pines
    d.shape("rock3", "M-30 200 V150 Q20 138 60 146 Q100 140 140 146 Q180 138 230 150 V200Z")
    for x, h in [(4, 34), (20, 44), (38, 32), (164, 36), (180, 46), (198, 34), (82, 28), (120, 30)]:
        d.shape("pine", pine(x, 176, h))
    d.band("deep", hills(178, 4), line=False)


# ================================================================ NIAGARA FALLS
FALLS = {"water": "#6CC1DD", "water2": "#E8F7FC", "boat": "#2F5D8A", "rain1": "#E5533D", "rain2": "#F2C14E", "rain3": "#4FA3D9"}


def niagara_horseshoe(d: Drawing):
    d.band("far", hills(84, 6))
    # rainbow
    if d.paper:
        for r, role in [(88, "rain1"), (83, "rain2"), (78, "rain3")]:
            d.stroke(role, f"M{100 - r} 150 A{r} {r} 0 0 1 {100 + r} 150", 5)
    else:
        d.stroke("dark", "M12 150 A88 88 0 0 1 188 150 M22 150 A78 78 0 0 1 178 150", 2)
    # the horseshoe: far crest curves away, near flanks come towards us
    d.shape("near", "M-30 92 Q30 88 50 96 L46 140 H-30Z")
    d.shape("near", "M230 92 Q170 88 150 96 L154 140 H230Z")
    d.shape("water", "M42 96 Q100 74 158 96 L156 142 Q100 132 44 142Z", spot=True)
    d.stroke("water2", "M56 102 V136 M70 96 V134 M86 92 V132 M100 90 V132 M114 92 V132 M130 96 V134 M144 102 V136", 2.2, line=False)
    d.stroke("water2", "M42 96 Q100 74 158 96", 3)
    d.shape("deep", "M-30 86 Q30 82 50 90 L42 96 Q30 90 -30 94Z M230 86 Q170 82 150 90 L158 96 Q170 90 230 94Z", shadow=False, line=False)
    # mist
    d.shape("light", "M20 150 Q26 132 44 136 Q52 120 70 128 Q84 116 100 126 Q118 116 132 128 Q150 120 158 136 Q176 132 182 150Z")
    d.band("mid", waves(150, 3, 22))
    # tour boat
    def boat():
        d.shape("light", "M-30 0 H32 L26 12 H-24Z")
        d.shape("boat", "M-30 0 H32 L30 4 H-28Z", shadow=False, spot=True)
        d.shape("light", rrect(-20, -10, 38, 10, 1.5))
        d.shape("boat", rrect(-14, -16, 26, 6, 1.5), shadow=False)
        d.marks("boat", "M-16 -7 h6 v4 h-6Z M-6 -7 h6 v4 h-6Z M4 -7 h6 v4 h-6Z")
    group(d, "translate(108 160) scale(.9)", boat)
    d.band("near", waves(172, 3, 26))
    d.band("deep", waves(186, 3, 30), line=False)


# ================================================================ MONUMENT VALLEY
REDROCK = {"rock": "#C8613A", "rock2": "#9A4429", "sand": "#E2A167", "sand2": "#C97D49", "road": "#4A4E57"}


def mitten(d: Drawing, x, base, s=1.0, flip=1):
    """A mitten butte: wide talus skirt, sheer block on top, a slim thumb spire beside."""
    def draw():
        d.shape("rock2", "M-46 0 Q-34 -4 -26 -18 Q-23 -24 -18 -26 H22 Q28 -22 31 -12 Q36 -4 48 0Z")
        d.shape("rock", "M-17 -24 L-16 -62 Q-16 -76 -9 -78 L4 -79 Q10 -78 11 -70 L12 -24Z", spot=True)
        d.shape("rock", "M17 -24 L18 -54 Q20 -62 22 -54 L23 -24Z", spot=True)
        d.shape("rock2", "M3 -78 Q10 -78 11 -70 L12 -24 H4Z M20 -60 Q21 -60 22 -54 L23 -24 H20Z", shadow=False, line=False)
    group(d, f"translate({x} {base}) scale({s * flip} {s})", draw)


def monument_valley(d: Drawing):
    d.disc("glow", 100, 70, 24)
    d.band("far", "M-30 120 H20 V110 H46 V120 H160 V112 H186 V120 H230")
    d.band("sand", "M-30 124 Q100 118 230 124")
    mitten(d, 50, 128, 1.0, 1)
    mitten(d, 144, 128, 0.92, -1)
    # mesa on the right edge
    d.shape("rock", "M180 130 Q186 122 192 108 V82 H230 V130Z")
    # road running straight to the buttes
    d.shape("sand2", "M-30 150 Q100 136 230 150 V200 H-30Z")
    d.shape("road", "M96 128 H104 L136 200 H64Z", spot=True)
    d.stroke("light", "M100 134 V140 M100 150 V160 M100 172 V186", 2)


# ================================================================ HALF DOME
HALFDOME = {"granite": "#BDB7AB", "granite2": "#8E897F", "pine": "#3F6B4A", "pine2": "#2E5238"}


def half_dome(d: Drawing):
    d.disc("glow", 52, 54, 16)
    d.band("far", "M-30 120 Q10 104 40 110 Q60 100 80 108 L230 104")
    # the dome: rounded back, sheer cut face on the left
    d.shape("granite", "M56 142 L58 64 Q59 44 72 38 Q92 30 112 34 Q144 42 164 68 Q182 94 200 118 L230 128 V142Z")
    d.shape("granite2", "M56 142 L58 64 Q59 44 72 38 L80 37 Q74 48 76 70 L78 142Z", shadow=False, spot=True)
    d.stroke("dark", "M63 58 V128 M69 50 V134 M74 64 V120", 1.2, line=False)
    d.stroke("granite2", "M92 44 Q128 42 154 70 M104 60 Q138 62 164 88 M118 80 Q150 86 176 110", 1.8, line=False)
    d.band("mid", "M-30 132 Q30 120 60 128 Q100 134 140 126 Q180 120 230 130")
    for x, h in [(-2, 50), (14, 62), (30, 46), (150, 48), (168, 60), (186, 50), (202, 42)]:
        d.shape("pine", pine(x, 172, h))
    d.band("near", "M-30 164 Q60 154 100 160 Q150 166 230 156")
    d.shape("pine2", pine(124, 172, 30), shadow=False)
    d.shape("pine2", pine(58, 174, 34), shadow=False)
    d.band("deep", hills(182, 4), line=False)


# ================================================================ CN TOWER
CN = {"concrete": "#BEB8AE", "concrete2": "#8F897F", "pod": "#8A93A3", "dome": "#F2F2EE"}


def cn_tower(d: Drawing):
    d.disc("glow", 140, 62, 18)
    birds(d, [(36, 50, 1), (50, 42, .8)])
    x = 100
    d.stroke("concrete2", f"M{x} 16 V46", 2.2)
    d.shape("concrete", poly((x - 2.5, 60), (x - 2, 46), (x + 2, 46), (x + 2.5, 60)))
    d.shape("pod", ellipse(x, 52, 6, 3.5))
    d.shape("concrete", poly((x - 9, 176), (x - 4, 70), (x + 4, 70), (x + 9, 176)), spot=False)
    d.shape("concrete2", poly((x + 1, 70), (x + 4, 70), (x + 9, 176), (x + 2, 176)), shadow=False, line=False)
    # main pod
    d.shape("concrete", "M84 86 Q84 80 100 78 Q116 80 116 86 V94 Q100 98 84 94Z")
    d.shape("pod", "M76 94 Q100 88 124 94 L120 102 Q100 106 80 102Z", spot=True)
    d.shape("concrete", "M84 102 Q100 106 116 102 L112 110 Q100 113 88 110Z")
    d.stroke("glow2", "M86 98 H114", 1.6, line=False)
    # skyline, dome, lake
    d.shape("far", "M-30 200 V150 H20 V132 H32 V146 H44 V128 H54 V150 H86 V200Z M114 200 V140 H130 V120 H142 V138 H154 V126 H166 V146 H180 V136 H192 V150 H230 V200Z")
    d.shape("dome", "M40 168 Q40 144 66 142 Q88 144 88 168Z")
    d.stroke("concrete2", "M48 150 Q66 142 82 150 M44 158 Q66 150 86 158", 1.4)
    d.band("mid", "M-30 166 H230")
    d.band("near", waves(176, 3, 24))
    d.band("deep", waves(188, 3, 30), line=False)


# ================================================================ MACHU PICCHU
INCA = {"g1": "#9CCB72", "g2": "#6EA654", "g3": "#4C8344", "peak": "#4E7F4C", "peak2": "#3A6239", "stone": "#D6CEBE", "stone2": "#9F9583"}


def machu_picchu(d: Drawing):
    d.band("far", "M-30 96 L10 70 L30 84 L50 62 L64 78 L230 72")
    # Huayna Picchu
    d.shape("peak", "M88 128 Q110 112 118 70 Q124 34 140 32 Q156 34 160 64 Q164 96 184 120 L196 128Z")
    d.shape("peak2", "M140 32 Q156 34 160 64 Q164 96 184 120 L196 128 H160 Q150 90 140 32Z", shadow=False, line=False)
    d.shape("peak", "M160 128 Q174 108 184 90 Q192 80 200 88 Q212 104 230 112 V128Z")
    d.shape("light", cloud(160, 84, 0.9))
    # saddle with ruins
    d.band("g2", "M-30 136 Q40 118 90 120 Q150 120 230 132")
    for x, y, w, h in [(36, 116, 18, 10), (58, 112, 22, 12), (86, 112, 16, 10), (108, 114, 20, 10), (132, 116, 16, 9)]:
        d.shape("stone", poly((x, y + h), (x, y), (x + w / 2, y - 6), (x + w, y), (x + w, y + h)))
        d.marks("stone2", rrect(x + w / 2 - 2, y + 2, 4, h - 2, 1))
    d.shape("stone", rrect(60, 124, 70, 6, 1.5))
    # terraces stepping down the slope
    for i in range(5):
        y = 132 + i * 11
        x1 = 120 + i * 12
        d.shape("g1" if i % 2 == 0 else "g2", f"M-30 {y} H{x1} L{x1 + 6} 200 H-30Z")
        d.stroke("stone2", f"M-30 {y + 1.5} H{x1}", 1.4, line=False)
    d.shape("g3", "M150 200 Q160 170 182 150 Q200 140 230 142 V200Z")


# ================================================================ CHRIST THE REDEEMER
CRISTO = {"statue": "#ECE7DD", "statue2": "#C2BAAA", "forest": "#3E7348", "forest2": "#2C5636", "sea": "#4D9BC4"}


def christ_redeemer(d: Drawing):
    d.disc("glow", 100, 74, 60)
    # Sugarloaf across the bay
    d.shape("far", "M-30 150 L6 150 Q10 124 22 116 Q32 112 36 128 L40 150 L54 150 Q60 138 68 140 L74 150 H230 V200 H-30Z")
    d.band("sea", "M-30 150 H230", line=False)
    # Corcovado
    d.shape("forest", "M30 200 Q60 170 76 150 Q88 132 100 130 Q112 132 124 150 Q140 170 170 200Z")
    d.shape("forest2", "M100 130 Q112 132 124 150 Q140 170 170 200 H118 Q112 160 100 130Z", shadow=False, line=False)
    # statue: arms spread wide
    d.shape("statue2", rrect(93, 120, 14, 12, 1))
    d.shape("statue", "M88 60 L50 59 Q46 60 46 64 L50 67 L88 68 L90 92 L91 122 H109 L110 92 L112 68 L150 67 L154 64 Q154 60 150 59 L112 60 Q108 54 100 54 Q92 54 88 60Z", spot=False)
    d.shape("statue2", "M104 56 Q108 56 112 60 L150 59 Q154 60 154 64 L150 67 L112 68 L110 92 L109 122 H104Z", shadow=False, line=False)
    d.stroke("statue2", "M96 76 L94 120 M100 70 V120", 1.2, line=False)
    d.shape("statue", circle(100, 48, 6.5))
    d.shape("statue2", "M100 41.5 A6.5 6.5 0 0 1 100 54.5 Q103 48 100 41.5Z", shadow=False, line=False)
    birds(d, [(140, 112, .9), (152, 104, .7)])


# ================================================================ CHICHEN ITZA
MAYA = {"stone": "#D4BF92", "stone2": "#A88F66", "stone3": "#7E6A4A", "jungle": "#4E8A4A", "jungle2": "#36683A"}


def chichen_itza(d: Drawing):
    d.disc("glow", 100, 78, 52)
    d.band("far", hills(150, 6))
    base, top, n = 160, 76, 9
    h = (base - top) / n
    for i in range(n):
        y = base - (i + 1) * h
        w0 = 148 - i * 10
        w1 = w0 - 4
        d.shape("stone", poly((100 - w0 / 2, y + h), (100 - w1 / 2, y), (100 + w1 / 2, y), (100 + w0 / 2, y + h)), shadow=i == 0)
        d.stroke("stone2", f"M{100 - w0 / 2 + 2} {y + h - 1.2} H{100 + w0 / 2 - 2}", 1.4, line=False)
    # grand staircase with balustrades
    d.shape("stone", poly((80, base), (90, top), (110, top), (120, base)), spot=False)
    d.stroke("stone3", " ".join(f"M{82 + i * 1.6:.1f} {base - 6 - i * 7:.1f} H{118 - i * 1.6:.1f}" for i in range(12)), 1.6, line=False)
    d.shape("stone2", poly((76, base), (88, top), (91, top), (81, base)))
    d.shape("stone2", poly((124, base), (112, top), (109, top), (119, base)))
    # serpent heads at the foot
    d.shape("stone3", "M72 160 V152 Q72 148 78 148 Q84 148 84 154 V160Z M116 160 V154 Q116 148 122 148 Q128 148 128 152 V160Z")
    d.marks("dark", circle(77, 153, 1.4))
    d.marks("dark", circle(123, 153, 1.4))
    # temple on top
    d.shape("stone", rrect(80, 54, 40, 23, 1))
    d.shape("stone2", rrect(78, 50, 44, 6, 1), shadow=False)
    d.shape("stone2", rrect(80, 60, 40, 3, 0), shadow=False, line=False)
    d.marks("dark", "M86 65 H93 V77 H86Z M96.5 65 H103.5 V77 H96.5Z M107 65 H114 V77 H107Z")
    # jungle edges
    for x, y, r in [(10, 156, 20), (30, 166, 16), (186, 154, 20), (168, 166, 14)]:
        d.shape("jungle", circle(x, y, r))
    d.band("ground", hills(170, 3))
    d.band("jungle2", hills(184, 3, 20), line=False)


# ================================================================ MOAI
MOAI = {"rock": "#7D6E62", "rock2": "#5A4D44", "rock3": "#3B312B", "pukao": "#A9523A", "grass": "#6E9E52", "grass2": "#4E7E3E", "sea": "#7ABCDC"}


def moai(d: Drawing, x, base, s=1.0, hat=False):
    def draw():
        body = ("M-16 0 V-30 Q-18 -34 -18 -40 L-17 -70 Q-17 -84 -10 -86 H10 Q17 -84 17 -70 L18 -40 Q18 -34 16 -30 V0Z")
        d.shape("rock", body)
        d.shape("rock2", "M6 -86 H10 Q17 -84 17 -70 L18 -40 Q18 -34 16 -30 V0 H8Z", shadow=False, line=False)
        # ears
        d.shape("rock", "M-17 -70 Q-23 -68 -22 -56 Q-21 -46 -17 -46Z M17 -70 Q23 -68 22 -56 Q21 -46 17 -46Z", shadow=False)
        # heavy brow shading the eyes
        d.shape("rock3", "M-14 -70 H14 L13 -63 Q8 -61 2 -64 H-2 Q-8 -61 -13 -63Z", shadow=False)
        d.shape("rock", "M-15 -72 H15 V-69 H-15Z", shadow=False, line=False)
        # long nose with flared base
        d.shape("rock", "M-3 -66 L-4 -46 Q-8 -44 -7 -41 H7 Q8 -44 4 -46 L3 -66Z", shadow=False)
        d.shape("rock3", "M-6 -42 Q-4 -40 -2 -42 M2 -42 Q4 -40 6 -42", shadow=False, line=False)
        # pursed lips, jutting chin
        d.stroke("rock3", "M-7 -35 Q0 -32 7 -35", 1.8)
        d.stroke("rock2", "M-7 -30 Q0 -26 7 -30", 1.4, line=False)
        # arms
        d.stroke("rock2", "M-14 -22 Q-8 -14 0 -12 M14 -22 Q8 -14 0 -12", 1.6, line=False)
        if hat:
            d.shape("pukao", "M-12 -86 V-96 Q0 -100 12 -96 V-86Z", spot=True)
    group(d, f"translate({x} {base}) scale({s})", draw)


def moai_row(d: Drawing):
    d.disc("glow", 100, 82, 40)
    d.band("sea", "M-30 120 H230", line=False)
    if not d.paper:
        d.stroke("dark", "M-30 120 H230", 2)
    d.stroke("light", "M10 128 h20 M150 130 h24 M60 134 h16", 1.8)
    d.band("grass", "M-30 150 Q60 140 230 148")
    # ahu platform
    d.shape("rock2", rrect(22, 140, 156, 14, 2))
    moai(d, 48, 142, 0.82)
    moai(d, 152, 142, 0.82)
    moai(d, 100, 144, 1.12, hat=True)
    d.band("grass2", "M-30 168 Q100 158 230 168")
    d.band("deep", hills(184, 3), line=False)


# ================================================================ IGUAZU FALLS
IGUAZU = {"water": "#BFE6F2", "water2": "#FFFFFF", "jungle": "#4E8A4A", "jungle2": "#36683A", "rock": "#7A5E48",
          "toucan": "#1E1E22", "beak": "#F29A2E", "beak2": "#E84E3A", "bib": "#FFE07A"}


def canopy(x0, x1, y, r, bottom) -> str:
    """A jungle edge: a row of round treetops from x0 to x1 along y, filled down to `bottom`."""
    n = max(1, round((x1 - x0) / (r * 1.6)))
    step = (x1 - x0) / n
    s = f"M{x0:g} {bottom:g} V{y:g}"
    for i in range(n):
        s += f" A{r * .9:g} {r:g} 0 0 1 {x0 + (i + 1) * step:.1f} {y + (2 if i % 2 else -1):g}"
    return s + f" V{bottom:g}Z"


def iguazu_falls(d: Drawing):
    d.band("far", "M-30 66 Q40 56 100 62 Q160 56 230 66")
    # top shelf of jungle, water spilling out between the trees
    d.shape("jungle", canopy(-30, 230, 74, 9, 100))
    for x0, x1 in [(4, 40), (58, 98), (116, 148), (166, 200)]:
        d.shape("water", f"M{x0} 90 Q{(x0 + x1) / 2} 86 {x1} 90 L{x1 + 3} 124 H{x0 - 3}Z")
        d.stroke("water2", " ".join(f"M{x} 92 V122" for x in range(x0 + 6, x1, 9)), 1.6, line=False)
        if not d.paper:
            d.stroke("dark", " ".join(f"M{x} 96 V{116 - (x % 7)}" for x in range(x0 + 9, x1 - 4, 12)), 1.6)
    # islands of jungle between the two tiers
    for x0, x1 in [(-30, 10), (38, 62), (96, 118), (146, 170), (196, 230)]:
        d.shape("jungle2", canopy(x0, x1, 112, 6, 134), line=False)
    d.shape("jungle2", "M-30 122 H230 V134 H-30Z", shadow=False, line=False)
    # broad lower curtain
    d.shape("water", "M-30 130 Q100 124 230 130 V156 H-30Z")
    d.stroke("water2", " ".join(f"M{x} 132 V152" for x in range(-24, 230, 9)), 1.6, line=False)
    if not d.paper:
        d.stroke("dark", " ".join(f"M{x} 134 V{148 - (x % 5)}" for x in range(-14, 230, 14)), 1.6)
    d.shape("light", "M-30 156 Q-10 144 10 150 Q26 140 44 148 Q62 140 80 150 Q100 140 118 150 Q136 140 156 150 Q176 140 196 150 Q214 144 230 152 V164 H-30Z")
    d.band("mid", waves(164, 3, 22))
    d.band("deep", waves(180, 3, 30), line=False)
    # toucan on a branch
    d.limb("rock", "M110 186 Q140 170 200 170", 4)
    def toucan():
        d.shape("toucan", "M0 0 C-6 -12 -2 -26 10 -28 C18 -28 22 -22 22 -14 C22 0 14 12 8 22 L2 34 L-2 22 C-2 14 0 8 0 0Z")
        d.shape("bib", "M10 -26 C2 -24 0 -16 4 -10 C10 -10 14 -14 14 -20 C14 -24 12 -26 10 -26Z", shadow=False)
        d.shape("beak", "M8 -26 C4 -32 -16 -32 -30 -20 C-16 -22 -4 -18 6 -16Z", spot=True)
        d.shape("beak2", "M-30 -20 C-24 -24 -20 -25 -16 -25 L-20 -21Z", shadow=False)
        d.stroke("toucan", "M8 -22 C-4 -24 -16 -24 -26 -20", 1, line=False)
        d.marks("light", circle(12, -22, 2.4))
        d.marks("toucan", circle(12, -22, 1.2))
        d.shape("beak2", "M4 4 C6 8 10 8 12 4Z", shadow=False, line=False)
    group(d, "translate(150 136) scale(1.1)", toucan)


# ================================================================ TORRES DEL PAINE
PAINE = {"granite": "#D9CDBE", "granite2": "#A8998A", "lake": "#5CC3C8", "lake2": "#9FE0E2", "scree": "#8E8A84", "scree2": "#6E6A66"}


def torres_del_paine(d: Drawing):
    d.disc("glow", 100, 100, 62)
    d.band("far", "M-30 120 L10 96 L30 106 L50 86 L70 104 H130 L150 84 L170 102 L190 92 L230 112")
    # three granite towers
    d.shape("granite", "M56 124 L62 72 L66 56 Q70 44 74 56 L78 70 L80 124Z")
    d.shape("granite", "M80 124 L84 58 L90 32 Q96 22 100 32 L106 58 L110 124Z")
    d.shape("granite", "M110 124 L114 64 L120 46 Q125 38 130 48 L136 70 L142 124Z")
    d.shape("granite2", "M70 50 Q72 50 74 56 L78 70 L80 124 H72Z M96 26 Q98 28 100 32 L106 58 L110 124 H100Z M126 42 Q128 44 130 48 L136 70 L142 124 H132Z",
            shadow=False, line=False)
    d.stroke("granite2", "M66 80 V110 M90 52 V118 M120 64 V116", 1.4, line=False)
    d.shape("light", "M88 40 L90 32 Q96 22 100 32 L102 40 Q96 36 94 40 Q92 36 88 40Z", shadow=False)
    # moraine and the glacial lake
    d.shape("scree", "M20 140 Q40 118 60 122 Q100 116 140 122 Q160 118 180 140Z")
    d.shape("scree2", "M100 117 Q140 116 160 120 L180 140 H120Z", shadow=False, line=False)
    d.shape("lake", "M-30 140 Q40 132 100 136 Q160 132 230 140 V200 H-30Z")
    d.stroke("lake2", "M30 148 h24 M120 152 h30 M70 160 h16", 2)
    d.shape("scree2", "M-30 200 V168 Q10 156 40 164 Q60 170 70 200Z M230 200 V164 Q190 154 160 166 Q146 174 140 200Z")
    d.shape("scree", "M-30 200 V176 Q10 166 40 172 Q50 180 52 200Z M230 200 V174 Q196 164 170 174 Q160 184 158 200Z", shadow=False)


# ================================================================ concepts
CONCEPTS = [
    Concept("lm-grandcanyon-sunset", "landmark-grand-canyon", "Grand Canyon", canyon_sunset, overrides=CANYON,
            checks=[("c1", "haze"), ("haze", "glow"), ("haze", "sky"), ("glow", "sky"), ("river", "c4")],
            fixes={"haze": ["#C49AA6", "#B88C8C", "far"], "glow": ["glow2", "light", "pop", "mid", "near"]}),
    Concept("lm-grandcanyon-rim", "landmark-grand-canyon", "Grand Canyon rim & condor", canyon_rim, overrides=CANYON,
            palettes=["golden", "coastal", "meadow", "blush"],
            checks=[("c1", "far"), ("far", "sky"), ("dark", "sky"), ("pine", "sky"), ("pine", "far"), ("c4", "c2")],
            fixes={"far": ["mid", "#CFA6A0", "#B98E96"]}),
    Concept("lm-liberty-torch", "landmark-statue-of-liberty", "Statue of Liberty", liberty_torch, overrides=COPPER,
            checks=[("cu", "sky"), ("cu", "glow"), ("gold", "sky"), ("stone", "far"), ("stone", "mid"), ("far", "sky")],
            fixes={"glow": ["light", "glow2", "pop"], "sky": ["sky2"], "far": ["mid", "near"], "mid": ["near", "far"]}),
    Concept("lm-goldengate-fog", "landmark-golden-gate", "Golden Gate Bridge", goldengate_fog, overrides=BRIDGE,
            checks=[("gg", "sky"), ("gg", "far"), ("gg", "glow"), ("light", "mid"), ("gg", "light")],
            fixes={"far": ["mid", "near", "deep"], "glow": ["glow2", "light"]}),
    Concept("lm-empirestate-dusk", "landmark-empire-state", "Empire State Building", empire_state, overrides=ESB,
            checks=[("tower", "glow"), ("tower", "sky"), ("tower", "far"), ("tower", "mid")],
            fixes={"far": ["sky2", "light"], "mid": ["far", "near"], "sky": ["sky2", "glow2"]}),
    Concept("lm-rushmore-faces", "landmark-mount-rushmore", "Mount Rushmore", rushmore_faces, overrides=GRANITE,
            checks=[("rock2", "sky"), ("rock", "sky"), ("pine", "rock3")],
            fixes={"sky": ["sky2", "far", "mid"]}),
    Concept("lm-niagara-rainbow", "landmark-niagara-falls", "Niagara Falls", niagara_horseshoe, palettes=["coastal", "meadow", "blush", "dusk"], overrides=FALLS,
            checks=[("water", "near"), ("light", "mid"), ("near", "sky"), ("boat", "mid")],
            fixes={"near": ["deep", "mid"], "boat": ["pop", "#E4572E"]}),
    Concept("lm-monumentvalley-road", "landmark-monument-valley", "Monument Valley", monument_valley, overrides=REDROCK,
            checks=[("rock", "glow"), ("rock", "sky"), ("rock", "far"), ("far", "sky")],
            fixes={"glow": ["glow2", "light"], "far": ["sky2", "mid", "near"]}),
    Concept("lm-halfdome-valley", "landmark-half-dome", "Yosemite Half Dome", half_dome, overrides=HALFDOME,
            checks=[("granite", "sky"), ("granite", "far"), ("pine", "mid"), ("granite", "mid")],
            fixes={"sky": ["sky2", "far"], "far": ["mid", "near", "deep"], "mid": ["near", "deep"]}),
    Concept("lm-cntower-lake", "landmark-cn-tower", "CN Tower", cn_tower, overrides=CN,
            checks=[("concrete", "sky"), ("concrete", "glow"), ("concrete", "far"), ("dome", "far"), ("pod", "sky")],
            fixes={"sky": ["sky2", "far"], "glow": ["glow2", "pop", "near"], "far": ["mid", "near", "deep"]}),
    Concept("lm-machupicchu-terraces", "landmark-machu-picchu", "Machu Picchu", machu_picchu, overrides=INCA,
            checks=[("peak", "sky"), ("peak", "far"), ("far", "sky"), ("stone", "g2")],
            fixes={"far": ["sky2", "light", "mid"]}),
    Concept("lm-cristo-corcovado", "landmark-christ-redeemer", "Christ the Redeemer", christ_redeemer, overrides=CRISTO,
            checks=[("statue", "glow"), ("far", "sky"), ("far", "glow"), ("forest", "glow")],
            fixes={"glow": ["glow2", "hero2", "pop", "hero", "near"], "far": ["mid", "near", "deep"]}),
    Concept("lm-chichenitza-castillo", "landmark-chichen-itza", "Chichen Itza", chichen_itza, overrides=MAYA,
            checks=[("stone", "glow"), ("stone", "sky"), ("stone", "far")],
            fixes={"glow": ["near", "mid", "pop", "deep"], "far": ["mid", "near", "deep"]}),
    Concept("lm-moai-ahu", "landmark-moai", "Easter Island moai", moai_row, overrides=MOAI,
            checks=[("rock", "glow"), ("rock", "sky"), ("rock", "sea"), ("glow", "sky")],
            fixes={"glow": ["glow2", "light", "pop"]}),
    Concept("lm-iguazu-toucan", "landmark-iguazu-falls", "Iguazu Falls", iguazu_falls, palettes=["coastal", "meadow", "blush", "dusk"], overrides=IGUAZU,
            checks=[("toucan", "light"), ("toucan", "jungle2"), ("far", "sky"), ("jungle", "far")],
            fixes={"far": ["mid", "near", "sky2"]}),
    Concept("lm-torres-sunrise", "landmark-torres-del-paine", "Torres del Paine", torres_del_paine, palettes=["coastal", "meadow", "blush", "dusk", "golden"], overrides=PAINE,
            checks=[("granite", "glow"), ("granite", "far"), ("far", "sky"), ("far", "glow")],
            fixes={"glow": ["glow2", "pop", "mid", "near"], "far": ["mid", "near", "deep"]}),
]
