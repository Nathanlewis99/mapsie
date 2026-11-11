"""Trails A: hiking, trekking, summit climb, rock climbing, caving, sandboarding,
dune bashing, quad biking, mountain biking and cycling tours."""
from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group


# ================================================================ private helpers
def pine(x: float, base: float, h: float, w: float | None = None) -> str:
    """A three-tier pine tree, base centred on (x, base)."""
    w = w or h * 0.55
    t = base - h
    return (f"M{x} {t} L{x + w*0.32} {t + h*0.32} L{x + w*0.2} {t + h*0.32} L{x + w*0.42} {t + h*0.62} "
            f"L{x + w*0.28} {t + h*0.62} L{x + w*0.5} {base - h*0.12} L{x - w*0.5} {base - h*0.12} "
            f"L{x - w*0.28} {t + h*0.62} L{x - w*0.42} {t + h*0.62} L{x - w*0.2} {t + h*0.32} L{x - w*0.32} {t + h*0.32}Z")


def pine_tree(d: Drawing, x, base, h, role="deep"):
    d.limb("dark", f"M{x} {base} V{base - h*0.2}", max(h * 0.08, 2))
    d.shape(role, pine(x, base, h))


def stars(d: Drawing, pts, role="light"):
    for x, y, r in pts:
        d.marks(role, f"M{x} {y-r} L{x+r*0.3} {y-r*0.3} L{x+r} {y} L{x+r*0.3} {y+r*0.3} L{x} {y+r} "
                      f"L{x-r*0.3} {y+r*0.3} L{x-r} {y} L{x-r*0.3} {y-r*0.3}Z")


def flags(d: Drawing, x0, y0, x1, y1, sag, n, roles=("pop", "hero2", "hero", "light", "far"), size=3.5):
    """Prayer flags on a sagging string between two points."""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + sag
    d.stroke("dark", f"M{x0} {y0} Q{cx} {cy} {x1} {y1}", 1.3)
    for i in range(1, n + 1):
        t = i / (n + 1)
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1
        d.shape(roles[i % len(roles)], rrect(x - size, y, size * 2, size * 2.2, 0.6), shadow=False, spot=i % 2 == 0)


def bicycle(d: Drawing, frame="hero", wheels="dark", tyre_w=4.5, r=22, knobbly=False, rack=False):
    """Side-view bike, rear wheel at (60,140), front at (140,140), facing right."""
    rx, fx, y = 60, 140, 140
    for x in (rx, fx):
        d.stroke(wheels, circle(x, y, r), tyre_w, shadow=True)
        if knobbly:
            d.stroke(wheels, circle(x, y, r + tyre_w * 0.55), 2.2, line=False)
        d.stroke(wheels, f"M{x-r+2} {y} H{x+r-2} M{x} {y-r+2} V{y+r-2} M{x-r*0.7} {y-r*0.7} L{x+r*0.7} {y+r*0.7} "
                         f"M{x-r*0.7} {y+r*0.7} L{x+r*0.7} {y-r*0.7}", 0.8, line=False)
        d.marks("dark", circle(x, y, 2.6))
    bb = (92, 142)
    seat = (84, 104)
    head = (126, 102)
    d.limb(frame, f"M{rx} {y} L{bb[0]} {bb[1]} L{head[0]} {head[1]+6} L{seat[0]+1} {seat[1]+4} Z M{rx} {y} L{seat[0]+1} {seat[1]+4} "
                  f"L{seat[0]} {seat[1]} M{head[0]} {head[1]} L{fx} {y}", 5, spot=True)
    d.limb("dark", f"M{seat[0]-8} {seat[1]-2} L{seat[0]+6} {seat[1]-2}", 4)
    d.limb("dark", f"M{head[0]} {head[1]} L{head[0]-3} {head[1]-8} L{head[0]+8} {head[1]-10}", 3.6)
    d.stroke("dark", f"M{bb[0]} {bb[1]} L{bb[0]+7} {bb[1]+8}", 2.6)
    d.marks("dark", circle(bb[0], bb[1], 5))
    if rack:
        d.limb("dark", f"M{rx} {y} L{rx-4} {y-30} M{rx+16} {y-29} L{rx-14} {y-31}", 2.4)


