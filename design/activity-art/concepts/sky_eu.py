"""Mapsie Originals: European city skylines (one layered skyline per city).

Every skyline uses the same layer system so the set reads as one series:
  far   pale distant towers            (role "far")
  near  the mid layer of the city      (role "near")
  deep  the front layer of signature buildings, drawn as ONE silhouette
  mid   river / harbour / sea, with a soft mirrored reflection of the front layer
  glow  sun or moon disc; glow2 lit windows; light water glints

A layer is drawn as one group with one shadow in papercut, and as one merged outline
in line style (thick ink under, paper on top), so the skyline reads as a clean outline.
"""
from _common import Concept, Drawing, cloud, circle, ellipse, rrect, group  # noqa: F401
import math


# ================================================================ geometry helpers
def poly(*pts, close=True) -> str:
    s = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    return s + ("Z" if close else "")


def arch(x, y, w, h) -> str:
    """Round-topped opening, (x, y) top-left of its bounding box."""
    r = w / 2
    return f"M{x:g} {y + h:g} V{y + r:g} A{r:g} {r:g} 0 0 1 {x + w:g} {y + r:g} V{y + h:g}Z"


def garch(x, y, w, h) -> str:
    """Pointed (gothic) opening, (x, y) top-left of its bounding box."""
    return (f"M{x:g} {y + h:g} V{y + w * .7:g} Q{x:g} {y + w * .15:g} {x + w / 2:g} {y:g} "
            f"Q{x + w:g} {y + w * .15:g} {x + w:g} {y + w * .7:g} V{y + h:g}Z")


def rect(x, y, w, h) -> str:
    return f"M{x:g} {y:g} H{x + w:g} V{y + h:g} H{x:g}Z"


def dome(cx, by, w, h) -> str:
    """Half-ellipse dome sitting on y = by."""
    return f"M{cx - w / 2:g} {by:g} A{w / 2:g} {h:g} 0 0 1 {cx + w / 2:g} {by:g}Z"


def bulb(cx, by, w, h) -> str:
    """Pointed ogee/onion cap, bottom centre (cx, by)."""
    return (f"M{cx - w * .36:g} {by:g} C{cx - w * .62:g} {by - h * .2:g} {cx - w * .56:g} {by - h * .55:g} {cx - w * .2:g} {by - h * .74:g} "
            f"Q{cx - w * .03:g} {by - h * .84:g} {cx:g} {by - h:g} Q{cx + w * .03:g} {by - h * .84:g} {cx + w * .2:g} {by - h * .74:g} "
            f"C{cx + w * .56:g} {by - h * .55:g} {cx + w * .62:g} {by - h * .2:g} {cx + w * .36:g} {by:g}Z")


def tri(cx, by, w, h) -> str:
    return poly((cx - w / 2, by), (cx, by - h), (cx + w / 2, by))


def gparab(x, top, base, w) -> str:
    """Gaudi-style parabolic tower."""
    H = base - top
    k = base - H * .38
    return (f"M{x - w:g} {base:g} V{k:g} C{x - w:g} {top + H * .25:g} {x - w * .3:g} {top + H * .06:g} {x:g} {top:g} "
            f"C{x + w * .3:g} {top + H * .06:g} {x + w:g} {top + H * .25:g} {x + w:g} {k:g} V{base:g}Z")


def crenel(x, y, w, h, n, mh=3.0) -> str:
    """A block whose top edge has n merlons."""
    mw = w / (2 * n - 1)
    s = f"M{x:g} {y + h:g} V{y:g}"
    for i in range(n):
        x0 = x + 2 * i * mw
        s += f" H{x0 + mw:g}"
        if i < n - 1:
            s += f" V{y + mh:g} H{x0 + 2 * mw:g} V{y:g}"
    return s + f" V{y + h:g}Z"


def gables(x, y, w, kind) -> str:
    """Dutch / Nordic gable tops sitting on y, spanning x..x+w (closed down to y + 2)."""
    c = x + w / 2
    if kind == "step":
        s = w / 6
        return poly((x, y + 2), (x, y), (x + s, y), (x + s, y - 6), (x + 2 * s, y - 6), (x + 2 * s, y - 12), (x + 4 * s, y - 12),
                    (x + 4 * s, y - 6), (x + 5 * s, y - 6), (x + 5 * s, y), (x + w, y), (x + w, y + 2))
    if kind == "bell":
        return (f"M{x:g} {y + 2:g} V{y:g} Q{x + w * .18:g} {y:g} {x + w * .22:g} {y - 6:g} Q{x + w * .22:g} {y - 14:g} {c:g} {y - 16:g} "
                f"Q{x + w * .78:g} {y - 14:g} {x + w * .78:g} {y - 6:g} Q{x + w * .82:g} {y:g} {x + w:g} {y:g} V{y + 2:g}Z")
    if kind == "neck":
        return poly((x, y + 2), (x, y), (x + w * .25, y - 4), (x + w * .25, y - 14), (x + w * .75, y - 14), (x + w * .75, y - 4),
                    (x + w, y), (x + w, y + 2))
    return poly((x, y + 2), (x, y), (c, y - w * .55), (x + w, y), (x + w, y + 2))  # plain triangle


# ================================================================ drawing helpers
def F(path, spot=False):
    return ("f", path, spot)


def FE(path, spot=False):
    """Filled with holes (evenodd)."""
    return ("e", path, spot)


def S(path, w):
    """Thick stroke: a tube in line style."""
    return ("s", path, w)


def T(path, w):
    """Thin stroke (cables, spokes): a fine ink line in line style."""
    return ("t", path, w)


def layer(d: Drawing, role: str, items, line=True, lw=3.2, shadow=True):
    """Draw items as one silhouette layer."""
    if d.paper:
        col = d.c[role]
        body = ""
        for it in items:
            k, p = it[0], it[1]
            if k in "fe":
                body += f'<path d="{p}"{" fill-rule=" + chr(34) + "evenodd" + chr(34) if k == "e" else ""}/>'
            else:
                body += (f'<path d="{p}" fill="none" stroke="{col}" stroke-width="{it[2]}" '
                         f'stroke-linecap="round" stroke-linejoin="round"/>')
        filt = ' filter="url(#psl)"' if shadow else ""
        d.raw(f'<g{filt} fill="{col}">{body}</g>')
        return
    if not line:
        return
    ink, paper, spot = d.c["ink"], d.c["paper"], d.c["spot"]
    under, over, thin = "", "", ""
    for it in items:
        k, p = it[0], it[1]
        if k in "fe":
            fr = ' fill-rule="evenodd"' if k == "e" else ""
            under += f'<path d="{p}"{fr} fill="{ink}" stroke="{ink}" stroke-width="{2 * lw}" stroke-linejoin="round"/>'
            over += f'<path d="{p}"{fr} fill="{spot if it[2] else paper}"/>'
        elif k == "s":
            under += f'<path d="{p}" fill="none" stroke="{ink}" stroke-width="{it[2] + 2 * lw}" stroke-linecap="round" stroke-linejoin="round"/>'
            over += f'<path d="{p}" fill="none" stroke="{paper}" stroke-width="{it[2]}" stroke-linecap="round" stroke-linejoin="round"/>'
        else:
            thin += f'<path d="{p}" fill="none" stroke="{ink}" stroke-width="{min(it[2], 1.6)}" stroke-linecap="round" stroke-linejoin="round"/>'
    d.raw("", under + over + thin)


def reflect(d: Drawing, role: str, items, y0: float, opacity=.3, ripple="mid"):
    """Papercut only: a soft mirror image of a layer in the water below y0, broken by ripples."""
    if not d.paper:
        return
    n = getattr(d, "_skyeu_clip", 0) + 1
    d._skyeu_clip = n
    col = d.c[role]
    body = ""
    for it in items:
        k, p = it[0], it[1]
        if k in "fe":
            body += f'<path d="{p}"{" fill-rule=" + chr(34) + "evenodd" + chr(34) if k == "e" else ""}/>'
        else:
            body += f'<path d="{p}" fill="none" stroke="{col}" stroke-width="{it[2]}" stroke-linecap="round"/>'
    d.raw(f'<clipPath id="skyeu{n}"><rect x="-30" y="{y0 + 1}" width="260" height="120"/></clipPath>'
          f'<g clip-path="url(#skyeu{n})"><g transform="translate(0 {2 * y0}) scale(1 -1)" opacity="{opacity}" fill="{col}">{body}</g></g>')
    rip = ""
    for i in range(8):
        y = y0 + 4 + i * 6 + i * i * .6
        rip += (f'<path d="M-30 {y:.1f} H230" stroke-dasharray="{34 + (i * 17) % 23} {3 + i % 3} {12 + (i * 7) % 11} {4 + (i * 5) % 4}" '
                f'stroke-dashoffset="{(i * 29) % 50}"/>')
    d.raw(f'<g fill="none" stroke="{d.c[ripple]}" stroke-width="{1.7}">{rip}</g>')


def water(d: Drawing, y0: float, front=None, glints=((30, 10), (124, 16), (160, 8)), role="mid"):
    """River / harbour band at y0 with reflection of the front layer and a few glints."""
    d.band(role, f"M-30 {y0} H230")
    if front:
        reflect(d, "deep", front, y0, ripple=role)
    gl = " ".join(f"M{x} {y0 + 10 + (i % 3) * 9} h{w}" for i, (x, w) in enumerate(glints))
    d.stroke("light", gl, 2, line=False)
    if not d.paper:
        line_water(d, y0)


def line_water(d: Drawing, y0: float, dashes=((40, 14, 14), (118, 22, 22), (150, 12, 10))):
    """Line style: hide whatever sits below the waterline, then draw the shore line and a few ripples."""
    line_ground(d, f"M-30 {y0} H230")
    ds = " ".join(f"M{x} {y0 + dy} h{w}" for x, dy, w in dashes)
    d.raw("", f'<path d="{ds}" fill="none" stroke="{d.c["ink"]}" stroke-width="1.6" stroke-linecap="round"/>')


def line_ground(d: Drawing, edge: str):
    """Line style: a foreground edge drawn over the buildings, wash-filled below (clipped to the wash disc)."""
    if d.paper:
        return
    n = getattr(d, "_skyeu_clip", 0) + 1
    d._skyeu_clip = n
    d.raw("", f'<clipPath id="skyeuw{n}"><circle cx="100" cy="100" r="84"/></clipPath>'
              f'<path d="{edge} L230 240 L-30 240Z" fill="{d.c["bg"]}"/>'
              f'<path clip-path="url(#skyeuw{n})" d="{edge} L230 240 L-30 240Z" fill="{d.c["wash"]}"/>'
              f'<path d="{edge}" fill="none" stroke="{d.c["ink"]}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')


def bushes(y, r=7, step=12):
    s = f"M-30 {y}"
    x, i = -30, 0
    jit = (0, 3, 1, 4, 2)
    while x < 230:
        s += f" Q{x + step / 2} {y - r - jit[i % 5]} {x + step} {y}"
        x += step
        i += 1
    return s


def trees(d: Drawing, y, role="mid", r=7, step=12):
    """Park trees along the front (land cities): papercut band, line style edge over the buildings."""
    e = bushes(y, r, step)
    d.band(role, e, line=False)
    line_ground(d, e)


def lights(d: Drawing, rects, role="glow2"):
    """Lit windows: papercut only (line style keeps the outline clean)."""
    if d.paper:
        d.marks(role, " ".join(rect(x, y, w, h) for x, y, w, h in rects))


def ink(d: Drawing, role: str, path: str, w: float, line_w: float = 1.3, line=True):
    """Thin detail line: palette colour in papercut, fine ink in line style."""
    if d.paper:
        d.stroke(role, path, w)
    elif line:
        d.raw("", f'<path d="{path}" fill="none" stroke="{d.c["ink"]}" stroke-width="{line_w}" stroke-linecap="round" stroke-linejoin="round"/>')


def flat(d: Drawing, role: str, path: str, line=False, spot=False):
    """A flat detail on a building (facade colour, roof tiles)."""
    d.shape(role, path, shadow=False, line=line, spot=spot)


