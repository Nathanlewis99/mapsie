"""Transport & moments, round two: three ideas each for first class, long-haul flights, sleeper and bullet
trains, funiculars, rickshaws, canal boats, hitchhiking, bus journeys, and birthday, anniversary, girls',
lads', graduation, digital-nomad and reunion trips."""
import math

from _common import Concept, Drawing, cloud, circle, ellipse, waves, hills, rrect, group

ALL = ["golden", "coastal", "meadow", "blush", "dusk"]
SEA = ["coastal", "meadow", "blush", "dusk"]
EVENODD = 'fill-rule="evenodd"'


# ================================================================ private helpers
def _clip(d: Drawing, cid: str, path: str, fn):
    """Clip everything drawn by fn to `path`, in both styles."""
    tag = f'<clipPath id="{cid}"><path d="{path}"/></clipPath><g clip-path="url(#{cid})">'
    d.raw(tag, tag)
    fn()
    d.raw("</g>", "</g>")


def framed(fn):
    """Line style doesn't clip shapes to the sticker; clip anything that bleeds past the edge."""
    def draw(d: Drawing):
        if d.paper:
            fn(d)
        else:
            _clip(d, "frame", circle(100, 100, 89), lambda: fn(d))
    draw.__name__ = fn.__name__
    return draw


def _post(d: Drawing, role, x, y0, y1, w, shadow=True, spot=False):
    """A vertical pole as a thin shape (vertical limbs lose their shadow filter)."""
    d.shape(role, rrect(x - w / 2, y0, w, y1 - y0, w / 2), shadow=shadow, spot=spot)


def _puffs(y, radii=(12, 16, 10, 14, 11, 15), x0=-30):
    """A cloud-bank edge: a row of upward bumps from x0 to past 230."""
    s, x, i = f"M{x0} {y}", x0, 0
    while x < 232:
        r = radii[i % len(radii)]
        s += f" a{r} {r} 0 0 1 {2 * r} 0"
        x += 2 * r
        i += 1
    return s


def _wheel(d: Drawing, x, y, r, tyre="dark", hub="light"):
    d.shape(tyre, circle(x, y, r))
    d.shape(hub, circle(x, y, r * 0.42), shadow=False)


def _pine(x, y, s=1.0):
    return (f"M{x} {y - 30 * s} L{x + 9 * s} {y - 16 * s} L{x + 5 * s} {y - 16 * s} L{x + 12 * s} {y - 4 * s} "
            f"L{x + 2 * s} {y - 4 * s} V{y} H{x - 2 * s} V{y - 4 * s} L{x - 12 * s} {y - 4 * s} "
            f"L{x - 5 * s} {y - 16 * s} L{x - 9 * s} {y - 16 * s}Z")


def _star(x, y, r, k=0.42, n=5, rot=-90):
    pts = []
    for i in range(2 * n):
        a = math.radians(rot + i * 180 / n)
        rr = r if i % 2 == 0 else r * k
        pts.append(f"{x + rr * math.cos(a):.1f} {y + rr * math.sin(a):.1f}")
    return "M" + " L".join(pts) + "Z"


def _sparkle(x, y, r):
    return _star(x, y, r, 0.3, 4)


def _heart(x, y, s=1.0):
    """A heart centred on (x, y), about 20*s wide."""
    return (f"M{x} {y + 8 * s} C{x - 4 * s} {y + 4 * s} {x - 10 * s} {y} {x - 10 * s} {y - 4 * s} "
            f"C{x - 10 * s} {y - 9 * s} {x - 5 * s} {y - 11 * s} {x} {y - 6 * s} "
            f"C{x + 5 * s} {y - 11 * s} {x + 10 * s} {y - 9 * s} {x + 10 * s} {y - 4 * s} "
            f"C{x + 10 * s} {y} {x + 4 * s} {y + 4 * s} {x} {y + 8 * s}Z")


def _night(d: Drawing):
    """A night sky that follows the palette: the darkest landscape colour, edge to edge."""
    d.band("deep", "M-30 -30 H230", shadow=False, line=False)


def _stars(d: Drawing, pts, role="light"):
    for x, y, r in pts:
        d.shape(role, _sparkle(x, y, r), shadow=False)


def _dash(d: Drawing, path, role, w=2.4, dash="1 6", line=True):
    """A dotted / dashed route line."""
    col = d.c[role] if d.paper else d.c["ink"]
    if d.paper or line:
        d.raw(f'<path d="{path}" fill="none" stroke="{col}" stroke-width="{w}" stroke-dasharray="{dash}" stroke-linecap="round"/>',
              f'<path d="{path}" fill="none" stroke="{col}" stroke-width="{min(w, 2.6)}" stroke-dasharray="{dash}" stroke-linecap="round"/>')


def _person(d: Drawing, x, base, s, role="dark", legs=True):
    """A simple standing figure (head, rounded body, legs), feet on `base`, absolute coordinates."""
    X = lambda dx: round(x + dx * s, 1)
    Y = lambda dy: round(base + dy * s, 1)
    if legs:
        d.limb(role, f"M{X(-5)} {Y(-2)} L{X(-5.5)} {Y(-26)} M{X(5)} {Y(-2)} L{X(5.5)} {Y(-26)}", 6.5 * s)
    d.shape(role, f"M{X(-11)} {Y(-26)} V{Y(-50)} C{X(-11)} {Y(-58)} {X(-6)} {Y(-62)} {X(0)} {Y(-62)} "
                  f"C{X(6)} {Y(-62)} {X(11)} {Y(-58)} {X(11)} {Y(-50)} V{Y(-26)}Z")
    d.shape(role, circle(X(0), Y(-72), 9 * s))


def _palm(d: Drawing, x, y, s=1.0, role="dark", lean=6):
    """A palm tree whose trunk base is at (x, y)."""
    tx, ty = x + lean * s, y - 62 * s
    d.limb(role, f"M{x} {y} Q{x + lean * 0.2 * s} {y - 34 * s} {tx} {ty}", 4.5 * s)
    for dx, dy, cx, cy in [(-26, 10, -14, -8), (26, 12, 14, -8), (-20, -10, -12, -14), (22, -8, 12, -14), (-4, 18, -6, 4), (6, 20, 8, 4)]:
        d.shape(role, f"M{tx} {ty} Q{tx + cx * s} {ty + cy * s} {tx + dx * s} {ty + dy * s} "
                      f"Q{tx + cx * 0.6 * s} {ty + cy * 0.2 * s} {tx} {ty + 2 * s}Z", shadow=False)


def _bulbs(d: Drawing, x0, y0, x1, y1, sag, n, roles, r=2.6):
    """Festoon lights on a sagging string."""
    cx, cy = (x0 + x1) / 2, max(y0, y1) + sag
    d.stroke("dark", f"M{x0} {y0} Q{cx} {cy} {x1} {y1}", 1.3)
    for i in range(1, n + 1):
        t = i / (n + 1)
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1
        d.shape(roles[i % len(roles)], circle(round(x, 1), round(y + r, 1), r), shadow=False, spot=True)


def _flags(d: Drawing, x0, y0, x1, y1, sag, n, roles, size=4.0):
    """Bunting on a sagging string."""
    cx, cy = (x0 + x1) / 2, max(y0, y1) + sag
    d.stroke("dark", f"M{x0} {y0} Q{cx} {cy} {x1} {y1}", 1.3)
    for i in range(1, n + 1):
        t = i / (n + 1)
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1
        d.shape(roles[i % len(roles)], f"M{x - size:.1f} {y:.1f} L{x + size:.1f} {y:.1f} L{x:.1f} {y + size * 2:.1f}Z",
                shadow=False, spot=i % 2 == 0)


def _annulus(cx, cy, r1, r2, a1, a2):
    """A segment of a ring between angles a1 and a2 (degrees, clockwise)."""
    p = lambda r, a: f"{cx + r * math.cos(math.radians(a)):.1f} {cy + r * math.sin(math.radians(a)):.1f}"
    big = 1 if (a2 - a1) % 360 > 180 else 0
    return f"M{p(r2, a1)} A{r2} {r2} 0 {big} 1 {p(r2, a2)} L{p(r1, a2)} A{r1} {r1} 0 {big} 0 {p(r1, a1)}Z"