# ================================================================ HIKING
BOOT = ("M70 94 Q86 88 104 90 L104 84 Q110 82 112 88 L112 114 Q132 118 148 128 Q160 136 158 152 "
        "L62 152 Q58 122 70 94Z")


def hike_boot(d: Drawing):
    d.disc("glow", 140, 62, 22)
    d.band("far", "M-30 112 L18 86 L46 104 L84 66 L118 100 L150 78 L190 104 L230 90")
    for snow in ["M84 66 L95 77 L89 76 L84 81 L78 75 L73 77Z", "M150 78 L160 87 L155 86 L150 90 L145 85 L141 86Z"]:
        d.shape("light", snow, shadow=False)
    d.band("mid", hills(130, 10))
    # signpost
    d.shape("dark", rrect(45.5, 68, 5, 100, 2))
    d.shape("hero2", "M32 70 H74 L82 77 L74 84 H32Z", spot=True)
    d.shape("hero2", "M66 90 H26 L18 97 L26 104 H66Z", spot=True)
    d.marks("dark", circle(38, 77, 1.6) + circle(60, 97, 1.6))
    d.band("ground", "M-30 168 Q60 150 120 158 T230 150")
    d.band("near", "M-30 186 Q50 176 110 182 T230 178", line=False)

    def boot():
        d.shape("hero", BOOT)
        d.shape("mark", "M118 116 Q140 120 152 132 Q158 140 158 152 L122 152 Q114 132 118 116Z", shadow=False)
        d.shape("hero2", "M62 140 H158 V152 H62Z", shadow=False, spot=True)
        d.shape("dark", rrect(58, 150, 104, 11, 4.5))
        d.marks("light", "M66 158 h7 v2 h-7Z M80 158 h7 v2 h-7Z M94 158 h7 v2 h-7Z M108 158 h7 v2 h-7Z M122 158 h7 v2 h-7Z M136 158 h7 v2 h-7Z M150 158 h7 v2 h-7Z")
        d.stroke("light", "M98 96 L112 93 M99 104 L113 101 M100 112 L114 109 M101 120 L115 118", 2.2)
        d.shape("mark", "M70 94 Q86 88 104 90 L104 96 Q86 94 69 100Z", shadow=False)
        d.stroke("dark", "M68 96 Q62 88 68 84", 2.4)
    group(d, "translate(40 34) scale(.84)", boot)


def hike_backpack(d: Drawing):
    d.disc("glow", 52, 60, 20)
    d.band("far", "M-30 120 L22 88 L52 108 L96 64 L134 100 L164 80 L230 112")
    for snow in ["M96 64 L108 76 L102 75 L96 80 L90 74 L84 76Z", "M164 80 L173 88 L168 87 L164 91 L159 86 L156 87Z"]:
        d.shape("light", snow, shadow=False)
    d.band("mid", hills(140, 10, 10))
    pine_tree(d, 28, 150, 40)
    pine_tree(d, 172, 148, 46)
    pine_tree(d, 186, 154, 30)
    d.band("ground", "M-30 168 Q100 156 230 168")
    # sleeping mat on top
    d.shape("hero2", rrect(66, 50, 68, 18, 9), spot=True)
    d.stroke("dark", "M78 51 V67 M122 51 V67", 2)
    d.shape("light", ellipse(130, 59, 4, 8.5), shadow=False)
    # side water bottle
    d.shape("pop", rrect(136, 98, 16, 34, 5))
    d.shape("dark", rrect(139, 92, 10, 8, 2), shadow=False)
    # body
    d.shape("hero", "M70 74 Q70 64 82 64 H118 Q130 64 130 74 L134 160 Q134 168 126 168 H74 Q66 168 66 160Z")
    d.shape("mark", "M70 72 Q70 62 84 62 H116 Q130 62 130 72 L130 92 Q100 100 70 92Z")
    d.shape("hero", rrect(78, 116, 44, 40, 9))
    d.stroke("dark", "M82 124 H118", 2.2)
    d.shape("mark", rrect(94, 88, 12, 18, 2), shadow=False)
    d.marks("light", rrect(96.5, 99, 7, 5, 1.5))
    d.stroke("dark", "M84 138 Q76 144 78 152 M116 138 Q124 144 122 152", 1.6, line=False)
    d.shape("dark", rrect(92, 160, 16, 6, 2), shadow=False)
    d.stroke("pop", "M108 60 q6 -12 12 -2", 2.4)
    d.band("near", "M-30 182 Q100 172 230 182", line=False)


