"""Basics: nature. One clear, iconic, generic sticker for each everyday nature subject."""
import math

from _common import Concept, Drawing, cloud, fish, circle, ellipse, waves, hills, rrect, group  # noqa: F401

_uid = [0]


# ================================================================ private helpers (copied from nature_b.py & co)
def _id(prefix):
    _uid[0] += 1
    return f"{prefix}{_uid[0]}"


def clipped(d: Drawing, path: str, fn):
    """Draw fn() clipped to `path`."""
    cid = _id("bnatclip")
    tag = f'<clipPath id="{cid}"><path d="{path}"/></clipPath><g clip-path="url(#{cid})">'
    d.raw(tag, tag)
    fn()
    d.raw("</g>", "</g>")


def pt(x, y):
    return f"{x:.1f} {y:.1f}"


def scallop(cx, cy, r, n=12, bump=0.22, rot=0.0, ry=None):
    """A bumpy circle (or ellipse): tree crowns, clouds, flower heads."""
    ry = r if ry is None else ry
    pts = []
    for i in range(n + 1):
        a = rot + 2 * math.pi * i / n
        pts.append((cx + r * math.cos(a), cy + ry * math.sin(a)))
    s = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(n):
        a = rot + 2 * math.pi * (i + 0.5) / n
        qx, qy = cx + r * (1 + bump * 2) * math.cos(a), cy + ry * (1 + bump * 2) * math.sin(a)
        s += f" Q{qx:.1f} {qy:.1f} {pts[i + 1][0]:.1f} {pts[i + 1][1]:.1f}"
    return s + "Z"


def leaf(x, y, length, width, angle):
    """A pointed leaf from (x, y) pointing at `angle` degrees (0 = right, -90 = up)."""
    a = math.radians(angle)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    tx, ty = x + ux * length, y + uy * length
    c1 = (x + ux * length * 0.35 + px * width, y + uy * length * 0.35 + py * width)
    c2 = (x + ux * length * 0.35 - px * width, y + uy * length * 0.35 - py * width)
    return (f"M{x:.1f} {y:.1f} Q{c1[0]:.1f} {c1[1]:.1f} {tx:.1f} {ty:.1f} "
            f"Q{c2[0]:.1f} {c2[1]:.1f} {x:.1f} {y:.1f}Z")


def frond(x, y, ang, length, droop, w=0.22) -> str:
    """A palm leaf from (x, y) at angle ang (degrees), drooping by `droop`."""
    a = math.radians(ang)
    ex, ey = x + length * math.cos(a), y + length * math.sin(a) + droop
    mx, my = (x + ex) / 2, (y + ey) / 2 - droop * .6
    nx, ny = -(ey - y), ex - x
    k = w / 2
    return (f"M{x:.1f} {y:.1f} Q{mx + nx * k:.1f} {my + ny * k:.1f} {ex:.1f} {ey:.1f} "
            f"Q{mx - nx * k * .3:.1f} {my - ny * k * .3:.1f} {x:.1f} {y:.1f}Z")


def frond_rib(x, y, ang, length, droop) -> str:
    a = math.radians(ang)
    ex, ey = x + length * math.cos(a), y + length * math.sin(a) + droop
    mx, my = (x + ex) / 2, (y + ey) / 2 - droop * .6
    return f"M{x:.1f} {y:.1f} Q{mx:.1f} {my:.1f} {ex:.1f} {ey:.1f}"


def birds(d: Drawing, pts, role="dark"):
    s = " ".join(f"M{x} {y} q{3 * k} {-3 * k} {6 * k} 0 q{3 * k} {-3 * k} {6 * k} 0" for x, y, k in pts)
    d.stroke(role, s, 1.8)


def grass(d: Drawing, x0, x1, y, h=12, role="near", step=16, line=False):
    x, i = x0, 0
    while x < x1:
        k = h * (0.75 + 0.25 * ((i * 5) % 3) / 2)
        d.shape(role, f"M{x} {y} L{x + 2} {y - k * 0.7} L{x + 4} {y - 2} L{x + 6} {y - k} L{x + 8} {y - 2} "
                      f"L{x + 10} {y - k * 0.6} L{x + 12} {y}Z", shadow=False, line=line)
        x += step
        i += 1


def pine(d: Drawing, x, y, h, role="near", shadow=True, line=True, spot=False):
    w = h * 0.36
    d.shape(role, f"M{x} {y - h} L{x + w * 0.6} {y - h * 0.62} L{x + w * 0.35} {y - h * 0.62} L{x + w * 0.85} {y - h * 0.3} "
                  f"L{x + w * 0.5} {y - h * 0.3} L{x + w} {y - h * 0.06} L{x - w} {y - h * 0.06} L{x - w * 0.5} {y - h * 0.3} "
                  f"L{x - w * 0.85} {y - h * 0.3} L{x - w * 0.35} {y - h * 0.62} L{x - w * 0.6} {y - h * 0.62}Z",
            shadow=shadow, line=line, spot=spot)


def sparkle(x, y, r) -> str:
    """A four-point twinkle star."""
    k = r * 0.22
    return (f"M{x} {y - r} Q{x + k} {y - k} {x + r} {y} Q{x + k} {y + k} {x} {y + r} "
            f"Q{x - k} {y + k} {x - r} {y} Q{x - k} {y - k} {x} {y - r}Z")


def crescent(cx, cy, r, k=None) -> str:
    """Crescent opening to the right."""
    k = r * .8 if k is None else k
    hy = math.sqrt(r * r - k * k / 4)
    x = cx + k / 2
    return (f"M{x:.2f} {cy - hy:.2f} A{r} {r} 0 1 0 {x:.2f} {cy + hy:.2f} "
            f"A{r} {r} 0 0 1 {x:.2f} {cy - hy:.2f}Z")


def star5(x, y, r, r2=None, rot=-90) -> str:
    r2 = r * 0.45 if r2 is None else r2
    pts = []
    for i in range(10):
        a = math.radians(rot + 36 * i)
        rr = r if i % 2 == 0 else r2
        pts.append(pt(x + rr * math.cos(a), y + rr * math.sin(a)))
    return "M" + " L".join(pts) + "Z"


