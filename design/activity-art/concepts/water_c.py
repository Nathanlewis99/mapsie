"""Water C: bodyboarding, sea kayaking, canoeing, yacht charter, catamaran cruise, river cruise,
waterskiing, wakeboarding, windsurfing and whale shark swims. Three concepts each."""
from _common import Concept, Drawing, cloud, fish, circle, ellipse, waves, hills, rrect, group, bubbles

UNDERWATER = ["coastal", "dusk", "meadow"]
SEA = ["coastal", "meadow", "blush", "dusk"]  # sea and lake scenes: no golden
SKIN = {"skin": "#E2A47C"}


# ================================================================ helpers
def clipline(fn):
    """Line style doesn't clip shapes to the circle; wrap concepts whose shapes bleed off the edge."""
    def draw(d: Drawing):
        d.raw("", '<g clip-path="url(#clip)">')
        fn(d)
        d.raw("", "</g>")
    return draw


def sea(d: Drawing, y: float, deep: bool = True):
    """Open water seen from above the surface: horizon at y, then rolling layers."""
    d.band("far", f"M-30 {y} H230")
    d.band("mid", waves(y + 18, 3, 26))
    if deep:
        d.band("near", waves(y + 44, 4, 32), line=False)


def spray(x, y, s=1.0, left=True):
    """A splash fan rising from (x, y)."""
    k = -1 if left else 1
    return (f"M{x} {y} C{x+k*4*s} {y-10*s} {x+k*14*s} {y-18*s} {x+k*24*s} {y-16*s} "
            f"C{x+k*18*s} {y-12*s} {x+k*14*s} {y-6*s} {x+k*16*s} {y}Z")


def pine(x, y, h):
    w = h * 0.34
    return (f"M{x} {y-h} L{x+w*.55} {y-h*.5} H{x+w*.3} L{x+w} {y} H{x-w} L{x-w*.3} {y-h*.5} H{x-w*.55}Z")


def person_in_boat(d: Drawing, x, y, vest="pop", hat="hero2", s=1.0):
    """Seated paddler from the waist up, torso base at (x, y)."""
    d.shape(vest, rrect(x - 6.5 * s, y - 26 * s, 14 * s, 28 * s, 6 * s), spot=True)
    d.marks("skin", circle(x + 1.5 * s, y - 31 * s, 7.5 * s))
    d.shape(hat, f"M{x-6.5*s} {y-31*s} C{x-6.5*s} {y-42*s} {x+9.5*s} {y-42*s} {x+9.5*s} {y-31*s}Z", shadow=False)


def gulls(d: Drawing, x, y, s=1.0):
    d.stroke("dark", f"M{x} {y} q{4*s} {-4*s} {8*s} 0 q{4*s} {-4*s} {8*s} 0", 1.8)


# ================================================================ BODYBOARDING
BODYBOARD = "M-30 -52 C-30 -64 30 -64 30 -52 L28 44 C28 54 22 60 14 60 Q0 50 -14 60 C-22 60 -28 54 -28 44Z"
BB_NOSE = "M-30 -52 C-30 -64 30 -64 30 -52 L29.6 -42 C18 -48 -18 -48 -29.6 -42Z"
BB_TAIL = "M-28 44 C-28 54 -22 60 -14 60 Q0 50 14 60 C22 60 28 54 28 44 L28.2 36 Q0 30 -28.2 36Z"
SWIMFIN = "M-9 -30 C-9 -38 9 -38 9 -30 L11 -8 L22 30 C12 36 -12 36 -22 30 L-11 -8Z"


def bodyboard(d: Drawing, body="hero", rail="hero2"):
    d.shape(body, BODYBOARD)
    d.shape(rail, BB_NOSE, shadow=False, spot=True)
    d.shape(rail, BB_TAIL, shadow=False, spot=True)
    d.stroke("light", "M-16 -32 V30 M16 -32 V30", 2.2, line=False)


def swimfin(d: Drawing, role="mark"):
    d.shape(role, SWIMFIN, spot=True)
    d.shape("sky2", ellipse(0, -22, 5, 8), shadow=False, line=False)
    d.stroke("sky2", "M-12 0 L-16 26 M0 0 V30 M12 0 L16 26", 1.6, line=False)


def bb_flatlay(d: Drawing):
    d.band("ground", "M-30 -30 H230")
    d.shape("mid", "M-30 -30 H230 V46 C190 58 160 40 120 50 C80 60 40 40 -30 52Z")
    d.stroke("light", "M-30 52 C40 40 80 60 120 50 C160 40 190 58 230 46", 4)
    d.marks("dark", circle(150, 74, 1.4) + circle(60, 170, 1.4) + circle(156, 160, 1.2))
    group(d, "translate(82 112) rotate(-12) scale(.88)", lambda: bodyboard(d))
    d.stroke("dark", "M76 66 c-8 2 -14 6 -12 12 c2 6 10 6 8 12 c-2 6 -10 6 -10 12 c0 6 8 8 6 14 c-2 6 -10 6 -10 12", 2)
    d.shape("dark", rrect(40, 126, 16, 8, 3), extra='transform="rotate(-20 48 130)"')
    group(d, "translate(140 118) rotate(8) scale(.92)", lambda: swimfin(d))
    group(d, "translate(162 104) rotate(22) scale(.92)", lambda: swimfin(d))
    d.shape("pop", "M118 168 l3 -7 l3 7 l7 1 l-5 5 l2 7 l-7 -4 l-7 4 l2 -7 l-5 -5z", shadow=False)


def bb_wave(d: Drawing):
    d.disc("glow", 50, 48, 16)
    d.band("far", "M-30 118 H230")
    d.band("near", "M-30 152 C30 150 66 138 96 110 C116 90 132 70 156 62 C180 56 200 66 204 84 "
                   "C190 100 210 130 230 138")
    d.stroke("light", "M126 80 C140 64 164 56 186 62 C196 66 202 74 204 84", 5)
    d.shape("light", "M176 60 C188 56 198 62 204 74 C196 70 190 72 186 78 C184 70 180 64 176 60Z", shadow=False)
    d.stroke("light", "M174 98 Q182 110 192 114 M168 126 Q178 134 190 134", 2.4)

    def rider():
        d.shape("light", spray(30, 2, 1.1, left=False), shadow=False)
        d.shape("hero", "M-32 -2 C-32 -8 -24 -9 -18 -9 H24 C30 -9 32 -6 32 -2 C32 2 30 4 24 4 H-26 C-30 4 -32 2 -32 -2Z", spot=True)
        d.limb("dark", "M12 -10 L30 -16 M12 -9 L32 -7", 6)
        d.shape("pop", ellipse(37, -18, 7, 3), extra='transform="rotate(-20 37 -18)"', spot=True)
        d.shape("pop", ellipse(39, -7, 7, 3), shadow=False, spot=True)
        d.limb("dark", "M-12 -13 L14 -11", 11)
        d.limb("skin", "M-14 -14 L-26 -8 M-12 -11 L-24 -4", 4.4)
        d.marks("skin", circle(-20, -20, 6.5))
        d.marks("dark", "M-26 -21 C-26 -28 -14 -29 -13 -21 C-17 -24 -22 -24 -26 -21Z")
    group(d, "translate(98 120) rotate(-26) scale(1.25)", rider)
    d.band("mid", waves(166, 4, 28))
    d.band("deep", waves(186, 3, 34), line=False)


def bb_tower(d: Drawing):
    d.disc("glow", 150, 46, 15)
    d.shape("light", cloud(20, 52, 0.8), shadow=False)
    d.band("far", "M-30 102 H230")
    d.band("mid", waves(116, 3, 24))
    d.stroke("light", "M-30 132 Q10 126 50 132 T130 132 T230 132", 3, line=False)
    d.band("ground", "M-30 140 Q100 130 230 140")
    # lifeguard tower
    d.limb("dark", "M50 166 L58 102 M96 166 L88 102 M54 132 H92", 4)
    d.stroke("dark", "M98 104 L112 160 M100 116 H106 M102 128 H108 M105 140 H111", 2.4)
    d.shape("dark", rrect(44, 98, 60, 6, 2))
    d.shape("light", rrect(50, 70, 48, 30, 3))
    d.shape("sky2", rrect(56, 76, 36, 12, 2), shadow=False)
    d.shape("pop", "M42 74 L74 54 L106 74Z", spot=True)
    d.stroke("dark", "M74 54 V30", 2)
    d.shape("pop", "M75 30 L92 30 L75 42Z", shadow=False)
    d.shape("hero2", "M92 30 L92 42 L75 42Z", shadow=False)
    # board and fins on the sand
    group(d, "translate(140 128) rotate(12) scale(.68)", lambda: bodyboard(d))
    group(d, "translate(170 168) rotate(70) scale(.5)", lambda: swimfin(d))
    d.band("deep", hills(188, 4, 20), line=False)


