"""Water B: kitesurfing, dolphins, turtles, shark cage, cliff jumping, hot springs,
waterfall swim, fishing, beach day and beach hammock. Three concepts each."""
from math import hypot

from _common import Concept, Drawing, cloud, fish, circle, ellipse, waves, hills, rrect, group, bubbles, water

UNDERWATER = ["coastal", "dusk", "meadow"]
DOLPHIN_GREY = {"hero": "#7C95AB", "light": "#E4ECF2", "mark": "#1E3242"}
TURTLE_GREEN = {"hero": "#6E8B3D", "hero2": "#B9C77A", "mark": "#33461C"}
GREAT_WHITE = {"hero": "#56697A", "light": "#EEF2F5", "mark": "#16242F"}
SKIN = {"hero2": "#E8B48C"}
MONKEY = {"hero": "#9C8B78", "hero2": "#E79A8E", "mark": "#3A2A22"}
WOOD = {"hero2": "#D9A86A", "mark": "#8A5A2B"}
HATCHLING = {"hero": "#5B5146", "hero2": "#8A7C6A", "mark": "#2E2822"}


# ================================================================ helpers
def sea(d: Drawing, y: float = 120):
    """Open sea seen from above the surface: three bands from the horizon down."""
    d.band("far", f"M-30 {y} H230")
    d.band("mid", waves(y + 22, 4, 30))
    d.band("near", waves(y + 44, 5, 34))


def spray(x, y, s=1.0, left=True):
    """A splash fan of three droplet petals rising from (x, y)."""
    k = -1 if left else 1
    return (f"M{x} {y} C{x+k*4*s} {y-10*s} {x+k*14*s} {y-18*s} {x+k*24*s} {y-16*s} "
            f"C{x+k*18*s} {y-12*s} {x+k*14*s} {y-6*s} {x+k*16*s} {y}Z")


def clipline(fn):
    """Line style doesn't clip shapes to the circle; wrap concepts whose shapes bleed off the edge."""
    def draw(d: Drawing):
        d.raw("", '<g clip-path="url(#clip)">')
        fn(d)
        d.raw("", "</g>")
    return draw


def leaf(tx, ty, ex, ey, bulge=0.36, droop=8):
    """A pointed, slightly drooping leaf from (tx, ty) to (ex, ey)."""
    dx, dy = ex - tx, ey - ty
    n = hypot(dx, dy)
    px, py = -dy / n * n * bulge / 2, dx / n * n * bulge / 2
    mx, my = (tx + ex) / 2, (ty + ey) / 2 - droop
    return (f"M{tx} {ty} Q{mx+px:.1f} {my+py:.1f} {ex} {ey} Q{mx-px:.1f} {my-py:.1f} {tx} {ty}Z")


def palm(d: Drawing, x, y, h, lean, role="dark", trunk_w=6):
    """A palm tree with its base at (x, y), top at (x + lean, y - h)."""
    tx, ty = x + lean, y - h
    d.limb(role, f"M{x} {y} Q{x + lean*0.1} {y - h*0.6} {tx} {ty}", trunk_w)
    for ex, ey, dr in [(-34, 10, 6), (-28, -12, 6), (-6, -24, 4), (20, -18, 6), (34, 4, 6), (-16, 22, 2), (18, 20, 2)]:
        d.shape(role, leaf(tx, ty, tx + ex, ty + ey, 0.34, dr), shadow=False)


# A dolphin facing right, about 140 wide, centred near (95, 100).
DOLPHIN = ("M164 103 C160 100 152 99 146 97 C142 88 128 82 108 82 C84 82 62 90 48 100 L36 104 "
           "L22 92 C26 101 27 107 23 118 L38 110 C56 114 80 118 104 116 C126 114 140 110 150 106 "
           "C156 105 160 105 164 103Z")
DOLPHIN_BELLY = "M58 106 C76 113 100 114 122 111 C136 109 146 106 154 104 C146 109 128 114 104 116 C84 117 68 113 58 106Z"
DOLPHIN_FIN = "M90 85 C96 74 102 66 112 60 C109 69 110 77 116 84Z"
DOLPHIN_FLIPPER = "M122 108 C120 117 114 124 104 129 C109 121 111 114 112 109Z"


def dolphin(d: Drawing, body="hero", belly="light", eye="mark", spot=False):
    d.shape(body, DOLPHIN_FIN)
    d.shape(body, DOLPHIN, spot=spot)
    d.shape(belly, DOLPHIN_BELLY, shadow=False)
    d.shape(body, DOLPHIN_FLIPPER, shadow=False)
    d.stroke(eye, "M164 103 Q157 106 150 104", 1.4)
    d.marks(eye, circle(142, 96, 2.2))


def turtle_top(d: Drawing, shell="hero", skin="hero2", mark="mark"):
    """A sea turtle seen from above, swimming left, centred at (100, 93)."""
    d.shape(skin, ellipse(74, 70, 20, 6.5), extra='transform="rotate(-38 74 70)"')
    d.shape(skin, ellipse(76, 116, 20, 6.5), extra='transform="rotate(36 76 116)"')
    d.shape(skin, ellipse(132, 80, 10, 4.5), extra='transform="rotate(30 132 80)"')
    d.shape(skin, ellipse(132, 106, 10, 4.5), extra='transform="rotate(-30 132 106)"')
    d.shape(skin, ellipse(60, 93, 12, 9))
    d.shape(shell, ellipse(100, 93, 34, 24))
    d.stroke(mark, "M88 84 L100 78 L112 84 L112 102 L100 108 L88 102Z M88 84 L74 88 M112 84 L126 88 "
                   "M112 102 L126 99 M88 102 L74 99 M100 78 V70 M100 108 V116", 2.2)
    d.marks(mark, circle(55, 90, 1.9))


# ================================================================ KITESURFING
KITE = "M30 74 C40 26 160 26 170 74 C166 78 158 78 154 72 C140 46 60 46 46 72 C42 78 34 78 30 74Z"


def kite_canopy(d: Drawing, body="hero", stripe="hero2"):
    d.shape(body, KITE)
    d.shape(stripe, "M70 38 C80 34 90 33 100 32 L100 48 C88 48 78 50 68 54Z", shadow=False, spot=True)
    d.shape(stripe, "M130 38 C120 34 110 33 100 32 L100 48 C112 48 122 50 132 54Z", shadow=False, spot=True)
    d.stroke("dark", "M50 52 L58 64 M70 38 L68 54 M100 32 V48 M130 38 L132 54 M150 52 L142 64", 1.4, line=False)


def rider(d: Drawing, suit="dark", board="pop", helmet="hero2", bar="pop", detail=True):
    """A kitesurfer leaning back on a board; the bar ends are at (96, 108) and (106, 126)."""
    if detail:
        d.shape("light", spray(58, 170, 1.3, left=True), shadow=False)
    d.limb(suit, "M78 166 L86 152 L82 138 M106 162 L100 150 L82 138", 7)
    d.limb(suit, "M82 138 L76 117", 12)
    d.limb(suit, "M77 121 L97 112 M77 124 L103 122", 4.5)
    d.stroke(bar, "M96 107 L106 127", 3.5)
    d.shape(suit, circle(72, 106, 8))
    if detail:
        d.shape(helmet, "M64 105 A8 8 0 0 1 80 105Z", shadow=False)
    d.shape(board, rrect(56, 163, 78, 8, 4), spot=True, extra='transform="rotate(-8 95 167)"')


def kite_rider(d: Drawing):
    d.disc("glow", 156, 100, 15)
    d.shape("light", cloud(16, 84, 0.9), shadow=False)
    d.band("far", "M-30 124 H230")
    d.band("mid", waves(144, 4, 30))
    group(d, "translate(30 -4) scale(.7)", lambda: kite_canopy(d))
    d.stroke("dark", "M52 48 L96 107 M148 48 L106 127", 1.1)
    d.band("near", waves(164, 5, 34))
    rider(d)
    d.band("deep", waves(186, 4, 38), line=False)


