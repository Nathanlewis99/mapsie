"""Turn text in Playfair Display (ExtraBold) into SVG path data, for the logo."""
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from pathlib import Path

FONT = Path(__file__).parents[2] / "node_modules/@fontsource-variable/playfair-display/files/playfair-display-latin-wght-normal.woff2"
_font = None


def font():
    global _font
    if _font is None:
        f = TTFont(str(FONT))
        _font = instantiateVariableFont(f, {"wght": 850})
    return _font


def text_path(text: str, size: float, x: float = 0, y: float = 0, tracking: float = 0):
    """Return (path_d, advance_width) for text with its baseline at (x, y)."""
    f = font()
    upm = f["head"].unitsPerEm
    cmap = f.getBestCmap()
    gs = f.getGlyphSet()
    hmtx = f["hmtx"]
    s = size / upm
    pen = SVGPathPen(gs)
    cx = 0.0
    for ch in text:
        g = cmap[ord(ch)]
        tp = TransformPen(pen, (s, 0, 0, -s, x + cx, y))
        gs[g].draw(tp)
        cx += hmtx[g][0] * s + tracking
    return pen.getCommands(), cx - tracking
