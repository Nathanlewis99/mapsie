"""Painted (realistic) Mapsie Originals, generated with Google's Gemini image model.

    python3 design/painted/generate.py --pilot            # 12 varied concepts, for review
    python3 design/painted/generate.py lm-taj-reflection  # specific concept ids
    python3 design/painted/generate.py --all              # everything not yet done
    python3 design/painted/generate.py --sheet            # contact sheet of what exists
    python3 design/painted/generate.py --prompts --pilot  # no API: prompts to paste into the Gemini app
    python3 design/painted/generate.py --import <folder>  # no API: cut saved Gemini images into stickers
    python3 design/painted/generate.py --index            # after review: switch the style on in the app

Each concept is painted from its title and activity with one fixed style brief
(plus up to two approved reference images in design/painted/refs/ to keep the set
consistent), then cut to a circle like the other Originals and saved as
public/stickers/originals/<id>/painted.webp. The API key is never handled here:
the session's network proxy adds it to requests to generativelanguage.googleapis.com.
"""
import base64, io, json, sys, time, urllib.request, urllib.error
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = json.loads((ROOT / "src/lib/originals.json").read_text())
OUT = ROOT / "public/stickers/originals"
REFS = Path(__file__).parent / "refs"
MODEL = "gemini-2.5-flash-image"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
SIZE = 768  # final sticker size in px (prints at ~6.5 cm at 300 dpi, plenty for a sticker)

STYLE = (
    "A single travel sticker illustration in a realistic painted style: rich gouache and watercolour on textured paper, "
    "natural colours and lighting, believable detail and proportions, soft painterly edges, like a page from a beautiful "
    "illustrated travel journal. The subject is centred and large, with its painted setting continuing right to all four "
    "edges of the square: full-bleed, no empty paper margin, no circle or vignette, no border, no frame (it will be cut into a "
    "circle afterwards, so keep the subject inside the central circle). Not a photo, not 3D render, not cartoon, not flat vector. "
    "No text, no letters, no numbers, no logos, no watermark. Square image."
)

def prompt_for(c):
    subject = c["title"]
    if c["label"].lower() not in subject.lower():
        subject = f"{c['title']} ({c['label']})"
    where = ""
    if c["category"] in ("Landmarks", "City skylines"):
        where = " Show the real landmark's true architecture and setting accurately."
    if c["category"] == "Animals":
        where = " Show the animal with anatomically accurate features and natural colouring."
    return f"{STYLE}\n\nSubject: {subject}. Category: {c['category'].lower()}.{where}"

