"""Hang the rendered Mapsie posters in the room photos, framed, for listing images.

    python3 design/mockups/compose.py <renders dir> <out dir>

Uses the room placement data from src/lib/rooms.ts (centre, bottom edge, wall width in
cm) so prints hang at a believable real-world size, with mitred frame moulding lit from
the left (the window side), a recessed print, glass sheen and a soft wall shadow.
"""
import json, re, sys, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
RENDERS, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

ROOMS = {}
for m in re.finditer(r'\{ id: "([^"]+)".*?cx: ([\d.]+), by: ([\d.]+), wallCm: (\d+), maxHeight: ([\d.]+)', (ROOT / "src/lib/rooms.ts").read_text()):
    ROOMS[m[1]] = dict(cx=float(m[2]), by=float(m[3]), wallCm=float(m[4]), maxH=float(m[5]))

TRIPS = []  # slug, frame, room from trips.ts
for m in re.finditer(r'slug: "([^"]+)",.*?frame: "([^"]+)",\s*room: "([^"]+)"', (ROOT / "design/mockups/trips.ts").read_text(), re.S):
    TRIPS.append((m[1], m[2], m[3]))

FRAME = {  # base colour, wood grain
    "black": ((28, 28, 28), False), "white": ((240, 239, 235), False), "oak": ((196, 154, 108), True),
    "brown": ((90, 59, 38), True), "darkgrey": ((74, 77, 82), False), "lightgrey": ((185, 188, 191), False),
}
OUT_W, OUT_H = 2400, 1800  # 4:3, Etsy-friendly
MOULD_CM = 2.4

def shade(rgb, k):
    a = np.array(rgb, float)
    return tuple(int(v) for v in (a + (255 - a) * k if k > 0 else a * (1 + k)))