def kite_board(d: Drawing):
    d.disc("glow", 52, 56, 15)
    group(d, "translate(116 24) scale(.36)", lambda: kite_canopy(d, "pop", "light"))
    sea(d, 96)
    d.band("deep", waves(172, 5, 38), line=False)

    def board():
        d.shape("light", "M44 140 C22 132 16 110 26 92 C30 106 40 116 56 122Z", shadow=False)
        d.shape("light", "M40 112 C34 100 36 90 44 84 C44 94 48 102 54 108Z", shadow=False)
        d.stroke("light", "M20 150 Q36 146 48 138 M14 136 Q24 132 32 126", 2.4, line=False)
        d.shape("hero", rrect(34, 106, 136, 32, 16))
        d.shape("hero2", rrect(42, 112, 120, 5, 2.5), shadow=False, spot=True)
        for x in (66, 138):
            d.shape("light", rrect(x - 13, 114, 26, 18, 7))
            d.shape("dark", rrect(x - 5, 108, 10, 28, 5))
        d.shape("dark", rrect(94, 118, 12, 8, 4), shadow=False)
    group(d, "rotate(-14 100 121)", board)


def kite_beach(d: Drawing):
    d.disc("glow", 150, 92, 16)
    d.band("far", "M-30 128 Q10 108 44 112 Q66 116 76 130 H230")
    group(d, "translate(10 18) scale(.6)", lambda: kite_canopy(d))
    group(d, "translate(118 36) scale(.36)", lambda: kite_canopy(d, "pop", "light"))
    d.stroke("dark", "M28 62 L72 136 M112 62 L76 144", 1)
    d.stroke("dark", "M129 59 L148 137 M179 59 L151 142", 0.9)
    d.band("mid", waves(148, 3, 26))
    group(d, "translate(28.5 87.4) scale(.45)", lambda: rider(d, detail=False))
    group(d, "translate(121.7 107.2) scale(.28)", lambda: rider(d, detail=False))
    d.band("near", waves(168, 4, 30))
    d.band("ground", "M-30 182 Q60 172 120 178 T230 176")


# ================================================================ DOLPHINS
def snorkeller(d: Drawing, suit="hero2", fins="pop", skin="dark"):
    """A snorkeller floating face-down, head to the left at (60, 52)."""
    d.limb(skin, "M112 52 L140 46 M112 58 L142 60", 7)
    d.shape(fins, ellipse(150, 42, 11, 4.5), extra='transform="rotate(-14 150 42)"', spot=True)
    d.shape(fins, ellipse(152, 62, 11, 4.5), extra='transform="rotate(10 152 62)"', spot=True)
    d.shape(suit, rrect(66, 46, 52, 18, 9))
    d.limb(suit, "M74 60 Q60 70 46 66", 6)
    d.shape(suit, circle(60, 52, 10))
    d.shape(skin, rrect(48, 49, 12, 9, 3), shadow=False)
    d.shape("light", rrect(50, 51, 8, 5, 2), shadow=False)
    d.stroke(fins, "M66 46 V32", 3)


def dolphin_leap(d: Drawing):
    d.disc("glow", 128, 96, 32)
    d.shape("light", cloud(26, 62, 1.0), shadow=False)
    d.band("far", "M-30 128 H230")
    group(d, "translate(-2 -14) rotate(-24 95 100)", lambda: dolphin(d, spot=True))
    d.band("mid", waves(140, 4, 30))
    d.shape("light", "M38 150 C42 138 48 130 58 128 C54 136 54 142 58 150Z M64 150 C66 140 72 134 82 132 C76 140 76 144 78 150Z", shadow=False)
    d.band("near", waves(152, 5, 34))
    d.band("deep", waves(176, 4, 38), line=False)


def dolphin_pod(d: Drawing):
    water(d, bottom=False)
    d.raw('<g opacity=".16" fill="#fff"><path d="M50 0 L70 0 L108 200 L88 200Z"/><path d="M120 0 L134 0 L172 200 L158 200Z"/></g>', "")
    group(d, "translate(36 22) scale(.58) rotate(12 95 100)", lambda: dolphin(d))
    group(d, "translate(-4 46) scale(.9) rotate(-6 95 100)", lambda: dolphin(d, spot=True))
    bubbles(d, [(162, 80, 3), (168, 66, 4.2), (160, 54, 2.4)])
    d.band("ground", "M-30 182 Q40 170 90 180 T230 176")


def dolphin_swimmer(d: Drawing):
    water(d, bottom=False)
    snorkeller(d)
    group(d, "translate(0 50) scale(.92) rotate(-4 95 100)", lambda: dolphin(d))
    bubbles(d, [(38, 96, 2.5), (32, 84, 3.5)])
    d.band("ground", "M-30 186 Q40 174 90 184 T230 180")


# ================================================================ TURTLES
def turtle_snorkel(d: Drawing):
    water(d)
    for x in (150, 162, 174):
        d.limb("near", f"M{x} 180 Q{x-6} 166 {x+2} 150", 4, shadow=False)
    group(d, "translate(6 30) scale(.84) rotate(-12 100 93)", lambda: turtle_top(d))
    group(d, "translate(200 -4) scale(-1 1)", lambda: snorkeller(d, suit="pop", fins="dark"))
    bubbles(d, [(160, 104, 2.5), (166, 92, 3.5)])


def turtle_breath(d: Drawing):
    d.disc("glow", 50, 54, 18)
    d.shape("light", cloud(110, 34, 1.0), shadow=False)
    d.band("far", "M-30 100 H230")
    d.band("mid", waves(122, 3, 26), line=False)
    d.band("near", waves(150, 4, 30), line=False)
    d.band("deep", waves(176, 4, 36), line=False)

    def body():
        d.shape("hero2", "M60 132 C54 144 44 152 32 156 C46 158 60 152 70 140Z")
        d.shape("hero2", "M124 122 C132 106 142 88 146 76 L162 74 C158 90 150 110 142 128Z")
        d.shape("hero", "M48 134 C50 108 70 94 96 94 C122 94 138 110 140 130 C116 138 74 140 48 134Z")
        d.shape("hero2", "M48 134 C74 140 116 138 140 130 C138 136 132 140 126 140 C102 144 74 144 54 140Z", shadow=False)
        d.stroke("mark", "M70 132 C70 118 80 104 94 100 C108 100 120 108 126 122 M94 100 C92 110 94 124 98 136 M64 118 H130", 2)
        d.shape("hero2", "M106 136 C118 152 136 164 160 166 C146 152 132 140 122 130Z")
    group(d, "translate(-6 16)", body)
    d.shape("hero2", ellipse(148, 86, 13, 8.5), extra='transform="rotate(-20 148 86)"')
    d.marks("mark", circle(153, 82, 2))
    d.stroke("dark", "M156 90 Q158 92 161 90", 1.2, line=False)
    if d.paper:
        d.raw(f'<path d="{waves(100, 3, 24)} L230 230 L-30 230Z" fill="{d.c["near"]}" opacity=".42"/>')
    d.stroke("light", "M122 100 Q134 96 146 100 T170 100", 2.4)
    d.stroke("light", "M110 106 Q118 104 126 106 M156 106 Q166 104 176 106", 1.8, line=False)
    if not d.paper:
        d.stroke("dark", waves(100, 3, 24), 2)
    bubbles(d, [(84, 170, 2.5), (92, 180, 3.5)])


