"""Render concepts in every style and suitable palette.

    python3 design/activity-art/build.py                 # all concept modules
    python3 design/activity-art/build.py water_a food    # just these modules
    python3 design/activity-art/build.py --export        # all modules, then copy into the app

Writes design/activity-art/out/<concept>/<style>-<palette>.svg and a manifest per
module (out/manifest-<module>.json). --export also writes the sticker files to
public/stickers/originals/ and the catalogue to src/lib/originals.json.
"""
import importlib
import json
import shutil
import xml.etree.ElementTree as ET
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "concepts"))
from artkit import LINE_PALETTES, render, contrast, delta_e  # noqa: E402
import polish  # noqa: E402

OUT = HERE / "out"
ACTIVITIES = {a["id"]: a for a in json.loads((HERE / "activities.json").read_text())}


def all_modules():
    return sorted(p.stem for p in (HERE / "concepts").glob("*.py") if not p.stem.startswith("_"))


def ids_in_other_modules(mod: str) -> dict[str, str]:
    """Concept ids already built by other modules (from their manifests), to catch clashes early."""
    taken = {}
    for f in OUT.glob("manifest-*.json"):
        other = f.stem.removeprefix("manifest-")
        if other != mod:
            for c in json.loads(f.read_text()):
                taken[c["id"]] = other
    return taken


def build_module(mod: str, seen: set[str]) -> list[dict]:
    m = importlib.import_module(mod)
    manifest = []
    taken = ids_in_other_modules(mod)
    for c in m.CONCEPTS:
        polish.apply(c)
        problems = []
        if c.activity not in ACTIVITIES:
            problems.append(f"unknown activity '{c.activity}'")
        if c.id in seen:
            problems.append(f"duplicate concept id '{c.id}'")
        if c.id in taken:
            problems.append(f"concept id '{c.id}' is already used by module '{taken[c.id]}': rename yours")
        seen.add(c.id)
        good = c.good_palettes()
        if len(good) < 2:
            problems.append(f"only {len(good)} papercut palette(s) pass the clash check")
        dropped = [p for p in c.palettes if p not in good]
        d = OUT / c.id
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
        for p in good:
            (d / f"papercut-{p}.svg").write_text(render(c, "papercut", p))
        for p in LINE_PALETTES:
            (d / f"line-{p}.svg").write_text(render(c, "line", p))
        # Every file must be valid SVG/XML, or browsers and the print renderer will drop it.
        for f in d.glob("*.svg"):
            try:
                ET.parse(f)
            except ET.ParseError as e:
                problems.append(f"{f.name} is not valid SVG ({e})")
                break
        why = {p: min((round(contrast(c.colours(p)[a], c.colours(p)[b]), 2), round(delta_e(c.colours(p)[a], c.colours(p)[b])))
                      for a, b in c.checks) for p in dropped}
        manifest.append({"id": c.id, "activity": c.activity, "title": c.title, "module": mod,
                         "papercut": good, "line": list(LINE_PALETTES), "dropped": why})
        flag = "  !! " + "; ".join(problems) if problems else ""
        print(f"{c.id:30} papercut: {', '.join(good) or '-':36}{flag}")
    (OUT / f"manifest-{mod}.json").write_text(json.dumps(manifest, indent=1))
    return manifest


def export():
    """Copy every built concept into the app and write the catalogue."""
    items = []
    for f in sorted(OUT.glob("manifest-*.json")):
        items += json.loads(f.read_text())
    dest = ROOT / "public" / "stickers" / "originals"
    if dest.exists():
        shutil.rmtree(dest)
    for it in items:
        shutil.copytree(OUT / it["id"], dest / it["id"])
    catalogue = [{"id": it["id"], "activity": it["activity"], "title": it["title"],
                  "label": ACTIVITIES[it["activity"]]["label"], "category": ACTIVITIES[it["activity"]]["category"],
                  "keywords": ACTIVITIES[it["activity"]].get("keywords", ""),
                  "papercut": it["papercut"], "line": it["line"]} for it in items]
    catalogue.sort(key=lambda x: (x["category"], x["label"], x["id"]))
    (ROOT / "src" / "lib" / "originals.json").write_text(json.dumps(catalogue))
    print(f"exported {len(catalogue)} concepts for {len({c['activity'] for c in catalogue})} activities")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    OUT.mkdir(exist_ok=True)
    seen: set[str] = set()
    for mod in args or all_modules():
        build_module(mod, seen)
    if "--export" in sys.argv:
        export()