# ================================================================ SEA KAYAKING
SEAKAYAK = ("M14 126 C26 128 40 130 60 131 C100 133 140 131 172 124 L190 116 C184 128 172 138 150 140 "
            "C110 144 70 144 40 140 C28 138 18 132 14 126Z")


def seakayak(d: Drawing, paddler=True, body="hero"):
    d.shape(body, SEAKAYAK, spot=True)
    d.stroke("dark", "M24 130 C70 135 130 134 180 122", 1.4)
    d.shape("light", ellipse(52, 132, 8, 2.4), shadow=False, line=False)
    d.shape("light", ellipse(146, 130, 8, 2.4), shadow=False, line=False)
    d.shape("dark", ellipse(98, 131, 15, 3.4), shadow=False)
    if paddler:
        person_in_boat(d, 98, 131)
        d.limb("dark", "M52 92 L146 146", 3.6)
        d.shape("hero2", ellipse(48, 90, 11, 4.5), extra='transform="rotate(30 48 90)"', spot=True)
        d.shape("hero2", ellipse(150, 148, 11, 4.5), extra='transform="rotate(30 150 148)"', spot=True)
        d.limb("skin", "M96 116 L82 108 M100 114 L114 122", 4.6)


ARCH = ("M36 124 L42 74 C44 54 70 42 98 42 C130 42 154 56 158 78 L164 124 H134 L132 102 C128 88 114 80 100 80 "
        "C84 80 72 88 70 102 L68 124Z")


def sk_arch(d: Drawing):
    d.disc("glow", 150, 40, 13)
    d.band("far", "M-30 122 H230")
    d.shape("near", ARCH)
    d.stroke("deep", "M44 70 C70 58 128 58 156 72 M40 96 C50 92 60 92 70 96 M132 96 C142 92 152 92 162 96", 2, line=False)
    d.shape("near", "M170 124 L172 100 C174 90 184 90 186 100 L188 124Z")
    gulls(d, 106, 26)
    gulls(d, 120, 34, 0.7)
    d.band("mid", waves(128, 3, 24))
    d.stroke("light", "M74 140 H100 M140 138 H160", 2.2)
    group(d, "translate(98 152) scale(.62) translate(-100 -130)", lambda: seakayak(d))
    d.band("deep", waves(176, 4, 32), line=False)


def sk_seal(d: Drawing):
    d.disc("glow", 152, 44, 14)
    d.band("far", "M-30 96 Q20 82 60 92 Q90 98 110 96 H230")
    d.band("mid", "M-30 104 H230")
    d.stroke("light", "M30 122 H52 M150 160 H172", 2.2)
    # seal
    d.stroke("light", ellipse(150, 146, 34, 7), 2.4)
    d.shape("seal", "M124 150 C124 128 134 116 150 116 C166 116 176 128 176 150Z")
    d.shape("seal", ellipse(150, 108, 22, 20))
    d.shape("seal2", ellipse(143, 118, 8, 6), shadow=False)
    d.shape("seal2", ellipse(157, 118, 8, 6), shadow=False)
    d.marks("mark", "M146 112 H154 L150 117Z")
    d.marks("mark", circle(140, 102, 4.2) + circle(160, 102, 4.2))
    d.marks("light", circle(141.4, 100.6, 1.3) + circle(161.4, 100.6, 1.3))
    d.stroke("mark", "M136 118 L124 115 M136 121 L124 122 M164 118 L176 115 M164 121 L176 122", 1.1)
    # kayak bow coming in from the left
    d.shape("hero", "M-30 128 C20 132 70 134 108 128 L124 120 C120 136 104 148 80 152 C40 156 0 154 -30 152Z", spot=True)
    d.stroke("dark", "M-30 136 C30 140 80 138 116 124", 1.4)
    d.stroke("dark", "M24 128 L64 148 M24 148 L64 130", 2)
    d.shape("light", circle(86, 136, 6), shadow=False)
    d.marks("pop", "M86 131 L88 136 L84 136Z")
    d.band("near", waves(168, 4, 30), line=False)


def sk_deck(d: Drawing):
    d.disc("glow", 130, 66, 14)
    d.band("far", "M-30 104 H230")
    d.shape("near", "M24 106 Q44 82 66 96 Q78 86 98 106Z")
    d.shape("near", "M136 106 Q152 94 172 106Z", line=False)
    d.band("mid", waves(118, 3, 22))
    d.stroke("light", "M30 136 H52 M152 140 H176", 2.2)
    d.band("near", waves(150, 4, 30), line=False)
    d.shape("hero", "M30 230 C40 180 74 130 100 104 C126 130 160 180 170 230Z", spot=True)
    d.stroke("dark", "M100 108 V230", 1.6, line=False)
    d.shape("light", "M82 150 L116 146 L120 172 L84 176Z", shadow=False)
    d.stroke("far", "M88 160 Q98 154 110 160", 1.6, line=False)
    d.marks("pop", circle(104, 164, 2))
    d.stroke("dark", "M66 146 L134 186 M134 146 L66 186 M72 158 H128", 2.2)
    d.marks("dark", circle(66, 146, 2.6) + circle(134, 146, 2.6) + circle(66, 186, 2.6) + circle(134, 186, 2.6))
    d.shape("light", circle(100, 128, 8))
    d.marks("pop", "M100 121 L103 128 L97 128Z")
    d.marks("dark", "M100 135 L103 128 L97 128Z")
    d.limb("dark", "M20 176 L180 176", 4)
    d.shape("hero2", ellipse(30, 176, 16, 7), spot=True)
    d.shape("hero2", ellipse(170, 176, 16, 7), spot=True)
    d.shape("skin", ellipse(74, 176, 8, 9))
    d.shape("skin", ellipse(126, 176, 8, 9))


# ================================================================ CANOEING
CANOE = ("M24 118 C22 110 25 104 30 101 C34 110 46 116 62 118 H138 C154 116 166 110 170 101 C175 104 178 110 176 118 "
         "C170 134 150 142 100 142 C50 142 30 134 24 118Z")


def canoe(d: Drawing, body="hero", paddlers=2):
    d.shape(body, CANOE, spot=True)
    d.stroke("hero2", "M28 117 C44 122 62 121 100 121 C138 121 156 122 172 117", 2.4, line=False)
    d.stroke("dark", "M27 116 C44 121 62 120 100 120 C138 120 156 121 173 116", 1.4)
    for x, hat in ([(70, "hero2"), (128, "light")] if paddlers == 2 else [(100, "hero2")]):
        person_in_boat(d, x, 120, "pop", hat)
        d.limb("dark", f"M{x+16} 82 L{x+8} 140", 3.2)
        d.shape("dark", ellipse(x + 7, 146, 4, 10), extra=f'transform="rotate(10 {x+7} 146)"')
        d.limb("skin", f"M{x+2} 100 L{x+14} 90 M{x+2} 106 L{x+11} 112", 4.2)


def canoe_lake(d: Drawing):
    d.disc("glow", 68, 60, 16)
    d.band("far", "M-30 104 L20 76 L46 90 L86 56 L118 84 L146 70 L230 100")
    d.shape("light", "M86 56 L96 66 L90 65 L86 70 L81 64 L76 65Z", shadow=False)
    for x, h in [(10, 30), (24, 40), (38, 28), (150, 34), (164, 44), (178, 32), (192, 38)]:
        d.shape("deep", pine(x, 108, h), shadow=False, line=x in (24, 164))
    d.band("mid", "M-30 106 H230")
    d.stroke("light", "M40 124 H66 M136 128 H164 M84 166 H112", 2.2)
    group(d, "translate(100 148) scale(.78) translate(-100 -128)", lambda: canoe(d))
    d.band("near", waves(178, 3, 30), line=False)


