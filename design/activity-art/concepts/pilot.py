"""Pilot concepts: three ideas each for scuba diving, hot air balloon and safari."""
from _common import *  # noqa: F401,F403
from _common import Concept, Drawing, cloud, fish, circle, ellipse, waves, hills, rrect, group, balloon, bubbles, water, acacia
from _common import BALLOON, GIRAFFE, GIRAFFE_SPOTS


# ================================================================ SCUBA
def scuba_diver(d: Drawing):
    water(d)
    d.limb("pop", "M48 174 V150 M48 160 L38 146 M48 156 L59 142", 6)
    for x, y in [(138, 52), (154, 44), (156, 62)]:
        d.shape("hero2", fish(x, y))

    def diver():
        d.stroke("pop", "M84 86 Q60 78 47 99", 2.6)
        d.shape("hero2", rrect(78, 80, 46, 15, 7.5), spot=True)
        d.limb("dark", "M128 97 L152 87", 8)
        d.limb("dark", "M130 107 L155 107", 8)
        d.shape("pop", ellipse(166, 81, 14, 5.5), extra='transform="rotate(-24 166 81)"', spot=True)
        d.shape("pop", ellipse(169, 108, 14, 5.5), extra='transform="rotate(4 169 108)"', spot=True)
        d.shape("dark", rrect(60, 93, 74, 21, 10.5))
        d.limb("dark", "M73 111 Q58 119 41 118", 7)
        d.shape("dark", circle(54, 103, 12))
        d.shape("hero2", rrect(40, 97, 15, 11, 3.5), shadow=False)
        d.shape("light", rrect(42.5, 99.5, 10, 6, 2), shadow=False)
    group(d, "rotate(-8 100 100)", diver)
    bubbles(d, [(36, 84, 3), (31, 70, 4.5), (38, 56, 2.5)])


SHARK = ("M30 100 C45 86 75 78 110 80 C135 81 152 86 165 92 L186 72 C183 88 182 98 187 114 L166 104 "
         "C150 112 125 118 100 116 C70 115 45 110 30 100Z")
SHARK_BELLY = "M34 101 C55 108 85 113 110 112 C130 111 148 107 162 101 C150 112 125 118 100 116 C70 115 45 110 34 101Z"


def scuba_shark(d: Drawing):
    water(d)
    d.raw('<g opacity=".18" fill="#fff"><path d="M60 0 L82 0 L120 200 L98 200Z"/><path d="M118 0 L130 0 L170 200 L158 200Z"/></g>', "")
    d.limb("pop", "M150 176 V154 M150 162 L141 150 M150 159 L160 147", 5.5)
    d.shape("glow2", "M24 178 a20 16 0 0 1 40 0Z")
    d.stroke("dark", "M30 172 Q38 166 46 172 M40 168 Q48 162 56 168", 1.6)
    d.shape("dark", "M98 81 L113 54 L125 82Z")
    d.shape("dark", SHARK)
    d.shape("light", SHARK_BELLY, shadow=False)
    d.shape("dark", "M84 112 L72 134 L101 116Z", shadow=False)
    d.stroke("light", "M66 92 Q64 98 66 104 M71 91 Q69 97 71 103 M76 91 Q74 97 76 103", 1.5)
    d.marks("light", circle(46, 95, 2.4))
    d.stroke("mark", "M36 103 Q44 106 52 104", 1.6, line=False)
    for x, y, s in [(140, 140, 0.8), (154, 132, 0.7), (128, 150, 0.7), (60, 56, 0.9), (74, 48, 0.8)]:
        d.shape("hero2", fish(x, y, s), shadow=False)
    bubbles(d, [(26, 90, 2.5), (22, 78, 3.5)])