def turtle_hatchlings(d: Drawing):
    d.disc("glow", 140, 50, 15)
    d.band("far", "M-30 84 H230")
    d.band("mid", waves(96, 3, 26))
    d.shape("light", "M-30 106 Q20 98 60 106 T150 104 T230 106 V114 H-30Z", shadow=False, line=False)
    d.band("ground", "M-30 110 Q40 104 100 110 T230 108")
    for x0, y0, x1, y1 in [(58, 176, 54, 150), (100, 168, 96, 140), (132, 180, 124, 162)]:
        for i in range(4):
            t = i / 4
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            d.marks("near", f"M{x-5:.1f} {y:.1f} h3 v1.6 h-3Z M{x+2:.1f} {y-2:.1f} h3 v1.6 h-3Z")
    d.shape("near", ellipse(150, 176, 24, 8))
    for x, y in [(140, 173), (153, 171), (162, 176)]:
        d.shape("light", ellipse(x, y, 5, 3.6), shadow=False)

    def baby(x, y, s, rot):
        def draw():
            d.shape("hero2", ellipse(-10, -5, 9, 3), extra='transform="rotate(-35 -10 -5)"')
            d.shape("hero2", ellipse(10, -5, 9, 3), extra='transform="rotate(35 10 -5)"')
            d.shape("hero2", ellipse(-6, 9, 4.5, 2), extra='transform="rotate(40 -6 9)"')
            d.shape("hero2", ellipse(6, 9, 4.5, 2), extra='transform="rotate(-40 6 9)"')
            d.shape("hero2", ellipse(0, -13, 4, 4.6))
            d.shape("hero", ellipse(0, 1, 8.5, 10.5), spot=True)
            d.stroke("mark", "M0 -6 V8 M-5 -2 L0 -6 L5 -2 M-5 5 L0 8 L5 5", 1.1, line=False)
        group(d, f"translate({x} {y}) rotate({rot}) scale({s})", draw)
    baby(54, 136, 1.35, -6)
    baby(96, 126, 1.25, 4)
    baby(124, 150, 1.4, 14)


# ================================================================ SHARK CAGE
GW_BODY = ("M22 100 C30 86 52 78 80 76 C104 75 128 78 150 88 L178 66 C173 84 173 98 180 118 L152 108 "
           "C130 118 104 122 80 120 C56 118 36 112 22 100Z")
GW_BELLY = "M26 103 C40 110 60 114 84 114 C108 114 130 110 148 104 C130 116 104 122 80 120 C56 118 36 112 26 103Z"


def great_white(d: Drawing, body="hero", belly="light", eye="mark", spot=False):
    """A great white facing left, nose at (22, 100)."""
    d.shape(body, "M84 78 L98 48 L116 80Z")
    d.shape(body, GW_BODY, spot=spot)
    d.shape(belly, GW_BELLY, shadow=False)
    d.shape(body, "M70 114 L100 142 L96 115Z", shadow=False)
    d.stroke(eye, "M58 92 Q56 98 58 104 M64 91 Q62 97 64 103 M70 91 Q68 97 70 103", 1.6)
    d.stroke(eye, "M26 104 Q36 108 48 105", 1.6)
    d.marks("light", "M32 106 l2 3 l2 -3Z M38 107 l2 3 l2 -3Z M44 106 l2 3 l2 -3Z")
    d.marks(eye, circle(40, 94, 2.4))


def cage(d: Drawing, x, y, w, h, bar="hero2", diver=True):
    if diver:
        d.shape("dark", rrect(x + w / 2 - 8, y + h * 0.38, 16, h * 0.55, 8))
        d.limb("dark", f"M{x+w/2-4} {y+h*0.5} L{x+w*0.2} {y+h*0.62}", 5)
        d.shape("dark", circle(x + w / 2, y + h * 0.3, 9))
        d.shape("hero2", rrect(x + w / 2 - 9, y + h * 0.3 - 5, 13, 9, 3), shadow=False)
        d.shape("light", rrect(x + w / 2 - 7, y + h * 0.3 - 3, 9, 5, 2), shadow=False)
    bars = f"M{x} {y} H{x+w} V{y+h} H{x} Z"
    for i in range(1, 4):
        bars += f" M{x + w*i/4:.1f} {y} V{y+h}"
    bars += f" M{x} {y+h/2} H{x+w}"
    d.stroke(bar, bars, 3.2, shadow=True)


def shark_cage(d: Drawing):
    water(d, bottom=False)
    d.raw('<g opacity=".15" fill="#fff"><path d="M40 0 L58 0 L96 200 L78 200Z"/></g>', "")
    d.stroke("dark", "M123 22 L123.5 44", 1.6)
    cage(d, 96, 44, 54, 72)
    for x in (96, 150):
        d.shape("pop", rrect(x - 7, 36, 14, 12, 5), spot=True)
    group(d, "translate(12 70) scale(.78)", lambda: great_white(d))
    bubbles(d, [(160, 70, 2.5), (166, 58, 3.4), (160, 48, 2.2)])
    d.band("ground", "M-30 184 Q40 174 90 182 T230 178")


def shark_jaws(d: Drawing):
    water(d, bottom=False)
    head = "M-30 46 C30 28 118 32 158 64 C170 74 172 84 166 90 L104 104 L150 126 C158 132 156 140 146 146 C110 162 40 166 -30 160Z"
    d.shape("mark", "M166 88 L100 104 L150 128 C164 118 170 104 166 88Z", shadow=False)
    d.shape("pop", "M166 88 L100 104 L106 108 L164 96Z M104 104 L150 128 L148 122 L110 104Z", shadow=False)
    d.marks("light", "M156 92 l4 9 l3 -10Z M146 94 l4 9 l3 -10Z M136 96 l4 9 l3 -10Z M126 98 l3 8 l3 -9Z M116 100 l3 7 l3 -8Z")
    d.marks("light", "M142 120 l3 -9 l4 10Z M132 115 l3 -9 l4 10Z M122 110 l3 -8 l4 9Z")
    d.shape("hero", head)
    d.shape("light", "M-30 140 C30 146 100 138 140 136 L150 128 C158 132 156 140 146 146 C110 162 40 166 -30 160Z", shadow=False)
    d.stroke("mark", "M40 70 Q34 90 40 112 M52 68 Q46 88 52 110 M64 68 Q58 88 64 108", 2.4)
    d.marks("mark", circle(128, 66, 5))
    d.marks("light", circle(129.5, 64.5, 1.6))
    d.limb("hero2", "M146 20 V184 M184 30 V174 M120 46 H200 M120 158 H200", 6, spot=True)
    bubbles(d, [(170, 110, 2.5), (176, 98, 3.5), (172, 86, 2)])


def shark_boat(d: Drawing):
    d.disc("glow", 48, 50, 14)
    d.band("far", "M-30 90 H230")
    d.band("mid", waves(116, 3, 26), line=False)
    d.band("near", waves(146, 4, 30), line=False)
    d.band("deep", waves(174, 4, 36), line=False)
    cage(d, 138, 82, 38, 52, diver=True)
    if d.paper:
        d.raw(f'<path d="{waves(90, 2.5, 22)} L230 230 L-30 230Z" fill="{d.c["near"]}" opacity=".3"/>')
    d.stroke("dark", "M124 72 V40 L157 40 V82", 2.4)
    d.shape("hero2", rrect(52, 50, 48, 24, 4))
    d.marks("dark", f"{rrect(58, 56, 10, 8, 2)} {rrect(72, 56, 10, 8, 2)} {rrect(86, 56, 10, 8, 2)}")
    d.stroke("dark", "M76 50 V30", 2)
    d.shape("hero", "M22 72 H134 L126 96 H34Z", spot=True)
    d.shape("light", "M28 80 H131 L129 85 H30Z", shadow=False)
    group(d, "translate(196 92) scale(-.56 .56)", lambda: great_white(d, body="dark"))
    if not d.paper:
        d.stroke("dark", waves(90, 2.5, 22), 2)