def canoe_portage(d: Drawing):
    d.disc("glow", 150, 50, 14)
    d.band("far", hills(110, 14))
    for x, h in [(18, 48), (34, 62), (170, 58), (186, 44)]:
        d.shape("near", pine(x, 150, h), shadow=False)
    d.band("ground", "M-30 156 Q100 146 230 156")
    # walker under an upturned canoe, heading right
    d.limb("dark", "M98 126 L92 148 L86 166 M104 126 L114 146 L122 164", 7)
    d.shape("dark", "M80 162 H92 V170 H78Z")
    d.shape("dark", "M118 160 L130 162 L128 170 L116 168Z")
    d.shape("pop", rrect(91, 96, 20, 34, 8), spot=True)
    d.limb("skin", "M96 102 L84 92 L80 80 M106 102 L118 92 L122 80", 4.6)
    d.shape("hero", "M20 86 C22 78 30 72 40 70 C70 58 130 58 160 70 C170 72 178 78 180 86 "
                    "C172 82 160 80 150 82 H50 C40 80 28 82 20 86Z", spot=True)
    d.stroke("hero2", "M22 86 C30 82 40 81 50 82 H150 C160 81 170 82 178 86", 3.2, line=False)
    d.stroke("dark", "M22 87 C30 83 40 82 50 83 H150 C160 82 170 83 178 87", 1.4)
    d.shape("light", "M118 182 H140", line=False)
    d.band("deep", hills(186, 4, 20), line=False)


MOOSE = ("M150 96 C148 86 138 82 126 82 L108 76 C100 74 92 76 86 80 L76 84 C64 86 52 92 44 100 "
         "C38 104 34 110 38 116 C42 120 50 118 54 116 L66 108 C72 106 78 106 82 108 L84 124 L88 112 L96 118 "
         "L98 160 H105 L107 124 L136 124 L138 160 H145 L148 120 C152 114 152 104 150 96Z")
ANTLER_L = ("M74 84 C70 74 62 70 54 70 L48 62 L56 65 L54 55 L61 63 L62 52 L67 62 L70 52 L73 63 L76 56 "
            "C78 64 80 74 78 84Z")
ANTLER_R = ("M80 82 C82 72 92 64 104 62 L108 54 L102 57 L104 48 L97 55 L96 46 L91 54 L88 46 L86 56 "
            "C82 62 78 72 76 82Z")


def canoe_moose(d: Drawing):
    d.disc("glow", 104, 104, 46)
    d.band("far", "M-30 120 L20 102 L56 112 L92 92 L130 110 L170 96 L230 112")
    for x, h in [(8, 32), (22, 42), (182, 40), (194, 30)]:
        d.shape("deep", pine(x, 128, h), shadow=False, line=False)
    d.band("mid", "M-30 126 H230")
    group(d, "translate(158 132) scale(.3) translate(-100 -128)", lambda: canoe(d, paddlers=1))
    d.shape("moose", ANTLER_R)
    d.shape("moose2", "M110 120 L112 160 H118 L120 120Z")
    d.shape("moose2", "M128 120 L128 160 H134 L136 120Z")
    d.shape("moose", MOOSE)
    d.shape("moose", "M150 92 L156 100 L150 102Z", shadow=False)
    d.shape("moose", ANTLER_L)
    d.shape("moose2", "M80 84 L94 74 L88 86Z", shadow=False)
    d.marks("mark", circle(60, 96, 2.2))
    d.marks("mark", ellipse(40, 110, 2, 1.4))
    d.band("near", waves(150, 3, 26))
    d.stroke("light", "M60 164 H90 M110 170 H150", 2.2)
    d.band("deep", waves(180, 3, 32), line=False)


# ================================================================ YACHT CHARTER
def sloop(d: Drawing, sails=True):
    d.stroke("dark", "M100 32 L100.5 124", 3)
    d.stroke("dark", "M100 36 L42 124 M100 40 L160 120", 1.1, line=False)
    if sails:
        d.limb("hero2", "M101 50 L48 120", 5)
    d.limb("dark", "M100 112 L156 112", 3.6)
    d.shape("hero", "M102 104 H156 C160 104 160 114 156 114 H102Z", spot=True)
    d.shape("light", "M70 124 L78 114 H118 L124 124Z")
    d.marks("dark", rrect(84, 117, 7, 4, 1.5) + rrect(96, 117, 7, 4, 1.5) + rrect(108, 117, 7, 4, 1.5))
    d.shape("light", "M34 122 H170 C168 134 158 142 144 142 H58 C46 142 38 134 34 122Z")
    d.shape("hero", "M36 130 H168 C167 132 166 134 165 135 H38Z", shadow=False)
    d.stroke("dark", "M164 124 L166 148 M170 128 L172 150", 1.6)
    d.shape("pop", "M100 32 L112 35 L100 38Z", shadow=False)


def yacht_cove(d: Drawing):
    d.disc("glow", 44, 52, 14)
    d.band("far", "M-30 104 H230")
    d.shape("ground", "M120 128 C124 104 136 86 158 80 C178 76 200 82 230 88 V128Z")
    for x, y, w in [(140, 86, 12), (154, 80, 14), (170, 82, 12), (184, 86, 12), (148, 98, 12), (164, 94, 14), (180, 98, 12)]:
        d.shape("light", rrect(x, y, w, 10, 1.5), shadow=False)
    d.shape("hero", "M156 80 A6 6 0 0 1 168 80Z", shadow=False)
    d.band("mid", waves(140, 3, 24))
    d.stroke("dark", "M52 132 L46 166", 1.4)
    group(d, "translate(86 130) scale(.86) translate(-100 -128)", lambda: sloop(d))
    d.stroke("light", "M30 156 H52 M130 158 H156", 2.2)
    d.band("near", waves(170, 4, 30), line=False)


def yacht_anchor(d: Drawing):
    d.band("far", "M-30 112 H230")
    d.band("mid", waves(130, 3, 24))
    d.band("near", waves(156, 4, 30), line=False)
    d.stroke("light", "M30 140 H52 M150 146 H172", 2.2)
    d.limb("rope", "M100 -10 V40", 5)
    d.stroke("anchor", circle(100, 52, 11), 7, shadow=True, line=False)
    d.limb("anchor", "M89 52 a11 11 0 1 0 22 0 a11 11 0 1 0 -22 0", 5)
    d.limb("anchor", "M70 76 H130", 8)
    d.limb("anchor", "M100 62 V152", 10)
    d.limb("anchor", "M52 112 C54 140 76 154 100 156 C124 154 146 140 148 112", 9)
    d.shape("anchor", "M42 122 L50 102 L62 118Z")
    d.shape("anchor", "M158 122 L150 102 L138 118Z")
    d.limb("rope", "M100 40 C120 50 122 70 106 84 C88 98 82 116 100 126 C118 136 120 150 108 162", 4, spot=True)


def yacht_cap(d: Drawing):
    d.disc("glow", 152, 50, 14)
    gulls(d, 40, 54)
    d.band("far", "M-30 92 H230")
    d.band("mid", waves(106, 3, 24), line=False)
    d.band("ground", "M-30 130 H230")
    d.stroke("dark", "M-30 150 H230 M-30 172 H230 M60 130 V150 M140 150 V172 M30 172 V200 M170 172 V200", 1.4, line=False)
    d.shape("light", "M34 92 C34 72 70 62 100 62 C130 62 166 72 166 92 C166 102 152 108 136 110 H64 C48 108 34 102 34 92Z")
    d.shape("dark", "M56 102 H144 L144 128 H56Z")
    d.shape("hero2", rrect(54, 104, 92, 5, 2), shadow=False, spot=True)
    d.shape("dark", "M54 126 C60 144 140 144 146 126Z")
    d.shape("hero2", "M76 96 C70 90 70 82 76 76 M124 96 C130 90 130 82 124 76", line=False)
    d.stroke("hero2", "M78 98 C68 92 68 80 76 74 M122 98 C132 92 132 80 124 74", 3)
    d.shape("hero2", ellipse(100, 86, 13, 13), spot=True)
    d.stroke("dark", "M100 79 V94 M94 84 H106 M93 89 Q100 98 107 89", 1.8)
    d.marks("dark", circle(100, 79, 2))


