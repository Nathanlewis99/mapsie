"""Water activities (batch A): snorkelling, surfing, SUP, kayaking, rafting, sailing,
boat trips, island hopping, sunset cruises and jet skiing. Three concepts each."""
from _common import *  # noqa: F401,F403
from _common import Concept, Drawing, cloud, fish, circle, ellipse, waves, hills, rrect, group, bubbles, water

UNDERWATER = ["coastal", "dusk", "meadow"]
SKIN = {"skin": "#E2A47C"}


# ---------------------------------------------------------------- private helpers
def _sea(d: Drawing, y: float, deep: bool = True):
    """Open sea seen from above the surface: horizon at y, three rolling layers."""
    d.band("far", f"M-30 {y} H230")
    d.band("mid", waves(y + 16, 3, 24))
    if deep:
        d.band("near", waves(y + 40, 4, 30), line=False)


def _coral(d: Drawing, x: float, y: float, s: float = 1.0, role: str = "pop"):
    d.limb(role, f"M{x} {y} V{y-22*s} M{x} {y-12*s} L{x-9*s} {y-24*s} M{x} {y-15*s} L{x+10*s} {y-27*s}", 5.5 * s)


def _clip(d: Drawing, fn):
    """Clip to the sticker circle in both styles (line-style shapes are otherwise unclipped)."""
    d.raw('<g clip-path="url(#clip)">', '<g clip-path="url(#clip)">')
    fn()
    d.raw("</g>", "</g>")


def _person_in_boat(d: Drawing, x: float, y: float, vest: str = "pop", hat: str = "hero2", s: float = 1.0):
    """Seated paddler from the waist up, torso base at (x, y)."""
    d.shape(vest, rrect(x - 6.5 * s, y - 26 * s, 14 * s, 28 * s, 6 * s), spot=True)
    d.marks("skin", circle(x + 1.5 * s, y - 31 * s, 7.5 * s))
    d.shape(hat, f"M{x-6.5*s} {y-31*s} C{x-6.5*s} {y-42*s} {x+9.5*s} {y-42*s} {x+9.5*s} {y-31*s}Z", shadow=False)


def _surfboard(d: Drawing, cx: float, top: float, h: float, w: float, body: str, stripe: str):
    b = top + h
    d.shape(body, f"M{cx} {top} C{cx+w*.62} {top+h*.18} {cx+w*.56} {top+h*.72} {cx+w*.3} {b} H{cx-w*.3} "
                  f"C{cx-w*.56} {top+h*.72} {cx-w*.62} {top+h*.18} {cx} {top}Z")
    s = w * 0.18
    d.shape(stripe, f"M{cx} {top+3} C{cx+s} {top+h*.2} {cx+s} {top+h*.7} {cx+s*.8} {b} H{cx-s*.8} "
                    f"C{cx-s} {top+h*.7} {cx-s} {top+h*.2} {cx} {top+3}Z", shadow=False, spot=True)


# ================================================================ SNORKELLING
MASK = ("M60 78 H140 C150 78 153 88 151 100 C149 116 142 130 128 130 C118 130 112 124 108 118 L100 113 L92 118 "
        "C88 124 82 130 72 130 C58 130 51 116 49 100 C47 88 50 78 60 78Z")
LENS_L = "M62 86 H94 V108 L89 111 C85 117 80 122 72 122 C62 122 58 112 57 100 C57 92 57 86 62 86Z"
LENS_R = "M138 86 H106 V108 L111 111 C115 117 120 122 128 122 C138 122 142 112 143 100 C143 92 143 86 138 86Z"


def snorkel_mask(d: Drawing):
    water(d)
    _coral(d, 156, 176)
    for x, y, s in [(146, 150, 0.8), (160, 142, 0.7), (60, 152, 0.7)]:
        d.shape("hero2", fish(x, y, s), shadow=False)
    d.stroke("dark", ellipse(100, 92, 56, 20), 6)
    d.limb("hero2", "M54 118 C44 122 40 114 40 104 V54", 8, spot=True)
    d.shape("pop", rrect(34, 42, 12, 14, 4))
    d.shape("hero", MASK)
    d.shape("sky", LENS_L, shadow=False)
    d.shape("sky", LENS_R, shadow=False)
    d.stroke("light", "M64 104 L80 90 M70 110 L86 96 M112 104 L128 90", 3)
    bubbles(d, [(52, 34, 3), (60, 24, 2), (34, 30, 2.5)])


CLOWNFISH = ("M50 92 C54 72 82 64 106 68 C124 71 136 80 142 88 L160 72 C165 83 165 101 160 112 L142 96 "
             "C136 106 122 116 102 118 C78 120 54 112 50 92Z")


def snorkel_clownfish(d: Drawing):
    water(d, bottom=False)
    d.band("ground", "M-30 178 Q40 168 80 176 T160 172 T230 174")
    # anemone
    for k in range(9):
        x = 60 + k * 10
        tip = 132 + abs(k - 4) * 5
        bend = (k - 4) * 4
        d.limb("pop", f"M{100 + (k-4)*4} 178 Q{x - bend} {tip + 20} {x + bend} {tip}", 7, shadow=k % 2 == 0)
    d.shape("pop", ellipse(100, 176, 26, 8))
    # fish
    d.shape("hero", "M84 70 C88 54 110 52 120 72Z")
    d.shape("hero", "M96 114 C100 126 110 128 116 118Z")
    d.shape("hero", CLOWNFISH)
    for band in ["M66 74 C70 71 76 69 82 68 C77 84 77 102 84 117 C78 117 72 115 67 112 C61 100 61 86 66 74Z",
                 "M100 68 L112 68 C108 84 108 104 114 118 C110 118 104 118 100 118 C96 102 96 86 100 68Z",
                 "M138 84 L144 90 C140 94 140 100 143 96 L138 104 C134 98 134 90 138 84Z"]:
        d.shape("light", band, shadow=False, spot=True)
        d.stroke("mark", band, 1.6, line=False)
    d.stroke("mark", "M160 72 C165 83 165 101 160 112", 2.4)
    d.marks("light", circle(62, 86, 4.4))
    d.marks("mark", circle(61, 86, 2.4))
    bubbles(d, [(40, 66, 3), (34, 52, 4), (42, 40, 2.5)])


def snorkel_swimmer(d: Drawing):
    d.disc("glow", 150, 42, 16)
    d.shape("light", cloud(26, 52, 1.0))
    d.band("far", waves(76, 3, 22))
    d.band("mid", waves(116, 5, 30))
    d.band("near", waves(144, 5, 34), line=False)
    d.band("ground", "M-30 174 Q40 162 80 172 T160 168 T230 170")
    _coral(d, 156, 178, 1.0)
    _coral(d, 44, 176, 0.8, "hero2")
    for x, y, s in [(92, 146, 0.8), (106, 154, 0.7)]:
        d.shape("hero2", fish(x, y, s), shadow=False)
    # floating snorkeler, face down, head on the left
    d.limb("hero2", "M56 82 V50", 6, spot=True)
    d.shape("pop", rrect(52, 44, 8, 9, 3))
    d.limb("skin", "M104 92 L146 88", 8)
    d.limb("skin", "M104 98 L146 102", 8)
    d.shape("pop", ellipse(158, 86, 14, 5), extra='transform="rotate(-8 158 86)"', spot=True)
    d.shape("pop", ellipse(158, 104, 14, 5), extra='transform="rotate(8 158 104)"', spot=True)
    d.shape("hero", rrect(58, 82, 52, 20, 10))
    d.limb("skin", "M66 98 Q80 106 96 104", 7)
    d.shape("dark", circle(50, 90, 11))
    d.shape("hero2", rrect(38, 92, 12, 9, 3), shadow=False)
    d.shape("light", rrect(40, 94, 7, 5, 1.5), shadow=False)
    bubbles(d, [(36, 118, 2.5), (30, 108, 2)])