# ================================================================ CLIFF JUMPING
def jumper(d: Drawing, suit="pop", skin="dark"):
    """A person dropping feet first, arms up; centred on x=110, head at y=70."""
    d.limb(skin, "M106 96 L104 126 M114 96 L116 126", 6)
    d.limb(skin, "M106 80 L94 58 M114 80 L126 58", 5)
    d.shape(skin, rrect(103.5, 75, 13, 25, 6.5))
    d.shape(suit, rrect(103.3, 91, 13.4, 9, 3), shadow=False, spot=True)
    d.shape(skin, circle(110, 69, 7.5))


def cliff_leap(d: Drawing):
    d.disc("glow", 156, 58, 16)
    d.shape("light", cloud(116, 32, 0.8), shadow=False)
    d.band("far", "M-30 136 H230")
    d.shape("deep", "M-30 46 H30 Q42 46 44 58 L50 96 L44 124 L54 160 L40 200 H-30Z")
    d.shape("near", "M-30 46 H30 Q42 46 44 58 L46 72 L30 66 L-30 70Z", shadow=False)
    d.shape("mid", "M-30 40 H34 Q42 40 44 48 H-30Z")
    for i, (x, y) in enumerate([(52, 34), (62, 30), (72, 30), (82, 33), (91, 38)]):
        d.marks("dark", circle(x, y, 1.6))
    jumper(d)
    d.band("mid", waves(150, 4, 30))
    d.stroke("light", ellipse(112, 156, 16, 3.5), 2)
    d.stroke("light", ellipse(112, 156, 28, 6), 1.6, line=False)
    d.band("near", waves(170, 4, 34))
    d.band("deep", waves(188, 4, 38), line=False)


def cliff_splash(d: Drawing):
    d.disc("glow", 140, 48, 13)
    d.band("far", "M-30 120 H230")
    d.shape("deep", "M-30 40 L26 42 L40 70 L34 100 L48 132 H-30Z")
    d.shape("near", "M230 52 L152 54 L146 76 L154 104 L142 132 H230Z")
    group(d, "translate(122.5 18) scale(.36)", lambda: d.limb("dark", "M107 96 L106 126 M113 96 L114 126 M106 80 L94 58 M114 80 L126 58 M110 78 L110.6 96", 6))
    d.shape("dark", circle(162, 41.5, 2.8), shadow=False)
    d.limb("dark", "M162 43 L162.3 51", 4.5, shadow=False)
    d.band("mid", waves(136, 3, 26))
    d.shape("light", "M58 150 C60 128 52 112 62 98 C68 114 74 118 78 104 C80 88 88 76 98 66 C100 82 104 92 110 82 "
                     "C114 74 122 72 132 66 C126 84 126 98 130 104 C134 96 140 92 148 88 C146 106 140 128 142 150Z")
    d.shape("far", "M76 150 C78 132 74 120 82 112 C86 124 92 124 96 114 C100 106 106 102 112 104 C108 116 112 124 118 120 "
                   "C122 116 126 114 130 114 C128 126 126 138 126 150Z", shadow=False, line=False)
    for x, y, r in [(50, 84, 3.5), (72, 72, 2.6), (124, 50, 3), (150, 70, 3.6), (160, 96, 2.4), (92, 50, 2.2)]:
        d.shape("light", circle(x, y, r), shadow=False)
    d.band("near", waves(156, 4, 30))
    d.shape("light", ellipse(100, 154, 52, 8), shadow=False)
    d.stroke("light", ellipse(100, 162, 70, 10), 2, line=False)
    d.band("deep", waves(178, 4, 36), line=False)


def cliff_toes(d: Drawing):
    d.band("far", "M-30 -10 H230")
    d.band("mid", "M-30 60 Q40 40 90 56 T230 40", line=False)
    d.stroke("light", "M30 96 q6 -4 12 0 M120 40 q6 -4 12 0 M150 74 q6 -4 12 0", 2)
    d.stroke("light", ellipse(98, 72, 9, 3), 1.6)
    d.stroke("light", ellipse(98, 72, 16, 5.5), 1.4, line=False)
    d.shape("light", "M140 102 L160 102 L156 108 L142 108Z")
    d.stroke("dark", "M150 102 V88", 1.4)
    d.shape("pop", "M151 89 L160 99 H151Z", shadow=False)
    d.band("deep", "M-30 124 L10 118 L30 126 L56 116 L84 122 L112 114 L140 122 L168 116 L230 124")
    d.band("near", "M-30 150 L20 142 L60 150 L120 140 L170 148 L230 142", shadow=False, line=False)

    def foot(x, flip):
        k = -1 if flip else 1
        d.shape("hero2", f"M{x-11*k} 200 C{x-14*k} 170 {x-14*k} 140 {x-9*k} 128 C{x-6*k} 120 {x+6*k} 118 {x+10*k} 124 "
                          f"C{x+14*k} 132 {x+12*k} 170 {x+11*k} 200Z")
        for i, (dx, dy, r) in enumerate([(-7, 119, 3.8), (-1.5, 116, 3), (3.5, 116.5, 2.7), (7.5, 119, 2.4), (10.5, 123, 2.1)]):
            d.shape("hero2", circle(x + dx * k, dy, r), shadow=False)
    foot(80, False)
    foot(120, True)


# ================================================================ HOT SPRINGS
def steam(d: Drawing, pts, h=26):
    for x, y in pts:
        d.stroke("light", f"M{x} {y} q-5 {-h/4} 0 {-h/2} q5 {-h/4} 0 {-h/2}", 3)


def spring_monkey(d: Drawing):
    d.band("far", hills(108, 10), shadow=True)
    d.shape("light", "M-30 104 Q40 86 100 100 Q140 108 230 96 V102 Q140 114 100 106 Q40 94 -30 110Z", shadow=False, line=False)
    for x, y in [(30, 50), (54, 34), (160, 44), (140, 66), (176, 76), (40, 80)]:
        d.marks("light", circle(x, y, 2.2))
    d.shape("hero", ellipse(100, 140, 40, 24))
    d.shape("hero", "M66 98 C62 74 80 58 100 58 C120 58 138 74 134 98 C132 116 118 128 100 128 C82 128 68 116 66 98Z")
    d.shape("hero", circle(66, 94, 7), shadow=False)
    d.shape("hero", circle(134, 94, 7), shadow=False)
    d.shape("hero2", "M100 84 C110 76 124 82 121 98 C119 112 110 120 100 120 C90 120 81 112 79 98 C76 82 90 76 100 84Z", spot=True)
    d.marks("mark", circle(92, 96, 2.8) + circle(108, 96, 2.8))
    d.stroke("mark", "M96 108 Q100 111 104 108", 1.6)
    d.marks("mark", circle(97.5, 103, 1) + circle(102.5, 103, 1))
    d.shape("light", "M78 66 C86 54 114 54 122 66 C116 70 108 66 100 68 C92 66 84 70 78 66Z")
    d.band("mid", waves(134, 3, 24))
    d.stroke("light", "M60 140 Q72 136 84 140 M118 142 Q130 138 142 142", 2, line=False)
    d.shape("deep", "M-30 150 C0 136 30 142 40 160 C44 176 30 190 -30 200Z")
    d.shape("light", "M-30 150 C0 136 30 142 40 160 C26 150 4 148 -30 158Z", shadow=False)
    d.shape("deep", "M230 146 C196 134 168 146 164 164 C162 180 180 192 230 200Z")
    d.shape("light", "M230 146 C196 134 168 146 164 164 C178 152 200 150 230 156Z", shadow=False)
    d.band("near", waves(176, 3, 28))
    steam(d, [(60, 128), (144, 126)], 30)