def _flute(d: Drawing, x, base, s=1.0, glass="light", fizz="hero2", spot=False):
    """A champagne flute standing on `base`."""
    X = lambda dx: round(x + dx * s, 1)
    Y = lambda dy: round(base + dy * s, 1)
    d.shape(glass, f"M{X(-8)} {Y(-62)} H{X(8)} C{X(9)} {Y(-44)} {X(6)} {Y(-30)} {X(0)} {Y(-28)} C{X(-6)} {Y(-30)} {X(-9)} {Y(-44)} {X(-8)} {Y(-62)}Z")
    d.shape(fizz, f"M{X(-7)} {Y(-52)} H{X(7)} C{X(7)} {Y(-40)} {X(5)} {Y(-32)} {X(0)} {Y(-31)} C{X(-5)} {Y(-32)} {X(-7)} {Y(-40)} {X(-7)} {Y(-52)}Z",
            shadow=False, spot=spot)
    d.limb(glass, f"M{X(0)} {Y(-28)} L{X(0.2)} {Y(-3)}", 2.6 * s, shadow=False)
    d.shape(glass, ellipse(X(0), Y(-2), 9 * s, 2.6 * s))


# ================================================================ FIRST CLASS
@framed
def fc_seat(d: Drawing):
    d.band("far", "M-30 -30 H230", shadow=False, line=False)

    def view():
        d.shape("sky", "M110 20 H180 V120 H110Z", shadow=False, line=False)
        d.disc("glow", 152, 58, 9)
        d.shape("light", _puffs(84, (5, 8, 4, 7), 110) + " L230 230 L110 230Z", shadow=False)
    d.shape("light", rrect(126, 34, 42, 66, 21))
    _clip(d, "fcwin", rrect(132, 40, 30, 54, 15), view)
    d.band("mid", "M-30 160 H230")
    # seat, facing left
    d.shape("dark", "M70 134 H128 L124 162 H74Z")
    d.shape("hero", "M96 138 L104 46 C105 32 126 30 128 44 L134 138Z")
    d.shape("hero2", "M104 46 C105 32 126 30 128 44 L129.5 62 H103Z", shadow=False, spot=True)
    d.shape("hero", "M52 120 L28 146 C25 150 29 155 33 153 L64 132Z")
    d.shape("hero", rrect(46, 114, 92, 20, 9))
    d.shape("light", "M62 112 C78 108 104 108 116 112 L118 134 C102 138 80 138 60 134Z", shadow=False, spot=True)
    d.stroke("far", "M66 120 C82 117 100 117 116 120", 1.4, line=False)
    d.shape("hero", rrect(84, 98, 54, 11, 5.5))
    d.shape("dark", rrect(140, 124, 34, 6, 3))
    _post(d, "dark", 157, 128, 160, 4, shadow=False)
    _flute(d, 157, 124, 0.66, spot=False)


def fc_mask(d: Drawing):
    d.disc("glow", 100, 100, 62)
    _stars(d, [(40, 58, 5), (162, 50, 4), (160, 150, 4.5), (40, 142, 3.5)])

    def slipper(x, rot, spot):
        def s():
            d.shape("light", ellipse(0, 0, 15, 27))
            d.shape("hero", "M-15 -2 C-15 -20 -8 -27 0 -27 C8 -27 15 -20 15 -2 C8 3 -8 3 -15 -2Z", shadow=False, spot=spot)
            d.stroke("hero2", "M-13 -3 C-6 1 6 1 13 -3", 1.6, line=False)
        group(d, f"translate({x} 140) rotate({rot})", s)
    slipper(80, -10, False)
    slipper(120, 10, False)
    d.limb("dark", "M54 70 C40 66 32 72 30 82 M146 70 C160 66 168 72 170 82", 3.2, shadow=False)
    mask = "M52 72 C52 50 76 46 100 58 C124 46 148 50 148 72 C148 92 126 98 112 90 C106 86 94 86 88 90 C74 98 52 92 52 72Z"
    d.shape("hero", mask, spot=True)
    d.stroke("hero2", "M56 70 C58 54 78 52 100 62 C122 52 142 54 144 70", 1.8, line=False)
    for cx in (76, 124):
        d.stroke("mark", f"M{cx - 12} 72 Q{cx} 80 {cx + 12} 72", 2.4)
        d.stroke("mark", f"M{cx - 8} 77 L{cx - 10} 82 M{cx} 79 V85 M{cx + 8} 77 L{cx + 10} 82", 1.8)


@framed
def fc_cloche(d: Drawing):
    d.disc("glow", 100, 92, 60)
    _stars(d, [(44, 50, 5), (60, 34, 3), (158, 40, 4)])
    d.band("near", "M-30 150 H230")
    d.stroke("light", "M-30 156 H230", 2, line=False)
    d.shape("light", ellipse(88, 150, 56, 8))
    dome = "M38 146 C38 102 62 82 88 82 C114 82 138 102 138 146Z"
    d.shape("hero", dome, spot=True)
    d.stroke("light", "M52 126 C54 108 64 96 78 90", 3.2, line=False)
    d.shape("hero", rrect(30, 142, 116, 7, 3.5))
    d.limb("hero", "M88 82 L88.2 74", 4)
    d.shape("hero", ellipse(88, 72, 9, 5))
    _flute(d, 156, 148, 0.95, spot=False)
    # rose in a bud vase
    d.limb("near", "M34 114 Q30 100 34 86", 2.2, shadow=False)
    d.shape("pop", "M28 84 C26 76 30 72 34 72 C38 72 42 76 40 84 C38 88 30 88 28 84Z")
    d.stroke("dark", "M30 78 Q34 82 38 77", 1.2, line=False)


# ================================================================ LONG-HAUL FLIGHT
def _planform(d: Drawing, role="dark", lights=True):
    """Top-down airliner pointing up, centred on the origin."""
    d.shape(role, "M-4 -6 L-38 12 L-38 17 L-4 9Z M4 -6 L38 12 L38 17 L4 9Z", shadow=False)
    d.shape(role, "M-3 27 L-15 35 L-15 39 L-3 35Z M3 27 L15 35 L15 39 L3 35Z", shadow=False)
    d.shape(role, rrect(-5.5, -38, 11, 76, 5.5), shadow=False)
    d.shape(role, rrect(-22, 0, 5, 11, 2.5) + " " + rrect(17, 0, 5, 11, 2.5), shadow=False)
    if lights:
        d.marks("pop", circle(-38, 15, 2.2))
        d.marks("hero2", circle(38, 15, 2.2))


def lh_night(d: Drawing):
    _night(d)
    for x, y, r in [(34, 52, 3), (56, 30, 2.2), (162, 40, 2.6), (176, 112, 2), (28, 98, 2.4), (150, 22, 2)]:
        d.marks("light", _sparkle(x, y, r))
    d.disc("glow", 104, 88, 48)
    d.band("far", _puffs(150, (12, 16, 10, 15)))
    d.band("light", _puffs(168, (14, 10, 16, 12), -40))
    d.stroke("light", "M60 140 L82 116 M66 144 L88 120", 1.6, line=False)
    group(d, "translate(104 92) rotate(44)", lambda: _planform(d))


def lh_pillow(d: Drawing):
    d.disc("glow", 100, 104, 60)
    _stars(d, [(36, 56, 5), (166, 136, 4.5), (40, 148, 3.5), (164, 44, 4)], "pop")
    d.limb("dark", "M59 76 C59 26 141 26 141 76", 6)
    d.shape("dark", rrect(48, 64, 20, 32, 8))
    d.shape("dark", rrect(132, 64, 20, 32, 8))
    d.shape("hero2", rrect(64, 68, 6, 24, 3), shadow=False, spot=True)
    d.shape("hero2", rrect(130, 68, 6, 24, 3), shadow=False, spot=True)
    cx, cy, r1, r2 = 100, 126, 15, 43
    rm = (r1 + r2) / 2
    d.shape("hero", _annulus(cx, cy, r1, r2, -52, 232) + " " +
            circle(round(cx + rm * math.cos(math.radians(-52)), 1), round(cy + rm * math.sin(math.radians(-52)), 1), (r2 - r1) / 2) + " " +
            circle(round(cx + rm * math.cos(math.radians(232)), 1), round(cy + rm * math.sin(math.radians(232)), 1), (r2 - r1) / 2), spot=True)
    a, b = math.radians(-30), math.radians(210)
    d.stroke("mark", f"M{cx + rm * math.cos(a):.1f} {cy + rm * math.sin(a):.1f} A{rm} {rm} 0 1 1 {cx + rm * math.cos(b):.1f} {cy + rm * math.sin(b):.1f}",
             1.4, line=False)