# ================================================================ CATAMARAN CRUISE
def cat_aerial(d: Drawing):
    d.band("far", "M-30 -30 H230")
    d.stroke("sky2", "M30 60 q8 -5 16 0 M150 160 q8 -5 16 0 M146 36 q8 -5 16 0 M36 150 q8 -5 16 0", 2.2, line=False)

    def boat():
        d.limb("light", "M-24 58 L-30 120 M24 58 L30 120", 5, shadow=False)
        d.shape("net", rrect(-20, -50, 40, 38, 2), shadow=False)
        d.stroke("dark", "M-20 -40 H20 M-20 -30 H20 M-20 -21 H20 M-10 -50 V-12 M0 -50 V-12 M10 -50 V-12", 0.8, line=False)
        for x in (-24, 24):
            d.shape("light", f"M{x} -66 C{x+9} -50 {x+9} 30 {x+8} 56 H{x-8} C{x-9} 30 {x-9} -50 {x} -66Z")
        d.shape("light", rrect(-24, -14, 48, 56, 8))
        d.shape("sky2", rrect(-17, -8, 34, 14, 5), shadow=False)
        d.shape("hero2", rrect(-17, 22, 34, 14, 3), shadow=False)
        d.limb("dark", "M0 -10 L0 48", 3)
        d.shape("hero", "M2 -12 C16 4 18 28 6 48 L2 48Z", spot=True)
        d.marks("dark", circle(0, -10, 3.4))
        d.stroke("dark", "M0 -10 L-24 -62 M0 -10 L24 -62", 1, line=False)
    group(d, "translate(98 96) rotate(32)", boat)


def catamaran_side(d: Drawing):
    d.stroke("dark", "M100 30 L100.5 112", 3)
    d.shape("hero", "M98 34 C84 62 66 88 50 108 H98Z", spot=True)
    d.shape("light", "M103 40 L152 112 H103Z")
    d.shape("hero2", "M98 80 C92 90 84 100 76 108 H98Z", shadow=False)
    d.shape("deep", "M150 124 L172 116 C170 130 162 136 152 136Z")
    d.shape("light", "M58 124 L66 110 H128 L142 124Z")
    d.shape("dark", "M70 113 H126 L130 119 H67Z", shadow=False)
    d.shape("light", "M34 122 H176 L184 116 C182 130 170 140 156 140 H50 C40 140 34 132 34 122Z")
    d.shape("hero", "M36 128 H180 L178.6 132 H38Z", shadow=False)


def cat_lagoon(d: Drawing):
    d.disc("glow", 152, 46, 15)
    d.band("far", "M-30 126 H230")
    d.shape("ground", "M8 128 C18 116 38 112 56 118 C62 120 66 124 68 128Z")
    d.limb("trunk", "M34 122 Q34 104 42 90", 3.4)
    for ex, ey in [(-16, 6), (16, 4), (-8, -10), (10, -10)]:
        d.shape("near", f"M42 90 Q{42+ex*.6} {90+ey-6} {42+ex} {90+ey} Q{42+ex*.5} {90+ey*.5} 42 90Z", shadow=False)
    d.band("mid", waves(140, 3, 24))
    group(d, "translate(104 132) scale(.9) translate(-104 -128)", lambda: catamaran_side(d))
    d.stroke("light", "M140 150 H170 M30 156 H54", 2.2)
    d.band("near", waves(170, 4, 30), line=False)


DOLPHIN = ("M164 103 C160 100 152 99 146 97 C142 88 128 82 108 82 C84 82 62 90 48 100 L36 104 "
           "L22 92 C26 101 27 107 23 118 L38 110 C56 114 80 118 104 116 C126 114 140 110 150 106 "
           "C156 105 160 105 164 103Z")
DOLPHIN_BELLY = "M58 106 C76 113 100 114 122 111 C136 109 146 106 154 104 C146 109 128 114 104 116 C84 117 68 113 58 106Z"
DOLPHIN_FIN = "M90 85 C96 74 102 66 112 60 C109 69 110 77 116 84Z"
DOLPHIN_FLIPPER = "M122 108 C120 117 114 124 104 129 C109 121 111 114 112 109Z"


def cat_bow(d: Drawing):
    d.disc("glow", 150, 46, 13)
    d.band("far", "M-30 86 H230")
    d.shape("near", "M24 88 Q44 72 66 88Z", line=False)
    d.band("mid", waves(98, 3, 22))
    # dolphin arcing out of the water ahead
    group(d, "translate(102 96) rotate(-28) scale(.46) translate(-95 -100)", lambda: (
        d.shape("dolphin", DOLPHIN_FIN), d.shape("dolphin", DOLPHIN, spot=True),
        d.shape("belly", DOLPHIN_BELLY, shadow=False), d.shape("dolphin", DOLPHIN_FLIPPER, shadow=False),
        d.marks("mark", circle(142, 96, 3))))
    d.shape("light", spray(76, 120, 0.9, left=True), shadow=False)
    d.band("near", waves(120, 3, 26))
    for k in (-1, 1):
        x0 = 100 + k * 30
        d.shape("light", f"M{x0} 126 C{x0+k*14} 146 {x0+k*42} 190 {x0+k*58} 230 H{x0-k*30} C{x0-k*16} 190 {x0-k*6} 156 {x0} 126Z")
        d.stroke("hero", f"M{x0+k*4} 138 C{x0+k*18} 162 {x0+k*36} 200 {x0+k*48} 230", 3, line=False)
    d.shape("net", "M84 150 L116 150 L142 230 L58 230Z", shadow=False)
    d.stroke("dark", "M80 166 H120 M74 186 H126 M68 206 H132 M92 150 L84 230 M108 150 L116 230 M100 150 V230", 1.2)
    d.limb("dark", "M80 150 H120", 3.4)


# ================================================================ RIVER CRUISE
def river_ship(d: Drawing):
    """A long low river cruise ship, bow to the right, waterline at y 140."""
    d.shape("hero2", "M48 100 H140 L136 94 H52Z", spot=True)
    d.stroke("dark", "M56 100 V106 M96 100 V106 M134 100 V106", 1.4)
    d.shape("light", "M140 104 H154 L160 116 H140Z")
    d.shape("light", "M30 106 H160 L166 120 H30Z")
    d.shape("light", "M26 118 H172 L184 124 C182 134 176 140 166 140 H34 C28 140 26 134 26 118Z")
    d.shape("hero", "M26 130 H180 C178 136 174 140 166 140 H34 C28 140 26 136 26 130Z", shadow=False, spot=True)
    for x in range(36, 160, 10):
        d.marks("sky2", rrect(x, 109, 7, 6, 1.5))
        d.marks("dark", rrect(x, 122, 7, 4, 1.5))
    d.marks("dark", "M146 107 H154 L158 114 H146Z")


def rc_castle(d: Drawing):
    d.disc("glow", 52, 52, 14)
    d.band("far", "M-30 112 C10 106 30 86 60 82 C90 78 110 96 130 84 C150 70 176 64 230 80")
    d.stroke("near", "M40 104 L56 86 M54 104 L70 86 M68 104 L84 88 M82 104 L96 92", 2, line=False)
    # castle on the hill
    d.shape("light", "M134 82 V58 H144 V64 H150 V58 H160 V64 H166 V58 H176 V80Z")
    d.shape("light", rrect(140, 40, 14, 30, 1))
    d.shape("pop", "M138 42 L147 22 L156 42Z", spot=True)
    d.shape("pop", "M162 60 L169 46 L176 60Z")
    d.marks("dark", rrect(145, 48, 4, 6, 2) + rrect(150, 70, 6, 10, 3))
    d.band("near", "M-30 124 C30 118 70 120 100 116 C140 112 180 104 230 106")
    d.band("mid", "M-30 132 H230")
    group(d, "translate(100 150) scale(.86) translate(-104 -140)", lambda: river_ship(d))
    d.stroke("light", "M40 166 H66 M130 168 H160", 2.2)
    d.band("deep", waves(180, 3, 32), line=False)


