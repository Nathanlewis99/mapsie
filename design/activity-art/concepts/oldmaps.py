"""Old maps: the sea monsters, ships and wind heads that decorate 1600s-1700s maps
(John Speed, Blaeu, Ortelius). Bold, slightly fanciful silhouettes on engraved seas.
"""
import math

from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group  # noqa: F401


# ================================================================ helpers (spine/frame copied from wildlife)
def _bez(p, t):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = p
    u = 1 - t
    x = u**3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t**3 * x3
    y = u**3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t**3 * y3
    dx = 3 * u * u * (x1 - x0) + 6 * u * t * (x2 - x1) + 3 * t * t * (x3 - x2)
    dy = 3 * u * u * (y1 - y0) + 6 * u * t * (y2 - y1) + 3 * t * t * (y3 - y2)
    n = math.hypot(dx, dy) or 1
    return x, y, dx / n, dy / n


def _chain(pts, t):
    """A point on a chain of cubics [p0, c1, c2, p1, c3, c4, p2, ...] at t in 0..1."""
    segs = (len(pts) - 1) // 3
    k = min(int(t * segs), segs - 1)
    return _bez(pts[3 * k:3 * k + 4], t * segs - k)


def frame(pts, t, up=0.0, fwd=0.0):
    """Point at t, moved `up` (to the left of travel) and `fwd`."""
    x, y, dx, dy = _chain(pts, t)
    return x + dy * up + dx * fwd, y - dx * up + dy * fwd


def tube(pts, w, n=48, t0=0.0, t1=1.0):
    """A tapering body along a chain of cubics; w(t) -> full width."""
    left, right = [], []
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        x, y, dx, dy = _chain(pts, t)
        h = w(t) / 2
        left.append((x + dy * h, y - dx * h))
        right.append((x - dy * h, y + dx * h))
    out = left + right[::-1]
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in out) + "Z"


def spikes(pts, w, ts, h, side=1, base=5.0):
    """Triangular spines along one edge of a tube (side 1 = left of travel)."""
    s = ""
    for t in ts:
        x, y, dx, dy = _chain(pts, t)
        r = w(t) / 2 - 2
        nx, ny = dy * side, -dx * side
        bx, by = x + nx * r, y + ny * r
        tip = (bx + nx * h - dx * h * 0.35, by + ny * h - dy * h * 0.35)
        s += (f"M{bx - dx * base:.1f} {by - dy * base:.1f} L{tip[0]:.1f} {tip[1]:.1f} "
              f"L{bx + dx * base:.1f} {by + dy * base:.1f}Z ")
    return s


def drop(x, y, r):
    return f"M{x} {y - r * 2.2} C{x + r * 0.6} {y - r} {x + r} {y - r * 0.4} {x + r} {y} a{r} {r} 0 0 1 {-2 * r} 0 C{x - r} {y - r * 0.4} {x - r * 0.6} {y - r} {x} {y - r * 2.2}Z"


def curls(xs_ys, r=5):
    """Engraved wave crests: little hooked arcs, like the hatching on an old chart."""
    s = ""
    for x, y in xs_ys:
        s += f"M{x - r * 1.6} {y} q{r * 0.8} {-r * 1.4} {r * 1.8} {-r * 0.7} q{r * 0.6} {r * 0.4} {0} {r * 0.7} "
    return s


def front_sea(d: Drawing, y, role="near", amp=6, step=30, curl_pts=(), curl_r=4.5):
    """Foreground water as a filled shape (so it hides what's below the surface in line style too)."""
    d.shape(role, waves(y, amp, step) + " L230 230 L-30 230Z")
    if curl_pts:
        d.stroke("light", curls(curl_pts, curl_r), 2.0)


def back_sea(d: Drawing, y=118):
    d.band("far", waves(y, 3, 28))
    d.band("mid", waves(y + 14, 4, 32))


