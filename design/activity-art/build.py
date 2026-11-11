"""Render every concept in every style and suitable palette.

    python3 design/activity-art/build.py

Writes design/activity-art/out/<concept>/<style>-<palette>.svg and
out/manifest.json (which palettes passed the clash check for each concept).
"""
import importlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from artkit import LINE_PALETTES, PAPERCUT_PALETTES, render, contrast, delta_e  # noqa: E402

MODULES = sorted(p.stem for p in (HERE / "concepts").glob("*.py") if not p.stem.startswith("_"))
OUT = HERE / "out"


def main():
    manifest = []
    for mod in MODULES:
        m = importlib.import_module(f"concepts.{mod}")
        for c in m.CONCEPTS:
            good = c.good_palettes()
            dropped = [p for p in c.palettes if p not in good]
            d = OUT / c.id
            d.mkdir(parents=True, exist_ok=True)
            for p in good:
                (d / f"papercut-{p}.svg").write_text(render(c, "papercut", p))
            for p in LINE_PALETTES:
                (d / f"line-{p}.svg").write_text(render(c, "line", p))
            why = {p: min((round(contrast(c.colours(p)[a], c.colours(p)[b]), 2), round(delta_e(c.colours(p)[a], c.colours(p)[b]))) for a, b in c.checks) for p in dropped}
            manifest.append({"id": c.id, "activity": c.activity, "title": c.title, "papercut": good, "line": list(LINE_PALETTES), "dropped": why})
            print(f"{c.id:22} papercut ok: {', '.join(good):34} dropped: {why or '-'}")
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1))


if __name__ == "__main__":
    main()