# ================================================================ SURFING
WAVE_EDGE = ("M-30 152 L120 152 C136 140 136 112 124 96 C112 82 90 80 76 90 C66 98 64 112 70 118 "
             "C52 110 50 80 66 64 C84 46 120 44 140 56 C160 68 170 100 180 118 C188 132 206 140 230 140")
TUBE = "M70 118 C64 112 66 98 76 90 C90 80 112 82 124 96 C136 112 136 140 120 152 L66 152 C62 140 64 128 70 118Z"


def surf_wave(d: Drawing):
    d.disc("glow", 164, 42, 18)
    d.shape("light", cloud(30, 44, 0.9))
    d.band("far", "M-30 138 H230")
    d.band("near", WAVE_EDGE)
    d.shape("mid", TUBE, shadow=False, line=False)
    d.stroke("light", "M140 56 C120 44 84 46 66 64 C50 80 52 110 70 118", 4.5)
    d.stroke("light", "M158 98 Q166 106 176 104 M168 124 Q178 130 190 128", 2.4)
    d.marks("light", circle(58, 128, 2.6) + circle(50, 120, 1.8) + circle(54, 138, 2))

    def surfer():
        d.shape("hero", ellipse(0, 0, 17, 3.4), spot=True)
        d.limb("dark", "M-6 -2 L-4 -12 L1 -21 M7 -2 L5 -12 L1 -21", 4.2, shadow=False)
        d.limb("dark", "M1 -21 L-2 -33", 6, shadow=False)
        d.limb("dark", "M-1 -30 L-12 -24 M-1 -30 L10 -33", 3.2, shadow=False)
        d.marks("dark", circle(-3, -39, 4.2))
    group(d, "translate(102 140) rotate(8)", surfer)
    d.band("mid", waves(164, 4, 30))
    d.band("deep", waves(184, 3, 34), line=False)


def surf_boards(d: Drawing):
    d.disc("glow", 150, 60, 22)
    d.band("far", "M-30 120 H230")
    d.band("mid", waves(134, 3, 22))
    # palm
    d.limb("dark", "M34 170 C36 130 42 100 54 76", 6)
    for fr in ["M54 76 C40 62 22 64 12 76 C26 70 40 72 54 76Z", "M54 76 C46 58 52 44 64 38 C60 52 58 64 54 76Z",
               "M54 76 C68 64 84 66 92 78 C80 72 66 72 54 76Z", "M54 76 C40 78 30 90 28 104 C36 92 44 84 54 76Z"]:
        d.shape("near", fr)
    group(d, "rotate(-12 72 164)", lambda: _surfboard(d, 72, 56, 116, 30, "pop", "light"))
    group(d, "rotate(10 132 164)", lambda: _surfboard(d, 132, 62, 110, 30, "hero2", "pop"))
    _surfboard(d, 102, 40, 130, 32, "hero", "light")
    d.band("ground", "M-30 160 Q60 150 120 158 T230 156")
    d.stroke("dark", "M30 176 q6 -4 12 0 M150 174 q6 -4 12 0", 1.6, line=False)


VAN = "M36 146 V104 C36 86 46 76 66 76 H156 C166 76 170 82 170 92 V146Z"


def surf_van(d: Drawing):
    d.disc("glow", 140, 46, 18)
    d.band("far", "M-30 60 H230")
    d.band("mid", waves(90, 3, 22))
    d.band("near", waves(116, 3, 26), line=False)
    d.band("ground", "M-30 146 Q100 138 230 146")
    # board on the roof rack
    d.stroke("dark", "M60 70 V77 M146 70 V77", 2.4)
    d.shape("hero2", "M40 66 C60 58 150 58 176 64 C150 72 60 74 40 66Z", spot=True)
    d.stroke("pop", "M48 66 H168", 1.6, line=False)
    d.shape("light", VAN)
    d.shape("hero", "M36 112 H170 V146 H36Z", shadow=False)
    d.shape("hero", "M36 104 C36 86 46 76 66 76 H70 C58 84 52 96 52 112 H36Z", shadow=False, spot=True)
    for x in (58, 86, 114, 142):
        d.shape("sky2", rrect(x, 84, 22, 18, 4), shadow=False)
    d.stroke("mark", "M106 112 V144 M110 124 H116", 1.6)
    d.shape("dark", rrect(30, 140, 16, 6, 2))
    d.shape("dark", rrect(160, 140, 14, 6, 2))
    for x in (66, 140):
        d.shape("dark", circle(x, 148, 14))
        d.shape("light", circle(x, 148, 5.5), shadow=False)
    d.band("deep", hills(180, 4), line=False)


# ================================================================ STAND-UP PADDLEBOARDING
def sup_paddler(d: Drawing):
    d.disc("glow", 52, 96, 30)
    d.band("far", "M-30 128 L10 110 L40 120 L80 92 L112 118 L150 98 L190 116 L230 106 V128Z")
    d.band("mid", "M-30 128 H230")
    d.stroke("light", "M40 150 H70 M126 156 H160 M86 166 H110", 2.4)
    d.shape("hero", "M30 140 C40 134 160 134 176 138 C164 146 44 148 30 140Z", spot=True)
    # paddler
    d.limb("dark", "M98 106 L94 138 M102 106 L110 138", 8)
    d.shape("pop", rrect(92.5, 70, 15, 38, 7), spot=True)
    d.limb("dark", "M120 62 L140 146", 3.6)
    d.shape("dark", "M134 134 C142 130 150 140 150 156 C144 162 138 156 134 134Z")
    d.limb("skin", "M100 78 L112 82 L124 76 M100 80 L116 98 L128 98", 5)
    d.marks("skin", circle(100, 61, 9))
    d.marks("dark", "M91 60 C91 50 109 50 109 60 C104 56 96 56 91 60Z")
    d.band("near", waves(170, 4, 30), line=False)