def lilypad(d: Drawing, x, y, r, rot=0, spot=False, role="pad", role2="pad2"):
    notch = math.radians(rot)
    a1, a2 = notch - 0.1, notch + 0.1
    p1 = (x + r * math.cos(a1), y + r * 0.5 * math.sin(a1))
    p2 = (x + r * math.cos(a2), y + r * 0.5 * math.sin(a2))
    d.shape(role2, f"M{pt(x, y)} L{pt(*p2)} A{r} {r * 0.5} 0 1 1 {pt(*p1)}Z", spot=spot)
    rr = r * 0.84
    q1 = (x + rr * math.cos(a1), y - 1 + rr * 0.5 * math.sin(a1))
    q2 = (x + rr * math.cos(a2), y - 1 + rr * 0.5 * math.sin(a2))
    d.shape(role, f"M{pt(x, y - 1)} L{pt(*q2)} A{rr} {rr * 0.5} 0 1 1 {pt(*q1)}Z", shadow=False, line=False)


def palm(d: Drawing, x0, y0, x1, y1, s=1.0, bend=14, nuts=True, spot=False):
    """A palm on roles trunk/trunk2/frond/frond2/nut, from base (x0, y0) to crown (x1, y1)."""
    w0, w1 = 8 * s, 4.6 * s
    cx, cy = (x0 + x1) / 2 + bend, (y0 + y1) / 2
    d.shape("trunk", f"M{x0 - w0} {y0} Q{cx - (w0 + w1) / 2} {cy} {x1 - w1} {y1} L{x1 + w1} {y1} "
                     f"Q{cx + (w0 + w1) / 2} {cy} {x0 + w0} {y0}Z")
    rings = ""
    for i in range(1, 9):
        t = i / 9
        px = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1
        py = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1
        hw = w0 + (w1 - w0) * t
        rings += f"M{px - hw + 1:.1f} {py:.1f} q{hw - 1:.1f} {2.6 * s:.1f} {2 * hw - 2:.1f} 0 "
    d.stroke("trunk2", rings, 1.6 * s, line=False)
    back = [(-150, 40, 22), (-30, 40, 22), (160, 30, 30), (20, 30, 30)]
    front = [(-175, 50, 30), (-125, 44, 10), (-80, 36, -4), (-50, 46, 10), (-5, 50, 30)]
    for a, L, dr in back:
        d.shape("frond2", frond(x1, y1, a, L * s, dr * s, 0.6))
    if nuts:
        for nx, ny in [(-5, 5), (4, 6), (0, 1)]:
            d.shape("nut", circle(x1 + nx * s, y1 + ny * s, 4.2 * s))
    for a, L, dr in front:
        d.shape("frond", frond(x1, y1, a, L * s, dr * s, 0.6), spot=spot)
        d.stroke("frond2", frond_rib(x1, y1, a, L * s * 0.92, dr * s), 1.4 * s, line=False)


PALM = {"trunk": "#B5875A", "trunk2": "#8A6040", "frond": "#3E9A5A", "frond2": "#2A7144", "nut": "#6B4A2E"}


# ================================================================ TREE
GREEN = {"leaf": "#5E9C5A", "leaf2": "#3F7A4A", "leaf3": "#86BE6E", "bark": "#6B4A33"}
PINES = {"pineA": "#8DBF97", "pineB": "#4E8A5E", "pineC": "#2F6447", "bark": "#5A3E2B"}

def tree(d: Drawing):
    d.disc("glow", 156, 50, 15)
    d.band("far", hills(156, 8))
    d.band("mid", "M-30 166 Q100 154 230 166")
    d.shape("bark", "M88 172 C92 150 92 132 84 114 L80 104 L88 102 L96 116 L100 96 L108 98 L106 118 L116 104 L122 108 "
                    "L110 126 C108 144 108 156 114 172Z")
    d.shape("leaf2", scallop(100, 86, 58, 13, 0.1, ry=50))
    d.shape("leaf", scallop(96, 78, 50, 12, 0.11, ry=42), spot=True)
    d.shape("leaf3", scallop(76, 64, 16, 8, 0.12), shadow=False, line=False)
    d.shape("leaf3", scallop(108, 56, 11, 7, 0.12), shadow=False, line=False)
    grass(d, 40, 160, 170, 9, "near")
    d.band("near", hills(186, 3, 20), line=False)


# ================================================================ PINE FOREST
def pine_forest(d: Drawing):
    d.disc("glow", 52, 50, 15)
    d.band("far", "M-30 112 Q40 92 100 102 T230 96")
    for x in range(-4, 214, 16):
        pine(d, x, 128 + (x * 3) % 6, 46 + (x * 7) % 12, "pineA", shadow=False, line=False)
    d.band("pineA", "M-30 126 H230", shadow=False, line=False)
    for x, h in [(14, 84), (46, 96), (154, 100), (188, 86)]:
        d.limb("bark", f"M{x} 166 V150", 4, shadow=False)
        pine(d, x, 156, h, "pineB")
    for x, h in [(72, 104), (128, 108)]:
        d.limb("bark", f"M{x} 178 V164", 5, shadow=False)
        pine(d, x, 172, h, "pineB")
    d.limb("bark", "M100 180 V164", 7)
    pine(d, 100, 176, 140, "pineC", spot=True)
    d.band("ground", hills(176, 4))
    d.band("deep", hills(190, 3, 20), line=False)


# ================================================================ PALM TREE
def palm_tree(d: Drawing):
    d.disc("glow", 60, 70, 20)
    d.band("far", "M-30 140 H230")
    d.stroke("light", "M20 150 H50 M140 152 H176 M80 158 H110", 2, line=False)
    d.band("ground", "M-30 166 Q60 150 120 160 T230 158")
    palm(d, 120, 184, 98, 74, 1.45, bend=24, spot=True)
    d.shape("pop", star5(56, 176, 8, 3.6, -80), shadow=False)
    d.band("ground", hills(190, 3, 20), line=False)


# ================================================================ MOUNTAIN
def mountain(d: Drawing):
    d.disc("glow", 152, 52, 15)
    birds(d, [(34, 52, 1), (50, 44, 0.8)])
    d.band("far", "M-30 128 L10 104 L36 116 L60 92 L80 110 L140 96 L170 78 L230 112")
    d.shape("mid", "M6 178 L64 96 L76 104 L100 44 L122 84 L134 76 L196 178Z", spot=True)
    d.shape("near", "M100 44 L122 84 L134 76 L196 178 L120 178 L112 132 L118 108 L104 82Z", shadow=False, line=False)
    d.stroke("near", "M100 44 L104 82 L118 108 L112 132 L120 178", 2.4, line=True)
    d.band("deep", "M-30 162 Q40 148 90 160 T230 156")
    for x, h in [(26, 30), (40, 38), (154, 34), (170, 28), (184, 36)]:
        pine(d, x, 162, h, "dark", shadow=False)
    d.band("dark", hills(188, 4, 20), line=False)