# ================================================================ SEA SERPENT
def serpent(d: Drawing):
    back_sea(d, 104)
    d.stroke("light", curls([(40, 128), (150, 124), (176, 134)], 3.5), 1.6, line=False)
    wn = lambda t: 26 - 10 * t
    neck = [(80, 160), (88, 116), (52, 110), (62, 70)]
    wh = lambda t: 22
    hump = [(98, 160), (100, 104), (146, 104), (148, 160)]
    wt = lambda t: max(3, 20 * (1 - t) ** 0.9)
    tail = [(156, 160), (158, 126), (182, 122), (178, 98), (174, 82), (158, 84), (162, 96)]
    # spines behind the body
    d.shape("pop", spikes(neck, wn, [0.34, 0.52, 0.7, 0.88], 11, side=-1, base=6), spot=True)
    d.shape("pop", spikes(hump, wh, [0.3, 0.5, 0.7], 12, side=1, base=6), spot=True)
    d.shape("pop", spikes(tail, wt, [0.12, 0.25], 8, side=1), spot=True)
    d.shape("hero", tube(tail, wt, 60))
    d.shape("hero", tube(hump, wh))
    d.shape("hero", tube(neck, wn))
    # banded belly scales
    for body, w, ts in [(neck, wn, [0.38, 0.5, 0.62, 0.74]), (hump, wh, [0.3, 0.42, 0.54, 0.66]), (tail, wt, [0.1, 0.2, 0.3])]:
        for t in ts:
            a = frame(body, t, w(t) / 2 - 1.5)
            b = frame(body, t, -w(t) / 2 + 1.5)
            d.stroke("hero2", f"M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f}", 2.2)
    # head facing left, jaws open
    def head():
        d.shape("pop", "M54 54 L70 38 L64 58Z M60 60 L78 52 L66 66Z", spot=True)
        d.shape("hero", "M60 50 C50 44 36 46 26 52 L14 54 C12 58 16 62 22 62 L44 64 C52 68 58 74 62 80 C70 72 70 58 60 50Z")
        d.shape("hero", "M44 66 L22 72 C20 76 24 80 30 79 C40 78 50 76 58 78Z")
        d.shape("light", "M22 62 L26 66 L30 62 L34 66 L38 62 L42 66 L44 64Z M28 72 L31 69 L34 72.5 L37 69 L40 72 L43 69 L46 71Z", shadow=False)
        d.stroke("pop", "M20 68 Q13 70 10 66 M13 69 Q11 73 8 73", 2.0)
        d.marks("light", circle(46, 54, 4))
        d.marks("dark", circle(45, 54, 2.2))
        d.marks("dark", circle(18, 56, 1.3))
    group(d, "translate(18 4)", head)
    front_sea(d, 152, "near", 6, 26, [(60, 170), (124, 166), (176, 172), (96, 186)])
    d.band("deep", waves(182, 4, 34), line=False)


# ================================================================ GALLEON
def sail(cx, top, w, h, bulge=5):
    l, r = cx - w / 2, cx + w / 2
    return (f"M{l} {top} Q{cx} {top - 3} {r} {top} C{r + bulge} {top + h * 0.35} {r + bulge} {top + h * 0.75} {r - 1} {top + h} "
            f"Q{cx} {top + h + 7} {l + 1} {top + h} C{l + bulge * 0.4} {top + h * 0.7} {l + bulge * 0.4} {top + h * 0.3} {l} {top}Z")


def pennant(x, y, length=24, wave=3):
    return (f"M{x} {y} C{x + length * 0.3} {y - wave} {x + length * 0.6} {y + wave} {x + length} {y + 1} "
            f"L{x + length * 0.78} {y + 3.5} L{x + length} {y + 6} C{x + length * 0.6} {y + 6 + wave} {x + length * 0.3} {y + 6 - wave} {x} {y + 7}Z")


HULL = ("M30 108 L56 113 L130 113 L136 98 L172 92 L170 108 C168 128 154 142 124 146 L74 146 "
        "C54 143 40 130 30 108Z")