def scuba_turtle(d: Drawing):
    water(d)
    d.limb("pop", "M38 178 V156 M38 165 L29 153 M38 162 L48 150", 5.5)
    d.shape("glow2", "M142 180 a22 18 0 0 1 44 0Z")
    d.stroke("mark", "M148 174 Q156 166 164 174 M158 170 Q166 162 174 170", 1.6)
    for x, y, s in [(150, 50, 0.8), (164, 58, 0.7)]:
        d.shape("pop", fish(x, y, s), shadow=False)

    def turtle():
        d.shape("hero2", ellipse(74, 70, 20, 6.5), extra='transform="rotate(-38 74 70)"')
        d.shape("hero2", ellipse(76, 116, 20, 6.5), extra='transform="rotate(36 76 116)"')
        d.shape("hero2", ellipse(132, 78, 11, 5), extra='transform="rotate(30 132 78)"')
        d.shape("hero2", ellipse(134, 108, 11, 5), extra='transform="rotate(-30 134 108)"')
        d.shape("hero2", ellipse(60, 94, 13, 9.5))
        d.shape("hero", ellipse(100, 93, 35, 25))
        d.stroke("mark", "M86 83 L100 77 L114 83 L114 99 L100 105 L86 99Z M86 83 L72 88 M114 83 L128 87 "
                         "M114 99 L127 101 M86 99 L73 100 M100 77 V69 M100 105 V117", 2.2)
        d.marks("mark", circle(54, 91, 1.9))
    group(d, "rotate(-10 100 93)", turtle)
    bubbles(d, [(40, 64, 2.5), (34, 52, 3.5)])


# ================================================================ HOT AIR BALLOON
def balloon_cappadocia(d: Drawing):
    d.disc("glow", 148, 60, 24)
    d.shape("light", cloud(20, 96, 1.3))
    d.shape("light", cloud(138, 108, 0.9))
    group(d, "translate(18 40) scale(.3)", lambda: balloon(d, body="pop", stripes="light", centre="hero2"))
    group(d, "translate(146 30) scale(.22)", lambda: balloon(d, body="hero2", stripes="light", centre="hero"))
    d.band("far", hills(146, 16))
    d.shape("ground", "M138 182 L145 148 Q150 138 155 148 L162 182Z M160 182 L165 158 Q169 150 173 158 L178 182Z")
    d.band("mid", hills(164, 12, 20))
    d.band("near", hills(180, 8, -10))
    balloon(d)


def balloon_himalaya(d: Drawing):
    d.disc("glow", 52, 50, 15)
    d.band("far", "M-30 132 L20 104 L44 120 L78 78 L104 108 L132 70 L162 104 L184 90 L230 116")
    for snow in ["M78 78 L88 91 L82 89 L77 94 L71 88 L67 91Z", "M132 70 L143 85 L137 83 L131 89 L125 82 L121 85Z",
                 "M20 104 L28 113 L22 112 L18 116 L13 110Z", "M184 90 L191 98 L186 97 L182 101 L178 96Z"]:
        d.shape("light", snow, shadow=False)
    d.band("mid", "M-30 152 L30 128 L62 146 L100 120 L140 148 L176 130 L230 148")
    d.band("near", hills(168, 10))
    d.band("deep", hills(186, 6, 30), line=False)
    # prayer flags strung across the valley
    pts = [(18 + 86 * t + 0, (1 - t) ** 2 * 150 + 2 * (1 - t) * t * 172 + t * t * 156) for t in [i / 10 for i in range(11)]]
    d.stroke("dark", "M18 150 Q60 172 104 156", 1.3)
    roles = ["pop", "hero2", "hero", "light", "far"]
    for i, (x, y) in enumerate(pts[1:-1]):
        d.shape(roles[i % len(roles)], f"M{x-3.5:.1f} {y:.1f} L{x+3.5:.1f} {y:.1f} L{x:.1f} {y+8:.1f}Z", shadow=False, spot=i % 2 == 0)
    group(d, "translate(14 26) scale(.3)", lambda: balloon(d, body="pop", stripes="light", centre="hero2"))
    group(d, "translate(150 76) scale(.2)", lambda: balloon(d, body="hero2", stripes="light", centre="pop"))
    group(d, "translate(66 -6) scale(.64)", lambda: balloon(d))