# ================================================================ SNOWY PEAK
def snowy_peak(d: Drawing):
    d.disc("glow", 46, 62, 13)
    d.band("far", "M-30 136 L20 110 L44 124 L70 100 L100 120 L150 98 L180 112 L230 100", line=False)
    d.shape("mid", "M4 186 L60 120 L72 126 L104 32 L128 80 L140 72 L198 186Z")
    d.shape("near", "M104 32 L128 80 L140 72 L198 186 L118 186 L124 140 L110 104 L114 70Z", shadow=False, line=False)
    snow = "M104 32 L128 80 L140 72 L156 96 L144 92 L134 100 L124 90 L114 100 L104 88 L94 102 L86 90 L76 98 L80 80Z"
    d.shape("light", snow, spot=True)
    d.shape("snow2", "M104 32 L128 80 L140 72 L156 96 L144 92 L134 100 L124 90 L114 100 L114 70Z", shadow=False, line=False)
    d.band("light", "M-30 164 Q40 150 100 160 T230 154")
    for x, h in [(24, 40), (44, 30), (160, 36), (180, 44)]:
        pine(d, x, 166, h, "deep", shadow=False)
    d.band("snow2", hills(186, 3, 20), line=False)


# ================================================================ BEACH
def beach(d: Drawing):
    d.disc("glow", 46, 56, 15)
    d.band("far", "M-30 98 H230")
    d.band("mid", waves(112, 3, 26))
    d.shape("light", "M-30 124 Q30 116 80 124 T230 122 V132 H-30Z", shadow=False, line=False)
    d.band("ground", "M-30 128 Q60 120 120 128 T230 126")

    def parasol():
        r = 58
        d.limb("dark", f"M0 -4 L0 {r * 1.5}", 3.4)
        dome = (f"M{-r} 0 C{-r} {-r * 0.9} {r} {-r * 0.9} {r} 0 Q{r * 0.75} {-r * 0.12} {r * 0.5} 0 "
                f"Q{r * 0.25} {-r * 0.12} 0 0 Q{-r * 0.25} {-r * 0.12} {-r * 0.5} 0 Q{-r * 0.75} {-r * 0.12} {-r} 0Z")
        d.shape("hero", dome)
        d.shape("light", f"M{-r * 0.5} 0 C{-r * 0.5} {-r * 0.5} {-r * 0.18} {-r * 0.66} 0 {-r * 0.68} C{-r * 0.08} {-r * 0.6} "
                         f"{-r * 0.18} {-r * 0.3} 0 0 Q{-r * 0.25} {-r * 0.12} {-r * 0.5} 0Z", shadow=False, spot=True)
        d.shape("light", f"M{r * 0.5} 0 C{r * 0.5} {-r * 0.5} {r * 0.18} {-r * 0.66} 0 {-r * 0.68} C{r * 0.08} {-r * 0.6} "
                         f"{r * 0.18} {-r * 0.3} 0 0 Q{r * 0.25} {-r * 0.12} {r * 0.5} 0Z", shadow=False, spot=True)
        d.shape("dark", circle(0, -r * 0.68, 3), shadow=False)
    group(d, "translate(108 92) rotate(-12)", parasol)
    d.shape("pop", star5(40, 156, 10, 4.4, -80))
    d.marks("hero2", circle(40, 156, 1.4))


# ================================================================ LAKE
LAKE = {"water": "#6FB7D6", "water2": "#DDF1F8", "pine": "#3E6E52"}
LAKE_PINES = [(-4, 26), (8, 34), (20, 24), (30, 30), (152, 24), (164, 36), (176, 28), (188, 40), (200, 30)]


def lake(d: Drawing):
    d.disc("glow", 146, 50, 15)
    mtn = "M-30 112 L14 82 L40 96 L80 46 L114 92 L142 70 L176 96 L230 84 V112Z"
    d.shape("far", mtn)
    d.shape("light", "M80 46 L92 60 L86 59 L80 65 L73 58 L68 61Z", shadow=False)
    d.shape("light", "M142 70 L150 79 L145 78 L141 82 L136 77 L133 79Z", shadow=False)
    for x, h in LAKE_PINES:
        pine(d, x, 114, h, "pine", shadow=False, line=h > 30)
    d.band("water", "M-30 112 H230")
    # reflections
    d.raw('<g opacity=".35">', "")
    group(d, "translate(0 224) scale(1 -1)", lambda: d.shape("far", mtn, shadow=False, line=False))
    d.raw("</g>", "")
    d.raw('<g opacity=".3">', "")
    for x, h in LAKE_PINES:
        group(d, "translate(0 226) scale(1 -1)", lambda x=x, h=h: pine(d, x, 114, h * 0.8, "pine", shadow=False, line=False))
    d.raw("</g>", "")
    d.stroke("water2", "M24 138 H64 M120 134 H170 M60 156 H104 M136 168 H176 M20 178 H50", 2.4)
    # little rowing boat
    d.shape("hero", "M80 150 H124 C120 160 112 162 100 162 C90 162 84 160 80 150Z", spot=True)


# ================================================================ FIELD
FIELD = {"ear": "#F8DC85", "wheat": "#F0C75E", "wheat2": "#BE8630", "stalk": "#C8902F", "tree": "#4F8A55"}


def wheat_ear(d: Drawing, x, y, h, rot, spot=False):
    def draw():
        d.stroke("stalk", f"M0 0 Q2 {-h * 0.5} 0 {-h * 0.62}", 2.4)
        awns = ""
        for i in range(6):
            yy = -h * 0.6 - i * h * 0.075
            for k in (-1, 1):
                d.shape("ear", ellipse(k * 3.6, yy, 3, 6), extra=f'transform="rotate({k * 28} {k * 3.6} {yy:.1f})"',
                        shadow=i == 0, spot=spot)
                awns += f"M{k * 5} {yy - 4:.1f} l{k * 6} {-12} "
        top = -h * 0.6 - 6 * h * 0.075
        d.shape("ear", ellipse(0, top - 2, 2.8, 6), shadow=False, spot=spot)
        awns += f"M0 {top - 6:.1f} l0 -12"
        d.stroke("stalk", awns, 1.1)
    group(d, f"translate({x} {y}) rotate({rot})", draw)


