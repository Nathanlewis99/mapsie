"""Water B: kitesurfing, dolphins, turtles, shark cage, cliff jumping, hot springs,
waterfall swim, fishing, beach day and beach hammock. Three concepts each."""
import os

from _common import Concept, Drawing, cloud, fish, circle, ellipse, waves, hills, rrect, group, bubbles, water

UNDERWATER = ["coastal", "dusk", "meadow"]
DOLPHIN_GREY = {"hero": "#7C95AB", "light": "#E4ECF2", "mark": "#1E3242"}
TURTLE_GREEN = {"hero": "#6E8B3D", "hero2": "#B9C77A", "mark": "#33461C"}
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


def kite_canopy(d: Drawing, body="hero", stripe="hero2", s=1.0):
    d.shape(body, KITE)
    d.shape(stripe, "M70 38 C80 34 90 33 100 32 L100 48 C88 48 78 50 68 54Z", shadow=False, spot=True)
    d.shape(stripe, "M130 38 C120 34 110 33 100 32 L100 48 C112 48 122 50 132 54Z", shadow=False, spot=True)
    d.stroke("dark", "M50 52 L58 64 M70 38 L68 54 M100 32 V48 M130 38 L132 54 M150 52 L142 64", 1.4, line=False)


def kite_rider(d: Drawing):
    d.disc("glow", 160, 98, 16)
    d.shape("light", cloud(18, 92, 0.9), shadow=False)
    d.band("far", "M-30 118 H230")
    d.band("mid", waves(138, 4, 30))
    group(d, "translate(14 -6) scale(.86)", lambda: kite_canopy(d))
    # flying lines from the wing tips to the bar
    d.stroke("dark", "M42 59 L94 128 M160 59 L108 132", 1.1)
    d.band("near", waves(162, 5, 34))
    # rider leaning back against the pull
    d.shape("light", "M126 170 C140 160 152 158 160 150 C156 162 146 172 130 176Z", shadow=False)
    d.limb("dark", "M84 167 L86 152 L82 140 M98 165 L96 152 L82 140", 5)
    d.limb("dark", "M82 140 L80 124", 7)
    d.limb("dark", "M82 128 L96 129 M82 128 L105 133", 3.6)
    d.stroke("pop", "M92 125 L110 136", 3)
    d.shape("dark", circle(77, 117, 6))
    d.shape("hero2", "M71 115 A6 6 0 0 1 83 115Z", shadow=False)
    d.shape("pop", rrect(64, 162, 58, 7, 3.5), spot=True, extra='transform="rotate(-8 93 165)"')
    d.band("deep", waves(184, 4, 38), line=False)


def kite_board(d: Drawing):
    d.disc("glow", 50, 54, 15)
    group(d, "translate(118 20) scale(.36)", lambda: kite_canopy(d, "pop", "light"))
    d.stroke("dark", "M131 41 L152 96 M175 41 L156 96", 0.9, line=False)
    sea(d, 92)
    d.band("deep", waves(170, 5, 38), line=False)

    def board():
        d.shape("light", "M30 116 C36 96 50 86 64 82 C56 94 54 104 58 116Z", shadow=False)
        d.shape("light", "M34 128 C44 118 50 104 46 92 C58 104 58 120 50 132Z", shadow=False)
        d.shape("hero", rrect(36, 104, 128, 34, 17))
        d.shape("hero2", "M52 106 H148 C156 106 162 112 162 121 H38 C38 112 44 106 52 106Z", shadow=False, spot=True)
        for x in (64, 136):
            d.shape("dark", rrect(x - 10, 110, 20, 18, 6), shadow=False)
            d.shape("light", rrect(x - 13, 114, 26, 8, 4))
        d.shape("dark", rrect(94, 116, 12, 6, 3), shadow=False)
    group(d, "rotate(-14 100 121)", board)


def kite_beach(d: Drawing):
    d.disc("glow", 62, 74, 18)
    group(d, "translate(18 20) scale(.62)", lambda: kite_canopy(d))
    group(d, "translate(108 36) scale(.4) rotate(14 100 50)", lambda: kite_canopy(d, "pop", "light"))
    group(d, "translate(128 82) scale(.26) rotate(-10 100 50)", lambda: kite_canopy(d, "hero2", "light"))
    d.band("far", "M-30 136 Q8 118 40 122 Q60 124 70 136 H230")
    d.stroke("dark", "M37 56 L76 148 M118 56 L82 150", 1)
    d.stroke("dark", "M126 64 L148 140 M150 56 L152 140", 0.9)
    d.stroke("dark", "M135 96 L170 130 M152 98 L172 130", 0.8, line=False)
    d.band("mid", waves(146, 3, 26))
    d.shape("dark", "M70 152 L90 148 L91 151 L71 155Z", shadow=False)
    d.shape("dark", "M146 143 L160 141 L160 143 L146 145Z", shadow=False)
    d.band("near", waves(160, 4, 30))
    d.band("ground", "M-30 176 Q60 164 120 172 T230 170")