def spring_bucket(d: Drawing):
    d.band("far", "M-30 120 Q60 112 100 118 T230 116")
    d.band("mid", waves(134, 3, 26))
    for x, y, rx, ry in [(26, 132, 18, 10), (176, 128, 20, 11), (40, 172, 22, 12), (164, 174, 18, 10)]:
        d.shape("deep", ellipse(x, y, rx, ry))
    steam(d, [(84, 70), (100, 62), (116, 70)], 30)
    d.shape("hero2", "M56 92 H144 L136 166 H64Z", spot=True)
    d.shape("mid", ellipse(100, 92, 44, 8), shadow=False)
    d.shape("hero2", ellipse(100, 92, 44, 8), extra='fill-opacity="0"', shadow=False)
    d.stroke("mark", "M76 98 L80 166 M100 100 V166 M124 98 L120 166", 1.2, line=False)
    d.limb("dark", "M57 110 H143 M61 150 H139", 4, shadow=False)
    d.limb("mark", "M120 92 L156 56", 4)
    d.shape("mark", ellipse(160, 52, 9, 6), extra='transform="rotate(-45 160 52)"')
    d.shape("light", "M44 84 C60 78 80 80 94 86 L92 112 C80 108 62 108 48 112Z")
    d.shape("pop", "M46 96 C60 92 78 92 93 98 L92.5 103 C78 98 60 98 47 102Z", shadow=False)


def spring_lagoon(d: Drawing):
    d.disc("glow", 150, 62, 14)
    d.band("far", "M-30 108 L20 82 L46 96 L84 56 L120 94 L148 72 L230 108")
    d.shape("light", "M84 56 L95 70 L89 68 L84 74 L78 67 L73 70Z", shadow=False)
    d.shape("light", "M148 72 L157 82 L152 81 L148 86 L143 80 L139 83Z", shadow=False)
    d.band("near", "M-30 122 Q100 108 230 122")
    d.shape("hero", "M18 152 C20 132 60 126 100 128 C140 130 182 134 184 152 C184 170 140 178 100 178 C60 178 18 172 18 152Z", spot=True)
    d.stroke("light", "M50 150 Q60 146 70 150 M120 160 Q132 156 144 160 M90 168 Q98 165 106 168", 2, line=False)
    for x, y, rx, ry in [(22, 140, 14, 9), (48, 128, 12, 7), (150, 130, 13, 7), (180, 144, 13, 9), (30, 172, 16, 9), (168, 176, 16, 8)]:
        d.shape("dark", ellipse(x, y, rx, ry))
    d.shape("light", cloud(52, 118, 1.3), shadow=False, extra='opacity=".92"')
    d.shape("light", cloud(86, 92, 1.1), shadow=False, extra='opacity=".85"')
    d.shape("light", cloud(110, 122, 1.0), shadow=False, extra='opacity=".92"')
    d.shape("ground", "M120 200 L140 200 L132 166 L120 166Z")
    d.stroke("dark", "M121 174 H133 M121 182 H135 M121 190 H137", 1.4)


# ================================================================ WATERFALL SWIM
def falls(d: Drawing, x0, x1, y0, y1, water="light", lines="far"):
    d.shape(water, f"M{x0} {y0} Q{(x0+x1)/2} {y0-4} {x1} {y0} L{x1+4} {y1} H{x0-4}Z", spot=False)
    step = (x1 - x0) / 4
    flow = " ".join(f"M{x0 + step*i:.1f} {y0+6} L{x0 + step*i + (i-2)*0.8:.1f} {y1-10}" for i in (1, 2, 3))
    d.stroke(lines, flow, 2)


def falls_jungle(d: Drawing):
    d.band("far", hills(84, 10))
    d.shape("deep", "M-30 52 Q30 44 82 50 L84 156 H-30Z")
    d.shape("deep", "M118 54 Q170 44 230 50 V156 H116Z")
    for cx, cy, r in [(4, 50, 14), (26, 44, 12), (48, 48, 13), (70, 50, 10), (128, 52, 11), (150, 46, 13), (174, 48, 12), (196, 52, 14)]:
        d.shape("mid", circle(cx, cy, r), shadow=False, line=False)
    falls(d, 82, 118, 48, 152)
    d.band("far", waves(150, 3, 24))
    d.shape("light", ellipse(100, 152, 30, 6), shadow=False)
    bubbles(d, [(70, 140, 2.5), (130, 138, 3), (78, 128, 2)])
    d.band("mid", waves(168, 3, 28))
    d.limb("dark", "M146 166 L156 150", 4.5)
    d.shape("dark", circle(140, 164, 6.5))
    d.shape("pop", "M133.5 163 A6.5 6.5 0 0 1 146.5 163Z", shadow=False, spot=True)
    for (tx, ty, ex, ey) in [(-10, 200, 36, 150), (-10, 200, 50, 176), (210, 200, 160, 150), (210, 200, 150, 178)]:
        d.shape("near", leaf(tx, ty, ex, ey, 0.42, 6))
    d.band("deep", waves(190, 3, 32), line=False)


def falls_rope(d: Drawing):
    falls(d, 140, 178, 30, 132)
    d.shape("deep", "M178 26 Q200 22 230 26 V140 H180Z")
    d.band("far", waves(130, 3, 24))
    d.shape("light", ellipse(160, 132, 24, 5), shadow=False)
    d.band("mid", waves(156, 3, 28))
    d.band("near", waves(178, 4, 32))
    d.limb("dark", "M24 200 Q34 120 22 40", 16)
    d.limb("dark", "M24 66 Q70 44 116 36", 8)
    for cx, cy, r in [(14, 30, 16), (40, 22, 14), (66, 20, 12), (92, 22, 11)]:
        d.shape("near", circle(cx, cy, r), shadow=True)
    for (tx, ty, ex, ey) in [(20, 32, -6, 12), (20, 32, 50, 14), (116, 34, 140, 26), (100, 38, 116, 58), (60, 46, 70, 64)]:
        d.shape("near", leaf(tx, ty, ex, ey, 0.42, 4), shadow=False)
    d.stroke("ground", "M96 38 L129 97", 2.2)
    d.limb("dark", "M128 96 L122 116 M131 98 L128 117", 4)
    d.shape("dark", circle(119, 105, 6.5))
    d.shape("dark", rrect(118, 112, 13, 22, 6.5), extra='transform="rotate(14 124 123)"')
    d.shape("pop", rrect(115.5, 126, 13, 8, 3), shadow=False, spot=True, extra='transform="rotate(14 124 123)"')
    d.limb("dark", "M118 132 L134 136 L132 152 M120 130 L138 128 L142 144", 5)


def falls_swimmer(d: Drawing):
    d.shape("deep", "M-30 20 H60 L62 140 H-30Z")
    d.shape("deep", "M140 20 H230 V140 H138Z")
    falls(d, 54, 146, 10, 132)
    for x, y, r in [(46, 118, 3), (156, 112, 2.6), (40, 96, 2), (162, 90, 2.4)]:
        d.shape("light", circle(x, y, r), shadow=False)
    d.band("far", waves(126, 3, 24))
    d.shape("light", "M36 130 C50 116 70 120 82 112 C96 120 110 116 120 112 C132 120 150 116 164 130Z", shadow=False)
    d.limb("dark", "M84 138 L72 104 M116 138 L128 104", 7)
    d.shape("dark", ellipse(100, 150, 26, 14))
    d.shape("dark", circle(100, 122, 13))
    d.shape("pop", "M87 118 A13 13 0 0 1 113 118 L113 120 H87Z", shadow=False, spot=True)
    d.band("mid", waves(150, 3, 26))
    d.stroke("light", ellipse(100, 152, 34, 5), 2)
    d.band("near", waves(172, 4, 30))


# ================================================================ FISHING
FISH_BIG = "M40 100 C56 78 96 70 128 86 L158 66 C152 84 152 98 160 118 L128 110 C98 124 56 120 40 100Z"


