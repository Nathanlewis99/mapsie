"""Compose a vertical (1080x1920) ad video from screencast recordings and stills.

    python3 design/ads/src/compose.py <videos.json> <name> <recordings dir> <overlays dir> <out dir>

videos.json[name] = {
  "rec": recording dir name (frames + meta.json from record.js), optional,
  "layout": "phone" | "crop",  "crop": [x, y, w, h] in recording pixels (crop layout),
  "segments": [
     [from, to, speed],             a piece of the recording (times in recording seconds or marks)
     {"image": path, "seconds": s, "from": [cx, cy, h], "to": [cx, cy, h], "fade": 0.4, "caption": "x.png"}
  ],                                a still, full-bleed: a 9:16 window (centre, height) panning from -> to
  "captions": [[from, to, "cap.png"], ...],   for recording pieces, in recording time
  "end": "end-design.png", "end_seconds": 2.2
}
Recording times are seconds from the "start" mark, or mark names with an optional +/- offset ("map+1.2").
Still paths are relative to the repository root, or absolute. Full-size (1080x1920) caption images are
laid over the whole frame; smaller ones (1080x360) above the phone.
"""
import json, math, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

FPS = 30
W, H = 1080, 1920
SCREEN = dict(x=168, y=368, w=744, h=1323, r=58)  # must match graphics.ts
ROOT = Path(__file__).resolve().parents[3]

spec = json.loads(Path(sys.argv[1]).read_text())[sys.argv[2]]
ov = Path(sys.argv[4])
out = str(Path(sys.argv[5]) / f"{sys.argv[2]}.mp4")

frames, marks = [], {}
if spec.get("rec"):
    rec = Path(sys.argv[3]) / spec["rec"]
    meta = json.loads((rec / "meta.json").read_text())
    t0 = meta["marks"]["start"]
    frames = [(f["t"] - t0, rec / f["file"]) for f in meta["frames"]]
    marks = {k: v - t0 for k, v in meta["marks"].items()}


def T(v):
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v)
    for sep in "+-":
        if sep in s:
            name, off = s.split(sep, 1)
            if name in marks:
                return marks[name] + (float(off) if sep == "+" else -float(off))
    return marks[s]


def ease(k):
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, k)))


captions = [(T(a), T(b), c) for a, b, c in spec.get("captions", [])]

# The plan: one entry per output frame.
plan = []
for seg in spec["segments"]:
    if isinstance(seg, dict):
        n = int(round(seg["seconds"] * FPS))
        nf = max(1, int(seg.get("fade", 0.4) * FPS))
        for i in range(n):
            plan.append({"kind": "img", "seg": seg, "k": ease(i / max(1, n - 1)), "fade": (i + 1) / nf if i < nf else None, "first": i == 0, "cap": seg.get("caption")})
    else:
        a, b, speed = T(seg[0]), T(seg[1]), seg[2]
        n = int(round((b - a) / speed * FPS))
        for i in range(n):
            t = a + i * speed / FPS
            plan.append({"kind": "rec", "t": t, "cap": next((c for ca, cb, c in captions if ca <= t < cb), None)})


def frame_at(t):
    best = frames[0][1]
    for ft, f in frames:
        if ft <= t:
            best = f
        else:
            break
    return best


def rounded_mask(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255)
    return m


layout = spec.get("layout", "phone")
if layout == "phone":
    frame_ov = Image.open(ov / "frame.png").convert("RGBA")
    mask = rounded_mask(SCREEN["w"], SCREEN["h"], SCREEN["r"])
elif layout == "crop":
    bg = Image.open(ov / "bg.png").convert("RGBA")
    cx, cy, cw, ch = spec["crop"]
    tw = 1000
    th = round(ch * tw / cw)
    ty = 360 + max(0, (1360 - th) // 2)
    mask = rounded_mask(tw, th, 40)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((40, ty + 24, 40 + tw, ty + th + 24), 40, fill=(31, 36, 48, 90))
    base_bg = bg.copy()
    base_bg.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(28)))

stills, caps = {}, {}


def cap_img(name):
    if name not in caps:
        caps[name] = Image.open(ov / name).convert("RGBA")
    return caps[name]


def still(seg, k):
    p = seg["image"]
    if p not in stills:
        stills[p] = Image.open(p if p.startswith("/") else ROOT / p).convert("RGB")
    (x0, y0, h0), (x1, y1, h1) = seg["from"], seg["to"]
    h = h0 + (h1 - h0) * k
    w = h * W / H
    cx_, cy_ = x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
    return stills[p].resize((W, H), Image.LANCZOS, box=(cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2)).convert("RGBA")


# Caption fade: ~0.25 s at the ends of each run of the same caption.
keys = [p["cap"] for p in plan]


def cap_alpha(i):
    k = keys[i]
    j0 = i
    while j0 > 0 and keys[j0 - 1] == k:
        j0 -= 1
    j1 = i
    while j1 < len(keys) - 1 and keys[j1 + 1] == k:
        j1 += 1
    return min(1.0, (min(i - j0, j1 - i) + 1) / 8)


ff = subprocess.Popen(
    ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
     "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
    stdin=subprocess.PIPE,
)
cache_key, cache_img = None, None
last, fade_from = None, None
for i, p in enumerate(plan):
    if p["kind"] == "rec":
        f = frame_at(p["t"])
        if f != cache_key:
            src = Image.open(f).convert("RGB")
            if layout == "phone":
                canvas = Image.new("RGBA", (W, H), (251, 246, 238, 255))
                canvas.paste(src.resize((SCREEN["w"], SCREEN["h"]), Image.LANCZOS), (SCREEN["x"], SCREEN["y"]), mask)
                canvas.alpha_composite(frame_ov)
            else:
                canvas = base_bg.copy()
                canvas.paste(src.crop((cx, cy, cx + cw, cy + ch)).resize((tw, th), Image.LANCZOS), (40, ty), mask)
            cache_key, cache_img = f, canvas
        img = cache_img.copy()
    else:
        if p["first"]:
            fade_from = last
        img = still(p["seg"], p["k"])
    if p["cap"]:
        cap = cap_img(p["cap"])
        a = cap_alpha(i)
        if a < 1:
            cap = cap.copy()
            cap.putalpha(cap.getchannel("A").point(lambda v: int(v * a)))
        img.alpha_composite(cap, (0, 0) if cap.size == (W, H) else (0, 10))
    rgb = img.convert("RGB")
    if p["kind"] == "img" and p["fade"] is not None and fade_from is not None:
        rgb = Image.blend(fade_from, rgb, ease(p["fade"]))
    ff.stdin.write(rgb.tobytes())
    last = rgb

end_n = int(spec.get("end_seconds", 2.2) * FPS)
if spec.get("end"):
    end = Image.open(ov / spec["end"]).convert("RGB")
    for i in range(end_n):
        ff.stdin.write(Image.blend(last, end, ease((i + 1) / 10)).tobytes())
ff.stdin.close()
ff.wait()
print(out, f"{(len(plan) + end_n) / FPS:.1f}s")