def rc_bridge(d: Drawing):
    d.disc("glow", 150, 44, 14)
    for path in ["M24 92 V66 H38 V92Z", "M42 92 V52 L48 36 L54 52 V92Z", "M58 92 V72 H70 V92Z",
                 "M128 92 V66 C128 54 148 54 148 66 V92Z", "M154 92 V60 H168 V92Z", "M170 92 V74 H182 V92Z"]:
        d.shape("far", path, line=False)
    d.shape("far", "M135 58 L138 46 L141 58Z", line=False)
    d.band("far", "M-30 92 H230")
    d.band("mid", "M-30 100 H230")
    d.shape("bridge", "M-30 74 H230 V152 H-30Z M62 152 V128 A38 34 0 0 1 138 128 V152Z "
                      "M-34 152 V136 A30 26 0 0 1 26 136 V152Z M174 152 V136 A30 26 0 0 1 234 136 V152Z",
            extra='fill-rule="evenodd"')
    d.stroke("dark", "M-30 86 H230", 1.6, line=False)
    d.stroke("dark", "M26 152 V136 M62 152 V128 M138 152 V128 M174 152 V136", 1.2, line=False)
    for x in (44, 100, 156):
        d.stroke("dark", f"M{x} 74 V58", 2)
        d.shape("hero2", circle(x, 56, 4), shadow=False, spot=True)
    group(d, "translate(100 152) scale(.4) translate(-104 -140)", lambda: river_ship(d))
    d.band("near", waves(156, 3, 26))
    d.stroke("light", "M70 168 H96 M112 174 H132", 2.2)
    d.band("deep", waves(184, 3, 32), line=False)


def rc_steamer(d: Drawing):
    d.disc("glow", 48, 56, 14)
    d.band("far", hills(118, 8))
    d.band("mid", "M-30 130 H230")
    for x in (114, 132):
        d.shape("dark", f"M{x-4} 98 V48 H{x+4} V98Z")
        d.shape("dark", f"M{x-7} 44 L{x-4} 50 H{x+4} L{x+7} 44 L{x+4} 46 L{x+2} 42 L{x} 46 L{x-2} 42 L{x-4} 46Z")
    d.shape("light", cloud(108, 34, 0.8), shadow=False)
    d.shape("light", cloud(128, 22, 0.6), shadow=False)
    d.shape("light", "M60 98 H150 V108 H60Z")
    d.shape("light", rrect(132, 84, 20, 14, 2))
    d.marks("sky2", rrect(136, 88, 12, 5, 1))
    d.shape("light", "M44 108 H160 V122 H44Z")
    d.shape("light", "M36 122 H172 L180 126 C178 134 172 138 164 138 H44 C40 138 36 132 36 122Z")
    d.shape("hero", "M36 132 H178 C176 136 170 138 164 138 H44 C40 138 37 136 36 132Z", shadow=False, spot=True)
    d.stroke("dark", "M60 98 V108 M70 98 V108 M80 98 V108 M90 98 V108 M100 98 V108 M110 98 V108 M120 98 V108 M130 98 V108 M140 98 V108 "
                     "M54 112 H158", 1.2, line=False)
    for x in range(52, 160, 12):
        d.marks("dark", rrect(x, 112, 6, 7, 1.5))
    d.stroke("dark", "M150 98 V70", 1.6)
    d.shape("pop", "M151 70 L164 74 L151 78Z", shadow=False)
    # stern paddle wheel
    d.shape("pop", circle(30, 120, 22), spot=True)
    d.stroke("dark", "M8 120 H52 M30 98 V142 M14 104 L46 136 M14 136 L46 104", 2.4)
    d.shape("pop", circle(30, 120, 6), shadow=False)
    d.band("near", waves(140, 3, 24))
    d.stroke("light", "M60 156 H88 M130 160 H156", 2.2)
    d.band("deep", waves(176, 3, 30), line=False)


# ================================================================ WATERSKIING
def ski_pair(d: Drawing, role="hero"):
    d.shape(role, "M54 146 H138 C146 146 152 142 156 134 L159 136 C156 146 148 152 138 152 H54 C50 152 48 150 48 149 C48 147 50 146 54 146Z", spot=True)


def ws_skier(d: Drawing):
    d.disc("glow", 46, 50, 15)
    d.band("far", "M-30 120 H230")
    d.stroke("dark", "M126 92 L230 72", 1.4)
    d.shape("light", "M50 150 C34 140 20 120 22 96 C30 116 44 130 60 138Z", shadow=False)
    d.shape("light", "M44 154 C26 152 12 140 6 124 C18 136 32 142 50 144Z", shadow=False)
    group(d, "translate(-6 -6)", lambda: ski_pair(d, "hero2"))
    ski_pair(d)
    d.limb("dark", "M96 110 L112 126 L100 144 M92 112 L102 130 L88 146", 7.5)
    d.shape("pop", rrect(-7, -16, 15, 32, 7), extra='transform="translate(88 96) rotate(-24)"', spot=True)
    d.limb("skin", "M94 88 L112 96 L126 94 M92 92 L110 100 L126 96", 4.4)
    d.limb("dark", "M126 88 L126 100", 3.4)
    d.marks("skin", circle(80, 74, 8))
    d.marks("dark", "M72 72 C72 62 88 62 88 72 C84 68 76 68 72 72Z")
    d.band("mid", waves(150, 4, 26))
    d.band("near", waves(174, 4, 32), line=False)


def ws_skis(d: Drawing):
    d.disc("glow", 150, 44, 13)
    d.band("far", "M-30 72 L20 56 L60 66 L110 46 L160 64 L230 54")
    d.band("mid", "M-30 80 H230")
    d.band("near", waves(150, 3, 28), line=False)

    def ski(role):
        d.shape(role, "M0 -76 C8 -66 10 -54 10 -40 V66 C10 72 6 76 0 76 C-6 76 -10 72 -10 66 V-40 C-10 -54 -8 -66 0 -76Z", spot=True)
        d.shape("light", rrect(-2, -50, 4, 116, 2), shadow=False, line=False)
        d.shape("dark", rrect(-9, -6, 18, 20, 6))
        d.shape("dark", rrect(-8, 22, 16, 12, 5))
    group(d, "translate(100 108) rotate(-32)", lambda: ski("hero"))
    group(d, "translate(100 108) rotate(32)", lambda: ski("pop"))
    d.limb("rope", "M100 136 C80 150 120 168 100 186", 3.4)
    d.limb("dark", "M84 132 H116", 6)
    d.stroke("rope", "M84 132 L100 140 L116 132", 2)


SKIBOAT = "M20 120 C30 114 50 112 60 112 H150 L170 118 C166 130 156 136 146 136 H34 C26 136 20 130 20 120Z"


def ws_boat(d: Drawing):
    d.disc("glow", 150, 42, 14)
    d.band("far", "M-30 96 L20 70 L50 84 L90 56 L130 84 L160 68 L230 92")
    d.shape("light", "M90 56 L100 66 L94 65 L90 70 L85 64 L80 65Z", shadow=False)
    d.band("mid", "M-30 98 H230")
    # skier behind, on the right
    d.stroke("dark", "M68 98 L136 118", 1.2)
    d.shape("light", "M164 146 C176 136 182 120 180 104 C174 120 166 132 154 140Z", shadow=False)
    d.limb("dark", "M146 118 L152 132 L146 144 M142 120 L146 134 L138 144", 5)
    d.shape("pop", rrect(-5.5, -10, 11, 20, 5), extra='transform="translate(142 112) rotate(-20)"', spot=True)
    d.marks("skin", circle(138, 98, 5.4))
    d.limb("skin", "M140 108 L136 118", 3.4)
    d.shape("hero2", "M126 144 H164 C166 144 166 148 162 148 H126Z", spot=True)
    # boat, heading left
    group(d, "translate(16 50) scale(.62)", lambda: (
        d.shape("light", "M64 112 L84 92 H98 L92 112Z"),
        d.stroke("dark", "M86 112 V76 L92 74", 3),
        d.marks("skin", circle(108, 100, 6)),
        d.shape("pop", rrect(102, 104, 12, 10, 4), shadow=False),
        d.shape("hero", SKIBOAT, spot=True),
        d.stroke("light", "M30 124 H150", 2.4, line=False)))
    d.shape("light", "M104 130 C120 128 136 132 150 136 C136 136 120 134 104 130Z", shadow=False, line=False)
    d.band("near", waves(150, 3, 26))
    d.stroke("light", "M40 166 H66 M120 170 H150", 2.2)
    d.band("deep", waves(178, 3, 32), line=False)