def towers(specs, base=170):
    """Generic city blocks: (x, w, top, kind)."""
    out = []
    for x, w, top, kind in specs:
        if kind == "r":
            out.append(F(rect(x, top, w, base - top)))
        elif kind == "a":  # antenna
            out.append(F(rect(x, top, w, base - top)))
            out.append(S(f"M{x + w / 2:g} {top:g} V{top - 8:g}", 1.2))
        elif kind == "p":  # pointed
            out.append(F(poly((x, base), (x, top + w * .5), (x + w / 2, top), (x + w, top + w * .5), (x + w, base))))
        elif kind == "s":  # stepped
            out.append(F(poly((x, base), (x, top + 8), (x + w * .2, top + 8), (x + w * .2, top), (x + w * .8, top),
                              (x + w * .8, top + 8), (x + w, top + 8), (x + w, base))))
        elif kind == "d":  # domed
            out.append(F(rect(x, top + w * .4, w, base - top - w * .4)))
            out.append(F(dome(x + w / 2, top + w * .4 + .5, w, w * .4)))
        elif kind == "g":  # gable
            out.append(F(poly((x, base), (x, top + w * .45), (x + w / 2, top), (x + w, top + w * .45), (x + w, base))))
        elif kind == "w":  # wedge (slanted roof)
            out.append(F(poly((x, base), (x, top + w * .8), (x + w, top), (x + w, base))))
    return out


def birds(d: Drawing, pts, role="dark"):
    s = " ".join(f"M{x} {y} q{3 * k} {-3 * k} {6 * k} 0 q{3 * k} {-3 * k} {6 * k} 0" for x, y, k in pts)
    d.stroke(role, s, 1.5)


# ================================================================ LONDON
def big_ben(x, base, s=1.0):
    k = s
    w = 10 * k
    return [
        F(rect(x - w / 2, base - 70 * k, w, 70 * k)),
        F(rect(x - 7 * k, base - 84 * k, 14 * k, 15 * k)),
        F(rect(x - 6 * k, base - 92 * k, 12 * k, 9 * k)),
        F(poly((x - 6.5 * k, base - 91 * k), (x - 3 * k, base - 102 * k), (x + 3 * k, base - 102 * k), (x + 6.5 * k, base - 91 * k))),
        F(poly((x - 1.6 * k, base - 102 * k), (x, base - 112 * k), (x + 1.6 * k, base - 102 * k))),
        F(poly((x - 7.5 * k, base - 92 * k), (x - 6.5 * k, base - 96 * k), (x - 5.5 * k, base - 92 * k))),
        F(poly((x + 5.5 * k, base - 92 * k), (x + 6.5 * k, base - 96 * k), (x + 7.5 * k, base - 92 * k))),
    ]


def london_eye(cx, cy, r, base):
    caps = []
    for i in range(16):
        a = i * math.pi / 8
        caps.append(F(ellipse(cx + r * math.cos(a), cy + r * math.sin(a), 2.2, 1.7)))
    spokes = " ".join(f"M{cx:.1f} {cy:.1f} L{cx + r * math.cos(i * math.pi / 8):.1f} {cy + r * math.sin(i * math.pi / 8):.1f}" for i in range(16))
    return [S(circle(cx, cy, r), 2.4), T(spokes, .8), *caps, F(circle(cx, cy, 2.6)),
            S(f"M{cx} {cy} L{cx - r * .55:.1f} {base} M{cx} {cy} L{cx + r * .18:.1f} {base}", 2.2)]


def st_pauls(cx, base):
    return [
        F(rect(cx - 17, base - 22, 34, 22)),
        F(rect(cx - 10, base - 34, 20, 13)),
        F(rect(cx - 11.5, base - 35, 23, 2.4)),
        F(dome(cx, base - 34, 21, 15)),
        F(rect(cx - 2.2, base - 55, 4.4, 8)),
        F(tri(cx, base - 54.5, 5, 4)),
        S(f"M{cx} {base - 58} V{base - 62}", 1),
        F(rect(cx - 19, base - 34, 6, 13)), F(tri(cx - 16, base - 33.5, 6, 7)),
        F(rect(cx + 13, base - 34, 6, 13)), F(tri(cx + 16, base - 33.5, 6, 7)),
    ]


def shard(cx, base, top):
    return [F(poly((cx - 13, base), (cx - 9, top + 30), (cx - 2.5, top), (cx - .5, top + 5), (cx + 1, top + 1),
                   (cx + 4, top + 22), (cx + 13, base)), spot=True)]


def gherkin(cx, base, top, w=19):
    h = base - top
    return [F(f"M{cx - w * .42:g} {base:g} C{cx - w * .62:g} {base - h * .45:g} {cx - w * .45:g} {top + h * .08:g} {cx:g} {top:g} "
              f"C{cx + w * .45:g} {top + h * .08:g} {cx + w * .62:g} {base - h * .45:g} {cx + w * .42:g} {base:g}Z")]


def london(d: Drawing):
    y0 = 148
    d.disc("glow", 64, 62, 16)
    d.shape("light", cloud(140, 44, .8), line=False)
    layer(d, "far", towers([(4, 14, 120, "r"), (18, 10, 112, "p"), (96, 12, 100, "r"), (110, 10, 108, "a"), (170, 14, 104, "s"),
                            (184, 12, 116, "r"), (58, 12, 116, "r")]), line=False)
    layer(d, "near", towers([(-4, 18, 130, "r"), (12, 14, 124, "w"), (44, 14, 126, "r"), (102, 14, 112, "w"), (156, 12, 98, "r"),
                             (166, 16, 110, "s"), (180, 14, 124, "r"), (122, 10, 120, "r")]), lw=2)
    front = [*big_ben(36, y0 + 2, .95),
             F(poly((40, y0 + 2), (40, 132), *[(40 + i * 4 + dx, 132 - dy) for i in range(5) for dx, dy in ((1, 0), (2, 4), (3, 0))], (60, 132), (60, y0 + 2))),
             *london_eye(82, 104, 24, y0 + 2),
             *st_pauls(118, y0 + 2),
             *shard(143, y0 + 2, 30),
             *gherkin(166, y0 + 2, 84),
             F(rect(52, 138, 120, y0 + 2 - 138))]
    layer(d, "deep", front)
    ink(d, "far", "M159 92 L173 92 M157 104 L175 104 M157 116 L175 116 M157 128 L175 128 M160 98 L172 98 M158 110 L174 110 M158 122 L174 122", 1, line=False)
    ink(d, "far", "M136 120 L150 120 M138 100 L148 100 M140 80 L146 80 M141 60 L145 60", 1, line=False)
    if d.paper:
        d.shape("glow2", circle(36, 74.4, 4), shadow=False)
    else:
        d.raw("", f'<circle cx="36" cy="74.4" r="3.6" fill="{d.c["spot"]}" stroke="{d.c["ink"]}" stroke-width="1.3"/>')
    lights(d, [(108, 130, 3, 5), (114, 130, 3, 5), (121, 130, 3, 5), (127, 130, 3, 5), (45, 136, 2.5, 4), (51, 136, 2.5, 4)])
    water(d, y0, front)


# ================================================================ PARIS
def eiffel(cx, base, H, hw0):
    def y_at(t):
        return base - H * t

    def hw(t):
        return 2 + (hw0 - 2) * (1 - t) ** 3

    ts = [i / 40 for i in range(0, 34)]
    left = [(cx - hw(t), y_at(t)) for t in ts]
    right = [(cx + hw(t), y_at(t)) for t in reversed(ts)]
    tip = [(cx - 1.4, y_at(.9)), (cx - .6, y_at(.95)), (cx + .6, y_at(.95)), (cx + 1.4, y_at(.9))]
    ai = hw0 * .58
    outline = poly(*left, *tip, *right, close=False)
    outline += f" L{cx + ai:.1f} {base} A{ai:.1f} {H * .14:.1f} 0 0 0 {cx - ai:.1f} {base}Z"
    hole = poly((cx - 7, y_at(.2)), (cx - 2.4, y_at(.33)), (cx + 2.4, y_at(.33)), (cx + 7, y_at(.2)))
    out = [FE(outline + " " + hole, spot=True), S(f"M{cx} {y_at(.94)} V{base - H}", 1.2)]
    for t, extra, h in [(.17, 4, 5), (.35, 2.5, 4), (.8, 1.5, 3)]:
        w = hw(t) + extra
        out.append(F(rect(cx - w, y_at(t) - h / 2, 2 * w, h)))
    return out


def notre_dame(x, base):
    """Twin flat-topped west towers, nave with flying buttresses and the slim spire."""
    towers_ = (rect(x, base - 46, 12, 46) + " " + rect(x + 22, base - 46, 12, 46) + " " + rect(x + 11, base - 32, 12, 32)
               + " " + garch(x + 3, base - 42, 2.6, 14) + " " + garch(x + 6.4, base - 42, 2.6, 14)
               + " " + garch(x + 25, base - 42, 2.6, 14) + " " + garch(x + 28.4, base - 42, 2.6, 14)
               + " " + garch(x + 14, base - 14, 6, 14))
    return [
        FE(towers_),
        F(rect(x - 1, base - 47.5, 14, 2.4)), F(rect(x + 21, base - 47.5, 14, 2.4)),
        F(rect(x + 34, base - 24, 30, 24)),
        F(poly((x + 34, base - 24), (x + 37, base - 32), (x + 60, base - 32), (x + 64, base - 24))),
        F(poly((x + 46.6, base - 30), (x + 48.5, base - 68), (x + 50.4, base - 30))),
        S(f"M{x + 64} {base - 2} Q{x + 70} {base - 14} {x + 62} {base - 26} M{x + 56} {base - 2} Q{x + 64} {base - 12} {x + 57} {base - 24}", 1.6),
    ]


def sacre_coeur(cx, base):
    return [
        F(rect(cx - 16, base - 10, 32, 10)),
        F(rect(cx - 6, base - 20, 12, 11)), F(bulb(cx, base - 19.5, 15, 18)), S(f"M{cx} {base - 37} V{base - 42}", 1),
        F(rect(cx - 15, base - 15, 6, 6)), F(bulb(cx - 12, base - 14.5, 7.5, 8)),
        F(rect(cx + 9, base - 15, 6, 6)), F(bulb(cx + 12, base - 14.5, 7.5, 8)),
        F(rect(cx + 14, base - 30, 5, 20)), F(bulb(cx + 16.5, base - 29.5, 6, 7)),
    ]


def arc_triomphe(x, base, w=26, h=24):
    return [FE(rect(x, base - h, w, h) + " " + arch(x + w * .32, base - h * .62, w * .36, h * .62) + " "
               + rect(x + w * .3, base - h * .9, w * .4, 1.2)), F(rect(x - 1, base - h - 3, w + 2, 3.4))]


def paris(d: Drawing):
    y0 = 150
    d.disc("glow", 140, 66, 15)
    d.shape("light", cloud(18, 70, .8), line=False)
    layer(d, "far", towers([(104, 12, 102, "r"), (92, 8, 118, "r"), (176, 12, 110, "r"), (186, 10, 118, "r")]), line=False)
    hill = F("M120 170 V128 Q140 118 152 114 Q164 112 176 118 Q190 124 200 132 V170Z")
    layer(d, "near", [hill, *sacre_coeur(164, 115), *towers([(-6, 30, 132, "r"), (30, 22, 136, "w")])], lw=2)
    roofs = ("M-30 172 V144 H-6 L0 138 H12 L18 144 H30 V140 L34 136 H80 L84 140 V144 H96 L100 138 H112 L116 144 "
             "H170 L174 138 H186 L190 144 H230 V172Z")
    front = [F(roofs), *eiffel(68, y0, 118, 26), *notre_dame(112, y0 - 2), *arc_triomphe(26, y0 - 4)]
    layer(d, "deep", front)
    if d.paper:
        d.marks("glow2", circle(129, 128, 3.2))
    else:
        d.raw("", f'<circle cx="129" cy="128" r="3.2" fill="none" stroke="{d.c["ink"]}" stroke-width="1.3"/>')
    water(d, y0, front, glints=((24, 12), (100, 18), (160, 10)))


# ================================================================ ROME
def umbrella_pine(x, base, h, w):
    return [S(f"M{x} {base} C{x + 1} {base - h * .5} {x - 2} {base - h * .75} {x - 1} {base - h + 4}", 2.4),
            F(f"M{x - w / 2} {base - h + 6} Q{x - w / 2 + 2} {base - h - 6} {x} {base - h - 6} Q{x + w / 2 - 2} {base - h - 6} {x + w / 2} {base - h + 6}"
              f" Q{x} {base - h + 9} {x - w / 2} {base - h + 6}Z")]


def st_peters(cx, base):
    return [
        F(rect(cx - 25, base - 30, 50, 30)), F(poly((cx - 8, base - 30), (cx, base - 35), (cx + 8, base - 30))),
        F(rect(cx - 15, base - 46, 30, 17)),
        F(rect(cx - 17, base - 48, 34, 3)),
        F(f"M{cx - 16} {base - 47} C{cx - 16} {base - 64} {cx - 8} {base - 72} {cx} {base - 73} "
          f"C{cx + 8} {base - 72} {cx + 16} {base - 64} {cx + 16} {base - 47}Z"),
        F(rect(cx - 3, base - 82, 6, 10)), F(tri(cx, base - 81.5, 7, 4)), S(f"M{cx} {base - 85} V{base - 90} M{cx - 2} {base - 88} H{cx + 2}", 1),
        F(dome(cx - 21, base - 30, 9, 7)), F(dome(cx + 21, base - 30, 9, 7)),
    ]