def hike_trail(d: Drawing):
    d.disc("glow", 136, 56, 18)
    d.band("far", "M-30 104 L26 72 L58 92 L100 54 L140 88 L170 70 L230 98")
    for snow in ["M100 54 L112 65 L106 64 L100 69 L94 63 L88 65Z", "M26 72 L34 79 L29 78 L25 82 L21 77 L18 78Z",
                 "M170 70 L178 77 L173 76 L170 80 L166 76 L163 77Z"]:
        d.shape("light", snow, shadow=False)
    d.band("mid", hills(118, 12, -10))
    d.band("near", hills(140, 10, 20))
    # winding trail
    d.shape("ground", "M80 210 C100 180 150 176 140 156 C132 142 96 146 100 130 C102 122 112 120 118 118 "
                      "L122 119 C116 122 108 126 110 131 C114 140 150 140 156 156 C164 182 130 192 128 210Z")
    for x, b, h in [(30, 150, 46), (50, 162, 36), (176, 150, 42), (162, 168, 30)]:
        pine_tree(d, x, b, h)
    # hiker
    def hiker():
        d.shape("hero", rrect(-9, -36, 15, 22, 5), spot=True)  # pack
        d.limb("mark", "M2 -6 L-4 12 M4 -6 L10 12", 5)
        d.limb("hero2", "M0 -32 L4 -8", 9)
        d.limb("hero2", "M6 -26 L14 -14", 4)
        d.stroke("dark", "M14 -14 L18 12", 1.6)
        d.shape("mark", circle(4, -40, 5.5))
    group(d, "translate(106 152) scale(.95)", hiker)
    d.band("deep", "M-30 190 Q100 180 230 190", line=False)


# ================================================================ TREKKING
TENT = "M50 156 L96 82 L100 80 L104 82 L156 156Z"


def trek_tent(d: Drawing):
    stars(d, [(40, 52, 3), (62, 36, 2.2), (150, 40, 2.6), (170, 70, 2), (90, 30, 1.8), (124, 26, 2.2)])
    d.disc("glow", 140, 58, 14)
    d.band("far", "M-30 120 L30 78 L58 98 L100 56 L136 92 L168 72 L230 112")
    for snow in ["M100 56 L114 70 L107 69 L100 75 L93 68 L86 70Z", "M30 78 L40 87 L34 86 L30 90 L25 85 L21 86Z",
                 "M168 72 L177 80 L172 79 L168 83 L164 79 L160 80Z"]:
        d.shape("light", snow, shadow=False)
    d.band("mid", hills(140, 8))
    flags(d, 22, 112, 70, 104, 10, 6, size=3)
    d.shape("dark", rrect(20.8, 110, 2.4, 38, 1))
    d.shape("hero", TENT)
    d.shape("hero2", "M100 80 L104 82 L156 156 L134 156Z", shadow=False)
    d.shape("dark", "M100 104 L118 156 L82 156Z", spot=True)
    d.shape("glow2", "M100 120 L110 156 L90 156Z", shadow=False)
    d.stroke("dark", "M50 156 L36 160 M156 156 L170 160 M100 80 V72", 1.6)
    d.band("ground", "M-30 160 Q100 150 230 160")
    d.band("near", "M-30 182 Q100 172 230 182", line=False)