# ================================================================ WAKEBOARDING
WAKEBOARD = "M-50 -2 C-52 -8 -46 -10 -40 -8 C-20 -4 20 -4 40 -8 C46 -10 52 -8 50 -2 C46 6 36 10 20 10 H-20 C-36 10 -46 6 -50 -2Z"


def wb_air(d: Drawing):
    d.disc("glow", 48, 48, 15)
    d.band("far", "M-30 140 H230")
    d.band("mid", "M-30 168 C20 168 50 160 70 146 C80 140 90 146 96 156 C104 166 150 166 230 162")
    d.shape("light", spray(70, 150, 1.6, left=True), shadow=False)
    d.stroke("dark", "M126 70 L230 46", 1.4)

    def rider():
        d.shape("hero", WAKEBOARD, spot=True)
        d.shape("dark", rrect(-28, -12, 12, 8, 3), shadow=False)
        d.shape("dark", rrect(16, -12, 12, 8, 3), shadow=False)
        d.limb("dark", "M-22 -10 L-18 -28 L-4 -40 M22 -10 L16 -28 L2 -40", 7.5)
        d.shape("pop", rrect(-8, -70, 16, 32, 7), extra='transform="rotate(-8 0 -54)"', spot=True)
        d.limb("skin", "M2 -64 L18 -66 L28 -70 M-4 -56 L-22 -40 L-26 -12", 4.4)
        d.limb("dark", "M28 -76 L28 -64", 3.4)
        d.marks("skin", circle(-2, -80, 8))
        d.shape("hero2", "M-11 -80 C-11 -92 7 -92 7 -80Z", shadow=False)
    group(d, "translate(98 120) rotate(-14)", rider)


def wb_cable(d: Drawing):
    d.disc("glow", 160, 52, 13)
    d.band("far", hills(118, 10, 20))
    d.band("mid", "M-30 126 H230")
    d.stroke("dark", "M42 48 L230 70", 1.6)
    d.limb("dark", "M30 130 L42 46 M54 130 L42 46", 4)
    d.stroke("dark", "M34 104 H50 M37 80 H47 M34 104 L47 80 M50 104 L37 80", 1.6)
    d.shape("pop", rrect(34, 40, 16, 10, 3), spot=True)
    d.shape("dark", rrect(118, 56, 10, 8, 2))
    d.stroke("dark", "M123 64 L142 120", 1.2)
    # kicker ramp
    d.shape("light", "M62 152 L104 152 L104 138Z")
    d.shape("hero2", "M62 152 L104 138 L104 141 L68 152Z", shadow=False)
    # rider
    d.limb("dark", "M138 140 L136 130 L144 122 M150 140 L150 130 L144 122", 5)
    d.shape("pop", rrect(139, 102, 11, 20, 5), spot=True)
    d.limb("skin", "M146 106 L142 118", 3.4)
    d.marks("skin", circle(146, 96, 5.4))
    d.shape("hero", "M126 142 C130 140 160 140 164 142 C162 146 130 146 126 142Z", spot=True)
    d.shape("light", spray(126, 144, 0.9, left=True), shadow=False)
    d.band("near", waves(156, 3, 26))
    d.band("deep", waves(180, 3, 32), line=False)


def wb_board(d: Drawing):
    d.disc("glow", 52, 52, 14)
    d.band("far", "M-30 96 H230")
    d.band("mid", "M-30 150 C20 150 60 140 100 116 C140 140 180 150 230 150")
    d.stroke("light", "M60 134 C80 128 90 122 100 116 C110 122 120 128 140 134", 3)

    def board():
        d.shape("hero", "M-16 -76 C-6 -82 6 -82 16 -76 C22 -40 22 40 16 76 C6 82 -6 82 -16 76 C-22 40 -22 -40 -16 -76Z", spot=True)
        d.shape("hero2", "M-15 -68 C-6 -72 6 -72 15 -68 L16 -58 C6 -62 -6 -62 -16 -58Z", shadow=False)
        d.shape("hero2", "M-15 68 C-6 72 6 72 15 68 L16 58 C6 62 -6 62 -16 58Z", shadow=False)
        for y in (-32, 30):
            d.shape("dark", f"M-14 {y-12} H14 V{y+12} H-14Z")
            d.shape("boot", f"M-12 {y-10} C-12 {y-18} 12 {y-18} 12 {y-10} V{y+10} C12 {y+14} -12 {y+14} -12 {y+10}Z")
            d.stroke("dark", f"M-8 {y-8} H8 M-8 {y-2} H8 M-8 {y+4} H8", 1.6)
    group(d, "translate(102 104) rotate(-38)", board)
    d.shape("light", spray(56, 152, 1.3, left=True), shadow=False)
    d.shape("light", spray(146, 152, 1.3, left=False), shadow=False)
    d.band("near", waves(170, 3, 30), line=False)


# ================================================================ WINDSURFING
def windsurf(d: Drawing, sail="hero", panel="hero2", rider=True, board="light", vest="pop", skin="skin", window="sky2"):
    """Board along y 150; mast foot at (96, 148); sail to the left, rider on the right."""
    d.shape(board, "M30 150 C30 145 40 144 60 144 H160 C172 144 180 146 182 150 C176 156 160 158 140 158 H40 C34 158 30 155 30 150Z")
    d.shape(sail, "M94 146 C86 110 78 66 74 24 C58 44 40 80 30 120 C52 128 74 138 94 146Z", spot=True)
    d.shape(panel, "M77 52 C64 68 52 88 44 108 C52 112 58 114 64 116 C68 94 72 72 77 52Z", shadow=False)
    d.shape(window, "M86 116 C80 112 72 108 64 106 C64 116 66 124 70 130 C76 132 82 134 88 136Z", shadow=False)
    d.stroke("dark", "M94 146 C86 110 78 66 74 24", 2.6)
    d.stroke("dark", "M76 40 L58 60 M80 70 L48 92 M84 96 L40 116", 1.2, line=False)
    if rider:
        d.stroke("dark", "M88 104 C70 96 44 100 36 114 C50 112 74 108 88 108", 2.6)
        d.limb("dark", "M108 146 L114 128 L120 116 M126 146 L126 130 L120 116", 7)
        d.shape(vest, rrect(-7, -15, 15, 30, 7), extra='transform="translate(126 102) rotate(26)"', spot=True)
        d.limb(skin, "M124 96 L104 100 L90 104 M124 102 L106 108 L90 108", 4.4)
        d.marks(skin, circle(134, 82, 8))
        d.marks("dark", "M126 80 C126 70 142 70 142 80 C138 76 130 76 126 80Z")


def wsf_rider(d: Drawing):
    d.disc("glow", 156, 50, 15)
    d.band("far", "M-30 130 H230")
    windsurf(d)
    d.shape("light", spray(30, 152, 1.1, left=True), shadow=False)
    d.band("mid", waves(156, 4, 26))
    d.band("near", waves(178, 4, 32), line=False)


def wsf_fleet(d: Drawing):
    d.disc("glow", 150, 44, 13)
    d.band("far", "M-30 104 C10 102 30 84 60 82 C86 80 100 96 120 104 H230")
    d.band("mid", "M-30 106 H230")
    for tx, ty, s, sail, panel, r in [(128, 112, .26, "pop", "light", False), (84, 118, .3, "hero2", "pop", False),
                                      (154, 132, .44, "light", "hero", True), (66, 148, .6, "hero", "hero2", True)]:
        group(d, f"translate({tx} {ty}) scale({s}) translate(-100 -150)",
              lambda sail=sail, panel=panel, r=r: windsurf(d, sail, panel, rider=r))
    d.stroke("light", "M110 170 H140 M30 166 H50", 2.2)
    d.band("near", waves(174, 3, 30), line=False)


