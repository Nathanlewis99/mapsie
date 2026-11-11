"""Mapsie art kit: draw a concept once, get every style and colour palette.

A concept is a function `draw(d)` that builds a scene with the helper methods on
`Drawing` (band, shape, disc, limb, stroke, marks). Shapes are given *colour
roles* ("sky", "hero", "mark"...), never hex values. The kit then renders it as:

  papercut  layered paper with soft shadows, coloured from a palette
  line      one pen line plus a single spot colour

Colour clashes are caught automatically: each concept lists which roles sit
next to each other (e.g. the giraffe "hero" against the sun "glow"), and a
palette is only offered for that concept if those pairs have enough contrast.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable

# ---------------------------------------------------------------- colour roles
# sky/sky2   background            glow/glow2  sun or moon disc
# far/mid/near/deep  landscape (or water-depth) layers, back to front
# ground     sand / earth          hero/hero2  main subject colours
# mark       markings on the hero  dark        silhouettes, wheels, trunks
# light      clouds, snow, shine   pop         small accent (flame, coral, flags)
PAPERCUT_PALETTES: dict[str, dict[str, str]] = {
    "golden": dict(sky="#FDE7C8", sky2="#FBD3A5", glow="#F6A96B", glow2="#EF8354", far="#E9B98B", mid="#D98E5F",
                   near="#B9654A", deep="#7A3E3A", ground="#F2D49B", hero="#3E7CB1", hero2="#FFD166", mark="#2B2D42",
                   dark="#3B2A20", light="#FFFFFF", pop="#EF476F"),
    "coastal": dict(sky="#E6F6F7", sky2="#CDEFF2", glow="#FFE29A", glow2="#FFC857", far="#9ADBE0", mid="#5FBCC6",
                    near="#2F8FA3", deep="#16506B", ground="#F2D49B", hero="#FF7A5C", hero2="#FFC857", mark="#12354A",
                    dark="#0E2A3D", light="#FFFFFF", pop="#FF7A5C"),
    "meadow": dict(sky="#EEF6E4", sky2="#DCEFC8", glow="#FFE8A3", glow2="#FFD36E", far="#B8D99A", mid="#8CC084",
                   near="#5E9C6A", deep="#3A6B4E", ground="#E9D8A6", hero="#E76F51", hero2="#F4A261", mark="#264653",
                   dark="#2D3A2E", light="#FFFFFF", pop="#E9C46A"),
    "blush": dict(sky="#FDE2E4", sky2="#FAD2E1", glow="#FFF1E6", glow2="#FFD6BA", far="#F4ACB7", mid="#E5989B",
                  near="#B5838D", deep="#6D6875", ground="#FFE5D9", hero="#6D9DC5", hero2="#FFD166", mark="#3D405B",
                  dark="#4A3F55", light="#FFFFFF", pop="#E56B6F"),
    "dusk": dict(sky="#1F2A44", sky2="#2E3B5E", glow="#F2C14E", glow2="#F7DD8A", far="#3E4C72", mid="#4F5D8A",
                 near="#2A3354", deep="#151B30", ground="#C9A66B", hero="#F28F3B", hero2="#F2C14E", mark="#0F1424",
                 dark="#0B0F1C", light="#E8EDF7", pop="#E4572E"),
}

# Line style: ink for every line, one spot colour, a soft wash disc behind,
# and "paper" to fill shapes (so lines don't show through each other).
LINE_PALETTES: dict[str, dict[str, str]] = {
    "classic": dict(ink="#1D2D44", spot="#E4572E", wash="#F6D5C9", paper="#FFFFFF", bg="#FBF6EE"),
    "forest": dict(ink="#2D3A2E", spot="#E9A23B", wash="#DDEBCF", paper="#FFFDF6", bg="#F6F4EC"),
    "ocean": dict(ink="#12354A", spot="#2BB3A6", wash="#D3EEEC", paper="#FFFFFF", bg="#F4F9F9"),
    "night": dict(ink="#F3E9D2", spot="#F2C14E", wash="#2E3B5E", paper="#1F2A44", bg="#1F2A44"),
}

MIN_CONTRAST = 1.42  # papercut layers also have drop shadows separating them
MIN_DELTA_E = 42


def _lum(hex_: str) -> float:
    h = hex_.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a: str, b: str) -> float:
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def _lab(hex_: str):
    h = hex_.lstrip("#")
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    r, g, b = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    x, y, z = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047, 0.2126 * r + 0.7152 * g + 0.0722 * b, (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta_e(a: str, b: str) -> float:
    """Perceptual colour difference (CIE76). ~40+ reads as clearly different colours."""
    return sum((p - q) ** 2 for p, q in zip(_lab(a), _lab(b))) ** 0.5


def distinct(a: str, b: str) -> bool:
    """Do two touching colours read apart? Either brightness or hue must differ enough."""
    return contrast(a, b) >= MIN_CONTRAST or delta_e(a, b) >= MIN_DELTA_E


# ---------------------------------------------------------------- drawing
class Drawing:
    def __init__(self, style: str, colours: dict[str, str]):
        self.style = style
        self.c = colours
        self.parts: list[str] = []
        self.bands: list[str] = []  # line style: clipped landscape edges

    @property
    def paper(self) -> bool:
        return self.style == "papercut"

    def _sh(self, shadow: bool) -> str:
        return ' filter="url(#ps)"' if (self.paper and shadow) else ""

    def _line(self, spot: bool = False, width: float = 3.2) -> str:
        fill = self.c["spot"] if spot else self.c["paper"]
        return f'fill="{fill}" stroke="{self.c["ink"]}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"'

    # A landscape / water layer. `edge` is the top edge, running left to right
    # from x<=0 to x>=200; papercut fills everything below it.
    def band(self, role: str, edge: str, shadow: bool = True, line: bool = True):
        if self.paper:
            self.parts.append(f'<path{self._sh(shadow)} d="{edge} L230 230 L-30 230Z" fill="{self.c[role]}"/>')
        elif line:
            self.bands.append(f'<path d="{edge}" fill="none" stroke="{self.c["ink"]}" stroke-width="3" stroke-linecap="round"/>')

    def shape(self, role: str, d: str, spot: bool = False, shadow: bool = True, line: bool = True, extra: str = ""):
        if self.paper:
            self.parts.append(f'<path{self._sh(shadow)} d="{d}" fill="{self.c[role]}" {extra}/>')
        elif line:
            self.parts.append(f'<path d="{d}" {self._line(spot)} {extra}/>')

    def disc(self, role: str, cx: float, cy: float, r: float, shadow: bool = True, line: bool = True):
        if self.paper:
            self.parts.append(f'<circle{self._sh(shadow)} cx="{cx}" cy="{cy}" r="{r}" fill="{self.c[role]}"/>')
        elif line:
            self.parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{self.c["spot"]}"/>')

    def stroke(self, role: str, d: str, w: float = 3, shadow: bool = False, line: bool = True):
        if self.paper:
            self.parts.append(f'<path{self._sh(shadow)} d="{d}" fill="none" stroke="{self.c[role]}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')
        elif line:
            self.parts.append(f'<path d="{d}" fill="none" stroke="{self.c["ink"]}" stroke-width="{min(w, 3.2)}" stroke-linecap="round" stroke-linejoin="round"/>')

    # A thick rounded stroke (arms, legs, trunks). Line style draws it as an outlined tube.
    def limb(self, role: str, d: str, w: float, shadow: bool = True, spot: bool = False):
        if self.paper:
            self.parts.append(f'<path{self._sh(shadow)} d="{d}" fill="none" stroke="{self.c[role]}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')
        else:
            inner = self.c["spot"] if spot else self.c["paper"]
            self.parts.append(f'<path d="{d}" fill="none" stroke="{self.c["ink"]}" stroke-width="{w + 3.4}" stroke-linecap="round" stroke-linejoin="round"/>'
                              f'<path d="{d}" fill="none" stroke="{inner}" stroke-width="{max(w - 3.0, 1)}" stroke-linecap="round" stroke-linejoin="round"/>')

    # Small markings (spots, stripes, eyes): solid colour in papercut, solid ink in line.
    def marks(self, role: str, d: str):
        colour = self.c[role] if self.paper else self.c["ink"]
        self.parts.append(f'<path d="{d}" fill="{colour}"/>')

    def raw(self, papercut: str = "", line: str = ""):
        self.parts.append(papercut if self.paper else line)


# ---------------------------------------------------------------- concepts
@dataclass
class Concept:
    id: str  # e.g. "safari-jeep"
    activity: str  # activity id from activities.json
    title: str
    draw: Callable[[Drawing], None]
    palettes: list[str] = field(default_factory=lambda: list(PAPERCUT_PALETTES))  # palettes that suit the scene
    overrides: dict[str, str] = field(default_factory=dict)  # natural colours, e.g. a golden giraffe
    checks: list[tuple[str, str]] = field(default_factory=list)  # role pairs that touch and must not clash
    # When a check fails, swap a role for the first of these (palette roles or "#hex") that fixes it,
    # e.g. {"glow": ["near", "deep"]}: a darker sun behind a golden giraffe.
    fixes: dict[str, list[str]] = field(default_factory=dict)

    def _ok(self, c: dict[str, str], role: str | None = None) -> bool:
        return all(distinct(c[a], c[b]) for a, b in self.checks if role is None or role in (a, b))

    def colours(self, palette: str) -> dict[str, str]:
        base = {**PAPERCUT_PALETTES[palette], **self.overrides}
        c = dict(base)
        for role, candidates in self.fixes.items():
            if self._ok(c, role):
                continue
            for cand in candidates:
                trial = {**c, role: base.get(cand, cand)}  # a palette role, or a literal "#hex"
                if self._ok(trial, role):
                    c = trial
                    break
        return c

    def good_palettes(self) -> list[str]:
        """Palettes where every touching pair of roles has enough contrast (after fixes)."""
        return [p for p in self.palettes if self._ok(self.colours(p))]


def render(concept: Concept, style: str, palette: str) -> str:
    if style == "papercut":
        c = concept.colours(palette)
        d = Drawing("papercut", c)
        concept.draw(d)
        body = (f'<g clip-path="url(#clip)"><rect width="200" height="200" fill="{c["sky"]}"/>{"".join(d.parts)}</g>'
                f'<circle cx="100" cy="100" r="92" fill="none" stroke="#fff" stroke-width="4" opacity=".9"/>')
        defs = ('<clipPath id="clip"><circle cx="100" cy="100" r="92"/></clipPath>'
                '<filter id="ps" filterUnits="userSpaceOnUse" x="-40" y="-40" width="280" height="280">'
                '<feDropShadow dx="0" dy="2.2" stdDeviation="2" flood-color="#2a1f14" flood-opacity=".33"/></filter>')
    else:
        c = LINE_PALETTES[palette]
        d = Drawing("line", c)
        concept.draw(d)
        body = (f'<circle cx="100" cy="100" r="84" fill="{c["wash"]}"/>'
                f'<g clip-path="url(#clip)">{"".join(d.bands)}{"".join(d.parts)}</g>')
        defs = '<clipPath id="clip"><circle cx="100" cy="100" r="90"/></clipPath>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">'
            f'<defs>{defs}</defs>{body}</svg>\n')


# ---------------------------------------------------------------- reusable bits
def cloud(x: float, y: float, s: float = 1.0) -> str:
    return (f"M{x} {y} a{8*s} {8*s} 0 0 1 {12*s} {-6*s} a{11*s} {11*s} 0 0 1 {20*s} {2*s} "
            f"a{8*s} {8*s} 0 0 1 {6*s} {14*s} H{x+2*s} a{6*s} {6*s} 0 0 1 {-2*s} {-10*s}Z")


def fish(x: float, y: float, s: float = 1.0, right: bool = False) -> str:
    k = -1 if right else 1
    return (f"M{x-7*s*k} {y} C{x-4*s*k} {y-4.5*s} {x+3*s*k} {y-4.5*s} {x+6*s*k} {y} "
            f"L{x+12*s*k} {y-4.5*s} L{x+12*s*k} {y+4.5*s} L{x+6*s*k} {y} "
            f"C{x+3*s*k} {y+4.5*s} {x-4*s*k} {y+4.5*s} {x-7*s*k} {y}Z")


def circle(cx: float, cy: float, r: float) -> str:
    return f"M{cx-r} {cy} a{r} {r} 0 1 0 {2*r} 0 a{r} {r} 0 1 0 {-2*r} 0Z"


def ellipse(cx: float, cy: float, rx: float, ry: float) -> str:
    return f"M{cx-rx} {cy} a{rx} {ry} 0 1 0 {2*rx} 0 a{rx} {ry} 0 1 0 {-2*rx} 0Z"


def waves(y: float, amp: float = 6, step: float = 30) -> str:
    """A wavy edge across the full width at height y."""
    s = f"M-30 {y} Q{-30 + step/2} {y - amp} {-30 + step} {y}"
    x = -30 + step
    while x < 230:
        x += step
        s += f" T{x} {y}"
    return s


def hills(y: float, amp: float = 14, phase: float = 0) -> str:
    return f"M-30 {y + amp*0.3} Q{40+phase} {y - amp} {100+phase} {y} T{230+phase} {y - amp*0.4}"