@framed
def lh_screen(d: Drawing):
    d.band("sky2", "M-30 -30 H230", shadow=False, line=False)
    d.shape("hero", "M38 230 V44 C38 18 60 10 100 10 C140 10 162 18 162 44 V230Z")
    d.shape("dark", rrect(54, 34, 92, 70, 7))

    def scr():
        d.shape("mid", "M50 30 H150 V110 H50Z", shadow=False, line=False)
        d.shape("far", "M58 52 C66 42 84 44 88 54 C92 64 80 70 82 82 C84 94 70 98 62 90 C56 84 54 62 58 52Z "
                       "M110 44 C122 40 140 46 142 58 C138 70 126 66 120 74 C114 82 120 92 114 96 C106 98 104 80 106 68 C100 60 102 48 110 44Z",
                shadow=False)
        _dash(d, "M70 70 Q96 40 126 58", "light", 2.4, "1 5")
        d.marks("pop", circle(70, 70, 3))
        d.marks("pop", circle(126, 58, 3))

        def plane():
            d.shape("hero2", "M-9 0 C-9 -2 -6 -2 0 -2 L9 -2 C12 -2 13 -1 13 0 C13 1 12 2 9 2 L0 2 C-6 2 -9 2 -9 0Z "
                             "M1 -1 L-5 -10 L-1 -10 L7 -1Z M1 1 L-5 10 L-1 10 L7 1Z M-7 -1 L-11 -5 L-9 -5 L-4 -1Z", shadow=False, spot=True)
        group(d, "translate(94 50) rotate(-14)", plane)
    _clip(d, "lhscr", rrect(60, 40, 80, 58, 4), scr)
    d.shape("dark", rrect(90, 112, 20, 8, 3))
    d.shape("hero", rrect(50, 124, 100, 56, 8))
    d.stroke("mark", "M58 132 H142", 1.4, line=False)
    d.shape("dark", rrect(60, 186, 80, 6, 3), shadow=False)
    d.marks("light", circle(140, 108, 2) + circle(60, 108, 2))