LLAMA = ("M58 104 C58 92 70 88 84 88 L118 88 C124 88 126 84 126 78 L124 46 C124 40 128 36 134 36 L140 36 "
         "C146 36 150 40 152 44 L156 48 C158 52 154 56 148 54 L144 54 L142 82 C142 92 140 104 132 112 "
         "L132 156 L124 156 L122 120 L116 120 L115 156 L107 156 L104 124 L84 124 L82 156 L74 156 L72 122 "
         "L68 122 L66 156 L58 156 L58 118 C52 116 50 110 52 104Z")


def trek_llama(d: Drawing):
    d.disc("glow", 60, 62, 22)
    d.band("far", "M-30 100 L20 76 L48 92 L80 60 L112 86 L140 66 L180 92 L230 80")
    d.band("mid", "M-30 124 Q40 106 90 118 T230 112")
    for y in (128, 138):
        d.stroke("near", f"M-30 {y} Q40 {y-12} 90 {y-4} T230 {y-6}", 2.2, line=False)
    d.band("near", hills(150, 6))
    d.shape("light", cloud(150, 116, 0.8), shadow=False)

    def llama():
        d.stroke("hero", "M54 106 Q44 112 48 124", 5)
        d.shape("hero", LLAMA)
        d.shape("hero", "M132 38 L130 24 L137 34Z")
        d.shape("hero", "M140 37 L142 23 L145 35Z", shadow=False)
        d.shape("pop", "M80 86 H122 V114 Q101 120 80 114Z", spot=True)
        d.shape("hero2", "M80 94 H122 V100 H80Z", shadow=False)
        d.shape("hero2", "M80 106 H122 V110 H80Z", shadow=False)
        d.marks("dark", "M86 116 l2 6 l2 -6Z M96 117 l2 6 l2 -6Z M106 117 l2 6 l2 -6Z M116 116 l2 6 l2 -6Z")
        d.shape("hero2", rrect(88, 72, 26, 16, 5))
        d.stroke("dark", "M88 78 H114", 1.4)
        d.marks("mark", circle(143, 44, 1.9))
        d.marks("mark", "M152 48 l3 1 l-3 1Z")
        d.stroke("pop", "M126 50 Q134 56 142 50", 2.4, line=False)
    group(d, "translate(-6 10)", llama)
    d.band("ground", "M-30 168 Q100 160 230 168")
    d.band("deep", "M-30 186 Q100 178 230 186", line=False)