def field(d: Drawing):
    d.disc("glow", 100, 82, 22)
    d.band("far", "M-30 88 Q60 78 120 84 T230 82")
    d.limb("dark", "M154 86 V72", 2.6, shadow=False)
    d.shape("tree", scallop(154, 66, 9, 8, 0.12))
    d.band("wheat2", "M-30 92 Q100 86 230 92")
    vx, vy, n, x0 = 100, 88, 12, -260
    w = 720 / n
    for i in range(n):
        a, b = x0 + i * w, x0 + (i + 1) * w - w * 0.42
        d.shape("wheat", f"M{vx} {vy} L{b:.1f} 210 L{a:.1f} 210Z", shadow=False, line=i % 2 == 0)
    wheat_ear(d, 30, 210, 96, -10)
    wheat_ear(d, 46, 210, 74, 4)
    wheat_ear(d, 166, 210, 100, 12, spot=True)
    wheat_ear(d, 150, 210, 70, -4)


# ================================================================ POND
POND = {"water": "#76BBD8", "water2": "#DDF1F8", "pad": "#6BB061", "pad2": "#3F8048", "reed": "#4F7A44",
        "cat": "#7A4E2D", "duck": "#FFFFFF", "duck2": "#DCE3EA", "beak": "#F29A2E", "lily": "#F28FB0", "lily2": "#FBD3E0"}


def duck(d: Drawing, x, y, s=1.0):
    def draw():
        d.shape("duck", "M-24 -4 C-26 -16 -12 -18 4 -16 C12 -15 18 -18 26 -26 C30 -14 26 -2 14 4 C2 10 -18 8 -24 -4Z")
        d.shape("duck", "M-24 -8 C-26 -18 -24 -26 -20 -30 L-10 -26 C-12 -20 -10 -14 -6 -10Z", shadow=False)
        d.shape("duck", circle(-17, -32, 10))
        d.shape("beak", "M-26 -32 C-32 -34 -38 -32 -40 -28 C-36 -26 -30 -26 -26 -27Z", spot=True)
        d.marks("mark", circle(-19, -34, 1.9))
        d.shape("duck2", "M-4 -10 C6 -14 16 -12 20 -6 C12 -2 0 -2 -4 -10Z", shadow=False)
    group(d, f"translate({x} {y}) scale({s})", draw)


def cattail(d: Drawing, x, y, h, rot=0, spot=False):
    def draw():
        d.stroke("reed", f"M0 0 Q-2 {-h * 0.5} 0 {-h}", 2.4)
        d.shape("cat", rrect(-4, -h + 8, 8, 24, 4), spot=spot)
        d.stroke("reed", f"M0 {-h + 8} V{-h - 2}", 1.6)
    group(d, f"translate({x} {y}) rotate({rot})", draw)


def pond(d: Drawing):
    d.disc("glow", 150, 40, 12)
    d.band("far", hills(62, 6))
    d.band("mid", "M-30 72 Q100 62 230 72")
    pond_shape = "M-10 110 C-10 84 40 76 100 76 C160 76 210 84 210 110 C210 150 160 172 100 172 C40 172 -10 150 -10 110Z"
    d.shape("water", pond_shape)
    d.stroke("water2", "M56 96 H82 M128 92 H160 M120 150 H146", 2.2, line=False)
    lilypad(d, 48, 134, 22, -20)
    lilypad(d, 154, 136, 18, 200)
    lilypad(d, 140, 96, 12, 160)
    # lily flower
    for a in (-150, -120, -90, -60, -30):
        d.shape("lily", leaf(46, 132, 12, 4.2, a), shadow=a == -90)
    for a in (-135, -105, -75, -45):
        d.shape("lily2", leaf(46, 132, 8, 3, a), shadow=False, line=False)
    d.stroke("water2", "M76 124 Q100 130 128 124", 2)
    duck(d, 104, 120, 1.2)
    d.band("near", "M-30 182 Q60 168 120 176 T230 172")
    for x, h, r in [(20, 96, -6), (30, 80, 4), (176, 90, 6), (186, 104, -4)]:
        cattail(d, x, 186, h, r, spot=x == 176)
    for x, a in [(12, -80), (24, -100), (170, -78), (190, -104)]:
        d.shape("reed", leaf(x, 186, 60, 4, a), shadow=False)
    d.band("near", hills(192, 3, 20), line=False)


# ================================================================ OCEAN WAVE
def ocean_wave(d: Drawing):
    d.disc("glow", 160, 56, 14)
    d.band("far", "M-30 132 H230")
    body = ("M-30 210 V124 C14 120 44 98 60 70 C78 40 106 24 138 26 C170 28 192 52 190 80 C189 96 178 106 164 106 "
            "C150 106 142 96 144 86 C130 92 122 110 124 132 C126 156 150 172 230 176 V210Z")
    d.shape("mid", body, spot=True)
    d.shape("near", "M144 86 C130 92 122 110 124 132 C126 156 150 172 230 176 V188 C140 186 104 166 104 132 "
                    "C104 104 120 86 144 86Z", shadow=False, line=False)
    d.stroke("near", "M-30 150 C10 146 36 130 50 110 M-30 172 C20 168 50 156 70 136", 2.4, line=False)
    foam = ("M54 78 C72 44 104 26 138 28 C168 30 190 52 188 80 C187 94 178 104 166 105 C176 96 180 84 176 72 "
            "C168 52 148 44 126 48 C104 52 88 64 78 80 L72 74 L68 86 L62 78Z")
    d.shape("light", foam)
    d.shape("light", "M156 96 C152 90 154 84 160 84 C164 86 164 92 160 94Z", shadow=False)
    for x, y, r in [(46, 72, 3), (40, 82, 2.2), (196, 74, 2.6), (200, 88, 2), (150, 18, 2.4), (166, 22, 1.8)]:
        d.shape("light", circle(x, y, r), shadow=False)
    d.band("light", "M-30 186 Q20 178 60 184 T140 182 T230 180", shadow=False)
    d.band("deep", waves(194, 3, 24), line=False)


# ================================================================ RIVER
RIVER = {"water": "#6FB7D6", "water2": "#DDF1F8"}