def castel_sa(cx, base):
    return [
        F(crenel(cx - 22, base - 26, 44, 26, 9, 2.5)),
        F(rect(cx - 11, base - 38, 22, 13)),
        F(rect(cx - 4, base - 44, 8, 7)),
        F(f"M{cx - 1.6} {base - 44} V{base - 52} L{cx - 7} {base - 56} L{cx - 1} {base - 54} Q{cx} {base - 58} {cx + 1} {base - 54} "
          f"L{cx + 7} {base - 56} L{cx + 1.6} {base - 52} V{base - 44}Z"),
    ]


def vittoriano(x, base, w=50):
    cols = " ".join(rect(x + 9 + i * 4.1, base - 33, 2.2, 13) for i in range(8))
    quad = lambda qx: F(f"M{qx - 5} {base - 44} L{qx - 4} {base - 49} L{qx - 1} {base - 48} L{qx} {base - 53} L{qx + 2} {base - 49} "
                        f"L{qx + 5} {base - 50} L{qx + 4} {base - 44}Z")
    return [
        F(poly((x - 4, base), (x + 4, base - 14), (x + w - 4, base - 14), (x + w + 4, base))),
        FE(rect(x + 6, base - 36, w - 12, 23) + " " + cols),
        F(rect(x + 5, base - 37.5, w - 10, 3)),
        F(rect(x, base - 42, 10, 28)), F(rect(x + w - 10, base - 42, 10, 28)),
        quad(x + 5), quad(x + w - 5),
        F(rect(x + w / 2 - 4, base - 22, 8, 8)), F(f"M{x + w / 2 - 4} {base - 22} L{x + w / 2 - 2} {base - 28} L{x + w / 2 + 3} {base - 26} L{x + w / 2 + 4} {base - 22}Z"),
    ]


def colosseum(x, base):
    outer = poly((x, base), (x, base - 40), (x + 14, base - 41), (x + 16, base - 37), (x + 18, base - 32), (x + 24, base - 30),
                 (x + 26, base - 22), (x + 32, base - 20), (x + 34, base - 12), (x + 38, base - 10), (x + 38, base))
    holes = []
    for row, (y, h, lim) in enumerate([(base - 34, 7, 18), (base - 24, 8, 28), (base - 13, 9, 38)]):
        for i in range(7):
            ax = x + 2 + i * 5.2
            if ax + 3.2 < x + lim - 1:
                holes.append(arch(ax, y, 3.2, h))
    return [FE(outer + " " + " ".join(holes), spot=True)]


def rome(d: Drawing):
    y0 = 150
    d.disc("glow", 138, 62, 15)
    d.shape("light", cloud(14, 80, .7), line=False)
    layer(d, "far", towers([(96, 12, 110, "d"), (112, 14, 116, "r"), (130, 10, 112, "d"), (4, 14, 112, "d"), (180, 12, 112, "r")]), line=False)
    layer(d, "near", [*towers([(-8, 20, 126, "r"), (90, 16, 120, "g"), (150, 30, 124, "r")]),
                      *umbrella_pine(186, 150, 46, 34), *umbrella_pine(164, 150, 38, 26)], lw=2)
    front = [*st_peters(72, 152), *castel_sa(36, 152), *vittoriano(98, 152), *colosseum(146, 152),
             *umbrella_pine(150, 152, 56, 30), F(rect(10, 144, 170, 8))]
    layer(d, "deep", front)
    lights(d, [(64, 110, 2, 4), (70, 110, 2, 4), (76, 110, 2, 4)])
    water(d, y0, front)


# ================================================================ BARCELONA
def sagrada_fam(cx, base, s=1.0):
    out = []
    spec = [(0, 30, 13), (-16, 46, 9), (16, 46, 9), (-30, 64, 7.5), (-22, 56, 8), (22, 56, 8), (30, 64, 7.5), (-6, 52, 7), (6, 52, 7)]
    for dx, top, w in spec:
        out.append(F(gparab(cx + dx * s, base - (base - top) * 1 if s == 1 else top, base, w * .62 * s)))
    out.append(F(poly((cx - 34, base), (cx - 34, base - 22), (cx - 18, base - 34), (cx - 10, base - 26), (cx, base - 44),
                      (cx + 10, base - 26), (cx + 18, base - 34), (cx + 34, base - 22), (cx + 34, base))))
    out.append(S(f"M{cx} {32} V20 M{cx - 3.5} 24 H{cx + 3.5}", 1.8))
    for dx, top, w in spec[1:7]:
        out.append(F(circle(cx + dx, top - 2.5, 2.4)))
    out[0] = ("f", out[0][1], True)
    return out


def torre_glories(cx, base, top, w=22):
    h = base - top
    return [F(f"M{cx - w / 2} {base} V{top + h * .3} C{cx - w / 2} {top + 4} {cx - w * .3} {top} {cx} {top} "
              f"C{cx + w * .3} {top} {cx + w / 2} {top + 4} {cx + w / 2} {top + h * .3} V{base}Z")]


def palau_nacional(cx, base):
    return [F(rect(cx - 24, base - 14, 48, 14)), F(rect(cx - 9, base - 24, 18, 11)), F(dome(cx, base - 23.5, 18, 11)),
            S(f"M{cx} {base - 34} V{base - 39}", 1.4),
            *[F(rect(tx - 2.5, base - 26, 5, 13)) for tx in (cx - 20, cx + 20)],
            *[F(tri(tx, base - 25.5, 5, 6)) for tx in (cx - 20, cx + 20)]]


def barcelona(d: Drawing):
    y0 = 152
    d.disc("glow", 58, 62, 15)
    d.shape("light", cloud(140, 36, .8), line=False)
    layer(d, "far", towers([(124, 10, 112, "r"), (176, 12, 116, "r"), (186, 10, 124, "r"), (60, 12, 118, "r")]), line=False)
    hill = F("M-30 170 V128 Q0 108 30 104 Q52 104 70 120 Q80 128 88 140 V170Z")
    layer(d, "near", [hill, *palau_nacional(30, 106), *towers([(132, 14, 120, "r"), (170, 14, 126, "w")])], lw=2)
    column = [F(rect(62, 136, 12, 18)), F(rect(64.5, 130, 7, 7)), F(rect(66.6, 92, 2.8, 40)), F(circle(68, 89, 3.2)),
              F(rect(66.8, 80, 2.4, 7)), F(circle(68, 79, 1.6))]
    front = [*sagrada_fam(108, 154), *torre_glories(158, 154, 52), *column,
             F("M-30 154 V144 H40 L44 140 H80 V146 H178 V138 H190 V144 H230 V154Z")]
    layer(d, "deep", front)
    ink(d, "far", " ".join(f"M{150} {y} H{166}" for y in range(66, 146, 8)) + " M158 56 V146", 1, line=False)
    lights(d, [(150, 70, 2, 3), (156, 86, 2, 3), (162, 102, 2, 3), (152, 118, 2, 3), (160, 130, 2, 3)])
    water(d, y0, front, glints=((26, 12), (96, 22), (150, 12)))


# ================================================================ MADRID
def metropolis(x, base):
    """Curved-corner block with a dark cupola and the winged Victory on top."""
    cx = x + 15
    return [
        F(f"M{x} {base} V{base - 40} Q{x} {base - 46} {x + 6} {base - 46} H{x + 24} Q{x + 30} {base - 46} {x + 30} {base - 40} V{base}Z"),
        F(rect(cx - 9, base - 54, 18, 9)),
        F(dome(cx, base - 53.5, 18, 12)),
        F(rect(cx - 2, base - 70, 4, 6)),
        F(f"M{cx - 1.5} {base - 70} V{base - 76} L{cx - 9} {base - 82} L{cx - 3} {base - 78} L{cx} {base - 82} "
          f"L{cx + 3} {base - 78} L{cx + 9} {base - 82} L{cx + 1.5} {base - 76} V{base - 70}Z", spot=True),
    ]


def puerta_alcala(x, base, w=64):
    holes = [rect(x + 5, base - 20, 6, 15), arch(x + 16, base - 26, 8, 26), arch(x + w / 2 - 5, base - 28, 10, 28),
             arch(x + w - 24, base - 26, 8, 26), rect(x + w - 11, base - 20, 6, 15)]
    cx = x + w / 2
    return [FE(rect(x, base - 34, w, 34) + " " + " ".join(holes), spot=True),
            F(rect(x - 1.5, base - 36, w + 3, 3)),
            F(rect(cx - 12, base - 44, 24, 9)),
            F(f"M{cx - 9} {base - 44} L{cx - 6} {base - 50} L{cx - 2} {base - 49} L{cx} {base - 54} L{cx + 2} {base - 49} "
              f"L{cx + 6} {base - 50} L{cx + 9} {base - 44}Z"),
            F(f"M{x + 2} {base - 36} L{x + 4} {base - 42} L{x + 7} {base - 36}Z"),
            F(f"M{x + w - 7} {base - 36} L{x + w - 4} {base - 42} L{x + w - 2} {base - 36}Z")]


def kio(x, base):
    """Gate of Europe: two towers leaning towards each other."""
    return [F(poly((x, base), (x + 12, base - 52), (x + 26, base - 52), (x + 14, base))),
            F(poly((x + 48, base), (x + 36, base - 52), (x + 22, base - 52), (x + 34, base))),
            S(f"M{x + 13} {base - 52} V{base - 56} M{x + 35} {base - 52} V{base - 56}", 1)]


def cuatro_torres(x, base):
    t1 = rect(x, 56, 10, base - 56) + " " + rect(x + 2.5, 50, 5, 6)
    return [FE(poly((x - 1, base), (x - 1, 50), (x + 11, 50), (x + 11, base)) + " " + rect(x + 1.5, 52, 7, 6)),
            F(f"M{x + 14} {base} V{52} Q{x + 18.5} {44} {x + 23} {52} V{base}Z"),
            F(poly((x + 26, base), (x + 26, 48), (x + 36, 44), (x + 36, base))),
            F(rect(x + 39, 56, 9, base - 56)), S(f"M{x + 39} 54 Q{x + 43.5} 46 {x + 48} 54", 1.4)]


def madrid(d: Drawing):
    d.disc("glow", 62, 66, 16)
    d.shape("light", cloud(76, 38, .7), line=False)
    layer(d, "far", towers([(-10, 18, 110, "r"), (100, 12, 104, "r"), (176, 12, 108, "r"), (186, 10, 120, "r")]), line=False)
    layer(d, "near", [*cuatro_torres(122, 160), *towers([(56, 14, 114, "d"), (90, 14, 118, "r")])], lw=2)
    front = [*metropolis(20, 152), *puerta_alcala(54, 152), *kio(126, 152),
             F("M-30 160 V140 H22 V152 H180 V136 H230 V160Z")]
    layer(d, "deep", front)
    lights(d, [(24, 112, 2.5, 4), (30, 112, 2.5, 4), (36, 112, 2.5, 4), (42, 112, 2.5, 4),
               (24, 124, 2.5, 4), (30, 124, 2.5, 4), (36, 124, 2.5, 4), (42, 124, 2.5, 4)])
    trees(d, 154, role="deep", r=8, step=13)
    d.band("mid", "M-30 170 Q100 164 230 170", line=False)


# ================================================================ LISBON
def belem(cx, base):
    tw = 20
    turret = lambda tx, ty: [F(rect(tx - 2.2, ty - 5, 4.4, 5)), F(dome(tx, ty - 4.8, 5, 3.6))]
    return [
        F(crenel(cx - 20, base - 18, 40, 18, 7, 2.2)),
        *turret(cx - 18, base - 18), *turret(cx + 18, base - 18),
        F(rect(cx - tw / 2, base - 52, tw, 36)),
        F(crenel(cx - tw / 2 - 1, base - 58, tw + 2, 7, 4, 2)),
        *turret(cx - tw / 2, base - 52), *turret(cx + tw / 2, base - 52),
        F(rect(cx - 6, base - 66, 12, 9)), F(crenel(cx - 7, base - 68, 14, 3, 3, 1.5)),
    ]


def padrao(x, base):
    return [F(poly((x, base), (x, base - 6), (x + 4, base - 50), (x + 9, base - 50), (x + 10, base - 30), (x + 14, base - 26),
                   (x + 20, base - 20), (x + 26, base - 15), (x + 32, base - 10), (x + 40, base - 6), (x + 42, base)))]