def trek_bridge(d: Drawing):
    d.disc("glow", 100, 70, 26)
    d.band("far", "M-30 96 L26 66 L56 84 L100 44 L146 82 L176 64 L230 92")
    for snow in ["M100 44 L114 58 L107 57 L100 63 L93 56 L86 58Z", "M26 66 L34 73 L29 72 L25 76 L21 71 L18 72Z",
                 "M176 64 L185 72 L180 71 L176 75 L172 71 L168 72Z"]:
        d.shape("light", snow, shadow=False)
    d.band("mid", hills(130, 8))
    d.stroke("light", "M96 200 Q104 170 98 150 Q94 140 100 132", 6, line=False)
    # cliffs
    d.shape("near", "M-30 104 L36 104 Q42 118 38 140 Q46 168 40 230 L-30 230Z")
    d.shape("near", "M230 104 L164 104 Q158 118 162 140 Q154 168 160 230 L230 230Z")
    d.shape("deep", "M-30 104 L36 104 L37 110 L-30 110Z", shadow=False)
    d.shape("deep", "M230 104 L164 104 L163 110 L230 110Z", shadow=False)
    # posts
    for x in (30, 170):
        d.shape("dark", rrect(x - 2.2, 78, 4.4, 30, 1.5))
    # hangers and deck
    d.stroke("dark", "M30 82 Q100 116 170 82", 2)
    hangers = ""
    for i in range(1, 12):
        t = i / 12
        x = 30 + 140 * t
        top = (1 - t) ** 2 * 82 + 2 * (1 - t) * t * 116 + t * t * 82
        deck = (1 - t) ** 2 * 106 + 2 * (1 - t) * t * 138 + t * t * 106
        hangers += f"M{x:.1f} {top:.1f} V{deck:.1f} "
    d.stroke("dark", hangers, 1.2)
    d.limb("hero", "M30 106 Q100 138 170 106", 6, spot=True)
    planks = ""
    for i in range(1, 20):
        t = i / 20
        x = 30 + 140 * t
        y = (1 - t) ** 2 * 106 + 2 * (1 - t) * t * 138 + t * t * 106
        planks += f"M{x:.1f} {y-2.4:.1f} V{y+2.4:.1f} "
    d.stroke("mark", planks, 1, line=False)
    flags(d, 30, 80, 170, 80, 22, 10, size=3.2)
    d.band("deep", "M-30 196 Q100 190 230 196", line=False)


# ================================================================ SUMMIT CLIMB
def summit_flag(d: Drawing):
    d.disc("glow", 52, 64, 18)
    d.shape("light", cloud(136, 52, 0.9), shadow=False)
    d.band("far", "M-30 140 L30 104 L60 122 L84 108 L230 150")
    d.shape("mid", "M20 230 L100 66 L180 230Z")
    d.shape("near", "M100 66 L180 230 L118 230 L112 150 L120 120 Z", shadow=False)
    d.shape("light", "M100 66 L120 106 L110 100 L102 110 L94 98 L84 104 L80 106Z", shadow=False)
    d.shape("dark", rrect(98.6, 30, 2.8, 40, 1))
    d.shape("pop", "M101.5 31 L132 38 L101.5 46Z", spot=True)
    d.shape("light", cloud(10, 158, 1.5))
    d.shape("light", cloud(132, 166, 1.4))
    d.shape("light", cloud(60, 178, 1.6))


def summit_axe(d: Drawing):
    d.disc("glow", 140, 58, 20)
    d.band("far", "M-30 108 L28 74 L60 96 L102 58 L140 92 L172 72 L230 104")
    for snow in ["M102 58 L114 70 L108 69 L102 74 L96 68 L90 70Z", "M28 74 L36 81 L31 80 L27 84 L23 79 L20 80Z",
                 "M172 72 L181 80 L176 79 L172 83 L168 79 L164 80Z"]:
        d.shape("light", snow, shadow=False)
    d.band("mid", hills(124, 8, 10))
    d.band("light", "M-30 150 Q60 126 120 140 T230 128")
    # rope coil lying in the snow
    for k, (cx, cy, rx) in enumerate([(58, 158, 28), (58, 153, 26), (58, 148, 24)]):
        d.stroke("pop", ellipse(cx, cy, rx, rx * 0.38), 5, shadow=k == 0)
    d.stroke("pop", "M84 158 Q100 172 128 166", 4.5)
    # ice axe planted in the slope, pick at the top
    d.limb("hero", "M124 160 L136 70", 8, spot=True)
    d.shape("dark", "M124.4 146 L134.2 147.4 L132.4 160.6 L122.6 159.2Z", shadow=False)
    d.shape("mark", "M98 64 Q118 56 134 60 L144 62 Q160 66 172 84 Q172 88 168 88 Q156 74 142 72 L132 71 Q116 70 100 72 Q94 70 98 64Z")
    d.shape("mark", rrect(130, 56, 12, 20, 3))
    d.shape("light", "M118 160 Q130 150 142 160 Q130 164 118 160Z", shadow=False)
    d.band("light", "M-30 170 Q80 152 140 160 T230 154")
    d.stroke("far", "M100 168 Q120 162 140 166 M30 176 Q48 170 64 176", 2, line=False)


