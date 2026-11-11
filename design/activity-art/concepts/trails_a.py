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


def clipped(d: Drawing, fn):
    """Line style doesn't clip shapes to the circle; wrap big ground shapes in this."""
    d.raw("", '<g clip-path="url(#clip)">')
    fn()
    d.raw("", "</g>")


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
    if rack:
        d.limb("dark", f"M{rx} {y} L{rx+6} {y-34} M{rx-16} {y-33} L{rx+22} {y-35}", 2.4)
    d.limb(frame, f"M{rx} {y} L{bb[0]} {bb[1]} L{seat[0]+1} {seat[1]+4} Z M{bb[0]} {bb[1]} L{head[0]} {head[1]+6} "
                  f"L{seat[0]+1} {seat[1]+4} L{seat[0]} {seat[1]} M{head[0]} {head[1]} L{fx} {y}", 5, spot=True)
    d.limb("dark", f"M{seat[0]-8} {seat[1]-1} L{seat[0]+6} {seat[1]-3}", 4)
    d.limb("dark", f"M{head[0]} {head[1]} L{head[0]-3} {head[1]-8} L{head[0]+8} {head[1]-10}", 3.6)
    d.stroke("dark", f"M{bb[0]} {bb[1]} L{bb[0]+7} {bb[1]+8}", 2.6)
    d.marks("dark", circle(bb[0], bb[1], 5))


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
    group(d, "translate(34 40) scale(.78)", boot)


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
    clipped(d, lambda: d.shape("ground", "M80 210 C100 180 150 176 140 156 C132 142 96 146 100 130 C102 122 112 120 118 118 "
                      "L122 119 C116 122 108 126 110 131 C114 140 150 140 156 156 C164 182 130 192 128 210Z"))
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
    d.shape("far", "M98 132 Q92 150 100 166 Q108 186 92 210 L124 210 Q118 186 110 166 Q102 150 102 132Z", shadow=False, line=False)
    # cliffs
    clipped(d, lambda: (d.shape("near", "M-30 104 L36 104 Q42 118 38 140 Q46 168 40 230 L-30 230Z"),
                        d.shape("near", "M230 104 L164 104 Q158 118 162 140 Q154 168 160 230 L230 230Z")))
    d.shape("deep", "M-30 104 L36 104 L37 110 L-30 110Z", shadow=False, line=False)
    d.shape("deep", "M230 104 L164 104 L163 110 L230 110Z", shadow=False, line=False)
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
    clipped(d, lambda: (d.shape("mid", "M20 230 L100 66 L180 230Z"),
                        d.shape("near", "M100 66 L180 230 L118 230 L112 150 L120 120 Z", shadow=False, line=False)))
    d.shape("light", "M100 66 L120 106 L110 100 L102 110 L94 98 L84 104 L80 106Z", shadow=False)
    d.shape("dark", rrect(98.6, 30, 2.8, 40, 1))
    d.shape("pop", "M101.5 31 L132 38 L101.5 46Z", spot=True)
    clipped(d, lambda: (d.shape("light", cloud(10, 158, 1.5)), d.shape("light", cloud(132, 166, 1.4)),
                        d.shape("light", cloud(60, 178, 1.6))))


def summit_axe(d: Drawing):
    d.disc("glow", 140, 58, 20)
    d.band("far", "M-30 108 L28 74 L60 96 L102 58 L140 92 L172 72 L230 104")
    for snow in ["M102 58 L114 70 L108 69 L102 74 L96 68 L90 70Z", "M28 74 L36 81 L31 80 L27 84 L23 79 L20 80Z",
                 "M172 72 L181 80 L176 79 L172 83 L168 79 L164 80Z"]:
        d.shape("light", snow, shadow=False)
    d.band("mid", hills(124, 8, 10))
    d.band("light", "M-30 150 Q60 126 120 140 T230 128")
    # rope coil lying in the snow
    for k, (cx, cy) in enumerate([(48, 154), (58, 156), (68, 154)]):
        d.stroke("pop", ellipse(cx, cy, 20, 9), 3.6, shadow=True)
    d.stroke("pop", "M86 158 Q104 172 128 166", 3.6)
    # ice axe planted in the slope, pick at the top
    d.limb("hero", "M124 160 L136 70", 8, spot=True)
    d.shape("dark", "M124.4 146 L134.2 147.4 L132.4 160.6 L122.6 159.2Z", shadow=False)
    d.shape("mark", "M132 60 L144 61 Q162 66 174 86 Q174 90 170 89 Q160 78 150 74 L148 77 L145 73 L142 76 L140 72 L132 71Z")
    d.shape("mark", "M134 60 L110 57 Q106 57 106 61 L106 70 Q106 74 110 73 L134 71Z")
    d.shape("mark", rrect(130, 56, 12, 20, 3))
    d.shape("light", "M118 160 Q130 150 142 160 Q130 164 118 160Z", shadow=False)
    d.band("light", "M-30 170 Q80 152 140 160 T230 154")
    d.stroke("far", "M100 168 Q120 162 140 166 M30 176 Q48 170 64 176", 2, line=False)


def summit_climber(d: Drawing):
    d.disc("glow", 150, 58, 22)
    d.band("far", "M-30 118 L20 96 L54 110 L230 140")
    # ridge to the summit, going up to the right
    clipped(d, lambda: (d.shape("mid", "M-30 230 L-30 176 L60 150 L150 72 L172 86 L230 120 L230 230Z"),
                        d.shape("light", "M-30 176 L60 150 L150 72 L172 86 L156 82 L118 108 L70 160 L-30 190Z", shadow=False)))
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