def river(d: Drawing):
    d.disc("glow", 64, 52, 15)
    d.band("far", "M-30 92 L20 70 L50 84 L90 60 L120 80 L150 64 L230 88")
    d.band("mid", "M-30 92 Q60 82 120 88 T230 86")
    path = ("M96 88 C88 96 78 102 86 112 C98 126 132 126 128 146 C124 166 76 172 54 210 H176 C182 184 194 168 176 148 "
            "C160 128 116 124 108 112 C102 102 108 94 106 88Z")
    d.band("near", "M-30 120 Q60 100 120 112 T230 112")
    for x, y, r in [(22, 112, 16), (178, 110, 14)]:
        d.limb("dark", f"M{x} {y} V{y + 22}", 3.6, shadow=False)
        d.shape("deep", scallop(x, y, r, 9, 0.12))
    d.shape("water", path, spot=True)
    d.stroke("water2", "M92 104 H100 M114 132 H130 M96 160 H120 M120 186 H150", 2.2)
    for x, h in [(150, 40), (166, 52)]:
        pine(d, x, 146, h, "deep")
    d.band("deep", "M-30 190 Q20 178 50 196 L50 210 H-30Z", line=False)
    d.shape("ground", ellipse(140, 196, 10, 5))


# ================================================================ FOREST PATH
def forest_path(d: Drawing):
    d.disc("glow", 100, 96, 28)
    d.band("far", "M-30 104 Q100 98 230 104")
    d.band("mid", "M-30 112 H230")
    d.shape("ground", "M95 104 H105 C110 124 128 146 168 210 H40 C70 160 90 124 95 104Z", spot=True)
    for x, y, r in [(72, 84, 20), (128, 84, 20)]:
        d.limb("bark", f"M{x} {y} V{y + 34}", 4, shadow=False)
        d.shape("leaf3", scallop(x, y, r, 9, 0.12))
    for x, w in [(38, 12), (162, 12)]:
        d.limb("bark", f"M{x} 210 V40", w)
    d.shape("leaf2", scallop(6, 42, 58, 13, 0.1, ry=50))
    d.shape("leaf2", scallop(196, 40, 58, 13, 0.1, ry=50))
    d.shape("leaf", scallop(40, 18, 30, 9, 0.12), shadow=False, line=False)
    d.shape("leaf", scallop(162, 16, 30, 9, 0.12), shadow=False, line=False)
    grass(d, -4, 52, 184, 12, "deep")
    grass(d, 150, 210, 184, 12, "deep")
    d.band("deep", "M-30 184 H60 L52 210 H-30Z", shadow=False, line=False)


# ================================================================ DESERT DUNES
DUNE = {"dune1": "#EDB872", "dune2": "#D08E48", "dune3": "#E3A65C", "dune4": "#B87638"}


def desert_dunes(d: Drawing):
    d.disc("glow", 136, 66, 26)
    d.disc("glow2", 136, 66, 18, shadow=False, line=False)
    # back dune
    d.band("dune1", "M-30 118 Q20 104 60 108 Q100 92 140 104 Q180 114 230 106")
    d.shape("dune2", "M60 108 Q100 92 140 104 Q180 114 230 106 V130 Q150 110 60 108Z", shadow=False, spot=True)
    # middle dune
    d.band("dune3", "M-30 140 Q30 120 80 132 Q120 140 170 126 Q200 118 230 124")
    d.shape("dune4", "M170 126 Q200 118 230 124 V170 Q180 150 170 126Z M-30 140 Q30 120 80 132 Q40 140 -30 170Z",
            shadow=False)
    # front dune
    d.band("dune1", "M-30 176 Q40 146 100 152 Q150 158 230 150")
    d.shape("dune2", "M100 152 Q150 158 230 150 V210 H170 Q170 176 100 152Z", shadow=False, spot=True)
    d.stroke("dune2", "M20 178 q10 -4 20 0 M44 188 q10 -4 20 0 M110 180 q8 -3 16 0", 1.6, line=False)
    # small camel caravan on the back ridge
    def camel(x, y, s):
        def draw():
            d.shape("dark", "M-10 0 L-9 -8 C-10 -12 -6 -16 -2 -14 C0 -18 4 -18 6 -14 L10 -16 L12 -22 L16 -21 L14 -14 "
                            "L10 -8 L10 0 L8 0 L8 -6 L-6 -6 L-6 0 L-8 0 L-8 -6Z", shadow=False)
        group(d, f"translate({x} {y}) scale({s})", draw)
    camel(52, 110, 0.9)
    camel(70, 106, 0.9)


# ================================================================ ISLAND
def island(d: Drawing):
    d.disc("glow", 52, 52, 15)
    d.shape("light", cloud(128, 40, 0.9), shadow=False)
    d.band("far", "M-30 112 H230")
    d.band("mid", "M-30 124 H230", shadow=False)
    d.shape("far", ellipse(100, 140, 76, 18), shadow=False, line=False)
    d.shape("light", ellipse(100, 138, 64, 13), shadow=False, line=False)
    d.shape("ground", "M38 140 C50 116 80 108 100 108 C124 108 152 118 164 140 C140 146 60 146 38 140Z")
    palm(d, 92, 128, 76, 68, 1.0, bend=-12, spot=True)
    palm(d, 124, 132, 144, 88, 0.72, bend=10, nuts=False)
    d.stroke("light", "M22 164 H52 M150 170 H184 M80 178 H116", 2.4)
    d.band("near", waves(186, 3, 26), line=False)


# ================================================================ VOLCANO
VOLC = {"rock": "#5E4B4B", "rock2": "#46383A", "lava": "#E8562A", "lava2": "#F9A33B", "smoke": "#9C9496", "smoke2": "#C9C2C2"}


def volcano(d: Drawing):
    d.shape("smoke", scallop(112, 26, 26, 9, 0.14))
    d.shape("smoke", scallop(84, 38, 20, 8, 0.14))
    d.shape("smoke2", scallop(102, 50, 18, 8, 0.14))
    d.shape("smoke2", scallop(122, 6, 18, 8, 0.14), shadow=False)
    d.band("far", hills(150, 8))
    d.shape("rock", "M2 190 C30 150 60 110 76 72 Q100 64 124 72 C140 110 170 150 198 190Z")
    d.shape("rock2", "M100 68 Q114 66 124 72 C140 110 170 150 198 190 H120 C126 150 114 110 100 68Z", shadow=False, line=False)
    d.shape("lava", ellipse(100, 72, 24, 6), spot=True)
    d.shape("lava", "M84 74 C80 92 70 104 72 118 C74 128 82 126 84 116 C86 104 92 90 96 76Z", spot=True)
    d.shape("lava", "M104 76 C108 96 120 108 120 128 C120 146 130 154 134 144 C138 130 124 104 114 74Z", spot=True)
    d.shape("lava2", "M86 76 C84 90 78 102 78 112 C80 104 86 92 90 78Z M108 78 C112 96 120 108 124 126 C122 108 116 94 112 78Z",
            shadow=False, line=False)
    for x, y, r in [(90, 56, 4), (112, 52, 3.4), (100, 44, 2.6), (124, 60, 2.4)]:
        d.shape("lava2", circle(x, y, r), shadow=False)
    d.band("deep", hills(182, 5))
    d.band("dark", hills(194, 3, 20), line=False)