def cristo_rei(cx, base):
    return [F(poly((cx - 8, base), (cx - 5, base - 36), (cx + 5, base - 36), (cx + 8, base))),
            F(rect(cx - 6, base - 38, 12, 3)),
            F(poly((cx - 1.8, base - 38), (cx - 2.4, base - 46), (cx - 8, base - 47), (cx - 8, base - 49), (cx - 2, base - 49),
                   (cx - 1.4, base - 52), (cx + 1.4, base - 52), (cx + 2, base - 49), (cx + 8, base - 49), (cx + 8, base - 47),
                   (cx + 2.4, base - 46), (cx + 1.8, base - 38))),
            F(circle(cx, base - 53.5, 1.9))]


def bridge_25abril(d: Drawing, deck=124, tx=128, top=66):
    """Red suspension bridge from the left bank, one tower, running off to the right."""
    cab = f"M60 {deck - 2} Q{(60 + tx) / 2} {deck - 4} {tx} {top + 2} Q{tx + 46} {deck - 6} {tx + 100} {top + 8}"
    hangers = " ".join(f"M{x} {deck} V{deck - 2 - (1 - ((x - (tx + 50)) / 50) ** 2) * 0 - (deck - top) * (((x - tx - 46) / 54) ** 2) * .9:.1f}"
                       for x in range(tx + 8, 200, 7))
    hang_l = " ".join(f"M{x} {deck} V{deck - (deck - top) * (((x - 60) / (tx - 60)) ** 2) * .95 - 2:.1f}" for x in range(74, tx - 2, 7))
    items = [F(rect(40, deck, 200, 5)), S(cab, 1.8), T(hangers + " " + hang_l, .7),
             F(poly((tx - 6, 160), (tx - 4.5, top), (tx - 1.5, top), (tx - 1.5, 160)), spot=True),
             F(poly((tx + 1.5, 160), (tx + 1.5, top), (tx + 4.5, top), (tx + 6, 160)), spot=True),
             F(rect(tx - 5, top + 10, 10, 2.4)), F(rect(tx - 5.5, top + 30, 11, 2.6)), F(rect(tx - 6, deck - 6, 12, 2.6))]
    layer(d, "bridge", items, lw=2.4)


def lisbon(d: Drawing):
    y0 = 150
    d.disc("glow", 92, 58, 14)
    farbank = F("M96 170 V128 Q120 120 150 112 Q172 106 230 108 V170Z")
    layer(d, "far", [farbank], line=False)
    layer(d, "near", [*cristo_rei(170, 110), F("M140 170 V116 Q166 106 200 110 V170Z"),
                      *towers([(30, 12, 112, "r"), (60, 14, 118, "g")])], lw=2)
    bridge_25abril(d, deck=126, tx=136, top=74)
    hill = ("M-30 170 V112 Q-10 100 6 98 Q30 96 50 108 Q66 118 78 132 L84 146 H-30Z")
    castle = [F(crenel(-2, 82, 40, 18, 7, 2.6)), F(crenel(4, 72, 10, 12, 2, 2.2)), F(crenel(24, 74, 10, 10, 2, 2.2))]
    roofs = [F(gables(x, y, w, "tri")) for x, y, w in [(36, 108, 12), (46, 114, 12), (56, 120, 12), (2, 102, 12), (14, 104, 10)]]
    front = [F(hill), *castle, *roofs, *belem(86, 152), F(rect(-30, 144, 90, 10)), F(rect(60, 146, 50, 8))]
    layer(d, "deep", front)
    lights(d, [(42, 120, 2.5, 4), (52, 126, 2.5, 4), (62, 132, 2.5, 4), (20, 112, 2.5, 4), (8, 116, 2.5, 4), (30, 116, 2.5, 4)])
    if d.paper:
        d.shape("glow2", "M80 108 L84 106 L84 112 L80 112Z", shadow=False)
    water(d, y0, front, glints=((20, 10), (120, 18), (160, 12)))
    if d.paper:
        d.raw(f'<g opacity=".25" fill="{d.c["bridge"]}"><rect x="40" y="{2 * y0 - 131}" width="200" height="4"/>'
              f'<rect x="130" y="{y0}" width="12" height="40"/></g>')


# ================================================================ AMSTERDAM
def westerkerk(cx, base):
    return [F(rect(cx - 7, base - 66, 14, 66)),
            F(rect(cx - 8, base - 68, 16, 3)),
            F(rect(cx - 5.5, base - 80, 11, 13)),
            F(rect(cx - 6.5, base - 81.5, 13, 2.4)),
            F(rect(cx - 4, base - 90, 8, 9)),
            F(bulb(cx, base - 89.5, 9, 9)),
            F(rect(cx - 2.6, base - 101, 5.2, 4)),
            F(f"M{cx - 3.2} {base - 101} Q{cx - 4} {base - 106} {cx} {base - 107} Q{cx + 4} {base - 106} {cx + 3.2} {base - 101}Z", spot=True),
            S(f"M{cx} {base - 107} V{base - 114}", 1.1)]


def canal_houses(x0, base, spec):
    """spec: (width, top, gable). Returns (items, separators, windows)."""
    items, seps, wins = [], [], []
    x = x0
    for w, top, kind in spec:
        items.append(F(rect(x, top, w, base - top)))
        items.append(F(gables(x, top, w, kind)))
        seps.append(f"M{x} {top + 2} V{base}")
        for r in range(3):
            for c in range(2):
                wins.append((x + w * .2 + c * w * .38, top + 4 + r * 9, w * .22, 5))
        x += w
    return items, " ".join(seps[1:]), wins


def windmill(cx, base, r=20, hub=None):
    hy = hub or base - 40
    sails = []
    for a in (40, 130, 220, 310):
        t = math.radians(a)
        ex, ey = cx + r * math.cos(t), hy + r * math.sin(t)
        nx, ny = -math.sin(t) * 3.4, math.cos(t) * 3.4
        sails.append(F(poly((cx + nx * .3, hy + ny * .3), (ex + nx * .3, ey + ny * .3), (ex + nx, ey + ny),
                            (cx + (ex - cx) * .25 + nx, hy + (ey - hy) * .25 + ny))))
    return [F(poly((cx - 9, base), (cx - 6, hy + 4), (cx + 6, hy + 4), (cx + 9, base))),
            F(f"M{cx - 7} {hy + 5} Q{cx} {hy - 8} {cx + 7} {hy + 5}Z"),
            F(rect(cx - 12, base - 18, 24, 2.4)),
            *sails, F(circle(cx, hy, 2.2))]


def amsterdam(d: Drawing):
    y0 = 150
    d.disc("glow", 150, 62, 14)
    d.shape("light", cloud(20, 60, .8), line=False)
    layer(d, "far", towers([(-6, 16, 104, "r"), (40, 12, 100, "g"), (118, 12, 98, "g"), (176, 14, 108, "r")]), line=False)
    layer(d, "near", [*windmill(166, 140, 22, 98), F(rect(148, 120, 40, 40)), *towers([(10, 14, 96, "g"), (52, 12, 104, "g")])], lw=2)
    spec = [(13, 110, "step"), (12, 104, "bell"), (14, 112, "neck"), (12, 100, "step"), (14, 106, "tri"), (12, 110, "bell"),
            (13, 102, "neck"), (12, 112, "step"), (14, 106, "bell"), (13, 114, "tri")]
    items, seps, wins = canal_houses(22, 152, spec)
    front = [*westerkerk(92, 152), *items, F(rect(-30, 144, 260, 10))]
    layer(d, "deep", front)
    ink(d, "near", seps, 1, line_w=1.2)
    lights(d, [w for w in wins if not (84 < w[0] < 100)])
    water(d, y0, front, glints=((14, 10), (136, 16), (168, 8)))
    # humpback bridge over the canal, with a parked bike
    bridge = FE("M30 166 V150 Q70 136 110 150 V166Z " + "M44 166 V160 A26 12 0 0 1 96 160 V166Z")
    layer(d, "deep", [bridge, S("M36 146 Q70 133 104 146", 1.4), T("M48 142 V146 M60 139 V143 M72 138 V142 M84 139 V143 M96 142 V146", 1)])
    d.stroke("deep", "M126 150 Q130 140 134 150", 2.6, line=False)
    bike = f"{circle(122, 147, 4)} {circle(134, 147, 4)}"
    layer(d, "deep", [S(bike, 1.2), S("M122 147 L126 141 L132 141 L134 147 M126 141 L128 147 L132 141 M125 139 H128 M132 141 L131 138 H134", 1.1)], lw=1.6)


# ================================================================ BERLIN
def brandenburg(x, base, w=58):
    cols = " ".join(rect(x + 4 + i * (w - 8) / 5 + 2.6, base - 24, (w - 8) / 5 - 5.2, 24) for i in range(5))
    cx = x + w / 2
    return [FE(rect(x, base - 32, w, 32) + " " + cols, spot=True),
            F(rect(x - 2, base - 34, w + 4, 3)),
            F(rect(cx - 13, base - 40, 26, 7)),
            F(poly((cx - 13, base - 40), (cx - 8, base - 44), (cx + 8, base - 44), (cx + 13, base - 40))),
            F(f"M{cx - 7} {base - 44} L{cx - 6} {base - 49} L{cx - 3} {base - 48} L{cx - 1} {base - 53} L{cx + 1} {base - 50} "
              f"L{cx + 2} {base - 55} L{cx + 3} {base - 50} L{cx + 6} {base - 50} L{cx + 7} {base - 44}Z")]


def fernsehturm(cx, base, ball_y, top):
    return [F(poly((cx - 4, base), (cx - 2.4, ball_y), (cx + 2.4, ball_y), (cx + 4, base))),
            F(circle(cx, ball_y, 11), spot=True),
            F(rect(cx - 6, ball_y - 13, 12, 3)),
            F(poly((cx - 2, ball_y - 12), (cx - 1.2, ball_y - 24), (cx + 1.2, ball_y - 24), (cx + 2, ball_y - 12))),
            S(f"M{cx} {ball_y - 24} V{top}", 1.4),
            F(rect(cx - 9, base - 8, 18, 8))]


def reichstag(x, base, w=40):
    cx = x + w / 2
    return [F(rect(x + 4, base - 26, w - 8, 26)),
            F(rect(x, base - 32, 9, 32)), F(rect(x + w - 9, base - 32, 9, 32)),
            F(rect(cx - 8, base - 34, 16, 9)), F(poly((cx - 8, base - 34), (cx, base - 38), (cx + 8, base - 34))),
            F(rect(cx - 9, base - 30, 18, 3)),
            F(f"M{cx - 9} {base - 38} A9 11 0 0 1 {cx + 9} {base - 38}Z", spot=True)]


def berlin_dom(cx, base):
    return [F(rect(cx - 18, base - 28, 36, 28)),
            F(rect(cx - 9, base - 40, 18, 13)),
            F(f"M{cx - 10} {base - 39} C{cx - 10} {base - 52} {cx - 4} {base - 56} {cx} {base - 57} "
              f"C{cx + 4} {base - 56} {cx + 10} {base - 52} {cx + 10} {base - 39}Z"),
            F(rect(cx - 1.6, base - 63, 3.2, 7)), F(circle(cx, base - 64, 1.8)),
            *[F(rect(tx - 3, base - 36, 6, 9)) for tx in (cx - 15, cx + 15)],
            *[F(dome(tx, base - 35.5, 6, 5)) for tx in (cx - 15, cx + 15)]]


def berlin(d: Drawing):
    y0 = 152
    d.disc("glow", 60, 64, 15)
    d.shape("light", cloud(150, 48, .7), line=False)
    layer(d, "far", towers([(-6, 16, 112, "r"), (86, 12, 108, "r"), (150, 12, 104, "a"), (172, 14, 112, "r")]), line=False)
    layer(d, "near", [*berlin_dom(96, 140), *towers([(-10, 30, 124, "r"), (176, 20, 126, "w")])], lw=2)
    front = [*brandenburg(22, 154), *fernsehturm(132, 154, 62, 22), *reichstag(144, 154), F(rect(-30, 146, 260, 8))]
    layer(d, "deep", front)
    lights(d, [(150, 132, 2, 4), (156, 132, 2, 4), (166, 132, 2, 4), (172, 132, 2, 4)])
    if d.paper:
        d.marks("near", f"M126 62 H138" + f" M{132} 51 V73")
        d.stroke("glow2", "M123.5 60 H140.5", 1.4)
    water(d, y0, front)