# ================================================================ ROCK CLIMBING
def blob(cx, cy, r, k=0) -> str:
    """An irregular rounded climbing hold."""
    import math
    pts = []
    for i in range(7):
        a = i / 7 * 2 * math.pi + k
        rr = r * (0.78 + 0.32 * math.sin(i * 2.3 + k * 3))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.8))
    s = ""
    for i in range(7):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % 7]
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        s += (f"M{mx:.1f} {my:.1f} " if i == 0 else "") + f"Q{x1:.1f} {y1:.1f} {(x1 + pts[(i + 2) % 7][0]) / 2:.1f} {(y1 + pts[(i + 2) % 7][1]) / 2:.1f} "
    return s + "Z"


def rock_holds(d: Drawing):
    d.shape("far", circle(100, 100, 96), shadow=False, line=False)
    d.stroke("mid", "M-10 70 L210 54 M-10 140 L210 128 M70 -10 L78 210 M146 -10 L152 210", 1.6, line=False)
    d.marks("mid", "".join(circle(x, y, 1.4) for x, y in [(40, 40), (110, 30), (30, 104), (122, 96), (60, 170), (170, 160), (176, 90), (100, 160), (46, 128)]))
    holds = [("hero", 56, 54, 17, 0.2, True), ("pop", 96, 84, 13, 1.1, False), ("hero2", 154, 50, 14, 2.0, False),
             ("mark", 38, 108, 12, 0.7, False), ("hero2", 82, 136, 18, 2.6, True), ("hero", 158, 118, 13, 1.6, False),
             ("pop", 48, 160, 12, 0.4, True), ("mark", 124, 172, 13, 2.9, False)]
    for role, x, y, r, k, sp in holds:
        d.shape(role, blob(x, y, r, k), spot=sp)
        d.marks("dark", circle(x + r * 0.15, y - r * 0.1, 1.5))
    d.marks("light", ellipse(92, 80, 5, 2.4) + ellipse(76, 130, 6, 3))
    # bolt hanger, quickdraw and rope
    d.shape("mark", circle(118, 30, 5.5))
    d.limb("mark", "M114 34 Q112 44 118 46 Q124 44 122 34", 3)
    d.shape("hero2", rrect(113, 44, 10, 26, 4), spot=True)
    d.limb("mark", "M118 68 Q108 72 110 84 Q114 94 122 92 Q130 88 128 76 Q126 70 118 68", 3.4)
    clipped(d, lambda: d.limb("pop", "M112 210 Q100 150 116 96 Q120 86 126 92 Q132 100 140 120 Q150 150 146 210", 6, spot=True))


def rock_cliff(d: Drawing):
    d.disc("glow", 52, 58, 18)
    d.band("far", "M-30 140 L10 140 L14 118 L46 116 L50 140 L180 142 L184 124 L206 124 L210 142 L230 142")
    d.band("ground", hills(170, 6))

    def tower():
        d.shape("near", "M86 230 L88 150 Q80 120 92 96 L98 64 Q100 44 116 40 L146 42 Q160 46 160 64 L164 120 Q172 160 172 230Z")
        d.shape("deep", "M146 42 Q160 46 160 64 L164 120 Q172 160 172 230 L150 230 Q150 170 148 120 Q146 80 146 42Z", shadow=False, line=False)
        d.stroke("deep", "M118 60 Q122 90 116 120 M128 140 Q132 170 126 200", 2.2, line=False)
    clipped(d, tower)
    # rope from top anchor down to the climber's harness and on to the ground
    d.marks("dark", circle(110, 44, 3))
    clipped(d, lambda: d.stroke("pop", "M110 44 Q102 80 92 112 M92 118 Q72 150 76 210", 2.4))

    def climber():
        d.limb("mark", "M0 0 L10 12 L6 24 M0 0 L-2 14 L8 30", 6)
        d.limb("hero2", "M0 -26 L0 0", 12)
        d.shape("hero", rrect(-12, -26, 7, 18, 3), shadow=False, spot=True)
        d.limb("hero2", "M2 -22 L10 -36 M2 -14 L12 -10", 5)
        d.shape("hero", circle(0, -34, 7))
        d.shape("light", "M-6 -33 a6 6 0 0 1 12 0Z", shadow=False)
    group(d, "translate(90 116)", climber)
    d.band("deep", "M-30 188 Q100 182 230 190", line=False)


def rock_carabiner(d: Drawing):
    d.disc("glow", 150, 56, 20)
    d.band("far", hills(110, 12, 30))
    d.band("mid", "M-30 150 L30 140 L60 152 L120 136 L170 148 L230 138")
    d.band("near", hills(178, 6))
    # bolt hanger on the rock, carabiner hanging from it, rope running through
    d.shape("mark", circle(100, 34, 7))
    d.limb("mark", "M94 38 Q92 50 100 54 Q108 50 106 38", 4)

    def biner():
        d.limb("hero", "M-12 -40 Q-26 -40 -26 -26 L-22 34 Q-20 48 -6 48 L10 44 Q24 40 24 26 L26 -26 Q26 -40 10 -40Z", 10, spot=True)
        d.limb("mark", "M-26 -22 L-23 26", 5, shadow=False)
        d.limb("light", "M-4 -35 L14 -35.5", 2.4, shadow=False)
    group(d, "translate(100 96) rotate(8)", biner)
    clipped(d, lambda: d.limb("pop", "M72 210 Q74 166 88 150 Q98 138 108 148 Q120 162 124 210", 8, spot=True))
    d.stroke("dark", "M76 186 l6 -1 M78 168 l6 1 M118 170 l6 -1 M121 190 l6 0", 1.4, line=False)


# ================================================================ CAVING
STALACTITES = ("M-30 -30 H230 V36 L206 40 L198 74 L190 44 L176 50 L168 92 L160 52 L146 46 L138 66 L130 44 "
               "L112 40 L104 58 L98 40 L80 44 L72 84 L64 46 L50 50 L42 70 L34 44 L-30 46Z")


def cave_floor(d: Drawing, y=158):
    d.shape("near", f"M-30 230 L-30 {y} L20 {y-4} L30 {y-30} L40 {y-6} L150 {y-2} L160 {y-38} L172 {y-4} L230 {y} L230 230Z")