def galleon_ship(d: Drawing, flags=True, sail_role="sail", rigging=True):
    if rigging:
        d.stroke("dark", "M38 108 L70 34 M70 34 L102 18 M102 18 L140 46 M140 46 L170 94", 1.1, line=False)
    # masts
    d.limb("dark", "M70 112 V34 M102 112 V18 M140 100 V46", 3.2)
    d.limb("dark", "M36 108 L8 88", 3.2)
    # spritsail under the bowsprit
    d.shape(sail_role, sail(22, 94, 16, 13, 3))
    # mizzen lateen
    d.shape(sail_role, "M140 50 L166 90 Q150 94 132 92 Q138 72 140 50Z")
    # fore and main, course + topsail
    d.shape(sail_role, sail(70, 62, 34, 32))
    d.shape(sail_role, sail(70, 38, 24, 20))
    d.shape(sail_role, sail(102, 54, 44, 38, 6))
    d.shape(sail_role, sail(102, 24, 32, 26))
    d.shape("pop", "M98 60 H106 V72 H118 V80 H106 V92 H98 V80 H86 V72 H98Z", shadow=False, spot=True)
    if flags:
        d.shape("pop", pennant(70, 26, 20), spot=True)
        d.shape("pop", pennant(102, 8, 28), spot=True)
        d.shape("pop", pennant(140, 38, 18), spot=True)
        d.stroke("dark", "M70 34 V25 M102 18 V7 M140 46 V37", 1.6)
    # hull
    d.shape("hull", HULL)
    d.shape("hero2", "M36 120 C70 124 120 124 168 116 L167 122 C120 130 70 130 39 126Z", shadow=False, spot=True)
    d.shape("hero2", "M136 98 L172 92 L171 97 L137 103Z", shadow=False)
    d.marks("dark", "".join(rrect(x, 115, 5, 5, 1) for x in (60, 76, 92, 108, 124)))
    d.marks("hero2", rrect(150, 100, 5, 6, 1.5) + rrect(158, 99, 5, 6, 1.5))
    d.stroke("dark", "M44 113 L136 113", 1.2, line=False)


def galleon(d: Drawing):
    d.disc("glow", 104, 74, 62)
    back_sea(d, 120)
    group(d, "translate(4 10)", lambda: galleon_ship(d))
    front_sea(d, 146, "near", 6, 28, [(40, 166), (100, 172), (160, 164), (70, 186), (138, 188)])
    d.band("deep", waves(186, 4, 34), line=False)


# ================================================================ WIND HEAD
def billow(pts, bulge=1.25):
    """A billowing cloud: arcs bulging outward between outline points (given clockwise on screen)."""
    s = f"M{pts[0][0]} {pts[0][1]}"
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        r = math.hypot(b[0] - a[0], b[1] - a[1]) / 2 * bulge
        s += f" A{r:.1f} {r:.1f} 0 0 1 {b[0]} {b[1]}"
    return s + "Z"


def gust(pts, w0, w1, n=60):
    """A stream of breath: narrow at the lips, swelling, then thinning into its curl."""
    return tube(pts, lambda t: max(1.6, w0 + (w1 - w0) * math.sin(math.pi * min(1, t * 1.6)) * (1 - t) ** 0.6), n)


def ringlet(x, y, r):
    """A spiral curl of hair."""
    return f"M{x + r * 0.55:.1f} {y:.1f} A{r * 0.55:.1f} {r * 0.55:.1f} 0 1 0 {x:.1f} {y + r * 0.55:.1f} A{r * 0.3:.1f} {r * 0.3:.1f} 0 0 0 {x + r * 0.25:.1f} {y + r * 0.1:.1f}"