def big_fish(d: Drawing, body="hero", belly="light", spots="mark", spot=False):
    """A plump fish facing left, mouth at (40, 100)."""
    d.shape(body, "M76 80 C86 66 106 66 116 82Z")
    d.shape(body, FISH_BIG, spot=spot)
    d.shape(belly, "M44 104 C62 112 96 114 126 108 C98 122 58 120 44 104Z", shadow=False)
    d.shape(body, "M84 110 C88 120 96 126 104 128 C100 120 98 114 98 112Z", shadow=False)
    d.stroke(spots, "M64 88 Q58 98 64 110", 2)
    d.marks(spots, circle(84, 92, 2.2) + circle(96, 88, 2) + circle(104, 96, 2.2) + circle(116, 92, 1.8) + circle(92, 100, 1.8))
    d.marks(spots, circle(52, 94, 2.8))
    d.marks("light", circle(53, 93, 0.9))


def fish_hooked(d: Drawing):
    d.disc("glow", 150, 54, 16)
    d.band("far", hills(118, 10))
    d.band("mid", "M-30 140 H230")
    d.limb("dark", "M-10 106 Q20 60 54 32", 4.5)
    d.stroke("dark", "M54 32 Q56 52 58.6 65.5", 1.2)
    group(d, "rotate(36 96 108) translate(0 -4)", lambda: big_fish(d, spot=True))
    d.stroke("dark", "M58.6 65.5 q-4 4 0 7", 1.6)
    d.shape("light", spray(150, 154, 1.4, left=False), shadow=False)
    d.shape("light", spray(142, 154, 1.1, left=True), shadow=False)
    for x, y, r in [(116, 140, 2.4), (178, 128, 2.6), (124, 126, 2)]:
        d.shape("light", circle(x, y, r), shadow=False)
    d.band("near", waves(156, 4, 30))
    d.band("deep", waves(180, 4, 36), line=False)


def fish_boat(d: Drawing):
    d.disc("glow", 100, 112, 40)
    d.band("far", "M-30 112 L20 88 L50 102 L86 72 L122 100 L150 84 L230 112")
    d.band("mid", "M-30 124 H230")
    d.stroke("light", "M60 140 H90 M112 140 H150 M74 150 H130", 2.4, line=False)
    d.limb("dark", "M84 120 L110 64", 3)
    d.stroke("dark", "M110 64 Q150 70 160 138", 1.2)
    d.stroke("light", ellipse(160, 140, 8, 2.5), 1.6)
    d.shape("dark", circle(70, 100, 6.5))
    d.shape("hero2", "M62 98 L78 98 L72 89 L68 89Z M60 98 H80 V100 H60Z", shadow=False, spot=True)
    d.shape("dark", rrect(62, 106, 16, 22, 7))
    d.limb("dark", "M74 112 L86 118", 4)
    d.shape("hero", "M36 124 H134 C128 136 118 140 104 140 H58 C46 140 40 134 36 124Z", spot=True)
    d.shape("light", "M38 128 H132 L131 130 H39Z", shadow=False)
    d.band("near", waves(162, 3, 32))
    d.band("deep", waves(184, 3, 36), line=False)


def fish_bobber(d: Drawing):
    d.band("far", hills(78, 8))
    for x in (20, 30, 40):
        d.limb("near", f"M{x} 92 Q{x-2} 70 {x+4} 50", 2.6, shadow=False)
        d.shape("deep", ellipse(x + 4, 52, 3, 8), shadow=False)
    d.band("mid", "M-30 90 H230")
    d.band("near", waves(130, 3, 28), line=False)
    d.band("deep", waves(170, 3, 34), line=False)
    if not d.paper:
        d.stroke("dark", "M-30 90 H230", 2)
    d.stroke("dark", "M112 30 L112.4 64", 1.2)
    d.stroke("light", ellipse(112, 92, 20, 4), 2)
    d.stroke("light", ellipse(112, 92, 34, 7), 1.6, line=False)
    d.stroke("dark", "M112 98 V138", 1.2)
    d.stroke("dark", "M112 138 V146 Q112 152 106 150", 1.6)
    d.limb("pop", "M106 140 Q100 146 106 152 Q112 156 108 162", 3.2)
    d.shape("light", "M100 80 A12 12 0 0 0 124 80 Q124 96 112 98 Q100 96 100 80Z")
    d.shape("pop", "M100 80 A12 12 0 0 1 124 80Z", spot=True, shadow=False)
    d.shape("pop", "M100 80 C100 66 124 66 124 80Z", spot=True)
    d.shape("light", rrect(109.5, 58, 5, 10, 2.5), shadow=False)
    group(d, "translate(176 104) scale(-.62 .62)", lambda: big_fish(d))
    bubbles(d, [(66, 132, 2.4), (62, 120, 3)])


# ================================================================ BEACH DAY
def parasol(d: Drawing, x, y, r, tilt, a="hero", b="light"):
    def draw():
        d.limb("dark", f"M0 0 L1 {r*1.6}", 3)
        dome = f"M{-r} 0 C{-r} {-r*0.9} {r} {-r*0.9} {r} 0 Q{r*0.75} {-r*0.12} {r*0.5} 0 Q{r*0.25} {-r*0.12} 0 0 Q{-r*0.25} {-r*0.12} {-r*0.5} 0 Q{-r*0.75} {-r*0.12} {-r} 0Z"
        d.shape(a, dome)
        d.shape(b, f"M{-r*0.5} 0 C{-r*0.5} {-r*0.5} {-r*0.18} {-r*0.66} 0 {-r*0.68} C{-r*0.08} {-r*0.6} {-r*0.18} {-r*0.3} 0 0 Q{-r*0.25} {-r*0.12} {-r*0.5} 0Z", shadow=False, spot=True)
        d.shape(b, f"M{r*0.5} 0 C{r*0.5} {-r*0.5} {r*0.18} {-r*0.66} 0 {-r*0.68} C{r*0.08} {-r*0.6} {r*0.18} {-r*0.3} 0 0 Q{r*0.25} {-r*0.12} {r*0.5} 0Z", shadow=False, spot=True)
        d.shape("dark", circle(0, -r * 0.7, 2.5), shadow=False)
    group(d, f"translate({x} {y}) rotate({tilt})", draw)


def beach_parasol(d: Drawing):
    d.disc("glow", 46, 56, 14)
    d.band("far", "M-30 102 H230")
    d.band("mid", waves(116, 3, 26))
    d.shape("light", "M-30 126 Q30 118 80 126 T230 124 V132 H-30Z", shadow=False, line=False)
    d.band("ground", "M-30 130 Q60 122 120 130 T230 128")
    d.shape("near", ellipse(118, 166, 36, 6), shadow=False, line=False)
    d.shape("hero2", "M54 150 L128 144 L140 172 L62 180Z", spot=True)
    d.stroke("light", "M60 156 L132 150 M64 172 L137 166", 3, line=True)
    parasol(d, 112, 84, 46, -12)
    d.shape("pop", circle(160, 146, 10))
    d.shape("light", "M150 146 A10 10 0 0 1 160 136 L160 156 A10 10 0 0 1 150 146Z", shadow=False)


def castle(d: Drawing, tower):
    d.shape("hero2", "M48 166 H146 V174 H48Z")
    d.shape("hero2", tower(58, 116, 30, 52))
    d.shape("hero2", tower(106, 116, 30, 52))
    d.shape("hero2", tower(80, 96, 34, 72))
    d.stroke("dark", "M97 94 L97.5 72", 1.6)
    d.shape("pop", "M98 72 L114 77 L98 82Z", spot=True, shadow=False)
    d.shape("dark", "M89 168 V150 A8 8 0 0 1 105 150 V168Z", shadow=False)
    d.marks("dark", rrect(67, 128, 8, 10, 3) + rrect(115, 128, 8, 10, 3) + rrect(93, 112, 8, 10, 3))