def compose(slug, frame, room_id):
    room = ROOMS[room_id]
    poster = Image.open(RENDERS / f"{slug}.png").convert("RGB")
    bg = Image.open(ROOT / f"public/rooms/{room_id}.jpg").convert("RGB")
    W0, H0 = bg.size
    # Crop the room to 4:3 around the picture, then scale up to the output size.
    cw = int(H0 * 4 / 3)
    x0 = int(min(max(room["cx"] * W0 - cw / 2, 0), W0 - cw))
    bg = bg.crop((x0, 0, x0 + cw, H0)).resize((OUT_W, OUT_H), Image.LANCZOS)
    k = OUT_W / cw  # output px per original px
    ppc = W0 / room["wallCm"] * k  # px per cm on the wall
    cx = (room["cx"] * W0 - x0) * k
    bottom = room["by"] * H0 * k

    portrait = poster.height >= poster.width
    aspect = poster.height / poster.width
    mould = MOULD_CM * ppc if frame != "none" else 0
    # As large as A1 (59.4 x 84.1 cm), but within the room's comfortable height.
    long_cm = 84.1
    max_h = room["maxH"] * H0 * k
    ph = long_cm * ppc if portrait else long_cm / aspect * ppc * aspect
    pw = ph / aspect
    if ph + 2 * mould > max_h:
        s = (max_h - 2 * mould) / ph
        ph, pw = ph * s, pw * s
    if not portrait:  # landscape: 84 cm wide
        pw = min(long_cm * ppc, (max_h - 2 * mould) / aspect)
        ph = pw * aspect
    fw, fh = pw + 2 * mould, ph + 2 * mould
    L, T = cx - fw / 2, bottom - fh
    L, T, fw, fh, mould = (round(v) for v in (L, T, fw, fh, mould))
    pw, ph = fw - 2 * mould, fh - 2 * mould

    canvas = bg.convert("RGBA")
    # Wall shadow: light from the left, so it falls down and to the right.
    sh = Image.new("L", canvas.size, 0)
    d = ImageDraw.Draw(sh)
    off = (0.9 * ppc, 1.4 * ppc)
    d.rectangle((L + off[0], T + off[1], L + fw + off[0], T + fh + off[1]), fill=110)
    sh = sh.filter(ImageFilter.GaussianBlur(2.2 * ppc))
    contact = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(contact).rectangle((L + 0.15 * ppc, T + 0.2 * ppc, L + fw + 0.25 * ppc, T + fh + 0.35 * ppc), fill=90)
    contact = contact.filter(ImageFilter.GaussianBlur(0.35 * ppc))
    shadow = Image.new("RGBA", canvas.size, (30, 24, 18, 0))
    shadow.putalpha(Image.fromarray(np.maximum(np.array(sh), np.array(contact))))
    canvas = Image.alpha_composite(canvas, shadow)

    # The print, with the room's light: brighter towards the window (left), a touch warmer.
    art = poster.resize((pw, ph), Image.LANCZOS)
    a = np.array(art).astype(float)
    gx = np.linspace(1.02, 0.93, pw)[None, :, None]
    gy = np.linspace(1.0, 0.97, ph)[:, None, None]
    a = a * gx * gy * np.array([1.0, 0.99, 0.965])
    if frame != "none":
        # The frame's lip casts a shadow onto the print along the top and left edges.
        lip = 0.9 * ppc
        yy, xx = np.mgrid[0:ph, 0:pw]
        dark = np.clip(1 - yy / lip, 0, 1) * 0.32 + np.clip(1 - xx / lip, 0, 1) * 0.22
        dark += np.clip(1 - (pw - xx) / (lip * 0.4), 0, 1) * 0.08 + np.clip(1 - (ph - yy) / (lip * 0.4), 0, 1) * 0.06
        a = a * (1 - np.clip(dark, 0, 0.45))[..., None]
        # Glazing: a faint diagonal reflection.
        diag = (xx / pw * 0.8 + yy / ph * 0.4)
        sheen = np.exp(-((diag - 0.28) ** 2) / 0.006) * 14 + np.exp(-((diag - 0.62) ** 2) / 0.002) * 7
        a = a + sheen[..., None]
    art = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    canvas.paste(art, (L + mould, T + mould))

    if frame != "none":
        base, wood = FRAME[frame]
        fr = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        dr = ImageDraw.Draw(fr)
        R, B = L + fw, T + fh
        il, it, ir, ib = L + mould, T + mould, R - mould, B - mould
        sides = {
            "top": ([(L, T), (R, T), (ir, it), (il, it)], 0.16),
            "left": ([(L, T), (il, it), (il, ib), (L, B)], 0.06),
            "right": ([(R, T), (R, B), (ir, ib), (ir, it)], -0.12),
            "bottom": ([(L, B), (il, ib), (ir, ib), (R, B)], -0.22),
        }
        for name, (poly, k2) in sides.items():
            dr.polygon(poly, fill=shade(base, k2) + (255,))
        arr = np.array(fr).astype(float)
        yy, xx = np.mgrid[0:canvas.size[1], 0:canvas.size[0]]
        inside = arr[..., 3] > 0
        # Rounded moulding profile: highlight ridge near the outer edge, darker towards the glass.
        dist = np.minimum.reduce([xx - L, R - xx, yy - T, B - yy]).astype(float) / max(mould, 1)
        profile = np.interp(dist, [0, 0.12, 0.35, 0.8, 1.0], [-0.18, 0.14, 0.05, -0.04, -0.28])
        if wood:
            rng = np.random.default_rng(7)
            # Fine grain running along each side of the moulding, softly blurred.
            along = np.where(np.abs(xx - (L + R) / 2) / fw > np.abs(yy - (T + B) / 2) / fh, xx, yy).astype(float)
            noise = np.array(Image.fromarray((rng.random(xx.shape) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(float) / 255 - 0.5
            grain = (np.sin(along * 0.35 + noise * 3) * 0.5 + noise) * 0.022
            profile = profile + grain
        mult = 1 + profile[..., None]
        arr[..., :3] = np.where(inside[..., None], np.clip(arr[..., :3] * mult + (mult > 1) * 6, 0, 255), arr[..., :3])
        fr = Image.fromarray(arr.astype(np.uint8))
        # Mitre lines
        md = ImageDraw.Draw(fr)
        for a1, a2 in [((L, T), (il, it)), ((R, T), (ir, it)), ((L, B), (il, ib)), ((R, B), (ir, ib))]:
            md.line([a1, a2], fill=shade(base, -0.35) + (140,), width=max(1, round(ppc * 0.06)))
        canvas = Image.alpha_composite(canvas, fr)
    else:
        # Unframed print: a hairline paper edge.
        ImageDraw.Draw(canvas).rectangle((L, T, L + fw - 1, T + fh - 1), outline=(0, 0, 0, 40), width=1)

    out = OUT / f"{slug}.jpg"
    canvas.convert("RGB").save(out, quality=92, subsampling=0)
    return out

for slug, frame, room in TRIPS:
    print(compose(slug, frame, room))