def windhead(d: Drawing):
    # the sea below, whipped up by the wind
    d.band("mid", waves(146, 4, 30))
    front_sea(d, 160, "near", 5, 28, [(64, 172), (112, 176), (152, 168)], 4)
    # streams of breath fanning out across the circle, each ending in a curl
    streams = [
        ([(122, 94), (134, 82), (144, 70), (156, 64), (168, 58), (176, 70), (168, 76), (160, 80), (156, 70), (162, 68)], 3, 13),
        ([(124, 104), (140, 103), (156, 104), (168, 101), (180, 98), (182, 116), (170, 117), (162, 118), (160, 108), (166, 107)], 3, 14),
        ([(122, 114), (132, 126), (140, 140), (154, 142), (168, 144), (172, 128), (162, 127), (154, 127), (154, 137), (160, 137)], 3, 13),
    ]
    for pts, w0, w1 in streams:
        d.shape("wind", gust(pts, w0, w1), spot=True)
    # a big billowing cloud behind the head...
    ring = [(40, 46), (24, 48), (6, 50), (-12, 49), (-32, 48), (-54, 49), (-78, 50), (-102, 49), (-126, 50), (-150, 49),
            (-174, 47), (160, 46), (138, 47), (116, 46), (94, 44)]
    back = [(round(74 + r * math.cos(math.radians(-t)), 1), round(96 + r * math.sin(math.radians(-t)), 1)) for t, r in ring]
    d.shape("cloud", billow(back, 1.2))
    d.stroke("cloud2", "M36 84 C34 76 40 70 46 72", 2.2, line=False)

    def head():
        # face, three-quarter view facing right, with a plump chin
        d.shape("skin", "M46 92 C46 72 60 60 76 60 C92 60 104 72 104 90 C104 108 94 122 76 122 C60 122 46 110 46 92Z")
        # curly hair over the crown and down the back of the head
        curls = [(50, 100, 9), (47, 86, 9.5), (52, 72, 10), (64, 62, 10.5), (79, 58, 10), (92, 62, 8.5)]
        d.shape("hair", "".join(circle(x, y, r) for x, y, r in curls), spot=True)
        d.stroke("hair2", "".join(ringlet(x, y, r) for x, y, r in curls), 1.8)
        # puffed-out cheek bulging past the face, and pursed lips
        d.shape("skin", circle(98, 104, 17))
        d.shape("cheek", circle(97, 106, 9), shadow=False, line=False)
        d.shape("lips", ellipse(117, 101, 5, 6))
        d.marks("dark", ellipse(118.5, 101, 2, 2.8))
        # nose, screwed-up eye and raised brow
        d.shape("skin", "M93 78 C100 80 105 87 103 92 C100 95 95 93 92 90Z")
        d.stroke("skin2", "M96 93 Q100 94 103 91", 1.6, line=False)
        d.stroke("dark", "M80 84 Q86 89 93 84", 2.8)
        d.stroke("hair2", "M77 74 Q85 68 95 73", 3.2)
        d.stroke("skin2", "M64 112 Q70 120 80 120", 2.0, line=False)
    group(d, "translate(78 96) scale(.94) translate(-74 -94)", head)
    # ...and billowing round in front of the chin, so the head rises out of it
    d.shape("cloud", billow([(26, 104), (40, 112), (54, 120), (70, 128), (86, 134), (102, 134), (116, 130), (120, 142), (104, 150),
                             (78, 152), (52, 146), (32, 134), (24, 118)], 1.22))
    d.shape("cloud2", billow([(30, 126), (44, 134), (62, 140), (80, 144), (100, 146), (80, 151), (54, 146), (36, 138)], 1.15),
            shadow=False, line=False)


