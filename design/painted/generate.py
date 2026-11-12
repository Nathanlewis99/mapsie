"""Painted (realistic) Mapsie Originals, generated with Google's Gemini image model.

    python3 design/painted/generate.py --pilot            # 12 varied concepts, for review
    python3 design/painted/generate.py lm-taj-reflection  # specific concept ids
    python3 design/painted/generate.py --all              # everything not yet done
    python3 design/painted/generate.py --sheet            # contact sheet of what exists
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
    "illustrated travel journal. The subject is centred and fills a circular composition with a simple, softly painted "
    "background scene that fades to the edges. Not a photo, not 3D render, not cartoon, not flat vector. "
    "No text, no letters, no numbers, no logos, no watermark, no border, no frame. Square image."
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

def to_sticker(png: bytes) -> Image.Image:
    im = Image.open(io.BytesIO(png)).convert("RGB").resize((SIZE, SIZE), Image.LANCZOS)
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
    ids = pilot_ids() if "--pilot" in args else [c["id"] for c in CATALOGUE] if "--all" in args else [a for a in args if not a.startswith("--")]
    by = {c["id"]: c for c in CATALOGUE}
    for n, i in enumerate(ids, 1):
        try:
            print(f"[{n}/{len(ids)}] {i}: {make(by[i])}", flush=True)
        except Exception as e:
            print(f"[{n}/{len(ids)}] {i}: FAILED {e}", flush=True)