# ================================================================ WATERFALL
FALLS = {"water": "#7CC4E4", "water2": "#E3F4FB", "rock": "#8A7766", "rock2": "#6C5B4D", "moss": "#5E9C5A"}


def waterfall(d: Drawing):
    d.disc("glow", 150, 40, 12)
    d.band("far", hills(66, 6))
    # cliffs
    d.shape("rock", "M-30 60 L64 56 L70 80 L64 120 L72 160 L40 210 H-30Z")
    d.shape("rock", "M230 60 L136 56 L130 84 L138 124 L128 160 L160 210 H230Z")
    d.shape("rock2", "M64 56 L70 80 L64 120 L72 160 L60 176 L52 130 L58 90Z M136 56 L130 84 L138 124 L128 160 L142 176 L146 120 L140 90Z",
            shadow=False, line=False)
    d.shape("moss", "M-30 56 L68 52 C66 60 56 62 46 60 C30 66 10 60 -30 66Z")
    d.shape("moss", "M230 56 L132 52 C134 60 146 62 156 60 C170 66 190 60 230 66Z")
    for x, h in [(14, 40), (30, 30), (170, 34), (188, 44)]:
        pine(d, x, 60, h, "deep", shadow=False)
    # the fall
    d.shape("water", "M64 52 H136 C134 70 132 100 134 150 H66 C68 100 66 70 64 52Z", spot=True)
    d.stroke("water2", "M76 60 V146 M90 58 V150 M104 58 V140 M118 60 V148 M128 62 V120", 2.4, line=False)
    d.stroke("water2", "M84 60 V128 M112 60 V120", 1.6, line=True)
    # plunge pool and spray
    d.band("water", "M-30 160 Q100 150 230 160")
    d.shape("light", scallop(100, 150, 50, 11, 0.18, ry=17))
    d.stroke("water2", "M30 176 H60 M130 182 H170 M80 190 H110", 2.2)
    d.band("rock2", "M-30 190 Q30 180 60 196 L60 210 H-30Z", line=False)


# ================================================================ WILDFLOWERS
FLOWERS = {"daisy": "#FFFFFF", "daisy2": "#F6C445", "poppy": "#E5402F", "poppy2": "#2A1E1E", "corn": "#4A7FD6",
           "corn2": "#2F5BA8", "stem": "#5E9C4A", "stem2": "#3E7A3A"}


def daisy(d: Drawing, x, y, r, spot=False):
    for i in range(14):
        a = 360 * i / 14
        d.shape("daisy", leaf(x, y, r, r * 0.22, a), shadow=i == 0)
    d.shape("daisy2", circle(x, y, r * 0.32), spot=spot)


def poppy(d: Drawing, x, y, r, spot=False):
    d.shape("poppy", f"M{x - r} {y - r * 0.2} C{x - r * 1.1} {y + r * 0.8} {x + r * 1.1} {y + r * 0.8} {x + r} {y - r * 0.2} "
                     f"C{x + r * 0.6} {y - r * 0.6} {x + r * 0.2} {y - r * 0.3} {x} {y - r * 0.6} C{x - r * 0.2} {y - r * 0.3} "
                     f"{x - r * 0.6} {y - r * 0.6} {x - r} {y - r * 0.2}Z", spot=spot)
    d.shape("poppy2", ellipse(x, y - r * 0.2, r * 0.3, r * 0.16), shadow=False)


def cornflower(d: Drawing, x, y, r):
    pts = []
    for i in range(18):
        a = math.radians(-90 + 20 * i)
        rr = r if i % 2 == 0 else r * 0.6
        pts.append(pt(x + rr * math.cos(a), y + rr * math.sin(a)))
    d.shape("corn", "M" + " L".join(pts) + "Z")
    d.shape("corn2", circle(x, y, r * 0.35), shadow=False)


def wildflowers(d: Drawing):
    d.disc("glow", 150, 46, 15)
    d.band("far", "M-30 128 Q60 112 120 120 T230 116")
    stems = [("M100 210 Q96 150 100 96", 3), ("M56 210 Q52 160 50 122", 2.6), ("M150 210 Q154 160 150 112", 2.6),
             ("M24 210 Q28 170 26 146", 2.2), ("M180 210 Q176 170 178 148", 2.2), ("M126 210 Q128 170 124 150", 2.2),
             ("M78 210 Q76 176 78 156", 2.2)]
    for s, w in stems:
        d.stroke("stem2", s, w + 0.6)
    for x, y, L, a in [(100, 168, 30, -130), (100, 152, 28, -50), (52, 178, 24, -120), (152, 170, 24, -60)]:
        d.shape("stem", leaf(x, y, L, 6, a), shadow=False)
    d.band("stem", "M-30 182 Q20 170 60 180 Q100 168 140 180 Q180 170 230 178")
    grass(d, -6, 210, 186, 14, "stem2")
    daisy(d, 100, 92, 30, spot=True)
    poppy(d, 50, 118, 20, spot=True)
    cornflower(d, 150, 108, 18)
    daisy(d, 26, 144, 12)
    poppy(d, 178, 146, 13)
    cornflower(d, 78, 154, 10)
    daisy(d, 124, 148, 11)


# ================================================================ SEA CLIFFS
CLIFF = {"cliff": "#EFE6D2", "cliff2": "#CFC0A2", "grass": "#6FA85A", "grass2": "#4F8A44"}