def cave_headtorch(d: Drawing):
    d.shape("deep", circle(100, 100, 96), shadow=False, line=False)
    clipped(d, lambda: (d.shape("near", STALACTITES), cave_floor(d, 160)))
    beam = "M140 118 L210 80 L210 160Z"
    if d.paper:
        d.raw(f'<path clip-path="url(#clip)" d="{beam}" fill="{d.c["glow2"]}" opacity=".5"/>')
    else:
        d.raw("", f'<path clip-path="url(#clip)" d="{beam}" fill="{d.c["spot"]}" opacity=".35"/>')
    # helmet resting on the cave floor, lamp facing right
    d.shape("hero", "M52 150 Q50 104 94 102 Q136 104 138 150Z", spot=True)
    d.shape("light", "M62 132 Q64 114 84 110 Q70 118 68 132Z", shadow=False, line=False)
    d.shape("dark", rrect(44, 146, 104, 9, 4.5))
    d.stroke("mark", "M94 102 V150", 2.2, line=False)
    d.shape("dark", rrect(122, 108, 16, 22, 5))
    d.disc("glow2", 139, 119, 7)
    d.shape("light", circle(140, 119, 3.4), shadow=False, line=False)


def bat(x, y, s=1.0) -> str:
    pts = [(0, -3), (2, -6), (3, -2), (8, -6), (14, -6), (12, -2), (13, 2), (9, 0), (7, 3), (4, 1), (2, 4), (0, 6),
           (-2, 4), (-4, 1), (-7, 3), (-9, 0), (-13, 2), (-12, -2), (-14, -6), (-8, -6), (-3, -2), (-2, -6)]
    return "M" + " L".join(f"{x + px * s:.1f} {y + py * s:.1f}" for px, py in pts) + "Z"


def cave_bats(d: Drawing):
    d.disc("glow", 104, 110, 24)
    d.band("far", hills(132, 10))
    d.band("mid", hills(150, 8, 20))
    frame = ("M-30 -30 H230 V230 H-30Z M40 170 Q30 120 44 86 L52 92 L58 70 Q76 46 100 44 L106 62 L112 44 "
             "Q140 50 152 74 L158 92 L162 80 Q176 120 164 170Z")
    clipped(d, lambda: d.shape("near", frame, extra='fill-rule="evenodd"'))
    d.band("deep", "M-30 172 Q100 160 230 172")
    for x, y, s in [(100, 82, 1.7), (72, 104, 1.1), (130, 96, 1.25), (118, 66, 0.9), (84, 70, 0.8), (146, 126, 0.8)]:
        d.shape("dark", bat(x, y, s), shadow=False)
    d.stroke("dark", "M52 92 Q48 110 52 120", 1.2, line=False)


def cave_pool(d: Drawing):
    d.shape("deep", circle(100, 100, 96), shadow=False, line=False)
    clipped(d, lambda: d.shape("near", STALACTITES))
    d.marks("light", ellipse(72, 98, 1.6, 2.4) + ellipse(130, 112, 1.6, 2.4) + ellipse(168, 104, 1.4, 2.2))
    d.band("mid", "M-30 138 Q100 128 230 138")
    for x, y, h in [(150, 138, 40), (166, 138, 22), (32, 140, 24)]:
        d.shape("mid", f"M{x-10} {y} Q{x-3} {y-h*0.4} {x} {y-h} Q{x+3} {y-h*0.4} {x+10} {y}Z")
    d.shape("hero", ellipse(104, 166, 80, 22), spot=True)
    d.shape("far", "M140 146 L150 172 L160 146Z M158 146 L166 160 L174 146Z", shadow=False, line=False)
    d.stroke("light", "M54 160 H82 M96 170 H128 M70 178 H90 M126 156 H138", 2, line=False)
    d.stroke("light", ellipse(130, 160, 6, 1.8), 1.2, line=False)
    # lantern on a rock ledge
    if d.paper:
        d.raw(f'<circle cx="74" cy="128" r="20" fill="{d.c["glow2"]}" opacity=".3"/>')
    d.shape("near", "M50 150 Q52 138 74 138 Q96 138 98 150Z")
    d.limb("dark", "M68 114 Q74 104 80 114", 2.2, shadow=False)
    d.shape("dark", rrect(64, 114, 20, 5, 2))
    d.shape("pop", rrect(65.5, 119, 17, 16, 3), spot=True)
    d.shape("glow2", rrect(69.5, 122, 9, 10, 2.5), shadow=False)
    d.shape("dark", rrect(64, 134, 20, 5, 2))


# ================================================================ SANDBOARDING
def dunes(d: Drawing, sun=(140, 62, 22)):
    d.disc("glow", *sun)
    d.band("far", "M-30 120 Q30 104 70 112 Q110 96 150 104 Q190 92 230 106")
    d.band("mid", "M-30 146 Q40 116 92 126 Q140 136 230 124")
    d.shape("near", "M92 126 Q140 136 230 124 L230 140 Q160 150 92 126Z", shadow=False, line=False)


def sand_board(d: Drawing):
    dunes(d, (56, 60, 20))

    def board():
        d.shape("hero", rrect(-15, -58, 30, 116, 15), spot=True)
        d.shape("hero2", "M-15 -20 H15 V-12 H-15Z M-15 -4 H15 V2 H-15Z", shadow=False)
        d.shape("dark", rrect(-12, -40, 24, 7, 3))
        d.shape("dark", rrect(-12, 20, 24, 7, 3))
        d.marks("light", rrect(-9, -52, 4, 10, 2))
    group(d, "translate(108 98) rotate(10)", board)
    d.band("ground", "M-30 156 Q40 140 100 146 Q150 152 230 140")
    d.marks("near", "".join(ellipse(x, y, 3, 1.4) for x, y in [(40, 168), (52, 164), (64, 170), (76, 166), (154, 160), (166, 156)]))
    d.band("deep", "M-30 188 Q100 178 230 186", line=False)