def call(parts, tries=4):
    body = json.dumps({"contents": [{"parts": parts}], "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "1:1"}}}).encode()
    for i in range(tries):
        # The key is injected by the session's proxy; this placeholder is replaced.
        req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json", "x-goog-api-key": "injected-by-proxy"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.loads(r.read())
            for p in data["candidates"][0]["content"]["parts"]:
                if "inlineData" in p:
                    return base64.b64decode(p["inlineData"]["data"])
            raise RuntimeError("no image in response")
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            if e.code in (429, 500, 503) and i < tries - 1:
                time.sleep(4 * (i + 1)); continue
            raise RuntimeError(f"HTTP {e.code}: {msg}")

def ref_parts():
    parts = []
    for f in sorted(REFS.glob("*.png"))[:2]:
        parts.append({"inlineData": {"mimeType": "image/png", "data": base64.b64encode(f.read_bytes()).decode()}})
    if parts:
        parts.append({"text": "Match the painting style, palette and finish of the reference image(s) exactly, but paint the new subject below."})
    return parts

def trim_margin(im: Image.Image) -> Image.Image:
    """If the painting sits inside a plain paper margin (a painted circle on cream paper),
    crop to the painting so every sticker fills its circle the same way."""
    w, h = im.size
    small = im.resize((128, 128))
    px = small.load()
    corners = [px[2, 2], px[125, 2], px[2, 125], px[125, 125]]
    paper = tuple(sum(c[i] for c in corners) // 4 for i in range(3))
    if max(max(abs(c[i] - paper[i]) for i in range(3)) for c in corners) > 30:
        return im  # the corners differ: the painting already runs to the edges
    def busy(x, y):
        return sum(abs(px[x, y][i] - paper[i]) for i in range(3)) > 60
    # Radius of the painted area along the 8 directions from the centre.
    import math
    reach = []
    for k in range(16):
        a = 2 * math.pi * k / 16
        r = 63
        while r > 10 and not busy(int(64 + r * math.cos(a)), int(64 + r * math.sin(a))):
            r -= 1
        reach.append(r)
    r = sorted(reach)[len(reach) // 4]  # robust: ignore a few stray strokes
    if r > 58:
        return im
    scale = w / 128
    half = int(r * 0.97 * scale)
    cx, cy = w // 2, h // 2
    return im.crop((cx - half, cy - half, cx + half, cy + half))

def to_sticker(png: bytes) -> Image.Image:
    im = trim_margin(Image.open(io.BytesIO(png)).convert("RGB")).resize((SIZE, SIZE), Image.LANCZOS)
    # Circle cut with a soft, slightly feathered edge and a white rim, like the papercut set.
    mask = Image.new("L", (SIZE, SIZE), 0)
    m = int(SIZE * 0.04)
    ImageDraw.Draw(mask).ellipse((m, m, SIZE - m, SIZE - m), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(1.2))
    out = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    rim = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(rim).ellipse((m - 8, m - 8, SIZE - m + 8, SIZE - m + 8), fill=255)
    out.paste((255, 255, 255, 255), (0, 0), rim.filter(ImageFilter.GaussianBlur(1)))
    out.paste(im, (0, 0), mask)
    return out

def make(c):
    dest = OUT / c["id"] / "painted.webp"
    if dest.exists():
        return "exists"
    png = call(ref_parts() + [{"text": prompt_for(c)}])
    raw = Path(__file__).parent / "raw" / f"{c['id']}.png"  # kept (not in git) so stickers can be re-cut for free
    raw.parent.mkdir(exist_ok=True); raw.write_bytes(png)
    dest.parent.mkdir(parents=True, exist_ok=True)
    to_sticker(png).save(dest, "WEBP", quality=88, method=6)
    return "ok"

def pilot_ids():
    want = ["lm-taj-reflection", "lm-opera-harbour", "lm-bigben-thames", "sky-tokyo", "basic-beach", "basic-car",
            "slothbear-portrait", "treefrog-portrait", "lm-machupicchu-terraces", "basic-noodles", "lm2-cappadocia", "peacockspider-portrait"]
    ids = {c["id"] for c in CATALOGUE}
    return [i for i in want if i in ids]

def sheet():
    files = sorted(OUT.glob("*/painted.webp"))
    cols, cell = 6, 220
    rows = (len(files) + cols - 1) // cols or 1
    s = Image.new("RGB", (cols * cell, rows * (cell + 20)), "#fbf6ee")
    for i, f in enumerate(files):
        im = Image.open(f).convert("RGBA").resize((cell - 20, cell - 20))
        s.paste(im, ((i % cols) * cell + 10, (i // cols) * (cell + 20) + 10), im)
    p = Path("/tmp/painted-sheet.png"); s.save(p); print(p, len(files))

def prompts(ids):
    """Prompts to paste into the Gemini app by hand, one per sticker, with the file name to save each as."""
    by = {c["id"]: c for c in CATALOGUE}
    out = ["# Painted sticker prompts (Gemini app, Nano Banana)", "",
           "Paste each prompt into a new Gemini chat, download the image, and save it as the file name shown",
           "(any of .png / .jpg / .webp). Put them all in design/painted/inbox/ and push, or upload them to the chat.", ""]
    for i in ids:
        out += [f"## {by[i]['title']}  →  save as `{i}.png`", "", "```", prompt_for(by[i]).replace(chr(10) + chr(10), " "), "```", ""]
    dest = Path(__file__).parent / "PROMPTS.md"
    dest.write_text("\n".join(out)); print(dest)

def import_dir(folder):
    """Turn hand-made images (named <concept id>.png/.jpg/.webp) into stickers. The circle cut also
    removes the Gemini app's corner watermark."""
    ids = {c["id"] for c in CATALOGUE}
    for f in sorted(Path(folder).iterdir()):
        if f.stem in ids and f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
            dest = OUT / f.stem / "painted.webp"
            im = Image.open(f).convert("RGB"); w, h = im.size; side = min(w, h)
            buf = io.BytesIO(); im.crop(((w - side) // 2, (h - side) // 2, (w + side) // 2, (h + side) // 2)).save(buf, "PNG")
            to_sticker(buf.getvalue()).save(dest, "WEBP", quality=88, method=6); print("imported", f.stem)
        else:
            print("skipped (name isn't a sticker id)", f.name)

def index():
    """List painted concepts in src/lib/painted.json, which turns the style on in the app.
    Run this only once the art has been reviewed."""
    ids = sorted(f.parent.name for f in OUT.glob("*/painted.webp"))
    (ROOT / "src/lib/painted.json").write_text(json.dumps(ids) + "\n")
    print(len(ids), "painted concepts published to the app")

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--sheet" in args: sheet(); sys.exit()
    if "--index" in args: index(); sys.exit()
    if "--import" in args: import_dir(args[args.index("--import") + 1]); sys.exit()
    if "--prompts" in args: prompts(pilot_ids() if "--pilot" in args else [a for a in args if not a.startswith("--")]); sys.exit()
    ids = pilot_ids() if "--pilot" in args else [c["id"] for c in CATALOGUE] if "--all" in args else [a for a in args if not a.startswith("--")]
    by = {c["id"]: c for c in CATALOGUE}
    for n, i in enumerate(ids, 1):
        try:
            print(f"[{n}/{len(ids)}] {i}: {make(by[i])}", flush=True)
        except Exception as e:
            print(f"[{n}/{len(ids)}] {i}: FAILED {e}", flush=True)