# ================================================================ PRAGUE
def st_vitus(x, base):
    """Cathedral on the castle: twin west spires, nave with pinnacles, the great south tower with its baroque cap."""
    return [F(rect(x, base - 14, 46, 14)),
            F(poly((x, base - 14), (x + 4, base - 22), (x + 42, base - 22), (x + 46, base - 14))),
            F(rect(x + 1, base - 40, 7, 26)), F(tri(x + 4.5, base - 39.5, 7, 16)),
            F(rect(x + 10, base - 40, 7, 26)), F(tri(x + 13.5, base - 39.5, 7, 16)),
            *[F(tri(px, base - 21.5, 3, 7)) for px in (x + 22, x + 27, x + 32, x + 41)],
            F(rect(x + 30, base - 54, 11, 40)),
            F(rect(x + 29, base - 56, 13, 3)),
            F(bulb(x + 35.5, base - 55.5, 13, 12)),
            F(rect(x + 33.5, base - 72, 4, 6)), F(bulb(x + 35.5, base - 71.5, 6, 8))]


def tyn(cx, base):
    def twr(tx):
        return [F(rect(tx - 5, base - 46, 10, 46)),
                F(tri(tx, base - 45.5, 11, 20)),
                F(tri(tx - 5, base - 44, 3.4, 10)), F(tri(tx + 5, base - 44, 3.4, 10)),
                F(tri(tx - 3, base - 52, 2.6, 9)), F(tri(tx + 3, base - 52, 2.6, 9))]
    return [F(rect(cx - 13, base - 30, 26, 30)), F(tri(cx, base - 29.5, 16, 12)), *twr(cx - 9), *twr(cx + 9)]


def prague(d: Drawing):
    y0 = 150
    d.disc("glow", 108, 58, 14)
    layer(d, "far", [F("M-30 170 V112 Q20 96 60 104 Q90 112 120 118 V170Z"),
                     *towers([(120, 12, 106, "g"), (184, 12, 110, "r")])], line=False)
    layer(d, "near", towers([(98, 12, 112, "g"), (110, 10, 118, "r"), (178, 16, 116, "g"), (132, 12, 116, "d")]), lw=2)
    hill = F("M-30 170 V122 Q-8 112 6 110 H90 Q104 116 112 132 V170Z")
    castle = F(rect(4, 100, 42, 14))
    front = [hill, castle, F(poly((4, 100), (6, 96), (44, 96), (46, 100))), *st_vitus(42, 112), *tyn(160, 146),
             F(rect(108, 138, 70, 16))]
    layer(d, "deep", front)
    lights(d, [(9, 104, 2, 3.5), (15, 104, 2, 3.5), (21, 104, 2, 3.5), (27, 104, 2, 3.5), (33, 104, 2, 3.5), (39, 104, 2, 3.5),
               (156, 124, 2, 4), (162, 124, 2, 4), (152, 136, 2, 4)])
    water(d, y0, front, glints=((24, 10), (90, 16), (160, 12)))
    # Charles Bridge and its Old Town bridge tower
    arches = " ".join(arch(x, 146, 16, 16) for x in range(-24, 120, 22))
    statues = " ".join(rect(x, 136, 2, 4) + " " + circle(x + 1, 135, 1.3) for x in range(-20, 120, 11))
    br = [FE(rect(-30, 140, 150, 22) + " " + arches), F(rect(-30, 138, 150, 3)), F(statues),
          FE(rect(110, 102, 20, 52) + " " + arch(114, 128, 12, 26)),
          F(poly((109, 103), (120, 78), (131, 103))),
          F(tri(110.5, 103, 3.6, 12)), F(tri(129.5, 103, 3.6, 12)), F(tri(120, 82, 3, 10))]
    layer(d, "deep", br)


# ================================================================ VIENNA
def riesenrad(cx, cy, r, base):
    gond = [F(rect(cx + (r + 2.5) * math.cos(i * math.pi / 6) - 2.4, cy + (r + 2.5) * math.sin(i * math.pi / 6) - 1.8, 4.8, 3.6))
            for i in range(12)]
    spokes = " ".join(f"M{cx + r * math.cos(i * math.pi / 6 + .26):.1f} {cy + r * math.sin(i * math.pi / 6 + .26):.1f} "
                      f"L{cx - r * math.cos(i * math.pi / 6 + .26):.1f} {cy - r * math.sin(i * math.pi / 6 + .26):.1f}" for i in range(6))
    return [S(circle(cx, cy, r), 2.6), S(circle(cx, cy, r - 5), 1), T(spokes, .8), *gond, F(circle(cx, cy, 3)),
            S(f"M{cx} {cy} L{cx - r * .5:.1f} {base} M{cx} {cy} L{cx + r * .5:.1f} {base}", 2.4),
            F(rect(cx - r * .7, base - 8, r * 1.4, 8))]


def stephansdom(sx, base):
    """South tower spire at sx, with the steep patterned roof running to the right."""
    tw = poly((sx - 9, base), (sx - 8, base - 48), (sx - 6, base - 66), (sx - 4.5, base - 90), (sx - 1.6, base - 112),
              (sx, base - 120), (sx + 1.6, base - 112), (sx + 4.5, base - 90), (sx + 6, base - 66), (sx + 8, base - 48), (sx + 9, base))
    crockets = poly(*[(sx + side * (6.4 - 5.2 * t) + side * (1.6 if i % 2 else 0), base - 66 - 46 * t)
                      for side in (-1,) for i, t in enumerate([j / 12 for j in range(13)])], close=False)
    crockets_r = poly(*[(sx + (6.4 - 5.2 * t) + (1.6 if i % 2 else 0), base - 66 - 46 * t) for i, t in enumerate([j / 12 for j in range(13)])], close=False)
    roof = poly((sx + 6, base), (sx + 6, base - 34), (sx + 14, base - 56), (sx + 48, base - 56), (sx + 56, base - 34), (sx + 56, base))
    return [F(tw, spot=True), S(crockets + " " + crockets_r, 1.2), F(roof), F(rect(sx + 6, base - 34, 54, 34)),
            F(tri(sx + 58, base - 33.5, 5, 10))]


def karlskirche(cx, base):
    col = lambda x: [F(rect(x - 3.2, base - 50, 6.4, 50)), F(rect(x - 4.4, base - 54, 8.8, 4.4)),
                     F(rect(x - 2, base - 60, 4, 6)), F(tri(x, base - 59.5, 4.6, 5))]
    return [F(rect(cx - 26, base - 24, 52, 24)),
            F(rect(cx - 9, base - 32, 18, 9)), F(tri(cx, base - 31.5, 22, 8)),
            F(rect(cx - 11, base - 46, 22, 15)),
            F(f"M{cx - 12} {base - 45} C{cx - 12} {base - 60} {cx - 5} {base - 64} {cx} {base - 64} "
              f"C{cx + 5} {base - 64} {cx + 12} {base - 60} {cx + 12} {base - 45}Z"),
            F(rect(cx - 2, base - 72, 4, 8)), F(tri(cx, base - 71.5, 5, 5)),
            *col(cx - 20), *col(cx + 20),
            *[F(rect(tx - 4, base - 34, 8, 10)) for tx in (cx - 29, cx + 29)],
            *[F(bulb(tx, base - 33.5, 8, 8)) for tx in (cx - 29, cx + 29)]]


def vienna(d: Drawing):
    d.disc("glow", 148, 54, 13)
    d.shape("light", cloud(54, 44, .7), line=False)
    layer(d, "far", towers([(118, 8, 50, "r"), (4, 14, 108, "r"), (76, 12, 104, "r"), (176, 14, 104, "r")]), line=False)
    layer(d, "near", towers([(-8, 22, 122, "g"), (64, 16, 116, "r"), (118, 14, 112, "g"), (186, 16, 120, "r")]), lw=2)
    front = [*riesenrad(42, 104, 25, 154), *stephansdom(92, 154), *karlskirche(160, 154), F(rect(-30, 144, 260, 12))]
    layer(d, "deep", front)
    if d.paper:
        zz = " ".join(poly(*[(108 + i * 5, y + (2.6 if i % 2 else 0)) for i in range(9)], close=False) for y in (104, 110, 116))
        d.stroke("glow2", zz, 1.4)
        d.stroke("pop", poly(*[(108 + i * 5, 122 + (2.6 if i % 2 else 0)) for i in range(9)], close=False), 1.4)
    else:
        zz = " ".join(poly(*[(108 + i * 5, y + (2.6 if i % 2 else 0)) for i in range(9)], close=False) for y in (106, 114))
        d.raw("", f'<path d="{zz}" fill="none" stroke="{d.c["ink"]}" stroke-width="1.3" stroke-linejoin="round"/>')
    lights(d, [(150, 132, 2.5, 5), (156, 132, 2.5, 5), (164, 132, 2.5, 5), (170, 132, 2.5, 5)])
    trees(d, 152, role="deep", r=8, step=13)
    d.band("mid", "M-30 170 Q100 164 230 170", line=False)


# ================================================================ BUDAPEST
def parliament_hu(x, base, w=98):
    cx = x + 48
    pins = " ".join(tri(px, base - 34, 2.6, 8) for px in range(int(x) + 3, int(x + w), 6))
    return [F(rect(x, base - 34, w, 34)),
            F(pins),
            F(rect(x + 2, base - 44, 10, 12)), F(tri(x + 7, base - 43.5, 12, 10)),
            F(rect(x + w - 12, base - 44, 10, 12)), F(tri(x + w - 7, base - 43.5, 12, 10)),
            F(rect(cx - 22, base - 50, 9, 18)), F(tri(cx - 17.5, base - 49.5, 9, 18)),
            F(rect(cx + 13, base - 50, 9, 18)), F(tri(cx + 17.5, base - 49.5, 9, 18)),
            F(rect(cx - 12, base - 56, 24, 22)),
            F(f"M{cx - 13} {base - 55} C{cx - 13} {base - 70} {cx - 6} {base - 76} {cx} {base - 78} "
              f"C{cx + 6} {base - 76} {cx + 13} {base - 70} {cx + 13} {base - 55}Z", spot=True),
            F(poly((cx - 2.4, base - 77), (cx, base - 92), (cx + 2.4, base - 77))),
            *[F(tri(px, base - 55.5, 2.6, 9)) for px in (cx - 12, cx + 12)]]


def chain_bridge(x0, x1, deck, top):
    def pylon(px):
        return [FE(rect(px - 8, top, 16, 160 - top) + " " + arch(px - 4.5, deck - 18, 9, 18) + " " + rect(px - 4.5, deck + 4, 9, 20)),
                F(rect(px - 9, top - 3, 18, 4))]
    xa, xb = x0 + 14, x1 - 14
    mid = (xa + xb) / 2
    chain = f"M{x0 - 40} {deck - 2} Q{x0 - 10} {deck - 6} {xa} {top + 4} Q{mid} {deck + 18} {xb} {top + 4} Q{x1 + 4} {deck - 6} {x1 + 14} {deck}"
    hang = " ".join(f"M{x} {deck} V{top + 4 + (deck - top) * (1 - ((x - mid) / ((xb - xa) / 2)) ** 2) * .82:.1f}" for x in range(int(xa) + 7, int(xb), 6))
    return [F(rect(x0 - 60, deck, x1 - x0 + 76, 4)), S(chain, 2), T(hang, .7), *pylon(xa), *pylon(xb)]


def budapest(d: Drawing):
    y0 = 150
    d.disc("glow", 100, 56, 13)
    hill = F("M-30 170 V108 Q-4 92 22 90 Q44 90 60 104 Q72 114 80 126 V170Z")
    buda = [F(rect(0, 82, 54, 12)), F(rect(20, 70, 14, 13)), F(rect(18.5, 68.5, 17, 2.4)), F(dome(27, 69, 15, 13)),
            F(rect(25.6, 50, 2.8, 7)), F(circle(27, 49, 1.8)), F(tri(4, 82.5, 6, 8)), F(tri(50, 82.5, 6, 8))]
    layer(d, "far", towers([(110, 10, 112, "r"), (180, 12, 112, "r")]), line=False)
    layer(d, "near", [hill, *buda, *towers([(100, 14, 116, "r"), (150, 12, 112, "d")])], lw=2)
    front = [*parliament_hu(88, 152), F(rect(80, 144, 120, 10))]
    layer(d, "deep", front)
    lights(d, [(x, 128, 2, 5) for x in range(92, 186, 6) if not 124 < x < 150] + [(x, 138, 2, 4) for x in range(92, 186, 6)])
    water(d, y0, front, glints=((20, 10), (110, 16), (160, 12)))
    layer(d, "deep", chain_bridge(-4, 70, 132, 100), lw=2.6)