def balloon_flame(d: Drawing):
    d.shape("light", cloud(4, 168, 1.5))
    d.shape("light", cloud(146, 176, 1.2))
    env = "M14 -10 H186 V30 C186 58 150 84 128 96 H72 C50 84 14 58 14 30Z"
    d.shape("hero", env)
    d.shape("hero2", "M40 -10 C36 30 52 70 72 96 H84 C66 70 56 30 58 -10Z", shadow=False, spot=True)
    d.shape("hero2", "M160 -10 C164 30 148 70 128 96 H116 C134 70 144 30 142 -10Z", shadow=False, spot=True)
    d.shape("light", "M86 -10 C84 30 88 70 94 96 H106 C112 70 116 30 114 -10Z", shadow=False)
    d.shape("dark", rrect(68, 92, 64, 7, 3))
    d.stroke("dark", "M74 99 L82 128 M126 99 L118 128 M90 99 L94 108 M110 99 L106 108", 1.8)
    d.shape("pop", "M100 58 C116 76 120 90 114 102 C110 110 90 110 86 102 C80 90 84 76 100 58Z", spot=True)
    d.shape("glow2", "M100 74 C108 86 110 94 106 101 C103 105 97 105 94 101 C90 94 92 86 100 74Z", shadow=False)
    d.shape("dark", rrect(86, 106, 28, 9, 3))
    d.shape("ground", rrect(70, 124, 60, 8, 3))
    d.shape("ground", rrect(74, 130, 52, 40, 4))
    d.stroke("dark", "M74 140 H126 M74 150 H126 M74 160 H126 M87 131 V170 M100 131 V170 M113 131 V170", 1.2)


# ================================================================ SAFARI
def safari_giraffe(d: Drawing):
    d.disc("glow", 100, 118, 50)
    d.band("far", hills(160, 8))
    acacia(d)
    d.stroke("dark", "M44 144 Q36 152 38 162", 2.5)
    d.shape("hero", GIRAFFE)
    for x, y, rx, ry in GIRAFFE_SPOTS:
        d.marks("mark", ellipse(x, y, rx, ry))
    d.band("ground", hills(182, 6))
    d.band("deep", hills(192, 4, 40), line=False)


JEEP = "M38 140 L42 118 L60 113 L70 94 L134 94 L138 113 L162 115 L166 140Z"


def safari_jeep(d: Drawing):
    d.disc("glow", 136, 74, 34)
    d.band("far", hills(124, 10))
    acacia(d, -56, 24, 0.55)
    group(d, "translate(150 72) scale(.32)", lambda: d.shape("dark", GIRAFFE))
    d.band("ground", "M-30 152 Q100 144 230 152")
    d.shape("light", cloud(160, 140, 0.9), shadow=False)
    d.shape("light", cloud(176, 132, 0.6), shadow=False)
    d.stroke("dark", "M68 87 V95 M102 87 V95 M134 87 V95", 2.2)
    d.shape("hero2", rrect(62, 82, 78, 7, 2.5), spot=True)
    d.shape("hero", JEEP)
    d.shape("light", "M75 98 H98 V112 H67Z", shadow=False)
    d.shape("light", "M104 98 H130 V112 H104Z", shadow=False)
    d.marks("dark", circle(86, 105, 4.5))
    d.marks("dark", "M80 103 Q86 96 92 103Z")
    d.stroke("mark", "M101 98 V136 M106 120 H112", 1.6)
    d.shape("hero2", "M40 126 H164 V131 H40Z", shadow=False, spot=True)
    d.shape("dark", rrect(32, 134, 12, 6, 2))
    d.shape("glow2", circle(43, 123, 3.5), shadow=False)
    for x, y, r in [(68, 142, 15), (138, 142, 15), (168, 122, 10)]:
        d.shape("dark", circle(x, y, r))
        d.shape("light", circle(x, y, r * 0.38), shadow=False)
    d.band("deep", hills(178, 5), line=False)