# ================================================================ SPOUTING WHALE
def whale(d: Drawing):
    back_sea(d, 118)
    # spout: a fountain from the blowhole, splitting left and right
    d.shape("spout", "M70 84 C64 62 50 44 30 42 C40 34 58 38 66 52 C66 38 70 26 76 18 C82 26 86 38 86 52 "
                     "C94 38 112 34 122 42 C102 44 88 62 82 84Z", spot=True)
    for x, y, r in [(26, 54, 3), (34, 66, 2.4), (126, 54, 3), (118, 66, 2.4), (60, 28, 2.2), (92, 28, 2.2)]:
        d.shape("spout", drop(x, y, r), shadow=False)
    # raised flukes behind
    d.shape("whale", "M150 140 C152 120 156 106 162 96 C152 90 144 76 142 58 C150 62 160 74 170 84 "
                     "C176 70 184 60 196 56 C194 72 186 88 174 98 C170 112 170 128 172 140Z")
    # body
    d.shape("whale", "M156 150 C154 124 140 96 112 84 C92 76 62 74 46 84 C30 92 22 106 22 120 C22 132 26 142 32 150Z")
    # belly grooves
    d.shape("belly", "M23 124 C40 128 70 130 100 128 C120 127 140 130 154 140 L154 150 L31 150 C26 143 23 134 23 124Z", shadow=False)
    d.stroke("whale", "M30 134 C60 138 100 136 150 146 M30 142 C60 146 100 144 150 152", 1.6)
    # mouth and teeth
    d.stroke("dark", "M24 112 C36 116 48 118 62 114", 2.2)
    d.shape("light", "M30 114 L32 119 L35 115 L38 120 L41 116 L44 121 L47 116 L50 120 L53 116 Z", shadow=False)
    # eye, brow and blowhole
    d.marks("light", circle(66, 102, 4.6))
    d.marks("dark", circle(67, 102, 2.4))
    d.stroke("dark", "M58 94 Q66 90 74 95", 2.0)
    d.marks("dark", ellipse(76, 84, 4, 1.6))
    # pectoral fin
    d.shape("whale2", "M86 120 C96 120 110 128 116 140 C104 140 92 134 86 120Z", spot=True)
    front_sea(d, 144, "near", 6, 30, [(40, 164), (100, 170), (170, 164), (70, 186), (140, 186)])
    d.band("deep", waves(184, 4, 34), line=False)


# ================================================================ KRAKEN
def tentacle(start, c1, c2, end, curl=None, w0=14.0):
    pts = [start, c1, c2, end]
    if curl:
        pts += curl
    return pts, (lambda t: max(2.2, w0 * (1 - t) ** 0.85))


def suckers(pts, w, ts, side=-1, role_r=1.9):
    s = ""
    for t in ts:
        x, y = frame(pts, t, side * (w(t) / 2 - role_r - 0.8))
        s += circle(round(x, 1), round(y, 1), max(1.0, role_r * w(t) / 14))
    return s


def kraken(d: Drawing):
    back_sea(d, 112)
    # head (mantle) rising behind the ship
    d.shape("kraken", "M112 134 C98 100 106 50 142 32 C174 18 200 44 198 82 C196 110 186 124 178 136Z", spot=True)
    d.shape("kraken2", "M128 50 C136 40 150 36 158 40 C146 44 138 50 134 60Z", shadow=False, line=False)
    d.marks("light", ellipse(140, 98, 8.5, 7) + ellipse(170, 102, 7.5, 6.5))
    d.marks("dark", ellipse(142, 99, 3.8, 5) + ellipse(171, 103, 3.4, 4.6))
    d.stroke("dark", "M128 86 Q140 80 152 88 M160 90 Q170 85 182 92", 2.2)
    # the ship, small and tilted, in front of the head
    group(d, "translate(14 60) rotate(-8 60 100) scale(.6)", lambda: galleon_ship(d, flags=True, sail_role="sail", rigging=False))
    arms = [
        # arm rising behind the ship and coiling round the mainmast
        tentacle((126, 150), (126, 108), (106, 72), (88, 62), [(72, 56), (62, 70), (72, 78), (82, 84), (88, 74), (80, 70)], 15),
        # arm rising on the far left, curling
        tentacle((40, 152), (20, 128), (12, 100), (26, 82), [(36, 68), (54, 74), (48, 88), (42, 96), (34, 90), (38, 84)], 13),
        # arm hooked over the stern
        tentacle((160, 150), (158, 128), (136, 110), (118, 116), [(108, 120), (108, 132), (116, 132)], 12),
    ]
    for pts, w in arms:
        d.shape("kraken", tube(pts, w, 70), spot=True)
        d.marks("kraken2", suckers(pts, w, [0.1, 0.2, 0.3, 0.4, 0.5]))
    front_sea(d, 148, "near", 6, 26, [(70, 168), (120, 174), (172, 168), (96, 188), (40, 186)])
    d.band("deep", waves(186, 4, 34), line=False)