def sup_dog(d: Drawing):
    d.disc("glow", 50, 60, 22)
    d.shape("light", cloud(120, 46, 1.1))
    d.band("far", hills(118, 12))
    d.band("mid", "M-30 130 H230")
    d.stroke("light", "M30 160 H58 M140 164 H170", 2.4)
    d.shape("hero", "M24 146 C34 138 164 138 178 142 C166 152 40 154 24 146Z")
    d.shape("hero2", rrect(60, 140, 40, 4, 2), shadow=False)
    # paddle resting on the board
    d.limb("dark", "M48 136 L110 140", 3.4)
    d.shape("dark", "M30 130 C38 128 48 132 50 136 C46 140 38 142 30 140Z")
    # dog, sitting, facing right
    d.stroke("dog", "M112 132 C100 128 98 118 102 112", 4.4)
    d.shape("dog", "M110 142 C104 124 112 106 130 102 C144 100 150 110 150 122 L148 142Z")
    d.limb("dog", "M144 118 L144 142", 8)
    d.shape("pop", "M120 106 C130 100 146 102 150 112 L150 128 C140 132 126 130 116 124 C114 118 116 110 120 106Z", spot=True)
    d.shape("dog", "M136 92 C134 78 146 72 156 76 C162 78 164 82 168 84 C176 86 178 94 172 96 L156 98 C146 100 138 98 136 92Z")
    d.shape("ear", "M140 78 C134 78 130 86 132 96 C136 98 142 92 144 84Z", shadow=False)
    d.marks("mark", circle(176, 89, 2.8))
    d.marks("mark", circle(155, 84, 2))
    d.band("near", waves(174, 4, 30), line=False)


def sup_aerial(d: Drawing):
    d.band("far", "M-30 -30 H230")
    d.stroke("sky2", "M30 60 q10 -6 20 0 M140 150 q10 -6 20 0 M150 40 q8 -5 16 0 M40 150 q8 -5 16 0", 2.4)
    for x, y, s in [(146, 76, 0.9), (158, 86, 0.7), (50, 120, 0.8)]:
        d.shape("mid", fish(x, y, s), shadow=False, line=False)

    def board():
        d.shape("hero", "M22 100 C22 84 60 80 100 80 C148 80 176 90 182 100 C176 110 148 120 100 120 C60 120 22 116 22 100Z")
        d.shape("hero2", rrect(58, 88, 46, 24, 8), shadow=False, spot=True)
        d.stroke("dark", "M64 94 H98 M64 100 H98 M64 106 H98", 1.4, line=False)
        d.stroke("light", "M110 100 H172", 2)
        d.stroke("dark", "M24 100 C14 100 10 92 16 88 C22 84 26 92 18 96", 1.8)
    group(d, "rotate(-34 100 100)", board)
    d.limb("dark", "M56 42 L132 156", 4.4)
    d.shape("dark", "M126 146 C134 140 146 146 150 162 C150 172 142 176 136 168 C130 160 126 152 126 146Z", spot=True)
    d.limb("dark", "M48 46 L64 36", 4.4)


# ================================================================ KAYAKING
KAYAK = "M20 132 C46 142 150 142 182 128 C152 124 52 122 20 132Z"


def kayak_paddler(d: Drawing):
    d.disc("glow", 150, 62, 22)
    d.band("far", hills(108, 12))
    for x, h in [(22, 30), (36, 40), (172, 36), (186, 26)]:
        d.shape("near", f"M{x} {110-h} L{x+9} {112} H{x-9}Z", line=False)
    d.band("mid", "M-30 120 H230")
    d.stroke("light", "M36 152 H64 M140 156 H170", 2.4)
    d.shape("hero", KAYAK, spot=True)
    d.stroke("dark", "M30 132 C70 128 140 128 172 129", 1.6)
    d.shape("dark", ellipse(98, 128, 16, 3.4), shadow=False)
    _person_in_boat(d, 98, 128)
    d.limb("dark", "M52 80 L150 144", 3.6)
    d.shape("hero2", "M52 80 C40 70 34 76 38 84 C44 92 50 86 52 80Z", spot=True)
    d.shape("hero2", "M150 144 C162 154 168 148 164 140 C158 132 152 138 150 144Z", spot=True)
    d.limb("skin", "M96 112 L84 101 M100 110 L114 117", 4.6)
    d.band("near", waves(170, 4, 30), line=False)


def kayak_fjord(d: Drawing):
    d.disc("glow", 104, 70, 16)
    d.band("far", "M-30 112 L40 96 L74 72 L96 90 L122 66 L160 96 L230 104")
    for snow in ["M74 72 L84 82 L78 81 L74 85 L69 80 L64 80Z", "M122 66 L133 78 L127 77 L122 82 L117 76 L112 76Z"]:
        d.shape("light", snow, shadow=False)
    d.band("near", "M-30 34 L14 40 L40 92 L56 122 L74 130 L130 130 L146 120 L168 84 L190 44 L230 36")
    d.stroke("light", "M52 100 C56 110 54 120 60 128", 2.4)
    d.band("mid", "M-30 132 H230")
    d.stroke("light", "M40 152 H64 M136 160 H160 M80 176 H104", 2.2)
    group(d, "translate(100 150) scale(.62) translate(-100 -132)", lambda: (
        d.shape("hero", KAYAK, spot=True), _person_in_boat(d, 98, 128),
        d.limb("dark", "M62 86 L136 140", 4), d.shape("hero2", ellipse(60, 84, 9, 4.5), shadow=False),
        d.shape("hero2", ellipse(138, 142, 9, 4.5), shadow=False)))
    d.band("deep", waves(186, 3, 34), line=False)


ORCA = ("M24 152 C40 120 70 100 104 98 L96 46 C112 58 124 82 128 100 C150 106 170 124 182 150Z")


def kayak_orca(d: Drawing):
    d.disc("glow", 52, 52, 18)
    d.band("far", "M-30 96 H230")
    group(d, "translate(146 92) scale(.32) translate(-100 -132)", lambda: (
        d.shape("hero", KAYAK), _person_in_boat(d, 98, 128),
        d.limb("dark", "M62 84 L134 142", 5)))
    d.band("mid", waves(110, 3, 26))
    d.shape("orca", ORCA)
    d.shape("saddle", "M108 104 C118 100 130 102 138 108 C128 112 116 112 108 104Z", shadow=False, line=False)
    d.shape("light", "M44 132 C52 122 66 120 74 126 C66 132 54 134 44 132Z", shadow=False, spot=True)
    d.band("near", waves(150, 5, 30))
    d.stroke("light", "M20 150 q8 -8 16 -2 M168 150 q8 -8 16 -2", 2.6)
    d.band("deep", waves(176, 4, 34), line=False)


# ================================================================ WHITE-WATER RAFTING
RAFT = "M28 128 C26 114 38 108 52 114 H150 C164 108 176 114 172 128 C170 142 158 148 142 148 H58 C42 148 30 142 28 128Z"


def raft_crew(d: Drawing):
    d.band("far", "M-30 98 L0 80 L18 92 L40 70 L62 90 L90 74 L120 92 L150 66 L176 88 L200 74 L230 90")
    d.band("mid", waves(118, 4, 26))

    def raft():
        for x, hat in [(66, "hero2"), (100, "light"), (134, "hero2")]:
            _person_in_boat(d, x, 120, "pop", hat)
            d.limb("dark", f"M{x-12} {94} L{x+14} {158}", 3.4)
            d.limb("skin", f"M{x+2} {104} L{x-4} {104} M{x+2} {104} L{x+6} {124}", 4.2)
        d.shape("hero", RAFT, spot=True)
        d.stroke("dark", "M44 122 Q60 128 76 122 Q92 128 108 122 Q124 128 140 122 Q152 128 160 122", 1.6)
    group(d, "rotate(-7 100 128)", raft)
    d.band("near", waves(150, 5, 22))
    for x, y, s in [(26, 140, 1.0), (172, 116, 0.8), (150, 152, 0.9), (60, 154, 0.8)]:
        d.shape("light", cloud(x, y, s), shadow=False)
    d.band("deep", waves(178, 4, 30), line=False)


