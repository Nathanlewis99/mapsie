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
    neck = [(78, 160), (84, 118), (36, 110), (46, 68)]
    wh = lambda t: 22
    hump = [(98, 160), (100, 104), (146, 104), (148, 160)]
    wt = lambda t: max(3, 20 * (1 - t) ** 0.9)
    tail = [(160, 160), (162, 122), (196, 118), (186, 88), (180, 72), (158, 74), (164, 88)]
    # spines behind the body
    d.shape("pop", spikes(neck, wn, [0.3, 0.45, 0.6, 0.75, 0.9], 9, side=-1), spot=True)
    d.shape("pop", spikes(hump, wh, [0.28, 0.42, 0.58, 0.72], 10, side=1), spot=True)
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
    d.shape("pop", "M54 54 L70 38 L64 58Z M60 60 L78 52 L66 66Z", spot=True)
    d.shape("hero", "M60 50 C50 44 36 46 26 52 L14 54 C12 58 16 62 22 62 L44 64 C52 68 58 74 62 80 C70 72 70 58 60 50Z")
    d.shape("hero", "M44 66 L22 72 C20 76 24 80 30 79 C40 78 50 76 58 78Z")
    d.shape("light", "M22 62 L26 66 L30 62 L34 66 L38 62 L42 66 L44 64Z M28 72 L31 69 L34 72.5 L37 69 L40 72 L43 69 L46 71Z", shadow=False)
    d.stroke("pop", "M20 68 Q10 70 6 66 M10 69 Q6 74 2 74", 2.0)
    d.marks("light", circle(46, 54, 4))
    d.marks("dark", circle(45, 54, 2.2))
    d.marks("dark", circle(18, 56, 1.3))
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
    back_sea(d, 120)
    d.shape("light", cloud(150, 40, 0.9), shadow=False, line=False)
    d.shape("light", cloud(10, 54, 0.7), shadow=False, line=False)
    group(d, "translate(4 6)", lambda: galleon_ship(d))
    front_sea(d, 146, "near", 6, 28, [(40, 166), (100, 172), (160, 164), (70, 186), (138, 188)])
    d.band("deep", waves(186, 4, 34), line=False)