# ================================================================ MERMAID
def mermaid(d: Drawing):
    back_sea(d, 120)
    # rock she sits on
    d.shape("rock", "M40 150 C44 128 60 116 82 116 C104 116 118 128 122 150Z")
    d.stroke("dark", "M58 132 Q66 128 72 132 M92 128 Q100 124 106 130", 1.6, line=False)
    # tail: from the hips down over the rock, then curling up over a wave
    tail = [(88, 112), (98, 134), (120, 150), (146, 140), (166, 132), (170, 112), (160, 98)]
    wt = lambda t: max(5, 26 * (1 - t) ** 0.7)
    d.shape("tail", tube(tail, wt, 64))
    fx, fy, dx, dy = _chain(tail, 1.0)
    d.shape("tail", f"M{fx:.1f} {fy + 2:.1f} C{fx - 8:.1f} {fy - 6:.1f} {fx - 18:.1f} {fy - 10:.1f} {fx - 22:.1f} {fy - 20:.1f} "
                    f"C{fx - 10:.1f} {fy - 18:.1f} {fx - 4:.1f} {fy - 12:.1f} {fx:.1f} {fy - 6:.1f} "
                    f"C{fx + 2:.1f} {fy - 16:.1f} {fx + 8:.1f} {fy - 24:.1f} {fx + 18:.1f} {fy - 28:.1f} "
                    f"C{fx + 16:.1f} {fy - 16:.1f} {fx + 10:.1f} {fy - 6:.1f} {fx + 4:.1f} {fy + 2:.1f}Z", spot=True)
    sc = ""
    for t in [0.14, 0.26, 0.38, 0.5, 0.62, 0.74]:
        for off in (-0.25, 0.0, 0.25):
            x, y = frame(tail, t, off * wt(t))
            r = max(1.4, wt(t) * 0.13)
            sc += f"M{x - r:.1f} {y:.1f} a{r:.1f} {r:.1f} 0 0 0 {2 * r:.1f} 0 "
    d.stroke("tail2", sc, 1.4, line=False)
    # long hair down her back
    d.shape("hair", "M86 46 C100 44 108 56 106 72 C104 88 110 102 118 114 C104 118 94 110 90 98 C86 86 82 74 80 60Z")
    # torso and head, facing left towards the mirror
    d.shape("skin", "M79 78 C75 88 75 102 79 114 L99 112 C101 100 99 88 95 78Z")
    d.shape("skin", "M84 66 L92 66 L93 80 L84 80Z", shadow=False)
    d.shape("skin", "M74 52 C74 44 80 40 88 40 C96 40 100 48 100 56 C100 64 96 70 88 70 C82 70 78 68 76 64 "
                    "L73 64 L74 60 L71 58 L74 54Z")
    d.stroke("tail2", "M80 112 C86 116 94 116 100 110", 2.4)
    # arm raised, holding a hand mirror
    d.limb("skin", "M84 84 C74 86 64 80 60 70", 6.5)
    d.limb("mirror", "M60 70 L57 60", 3.2)
    d.shape("mirror", ellipse(54, 48, 9.5, 11.5), spot=True)
    d.shape("glass", ellipse(54, 48, 6.5, 8.5), shadow=False)
    d.stroke("light", "M51 43 L55 39", 1.6, line=False)
    # hair: crown and a lock falling over the shoulder and chest
    d.shape("hair", "M76 48 C78 38 94 34 100 44 C104 52 102 60 98 66 C100 78 98 92 90 104 C86 96 88 84 90 74 "
                    "C92 66 92 58 88 52 C84 48 80 48 76 50Z", spot=True)
    d.marks("dark", ellipse(80, 54, 1.4, 1.8))
    d.stroke("dark", "M77 49 Q80 47 83 49", 1.2, line=False)
    d.stroke("lips", "M74 62 Q76 63 78 62", 1.4, line=False)
    front_sea(d, 150, "near", 6, 28, [(40, 168), (100, 174), (160, 168), (70, 188), (136, 188)])
    d.band("deep", waves(186, 4, 34), line=False)