def sea_cliffs(d: Drawing):
    d.disc("glow", 48, 52, 14)
    birds(d, [(60, 80, 1), (78, 70, 0.8), (40, 92, 0.7)])
    d.band("mid", "M-30 112 H230")
    d.band("near", waves(126, 3, 26))
    # sea stack
    d.shape("cliff", "M40 150 L44 118 Q52 112 60 118 L64 150Z")
    d.shape("grass", "M43 120 Q52 110 61 120 Q52 116 43 120Z", shadow=False)
    # main cliff
    d.shape("cliff", "M92 210 L96 160 L90 120 L102 80 L100 52 L230 40 V210Z", spot=True)
    d.shape("cliff2", "M110 70 L106 110 L114 150 L108 210 H118 L124 150 L118 110 L122 70Z M146 64 L140 110 L150 160 L146 210 H156 "
                      "L160 160 L152 110 L156 60Z", shadow=False, line=False)
    d.stroke("cliff2", "M110 70 L106 110 L114 150 L108 200 M146 64 L140 110 L150 160 L146 200", 2, line=True)
    d.shape("grass", "M96 56 Q120 40 230 32 V44 L100 54Z")
    d.shape("grass2", "M98 54 Q140 46 230 40 V46 L100 56Z", shadow=False, line=False)
    # foam and nearer sea
    d.shape("light", "M76 166 C84 156 94 156 100 162 C104 156 112 156 116 162 L116 172 H76Z", shadow=False)
    d.band("deep", waves(170, 4, 28))
    d.stroke("light", "M14 182 q10 -5 20 0 M50 190 q10 -5 20 0 M140 186 q10 -5 20 0", 2.2, line=False)


# ================================================================ ROLLING HILLS
def rolling_hills(d: Drawing):
    d.disc("glow", 146, 52, 17)
    d.shape("light", cloud(28, 52, 0.8), shadow=False)
    d.band("far", "M-30 100 Q20 76 70 90 Q120 66 170 86 Q200 78 230 82")
    mid = "M-30 132 Q40 92 110 114 Q160 94 230 108 V230 H-30Z"
    d.shape("mid", mid)

    clipped(d, mid, lambda: d.stroke("far", "M-30 140 Q40 104 110 124 M-30 152 Q50 116 120 136 M110 122 Q160 104 230 118 "
                                            "M116 134 Q170 116 230 128", 2.4, line=False))
    for x, y, r in [(70, 102, 7), (160, 96, 6)]:
        d.limb("dark", f"M{x} {y} V{y + 8}", 2.2, shadow=False)
        d.shape("deep", scallop(x, y, r, 8, 0.12))
    near = "M-30 164 Q50 120 130 140 Q180 126 230 134 V230 H-30Z"
    d.shape("near", near, spot=True)
    clipped(d, near, lambda: d.stroke("mid", "M-30 156 Q50 126 130 150 M-30 170 Q60 140 140 162 M-30 186 Q70 154 150 176 "
                                             "M120 146 Q180 132 230 142 M130 160 Q190 146 230 156", 2.6, line=False))
    d.limb("dark", "M140 134 V146", 3, shadow=False)
    d.shape("deep", scallop(140, 126, 12, 9, 0.12))
    d.band("deep", "M-30 186 Q80 168 230 184")


# ================================================================ STARRY NIGHT
NIGHT = {"sky": "#1F2A44", "sky2": "#2E3B5E", "light": "#F6EBC8", "moon": "#FBE7A1"}


def starry_night(d: Drawing):
    d.raw('<circle cx="122" cy="66" r="46" fill="#FFFFFF" opacity=".06"/>', "")
    d.shape("moon", crescent(122, 66, 30, 22), spot=True)
    for x, y, r in [(48, 52, 9), (80, 30, 6), (160, 120, 6), (40, 100, 5), (170, 34, 4.5)]:
        d.shape("light", sparkle(x, y, r), shadow=False)
    for x, y, r in [(64, 76, 1.8), (100, 22, 1.4), (30, 74, 1.5), (90, 104, 1.4), (182, 80, 1.6), (140, 22, 1.4), (118, 118, 1.3)]:
        d.marks("light", circle(x, y, r))
    d.band("far", "M-30 150 Q40 126 100 140 T230 132")
    for x, h in [(150, 40), (166, 54), (182, 44)]:
        pine(d, x, 150, h, "near", shadow=False)
    d.band("near", "M-30 168 Q60 150 120 162 T230 158")
    d.band("deep", hills(186, 4, 20), line=False)


# ================================================================ SUNSHINE
SUN = {"sun": "#FFC233", "sun2": "#FFDE6E", "ray": "#FFB020"}


def sunshine(d: Drawing):
    rays = ""
    for i in range(12):
        a = math.radians(i * 30 - 90)
        L = 80 if i % 2 == 0 else 68
        w = math.radians(7 if i % 2 == 0 else 6)
        p0 = (100 + 50 * math.cos(a - w), 100 + 50 * math.sin(a - w))
        p1 = (100 + L * math.cos(a), 100 + L * math.sin(a))
        p2 = (100 + 50 * math.cos(a + w), 100 + 50 * math.sin(a + w))
        rays += f"M{pt(*p0)} L{pt(*p1)} L{pt(*p2)}Z "
    d.shape("ray", rays)
    d.disc("sun", 100, 100, 46)
    d.shape("sun2", circle(100, 100, 34), shadow=False, line=False)
    d.shape("light", "M88 82 Q96 74 106 74", shadow=False, line=False) if False else None
    d.stroke("light", "M78 92 Q82 80 94 74", 4, line=False)
    d.shape("light", cloud(20, 170, 1.6))
    d.shape("light", cloud(132, 172, 1.2))


# ================================================================ CLOUDS
CLOUDS = {"cloud": "#FFFFFF", "cloud2": "#E1E9F1"}


def big_cloud(x, y, s):
    """A flat-bottomed cumulus about 150*s wide, bottom at y."""
    k = s
    return (f"M{x} {y} C{x - 20 * k} {y} {x - 22 * k} {y - 30 * k} {x + 4 * k} {y - 32 * k} "
            f"C{x + 4 * k} {y - 58 * k} {x + 40 * k} {y - 66 * k} {x + 56 * k} {y - 48 * k} "
            f"C{x + 66 * k} {y - 86 * k} {x + 120 * k} {y - 84 * k} {x + 122 * k} {y - 44 * k} "
            f"C{x + 150 * k} {y - 52 * k} {x + 164 * k} {y - 18 * k} {x + 146 * k} {y} Z")