def wsf_sunset(d: Drawing):
    d.disc("glow", 100, 112, 58)
    d.disc("glow2", 100, 112, 40, shadow=False, line=False)
    gulls(d, 150, 46)
    d.band("far", "M-30 136 H230")
    d.stroke("glow2", "M60 160 H90 M118 160 H140 M78 172 H122 M90 184 H110", 3, line=False)
    group(d, "translate(98 142) scale(.92) translate(-100 -150)",
          lambda: windsurf(d, "dark", "dark", True, "dark", "dark", "dark", "dark"))
    d.band("mid", waves(186, 3, 30), line=False)


# ================================================================ WHALE SHARK
WHALESHARK = ("M24 104 C24 92 40 84 64 82 C96 80 124 84 146 94 L160 100 L172 72 C178 86 178 100 174 108 "
              "C178 116 178 124 172 134 L158 112 C140 120 112 124 80 122 C50 120 24 116 24 104Z")
WS_BELLY = "M26 108 C40 114 60 118 80 118 C110 118 136 114 156 110 C140 120 112 124 80 122 C50 120 30 116 26 108Z"


def whaleshark(d: Drawing, spots=True):
    d.shape("hero", "M96 84 L112 60 L122 88Z")
    d.shape("hero", WHALESHARK)
    d.shape("light", WS_BELLY, shadow=False)
    d.shape("hero", "M62 114 L50 140 L84 118Z", shadow=False)
    d.stroke("mark", "M24 106 Q34 111 46 109", 1.8)
    d.stroke("mark", "M58 96 Q56 102 58 108 M63 95 Q61 101 63 107 M68 95 Q66 101 68 107", 1.4, line=False)
    d.marks("mark", circle(44, 98, 2))
    if spots:
        pts = []
        for col, x in enumerate(range(76, 156, 9)):
            for row, y in enumerate((88, 96, 104, 112)):
                yy = y + (4 if col % 2 else 0) - (x - 76) * 0.04 * row
                if yy < 113 - (x - 76) * 0.06:
                    pts.append(circle(x, yy, 1.9))
        for x, y in [(34, 96), (40, 92), (48, 90), (36, 102), (54, 92), (52, 86)]:
            pts.append(circle(x, y, 1.4))
        d.marks("light", " ".join(pts))
        d.stroke("light", "M74 86 C72 96 72 106 74 114 M100 85 C98 96 98 106 100 116", 1.2, line=False)


def ocean(d: Drawing):
    d.band("far", "M-30 30 H230", line=False)
    d.band("mid", waves(150, 4, 30))
    d.band("deep", waves(176, 3, 34), line=False)


def wss_portrait(d: Drawing):
    d.band("sky2", waves(22, 4, 26))
    d.raw('<g opacity=".18" fill="#fff"><path d="M60 0 L82 0 L120 200 L98 200Z"/><path d="M128 0 L140 0 L176 200 L164 200Z"/></g>', "")
    ocean(d)
    for x, y, s in [(56, 152, 0.6), (148, 156, 0.7), (160, 46, 0.7)]:
        d.shape("hero2", fish(x, y, s), shadow=False)
    group(d, "translate(100 100) scale(1.0) translate(-100 -104)", lambda: whaleshark(d))
    bubbles(d, [(30, 76, 2.5), (24, 64, 3.5)])


def wss_swimmer(d: Drawing):
    d.band("sky2", waves(46, 4, 26))
    d.band("far", waves(56, 3, 30), line=False)
    d.band("mid", waves(170, 4, 30))
    # snorkeller floating face-down at the surface
    d.limb("hero2", "M64 52 V28", 4.4, spot=True)
    d.limb("skin", "M96 60 L126 56 M96 64 L126 66", 6)
    d.shape("pop", ellipse(134, 55, 10, 4), extra='transform="rotate(-8 134 55)"', spot=True)
    d.shape("pop", ellipse(134, 67, 10, 4), extra='transform="rotate(8 134 67)"', spot=True)
    d.shape("hero2", rrect(64, 54, 38, 14, 7))
    d.shape("dark", circle(60, 60, 8))
    d.shape("light", rrect(50, 61, 9, 6, 2), shadow=False)
    group(d, "translate(100 124) scale(.9) translate(-100 -104)", lambda: whaleshark(d))
    bubbles(d, [(46, 80, 2), (40, 70, 2.6)])


def wss_mouth(d: Drawing):
    d.band("sky2", waves(22, 4, 26))
    ocean(d)
    d.marks("light", " ".join(circle(x, y, 1.2) for x, y in [(30, 60), (44, 48), (160, 58), (172, 76), (150, 42), (24, 84), (60, 34), (140, 30)]))
    d.shape("hero", "M30 122 L12 154 L50 134Z")
    d.shape("hero", "M170 122 L188 154 L150 134Z")
    d.shape("hero", "M100 46 L90 70 H110Z")
    d.shape("hero", "M22 110 C22 80 60 66 100 66 C140 66 178 80 178 110 C178 132 150 146 100 146 C50 146 22 132 22 110Z")
    d.shape("light", "M30 124 C50 140 150 140 170 124 C162 138 136 146 100 146 C64 146 38 138 30 124Z", shadow=False)
    d.shape("dark", "M34 114 C60 124 140 124 166 114 C156 134 130 140 100 140 C70 140 44 134 34 114Z", spot=True)
    d.stroke("mark", "M42 120 C64 130 136 130 158 120", 1.4, line=False)
    pts = []
    for x in range(40, 164, 12):
        for y in (78, 88, 98):
            dy = abs(x - 100) * 0.12
            if 22 < x < 178 and (y + dy) < 106:
                pts.append(circle(x + (6 if y == 88 else 0), y + dy, 2.2))
    d.marks("light", " ".join(pts))
    d.marks("mark", circle(30, 104, 3) + circle(170, 104, 3))
    d.shape("hero2", fish(100, 156, 0.7), shadow=False)
    bubbles(d, [(100, 34, 2.5), (92, 24, 2)])


# ================================================================ concepts
WHALE = {"hero": "#4E6E86", "light": "#EEF3F6", "mark": "#16242F"}
SEAL = {"seal": "#8A8F96", "seal2": "#C3C8CD", "mark": "#1E2230"}
MOOSE_C = {"moose": "#5A3E2B", "moose2": "#3E2A1D", "mark": "#1A120C"}