def sand_rider(d: Drawing):
    d.disc("glow", 150, 52, 18)
    d.band("far", "M-30 96 Q40 86 90 92 T230 86")
    d.band("ground", "M-30 52 Q20 56 60 84 Q110 120 160 136 Q200 148 230 150")
    d.shape("near", "M-30 52 Q20 56 60 84 Q110 120 160 136 Q200 148 230 150 L230 168 Q170 160 120 140 Q60 112 -30 70Z", shadow=False, line=False)
    # sand spray behind
    d.marks("glow2", "".join(circle(x, y, r) for x, y, r in [(52, 92, 4), (44, 84, 3), (58, 82, 2.5), (38, 94, 2), (48, 74, 2)]))

    def rider():
        d.shape("hero", rrect(-34, -4, 68, 9, 4.5), spot=True)
        d.limb("mark", "M-14 -2 L-4 -14 L-2 -26 M12 -2 L10 -14 L2 -26", 6.5)
        d.limb("hero2", "M0 -26 L-6 -48", 12)
        d.limb("hero2", "M-4 -46 L-24 -36 M-2 -46 L20 -42", 4.5)
        d.shape("dark", circle(-8, -58, 7))
        d.shape("pop", "M-15 -59 a7 7 0 0 1 14 0Z", shadow=False)
    group(d, "translate(98 104) rotate(28)", rider)
    d.band("deep", "M-30 182 Q100 172 230 184", line=False)


def sand_tracks(d: Drawing):
    d.disc("glow", 50, 54, 18)
    d.band("far", "M-30 110 Q40 92 80 100 T230 96")
    d.band("ground", "M-30 160 Q20 150 60 110 Q90 70 110 60 Q160 90 230 120")
    d.shape("mid", "M110 60 Q160 90 230 120 L230 230 L120 230 Q140 140 110 60Z", shadow=False, line=False)
    d.stroke("near", "M106 66 Q86 84 104 98 Q124 112 96 128 Q70 142 98 158", 2.4)
    d.stroke("near", "M112 66 Q92 84 110 98 Q130 112 102 128 Q76 142 104 158", 1.4, line=False)
    # small rider at the bottom of the tracks
    def rider():
        d.shape("hero", rrect(-16, -2, 32, 5, 2.5), spot=True)
        d.limb("mark", "M-5 -1 L-6 -10 L0 -16 M5 -1 L6 -10 L0 -16", 3.4)
        d.limb("hero2", "M0 -16 L0 -28", 6)
        d.limb("hero2", "M0 -26 L-10 -22 M0 -26 L10 -30", 2.6)
        d.shape("mark", circle(0, -33, 4))
    group(d, "translate(98 172) rotate(-6) scale(1.35)", rider)
    # palm in the corner
    d.limb("dark", "M162 172 Q166 140 158 116", 4.5)
    for leaf in ["M158 116 Q140 100 122 110 Q142 108 158 118Z", "M158 116 Q150 96 132 92 Q152 100 157 117Z",
                 "M158 116 Q170 94 188 98 Q170 104 159 118Z", "M158 116 Q178 108 190 124 Q174 116 158 118Z"]:
        d.shape("deep", leaf, shadow=False)
    d.marks("dark", circle(158, 118, 3))
    d.band("deep", "M-30 186 Q100 176 230 186", line=False)


# ================================================================ DUNE BASHING
SUV = ("M36 134 L38 112 Q40 106 48 104 L64 102 L76 80 Q78 76 84 76 L132 76 Q138 76 140 80 L152 102 L162 104 "
       "Q168 106 168 112 L168 134Z")


def suv(d: Drawing, body="hero"):
    d.shape("dark", rrect(80, 70, 56, 6, 2))
    d.stroke("dark", "M86 76 V70 M130 76 V70", 2)
    d.shape(body, SUV, spot=True)
    d.shape("light", "M80 82 H104 V102 H69Z", shadow=False)
    d.shape("light", "M110 82 H134 L145 102 H110Z", shadow=False)
    d.stroke("dark", "M107 78 V132 M112 110 H118", 1.6, line=False)
    d.shape("hero2", "M38 118 H168 V123 H38Z", shadow=False)
    d.shape("glow2", rrect(162, 108, 6, 6, 2), shadow=False)
    d.shape("dark", rrect(30, 128, 12, 6, 2))
    for x in (66, 140):
        d.shape("dark", circle(x, 136, 16))
        d.shape("light", circle(x, 136, 6), shadow=False)


def dune_4x4(d: Drawing):
    d.disc("glow", 52, 58, 20)
    d.band("far", "M-30 112 Q40 92 100 104 T230 100")
    d.band("ground", "M-30 168 Q40 150 90 128 Q120 116 150 124 Q190 136 230 150")
    d.shape("mid", "M90 128 Q120 116 150 124 Q190 136 230 150 L230 230 L160 230 Q150 170 90 128Z", shadow=False, line=False)
    # sand spray from the rear wheel
    d.marks("glow2", "".join(circle(x, y, r) for x, y, r in [(46, 116, 7), (34, 104, 5), (56, 100, 4), (26, 122, 4), (40, 88, 3), (22, 96, 2.5)]))
    group(d, "translate(108 100) rotate(-14) scale(.78) translate(-100 -120)", lambda: suv(d))
    d.band("deep", "M-30 186 Q100 176 230 186", line=False)


CAMEL = ("M152 108 Q154 122 142 124 L140 160 L134 160 L131 126 L122 126 L121 160 L115 160 L112 124 L94 122 "
         "L90 160 L84 160 L82 122 L76 120 L75 160 L69 160 L68 116 Q62 112 58 104 L48 82 Q46 76 40 76 L30 76 "
         "Q24 76 24 70 Q26 64 32 64 L44 62 Q54 62 58 72 L70 96 Q76 88 88 86 Q102 58 118 66 Q128 72 134 90 "
         "Q150 94 152 108Z")


