"""Check posts before they go out, with the Instagram skills' own tools (.claude/skills):
  - ig-caption/caption.py: first line, one call to action, hashtags, search terms
  - ig-human/detect.py:    anything that reads as machine-written
and refuse drafts (posts.json "draft": true means the owner hasn't approved it yet).

  python3 scripts/social/check.py 18 20        # report on posts 18 to 20
Used by instagram.py and facebook.py before posting; exits 1 if a post shouldn't go out.
"""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SKILLS = os.path.join(ROOT, ".claude", "skills")


def run(script, path, *args):
    tool = os.path.join(SKILLS, script)
    if not os.path.exists(tool):
        return None
    r = subprocess.run([sys.executable, "-I", tool, path, "--json", *args], capture_output=True, text=True, timeout=60)
    try:
        return json.loads(r.stdout)
    except Exception:
        return None


def check(post):
    """Returns (ok, notes)."""
    notes = []
    if post.get("draft"):
        return False, ["still a draft: the owner hasn't approved it (remove \"draft\" once they have)"]
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(post["caption"])
        path = f.name
    try:
        cap = run("ig-caption/caption.py", path, "--keywords", "map,mapsie")
        hum = run("ig-human/detect.py", path)
    finally:
        os.unlink(path)
    ok = True
    if cap:
        for c in cap.get("checks", []):
            if c.get("status") == "FAIL":
                ok = False
                notes.append(f"caption: {c.get('check')}: {c.get('detail')}")
            elif c.get("status") == "WARN":
                notes.append(f"caption (warning): {c.get('check')}: {c.get('detail')}")
    if hum:
        score = hum.get("human_score")
        if isinstance(score, (int, float)) and score < 60:
            ok = False
            notes.append(f"reads as machine-written (human score {score:.0f}/100): rewrite with the ig-human skill")
    return ok, notes


if __name__ == "__main__":
    first, last = int(sys.argv[1]), int(sys.argv[2])
    posts = [p for p in json.load(open(os.path.join(HERE, "posts.json"))) if first <= p["n"] <= last]
    bad = 0
    for p in posts:
        ok, notes = check(p)
        bad += not ok
        print(f"post {p['n']}: {'OK' if ok else 'NOT READY'}")
        for n in notes:
            print("   -", n)
    sys.exit(1 if bad else 0)
