# Publish Mapsie social posts from posts.json (media served from mapsie.shop/social/).
# The Meta token is added by the session's network proxy; it is never read or printed here.
# usage: python3 fb.py <first n> <last n> <gap seconds>
import json, re, sys, time, urllib.request, urllib.parse
PAGE = "1392111207326621"; G = "https://graph.facebook.com/v23.0"; BASE = "https://mapsie.shop/social/"
def call(method, path, data=None, token=None):
    data = dict(data or {})
    if token: data["access_token"] = token
    url = f"{G}/{path}"
    body = urllib.parse.urlencode(data).encode() if method == "POST" else None
    if method == "GET" and data: url += "?" + urllib.parse.urlencode(data)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=body, method=method), timeout=120) as r: return json.load(r)
    except urllib.error.HTTPError as e:
        return {"error": json.load(e).get("error", {})}
def fb_text(c):
    c = c.replace("Link in bio → Gift cards", "Buy one at https://mapsie.shop/gift")
    c = c.replace("Link in bio to design yours.", "Design yours at https://mapsie.shop")
    c = c.replace("Link in bio.", "https://mapsie.shop")
    c = c.replace(" (link in bio)", "").replace("at mapsie.shop", "at https://mapsie.shop")
    c = re.sub(r"\n\n(#\w+\s*)+$", "", c.strip())
    return c
token = call("GET", PAGE, {"fields": "access_token"}).get("access_token")  # page token, never printed
if not token: sys.exit("could not get page token")
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
    msg = fb_text(p["caption"])
    if p["type"] == "carousel":
        # Facebook: one post with several photos (each uploaded unpublished, then attached).
        ids = [call("POST", f"{PAGE}/photos", {"url": BASE + f, "published": "false"}, token).get("id") for f in p["files"]]
        r = call("POST", f"{PAGE}/feed", {"message": msg, "attached_media": json.dumps([{"media_fbid": i} for i in ids if i])}, token)
    elif p["type"] == "image":
        r = call("POST", f"{PAGE}/photos", {"url": BASE + p["file"], "message": msg}, token)
    else:
        r = call("POST", f"{PAGE}/videos", {"file_url": BASE + p["file"], "description": msg}, token)
    if "id" in r: print(f"FB {p['n']} OK {p.get('file') or 'carousel'} https://www.facebook.com/{r.get('post_id', r['id'])}", flush=True)
    else: print(f"FB {p['n']} FAILED: {r.get('error',{}).get('message')}", flush=True)