# ================================================================ concepts
SEA = ["coastal", "dusk", "meadow", "blush"]
SHIP = {"hull": "#8A5A36", "sail": "#FBF3DC"}
WIND = {"skin": "#F4C9A4", "cheek": "#EE9C88", "lips": "#D9604C", "hair": "#E0A43A", "cloud": "#FFFFFF", "cloud2": "#E8EEF4",
        "wind": "#FFFFFF", "hair2": "#A8701E", "skin2": "#E0A887"}
WHALE_C = {"whale": "#5E7389", "whale2": "#46596E", "belly": "#E9DCC0"}
KRAKEN_C = {"kraken": "#C9473C", "kraken2": "#F3B7A0", **SHIP}
MERMAID_C = {"skin": "#F4C9A4", "lips": "#C65A4A", "hair": "#C8643A", "tail": "#2E9C83", "tail2": "#1F6E5D", "rock": "#8C8478",
             "mirror": "#D9A441", "glass": "#DDEEF3"}

CONCEPTS = [
    Concept("oldmap-serpent", "oldmap-sea-serpent", "Sea serpent", serpent, SEA,
            checks=[("hero", "near"), ("hero", "mid"), ("hero", "sky"), ("pop", "sky"), ("hero", "far")],
            fixes={"hero": ["pop", "hero2", "#3F8F5A", "#C9473C"], "pop": ["hero2", "deep", "dark"]}),
    Concept("oldmap-galleon", "oldmap-galleon", "Galleon", galleon, SEA, overrides=SHIP,
            checks=[("sail", "glow"), ("hull", "near"), ("hull", "mid"), ("glow", "sky")],
            fixes={"glow": ["far", "mid", "near"]}),
    Concept("oldmap-windhead", "oldmap-wind-head", "Wind head", windhead, SEA, overrides=WIND,
            checks=[("cloud", "sky"), ("wind", "sky"), ("skin", "cloud"), ("hair", "cloud"), ("cloud", "mid")],
            fixes={"sky": ["far", "sky2", "#9FC9DB", "mid"]}),
    Concept("oldmap-whale", "oldmap-whale", "Spouting whale", whale, SEA, overrides={**WHALE_C, "spout": "#FFFFFF"},
            checks=[("whale", "near"), ("whale", "mid"), ("whale", "far"), ("spout", "sky")],
            fixes={"whale": ["#8D99AE", "#3E4A5A", "hero"], "sky": ["far", "mid", "sky2"]}),
    Concept("oldmap-kraken", "oldmap-kraken", "Kraken", kraken, SEA, overrides=KRAKEN_C,
            checks=[("kraken", "near"), ("kraken", "mid"), ("kraken", "far"), ("kraken", "sky"), ("sail", "kraken")],
            fixes={"kraken": ["#9E3B6B", "#E0653A", "hero"]}),
    Concept("oldmap-mermaid", "oldmap-mermaid", "Mermaid", mermaid, SEA, overrides=MERMAID_C,
            checks=[("tail", "near"), ("tail", "mid"), ("hair", "sky"), ("skin", "sky"), ("rock", "near"), ("tail", "rock")],
            fixes={"tail": ["#3AA58A", "#2A7F8F", "hero", "hero2"], "sky": ["far", "sky2", "#CFE3EA", "mid"], "rock": ["#B8AD9C", "#6E655A", "dark"]}),
]