def dune_camel(d: Drawing):
    d.disc("glow", 150, 60, 20)
    d.band("far", "M-30 108 Q40 92 100 100 T230 96")
    d.band("mid", "M-30 132 Q60 112 120 118 Q170 124 230 116")
    group(d, "translate(150 98) scale(.36) translate(-100 -110)", lambda: suv(d, "pop"))
    d.marks("glow2", "".join(circle(x, y, r) for x, y, r in [(126, 108, 4), (120, 100, 3), (116, 110, 2.5)]))

    def camel():
        d.stroke("hero", "M150 106 Q160 116 156 132", 3)
        d.shape("hero", CAMEL)
        d.shape("pop", "M86 86 Q102 70 120 74 L124 92 Q104 98 86 96Z", spot=True)
        d.shape("hero2", "M88 92 Q104 86 122 88 L123 92 Q104 98 87 96Z", shadow=False)
        d.marks("mark", circle(34, 68, 1.6))
        d.stroke("pop", "M44 64 Q50 74 58 72", 1.6, line=False)
    group(d, "translate(-4 32) scale(.9)", camel)
    d.band("ground", "M-30 176 Q100 166 230 176")


def dune_convoy(d: Drawing):
    d.disc("glow", 100, 96, 44)
    d.band("far", "M-30 120 Q40 100 100 112 T230 104")
    d.band("mid", "M-30 150 Q30 128 80 118 Q120 110 160 126 Q200 140 230 136")
    for tx, ty, rot, sc, role in [(52, 108, -10, .3, "hero"), (98, 98, 0, .32, "pop"), (146, 108, 12, .3, "hero2")]:
        group(d, f"translate({tx} {ty}) rotate({rot}) scale({sc}) translate(-100 -140)", lambda role=role: suv(d, role))
    d.band("ground", "M-30 170 Q40 140 100 148 Q160 156 230 140")
    d.stroke("near", "M60 186 Q90 160 110 156 M70 190 Q98 166 120 160", 2, line=False)
    d.band("deep", "M-30 190 Q100 182 230 190", line=False)



# ================================================================ QUAD BIKING
def quad(d: Drawing, body="hero"):
    """Side-view quad bike facing right, wheels at (56,142) and (146,142)."""
    d.limb("dark", "M126 104 L122 86", 4)
    d.limb("dark", "M114 86 L130 84", 4)
    d.limb("dark", "M152 112 L168 104 L176 112", 3)
    d.shape("dark", "M70 116 L136 116 L128 134 L78 134Z")
    d.shape("dark", rrect(58, 98, 46, 11, 5.5))
    d.shape(body, "M28 126 Q30 104 56 102 Q78 104 86 116 L86 126Z", spot=True)
    d.shape(body, "M116 116 Q122 102 146 102 Q170 104 174 126 L116 126Z", spot=True)
    d.shape(body, "M88 118 Q92 104 112 103 L134 104 Q144 108 142 118Z")
    d.shape("hero2", "M28 120 H86 V126 H28Z M116 120 H174 V126 H116Z", shadow=False)
    d.shape("glow2", rrect(166, 108, 8, 7, 2.5), shadow=False)
    for x in (56, 146):
        d.shape("dark", circle(x, 142, 21))
        d.stroke("mark", circle(x, 142, 16), 1.6, line=False)
        d.shape("light", circle(x, 142, 7), shadow=False)
        d.marks("dark", circle(x, 142, 2.5))


def quad_trail(d: Drawing):
    d.disc("glow", 150, 56, 20)
    d.band("far", hills(104, 12, 20))
    for x, b, h in [(30, 128, 40), (48, 134, 30), (176, 130, 38)]:
        pine_tree(d, x, b, h)
    d.band("mid", hills(140, 8))
    d.band("ground", "M-30 160 Q100 148 230 160")
    # mud splats
    d.marks("near", "".join(circle(x, y, r) for x, y, r in [(26, 128, 4.5), (18, 116, 3), (34, 112, 2.5), (14, 136, 2.5)]))
    group(d, "translate(100 116) scale(.86) translate(-100 -120)", lambda: quad(d))
    d.shape("near", "M30 166 Q60 156 90 164 Q120 170 150 160 Q170 156 186 162 Q160 174 120 176 Q70 176 30 166Z", shadow=False, line=False)
    d.band("deep", "M-30 188 Q100 178 230 188", line=False)


HELMET = "M52 110 Q50 62 98 58 Q140 58 148 92 L152 118 Q154 140 140 148 L104 152 Q66 154 56 138 Q52 126 52 110Z"


def quad_helmet(d: Drawing):
    d.disc("glow", 52, 58, 20)
    d.band("far", hills(118, 12, -20))
    d.band("mid", hills(150, 10, 30))
    d.shape("light", cloud(150, 40, 0.8), shadow=False)
    d.shape("hero", HELMET, spot=True)
    d.shape("hero2", "M56 132 Q76 120 100 128 Q120 134 146 128 L144 142 Q120 150 100 150 Q70 152 58 140Z", shadow=False)
    d.shape("hero2", "M64 80 Q76 64 98 62 Q80 72 72 88Z", shadow=False, line=False)
    # goggles strapped round the dome, lens in the eye port
    d.limb("dark", "M112 104 Q82 96 54 102", 5, shadow=False)
    d.shape("dark", rrect(108, 92, 44, 26, 11))
    d.shape("pop", rrect(112, 96, 36, 18, 8), shadow=False, spot=True)
    d.shape("light", "M118 99 L126 99 L121 108 L116 108Z", shadow=False, line=False)
    # peak
    d.shape("mark", "M98 68 Q132 58 168 72 L163 83 Q134 74 108 80Z")
    d.stroke("dark", "M124 130 H140 M126 137 H138", 2, line=False)
    d.band("ground", "M-30 170 Q100 160 230 170")
    d.band("near", "M-30 186 Q100 176 230 186", line=False)


