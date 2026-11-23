# Publish Mapsie social posts from posts.json (media served from mapsie.shop/social/).
# The Meta token is added by the session's network proxy; it is never read or printed here.
# usage: python3 post.py <first n> <last n> <gap seconds>
import json, sys, time, urllib.request, urllib.parse
IG = "17841431025006423"; G = "https://graph.facebook.com/v23.0"; BASE = "https://mapsie.shop/social/"
def call(method, path, data=None):
    url = f"{G}/{path}"
    body = urllib.parse.urlencode(data).encode() if data and method == "POST" else None
    if data and method == "GET": url += "?" + urllib.parse.urlencode(data)
    req = urllib.request.Request(url, data=body, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
    except urllib.error.HTTPError as e:
        return {"error": json.load(e).get("error", {})}
def live(f):
    try: return urllib.request.urlopen(BASE + f, timeout=30).status == 200
    except Exception: return False
first, last, gap = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
posts = [p for p in json.load(open(__import__("os").path.join(__import__("os").path.dirname(__file__), "posts.json"))) if first <= p["n"] <= last]
# Captions are checked with the Instagram skills, and drafts (not yet approved) never go out.
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from check import check as _check
for _p in posts:
    _ok, _notes = _check(_p)
    if not _ok:
        sys.exit(f"post {_p['n']} isn't ready: " + "; ".join(_notes))
for i, p in enumerate(posts):
    if i: time.sleep(gap)
    for f in (p.get("files") or [p["file"]]) + ([p["cover"]] if p.get("cover") else []):
        for _ in range(40):
            if live(f): break
            time.sleep(30)
    d = {"caption": p["caption"]}
    if p["type"] == "carousel":
        kids = []
        for f in p["files"]:
            k = call("POST", f"{IG}/media", {"image_url": BASE + f, "is_carousel_item": "true"})
            if "id" not in k: print(f"POST {p['n']} FAILED child {f}: {k.get('error',{}).get('message')}", flush=True); kids = None; break
            kids.append(k["id"])
        if kids is None: continue
        d.update(media_type="CAROUSEL", children=",".join(kids))
    elif p["type"] == "image": d["image_url"] = BASE + p["file"]
    else: d.update(media_type="REELS", video_url=BASE + p["file"], cover_url=BASE + p["cover"], share_to_feed="true")
    c = call("POST", f"{IG}/media", d)
    if "id" not in c: print(f"POST {p['n']} FAILED create: {c.get('error',{}).get('message')}", flush=True); continue
    cid = c["id"]
    for _ in range(60):
        s = call("GET", cid, {"fields": "status_code,status"})
        if s.get("status_code") in ("FINISHED", "ERROR", "EXPIRED"): break
        time.sleep(10)
    if s.get("status_code") != "FINISHED": print(f"POST {p['n']} FAILED processing: {s}", flush=True); continue
    r = call("POST", f"{IG}/media_publish", {"creation_id": cid})
    if "id" not in r: print(f"POST {p['n']} FAILED publish: {r.get('error',{}).get('message')}", flush=True); continue
    link = call("GET", r["id"], {"fields": "permalink"}).get("permalink")
    print(f"POST {p['n']} OK {p.get('file') or 'carousel'} {link}", flush=True)