CONCEPTS = [
    Concept("bodyboard-flatlay", "bodyboarding", "Board & fins", clipline(bb_flatlay), SEA,
            checks=[("hero", "ground"), ("pop", "ground"), ("hero2", "hero"), ("mid", "ground"), ("mark", "ground")],
            fixes={"hero": ["hero", "pop", "near"], "pop": ["hero", "near", "deep"], "hero2": ["light", "glow2"]}),
    Concept("bodyboard-wave", "bodyboarding", "Riding the wave", clipline(bb_wave), SEA, SKIN,
            checks=[("hero", "near"), ("dark", "near"), ("near", "far"), ("light", "near")], fixes={"hero": ["pop", "hero2", "light"], "far": ["sky2", "mid"]}),
    Concept("bodyboard-tower", "bodyboarding", "Lifeguard beach", clipline(bb_tower), SEA,
            checks=[("hero", "ground"), ("light", "far"), ("pop", "sky"), ("dark", "ground")], fixes={"hero": ["pop", "near", "deep"], "light": ["#FFF4DE"]}),
    Concept("seakayak-arch", "sea-kayaking", "Sea arch", sk_arch, SEA, SKIN,
            checks=[("near", "far"), ("near", "sky"), ("hero", "mid"), ("hero", "deep")], fixes={"near": ["deep", "ground"], "hero": ["pop", "hero2"]}),
    Concept("seakayak-seal", "sea-kayaking", "Seal says hello", clipline(sk_seal), SEA, SEAL,
            checks=[("seal", "mid"), ("hero", "mid"), ("seal", "far")], fixes={"mid": ["near", "far"], "hero": ["pop", "dark"]}),
    Concept("seakayak-deck", "sea-kayaking", "On deck", clipline(sk_deck), SEA, SKIN,
            checks=[("hero", "mid"), ("hero", "near"), ("near", "far")], fixes={"hero": ["pop", "hero2"]}),
    Concept("canoe-lake", "canoeing", "Canoe on the lake", canoe_lake, SEA, SKIN,
            checks=[("hero", "mid"), ("deep", "mid"), ("far", "sky")], fixes={"hero": ["pop", "dark"], "far": ["mid", "near"]}),
    Concept("canoe-portage", "canoeing", "Portage", clipline(canoe_portage), overrides=SKIN,
            checks=[("hero", "sky"), ("hero", "far"), ("pop", "hero"), ("dark", "ground")], fixes={"hero": ["pop", "near", "deep"], "pop": ["hero2", "mark"]}),
    Concept("canoe-moose", "canoeing", "Moose at dawn", canoe_moose, SEA, {**SKIN, **MOOSE_C},
            checks=[("moose", "glow"), ("moose", "far"), ("moose", "mid"), ("moose", "sky")], fixes={"glow": ["glow2", "light"], "far": ["mid", "sky2"]}),
    Concept("yacht-cove", "yacht-charter", "Anchored in a cove", yacht_cove, SEA,
            checks=[("light", "far"), ("hero2", "sky"), ("ground", "far"), ("light", "ground"), ("ground", "sky")], fixes={"ground": ["near", "deep"], "far": ["mid", "near"], "hero2": ["pop", "hero"]}),
    Concept("yacht-anchor", "yacht-charter", "Anchor & rope", yacht_anchor, SEA, {"anchor": "#2F3E4E", "rope": "#C8945A"},
            checks=[("anchor", "far"), ("anchor", "mid"), ("anchor", "sky"), ("rope", "far"), ("rope", "sky")], fixes={"far": ["mid", "near"], "mid": ["far", "near"]}),
    Concept("yacht-cap", "yacht-charter", "Skipper's cap", yacht_cap, SEA,
            checks=[("light", "ground"), ("light", "far"), ("light", "sky"), ("dark", "ground")], fixes={"ground": ["near", "deep", "mid"], "sky": ["sky2", "far"]}),
    Concept("catamaran-aerial", "catamaran-cruise", "Twin hulls from above", clipline(cat_aerial), SEA, {"net": "#F3EBDD"},
            checks=[("light", "far"), ("hero", "light"), ("hero2", "light")], fixes={"far": ["mid", "near"], "hero2": ["pop", "hero"]}),
    Concept("catamaran-lagoon", "catamaran-cruise", "Lagoon sail", cat_lagoon, SEA, {"trunk": "#8A5A3B"},
            checks=[("light", "sky"), ("light", "far"), ("hero", "sky"), ("ground", "far")], fixes={"sky": ["sky2", "far"], "far": ["mid", "near"], "ground": ["hero2", "light"]}),
    Concept("catamaran-bow", "catamaran-cruise", "Bow net & dolphin", clipline(cat_bow), SEA,
            {"dolphin": "#6F8FAF", "belly": "#D9E4EE", "net": "#F3EBDD", "mark": "#1E2A3A"},
            checks=[("dolphin", "mid"), ("light", "near"), ("light", "mid")], fixes={"mid": ["far", "near"]}),
    Concept("rivercruise-castle", "river-cruise", "Castle on the river", rc_castle,
            checks=[("light", "far"), ("light", "mid"), ("hero2", "light"), ("light", "near")], fixes={"far": ["mid", "near"], "hero2": ["pop", "hero"]}),
    Concept("rivercruise-bridge", "river-cruise", "Under the bridge", rc_bridge, overrides={"bridge": "#D9C2A0"},
            checks=[("bridge", "sky"), ("bridge", "far"), ("light", "near"), ("bridge", "mid"), ("bridge", "near")],
            fixes={"bridge": ["#C4A27A", "#B08A64", "#E8D8BE"], "far": ["mid", "near", "deep"]}),
    Concept("rivercruise-steamer", "river-cruise", "Paddle steamer", rc_steamer,
            checks=[("light", "sky"), ("light", "far"), ("pop", "mid"), ("dark", "sky")], fixes={"sky": ["sky2", "far"], "far": ["mid", "near"], "pop": ["hero", "deep"]}),
    Concept("waterski-skier", "waterskiing", "Water skier", ws_skier, SEA, SKIN,
            checks=[("hero", "mid"), ("hero", "far"), ("dark", "far"), ("light", "far")], fixes={"hero": ["pop", "dark"], "far": ["mid", "near"]}),
    Concept("waterski-skis", "waterskiing", "Skis & handle", ws_skis, SEA, {"rope": "#E8D3A8"},
            checks=[("hero", "mid"), ("pop", "mid"), ("hero", "pop"), ("pop", "near")], fixes={"hero": ["hero2", "dark"], "pop": ["dark", "deep"]}),
    Concept("waterski-boat", "waterskiing", "Tow boat", ws_boat, SEA, SKIN,
            checks=[("hero", "mid"), ("light", "mid"), ("pop", "mid"), ("hero2", "mid")], fixes={"hero": ["pop", "dark"], "pop": ["hero", "dark"], "hero2": ["light", "pop"]}),
    Concept("wakeboard-air", "wakeboarding", "Big air", wb_air, SEA, SKIN,
            checks=[("hero", "sky"), ("dark", "sky"), ("pop", "sky"), ("hero", "far")], fixes={"hero": ["pop", "near", "deep"]}),
    Concept("wakeboard-cable", "wakeboarding", "Cable park", wb_cable, SEA, SKIN,
            checks=[("dark", "sky"), ("light", "mid"), ("hero", "mid"), ("pop", "mid")], fixes={"hero": ["hero2", "light"], "pop": ["hero", "dark"]}),
    Concept("wakeboard-board", "wakeboarding", "Board & boots", wb_board, SEA, {"boot": "#2F3E4E"},
            checks=[("hero", "far"), ("hero", "mid"), ("hero", "sky"), ("boot", "hero")], fixes={"hero": ["pop", "hero2"]}),
    Concept("windsurf-rider", "windsurfing", "Windsurfer", wsf_rider, SEA, SKIN,
            checks=[("hero", "sky"), ("hero", "far"), ("hero2", "hero"), ("pop", "sky")], fixes={"hero": ["pop", "deep"], "hero2": ["light", "glow2"]}),
    Concept("windsurf-fleet", "windsurfing", "Sails on the bay", wsf_fleet, SEA, SKIN,
            checks=[("hero", "mid"), ("pop", "far"), ("light", "far"), ("hero2", "mid")], fixes={"far": ["near", "deep"], "hero": ["pop", "dark"]}),
    Concept("windsurf-sunset", "windsurfing", "Sunset session", wsf_sunset,
            checks=[("dark", "glow"), ("dark", "glow2"), ("dark", "sky"), ("glow", "sky"), ("far", "glow")], fixes={"glow": ["glow2", "pop", "hero2"], "far": ["mid", "near", "deep"]}),
    Concept("whaleshark-portrait", "whale-shark-swim", "Whale shark", wss_portrait, UNDERWATER, WHALE,
            checks=[("hero", "far"), ("hero", "mid"), ("hero", "sky2")], fixes={"hero": ["#7D9AB2", "#8FA9BC"]}),
    Concept("whaleshark-swimmer", "whale-shark-swim", "Swim alongside", wss_swimmer, UNDERWATER, {**WHALE, **SKIN},
            checks=[("hero", "far"), ("hero", "mid"), ("hero2", "sky2"), ("hero2", "far")], fixes={"hero": ["#7D9AB2", "#8FA9BC"]}),
    Concept("whaleshark-mouth", "whale-shark-swim", "Open wide", wss_mouth, UNDERWATER, WHALE,
            checks=[("hero", "far"), ("hero", "mid"), ("dark", "hero")], fixes={"hero": ["#7D9AB2", "#8FA9BC"]}),
]