def quad_dust(d: Drawing):
    d.disc("glow", 56, 62, 22)
    d.band("far", "M-30 104 L20 84 L50 98 L90 74 L130 96 L170 80 L230 100")
    d.band("mid", hills(126, 10, 10))
    d.band("ground", "M-30 150 Q50 128 120 136 T230 134")
    d.stroke("mid", "M-10 170 Q60 150 110 152 Q150 154 200 140", 9, line=False)
    clipped(d, lambda: [d.shape("light", cloud(x, y, sc)) for x, y, sc in [(30, 132, 1.2), (8, 140, 1.0), (52, 128, 0.7)]])
    group(d, "translate(118 136) scale(.62) translate(-100 -120)", lambda: quad(d))
    d.band("near", "M-30 176 Q100 164 230 176")
    d.band("deep", "M-30 192 Q100 184 230 192", line=False)


# ================================================================ MOUNTAIN BIKING
def mtb_ridge(d: Drawing):
    d.disc("glow", 140, 58, 22)
    d.band("far", "M-30 108 L18 80 L50 98 L92 62 L130 92 L164 74 L230 104")
    for snow in ["M92 62 L104 73 L98 72 L92 77 L86 71 L80 73Z", "M164 74 L172 81 L167 80 L164 84 L160 80 L156 81Z"]:
        d.shape("light", snow, shadow=False)
    d.band("mid", hills(130, 10, -10))
    for x, b, h in [(26, 146, 44), (176, 140, 40), (190, 150, 30)]:
        pine_tree(d, x, b, h)
    d.band("ground", "M-30 170 Q60 152 120 160 T230 158")
    group(d, "translate(100 106) scale(.9) translate(-100 -120)", lambda: bicycle(d, tyre_w=6, r=21, knobbly=True))
    d.shape("near", "M26 172 Q28 160 40 158 Q52 156 58 166 L60 172Z M146 168 Q150 156 162 156 Q174 158 176 168Z")
    d.band("deep", "M-30 188 Q100 178 230 188", line=False)


def mtb_jump(d: Drawing):
    d.disc("glow", 60, 60, 20)
    d.band("far", hills(110, 12))
    for x, b, h in [(170, 130, 50), (150, 138, 36), (30, 136, 34)]:
        pine_tree(d, x, b, h)
    # dirt kicker the rider has just left
    d.band("ground", "M-30 170 Q20 168 40 150 Q50 142 58 150 L66 172 Q120 168 230 172")
    d.stroke("near", "M10 172 Q30 166 44 154", 2, line=False)

    def rider():
        bicycle(d, frame="hero", tyre_w=6, r=21, knobbly=True)
        d.limb("mark", "M86 98 L104 118 L96 140 M86 98 L94 124 L88 140", 7)
        d.limb("hero2", "M86 98 L112 76", 13, spot=False)
        d.limb("hero2", "M112 78 L130 96", 5)
        d.shape("hero2", circle(122, 64, 9))
        d.shape("mark", "M112 62 Q114 52 126 54 Q134 56 134 64 L138 64 L136 68 L112 66Z", shadow=False)
    group(d, "translate(106 92) rotate(-14) scale(.88) translate(-100 -110)", rider)
    d.band("deep", "M-30 188 Q100 178 230 188", line=False)


def mtb_sign(d: Drawing):
    d.disc("glow", 56, 56, 18)
    d.band("far", hills(98, 12, 20))
    for x, b, h in [(28, 130, 48), (50, 124, 38), (176, 124, 56), (154, 132, 40), (186, 140, 30)]:
        pine_tree(d, x, b, h, "deep")
    d.band("mid", "M-30 140 Q100 128 230 140")
    # berm track sweeping through
    clipped(d, lambda: d.shape("ground", "M-30 178 Q60 150 120 150 Q170 150 190 140 L230 140 L230 152 Q180 168 120 168 Q70 170 -30 200Z"))
    # trail sign
    d.shape("dark", rrect(96, 74, 8, 96, 2))
    d.shape("light", rrect(72, 50, 56, 50, 7))
    d.shape("dark", "M100 58 L114 75 L100 92 L86 75Z", spot=True)
    d.shape("hero", "M60 112 H126 L138 121 L126 130 H60Z", spot=True)
    d.marks("light", "M70 119 H112 V123 H70Z M108 115 L118 121 L108 127Z")
    d.band("near", "M-30 182 Q100 172 230 182")


# ================================================================ CYCLING TOUR
def tour_fence(d: Drawing):
    d.disc("glow", 140, 56, 22)
    d.band("far", hills(104, 12, 20))
    d.band("mid", hills(124, 10, -20))
    # lavender rows
    for y in (132, 140, 148):
        d.stroke("hero2", f"M-30 {y+6} Q100 {y-4} 230 {y+6}", 3, line=False)
    d.band("ground", "M-30 162 Q100 154 230 162")
    # fence behind the bike
    for x in (34, 100, 166):
        d.shape("dark", rrect(x - 3, 98, 6, 66, 2))
    d.shape("near", "M20 104 L180 101 L180 108 L20 111Z")
    d.shape("near", "M20 126 L180 123 L180 130 L20 133Z")

    def bike():
        bicycle(d, frame="hero", tyre_w=4.5, r=23, rack=True)
        d.shape("pop", rrect(36, 102, 30, 32, 7), spot=True)
        d.shape("pop", rrect(60, 106, 14, 26, 5))
        d.stroke("dark", "M40 112 H62", 1.6, line=False)
        d.shape("hero2", rrect(122, 86, 16, 12, 3))
    group(d, "translate(100 108) scale(.92) translate(-100 -120)", bike)
    d.band("deep", "M-30 190 Q100 180 230 190", line=False)


