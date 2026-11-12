"""Mapsie logo directions: wordmark lockups and square icons, as standalone SVG.

    python3 design/brand/logos.py     -> design/brand/out/<direction>-{wordmark,icon}.svg
"""
from pathlib import Path
from glyphs import text_path

OUT = Path(__file__).parent / "out"
INK, CORAL, CREAM, SEA = "#1F2430", "#FF6B4A", "#FBF6EE", "#2BB3A6"


def svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{body}</svg>\n'


def pin(cx, tip_y, r, fill, hole=None):
    """Map pin with its point at (cx, tip_y) and head radius r."""
    cy = tip_y - r * 2.35
    d = (f"M{cx} {tip_y} C{cx - r * 0.35} {tip_y - r * 0.9} {cx - r} {cy + r * 0.75} {cx - r} {cy} "
         f"A{r} {r} 0 1 1 {cx + r} {cy} C{cx + r} {cy + r * 0.75} {cx + r * 0.35} {tip_y - r * 0.9} {cx} {tip_y}Z")
    out = f'<path d="{d}" fill="{fill}"/>'
    if hole:
        out += f'<circle cx="{cx}" cy="{cy}" r="{r * 0.42}" fill="{hole}"/>'
    return out


# ---------------------------------------------------------------- A. Classic dot
def classic():
    d, w = text_path("Mapsie", 100, 0, 100)
    word = svg(w + 40, 130, f'<path d="{d}" fill="{INK}"/><circle cx="{w + 18}" cy="88" r="12" fill="{CORAL}"/>')
    m, mw = text_path("M", 84, 0, 0)
    icon = svg(128, 128, f'<rect width="128" height="128" rx="30" fill="{INK}"/>'
                         f'<g transform="translate({(128 - mw) / 2 - 7} 92)"><path d="{m}" fill="{CREAM}"/></g>'
                         f'<circle cx="{(128 + mw) / 2 + 3}" cy="84" r="8" fill="{CORAL}"/>')
    return word, icon


# ---------------------------------------------------------------- B. Pin dot
def pin_dot():
    d, w = text_path("Mapsie", 100, 0, 100)
    word = svg(w + 48, 130, f'<path d="{d}" fill="{INK}"/>{pin(w + 22, 101, 13, CORAL, CREAM)}')
    m, mw = text_path("M", 64, 0, 0)
    icon = svg(128, 128, f'<rect width="128" height="128" rx="30" fill="{CREAM}"/>'
                         f'{pin(64, 116, 40, CORAL)}'
                         f'<g transform="translate({64 - mw / 2} 66)"><path d="{m}" fill="{CREAM}"/></g>')
    return word, icon


# ---------------------------------------------------------------- C. Route
def route():
    d, w = text_path("Mapsie", 100, 0, 128)
    arc = f'<path d="M14 22 Q {w * 0.45} -14 {w + 6} 40" fill="none" stroke="{CORAL}" stroke-width="5" stroke-dasharray="11 9" stroke-linecap="round"/>'
    word = svg(w + 44, 158, f'<circle cx="14" cy="22" r="7" fill="{INK}"/>{arc}<path d="{d}" fill="{INK}"/>'
                            f'{pin(w + 8, 52, 11, CORAL, CREAM)}')
    m, mw = text_path("M", 82, 0, 0)
    icon = svg(128, 128, f'<rect width="128" height="128" rx="30" fill="{CREAM}"/>'
                         f'<path d="M20 44 Q 60 6 104 30" fill="none" stroke="{CORAL}" stroke-width="7" stroke-dasharray="12 9" stroke-linecap="round"/>'
                         f'<circle cx="20" cy="44" r="8" fill="{INK}"/><circle cx="104" cy="30" r="10" fill="{CORAL}"/>'
                         f'<g transform="translate({64 - mw / 2} 112)"><path d="{m}" fill="{INK}"/></g>')
    return word, icon


# ---------------------------------------------------------------- D. Postmark
def postmark():
    d, w = text_path("Mapsie", 100, 0, 100)
    word = svg(w + 40, 130, f'<path d="{d}" fill="{INK}"/><circle cx="{w + 18}" cy="88" r="12" fill="{CORAL}"/>')
    m, mw = text_path("M", 60, 0, 0)
    ring = "".join(
        f'<circle cx="{64 + 50 * __import__("math").cos(a * 6.2832 / 28):.2f}" cy="{64 + 50 * __import__("math").sin(a * 6.2832 / 28):.2f}" r="2.6" fill="{CORAL}"/>'
        for a in range(28))
    icon = svg(128, 128, f'<rect width="128" height="128" rx="30" fill="{CORAL}"/>'
                         f'<circle cx="64" cy="64" r="44" fill="{CREAM}"/>{ring.replace(CORAL, CREAM)}'
                         f'<circle cx="64" cy="64" r="38" fill="none" stroke="{CORAL}" stroke-width="2.5"/>'
                         f'<g transform="translate({64 - mw / 2 - 3} 85)"><path d="{m}" fill="{INK}"/></g>'
                         f'<circle cx="{64 + mw / 2 + 4}" cy="79" r="6" fill="{CORAL}"/>')
    return word, icon


DIRECTIONS = {"classic": classic, "pin": pin_dot, "route": route, "postmark": postmark}

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, fn in DIRECTIONS.items():
        word, icon = fn()
        (OUT / f"{name}-wordmark.svg").write_text(word)
        (OUT / f"{name}-icon.svg").write_text(icon)
    print("wrote", len(DIRECTIONS) * 2, "files to", OUT)