# ================================================================ EDINBURGH
def scott_monument(cx, base, h=88):
    t = lambda f: base - h * f
    body = poly((cx - 11, base), (cx - 9, t(.36)), (cx - 7, t(.5)), (cx - 5, t(.66)), (cx - 3.2, t(.8)), (cx - 1.4, t(.93)), (cx, t(1)),
                (cx + 1.4, t(.93)), (cx + 3.2, t(.8)), (cx + 5, t(.66)), (cx + 7, t(.5)), (cx + 9, t(.36)), (cx + 11, base))
    holes = garch(cx - 4, base - 22, 8, 22) + " " + garch(cx - 2.5, t(.46), 5, 9) + " " + garch(cx - 1.6, t(.64), 3.2, 7)
    pins = " ".join(tri(cx + s * dx, y, 2.6, 9) for s in (-1, 1) for dx, y in ((10, t(.34)), (8, t(.48)), (6, t(.64)), (4.2, t(.78))))
    return [FE(body + " " + holes, spot=True), F(pins),
            F(tri(cx - 13, base - 30, 3, 12)), F(rect(cx - 14.5, base - 30, 3, 30)),
            F(tri(cx + 13, base - 30, 3, 12)), F(rect(cx + 11.5, base - 30, 3, 30))]


def balmoral(cx, base):
    return [F(rect(cx - 13, base - 40, 26, 40)), F(rect(cx - 6, base - 66, 12, 28)), F(rect(cx - 7, base - 68, 14, 3)),
            F(rect(cx - 4, base - 76, 8, 9)), F(dome(cx, base - 75.5, 8, 4)), S(f"M{cx} {base - 80} V{base - 86}", 1),
            *[F(rect(tx - 2, base - 46, 4, 7)) for tx in (cx - 11, cx + 11)]]


def edinburgh(d: Drawing):
    d.disc("glow", 150, 62, 13)
    d.shape("light", cloud(80, 44, .7), line=False)
    seat = F("M60 170 V124 Q100 120 124 100 Q132 92 140 98 L150 92 Q160 86 166 96 Q172 108 190 114 Q210 120 230 126 V170Z")
    layer(d, "far", [seat], line=False)
    calton = [F("M140 170 V132 Q160 120 200 124 V170Z"),
              F(rect(150, 112, 7, 16)), F(rect(149, 108, 9, 4)), F(rect(150.5, 102, 6, 6)), F(rect(151.5, 98, 4, 4)),
              FE(rect(166, 116, 26, 12) + " " + " ".join(rect(168.5 + i * 4.2, 120, 2.2, 8) for i in range(5)))]
    layer(d, "near", [*calton, *towers([(84, 14, 116, "r"), (64, 12, 122, "g")])], lw=2)
    rock = F("M-30 170 V132 Q-14 128 -8 118 L0 106 L6 103 H60 L66 108 L70 122 L76 128 Q80 134 88 138 V170Z")
    castle = [F(crenel(2, 92, 26, 13, 5, 2.4)), F(rect(28, 86, 24, 19)), F(poly((27, 87), (31, 80), (49, 80), (53, 87))),
              F(crenel(50, 96, 12, 10, 3, 2)), F(rect(10, 82, 8, 11)), F(tri(14, 82.5, 9, 8)),
              S("M40 80 V66", 1.2), F("M40 66 H49 V72 H40Z", spot=True)]
    front = [rock, *castle, *scott_monument(100, 152), *balmoral(140, 152), F(rect(-30, 140, 260, 16))]
    layer(d, "deep", front)
    lights(d, [(31, 92, 2.5, 4), (37, 92, 2.5, 4), (43, 92, 2.5, 4), (6, 98, 2, 3.5), (12, 98, 2, 3.5), (18, 98, 2, 3.5)])
    if d.paper:
        d.marks("glow2", circle(140, 102, 3))
    else:
        d.raw("", f'<circle cx="140" cy="102" r="3" fill="none" stroke="{d.c["ink"]}" stroke-width="1.2"/>')
    trees(d, 150, role="deep", r=8, step=13)
    d.band("mid", "M-30 170 Q100 164 230 170", line=False)


# ================================================================ DUBLIN
def custom_house(x, base, w=58):
    cx = x + w / 2
    cols = " ".join(rect(cx - 9 + i * 4.4, base - 20, 2.2, 13) for i in range(5))
    return [F(rect(x, base - 18, w, 18)), FE(rect(cx - 11, base - 24, 22, 24) + " " + cols),
            F(tri(cx, base - 23.5, 26, 7)),
            F(rect(cx - 5, base - 38, 10, 12)), F(rect(cx - 6.5, base - 39.5, 13, 2.4)),
            F(dome(cx, base - 39, 11, 9)), F(rect(cx - 1, base - 54, 2, 8)), F(circle(cx, base - 55, 2))]


def harp_bridge(x, base, deck):
    """Samuel Beckett Bridge: a curved pylon leaning back like a harp, with fanned cables."""
    px, top = x + 14, deck - 50
    pylon = f"M{px - 3} {deck} C{px - 4} {deck - 20} {px - 2} {top + 10} {px + 6} {top} L{px + 8} {top + 2} C{px + 2} {top + 12} {px + 1} {deck - 20} {px + 3} {deck}Z"
    cables = " ".join(f"M{px + 5 - k * .9:.1f} {top + 4 + k * 4.6:.1f} L{x + 26 + k * 4.2:.1f} {deck}" for k in range(9))
    back = " ".join(f"M{px + 5 - k * .9:.1f} {top + 4 + k * 4.6:.1f} L{x + 2 - k * .6:.1f} {deck}" for k in range(0, 6, 2))
    return [F(rect(x - 6, deck, 70, 4)), F(pylon, spot=True), T(cables + " " + back, .8)]


def dublin(d: Drawing):
    y0 = 150
    d.disc("glow", 60, 60, 13)
    layer(d, "far", towers([(-6, 14, 116, "r"), (80, 12, 112, "r"), (120, 10, 114, "r"), (182, 10, 116, "r")]), line=False)
    chim = [F(poly((150, 160), (151.5, 58), (156.5, 58), (158, 160))), F(poly((164, 160), (165.5, 64), (170.5, 64), (172, 160)))]
    layer(d, "near", [*chim, *towers([(100, 16, 118, "r"), (124, 12, 112, "g"), (176, 18, 120, "r")])], lw=2)
    if d.paper:
        d.marks("light", " ".join(rect(151.4, y, 5.2, 4) for y in (62, 72)) + " " + " ".join(rect(165.4, y, 5.2, 4) for y in (68, 78)))
    else:
        d.raw("", f'<path d="M151.6 64 H156.4 M151.6 72 H156.4 M165.6 70 H170.4 M165.6 78 H170.4" stroke="{d.c["ink"]}" stroke-width="1.2"/>')
    spire = F(poly((92.6, 152), (95.2, 24), (97.8, 152)), spot=True)
    front = [spire, *custom_house(28, 152), F(rect(-30, 144, 260, 10)), *towers([(84, 16, 126, "r"), (100, 12, 132, "r")])]
    layer(d, "deep", front)
    lights(d, [(31, 138, 2, 3.5), (36, 138, 2, 3.5), (41, 138, 2, 3.5), (74, 138, 2, 3.5), (79, 138, 2, 3.5), (84, 138, 2, 3.5)])
    water(d, y0, front, glints=((14, 10), (90, 16), (170, 10)))
    layer(d, "deep", harp_bridge(126, 152, 138), lw=2.6)
    hap = FE("M30 164 V148 Q70 128 110 148 V164Z M36 164 V152 Q70 136 104 152 V164Z")
    rails = T(" ".join(f"M{x} {148 - 20 * (1 - ((x - 70) / 40) ** 2) * .95:.1f} L{x + 3} {152 - 16 * (1 - ((x + 3 - 70) / 34) ** 2) * .95:.1f}"
                       for x in range(40, 100, 6)), .8)
    lamps = S("M58 135 V128 M82 135 V128", 1.2)
    layer(d, "deep", [hap, rails, lamps, F(circle(58, 127, 1.8)), F(circle(82, 127, 1.8))], lw=2.4)


# ================================================================ COPENHAGEN
def our_saviour(cx, base):
    """Church of Our Saviour: square tower, then the black spire with its outside spiral staircase."""
    body = [F(rect(cx - 9, base - 52, 18, 52)), F(rect(cx - 10, base - 54, 20, 3)), F(rect(cx - 6.5, base - 64, 13, 11))]
    sp_base = base - 64
    sp = poly((cx - 6, sp_base), (cx - .8, base - 114), (cx + .8, base - 114), (cx + 6, sp_base))
    turns = []
    for k in range(5):
        y = sp_base - k * 10
        w = 6 - k * 1.05
        turns.append(f"M{cx - w - 1.2:.1f} {y - 1:.1f} L{cx + w - 1:.1f} {y - 8:.1f}")
    return [*body, F(sp, spot=True), S(" ".join(turns), 1.6), F(circle(cx, base - 116, 2)), S(f"M{cx} {base - 118} V{base - 124}", 1)]


def nyhavn(x0, base, spec):
    items, facades, wins = [], [], []
    x = x0
    for w, top, kind, role in spec:
        items.append(F(rect(x, top, w, base - top)))
        items.append(F(gables(x, top, w, kind)))
        facades.append((role, rect(x + 1.2, top + 1, w - 2.4, base - top - 1)))
        for r in range(3):
            for c in range(2):
                wins.append((x + w * .22 + c * w * .36, top + 5 + r * 8, w * .2, 4.2))
        x += w
    return items, facades, wins


def copenhagen(d: Drawing):
    y0 = 150
    d.disc("glow", 150, 60, 13)
    d.shape("light", cloud(14, 54, .7), line=False)
    layer(d, "far", towers([(-6, 18, 112, "r"), (96, 12, 104, "r"), (180, 14, 112, "r")]), line=False)
    cityhall = [F(rect(152, 66, 9, 80)), F(rect(151, 64, 11, 3)), F(tri(156.5, 64.5, 9, 14)), S("M156.5 50 V44", 1)]
    marble = [F(rect(104, 112, 30, 40)), F(rect(108, 98, 22, 15)), F(dome(119, 98.5, 24, 15)), F(rect(117, 78, 4, 6)), F(tri(119, 78.5, 5, 5))]
    layer(d, "near", [*cityhall, *marble, *towers([(160, 16, 118, "r"), (174, 18, 124, "g")])], lw=2)
    spec = [(13, 108, "tri", "pop"), (12, 104, "step", "hero2"), (14, 110, "bell", "hero"), (12, 102, "tri", "light"),
            (13, 106, "neck", "pop"), (12, 112, "tri", "hero2")]
    items, facades, wins = nyhavn(20, 152, spec)
    front = [*our_saviour(116, 152), *items, F(rect(-30, 144, 260, 10)), *towers([(130, 16, 122, "g"), (146, 14, 126, "r"), (160, 16, 130, "g")])]
    layer(d, "deep", front)
    if d.paper:
        for role, f in facades:
            flat(d, role, f)
        d.marks("dark", " ".join(rect(*w) for w in wins))
    else:
        d.raw("", " ".join(f'<path d="M{x} 154 V{t + 2}" stroke="{d.c["ink"]}" stroke-width="1.2"/>' for x, t in [(33, 108), (45, 104), (59, 110), (71, 102), (84, 106)]))
    lights(d, [(134, 132, 2, 4), (140, 132, 2, 4), (150, 134, 2, 4), (164, 136, 2, 4)])
    water(d, y0, front, glints=((96, 12), (140, 16), (176, 8)))
    boat = [F("M28 156 H80 L74 164 H34Z"), S("M44 156 V112 M64 156 V118", 1.4), T("M44 114 L30 154 M44 114 L60 154 M64 120 L78 154", .8)]
    layer(d, "deep", boat, lw=2.2)


# ================================================================ STOCKHOLM
def stadshuset(x, base):
    """Stockholm City Hall: long brick hall and the tall square tower with lantern and three crowns."""
    tx = x + 52
    return [F(rect(x, base - 26, 60, 26)), F(poly((x, base - 26), (x + 3, base - 31), (x + 46, base - 31), (x + 46, base - 26))),
            F(rect(tx - 8, base - 90, 16, 90)),
            F(rect(tx - 9, base - 92, 18, 3)),
            F(rect(tx - 5, base - 102, 10, 10)),
            F(tri(tx, base - 101.5, 11, 10)),
            S(f"M{tx} {base - 112} V{base - 118}", 1.2),
            *[F(f"M{tx + dx - 2.6} {base - 116 + dy} V{base - 119 + dy} L{tx + dx - 1.3} {base - 117.5 + dy} L{tx + dx} {base - 120 + dy} "
                f"L{tx + dx + 1.3} {base - 117.5 + dy} L{tx + dx + 2.6} {base - 119 + dy} V{base - 116 + dy}Z", spot=True)
              for dx, dy in ((0, -6), (-3.4, 0), (3.4, 0))],
            *[F(tri(tx + s * 8, base - 91.5, 3.4, 6)) for s in (-1, 1)]]