def tour_pass(d: Drawing):
    d.disc("glow", 150, 50, 18)
    d.band("far", "M-30 96 L30 64 L66 86 L104 46 L146 82 L180 64 L230 92")
    for snow in ["M104 46 L116 57 L110 56 L104 61 L98 55 L92 57Z", "M30 64 L38 71 L33 70 L29 74 L25 69 L22 70Z"]:
        d.shape("light", snow, shadow=False)
    d.band("mid", "M-30 112 Q40 92 100 96 Q160 100 230 92")
    # switchback road
    road = "M98 98 L140 108 L60 120 L150 134 L44 150 L170 172 L120 230"
    clipped(d, lambda: d.stroke("light", road, 9, shadow=True))
    d.raw(f'<path d="{road}" fill="none" stroke="{d.c["mark"]}" stroke-width="1" stroke-dasharray="3 4" opacity=".6"/>' if d.paper else "")
    # pass sign
    d.shape("dark", rrect(70, 82, 3, 18, 1))
    d.shape("hero2", rrect(58, 72, 28, 12, 2), spot=True)
    d.stroke("dark", "M63 78 H81", 1.6, line=False)
    # rider on the switchback
    def rider():
        bicycle(d, frame="pop", tyre_w=5, r=22)
        d.limb("mark", "M86 96 L104 122 L96 142 M86 96 L94 128 L90 140", 8)
        d.limb("hero", "M86 98 L114 74", 14)
        d.limb("hero", "M114 76 L130 96", 6)
        d.shape("hero", circle(122, 60, 10))
        d.shape("hero2", "M110 58 Q114 46 126 48 Q134 50 134 58 L112 60Z", shadow=False)
    group(d, "translate(106 138) scale(.36) translate(-100 -130)", rider)
    d.band("near", "M-30 186 Q100 176 230 186", line=False)


def tour_handlebar(d: Drawing):
    d.disc("glow", 100, 70, 20)
    d.band("far", hills(92, 10, 10))
    d.band("mid", "M-30 112 Q60 96 100 104 Q150 112 230 100")
    clipped(d, lambda: (d.shape("ground", "M96 104 L104 104 Q140 160 168 230 L32 230 Q64 160 96 104Z"),
                        d.stroke("light", "M100 112 V124 M100 136 V152 M100 168 V190", 2.6, line=False)))
    for x, b, h in [(26, 120, 30), (174, 118, 34), (156, 112, 22)]:
        pine_tree(d, x, b, h)
    # handlebar, stem and bar bag
    clipped(d, lambda: (d.limb("dark", "M10 156 Q30 146 60 150 Q100 154 140 150 Q170 146 190 156", 8),
                        d.limb("hero2", "M12 156 Q20 152 30 151 M170 151 Q180 152 188 156", 11, spot=True)))
    d.shape("hero", rrect(70, 140, 60, 40, 8))
    d.shape("light", rrect(76, 132, 48, 30, 4))
    d.stroke("pop", "M82 154 Q92 140 102 148 Q110 154 118 138", 2)
    d.marks("pop", circle(118, 138, 2.6))
    d.marks("dark", circle(82, 154, 2))
    d.stroke("far", "M78 142 Q88 136 96 140 M104 156 Q112 150 122 154", 1, line=False)
    # bell
    d.shape("glow2", "M146 140 Q146 128 154 128 Q162 128 162 140Z", spot=True)
    d.shape("dark", rrect(144, 139, 20, 4, 2))