# ================================================================ DOLPHINS
def dolphin_leap(d: Drawing):
    d.disc("glow", 128, 96, 32)
    d.shape("light", cloud(26, 62, 1.0), shadow=False)
    d.band("far", "M-30 128 H230")
    group(d, "translate(-2 -14) rotate(-24 95 100)", lambda: dolphin(d, spot=True))
    d.band("mid", waves(140, 4, 30))
    d.shape("light", spray(56, 150, 1.0, left=True), shadow=False)
    d.shape("light", spray(62, 150, 0.8, left=False), shadow=False)
    d.band("near", waves(156, 5, 34))
    d.band("deep", waves(178, 4, 38), line=False)


def dolphin_pod(d: Drawing):
    water(d, bottom=False)
    d.raw('<g opacity=".16" fill="#fff"><path d="M50 0 L70 0 L108 200 L88 200Z"/><path d="M120 0 L134 0 L172 200 L158 200Z"/></g>', "")
    group(d, "translate(36 22) scale(.58) rotate(12 95 100)", lambda: dolphin(d))
    group(d, "translate(-4 46) scale(.9) rotate(-6 95 100)", lambda: dolphin(d, spot=True))
    bubbles(d, [(162, 80, 3), (168, 66, 4.2), (160, 54, 2.4)])
    d.band("ground", "M-30 182 Q40 170 90 180 T230 176")


def dolphin_swimmer(d: Drawing):
    water(d, bottom=False)
    # snorkeller floating at the surface
    def swimmer():
        d.limb("dark", "M112 52 L140 46 M112 58 L142 60", 7)
        d.shape("pop", ellipse(150, 42, 11, 4.5), extra='transform="rotate(-14 150 42)"', spot=True)
        d.shape("pop", ellipse(152, 62, 11, 4.5), extra='transform="rotate(10 152 62)"', spot=True)
        d.shape("hero2", rrect(66, 46, 52, 18, 9))
        d.limb("hero2", "M74 60 Q60 70 46 66", 6)
        d.shape("hero2", circle(60, 52, 10))
        d.shape("dark", rrect(48, 49, 12, 9, 3), shadow=False)
        d.shape("light", rrect(50, 51, 8, 5, 2), shadow=False)
        d.stroke("pop", "M66 46 V34", 3)
    swimmer()
    group(d, "translate(6 52) scale(.86) rotate(-4 95 100)", lambda: dolphin(d, spot=False))
    bubbles(d, [(38, 96, 2.5), (32, 84, 3.5)])
    d.band("ground", "M-30 184 Q40 172 90 182 T230 178")


# ================================================================ TURTLES
def turtle_snorkel(d: Drawing):
    water(d)
    d.limb("pop", "M160 178 V156 M160 165 L151 153 M160 162 L170 150", 5.5)
    group(d, "translate(20 34) scale(.7) rotate(-12 100 93)", lambda: turtle_top(d))

    def swimmer():
        d.limb("dark", "M68 46 L42 40 M68 52 L40 54", 7)
        d.shape("pop", ellipse(32, 36, 11, 4.5), extra='transform="rotate(14 32 36)"', spot=True)
        d.shape("pop", ellipse(30, 56, 11, 4.5), extra='transform="rotate(-10 30 56)"', spot=True)
        d.shape("hero2", rrect(64, 40, 52, 18, 9))
        d.limb("hero2", "M108 54 Q122 66 136 64", 6)
        d.shape("hero2", circle(124, 46, 10))
        d.shape("dark", rrect(124, 43, 12, 9, 3), shadow=False)
        d.shape("light", rrect(126, 45, 8, 5, 2), shadow=False)
        d.stroke("pop", "M118 40 V26", 3)
    swimmer()
    bubbles(d, [(150, 96, 2.5), (156, 84, 3.5)])


TURTLE_SIDE = "M60 112 C62 88 82 74 108 74 C132 74 148 90 150 110 C126 116 86 118 60 112Z"