def raft_canyon(d: Drawing):
    d.disc("glow", 150, 46, 16)
    d.band("far", "M-30 84 H20 L24 72 H64 L68 84 H120 L126 66 H170 L176 84 H230")
    d.band("mid", "M-30 60 L22 64 L44 104 L58 116 L142 116 L156 100 L178 62 L230 58")
    d.band("near", "M-30 110 L30 118 L64 156 L136 156 L170 120 L230 112")
    river = "M86 116 H114 C116 128 128 136 140 150 C150 162 156 176 160 200 H40 C44 176 52 160 62 150 C72 138 84 128 86 116Z"
    _clip(d, lambda: d.shape("far", river))
    d.stroke("light", "M90 126 H110 M76 142 Q86 138 96 142 Q106 138 116 142 Q124 138 130 142 M58 172 Q70 166 82 172 Q94 166 106 172 Q118 166 130 172 Q140 166 148 172", 2.4)
    group(d, "translate(98 156) rotate(-4) scale(.36) translate(-100 -128)", lambda: (
        d.shape("hero", RAFT, spot=True),
        _person_in_boat(d, 66, 118), _person_in_boat(d, 100, 118, hat="light"), _person_in_boat(d, 134, 118)))


def raft_helmet(d: Drawing):
    d.band("mid", waves(128, 5, 26))
    d.band("near", waves(150, 5, 30))
    for a, b in [("M44 44 L156 156", "M156 44 L44 156")]:
        d.limb("dark", a, 5)
        d.limb("dark", b, 5)
    for x, y, r in [(48, 48, -45), (152, 48, 45)]:
        d.shape("hero2", ellipse(x, y, 7, 6), shadow=False)
        d.shape("dark", rrect(x - 9, y - 4, 18, 8, 3), extra=f'transform="rotate({r} {x} {y})"')
    for x, y, r in [(150, 150, -45), (50, 150, 45)]:
        d.shape("hero2", ellipse(x, y, 11, 19), extra=f'transform="rotate({r} {x} {y})"', spot=True)
    d.shape("hero", "M52 120 C50 86 74 62 102 62 C130 62 152 82 152 110 L160 114 C164 120 160 126 152 126 H60 C54 126 52 124 52 120Z")
    d.stroke("light", "M66 106 C66 90 80 78 98 76", 3.4)
    d.marks("mark", rrect(96, 66, 6, 14, 3) + rrect(114, 70, 6, 14, 3) + rrect(78, 70, 6, 14, 3))
    d.stroke("dark", "M66 126 C70 146 92 152 104 140", 3)
    d.shape("dark", rrect(52, 120, 108, 8, 3), shadow=False)
    for x, y, s in [(14, 148, 1.0), (152, 160, 1.0)]:
        d.shape("light", cloud(x, y, s), shadow=False)


# ================================================================ SAILING
def sail_yacht(d: Drawing):
    d.disc("glow", 100, 92, 56)
    d.band("far", "M-30 136 H230")
    d.stroke("dark", "M104 32 L104.5 136", 3)
    d.shape("light", "M101 36 C86 70 66 106 50 132 H101Z")
    d.shape("pop", "M101 104 C96 112 92 120 88 132 H101Z", shadow=False, spot=True)
    d.shape("light", "M108 44 C126 74 146 104 158 128 H108Z")
    d.shape("hero", "M38 138 H170 C166 150 156 156 146 156 H60 C50 156 42 150 38 138Z", spot=True)
    d.stroke("light", "M52 144 H156", 1.6, line=False)
    d.shape("pop", "M104 30 L116 34 L104 38Z", shadow=False)
    d.band("mid", waves(154, 4, 26))
    d.band("near", waves(176, 4, 32), line=False)
    d.stroke("dark", "M150 62 q4 -4 8 0 q4 -4 8 0", 1.8)


def sail_lighthouse(d: Drawing):
    d.disc("glow", 46, 70, 16)
    d.raw('<g opacity=".35" fill="#fff"><path d="M140 52 L30 30 L30 70Z"/></g>', "")
    d.band("far", "M-30 128 H230")
    _clip(d, lambda: (d.shape("near", "M110 200 L116 128 C122 116 136 110 150 110 H230 V200Z"),
                      d.shape("mid", "M120 200 L128 146 C134 136 146 132 160 134 L230 132 V200Z", line=False)))
    d.shape("light", "M130 112 L134 62 H146 L150 112Z")
    d.shape("pop", "M131.2 96 L132.3 82 H147.7 L148.8 96Z", shadow=False, spot=True)
    d.shape("pop", "M133.6 70 L134 64 H146 L146.4 70Z", shadow=False, spot=True)
    d.shape("dark", rrect(130, 58, 20, 5, 2))
    d.shape("glow2", rrect(134, 46, 12, 12, 2))
    d.stroke("dark", "M134 46 V58 M140 46 V58 M146 46 V58", 1.4)
    d.shape("pop", "M130 46 L140 36 L150 46Z")
    group(d, "translate(66 116) scale(.5) translate(-100 -140)", lambda: (
        d.stroke("dark", "M104 32 L104.5 136", 3),
        d.shape("light", "M101 36 C86 70 66 106 50 132 H101Z"),
        d.shape("light", "M108 44 C126 74 146 104 158 128 H108Z"),
        d.shape("hero", "M38 138 H170 C166 150 156 156 146 156 H60 C50 156 42 150 38 138Z", spot=True)))
    d.band("mid", waves(146, 4, 26))
    d.band("deep", waves(172, 4, 32), line=False)
    d.stroke("dark", "M28 98 q4 -4 8 0 q4 -4 8 0", 1.8)


def sail_wheel(d: Drawing):
    d.disc("glow", 150, 56, 18)
    d.band("far", "M-30 112 H230")
    d.band("mid", waves(130, 3, 24))
    d.band("ground", "M-30 160 H230")
    d.stroke("dark", "M-30 168 H230 M-30 180 H230", 1.4, line=False)
    cx, cy = 100, 100
    import math
    for k in range(8):
        a = math.pi * k / 4 + math.pi / 8
        x1, y1 = cx + 12 * math.cos(a), cy + 12 * math.sin(a)
        x2, y2 = cx + 66 * math.cos(a), cy + 66 * math.sin(a)
        d.limb("wood", f"M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}", 6)
        hx, hy = cx + 64 * math.cos(a), cy + 64 * math.sin(a)
        d.shape("wood", ellipse(hx, hy, 6, 6), shadow=False)
    d.stroke("wood", circle(cx, cy, 44), 10, shadow=True, line=False)
    d.limb("wood", f"M{cx-44} {cy} a44 44 0 1 0 88 0 a44 44 0 1 0 -88 0", 8)
    d.stroke("woodlight", circle(cx, cy, 44), 2, line=False)
    d.shape("hero2", circle(cx, cy, 15), spot=True)
    d.shape("wood", circle(cx, cy, 7), shadow=False)