def beach_castle(d: Drawing):
    d.disc("glow", 152, 52, 14)
    d.band("far", "M-30 96 H230")
    d.band("mid", waves(110, 3, 26))
    d.band("ground", "M-30 124 Q60 116 120 124 T230 122")

    def tower(x, y, w, h):
        cren = f"M{x} {y} h{w/5:.1f} v-6 h{w/5:.1f} v6 h{w/5:.1f} v-6 h{w/5:.1f} v6 h{w/5:.1f} v-6"
        return f"{cren} H{x+w} V{y+h} H{x}Z".replace(f"v-6 H{x+w}", f"v-6 V{y}")
    group(d, "translate(-14 -4)", lambda: castle(d, tower))
    d.shape("hero", "M136 130 H164 L161 160 H139Z", spot=True)
    d.stroke("dark", "M138 132 Q150 114 162 132", 1.8)
    d.shape("light", "M136 137 H164 V140 H136Z", shadow=False)
    group(d, "translate(54 170) rotate(-20) scale(.7)", lambda: d.shape("pop", "M0 -16 L4 -5 L15 -5 L6 2 L10 13 L0 6 L-10 13 L-6 2 L-15 -5 L-4 -5Z", spot=True))
    d.band("near", hills(186, 4), line=False)


def beach_flipflops(d: Drawing):
    d.band("ground", "M-30 -10 H230")
    d.stroke("far", "M10 40 q10 -5 20 0 t20 0 M140 160 q10 -5 20 0 t20 0 M150 40 q10 -5 20 0", 1.6, line=False)
    d.shape("hero", "M-30 120 L60 -30 L180 -30 L50 230 H-30Z")
    d.stroke("light", "M-30 92 L44 -30 M-6 230 L120 -30", 6, line=False)

    def flop(x, y, rot):
        def draw():
            d.shape("hero2", "M0 -34 C14 -34 16 -16 13 0 C10 16 14 30 0 34 C-14 30 -10 16 -12 0 C-16 -16 -14 -34 0 -34Z", spot=True)
            d.limb("pop", "M-11 2 Q-8 -14 0 -22 Q8 -14 11 2", 4.5)
            d.marks("pop", circle(0, -22, 3))
        group(d, f"translate({x} {y}) rotate({rot})", draw)
    flop(84, 110, -14)
    flop(122, 116, 10)

    def shades():
        d.stroke("dark", "M126 56 Q134 50 142 56", 3)
        d.shape("dark", "M106 54 H128 C128 66 122 72 116 72 C110 72 106 66 106 54Z")
        d.shape("dark", "M140 54 H162 C162 66 158 72 152 72 C146 72 140 66 140 54Z")
        d.stroke("dark", "M106 54 L96 50 M162 54 L172 50", 3)
        d.shape("light", "M110 58 L116 58 L112 66Z M144 58 L150 58 L146 66Z", shadow=False, line=False)
    group(d, "translate(-12 14) rotate(-14 134 62)", shades)
    star = "M0 -16 L4 -5 L15 -5 L6 2 L10 13 L0 6 L-10 13 L-6 2 L-15 -5 L-4 -5Z"
    group(d, "translate(150 156) rotate(12) scale(1.1)", lambda: d.shape("pop", star, spot=True))
    d.shape("light", "M40 160 C40 150 54 146 60 152 C64 156 60 166 52 168 C46 170 40 166 40 160Z")
    d.stroke("far", "M44 160 Q50 154 56 158 M46 164 Q52 160 58 162", 1.2)


# ================================================================ BEACH HAMMOCK
def hammock(d: Drawing, x0, y0, x1, y1, sag, a="hero", b="hero2"):
    mx = (x0 + x1) / 2
    d.stroke("dark", f"M{x0} {y0} L{x0+14} {y0+6} M{x0} {y0} L{x0+14} {y0+12} M{x1} {y1} L{x1-14} {y1+6} M{x1} {y1} L{x1-14} {y1+12}", 1.4)
    outer = f"M{x0+14} {y0+4} Q{mx} {y0+sag*2.2} {x1-14} {y1+4} L{x1-14} {y1+14} Q{mx} {y0+sag*2.2+14} {x0+14} {y0+14}Z"
    d.shape(a, outer)
    d.shape(b, f"M{x0+14} {y0+8} Q{mx} {y0+sag*2.2+4} {x1-14} {y1+8} L{x1-14} {y1+10} Q{mx} {y0+sag*2.2+7} {x0+14} {y0+10}Z", shadow=False, spot=True)


def hammock_palms(d: Drawing):
    d.disc("glow", 100, 112, 34)
    d.band("far", "M-30 118 H230")
    d.band("mid", waves(132, 3, 26))
    d.band("ground", "M-30 150 Q60 140 120 148 T230 146")
    palm(d, 36, 176, 116, -14)
    palm(d, 162, 178, 112, 16)
    hammock(d, 30, 104, 168, 104, 26)
    d.band("near", hills(188, 4), line=False)


def hammock_feet(d: Drawing):
    d.disc("glow", 100, 44, 12)
    d.band("far", "M-30 70 H230")
    d.band("mid", waves(96, 3, 26))
    d.band("near", waves(124, 3, 30), line=False)
    d.band("ground", "M-30 156 Q60 148 120 154 T230 150")
    palm(d, 8, 200, 150, 14, trunk_w=7)
    palm(d, 192, 200, 150, -14, trunk_w=7)
    d.stroke("dark", "M17 92 L30 96 M183 92 L170 96", 1.6)
    d.limb("hero2", "M126 118 L152 90 M134 122 L162 96", 8)
    d.shape("hero2", "M148 92 C146 82 148 76 152 74 C157 74 160 80 158 92Z", extra='transform="rotate(30 154 86)"')
    d.shape("hero2", "M158 98 C156 88 158 82 162 80 C167 80 170 86 168 98Z", extra='transform="rotate(30 164 92)"')
    d.shape("hero", "M28 92 Q100 150 172 92 L174 104 Q100 168 26 104Z", spot=True)
    d.shape("light", "M27 97 Q100 158 173 97 L173.5 101 Q100 163 26.5 101Z", shadow=False)
    d.shape("glow2", "M40 100 C44 86 62 84 70 94 C82 96 82 104 68 106 C56 110 42 110 40 100Z")
    d.shape("pop", "M45 96 C53 92 63 92 70 94 L70 97 C62 96 53 97 45 100Z", shadow=False)
    d.shape("light", "M40 160 L60 160 L55 176 H45Z")
    d.shape("pop", ellipse(50, 160, 10, 2.5), shadow=False)
    d.stroke("dark", "M52 160 L58 144", 1.8)
    d.shape("pop", "M50 145 Q58 136 68 142Z", spot=True)


def hammock_hut(d: Drawing):
    d.disc("glow", 150, 60, 15)
    d.band("far", "M-30 112 H230")
    d.band("mid", waves(126, 3, 26))
    d.band("ground", "M-30 148 Q60 140 120 146 T230 144")
    d.limb("dark", "M34 168 L34.6 92 M86 168 L86.4 92", 5)
    d.shape("hero2", rrect(26, 88, 68, 50, 3))
    d.shape("dark", rrect(48, 104, 22, 34, 2), shadow=False)
    d.marks("mark", rrect(30, 96, 12, 3, 1) + rrect(78, 96, 12, 3, 1))
    d.shape("glow2", "M14 92 L60 54 L108 92 Q60 86 14 92Z")
    d.stroke("mark", "M24 88 L60 58 M60 58 L98 88 M40 86 L60 62 L80 86", 1.4, line=False)
    d.shape("near", rrect(22, 136, 76, 6, 2))
    palm(d, 168, 176, 110, 10)
    hammock(d, 86, 110, 170, 112, 16)
    d.band("near", hills(186, 4), line=False)