# ================================================================ SLEEPER TRAIN
def _carriage(d: Drawing, x, w, y=100, h=30, spot=False):
    d.shape("hero", rrect(x, y, w, h, 6))
    d.shape("dark", f"M{x + 2} {y + 4} Q{x + 4} {y - 3} {x + 12} {y - 3} H{x + w - 12} Q{x + w - 4} {y - 3} {x + w - 2} {y + 4}Z", shadow=False)
    for i in range(int((w - 12) // 13)):
        d.shape("glow2", rrect(x + 7 + i * 13, y + 6, 9, 9, 2), shadow=False, spot=spot)
    d.stroke("hero2", f"M{x + 2} {y + h - 7} H{x + w - 2}", 1.8, line=False)
    for wx in (x + 10, x + 18, x + w - 18, x + w - 10):
        d.shape("dark", circle(wx, y + h + 1, 3.6), shadow=False)


def sl_night(d: Drawing):
    _night(d)
    d.disc("glow", 150, 48, 16)
    for x, y, r in [(40, 46, 2.6), (70, 28, 2), (110, 40, 2.4), (182, 80, 2), (24, 74, 2)]:
        d.marks("light", _sparkle(x, y, r))
    d.band("far", "M-30 108 L10 86 L44 102 L84 70 L120 96 L150 84 L230 104")
    # locomotive, facing left
    d.shape("hero2", "M10 130 V110 C10 102 16 99 26 99 H62 V130Z")
    d.shape("light", "M16 110 C17 105 20 104 26 104 H30 V113 H16Z", shadow=False)
    d.shape("glow2", circle(14, 122, 2.6), shadow=False)
    for wx in (20, 30, 50):
        d.shape("dark", circle(wx, 131, 3.6), shadow=False)
    _carriage(d, 64, 62, spot=True)
    _carriage(d, 128, 62)
    _carriage(d, 192, 62)
    d.band("mid", "M-30 134 H230")
    d.stroke("dark", "M-30 134 H230", 2.4)
    for x, s in [(18, 1.3), (40, 1.0), (164, 1.2), (186, 1.5)]:
        d.shape("near", _pine(x, 170, s), shadow=False)
    d.band("near", hills(168, 6, 10))


@framed
def sl_bunks(d: Drawing):
    d.band("far", "M-30 -30 H230", shadow=False, line=False)

    def view():
        d.shape("deep", "M40 70 H160 V130 H40Z", shadow=False, line=False)
        d.disc("glow", 118, 92, 7)
        d.marks("light", _sparkle(62, 90, 2) + _sparkle(84, 84, 1.6))
        d.shape("mid", "M40 116 L60 104 L78 112 L100 100 L120 110 L140 104 V130 H40Z", shadow=False, line=False)
    d.shape("light", rrect(42, 74, 94, 50, 9))
    _clip(d, "slwin", rrect(48, 80, 82, 38, 5), view)
    d.shape("pop", "M40 72 H54 C50 92 56 108 48 126 H40Z", spot=True)
    d.shape("pop", "M138 72 H124 C128 92 122 108 130 126 H138Z", spot=True)
    # upper bunk
    d.shape("light", rrect(24, 46, 124, 14, 7))
    d.shape("light", ellipse(40, 46, 12, 6))
    d.shape("hero2", "M76 44 C100 40 130 40 148 44 V60 H76Z", shadow=False)
    d.shape("dark", rrect(20, 58, 132, 7, 3))
    # lower bunk
    d.shape("light", rrect(22, 130, 150, 16, 8))
    d.shape("light", ellipse(42, 130, 14, 7))
    d.shape("hero", "M74 128 C104 122 150 122 172 128 V146 H74Z", shadow=False, spot=True)
    d.stroke("light", "M74 134 C104 128 150 128 172 134", 2, line=False)
    d.shape("dark", rrect(16, 144, 162, 9, 3))
    # ladder
    d.stroke("dark", "M150 62 L160 144 M164 62 L174 144", 3)
    for i in range(1, 5):
        y = 62 + i * 16.4
        x = 150 + (y - 62) * 10 / 82
        d.stroke("dark", f"M{x:.1f} {y:.1f} H{x + 14:.1f}", 2.6)


@framed
def sl_tea(d: Drawing):
    d.band("near", "M-30 -30 H230", shadow=False, line=False)

    def view():
        d.shape("deep", "M30 20 H170 V130 H30Z", shadow=False, line=False)
        d.disc("glow", 136, 52, 12)
        d.marks("light", _sparkle(60, 40, 2.4) + _sparkle(98, 30, 2) + _sparkle(160, 84, 2))
        d.shape("mid", "M30 96 L60 80 L92 92 L124 74 L170 92 V130 H30Z", shadow=False, line=False)
        for x in (40, 52, 150, 160):
            d.stroke("light", f"M{x} 130 V{70 + (x % 7) * 3}", 2.4, line=False)
    d.shape("light", rrect(32, 22, 136, 104, 12))
    _clip(d, "sltwin", rrect(38, 28, 124, 92, 8), view)
    d.shape("pop", "M26 18 H48 C40 54 50 92 40 132 H26Z", spot=True)
    d.shape("pop", "M174 18 H152 C160 54 150 92 160 132 H174Z", spot=True)
    d.band("ground", "M-30 132 H230")
    d.shape("dark", "M-30 132 H230 V138 H-30Z", shadow=False)
    # glass in a holder
    d.shape("light", "M80 64 H120 L117 112 H83Z")
    d.shape("hero2", "M82 74 H118 L116 110 H84Z", shadow=False)
    d.stroke("light", "M86 78 L88 104", 2, line=False)
    d.limb("dark", "M110 50 L104 104", 2.6, shadow=False)
    d.shape("glow2", ellipse(100, 74, 9, 3), shadow=False, line=False)
    d.limb("hero", "M118 104 C140 102 140 128 116 128", 5)
    d.shape("hero", "M78 98 H122 L118 144 H82Z", spot=True)
    d.stroke("mark", "M84 106 Q92 116 100 106 Q108 116 116 106 M86 126 Q93 118 100 126 Q107 118 114 126", 1.4, line=False)
    d.shape("hero", ellipse(100, 146, 26, 5))
    for x, y in [(144, 136), (154, 136), (149, 128)]:
        d.shape("light", rrect(x - 4.5, y - 4.5, 9, 9, 1.5))
    d.stroke("light", "M92 56 Q86 46 92 36 M104 52 Q98 42 104 32", 2.4, line=False)


# ================================================================ BULLET TRAIN
SHINKANSEN = {"hero": "#F4F2EC", "hero2": "#2E5AA8"}


def bt_headon(d: Drawing):
    d.disc("glow", 100, 96, 60)
    d.band("mid", "M-30 120 H14 V100 H30 V108 H44 V94 H56 V120 H144 V104 H156 V88 H170 V102 H186 V120 H230")
    d.band("near", "M-30 140 Q100 132 230 140")
    for i in range(6):
        t = (i / 5) ** 1.5
        y = 152 + t * 50
        hw = 22 + t * 52
        d.shape("dark", f"M{100 - hw:.1f} {y:.1f} H{100 + hw:.1f} V{y + 3 + t * 4:.1f} H{100 - hw:.1f}Z", shadow=False, line=False)
    d.stroke("mark", "M86 150 L52 230 M114 150 L148 230", 3)
    # catenary poles
    for x in (28, 172):
        _post(d, "dark", x, 52, 140, 4, shadow=False)
    d.stroke("dark", "M18 58 H60 M140 58 H182", 2.2)
    d.shape("hero", "M54 150 V96 C54 62 74 44 100 44 C126 44 146 62 146 96 V150Z")
    d.shape("dark", "M66 82 C70 62 84 54 100 54 C116 54 130 62 134 82 C124 90 76 90 66 82Z", shadow=False)
    d.stroke("light", "M76 72 C80 64 88 60 96 59", 2, line=False)
    d.stroke("light", "M100 92 C96 108 96 126 100 146", 1.4, line=False)
    d.shape("hero2", "M54 122 C78 130 122 130 146 122 V132 C122 140 78 140 54 132Z", shadow=False, spot=True)
    d.shape("glow2", ellipse(70, 110, 7, 4), shadow=False)
    d.shape("glow2", ellipse(130, 110, 7, 4), shadow=False)
    d.shape("dark", "M58 150 C62 142 138 142 142 150Z", shadow=False)


def _blossom(d: Drawing, x, y, r, role="pop", centre="light"):
    d.shape(role, " ".join(circle(round(x + r * 0.62 * math.cos(math.radians(a)), 1), round(y + r * 0.62 * math.sin(math.radians(a)), 1), r * 0.5)
                           for a in range(-90, 270, 72)), shadow=False, spot=True)
    d.marks(centre, circle(x, y, r * 0.28))


def bt_blossom(d: Drawing):
    d.disc("glow", 140, 70, 24)
    d.band("far", "M-30 112 L20 92 L52 104 L94 72 L132 100 L166 90 L230 108")
    d.shape("light", "M94 72 L104 80 L98 79 L94 83 L89 78 L84 80Z", shadow=False)
    # elevated line and train, nose right
    d.band("mid", "M-30 130 H230")
    for x in (10, 60, 110, 160):
        d.shape("near", rrect(x, 128, 8, 40, 2), shadow=False)
    d.shape("hero", "M-30 104 H118 C142 104 164 114 182 126 C184 128 182 130 178 130 H-30Z")
    for x in range(-24, 112, 14):
        d.marks("dark", rrect(x, 109, 8, 5, 2))
    d.shape("dark", "M130 108 C142 110 152 114 160 120 H146 C142 116 136 112 130 108Z", shadow=False)
    d.shape("hero2", "M-30 120 H164 C170 122 174 124 178 126 H-30Z", shadow=False, spot=True)
    d.shape("dark", "M-30 130 H230 V134 H-30Z", shadow=False)
    for y, x0, x1 in [(96, 140, 176), (112, 178, 196), (140, 120, 170)]:
        d.stroke("light", f"M{x0} {y} H{x1}", 2.2, line=False)
    d.band("near", hills(170, 6, 20))
    # cherry branch in the foreground
    d.limb("dark", "M-10 34 C26 44 56 40 92 22 M34 42 C44 54 46 64 42 76 M70 34 C80 40 92 42 104 40", 5, shadow=True)
    for x, y, r in [(92, 22, 9), (104, 40, 8), (42, 76, 8.5), (58, 42, 7), (18, 38, 7.5), (78, 30, 6.5), (36, 58, 6), (118, 34, 6)]:
        _blossom(d, x, y, r)
    for x, y in [(130, 56), (66, 92), (150, 46), (100, 82)]:
        d.shape("pop", ellipse(x, y, 3, 2), shadow=False, line=False)


@framed
def bt_platform(d: Drawing):
    d.disc("glow", 48, 92, 16)
    d.band("far", "M-30 108 H12 V86 H30 V100 H46 V80 H64 V108 H230")
    # train arriving, nose left
    d.shape("hero", "M230 72 H156 C120 72 88 88 64 112 C60 118 62 124 70 124 H230Z")
    d.shape("dark", "M118 78 C104 80 92 86 84 94 H104 C110 88 116 82 124 78Z", shadow=False)
    for x in range(140, 200, 16):
        d.marks("dark", rrect(x, 84, 10, 7, 2))
    d.shape("hero2", "M76 116 C94 112 150 110 230 110 V118 H70Z", shadow=False, spot=True)
    d.shape("glow2", ellipse(78, 112, 5, 2.6), shadow=False)
    # roof canopy
    d.shape("dark", "M-30 -30 H230 V34 H-30Z")
    d.shape("near", "M-30 34 H230 V40 H-30Z", shadow=False)
    _post(d, "dark", 30, 34, 150, 6)
    d.limb("dark", "M150 40 L150.2 50", 2.4, shadow=False)
    d.shape("dark", circle(150, 62, 12))
    d.shape("light", circle(150, 62, 9), shadow=False)
    d.stroke("dark", "M150 62 V56 M150 62 L155 64", 1.6)
    # platform
    d.band("ground", "M-30 128 H230")
    d.shape("hero2", "M-30 132 H230 V138 H-30Z", shadow=False, line=False)
    d.stroke("mark", "M-30 128 H230", 2.4)
    _person(d, 72, 172, 0.72)
    d.shape("pop", rrect(86, 140, 18, 26, 4), spot=True)
    d.stroke("dark", "M91 140 V134 H99 V140", 1.8)
    d.shape("dark", circle(89, 168, 2) + " " + circle(101, 168, 2), shadow=False)


# ================================================================ FUNICULAR
def _funicar(d: Drawing, x0, y0, n, w, h, k, body="hero", trim="hero2", heads=False, spot=True):
    """A stepped funicular car climbing to the right; (x0, y0) is its lower-back corner on the track."""
    yb = lambda x: y0 - k * (x - x0)
    xe = x0 + n * w
    p = f"M{x0} {yb(x0):.1f} L{xe} {yb(xe):.1f}"
    for i in range(n - 1, -1, -1):
        p += f" V{yb(x0 + (i + 1) * w) - h:.1f} H{x0 + i * w}"
    d.shape(body, p + "Z", spot=spot)
    for i in range(n):
        top = yb(x0 + (i + 1) * w) - h
        d.shape(trim, f"M{x0 + i * w} {top:.1f} H{x0 + (i + 1) * w} V{top + h * 0.12:.1f} H{x0 + i * w}Z", shadow=False)
        wx, ww, wy, wh = x0 + i * w + w * 0.14, w * 0.72, top + h * 0.22, h * 0.36
        d.shape("light", rrect(round(wx, 1), round(wy, 1), round(ww, 1), round(wh, 1), 2.5), shadow=False)
        if heads:
            d.marks("dark", circle(round(wx + ww * 0.32, 1), round(wy + wh * 0.72, 1), wh * 0.28) + " " +
                    circle(round(wx + ww * 0.72, 1), round(wy + wh * 0.68, 1), wh * 0.3))
    d.stroke(trim, f"M{x0 + 2} {yb(x0) - h * 0.16:.1f} L{xe - 2} {yb(xe) - h * 0.16:.1f}", 2.2, line=False)
    for i in range(n + 1):
        x = x0 + 4 + i * (n * w - 8) / n
        d.shape("dark", circle(round(x, 1), round(yb(x) + 2, 1), 3), shadow=False)


def fun_mountain(d: Drawing):
    d.disc("glow", 58, 58, 18)
    d.band("far", "M-30 104 L16 70 L50 92 L96 44 L140 86 L230 60")
    d.shape("light", "M96 44 L110 58 L103 56 L97 62 L90 55 L84 57Z", shadow=False)
    y = lambda x: 176 - 0.62 * (x - 10)
    d.band("near", f"M-30 {y(-30) + 6:.0f} L150 {y(150) + 6:.0f} Q170 {y(170):.0f} 230 {y(170):.0f}")
    for x, yy, s in [(24, 190, 1.0), (62, 172, 1.2), (110, 150, 0.9), (180, 150, 1.4)]:
        d.shape("deep", _pine(x, yy, s), shadow=False)
    # top station
    d.shape("hero2", f"M142 {y(150) - 10:.0f} V{y(150) - 30:.0f} L156 {y(150) - 40:.0f} L170 {y(150) - 30:.0f} V{y(150) - 10:.0f}Z")
    d.shape("dark", f"M139 {y(150) - 29:.0f} L156 {y(150) - 43:.0f} L173 {y(150) - 29:.0f}Z")
    d.stroke("dark", f"M-30 {y(-30):.1f} L150 {y(150):.1f}", 2.6)
    _funicar(d, 54, y(54) - 3, 3, 22, 28, 0.62)


@framed
def fun_street(d: Drawing):
    d.disc("glow", 152, 44, 14)
    k = 0.5
    y = lambda x: 176 - k * x
    roles = ["far", "light", "mid", "glow2", "far", "light"]
    for i, x in enumerate(range(-24, 200, 36)):
        base = y(x + 36) + 4
        top = base - 66 - (i % 2) * 10
        d.shape(roles[i % len(roles)], f"M{x} {base + 40} V{top} H{x + 36} V{base + 40}Z")
        d.shape("dark", f"M{x - 2} {top} H{x + 38} V{top + 4} H{x - 2}Z", shadow=False)
        for wy in (top + 12, top + 34):
            if wy < base - 16:
                d.shape("deep", rrect(x + 7, wy, 8, 13, 1.5) + " " + rrect(x + 21, wy, 8, 13, 1.5), shadow=False)
    d.stroke("dark", f"M-30 {y(-30) - 58:.1f} L230 {y(230) - 58:.1f}", 1.4)
    d.band("ground", f"M-30 {y(-30):.1f} L230 {y(230):.1f}")
    d.stroke("dark", f"M-30 {y(-30) + 6:.1f} L230 {y(230) + 6:.1f}", 2, line=False)
    _funicar(d, 40, y(40) + 2, 3, 30, 40, k, body="hero", trim="light", heads=True)
    d.stroke("dark", f"M100 {y(100) - 46:.1f} L104 {y(104) - 57:.1f}", 1.8)


def fun_close(d: Drawing):
    d.disc("glow", 150, 56, 18)
    d.band("far", hills(92, 12, 10))
    k = 0.36
    y = lambda x: 168 - k * (x - 10)
    d.band("mid", f"M-30 {y(-30) + 8:.0f} L230 {y(230) + 8:.0f}")
    for x, s in [(30, 1.1), (178, 1.0)]:
        d.shape("near", _pine(x, y(x) + 30, s), shadow=False)
    d.stroke("dark", f"M-30 {y(-30) + 2:.1f} L230 {y(230) + 2:.1f}", 2.6)
    d.stroke("dark", f"M180 {y(180) - 6:.1f} L230 {y(230) - 6:.1f}", 1.4)
    _funicar(d, 22, y(22), 4, 39, 48, k, heads=True)
    d.band("near", hills(186, 4, 10), line=False)


# ================================================================ RICKSHAW
def rk_cycle(d: Drawing):
    d.disc("glow", 64, 70, 28)
    d.band("far", "M-30 120 H10 V96 Q22 80 34 96 V120 H120 V100 H140 V86 H160 V120 H230")
    _bulbs(d, -10, 30, 210, 30, 24, 9, ["pop", "hero2", "light"])
    d.band("ground", "M-30 168 H230")
    # passenger seat and hood
    d.shape("pop", "M30 112 C26 74 48 54 82 56 L86 64 C62 68 52 84 54 112Z", spot=True)
    d.stroke("dark", "M38 104 C36 84 46 70 62 64 M46 108 C44 90 52 76 70 66", 1.4, line=False)
    d.shape("hero", "M34 108 H90 L94 136 H40Z")
    d.shape("hero2", rrect(42, 100, 46, 10, 5), shadow=False)
    d.limb("dark", "M66 150 L120 130 L152 152 M120 130 L122 110 M66 150 L94 136", 4)
    d.limb("dark", "M152 152 L144 104 L134 100", 3.5)
    d.shape("dark", rrect(112, 104, 20, 6, 3))
    # rider
    d.limb("dark", "M122 106 L138 120 L130 140", 6)
    d.shape("dark", "M116 108 C114 96 118 84 126 78 C132 74 138 80 136 88 C132 96 128 102 128 108Z")
    d.limb("dark", "M130 86 L140 100", 4.5)
    d.shape("dark", circle(132, 68, 7.5))
    d.shape("hero2", "M122 66 Q132 54 142 66Z", shadow=False)
    _wheel(d, 66, 150, 18)
    _wheel(d, 152, 152, 15)


@framed
def rk_pulled(d: Drawing):
    d.disc("glow", 100, 84, 50)
    for x, role in [(12, "mid"), (34, "near"), (160, "near"), (184, "mid"), (60, "mid"), (140, "mid")]:
        d.shape(role, rrect(x - 4, -10, 8, 190, 3), shadow=role == "near")
        d.stroke("deep", f"M{x - 4} 40 H{x + 4} M{x - 4} 90 H{x + 4} M{x - 4} 140 H{x + 4}", 1.2, line=False)
    for x, y, a in [(16, 52, -30), (36, 74, 30), (164, 48, 30), (186, 80, -30), (140, 60, -30), (60, 46, 30)]:
        def leaf(x=x, y=y, a=a):
            d.shape("near", "M0 0 C6 -4 16 -4 22 0 C16 4 6 4 0 0Z", shadow=False)
        group(d, f"translate({x} {y}) rotate({a})", leaf)
    d.band("ground", "M-30 168 H230")
    # rickshaw, facing right
    d.shape("pop", "M28 112 C24 74 46 56 80 58 L84 66 C60 70 50 86 52 112Z", spot=True)
    d.shape("hero", "M32 106 H88 Q94 106 94 112 V130 H40 Q32 130 32 122Z")
    d.shape("hero2", rrect(38, 98, 44, 10, 5), shadow=False)
    d.limb("dark", "M84 126 L158 138", 3.6)
    d.stroke("dark", circle(62, 138, 26), 3.2)
    d.stroke("dark", "M62 112 V164 M36 138 H88 M44 120 L80 156 M80 120 L44 156", 1.2)
    d.shape("dark", circle(62, 138, 4))
    # runner holding the shafts
    _person(d, 154, 172, 0.8)
    d.limb("dark", "M150 122 L156 138", 4)
    d.shape("hero2", "M136 102 L154 86 L172 102 Q154 106 136 102Z", spot=True)


@framed
def rk_painted(d: Drawing):
    d.disc("glow", 100, 80, 52)
    d.band("far", "M-30 112 H18 V82 H40 V96 H58 V112 H142 V90 H160 V74 H182 V112 H230")
    d.band("ground", "M-30 160 Q100 152 230 160")
    # wheels edge-on and axle
    d.shape("dark", rrect(40, 116, 12, 54, 6))
    d.shape("dark", rrect(148, 116, 12, 54, 6))
    d.stroke("dark", "M52 146 H148", 3)
    # hood
    d.shape("pop", "M44 102 C44 46 72 30 100 30 C128 30 156 46 156 102Z", spot=True)
    d.stroke("dark", "M62 100 C62 62 78 42 100 38 M138 100 C138 62 122 42 100 38 M100 38 V100", 1.4, line=False)
    for i in range(10):
        x = 48 + i * 11.6
        d.shape("hero2", f"M{x - 4:.1f} 100 L{x + 4:.1f} 100 L{x:.1f} 110Z", shadow=False)
    # painted back panel
    d.shape("hero2", rrect(56, 108, 88, 34, 4))
    d.shape("light", rrect(62, 113, 76, 24, 3), shadow=False)
    for i, a in enumerate(range(0, 360, 60)):
        d.shape("pop", ellipse(round(100 + 7 * math.cos(math.radians(a)), 1), round(125 + 7 * math.sin(math.radians(a)), 1), 4.5, 4.5), shadow=False)
    d.marks("hero2", circle(100, 125, 3.5))
    _leaf = lambda x, a: group(d, f"translate({x} 125) rotate({a})", lambda: d.shape("near", "M0 0 C6 -5 16 -5 22 0 C16 5 6 5 0 0Z", shadow=False))
    _leaf(86, 180)
    _leaf(114, 0)
    d.shape("dark", rrect(70, 142, 60, 22, 3))
    d.shape("pop", circle(60, 150, 4) + " " + circle(140, 150, 4), shadow=False)
    d.marks("hero2", _heart(100, 152, 0.5))


# ================================================================ CANAL BOAT
@framed
def cb_narrowboat(d: Drawing):
    d.disc("glow", 152, 52, 16)
    d.shape("light", cloud(26, 52, 0.8))
    d.band("far", hills(104, 10, 10))
    for x, r in [(30, 16), (56, 12), (176, 14)]:
        d.shape("near", circle(x, 104 - r * 0.6, r), shadow=False)
    d.band("ground", "M-30 114 H230")
    d.band("mid", "M-30 126 H230")
    d.shape("light", cloud(150, 66, 0.55))
    d.shape("light", cloud(160, 54, 0.4), shadow=False)
    # boat, bow right
    d.shape("dark", rrect(140, 80, 7, 20, 2))
    d.shape("hero2", rrect(139, 84, 9, 3, 1), shadow=False)
    d.shape("hero", "M30 124 V102 Q30 98 34 98 H164 Q168 98 168 102 V124Z")
    d.shape("hero2", rrect(26, 94, 146, 6, 3), shadow=False)
    for x in (58, 78, 98, 118):
        d.shape("light", circle(x, 110, 4.5), shadow=False)
        d.stroke("hero2", circle(x, 110, 4.5), 1.4, line=False)
    d.shape("pop", rrect(132, 102, 26, 18, 3), shadow=False, spot=True)
    d.shape("hero2", "M145 104 L155 111 L145 118 L135 111Z", shadow=False)
    d.shape("dark", rrect(34, 102, 12, 22, 2), shadow=False)
    d.shape("pop", rrect(64, 88, 10, 7, 2) + " " + rrect(96, 88, 10, 7, 2), shadow=False)
    d.marks("near", circle(66, 86, 3) + circle(72, 85, 3) + circle(98, 86, 3) + circle(104, 85, 3))
    d.shape("dark", "M16 124 H178 L190 116 L188 132 Q184 140 172 140 H24 Q16 140 16 134Z")
    d.shape("pop", "M18 124 H178 L182 121 L183 126 H18Z", shadow=False)
    d.limb("dark", "M24 120 Q14 106 22 98 L8 96", 3)
    d.band("near", waves(150, 2, 30))
    d.stroke("light", "M40 158 H70 M110 162 H150 M60 172 H90", 2, line=False)


@framed
def cb_lock(d: Drawing):
    d.disc("glow", 100, 54, 22)
    d.band("far", hills(70, 8))
    # lock walls and coping
    d.shape("near", "M-30 62 H64 V118 L24 200 H-30Z")
    d.shape("near", "M230 62 H136 V118 L176 200 H230Z")
    d.stroke("deep", "M-30 84 H62 M-30 106 H58 M-30 128 H48 M-30 150 H38 M230 84 H138 M230 106 H142 M230 128 H152 M230 150 H162", 1.2, line=False)
    d.shape("light", "M-30 58 H66 V64 H-30Z M230 58 H134 V64 H230Z", shadow=False)
    # gates
    d.shape("dark", "M64 62 H99 V122 H64Z")
    d.shape("dark", "M101 62 H136 V122 H101Z")
    d.stroke("ground", "M68 76 H96 M68 94 H96 M68 110 H96 M104 76 H132 M104 94 H132 M104 110 H132 M68 76 L96 110 M132 76 L104 110", 1.6)
    # balance beams
    d.limb("dark", "M66 58 L10 86", 6)
    d.limb("dark", "M134 58 L190 86", 6)
    d.limb("light", "M18 82 L10 86 M182 82 L190 86", 6.2, shadow=False)
    # water and boat
    d.shape("mid", "M64 120 H136 L176 200 H24Z")
    d.stroke("light", "M60 140 H76 M124 146 H142", 2, line=False)
    d.shape("hero2", rrect(74, 124, 52, 6, 3))
    d.shape("hero", rrect(78, 128, 44, 28, 4), spot=True)
    d.shape("light", rrect(86, 134, 28, 12, 3), shadow=False)
    d.shape("dark", "M72 156 H128 L120 192 H80Z")
    d.shape("pop", "M74 162 H126 L125 166 H75Z", shadow=False)
    d.shape("ground", ellipse(100, 186, 9, 7))
    d.stroke("dark", "M93 184 Q100 180 107 184 M93 189 Q100 185 107 189", 1, line=False)


def _gable(x, w, base, top, kind):
    """A canal house front from `base` up to `top`, with a gable of the given kind."""
    m = x + w / 2
    if kind == "step":
        s = w / 6
        return (f"M{x} {base} V{top} H{x + s} V{top - 7} H{x + 2 * s} V{top - 14} H{x + 4 * s} V{top - 7} H{x + 5 * s} V{top} "
                f"H{x + w} V{base}Z").replace(f"V{top - 14} H{x + 4 * s}", f"V{top - 14} H{x + 4 * s}")
    if kind == "bell":
        return (f"M{x} {base} V{top} C{x + 2} {top - 6} {x + w * 0.3} {top - 6} {x + w * 0.3} {top - 14} "
                f"Q{m} {top - 22} {x + w * 0.7} {top - 14} C{x + w * 0.7} {top - 6} {x + w - 2} {top - 6} {x + w} {top} V{base}Z")
    return f"M{x} {base} V{top} L{m} {top - 16} L{x + w} {top} V{base}Z"


def cb_city(d: Drawing):
    d.disc("glow", 160, 44, 14)
    houses = [(-6, 30, 52, "near", "bell"), (24, 28, 44, "hero2", "step"), (52, 32, 58, "deep", "neck"),
              (84, 30, 48, "far", "bell"), (114, 30, 56, "near", "step"), (144, 28, 46, "hero2", "neck"), (172, 34, 54, "deep", "bell")]
    for x, w, top, role, kind in houses:
        d.shape(role, _gable(x, w, 124, top + 6, kind))
        for wy in (top + 20, top + 40, top + 60):
            if wy < 112:
                d.shape("light", rrect(x + 5, wy, w / 2 - 7, 12, 1.5) + " " + rrect(x + w / 2 + 2, wy, w / 2 - 7, 12, 1.5), shadow=False)
        d.stroke("dark", f"M{x + w / 2} {top + 6} V{top + 12}", 1.6, line=False)
    d.shape("dark", "M-30 118 H230 V126 H-30Z")
    d.band("mid", "M-30 126 H230")
    d.stroke("light", "M20 156 H48 M140 160 H172 M74 172 H104", 2, line=False)
    # glass-roofed tour boat
    d.shape("light", "M44 132 Q46 118 62 116 H150 Q164 118 166 132Z")
    d.stroke("dark", "M66 117 V132 M86 116 V132 M106 116 V132 M126 116 V132 M146 117 V132", 1.4)
    d.shape("hero", "M30 132 H172 Q176 132 174 138 L168 148 H38 L28 138 Q26 132 30 132Z", spot=True)
    d.shape("hero2", "M32 138 H172 L170 142 H34Z", shadow=False)


# ================================================================ HITCHHIKING
def hh_thumb(d: Drawing):
    d.disc("glow", 140, 72, 22)
    d.band("far", "M-30 112 L20 92 L60 106 L104 80 L150 104 L230 96")
    d.band("ground", "M-30 120 H230")
    d.shape("dark", "M44 120 H56 L130 230 H-30 V196Z", shadow=False)
    _dash(d, "M50 124 L-6 216", "light", 3, "8 9", line=False)
    _post(d, "dark", 168, 98, 160, 4)
    d.shape("hero2", "M168 76 L184 92 L168 108 L152 92Z", spot=True)
    d.shape("dark", "M162 92 L168 86 L174 92 M168 86 V100", shadow=False, line=False)
    # hand
    d.shape("hero", rrect(78, 138, 46, 80, 6))
    d.shape("hero2", rrect(76, 132, 50, 12, 5), shadow=False, spot=True)
    d.shape("dark", rrect(74, 96, 52, 42, 14))
    d.shape("dark", "M78 106 C74 88 76 66 82 56 C86 48 96 50 96 60 C96 70 94 86 96 100Z")
    d.stroke("light", "M104 108 H124 M104 118 H124 M102 128 H122", 2, line=False)
    d.stroke("light", "M86 64 C84 72 84 80 86 88", 1.6, line=False)


def hh_roadside(d: Drawing):
    d.disc("glow", 150, 64, 20)
    d.band("far", "M-30 100 L30 80 L60 92 L96 70 L132 96 L230 90")
    d.band("ground", "M-30 112 H230")
    d.shape("dark", "M118 112 H126 L230 200 V230 H40Z", shadow=False)
    _dash(d, "M123 116 L118 230", "light", 3, "8 9", line=False)
    d.shape("hero2", rrect(116, 104, 10, 6, 2), shadow=False)
    d.shape("light", rrect(118, 105, 6, 2.5, 1), shadow=False)
    # cactus
    d.limb("near", "M178 128 V96 M178 112 Q186 112 186 102 M178 106 Q170 106 170 98", 6)
    # hitchhiker, facing right, thumb out
    d.limb("dark", "M60 168 L62 140 M70 168 L68 140", 6.5)
    d.shape("hero", rrect(36, 94, 22, 40, 7), spot=True)
    d.shape("hero2", rrect(34, 88, 26, 10, 5), shadow=False)
    d.shape("dark", "M54 142 V112 C54 102 60 98 66 98 C72 98 78 102 78 112 V142Z")
    d.limb("dark", "M72 106 L96 114", 5)
    d.shape("dark", rrect(94, 108, 8, 10, 3.5))
    d.limb("dark", "M98 109 L99.5 101", 3.4, shadow=False)
    d.shape("dark", circle(67, 86, 8.5))
    d.shape("pop", "M57 84 Q67 70 77 84 H82 V87 H57Z", shadow=False)


def hh_pickup(d: Drawing):
    d.disc("glow", 140, 60, 20)
    d.band("far", "M-30 104 H10 L22 82 H44 L54 104 H120 L132 90 H152 L160 104 H230")
    d.band("ground", "M-30 128 Q100 120 230 128")
    d.shape("light", cloud(-14, 140, 1.2))
    d.shape("light", cloud(6, 124, 0.8))
    # riders in the bed
    d.shape("pop", rrect(40, 88, 22, 28, 6), spot=True)
    d.stroke("dark", "M44 96 H58", 1.4)
    d.shape("dark", "M70 116 V96 C70 88 76 84 82 84 C88 84 94 88 94 96 V116Z")
    d.shape("dark", circle(82, 74, 8))
    d.limb("dark", "M90 92 L104 76", 4.5)
    d.shape("hero2", rrect(96, 100, 18, 16, 4))
    # pickup, facing right
    d.shape("hero", "M28 114 H118 V96 Q118 90 124 90 H146 Q152 90 156 98 L164 112 H178 Q186 112 186 120 V136 H28Z")
    d.shape("light", "M128 96 H144 Q148 96 150 100 L156 112 H128Z", shadow=False)
    d.stroke("mark", "M116 114 V136 M28 120 H116", 1.6, line=False)
    d.shape("glow2", rrect(180, 116, 6, 6, 2), shadow=False)
    d.shape("pop", rrect(26, 118, 4, 6, 1.5), shadow=False)
    for x in (58, 154):
        d.marks("dark", f"M{x - 17} 136 A17 17 0 0 1 {x + 17} 136Z")
        _wheel(d, x, 138, 13)
    d.band("deep", hills(170, 4, 20), line=False)


# ================================================================ BUS JOURNEY
@framed
def bus_mountain(d: Drawing):
    d.disc("glow", 56, 50, 16)
    d.band("far", "M-30 96 L24 56 L60 80 L104 34 L150 76 L230 50")
    d.shape("light", "M104 34 L116 48 L109 46 L104 52 L97 45 L92 47Z", shadow=False)
    d.band("mid", "M-30 112 L60 88 L120 96 L230 80")
    d.stroke("ground", "M200 86 L70 100 L150 108 L20 122", 4.5)
    d.stroke("light", "M200 86 L70 100 L150 108 L20 122", 1, line=False)
    d.band("near", "M-30 130 Q100 118 230 128")
    d.band("dark", "M-30 156 H230")
    d.stroke("light", "M-30 166 H10 M30 166 H70 M90 166 H130 M150 166 H190", 2.4, line=False)
    # coach, facing right
    d.shape("hero", "M30 100 Q30 92 38 92 H158 Q168 92 172 104 L176 140 Q176 148 168 148 H38 Q30 148 30 140Z")
    d.shape("dark", "M34 100 H156 L162 122 H34Z", shadow=False)
    for x in range(44, 150, 22):
        d.stroke("light", f"M{x} 118 L{x + 10} 104", 2, line=False)
    d.shape("hero2", "M30 128 H175 V134 H30Z", shadow=False, spot=True)
    d.shape("glow2", rrect(168, 136, 8, 5, 2), shadow=False)
    d.stroke("mark", "M140 122 V146", 1.4, line=False)
    for x in (60, 146):
        d.marks("dark", f"M{x - 15} 148 A15 15 0 0 1 {x + 15} 148Z")
        _wheel(d, x, 149, 12)


@framed
def bus_painted(d: Drawing):
    d.disc("glow", 100, 80, 50)
    _palm(d, 22, 150, 1.0, "near", 6)
    _palm(d, 180, 150, 0.9, "near", -6)
    d.band("ground", "M-30 152 Q100 146 230 152")
    # roof rack and luggage
    d.shape("pop", rrect(34, 58, 30, 18, 4), spot=True)
    d.shape("hero2", rrect(66, 62, 22, 14, 3))
    d.shape("light", ellipse(104, 68, 14, 8))
    d.shape("near", rrect(118, 56, 22, 20, 3))
    d.stroke("dark", "M118 66 H140 M129 56 V76", 1.4)
    d.stroke("dark", "M28 76 H146 M32 76 V82 M90 76 V82 M144 76 V82", 2.4)
    # bus, facing right
    d.shape("hero", "M24 88 Q24 80 32 80 H140 Q148 80 148 88 V104 H170 Q182 104 182 116 V140 H24Z")
    d.shape("light", "M150 88 H142 V104 H156Z", shadow=False)
    for x in range(32, 140, 18):
        d.shape("light", rrect(x, 88, 13, 15, 2), shadow=False)
    d.shape("pop", "M24 110 H182 V116 H24Z", shadow=False, spot=True)
    d.shape("hero2", "M24 116 H182 V122 H24Z", shadow=False)
    zig = "M24 128 " + " ".join(f"L{x + 6} {124 if i % 2 == 0 else 132}" for i, x in enumerate(range(24, 176, 6))) + " L182 128"
    d.stroke("light", zig, 1.6, line=False)
    d.shape("glow2", rrect(176, 118, 6, 6, 2), shadow=False)
    d.shape("dark", rrect(176, 136, 10, 6, 3), shadow=False)
    for x in (52, 150):
        d.marks("dark", f"M{x - 16} 140 A16 16 0 0 1 {x + 16} 140Z")
        _wheel(d, x, 142, 13)


def bus_stop(d: Drawing):
    d.disc("glow", 150, 60, 22)
    d.band("far", hills(108, 10, 20))
    d.band("ground", "M-30 140 H230")
    d.band("dark", "M-30 156 H230")
    d.stroke("light", "M-30 168 H20 M44 168 H94 M118 168 H168 M192 168 H230", 2.4, line=False)
    # shelter
    _post(d, "dark", 104, 70, 142, 4)
    _post(d, "dark", 168, 70, 142, 4)
    d.shape("far", rrect(106, 76, 60, 44, 3), line=False)
    d.shape("hero2", "M96 64 H176 L172 74 H100Z", spot=True)
    d.shape("dark", rrect(108, 120, 56, 6, 3))
    d.limb("dark", "M114 126 V140 M158 126 V140", 3, shadow=False)
    # stop sign
    _post(d, "dark", 64, 52, 146, 5)
    d.shape("hero", circle(64, 50, 20), spot=True)
    d.shape("light", circle(64, 50, 15), shadow=False)
    d.shape("hero", rrect(54, 40, 20, 18, 4), shadow=False)
    d.shape("light", rrect(57, 43, 14, 7, 1.5), shadow=False)
    d.marks("dark", circle(58, 59, 2.4) + circle(70, 59, 2.4))
    # suitcase
    d.shape("pop", rrect(74, 112, 24, 32, 4))
    d.stroke("dark", "M80 112 V104 H92 V112", 2)
    d.stroke("mark", "M80 116 V140 M92 116 V140", 1.4, line=False)
    d.shape("dark", circle(78, 146, 2.2) + " " + circle(94, 146, 2.2), shadow=False)


# ================================================================ CONCEPTS
SILVER = {"hero": "#C9CED6", "mark": "#8D96A6"}
TEA = {"hero": "#C9CED6", "hero2": "#C8702A", "mark": "#7D8696"}
LISBON = {"hero": "#F5C343"}
BLOSSOM = {"pop": "#F29CB7", **SHINKANSEN}

CONCEPTS = [
    Concept("firstclass-seat", "first-class", "Big seat by the window", fc_seat,
            checks=[("hero", "far"), ("hero", "mid"), ("light", "far")], fixes={"hero": ["deep", "near", "pop"]}),
    Concept("firstclass-sleep-mask", "first-class", "Sleep mask & slippers", fc_mask,
            checks=[("hero", "glow"), ("light", "glow"), ("hero", "sky")], fixes={"glow": ["far", "mid", "near"]}),
    Concept("firstclass-cloche", "first-class", "Silver service", fc_cloche, overrides=SILVER,
            checks=[("hero", "glow"), ("hero", "near"), ("light", "glow")], fixes={"glow": ["near", "mid", "deep"], "near": ["deep", "dark"]}),
    Concept("longhaul-night-flight", "long-haul-flight", "Night flight", lh_night,
            checks=[("dark", "glow"), ("glow", "deep"), ("far", "deep"), ("light", "far")], fixes={"far": ["mid", "near"]}),
    Concept("longhaul-neck-pillow", "long-haul-flight", "Neck pillow & headphones", lh_pillow,
            checks=[("hero", "glow"), ("dark", "glow"), ("pop", "sky"), ("pop", "glow")], fixes={"glow": ["far", "mid"], "hero": ["pop", "deep"]}),
    Concept("longhaul-seatback-map", "long-haul-flight", "Seatback flight map", lh_screen,
            checks=[("hero", "sky2"), ("far", "mid"), ("dark", "hero")], fixes={"hero": ["deep", "near", "pop"], "far": ["light", "glow2"]}),
    Concept("sleeper-night-train", "sleeper-train", "Night train", sl_night,
            checks=[("hero", "far"), ("hero", "deep"), ("glow2", "hero"), ("far", "deep"), ("hero2", "far")],
            fixes={"far": ["mid", "near"], "hero": ["pop", "light"]}),
    Concept("sleeper-bunks", "sleeper-train", "Bunks by the window", sl_bunks,
            checks=[("light", "far"), ("dark", "far"), ("hero", "light")], fixes={"far": ["mid", "sky2"]}),
    Concept("sleeper-tea-glass", "sleeper-train", "Tea by the window", sl_tea, overrides=TEA,
            checks=[("hero", "ground"), ("light", "deep"), ("pop", "near"), ("hero", "deep")], fixes={"ground": ["near", "mid"], "near": ["mid", "far"]}),
    Concept("bullet-head-on", "bullet-train", "Head-on", bt_headon, overrides=SHINKANSEN,
            checks=[("hero", "glow"), ("hero", "near"), ("hero", "mid")], fixes={"glow": ["near", "mid", "deep"]}),
    Concept("bullet-blossom", "bullet-train", "Past the cherry blossom", bt_blossom, overrides=BLOSSOM,
            checks=[("hero", "mid"), ("hero", "far"), ("pop", "sky"), ("pop", "far")], fixes={"far": ["mid", "near"], "mid": ["near", "deep"]}),
    Concept("bullet-platform", "bullet-train", "At the platform", bt_platform, overrides=SHINKANSEN,
            checks=[("hero", "sky"), ("hero", "far"), ("dark", "ground"), ("pop", "ground")], fixes={"sky": ["sky2", "far"], "far": ["mid", "near"]}),
    Concept("funicular-mountain", "funicular", "Up the mountain", fun_mountain,
            checks=[("hero", "near"), ("hero", "far"), ("hero", "sky")], fixes={"hero": ["pop", "hero2", "light"]}),
    Concept("funicular-street", "funicular", "Steep city street", fun_street, overrides=LISBON,
            checks=[("hero", "far"), ("hero", "mid"), ("hero", "ground"), ("light", "sky")], fixes={"far": ["near", "deep"], "ground": ["near", "deep"]}),
    Concept("funicular-carriage", "funicular", "Stepped carriage", fun_close,
            checks=[("hero", "mid"), ("hero", "far"), ("hero", "sky")], fixes={"hero": ["pop", "hero2"]}),
    Concept("rickshaw-cycle", "rickshaw", "Cycle rickshaw", rk_cycle,
            checks=[("dark", "glow"), ("dark", "sky"), ("pop", "glow"), ("hero", "ground")], fixes={"glow": ["far", "glow2"], "hero": ["deep", "near"]}),
    Concept("rickshaw-pulled", "rickshaw", "Pulled rickshaw", rk_pulled,
            checks=[("dark", "glow"), ("pop", "glow"), ("hero", "glow"), ("dark", "ground")], fixes={"glow": ["glow2", "far", "light"]}),
    Concept("rickshaw-painted", "rickshaw", "Painted rickshaw", rk_painted,
            checks=[("pop", "glow"), ("pop", "sky"), ("hero2", "pop")], fixes={"glow": ["far", "mid", "glow2"], "hero2": ["light", "glow2"]}),
    Concept("canalboat-narrowboat", "canal-boat", "Narrowboat", cb_narrowboat,
            checks=[("hero", "mid"), ("hero", "ground"), ("dark", "mid"), ("hero", "near")], fixes={"hero": ["near", "deep", "pop"]}),
    Concept("canalboat-lock", "canal-boat", "Through the lock", cb_lock,
            checks=[("dark", "near"), ("dark", "sky"), ("hero", "mid"), ("near", "sky")], fixes={"near": ["mid", "far"]}),
    Concept("canalboat-city", "canal-boat", "City canal", cb_city,
            checks=[("hero", "mid"), ("near", "sky"), ("far", "sky"), ("light", "mid")], fixes={"far": ["mid", "pop"]}),
    Concept("hitchhike-thumb", "hitchhiking", "Thumbs up", hh_thumb,
            checks=[("dark", "glow"), ("dark", "ground"), ("dark", "sky"), ("hero", "ground")], fixes={"hero": ["pop", "near"]}),
    Concept("hitchhike-roadside", "hitchhiking", "On the roadside", hh_roadside,
            checks=[("dark", "ground"), ("dark", "sky"), ("hero", "ground"), ("hero", "dark")], fixes={"hero": ["pop", "near"]}),
    Concept("hitchhike-pickup", "hitchhiking", "In the back of a pickup", hh_pickup,
            checks=[("hero", "ground"), ("hero", "sky"), ("dark", "sky"), ("pop", "sky")], fixes={"hero": ["pop", "near", "deep"]}),
    Concept("bus-mountain-road", "bus-journey", "Coach on the pass", bus_mountain,
            checks=[("hero", "near"), ("hero", "mid"), ("hero", "dark")], fixes={"hero": ["pop", "hero2", "light"]}),
    Concept("bus-painted", "bus-journey", "Painted bus", bus_painted,
            checks=[("hero", "glow"), ("hero", "sky"), ("pop", "hero"), ("hero2", "hero")], fixes={"glow": ["far", "glow2"], "hero2": ["light", "glow2"]}),
    Concept("bus-stop", "bus-journey", "Bus stop", bus_stop,
            checks=[("hero", "sky"), ("hero", "glow"), ("pop", "ground"), ("hero2", "sky")], fixes={"glow": ["far", "glow2"], "hero2": ["near", "pop"]}),
]