# ================================================================ WIND HEAD
def puff(cx, cy, r, n=9, k=0.3):
    """A scalloped cloud ring."""
    s = ""
    pts = [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    s = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(n):
        a = pts[i]
        b = pts[(i + 1) % n]
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        ox, oy = mx - cx, my - cy
        L = math.hypot(ox, oy)
        c = (mx + ox / L * r * k * 1.6, my + oy / L * r * k * 1.6)
        s += f" Q{c[0]:.1f} {c[1]:.1f} {b[0]:.1f} {b[1]:.1f}"
    return s + "Z"


def windhead(d: Drawing):
    # wind lines streaming right, curling at their ends
    d.stroke("wind", "M118 98 C140 92 160 86 176 92 C188 97 186 110 176 110 C168 110 168 100 176 100", 4.2)
    d.stroke("wind", "M120 110 C146 112 170 116 190 124", 4.2)
    d.stroke("wind", "M118 122 C138 132 152 146 172 150 C184 152 188 140 180 136 C172 134 170 142 176 144", 4.2)
    d.stroke("wind", "M116 86 C134 74 150 66 168 66", 3.4)
    # cloud around the back of the head
    d.shape("cloud", puff(62, 100, 46, 11, 0.32))
    d.shape("cloud2", puff(56, 104, 30, 9, 0.3), shadow=False)
    # hair curls
    d.shape("hair", puff(64, 84, 26, 9, 0.35))
    # face: puffed cheeks, pursed lips, facing right
    d.shape("skin", "M60 78 C76 66 98 70 104 84 C108 88 110 92 108 96 C116 98 118 108 112 114 "
                    "C108 126 96 134 82 132 C68 132 56 122 54 106 C52 94 54 84 60 78Z")
    d.shape("cheek", circle(90, 112, 9), shadow=False)
    d.shape("skin", "M110 100 C118 98 122 104 118 110 C122 114 118 120 112 118Z")
    d.marks("lips", ellipse(119, 108, 3.5, 4.2))
    d.marks("dark", ellipse(119, 108, 1.6, 2))
    d.stroke("dark", "M84 92 Q90 88 96 92", 2.2)
    d.stroke("dark", "M82 84 Q90 78 99 83", 2.0)
    d.stroke("dark", "M66 104 Q62 98 66 94", 1.8, line=False)
    # little wind puffs at the lips
    d.shape("cloud", puff(136, 106, 6, 6, 0.3), shadow=False)
    d.shape("cloud", puff(150, 100, 4, 6, 0.3), shadow=False)


# ================================================================ SPOUTING WHALE
WHALE = [(152, 148), (150, 112), (126, 82), (92, 80), (64, 78), (36, 92), (28, 122)]


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
    w = lambda t: 10 + 46 * math.sin(math.pi * min(1, t * 1.05) ** 0.8) if t < 0.95 else 46
    d.shape("whale", "M156 150 C154 124 140 96 112 84 C92 76 62 74 46 84 C32 92 24 106 24 122 L24 150Z")
    # belly grooves
    d.shape("belly", "M24 122 C40 128 70 130 100 128 C120 127 140 130 154 140 L154 150 L24 150Z", shadow=False)
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
    d.shape("kraken", "M118 128 C104 104 108 56 140 38 C170 22 198 44 198 78 C198 104 186 120 176 132Z")
    d.shape("kraken2", "M132 50 C140 42 152 40 158 44 C148 46 140 52 136 60Z", shadow=False)
    d.marks("light", ellipse(140, 104, 8, 6.5) + ellipse(168, 108, 7, 6))
    d.marks("dark", ellipse(142, 105, 3.6, 4.6) + ellipse(169, 109, 3.2, 4.2))
    d.stroke("dark", "M130 94 Q140 90 150 96 M160 98 Q168 94 178 100", 2.0)
    arms = [
        # arm wrapping over and round the mainmast
        tentacle((130, 132), (118, 90), (106, 56), (86, 46), [(70, 40), (60, 56), (74, 62), (84, 66), (90, 56), (82, 52)], 16),
        # arm rising on the far left, curling
        tentacle((40, 150), (24, 124), (14, 98), (28, 78), [(38, 64), (54, 74), (46, 86), (40, 94), (32, 88), (36, 82)], 14),
        # arm hooked over the stern
        tentacle((176, 136), (184, 116), (176, 96), (160, 98), [(150, 100), (146, 112), (154, 114)], 13),
    ]
    # the ship, small and tilted, behind the front arms
    group(d, "translate(44 52) rotate(-10 60 100) scale(.62)", lambda: galleon_ship(d, flags=True, sail_role="sail", rigging=False))
    for pts, w in arms:
        d.shape("kraken", tube(pts, w, 70))
        d.marks("kraken2", suckers(pts, w, [0.08, 0.16, 0.24, 0.32, 0.4, 0.48, 0.56]))
    front_sea(d, 146, "near", 6, 26, [(70, 166), (120, 172), (172, 168), (96, 186), (40, 184)])
    d.band("deep", waves(184, 4, 34), line=False)


# ================================================================ MERMAID
def mermaid(d: Drawing):
    back_sea(d, 120)
    # rock she sits on
    d.shape("rock", "M40 150 C44 128 60 116 82 116 C104 116 118 128 122 150Z")
    # tail: from the hips down over the rock, then curling up over a wave
    tail = [(86, 112), (96, 134), (120, 150), (146, 140), (166, 132), (170, 112), (160, 98)]
    wt = lambda t: max(5, 26 * (1 - t) ** 0.7)
    d.shape("tail", tube(tail, wt, 64))
    # fluke
    fx, fy, dx, dy = _chain(tail, 1.0)
    d.shape("tail", f"M{fx:.1f} {fy + 2:.1f} C{fx - 8:.1f} {fy - 6:.1f} {fx - 18:.1f} {fy - 10:.1f} {fx - 22:.1f} {fy - 20:.1f} "
                    f"C{fx - 10:.1f} {fy - 18:.1f} {fx - 4:.1f} {fy - 12:.1f} {fx:.1f} {fy - 6:.1f} "
                    f"C{fx + 2:.1f} {fy - 16:.1f} {fx + 8:.1f} {fy - 24:.1f} {fx + 18:.1f} {fy - 28:.1f} "
                    f"C{fx + 16:.1f} {fy - 16:.1f} {fx + 10:.1f} {fy - 6:.1f} {fx + 4:.1f} {fy + 2:.1f}Z", spot=True)
    # scales
    sc = ""
    for t in [0.14, 0.26, 0.38, 0.5, 0.62, 0.74]:
        for off in (-0.25, 0.0, 0.25):
            x, y = frame(tail, t, off * wt(t))
            r = max(1.4, wt(t) * 0.13)
            sc += f"M{x - r:.1f} {y:.1f} a{r:.1f} {r:.1f} 0 0 0 {2 * r:.1f} 0 "
    d.stroke("tail2", sc, 1.4, line=False)
    d.stroke("tail2", "M78 112 C84 116 92 116 98 110", 2.4)
    # back hair
    d.shape("hair", "M84 54 C98 52 106 64 104 78 C102 92 110 104 116 114 C104 116 96 110 92 100 C88 90 80 80 78 66Z")
    # body: torso and head, facing left
    d.shape("skin", "M76 76 C72 86 72 100 76 114 L98 112 C100 100 98 88 92 78Z")
    d.shape("skin", "M84 68 L90 68 L91 80 L83 80Z", shadow=False)
    d.shape("skin", circle(86, 56, 13))
    d.marks("skin", "M74 56 L70 60 L74 62Z")
    # arm raised, holding a mirror
    d.limb("skin", "M80 84 C70 86 62 80 58 70", 6.5)
    d.limb("mirror", "M58 72 L56 62", 3.2)
    d.shape("mirror", ellipse(54, 50, 9, 11), spot=True)
    d.shape("glass", ellipse(54, 50, 6, 8), shadow=False)
    # front hair, flowing over the shoulder and chest
    d.shape("hair", "M76 52 C76 40 94 38 100 48 C104 56 100 66 96 72 C98 84 96 96 90 104 C86 94 84 86 84 76 "
                    "C80 72 76 62 76 52Z")
    d.marks("dark", circle(78, 56, 1.4))
    d.stroke("dark", "M75 63 Q77 65 79 64", 1.2, line=False)
    front_sea(d, 150, "near", 6, 28, [(40, 168), (100, 174), (160, 168), (70, 188), (136, 188)])
    d.band("deep", waves(186, 4, 34), line=False)


# ================================================================ concepts
SEA = ["coastal", "dusk", "meadow", "blush"]
SHIP = {"hull": "#8A5A36", "sail": "#FBF3DC"}
WIND = {"skin": "#F4C9A4", "cheek": "#EE9C88", "lips": "#D9604C", "hair": "#E7B04A", "cloud": "#FFFFFF", "cloud2": "#EEF2F6"}
WHALE_C = {"whale": "#5E7389", "whale2": "#46596E", "belly": "#E9DCC0"}
KRAKEN_C = {"kraken": "#C9473C", "kraken2": "#F3B7A0", **SHIP}
MERMAID_C = {"skin": "#F4C9A4", "hair": "#C8643A", "tail": "#2E9C83", "tail2": "#1F6E5D", "rock": "#8C8478",
             "mirror": "#D9A441", "glass": "#DDEEF3"}

CONCEPTS = [
    Concept("oldmap-serpent", "oldmap-sea-serpent", "Sea serpent", serpent, SEA,
            checks=[("hero", "near"), ("hero", "mid"), ("hero", "sky"), ("pop", "sky"), ("hero", "far")],
            fixes={"hero": ["pop", "hero2", "#3F8F5A", "#C9473C"], "pop": ["hero2", "deep", "dark"]}),
    Concept("oldmap-galleon", "oldmap-galleon", "Galleon", galleon, SEA, overrides=SHIP,
            checks=[("sail", "sky"), ("hull", "near"), ("sail", "far")],
            fixes={"sky": ["far", "mid", "sky2"]}),
    Concept("oldmap-windhead", "oldmap-wind-head", "Wind head", windhead, overrides={**WIND, "wind": "#5C7A99"},
            checks=[("cloud", "sky"), ("skin", "cloud"), ("wind", "sky")],
            fixes={"sky": ["far", "mid", "sky2"], "wind": ["deep", "near", "mark", "light"]}),
    Concept("oldmap-whale", "oldmap-whale", "Spouting whale", whale, SEA, overrides={**WHALE_C, "spout": "#FFFFFF"},
            checks=[("whale", "near"), ("whale", "mid"), ("whale", "far"), ("spout", "sky")],
            fixes={"whale": ["#8D99AE", "#3E4A5A", "hero"], "sky": ["far", "mid", "sky2"]}),
    Concept("oldmap-kraken", "oldmap-kraken", "Kraken", kraken, SEA, overrides=KRAKEN_C,
            checks=[("kraken", "near"), ("kraken", "mid"), ("kraken", "far"), ("kraken", "sky"), ("sail", "kraken")],
            fixes={"kraken": ["#9E3B6B", "#E0653A", "hero"]}),
    Concept("oldmap-mermaid", "oldmap-mermaid", "Mermaid", mermaid, SEA, overrides=MERMAID_C,
            checks=[("tail", "near"), ("tail", "mid"), ("hair", "sky"), ("skin", "sky"), ("rock", "near"), ("tail", "rock")],
            fixes={"tail": ["#3AA58A", "#2A7F8F", "hero", "hero2"], "sky": ["far", "sky2", "mid"], "rock": ["#B8AD9C", "#6E655A", "dark"]}),
]