def clouds(d: Drawing):
    d.disc("glow", 138, 70, 26)
    d.shape("cloud", big_cloud(106, 68, 0.42))
    d.shape("cloud", big_cloud(44, 140, 0.92), spot=True)
    d.shape("cloud2", f"M44 140 C30 140 26 132 30 126 C60 134 140 134 172 124 C178 132 172 140 160 140Z", shadow=False, line=False)
    d.shape("cloud", big_cloud(12, 178, 0.4))
    d.shape("cloud", big_cloud(132, 182, 0.36))


# ================================================================ concepts
NO_GOLD = ["coastal", "meadow", "blush", "dusk"]

CONCEPTS = [
    Concept("basic-tree", "basic-tree", "Tree", tree, overrides=GREEN,
            checks=[("leaf", "sky"), ("leaf2", "sky"), ("bark", "mid"), ("leaf2", "far"), ("leaf", "glow")],
            fixes={"far": ["mid", "sky2"], "glow": ["glow2", "hero2"]}),
    Concept("basic-pine-forest", "basic-pine-forest", "Pine forest", pine_forest, overrides=PINES,
            checks=[("pineC", "pineB"), ("pineB", "pineA"), ("pineA", "far"), ("pineC", "sky"), ("pineC", "ground")],
            fixes={"far": ["sky2", "mid"]}),
    Concept("basic-palm-tree", "basic-palm-tree", "Palm tree", palm_tree, overrides=PALM,
            checks=[("frond", "sky"), ("frond", "glow"), ("trunk", "far"), ("trunk", "ground")],
            fixes={"glow": ["glow2", "pop", "hero2"]}),
    Concept("basic-mountain", "basic-mountain", "Mountain", mountain,
            checks=[("mid", "sky"), ("mid", "far"), ("deep", "mid")], fixes={"far": ["sky2", "light"]}),
    Concept("basic-snowy-peak", "basic-snowy-peak", "Snowy peak", snowy_peak, overrides={"snow2": "#D6E2EC"},
            checks=[("light", "sky"), ("mid", "far"), ("deep", "light")], fixes={"sky": ["sky2", "far", "mid"], "far": ["near", "deep", "sky2"]}),
    Concept("basic-beach", "basic-beach", "Beach", beach, NO_GOLD,
            checks=[("hero", "sky"), ("hero", "far"), ("ground", "mid"), ("pop", "ground")], fixes={"hero": ["pop", "hero2"], "pop": ["hero", "deep"]}),
    Concept("basic-lake", "basic-lake", "Lake", lake, NO_GOLD, overrides=LAKE,
            checks=[("far", "sky"), ("pine", "water"), ("hero", "water")], fixes={"far": ["mid", "near"], "hero": ["pop", "hero2"]}),
    Concept("basic-field", "basic-field", "Field", field, overrides=FIELD,
            checks=[("wheat", "wheat2"), ("wheat", "far"), ("far", "sky")], fixes={"far": ["mid", "near"]}),
    Concept("basic-pond", "basic-pond", "Pond", pond, NO_GOLD, overrides=POND,
            checks=[("water", "mid"), ("duck", "water"), ("pad", "water")], fixes={"mid": ["near", "far"]}),
    Concept("basic-ocean-wave", "basic-ocean-wave", "Ocean wave", ocean_wave, NO_GOLD,
            checks=[("mid", "sky"), ("mid", "far"), ("light", "mid")], fixes={"far": ["sky2", "light"]}),
    Concept("basic-river", "basic-river", "River", river, overrides=RIVER,
            checks=[("water", "near"), ("water", "mid"), ("deep", "near")], fixes={"near": ["mid", "far"], "mid": ["far", "near", "ground"]}),
    Concept("basic-forest-path", "basic-forest-path", "Forest path", forest_path, overrides=GREEN,
            checks=[("ground", "mid"), ("leaf2", "sky"), ("leaf3", "glow"), ("leaf3", "far")],
            fixes={"mid": ["near", "deep"], "glow": ["glow2", "light"], "far": ["mid", "near"]}),
    Concept("basic-desert-dunes", "basic-desert-dunes", "Desert dunes", desert_dunes, overrides=DUNE,
            checks=[("dune1", "sky"), ("glow", "dune1")], fixes={"sky": ["sky2", "far"], "glow": ["glow2", "pop", "hero"]}),
    Concept("basic-island", "basic-island", "Island", island, NO_GOLD, overrides=PALM,
            checks=[("ground", "mid"), ("frond", "sky"), ("frond", "mid")]),
    Concept("basic-volcano", "basic-volcano", "Volcano", volcano, overrides=VOLC,
            checks=[("rock", "sky"), ("smoke", "sky"), ("rock", "far")], fixes={"far": ["mid", "sky2", "light"]}),
    Concept("basic-waterfall", "basic-waterfall", "Waterfall", waterfall, overrides=FALLS,
            checks=[("water", "rock"), ("moss", "sky"), ("water", "sky")], fixes={"sky": ["sky2", "far"]}),
    Concept("basic-wildflowers", "basic-wildflowers", "Wildflowers", wildflowers, overrides=FLOWERS,
            checks=[("daisy", "sky"), ("poppy", "far"), ("corn", "far"), ("daisy", "far")],
            fixes={"sky": ["sky2", "far"], "far": ["mid", "near"]}),
    Concept("basic-sea-cliffs", "basic-sea-cliffs", "Sea cliffs", sea_cliffs, NO_GOLD, overrides=CLIFF,
            checks=[("cliff", "mid"), ("cliff", "near"), ("cliff", "deep"), ("grass", "sky")], fixes={"sky": ["sky2", "far"]}),
    Concept("basic-rolling-hills", "basic-rolling-hills", "Rolling hills", rolling_hills,
            checks=[("near", "sky"), ("deep", "near"), ("ground", "mid")], fixes={"ground": ["light", "far"]}),
    Concept("basic-starry-night", "basic-starry-night", "Starry night", starry_night, ["dusk", "coastal", "meadow", "blush", "golden"],
            overrides=NIGHT, checks=[("far", "sky"), ("near", "far")], fixes={"far": ["mid", "near"], "near": ["deep", "mid"]}),
    Concept("basic-sunshine", "basic-sunshine", "Sunshine", sunshine, overrides=SUN,
            checks=[("sun", "sky"), ("ray", "sky"), ("light", "sky")], fixes={"sky": ["sky2", "far", "mid"]}),
    Concept("basic-clouds", "basic-clouds", "Clouds", clouds, ["golden", "coastal", "blush", "dusk"], overrides=CLOUDS,
            checks=[("cloud", "sky")], fixes={"sky": ["far", "mid"]}),
]