def turtle_breath(d: Drawing):
    d.disc("glow", 52, 52, 18)
    d.shape("light", cloud(128, 46, 1.1), shadow=False)
    d.band("far", "M-30 96 H230")
    d.band("mid", waves(104, 3, 24), line=False)
    # turtle rising, head poking above the water
    def turtle():
        d.shape("hero2", "M140 104 C148 92 150 78 156 70 C162 64 172 66 174 72 C176 80 168 86 160 92 L152 110Z")
        d.shape("hero2", "M104 112 C112 124 126 140 146 146 C134 132 124 120 120 108Z")
        d.shape("hero2", "M68 108 C64 118 58 124 50 128 C60 128 70 122 78 114Z")
        d.shape("hero", TURTLE_SIDE)
        d.shape("hero2", "M60 112 C86 118 126 116 150 110 C146 116 140 120 134 120 C110 124 84 122 64 118Z", shadow=False)
        d.stroke("mark", "M80 108 C82 96 90 86 100 82 M100 82 C112 82 124 86 132 96 C136 100 138 106 138 110 "
                         "M100 82 C98 92 100 104 104 114 M80 96 H122", 2)
        d.marks("mark", circle(165, 72, 1.9))
    group(d, "rotate(-14 110 100)", turtle)
    d.band("near", waves(112, 3, 26), shadow=False)
    d.stroke("light", "M140 98 Q154 94 168 98 M128 104 Q150 100 176 104", 2, line=False)
    d.band("deep", waves(160, 4, 36), line=False)
    bubbles(d, [(94, 140, 2.5), (100, 152, 3.5), (86, 160, 2)])


def turtle_hatchlings(d: Drawing):
    d.disc("glow", 140, 52, 16)
    d.band("far", "M-30 86 H230")
    d.band("mid", waves(96, 3, 26))
    d.shape("light", "M-30 108 Q20 100 60 108 T150 106 T230 108 V114 H-30Z", shadow=False, line=False)
    d.band("ground", "M-30 112 Q40 106 100 112 T230 110")
    d.stroke("near", "M50 168 q-4 -8 0 -16 q4 -8 0 -16 M118 172 q-4 -8 0 -16 q4 -8 0 -16", 1.4, line=False)
    d.shape("near", ellipse(150, 172, 26, 9))
    for x, y in [(138, 168), (152, 166), (162, 172)]:
        d.shape("light", ellipse(x, y, 5, 4), shadow=False)

    def baby(x, y, s, rot):
        def draw():
            d.shape("hero2", ellipse(-9, -7, 7, 2.5), extra='transform="rotate(-50 -9 -7)"')
            d.shape("hero2", ellipse(9, -7, 7, 2.5), extra='transform="rotate(50 9 -7)"')
            d.shape("hero2", ellipse(-6, 8, 5, 2), extra='transform="rotate(40 -6 8)"')
            d.shape("hero2", ellipse(6, 8, 5, 2), extra='transform="rotate(-40 6 8)"')
            d.shape("hero2", circle(0, -14, 4.5))
            d.shape("hero", ellipse(0, 0, 9, 11), spot=True)
            d.stroke("mark", "M0 -8 V8 M-6 -2 H6", 1.2, line=False)
        group(d, f"translate({x} {y}) rotate({rot}) scale({s})", draw)
    baby(54, 138, 1.25, -8)
    baby(96, 128, 1.15, 6)
    baby(122, 150, 1.3, 14)


# ================================================================ concepts
CONCEPTS = [
    Concept("kite-rider", "kitesurfing", "Kite & rider", kite_rider,
            checks=[("hero", "sky"), ("hero2", "hero"), ("pop", "near"), ("dark", "near")],
            fixes={"hero": ["pop", "deep", "near"]}),
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
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "far")]),
    Concept("dolphin-swimmer", "swimming-with-dolphins", "Swim with a dolphin", dolphin_swimmer, UNDERWATER, DOLPHIN_GREY,
            checks=[("hero", "mid"), ("hero", "near"), ("hero2", "far")]),
    Concept("turtle-snorkel", "swimming-with-turtles", "Snorkel with a turtle", turtle_snorkel, UNDERWATER, TURTLE_GREEN,
            checks=[("hero", "mid"), ("hero2", "mid"), ("hero2", "sky2")]),
    Concept("turtle-breath", "swimming-with-turtles", "Coming up for air", turtle_breath, overrides=TURTLE_GREEN,
            checks=[("hero2", "sky"), ("hero", "near"), ("hero", "far")]),
    Concept("turtle-hatchlings", "swimming-with-turtles", "Hatchlings to the sea", turtle_hatchlings, overrides=HATCHLING,
            checks=[("hero", "ground"), ("hero2", "ground")]),
]

_only = os.environ.get("WB_ONLY")  # dev filter while drawing: comma-separated activity ids
if _only:
    CONCEPTS = [c for c in CONCEPTS if c.activity in _only.split(",")]