# ================================================================ BOAT TRIP
def boat_ferry(d: Drawing):
    d.disc("glow", 150, 52, 18)
    d.shape("light", cloud(24, 56, 1.0))
    d.band("far", hills(86, 12, 10))
    d.band("mid", "M-30 122 H230")
    # tour boat, bow to the right
    d.stroke("dark", "M66 76 L66.5 92 M104 76 L104.5 92 M140 76 L140.5 92", 2.2)
    d.shape("pop", "M58 70 H148 L142 78 H64Z", spot=True)
    d.shape("light", "M52 90 H150 V112 H52Z")
    for x in (60, 80, 100, 120):
        d.shape("sky2", rrect(x, 96, 14, 10, 3), shadow=False)
    d.shape("hero2", rrect(136, 94, 12, 18, 3), shadow=False)
    d.stroke("dark", "M54 90 H150", 1.6)
    d.shape("hero", "M26 110 H176 C174 120 168 130 158 136 H48 C38 132 30 122 26 110Z", spot=True)
    d.stroke("light", "M36 118 H168", 2.2)
    d.stroke("dark", "M150 70 L150.5 44", 2)
    d.shape("pop", "M151 44 L166 49 L151 54Z", shadow=False)
    d.marks("light", circle(50, 124, 3) + circle(62, 124, 3) + circle(74, 124, 3))
    d.band("near", waves(140, 4, 26))
    d.band("deep", waves(170, 4, 32), line=False)


DOLPHIN = ("M30 100 C50 88 90 82 120 88 C132 90 140 94 146 98 C152 99 158 100 161 102 C157 105 148 105 142 104 "
           "C130 112 108 116 86 114 C64 112 46 108 34 104Z")


def _dolphin(d: Drawing):
    d.shape("dolphin", "M36 102 L14 88 C18 98 18 106 12 116Z")
    d.shape("dolphin", "M88 87 C90 76 98 68 110 66 C104 74 104 82 106 89Z")
    d.shape("dolphin", DOLPHIN, spot=True)
    d.shape("belly", "M60 110 C80 114 110 114 128 108 C134 106 140 104 146 104 C130 112 108 116 86 114 C76 113 68 112 60 110Z", shadow=False)
    d.shape("dolphin2", "M102 108 C100 118 94 124 86 126 C90 118 92 114 94 110Z", shadow=False)
    d.marks("mark", circle(136, 96, 2.2))


def boat_dolphins(d: Drawing):
    d.disc("glow", 52, 54, 18)
    d.band("far", "M-30 112 H230")
    group(d, "translate(150 132) rotate(30) scale(.62) translate(-90 -100)", lambda: _dolphin(d))
    d.band("mid", waves(126, 4, 26))
    group(d, "translate(88 92) rotate(-32) scale(.95) translate(-90 -100)", lambda: _dolphin(d))
    d.marks("light", circle(46, 140, 3) + circle(38, 132, 2.2) + circle(56, 128, 2))
    d.stroke("light", "M30 146 Q40 136 52 144 M136 140 Q146 132 158 140", 2.6)
    d.band("near", waves(150, 5, 30))
    d.band("deep", waves(176, 4, 34), line=False)