# ================================================================ concepts
CONCEPTS = [
    Concept("kite-rider", "kitesurfing", "Kite & rider", kite_rider,
            checks=[("hero", "sky"), ("hero2", "hero"), ("pop", "near"), ("dark", "near")],
            fixes={"hero": ["pop", "deep", "near"], "pop": ["hero2", "light"]}),
    Concept("kite-board", "kitesurfing", "Twin-tip board", kite_board,
            checks=[("hero", "mid"), ("hero", "near"), ("hero2", "hero")],
            fixes={"hero": ["pop", "dark", "deep"]}),
    Concept("kite-beach", "kitesurfing", "Kite beach", kite_beach,
            checks=[("hero", "sky"), ("pop", "sky"), ("hero2", "sky"), ("ground", "near")],
            fixes={"hero2": ["glow2", "pop", "deep"]}),
    Concept("dolphin-leap", "swimming-with-dolphins", "Leaping dolphin", dolphin_leap, overrides=DOLPHIN_GREY,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero", "far")],
            fixes={"glow": ["glow2", "#E07A5F", "pop"]}),
    Concept("dolphin-pod", "swimming-with-dolphins", "Dolphin pod", dolphin_pod, UNDERWATER, DOLPHIN_GREY,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "far")], fixes={"hero": ["#5B7287"]}),
    Concept("dolphin-swimmer", "swimming-with-dolphins", "Swim with a dolphin", dolphin_swimmer, UNDERWATER, DOLPHIN_GREY,
            checks=[("hero", "mid"), ("hero", "near"), ("hero2", "far")], fixes={"hero": ["#5B7287"]}),
    Concept("turtle-snorkel", "swimming-with-turtles", "Snorkel with a turtle", turtle_snorkel, UNDERWATER, TURTLE_GREEN,
            checks=[("hero", "mid"), ("hero2", "mid"), ("pop", "sky2")]),
    Concept("turtle-breath", "swimming-with-turtles", "Coming up for air", turtle_breath, overrides=TURTLE_GREEN,
            checks=[("hero2", "sky"), ("hero", "near"), ("hero", "far")]),
    Concept("turtle-hatchlings", "swimming-with-turtles", "Hatchlings to the sea", turtle_hatchlings, overrides=HATCHLING,
            checks=[("hero", "ground"), ("hero2", "ground")]),
    Concept("shark-cage", "shark-cage-diving", "Cage & great white", shark_cage, UNDERWATER, GREAT_WHITE,
            checks=[("hero", "mid"), ("hero", "near"), ("hero2", "mid")], fixes={"hero": ["#9AA9B6"]}),
    Concept("shark-jaws", "shark-cage-diving", "Jaws at the bars", clipline(shark_jaws), UNDERWATER, GREAT_WHITE,
            checks=[("hero", "mid"), ("hero", "near"), ("hero2", "hero"), ("hero2", "mid")], fixes={"hero": ["#9AA9B6"]}),
    Concept("shark-boat", "shark-cage-diving", "Cage boat", shark_boat, ["coastal", "dusk", "meadow", "golden"],
            checks=[("hero", "far"), ("hero", "sky"), ("hero2", "sky"), ("hero2", "hero"), ("dark", "near")],
            fixes={"hero": ["pop", "deep"], "hero2": ["light", "glow2"]}),
    Concept("cliff-leap", "cliff-jumping", "The leap", clipline(cliff_leap),
            checks=[("dark", "sky"), ("dark", "glow"), ("deep", "sky"), ("pop", "sky")]),
    Concept("cliff-splash", "cliff-jumping", "Big splash", clipline(cliff_splash),
            checks=[("light", "mid"), ("light", "far"), ("deep", "sky"), ("near", "sky")]),
    Concept("cliff-toes", "cliff-jumping", "Toes over the edge", clipline(cliff_toes), UNDERWATER + ["blush"], SKIN,
            checks=[("hero2", "deep"), ("hero2", "far"), ("deep", "far")]),
    Concept("spring-monkey", "hot-springs", "Snow monkey", clipline(spring_monkey), overrides=MONKEY,
            checks=[("hero", "sky"), ("hero", "mid"), ("hero2", "hero"), ("hero", "far")], fixes={"far": ["near", "deep"]}),
    Concept("spring-bucket", "hot-springs", "Onsen bucket", clipline(spring_bucket), overrides=WOOD,
            checks=[("hero2", "far"), ("hero2", "mid"), ("light", "hero2")], fixes={"far": ["near", "deep"], "mid": ["near", "deep"]}),
    Concept("spring-lagoon", "hot-springs", "Steaming lagoon", spring_lagoon, overrides={"hero": "#7FD0D8"},
            checks=[("hero", "near"), ("hero", "dark"), ("light", "far")], fixes={"near": ["deep", "mid"]}),
    Concept("falls-jungle", "waterfall-swim", "Jungle falls", clipline(falls_jungle),
            checks=[("light", "deep"), ("far", "deep"), ("light", "far"), ("mid", "deep")], fixes={"far": ["mid", "near"]}),
    Concept("falls-rope", "waterfall-swim", "Rope swing", clipline(falls_rope),
            checks=[("dark", "sky"), ("dark", "far"), ("light", "deep"), ("near", "sky")]),
    Concept("falls-swimmer", "waterfall-swim", "Under the falls", clipline(falls_swimmer),
            checks=[("dark", "light"), ("light", "deep"), ("dark", "far")]),
    Concept("fish-hooked", "fishing", "Fish on the line", fish_hooked,
            checks=[("hero", "sky"), ("hero", "far"), ("hero", "mid"), ("light", "mid")], fixes={"hero": ["pop", "deep", "near"]}),
    Concept("fish-boat", "fishing", "Lake at dawn", fish_boat,
            checks=[("hero", "mid"), ("dark", "glow"), ("dark", "mid")], fixes={"hero": ["pop", "light"]}),
    Concept("fish-bobber", "fishing", "Bobber & bite", fish_bobber,
            checks=[("pop", "mid"), ("pop", "sky"), ("hero", "near"), ("light", "mid")], fixes={"pop": ["hero", "deep"]}),
    Concept("beach-parasol", "beach-day", "Parasol & towel", beach_parasol,
            checks=[("hero", "sky"), ("hero", "mid"), ("hero2", "ground"), ("pop", "ground")], fixes={"hero2": ["pop", "hero"], "hero": ["pop", "deep"]}),
    Concept("beach-castle", "beach-day", "Sandcastle", beach_castle,
            checks=[("hero2", "ground"), ("hero2", "sky"), ("hero", "ground")], fixes={"hero2": ["glow", "far", "mid"]}),
    Concept("beach-flipflops", "beach-day", "Flip-flops & shades", clipline(beach_flipflops),
            checks=[("hero2", "hero"), ("hero2", "ground"), ("dark", "ground"), ("pop", "hero2")], fixes={"hero2": ["light", "glow2"]}),
    Concept("hammock-palms", "beach-hammock", "Between two palms", hammock_palms,
            checks=[("hero", "glow"), ("hero", "sky"), ("hero", "far"), ("hero2", "hero")], fixes={"hero": ["pop", "deep"]}),
    Concept("hammock-feet", "beach-hammock", "Feet up", clipline(hammock_feet), overrides=SKIN,
            checks=[("hero", "near"), ("hero", "ground"), ("hero2", "far"), ("hero2", "mid"), ("glow2", "hero")],
            fixes={"hero": ["pop", "deep"], "glow2": ["hero2", "light"], "far": ["near", "mid"], "mid": ["near", "deep"]}),
    Concept("hammock-hut", "beach-hammock", "Beach hut", hammock_hut,
            checks=[("hero2", "sky"), ("hero2", "far"), ("glow2", "sky"), ("glow2", "hero2"), ("hero", "far")],
            fixes={"glow2": ["mid", "near", "far"], "hero2": ["near", "pop", "hero"], "hero": ["pop", "deep"]}),
]