def summit_climber(d: Drawing):
    d.disc("glow", 150, 58, 22)
    d.band("far", "M-30 118 L20 96 L54 110 L230 140")
    # ridge to the summit, going up to the right
    d.shape("mid", "M-30 230 L-30 176 L60 150 L150 72 L172 86 L230 120 L230 230Z")
    d.shape("light", "M-30 176 L60 150 L150 72 L172 86 L156 82 L118 108 L70 160 L-30 190Z", shadow=False)
    d.shape("dark", rrect(148.8, 48, 2.4, 28, 1))
    d.shape("pop", "M151 49 L170 54 L151 60Z", spot=True)

    def climber():
        d.stroke("pop", "M-6 -14 Q-30 0 -54 20", 2.2)
        d.limb("mark", "M-2 4 L-10 22 M4 4 L12 20", 6.5)
        d.shape("hero", rrect(-16, -34, 14, 22, 4), spot=True)  # pack
        d.limb("hero2", "M-3 -32 L2 -2", 12)
        d.limb("hero2", "M2 -26 L14 -16", 5)
        d.limb("dark", "M14 -16 L18 6", 2.2)
        d.shape("dark", "M12 -18 L24 -20 L22 -16Z", shadow=False)
        d.shape("hero2", circle(-2, -42, 7))
        d.shape("light", "M1 -46 Q7 -44 7 -40 L2 -40Z", shadow=False)
    group(d, "translate(100 126) rotate(-12)", climber)


CONCEPTS = [
    Concept("hike-boot-signpost", "hiking", "Boot & signpost", hike_boot, checks=[("hero", "ground"), ("hero", "mid"), ("hero2", "far"), ("hero2", "sky")],
            fixes={"hero": ["deep", "pop", "near"]}),
    Concept("hike-backpack", "hiking", "Backpack", hike_backpack, checks=[("hero", "mid"), ("hero", "far"), ("hero2", "sky")],
            fixes={"hero": ["pop", "deep", "near"]}),
    Concept("hike-trail", "hiking", "Mountain trail", hike_trail, checks=[("ground", "near"), ("hero2", "ground"), ("deep", "near")],
            fixes={"ground": ["light", "glow2"]}),
    Concept("trek-tent", "trekking", "Base camp", trek_tent, checks=[("hero", "mid"), ("hero", "ground"), ("hero", "far")],
            fixes={"hero": ["pop", "deep", "near"]}),
    Concept("trek-llama", "trekking", "Pack llama", trek_llama, overrides={"hero": "#C8935F"}, checks=[("hero", "near"), ("hero", "mid"), ("hero", "far"), ("hero", "ground")],
            fixes={"near": ["deep", "far"], "far": ["sky2", "glow2"]}),
    Concept("trek-bridge", "trekking", "Rope bridge", trek_bridge, checks=[("hero", "mid"), ("near", "mid"), ("hero", "sky")],
            fixes={"hero": ["dark", "deep", "pop"]}),
    Concept("summit-flag", "summit-climb", "Summit flag", summit_flag, checks=[("mid", "sky"), ("pop", "sky"), ("light", "mid")],
            fixes={"mid": ["near", "deep"]}),
    Concept("summit-ice-axe", "summit-climb", "Ice axe", summit_axe, checks=[("hero", "light"), ("mark", "light"), ("pop", "light")],
            fixes={"hero": ["pop", "deep"]}),
    Concept("summit-climber", "summit-climb", "Roped climber", summit_climber, checks=[("hero2", "light"), ("hero2", "mid"), ("mid", "sky")],
            fixes={"hero2": ["pop", "hero", "deep"], "mid": ["near", "deep"]}),
]