def riddarholmen(cx, base):
    """Riddarholmen church: brick nave and the open cast-iron spire."""
    sp = poly((cx - 6, base - 46), (cx - 1, base - 92), (cx + 1, base - 92), (cx + 6, base - 46))
    holes = " ".join(poly((cx - 4.4 + k * .9, base - 50 - k * 9), (cx - .8, base - 54 - k * 9), (cx - 3.4 + k * .9, base - 56 - k * 9.5)) + " " +
                     poly((cx + 4.4 - k * .9, base - 50 - k * 9), (cx + .8, base - 54 - k * 9), (cx + 3.4 - k * .9, base - 56 - k * 9.5))
                     for k in range(3))
    return [F(rect(cx - 8, base - 46, 16, 46)), F(rect(cx - 9, base - 48, 18, 3)), FE(sp + " " + holes, spot=True),
            F(rect(cx + 6, base - 26, 22, 26)), F(poly((cx + 6, base - 26), (cx + 10, base - 32), (cx + 28, base - 32), (cx + 28, base - 26)))]


def stockholm(d: Drawing):
    y0 = 150
    d.disc("glow", 56, 56, 13)
    d.shape("light", cloud(110, 40, .7), line=False)
    layer(d, "far", [*towers([(-6, 16, 118, "r"), (100, 12, 110, "r"), (184, 12, 116, "r")]), F(dome(170, 130, 30, 22))], line=False)
    storkyrkan = [F(rect(160, 84, 12, 40)), F(rect(158.5, 82, 15, 3)), F(dome(166, 82.5, 12, 8)), F(rect(165, 68, 2, 8)), F(circle(166, 67, 2))]
    tyska = [F(rect(140, 96, 9, 30)), F(tri(144.5, 96.5, 10, 26))]
    layer(d, "near", [*storkyrkan, *tyska, *towers([(150, 14, 112, "r"), (126, 12, 118, "g"), (176, 16, 116, "g")])], lw=2)
    gamla = [F(gables(x, t, w, k)) for x, t, w, k in [(114, 126, 12, "tri"), (126, 122, 12, "step"), (138, 128, 12, "tri"),
                                                     (150, 124, 14, "neck"), (164, 128, 12, "tri"), (176, 124, 14, "step")]]
    front = [*stadshuset(18, 152), *riddarholmen(98, 152), *gamla, F(rect(114, 126, 80, 28)), F(rect(-30, 144, 260, 10))]
    layer(d, "deep", front)
    lights(d, [(22, 134, 2.5, 5), (28, 134, 2.5, 5), (34, 134, 2.5, 5), (40, 134, 2.5, 5), (46, 134, 2.5, 5), (66, 84, 2.5, 6), (66, 104, 2.5, 6),
               (118, 132, 2, 4), (130, 132, 2, 4), (142, 134, 2, 4), (156, 132, 2, 4), (168, 134, 2, 4), (180, 132, 2, 4)])
    water(d, y0, front)


# ================================================================ ISTANBUL
def minaret(x, base, top, w=3.4):
    return [F(rect(x - w / 2, top + 7, w, base - top - 7)), F(rect(x - w / 2 - 1.2, top + 18, w + 2.4, 1.8)),
            F(rect(x - w / 2 - 1, top + 30, w + 2, 1.6)), F(tri(x, top + 7.5, w + .6, 8)), S(f"M{x} {top} V{top - 2}", .8)]


def hagia_sophia(cx, base):
    return [F(rect(cx - 22, base - 20, 44, 20)),
            F(poly((cx - 26, base - 10), (cx - 26, base - 20), (cx - 20, base - 26), (cx - 20, base - 10))),
            F(poly((cx + 26, base - 10), (cx + 26, base - 20), (cx + 20, base - 26), (cx + 20, base - 10))),
            F(rect(cx - 14, base - 30, 28, 11)),
            F(dome(cx - 14, base - 24, 14, 6)), F(dome(cx + 14, base - 24, 14, 6)),
            F(f"M{cx - 15} {base - 30} C{cx - 15} {base - 42} {cx - 8} {base - 46} {cx} {base - 46} C{cx + 8} {base - 46} {cx + 15} {base - 42} {cx + 15} {base - 30}Z", spot=True),
            S(f"M{cx} {base - 46} V{base - 50}", 1),
            *minaret(cx - 28, base, base - 64), *minaret(cx + 28, base, base - 64), *minaret(cx - 20, base, base - 56, 3), *minaret(cx + 20, base, base - 58, 3)]


def blue_mosque(cx, base):
    return [F(rect(cx - 26, base - 16, 52, 16)),
            F(dome(cx - 18, base - 15.5, 14, 7)), F(dome(cx + 18, base - 15.5, 14, 7)),
            F(rect(cx - 16, base - 24, 32, 9)),
            F(dome(cx - 10, base - 23.5, 14, 8)), F(dome(cx + 10, base - 23.5, 14, 8)),
            F(rect(cx - 10, base - 31, 20, 8)),
            F(f"M{cx - 12} {base - 30} C{cx - 12} {base - 40} {cx - 6} {base - 43} {cx} {base - 43} C{cx + 6} {base - 43} {cx + 12} {base - 40} {cx + 12} {base - 30}Z"),
            S(f"M{cx} {base - 43} V{base - 47}", 1),
            *minaret(cx - 30, base, base - 72, 3.2), *minaret(cx + 30, base, base - 72, 3.2),
            *minaret(cx - 22, base, base - 64, 3), *minaret(cx + 22, base, base - 64, 3)]


def galata(cx, base):
    return [F(rect(cx - 8, base - 50, 16, 50)), F(rect(cx - 9.5, base - 52, 19, 3)), F(rect(cx - 7.5, base - 58, 15, 7)),
            F(rect(cx - 9, base - 59.5, 18, 2.4)), F(poly((cx - 8.5, base - 59), (cx, base - 80), (cx + 8.5, base - 59)), spot=True),
            S(f"M{cx} {base - 80} V{base - 84}", 1)]


def istanbul(d: Drawing):
    y0 = 152
    d.disc("glow", 98, 58, 13)
    d.shape("light", cloud(130, 36, .7), line=False)
    layer(d, "far", [F("M-30 170 V128 Q20 120 60 124 L70 130 H230 V170Z"), *towers([(150, 12, 112, "r"), (168, 10, 116, "r")])], line=False)
    layer(d, "near", [F("M-30 170 V120 Q0 104 26 102 Q46 102 60 116 L68 130 V170Z"), *towers([(-6, 12, 108, "r"), (44, 12, 112, "r")]),
                      F(rect(120, 132, 80, 40))], lw=2)
    front = [*galata(38, 128), F("M-30 170 V134 Q0 128 26 126 H44 Q54 128 60 138 L64 146 H-30Z"),
             *hagia_sophia(104, 146), *blue_mosque(162, 146), F(rect(70, 140, 140, 14))]
    layer(d, "deep", front)
    lights(d, [(4, 134, 2, 3.5), (10, 132, 2, 3.5), (40, 134, 2, 3.5), (36, 92, 2.5, 4), (92, 132, 2, 4), (100, 132, 2, 4), (108, 132, 2, 4),
               (116, 132, 2, 4), (150, 134, 2, 4), (158, 134, 2, 4), (166, 134, 2, 4), (174, 134, 2, 4)])
    water(d, y0, front, glints=((14, 12), (86, 18), (150, 12)))
    ferry = [F("M66 162 H112 L106 170 H72Z"), F(rect(74, 155, 30, 7)), F(rect(80, 150, 16, 5)), S("M88 150 V146", 1.6)]
    layer(d, "deep", ferry, lw=2.2)
    lights(d, [(78, 157, 2.5, 2.5), (84, 157, 2.5, 2.5), (90, 157, 2.5, 2.5), (96, 157, 2.5, 2.5)], role="light")


# ================================================================ ATHENS
def parthenon(x, base, w=64):
    n = 8
    cw = w / (n * 1.7)
    cols = " ".join(rect(x + 3 + i * (w - 6) / n + cw * .5, base - 24, (w - 6) / n - cw, 20) for i in range(n))
    return [FE(rect(x, base - 26, w, 26) + " " + cols, spot=True),
            F(rect(x - 2, base - 30, w + 4, 5)), F(poly((x - 2, base - 30), (x + w / 2, base - 40), (x + w + 2, base - 30))),
            F(rect(x - 4, base - 4, w + 8, 4))]


def athens(d: Drawing):
    d.disc("glow", 60, 58, 14)
    d.shape("light", cloud(110, 34, .7), line=False)
    lyc = [F("M100 170 V128 Q130 112 146 82 Q152 72 158 82 Q172 110 200 124 L230 130 V170Z"),
           F(rect(148, 72, 10, 8)), F(tri(153, 72.5, 11, 5)), F(rect(155, 66, 3, 7)), S("M156.5 66 V61 M154.5 63 H158.5", 1)]
    layer(d, "far", lyc, line=False)
    layer(d, "near", towers([(-6, 18, 126, "r"), (100, 14, 128, "r"), (116, 12, 124, "r"), (182, 16, 124, "r")]), lw=2)
    rock = F("M-30 170 V138 Q-4 132 6 122 L14 108 Q18 104 26 104 H100 Q108 104 112 110 L120 124 Q130 136 150 142 V170Z")
    zeus = [F(rect(140, 132, 46, 4)), *[F(rect(142 + i * 7, 112, 4, 20)) for i in range(6)],
            F(rect(141, 109, 34, 4)), F(rect(176, 118, 4, 14))]
    front = [rock, *parthenon(30, 104), *zeus, F(rect(-30, 146, 260, 10))]
    layer(d, "deep", front)
    ink(d, "near", "M30 120 L42 128 M76 112 L90 120 M100 114 L108 126", 1.4, line=False)
    blocks = [F(rect(x, y, w, 170 - y)) for x, y, w in [(-10, 150, 22), (14, 152, 18), (34, 148, 20), (56, 152, 18), (76, 146, 22),
                                                         (100, 150, 20), (122, 148, 18), (142, 152, 22), (166, 148, 18), (186, 152, 20)]]
    layer(d, "mid", blocks, line=False)
    if d.paper:
        d.marks("near", " ".join(rect(x + 4, y + 4, 3, 4) + " " + rect(x + 11, y + 4, 3, 4) for x, y, w in
                                 [(-10, 150, 22), (34, 148, 20), (76, 146, 22), (122, 148, 18), (166, 148, 18)]))
    line_ground(d, "M-30 150 H230")
    d.band("ground", "M-30 172 Q100 166 230 172", line=False)


# ================================================================ FLORENCE
def duomo(cx, base):
    return [F(rect(cx - 30, base - 22, 60, 22)),
            F(rect(cx - 18, base - 36, 36, 15)),
            F(rect(cx - 19.5, base - 37.5, 39, 2.6)),
            F(f"M{cx - 18} {base - 36} C{cx - 17} {base - 58} {cx - 8} {base - 76} {cx} {base - 78} "
              f"C{cx + 8} {base - 76} {cx + 17} {base - 58} {cx + 18} {base - 36}Z", spot=True),
            F(rect(cx - 3, base - 88, 6, 11)), F(tri(cx, base - 87.5, 6, 6)), S(f"M{cx} {base - 93} V{base - 97}", 1),
            F(dome(cx - 26, base - 21.5, 10, 7)), F(dome(cx + 26, base - 21.5, 10, 7))]


def campanile(cx, base, top):
    return [F(rect(cx - 5.5, top + 4, 11, base - top - 4)), F(rect(cx - 7, top, 14, 4.4)), F(crenel(cx - 6.5, top - 3, 13, 3.4, 4, 1.6))]


def palazzo_vecchio(cx, base):
    return [F(crenel(cx - 20, base - 34, 34, 34, 7, 2.6)),
            F(rect(cx - 1, base - 52, 10, 20)), F(crenel(cx - 2.5, base - 58, 13, 7, 4, 2)),
            F(rect(cx + 1, base - 70, 6, 12)), F(rect(cx, base - 72, 8, 2.4)), F(bulb(cx + 4, base - 71.5, 7, 6)),
            S(f"M{cx + 4} {base - 77} V{base - 82}", 1)]