CONCEPTS = [
    Concept("hike-boot-signpost", "hiking", "Boot & signpost", hike_boot, checks=[("hero", "ground"), ("hero", "mid"), ("hero2", "far"), ("hero2", "sky")],
            fixes={"hero": ["deep", "pop", "near"], "hero2": ["pop", "glow2"]}),
    Concept("hike-backpack", "hiking", "Backpack", hike_backpack, checks=[("hero", "mid"), ("hero", "far"), ("hero2", "sky")],
            fixes={"hero": ["pop", "deep", "near"], "hero2": ["glow2", "pop"]}),
    Concept("hike-trail", "hiking", "Mountain trail", hike_trail, checks=[("ground", "near"), ("hero2", "ground"), ("deep", "near")],
            fixes={"ground": ["light", "glow2"], "deep": ["dark"]}),
    Concept("trek-tent", "trekking", "Base camp", trek_tent, checks=[("hero", "mid"), ("hero", "ground"), ("hero", "far")],
            fixes={"hero": ["pop", "deep", "near"]}),
    Concept("trek-llama", "trekking", "Pack llama", trek_llama, overrides={"hero": "#C8935F"}, checks=[("hero", "near"), ("hero", "mid"), ("hero", "far"), ("hero", "ground")],
            fixes={"near": ["deep", "far"], "far": ["sky2", "glow2"], "mid": ["far", "near", "deep"], "ground": ["far", "light"]}),
    Concept("trek-bridge", "trekking", "Rope bridge", trek_bridge, checks=[("hero", "mid"), ("near", "mid"), ("hero", "sky")],
            fixes={"hero": ["dark", "deep", "pop"], "near": ["deep"]}),
    Concept("summit-flag", "summit-climb", "Summit flag", summit_flag, checks=[("mid", "sky"), ("pop", "sky"), ("light", "mid")],
            fixes={"mid": ["near", "deep"]}),
    Concept("summit-ice-axe", "summit-climb", "Ice axe", summit_axe, checks=[("hero", "light"), ("mark", "light"), ("pop", "light")],
            fixes={"hero": ["pop", "deep"]}),
    Concept("summit-climber", "summit-climb", "Roped climber", summit_climber, checks=[("hero2", "light"), ("hero2", "mid"), ("mid", "sky")],
            fixes={"hero2": ["pop", "hero", "deep"], "mid": ["near", "deep"]}),
    Concept("rock-holds", "rock-climbing", "Climbing wall", rock_holds, checks=[("hero", "far"), ("hero2", "far"), ("pop", "far"), ("mark", "far")],
            fixes={"far": ["light", "sky", "ground"]}),
    Concept("rock-cliff", "rock-climbing", "Desert tower", rock_cliff, checks=[("near", "sky"), ("hero2", "near"), ("pop", "near")],
            fixes={"hero2": ["light", "glow2"], "pop": ["light", "hero2"], "near": ["mid", "far"]}),
    Concept("rock-carabiner", "rock-climbing", "Carabiner & rope", rock_carabiner, overrides={"hero": "#9AA5B4"},
            checks=[("hero", "sky"), ("pop", "hero"), ("hero", "far"), ("mark", "near")], fixes={"hero": ["#6C7A8C", "#C9CED6"], "mark": ["dark", "light"]}),
    Concept("cave-headtorch", "caving", "Headtorch", cave_headtorch, checks=[("hero", "deep"), ("hero", "near"), ("near", "deep")],
            fixes={"near": ["mid", "far"], "hero": ["hero2", "pop"]}),
    Concept("cave-bats", "caving", "Bats at dusk", cave_bats, checks=[("dark", "sky"), ("dark", "glow"), ("near", "far"), ("dark", "far")],
            fixes={"near": ["deep", "dark"], "sky": ["sky2", "far", "mid"], "dark": ["mark", "#000000"]}),
    Concept("cave-pool", "caving", "Underground pool", cave_pool, overrides={"hero": "#3FA7C4"}, checks=[("near", "deep"), ("hero", "mid"), ("mid", "deep")],
            fixes={"near": ["mid", "far"], "mid": ["far"]}),
    Concept("sand-board", "sandboarding", "Board in the dunes", sand_board, checks=[("hero", "mid"), ("hero", "far"), ("hero", "ground")],
            fixes={"hero": ["pop", "deep"]}),
    Concept("sand-rider", "sandboarding", "Dune rider", sand_rider, checks=[("hero2", "ground"), ("hero2", "sky"), ("ground", "sky")],
            fixes={"hero2": ["pop", "hero"], "ground": ["glow2", "mid"]}),
    Concept("sand-tracks", "sandboarding", "Tracks down the dune", sand_tracks, checks=[("ground", "sky"), ("near", "ground"), ("hero2", "mid")],
            fixes={"ground": ["glow2", "far"], "hero2": ["pop", "hero"]}),
    Concept("dune-4x4", "dune-bashing", "Over the crest", dune_4x4, checks=[("hero", "ground"), ("hero", "sky"), ("glow2", "ground")],
            fixes={"hero": ["pop", "deep"], "glow2": ["light", "far", "near"]}),
    Concept("dune-camel", "dune-bashing", "Camel & 4x4", dune_camel, overrides={"hero": "#C8935F"}, checks=[("hero", "mid"), ("hero", "far"), ("hero", "ground"), ("hero", "sky")],
            fixes={"mid": ["near", "deep", "far"], "far": ["sky2", "glow2"], "ground": ["far", "light"]}),
    Concept("dune-convoy", "dune-bashing", "Sunset convoy", dune_convoy, checks=[("hero", "mid"), ("pop", "mid"), ("hero2", "mid"), ("hero2", "glow")],
            fixes={"glow": ["glow2", "light", "far"], "mid": ["near", "deep"]}),
    Concept("quad-trail", "quad-biking", "Muddy trail", quad_trail, checks=[("hero", "mid"), ("hero", "ground"), ("dark", "ground"), ("hero", "far")],
            fixes={"hero": ["pop", "deep"]}),
    Concept("quad-helmet", "quad-biking", "Helmet & goggles", quad_helmet, checks=[("hero", "mid"), ("hero", "far"), ("hero", "sky"), ("mark", "hero"), ("pop", "dark")],
            fixes={"hero": ["pop", "deep"], "mark": ["dark", "light"]}),
    Concept("quad-dust", "quad-biking", "Dusty track", quad_dust, checks=[("hero", "ground"), ("light", "ground"), ("hero", "mid")],
            fixes={"hero": ["pop", "deep"], "light": ["far", "mid"]}),
    Concept("mtb-ridge", "mountain-biking", "Bike on the ridge", mtb_ridge, checks=[("hero", "mid"), ("hero", "far"), ("dark", "mid"), ("hero", "ground")],
            fixes={"hero": ["pop", "deep"]}),
    Concept("mtb-jump", "mountain-biking", "Big air", mtb_jump, checks=[("hero", "far"), ("hero", "sky"), ("hero2", "sky"), ("hero2", "far"), ("dark", "far")],
            fixes={"hero2": ["pop", "deep"], "hero": ["deep", "pop"]}),
    Concept("mtb-sign", "mountain-biking", "Trail marker", mtb_sign, checks=[("light", "deep"), ("hero", "light"), ("hero", "deep"), ("ground", "mid")],
            fixes={"hero": ["pop", "near"], "ground": ["light", "glow2"]}),
    Concept("tour-bike-fence", "cycling-tour", "Bike by the fence", tour_fence, checks=[("hero", "mid"), ("pop", "mid"), ("hero", "near"), ("near", "mid")],
            fixes={"hero": ["deep", "pop"], "near": ["deep", "dark"], "pop": ["deep", "hero2", "dark"]}),
    Concept("tour-pass", "cycling-tour", "Mountain pass", tour_pass, checks=[("light", "mid"), ("hero", "mid"), ("mid", "far")],
            fixes={"mid": ["near", "deep"], "hero": ["pop", "deep"]}),
    Concept("tour-handlebar", "cycling-tour", "Open road", tour_handlebar, checks=[("hero", "ground"), ("light", "ground"), ("ground", "mid"), ("dark", "ground")],
            fixes={"ground": ["near", "deep"], "hero": ["pop", "deep"]}),
]