ELEPHANT = ("M46 120 C46 96 66 84 92 84 C108 84 120 88 128 96 C134 86 150 84 160 92 C168 99 168 112 162 120 "
            "C160 132 161 148 166 160 C168 166 163 171 158 166 C151 154 149 140 148 130 L144 132 L144 172 "
            "L132 172 L131 148 L118 148 L117 172 L105 172 L104 148 L80 146 L79 172 L67 172 L66 146 L58 145 "
            "L57 172 L45 172 L46 140 C44 134 44 126 46 120Z")


def safari_elephant(d: Drawing):
    d.disc("glow", 112, 104, 50)
    d.band("far", hills(140, 10))
    acacia(d, -100, -16, 0.7)
    d.stroke("dark", "M150 58 q4 -4 8 0 q4 -4 8 0 M168 70 q3 -3 6 0 q3 -3 6 0", 1.8)
    d.stroke("dark", "M46 122 Q37 130 40 142", 2.5)
    d.shape("hero", ELEPHANT)
    d.shape("hero2", "M128 98 C120 104 118 122 126 132 C134 136 142 130 143 120 C144 108 138 98 128 98Z", shadow=False, spot=True)
    d.marks("mark", circle(152, 103, 2.2))
    d.stroke("light", "M148 128 C152 136 158 138 165 135", 3.2)
    d.band("ground", hills(172, 5))
    d.band("deep", hills(186, 4, 20), line=False)


GIRAFFE_GOLD = {"hero": "#F6C453", "mark": "#A0522D"}
ELEPHANT_GREY = {"hero": "#8D99AE", "hero2": "#B7C0CE", "mark": "#2B2D42"}
TURTLE_GREEN = {"hero": "#B5832E", "hero2": "#E3C77A", "mark": "#5A3A12"}  # hawksbill
FLAME = {"pop": "#FF7B3A", "glow2": "#FFD25E", "ground": "#C68B59"}
UNDERWATER = ["coastal", "dusk", "meadow"]

CONCEPTS = [
    Concept("scuba-diver", "scuba-diving", "Diver", scuba_diver, UNDERWATER, checks=[("dark", "mid"), ("dark", "near")]),
    Concept("scuba-shark", "scuba-diving", "Shark", scuba_shark, UNDERWATER, checks=[("dark", "mid"), ("dark", "near")]),
    Concept("scuba-turtle", "scuba-diving", "Turtle & reef", scuba_turtle, UNDERWATER, TURTLE_GREEN, checks=[("hero", "near"), ("hero2", "mid")]),
    Concept("balloon-cappadocia", "hot-air-balloon", "Valley sunrise", balloon_cappadocia, checks=[("hero", "sky"), ("hero", "glow"), ("hero", "mid")],
            fixes={"hero": ["pop", "deep", "dark", "near"]}),
    Concept("balloon-himalaya", "hot-air-balloon", "Over the Himalayas", balloon_himalaya, checks=[("hero", "sky"), ("hero", "far")]),
    Concept("balloon-flame", "hot-air-balloon", "Big flame", balloon_flame, overrides=FLAME, checks=[("hero", "sky"), ("pop", "hero")],
            fixes={"hero": ["deep", "near", "dark", "mid"]}),
    Concept("safari-giraffe", "safari", "Giraffe at sunset", safari_giraffe, overrides=GIRAFFE_GOLD, checks=[("hero", "glow"), ("hero", "sky")],
            fixes={"glow": ["#E07A5F", "#C8553D", "near"], "sky": ["sky2", "far"]}),
    Concept("safari-jeep", "safari", "Safari jeep", safari_jeep, checks=[("hero", "sky"), ("hero", "glow"), ("hero", "ground")],
            fixes={"glow": ["light", "far", "glow2"], "hero": ["pop", "deep", "near"]}),
    Concept("safari-elephant", "safari", "Elephant", safari_elephant, overrides=ELEPHANT_GREY, checks=[("hero", "glow"), ("hero", "sky"), ("hero", "ground")],
            fixes={"glow": ["glow2", "far", "near", "deep"]}),
]