def ponte_vecchio(x0, x1, deck):
    shops = [F(rect(x, deck - h, w, h + 1)) for x, w, h in [(x0, 14, 10), (x0 + 14, 10, 13), (x0 + 24, 12, 9), (x0 + 36, 10, 12),
                                                             (x0 + 46, 14, 8), (x0 + 60, 12, 11), (x0 + 72, 10, 9), (x0 + 82, 12, 13), (x0 + 94, x1 - x0 - 94, 10)]]
    span = (x1 - x0) / 3
    arches = " ".join(f"M{x0 + i * span + 4:.1f} 170 V{deck + 10:.1f} Q{x0 + (i + .5) * span:.1f} {deck + 2:.1f} {x0 + (i + 1) * span - 4:.1f} {deck + 10:.1f} V170Z"
                      for i in range(3))
    return [FE(rect(x0, deck, x1 - x0, 170 - deck) + " " + arches, spot=False), *shops, F(rect(x0 - 2, deck + 1, x1 - x0 + 4, 2.4))]


def florence(d: Drawing):
    y0 = 152
    d.disc("glow", 150, 58, 13)
    hills = F("M-30 170 V118 Q20 104 60 112 Q110 120 150 106 Q190 96 230 110 V170Z")
    cyp = " ".join(f"M{x} {b} Q{x - 3} {b - 8} {x} {b - 18} Q{x + 3} {b - 8} {x} {b}Z" for x, b in [(26, 114), (32, 113), (166, 106), (174, 105), (180, 107)])
    layer(d, "far", [hills, F(cyp)], line=False)
    layer(d, "near", towers([(-6, 20, 124, "r"), (130, 14, 120, "g"), (172, 18, 124, "r")]), lw=2)
    front = [*palazzo_vecchio(48, 140), *duomo(102, 140), *campanile(140, 140, 70), F(rect(-30, 132, 260, 22)),
             *towers([(-14, 30, 126, "g"), (152, 18, 124, "g"), (168, 24, 128, "r")])]
    layer(d, "deep", front)
    lights(d, [(80, 124, 2, 4), (86, 124, 2, 4), (116, 124, 2, 4), (122, 124, 2, 4), (138, 80, 4, 6), (138, 96, 4, 6),
               (36, 116, 2.5, 4), (44, 116, 2.5, 4), (52, 116, 2.5, 4)])
    if d.paper:
        d.stroke("near", "M102 64 V102 M92 68 Q88 84 86 102 M112 68 Q116 84 118 102", 1.1)
    water(d, y0, front, glints=((14, 10), (90, 16), (170, 10)))
    pv = ponte_vecchio(20, 130, 142)
    layer(d, "deep", pv, lw=2.6)
    if d.paper:
        d.marks("glow2", " ".join(rect(x, 135, 2.5, 3.4) for x in range(26, 124, 9)))


# ================================================================ REYKJAVIK
def hallgrims(cx, base):
    steps = []
    for k in range(6):
        h = 30 + k * 8
        steps.append(F(rect(cx + 5 + k * 4.2, base - (78 - k * 11), 4.4, 78 - k * 11)))
        steps.append(F(rect(cx - 9.4 - k * 4.2, base - (78 - k * 11), 4.4, 78 - k * 11)))
    return [F(rect(cx - 5.5, base - 96, 11, 96), spot=True), F(poly((cx - 5.5, base - 95), (cx, base - 112), (cx + 5.5, base - 95))),
            S(f"M{cx} {base - 112} V{base - 118}", 1), *steps, F(rect(cx - 36, base - 18, 72, 18))]


def harpa(x, base, w=44):
    return [F(poly((x, base), (x, base - 18), (x + 12, base - 30), (x + 30, base - 26), (x + w, base - 34), (x + w, base)))]


def sun_voyager(x, base):
    hull = f"M{x} {base - 6} Q{x + 18} {base} {x + 40} {base - 6} L{x + 46} {base - 16}"
    ribs = " ".join(f"M{x + 6 + i * 6} {base - 4} L{x + 4 + i * 6} {base - 18 + abs(i - 3) * 1.6}" for i in range(6))
    return [S(hull, 2.2), S(ribs, 1.4), S(f"M{x} {base - 6} L{x - 6} {base - 14}", 1.6), F(rect(x - 2, base - 3, 46, 4))]


def reykjavik(d: Drawing):
    y0 = 150
    d.disc("glow", 150, 54, 12)
    esja = F("M-30 170 V112 L10 100 Q30 92 50 96 L70 92 Q100 88 120 96 L150 94 Q180 98 230 106 V170Z")
    layer(d, "far", [esja], line=False)
    if d.paper:
        d.shape("light", "M10 100 Q30 92 50 96 L70 92 Q100 88 120 96 L114 98 L100 94 L84 98 L66 96 L52 100 L40 97 L24 102Z", shadow=False)
    perlan = [F(rect(30, 112, 26, 12)), F(dome(43, 112.5, 22, 10))]
    layer(d, "near", [*perlan, *towers([(-6, 18, 120, "r"), (150, 16, 118, "r"), (172, 14, 122, "g")])], lw=2)
    houses = [(4, 126, 14, "pop"), (18, 130, 12, "hero2"), (128, 128, 14, "hero"), (142, 126, 12, "pop")]
    hs = []
    for x, t, w, r in houses:
        hs += [F(rect(x, t, w, 154 - t)), F(poly((x - 1, t + 1), (x + w / 2, t - 8), (x + w + 1, t + 1)))]
    front = [*hallgrims(80, 152), *hs, *harpa(150, 152), F(rect(-30, 144, 260, 10))]
    layer(d, "deep", front)
    if d.paper:
        for x, t, w, r in houses:
            flat(d, r, poly((x - 1, t + 1), (x + w / 2, t - 8), (x + w + 1, t + 1)))
        d.marks("glow2", " ".join(rect(x + 3, t + 6, 3, 4) + " " + rect(x + w - 6, t + 6, 3, 4) for x, t, w, r in houses))
        d.stroke("glow2", "M154 136 L162 124 L170 128 L178 120 M158 146 L168 132 L176 140 L184 128 M150 128 L156 142", 1.1)
    water(d, y0, front, glints=((100, 14), (140, 18), (170, 10)))
    layer(d, "deep", sun_voyager(22, 162), lw=2.2)


# ================================================================ MUNICH
def frauenkirche(x, base):
    def twr(tx):
        return [F(rect(tx - 6, base - 76, 12, 76)), F(rect(tx - 6.5, base - 78, 13, 2.4)),
                F(f"M{tx - 6} {base - 77} C{tx - 7} {base - 86} {tx - 2} {base - 88} {tx - 1.6} {base - 93} H{tx + 1.6} "
                  f"C{tx + 2} {base - 88} {tx + 7} {base - 86} {tx + 6} {base - 77}Z", spot=True),
                S(f"M{tx} {base - 93} V{base - 98}", 1)]
    return [*twr(x + 6), *twr(x + 22), F(rect(x + 12, base - 60, 4, 60)),
            F(poly((x + 26, base), (x + 26, base - 34), (x + 32, base - 58), (x + 60, base - 58), (x + 64, base - 34), (x + 64, base)))]


def neues_rathaus(x, base):
    tx = x + 18
    pins = " ".join(tri(px, base - 34, 3, 8) for px in range(int(x) + 3, int(x + 46), 6))
    return [F(rect(x, base - 34, 46, 34)), F(pins),
            F(rect(tx - 6, base - 70, 12, 38)), F(rect(tx - 7, base - 72, 14, 3)),
            F(rect(tx - 4.5, base - 82, 9, 10)), F(tri(tx, base - 81.5, 10, 8)), F(rect(tx - 1, base - 92, 2, 4)), F(circle(tx, base - 92, 1.8)),
            *[F(tri(tx + s * 7, base - 71.5, 3, 8)) for s in (-1, 1)]]


def olympiaturm(cx, base, top):
    return [F(poly((cx - 3.4, base), (cx - 2, top + 18), (cx + 2, top + 18), (cx + 3.4, base))),
            F(f"M{cx - 7} {top + 18} Q{cx - 8} {top + 10} {cx - 5} {top + 8} H{cx + 5} Q{cx + 8} {top + 10} {cx + 7} {top + 18}Z"),
            S(f"M{cx} {top + 8} V{top - 6}", 1.4)]


def munich(d: Drawing):
    d.disc("glow", 150, 52, 12)
    alps = F("M-30 170 V120 L0 104 L18 112 L40 90 L58 106 L76 96 L96 108 L120 86 L144 104 L164 92 L186 108 L230 100 V170Z")
    layer(d, "far", [alps], line=False)
    if d.paper:
        d.shape("light", "M40 90 L48 97 L43 96 L39 99 L35 95Z M120 86 L129 93 L124 92 L120 96 L115 92Z M164 92 L171 98 L166 97 L162 100 L158 96Z",
                shadow=False)
    theatiner = [F(rect(14, 112, 30, 40)), F(rect(8, 104, 8, 30)), F(bulb(12, 104.5, 9, 10)), F(rect(42, 104, 8, 30)), F(bulb(46, 104.5, 9, 10)),
                 F(rect(23, 100, 12, 13)), F(dome(29, 100.5, 14, 10)), F(rect(27.6, 86, 3, 6))]
    layer(d, "near", [*olympiaturm(66, 160, 24), *theatiner, *towers([(-8, 16, 122, "r"), (176, 16, 120, "g")])], lw=2)
    front = [*frauenkirche(80, 152), *neues_rathaus(138, 152), F(rect(-30, 140, 260, 16)), *towers([(56, 20, 126, "g"), (186, 20, 128, "r")])]
    layer(d, "deep", front)
    lights(d, [(141, 128, 2, 5), (147, 128, 2, 5), (163, 128, 2, 5), (169, 128, 2, 5), (175, 128, 2, 5), (154, 96, 3, 5), (154, 106, 3, 5),
               (112, 118, 2, 6), (120, 118, 2, 6), (128, 118, 2, 6)])
    if d.paper:
        d.marks("glow2", circle(156, 90, 2.4))
    trees(d, 150, role="deep", r=8, step=13)
    d.band("mid", "M-30 170 Q100 164 230 170", line=False)


# ================================================================ concepts
LAYER_CHECKS = [("far", "sky"), ("near", "sky"), ("deep", "sky"), ("deep", "near"), ("near", "far"), ("deep", "mid"),
                ("near", "glow"), ("deep", "glow")]
LAYER_FIXES = {
    "far": ["mid", "sky2"],
    "near": ["#6877A8", "#7483B3"],
    "deep": ["ground", "light"],
    "glow": ["glow2", "light", "pop"],
}


def city(cid, activity, title, fn, palettes=None, checks=(), overrides=None, fixes=None):
    fx = dict(fixes or {})
    for k, v in LAYER_FIXES.items():
        fx.setdefault(k, v)
    return Concept(cid, activity, title, fn, palettes=list(palettes or ["golden", "coastal", "meadow", "blush", "dusk"]),
                   overrides=dict(overrides or {}), checks=LAYER_CHECKS + list(checks), fixes=fx)


CONCEPTS = [
    city("sky-london", "skyline-london", "London", london),
    city("sky-paris", "skyline-paris", "Paris", paris),
    city("sky-rome", "skyline-rome", "Rome", rome),
    city("sky-barcelona", "skyline-barcelona", "Barcelona", barcelona),
    city("sky-madrid", "skyline-madrid", "Madrid", madrid),
    city("sky-lisbon", "skyline-lisbon", "Lisbon", lisbon, overrides={"bridge": "#C8452E"},
         checks=[("bridge", "sky"), ("bridge", "mid"), ("bridge", "near"), ("bridge", "far")],
         fixes={"bridge": ["#E0603A", "#9E2E22", "pop"]}),
    city("sky-amsterdam", "skyline-amsterdam", "Amsterdam", amsterdam),
    city("sky-berlin", "skyline-berlin", "Berlin", berlin),
    city("sky-prague", "skyline-prague", "Prague", prague),
    city("sky-vienna", "skyline-vienna", "Vienna", vienna),
    city("sky-budapest", "skyline-budapest", "Budapest", budapest),
    city("sky-edinburgh", "skyline-edinburgh", "Edinburgh", edinburgh),
    city("sky-dublin", "skyline-dublin", "Dublin", dublin),
    city("sky-copenhagen", "skyline-copenhagen", "Copenhagen", copenhagen,
         overrides={"hero": "#E8833A", "hero2": "#F2C14E", "pop": "#C8452E", "dark": "#2B2D42"}),
    city("sky-stockholm", "skyline-stockholm", "Stockholm", stockholm),
    city("sky-istanbul", "skyline-istanbul", "Istanbul", istanbul),
    city("sky-athens", "skyline-athens", "Athens", athens, checks=[("mid", "deep"), ("mid", "sky")]),
    city("sky-florence", "skyline-florence", "Florence", florence),
    city("sky-reykjavik", "skyline-reykjavik", "Reykjavík", reykjavik,
         overrides={"hero": "#2F6DB5", "hero2": "#F2C14E", "pop": "#C8452E"}),
    city("sky-munich", "skyline-munich", "Munich", munich),
]