def _ring_seg(cx, cy, r1, r2, a0, a1):
    import math
    p = lambda r, a: (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = p(r2, a0), p(r2, a1), p(r1, a1), p(r1, a0)
    return (f"M{x0:.1f} {y0:.1f} A{r2} {r2} 0 0 1 {x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f} "
            f"A{r1} {r1} 0 0 0 {x3:.1f} {y3:.1f}Z")


def boat_lifering(d: Drawing):
    d.disc("glow", 46, 92, 16)
    d.band("far", "M-30 120 H230")
    d.band("mid", waves(136, 3, 22))
    d.band("near", waves(160, 4, 28), line=False)
    # deck rail
    _clip(d, lambda: d.limb("wood", "M-10 52 C60 50 140 50 210 52", 8))
    _clip(d, lambda: d.limb("wood", "M30 52 L32 200 M170 52 L168 200", 7))
    d.stroke("dark", "M88 54 L82 66 M112 54 L118 66", 2.4)
    cx, cy = 100, 112
    ring = circle(cx, cy, 46) + " " + circle(cx, cy, 22)
    d.shape("light", ring, extra='fill-rule="evenodd"')
    for a in (-90, 0, 90, 180):
        d.shape("pop", _ring_seg(cx, cy, 22, 46, a - 20, a + 20), shadow=False, spot=True)
    d.stroke("dark", circle(cx, cy, 34), 1.6, line=False)
    for a in (-135, -45, 45, 135):
        import math
        x, y = cx + 34 * math.cos(math.radians(a)), cy + 34 * math.sin(math.radians(a))
        d.limb("rope", f"M{x - 4*math.sin(math.radians(a)):.1f} {y + 4*math.cos(math.radians(a)):.1f} "
                       f"L{x + 4*math.sin(math.radians(a)):.1f} {y - 4*math.cos(math.radians(a)):.1f}", 4, shadow=False)
    d.limb("rope", "M82 66 C78 70 74 72 70 78", 3, shadow=False)
    d.limb("rope", "M118 66 C122 70 126 72 130 78", 3, shadow=False)


# ================================================================ ISLAND HOPPING
def _palm(d: Drawing, x: float, y: float, s: float = 1.0, lean: float = 1.0, role: str = "near"):
    tx, ty = x + 14 * s * lean, y - 52 * s
    d.limb("trunk", f"M{x} {y} Q{x + 2*s*lean} {y - 30*s} {tx} {ty}", 4.5 * s)
    for dx, dy, cx1, cy1 in [(-24, 2, -14, -8), (22, 4, 12, -8), (-12, -16, -10, -12), (12, -16, 6, -14), (0, 14, -2, 4)]:
        d.shape(role, f"M{tx} {ty} Q{tx + cx1*s} {ty + cy1*s} {tx + dx*s} {ty + dy*s} Q{tx + dx*s*.5} {ty + (dy*.5 - 2)*s} {tx} {ty}Z",
                shadow=False)
    d.marks("dark", circle(tx, ty + 2 * s, 2.4 * s))


def island_palms(d: Drawing):
    d.disc("glow", 140, 54, 22)
    d.shape("light", cloud(28, 54, 0.9))
    d.band("far", "M-30 116 H230")
    d.shape("far", "M150 118 Q170 98 196 112 L200 118Z", line=False)
    d.shape("ground", "M34 132 C50 112 80 104 104 106 C128 108 150 118 166 132Z")
    _palm(d, 80, 112, 1.2, -0.6)
    _palm(d, 108, 114, 1.0, 1.0)
    d.band("mid", waves(130, 3, 22))
    group(d, "translate(150 150) scale(.5)", lambda: (
        d.shape("hero", "M-40 -8 H40 C36 4 28 10 18 12 H-34 C-38 6 -40 0 -40 -8Z", spot=True),
        d.shape("light", "M-24 -8 L-16 -22 H10 L18 -8Z"),
        d.shape("dark", rrect(-12, -18, 20, 6, 2), shadow=False)))
    d.stroke("light", "M100 154 Q112 148 124 154 M40 160 H64", 2.2)
    d.band("near", waves(168, 4, 30), line=False)


def island_map(d: Drawing):
    d.band("far", "M-30 -30 H230")
    d.stroke("sky2", "M30 120 q8 -5 16 0 M140 60 q8 -5 16 0 M120 140 q8 -5 16 0 M60 56 q8 -5 16 0", 2.2, line=False)
    isles = [(56, 74, 26, 18), (140, 92, 22, 16), (84, 146, 28, 17)]
    for x, y, rx, ry in isles:
        d.shape("ground", f"M{x-rx} {y} C{x-rx} {y-ry} {x-rx*.3} {y-ry*1.1} {x+rx*.2} {y-ry} C{x+rx} {y-ry*.8} {x+rx*1.1} {y} "
                          f"{x+rx*.8} {y+ry*.6} C{x+rx*.4} {y+ry*1.1} {x-rx*.6} {y+ry} {x-rx} {y}Z")
        d.shape("jungle", ellipse(x + 2, y - 3, rx * .62, ry * .55), shadow=False, line=False)
        d.shape("jungle2", circle(x - rx * .2, y - ry * .3, ry * .22) + circle(x + rx * .3, y - ry * .15, ry * .2), shadow=False, line=False)
    import math
    pts = []
    for t in [i / 22 for i in range(23)]:
        # route: island 1 -> island 2 -> island 3
        if t <= .5:
            u = t * 2; p0, p1, p2 = (74, 84), (118, 60), (126, 82)
        else:
            u = (t - .5) * 2; p0, p1, p2 = (126, 104), (126, 140), (106, 140)
        pts.append(((1-u)**2*p0[0] + 2*(1-u)*u*p1[0] + u*u*p2[0], (1-u)**2*p0[1] + 2*(1-u)*u*p1[1] + u*u*p2[1]))
    d.marks("pop", " ".join(circle(x, y, 1.9) for x, y in pts[1:-1] if not (100 < x < 112 and 60 < y < 72)))
    d.shape("pop", "M84 144 C84 132 100 132 100 144 C100 152 92 158 92 164 C92 158 84 152 84 144Z", spot=True)
    d.marks("light", circle(92, 143, 3.2))
    group(d, "translate(108 66) rotate(16) scale(.62)", lambda: (
        d.shape("hero", "M-30 -8 H22 C30 -8 38 -2 40 0 C38 2 30 8 22 8 H-30Z", spot=True),
        d.shape("light", rrect(-14, -5, 18, 10, 3), shadow=False)))
    # compass
    d.shape("light", "M40 128 L44 140 L56 144 L44 148 L40 160 L36 148 L24 144 L36 140Z")
    d.marks("pop", "M40 128 L44 140 L36 140Z")


SEAPLANE = "M36 92 C36 84 46 80 60 80 H128 L166 68 L170 70 L162 92 C148 98 118 100 60 100 C46 100 36 98 36 92Z"


def island_seaplane(d: Drawing):
    d.disc("glow", 152, 40, 16)
    d.band("far", "M-30 136 H230")
    d.shape("ground", "M10 140 C24 126 50 122 70 128 C80 132 86 136 90 140Z")
    d.shape("near", "M18 134 C28 126 46 124 62 128 C54 132 32 134 18 134Z", shadow=False, line=False)
    d.shape("ground", "M120 140 C134 130 158 128 176 136 L180 140Z")
    _palm(d, 44, 130, 0.5, 1)
    _palm(d, 150, 132, 0.45, -1)
    d.band("mid", waves(146, 3, 24))
    d.band("near", waves(170, 4, 30), line=False)
    d.shape("light", cloud(150, 92, 1.0))

    def plane():
        d.shape("hero", "M146 74 L160 46 H170 L164 80Z", spot=True)
        d.stroke("dark", "M70 100 L66 116 M110 99 L114 116 M84 84 L80 100", 2.2)
        d.shape("dark", rrect(48, 114, 84, 7, 3.5))
        d.shape("hero", SEAPLANE)
        d.shape("light", "M46 84 C48 82 52 82 56 82 L60 92 H44Z", shadow=False)
        d.marks("dark", rrect(68, 86, 8, 6, 2) + rrect(82, 86, 8, 6, 2) + rrect(96, 86, 8, 6, 2))
        d.stroke("hero2", "M60 96 H150", 2.4, line=False)
        d.shape("hero2", rrect(64, 74, 70, 8, 4), spot=True)
        d.shape("dark", ellipse(32, 91, 3, 14))
        d.shape("dark", circle(36, 91, 4), shadow=False)
    group(d, "translate(100 92) rotate(-8) scale(.86) translate(-104 -92)", plane)


# ================================================================ SUNSET CRUISE
def cruise_sunset(d: Drawing):
    d.disc("glow", 100, 116, 56)
    d.disc("glow2", 100, 116, 38, shadow=False, line=False)
    d.stroke("dark", "M146 50 q4 -4 8 0 q4 -4 8 0 M160 62 q3 -3 6 0 q3 -3 6 0", 1.8)
    d.band("far", "M-30 120 H230")
    d.stroke("glow2", "M64 132 H136 M76 146 H124 M86 160 H114 M94 174 H106", 3, line=False)
    d.band("mid", waves(178, 3, 30), line=False)
    # motor yacht silhouette
    d.stroke("dark", "M112 82 L112.5 102", 2.2)
    d.shape("dark", "M88 110 L94 100 H124 L132 110Z")
    d.shape("dark", "M62 124 L72 110 H142 L152 124Z")
    d.shape("dark", "M40 124 H170 L160 140 H56 C50 136 44 130 40 124Z", spot=True)
    d.marks("glow2", rrect(80, 114, 10, 5, 1.5) + rrect(96, 114, 10, 5, 1.5) + rrect(112, 114, 10, 5, 1.5) + rrect(128, 114, 8, 5, 1.5))
    d.marks("glow2", rrect(98, 103, 8, 4, 1.5) + rrect(110, 103, 8, 4, 1.5))


def _coupe(d: Drawing):
    d.shape("light", "M38 70 H102 C102 98 88 112 70 112 C52 112 38 98 38 70Z")
    d.shape("pop", "M42 78 H98 C96 98 86 108 70 108 C54 108 44 98 42 78Z", shadow=False, spot=True)
    d.shape("light", rrect(67.5, 110, 5, 40, 2.5))
    d.shape("light", ellipse(70, 150, 18, 4.5))
    d.stroke("glow2", "M48 84 C50 94 56 100 62 102", 2.2, line=False)


def cruise_cocktails(d: Drawing):
    d.disc("glow", 100, 128, 50)
    d.band("far", "M-30 132 H230")
    d.band("mid", waves(150, 3, 24))
    d.band("near", waves(174, 3, 30), line=False)
    group(d, "rotate(10 64 168) translate(-6 14)", lambda: (
        _coupe(d), d.shape("hero2", circle(46, 72, 9)), d.shape("light", circle(46, 72, 5), shadow=False, line=False)))
    group(d, "rotate(-10 136 168) translate(66 14)", lambda: (
        _coupe(d), d.stroke("dark", "M84 72 L96 40", 2),
        d.shape("hero", "M80 44 C86 30 108 30 114 44 Z", spot=True)))
    d.stroke("light", "M100 62 L100.5 52 M90 64 L84 56 M110 64 L116 56", 2.4)


def cruise_pelican(d: Drawing):
    d.disc("glow", 104, 96, 52)
    d.band("far", "M-30 132 H230")
    group(d, "translate(160 124) scale(.3) translate(-100 -132)", lambda: (
        d.shape("dark", "M40 124 H170 L160 140 H56 C50 136 44 130 40 124Z"),
        d.shape("dark", "M62 124 L72 110 H142 L152 124Z")))
    _clip(d, lambda: d.shape("wood", rrect(96, 128, 22, 90, 4)))
    d.stroke("dark", "M96 146 L118 150 M96 152 L118 156", 2, line=False)
    d.limb("bill", "M110 120 L108 130 M118 120 L118.5 130", 3, shadow=False)
    d.shape("pelican", "M94 104 C100 92 120 92 136 102 L156 116 C146 120 134 120 126 122 C110 126 96 118 94 104Z")
    d.shape("wing", "M104 104 C116 96 134 100 156 116 C140 118 124 116 104 104Z", shadow=False, spot=True)
    d.limb("pelican", "M98 106 C86 98 84 82 92 72", 9)
    d.shape("pelican", circle(94, 68, 8.5))
    d.shape("bill", "M88 64 L48 86 L52 88 L92 72Z")
    d.shape("pouch", "M90 72 L52 88 C62 94 82 88 92 76Z", shadow=False)
    d.marks("mark", circle(95, 66, 1.8))
    d.band("mid", waves(150, 3, 24))
    d.band("near", waves(174, 3, 30), line=False)


# ================================================================ JET SKIING
JETSKI = "M28 124 C40 108 70 102 100 100 L136 98 C156 98 172 104 180 114 C176 124 160 130 140 130 H40 C32 130 28 128 28 124Z"
JETSKI_HULL = "M34 128 H150 C160 128 170 124 177 119 C172 132 158 138 140 138 H44 C38 138 34 134 34 128Z"


def _jetski(d: Drawing, rider: bool = True):
    d.shape("dark", JETSKI_HULL)
    d.shape("hero", JETSKI, spot=True)
    d.shape("hero2", "M120 100 L138 98 C156 98 172 104 180 114 L150 112Z", shadow=False)
    d.stroke("light", "M44 118 H120", 2.4, line=False)
    d.limb("dark", "M124 100 L116 84", 5)
    d.limb("dark", "M110 82 L122 84", 3.4, shadow=False)
    if rider:
        d.limb("dark", "M80 92 L104 96 L104 112", 8)
        d.shape("pop", rrect(-7, -26, 15, 30, 7), extra='transform="translate(84 92) rotate(24)"', spot=True)
        d.limb("skin", "M96 72 L110 80 L114 82", 4.6)
        d.marks("skin", circle(102, 60, 8))
        d.marks("dark", "M96 58 H110 V62 H96Z")
    d.shape("dark", rrect(56, 96, 38, 8, 4))


def jetski_ride(d: Drawing):
    d.disc("glow", 150, 48, 18)
    d.band("far", "M-30 112 H230")
    d.shape("light", "M44 124 C30 110 18 92 22 70 C30 92 40 102 54 112Z")
    d.shape("light", "M38 128 C22 122 6 110 0 92 C14 106 26 112 42 116Z")
    group(d, "rotate(-8 100 120)", lambda: _jetski(d))
    d.band("mid", waves(134, 4, 22))
    for x, y, s in [(30, 128, 0.9), (150, 134, 0.7)]:
        d.shape("light", cloud(x, y, s), shadow=False)
    d.band("near", waves(162, 4, 30), line=False)


def jetski_wake(d: Drawing):
    d.band("far", "M-30 -30 H230")
    d.stroke("sky2", "M40 60 q8 -5 16 0 M150 150 q8 -5 16 0 M140 40 q8 -5 16 0", 2.2, line=False)
    wake = "M46 158 C58 128 104 152 108 120 C110 108 108 102 110 96"
    d.limb("light", wake, 18)
    d.limb("mid", wake, 6, shadow=False)

    def ski():
        d.shape("hero", "M0 -28 C8 -20 10 -6 10 14 C10 22 6 26 0 26 C-6 26 -10 22 -10 14 C-10 -6 -8 -20 0 -28Z", spot=True)
        d.shape("dark", rrect(-5, -2, 10, 22, 5), shadow=False)
        d.shape("hero2", "M-7 -12 H7 L5 -18 H-5Z", shadow=False)
        d.limb("dark", "M-10 -8 L10 -8", 3, shadow=False)
        d.marks("pop", circle(0, 6, 5))
        d.marks("skin", circle(0, 4, 3.6))
    group(d, "translate(124 64) rotate(24) scale(1.35)", ski)


def jetski_jump(d: Drawing):
    d.disc("glow", 52, 50, 18)
    d.shape("light", cloud(128, 36, 1.0))
    d.band("far", "M-30 128 H230")
    d.band("mid", "M-30 150 C20 150 40 140 60 118 C70 108 80 116 84 130 C90 146 140 150 230 146")
    for x, y, s in [(20, 120, 0.9), (60, 104, 0.8), (78, 112, 0.7)]:
        d.shape("light", cloud(x, y, s), shadow=False)
    group(d, "translate(8 -18) rotate(-20 100 120)", lambda: _jetski(d))
    d.marks("light", circle(70, 96, 2.4) + circle(62, 88, 1.8) + circle(80, 90, 2))
    d.band("near", waves(168, 4, 30), line=False)


CONCEPTS = [
    Concept("snorkel-mask", "snorkelling", "Mask & snorkel", snorkel_mask, UNDERWATER,
            checks=[("hero", "mid"), ("hero", "near"), ("hero", "far"), ("hero2", "far")], fixes={"hero2": ["light", "glow2"]}),
    Concept("snorkel-clownfish", "snorkelling", "Clownfish", snorkel_clownfish, UNDERWATER,
            {"hero": "#F7853A", "mark": "#1E2230", "pop": "#B07CD8", "light": "#FFFFFF"},
            checks=[("hero", "mid"), ("hero", "far"), ("pop", "near"), ("pop", "deep")]),
    Concept("snorkel-swimmer", "snorkelling", "Snorkeller", snorkel_swimmer, UNDERWATER, SKIN,
            checks=[("hero", "far"), ("skin", "far"), ("pop", "far"), ("dark", "far")]),
    Concept("surf-wave", "surfing", "Big wave", surf_wave,
            checks=[("near", "far"), ("near", "sky"), ("mid", "near"), ("dark", "mid"), ("hero", "mid")], fixes={"far": ["sky2", "mid"]}),
    Concept("surf-boards", "surfing", "Boards in the sand", surf_boards,
            checks=[("hero", "sky"), ("hero2", "sky"), ("pop", "sky"), ("hero", "ground")], fixes={"hero2": ["glow2", "mid"], "ground": ["far", "light"]}),
    Concept("surf-van", "surfing", "Surf van", surf_van,
            checks=[("hero", "ground"), ("hero2", "far"), ("light", "far"), ("light", "mid")], fixes={"hero": ["pop", "near"], "hero2": ["glow2", "light"]}),
    Concept("sup-paddler", "stand-up-paddleboarding", "Paddler at sunset", sup_paddler, overrides=SKIN,
            checks=[("hero", "mid"), ("pop", "far"), ("pop", "sky"), ("dark", "mid"), ("dark", "far")], fixes={"pop": ["hero", "mark"]}),
    Concept("sup-dog", "stand-up-paddleboarding", "Paddle pup", sup_dog,
            overrides={"dog": "#C9925B", "ear": "#8A5A3B", "mark": "#2B2D42"},
            checks=[("hero", "mid"), ("dog", "far"), ("dog", "sky"), ("pop", "dog")], fixes={"pop": ["hero2", "hero", "mark"], "far": ["mid", "near"]}),
    Concept("sup-aerial", "stand-up-paddleboarding", "Board from above", sup_aerial,
            checks=[("hero", "far"), ("hero2", "hero"), ("dark", "far")]),
    Concept("kayak-paddler", "kayaking", "Kayaker", kayak_paddler, overrides=SKIN,
            checks=[("hero", "mid"), ("hero2", "sky"), ("pop", "far"), ("dark", "mid")], fixes={"hero2": ["pop", "mark"], "pop": ["hero2", "mark"]}),
    Concept("kayak-fjord", "kayaking", "Fjord", kayak_fjord, overrides=SKIN,
            checks=[("far", "sky"), ("near", "far"), ("mid", "near"), ("hero", "mid")], fixes={"far": ["sky2", "mid"], "mid": ["far", "deep"], "hero": ["pop", "dark"]}),
    Concept("kayak-orca", "kayaking", "Orca encounter", kayak_orca, overrides={**SKIN, "orca": "#1F2633", "saddle": "#8C97A8"},
            checks=[("orca", "mid"), ("orca", "far"), ("hero", "far")], fixes={"far": ["sky2", "far"]}),
    Concept("raft-crew", "white-water-rafting", "Raft crew", raft_crew, overrides=SKIN,
            checks=[("hero", "mid"), ("hero", "near"), ("pop", "far"), ("pop", "hero"), ("light", "near")], fixes={"hero": ["pop", "hero2"], "pop": ["hero2", "mark"]}),
    Concept("raft-canyon", "white-water-rafting", "Canyon rapids", raft_canyon, overrides=SKIN,
            checks=[("far", "near"), ("mid", "near"), ("hero", "far"), ("light", "far")], fixes={"far": ["sky2", "mid"]}),
    Concept("raft-helmet", "white-water-rafting", "Helmet & paddles", raft_helmet,
            checks=[("hero", "sky"), ("hero", "mid"), ("hero2", "mid"), ("hero2", "near")], fixes={"hero2": ["light", "pop"]}),
    Concept("sail-yacht", "sailing", "Under sail", sail_yacht,
            checks=[("light", "glow"), ("hero", "mid"), ("hero", "far")], fixes={"glow": ["glow2", "far", "mid", "near"]}),
    Concept("sail-lighthouse", "sailing", "Lighthouse", sail_lighthouse,
            checks=[("light", "sky"), ("light", "far"), ("near", "far"), ("light", "near")], fixes={"sky": ["sky2", "far"]}),
    Concept("sail-wheel", "sailing", "Ship's wheel", sail_wheel, overrides={"wood": "#9A5B34", "woodlight": "#C98A55"},
            checks=[("wood", "sky"), ("wood", "far"), ("wood", "mid"), ("wood", "ground")], fixes={"ground": ["light", "far", "sky2"]}),
    Concept("boat-ferry", "boat-trip", "Tour boat", boat_ferry,
            checks=[("hero", "mid"), ("hero", "near"), ("light", "far"), ("pop", "far"), ("pop", "sky")], fixes={"far": ["mid", "near"], "hero": ["pop", "dark"], "pop": ["hero", "dark"]}),
    Concept("boat-dolphins", "boat-trip", "Dolphins", boat_dolphins, overrides={"dolphin": "#6F8FAF", "dolphin2": "#58779A", "belly": "#D9E4EE", "mark": "#1E2A3A"},
            checks=[("dolphin", "sky"), ("dolphin", "far"), ("dolphin", "mid"), ("dolphin", "glow")], fixes={"far": ["sky2", "light"], "mid": ["near", "far"]}),
    Concept("boat-lifering", "boat-trip", "Life ring", boat_lifering, overrides={"wood": "#9A5B34", "rope": "#E8D3A8"},
            checks=[("light", "far"), ("light", "sky"), ("pop", "far"), ("wood", "sky")], fixes={"sky": ["sky2", "far"], "light": ["#FFF4DE"], "pop": ["hero", "near"]}),
    Concept("island-palms", "island-hopping", "Palm island", island_palms, overrides={"trunk": "#8A5A3B"},
            checks=[("ground", "far"), ("near", "sky"), ("near", "ground"), ("hero", "mid")], fixes={"ground": ["hero2", "light"], "near": ["deep", "mid"], "hero": ["pop", "dark"]}),
    Concept("island-map", "island-hopping", "Island route", island_map, overrides={"jungle": "#6FAE6A", "jungle2": "#4E8C55"},
            checks=[("ground", "far"), ("pop", "far"), ("pop", "ground"), ("hero", "far")], fixes={"ground": ["hero2", "light"], "pop": ["hero", "mark", "dark"], "hero": ["pop", "dark"]}),
    Concept("island-seaplane", "island-hopping", "Seaplane", island_seaplane, overrides={"trunk": "#8A5A3B"},
            checks=[("hero", "sky"), ("hero", "light"), ("ground", "far"), ("hero2", "hero")], fixes={"ground": ["hero2", "light"], "hero": ["pop", "near", "dark"], "hero2": ["light", "glow2"]}),
    Concept("cruise-sunset", "sunset-cruise", "Sunset yacht", cruise_sunset,
            checks=[("dark", "glow"), ("dark", "glow2"), ("glow", "sky"), ("far", "glow")], fixes={"glow": ["glow2", "pop", "hero2"], "far": ["mid", "near", "deep"]}),
    Concept("cruise-cocktails", "sunset-cruise", "Cocktails at sunset", cruise_cocktails,
            checks=[("light", "glow"), ("light", "sky"), ("pop", "light"), ("glow", "sky")], fixes={"sky": ["sky2", "far", "mid"], "glow": ["near", "mid"]}),
    Concept("cruise-pelican", "sunset-cruise", "Pelican", cruise_pelican,
            overrides={"pelican": "#F4F1EA", "wing": "#9AA3AE", "bill": "#F2A541", "pouch": "#D9822B", "wood": "#7A4E31", "mark": "#1E2230"},
            checks=[("pelican", "glow"), ("wood", "far"), ("wood", "glow")], fixes={"glow": ["#E07A5F", "near", "mid"]}),
    Concept("jetski-ride", "jet-skiing", "Jet ski", jetski_ride, overrides=SKIN,
            checks=[("hero", "far"), ("hero", "sky"), ("hero", "mid"), ("pop", "hero"), ("light", "far")], fixes={"hero": ["pop", "dark"], "pop": ["hero2", "mark"]}),
    Concept("jetski-wake", "jet-skiing", "Carving the wake", jetski_wake, overrides=SKIN,
            checks=[("hero", "far"), ("light", "far"), ("mid", "light")], fixes={"hero": ["pop", "dark"]}),
    Concept("jetski-jump", "jet-skiing", "Wave jump", jetski_jump, overrides=SKIN,
            checks=[("hero", "sky"), ("hero", "far"), ("pop", "hero"), ("mid", "far")], fixes={"hero": ["pop", "dark"], "pop": ["hero2", "mark"], "far": ["sky2", "near"]}),
]
